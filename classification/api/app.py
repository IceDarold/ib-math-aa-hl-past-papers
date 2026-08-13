"""Read-only FastAPI service for the Question Atlas."""

from __future__ import annotations

import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse


DATABASE = Path(os.environ.get("QUESTION_ATLAS_DB", Path(__file__).with_name("data") / "questions.sqlite"))
PAGE_SIZE = 50
MAX_PAGE_SIZE = 100
ORDER = "CAST(substr(session, -4) AS INTEGER), CASE WHEN session LIKE 'May %' THEN 5 ELSE 11 END, zone, CAST(paper AS INTEGER), CAST(question AS INTEGER), part"
LIST_COLUMNS = (
    "id", "paper", "question", "part", "marks", "calculator", "source_pages",
    "markscheme_pages", "task_summary", "primary_topic", "method_family", "session",
    "zone", "source_root", "review_status",
)
DETAIL_COLUMNS = (
    "id", "paper", "question", "part", "marks", "calculator", "source_pages",
    "markscheme_pages", "task_summary", "primary_topic", "secondary_topics",
    "method_family", "method_tags", "method_path", "accepted_alternatives", "session",
    "zone", "source_root", "review_status", "evidence", "confidence", "review_flags",
)

app = FastAPI(title="Question Atlas API", version="1.0")


@contextmanager
def database() -> Iterator[sqlite3.Connection]:
    if not DATABASE.is_file():
        raise HTTPException(status_code=503, detail="Question Atlas index is not available")
    connection = sqlite3.connect(f"file:{DATABASE}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()


def rows(connection: sqlite3.Connection, sql: str, params: list[object]) -> list[dict[str, str]]:
    return [dict(row) for row in connection.execute(sql, params).fetchall()]


def columns(names: tuple[str, ...]) -> str:
    return ", ".join(f'"{name}"' for name in names)


def fts_query(value: str) -> str | None:
    terms = re.findall(r"[\w]+", value, flags=re.UNICODE)
    return " AND ".join(f'"{term}"*' for term in terms) or None


def where_clause(
    query: str | None, paper: int | None, calculator: str | None, session: str | None,
    zone: str | None, status: str | None, topics: list[str], methods: list[str],
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
        params.append(str(paper))
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
    return (f" WHERE {' AND '.join(conditions)}" if conditions else ""), params


def count_by(connection: sqlite3.Connection, column: str) -> list[list[object]]:
    return [[row[0], row[1]] for row in connection.execute(
        f"SELECT {column}, COUNT(*) FROM questions GROUP BY {column} ORDER BY COUNT(*) DESC, {column}",
    ).fetchall()]


@app.get("/health")
def health() -> dict[str, object]:
    with database() as connection:
        question_count = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    return {"ok": True, "questions": question_count}


@app.get("/api/facets")
def facets() -> dict[str, object]:
    with database() as connection:
        total = connection.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
        verified = connection.execute("SELECT COUNT(*) FROM questions WHERE review_status = 'manual_verified'").fetchone()[0]
        return {
            "total": total,
            "verified": verified,
            "session_zones": connection.execute("SELECT COUNT(*) FROM (SELECT DISTINCT session, zone FROM questions)").fetchone()[0],
            "sessions": count_by(connection, "session"),
            "zones": count_by(connection, "zone"),
            "topics": count_by(connection, "topic_family"),
            "methods": count_by(connection, "method_family"),
        }


@app.get("/api/questions")
def questions(
    q: str | None = Query(default=None, max_length=200),
    paper: int | None = Query(default=None, ge=1, le=3),
    calculator: str | None = Query(default=None, pattern="^(yes|no)$"),
    session: str | None = Query(default=None, max_length=32),
    zone: str | None = Query(default=None, max_length=16),
    status: str | None = Query(default=None, pattern="^(manual_verified|ai_draft)$"),
    topic: list[str] = Query(default=[]),
    method: list[str] = Query(default=[]),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
) -> dict[str, object]:
    clause, params = where_clause(q, paper, calculator, session, zone, status, topic, method)
    with database() as connection:
        total, total_marks = connection.execute(
            f"SELECT COUNT(*), COALESCE(SUM(CAST(marks AS INTEGER)), 0) FROM questions{clause}", params,
        ).fetchone()
        items = rows(
            connection,
            f"SELECT {columns(LIST_COLUMNS)} FROM questions{clause} ORDER BY {ORDER} LIMIT ? OFFSET ?",
            [*params, page_size, (page - 1) * page_size],
        )
    return {"items": items, "total": total, "total_marks": total_marks, "page": page, "page_size": page_size}


@app.get("/api/questions/{question_id}")
def question(question_id: str) -> JSONResponse:
    with database() as connection:
        row = connection.execute(f"SELECT {columns(DETAIL_COLUMNS)} FROM questions WHERE id = ?", [question_id]).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return JSONResponse(dict(row))
