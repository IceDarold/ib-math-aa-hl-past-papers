"""Задачи на счёт для практикума E9: оптимизация и связанные скорости.

Генераторы идут по лестнице карточки: скорость величины в момент; когда
частица разворачивается; наибольший модуль скорости на отрезке; связанная
скорость через одну величину и через угол; оптимум модели и то, что в нём
спрашивают; ближайшая точка кривой; когда рост быстрее всего; наилучшее
целое.

Проверки эталона не хранят. `rates_check` отдаёт странице саму модель, и
страница зовёт те же verify_rate, verify_when, verify_extreme,
verify_related и verify_best, что стоят в ноутбуке: скорость там меряют
сдвигом времени, связанную скорость — тем, что связь не ломается,
наибольшее — просмотром всего промежутка. Эталон в задании только для
показа после попытки; строится он здесь от ответа к условию, в точных
числах.
"""
from __future__ import annotations

import sympy as sp

from .common import rates_check

t, x = sp.symbols('t x')
R = sp.Rational


def _tex(expr):
    return sp.latex(sp.sympify(expr))


def rate(rng):
    """Скорость изменения величины в момент."""
    if rng.random() < 0.5:
        a, b, c = rng.choice([1, 2, 3]), rng.randint(-6, 6), rng.randint(5, 40)
        f = a * t ** 3 + b * t ** 2 + c
        at = rng.randint(1, 4)
        answer = 3 * a * at ** 2 + 2 * b * at
        what = 'объёма'
    else:
        start, gap, scale = rng.choice([15, 20, 25]), rng.choice([40, 60, 80]), rng.choice([2, 4, 5])
        f = start + gap * sp.exp(-t / scale)
        at = rng.choice([1, 2, 3, 5])
        answer = sp.simplify(-sp.Integer(gap) / scale * sp.exp(-sp.Integer(at) / scale))
        what = 'температуры'
    return {
        'prompt': (f'Величина меняется по закону $Q(t) = {_tex(f)}$. Найдите скорость '
                   f'изменения {what} в момент $t = {at}$. Ответ точный или с тремя '
                   f'значащими цифрами.'),
        'answer': sp.nsimplify(answer),
        'check': rates_check('rate', f=f, at=at),
        'budget_ms': 75_000,
        'note': 'Скорость изменения — производная в момент, а не сама величина.',
    }


def rest(rng):
    """Когда частица меняет направление."""
    first = rng.randint(1, 4)
    second = first + rng.randint(1, 4)
    scale = rng.choice([1, 2, -1, -2])
    v = sp.expand(scale * (t - first) * (t - second))
    which = rng.choice([1, 2])
    word = 'впервые' if which == 1 else 'во второй раз'
    return {
        'prompt': (f'Частица движется по прямой со скоростью $v(t) = {_tex(v)}$ м/с, '
                   f'$0 \\le t \\le {second + 2}$. Когда она {word} меняет направление?'),
        'answer': sp.Integer(first if which == 1 else second),
        'check': rates_check('when', v=v, span=(0, second + 2), event='turn', which=which),
        'budget_ms': 75_000,
        'note': 'Разворот — там, где v меняет знак; корни v считают по порядку.',
    }


def peak(rng):
    """Наибольший модуль скорости на отрезке: он на конце."""
    top = rng.randint(2, 6)
    end = rng.randint(3, 5)
    # Конец отрезка не должен совпасть со значением в вершине: иначе промах
    # «взята вершина» неотличим от «назван момент вместо значения».
    while end ** 2 <= 2 * top or end == top:
        end += 1
    v = top - t ** 2
    return {
        'prompt': (f'Частица движется со скоростью $v(t) = {_tex(v)}$ м/с, '
                   f'$0 \\le t \\le {end}$. Найдите наибольший модуль скорости.'),
        'answer': sp.Integer(end ** 2 - top),
        'check': rates_check('extreme', v=v, span=(0, end), quantity='speed', kind='max'),
        'budget_ms': 75_000,
        'note': 'Модуль скорости — |v|; вершина графика v здесь проигрывает концу отрезка.',
    }


_SHAPES = {
    'square': ('площадь квадрата', 'A', lambda s: s ** 2, 'сторона'),
    'cube': ('объём куба', 'V', lambda s: s ** 3, 'ребро'),
    'sphere': ('объём шара', 'V', lambda s: R(4, 3) * sp.pi * s ** 3, 'радиус'),
}


def chain(rng):
    """Связанная скорость через одну величину."""
    shape = rng.choice(sorted(_SHAPES))
    title, letter, law, side = _SHAPES[shape]
    speed = rng.choice([2, 3, 5, 6, 12])
    size = rng.randint(2, 6)
    big, s = sp.symbols(f'{letter} s')
    body = law(s)
    answer = sp.simplify(speed / body.diff(s).subs(s, size))
    return {
        'prompt': (f'{title.capitalize()} растёт со скоростью {speed} в секунду: '
                   f'${letter} = {_tex(body)}$. Найдите, с какой скоростью растёт '
                   f'{side} $s$ в момент, когда $s = {size}$. Ответ точный.'),
        'answer': answer,
        'check': rates_check('related', relations=[sp.Eq(big, body)], at=[sp.Eq(s, size)],
                             rates={letter: speed}, want='s', where={'s': (0, 20)}),
        'budget_ms': 100_000,
        'note': f'ds/dt = (d{letter}/dt) / (d{letter}/ds): связь сначала, числа потом.',
    }


def angle(rng):
    """Связанная скорость через угол: лестница скользит."""
    length = rng.choice([4, 5, 6, 10])
    turn = rng.choice([R(1, 10), R(1, 5), R(1, 2)])
    place = rng.choice([sp.pi / 6, sp.pi / 4, sp.pi / 3])
    theta = sp.Symbol('theta')
    answer = sp.nsimplify(length * turn * sp.sin(place))
    return {
        'prompt': (f'Лестница длиной {length} м скользит так, что угол $\\theta$ с землёй '
                   f'уменьшается на ${_tex(turn)}$ рад/с. Основание стоит на расстоянии '
                   f'$x = {length}\\cos\\theta$ от стены. С какой скоростью оно удаляется '
                   f'при $\\theta = {_tex(place)}$? Ответ точный.'),
        'answer': answer,
        'check': rates_check('related', relations=[sp.Eq(x, length * sp.cos(theta))],
                             at=[sp.Eq(theta, place)], rates={'theta': -turn}, want='x',
                             where={'theta': (0, sp.pi / 2)}),
        'budget_ms': 100_000,
        'note': 'Угол уменьшается — его скорость отрицательна, и знак проходит сквозь цепочку.',
    }


def optimum(rng):
    """Оптимум модели и то, что в нём спрашивают."""
    root = rng.randint(1, 4)
    top = 3 * root ** 2
    curve = top - x ** 2
    return {
        'prompt': (f'Прямоугольник стоит на оси $x$, а его верхние вершины лежат на '
                   f'$y = {_tex(curve)}$ в точках $(\\pm x, {_tex(curve)})$. Найдите высоту '
                   f'прямоугольника наибольшей площади.'),
        'answer': sp.Integer(2 * top // 3),
        'check': rates_check('best', f=2 * x * curve, var='x',
                             domain=(0, sp.sqrt(top), True, True), kind='max',
                             report=curve, exact=True),
        'budget_ms': 105_000,
        'note': 'Спрашивают высоту, а не x: после A′ = 0 ответ ещё надо дочитать.',
    }


def distance(rng):
    """Ближайшая точка кривой — через квадрат расстояния."""
    far = rng.randint(1, 6)
    return {
        'prompt': (f'Найдите $x$-координату точки кривой $y = \\sqrt{{x}}$, ближайшей к '
                   f'точке $({far}, 0)$. Ответ точный.'),
        'answer': far - R(1, 2),
        'check': rates_check('best', f=sp.sqrt((x - far) ** 2 + x), var='x',
                             domain=(0, far + 10, True, False), kind='min',
                             report='place', exact=True),
        'budget_ms': 100_000,
        'note': 'Минимизируют D² — у квадрата та же вершина, а корня в производной нет.',
    }


def fastest(rng):
    """Когда рост быстрее всего: вершина скорости."""
    ceiling = rng.choice([100, 200, 500, 1000])
    start = rng.choice([4, 9, 19])
    pace = rng.choice([R(1, 2), sp.Integer(1), sp.Integer(2)])
    growth = ceiling / (1 + start * sp.exp(-pace * t))
    return {
        'prompt': (f'Численность растёт по закону $P(t) = {_tex(growth)}$. В какой момент '
                   f'она растёт быстрее всего? Ответ точный или с тремя значащими цифрами.'),
        'answer': sp.log(start) / pace,
        'check': rates_check('best', f=growth, var='t', domain=(0, 60, False, False),
                             kind='max', report='place', rate=True),
        'budget_ms': 100_000,
        'note': 'Наибольшая скорость — вершина P′, то есть перегиб P: там P = половине предела.',
    }


def whole(rng):
    """Наилучшее целое: вершину не округляют, а сравнивают соседей."""
    while True:
        top = rng.randint(10, 40)
        if top % 3 == 0:
            continue
        values = {n: n * (top - n) ** 2 for n in range(1, top)}
        best = max(values, key=values.get)
        if list(values.values()).count(values[best]) == 1:
            break
    n = sp.Symbol('n')
    return {
        'prompt': (f'При каком целом $n$ от 1 до {top - 1} величина $n({top} - n)^2$ '
                   f'наибольшая?'),
        'answer': sp.Integer(best),
        'check': rates_check('best', f=n * (top - n) ** 2, var='n',
                             domain=(1, top - 1, False, False), kind='max',
                             report='place', integer=True),
        'budget_ms': 90_000,
        'note': f'Вершина при n = {top}/3 не целая: сравнивают соседние целые.',
    }


GENERATORS = {
    'E9.rate': rate,
    'E9.rest': rest,
    'E9.peak': peak,
    'E9.chain': chain,
    'E9.angle': angle,
    'E9.optimum': optimum,
    'E9.distance': distance,
    'E9.fastest': fastest,
    'E9.whole': whole,
}
