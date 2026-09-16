"""Независимая проверка каждого ответа практикума C6.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **не решать так, как решает ноутбук**.
Проверки ноутбука берут нормаль векторным произведением, общую часть
плоскостей находят linsolve, основание перпендикуляра — подстановкой прямой
по нормали, отражение — удвоенным шагом до основания.

Тест идёт другими путями. Плоскость через три точки — определителем
3×3 с x, y, z в первой строке, без векторного произведения. Нормаль из
двух направлений — нуль-пространством матрицы из них. Системы — приведением
расширенной матрицы к ступенчатому виду (rref), и случай «прямая» или
«ничего» читается по рангу. Основание перпендикуляра и ближайшая точка —
минимумом квадрата расстояния: производные по двум свободным координатам
плоскости. Отражение — точка, равноудалённая от трёх точек плоскости, кроме
самой исходной. Отражённая прямая — через отражения двух её точек.

Второй якорь — числа схем оценивания: 2x − 3y − z = 6, (−6, 3, −4),
(1.95, −0.476, 1.10), b = 4/3 и d = 19, (29, −73.5, −49.5), √94/2,
6.71, (−3, 0, 8), (3/2, −2, −3/2), (0, −0.8, 1.6).

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_c6.py
"""
import contextlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_c6 as gen

res = []
Mx = sp.Matrix
X, Y, Z = sp.symbols('x y z')


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    """Эталон из генератора — в пространстве имён ноутбука."""
    import kit
    names = dict(vars(kit))
    names['s'] = sp.Symbol('s')
    return eval(gen.ANSWERS[name], names)


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр (схема обрезает)."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def coefficients(equation):
    """(a, b, c, d) уравнения ax + by + cz = d."""
    expr = sp.expand(equation.lhs - equation.rhs)
    return Mx([expr.coeff(X), expr.coeff(Y), expr.coeff(Z), -expr.subs({X: 0, Y: 0, Z: 0})])


def same_plane(one, two):
    """Уравнения одной плоскости: четвёрки коэффициентов кратны (ранг 1)."""
    return Mx.hstack(coefficients(one), coefficients(two)).rank() == 1


def through_three(P, Q, R):
    """Плоскость через три точки — определитель с x, y, z в первой строке."""
    rows = Mx([[X - P[0], Y - P[1], Z - P[2]],
               [Q[0] - P[0], Q[1] - P[1], Q[2] - P[2]],
               [R[0] - P[0], R[1] - P[1], R[2] - P[2]]])
    return sp.Eq(sp.expand(rows.det()), 0)


def normal_of(*directions):
    """Нормаль — базис нуль-пространства матрицы из направлений."""
    space = Mx([list(d) for d in directions]).nullspace()
    assert len(space) == 1
    return space[0]


def with_point(normal, point):
    return sp.Eq(sp.expand(Mx(normal).dot(Mx([X, Y, Z]))), Mx(normal).dot(Mx(point)))


def solve_rref(equations):
    """Ступенчатый вид расширенной матрицы: ('point', v), ('line', ранг) или ('none',)."""
    rows = [list(coefficients(e)) for e in equations]
    full = Mx(rows)
    reduced, pivots = full.rref()
    if 3 in pivots:
        return ('none',)
    if len(pivots) == 3:
        return ('point', Mx([reduced[i, 3] for i in range(3)]))
    return ('line', len(pivots))


def closest_on_plane(equation, point):
    """Точка плоскости, ближайшая к point: минимум квадрата расстояния."""
    a, b, c, d = coefficients(equation)
    free = [s for s, coef in zip((X, Y, Z), (a, b, c)) if coef != 0][-1]
    others = [s for s in (X, Y, Z) if s != free]
    expressed = sp.solve(equation, free)[0]
    position = Mx([X, Y, Z]).subs(free, expressed)
    gap = position - Mx(point)
    square = sp.expand(gap.dot(gap))
    found = sp.solve([sp.diff(square, s) for s in others], others, dict=True)[0]
    return position.subs(found)


def equidistant_image(equation, point):
    """Отражение — точка, равноудалённая с point от трёх точек плоскости."""
    a, b, c, d = coefficients(equation)
    base = [Mx(p) for p in _three_points(a, b, c, d)]
    image = Mx(sp.symbols('i1:4'))
    conditions = [sp.expand((image - q).dot(image - q) - (Mx(point) - q).dot(Mx(point) - q)) for q in base]
    found = sp.solve(conditions, list(image), dict=True)
    others = [image.subs(f) for f in found if image.subs(f) != Mx(point)]
    assert len(others) == 1
    return others[0]


def _three_points(a, b, c, d):
    """Три неколлинеарные точки плоскости ax + by + cz = d."""
    points = []
    for u, v in ((0, 0), (1, 0), (0, 1)):
        if c != 0:
            points.append((u, v, (d - a * u - b * v) / c))
        elif b != 0:
            points.append((u, (d - a * u - c * v) / b, v))
        else:
            points.append(((d - b * u - c * v) / a, u, v))
    return points


print('=== Задание 1: перпендикулярна и параллельна ===')
k, q, p = sp.symbols('k q p')
n1 = Mx([2, 6, -2])
n2 = Mx([k ** 2 - 6, 2 * k + 3, -6])
k_roots = sp.roots(sp.Poly(sp.expand(n1.dot(n2)), k))
A1 = Mx([2, sp.Rational(1, 2), 1])
q_value = n2.subs(k, -3).dot(A1)
chk('1b: 2k² + 12k + 18 = 2(k + 3)² — корень −3 кратности два, q = −3/2 (markscheme)',
    k_roots == {-3: 2} and q_value == sp.Rational(-3, 2) and A('q1b') == [-3, sp.Rational(-3, 2)])
ratios = sp.solve(sp.Eq(sp.Rational(3, 2) * n1[2], p), p)
chk('1c: (3, 9, p) = 3/2·(2, 6, −2) — p = −3 (markscheme)', ratios == [-3] and A('q1c') == -3)
chk('1a: 2·2 + 6·½ − 2·1 = 5', 2 * 2 + 6 * sp.Rational(1, 2) - 2 == 5)

print('\n=== Задание 2: плоскость через три точки ===')
PA, PB, PC = Mx([3, 0, 0]), Mx([0, -2, 0]), Mx([1, 1, -7])
plane2 = through_three(PA, PB, PC)
chk('2a(ii): определитель — 14x − 21y − 7z = 42, то есть 2x − 3y − z = 6 (markscheme)',
    same_plane(plane2, A('q2a_ii')) and same_plane(plane2, sp.Eq(2 * X - 3 * Y - Z, 6)))
chk('2a(i): AB = (−3, −2, 0), AC = (−2, 1, −7) (markscheme)',
    list(A('q2a_AB')) == list(PB - PA) and list(A('q2a_AC')) == list(PC - PA))

print('\n=== Задание 3: плоскость двух прямых ===')
b3, c3 = Mx([1, -1, 1]), Mx([2, 1, 3])
n3 = normal_of(b3, c3)
plane3 = with_point(n3, [5, 4, 2])
chk('3b(ii): нуль-пространство (1, −1, 1) и (2, 1, 3) — 4x + y − 3z = 18 (markscheme)',
    same_plane(plane3, sp.Eq(4 * X + Y - 3 * Z, 18)) and A('q3b_ii') == -18
    and Mx([1, 8, -2]).dot(Mx([-4, -1, 3])) == -18)
lam, mu = sp.symbols('lambda mu')
vector_form = A('q3b_i')
params = sorted(vector_form.free_symbols, key=str)
on_plane = [sp.expand(coefficients(plane3)[:3, 0].dot(vector_form) - coefficients(plane3)[3])]
chk('3b(i): векторная форма эталона целиком лежит в 4x + y − 3z = 18', on_plane == [0] and len(params) == 2)
chk('3c: q = 18, r = −6 (markscheme)', sp.solve(plane3.subs({X: 0, Z: 0}), Y) == [A('q3c_i')]
    and sp.solve(plane3.subs({X: 0, Y: 0}), Z) == [A('q3c_ii')])
L3 = A('q3e')
step3 = L3.diff(sorted(L3.free_symbols, key=str)[0])
chk('3e: направление L3 кратно нормали, точка (1, 8, −2)',
    Mx.hstack(step3, n3).rank() == 1 and list(L3.subs({s: 0 for s in L3.free_symbols})) == [1, 8, -2])

print('\n=== Задание 4: перпендикулярна двум плоскостям ===')
n4 = normal_of([1, 2, 1], [1, -1, -2])
chk('4: нормаль ⟂ обеим нормалям, через R — x − y + z = 15, то есть −3x + 3y − 3z = −45 (markscheme)',
    same_plane(with_point(n4, [5, -5, 5]), A('q4'))
    and same_plane(A('q4'), sp.Eq(-3 * X + 3 * Y - 3 * Z, -45)))

print('\n=== Задание 5: плоскость параллелограмма и точка F ===')
P5A, P5B, P5D, P5E = Mx([1, -4, 0]), Mx([-3, -6, 2]), Mx([3, 0, 2]), Mx([0, -3, 2])
plane5 = through_three(P5A, P5B, P5D)
chk('5d: определитель через A, B, D — −x + y − z = −5 (markscheme)',
    same_plane(plane5, A('q5d')) and same_plane(plane5, sp.Eq(-X + Y - Z, -5)))
normal5 = coefficients(plane5)[:3, 0]
tt = sp.Symbol('tt')
F5 = sp.solve(sp.Eq(5 * (P5E[0] + tt * normal5[0]) + (P5E[1] + tt * normal5[1]) - 7 * (P5E[2] + tt * normal5[2]), 1), tt)
point5 = P5E + F5[0] * normal5
chk('5f: F = (−6, 3, −4) (markscheme)', list(point5) == [-6, 3, -4] and list(A('q5f')) == [-6, 3, -4])
L5 = A('q5f_L')
chk('5f: эталон L через E и по нормали', Mx.hstack(L5.diff(sorted(L5.free_symbols, key=str)[0]), normal5).rank() == 1
    and list(L5.subs({s: 0 for s in L5.free_symbols})) == [0, -3, 2])

print('\n=== Задание 6: прямая пересечения ===')
system6 = [sp.Eq(2 * X - Y + 2 * Z, 6), sp.Eq(4 * X + 3 * Y - Z, 2), sp.Eq(X, 0)]
kind6 = solve_rref(system6)
chk('6: rref с x = 0 — точка (0, 2, 4)', kind6 == ('point', Mx([0, 2, 4])) and list(A('q6_point')) == [0, 2, 4])
d6 = normal_of([2, -1, 2], [4, 3, -1])
chk('6: нуль-пространство нормалей кратно (1, −2, −2) и эталону',
    Mx.hstack(d6, Mx([1, -2, -2])).rank() == 1 and Mx.hstack(d6, A('q6_direction')).rank() == 1)

print('\n=== Задание 7: три плоскости через начало координат ===')
n7 = normal_of([3, 2, 1], [1, -2, 1])
plane7 = with_point(n7, [0, 0, 0])
chk('7a: 2x − y − 4z = 0 (markscheme 4x − 2y − 8z = 0)', same_plane(plane7, A('q7a'))
    and same_plane(plane7, sp.Eq(4 * X - 2 * Y - 8 * Z, 0)))
kind7 = solve_rref([sp.Eq(3 * X + 2 * Y + Z, 6), sp.Eq(X - 2 * Y + Z, 4), plane7])
chk('7b: rref — (41/21, −10/21, 23/21) = (1.95, −0.476, 1.10) (markscheme)',
    kind7[0] == 'point' and list(kind7[1]) == list(A('q7b'))
    and near(kind7[1][0], '1.95') and near(kind7[1][1], '-0.476') and near(kind7[1][2], '1.10'))

print('\n=== Задание 8: три плоскости по прямой ===')
n8 = normal_of([1, 0, 1], [2, 1, 3])
chk('8a: нормаль из (1, 0, 1) и (2, 1, 3) — x + y − z = −2', same_plane(with_point(n8, [0, 0, 2]), sp.Eq(X + Y - Z, -2))
    and Mx.hstack(n8, A('q8a')).rank() == 1)
bb, dd = sp.symbols('b d', positive=True)
line_cases = []
for b_try in (sp.Rational(4, 3), 1, 2):
    for d_try in (19, 18, 20):
        found = solve_rref([sp.Eq(X + Y - Z, -2), sp.Eq(2 * X + b_try * Y - Z, 3), sp.Eq(X - Y + 2 * Z, d_try)])
        if found[0] == 'line':
            line_cases.append((b_try, d_try))
full8 = Mx([[1, 1, -1, -2], [2, bb, -1, 3], [1, -1, 2, dd]])
minors8 = [full8.extract([0, 1, 2], cols).det() for cols in ([0, 1, 2], [0, 1, 3], [0, 2, 3], [1, 2, 3])]
roots8 = sp.solve(minors8, [bb, dd], dict=True)
chk('8b: ранг расширенной матрицы 2 — b = 4/3, d = 19, и из девяти пар прямую даёт одна (markscheme)',
    roots8 == [{bb: sp.Rational(4, 3), dd: 19}] and line_cases == [(sp.Rational(4, 3), 19)]
    and A('q8b') == [sp.Rational(4, 3), 19])

print('\n=== Задание 9: система с параметрами ===')
tt9 = sp.Symbol('t')
general = A('q9a')
chk('9a: эталон удовлетворяет обоим уравнениям при любом t',
    sp.expand(2 * general[0] + 6 * general[1] - 8 * general[2]) == 13
    and sp.expand(3 * general[0] - general[1] + 3 * general[2]) == 12 and general.free_symbols)
kind9 = solve_rref([sp.Eq(2 * X + 6 * Y - 8 * Z, 13), sp.Eq(3 * X - Y + 3 * Z, 12), sp.Eq(3 * X + 12 * Y - 16 * Z, -3)])
chk('9b: rref — x = 29, y = −73.5, z = −49.5 (markscheme)',
    kind9 == ('point', Mx([29, sp.Rational(-147, 2), sp.Rational(-99, 2)])) and list(A('q9b')) == [29, -73.5, -49.5])
aa, kk = sp.symbols('a k')
det9 = Mx([[2, 6, -8], [3, -1, 3], [aa, 12, -16]]).det()
chk('9c(i): определитель нормалей ноль — a = 4 (markscheme)', sp.solve(det9, aa) == [4] and A('q9c_i') == 4)
ranks = {kv: solve_rref([sp.Eq(2 * X + 6 * Y - 8 * Z, 13), sp.Eq(3 * X - Y + 3 * Z, 12),
                        sp.Eq(4 * X + 12 * Y - 16 * Z, kv)])[0] for kv in (25, 26, 27)}
chk('9c(ii): при a = 4 прямую даёт только k = 26, остальные — ничего (markscheme)',
    ranks == {25: 'none', 26: 'line', 27: 'none'} and A('q9c_ii') == 26)

print('\n=== Задание 10: три плоскости без общей точки ===')
system10 = [sp.Eq(2 * X - Y + Z, 4), sp.Eq(X - 2 * Y + 3 * Z, 5), sp.Eq(-9 * X + 3 * Y - 2 * Z, 32)]
chk('10a: rref — строка 0 = c, общей точки нет', solve_rref(system10) == ('none',) and A('q10a') == 'none')
d10 = normal_of([2, -1, 1], [1, -2, 3])
chk('10b(ii): направление кратно (1, 5, 3), P(1, −2, 0) на обеих (markscheme)',
    Mx.hstack(d10, Mx([1, 5, 3])).rank() == 1 and 2 + 2 == 4 and 1 + 4 == 5
    and Mx.hstack(A('q10b').diff(sorted(A('q10b').free_symbols, key=str)[0]), d10).rank() == 1)
chk('10a value: −9x + 3y − 2z на прямой — −15 при любом λ', sp.expand(Mx([-9, 3, -2]).dot(A('q10b'))) == -15
    and A('q10a_value') == -15)
foot10 = closest_on_plane(system10[2], [1, -2, 0])
gap10 = foot10 - Mx([1, -2, 0])
chk('10c: минимум квадрата расстояния — √94/2 (markscheme)',
    sp.simplify(sp.sqrt(gap10.dot(gap10)) - sp.sqrt(94) / 2) == 0 and sp.simplify(A('q10c') - sp.sqrt(94) / 2) == 0
    and list(foot10) == [sp.Rational(-7, 2), sp.Rational(-1, 2), -1])

print('\n=== Задание 11: основание и отражение ===')
s11, t11 = sp.symbols('s t')
chk('11b: 2(2 + 3s) − (−3 + 6s) = 7 и 2(9 + t) − (11 + 2t) = 7',
    sp.expand(2 * (2 + 3 * s11) - (-3 + 6 * s11)) == 7 == A('q11b_L') and A('q11b_M') == 7)
plane11 = sp.Eq(2 * Y - Z, 7)
B11 = Mx([-3, 12, 2])
foot11 = closest_on_plane(plane11, B11)
chk('11c(i): минимум квадрата расстояния — C = (−3, 6, 5) (markscheme)', list(foot11) == [-3, 6, 5]
    and list(A('q11c_i')) == [-3, 6, 5])
BC = foot11 - B11
chk('11c(ii): |BC| = √45 = 6.71 (markscheme)', sp.sqrt(BC.dot(BC)) == 3 * sp.sqrt(5) and near(sp.N(3 * sp.sqrt(5)), '6.71')
    and A('q11c_ii') == 3 * sp.sqrt(5))
image11 = equidistant_image(plane11, B11)
chk('11d: равноудалённая от трёх точек плоскости — (−3, 0, 8) (markscheme)', list(image11) == [-3, 0, 8]
    and list(A('q11d')) == [-3, 0, 8])

print('\n=== Задание 12: прямая, отражённая в плоскости ===')
d12 = normal_of([2, -3, -1], [3, -1, 2])
chk('12b: нуль-пространство нормалей кратно (1, 1, −1), и эталон тоже',
    Mx.hstack(d12, Mx([1, 1, -1])).rank() == 1 and Mx.hstack(d12, A('q12b')).rank() == 1)
lam12 = sp.solve(sp.Eq(2 * lam - 2 * (-lam), 3), lam)
chk('12c(i): λ = 3/4 (markscheme)', lam12 == [sp.Rational(3, 4)] and A('q12c_i') == sp.Rational(3, 4))
P12 = Mx([0, -2, 0]) + lam12[0] * Mx([1, 1, -1])
chk('12c(ii): P = (3/4, −5/4, −3/4) (markscheme)', list(P12) == list(A('q12c_ii')))
plane12 = sp.Eq(2 * X - 2 * Z, 3)
image12 = equidistant_image(plane12, [0, -2, 0])
chk('12d(i): равноудалённая — (3/2, −2, −3/2) (markscheme)', list(image12) == [sp.Rational(3, 2), -2, sp.Rational(-3, 2)]
    and list(A('q12d_i')) == list(image12))
other = equidistant_image(plane12, [1, -1, -1])
reflected = A('q12d_ii')
free12 = sorted(reflected.free_symbols, key=str)[0]
on_line = [sp.solve(list(reflected - pt), free12, dict=True) for pt in (image12, other, P12)]
chk('12d(ii): отражения B и (1, −1, −1) и точка P — на эталонной прямой', all(on_line))

print('\n=== Таймер ===')
kt = sp.Symbol('k')
plane_t = through_three(Mx([1, 2, 3]), Mx([kt, -2, 1]), Mx([5, 0, 2]))
expr_t = sp.factor(plane_t.lhs)
chk('timer (i): определитель — (k − 9)(y − 2z + 4) = 0, при k ≠ 9 y − 2z = −4 (markscheme)',
    sp.simplify(expr_t / (kt - 9) - (Y - 2 * Z + 4)) == 0 or sp.simplify(expr_t / (9 - kt) - (Y - 2 * Z + 4)) == 0)
chk('timer (i): эталон — та же плоскость', same_plane(sp.Eq(Y - 2 * Z, -4), A('qt_i')))
closest_t = closest_on_plane(sp.Eq(Y - 2 * Z, -4), [0, 0, 0])
chk('timer (ii): минимум x² + y² + z² — (0, −0.8, 1.6) (markscheme)',
    list(closest_t) == [0, sp.Rational(-4, 5), sp.Rational(8, 5)] and list(A('qt_ii')) == list(closest_t))

BREAK_C6 = {
    'q1b': '[-3, Rational(3, 2)]',                    # знак q: A не на P2
    'q1c': '3',                                       # нормали не кратны
    'q2a_AB': 'vec(3, 2, 0)',                         # BA
    'q2a_AC': 'vec(2, -1, 7)',                        # CA
    'q2a_ii': 'Eq(14*x + 21*y - 7*z, 42)',            # знак средней компоненты
    'q3b_i': 'vec(5, 4, 2) + lam*vec(1, -1, 1) + mu*vec(-1, 7, -5)',   # точка L2 вместо направления
    'q3b_ii': '18',                                   # знак
    'q3c_i': '-18',                                   # знак
    'q3c_ii': '6',                                    # знак
    'q3e': 'vec(1, 8, -2) + lam*vec(1, -1, 1)',       # направление L1 вместо нормали
    'q4': 'Eq(x + y + z, 5)',                         # знак средней компоненты
    'q5d': 'Eq(-x + y - z, 5)',                       # знак правой части
    'q5f_L': 'vec(0, -3, 2) + lam*vec(5, 1, -7)',     # нормаль P2
    'q5f': '(6, -9, 8)',                              # λ со знаком минус
    'q6_point': '(0, 2, -4)',                         # знак z
    'q6_direction': 'vec(2, -1, 2)',                  # нормаль Π1
    'q7a': 'Eq(4*x + 2*y - 8*z, 0)',                  # знак средней компоненты
    'q7b': '(Rational(41, 21), Rational(10, 21), Rational(23, 21))',   # знак y
    'q8a': 'vec(2, 1, 5)',                            # радиус-вектор точки
    'q8b': '[Rational(4, 3), 18]',                    # правая часть не та
    'q9a': '(Rational(17, 4), Rational(3, 4), 0)',    # одна точка вместо прямой
    'q9b': '(29, -73.5, 49.5)',                       # знак z
    'q9c_i': '3',                                     # a из (b)
    'q9c_ii': '-26',                                  # знак
    'q10a': '(1, -2, 0)',                             # точка двух плоскостей
    'q10a_value': '15',                               # знак
    'q10b': 'vec(1, -2, 0) + lam*vec(2, -1, 1)',      # нормаль Π1
    'q10c': '47',                                     # не поделено на |n|
    'q11b_L': '2*(2 + 3*s) + (-3 + 6*s)',             # знак второй компоненты нормали
    'q11b_M': '2*(9 + t) + (11 + 2*t)',               # то же
    'q11c_i': '(-3, 18, -1)',                         # λ = +3
    'q11c_ii': '3',                                   # |λ| вместо |λ||n|
    'q11d': '(-3, 6, 5)',                             # основание вместо отражения
    'q12b': 'vec(2, -3, -1)',                         # нормаль Π1
    'q12c_i': 'Rational(3, 2)',                       # 2λ = 3
    'q12c_ii': 'Rational(3, 4)',                      # λ вместо точки
    'q12d_i': '(Rational(3, 4), -2, Rational(-3, 4))',   # основание
    'q12d_ii': 'vec(Rational(3, 2), -2, Rational(-3, 2)) + mu*vec(1, 1, -1)',   # направление не отражено
    'qt_i': 'Eq(y - 2*z, 4)',                         # знак правой части
    'qt_ii': '(0, Rational(4, 5), Rational(-8, 5))',  # знак λ
}

print('\n=== Ноутбук: пустой и с эталонами ===')
with open(gen.NOTEBOOK) as fh:
    notebook = json.load(fh)
notebook_cells = [''.join(c['source']) for c in notebook['cells']
                  if c['cell_type'] == 'code']

PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')
TRAINER_FILL = '    ' + ', '.join(
    f"{i}: {gen.TRIGGER[i]!r}" for i in sorted(gen.TRIGGER)) + ','


def filled(source, override=None):
    out, in_trainer = [], False
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {(override or {}).get(name, gen.ANSWERS[name])}')
            continue
        if line.startswith('answers = {'):
            in_trainer = True
            out.append(line)
            out.append(TRAINER_FILL)
            continue
        if in_trainer:
            if line.startswith('}'):
                in_trainer = False
                out.append(line)
            continue
        out.append(line)
    return '\n'.join(out)


def run(cells):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in cells:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


here_dir = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'geometry'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 30)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = BREAK_C6
snapshots, cell_of = [], {}
space = {'__name__': '__main__'}
with contextlib.redirect_stdout(io.StringIO()):
    for index, source in enumerate(notebook_cells):
        snapshots.append(dict(space))
        for line in source.split('\n'):
            found = PLACEHOLDER.match(line)
            if found:
                cell_of[found.group(1)] = index
        exec(compile(filled(source), '<cell>', 'exec'), space)
chk('у каждого эталона нашлась своя ячейка', set(cell_of) == set(gen.ANSWERS))
chk('у каждого эталона есть типовая ошибка', set(BREAK) == set(gen.ANSWERS))

generic = ('does not meet the conditions', 'something else', 'a condition does not hold',
           'nothing satisfies')
missed, named = [], 0
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}), '<cell>', 'exec'), room)
    rejected = [line for line in buffer.getvalue().split('\n') if line.startswith('❌')]
    if not rejected:
        missed.append(name)
        continue
    if not any(word in rejected[0] for word in generic):
        named += 1
        print(f'   {name}: {rejected[0]}')
    else:
        print(f'   без имени: {name}: {rejected[0]}')
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
print(f'   названы по имени {named} из {len(BREAK)}')
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
