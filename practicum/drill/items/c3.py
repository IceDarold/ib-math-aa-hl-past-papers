"""Задачи на счёт для практикума C3: тригонометрические уравнения.

Главное здесь не решить, а не потерять корни: область задана в условии,
и ответ проверяется сканированием отрезка, а не сверкой с эталоном.
Поэтому и потерянный корень, и лишний видны по отдельности.
"""
from __future__ import annotations

import sympy as sp

from .common import count_check, exact_check, num_check, roots_in_check

x = sp.Symbol('x')
PI = sp.pi


def _roots_in(expression, high, low=0):
    """Все корни на замкнутом отрезке, включая концы.

    Концы важны: на отрезке 0 ≤ x ≤ 2π у cos x = 1 корня два, и второй
    из них — ровно 2π. Сканирование его не находит, поэтому проверка
    в check.py досчитывает количество точно.
    """
    return sorted(sp.solveset(expression, x, sp.Interval(low, high)),
                  key=float)


def reference_angle(rng):
    which = rng.choice(['sin', 'cos'])
    numerator, denominator = rng.choice([(1, 2), (-1, 2), (1, 1), (-1, 1)])
    value = sp.Rational(numerator, denominator)
    function = sp.sin if which == 'sin' else sp.cos
    expression = function(x) - value
    return {
        'prompt': (f'Решите $\\{which} x = {sp.latex(value)}$ на отрезке '
                   f'$0 \\le x \\le 2\\pi$. Все корни через запятую, точные.'),
        'answer': _roots_in(expression, 2 * PI),
        'check': roots_in_check(expression, (0, 2 * PI)),
        'budget_ms': 90_000,
    }


def compound_argument(rng):
    inner = rng.choice([2, 3])
    shift = rng.choice([sp.Rational(1, 6), sp.Rational(1, 4),
                        sp.Rational(1, 3), sp.Rational(-1, 4)])
    value = rng.choice([sp.Rational(1, 2), sp.Rational(-1, 2), sp.Integer(0)])
    expression = sp.sin(inner * x + shift * PI) - value
    sign = '+' if shift > 0 else '-'
    return {
        'prompt': (f'Решите $\\sin\\left({inner}x {sign} '
                   f'{sp.latex(sp.nsimplify(abs(shift) * PI))}\\right) = '
                   f'{sp.latex(value)}$ на отрезке $0 \\le x \\le \\pi$. '
                   f'Все корни через запятую, точные.'),
        'answer': _roots_in(expression, PI),
        'check': roots_in_check(expression, (0, PI)),
        'budget_ms': 150_000,
        'note': 'Область для внутреннего выражения тоже меняется.',
    }


EXACT_SUM = {
    (15, 'sin'): (sp.sqrt(6) - sp.sqrt(2)) / 4,
    (75, 'sin'): (sp.sqrt(6) + sp.sqrt(2)) / 4,
    (15, 'cos'): (sp.sqrt(6) + sp.sqrt(2)) / 4,
    (75, 'cos'): (sp.sqrt(6) - sp.sqrt(2)) / 4,
    (105, 'sin'): (sp.sqrt(6) + sp.sqrt(2)) / 4,
    (105, 'cos'): (sp.sqrt(2) - sp.sqrt(6)) / 4,
}


def angle_sum(rng):
    degrees, which = rng.choice(sorted(EXACT_SUM))
    want = sp.nsimplify(EXACT_SUM[(degrees, which)])
    return {
        'prompt': (f'Найдите **точное** значение $\\{which} {degrees}^\\circ$, '
                   f'разложив угол на сумму или разность табличных.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 120_000,
        'note': 'Десятичная дробь здесь не принимается.',
    }


def pythagorean_reduction(rng):
    a = rng.choice([2, 3])
    b = rng.choice([-3, -1, 1, 3])
    # a·cos²x + b·sin x + c = 0 после замены cos² = 1 − sin².
    c = rng.choice([-2, -1, 0, 1])
    expression = a * sp.cos(x)**2 + b * sp.sin(x) + c
    roots = _roots_in(expression, 2 * PI)
    if not roots:
        expression = a * sp.cos(x)**2 + b * sp.sin(x) - a
        roots = _roots_in(expression, 2 * PI)
    return {
        'prompt': (f'Решите ${sp.latex(sp.Eq(expression, 0))}$ на отрезке '
                   f'$0 \\le x \\le 2\\pi$. Все корни через запятую, точные.'),
        'answer': roots,
        'check': roots_in_check(expression, (0, 2 * PI)),
        'budget_ms': 150_000,
        'note': 'Пифагорово тождество приводит это к квадратному.',
    }


def double_angle_reduction(rng):
    b = rng.choice([1, 2, 3])
    c = rng.choice([-1, 0, 1])
    expression = sp.cos(2 * x) + b * sp.sin(x) + c
    roots = _roots_in(expression, 2 * PI)
    if not roots:
        expression = sp.cos(2 * x) + b * sp.sin(x) - 1
        roots = _roots_in(expression, 2 * PI)
    return {
        'prompt': (f'Решите ${sp.latex(sp.Eq(expression, 0))}$ на отрезке '
                   f'$0 \\le x \\le 2\\pi$. Все корни через запятую, точные.'),
        'answer': roots,
        'check': roots_in_check(expression, (0, 2 * PI)),
        'budget_ms': 150_000,
        'note': 'Двойной угол — через одну и ту же функцию.',
    }


def factor_not_divide(rng):
    which = rng.choice(['sin', 'cos'])
    if which == 'sin':
        expression = sp.sin(2 * x) - sp.sin(x)
        shown = r'\sin 2x = \sin x'
    else:
        expression = sp.sin(2 * x) - sp.cos(x)
        shown = r'\sin 2x = \cos x'
    roots = _roots_in(expression, 2 * PI)
    return {
        'prompt': (f'Решите ${shown}$ на отрезке $0 \\le x \\le 2\\pi$. '
                   f'Все корни через запятую, точные.'),
        'answer': roots,
        'check': roots_in_check(expression, (0, 2 * PI)),
        'budget_ms': 150_000,
        'note': 'Делить на общий множитель нельзя — он даёт свои корни.',
    }


def reduce_to_tangent(rng):
    a = rng.choice([1, 2, 3])
    b = rng.choice([1, 2, 3])
    expression = a * sp.sin(x) - b * sp.cos(x)
    roots = _roots_in(expression, 2 * PI)
    left = f'{a if a != 1 else ""}\\sin x'
    right = f'{b if b != 1 else ""}\\cos x'
    return {
        'prompt': (f'Решите ${left} = {right}$ на отрезке '
                   f'$0 \\le x \\le 2\\pi$. Все корни через запятую, точные.'),
        'answer': roots,
        'check': roots_in_check(expression, (0, 2 * PI)),
        'budget_ms': 120_000,
        'note': 'Разделите на cos x — но проверьте, не терялись ли корни.',
    }


def root_selection(rng):
    inner = rng.choice([2, 3, 4])
    value = rng.choice([sp.Rational(1, 2), sp.Rational(-1, 2), sp.Integer(0),
                        sp.Integer(1)])
    expression = sp.sin(inner * x) - value
    count = len(_roots_in(expression, 2 * PI))
    return {
        'prompt': (f'Сколько корней у уравнения $\\sin {inner}x = '
                   f'{sp.latex(value)}$ на отрезке $0 \\le x \\le 2\\pi$?'),
        'answer': count,
        'check': count_check(count),
        'budget_ms': 90_000,
        'note': 'Внутренний аргумент пробегает отрезок в несколько раз длиннее.',
    }


def numeric_gdc(rng):
    a = rng.choice([1, 2])
    b = rng.choice([2, 3, 4])
    # a·cos x = x/b — трансцендентное, точного ответа нет.
    expression = a * sp.cos(x) - x / b
    value = float(sp.nsolve(expression, x, 1.0))
    left = f'{a if a != 1 else ""}\\cos x'
    return {
        'prompt': (f'Решите ${left} = \\dfrac{{x}}{{{b}}}$ при $x > 0$. '
                   f'Наименьший корень, три значащие цифры (калькулятор).'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 90_000,
    }


GENERATORS = {
    'C3.reference_angle': reference_angle,
    'C3.compound_argument': compound_argument,
    'C3.angle_sum': angle_sum,
    'C3.pythagorean_reduction': pythagorean_reduction,
    'C3.double_angle_reduction': double_angle_reduction,
    'C3.factor_not_divide': factor_not_divide,
    'C3.reduce_to_tangent': reduce_to_tangent,
    'C3.root_selection': root_selection,
    'C3.numeric_gdc': numeric_gdc,
}
