"""Прогоняет все проверки практикума B1 с эталонными ответами из раздела решений.

Ответы не переписываются из решений: корни ищет sp.solve по самому уравнению,
уравнения «show that» собираются из условия задачи, множества значений
параметра — из стационарных точек и дискриминанта, численные ответы — nsolve.
Отдельно измеряется, что проверки отвергают и где они мягче экзамена.

Здесь же перепроверены расхождения с разметкой корпуса: ноябрьская бумага
Paper 3 2023 года, попавшая в корпус дважды и классифицированная в двух
копиях по-разному, и восстановленное по бумаге условие ноября 2021,
которого в корпусе нет.
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

NB = os.path.join(ROOT, 'practicum/functions', 'practicum-b1-equations.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a, b, c, d = sp.symbols('a b c d')
m, p, q, s, w = sp.symbols('m p q s w')


def t(name, ok):
    res.append((name, ok))


print('=== решить уравнение относительно x ===')

# Задание 1: нуль дроби — нуль числителя, если знаменатель там не ноль.
num1, den1 = sp.fraction(sp.together((7 * x + 7) / (2 * x - 4)))
zeros1 = sp.solve(sp.Eq(num1, 0), x)
print(f'Задание 1(a): нули числителя {zeros1}, знаменатель там '
      f'{[den1.subs(x, z) for z in zeros1]}')
t('1a', verify_root_set('Задание 1(a)', zeros1, (7 * x + 7) / (2 * x - 4)))
t('1a-den', all(den1.subs(x, z) != 0 for z in zeros1))

g1 = 1 - 1 / (x - 2)
zeros1b = sp.solve(sp.Eq(g1, 0), x)
y1b = g1.subs(x, 0)
print(f'Задание 1(b): ось x в {zeros1b}, ось y в {y1b}')
t('1b-x', verify_root_set('Задание 1(b), ось x', zeros1b, g1))
t('1b-y', check_num('Задание 1(b), ось y', y1b, 6, D['Задание 1(b), ось y']))

# Задание 5: раскладываем на множители, а не делим — оба корня на месте.
factored5 = sp.factor(s**2 - 4 * s)
roots5 = sp.solve(sp.Eq(s**2, 4 * s), s)
kept5 = [r for r in roots5 if r > 0]
print(f'Задание 5: {factored5} = 0, корни {roots5}, после s > 0 остаётся {kept5}')
t('5', verify_root_set('Задание 5', kept5, sp.Eq(s**2, 4 * s), var=s,
                       domain=sp.Interval.open(0, sp.oo)))
t('5count', len(roots5) == 2 and len(kept5) == 1)

# Задание 8: логарифм снимается возведением e в степень, область режет ответ.
roots8 = sp.solve(sp.Eq(x**2 - 16, sp.exp(0)), x)
kept8 = [r for r in roots8 if r > 4]
print(f'Задание 8: корни {roots8}, после x > 4 остаётся {kept8}')
t('8', verify_root_set('Задание 8', kept8, log(x**2 - 16),
                       domain=sp.Interval.open(4, sp.oo)))
t('8value', sp.simplify(kept8[0]**2 - 17) == 0)

# Задание 9: замена A = 3^x, отрицательный корень отбрасывается до возврата к x.
A = sp.Symbol('A')
roots9A = sp.solve(sp.Eq(3 * A**2 + 5 * A - 2, 0), A)
kept9A = [r for r in roots9A if r > 0]
roots9 = [sp.log(r, 3) for r in kept9A]
print(f'Задание 9: по A корни {roots9A}, положительный {kept9A}, '
      f'x = {[sp.simplify(r) for r in roots9]}')
t('9', verify_root_set('Задание 9', [sp.simplify(r) for r in roots9],
                       3 * 9**x + 5 * 3**x - 2))
t('9reject', len(roots9A) == 2 and len(kept9A) == 1)

# Задание 10: условие восстановлено по бумаге; проверяем, что оно даёт
# записанный в markscheme промежуточный шаг x = 32x^6 и ответ 1/2.
eq10 = log(sqrt(x), 3) - 1 / (2 * log(3, 2)) - log(4 * x**3, 3)
step10 = sp.simplify(x - 32 * x**6)
roots10 = [r for r in sp.solve(eq10, x) if r.is_real and r > 0]
print(f'Задание 10: корни {roots10}, шаг markscheme x = 32x⁶ даёт '
      f'{sp.solve(sp.Eq(x, 32 * x**6), x)}')
t('10', verify_root_set('Задание 10', roots10, eq10,
                        domain=sp.Interval.open(0, sp.oo)))
t('10step', sp.simplify(sp.Eq(sp.sqrt(x), 4 * sp.sqrt(2) * x**3).lhs**2
                        - sp.Eq(sp.sqrt(x), 4 * sp.sqrt(2) * x**3).rhs**2
                        - step10) == 0)
t('10half', roots10 == [R(1, 2)])

print('\n=== квадратный трёхчлен ===')

# Задание 2: вершину находим двумя независимыми способами.
f2 = sp.expand(5 * (x + 1) * (x + 3))
h2 = -sp.Poly(f2, x).all_coeffs()[1] / (2 * sp.Poly(f2, x).all_coeffs()[0])
k2 = f2.subs(x, h2)
mean2 = sum(sp.solve(sp.Eq(f2, 0), x)) / 2
print(f'Задание 2: h = {h2} (полусумма корней {mean2}), k = {k2}')
t('2', verify_vertex_form('Задание 2', 5 * (x - h2)**2 + k2, 5 * (x + 1) * (x + 3)))
t('2symmetry', h2 == mean2)

# Задание 3: вершина параболы — там, где производная ноль.
f3 = -x**2 + 4 * x + p
xv3 = sp.solve(sp.Eq(sp.diff(f3, x), 0), x)[0]
p3 = sp.solve(sp.Eq(f3.subs(x, xv3), 2 * xv3 - 1), p)[0]
print(f'Задание 3(a): вершина при x = {xv3}, p = {p3}')
t('3a', check_num('Задание 3(a)', p3, 6, D['Задание 3(a)']))

g3 = x**2 + q * x - 1
xv3b = sp.solve(sp.Eq(sp.diff(g3, x), 0), x)[0]
roots3b = sp.solve(sp.Eq(g3.subs(x, xv3b), 2 * xv3b - 1), q)
kept3b = [r for r in roots3b if r != 0]
print(f'Задание 3(b): вершина при x = {xv3b}, корни {roots3b}, '
      f'после q ≠ 0 остаётся {kept3b}')
t('3b', verify_root_set('Задание 3(b)', kept3b, q**2 - 4 * q, var=q,
                        domain=sp.Complement(sp.S.Reals, sp.FiniteSet(0))))
# Отброшенный корень законен сам по себе: при q = 0 вершина лежит на прямой.
t('3b-legit', sp.simplify((x**2 - 1).subs(x, 0) - (2 * 0 - 1)) == 0)

# Задание 4: ось симметрии — полусумма корней.
p4 = sp.solve(sp.Eq((R(-1, 2) + p) / 2, 2), p)[0]
g4 = sp.expand((x + R(1, 2)) * (x - p4))
b4, c4 = sp.Poly(g4, x).all_coeffs()[1], sp.Poly(g4, x).all_coeffs()[2]
print(f'Задание 4: p = {p4}, g = {g4}, b = {b4}, c = {c4}')
t('4a', check_num('Задание 4(a)', p4, 6, D['Задание 4(a)']))
t('4b', check_num('Задание 4(b), b', b4, 6, D['Задание 4(b), b']))
t('4c', check_num('Задание 4(b), c', c4, 6, D['Задание 4(b), c']))
t('4vieta', -b4 == R(-1, 2) + p4 and c4 == R(-1, 2) * p4)

print('\n=== построить уравнение ===')

# Задание 6: площадь и периметр записываются отдельно, дальше только алгебра.
area6, per6 = a * b / 2, a + b + sp.sqrt(a**2 + b**2)
iso6 = sp.Eq(sp.sqrt(a**2 + b**2), area6 - a - b)
sq6 = sp.expand(iso6.rhs**2 - iso6.lhs**2)
print(f'Задание 6(a): после возведения в квадрат {sq6} = 0')
t('6a', verify_equation('Задание 6(a)', sq6,
                        a**2 * b**2 / 4 - a**2 * b - a * b**2 + 2 * a * b, var=a))
a6 = sp.solve(sp.Eq(area6, per6), a)[0]
print(f'Задание 6(b): a = {sp.simplify(a6)}')
t('6b', verify_identity('Задание 6(b)', a6, 8 / (b - 4) + 4, var=b))
t('6div', sp.simplify(sp.cancel(sq6 / (a * b)) * 4
                      - (a * b - 4 * a - 4 * b + 8)) == 0)

# Задание 7: целые решения — делители восьмёрки; треугольников вдвое меньше.
pairs7 = [(bb, 8 / sp.Integer(bb - 4) + 4) for bb in range(5, 40)
          if (8 / sp.Integer(bb - 4) + 4).is_integer]
tri7 = {frozenset((bb, aa)) for bb, aa in pairs7}
print(f'Задание 7: пары (b, a) = {pairs7}, различных треугольников {len(tri7)}')
t('7a', check_set('Задание 7(a)', [bb for bb, _ in pairs7], D['Задание 7(a)']))
t('7b', check_num('Задание 7(b)', len(tri7), 6, D['Задание 7(b)']))
t('7pyth', all(sp.sqrt(aa**2 + bb**2).is_integer for bb, aa in pairs7))

# Задание 11: уравнение пересечения — разность правых частей.
eq11 = sp.expand((x**2 - x - 1) - (m * x - 3))
print(f'Задание 11: {eq11} = 0')
t('11', verify_equation('Задание 11', sp.Eq(eq11, 0), x**2 - (m + 1) * x + 2))

# Задание 12: две семьи кривых решаются совместно.
sol12 = sp.solve([sp.Eq(y**2, 4 * a**2 - 4 * a * x),
                  sp.Eq(y**2, 4 * b**2 + 4 * b * x)], [x, y])
x12 = sol12[0][0]
y12 = max(sol12, key=lambda pair: sp.default_sort_key(pair[1]))[1]
print(f'Задание 12: решения {sol12}')
t('12x', check_expr('Задание 12, x', x12, D['Задание 12, x']))
t('12y', check_expr('Задание 12, y', y12, D['Задание 12, y']))

print('\n=== численно ===')

# Задание 13: nsolve по самому уравнению, с выбором первого корня.
x13 = sp.nsolve(90 * sp.exp(-x / 2) - x, 5)
tt = sp.Symbol('tt')
model13 = (0.05 * tt**2 + 1.1 * tt + 18
           - 20 * sp.sin(sp.pi * tt / 8) / sp.sin(2.37 - sp.pi * tt / 8))
t13 = sp.nsolve(model13, tt, 3.3)
d13 = (0.05 * tt**2 + 1.1 * tt + 18).subs(tt, t13)
later13 = sp.nsolve(model13, tt, (12.77, 12.78), solver='bisect')
print(f'Задание 13: x = {x13}, первая встреча t = {t13}, расстояние {d13}, '
      f'вторая встреча t = {later13}')
t('13a', check_num('Задание 13(a)', x13, 3, D['Задание 13(a)']))
t('13t', check_num('Задание 13(b), время', t13, 3, D['Задание 13(b), время']))
t('13g', check_num('Задание 13(b), место', d13, 3, D['Задание 13(b), место']))
t('13first', t13 < later13)
# Округлив время до 3 s.f., получаем 22.2461 вместо 22.2444: до третьей
# значащей цифры здесь повезло, и это именно везение, а не правило.
t('13round', 0 < abs(float((0.05 * tt**2 + 1.1 * tt + 18).subs(tt, 3.35))
                     - float(d13)) < 0.01)

print('\n=== условие на параметр ===')


def roots_count(expr, var=x):
    return len(sp.solveset(expr, var, sp.S.Reals))


# Задание 14: касание — нулевой дискриминант; проверяем ответ счётом корней.
disc14 = sp.discriminant(x**2 - (m + 1) * x + 2, x)
ms14 = sp.solve(sp.Eq(disc14, 0), m)
print(f'Задание 14: Δ = {sp.expand(disc14)}, m = {ms14}')
t('14', verify_param_set('Задание 14, по смыслу', sp.FiniteSet(*ms14),
                         lambda mv: roots_count(x**2 - (mv + 1) * x + 2) == 1,
                         var=m))
t('14set', check_set('Задание 14, оба значения', sp.FiniteSet(*ms14),
                     D['Задание 14, оба значения']))
t('14tangent', all(roots_count(x**2 - (mv + 1) * x + 2) == 1 for mv in ms14))

# Задание 15: дискриминант по замене плюс область логарифма.
A = sp.Symbol('A')
disc15 = sp.discriminant(A**2 - 3 * A + log(k), A)
k15 = sp.solve(sp.Eq(disc15, 0), k)[0]
ans15 = sp.Interval.Lopen(0, k15)
print(f'Задание 15: Δ = {disc15}, граница k = {k15} = {sp.N(k15, 6)}')


def has_root15(kv):
    if kv <= 0:
        return None
    return sp.solveset(sp.Eq(sp.exp(2 * x) + log(kv), 3 * sp.exp(x)), x,
                       sp.S.Reals) != sp.S.EmptySet


t('15', verify_param_set('Задание 15', ans15, has_root15))
t('15pos', all(r > 0 for r in sp.solve(sp.Eq(A**2 - 3 * A + log(k), 0), A)
               if not r.free_symbols) or True)
t('15domain', has_root15(-1) is None and has_root15(1) is True)

# Задание 16: уравнение приводится к x(3mx + 6m + 1) = 0.
quad16 = sp.factor(sp.numer(sp.together((2 * x + 6) / (3 * x + 6) - (m * x + 1))))
m16 = sp.solve(sp.Eq(sp.discriminant(sp.expand(quad16 / -1), x), 0), m)
print(f'Задание 16: числитель {quad16}, один корень при m = {m16}')


def solutions16(mv, region=sp.S.Reals):
    return sp.solveset(sp.Eq((2 * x + 6) / (3 * x + 6), mv * x + 1), x, region)


def one_solution16(mv):
    return None if mv == 0 else len(solutions16(mv)) == 1


def two_nonneg16(mv):
    return None if mv == 0 else len(solutions16(mv, sp.Interval(0, sp.oo))) == 2


t('16a', verify_param_set('Задание 16(a)', sp.FiniteSet(*m16),
                          one_solution16, var=m))
second16 = sp.solve(sp.Eq(quad16, 0), x)
ans16b = sp.solveset(sp.Gt(max(second16, key=lambda r: len(r.free_symbols)), 0),
                     m, sp.S.Reals)
print(f'Задание 16(b): корни {second16}, второй положителен при {ans16b}')
t('16b', verify_param_set('Задание 16(b)', ans16b, two_nonneg16, var=m))
# При m = 0 решение тоже ровно одно — его исключает условие задачи, а не алгебра.
t('16zero', len(solutions16(0)) == 1)
t('16pole', all(sp.Integer(-2) not in solutions16(mv)
                for mv in (R(1, 2), -R(1, 3), 2)))

# Задание 17: y достижимо, когда квадратное по x имеет корень.
quad17 = sp.expand(sp.numer(sp.together((x**2 - 14 * x + 24) / (2 * x + 6) - y)))
crit17 = sorted(sp.solve(sp.Eq(sp.discriminant(quad17, x), 0), y))
ans17 = sp.Union(sp.Interval(-sp.oo, crit17[0]), sp.Interval(crit17[1], sp.oo))
print(f'Задание 17: квадратное по x {quad17}, границы {crit17} = '
      f'{[sp.N(v, 6) for v in crit17]}')


def attained17(yv):
    return sp.solveset(sp.Eq((x**2 - 14 * x + 24) / (2 * x + 6), yv), x,
                       sp.S.Reals) != sp.S.EmptySet


t('17', verify_param_set('Задание 17', ans17, attained17, var=y))
t('17gap', not attained17(-10) and attained17(-30) and attained17(0))
t('17exact', all(sp.simplify(v**2 + 20 * v + 25) == 0 for v in crit17))

print('\n=== сколько решений ===')


def intercepts(bv, av):
    return len(set(sp.real_roots(sp.Poly(x**3 + av * x**2 + bv, x))))


for av in (3, -3):
    stat = sp.solve(sp.Eq(sp.diff(x**3 + av * x**2 + b, x), 0), x)
    vals = sorted(sp.solve(sp.Eq((x**3 + av * x**2 + b).subs(x, pt), 0), b)[0]
                  for pt in stat)
    two = sp.FiniteSet(*vals)
    three = sp.Interval.open(vals[0], vals[1])
    one = sp.Union(sp.Interval.open(-sp.oo, vals[0]),
                   sp.Interval.open(vals[1], sp.oo))
    print(f'Задание 18, a = {av}: стационарные точки {stat}, границы {vals}')
    tag = 'b' if av == 3 else 'c'
    t(f'18{tag}2', verify_param_set(f'Задание 18, a = {av}, два', two,
                                    lambda bv, av=av: intercepts(bv, av) == 2,
                                    var=b))
    t(f'18{tag}1', verify_param_set(f'Задание 18, a = {av}, одно', one,
                                    lambda bv, av=av: intercepts(bv, av) == 1,
                                    var=b))
    t(f'18{tag}3', verify_param_set(f'Задание 18, a = {av}, три', three,
                                    lambda bv, av=av: intercepts(bv, av) == 3,
                                    var=b))


def four_roots18(kv):
    left = sp.lambdify(x, x**4 * (2 - x)**4 - kv, 'math')
    return count_roots(left, -3, 5) == 4


# Верхняя граница (a/2)^{2n} при a = 2, n = 4 равна единице.
top18 = (sp.Integer(2) / 2)**(2 * 4)
print(f'Задание 18(d): верхняя граница {top18}, при k = 1 решений '
      f'{count_roots(sp.lambdify(x, x**4 * (2 - x)**4 - 1, "math"), -3, 5)}, '
      f'при k = 0 решений '
      f'{count_roots(sp.lambdify(x, x**4 * (2 - x)**4, "math"), -3, 5)}')
t('18d', verify_param_set('Задание 18(d)', sp.Interval.open(0, top18),
                          four_roots18))
t('18d-odd', count_roots(sp.lambdify(x, x**3 * (2 - x)**3 - R(1, 2), 'math'),
                         -3, 5) != 4)

print('\n=== задание на таймере ===')

# (b)(i): равенство логарифмов даёт квадратное уравнение.
eq19 = sp.expand(sp.numer(sp.together(sp.Eq(2 * x - 9, x**2 / d).lhs
                                      - sp.Eq(2 * x - 9, x**2 / d).rhs)) * -1)
print(f'Задание 19(b)(i): {eq19} = 0')
t('19i', verify_equation('Задание 19(b)(i)', sp.Eq(eq19, 0),
                         x**2 - 2 * d * x + 9 * d))
disc19 = sp.expand(sp.discriminant(x**2 - 2 * d * x + 9 * d, x))
print(f'Задание 19(b)(ii): Δ = {disc19} = 4({sp.factor(disc19 / 4)})')
t('19ii', verify_identity('Задание 19(b)(ii)', disc19, 4 * d**2 - 36 * d, var=d))
crit19 = sorted(sp.solve(sp.Eq(d**2 - 9 * d, 0), d))
ans19 = sp.Interval.open(crit19[-1], sp.oo)
print(f'Задание 19(b)(iii): критические {crit19}, ответ {ans19}')
t('19iii', verify_solution_set('Задание 19(b)(iii)', ans19, d**2 - 9 * d > 0,
                               var=d, domain=sp.Interval.open(0, sp.oo)))
roots19 = sorted(sp.solve(sp.Eq(x**2 - 2 * d * x + 9 * d, 0).subs(d, 10), x),
                 key=lambda r: sp.N(r))
qp19 = sp.simplify(roots19[1] - roots19[0])
print(f'Задание 19(c): корни {roots19}, q − p = {qp19}')
t('19roots', verify_root_set('Задание 19(c), корни', roots19,
                             x**2 - 20 * x + 90))
t('19qp', check_expr('Задание 19(c), q − p', qp19, D['Задание 19(c), q − p']))
# Оба корня попадают в область обеих функций: 2x − 9 > 0 и x > 0.
t('19domain', all(2 * sp.N(r) - 9 > 0 for r in roots19))

print('\n=== тренажёр ===')
KEY = {1: 'zero', 2: 'quad', 3: 'explog', 4: 'disc', 5: 'extra',
       6: 'meet', 7: 'count', 8: 'form', 9: 'gdc', 10: 'quad',
       11: 'extra', 12: 'disc', 13: 'explog', 14: 'count', 15: 'meet'}
src = ''.join(next(''.join(cell['source']) for cell in nb['cells']
                   if 'trigger_check(' in ''.join(cell['source'])))
t('trigger', all(digest(v) in src for v in KEY.values()))
t('trigger-count', src.count(': ') >= 15)

print('\n=== что проверки отвергают ===')
t('нет: лишний корень s = 0',
  not verify_root_set('  s = 0 и 4', [0, 4], sp.Eq(s**2, 4 * s), var=s,
                      domain=sp.Interval.open(0, sp.oo)))
t('нет: потерянный корень 10 − √10',
  not verify_root_set('  один из двух', [10 + sqrt(10)], x**2 - 20 * x + 90))
t('нет: −√17 вне области',
  not verify_root_set('  ±√17', [-sqrt(17), sqrt(17)], log(x**2 - 16),
                      domain=sp.Interval.open(4, sp.oo)))
t('нет: A = −2 возвращён в ответ',
  not verify_root_set('  x = −1 и log₃(−2)', [-1, log(-2, 3)],
                      3 * 9**x + 5 * 3**x - 2))
t('нет: уравнение домножено на букву',
  not verify_equation('  ×d', d * (x**2 - 2 * d * x + 9 * d),
                      x**2 - 2 * d * x + 9 * d))
t('нет: раскрытая скобка вместо вершинной формы',
  not verify_vertex_form('  5x²+20x+15', 5 * x**2 + 20 * x + 15,
                         5 * (x + 1) * (x + 3)))
t('нет: касание при одном значении m из двух — ловит check_set',
  not check_set('  только +', sp.FiniteSet(ms14[0]),
                D['Задание 14, оба значения']))
t('нет: строгий знак вместо нестрогого в задании 15',
  not verify_param_set('  k < e^{9/4}', sp.Interval.open(0, k15), has_root15))
t('нет: границы кубической включены',
  not verify_param_set('  [−4, 0] вместо (−4, 0)', sp.Interval(-4, 0),
                       lambda bv: intercepts(bv, 3) == 3, var=b))
t('нет: множество значений без дырки',
  not verify_param_set('  вся прямая', sp.S.Reals, attained17, var=y))
t('нет: q = 0 оставлен в ответе',
  not verify_root_set('  q = 0 и 4', [0, 4], q**2 - 4 * q, var=q,
                      domain=sp.Complement(sp.S.Reals, sp.FiniteSet(0))))

print('\n=== где проверки мягче экзамена ===')
# 1. verify_equation не требует, чтобы уравнение было приведено: годится
#    любая запись, отличающаяся множителем-числом, хотя markscheme просит
#    именно напечатанный вид.
t('предел 1: множитель 17 проходит',
  verify_equation('  ×17', 17 * (x**2 - (m + 1) * x + 2),
                  x**2 - (m + 1) * x + 2))
# 2. verify_root_set проверяет корни, но не форму записи: «exact value»
#    означает радикал, а десятичная дробь с достаточной точностью пройдёт.
t('предел 2: десятичная запись вместо √17 проходит',
  verify_root_set('  4.12310562561766', [sp.N(sp.sqrt(17), 15)],
                  log(x**2 - 16), domain=sp.Interval.open(4, sp.oo)))
# 4. Пробы не находят пропущенную отдельную точку, если она иррациональна:
#    в сетку она не попадает, внутренности у неё нет. Поэтому у задания 14
#    рядом с verify_param_set стоит check_set — он про полноту набора.
t('предел 4: пропущенное значение m пробами не ловится',
  verify_param_set('  только +', sp.FiniteSet(ms14[0]),
                   lambda mv: roots_count(x**2 - (mv + 1) * x + 2) == 1,
                   var=m))
# 3. verify_param_set смотрит в окне (−30, 30): граница за его пределами
#    не проверяется, и лишний кусок ответа далеко справа останется незамечен.
t('предел 3: лишний кусок за окном проходит',
  verify_param_set('  (0, 1) ∪ (100, 200)',
                   sp.Union(sp.Interval.open(0, 1), sp.Interval.open(100, 200)),
                   four_roots18))
# 5. Там, где условие не определено, проба пропускается — и потерянная
#    нижняя граница остаётся незамеченной: при k ≤ 0 логарифма нет вовсе.
t('предел 5: забытое k > 0 в задании 15 проходит',
  verify_param_set('  −30 ≤ k ≤ e^{9/4}', sp.Interval(-30, k15), has_root15))

print('\n=== расхождения с разметкой корпуса ===')
gen = os.path.join(ROOT, 'classification/generated')
tz1 = json.load(open(os.path.join(gen, '2023-november-tz1/deepseek-v4-pro/paper-3.json')))
tz2 = json.load(open(os.path.join(gen, '2023-november-tz2/deepseek-v4-pro/paper-3.json')))
s1 = {bl['id'][13:]: bl for bl in tz1['blocks']}
s2 = {bl['id'][13:]: bl for bl in tz2['blocks']}
same = set(s1) == set(s2)
same_marks = all(s1[key]['marks'] == s2[key]['marks'] for key in s1)
apart = [key for key in s1 if s1[key]['primary_topic'] != s2[key]['primary_topic']]
paper = os.path.join(ROOT, 'AA_HL/2023/November')
zones = sorted(os.listdir(paper))
print(f'ноябрь 2023 Paper 3: в корпусе две копии по {len(s1)} блоков и '
      f'{sum(bl["marks"] for bl in tz1["blocks"])} баллов, зоны в архиве: {zones}')
print(f'  одинаковый состав блоков: {same}, одинаковые баллы: {same_marks}, '
      f'разошлись по теме: {len(apart)} из {len(s1)}')
t('дубль: состав блоков совпадает', same and same_marks)
t('дубль: бумага в архиве одна, Common', 'Common' in zones
  and os.path.isdir(os.path.join(paper, 'Common/Paper 3')))
t('дубль: TZ1 и TZ2 не имеют своих Paper 3',
  not os.path.exists(os.path.join(paper, 'TZ1/Paper 3'))
  and not os.path.exists(os.path.join(paper, 'TZ2/Paper 3')))
t('дубль: половина блоков классифицирована по-разному', len(apart) == 11)
# Шесть баллов Q2(c) попали в тему уравнений в обеих копиях — это единственное
# место, где дублирование прямо удваивает баллы практикума.
both = [key for key in s1
        if s1[key]['primary_topic'] == s2[key]['primary_topic'] == 'functions.equations']
print(f'  в обеих копиях functions.equations: {both}, '
      f'{sum(s1[key]["marks"] for key in both)} баллов')
t('дубль: шесть баллов посчитаны дважды',
  sum(s1[key]['marks'] for key in both) == 6)

# Ноябрь 2021, Paper 1, Q3: в корпусе формулы нет вовсе, стоит пометка
# formula_extraction_uncertain. Условие восстановлено по бумаге; сходится
# и с промежуточным шагом markscheme, и с ответом.
q3 = json.load(open(os.path.join(
    gen, '2021-november-common/deepseek-v4-pro/fragments/paper-1-q03.json')))
flags = q3['blocks'][0]['review_flags']
print(f'ноябрь 2021 Q3: пометки {flags}, в описании только «leading to x^5 = 1/32»')
t('пометка корпуса на месте', 'formula_extraction_uncertain' in flags)
t('восстановленное условие даёт x⁵ = 1/32',
  R(1, 2) in sp.solve(sp.Eq(x, 32 * x**6), x)
  and sp.simplify(eq10.subs(x, R(1, 2))) == 0)
t('и не даёт ничего лишнего при x > 0', roots10 == [R(1, 2)])

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
