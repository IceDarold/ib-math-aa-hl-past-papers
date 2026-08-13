"""Прогоняет все проверки практикума C3 с эталонными ответами из раздела решений."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

x, theta = sp.symbols('x theta')
P = sp.pi

NB = os.path.join(ROOT, 'practicum/geometry',
              'practicum-c3-trigonometric-equations.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []


def t(name, ok):
    res.append((name, ok))


print('=== тождества ===')
t('T1a', verify_identity('Задание Т1(a)', 4*sp.cos(x)/sp.sin(x) + sp.sin(x),
                         4*sp.cot(x) + sp.sin(x)))
t('T1b', check_num('Задание Т1(b)', 8/sp.sqrt(5) + sp.sqrt(5)/3, 3, D['Задание Т1(b)']))
t('T2', check_expr('Задание Т2(b)', (sp.sqrt(6) - sp.sqrt(2))/4, D['Задание Т2(b)']))

T3 = 2*sp.sin(x)*sp.cos(x) + (1 - 2*sp.sin(x)**2) - 1
t('T3a', verify_identity('Задание Т3, переход', T3, sp.sin(2*x) + sp.cos(2*x) - 1))
t('T3b', verify_identity('Задание Т3, тождество', T3,
                         2*sp.sin(x)*(sp.cos(x) - sp.sin(x))))
t('T4', check_expr('Задание Т4', -sp.sqrt(5)/2, D['Задание Т4']))
t('T5', check_expr('Задание Т5(b)', P/4, D['Задание Т5(b)']))

# check_expr сверяет хеш канонической формы: убеждаемся, что эквивалентные
# записи ответа проходят, иначе верное решение получило бы ❌
for name, form in [('atan(1)', sp.atan(1)), ('45*pi/180', 45*P/180),
                   ('acos(1/sqrt2)', sp.acos(1/sp.sqrt(2))), ('2*pi/8', 2*P/8)]:
    t(f'T5~{name}', check_expr(f'Задание Т5(b) как {name}', form, D['Задание Т5(b)']))

print('\n=== эталонные ответы ===')
t('1', verify_roots('Задание 1', [P, 3*P], 6 + 6*sp.cos(x), (0, 4*P)))
t('2', verify_roots('Задание 2', [25, 115], sp.tan(2*x - 5*P/180) - 1, (0, 180), deg=True))
t('3', check_expr('Задание 3', 17*P/6, D['Задание 3']))
t('4', verify_roots('Задание 4', [P/6, 5*P/6], 2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)))
t('5', verify_roots('Задание 5', [-P/2, P/6, 5*P/6], sp.cos(2*x) - sp.sin(x), (-P, P)))
t('6', verify_roots('Задание 6', [3*P/2], 2*sp.cos(2*theta) - 5*sp.cos(theta) + 2,
                    (P, 2*P), var=theta))
t('7', verify_roots('Задание 7', [P/6, P/2, 5*P/6], sp.cos(x) - sp.sin(2*x), (0, P)))
t('8', verify_roots('Задание 8', [P/6, 5*P/6], sp.cos(x)**2 - 3*sp.sin(x)**2, (0, P)))
t('9', verify_roots('Задание 9', [7*P/12, 11*P/12],
                    (2*sp.sin(2*theta)**2 - 5*sp.sin(2*theta) - 3)/(sp.sin(2*theta) - 1),
                    (0, P), var=theta))

# 10: посторонний корень отсеивается подстановкой в исходное уравнение
good = -1/sp.sqrt(10)
t('10', abs(float(sp.acos(good) + sp.acos(3*good)) - float(3*P/2)) < 1e-9)
print(('✅' if res[-1][1] else '❌'), 'Задание 10: x = -1/sqrt(10) даёт 3*pi/2')
extr = 1/sp.sqrt(10)
t('10-neg', abs(float(sp.acos(extr) + sp.acos(3*extr)) - float(3*P/2)) > 1e-9)
print(('✅' if res[-1][1] else '❌'), 'Задание 10: x = +1/sqrt(10) отбраковывается')

t('11', check_num('Задание 11', 1.8954942670339809, 3, D['Задание 11']))
t('12', verify_roots('Задание 12', [P/4, 7*P/6, 5*P/4, 11*P/6],
                     sp.sin(2*x) + sp.cos(2*x) - 1 + sp.cos(x) - sp.sin(x), (0, 2*P)))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good_k = {1: 'base', 2: 'arg', 3: 'pyth', 4: 'dbl', 5: 'fact', 6: 'tan',
          7: 'select', 8: 'gdc', 9: 'arg', 10: 'dbl', 11: 'select', 12: 'fact',
          13: 'sum', 14: 'pyth', 15: 'sum'}
t('trigger', trigger_check(good_k, KEY))
print('  порча пункта 5:', end=' ')
t('trigger-neg', not trigger_check({**good_k, 5: 'dbl'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('n1', not verify_roots('поделили на cos x', [P/6, 5*P/6], sp.cos(x) - sp.sin(2*x), (0, P)))
t('n2', not verify_roots('один оборот вместо двух', [P],
                         6 + 6*sp.cos(x), (0, 4*P)))
t('n3', not verify_roots('потерян минус у тангенса', [P/6],
                         sp.cos(x)**2 - 3*sp.sin(x)**2, (0, P)))
t('n4', not verify_roots('забыта левая половина области', [P/6, 5*P/6],
                         sp.cos(2*x) - sp.sin(x), (-P, P)))
t('n5', not verify_roots('область не пересчитана для 2x', [7*P/6],
                         (2*sp.sin(2*theta)**2 - 5*sp.sin(2*theta) - 3)/(sp.sin(2*theta) - 1),
                         (0, P), var=theta))
t('n6', not check_expr('шаг на 2pi вместо 4pi', 23*P/6, D['Задание 3']))
t('n7', not check_expr('Т4 без учёта четверти', sp.sqrt(5)/2, D['Задание Т4']))
t('n8', not check_expr('Т2 со знаком плюс', (sp.sqrt(6) + sp.sqrt(2))/4, D['Задание Т2(b)']))
t('n9', not verify_identity('Т1 с потерянным множителем',
                            sp.cos(x)/sp.sin(x) + sp.sin(x), 4*sp.cot(x) + sp.sin(x)))

# Т3 допускает не одну форму cos 2x: «неудобная» тоже даёт верное тождество,
# просто выкладка длиннее. Проверка обязана её принимать
print('\n=== другая форма cos 2x в Т3 (должна пройти) ===')
t('T3-alt', verify_identity('Т3 через 2cos^2 x - 1',
                            2*sp.sin(x)*sp.cos(x) + (2*sp.cos(x)**2 - 1) - 1,
                            2*sp.sin(x)*(sp.cos(x) - sp.sin(x))))

bad = [n for n, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
