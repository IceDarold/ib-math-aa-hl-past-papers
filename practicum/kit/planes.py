"""Плоскости (C6): плоскость — множество точек, система — плоскости, решение — их общая часть.
"""

from itertools import combinations

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .vectors import (
    _Fact, _Line, _VEC_LOOSE, _agree_vec, _as_vec, _generic_slip, _has_float, _minors,
    _one_sign, _on, _parallel, _parse_line, _plain, _scale, _text, _vec_agree,
    _vec_number, _vec_runs, _at_words, dot, lam, mag, z,
)


# ================================================================ плоскости
# Двадцать пятое понятие равенства ответов: плоскость — тоже множество точек,
# а система уравнений — набор плоскостей, и её решение — их общая часть.
#
# Уравнение плоскости задано с точностью до множителя: 2x − 3y − z = 6 и
# 14x − 21y − 7z = 42 — одна плоскость, и r = a + λb + μc с любой её точкой
# и любыми двумя непараллельными направлениями в ней — тоже она. Нормаль —
# любой ненулевой вектор, перпендикулярный плоскости. Общее решение системы
# — прямая, и она принимается в любой параметризации, как прямая C5.
#
# Точка, которую вопрос задаёт словами, — основание перпендикуляра, отражение
# — находится из условий, как в C5: on(C, P), perpendicular(C − B, P),
# reflection(B2, B, P). Буквы при плоскостях — из условий meet_in_line
# («пересекаются по прямой») и no_unique_meet («нет единственного решения»).

def _axes():
    return (x, y, z)


def _as_vec3(value, what='cross'):
    vector = value.direction if isinstance(value, _Line) else _as_vec(value)
    if vector is None or len(vector) != 3:
        raise ValueError(f'{what}: vectors with three components')
    return vector


def cross(u, v):
    """Векторное произведение: `cross(vec(1, 2, 0), vec(0, 1, 3))` — (6, −3, 1)."""
    one, two = _as_vec3(u), _as_vec3(v)
    return sp.Matrix([one[1] * two[2] - one[2] * two[1],
                      one[2] * two[0] - one[0] * two[2],
                      one[0] * two[1] - one[1] * two[0]])


def _sign_words(index, what):
    """Знак одной компоненты; про среднюю — правило векторного произведения."""
    axis = 'xyz'[index]
    normal = what == 'normal'
    whose = _t("у нормали" if normal else "у направления", "of the normal" if normal else "of the direction")
    if index == 1:
        return _t(f"{whose} неверный знак компоненты y: в векторном произведении средняя компонента — "
                  f"a₃b₁ − a₁b₃, а не a₁b₃ − a₃b₁",
                  f"the y-component {whose} has the wrong sign: in a vector product the middle "
                  f"component is a₃b₁ − a₁b₃, not a₁b₃ − a₃b₁")
    return _t(f"{whose} неверный знак компоненты {axis}", f"the {axis}-component {whose} has the wrong sign")


def _is_zero_vector(vector):
    return all(sp.simplify(c) == 0 for c in vector)


class _Plane:
    """Плоскость n · r = d. points и directions — из чего её построил вопрос."""

    def __init__(self, normal, constant, name=None, points=(), directions=(), crossed=False):
        self.normal = sp.Matrix(normal)
        self.constant = sp.sympify(constant)
        self.name = name
        self.points = [sp.Matrix(p) for p in points]
        self.directions = [sp.Matrix(d) for d in directions]
        self.crossed = crossed          # нормаль получена векторным произведением

    @property
    def letters(self):
        return self.normal.free_symbols | self.constant.free_symbols

    def side(self, point):
        """Левая часть уравнения в точке."""
        return sp.expand(dot(self.normal, _as_vec(point)))

    def gap(self, point):
        return self.side(point) - self.constant

    def subs(self, *args):
        run = dict(args[0]) if len(args) == 1 else {args[0]: args[1]}
        if not run:
            return self
        return _Plane(self.normal.subs(run), self.constant.subs(run), self.name,
                      [p.subs(run) for p in self.points],
                      [d.subs(run) for d in self.directions], self.crossed)

    def left(self):
        return sum((c * axis for c, axis in zip(self.normal, _axes())), sp.Integer(0))

    def equation(self):
        return sp.Eq(self.left(), self.constant)

    def some_point(self):
        """Какая-нибудь точка плоскости: на оси при ненулевой компоненте нормали."""
        for i, c in enumerate(self.normal):
            if sp.simplify(c) != 0:
                point = [sp.Integer(0)] * 3
                point[i] = self.constant / c
                return sp.Matrix(point)
        raise ValueError('plane: the normal is the zero vector')

    def __repr__(self):
        shown = _plane_tidy(self)
        return f"{_plain(shown.left())} = {_plain(shown.constant)}"


def _linear_in(expr, symbols):
    """Выражение первой степени по symbols и не пропадает целиком."""
    expr = sp.expand(sp.sympify(expr))
    for s in symbols:
        if sp.simplify(sp.diff(expr, s, 2)) != 0:
            return False
        if sp.diff(expr, s).free_symbols & set(symbols):
            return False
    return any(sp.diff(expr, s) != 0 for s in symbols)


def _plane_from_equation(equation):
    if not isinstance(equation, sp.Equality):
        return None
    expr = sp.expand(equation.lhs - equation.rhs)
    axes = _axes()
    if not _linear_in(expr, axes):
        return None
    normal = [sp.diff(expr, axis) for axis in axes]
    constant = -expr.subs({axis: 0 for axis in axes})
    return _Plane(normal, constant)


def _plane_from_vector(expr, exclude=(), params=None):
    """r = a + λb + μc: (плоскость, точка, b, c) или None."""
    vector = _as_vec(expr)
    if vector is None or len(vector) != 3:
        return None
    if params is None:
        candidates = [s for s in vector.free_symbols if s not in exclude]
        params = [s for s in sorted(candidates, key=str)
                  if all(sp.diff(c, s, 2) == 0 for c in vector)
                  and any(sp.diff(c, s) != 0 for c in vector)]
        if len(params) != 2 or len(candidates) != 2:
            return None
    one, two = params
    b, c = vector.diff(one), vector.diff(two)
    if b.has(one) or b.has(two) or c.has(one) or c.has(two):
        return None
    point = vector.subs({one: 0, two: 0})
    return _Plane(cross(b, c), dot(cross(b, c), point), points=[point],
                  directions=[b, c], crossed=True), point, b, c


def plane(*parts, name=None):
    """Плоскость, как её задаёт вопрос.

    `plane(Eq(2*x - 3*y - z, 6))` — декартово уравнение; `plane(A, n)` —
    точка и нормаль; `plane(A, B, C)` — три точки; `plane(L, P)` — прямая и
    точка; `plane(L1, L2)` — две прямые; `plane(R, P1, P2)` — через точку R
    перпендикулярно двум плоскостям; `plane(vec(...) + lam*vec(...) +
    mu*vec(...))` — векторная форма.
    """
    found = None
    if len(parts) == 1:
        item = parts[0]
        if isinstance(item, _Plane):
            found = item
        elif isinstance(item, sp.Equality):
            found = _plane_from_equation(item)
            if found is None:
                raise ValueError('plane: a linear equation in x, y and z')
        else:
            parsed = _plane_from_vector(item)
            if parsed is None:
                raise ValueError('plane: write it as vec(point) + lam*vec(...) + mu*vec(...)')
            found = parsed[0]
    elif len(parts) == 2:
        one, two = parts
        if isinstance(one, _Line) and isinstance(two, _Line):
            step = two.point - one.point
            normal = cross(one.direction, two.direction)
            directions = [one.direction, two.direction]
            if _is_zero_vector(normal):
                normal, directions = cross(one.direction, step), [one.direction, step]
            found = _Plane(normal, dot(normal, one.point), points=[one.point, two.point],
                           directions=directions, crossed=True)
        elif isinstance(one, _Line) or isinstance(two, _Line):
            L, point = (one, _as_vec(two)) if isinstance(one, _Line) else (two, _as_vec(one))
            step = point - L.point
            normal = cross(L.direction, step)
            found = _Plane(normal, dot(normal, point), points=[L.point, point],
                           directions=[L.direction, step], crossed=True)
        else:
            point, normal = _as_vec(one), _as_vec(two)
            found = _Plane(normal, dot(normal, point), points=[point])
    elif len(parts) == 3:
        if isinstance(parts[1], _Plane) and isinstance(parts[2], _Plane):
            point = _as_vec(parts[0])
            normal = cross(parts[1].normal, parts[2].normal)
            found = _Plane(normal, dot(normal, point), points=[point],
                           directions=[parts[1].normal, parts[2].normal], crossed=True)
        else:
            A, B, C = (_as_vec(p) for p in parts)
            normal = cross(B - A, C - A)
            found = _Plane(normal, dot(normal, A), points=[A, B, C],
                           directions=[B - A, C - A], crossed=True)
    if found is None:
        raise ValueError('plane: an equation, a point and a normal, three points, or lines')
    if _is_zero_vector(found.normal):
        raise ValueError('plane: these do not fix a plane — the normal comes out zero')
    if name is not None:
        found = _Plane(found.normal, found.constant, name, found.points, found.directions, found.crossed)
    return found


# ------------------------------------------------------------ общая часть

def _letters(*items):
    out = set()
    for item in items:
        if isinstance(item, (_Plane, _Line)):
            out |= item.letters
        elif isinstance(item, sp.MatrixBase):
            out |= item.free_symbols
        elif isinstance(item, (list, tuple)):
            out |= _letters(*item)
    return out


def _subs_item(item, run):
    if not run:
        return item
    if isinstance(item, (_Plane, _Line)):
        return item.subs(run)
    vector = _as_vec(item)
    return vector.subs(run) if vector is not None else sp.sympify(item).subs(run)


def _whole(vector):
    """Направление с рациональными компонентами — к целым без общего делителя."""
    if not all(isinstance(c, sp.Rational) for c in vector) or _is_zero_vector(vector):
        return vector
    top = sp.ilcm(*[c.q for c in vector])
    common = sp.igcd(*[int(c * top) for c in vector if c != 0])
    return vector * sp.Rational(top, common)


def intersection(*objects):
    """Общая часть плоскостей и прямых: точка, прямая, плоскость или None."""
    X = sp.Matrix([sp.Dummy('px'), sp.Dummy('py'), sp.Dummy('pz')])
    equations, unknowns = [], list(X)
    for item in objects:
        if isinstance(item, _Plane):
            equations.append(dot(item.normal, X) - item.constant)
        elif isinstance(item, _Line):
            s = sp.Dummy('s')
            unknowns.append(s)
            equations += list(X - item.at(s))
        else:
            equations += list(X - _as_vec(item))
    found = sp.linsolve(equations, unknowns)
    if not found or found == sp.EmptySet:
        return None
    point = sp.Matrix([sp.simplify(c) for c in next(iter(found))[:3]])
    free = sorted(point.free_symbols & set(unknowns), key=str)
    if not free:
        return point
    if len(free) == 1:
        found_line = _Line(point.subs(free[0], 0), _whole(point.diff(free[0])), lam)
        found_line.extra['planes'] = [item for item in objects if isinstance(item, _Plane)]
        return found_line
    base = point.subs({s: 0 for s in free})
    normal = cross(point.diff(free[0]), point.diff(free[1]))
    return _Plane(normal, dot(normal, base))


def _called(item, index):
    """Имя объекта для сообщения: своё или по порядку — «вторая плоскость»."""
    if getattr(item, 'name', None):
        return item.name
    place = min(index, 3)
    if isinstance(item, _Plane):
        return _t(("первая", "вторая", "третья", "четвёртая")[place] + " плоскость",
                  "the " + ("first", "second", "third", "fourth")[place] + " plane")
    return _t(("первая", "вторая", "третья", "четвёртая")[place] + " прямая",
              "the " + ("first", "second", "third", "fourth")[place] + " line")


def _plane_close(value, want, loose, size=1.0):
    difference = sp.sympify(value) - sp.sympify(want)
    if not loose:
        exact = sp.simplify(difference)
        if exact == 0:
            return True
        if not exact.has(sp.Float) and exact.is_number:
            return False
    number = _vec_number(difference)
    return number is not None and abs(number) <= (_VEC_LOOSE if loose else 1e-9) * max(1.0, size)


def _in_plane(point, P, loose=False):
    size = _scale(_as_vec(point), P.normal) * max(1.0, abs(_vec_number(P.constant) or 0))
    return _plane_close(P.side(point), P.constant, loose, size)


def _plane_tidy(P):
    """Плоскость с дробными коэффициентами — к целым: для сообщений, не для счёта."""
    numbers = list(P.normal) + [P.constant]
    if not all(isinstance(c, sp.Rational) for c in numbers):
        return P
    top = sp.ilcm(*[c.q for c in numbers])
    whole = [c * top for c in numbers]
    common = sp.igcd(*[int(c) for c in whole if c != 0])
    scale = sp.Rational(top, common)
    if scale == 1:
        return P
    return _Plane(P.normal * scale, P.constant * scale, P.name, P.points, P.directions, P.crossed)


def _not_on_words(point, P, name):
    P = _plane_tidy(P)
    return _t(f"{_text(point)} не лежит в плоскости {name}: {_plain(P.left())} даёт "
              f"{_text(P.side(point))}, а не {_text(P.constant)}",
              f"{_text(point)} is not on {name}: {_plain(P.left())} gives "
              f"{_text(P.side(point))}, not {_text(P.constant)}")


def _where_not(point, objects, loose):
    """Первый объект, на котором точки нет, словами; None — точка на всех."""
    for index, item in enumerate(objects):
        name = _called(item, index)
        if isinstance(item, _Plane):
            if not _in_plane(point, item, loose):
                return _not_on_words(point, item, name)
        elif isinstance(item, _Line):
            if not _on(point, item, loose):
                return _t(f"{_text(point)} не лежит на прямой {name}",
                          f"{_text(point)} is not on {name}")
    return None


def _line_in_plane(L, P, loose):
    return _in_plane(L.point, P, loose) and _plane_close(dot(L.direction, P.normal), 0, loose, _scale(L.direction, P.normal))


def _line_not_in(L, objects, loose):
    for index, item in enumerate(objects):
        name = _called(item, index)
        if isinstance(item, _Plane) and not _line_in_plane(L, item, loose):
            if not _in_plane(L.point, item, loose):
                return _not_on_words(L.point, item, name)
            product = dot(L.direction, item.normal)
            return _t(f"направление {_text(L.direction)} не лежит в плоскости {name}: его "
                      f"скалярное произведение с нормалью {_text(item.normal)} равно "
                      f"{_text(product)}, а не 0",
                      f"the direction {_text(L.direction)} does not lie in {name}: its scalar "
                      f"product with the normal {_text(item.normal)} is {_text(product)}, not 0")
        if isinstance(item, _Line) and not (_parallel(L.direction, item.direction, loose)
                                            and _on(L.point, item, loose)):
            return _t(f"это не прямая {name}", f"that is not {name}")
    return None


_NONE_WORDS = {'none', 'no point', 'no points', 'no common point', 'no common points',
               'empty', 'nothing', 'no intersection', 'no solution', 'no solutions'}


def _answer_set(got, exclude):
    """Ответ о общей части: ('none',), ('point', v), ('line', L), ('plane', P), ('number', n)."""
    if got is None or got is sp.EmptySet or (isinstance(got, str) and
                                             got.strip().strip("'\"").lower() in _NONE_WORDS):
        return ('none',)
    if isinstance(got, _Line):
        return ('line', got)
    if isinstance(got, _Plane):
        return ('plane', got)
    if isinstance(got, sp.Equality):
        found = _plane_from_equation(got)
        return ('plane', found) if found is not None else (None, None)
    vector = _as_vec(got)
    if vector is not None:
        parsed = _parse_line(vector, exclude=exclude)
        if parsed is not None and len(parsed.point) == 3:
            return ('line', parsed)
        if len(vector) == 3:
            return ('point', vector)
        return (None, None)
    if isinstance(got, str):
        return (None, None)
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError):
        return (None, None)
    return ('number', value) if _vec_number(value) is not None else (None, None)


def _answer_subs(kind, run):
    if len(kind) == 1 or not run:
        return kind
    return (kind[0], _subs_item(kind[1], run))


def _plane_set_text(kind):
    if kind[0] == 'none':
        return _t('общих точек нет', 'no common point')
    return _text(kind[1]) if kind[0] in ('point', 'number') else repr(kind[1])


def verify_intersection(label, got, *objects, free=None):
    """Ответ — общая часть плоскостей и прямых: точка, прямая или 'none'.

    `verify_intersection('b', q, P1, P2, P3)` — где три плоскости сходятся;
    `(L, P)` — где прямая протыкает плоскость; `(P1, P2)` — прямая пересечения,
    её принимают в любой параметризации. Система уравнений — те же плоскости:
    общее решение — прямая, `vec(-t/2 + 4, 3*t/2, t)` годится. Неверный ответ
    получает имя: точка не на такой-то плоскости (и что даёт подстановка),
    параметр вместо точки, направление по нормали, прямая вместо точки.
    """
    if _blank(label, got):
        return False
    letters = _letters(*objects)
    kind = _answer_set(got, letters)
    if kind[0] is None:
        print(f"{NO} {label}: " + _t(
            "ответ — точка (x, y, z), прямая vec(точка) + lam*vec(направление) или 'none'",
            "the answer is a point (x, y, z), a line vec(point) + lam*vec(direction), or 'none'"))
        return False
    loose = _has_float(got) or (kind[0] == 'line' and _has_float(kind[1]))
    for run in _vec_runs(letters, free):
        items = [_subs_item(item, run) for item in objects]
        truth = intersection(*items)
        mine = _answer_subs(kind, run)
        message = _intersection_slip(mine, truth, items, loose)
        if message is None:
            continue
        print(f"{NO} {label}: {message}" + _at_words(run))
        return False
    print(f"{OK} {label}: {_plane_set_text(kind)}")
    return True


def _param_at(L, point):
    s = sp.Dummy('s')
    found = sp.linsolve(list(L.at(s) - _as_vec(point)), [s])
    if not found or found == sp.EmptySet:
        return None
    value = next(iter(found))[0]
    return None if value.has(s) else value


def _intersection_slip(mine, truth, items, loose):
    """None — ответ верен; иначе — что с ним не так."""
    lines = [item for item in items if isinstance(item, _Line)]
    if truth is None:
        if mine[0] == 'none':
            return None
        if mine[0] == 'point':
            return _where_not(mine[1], items, loose) or _t("общих точек нет", "there is no common point")
        if mine[0] == 'line':
            return _line_not_in(mine[1], items, loose) or _t("общих точек нет", "there is no common point")
        return _t("ответ — точка, прямая или 'none'", "the answer is a point, a line or 'none'")
    if isinstance(truth, sp.MatrixBase):
        if mine[0] == 'point':
            if _agree_vec(mine[1], truth, not loose):
                return None
            for L in lines:
                value = _param_at(L, truth)
                if value is not None and value != 0 and _agree_vec(mine[1], L.at(-value), not loose):
                    return _t(f"{_text(mine[1])} лежит на прямой, но по другую сторону от её точки "
                              f"{_text(L.point)}: проверьте знак параметра",
                              f"{_text(mine[1])} is on the line, but on the other side of its point "
                              f"{_text(L.point)}: check the sign of the parameter")
            return _where_not(mine[1], items, True) or _t("точка другая", "the point is something else")
        if mine[0] == 'number':
            for L in lines:
                value = _param_at(L, truth)
                if value is not None and _vec_agree(mine[1], value, not loose):
                    return _t(f"это значение параметра, {_text(L.param)} = {_text(mine[1])}; вопрос "
                              f"спрашивает точку — подставьте его в прямую",
                              f"that is the value of the parameter, {_text(L.param)} = "
                              f"{_text(mine[1])}; the question asks for the point — put it into the line")
            return _t("ответ — точка (x, y, z)", "the answer is a point (x, y, z)")
        if mine[0] == 'none':
            return _t("общая точка есть: решите уравнения вместе", "there is a common point: solve the equations together")
        if mine[0] == 'line':
            return _line_not_in(mine[1], items, loose) or _t(
                "общая часть — одна точка, а не прямая", "they share a single point, not a line")
        return _t("общая часть — одна точка", "they share a single point")
    if isinstance(truth, _Line):
        if mine[0] == 'line':
            L = mine[1]
            if _is_zero_vector(L.direction):
                return _t("направление — нулевой вектор", "the direction is the zero vector")
            if _parallel(L.direction, truth.direction, loose) and _on(L.point, truth, loose):
                return None
            planes = [item for item in items if isinstance(item, _Plane)]
            for index, P in enumerate(planes):
                if _parallel(L.direction, P.normal, loose):
                    name = _called(P, items.index(P))
                    return _t(f"направление {_text(L.direction)} — нормаль плоскости {name}, а прямая "
                              f"лежит в {name}: её направление перпендикулярно этой нормали",
                              f"the direction {_text(L.direction)} is the normal of {name}, and the "
                              f"line lies in {name}: its direction is perpendicular to that normal")
            for index, item in enumerate(items):
                if isinstance(item, _Plane) and not _in_plane(L.point, item, loose):
                    return _not_on_words(L.point, item, _called(item, index))
            if not _parallel(L.direction, truth.direction, loose) and _one_sign(L.direction, truth.direction) is not None:
                return _sign_words(_one_sign(L.direction, truth.direction), 'direction')
            return _line_not_in(L, items, loose) or _t("прямая другая", "the line is something else")
        if mine[0] == 'point':
            where = _where_not(mine[1], items, loose)
            if where is None:
                return _t(f"{_text(mine[1])} лежит на всех, но общая часть — целая прямая через "
                          f"эту точку: запишите прямую, r = a + λb",
                          f"{_text(mine[1])} is on all of them, but they share a whole line "
                          f"through it: give the line, r = a + λb")
            return where
        if mine[0] == 'none':
            return _t("общие точки есть: из уравнений одно неизвестное остаётся свободным",
                      "there are common points: one unknown stays free in the equations")
        return _t("общая часть — прямая: vec(точка) + lam*vec(направление)",
                  "they share a line: vec(point) + lam*vec(direction)")
    # общая часть — целая плоскость
    if mine[0] == 'plane' and _same_plane(mine[1], truth, loose):
        return None
    return _t("это одна и та же плоскость", "these are one and the same plane")


# ------------------------------------------------------------ ответ-плоскость

def _four(P):
    return sp.Matrix(list(P.normal) + [P.constant])


def _same_plane(one, two, loose=False):
    return _parallel(_four(one), _four(two), loose)


def _parse_plane(got, exclude):
    """(плоскость, части векторной формы или None) либо (None, слова)."""
    if isinstance(got, _Plane):
        return got, None
    if isinstance(got, sp.Equality):
        found = _plane_from_equation(got)
        if found is None:
            return None, _t("уравнение плоскости — первой степени по x, y и z: Eq(2*x - 3*y - z, 6)",
                            "a plane's equation is linear in x, y and z: Eq(2*x - 3*y - z, 6)")
        return found, None
    vector = _as_vec(got)
    if vector is not None:
        candidates = [s for s in vector.free_symbols if s not in exclude]
        if len(vector) == 3 and len(candidates) == 2:
            params = sorted(candidates, key=str)
            b, c = vector.diff(params[0]), vector.diff(params[1])
            if not (b.free_symbols & set(params) or c.free_symbols & set(params)):
                if _is_zero_vector(cross(b, c)):
                    return None, _t(
                        f"направления {_text(b)} и {_text(c)} параллельны: они задают прямую, а не плоскость",
                        f"the directions {_text(b)} and {_text(c)} are parallel: they give a line, not a plane")
                parsed = _plane_from_vector(vector, params=params)
                parsed[0].params = params
                return parsed[0], parsed[1:]
    try:
        expr = sp.sympify(got)
        if expr.free_symbols & set(_axes()):
            return None, _t("это выражение, а плоскость — уравнение: Eq(2*x - 3*y - z, 6)",
                            "that is an expression, and a plane is an equation: Eq(2*x - 3*y - z, 6)")
    except (sp.SympifyError, TypeError):
        pass
    return None, _t("плоскость пишут Eq(a*x + b*y + c*z, d) или vec(точка) + lam*vec(...) + mu*vec(...)",
                    "a plane is written Eq(a*x + b*y + c*z, d) or vec(point) + lam*vec(...) + mu*vec(...)")


def _plane_slip(mine, theirs, pieces, loose):
    """Чем неверная плоскость отличается от нужной."""
    if pieces is not None:
        point, b, c = pieces
        if not _in_plane(point, theirs, loose):
            return _t(f"точка {_text(point)} не лежит в плоскости: {_plain(theirs.left())} даёт "
                      f"{_text(theirs.side(point))}, а не {_text(theirs.constant)}",
                      f"the point {_text(point)} is not on the plane: {_plain(theirs.left())} gives "
                      f"{_text(theirs.side(point))}, not {_text(theirs.constant)}")
        for d in (b, c):
            if not _plane_close(dot(d, theirs.normal), 0, loose, _scale(d, theirs.normal)):
                return _t(f"направление {_text(d)} не лежит в плоскости", f"the direction {_text(d)} does not lie in the plane")
    if _parallel(mine.normal, theirs.normal, loose):
        if _parallel(_four(mine), sp.Matrix(list(theirs.normal) + [-theirs.constant]), loose) and \
                sp.simplify(theirs.constant) != 0:
            return _t("знак у правой части не тот: d = n · a для точки a плоскости",
                      "the right-hand side has the wrong sign: d = n · a for a point a of the plane")
        for point in theirs.points or [theirs.some_point()]:
            if not _in_plane(point, mine, loose):
                return _t(f"нормаль верная, но это параллельная плоскость: {_text(point)} на ней не "
                          f"лежит — {_plain(mine.left())} даёт {_text(mine.side(point))}, а не "
                          f"{_text(mine.constant)}",
                          f"the normal is right, but this is a parallel plane: {_text(point)} is not on "
                          f"it — {_plain(mine.left())} gives {_text(mine.side(point))}, not "
                          f"{_text(mine.constant)}")
        return _t("нормаль верная, а правая часть — нет", "the normal is right, and the right-hand side is not")
    if theirs.crossed:
        flipped = _one_sign(mine.normal, theirs.normal)
        if flipped is not None:
            return _sign_words(flipped, 'normal')
    if _plane_close(dot(mine.normal, theirs.normal), 0, loose, _scale(mine.normal, theirs.normal)):
        return _t(f"вектор {_text(mine.normal)} лежит вдоль плоскости, а нормаль — поперёк неё",
                  f"the vector {_text(mine.normal)} lies along the plane, and a normal goes across it")
    for point in theirs.points:
        if not _in_plane(point, mine, loose):
            return _t(f"{_text(point)} не лежит на этой плоскости: {_plain(mine.left())} даёт "
                      f"{_text(mine.side(point))}, а не {_text(mine.constant)}",
                      f"{_text(point)} is not on this plane: {_plain(mine.left())} gives "
                      f"{_text(mine.side(point))}, not {_text(mine.constant)}")
    for d in theirs.directions:
        product = dot(d, mine.normal)
        if not _plane_close(product, 0, loose, _scale(d, mine.normal)):
            return _t(f"нормаль {_text(mine.normal)} не перпендикулярна направлению {_text(d)}: "
                      f"скалярное произведение {_text(product)}, а не 0",
                      f"the normal {_text(mine.normal)} is not perpendicular to the direction "
                      f"{_text(d)}: the scalar product is {_text(product)}, not 0")
    return _t("плоскость другая", "the plane is something else")


def verify_plane(label, got, P, free=None):
    """Ответ — плоскость: `Eq(2*x - 3*y - z, 6)` или `vec(3, 0, 0) + lam*vec(...) + mu*vec(...)`.

    Годится любое уравнение, кратное нужному, и векторная форма с любой точкой
    плоскости и любыми двумя непараллельными направлениями в ней. Проверка
    знает плоскость так, как её дал вопрос: `plane(A, B, C)`, `plane(L1, L2)`,
    `plane(R, P1, P2)`. Промахи: знак в векторном произведении, параллельная
    плоскость, знак правой части, вектор вдоль плоскости вместо нормали.
    """
    if _blank(label, got):
        return False
    letters = P.letters
    mine, pieces = _parse_plane(got, letters)
    if mine is None:
        print(f"{NO} {label}: {pieces}")
        return False
    if _is_zero_vector(mine.normal):
        print(f"{NO} {label}: " + _t("в уравнении нет x, y и z", "the equation has no x, y or z"))
        return False
    loose = _has_float(got)
    for run in _vec_runs(letters | (mine.letters - letters), free):
        one, two = mine.subs(run), P.subs(run)
        parts = None if pieces is None else tuple(p.subs(run) for p in pieces)
        if _same_plane(one, two, loose):
            continue
        print(f"{NO} {label}: " + _plane_slip(one, two, parts, loose) + _at_words(run))
        return False
    if pieces is None:
        print(f"{OK} {label}: {mine!r}")
    else:
        point, b, c = pieces
        one, two = (_text(s) for s in mine.params)
        print(f"{OK} {label}: r = {_text(point)} + {one}{_text(b)} + {two}{_text(c)}")
    return True


def verify_normal_vector(label, got, P, free=None):
    """Ответ — нормаль плоскости: любой ненулевой вектор, кратный нужному."""
    if _blank(label, got):
        return False
    mine = _as_vec(got)
    if mine is None or len(mine) != 3:
        print(f"{NO} {label}: " + _t("нормаль — вектор из трёх чисел", "a normal is a vector of three numbers"))
        return False
    if _is_zero_vector(mine):
        print(f"{NO} {label}: " + _t("нулевой вектор нормалью не бывает", "the zero vector is not a normal"))
        return False
    loose = _has_float(got)
    for run in _vec_runs(P.letters, free):
        vector, Q = mine.subs(run), P.subs(run)
        if _parallel(vector, Q.normal, loose):
            continue
        print(f"{NO} {label}: " + _normal_slip(vector, Q, loose) + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(mine)}")
    return True


def _normal_slip(vector, P, loose):
    if P.crossed:
        flipped = _one_sign(vector, P.normal)
        if flipped is not None:
            return _sign_words(flipped, 'normal')
    if _plane_close(dot(vector, P.normal), 0, loose, _scale(vector, P.normal)):
        return _t(f"вектор {_text(vector)} лежит в плоскости; нормаль перпендикулярна каждому "
                  f"направлению в ней",
                  f"the vector {_text(vector)} lies in the plane; a normal is perpendicular to every "
                  f"direction in it")
    for point in P.points:
        if _parallel(vector, point, loose):
            return _t("это радиус-вектор точки плоскости, а не нормаль",
                      "that is the position vector of a point in the plane, not a normal")
    for d in P.directions:
        product = dot(vector, d)
        if not _plane_close(product, 0, loose, _scale(vector, d)):
            return _t(f"не перпендикулярен направлению {_text(d)}: скалярное произведение "
                      f"{_text(product)}, а не 0",
                      f"not perpendicular to the direction {_text(d)}: the scalar product is "
                      f"{_text(product)}, not 0")
    return _t("вектор не перпендикулярен плоскости", "the vector is not perpendicular to the plane")


def verify_direction(label, got, L, free=None):
    """Ответ — направление прямой: любой ненулевой кратный вектор.

    Для прямой пересечения двух плоскостей, `intersection(P1, P2)`, промах
    «нормаль одной из плоскостей» называется отдельно.
    """
    if _blank(label, got):
        return False
    mine = _as_vec(got)
    if mine is None or len(mine) != len(L.direction):
        print(f"{NO} {label}: " + _t(f"направление — вектор из {len(L.direction)} чисел",
                                     f"a direction is a vector of {len(L.direction)} numbers"))
        return False
    if _is_zero_vector(mine):
        print(f"{NO} {label}: " + _t("нулевой вектор направлением не бывает", "the zero vector is not a direction"))
        return False
    loose = _has_float(got)
    planes = L.extra.get('planes', [])
    for run in _vec_runs(L.letters, free):
        vector, line_now = mine.subs(run), L.subs(run)
        if _parallel(vector, line_now.direction, loose):
            continue
        message = None
        for index, P in enumerate(planes):
            Q = P.subs(run)
            if _parallel(vector, Q.normal, loose):
                name = _called(Q, index)
                message = _t(f"это нормаль плоскости {name}; прямая лежит в {name}, и её направление "
                             f"перпендикулярно этой нормали",
                             f"that is the normal of {name}; the line lies in {name}, and its direction "
                             f"is perpendicular to that normal")
                break
        if message is None and planes and _one_sign(vector, line_now.direction) is not None:
            message = _sign_words(_one_sign(vector, line_now.direction), 'direction')
        if message is None:
            for index, P in enumerate(planes):
                Q = P.subs(run)
                product = dot(vector, Q.normal)
                if not _plane_close(product, 0, loose, _scale(vector, Q.normal)):
                    name = _called(Q, index)
                    message = _t(f"направление не лежит в плоскости {name}: скалярное произведение с "
                                 f"нормалью {_text(Q.normal)} равно {_text(product)}, а не 0",
                                 f"the direction does not lie in {name}: its scalar product with the "
                                 f"normal {_text(Q.normal)} is {_text(product)}, not 0")
                    break
        print(f"{NO} {label}: " + (message or _t("вектор идёт не вдоль прямой",
                                                 "the vector does not run along the line")) + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(mine)}")
    return True


# ------------------------------------------------------------ расстояние

def _distance_parts(first, second):
    """(плоскость, точка) для расстояния; точка — у второй плоскости или прямой."""
    if isinstance(second, _Plane) and not isinstance(first, _Plane):
        first, second = second, first
    if not isinstance(first, _Plane):
        raise ValueError('distance: a plane and a point, a parallel line or a parallel plane')
    if isinstance(second, _Plane):
        if not _parallel(first.normal, second.normal):
            return first, None
        return first, second.some_point()
    if isinstance(second, _Line):
        if sp.simplify(dot(second.direction, first.normal)) != 0:
            return first, None
        return first, second.point
    return first, _as_vec(second)


def _plane_distance(first, second):
    P, point = _distance_parts(first, second)
    if point is None:
        return sp.Integer(0)
    return sp.Abs(P.gap(point)) / mag(P.normal)


def verify_distance(label, got, first, second, exact=False):
    """Ответ — расстояние от точки до плоскости, между параллельными плоскостями
    или от параллельной прямой до плоскости.

    Промахи: |n·a − d| без деления на |n|, параметр основания вместо
    расстояния, расстояние от начала координат, расстояние до отражения.
    """
    if _blank(label, got):
        return False
    P, point = _distance_parts(first, second)
    want = _plane_distance(first, second)
    value = _vec_number(got)
    if value is None:
        print(f"{NO} {label}: " + _t("ответ — число", "the answer is a number"))
        return False
    if exact and _has_float(got):
        print(f"{NO} {label}: " + _t("вопрос просит точное значение, а это десятичная дробь",
                                     "the question asks for the exact value, and this is a decimal"))
        return False
    if _vec_agree(got, want, exact or not _has_float(got)):
        print(f"{OK} {label}: {_text(got)}")
        return True
    message = None
    if point is None:
        message = _t("они не параллельны и пересекаются: расстояние между ними ноль",
                     "they are not parallel, so they meet: the distance between them is 0")
    else:
        raw = sp.Abs(P.gap(point))
        size = mag(P.normal)
        tries = [
            (raw, _t(f"не поделено на длину нормали: расстояние — |n·a − d|/|n|, и |n| = {_text(size)}",
                     f"the length of the normal is not divided out: the distance is |n·a − d|/|n|, "
                     f"and |n| = {_text(size)}")),
            (raw / size ** 2, _t("это параметр основания перпендикуляра; расстояние — |λ|·|n|",
                                 "that is the parameter of the foot of the perpendicular; the distance "
                                 "is |λ|·|n|")),
            (2 * want, _t("это вдвое больше: расстояние до отражения, а не до плоскости",
                          "that is twice the distance: to the reflection, not to the plane")),
            (mag(point), _t("это расстояние от начала координат до точки",
                            "that is the distance of the point from the origin")),
            (sp.Abs(P.constant) / size, _t("это расстояние от начала координат до плоскости",
                                           "that is the distance of the plane from the origin")),
        ]
        for candidate, words in tries:
            if sp.simplify(candidate - want) != 0 and _vec_agree(got, candidate):
                message = words
                break
    print(f"{NO} {label}: " + (message or _generic_slip(got, want)
                               or _t("расстояние другое", "the distance is something else")))
    return False


# ------------------------------------------------------------ условия с плоскостями

def _direction_or_normal(item):
    if isinstance(item, _Plane):
        return item.normal
    if isinstance(item, _Line):
        return item.direction
    return _as_vec(item)


def _plane_on_fact(point, P):
    vector = _as_vec(point)
    name = P.name or _t('плоскость', 'the plane')

    def words(run):
        return _not_on_words(vector.subs(run), P.subs(run), name)
    return _Fact([P.gap(vector)], words=words)


def _plane_pair_fact(one, two, kind):
    """parallel и perpendicular, когда хотя бы одна сторона — плоскость."""
    planes = [item for item in (one, two) if isinstance(item, _Plane)]
    u, v = _direction_or_normal(one), _direction_or_normal(two)
    both = len(planes) == 2
    # вектор или прямая ⟂ плоскости — параллельны нормали; ∥ плоскости — перпендикулярны ей
    along = (kind == 'parallel') == both

    def words(run):
        uu, vv = u.subs(run), v.subs(run)
        if along:
            if both:
                return _t(f"нормали {_text(uu)} и {_text(vv)} не кратны: плоскости не параллельны",
                          f"the normals {_text(uu)} and {_text(vv)} are not multiples: the planes are "
                          f"not parallel")
            return _t(f"{_text(uu if not isinstance(one, _Plane) else vv)} не кратен нормали "
                      f"{_text(vv if not isinstance(one, _Plane) else uu)}: не перпендикулярен плоскости",
                      f"{_text(uu if not isinstance(one, _Plane) else vv)} is not a multiple of the normal "
                      f"{_text(vv if not isinstance(one, _Plane) else uu)}: not perpendicular to the plane")
        product = _text(dot(uu, vv))
        if both:
            return _t(f"плоскости не перпендикулярны: скалярное произведение нормалей {product}, а не 0",
                      f"the planes are not perpendicular: the scalar product of the normals is {product}, not 0")
        return _t(f"не параллельно плоскости: скалярное произведение с нормалью {product}, а не 0",
                  f"not parallel to the plane: the scalar product with the normal is {product}, not 0")
    return _Fact(_minors(u, v) if along else [dot(u, v)], words=words)


def _augmented(planes):
    return sp.Matrix([list(P.normal) + [P.constant] for P in planes])


def _arrangement_words(planes):
    found = intersection(*planes)
    if found is None:
        return _t("у плоскостей нет общей точки", "the planes have no common point")
    if isinstance(found, sp.MatrixBase):
        return _t(f"плоскости сходятся в одной точке {_text(found)}",
                  f"the planes meet at the single point {_text(found)}")
    if isinstance(found, _Line):
        return _t("плоскости пересекаются по прямой", "the planes meet in a line")
    return _t("это одна плоскость", "they are one plane")


def _plane_meet_fact(objects):
    """Есть общая точка: координаты X — свежие параметры."""
    X = sp.Matrix([sp.Dummy('mx'), sp.Dummy('my'), sp.Dummy('mz')])
    equations, params = [], list(X)
    for item in objects:
        if isinstance(item, _Plane):
            equations.append(item.gap(X))
        else:
            s = sp.Dummy('s')
            params.append(s)
            equations += list(X - item.at(s))
    return _Fact(equations, params=params, words=lambda run: _t(
        "при этих значениях общей точки нет", "with these values there is no common point"))


def meet_in_line(*planes):
    """Условие: плоскости пересекаются по прямой — «infinitely many solutions»."""
    if len(planes) < 2 or not all(isinstance(P, _Plane) for P in planes):
        raise ValueError('meet_in_line: two or more planes')
    full = _augmented(planes)
    normals = full[:, :3]
    equations = []
    if len(planes) >= 3:
        for rows in _combinations(range(len(planes)), 3):
            for cols in _combinations(range(4), 3):
                equations.append(sp.expand(full.extract(list(rows), list(cols)).det()))
    loose_rank = [sp.expand(m) for m in _two_minors(normals)]

    def words(run):
        return _arrangement_words([P.subs(run) for P in planes])
    fact = _Fact(equations, words=words)
    fact.filters = [sp.Ne(sp.Add(*[m ** 2 for m in loose_rank]), 0)] if loose_rank else []
    return fact


def _combinations(items, size):
    return list(combinations(list(items), size))


def _two_minors(matrix):
    out = []
    for rows in _combinations(range(matrix.rows), 2):
        for cols in _combinations(range(matrix.cols), 2):
            out.append(matrix.extract(list(rows), list(cols)).det())
    return out


def _plane_no_unique(objects):
    planes = [item for item in objects if isinstance(item, _Plane)]
    if len(planes) != 3 or len(planes) != len(objects):
        raise ValueError('no_unique_meet: three planes')
    normals = sp.Matrix([list(P.normal) for P in planes])

    def words(run):
        return _arrangement_words([P.subs(run) for P in planes])
    return _Fact([sp.expand(normals.det())], words=words)


def reflection(image, point, P):
    """Условие: image — отражение point в плоскости P."""
    B2, B = _as_vec(image), _as_vec(point)
    middle = (B + B2) / 2

    def words(run):
        one, two, Q = B2.subs(run), B.subs(run), P.subs(run)
        foot = mirror(two, Q, half=True)
        if _agree_vec(one, foot, not _has_float(one)):
            return _t(f"это основание перпендикуляра {_text(foot)}, где прямая через точку "
                      f"встречает плоскость; отражение — ещё столько же за ним",
                      f"that is the foot of the perpendicular {_text(foot)}, where the line through "
                      f"the point meets the plane; the reflection is as far again beyond it")
        if _agree_vec(one, two, True):
            return _t("это сама точка, а не её отражение", "that is the point itself, not its reflection")
        halfway = (one + two) / 2
        if not _in_plane(halfway, Q, _has_float(one)):
            return _t(f"середина между точкой и отражением, {_text(halfway)}, не лежит в плоскости: "
                      f"{_plain(Q.left())} даёт {_text(Q.side(halfway))}, а не {_text(Q.constant)}",
                      f"halfway between the point and its image, {_text(halfway)}, is not on the "
                      f"plane: {_plain(Q.left())} gives {_text(Q.side(halfway))}, not {_text(Q.constant)}")
        return _t("отрезок от точки до отражения не перпендикулярен плоскости",
                  "the segment from the point to its image is not perpendicular to the plane")
    return _Fact([P.gap(middle)] + _minors(B2 - B, P.normal), words=words)


def mirror(item, P, half=False):
    """Отражение точки или прямой в плоскости; half=True — основание перпендикуляра."""
    if isinstance(item, _Line):
        one, two = mirror(item.point, P), mirror(item.point + item.direction, P)
        image = _Line(one, two - one, item.param, item.name)
        image.extra['mirrored'] = item
        return image
    point = _as_vec(item)
    step = (P.constant - P.side(point)) / dot(P.normal, P.normal)
    return point + (1 if half else 2) * step * P.normal
