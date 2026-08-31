"""Журнал попыток. Единственные данные тренажёра, которых нет в git.

Хранится sqlite: одна строка на попытку и одна на состояние приёма.
Журнал держится вне каталога релиза, чтобы выкатка новой версии не сбивала
расписание повторения.

Время меряется на странице и приходит готовым: сколько прошло до первого
нажатия и сколько до отправки. Разделять их важно — первое показывает,
узнан ли приём, второе — насколько быстро считается. Второе к тому же
решает оценку попытки: см. `memory.grade`.

Состояние приёма — стойкость и трудность, а не номер ящика. Ящики
отвечали только на вопрос «показывать сегодня или нет»; карта приёмов
требует знать, насколько приём отточен, а это непрерывная величина.
Правила её движения живут в `memory.py`, здесь только хранение.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time

from drill import memory

DEFAULT_DB = os.environ.get(
    'DRILL_DB', os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             'drill.sqlite'))

SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          REAL    NOT NULL,
    mode        TEXT    NOT NULL,
    kind        TEXT    NOT NULL,
    practicum   TEXT    NOT NULL,
    skill       TEXT    NOT NULL,
    item        TEXT    NOT NULL,
    answer      TEXT    NOT NULL,
    ok          INTEGER NOT NULL,
    ms          INTEGER NOT NULL,
    first_ms    INTEGER NOT NULL,
    budget_ms   INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS attempts_skill ON attempts (skill, ts);

CREATE TABLE IF NOT EXISTS written (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          REAL    NOT NULL,
    block       TEXT    NOT NULL DEFAULT '',
    practicum   TEXT    NOT NULL DEFAULT '',
    skill       TEXT    NOT NULL DEFAULT '',
    reference   TEXT    NOT NULL DEFAULT '',
    available   INTEGER,
    earned      INTEGER,
    math        TEXT    NOT NULL DEFAULT '',
    photos      TEXT    NOT NULL DEFAULT '',
    verdict     TEXT    NOT NULL DEFAULT '',
    model       TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS written_skill ON written (skill, ts);

CREATE TABLE IF NOT EXISTS evening (
    id         TEXT    PRIMARY KEY,
    ts         REAL    NOT NULL,
    minutes    INTEGER NOT NULL,
    marks      INTEGER NOT NULL,
    questions  TEXT    NOT NULL,
    state      TEXT    NOT NULL DEFAULT 'draft',
    scanned_at REAL,
    started_at REAL,
    pages      TEXT    NOT NULL DEFAULT '',
    results    TEXT    NOT NULL DEFAULT ''
);
CREATE INDEX IF NOT EXISTS evening_ts ON evening (ts);

CREATE TABLE IF NOT EXISTS skill_state (
    skill      TEXT PRIMARY KEY,
    due        REAL    NOT NULL DEFAULT 0,
    seen       INTEGER NOT NULL DEFAULT 0,
    wrong      INTEGER NOT NULL DEFAULT 0,
    last_ok    REAL,
    last_ts    REAL,
    stability  REAL,
    difficulty REAL
);
"""

# Столбцы, которых нет в базах, заведённых до карты приёмов.
ADDED = (('stability', 'REAL'), ('difficulty', 'REAL'))
EVENING_ADDED = (('started_at', 'REAL'),)

DAY = memory.DAY


def connect(path=None):
    db = sqlite3.connect(path or DEFAULT_DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    have = {row['name'] for row in db.execute('PRAGMA table_info(skill_state)')}
    for name, kind in ADDED:
        if name not in have:
            db.execute(f'ALTER TABLE skill_state ADD COLUMN {name} {kind}')
    seen = {row['name'] for row in db.execute('PRAGMA table_info(evening)')}
    for name, kind in EVENING_ADDED:
        if name not in seen:
            db.execute(f'ALTER TABLE evening ADD COLUMN {name} {kind}')
    db.commit()
    return db


def record(db, *, mode, kind, practicum, skill, item, answer, ok, ms,
           first_ms, budget_ms):
    """Записывает попытку и двигает стойкость приёма.

    Возвращает оценку попытки — её показывают в разборе, чтобы было
    видно, почему верный, но медленный ответ продвинул меньше.
    """
    now = time.time()
    db.execute(
        'INSERT INTO attempts (ts, mode, kind, practicum, skill, item, '
        'answer, ok, ms, first_ms, budget_ms) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (now, mode, kind, practicum, skill, item, answer[:200], int(bool(ok)),
         int(ms), int(first_ms), int(budget_ms)))

    row = db.execute('SELECT * FROM skill_state WHERE skill = ?',
                     (skill,)).fetchone()
    seen = (row['seen'] if row else 0) + 1
    wrong = (row['wrong'] if row else 0) + (0 if ok else 1)
    last_ok = (now if ok else (row['last_ok'] if row else None))
    stability, difficulty, mark = memory.advance(
        row['stability'] if row else None,
        row['difficulty'] if row else None,
        row['last_ts'] if row else None,
        now, ok=ok, ms=ms, budget_ms=budget_ms, kind=kind)
    _save_state(db, skill, stability, difficulty, seen, wrong, last_ok, now)
    db.commit()
    return mark


def _save_state(db, skill, stability, difficulty, seen, wrong, last_ok, now):
    """Срок берётся из самой стойкости: приём возвращается тогда, когда
    просядет до девяноста процентов. Таблицы интервалов больше нет, и
    потолка в двадцать один день тоже."""
    db.execute(
        'INSERT INTO skill_state (skill, due, seen, wrong, last_ok, '
        'last_ts, stability, difficulty) VALUES (?, ?, ?, ?, ?, ?, ?, ?) '
        'ON CONFLICT(skill) DO UPDATE SET due = excluded.due, '
        'seen = excluded.seen, wrong = excluded.wrong, '
        'last_ok = excluded.last_ok, last_ts = excluded.last_ts, '
        'stability = excluded.stability, difficulty = excluded.difficulty',
        (skill, memory.due_at(now, stability), seen, wrong, last_ok, now,
         stability, difficulty))


def states(db):
    """Состояние всех приёмов, которые хоть раз показывались."""
    return {row['skill']: dict(row)
            for row in db.execute('SELECT * FROM skill_state')}


def strength(db, bank, now=None):
    """Карта приёмов: по числу на каждый квадрат.

    Счёт практикума — среднее по его приёмам, взвешенное баллами архива,
    которые за приёмами стоят: приём, на котором висит сорок баллов
    экзамена, тянет строку сильнее, чем приём на четыре. Приёмы, которых
    ни разу не показывали, в среднее не идут вовсе — иначе новая тема
    выглядела бы забытой, хотя её не начинали.
    """
    now = time.time() if now is None else now
    known = states(db)
    archive = bank.get('archive') or {}
    rows, by_practicum = [], {}
    for skill in bank['skills']:
        marks = sum((archive.get(block) or {}).get('marks') or 0
                    for block in (skill.get('blocks') or ()))
        state = known.get(skill['id'])
        row = {'id': skill['id'], 'practicum': skill['practicum'],
               'name': skill['name'], 'rung': skill['rung'], 'marks': marks,
               'seen': state['seen'] if state else 0,
               'wrong': state['wrong'] if state else 0}
        row.update(memory.snapshot(state, now))
        rows.append(row)
        by_practicum.setdefault(skill['practicum'], []).append(row)

    summary = []
    for practicum in bank['practicums']:
        group = by_practicum.get(practicum['id']) or []
        scored = [r for r in group if r['score'] is not None]
        weight = sum(r['marks'] for r in scored)
        summary.append({
            'id': practicum['id'],
            'title': practicum.get('title') or practicum['id'],
            'skills': len(group),
            'started': len(scored),
            'marks': sum(r['marks'] for r in group),
            'score': (round(sum(r['score'] * r['marks'] for r in scored)
                            / weight) if weight else
                      (round(sum(r['score'] for r in scored) / len(scored))
                       if scored else None)),
            'due': sum(1 for r in group
                       if r['due_in_days'] is not None and r['due_in_days'] <= 0),
        })
    return {'skills': rows, 'practicums': summary,
            'horizon': memory.HORIZON}


def recent(db, limit=200):
    return [dict(row) for row in db.execute(
        'SELECT * FROM attempts ORDER BY id DESC LIMIT ?', (limit,))]


def totals(db):
    row = db.execute(
        'SELECT COUNT(*) AS n, SUM(ok) AS ok, AVG(ms) AS ms, '
        'AVG(first_ms) AS first_ms FROM attempts').fetchone()
    today = db.execute(
        'SELECT COUNT(*) AS n, SUM(ok) AS ok FROM attempts WHERE ts > ?',
        (time.time() - DAY,)).fetchone()
    return {
        'attempts': row['n'] or 0,
        'correct': row['ok'] or 0,
        'avg_ms': int(row['ms'] or 0),
        'avg_first_ms': int(row['first_ms'] or 0),
        'today': today['n'] or 0,
        'today_correct': today['ok'] or 0,
    }


def open_evening(db, *, id, minutes, marks, questions):
    """Заводит вечерний набор черновиком.

    Набор живёт на сервере, а не в браузере: задания берут в семь вечера,
    а работу присылают в десять и с другого устройства. Пока это лежало
    в localStorage, такой вечер был невозможен.

    Черновик ещё не вечер: его можно посмотреть и пересобрать. Учитывается
    он только со `start_evening` — иначе брошенный набор занимал бы собой
    и список «продолжить», и память о недавних вопросах.
    """
    db.execute("DELETE FROM evening WHERE state = 'draft'")
    db.execute(
        "INSERT INTO evening (id, ts, minutes, marks, questions, state) "
        "VALUES (?, ?, ?, ?, ?, 'draft')",
        (id, time.time(), int(minutes), int(marks),
         json.dumps(questions, ensure_ascii=False)))
    db.commit()


def start_evening(db, set_id):
    """Черновик становится вечером. С этой минуты он считается."""
    changed = db.execute(
        "UPDATE evening SET state = 'open', started_at = ? "
        "WHERE id = ? AND state = 'draft'",
        (time.time(), set_id)).rowcount
    db.commit()
    if not changed and evening(db, set_id)['state'] == 'draft':
        raise LookupError('набор не удалось начать')


def drop_evening(db, set_id):
    """Выбрасывает черновик. Начатый вечер не трогаем."""
    dropped = db.execute("DELETE FROM evening WHERE id = ? AND state = 'draft'",
                         (set_id,)).rowcount
    db.commit()
    return bool(dropped)


def _evening_row(row):
    record = dict(row)
    for field in ('questions', 'pages', 'results'):
        try:
            record[field] = json.loads(record.get(field) or '[]')
        except json.JSONDecodeError:
            record[field] = []
    return record


def evening(db, set_id):
    row = db.execute('SELECT * FROM evening WHERE id = ?',
                     (set_id,)).fetchone()
    if row is None:
        raise LookupError('такого набора нет')
    return _evening_row(row)


def evenings(db, limit=20):
    return [_evening_row(row) for row in db.execute(
        'SELECT * FROM evening ORDER BY ts DESC LIMIT ?', (limit,))]


def recent_blocks(db, limit=6):
    """Вопросы, уже выданные в последних вечерах.

    Приём после ответа проседает почти до нуля веса, но у приёма бывает по
    десятку вопросов, и один и тот же билет дважды за неделю — случайность,
    которую дешевле запретить, чем объяснять.
    """
    seen = set()
    for row in db.execute("SELECT questions FROM evening "
                          "WHERE state != 'draft' "
                          "ORDER BY ts DESC LIMIT ?", (limit,)):
        try:
            for question in json.loads(row['questions'] or '[]'):
                if question.get('block'):
                    seen.add(question['block'])
        except json.JSONDecodeError:
            continue
    return seen


def save_pages(db, set_id, pages):
    """Страницы присланной работы: путь и к какому вопросу отнесены."""
    db.execute('UPDATE evening SET pages = ?, scanned_at = ? WHERE id = ?',
               (json.dumps(pages, ensure_ascii=False), time.time(), set_id))
    db.commit()


def finish_evening(db, set_id, results):
    db.execute("UPDATE evening SET results = ?, state = 'graded' "
               'WHERE id = ?',
               (json.dumps(results, ensure_ascii=False), set_id))
    db.commit()


def record_written(db, *, block, practicum, skill, reference, verdict,
                   photos):
    """Записывает разбор письменной работы.

    Отдельная таблица и отдельный счёт: здесь измеряется ещё и качество
    записи, а оно к силе приёма отношения не имеет, и смешивать их в
    одной строке нельзя.

    А вот на стойкость приёма работа влияет, и сильнее всего остального:
    это единственное свидетельство, снятое в условиях экзамена. Оценка
    берётся из доли набранных баллов, а не из секундомера — на бумаге
    он мерил бы скорость письма.
    """
    marks = verdict.get('marks') or {}
    cursor = db.execute(
        'INSERT INTO written (ts, block, practicum, skill, reference, '
        'available, earned, math, photos, verdict, model) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (time.time(), block or '', practicum or '', skill or '',
         reference or '', marks.get('available'), marks.get('earned'),
         (verdict.get('mathematics') or {}).get('verdict', ''),
         json.dumps(photos, ensure_ascii=False),
         json.dumps(verdict, ensure_ascii=False),
         verdict.get('model', '')))
    mark = memory.grade_written(marks.get('earned'), marks.get('available'))
    if skill and mark:
        now = time.time()
        row = db.execute('SELECT * FROM skill_state WHERE skill = ?',
                         (skill,)).fetchone()
        stability, difficulty = memory.step(
            row['stability'] if row else None,
            row['difficulty'] if row else None,
            row['last_ts'] if row else None, now, mark, 'written')
        _save_state(db, skill, stability, difficulty,
                    (row['seen'] if row else 0) + 1,
                    (row['wrong'] if row else 0) + (mark == 'again'),
                    now if mark != 'again' else (row['last_ok'] if row else None),
                    now)
    db.commit()
    return cursor.lastrowid, mark


def written_history(db, limit=50):
    rows = [dict(row) for row in db.execute(
        'SELECT id, ts, block, practicum, skill, reference, available, '
        'earned, math, model, photos FROM written ORDER BY id DESC LIMIT ?',
        (limit,))]
    for row in rows:
        row['pages'] = len(json.loads(row.pop('photos') or '[]'))
    return rows


def written_one(db, row_id):
    """Одна работа со всем, что о ней сохранено."""
    row = db.execute('SELECT * FROM written WHERE id = ?',
                     (row_id,)).fetchone()
    if row is None:
        raise LookupError('такой работы нет')
    record = dict(row)
    record['photos'] = json.loads(record.get('photos') or '[]')
    try:
        record['verdict'] = json.loads(record.get('verdict') or '{}')
    except json.JSONDecodeError:
        record['verdict'] = {}
    return record


def written_totals(db):
    row = db.execute(
        'SELECT COUNT(*) AS n, SUM(available) AS available, SUM(earned) AS '
        'earned FROM written').fetchone()
    return {'attempts': row['n'] or 0,
            'marks_available': row['available'] or 0,
            'marks_earned': row['earned'] or 0}
