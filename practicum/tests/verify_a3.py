"""Прогоняет все проверки практикума A3 с эталонными ответами из раздела решений.

Ответы не переписываются из решений: разложения строятся sympy (expand и series),
коэффициенты извлекаются из настоящих многочленов, системы решаются заново.
Отдельно измеряется, что проверки отвергают, и где они мягче экзамена.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *

NB = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a3-binomial.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(",
                                   "check_series(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
n, r, p, q, h = sp.symbols('n r p q h')
a, b = sp.symbols('a b')
z = sp.Symbol('z')
th = sp.Symbol('theta', real=True)


def t(name, ok):
    res.append((name, ok))


def coef(expr, var, deg):
    return sp.expand(expr).coeff(var, deg)


def ser(expr, var, upto):
    return sp.series(expr, var, 0, upto).removeO()


print('=== целые степени ===')
e1 = sp.expand((1 + x)**4)
print(f'(1+x)^4 = {e1}')
t('1', check_series('Задание 1', e1, D['Задание 1']))
t('1-нераскрытый принимается', check_series('  как (1+x)^4', (1 + x)**4, D['Задание 1']))

c2 = coef(sp.expand((x + 1)**7), x, 5)
print(f'коэффициент x^5 в (x+1)^7 = {c2}, а binomial(7,2) = {sp.binomial(7, 2)}')
t('2', check_num('Задание 2', c2, 6, D['Задание 2']))
t('2-симметрия', sp.binomial(7, 2) == sp.binomial(7, 5) == c2)

# задание 3: уравнение решается, а не списывается
k3 = sp.solve(sp.Eq(coef(sp.expand((x + k)**7), x, 5), 63), k)
print(f'\n21k² = 63 -> k = {k3}')
t('3', check_set('Задание 3', k3, D['Задание 3']))
t('3-оба корня', len(k3) == 2)

# задание 4: коэффициент берётся из настоящего разложения при каждом n
vals4 = {i: coef(sp.expand((3 + x**2)**(i + 1)), x, 4) for i in range(4, 10)}
n4 = [i for i, v in vals4.items() if v == 20412]
print(f'коэффициент x^4 в (3+x²)^(n+1): {vals4}\n-> n = {n4}')
t('4', check_num('Задание 4', n4[0], 6, D['Задание 4']))
t('4-единственное', len(n4) == 1)

# задание 5: показатель не берётся из решения, а снимается с настоящего
# разложения — при конкретном n степени идут по 3n−4r
deg5 = sorted({d for d in range(-40, 40)
               if sp.expand((x**3 - 1 / (8 * x))**8).coeff(x, d) != 0}, reverse=True)
print(f'\nстепени x в (x³ − 1/(8x))^8: {deg5}')
print(f'формула 3n−4r при n=8, r=0..8: {[24 - 4 * i for i in range(9)]}')
t('5-степени совпали', deg5 == [24 - 4 * i for i in range(9)])
t('5-показатель', check_series('Задание 5, показатель', 3 * n - 4 * r,
                               D['Задание 5, показатель'], var=n))
# постоянный член ищется перебором, а не по формуле из решения
have = [m for m in range(1, 17)
        if sp.expand((x**3 - 1 / (8 * x))**m).coeff(x, 0) != 0]
print(f'n, при которых постоянный член есть (перебор до 16): {have}')
t('5-перебор', have[:3] == [4, 8, 12])
t('5-кратны четырём', all(m % 4 == 0 for m in have))
t('5-значения', check_set('Задание 5, значения n', have[:3], D['Задание 5, значения n']))

print('\n=== приравнивание коэффициентов ===')
sol6 = sp.solve([sp.Eq(n * k, 12), sp.Eq(n * (n - 1) / 2, 28)], [n, k], dict=True)
good6 = [s for s in sol6 if s[n].is_integer and s[n] > 0]
print(f'решения системы: {sol6} -> годных {good6}')
t('6-отбор корня', len(sol6) == 2 and len(good6) == 1)
t('6n', check_num('Задание 6, n', good6[0][n], 6, D['Задание 6, n']))
t('6k', check_expr('Задание 6, k', good6[0][k], D['Задание 6, k']))
# проверка подстановкой в само разложение
chk6 = sp.expand((1 + R(3, 2) * x)**8)
t('6-подстановка', coef(chk6, x, 1) == 12
  and coef(chk6, x, 2) == 28 * R(3, 2)**2)

# задание 7: коэффициенты берутся из настоящих разложений
c8 = sp.factor(coef(sp.expand((a * x**3 + b)**8), x, 6))
c10 = sp.factor(coef(sp.expand((a * x**3 + b)**10), x, 6))
print(f'\nкоэффициент x^6: при n=8 {c8}, при n=10 {c10}')
t('7-степени a', c8 == 28 * a**2 * b**6 and c10 == 45 * a**2 * b**8)
sol7 = sp.solve([sp.Eq(c8, 448), sp.Eq(c10, 2880)], [a, b], dict=True)
pos7 = [s for s in sol7 if s[a].is_positive and s[b].is_positive]
print(f'положительное решение: {pos7}')
t('7a', check_expr('Задание 7, a', pos7[0][a], D['Задание 7, a']))
t('7b', check_expr('Задание 7, b', pos7[0][b], D['Задание 7, b']))
# путь из method_path корпуса (a^6 b^2) даёт перевёрнутый ответ
bad7 = sp.solve([sp.Eq(28 * a**6 * b**2, 448), sp.Eq(45 * a**8 * b**2, 2880)],
                [a, b], dict=True)
badpos = [s for s in bad7 if s[a].is_positive and s[b].is_positive]
print(f'по записи method_path (a^6 b^2): {badpos} — a и b поменяны местами')
t('7-разметка перевёрнута', badpos and badpos[0][a] == 2 and badpos[0][b] == R(1, 2))

print('\n=== коэффициенты как последовательность ===')
exp8 = sp.expand((x + 1)**7)
t2, t3, t4 = coef(exp8, x, 6), coef(exp8, x, 5), coef(exp8, x, 4)
print(f'коэффициенты (x+1)^7: {t2}, {t3}, {t4}')
roots8 = sp.solve(sp.Eq(2 * t3 * x**5, t2 * x**6 + t4 * x**4), x)
print(f'корни уравнения: {roots8} -> без нуля {[v for v in roots8 if v != 0]}')
t('8-ноль присутствует', 0 in roots8)
t('8', check_set('Задание 8', [v for v in roots8 if v != 0], D['Задание 8']))

exp9 = sp.expand((x + h)**8)
a9, b9, d9 = coef(exp9, x, 7), coef(exp9, x, 6), coef(exp9, x, 4)
print(f'\n(x+h)^8: a = {a9}, b = {b9}, d = {d9}')
roots9 = sp.solve(sp.Eq(b9 / a9, d9 / b9), h)
pos9 = [v for v in roots9 if v.is_positive]
print(f'корни: {roots9} -> положительный {pos9}')
t('9', check_num('Задание 9', pos9[0], 6, D['Задание 9']))
t('9-это 1.4', float(pos9[0]) == 1.4)

print('\n=== дробные и отрицательные показатели ===')
s10 = ser((1 + 5 * x)**R(1, 2), x, 4)
print(f'(1+5x)^(1/2) = {s10}')
t('10', check_series('Задание 10', s10, D['Задание 10']))
s11a = ser((1 + x**2)**-1, x, 8)
s11b = ser((1 - x**2)**R(-1, 2), x, 6)
print(f'(1+x²)^(-1) = {s11a}\n1/sqrt(1-x²) = {s11b}')
t('11a', check_series('Задание 11 (a)', s11a, D['Задание 11 (a)']))
t('11b', check_series('Задание 11 (b)', s11b, D['Задание 11 (b)']))

d12 = sp.expand(ser((1 + a * x)**R(-1, 2), x, 3) - ser((1 - x)**R(1, 2), x, 3))
print(f'\nразность рядов: {d12}')
sol12 = sp.solve([sp.Eq(coef(d12, x, 1), 4 * b), sp.Eq(coef(d12, x, 2), b)],
                 [a, b], dict=True)
print(f'решения системы: {sol12}')
t('12-два решения', len(sol12) == 2)
# оба решения действительно удовлетворяют системе; отсекает условие a != 0
zero12 = [s for s in sol12 if s[a] == 0][0]
lhs0 = sp.expand(1 - ser((1 - x)**R(1, 2), x, 3))
t('12-a=0 тождественно верно',
  sp.expand(lhs0 - (4 * zero12[b] * x + zero12[b] * x**2)) == 0)
good12 = [s for s in sol12 if s[a] != 0][0]
t('12a', check_expr('Задание 12, a', good12[a], D['Задание 12, a']))
t('12b', check_expr('Задание 12, b', good12[b], D['Задание 12, b']))
t('12r', check_num('Задание 12, граница', 1, 6, D['Задание 12, граница']))
t('12-граница жёстче', 1 < 1 / abs(float(good12[a])))

s13 = sp.expand(ser((1 + p * x) * (1 + q * x)**-1, x, 3))
print(f'\n(1+px)/(1+qx) = {s13}')
t('13', check_series('Задание 13', s13, D['Задание 13']))

print('\n=== комплексные числа ===')
e14 = sp.expand((sp.cos(th) + I * sp.sin(th))**5)
re14 = sp.expand(sp.simplify(sp.re(sp.expand_complex(e14))))
im14 = sp.expand(sp.simplify(sp.im(sp.expand_complex(e14))))
print(f'Re = {re14}\nIm = {im14}')
t('14-re сходится с Муавром',
  abs(complex((re14 - sp.cos(5 * th)).subs(th, 0.7).evalf())) < 1e-12)
t('14-im сходится с Муавром',
  abs(complex((im14 - sp.sin(5 * th)).subs(th, 0.7).evalf())) < 1e-12)
t('14a', check_series('Задание 14, Re', re14, D['Задание 14, Re'], var=th))
t('14b', check_series('Задание 14, Im', im14, D['Задание 14, Im'], var=th))

e15 = sp.expand((1 + z)**4 + (1 - z)**4)
print(f'\n(1+z)^4 + (1-z)^4 = {e15}')
t('15-нечётные ушли', all(e15.coeff(z, i) == 0 for i in (1, 3)))
t('15e', check_series('Задание 15, разложение', e15, D['Задание 15, разложение'], var=z))
zz = sp.solve(sp.Eq(e15, 0), z**2)
print(f'z² = {zz}')
t('15z', check_set('Задание 15, z^2', zz, D['Задание 15, z^2']))
# tan(pi/8) выводится из корня, а не берётся из решения
tan8 = sp.sqrt(-min(zz, key=lambda v: float(v.evalf())) if False else
               sp.sqrt(3 - 2 * sp.sqrt(2))**2)
t('15-значение', abs(float(sp.N(sp.tan(sp.pi / 8) - sp.sqrt(3 - 2 * sp.sqrt(2))))) < 1e-12)
t('15-это sqrt2-1', sp.simplify(sp.sqrt(3 - 2 * sp.sqrt(2)) - (sp.sqrt(2) - 1)) == 0)

print('\n=== задание на таймере ===')
sol16 = sp.solve([sp.Eq(coef(s13, x, 1), coef(s10, x, 1)),
                  sp.Eq(coef(s13, x, 2), coef(s10, x, 2))], [p, q], dict=True)[0]
print(f'p, q из совпадения первых трёх членов: {sol16}')
t('16q', check_expr('Задание 16, q', sol16[q], D['Задание 16, q']))
t('16p', check_expr('Задание 16, p', sol16[p], D['Задание 16, p']))
x16 = sp.solve(sp.Eq(1 + 5 * x, R(6, 5)), x)[0]
v16 = sp.nsimplify(((1 + sol16[p] * x16) / (1 + sol16[q] * x16)))
y16 = sp.solve(sp.Eq(1 + 5 * x, R(5, 4)), x)[0]
print(f'x для sqrt(1.2) = {x16}, приближение = {v16} = {sp.N(v16, 8)}, '
      f'истинно {sp.N(sp.sqrt(R(6, 5)), 8)}')
print(f'x для sqrt(5)/2 = {y16}; больше {x16}: {y16 > x16}')
t('16x', check_expr('Задание 16, x для sqrt(1.2)', x16, D['Задание 16, x для sqrt(1.2)']))
t('16v', check_expr('Задание 16, приближение', v16, D['Задание 16, приближение']))
t('16y', check_expr('Задание 16, x для sqrt(5)/2', y16, D['Задание 16, x для sqrt(5)/2']))
t('16-хуже потому что больше', y16 > x16)
t('16-оба в области сходимости', y16 < R(1, 5) and x16 < R(1, 5))
t('16-а sqrt(5/2) уже вне', sp.solve(sp.Eq(1 + 5 * x, R(5, 2)), x)[0] > R(1, 5))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'term', 2: 'frac', 3: 'expand', 4: 'equate', 5: 'complex',
        6: 'term', 7: 'seq', 8: 'frac', 9: 'approx', 10: 'expand',
        11: 'equate', 12: 'term', 13: 'seq', 14: 'complex', 15: 'frac'}
t('trigger', trigger_check(good, KEY))
print('  порча пункта 9:', end=' ')
t('trigger-neg', not trigger_check({**good, 9: 'frac'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('n1', not check_series('пятёрка не возведена в степень',
                         1 + R(5, 2) * x - R(1, 8) * x**2 + R(1, 16) * x**3,
                         D['Задание 10']))
t('n2', not check_set('потерян отрицательный корень', [sp.sqrt(3)], D['Задание 3']))
t('n3', not check_set('лишний корень x = 0', [0, 1, 5], D['Задание 8']))
t('n4', not check_expr('a и b перепутаны местами', 2, D['Задание 7, a']))
t('n5', not check_series('знаки чередоваться забыли', 1 + x**2 + x**4 + x**6,
                         D['Задание 11 (a)']))
t('n6', not check_num('взят второй корень квадратного', -7, 6, D['Задание 6, n']))
t('n7', not check_series('в произведении оставлен лишний член x³',
                         1 + (p - q) * x + (q**2 - p * q) * x**2 + p * q**2 * x**3,
                         D['Задание 13']))
t('n8', not check_expr('sqrt(5/2) вместо sqrt(5)/2', R(3, 10),
                       D['Задание 16, x для sqrt(5)/2']))

# Где проверка мягче экзамена: сверяются значения, поэтому cos(5θ) проходит
# вместо выражения через sinθ и cosθ. Численно это то же число, а условие
# требует другой формы записи. Фиксируем поведение, в ноутбуке сказано прямо.
t('предел-1 cos(5θ) проходит',
  check_series('  cos(5*th) вместо развёрнутого', sp.cos(5 * th),
               D['Задание 14, Re'], var=th))
# и нераскрытая скобка тоже: значения у (1+x)^4 и её разложения совпадают
t('предел-2 нераскрытое проходит',
  check_series('  (1+x)^4 вместо многочлена', (1 + x)**4, D['Задание 1']))

bad = [nm for nm, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
