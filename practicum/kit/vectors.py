"""Векторы (C5): точка — там, где выполнены условия; прямая — множество точек.
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .functions import _scan_roots
from .distribution import _draw_agree


# ================================================================= векторы
# Двадцать четвёртое понятие равенства ответов: прямая — множество точек, а
# точка — там, где выполнены условия вопроса.
#
# Уравнение прямой не сверяется с записью. r = (1, −2, 0) + λ(2, 3, 1) и
# r = (5, 4, 2) + μ(−4, −6, −2) — одна прямая, и проверка принимает любую
# точку прямой с любым параллельным ей направлением. Точка пересечения —
# точка, лежащая на обеих прямых; угол между прямыми — угол между их
# направлениями, острый.
#
# Искомое, которое задают словами, — «D, противоположная B в параллелограмме
# ABCD», «q ⟂ a и |q| = 15», «при каких a прямые перпендикулярны и
# пересекаются», — проверка находит сама из условий, записанных как в
# билете: parallelogram(A, B, C, D), perpendicular(q, a), meet(L1, L2).
# Решает их sympy, все решения сразу, и отбрасывает те, что нарушают
# ограничения вопроса (x, y > 0; C ≠ A). Неверный ответ подставляется в те
# же условия по одному, и первое нарушенное называется словами.

z = sp.Symbol('z')
lam, mu = sp.symbols('lambda mu')

_VEC_RUNS = 3            # сколько наборов значений пробуется для свободных букв
_VEC_LOOSE = 5e-4        # допуск для ответа с десятичными дробями: три цифры
_VEC_SCAN = (-60, 60)    # где искать корни, если sympy уравнение не решил


def _is_sequence(value):
    return isinstance(value, (list, tuple, sp.Tuple)) or (
        isinstance(value, sp.MatrixBase) and 1 in value.shape)


def vec(*components, name=None):
    """Вектор-столбец или точка: `vec(1, -4, 0)`. `name` — буква для сообщений."""
    if len(components) == 1 and _is_sequence(components[0]):
        components = tuple(components[0])
    out = sp.Matrix([sp.sympify(c) for c in components])
    if name:
        out._vec_name = name
    return out


def _as_vec(value):
    """Ответ-вектор — в столбец sympy; не вектор — None."""
    if isinstance(value, _Line):
        return None
    if isinstance(value, sp.MatrixBase):
        return sp.Matrix(list(value)) if 1 in value.shape else None
    if isinstance(value, (list, tuple, sp.Tuple)):
        try:
            return sp.Matrix([sp.sympify(v) for v in value])
        except (sp.SympifyError, TypeError):
            return None
    return None


def _has_float(value):
    if isinstance(value, _Line):
        return _has_float(value.point) or _has_float(value.direction)
    vector = _as_vec(value)
    if vector is not None:
        return any(sp.sympify(c).has(sp.Float) for c in vector)
    if isinstance(value, (list, tuple, set)):
        return any(_has_float(v) for v in value)
    try:
        return sp.sympify(value).has(sp.Float)
    except (sp.SympifyError, TypeError):
        return False


_GREEK = {'lambda': 'λ', 'mu': 'μ', 'gamma': 'γ', 'theta': 'θ', 'alpha': 'α', 'beta': 'β'}


def _plain(expr):
    """Искомые печатаются своими буквами: Cx, а не _Cx; lambda — λ."""
    swap = {s: sp.Symbol(_GREEK.get(s.name, s.name)) for s in expr.free_symbols
            if isinstance(s, sp.Dummy) or s.name in _GREEK}
    return sp.sstr(expr.xreplace(swap)) if swap else sp.sstr(expr)


def _text(value):
    """Число или вектор для сообщения: короткое точное — как есть, длинное — 4 цифры."""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, sp.Symbol):
        return _plain(value)
    if isinstance(value, list):
        return '[' + ', '.join(_text(c) for c in value) + ']'
    vector = _as_vec(value)
    if vector is not None:
        names = [c.name for c in vector if isinstance(c, sp.Dummy)]
        if len(names) == len(vector) and len({n[:-1] for n in names}) == 1:
            return names[0][:-1]
        return '(' + ', '.join(_text(c) for c in vector) + ')'
    try:
        expr = sp.sympify(value)
    except (sp.SympifyError, TypeError):
        return str(value)
    if expr.free_symbols or not expr.is_number:
        return _plain(expr)
    plain = sp.sstr(expr)
    if expr.has(sp.Float) or expr.atoms(sp.Function) or len(plain) > 20:
        number = _vec_number(expr)
        return sig(number, 4) if number is not None else plain
    return plain


def _vec_number(value):
    """Действительное число или None."""
    try:
        c = complex(sp.N(sp.sympify(value), 30))
    except (TypeError, ValueError, sp.SympifyError):
        return None
    if not (math.isfinite(c.real) and math.isfinite(c.imag)):
        return None
    if abs(c.imag) > 1e-9 * max(1.0, abs(c.real)):
        return None
    return c.real


def _scale(*vectors):
    return max([1.0] + [abs(_vec_number(c) or 0.0) for v in vectors for c in v])


# ---------------------------------------------------------------- действия

def _direction(item):
    return item.direction if isinstance(item, _Line) else _as_vec(item)


def dot(u, v):
    """Скалярное произведение: `dot(a, c)`. Прямые дают свои направления."""
    one, two = _direction(u), _direction(v)
    if one is None or two is None or len(one) != len(two):
        raise ValueError('dot: two vectors of the same size')
    return sum((p * q for p, q in zip(one, two)), sp.Integer(0))


def mag(v):
    """Длина вектора: `mag(vec(3, -4))` — 5."""
    return sp.sqrt(dot(v, v))


def distance(A, B):
    """Расстояние между точками — длина AB."""
    return mag(_as_vec(B) - _as_vec(A))


def angle(u, v):
    """Угол между векторами, от 0 до π. Между прямыми — острый."""
    acute = isinstance(u, _Line) or isinstance(v, _Line)
    one, two = _direction(u), _direction(v)
    cosine = dot(one, two) / (mag(one) * mag(two))
    return sp.acos(sp.Abs(cosine) if acute else cosine)


def _time(r, var):
    """Буква времени: названная, а если её в движении нет — единственная буква движения.

    В архиве t переопределяют с условием positive, и t из kit с ним уже не
    совпадает: производная по «чужому» t была бы нулём.
    """
    letters = _as_vec(r).free_symbols
    if var in letters or len(letters) != 1:
        return var
    return next(iter(letters))


def velocity(r, var=t):
    """Скорость движения r(t): производная положения по времени."""
    return _as_vec(r).diff(_time(r, var))


# ----------------------------------------------------------------- прямые

class _Line:
    """Прямая r = point + param·direction."""

    def __init__(self, point, direction, param=None, name=None):
        self.point = sp.Matrix(point)
        self.direction = sp.Matrix(direction)
        self.param = param if param is not None else lam
        self.name = name

    @property
    def letters(self):
        return self.point.free_symbols | self.direction.free_symbols

    def at(self, value):
        return self.point + value * self.direction

    def subs(self, run):
        if not run:
            return self
        return _Line(self.point.subs(run), self.direction.subs(run), self.param, self.name)

    def __repr__(self):
        return f"r = {_text(self.point)} + {_text(self.param)}{_text(self.direction)}"


def _parse_line(expr, param=None, exclude=()):
    """r = a + λb из выражения: параметр входит в первой степени, и он один."""
    vector = _as_vec(expr)
    if vector is None:
        return None
    if param is None:
        candidates = [s for s in vector.free_symbols if s not in exclude]
        linear = [s for s in candidates
                  if all(sp.diff(c, s, 2) == 0 for c in vector)
                  and any(sp.diff(c, s) != 0 for c in vector)]
        if len(linear) != 1 or len(candidates) != 1:
            return None
        param = linear[0]
    if any(sp.simplify(sp.diff(c, param, 2)) != 0 for c in vector):
        return None
    direction = vector.diff(param)
    if direction.has(param):
        return None
    return _Line(vector.subs(param, 0), direction, param)


def line(first, second=None, name=None):
    """Прямая, как её пишет вопрос.

    `line(vec(1, 2, -3) + s*vec(2, 3, 6))` — параметр найдётся сам, если буква
    одна; иначе его называют: `line(vec(0, 1, 2) + t*vec(a, 1, -1), t)`.
    `line(point, direction)` — точка и направление порознь.
    """
    if second is not None and _as_vec(second) is not None:
        return _Line(_as_vec(first), _as_vec(second), lam, name)
    parsed = _parse_line(first, second)
    if parsed is None:
        raise ValueError("line: write it as vec(point) + parameter*vec(direction)")
    parsed.name = name
    return parsed


def through(A, B, name=None):
    """Прямая через две точки."""
    one, two = _as_vec(A), _as_vec(B)
    return _Line(one, two - one, lam, name)


def cartesian(*parts, name=None):
    """Прямая в декартовой форме: (x + 1)/2 = y = 3 − z — `cartesian((x + 1)/2, y, 3 - z)`."""
    axes = (x, y, z)[:len(parts)]
    if len(parts) not in (2, 3):
        raise ValueError('cartesian: two or three equal parts')
    point, direction = [], []
    for part, axis in zip(parts, axes):
        part = sp.sympify(part)
        others = part.free_symbols & (set((x, y, z)) - {axis})
        if others or sp.diff(part, axis, 2) != 0 or sp.diff(part, axis) == 0:
            raise ValueError(f'cartesian: each part is linear in its own coordinate ({axis})')
        value = sp.solve(sp.Eq(part, lam), axis)[0]
        point.append(value.subs(lam, 0))
        direction.append(sp.diff(value, lam))
    return _Line(point, direction, lam, name)


# ------------------------------------------------------ сравнения векторов

def _exact_zero(expression):
    """Точный ноль, если его видно без чисел с плавающей точкой; иначе None."""
    value = sp.expand(sp.sympify(expression))
    if value == 0:
        return True
    if value.is_Rational:
        return False
    return None


def _parallel(u, v, loose=False):
    """u ∥ v: |u|²|v|² − (u·v)² ноль относительно |u|²|v|²."""
    uu, vv, uv = dot(u, u), dot(v, v), dot(u, v)
    if not loose and _exact_zero(uu) is not True and _exact_zero(vv) is not True:
        exact = _exact_zero(uu * vv - uv * uv)
        if exact is not None:
            return exact
    uu, vv, uv = (_vec_number(sp.N(value, 40)) for value in (uu, vv, uv))
    if None in (uu, vv, uv) or uu == 0 or vv == 0:
        return False
    return abs(uu * vv - uv * uv) <= (1e-6 if loose else 1e-12) * uu * vv


def _on(P, L, loose=False):
    """Точка на прямой: расстояние до неё ноль относительно масштаба."""
    w = _as_vec(P) - L.point
    if not loose:
        exact = _exact_zero(dot(w, w) * dot(L.direction, L.direction) - dot(w, L.direction) ** 2)
        if exact is not None and _exact_zero(dot(L.direction, L.direction)) is False:
            return exact
    ww, wd, dd = _vec_number(dot(w, w)), _vec_number(dot(w, L.direction)), _vec_number(dot(L.direction, L.direction))
    if None in (ww, wd, dd) or dd == 0:
        return False
    far = max(0.0, ww - wd * wd / dd)
    scale = _scale(_as_vec(P), L.point)
    return math.sqrt(far) <= (_VEC_LOOSE if loose else 1e-9) * scale


def _vec_agree(got, want, exact=False):
    """Два числа сходятся: точно, или до трёх значащих цифр у десятичной дроби."""
    one, two = _vec_number(got), _vec_number(want)
    if one is None or two is None:
        return False
    if abs(one - two) <= 1e-9 * max(1.0, abs(two)):
        return True
    # 108 за 107.703 — те же три цифры, записанные целым числом
    return not exact and _draw_agree(one, two)


def _agree_vec(got, want, exact=False):
    one, two = _as_vec(got), _as_vec(want)
    if one is None or two is None or len(one) != len(two):
        return False
    return all(_vec_agree(p, q, exact) for p, q in zip(one, two))


def _vec_same(got, want, exact=False):
    if _as_vec(want) is not None:
        return _agree_vec(got, want, exact)
    if _as_vec(got) is not None:
        return False
    return _vec_agree(got, want, exact)


def _subs(value, run):
    if not run:
        return value
    if isinstance(value, _Line):
        return value.subs(run)
    vector = _as_vec(value)
    if vector is not None:
        return vector.subs(run)
    if isinstance(value, (list, tuple)):
        return [_subs(v, run) for v in value]
    try:
        return sp.sympify(value).subs(run)
    except (sp.SympifyError, TypeError):
        return value


def _letters_of(*items):
    out = set()
    for item in items:
        if isinstance(item, _Line):
            out |= item.letters
        elif isinstance(item, _Fact):
            out |= item.letters
        elif isinstance(item, (list, tuple, set)):
            out |= _letters_of(*item)
        elif isinstance(item, sp.MatrixBase):
            out |= item.free_symbols
        else:
            try:
                out |= sp.sympify(item).free_symbols
            except (sp.SympifyError, TypeError):
                pass
    return out


def _vec_sample(letter, index):
    """Значение свободной буквы: целые — целыми, положительные — положительными."""
    if letter.is_integer:
        return sp.Integer([1, 2, 5, 3][index % 4])
    if letter.is_positive:
        return [sp.Rational(7, 5), sp.Rational(13, 4), sp.Rational(5, 7)][index % 3]
    return [sp.Rational(7, 5), sp.Rational(-3, 2), sp.Rational(11, 3)][index % 3]


def _vec_runs(letters, free=None):
    """Наборы значений свободных букв: один пустой, если букв нет."""
    if isinstance(free, (list, tuple)) and free and isinstance(free[0], dict):
        return [dict(run) for run in free]
    letters = sorted(letters, key=str)
    if not letters:
        return [{}]
    return [{letter: _vec_sample(letter, i + j) for j, letter in enumerate(letters)}
            for i in range(_VEC_RUNS)]


def _at_words(run):
    if not run:
        return ''
    shown = ', '.join(f"{_text(name)} = {_text(value)}" for name, value in run.items())
    return _t(f" (при {shown})", f" (at {shown})")


# ============================================================ ответ-прямая

def _one_sign(mine, theirs):
    """Направление станет параллельным, если сменить знак одной компоненты."""
    for i in range(len(mine)):
        flipped = sp.Matrix(mine)
        flipped[i] = -flipped[i]
        if flipped[i] != 0 and _parallel(flipped, theirs):
            return i
    return None


def _line_slip(mine, theirs, loose):
    par = _parallel(mine.direction, theirs.direction, loose)
    on = _on(mine.point, theirs, loose)
    if not par and _parallel(mine.point, theirs.direction, loose) and _on(mine.direction, theirs, loose):
        return _t("точка и направление поменялись местами: точка прямой стоит "
                  "там, где направление, и наоборот",
                  "the point and the direction are swapped: a point of the line "
                  "stands where the direction should be, and the other way round")
    if par:
        if _on(-mine.point, theirs, loose):
            return _t(f"точка {_text(mine.point)} взята с обратными знаками: в (x − 1)/2 "
                      f"у точки x = 1, а не −1",
                      f"the point {_text(mine.point)} has the wrong signs: in (x − 1)/2 "
                      f"the point has x = 1, not −1")
        return _t(f"направление верное, но точка {_text(mine.point)} на прямой не лежит: "
                  f"это параллельная прямая",
                  f"the direction is right, but the point {_text(mine.point)} is not on "
                  f"the line: this is a parallel line")
    if on:
        if _on(mine.direction, theirs, loose):
            return _t(f"направление {_text(mine.direction)} — радиус-вектор точки прямой, "
                      f"а не шаг вдоль неё: направление — разность двух точек",
                      f"the direction {_text(mine.direction)} is the position vector of a "
                      f"point on the line, not a step along it: the direction is the "
                      f"difference of two points")
        flipped = _one_sign(mine.direction, theirs.direction)
        if flipped is not None:
            axis = 'xyz'[flipped] if len(mine.direction) <= 3 else str(flipped + 1)
            return _t(f"у направления неверный знак компоненты {axis}: в 3 − z "
                      f"коэффициент при z равен −1",
                      f"the {axis}-component of the direction has the wrong sign: "
                      f"in 3 − z the coefficient of z is −1")
        return _t(f"точка {_text(mine.point)} на прямой, но направление "
                  f"{_text(mine.direction)} идёт не вдоль неё",
                  f"the point {_text(mine.point)} is on the line, but the direction "
                  f"{_text(mine.direction)} does not run along it")
    return _t(f"ни точка {_text(mine.point)} не лежит на прямой, ни направление "
              f"{_text(mine.direction)} не идёт вдоль неё",
              f"the point {_text(mine.point)} is not on the line, and the direction "
              f"{_text(mine.direction)} does not run along it")


def verify_line(label, got, L, free=None):
    """Ответ — уравнение прямой: `vec(-1, 0, 3) + lam*vec(2, 1, -1)`.

    Прямая — множество точек, поэтому годится любая её точка и любое
    параллельное ей направление, с любым именем параметра. Проверка знает
    прямую так, как её дал вопрос: `cartesian((x + 1)/2, y, 3 - z)`,
    `through(A, B)`, `line(P, d)`. Неверный ответ получает имя промаха:
    параллельная прямая, радиус-вектор вместо направления, точка и
    направление местами, знак из декартовой формы.
    """
    if _blank(label, got):
        return False
    letters = L.letters
    parsed = got if isinstance(got, _Line) else _parse_line(got, exclude=letters)
    if parsed is None:
        print(f"{NO} {label}: " + _t(
            "прямую пишут r = a + λb: точка плюс один параметр, умноженный на "
            "направление, — vec(1, 2, 0) + lam*vec(3, -1, 2)",
            "a line is written r = a + λb: a point plus one parameter times a "
            "direction — vec(1, 2, 0) + lam*vec(3, -1, 2)"))
        return False
    if len(parsed.point) != len(L.point):
        print(f"{NO} {label}: " + _t(
            f"у прямой {len(L.point)} координаты, а в ответе {len(parsed.point)}",
            f"the line has {len(L.point)} coordinates, and the answer has {len(parsed.point)}"))
        return False
    if all(sp.simplify(c) == 0 for c in parsed.direction):
        print(f"{NO} {label}: " + _t(
            "направление — нулевой вектор: это одна точка, а не прямая",
            "the direction is the zero vector: that is a single point, not a line"))
        return False
    loose = _has_float(parsed)
    for run in _vec_runs(letters | (parsed.letters - {parsed.param}), free):
        mine, theirs = parsed.subs(run), L.subs(run)
        if _parallel(mine.direction, theirs.direction, loose) and _on(mine.point, theirs, loose):
            continue
        print(f"{NO} {label}: " + _line_slip(mine, theirs, loose) + _at_words(run))
        return False
    print(f"{OK} {label}: r = {_text(parsed.point)} + {_text(parsed.param)}{_text(parsed.direction)}")
    return True


# ===================================================== пересечение прямых

def _meet_params(one, two):
    """Параметры общей точки: (s, t), 'many' для одной прямой или None."""
    s, u = sp.Dummy('s'), sp.Dummy('u')
    equations = list(one.at(s) - two.at(u))
    found = sp.linsolve(equations, [s, u])
    if found == sp.EmptySet or not found:
        return None
    pair = next(iter(found))
    if any(value.has(s) or value.has(u) for value in pair):
        return 'many'
    return pair


def _relation(one, two):
    if _parallel(one.direction, two.direction):
        return 'same' if _on(one.point, two) else 'parallel'
    return 'skew' if _meet_params(one, two) is None else 'intersecting'


def _vec_line(item):
    """Прямая из вопроса или из ответа ученика."""
    return item if isinstance(item, _Line) else _parse_line(item)


def _two_params(L1, L2):
    one, two = _text(L1.param), _text(L2.param)
    return (one, two) if one != two else (one, 'μ' if one != 'μ' else 'λ')


def verify_meet(label, got, L1, L2, free=None):
    """Ответ — точка пересечения двух прямых: `(5, 4, 2)` или `vec(5, 4, 2)`.

    Проверка находит её сама, решая L1 = L2 с разными параметрами. Неверный
    ответ разбирается по прямым: лежит на одной, но не на другой; значение
    параметра одной прямой подставлено в другую; вместо точки — сами
    параметры. `free` — буква, через которую выражен ответ («A через a»):
    проверка пробует несколько её значений.
    """
    if _blank(label, got):
        return False
    letters = L1.letters | L2.letters
    for run in _vec_runs(letters, free):
        one, two = L1.subs(run), L2.subs(run)
        where = _meet_params(one, two)
        if where is None or where == 'many':
            print(f"{NO} {label}: " + _t(
                "у этих прямых нет единственной общей точки",
                "these lines have no single common point") + _at_words(run))
            return False
        s, u = where
        point = one.at(s)
        mine = _as_vec(_subs(got, run))
        if mine is None:
            print(f"{NO} {label}: " + _t("ответ — точка: (x, y, z)",
                                         "the answer is a point: (x, y, z)"))
            return False
        exact = not _has_float(got)
        if len(mine) != len(point):
            if len(mine) == 2 and _vec_agree(mine[0], s) and _vec_agree(mine[1], u):
                p1, p2 = _two_params(one, two)
                print(f"{NO} {label}: " + _t(
                    f"это значения параметров, {p1} = {_text(s)} и {p2} = "
                    f"{_text(u)}; вопрос спрашивает саму точку — подставьте одно из них "
                    f"в свою прямую",
                    f"those are the parameters, {p1} = {_text(s)} and {p2} = "
                    f"{_text(u)}; the question asks for the point — put one of them into "
                    f"its own line"))
            else:
                print(f"{NO} {label}: " + _t(
                    f"у точки {len(point)} координаты", f"the point has {len(point)} coordinates"))
            return False
        if _agree_vec(mine, point, exact):
            continue
        loose = not exact
        if _agree_vec(mine, two.at(s), exact) or _agree_vec(mine, one.at(u), exact):
            message = _t(
                "значение параметра одной прямой подставлено в другую: у каждой прямой "
                "свой параметр, и подставляют его в ту прямую, которой он принадлежит",
                "the parameter of one line has been put into the other: each line has "
                "its own parameter, and it goes into the line it belongs to")
        elif _on(mine, one, loose) and not _on(mine, two, loose):
            message = _t(f"{_text(mine)} лежит на первой прямой, но не на второй: "
                         f"проверьте все три компоненты",
                         f"{_text(mine)} is on the first line, but not on the second: "
                         f"check all three components")
        elif _on(mine, two, loose) and not _on(mine, one, loose):
            message = _t(f"{_text(mine)} лежит на второй прямой, но не на первой: "
                         f"проверьте все три компоненты",
                         f"{_text(mine)} is on the second line, but not on the first: "
                         f"check all three components")
        else:
            message = _t(f"{_text(mine)} не лежит ни на одной из прямых",
                         f"{_text(mine)} is on neither line")
        print(f"{NO} {label}: " + message + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


_RELATION_WORDS = {
    'parallel': 'parallel', 'skew': 'skew',
    'intersect': 'intersecting', 'intersecting': 'intersecting', 'meet': 'intersecting',
    'same': 'same', 'coincident': 'same', 'identical': 'same',
}


def verify_relation(label, got, L1, L2):
    """Ответ — слово: 'parallel', 'intersecting', 'skew' или 'same'.

    Проверка сама смотрит на направления и решает систему. Неверное слово
    получает причину: направления кратны или нет, какие значения параметров
    дали две компоненты и что стало с третьей.
    """
    if _blank(label, got):
        return False
    word = _RELATION_WORDS.get(str(got).strip().strip("'\"").lower())
    if word is None:
        print(f"{NO} {label}: " + _t(
            "ответ — одно слово: 'parallel', 'intersecting', 'skew' или 'same'",
            "the answer is one word: 'parallel', 'intersecting', 'skew' or 'same'"))
        return False
    truth = _relation(L1, L2)
    if word == truth:
        print(f"{OK} {label}: {word}")
        return True
    d1, d2 = _text(L1.direction), _text(L2.direction)
    if truth == 'parallel':
        message = _t(f"направления {d1} и {d2} кратны: прямые параллельны. "
                     f"Параллельные прямые не пересекаются, но и не скрещиваются — "
                     f"скрещиваются только непараллельные",
                     f"the directions {d1} and {d2} are multiples: the lines are parallel. "
                     f"Parallel lines never meet, but they are not skew — skew lines are "
                     f"not parallel") if word in ('skew', 'intersecting') else \
            _t("точка первой прямой не лежит на второй: прямые разные",
               "a point of the first line is not on the second: the lines are different")
    elif truth == 'same':
        message = _t("точка первой прямой лежит и на второй, а направления кратны: "
                     "это одна прямая",
                     "a point of the first line is also on the second, and the directions "
                     "are multiples: it is one line")
    elif word in ('parallel', 'same'):
        message = _t(f"направления {d1} и {d2} не кратны друг другу",
                     f"the directions {d1} and {d2} are not multiples of each other")
    elif truth == 'skew':
        s, u = sp.Dummy('s'), sp.Dummy('u')
        gap = list(L1.at(s) - L2.at(u))
        pair = sp.solve(gap[:2], [s, u], dict=True)
        if pair:
            p1, p2 = _two_params(L1, L2)
            one, two = L1.at(pair[0][s])[2], L2.at(pair[0][u])[2]
            message = _t(f"первые две компоненты дают {p1} = {_text(pair[0][s])}, "
                         f"{p2} = {_text(pair[0][u])}, а третья при них не сходится "
                         f"({_text(one)} ≠ {_text(two)}): общей точки нет",
                         f"the first two components give {p1} = {_text(pair[0][s])}, "
                         f"{p2} = {_text(pair[0][u])}, and the third does not hold for "
                         f"them ({_text(one)} ≠ {_text(two)}): there is no common point")
        else:
            message = _t("общей точки у прямых нет", "the lines have no common point")
    else:
        s, u = _meet_params(L1, L2)
        message = _t(f"прямые пересекаются в {_text(L1.at(s))}",
                     f"the lines meet at {_text(L1.at(s))}")
    print(f"{NO} {label}: {message}")
    return False


def verify_pair(label, got, L1, L2):
    """Ответ — значения двух параметров из двух уравнений по компонентам.

    Так начинается «show that the lines are skew»: две компоненты решают
    вместе, третью проверяют. Годится любая пара компонент; проверка
    говорит, выполнилась ли при найденных значениях третья.
    """
    if _blank(label, got, L1, L2):
        return False
    L1, L2 = _vec_line(L1), _vec_line(L2)
    if L1 is None or L2 is None:
        print(f"{NO} {label}: " + _t(
            "сначала запишите обе прямые: vec(точка) + lam*vec(направление)",
            "write both lines first: vec(point) + lam*vec(direction)"))
        return False
    values = list(got) if isinstance(got, (list, tuple)) else None
    p1, p2 = _two_params(L1, L2)
    if values is None or len(values) != 2:
        print(f"{NO} {label}: " + _t(f"ответ — два числа: [{p1}, {p2}]",
                                     f"the answer is two numbers: [{p1}, {p2}]"))
        return False
    gap = [sp.sympify(c) for c in (L1.at(values[0]) - L2.at(values[1]))]
    loose = _has_float(values)
    held = [i for i, c in enumerate(gap) if _vec_agree(c, 0) or (
        loose and abs(_vec_number(c) or 1) <= _VEC_LOOSE * _scale(L1.at(values[0])))]
    if len(held) < 2:
        print(f"{NO} {label}: " + _t(
            f"при {p1} = {_text(values[0])}, {p2} = {_text(values[1])} "
            f"не сходятся никакие две компоненты",
            f"at {p1} = {_text(values[0])}, {p2} = {_text(values[1])} "
            f"no two of the components agree"))
        return False
    if len(held) == len(gap):
        tail = _t("; сходится и третья — прямые пересекаются",
                  "; the third agrees too — the lines meet")
    else:
        rest = [i for i in range(len(gap)) if i not in held][0]
        one, two = L1.at(values[0])[rest], L2.at(values[1])[rest]
        tail = _t(f"; третья компонента не сходится: {_text(one)} ≠ {_text(two)}",
                  f"; the remaining component does not: {_text(one)} ≠ {_text(two)}")
    print(f"{OK} {label}: {p1} = {_text(values[0])}, {p2} = {_text(values[1])}" + tail)
    return True


def verify_line_parameter(label, got, L, P):
    """Ответ — значение параметра, при котором прямая проходит через точку P."""
    if _blank(label, got):
        return False
    point = _as_vec(P)
    s = sp.Dummy('s')
    found = sp.linsolve(list(L.at(s) - point), [s])
    if found == sp.EmptySet or not found:
        print(f"{NO} {label}: " + _t(f"точка {_text(point)} на прямой не лежит",
                                     f"the point {_text(point)} is not on the line"))
        return False
    value = next(iter(found))[0]
    exact = not _has_float(got)
    if _vec_agree(got, value, exact):
        print(f"{OK} {label}: {_text(L.param)} = {_text(got)}")
        return True
    if _vec_agree(got, -value, exact):
        message = _t(f"это значение для противоположного направления: у этой прямой "
                     f"направление {_text(L.direction)}",
                     f"that is the value for the opposite direction: this line has the "
                     f"direction {_text(L.direction)}")
    elif _vec_number(got) is not None:
        message = _t(f"при {_text(L.param)} = {_text(got)} прямая в точке {_text(L.at(got))}, "
                     f"а не в {_text(point)}",
                     f"at {_text(L.param)} = {_text(got)} the line is at {_text(L.at(got))}, "
                     f"not at {_text(point)}")
    else:
        message = _t("ответ — число", "the answer is a number")
    print(f"{NO} {label}: {message}")
    return False


# ==================================================================== угол

def _angle_parts(objects):
    """(u, v, acute, kind, extra) из того, что передал вопрос."""
    if len(objects) == 3:
        P, V, Q = (_as_vec(item) for item in objects)
        return P - V, Q - V, False, 'vertex', (P, V, Q)
    if len(objects) != 2:
        raise ValueError('verify_angle: two vectors, two lines or three points')
    first, second = objects
    if isinstance(second, str):
        if second != 'horizontal':
            raise ValueError("verify_angle: the only word is 'horizontal'")
        return _as_vec(first), None, True, 'horizontal', None
    acute = isinstance(first, _Line) or isinstance(second, _Line)
    return _direction(first), _direction(second), acute, 'lines' if acute else 'vectors', None


def _angle_value(u, v, acute, kind):
    """Угол в радианах и его косинус — для сравнения."""
    if kind == 'horizontal':
        size = mag(u)
        return sp.asin(sp.Abs(u[len(u) - 1]) / size), None
    cosine = dot(u, v) / (mag(u) * mag(v))
    if acute:
        cosine = sp.Abs(cosine)
    return sp.acos(cosine), cosine


def verify_angle(label, got, *objects, deg=None, cosine=False, exact=False, free=None):
    """Ответ — угол.

    `verify_angle('b', q, u, v)` — между векторами; `(L1, L2)` — между
    прямыми, острый; `(B, V, C)` — угол BVC при вершине V, из рёбер VB и VC;
    `(v, 'horizontal')` — между направлением движения и горизонталью.
    `deg=True` — в градусах, `deg=False` — в радианах, `None` — годится
    любое. `cosine=True` — ответ сам косинус, можно с буквами (`free`).
    """
    if _blank(label, got):
        return False
    u, v, acute, kind, extra = _angle_parts(objects)
    letters = _letters_of(u, v) if v is not None else _letters_of(u)
    for run in _vec_runs(letters, free):
        uu, vv = _subs(u, run), (_subs(v, run) if v is not None else None)
        theta, cos_value = _angle_value(uu, vv, acute, kind)
        mine = _subs(got, run)
        if _vec_number(mine) is None:
            print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number") + _at_words(run))
            return False
        if cosine:
            if exact and _has_float(got):
                print(f"{NO} {label}: " + _t(
                    "вопрос просит точное значение, а это десятичная дробь",
                    "the question asks for the exact value, and this is a decimal"))
                return False
            if _vec_agree(mine, cos_value, exact):
                continue
            message = _cosine_slip(mine, uu, vv, cos_value)
            print(f"{NO} {label}: {message}" + _at_words(run))
            return False
        radians = _vec_number(theta)
        degrees = radians * 180 / math.pi
        if exact and _has_float(got):
            print(f"{NO} {label}: " + _t(
                "вопрос просит точное значение, а это десятичная дробь",
                "the question asks for the exact value, and this is a decimal"))
            return False
        fits_rad = _vec_agree(mine, theta, exact)
        fits_deg = _vec_agree(mine, degrees) if not exact else _vec_agree(mine, theta * 180 / sp.pi, True)
        if (deg is None and (fits_rad or fits_deg)) or (deg is True and fits_deg) or \
                (deg is False and fits_rad):
            continue
        print(f"{NO} {label}: " + _angle_slip(mine, radians, cos_value, deg, kind, extra, uu)
              + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


def _cosine_slip(mine, u, v, want):
    product = dot(u, v)
    if _vec_agree(mine, product):
        return _t("это скалярное произведение u·v; косинус — оно, делённое на |u||v|",
                  "that is the scalar product u·v; the cosine is that divided by |u||v|")
    if _vec_agree(mine, product / mag(u)) or _vec_agree(mine, product / mag(v)):
        return _t("поделено только на одну длину: косинус — u·v/(|u||v|)",
                  "only one length is divided out: the cosine is u·v/(|u||v|)")
    if _vec_agree(mine, -want):
        return _t("знак не тот: у острого угла косинус положителен",
                  "the sign is wrong: an acute angle has a positive cosine")
    return _t("косинус угла другой", "the cosine of the angle is something else")


def _angle_slip(mine, radians, cos_value, deg, kind, extra, u):
    value = _vec_number(mine)
    degrees = radians * 180 / math.pi
    unit = 180.0 if (deg is True or (deg is None and abs(value) > 2 * math.pi)) else math.pi
    here = degrees if unit == 180.0 else radians
    if deg is True and _draw_agree(value, radians):
        return _t("это радианы, а вопрос просит градусы", "that is in radians, and the question asks for degrees")
    if deg is False and _draw_agree(value, degrees):
        return _t("это градусы, а вопрос просит радианы", "that is in degrees, and the question asks for radians")
    if cos_value is not None and _draw_agree(value, _vec_number(cos_value)):
        return _t("это cos θ, а не сам угол", "that is cos θ, not the angle itself")
    if _draw_agree(value, unit - here):
        if kind == 'lines':
            return _t("это тупой угол между направлениями; угол между прямыми — "
                      "острый, 180° − θ",
                      "that is the obtuse angle between the directions; the angle between "
                      "lines is the acute one, 180° − θ")
        return _t("это угол с одним из векторов, развёрнутым в обратную сторону",
                  "that is the angle with one of the vectors reversed")
    if kind == 'horizontal' and _draw_agree(value, unit / 2 - here):
        return _t("это угол с вертикалью, а не с горизонталью",
                  "that is the angle with the vertical, not with the horizontal")
    if kind == 'vertex':
        P, V, Q = extra
        at_origin = _vec_number(angle(P, Q))
        if at_origin is not None and _draw_agree(value, at_origin * (unit / math.pi)):
            return _t("это угол между радиус-векторами OP и OQ из начала координат; угол "
                      "при вершине V — между рёбрами VP и VQ",
                      "that is the angle between the position vectors from the origin; the "
                      "angle at the vertex V is between the edges from V")
        for one, vertex, two in ((V, P, Q), (P, Q, V)):
            other = _vec_number(angle(one - vertex, two - vertex))
            if other is not None and _draw_agree(value, other * (unit / math.pi)):
                return _t("это угол при другой вершине треугольника",
                          "that is the angle at another vertex of the triangle")
    if sig(value, 2) == sig(here, 2) and float(sig(value, 2)) == value:
        return _t("две значащие цифры, а нужны три", "two significant figures, and three are needed")
    return _t("угол другой", "the angle is something else")


# ============================================================ пеленг, скорость

def verify_bearing(label, got, v):
    """Ответ — трёхзначный пеленг направления v: x — восток, y — север."""
    if _blank(label, got):
        return False
    vector = _as_vec(v)
    bearing = math.degrees(math.atan2(_vec_number(vector[0]), _vec_number(vector[1]))) % 360
    text = str(got).strip().rstrip('°')
    try:
        value = float(text)
    except ValueError:
        print(f"{NO} {label}: " + _t("пеленг — число градусов: '063'",
                                     "a bearing is a number of degrees: '063'"))
        return False
    whole = round(bearing) % 360
    if abs(value - whole) < 1e-9:
        print(f"{OK} {label}: {int(whole):03d}°")
        return True
    if abs(value - bearing) < 0.5:
        message = _t(f"пеленг пишут тремя цифрами целых градусов: {int(whole):03d}°",
                     f"a three-figure bearing is whole degrees: {int(whole):03d}°")
    elif abs(value - (90 - bearing) % 360) < 1:
        message = _t("угол отсчитан от востока; пеленг отсчитывают от севера по часовой стрелке",
                     "the angle is measured from east; a bearing is measured from north, clockwise")
    elif abs(value - (bearing + 180) % 360) < 1:
        message = _t("это пеленг обратного направления", "that is the bearing of the opposite direction")
    elif abs(value - (360 - bearing) % 360) < 1:
        message = _t("угол отсчитан против часовой стрелки", "the angle is measured anticlockwise")
    else:
        message = _t("пеленг другой", "the bearing is something else")
    print(f"{NO} {label}: {message}")
    return False


def verify_speed(label, got, r, var=t, exact=False):
    """Ответ — скорость движения r(t) = r₀ + t·v: длина вектора скорости."""
    if _blank(label, got):
        return False
    var = _time(r, var)
    speed_vec = velocity(r, var)
    if speed_vec.has(var):
        raise ValueError('verify_speed: the motion must have a constant velocity')
    speed = mag(speed_vec)
    if exact and _has_float(got):
        print(f"{NO} {label}: " + _t(
            "вопрос просит точное значение, а это десятичная дробь",
            "the question asks for the exact value, and this is a decimal"))
        return False
    if _vec_agree(got, speed, exact):
        print(f"{OK} {label}: {_text(got)}")
        return True
    value = _vec_number(got)
    start = _as_vec(r).subs(var, 0)
    if value is not None and _draw_agree(value, _vec_number(mag(start))):
        message = _t("это расстояние от O до начальной точки, а не скорость: скорость — "
                     "длина вектора при t",
                     "that is the distance of the starting point from O, not the speed: the "
                     "speed is the length of the vector multiplying t")
    elif value is not None and _draw_agree(value, _vec_number(mag(start + speed_vec))):
        message = _t("это расстояние от O в момент t = 1, а не скорость",
                     "that is the distance from O at t = 1, not the speed")
    elif value is not None and any(_draw_agree(value * n, _vec_number(speed)) for n in range(2, 13)):
        n = next(n for n in range(2, 13) if _draw_agree(value * n, _vec_number(speed)))
        message = _t(f"потерян множитель {n}: скорость — весь вектор при t, вместе с числом перед t",
                     f"a factor of {n} is missing: the velocity is everything that multiplies t, "
                     f"the number in front included")
    elif value is not None and _draw_agree(value, _vec_number(speed) ** 2):
        message = _t("это квадрат скорости: корень не извлечён", "that is the square of the speed: the square root is missing")
    else:
        message = _t("скорость другая", "the speed is something else")
    print(f"{NO} {label}: {message}")
    return False


def verify_optimum(label, got, target, var, domain, kind='min', of=None):
    """Ответ — вектор target в момент, когда of(target) наименьшая (или наибольшая).

    `verify_optimum('b', p, a + b, theta, Interval(0, 2*pi))`: b пробегает
    окружность, и проверка сама ищет, где |a + b| меньше всего.
    """
    if _blank(label, got):
        return False
    measure = of or mag
    target = _as_vec(target)
    where, extreme = _sweep(measure(target), var, domain, kind)
    want = target.subs(var, where).evalf(20)
    mine = _as_vec(got)
    if mine is None or len(mine) != len(want):
        print(f"{NO} {label}: " + _t(f"ответ — вектор из {len(want)} чисел",
                                     f"the answer is a vector of {len(want)} numbers"))
        return False
    if all(_draw_agree(_vec_number(p), _vec_number(q)) for p, q in zip(mine, want)):
        print(f"{OK} {label}: {_text(mine)}")
        return True
    yours = _vec_number(measure(mine))
    word = _t('наименьшем' if kind == 'min' else 'наибольшем', 'minimum' if kind == 'min' else 'maximum')
    if yours is not None and not _draw_agree(yours, extreme):
        message = _t(f"у вашего вектора длина {sig(yours, 4)}, а при {word} значении она "
                     f"{sig(extreme, 4)}",
                     f"your vector has length {sig(yours, 4)}, and at the {word} it is "
                     f"{sig(extreme, 4)}")
    else:
        message = _t("длина та, но вектор смотрит в другую сторону",
                     "the length is right, but the vector points another way")
    print(f"{NO} {label}: {message}")
    return False


def _sweep(expr, var, domain, kind):
    """Наименьшее или наибольшее значение выражения на отрезке: сетка и золотое сечение."""
    lo, hi = float(domain.start), float(domain.end)
    size = sp.lambdify(var, expr, 'math')
    grid = [lo + (hi - lo) * i / 2000 for i in range(2001)]
    pick = min if kind == 'min' else max
    best = pick(grid, key=size)
    left, right = max(lo, best - (hi - lo) / 2000), min(hi, best + (hi - lo) / 2000)
    golden = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        one, two = right - golden * (right - left), left + golden * (right - left)
        if (size(one) < size(two)) == (kind == 'min'):
            right = two
        else:
            left = one
    where = (left + right) / 2
    return where, size(where)


def verify_extent(label, got, expr, var, domain):
    """Ответ — промежуток, который пробегает величина: `Interval(2, 28)`.

    «Find the possible range of values for |a + b|»: b пробегает окружность
    `15*vec(cos(theta), sin(theta))`, и проверка сама ищет наименьшее и
    наибольшее |a + b|. Концы достигаются, поэтому промежуток закрытый.
    """
    if _blank(label, got):
        return False
    if not isinstance(got, sp.Interval):
        print(f"{NO} {label}: " + _t("ответ — промежуток: Interval(a, b)",
                                     "the answer is an interval: Interval(a, b)"))
        return False
    _, low = _sweep(expr, var, domain, 'min')
    _, high = _sweep(expr, var, domain, 'max')
    ends = [(got.start, low, _t('наименьшее', 'smallest'), got.left_open),
            (got.end, high, _t('наибольшее', 'largest'), got.right_open)]
    for end, want, word, _ in ends:
        if not _vec_agree(end, want):
            below = _vec_number(end) > want
            message = _t(f"{word} значение не {_text(end)}: величина бывает и "
                         f"{'меньше' if below else 'больше'}" if word.startswith('наим') == below else
                         f"{word} значение не {_text(end)}: столько не достигается",
                         f"the {word} value is not {_text(end)}: the quantity also goes "
                         f"{'below' if below else 'above'} it" if (word == 'smallest') == below else
                         f"the {word} value is not {_text(end)}: it is never reached")
            print(f"{NO} {label}: {message}")
            return False
    if got.left_open or got.right_open:
        print(f"{NO} {label}: " + _t("оба конца достигаются, промежуток закрытый: ≤, а не <",
                                     "both ends are reached, so the interval is closed: ≤, not <"))
        return False
    print(f"{OK} {label}: {_text(got.start)} ≤ … ≤ {_text(got.end)}")
    return True


# ============================================================ условия и искомое

_UNKNOWN = set()


def unknown(name, dim=None):
    """Искомое: точка `unknown('D', 3)`, вектор `unknown('q', 2)` или число `unknown('r')`."""
    if dim is None:
        symbol = sp.Dummy(name)
        _UNKNOWN.add(symbol)
        return symbol
    parts = [sp.Dummy(f"{name}{'xyz'[i] if dim <= 3 else i + 1}") for i in range(dim)]
    _UNKNOWN.update(parts)
    out = sp.Matrix(parts)
    out._vec_name = name
    return out


class _Fact:
    """Условие вопроса: уравнения (= 0), ограничения и свежие параметры.

    `words(run)` — как условие звучит нарушенным, с подставленными значениями.
    """

    def __init__(self, equations=(), filters=(), params=(), words=None, plain=False):
        self.equations = [sp.sympify(e) for e in equations]
        self.filters = list(filters)
        self.params = list(params)
        self.words = words
        self.plain = plain          # просто Eq: его слова — только числа

    @property
    def letters(self):
        out = set()
        for e in self.equations:
            out |= e.free_symbols
        for f in self.filters:
            out |= f.free_symbols
        return out - set(self.params)

    def subs(self, run):
        if not run:
            return self
        words = self.words
        return _Fact([e.subs(run) for e in self.equations],
                     [f.subs(run) for f in self.filters], self.params,
                     None if words is None else (lambda more: words({**run, **more})), self.plain)

    def say(self, run):
        if self.words is None:
            return _t("условие не выполняется", "a condition does not hold")
        return self.words(run)


def _names(names, count, default):
    names = list(names or default)
    return names[:count] if len(names) >= count else list(default)[:count]


def parallelogram(A, B, C, D, names='ABCD'):
    """Условие: ABCD — параллелограмм, вершины по порядку (AB = DC)."""
    a, b, c, d = (_as_vec(p) for p in (A, B, C, D))
    n = ''.join(_names(names, 4, 'ABCD'))

    def words(run):
        one, two = (b - a).subs(run), (c - d).subs(run)
        return _t(f"{n} — не параллелограмм: {n[0]}{n[1]} = {_text(one)}, "
                  f"а {n[3]}{n[2]} = {_text(two)}",
                  f"{n} is not a parallelogram: {n[0]}{n[1]} = {_text(one)}, "
                  f"and {n[3]}{n[2]} = {_text(two)}")
    return _Fact(list(b - a - (c - d)), words=words)


def midpoint(M, A, B):
    """Условие: M — середина AB."""
    m, a, b = (_as_vec(p) for p in (M, A, B))

    def words(run):
        return _t(f"{_text(m.subs(run))} — не середина между {_text(a.subs(run))} и {_text(b.subs(run))}",
                  f"{_text(m.subs(run))} is not halfway between {_text(a.subs(run))} and {_text(b.subs(run))}")
    return _Fact(list(2 * m - a - b), words=words)


def on(P, first, second=None):
    """Условие: P лежит на прямой — `on(E, L)` или `on(E, A, C)`."""
    L = first if isinstance(first, _Line) else through(first, second)
    point = _as_vec(P)
    s = sp.Dummy('s')

    def words(run):
        return _t(f"{_text(point.subs(run))} не лежит на прямой {L.subs(run)}",
                  f"{_text(point.subs(run))} is not on the line {L.subs(run)}")
    return _Fact(list(point - L.at(s)), params=[s], words=words)


def _minors(one, two):
    return [one[i] * two[j] - one[j] * two[i]
            for i in range(len(one)) for j in range(i + 1, len(one))]


def parallel(u, v):
    """Условие: векторы (или прямые) параллельны."""
    one, two = _direction(u), _direction(v)

    def words(run):
        return _t(f"{_text(one.subs(run))} и {_text(two.subs(run))} не кратны друг другу",
                  f"{_text(one.subs(run))} and {_text(two.subs(run))} are not multiples of each other")
    return _Fact(_minors(one, two), words=words)


def perpendicular(u, v):
    """Условие: векторы (или прямые) перпендикулярны — скалярное произведение ноль."""
    one, two = _direction(u), _direction(v)

    def words(run):
        product = _text(dot(one.subs(run), two.subs(run)))
        return _t(f"не перпендикулярны: скалярное произведение {product}, а не 0",
                  f"not perpendicular: the scalar product is {product}, not 0")
    return _Fact([dot(one, two)], words=words)


def length(v, size):
    """Условие: длина вектора равна size."""
    vector, size = _as_vec(v), sp.sympify(size)

    def words(run):
        return _t(f"длина {_text(mag(vector.subs(run)))}, а не {_text(size.subs(run))}",
                  f"the length is {_text(mag(vector.subs(run)))}, not {_text(size.subs(run))}")
    return _Fact([dot(vector, vector) - size ** 2], [size >= 0] if size.free_symbols else [],
                 words=words)


def meet(L1, L2):
    """Условие: прямые пересекаются — у них есть общая точка."""
    s, u = sp.Dummy('s'), sp.Dummy('u')
    return _Fact(list(L1.at(s) - L2.at(u)), params=[s, u], words=lambda run: _t(
        "при этих значениях прямые не пересекаются", "with these values the lines do not meet"))


def no_unique_meet(L1, L2):
    """Условие: у прямых нет единственной общей точки — направления кратны."""
    return _Fact(_minors(L1.direction, L2.direction), words=lambda run: _t(
        "при этом значении прямые пересекаются в одной точке",
        "with this value the lines meet at a single point"))


def _as_fact(item):
    if isinstance(item, _Fact):
        return item
    if isinstance(item, sp.Equality):
        left, right = item.lhs, item.rhs
        if isinstance(left, sp.MatrixBase) or isinstance(right, sp.MatrixBase):
            left, right = sp.Matrix(left), sp.Matrix(right)
            equations = list(left - right)
        else:
            equations = [left - right]

        def words(run):
            one, two = _subs(left, run), _subs(right, run)
            return _t(f"условие не выполняется: {_text(one)} ≠ {_text(two)}",
                      f"the condition does not hold: {_text(one)} ≠ {_text(two)}")
        return _Fact(equations, words=words, plain=True)
    if item is sp.true or item is True:
        return _Fact()
    if item is sp.false or item is False:
        return _Fact([sp.Integer(1)])
    if isinstance(item, sp.Rel):
        return _Fact(filters=[item])
    raise ValueError(f'verify_find: cannot read the condition {item!r}')


def _unwrap(expression):
    """acos(A) − acos(B) → A − B, acos(A) − c → A − cos c: у уравнения те же корни."""
    terms = sp.Add.make_args(sp.sympify(expression))
    arcs = [term for term in terms if isinstance(term, sp.acos)
            or (term.is_Mul and len(term.args) == 2 and term.args[0] == -1
                and isinstance(term.args[1], sp.acos))]
    rest = [term for term in terms if term not in arcs]
    if len(arcs) == 2 and not rest:
        signs = [1 if isinstance(term, sp.acos) else -1 for term in arcs]
        inner = [term if isinstance(term, sp.acos) else term.args[1] for term in arcs]
        if signs[0] != signs[1]:
            return inner[0].args[0] - inner[1].args[0]
    if len(arcs) == 1 and all(not (term.free_symbols & arcs[0].free_symbols) for term in rest):
        arc = arcs[0]
        sign = 1 if isinstance(arc, sp.acos) else -1
        inner = arc if sign == 1 else arc.args[1]
        constant = -sp.Add(*rest) * sign
        if not constant.free_symbols:
            return inner.args[0] - sp.cos(constant)
    return expression


def _branches(expression):
    """Все варианты уравнения без модулей: |A| → A и −A."""
    inner = sorted(expression.atoms(sp.Abs), key=sp.default_sort_key)
    if not inner:
        return [expression]
    first = inner[0]
    out = []
    for sign in (1, -1):
        out.extend(_branches(expression.xreplace({first: sign * first.args[0]})))
    return out


def _candidates(equations, names):
    """Решения системы: sympy, со снятыми арккосинусами и модулями."""
    prepared = [_unwrap(e) for e in equations]
    systems = [[]]
    for e in prepared:
        systems = [s + [variant] for s in systems for variant in _branches(e)][:16]
    found = []
    for system in systems:
        try:
            solutions = sp.solve(system, names, dict=True)
        except (NotImplementedError, ValueError, TypeError, KeyError):
            solutions = []
        found.extend(solutions)
    if not found and len(names) == 1 and len(prepared) >= 1:
        found = _scan(prepared, names[0])
    return found


def _scan(equations, name):
    """Корни одного уравнения с одной буквой — сеткой, если sympy не справился."""
    fn = sp.lambdify(name, equations[0], 'math')

    def value(point):
        out = fn(point)
        if isinstance(out, complex):
            raise ValueError
        return float(out)
    return [{name: sp.Float(root, 15)} for root in _scan_roots(value, *_VEC_SCAN)]


def _holds_equation(expression, solution):
    value = sp.sympify(expression).subs(solution)
    if value.free_symbols:
        return sp.simplify(value) == 0
    number = _vec_number(value)
    size = max([1.0] + [abs(_vec_number(term) or 0.0) for term in sp.Add.make_args(sp.expand(value))])
    return number is not None and abs(number) <= 1e-8 * size


def _holds_filter(relation, solution):
    value = relation.subs(solution)
    if value in (sp.true, True):
        return True
    if value in (sp.false, False):
        return False
    if isinstance(value, sp.Rel) and not value.free_symbols:
        if isinstance(value, sp.Ne):
            left, right = value.lhs, value.rhs
            if isinstance(left, sp.MatrixBase):
                return not _agree_vec(left, right)
            return not _vec_agree(left, right)
        difference = _vec_number(value.lhs - value.rhs)
        if difference is None:
            return True
        return bool(value.func(difference, 0))
    return True


def _solve_facts(facts, unknowns):
    """Все решения условий: (подходящие, отброшенные с нарушенным ограничением)."""
    equations, filters, params = [], [], []
    for fact in facts:
        equations += [e for e in fact.equations if e != 0]
        filters += fact.filters
        params += fact.params
    names = [s for s in list(unknowns) + params if any(e.has(s) for e in equations)]
    if not equations:
        return [{}], []
    found = _candidates(equations, names)
    good, rejected = [], []
    seen = []
    for solution in found:
        if not all(_holds_equation(e, solution) for e in equations):
            continue
        if any(_vec_number(v) is None for v in solution.values() if not sp.sympify(v).free_symbols):
            continue
        key = tuple(_text(solution.get(s, s)) for s in names)
        if key in seen:
            continue
        seen.append(key)
        broken = next((f for f in filters if not _holds_filter(f, solution)), None)
        (good if broken is None else rejected).append((solution, broken))
    return [s for s, _ in good], rejected


def _target_value(target, solution):
    if isinstance(target, (list, tuple)):
        return [_target_value(item, solution) for item in target]
    vector = _as_vec(target)
    if vector is not None:
        return vector.subs(solution)
    return sp.sympify(target).subs(solution)


def _same_answer(mine, want, exact):
    if isinstance(want, list):
        return isinstance(mine, (list, tuple)) and len(mine) == len(want) and \
            all(_vec_same(m, w, exact) for m, w in zip(mine, want))
    return _vec_same(mine, want, exact)


def _generic_slip(mine, want):
    """Промахи, которые узнаются по одному числу или вектору."""
    wanted_vec, mine_vec = _as_vec(want), _as_vec(mine)
    if wanted_vec is not None:
        if mine_vec is None:
            return _t("ответ — вектор: vec(...) или (x, y, z)", "the answer is a vector: vec(...) or (x, y, z)")
        if len(mine_vec) == len(wanted_vec) and _agree_vec(mine_vec, -wanted_vec):
            return _t("это тот же вектор в обратную сторону: вектор между точками — "
                      "конец минус начало",
                      "that is the same vector the other way round: a vector between two "
                      "points is the end minus the start")
        return None
    if mine_vec is not None:
        if _vec_agree(mag(mine_vec), want):
            return _t("это вектор, а вопрос спрашивает его длину",
                      "that is a vector, and the question asks for its length")
        return _t("ответ — число, а не вектор", "the answer is a number, not a vector")
    value, target = _vec_number(mine), _vec_number(want)
    if value is None or target is None:
        return None
    for factor, words in ((-1, _t("знак не тот", "the sign is the other way")),
                          (2, _t("это вдвое больше", "that is twice the value")),
                          (0.5, _t("это вдвое меньше", "that is half the value")),
                          (60, _t("это в 60 раз больше — проверьте единицы времени",
                                  "that is 60 times the value — check the units of time")),
                          (1 / 60, _t("это в 60 раз меньше — проверьте единицы времени",
                                      "that is a sixtieth of the value — check the units of time"))):
        if target != 0 and _draw_agree(value, target * factor):
            return words
    if target > 0 and _draw_agree(value, target ** 2):
        return _t("это квадрат: не извлечён корень", "that is the square: the square root is missing")
    if sig(value, 2) == sig(target, 2) and float(sig(value, 2)) == value:
        return _t("две значащие цифры, а нужны три", "two significant figures, and three are needed")
    return None


def _fact_slip(facts, target, mine, unknowns):
    """Ответ подставляется в условия по одному: какое нарушено первым."""
    assignment = {}
    if isinstance(target, (list, tuple)) and isinstance(mine, (list, tuple)):
        pairs = list(zip(target, mine))
    else:
        pairs = [(target, mine)]
    for name, value in pairs:
        name_vec, value_vec = _as_vec(name), _as_vec(value)
        if name_vec is not None:
            if value_vec is None or len(value_vec) != len(name_vec):
                return None
            if not all(s in unknowns for s in name_vec):
                return None
            assignment.update(dict(zip(name_vec, value_vec)))
        elif isinstance(name, sp.Symbol) and name in unknowns:
            if _as_vec(value) is not None:
                return None
            assignment[name] = sp.sympify(value)
        else:
            return None
    for fact in facts:
        placed = fact.subs(assignment)
        rest = [s for s in list(unknowns) + fact.params
                if any(e.has(s) for e in placed.equations)]
        if not placed.equations:
            broken = next((f for f in placed.filters if not _holds_filter(f, {})), None)
            if broken is not None:
                return (_t(f"не выполнено ограничение вопроса {_rule_text(broken)}",
                           f"the question's restriction {_rule_text(broken)} fails"), False)
            continue
        if any(s not in fact.params for s in rest):
            continue
        loose = _has_float(mine)
        if rest:
            good, _ = _solve_facts([placed], rest)
            holds = bool(good)
        else:
            holds = all(abs(_vec_number(e) or 0) <= (_VEC_LOOSE * 10 if loose else 1e-8) * max(
                1.0, max(abs(_vec_number(v) or 0) for v in assignment.values()) ** 2)
                for e in placed.equations)
        if not holds:
            return fact.say(assignment), fact.plain
    return None


def verify_find(label, got, target, facts=(), exact=False, free=None):
    """Ответ — искомое, которое вопрос задаёт условиями.

    `verify_find('a', q, D, [parallelogram(A, B, C, D)])` — D из того, что
    ABCD параллелограмм; `verify_find('b', q, k, [parallel(B - A, C - A)])` —
    буква; `verify_find('c', q, distance(B, V))` — величина без условий.
    Искомые точки заводят `unknown('D', 3)`; буква-ответ — сама искомая.
    Остальные буквы свободны: ответ через них обязан годиться при любых
    значениях, и проверка пробует несколько.

    Условия решаются все сразу; ограничения вопроса (`q[0] > 0`, `Ne(C, A)`)
    отбрасывают решения. Если решений несколько, ответ — все они списком.
    Неверный ответ подставляется в условия по одному, и первое нарушенное
    называется.
    """
    if _blank(label, got):
        return False
    facts = [_as_fact(item) for item in facts]
    targets = list(target) if isinstance(target, (list, tuple)) else None
    wanted = [s for s in _letters_of(target)
              if isinstance(s, sp.Symbol) and (s in _UNKNOWN or (
                  targets is not None and s in targets) or s == target)]
    unknowns = set(_UNKNOWN) | set(wanted)
    params = set().union(*[set(f.params) for f in facts]) if facts else set()
    letters = (_letters_of(target, *facts) - unknowns - params)
    exact = exact or False
    for run in _vec_runs(letters, free):
        placed = [f.subs(run) for f in facts]
        present = [s for s in unknowns if any(e.has(s) for f in placed for e in f.equations)
                   or s in wanted]
        good, rejected = _solve_facts(placed, present)
        values = []
        for solution in good:
            value = _target_value(_subs(target, run) if targets is None else
                                  [_subs(item, run) for item in targets], solution)
            if _letters_of(value) & unknowns:
                print(f"{NO} {label}: " + _t("условий не хватает, чтобы найти ответ",
                                             "the conditions are not enough to fix the answer"))
                return False
            if not any(_same_answer(value, other, True) for other in values):
                values.append(value)
        if not values:
            print(f"{NO} {label}: " + _t("условиям не удовлетворяет ничто",
                                         "nothing satisfies the conditions") + _at_words(run))
            return False
        mine = _subs(got, run)
        if _letters_of(mine) - set(run):
            extra = _letters_of(mine) - set(run)
            if extra - letters:
                print(f"{NO} {label}: " + _t(
                    f"в ответе лишние буквы: {', '.join(sorted(map(str, extra)))}",
                    f"the answer has letters the question does not: "
                    f"{', '.join(sorted(map(str, extra)))}"))
                return False
        if exact and _has_float(got):
            print(f"{NO} {label}: " + _t(
                "вопрос просит точное значение, а это десятичная дробь",
                "the question asks for the exact value, and this is a decimal"))
            return False
        closeness = exact or not _has_float(got)
        if len(values) == 1:
            if _same_answer(mine, values[0], closeness):
                continue
            message = _find_slip(placed, target, mine, values[0], rejected, unknowns, run)
            print(f"{NO} {label}: {message}" + _at_words(run))
            return False
        given = list(mine) if isinstance(mine, (list, tuple, set)) and not (
            targets is None and _as_vec(target) is not None and _as_vec(mine) is not None) else [mine]
        matched = [any(_same_answer(item, value, closeness) for item in given) for value in values]
        stray = [item for item in given if not any(_same_answer(item, v, closeness) for v in values)]
        if all(matched) and not stray:
            continue
        if stray:
            message = _find_slip(placed, target, stray[0], values[0], rejected, unknowns, run,
                                 several=True)
        else:
            message = _t(f"годных ответов {len(values)}, а у вас {sum(matched)}: "
                         f"потерян {'один' if len(values) - sum(matched) == 1 else 'не один'}",
                         f"there are {len(values)} valid answers and you have {sum(matched)}: "
                         f"{'one is' if len(values) - sum(matched) == 1 else 'some are'} missing")
        print(f"{NO} {label}: {message}" + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


def _rule_text(relation):
    """Ограничение вопроса словами: `Cx ≠ …` для точки — «C ≠ A»."""
    if isinstance(relation, sp.Ne):
        return f"{_text(relation.lhs)} ≠ {_text(relation.rhs)}"
    symbol = {sp.StrictGreaterThan: '>', sp.GreaterThan: '≥',
              sp.StrictLessThan: '<', sp.LessThan: '≤'}.get(type(relation), '?')
    return f"{_text(relation.lhs)} {symbol} {_text(relation.rhs)}"


def _find_slip(facts, target, mine, want, rejected, unknowns, run, several=False):
    closeness = not _has_float(mine)
    for solution, broken in rejected:
        value = _target_value(_subs(target, run), solution)
        if _same_answer(mine, value, closeness):
            return _t(f"это решение условий, но оно нарушает ограничение вопроса "
                      f"{_rule_text(broken)}: такое решение отбрасывают",
                      f"that solves the conditions, but it breaks the question's restriction "
                      f"{_rule_text(broken)}: such a solution is rejected")
    by_fact = _fact_slip(facts, _subs(target, run), mine, unknowns)
    generic = None if isinstance(want, list) else _generic_slip(mine, want)
    if by_fact and not (generic and by_fact[1]):
        return by_fact[0]
    if generic:
        return generic
    if several:
        return _t(f"{_text(mine)} условиям не удовлетворяет", f"{_text(mine)} does not meet the conditions")
    return _t("ответ не удовлетворяет условиям вопроса", "the answer does not meet the conditions")
