"""Проверяет механику проверок из темы пределов.

Ответ здесь — предел, и это десятое понятие равенства ответов в серии.
У предела нет числа, которое можно взять и сравнить: он определён тем, к
чему выражение подходит. Поэтому verify_limit не хранит эталона вовсе —
он подставляет в само выражение из условия точки, приближающиеся к
искомой, и требует, чтобы названное число оказалось тем, к чему эти
значения сходятся.

Решает при этом самая тонкая ступень лестницы, а не средняя по ней: у
медленной дроби (3x-1)/(2x+1) на x = 10^5 ошибка ещё 10^-5, и по такой
ступени 1.5 не отличить от 1.49999. Отдельный тест ниже держит это
свойство: проверка обязана принимать медленную сходимость и всё равно
отвергать соседнее число.

verify_indeterminate сторожит балл, который в архиве стоит отдельно:
«show that the limit is in indeterminate form». Он смотрит на числитель и
знаменатель порознь и не верит на слово — 0/0 там, где на самом деле
oo/oo, не проходит.

Запуск:  python practicum/tests/test_kit_limit.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

res = []
n, b, m, c = sp.symbols('n b m c')
R = sp.Rational


def T(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


# Май 2021 TZ1 P1 Q8 — правило Лопиталя один раз.
ARCTAN = sp.atan(2 * x) / sp.tan(3 * x)
# Май 2024 TZ2 P1 Q8 — дважды, и после второго раза форма уже не 0/0.
SEC = (sp.sec(x)**4 - sp.cos(x)**2) / (x**4 - x**2)
# Май 2022 TZ1 P1 Q12(e) — трижды.
ECOS = (sp.exp(x) * sp.cos(x) - 1 - x) / x**3
# Май 2023 TZ1 P3 Q1(c)(i) — форма oo/oo, точка на бесконечности.
AREA = (sp.exp(b) - b - 1) / sp.exp(b)
# Май 2024 TZ1 P1 Q11(f) — сокращение и старшие степени.
RAT = (3 * x - 1) / (2 * x + 1)

print('=== verify_limit принимает верный предел ===')
T('лопиталь один раз', verify_limit('  2/3', R(2, 3), ARCTAN))
T('лопиталь дважды', verify_limit('  -3', -3, SEC))
T('лопиталь трижды', verify_limit('  -1/3', -R(1, 3), ECOS))
T('форма oo/oo на бесконечности',
  verify_limit('  1', 1, AREA, var=b, point=sp.oo))
T('устранимая особенность в точке', verify_limit('  4', 4, RAT, point=-1))
T('старшие степени на бесконечности',
  verify_limit('  3/2', R(3, 2), RAT, point=sp.oo))
T('ряд Маклорена вместо лопиталя',
  verify_limit('  1', 1, (x**2 * sp.exp(x) - x**2)**3 / x**9))
T('бесконечный предел', verify_limit('  oo', sp.oo, 1 / x**2))
T('односторонний предел',
  verify_limit('  1', 1, sp.sign(x), side='+'))

print('\n=== verify_limit отвергает неверный ===')
T('соседнее число', not verify_limit('  1', 1, ARCTAN))
T('округление вместо точного значения',
  not verify_limit('  0.667', 0.667, ARCTAN))
T('остановка на полпути: 0/0 после первого применения',
  not verify_limit('  0', 0, ECOS))
T('переменная осталась в ответе',
  not verify_limit('  с x', x, ARCTAN))
T('двусторонний предел, стороны расходятся',
  not verify_limit('  1', 1, sp.sign(x)))
T('незаполненный ответ печатает ⬜', not verify_limit('  пусто', ..., ARCTAN))

print('\n=== медленная сходимость ===')
# На x = 10^5 дробь равна 1.49999, и по этой ступени 3/2 не отличить от
# 1.49999. Решает ступень 10^8, где ошибка уже 2.5e-8.
T('медленная сходимость всё-таки принимается',
  verify_limit('  3/2', R(3, 2), RAT, point=sp.oo))
T('и соседнее число при этом отвергается',
  not verify_limit('  1.49999', R(149999, 100000), RAT, point=sp.oo))

print('\n=== предел через параметр ===')
COSN = (sp.cos(x)**n - 1) / x**2
F1 = (n * x**(n + 2) - (n + 1) * x**(n + 1) + x) / (x - 1)**2
T('ответ через n верен при каждом n',
  verify_limit('  -n/2', -n / 2, COSN, params={n: (1, 2, 5, 9)}))
T('лопиталь с параметром в показателе',
  verify_limit('  n(n+1)/2', n * (n + 1) / 2, F1, point=1, params={n: (2, 3, 7)}))
T('неверная зависимость от n не проходит',
  not verify_limit('  -n', -n, COSN, params={n: (1, 2, 5)}))
T('параметр без params не проходит', not verify_limit('  -n/2', -n / 2, COSN))
T('списки разной длины — ошибка условия',
  not verify_limit('  -n/2', -n / 2, COSN, params={n: (1, 2), m: (3,)}))

print('\n=== verify_indeterminate ===')
T('0/0 названо верно',
  verify_indeterminate('  0/0', '0/0', n * x**(n + 2) - (n + 1) * x**(n + 1) + x,
                       (x - 1)**2, point=1, params={n: (2, 5)}))
T('oo/oo названо верно',
  verify_indeterminate('  oo/oo', 'oo/oo', sp.exp(b) - b - 1, sp.exp(b),
                       var=b, point=sp.oo))
T('0/0 вместо oo/oo не проходит',
  not verify_indeterminate('  0/0', '0/0', sp.exp(b) - b - 1, sp.exp(b),
                           var=b, point=sp.oo))
T('там, где неопределённости нет, не проходит',
  not verify_indeterminate('  нет', '0/0', sp.cos(x), x**2))
T('форма пишется строкой', not verify_indeterminate('  мусор', 'junk', x, x))
T('незаполненный ответ печатает ⬜',
  not verify_indeterminate('  пусто', ..., x, x))

print('\n=== сообщения на английском ===')
language('en')
T('verify_limit говорит по-английски', not verify_limit('  english', 1, ARCTAN))
T('verify_indeterminate говорит по-английски',
  not verify_indeterminate('  english', '0/0', sp.cos(x), x**2))
language('ru')

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
