"""Проверяет механику плотности: Density, моменты, моду и проверки D6.

verify_d6 сверяет ответы одного практикума, а здесь сверяется сама
проверка: что площадь под формулой сходится с первообразной sympy до
десятого знака — и у многочлена, и у arccos с корневой особенностью на
краю, и на бесконечном промежутке; что буквы плотности она находит сама
из того, что площадь — единица, и отбрасывает решение, при котором
плотность отрицательна, называя точку; что медиана, мода и моменты
разбираются с именем промаха; что ответ-выражение сверяется в нескольких
значениях букв; что пустой ответ не роняет ячейку.

Главное свойство секции: всё — интеграл одной плотности, и считает его
квадратура. Первообразная в тесте есть (sympy.integrate), а в проверке —
нет. Последний раздел проверяет это по коду.

Запуск:  python practicum/tests/test_kit_density.py
"""
import ast
import io
import math
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
import kit
from kit import *

ok, bad = [], []


def check(name, got, expect=True):
    (ok if got == expect else bad).append(name)
    if got != expect:
        print(f'  ПРОВАЛ {name}')


def said(call):
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        call()
    text = buffer.getvalue()
    print(text, end='')
    return text


language('en')
m, a, b, c, q = sp.symbols('m a b c q')
kp = sp.Symbol('k', positive=True)

print('=== площадь под формулой ===')
cases = [
    ({(0, 2): 3 * x ** 2 / 8}, (0.5, 1.5)),
    ({(0, 1): acos(x)}, (0.3, 1)),                               # корневая особенность у 1
    ({(0, 1): 2 / (pi * sqrt(1 - x ** 2))}, (0.5, 1)),          # подынтегральное уходит в ∞
    ({(0, 1): x / 2, (1, Rational(5, 2)): Rational(1, 2)}, (0.5, 2)),
    ({(0, oo): 9 * x * exp(-3 * x)}, (0.2, oo)),
    ({(Rational(1, 2), 3): Rational(6, 85) * (4 + 3 * x - x ** 2)}, (1, 2)),
]
worst = 0.0
for pieces, (lo, hi) in cases:
    X = Density(pieces)
    got = float(sympify(P((X > lo) & (X < hi)) if hi is not oo else P(X > lo)))
    want = sum(float(sp.integrate(expr, (x, max(sp.sympify(lo), sp.sympify(left)), min(sp.sympify(hi), sp.sympify(right)))))
               for (left, right), expr in pieces.items()
               if max(sp.sympify(lo), sp.sympify(left)) < min(sp.sympify(hi), sp.sympify(right)))
    worst = max(worst, abs(got - want) / want)
check('area-matches-antiderivative', worst < 1e-10)
print(f'   наибольшее относительное расхождение с первообразной: {worst:.1e}')
X = Density({(0, 2): 3 * x ** 2 / 8}, 'X')
check('le-equals-lt', float(sympify(P(X <= 1.2))) == float(sympify(P(X < 1.2))))
check('point-has-no-area', float(sympify(P(X == 1.2))) == 0.0)
check('outside-is-zero', float(sympify(P(X > 5))) == 0.0 and abs(float(sympify(P(X < 5))) - 1) < 1e-12)
check('total-is-one', abs(float(sympify(total_probability(X))) - 1) < 1e-12)
check('blank-density', P(Density({(0, ...): x}) < 1) is Ellipsis)
try:
    Density({(0, 2): x})
    check('area-not-one-raises', False)
except ValueError:
    check('area-not-one-raises', True)
try:
    Density({(0, 2): Rational(3, 2) - x})
    check('negative-density-raises', False)
except ValueError:
    check('negative-density-raises', True)
check('pdf-value', X.pdf(1) == Rational(3, 8) and X.pdf(3) == 0)

print('\n=== буквы плотности: площадь — единица ===')
K = Density({(0, 1): kp / sqrt(4 - 3 * x ** 2)}, 'K')
check('constant-exact', verify_letters('k', 3 * sqrt(3) / pi, kp, [K], exact=True))
text = said(lambda: verify_letters('k', 1.65, kp, [K], exact=True))
check('decimal-for-exact-named', '❌' in text and 'exact value' in text)
check('constant-decimal', verify_letters('k', 1.65, kp, [K]))
text = said(lambda: verify_letters('k', 1.8, kp, [K]))
check('wrong-constant-area-named', '❌' in text and 'area under the density' in text)
L = Density({(0, 2): c - x}, 'L')
text = said(lambda: verify_letters('c', 1.5, c, [L]))
check('negative-density-root-named', '❌' in text and 'density is never negative' in text)
two = Density({(0, 2): a * x + b}, 'two')
check('two-letters', verify_letters('a, b', [Rational(-1, 2), 1], [a, b], [two], [Eq(two.pdf(2), 0)]))
check('two-letters-one-condition', verify_letters('a, b', [Rational(-1, 2), 1], [a, b], [two]), False)
bounds = Density({(0, kp): kp * x, (kp, 2 * kp): 2 * kp * x - x ** 2}, 'B')
check('letter-in-bounds', verify_letters('k', 0.950, kp, [bounds]))
check('area-expression', verify_chance('площадь', 7 * kp ** 3 / 6, total_probability(bounds), free=kp))
check('area-expression-wrong', verify_chance('площадь', 7 * kp ** 3 / 3, total_probability(bounds), free=kp), False)
shift = Density({(0, b): a * x * exp(x)}, 'S')
check('letter-in-terms-of', verify_letters('a(b)', 1 / (b * exp(b) - exp(b) + 1), a, [shift], free=b))
text = said(lambda: verify_letters('a(b)', 1 / (b * exp(b) - exp(b)), a, [shift], free=b))
check('letter-in-terms-of-wrong', '❌' in text and '(at b = ' in text)

print('\n=== медиана и квартиль ===')
check('median-found', verify_letters('медиана', 1.59, m, [X], [Eq(P(X < m), 0.5)]))
check('quartile-found', verify_letters('квартиль', 1.26, q, [X], [Eq(P(X < q), 0.25)]))
text = said(lambda: verify_letters('квартиль', 1.82, q, [X], [Eq(P(X < q), 0.25)]))
check('upper-for-lower-named', '❌' in text and 'other side' in text)
choc = Density({(Rational(1, 2), 3): Rational(6, 85) * (4 + 3 * x - x ** 2)}, 'C')
text = said(lambda: verify_letters('от нуля', 1.31, m, [choc], [Eq(P(choc < m), 0.5)]))
check('from-zero-named', '❌' in text and 'collected from 0' in text)
text = said(lambda: verify_letters('вне', 5.73, m, [choc], [Eq(P(choc < m), 0.5)]))
check('root-outside-named', '❌' in text and 'outside' in text and 'rejected' in text)
steps = Density({(0, 1): x / 2, (1, Rational(5, 2)): Rational(1, 2)}, 'S')
check('median-second-piece', verify_letters('кусок', 1.5, m, [steps], [Eq(P(steps < m), 0.5)]))
text = said(lambda: verify_letters('кусок', 1.41, m, [steps], [Eq(P(steps < m), 0.5)]))
check('one-formula-named', '❌' in text and ('used everywhere' in text or 'another piece' in text))
arc = Density({(0, 1): acos(x)}, 'A')
text = said(lambda: verify_letters('среднее', 0.393, m, [arc], [Eq(P(arc < m), 0.5)]))
check('mean-for-median-named', '❌' in text and 'that is the mean' in text)
tri = Density({(a, c): 2 * (x - a) / ((b - a) * (c - a)), (c, b): 2 * (b - x) / ((b - a) * (b - c))}, 'T')
shapes = [{a: 0, b: 4, c: 3}, {a: 1, b: 3, c: Rational(5, 2)}]
check('median-expression', verify_letters('треугольник', a + sqrt((b - a) * (c - a) / 2), m, [tri],
                                          [Eq(P(tri < m), 0.5)], free=shapes))
text = said(lambda: verify_letters('треугольник', a - sqrt((b - a) * (c - a) / 2), m, [tri],
                                   [Eq(P(tri < m), 0.5)], free=shapes))
check('median-expression-rejected-root', '❌' in text and 'rejected' in text)
d = sp.Symbol('d', positive=True)
med = Eq(P(arc < m), 0.5)
check('around-median', verify_letters('±a', 0.125, d, [arc], [med, Eq(P((arc >= m - d) & (arc <= m + d)), 0.3)]))
expo = Density({(0, oo): 9 * t * exp(-3 * t)}, 'E', var=t)
check('infinite-median', verify_letters('∞', 0.559, m, [expo], [Eq(P(expo < m), 0.5)]))

print('\n=== мода ===')
hump = Density({(0, 1): 12 * x ** 2 * (1 - x)}, 'H')
check('mode-inside', verify_mode('мода', Rational(2, 3), hump))
check('mode-at-end', verify_mode('мода', 2, X))
text = said(lambda: verify_mode('высота', Rational(16, 9), hump))
check('height-for-mode-named', '❌' in text and 'largest value of the density' in text)
text = said(lambda: verify_mode('медиана', float(kit._density_share(hump, {}, 0.5)), hump))
check('median-for-mode-named', '❌' in text and 'that is the median' in text)
check('greater-ok', verify_greater('больше', 'mode', hump))
text = said(lambda: verify_greater('больше', 'median', hump))
check('greater-reason', '❌' in text and 'left of the mode' in text and 'more than a half' in text)
check('greater-not-a-word', verify_greater('слово', 'mean', hump), False)
jump = Density({(3, 9): a * (x - 3) ** 3 + b * (x - 3) ** 2}, 'J')
zero = [Eq(6 * a + b, 0)]
check('mode-with-letters', verify_mode('мода', 7, jump, given=zero, var=[a, b]))

print('\n=== среднее и дисперсия ===')
check('mean-exact', abs(float(sympify(Expect(X))) - 1.5) < 1e-12 and abs(float(sympify(Var(X))) - 0.15) < 1e-12)
check('mean-linear', abs(float(sympify(Expect(2 * X + 1))) - 4) < 1e-12 and abs(float(sympify(Var(2 * X + 1))) - 0.6) < 1e-12)
text = said(lambda: verify_moment('Var', 2.4, Var(X)))
check('square-for-variance-named', '❌' in text and 'E(X²)' in text)
text = said(lambda: verify_moment('E', 2, Expect(X)))
check('no-density-named', '❌' in text and 'no density' in text)
text = said(lambda: verify_moment('E', 1, Expect(X)))
check('midpoint-named', '❌' in text and 'middle of the interval' in text)
uni = Density({(a, 3 * a): 1 / (2 * a)}, 'U')
check('mean-in-terms-of', verify_moment('E(a)', 2 * a, Expect(uni)))
check('variance-in-terms-of', verify_moment('Var(a)', a ** 2 / 3, Var(uni)))
text = said(lambda: verify_moment('Var(a)', 13 * a ** 2 / 3, Var(uni)))
check('square-in-terms-of-named', '❌' in text and 'E(U²)' in text)
timer = Density({(0, 2): 6 / (pi * sqrt(16 - x ** 2))}, 'T')
check('mean-exact-form', verify_moment('точно', 12 * (2 - sqrt(3)) / pi, Expect(timer), exact=True))
text = said(lambda: verify_moment('точно', 1.02, Expect(timer), exact=True))
check('mean-decimal-named', '❌' in text and 'exact value' in text)
arc3 = Density({(0, kp): 3 * x * acos(x ** 2)}, 'X')
check('moment-letters-found', verify_moment('E', 0.456, Expect(arc3), given=[], var=kp))
check('interval-from-moments', verify_chance('μ ± σ', 0.620, P((arc3 > Expect(arc3) - SD(arc3)) &
                                                           (arc3 < Expect(arc3) + SD(arc3))), given=[], var=kp))

print('\n=== событие про другую величину ===')
spend = choc.map(lambda w: Piecewise((25 * w, w < 0.75), (24 * w, True)), 'spend')
check('mapped-event', abs(float(sympify(P(spend <= 48))) - 54 / 85) < 1e-10)
check('mapped-mean', abs(float(sympify(Expect(spend))) - 40.9576516544) < 1e-8)
check('places-ok', verify_moment('цент', 40.96, Expect(spend), places=2))
text = said(lambda: verify_moment('цент', 41.0, Expect(spend), places=2))
check('places-named', '❌' in text and 'decimal places' in text)
clock = Density({(0, 5): Rational(1, 5)}, 'T', var=t)
height = clock.map(lambda s: -0.4 * cos(7.8 * s) + 1.4, 'H')
check('time-share', verify_chance('время', 0.406, P(height > 1.5)))

print('\n=== условная ===')
text = said(lambda: verify_chance('условная', 0.0344, P(jump > 8.52, given=jump > 8), given=zero, var=[a, b]))
check('not-divided-named', '❌' in text and 'not been divided' in text)
check('rounded-letters-remark', verify_chance('3 цифры', 0.263, P(jump > 8.52, given=jump > 8), given=zero, var=[a, b]))
text = said(lambda: verify_chance('высота', 3 * 1.2 ** 2 / 8, P(X < 1.2)))
check('density-value-named', '❌' in text and 'value of the density' in text)
check('blank-answer', verify_chance('пусто', ..., P(X < 1)), False)

print('\n=== первообразной внутри проверки нет ===')
source = open(os.path.join(ROOT, 'practicum', 'kit.py')).read()
start = source.index('# ======================================================= плотность формулой')
end = source.index('\ndef trigger_check(')
section = source[start:end]
tree = ast.parse(section)
check('section-parses', isinstance(tree, ast.Module))
# Ни интеграла sympy, ни решателя уравнений: площадь — квадратура, буквы — Ньютон.
for word in ('integrate', 'Integral', 'solve', 'nsolve', 'scipy', 'numpy', 'mpmath', 'quad_'):
    names = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id.startswith(word)] + \
            [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr.startswith(word)]
    check(f'no-{word}', not names)
quad = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_gauss_piece')
check('quadrature-is-gauss', '_GAUSS' in ast.unparse(quad))

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
