"""Измерения в пространстве (C7): векторное произведение и то, что оно меряет.
"""

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .vectors import (
    _Line, _agree_vec, _as_vec, _direction, _generic_slip, _has_float, _letters_of,
    _subs, _text, _vec_agree, _vec_number, _vec_runs, _at_words, angle, dot, mag,
)
from .planes import _Plane, _sign_words, cross


# ================================================================ измерения
# Двадцать шестое понятие равенства ответов: **величина меряется фигурой, а не
# формулой**. Площадь треугольника — половина длины векторного произведения
# его рёбер, объём пирамиды — шестая часть определителя, расстояние до прямой
# — длина перпендикуляра к ней; какой формулой это получено, проверке
# безразлично, и в ячейке стоит сама фигура из билета.
#
# Само векторное произведение, в отличие от нормали плоскости, множителем не
# задано: у него своя длина |u||v| sin θ и своё направление. Поэтому
# verify_cross требует вектор целиком, а verify_normal_vector (C6) —
# с точностью до множителя.


def _as_point(value, what):
    vector = _as_vec(value)
    if vector is None or len(vector) != 3:
        raise ValueError(f'{what}: points with three coordinates')
    return vector


# ----------------------------------------------------- векторное произведение

def _cross_slip(mine, u, v, want):
    """Промахи в векторном произведении: порядок, знак компоненты, не тот продукт."""
    if _agree_vec(mine, -want):
        return _t("это v × u: у векторного произведения от перестановки множителей "
                  "меняется знак",
                  "that is v × u: swapping the factors of a vector product changes its sign")
    for i in range(3):
        flipped = sp.Matrix(want)
        flipped[i] = -flipped[i]
        if flipped[i] != 0 and _agree_vec(mine, flipped):
            return _sign_words(i, 'product')
    if _agree_vec(mine, sp.Matrix([u[i] * v[i] for i in range(3)])):
        return _t("компоненты перемножены по отдельности; у векторного произведения "
                  "каждая компонента — разность двух произведений",
                  "the components have been multiplied one by one; in a vector product each "
                  "component is a difference of two products")
    vector = _as_vec(mine)
    if vector is not None and len(vector) == 3 and any(vector):
        if sp.simplify(dot(vector, u)) != 0 or sp.simplify(dot(vector, v)) != 0:
            first = 'u' if sp.simplify(dot(vector, u)) != 0 else 'v'
            return _t(f"этот вектор не перпендикулярен {first}: скалярное произведение с ним "
                      f"не ноль, а у u × v оно ноль с обоими",
                      f"this vector is not perpendicular to {first}: its scalar product with it "
                      f"is not zero, and u × v has zero with both")
        if _vec_agree(mag(vector) * mag(want), dot(vector, want)) and \
                not _vec_agree(mag(vector), mag(want)):
            return _t("направление верное, а длина нет: |u × v| = |u||v| sin θ, и множителем "
                      "векторное произведение не задано",
                      "the direction is right and the length is not: |u × v| = |u||v| sin θ, and "
                      "a vector product is not fixed only up to a factor")
    return None


def verify_cross(label, got, u, v, free=None):
    """Ответ — векторное произведение u × v, вектор целиком.

    Промахи: v × u, знак средней компоненты, скалярное произведение,
    покомпонентное умножение, вектор не перпендикулярен множителям.
    """
    if _blank(label, got):
        return False
    for run in _vec_runs(_letters_of(u, v), free):
        one, two = _subs(u, run), _subs(v, run)
        want = cross(one, two)
        mine = _subs(got, run)
        if _as_vec(mine) is None or len(_as_vec(mine)) != 3:
            words = _t("ответ — вектор из трёх чисел",
                       "the answer is a vector of three numbers")
            if _vec_number(mine) is not None and _vec_agree(mine, dot(one, two)):
                words = _t("это скалярное произведение, число; векторное — вектор",
                           "that is the scalar product, a number; a vector product is a vector")
            print(f"{NO} {label}: {words}" + _at_words(run))
            return False
        if _agree_vec(mine, want):
            continue
        message = _cross_slip(_as_vec(mine), one, two, want) or \
            _t("это не u × v", "that is not u × v")
        print(f"{NO} {label}: {message}" + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


# ------------------------------------------------------- площадь и объём

_FIGURES = {'triangle': 3, 'parallelogram': 4, 'pyramid': 4}


def _figure_edges(kind, points):
    """Рёбра фигуры из одной вершины: у пирамиды — из вершины, у остальных — из первой."""
    if kind not in _FIGURES:
        known = ', '.join(sorted(_FIGURES))
        raise ValueError(f'measure: the figure is one of {known}')
    if len(points) != _FIGURES[kind]:
        raise ValueError(f'measure: {kind} takes {_FIGURES[kind]} points')
    corners = [_as_point(p, 'measure') for p in points]
    if kind == 'pyramid':
        apex, base = corners[0], corners[1:]
        return [p - apex for p in base]
    if kind == 'triangle':
        return [corners[1] - corners[0], corners[2] - corners[0]]
    return [corners[1] - corners[0], corners[3] - corners[0]]


def measure(kind, *points):
    """Площадь треугольника или параллелограмма, объём пирамиды — по вершинам.

    `measure('triangle', A, B, C)` — половина |AB × AC|;
    `measure('parallelogram', A, B, C, D)` — |AB × AD|, стороны от вершины A;
    `measure('pyramid', S, P, Q, R)` — шестая часть определителя рёбер из S.
    """
    edges = _figure_edges(kind, points)
    if kind == 'pyramid':
        return sp.Abs(sp.Matrix([list(e) for e in edges]).det()) / 6
    size = mag(cross(edges[0], edges[1]))
    return size / 2 if kind == 'triangle' else size


def _measure_words(kind):
    return {'triangle': _t('площадь', 'the area'),
            'parallelogram': _t('площадь', 'the area'),
            'pyramid': _t('объём', 'the volume')}[kind]


def _measure_slips(kind, edges, want):
    """Промахи меры: пропущенный множитель, не то произведение, не та часть фигуры."""
    slips = []
    if kind == 'pyramid':
        base = mag(cross(edges[1] - edges[0], edges[2] - edges[0])) / 2
        slips += [
            (6 * want, _t("это объём параллелепипеда на тех же трёх рёбрах; пирамида — "
                          "его шестая часть",
                          "that is the volume of the parallelepiped on the same three edges; "
                          "a pyramid is a sixth of it")),
            (3 * want, _t("не поделено на три: пирамида — треть призмы с тем же основанием",
                          "the third is missing: a pyramid is a third of the prism on the same base")),
            (2 * want, _t("основание — треугольник, и его площадь вдвое меньше",
                          "the base is a triangle, and its area is half of that")),
            (base, _t("это площадь основания, а вопрос просит объём",
                      "that is the area of the base, and the question asks for the volume")),
        ]
        return slips
    u, v = edges
    whole = mag(cross(u, v))
    slips.append((sp.Abs(dot(u, v)), _t(
        "это скалярное произведение рёбер; площадь считается векторным",
        "that is the scalar product of the edges; the area comes from the vector product")))
    slips.append((mag(u) * mag(v) / (2 if kind == 'triangle' else 1), _t(
        "это |u||v|: столько было бы у прямого угла между рёбрами, а вообще "
        "площадь — |u × v| = |u||v| sin θ",
        "that is |u||v|: it would be the answer for a right angle between the edges, and in "
        "general the area is |u × v| = |u||v| sin θ")))
    slips.append((whole ** 2 / (4 if kind == 'triangle' else 1), _t(
        "это квадрат: не извлечён корень из суммы квадратов компонент",
        "that is the square: the root of the sum of squares is missing")))
    if kind == 'triangle':
        slips.append((2 * want, _t(
            "половина забыта: треугольник — половина параллелограмма на тех же рёбрах",
            "the half is missing: a triangle is half the parallelogram on the same edges")))
    else:
        slips.append((want / 2, _t(
            "это треугольник на двух сторонах; параллелограмм вдвое больше",
            "that is the triangle on the two sides; the parallelogram is twice it")))
    return slips


def verify_measure(label, got, kind, *points, exact=False, free=None):
    """Ответ — площадь треугольника или параллелограмма, объём пирамиды.

    Фигура передаётся вершинами, как её называет вопрос:
    `verify_measure('4', q4, 'triangle', P, Q, R)`. Проверка меряет её сама.
    """
    if _blank(label, got):
        return False
    what = _measure_words(kind)
    for run in _vec_runs(_letters_of(points), free):
        corners = [_subs(p, run) for p in points]
        edges = _figure_edges(kind, corners)
        want = measure(kind, *corners)
        mine = _subs(got, run)
        if _vec_number(mine) is None:
            print(f"{NO} {label}: " + _t(f"{what} — это число", f"{what} is a number")
                  + _at_words(run))
            return False
        if exact and _has_float(got):
            print(f"{NO} {label}: " + _t("вопрос просит точное значение, а это десятичная дробь",
                                         "the question asks for the exact value, and this is a decimal"))
            return False
        if kind == 'parallelogram' and \
                sp.simplify(sp.Matrix(corners[1] - corners[0]) - (corners[2] - corners[3])) != \
                sp.zeros(3, 1):
            print(f"{NO} {label}: " + _t("вершины даны не по кругу: в параллелограмме ABCD "
                                         "AB = DC",
                                         "the vertices are not in order: in a parallelogram ABCD "
                                         "AB = DC") + _at_words(run))
            return False
        if _vec_agree(mine, want, exact):
            continue
        message = None
        for candidate, words in _measure_slips(kind, edges, want):
            if sp.simplify(candidate - want) != 0 and _vec_agree(mine, candidate):
                message = words
                break
        print(f"{NO} {label}: " + (message or _generic_slip(mine, want)
                                   or _t(f"у фигуры из условия {what} другая",
                                         f"the figure in the question does not measure that"))
              + _at_words(run))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


# ------------------------------------------------------------ дуга на сфере

def verify_arc(label, got, radius, u, v, exact=False):
    """Ответ — кратчайший путь по сфере: дуга большого круга между u и v.

    `verify_arc('e', q, 6, b, m)` — радиус и два направления из центра.
    Проверка сама берёт центральный угол; промахи: сам угол, угол в
    градусах, хорда вместо дуги.
    """
    if _blank(label, got):
        return False
    size = sp.sympify(radius)
    central = angle(u, v)
    want = size * central
    if _vec_number(got) is None:
        print(f"{NO} {label}: " + _t("длина дуги — это число", "an arc length is a number"))
        return False
    if exact and _has_float(got):
        print(f"{NO} {label}: " + _t("вопрос просит точное значение, а это десятичная дробь",
                                     "the question asks for the exact value, and this is a decimal"))
        return False
    if _vec_agree(got, want, exact or not _has_float(got)):
        print(f"{OK} {label}: {_text(got)}")
        return True
    chord = mag(_as_vec(v) - _as_vec(u))
    tries = [
        (central, _t("это сам центральный угол; дуга — rθ, и на радиус надо умножить",
                     "that is the central angle itself; an arc is rθ, and the radius still has "
                     "to multiply it")),
        (central * 180 / sp.pi, _t("это центральный угол в градусах",
                                   "that is the central angle in degrees")),
        (size * central * 180 / sp.pi, _t("угол подставлен в градусах, а в rθ он обязан быть "
                                          "в радианах",
                                          "the angle went in as degrees, and rθ needs radians")),
        (chord, _t("это хорда — прямой отрезок сквозь шар, а путь идёт по поверхности",
                   "that is the chord, a straight segment through the ball, and the path goes "
                   "along the surface")),
    ]
    message = None
    for candidate, words in tries:
        if sp.simplify(candidate - want) != 0 and _vec_agree(got, candidate):
            message = words
            break
    print(f"{NO} {label}: " + (message or _generic_slip(got, want)
                               or _t("длина дуги другая", "the arc length is something else")))
    return False


# --------------------------------------------- величина через длины и угол

def _formula_runs(letters, count=4):
    """Наборы чисел для букв символических векторов: целые, не слишком мелкие."""
    names = sorted(letters, key=str)
    seeds = [3, -2, 5, 1, -4, 2, 7, -1, 6, -3, 4, -5]
    runs = []
    for i in range(count):
        runs.append({name: sp.Integer(seeds[(i * 5 + j * 3) % len(seeds)])
                     for j, name in enumerate(names)})
    return runs


def verify_formula(label, got, target, letters, samples=4):
    """Ответ — та же величина, записанная через длины и угол.

    `letters` — что означает каждая буква ответа: `{A: mag(a), B: mag(b), th: angle(a, b)}`
    на символических векторах a и b. Проверка подставляет в них числа и
    сравнивает ответ с самой величиной; годится любая эквивалентная запись.
    """
    if _blank(label, got):
        return False
    free = set()
    for value in letters.values():
        free |= _letters_of(value)
    free |= _letters_of(target)
    free -= set(letters)
    mine = sp.sympify(got)
    if mine.free_symbols - set(letters):
        extra = ', '.join(sorted(str(s) for s in mine.free_symbols - set(letters)))
        print(f"{NO} {label}: " + _t(f"ответ записан через {extra}, а вопрос просит запись через "
                                     f"длины и угол",
                                     f"the answer uses {extra}, and the question asks for lengths "
                                     f"and the angle"))
        return False
    swapped = None
    for run in _formula_runs(free, samples):
        want = sp.sympify(_subs(target, run)).evalf(30)
        values = {name: sp.sympify(_subs(value, run)).evalf(30) for name, value in letters.items()}
        here = mine.subs(values).evalf(30)
        if _vec_agree(here, want, exact=True):
            continue
        if swapped is None:
            angles = [name for name, value in letters.items()
                      if isinstance(_subs(value, run), sp.Expr) and _subs(value, run).has(sp.acos)]
            swapped = angles[0] if angles else False
        if swapped:
            other = dict(values)
            other[swapped] = (sp.pi / 2 - values[swapped]).evalf(30)
            if _vec_agree(mine.subs(other).evalf(30), want, exact=True):
                print(f"{NO} {label}: " + _t(
                    "синус и косинус поменялись местами: у скалярного произведения косинус, "
                    "у векторного синус",
                    "the sine and the cosine have swapped: the scalar product has the cosine and "
                    "the vector product the sine"))
                return False
        if _vec_agree(here ** 2, want, exact=True):
            print(f"{NO} {label}: " + _t("это сама величина, а вопрос просит её квадрат",
                                         "that is the quantity itself, and the question asks "
                                         "for its square"))
            return False
        if _vec_agree(here, -want, exact=True):
            print(f"{NO} {label}: " + _t("знак не тот", "the sign is the other way"))
            return False
        here, want = sig(float(here), 8), sig(float(want), 8)
        print(f"{NO} {label}: " + _t(
            f"при числах это даёт {here}, а величина равна {want}",
            f"with numbers this gives {here}, and the quantity is {want}"))
        return False
    print(f"{OK} {label}: {_text(got)}")
    return True


# ------------------------------------------------------- углы с плоскостью

def _space_angle_parts(objects):
    """(u, v, острый, вид, что) для угла с плоскостью — зовёт verify_angle."""
    if len(objects) != 2:
        raise ValueError('verify_angle: a plane goes with a line, a vector or another plane')
    first, second = objects
    if isinstance(first, _Plane) and isinstance(second, _Plane):
        return first.normal, second.normal, True, 'planes', (first, second)
    P = first if isinstance(first, _Plane) else second
    other = second if isinstance(first, _Plane) else first
    return _direction(other), P.normal, True, 'line_plane', (other, P)


def _space_angle_value(u, v):
    """Угол прямой с плоскостью: дополнение до прямого угла с нормалью."""
    return sp.asin(sp.Abs(dot(u, v)) / (mag(u) * mag(v)))


def _space_angle_words(kind, value, here, unit):
    """Промахи угла с плоскостью: угол с нормалью, тупой угол между нормалями."""
    if kind == 'line_plane' and abs(value - (unit / 2 - here)) < 5e-3 * max(1.0, abs(here)):
        return _t("это угол прямой с нормалью; угол с плоскостью — то, что осталось "
                  "до прямого угла",
                  "that is the angle between the line and the normal; the angle with the plane "
                  "is what is left of a right angle")
    if kind == 'planes' and abs(value - (unit - here)) < 5e-3 * max(1.0, abs(here)):
        return _t("это тупой угол между нормалями; острый угол между плоскостями — 180° − θ",
                  "that is the obtuse angle between the normals; the acute angle between the "
                  "planes is 180° − θ")
    return None


# ----------------------------------------------------- расстояния до прямой

def _line_parts(first, second):
    """(прямая, вторая прямая или точка) — расстояние всегда меряется от прямой."""
    if isinstance(second, _Line) and not isinstance(first, _Line):
        first, second = second, first
    if not isinstance(first, _Line):
        raise ValueError('distance: a line and a point, or two lines')
    return first, second


def _line_distance(first, second):
    """Расстояние от точки до прямой или между двумя прямыми."""
    L, other = _line_parts(first, second)
    if not isinstance(other, _Line):
        gap = _as_point(other, 'distance') - L.point
        return mag(cross(gap, L.direction)) / mag(L.direction)
    gap = other.point - L.point
    normal = cross(L.direction, other.direction)
    if all(sp.simplify(c) == 0 for c in normal):        # параллельны
        return mag(cross(gap, L.direction)) / mag(L.direction)
    return sp.Abs(dot(gap, normal)) / mag(normal)


def _line_distance_slips(L, other, want):
    """Промахи расстояния до прямой: без деления, не тот отрезок, длина проекции."""
    slips = []
    if isinstance(other, _Line):
        gap = other.point - L.point
        parallel = all(sp.simplify(c) == 0 for c in cross(L.direction, other.direction))
        slips.append((mag(gap), _t(
            "это расстояние между двумя выбранными точками, а не между прямыми: "
            "кратчайший отрезок перпендикулярен обеим",
            "that is the distance between the two points you picked, not between the lines: "
            "the shortest segment is perpendicular to both")))
        if parallel:
            for direction in (L.direction, other.direction):
                slips.append((mag(cross(gap, direction)), _t(
                    "не поделено на длину направления: расстояние — |AB × d|/|d|",
                    "the length of the direction is not divided out: the distance is "
                    "|AB × d|/|d|")))
        else:
            slips.append((sp.Abs(dot(gap, cross(L.direction, other.direction))), _t(
                "не поделено на |d₁ × d₂|: расстояние — |AB · (d₁ × d₂)|/|d₁ × d₂|",
                "|d₁ × d₂| is not divided out: the distance is |AB · (d₁ × d₂)|/|d₁ × d₂|")))
        return slips
    point = _as_point(other, 'distance')
    gap = point - L.point
    slips.append((mag(gap), _t(
        "это расстояние до точки прямой из её уравнения, а кратчайшее — по перпендикуляру",
        "that is the distance to the point of the line written in its equation, and the "
        "shortest one goes along the perpendicular")))
    slips.append((mag(cross(gap, L.direction)), _t(
        "не поделено на длину направления: расстояние — |AP × d|/|d|",
        "the length of the direction is not divided out: the distance is |AP × d|/|d|")))
    slips.append((sp.Abs(dot(gap, L.direction)) / mag(L.direction), _t(
        "это длина проекции на прямую, а не расстояние до неё: они — два катета",
        "that is the length of the projection onto the line, not the distance to it: the two "
        "are the legs of a right angle")))
    slips.append((mag(point), _t("это расстояние от начала координат до точки",
                                 "that is the distance of the point from the origin")))
    return slips


def _verify_line_distance(label, got, first, second, exact=False):
    """Ответ — кратчайшее расстояние до прямой; зовётся из verify_distance."""
    L, other = _line_parts(first, second)
    want = _line_distance(L, other)
    mine = _vec_number(got)
    if mine is None:
        print(f"{NO} {label}: " + _t("расстояние — это число", "a distance is a number"))
        return False
    if exact and _has_float(got):
        print(f"{NO} {label}: " + _t("вопрос просит точное значение, а это десятичная дробь",
                                     "the question asks for the exact value, and this is a decimal"))
        return False
    if _vec_agree(got, want, exact or not _has_float(got)):
        print(f"{OK} {label}: {_text(got)}")
        return True
    if isinstance(other, _Line) and sp.simplify(want) == 0:
        print(f"{NO} {label}: " + _t("прямые пересекаются, и расстояние между ними ноль",
                                     "the lines meet, so the distance between them is 0"))
        return False
    message = None
    for candidate, words in _line_distance_slips(L, other, want):
        if sp.simplify(candidate - want) != 0 and _vec_agree(got, candidate):
            message = words
            break
    print(f"{NO} {label}: " + (message or _generic_slip(got, want)
                               or _t("расстояние другое", "the distance is something else")))
    return False
