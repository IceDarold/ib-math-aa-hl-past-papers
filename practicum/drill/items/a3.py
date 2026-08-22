"""Задачи на счёт для практикума A3: биномиальная теорема.

Почти вся тема — прочтения одной формулы общего члена, поэтому и задачи
однотипны по виду и различаются тем, что именно спрашивают: весь ряд,
один член, коэффициент как условие на букву.
"""
from __future__ import annotations

import sympy as sp

from .common import complex_check, exact_check, num_check, series_check

x = sp.Symbol('x')


def full_expansion(rng):
    a = rng.choice([1, 2, 3])
    b = rng.choice([-3, -2, -1, 1, 2, 3])
    n = rng.choice([3, 4, 5])
    expr = sp.expand((a + b * x)**n)
    shown = f'{a} {"+" if b > 0 else "-"} {abs(b) if abs(b) != 1 else ""}x'
    return {
        'prompt': (f'Раскройте $({shown})^{{{n}}}$ полностью. '
                   f'Ответ — многочлен.'),
        'answer': expr,
        'check': series_check(expr),
        'budget_ms': 90_000,
    }


def general_term(rng):
    n = rng.choice([6, 7, 8, 9, 10])
    a = rng.choice([1, 2, 3])
    b = rng.choice([-3, -2, -1, 1, 2])
    p = rng.choice([1, 2])
    # Степень k-го члена: p(n − k) − k. Формулу берём прямо, а не через
    # разложение: sp.degree на отрицательных степенях спотыкается.
    powers = {k: p * (n - k) - k for k in range(n + 1)}
    # Экзамен спрашивает про неотрицательные степени и про свободный член,
    # отрицательные оставляем за скобками.
    which = rng.choice([k for k, power in powers.items() if power >= 0])
    power = powers[which]
    coefficient = sp.binomial(n, which) * a**(n - which) * b**which
    top = f'{a if a != 1 else ""}x^{{{p}}}' if p > 1 else f'{a if a != 1 else ""}x'
    tail = f'{"+" if b > 0 else "-"} \\dfrac{{{abs(b)}}}{{x}}'
    return {
        'prompt': (f'Найдите коэффициент при $x^{{{power}}}$ в разложении '
                   f'$\\left({top} {tail}\\right)^{{{n}}}$.'),
        'answer': coefficient,
        'check': exact_check(coefficient),
        'budget_ms': 90_000,
    }


def equate_coefficients(rng):
    m = rng.choice([5, 6, 7, 8, 9, 10])
    c = rng.choice([2, 3, 4, 5])
    first = m * c
    second = sp.binomial(m, 2) * c**2
    return {
        'prompt': (f'В разложении $(1 + cx)^m$ первые три члена равны '
                   f'$1 + {first}x + {second}x^2$. Найдите $m$.'),
        'answer': m,
        'check': exact_check(m),
        'budget_ms': 90_000,
        'note': 'Два уравнения на две буквы; делить одно на другое удобнее.',
    }


def coefficients_as_sequence(rng):
    # Коэффициенты при x, x², x³ в (1+x)^n образуют арифметическую
    # прогрессию ровно при n = 7 и n = 14; берём одно из них и спрашиваем
    # проверяемое следствие — сам коэффициент.
    n = rng.choice([7, 14])
    which = rng.choice([1, 2, 3])
    coefficient = sp.binomial(n, which)
    return {
        'prompt': (f'Коэффициенты при $x$, $x^2$ и $x^3$ в разложении '
                   f'$(1+x)^n$ образуют арифметическую прогрессию, причём '
                   f'$n = {n}$. Найдите коэффициент при $x^{{{which}}}$.'),
        'answer': coefficient,
        'check': exact_check(coefficient),
        'budget_ms': 75_000,
    }


def fractional_index(rng):
    a = rng.choice([-3, -2, -1, 1, 2, 3])
    power = rng.choice([sp.Rational(1, 2), sp.Rational(-1, 2), -1, -2])
    series = sp.series((1 + a * x)**power, x, 0, 3).removeO()
    shown = f'1 {"+" if a > 0 else "-"} {abs(a) if abs(a) != 1 else ""}x'
    return {
        'prompt': (f'Разложите $({shown})^{{{sp.latex(power)}}}$ по степеням '
                   f'$x$ до члена с $x^2$ включительно.'),
        'answer': sp.expand(series),
        'check': series_check(sp.expand(series)),
        'budget_ms': 120_000,
        'note': 'Ответ — три слагаемых.',
    }


def product_and_approximation(rng):
    a = rng.choice([1, 2, 3])
    b = rng.choice([-3, -2, -1, 1, 2])
    m = rng.choice([3, 4, 5])
    k = rng.choice([3, 4, 5])
    product = sp.expand((1 + a * x)**m * (1 + b * x)**k)
    coefficient = product.coeff(x, 2)
    left = f'(1 {"+" if a > 0 else "-"} {abs(a) if abs(a) != 1 else ""}x)^{{{m}}}'
    right = f'(1 {"+" if b > 0 else "-"} {abs(b) if abs(b) != 1 else ""}x)^{{{k}}}'
    return {
        'prompt': (f'Найдите коэффициент при $x^2$ в разложении '
                   f'${left}\\,{right}$.'),
        'answer': coefficient,
        'check': exact_check(coefficient),
        'budget_ms': 105_000,
        'note': 'Достаточно членов до x² в каждой скобке.',
    }


def binomial_with_i(rng):
    n = rng.choice([3, 4, 5, 6, 8])
    base = rng.choice([1 + sp.I, 1 - sp.I, 2 + 2 * sp.I])
    value = sp.expand(base**n)
    return {
        'prompt': (f'Вычислите ${sp.latex(base)}$ в степени ${n}$. '
                   f'Ответ в виде $a + bi$.'),
        'answer': value,
        'check': complex_check(value),
        'budget_ms': 90_000,
    }


GENERATORS = {
    'A3.full_expansion': full_expansion,
    'A3.general_term': general_term,
    'A3.equate_coefficients': equate_coefficients,
    'A3.coefficients_as_sequence': coefficients_as_sequence,
    'A3.fractional_index': fractional_index,
    'A3.product_and_approximation': product_and_approximation,
    'A3.binomial_with_i': binomial_with_i,
}
