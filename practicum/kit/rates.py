"""Скорости и наилучшее (E9): движение по прямой, связанные скорости, оптимизация.
"""

import math

import mpmath as mp
import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .tangent import _rounds_to, _say


# ================================================================ скорости
# Двадцать девятое понятие равенства ответов: **скорость меряют движением,
# а наилучшее — выбирают из всего, что разрешено**.
#
# Проверка не дифференцирует ни разу. Скорость величины в момент t — это
# то, насколько она сдвинулась, пока время сдвинулось на мгновение: время
# двигают на 10⁻¹² в обе стороны и делят разность на промежуток. Счёт идёт
# с пятьюдесятью знаками, и от мгновения в ответе не остаётся ничего:
# ошибка такого деления — квадрат шага, 10⁻²⁴. Ускорение — та же мера,
# взятая у скорости.
#
# Связанные скорости — это картинка, которая движется. Связь между
# величинами (объём и высота, угол и сторона) обязана выполняться в каждый
# момент, и проверка не выводит из неё формулу для dh/dt. Она подталкивает
# каждую величину по отдельности и смотрит, насколько связь ломается. Набор
# скоростей годится, если при движении с ними все поломки взаимно
# гасятся: картинка сдвинулась, а связь осталась верной.
#
# Наилучшее — не корень f′ = 0. Это лучшее значение из всего, что условие
# разрешает: проверка просматривает весь промежуток вместе с его концами, а
# если величина считает предметы — каждое целое число. Поэтому ей всё
# равно, где стоит ответ: в вершине, на конце отрезка или в целой точке
# рядом с вершиной. Ученик, который решает только f′ = 0, ошибается ровно
# там, где ответ не в вершине, — и там проверка называет промах.

_DPS = 50                     # столько знаков у счёта скоростей
_NUDGE = mp.mpf(10) ** -12    # мгновение: на столько двигают время
_GRID = 4000                  # столько точек просматривается на промежутке
_ENDLESS = 50                 # бесконечный промежуток времени смотрят на такую длину
_WIDE = 60                    # столько ещё просматривается за краями области
_EXACT_TOL = 1e-9             # точный ответ сверяется с найденным до этой доли
_INTEGER_CAP = 100000         # больше целых перебирать не станем
_QUANTITIES = ('displacement', 'velocity', 'speed', 'acceleration')


def _precise(fn):
    """Весь счёт внутри — с пятьюдесятью знаками, а не с пятнадцатью по умолчанию."""
    def wrapped(*args, **kwargs):
        with mp.workdps(_DPS):
            return fn(*args, **kwargs)
    wrapped.__name__, wrapped.__doc__ = fn.__name__, fn.__doc__
    return wrapped


def _mp_real(value):
    """Число mpmath или None: комплексное с заметной мнимой частью — не число."""
    try:
        if isinstance(value, mp.mpc):
            if abs(value.imag) > mp.mpf(10) ** (-_DPS // 2) * max(1, abs(value.real)):
                return None
            value = value.real
        value = mp.mpf(value)
    except (TypeError, ValueError, ZeroDivisionError, OverflowError):
        return None
    return value if mp.isfinite(value) else None


class _Measured:
    """Величина как функция одного числа — времени или буквы задачи.

    Два счёта одной величины: быстрый, в обычных float, — чтобы
    просмотреть промежуток по тысячам точек, и точный, в пятидесяти знаках,
    — чтобы уточнить найденный корень или вершину. Оба отдают None там, где
    величины нет (корень из отрицательного, деление на ноль). Такие
    величины складываются и вычитаются: `rate_of(hB) - rate_of(hA)`.
    """

    def __init__(self, fn, text, var, expr=None, quick=None):
        self.fn, self.text, self.var, self.expr = fn, text, var, expr
        self._quick = quick

    def __call__(self, value):
        with mp.workdps(_DPS):
            try:
                return _mp_real(self.fn(mp.mpf(value)))
            except (TypeError, ValueError, ZeroDivisionError, OverflowError,
                    AttributeError):
                return None

    def quick(self, value):
        """Быстрый счёт в float — для просмотра сетки."""
        if self._quick is None:
            found = self(value)
            return None if found is None else float(found)
        try:
            found = self._quick(float(value))
        except (TypeError, ValueError, ZeroDivisionError, OverflowError, AttributeError,
                NameError):
            return None
        if isinstance(found, complex):
            if abs(found.imag) > 1e-9 * max(1.0, abs(found.real)):
                return None
            found = found.real
        try:
            found = float(found)
        except (TypeError, ValueError):
            return None
        return found if math.isfinite(found) else None

    def __repr__(self):
        return self.text

    def _join(self, other, how, sign):
        other = _quantity_of(other, self.var)

        def fn(u):
            one, two = self(u), other(u)
            return None if one is None or two is None else how(one, two)

        def quick(u):
            one, two = self.quick(u), other.quick(u)
            return None if one is None or two is None else how(one, two)
        return _Measured(fn, f"({self.text} {sign} {other.text})", self.var, quick=quick)

    def __add__(self, other):
        return self._join(other, lambda a, b: a + b, '+')

    def __radd__(self, other):
        return _quantity_of(other, self.var)._join(self, lambda a, b: a + b, '+')

    def __sub__(self, other):
        return self._join(other, lambda a, b: a - b, '−')

    def __rsub__(self, other):
        return _quantity_of(other, self.var)._join(self, lambda a, b: a - b, '−')

    def __mul__(self, other):
        return self._join(other, lambda a, b: a * b, '·')

    def __rmul__(self, other):
        return _quantity_of(other, self.var)._join(self, lambda a, b: a * b, '·')

    def __truediv__(self, other):
        return self._join(other, lambda a, b: a / b if b else None, '/')

    def __neg__(self):
        return _Measured(lambda u: None if self(u) is None else -self(u),
                         f"−{self.text}", self.var,
                         quick=lambda u: None if self.quick(u) is None else -self.quick(u))

    def __abs__(self):
        return _Measured(lambda u: None if self(u) is None else abs(self(u)),
                         f"|{self.text}|", self.var,
                         quick=lambda u: None if self.quick(u) is None else abs(self.quick(u)))

    def shifted(self, level):
        """Та же величина минус число: её нули — моменты, когда она равна level."""
        level = mp.mpf(level)
        return _Measured(lambda u: None if self(u) is None else self(u) - level,
                         f"{self.text} − {level}", self.var,
                         quick=lambda u: None if self.quick(u) is None
                         else self.quick(u) - float(level))


def _quantity_of(q, var):
    """Выражение sympy, число или уже измеряемая величина — в _Measured."""
    if isinstance(q, _Measured):
        return q
    expr = sp.sympify(q)
    extra = expr.free_symbols - {var}
    if extra:
        raise ValueError(_t(f"в величине лишние буквы: {sorted(map(str, extra))}",
                            f"the quantity has letters other than {var}: "
                            f"{sorted(map(str, extra))}"))
    fn = sp.lambdify(var, expr, 'mpmath')
    try:
        quick = sp.lambdify(var, expr, 'math')
        quick(0.5)
    except (NameError, TypeError, AttributeError, KeyError, RecursionError):
        quick = None
    except (ValueError, ZeroDivisionError, OverflowError):
        pass
    return _Measured(fn, str(expr), var, expr, quick)


def rate_of(q, var=t):
    """Скорость изменения величины — измеренная, а не выведенная.

    `rate_of(H)` в момент 13 — это (H(13 + h) − H(13 − h)) / 2h при
    h = 10⁻¹²: насколько сдвинулась высота, пока время сдвинулось на
    мгновение. Производной внутри нет. У края области, где с одной
    стороны величины нет, мгновение берётся с той стороны, где она есть.
    Для просмотра сетки то же самое делается в float с шагом 10⁻⁵.
    """
    base = _quantity_of(q, var)

    def fn(u):
        ahead, behind = base(u + _NUDGE), base(u - _NUDGE)
        if ahead is not None and behind is not None:
            return (ahead - behind) / (2 * _NUDGE)
        here = base(u)
        if here is None:
            return None
        if ahead is not None:
            further = base(u + 2 * _NUDGE)
            return None if further is None else (-3 * here + 4 * ahead - further) / (2 * _NUDGE)
        if behind is not None:
            further = base(u - 2 * _NUDGE)
            return None if further is None else (3 * here - 4 * behind + further) / (2 * _NUDGE)
        return None

    def quick(u):
        step = 1e-5 * max(1.0, abs(u))
        ahead, behind = base.quick(u + step), base.quick(u - step)
        if ahead is not None and behind is not None:
            return (ahead - behind) / (2 * step)
        return None if base.quick(u) is None else fn(u)
    return _Measured(fn, f"d({base.text})/d{var}", var, quick=quick)


def _in_degrees(expr):
    """То же выражение, посчитанное калькулятором в градусах: sin(t) как sin(t°)."""
    trig = (sp.sin, sp.cos, sp.tan, sp.sec, sp.csc, sp.cot)
    return sp.sympify(expr).replace(lambda e: isinstance(e, trig),
                                    lambda e: e.func(e.args[0] * sp.pi / 180))


def _span_of(span):
    """Промежуток времени из условия: концы числами и открыт ли каждый."""
    if isinstance(span, sp.Interval):
        lo, hi, open_lo, open_hi = span.start, span.end, span.left_open, span.right_open
    else:
        lo, hi = span
        open_lo = open_hi = False
    lo = float(sp.N(sp.sympify(lo), 30))
    if sp.sympify(hi) in (sp.oo,) or hi == math.inf:
        hi, open_hi = lo + _ENDLESS, True
    else:
        hi = float(sp.N(sp.sympify(hi), 30))
    return lo, hi, open_lo, open_hi


# ========================================================= просмотр и поиск
# Промежуток просматривается быстрым счётом, по тысячам точек в float, а
# найденное — корень или вершина — уточняется точным, в пятидесяти знаках.

def _grid(lo, hi, count=_GRID):
    lo, hi = float(lo), float(hi)
    step = (hi - lo) / count
    return [lo + step * i for i in range(count + 1)]


@_precise
def _bisect(fn, left, right):
    """Корень между двумя точками разного знака — делением пополам, точно."""
    left, right = mp.mpf(left), mp.mpf(right)
    fl = fn(left)
    if fl is None:
        return None
    for _ in range(120):
        middle = (left + right) / 2
        fm = fn(middle)
        if fm is None:
            return None
        if fm == 0:
            return middle
        if (fm > 0) == (fl > 0):
            left, fl = middle, fm
        else:
            right = middle
        if right - left < mp.mpf(10) ** -30 * max(1, abs(left)):
            break
    return (left + right) / 2


@_precise
def _golden(fn, left, right, kind):
    """Вершина между двумя точками — золотым сечением, без производной."""
    left, right = mp.mpf(left), mp.mpf(right)
    ratio = (mp.sqrt(5) - 1) / 2
    better = (lambda a, b: a < b) if kind == 'min' else (lambda a, b: a > b)
    one, two = right - ratio * (right - left), left + ratio * (right - left)
    f1, f2 = fn(one), fn(two)
    for _ in range(110):
        if f1 is None or f2 is None:
            break
        if better(f1, f2):
            right, two, f2 = two, one, f1
            one = right - ratio * (right - left)
            f1 = fn(one)
        else:
            left, one, f1 = one, two, f2
            two = left + ratio * (right - left)
            f2 = fn(two)
    place = (left + right) / 2
    return place, fn(place)


@_precise
def _zeros(fn, lo, hi, count=_GRID):
    """Все места, где величина обращается в ноль, и пересекает ли она там ноль.

    Смена знака между соседними точками сетки — пересечение. Касание нуля
    без смены знака (частица остановилась и поехала дальше) видно иначе:
    |f| проседает почти до нуля между соседями. Его ищут золотым сечением
    по |f| и признают, если провал доходит до нуля с точностью счёта.
    """
    points = _grid(lo, hi, count)
    known = [(u, f) for u, f in ((u, fn.quick(u)) for u in points) if f is not None]
    if not known:
        return []
    scale = max(abs(f) for _, f in known) or 1.0
    found = []
    for (u, fu), (w, fw) in zip(known, known[1:]):
        if fu == 0:
            found.append((mp.mpf(u), None))
        elif fw != 0 and (fu > 0) != (fw > 0):
            root = _bisect(fn, u, w)
            if root is not None:
                found.append((root, True))
    if known[-1][1] == 0:
        found.append((mp.mpf(known[-1][0]), None))
    size = abs(fn)
    for i in range(1, len(known) - 1):
        (u, fu), (w, fw), (z, fz) = known[i - 1], known[i], known[i + 1]
        if abs(fw) <= abs(fu) and abs(fw) <= abs(fz) and fw != 0 \
                and (fu > 0) == (fw > 0) == (fz > 0) and abs(fw) < scale * 1e-2:
            place, depth = _golden(size, u, z, 'min')
            if depth is not None and depth < scale * mp.mpf(10) ** -20:
                found.append((place, False))
    tidy = []
    for place, crosses in sorted(found, key=lambda item: item[0]):
        if tidy and abs(place - tidy[-1][0]) < (hi - lo) * 1e-9:
            continue
        if crosses is None:
            step = (hi - lo) / count / 10
            left, right = fn.quick(place - step), fn.quick(place + step)
            crosses = left is not None and right is not None and (left > 0) != (right > 0)
        tidy.append((place, crosses))
    return tidy


@_precise
def _turning(fn, lo, hi, count=_GRID):
    """Все вершины величины внутри промежутка: (место, значение, 'max' или 'min')."""
    points = _grid(lo, hi, count)
    values = [fn.quick(u) for u in points]
    out = []
    for i in range(1, len(points) - 1):
        a, b, c = values[i - 1], values[i], values[i + 1]
        if a is None or b is None or c is None:
            continue
        if b >= a and b > c or b > a and b >= c:
            place, value = _golden(fn, points[i - 1], points[i + 1], 'max')
            out.append((place, value, 'max'))
        elif b <= a and b < c or b < a and b <= c:
            place, value = _golden(fn, points[i - 1], points[i + 1], 'min')
            out.append((place, value, 'min'))
    return [item for item in out if item[1] is not None]


@_precise
def _optimum(fn, lo, hi, kind, open_lo=False, open_hi=False, integer=False):
    """Наилучшее значение на промежутке: вершины и концы, или каждое целое.

    Отдаёт (место, значение). Открытый конец в сравнение не идёт: к нему
    можно подойти сколь угодно близко, но стоять на нём нельзя.
    """
    better = (lambda a, b: a < b) if kind == 'min' else (lambda a, b: a > b)
    if integer:
        start = math.floor(lo) + 1 if open_lo or lo != math.floor(lo) else int(lo)
        end = math.ceil(hi) - 1 if open_hi or hi != math.ceil(hi) else int(hi)
        best = None
        for n in range(start, min(end, start + _INTEGER_CAP) + 1):
            value = fn(n)
            if value is not None and (best is None or better(value, best[1])):
                best = (mp.mpf(n), value)
        return best
    width = mp.mpf(hi) - mp.mpf(lo)
    inner_lo = mp.mpf(lo) + (width * mp.mpf(10) ** -9 if open_lo else 0)
    inner_hi = mp.mpf(hi) - (width * mp.mpf(10) ** -9 if open_hi else 0)
    candidates = [(place, value) for place, value, what in _turning(fn, inner_lo, inner_hi)
                  if what == kind]
    for end, is_open in ((mp.mpf(lo), open_lo), (mp.mpf(hi), open_hi)):
        if not is_open and fn(end) is not None:
            candidates.append((end, fn(end)))
    if not candidates:
        # Ни вершины внутри, ни закрытого конца: к краю можно подойти сколь
        # угодно близко, но лучшего значения у величины нет вовсе.
        return None
    best = candidates[0]
    for item in candidates[1:]:
        if better(item[1], best[1]):
            best = item
    return best


# ================================================================== ответы

def _rate_number(value):
    """Ответ-число: float или точное значение sympy. Иначе None."""
    if isinstance(value, bool) or value is None:
        return None
    try:
        value = sp.sympify(value)
    except (sp.SympifyError, TypeError):
        return None
    if not value.is_number:
        return None
    try:
        number = complex(sp.N(value, 30))
    except (TypeError, ValueError):
        return None
    if abs(number.imag) > 1e-12 * max(1.0, abs(number.real)):
        return None
    return number.real


def _is_decimal(value):
    """Записан ли ответ десятичной дробью, а не точным значением."""
    try:
        value = sp.sympify(value)
    except (sp.SympifyError, TypeError):
        return False
    floats = value.atoms(sp.Float)
    return bool(floats) and not all(f == int(f) for f in floats)


def _rate_agrees(got, want, exact=False):
    """Годится ли ответ: точный — до 10⁻⁹, десятичный — до трёх значащих цифр."""
    if got is None or want is None:
        return False
    mine = _rate_number(got)
    if mine is None:
        return False
    want = float(want)
    if not _is_decimal(got):
        if abs(mine - want) <= _EXACT_TOL * max(1.0, abs(want)):
            return True
        # Целое без точки на калькуляторной бумаге — это тоже округление:
        # 425 вместо 424.88…, 1550 вместо 1554.26…
        return not exact and mine == int(mine) and _rounds_to(mine, want)
    return not exact and _rounds_to(mine, want)


def _rate_close(got, value):
    """Совпадает ли ответ с чужим числом — для названия промаха."""
    if value is None:
        return False
    mine = _rate_number(got)
    if mine is None:
        return False
    return _rate_agrees(got, value) or _rounds_to(mine, float(value))


def _two_figures(got, want):
    """Ответ округлён до двух значащих цифр там, где просят три."""
    mine = _rate_number(got)
    if mine is None or want is None or not _is_decimal(got) or float(want) == 0:
        return False
    digits = len(sp.Float(mine, 15).__format__('.15g').replace('-', '').replace('.', '')
                 .lstrip('0').rstrip('0'))
    return digits <= 2 and _rounds_to(mine, float(want), 2)


def _exact_refusal(label, got, exact):
    """Бумага без калькулятора: десятичный ответ не принимается."""
    if exact and _is_decimal(got):
        print(f"{NO} {label}: " + _t(
            "это десятичная запись, а бумага без калькулятора: нужно точное значение",
            "this is a decimal, and the paper has no calculator: give the exact value"))
        return True
    return False


def _verdict(label, got, want, slips, exact=False, fallback=None, shown=None):
    """Общий разбор: сходится, узнанный промах или мимо. Промахи — по порядку."""
    if _exact_refusal(label, got, exact):
        return False
    if _rate_agrees(got, want, exact):
        print(f"{OK} {label}: {shown if shown is not None else _say(got)}")
        return True
    if _rate_number(got) is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    for value, message in (slips() if callable(slips) else slips):
        if value is not None and _rate_close(got, value) and not _rate_close(got, want):
            print(f"{NO} {label}: {message}")
            return False
    if _rate_close(-_rate_number(got), want):
        print(f"{NO} {label}: " + _t("знак не тот", "the sign is wrong"))
        return False
    if _two_figures(got, want):
        print(f"{NO} {label}: " + _t("нужно три значащие цифры", "give three significant figures"))
        return False
    print(f"{NO} {label}: " + (fallback or _t("выходит другое число",
                                              "the number is something else")))
    return False


def _times_of(got):
    """Ответ-моменты: одно число или список чисел."""
    if isinstance(got, (list, tuple, set, sp.FiniteSet)):
        items = list(got)
    else:
        items = [got]
    numbers = [_rate_number(item) for item in items]
    return None if any(n is None for n in numbers) else numbers


def _at_str(place):
    return _say(place)


# ======================================================= движение по прямой

class _Particle:
    """Частица на прямой: её скорость или перемещение и промежуток времени."""

    def __init__(self, v, s, span, var):
        if (v is None) == (s is None):
            raise ValueError(_t("частица задаётся одним: v=… или s=…",
                                "a particle is given by one of v=… or s=…"))
        self.var, self.span = var, span
        self.lo, self.hi, self.open_lo, self.open_hi = _span_of(span)
        self.given = 's' if s is not None else 'v'
        self.expr = sp.sympify(s if s is not None else v)
        self.s = _quantity_of(s, var) if s is not None else None
        self.v = _quantity_of(v, var) if v is not None else rate_of(self.s, var)
        self.a = rate_of(self.v, var)
        self.speed = abs(self.v)

    def quantity(self, name):
        found = {'displacement': self.s, 'velocity': self.v, 'speed': self.speed,
                 'acceleration': self.a}.get(name)
        if name not in _QUANTITIES:
            raise ValueError(f"quantity: one of {_QUANTITIES}")
        if found is None:
            raise ValueError(_t("перемещения нет: частица задана скоростью",
                                "there is no displacement: the particle is given by its velocity"))
        return found

    def in_degrees(self):
        """Та же частица, если калькулятор стоял в градусах."""
        changed = _in_degrees(self.expr)
        if changed == self.expr:
            return None
        return _Particle(changed if self.given == 'v' else None,
                         changed if self.given == 's' else None, self.span, self.var)

    def __repr__(self):
        return f"particle({self.given}={self.expr}, span={self.span})"


def particle(v=None, s=None, span=(0, 10), var=t):
    """Частица на прямой: `particle(v=t*sin(t) - 3, span=(0, 10))`.

    Задаётся тем, что дано в условии: скоростью v или перемещением s.
    Ускорение проверка меряет сама — как скорость изменения скорости, — а
    по перемещению меряет и скорость. span — промежуток времени из условия;
    `(0, oo)` значит «t ≥ 0», и тогда смотрят первые пятьдесят единиц.
    """
    return _Particle(v, s, span, var)


@_precise
def _event_moments(P, event, lo=None, hi=None):
    """Моменты события внутри промежутка: 'rest', 'turn' или ('acceleration', 4)."""
    lo = P.lo if lo is None else lo
    hi = P.hi if hi is None else hi
    if event in ('rest', 'turn'):
        zeros = _zeros(P.v, lo, hi)
        return [place for place, crosses in zeros if event == 'rest' or crosses]
    name, level = event
    source = P.quantity(name)
    level = mp.mpf(float(sp.N(sp.sympify(level), 30)))
    return [place for place, _ in _zeros(source.shifted(level), lo, hi)]


def _event_words(event):
    if event == 'rest':
        return _t("частица стоит", "the particle is at rest")
    if event == 'turn':
        return _t("частица меняет направление", "the particle changes direction")
    name, level = event
    words = {'displacement': _t('перемещение', 'the displacement'),
             'velocity': _t('скорость', 'the velocity'),
             'speed': _t('модуль скорости', 'the speed'),
             'acceleration': _t('ускорение', 'the acceleration')}[name]
    return f"{words} = {_say(level)}"


def _ordinal(n):
    return _t(f"{n}-й раз", {1: 'the first time', 2: 'the second time',
                             3: 'the third time'}.get(n, f'time number {n}'))


@_precise
def _motion_moment(P, at):
    """Момент из условия: число или слово — 'turn', ('turn', 2), 'fastest'…"""
    if isinstance(at, str) or (isinstance(at, tuple) and at and isinstance(at[0], str)):
        kind, index = (at, 1) if isinstance(at, str) else at
        if kind in ('rest', 'turn'):
            moments = _event_moments(P, kind)
            return moments[index - 1] if len(moments) >= index else None
        if kind == 'fastest':
            best = _optimum(P.speed, P.lo, P.hi, 'max', P.open_lo, P.open_hi)
            return None if best is None else best[0]
        if kind == 'start':
            return mp.mpf(P.lo)
        raise ValueError("at: a number, 'rest', 'turn', ('turn', 2) or 'fastest'")
    return mp.mpf(float(sp.N(sp.sympify(at), 30)))


def _moment_words(at):
    if isinstance(at, str):
        at = (at, 1)
    if isinstance(at, tuple) and at and isinstance(at[0], str):
        kind, index = at
        return {'rest': _t(f"когда частица стоит ({_ordinal(index)})",
                           f"when the particle is at rest ({_ordinal(index)})"),
                'turn': _t(f"когда частица меняет направление ({_ordinal(index)})",
                           f"when the particle changes direction ({_ordinal(index)})"),
                'fastest': _t("когда модуль скорости наибольший",
                              "when the speed is greatest"),
                'start': _t("в начале", "at the start")}[kind]
    return f"t = {_say(at)}"


def _quantity_words(name):
    return {'displacement': _t('перемещение', 'the displacement'),
            'velocity': _t('скорость', 'the velocity'),
            'speed': _t('модуль скорости', 'the speed'),
            'acceleration': _t('ускорение', 'the acceleration')}[name]


@_precise
def verify_motion(label, got, P, quantity, at):
    """Величина движения в момент: `verify_motion('4', q4, P, 'acceleration', ('turn', 2))`.

    quantity — 'displacement', 'velocity', 'speed' или 'acceleration'; at —
    число или момент словами условия: 'rest', 'turn', ('turn', 2) — второй
    раз меняет направление, 'fastest' — модуль скорости наибольший. Момент
    проверка находит сама, и ускорение в нём меряет сама.
    """
    if _blank(label, got):
        return False
    when = _motion_moment(P, at)
    if when is None:
        raise ValueError(f"verify_motion: no such moment in the span: {at}")
    want = P.quantity(quantity)(when)
    def slips():
        found_slips = []
        for other in _QUANTITIES:
            if other == quantity or (other == 'displacement' and P.s is None):
                continue
            found_slips.append((P.quantity(other)(when), _t(
                f"это {_quantity_words(other)} в тот момент, а вопрос про {_quantity_words(quantity)}",
                f"that is {_quantity_words(other)} at that moment, and the question asks for "
                f"{_quantity_words(quantity)}")))
        if isinstance(at, (str, tuple)):
            kind = at if isinstance(at, str) else at[0]
            index = 1 if isinstance(at, str) else at[1]
            if kind in ('rest', 'turn'):
                for n, moment in enumerate(_event_moments(P, kind), start=1):
                    if n != index:
                        found_slips.append((P.quantity(quantity)(moment), _t(
                            f"это момент t = {_say(moment)}: {_ordinal(n)}, а вопрос про "
                            f"{_ordinal(index)}",
                            f"that is at t = {_say(moment)}, {_ordinal(n)}; the question asks "
                            f"for {_ordinal(index)}")))
            if kind == 'fastest':
                for place, _, what in _turning(P.v, P.lo, P.hi):
                    found_slips.append((P.quantity(quantity)(place), _t(
                        f"это в вершине графика скорости, t = {_say(place)}, но модуль скорости "
                        f"больше всего не там: смотрите и концы промежутка",
                        f"that is at a turning point of the velocity graph, t = {_say(place)}, but "
                        f"the speed is not greatest there: check the ends of the interval too")))
        turned = P.in_degrees()
        if turned is not None:
            try:
                other_when = _motion_moment(turned, at)
                if other_when is not None:
                    found_slips.append((turned.quantity(quantity)(other_when), _t(
                        "калькулятор в градусах: время здесь в радианах",
                        "the calculator is in degrees: t here is in radians")))
            except ValueError:
                pass
        return found_slips
    return _verdict(label, got, want, slips, fallback=_t(
        f"{_quantity_words(quantity)} {_moment_words(at)} другое",
        f"{_quantity_words(quantity)} {_moment_words(at)} is something else"))


@_precise
def verify_when(label, got, P, event, which=1):
    """Момент события: `verify_when('3(a)', q, P, 'turn')`.

    event — 'rest' (стоит), 'turn' (меняет направление) или пара вроде
    ('acceleration', 4): когда ускорение равно 4. which — какой по счёту
    раз, начиная с 1, или 'all' — все моменты списком.
    """
    if _blank(label, got):
        return False
    moments = _event_moments(P, event)
    mine = _times_of(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — момент времени, число",
                                     "the answer is a time, a number"))
        return False
    if which == 'all':
        want = moments
        shown = ', '.join(_say(m) for m in mine)
        if len(mine) == len(want) and all(_rate_agrees(m, w) for m, w in zip(sorted(mine), want)):
            print(f"{OK} {label}: {shown}")
            return True
        if len(mine) < len(want) and all(any(_rate_agrees(m, w) for w in want) for m in mine):
            print(f"{NO} {label}: " + _t(f"не все: таких моментов {len(want)}",
                                         f"not all of them: there are {len(want)} such times"))
            return False
    else:
        if len(moments) < which:
            raise ValueError(f"verify_when: fewer than {which} moments for {event}")
        target = moments[which - 1]
        if len(mine) > 1:
            if any(_rate_agrees(m, target) for m in mine):
                print(f"{NO} {label}: " + _t(
                    "просят один момент; лишние значения схема не прощает",
                    "one time is asked for, and the markscheme does not accept extra values"))
            else:
                print(f"{NO} {label}: " + _t("просят один момент", "one time is asked for"))
            return False
        if _rate_agrees(mine[0], target):
            print(f"{OK} {label}: t = {_say(got)}")
            return True
        for n, moment in enumerate(moments, start=1):
            if n != which and _rate_close(mine[0], moment):
                print(f"{NO} {label}: " + _t(
                    f"это {_ordinal(n)}, а вопрос про {_ordinal(which)}",
                    f"that is {_ordinal(n)}, and the question asks for {_ordinal(which)}"))
                return False
    slips = _when_slips(P, event)
    for value, message in slips:
        if any(_rate_close(m, value) for m in mine):
            print(f"{NO} {label}: {message}")
            return False
    print(f"{NO} {label}: " + _t(f"в этот момент не {_event_words(event)}",
                                 f"at that time it is not true that {_event_words(event)}"))
    return False


def _when_slips(P, event):
    """Моменты, которые путают с нужным: соседнее событие, края, градусы."""
    found_slips = []
    width = P.hi - P.lo
    for moment in _event_moments(P, event, P.lo - width, P.hi + width):
        if moment < P.lo or moment > P.hi:
            found_slips.append((moment, _t(
                f"t = {_say(moment)} лежит вне промежутка {_say(P.lo)} ≤ t ≤ {_say(P.hi)}",
                f"t = {_say(moment)} is outside {_say(P.lo)} ≤ t ≤ {_say(P.hi)}")))
    if event == 'turn':
        for moment in _event_moments(P, 'rest'):
            found_slips.append((moment, _t(
                "здесь частица только останавливается: скорость ноль, но знак не меняется, "
                "и направление остаётся прежним",
                "the particle only stops here: the velocity is zero but keeps its sign, "
                "so the direction does not change")))
    if event in ('rest', 'turn') and P.s is not None:
        for moment in _event_moments(P, ('displacement', 0)):
            found_slips.append((moment, _t(
                "здесь частица проходит через O: ноль у перемещения, а стоит она там, где "
                "ноль у скорости",
                "the particle passes O here: the displacement is zero; it is at rest where "
                "the velocity is zero")))
    if event in ('rest', 'turn'):
        for moment in _event_moments(P, ('acceleration', 0)):
            found_slips.append((moment, _t(
                "здесь ноль у ускорения, а стоит частица там, где ноль у скорости",
                "the acceleration is zero here; the particle is at rest where the velocity is zero")))
    elif isinstance(event, tuple):
        name, level = event
        for other in ('velocity', 'acceleration', 'displacement'):
            if other == name or (other == 'displacement' and P.s is None):
                continue
            for moment in _event_moments(P, (other, level)):
                found_slips.append((moment, _t(
                    f"здесь {_quantity_words(other)} равно {_say(level)}, а вопрос про "
                    f"{_quantity_words(name)}",
                    f"here {_quantity_words(other)} equals {_say(level)}, and the question "
                    f"asks about {_quantity_words(name)}")))
        if name == 'acceleration' and sp.sympify(level) == 0:
            for moment in _event_moments(P, 'rest'):
                found_slips.append((moment, _t(
                    "здесь ноль у скорости: частица стоит, а ускорение не ноль",
                    "the velocity is zero here: the particle is at rest, and the "
                    "acceleration is not zero")))
    turned = P.in_degrees()
    if turned is not None:
        for moment in _event_moments(turned, event):
            found_slips.append((moment, _t("калькулятор в градусах: время здесь в радианах",
                                     "the calculator is in degrees: t here is in radians")))
    return found_slips


def _interval_pieces(got):
    """Промежутки ответа списком пар (начало, конец)."""
    if isinstance(got, sp.Interval):
        return [(got.start, got.end)]
    if isinstance(got, sp.Union):
        parts = [_interval_pieces(arg) for arg in got.args]
        return None if any(p is None for p in parts) else [q for p in parts for q in p]
    if isinstance(got, (list, tuple)) and all(isinstance(g, sp.Interval) for g in got):
        return [(g.start, g.end) for g in got]
    return None


@_precise
def _stretches(fn, lo, hi):
    """Куски промежутка, где величина больше нуля: пары (начало, конец)."""
    cuts = [place for place, crosses in _zeros(fn, lo, hi) if crosses]
    edges = [mp.mpf(lo)] + cuts + [mp.mpf(hi)]
    out = []
    for left, right in zip(edges, edges[1:]):
        middle = fn((left + right) / 2)
        if middle is not None and middle > 0:
            out.append((left, right))
    return out


def _same_stretches(mine, want):
    if len(mine) != len(want):
        return False
    return all(_rate_agrees(a, c) and _rate_agrees(b, d) for (a, b), (c, d) in zip(sorted(mine), want))


@_precise
def verify_while(label, got, P, what='forward'):
    """Когда перемещение растёт: `verify_while('3(b)', q, P)` — ответ `Interval(a, b)`.

    what='forward' — перемещение растёт (частица едет вперёд), 'backward' —
    убывает. Концы сверяются до трёх значащих цифр; круглые скобки или
    квадратные — всё равно: на самом конце скорость ноль.
    """
    if _blank(label, got):
        return False
    sign = 1 if what == 'forward' else -1
    want = _stretches(P.v if sign > 0 else -P.v, P.lo, P.hi)
    mine = _interval_pieces(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ — промежуток: Interval(a, b)",
                                     "the answer is an interval: Interval(a, b)"))
        return False
    if _same_stretches(mine, want):
        print(f"{OK} {label}: " + ', '.join(f"{_say(a)} < t < {_say(b)}" for a, b in mine))
        return True
    other = _stretches(-P.v if sign > 0 else P.v, P.lo, P.hi)
    rising = _stretches(P.a, P.lo, P.hi)
    if _same_stretches(mine, other):
        message = _t("это наоборот: здесь скорость отрицательна, и перемещение убывает",
                     "this is the other way round: here the velocity is negative, "
                     "and the displacement decreases")
    elif _same_stretches(mine, rising):
        message = _t("здесь растёт скорость, а перемещение растёт там, где скорость положительна",
                     "this is where the velocity increases; the displacement increases "
                     "where the velocity is positive")
    elif len(mine) != len(want):
        message = _t(f"таких кусков {len(want)}, а в ответе {len(mine)}",
                     f"there are {len(want)} such stretches, and the answer has {len(mine)}")
    else:
        message = _t("концы промежутка другие: перемещение растёт, пока скорость положительна",
                     "the ends are elsewhere: the displacement increases while the "
                     "velocity is positive")
    print(f"{NO} {label}: {message}")
    return False


@_precise
def verify_extreme(label, got, P, quantity, kind='max'):
    """Наибольшее (наименьшее) значение величины движения на всём промежутке.

    `verify_extreme('5(a)', q, P, 'speed')` — наибольший модуль скорости.
    Концы промежутка входят в сравнение: частица может быть быстрее всего в
    самом начале или в самом конце, где вершины у графика нет.
    """
    if _blank(label, got):
        return False
    source = P.quantity(quantity)
    best = _optimum(source, P.lo, P.hi, kind, P.open_lo, P.open_hi)
    place, want = best
    def slips():
        found_slips = [(place, _t(f"это момент t, а вопрос просит само значение",
                            "that is the time; the question asks for the value itself"))]
        if quantity == 'speed':
            for sign_kind in ('min', 'max'):
                found = _optimum(P.v, P.lo, P.hi, sign_kind, P.open_lo, P.open_hi)
                if found is not None and found[1] < 0:
                    found_slips.append((found[1], _t(
                        "модуль скорости не бывает отрицательным: это наименьшая скорость со знаком",
                        "speed is never negative: this is the least velocity, sign included")))
                elif found is not None:
                    found_slips.append((found[1], _t(
                        "модуль скорости — размер v без знака: самая отрицательная скорость тоже "
                        "в счёт",
                        "speed is the size of v without its sign: the most negative velocity "
                        "counts too")))
        for spot, value, what in _turning(source, P.lo, P.hi):
            if what == kind and not _rate_close(value, want):
                found_slips.append((value, _t(
                    f"это вершина графика внутри промежутка, t = {_say(spot)}; на конце "
                    f"промежутка величина {'больше' if kind == 'max' else 'меньше'}",
                    f"that is a turning point inside the interval, t = {_say(spot)}; at an end of "
                    f"the interval the value is {'larger' if kind == 'max' else 'smaller'}")))
        other = _optimum(source, P.lo, P.hi, 'min' if kind == 'max' else 'max',
                         P.open_lo, P.open_hi)
        if other is not None:
            found_slips.append((other[1], _t("это наименьшее вместо наибольшего или наоборот",
                                       "that is the smallest instead of the largest, or the other way")))
        turned = P.in_degrees()
        if turned is not None:
            found = _optimum(turned.quantity(quantity), P.lo, P.hi, kind, P.open_lo, P.open_hi)
            if found is not None:
                found_slips.append((found[1], _t("калькулятор в градусах: время здесь в радианах",
                                           "the calculator is in degrees: t here is in radians")))
        return found_slips
    word = _t('наибольшее' if kind == 'max' else 'наименьшее',
              'the largest' if kind == 'max' else 'the smallest')
    return _verdict(label, got, want, slips, fallback=_t(
        f"{word} значение на промежутке другое",
        f"{word} value on the interval is something else"))


# ================================================ скорость изменения величины

@_precise
def verify_rate(label, got, f, at, var=t, exact=False):
    """Скорость изменения величины в момент: `verify_rate('1', q, H, 13)`."""
    if _blank(label, got):
        return False
    base = _quantity_of(f, var)
    when = mp.mpf(float(sp.N(sp.sympify(at), 30)))
    want = rate_of(base, var)(when)
    def slips():
        found_slips = [(base(when), _t("это сама величина в тот момент, а не скорость её изменения",
                                 "that is the quantity itself at that moment, not its rate of change"))]
        if base.expr is not None:
            turned = _in_degrees(base.expr)
            if turned != base.expr:
                found_slips.append((rate_of(turned, var)(when), _t(
                    "калькулятор в градусах: время здесь в радианах",
                    "the calculator is in degrees: t here is in radians")))
        return found_slips
    return _verdict(label, got, want, slips, exact, fallback=_t(
        f"скорость изменения при {var} = {_say(at)} другая",
        f"the rate of change at {var} = {_say(at)} is something else"))


@_precise
def verify_duration(label, got, first, second, span, var=t):
    """Сколько времени первая величина растёт быстрее второй.

    `verify_duration('2', q, hB, hA, (0, 9))`: складываются длины всех
    кусков промежутка, где скорость роста hB больше скорости роста hA.
    """
    if _blank(label, got):
        return False
    lo, hi, _, _ = _span_of(span)
    one, two = _quantity_of(first, var), _quantity_of(second, var)
    gap = rate_of(one, var) - rate_of(two, var)
    stretches = _stretches(gap, lo, hi)
    want = sum((b - a for a, b in stretches), mp.mpf(0))
    def slips():
        found_slips = [(hi - lo - want, _t("это время, когда быстрее растёт второе",
                                     "that is the time when the other one grows faster"))]
        taller = _stretches(one - two, lo, hi)
        found_slips.append((sum((b - a for a, b in taller), mp.mpf(0)), _t(
            "здесь сравниваются высоты, а вопрос про скорости роста",
            "this compares the heights; the question compares the rates of growth")))
        if len(stretches) > 1:
            found_slips.append((stretches[0][1] - stretches[0][0], _t(
                f"это только один кусок из {len(stretches)}",
                f"that is only one of the {len(stretches)} stretches")))
        for part in (one, two):
            if part.expr is not None and _in_degrees(part.expr) != part.expr:
                turned = rate_of(_in_degrees(one.expr), var) - rate_of(_in_degrees(two.expr), var)
                found_slips.append((sum((b - a for a, b in _stretches(turned, lo, hi)), mp.mpf(0)), _t(
                    "калькулятор в градусах: время здесь в радианах",
                    "the calculator is in degrees: t here is in radians")))
                break
        return found_slips
    return _verdict(label, got, want, slips, fallback=_t(
        "всего времени выходит другое", "the total time is something else"))


# ======================================================= связанные скорости

_RATE_SYMBOLS = {}


def dt(q):
    """Скорость величины во времени: `dt(h)` — это dh/dt.

    Пишется там, где в условии стоит скорость: `rates={dt(V): 2}`,
    `rates=[Eq(dt(y), 2*dt(x))]`, `want=dt(h)`.
    """
    q = sp.sympify(q)
    if q not in _RATE_SYMBOLS:
        _RATE_SYMBOLS[q] = sp.Symbol(f"d{sp.pretty(q)}/dt")
    return _RATE_SYMBOLS[q]


def _is_rate(symbol):
    return symbol in _RATE_SYMBOLS.values()


def _of_rate(symbol):
    return next(q for q, r in _RATE_SYMBOLS.items() if r == symbol)


def _eq_list(items):
    if items is None:
        return []
    if isinstance(items, dict):
        return [sp.Eq(k, v) for k, v in items.items()]
    if isinstance(items, (sp.Equality, sp.Basic)) and not isinstance(items, (list, tuple)):
        return [items]
    return list(items)


def _expr_of(eq):
    eq = sp.sympify(eq)
    return eq.lhs - eq.rhs if isinstance(eq, sp.Equality) else eq


def _roots_1d(expr, var, lo, hi):
    fn = _quantity_of(expr, var)
    return [place for place, _ in _zeros(fn, lo, hi, 6000)]


def _instants(relations, pins, where, pin_value, beyond=False):
    """Все состояния картинки в тот момент: значения каждой величины.

    Сначала убираются определения (V = …, x = …): их величина выражается
    через остальные. Оставшееся уравнение с одной буквой решается просмотром
    её промежутка из where — так находятся все корни, а не ближайший.
    Буква, которую условие не закрепляет (где именно лодки), ставится
    произвольно: pin_value.
    Отдаёт (состояния внутри where, состояния за его краями); вторые ищутся
    только с beyond=True — они нужны лишь для того, чтобы назвать промах.
    """
    exprs = [_expr_of(e) for e in relations + pins]
    quantities = sorted(set().union(*(e.free_symbols for e in exprs)), key=str)
    where = {sp.sympify(k): v for k, v in (where or {}).items()}
    defined = []
    work = list(exprs)
    changed = True
    while changed:
        changed = False
        for expr in list(work):
            for q in sorted(expr.free_symbols, key=lambda s: (s in where, str(s))):
                # Определение — это величина, стоящая в связи одна и в первой
                # степени: V − (5πh² − πh³/3). Её выражают через остальные.
                rest, part = expr.as_independent(q, as_Add=True)
                scale = sp.cancel(part / q)
                if q in scale.free_symbols or scale == 0:
                    continue
                value = -rest / scale
                defined.append((q, value))
                work.remove(expr)
                work = [w.subs(q, value) for w in work]
                changed = True
                break
            if changed:
                break
    work = [w for w in work if w != 0]
    left = sorted(set().union(*(w.free_symbols for w in work)) if work else set(), key=str)
    inside, outside = [], []
    if len(left) == 1 and len(work) >= 1:
        q = left[0]
        lo, hi = where.get(q, (-_WIDE, _WIDE))
        lo, hi = float(sp.N(lo, 30)), float(sp.N(hi, 30))
        pad = max(10.0, hi - lo)
        found = []
        for w in work:
            found += [(r, True) for r in _roots_1d(w, q, lo, hi)]
            if beyond:
                found += [(r, False) for r in _roots_1d(w, q, lo - pad, lo)
                          + _roots_1d(w, q, hi, hi + pad)
                          if r < lo or r > hi]
        for root, ok in found:
            (inside if ok else outside).append({q: root})
    elif not left:
        inside.append({})
    else:
        raise ValueError(_t("момент задан не одним уравнением с одной буквой: упростите связи",
                            "the moment is not pinned by one equation in one letter: "
                            "simplify the relations"))
    free = [q for q in quantities if q not in left and q not in dict(defined)]

    def finish(state):
        state = dict(state)
        for q in free:
            state[q] = mp.mpf(pin_value)
        for q, value in reversed(defined):
            number = _mp_real(sp.lambdify(sorted(state, key=str), value, 'mpmath')(
                *[state[s] for s in sorted(state, key=str)]))
            state[q] = number
        return state if all(v is not None for v in state.values()) else None

    with mp.workdps(_DPS):
        inside = [s for s in (finish(s) for s in inside) if s is not None]
        outside = [s for s in (finish(s) for s in outside) if s is not None]
    return quantities, inside, outside, free


def _moving_rates(relations, rate_eqs, quantities, state):
    """Скорости всех величин, при которых связи не ломаются.

    Для каждой связи F каждая величина подталкивается на мгновение, при
    остальных на месте, и меряется, насколько F сдвинулась. Картинка может
    двигаться со скоростями r, только если сумма сдвигов, взятых с этими
    скоростями, равна нулю — иначе связь нарушилась. Эти равенства вместе
    со скоростями из условия дают систему, и она решается.
    """
    with mp.workdps(_DPS):
        names = sorted(quantities, key=str)
        rows, rhs = [], []
        for relation in relations:
            fn = sp.lambdify(names, _expr_of(relation), 'mpmath')
            row = []
            for q in names:
                step = _NUDGE * max(1, abs(state[q]))
                ahead = dict(state)
                behind = dict(state)
                ahead[q] += step
                behind[q] -= step
                change = _mp_real(fn(*[ahead[n] for n in names])) - _mp_real(fn(*[behind[n] for n in names]))
                row.append(change / (2 * step))
            rows.append(row)
            rhs.append(mp.mpf(0))
        rate_names = [dt(q) for q in names]
        for eq in rate_eqs:
            expr = _expr_of(eq)
            extra = [s for s in expr.free_symbols if s not in rate_names]
            if extra:
                expr = expr.subs({s: state[s] for s in extra if s in state})
            matrix, vector = sp.linear_eq_to_matrix([expr], rate_names)
            rows.append([mp.mpf(float(sp.N(c, 30))) for c in matrix.row(0)])
            rhs.append(mp.mpf(float(sp.N(vector[0], 30))))
        if len(rows) != len(names):
            raise ValueError(_t(
                f"скоростей {len(names)}, а условий на них {len(rows)}: связи и скорости "
                f"из условия должны закреплять их все",
                f"there are {len(names)} rates and {len(rows)} conditions on them: the relations "
                f"and the given rates must pin all of them"))
        solution = mp.lu_solve(mp.matrix(rows), mp.matrix(rhs))
        return {dt(q): solution[i] for i, q in enumerate(names)}


@_precise
def _related_value(relations, pins, rate_eqs, want, where, pin_value=1.3, beyond=False):
    quantities, inside, outside, free = _instants(relations, pins, where, pin_value, beyond)
    if len(inside) != 1:
        raise ValueError(_t(f"в тот момент подходит {len(inside)} состояний: уточните where",
                            f"{len(inside)} states fit that moment: narrow it with where="))
    rate = _moving_rates(relations, rate_eqs, quantities, inside[0])[want]
    others = []
    for state in outside:
        try:
            others.append((state, _moving_rates(relations, rate_eqs, quantities, state)[want]))
        except (ValueError, ZeroDivisionError):
            continue
    return rate, inside[0], others, free


@_precise
def verify_related(label, got, relations, at, rates, want, where=None, size=False, exact=False):
    """Связанные скорости: скорость, которая держит связь между величинами.

    relations — что верно в любой момент: `Eq(V, 5*pi*h**2 - pi*h**3/3)`.
    at — что верно в тот самый момент: `Eq(V, 200)`.
    rates — скорости из условия: `{dt(V): 2}` или `[Eq(dt(y), 2*dt(x))]`.
    want — искомая скорость: `dt(h)`.
    where — где искать состояние, если корней несколько: `{h: (0, 10)}`.
    size=True — просят «speed», размер без знака.

    Если условие не закрепляет какую-то величину (где именно лодки), проверка
    ставит её произвольно дважды и убеждается, что ответ от этого не зависит.
    """
    if _blank(label, got):
        return False
    relations, pins, rate_eqs = _eq_list(relations), _eq_list(at), _eq_list(rates)
    value, state, _, free = _related_value(relations, pins, rate_eqs, want, where)
    if free:
        again, _, _, _ = _related_value(relations, pins, rate_eqs, want, where, pin_value=4.7)
        if abs(again - value) > mp.mpf(10) ** -12 * max(1, abs(value)):
            raise ValueError(_t(f"ответ зависит от {free}: момент задан не полностью",
                                f"the answer depends on {free}: the moment is not pinned down"))
    target = _of_rate(want)
    wanted = abs(value) if size else value
    def slips():
        found_slips = []
        if size and value < 0:
            found_slips.append((value, _t("просят размер скорости, speed: без знака",
                                    "the question asks for a speed: a size, without the sign")))
        if not size and value < 0:
            found_slips.append((-value, _t(
                f"{target} уменьшается, и скорость её изменения отрицательна: знак — часть ответа",
                f"{target} is decreasing, so its rate of change is negative: the sign is part "
                f"of the answer")))
        known = [e for e in rate_eqs if isinstance(e, sp.Equality) and _is_rate(e.lhs)
                 and not (e.rhs.free_symbols) and e.rhs != 0]
        if len(known) == 1:
            given = known[0].lhs
            speed = sp.N(known[0].rhs, 30)
            unit = [sp.Eq(given, sp.sign(speed))] + [e for e in rate_eqs if e is not known[0]]
            per_unit, _, _, _ = _related_value(relations, pins, unit, want, where)
            source = _of_rate(given)
            if abs(speed) != 1:
                found_slips.append((abs(per_unit) if size else per_unit, _t(
                    f"это d{target}/d{source}: на сколько меняется {target} на единицу {source}. "
                    f"Вопрос про время — умножьте на d{source}/dt",
                    f"that is d{target}/d{source}, the change in {target} per unit of {source}. "
                    f"The question is per unit of time: multiply by d{source}/dt")))
                if per_unit != 0:
                    flipped = float(speed) ** 2 / value
                    found_slips.append((abs(flipped) if size else flipped, _t(
                        f"цепочка перевёрнута: d{target}/dt = d{target}/d{source} · d{source}/dt, "
                        f"а d{target}/d{source} = 1 / (d{source}/d{target})",
                        f"the chain is upside down: d{target}/dt = d{target}/d{source} · "
                        f"d{source}/dt, and d{target}/d{source} = 1 / (d{source}/d{target})")))
        others = _related_value(relations, pins, rate_eqs, want, where, beyond=True)[2]
        for other_state, other in others:
            spot = ', '.join(f"{q} = {_say(v)}" for q, v in other_state.items()
                             if q not in free and where and q in {sp.sympify(k) for k in where})
            found_slips.append((abs(other) if size else other, _t(
                f"это в другом состоянии ({spot}), которое условие не допускает",
                f"that is at another state ({spot}), which the question does not allow")))
        return found_slips
    return _verdict(label, got, wanted, slips, exact, fallback=_t(
        "с такой скоростью связь между величинами не держится",
        "at that rate the relation between the quantities does not hold"))


# ================================================================ наилучшее

def _domain_of(domain):
    if isinstance(domain, sp.Interval):
        return domain.start, domain.end, bool(domain.left_open), bool(domain.right_open)
    lo, hi = domain
    return lo, hi, False, False


def _letter_sets(params):
    if not params:
        return [{}]
    count = len(next(iter(params.values())))
    return [{k: sp.sympify(v[i]) for k, v in params.items()} for i in range(count)]


def _report_value(report, place, value, var, run):
    """Что просит вопрос: само значение, место или величину в этом месте."""
    if report == 'value':
        return value
    if report == 'place':
        return place
    expr = sp.sympify(report).subs(run)
    fn = _quantity_of(expr, var)
    return fn(place)


def verify_best(label, got, f, domain, kind='max', var=x, report='value', integer=False,
                exact=False, params=None):
    """Наилучшее: `verify_best('10', q, A, Interval.open(0, 3), 'max', report=-sqrt(9 - x**2))`.

    f — величина, которую делают наибольшей (kind='max') или наименьшей, как
    выражение от var или `rate_of(...)`. domain — отрезок `(a, b)` или
    `Interval` с открытыми концами. report — что просит вопрос: 'value' (само
    наибольшее значение), 'place' (при каком var), выражение от var (другая
    величина в том месте) или кортеж из них. integer=True — var считает
    предметы и бывает только целым. params — буквы задачи и несколько их
    наборов: ответ с буквами сверяется на каждом.
    """
    if _blank(label, got):
        return False
    reports = report if isinstance(report, tuple) else (report,)
    answers = got if isinstance(report, tuple) else (got,)
    if isinstance(report, tuple) and (not isinstance(got, (tuple, list)) or len(got) != len(report)):
        print(f"{NO} {label}: " + _t(f"ответ — {len(report)} числа в скобках",
                                     f"the answer is {len(report)} numbers in brackets"))
        return False
    if _exact_refusal(label, got if not isinstance(got, (tuple, list)) else sp.Tuple(*got), exact):
        return False
    for piece, what in zip(answers, reports):
        verdict = _best_piece(label, piece, what, f, domain, kind, var, integer, exact, params)
        if verdict is not True:
            print(f"{NO} {label}: {verdict}")
            return False
    shown = ', '.join(str(a) if not _is_decimal(a) else _say(a) for a in answers)
    print(f"{OK} {label}: {shown}")
    return True


@_precise
def _best_piece(label, got, report, f, domain, kind, var, integer, exact, params):
    """Один ответ из кортежа: True или текст промаха."""
    lo, hi, open_lo, open_hi = _domain_of(domain)
    word = _t('наибольшее' if kind == 'max' else 'наименьшее',
              'the largest' if kind == 'max' else 'the smallest')
    cases = []
    for run in _letter_sets(params):
        body = f if isinstance(f, _Measured) else sp.sympify(f).subs(run)
        fn = _quantity_of(body, var)
        a = float(sp.N(sp.sympify(lo).subs(run), 30))
        b = float(sp.N(sp.sympify(hi).subs(run), 30))
        found = _optimum(fn, a, b, kind, open_lo, open_hi, integer)
        if found is None:
            raise ValueError("verify_best: no best value on this domain — no turning point "
                             "inside and no closed end")
        place, value = found
        try:
            mine = sp.sympify(got).subs(run) if params else got
        except (sp.SympifyError, TypeError):
            return _t("ответ — число или выражение", "the answer is a number or an expression")
        if _rate_number(mine) is None:
            return _t("ответ — число" if not params else "ответ — выражение с буквами задачи",
                      "the answer is a number" if not params
                      else "the answer is an expression in the letters of the question")
        cases.append((run, fn, a, b, place, value,
                      _report_value(report, place, value, var, run), mine))
    if all(_rate_agrees(mine, want, exact) for *_, want, mine in cases):
        return True
    # Промахи ищутся на первом наборе букв: им одного и хватает, чтобы назвать ход.
    run, fn, a, b, place, value, want, mine = cases[0]
    for there, message in _best_slips(report, fn, a, b, open_lo, open_hi, kind, var, run,
                                      integer, place, value, word):
        if there is not None and _rate_close(mine, there) and not _rate_close(mine, want):
            return message
    if all(_rate_close(-_rate_number(mine), want) for *_, want, mine in cases):
        return _t("знак не тот", "the sign is wrong")
    if all(_two_figures(mine, want) for *_, want, mine in cases):
        return _t("нужно три значащие цифры", "give three significant figures")
    return _t(f"{word} выходит в другом месте или другим",
              f"{word} value is elsewhere, or it is something else")


def _best_slips(report, fn, a, b, open_lo, open_hi, kind, var, run, integer, place, value, word):
    """Что путают с наилучшим: место и значение, квадрат, другая вершина, конец, целое."""
    if report != 'place':
        yield place, _t(f"это значение {var} в лучшей точке, а вопрос просит другое",
                        f"that is the value of {var} at the best point; the "
                        f"question asks for something else")
    if report != 'value':
        yield value, _t(f"это {word} значение самой величины, а вопрос просит другое",
                        f"that is {word} value of the quantity itself; the question "
                        f"asks for something else")
    if report == 'value' and value is not None:
        yield value ** 2, _t("это квадрат: корень не извлечён",
                             "that is the square: the root is missing")
        if value >= 0:
            yield mp.sqrt(value), _t("из ответа лишний раз извлечён корень",
                                     "an extra square root was taken")
    if integer:
        smooth = _optimum(fn, a, b, kind, open_lo, open_hi, False)
        if smooth is not None:
            yield _report_value(report, smooth[0], smooth[1], var, run), _t(
                f"{var} считает предметы и бывает только целым: сравните целые по обе "
                f"стороны от вершины",
                f"{var} counts things, so it is a whole number: compare the whole numbers "
                f"on either side of the vertex")
    for end, is_open in ((a, open_lo), (b, open_hi)):
        if is_open and report == 'place':
            yield mp.mpf(end), _t(
                f"{var} = {_say(end)} в область не входит: промежуток там открыт",
                f"{var} = {_say(end)} is not in the domain: the interval is open there")
        if abs(end - place) > 1e-9 and fn(end) is not None:
            yield _report_value(report, mp.mpf(end), fn(end), var, run), _t(
                f"это на конце {var} = {_say(end)}, а {word} значение не там",
                f"that is at the end {var} = {_say(end)}, and {word} value is not there")
    other = _optimum(fn, a, b, 'min' if kind == 'max' else 'max', open_lo, open_hi, integer)
    if other is not None:
        yield _report_value(report, other[0], other[1], var, run), _t(
            "это наименьшее вместо наибольшего или наоборот",
            "that is the smallest instead of the largest, or the other way")
    width = b - a
    for spot, height, what in _turning(fn, a - _WIDE - width, b + _WIDE + width, 8000):
        inside = (a < spot < b) or (not open_lo and spot == a) or (not open_hi and spot == b)
        if abs(spot - place) < 1e-9 * max(1, abs(place)):
            continue
        there = _report_value(report, spot, height, var, run)
        if not inside:
            yield there, _t(
                f"это в точке {var} = {_say(spot)}, а она вне области из условия",
                f"that is at {var} = {_say(spot)}, which is outside the domain in the question")
        else:
            yield there, _t(
                f"это в другой вершине, {var} = {_say(spot)}: {word} значение не там",
                f"that is at the other turning point, {var} = {_say(spot)}: "
                f"{word} value is not there")


@_precise
def verify_fits(label, got, f, domain, size, var=x):
    """Пройдёт ли предмет длины size: 'yes' или 'no'.

    Шест проносят за угол, если он не длиннее самого короткого отрезка AB,
    касающегося угла, — наименьшего значения f на области. Проверка находит
    это наименьшее сама.
    """
    if _blank(label, got):
        return False
    word = str(got).strip().lower()
    if word not in ('yes', 'no'):
        print(f"{NO} {label}: " + _t("ответ — 'yes' или 'no'", "the answer is 'yes' or 'no'"))
        return False
    lo, hi, open_lo, open_hi = _domain_of(domain)
    fn = _quantity_of(f, var)
    found = _optimum(fn, float(sp.N(lo, 30)), float(sp.N(hi, 30)), 'min', open_lo, open_hi)
    passes = float(sp.N(sp.sympify(size), 30)) <= found[1]
    want = 'yes' if passes else 'no'
    if word == want:
        print(f"{OK} {label}: {word}")
        return True
    print(f"{NO} {label}: " + _t(
        "за угол проходит только то, что не длиннее самого короткого отрезка через угол: "
        "сравните длину с наименьшим значением",
        "only something no longer than the shortest segment through the corner gets past it: "
        "compare the length with the smallest value"))
    return False
