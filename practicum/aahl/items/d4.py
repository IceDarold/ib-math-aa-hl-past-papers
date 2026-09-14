"""Задачи на счёт для практикума D4: дискретные случайные величины.

Генераторы идут по той же лестнице, что практикум: буква в таблице;
среднее; две буквы и второе условие; дисперсия и величина, построенная
из X; первый успех; производящая функция.

Проверки эталона не хранят. `table_check` отдаёт странице таблицу и условия
вопроса, и страница зовёт те же verify_letters, verify_moment,
verify_table_range, verify_mode и verify_pgf, что стоят в ноутбуке: буквы
находит сама проверка, а корень, при котором клетка уходит в минус,
отбрасывает с именем клетки. Эталон в задании только для показа после
попытки.

Таблицы собираются из точных дробей — сотых и десятых, — чтобы сумма
была единицей без округления, а ответ читался и без калькулятора.
"""
from __future__ import annotations

import sympy as sp

from .common import table_check

R = sp.Rational


def _dec(value):
    """Десятичная запись для условия: 0.35, а не 7/20."""
    value = sp.nsimplify(value)
    return f'{float(value):g}'


def _cell(expr):
    """Клетка таблицы в LaTeX: буквы оставить, дроби записать десятичными."""
    expr = sp.sympify(expr)
    decimals = {n: sp.Float(str(float(n))) for n in expr.atoms(sp.Rational)
                if not n.is_Integer}
    return sp.latex(expr.xreplace(decimals))


def _table_text(table, head='x', row='P(X = x)'):
    """Таблица распределения строкой KaTeX: страница markdown-таблиц не рисует."""
    columns = 'c|' + 'c' * len(table)
    values = ' & '.join(sp.latex(sp.sympify(v)) for v in table)
    cells = ' & '.join(_cell(c) for c in table.values())
    head_tex, row_tex = f'\\text{{{head}}}' if len(head) > 1 else head, \
        (f'\\text{{{row}}}' if not row.startswith('P(') else row)
    return (f'\n$$\\begin{{array}}{{{columns}}} {head_tex} & {values} \\\\ \\hline '
            f'{row_tex} & {cells} \\end{{array}}$$\n')


def _hundredths(rng, count, low=5):
    """count вероятностей в сотых, каждая не меньше low сотых, в сумме единица."""
    while True:
        cuts = sorted(rng.sample(range(low, 100 - low), count - 1))
        parts = [b - a for a, b in zip([0] + cuts, cuts + [100])]
        if min(parts) >= low and len(set(parts)) == count:
            return [R(part, 100) for part in parts]


def valid_table(rng):
    """Буква в таблице: найти по сумме, отбросить корень, диапазон, мода."""
    kind = rng.choice(['root', 'range', 'mode'])
    k = sp.Symbol('k')
    if kind == 'root':
        while True:
            low = R(rng.choice([1, 2]), 10)
            high = R(rng.choice([4, 5]), 10)
            shift = low + R(1, 10)
            slope = 1 + low + high
            spare = R(rng.choice([10, 15, 20]), 100)
            third = slope * high + spare
            first = 1 + low * high + shift - third
            table = {0: first, 1: k ** 2, 2: third - slope * k, 3: k - shift}
            good = [c.subs(k, high) for c in table.values()]
            if all(0 <= c <= 1 for c in good) and 0 < first < 1:
                break
        return {
            'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                       + _table_text(table) + 'Найдите $k$.'),
            'answer': sp.Float(high, 15),
            'check': table_check('letters', {'X': (table, False)}, unknowns=[k]),
            'budget_ms': 120_000,
            'note': (f'Сумма клеток — единица: квадратное уравнение, корни {_dec(low)} '
                     f'и {_dec(high)}. При k = {_dec(low)} клетка k − {_dec(shift)} '
                     f'отрицательна, и этот корень отбрасывают — с причиной.'),
        }
    if kind == 'range':
        c = rng.choice([2, 3, 4])
        m = sp.Symbol('m')
        table = {1: m, 2: c * m, 3: 1 - (1 + c) * m}
        return {
            'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                       + _table_text(table) + 'Найдите все возможные значения $m$.'),
            'answer': sp.Interval(0, R(1, 1 + c)),
            'check': table_check('range', {'X': (table, False)}, var=m),
            'budget_ms': 90_000,
            'note': (f'Сумма здесь единица при любом m, решают клетки: m ≥ 0, '
                     f'{c}m ≤ 1, 1 − {1 + c}m ≥ 0. Последнее строже всех. Концы '
                     f'входят: вероятность бывает и нулём.'),
        }
    a = sp.Symbol('a')
    while True:
        weights = rng.sample([1, R(3, 2), 2, R(5, 2), 3], 3)
        constant = R(rng.choice([10, 15, 20, 25, 30]), 100)
        value = (1 - constant) / sum(weights)
        cells = [w * value for w in weights] + [constant]
        if len(set(cells)) == 4:
            break
    order = rng.sample(range(4), 4)
    table = {}
    for position, index in enumerate(order, start=1):
        table[position] = weights[index] * a if index < 3 else constant
    mode = max(table, key=lambda v: table[v].subs(a, value))
    return {
        'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                   + _table_text(table) + 'Найдите моду $X$.'),
        'answer': sp.Integer(mode),
        'check': table_check('mode', {'X': (table, False)}, target='X'),
        'budget_ms': 75_000,
        'note': ('Сначала a из суммы клеток, потом сравнить вероятности. Мода — '
                 'значение с наибольшей вероятностью, а не сама вероятность.'),
    }


def expectation(rng):
    """Среднее: взвешенная сумма по таблице, по частотам, от aX + b."""
    kind = rng.choice(['table', 'freq', 'linear'])
    if kind == 'freq':
        values = list(range(0, 5))
        counts = [rng.randint(1, 12) for _ in values]
        total = sum(counts)
        crowd = rng.choice([10, 20, 30, 50])
        table = dict(zip(values, counts))
        mean = sum(R(v * c, total) for v, c in table.items())
        return {
            'prompt': (f'Опросили ${total}$ посетителей кафе, сколько чашек кофе они '
                       f'выпили за визит:'
                       + _table_text(table, 'чашек', 'посетителей')
                       + f'Оцените ожидаемое число чашек, которое выпьют ${crowd}$ '
                       f'посетителей.'),
            'answer': sp.Float(crowd * mean, 15),
            'check': table_check('mean', {'X': (table, True)}, target='X', a=crowd),
            'budget_ms': 90_000,
            'note': (f'Частота делится на {total} и становится вероятностью; '
                     f'среднее на одного — Σx·f/{total}, на {crowd} — в {crowd} '
                     f'раз больше.'),
        }
    values = sorted(rng.sample([-2, -1, 0, 1, 2, 3, 4, 5], 4))
    table = dict(zip(values, _hundredths(rng, 4)))
    mean = sum(v * c for v, c in table.items())
    if kind == 'table':
        return {
            'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                       + _table_text(table) + 'Найдите $E(X)$.'),
            'answer': sp.Float(mean, 15),
            'check': table_check('mean', {'X': (table, False)}, target='X'),
            'budget_ms': 60_000,
            'note': ('E(X) = Σ x·P(X = x): каждое значение на свою вероятность. '
                     'Среднее самих значений без весов — другой ответ.'),
        }
    a = rng.choice([2, 3, 5, -2, -4])
    b = rng.choice([1, 4, -3, 10])
    return {
        'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                   + _table_text(table)
                   + f'Найдите $E({b} {"+" if a > 0 else "-"} {abs(a)}X)$.'),
        'answer': sp.Float(a * mean + b, 15),
        'check': table_check('mean', {'X': (table, False)}, target='X', a=a, b=b),
        'budget_ms': 75_000,
        'note': f'E(aX + b) = a·E(X) + b, и E(X) = {_dec(mean)}.',
    }


def two_conditions(rng):
    """Две буквы: одно уравнение из суммы, второе из данного среднего."""
    if rng.random() < 0.5:
        a, b = sp.symbols('a b')
        while True:
            first, second = R(rng.randint(1, 5), 10), R(rng.randint(1, 5), 10)
            rest = 1 - first - second
            if rest <= 0 or first == second:
                continue
            split = R(rng.randint(1, int(rest * 10) - 1), 10) if rest > R(1, 10) else None
            if split is None:
                continue
            table = {0: a, 1: b, 2: split, 3: rest - split}
            if 0 < rest - split:
                break
        mean = first * 0 + second * 1 + split * 2 + (rest - split) * 3
        return {
            'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                       + _table_text(table)
                       + f'Известно, что $E(X) = {_dec(mean)}$. Найдите $a$ и $b$ '
                       f'(через запятую).'),
            'answer': [sp.Float(first, 15), sp.Float(second, 15)],
            'check': table_check('letters', {'X': (table, False)}, unknowns=[a, b],
                                 conditions=[('mean', 'X', mean)]),
            'budget_ms': 120_000,
            'note': ('Сумма клеток даёт a + b, среднее — второе уравнение: при a '
                     'стоит ноль, так что b выходит сразу.'),
        }
    f, g = sp.symbols('f g')
    flags = {'integer': True, 'nonnegative': True}
    letters = {'f': flags, 'g': flags}
    while True:
        fv, gv = rng.randint(1, 9), rng.randint(1, 9)
        middle, top = rng.randint(1, 9), rng.randint(1, 9)
        total = fv + middle + gv + top
        mean = R(fv * 1 + middle * 2 + gv * 3 + top * 4, total)
        if mean.q in (1, 2, 4, 5, 10) and fv != gv:
            break
    table = {1: sp.Symbol('f', **flags), 2: middle, 3: sp.Symbol('g', **flags), 4: top}
    return {
        'prompt': (f'В игре записали ${total}$ результатов броска:'
                   + _table_text(table, 'очки', 'частота')
                   + f'Среднее число очков ${_dec(mean)}$. Найдите $f$ и $g$ '
                   f'(через запятую).'),
        'answer': [sp.Integer(fv), sp.Integer(gv)],
        'check': table_check('letters', {'X': (table, True)}, unknowns=[f, g],
                             conditions=[('size', 'X', total), ('mean', 'X', mean)],
                             letters=letters),
        'budget_ms': 120_000,
        'note': (f'Сумма частот — {total}, сумма x·f — {_dec(mean)}·{total}. '
                 f'Две линейные строки на f и g.'),
    }


def variance_linear(rng):
    """Дисперсия таблицы, дисперсия aX + b, величина с известными E и Var."""
    kind = rng.choice(['var', 'linear', 'moments'])
    if kind == 'moments':
        mean = rng.choice([12, 20, 35, 48])
        spread = rng.choice([4, R(9, 4), 6, R(25, 2)])
        a = rng.choice([R(3, 2), 2, R(9, 5), -3])
        b = rng.choice([5, 32, -10, 100])
        table = {mean - sp.sqrt(spread): R(1, 2), mean + sp.sqrt(spread): R(1, 2)}
        return {
            'prompt': (f'Про величину $T$ известно: $E(T) = {_dec(mean)}$, '
                       f'$\\mathrm{{Var}}(T) = {_dec(spread)}$. Найдите '
                       f'$\\mathrm{{Var}}({_dec(b)} {"+" if a > 0 else "-"} '
                       f'{_dec(abs(a))}T)$.'),
            'answer': sp.Float(a * a * spread, 15),
            'check': table_check('var', {'T': (table, False)}, target='T', a=a, b=b),
            'budget_ms': 60_000,
            'note': (f'Var(aT + b) = a²·Var(T): сдвиг {_dec(b)} уходит, множитель '
                     f'{_dec(a)} в квадрате — {_dec(a * a)}.'),
        }
    values = sorted(rng.sample([-1, 0, 1, 2, 3, 4], 3))
    table = dict(zip(values, _hundredths(rng, 3, low=10)))
    mean = sum(v * c for v, c in table.items())
    square = sum(v * v * c for v, c in table.items())
    if kind == 'var':
        return {
            'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                       + _table_text(table) + 'Найдите $\\mathrm{Var}(X)$.'),
            'answer': sp.Float(square - mean ** 2, 15),
            'check': table_check('var', {'X': (table, False)}, target='X'),
            'budget_ms': 90_000,
            'note': (f'E(X) = {_dec(mean)}, E(X²) = {_dec(square)}; Var = E(X²) − '
                     f'E(X)². Без вычитания квадрата среднего это ещё не дисперсия.'),
        }
    a = rng.choice([2, -2, 3, -3])
    b = rng.choice([1, 5, -4])
    return {
        'prompt': ('Дискретная случайная величина $X$ задана таблицей:'
                   + _table_text(table)
                   + f'Найдите $\\mathrm{{Var}}({b} {"+" if a > 0 else "-"} {abs(a)}X)$.'),
        'answer': sp.Float(a * a * (square - mean ** 2), 15),
        'check': table_check('var', {'X': (table, False)}, target='X', a=a, b=b),
        'budget_ms': 105_000,
        'note': (f'Var(X) = {_dec(square - mean ** 2)}, а Var(aX + b) = a²·Var(X): '
                 f'множитель {a} в квадрате, постоянная уходит.'),
    }


def first_success(rng):
    """Первый успех: среднее и дисперсия ряда, p по среднему."""
    p = rng.choice([R(1, 2), R(1, 4), R(1, 5), R(2, 5), R(1, 10), R(3, 10)])
    kind = rng.choice(['mean', 'var', 'p'])
    head = (f'Попытки повторяют, пока одна не удастся; каждая удаётся с '
            f'вероятностью ${_dec(p)}$ независимо от других. $X$ — номер первой '
            f'удачной попытки.')
    if kind == 'mean':
        return {
            'prompt': f'{head} Найдите $E(X)$.',
            'answer': sp.Integer(1) / p,
            'check': table_check('mean', {}, target='X', geo=p),
            'budget_ms': 45_000,
            'note': ('E(X) = Σ x·p(1 − p)^(x − 1) — сумма ряда, и она равна 1/p: '
                     'в среднем удача раз в 1/p попыток.'),
        }
    if kind == 'var':
        return {
            'prompt': (f'{head} Известно, что $\\mathrm{{Var}}(X) = \\frac{{1-p}}{{p^2}}$. '
                       f'Найдите $\\mathrm{{Var}}(X)$.'),
            'answer': (1 - p) / p ** 2,
            'check': table_check('var', {}, target='X', geo=p),
            'budget_ms': 45_000,
            'note': f'(1 − p)/p² при p = {_dec(p)}.',
        }
    q = sp.Symbol('p')
    mean = sp.Integer(1) / p
    return {
        'prompt': ('Попытки повторяют, пока одна не удастся; каждая удаётся с '
                   'одной и той же вероятностью $p$. В среднем первая удача '
                   f'приходится на попытку номер ${_dec(mean)}$. Найдите $p$.'),
        'answer': sp.Float(p, 15),
        'check': table_check('letters', {}, unknowns=[q], geo=q,
                             conditions=[('mean', 'X', mean)]),
        'budget_ms': 45_000,
        'note': 'E(X) = 1/p, поэтому p = 1/E(X).',
    }


def generating_function(rng):
    """Производящая функция: построить по опыту, коэффициент-буква, среднее через G′(1)."""
    kind = rng.choice(['build', 'letter', 'mean'])
    if kind == 'build':
        p = rng.choice([R(1, 3), R(1, 4), R(2, 5), R(3, 5), R(2, 3)])
        fair = {0: R(1, 2), 1: R(1, 2)}
        biased = {0: 1 - p, 1: p}
        table = {n: sum(fair[i] * biased[n - i] for i in range(2) if 0 <= n - i <= 1)
                 for n in range(3)}
        t = sp.Symbol('t')
        return {
            'prompt': (f'Бросают честную монету и монету, у которой орёл выпадает '
                       f'с вероятностью ${_dec(p)}$. $Y$ — число орлов. Запишите '
                       f'производящую функцию $G_Y(t) = \\sum P(Y = y)\\,t^y$.'),
            'answer': sp.expand(sum(c * t ** n for n, c in table.items())),
            'check': table_check('pgf', {'Y': (table, False)}, target='Y'),
            'budget_ms': 120_000,
            'note': ('Коэффициент при tʸ — это P(Y = y): ноль орлов — обе решки, '
                     'один — любая из двух, два — оба орла. G(1) обязано быть 1.'),
        }
    values = [0, 1, 2, 3]
    chances = _hundredths(rng, 4)
    t = sp.Symbol('t')
    if kind == 'mean':
        polynomial = sp.Add(*[c * t ** v for v, c in zip(values, chances)])
        shown = ' + '.join(f'{_dec(c)}' + ('' if v == 0 else ('t' if v == 1 else f't^{v}'))
                           for v, c in zip(values, chances))
        return {
            'prompt': (f'Производящая функция величины $X$: $G(t) = {shown}$. '
                       f'Найдите $E(X)$.'),
            'answer': sp.Float(sp.diff(polynomial, t).subs(t, 1), 15),
            'check': table_check('mean', {'X': (dict(zip(values, chances)), False)},
                                 target='X'),
            'budget_ms': 60_000,
            'note': "E(X) = G′(1): производная многочлена в единице.",
        }
    a = sp.Symbol('a')
    hidden = rng.randrange(4)
    table = {v: (a if i == hidden else c) for i, (v, c) in enumerate(zip(values, chances))}
    shown = ' + '.join((f'{_dec(c)}' if i != hidden else 'a')
                       + ('' if v == 0 else ('t' if v == 1 else f't^{v}'))
                       for i, (v, c) in enumerate(zip(values, chances)))
    return {
        'prompt': (f'Производящая функция величины $X$: $G(t) = {shown}$. '
                   f'Найдите $a$.'),
        'answer': sp.Float(chances[hidden], 15),
        'check': table_check('letters', {'X': (table, False)}, unknowns=[a]),
        'budget_ms': 45_000,
        'note': 'G(1) = 1: коэффициенты — вся таблица, и они складываются в единицу.',
    }


GENERATORS = {
    'D4.valid_table': valid_table,
    'D4.expectation': expectation,
    'D4.two_conditions': two_conditions,
    'D4.variance_linear': variance_linear,
    'D4.first_success': first_success,
    'D4.generating_function': generating_function,
}
