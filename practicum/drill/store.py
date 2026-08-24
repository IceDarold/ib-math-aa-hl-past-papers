"""Журнал попыток. Единственные данные тренажёра, которых нет в git.

Хранится sqlite: одна строка на попытку и одна на состояние приёма.
Журнал держится вне каталога релиза, чтобы выкатка новой версии не сбивала
расписание повторения.

Время меряется на странице и приходит готовым: сколько прошло до первого
нажатия и сколько до отправки. Разделять их важно — первое показывает,
узнан ли приём, второе — насколько быстро считается.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time

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

CREATE TABLE IF NOT EXISTS skill_state (
    skill    TEXT PRIMARY KEY,
    box      INTEGER NOT NULL DEFAULT 0,
    due      REAL    NOT NULL DEFAULT 0,
    seen     INTEGER NOT NULL DEFAULT 0,
    wrong    INTEGER NOT NULL DEFAULT 0,
    last_ok  REAL,
    last_ts  REAL
);
"""

# Ящики Лейтнера: интервал до следующего показа, в днях.
BOXES = (0.0, 1.0, 3.0, 7.0, 21.0)
DAY = 86400.0


def connect(path=None):
    db = sqlite3.connect(path or DEFAULT_DB, timeout=10)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def record(db, *, mode, kind, practicum, skill, item, answer, ok, ms,
           first_ms, budget_ms):
    """Записывает попытку и двигает приём по ящикам."""
    now = time.time()
    db.execute(
        'INSERT INTO attempts (ts, mode, kind, practicum, skill, item, '
        'answer, ok, ms, first_ms, budget_ms) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (now, mode, kind, practicum, skill, item, answer[:200], int(bool(ok)),
         int(ms), int(first_ms), int(budget_ms)))

    row = db.execute('SELECT * FROM skill_state WHERE skill = ?',
                     (skill,)).fetchone()
    box = row['box'] if row else 0
    seen = (row['seen'] if row else 0) + 1
    wrong = (row['wrong'] if row else 0) + (0 if ok else 1)
    last_ok = (now if ok else (row['last_ok'] if row else None))
    # Верный ответ поднимает на ящик вверх, неверный возвращает в начало:
    # приём, который не сработал, нужен завтра, а не через три недели.
    box = min(box + 1, len(BOXES) - 1) if ok else 0
    due = now + BOXES[box] * DAY

    db.execute(
        'INSERT INTO skill_state (skill, box, due, seen, wrong, last_ok, '
        'last_ts) VALUES (?, ?, ?, ?, ?, ?, ?) '
        'ON CONFLICT(skill) DO UPDATE SET box = excluded.box, '
        'due = excluded.due, seen = excluded.seen, wrong = excluded.wrong, '
        'last_ok = excluded.last_ok, last_ts = excluded.last_ts',
        (skill, box, due, seen, wrong, last_ok, now))
    db.commit()


def states(db):
    """Состояние всех приёмов, которые хоть раз показывались."""
    return {row['skill']: dict(row)
            for row in db.execute('SELECT * FROM skill_state')}


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


def record_written(db, *, block, practicum, skill, reference, verdict,
                   photos):
    """Записывает разбор письменной работы.

    Отдельная таблица и отдельный счёт: здесь измеряется качество записи,
    а не скорость узнавания, и в ящики Лейтнера это не идёт. Смешать их
    значило бы испортить расписание повторения чужой метрикой.
    """
    marks = verdict.get('marks') or {}
    db.execute(
        'INSERT INTO written (ts, block, practicum, skill, reference, '
        'available, earned, math, photos, verdict, model) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (time.time(), block or '', practicum or '', skill or '',
         reference or '', marks.get('available'), marks.get('earned'),
         (verdict.get('mathematics') or {}).get('verdict', ''),
         json.dumps(photos, ensure_ascii=False),
         json.dumps(verdict, ensure_ascii=False),
         verdict.get('model', '')))
    db.commit()


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
