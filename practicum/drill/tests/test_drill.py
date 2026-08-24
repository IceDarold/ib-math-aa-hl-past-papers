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

print('\n=== запрос на разбор ===')
message = grader.build_messages(
    work_images=[b'\x89PNG-fake'], question_images=[b'\x89PNG-q'],
    markscheme_images=[b'\x89PNG-m'], reference='May 2022 TZ2, Paper 1, Q3(b)',
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
