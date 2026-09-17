"""Независимая проверка каждого ответа практикума C7.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **обойтись без векторного произведения
там, где ноутбук на нём стоит**. Проверки ноутбука меряют площадь длиной
произведения, объём — определителем, расстояние до прямой — тем же
произведением, углы — через нормаль.

Тест идёт другими путями. Площадь треугольника — формулой Герона по трём
длинам сторон; площадь параллелограмма — двумя такими треугольниками.
Объём пирамиды — третью произведения площади основания на высоту, а высота
— расстоянием от вершины до плоскости основания, выписанной определителем
с x, y, z в первой строке. Угол между плоскостями — двугранный: в каждой
плоскости берётся вектор, перпендикулярный линии их пересечения, и угол
считается между ними. Угол прямой с плоскостью — между направлением и его
проекцией на плоскость. Ближайшая точка и оба расстояния — минимумом
квадрата длины по параметру, производной. Тождество — прямой подстановкой
случайных векторов.

Само векторное произведение сверяется с Matrix.cross из sympy — оно
написано не здесь и не в kit.

Второй якорь — числа схем оценивания: (0, −36, 0), 6.75, 1.30, m = 12,
12√3, 68.8, 351, 2√6, √3, p = 1 и q = 2, p = 1.4 и q = 0.8, 60°, 1/5,
0.932, 11.1, 029.1°, 10 + 30μ, (1/3, −10/3, 7/3), (4/3, −2/3, 4/3),
3√6 = √54, 3√2 = √18, ±5√66/33.

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_c7.py
"""
import contextlib
import io
import json
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_c7 as gen

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
    names['p'] = sp.Symbol('p', positive=True)      # как в ноутбуке
    names.update({letter: sp.Symbol(letter) for letter in ('q', 'th', 'U', 'V')})
    return eval(gen.ANSWERS[name], names)


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр (схема обрезает)."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def heron(P, Q, R):
    """Площадь треугольника по трём сторонам — без векторного произведения."""
    a, b, c = ((Mx(one) - Mx(two)).norm() for one, two in ((Q, R), (P, R), (P, Q)))
    s = (a + b + c) / 2
    return sp.sqrt(sp.expand(s * (s - a) * (s - b) * (s - c)))


def plane_through(P, Q, R):
    """Плоскость через три точки — определителем с x, y, z в первой строке."""
    rows = Mx([[X - P[0], Y - P[1], Z - P[2]],
               [Q[0] - P[0], Q[1] - P[1], Q[2] - P[2]],
               [R[0] - P[0], R[1] - P[1], R[2] - P[2]]])
    return sp.expand(rows.det())


def height_over(apex, P, Q, R):
    """Высота над плоскостью основания: минимум расстояния до её точек."""
    left = plane_through(P, Q, R)
    coefficients = Mx([left.coeff(X), left.coeff(Y), left.coeff(Z)])
    constant = -left.subs({X: 0, Y: 0, Z: 0})
    return sp.Abs(coefficients.dot(Mx(apex)) - constant) / coefficients.norm()


def least_square(expression, *letters):
    """Наименьшее значение квадрата длины: производные по параметрам в ноль."""
    square = sp.expand(Mx(expression).dot(Mx(expression)))
    found = sp.solve([sp.diff(square, letter) for letter in letters], letters, dict=True)[0]
    return sp.simplify(square.subs(found)), found


def dihedral(one, two):
    """Угол между плоскостями как двугранный: по вектору в каждой, поперёк их общей прямой."""
    left = [sp.expand(eq) for eq in (one, two)]
    normals = [Mx([e.coeff(X), e.coeff(Y), e.coeff(Z)]) for e in left]
    edge = normals[0].cross(normals[1])
    arms = [edge.cross(n) for n in normals]                 # каждый лежит в своей плоскости
    cosine = arms[0].dot(arms[1]) / (arms[0].norm() * arms[1].norm())
    return sp.acos(sp.Abs(sp.simplify(cosine)))


def to_plane(direction, left):
    """Угол прямой с плоскостью: между направлением и его проекцией на плоскость."""
    normal = Mx([left.coeff(X), left.coeff(Y), left.coeff(Z)])
    d = Mx(direction)
    shadow = d - (d.dot(normal) / normal.dot(normal)) * normal
    return sp.acos(sp.Abs(d.dot(shadow)) / (d.norm() * shadow.norm()))


print('=== 1. Векторное произведение на сфере (май 2025 TZ2 Paper 3 Q2(c)) ===')
a, p_vec, n_vec = Mx([6, 0, 0]), Mx([0, 0, 6]), Mx([0, 6, 0])
chk('1(i) a × p совпадает с Matrix.cross', Mx(A('q1_i')) == a.cross(p_vec))
chk('1(i) схема: (0, −36, 0)', list(a.cross(p_vec)) == [0, -36, 0])
chk('1(i) произведение перпендикулярно обоим',
    a.cross(p_vec).dot(a) == 0 and a.cross(p_vec).dot(p_vec) == 0)
right = sp.acos(a.cross(p_vec).dot(a.cross(n_vec))
                / (a.cross(p_vec).norm() * a.cross(n_vec).norm()))
chk('1(ii) угол при вершине A прямой', sp.simplify(right - sp.pi / 2) == 0)
chk('1(ii) схема: 90°', A('q1_ii') == 90)

print('\n=== 2. Произведение с буквой и наименьшая площадь (ноябрь 2023 TZ1 Q8) ===')
p = sp.Symbol('p', positive=True)
A2, B2, C2 = Mx([0, p, 2]), Mx([1, 1, 1]), Mx([p, 0, 4])
product = (B2 - A2).cross(C2 - A2)
chk('2(a) произведение совпадает с Matrix.cross', sp.simplify(Mx(A('q2a')) - product) == sp.zeros(3, 1))
chk('2(a) схема: (2 − 3p, −2 − p, p² − 2p)',
    [sp.expand(c) for c in product] == [sp.expand(c) for c in (2 - 3 * p, -2 - p, p ** 2 - 2 * p)])
quartic = sp.expand(product.dot(product))
chk('2(b) квадрат длины — p⁴ − 4p³ + 14p² − 8p + 8',
    quartic == sp.expand(p ** 4 - 4 * p ** 3 + 14 * p ** 2 - 8 * p + 8))
roots = [r for r in sp.solve(sp.diff(quartic, p), p) if r.is_real and r > 0]
least = min(float(quartic.subs(p, r)) for r in roots)
chk('2(b) схема: 6.75', near(A('q2b'), '6.75') and near(least, '6.75'))
by_heron = min(float(heron(A2, B2, C2).subs(p, r)) for r in roots)
chk('2(c) площадь по Герону совпадает с половиной корня',
    abs(by_heron - float(sp.sqrt(least)) / 2) < 1e-9)
chk('2(c) схема: 1.30', near(A('q2c'), '1.30') and near(by_heron, '1.30'))

print('\n=== 3. Площадь параллелограмма (май 2025 TZ3 Q11(c)) ===')
A3, B3, C3, D3 = Mx([1, -4, 0]), Mx([-3, -6, 2]), Mx([-1, -2, 4]), Mx([3, 0, 2])
chk('3 ABCD — параллелограмм: AB = DC', B3 - A3 == C3 - D3)
m = sp.Symbol('m')
found_m = sp.solve(list((B3 - A3).cross(D3 - A3) - m * Mx([-1, 1, -1])), m)
chk('3(i) схема: m = 12', found_m == {m: 12} and A('q3_i') == 12)
area3 = heron(A3, B3, D3) + heron(B3, C3, D3)
chk('3(ii) два треугольника по Герону дают ту же площадь',
    sp.simplify(area3 - A('q3_ii')) == 0)
chk('3(ii) схема: 12√3', sp.simplify(area3 - 12 * sp.sqrt(3)) == 0)

print('\n=== 4. Площадь треугольника PQR (ноябрь 2025 TZ1 Q12(d)) ===')
P4, Q4, R4 = Mx([sp.Rational(9, 2), 0, 0]), Mx([0, 18, 0]), Mx([0, 0, -6])
chk('4 вершины лежат на 4x + y − 3z = 18',
    all(4 * V[0] + V[1] - 3 * V[2] == 18 for V in (P4, Q4, R4)))
area4 = heron(P4, Q4, R4)
chk('4 схема: 68.8', near(area4, '68.8') and near(A('q4'), '68.8'))
chk('4 схема: ½√18954', sp.simplify(area4 - sp.sqrt(18954) / 2) == 0)

print('\n=== 5. Объём пирамиды PQRS (ноябрь 2025 TZ1 Q12(g)) ===')
S5 = Mx([-11, 5, 7])
chk('5 S лежит на нормальной прямой при γ = 3', S5 == Mx([1, 8, -2]) + 3 * Mx([-4, -1, 3]))
h = height_over(S5, P4, Q4, R4)
chk('5 высота — √234', sp.simplify(h ** 2 - 234) == 0)
volume = sp.simplify(area4 * h / 3)
chk('5 треть основания на высоту — 351', sp.simplify(volume - 351) == 0)
chk('5 схема: 351', A('q5') == 351)

print('\n=== 6. Тождество (май 2021 TZ2 Q5 и май 2024 TZ1 Q12(a)) ===')
random.seed(7)
holds, lhs_ok, rhs_ok, sum_ok = True, True, True, True
AA, BB, TH = sp.symbols('A B th')
UU, VV = sp.symbols('U V')
for _ in range(12):
    u = Mx([random.randint(-6, 6) for _ in range(3)])
    w = Mx([random.randint(-6, 6) for _ in range(3)])
    if u.norm() == 0 or w.norm() == 0:
        continue
    theta = sp.acos(u.dot(w) / (u.norm() * w.norm()))
    run = {AA: u.norm(), BB: w.norm(), TH: theta}
    cross_square = u.cross(w).dot(u.cross(w))
    holds &= sp.simplify(cross_square - (u.dot(u) * w.dot(w) - u.dot(w) ** 2)) == 0
    lhs_ok &= abs(float(A('q6_i').subs(run).evalf()) - float(cross_square)) < 1e-9
    rhs_ok &= abs(float(A('q6_ii').subs(run).evalf()) - float(u.dot(w) ** 2)) < 1e-9
    sum_ok &= abs(float(A('q7a').subs({UU: u.norm(), VV: w.norm(), TH: theta}).evalf())
                  - float(u.dot(u) * w.dot(w))) < 1e-9
chk('6 тождество выполняется на случайных векторах', holds)
chk('6(i) ответ равен |a × b|² на тех же векторах', lhs_ok)
chk('6(ii) ответ равен (a · b)² на тех же векторах', rhs_ok)
chk('7(a) ответ равен |u|²|v|² на тех же векторах', sum_ok)

print('\n=== 7. Длины и буквы из тождества (май 2024 TZ1 Q12(b)) ===')
pp, qq = sp.symbols('p q')
A7, B7, C7 = Mx([0, 1, 2]), Mx([pp, qq, 3]), Mx([3, 2, 1])
u7, v7 = B7 - A7, C7 - A7
chk('7(b)(i) площадь √6 даёт |u × v| = 2√6', sp.simplify(A('q7b_i') - 2 * sp.sqrt(6)) == 0)
identity = sp.Eq(3 ** 2 + (2 * sp.sqrt(6)) ** 2, sp.Symbol('L') ** 2 * v7.dot(v7))
length = [s for s in sp.solve(identity, sp.Symbol('L')) if s > 0]
chk('7(b)(ii) тождество даёт |u| = √3', length == [sp.sqrt(3)] and A('q7b_ii') == sp.sqrt(3))
system = sp.solve([sp.Eq(u7.dot(v7), 3), sp.Eq(u7.dot(u7), 3)], [pp, qq], dict=True)
pairs = sorted((sp.nsimplify(s[pp]), sp.nsimplify(s[qq])) for s in system)
chk('7(b)(iii) пары решений — (1, 2) и (7/5, 4/5)',
    pairs == [(sp.Integer(1), sp.Integer(2)), (sp.Rational(7, 5), sp.Rational(4, 5))])
chk('7(b)(iii) эталон — обе пары', sorted(tuple(pair) for pair in A('q7b_iii')) == pairs)
chk('7(b)(iii) обе пары дают площадь √6',
    all(sp.simplify(heron(A7, B7.subs({pp: a_, qq: b_}), C7) - sp.sqrt(6)) == 0
        for a_, b_ in pairs))

print('\n=== 8. Углы между плоскостями (май 2025 TZ1 Q11(a) и TZ3 Q11(e)) ===')
first = dihedral(X + 2 * Y + Z, X - Y - 2 * Z)
chk('8(a) двугранный угол — 60°', sp.simplify(first - sp.pi / 3) == 0)
chk('8(a) схема: 60°', A('q8a') == 60)
second = dihedral(-X + Y - Z + 5, 5 * X + Y - 7 * Z - 1)
chk('8(b) двугранный угол имеет косинус 1/5',
    sp.simplify(sp.cos(second) - sp.Rational(1, 5)) == 0)
chk('8(b) схема: 1/5', A('q8b') == sp.Rational(1, 5))

print('\n=== 9. Угол прямой с плоскостью (май 2023 TZ1 P2 Q8) ===')
alpha = sp.Symbol('alpha', positive=True)
tilt = to_plane([3, 2, -1], 4 * X + sp.cos(alpha) * Y + sp.sin(alpha) * Z - 1)
equation = sp.lambdify(alpha, sp.sin(tilt) - sp.sin(alpha), 'math')
lo, hi = 0.01, 1.5
for _ in range(200):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if equation(mid) * equation(lo) > 0 else (lo, mid)
chk('9 корень уравнения — 0.932', near((lo + hi) / 2, '0.932'))
chk('9 схема: 0.932 радиан', near(A('q9'), '0.932'))
# В градусном режиме уравнение то же самое с α = β·π/180, поэтому корень
# просто пересчитывается: 0.932389 рад = 53.4219°. В схеме напечатано
# 54.4219° — опечатка, и она записана в corpus_issues карточки.
in_degrees = sp.lambdify(alpha, sp.sin(to_plane([3, 2, -1],
                         4 * X + sp.cos(alpha * sp.pi / 180) * Y
                         + sp.sin(alpha * sp.pi / 180) * Z - 1))
                         - sp.sin(alpha * sp.pi / 180), 'math')
lo2, hi2 = 1.0, 89.0
for _ in range(200):
    mid = (lo2 + hi2) / 2
    lo2, hi2 = (mid, hi2) if in_degrees(mid) * in_degrees(lo2) > 0 else (lo2, mid)
chk('9 в градусном режиме тот же корень — 53.4°, а не 54.4 из схемы',
    near((lo2 + hi2) / 2, '53.42') and near(0.932389 * 180 / float(sp.pi), '53.42'))

print('\n=== 10. Сфера: расстояние и пеленг (май 2025 TZ2 Paper 3 Q2(e), (f)) ===')
theta10 = sp.Rational(573, 10) * sp.pi / 180
b10 = Mx([6 * sp.sin(2 * sp.pi / 3), 6 * sp.cos(2 * sp.pi / 3), 0])
m10 = Mx([0, 6 * sp.cos(theta10), 6 * sp.sin(theta10)])
p10 = Mx([0, 0, 6])
central = sp.acos(b10.dot(m10) / (b10.norm() * m10.norm()))
chk('10(e) центральный угол — 105.7°', near(float(central) * 180 / float(sp.pi), '105.7'))
chk('10(e) дуга 6θ — 11.1', near(6 * float(central), '11.1') and near(A('q10_i'), '11.1'))
bearing = sp.acos(b10.cross(m10).dot(b10.cross(p10))
                  / (b10.cross(m10).norm() * b10.cross(p10).norm()))
chk('10(f) схема: 029.1°', near(float(bearing) * 180 / float(sp.pi), '29.1')
    and near(A('q10_ii'), '29.1'))

print('\n=== 11. Ближайшая точка (ноябрь 2025 TZ3 Q10 и май 2023 TZ2 Q6(b)) ===')
mu = sp.Symbol('mu')
P11, A11, B11 = Mx([-1, 1, -13]), Mx([2, -4, 2]), Mx([7, -6, 1])
PN = (A11 + mu * (B11 - A11)) - P11
chk('11(a) PN · AB — 10 + 30μ', sp.expand(PN.dot(B11 - A11)) == sp.expand(10 + 30 * mu))
chk('11(a) эталон совпадает', sp.expand(A('q11a') - PN.dot(B11 - A11)) == 0)
_, at = least_square(PN, mu)
N = (A11 + mu * (B11 - A11)).subs(at)
chk('11(b) минимум квадрата длины даёт μ = −1/3', at[mu] == sp.Rational(-1, 3))
chk('11(b) схема: (1/3, −10/3, 7/3)', list(N) == [sp.Rational(1, 3), sp.Rational(-10, 3),
                                                  sp.Rational(7, 3)])
chk('11(b) эталон совпадает', Mx(A('q11b')) == N)
lam = sp.Symbol('lam')
line = Mx([0, 2, 4]) + lam * Mx([1, -2, -2])
chk('11(c) прямая лежит в обеих плоскостях',
    sp.expand(2 * line[0] - line[1] + 2 * line[2]) == 6
    and sp.expand(4 * line[0] + 3 * line[1] - line[2]) == 2)
_, at = least_square(line, lam)
nearest = line.subs(at)
chk('11(c) схема: (4/3, −2/3, 4/3)',
    list(nearest) == [sp.Rational(4, 3), sp.Rational(-2, 3), sp.Rational(4, 3)])
chk('11(c) эталон совпадает', Mx(A('q11c')) == nearest)

print('\n=== 12. Расстояния до прямой (май 2023 TZ1 Q12(c) и май 2021 TZ2 Q8(b)) ===')
P12, A12 = Mx([0, 8, -3]), Mx([6, 8, 3])
chk('12(a) PA = (6, 0, 6) и угол между PA и (1, 1, 0) — π/3',
    A12 - P12 == Mx([6, 0, 6])
    and sp.simplify(sp.acos((A12 - P12).dot(Mx([1, 1, 0]))
                            / ((A12 - P12).norm() * Mx([1, 1, 0]).norm())) - sp.pi / 3) == 0)
square, _ = least_square(P12 + lam * Mx([1, 1, 0]) - A12, lam)
chk('12(a) минимум квадрата расстояния — 54', sp.simplify(square - 54) == 0)
chk('12(a) схема: 3√6 = √54', sp.simplify(A('q12a') ** 2 - 54) == 0)
nu = sp.Symbol('nu')
gap = (Mx([3, 2, -1]) + lam * Mx([2, -2, 2])) - (Mx([2, 0, 4]) + nu * Mx([1, -1, 1]))
chk('12(b) направления кратны: прямые параллельны',
    Mx([2, -2, 2]).cross(Mx([1, -1, 1])) == sp.zeros(3, 1))
square = sp.expand(gap.dot(gap)).subs(nu, 0)             # параллельны: хватит одного параметра
least = sp.minimum(square, lam, sp.S.Reals)
chk('12(b) минимум квадрата расстояния — 18', sp.simplify(least - 18) == 0)
chk('12(b) схема: 3√2 = √18', sp.simplify(A('q12b') ** 2 - 18) == 0)

print('\n=== таймер. Вектор w (май 2024 TZ1 Q12(c)) ===')
At, Ct = Mx([0, 1, 2]), Mx([3, 2, 1])
ut, vt = Mx([1, 1, 1]), Ct - At
both = [Mx(list(item)) for item in A('qt')]
chk('таймер оба w перпендикулярны u и v',
    all(sp.simplify(w.dot(ut)) == 0 and sp.simplify(w.dot(vt)) == 0 for w in both))
chk('таймер у обоих площадь ACD равна 5',
    all(sp.simplify(heron(At, Ct, Ct + w) - 5) == 0 for w in both))
chk('таймер второй — первый в обратную сторону', sp.simplify(both[0] + both[1]) == sp.zeros(3, 1))
chk('таймер схема: |w| = 5√66/33 · √6 = 10/√11',
    sp.simplify(both[0].norm() - 10 / sp.sqrt(11)) == 0)
chk('таймер схема: x = ±1.2309', near(float(both[0][0]), '1.2309'))

# ------------------------------------------------------------------ ноутбук

BREAK_C7 = {
    'q1_i': 'vec(0, 36, 0)',                            # знак средней компоненты
    'q1_ii': '0',                                       # угол не тот
    'q2a': 'vec(2 - 3*p, 2 + p, p**2 - 2*p)',           # знак средней компоненты
    'q2b': '0.326',                                     # значение p вместо величины
    'q2c': '2.60',                                      # половина забыта
    'q3_i': '-12',                                      # знак m
    'q3_ii': '6*sqrt(3)',                               # взят треугольник
    'q4': '137.7',                                      # половина забыта
    'q5': '1053',                                       # треть забыта
    'q6_i': 'A**2*B**2*cos(th)**2',                     # синус и косинус местами
    'q6_ii': 'A**2*B**2*sin(th)**2',                    # синус и косинус местами
    'q7a': 'U*V*cos(th)**2 + U*V*sin(th)**2',           # длины не возведены в квадрат
    'q7b_i': 'sqrt(6)',                                 # площадь не удвоена
    'q7b_ii': '3',                                      # корень не извлечён
    'q7b_iii': '[[1, Rational(4, 5)], [Rational(7, 5), 2]]',   # пары перепутаны
    'q8a': '120',                                       # тупой угол между нормалями
    'q8b': '-Rational(1, 5)',                           # знак: острый угол
    'q9': '0.639',                                      # угол с нормалью
    'q10_i': '1.84',                                    # центральный угол вместо дуги
    'q10_ii': '150.9',                                  # смежный угол
    'q11a': '-10 - 30*mu',                              # PN взят как OP − ON
    'q11b': '(Rational(11, 3), Rational(-14, 3), Rational(5, 3))',   # знак μ
    'q11c': 'Rational(4, 3)',                           # параметр вместо точки
    'q12a': 'sqrt(108)',                                # не поделено на |v|
    'q12b': 'sqrt(54)',                                 # не поделено на |v|
    'qt': '[vec(1, -2, 1), vec(-1, 2, -1)]',            # длина не подобрана
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
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 25)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = BREAK_C7
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
           'nothing satisfies', 'is not u × v', 'does not measure that', 'with numbers this gives')
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
