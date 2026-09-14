"""Задачи на счёт для практикума C5: векторы, прямые и углы.

Генераторы идут по лестнице карточки: точки и длины; скалярное
произведение; угол между векторами; уравнение прямой; угол между прямыми;
точка пересечения; параллельны, пересекаются или скрещиваются; движение по
прямой.

Проверки эталона не хранят. `vector_check` отдаёт странице точки,
направления и то, что спрашивают, и страница зовёт те же verify_find,
verify_line, verify_meet, verify_relation, verify_angle, verify_speed и
verify_bearing, что стоят в ноутбуке: вершину, точку пересечения и угол
проверка находит сама. Эталон в задании только для показа после попытки;
считает его здесь sympy по формулам, которых в проверке нет.
"""
from __future__ import annotations

import math

import sympy as sp

from .common import vector_check

R = sp.Rational
p = sp.Symbol('p')


def _v(values):
    return '(' + ', '.join(sp.sstr(sp.sympify(v)) for v in values) + ')'


def _tex(values):
    return r'\begin{pmatrix}' + r'\\'.join(sp.latex(sp.sympify(v)) for v in values) + r'\end{pmatrix}'


def _point(rng, low=-6, high=6):
    return [rng.randint(low, high) for _ in range(3)]


def _direction(rng):
    while True:
        d = [rng.randint(-4, 4) for _ in range(3)]
        if any(d) and math.gcd(*d) == 1:
            return d


def _add(a, b, k=1):
    return [x + k * y for x, y in zip(a, b)]


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def points(rng):
    """Точки и длины: середина, четвёртая вершина или расстояние."""
    A, B = _point(rng), _point(rng)
    while A == B:
        B = _point(rng)
    kind = rng.choice(['midpoint', 'vertex', 'distance'])
    if kind == 'midpoint':
        B = [b + (b - a) % 2 for a, b in zip(A, B)]         # середина — целая
        return {
            'prompt': f'Даны точки $A{_v(A)}$ и $B{_v(B)}$. Найдите координаты середины отрезка $[AB]$.',
            'answer': tuple((a + b) // 2 for a, b in zip(A, B)),
            'check': vector_check('midpoint', A=A, B=B),
            'budget_ms': 45_000,
            'note': 'Середина — полусумма концов, (a + b)/2, а не половина вектора AB.',
        }
    if kind == 'vertex':
        C = _point(rng)
        while C in (A, B):
            C = _point(rng)
        return {
            'prompt': (f'Точки $A{_v(A)}$, $B{_v(B)}$, $C{_v(C)}$ и $D$ — вершины '
                       f'параллелограмма $ABCD$ (по порядку). Найдите координаты $D$.'),
            'answer': tuple(a + c - b for a, b, c in zip(A, B, C)),
            'check': vector_check('vertex', A=A, B=B, C=C),
            'budget_ms': 60_000,
            'note': 'В ABCD по порядку AB = DC, поэтому d = a + c − b. Порядок вершин меняет ответ.',
        }
    return {
        'prompt': f'Найдите расстояние между точками $A{_v(A)}$ и $B{_v(B)}$.',
        'answer': sp.sqrt(sum((b - a) ** 2 for a, b in zip(A, B))),
        'check': vector_check('distance', A=A, B=B),
        'budget_ms': 45_000,
        'note': 'Длина AB — корень из суммы квадратов разностей координат.',
    }


def scalar(rng):
    """Скалярное произведение: значение или буква, при которой векторы перпендикулярны."""
    u = _direction(rng)
    if rng.random() < 0.5:
        v = _direction(rng)
        return {
            'prompt': f'Найдите скалярное произведение $\\mathbf u={_tex(u)}$ и $\\mathbf v={_tex(v)}$.',
            'answer': sp.Integer(_dot(u, v)),
            'check': vector_check('dot', u=u, v=v),
            'budget_ms': 30_000,
            'note': 'Сумма произведений компонент: это число, а не вектор.',
        }
    while u[0] == 0:
        u = _direction(rng)
    rest = [rng.randint(-5, 5), rng.randint(-5, 5)]
    v = [p] + rest
    value = R(-(u[1] * rest[0] + u[2] * rest[1]), u[0])
    return {
        'prompt': (f'Векторы $\\mathbf u={_tex(u)}$ и $\\mathbf v={_tex(v)}$ перпендикулярны. '
                   f'Найдите $p$.'),
        'answer': value,
        'check': vector_check('perpendicular', u=u, v=v, letter='p'),
        'budget_ms': 45_000,
        'note': 'Перпендикулярны — скалярное произведение ноль: одно линейное уравнение на p.',
    }


def angle(rng):
    """Угол между векторами или при вершине треугольника."""
    if rng.random() < 0.5:
        u, v = _direction(rng), _direction(rng)
        while _cross(u, v) == [0, 0, 0]:
            v = _direction(rng)
        theta = sp.acos(sp.Rational(_dot(u, v)) / sp.sqrt(_dot(u, u) * _dot(v, v)))
        return {
            'prompt': (f'Найдите угол между векторами $\\mathbf u={_tex(u)}$ и $\\mathbf v={_tex(v)}$ '
                       f'в градусах.'),
            'answer': float(theta * 180 / sp.pi),
            'check': vector_check('angle', u=u, v=v),
            'budget_ms': 60_000,
            'note': 'cos θ = u·v/(|u||v|); тупой угол между векторами — законный ответ.',
        }
    P, V, Q = _point(rng), _point(rng), _point(rng)
    while _cross(_add(P, V, -1), _add(Q, V, -1)) == [0, 0, 0]:
        Q = _point(rng)
    one, two = _add(P, V, -1), _add(Q, V, -1)
    theta = sp.acos(sp.Rational(_dot(one, two)) / sp.sqrt(_dot(one, one) * _dot(two, two)))
    return {
        'prompt': (f'Треугольник $PVQ$: $P{_v(P)}$, $V{_v(V)}$, $Q{_v(Q)}$. Найдите угол '
                   f'$P\\hat VQ$ в градусах.'),
        'answer': float(theta * 180 / sp.pi),
        'check': vector_check('vertex_angle', P=P, V=V, Q=Q),
        'budget_ms': 75_000,
        'note': 'Угол при V — между векторами из V: VP и VQ, а не радиус-векторами OP и OQ.',
    }


def line(rng):
    """Уравнение прямой: через две точки или из декартовой формы."""
    A, d = _point(rng), _direction(rng)
    if rng.random() < 0.5 or 0 in d:
        B = _add(A, d)
        return {
            'prompt': (f'Запишите векторное уравнение прямой через точки $A{_v(A)}$ и $B{_v(B)}$. '
                       f'Ответ в виде r = (x, y, z) + λ(a, b, c).'),
            'answer': f'r = {_v(A)} + λ{_v(d)}',
            'check': vector_check('line', point=A, direction=d),
            'budget_ms': 60_000,
            'note': 'Направление — разность точек B − A; радиус-вектор B направлением не бывает.',
        }
    parts = []
    for axis, a, b in zip('xyz', A, d):
        top = sp.latex(sp.Symbol(axis) - a)
        parts.append(top if b == 1 else f'-({top})' if b == -1 else f'\\frac{{{top}}}{{{b}}}')
    return {
        'prompt': (f'Прямая задана декартовым уравнением ${"=".join(parts)}$. Запишите её векторное '
                   f'уравнение в виде r = (x, y, z) + λ(a, b, c).'),
        'answer': f'r = {_v(A)} + λ{_v(d)}',
        'check': vector_check('line', point=A, direction=d),
        'budget_ms': 60_000,
        'note': 'Приравнять все части λ: точка — числа при x, y, z с обратным знаком, направление — знаменатели.',
    }


def line_angle(rng):
    """Острый угол между прямыми — по направлениям."""
    d1, d2 = _direction(rng), _direction(rng)
    while _cross(d1, d2) == [0, 0, 0] or _dot(d1, d2) == 0:
        d2 = _direction(rng)
    P1, P2 = _point(rng), _point(rng)
    theta = sp.acos(sp.Abs(sp.Rational(_dot(d1, d2))) / sp.sqrt(_dot(d1, d1) * _dot(d2, d2)))
    return {
        'prompt': (f'Найдите острый угол между прямыми $\\mathbf r={_tex(P1)}+\\lambda{_tex(d1)}$ и '
                   f'$\\mathbf r={_tex(P2)}+\\mu{_tex(d2)}$ в градусах.'),
        'answer': float(theta * 180 / sp.pi),
        'check': vector_check('line_angle', p1=P1, d1=d1, p2=P2, d2=d2),
        'budget_ms': 60_000,
        'note': 'Только направления; |d₁·d₂| в числителе — угол между прямыми острый.',
    }


def meet(rng):
    """Точка пересечения двух прямых."""
    X, d1 = _point(rng, -4, 4), _direction(rng)
    d2 = _direction(rng)
    while _cross(d1, d2) == [0, 0, 0]:
        d2 = _direction(rng)
    s, u = rng.choice([-2, -1, 1, 2, 3]), rng.choice([-3, -1, 1, 2])
    P1, P2 = _add(X, d1, -s), _add(X, d2, -u)
    return {
        'prompt': (f'Найдите точку пересечения прямых $\\mathbf r={_tex(P1)}+\\lambda{_tex(d1)}$ и '
                   f'$\\mathbf r={_tex(P2)}+\\mu{_tex(d2)}$.'),
        'answer': tuple(X),
        'check': vector_check('meet', p1=P1, d1=d1, p2=P2, d2=d2),
        'budget_ms': 90_000,
        'note': 'Свои параметры λ и μ, две компоненты решить, третью проверить, λ — в свою прямую.',
    }


def skew(rng):
    """Параллельны, пересекаются или скрещиваются."""
    P1, d1 = _point(rng, -4, 4), _direction(rng)
    kind = rng.choice(['parallel', 'intersecting', 'skew'])
    if kind == 'parallel':
        factor = rng.choice([-2, 2])
        d2 = [factor * c for c in d1]
        P2 = _add(P1, _direction(rng))
        while _cross(_add(P2, P1, -1), d1) == [0, 0, 0]:
            P2 = _add(P2, [1, 0, 0])
    else:
        d2 = _direction(rng)
        while _cross(d1, d2) == [0, 0, 0]:
            d2 = _direction(rng)
        P2 = _add(_add(P1, d1, rng.choice([-2, 1, 2])), d2, rng.choice([-1, 1, 2]))
        if kind == 'skew':
            normal = _cross(d1, d2)
            P2 = _add(P2, normal, 1 if normal != [0, 0, 0] else 0)
    return {
        'prompt': (f'Прямые $\\mathbf r={_tex(P1)}+\\lambda{_tex(d1)}$ и $\\mathbf r={_tex(P2)}+\\mu{_tex(d2)}$ '
                   f'параллельны, пересекаются или скрещиваются? Ответ одним словом.'),
        'answer': {'parallel': 'параллельны', 'intersecting': 'пересекаются', 'skew': 'скрещиваются'}[kind],
        'check': vector_check('relation', p1=P1, d1=d1, p2=P2, d2=d2),
        'budget_ms': 90_000,
        'note': ('Сначала направления: кратны — параллельны. Не кратны — две компоненты и третья: '
                 'сошлась — пересекаются, нет — скрещиваются.'),
    }


def motion(rng):
    """Движение по прямой: скорость или курс."""
    r0 = [rng.randint(-9, 9), rng.randint(-9, 9), rng.randint(0, 5)]
    if rng.random() < 0.5:
        a, b, c = rng.choice([(3, 4, 0), (2, 3, 6), (1, 4, 8), (6, -2, 3), (-4, 4, 7), (2, -6, 9)])
        factor = rng.choice([1, 2, 3])
        v = [a, b, c]
        return {
            'prompt': (f'Положение самолёта в момент $t$ (ч): $\\mathbf r={_tex(r0)}+{factor if factor > 1 else ""}t{_tex(v)}$ км. '
                       f'Найдите его скорость, км/ч.'),
            'answer': sp.Integer(factor) * sp.sqrt(a * a + b * b + c * c),
            'check': vector_check('speed', r0=r0, v=[factor * x for x in v]),
            'budget_ms': 45_000,
            'note': 'Скорость — длина всего вектора при t, вместе с числом перед t; положение ни при чём.',
        }
    east, north = rng.choice([(3, 4), (4, 3), (-5, 12), (12, -5), (-8, -6), (1, 1), (-2, 5)])
    v = [east, north, rng.randint(-2, 2)]
    bearing = round(math.degrees(math.atan2(east, north)) % 360) % 360
    return {
        'prompt': (f'Катер движется по закону $\\mathbf r={_tex(r0)}+t{_tex(v)}$, где $x$ — восток, $y$ — '
                   f'север. Найдите курс катера: трёхзначный пеленг в градусах.'),
        'answer': f'{bearing:03d}',
        'check': vector_check('bearing', v=v),
        'budget_ms': 60_000,
        'note': 'Пеленг — от севера по часовой стрелке по горизонтальным компонентам, тремя цифрами.',
    }


GENERATORS = {
    'C5.points': points,
    'C5.scalar': scalar,
    'C5.angle': angle,
    'C5.line': line,
    'C5.line_angle': line_angle,
    'C5.meet': meet,
    'C5.skew': skew,
    'C5.motion': motion,
}
