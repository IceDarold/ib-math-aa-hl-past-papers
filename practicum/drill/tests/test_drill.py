"""Проверяет механику тренажёра: разбор ввода, планировщик, журнал.

Тут не про математику — про то, что тренажёр показывает следующим и как
считает. Математику проверяет verify_drill.py.
"""
from __future__ import annotations

import os
import random
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
t('счёт есть у всех приёмов B1 и C1',
  len(skills_with_compute) == len(GENERATORS))

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
