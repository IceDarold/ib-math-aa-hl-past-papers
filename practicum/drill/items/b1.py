"""Задачи на счёт для практикума B1: уравнения.

Как и в C1, генератор детерминирован по зерну: сервер пересобирает задание,
когда приходит проверять ответ, и хранить эталон ему не нужно.

Там, где ответ — корни, проверка идёт подстановкой в само уравнение, а не
сверкой с эталоном: лишний корень и потерянный различаются в сообщении.
"""
from __future__ import annotations

import sympy as sp

from .common import (count_check, equation_check, exact_check, num_check,
                     roots_check, set_check)

x = sp.Symbol('x')


def zero_of_function(rng):
    a = rng.choice([2, 3, 4, 5, 6, 7])
    b = rng.choice([-9, -7, -5, -3, 3, 5, 8, 11])
    c = rng.choice([1, 2, 3])
    d = rng.choice([-8, -6, -4, 4, 6, 9])
    while sp.Rational(-b, a) == sp.Rational(-d, c):
        d = rng.choice([-8, -6, -4, 4, 6, 9])
    top = f'{a}x {"+" if b > 0 else "-"} {abs(b)}'
    bottom = f'{c}x {"+" if d > 0 else "-"} {abs(d)}'
    return {
        'prompt': (f'Найдите нуль функции $f(x) = \\dfrac{{{top}}}{{{bottom}}}$. '
                   f'Ответ точный.'),
        'answer': sp.Rational(-b, a),
        'check': exact_check(sp.Rational(-b, a)),
        'budget_ms': 45_000,
    }


def quadratic_toolkit(rng):
    root_sum = rng.choice([-9, -7, -5, -3, 3, 5, 7, 9, 11])
    const = rng.choice([-12, -8, -6, 4, 6, 9, 14])
    expr = x**2 - root_sum * x + const
    if sp.discriminant(expr, x) <= 0:
        expr = x**2 - root_sum * x - abs(const)
    return {
        'prompt': (f'Решите уравнение ${sp.latex(sp.Eq(expr, 0))}$. '
                   f'Ответ точный, все корни через запятую.'),
        'answer': sorted(sp.solveset(expr, x, sp.S.Reals), key=float),
        'check': roots_check(expr),
        'budget_ms': 75_000,
    }


def equation_from_situation(rng):
    gap = rng.choice([2, 3, 4, 5])
    width = rng.choice([4, 5, 6, 7, 8, 9])
    area = width * (width + gap)
    return {
        'prompt': (f'Длина прямоугольника на ${gap}$ см больше ширины, '
                   f'а площадь равна ${area}$ см². Обозначив ширину за $x$, '
                   f'составьте уравнение (записывать решать не нужно).'),
        'answer': sp.Eq(x * (x + gap), area),
        'check': equation_check(x * (x + gap) - area),
        'budget_ms': 60_000,
        'note': 'Ответ — уравнение, например `x(x+3)=40`.',
    }


def extraneous_roots(rng):
    shift = rng.choice([1, 2, 3])
    # √(x + a) = x − shift. После возведения в квадрат корней всегда два:
    # выбранный root и второй, равный 2·shift + 1 − root. Второй обязан
    # оказаться лишним, иначе ответ не один, — а он лишний ровно тогда,
    # когда меньше shift, то есть при root > shift + 1.
    root = rng.choice([n for n in range(shift + 2, 10)])
    a = (root - shift)**2 - root
    expr = sp.sqrt(x + a) - x + shift
    return {
        'prompt': (f'Решите уравнение $\\sqrt{{x {"+" if a >= 0 else "-"} '
                   f'{abs(a)}}} = x - {shift}$. Все корни через запятую; '
                   f'если корней нет, напишите «нет».'),
        'answer': [root],
        'check': roots_check(expr),
        'budget_ms': 90_000,
        'note': 'Возведение в квадрат добавляет корни — проверьте каждый.',
    }


def exp_log_equation(rng):
    base = rng.choice([2, 3, 5])
    small = rng.choice([1, 2, 3])
    # t² − (bᵏ + 1)t + bᵏ = 0 по замене t = bˣ даёт корни x = 0 и x = k.
    power = base**small
    expr = base**(2 * x) - (power + 1) * base**x + power
    return {
        'prompt': (f'Решите уравнение ${base}^{{2x}} - {power + 1}\\cdot'
                   f'{base}^{{x}} + {power} = 0$. Все корни через запятую.'),
        'answer': [0, small],
        'check': set_check([0, small]),
        'budget_ms': 90_000,
        'note': f'Замена $t = {base}^x$.',
    }


def curve_meets_line(rng):
    first = rng.choice([-4, -3, -2, -1, 1, 2])
    second = first + rng.choice([2, 3, 4, 5])
    slope = rng.choice([1, 2, -1, -2])
    # (x − first)(x − second) = 0 после переноса прямой в левую часть.
    quad = sp.expand((x - first) * (x - second) + slope * x)
    line = sp.expand(slope * x)
    return {
        'prompt': (f'Найдите абсциссы точек пересечения кривой '
                   f'$y = {sp.latex(quad)}$ и прямой $y = {sp.latex(line)}$. '
                   f'Все значения через запятую, ответ точный.'),
        'answer': [first, second],
        'check': set_check([first, second]),
        'budget_ms': 75_000,
    }


def gdc_solve(rng):
    shift = rng.choice([2, 3, 4, 5])
    scale = rng.choice([1, 2])
    expr = sp.exp(x) + scale * x - shift
    value = float(sp.nsolve(expr, x, 0.5))
    body = f'e^x + {scale}x' if scale > 1 else 'e^x + x'
    return {
        'prompt': (f'Решите уравнение ${body} = {shift}$. Три значащие '
                   f'цифры (калькулятор).'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 60_000,
    }


def discriminant_condition(rng):
    const = rng.choice([2, 3, 5, 6, 7, 8])
    # x² − (m+1)x + c = 0 касается оси при (m+1)² = 4c.
    values = [-1 - 2 * sp.sqrt(const), -1 + 2 * sp.sqrt(const)]
    return {
        'prompt': (f'При каких значениях $m$ уравнение '
                   f'$x^2 - (m+1)x + {const} = 0$ имеет ровно один корень? '
                   f'Ответ точный, значения через запятую.'),
        'answer': values,
        'check': set_check(values),
        'budget_ms': 90_000,
    }


def solution_count(rng):
    a = rng.choice([1, 2, 3])
    b = rng.choice([-6, -5, -4, -3])
    expr = a * x**3 + b * x
    shift = rng.choice([0, 1, 2])
    # solveset на кубическом с иррациональными корнями возвращает
    # невычисленное пересечение, из которого длину не достать; real_roots
    # даёт сами корни, а set убирает кратные.
    count = len(set(sp.real_roots(sp.Poly(expr - shift, x))))
    return {
        'prompt': (f'Сколько действительных корней у уравнения '
                   f'${sp.latex(sp.Eq(expr, shift))}$?'),
        'answer': count,
        'check': count_check(count),
        'budget_ms': 60_000,
    }


GENERATORS = {
    'B1.zero_of_function': zero_of_function,
    'B1.quadratic_toolkit': quadratic_toolkit,
    'B1.equation_from_situation': equation_from_situation,
    'B1.extraneous_roots': extraneous_roots,
    'B1.exp_log_equation': exp_log_equation,
    'B1.curve_meets_line': curve_meets_line,
    'B1.gdc_solve': gdc_solve,
    'B1.discriminant_condition': discriminant_condition,
    'B1.solution_count': solution_count,
}
