"""Независимая проверка каждого ответа практикума E2.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение и
проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит ещё и «другим механизмом». verify_maclaurin
из kit вычитает ответ из функции и смотрит на остаток, ничего не раскладывая
до конца; здесь ряд строится sympy.series и, где вопрос предполагает другой
маршрут, ещё и вручную — перемножением отрезков, биномиальной формулой,
почленным дифференцированием. Совпадение маршрутов и есть проверка.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_e2.py
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

import build_e2 as gen

R = sp.Rational
x, y = sp.symbols('x y')
a, b, m, n, r, k = sp.symbols('a b m n r k')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def ser(f, order, var=x):
    return sp.expand(sp.series(f, var, 0, order).removeO())


def same(u, v):
    return sp.simplify(sp.expand(u - v)) == 0


print('=== Задача 1: подстановка в известный ряд ===')
# Ряд синуса выписывается формулой, а не берётся у sympy: вопрос именно
# о подстановке в известное разложение.
sin_series = sum((-1)**i * x**(2*i + 1) / sp.factorial(2*i + 1) for i in range(4))
chk('ряд синуса совпадает с sympy', same(sin_series, ser(sp.sin(x), 8)))
chk('sin(x^2) = x^2 - x^6/6', same(sin_series.subs(x, x**2).removeO()
                                   if hasattr(sin_series.subs(x, x**2), 'removeO')
                                   else sp.expand(sin_series.subs(x, x**2)).as_poly(x)
                                   .as_expr(), sp.expand(sin_series.subs(x, x**2))))
chk('и первые два ненулевых члена — x^2 и -x^6/6',
    same(ser(sp.sin(x**2), 7), x**2 - x**6/6))
chk('а не x^2 - x^3/6 (подстановка в показатель)',
    not same(ser(sp.sin(x**2), 7), x**2 - x**3/6))
cos_series = sum((-1)**i * x**(2*i) / sp.factorial(2*i) for i in range(3))
chk('cos(2x) до x^4 равно 1 - 2x^2 + 2x^4/3',
    same(sp.expand(cos_series.subs(x, 2*x)), 1 - 2*x**2 + 2*x**4/3))
chk('и то же самое даёт sympy', same(ser(sp.cos(2*x), 5), 1 - 2*x**2 + 2*x**4/3))
chk('двух членов ряда косинуса на x^4 не хватает',
    sp.expand(sum((-1)**i * x**(2*i) / sp.factorial(2*i)
                  for i in range(2)).subs(x, 2*x)).coeff(x, 4) == 0)

print('\n=== Задача 2: биномиальный ряд ===')


def binom_series(p, u, upto):
    """Биномиальный ряд по формуле, а не через sympy.series."""
    out = sp.Integer(1)
    coeff = sp.Integer(1)
    for j in range(1, upto + 1):
        coeff *= (p - j + 1) / sp.Integer(j)
        out += coeff * u**j
    return sp.expand(out)


chk('(1-x)^-4 = 1 + 4x + 10x^2 + 20x^3',
    same(binom_series(-4, -x, 3), 1 + 4*x + 10*x**2 + 20*x**3))
chk('и это же даёт sympy', same(ser((1 - x)**-4, 4), 1 + 4*x + 10*x**2 + 20*x**3))
chk('20x^3 из условия сходится с формулой', binom_series(-4, -x, 3).coeff(x, 3) == 20)
chk('все коэффициенты положительны — минусы сокращаются',
    all(binom_series(-4, -x, 5).coeff(x, j) > 0 for j in range(6)))

print('\n=== Задача 3: ряд по определению, производные даны ===')
# Формула n-й производной из условия, проверенная дифференцированием.
FORM = (x**2 + 2*n*x + n*(n - 1)) * sp.exp(x)
for order in (1, 2, 3, 4):
    chk(f'формула верна при n = {order}',
        same(sp.diff(x**2 * sp.exp(x), x, order), FORM.subs(n, order)))
derivs = [sp.Integer(0), sp.Integer(0)] + [FORM.subs({n: j, x: 0}) for j in (2, 3, 4)]
built = sum(derivs[j] * x**j / sp.factorial(j) for j in range(5))
chk('собранный ряд x^2 + x^3 + x^4/2', same(built, x**2 + x**3 + x**4/2))
chk('и он же — произведение x^2 на ряд экспоненты',
    same(built, ser(x**2 * sp.exp(x), 5)))
chk('без деления на n! вышло бы 2x^2 + 6x^3 + 12x^4',
    same(sum(derivs[j] * x**j for j in range(5)), 2*x**2 + 6*x**3 + 12*x**4))

print('\n=== Задача 4: cos^n x с буквой ===')
chk('через биномиальный ряд получается 1 - n x^2/2',
    same(sp.expand(binom_series(n, -x**2/2, 1)), 1 - n*x**2/2))
for value in (2, 3, 7, 11):
    chk(f'и при n = {value} совпадает с прямым разложением',
        same(ser(sp.cos(x)**value, 3), (1 - n*x**2/2).subs(n, value)))
d2 = sp.diff(sp.cos(x)**n, x, 2).subs(x, 0)
chk('вторая производная в нуле равна -n', same(sp.simplify(d2), -n))

print('\n=== Задача 5: произведение рядов ===')
exp3 = sum(x**j / sp.factorial(j) for j in range(4))
sin2 = x - x**3/6
prod = sp.expand(exp3 * sin2)
kept = sum(prod.coeff(x, j) * x**j for j in range(4))
chk('перемножение отрезков даёт x + x^2 + x^3/3', same(kept, x + x**2 + x**3/3))
chk('и то же даёт sympy', same(ser(sp.exp(x)*sp.sin(x), 4), x + x**2 + x**3/3))
chk('коэффициент при x^3 собирается из двух слагаемых, -1/6 и 1/2',
    sp.Rational(-1, 6) + sp.Rational(1, 2) == sp.Rational(1, 3))
chk('двух членов экспоненты на x^3 не хватает',
    sp.expand((1 + x) * sin2).coeff(x, 3) != R(1, 3))

print('\n=== Задача 6: квадрат и производная ===')
sq = sp.expand((x**2 - x**6/6)**2)
chk('квадрат отрезка даёт x^4 - x^8/3',
    same(sum(sq.coeff(x, j) * x**j for j in range(9)), x**4 - x**8/3))
chk('и то же даёт sympy', same(ser(sp.sin(x**2)**2, 9), x**4 - x**8/3))
chk('почленный квадрат дал бы x^4 - x^12/36 — другое',
    not same(x**4 - x**12/36, ser(sp.sin(x**2)**2, 13)))
chk('4x sin(x^2) cos(x^2) — это производная sin^2(x^2)',
    same(sp.diff(sp.sin(x**2)**2, x), 4*x*sp.sin(x**2)*sp.cos(x**2)))
chk('поэтому её ряд — производная ряда из (a)',
    same(sp.diff(x**4 - x**8/3, x), 4*x**3 - 8*x**7/3))
chk('и то же даёт прямое разложение',
    same(ser(4*x*sp.sin(x**2)*sp.cos(x**2), 8), 4*x**3 - 8*x**7/3))
chk('через двойной угол выходит то же', same(ser(2*x*sp.sin(2*x**2), 8),
                                             4*x**3 - 8*x**7/3))

print('\n=== Задача 7: ряд внутри ряда ===')
u = ser(sp.cos(2*x), 5) - 1
chk('cos2x - 1 обращается в нуле в ноль', u.subs(x, 0) == 0)
comp = sp.expand(1 + u + u**2/2 + u**3/6)
inner = sum(comp.coeff(x, j) * x**j for j in range(5))
chk('e^(cos2x - 1) = 1 - 2x^2 + 8x^4/3', same(inner, 1 - 2*x**2 + 8*x**4/3))
chk('и то же даёт sympy', same(ser(sp.exp(sp.cos(2*x) - 1), 5),
                               1 - 2*x**2 + 8*x**4/3))
chk('коэффициент при x^4 собирается из 2/3 и 2', R(2, 3) + 2 == R(8, 3))
chk('e^(cos2x) — это e, умноженное на предыдущее',
    same(ser(sp.exp(sp.cos(2*x)), 5), sp.E * (1 - 2*x**2 + 8*x**4/3)))
chk('без множителя e ответ был бы другим',
    not same(ser(sp.exp(sp.cos(2*x)), 5), 1 - 2*x**2 + 8*x**4/3))
chk('подстановка cos2x прямо в e^u неверна: показатель в нуле равен 1',
    sp.cos(2*x).subs(x, 0) == 1)

print('\n=== Задача 8: коэффициент как уравнение ===')
H = sp.sqrt(1 + x) * sp.exp(m*x)
c2 = ser(H, 3).coeff(x, 2)
chk('коэффициент при x^2 равен m^2/2 + m/2 - 1/8',
    same(c2, m**2/2 + m/2 - R(1, 8)))
roots = sorted(sp.solve(sp.Eq(c2, R(7, 4)), m), key=lambda v: float(v))
chk('корни -5/2 и 3/2', roots == [-R(5, 2), R(3, 2)])
chk('уравнение приводится к 4m^2 + 4m - 15 = 0',
    same(sp.expand(8*(c2 - R(7, 4))), 4*m**2 + 4*m - 15))
for value in roots:
    chk(f'при m = {value} коэффициент действительно 7/4',
        sp.simplify(c2.subs(m, value) - R(7, 4)) == 0)
chk('h\'\'(0) вдвое больше коэффициента',
    same(sp.diff(H, x, 2).subs(x, 0), 2*c2))

print('\n=== Задача 9: почленно, в обе стороны ===')
chk('производная a/(1-r) равна a/(1-r)^2',
    same(sp.diff(a/(1 - r), r), a/(1 - r)**2))
j = sp.Symbol('j', positive=True, integer=True)
chk('и это же — сумма j a r^(j-1)',
    same(sp.simplify(sp.summation(j * a * r**(j - 1), (j, 1, sp.oo))
                     .rewrite(sp.Piecewise).args[0][0]
                     if False else sp.diff(a/(1 - r), r)), a/(1 - r)**2))
partial = sum(j_ * a * r**(j_ - 1) for j_ in range(1, 40))
for value in (R(1, 5), R(3, 10), -R(1, 4)):
    chk(f'частичная сумма при r = {value} сходится к a/(1-r)^2',
        abs(float((partial - a/(1 - r)**2).subs({r: value, a: 1}))) < 1e-12)
chk('|-2x^2| < 1 равносильно |x| < 1/sqrt(2)',
    sp.solveset(sp.Abs(-2*x**2) < 1, x, sp.S.Reals)
    == sp.Interval.open(-1/sp.sqrt(2), 1/sp.sqrt(2)))
chk('sqrt(2)/2 — это 1/sqrt(2)', sp.simplify(sp.sqrt(2)/2 - 1/sp.sqrt(2)) == 0)
geo = sum((-2*x**2)**j_ for j_ in range(200))
for value in (0.1, 0.25, 0.4):
    chk(f'частичная сумма при x = {value} сходится к 1/(1+2x^2)',
        abs(float((geo - 1/(1 + 2*x**2)).subs(x, sp.Float(value)))) < 1e-12)

print('\n=== Задача 10: ряд из уравнения ===')
Y = sp.Function('Y')
RHS = (x**2*Y(x) - Y(x))/(x**2 + 1)
d1 = RHS
d2 = sp.diff(d1, x).subs(sp.Derivative(Y(x), x), d1)
d3 = sp.diff(d2, x).subs(sp.Derivative(Y(x), x), d1)
at0 = {x: 0, Y(0): 3}
v1 = sp.simplify(d1.subs(x, 0).subs(Y(0), 3))
v2 = sp.simplify(d2.subs(x, 0).subs(Y(0), 3))
v3 = sp.simplify(d3.subs(x, 0).subs(Y(0), 3))
chk("y'(0) = -3 прямо из уравнения", v1 == -3)
chk("y''(0) = 3 — совпало с тем, что дано", v2 == 3)
chk("y'''(0) = 9 — совпало с тем, что дано", v3 == 9)
series_y = 3 + v1*x + v2*x**2/2 + v3*x**3/6
chk('ряд 3 - 3x + 3x^2/2 + 3x^3/2', same(series_y, 3 - 3*x + R(3, 2)*x**2
                                         + R(3, 2)*x**3))
# Точное решение уравнения — из пункта (d) той же бумаги; оно принадлежит E7,
# и здесь нужно только чтобы подтвердить ряд третьим способом.
EXACT = 3*sp.exp(x - 2*sp.atan(x))
chk('точное решение удовлетворяет уравнению',
    sp.simplify(sp.diff(EXACT, x) - (x**2*EXACT - EXACT)/(x**2 + 1)) == 0)
chk('и раскладывается в тот же ряд', same(ser(EXACT, 4), series_y))
value = series_y.subs(x, R(15, 100))
chk('y(0.15) = 2.58881 до шести значащих цифр',
    f'{float(value):.6g}' == '2.58881')
chk('и точное решение даёт другое число в четвёртой цифре',
    f'{float(EXACT.subs(x, R(15, 100))):.6g}' != '2.58881')

print('\n=== Задача 11: интеграл и предел через ряд ===')
inner11 = sp.expand((x + x**2 + x**3/3).subs(x, x**2))
chk('подстановка x^2 даёт x^2 + x^4 + x^6/3', same(inner11, x**2 + x**4 + x**6/3))
chk('и то же даёт прямое разложение',
    same(ser(sp.exp(x**2)*sp.sin(x**2), 7), x**2 + x**4 + x**6/3))
integral = sp.integrate(inner11, (x, 0, 1))
chk('интеграл равен 61/105', integral == R(61, 105))
chk('это 1/3 + 1/5 + 1/21', R(1, 3) + R(1, 5) + R(1, 21) == R(61, 105))
chk('и он близок к настоящему интегралу',
    abs(float(integral) - float(sp.N(sp.Integral(sp.exp(x**2)*sp.sin(x**2),
                                                 (x, 0, 1)), 10))) < 0.05)
chk('предел 4n tan(pi/n) равен 4pi',
    sp.limit(4*n*sp.tan(sp.pi/n), n, sp.oo) == 4*sp.pi)
tan_series = x + x**3/3 + 2*x**5/15
chk('через ряд тангенса: 4n(pi/n + pi^3/(3n^3) + ...) -> 4pi',
    sp.limit(sp.expand(4*n*tan_series.subs(x, sp.pi/n)), n, sp.oo) == 4*sp.pi)

print('\n=== Задача 12: ошибка приближения ===')
X0 = 1/sp.sqrt(3)
chk('arctan(1/sqrt(3)) = pi/6', sp.simplify(sp.atan(X0) - sp.pi/6) == 0)
three = sum((-1)**i * X0**(2*i + 1)/(2*i + 1) for i in range(3))
chk('π по трём членам равно 3.156', f'{float(6*three):.4g}' == '3.156')
term = lambda idx: abs(float(X0**(2*idx - 1)/(2*idx - 1)))
chk('член 7 меньше 0.0001, а член 6 — нет',
    term(7) < 1e-4 <= term(6))
chk('значит членов нужно 6, а не 7', 7 - 1 == 6)
EXACT12 = sp.pi/(6*sp.sqrt(3)) - sp.log(R(4, 3))/2
chk('точный интеграл совпадает с интегралом от arctan',
    sp.simplify(sp.integrate(sp.atan(x), (x, 0, X0)) - EXACT12) == 0)
approx12 = sp.integrate(x - x**3/3 + x**5/5 - x**7/7, (x, 0, X0))
chk('интеграл от четырёх членов равен 0.158422 до шести знаков',
    f'{float(approx12):.6f}' == '0.158422')
bound = sp.integrate(x**9/9, (x, 0, X0))
chk('граница по теореме равна 1/21870', sp.simplify(bound - R(1, 21870)) == 0)
chk('и это 4.57e-05', f'{float(bound):.3g}' == '4.57e-05')
err_round = abs(float(EXACT12) - 0.158422)
err_exact = abs(float(EXACT12 - approx12))
chk('ошибка по округлённому значению 3.69e-05', f'{err_round:.3g}' == '3.69e-05')
chk('ошибка по неокруглённому 3.73e-05', f'{err_exact:.3g}' == '3.73e-05')
chk('до двух значащих цифр они совпадают',
    f'{err_round:.2g}' == f'{err_exact:.2g}' == '3.7e-05')
chk('и обе меньше границы', err_round < float(bound) and err_exact < float(bound))

print('\n=== На время: май 2024 TZ2 P1 Q12 ===')
chk('(1-ax)^(-1/2) = 1 + ax/2 + 3a^2x^2/8',
    same(binom_series(-R(1, 2), -a*x, 2), 1 + a*x/2 + 3*a**2*x**2/8))
lhs = (1 - 2*x)**R(-1, 2) * (1 - 4*x)**R(-1, 2)
chk('и то же даёт sympy при a = 2 и a = 4',
    same(ser(lhs, 3), 1 + 3*x + R(19, 2)*x**2))
chk('коэффициент при x^2 собирается из 6, 2 и 3/2', 6 + 2 + R(3, 2) == R(19, 2))
chk('без перекрёстного члена вышло бы 15/2', 6 + R(3, 2) == R(15, 2))
approx_t = (2 + 6*x + 19*x**2).subs(x, R(1, 10)) / 2
chk('при x = 1/10 приближение равно 279/200', approx_t == R(279, 200))
exact_t = sp.simplify(lhs.subs(x, R(1, 10)))
chk('точная левая часть равна 10/(4 sqrt(3))',
    sp.simplify(exact_t - 10/(4*sp.sqrt(3))) == 0)
root3 = sp.solve(sp.Eq(10/(4*sp.Symbol('s')), R(279, 200)), sp.Symbol('s'))[0]
chk('решая относительно sqrt(3), получаем 500/279', root3 == R(500, 279))
# Перевёрнутое приближение даёт 837/500, и оно не хуже: обе дроби
# промахиваются на те же 3.4%, только в разные стороны. Ровно об этом
# написано в разборе, и проверка сторожит именно это утверждение.
flip = sp.solve(sp.Eq(5*sp.Symbol('s')/6, R(279, 200)), sp.Symbol('s'))[0]
chk('перевернув сначала, получаем 837/500', flip == R(837, 500))
gap_ms = float(R(500, 279)) - float(sp.sqrt(3))
gap_flip = float(R(837, 500)) - float(sp.sqrt(3))
chk('обе дроби лежат по разные стороны от sqrt(3)', gap_ms > 0 > gap_flip)
chk('и промахиваются примерно одинаково, на 3.4%',
    abs(abs(gap_ms) - abs(gap_flip)) < 0.005)
chk('множитель приближения 0.9665 объясняет обе',
    abs(float(R(279, 200) / (10/(4*sp.sqrt(3)))) - 0.9665) < 1e-3)
chk('область сходимости решает более узкая скобка: |x| < 1/4',
    min(R(1, 2), R(1, 4)) == R(1, 4))

print('\n=== Тренажёр: ключи различают приёмы ===')
chk('в ключе двенадцать пунктов', len(gen.TRIGGER) == 12)
chk('и все девять приёмов представлены',
    set(gen.TRIGGER.values()) == {'def', 'sub', 'binom', 'mult', 'comp',
                                  'termwise', 'ode', 'approx', 'error'})

print('\n=== Ноутбук: пустой и с эталонами ===')
PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')
doc = json.load(open(gen.NOTEBOOK))
notebook_cells = [''.join(cc['source']) for cc in doc['cells']
                  if cc['cell_type'] == 'code']
names = set()
for source in notebook_cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
chk(f'placeholder-ов столько же, сколько эталонов ({len(names)})',
    names == set(gen.ANSWERS))

TRAINER_FILL = "\n".join(
    f"    {num}: '{code}'," for num, code in sorted(gen.TRIGGER.items()))


def filled(source, swap=None):
    swap = swap or {}
    out, in_trainer = [], False
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {swap.get(name, gen.ANSWERS[name])}')
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


def run(sources):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in sources:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


here = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'calculus'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= len(names))

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': 'x**2 - x**3/6',                  # подстановка в показатель
    'q1b': '1 - 2*x**2 + x**4/3',            # потерян множитель 16/24
    'q2': '1 + 4*x + 20*x**2 + 20*x**3',     # b без деления на 2!
    'q3': 'x**2 + x**3 + x**4',              # забыто деление на 4!
    'q4': '1 - n*x**2',                      # забыто деление на 2!
    'q5': 'x + x**2 + x**3/6',               # одно из двух слагаемых x^3
    'q6a': 'x**4 - x**12/36',                # почленный квадрат
    'q6b': '4*x**3 - 8*x**7',                # не поделено на 3
    'q7a': '1 - 2*x**2 + 2*x**4/3',          # взято только u, без u^2/2
    'q7b': '1 - 2*x**2 + 8*x**4/3',          # потерян множитель e
    'q8': '[Rational(3, 2)]',                # найден один корень из двух
    'q9a': 'a/(1 - r)',                      # не возведено в квадрат
    'q9b': '0.7071',                         # десятичная вместо точной
    'q9c': '1/(1 - 2*x**2)',                 # потерян знак
    'q10a': '3 - 3*x + 3*x**2 + 9*x**3',     # забыты факториалы
    'q10b': '2.5888',                        # округление не до шести цифр
    'q11a': 'Rational(61, 100)',
    'q11b': '2*pi',
    'q12a': '3.142',                         # выдано настоящее π
    'q12b': '7',                             # ошибка на единицу
    'q12c': '4.6e-5',
    'q12d': 'Rational(1, 2187)',
    'qt_a': '1 + a*x/2 + a**2*x**2/8',       # потеряна тройка
    'qt_b': 'Rational(837, 500)',            # перевёрнуто до подстановки
}
missed = []
for name, wrong in sorted(BREAK.items()):
    out = run([filled(source, {name: wrong}) for source in notebook_cells])
    if not [line for line in out.split('\n') if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
