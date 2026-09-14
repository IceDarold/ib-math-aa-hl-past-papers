"""Проверяет механику таблицы распределения: Dist, Freq, Geo, Moments и проверки D4.

verify_d4 сверяет ответы одного практикума, а здесь сверяется сама
проверка: что она находит буквы таблицы сама, отбрасывает корни, при
которых клетка перестаёт быть вероятностью, и называет клетку; что
диапазон буквы строится из всех клеток вместе; что производящая функция
сверяется по коэффициентам; что пустой ответ не роняет ячейку.

Главное свойство секции: эталона нет нигде. Буквы — решения собственных
правил таблицы и условий вопроса, среднее и дисперсия — суммы по
значениям, ряд первого успеха складывает sympy. Последний раздел
проверяет по коду, что формул темы (1/p, (1 − p)/p², a²Var) внутри нет.

Запуск:  python practicum/tests/test_kit_table.py
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


k, a, b, p, q, r = sp.symbols('k a b p q r')

print('=== таблица складывается по значениям ===')
X = Dist({1: 0.2, 2: 0.5, 3: 0.3})
check('exact-cells', X.chance(2) == Rational(1, 2))
check('mean', sp.sympify(Expect(X)) == Rational(21, 10))
check('var', sp.sympify(Var(X)) == Rational(49, 100))
check('linear', sp.sympify(Var(5 - 2 * X)) == Rational(49, 25))
check('event', sp.sympify(P(X >= 2)) == Rational(4, 5))
F = Freq({0: 6, 1: 16, 2: 13, 3: 2, 4: 3})
check('freq-size', F.size == 40)
check('freq-mean', sp.sympify(Expect(F)) == Rational(3, 2))
M = Dist({(i, j): Rational(1, 16) for i in range(1, 5) for j in range(1, 5)}, 'M', rule=max)
check('rule', [M.chance(m) for m in range(1, 5)] == [Rational(n, 16) for n in (1, 3, 5, 7)])
two = Dist({0: Rational(1, 2), 1: Rational(1, 2)}) + Dist({0: Rational(1, 2), 1: Rational(1, 2)})
check('sum-convolves', [two.chance(v) for v in range(3)] == [Rational(1, 4), Rational(1, 2), Rational(1, 4)])
T = Moments(4.723, 0.906)
check('stand-in-mean', sp.sympify(Expect(100 - 20 * T)) == 100 - 20 * Rational(4723, 1000))
check('stand-in-var', sp.sympify(Var(100 - 20 * T)) == 400 * Rational(906, 1000))
G = Geo(Rational(1, 10))
check('geo-mean', sp.sympify(Expect(G)) == 10)
check('geo-var', sp.sympify(Var(G)) == 90)
check('geo-symbolic', sp.simplify(sp.sympify(Expect(Geo(p))) - 1 / p) == 0)
check('pgf', sp.expand(Pgf(M, t) - (t + 3 * t ** 2 + 5 * t ** 3 + 7 * t ** 4) / 16) == 0)
Y1, Y2 = Dist({1: 0.5, 2: 0.5}, 'A'), Dist({1: 0.5, 2: 0.5}, 'B')
check('two-variables', sp.sympify(P(Y1 < Y2)) == Rational(1, 4))

print('\n=== буквы таблицы ===')
table = Dist({0: 0.41, 1: k - 0.28, 2: 0.46, 3: 0.29 - 2 * k ** 2})
check('letter-ok', verify_letters('k', 0.3, k, [table]))
text = said(lambda: check('letter-rejected', verify_letters('k отброшен', 0.2, k, [table]), False))
check('letter-rejected-names-cell', 'P(X = 1)' in text and '-0.08' in text)
text = said(lambda: check('letter-sum', verify_letters('сумма', 0.5, k, [table]), False))
check('letter-sum-says', '0.88' in text)
cubic = Dist({1: k, 2: k ** 2, 3: a, 4: k ** 3})
check('cubic', verify_letters('кубическое', 0.553, a, [cubic], [Eq(Expect(cubic), 2.3)]))
text = said(lambda: check('cubic-other-root', verify_letters('другой корень', 2.44587, a, [cubic],
                                                           [Eq(Expect(cubic), 2.3)]), False))
check('cubic-other-root-named', '-1.185' in text)
check('cubic-2sf', verify_letters('две цифры', 0.55, a, [cubic], [Eq(Expect(cubic), 2.3)]), False)
pq = sp.symbols('m n', positive=True, integer=True)
quiz = Freq({20: 12, 35: pq[1], pq[0]: 8})
check('freq-letters', verify_letters('частоты', [45, 5], list(pq), [quiz],
                                 [Eq(Expect(quiz), 31), Eq(Var(quiz), 124)]))
text = said(lambda: check('freq-negative', verify_letters('отрицательное', [-10, 115], list(pq), [quiz],
                                                      [Eq(Expect(quiz), 31), Eq(Var(quiz), 124)]),
                        False))
check('freq-negative-named', 'положительное' in text or 'positive' in text)
aa, bb = sp.symbols('a b', positive=True)
score = [Eq(Expect(aa - bb * T), 100), Eq(aa - 2.25 * bb, 150)]
check('whole', verify_letters('до целого', [195, 20], [aa, bb], [T], score, whole=True))
check('whole-not-rounded', verify_letters('не округлено', [195.491, 20.2183], [aa, bb], [T], score,
                                      whole=True), False)
dieX = Dist({1: p, 2: p, 3: p, 4: p / 2}, 'X')
dieY = Dist({1: q, 2: q, 3: q, 4: r}, 'Y')
game = [Eq(P(dieX < dieY), Rational(1, 2))]
check('two-tables', verify_letters('две таблицы', [Rational(5, 24), Rational(3, 8)], [q, r],
                               [dieX, dieY], game))
check('blank-letters', verify_letters('пусто', ..., k, [table]), False)
check('underdetermined', verify_letters('мало условий', 0.1, q, [dieY]), False)

print('\n=== диапазоны ===')
check('range-r', verify_table_range('r', Interval(0, 1), r, [dieY]))
check('range-q', verify_table_range('q', Interval(0, Rational(1, 3)), q, [dieY]))
check('range-q-relational', verify_table_range('q неравенством', (q >= 0) & (q <= Rational(1, 3)), q, [dieY]))
text = said(lambda: check('range-loose', verify_table_range('без суммы', Interval(0, 1), q, [dieY]), False))
check('range-loose-says', 'add up' in text or 'складываются' in text)
text = said(lambda: check('range-open', verify_table_range('выколото', Interval.open(0, Rational(1, 3)),
                                                      q, [dieY]), False))
check('range-open-says', 'ends' in text or 'концы' in text)
check('range-mean', verify_table_range('E(Y)', Interval(2, 4), Expect(dieY), [dieY]))
check('range-mean-wrong', verify_table_range('E(Y) не так', Interval(2, 3), Expect(dieY), [dieY]), False)
three = Dist({1: 0.6 - 2 * a, 2: 3 * a, 3: 0.4 - a})
check('range-decimal', verify_table_range('0.3', Interval(0, 0.3), a, [three]))
text = said(lambda: check('range-witness', verify_table_range('до 0.4', Interval(0, 0.4), a, [three]), False))
check('range-witness-cell', 'P(X = 1)' in text)

print('\n=== среднее, дисперсия, мода ===')
check('mean-letters', verify_moment('E', 1.27, Expect(table), given=[], var=k))
text = said(lambda: check('mean-unweighted', verify_moment('без весов', 1.5, Expect(table),
                                                       given=[], var=k), False))
check('mean-unweighted-named', 'weights' in text or 'весов' in text)
check('var-linear', verify_moment('Var(2 − X)', 0.4, Var(2 - three), given=Eq(a, 0.2), var=a))
text = said(lambda: check('var-square-mean', verify_moment('E(X²)', 4.4, Var(2 - three),
                                                       given=Eq(a, 0.2), var=a), False))
check('var-square-mean-named', 'E(X²)' in text)
check('var-letters', verify_moment('Var(P)', 370, Var(aa - bb * T), given=score, var=[aa, bb]))
text = said(lambda: check('var-rounded-letter', verify_moment('b = 20', 362, Var(aa - bb * T),
                                                          given=score, var=[aa, bb])))
check('var-rounded-letter-remark', 'rounded' in text or 'округлённым' in text)
check('var-unsquared', verify_moment('b не в квадрате', 18.3, Var(aa - bb * T), given=score,
                                 var=[aa, bb]), False)
check('mean-two-tables', verify_moment('E(Y)', Rational(11, 4), Expect(dieY), given=game,
                                   var=[p, q, r], tables=[dieX]))
check('mode', verify_mode('мода', 2, Dist({1: 0.2, 2: 0.5, 3: 0.3})))
check('mode-probability', verify_mode('мода-вероятность', 0.5, Dist({1: 0.2, 2: 0.5, 3: 0.3})), False)
check('geo-sum', verify_moment('ряд', Sum(x * p * (1 - p) ** (x - 1), (x, 1, oo)), Expect(Geo(p))))
check('geo-closed', verify_moment('1/p', 1 / p, Expect(Geo(p))))
check('geo-no-weight', verify_moment('без x', Sum(p * (1 - p) ** (x - 1), (x, 1, oo)), Expect(Geo(p))),
  False)
same = Eq(Expect(Geo(p)), 2.5104)
check('geo-letter', verify_letters('p', 0.398, p, [Geo(p)], [same]))
check('geo-var-given', verify_moment('Var', 3.79, Var(Geo(p)), given=same, var=p))

print('\n=== производящая функция ===')
reds = Dist({(i, j): Rational(1, 20) for i in range(5) for j in range(5) if i != j}, 'X',
            rule=lambda o: ('RRYYY'[o[0]] == 'R') + ('RRYYY'[o[1]] == 'R'))
check('pgf-ok', verify_pgf('G', Rational(3, 10) + Rational(3, 5) * t + Rational(1, 10) * t ** 2, reds, t))
check('pgf-decimal', verify_pgf('G десятичными', 0.3 + 0.6 * t + 0.1 * t ** 2, reds, t))
text = said(lambda: check('pgf-reversed', verify_pgf('обратно', 0.1 + 0.6 * t + 0.3 * t ** 2, reds, t),
                        False))
check('pgf-reversed-named', 'reverse' in text or 'обратном' in text)
check('pgf-shifted', verify_pgf('сдвиг', 0.3 * t + 0.6 * t ** 2 + 0.1 * t ** 3, reds, t), False)
check('pgf-not-one', verify_pgf('не единица', 0.3 + 0.5 * t + 0.1 * t ** 2, reds, t), False)
coinY = Dist(Dist({0: Rational(1, 2), 1: Rational(1, 2)}) + Dist({0: 1 - p, 1: p}), 'Y')
top = Eq(P(coinY == 2), Rational(1, 3))
check('pgf-given', verify_pgf('G_Y', Rational(1, 6) + t / 2 + t ** 2 / 3, coinY, t, given=top, unknowns=p))
check('pgf-sum-mean', verify_moment('E(Z)', 1.97, Expect(reds + coinY), given=top, var=p))
check('blank-pgf', verify_pgf('пусто', ..., reds, t), False)

print('\n=== формул темы внутри проверки нет ===')
# Таблица живёт в kit/table.py, а моменты, которыми она пользуется, — в
# kit/distribution.py рядом с биномиальным распределением.
source = ''.join(open(os.path.join(ROOT, 'practicum', 'kit', name)).read()
                 for name in ('distribution.py', 'table.py'))
tree = ast.parse(source)
names = {'_Table', '_Series', 'Dist', 'Freq', 'Moments', '_sum_of', 'Geo', 'total_probability',
         'Pgf', 'verify_letters', '_letter_runs', '_system_roots', 'verify_table_range',
         'verify_mode', 'verify_pgf', '_moment_expression', 'verify_moment', '_moment'}
bodies = {}
for node in tree.body:
    if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names:
        bodies[node.name] = ast.unparse(node)
check('all-found', set(bodies) == names)
code = '\n'.join(bodies.values())
# Среднее первого успеха — сумма ряда, а не 1/p; дисперсия — не (1 − p)/p².
check('no-geo-mean', all(text not in code for text in ('1 / self.p', '1 / p', '/ self.p ** 2')))
series = bodies['_Series']
check('series-adds', 'sp.summation(term(index) * self.chance(index)' in series)
# Дисперсия линейной величины — сумма квадратов отклонений aX + b, а не a²Var.
check('no-a-squared-var', 'a ** 2 * ' not in bodies['_moment'] and 'a * a *' not in bodies['_moment'])
# Буквы — решения условий, собранных из таблицы: сумма клеток минус единица.
check('letters-from-table', 'sp.Add(*[var.chance(v) for v in var.values()]) - 1' in bodies['_letter_runs'])
# Производящая функция — те же клетки при степенях t.
check('pgf-from-cells', 'X.chance(v) * var ** v' in bodies['Pgf'])
# Величина с известными E и Var — два значения, а не формула aE + b.
check('stand-in-two-values', 'centre - step' in bodies['Moments'] and 'centre + step' in bodies['Moments'])

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
