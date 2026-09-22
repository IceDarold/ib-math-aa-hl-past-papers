"""Независимая проверка каждого ответа практикума E9.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Проверки ноутбука не дифференцируют: скорость они меряют сдвигом времени,
связанную скорость — подталкиванием величин, наибольшее — просмотром
промежутка. Тест поэтому делает ровно обратное — **дифференцирует
символьно**: ускорение — sympy.diff(v, t), связанная скорость — неявное
дифференцирование связи по t (idiff и цепочка вручную), наибольшее —
корни f′ = 0 и сравнение с концами. Там, где ответ точный (30, −3√3/2,
2/3, 15√5/4, e^{−1/2}, N/2, kN/4), он получается sympy в точном виде.

Второй якорь — числа схем: −0.651, 0.591, π, 1.69, 6.12, −4.71, 0.986, e,
−1.84, 1.81, 4π/3, −1.47, 30, 0.0261, −0.724, 5.2, −3√3/2, 2/3, 15√5/4,
e^{−1/2}, 1.01, N/2, kN/4, 81 и 4, 1550 и 7, 9.47·10¹⁵, 425.

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора и
по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_e9.py
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

import build_e9 as gen

res = []
T, X = sp.symbols('t x', real=True)


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    """Эталон из генератора — в пространстве имён ноутбука."""
    import kit
    return eval(gen.ANSWERS[name], dict(vars(kit)))


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 0.5 * 10 ** -places * 1.001


def roots(f, lo, hi, var=T, count=3000):
    """Все корни на отрезке: смена знака на сетке, затем nsolve."""
    fast = sp.lambdify(var, f, 'mpmath')
    out, last, where = [], None, None
    for i in range(count + 1):
        point = lo + (hi - lo) * i / count
        try:
            value = float(fast(point))
        except (ValueError, ZeroDivisionError, TypeError):
            last = where = None
            continue
        if last is not None and last * value < 0:
            out.append(float(sp.nsolve(f, var, (where, point), solver='bisect')))
        last, where = value, point
    return out


print('=== Задача 1: скорость в момент ===')
H = sp.Float('1.63') * sp.sin(sp.Float('0.513') * (T - sp.Float('8.20'))) + sp.Float('2.13')
rate = sp.diff(H, T).subs(T, 13)
chk('схема: H′(13) = −0.651', near(rate, '-0.651'))
chk('эталон 1(a) совпал', near(rate, gen.ANSWERS['q1a']))
v = sp.Float('8.14') * T / sp.sqrt(T ** 2 + sp.Float('0.2'))
moments = roots(sp.diff(v, T) - 4, 0.001, 10)
chk('a = 4 ровно один раз', len(moments) == 1)
chk('схема: t = 0.591', near(moments[0], '0.591'))
chk('эталон 1(b) совпал', near(moments[0], gen.ANSWERS['q1b']))

print('\n=== Задача 2: растения ===')
gap = 8 - sp.diff(sp.sin(2 * T + 6) + 9 * T + 27, T)
cuts = roots(gap, 0, 9)
total = sum(b - a for a, b in zip(cuts[::2], cuts[1::2]))
chk('три куска', len(cuts) == 6)
chk('каждый длиной π/3', all(abs((b - a) - float(sp.pi) / 3) < 1e-9
                             for a, b in zip(cuts[::2], cuts[1::2])))
chk('всего π', abs(total - float(sp.pi)) < 1e-9)
chk('эталон совпал', near(total, gen.ANSWERS['q2']))

print('\n=== Задача 3: разворот и рост перемещения ===')
v3 = 2 * sp.sin(T / 2) + sp.Rational(3, 10) * T - 2
zeros = roots(v3, 0, 10)
chk('схема: 1.69 и 6.12', near(zeros[0], '1.69') and near(zeros[1], '6.12'))
chk('между ними v > 0', v3.subs(T, 4) > 0)
chk('эталон (a)', near(zeros[0], gen.ANSWERS['q3a']))
chk('эталон (b)', near(A('q3b').start, '1.69') and near(A('q3b').end, '6.12'))

print('\n=== Задача 4: ускорение при развороте ===')
v4 = sp.exp(sp.sin(T)) + 4 * sp.sin(T)
zeros = roots(v4, 0, 6)
chk('разворот один', len(zeros) == 1)
chk('схема: a = −4.71', near(sp.diff(v4, T).subs(T, zeros[0]), '-4.71'))
v4b = sp.exp(-sp.sin(T)) * sp.cos(2 * T)
second = sp.solve(sp.cos(2 * T), T)
second = sorted(r for r in sp.solveset(sp.cos(2 * T), T, sp.Interval(0, 5)))[1]
chk('второй разворот — 3π/4', second == 3 * sp.pi / 4)
exact = sp.simplify(sp.diff(v4b, T).subs(T, second))
chk('a = 2e^{−1/√2} точно', sp.simplify(exact - 2 * sp.exp(-1 / sp.sqrt(2))) == 0)
chk('эталоны 4', near(A('q4a'), '-4.71') and near(exact, gen.ANSWERS['q4b']))

print('\n=== Задача 5: наибольший модуль скорости ===')
turning = roots(sp.diff(v4b, T), 0, 5)
candidates = [abs(float(v4b.subs(T, p))) for p in turning + [0, 5]]
chk('схема: e', near(max(candidates), '2.72') and abs(max(candidates) - float(sp.E)) < 1e-9)
v5 = (T ** 2 + 1) * sp.cos(T) / 4
turning = roots(sp.diff(v5, T), 0, 3)
speeds = {p: abs(float(v5.subs(T, p))) for p in turning + [0, 3]}
chk('модуль скорости больше всего на конце t = 3', max(speeds, key=speeds.get) == 3)
chk('схема: a(3) = −1.84', near(sp.diff(v5, T).subs(T, 3), '-1.84'))
chk('эталоны 5', near(A('q5a'), '2.72') and near(A('q5b'), '-1.84'))

print('\n=== Задача 6: частица по перемещению ===')
s6 = 2 ** (1 - T / 5) * sp.sin(2 * sp.pi * T / 3)
flat = roots(sp.diff(s6, T), 0, 30)
values = [float(s6.subs(T, p)) for p in flat]
chk('схема: наибольшее 1.81', near(max(values), '1.81'))
chk('схема: наименьшее −1.47', near(min(values), '-1.47'))
v6 = sp.diff(s6, T)
inner = [float(v6.subs(T, p)) for p in roots(sp.diff(v6, T), 0, 30)]
chk('v(0) = 4π/3 точно', sp.simplify(v6.subs(T, 0) - 4 * sp.pi / 3) == 0)
chk('и больше любой вершины v внутри', float(4 * sp.pi / 3) > max(inner))
chk('эталоны 6', near(A('q6a'), '1.81') and near(A('q6b'), '4.19') and near(A('q6c'), '-1.47'))

print('\n=== Задача 7: равносторонний треугольник ===')
side = sp.Function('s')(T)
area = sp.sqrt(3) / 4 * side ** 2
rate7 = sp.diff(area, T).subs(sp.Derivative(side, T), 4).subs(side, 5 * sp.sqrt(3))
chk('dA/dt = 30 точно', sp.simplify(rate7) == 30)
chk('эталон 7', A('q7') == 30)

print('\n=== Задача 8: колба ===')
Hh = sp.Symbol('h', positive=True)
Vh = 5 * sp.pi * Hh ** 2 - sp.pi * Hh ** 3 / 3
states = [r for r in sp.Poly(Vh - 200, Hh).nroots() if abs(sp.im(r)) < 1e-12]
inside = [sp.re(r) for r in states if 0 < sp.re(r) < 10]
chk('в колбе ровно одно состояние', len(inside) == 1)
chk('схема: h = 4.21', near(inside[0], '4.21'))
rate8 = 2 / sp.diff(Vh, Hh).subs(Hh, inside[0])
chk('схема: dh/dt = 0.0261', near(rate8, '0.0261'))
chk('эталон 8', near(rate8, gen.ANSWERS['q8']))

print('\n=== Задача 9: треугольник и угол ===')
theta = sp.Function('theta')(T)
length = sp.sqrt(625 - 600 * sp.cos(theta))
rate9 = sp.diff(length, T).subs(sp.Derivative(theta, T), -sp.pi / 60)
rate9 = rate9.subs(theta, sp.asin(sp.Rational(14, 15)))
chk('sin θ = 14/15 даёт площадь 140', sp.Rational(1, 2) * 15 * 20 * sp.Rational(14, 15) == 140)
chk('схема: −0.724', near(sp.N(rate9), '-0.724'))
chk('эталон 9', near(sp.N(rate9), gen.ANSWERS['q9']))

print('\n=== Задача 10: лодки ===')
xb, th = sp.Function('x')(T), sp.Function('theta')(T)
yb = xb + 50 * sp.cot(th)
dx = sp.Symbol('dx')
equation = sp.Eq(sp.diff(yb, T).subs(sp.Derivative(xb, T), dx)
                 .subs(sp.Derivative(th, T), sp.Rational(-1, 10)), 2 * dx)
speed = sp.solve(equation, dx)[0].subs(th, sp.acot(sp.Rational(1, 5)))
chk('скорость лодки A = 26/5 точно', sp.simplify(speed) == sp.Rational(26, 5))
chk('от x ответ не зависит', not sp.simplify(speed).free_symbols)
chk('эталон 10', near(speed, gen.ANSWERS['q10']))

print('\n=== Задача 11: оптимум модели ===')
area11 = (X + 3) * sp.sqrt(9 - X ** 2)
flat = sp.solve(sp.diff(area11, X), X)
chk('dA/dx = 0 только при x = 3/2 (x = −3 — концевая точка)',
    [p for p in flat if 0 < p < 3] == [sp.Rational(3, 2)])
chk('y_R = −3√3/2', sp.simplify(A('q11a') + sp.sqrt(9 - sp.Rational(9, 4))) == 0)
th2 = sp.Symbol('theta', positive=True)
T11 = 500 * sp.sec(th2) + (2500 - 1000 * sp.tan(th2)) / 3
chk('dT/dθ = 0 при sin θ = 2/3', sp.simplify(sp.diff(T11, th2).subs(th2, sp.asin(sp.Rational(2, 3)))) == 0)
chk('и PX = 160√5', sp.simplify(400 * sp.tan(sp.asin(sp.Rational(2, 3))) - 160 * sp.sqrt(5)) == 0)
al = sp.Symbol('alpha', positive=True)
L = sp.Rational(3, 4) * sp.sec(al) + 6 * sp.csc(al)
chk('dL/dα = 0 при α = arctan 2', sp.simplify(sp.diff(L, al).subs(al, sp.atan(2))) == 0)
chk('d²L/dα² > 0 там', sp.N(sp.diff(L, al, 2).subs(al, sp.atan(2))) > 0)
chk('L_min = 15√5/4', sp.simplify(L.subs(al, sp.atan(2)) - 15 * sp.sqrt(5) / 4) == 0)
chk('шест 11.25 длиннее: no', sp.Rational(45, 4) > 15 * sp.sqrt(5) / 4 and A('q11d') == 'no')
chk('эталоны 11', A('q11b') == sp.Rational(2, 3) and A('q11c') == 15 * sp.sqrt(5) / 4)

print('\n=== Задача 12: расстояние ===')
Xp = sp.Symbol('x', positive=True)
flat = sp.solve(sp.diff(Xp ** 2 * sp.log(Xp) + 4, Xp), Xp)
chk('x = e^{−1/2}', flat == [sp.exp(-sp.Rational(1, 2))] and A('q12a') == flat[0])
gapv = sp.Matrix([1, 0, 12]) + T * sp.Matrix([4, 2, -2]) - sp.Matrix([19, -1, 1]) \
    - T * sp.Matrix([-6, 2, 4])
square = sp.expand(gapv.dot(gapv))
when = sp.solve(sp.diff(square, T), T)[0]
chk('D² = 136t² − 492t + 446', square == 136 * T ** 2 - 492 * T + 446)
chk('t = 123/68 внутри [0, 2.5]', when == sp.Rational(123, 68))
chk('D_min = √1190/34 ≈ 1.01', sp.simplify(sp.sqrt(square.subs(T, when)) - sp.sqrt(1190) / 34) == 0
    and near(sp.sqrt(1190) / 34, gen.ANSWERS['q12b']))

print('\n=== Задача 13: логистика ===')
Pp = sp.Symbol('P')
kk, NN = sp.symbols('k N', positive=True)
growth = kk * Pp * (1 - Pp / NN)
vertex = sp.solve(sp.diff(growth, Pp), Pp)
chk('вершина dP/dt — P = N/2', vertex == [NN / 2])
second = sp.factor(sp.diff(growth, Pp) * growth)          # d²P/dt² = g′(P)·g(P)
chk('d²P/dt² = 0 при P = 0, N/2, N', set(sp.solve(second, Pp)) == {0, NN / 2, NN})
chk('наибольшее dP/dt = kN/4', sp.simplify(growth.subs(Pp, NN / 2) - kk * NN / 4) == 0)
chk('эталоны 13', sp.simplify(A('q13c') - sp.Symbol('N') / 2) == 0
    and sp.simplify(A('q13d') - sp.Symbol('k') * sp.Symbol('N') / 4) == 0)

print('\n=== Задача 14: наилучшее целое ===')
table12 = {n: sp.Rational(12, n) ** n for n in range(1, 13)}
chk('P(12) = 81 при n = 4', max(table12.values()) == 81 and max(table12, key=table12.get) == 4)
table20 = {n: float(sp.Rational(20, n) ** n) for n in range(1, 21)}
best20 = max(table20, key=table20.get)
chk('P(20) при n = 7, 1554.26', best20 == 7 and near(table20[7], '1554.26'))
table100 = {n: sp.Rational(100, n) ** n for n in (36, 37)}
chk('37 лучше 36', table100[37] > table100[36])
chk('9.47 × 10¹⁵', near(float(table100[37]) / 1e15, '9.47'))
chk('а вершина дала бы 9.48 × 10¹⁵', near(float(sp.exp(100 / sp.E)) / 1e15, '9.48'))
chk('эталоны 14', A('q14f') == (81, 4) and A('q14g') == (1550, 7))

print('\n=== Таймер: самолёт ===')
angle = sp.atan((X + 2) / 6) - sp.atan(X / 6)
place = sp.nsolve(angle - sp.Float('0.178'), X, 4.6)
turn = sp.diff(angle, X).subs(X, place)
chk('схема: x = 4.63', near(place, '4.63'))
chk('схема: скорость 425', near(abs(sp.Float('12.5') / turn), '425'))
chk('эталон таймера', A('qt') == 425)

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: пустой и с эталонами ===')
BREAK_E9 = {
    # 1(a): высота вместо её скорости
    'q1a': '3.15',
    # 1(b): момент, когда скорость равна 4, а не ускорение
    'q1b': '0.252',
    # 2: время, когда быстрее растёт A
    'q2': '5.86',
    # 3(a): второй разворот
    'q3a': '6.12',
    # 3(b): где растёт скорость
    'q3b': 'Interval(0, 3.87)',
    # 4(a): скорость в момент разворота
    'q4a': '0',
    # 4(b): первый разворот вместо второго
    'q4b': '-0.986',
    # 5(a): модуль скорости со знаком
    'q5a': '-2.72',
    # 5(b): ускорение в вершине графика v
    'q5b': '0',
    # 6(a)(i): момент вместо значения
    'q6a': '0.718',
    # 6(a)(ii): вершина v внутри, а не начало
    'q6b': '2.79',
    # 6(b): наибольшее вместо наименьшего
    'q6c': '1.81',
    # 7: десятичная запись на бумаге без калькулятора
    'q7': '30.1',
    # 8: dh/dV без dV/dt
    'q8': '0.0131',
    # 9: без знака
    'q9': '0.724',
    # 10: dx/dθ-путаница — скорость со знаком
    'q10': '-5.2',
    # 11(a): это Q, а не R
    'q11a': '3*sqrt(3)/2',
    # 11(b): сам угол вместо sin θ
    'q11b': 'asin(Rational(2, 3))',
    # 11(c): место вместо значения
    'q11c': 'atan(2)',
    'q11d': "'yes'",
    # 12(a): значение вместо места
    'q12a': 'sqrt(4 - exp(-1)/2)',
    # 12(b): D² вместо D
    'q12b': '1.03',
    # 13(c): другой ноль d²P/dt², край области
    'q13c': 'N',
    # 13(d): место вершины вместо значения
    'q13d': 'N/2',
    # 14: вершина вместо целого
    'q14f': '(82.6, 4.41)',
    'q14g': '(1570, 7.36)',
    'q14j': '9.48*10**15',
    # таймер: скорость со знаком
    'qt': '-425',
}

with open(gen.NOTEBOOK) as fh:
    notebook = json.load(fh)
notebook_cells = [''.join(cell['source']) for cell in notebook['cells']
                  if cell['cell_type'] == 'code']

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
os.chdir(os.path.join(ROOT, 'practicum', 'calculus'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 28)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
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
chk('у каждого эталона есть типовая ошибка', set(BREAK_E9) == set(gen.ANSWERS))

generic = ('is something else', 'is not true', 'does not hold', 'value is elsewhere',
           'the number is something else', 'only something no longer')
missed, named = [], 0
for name, wrong in sorted(BREAK_E9.items()):
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
chk(f'все {len(BREAK_E9)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
print(f'   названы по имени {named} из {len(BREAK_E9)}')
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
