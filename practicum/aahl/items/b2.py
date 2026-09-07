"""Задачи на счёт для практикума B2: композиция и обратные функции.

Практикум английский, а тренажёр русский, и это не противоречие: коды
приёмов общие, а условия задач пишутся на языке того, кто их читает.

Два вида проверки здесь свои. Обратная функция сверяется не с эталоном,
а подстановкой исходной функции внутрь ответа: у ответа с корнем ветвей
две, и выбирает её область из условия. Область определения сверяется как
множество — запись свободна, концы нет.
"""
from __future__ import annotations

import sympy as sp

from .common import (domain_check, exact_check, inverse_check, roots_check,
                     series_check)

x = sp.Symbol('x')
k = sp.Symbol('k')


def _sign(value):
    return '+' if value >= 0 else '-'


def evaluate_composite(rng):
    a = rng.choice([2, 3, 4, 5])
    b = rng.choice([-7, -5, -3, 3, 5, 7])
    p = rng.choice([-4, -3, -2, 2, 3, 4])
    v = rng.choice([1, 2, 3, 4])
    outer = a * x + b
    inner = x**2 + p * x
    want = outer.subs(x, inner.subs(x, v))
    return {
        'prompt': (f'$f(x) = {a}x {_sign(b)} {abs(b)}$ и '
                   f'$g(x) = x^2 {_sign(p)} {abs(p)}x$. '
                   f'Найдите $(f \\circ g)({v})$.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 45_000,
        'note': 'Сначала внутренняя функция, потом внешняя.',
    }


def build_composite(rng):
    p = rng.choice([-5, -4, -3, -2, 2, 3, 4, 5])
    q = rng.choice([-9, -7, -4, 4, 7, 9])
    want = sp.expand((x + p)**2 + q)
    return {
        'prompt': (f'$f(x) = x {_sign(p)} {abs(p)}$ и '
                   f'$g(x) = x^2 {_sign(q)} {abs(q)}$. '
                   f'Запишите $(g \\circ f)(x)$, раскрыв скобки.'),
        'answer': want,
        'check': series_check(want),
        'budget_ms': 60_000,
    }


def composite_equation(rng):
    p = rng.choice([2, 3, 4, 5])
    v = rng.choice([1, 6, 7, 8, 9])
    s = rng.choice([1, 2, 3, 4, 5])
    total = (v - p)**2 + s**2
    return {
        'prompt': (f'$f(x) = x - {p}$ и $g(x) = x^2 + k^2$, где $k$ — '
                   f'действительная постоянная. Дано, что '
                   f'$(g \\circ f)({v}) = {total}$. Найдите все значения $k$.'),
        'answer': [-s, s],
        'check': roots_check(k**2 - s**2, var='k'),
        'budget_ms': 75_000,
        'note': 'Значений два: k² = s² даёт оба знака.',
    }


def parity_test(rng):
    a = rng.choice([1, 2, 3])
    b = rng.choice([-5, -3, -2, 2, 3, 5])
    c = rng.choice([-7, -4, 4, 7])
    f = a * x**4 + b * x**3 + c * x
    want = sp.expand(f.subs(x, -x))
    return {
        'prompt': (f'$f(x) = {a}x^4 {_sign(b)} {abs(b)}x^3 '
                   f'{_sign(c)} {abs(c)}x$. Запишите $f(-x)$, раскрыв скобки.'),
        'answer': want,
        'check': series_check(want),
        'budget_ms': 60_000,
        'note': 'Чётные степени знак не меняют, нечётные меняют.',
    }


def iterate_function(rng):
    m = rng.choice([-3, -2, 2, 3])
    c = rng.choice([-5, -3, -1, 1, 3, 5])
    f = m * x + c
    want = sp.expand(f.subs(x, f.subs(x, f)))
    return {
        'prompt': (f'$f(x) = {m}x {_sign(c)} {abs(c)}$. Найдите '
                   f'$f^3(x) = f(f(f(x)))$, раскрыв скобки.'),
        'answer': want,
        'check': series_check(want),
        'budget_ms': 75_000,
        'note': 'f³ — это тройная композиция, а не куб значения.',
    }


def inverse_property(rng):
    s = rng.choice([1, 2, 3])
    power = rng.choice([1, 2, 3, 4, 5, 6, 7, 8, 9])
    base, target = 2**s, 2**power
    want = sp.Rational(power, s)
    return {
        'prompt': (f'$f(x) = {base}^x$. Найдите $f^{{-1}}({target})$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'f⁻¹(a) = b означает f(b) = a — решайте уравнение.',
    }


def inverse_by_swap(rng):
    a = rng.choice([1, 2, 3, 4])
    b = rng.choice([-7, -5, -3, 3, 5, 7])
    c = rng.choice([1, 2])
    d = rng.choice([-6, -4, -2, 2, 4, 6])
    while a * d - b * c == 0:
        d = rng.choice([-6, -4, -2, 2, 4, 6])
    f = (a * x + b) / (c * x + d)
    pole = sp.Rational(-d, c)
    want = sp.simplify(sp.solve(sp.Eq(sp.Symbol('y'), f), x)[0]
                       .subs(sp.Symbol('y'), x))
    return {
        'prompt': (f'$f(x) = \\dfrac{{{a}x {_sign(b)} {abs(b)}}}'
                   f'{{{c}x {_sign(d)} {abs(d)}}}$. Найдите $f^{{-1}}(x)$.'),
        'answer': want,
        'check': inverse_check(f, domain=sp.Interval(pole + 1, pole + 9)),
        'budget_ms': 90_000,
        'note': 'Поменяйте x и y, соберите y с одной стороны, вынесите его.',
    }


def inverse_domain(rng):
    c = rng.choice([-4, -3, -1, 0, 2, 5])
    h = rng.choice([2, 3, 4, 5])
    tail = f' {_sign(c)} {abs(c)}' if c else ''
    return {
        'prompt': (f'$f(x) = x^2{tail}$, где $0 \\le x \\le {h}$. '
                   f'Запишите неравенством область определения $f^{{-1}}$.'),
        'answer': sp.Interval(c, h**2 + c),
        'check': domain_check(sp.Interval(c, h**2 + c)),
        'budget_ms': 75_000,
        'note': 'Область обратной — это множество значений исходной.',
    }


def inverse_branch(rng):
    h = rng.choice([1, 2, 3, 4, 5])
    right = rng.choice([True, False])
    f = (x - h)**2
    if right:
        domain = sp.Interval(h, h + 6)
        want = h + sp.sqrt(x)
        where = f'x \\ge {h}'
    else:
        domain = sp.Interval(h - 6, h)
        want = h - sp.sqrt(x)
        where = f'x \\le {h}'
    return {
        'prompt': (f'$f(x) = (x - {h})^2$, где ${where}$. '
                   f'Найдите $f^{{-1}}(x)$, выбрав верную ветвь.'),
        'answer': want,
        'check': inverse_check(f, domain=domain),
        'budget_ms': 90_000,
        'note': 'Значения f⁻¹ обязаны лежать в области f — это и выбирает знак.',
    }


GENERATORS = {
    'B2.evaluate_composite': evaluate_composite,
    'B2.build_composite': build_composite,
    'B2.composite_equation': composite_equation,
    'B2.parity_test': parity_test,
    'B2.iterate_function': iterate_function,
    'B2.inverse_property': inverse_property,
    'B2.inverse_by_swap': inverse_by_swap,
    'B2.inverse_domain': inverse_domain,
    'B2.inverse_branch': inverse_branch,
}
