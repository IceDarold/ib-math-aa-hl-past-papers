"""Проверяет механику нормального распределения: Normal, Mix, map и проверки D5.

verify_d5 сверяет ответы одного практикума, а здесь сверяется сама
проверка: что площадь под кривой сходится с функцией ошибок до десятого
знака; что буквы модели она находит сама — одну, две, три — и отбрасывает
решение с отрицательным σ, называя его; что событие над величиной,
посчитанной из Z, сворачивается в правильный интервал; что смесь
складывается по частям; что правило из условия заменяет кривую; что
значащие цифры и проценты разбираются с именем; что пустой ответ не
роняет ячейку.

Главное свойство секции: вероятность — площадь, и больше ничего. Функция
ошибок и обратная нормальная в тесте есть (statistics.NormalDist), а в
проверке — нет. Последний раздел проверяет это по коду.

Запуск:  python practicum/tests/test_kit_normal.py
"""
import ast
import io
import os
import sys
from contextlib import redirect_stdout
from statistics import NormalDist

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
s, m, w, a, b = sp.symbols('s m w a b')

print('=== площадь под кривой ===')
cases = [(1000, 3.5, None, 995), (204, 5, 210, None), (175, 8, 170, 185),
         (0, 1, -1.25, -1), (10, 2, 13, None), (62, 2.9, None, 61), (0, 1, 3, None)]
worst = 0.0
for mean, spread, lo, hi in cases:
    X = Normal(mean, spread ** 2)
    event = (X > lo) & (X < hi) if lo is not None and hi is not None else (
        X > lo if lo is not None else X < hi)
    got = float(sympify(P(event)))
    curve = NormalDist(mean, spread)
    want = (curve.cdf(hi) if hi is not None else 1.0) - (curve.cdf(lo) if lo is not None else 0.0)
    worst = max(worst, abs(got - want) / want)
check('area-matches-erf', worst < 1e-9)
print(f'   наибольшее относительное расхождение с функцией ошибок: {worst:.1e}')
X = Normal(50, 16)
check('le-equals-lt', float(sympify(P(X <= 53))) == float(sympify(P(X < 53))))
check('point-has-no-area', float(sympify(P(X == 53))) == 0.0)
check('total-is-one', abs(float(sympify(P((X < 40) | (X >= 40)))) - 1) < 1e-12)
check('not-is-complement', abs(float(sympify(P(~(X > 55)))) - NormalDist(50, 4).cdf(55)) < 1e-12)
check('variance-not-sd', abs(float(sympify(P(Normal(0, 4) < 2))) - NormalDist(0, 2).cdf(2)) < 1e-12)
check('blank-model', P(Normal(..., 4) < 1) is Ellipsis)
try:
    Normal(3, -1)
    check('negative-variance-raises', False)
except ValueError:
    check('negative-variance-raises', True)
try:
    P(X + Normal(1, 1) < 3)
    check('sum-of-curves-raises', False)
except TypeError:
    check('sum-of-curves-raises', True)
try:
    P(X < Normal(1, 1, 'Y'))
    check('two-curves-raise', False)
except ValueError:
    check('two-curves-raise', True)

print('\n=== площадь с буквами — выражение, с числами — число ===')
T = Normal(75, s ** 2, 'T')
area = sympify(P(T > 82))
check('letters-stay', bool(area.free_symbols == {s}))
check('numbers-evaluate', abs(float(area.subs(s, 3.408401)) - 0.02) < 1e-6)

print('\n=== буквы модели ===')
two = [Eq(P(T > 82), 0.02)]
check('sigma-found', verify_letters('σ', 3.41, s, [T], two))
text = said(lambda: verify_letters('−σ', -3.41, s, [T], two))
check('negative-root-named', '❌' in text and 'standard deviation is positive' in text)
text = said(lambda: verify_letters('2 цифры', 3.4, s, [T], two))
check('two-figures-named', 'two significant figures' in text)
text = said(lambda: verify_letters('мимо', 3.9, s, [T], two))
check('wrong-sigma', '❌' in text)
H = Normal(m, s ** 2, 'H')
wheat = [Eq(P(H < 94.6), 0.288), Eq(P(H > 98.1), 0.434)]
check('two-letters', verify_letters('μ, σ', [97.3, 4.82], [m, s], [H], wheat))
check('two-letters-swapped', verify_letters('σ, μ', [4.82, 97.3], [m, s], [H], wheat), False)
check('fewer-conditions', verify_letters('мало', 97.3, m, [H], wheat[:1]), False)
Q1, Q3 = sp.symbols('Q1 Q3')
D = Normal(32, s ** 2, 'D')
check('three-letters', verify_letters('IQR', 0.208, s, [D],
                                      [Eq(P(D < Q1), 0.25), Eq(P(D < Q3), 0.75), Eq(Q3 - Q1, 0.28)]))
W = Normal(175, 64, 'W')
check('four-figures', verify_letters('4 цифры', 181.7, w, [W], [Eq(P(W > w), 0.2)], sf=4))
text = said(lambda: verify_letters('5 цифр', 181.73, w, [W], [Eq(P(W > w), 0.2)], sf=4))
check('too-many-figures-named', 'asks for 4 significant figures' in text)
text = said(lambda: verify_letters('хвост', 168.3, w, [W], [Eq(P(W > w), 0.2)], sf=4))
check('wrong-tail-named', '❌' in text and 'other side of the boundary' in text)
Xa, Ya = Normal(7, a ** 2, 'X'), Normal(19, a ** 2, 'Y')
check('free-letter', verify_letters('свободная a', 10, b, [Xa, Ya], [Eq(P(Xa > b), P(Ya > 22))], free=a))
check('free-letter-wrong', verify_letters('свободная a', 4, b, [Xa, Ya],
                                          [Eq(P(Xa > b), P(Ya > 22))], free=a), False)
# далёкий хвост: невязка мала и там, где обе площади почти нули, — корнем это не считается
roots = kit._curve_roots([sympify(P(Normal(7, 0.25, 'X') > b)) - sympify(P(Normal(19, 0.25, 'Y') > 22))],
                         [b], [])
check('no-flat-tail-roots', len(roots) == 1 and abs(float(roots[0][b]) - 10) < 1e-6)

print('\n=== ответ-вероятность ===')
bags = Normal(1000, 3.5 ** 2)
check('area-ok', verify_chance('площадь', 0.0766, P(bags < 995)))
for name, value, words in [
        ('opposite', 0.923, 'opposite event'),
        ('variance-as-sd', float(sympify(P(Normal(1000, 3.5 ** 4) < 995))), 'is the variance'),
        ('height', NormalDist(1000, 3.5).pdf(995), 'height of the curve'),
        ('both-tails', 2 * 0.0765637, 'both tails'),
        ('half-curve', 0.5 - 0.0765637, 'from the mean to the boundary'),  # для P(X < 1005)
        ('two-figures', 0.077, 'two significant figures')]:
    event = bags < (1005 if name == 'half-curve' else 995)
    text = said(lambda: verify_chance(name, value, P(event)))
    check(name, '❌' in text and words in text)
text = said(lambda: verify_chance('процент', 7.66, P(bags < 995)))
check('percent-accepted-with-remark', '✅' in text and 'accepts it' in text)
rice = Normal(175, 64, 'W')
text = said(lambda: verify_chance('доля', 0.628, P((rice > 170) & (rice < 185)), percent=True))
check('probability-for-percent', '❌' in text and 'asks for a percentage' in text)
text = said(lambda: verify_chance('граница', 73.4, P((rice > 170) & (rice < 185)), percent=True))
check('lost-boundary', '❌' in text and 'is lost' in text)
text = said(lambda: verify_chance('условная', 0.0766, P(bags > 1005, given=bags >= 995)))
check('not-divided', 'not been divided' in text)
check('conditional-ok', verify_chance('условная', 0.0829, P(bags > 1005, given=bags >= 995)))
check('given-letters', verify_chance('σ из условия', 0.0712, P(T > 80), given=two, var=s))
check('rounded-letter-remark', verify_chance('σ = 3.4', float(sympify(P(Normal(75, 3.41 ** 2) > 80))) * 1.0,
                                             P(T > 80), given=two, var=s))
check('blank-answer', verify_chance('пусто', ..., P(bags < 995)), False)

print('\n=== правило из условия ===')
ruled = Normal(100, 400, 'E', rule={2: 0.95})
check('rule-area', abs(float(sympify(P(ruled > 140))) - 0.025) < 1e-15)
check('rule-at-mean', abs(float(sympify(P(ruled < 100))) - 0.5) < 1e-15)
text = said(lambda: verify_chance('кривая', 2.28, P(ruled > 140), percent=True))
check('exact-curve-named', 'rule it gives' in text)
try:
    P(ruled > 130)
    check('rule-refuses-other-boundary', False)
except ValueError:
    check('rule-refuses-other-boundary', True)

print('\n=== смесь ===')
C, B = Normal(62, 2.9 ** 2, 'C'), Normal(68, 3.4 ** 2, 'B')
muffin = Mix({C: 0.6, B: 0.4}, 'muffin')
mixed = 0.6 * NormalDist(62, 2.9).cdf(61) + 0.4 * NormalDist(68, 3.4).cdf(61)
check('mixture-area', abs(float(sympify(P(muffin < 61))) - mixed) < 1e-12)
check('mixture-bayes', abs(float(sympify(P(muffin.came_from(C), given=muffin < 61)))
                           - 0.6 * NormalDist(62, 2.9).cdf(61) / mixed) < 1e-12)
check('part-share', float(sympify(P(muffin.came_from(B)))) == 0.4)
text = said(lambda: verify_chance('одна часть', 0.365, P(muffin < 61)))
check('one-part-named', 'only' in text and 'other part' in text)
try:
    Mix({C: 0.6, B: 0.3})
    check('shares-must-add', False)
except ValueError:
    check('shares-must-add', True)
sigma = sp.Symbol('sigma')
adjusted = Normal(62, sigma ** 2, 'C')
check('mixture-letter', verify_letters('σ смеси', 1.47, sigma, [adjusted],
                                       [Eq(P(Mix({adjusted: 0.6, B: 0.4}) < 61), 0.157)]))

print('\n=== величина, посчитанная из Z ===')
Z = Normal(0, 1, 'Z')
X1 = Z.map(lambda z: -z - sqrt(z ** 2 - 1), 'X1')
X2 = Z.map(lambda z: -z + sqrt(z ** 2 - 1), 'X2')
check('mapped-real-roots', abs(float(sympify(P(X1 < X2))) - 2 * NormalDist().cdf(-1)) < 1e-10)
both = NormalDist().cdf(-1) - NormalDist().cdf(-1.25)
check('mapped-interval', abs(float(sympify(P((X1 > 0.5) & (X2 > 0.5)))) - both) < 1e-10)
check('mapped-undefined-is-false', X1.at(0.3) is None and abs(X1.at(-2) - (2 - 3 ** 0.5)) < 1e-12)
cube = Z.map(lambda z: z ** 3, 'C')
check('mapped-monotone', abs(float(sympify(P(cube < 8))) - NormalDist().cdf(2)) < 1e-10)

print('\n=== SD и оценка числа ===')
data = Freq({Interval.Lopen(15, 20): 31, Interval.Lopen(20, 25): 42, Interval.Lopen(25, 30): 61,
             Interval.Lopen(30, 35): 46, Interval.Lopen(35, 40): 29}, 'y')
check('interval-midpoints', sp.sympify(Expect(data)) == Rational(55, 2))
check('sd-ok', verify_moment('SD', 6.26, SD(data)))
text = said(lambda: verify_moment('n − 1', 6.28, SD(data)))
check('sample-sd-named', 'n − 1' in text)
check('count-whole', verify_moment('8 мешков', 8, Expect(Bin(100, P(bags < 995))), count=True))
check('count-not-by-default', verify_moment('8 мешков', 8, Expect(Bin(100, P(bags < 995)))), False)

print('\n=== формул темы внутри проверки нет ===')
source = open(os.path.join(ROOT, 'practicum', 'kit', 'normal.py')).read()
start = source.index('# ================================================== нормальное распределение')
section = source[start:]
tree = ast.parse(section)
check('section-parses', isinstance(tree, ast.Module))
# Ни функции ошибок, ни обратной нормальной, ни таблиц z.
# Имя сравнивается с началом: OverflowError содержит «erf», но функцией ошибок не является.
for word in ('erf', 'NormalDist', 'inv_cdf', 'ndtr', 'invNorm', 'norm', 'scipy', 'numpy'):
    names = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id.startswith(word)] + \
            [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr.startswith(word)]
    check(f'no-{word}', not names)
# Площадь — сумма значений кривой exp(−(x − μ)²/(2σ²)) в узлах, и больше нигде exp не зовётся.
calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
         and n.func.attr == 'exp']
check('exp-only-for-the-curve', len(calls) == 2)
bell = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_bell_area')
check('bell-sums-curve', '(point - mean) ** 2 / twice' in ast.unparse(bell))

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
