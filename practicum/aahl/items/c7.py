"""Задачи на счёт для практикума C7: чем и как в пространстве меряют.

Генераторы идут по лестнице карточки: само векторное произведение;
площадь треугольника и параллелограмма; объём пирамиды; тождество
|u × v|² = |u|²|v|² − (u · v)², из которого достаётся длина; углы с
плоскостью и дуга на сфере; ближайшая точка прямой; расстояние до
прямой и между параллельными прямыми.

Проверки эталона не хранят. `vector_check` отдаёт странице вершины
фигуры, нормали и направления, и страница зовёт те же verify_cross,
verify_measure, verify_angle, verify_arc, verify_find и verify_distance,
что стоят в ноутбуке: площадь, объём, угол и расстояние проверка меряет
сама, а длину из тождества и ближайшую точку — находит. Эталон в задании
только для показа после попытки; считает его здесь целочисленная
арифметика, построенная от ответа к условию.
"""
from __future__ import annotations

import math

import sympy as sp

from .common import vector_check

R = sp.Rational

# Тройки для тождества: d² + c² = (ab)², где d = u · v и c = |u × v|.
# Произведение длин составное: и |u|, и |v| должны выйти больше единицы,
# иначе «квадрат вместо длины» перестаёт быть ошибкой.
_TRIPLES = ((6, 8, 10), (9, 12, 15), (12, 16, 20), (15, 20, 25), (7, 24, 25),
            (10, 24, 26), (18, 24, 30), (16, 30, 34))


def _v(values):
    return '(' + ', '.join(sp.sstr(sp.sympify(v)) for v in values) + ')'


def _tex(values):
    return r'\begin{pmatrix}' + r'\\'.join(sp.latex(sp.sympify(v)) for v in values) + r'\end{pmatrix}'


def _point(rng, low=-5, high=5):
    return [rng.randint(low, high) for _ in range(3)]


def _direction(rng, low=-4, high=4):
    while True:
        d = [rng.randint(low, high) for _ in range(3)]
        if any(d) and math.gcd(*d) == 1:
            return d


def _dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _add(a, b, k=1):
    return [p + k * q for p, q in zip(a, b)]


def _det(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _across(rng, direction):
    """Ненулевой вектор поперёк направления: скалярное произведение ноль."""
    while True:
        other = _direction(rng, -3, 3)
        across = _cross(direction, other)
        if any(across):
            return across


def _triangle(rng):
    """Три точки, не лежащие на одной прямой."""
    while True:
        A, B, C = _point(rng, -4, 4), _point(rng, -4, 4), _point(rng, -4, 4)
        if any(_cross(_add(B, A, -1), _add(C, A, -1))):
            return A, B, C


def _tex_plane(n, d):
    x, y, z = sp.symbols('x y z')
    return sp.latex(n[0] * x + n[1] * y + n[2] * z) + '=' + sp.latex(d)


def cross(rng):
    """Векторное произведение: по двум векторам или по трём точкам."""
    if rng.random() < 0.5:
        u, v = _direction(rng, -4, 4), _direction(rng, -4, 4)
        while not any(_cross(u, v)):
            v = _direction(rng, -4, 4)
        return {
            'prompt': (f'Найдите векторное произведение $\\mathbf u\\times\\mathbf v$, '
                       f'где $\\mathbf u={_tex(u)}$ и $\\mathbf v={_tex(v)}$.'),
            'answer': tuple(_cross(u, v)),
            'check': vector_check('cross', u=u, v=v),
            'budget_ms': 60_000,
            'note': 'Средняя компонента — u₃v₁ − u₁v₃. Проверка: произведение перпендикулярно обоим.',
        }
    A, B, C = _triangle(rng)
    return {
        'prompt': (f'Точки $A{_v(A)}$, $B{_v(B)}$ и $C{_v(C)}$. Найдите '
                   f'$\\overrightarrow{{AB}}\\times\\overrightarrow{{AC}}$.'),
        'answer': tuple(_cross(_add(B, A, -1), _add(C, A, -1))),
        'check': vector_check('cross', u=_add(B, A, -1), v=_add(C, A, -1)),
        'budget_ms': 75_000,
        'note': 'Сначала рёбра: AB = B − A и AC = C − A, конец минус начало. Потом произведение.',
    }


def area(rng):
    """Площадь треугольника или параллелограмма."""
    A, B, C = _triangle(rng)
    size = sp.sqrt(_dot(_cross(_add(B, A, -1), _add(C, A, -1)),
                        _cross(_add(B, A, -1), _add(C, A, -1))))
    if rng.random() < 0.5:
        return {
            'prompt': (f'Найдите площадь треугольника с вершинами $A{_v(A)}$, $B{_v(B)}$ '
                       f'и $C{_v(C)}$. Ответ точный.'),
            'answer': sp.nsimplify(size / 2),
            'check': vector_check('area_triangle', A=A, B=B, C=C),
            'budget_ms': 90_000,
            'note': 'Половина длины AB × AC. Половину забывают чаще всего.',
        }
    D = _add(_add(A, C), B, -1)          # ABCD — параллелограмм: D = A + C − B
    return {
        'prompt': (f'$ABCD$ — параллелограмм с вершинами $A{_v(A)}$, $B{_v(B)}$, $C{_v(C)}$ '
                   f'и $D{_v(D)}$. Найдите его площадь. Ответ точный.'),
        'answer': sp.nsimplify(size),
        'check': vector_check('area_parallelogram', A=A, B=B, C=C, D=D),
        'budget_ms': 90_000,
        'note': 'Длина AB × AD: стороны от одной вершины, а не диагональ AC.',
    }


def volume(rng):
    """Объём пирамиды на треугольном основании."""
    while True:
        A, B, C = _triangle(rng)
        S = _point(rng, -4, 4)
        determinant = _det([_add(A, S, -1), _add(B, S, -1), _add(C, S, -1)])
        if determinant:
            break
    return {
        'prompt': (f'Найдите объём пирамиды с вершиной $S{_v(S)}$ и основанием — '
                   f'треугольником $A{_v(A)}$, $B{_v(B)}$, $C{_v(C)}$.'),
        'answer': R(abs(determinant), 6),
        'check': vector_check('volume', S=S, A=A, B=B, C=C),
        'budget_ms': 120_000,
        'note': 'Треть площади основания на высоту — или шестая часть определителя рёбер из S.',
    }


def identity(rng):
    """Тождество |u × v|² = |u|²|v|² − (u · v)²: длина, которой не дали."""
    d, c, product = rng.choice(_TRIPLES)
    # Ни 1, ни 2: при |u| = 2 квадрат совпал бы с удвоением, и «корень не
    # извлечён» перестало бы отличаться от «это вдвое больше».
    divisors = [k for k in range(3, product) if product % k == 0]
    length = rng.choice(divisors)
    other = product // length
    if rng.random() < 0.5:
        d = -d
    if rng.random() < 0.5:
        return {
            'prompt': (f'Известно, что $\\mathbf u\\cdot\\mathbf v={d}$, '
                       f'$|\\mathbf u\\times\\mathbf v|={c}$ и $|\\mathbf v|={other}$. '
                       f'Найдите $|\\mathbf u|$.'),
            'answer': sp.Integer(length),
            'check': vector_check('lagrange', letter='u', dot=[d], cross=[c], known=[other]),
            'budget_ms': 75_000,
            'note': '(u · v)² + |u × v|² = |u|²|v|²: подставить три числа и извлечь корень.',
        }
    return {
        'prompt': (f'Известно, что $\\mathbf u\\cdot\\mathbf v={d}$, $|\\mathbf u|={length}$ '
                   f'и $|\\mathbf v|={other}$. Найдите $|\\mathbf u\\times\\mathbf v|$.'),
        'answer': sp.Integer(c),
        'check': vector_check('lagrange', letter='cross', dot=[d], known=[length], other=[other]),
        'budget_ms': 75_000,
        'note': '|u × v|² = |u|²|v|² − (u · v)². Скалярное произведение входит в квадрате.',
    }


def angle(rng):
    """Углы с плоскостью — и дуга на сфере, где угол считают произведениями."""
    choice = rng.random()
    if choice < 0.4:
        n1, n2 = _direction(rng, -3, 3), _direction(rng, -3, 3)
        while _dot(n1, n2) == 0 or not any(_cross(n1, n2)):
            n2 = _direction(rng, -3, 3)
        cosine = sp.nsimplify(abs(_dot(n1, n2)) / sp.sqrt(_dot(n1, n1) * _dot(n2, n2)))
        return {
            'prompt': (f'Плоскости ${_tex_plane(n1, rng.randint(-6, 6))}$ и '
                       f'${_tex_plane(n2, rng.randint(-6, 6))}$ пересекаются под острым '
                       f'углом $\\theta$. Найдите $\\cos\\theta$. Ответ точный.'),
            'answer': cosine,
            'check': vector_check('plane_angle', n1=n1, n2=n2),
            'budget_ms': 90_000,
            'note': 'Угол между плоскостями — между нормалями, острый: модуль в числителе.',
        }
    if choice < 0.75:
        n, d = _direction(rng, -3, 3), _direction(rng, -3, 3)
        while _dot(n, d) == 0:
            d = _direction(rng, -3, 3)
        value = math.degrees(math.asin(abs(_dot(n, d)) / math.sqrt(_dot(n, n) * _dot(d, d))))
        return {
            'prompt': (f'Прямая $\\mathbf r={_tex(_point(rng, -3, 3))}+\\lambda{_tex(d)}$ '
                       f'пересекает плоскость ${_tex_plane(n, rng.randint(-6, 6))}$ под углом '
                       f'$\\alpha$. Найдите $\\alpha$ в градусах, три значащие цифры.'),
            'answer': sp.Float(value, 15),
            'check': vector_check('line_plane_angle', n=n, d=d),
            'budget_ms': 90_000,
            'note': 'sin α = |d · n| / (|d||n|): у прямой с плоскостью синус, а не косинус.',
        }
    radius = rng.choice([2, 3, 5, 6, 10])
    while True:
        first, second = _direction(rng, -3, 3), _direction(rng, -3, 3)
        if any(_cross(first, second)):
            break
    cosine = _dot(first, second) / math.sqrt(_dot(first, first) * _dot(second, second))
    return {
        'prompt': (f'Точки $A$ и $B$ лежат на сфере радиуса ${radius}$ с центром в начале '
                   f'координат, в направлениях ${_tex(first)}$ и ${_tex(second)}$ от центра. '
                   f'Найдите длину кратчайшего пути от $A$ до $B$ по сфере, три значащие цифры.'),
        'answer': sp.Float(radius * math.acos(cosine), 15),
        'check': vector_check('sphere_arc', u=first, v=second, radius=[radius]),
        'budget_ms': 90_000,
        'note': 'Дуга — rθ, и θ обязано быть в радианах; сама хорда короче дуги.',
    }


def closest(rng):
    """Ближайшая точка прямой: перпендикуляр из точки."""
    d = _direction(rng)
    step = rng.choice([-3, -2, -1, 1, 2, 3])
    N = _add(_point(rng, -3, 3), d, step)          # точка прямой при известном параметре
    start = _add(N, d, -step)
    across = _across(rng, d)
    Q = _add(N, across, rng.choice([-2, -1, 1, 2]))
    return {
        'prompt': (f'Найдите точку прямой $\\mathbf r={_tex(start)}+\\lambda{_tex(d)}$, '
                   f'ближайшую к точке $Q{_v(Q)}$.'),
        'answer': tuple(N),
        'check': vector_check('closest', p=start, d=d, q=Q),
        'budget_ms': 90_000,
        'note': 'Ближайшая — та, где PN перпендикулярен направлению: PN · d = 0. Ответ — точка, не λ.',
    }


def distance(rng):
    """Расстояние до прямой или между параллельными прямыми."""
    d = _direction(rng)
    while _dot(d, d) == 1:          # у единичного направления деление на |d| незаметно
        d = _direction(rng)
    across = _across(rng, d)
    step = rng.choice([-2, -1, 1, 2])
    start = _point(rng, -3, 3)
    gap = sp.sqrt(_dot(_add([0, 0, 0], across, step), _add([0, 0, 0], across, step)))
    if rng.random() < 0.5:
        Q = _add(_add(start, d, rng.choice([-2, -1, 1, 2])), across, step)
        return {
            'prompt': (f'Найдите кратчайшее расстояние от точки $Q{_v(Q)}$ до прямой '
                       f'$\\mathbf r={_tex(start)}+\\lambda{_tex(d)}$. Ответ точный.'),
            'answer': sp.nsimplify(gap),
            'check': vector_check('line_distance', p=start, d=d, q=Q),
            'budget_ms': 90_000,
            'note': '|QP × d| / |d|: делить на длину направления обязательно.',
        }
    second = _add(_add(start, d, rng.choice([-2, -1, 1, 2])), across, step)
    factor = rng.choice([-2, -1, 2, 3])
    return {
        'prompt': (f'Прямые $\\mathbf r_1={_tex(start)}+\\lambda{_tex(d)}$ и '
                   f'$\\mathbf r_2={_tex(second)}+\\mu{_tex([factor * c for c in d])}$ '
                   f'параллельны. Найдите расстояние между ними. Ответ точный.'),
        'answer': sp.nsimplify(gap),
        'check': vector_check('line_distance', p=start, d=d, p2=second,
                              d2=[factor * c for c in d]),
        'budget_ms': 105_000,
        'note': 'Взять точку на одной прямой и мерить до другой: |AB × d| / |d|.',
    }


GENERATORS = {
    'C7.cross': cross,
    'C7.area': area,
    'C7.volume': volume,
    'C7.identity': identity,
    'C7.angle': angle,
    'C7.closest': closest,
    'C7.distance': distance,
}
