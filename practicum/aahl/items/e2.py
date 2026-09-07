"""Задачи на счёт для практикума E2: ряды Маклорена.

Тема — один обмен, повторённый девять раз: функцию отдают, многочлен
получают. Генераторы держатся того же разреза, что и лестница: первые
пять строят ряд (по определению, подстановкой, биномом, умножением,
подстановкой ряда в ряд), два следующих получают его из другого ряда
или прямо из уравнения, последние два им пользуются.

Три проверки здесь новые и живут в kit вместе с практикумом.
`maclaurin_check` эталона не хранит: он вычитает написанное из функции
и смотрит, с какой степени начинается остаток — а это и есть определение
ряда Маклорена. `series_solution_check` подставляет многочлен в само
дифференциальное уравнение, потому что функции там нет вовсе.
`terms_check` примеряет границу к члену n и к члену n + 1, потому что
вся потеря баллов приёма 9 — ошибка на единицу.
"""
from __future__ import annotations

import sympy as sp

from .common import (expr_check, maclaurin_check, num_check, poly_latex,
                     series_solution_check, terms_check)

x, y, k, n = sp.symbols('x y k n')
R = sp.Rational

ORDINAL = {2: 'x^{2}', 3: 'x^{3}', 4: 'x^{4}'}


def _upto(order):
    return f'до члена с ${ORDINAL[order]}$ включительно'


def from_derivatives(rng):
    """Производные даны соотношением: подставить 0 и поделить на n!."""
    p = rng.choice([1, 2, 3])
    q = rng.choice([1, 2])
    f = sp.exp(p * x) * sp.cos(q * x)
    # f'' = 2p f' - (p^2 + q^2) f — то же соотношение, что в мае 2022,
    # только с буквами. Проверено ниже в tests/test_drill.py.
    order = rng.choice([3, 4])
    return {
        'prompt': (f'Функция $f$ удовлетворяет соотношению '
                   f'$f\'\'(x) = {2 * p}f\'(x) - {p**2 + q**2}f(x)$, '
                   f'причём $f(0) = 1$ и $f\'(0) = {p}$. '
                   f'Найдите ряд Маклорена для $f$ {_upto(order)}.'),
        'answer': sp.expand(sp.series(f, x, 0, order + 1).removeO()),
        'check': maclaurin_check(f, order=order),
        'budget_ms': 150_000,
        'note': ('Подставить $x = 0$ в само соотношение: оно превращается '
                 'в числовую рекурсию и выдаёт производные по одной. '
                 'Каждую поделить на $n!$.'),
    }


def substitution(rng):
    """Известный ряд с новым аргументом: возводится в степень всё."""
    power = rng.choice([2, 3])
    a = rng.choice([1, 2, 3])
    base, name = rng.choice([
        (sp.sin, '\\sin'), (sp.tan, '\\tan'), (sp.atan, '\\arctan'),
    ])
    inner = a * x**power
    f = base(inner)
    return {
        'prompt': (f'Найдите первые два ненулевых члена ряда Маклорена '
                   f'для ${name}\\left({sp.latex(inner)}\\right)$.'),
        'answer': sp.expand(sp.series(f, x, 0, 4 * power + 1).removeO()),
        'check': maclaurin_check(f, terms=2),
        'budget_ms': 120_000,
        'note': (f'Подставить ${sp.latex(inner)}$ вместо $x$ целиком: '
                 f'куб аргумента даёт $x^{{{3 * power}}}$, а не '
                 f'$x^{{{power * 3 // 3 * 3 // power}}}$ и не $x^3$.'),
    }


def binomial_series(rng):
    """Скобка в нецелой или отрицательной степени."""
    a = rng.choice([1, 2, 3])
    p = rng.choice([R(-1), R(-2), R(-3), R(1, 2), R(-1, 2)])
    sign = rng.choice([1, -1])
    f = (1 + sign * a * x)**p
    inside = poly_latex([(1, 0), (sign * a, 1)])
    return {
        'prompt': (f'Найдите ряд Маклорена для '
                   f'$\\left({inside}\\right)^{{{sp.latex(p)}}}$ '
                   f'{_upto(2)}.'),
        'answer': sp.expand(sp.series(f, x, 0, 3).removeO()),
        'check': maclaurin_check(f, order=2),
        'budget_ms': 120_000,
        'note': ('Биномиальный ряд: $1 + pu + \\frac{p(p-1)}{2}u^2$, '
                 f'где $u = {poly_latex([(sign * a, 1)])}$. Знак внутри '
                 f'скобки едет вместе с $u$ и в квадрате исчезает.'),
    }


def product_of_series(rng):
    """Произведение двух известных рядов: глубина у множителей разная."""
    a = rng.choice([1, 2])
    b = rng.choice([1, 2, 3])
    f, shown = rng.choice([
        (sp.exp(a * x) * sp.sin(b * x),
         f'e^{{{poly_latex([(a, 1)])}}}\\sin {poly_latex([(b, 1)])}'),
        (sp.sqrt(1 + a * x) * sp.exp(b * x),
         f'\\sqrt{{1 + {poly_latex([(a, 1)])}}}\\;'
         f'e^{{{poly_latex([(b, 1)])}}}'),
        (sp.cos(a * x) * sp.log(1 + b * x),
         f'\\cos {poly_latex([(a, 1)])}\\,\\ln\\left(1 + '
         f'{poly_latex([(b, 1)])}\\right)'),
    ])
    return {
        'prompt': f'Найдите ряд Маклорена для ${shown}$ {_upto(3)}.',
        'answer': sp.expand(sp.series(f, x, 0, 4).removeO()),
        'check': maclaurin_check(f, order=3),
        'budget_ms': 180_000,
        'note': ('Разложить каждый множитель с запасом и перемножить, '
                 'отбрасывая лишние степени по ходу. Множителю, чей ряд '
                 'начинается с $x$, хватает на один член меньше.'),
    }


def composition(rng):
    """Внутрь ряда подставлен ряд: внутреннее обязано обнуляться в нуле."""
    a = rng.choice([1, 2])
    if rng.random() < 0.5:
        f = sp.exp(sp.cos(a * x) - 1)
        shown = f'e^{{\\cos {poly_latex([(a, 1)])} - 1}}'
        note = (f'$\\cos {poly_latex([(a, 1)])} - 1$ в нуле равно нулю — '
                f'поэтому подставлять его в $e^u$ можно. Квадрат внутреннего '
                f'ряда тоже даёт вклад в $x^4$.')
    else:
        f = sp.exp(sp.sin(a * x))
        shown = f'e^{{\\sin {poly_latex([(a, 1)])}}}'
        note = (f'$\\sin {poly_latex([(a, 1)])}$ в нуле равно нулю, значит '
                f'подставлять его в $e^u$ можно прямо. Нужны $u$, $u^2/2$ '
                f'и $u^3/6$.')
    order = 4 if 'cos' in shown else 3
    return {
        'prompt': f'Найдите ряд Маклорена для ${shown}$ {_upto(order)}.',
        'answer': sp.expand(sp.series(f, x, 0, order + 1).removeO()),
        'check': maclaurin_check(f, order=order),
        'budget_ms': 210_000,
        'note': note,
    }


def term_by_term(rng):
    """Ряд получается из другого ряда почленно."""
    a = rng.choice([1, 2, 3])
    if rng.random() < 0.5:
        f = a / (1 - a * x)**2
        return {
            'prompt': (f'Ряд Маклорена для $\\dfrac{{1}}'
                       f'{{1 - {poly_latex([(a, 1)])}}}$ — это '
                       f'$1 + {poly_latex([(a, 1)])} + '
                       f'{poly_latex([(a**2, 2)])} + \\dots$ '
                       f'Продифференцировав его почленно, найдите ряд '
                       f'Маклорена для $\\dfrac{{{a}}}'
                       f'{{\\left(1 - {poly_latex([(a, 1)])}\\right)^{{2}}}}$ '
                       f'{_upto(2)}.'),
            'answer': sp.expand(sp.series(f, x, 0, 3).removeO()),
            'check': maclaurin_check(f, order=2),
            'budget_ms': 150_000,
            'note': ('Дифференцировать обе части: слева почленно, справа '
                     'по правилу степени с цепочкой. Постоянная при '
                     'дифференцировании не появляется.'),
        }
    f = sp.log(1 + a * x)
    return {
        'prompt': (f'Ряд Маклорена для $\\dfrac{{{a}}}'
                   f'{{1 + {poly_latex([(a, 1)])}}}$ — это '
                   f'${a} - {poly_latex([(a**2, 1)])} + '
                   f'{poly_latex([(a**3, 2)])} - \\dots$ '
                   f'Проинтегрировав его почленно, найдите ряд Маклорена '
                   f'для $\\ln\\left(1 + {poly_latex([(a, 1)])}\\right)$ '
                   f'{_upto(3)}.'),
        'answer': sp.expand(sp.series(f, x, 0, 4).removeO()),
        'check': maclaurin_check(f, order=3),
        'budget_ms': 150_000,
        'note': ('Интегрировать почленно и найти постоянную подстановкой '
                 '$x = 0$: логарифм единицы — ноль, значит $C = 0$. '
                 'Это отдельный балл.'),
    }


def from_ode(rng):
    """Функции нет — есть уравнение и начальное условие."""
    a = rng.choice([1, 2, 3])
    c = rng.choice([1, 2, 3])
    rhs, shown = rng.choice([
        (a * y + x, f'{poly_latex([(a, 0)])}y + x'),
        (x * y + a, f'xy + {a}'),
        (y - a * x**2, f'y - {poly_latex([(a, 2)])}'),
    ])
    solution = sp.dsolve(sp.Eq(sp.Derivative(sp.Function('Y')(x), x),
                               rhs.subs(y, sp.Function('Y')(x))),
                         sp.Function('Y')(x),
                         ics={sp.Function('Y')(0): c}).rhs
    return {
        'prompt': (f'Функция $y$ задана уравнением '
                   f'$\\dfrac{{dy}}{{dx}} = {shown}$ и условием '
                   f'$y(0) = {c}$. Найдите первые четыре члена её ряда '
                   f'Маклорена.'),
        'answer': sp.expand(sp.series(solution, x, 0, 4).removeO()),
        'check': series_solution_check(rhs, c, 3),
        'budget_ms': 240_000,
        'note': ('Подставить $x = 0$ в уравнение — это $y\'(0)$. '
                 'Продифференцировать уравнение, помня, что $y$ зависит '
                 'от $x$, — это $y\'\'(0)$. И так далее; каждую поделить '
                 'на $n!$.'),
    }


def use_series(rng):
    """Ряд замещает функцию: подставить и проинтегрировать."""
    power = rng.choice([2, 3])
    top = rng.choice([1, 2])
    base, name, series = rng.choice([
        (sp.sin, '\\sin', lambda u: u - u**3 / 6),
        (sp.atan, '\\arctan', lambda u: u - u**3 / 3),
    ])
    inner = x**power
    poly = sp.expand(series(inner))
    want = sp.integrate(poly, (x, 0, R(1, top)))
    limit = '1' if top == 1 else f'\\frac{{1}}{{{top}}}'
    return {
        'prompt': (f'Первые два ненулевых члена ряда Маклорена для '
                   f'${name} u$ — это ${sp.latex(series(sp.Symbol("u")))}$. '
                   f'Пользуясь ими, найдите приближённое значение '
                   f'$\\displaystyle\\int_{{0}}^{{{limit}}} '
                   f'{name}\\left({sp.latex(inner)}\\right)\\,dx$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': expr_check(want),
        'budget_ms': 180_000,
        'note': (f'Подставить $u = {sp.latex(inner)}$ в ряд, получить '
                 f'многочлен и проинтегрировать его почленно. Саму функцию '
                 f'интегрировать бессмысленно: первообразной в замкнутом '
                 f'виде у неё нет.'),
    }


def error_bound(rng):
    """Сколько членов знакочередующегося ряда нужно взять."""
    root = rng.choice([2, 3, 5])
    power = rng.choice([3, 4, 5])
    bound = R(1, 10**power)
    point = 1 / sp.sqrt(root)
    term = point**(2 * k - 1) / (2 * k - 1)
    # Наименьшее n, при котором член n + 1 уже меньше границы.
    want = 1
    while abs(float(term.subs(k, want + 1))) >= float(bound):
        want += 1
    return {
        'prompt': (f'Ряд Маклорена для $\\arctan x$ — это '
                   f'$x - \\frac{{x^{{3}}}}{{3}} + \\frac{{x^{{5}}}}{{5}} '
                   f'- \\dots$, и он знакочередующийся. Сколько ненулевых '
                   f'членов нужно взять при '
                   f'$x = \\frac{{1}}{{\\sqrt{{{root}}}}}$, чтобы ошибка '
                   f'была меньше $10^{{-{power}}}$?'),
        'answer': sp.Integer(want),
        'check': terms_check(term, bound),
        'budget_ms': 180_000,
        'note': ('Ошибка от $n$ членов не превосходит члена номер $n + 1$. '
                 'Перебрать номера, найти первый член меньше границы — '
                 'и вычесть единицу: это номер первого отброшенного.'),
    }


GENERATORS = {
    'E2.from_derivatives': from_derivatives,
    'E2.substitution': substitution,
    'E2.binomial_series': binomial_series,
    'E2.product_of_series': product_of_series,
    'E2.composition': composition,
    'E2.term_by_term': term_by_term,
    'E2.from_ode': from_ode,
    'E2.use_series': use_series,
    'E2.error_bound': error_bound,
}
