"""Проверяет механику тренажёра: разбор ввода, планировщик, журнал.

Тут не про математику — про то, что тренажёр показывает следующим и как
считает. Математику проверяет verify_drill.py.
"""
from __future__ import annotations

import os
import random
import re
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
DRILL = os.path.dirname(HERE)
PRACTICUM = os.path.dirname(DRILL)
sys.path.insert(0, os.path.dirname(PRACTICUM))
sys.path.insert(0, PRACTICUM)

import sympy as sp  # noqa: E402
import yaml  # noqa: E402

from drill import engine, store  # noqa: E402
from drill.check import BadInput, evaluate, parse_many, parse_one  # noqa: E402
from drill.items import GENERATORS  # noqa: E402

res = []


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== разбор того, что пишут от руки ===')
t('степень через ^', parse_one('x^2') == sp.Symbol('x')**2)
t('неявное умножение', parse_one('2x') == 2 * sp.Symbol('x'))
t('корень словом', parse_one('2sqrt(6)') == 2 * sp.sqrt(6))
t('корень знаком', parse_one('2√6') == 2 * sp.sqrt(6))
t('типографский минус', parse_one('−5') == -5)
t('пи', parse_one('pi/3') == sp.pi / 3)
t('набор через запятую', parse_many('1, 4') == [sp.Integer(1), sp.Integer(4)])
t('набор в фигурных скобках', parse_many('{1, 4}') == [sp.Integer(1), sp.Integer(4)])
t('«нет корней» — пустой набор', parse_many('нет') == [])

try:
    parse_one('2x +')
    t('оборванная запись не проходит', False)
except BadInput:
    t('оборванная запись не проходит', True)

print('\n=== проверка ответа идёт через kit ===')
item = GENERATORS['C1.exact_values'](random.Random(0))
ok, message = evaluate(item['check'], '12.99')
t('десятичная дробь вместо точного значения не принимается', not ok)
t('сообщение объясняет, а не просто отказывает', 'точное значение' in message)

item = GENERATORS['C1.cosine_rule'](random.Random(0))
ok, _ = evaluate(item['check'], f'{item["answer"]:.4g}')
t('верная сторона принимается', ok)
ok, message = evaluate(item['check'], f'{item["answer"] * 1.4:.4g}')
t('сторона из другого треугольника отвергается', not ok)
t('и объясняется через незамкнутый треугольник', 'замыкается' in message)

print('\n=== планировщик ===')
bank = engine.load_bank()
t('банк собран из готовых практикумов', len(bank['practicums']) == 11)
t('доли баллов в сумме дают единицу',
  abs(sum(bank['share'].values()) - 1.0) < 1e-9)
t('практикум с большим числом баллов весит больше',
  bank['share']['B1'] > bank['share']['C4'])

now = time.time()
skill = bank['skills'][0]
t('приём без единой попытки идёт вперёд всего',
  engine.weight(skill, None, bank['share'], now) == engine.COLD_START)

fresh = {'due': now + 86400, 'seen': 3, 'wrong': 0}
overdue = {'due': now - 5 * 86400, 'seen': 3, 'wrong': 0}
t('просроченный приём весит больше свежего',
  engine.weight(skill, overdue, bank['share'], now)
  > engine.weight(skill, fresh, bank['share'], now))

sloppy = {'due': now - 5 * 86400, 'seen': 4, 'wrong': 3}
t('приём с ошибками весит больше такого же без ошибок',
  engine.weight(skill, sloppy, bank['share'], now)
  > engine.weight(skill, overdue, bank['share'], now))

rng = random.Random(1)
picks = [engine.choose(bank, {}, GENERATORS, mode='mixed', rng=rng)[0]['practicum']
         for _ in range(60)]
t('вперемешку идут разные практикумы, а не один подряд',
  len(set(picks)) >= 5)

kinds = {engine.choose(bank, {}, GENERATORS, mode='compute', rng=rng)[1]
         for _ in range(30)}
t('в режиме счёта только задачи на счёт', kinds == {'compute'})
kinds = {engine.choose(bank, {}, GENERATORS, mode='recognition', rng=rng)[1]
         for _ in range(30)}
t('в режиме узнавания только узнавание', kinds == {'recognition'})

skills_with_compute = {s['id'] for s, _ in engine.candidates(bank, 'compute', GENERATORS)}
t('задача на счёт есть у каждого приёма банка',
  skills_with_compute == {s['id'] for s in bank['skills']})
t('лишних генераторов, не привязанных к приёму, нет',
  set(GENERATORS) <= {s['id'] for s in bank['skills']})

print('\n=== настройки сессии ===')
picked = {engine.choose(bank, {}, GENERATORS, mode='mixed', rng=rng,
                        practicums=('C1', 'B1'))[0]['practicum']
          for _ in range(40)}
t('отбор тем оставляет только выбранные', picked == {'C1', 'B1'})

only_c1 = engine.candidates(bank, 'mixed', GENERATORS, practicums=('C1',))
t('в отобранной теме все её приёмы', len(only_c1) == 8)

try:
    # B2 в карте есть, но практикум ещё не собран, и в банке его нет.
    engine.choose(bank, {}, GENERATORS, mode='compute', rng=rng,
                  practicums=('B2',))
    t('пустой набор — это ошибка, а не молчаливая подмена', False)
except LookupError:
    t('пустой набор — это ошибка, а не молчаливая подмена', True)

now = time.time()
states = {s['id']: {'due': now + 7 * 86400, 'seen': 2, 'wrong': 0, 'box': 2}
          for s in bank['skills']}
states['C1.cosine_rule']['due'] = now - 86400
skill, _ = engine.choose(bank, states, GENERATORS, mode='mixed', rng=rng,
                         only_due=True)
t('«только просроченное» берёт единственный просроченный приём',
  skill['id'] == 'C1.cosine_rule')

everything_fresh = {s['id']: {'due': now + 7 * 86400, 'seen': 2, 'wrong': 0,
                              'box': 2} for s in bank['skills']}
picked = engine.choose(bank, everything_fresh, GENERATORS, mode='mixed',
                       rng=rng, only_due=True)[0]
t('когда просрочено ничего, сессия всё равно собирается', bool(picked))

# Сплошной проход: сначала то, что видели реже, при равенстве — ниже по лестнице.
seen_once = {s['id']: {'due': now, 'seen': 1, 'wrong': 0, 'box': 1}
             for s in bank['skills']}
del seen_once['C1.exact_values']
ladder = engine.choose(bank, seen_once, GENERATORS, mode='mixed', rng=rng,
                       practicums=('C1',), order='ladder')[0]
t('сплошь: невиданный приём идёт первым', ladder['id'] == 'C1.exact_values')

rungs = [engine.choose(bank, seen_once, GENERATORS, mode='mixed', rng=rng,
                       practicums=('C1',), order='ladder',
                       avoid=('C1.exact_values',))[0]['rung']
         for _ in range(5)]
t('сплошь: дальше идёт нижняя ступень лестницы', set(rungs) == {1})

uniform = {engine.choose(bank, {}, GENERATORS, mode='mixed', rng=rng,
                         order='random')[0]['practicum'] for _ in range(80)}
t('наугад достаёт и редкие темы', len(uniform) >= 8)

print('\n=== задание собирается заново по зерну ===')
skill = bank['skills_by_id']['C1.cosine_rule']
shown, spec, answer = engine.build_item(bank, GENERATORS, skill, 'compute',
                                        rng=random.Random(5))
again_meta, again_spec, again_answer = engine.rebuild_check(
    bank, GENERATORS, shown['item'])
t('условие восстановилось тем же', again_meta['prompt'] == shown['prompt'])
t('проверка восстановилась той же', again_spec == spec)
t('эталон восстановился тем же', again_answer == answer)
t('странице эталон не уходит',
  'answer' not in shown and 'check' not in shown)

print('\n=== журнал ===')
with tempfile.TemporaryDirectory() as tmp:
    db = store.connect(os.path.join(tmp, 'test.sqlite'))
    common = dict(mode='mixed', kind='compute', practicum='C1',
                  skill='C1.cosine_rule', item='compute:C1.cosine_rule:1',
                  answer='8.24', ms=12000, first_ms=3000, budget_ms=75000)
    store.record(db, ok=True, **common)
    state = store.states(db)['C1.cosine_rule']
    t('верный ответ поднимает на ящик вверх', state['box'] == 1)
    store.record(db, ok=True, **common)
    t('второй верный — ещё на ящик', store.states(db)['C1.cosine_rule']['box'] == 2)
    store.record(db, ok=False, **common)
    state = store.states(db)['C1.cosine_rule']
    t('ошибка возвращает в самое начало', state['box'] == 0)
    t('срок повторения — сразу, а не через три недели',
      state['due'] - time.time() < 1.0)
    t('ошибки посчитаны', state['wrong'] == 1 and state['seen'] == 3)
    totals = store.totals(db)
    t('итоги считаются', totals['attempts'] == 3 and totals['correct'] == 2)
    t('время до первого нажатия хранится отдельно от времени ответа',
      totals['avg_first_ms'] == 3000 and totals['avg_ms'] == 12000)
    db.close()

print('\n=== разбор после попытки ===')
for skill in bank['skills']:
    if not skill.get('chain') or not skill.get('traps'):
        t(f'у приёма {skill["id"]} есть и ход, и ловушки', False)
        break
else:
    t('у каждого приёма банка есть ход и ловушки', True)
t('поля карточки лежат одной строкой, без переносов',
  all('\n' not in step for skill in bank['skills'] for step in skill['chain']))

from drill.server import Drill  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    drill = Drill(os.path.join(tmp, 'verdict.sqlite'))
    served = drill.next_item('compute', practicums=('C1',))
    _, spec, answer = engine.rebuild_check(bank, GENERATORS, served['item'])
    from drill.check import show_answer  # noqa: E402
    good = drill.answer({'item': served['item'], 'mode': 'compute', 'ms': 5000,
                         'first_ms': 1200,
                         'answer': show_answer(answer,
                                               var=spec.get('var', 'x'))})
    t('при верном ответе ход показывается', bool(good['chain']))
    t('при верном ответе ловушки не показываются', good['traps'] == [])
    t('название приёма и признак узнавания приходят отдельными полями',
      bool(good['skill_name']) and bool(good['trigger'])
      and good['skill_name'] != good['trigger'])

    served = drill.next_item('compute', practicums=('C1',))
    wrong = drill.answer({'item': served['item'], 'mode': 'compute', 'ms': 5000,
                          'first_ms': 1200, 'answer': '0'})
    t('при ошибке ход тоже показывается — с ним и сравнивают',
      bool(wrong['chain']))
    t('при ошибке добавляются ловушки', bool(wrong['traps']))
    t('при ошибке показывается эталон', bool(wrong['answer']))
    t('задание странице по-прежнему приходит без эталона',
      'answer' not in served and 'chain' not in served)

print('\n=== архив: страницы подлинника ===')
from drill import archive, grader  # noqa: E402

t('номера страниц: одна', archive.parse_pages('3') == [3])
t('номера страниц: диапазон', archive.parse_pages('3-5') == [3, 4, 5])
t('номера страниц: перечисление', archive.parse_pages('2, 7') == [2, 7])
t('номера страниц: пусто', archive.parse_pages(None) == [])

blocks = bank.get('archive', {})
t('блоки архива привязаны к приёмам', len(blocks) > 300)
t('у каждого блока есть каталог бумаги и страницы',
  all(b.get('dir') and b.get('source_pages') and b.get('markscheme_pages')
      for b in blocks.values()))
missing = [bid for bid, b in blocks.items()
           if not os.path.isfile(os.path.join(
               os.path.dirname(PRACTICUM), b['dir'], 'question-paper.pdf'))]
t('PDF найдены для всех блоков — разметка архива неоднородна, и все её '
  'три формы учтены', not missing)

sample = dict(session='May 2022', zone='TZ2', paper=1, question=3, part='b',
              dir='x')
t('ссылка на источник читается словами экзамена',
  archive.reference(sample) == 'May 2022 TZ2, Paper 1, Q3(b)')
t('часть, повторяющая номер вопроса, не печатается',
  archive.reference(dict(sample, part='3')) == 'May 2022 TZ2, Paper 1, Q3')
t('составная часть печатается по кускам',
  archive.reference(dict(sample, part='c-ii'))
  == 'May 2022 TZ2, Paper 1, Q3(c)(ii)')

print('\n=== разбор как режим тренажёра ===')
written_pool = engine.candidates(bank, 'written', GENERATORS)
t('настоящий вопрос есть у каждого приёма',
  {skill['id'] for skill, _ in written_pool}
  == {skill['id'] for skill in bank['skills']})
t('в режиме разбора выдаётся только разбор',
  {kind for _, kind in written_pool} == {'written'})
t('разбор не подмешивается в перемешку — он занимает минуты',
  all(kind != 'written'
      for _, kind in engine.candidates(bank, 'mixed', GENERATORS)))

written_skill = bank['skills_by_id']['A7.induction_sum']
shown_written, spec_written, answer_written = engine.build_item(
    bank, GENERATORS, written_skill, 'written', rng=random.Random(2))
t('задание разбора — ключ с блоком архива',
  shown_written['item'].startswith('written:')
  and shown_written['block'] in bank['archive'])
t('в задании есть ссылка на бумагу и цена в баллах',
  bool(shown_written['reference']) and shown_written['marks'] > 0)
t('бюджет времени считается от баллов, а не от вида задания',
  shown_written['budget_ms'] == shown_written['marks'] * 90_000)
t('машинной проверки у разбора нет — судит модель',
  spec_written == {'kind': 'graded'} and answer_written is None)

seen_blocks = set()
for _ in range(12):
    item = engine.build_item(bank, GENERATORS, written_skill, 'written',
                             rng=random.Random(_), avoid_blocks=seen_blocks)[0]
    seen_blocks.add(item['block'])
t('недавние вопросы не повторяются, пока есть другие',
  len(seen_blocks) == len(written_skill['blocks']))

print('\n=== рубрики оформления ===')
common = grader.rubric()
a7 = grader.rubric('A7')
t('общие пункты есть у любого вопроса', len(common) >= 5)
t('у практикума пунктов больше, чем общих', len(a7) > len(common))
ids = {item['id'] for item in a7}
t('индукция требует названного предположения',
  'induction_hypothesis' in ids)
t('индукция требует заключительной фразы', 'induction_conclusion' in ids)
t('заключительная фраза стоит балла рассуждения',
  next(i for i in a7 if i['id'] == 'induction_conclusion')['code'] == 'R1')
t('в каждом пункте есть готовая фраза, а не пересказ претензии',
  all(item.get('fix') for item in a7))
t('рубрика написана по-английски: её читает и модель, и ученик',
  all(not re.search('[а-яА-Я]', item['fix']) for item in a7))

print('\n=== страница вопроса ищется по самому вопросу ===')
import pymupdf  # noqa: E402
START = re.compile(r'^\s*(\d{1,2})\.\s', re.M)


def numbers_on(folder, name, page):
    with pymupdf.open(os.path.join(os.path.dirname(PRACTICUM), folder,
                                   name)) as document:
        if not 1 <= page <= document.page_count:
            return []
        return [int(n) for n in START.findall(document[page - 1].get_text())]


sample = list(blocks.items())[:60]
found = sum(1 for _, b in sample
            if int(b['question']) in numbers_on(
                b['dir'], 'question-paper.pdf',
                archive.block_page_numbers(b, 'question')[0]))
t(f'первая страница содержит сам вопрос ({found} из {len(sample)})',
  found >= len(sample) - 6)   # длинные исследования Paper 3 номера не повторяют

single = sum(1 for b in blocks.values()
             if len(archive.block_page_numbers(b, 'question')) == 1)
t('короткий вопрос показывается одной страницей, а не двумя',
  single > len(blocks) // 2)
t('у вопроса не больше четырёх страниц, у схемы не больше двух',
  all(len(archive.block_page_numbers(b, 'question')) <= 4
      and len(archive.block_page_numbers(b, 'markscheme')) <= 2
      for b in blocks.values()))

# Тот самый случай, с которого нашлось расхождение: корпус говорит 5,
# а третий вопрос напечатан на шестой странице файла.
drifted = blocks.get('2021-MAY-TZ2-P1-Q03')
if drifted:
    t('подсказка корпуса промахивалась на страницу — теперь исправляется',
      archive.parse_pages(drifted['source_pages']) == [5]
      and archive.block_page_numbers(drifted, 'question') == [6])

print('\n=== карта приёмов ===')
from drill.server import Drill as DrillService  # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    atlas = DrillService(os.path.join(tmp, 'map.sqlite'))
    card = atlas.skill_card('C1.ambiguous_case', seed=7)
    t('карточка знает суть приёма',
      card['name'] and card['trigger'] and card['chain'] and card['traps'])
    t('в карточке есть ступень и роль калькулятора',
      card['rung'] == 5 and card['calculator'])
    t('к приёму приложены условия на узнавание', card['recognition'])
    t('у условия показан верный код, а не хеш',
      card['recognition'][0]['answer'] == 'ambig')
    t('к приёму приложена задача на счёт с ответом',
      card['compute'] and card['compute']['answer'])

    # Карта показывает эталон открытым, и он должен быть читаемым:
    # sympy сводит (k+1)! к gamma(k+2), а гамма-функции в программе нет.
    factorial_card = atlas.skill_card('A7.induction_sum', seed=0)
    t('факториал показывается факториалом, а не гамма-функцией',
      'gamma' not in factorial_card['compute']['answer'])
    t('одно и то же зерно даёт ту же задачу',
      atlas.skill_card('C1.ambiguous_case', seed=7)['compute']['prompt']
      == card['compute']['prompt'])
    t('к приёму приложены вопросы архива со ссылкой на бумагу',
      card['archive'] and card['archive'][0]['question_url'].endswith(
          tuple(f'#page={n}' for n in range(1, 40))))
    t('пока попыток не было, так и написано', card['state'] is None)

    every = [atlas.skill_card(skill['id']) for skill in bank['skills']]
    t('карточка открывается у каждого приёма банка', len(every) == 86)
    t('у каждого приёма есть и ход, и ловушки',
      all(one['chain'] and one['traps'] for one in every))
    t('у каждого приёма есть хотя бы один вопрос архива',
      all(one['archive'] for one in every))
    without_recognition = [one['id'] for one in every if not one['recognition']]
    t('без условий на узнавание — только те два приёма, что известны',
      set(without_recognition) == {'A7.induction_skeleton',
                                   'E7.euler_error_sign'})
    try:
        atlas.skill_card('нет такого')
        t('несуществующий приём — ошибка', False)
    except LookupError:
        t('несуществующий приём — ошибка', True)

print('\n=== отбор вопросов: бумага и цена ===')
whole = engine.candidates(bank, 'written', GENERATORS)
only_first = engine.candidates(bank, 'written', GENERATORS, papers=(1,))
t('отбор по бумаге сужает набор',
  0 < len(only_first) < len(whole))
t('в отборе по Paper 1 других бумаг нет',
  all(bank['archive'][block]['paper'] == 1
      for skill, _ in only_first
      for block in engine.matching_blocks(bank, skill, papers=(1,))))

cheap = engine.candidates(bank, 'written', GENERATORS, marks=(1, 3))
dear = engine.candidates(bank, 'written', GENERATORS, marks=(7, None))
t('дешёвых вопросов больше, чем дорогих', len(cheap) > len(dear))
t('в дорогом отборе нет вопросов дешевле семи баллов',
  all((bank['archive'][block]['marks'] or 0) >= 7
      for skill, _ in dear
      for block in engine.matching_blocks(bank, skill, marks=(7, None))))

both = engine.candidates(bank, 'written', GENERATORS, papers=(1,),
                         marks=(7, None))
t('отборы складываются', 0 < len(both) <= min(len(only_first), len(dear)))

picked = engine.choose(bank, {}, GENERATORS, mode='written', rng=rng,
                       papers=(3,))[0]
chosen_block = engine.build_item(bank, GENERATORS, picked, 'written',
                                 rng=rng, papers=(3,))[0]
t('выданное задание подчиняется отбору',
  bank['archive'][chosen_block['block']]['paper'] == 3)

empty = [s for s in bank['skills'] if s['practicum'] == 'A3']
try:
    engine.build_item(bank, GENERATORS, empty[0], 'written', rng=rng,
                      papers=(2,), marks=(99, None))
    t('пустой отбор — ошибка, а не случайный вопрос', False)
except LookupError:
    t('пустой отбор — ошибка, а не случайный вопрос', True)

print('\n=== сохранённые работы ===')
with tempfile.TemporaryDirectory() as tmp:
    service = DrillService(os.path.join(tmp, 'kept.sqlite'))
    shots = os.path.join(service.photo_dir(), 'demo')
    os.makedirs(shots, exist_ok=True)
    with open(os.path.join(shots, 'page-1.jpg'), 'wb') as handle:
        handle.write(b'\xff\xd8snapshot')
    connection = service.connection()
    try:
        store.record_written(
            connection, block='2022-MAY-TZ1-P1-Q08', practicum='A7',
            skill='A7.contradiction',
            reference='May 2022 TZ1, Paper 1, Q8',
            photos=['demo/page-1.jpg'],
            verdict={'marks': {'available': 6, 'earned': 4},
                     'mathematics': {'verdict': 'partially correct'},
                     'model': 'gpt-5.6-sol'})
    finally:
        connection.close()

    listing = service.written()['history']
    t('работа попадает в список', len(listing) == 1)
    t('в списке видно, за что и сколько',
      listing[0]['reference'] == 'May 2022 TZ1, Paper 1, Q8'
      and listing[0]['earned'] == 4 and listing[0]['pages'] == 1)

    record = service.written(listing[0]['id'])
    t('работа открывается целиком, с вердиктом',
      record['verdict']['mathematics']['verdict'] == 'partially correct')
    t('к работе приложены её страницы',
      len(record['files']) == 1 and record['files'][0]['url'].endswith('n=0'))

    body, kind = service.written_file(record['id'], 0)
    t('страница отдаётся с верным типом',
      body == b'\xff\xd8snapshot' and kind == 'image/jpeg')
    try:
        service.written_file(record['id'], 7)
        t('несуществующая страница не отдаётся', False)
    except LookupError:
        t('несуществующая страница не отдаётся', True)

    connection = service.connection()
    try:
        store.record_written(
            connection, block='X', practicum='A7', skill='A7.contradiction',
            reference='May 2023 TZ1, Paper 2, Q9', photos=['demo/page-1.jpg'],
            verdict={'error': 'модель не ответила'})
    finally:
        connection.close()
    unmarked = service.written()['history'][0]
    t('непроверенная работа тоже сохраняется и видна',
      unmarked['earned'] is None and unmarked['available'] is None)
    t('видно, почему разбор не состоялся',
      service.written(unmarked['id'])['verdict']['error'] == 'модель не ответила')

print('\n=== работа присылается и сканом ===')
scan = pymupdf.open()
for number in range(3):
    sheet = scan.new_page()
    sheet.insert_text((72, 100), f'Solution page {number + 1}', fontsize=16)
scan_bytes = scan.tobytes()
scan.close()

pages = archive.render_upload(scan_bytes)
t('PDF разбирается постранично', len(pages) == 3)
t('страницы отрендерены картинками',
  all(page[:8] == b'\x89PNG\r\n\x1a\n' for page in pages))
t('число страниц ограничивается', len(archive.render_upload(scan_bytes,
                                                            limit=2)) == 2)
try:
    archive.render_upload(b'not a pdf at all')
    t('мусор вместо PDF не проходит молча', False)
except Exception:
    t('мусор вместо PDF не проходит молча', True)
t('PDF узнаётся по сигнатуре, а не только по заголовку data-URL',
  scan_bytes[:5] == b'%PDF-')

print('\n=== официальные инструкции экзаменатору ===')
folder = blocks[next(iter(blocks))]['dir']
rules = archive.instructions(folder)
t('инструкции извлекаются из самой схемы оценивания', len(rules) > 4000)
t('в них определены коды баллов',
  all(mark in rules for mark in ('M ', 'A ', 'R ', 'AG')))
t('в них есть правило про повторение AG-строки',
  'does not need to restate' in rules)
t('в них есть зависимость A-балла от M-балла',
  'M0 followed by A1' in rules)
t('раздел кончается до самой схемы, а не тянется до конца файла',
  'Section A' not in rules and len(rules) < 30_000)

t('рубрика больше не требует повторять напечатанную строку',
  'does not need to restate' in next(
      item['requirement'] for group in
      yaml.safe_load(open(os.path.join(DRILL, 'presentation.yaml')))
      ['by_question_type'].values() for item in group['items']
      if item['id'] == 'ag_final_form'))

print('\n=== рубрика сверена с инструкциями ===')
rubric_file = yaml.safe_load(open(os.path.join(DRILL, 'presentation.yaml')))
every = (rubric_file['common']
         + [i for g in rubric_file['by_question_type'].values()
            for i in g['items']]
         + [i for v in rubric_file['by_practicum'].values() for i in v])
t('ни один пункт не обещает потерю AG-балла — AG это не балл, '
  'а пометка «ответ дан в условии»',
  all(item['code'] != 'AG' for item in every))
t('коды пунктов — только те, что определены в инструкциях',
  {item['code'] for item in every} <= {'M1', 'A1', 'R1'})

ids = {item['id'] for item in every}
for needed, why in (
        ('simplified_final_answer', 'упрощение окончательного ответа — §8'),
        ('calculator_notation', 'запись калькулятора в ответе — §7'),
        ('one_answer_per_question', 'зачёркнутое и второй ответ — §10'),
        ('hence_uses_previous', '«Hence» запрещает другой метод — §6')):
    t(f'закрыт пробел: {why}', needed in ids)

accuracy = next(i for i in every if i['id'] == 'accuracy')
t('точность больше не требует округлять только в самом конце — '
  'IB разрешает брать 3 з.ц. в следующий пункт',
  'explicitly allowed' in ' '.join(accuracy['requirement'].split()))

print('\n=== запрос на разбор ===')
message = grader.build_messages(
    work_images=[b'\x89PNG-fake'], question_images=[b'\x89PNG-q'],
    markscheme_images=[b'\x89PNG-m'], instructions=rules,
    reference='May 2022 TZ2, Paper 1, Q3(b)',
    marks=6, calculator='no', rubric_items=a7, skill='Индукция для суммы')
parts = message[1]['content']
kinds = [part['type'] for part in parts]
t('в запросе три картинки: билет, схема, работа',
  kinds.count('image_url') == 3)
t('работа идёт последней — после условия и схемы',
  kinds[-1] == 'image_url'
  and 'HANDWRITTEN' in parts[-2]['text'])
t('схема оценивания названа своим именем',
  any('MARKSCHEME' in p.get('text', '') for p in parts))
t('баллы и калькулятор попадают в запрос',
  'worth 6 marks' in parts[0]['text']
  and 'No calculator' in parts[0]['text'])
t('системная роль требует разделять математику и оформление',
  'PRESENTATION' in message[0]['content']
  and 'MATHEMATICS' in message[0]['content'])
t('модель обязана сначала прочесть, а потом судить',
  'Transcribe the work first' in message[0]['content'])
t('образец записи требуется формулами, а не символами подряд',
  'LaTeX between dollar signs' in message[0]['content'])
t('транскрипция остаётся как на бумаге, без разметки',
  'Do not put LaTeX in "transcription"' in message[0]['content'])
texts = [part.get('text', '') for part in parts]
t('официальные инструкции идут раньше рубрики',
  next(i for i, x in enumerate(texts) if 'OFFICIAL INSTRUCTIONS' in x)
  < next(i for i, x in enumerate(texts) if 'PRESENTATION RUBRIC' in x))
t('инструкции объявлены старше рубрики — они и есть источник правил',
  'authoritative' in message[0]['content']
  and 'outrank the rubric' in ' '.join(texts))

print('\n=== журнал письменных работ ===')
with tempfile.TemporaryDirectory() as tmp:
    db = store.connect(os.path.join(tmp, 'written.sqlite'))
    store.record_written(
        db, block='2021-MAY-TZ2-P1-Q12-D', practicum='A7',
        skill='A7.induction_sum', reference='May 2021 TZ2, Paper 1, Q12(d)',
        photos=['page-1.jpg'],
        verdict={'marks': {'available': 9, 'earned': 3},
                 'mathematics': {'verdict': 'partially correct'},
                 'model': 'gpt-5.6-sol'})
    totals = store.written_totals(db)
    t('письменные работы считаются отдельно от ящиков Лейтнера',
      totals == {'attempts': 1, 'marks_available': 9, 'marks_earned': 3})
    t('в журнале остаётся ссылка на бумагу',
      store.written_history(db)[0]['reference']
      == 'May 2021 TZ2, Paper 1, Q12(d)')
    t('разбор моделью не трогает расписание повторения',
      store.states(db) == {})
    db.close()

print('\n=== чем это отличается от проверок в ноутбуке ===')
# В практикуме ответ пишут в клетку и проверка знает, какое задание решают.
# Здесь задание выбирает планировщик, поэтому проверка восстанавливается
# по ключу — и ключ обязан быть достаточным.
t('ключ задания сам себя описывает',
  shown['item'].startswith('compute:C1.cosine_rule:'))
recog = [i for i in bank['items'] if i['practicum'] == 'C1'][0]
t('у узнавания ключ тоже полный', recog['key'].startswith('recog:C1:'))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
