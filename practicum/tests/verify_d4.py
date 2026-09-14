"""Независимая проверка каждого ответа практикума D4.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **не решать таблицу так, как её решает
ноутбук**. Ноутбук ищет буквы базисом Грёбнера и численными корнями
многочлена, среднее и дисперсию складывает sympy, ряд первого успеха
суммирует символьно, производящую функцию строит из таблицы.

Тест идёт другими путями. Таблицы — точными дробями модуля fractions,
без sympy. Системы — формулами, выписанными руками, и mpmath.findroot
от разных начальных точек. Ряд Σ x·p(1 − p)^(x − 1) — частичной суммой
из трёх тысяч членов, а не символьной. Линейное преобразование — формулами
a·E(T) + b и a²·Var(T), которых в проверке ноутбука нет вовсе: там T
заменена двумя значениями. Производящие функции — перемножением списков
коэффициентов и перебором исходов опыта заново.

Второй якорь — числа схем оценивания: 0.552839…, 370.356…, 1.18749…,
3.79170…, 59/30.

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_d4.py
"""
import contextlib
import io
import itertools
import json
import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import mpmath as mp
import sympy as sp

import build_d4 as gen

mp.mp.dps = 30
res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name])


def sig3(value):
    return f"{float(value):.3g}"


def agrees(answer, exact):
    return sig3(answer) == sig3(exact)


def mean(table):
    return sum(F(x) * P for x, P in table.items())


def variance(table):
    m = mean(table)
    return sum((F(x) - m) ** 2 * P for x, P in table.items())


def fr(text):
    return F(text)


print('=== Задание 1: супермаркет ===')
a1 = (1 - fr('0.281') - fr('0.026')) / fr('4.5')
chk('1a: 4.5a = 0.693, a = 0.154 (markscheme)', a1 == fr('0.154'))
chk('1a: ответ', agrees(A('q1a'), a1))
visits = {1: fr('1.5') * a1, 2: 2 * a1, 3: fr('0.281'), 4: a1, 5: fr('0.026')}
chk('1: таблица складывается в единицу', sum(visits.values()) == 1)
chk('1a(ii): мода 2', max(visits, key=visits.get) == 2 == A('q1m'))
chk('1b: среднее 2.436 (markscheme)', mean(visits) == fr('2.436'))
chk('1b: ответ', agrees(A('q1b'), mean(visits)))

print('\n=== Задание 2: квадратное уравнение на k ===')
k = sp.Symbol('k')
chk('2a: ответ — то же уравнение, что даёт сумма таблицы',
    sp.simplify(sp.nsimplify(A('q2a').lhs - A('q2a').rhs)
                + (sp.nsimplify(0.41 + (k - 0.28) + 0.46 + (0.29 - 2 * k ** 2)) - 1)) == 0)
roots = sorted(float(r) for r in sp.solve(2 * k ** 2 - k + sp.Rational(12, 100), k))
chk('2b: корни 0.2 и 0.3', roots == [0.2, 0.3])
chk('2b: при 0.2 клетка k − 0.28 отрицательна, при 0.3 все клетки годны',
    0.2 - 0.28 < 0 and all(0 <= c <= 1 for c in (0.41, 0.02, 0.46, 0.29 - 2 * 0.09)))
chk('2b: ответ', agrees(A('q2b'), F(3, 10)))
table2 = {0: fr('0.41'), 1: fr('0.02'), 2: fr('0.46'), 3: fr('0.11')}
chk('2c: E(X) = 1.27 (markscheme)', mean(table2) == fr('1.27') and agrees(A('q2c'), mean(table2)))

print('\n=== Задание 3: карусель ===')
freq = {0: 6, 1: 16, 2: 13, 3: 2, 4: 3}
n3 = sum(freq.values())
chk('3a(i): 34/40 (markscheme)', F(n3 - freq[0], n3) == F(34, 40) and agrees(A('q3p'), F(34, 40)))
chk('3a(ii): 60/40 = 1.5 (markscheme)', F(sum(x * f for x, f in freq.items()), n3) == F(3, 2)
    and agrees(A('q3e'), 1.5))
chk('3b: 1000·1.5/10 = 150 (markscheme)', A('q3r') == 150 == 1000 * F(3, 2) / 10)

print('\n=== Задание 4: p и q из среднего ===')
# p + q = 0.6 и p + 3q = 1 — определитель системы и решение по Крамеру
det = 1 * 3 - 1 * 1
p4 = (fr('0.6') * 3 - 1 * 1) / det
q4 = (1 * 1 - 1 * fr('0.6')) / det
chk('4: по Крамеру p = 0.4, q = 0.2', (p4, q4) == (fr('0.4'), fr('0.2')))
chk('4: ответ', [float(v) for v in A('q4')] == [0.4, 0.2])
chk('4: уравнения ответа выполняются при этих p, q',
    all(abs(float((eq.lhs - eq.rhs).subs({'p': 0.4, 'q': 0.2}))) < 1e-12
        for eq in (A('q4sum'), A('q4mean'))))
chk('4: E(X) = 2 при них', mean({1: p4, 2: fr('0.3'), 3: q4, 4: fr('0.1')}) == 2)

print('\n=== Задание 5: кубическое ===')
found = set()
for start in (-2, -1, 0.3, 1, 2):
    try:
        root = mp.findroot(lambda kk: kk ** 3 - kk ** 2 - 2 * kk + mp.mpf('0.7'), start)
        if not any(abs(float(root) - seen) < 1e-9 for seen in found):
            found.add(float(root))
    except (ValueError, ZeroDivisionError):
        pass
chk('5: у кубического три корня: 0.315870, −1.18538, 1.86951 (markscheme)',
    len(found) == 3 and all(abs(a - b) < 1e-5 for a, b in
                            zip(sorted(found), [-1.18538, 0.315870, 1.86951])))
k5 = mp.findroot(lambda kk: kk ** 3 - kk ** 2 - 2 * kk + mp.mpf('0.7'), 0.3)
a5 = 1 - k5 - k5 ** 2 - k5 ** 3
chk('5: a = 0.552839 (markscheme)', abs(a5 - mp.mpf('0.552839')) < 1e-6)
chk('5: и E(X) при нём 2.3', abs(k5 + 2 * k5 ** 2 + 3 * a5 + 4 * k5 ** 3 - mp.mpf('2.3')) < 1e-20)
chk('5: ответ', agrees(A('q5'), a5))
others = [1 - r - r ** 2 - r ** 3 for r in (-1.185382, 1.869512)]
chk('5: другие корни дают a = 2.44587 и −10.8987 — оговорка схемы',
    abs(others[0] - 2.44587) < 1e-4 and abs(others[1] + 10.8987) < 1e-3)

print('\n=== Задание 6: две кости ===')
p6 = F(1) / (3 + F(1, 2))
chk('6a: p = 2/7', p6 == F(2, 7) and A('q6a') == sp.Rational(2, 7))
X6 = {1: p6, 2: p6, 3: p6, 4: p6 / 2}
chk('6b: E(X) = 16/7 (markscheme)', mean(X6) == F(16, 7) and A('q6b') == sp.Rational(16, 7))
chk('6c(i): r ∈ [0, 1]', A('q6r') == sp.Interval(0, 1))
chk('6c(ii): q = (1 − r)/3 при r от 0 до 1 — [0, 1/3]',
    A('q6q') == sp.Interval(sp.Rational(1 - 1, 3), sp.Rational(1 - 0, 3)))
ends = [mean({1: q, 2: q, 3: q, 4: 1 - 3 * q}) for q in (F(0), F(1, 3))]
chk('6d: E(Y) = 4 − 6q, концы 4 и 2 (markscheme)', sorted(ends) == [2, 4] and A('q6d') == sp.Interval(2, 4))


def less(q, r):
    Y = {1: q, 2: q, 3: q, 4: r}
    return sum(X6[x] * Y[y] for x in X6 for y in Y if x < y)


# два линейных уравнения: 6/7(q + r) = 1/2 и 3q + r = 1
q6 = (1 - F(7, 12)) / 2
r6 = F(7, 12) - q6
chk('6e: q = 5/24, r = 3/8 (markscheme)', (q6, r6) == (F(5, 24), F(3, 8)))
chk('6e: и перебор пар даёт P(X < Y) = 1/2', less(q6, r6) == F(1, 2))
chk('6e: ответ q, r', [A('q6qr')[0], A('q6qr')[1]] == [sp.Rational(5, 24), sp.Rational(3, 8)])
chk('6e: E(Y) = 11/4 (markscheme)', mean({1: q6, 2: q6, 3: q6, 4: r6}) == F(11, 4)
    and A('q6e') == sp.Rational(11, 4))

print('\n=== Задание 7: Var(2 − X) ===')
bounds = [F(6, 10) / 2, F(4, 10)]        # 0.6 − 2a ≥ 0 и 0.4 − a ≥ 0; 3a ≥ 0 даёт 0
chk('7a: 0 ≤ a ≤ 0.3', min(bounds) == F(3, 10) and sp.nsimplify(A('q7a').end) == sp.Rational(3, 10)
    and A('q7a').start == 0 and not A('q7a').left_open and not A('q7a').right_open)
X7 = {1: F(2, 10), 2: F(6, 10), 3: F(2, 10)}
Y7 = {2 - x: P for x, P in X7.items()}
chk('7b: E(X²) = 4.4 (markscheme)', sum(x * x * P for x, P in X7.items()) == F(44, 10))
chk('7b: Var(2 − X) по таблице самой 2 − X = 0.4 — второй метод схемы', variance(Y7) == F(2, 5))
chk('7b: ответ', agrees(A('q7b'), 0.4))

print('\n=== Задание 8: викторина ===')


def quiz(p, q):
    return {20: F(12, 20 + q), 35: F(q, 20 + q), p: F(8, 20 + q)}


found8 = [(p, q) for p in range(1, 200) for q in range(1, 400)
          if mean(quiz(p, q)) == 31 and variance(quiz(p, q)) == 124]
chk('8: перебором целых положительных — единственная пара (45, 5)', found8 == [(45, 5)])
chk('8: вторая пара системы (−10, 115) — из оговорки схемы — не положительна',
    8 * (-10) + 4 * 115 == 380 and 115 == 95 - 2 * (-10))
chk('8: ответ', [int(v) for v in A('q8')] == [45, 5])

print('\n=== Задание 9: марафон ===')
b9 = F(50) / (fr('4.723') - fr('2.25'))
a9 = 150 + fr('2.25') * b9
chk('9e: b = 20.2183, a = 195.491 (markscheme)',
    abs(float(b9) - 20.2183) < 1e-4 and abs(float(a9) - 195.491) < 1e-3)
chk('9e: ответ до целого', [int(v) for v in A('q9ab')] == [round(a9), round(b9)] == [195, 20])
var9 = b9 ** 2 * fr('0.906')
chk('9f: Var(P) = b²·Var(T) = 370.356 (markscheme)', abs(float(var9) - 370.356) < 1e-3)
chk('9f: ответ', agrees(A('q9v'), var9))
chk('9f: с b = 20 выходит 362.4 — нижний край допуска схемы', 400 * fr('0.906') == fr('362.4'))

print('\n=== Задание 10: первое усиление ===')


# Частичная сумма до трёх тысяч членов. mpmath.nsum здесь не годится:
# его ускорение сходимости на (x − m)²·p(1 − p)^(x − 1) при p = 0,1 даёт
# 23,75 вместо 90 — тест поймал это раньше, чем ноутбук.
TERMS = 3000


def geo_mean(p):
    return mp.fsum(x * p * (1 - p) ** (x - 1) for x in range(1, TERMS))


def geo_var(p):
    m = geo_mean(p)
    return mp.fsum((x - m) ** 2 * p * (1 - p) ** (x - 1) for x in range(1, TERMS))


xs, ps = sp.symbols('x p')
for p in (mp.mpf('0.15'), mp.mpf('0.55')):
    chk(f'10b(ii): сумма ответа при p = {p} равна численной сумме ряда',
        abs(float(A('q10b').subs(ps, sp.Float(str(p))).evalf()) - float(geo_mean(p))) < 1e-9)
chk('10c(ii): ряд при p = 0.3 равен 1/p', abs(geo_mean(mp.mpf('0.3')) - 1 / mp.mpf('0.3')) < 1e-20)
chk('10d: E = 10, Var = 90 (markscheme)',
    abs(geo_mean(mp.mpf('0.1')) - 10) < 1e-20 and abs(geo_var(mp.mpf('0.1')) - 90) < 1e-12
    and A('q10m') == 10 and A('q10v') == 90)
# вторая модель: вероятность усиления 0.2, 0.4, 0.6, 0.8, 1 — таблица из опыта заново
Y10, alive = {}, F(1)
for y in range(1, 6):
    boost = F(y, 5)
    Y10[y] = alive * boost
    alive *= 1 - boost
chk('10g(i): таблица второй модели из опыта — 0.2, 0.32, 0.288, 0.1536, 0.0384',
    [Y10[y] for y in range(1, 6)] == [fr('0.2'), fr('0.32'), fr('0.288'), fr('0.1536'), fr('0.0384')])
chk('10g(ii): E(Y) = 2.5104', mean(Y10) == fr('2.5104') and A('q10ey') == sp.Float('2.5104'))
chk('10g(iii): Var(Y) = 1.18749 (markscheme)', abs(float(variance(Y10)) - 1.18749) < 1e-5
    and agrees(A('q10vy'), variance(Y10)))
p10 = mp.findroot(lambda p: geo_mean(p) - mp.mpf('2.5104'), 0.4)
chk('10h(i): p = 0.398342 (markscheme)', abs(p10 - mp.mpf('0.398342')) < 1e-6 and agrees(A('q10p'), p10))
chk('10h(ii): Var(X) = 3.79170 (markscheme)', abs(geo_var(p10) - mp.mpf('3.79170')) < 1e-5
    and agrees(A('q10vx'), geo_var(p10)))
chk('10h(ii): с p = 0.398 выходит 3.80040 — оговорка схемы',
    abs(geo_var(mp.mpf('0.398')) - mp.mpf('3.80040')) < 1e-5)
chk('10h(iii): Var(Y) < Var(X)', float(variance(Y10)) < float(geo_var(p10)))

print('\n=== Задание 11: производящие функции ===')
M11 = {}
for i, j in itertools.product(range(1, 5), repeat=2):
    M11[max(i, j)] = M11.get(max(i, j), 0) + F(1, 16)
chk('11: максимум двух костей — 1/16, 3/16, 5/16, 7/16', [M11[m] for m in range(1, 5)]
    == [F(1, 16), F(3, 16), F(5, 16), F(7, 16)])
chk('11a: E(M) = 25/8 (markscheme)', mean(M11) == F(25, 8) and A('q11a') == sp.Float('3.125'))
tt = sp.Symbol('t')
chk("11c(i): G'(t) — коэффициенты m·P(M = m) при t^(m−1)",
    [A('q11g').coeff(tt, m - 1) for m in range(1, 5)] == [sp.Rational(m * M11[m].numerator, M11[m].denominator)
                                                       for m in range(1, 5)])
chk("11c(ii): G'(1) = 50/16", A('q11c') == sp.Float('3.125'))
X11 = {}
for first, second in itertools.permutations(range(5), 2):
    red = ('RRYYY'[first] == 'R') + ('RRYYY'[second] == 'R')
    X11[red] = X11.get(red, 0) + F(1, 20)
chk('11d: сочетаниями C(2,x)C(3,2−x)/C(5,2) — то же, что перебор',
    all(X11[x] == F(sp.binomial(2, x) * sp.binomial(3, 2 - x), sp.binomial(5, 2)) for x in range(3)))
chk('11d: ответ — 3/10, 3/5, 1/10', [A('q11d').coeff(tt, x) for x in range(3)]
    == [sp.Rational(X11[x].numerator, X11[x].denominator) for x in range(3)])
p11 = F(1, 3) * 2
chk('11e(i): ½p = 1/3, p = 2/3', A('q11p') == sp.Rational(2, 3) and p11 == F(2, 3))
coin, bias = [F(1, 2), F(1, 2)], [1 - p11, p11]
GY = [sum(coin[i] * bias[n - i] for i in range(2) if 0 <= n - i < 2) for n in range(3)]
chk('11e(ii): перемножение списков — 1/6, 1/2, 1/3 (markscheme)', GY == [F(1, 6), F(1, 2), F(1, 3)]
    and [A('q11y').coeff(tt, n) for n in range(3)] == [sp.Rational(1, 6), sp.Rational(1, 2), sp.Rational(1, 3)])
GX = [X11[x] for x in range(3)]
GZ = [sum(GX[i] * GY[n - i] for i in range(3) if 0 <= n - i < 3) for n in range(5)]
chk('11f: G_Z = 1/20 + 1/4 t + 5/12 t² + 1/4 t³ + 1/30 t⁴ (markscheme)',
    GZ == [F(1, 20), F(1, 4), F(5, 12), F(1, 4), F(1, 30)])
chk("11f: G_Z'(1) = 59/30 (markscheme)", sum(n * c for n, c in enumerate(GZ)) == F(59, 30)
    and agrees(A('q11z'), F(59, 30)))

print('\n=== Таймер: кубик Клэр ===')
found_t = [(p, q) for p in range(17) for q in range(17)
           if p + q + 9 == 16 and p + 2 * q + 12 + 8 + 18 == 48]
chk('timer (a): перебором — только (4, 3) (markscheme)', found_t == [(4, 3)]
    and [int(v) for v in A('qt_pq')] == [4, 3])
chk('timer (b): 10·3 = 30', A('qt_b') == 30)

BREAK_D4 = {
    'q1a': '0.198',                  # сумма без одной клетки
    'q1m': '0.308',                  # наибольшая вероятность вместо значения
    'q1b': '3.5',                    # среднее значений без весов
    'q2a': 'Eq(2*k**2 - k + 0.88, 0)',   # левая часть без единицы
    'q2b': '0.2',                    # корень, при котором P(X = 1) < 0
    'q2c': '1.5',                    # среднее значений без весов
    'q3p': '0.45',                   # «хотя бы раз» взято как больше одного
    'q3e': '2',                      # среднее значений без весов
    'q3r': '15',                     # забыли тысячу посетителей
    'q4sum': 'Eq(p + q, 0.4)',       # вычли 0.3 + 0.1 не из единицы
    'q4mean': 'Eq(p + 3*q, 2)',      # не перенесли 0.6 + 0.4
    'q4': '[0.2, 0.4]',              # p и q местами
    'q5': '2.44587',                 # корень с отрицательной клеткой
    'q6a': 'Rational(1, 4)',         # клетка ½p взята как p
    'q6b': 'Rational(5, 2)',         # среднее значений без весов
    'q6r': 'Interval.open(0, 1)',    # концы выколоты
    'q6q': 'Interval(0, 1)',         # клетка без суммы
    'q6d': 'Interval(1, 4)',         # не тот диапазон
    'q6qr': '[Rational(3, 8), Rational(5, 24)]',   # q и r местами
    'q6e': 'Rational(5, 2)',         # среднее значений без весов
    'q7a': 'Interval(0, 0.4)',       # граница по третьей клетке, а не по первой
    'q7b': '4.4',                    # E(X²) без вычитания
    'q8': '[-10, 115]',              # второе решение системы
    'q9ab': '[195.491, 20.2183]',    # не округлено до целого
    'q9v': '18.3',                   # b не возведено в квадрат
    'q10b': 'Sum(p*(1 - p)**(x - 1), (x, 1, oo))',   # без множителя x
    'q10m': '9',                     # не то среднее
    'q10v': '9.49',                  # стандартное отклонение
    'q10ey': '3',                    # среднее значений без весов
    'q10vy': '7.4896',               # E(Y²) без вычитания
    'q10p': '0.4',                   # две значащие цифры
    'q10vx': '1.19',                 # дисперсия другой модели
    'q11a': '2.5',                   # среднее значений без весов
    'q11g': 'Rational(1, 16) + Rational(3, 16)*t + Rational(5, 16)*t**2 + Rational(7, 16)*t**3',  # степени сдвинуты, множители потеряны
    'q11c': '1',                     # G(1) вместо G'(1)
    'q11d': 'Rational(1, 10) + Rational(3, 5)*t + Rational(3, 10)*t**2',   # посчитаны жёлтые
    'q11p': 'Rational(1, 3)',        # вероятность орла вместо решки
    'q11y': 'Rational(1, 3) + t/2 + t**2/6',   # коэффициенты в обратном порядке
    'q11z': '2.57',                  # не то среднее
    'qt_pq': '[3, 4]',               # p и q местами
    'qt_b': '3',                     # множитель потерян
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
chk('с эталонами ни одного замечания об округлении', 'rounded on the way' not in answered and 'rounded to three' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = BREAK_D4
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

missed = []
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}),
                     '<cell>', 'exec'), room)
    if not [line for line in buffer.getvalue().split('\n')
            if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
