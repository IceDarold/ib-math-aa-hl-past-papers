"""Задачи на счёт для практикума E7: дифференциальные уравнения.

Здесь проверка сильнее всего отличается от сверки с эталоном: решение
подставляется в само уравнение, и любая верная форма записи проходит.
Поэтому и константу можно писать как угодно — лишь бы уравнение
удовлетворялось и начальное условие выполнялось.
"""
from __future__ import annotations

import sympy as sp

from .common import exact_check, num_check, ode_check

x, y = sp.Symbol('x'), sp.Symbol('y')


def direct_integration(rng):
    a = rng.choice([1, 2, 3])
    power = rng.choice([1, 2, 3])
    start = rng.choice([0, 1])
    value = rng.choice([1, 2, 3, 5])
    rhs = a * x**power
    solution = sp.integrate(rhs, x)
    constant = value - solution.subs(x, start)
    return {
        'prompt': (f'Решите $\\dfrac{{dy}}{{dx}} = {sp.latex(rhs)}$ при '
                   f'$y({start}) = {value}$. Ответ — $y$ как функция $x$.'),
        'answer': sp.expand(solution + constant),
        'check': ode_check(rhs, ic=(start, value)),
        'budget_ms': 90_000,
    }


def separation(rng):
    rate = rng.choice([1, 2, 3])
    start = rng.choice([1, 2, 4])
    # dy/dx = k·y, решение — экспонента.
    rhs = rate * y
    solution = start * sp.exp(rate * x)
    return {
        'prompt': (f'Решите $\\dfrac{{dy}}{{dx}} = {rate if rate != 1 else ""}y$ '
                   f'при $y(0) = {start}$. Ответ — $y$ как функция $x$.'),
        'answer': solution,
        'check': ode_check(rhs, ic=(0, start)),
        'budget_ms': 120_000,
        'note': 'Разделите переменные и не потеряйте константу.',
    }


def separation_partial_fractions(rng):
    limit = rng.choice([2, 4, 5])
    start = sp.Rational(1, rng.choice([2, 3, 4]))
    # Логистическое: dy/dx = y(L − y)/L.
    rhs = y * (limit - y) / limit
    constant = (limit - start) / start
    solution = limit / (1 + constant * sp.exp(-x))
    return {
        'prompt': (f'Решите $\\dfrac{{dy}}{{dx}} = \\dfrac{{y({limit} - y)}}'
                   f'{{{limit}}}$ при $y(0) = {sp.latex(start)}$. '
                   f'Ответ — $y$ как функция $x$.'),
        'answer': sp.simplify(solution),
        'check': ode_check(rhs, ic=(0, start)),
        'budget_ms': 180_000,
        'note': 'Слева получится дробь, которую надо разложить на простейшие.',
    }


def homogeneous_substitution(rng):
    start = rng.choice([1, 2, 3])
    # dy/dx = (x + y)/x = 1 + y/x, решение y = x·ln x + Cx.
    rhs = (x + y) / x
    constant = start
    solution = x * sp.log(x) + constant * x
    return {
        'prompt': (f'Решите $\\dfrac{{dy}}{{dx}} = \\dfrac{{x + y}}{{x}}$ при '
                   f'$y(1) = {start}$, $x > 0$. Ответ — $y$ как функция $x$.'),
        'answer': solution,
        'check': ode_check(rhs, ic=(1, start)),
        'budget_ms': 180_000,
        'note': 'Подстановка y = vx превращает это в уравнение на v.',
    }


def integrating_factor(rng):
    a = rng.choice([1, 2])
    start = rng.choice([0, 1, 2])
    # dy/dx + a·y = a·x  →  множитель e^{ax}.
    rhs = a * x - a * y
    particular = x - sp.Rational(1, a)
    constant = start - particular.subs(x, 0)
    solution = particular + constant * sp.exp(-a * x)
    left = f'{a}y' if a != 1 else 'y'
    right = f'{a}x' if a != 1 else 'x'
    return {
        'prompt': (f'Решите $\\dfrac{{dy}}{{dx}} + {left} = {right}$ при '
                   f'$y(0) = {start}$. Ответ — $y$ как функция $x$.'),
        'answer': sp.simplify(solution),
        'check': ode_check(rhs, ic=(0, start)),
        'budget_ms': 180_000,
        'note': 'Интегрирующий множитель — экспонента от интеграла '
                'коэффициента при y.',
    }


def euler_method(rng):
    step = rng.choice([sp.Rational(1, 10), sp.Rational(1, 5),
                       sp.Rational(1, 4), sp.Rational(1, 2)])
    steps = rng.choice([2, 3, 4])
    start = rng.choice([1, 2])
    slope = rng.choice([1, 2])
    # dy/dx = x + slope·y
    point_x, point_y = sp.Integer(0), sp.Integer(start)
    for _ in range(steps):
        point_y = point_y + step * (point_x + slope * point_y)
        point_x = point_x + step
    value = float(point_y)
    tail = f'{slope}y' if slope != 1 else 'y'
    return {
        'prompt': (f'Для $\\dfrac{{dy}}{{dx}} = x + {tail}$ с $y(0) = {start}$ '
                   f'сделайте ${steps}$ шага метода Эйлера с шагом '
                   f'$h = {sp.latex(step)}$. Найдите приближённое значение '
                   f'$y({sp.latex(steps * step)})$. Три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 150_000,
        'note': 'Каждый шаг: новое y равно старому плюс h на наклон.',
    }


def euler_error_sign(rng):
    # У выпуклой вниз кривой ломаная Эйлера идёт ниже настоящего решения.
    convex = rng.random() < 0.5
    want = sp.Integer(1 if convex else -1)
    shape = 'выпуклым вниз' if convex else 'выпуклым вверх'
    words = ('занижает' if convex else 'завышает')
    return {
        'prompt': (f'Решение уравнения оказалось {shape} на всём отрезке. '
                   f'Метод Эйлера {words} его значение — введите $1$, если '
                   f'это верно, и $-1$, если наоборот.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'Шаг Эйлера идёт по касательной, а касательная к выпуклой '
                'вниз кривой лежит под ней.',
    }


GENERATORS = {
    'E7.direct_integration': direct_integration,
    'E7.separation': separation,
    'E7.separation_partial_fractions': separation_partial_fractions,
    'E7.homogeneous_substitution': homogeneous_substitution,
    'E7.integrating_factor': integrating_factor,
    'E7.euler_method': euler_method,
    'E7.euler_error_sign': euler_error_sign,
}
