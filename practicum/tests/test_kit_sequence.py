"""Проверяет механику последовательностей: progression и семь проверок над ней.

Отдельный тест нужен по той же причине, по какой он есть у verify_roots
и у фигур: verify_a1 сверяет ответы одного практикума, а здесь сверяется
сама проверка — что она принимает любую верную запись, ловит типовые
промахи и не падает на пустом ответе.

Главное свойство, ради которого всё затевалось: внутри проверки нет
ни u₁ + (n − 1)d, ни n/2 (2u₁ + (n − 1)d). Член она получает сложением
шага, сумму — сложением членов, наибольшую сумму — перебором. Поэтому
5 + 2(n − 1), 2n + 3 и n + (n + 3) проходят одинаково, и поэтому же
логарифмические члены работают наравне с числовыми.

Запуск:  python practicum/tests/test_kit_sequence.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

n = Symbol('n')
m = Symbol('m')
xp = Symbol('x', positive=True)
ok, bad = [], []


def t(name, got, expect=True):
    (ok if got == expect else bad).append(name)


print('=== прогрессия как правило ===')
ap = progression(5, 2)                      # 5, 7, 9, 11, 13, ...
t('term', verify_term('пятый член', 13, ap, 5))
t('term-1', verify_term('первый член', 5, ap, 1))
t('total', verify_total('сумма пяти', 45, ap, 5))
t('total-1', verify_total('сумма одного', 5, ap, 1))
t('start', verify_start('первые четыре', [5, 7, 9, 11], ap))
t('helper-term', term(ap, 5) == 13)
t('helper-total', total(ap, 5) == 45)

print('\n=== ответ-выражение сверяется при нескольких n ===')
t('law', verify_term('u_n = 2n + 3', 2*n + 3, ap, n))
t('law-other', verify_term('та же формула иначе', 5 + 2*(n - 1), ap, n))
t('law-third', verify_term('и ещё иначе', n + (n + 3), ap, n))
t('law-sum', verify_total('S_n = n(n + 4)', n*(n + 4), ap, n))
t('law-wrong', verify_term('формула мимо', 2*n + 1, ap, n), False)
t('law-lucky', verify_term('совпадает только при n = 1', n**2 + 4, ap, n), False)

print('\n=== в обе стороны: ответ внутри прогрессии ===')
t('back', verify_term('ваш восьмой член равен восьми', 8,
                      progression(-6, 2), 8))
t('back-sum', verify_total('и первые восемь дают восемь', 8,
                           progression(-6, 2), 8))
t('back-bad', verify_term('а при другой паре — нет', 8,
                          progression(-6, 3), 8), False)
t('back-index', verify_total('номер тоже бывает ответом', 0,
                             progression(36, -6), 13))

print('\n=== номер обязан быть целым и положительным ===')
t('zero', verify_total('ноль членов', 0, progression(36, -6), 0), False)
t('neg', verify_term('отрицательный номер', 5, ap, -2), False)
t('frac', verify_term('дробный номер', 5, ap, 2.5), False)
t('symbol-answer', verify_term('буква вместо номера при числовом ответе',
                               13, ap, m), False)
t('far', verify_term('слишком далеко', 5, ap, 10 ** 6), False)

print('\n=== типовые промахи названы ===')
t('next', verify_term('следующий член', 15, ap, 5), False)
t('prev', verify_term('предыдущий член', 11, ap, 5), False)
t('step-n', verify_term('шаг сделан n раз', 15, ap, 5), False)
t('sum-for-term', verify_term('сумма вместо члена', 45, ap, 5), False)
t('term-for-sum', verify_total('член вместо суммы', 13, ap, 5), False)
t('one-more', verify_total('сложено на один больше', 60, ap, 5), False)
t('one-less', verify_total('сложено на один меньше', 32, ap, 5), False)
t('doubled', verify_total('сумма удвоена', 90, ap, 5), False)
t('halved', verify_total('половина суммы', 22.5, ap, 5), False)
t('start-wrong', verify_start('третий член не тот', [5, 7, 8], ap), False)
t('start-empty', verify_start('пустой список', [], ap), False)
t('not-number', verify_term('выражение там, где число', 2*m, ap, 5), False)

print('\n=== постоянная разность ===')
t('arith', verify_arithmetic('три члена', [2, Rational(1, 2), -1]))
t('arith-five', verify_arithmetic('пять членов', [1, 3, 5, 7, 9]))
t('arith-no', verify_arithmetic('геометрическая', [1, 2, 4]), False)
t('arith-two', verify_arithmetic('двух членов мало', [1, 2]), False)
t('step', verify_step('разность', Rational(-3, 2), [2, Rational(1, 2), -1]))
t('step-sign', verify_step('знак наоборот', Rational(3, 2),
                           [2, Rational(1, 2), -1]), False)
t('step-double', verify_step('через один член', -3,
                             [2, Rational(1, 2), -1]), False)
t('step-nonconst', verify_step('разность непостоянна', 1, [1, 2, 4]), False)

print('\n=== буква внутри членов ===')
c = -m**2/(m + 2)
t('letter', verify_arithmetic('m, -c/m, c при c = -m^2/(m+2)',
                              [m, -c/m, c], m, (1, 3, -5)))
t('letter-bad', verify_arithmetic('а при c = m^2/(m+2) не выходит',
                                  [m, -(-c)/m, -c], m, (1, 3, -5)), False)
t('letter-lucky', verify_arithmetic('совпадение при одном значении',
                                    [m, m + 1, m + 3], m, (1, 3, -5)), False)
t('letter-step', verify_step('разность с буквой', -c/m - m,
                             [m, -c/m, c], m, (1, 3, -5)))

print('\n=== члены-логарифмы ===')
logs = progression(9 + log(9), -4 - log(3))
t('log-step', verify_step('разность через ln 3', -4 - log(3),
                          [9 + log(9), 5 + log(3), 1 + log(1)]))
t('log-total', verify_total('сумма первых десяти', -90 - 25*log(3), logs, 10))
t('log-decimal', verify_total('та же сумма десятичной дробью',
                              -117.4629, logs, 10))
t('log-lost', verify_total('логарифмическая часть потеряна', -90, logs, 10),
  False)
series = progression(log(xp), -log(xp)/3)
t('log-series', verify_total('ряд из логарифмов', log(1/xp**3), series, 9))
t('log-series-bad', verify_total('и не при восьми членах',
                                 log(1/xp**3), series, 8), False)

print('\n=== наибольшая сумма ===')
falling = progression(60, Rational(-5, 2))
t('peak', verify_peak('наибольшая сумма', 750, falling))
t('peak-at', verify_peak('и номер', 750, falling, at=25))
t('peak-at-other', verify_peak('и соседний номер тоже', 750, falling, at=24))
t('peak-at-bad', verify_peak('а этот нет', 750, falling, at=26), False)
t('peak-short', verify_peak('сумма оборвана раньше', 747.5, falling), False)
t('peak-wrong', verify_peak('мимо', 700, falling), False)
t('peak-growing', verify_peak('у растущей максимума нет', 750,
                              progression(1, 2)), False)

print('\n=== пустой ответ даёт ⬜, а не падение ===')
empty = progression(..., ...)
t('blank-term', verify_term('пустой член', ..., ap, 5), False)
t('blank-seq', verify_term('пустая прогрессия', 13, empty, 5), False)
t('blank-index', verify_term('пустой номер', 13, ap, ...), False)
t('blank-total', verify_total('пустая сумма', ..., ap, 5), False)
t('blank-start', verify_start('пустой список', [...], ap), False)
t('blank-arith', verify_arithmetic('пустой член в списке', [2, ..., -1]), False)
t('blank-step', verify_step('пустая разность', ..., [1, 3, 5]), False)
t('blank-peak', verify_peak('пустая наибольшая', ..., falling), False)
t('blank-peak-at', verify_peak('пустой номер максимума', 750, falling, at=...),
  False)
t('blank-helper', term(empty, 5) is Ellipsis)
t('blank-helper-total', total(empty, 5) is Ellipsis)
t('blank-predicate', blank(1, ..., 3) and not blank(1, 2, 3))

print('\n=== формулы темы внутри проверки нет ===')
# Смотреть надо на код, а не на текст: в строках документации обе формулы
# как раз названы — там сказано, что их-то проверка и не использует.
import ast

source = open(os.path.join(ROOT, 'practicum', 'kit.py')).read()
tree = ast.parse(source)
names = {'progression', '_run', '_index', '_as_value', '_agree', '_seq_report',
         '_sampled', '_differences', 'term', 'total', 'blank', 'verify_term',
         'verify_total', 'verify_start', 'verify_arithmetic', 'verify_step',
         'verify_peak'}
bodies = {}
for node in tree.body:
    if isinstance(node, ast.FunctionDef) and node.name in names:
        stripped = list(node.body)
        if (stripped and isinstance(stripped[0], ast.Expr)
                and isinstance(stripped[0].value, ast.Constant)
                and isinstance(stripped[0].value.value, str)):
            stripped = stripped[1:]
        bodies[node.name] = '\n'.join(ast.unparse(line) for line in stripped)
t('all-found', set(bodies) == names)

# Члены порождает ровно одна функция, и она только складывает.
walk = ast.parse(bodies['_run'])
t('walk-adds-only', not any(isinstance(node, (ast.Mult, ast.Pow, ast.Div))
                            for node in ast.walk(walk)))
t('walk-uses-add', any(isinstance(node, ast.Add) for node in ast.walk(walk)))

code = '\n'.join(bodies.values())
t('no-step-times', 'seq[2] *' not in code and '* seq[2]' not in code)
t('no-n-minus-one', '(n - 1)' not in code and 'index - 1) *' not in code)
t('no-half-sum', 'index / 2' not in code and 'index * (' not in code)

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
