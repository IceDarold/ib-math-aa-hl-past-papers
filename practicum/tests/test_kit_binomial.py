"""Проверяет механику биномиального распределения: Bin, P и четыре проверки.

Отдельный тест нужен по той же причине, что у прогрессий и фигур:
verify_d3 сверяет ответы одного практикума, а здесь сверяется сама
проверка — что она принимает верное число в любой записи, называет
сдвинутую границу, не путает накопленную вероятность с точечной и не
падает на пустом ответе.

Главное свойство, ради которого секция так устроена: проверка знает
только вероятность одного значения, P(X = k). «Не больше шести» она
складывает, среднее получает суммой k·P(X = k), дисперсию — суммой
квадратов отклонений, наименьшее n — перебором. Ни np, ни np(1 − p),
ни 1 − (1 − p)ⁿ внутри нет, и последний раздел это проверяет по коду.

Запуск:  python practicum/tests/test_kit_binomial.py
"""
import ast
import io
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

p = Symbol('p')
ok, bad = [], []


def t(name, got, expect=True):
    (ok if got == expect else bad).append(name)


def said(call):
    """Что проверка напечатала: нужно, чтобы убедиться, что промах назван."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        call()
    text = buffer.getvalue()
    print(text, end='')
    return text


print('=== распределение складывается по значениям ===')
X = Bin(4, Rational(1, 2))
t('pmf', P(X == 2).expr == Rational(3, 8))
t('cdf', sp.sympify(P(X <= 1)) == Rational(5, 16))
t('whole', sp.sympify(P(X >= 0)) == 1)
t('strict', sp.sympify(P(X < 1)) == Rational(1, 16))
t('not', sp.sympify(P(X != 2)) == Rational(5, 8))
t('and', sp.sympify(P((X >= 1) & (X <= 2))) == Rational(5, 8))
t('given', sp.sympify(P(X == 2, given=X >= 1)) == Rational(6, 15))
t('gdc-pdf', abs(binompdf(31, 0.2, 10) - 0.0418894354877) < 1e-10)
t('gdc-cdf', abs(binomcdf(31, 0.2, 9) - 0.925400130586) < 1e-10)
t('gdc-casio', abs(binomcdf(31, 0.2, 10, 31) - 0.0745998694137) < 1e-10)
Y, Z = Bin(2, Rational(1, 2), 'Y'), Bin(1, Rational(1, 3), 'Z')
t('two-variables', sp.sympify(P((Y >= 1) ^ (Z >= 1))) ==
  Rational(3, 4) * Rational(2, 3) + Rational(1, 4) * Rational(1, 3))
t('mean', sp.sympify(Expect(Bin(10, Rational(3, 10)))) == 3)
t('variance', sp.sympify(Var(Bin(10, Rational(3, 10)))) == Rational(21, 10))
t('variance-linear', sp.sympify(Var(1 - 2 * Bin(10, Rational(3, 10)))) == Rational(42, 5))
t('mean-linear', sp.sympify(Expect(3 * Bin(10, Rational(3, 10)) + 1)) == 10)
t('variance-letter', sp.expand(sp.sympify(Var(Bin(25, p))) - 25 * p * (1 - p)) == 0)
t('nested', abs(float(sp.sympify(P(Bin(10, P(Bin(40, 0.6283647) >= 30)) == 4)))
                - 0.0039441399) < 1e-8)
t('repr', repr(1 - 2 * Bin(25, p)) == '1 - 2X' and repr(P(X < 3)) == 'P(X < 3)')

print('\n=== верный ответ в любой записи ===')
lamps = Bin(30, 0.05, 'D')
t('three-sf', verify_binomial('хотя бы одна', 0.785, P(lamps >= 1)))
t('more-digits', verify_binomial('больше цифр', 0.78536, P(lamps >= 1)))
t('expression', verify_binomial('выражением', 1 - 0.95 ** 30, P(lamps >= 1)))
t('gdc-call', verify_binomial('кнопкой', 1 - binomcdf(30, 0.05, 0), P(lamps >= 1)))
t('exact', verify_binomial('дробью', Rational(15, 16), P(X >= 1)))
t('prob-object', verify_binomial('самим P', P(lamps >= 1), P(lamps >= 1)))
t('conditional', verify_binomial('условная', 0.761, P(lamps <= 2, given=lamps >= 1)))
wheat = Bin(100, 0.434)
t('small', verify_binomial('малая вероятность', 0.0133, P(wheat == 34)))
t('small-cond', verify_binomial('малая условная', 0.0157,
                                P(wheat == 34, given=wheat < 49)))

print('\n=== промахи называются ===')
text = said(lambda: t('boundary-gt', verify_binomial(
    'больше шести', 1 - binomcdf(64, 0.071193, 5), P(Bin(64, 0.071193) > 6)), False))
t('boundary-gt-named', 'начинается' in text or 'starts' in text)
text = said(lambda: t('boundary-ge', verify_binomial(
    'хотя бы десять', 1 - binomcdf(31, 0.2, 10), P(Bin(31, 0.2) >= 10)), False))
t('boundary-ge-named', 'включает' in text or 'includes' in text)
text = said(lambda: t('boundary-cond', verify_binomial(
    'меньше 49 в условии', 0.0133199 / 0.890474, P(wheat == 34, given=wheat < 49)), False))
t('boundary-cond-named', 'в условии' in text or 'in the condition' in text)
text = said(lambda: t('cdf-for-pdf', verify_binomial(
    'ровно десять', binomcdf(31, 0.2, 10), P(Bin(31, 0.2) == 10)), False))
t('cdf-for-pdf-named', 'cdf' in text)
text = said(lambda: t('swap', verify_binomial(
    'p и 1 − p', binompdf(31, 0.8, 10), P(Bin(31, 0.2) == 10)), False))
t('swap-named', '1 − p' in text)
text = said(lambda: t('opposite', verify_binomial(
    'противоположное', 0.215, P(lamps >= 1)), False))
t('opposite-named', 'противоположного' in text or 'opposite' in text)
text = said(lambda: t('backwards', verify_binomial(
    'наоборот', 0.761, P(lamps >= 1, given=lamps <= 2)), False))
t('backwards-named', 'обратную' in text or 'wrong way' in text)
text = said(lambda: t('not-divided', verify_binomial(
    'не поделили', 0.597540, P(lamps <= 2, given=lamps >= 1)), False))
t('not-divided-named', 'пересечения' in text or 'intersection' in text)
javelin = P((Bin(5, 0.1216725, 'R') >= 1) ^ (Bin(5, 0.0824333, 'S') >= 1))
text = said(lambda: t('xor-union', verify_binomial(
    'хотя бы один', 1 - 0.522736 * 0.650412, javelin), False))
t('xor-union-named', 'оба' in text or 'both' in text)
text = said(lambda: t('two-sf', verify_binomial('две цифры', 0.042,
                                                P(Bin(31, 0.2) == 10)), False))
t('two-sf-named', 'две значащие' in text or 'two significant' in text)
t('above-one', verify_binomial('больше единицы', 1.03, P(lamps >= 1)), False)
t('rounded-accepted', verify_binomial(
    'от округлённого', 0.00395134, P(Bin(10, P(Bin(40, 0.6283647) >= 30)) == 4)))
t('rounded-not-wrong', verify_binomial(
    'но не что угодно', 0.0036, P(Bin(10, P(Bin(40, 0.6283647) >= 30)) == 4)), False)
t('not-an-event', verify_binomial('не событие', 0.5, 0.5), False)
text = said(lambda: t('one-trial', verify_binomial('одно испытание', 0.0849,
                                                   P(Bin(10, 0.0849303) == 1)), False))
t('one-trial-named', 'одного испытания' in text or 'single trial' in text)
apples = Bin(40, 0.628364)
text = said(lambda: t('inner-p', verify_binomial('p яблока снаружи', 0.0863,
                                                 P(Bin(10, P(apples >= 30)) == 4)), False))
t('inner-p-named', 'внутренн' in text or 'inner' in text)

print('\n=== среднее и дисперсия ===')
flights = Bin(64, 0.0711930)
t('mean-ok', verify_moment('среднее', 4.56, Expect(flights)))
text = said(lambda: t('mean-failures', verify_moment('неудачи', 59.44, Expect(flights)), False))
t('mean-failures-named', 'неудач' in text or 'failures' in text)
t('mean-p', verify_moment('вероятность', 0.0712, Expect(flights)), False)
text = said(lambda: t('mean-whole', verify_moment('до целого', 5, Expect(flights)), False))
t('mean-whole-named', 'целого' in text or 'whole number' in text)
condition = Eq(Var(Bin(25, p)), 5.75)
t('var-given', verify_moment('дисперсия 1 − 2X', 23, Var(1 - 2 * Bin(25, p)),
                             given=condition, var=p))
text = said(lambda: t('var-square', verify_moment('не в квадрате', 11.5,
                                                  Var(1 - 2 * Bin(25, p)),
                                                  given=condition, var=p), False))
t('var-square-named', 'квадрат' in text or 'squared' in text)
text = said(lambda: t('var-shift', verify_moment('со сдвигом', 24, Var(1 - 2 * Bin(25, p)),
                                                 given=condition, var=p), False))
t('var-shift-named', 'постоянная' in text or 'constant' in text)
t('var-negative', verify_moment('отрицательная', -11.5, Var(1 - 2 * Bin(25, p)),
                                given=condition, var=p), False)
t('var-mean', verify_moment('это среднее', 3, Var(Bin(10, Rational(3, 10)))), False)
t('var-sd', verify_moment('это отклонение', sqrt(2.1), Var(Bin(10, Rational(3, 10)))), False)

print('\n=== буква вместо p ===')
t('param', verify_parameter('оба p', [0.641, 0.359], condition, p))
t('param-exact', verify_parameter('точно', [Rational(1, 2) + sqrt(Rational(2, 100)),
                                           Rational(1, 2) - sqrt(Rational(2, 100))],
                                  condition, p))
text = said(lambda: t('param-missing', verify_parameter('один', [0.641], condition, p), False))
t('param-missing-named', '1 − p' in text)
t('param-wrong', verify_parameter('мимо', [0.641, 0.3], condition, p), False)
t('param-outside', verify_parameter('больше единицы', [0.641, 1.359], condition, p), False)

print('\n=== число испытаний ===')
grow = lambda n: P(Bin(n, 0.25) >= 1)
t('least', verify_trials('наименьшее', 17, grow, holds=lambda v: v > 0.99))
text = said(lambda: t('least-short', verify_trials('на одно меньше', 16, grow,
                                                  holds=lambda v: v > 0.99), False))
t('least-short-says-value', '0.989977' in text)
t('least-long', verify_trials('на одно больше', 18, grow, holds=lambda v: v > 0.99), False)
t('least-fraction', verify_trials('граница из логарифма', 16.0078, grow,
                                  holds=lambda v: v > 0.99), False)
shrink = lambda n: P(Bin(n, 0.08) <= 6)
t('near', verify_trials('приблизительно', 94, shrink, near=0.367))
t('near-neighbour', verify_trials('соседнее', 93, shrink, near=0.367), False)

print('\n=== пустые ответы ===')
t('blank-answer', verify_binomial('пустой', ..., P(lamps >= 1)), False)
t('blank-model', P(Bin(10, ...) == 3) is Ellipsis)
t('blank-gdc', binompdf(10, ..., 3) is Ellipsis and binomcdf(..., 0.2, 3) is Ellipsis)
t('blank-moment', Var(Bin(3, ...)) is Ellipsis and Expect(Bin(..., 0.5)) is Ellipsis)
t('blank-find', verify_binomial('пустая модель', 0.5, P(Bin(10, ...) == 3)), False)
t('blank-trials', verify_trials('пустое n', ..., grow, holds=lambda v: v > 0.99), False)
t('blank-trials-model', verify_trials('пустая модель', 17,
                                      lambda n: P(Bin(n, ...) >= 1),
                                      holds=lambda v: v > 0.99), False)
t('blank-param', verify_parameter('пустые p', [..., ...], condition, p), False)
t('blank-moment-answer', verify_moment('пустое среднее', ..., Expect(flights)), False)

print('\n=== формул темы внутри проверки нет ===')
# Смотреть надо на код, а не на текст: в документации np и np(1 − p)
# как раз названы — там сказано, что проверка их не использует.
source = open(os.path.join(ROOT, 'practicum', 'kit', 'distribution.py')).read()
tree = ast.parse(source)
names = {'_Trials', 'Bin', '_Linear', '_as_linear', '_Draw', '_draw_say',
         '_draw_vars', '_draw_holds', '_draw_blank', '_draw_chance', '_draw_mass',
         '_DrawSpace', '_draw_prob', '_draw_leaves', '_draw_swap', '_draw_value',
         '_boundary_words', '_draw_slips', '_chance_answer', '_draw_agree',
         'verify_binomial', '_moment', 'Expect', 'Var', 'binompdf', 'binomcdf',
         '_draw_roots', 'verify_parameter', 'verify_moment', 'verify_trials'}


def body_of(node):
    stripped = list(node.body)
    if (stripped and isinstance(stripped[0], ast.Expr)
            and isinstance(stripped[0].value, ast.Constant)
            and isinstance(stripped[0].value.value, str)):
        stripped = stripped[1:]
    return stripped


bodies, chance = {}, None
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
        if isinstance(node, ast.ClassDef):
            for inner in node.body:
                if isinstance(inner, ast.FunctionDef) and inner.name == 'chance':
                    chance = inner
                    continue
                if isinstance(inner, ast.FunctionDef):
                    bodies[f'{node.name}.{inner.name}'] = '\n'.join(
                        ast.unparse(line) for line in body_of(inner))
            bodies.setdefault(node.name, '')
        else:
            bodies[node.name] = '\n'.join(ast.unparse(line) for line in body_of(node))
found = {name.split('.')[0] for name in bodies}
t('all-found', found == names and chance is not None)

# p возводится в степень ровно в одном месте — в вероятности одного значения.
# Степень p в любом другом месте и есть формула: (1 − p)ⁿ, p^k вне суммы.
chance_code = '\n'.join(ast.unparse(line) for line in body_of(chance))
t('chance-is-the-definition', 'binomial(self.n, k)' in chance_code
  and 'p ** k' in chance_code)
code = '\n'.join(bodies.values())
t('no-np', all(text not in code for text in (
    '.n * var.p', 'n * p', '.n * self.p', 'var.n *', '* var.n')))
t('no-power-of-p', all(text not in code for text in (
    'p) **', 'p **', '.p **')))
t('no-least-by-log', 'log(' not in code)
# Наименьшее n находит перебор, а не неравенство: цикл по числу испытаний.
t('trials-walk', 'for i in range(1, limit + 1)' in bodies['verify_trials'])
# Вероятность события — сумма по значениям, при которых оно выполняется.
t('mass-adds', 'running = running + weight' in bodies['_draw_mass'])
# Среднее и дисперсия — суммы по значениям X, а не произведения n и p.
t('moment-sums', 'for k in var.values()' in bodies['_moment'])

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
