"""Прогоняет все проверки практикума E7 с эталонными ответами из раздела решений."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import json
import sympy as sp
from kit import *

x, y, v, t, C = sp.symbols('x y v t C')
K = sp.Symbol('k')

NB = os.path.join(ROOT, 'practicum/calculus',
                  'practicum-e7-differential-equations.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

results = []


def t_(name, ok):
    results.append((name, ok))


print('=== задания с эталонными ответами ===')
t_('1', verify_ode('Задание 1', sp.sin(x - sp.pi/4) + 1, sp.cos(x - sp.pi/4), ic=(3*sp.pi/4, 2)))
t_('2', verify_implicit('Задание 2', sp.Eq(x**2 + y**2, K), sp.Eq(x**2 + y**2, K)))
t_('3', verify_ode('Задание 3', 4 - 2*sp.exp(-x/10), (4 - y)/10, ic=(0, 2)))

a, b = sp.Integer(-4), -4 - sp.pi
t_('4a', check_expr('Задание 4(a), a', a, D['Задание 4(a), a']))
t_('4b', check_expr('Задание 4(b), b', b, D['Задание 4(b), b']))
t_('4whole', verify_ode('Задание 4 целиком', a/(2*x + sp.sin(2*x) + b),
                        y**2*sp.cos(x)**2, ic=(sp.pi/2, 1)))

t_('5', check_expr('Задание 5(b), k', sp.log(9)/10, D['Задание 5(b), k']))  # эквивалентная форма

t_('6', verify_implicit('Задание 6', sp.Eq(x**2 - 2*x*y - y**2, 4),
                        sp.Eq(x**2 - 2*x*y - y**2, 4)))
t_('7', verify_ode('Задание 7', 3*sp.exp(x) - x - 1, y + x, ic=(0, 2)))
t_('8', verify_ode('Задание 8', x**2 - 2*x - 3 + C*sp.exp(-x), x**2 - 5 - y))

# --- задание 9: числа считаем честно, а не берём из решения ---
pts = euler(lambda a_, b_: (4 - b_)/10, 0.0, 2.0, 0.1, 5)
approx = pts[-1][1]
exact = float(4 - 2*sp.exp(sp.Rational(-5, 100)))
err = abs(approx - exact)
print(f'\nЭйлер: {approx!r}, точное: {exact!r}, ошибка: {err!r}')
t_('9a', check_num('Задание 9(a)', approx, 4, D['Задание 9(a)']))
t_('9b', check_num('Задание 9(b)', err, 3, D['Задание 9(b)']))

# знак ошибки: y'' = -(4-y)/100 < 0 при y<4 => завышает
print('  завышает?', approx > exact)
t_('9c', approx > exact)

# --- задание 10 ---
p2 = euler(lambda a_, b_: (b_**2 - 2*a_**2)/a_**2, 1.0, 3.0, 0.1, 5)
print('\nЭйлер 10:', [f'{q:.4f}' for _, q in p2])
t_('10a', check_num('Задание 10(a)', p2[-1][1], 3, D['Задание 10(a)']))

vx = sp.Function('v')(x)
got = sp.simplify(sp.solve(sp.Eq(sp.diff(vx*x, x), ((vx*x)**2 - 2*x**2)/x**2),
                           sp.diff(vx, x))[0]*x)
want = vx**2 - vx - 2
t_('10b', sp.simplify(got - want) == 0)
print(('✅' if results[-1][1] else '❌'), f'Задание 10(b): x dv/dx = {got}')

# --- задание 11 (на таймере) ---
t_('11a', verify_ode('11(a)', 2*x*sp.sqrt(1 - sp.log(x)), (y**2 - 2*x**2)/(x*y), ic=(1, 2)))
t_('11b', check_set('11(b)', [-sp.sqrt(2), sp.sqrt(2)], D['11(b)']))  # обратный порядок

# --- тренажёр ---
print()
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'int', 2: 'sep', 3: 'if', 4: 'hom', 5: 'pf', 6: 'sep',
        7: 'if', 8: 'hom', 9: 'int', 10: 'eu', 11: 'pf', 12: 'sep'}
t_('trigger', trigger_check(good, KEY))
bad = {**good, 3: 'sep'}
print('  подсунули ошибку в п.3:', end=' ')
t_('trigger-neg', not trigger_check(bad, KEY))

# --- негативные проверки: неверные ответы обязаны падать ---
print('\n=== негативные (должны быть ❌) ===')
t_('neg1', not verify_ode('минус потерян', 4/(2*x + sp.sin(2*x) - 4 - sp.pi),
                          y**2*sp.cos(x)**2, ic=(sp.pi/2, 1)))
t_('neg2', not verify_ode('потеряно v в подстановке', 3*sp.exp(x) - x, y + x, ic=(0, 2)))
t_('neg4', not check_set('m без минуса', [sp.sqrt(2)], D['11(b)']))
t_('neg5', not check_expr('пустой ответ', ..., D['Задание 5(b), k']))
t_('neg3', not check_num('шаг лишний', euler(lambda a_, b_: (4 - b_)/10, 0.0, 2.0, 0.1, 6)[-1][1],
                         4, D['Задание 9(a)']))

bad_n = sum(1 for n, ok in results if not ok)
print(f'\n{"ВСЁ ПРОШЛО" if bad_n == 0 else "ПРОВАЛЫ: " + str([n for n, ok in results if not ok])}'
      f'  ({len(results) - bad_n}/{len(results)})')
