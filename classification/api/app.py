"""Атлас вопросов: служба только на чтение.

Предметов может быть несколько, у каждого свой индекс. Индекс называется
в запросе (`?subject=physics`), а какие есть — говорит `/api/subjects`.
Не назвали — отвечает первый в списке; так работали все прежние ссылки,
когда предмет был один.

    QUESTION_ATLAS_DBS=math:/путь/questions.sqlite,physics:/путь/atlas.sqlite

Столбцы у предметов разные: у физики есть форма ответа, командное слово и
сам текст вопроса со схемой оценивания, у математики — ссылки на страницы
PDF и следы разметки моделью. Служба не держит списка полей, а смотрит,
что в таблице есть на самом деле, и отдаёт это.
"""

from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse


DEFAULT_DB = Path(__file__).with_name("data") / "questions.sqlite"
PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
# Бумага сортируется как текст: у физики это 1A, 1B и 2, и CAST их сплющил
# бы в одну единицу.
ORDER = ("CAST(substr(session, -4) AS INTEGER), "
         "CASE WHEN session LIKE 'May %' THEN 5 ELSE 11 END, "
         "zone, paper, CAST(question AS INTEGER), part")
# Что показывать в списке. Столбца может не быть — берётся пересечение с
# тем, что в таблице действительно есть.
LIST_COLUMNS = (
    "id", "paper", "question", "part", "marks", "calculator", "source_pages",
    "markscheme_pages", "task_summary", "primary_topic", "method_family", "session",
    "zone", "source_root", "review_status", "level", "form", "command_term",
    "marking_points",
)
INTERNAL = {"topic_family", "search_text"}


def parse_subjects(value: str) -> dict[str, Path]:
    """`math:/путь,physics:/путь` → словарь. Пусто — старая одиночная база."""
    found: dict[str, Path] = {}
    for chunk in value.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        name, _, path = chunk.partition(":")
        if not path:
            raise ValueError(f"QUESTION_ATLAS_DBS: ожидалось id:путь, получено {chunk!r}")
        found[name.strip()] = Path(path.strip()).expanduser()
    return found


SUBJECTS = parse_subjects(os.environ.get("QUESTION_ATLAS_DBS", "")) or {
    "math": Path(os.environ.get("QUESTION_ATLAS_DB", DEFAULT_DB)),
}
DEFAULT_SUBJECT = next(iter(SUBJECTS))

app = FastAPI(title="Question Atlas API", version="2.0")


def resolve(subject: str | None) -> Path:
    """Индекс предмета. Незнакомое имя — 404, а не молчаливый чужой ответ."""
    name = subject or DEFAULT_SUBJECT
    if name not in SUBJECTS:
        raise HTTPException(status_code=404, detail=f"No such subject: {name}")
    return SUBJECTS[name]


@contextmanager
def database(subject: str | None = None) -> Iterator[sqlite3.Connection]:
    path = resolve(subject)
    if not path.is_file():
        raise HTTPException(status_code=503, detail="Question Atlas index is not available")
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def present(connection: sqlite3.Connection) -> tuple[str, ...]:
    """Какие столбцы у этого предмета есть на самом деле."""
    return tuple(row["name"] for row in connection.execute("PRAGMA table_info(questions)")
                 if row["name"] not in INTERNAL)


def rows(connection: sqlite3.Connection, sql: str, params: list[object]) -> list[dict[str, str]]:
    return [dict(row) for row in connection.execute(sql, params).fetchall()]


def columns(names: tuple[str, ...]) -> str:
    return ", ".join(f'"{name}"' for name in names)


def fts_query(value: str) -> str | None:
    terms = re.findall(r"[\w]+", value, flags=re.UNICODE)
    return " AND ".join(f'"{term}"*' for term in terms) or None


def where_clause(
    query: str | None, paper: str | None, calculator: str | None, session: str | None,
    zone: str | None, status: str | None, topics: list[str], methods: list[str],
    forms: list[str], have: tuple[str, ...] = (),
) -> tuple[str, list[object]]:
    conditions: list[str] = []
    params: list[object] = []
    if query:
        match = fts_query(query)
        if match:
            conditions.append("id IN (SELECT id FROM question_fts WHERE question_fts MATCH ?)")
            params.append(match)
    if paper is not None:
        conditions.append("paper = ?")
        params.append(paper)
    if calculator is not None:
        conditions.append("calculator = ?")
        params.append(calculator)
    if session is not None:
        conditions.append("session = ?")
        params.append(session)
    if zone is not None:
        conditions.append("zone = ?")
        params.append(zone)
    if status is not None:
        conditions.append("review_status = ?")
        params.append(status)
    if topics:
        conditions.append(f"topic_family IN ({', '.join('?' for _ in topics)})")
        params.extend(topics)
    if methods:
        conditions.append(f"method_family IN ({', '.join('?' for _ in methods)})")
        params.extend(methods)
    # Форма ответа есть не у всех предметов; спрашивать про несуществующий
    # столбец — это пятисотка вместо пустого отбора.
    if forms and "form" in have:
        conditions.append(f"form IN ({', '.join('?' for _ in forms)})")
        params.extend(forms)
    return (f" WHERE {' AND '.join(conditions)}" if conditions else ""), params


def count_by(connection: sqlite3.Connection, column: str) -> list[list[object]]:
    return [[row[0], row[1]] for row in connection.execute(
        f"SELECT {column}, COUNT(*) FROM questions GROUP BY {column} ORDER BY COUNT(*) DESC, {column}",
    ).fetchall()]


@app.get("/health")
@app.get("/api/health")
def health(subject: str | None = Query(default=None)) -> dict[str, object]:
    with database(subject) as connection:
        question_count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    return {"ok": True, "subject": subject or DEFAULT_SUBJECT, "questions": question_count}


@app.get("/api/subjects")
def subjects() -> dict[str, object]:
    """Какие предметы подняты и у какого индекс на месте."""
    return {
        "default": DEFAULT_SUBJECT,
        "subjects": [
            {"id": name, "ready": path.is_file(), "default": name == DEFAULT_SUBJECT}
            for name, path in SUBJECTS.items()
        ],
    }


@app.get("/api/facets")
def facets(subject: str | None = Query(default=None)) -> dict[str, object]:
    with database(subject) as connection:
        have = present(connection)
        total = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        verified = connection.execute("SELECT COUNT(*) FROM questions WHERE review_status = 'manual_verified'").fetchone()[0]
        out: dict[str, object] = {
            "subject": subject or DEFAULT_SUBJECT,
            "total": total,
            "verified": verified,
            "session_zones": connection.execute("SELECT COUNT(*) FROM (SELECT DISTINCT session, zone FROM questions)").fetchone()[0],
            "sessions": count_by(connection, "session"),
            "zones": count_by(connection, "zone"),
            "topics": count_by(connection, "topic_family"),
            "methods": count_by(connection, "method_family"),
            # Бумаги, статусы и калькулятор раньше были вшиты в страницу
            # тремя парами кнопок. У физики бумаги называются 1A, 1B и 2, и
            # проверять их неоткуда, кроме самого индекса.
            "papers": count_by(connection, "paper"),
            "statuses": count_by(connection, "review_status"),
            "calculators": count_by(connection, "calculator"),
            "columns": list(have),
        }
        if "form" in have:
            out["forms"] = count_by(connection, "form")
        return out


@app.get("/api/questions")
def questions(
    subject: str | None = Query(default=None),
    q: str | None = Query(default=None, max_length=200),
    # Бумага стала строкой: у физики это 1A, 1B и 2.
    paper: str | None = Query(default=None, max_length=4),
    calculator: str | None = Query(default=None, pattern="^(yes|no)$"),
    session: str | None = Query(default=None, max_length=32),
    zone: str | None = Query(default=None, max_length=16),
    status: str | None = Query(default=None, max_length=32),
    topic: list[str] = Query(default=[]),
    method: list[str] = Query(default=[]),
    form: list[str] = Query(default=[]),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> dict[str, object]:
    with database(subject) as connection:
        have = present(connection)
        clause, params = where_clause(q, paper, calculator, session, zone, status,
                                      topic, method, form, have)
        total, total_marks = connection.execute(
            f"SELECT COUNT(*), COALESCE(SUM(CAST(marks AS INTEGER)), 0) FROM questions{clause}", params,
        ).fetchone()
        shown = tuple(name for name in LIST_COLUMNS if name in have)
        items = rows(
            connection,
            f"SELECT {columns(shown)} FROM questions{clause} ORDER BY {ORDER} LIMIT ? OFFSET ?",
            [*params, page_size, (page - 1) * page_size],
        )
    return {"items": items, "total": total, "total_marks": total_marks, "page": page, "page_size": page_size}


@app.get("/api/questions/{question_id}")
def question(question_id: str, subject: str | None = Query(default=None)) -> JSONResponse:
    with database(subject) as connection:
        # Подробности отдаются целиком: какие поля есть у предмета, такие и
        # уходят. Перечислять их здесь значило бы держать список полей в
        # двух местах и однажды забыть про одно.
        row = connection.execute(
            f"SELECT {columns(present(connection))} FROM questions WHERE id = ?",
            [question_id],
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return JSONResponse(dict(row))
