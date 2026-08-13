"""Прогоняет все проверки практикума A5 с эталонными ответами из раздела решений.

Ответы не берутся из решений на веру: корни уравнений подставляются обратно
в условие, система Виета решается заново, а формы записи проверяются на то,
что полярная и декартова засчитываются одинаково.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

NB = os.path.join(ROOT, 'practicum/number_algebra',
                  'practicum-a5-complex-forms.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(",
                                   "check_complex(", "check_complex_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []


def t(name, ok):
    res.append((name, ok))


z = Symbol('z')
A, B = symbols('A B', real=True)

print('=== эталонные ответы ===')
t('1', check_complex('Задание 1', 3 * sqrt(2) * exp(-I * pi / 4), D['Задание 1']))
t('2', check_complex('Задание 2', 2 * exp(I * pi / 3), D['Задание 2']))
t('3m', check_num('Задание 3, |u|', sp.Abs(-1 + sqrt(3) * I), 6, D['Задание 3, |u|']))
t('3a', check_expr('Задание 3, arg u', sp.arg(-1 + sqrt(3) * I), D['Задание 3, arg u']))

# задание 4: дробь упрощается здесь, а не переписывается из решения
w4 = sp.simplify(4 * I / (1 + I * sqrt(3)))
print(f'\n4i/(1 + i√3) упрощается до {w4}')
t('4', check_complex('Задание 4', w4, D['Задание 4']))
t('5m', check_num('Задание 5, |w|', sp.Abs(w4), 6, D['Задание 5, |w|']))
t('5a', check_expr('Задание 5, arg w', sp.arg(w4), D['Задание 5, arg w']))

# задание 6: система решается, а не списывается
q, p = symbols('q p', real=True)
zq = sp.expand((5 + q * I)**2 + I * (5 + q * I))
sol6 = sp.solve([sp.re(zq) + p, sp.im(zq) - 25], [p, q], dict=True)[0]
print(f'\nсистема задания 6 -> p = {sol6[p]}, q = {sol6[q]}')
t('6p', check_num('Задание 6, p', sol6[p], 6, D['Задание 6, p']))
t('6q', check_num('Задание 6, q', sol6[q], 6, D['Задание 6, q']))

# задание 7: корни подставляются в исходное уравнение
roots7 = [sp.Integer(2), -1 + sqrt(3) * I, -1 - sqrt(3) * I]
print('\nпроверка корней z² = 2z̄ подстановкой:')
for r in roots7:
    resid = sp.simplify(sp.expand(r**2 - 2 * sp.conjugate(r)))
    print(f'  z = {r}: невязка {resid}')
    t(f'7-подстановка {r}', resid == 0)
t('7', check_complex_set('Задание 7', roots7, D['Задание 7']))
t('7-ноль исключён', sp.simplify(sp.Integer(0)**2 - 2 * sp.conjugate(0)) == 0)

# задание 8: раскрытие произведения и аргумент
bb = Symbol('bb', real=True)
prod8 = sp.expand((1 + bb * I) * ((1 - bb**2) - 2 * bb * I))
print(f'\nz1z2 = {sp.factor(prod8)}')
t('8-форма', sp.simplify(prod8 - (1 + bb**2) * (1 - bb * I)) == 0)
t('8-arg при b=-1', sp.simplify(sp.arg(prod8.subs(bb, -1)) - pi / 4) == 0)
t('8', check_expr('Задание 8', -1, D['Задание 8']))

# задание 9
t('9k', check_num('Задание 9, k', 3, 6, D['Задание 9, k']))
t('9zw', check_complex('Задание 9, zw', 16 * (cos(-pi) + I * sin(-pi)), D['Задание 9, zw']))
t('9-условие', sp.simplify(sp.im(sp.expand(16 * exp(I * (1 - 2 * 3) * pi / 5)))) == 0)

# задание 10: оба пути markscheme считаются независимо и сверяются
a2_short = (2 + sqrt(3)) / 2
a2_long = sp.solve(sp.Eq(4 * Symbol('A2', positive=True)**2
                         - 4 * sqrt(3) * Symbol('A2', positive=True) - 1, 0),
                   Symbol('A2', positive=True))[0]
print(f'\nзадание 10: короткий путь {sp.simplify(a2_short)}, '
      f'через биквадратное {sp.simplify(a2_long)}')
t('10-пути совпали', sp.simplify(a2_short - a2_long) == 0)
aa, bbv = sqrt(a2_short), sqrt((2 - sqrt(3)) / 2)
t('10-подстановка', sp.simplify(sp.expand((aa + bbv * I)**2) - (sqrt(3) + I)) == 0)
t('10a', check_expr('Задание 10, a^2', a2_short, D['Задание 10, a^2']))
t('10b', check_expr('Задание 10, b^2', (2 - sqrt(3)) / 2, D['Задание 10, b^2']))

# задание 11: корни берутся из решения кубического, а не из текста
roots11 = sp.solve(z**3 + 5 * z**2 + 10 * z + 12, z)
print(f'\nкорни кубического: {roots11}')
rest = [r for r in roots11 if sp.simplify(r - (-1 + sqrt(3) * I)) != 0]
t('11', check_complex_set('Задание 11', rest, D['Задание 11']))

# задание 12: система Виета решается заново
solA = sp.solve([sp.Eq(A + B, -2), sp.Eq(A**2 + B**2, 20)], [A, B])
avals = sorted({s[0] for s in solA}, key=lambda v: float(v))
print(f'\nсистема Виета -> a ∈ {avals}')
t('12', check_complex_set('Задание 12', avals, D['Задание 12']))

print('\n=== форма записи не влияет ===')
for name, form in [('тригонометрическая', 3 * sqrt(2) * (cos(-pi / 4) + I * sin(-pi / 4))),
                   ('декартова', 3 - 3 * I),
                   ('через градусы', 3 * sqrt(2) * exp(-I * 45 * pi / 180))]:
    t(f'1~{name}', check_complex(f'Задание 1 как {name}', form, D['Задание 1']))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'form', 2: 'form', 3: 'modarg', 4: 'cart', 5: 'modarg', 6: 'parts',
        7: 'parts', 8: 'prop', 9: 'prop', 10: 'parts', 11: 'roots', 12: 'roots',
        13: 'cart', 14: 'roots', 15: 'prop'}
t('trigger', trigger_check(good, KEY))
print('  порча пункта 7:', end=' ')
t('trigger-neg', not trigger_check({**good, 7: 'cart'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('n1', not check_expr('arg по арктангенсу без четверти', -pi / 3, D['Задание 3, arg u']))
t('n2', not check_complex_set('поделили на b, потеряв корни', [2], D['Задание 7']))
t('n3', not check_num('знак p потерян', 19, 6, D['Задание 6, p']))
t('n4', not check_expr('a^2 как в разметке корпуса', (sqrt(3) + 1) / 2, D['Задание 10, a^2']))
t('n5', not check_complex('zw без учёта модуля', -1, D['Задание 9, zw']))
t('n6', not check_complex_set('только положительное a', [2], D['Задание 12']))

bad = [n for n, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
