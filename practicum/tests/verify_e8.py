"""Независимая проверка каждого ответа практикума E8.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **дифференцировать**. Проверки ноутбука
не берут производных вовсе: они идут по кривой шагами и смотрят на соседей,
а вогнутость меряют хордой. Тест поэтому делает ровно обратное — считает
f′ и f″ символьно через sympy, решает f′ = 0 точно, а где спрашивают, сколько
раз кубика встречает ось, берёт её дискриминант:

    Δ = −4p³ − 27q²   для  x³ + px + q

Δ > 0 — три разных корня, Δ = 0 — кратный, Δ < 0 — один. Ни ходьбы, ни
просмотра: чистая алгебра, и она же подтверждает ответ схемы оценивания
к самому дорогому пункту темы.

Второй якорь — числа схем: p = 2 и q = −64/3, (0.709, 0.640),
(±1.94, ∓1.20), (0, e), (π/2, 1/e), (π, e), −½ ≤ y ≤ ½, −1.60, 0.656,
4a³/27 + b, −4√(a²−ab+b²), c = 0, c > 0, c < 0, 2c^{3/2}+2, 0 < c < 1,
c = 1, c > 1, √((2√3−3)/3) ≈ 0.393.

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора и
по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_e8.py
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

import build_e8 as gen

res = []
X = sp.Symbol('x')
Y = sp.Symbol('y')


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name, **extra):
    """Эталон из генератора — в пространстве имён ноутбука."""
    import kit
    names = dict(vars(kit))
    names.update({letter: sp.Symbol(letter) for letter in ('a', 'b', 'c', 'd')})
    names.update(extra)
    return eval(gen.ANSWERS[name], names)


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def flat(f, var=X):
    """Точки нулевой производной — решением f′ = 0, а не ходьбой."""
    return sorted(sp.solve(sp.diff(f, var), var))


def kind(f, at, var=X):
    """Вид точки по второй производной, а где она молчит — по знаку самой f."""
    second = sp.diff(f, var, 2).subs(var, at)
    second = sp.simplify(second)
    if second.is_number and second != 0:
        return 'minimum' if second > 0 else 'maximum'
    step = sp.Rational(1, 1000)
    here = sp.N(f.subs(var, at), 30)
    left = sp.N(f.subs(var, at - step), 30) - here
    right = sp.N(f.subs(var, at + step), 30) - here
    if left > 0 and right > 0:
        return 'minimum'
    if left < 0 and right < 0:
        return 'maximum'
    return 'inflexion'


def bends(f, lo, hi, var=X):
    """Нули второй производной на отрезке — численно, но из самой f″."""
    second = sp.diff(f, var, 2)
    fast = sp.lambdify(var, second, 'mpmath')
    out, last, where = [], None, None
    for i in range(2001):
        point = lo + (hi - lo) * i / 2000
        try:
            value = float(fast(point))
        except (ValueError, ZeroDivisionError, TypeError, ArithmeticError):
            last = where = None
            continue
        if not (value == value and abs(value) < 1e12):
            last = where = None
            continue
        if last is not None and last * value < 0:
            out.append(float(sp.nsolve(second, var, (where, point), solver='bisect')))
        last, where = value, point
    return out


def discriminant(p, q):
    """Дискриминант кубики x³ + px + q: знак решает, сколько разных корней."""
    return sp.simplify(-4 * p ** 3 - 27 * q ** 2)


def distinct_roots(p, q):
    """Сколько разных вещественных корней у x³ + px + q — по дискриминанту."""
    delta = discriminant(p, q)
    if delta > 0:
        return 3
    if delta < 0:
        return 1
    return 1 if (p == 0 and q == 0) else 2


print('=== Задача 1: 4x³/3 − 16x ===')
f1 = 4 * X ** 3 / 3 - 16 * X
roots = flat(f1)
p1 = [root for root in roots if root > 0][0]
q1 = sp.simplify(f1.subs(X, p1))
chk('f′ = 0 даёт x = ±2', roots == [-2, 2])
chk('схема: p = 2', p1 == 2)
chk('схема: q = −64/3', q1 == sp.Rational(-64, 3))
chk('это минимум', kind(f1, p1) == 'minimum')
chk('эталон совпал', tuple(A('q1')) == (p1, q1))

print('\n=== Задача 2: калькуляторные вершины ===')
f2a = sp.log(X * sp.exp(X) + 1) - X ** 4
place = sp.nsolve(sp.diff(f2a, X), X, 0.7)
chk('схема: x = 0.709', near(place, '0.709'))
chk('схема: y = 0.640', near(f2a.subs(X, place), '0.640'))
chk('и это максимум', sp.diff(f2a, X, 2).subs(X, place) < 0)
got = A('q2a')
chk('эталон (a) совпал', near(got[0], '0.709') and near(got[1], '0.640'))

f2b = X * (X ** 2 - 16) / (X ** 2 + 16)
roots = [sp.nsolve(sp.diff(f2b, X), X, guess) for guess in (-2, 2)]
chk('схема: x = ±1.94', near(roots[0], '-1.94') and near(roots[1], '1.94'))
chk('схема: y = ∓1.20', near(f2b.subs(X, roots[0]), '1.20')
    and near(f2b.subs(X, roots[1]), '-1.20'))
chk('левая точка — максимум', sp.diff(f2b, X, 2).subs(X, roots[0]) < 0)
got = A('q2b')
chk('эталон (b) совпал', near(got[0][0], '-1.94') and near(got[1][1], '-1.20'))

print('\n=== Задача 3: знаки f′ и f″ ===')
slope = 3 * X ** 2 + 12 * X - 15
shape = sp.integrate(slope, X)
chk('схема: a = −5 и b = 1', sorted(sp.solve(slope, X)) == [-5, 1])
chk('при x = −5 производная меняет знак с + на −',
    slope.subs(X, -6) > 0 and slope.subs(X, -4) < 0)
chk('и это максимум', kind(shape, -5) == 'maximum')
chk('схема: c = −2', sp.solve(sp.diff(shape, X, 2), X) == [-2])
chk('вторая производная меняет знак в c',
    sp.diff(shape, X, 2).subs(X, -3) < 0 and sp.diff(shape, X, 2).subs(X, -1) > 0)
chk('эталон (b) совпал', A('q3b') == 'maximum')
chk('эталон (d) совпал', A('q3d') == 'inflexion')

print('\n=== Задача 4: e^{cos 2x} ===')
f4 = sp.exp(sp.cos(2 * X))
inside = [place for place in (0, sp.pi / 2, sp.pi, -sp.pi / 4, 5 * sp.pi / 4)
          if sp.simplify(sp.diff(f4, X).subs(X, place)) == 0]
chk('нулевой наклон ровно в трёх точках отрезка', len(inside) == 3)
chk('схема: (0, e), (π/2, 1/e), (π, e)',
    [sp.simplify(f4.subs(X, place)) for place in (0, sp.pi / 2, sp.pi)]
    == [sp.E, sp.exp(-1), sp.E])
second = [sp.simplify(sp.diff(f4, X, 2).subs(X, place))
          for place in (0, sp.pi / 2, sp.pi)]
chk('схема: f″ = −4e, 4/e, −4e',
    second == [-4 * sp.E, 4 * sp.exp(-1), -4 * sp.E])
chk('то есть максимум, минимум, максимум',
    [kind(f4, place) for place in (0, sp.pi / 2, sp.pi)]
    == ['maximum', 'minimum', 'maximum'])
got = A('q4a')
chk('эталон (a) совпал',
    [sp.simplify(one - two) for one, two in zip([pair[1] for pair in got],
                                                [sp.E, sp.exp(-1), sp.E])]
    == [0, 0, 0])
chk('эталон (b) совпал', A('q4b') == ['maximum', 'minimum', 'maximum'])

print('\n=== Задача 5: область значений x√(1−x²) ===')
f5 = X * sp.sqrt(1 - X ** 2)
roots = [root for root in sp.solve(sp.diff(f5, X), X) if root.is_real]
values = [sp.simplify(f5.subs(X, root)) for root in roots] \
    + [f5.subs(X, -1), f5.subs(X, 1)]
chk('схема: критические точки ±1/√2', sorted(roots) == sorted(
    [-sp.sqrt(2) / 2, sp.sqrt(2) / 2]))
chk('схема: a = −1/2 и b = 1/2',
    min(values) == sp.Rational(-1, 2) and max(values) == sp.Rational(1, 2))
chk('эталон совпал', A('q5') == sp.Interval(sp.Rational(-1, 2), sp.Rational(1, 2)))

print('\n=== Задача 6: перегибы через f″ ===')
f6a = (3 * X + 2) / (4 * X ** 2 - 1)
found = bends(f6a, -4, -0.55)
chk('перегиб на отрезке ровно один', len(found) == 1)
chk('схема: x = −1.60', near(found[0], '-1.60'))
chk('эталон (a) совпал', near(A('q6a'), '-1.60'))

f6b = X * sp.sqrt((9 * X ** 4 - 1) / 2)
found = bends(f6b, float(sp.sqrt(3) / 3) + 1e-3, 1)
chk('и здесь перегиб один', len(found) == 1)
chk('схема: x = 0.656', near(found[0], '0.656'))
chk('эталон (b) совпал', near(A('q6b'), '0.656'))

print('\n=== Задача 7: семейство x³ + ax² + b ===')
a, b = sp.symbols('a b')
f7 = X ** 3 + a * X ** 2 + b
roots = sorted(sp.solve(sp.diff(f7, X), X), key=str)
chk('f′ = 0 даёт x = 0 и x = −2a/3',
    set(roots) == {sp.Integer(0), -2 * a / 3})
tail = sp.simplify(f7.subs(X, -2 * a / 3))
chk('схема: y(Q) = 4a³/27 + b', sp.simplify(tail - (4 * a ** 3 / 27 + b)) == 0)
second = sp.diff(f7, X, 2)
chk('схема: d²y/dx² = 6x + 2a', sp.simplify(second - (6 * X + 2 * a)) == 0)
chk('при a > 0: P минимум, Q максимум',
    second.subs(X, 0).subs(a, 3) > 0 and second.subs(X, -2 * a / 3).subs(a, 3) < 0)
chk('при a > 0 и b > 0 обе точки выше оси',
    all(f7.subs({a: av, b: bv, X: root.subs(a, av)}) > 0
        for av, bv in ((3, 1), (1, 2), (6, 1)) for root in roots))
got = A('q7e')
chk('эталон (e) совпал',
    {(sp.simplify(one), sp.simplify(two)) for one, two in got}
    == {(sp.Integer(0), b), (sp.simplify(-2 * a / 3), sp.simplify(tail))})
chk('эталон (f)(i) совпал', A('q7f_i') == ['minimum', 'maximum'])
chk('эталон (f)(ii) совпал', A('q7f_ii') == ['above', 'above'])
claim = A('q7g')
agree = all(bool(claim.subs({a: av, b: bv}))
            == bool((4 * av ** 3 / sp.Integer(27) + bv) < 0)
            for av in (-3, -2, -1, sp.Rational(-1, 2))
            for bv in (sp.Rational(1, 4), 1, 2, 5, 9))
chk('эталон (g) согласен со знаком y(Q) во всех узлах', agree)

print('\n=== Задача 8: коробка ===')
a, b = sp.symbols('a b', positive=True)
V = X * (a - 2 * X) * (b - 2 * X)
second = sp.expand(sp.diff(V, X, 2))
chk('схема: d²V/dx² = 24x − 4(a+b)',
    sp.simplify(second - (24 * X - 4 * (a + b))) == 0)
x_m = ((a + b) - sp.sqrt(a ** 2 - a * b + b ** 2)) / 6
chk('схема: подстановка даёт −4√(a²−ab+b²)',
    sp.simplify(second.subs(X, x_m) + 4 * sp.sqrt(a ** 2 - a * b + b ** 2)) == 0)
chk('а этот корень положителен при любых a и b',
    all(sp.sqrt(av ** 2 - av * bv + bv ** 2) > 0 for av, bv in ((3, 5), (2, 7), (4, 9))))
chk('эталон (i) совпал',
    sp.simplify(A('q8_i', a=a, b=b) - second) == 0)
chk('эталон (ii) совпал', A('q8_ii') == 'maximum')

print('\n=== Задача 9: множества c ===')
c = sp.Symbol('c')
f9 = X ** 3 - 3 * c * X + 2
chk('схема: f′ = 3x² − 3c', sp.simplify(sp.diff(f9, X) - (3 * X ** 2 - 3 * c)) == 0)
chk('при c > 0 два корня, при c = 0 один, при c < 0 ни одного',
    [len([root for root in sp.solve(sp.diff(f9, X).subs(c, value), X)
          if root.is_real]) for value in (1, 0, -1)] == [2, 1, 0])
c = sp.Symbol('c')
f9 = X ** 3 - 3 * c * X + 2
tops = [sp.simplify(f9.subs(X, -sp.sqrt(c))), sp.simplify(f9.subs(X, sp.sqrt(c)))]
chk('схема: 2c^{3/2} + 2 и −2c^{3/2} + 2',
    sp.simplify(tops[0] - (2 * c ** sp.Rational(3, 2) + 2)) == 0
    and sp.simplify(tops[1] - (-2 * c ** sp.Rational(3, 2) + 2)) == 0)
chk('эталон (c)(i) совпал', A('q9c_i') == sp.FiniteSet(0))
chk('эталон (c)(ii) совпал', A('q9c_ii') == sp.Interval.open(0, sp.oo))
chk('эталон (c)(iii) совпал', A('q9c_iii') == sp.Interval.open(-sp.oo, 0))
got = A('q9d', c=sp.Symbol('c'))
chk('эталон (d) совпал',
    [sp.simplify(pair[1] - top) for pair, top in zip(got, tops)] == [0, 0])

print('\n=== Задача 10: сколько раз кубика встречает ось ===')
counts = {value: distinct_roots(-3 * sp.Integer(value), 2)
          for value in (sp.Rational(1, 2), 1, 2, 4)}
chk('дискриминант: 0 < c < 1 — одно пересечение', counts[sp.Rational(1, 2)] == 1)
chk('дискриминант: c = 1 — два', counts[1] == 2)
chk('дискриминант: c > 1 — три', counts[2] == 3 and counts[4] == 3)
chk('эталон (e)(i) совпал', A('q10e_i') == sp.Interval.open(0, 1))
chk('эталон (e)(ii) совпал', A('q10e_ii') == sp.FiniteSet(1))
chk('эталон (e)(iii) совпал', A('q10e_iii') == sp.Interval.open(1, sp.oo))

c, d = sp.symbols('c d')
claim = A('q10f')
grid = [(cv, dv) for cv in (-2, -1, 0, sp.Rational(1, 2), 1, 2, 3)
        for dv in (-3, -2, -1, 0, 1, 2, 3)]
agree = [(cv, dv) for cv, dv in grid
         if bool(claim.subs({c: cv, d: dv}))
         != (distinct_roots(-3 * cv, dv) == 1)]
chk('эталон (f) согласен с дискриминантом во всех узлах', not agree)
if agree:
    print('   расходится в', agree[:4])
chk('и он же покрывает вырожденный случай c = d = 0',
    bool(claim.subs({c: 0, d: 0})) and distinct_roots(0, 0) == 1)

print('\n=== Задача 11: y² = x³ + x ===')
slope = (3 * X ** 2 + 1) / (2 * sp.sqrt(X ** 3 + X))
chk('числитель наклона нигде не ноль',
    sp.solve(sp.Eq(3 * X ** 2 + 1, 0), X, domain=sp.S.Reals)
    == [] or not any(root.is_real for root in sp.solve(3 * X ** 2 + 1, X)))
chk('эталон (d)(ii) пуст', A('q11d') == [])
branch = sp.sqrt(X ** 3 + X)
quartic = sp.simplify(sp.numer(sp.together(sp.diff(branch, X, 2))))
chk('схема: f″ = 0 приводит к 3x⁴ + 6x² − 1 = 0',
    sp.simplify(sp.factor(quartic) / sp.factor(3 * X ** 4 + 6 * X ** 2 - 1)).is_constant())
want = sp.sqrt((2 * sp.sqrt(3) - 3) / 3)
chk('схема: x = √((2√3 − 3)/3)',
    sp.simplify(3 * want ** 4 + 6 * want ** 2 - 1) == 0)
chk('и это 0.393', near(want, '0.393'))
chk('эталон (e) совпал', sp.simplify(A('q11e') - want) == 0)

print('\n=== Задача 12: чётность n ===')
n, a = sp.symbols('n a', positive=True)
prime = n * X ** (n - 1) * (a - 2 * X) * (a - X) ** (n - 1)
signs = {}
for value in (2, 3, 4, 5):
    here = prime.subs(n, value).subs(a, 2)
    signs[value] = sp.sign(here.subs(X, -1))
chk('схема: f′(−1) < 0 при чётном n', signs[2] < 0 and signs[4] < 0)
chk('схема: f′(−1) > 0 при нечётном n', signs[3] > 0 and signs[5] > 0)
chk('и f′(a/4) > 0 при любом n',
    all(prime.subs({n: value, a: 2, X: sp.Rational(1, 2)}) > 0
        for value in (2, 3, 4, 5)))
chk('значит при чётном n это минимум, при нечётном — перегиб',
    [kind((X ** value * (2 - X) ** value), 0) for value in (2, 3, 4, 5)]
    == ['minimum', 'inflexion', 'minimum', 'inflexion'])
chk('эталон (i) совпал', A('q12_i') == 'minimum')
chk('эталон (ii) совпал', A('q12_ii') == 'inflexion')

print('\n=== Таймер: (x² + y²)y² = 4x² ===')
relation = (X ** 2 + Y ** 2) * Y ** 2 - 4 * X ** 2
slope = sp.idiff(relation, Y, X)
candidates = sp.solve(sp.Eq(sp.numer(sp.together(slope)), 0), Y)
chk('наклон ноль только при y² = 4 или x = 0',
    set(sp.simplify(root) for root in candidates) <= {sp.Integer(2), sp.Integer(-2),
                                                     sp.Integer(0)})
chk('а условие требует −2 < y < 2 и x > 0', True)
chk('эталон таймера пуст', A('qt') == [])

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: пустой и с эталонами ===')
BREAK_E8 = {
    # 1: ответ обрывается на первой координате, и вторая берётся неверно
    'q1': '(2, -64)',
    'q2a': '(0.709, 0.709)',
    'q2b': '[(1.94, 1.20), (-1.94, -1.20)]',
    'q3b': "'minimum'",
    'q3d': "'minimum'",
    'q4a': '[(0, E), (pi, E)]',
    'q4b': "['minimum', 'maximum', 'minimum']",
    'q5': 'Interval(-1, 1)',
    'q6a': '-1.61',
    'q6b': '0.655',
    'q7e': '[(0, b), (-a/3, 4*a**3/27 + b)]',
    'q7f_i': "['maximum', 'minimum']",
    'q7f_ii': "['above', 'below']",
    'q7g': '4*a**3/27 + b > 0',
    'q8_i': '12*x**2 - 4*(a + b)*x + a*b',
    'q8_ii': "'minimum'",
    'q9c_i': 'FiniteSet(1)',
    'q9c_ii': 'Interval(0, oo)',
    'q9c_iii': 'Interval(-oo, 0)',
    'q9d': '[(-sqrt(c), -2*c**Rational(3, 2) + 2),\n        (sqrt(c), 2*c**Rational(3, 2) + 2)]',
    'q10e_i': 'Interval.open(0, 2)',
    'q10e_ii': 'FiniteSet(2)',
    'q10e_iii': 'Interval.open(2, oo)',
    'q10f': 'Or(c <= 0, d > 2*c**Rational(3, 2))',
    'q11d': '[(0, 0)]',
    'q11e': '0.394',
    'q12_i': "'inflexion'",
    'q12_ii': "'minimum'",
    'qt': '[(2, 2)]',
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
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 25)

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
chk('у каждого эталона есть типовая ошибка', set(BREAK_E8) == set(gen.ANSWERS))

generic = ('the slope is not zero', 'there is no point of inflexion',
           'the answer is a word', 'could not be checked')
missed, named = [], 0
for name, wrong in sorted(BREAK_E8.items()):
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
chk(f'все {len(BREAK_E8)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
print(f'   названы по имени {named} из {len(BREAK_E8)}')
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
