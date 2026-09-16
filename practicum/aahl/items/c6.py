"""Задачи на счёт для практикума C6: плоскости и их общая часть.

Генераторы идут по лестнице карточки: плоскость через точку и нормаль (и
буква у перпендикулярных плоскостей); плоскость через три точки; где прямая
протыкает плоскость; прямая пересечения двух плоскостей; три плоскости —
точка или буква, при которой единственной точки нет; основание
перпендикуляра и расстояние; отражение точки.

Проверки эталона не хранят. `vector_check` отдаёт странице точки, нормали и
правые части, и страница зовёт те же verify_plane, verify_find,
verify_intersection и verify_distance, что стоят в ноутбуке: плоскость,
общую точку и отражение проверка находит сама. Эталон в задании только для
показа после попытки; считает его здесь целочисленная арифметика, построенная
от ответа к условию.
"""
from __future__ import annotations

import math

import sympy as sp

from .common import vector_check

R = sp.Rational
X, Y, Z = sp.symbols('x y z')


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


def _normal(rng):
    """Нормаль с длиной больше единицы: у единичной расстояние совпало бы с |λ|."""
    while True:
        n = _direction(rng, -3, 3)
        if sum(c * c for c in n) > 1:
            return n


def _dot(a, b):
    return sum(p * q for p, q in zip(a, b))


def _cross(a, b):
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _add(a, b, k=1):
    return [p + k * q for p, q in zip(a, b)]


def _primitive(v):
    common = math.gcd(*v)
    return [c // common for c in v] if common else v


def _det(m):
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def _equation(n, d):
    """Уравнение плоскости для показа: sympy сам уберёт нулевые члены."""
    return sp.Eq(n[0] * X + n[1] * Y + n[2] * Z, d)


def _tex_plane(n, d):
    return sp.latex(n[0] * X + n[1] * Y + n[2] * Z) + '=' + sp.latex(d)


def plane(rng):
    """Плоскость через точку и нормаль — или буква, при которой плоскости перпендикулярны."""
    if rng.random() < 0.5:
        A, n = _point(rng), _normal(rng)
        return {
            'prompt': (f'Запишите декартово уравнение плоскости, проходящей через точку $A{_v(A)}$ '
                       f'перпендикулярно вектору $\\mathbf n={_tex(n)}$. Ответ в виде ax + by + cz = d.'),
            'answer': _equation(n, _dot(n, A)),
            'check': vector_check('plane', point=A, normal=n),
            'budget_ms': 45_000,
            'note': 'n · r = n · a: коэффициенты — нормаль, правая часть — левая часть, вычисленная в точке A.',
        }
    n1 = _normal(rng)
    while n1[0] == 0:
        n1 = _normal(rng)
    rest = [rng.randint(-4, 4), rng.randint(-4, 4)]
    value = R(-(n1[1] * rest[0] + n1[2] * rest[1]), n1[0])
    return {
        'prompt': (f'Плоскости ${_tex_plane(n1, rng.randint(-6, 6))}$ и '
                   f'${sp.latex(sp.Symbol("p") * X + rest[0] * Y + rest[1] * Z)}={rng.randint(-6, 6)}$ '
                   f'перпендикулярны. Найдите $p$.'),
        'answer': value,
        'check': vector_check('perpendicular_planes', n1=n1, n2=['p'] + rest, letter='p'),
        'budget_ms': 45_000,
        'note': 'Плоскости перпендикулярны — перпендикулярны нормали: скалярное произведение нормалей ноль.',
    }


def normal(rng):
    """Плоскость через три точки: нормаль — векторное произведение двух сторон."""
    while True:
        A, B, C = _point(rng, -4, 4), _point(rng, -4, 4), _point(rng, -4, 4)
        n = _cross(_add(B, A, -1), _add(C, A, -1))
        if any(n):
            break
    n = _primitive(n)
    return {
        'prompt': (f'Найдите декартово уравнение плоскости, проходящей через точки $A{_v(A)}$, '
                   f'$B{_v(B)}$ и $C{_v(C)}$. Ответ в виде ax + by + cz = d.'),
        'answer': _equation(n, _dot(n, A)),
        'check': vector_check('three_points', A=A, B=B, C=C),
        'budget_ms': 120_000,
        'note': ('Нормаль — AB × AC; средняя компонента a₃b₁ − a₁b₃. Правая часть — из одной точки, '
                 'две другие обязаны дать то же число.'),
    }


def line_plane(rng):
    """Где прямая протыкает плоскость."""
    meet, n = _point(rng, -4, 4), _normal(rng)
    d = _direction(rng)
    while _dot(d, n) == 0:
        d = _direction(rng)
    s = rng.choice([-3, -2, -1, 1, 2, 3])
    P = _add(meet, d, -s)
    c = _dot(n, meet)
    return {
        'prompt': (f'Найдите точку, в которой прямая $\\mathbf r={_tex(P)}+\\lambda{_tex(d)}$ пересекает '
                   f'плоскость ${_tex_plane(n, c)}$.'),
        'answer': tuple(meet),
        'check': vector_check('line_plane', p=P, d=d, n=n, c=[c]),
        'budget_ms': 75_000,
        'note': 'Общую точку прямой подставить в уравнение плоскости: одно λ, и его — обратно в прямую.',
    }


def two_planes(rng):
    """Прямая пересечения двух плоскостей."""
    common = _point(rng, -4, 4)
    n1, n2 = _normal(rng), _normal(rng)
    while not any(_cross(n1, n2)):
        n2 = _normal(rng)
    direction = _primitive(_cross(n1, n2))
    return {
        'prompt': (f'Запишите векторное уравнение прямой, по которой пересекаются плоскости '
                   f'${_tex_plane(n1, _dot(n1, common))}$ и ${_tex_plane(n2, _dot(n2, common))}$. '
                   f'Ответ в виде r = (x, y, z) + λ(a, b, c).'),
        'answer': f'r = {_v(common)} + λ{_v(direction)}',
        'check': vector_check('two_planes', n1=n1, c1=[_dot(n1, common)], n2=n2, c2=[_dot(n2, common)]),
        'budget_ms': 120_000,
        'note': 'Направление — n₁ × n₂, перпендикулярно обеим нормалям; точка — общая, например при z = 0.',
    }


def three_planes(rng):
    """Три плоскости: общая точка — или буква, при которой единственной точки нет."""
    while True:
        n1, n2, n3 = _direction(rng, -3, 3), _direction(rng, -3, 3), _direction(rng, -3, 3)
        if _det([n1, n2, n3]) != 0:
            break
    if rng.random() < 0.5:
        point = _point(rng, -3, 3)
        cs = [_dot(n, point) for n in (n1, n2, n3)]
        system = r'\\'.join(_tex_plane(n, c) for n, c in zip((n1, n2, n3), cs))
        return {
            'prompt': (f'Найдите общую точку трёх плоскостей: '
                       f'$\\begin{{cases}}{system}\\end{{cases}}$'),
            'answer': tuple(point),
            'check': vector_check('three_planes', n1=n1, c1=[cs[0]], n2=n2, c2=[cs[1]], n3=n3, c3=[cs[2]]),
            'budget_ms': 150_000,
            'note': 'Исключить одно неизвестное из двух пар уравнений, решить два на два, подставить обратно.',
        }
    while True:
        k1, k2 = rng.choice([1, 2, -1]), rng.choice([1, -1, 2])
        combo = [k1 * p + k2 * q for p, q in zip(n1, n2)]
        index = rng.randrange(3)
        others = [i for i in range(3) if i != index]
        cofactor = n1[others[0]] * n2[others[1]] - n1[others[1]] * n2[others[0]]
        if cofactor != 0 and any(combo):
            break
    third = [sp.Symbol('a') if i == index else combo[i] for i in range(3)]
    c1, c2, c3 = rng.randint(-6, 6), rng.randint(-6, 6), rng.randint(-6, 6)
    system = r'\\'.join([_tex_plane(n1, c1), _tex_plane(n2, c2), _tex_plane(third, c3)])
    return {
        'prompt': (f'При каком значении $a$ система $\\begin{{cases}}{system}\\end{{cases}}$ не имеет '
                   f'единственного решения?'),
        'answer': sp.Integer(combo[index]),
        'check': vector_check('no_unique', n1=n1, c1=[c1], n2=n2, c2=[c2], n3=third, c3=[c3], letter='a'),
        'budget_ms': 120_000,
        'note': ('Нет единственного решения — нормали линейно зависимы: определитель из коэффициентов ноль, '
                 'правые части на это не влияют.'),
    }


def foot(rng):
    """Основание перпендикуляра из точки или расстояние до плоскости."""
    base, n = _point(rng, -4, 4), _normal(rng)
    step = rng.choice([-3, -2, -1, 1, 2, 3])
    Q = _add(base, n, step)
    c = _dot(n, base)
    if rng.random() < 0.5:
        return {
            'prompt': (f'Найдите основание перпендикуляра, опущенного из точки $Q{_v(Q)}$ на плоскость '
                       f'${_tex_plane(n, c)}$.'),
            'answer': tuple(base),
            'check': vector_check('foot', q=Q, n=n, c=[c]),
            'budget_ms': 90_000,
            'note': 'Прямая Q + λn подставляется в плоскость: одно λ, основание — прямая при нём.',
        }
    return {
        'prompt': (f'Найдите расстояние от точки $Q{_v(Q)}$ до плоскости ${_tex_plane(n, c)}$.'),
        'answer': abs(step) * sp.sqrt(_dot(n, n)),
        'check': vector_check('plane_distance', q=Q, n=n, c=[c]),
        'budget_ms': 75_000,
        'note': 'Расстояние — |n·q − d| / |n|, или |λ|·|n| для основания перпендикуляра; не |λ|.',
    }


def reflection(rng):
    """Отражение точки в плоскости."""
    base, n = _point(rng, -4, 4), _normal(rng)
    step = rng.choice([-2, -1, 1, 2])
    Q = _add(base, n, step)
    c = _dot(n, base)
    return {
        'prompt': (f'Найдите точку, симметричную точке $Q{_v(Q)}$ относительно плоскости '
                   f'${_tex_plane(n, c)}$.'),
        'answer': tuple(_add(base, n, -step)),
        'check': vector_check('reflection', q=Q, n=n, c=[c]),
        'budget_ms': 90_000,
        'note': 'Основание перпендикуляра — при λ, отражение — при 2λ на той же прямой: Q′ = 2F − Q.',
    }


GENERATORS = {
    'C6.plane': plane,
    'C6.normal': normal,
    'C6.line_plane': line_plane,
    'C6.two_planes': two_planes,
    'C6.three_planes': three_planes,
    'C6.foot': foot,
    'C6.reflection': reflection,
}
