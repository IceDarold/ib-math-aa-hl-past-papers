"""Задачи на счёт для практикума A1: арифметические прогрессии и суммы.

Тема держится на одной фразе — от члена к члену прибавляют одно и то же, —
и генераторы идут по тому же разрезу, что и лестница: первые два ходят
по известной прогрессии, третий и четвёртый ищут саму прогрессию, пятый
и шестой превращают её в условие на букву, последние три — три места,
где номер обязан быть целым, сумма наибольшей, а члены логарифмами.

Числа подобраны так, чтобы счёт был в уме или в одну кнопку: тренируется
решение о том, какую из двух формул писать, а не арифметика. Там, где
ответ выходит точным — разность, сумма с логарифмом, коэффициент
AS-линейной функции, — спрашивается точное значение, и десятичная запись
не принимается.
"""
from __future__ import annotations

import sympy as sp

from .common import exact_check, num_check

x = sp.Symbol('x')


def _seq(first, step, index):
    """n-й член: шаг сделан index − 1 раз."""
    return first + (index - 1) * step


def _sum(first, step, count):
    """Сумма первых count членов."""
    return sp.Rational(count, 2) * (2 * first + (count - 1) * step)


def nth_term(rng):
    """Член по номеру и номер по члену: u_n = u₁ + (n − 1)d."""
    kind = rng.choice(['term', 'index', 'formula'])
    first = rng.choice([-8, -3, 2, 5, 7, 12, 20])
    step = rng.choice([-7, -4, -3, 2, 3, 5, 6])
    if kind == 'term':
        index = rng.choice([9, 12, 15, 18, 21, 26, 30])
        answer = _seq(first, step, index)
        prompt = (f'Арифметическая последовательность имеет первый член '
                  f'${first}$ и общую разность ${step}$. Найдите '
                  f'${index}$-й член.')
        note = ('Шагов между первым членом и n-м ровно n − 1, а не n: '
                'до первого члена шагов нет вовсе.')
    elif kind == 'index':
        index = rng.choice([9, 12, 15, 18, 21, 26, 30])
        value = _seq(first, step, index)
        answer = index
        prompt = (f'Арифметическая последовательность имеет первый член '
                  f'${first}$ и общую разность ${step}$. Каким по счёту '
                  f'идёт член, равный ${value}$?')
        note = ('Из u₁ + (n − 1)d = u_n выходит линейное уравнение на n. '
                'Ответ обязан быть целым и положительным.')
    else:
        answer = first + step
        sign = '+' if step > 0 else '-'
        prompt = (f'$n$-й член последовательности задан формулой '
                  f'$u_n = {first} {sign} {abs(step)}n$. '
                  f'Найдите первый член.')
        note = (f'Свободный член ${first}$ — это u₀, а не u₁: '
                f'последовательность начинается с n = 1.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 45_000,
        'note': note,
    }


def series_sum(rng):
    """Сумма первых n членов."""
    first = rng.choice([-6, -2, 1, 3, 4, 8, 15])
    step = rng.choice([-5, -3, 2, 3, 4, 7])
    count = rng.choice([8, 10, 12, 15, 18, 20, 25])
    answer = _sum(first, step, count)
    return {
        'prompt': (f'Найдите сумму первых ${count}$ членов арифметической '
                   f'последовательности с первым членом ${first}$ и общей '
                   f'разностью ${step}$.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 60_000,
        'note': ('S_n = n/2 (u₁ + u_n) — это ряд, сложенный сам с собой '
                 'задом наперёд: n одинаковых пар, поделённых пополам.'),
    }


def two_conditions(rng):
    """Два факта о последовательности — система на u₁ и d."""
    first = rng.choice([-9, -4, 1, 3, 6, 11])
    step = rng.choice([-6, -3, 2, 4, 5, 7])
    one = rng.choice([3, 4, 5])
    two = one + rng.choice([4, 6, 7, 9])
    want = rng.choice(['first', 'step'])
    answer = first if want == 'first' else step
    asked = 'первый член' if want == 'first' else 'общую разность'
    return {
        'prompt': (f'В арифметической последовательности ${one}$-й член '
                   f'равен ${_seq(first, step, one)}$, а ${two}$-й равен '
                   f'${_seq(first, step, two)}$. Найдите {asked}.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 75_000,
        'note': ('Два факта — два линейных уравнения на u₁ и d. Вычитание '
                 'одного из другого сразу убирает u₁ и оставляет d.'),
    }


def sum_to_term(rng):
    """Сумма задана формулой, спрашивают член: u_n = S_n − S_(n−1)."""
    lead = rng.choice([1, 2, 3, 4])
    linear = rng.choice([-5, -2, 3, 4, 6])
    index = rng.choice([1, 4, 6, 7, 9, 11])
    sums = lambda i: lead * i ** 2 + linear * i
    answer = sums(index) - sums(index - 1) if index > 1 else sums(1)
    sign = '+' if linear > 0 else '-'
    head = 'n^2' if lead == 1 else f'{lead}n^2'
    which = 'первый член' if index == 1 else f'${index}$-й член'
    return {
        'prompt': (f'Сумма первых $n$ членов арифметической '
                   f'последовательности равна $S_n = {head} {sign} '
                   f'{abs(linear)}n$. Найдите {which}.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 60_000,
        'note': ('u₁ = S₁, а дальше u_n = S_n − S_(n−1): столько добавилось '
                 'на n-м шаге. Делить S_n на n нельзя — это среднее.'),
    }


def constant_difference(rng):
    """Буква внутри членов: равные разности дают уравнение на неё."""
    value = rng.choice([-3, -2, -1, 1, 2, 3, 4])
    step = rng.choice([-4, -2, 3, 5, 6])
    base = rng.choice([-5, -1, 2, 6])
    # Три члена строятся из ответа, поэтому уравнение всегда разрешимо.
    # Наклоны обязаны сами не быть арифметическими: иначе разности
    # оказываются равными при любом k, и уравнения на k нет вовсе.
    while True:
        slopes = [rng.choice([1, 2, 3]), rng.choice([-2, -1, 4]),
                  rng.choice([5, 6, -3])]
        if slopes[1] - slopes[0] != slopes[2] - slopes[1]:
            break
    shown = []
    for i, slope in enumerate(slopes):
        shift = base + i * step - slope * value
        head = 'k' if slope == 1 else ('-k' if slope == -1 else f'{slope}k')
        sign = '+' if shift >= 0 else '-'
        shown.append(f'${head} {sign} {abs(shift)}$')
    return {
        'prompt': (f'Первые три члена последовательности — {shown[0]}, '
                   f'{shown[1]} и {shown[2]}. При каком $k$ она '
                   f'арифметическая?'),
        'answer': value,
        'check': exact_check(value),
        'budget_ms': 75_000,
        'note': ('Условие всегда одно: u₂ − u₁ = u₃ − u₂. То же короче — '
                 'средний член равен среднему арифметическому соседних.'),
    }


def condition_on_coefficients(rng):
    """m, r, c в арифметической последовательности: AS-линейная функция."""
    slope = rng.choice([2, -3, -4, -6, -1])
    constant = sp.nsimplify(-sp.Rational(slope ** 2, slope + 2))
    root = sp.nsimplify(-constant / slope)
    if rng.random() < 0.5:
        answer, asked = constant, 'свободный член $c$'
        note = ('Из r = −c/m и r − m = c − r выходит m² + cm + 2c = 0, '
                'откуда c = −m²/(m + 2).')
    else:
        answer, asked = sp.nsimplify(root - slope), 'общую разность'
        note = ('Разность считается по любой соседней паре: r − m или '
                'c − r. Порядок m, r, c переставлять нельзя.')
    return {
        'prompt': (f'Функция $L(x) = {slope}x + c$ имеет корень $r$. '
                   f'Известно, что $m = {slope}$, $r$ и $c$ — именно '
                   f'в этом порядке — образуют арифметическую '
                   f'последовательность. Найдите {asked}.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 105_000,
        'note': note,
    }


def extremum_of_sum(rng):
    """Наибольшая сумма: она растёт, пока члены положительны."""
    step = -rng.choice([2, 3, 4, 5, 6])
    span = rng.choice([7, 9, 11, 13, 16])
    first = -step * span                     # член номер span + 1 равен нулю
    want = rng.choice(['value', 'index'])
    best = _sum(first, step, span)
    if want == 'value':
        answer, asked = best, 'Найдите наибольшее значение $S_n$.'
        note = ('Сумма растёт ровно пока члены положительны. Нулевой член '
                'ничего не добавляет, поэтому наибольших сумм две подряд.')
    else:
        answer, asked = span + 1, ('Найдите наибольшее $n$, при котором '
                                   '$S_n$ достигает максимума.')
        note = ('Член, равный нулю, суммы не меняет: S_n при этом номере '
                'та же, что и при предыдущем, и оба ответа верны.')
    return {
        'prompt': (f'Арифметическая последовательность имеет первый член '
                   f'${first}$ и общую разность ${step}$. Пусть $S_n$ — '
                   f'сумма первых $n$ членов. {asked}'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 90_000,
        'note': note,
    }


def integer_condition(rng):
    """Номер обязан быть целым: делимость решается таблицей, не алгеброй."""
    divisor = rng.choice([7, 11, 13, 17, 23])
    answer = next(n for n in range(2, 400)
                  if (n * (n + 1) // 2) % divisor == 0)
    return {
        'prompt': (f'Треугольные числа — это суммы $1 + 2 + \\dots + n$: '
                   f'$1, 3, 6, 10, 15, \\dots$ Найдите наименьшее $n > 1$, '
                   f'при котором $n$-е треугольное число делится '
                   f'на ${divisor}$.'),
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 105_000,
        'note': ('Целочисленных решений алгебра не ищет. Схемы оценивания '
                 'здесь единодушны: uses a table of values.'),
    }


def log_terms(rng):
    """Члены-логарифмы: сначала законы логарифма, потом обычная прогрессия."""
    base = rng.choice([2, 3, 5, 7])
    start = rng.choice([7, 9, 11, 13])
    drop = rng.choice([3, 4, 5, 6])
    # Логарифм держится отдельным множителем: nsimplify и expand на
    # выражении с ln внутри разбирают его на степени и портят ответ.
    piece = sp.log(base)
    first = start + 2 * piece
    step = -drop - piece
    shown = [f'${start} + \\ln {base ** 2}$',
             f'${start - drop} + \\ln {base}$',
             f'${start - 2 * drop} + \\ln 1$']
    if rng.random() < 0.5:
        answer = step
        asked = f'Найдите общую разность в виде числа и кратного $\\ln {base}$.'
        note = (f'ln {base ** 2} = 2 ln {base}, а ln 1 = 0. После этого '
                f'члены сравнимы, и разность видна.')
    else:
        count = rng.choice([6, 8, 10, 12])
        answer = sp.collect(sp.expand(_sum(first, step, count)), piece)
        asked = f'Найдите сумму первых ${count}$ членов.'
        note = ('Обе части ответа нужны: числовая и логарифмическая. '
                'Сокращать ln 1 = 0 вместе с остальными логарифмами нельзя.')
    return {
        'prompt': (f'Первые три члена арифметической последовательности — '
                   f'{shown[0]}, {shown[1]} и {shown[2]}. {asked}'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 105_000,
        'note': note,
    }


GENERATORS = {
    'A1.nth_term': nth_term,
    'A1.series_sum': series_sum,
    'A1.two_conditions': two_conditions,
    'A1.sum_to_term': sum_to_term,
    'A1.constant_difference': constant_difference,
    'A1.condition_on_coefficients': condition_on_coefficients,
    'A1.extremum_of_sum': extremum_of_sum,
    'A1.integer_condition': integer_condition,
    'A1.log_terms': log_terms,
}
