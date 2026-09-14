"""Независимая проверка каждого ответа практикума D6.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **не складывать площадь так, как её
складывает ноутбук**. Ноутбук берёт площадь адаптивной квадратурой Гаусса —
Лежандра под самой формулой, а буквы и границы находит методом Ньютона
по площадям.

Тест идёт путём схем оценивания: первообразная — sympy.integrate, как её
пишет схема (arcsin, интегрирование по частям, подстановка u = 16 − x²),
пределы подставляются руками, уравнение медианы решается mpmath.findroot
по первообразной, а не по площади. Там, где первообразной нет —
3x·arccos(x²), кусочная плотность марафона, — площадь берёт mpmath.quad,
то есть квадратура tanh-sinh, а не Гаусс — Лежандр. Доля времени в
задании 1 — корнями косинуса и числом периодов, без интеграла вовсе.

Второй якорь — числа схем оценивания: 0.405574…, 0.645038…, 0.768039…,
1.02925…, 0.360034… и 0.124861…, 0.103749…, 4.01290…, 0.456309…,
0.0289805…, 0.620012…, 40.9576…, 6.68563…, 0.260919…, 0.239358…

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_d6.py
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
import mpmath as mpm
import sympy as sp

import build_d6 as gen

mpm.mp.dps = 30
res = []
x, t = sp.symbols('x t')


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name])


def sig(value, sf=3):
    return f"{float(value):.{sf}g}"


def agrees(answer, exact, sf=3):
    return sig(answer, sf) == sig(exact, sf)


def near(value, anchor):
    """Совпадение с числом схемы оценивания до всех его напечатанных цифр.

    Схема печатает начало числа с многоточием, 0.405574…, — то есть
    обрезает, а не округляет. Поэтому допуск — единица последнего разряда.
    """
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def same(expr_one, expr_two, letters, samples):
    """Два выражения совпадают в каждой точке samples."""
    difference = sp.sympify(expr_one) - sp.sympify(expr_two)
    names = [str(letter) for letter in letters]
    for sample in samples:
        # буквы сверяются по имени: у эталона k без условия positive
        run = {s: dict(zip(names, sample))[s.name] for s in difference.free_symbols}
        if abs(complex(sp.N(difference.subs(run), 30))) > 1e-20:
            return False
    return True


print('=== Задание 1: груз на пружине ===')
w = mpm.mpf('7.8')
first = mpm.acos(-mpm.mpf('0.25')) / w          # −0.4cos(7.8t) + 1.4 = 1.5 ⇔ cos(7.8t) = −0.25
second = (2 * mpm.pi - mpm.acos(-mpm.mpf('0.25'))) / w
period = 2 * mpm.pi / w
chk('1e: второе время на 1.5 — 0.571757 (markscheme)', near(second, '0.571757'))
above = second - first
chk('1e: за период выше 1.5 — 0.337978 с (markscheme)', near(above, '0.337978'))
whole = int(5 / period)
chk('1e: в пяти секундах шесть полных периодов, и в седьмом до t = 5 выше 1.5 не бывает',
    whole == 6 and whole * period + first > 5)
share1 = whole * above / 5
chk('1e: 6·0.337978/5 = 0.405574 (markscheme)', near(whole * above, '2.02787') and near(share1, '0.405574'))
chk('1e: ответ', agrees(A('q1e'), share1))

print('\n=== Задание 2: k по arcsin ===')
k = sp.symbols('k', positive=True)
anti2 = sp.integrate(1 / sp.sqrt(4 - 3 * x ** 2), x)
chk('2a: первообразная — arcsin(√3x/2)/√3 (markscheme)', sp.simplify(sp.diff(sp.asin(sp.sqrt(3) * x / 2) / sp.sqrt(3), x)
                                                         - 1 / sp.sqrt(4 - 3 * x ** 2)) == 0)
area2 = anti2.subs(x, 1) - anti2.subs(x, 0)
k2 = sp.solve(sp.Eq(k * area2, 1), k)
chk('2a: k = 3√3/π (markscheme)', len(k2) == 1 and sp.simplify(k2[0] - 3 * sp.sqrt(3) / sp.pi) == 0)
chk('2a: ответ точный и тот же', sp.simplify(A('q2a') - 3 * sp.sqrt(3) / sp.pi) == 0 and not A('q2a').has(sp.Float))

print('\n=== Задание 3: k из площади ===')
anti3 = sp.integrate(x / (x ** 2 + k) ** sp.Rational(3, 2), x)
area3 = sp.simplify(anti3.subs(x, 4) - anti3.subs(x, 0))
chk('3a: площадь = 1/√k − 1/√(16 + k)', same(area3, 1 / sp.sqrt(k) - 1 / sp.sqrt(16 + k), [k], [(sp.Rational(1, 3),), (2,), (7,)]))
chk('3a: ответ совпадает с площадью', same(A('q3a'), area3, [k], [(sp.Rational(1, 2),), (3,), (11,)]))
k3 = mpm.findroot(lambda kk: mpm.sqrt(16 + kk) - mpm.sqrt(kk) - mpm.sqrt(kk) * mpm.sqrt(16 + kk), 0.6)
chk('3b: k = 0.645038 (markscheme)', near(k3, '0.645038') and agrees(A('q3b'), k3))

print('\n=== Задание 4: axeˣ ===')
a, b = sp.symbols('a b', positive=True)
anti4 = sp.integrate(x * sp.exp(x), x)
chk('4a: по частям — (x − 1)eˣ', sp.simplify(anti4 - (x - 1) * sp.exp(x)) == 0)
a4 = 1 / sp.simplify(anti4.subs(x, b) - anti4.subs(x, 0))
chk('4a: a = 1/(beᵇ − eᵇ + 1) (markscheme)', same(a4, 1 / (b * sp.exp(b) - sp.exp(b) + 1), [b], [(sp.Rational(1, 2),), (2,), (5,)]))
chk('4a: ответ', same(A('q4a'), a4, [b], [(sp.Rational(3, 4),), (sp.Rational(5, 2),), (4,)]))
m4 = mpm.findroot(lambda mm: mm * mpm.exp(mm) - mpm.exp(mm) + 1 - mpm.mpf('0.5'), 0.8)
chk('4b: m = 0.768039 (markscheme)', near(m4, '0.768039') and agrees(A('q4b'), m4))

print('\n=== Задание 5: кусочная плотность ===')
area5 = sp.integrate(k * x, (x, 0, k)) + sp.integrate(2 * k * x - x ** 2, (x, k, 2 * k))
chk('5a: площадь = 7k³/6, и 7k³ = 6', sp.simplify(area5 - 7 * k ** 3 / 6) == 0
    and same(A('q5a'), area5, [k], [(sp.Rational(1, 2),), (2,), (3,)]))
k5 = (mpm.mpf(6) / 7) ** (mpm.mpf(1) / 3)
chk('5b: k = 0.949914, первый кусок 3/7 = 0.428571 (markscheme)', near(k5, '0.949914') and near(k5 ** 3 / 2, '0.428571'))
m5 = mpm.findroot(lambda mm: k5 ** 3 / 2 + (k5 * mm ** 2 - mm ** 3 / 3) - (k5 ** 3 - k5 ** 3 / 3) - mpm.mpf('0.5'), 1.0)
chk('5b: m = 1.02925 (markscheme)', near(m5, '1.02925') and agrees(A('q5b'), m5))
chk('5b: формула первого куска дала бы 1.026 — те же три цифры, как предупреждает схема',
    agrees(1 / mpm.sqrt(k5), m5) and abs(1 / mpm.sqrt(k5) - m5) > 1e-3)

print('\n=== Задание 6: arccos ===')
anti6 = sp.integrate(sp.acos(x), x)
chk('6: первообразная — x·arccos x − √(1 − x²) (markscheme)', sp.simplify(sp.diff(x * sp.acos(x) - sp.sqrt(1 - x ** 2), x) - sp.acos(x)) == 0)
F6 = lambda q: q * mpm.acos(q) - mpm.sqrt(1 - q * q) + 1
m6 = mpm.findroot(lambda q: F6(q) - mpm.mpf('0.5'), 0.36)
chk('6a: m = 0.360034 (markscheme)', near(m6, '0.360034') and agrees(A('q6a'), m6))
a6 = mpm.findroot(lambda d: F6(m6 + d) - F6(m6 - d) - mpm.mpf('0.3'), 0.12)
chk('6b: a = 0.124861 (markscheme)', near(a6, '0.124861') and agrees(A('q6b'), a6))

print('\n=== Задание 7: треугольная плотность ===')
aa, bb, cc, mm = sp.symbols('a b c m', real=True)
left = sp.integrate(2 * (x - aa) / ((bb - aa) * (cc - aa)), (x, aa, mm))
roots7 = sp.solve(sp.Eq(left, sp.Rational(1, 2)), mm)
chk('7: у уравнения медианы два корня, a ± √((b − a)(c − a)/2)', len(roots7) == 2)
for case in ({aa: 0, bb: 4, cc: 3}, {aa: 1, bb: 3, cc: sp.Rational(5, 2)}, {aa: -2, bb: 6, cc: 5}):
    on_piece = [r.subs(case) for r in roots7 if case[aa] <= r.subs(case) <= case[cc]]
    first_area = sp.Rational(1, 2) * (case[cc] - case[aa]) * 2 / (case[bb] - case[aa])
    chk(f'7: при {case} первый кусок держит ≥ ½, и на нём ровно один корень',
        first_area >= sp.Rational(1, 2) and len(on_piece) == 1
        and sp.simplify(A('q7').subs({sp.Symbol('a'): case[aa], sp.Symbol('b'): case[bb],
                                       sp.Symbol('c'): case[cc]}) - on_piece[0]) == 0)

print('\n=== Задание 8: марафон ===')
fa = lambda tt: mpm.mpf(4) / 21 * (1 - mpm.cos(4 * mpm.pi / 9 * (tt - mpm.mpf('2.25'))))
fb = lambda tt: mpm.mpf(4) / 21 * (1 + mpm.cos(mpm.pi / 3 * (tt - mpm.mpf('4.5'))))
half = sp.integrate(sp.Rational(4, 21) * (1 - sp.cos(4 * sp.pi / 9 * (t - sp.Rational(9, 4)))), (t, sp.Rational(9, 4), sp.Rational(9, 2)))
chk('8a(i): ∫ от 2.25 до 4.5 = 3/7 (markscheme)', sp.simplify(half - sp.Rational(3, 7)) == 0 and A('q8ai') == sp.Rational(3, 7))
chk('8a(ii): f′ = 0 при 4.5, и f(4.5) = 8/21 — наибольшее на сетке',
    abs(mpm.diff(fb, mpm.mpf('4.5'))) < 1e-20
    and all(fa(2.25 + 2.25 * i / 400) <= fb(4.5) + 1e-25 for i in range(401))
    and all(fb(4.5 + 3 * i / 400) <= fb(4.5) + 1e-25 for i in range(401)) and A('q8aii') == sp.Float('4.5'))
F8 = lambda q: mpm.quad(fa, [2.25, q]) if q <= 4.5 else mpm.mpf(3) / 7 + mpm.quad(fb, [4.5, q])
median8 = mpm.findroot(lambda q: F8(q) - mpm.mpf('0.5'), 4.7)
chk('8a(iii): P(T < 4.5) = 3/7 < ½, медиана 4.69 больше моды (markscheme)', near(median8, '4.68') and str(A('q8aiii')) == 'median')
chk('8b: P(T ≤ 3.5) = 0.103749 (markscheme)', near(F8(3.5), '0.103749') and agrees(A('q8b'), F8(3.5)))
q8 = mpm.findroot(lambda q: F8(q) - mpm.mpf('0.25'), 4.0)
chk('8d: нижний квартиль 4.01290 (markscheme)', near(q8, '4.01290') and agrees(A('q8d'), q8))

print('\n=== Задание 9: равномерная на [a, 3a] ===')
a9 = sp.symbols('a', positive=True)
E9 = sp.integrate(x / (2 * a9), (x, a9, 3 * a9))
E9sq = sp.integrate(x ** 2 / (2 * a9), (x, a9, 3 * a9))
chk('9a: E(X) = 2a (markscheme)', sp.simplify(E9 - 2 * a9) == 0 and sp.simplify(A('q9a').subs(sp.Symbol('a'), a9) - E9) == 0)
chk('9b: E(X²) = 13a²/3, Var = a²/3 (markscheme)', sp.simplify(E9sq - 13 * a9 ** 2 / 3) == 0
    and sp.simplify(A('q9b').subs(sp.Symbol('a'), a9) - (E9sq - E9 ** 2)) == 0)

print('\n=== Задание 10: 3x·arccos(x²) ===')
k10 = mpm.findroot(lambda kk: kk * kk * mpm.acos(kk * kk) - mpm.sqrt(1 - kk ** 4) + mpm.mpf(1) / 3, 0.7)
f10 = lambda xx: 3 * xx * mpm.acos(xx * xx)
chk('10: k = 0.713250 (markscheme), и площадь до k — единица', near(k10, '0.713250') and abs(mpm.quad(f10, [0, k10]) - 1) < 1e-20)
E10 = mpm.quad(lambda xx: xx * f10(xx), [0, k10])
E10sq = mpm.quad(lambda xx: xx * xx * f10(xx), [0, k10])
V10 = E10sq - E10 ** 2
chk('10c(i): E(X) = 0.456309 (markscheme)', near(E10, '0.456309') and agrees(A('q10ci'), E10))
chk('10c(ii): E(X²) = 0.237198, Var = 0.0289805 (markscheme)', near(E10sq, '0.237198') and near(V10, '0.0289805')
    and agrees(A('q10cii'), V10))
s10 = mpm.sqrt(V10)
P10 = mpm.quad(f10, [E10 - s10, E10 + s10])
# схема печатает верхний предел 0.626549…, точное 0.6265458…: последние
# цифры — от сложения округлённых 0.456309 и 0.170236 не выходят вовсе,
# это опечатка; якорь — пять цифр
chk('10d: σ = 0.170236, пределы 0.28607 и 0.62654, P = 0.620012 (markscheme)',
    near(s10, '0.170236') and near(E10 - s10, '0.28607') and near(E10 + s10, '0.62654') and near(P10, '0.620012')
    and agrees(A('q10d'), P10))

print('\n=== Задание 11: шоколад ===')
f11 = sp.Rational(6, 85) * (4 + 3 * x - x ** 2)
P11 = sp.integrate(f11, (x, sp.Rational(1, 2), 2))
chk('11d: 25x ≤ 18.75 до 0.75 кг, 24x ≤ 48 до 2 кг — промежуток [0.5, 2]', 25 * 0.75 < 48 and 24 * 2 == 48)
chk('11d: P(0.5 ≤ X ≤ 2) = 0.635294 (markscheme)', near(P11, '0.635294') and agrees(A('q11d'), P11))
low = sp.integrate(x * f11, (x, sp.Rational(1, 2), sp.Rational(3, 4)))
high = sp.integrate(x * f11, (x, sp.Rational(3, 4), 3))
chk('11e: ∫x f на кусках — 0.060592 и 1.64345 (markscheme)', near(low, '0.060592') and near(high, '1.64345'))
E11 = 25 * low + 24 * high
chk('11e: 1.51482 + 39.4428 = 40.9576 (markscheme)', near(25 * low, '1.51482') and near(24 * high, '39.4428')
    and near(E11, '40.9576'))
chk('11e: до цента 40.96', f"{float(E11):.2f}" == '40.96' and A('q11e') == sp.Float('40.96'))

print('\n=== Задание 12: прыжки в длину ===')
a12, b12 = sp.symbols('a b')
f12 = a12 * (x - 3) ** 3 + b12 * (x - 3) ** 2
area12 = sp.expand(sp.integrate(f12, (x, 3, 9)))
chk('12a: площадь = 324a + 72b (markscheme)', sp.simplify(area12 - (324 * a12 + 72 * b12)) == 0
    and sp.simplify(A('q12a') - area12) == 0)
sol12 = sp.solve([sp.Eq(area12, 1), sp.Eq(f12.subs(x, 9), 0)], [a12, b12], dict=True)
chk('12b: f(9) = 0 — это 216a + 36b = 0, то есть 6a + b = 0', sp.expand(f12.subs(x, 9) - 36 * (6 * a12 + b12)) == 0)
chk('12b(ii): a = −1/108, b = 1/18 (markscheme)', len(sol12) == 1 and sol12[0] == {a12: sp.Rational(-1, 108), b12: sp.Rational(1, 18)}
    and list(A('q12bii')) == [sp.Rational(-1, 108), sp.Rational(1, 18)])
g12 = f12.subs(sol12[0])
crit = [r for r in sp.solve(sp.diff(g12, x), x) if 3 < r < 9]
chk('12c: единственная вершина внутри — x = 7, f(7) = 0.296296 (markscheme)', crit == [7] and near(g12.subs(x, 7), '0.296296')
    and A('q12c_mode') == 7)
chk('12c: площадь от 3 до 7 = 0.592592 > ½ (markscheme)', near(sp.integrate(g12, (x, 3, 7)), '0.592592'))
G12 = sp.integrate(g12, (x, 3, sp.Symbol('m')))
median12 = sp.nsolve(G12 - sp.Rational(1, 2), sp.Symbol('m'), 6.7)
chk('12c: медиана 6.68563 (markscheme)', near(median12, '6.68563') and agrees(A('q12c_median'), median12))
win = sp.integrate(g12, (x, sp.Rational(852, 100), 9))
over8 = sp.integrate(g12, (x, 8, 9))
chk('12d: 0.03442688 / 0.13194444 = 0.260919 (markscheme)', near(win, '0.03442688') and near(over8, '0.13194444')
    and near(win / over8, '0.260919') and agrees(A('q12d'), win / over8))
rough = f12.subs({a12: sp.Float('-0.00926'), b12: sp.Float('0.0556')})
chk('12d: с a, b до трёх цифр — 0.263, как принимает схема', agrees(sp.integrate(rough, (x, 8.52, 9)) / sp.integrate(rough, (x, 8, 9)), 0.263))

print('\n=== Таймер ===')
anti_t = sp.integrate(6 * x / (sp.pi * sp.sqrt(16 - x ** 2)), x)
Et = sp.simplify(anti_t.subs(x, 2) - anti_t.subs(x, 0))
chk('timer (a): E(X) = 12(2 − √3)/π (markscheme)', sp.simplify(Et - 12 * (2 - sp.sqrt(3)) / sp.pi) == 0
    and sp.simplify(A('qt_a') - Et) == 0)
chk('timer (a): и это 1.02349', near(Et, '1.02349'))
Pt = sp.N(6 / sp.pi * sp.asin(sp.Rational(1, 8)), 20)
chk('timer (b): 6/π·arcsin(1/8) = 0.239358 (markscheme)', near(Pt, '0.239358') and agrees(A('qt_b'), Pt))

BREAK_D6 = {
    'q1e': '0.594',                  # доля времени ниже 1.5, а не выше
    'q2a': '1.65',                   # десятичная дробь на Paper 1
    'q3a': '1/sqrt(16 + k) - 1/sqrt(k)',   # пределы наоборот
    'q3b': '0.65',                   # две значащие цифры
    'q4a': '1/(b*exp(b) - exp(b))',  # потеряно значение на нижнем пределе
    'q4b': '-1.68',                  # корень вне [0, 1]
    'q5a': '7*k**3/3',               # не та первообразная второго куска
    'q5b': '2.55',                   # корень кубического уравнения вне [0, 2k]
    'q6a': '0.393',                  # среднее π/8 вместо медианы
    'q6b': '0.25',                   # вся ширина 2a вместо a
    'q7': 'a - sqrt((b - a)*(c - a)/2)',   # не отброшен корень левее a
    'q8ai': 'Rational(4, 7)',        # вторая половина площади
    'q8aii': '0.381',                # высота f(4.5), а не x
    'q8aiii': "'mode'",              # не та сторона
    'q8b': '0.896',                  # медленные бегуны
    'q8d': '5.41',                   # верхний квартиль
    'q9a': '1',                      # ∫ f вместо ∫ x f
    'q9b': '13*a**2/3',              # E(X²) без вычитания
    'q10ci': '0.254',                # ∫ x dx без плотности
    'q10cii': '0.237',               # E(X²) без вычитания
    'q10d': '0.380',                 # площадь вне промежутка
    'q11d': '0.601',                 # 25x ≤ 48 для всех весов
    'q11e': '41.0',                  # не до цента
    'q12a': '216*a + 36*b',          # f(9), а не площадь
    'q12bii': '[-0.0093, 0.056]',    # две значащие цифры
    'q12c_mode': '0.296',            # высота вершины
    'q12c_median': '10.5',           # корень вне [3, 9]
    'q12d': '0.0344',                # не поделено на условие
    'qt_a': '1.02',                  # десятичная дробь вместо точного
    'qt_b': '0.761',                 # площадь с другой стороны
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
os.chdir(os.path.join(ROOT, 'practicum', 'statistics'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 20)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)
chk('с эталонами ни одного замечания', 'rounded on the way' not in answered
    and 'accepts it' not in answered and 'accepts both' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = BREAK_D6
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

missed, named = [], 0
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}),
                     '<cell>', 'exec'), room)
    rejected = [line for line in buffer.getvalue().split('\n') if line.startswith('❌')]
    if not rejected:
        missed.append(name)
        continue
    generic = ('gives something else', 'does not meet the conditions', 'condition fails',
               'no valid model', 'expression gives something else', 'something else (at')
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
