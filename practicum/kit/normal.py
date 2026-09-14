"""Нормальное распределение (D5): вероятность — площадь под кривой.
"""

import cmath
import itertools
import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _t
from .probability import _Prob, _PROB_TOL
from .distribution import (
    _Draw, _draw_agree, _draw_leaves, _draw_say, _draw_vars, _Variable,
)
from .table import (
    _as_conditions, _as_unknowns, _letter_runs, _letters_in, _rounded_runs,
)


# ================================================== нормальное распределение
# Двадцать второе понятие равенства ответов: вероятность — это площадь.
#
# В D3 и D4 у величины была таблица, и вероятность события складывалась
# по её значениям. У нормальной величины значений не перечислить: ей
# известна только кривая, e^(−(x − μ)²/(2σ²))/(σ√(2π)), и вероятность
# события — площадь под этой кривой над теми x, где событие выполняется.
# Проверка так её и получает: находит, где событие выполняется, и складывает
# площадь квадратурой Гаусса — Лежандра по кускам шириной σ. Ни функции
# ошибок, ни таблиц стандартного нормального, ни обратной нормальной внутри
# нет, и test_kit_normal.py проверяет это по коду.
#
# Отсюда всё остальное. «Найдите w, если P(W > w) = 0,2» — буква, при
# которой площадь равна 0,2; «найдите μ и σ» — две буквы и два условия
# на площади. Их проверка находит сама, методом Ньютона от нескольких
# начальных точек, и отбрасывает решения, при которых стандартное
# отклонение не положительно. Эталона нет ни одного.
#
# Событие хранится тем же деревом сравнений, что в D3. Граница, у которой
# сравнивается сама величина, известна сразу; величина, посчитанная из
# другой (X₁ = −Z − √(Z² − 1)), проходится по оси, и границы находятся
# там, где сравнение меняет знак или перестаёт иметь смысл.

_CURVE_SPAN = 15          # за μ ± 15σ площадь меньше 10⁻⁵⁰, её не складывают
_CURVE_GRID = 3000        # шагов по оси, когда границу события приходится искать


def _legendre(n):
    """Узлы и веса Гаусса — Лежандра на [−1, 1], найденные методом Ньютона."""
    nodes = []
    for i in range(1, n + 1):
        z = math.cos(math.pi * (i - 0.25) / (n + 0.5))
        for _ in range(100):
            before, here = 1.0, z
            for j in range(2, n + 1):
                before, here = here, ((2 * j - 1) * z * here - (j - 1) * before) / j
            slope = n * (z * here - before) / (z * z - 1)
            step = here / slope
            z -= step
            if abs(step) < 1e-16:
                break
        before, here = 1.0, z
        for j in range(2, n + 1):
            before, here = here, ((2 * j - 1) * z * here - (j - 1) * before) / j
        slope = n * (z * here - before) / (z * z - 1)
        nodes.append((z, 2 / ((1 - z * z) * slope * slope)))
    return nodes


_GAUSS = _legendre(16)


def _bell_area(mean, spread, lo, hi):
    """Площадь под кривой N(μ, σ²) от lo до hi.

    Кривая складывается кусками шириной σ, в каждом шестнадцать узлов.
    Хвост за μ ± 15σ отбрасывается: там площадь меньше любой, о которой
    спрашивают.
    """
    lo = max(lo, mean - _CURVE_SPAN * spread)
    hi = min(hi, mean + _CURVE_SPAN * spread)
    if hi <= lo:
        return 0.0
    pieces = max(1, math.ceil((hi - lo) / spread))
    width = (hi - lo) / pieces
    twice = 2 * spread * spread
    terms = []
    for i in range(pieces):
        centre = lo + (i + 0.5) * width
        for node, weight in _GAUSS:
            point = centre + node * width / 2
            terms.append(weight * math.exp(-(point - mean) ** 2 / twice))
    return math.fsum(terms) * width / 2 / (spread * math.sqrt(2 * math.pi))


class _Curve(_Variable):
    """X ~ N(μ, σ²): величина, у которой есть кривая и нет таблицы.

    Второй параметр — дисперсия, как пишет IB: N(1000, 3.5²). Буквы в
    обоих параметрах разрешены — так ставят вопрос «найдите σ».

    `rule` — когда вопрос сам говорит, какой площадью пользоваться:
    «95 % весов лежат в пределах двух стандартных отклонений». Тогда
    площади берутся из этого правила и симметрии, а не из кривой, и
    площадь, которую правило не даёт, проверка посчитать откажется.
    """

    def __init__(self, mean, variance, name='X', rule=None):
        self.name = name
        self.rule = None if rule is None else {float(k): float(v) for k, v in rule.items()}
        self._blank = mean is Ellipsis or variance is Ellipsis
        if self._blank:
            self.mean = self.variance = Ellipsis
            return
        self.mean, self.variance = sp.sympify(mean), sp.sympify(variance)
        if self.variance.is_number and not float(self.variance) > 0:
            raise ValueError(_t(f'дисперсия положительна, а не {variance}',
                                f'a variance is positive, not {variance}'))

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

    @property
    def spread(self):
        """σ так, как его пишет вопрос: у N(75, σ²) это σ, а не |σ|."""
        if isinstance(self.variance, sp.Pow) and self.variance.exp == 2:
            return self.variance.base
        return sp.sqrt(self.variance)

    def rules(self):
        return [(_t(f'стандартное отклонение {self.name}',
                    f'the standard deviation of {self.name}'), self.spread, 'sd')]

    def numbers(self, run=None):
        """μ и σ числами при данных буквах."""
        mean = float(sp.sympify(self.mean).subs(run or {}))
        variance = float(sp.sympify(self.variance).subs(run or {}))
        if not variance > 0:
            raise ValueError('variance')
        return mean, math.sqrt(variance)

    def map(self, rule, name=None):
        """Величина, посчитанная из этой: `Z.map(lambda z: -z - sqrt(z**2 - 1), 'X1')`."""
        return _Mapped(self, rule, name)

    def __repr__(self):
        return f"{self.name} ~ N({self.mean}, {self.variance})"


class _Mapped(_Variable):
    """Величина, посчитанная из непрерывной: X₁ = −Z − √(Z² − 1).

    Своей кривой у неё нет; событие над ней — это множество значений Z,
    при которых оно выполняется, и площадь берётся под кривой Z. Там, где
    значение не действительно (корень из отрицательного), событие не
    выполняется.
    """

    def __init__(self, base, rule, name=None):
        self.base = base
        self.name = name or f"g({base.name})"
        self.dummy = sp.Dummy('z')
        self.expr = sp.sympify(rule(self.dummy))
        # функции из cmath — корень из отрицательного даёт комплексное, а не
        # ошибку, — но печать чисел от math: у принтера cmath десятичная
        # дробь в правиле (−0,4·cos 7,8t, D6) уходит в бесконечную рекурсию
        functions = {name: getattr(cmath, name) for name in dir(cmath) if not name.startswith('_')}
        self._number = sp.lambdify(self.dummy, self.expr, modules=[functions, 'math'])

    __hash__ = object.__hash__

    def blank(self):
        return self.base.blank()

    def values(self):
        return self.base.values()

    def breaks(self):
        """Где правило может скакать: числа из условий Piecewise."""
        found = set()
        for piece in self.expr.atoms(sp.Piecewise):
            for _, cond in piece.args:
                for rel in cond.atoms(sp.core.relational.Relational):
                    for side in (rel.lhs, rel.rhs):
                        if side.is_number and side.is_real:
                            found.add(float(side))
        return sorted(found)

    def at(self, point):
        try:
            value = complex(self._number(point))
        except (ValueError, TypeError, ZeroDivisionError, OverflowError):
            return None
        if abs(value.imag) > 1e-12 * max(1.0, abs(value)):
            return None
        return value.real

    def __repr__(self):
        return f"{self.name} = {str(self.expr).replace(str(self.dummy), self.base.name)}"


def Normal(mean, variance, name='X', rule=None):
    """Нормальная величина: `W = Normal(204, 5**2, 'W')` — это W ~ N(204, 5²).

    Второй параметр — дисперсия, а не стандартное отклонение, как в записи
    IB. Сравнения дают события, `P()` находит их площадь: `P(W > 210)`,
    `P((W > w) & (W < 210))`, `P(T < 82, given=T > 80)`.
    """
    return _Curve(mean, variance, name, rule)


class _Mixture(_Variable):
    """Смесь: 60 % кексов шоколадные, 40 % банановые, и у каждых своя кривая.

    Событие над смесью раскладывается по частям: P(кекс < 61) — это доля
    шоколадных, умноженная на площадь под их кривой, плюс то же для
    банановых. `muffin.came_from(C)` — событие «кекс шоколадный», и
    условная вероятность P(muffin.came_from(C), given=muffin < 61)
    складывается из тех же частей.
    """

    def __init__(self, parts, name='X'):
        self.name = name
        self.parts = [(var, w if w is Ellipsis else sp.sympify(w)) for var, w in parts.items()]
        if self.blank():
            return
        for var, _ in self.parts:
            if not isinstance(var, _Curve):
                raise TypeError(_t('смешивать здесь можно нормальные величины',
                                   'only normal variables are mixed here'))
        total = sp.Add(*[w for _, w in self.parts])
        if total.is_number and abs(float(total) - 1) > 1e-9:
            raise ValueError(_t(f'доли частей складываются в {total}, а не в 1',
                                f'the shares of the parts add up to {total}, not 1'))

    __hash__ = object.__hash__

    def blank(self):
        return any(w is Ellipsis or var.blank() for var, w in self.parts)

    def values(self):
        raise TypeError(_t('у смеси непрерывных величин значений не перечислить',
                           'a mixture of continuous variables has no list of values'))

    def came_from(self, part):
        """Событие «значение взято из этой части смеси»."""
        return _Draw(('leaf', self, 'from', part))

    def rules(self):
        return [(_t(f'доля {var.name}', f'the share of {var.name}'), w, 'prob')
                for var, w in self.parts]

    def __repr__(self):
        return f"{self.name}: " + ', '.join(f"{w} of {var}" for var, w in self.parts)


def Mix(parts, name='X'):
    """Смесь нормальных величин: `Mix({C: 0.6, B: 0.4}, 'muffin')`."""
    return _Mixture(parts, name)


def _unmix(node):
    """[(доля, событие)] — событие над смесью, разложенное по её частям."""
    mixes = []
    for var in _draw_vars(node):
        if isinstance(var, _Mixture) and not any(var is seen for seen in mixes):
            mixes.append(var)
    if not mixes:
        return [(sp.Integer(1), node)]
    if len(mixes) > 1:
        raise ValueError(_t('в одном событии две смеси', 'one event has two mixtures'))
    mix = mixes[0]

    def pin(here, part):
        if here[0] == 'leaf':
            _, left, rel, right = here
            if rel == 'from':
                return ('yes',) if right is part else ('no',)
            return ('leaf', part if left is mix else left, rel, part if right is mix else right)
        return (here[0],) + tuple(pin(child, part) for child in here[1:])
    return [(weight, pin(node, part)) for part, weight in mix.parts]


def _curve_base(node):
    """Единственная непрерывная величина, над которой построено событие."""
    bases = []
    for var in _draw_vars(node):
        base = var.base if isinstance(var, _Mapped) else var
        if not isinstance(base, (_Curve, _Density)):
            raise TypeError(_t('в одном событии непрерывная величина и дискретная',
                               'one event mixes a continuous and a discrete variable'))
        if not any(base is seen for seen in bases):
            bases.append(base)
    if len(bases) != 1:
        raise ValueError(_t('событие над двумя непрерывными величинами здесь не складывается: '
                            'запишите его через одну',
                            'an event about two continuous variables is not added up here: '
                            'write it in terms of one'))
    return bases[0]


def _is_curve(node):
    return any(isinstance(var, (_Curve, _Mapped, _Mixture, _Density)) for var in _draw_vars(node))


def _no_variables(node):
    return not _draw_vars(node)


def _curve_side(item, point):
    if isinstance(item, (_Curve, _Density)):
        return point
    if isinstance(item, _Mapped):
        return item.at(point)
    return item


def _curve_holds(node, point):
    """Выполняется ли событие при данном значении непрерывной величины."""
    kind = node[0]
    if kind == 'leaf':
        _, left, rel, right = node
        one, two = _curve_side(left, point), _curve_side(right, point)
        if one is None or two is None:
            return False
        return {'==': one == two, '<': one < two, '<=': one <= two,
                '>': one > two, '>=': one >= two}[rel]
    if kind in ('yes', 'no'):
        return kind == 'yes'
    if kind == 'not':
        return not _curve_holds(node[1], point)
    left, right = _curve_holds(node[1], point), _curve_holds(node[2], point)
    return {'and': left and right, 'or': left or right, 'xor': left != right}[kind]


def _curve_fix(node, number):
    """То же дерево, где границы-выражения заменены числами."""
    if node[0] == 'leaf':
        _, left, rel, right = node
        if not isinstance(left, _Variable):
            left = number(left)
        if not isinstance(right, _Variable):
            right = number(right)
        return ('leaf', left, rel, right)
    return (node[0],) + tuple(_curve_fix(child, number) for child in node[1:])


def _curve_cuts(node, lo, hi):
    """Точки оси, где событие может начаться или кончиться; [lo, hi] — где искать."""
    cuts, walk = set(), []
    for _, leaf in _draw_leaves(node):
        _, left, _, right = leaf
        if isinstance(left, (_Curve, _Density)) and not isinstance(right, _Variable):
            cuts.add(right)
        elif isinstance(right, (_Curve, _Density)) and not isinstance(left, _Variable):
            cuts.add(left)
        else:
            walk.append(leaf)
    for _, left, _, right in walk:
        def state(point, left=left, right=right):
            one, two = _curve_side(left, point), _curve_side(right, point)
            if one is None or two is None:
                return None
            return one < two
        before = state(lo)
        for i in range(1, _CURVE_GRID + 1):
            a = lo + (hi - lo) * (i - 1) / _CURVE_GRID
            b = lo + (hi - lo) * i / _CURVE_GRID
            now = state(b)
            if now != before:
                start = state(a)
                for _ in range(80):
                    middle = (a + b) / 2
                    if state(middle) == start:
                        a = middle
                    else:
                        b = middle
                cuts.add((a + b) / 2)
            before = now
    return sorted(cuts)


def _rule_area(base, mean, spread, lo, hi):
    """Площадь по правилу из условия и симметрии, без кривой."""
    marks = [(-math.inf, 0.0), (mean, 0.5), (math.inf, 1.0)]
    for many, share in base.rule.items():
        marks += [(mean - many * spread, 0.5 - share / 2), (mean + many * spread, 0.5 + share / 2)]

    def below(point):
        for where, share in marks:
            if where == point or (math.isfinite(where) and math.isfinite(point)
                                  and abs(where - point) <= 1e-9 * max(1.0, abs(point), spread)):
                return share
        raise ValueError(_t(
            f'правило из условия не даёт площади до {sig(point, 6)}: граница стоит не на '
            f'μ ± kσ',
            f'the rule in the question gives no area up to {sig(point, 6)}: the boundary '
            f'is not at μ ± kσ'))
    return below(hi) - below(lo)


def _region_pieces(node, edges, window, step):
    """Промежутки между соседними точками edges, где событие выполняется.

    Проба в середине промежутка; у бесконечного края — на шаг step от
    конечного, а у промежутка без конечных краёв — в середине window.
    """
    pieces = []
    for lo, hi in zip(edges, edges[1:]):
        if not hi > lo:
            continue
        if math.isinf(lo) and math.isinf(hi):
            probe = (window[0] + window[1]) / 2
        elif math.isinf(lo):
            probe = hi - step
        elif math.isinf(hi):
            probe = lo + step
        else:
            probe = (lo + hi) / 2
        if _curve_holds(node, probe):
            if pieces and pieces[-1][1] == lo:
                pieces[-1] = (pieces[-1][0], hi)
            else:
                pieces.append((lo, hi))
    return pieces


def _region_area(base, node, mean, spread, exact=False):
    """Площадь под кривой над всеми x, где событие выполняется."""
    cuts = _curve_cuts(node, mean - _CURVE_SPAN * spread, mean + _CURVE_SPAN * spread)
    edges = [-math.inf] + cuts + [math.inf]
    total = 0.0
    for lo, hi in _region_pieces(node, edges, (mean, mean), spread):
        if base.rule is not None and not exact:
            total += _rule_area(base, mean, spread, lo, hi)
        else:
            total += _bell_area(mean, spread, lo, hi)
    return total


def _curve_mass(node, run=None, exact=False):
    """Площадь события при данных буквах — медленный путь, через подстановку."""
    parts = _unmix(node)
    if len(parts) > 1 or parts[0][1] is not node:
        return math.fsum(float(sp.sympify(w).subs(run or {})) * _curve_mass(n, run, exact)
                         for w, n in parts)
    if _no_variables(node):
        return 1.0 if _curve_holds(node, 0.0) else 0.0
    base = _curve_base(node)
    fixed = _curve_fix(node, lambda item: float(sp.sympify(item).subs(run or {})))
    if isinstance(base, _Density):
        return base.region_area(fixed, base.shape(run))
    mean, spread = base.numbers(run)
    return _region_area(base, fixed, mean, spread, exact)


_AREAS = []


def _area_call(key, *numbers):
    """Площадь события из реестра при числах вместо букв — быстрый путь.

    Запись реестра бывает и не площадью, а средним по плотности (D6): у неё
    своя функция `call`.
    """
    entry = _AREAS[int(key)]
    if 'call' in entry:
        return entry['call'](*numbers)
    fixed = _curve_fix(entry['node'], lambda item: float(entry['bound'](item)(*numbers)))
    if 'shape' in entry:
        return entry['base'].region_area(fixed, entry['shape'](*numbers))
    mean = float(entry['mean'](*numbers))
    variance = float(entry['variance'](*numbers))
    if not variance > 0:
        raise ValueError('variance')
    return _region_area(entry['base'], fixed, mean, math.sqrt(variance))


class _Area(sp.Function):
    """Площадь события под кривой, пока в модели есть буквы; с числами — число."""

    @classmethod
    def eval(cls, key, *letters):
        if key.is_Integer and all(value.is_number for value in letters):
            try:
                return sp.Float(_area_call(int(key), *[float(v) for v in letters]), 15)
            except (ValueError, TypeError, OverflowError, ZeroDivisionError):
                return sp.nan
        return None


def _numeric_lambda(letters, expr):
    """lambdify, который понимает и площади внутри выражения."""
    return sp.lambdify(letters, sp.sympify(expr), modules=[{'_Area': _area_call}, 'math'])


def _curve_letters(node):
    found = set()
    base = _curve_base(node)
    if isinstance(base, _Density):
        found |= set(base.letters)
    else:
        found |= sp.sympify(base.mean).free_symbols | sp.sympify(base.variance).free_symbols
    for _, leaf in _draw_leaves(node):
        for item in (leaf[1], leaf[3]):
            if not isinstance(item, _Variable):
                found |= sp.sympify(item).free_symbols
    return sorted(found, key=str)


def _area_of(node):
    """Площадь события как выражение sympy: число или _Area от букв."""
    parts = _unmix(node)
    if len(parts) > 1 or parts[0][1] is not node:
        return sp.Add(*[w * _area_of(n) for w, n in parts])
    if _no_variables(node):
        return sp.Integer(1 if _curve_holds(node, 0.0) else 0)
    letters = _curve_letters(node)
    base = _curve_base(node)
    compiled = {}

    def bound(item):
        text = sp.srepr(sp.sympify(item))
        if text not in compiled:
            compiled[text] = _numeric_lambda(letters, item)
        return compiled[text]

    if isinstance(base, _Density):
        _AREAS.append({'node': node, 'base': base, 'bound': bound,
                       'shape': base.compiler(letters)})
    else:
        _AREAS.append({'node': node, 'base': base, 'bound': bound,
                       'mean': sp.lambdify(letters, base.mean, 'math'),
                       'variance': sp.lambdify(letters, base.variance, 'math')})
    if not letters:
        # без букв площадь считается сразу, и ошибка — правило из условия
        # не даёт такой площади — доходит до ячейки, а не прячется в nan
        return sp.Float(_area_call(len(_AREAS) - 1), 15)
    return _Area(sp.Integer(len(_AREAS) - 1), *letters)


def _curve_prob(event, given=None):
    """P(...) для событий над непрерывной величиной — площадь, а не сумма."""
    if given is None:
        return _Prob(_area_of(event.node), 'plain', (event,), f"P({event})")
    base = _area_of(given.node)
    if base.is_number and float(base) == 0:
        raise ValueError(_t(f"условие {given} невозможно",
                            f"the condition {given} cannot happen"))
    joint = _area_of(('and', event.node, given.node))
    return _Prob(joint / base, 'given', (event, given), f"P({event} | {given})")


# ------------------------------------------------------ буквы из площадей

def _solve_small(matrix, right):
    """Линейная система n×n методом Гаусса с выбором главного элемента."""
    n = len(right)
    rows = [list(matrix[i]) + [right[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(rows[r][col]))
        if abs(rows[pivot][col]) < 1e-300:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for r in range(n):
            if r != col:
                factor = rows[r][col] / rows[col][col]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[col])]
    return [rows[i][n] / rows[i][i] for i in range(n)]


def _curve_starts(unknowns, variables, residuals):
    """Начальные точки для поиска букв: числа самого вопроса и масштаб разброса."""
    places, scales, spread_letters, density_letters, inner = set(), set(), set(), set(), set()
    nodes = []
    for residual in residuals:
        for area in residual.atoms(_Area):
            nodes.append(_AREAS[int(area.args[0])])
        plain = residual.xreplace({area: 0 for area in residual.atoms(_Area)})
        places |= {float(n) for n in plain.atoms(sp.Number) if n.is_finite and abs(n) > 1}
    bases = [entry['base'] for entry in nodes] + [v for v in variables
                                                   if isinstance(v, (_Curve, _Density))]
    for base in bases:
        if isinstance(base, _Density):
            # у плотности масштаб задают края промежутков, а буквы в ней
            # бывают любыми положительными: 0,645, 3√3/π, 9
            density_letters |= set(base.letters)
            for lo, hi, _ in base.pieces:
                for edge in (lo, hi):
                    places |= {float(n) for n in edge.atoms(sp.Number) if n.is_finite}
                if lo.is_number and hi.is_number and lo.is_finite and hi.is_finite:
                    # и точки внутри куска: из края промежутка Ньютон для
                    # границы по площади уходит туда, где плотность ноль
                    inner |= {float(lo + (hi - lo) * share) for share in (0.1, 0.3, 0.5, 0.7, 0.9)}
            continue
        spread_letters |= sp.sympify(base.variance).free_symbols
        places |= {float(n) for n in sp.sympify(base.mean).atoms(sp.Number) if n.is_finite}
        if sp.sympify(base.variance).is_number:
            scales.add(math.sqrt(float(base.variance)))
    nodes = [entry for entry in nodes if 'node' in entry]
    for entry in nodes:
        for _, leaf in _draw_leaves(entry['node']):
            for item in (leaf[1], leaf[3]):
                if not isinstance(item, _Variable):
                    places |= {float(n) for n in sp.sympify(item).atoms(sp.Number)
                               if n.is_finite}
    ordered = sorted(places)
    if len(ordered) > 1:
        scales.add((ordered[-1] - ordered[0]) / 2)
    scales = sorted(s for s in scales if s > 0) or [1.0]
    typical = scales[len(scales) // 2]
    spots = [ordered[i] for i in sorted({0, len(ordered) // 2, len(ordered) - 1})] \
        if ordered else [0.0]
    around = sorted({spot + shift * typical for spot in spots for shift in (-1, 0, 1)})
    if len(around) > 5:
        around = [around[round(i * (len(around) - 1) / 4)] for i in range(5)]
    options = []
    for letter in unknowns:
        if letter in spread_letters:
            # и отрицательный: σ² не отличает σ от −σ, а отброшенный корень
            # проверка должна уметь назвать
            options.append([typical / 3, typical, typical * 3, -typical])
        elif letter in density_letters:
            options.append(sorted(set(around) | {0.1, 0.5, 1.0, 2.0, 5.0}))
        elif inner:
            # граница по площади под плотностью: внутри промежутка и возле нуля
            options.append(sorted(inner | {0.1}))
        else:
            options.append(around)
    combos = list(itertools.product(*options))
    if len(combos) > 60:
        combos = combos[::math.ceil(len(combos) / 60)]
    return combos


def _curve_roots(residuals, unknowns, variables):
    """Решения условий на площади — Ньютоном от нескольких начальных точек.

    None — условий меньше, чем букв: решений бесконечно много.
    """
    unknowns = list(unknowns)
    if len(residuals) < len(unknowns):
        return None
    numeric = sp.lambdify(unknowns, list(residuals), modules=[{'_Area': _area_call}, 'math'])
    n = len(unknowns)

    def value(vector):
        try:
            out = [float(v) for v in numeric(*vector)]
        except (ValueError, TypeError, ZeroDivisionError, OverflowError, IndexError):
            return None
        if any(math.isnan(v) or math.isinf(v) for v in out):
            return None
        return out

    def size(vector):
        return max(abs(v) for v in vector)

    def newton_step(here, now):
        columns = []
        for j in range(n):
            nudge = 1e-7 * max(1.0, abs(here[j]))
            moved = list(here)
            moved[j] += nudge
            there = value(moved)
            if there is None:
                return None
            columns.append([(there[i] - now[i]) / nudge for i in range(len(now))])
        square = [[columns[j][i] for j in range(n)] for i in range(n)]
        return _solve_small(square, [-now[i] for i in range(n)])

    found = []
    for start in _curve_starts(unknowns, variables, residuals):
        here = list(start)
        now = value(here)
        if now is None:
            continue
        for _ in range(60):
            if size(now) < 1e-13:
                break
            step = newton_step(here, now)
            if step is None:
                # вырожденная точка — например, граница ровно на среднем, где
                # площадь не чувствует σ: сдвинуться и искать дальше
                here = [v + 1e-3 * max(1.0, abs(v)) * (j + 1) for j, v in enumerate(here)]
                now = value(here)
                if now is None:
                    break
                continue
            share, better = 1.0, False
            while share > 1e-9:
                trial = [here[i] + share * step[i] for i in range(n)]
                there = value(trial)
                if there is not None and size(there) < size(now):
                    here, now, better = trial, there, True
                    break
                share /= 2
            if not better:
                break
        if now is None or size(now) >= 1e-9:
            continue
        # невязка мала и там, где обе площади почти нули, — в далёком хвосте.
        # Корень настоящий, только если и шаг Ньютона здесь мал
        last = newton_step(here, now)
        if last is None or any(abs(d) > 1e-6 * max(1.0, abs(v)) for d, v in zip(last, here)):
            continue
        if not any(all(abs(a - b) <= 1e-6 * max(1.0, abs(a)) for a, b in zip(here, old))
                   for old in found):
            found.append(here)
    return [{u: sp.Float(v, 15) for u, v in zip(unknowns, root)} for root in found]


# ---------------------------------------------------------------- проверка

_FREE_SAMPLES = (1.5, 2.5, 4.0)


def _sf_agree(value, want, sf):
    if sf is None:
        return _draw_agree(value, want)
    return sig(value, sf) == sig(want, sf)


def _sf_words(sf):
    return _t(f"вопрос просит {sf} значащие цифры" if sf < 5 else f"вопрос просит {sf} значащих цифр",
              f"the question asks for {sf} significant figures")


def _curve_swap(node, old, new):
    if node[0] == 'leaf':
        _, left, rel, right = node
        return ('leaf', new if left is old else left, rel, new if right is old else right)
    return (node[0],) + tuple(_curve_swap(child, old, new) for child in node[1:])


def _curve_slips(find, run):
    """Типовые промахи с нормальной величиной — из самого события."""
    slips = {}
    if not (isinstance(find, _Prob) and find.args and isinstance(find.args[0], _Draw)):
        return slips
    target = find.args[0].node
    condition = find.args[1].node if find.kind == 'given' else None

    def area(node, exact=False):
        try:
            return _curve_mass(node, run, exact)
        except (ValueError, TypeError, ZeroDivisionError):
            return None

    whole = area(target if condition is None else ('and', target, condition))
    if condition is not None:
        base, alone = area(condition), area(target)
        if base and alone:
            slips[_t("условная вероятность взята в обратную сторону: посчитано "
                     "P(условие | событие)",
                     "the conditional is the wrong way round: that is "
                     "P(condition | event)")] = whole / alone
            slips[_t("это вероятность пересечения — делить на вероятность условия "
                     "ещё не стали",
                     "that is the intersection: it has not been divided by the "
                     "probability of the condition")] = whole
            slips[_t("в числителе всё событие, а нужна только та его часть, что "
                     "лежит внутри условия",
                     "the numerator is the whole event, but only the part of it "
                     "inside the condition belongs there")] = alone / base
            slips[_t("это вероятность самого условия, а не события внутри него",
                     "that is the probability of the condition itself, not of the "
                     "event inside it")] = base
        return slips
    slips[_t("это площадь с другой стороны от границы: вероятность противоположного "
             "события",
             "that is the area on the other side of the boundary: the probability of "
             "the opposite event")] = 1 - whole
    mixes = [var for var in _draw_vars(target) if isinstance(var, _Mixture)]
    if mixes:
        pieces = _unmix(target)
        for (part, _), (_, alone) in zip(mixes[0].parts, pieces):
            slips[_t(f"это площадь только для {part.name}: вторая часть смеси тоже "
                     f"даёт свою долю",
                     f"that is the area for {part.name} only: the other part of the "
                     f"mixture contributes its share too")] = area(alone)
        plain = [area(alone) for _, alone in pieces]
        if all(v is not None for v in plain):
            slips[_t("площади частей сложены без их долей",
                     "the areas of the parts are added without their shares")] = sum(plain)
            slips[_t("площади частей усреднены поровну, а доли частей разные",
                     "the areas of the parts are averaged equally, and the shares "
                     "differ")] = sum(plain) / len(plain)
        return slips
    base = _curve_base(target)
    leaves = _draw_leaves(target)
    if target[0] == 'and' and len(leaves) == 2:
        for (_, keep), (_, lost) in ((leaves[0], leaves[1]), (leaves[1], leaves[0])):
            slips[_t(f"здесь только «{_draw_say(keep)}»: граница «{_draw_say(lost)}» потеряна",
                     f"this is only «{_draw_say(keep)}»: the boundary «{_draw_say(lost)}» "
                     f"is lost")] = area(keep)
    if isinstance(base, _Density):
        return _density_slips(base, target, leaves, run, slips)
    if len(leaves) == 1 and isinstance(leaves[0][1][1], _Curve) and \
            not isinstance(leaves[0][1][3], _Variable):
        mean, spread = base.numbers(run)
        edge = float(sp.sympify(leaves[0][1][3]).subs(run))
        height = math.exp(-(edge - mean) ** 2 / (2 * spread * spread)) / (spread * math.sqrt(2 * math.pi))
        slips[_t(f"посчитаны оба хвоста, а спрашивают только тот, что за {sig(edge, 6)}",
                 f"that counts both tails, and only the one beyond {sig(edge, 6)} is "
                 f"asked")] = 2 * min(whole, 1 - whole)
        slips[_t(f"это высота кривой в точке {sig(edge, 6)}, а вероятность — площадь под ней",
                 f"that is the height of the curve at {sig(edge, 6)}; a probability is "
                 f"the area under it")] = height
        if _curve_holds(_curve_fix(target, lambda item: float(sp.sympify(item).subs(run))), mean) \
                and base.rule is None:
            slips[_t("это площадь только от среднего до границы: половина кривой по "
                     "другую сторону от среднего потеряна",
                     "that is only the area from the mean to the boundary: the half of "
                     "the curve on the other side of the mean is lost")] = \
                _bell_area(mean, spread, min(mean, edge), max(mean, edge))
    if base.rule is not None:
        slips[_t("это площадь под точной кривой, а вопрос велит пользоваться правилом "
                 "из условия",
                 "that is the area under the exact curve, and the question says to use "
                 "the rule it gives")] = area(target, exact=True)
    try:
        wide = _Curve(base.mean, sp.sympify(base.variance) ** 2, base.name)
        slips[_t("в N(μ, σ²) второе число — дисперсия: вместо σ взята σ²",
                 "the second number in N(μ, σ²) is the variance: σ² was used where σ "
                 "belongs")] = _curve_mass(_curve_swap(target, base, wide), run)
    except (ValueError, TypeError):
        pass
    return slips


def _curve_runs(label, conditions, unknowns, variables, free_run):
    """Годные наборы букв при данных значениях свободных букв, или None с сообщением."""
    conditions = [sp.sympify(c).subs(free_run) if not isinstance(c, (tuple, list)) else c
                  for c in conditions]
    letters = [u for u in _letters_in(variables, conditions) if u not in free_run]
    for name in unknowns:
        if name not in letters:
            letters.append(name)
    if not conditions and not letters:
        return [dict(free_run)]
    good, _ = _letter_runs(conditions, letters, variables)
    if good is None:
        print(f"{NO} {label}: " + _t("условий не хватает, чтобы найти буквы",
                                     "the conditions are not enough to fix the letters"))
        return None
    if not good:
        print(f"{NO} {label}: " + _t("условиям не отвечает ни одна годная модель",
                                     "no valid model satisfies the conditions"))
        return None
    return [{**free_run, **run} for run in good]


def _curve_variables(find, conditions=()):
    found = []
    items = [find] + list(conditions)
    for item in items:
        nodes = []
        if isinstance(item, _Prob) and item.args and isinstance(item.args[0], _Draw):
            nodes += [arg.node for arg in item.args if isinstance(arg, _Draw)]
        try:
            expr = sp.sympify(item)
        except (sp.SympifyError, TypeError):
            expr = None
        if isinstance(expr, sp.Basic):
            for area in expr.atoms(_Area):
                entry = _AREAS[int(area.args[0])]
                if 'node' in entry:
                    nodes.append(entry['node'])
                elif not any(entry['base'] is seen for seen in found):
                    found.append(entry['base'])
        for node in nodes:
            for _, piece in _unmix(node):
                if _no_variables(piece):
                    continue
                base = _curve_base(piece)
                if not any(base is seen for seen in found):
                    found.append(base)
    return found


def _verify_curve_chance(label, got, find, given, var, sf, percent, free):
    """verify_chance для непрерывной величины: ответ — площадь."""
    try:
        answer = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        answer = None
    loose = _as_unknowns(free)
    # ответ-выражение от свободных букв: «покажите, что площадь равна
    # 1/√k − 1/√(16 + k)» (D6) — сверяется при каждом их значении
    if answer is None or (getattr(answer, 'free_symbols', set()) - set(loose)) \
            or (not answer.free_symbols and (not answer.is_number or answer.is_real is False)):
        print(f"{NO} {label}: " + (_t("процент это число", "a percentage is a number")
                                   if percent else _t("вероятность это число",
                                                      "a probability is a number")))
        return False
    conditions = _as_conditions(given)
    unknowns = _as_unknowns(var)
    variables = _curve_variables(find, conditions)
    samples = [{}]
    if loose:
        samples = [{letter: sp.Float(s) for letter in loose} for s in _FREE_SAMPLES]
    unit = 100 if percent else 1
    for sample in samples:
        value = answer.subs(sample)
        if not value.is_number or value.is_real is False:
            print(f"{NO} {label}: " + _t("выражение не вычисляется", "the expression does not evaluate"))
            return False
        runs = _curve_runs(label, conditions, unknowns, variables, sample)
        if runs is None:
            return False
        for run in runs:
            want = float(sp.sympify(find).subs(run)) * unit
            if _sf_agree(value, want, sf):
                if sf is not None and float(value) != float(sig(value, sf)):
                    print(f"{NO} {label}: " + _sf_words(sf))
                    return False
                continue
            letters_only = {u: v for u, v in run.items() if u not in sample}
            for rounded, how in _rounded_runs(letters_only):
                near = float(sp.sympify(find).subs({**sample, **rounded})) * unit
                if not _sf_agree(near, want, sf) and _sf_agree(value, near, sf):
                    print(f"{OK} {label}: " + _t(
                        f"сходится с {how}, округлённым по дороге. Схема оценивания "
                        f"такое принимает, но промежуточное значение лучше держать "
                        f"полностью",
                        f"this matches {how} rounded on the way. The markscheme "
                        f"accepts it, but carry the full value next time"))
                    return True
            if sf is not None and _draw_agree(value, want):
                print(f"{NO} {label}: " + _sf_words(sf))
                return False
            if percent and _draw_agree(float(value) * 100, want):
                print(f"{NO} {label}: " + _t(
                    "это вероятность, а вопрос просит процент",
                    "that is a probability, and the question asks for a percentage"))
                return False
            if not percent and float(value) > 1 and _sf_agree(float(value) / 100, want, sf):
                print(f"{OK} {label}: " + _t(
                    "это процент, а вопрос просит вероятность. Схема оценивания "
                    "такое принимает, но записывать лучше долей единицы",
                    "that is a percentage, and the question asks for a probability. "
                    "The markscheme accepts it, but write it as a probability"))
                return True
            if not -_PROB_TOL <= float(value) / unit <= 1 + _PROB_TOL:
                print(f"{NO} {label}: " + (_t(
                    "процент лежит между 0 и 100", "a percentage lies between 0 and 100")
                    if percent else _t(
                    "вероятность не бывает меньше нуля или больше единицы",
                    "a probability is never below zero or above one")))
                return False
            for what, slip in _curve_slips(find, run).items():
                if slip is None:
                    continue
                slip = float(slip) * unit
                if not _sf_agree(slip, want, sf) and _sf_agree(value, slip, sf):
                    print(f"{NO} {label}: {what}")
                    return False
            if sf is None and sig(value, 2) == sig(want, 2) and float(sig(value, 2)) == float(value):
                print(f"{NO} {label}: " + _t(
                    "две значащие цифры, а нужны три",
                    "two significant figures, and three are needed"))
                return False
            print(f"{NO} {label}: " + _t("у этой модели выходит другое",
                                         "this model gives something else"))
            return False
    print(f"{OK} {label}")
    return True


# Ссылки вперёд: эти имена зовутся только изнутри функций, а модули,
# где они живут, сами импортируют этот. Поэтому импорт стоит в конце.
from .density import _Density, _density_slips  # noqa: E402
