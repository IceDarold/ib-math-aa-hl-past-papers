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
import base64
import json
import os
import random
import re
import sys
import threading
import time
from concurrent import futures
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from drill import archive, engine, evening, grader, memory  # noqa: E402
from drill import store  # noqa: E402
from drill.archive import reference as archive_reference  # noqa: E402
from drill.check import evaluate, show_answer  # noqa: E402
from drill.items import GENERATORS  # noqa: E402

# Скан вечера — до двух десятков страниц; проверка одного вопроса берёт
# из них только свои.
MAX_SHEET_PAGES = 24
EVENING_WORKERS = 4

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
                  order='schedule', avoid_blocks=(), papers=None, marks=None):
        with self.lock:
            db = self.connection()
            try:
                states = store.states(db)
            finally:
                db.close()
        skill, kind = engine.choose(self.bank, states, GENERATORS, mode=mode,
                                    rng=self.rng, avoid=avoid,
                                    practicums=practicums, only_due=only_due,
                                    order=order, papers=papers, marks=marks)
        shown, _, _ = engine.build_item(self.bank, GENERATORS, skill, kind,
                                        rng=self.rng, avoid_blocks=avoid_blocks,
                                        papers=papers, marks=marks)
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
                mark = store.record(
                    db, mode=str(payload.get('mode', 'mixed')),
                    kind=meta['kind'], practicum=skill['practicum'],
                    skill=skill_id, item=item_key, answer=raw, ok=bool(ok),
                    ms=int(payload.get('ms', 0)),
                    first_ms=int(payload.get('first_ms', 0)),
                    budget_ms=int(meta.get('budget_ms', 0)))
                state = store.states(db).get(skill_id)
            finally:
                db.close()
        strength = memory.snapshot(state, time.time())

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
            # Оценка и новая сила приёма: видно, что верный, но медленный
            # ответ продвинул меньше, чем верный и быстрый.
            'mark': mark,
            'strength': strength,
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

        skills, written = {}, {}
        for skill in self.bank['skills']:
            skills[skill['practicum']] = skills.get(skill['practicum'], 0) + 1
        for block in (self.bank.get('archive') or {}).values():
            practicum = block['skill'].split('.')[0]
            written[practicum] = written.get(practicum, 0) + 1

        written_blocks = [{
            'practicum': block['skill'].split('.')[0],
            'paper': block.get('paper'),
            'marks': block.get('marks'),
        } for block in (self.bank.get('archive') or {}).values()]

        return {
            'written_blocks': written_blocks,
            'practicums': [{
                'id': entry['id'],
                'title': entry['title'],
                'section': entry['section'],
                'marks': entry['marks'],
                'skills': skills.get(entry['id'], 0),
                'recognition': recognition.get(entry['id'], 0),
                'compute': compute.get(entry['id'], 0),
                'written': written.get(entry['id'], 0),
                'share': round(self.bank['share'].get(entry['id'], 0), 4),
            } for entry in self.bank['practicums']],
        }

    def photo_dir(self):
        """Куда складывать снимки: рядом с журналом, вне каталога релиза."""
        base = os.path.dirname(os.path.abspath(
            self.db_path or store.DEFAULT_DB))
        path = os.path.join(base, 'photos')
        os.makedirs(path, exist_ok=True)
        return path

    def page(self, block_id, kind='question', index=0):
        """Страница подлинника картинкой: билет или схема оценивания."""
        block = (self.bank.get('archive') or {}).get(block_id or '')
        if block is None:
            raise LookupError('такого вопроса нет')
        return archive.page_image(block, kind, index)

    def skill_card(self, skill_id, seed=None):
        """Всё, что известно о приёме: суть, ловушки и примеры заданий."""
        skill = self.bank['skills_by_id'].get(skill_id or '')
        if skill is None:
            raise LookupError('такого приёма нет')

        examples = []
        for item in self.bank['items_by_skill'].get(skill_id, [])[:3]:
            examples.append({'prompt': item['prompt'],
                             'answer': item['answer'],
                             'options': item['options']})

        compute = None
        if skill_id in GENERATORS:
            built = GENERATORS[skill_id](random.Random(
                int(seed) if seed else self.rng.randrange(2**31)))
            compute = {'prompt': built['prompt'],
                       'note': built.get('note'),
                       'answer': show_answer(
                           built['answer'],
                           var=built['check'].get('var', 'x'))}

        archive = []
        for block_id in skill.get('blocks') or ():
            block = (self.bank.get('archive') or {}).get(block_id)
            if block is None:
                continue
            archive.append({
                'block': block_id,
                'reference': archive_reference(block),
                'marks': block.get('marks'),
                'paper': block.get('paper'),
                'calculator': block.get('calculator'),
                'question_url': (f"/{block['dir']}/question-paper.pdf"
                                 f"#page={_first_page(block.get('source_pages'))}"),
            })
        archive.sort(key=lambda row: (row['paper'] or 0, row['marks'] or 0))

        with self.lock:
            db = self.connection()
            try:
                state = store.states(db).get(skill_id)
            finally:
                db.close()

        return {
            'id': skill_id,
            'practicum': skill['practicum'],
            'practicum_title': next(
                (p['title'] for p in self.bank['practicums']
                 if p['id'] == skill['practicum']), ''),
            'name': skill['name'],
            'rung': skill['rung'],
            'calculator': skill['calculator'],
            'trigger': skill['trigger'],
            'chain': skill.get('chain', []),
            'traps': skill.get('traps', []),
            'recognition': examples,
            'compute': compute,
            'archive': archive,
            'state': (dict({'seen': state['seen'], 'wrong': state['wrong']},
                            **memory.snapshot(state, time.time()))
                      if state else None),
        }

    def questions(self, practicum=None, skill=None):
        """Настоящие вопросы архива, привязанные к приёмам."""
        out = []
        for block_id, block in self.bank.get('archive', {}).items():
            if practicum and not block['skill'].startswith(f'{practicum}.'):
                continue
            if skill and block['skill'] != skill:
                continue
            out.append({
                'block': block_id,
                'reference': archive.reference(block),
                'skill': block['skill'],
                'skill_name': self.bank['skills_by_id'][block['skill']]['name'],
                'practicum': block['skill'].split('.')[0],
                'marks': block.get('marks'),
                'calculator': block.get('calculator'),
                'paper': block.get('paper'),
                'session': block.get('session'),
                # Прямые ссылки на подлинник: страницы отдаёт тот же сайт.
                'question_url': (f"/{block['dir']}/question-paper.pdf"
                                 f"#page={_first_page(block.get('source_pages'))}"),
                'markscheme_url': (f"/{block['dir']}/markscheme.pdf"
                                   f"#page={_first_page(block.get('markscheme_pages'))}"),
            })
        out.sort(key=lambda row: (row['practicum'], row['skill'],
                                  row['reference']))
        return {'questions': out}

    def written(self, row_id=None):
        with self.lock:
            db = self.connection()
            try:
                if row_id is None:
                    return {'history': store.written_history(db),
                            'totals': store.written_totals(db)}
                record = store.written_one(db, int(row_id))
            finally:
                db.close()
        record['files'] = [
            {'index': index, 'name': os.path.basename(name),
             'url': f'{PREFIX}/file?id={record["id"]}&n={index}'}
            for index, name in enumerate(record.pop('photos', []))]
        return record

    def written_file(self, row_id, index):
        """Отдаёт сохранённый снимок или скан работы."""
        with self.lock:
            db = self.connection()
            try:
                record = store.written_one(db, int(row_id))
            finally:
                db.close()
        names = record.get('photos') or []
        if not 0 <= int(index) < len(names):
            raise LookupError('такой страницы нет')
        root = os.path.realpath(self.photo_dir())
        path = os.path.realpath(os.path.join(root, names[int(index)]))
        # Имя пришло из базы, но проверяем всё равно: за пределы каталога
        # снимков отдавать нечего.
        if not path.startswith(root + os.sep) or not os.path.isfile(path):
            raise LookupError('файла нет')
        kind = {'.pdf': 'application/pdf', '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg'}.get(os.path.splitext(path)[1].lower(),
                                           'image/png')
        with open(path, 'rb') as handle:
            return handle.read(), kind

    def uploads(self, photos, limit=grader.MAX_PHOTOS):
        """Присланные файлы → страницы картинками и что сохранить на диск.

        Снимок приходит картинкой, скан — одним PDF на несколько страниц.
        Разбирать это на стороне браузера значило бы тащить туда pdf.js,
        тогда как PyMuPDF здесь уже есть.
        """
        images, kinds, keep = [], [], []
        for item in photos[:limit]:
            text = str(item)
            head = re.match(r'^data:(image/(\w+)|application/pdf);base64,',
                            text)
            try:
                data = base64.b64decode(
                    re.sub(r'^data:[\w/+.-]+;base64,', '', text),
                    validate=True)
            except Exception:  # noqa: BLE001
                raise ValueError('файл не разобрался')

            is_pdf = (head and head.group(1) == 'application/pdf') or \
                data[:5] == b'%PDF-'
            if is_pdf:
                try:
                    pages = archive.render_upload(data,
                                                  limit=limit - len(images))
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(f'PDF не открылся: {exc}')
                images += pages
                kinds += ['png'] * len(pages)
                # Страницы PDF сохраняются по одной, а не файлом целиком:
                # вечер раскладывает их по заданиям поимённо.
                keep += [('png', page) for page in pages]
            else:
                images.append(data)
                kinds.append('jpg' if head and head.group(2) in ('jpeg', 'jpg')
                             else 'png')
                keep.append((kinds[-1], data))
            if len(images) >= limit:
                break
        return images[:limit], keep[:limit]

    def store_pages(self, keep, folder=None):
        """Кладёт страницы на диск и отдаёт пути относительно каталога."""
        folder = folder or os.path.join(
            self.photo_dir(), f'{int(time.time())}-{uuid.uuid4().hex[:6]}')
        os.makedirs(folder, exist_ok=True)
        saved = []
        for number, (kind, data) in enumerate(keep, start=1):
            name = os.path.join(folder, f'page-{number}.{kind}')
            with open(name, 'wb') as fh:
                fh.write(data)
            saved.append(os.path.relpath(name, self.photo_dir()))
        return saved

    def grade(self, payload):
        """Разбирает сфотографированную работу против подлинной схемы."""
        photos = payload.get('photos') or []
        if not photos:
            raise ValueError('нет ни одного снимка работы')
        images, keep = self.uploads(photos)

        block_id = payload.get('block')
        block = (self.bank.get('archive', {}) or {}).get(block_id or '')
        pages, reference, skill_name, practicum, skill_id = {}, None, None, None, None
        rules = None
        if block:
            skill_id = block['skill']
            practicum = skill_id.split('.')[0]
            skill_name = self.bank['skills_by_id'][skill_id]['name']
            reference = archive.reference(block)
            try:
                pages = archive.block_pages(block)
            except LookupError:
                pages = {}
            rules = archive.instructions(block['dir'])

        # Снимки сохраняем до проверки, а не после: если модель не ответит,
        # работа всё равно должна остаться. Раньше она просто пропадала.
        saved = self.store_pages(keep)

        try:
            verdict = grader.grade(
                    work_images=images,
                question_text=payload.get('question_text') or None,
                question_images=pages.get('question', ()),
                markscheme_images=pages.get('markscheme', ()),
                instructions=rules,
                reference=reference,
                marks=(block or {}).get('marks'),
                calculator=(block or {}).get('calculator'),
                skill=skill_name,
                rubric_items=grader.rubric(practicum),
                model=payload.get('model'))
        except grader.GraderError as exc:
            # Работа сохранена, разбор не состоялся — так и записываем,
            # чтобы её было видно в списке и можно было отправить снова.
            with self.lock:
                db = self.connection()
                try:
                    store.record_written(
                        db, block=block_id or '', practicum=practicum or '',
                        skill=skill_id or '', reference=reference or '',
                        verdict={'error': str(exc)}, photos=saved)
                finally:
                    db.close()
            raise

        with self.lock:
            db = self.connection()
            try:
                store.record_written(
                    db, block=block_id or '', practicum=practicum or '',
                    skill=skill_id or '', reference=reference or '',
                    verdict=verdict, photos=saved)
            finally:
                db.close()

        verdict['reference'] = reference
        verdict['skill_name'] = skill_name
        verdict['graded_by_model'] = True
        return verdict

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
            row = {
                'id': skill['id'],
                'practicum': skill['practicum'],
                'name': skill['name'],
                'rung': skill['rung'],
                'seen': state['seen'] if state else 0,
                'wrong': state['wrong'] if state else 0,
                'has_compute': skill['id'] in GENERATORS,
            }
            row.update(memory.snapshot(state, now))
            skills.append(row)
        return {
            'skills': skills,
            'practicums': self.bank['practicums'],
            'share': self.bank['share'],
            'totals': totals,
            'recent': recent,
            'uncovered': self.bank.get('uncovered_skills', []),
        }

    def open_evening(self, minutes):
        """Собирает вечерний набор и запоминает его.

        Набор живёт на сервере: задания берут в семь, а работу присылают
        в десять и с другого устройства.
        """
        with self.lock:
            db = self.connection()
            try:
                states = store.states(db)
                questions, marks = evening.assemble(
                    self.bank, states, minutes, self.rng)
                set_id = evening.new_id(self.rng)
                store.open_evening(db, id=set_id, minutes=int(minutes),
                                   marks=marks, questions=questions)
                return store.evening(db, set_id)
            finally:
                db.close()

    def evening(self, set_id=None, limit=20):
        with self.lock:
            db = self.connection()
            try:
                return (store.evening(db, set_id) if set_id
                        else {'sets': store.evenings(db, limit)})
            finally:
                db.close()

    def sheet(self, set_id):
        """Лист заданий одним PDF."""
        record = self.evening(set_id)
        return archive.build_sheet(
            record['questions'], self.bank, minutes=record['minutes'],
            set_id=set_id,
            when=time.strftime('%Y-%m-%d', time.localtime(record['ts'])))

    def scan(self, payload):
        """Принимает работу за весь вечер и раскладывает её по заданиям."""
        set_id = str(payload.get('id') or '')
        record = self.evening(set_id)
        photos = payload.get('photos') or []
        if not photos:
            raise ValueError('нет ни одной страницы работы')
        count = len(record['questions'])
        images, keep = self.uploads(photos, limit=MAX_SHEET_PAGES)
        saved = self.store_pages(keep)

        # Раскладку предлагает дешёвый проход по номеру в углу. Не вышло —
        # раскладываем поровну по порядку: подтверждать всё равно глазами,
        # и поправить одно нажатие, а пустой экран пришлось бы заполнять
        # целиком руками.
        try:
            numbers = grader.assign_pages(
                [archive.shrink(png) for png in images], count)
            guessed = False
        except grader.GraderError:
            numbers = evening.split_by_question(images, count)
            guessed = True

        pages = [{'index': index, 'file': path,
                  'question': numbers[index] if index < len(numbers) else 1}
                 for index, path in enumerate(saved)]
        with self.lock:
            db = self.connection()
            try:
                store.save_pages(db, set_id, pages)
            finally:
                db.close()
        return {'id': set_id, 'pages': pages, 'guessed': guessed,
                'questions': record['questions']}

    def scan_page(self, set_id, index):
        """Одна страница присланной работы — для ленты подтверждения."""
        record = self.evening(set_id)
        pages = record.get('pages') or []
        if not 0 <= index < len(pages):
            raise LookupError('такой страницы нет')
        path = os.path.abspath(os.path.join(self.photo_dir(),
                                            pages[index]['file']))
        root = os.path.abspath(self.photo_dir())
        if not path.startswith(root + os.sep) or not os.path.isfile(path):
            raise LookupError('такой страницы нет')
        with open(path, 'rb') as handle:
            return handle.read(), ('image/jpeg' if path.endswith('.jpg')
                                   else 'image/png')

    def grade_evening(self, payload):
        """Разбирает весь вечер: каждый вопрос против своей схемы.

        Вопросы идут параллельно — они друг от друга не зависят, а ждать
        шесть проверок подряд значило бы сидеть перед экраном пять минут
        ровно после того, как встал из-за стола.
        """
        set_id = str(payload.get('id') or '')
        record = self.evening(set_id)
        pages = record.get('pages') or []
        if not pages:
            raise ValueError('работа за этот вечер ещё не прислана')

        told = payload.get('assignment') or []
        count = len(record['questions'])
        for index, page in enumerate(pages):
            if index < len(told):
                try:
                    number = int(told[index])
                except (TypeError, ValueError):
                    continue
                if 1 <= number <= count:
                    page['question'] = number
        with self.lock:
            db = self.connection()
            try:
                store.save_pages(db, set_id, pages)
            finally:
                db.close()

        groups = evening.group_pages(pages)
        jobs = [(question, groups.get(question['n']) or [])
                for question in record['questions']]
        results = [None] * len(jobs)
        with futures.ThreadPoolExecutor(max_workers=EVENING_WORKERS) as pool:
            running = {pool.submit(self._grade_one, question, group): index
                       for index, (question, group) in enumerate(jobs)}
            for done in futures.as_completed(running):
                results[running[done]] = done.result()

        with self.lock:
            db = self.connection()
            try:
                store.finish_evening(db, set_id, results)
                return store.evening(db, set_id)
            finally:
                db.close()

    def _grade_one(self, question, group):
        """Один вопрос вечера. Ошибка не роняет остальные."""
        head = {'n': question['n'], 'block': question['block'],
                'skill': question['skill'], 'skill_name': question['skill_name'],
                'practicum': question['practicum'],
                'reference': question['reference'],
                'available': question['marks'], 'pages': len(group)}
        if not group:
            # Пустое задание — не ошибка разбора, а решение не решать. В
            # журнал оно не идёт: сила приёма не должна падать за то, что
            # до вопроса не дошли руки.
            return dict(head, skipped=True, earned=None,
                        message='страниц по этому заданию не прислано')
        block = self.bank['archive'][question['block']]
        images = []
        for page in group:
            path = os.path.join(self.photo_dir(), page['file'])
            if os.path.isfile(path):
                with open(path, 'rb') as handle:
                    images.append(handle.read())
        try:
            pages = archive.block_pages(block)
        except LookupError:
            pages = {}
        try:
            verdict = grader.grade(
                work_images=images[:grader.MAX_PHOTOS],
                question_images=pages.get('question', ()),
                markscheme_images=pages.get('markscheme', ()),
                instructions=archive.instructions(block['dir']),
                reference=question['reference'], marks=question['marks'],
                calculator=block.get('calculator'),
                skill=question['skill_name'],
                rubric_items=grader.rubric(question['practicum']))
        except grader.GraderError as exc:
            return dict(head, error=str(exc), earned=None)

        with self.lock:
            db = self.connection()
            try:
                row_id, mark = store.record_written(
                    db, block=question['block'], practicum=question['practicum'],
                    skill=question['skill'], reference=question['reference'],
                    verdict=verdict,
                    photos=[page['file'] for page in group])
                strength = memory.snapshot(
                    store.states(db).get(question['skill']), time.time())
            finally:
                db.close()
        marks = verdict.get('marks') or {}
        verdict['reference'] = question['reference']
        verdict['skill_name'] = question['skill_name']
        # Вердикт уходит целиком: экран вечера показывает его тем же
        # разбором, что и одиночную работу, и второго его вида не заводится.
        return dict(head, written=row_id, mark=mark,
                    earned=marks.get('earned'),
                    available=marks.get('available') or question['marks'],
                    verdict=verdict, strength=strength)

    def strength(self):
        """Карта приёмов: число на каждый квадрат и счёт по практикумам."""
        with self.lock:
            db = self.connection()
            try:
                return store.strength(db, self.bank)
            finally:
                db.close()


def _first_page(spec):
    pages = archive.parse_pages(spec)
    return pages[0] if pages else 1


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
            skipped = (query.get('avoid_blocks') or [''])[0].split(',')
            order = (query.get('order') or ['schedule'])[0]
            only_due = (query.get('only_due') or ['0'])[0] in ('1', 'true')
            papers = tuple(int(p) for p in
                           (query.get('papers') or [''])[0].split(',') if p)
            low = (query.get('marks_min') or [''])[0]
            high = (query.get('marks_max') or [''])[0]
            marks = ((int(low or 0), int(high) if high else None)
                     if low or high else None)
            try:
                self.send_json(self.drill.next_item(
                    mode, avoid=tuple(a for a in avoid if a),
                    practicums=tuple(p for p in chosen if p) or None,
                    only_due=only_due, order=order,
                    avoid_blocks=tuple(b for b in skipped if b),
                    papers=papers or None, marks=marks))
            except LookupError as exc:
                self.send_json({'error': str(exc)}, 400)
            return
        if route == f'{PREFIX}/evening':
            set_id = (query.get('id') or [''])[0]
            try:
                self.send_json(self.drill.evening(set_id or None))
            except LookupError as exc:
                self.send_json({'error': str(exc)}, 404)
            return
        if route == f'{PREFIX}/evening/sheet':
            try:
                body = self.drill.sheet((query.get('id') or [''])[0])
            except LookupError as exc:
                self.send_json({'error': str(exc)}, 404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition',
                             'inline; filename="evening.pdf"')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if route == f'{PREFIX}/evening/page':
            try:
                body, kind = self.drill.scan_page(
                    (query.get('id') or [''])[0],
                    int((query.get('n') or ['0'])[0]))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 404)
                return
            self.send_response(200)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'private, max-age=600')
            self.end_headers()
            self.wfile.write(body)
            return
        if route == f'{PREFIX}/strength':
            self.send_json(self.drill.strength())
            return
        if route == f'{PREFIX}/stats':
            self.send_json(self.drill.stats())
            return
        if route == f'{PREFIX}/page':
            try:
                png = self.drill.page(
                    (query.get('block') or [''])[0],
                    (query.get('kind') or ['question'])[0],
                    int((query.get('n') or ['0'])[0]))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 404)
                return
            self.send_response(200)
            self.send_header('Content-Type', 'image/png')
            self.send_header('Content-Length', str(len(png)))
            self.send_header('Cache-Control', 'private, max-age=3600')
            self.end_headers()
            self.wfile.write(png)
            return
        if route == f'{PREFIX}/skill':
            try:
                self.send_json(self.drill.skill_card(
                    (query.get('id') or [''])[0],
                    (query.get('seed') or [None])[0]))
            except LookupError as exc:
                self.send_json({'error': str(exc)}, 404)
            return
        if route == f'{PREFIX}/questions':
            self.send_json(self.drill.questions(
                practicum=(query.get('practicum') or [None])[0],
                skill=(query.get('skill') or [None])[0]))
            return
        if route == f'{PREFIX}/written':
            try:
                self.send_json(self.drill.written(
                    (query.get('id') or [None])[0]))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 404)
            return
        if route == f'{PREFIX}/file':
            try:
                body, kind = self.drill.written_file(
                    (query.get('id') or [''])[0],
                    (query.get('n') or ['0'])[0])
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 404)
                return
            self.send_response(200)
            self.send_header('Content-Type', kind)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'private, max-age=3600')
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_json({'error': 'нет такой ручки'}, 404)

    def do_POST(self):
        route = urlparse(self.path).path
        allowed = (f'{PREFIX}/answer', f'{PREFIX}/grade',
                   f'{PREFIX}/evening/open', f'{PREFIX}/evening/scan',
                   f'{PREFIX}/evening/grade')
        if route not in allowed:
            self.send_json({'error': 'нет такой ручки'}, 404)
            return
        grading = route.endswith('/grade')
        # Скан за весь вечер — это до двух десятков страниц, вдвое больше
        # одной работы; ответ в поле — байты.
        heavy = grading or route.endswith('/scan')
        length = int(self.headers.get('Content-Length') or 0)
        if length > (64_000_000 if heavy else 64_000):
            self.send_json({'error': 'запрос слишком велик'}, 413)
            return
        try:
            payload = json.loads(self.rfile.read(length) or b'{}')
        except json.JSONDecodeError:
            self.send_json({'error': 'не разобрал запрос'}, 400)
            return

        if route == f'{PREFIX}/evening/open':
            try:
                self.send_json(self.drill.open_evening(
                    int(payload.get('minutes') or 40)))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 400)
            except Exception as exc:  # noqa: BLE001
                self.send_json({'error': f'набор не собрался: {exc}'}, 500)
            return

        if route == f'{PREFIX}/evening/scan':
            try:
                self.send_json(self.drill.scan(payload))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 400)
            except Exception as exc:  # noqa: BLE001
                self.send_json({'error': f'страницы не приняты: {exc}'}, 500)
            return

        if route == f'{PREFIX}/evening/grade':
            try:
                self.send_json(self.drill.grade_evening(payload))
            except (LookupError, ValueError) as exc:
                self.send_json({'error': str(exc)}, 400)
            except Exception as exc:  # noqa: BLE001
                self.send_json({'error': f'разбор не сработал: {exc}'}, 500)
            return

        if grading:
            try:
                self.send_json(self.drill.grade(payload))
            except ValueError as exc:
                self.send_json({'error': str(exc)}, 400)
            except grader.GraderError as exc:
                self.send_json({'error': str(exc)}, 502)
            except Exception as exc:  # noqa: BLE001
                self.send_json({'error': f'разбор не сработал: {exc}'}, 500)
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
