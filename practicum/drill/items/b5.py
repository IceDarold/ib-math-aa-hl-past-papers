"""Задачи на счёт для практикума B5: показательные и логарифмические модели.

Тема — два предложения: неизвестное в показателе (спуск логарифмом) или
неизвестное под логарифмом (подъём степенью). Генераторы держатся этого
разреза: первые три приёма поднимают, следующие пять опускают, девятый
спрашивает про сам логарифм как про функцию.

Две проверки здесь новые и живут в kit вместе с практикумом. `model_check`
подставляет в ответ данные из условия и эталона не хранит вовсе — так
ловится сдвинутый отсчёт времени. `in_terms_of_check` сторожит ответ
«через p и q»: чужих букв в нём быть не должно.
"""
from __future__ import annotations

import sympy as sp

from .common import (domain_check, exact_check, in_terms_of_check,
                     model_check, num_check, roots_in_check,
                     solution_set_check)

x, t = sp.symbols('x t')
p, q = sp.symbols('p q')
R = sp.Rational

# log_10 2 и log_10 3 — то, через что просят выразить всё остальное.
SUBS = {p: sp.log(2, 10), q: sp.log(3, 10)}


def log_laws(rng):
    """Разложить аргумент на 2 и 3 и собрать ответ через p и q."""
    powers = rng.choice([(3, 1), (2, 1), (1, 2), (4, 1), (1, 3), (2, 2),
                         (3, 2), (5, 0), (0, 3)])
    number = 2**powers[0] * 3**powers[1]
    want = powers[0] * p + powers[1] * q
    return {
        'prompt': (f'Пусть $\\log_{{10}}2 = p$ и $\\log_{{10}}3 = q$. '
                   f'Выразите $\\log_{{10}}{number}$ через $p$ и $q$.'),
        'answer': want,
        'check': in_terms_of_check(sp.log(number, 10), SUBS),
        'budget_ms': 60_000,
        'note': 'Сначала разложить аргумент на множители: закона для суммы нет.',
    }


def change_of_base(rng):
    if rng.random() < 0.5:
        # log_{10^m} a при известном log_10 a = 1/n.
        n = rng.choice([2, 3, 4, 5])
        m = rng.choice([2, 3, 4])
        want = R(1, n * m)
        return {
            'prompt': (f'Известно, что $\\log_{{10}}a = \\frac{{1}}{{{n}}}$, '
                       f'где $a > 0$. Найдите $\\log_{{10^{{{m}}}}}a$. '
                       f'Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 60_000,
            'note': f'log_(b^m) a = (1/m)·log_b a, здесь m = {m}.',
        }
    # log_3 2^k и log_2 3^k — обе стороны одной дроби.
    power = rng.choice([2, 3, 4, 5])
    flip = rng.random() < 0.5
    base, arg = (2, 3) if flip else (3, 2)
    want = power * (q / p if flip else p / q)
    return {
        'prompt': (f'Пусть $\\log_{{10}}2 = p$ и $\\log_{{10}}3 = q$. '
                   f'Выразите $\\log_{{{base}}}{arg**power}$ через $p$ и $q$.'),
        'answer': want,
        'check': in_terms_of_check(sp.log(arg**power, base), SUBS),
        'budget_ms': 75_000,
        'note': 'Аргумент сверху, основание снизу.',
    }


def log_equation(rng):
    """Уравнение с посторонним корнем, который отсекает область.

    Уравнение строится от ответа, а не решается: сумма логарифмов равна m,
    значит произведение аргументов равно N = base^m. Берём делитель d < √N,
    и тогда больший корень равен shift + d, а меньший гарантированно
    оказывается ниже shift — то есть отбрасывается областью.
    """
    base, power = rng.choice([(2, 1), (3, 1), (5, 1), (10, 1),
                              (2, 2), (3, 2), (5, 2), (10, 2)])
    product = base**power
    divisors = [d for d in range(1, product) if product % d == 0
                and d * d < product]
    step = rng.choice(divisors)
    shift = rng.choice([1, 2, 3, 4])
    root = shift + step
    c = sp.Integer(product // step - shift - step)
    inner = f'x + {c}' if c > 0 else (f'x - {-c}' if c < 0 else 'x')
    right = '1' if power == 1 else str(power)
    expression = (sp.log(x + c, base) + sp.log(x - shift, base)
                  - sp.Integer(power))
    return {
        'prompt': (f'Решите уравнение '
                   f'$\\log_{{{base}}}({inner}) + '
                   f'\\log_{{{base}}}(x - {shift}) = {right}$.'),
        'answer': [sp.Integer(root)],
        'check': roots_in_check(expression, (shift + sp.Rational(1, 1000),
                                             shift + 200)),
        'budget_ms': 120_000,
        'note': 'Свернуть в один логарифм, снять его, а потом проверить, '
                'что оба аргумента положительны: второй корень квадратного '
                'уравнения область отбрасывает.',
    }


def exponent_laws(rng):
    which = rng.choice(['reciprocal', 'as_exp', 'square'])
    if which == 'reciprocal':
        v = sp.Symbol('v')
        want = 1 / (1 + v)
        return {
            'prompt': ('Дано $e^{T} = 1 + v$. Выразите $e^{-T}$ через $v$.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 45_000,
            'note': 'Отрицательный показатель — это обратная величина, '
                    'а не противоположная.',
        }
    if which == 'as_exp':
        number = rng.choice([2, 3, 5, 7, 10, 12])
        want = sp.log(number)
        return {
            'prompt': (f'Запишите число ${number}$ в виде $e^{{a}}$, где '
                       f'$a \\in \\mathbb{{R}}$. Найдите $a$.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 30_000,
            'note': 'Определение логарифма, прочитанное назад.',
        }
    c = sp.Symbol('c')
    power = rng.choice([2, 3])
    want = c**power
    return {
        'prompt': (f'Дано $e^{{T}} = c$, где $c > 0$. Выразите '
                   f'$e^{{{power}T}}$ через $c$.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 45_000,
        'note': '(e^T)^n = e^{nT}.',
    }


def take_logs(rng):
    if rng.random() < 0.5:
        half_life = rng.choice([3, 5, 8, 12, 24, 5730])
        want = sp.log(2) / half_life
        unit = 'лет' if half_life > 100 else 'часов'
        return {
            'prompt': (f'Вещество распадается по закону $A = A_0e^{{-kt}}$, '
                       f'а период полураспада равен ${half_life}$ {unit}. '
                       f'Найдите $k$. Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 90_000,
            'note': 'Проще идти через e^{5730k} = 2: так минус не теряется.',
        }
    base = rng.choice([2, 3, 5])
    factor = rng.choice([4, 6, 10, 20])
    target = rng.choice([50, 100, 200, 500])
    want = sp.log(R(target, factor)) / sp.log(base)
    return {
        'prompt': (f'Решите уравнение ${factor}\\cdot{base}^{{x}} = {target}$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': f'Сначала разделить на {factor}, и только потом логарифмировать.',
    }


def fit_model(rng):
    """Две точки, две постоянные — и отдельный вопрос о том, где t = 0."""
    start = rng.choice([500, 1200, 8000, 15000, 20000])
    percent = rng.choice([10, 11, 15, 20, 25])
    span = rng.choice([4, 5, 8, 10])
    grows = rng.random() < 0.5
    ratio = R(100 + percent, 100) if grows else R(100 - percent, 100)
    later = start * ratio
    want = start * sp.exp(sp.log(ratio) / span * t)
    verb = 'выросло на' if grows else 'уменьшилось на'
    return {
        'prompt': (f'Величина меняется по закону $A(t) = A_0e^{{kt}}$, где '
                   f'$t$ — годы. При $t = 0$ она равна ${start}$, а за '
                   f'${span}$ лет она {verb} ${percent}\\%$. Запишите модель '
                   f'$A(t)$ целиком, с найденным $k$.'),
        'answer': want,
        'check': model_check([(0, start), (span, later)]),
        'budget_ms': 150_000,
        'note': f'{verb.capitalize()} {percent}% — это множитель '
                f'{sp.sstr(ratio)}, а не {percent/100}.',
    }


def percentage_model(rng):
    which = rng.choice(['depreciate', 'nominal', 'real'])
    if which == 'depreciate':
        price = rng.choice([8000, 12000, 25000, 30000])
        percent = rng.choice([8, 10, 12, 15, 20])
        years = rng.choice([3, 5, 7, 10])
        want = price * R(100 - percent, 100)**years
        return {
            'prompt': (f'Машина куплена за ${price}$ и дешевеет на '
                       f'${percent}\\%$ в год. Сколько она будет стоить '
                       f'через ${years}$ лет? Три значащие цифры.'),
            'answer': want,
            'check': num_check(want),
            'budget_ms': 90_000,
            'note': f'Множитель за год равен {(100 - percent) / 100}, '
                    f'а показатель считает годы.',
        }
    if which == 'nominal':
        percent = rng.choice([2, 3, 4, 6, 8, 12])
        times = rng.choice([2, 4, 12])
        want = R(percent, 100 * times)
        period = {2: 'дважды в год', 4: 'поквартально', 12: 'ежемесячно'}[times]
        return {
            'prompt': (f'Вклад под номинальные ${percent}\\%$ годовых, '
                       f'начисление {period}. Сумма через год записана как '
                       f'$P(1 + k)^{{{times}}}$. Найдите $k$. Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 60_000,
            'note': 'Номинальная ставка делится на число начислений.',
        }
    interest = rng.choice([10, 12, 15, 20])
    inflation = rng.choice([2, 4, 5])
    want = R(100 + interest, 100) / R(100 + inflation, 100)
    return {
        'prompt': (f'Вклад растёт на ${interest}\\%$ в год, инфляция за тот '
                   f'же год составляет ${inflation}\\%$. Найдите множитель, '
                   f'на который за год умножается реальная стоимость вклада. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': 'Реальный рост — это частное (1 + i)/(1 + j).',
    }


def logistic_model(rng):
    if rng.random() < 0.5:
        limit = rng.choice([200, 500, 1000, 2400])
        start = rng.choice([20, 40, 50, 100])
        while start >= limit:
            start = rng.choice([20, 40, 50])
        want = R(limit, start) - 1
        return {
            'prompt': (f'Популяция описывается моделью '
                       f'$x = \\dfrac{{{limit}}}{{1 + Ce^{{-kt}}}}$, и при '
                       f'$t = 0$ она равна ${start}$. Найдите $C$. '
                       f'Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 75_000,
            'note': 'e^0 = 1, и уравнение на C становится линейным.',
        }
    limit = rng.choice([200, 400, 800])
    start = rng.choice([25, 40, 50])
    span = rng.choice([2, 4, 5, 10])
    middle = rng.choice([2, 4])          # во сколько раз выросла к моменту span
    later = start * middle
    while later >= limit:
        middle, later = 2, start * 2
    const = R(limit, start) - 1
    rate = -sp.log((R(limit, later) - 1) / const) / span
    want = limit / (1 + const * sp.exp(-rate * t))
    return {
        'prompt': (f'Популяция описывается моделью '
                   f'$x = \\dfrac{{{limit}}}{{1 + Ce^{{-kt}}}}$. При $t = 0$ '
                   f'она равна ${start}$, при $t = {span}$ — ${later}$. '
                   f'Запишите модель целиком, с найденными $C$ и $k$.'),
        'answer': want,
        'check': model_check([(0, start), (span, later)]),
        'budget_ms': 180_000,
        'note': 'Сначала C из t = 0, потом k из второй точки.',
    }


def log_as_function(rng):
    which = rng.choice(['domain', 'decibel', 'composition'])
    if which == 'domain':
        edge = rng.choice([1, 2, 3, 4, 5])
        want = sp.Union(sp.Interval.open(-sp.oo, -edge),
                        sp.Interval.open(edge, sp.oo))
        return {
            'prompt': (f'Найдите область определения функции '
                       f'$h(x) = \\ln(x^2 - {edge**2})$.'),
            'answer': want,
            'check': solution_set_check(x**2 - edge**2 > 0),
            'budget_ms': 90_000,
            'note': 'Аргумент логарифма строго положителен, и это две ветви, '
                    'а не одна.',
        }
    if which == 'decibel':
        loud = rng.choice([70, 85, 90, 110, 115])
        want = sp.Integer(10)**(R(loud, 10) - 12)
        return {
            'prompt': (f'Громкость связана с интенсивностью формулой '
                       f'$L = 10\\log_{{10}}(I \\times 10^{{12}})$. Найдите '
                       f'$I$ при $L = {loud}$ децибел. Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 90_000,
            'note': 'Сначала разделить на 10, потом снять логарифм.',
        }
    low = rng.choice([-4, -3, -2])
    high = rng.choice([1, 2, 3])
    want = sp.Interval(sp.exp(low), sp.exp(high))
    return {
        'prompt': (f'Известно, что $f(u) \\le 0$ в точности при '
                   f'${low} \\le u \\le {high}$. Решите неравенство '
                   f'$f(\\ln x) \\le 0$ при $x > 0$. Ответ точный.'),
        'answer': want,
        'check': domain_check(want),
        'budget_ms': 90_000,
        'note': 'Сначала решить относительно ln x, и только потом '
                'возводить e в обе части: e^u возрастает и знак не меняет.',
    }


GENERATORS = {
    'B5.log_laws': log_laws,
    'B5.change_of_base': change_of_base,
    'B5.log_equation': log_equation,
    'B5.exponent_laws': exponent_laws,
    'B5.take_logs': take_logs,
    'B5.fit_model': fit_model,
    'B5.percentage_model': percentage_model,
    'B5.logistic_model': logistic_model,
    'B5.log_as_function': log_as_function,
}
