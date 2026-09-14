"""Величина с плотностью (D6): всё — интеграл одной плотности.
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .distribution import _draw_agree, _Variable
from .table import (
    _as_conditions, _as_unknowns, _exact, _letter_runs, _rule_words,
)
from .normal import (
    _Area, _AREAS, _curve_cuts, _GAUSS, _Mapped, _numeric_lambda,
    _region_pieces,
)


# ======================================================= плотность формулой
# Двадцать третье понятие равенства ответов: всё — интеграл одной плотности.
#
# В D5 кривая была одна на всех, и менялись только μ и σ. Здесь величину
# задаёт формула по кускам — f(x) = x/√((x² + k)³) на [0, 4] и ноль вне, —
# и проверка знает только её. Вероятность — площадь под f над тем, где
# событие выполняется; медиана и квартиль — граница, левее которой набралась
# нужная площадь; мода — где f наибольшая; среднее и дисперсия — интегралы
# x·f и (x − μ)²·f. Ни первообразной, ни формулы E(X) = ∫ x f(x) dx,
# записанной для этой плотности, внутри нет: площадь складывает адаптивная
# квадратура Гаусса — Лежандра, кусок за куском.
#
# Буквы в плотности — k, a и b, края промежутка вида [a, 3a] — находятся
# тем же Ньютоном, что σ в D5. Условие «площадь под плотностью — единица»
# проверка добавляет сама, как сумму таблицы в D4, и отбрасывает решения,
# при которых плотность где-то отрицательна.

_DENSITY_GRID = 4000      # узлов при поиске моды
_DENSITY_ROOT_SCAN = 600  # узлов при поиске корней «чужого» уравнения медианы
_QUAD_BUDGET = 3000       # сколько раз квадратура делит отрезок


def _gauss_piece(fn, a, b):
    half, middle = (b - a) / 2, (a + b) / 2
    return half * math.fsum(weight * fn(middle + half * node) for node, weight in _GAUSS)


def _adaptive(fn, a, b):
    """Интеграл fn от a до b: делить пополам, пока шестнадцать узлов не сойдутся."""
    whole = _gauss_piece(fn, a, b)
    stack, done, used = [(a, b, whole)], [], 0
    while stack:
        lo, hi, guess = stack.pop()
        middle = (lo + hi) / 2
        left, right = _gauss_piece(fn, lo, middle), _gauss_piece(fn, middle, hi)
        used += 1
        both = left + right
        if abs(both - guess) <= 1e-13 * max(1.0, abs(both)) or used > _QUAD_BUDGET \
                or hi - lo < 1e-12 * (b - a):
            done.append(both)
        else:
            stack += [(lo, middle, left), (middle, hi, right)]
    return math.fsum(done)


def _quad(fn, a, b):
    """∫ fn от a до b, в том числе до бесконечности — заменой x = a + s/(1 − s).

    Конечный отрезок проходится заменой x = a + (b − a)(3s² − 2s³): у неё
    производная обращается в ноль на концах, и корневая особенность на
    краю (arccos x у единицы) перестаёт требовать тысячи делений.
    """
    if a == b:
        return 0.0
    if b < a:
        return -_quad(fn, b, a)
    if math.isinf(a) and math.isinf(b):
        return _quad(fn, a, 0.0) + _quad(fn, 0.0, b)
    if math.isinf(b):
        return _adaptive(lambda s: fn(a + s / (1 - s)) / (1 - s) ** 2, 0.0, 1.0)
    if math.isinf(a):
        return _adaptive(lambda s: fn(b - s / (1 - s)) / (1 - s) ** 2, 0.0, 1.0)
    width = b - a
    return _adaptive(lambda s: fn(a + width * s * s * (3 - 2 * s)) * 6 * s * (1 - s) * width,
                     0.0, 1.0)


def _real(value):
    """Число из того, что вернула формула; комплексное — ошибка, как корень из минуса."""
    if isinstance(value, complex):
        if abs(value.imag) > 1e-12 * max(1.0, abs(value)):
            raise ValueError('complex')
        value = value.real
    value = float(value)
    if math.isnan(value):
        raise ValueError('nan')
    return value


class _Density(_Variable):
    """Величина с плотностью: f(x) по кускам и ноль вне их.

    `pieces` — словарь «промежуток → формула», как в условии:
    `{(0, k): k*x, (k, 2*k): 2*k*x - x**2}`. Края могут быть буквами и
    бесконечностью, формулы — содержать буквы. Где кусок кончается и
    начинается следующий, неважно, включён ли край: у точки площади нет.
    """

    def __init__(self, pieces, name='X', var=x):
        self.name = name
        self.var = sp.sympify(var)
        self.origin = self
        self._compiled = {}
        self._blank = pieces is Ellipsis or any(
            key is Ellipsis or expr is Ellipsis
            or (isinstance(key, tuple) and any(edge is Ellipsis for edge in key))
            for key, expr in pieces.items())
        if self._blank:
            self.pieces, self.letters = [], []
            return
        self.pieces = []
        for key, expr in pieces.items():
            lo, hi = (key.start, key.end) if isinstance(key, sp.Interval) else key
            self.pieces.append((_exact(lo), _exact(hi), _exact(expr)))
        found = set()
        for lo, hi, expr in self.pieces:
            found |= lo.free_symbols | hi.free_symbols | (expr.free_symbols - {self.var})
        self.letters = sorted(found, key=str)
        if not self.letters:
            broken = self.broken({})
            if broken is not None:
                raise ValueError(_rule_words(broken))
            whole = self.area_between(self.shape({}), -math.inf, math.inf)
            if abs(whole - 1) > 1e-6:
                raise ValueError(_t(f'площадь под плотностью {sig(whole, 6)}, а не 1',
                                    f'the area under the density is {sig(whole, 6)}, not 1'))

    __hash__ = object.__hash__

    def blank(self):
        return self._blank

    def values(self):
        raise TypeError(_t('у непрерывной величины значений не перечислить: вероятность '
                           'здесь площадь, а не сумма',
                           'a continuous variable has no list of values: a probability '
                           'here is an area, not a sum'))

    def chance(self, k, p=None):
        return self.values()

    def map(self, rule, name=None):
        """Величина, посчитанная из этой: `X.map(lambda w: 25*w, 'cost')`."""
        return _Mapped(self, rule, name)

    def pinned(self, run):
        """Та же плотность, где часть букв заменена числами.

        Площадь такой копии не проверяется: годится ли она — как раз то,
        что проверка выясняет.
        """
        copy = _Density.__new__(_Density)
        copy.name, copy.var, copy._compiled, copy._blank = self.name, self.var, {}, False
        copy.pieces = [(lo.subs(run), hi.subs(run), expr.subs(run))
                       for lo, hi, expr in self.pieces]
        found = set()
        for lo, hi, expr in copy.pieces:
            found |= lo.free_symbols | hi.free_symbols | (expr.free_symbols - {copy.var})
        copy.letters = sorted(found, key=str)
        copy.origin = self.origin
        return copy

    def pdf(self, value):
        """f(value) выражением: `X.pdf(9)` — то, что вопрос пишет как f(9)."""
        value = sp.sympify(value)
        for lo, hi, expr in self.pieces:
            inside = sp.And(sp.sympify(value >= lo), sp.sympify(value <= hi))
            if inside is sp.true:
                return expr.subs(self.var, value)
        for lo, hi, expr in self.pieces:
            if sp.And(sp.sympify(value >= lo), sp.sympify(value <= hi)) is not sp.false:
                raise ValueError(_t(f'не понять, на каком куске лежит {value}',
                                    f'cannot tell which piece {value} is on'))
        return sp.Integer(0)

    def compiler(self, letters):
        """Функция «числа букв → куски [(lo, hi, f)] числами»."""
        key = tuple(letters)
        if key not in self._compiled:
            parts = [(_numeric_lambda(letters, lo), _numeric_lambda(letters, hi),
                      sp.lambdify([self.var] + list(letters), expr, 'math'))
                     for lo, hi, expr in self.pieces]

            def shape(*numbers):
                out = []
                for lo_f, hi_f, fn in parts:
                    out.append((float(lo_f(*numbers)), float(hi_f(*numbers)),
                                lambda point, fn=fn: _real(fn(point, *numbers))))
                return out
            self._compiled[key] = shape
        return self._compiled[key]

    def shape(self, run=None):
        run = run or {}
        missing = [u for u in self.letters if u not in run]
        if missing:
            raise ValueError(_t(f"в плотности осталась буква {missing[0]}",
                                f"the density still has the letter {missing[0]}"))
        return self.compiler(self.letters)(*[float(run[u]) for u in self.letters])

    @staticmethod
    def support(shape):
        live = [(lo, hi) for lo, hi, _ in shape if hi > lo]
        if not live:
            raise ValueError('empty')
        return min(lo for lo, _ in live), max(hi for _, hi in live)

    @staticmethod
    def at(shape, point):
        """f(point) числом: кусок, где point лежит; на стыке — правый."""
        for lo, hi, fn in shape:
            if lo <= point < hi:
                return fn(point)
        for lo, hi, fn in reversed(shape):
            if hi > lo and point == hi:
                return fn(point)
        return 0.0

    @staticmethod
    def area_between(shape, a, b):
        total = []
        for lo, hi, fn in shape:
            left, right = max(a, lo), min(b, hi)
            if right > left:
                total.append(_quad(fn, left, right))
        return math.fsum(total)

    def window(self, shape):
        """Конечный отрезок, где лежит почти вся площадь: там ищут моду и границы."""
        lo, hi = self.support(shape)
        if math.isinf(lo) or math.isinf(hi):
            step = 1.0
            while step < 1e6:
                a = lo if not math.isinf(lo) else -step
                b = hi if not math.isinf(hi) else step
                outside = (self.area_between(shape, b, math.inf) if math.isinf(hi) else 0.0) + \
                    (self.area_between(shape, -math.inf, a) if math.isinf(lo) else 0.0)
                if abs(outside) < 1e-12:
                    return a, b
                step *= 2
            return (lo if not math.isinf(lo) else -step), (hi if not math.isinf(hi) else step)
        return lo, hi

    def region_area(self, node, shape, exact=False):
        """Площадь под f над теми x, где событие выполняется."""
        lo, hi = self.support(shape)
        window = self.window(shape)
        edges = {lo, hi}
        for a, b, _ in shape:
            edges |= {a, b}
        edges |= set(_curve_cuts(node, *window))
        edges = sorted(e for e in edges if lo <= e <= hi)
        step = max(1e-6, (window[1] - window[0]) / 1000)
        return math.fsum(self.area_between(shape, a, b)
                         for a, b in _region_pieces(node, edges, window, step))

    def broken(self, run):
        """Где плотность перестаёт быть плотностью при этих буквах, или None."""
        try:
            shape = self.shape(run)
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            return None
        for lo, hi, fn in shape:
            if not hi > lo:
                continue
            a, b = lo, hi
            if math.isinf(a) or math.isinf(b):
                a, b = self.window([(lo, hi, fn)]) if not (math.isinf(a) and math.isinf(b)) \
                    else (-50.0, 50.0)
            points = [a + (b - a) * (i + 0.5) / 200 for i in range(200)]
            points += [a + (b - a) * (1 + node) / 2 for node, _ in _GAUSS]
            for point in points:
                try:
                    value = fn(point)
                except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                    return f"f({sig(point, 4)})", None, 'density'
                if value < -1e-9:
                    return f"f({sig(point, 4)})", value, 'density'
        return None

    def __repr__(self):
        cells = '; '.join(f"{expr} on [{lo}, {hi}]" for lo, hi, expr in self.pieces)
        return f"{self.name}: f({self.var}) = {cells}, 0 otherwise"


def Density(pieces, name='X', var=x):
    """Величина с плотностью: `X = Density({(0, 4): x/sqrt((x**2 + k)**3)})`.

    Ключ — промежуток, значение — формула на нём; вне всех промежутков
    плотность ноль, как «0, otherwise» в условии. Сравнения дают события,
    `P()` — их площадь, `Expect`, `Var`, `SD` — интегралы. Буквы разрешены
    и в формуле, и в краях: `Density({(a, 3*a): 1/(2*a)})`.
    """
    return _Density(pieces, name, var)


# -------------------------------------------------- мода, медиана, моменты

def _density_top(X, run):
    """Мода и значение плотности в ней: сетка по окну, потом золотое сечение."""
    shape = X.shape(run)
    lo, hi = X.window(shape)

    def height(point):
        try:
            return X.at(shape, point)
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            return -math.inf
    grid = [lo + (hi - lo) * i / _DENSITY_GRID for i in range(_DENSITY_GRID + 1)]
    heights = [height(point) for point in grid]
    best = max(range(len(grid)), key=lambda i: heights[i])
    a, b = grid[max(0, best - 1)], grid[min(len(grid) - 1, best + 1)]
    ratio = (math.sqrt(5) - 1) / 2
    for _ in range(200):
        one, two = b - ratio * (b - a), a + ratio * (b - a)
        if height(one) >= height(two):
            b = two
        else:
            a = one
    point = (a + b) / 2
    candidates = [(height(point), point), (heights[best], grid[best])]
    top, where = max(candidates)
    return where, top


def _density_share(X, run, share):
    """Граница, левее которой площадь share, — делением пополам по окну."""
    shape = X.shape(run)
    lo, hi = X.window(shape)
    for _ in range(200):
        middle = (lo + hi) / 2
        if X.area_between(shape, -math.inf, middle) < share:
            lo = middle
        else:
            hi = middle
    return (lo + hi) / 2


def _density_moment_numbers(shape, kind, a, b, g=None, breaks=()):
    """E(aX + b), E((aX + b)²) или Var(aX + b) по кускам плотности.

    `breaks` — где g(x) скачет (цена 25x до 0,75 кг и 24x после): там кусок
    режется, иначе квадратура сходится к скачку тысячами делений.
    """
    if breaks:
        cut = []
        for lo, hi, fn in shape:
            edges = [lo] + sorted(p for p in breaks if lo < p < hi) + [hi]
            cut += [(one, two, fn) for one, two in zip(edges, edges[1:])]
        shape = cut

    def h(point):
        inner = point if g is None else g(point)
        if inner is None:
            raise ValueError('value')
        return a * inner + b
    mean = math.fsum(_quad(lambda p, fn=fn: h(p) * fn(p), lo, hi)
                     for lo, hi, fn in shape if hi > lo)
    if kind == 'mean':
        return mean
    if kind == 'square':
        return math.fsum(_quad(lambda p, fn=fn: h(p) ** 2 * fn(p), lo, hi)
                         for lo, hi, fn in shape if hi > lo)
    return math.fsum(_quad(lambda p, fn=fn: (h(p) - mean) ** 2 * fn(p), lo, hi)
                     for lo, hi, fn in shape if hi > lo)


def _density_moment(kind, var, a, b):
    """Среднее, квадрат или дисперсия aX + b — число или _Area от букв."""
    base = var.base if isinstance(var, _Mapped) else var
    g = var.at if isinstance(var, _Mapped) else None
    letters = sorted(set(base.letters) | sp.sympify(a).free_symbols | sp.sympify(b).free_symbols,
                     key=str)
    a_f, b_f = _numeric_lambda(letters, a), _numeric_lambda(letters, b)
    shape = base.compiler(letters)

    def call(*numbers):
        return _density_moment_numbers(shape(*numbers), kind, float(a_f(*numbers)),
                                       float(b_f(*numbers)), g,
                                       var.breaks() if isinstance(var, _Mapped) else ())
    if not letters:
        return sp.Float(call(), 15)
    _AREAS.append({'base': base, 'call': call})
    return _Area(sp.Integer(len(_AREAS) - 1), *letters)


def _density_slips(base, target, leaves, run, slips):
    """Промахи с площадью под плотностью — к тем, что уже набраны по событию."""
    if len(leaves) == 1 and isinstance(leaves[0][1][1], _Density) and \
            not isinstance(leaves[0][1][3], _Variable):
        try:
            shape = base.shape(run)
            edge = float(sp.sympify(leaves[0][1][3]).subs(run))
            slips[_t(f"это значение плотности в точке {sig(edge, 6)}, а вероятность — "
                     f"площадь под ней",
                     f"that is the value of the density at {sig(edge, 6)}; a probability "
                     f"is the area under it")] = base.at(shape, edge)
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            pass
    return slips


def _density_letter_slips(X, name, value, conditions, run, agree):
    """Промахи с границей по площади: медиана, квартиль. Слово или None.

    Три промаха, и все три — «не та площадь»: набрана от нуля, хотя
    плотность начинается дальше; формула одного куска взята на всём
    промежутке; корень уравнения лежит там, где эта формула не действует.
    """
    for item in conditions:
        eq = sp.sympify(item)
        if not (isinstance(eq, sp.Equality) and isinstance(eq.lhs, _Area)):
            continue
        entry = _AREAS[int(eq.lhs.args[0])]
        node = entry.get('node')
        if node is None or node[0] != 'leaf' or entry['base'] is not X.origin:
            continue
        _, left, rel, bound = node
        if not isinstance(left, _Density) or sp.sympify(bound) != name:
            continue
        try:
            share = float(sp.sympify(eq.rhs).subs(run))
            fixed = X.pinned({u: v for u, v in run.items() if u in X.letters})
            shape = fixed.shape({})
            lo, hi = fixed.support(shape)
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            return None
        if rel in ('>', '>='):
            share = 1 - share
        truth = float(run[name])
        wlo, whi = fixed.window(shape)
        width = whi - wlo

        def roots(fn, a, b):
            found, before = [], None
            for i in range(_DENSITY_ROOT_SCAN + 1):
                point = a + (b - a) * i / _DENSITY_ROOT_SCAN
                try:
                    now = fn(point)
                except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                    before = None
                    continue
                if before is not None and (before[1] < 0) != (now < 0):
                    x0, x1 = before[0], point
                    for _ in range(80):
                        middle = (x0 + x1) / 2
                        try:
                            if (fn(middle) < 0) == (before[1] < 0):
                                x0 = middle
                            else:
                                x1 = middle
                        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                            break
                    found.append((x0 + x1) / 2)
                before = (point, now)
            return found

        def said(root):
            return agree(value, root) and not agree(truth, root)
        if abs(share - 0.5) < 1e-12:
            try:
                mean = _density_moment_numbers(shape, 'mean', 1.0, 0.0)
                mode, _ = _density_top(fixed, {})
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                mean = mode = None
            if mean is not None and said(mean):
                return _t("это среднее, а медиана — граница, левее которой половина площади",
                          "that is the mean; the median is the boundary with half the area "
                          "to its left")
            if mode is not None and said(mode):
                return _t("это мода, а медиана — граница, левее которой половина площади",
                          "that is the mode; the median is the boundary with half the area "
                          "to its left")
        first_lo, first_hi, first_fn = min(((a, b, f) for a, b, f in shape if b > a),
                                           key=lambda item: item[0])
        if first_lo > 0 and not math.isinf(first_lo):
            zero = [(0.0, first_hi, first_fn)] + [p for p in shape if p[0] >= first_hi]
            for root in roots(lambda q: X.area_between(zero, -math.inf, q) - share, 0.0, whi):
                if said(root):
                    return _t(f"площадь набрана от 0, а плотность начинается с "
                              f"{sig(first_lo, 4)}: левее неё она ноль, и формула "
                              f"там не действует",
                              f"the area is collected from 0, and the density starts at "
                              f"{sig(first_lo, 4)}: to the left of it the density is zero, "
                              f"and the formula does not apply")
        live = [(a, b, f) for a, b, f in shape if b > a]
        before_area = 0.0
        for a, b, fn in sorted(live, key=lambda item: item[0]):
            def equation(q, a=a, fn=fn, start=before_area):
                return start + _quad(fn, a, q) - share
            for root in roots(equation, wlo - 4 * width, whi + 4 * width):
                if a <= root <= b or not said(root):
                    continue
                if root < lo or root > hi:
                    return _t(f"{sig(value, 6)} — корень уравнения, но он лежит вне "
                              f"[{sig(lo, 4)}, {sig(hi, 4)}], где задана плотность: такой "
                              f"корень отбрасывают",
                              f"{sig(value, 6)} solves the equation, but it lies outside "
                              f"[{sig(lo, 4)}, {sig(hi, 4)}], where the density lives: that "
                              f"root is rejected")
                return _t(f"это корень уравнения с формулой куска [{sig(a, 4)}, {sig(b, 4)}], "
                          f"а сам он лежит на другом куске, где формула другая",
                          f"that solves the equation with the formula of the piece "
                          f"[{sig(a, 4)}, {sig(b, 4)}], but it lies on another piece, where "
                          f"the formula is different")
            before_area += _quad(fn, a, b)
        if len(live) > 1:
            for a, b, fn in live:
                whole = [(lo, hi, fn)]
                for root in roots(lambda q: X.area_between(whole, -math.inf, q) - share, lo, hi):
                    if said(root):
                        return _t(f"формула куска [{sig(a, 4)}, {sig(b, 4)}] взята на всём "
                                  f"промежутке, а на остальных кусках плотность другая",
                                  f"the formula of the piece [{sig(a, 4)}, {sig(b, 4)}] is used "
                                  f"everywhere, and on the other pieces the density is "
                                  f"different")
    return None


def _exact_letters(label, names, numbers, good):
    """Точное значение буквы: без десятичных дробей и до последнего знака."""
    if any(value.has(sp.Float) for value in numbers):
        print(f"{NO} {label}: " + _t(
            "вопрос просит точное значение, а это десятичная дробь",
            "the question asks for the exact value, and this is a decimal"))
        return False
    run = good[0]
    if not all(abs(float(v) - float(run[n])) <= 1e-9 * max(1.0, abs(float(run[n])))
               for n, v in zip(names, numbers)):
        print(f"{NO} {label}: " + _t(
            "это близко, но не точное значение",
            "that is close, but it is not the exact value"))
        return False
    return True


def verify_greater(label, got, X, among=('mode', 'median'), given=None, var=None):
    """Ответ — слово: что больше, мода или медиана (или среднее).

    Проверка находит все три сама: моду — где плотность наибольшая,
    медиану — где набирается половина площади, среднее — интегралом. Неверное
    слово получает ту причину, за которую схема оценивания даёт R1:
    сколько площади левее моды.
    """
    if _blank(label, got, X):
        return False
    answer = str(got).strip().lower()
    if answer not in among:
        print(f"{NO} {label}: " + _t(f"ответ — одно из слов: {', '.join(among)}",
                                     f"the answer is one of the words: {', '.join(among)}"))
        return False
    unknowns = _as_unknowns(var)
    if given is None and not unknowns:
        runs = [{}]
    else:
        runs, _ = _letter_runs(_as_conditions(given), unknowns, [X])
        runs = runs or []
    if not runs:
        print(f"{NO} {label}: " + _t("условиям не отвечает ни одна годная плотность",
                                     "no valid density satisfies the conditions"))
        return False
    for run in runs:
        mode, _ = _density_top(X, run)
        values = {'mode': mode, 'median': _density_share(X, run, 0.5)}
        if 'mean' in among:
            values['mean'] = _density_moment_numbers(X.shape(run), 'mean', 1.0, 0.0)
        larger = max(among, key=lambda word: values[word])
        if answer == larger:
            continue
        shape = X.shape(run)
        left = X.area_between(shape, -math.inf, mode)
        if set(among) == {'mode', 'median'}:
            print(f"{NO} {label}: " + _t(
                f"левее моды лежит площадь {sig(left, 3)} — "
                f"{'меньше' if left < 0.5 else 'больше'} половины, так что половина "
                f"площади набирается {'правее' if left < 0.5 else 'левее'} моды",
                f"the area to the left of the mode is {sig(left, 3)} — "
                f"{'less' if left < 0.5 else 'more'} than a half, so half the area is "
                f"reached to the {'right' if left < 0.5 else 'left'} of the mode"))
        else:
            print(f"{NO} {label}: " + _t("у этой плотности больше другое",
                                         "for this density the other one is greater"))
        return False
    print(f"{OK} {label}")
    return True


def _verify_density_mode(label, got, X, given, var):
    unknowns = _as_unknowns(var)
    if given is None and not unknowns:
        runs = [{}]
    else:
        runs, _ = _letter_runs(_as_conditions(given), unknowns, [X])
        runs = runs or []
    if not runs:
        print(f"{NO} {label}: " + _t("условиям не отвечает ни одна годная плотность",
                                     "no valid density satisfies the conditions"))
        return False
    try:
        value = float(sp.sympify(got))
    except (TypeError, ValueError, sp.SympifyError):
        print(f"{NO} {label}: " + _t("мода — это число", "the mode is a number"))
        return False
    for run in runs:
        mode, top = _density_top(X, run)
        if _draw_agree(value, mode):
            continue
        shape = X.shape(run)
        if _draw_agree(value, top):
            print(f"{NO} {label}: " + _t(
                "это наибольшее значение плотности, а мода — x, при котором оно",
                "that is the largest value of the density; the mode is the x where it "
                "happens"))
        elif _draw_agree(value, _density_share(X, run, 0.5)):
            print(f"{NO} {label}: " + _t(
                "это медиана: мода — там, где плотность наибольшая",
                "that is the median: the mode is where the density is largest"))
        elif _draw_agree(value, _density_moment_numbers(shape, 'mean', 1.0, 0.0)):
            print(f"{NO} {label}: " + _t(
                "это среднее: мода — там, где плотность наибольшая",
                "that is the mean: the mode is where the density is largest"))
        else:
            try:
                here = X.at(shape, value)
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                here = None
            print(f"{NO} {label}: " + (_t(
                f"f({sig(value, 4)}) = {sig(here, 4)}, а плотность бывает и больше",
                f"f({sig(value, 4)}) = {sig(here, 4)}, and the density gets larger than "
                f"that") if here is not None else _t(
                f"в {sig(value, 4)} плотность не определена",
                f"the density is not defined at {sig(value, 4)}")))
        return False
    print(f"{OK} {label}")
    return True
