"""Проверка вечернего набора.

Проверяющая модель здесь подменена: набор проверяет сборку, лист заданий,
раскладку страниц по заданиям и то, что вечер доходит до журнала и до силы
приёма. Сама проверка работы моделью проверяется в `test_drill.py`.
"""
import base64
import os
import random
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

import pymupdf  # noqa: E402

from drill import archive, engine, evening, grader, memory, store  # noqa: E402
from drill import server as service  # noqa: E402

passed = failed = 0


def t(name, ok):
    global passed, failed
    print(('  ✅ ' if ok else '  ❌ ') + name)
    if ok:
        passed += 1
    else:
        failed += 1


bank = engine.load_bank()

print('=== сборка набора ===')
questions, marks = evening.assemble(bank, {}, 40, random.Random(3))
t('вечер набирается примерно на заказанное время',
  40 <= marks <= 40 + evening.OVERSHOOT)
t('вопросов получается немного, а не десятки', 4 <= len(questions) <= 10)
t('один приём в вечер попадает один раз',
  len({q['skill'] for q in questions}) == len(questions))
t('один вопрос архива в вечер попадает один раз',
  len({q['block'] for q in questions}) == len(questions))
t('у каждого вопроса есть ссылка на бумагу',
  all(q['reference'] and q['marks'] for q in questions))
t('нумерация идёт подряд с единицы',
  [q['n'] for q in questions] == list(range(1, len(questions) + 1)))
t('минуты считаются обратно из баллов',
  evening.minutes_for(questions) == marks)

short, short_marks = evening.assemble(bank, {}, 10, random.Random(5))
t('короткий вечер тоже собирается', 10 <= short_marks <= 10 + evening.OVERSHOOT)
long_set, long_marks = evening.assemble(bank, {}, 90, random.Random(5))
t('длинный вечер упирается в потолок по числу задач',
  len(long_set) <= evening.MAX_QUESTIONS)
t('вечер просят не короче нижней границы',
  evening.assemble(bank, {}, 1, random.Random(5))[1] >= evening.MIN_MINUTES)

print('\n=== приёмы берутся по расписанию ===')
# Все приёмы отвечены только что и держатся долго, кроме одного: он мелкий
# и месяц не поднимался. Вес у него на порядки выше, и вечер обязан его
# заметить. Время здесь настоящее — при last_ts = 0 просевшими выглядят
# все сразу, и проверка ничего бы не проверяла.
now = time.time()
target = 'C1.cosine_rule'
states = {s['id']: {'last_ts': now, 'stability': 200.0, 'difficulty': 3.0,
                    'seen': 5, 'wrong': 0} for s in bank['skills']}
states[target] = {'last_ts': now - 30 * memory.DAY, 'stability': 0.6,
                  'difficulty': 9.0, 'seen': 5, 'wrong': 4}
skill = bank['skills_by_id'][target]
weights = sorted(engine.weight(s, states[s['id']], bank['share'], now)
                 for s in bank['skills'])
t('просевший приём весит больше всех остальных',
  engine.weight(skill, states[target], bank['share'], now) == weights[-1])
hits = sum(target in {q['skill'] for q in
                      evening.assemble(bank, states, 40, random.Random(seed))[0]}
           for seed in range(30))
t('и попадает почти в каждый вечер', hits >= 24)

print('\n=== отборы ===')
picked, _ = evening.assemble(bank, {}, 40, random.Random(3),
                             practicums=['E1', 'B1'])
t('темы ограничивают набор',
  {q['practicum'] for q in picked} <= {'E1', 'B1'})
t('внутри выбранных тем вечер всё равно набирается',
  len(picked) >= 4)
only_one = evening.assemble(bank, {}, 40, random.Random(3),
                            papers=[1])[0]
t('бумага ограничивает набор',
  {q['paper'] for q in only_one} == {1})
t('Paper 1 — это вечер без калькулятора',
  all(q['calculator'] != 'yes' for q in only_one))
both = evening.assemble(bank, {}, 40, random.Random(3),
                        practicums=['C4'], papers=[2])[0]
t('темы и бумаги действуют вместе',
  {q['practicum'] for q in both} == {'C4'} and {q['paper'] for q in both} == {2})
try:
    evening.assemble(bank, {}, 40, random.Random(3), practicums=['нет такой'])
    t('пустой отбор объясняет себя, а не молчит', False)
except LookupError as exc:
    t('пустой отбор объясняет себя, а не молчит', 'отбор' in str(exc))

# «Только просроченное»: всё свежее, кроме одной темы.
now = time.time()
ripe = 'C1'
states = {s['id']: {'last_ts': now, 'due': now + 7 * memory.DAY,
                    'stability': 200.0, 'difficulty': 3.0,
                    'seen': 3, 'wrong': 0} for s in bank['skills']}
for skill in bank['skills']:
    if skill['practicum'] == ripe:
        states[skill['id']]['due'] = now - memory.DAY
due_only = evening.assemble(bank, states, 30, random.Random(3),
                            only_due=True)[0]
t('«только просроченное» берёт лишь то, чему подошёл срок',
  {q['practicum'] for q in due_only} == {ripe})
fresh_all = {s['id']: {'last_ts': now, 'due': now + 7 * memory.DAY,
                       'stability': 200.0, 'difficulty': 3.0,
                       'seen': 3, 'wrong': 0} for s in bank['skills']}
t('когда просрочено ничего, вечер всё равно собирается',
  len(evening.assemble(bank, fresh_all, 30, random.Random(3),
                       only_due=True)[0]) >= 3)

used = {q['block'] for q in picked}
again = evening.assemble(bank, {}, 40, random.Random(8),
                         avoid_blocks=used)[0]
t('вопросы недавних вечеров не повторяются',
  not ({q['block'] for q in again} & used))
narrow = evening.assemble(bank, {}, 40, random.Random(8),
                          practicums=['E1'], papers=[1],
                          avoid_blocks=set(bank['archive']))[0]
t('но лучше повтор билета, чем вечер из двух задач',
  len(narrow) >= 3)

print('\n=== лист заданий ===')
pdf = archive.build_sheet(questions, bank, minutes=40, set_id='abc12xyz',
                          when='2026-08-31')
t('лист — настоящий PDF', pdf[:5] == b'%PDF-')
with pymupdf.open(stream=pdf, filetype='pdf') as sheet:
    pages = sheet.page_count
    cover = sheet[0].get_text()
    stamped = sheet[1].get_text()
t('в листе есть обложка и страницы билетов', pages > len(questions))
t('на обложке стоит номер набора', 'abc12xyz' in cover)
t('на обложке перечислены все вопросы',
  all(q['reference'] in cover for q in questions))
t('на обложке написано, что подписывать страницы',
  'номер задания' in cover or 'question number' in cover)
t('страница билета помечена номером задания', '1' in stamped)

print('\n=== раскладка страниц ===')
t('поровну по порядку при трёх заданиях на шесть страниц',
  evening.split_by_question([None] * 6, 3) == [1, 1, 2, 2, 3, 3])
t('лишние страницы уходят в последнее задание',
  evening.split_by_question([None] * 7, 3)[-1] == 3)
t('пустой скан даёт пустую раскладку', evening.split_by_question([], 3) == [])
t('без заданий раскладки нет', evening.split_by_question([None], 0) == [])
t('страницы группируются по заданиям',
  evening.group_pages([{'question': 2, 'file': 'b'},
                       {'question': 1, 'file': 'a'},
                       {'question': 2, 'file': 'c'}])
  == {2: [{'question': 2, 'file': 'b'}, {'question': 2, 'file': 'c'}],
      1: [{'question': 1, 'file': 'a'}]})

print('\n=== журнал вечеров ===')
with tempfile.TemporaryDirectory() as tmp:
    db = store.connect(os.path.join(tmp, 'evening.sqlite'))
    store.open_evening(db, id='zzz', minutes=40, marks=marks,
                       questions=questions)
    record = store.evening(db, 'zzz')
    t('набор сохраняется и читается обратно',
      len(record['questions']) == len(questions))
    t('набор заводится черновиком', record['state'] == 'draft')
    t('пока страниц нет, их список пуст', record['pages'] == [])
    t('черновик в память о недавних вопросах не идёт',
      store.recent_blocks(db) == set())

    store.open_evening(db, id='www', minutes=40, marks=marks,
                       questions=questions)
    t('новый черновик выбрасывает прошлый',
      [row['id'] for row in store.evenings(db)] == ['www'])
    t('черновик выбрасывается по «назад»', store.drop_evening(db, 'www'))
    t('после этого наборов не остаётся', store.evenings(db) == [])

    store.open_evening(db, id='zzz', minutes=40, marks=marks,
                       questions=questions)
    store.start_evening(db, 'zzz')
    t('старт делает набор вечером', store.evening(db, 'zzz')['state'] == 'open')
    t('время старта записано', store.evening(db, 'zzz')['started_at'])
    t('после старта вопросы помнятся',
      store.recent_blocks(db) == {q['block'] for q in questions})
    t('глубина памяти ограничена', store.recent_blocks(db, 0) == set())
    t('начатый вечер не выбрасывается', store.drop_evening(db, 'zzz') is False)

    store.save_pages(db, 'zzz', [{'index': 0, 'file': 'p.png', 'question': 1}])
    t('страницы сохраняются вместе с раскладкой',
      store.evening(db, 'zzz')['pages'][0]['question'] == 1)
    t('время скана записывается', store.evening(db, 'zzz')['scanned_at'])
    store.finish_evening(db, 'zzz', [{'n': 1, 'earned': 3}])
    t('разобранный вечер помечается',
      store.evening(db, 'zzz')['state'] == 'graded')
    t('вечера перечисляются свежими вперёд',
      [row['id'] for row in store.evenings(db)] == ['zzz'])
    t('разобранный вечер тоже помнится',
      store.recent_blocks(db) == {q['block'] for q in questions})
    try:
        store.evening(db, 'нет такого')
        t('чужой набор не находится', False)
    except LookupError:
        t('чужой набор не находится', True)
    db.close()

print('\n=== вечер целиком, с подменённой моделью ===')


def fake_grade(**kwargs):
    """Ставит половину баллов и не ходит в сеть."""
    available = kwargs.get('marks') or 6
    return {'marks': {'available': available, 'earned': available},
            'mathematics': {'verdict': 'correct', 'notes': []},
            'presentation': {'verdict': 'clean', 'items': []},
            'model': 'подмена'}


def fake_assign(pages, count, model=None):
    """Первая страница первому заданию, вторая второму и так далее."""
    return [min(count, index + 1) for index in range(len(pages))]


def blank_png(text='1'):
    page = pymupdf.open()
    sheet = page.new_page(width=300, height=400)
    sheet.insert_text(pymupdf.Point(240, 40), text, fontsize=24)
    data = sheet.get_pixmap(dpi=72).tobytes('png')
    page.close()
    return 'data:image/png;base64,' + base64.b64encode(data).decode()


with tempfile.TemporaryDirectory() as tmp:
    real_grade, real_assign = grader.grade, grader.assign_pages
    grader.grade, grader.assign_pages = fake_grade, fake_assign
    try:
        drill = service.Drill(db_path=os.path.join(tmp, 'run.sqlite'))
        drill.rng = random.Random(4)
        opened = drill.open_evening(30)
        count = len(opened['questions'])
        t('ручка отдаёт собранный набор с ключом',
          len(opened['id']) == 8 and count >= 3)
        t('набор приходит черновиком, а не начатым вечером',
          opened['state'] == 'draft')

        # Черновик — ещё не вечер: работу он не принимает, а пересборка
        # его выбрасывает, чтобы брошенные наборы не копились.
        try:
            drill.scan({'id': opened['id'], 'photos': [blank_png('1')]})
            t('черновик не принимает работу', False)
        except ValueError as exc:
            t('черновик не принимает работу', 'не начат' in str(exc))
        again = drill.open_evening(30)
        t('пересборка выбрасывает прошлый черновик',
          drill.evening()['sets'][0]['id'] == again['id']
          and len(drill.evening()['sets']) == 1)
        t('черновик выбрасывается по «назад»',
          drill.drop_evening(again['id'])['dropped'] is True
          and not drill.evening()['sets'])

        opened = drill.open_evening(30)
        count = len(opened['questions'])
        opened = drill.start_evening(opened['id'])
        t('старт открывает вечер', opened['state'] == 'open')

        sheet = drill.sheet(opened['id'])
        t('лист собирается по ключу набора', sheet[:5] == b'%PDF-')

        scanned = drill.scan({'id': opened['id'],
                              'photos': [blank_png(str(n))
                                         for n in range(1, count + 1)]})
        t('страницы приняты и разложены', len(scanned['pages']) == count)
        t('раскладка не помечена догадкой', scanned['guessed'] is False)
        t('каждая страница получила задание',
          [page['question'] for page in scanned['pages']]
          == list(range(1, count + 1)))

        body, kind = drill.scan_page(opened['id'], 0)
        t('страницу работы можно посмотреть обратно',
          body[:4] == b'\x89PNG' and kind == 'image/png')

        graded = drill.grade_evening({'id': opened['id']})
        results = graded['results']
        t('вечер разобран', graded['state'] == 'graded')
        t('вердикт пришёл на каждое задание', len(results) == count)
        t('порядок заданий сохранён',
          [row['n'] for row in results] == list(range(1, count + 1)))
        t('баллы посчитаны',
          all(row.get('earned') == row.get('available') for row in results))
        t('у каждого задания названы приём и бумага',
          all(row['skill_name'] and row['reference'] for row in results))
        t('вердикт приходит целиком, тем же видом, что у одиночной работы',
          all(row['verdict']['mathematics'] and row['verdict']['reference']
              for row in results))

        db = store.connect(drill.db_path)
        moved = store.states(db)
        t('каждое задание вечера двинуло свой приём',
          all(row['skill'] in moved for row in results))
        t('сила приёма выросла',
          all(moved[row['skill']]['stability'] > 0 for row in results))
        t('работы попали в журнал письменных',
          store.written_totals(db)['attempts'] == count)
        t('снимок силы вернулся вместе с вердиктом',
          all((row.get('strength') or {}).get('score') is not None
              for row in results))
        db.close()

        # Пропущенное задание: страниц по нему не прислали.
        second = drill.start_evening(drill.open_evening(30)['id'])
        drill.scan({'id': second['id'], 'photos': [blank_png('1')]})
        done = drill.grade_evening({'id': second['id'],
                                    'assignment': [1]})
        skipped = [row for row in done['results'] if row.get('skipped')]
        t('нерешённые задания помечены, а не сломали разбор',
          len(skipped) == len(second['questions']) - 1)
        t('у пропущенного задания баллов нет',
          all(row['earned'] is None for row in skipped))
        db = store.connect(drill.db_path)
        t('пропущенное задание не роняет силу приёма',
          all(row['skill'] not in store.states(db) for row in skipped))
        db.close()

        # Поправка раскладки руками должна пережить повторный разбор.
        third = drill.start_evening(drill.open_evening(30)['id'])
        drill.scan({'id': third['id'], 'photos': [blank_png('1'), blank_png('2')]})
        fixed = drill.grade_evening({'id': third['id'], 'assignment': [2, 2]})
        t('исправленная раскладка применяется',
          [page['question'] for page in fixed['pages']] == [2, 2])
        t('исправленная раскладка сохранена в наборе',
          [page['question'] for page in drill.evening(third['id'])['pages']]
          == [2, 2])
    finally:
        grader.grade, grader.assign_pages = real_grade, real_assign

print('\n=== раскладка, когда модель не ответила ===')
with tempfile.TemporaryDirectory() as tmp:
    real_assign = grader.assign_pages
    real_grade = grader.grade
    grader.grade = fake_grade

    def broken(pages, count, model=None):
        raise grader.GraderError('нет ключа')

    grader.assign_pages = broken
    try:
        drill = service.Drill(db_path=os.path.join(tmp, 'fallback.sqlite'))
        drill.rng = random.Random(9)
        opened = drill.start_evening(drill.open_evening(30)['id'])
        scanned = drill.scan({'id': opened['id'],
                              'photos': [blank_png('1')] * 4})
        t('без раскладки страницы всё равно приняты',
          len(scanned['pages']) == 4)
        t('раскладка помечена как догаданная', scanned['guessed'] is True)
        t('ни одна страница не осталась без задания',
          all(page['question'] for page in scanned['pages']))
    finally:
        grader.assign_pages, grader.grade = real_assign, real_grade

print(f'\n{passed} проверок пройдено, {failed} провалено')
sys.exit(1 if failed else 0)
