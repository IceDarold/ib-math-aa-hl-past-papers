"""Задачи на счёт для практикума A7: доказательства.

Здесь честное ограничение: доказательство напечатанным ответом не
проверить. Проверять «покажите, что» тренажёр не умеет и не притворяется,
что умеет.

Зато у каждого доказательства из темы есть счётное ядро — то место, где
на экзамене и теряют баллы: чему равна база индукции, что остаётся после
вычитания S(k+1) − S(k), какой множитель выносится в задаче на делимость.
Эти куски и спрашиваются. Приём тренируется, полное доказательство
остаётся за практикумом.
"""
from __future__ import annotations

import sympy as sp

from .common import count_check, exact_check, expr_check, num_check

a, b, n, k = sp.symbols('a b n k')
x = sp.Symbol('x')


def direct_proof(rng):
    which = rng.choice(['squares', 'consecutive', 'odd'])
    if which == 'squares':
        want, shown, letters = 4 * a * b, '(a+b)^2 - (a-b)^2', 'a и b'
    elif which == 'consecutive':
        want, shown, letters = 2 * n + 1, '(n+1)^2 - n^2', 'n'
    else:
        want, shown, letters = 8 * n, '(2n+1)^2 - (2n-1)^2', 'n'
    return {
        'prompt': (f'Раскройте и упростите ${shown}$. '
                   f'Ответ — выражение через ${letters}$.'),
        'answer': sp.expand(want),
        'check': expr_check(want),
        'budget_ms': 60_000,
    }


def integer_representation(rng):
    which = rng.choice(['three', 'squares', 'even'])
    if which == 'three':
        want = 3 * n + 3
        question = ('Сумма трёх последовательных целых, наименьшее из которых '
                    'равно $n$.')
    elif which == 'squares':
        want = 2 * n**2 + 2 * n + 1
        question = ('Сумма квадратов двух последовательных целых, меньшее '
                    'из которых равно $n$.')
    else:
        want = 4 * n**2 + 4 * n
        question = ('Произведение двух последовательных чётных чисел, '
                    'меньшее из которых равно $2n$.')
    return {
        'prompt': f'{question} Запишите её через $n$ и упростите.',
        'answer': sp.expand(want),
        'check': expr_check(want),
        'budget_ms': 75_000,
        'note': 'Проверять делимость удобно уже после упрощения.',
    }


def contradiction(rng):
    which = rng.choice(['odd_square', 'mod3', 'even'])
    if which == 'odd_square':
        want = 1
        question = ('Нечётное число возвели в квадрат. Каков остаток от '
                    'деления результата на $8$?')
    elif which == 'mod3':
        want = 1
        question = ('Целое $p$ не делится на $3$. Каков остаток от деления '
                    '$p^2$ на $3$?')
    else:
        want = 0
        question = ('В доказательстве иррациональности $\\sqrt2$ получили '
                    '$p^2 = 2q^2$. Каков остаток от деления $p$ на $2$?')
    return {
        'prompt': question,
        'answer': want,
        'check': count_check(want),
        'budget_ms': 90_000,
        'note': 'Здесь и рождается противоречие: тот же вывод получается '
                'и для второго числа.',
    }


def induction_skeleton(rng):
    which = rng.choice(['sum', 'squares', 'cubes'])
    start = rng.choice([1, 1, 2])
    if which == 'sum':
        formula, shown = n * (n + 1) / 2, r'\sum_{r=1}^{n} r = \dfrac{n(n+1)}2'
    elif which == 'squares':
        formula = n * (n + 1) * (2 * n + 1) / 6
        shown = r'\sum_{r=1}^{n} r^2 = \dfrac{n(n+1)(2n+1)}6'
    else:
        formula = (n * (n + 1) / 2)**2
        shown = r'\sum_{r=1}^{n} r^3 = \left(\dfrac{n(n+1)}2\right)^2'
    want = sp.nsimplify(formula.subs(n, start))
    return {
        'prompt': (f'Доказывают по индукции, что ${shown}$. Чему равна правая '
                   f'часть при $n = {start}$? Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'База — это подстановка, а не рассуждение.',
    }


def induction_sum(rng):
    which = rng.choice(['linear', 'squares', 'cubes', 'factorial'])
    if which == 'linear':
        formula = k * (k + 1) / 2
    elif which == 'squares':
        formula = k * (k + 1) * (2 * k + 1) / 6
    elif which == 'cubes':
        formula = (k * (k + 1) / 2)**2
    else:
        formula = sp.factorial(k + 1) - 1
    difference = sp.simplify(formula.subs(k, k + 1) - formula)
    shown = {'linear': r'\dfrac{k(k+1)}2',
             'squares': r'\dfrac{k(k+1)(2k+1)}6',
             'cubes': r'\left(\dfrac{k(k+1)}2\right)^2',
             'factorial': r'(k+1)! - 1'}[which]
    return {
        'prompt': (f'В шаге индукции $S(k) = {shown}$. Найдите и упростите '
                   f'$S(k+1) - S(k)$. Ответ через $k$.'),
        'answer': sp.simplify(difference),
        'check': expr_check(difference),
        'budget_ms': 120_000,
        'note': 'Именно это выражение и должно совпасть с очередным слагаемым.',
    }


def induction_divisibility(rng):
    first = rng.choice([5, 7, 8, 9])
    second = rng.choice([2, 3, 4])
    while first == second:
        second = rng.choice([2, 3, 4])
    # aᵏ⁺¹ − bᵏ⁺¹ = a(aᵏ − bᵏ) + (a − b)·bᵏ
    want = first - second
    return {
        'prompt': (f'В шаге индукции для делимости ${first}^n - {second}^n$ '
                   f'записали ${first}^{{k+1}} - {second}^{{k+1}} = '
                   f'{first}\\left({first}^k - {second}^k\\right) + '
                   f'c\\cdot{second}^k$. Найдите $c$.'),
        'answer': sp.Integer(want),
        'check': exact_check(want),
        'budget_ms': 90_000,
        'note': 'Тот самый ход, ради которого всё и переписывают.',
    }


def induction_derivative(rng):
    which = rng.choice(['xe', 'inverse', 'exp'])
    order = rng.choice([2, 3, 4])
    if which == 'xe':
        function, shown = x * sp.exp(x), 'xe^x'
    elif which == 'inverse':
        function, shown = 1 / x, r'\dfrac1x'
    else:
        function, shown = sp.exp(2 * x), 'e^{2x}'
    want = sp.simplify(sp.diff(function, x, order))
    return {
        'prompt': (f'Найдите производную порядка ${order}$ функции ${shown}$. '
                   f'Ответ через $x$.'),
        'answer': want,
        'check': expr_check(want),
        'budget_ms': 90_000,
        'note': 'Общая формула доказывается индукцией; здесь нужен один её случай.',
    }


def induction_recursion(rng):
    multiplier = rng.choice([2, 3])
    shift = rng.choice([-2, -1, 1, 2, 4])
    start = rng.choice([1, 2, 3])
    steps = rng.choice([3, 4, 5])
    value = start
    for _ in range(steps - 1):
        value = multiplier * value + shift
    sign = '+' if shift > 0 else '-'
    return {
        'prompt': (f'Последовательность задана как $u_{{n+1}} = {multiplier}u_n '
                   f'{sign} {abs(shift)}$, причём $u_1 = {start}$. '
                   f'Найдите $u_{{{steps}}}$.'),
        'answer': sp.Integer(value),
        'check': exact_check(value),
        'budget_ms': 75_000,
    }


def induction_inequality(rng):
    which = rng.choice(['power', 'factorial'])
    if which == 'power':
        smallest = next(m for m in range(1, 60) if 2**m > m**2)
        # 2ⁿ > n² выполняется при n = 1, потом ломается и снова держится с 5.
        smallest = next(m for m in range(3, 60) if all(2**j > j**2
                                                       for j in range(m, m + 6)))
        shown = '2^n > n^2'
    else:
        smallest = next(m for m in range(1, 40) if sp.factorial(m) > 2**m)
        shown = 'n! > 2^n'
    return {
        'prompt': (f'Начиная с какого наименьшего целого $n$ неравенство '
                   f'${shown}$ выполняется и дальше не нарушается?'),
        'answer': sp.Integer(smallest),
        'check': exact_check(smallest),
        'budget_ms': 90_000,
        'note': 'Это и есть база индукции в задачах на неравенство.',
    }


GENERATORS = {
    'A7.direct_proof': direct_proof,
    'A7.integer_representation': integer_representation,
    'A7.contradiction': contradiction,
    'A7.induction_skeleton': induction_skeleton,
    'A7.induction_sum': induction_sum,
    'A7.induction_divisibility': induction_divisibility,
    'A7.induction_derivative': induction_derivative,
    'A7.induction_recursion': induction_recursion,
    'A7.induction_inequality': induction_inequality,
}
