"""Задачи на счёт для практикума A8: неравенства.

Ответ здесь — множество, и проверка сверяет его с самим неравенством:
эталона нет, sympy решает условие сам. Концы входят в сравнение, потому
что в markscheme строгое и нестрогое — разные баллы.
"""
from __future__ import annotations

import sympy as sp

from .common import (count_check, exact_check, num_check, poly_latex,
                     solution_set_check)

x = sp.Symbol('x')
k = sp.Symbol('k')


def critical_values(rng):
    first = rng.choice([-4, -3, -2, -1])
    second = rng.choice([1, 2, 3, 4])
    strict = rng.random() < 0.5
    positive = rng.random() < 0.5
    quadratic = sp.expand((x - first) * (x - second))
    if positive:
        inequality = quadratic > 0 if strict else quadratic >= 0
    else:
        inequality = quadratic < 0 if strict else quadratic <= 0
    sign = ('>' if strict else r'\ge') if positive else ('<' if strict else r'\le')
    return {
        'prompt': (f'Решите ${poly_latex([(1, 2), (quadratic.coeff(x, 1), 1), (quadratic.coeff(x, 0), 0)])} '
                   f'{sign} 0$. Ответ неравенством, например `x < -2 or x > 3`.'),
        'answer': inequality.as_set(),
        'check': solution_set_check(inequality),
        'budget_ms': 90_000,
    }


def rational_inequality(rng):
    top = rng.choice([-3, -2, -1, 1, 2, 3])
    bottom = rng.choice([-4, -2, 2, 4])
    while top == bottom:
        bottom = rng.choice([-4, -2, 2, 4])
    expression = (x - top) / (x - bottom)
    inequality = expression > 0 if rng.random() < 0.5 else expression < 0
    return {
        'prompt': (f'Решите ${sp.latex(inequality)}$. '
                   f'Ответ неравенством.'),
        'answer': inequality.as_set(),
        'check': solution_set_check(inequality),
        'budget_ms': 105_000,
        'note': 'Знаменатель в ноль не обращается — эта точка выпадает.',
    }


def absolute_value(rng):
    inner = rng.choice([1, 2, 3])
    shift = rng.choice([-5, -3, -1, 2, 4])
    bound = rng.choice([1, 2, 3, 5, 7])
    less = rng.random() < 0.5
    expression = sp.Abs(inner * x + shift)
    inequality = expression < bound if less else expression > bound
    return {
        'prompt': (f'Решите ${sp.latex(inequality)}$. Ответ неравенством.'),
        'answer': inequality.as_set(),
        'check': solution_set_check(inequality),
        'budget_ms': 105_000,
    }


def gdc_intervals(rng):
    a = rng.choice([1, 2])
    b = rng.choice([2, 3, 4, 5])
    # x³ − bx > a: границы иррациональные, экзамен просит три знака.
    expression = a * x**3 - b * x - 1
    roots = sorted(sp.Poly(expression, x).real_roots(), key=float)
    value = float(roots[-1])
    return {
        'prompt': (f'Решите ${poly_latex([(a, 3), (-b, 1)])} > 1$ '
                   f'(калькулятор). Назовите наибольшее критическое значение, '
                   f'три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 90_000,
        'note': 'Критические значения — там, где обе части равны.',
    }


def discriminant_condition(rng):
    b = rng.choice([2, 4, 6])
    # x² + bx + k > 0 при всех x ⟺ дискриминант отрицателен ⟺ k > b²/4.
    threshold = sp.Rational(b**2, 4)
    inequality = k > threshold
    return {
        'prompt': (f'При каких значениях $k$ выражение '
                   f'$x^2 + {b}x + k$ положительно при всех действительных '
                   f'$x$? Ответ неравенством относительно $k$.'),
        'answer': inequality.as_set(),
        'check': solution_set_check(inequality, var='k'),
        'budget_ms': 105_000,
        'note': 'Условие на дискриминант, а не на корни.',
    }


def root_signs(rng):
    total = rng.choice([5, 6, 7, 8])
    product = rng.choice([4, 6, 8, 9])
    ask = rng.choice(['sum', 'product', 'both'])
    if ask == 'sum':
        want, question = sp.Integer(total), 'сумму корней'
    elif ask == 'product':
        want, question = sp.Integer(product), 'произведение корней'
    else:
        want, question = sp.Integer(total**2 - 2 * product), 'сумму их квадратов'
    return {
        'prompt': (f'Оба корня уравнения $x^2 - {total}x + {product} = 0$ '
                   f'положительны. Найдите {question}. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': 'Знаки корней читаются из Виета, сами корни не нужны.',
    }


def solution_count(rng):
    first = rng.choice([-5, -4, -3])
    second = rng.choice([2, 3, 4, 5])
    quadratic = sp.expand((x - first) * (x - second))
    solution = (quadratic < 0).as_set()
    count = len([n for n in range(first, second + 1) if solution.contains(n)])
    return {
        'prompt': (f'Сколько **целых** решений у неравенства '
                   f'${poly_latex([(1, 2), (quadratic.coeff(x, 1), 1), (quadratic.coeff(x, 0), 0)])} < 0$?'),
        'answer': count,
        'check': count_check(count),
        'budget_ms': 90_000,
        'note': 'Концы отрезка в строгое неравенство не входят.',
    }


def prove_inequality(rng):
    coefficient = rng.choice([1, 4, 9, 16, 25])
    # x + c/x ≥ 2√c при x > 0, равенство при x = √c.
    point = sp.sqrt(coefficient)
    ask = rng.choice(['point', 'value'])
    if ask == 'point':
        want = sp.nsimplify(point)
        question = 'при каком $x$ достигается наименьшее значение'
    else:
        want = sp.nsimplify(2 * point)
        question = 'чему равно наименьшее значение'
    return {
        'prompt': (f'При $x > 0$ рассмотрите $x + \\dfrac{{{coefficient}}}{{x}}$. '
                   f'Найдите, {question}. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 105_000,
        'note': 'Неравенство о средних: сумма не меньше удвоенного корня '
                'из произведения.',
    }


GENERATORS = {
    'A8.critical_values': critical_values,
    'A8.rational_inequality': rational_inequality,
    'A8.absolute_value': absolute_value,
    'A8.gdc_intervals': gdc_intervals,
    'A8.discriminant_condition': discriminant_condition,
    'A8.root_signs': root_signs,
    'A8.solution_count': solution_count,
    'A8.prove_inequality': prove_inequality,
}
