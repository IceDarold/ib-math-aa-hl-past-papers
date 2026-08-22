"""Задачи на счёт для практикума C1: треугольник.

Одна задача на приём, каждый раз с новыми числами. Генератор получает
random.Random с зерном и обязан быть детерминированным: сервер не хранит
ответ, а пересобирает задание по зерну, когда приходит проверять.

Числа подбираются так, чтобы треугольник существовал и ответ был не
вырожденным. Где условие просит точное значение, углы берутся только из
тех, у которых синус и косинус точные.
"""
from __future__ import annotations

import sympy as sp

from .common import exact_check, num_check, triangle_check

DEG = sp.pi / 180


def right_triangle(rng):
    length = rng.choice([3, 3.5, 4, 4.5, 5, 6, 7, 8])
    angle = rng.choice([52, 55, 58, 61, 64, 67, 70, 73])
    value = float(length * sp.sin(angle * DEG))
    return {
        'prompt': (f'Лестница длиной ${length}$ м приставлена к стене под '
                   f'углом ${angle}^\\circ$ к земле. На какой высоте её '
                   f'верхний конец? Три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 60_000,
    }


def elevation_and_bearing(rng):
    if rng.random() < 0.5:
        distance = rng.choice([20, 25, 30, 40, 50, 60, 80, 100])
        angle = rng.choice([24, 27, 31, 35, 38, 42, 46])
        eye = rng.choice([0, 0, 1.5, 1.6, 1.8])
        tail = (f' Глаз наблюдателя на высоте ${eye}$ м.' if eye else '')
        value = float(distance * sp.tan(angle * DEG) + eye)
        return {
            'prompt': (f'С точки на земле, удалённой на ${distance}$ м от '
                       f'основания башни, её вершина видна под углом '
                       f'${angle}^\\circ$ к горизонту.{tail} Какова высота '
                       f'башни? Три значащие цифры.'),
            'answer': value,
            'check': num_check(value, 3),
            'budget_ms': 75_000,
        }
    first = rng.choice([20, 25, 30, 35, 40])
    second = rng.choice([15, 20, 28, 32, 45])
    turn = rng.choice([50, 60, 70, 80, 90, 100, 110])
    # Угол в вершине маршрута дополняет поворот до 180°.
    inner = 180 - turn
    value = float(sp.sqrt(first**2 + second**2
                          - 2 * first * second * sp.cos(inner * DEG)))
    return {
        'prompt': (f'Корабль прошёл ${first}$ км, затем повернул на '
                   f'${turn}^\\circ$ и прошёл ещё ${second}$ км. На каком '
                   f'расстоянии он от точки старта? Три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 90_000,
    }


def cosine_rule(rng):
    if rng.random() < 0.5:
        a = rng.choice([5, 6, 7, 8, 9, 11, 12])
        b = rng.choice([6, 7, 8, 9, 10, 13, 14])
        angle = rng.choice([37, 42, 48, 55, 63, 71, 84, 96, 110, 124])
        value = float(sp.sqrt(a**2 + b**2 - 2 * a * b * sp.cos(angle * DEG)))
        return {
            'prompt': (f'В треугольнике $ABC$: $a = {a}$, $b = {b}$, '
                       f'$C = {angle}^\\circ$. Найдите $c$. Три значащие цифры.'),
            'answer': value,
            'check': triangle_check('c', value, {'a': a, 'b': b, 'C': angle}),
            'budget_ms': 75_000,
        }
    # Три стороны: спрашиваем наибольший угол — он против наибольшей стороны.
    while True:
        a, b, c = sorted(rng.sample([4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 3))
        if a + b > c + 0.5:
            break
    value = float(sp.acos(sp.Rational(a**2 + b**2 - c**2, 2 * a * b)) / DEG)
    return {
        'prompt': (f'В треугольнике стороны ${a}$, ${b}$ и ${c}$. Найдите '
                   f'наибольший угол в градусах. Три значащие цифры.'),
        'answer': value,
        'check': triangle_check('C', value, {'a': a, 'b': b, 'c': c}),
        'budget_ms': 75_000,
    }


def sine_rule(rng):
    first = rng.choice([32, 38, 44, 51, 57, 63])
    second = rng.choice([48, 55, 62, 68, 74, 81])
    side = rng.choice([7, 8, 9, 10, 12, 14, 15])
    third = 180 - first - second
    value = float(side * sp.sin(second * DEG) / sp.sin(first * DEG))
    return {
        'prompt': (f'В треугольнике $ABC$: $A = {first}^\\circ$, '
                   f'$B = {second}^\\circ$, $a = {side}$. Найдите $b$. '
                   f'Три значащие цифры.'),
        'answer': value,
        'check': triangle_check('b', value,
                                {'A': first, 'B': second, 'a': side}),
        'budget_ms': 70_000,
        'note': f'Третий угол ${third}^\\circ$ здесь не нужен.',
    }


def ambiguous_case(rng):
    angle = rng.choice([28, 32, 35, 38, 41])
    a = rng.choice([7, 8, 9, 10])
    # b > a и a > b·sin A — ровно два треугольника.
    lower = float(a / sp.sin(angle * DEG))
    b = rng.choice([n for n in range(a + 1, int(lower)) if n > a])
    if rng.random() < 0.5:
        return {
            'prompt': (f'В треугольнике $a = {a}$, $b = {b}$, '
                       f'$A = {angle}^\\circ$. Сколько таких треугольников '
                       f'существует?'),
            'answer': 2,
            'check': {'kind': 'count', 'value': 2},
            'budget_ms': 45_000,
        }
    value = float(180 - sp.asin(b * sp.sin(angle * DEG) / a) / DEG)
    return {
        'prompt': (f'В треугольнике $a = {a}$, $b = {b}$, '
                   f'$A = {angle}^\\circ$. Найдите **тупой** из двух '
                   f'возможных углов $B$ в градусах. Три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 75_000,
    }


def triangle_area(rng):
    if rng.random() < 0.5:
        a = rng.choice([5, 6, 7, 8, 9, 11, 12])
        b = rng.choice([6, 7, 9, 10, 13, 14])
        angle = rng.choice([34, 41, 47, 53, 62, 68, 76, 104, 118])
        value = float(sp.Rational(1, 2) * a * b * sp.sin(angle * DEG))
        return {
            'prompt': (f'Найдите площадь треугольника со сторонами ${a}$ и '
                       f'${b}$ и углом ${angle}^\\circ$ между ними. '
                       f'Три значащие цифры.'),
            'answer': value,
            'check': num_check(value, 3),
            'budget_ms': 60_000,
        }
    a = rng.choice([6, 8, 9, 10, 12])
    b = rng.choice([7, 9, 11, 13, 15])
    angle = rng.choice([35, 44, 52, 66, 73])
    area = sp.Rational(1, 2) * a * b * sp.sin(angle * DEG)
    shown = float(area)
    return {
        'prompt': (f'Площадь треугольника со сторонами ${a}$ и $b$ и углом '
                   f'${angle}^\\circ$ между ними равна ${shown:.3g}$. '
                   f'Найдите $b$. Три значащие цифры.'),
        'answer': float(b),
        'check': num_check(float(b), 3),
        'budget_ms': 70_000,
    }


EXACT_ANGLES = {30: sp.Rational(1, 2), 150: sp.Rational(1, 2),
                45: sp.sqrt(2) / 2, 135: sp.sqrt(2) / 2,
                60: sp.sqrt(3) / 2, 120: sp.sqrt(3) / 2}


def exact_values(rng):
    angle = rng.choice(sorted(EXACT_ANGLES))
    a = rng.choice([4, 6, 8, 10, 12])
    b = rng.choice([3, 5, 6, 9, 14])
    want = sp.nsimplify(sp.Rational(1, 2) * a * b * EXACT_ANGLES[angle])
    return {
        'prompt': (f'Найдите **точное** значение площади треугольника со '
                   f'сторонами ${a}$ и ${b}$ и углом ${angle}^\\circ$ '
                   f'между ними.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'Десятичная дробь здесь не принимается.',
    }


def triangle_as_model(rng):
    total = rng.choice([10, 12, 14, 16])
    angle = rng.choice([30, 150])
    # Площадь x(total − x)·sin(angle)/2 максимальна при x = total/2.
    peak = sp.Rational(total, 2)
    want = sp.nsimplify(sp.Rational(1, 2) * peak * (total - peak)
                        * EXACT_ANGLES[angle])
    return {
        'prompt': (f'Стороны $AB = x$ и $AC = {total} - x$, угол между ними '
                   f'${angle}^\\circ$. При каком $x$ площадь треугольника '
                   f'наибольшая?'),
        'answer': peak,
        'check': exact_check(peak),
        'budget_ms': 75_000,
        'note': f'Наибольшая площадь при этом равна ${sp.latex(want)}$.',
    }


GENERATORS = {
    'C1.right_triangle': right_triangle,
    'C1.elevation_and_bearing': elevation_and_bearing,
    'C1.cosine_rule': cosine_rule,
    'C1.sine_rule': sine_rule,
    'C1.ambiguous_case': ambiguous_case,
    'C1.triangle_area': triangle_area,
    'C1.exact_values': exact_values,
    'C1.triangle_as_model': triangle_as_model,
}
