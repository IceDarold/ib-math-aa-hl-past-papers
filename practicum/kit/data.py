"""Данные (D7): сводные числа, ящик с усами, регрессия и корреляция.
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .tangent import _rounds_to, _say


# =================================================================== данные
# Двадцать восьмое понятие равенства ответов: **прямая — это наименьшая
# сумма квадратов**.
#
# Проверка не знает ни Sxy/Sxx, ни формулы для r. Она умеет одно — мерить,
# насколько плохо прямая описывает данные: складывает квадраты вертикальных
# промахов. Прямая регрессии — та, у которой эта сумма наименьшая, и
# проверка ищет её поиском, как ищут дно у чаши. r получается из того же
# поиска: r² — доля разброса y, которую прямая объяснила, 1 − остаток/весь
# разброс; знак r — знак наклона.
#
# Всё остальное — тоже свойства одного набора. Среднее, медиана, квартили,
# стандартное отклонение считаются по списку, а обратный ход — «найдите
# пропавшее значение» — проверяется тем, что ответ ставят в набор и
# пересчитывают. Своего числа у проверки нет ни в одном задании.

_GOLDEN = (math.sqrt(5) - 1) / 2
_SEARCH_STEPS = 200        # шагов золотого сечения на одну букву
_SEARCH_PASSES = 6         # проходов по двум буквам прямой
_SUMMARY_WORDS = ('mean', 'median', 'deviation', 'range', 'size', 'q1', 'q3',
                  'iqr', 'lowest', 'highest')


def _datum(value):
    """Число из условия — точной дробью: 3.3 это 33/10, а не 3.2999…"""
    if isinstance(value, float):
        return sp.Rational(repr(value))
    value = sp.sympify(value)
    if value.is_Float:
        return sp.Rational(str(value))
    return value


class _Bunch:
    """Часть набора, о которой известны только размер, среднее и края."""

    def __init__(self, size, average, lowest, highest):
        self.size = _datum(size)
        self.total = self.size * _datum(average)
        self.lowest, self.highest = _datum(lowest), _datum(highest)

    def __repr__(self):
        return (f"Bunch({self.size}, average={self.total / self.size}, "
                f"lowest={self.lowest}, highest={self.highest})")


def Bunch(size, average, lowest, highest):
    """Наблюдения, которых не видно: `Bunch(28, average=10.5, lowest=6, highest=17)`.

    Так выглядят 28 учеников, от которых на картинке остался ящик с усами и
    одно среднее. Сумма у них есть (28 · 10.5), края тоже, а медиану и
    стандартное отклонение по ним не посчитать — проверка их и не просит.
    """
    return _Bunch(size, average, lowest, highest)


class _Sample:
    """Набор наблюдений одной величины."""

    def __init__(self, items, name):
        self.name = name
        self.items = items            # числа и буквы, по одному на наблюдение
        self.bunches = [item for item in items if isinstance(item, _Bunch)]
        self.plain = [item for item in items if not isinstance(item, _Bunch)]
        self.weights = None           # таблица частот: {значение: частота}

    def letters(self):
        found = set()
        for item in self.plain:
            found |= sp.sympify(item).free_symbols
        for value, count in (self.weights or {}).items():
            found |= sp.sympify(value).free_symbols | sp.sympify(count).free_symbols
        return found

    def put(self, fill):
        """Тот же набор, где буквы заменены числами."""
        if self.weights is not None:
            table = {sp.sympify(value).subs(fill): sp.sympify(count).subs(fill)
                     for value, count in self.weights.items()}
            return Sample(table, self.name)
        return _Sample([item if isinstance(item, _Bunch) else sp.sympify(item).subs(fill)
                        for item in self.items], self.name)

    def listed(self):
        """Все наблюдения по возрастанию — только если каждое видно."""
        if self.bunches:
            raise ValueError(_t(
                'часть наблюдений не видна: этого по такому набору не посчитать',
                'some observations are not visible: this cannot be found from such a set'))
        values = [sp.sympify(item) for item in self.plain]
        if any(value.free_symbols for value in values):
            raise ValueError(_t('в наборе ещё есть буквы', 'the set still has letters in it'))
        return sorted(values, key=float)

    def __repr__(self):
        if self.weights is not None:
            cells = ', '.join(f"{value}: {count}" for value, count in self.weights.items())
            return f"{self.name}: {{{cells}}}"
        return f"{self.name}: {self.items}"


def Sample(values, name='x'):
    """Набор наблюдений: `Sample([3.3, 6.9, 11.9])`, `Sample({2: 5, 3: 1, 6: x})`.

    Список — сами наблюдения; в нём могут стоять буквы (пропавшие значения)
    и `Bunch` (наблюдения, от которых известны только сумма и края).
    Словарь — таблица частот: значение → сколько раз оно встретилось;
    частота тоже может быть буквой.
    """
    if values is Ellipsis:
        return Ellipsis
    if isinstance(values, dict):
        table = {_datum(value): _datum(count) for value, count in values.items()}
        items = []
        if not any(sp.sympify(count).free_symbols for count in table.values()):
            for value, count in table.items():
                items += [value] * int(count)
        made = _Sample(items, name)
        made.weights = table
        return made
    return _Sample([item if isinstance(item, _Bunch) else _datum(item)
                    for item in values], name)


def _plain_table(S):
    """Таблица частот с буквой в частоте ещё не раскрыта в список."""
    if S.weights is not None and any(sp.sympify(c).free_symbols for c in S.weights.values()):
        raise ValueError(_t('частота ещё буква — подставьте её',
                            'a frequency is still a letter: put a number in'))


def size(S):
    """Сколько наблюдений в наборе."""
    if S.weights is not None:
        return sp.Add(*S.weights.values())
    return len(S.plain) + sum((b.size for b in S.bunches), sp.Integer(0))


def mean(S):
    """Среднее: сумма, делённая на число наблюдений. Работает и с буквами."""
    if S.weights is not None:
        return sp.Add(*(v * c for v, c in S.weights.items())) / size(S)
    total = sp.Add(*S.plain) + sum((b.total for b in S.bunches), sp.Integer(0))
    return sp.nsimplify(total / size(S)) if not total.free_symbols else total / size(S)


def _middle_of(values):
    n = len(values)
    if n == 0:
        raise ValueError(_t('в наборе нет наблюдений', 'the set is empty'))
    half = n // 2
    return values[half] if n % 2 else (values[half - 1] + values[half]) / 2


def median(S):
    """Медиана: середина упорядоченного набора."""
    if isinstance(S, _Box):
        return S.middle
    _plain_table(S)
    return _middle_of(S.listed())


def quartiles(S):
    """Q1 и Q3 так, как их считает GDC в IB: медианы нижней и верхней половин.

    При нечётном числе наблюдений сама медиана не входит ни в одну половину.
    """
    if isinstance(S, _Box):
        return S.lower, S.upper
    _plain_table(S)
    values = S.listed()
    half = len(values) // 2
    return _middle_of(values[:half]), _middle_of(values[len(values) - half:])


def iqr(S):
    """Межквартильный размах Q3 − Q1."""
    lower, upper = quartiles(S)
    return upper - lower


def spread(S):
    """Размах набора: наибольшее минус наименьшее (range в IB)."""
    return _highest(S) - _lowest(S)


def _lowest(S):
    if isinstance(S, _Box):
        return S.lowest
    _plain_table(S)
    return sp.Min(*[sp.sympify(item) for item in S.plain], *[b.lowest for b in S.bunches])


def _highest(S):
    if isinstance(S, _Box):
        return S.highest
    _plain_table(S)
    return sp.Max(*[sp.sympify(item) for item in S.plain], *[b.highest for b in S.bunches])


def deviation(S):
    """Стандартное отклонение σ: деление на n, а не на n − 1, как в IB."""
    _plain_table(S)
    values = S.listed()
    centre = sum(values) / len(values)
    return sp.sqrt(sum((value - centre) ** 2 for value in values) / len(values))


def _summary(S, what):
    """Сводное число по имени."""
    what = what.lower()
    table = {'mean': mean, 'median': median, 'deviation': deviation,
             'range': spread, 'size': size, 'iqr': iqr,
             'lowest': _lowest, 'highest': _highest}
    if what in table:
        return table[what](S)
    if what == 'q1':
        return quartiles(S)[0]
    if what == 'q3':
        return quartiles(S)[1]
    raise ValueError(f"summary: {what}?")


def _summary_name(what):
    what = what.lower()
    if what == 'mean':
        return _t('среднее', 'the mean')
    if what == 'median':
        return _t('медиана', 'the median')
    if what == 'deviation':
        return _t('стандартное отклонение', 'the standard deviation')
    if what == 'range':
        return _t('размах', 'the range')
    if what == 'size':
        return _t('число наблюдений', 'the number of observations')
    if what == 'q1':
        return _t('нижний квартиль', 'the lower quartile')
    if what == 'q3':
        return _t('верхний квартиль', 'the upper quartile')
    if what == 'iqr':
        return _t('межквартильный размах', 'the interquartile range')
    if what == 'lowest':
        return _t('наименьшее значение', 'the smallest value')
    return _t('наибольшее значение', 'the largest value')


# ================================================================= ящик с усами
class _Box:
    """Пять чисел ящика с усами. Шестого — среднего — на диаграмме нет."""

    def __init__(self, lowest, lower, middle, upper, highest, name):
        self.lowest, self.lower, self.middle = _datum(lowest), _datum(lower), _datum(middle)
        self.upper, self.highest = _datum(upper), _datum(highest)
        self.name = name

    def five(self):
        return (self.lowest, self.lower, self.middle, self.upper, self.highest)

    def letters(self):
        found = set()
        for value in self.five():
            found |= sp.sympify(value).free_symbols
        return found

    def put(self, fill):
        return _Box(*(sp.sympify(value).subs(fill) for value in self.five()), self.name)

    def __repr__(self):
        return f"Box{self.five()}"


def Box(lowest, lower, middle, upper, highest, name='x'):
    """Ящик с усами: `Box(2, 6, 7, 10, 18)` — минимум, Q1, медиана, Q3, максимум.

    Любое из пяти может быть буквой: `Box(10, L, 40, U, 75)`.
    """
    return _Box(lowest, lower, middle, upper, highest, name)


def fence(S):
    """Границы выброса: Q1 − 1.5·IQR и Q3 + 1.5·IQR."""
    lower, upper = quartiles(S)
    step = sp.Rational(3, 2) * (upper - lower)
    return lower - step, upper + step


def clean(S):
    """Условие «выбросов нет»: оба края набора внутри границ."""
    low, high = fence(S)
    return sp.And(_lowest(S) >= low, _highest(S) <= high)


def _box_order(B):
    """Пять чисел ящика идут не убывая — это часть условия любой задачи."""
    five = B.five()
    return [sp.Le(one, two) for one, two in zip(five, five[1:])
            if (sp.sympify(one) - sp.sympify(two)).free_symbols]


def skew(S):
    """Куда вытянут хвост: 'positive', 'negative' или 'none'.

    По коробке: медиана ближе к Q1 — хвост справа, и среднее больше медианы.
    """
    lower, upper = quartiles(S)
    middle = median(S)
    left, right = middle - lower, upper - middle
    if sp.simplify(left - right) == 0:
        return 'none'
    return 'positive' if float(left) < float(right) else 'negative'


# ================================================================= две величины
class _Pairs:
    """Двумерные данные: пары (x, y) одной длины."""

    def __init__(self, xs, ys, names):
        self.xs = [_datum(value) for value in xs]
        self.ys = [_datum(value) for value in ys]
        self.names = names

    def column(self, which):
        return self.xs if which == self.names[0] else self.ys

    def put(self, fill):
        return _Pairs([sp.sympify(v).subs(fill) for v in self.xs],
                      [sp.sympify(v).subs(fill) for v in self.ys], self.names)

    def letters(self):
        found = set()
        for value in self.xs + self.ys:
            found |= sp.sympify(value).free_symbols
        return found

    def __repr__(self):
        return f"Pairs({self.names[0]}: {self.xs}, {self.names[1]}: {self.ys})"


def Pairs(xs, ys, names=('x', 'y')):
    """Двумерные данные: `Pairs([3, 9, 11], [6, 10, 12])`.

    names — как переменные называются в вопросе: `names=('d', 'h')`.
    """
    if xs is Ellipsis or ys is Ellipsis:
        return Ellipsis
    if len(xs) != len(ys):
        raise ValueError(_t(f'списки разной длины: {len(xs)} и {len(ys)}',
                            f'the lists differ in length: {len(xs)} and {len(ys)}'))
    return _Pairs(xs, ys, tuple(str(name) for name in names))


def _numbers(values):
    try:
        return [float(value) for value in values]
    except TypeError:
        raise ValueError(_t('в данных ещё есть буквы', 'the data still has letters in it'))


def _misfit(xs, ys, slope, level, centre):
    """Сумма квадратов вертикальных промахов прямой y = level + slope·(x − centre)."""
    return sum((b - level - slope * (a - centre)) ** 2 for a, b in zip(xs, ys))


def _lowest_point(cost, guess, scale):
    """Дно выпуклой функции одной переменной: вилка, потом золотое сечение."""
    lo, hi = guess - scale, guess + scale
    for _ in range(200):                      # расширяем вилку, пока дно не внутри
        middle = (lo + hi) / 2
        if cost(lo) > cost(middle) < cost(hi) or cost(lo) == cost(middle) == cost(hi):
            break
        width = hi - lo
        if cost(lo) <= cost(hi):
            lo -= width
        else:
            hi += width
    one = hi - _GOLDEN * (hi - lo)
    two = lo + _GOLDEN * (hi - lo)
    for _ in range(_SEARCH_STEPS):
        if cost(one) <= cost(two):
            hi, two = two, one
            one = hi - _GOLDEN * (hi - lo)
        else:
            lo, one = one, two
            two = lo + _GOLDEN * (hi - lo)
        if hi - lo <= 1e-15 * max(1.0, abs(lo), abs(hi)):
            break
    return (lo + hi) / 2


def _best_line(xs, ys):
    """Прямая наименьших квадратов — как дно суммы квадратов, а не по формуле.

    Прямую пишут через точку x = centre (середина x-ов): так две её буквы,
    наклон и высота, почти не мешают друг другу, и поиск по очереди то
    одной, то другой сходится за пару проходов. Точку взять можно любую —
    дно от этого не сдвигается, меняется только то, как быстро до него
    доходят.
    """
    xs, ys = _numbers(xs), _numbers(ys)
    centre = sum(xs) / len(xs)
    width = (max(xs) - min(xs)) or 1.0
    height = (max(ys) - min(ys)) or 1.0
    slope, level = 0.0, sum(ys) / len(ys)
    for _ in range(_SEARCH_PASSES):
        slope = _lowest_point(lambda s: _misfit(xs, ys, s, level, centre),
                              slope, height / width)
        level = _lowest_point(lambda h: _misfit(xs, ys, slope, h, centre),
                              level, height)
    return slope, level - slope * centre


def _names_of(P, of):
    """Какая переменная предсказывается и какая предсказывает."""
    target = P.names[1] if of is None else str(of)
    if target not in P.names:
        raise ValueError(_t(f'переменной {target} в данных нет',
                            f'there is no variable {target} in the data'))
    source = P.names[0] if target == P.names[1] else P.names[1]
    return target, source


def fit(P, of=None):
    """Прямая регрессии (a, b): target = a·source + b.

    По умолчанию — y на x. `fit(P, of='x')` — прямая x на y: она
    предсказывает x, и это другая прямая, а не первая, решённая относительно x.
    """
    target, source = _names_of(P, of)
    return _best_line(P.column(source), P.column(target))


def strength(P):
    """Коэффициент корреляции r — из той же суммы квадратов.

    r² — доля разброса y, которую прямая объяснила: 1 − остаток/весь разброс.
    Знак r — знак наклона.
    """
    xs, ys = _numbers(P.xs), _numbers(P.ys)
    slope, cut = _best_line(xs, ys)
    level = sum(ys) / len(ys)
    whole = sum((b - level) ** 2 for b in ys)
    left = sum((b - slope * a - cut) ** 2 for a, b in zip(xs, ys))
    if whole == 0:
        raise ValueError(_t('у y нет разброса: r не определён',
                            'y does not vary: r is not defined'))
    share = max(0.0, 1 - left / whole)
    return math.copysign(math.sqrt(share), slope)


def centre(P):
    """Точка средних (x̄, ȳ)."""
    return (sp.Add(*P.xs) / len(P.xs), sp.Add(*P.ys) / len(P.ys))


# ================================================================= проверки
def _as_number(value):
    try:
        return float(sp.N(sp.sympify(value), 30))
    except (TypeError, ValueError, AttributeError):
        return None


def _fill_of(got, letters, label):
    """Ответ с буквами — в словарь {буква: число}."""
    order = sorted(letters, key=str)
    if isinstance(got, dict):
        fill = {sp.Symbol(str(k)) if isinstance(k, str) else k: v for k, v in got.items()}
    elif isinstance(got, (list, tuple, sp.Tuple)):
        if len(got) != len(order):
            print(f"{NO} {label}: " + _t(
                f"неизвестных {len(order)} ({', '.join(map(str, order))}), а чисел {len(got)}",
                f"there are {len(order)} unknowns ({', '.join(map(str, order))}) "
                f"and {len(got)} numbers"))
            return None
        fill = dict(zip(order, got))
    elif len(order) == 1:
        fill = {order[0]: got}
    else:
        print(f"{NO} {label}: " + _t(
            f"неизвестных {len(order)}: назови все ({', '.join(map(str, order))})",
            f"there are {len(order)} unknowns: give all of them ({', '.join(map(str, order))})"))
        return None
    return {key: _datum(value) for key, value in fill.items()}


def _holds(rule):
    rule = sp.sympify(rule)
    if rule is sp.true or rule is True:
        return True
    if rule is sp.false or rule is False:
        return False
    if isinstance(rule, sp.Eq):
        gap = _as_number(rule.lhs - rule.rhs)
        return gap is not None and abs(gap) <= 1e-9 * max(1.0, abs(_as_number(rule.rhs) or 0))
    return bool(rule)


def verify_summary(label, got, S, what='mean', digits=3):
    """Ответ — сводное число набора: среднее, медиана, σ, размах, квартиль."""
    if _blank(label, got):
        return False
    truth = _summary(S, what)
    mine = _as_number(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    want = float(truth)
    if _rounds_to(mine, want, digits):
        print(f"{OK} {label}: {_say(got)}")
        return True
    why = None
    weights = getattr(S, 'weights', None)
    if isinstance(S, _Box):
        for name, value in (('q1', S.lower), ('q3', S.upper), ('lowest', S.lowest),
                            ('highest', S.highest)):
            if name != what and _rounds_to(mine, float(value), digits):
                why = _t(f"это {_summary_name(name)}", f"that is {_summary_name(name)}")
                break
    elif what == 'deviation':
        n = len(S.listed())
        if n > 1 and _rounds_to(mine, want * math.sqrt(n / (n - 1)), digits):
            why = _t("это деление на n − 1; в IB σ делят на n",
                     "that divides by n − 1; in IB σ divides by n")
        elif _rounds_to(mine, want ** 2, digits):
            why = _t("это дисперсия, а не стандартное отклонение",
                     "that is the variance, not the standard deviation")
    if what == 'mean' and weights is not None:
        values = list(S.weights)
        if _rounds_to(mine, float(sum(values) / len(values)), digits):
            why = _t("это среднее значений без частот", "that is the mean of the values, ignoring the frequencies")
    if what == 'median' and weights is not None:
        values = sorted(S.weights, key=float)
        if _rounds_to(mine, float(_middle_of(values)), digits):
            why = _t("это середина столбца значений, а не медиана наблюдений",
                     "that is the middle of the list of values, not the median of the observations")
    print(f"{NO} {label}: " + (why or _t(
        f"{_summary_name(what)} набора — другое число",
        f"{_summary_name(what)} of the set is a different number")))
    return False


def verify_missing(label, got, S, holds=(), **given):
    """Пропавшие значения набора: ответ ставят в набор и пересчитывают.

    given — сводные числа из условия: `mean=10.6, range=14`; holds — прочие
    условия на буквы: `[a < 6, b > 17]`. Верен ответ, при котором сходится всё.
    """
    if _blank(label, got):
        return False
    letters = S.letters() | set().union(*(sp.sympify(r).free_symbols for r in holds))
    fill = _fill_of(got, letters, label)
    if fill is None:
        return False
    try:
        filled = S.put(fill)
    except ValueError as error:
        print(f"{NO} {label}: {error}")
        return False
    for what, want in given.items():
        try:
            value = _summary(filled, what)
        except ValueError as error:
            print(f"{NO} {label}: {error}")
            return False
        value = _as_number(value)
        if value is None or abs(value - float(_datum(want))) > 1e-9 * max(1.0, abs(float(_datum(want)))):
            print(f"{NO} {label}: " + _t(
                f"с таким ответом {_summary_name(what)} выходит {_say(value)}, а не {_say(want)}",
                f"with this answer {_summary_name(what)} comes out as {_say(value)}, "
                f"not {_say(want)}"))
            return False
    for rule in holds:
        if not _holds(sp.sympify(rule).subs(fill)):
            print(f"{NO} {label}: " + _t(f"не выполнено условие {rule}",
                                        f"the condition {rule} does not hold"))
            return False
    shown = ', '.join(f"{key} = {_say(value)}" for key, value in
                      sorted(fill.items(), key=lambda item: str(item[0])))
    print(f"{OK} {label}: {shown}")
    return True


def _possible(B, letter, holds):
    """Все значения letter, при которых ящик B и условия holds возможны."""
    rules = [sp.sympify(rule) for rule in list(holds) + _box_order(B)]
    equal = [rule for rule in rules if isinstance(rule, sp.Eq)]
    rest = [rule for rule in rules if not isinstance(rule, sp.Eq)]
    others = sorted((B.letters() | set().union(*(r.free_symbols for r in rules))) - {letter},
                    key=str)
    if equal and others:
        found = sp.solve(equal, others, dict=True)
        if not found:
            return sp.EmptySet
        rest = [rule.subs(found[0]) for rule in rest]
    rest = [rule for rule in rest if rule is not sp.true]
    if any(rule is sp.false for rule in rest):
        return sp.EmptySet
    region = sp.Interval(-sp.oo, sp.oo)
    for rule in rest:
        for part in (rule.args if isinstance(rule, sp.And) else (rule,)):
            region &= sp.solveset(part, letter, sp.S.Reals)
    return region


def verify_bound(label, got, B, letter, kind='least', holds=()):
    """Крайнее возможное значение буквы ящика: «find the minimum possible value of U».

    holds — условия задачи на буквы, например `[Eq(iqr(B), 20), clean(B)]`.
    Проверка находит всё множество допустимых значений и берёт его край.
    """
    if _blank(label, got):
        return False
    region = _possible(B, letter, holds)
    if region is sp.EmptySet:
        print(f"{NO} {label}: " + _t("условия задачи несовместны", "the conditions cannot all hold"))
        return False
    edge = region.inf if kind == 'least' else region.sup
    other = region.sup if kind == 'least' else region.inf
    mine = _as_number(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    if abs(mine - float(edge)) <= 1e-9 * max(1.0, abs(float(edge))):
        print(f"{OK} {label}: {letter} = {_say(got)}")
        return True
    if other.is_finite and abs(mine - float(other)) <= 1e-9 * max(1.0, abs(float(other))):
        why = _t(f"это другой край: {letter} может быть от {_say(region.inf)} до {_say(region.sup)}",
                 f"that is the other end: {letter} can be anything from {_say(region.inf)} "
                 f"to {_say(region.sup)}")
    elif sp.sympify(got) in region:
        why = _t(f"{letter} = {_say(got)} возможно, но возможно и "
                 f"{'меньше' if kind == 'least' else 'больше'}",
                 f"{letter} = {_say(got)} is possible, but so is a "
                 f"{'smaller' if kind == 'least' else 'larger'} value")
    else:
        why = _t(f"при {letter} = {_say(got)} условия не выполняются: "
                 f"{letter} может быть от {_say(region.inf)} до {_say(region.sup)}",
                 f"with {letter} = {_say(got)} the conditions fail: {letter} can be "
                 f"anything from {_say(region.inf)} to {_say(region.sup)}")
    print(f"{NO} {label}: " + why)
    return False


def verify_fence(label, got, S, side='upper'):
    """Граница выброса — «the largest value that would not be an outlier»."""
    if _blank(label, got):
        return False
    low, high = fence(S)
    want = float(high if side == 'upper' else low)
    mine = _as_number(got)
    if mine is not None and _rounds_to(mine, want):
        print(f"{OK} {label}: {_say(got)}")
        return True
    lower, upper = quartiles(S)
    step = float(upper - lower)
    why = None
    if mine is not None:
        if side == 'upper' and _rounds_to(mine, 1.5 * float(upper)):
            why = _t("это 1.5 · Q3, а граница — Q3 + 1.5 · IQR",
                     "that is 1.5 × Q3; the fence is Q3 + 1.5 × IQR")
        elif side == 'upper' and _rounds_to(mine, float(median(S)) + 1.5 * step):
            why = _t("граница отложена от медианы, а не от Q3",
                     "the fence is measured from the median instead of Q3")
        elif _rounds_to(mine, float(low if side == 'upper' else high)):
            why = _t("это другая граница", "that is the other fence")
        elif side == 'upper' and _rounds_to(mine, float(upper) + step):
            why = _t("IQR не умножен на 1.5", "the IQR is not multiplied by 1.5")
    print(f"{NO} {label}: " + (why or _t("граница выброса — другое число",
                                        "the outlier fence is a different number")))
    return False


def _yes_no(got):
    word = str(got).strip().lower()
    if word in ('yes', 'y', 'true'):
        return True
    if word in ('no', 'n', 'false'):
        return False
    return None


def verify_outlier(label, got, S, value):
    """Ответ 'yes' или 'no': выброс ли value для набора с этим ящиком."""
    if _blank(label, got):
        return False
    mine = got if isinstance(got, bool) else _yes_no(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — 'yes' или 'no'", "the answer is 'yes' or 'no'"))
        return False
    low, high = fence(S)
    truth = float(value) > float(high) or float(value) < float(low)
    if mine == truth:
        print(f"{OK} {label}: {'yes' if truth else 'no'}")
        return True
    print(f"{NO} {label}: " + _t(
        f"границы выброса {_say(low)} и {_say(high)}, а {_say(value)} "
        f"{'снаружи' if truth else 'внутри'}",
        f"the fences are {_say(low)} and {_say(high)}, and {_say(value)} is "
        f"{'outside' if truth else 'inside'}"))
    return False


_SKEW_WORDS = {'positive': 'positive', 'right': 'positive', 'negative': 'negative',
               'left': 'negative', 'none': 'none', 'symmetric': 'none', 'symmetrical': 'none'}


def verify_skew(label, got, S):
    """Куда вытянут набор: 'positive', 'negative' или 'none' — по его коробке."""
    if _blank(label, got):
        return False
    mine = _SKEW_WORDS.get(str(got).strip().lower())
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — 'positive', 'negative' или 'none'",
                                    "the answer is 'positive', 'negative' or 'none'"))
        return False
    truth = skew(S)
    if mine == truth:
        print(f"{OK} {label}: {truth}")
        return True
    lower, upper = quartiles(S)
    middle = median(S)
    print(f"{NO} {label}: " + _t(
        f"от медианы до Q1 — {_say(middle - lower)}, до Q3 — {_say(upper - middle)}",
        f"from the median to Q1 is {_say(middle - lower)}, to Q3 is {_say(upper - middle)}"))
    return False


def _line_of(model, of):
    """Прямая (a, b, target, source) — по данным или как её дали в условии."""
    if isinstance(model, _Pairs):
        target, source = _names_of(model, of)
        slope, cut = fit(model, target)
        return slope, cut, sp.Symbol(target), sp.Symbol(source)
    if isinstance(model, (list, tuple)):
        chosen = [line for line in model if of is None or str(sp.sympify(line).lhs) == str(of)]
        if len(chosen) != 1:
            raise ValueError(_t(f'из прямых не выбрать ту, что предсказывает {of}',
                                f'none of the lines is the one that predicts {of}'))
        model = chosen[0]
    relation = sp.sympify(model)
    if not isinstance(relation, sp.Eq):
        raise ValueError(_t('прямую передают уравнением: Eq(y, 2*x + 1)',
                            'pass the line as an equation: Eq(y, 2*x + 1)'))
    target = relation.lhs
    source = (relation.rhs.free_symbols - {target}).pop()
    slope = sp.diff(relation.rhs, source)
    return float(slope), float(relation.rhs.subs(source, 0)), target, source


def _pair_of(got):
    """Ответ-прямая: пара (a, b), уравнение или правая часть."""
    if isinstance(got, str):
        return None, None
    if isinstance(got, (tuple, list, sp.Tuple)) and len(got) == 2:
        return _as_number(got[0]), _as_number(got[1])
    relation = sp.sympify(got)
    if isinstance(relation, sp.Eq):
        relation = relation.rhs
    symbols_in = relation.free_symbols
    if len(symbols_in) != 1:
        return None, None
    source = symbols_in.pop()
    return _as_number(sp.diff(relation, source)), _as_number(relation.subs(source, 0))


def verify_fit(label, got, P, of=None):
    """Ответ — прямая регрессии: пара (a, b) или уравнение, три значащие цифры."""
    if _blank(label, got):
        return False
    slope, cut = _pair_of(got)
    if slope is None or cut is None:
        print(f"{NO} {label}: " + _t("ответ — пара (a, b) или уравнение прямой",
                                    "the answer is a pair (a, b) or the equation of the line"))
        return False
    target, source = _names_of(P, of)
    a, b = fit(P, target)
    if _rounds_to(slope, a) and _rounds_to(cut, b):
        print(f"{OK} {label}: {target} = {_say(slope)}{source} "
              f"{'+' if cut >= 0 else '−'} {_say(abs(cut))}")
        return True
    back, other = fit(P, source)
    why = None
    if _rounds_to(slope, b) and _rounds_to(cut, a):
        why = _t("a и b переставлены местами", "a and b are the other way round")
    elif _rounds_to(slope, back) and _rounds_to(cut, other):
        why = _t(f"это прямая {source} на {target}, а нужна {target} на {source}",
                 f"that is the line of {source} on {target}; this asks for {target} on {source}")
    elif back and _rounds_to(slope, 1 / back) and _rounds_to(cut, -other / back):
        why = _t(f"это прямая {source} на {target}, решённая относительно {target}: "
                 f"такая прямая другая",
                 f"that is the line of {source} on {target} solved for {target}: "
                 f"it is a different line")
    elif _rounds_to(slope, a) and not _rounds_to(cut, b):
        why = _t("наклон верный, а свободный член — нет",
                 "the gradient is right, the intercept is not")
    elif _rounds_to(cut, b) and not _rounds_to(slope, a):
        why = _t("свободный член верный, а наклон — нет",
                 "the intercept is right, the gradient is not")
    else:
        mine = _misfit(_numbers(P.column(source)), _numbers(P.column(target)), slope, cut, 0.0)
        best = _misfit(_numbers(P.column(source)), _numbers(P.column(target)), a, b, 0.0)
        why = _t(f"сумма квадратов промахов у этой прямой {_say(mine)}, а наименьшая — {_say(best)}",
                 f"this line leaves a sum of squared misses of {_say(mine)}; the least "
                 f"possible is {_say(best)}")
    print(f"{NO} {label}: " + why)
    return False


def verify_strength(label, got, P):
    """Ответ — r, три значащие цифры."""
    if _blank(label, got):
        return False
    mine = _as_number(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    truth = strength(P)
    if _rounds_to(mine, truth):
        print(f"{OK} {label}: r = {_say(got)}")
        return True
    if _rounds_to(mine, truth ** 2):
        why = _t("это r², а не r", "that is r², not r")
    elif _rounds_to(mine, -truth):
        why = _t("знак не тот: наклон прямой другого знака",
                 "wrong sign: the line slopes the other way")
    elif _rounds_to(mine, truth, 2):
        why = _t("нужно три значащие цифры", "three significant figures are needed")
    elif abs(mine) > 1:
        why = _t("|r| не бывает больше единицы", "|r| is never more than 1")
    else:
        why = _t("r по этим данным — другое число", "r for this data is a different number")
    print(f"{NO} {label}: " + why)
    return False


def verify_estimate(label, got, model, at, of=None, whole=False):
    """Предсказание по прямой: подстановка at в прямую регрессии.

    model — данные (`Pairs`, прямая находится) или уравнение прямой из
    условия. Принимается и подстановка в прямую с коэффициентами,
    округлёнными до трёх цифр: схема так и пишет, «their equation».
    whole=True — ответ просят целым.
    """
    if _blank(label, got):
        return False
    mine = _as_number(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    a, b, target, source = _line_of(model, of)
    at = float(_datum(at))
    exact = a * at + b
    rounded = float(sp.Float(a, 3)) * at + float(sp.Float(b, 3))
    if whole:
        ok = mine == round(mine) and int(mine) in (round(exact), round(rounded))
    else:
        ok = _rounds_to(mine, exact) or _rounds_to(mine, rounded)
    if ok:
        print(f"{OK} {label}: {target} ≈ {_say(got)}")
        return True
    why = None
    if whole and _rounds_to(mine, exact):
        why = _t("просили целое число", "the answer was asked for to the nearest integer")
    if why is None and isinstance(model, (list, tuple)):
        for line in model:
            line = sp.sympify(line)
            if line.lhs != target and len(line.rhs.free_symbols) == 1:
                there = line.rhs.free_symbols.pop()
                if _rounds_to(mine, float(line.rhs.subs(there, at))):
                    why = _t(f"значение подставлено в прямую {line.lhs} на {there}: "
                             f"предсказывать {target} нужно прямой {target} на {source}",
                             f"the value went into the line of {line.lhs} on {there}: "
                             f"to predict {target} use the line of {target} on {source}")
    if why is None and isinstance(model, _Pairs):
        c, d = fit(model, str(source))
        if c and (_rounds_to(mine, (at - d) / c) or (whole and mine == round((at - d) / c))):
            why = _t(f"это прямая {source} на {target}, решённая относительно {target}: "
                     f"предсказывать {target} нужно прямой {target} на {source}",
                     f"this solves the line of {source} on {target} for {target}: "
                     f"to predict {target} use the line of {target} on {source}")
    if why is None and a and _rounds_to(mine, (at - b) / a):
        why = _t(f"подставлено {target} = {_say(at)}, а дано {source} = {_say(at)}",
                 f"this puts {target} = {_say(at)}; the value given is {source} = {_say(at)}")
    if why is None and _rounds_to(mine, a * at):
        why = _t("свободный член потерян: a·x без b", "the intercept is left out: a·x without b")
    print(f"{NO} {label}: " + (why or _t(
        f"по прямой при {source} = {_say(at)} выходит другое",
        f"the line gives something else at {source} = {_say(at)}")))
    return False


def verify_change(label, got, model, step, of=None):
    """«На сколько изменится y, если x вырастет на step» — это a · step."""
    if _blank(label, got):
        return False
    mine = _as_number(got)
    a, b, target, source = _line_of(model, of)
    want = a * float(_datum(step))
    if mine is not None and (_rounds_to(mine, want) or _rounds_to(mine, want, 2)
                             or mine == round(want)):
        print(f"{OK} {label}: {_say(got)}")
        return True
    why = None
    if mine is not None and _rounds_to(mine, b * float(_datum(step))):
        why = _t("на шаг умножен свободный член, а нужен наклон",
                 "the step is multiplied by the intercept; it should be the gradient")
    elif mine is not None and _rounds_to(mine, a):
        why = _t("это изменение на одну единицу, а шаг другой",
                 "that is the change for one unit; the step is different")
    print(f"{NO} {label}: " + (why or _t("изменение — наклон, умноженный на шаг",
                                        "the change is the gradient times the step")))
    return False


def verify_centre(label, got, model, of=None, order=None):
    """Точка средних: по данным или как пересечение двух прямых регрессии.

    model — `Pairs` или список из двух уравнений прямых. of — если нужна
    одна координата, её буква; order — в каком порядке спрошена пара.
    """
    if _blank(label, got):
        return False
    if isinstance(model, _Pairs):
        names = [sp.Symbol(n) for n in model.names]
        point = dict(zip(names, (float(v) for v in centre(model))))
    else:
        lines = [sp.sympify(line) for line in model]
        names = [line.lhs for line in lines]
        try:
            found = sp.solve(lines, names, dict=True) if len(set(names)) == 2 else []
        except (ValueError, NotImplementedError):
            found = []
        if len(found) != 1:
            print(f"{NO} {label}: " + _t("прямые не пересекаются в одной точке",
                                        "the lines do not meet in one point"))
            return False
        if any(value.free_symbols for value in found[0].values()):
            print(f"{NO} {label}: " + _t("прямые не пересекаются в одной точке",
                                        "the lines do not meet in one point"))
            return False
        point = {key: float(value) for key, value in found[0].items()}
    if of is not None:
        want = point[sp.Symbol(str(of))]
        mine = _as_number(got)
        if mine is not None and _rounds_to(mine, want):
            print(f"{OK} {label}: {of} = {_say(got)}")
            return True
        others = [value for key, value in point.items() if str(key) != str(of)]
        why = None
        if mine is not None and others and _rounds_to(mine, others[0]):
            why = _t("это среднее другой переменной", "that is the mean of the other variable")
        print(f"{NO} {label}: " + (why or _t(
            "обе прямые проходят через точку средних — она у них общая",
            "both lines pass through the mean point: it is the one they share")))
        return False
    order = [sp.Symbol(str(n)) for n in (order or names)]
    if not isinstance(got, (tuple, list, sp.Tuple)) or len(got) != 2:
        print(f"{NO} {label}: " + _t(
            f"ответ — пара ({order[0]}, {order[1]})", f"the answer is a pair ({order[0]}, {order[1]})"))
        return False
    mine = [_as_number(value) for value in got]
    want = [point[key] for key in order]
    if None not in mine and all(_rounds_to(m, w) for m, w in zip(mine, want)):
        print(f"{OK} {label}: ({_say(got[0])}, {_say(got[1])})")
        return True
    if None not in mine and all(_rounds_to(m, w) for m, w in zip(mine, want[::-1])):
        why = _t(f"координаты переставлены: порядок ({order[0]}, {order[1]})",
                 f"the coordinates are swapped: the order is ({order[0]}, {order[1]})")
    else:
        why = _t("обе прямые проходят через точку средних — она у них общая",
                 "both lines pass through the mean point: it is the one they share")
    print(f"{NO} {label}: " + why)
    return False


_EFFECT_WORDS = {'no effect': 'none', 'none': 'none', 'unchanged': 'none', 'same': 'none',
                 'no change': 'none', 'increases': 'up', 'increase': 'up', 'up': 'up',
                 'decreases': 'down', 'decrease': 'down', 'down': 'down'}


def verify_effect(label, got, P, change, which='x'):
    """Как изменится r, если все значения одной переменной пересчитать.

    change — что делают с каждым значением: `lambda h: h - 3`. Проверка
    так и делает и считает r заново.
    """
    if _blank(label, got):
        return False
    mine = _EFFECT_WORDS.get(str(got).strip().lower())
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — 'no effect', 'increases' или 'decreases'",
                                    "the answer is 'no effect', 'increases' or 'decreases'"))
        return False
    before = strength(P)
    if which == P.names[0]:
        moved = _Pairs([change(v) for v in P.xs], P.ys, P.names)
    else:
        moved = _Pairs(P.xs, [change(v) for v in P.ys], P.names)
    after = strength(moved)
    truth = 'none' if abs(after - before) < 1e-9 else ('up' if after > before else 'down')
    if mine == truth:
        print(f"{OK} {label}: {got}")
        return True
    if truth == 'none':
        print(f"{NO} {label}: " + _t(
            f"r после правки тот же, {after:.3f}: сдвиг двигает облако точек, а не меняет его форму",
            f"r is the same after the change, {after:.3f}: a shift moves the cloud of points, "
            f"it does not change its shape"))
    else:
        print(f"{NO} {label}: " + _t(f"после такой правки данных r = {after:.3f}, а было {before:.3f}",
                                    f"after this change to the data r = {after:.3f}; it was {before:.3f}"))
    return False


_REASONS = {'extrapolation': 'extrapolation', 'extrapolate': 'extrapolation',
            'outside': 'extrapolation', 'wrong line': 'wrong line', 'line': 'wrong line',
            'other line': 'wrong line'}


def verify_reason(label, got, P, at, given, predict):
    """Почему подстановка не годится: 'extrapolation' или 'wrong line'.

    given — какая переменная известна (её значение at), predict — какую
    предсказывают прямой y на x. Проверка сама смотрит, лежит ли at внутри
    данных и та ли прямая взята.
    """
    if _blank(label, got):
        return False
    mine = _REASONS.get(str(got).strip().lower())
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — 'extrapolation' или 'wrong line'",
                                    "the answer is 'extrapolation' or 'wrong line'"))
        return False
    known = _numbers(P.column(str(given)))
    outside = not (min(known) <= float(at) <= max(known))
    wrong = str(predict) != P.names[1]
    truths = ({'extrapolation'} if outside else set()) | ({'wrong line'} if wrong else set())
    if mine in truths:
        print(f"{OK} {label}: {mine}")
        return True
    if not truths:
        why = _t("этот ход здесь годится", "this method is fine here")
    elif mine == 'extrapolation':
        why = _t(f"{given} = {_say(at)} лежит внутри данных, от {_say(min(known))} "
                 f"до {_say(max(known))}",
                 f"{given} = {_say(at)} lies inside the data, from {_say(min(known))} "
                 f"to {_say(max(known))}")
    else:
        why = _t("прямая та самая: она и предсказывает эту переменную",
                 "the line is the right one: it predicts this very variable")
    print(f"{NO} {label}: " + why)
    return False


def check_word(label, got, want_digest):
    """Ответ — слово или буква варианта, которые не из чего вычислить."""
    if _blank(label, got):
        return False
    word = str(got).strip().lower()
    if digest(word) == want_digest:
        print(f"{OK} {label}: {word}")
        return True
    print(f"{NO} {label}: {word} — " + _t("не тот ответ", "not this one"))
    return False
