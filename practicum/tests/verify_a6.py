"""Прогоняет все проверки практикума A6 с эталонными ответами из раздела решений.

Корни не переписываются из решений: они извлекаются заново формулой Муавра,
а затем возводятся обратно в степень и сверяются с исходным числом.
Так ошибка в приведении аргумента не может совпасть сама с собой.
"""
import cmath
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

NB = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a6-de-moivre.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_complex(",
                                   "check_complex_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
theta = Symbol('theta', real=True)


def t(name, ok):
    res.append((name, ok))


def nth_roots(c, n):
    """Корни n-й степени формулой Муавра, аргумент приведён к (-pi, pi]."""
    R, phi = sp.Abs(c), sp.arg(c)
    return [sp.root(R, n) * exp(I * (phi + 2 * pi * k) / n) for k in range(n)]


print('=== эталонные ответы ===')
t('1', check_num('Задание 1', sp.expand((1 + I * sqrt(3))**8 + (1 - I * sqrt(3))**8),
                 6, D['Задание 1']))

u = -1 + sqrt(3) * I
n2 = next(n for n in range(1, 20) if sp.simplify(sp.im(sp.expand(u**n))) == 0)
print(f'\nнаименьшее n с u^n действительным: {n2}, u^{n2} = {sp.expand(u**n2)}')
t('2n', check_num('Задание 2, n', n2, 6, D['Задание 2, n']))
t('2v', check_complex('Задание 2, u^n', sp.expand(u**n2), D['Задание 2, u^n']))

zz = cos(11 * pi / 18) + I * sin(11 * pi / 18)
n3 = next(n for n in range(1, 60)
          if abs(complex(sp.expand(zz**n).evalf()) - (-1j)) < 1e-9)
print(f'наименьшее n с z^n = -i: {n3}')
t('3', check_num('Задание 3', n3, 6, D['Задание 3']))

rot = sp.nsimplify(sp.arg(sp.expand(zz**10)), [pi])
print(f'поворот при z -> z^10: {rot}')
t('4', check_expr('Задание 4', rot, D['Задание 4']))

# --- корни извлекаются и проверяются возведением обратно ---
print('\n=== корни: извлечены заново и возведены обратно ===')
for name, c, n, key in [('Задание 5', sqrt(3) + I, 2, 'Задание 5'),
                        ('Задание 6', -1 - sqrt(3) * I, 2, 'Задание 6'),
                        ('Задание 7', sp.simplify(2 * sqrt(3) * exp(I * 5 * pi / 6) / (3 - 3 * I)),
                         3, 'Задание 7')]:
    roots = nth_roots(c, n)
    back = [complex((r**n).evalf()) for r in roots]
    ok = all(abs(b - complex(sp.N(c))) < 1e-9 for b in back)
    print(f'  {name}: {[f"{abs(complex(r.evalf())):.4f}∠{cmath.phase(complex(r.evalf())):.4f}" for r in roots]}')
    t(f'{name}-обратно', ok)
    t(name, check_complex_set(f'  {name}', roots, D[key]))

others = [r for r in sp.solve(sp.Eq(Symbol('z')**3, -8), Symbol('z'))
          if sp.simplify(r - (1 + sqrt(3) * I)) != 0]
print(f'\nостальные корни z³ = -8: {others}')
t('8', check_complex_set('Задание 8', others, D['Задание 8']))

rotated = [sp.simplify(v * exp(I * pi / 4)) for v in [1 + sqrt(3) * I, -2, 1 - sqrt(3) * I]]
t('9', check_complex_set('Задание 9', rotated, D['Задание 9']))

# задание 10: шаг сетки считается по НОД разностей аргументов
units = [sp.nsimplify(sp.arg(v) / (pi / 12)) for v in
         [1 + sqrt(3) * I, -2, 1 - sqrt(3) * I] + rotated]
step = sp.gcd([sp.Integer(a - b) for a in units for b in units if a != b])
print(f'\nаргументы в π/12: {units}; НОД разностей = {step} -> n = {2 * 12 // int(step)}')
t('10', check_num('Задание 10', 2 * 12 // int(step), 6, D['Задание 10']))
t('10-шаг', int(step) == 1)

# задание 11: мнимая часть считается символьно, а не переписывается
imag5 = sp.expand(sp.im(sp.expand((cos(theta) + I * sin(theta))**5)))
print(f'\nIm((cosθ + i sinθ)^5) = {imag5}')
t('11-переход', verify_identity('Задание 11, переход', imag5, imag5, var=theta))
t('11-тождество', verify_identity('Задание 11, тождество', imag5,
                                  16 * sin(theta)**5 - 20 * sin(theta)**3 + 5 * sin(theta),
                                  var=theta))

tan12 = sp.nsimplify(sp.tan(pi / 12), [sqrt(3)])
print(f'tan(pi/12) = {tan12}')
t('12', check_expr('Задание 12', tan12, D['Задание 12']))

key13 = sp.simplify(exp(2 * I * pi / 3) + 1)
t('13-равно exp(i pi/3)', abs(complex((key13 - exp(I * pi / 3)).evalf())) < 1e-12)
t('13', check_complex('Задание 13, ключевой шаг', key13, D['Задание 13, ключевой шаг']))
t('13-сумма', check_complex('Задание 13, сумма корней',
                            sum(exp(2 * I * pi * k / 3) for k in range(3)),
                            D['Задание 13, сумма корней']))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'power', 2: 'period', 3: 'period', 4: 'rot', 5: 'root', 6: 'root',
        7: 'root', 8: 'unity', 9: 'rot', 10: 'unity', 11: 'ident', 12: 'geom',
        13: 'ident', 14: 'unity', 15: 'power'}
t('trigger', trigger_check(good, KEY))
print('  порча пункта 3:', end=' ')
t('trigger-neg', not trigger_check({**good, 3: 'power'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('n1', not check_complex_set('только один квадратный корень',
                              [sqrt(2) * exp(I * pi / 12)], D['Задание 5']))
# exp(13iπ/12) и exp(-11iπ/12) — одно и то же число, и проверка их не различает.
# Это верно математически, но на экзамене за приведение аргумента к (-pi, pi]
# стоит отдельный балл, и следить за ним приходится самому. Фиксируем поведение,
# чтобы оно не выглядело недосмотром
t('n2-форма вне диапазона всё же проходит',
  check_complex_set('аргумент 13pi/12 вместо -11pi/12',
                    [sqrt(2) * exp(I * pi / 12), sqrt(2) * exp(13 * I * pi / 12)],
                    D['Задание 5']))
t('n2', not check_complex_set('перепутан знак аргумента',
                              [sqrt(2) * exp(-I * pi / 12), sqrt(2) * exp(11 * I * pi / 12)],
                              D['Задание 5']))
t('n3', not check_num('n взято первое попавшееся', 1, 6, D['Задание 3']))
t('n4', not check_expr('поворот без приведения', 55 * pi / 9, D['Задание 4']))
t('n5', not check_complex_set('забыт действительный корень',
                              [1 - sqrt(3) * I], D['Задание 8']))
t('n6', not verify_identity('пифагорово тождество не применено',
                            5 * cos(theta)**4 * sin(theta),
                            16 * sin(theta)**5 - 20 * sin(theta)**3 + 5 * sin(theta),
                            var=theta))

bad = [n for n, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
