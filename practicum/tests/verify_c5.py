"""Независимая проверка каждого ответа практикума C5.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **не решать так, как решает ноутбук**.
Проверки ноутбука приравнивают компоненты, решают системы sympy и считают
углы через скалярное произведение.

Тест идёт другими путями. Скрещивание и пересечение — смешанным
произведением (A − P)·(d₁ × d₂): ноль — прямые в одной плоскости. Угол
между прямыми — векторным произведением, sin θ = |d₁ × d₂|/(|d₁||d₂|), и
он острый сам собой. Угол при вершине пирамиды — теоремой косинусов по
трём сторонам, как METHOD 1 схемы. Равные углы в задании 5 — через atan2
направлений на плоскости, без скалярного произведения вовсе. Точка
пересечения — подстановкой параметрической прямой в декартову форму
другой. Четвёртая вершина — из того, что диагонали делятся пополам.

Второй якорь — числа схем оценивания: 10.2956…, 0.798037…, 4.78727…,
0.7637…, 107.703…, 8.44984…

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_c5.py
"""
import contextlib
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import mpmath as mpm
import sympy as sp

import build_c5 as gen

mpm.mp.dps = 30
res = []
Mx = sp.Matrix


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    """Эталон из генератора — в пространстве имён ноутбука."""
    import kit
    names = dict(vars(kit))
    names.update({letter: sp.Symbol(letter) for letter in ('p', 'a', 'b', 'k', 'la', 'theta')})
    return eval(gen.ANSWERS[name], names)


def sig(value, sf=3):
    return f"{float(value):.{sf}g}"


def agrees(answer, exact, sf=3):
    return sig(answer, sf) == sig(exact, sf)


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр (схема обрезает)."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def cross(u, v):
    return Mx(u).cross(Mx(v))


def triple(P, Q, d1, d2):
    """(Q − P)·(d₁ × d₂): ноль — две прямые лежат в одной плоскости."""
    return (Mx(Q) - Mx(P)).dot(cross(d1, d2))


def same_vec(one, two):
    return all(sp.simplify(sp.sympify(p) - sp.sympify(q)) == 0 for p, q in zip(one, two))


print('=== Задание 1: параллелограмм ===')
PA, PB, PC = Mx([1, -4, 0]), Mx([-3, -6, 2]), Mx([-1, -2, 4])
d, e = sp.symbols('d1:4'), None
D1 = Mx(sp.symbols('d1:4'))
middle = sp.solve(list((PA + PC) / 2 - (PB + D1) / 2), list(D1), dict=True)[0]
D_true = D1.subs(middle)
chk('1a: диагонали делятся пополам — D = (3, 0, 2), и BC = AD = (2, 4, 2) (markscheme)',
    list(D_true) == [3, 0, 2] and list(PC - PB) == [2, 4, 2] and list(A('q1a')) == [3, 0, 2])
chk('1b: E — середина BD = (0, −3, 2) (markscheme)', list((PB + D_true) / 2) == [0, -3, 2]
    and list(A('q1b')) == [0, -3, 2])

print('\n=== Задание 2: |a + b| ===')
lengths = (13, 15)
low, high = abs(lengths[1] - lengths[0]), lengths[0] + lengths[1]
phi = sp.symbols('phi', real=True)
square = 13 ** 2 + 15 ** 2 + 2 * 13 * 15 * sp.cos(phi)
chk('2a: |a + b|² = 169 + 225 + 390 cos φ — от 4 до 784, то есть от 2 до 28',
    sp.sqrt(square.subs(phi, sp.pi)) == 2 and sp.sqrt(square.subs(phi, 0)) == 28
    and A('q2a') == sp.Interval(low, high))
p_true = Mx([12, -5]) * sp.Rational(13 - 15, 13)
chk('2b: p = −(2/13)a = (−24/13, 10/13) ≈ (−1.85, 0.769) (markscheme)',
    same_vec(p_true, A('q2b')) and agrees(p_true[0], -1.85) and agrees(p_true[1], 0.769))
turn = Mx([[0, -1], [1, 0]]) * Mx([12, -5])        # поворот на 90°: (5, 12)
q_true = turn * sp.Rational(15, 13)
chk('2c: поворот a на 90° и растяжение до 15 — (75/13, 180/13), обе компоненты положительны',
    list(turn) == [5, 12] and same_vec(q_true, A('q2c')) and agrees(q_true[1], 13.8))

print('\n=== Задание 3: OM · MC ===')
la, th, kk, rot = sp.symbols('la theta k rot', positive=True)
import kit
ai = la * Mx([sp.cos(rot), sp.sin(rot)])                # фигура повёрнута на rot — не как в ноутбуке
ci = 2 * la * Mx([sp.cos(rot + th), sp.sin(rot + th)])
Bi = ai + ci
Mi = ai + kk * (Bi - ai)
OMMC = sp.simplify(sp.expand_trig(Mi.dot(ci - Mi)))
given = sp.simplify(la ** 2 * (1 - 2 * kk) * (2 * sp.cos(th) - (1 - 2 * kk)))
chk('3b: в повёрнутой фигуре OM·MC = |a|²(1 − 2k)(2cos θ − (1 − 2k))', sp.simplify(OMMC - given) == 0)
space = dict(vars(kit))
space.update({'la': la, 'theta': th, 'k': kk, 'a': ai, 'c': ci})
chk('3a: эталоны OM и MC совпадают с фигурой',
    same_vec(eval(gen.ANSWERS['q3a_OM'], space), Mi) and same_vec(eval(gen.ANSWERS['q3a_MC'], space), ci - Mi))
chk('3b: эталон — это OM·MC до разложения на множители',
    sp.simplify(eval(gen.ANSWERS['q3b'], space) - given) == 0)

print('\n=== Задание 4: пирамида ===')
PB4, PC4, PV4 = Mx([6, 8, 0]), Mx([6, 0, 0]), Mx([3, 4, 9])
BV = sp.sqrt((PB4 - PV4).dot(PB4 - PV4))
CV = sp.sqrt((PC4 - PV4).dot(PC4 - PV4))
BC = sp.sqrt((PB4 - PC4).dot(PB4 - PC4))
chk('4a: BV = √106 = 10.2956 (markscheme)', BV == sp.sqrt(106) and near(sp.N(BV, 20), '10.2956') and agrees(A('q4a'), BV))
cosine_rule = (BV ** 2 + CV ** 2 - BC ** 2) / (2 * BV * CV)
angle4 = sp.acos(cosine_rule)
chk('4b: теорема косинусов, BC = 8 — угол 0.798037 рад (markscheme)', BC == 8 and near(sp.N(angle4, 20), '0.798037')
    and agrees(A('q4b'), angle4))

print('\n=== Задание 5: равные углы ===')
p = sp.symbols('p')
chk('5a: a·c = −5p − 42, b·c = −8p − 54 (markscheme)',
    sp.expand(Mx([-5, 7]).dot(Mx([p, -6])) - A('q5a_i').subs(sp.Symbol('p'), p)) == 0
    and sp.expand(Mx([-8, 9]).dot(Mx([p, -6])) - A('q5a_ii').subs(sp.Symbol('p'), p)) == 0)


def spread(u, w):
    """Угол между направлениями на плоскости через atan2, от 0 до π."""
    gap = abs(mpm.atan2(u[1], u[0]) - mpm.atan2(w[1], w[0]))
    return gap if gap <= mpm.pi else 2 * mpm.pi - gap


p5 = mpm.findroot(lambda pp: spread((-5, 7), (pp, -6)) - spread((-8, 9), (pp, -6)), 4.8)
chk('5b: равные углы через atan2 — p = 4.78727 (markscheme)', near(p5, '4.78727') and agrees(A('q5b'), p5))

print('\n=== Задание 6: декартова форма ===')
x, y, z, t = sp.symbols('x y z t')
cart6 = [(x - 1) / 2 - (y + 2) / 3, (y + 2) / 3 - z]
line6 = A('q6a')
lam6 = [symbol for symbol in line6.free_symbols][0]
start6, step6 = line6.subs(lam6, 0), line6.diff(lam6)
points6 = [Mx([sp.solve(cart6 + [z - value], [x, y, z], dict=True)[0][s] for s in (x, y, z)])
           for value in (0, 1)]
chk('6a: две точки декартовой прямой (z = 0 и z = 1) лежат на эталонной прямой: (P − a) × b = 0',
    all(cross(pt - start6, step6) == Mx([0, 0, 0]) for pt in points6))
sol6 = sp.solve([expr.subs({x: t, y: 4, z: -8 + 2 * t}) for expr in cart6], [t], dict=True)
chk('6b: L2 в декартову форму L1 — t = 5, точка (5, 4, 2) (markscheme)',
    sol6 == [{t: 5}] and list(A('q6b')) == [5, 4, 2])

print('\n=== Задание 7: угол 45° и точка A ===')
a = sp.symbols('a', real=True)
d1, d2 = Mx([2, 1, -1]), Mx([a, 1, -1])
sine_sq = cross(d1, d2).dot(cross(d1, d2)) / (d1.dot(d1) * d2.dot(d2))
roots7 = sp.solve(sp.Eq(sine_sq, sp.Rational(1, 2)), a)
chk('7b: sin²θ = 1/2 через векторное произведение — a = −4 ± 3√2 (markscheme)',
    sorted(roots7, key=float) == sorted(A('q7b'), key=float))
point7 = Mx([a * t, 1 + t, 2 - t])
sol7 = sp.solve([(point7[0] + 1) / 2 - point7[1], point7[1] - (3 - point7[2])], [t], dict=True)
chk('7c: L2 в декартову форму L1 — t = 1/(a − 2), k = 2',
    len(sol7) == 1 and sp.simplify(sol7[0][t] - 1 / (a - 2)) == 0 and A('q7c_k') == 2)
chk('7c: A = (a/(a − 2), (a − 1)/(a − 2), (2a − 5)/(a − 2)) (markscheme)',
    same_vec(point7.subs(sol7[0]), [c.subs(sp.Symbol('a'), a) for c in A('q7c_A')]))
chk('7a: точка (−1, 0, 3) удовлетворяет декартовой форме', (-1 + 1) / 2 == 0 == 3 - 3)

print('\n=== Задание 8: скрещиваются ===')
P8, dir8 = Mx([-1, 1, -13]), Mx([7, 1, 2])
A8, B8 = Mx([2, -4, 2]), Mx([7, -6, 1])
chk('8c: d₁ × d₂ ≠ 0 и смешанное произведение ≠ 0 — скрещиваются',
    cross(dir8, B8 - A8) != Mx([0, 0, 0]) and triple(P8, A8, dir8, B8 - A8) != 0 and A('q8c') == 'skew')
lam8, mu8 = sp.symbols('lam mu')
pair8 = sp.solve(list((P8 + lam8 * dir8 - A8 - mu8 * (B8 - A8))[:2]), [lam8, mu8], dict=True)[0]
chk('8c: первые две компоненты — λ = −1, μ = −2, третья: −15 ≠ 4 (markscheme)',
    [pair8[lam8], pair8[mu8]] == A('q8c_pair') and (P8 + lam8 * dir8)[2].subs(pair8) == -15
    and (A8 + mu8 * (B8 - A8))[2].subs(pair8) == 4)

print('\n=== Задание 9: перпендикулярны и пересекаются ===')
aa, bb = sp.symbols('a b')
dA, dB = Mx([0, aa, 1]), Mx([1, 2, 3])
a9 = sp.solve(dA.dot(dB), aa)
b9 = sp.solve(triple(Mx([4, 0, -1]), Mx([1, 0, -bb]), dA.subs(aa, a9[0]), dB), bb)
chk('9: d₁·d₂ = 0 даёт a = −3/2, смешанное произведение ноль — b = 14 (markscheme)',
    a9 == [sp.Rational(-3, 2)] and b9 == [14] and list(A('q9')) == [sp.Rational(-3, 2), 14])

print('\n=== Задание 10: три точки на прямой ===')
k = sp.symbols('k')
AB10, AC10 = Mx([k, -2, 1]) - Mx([1, 2, 3]), Mx([5, 0, 2]) - Mx([1, 2, 3])
k10 = sp.solve(list(cross(AB10, AC10)), k, dict=True)
chk('10b: AB × AC = 0 — k = 9', k10 == [{k: 9}] and A('q10b') == 9)
chk('10a: AB = (k − 1, −4, −2), AC = (4, −2, −1) (markscheme)',
    same_vec(AB10, [c.subs(sp.Symbol('k'), k) for c in A('q10a_AB')]) and list(A('q10a_AC')) == [4, -2, -1])
P10, d10 = Mx([1, 2, 3]), AC10
Q10, e10 = Mx([1, 0, 1]), Mx([2, 3, -1])
chk('10c(ii): направления не кратны, смешанное произведение ≠ 0 — скрещиваются',
    cross(d10, e10) != Mx([0, 0, 0]) and triple(P10, Q10, d10, e10) != 0 and A('q10cii') == 'skew')
pair10 = sp.solve(list((P10 + lam8 * d10 - Q10 - mu8 * e10)[:2]), [lam8, mu8], dict=True)[0]
chk('10c(ii): λ = 1/4, μ = 1/2, третья: 2.75 ≠ 0.5 (markscheme)',
    [pair10[lam8], pair10[mu8]] == A('q10cii_pair')
    and (P10 + lam8 * d10)[2].subs(pair10) == sp.Rational(11, 4) and (Q10 + mu8 * e10)[2].subs(pair10) == sp.Rational(1, 2))

print('\n=== Задание 11: самолёты ===')
vA, vB = Mx([-6, 2, 4]), Mx([4, 2, -2])
bearing = math.degrees(math.atan2(4, 2))
chk('11a: atan2(восток 4, север 2) = 63.4° — 063 (markscheme)', round(bearing) == 63 and A('q11a') == '063')
chk('11b: √56 = 7.48 и √24 = 4.90 (markscheme 7.48…, 4.89…)',
    agrees(A('q11b_A'), sp.sqrt(56)) and agrees(A('q11b_B'), sp.sqrt(24)) and near(sp.N(sp.sqrt(24)), '4.89'))
sine11 = sp.sqrt(cross(vA, vB).dot(cross(vA, vB)) / (vA.dot(vA) * vB.dot(vB)))
angle11 = math.degrees(math.asin(float(sine11)))
chk('11c: arcsin через векторное произведение — 40.2°, а cos θ = −0.7637 (markscheme)',
    agrees(A('q11c'), angle11) and near(vA.dot(vB) / (sp.sqrt(56) * sp.sqrt(24)), '-0.7637'))
t1, t2 = sp.symbols('t1 t2')
sol11 = sp.solve(list(Mx([19, -1, 1]) + t1 * vA - Mx([1, 0, 12]) - t2 * vB), [t1, t2], dict=True)
chk('11d: t₁ = 2, t₂ = 3/2, P(7, 3, 9), разница 0.5 минуты (markscheme)',
    sol11 == [{t1: 2, t2: sp.Rational(3, 2)}] and list(A('q11d_i')) == [7, 3, 9]
    and A('q11d_ii') == sp.Float(0.5))

print('\n=== Задание 12: вертолёт ===')
r12 = lambda tt: Mx([10, 3, sp.Rational(1, 2)]) + 4 * tt * Mx([10, -25, 0])
step = r12(1) - r12(0)
speed12 = sp.sqrt(step.dot(step))
chk('12a: |r(1) − r(0)| = 20√29 = 107.703 (markscheme)', speed12 == 20 * sp.sqrt(29) and near(sp.N(speed12), '107.703')
    and agrees(A('q12a'), speed12))
beta = math.degrees(math.asin(16 / math.sqrt(float(speed12) ** 2 + 256)))
chk('12b: arcsin(16/|v|) = 8.44984° (markscheme)', near(beta, '8.44984') and agrees(A('q12b'), beta))

print('\n=== Таймер ===')
PL, dL, PM, dM = Mx([1, 2, -3]), Mx([2, 3, 6]), Mx([9, 9, 11]), Mx([4, 1, 2])
chk('timer: смешанное произведение ноль — прямые в одной плоскости и не параллельны',
    triple(PL, PM, dL, dM) == 0 and cross(dL, dM) != Mx([0, 0, 0]))
sol_t = sp.solve(list(PL + t1 * dL - PM - t2 * dM), [t1, t2], dict=True)
chk('timer: s = 2, t = −1, A = (5, 8, 9) (markscheme)',
    sol_t == [{t1: 2, t2: -1}] and list(A('qt')) == [5, 8, 9] and list(A('qt_pair')) == [2, -1])

BREAK_C5 = {
    'q1a': '(-1, -8, -2)',                        # D = a + b − c: не тот порядок вершин
    'q1b': '(-1, -5, 1)',                         # середина AB, а не AC
    'q2a': 'Interval(13, 28)',                    # наименьшее — |a|
    'q2b': 'vec(Rational(-180, 13), Rational(75, 13))',   # b вместо a + b
    'q2c': 'vec(5, 12)',                          # направление не растянуто до 15
    'q3a_OM': 'a + k*a',                          # AB принят за a
    'q3a_MC': 'a - (1 - k)*c',                    # CM вместо MC
    'q3b': '2*(1 - 2*k)*la**2*cos(theta) - la**2 + k*(1 - k)*la**2',   # |c|² = |a|²
    'q4a': '(-3, -4, 9)',                         # вектор вместо длины
    'q4b': '0.927',                               # угол между OB и OC
    'q5a_i': '5*p - 42',                          # потерян знак −5
    'q5a_ii': '(-8*p, -54)',                      # покомпонентное произведение — вектор
    'q5b': '4.8',                                 # две значащие цифры
    'q6a': 'vec(-1, 2, 0) + lam*vec(2, 3, 1)',    # знаки точки из числителей
    'q6b': '(2, 4, -4)',                          # λ = 2 подставлено в L2
    'q7a': 'vec(-1, 0, 3) + lam*vec(2, 1, 1)',    # 3 − z: знак направления
    'q7b': '[-4 + 3*sqrt(2)]',                    # потерян второй корень
    'q7c_k': '-2',                                # знак
    'q7c_A': '(2/(a - 2) - 1, 1/(a - 2), (3*a - 7)/(a - 2))',   # t подставлено в L1
    'q8a': 'vec(7, 1, 2) + lam*vec(-1, 1, -13)',  # точка и направление местами
    'q8b': 'vec(2, -4, 2) + mu*vec(7, -6, 1)',    # радиус-вектор B вместо AB
    'q8c': "'intersecting'",                      # третья компонента не проверена
    'q8c_pair': '[-1, 2]',                        # знак μ
    'q9': '[Rational(3, 2), 14]',                 # знак a: не перпендикулярны
    'q10a_AB': 'vec(1 - k, 4, 2)',                # BA вместо AB
    'q10a_AC': 'vec(-4, 2, 1)',                   # CA вместо AC
    'q10b': '5',                                  # k − 1 = 4
    'q10ci': 'vec(1, 2, 3) + lam*vec(5, 0, 2)',   # радиус-вектор C
    'q10cii': "'parallel'",                       # направления не кратны
    'q10cii_pair': '[Rational(1, 4), Rational(-1, 2)]',   # знак μ
    'q11a': "'027'",                              # от востока
    'q11b_A': '19.1',                             # длина положения (19, −1, 1)
    'q11b_B': '12.0',                             # то же для B
    'q11c': '139.8',                              # тупой угол
    'q11d_i': '(9, 4, 8)',                        # t₁ = 2 подставлено в r_B
    'q11d_ii': '30',                              # секунды
    'q12a': '26.9',                               # потерян множитель 4
    'q12b': '0.147',                              # радианы
    'qt_pair': '[-1, 2]',                         # параметры местами
    'qt': '(17, 11, 15)',                         # s = 2 подставлено в M
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
BREAK = BREAK_C5
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
