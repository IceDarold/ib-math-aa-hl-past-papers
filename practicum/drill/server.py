#!/usr/bin/env python3
"""HTTP-служба тренажёра.

Стандартная библиотека и sympy — больше ничего. Соседняя служба атласа
живёт на FastAPI, но там читается sqlite и нужен полноценный веб-каркас;
здесь шесть ручек на одного человека, а машина уже уходила в перезагрузки
по памяти, так что лишний десяток мегабайт резидента ни к чему.

Правило, на котором всё держится: вся логика здесь, страница только рисует
и меряет время. Эталон ответа странице не отдаётся никогда — задание на
счёт пересобирается по зерну, когда приходит ответ.

Наружу служба не смотрит: слушает 127.0.0.1, а пароль и TLS — на nginx.
Страницу отдаёт атлас: на боевой машине готовой сборкой, локально —
`npm --prefix classification/web run dev`, где /api/drill проксируется сюда.

    python practicum/drill/server.py
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from drill import engine, store  # noqa: E402
from drill.check import evaluate, show_answer  # noqa: E402
from drill.items import GENERATORS  # noqa: E402

PREFIX = '/api/drill'


class Drill:
    """Общее состояние службы: банк, журнал, генераторы."""

    def __init__(self, db_path=None):
        self.bank = engine.load_bank()
        self.db_path = db_path
        self.lock = threading.Lock()
        self.rng = random.Random()

    def connection(self):
        return store.connect(self.db_path)

    def next_item(self, mode, avoid=(), practicums=None, only_due=False,
                  order='schedule'):
        with self.lock:
            db = self.connection()
            try:
                states = store.states(db)
            finally:
                db.close()
        skill, kind = engine.choose(self.bank, states, GENERATORS, mode=mode,
                                    rng=self.rng, avoid=avoid,
                                    practicums=practicums, only_due=only_due,
                                    order=order)
        shown, _, _ = engine.build_item(self.bank, GENERATORS, skill, kind,
                                        rng=self.rng)
        shown['skill_name'] = skill['name']
        shown['trigger'] = skill['trigger']
        shown['practicum_title'] = next(
            (p['title'] for p in self.bank['practicums']
             if p['id'] == shown['practicum']), '')
        return shown

    def answer(self, payload):
        item_key = str(payload.get('item', ''))
        raw = str(payload.get('answer', ''))
        meta, spec, answer = engine.rebuild_check(
            self.bank, GENERATORS, item_key)

        if spec['kind'] == 'digest':
            got = raw.strip().lower()
            ok = got and engine_digest(got) == spec['digest']
            message = ('✅ ' + got if ok
                       else f'❌ {got or "пусто"} — не тот приём')
        else:
            ok, message = evaluate(spec, raw)

        skill_id = meta['skill']
        skill = self.bank['skills_by_id'][skill_id]
        with self.lock:
            db = self.connection()
            try:
                store.record(
                    db, mode=str(payload.get('mode', 'mixed')),
                    kind=meta['kind'], practicum=skill['practicum'],
                    skill=skill_id, item=item_key, answer=raw, ok=bool(ok),
                    ms=int(payload.get('ms', 0)),
                    first_ms=int(payload.get('first_ms', 0)),
                    budget_ms=int(meta.get('budget_ms', 0)))
            finally:
                db.close()

        return {
            'ok': bool(ok),
            'message': message,
            'skill': skill_id,
            'skill_name': skill['name'],
            'trigger': skill['trigger'],
            'chain': skill.get('chain', []),
            # Ловушки — разбор того, где срезаются; при верном ответе они
            # только отвлекают, поэтому уходят лишь вместе с ошибкой.
            'traps': [] if ok else skill.get('traps', []),
            'practicum': skill['practicum'],
            'answer': show_answer(answer, var=spec.get('var', 'x')),
        }

    def setup(self):
        """Из чего собирается сессия: темы, сколько в каждой чего есть."""
        recognition, compute = {}, {}
        for item in self.bank['items']:
            recognition[item['practicum']] = recognition.get(
                item['practicum'], 0) + 1
        for skill_id in GENERATORS:
            practicum = self.bank['skills_by_id'][skill_id]['practicum']
            compute[practicum] = compute.get(practicum, 0) + 1

        skills = {}
        for skill in self.bank['skills']:
            skills[skill['practicum']] = skills.get(skill['practicum'], 0) + 1

        return {
            'practicums': [{
                'id': entry['id'],
                'title': entry['title'],
                'section': entry['section'],
                'marks': entry['marks'],
                'skills': skills.get(entry['id'], 0),
                'recognition': recognition.get(entry['id'], 0),
                'compute': compute.get(entry['id'], 0),
                'share': round(self.bank['share'].get(entry['id'], 0), 4),
            } for entry in self.bank['practicums']],
        }

    def stats(self):
        with self.lock:
            db = self.connection()
            try:
                states = store.states(db)
                totals = store.totals(db)
                recent = store.recent(db, 40)
            finally:
                db.close()
        now = time.time()
        skills = []
        for skill in self.bank['skills']:
            state = states.get(skill['id'])
            skills.append({
                'id': skill['id'],
                'practicum': skill['practicum'],
                'name': skill['name'],
                'rung': skill['rung'],
                'seen': state['seen'] if state else 0,
                'wrong': state['wrong'] if state else 0,
                'box': state['box'] if state else None,
                'due_in_days': (round((state['due'] - now) / 86400.0, 2)
                                if state else None),
                'has_compute': skill['id'] in GENERATORS,
            })
        return {
            'skills': skills,
            'practicums': self.bank['practicums'],
            'share': self.bank['share'],
            'totals': totals,
            'recent': recent,
            'uncovered': self.bank.get('uncovered_skills', []),
        }


def engine_digest(value):
    import hashlib
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


class Handler(BaseHTTPRequestHandler):
    server_version = 'drill'
    drill: Drill = None

    def log_message(self, fmt, *args):  # тише в журнале службы
        if self.path.startswith(PREFIX):
            sys.stderr.write(f'{self.log_date_time_string()} {fmt % args}\n')

    # --- ответы ---------------------------------------------------------
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    # --- маршруты -------------------------------------------------------
    def do_GET(self):
        url = urlparse(self.path)
        route = url.path
        query = parse_qs(url.query)

        if route == f'{PREFIX}/health':
            self.send_json({'ok': True,
                            'skills': len(self.drill.bank['skills']),
                            'items': len(self.drill.bank['items']),
                            'generators': len(GENERATORS)})
            return
        if route == f'{PREFIX}/setup':
            self.send_json(self.drill.setup())
            return
        if route == f'{PREFIX}/next':
            mode = (query.get('mode') or ['mixed'])[0]
            avoid = (query.get('avoid') or [''])[0].split(',')
            chosen = (query.get('practicums') or [''])[0].split(',')
            order = (query.get('order') or ['schedule'])[0]
            only_due = (query.get('only_due') or ['0'])[0] in ('1', 'true')
            try:
                self.send_json(self.drill.next_item(
                    mode, avoid=tuple(a for a in avoid if a),
                    practicums=tuple(p for p in chosen if p) or None,
                    only_due=only_due, order=order))
            except LookupError as exc:
                self.send_json({'error': str(exc)}, 400)
            return
        if route == f'{PREFIX}/stats':
            self.send_json(self.drill.stats())
            return

        self.send_json({'error': 'нет такой ручки'}, 404)

    def do_POST(self):
        if urlparse(self.path).path != f'{PREFIX}/answer':
            self.send_json({'error': 'нет такой ручки'}, 404)
            return
        length = int(self.headers.get('Content-Length') or 0)
        if length > 64_000:
            self.send_json({'error': 'слишком длинный ответ'}, 413)
            return
        try:
            payload = json.loads(self.rfile.read(length) or b'{}')
        except json.JSONDecodeError:
            self.send_json({'error': 'не разобрал запрос'}, 400)
            return
        try:
            self.send_json(self.drill.answer(payload))
        except LookupError:
            self.send_json({'error': 'задание не опознано'}, 400)
        except Exception as exc:  # noqa: BLE001
            self.send_json({'error': f'проверка не сработала: {exc}'}, 500)


def main():
    parser = argparse.ArgumentParser(description='Служба тренажёра')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8042)
    parser.add_argument('--db', default=None, help='файл журнала')
    args = parser.parse_args()

    Handler.drill = Drill(args.db)
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    where = f'http://{args.host}:{args.port}'
    print(f'тренажёр: {len(Handler.drill.bank["skills"])} приёмов, '
          f'{len(Handler.drill.bank["items"])} условий, '
          f'{len(GENERATORS)} генераторов задач')
    print(f'слушаю {where}{PREFIX}/')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nостановлен')


if __name__ == '__main__':
    main()
