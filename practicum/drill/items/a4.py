"""Задачи на счёт для практикума A4: многочлены.

Тема держится на двух вещах: остаток от деления читается подстановкой,
а связь корней с коэффициентами — формулами Виета. Обе проверяются
без раскрытия скобок, поэтому и спрашивать можно точный ответ.
"""
from __future__ import annotations

import sympy as sp

from .common import (apart_check, complex_check, equation_check, exact_check,
                     expr_check, poly_latex)

x = sp.Symbol('x')


def factor_remainder(rng):
    coefficients = [rng.choice([1, 2, 3]), rng.choice([-5, -3, -2, 2, 4]),
                    rng.choice([-7, -4, 1, 3, 6]), rng.choice([-9, -6, 2, 5])]
    poly = sum(c * x**(3 - i) for i, c in enumerate(coefficients))
    point = rng.choice([-3, -2, -1, 1, 2, 3])
    value = poly.subs(x, point)
    sign = '-' if point > 0 else '+'
    return {
        'prompt': (f'Найдите остаток от деления $P(x) = {sp.latex(poly)}$ '
                   f'на $(x {sign} {abs(point)})$.'),
        'answer': value,
        'check': exact_check(value),
        'budget_ms': 60_000,
    }


def polynomial_division(rng):
    root = rng.choice([-3, -2, -1, 1, 2, 3])
    quotient = (rng.choice([1, 2]) * x**2 + rng.choice([-4, -2, 1, 3]) * x
                + rng.choice([-6, -1, 2, 5]))
    remainder = rng.choice([-5, -2, 0, 3, 7])
    poly = sp.expand((x - root) * quotient + remainder)
    sign = '-' if root > 0 else '+'
    return {
        'prompt': (f'Разделите ${sp.latex(poly)}$ на $(x {sign} {abs(root)})$. '
                   f'Запишите **частное**.'),
        'answer': sp.expand(quotient),
        'check': expr_check(sp.expand(quotient)),
        'budget_ms': 105_000,
        'note': f'Остаток здесь равен ${remainder}$, его писать не нужно.',
    }


def repeated_root(rng):
    root = rng.choice([-3, -2, -1, 1, 2, 3])
    others = [n for n in [-4, -2, 1, 3, 5] if n != root]
    while True:
        other = rng.choice(others)
        poly = sp.expand((x - root)**2 * (x - other))
        coefficient = poly.coeff(x, 1)
        if coefficient != 0:      # k = 0 делает задачу вырожденной
            break
    # Показываем многочлен с буквой на месте искомого коэффициента:
    # собирать строку из знаков руками — верный способ ошибиться.
    shown = poly_latex([(1, 3), (poly.coeff(x, 2), 2), (sp.Symbol('k'), 1),
                        (poly.coeff(x, 0), 0)])
    return {
        'prompt': (f'У многочлена ${shown}$ есть кратный '
                   f'корень $x = {root}$. Найдите $k$.'),
        'answer': coefficient,
        'check': exact_check(coefficient),
        'budget_ms': 90_000,
        'note': 'Кратный корень — общий корень многочлена и его производной.',
    }


def vieta_quadratic(rng):
    b = rng.choice([-9, -7, -5, -3, 3, 5, 7])
    c = rng.choice([-8, -6, 2, 4, 9, 12])
    what = rng.choice(['squares', 'reciprocals', 'sum'])
    if what == 'squares':
        want, ask = b**2 - 2 * c, r'\alpha^2 + \beta^2'
    elif what == 'reciprocals':
        want, ask = sp.Rational(-b, c), r'\dfrac1\alpha + \dfrac1\beta'
    else:
        want, ask = sp.Integer(-b), r'\alpha + \beta'
    return {
        'prompt': (f'Корни уравнения $x^2 {"+" if b > 0 else "-"} {abs(b)}x '
                   f'{"+" if c > 0 else "-"} {abs(c)} = 0$ — это $\\alpha$ '
                   f'и $\\beta$. Найдите ${ask}$. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': 'Раскрывать корни не нужно — хватит формул Виета.',
    }


def vieta_higher(rng):
    a = rng.choice([1, 2])
    b = rng.choice([-6, -4, -2, 3, 5])
    c = rng.choice([-7, -3, 2, 8])
    d = rng.choice([-10, -5, 4, 9])
    what = rng.choice(['sum', 'pairs', 'product'])
    if what == 'sum':
        want, ask = sp.Rational(-b, a), r'\alpha + \beta + \gamma'
    elif what == 'pairs':
        want, ask = sp.Rational(c, a), r'\alpha\beta + \beta\gamma + \gamma\alpha'
    else:
        want, ask = sp.Rational(-d, a), r'\alpha\beta\gamma'
    poly = a * x**3 + b * x**2 + c * x + d
    return {
        'prompt': (f'Корни уравнения ${sp.latex(poly)} = 0$ — это $\\alpha$, '
                   f'$\\beta$, $\\gamma$. Найдите ${ask}$. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
    }


def conjugate_roots(rng):
    real = rng.choice([1, 2, 3, -1, -2])
    imaginary = rng.choice([1, 2, 3])
    third = rng.choice([-4, -2, 1, 5])
    root = real + imaginary * sp.I
    poly = sp.expand((x - root) * (x - sp.conjugate(root)) * (x - third))
    ask = rng.choice(['conjugate', 'third'])
    if ask == 'conjugate':
        want = sp.conjugate(root)
        question = ('Многочлен с действительными коэффициентами имеет корень '
                    f'${sp.latex(root)}$. Назовите ещё один его корень.')
        check = complex_check(want)
    else:
        want = sp.Integer(third)
        question = (f'У кубического многочлена ${sp.latex(poly)}$ есть корень '
                    f'${sp.latex(root)}$. Найдите его действительный корень.')
        check = exact_check(want)
    return {
        'prompt': question,
        'answer': want,
        'check': check,
        'budget_ms': 75_000,
    }


def symmetric_sums(rng):
    b = rng.choice([-6, -4, -2, 3, 5])
    c = rng.choice([-7, -3, 2, 8])
    d = rng.choice([-10, -5, 4, 9])
    # α² + β² + γ² = (Σα)² − 2Σαβ
    want = b**2 - 2 * c
    poly = x**3 + b * x**2 + c * x + d
    return {
        'prompt': (f'Корни уравнения ${sp.latex(poly)} = 0$ — это $\\alpha$, '
                   f'$\\beta$, $\\gamma$. Найдите '
                   f'$\\alpha^2 + \\beta^2 + \\gamma^2$. Ответ точный.'),
        'answer': sp.Integer(want),
        'check': exact_check(want),
        'budget_ms': 90_000,
    }


def root_transformation(rng):
    b = rng.choice([-7, -5, -3, 3, 5])
    c = rng.choice([-6, 2, 4, 8])
    factor = rng.choice([2, 3])
    # Корни умножаются на factor: подстановка x → x/factor.
    original = x**2 + b * x + c
    transformed = sp.expand(original.subs(x, sp.Rational(1, factor) * x)
                            * factor**2)
    return {
        'prompt': (f'Корни уравнения $x^2 {"+" if b > 0 else "-"} {abs(b)}x '
                   f'{"+" if c > 0 else "-"} {abs(c)} = 0$ — это $\\alpha$ '
                   f'и $\\beta$. Составьте уравнение с корнями '
                   f'${factor}\\alpha$ и ${factor}\\beta$.'),
        'answer': sp.Eq(transformed, 0),
        'check': equation_check(transformed),
        'budget_ms': 105_000,
        'note': 'Ответ — уравнение, например `x^2 - 4x + 3 = 0`.',
    }


def partial_fractions(rng):
    first = rng.choice([-3, -2, -1, 1])
    second = rng.choice([2, 3, 4, 5])
    top = rng.choice([1, 2, 3, 5])
    original = sp.Rational(top, 1) / ((x - first) * (x - second))
    return {
        'prompt': (f'Разложите $\\dfrac{{{top}}}{{(x {"-" if first > 0 else "+"} '
                   f'{abs(first)})(x - {second})}}$ на простейшие дроби.'),
        'answer': sp.apart(original, x),
        'check': apart_check(original),
        'budget_ms': 105_000,
    }


GENERATORS = {
    'A4.factor_remainder': factor_remainder,
    'A4.polynomial_division': polynomial_division,
    'A4.repeated_root': repeated_root,
    'A4.vieta_quadratic': vieta_quadratic,
    'A4.vieta_higher': vieta_higher,
    'A4.conjugate_roots': conjugate_roots,
    'A4.symmetric_sums': symmetric_sums,
    'A4.root_transformation': root_transformation,
    'A4.partial_fractions': partial_fractions,
}
