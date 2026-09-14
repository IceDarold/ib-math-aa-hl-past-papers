"""Таблица распределения (D4): буквы в клетках, множество значений, мода, G(t).
"""

import contextlib
import io
import math

import sympy as sp
from mpmath.libmp.libhyper import NoConvergence as mpmath_NoConvergence

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .algebra import _as_set, _pieces, _show_set
from .sequences import blank
from .probability import _Prob
from .distribution import (
    _Draw, _draw_agree, _Linear, _moment, _Variable, verify_binomial,
)


# ================================================== таблица распределения
# Двадцать первое понятие равенства ответов: таблица сама себе условие.
#
# В D3 распределение задавала модель, и проверка знала P(X = k) по формуле.
# В D4 его задаёт таблица, и в таблице стоят буквы. Проверке не нужен
# эталон: у таблицы есть два собственных правила — каждая вероятность лежит
# в [0, 1], и все вместе они дают единицу, — и вопрос добавляет к ним своё
# (E(X) = 2,3, P(X < Y) = 1/2). Буквы — это решения этих условий, найденные
# самой проверкой, а корень, при котором клетка таблицы уходит в минус,
# решением не считается, и проверка говорит, какая клетка.
#
# Всё остальное снова складывается по значениям: среднее, дисперсия, мода,
# вероятность события. У геометрического распределения значений бесконечно
# много, и сумму ряда складывает sympy — 1/p внутри не написано. Производящая
# функция — та же таблица, записанная многочленом, и сверяется она
# коэффициент за коэффициентом.
#
# Величина, о которой известны только E(T) и Var(T), заменяется таблицей
# из двух равновероятных значений μ ± σ. Среднее и дисперсия aT + b
# зависят только от E(T) и Var(T), так что любая таблица с теми же двумя
# числами даёт тот же ответ, а сложение по значениям остаётся сложением.

_LETTER_TOL = 1e-9


class _Table(_Variable):
    """Величина, заданная таблицей: значение → вероятность (или частота).

    Вероятности и значения могут содержать буквы. Десятичные дроби
    переводятся в точные: 0,41 — это 41/100, и сумма таблицы тогда
    проверяется точно, а не с допуском.
    """

    def __init__(self, table, name='X', counts=False, parts=(), stand_in=None):
        self.name = name
        self.counts = counts
        self.parts = tuple(parts)
        self.stand_in = stand_in
        self.shown = dict(table)
        self._blank = any(key is Ellipsis or value is Ellipsis
                          for key, value in table.items())
        if self._blank:
            self.table, self.size = {}, None
            return
        merged = {}
        for key, value in table.items():
            key = _exact(key)
            value = _exact(value)
            for seen in merged:
                if sp.simplify(seen - key) == 0:
                    merged[seen] = merged[seen] + value
                    break
            else:
                merged[key] = value
        self.weights = merged
        if counts:
            self.size = sp.Add(*merged.values())
            self.table = {key: value / self.size for key, value in merged.items()}
        else:
            self.size = None
            self.table = merged

    def blank(self):
        return self._blank or any(part.blank() for part in self.parts)

    def values(self):
        keys = list(self.table)
        if all(key.is_number for key in keys):
            keys.sort(key=float)
        return keys

    def chance(self, k, p=None):
        """P(X = k) — то, что стоит в клетке таблицы."""
        for key, value in self.table.items():
            if key is k or sp.simplify(key - k) == 0:
                return value
        return sp.Integer(0)

    def rules(self):
        if self.parts:
            return [rule for part in self.parts for rule in part.rules()]
        if self.counts:
            return [(_t(f"частота значения {key}", f"the frequency of {key}"), value, 'count')
                    for key, value in self.weights.items()]
        return [(f"P({self.name} = {key})", value, 'prob')
                for key, value in self.table.items()]

    def __repr__(self):
        if self.stand_in is not None:
            mean, spread = self.stand_in
            return f"{self.name}: E({self.name}) = {mean}, Var({self.name}) = {spread}"
        cells = ', '.join(f"{key}: {value}" for key, value in self.shown.items())
        return f"{self.name} ~ {{{cells}}}"


def _exact(value):
    """Десятичную дробь — в точную, буквы оставить буквами."""
    value = sp.sympify(value)
    if value.has(sp.Float):
        value = sp.nsimplify(value, rational=True)
    return value


def Dist(table, name='X', rule=None):
    """Дискретная величина по таблице: `Dist({0: 0.41, 1: k - 0.28, ...})`.

    Таблицу можно не выписывать, а получить из опыта: `rule` переводит
    исход в значение, и вероятности исходов с одним значением складываются.
    Два кубика и их максимум — `Dist(dice, rule=max, name='M')`, где
    `dice` — словарь «пара очков → 1/16».

    `Dist(X + Y, name='Z')` — просто даёт сумме имя.
    """
    if isinstance(table, _Table):
        return _Table(table.shown, name, table.counts, table.parts, table.stand_in)
    if rule is not None:
        gathered = {}
        for outcome, weight in table.items():
            value = sp.sympify(rule(outcome))
            gathered[value] = gathered.get(value, 0) + sp.sympify(weight)
        table = gathered
    return _Table(table, name)


def Freq(table, name='X'):
    """Таблица частот как распределение: `Freq({0: 6, 1: 16, 2: 13})`.

    Вероятность значения — его доля, f/Σf. Среднее и дисперсия таблицы
    частот и есть E и Var этого распределения; дисперсия делится на Σf,
    а не на Σf − 1, как и в IB. `X.size` — сколько всего наблюдений.
    """
    if not any(key is Ellipsis for key in table):
        # класс 15 < y ≤ 20 читается серединой, как в IB
        table = {(key.start + key.end) / 2 if isinstance(key, sp.Interval) else key: value
                 for key, value in table.items()}
    return _Table(table, name, counts=True)


def Moments(mean, variance, name='T'):
    """Величина, о которой известны только E и Var: `Moments(4.723, 0.906)`.

    Внутри — два равновероятных значения μ ± σ. Этого достаточно для
    среднего и дисперсии любого aT + b, и ничего другого у такой величины
    не спрашивают: P(T < 3) по ней не посчитать, и проверка это запрещает.
    """
    if blank(mean, variance):
        return _Table({...: ...}, name)
    centre, spread = _exact(mean), _exact(variance)
    step = sp.sqrt(spread)
    half = sp.Rational(1, 2)
    return _Table({centre - step: half, centre + step: half}, name,
                  stand_in=(mean, variance))


def _sum_of(first, second):
    """X + Y для независимых X и Y: по парам значений, с произведением вероятностей."""
    for var in (first, second):
        if isinstance(var, (_Curve, _Mapped, _Density)):
            raise TypeError(_t('сумма непрерывных величин здесь не складывается',
                               'a sum of continuous variables is not added up here'))
        if isinstance(var, _Series):
            raise TypeError(_t('сумма с величиной без последнего значения здесь не складывается',
                               'a sum with a variable that has no last value is not added up here'))
    if first.blank() or second.blank():
        return _Table({...: ...}, f"{first.name} + {second.name}")
    table = {}
    for one in first.values():
        for two in second.values():
            key = sp.sympify(one + two)
            table[key] = table.get(key, 0) + first.chance(one) * second.chance(two)
    return _Table(table, f"{first.name} + {second.name}", parts=(first, second))


class _Series(_Variable):
    """X ~ Geo(p): номер испытания, на котором случился первый успех.

    Значений бесконечно много, поэтому среднее и дисперсию нельзя сложить
    циклом — их складывает sympy как ряд Σ x·P(X = x). Ответ ряда верен
    при 0 < p < 1, и берётся именно эта ветвь.
    """

    def __init__(self, p, name='X'):
        self.name = name
        self.p = p if p is Ellipsis else _exact(p)
        self._sums = {}

    def blank(self):
        return self.p is Ellipsis

    def values(self):
        raise TypeError(_t('у этой величины значений бесконечно много: событие над '
                           'ней здесь не складывается',
                           'this variable has infinitely many values: an event about '
                           'it is not added up here'))

    def chance(self, k, p=None):
        """P(X = k): k − 1 неудача подряд, потом успех."""
        return self.p * (1 - self.p) ** (k - 1)

    def rules(self):
        return [(_t('вероятность успеха', 'the probability of success'), self.p, 'prob')]

    def add_up(self, term):
        """Σ term(j)·P(X = j) по j = 1, 2, 3, …"""
        index = sp.Symbol('j', integer=True, positive=True)
        key = sp.srepr(term(index))
        if key not in self._sums:
            total = sp.piecewise_fold(sp.summation(term(index) * self.chance(index),
                                                   (index, 1, sp.oo)))
            if isinstance(total, sp.Piecewise):
                total = total.args[0][0]           # ветвь, где ряд сходится
            if total.has(sp.Sum):
                raise ValueError(_t('ряд не сложился', 'the series did not add up'))
            self._sums[key] = sp.simplify(total)
        return self._sums[key]

    def moment(self, kind, a, b):
        if kind == 'square':
            return self.add_up(lambda j: (a * j + b) ** 2)
        mean = self.add_up(lambda j: a * j + b)
        if kind == 'mean':
            return mean
        return self.add_up(lambda j: (a * j + b - mean) ** 2)

    def __repr__(self):
        return f"{self.name} ~ Geo({self.p})"


def Geo(p, name='X'):
    """Первый успех на X-м испытании: P(X = x) = p(1 − p)^(x − 1), x = 1, 2, …"""
    return _Series(p, name)


def total_probability(X):
    """Сумма всех вероятностей таблицы — то, что обязано быть единицей."""
    if X.blank():
        return Ellipsis
    if isinstance(X, _Density):
        # у плотности — площадь над всей осью: событие «X < 0 или X ≥ 0»
        return _area_of(('or', ('leaf', X, '<', sp.Integer(0)), ('leaf', X, '>=', sp.Integer(0))))
    whole = sp.Add(*[X.chance(v) for v in X.values()])
    return _Prob(whole, 'whole', (X,), f"ΣP({X.name} = x)")


def Pgf(X, var=t):
    """G(t) = Σ P(X = x)·tˣ — таблица, записанная многочленом."""
    if X.blank():
        return Ellipsis
    return sp.Add(*[X.chance(v) * var ** v for v in _whole_values(X)])


def _whole_values(X):
    listed = list(X.values())
    if not all(v.is_integer and v >= 0 for v in listed):
        raise ValueError(_t('производящая функция пишется для величин со значениями 0, 1, 2, …',
                            'a generating function is for variables taking the values 0, 1, 2, …'))
    return listed


def verify_chance(label, got, find, given=None, var=None, sf=None, percent=False,
                  free=None):
    """Ответ — вероятность события над величинами: `P(rides >= 1)`, `P(X < Y)`.

    То же, что `verify_binomial` из D3, для любых величин — таблиц, частот,
    сумм. Сравнение в событии помнит свою границу, и неверный ответ
    разбирается по ней: «X ≥ 1 включает само 1».

    Для нормальной величины (D5) вероятность — площадь, и параметров
    больше. `given` и `var` — условия, из которых проверка сама находит
    буквы модели: σ по «2 % дольше 82 минут». `sf` — вопрос просит
    столько значащих цифр, и не больше. `percent=True` — ответ в процентах.
    `free` — буква, от которой ответ не зависит и должен годиться при
    любом её значении. `find` может быть и выражением из площадей:
    `0.6*P(C < 61) + 0.4*P(B < 61)`.
    """
    if _blank(label, got, find):
        return False
    curve = isinstance(find, sp.Basic) or (
        isinstance(find, _Prob) and find.args and isinstance(find.args[0], _Draw)
        and _is_curve(find.args[0].node))
    if not curve:
        return verify_binomial(label, got, find)
    return _verify_curve_chance(label, got, find, given, var, sf, percent, free)


# ---------------------------------------------------------------- буквы

def _as_unknowns(var):
    if var is None:
        return []
    if isinstance(var, (list, tuple, set)):
        return list(var)
    return [var]


def _as_conditions(given):
    if given is None:
        return []
    if isinstance(given, (list, tuple)):
        return list(given)
    return [given]


def _residual(item):
    """Условие → выражение, обращающееся в ноль. True — нет условия, False — нет решений."""
    if isinstance(item, (tuple, list)):
        item = sp.Eq(sp.sympify(item[0]), sp.sympify(item[1]), evaluate=False)
    item = sp.sympify(item)
    if item is sp.true:
        return None
    if item is sp.false:
        return sp.Integer(1)
    if isinstance(item, sp.Equality):
        item = item.lhs - item.rhs
    return _exact(item)


def _system_roots(polys, unknowns):
    """Все действительные решения системы многочленов. None — решений бесконечно много.

    Базис Грёбнера в лексикографическом порядке ставит последним многочлен
    от одной последней буквы; его корни ищутся численно, подставляются, и
    так буква за буквой.
    """
    if not unknowns:
        return [{}]
    if not polys:
        return None
    basis = sp.groebner(polys, *unknowns, order='lex')
    exprs = list(basis.exprs)
    if exprs == [1]:
        return []
    runs = [{}]
    for letter in reversed(unknowns):
        following = []
        for run in runs:
            here = [sp.expand(e.subs(run)) for e in exprs]
            here = [e for e in here if not (e.is_number and abs(complex(e)) < 1e-12)]
            alone = [e for e in here if e.free_symbols == {letter}]
            if not alone:
                return None
            base = min(alone, key=lambda e: sp.Poly(e, letter).degree())
            for root in _poly_roots(sp.Poly(base, letter)):
                number = complex(root)
                if abs(number.imag) > 1e-9 * max(1.0, abs(number)):
                    continue
                value = sp.Float(number.real, 30)
                scale = max([1.0] + [abs(float(c)) for e in alone
                                     for c in sp.Poly(e, letter).coeffs()])
                if all(abs(complex(e.subs(letter, value))) < 1e-7 * scale for e in alone):
                    if not any(abs(float(old[letter] - value)) < 1e-12 and
                               all(old[u] == run[u] for u in run) for old in following):
                        following.append({**run, letter: value})
        runs = following
    return runs


def _poly_roots(poly):
    """Корни многочлена численно.

    Кратный корень численный поиск находит плохо — знаменатель q + 20
    таблицы частот входит в условия квадратом, и корень −20 у многочлена
    двойной. Поэтому у точного многочлена кратность сначала снимается.
    """
    if all(c.is_Rational for c in poly.all_coeffs()):
        poly = poly.sqf_part()
    for digits, steps in ((30, 200), (30, 2000), (15, 5000)):
        try:
            return poly.nroots(n=digits, maxsteps=steps)
        except mpmath_NoConvergence:
            continue
    return [root for root in sp.polys.polyroots.roots(poly, multiple=True)]


def _broken_rule(run, variables, unknowns):
    """Что сломано в таблице при этих буквах, или None, если ничего."""
    for var in variables:
        if isinstance(var, _Density):
            broken = var.broken(run)
            if broken is not None:
                return broken
            continue
        for what, expr, kind in var.rules():
            value = sp.sympify(expr).subs(run)
            if value.free_symbols:
                continue
            number = complex(sp.N(value, 30))
            if abs(number.imag) > _LETTER_TOL:
                return what, None, kind
            if kind == 'prob' and not -_LETTER_TOL <= number.real <= 1 + _LETTER_TOL:
                return what, number.real, kind
            if kind == 'count' and number.real < -_LETTER_TOL:
                return what, number.real, kind
            if kind == 'sd' and number.real <= _LETTER_TOL:
                return what, number.real, kind
    for letter in unknowns:
        if letter not in run:
            continue
        value = float(run[letter])
        if letter.is_integer and abs(value - round(value)) > 1e-7:
            return str(letter), value, 'whole'
        if letter.is_positive and value <= _LETTER_TOL:
            return str(letter), value, 'positive'
        if letter.is_nonnegative and value < -_LETTER_TOL:
            return str(letter), value, 'positive'
    return None


def _rule_words(broken):
    what, value, kind = broken
    shown = '' if value is None else f" = {sig(value, 4)}"
    if kind == 'prob' and value is not None and value < 0:
        return _t(f"{what}{shown}, а вероятность не бывает отрицательной",
                  f"{what}{shown}, and a probability is never negative")
    if kind == 'prob':
        return _t(f"{what}{shown}, а вероятность не бывает больше единицы",
                  f"{what}{shown}, and a probability is never above one")
    if kind == 'count':
        return _t(f"{what}{shown}, а частота не бывает отрицательной",
                  f"{what}{shown}, and a frequency is never negative")
    if kind == 'sd':
        return _t(f"{what}{shown}, а стандартное отклонение положительно",
                  f"{what}{shown}, and a standard deviation is positive")
    if kind == 'density' and value is None:
        return _t(f"{what} не действительное число, а плотность — число",
                  f"{what} is not a real number, and a density is a number")
    if kind == 'density':
        return _t(f"{what}{shown}, а плотность не бывает отрицательной",
                  f"{what}{shown}, and a density is never negative")
    if kind == 'whole':
        return _t(f"{what}{shown}, а по условию это целое число",
                  f"{what}{shown}, and the question says it is a whole number")
    return _t(f"{what}{shown}, а по условию это положительное число",
              f"{what}{shown}, and the question says it is positive")


def _letter_runs(conditions, unknowns, variables=()):
    """Решения условий вопроса: годные и отброшенные вместе с причиной.

    К условиям вопроса сами добавляются условия таблиц: вероятности
    складываются в единицу. Возвращает (годные, [(отброшенное, причина)]),
    или (None, None), если условий не хватает.
    """
    unknowns = list(unknowns)
    residuals = []
    for item in conditions:
        residual = _residual(item)
        if residual is not None:
            residuals.append(residual)
    for var in variables:
        if isinstance(var, _Table) and not var.counts and not var.parts:
            residuals.append(sp.Add(*[var.chance(v) for v in var.values()]) - 1)
        if isinstance(var, _Density) and var.letters:
            # площадь под плотностью — единица, как сумма таблицы в D4
            residuals.append(total_probability(var) - 1)
    if any(isinstance(var, (_Curve, _Mapped, _Density)) for var in variables) or \
            any(sp.sympify(r).has(_Area) for r in residuals):
        # площади не многочлены: буквы ищет Ньютон, D5
        roots = _curve_roots([sp.sympify(r) for r in residuals], unknowns, variables)
    else:
        polys = []
        for residual in residuals:
            top = sp.expand(sp.numer(sp.together(sp.sympify(residual))))
            if top != 0:
                polys.append(top)
        roots = _system_roots(polys, unknowns)
    if roots is None:
        return None, None
    good, bad = [], []
    for run in roots:
        broken = _broken_rule(run, variables, unknowns)
        if broken is None:
            good.append(run)
        else:
            bad.append((run, broken))
    return good, bad


def _rounded_runs(run):
    """Те же буквы, округлённые так, как их округляют по дороге."""
    if not run:
        return []
    out = []
    try:
        three = {u: sp.Float(sig(v, 3)) for u, v in run.items()}
        whole = {u: sp.Integer(round(float(v))) for u, v in run.items()}
    except (TypeError, ValueError):
        return out
    names = ', '.join(str(u) for u in run)
    out.append((three, _t(f"{names} до трёх значащих цифр", f"{names} to three figures")))
    if whole != three:
        out.append((whole, _t(f"{names} до целого", f"{names} to the nearest whole number")))
    return out


def _letters_in(variables, conditions):
    found = set()
    for var in variables:
        if isinstance(var, _Density):
            found |= set(var.letters)
            continue
        for _, expr, _ in var.rules():
            found |= sp.sympify(expr).free_symbols
        if isinstance(var, _Table):
            for key in var.values():
                found |= sp.sympify(key).free_symbols
    for item in conditions:
        residual = _residual(item)
        if residual is not None:
            found |= residual.free_symbols
    return sorted(found, key=str)


def _pinned(variables, run):
    """Те же величины, где часть букв заменена числами."""
    out = []
    for var in variables:
        if isinstance(var, _Curve):
            out.append(_Curve(sp.sympify(var.mean).subs(run), sp.sympify(var.variance).subs(run),
                              var.name, var.rule))
        elif isinstance(var, _Density):
            out.append(var.pinned(run))
        else:
            out.append(var)
    return out


def _free_runs(free):
    """Наборы значений свободных букв: буква, список букв или готовые наборы."""
    if isinstance(free, (list, tuple)) and free and all(isinstance(item, dict) for item in free):
        return [{sp.sympify(u): sp.sympify(v) for u, v in item.items()} for item in free]
    loose = _as_unknowns(free)
    return [{letter: sp.Float(sample) for letter in loose} for sample in _FREE_SAMPLES]


def verify_letters(label, got, unknowns, variables, conditions=(), whole=False,
                   sf=None, free=None, exact=False):
    """Ответ — буквы таблицы: `verify_letters('2b', 0.3, k, [X])`.

    Условия — те, что даёт вопрос (`Eq(Expect(X), 2.3)`); условие «таблица
    складывается в единицу» проверка добавляет сама. Решает она их сама же,
    все буквы сразу, даже если спрашивают одну, — и отбрасывает решения,
    при которых таблица перестаёт быть таблицей вероятностей.

    Ответ, совпавший с отброшенным корнем, получает имя клетки, которая
    при нём ломается: «P(X = 1) = −0,08». За эту фразу схема оценивания
    даёт отдельный балл R1.

    `whole=True` — вопрос просит буквы до целого.

    С нормальной величиной (D5) условия — площади: `Eq(P(T > 82), 0.02)`,
    и буквы ищутся численно; отбрасываются решения с σ ≤ 0. `sf` — вопрос
    просит столько значащих цифр, и не больше. `free` — буква модели,
    которую вопрос оставляет свободной: ответ обязан годиться при любом её
    значении, и проверка пробует несколько.

    С плотностью (D6) условие «площадь под ней — единица» добавляется само,
    как сумма таблицы. Медиана и квартиль — тоже буквы: `Eq(P(X < m), 0.5)`.
    Ответ может быть выражением от свободных букв («a через b», «медиана
    через a, b и c»); тогда `free` — буква или список готовых наборов
    `[{a: 0, b: 4, c: 3}, ...]`, если значения букв связаны условием.
    `exact=True` — вопрос Paper 1 просит точное значение.
    """
    if _blank(label, got):
        return False
    if free is not None and _as_unknowns(free):
        verdict = True
        for run in _free_runs(free):
            fixed = [sp.sympify(c).subs(run) for c in conditions]
            pinned = _pinned(variables, run)
            given = [sp.sympify(item).subs(run) for item in got] if isinstance(got, (list, tuple)) \
                else sp.sympify(got).subs(run)
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                verdict = verify_letters(label, given, unknowns, pinned, fixed, whole, sf,
                                         exact=exact)
            if not verdict:
                shown = ', '.join(f"{u} = {sig(v, 4)}" for u, v in run.items())
                print(buffer.getvalue().rstrip() + _t(f" (при {shown})", f" (at {shown})"))
                return False
        if isinstance(got, (list, tuple)) or not sp.sympify(got).free_symbols:
            print(buffer.getvalue().rstrip())
        else:
            print(f"{OK} {label}: {got}")
        return True
    names = _as_unknowns(unknowns)
    given = list(got) if isinstance(got, (list, tuple)) else [got]
    if len(given) != len(names):
        print(f"{NO} {label}: " + _t(f"букв {len(names)}, а значений {len(given)}",
                                     f"there are {len(names)} letters and {len(given)} values"))
        return False
    numbers = []
    for item in given:
        try:
            value = sp.sympify(item)
        except (sp.SympifyError, TypeError):
            value = None
        if value is None or value.free_symbols or not value.is_number:
            print(f"{NO} {label}: " + _t("буква — это число", "each letter is a number"))
            return False
        numbers.append(value)
    conditions = list(conditions)
    letters = _letters_in(variables, conditions)
    for name in names:
        if name not in letters:
            letters.append(name)
    good, bad = _letter_runs(conditions, letters, variables)
    if good is None:
        print(f"{NO} {label}: " + _t("условий не хватает, чтобы найти буквы",
                                     "the conditions are not enough to fix the letters"))
        return False

    def agree(value, want):
        if whole:
            return value.is_integer and int(value) == round(float(want))
        return _sf_agree(value, want, sf)

    def matches(run):
        return all(agree(value, run[name]) for name, value in zip(names, numbers))

    shown = ', '.join(f"{n} = {sig(v, 6)}" for n, v in zip(names, numbers))
    plain_shown = ', '.join(f"{n} = {sig(v, 6) if isinstance(v, (float, sp.Float)) else v}"
                            for n, v in zip(names, given))
    if any(matches(run) for run in good):
        wanted = {tuple(sig(run[n], 6) for n in names) for run in good}
        if len(wanted) > 1:
            print(f"{NO} {label}: " + _t(
                f"это одно из решений, а годных решений {len(wanted)}",
                f"that is one of the solutions, and {len(wanted)} of them are valid"))
            return False
        if sf is not None and any(float(v) != float(sig(v, sf)) for v in numbers):
            print(f"{NO} {label}: " + _sf_words(sf))
            return False
        if exact and not _exact_letters(label, names, numbers, good):
            return False
        print(f"{OK} {label}: {plain_shown}")
        return True
    for run, broken in bad:
        if matches(run):
            print(f"{NO} {label}: " + _t(
                f"{shown} удовлетворяет уравнениям, но при этом {_rule_words(broken)}. "
                f"Такое решение отбрасывают",
                f"{shown} satisfies the equations, but then {_rule_words(broken)}. "
                f"That solution is rejected"))
            return False
    if sf is not None and any(all(_draw_agree(v, run[n]) for n, v in zip(names, numbers))
                              for run in good):
        print(f"{NO} {label}: " + _sf_words(sf))
        return False
    if not whole and sf is None and any(
            all(sig(v, 2) == sig(run[n], 2) and float(sig(v, 2)) == float(v)
                for n, v in zip(names, numbers)) for run in good):
        print(f"{NO} {label}: " + _t("две значащие цифры, а нужны три",
                                     "two significant figures, and three are needed"))
        return False
    if whole and any(all(_draw_agree(v, run[n]) for n, v in zip(names, numbers))
                     for run in good):
        print(f"{NO} {label}: " + _t("вопрос просит ответ до целого",
                                     "the question asks for whole numbers"))
        return False
    curve = any(isinstance(var, (_Curve, _Mapped, _Density)) for var in variables)
    dense = [var for var in variables if isinstance(var, _Density)]
    if curve and good:
        # граница, найденная по площади с другой стороны: invNorm(0,2)
        # там, где «больше w с вероятностью 0,2» требует 0,8 слева
        for number, item in enumerate(conditions):
            eq = sp.sympify(item)
            if not (isinstance(eq, sp.Equality) and isinstance(eq.lhs, _Area)
                    and 'node' in _AREAS[int(eq.lhs.args[0])]):
                continue
            flipped = list(conditions)
            flipped[number] = sp.Eq(1 - eq.lhs, eq.rhs)
            runs, _ = _letter_runs(flipped, letters, variables)
            if runs and any(matches(run) for run in runs):
                print(f"{NO} {label}: " + (_t(
                    "здесь площадь набрана с другой стороны: нижний квартиль — "
                    "четверть площади слева, а не справа",
                    "this collects the area from the other side: the lower quartile "
                    "has a quarter of the area to its left, not to its right") if dense else _t(
                    "здесь взята площадь с другой стороны от границы: калькулятор "
                    "и invNorm считают площадь слева, и «больше» надо перевести в "
                    "1 − данное",
                    "this uses the area on the other side of the boundary: invNorm "
                    "works with the area to the left, so «more than» becomes 1 − the "
                    "given area")))
                return False
    if dense and good and len(names) == 1:
        said = _density_letter_slips(dense[0], names[0], numbers[0], conditions, good[0], agree)
        if said:
            print(f"{NO} {label}: {said}")
            return False
    if not good:
        print(f"{NO} {label}: " + (_t("условиям не отвечает ни одна годная модель",
                                      "no valid model satisfies the conditions") if curve else
                                   _t("условиям не отвечает ни одна годная таблица",
                                      "no valid table satisfies the conditions")))
        return False
    if len(names) == len(letters):
        run = dict(zip(names, numbers))
        for var in variables:
            if isinstance(var, _Density) and var.letters:
                try:
                    whole_area = sp.sympify(total_probability(var)).subs(run)
                    whole_area = float(whole_area)
                except (TypeError, ValueError):
                    whole_area = None
                if whole_area is not None and not math.isnan(whole_area) \
                        and not _draw_agree(whole_area, 1):
                    print(f"{NO} {label}: " + _t(
                        f"при {shown} площадь под плотностью {var.name} равна "
                        f"{sig(whole_area, 4)}, а должна быть 1",
                        f"with {shown} the area under the density of {var.name} is "
                        f"{sig(whole_area, 4)}, and it has to be 1"))
                    return False
            if isinstance(var, _Table) and not var.counts and not var.parts:
                whole_sum = sp.Add(*[var.chance(v) for v in var.values()]).subs(run)
                if not _draw_agree(whole_sum, 1):
                    print(f"{NO} {label}: " + _t(
                        f"при {shown} вероятности {var.name} складываются в "
                        f"{sig(whole_sum, 4)}, а не в 1",
                        f"with {shown} the probabilities of {var.name} add up to "
                        f"{sig(whole_sum, 4)}, not 1"))
                    return False
        for number, item in enumerate(conditions, start=1):
            residual = _residual(item)
            if residual is None:
                continue
            eq = sp.sympify(item)
            left = eq.lhs.subs(run) if isinstance(eq, sp.Equality) else residual.subs(run)
            right = eq.rhs.subs(run) if isinstance(eq, sp.Equality) else 0
            if not _draw_agree(left, right):
                which = _t(f"условие вопроса номер {number}", f"the question's condition number {number}") \
                    if len(conditions) > 1 else _t("условие вопроса", "the question's condition")
                print(f"{NO} {label}: " + _t(f"при {shown} не выполнено {which}",
                                             f"with {shown} {which} fails"))
                return False
    print(f"{NO} {label}: " + (_t("с этими значениями модель не выполняет условий вопроса",
                                  "with these values the model does not meet the conditions")
                               if curve else
                               _t("с этими значениями таблица не выполняет условий вопроса",
                                  "with these values the table does not meet the conditions")))
    return False


# --------------------------------------------------------- множество значений

def _same_set(one, two):
    """Два объединения промежутков совпадают — концы с точностью до трёх цифр."""
    if one == two:
        return True
    left, right = _pieces(one), _pieces(two)
    if left is None or right is None or len(left) != len(right):
        return False
    for (a1, b1, lo1, ro1), (a2, b2, lo2, ro2) in zip(left, right):
        if (lo1, ro1) != (lo2, ro2):
            return False
        if not (_draw_agree(a1, a2) and _draw_agree(b1, b2)):
            return False
    return True


def _feasible_set(letter, variables, others=()):
    """Где может лежать буква, чтобы каждая клетка была вероятностью."""
    region = sp.S.Reals
    for var in variables:
        for _, expr, kind in var.rules():
            expr = sp.sympify(expr)
            if expr.free_symbols - {letter}:
                continue
            if not expr.free_symbols:
                continue
            upper = 1 if kind == 'prob' else sp.oo
            here = (expr >= 0).as_set()
            if upper != sp.oo:
                here = sp.Intersection(here, (expr <= upper).as_set())
            region = sp.Intersection(region, here)
    return region


def verify_table_range(label, got, target, variables):
    """Ответ — все возможные значения буквы или E(X): `Interval(0, 1/3)`.

    Проверка исключает лишние буквы условием «таблица складывается
    в единицу», требует от каждой клетки лежать в [0, 1] и получает
    множество сама. Для E(X) — образ этого множества.

    Промахи с именем: клетки взяты по отдельности, без суммы; концы
    выколоты, хотя вероятность бывает и нулём, и единицей.
    """
    if _blank(label, got, target):
        return False
    letters = _letters_in(variables, ())
    as_letter = isinstance(target, sp.Symbol)
    free = target if as_letter else (letters[0] if letters else None)
    if free is None:
        print(f"{NO} {label}: " + _t("в таблице нет букв", "the table has no letters"))
        return False
    others = [u for u in letters if u != free]
    sums = [sp.Add(*[var.chance(v) for v in var.values()]) - 1
            for var in variables if isinstance(var, _Table) and not var.counts]
    sums = [s for s in sums if s.free_symbols]
    fix = {}
    if others:
        solved = sp.solve(sums, others, dict=True)
        if len(solved) != 1 or set(solved[0]) != set(others):
            print(f"{NO} {label}: " + _t("условий не хватает, чтобы свести таблицу к одной букве",
                                         "the conditions do not reduce the table to one letter"))
            return False
        fix = solved[0]
    reduced = [_Table({key: sp.sympify(value).subs(fix) for key, value in var.table.items()},
                      var.name) for var in variables]
    region = _feasible_set(free, reduced)
    if as_letter:
        truth = region
        loose = _feasible_set(free, variables)
    else:
        expr = sp.sympify(target).subs(fix)
        from sympy.calculus.util import function_range
        truth = function_range(expr, free, region)
        loose = None
    try:
        mine = _as_set(got, free)
    except (TypeError, ValueError):
        mine = None
    if mine is None and not as_letter:
        value = sp.sympify(got)
        if isinstance(value, sp.core.relational.Relational) or isinstance(value, sp.And):
            symbols_here = list(value.free_symbols)
            mine = value.as_set() if len(symbols_here) == 1 else None
    if mine is None:
        print(f"{NO} {label}: " + _t(
            "ответ — множество: Interval(0, 1) или (r >= 0) & (r <= 1)",
            "the answer is a set: Interval(0, 1) or (r >= 0) & (r <= 1)"))
        return False
    mine = sp.Intersection(mine, sp.S.Reals) if not isinstance(mine, sp.Interval) else mine
    if _same_set(mine, truth):
        print(f"{OK} {label}: {_show_set(truth, free) if as_letter else truth}")
        return True
    pieces = _pieces(truth)
    if pieces and len(pieces) == 1:
        a, b, _, _ = pieces[0]
        if _same_set(mine, sp.Interval(a, b, True, True)) and truth != sp.Interval(a, b, True, True):
            print(f"{NO} {label}: " + _t(
                "концы входят: вероятность бывает и нулём, и единицей",
                "the ends belong: a probability can be 0 or 1 itself"))
            return False
    if loose is not None and not _same_set(loose, truth) and _same_set(mine, loose):
        print(f"{NO} {label}: " + _t(
            "каждая клетка по отдельности лежит в [0, 1], но клетки ещё и "
            "складываются в единицу — это сужает множество",
            "each cell on its own lies in [0, 1], but the cells also add up "
            "to one, and that narrows the set"))
        return False
    extra = sp.Complement(mine, truth)
    if as_letter and extra is not sp.S.EmptySet:
        spots = _pieces(extra) or []
        for a, b, _, _ in spots:
            probe = (a + b) / 2 if a.is_finite and b.is_finite else (a + 1 if a.is_finite else b - 1)
            run = {free: probe, **{u: sp.sympify(e).subs(free, probe) for u, e in fix.items()}}
            broken = _broken_rule(run, variables, [])
            if broken is not None:
                print(f"{NO} {label}: " + _t(
                    f"при {free} = {sig(probe, 4)} {_rule_words(broken)}",
                    f"at {free} = {sig(probe, 4)} {_rule_words(broken)}"))
                return False
    if extra is not sp.S.EmptySet:
        print(f"{NO} {label}: " + _t("в ответе есть значения, которых быть не может",
                                     "the answer contains values that cannot occur"))
    else:
        print(f"{NO} {label}: " + _t("потеряны значения, которые возможны",
                                     "some possible values are missing"))
    return False


# ------------------------------------------------------------- мода и G(t)

def verify_mode(label, got, X, given=None, var=None):
    """Ответ — мода: значение с наибольшей вероятностью, а не сама вероятность."""
    if _blank(label, got, X):
        return False
    if isinstance(X, _Density):
        return _verify_density_mode(label, got, X, given, var)      # D6
    unknowns = _as_unknowns(var)
    if given is None and not unknowns:
        runs = [{}]
    else:
        runs, _ = _letter_runs(_as_conditions(given), unknowns, [X])
        runs = runs or []
    if not runs:
        print(f"{NO} {label}: " + _t("условиям не отвечает ни одна таблица",
                                     "no table satisfies the conditions"))
        return False
    value = sp.sympify(got)
    for run in runs:
        chances = {v: sp.N(sp.sympify(X.chance(v)).subs(run), 20) for v in X.values()}
        top = max(chances.values())
        modes = [v for v, c in chances.items() if abs(c - top) < 1e-12]
        if not any(_draw_agree(value, v) for v in modes):
            if _draw_agree(value, top):
                print(f"{NO} {label}: " + _t(
                    "это наибольшая вероятность, а мода — значение, у которого она",
                    "that is the largest probability; the mode is the value that has it"))
            else:
                print(f"{NO} {label}: " + _t(
                    f"у значения {value} вероятность не наибольшая",
                    f"the value {value} does not have the largest probability"))
            return False
    print(f"{OK} {label}")
    return True


def verify_pgf(label, got, X, var=t, given=None, unknowns=None):
    """Ответ — производящая функция G(t) = Σ P(X = x)·tˣ.

    Сверяется коэффициент за коэффициентом с таблицей величины, а таблицу
    проверка строит сама: из опыта (`Dist(..., rule=...)`) или из суммы
    независимых величин. Промахи с именем: G(1) не единица, коэффициенты
    в обратном порядке (посчитана противоположная величина), степени
    сдвинуты на одну.
    """
    if _blank(label, got, X):
        return False
    try:
        answer = sp.expand(sp.sympify(got))
    except (sp.SympifyError, TypeError):
        answer = None
    if answer is None or answer.free_symbols - {var}:
        print(f"{NO} {label}: " + _t(f"ответ — многочлен от {var} с числовыми коэффициентами",
                                     f"the answer is a polynomial in {var} with number coefficients"))
        return False
    try:
        mine = sp.Poly(answer, var)
    except sp.PolynomialError:
        print(f"{NO} {label}: " + _t(f"это не многочлен от {var}",
                                     f"that is not a polynomial in {var}"))
        return False
    letters = _as_unknowns(unknowns)
    if given is None and not letters:
        runs = [{}]
    else:
        runs, _ = _letter_runs(_as_conditions(given), letters, [X])
        runs = runs or []
    if not runs:
        print(f"{NO} {label}: " + _t("условиям не отвечает ни одна таблица",
                                     "no table satisfies the conditions"))
        return False
    listed = _whole_values(X)
    top = max(max(listed), mine.degree())
    have = [mine.coeff_monomial(var ** i) for i in range(top + 2)]
    for run in runs:
        want = [sp.sympify(X.chance(i)).subs(run) if any(i == v for v in listed) else 0
                for i in range(top + 2)]
        if all(_draw_agree(h, w) for h, w in zip(have, want)):
            continue
        whole = sp.Add(*have)
        if not _draw_agree(whole, 1):
            print(f"{NO} {label}: " + _t(
                f"G(1) = {sig(whole, 4)}, а должно быть 1: коэффициенты — это вся "
                f"таблица, и они складываются в единицу",
                f"G(1) = {sig(whole, 4)}, and it has to be 1: the coefficients are "
                f"the whole table, and they add up to one"))
            return False
        last = max(listed)
        flipped = [want[last - i] if i <= last else 0 for i in range(top + 2)]
        if all(_draw_agree(h, w) for h, w in zip(have, flipped)):
            print(f"{NO} {label}: " + _t(
                f"коэффициенты стоят в обратном порядке: при {var}ᵏ должна быть "
                f"P({X.name} = k), а здесь P({X.name} = {last} − k) — посчитано "
                f"противоположное",
                f"the coefficients are in reverse order: {var}ᵏ carries "
                f"P({X.name} = k), and this has P({X.name} = {last} − k) — the "
                f"opposite count"))
            return False
        shifted = [0] + want[:-1]
        if all(_draw_agree(h, w) for h, w in zip(have, shifted)):
            print(f"{NO} {label}: " + _t(
                f"степени сдвинуты на одну: P({X.name} = k) стоит при {var}ᵏ, а не "
                f"при {var}ᵏ⁺¹",
                f"the powers are shifted by one: P({X.name} = k) goes with {var}ᵏ, "
                f"not {var}ᵏ⁺¹"))
            return False
        for i, (h, w) in enumerate(zip(have, want)):
            if not _draw_agree(h, w):
                print(f"{NO} {label}: " + _t(
                    f"коэффициент при {var}^{i} — это P({X.name} = {i}), и он не сходится",
                    f"the coefficient of {var}^{i} is P({X.name} = {i}), and it does "
                    f"not match"))
                return False
    print(f"{OK} {label}")
    return True


def _moment_expression(label, got, what, letters):
    """Ответ — E или Var как выражение от буквы: сверка в нескольких её значениях."""
    try:
        answer = sp.sympify(got)
    except (sp.SympifyError, TypeError):
        answer = None
    if answer is None or answer.free_symbols - set(letters):
        names = ', '.join(str(u) for u in letters)
        print(f"{NO} {label}: " + _t(f"ответ — выражение от {names}",
                                     f"the answer is an expression in {names}"))
        return False
    samples = [sp.Rational(3, 20), sp.Rational(3, 10), sp.Rational(11, 20), sp.Rational(4, 5)]
    want_expr = sp.sympify(what)
    if what.kind == 'var':
        # E(X²) без вычтенного квадрата среднего — самый частый промах
        linear = what.args[0]
        square = _moment('square', _Linear(linear.var, 1, 0))
        try:
            if all(_draw_agree(sp.N(answer.subs({u: s for u in letters}).doit(), 20),
                               sp.N(square.subs({u: s for u in letters}), 20)) and
                   not _draw_agree(sp.N(square.subs({u: s for u in letters}), 20),
                                   sp.N(want_expr.subs({u: s for u in letters}), 20))
                   for s in samples):
                print(f"{NO} {label}: " + _t(
                    f"это E({linear.var.name}²): квадрат среднего ещё не вычтен",
                    f"that is E({linear.var.name}²): the square of the mean has not been "
                    f"subtracted yet"))
                return False
        except (TypeError, ValueError, ZeroDivisionError):
            pass
    weightless = True
    for sample in samples:
        run = {u: sample for u in letters}
        try:
            mine = sp.N(answer.subs(run).doit(), 20)
            want = sp.N(want_expr.subs(run), 20)
        except (TypeError, ValueError, ZeroDivisionError):
            print(f"{NO} {label}: " + _t("выражение не вычисляется",
                                         "the expression does not evaluate"))
            return False
        if not _draw_agree(mine, 1):
            weightless = False
        if not _draw_agree(mine, want):
            if weightless and what.kind == 'mean':
                continue
            print(f"{NO} {label}: " + _t(
                f"при {letters[0]} = {sample} выражение даёт другое",
                f"at {letters[0]} = {sample} the expression gives something else"))
            return False
    if weightless and what.kind == 'mean':
        print(f"{NO} {label}: " + _t(
            "это сумма вероятностей, и она равна единице: среднее — сумма x·P(X = x)",
            "that is the sum of the probabilities, which is one: the mean is the sum "
            "of x·P(X = x)"))
        return False
    print(f"{OK} {label}")
    return True


# Ссылки вперёд: эти имена зовутся только изнутри функций, а модули,
# где они живут, сами импортируют этот. Поэтому импорт стоит в конце.
from .normal import (  # noqa: E402
    _Area, _area_of, _AREAS, _Curve, _curve_roots, _FREE_SAMPLES, _is_curve,
    _Mapped, _sf_agree, _sf_words, _verify_curve_chance,
)
from .density import (  # noqa: E402
    _Density, _density_letter_slips, _exact_letters, _verify_density_mode,
)
