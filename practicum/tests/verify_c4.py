"""Прогоняет все проверки практикума C4 с эталонными ответами из раздела решений.

Числа не берутся из решений на веру: период, высота прилива, суммарное время
выше порога и число максимумов пересчитываются здесь заново из условия.
Если бы в решении была арифметическая ошибка, сошлись бы хеш и решение,
но не сошёлся бы пересчёт.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

NB = os.path.join(ROOT, 'practicum/functions',
                  'practicum-c4-sinusoidal-models.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []


def check(name, ok):
    res.append((name, ok))


# --- модель прилива собирается здесь заново, из условия задачи ---
MIN_H, MAX_H, PERIOD, FIRST_HIGH = sp.Rational(11, 5), sp.Rational(34, 5), 12, sp.Rational(9, 2)
amp = (MAX_H - MIN_H) / 2
mid = (MAX_H + MIN_H) / 2
b_tide = 2 * pi / PERIOD
c_tide = FIRST_HIGH - sp.Rational(PERIOD, 4)
tide = lambda tt: amp * sin(b_tide * (tt - c_tide)) + mid

print('=== модель прилива, пересчитанная из условия ===')
print(f'  a = {amp}, d = {mid}, b = {b_tide}, c = {c_tide}')
check('прилив: максимум там, где сказано', abs(float(tide(FIRST_HIGH)) - float(MAX_H)) < 1e-12)
print(f'  H({FIRST_HIGH}) = {float(tide(FIRST_HIGH))} — должно быть {float(MAX_H)}')

print('\n=== эталонные ответы ===')
check('1', check_num('Задание 1', 2 * pi / sp.Rational(78, 10), 3, D['Задание 1']))
check('2', check_expr('Задание 2', pi / 2, D['Задание 2']))
check('3a', check_num('Задание 3, a', amp, 3, D['Задание 3, a']))
check('3d', check_num('Задание 3, d', mid, 3, D['Задание 3, d']))
check('4', check_expr('Задание 4', b_tide, D['Задание 4']))
check('5a', check_num('Задание 5, a', -0.4, 3, D['Задание 5, a']))
check('5b', check_num('Задание 5, b', 1.4, 3, D['Задание 5, b']))
check('6', check_num('Задание 6', c_tide, 3, D['Задание 6']))
check('7a', check_num('Задание 7, a', -55, 3, D['Задание 7, a']))
check('7b', check_expr('Задание 7, b', 2 * pi / 20, D['Задание 7, b']))
check('7c', check_num('Задание 7, c', 65, 3, D['Задание 7, c']))

# задание 8: система решается, а не списывается
a_s, b_s = sp.symbols('a_s b_s')
sol = sp.solve([a_s * tan(pi / 6) + b_s - 5, a_s * tan(2 * pi / 3) + b_s - 7], [a_s, b_s])
print(f'\nсистема задания 8 -> a = {sol[a_s]}, b = {sol[b_s]}')
check('8a', check_expr('Задание 8, a', sol[a_s], D['Задание 8, a']))
check('8b', check_expr('Задание 8, b', sol[b_s], D['Задание 8, b']))

check('9', check_num('Задание 9', tide(12), 3, D['Задание 9']))

# задание 10: максимумы отсчитываются от первого, а не делением интервала
T_w = float(2 * pi / sp.Rational(78, 10))
maxima = [T_w / 2 + k * T_w for k in range(20)]
in_window = [m for m in maxima if m <= 5]
print(f'\nмаксимумы груза: {[round(m, 3) for m in in_window]}')
check('10', check_num('Задание 10', len(in_window), 3, D['Задание 10']))

# задание 11: корни порога ищутся заново
u = sp.asin((5 - mid) / amp)
hours = 2 * (sp.Rational(PERIOD, 2) - PERIOD * u / pi)
print(f'\nсуммарное время выше 5 м: {float(hours)}')
check('11', check_num('Задание 11', hours, 3, D['Задание 11']))

check('12', check_num('Задание 12', c_tide - sp.Rational(50, 60), 3, D['Задание 12']))

# задание 13: оба способа markscheme обязаны давать один ответ
q_min = 7 + 4 - sp.Rational(5, 2)                    # -4 + 2.5 + q >= 7
r1 = 4 * sin(-3 * pi / 2) + sp.Rational(5, 2) + q_min
r2 = 7 + 2 * 4                                       # минимум + двойная амплитуда
print(f'\nзадание 13: способ 1 даёт {float(r1)}, способ 2 даёт {r2}')
check('13-оба способа совпали', sp.simplify(r1 - r2) == 0)
check('13', check_num('Задание 13', r1, 3, D['Задание 13']))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'per', 2: 'per', 3: 'amp', 4: 'per', 5: 'sign', 6: 'phase',
        7: 'build', 8: 'build', 9: 'use', 10: 'use', 11: 'thresh',
        12: 'phase', 13: 'bound', 14: 'bound', 15: 'sign'}
check('trigger', trigger_check(good, KEY))
print('  порча пункта 11:', end=' ')
check('trigger-neg', not trigger_check({**good, 11: 'use'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
check('n1', not check_expr('период тангенса по формуле синуса', pi, D['Задание 2']))
check('n2', not check_num('амплитуда без минуса', 0.4, 3, D['Задание 5, a']))
check('n3', not check_num('одна полоса из двух', 6 - 12 * u / pi, 3, D['Задание 11']))
check('n4', not check_num('сдвиг прибавлен, а не вычтен',
                          c_tide + sp.Rational(50, 60), 3, D['Задание 12']))
check('n5', not check_num('50 минут не переведены в часы', c_tide - 50, 3, D['Задание 12']))
check('n6', not check_num('высота в градусном режиме',
                          float(amp * sp.sin(sp.rad(float(b_tide * (12 - c_tide)))) + mid),
                          3, D['Задание 9']))
check('n7', not check_num('r без учёта минимума', 6.5, 3, D['Задание 13']))

bad = [n for n, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
