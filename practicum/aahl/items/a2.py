"""Задачи на счёт для практикума A2: геометрические прогрессии и бесконечные суммы.

Тема держится на одной фразе — от члена к члену умножают на одно и то же, —
и генераторы идут по тому же разрезу, что и лестница: чем оказывается
знаменатель. Сначала он число и берётся делением; потом решает, есть ли
у ряда сумма; потом прячется в сигму; потом становится буквой в условии;
потом n уходит в показатель; напоследок знаменатель — выражение с x.

Числа подобраны так, чтобы счёт был в уме или в одну кнопку: тренируется
решение о том, какую формулу писать и сколько раз применён знаменатель,
а не арифметика. Там, где ответ точный — дробь, корень, выражение, —
десятичная запись не принимается.
"""
from __future__ import annotations

import sympy as sp

from .common import exact_check, identity_check, roots_check

x = sp.Symbol('x')
w = sp.Symbol('w')
R = sp.Rational


def _tex(value):
    """Число для условия: дробь — через \\frac, со знаком впереди."""
    value = sp.nsimplify(value)
    if value.is_Integer:
        return str(value)
    sign = '-' if value < 0 else ''
    return f'{sign}\\frac{{{abs(value.p)}}}{{{value.q}}}'


def _term(first, ratio, index):
    """n-й член: знаменатель применён index − 1 раз."""
    return first * ratio ** (index - 1)


def _sum(first, ratio, count):
    """Сумма первых count членов."""
    return sp.nsimplify(first * (ratio ** count - 1) / (ratio - 1))


def ratio_and_term(rng):
    """Член по номеру, знаменатель по двум членам, второй член по четвёртому."""
    first = rng.choice([2, 3, 5, -4, 6, 7])
    ratio = rng.choice([2, 3, -2, -3])
    kind = rng.choice(['term', 'ratio', 'second'])
    if kind == 'term':
        index = rng.choice([5, 6, 7, 8])
        answer = sp.Integer(_term(first, ratio, index))
        prompt = (f'Геометрическая последовательность имеет первый член '
                  f'${first}$ и знаменатель ${ratio}$. Найдите '
                  f'${index}$-й член.')
        note = ('Умножений между первым членом и n-м ровно n − 1: до первого '
                'члена знаменатель не применялся ни разу.')
    elif kind == 'ratio':
        low = rng.choice([2, 3])
        high = low + 3
        answer = sp.Integer(ratio)
        prompt = (f'В геометрической последовательности ${low}$-й член равен '
                  f'${_term(first, ratio, low)}$, а ${high}$-й равен '
                  f'${_term(first, ratio, high)}$. Найдите знаменатель.')
        note = ('Между этими членами три шага, значит их отношение — r³. '
                'Кубический корень единственный, и знак он сохраняет.')
    else:
        answer = sp.Integer(first * ratio)
        prompt = (f'Геометрическая последовательность имеет первый член '
                  f'${first}$ и четвёртый член ${_term(first, ratio, 4)}$. '
                  f'Найдите второй член.')
        note = ('От первого члена до четвёртого три умножения: r³ = u₄/u₁. '
                'Второй член — это первый, умноженный на r один раз.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 45_000,
        'note': note,
    }


def finite_sum(rng):
    """Сумма первых n членов — и сколько их на самом деле."""
    first = rng.choice([1, 2, 3, 5, -2])
    ratio = rng.choice([2, 3, -2])
    if rng.random() < 0.5:
        count = rng.choice([5, 6, 7, 8])
        answer = _sum(first, ratio, count)
        prompt = (f'Найдите сумму первых ${count}$ членов геометрической '
                  f'последовательности с первым членом ${first}$ '
                  f'и знаменателем ${ratio}$.')
        note = ('S_n = u₁(rⁿ − 1)/(r − 1): ряд, умноженный на r и вычтенный '
                'из самого себя, — в середине всё сокращается.')
    else:
        top = rng.choice([4, 5, 6, 7])
        answer = _sum(first, ratio, top + 1)
        prompt = (f'Найдите $\\sum_{{i=0}}^{{{top}}} {first}\\cdot '
                  f'({ratio})^{{i}}$.')
        note = (f'Индекс идёт от 0 до {top}, значит слагаемых {top + 1}, '
                f'а не {top}: первое из них — при i = 0.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 60_000,
        'note': note,
    }


def sum_to_infinity(rng):
    """Сумма всей прогрессии при |r| < 1, прямо и обратно."""
    first = rng.choice([6, 8, 9, 12, 15, 20])
    ratio = rng.choice([R(1, 2), R(1, 3), R(-1, 2), R(2, 3), R(-1, 3),
                        R(1, 4), R(3, 4)])
    whole = sp.nsimplify(first / (1 - ratio))
    if rng.random() < 0.5:
        answer = whole
        prompt = (f'Геометрическая последовательность имеет первый член '
                  f'${first}$ и знаменатель ${_tex(ratio)}$. Найдите сумму '
                  f'всех её членов.')
        note = ('S∞ = u₁/(1 − r), и пользоваться ей можно только при |r| < 1. '
                'При отрицательном r в знаменателе 1 − r больше единицы.')
    else:
        answer = sp.Integer(first)
        prompt = (f'Сумма бесконечной геометрической прогрессии со '
                  f'знаменателем ${_tex(ratio)}$ равна ${_tex(whole)}$. '
                  f'Найдите первый член.')
        note = ('Та же формула, прочитанная наоборот: u₁ = S∞ · (1 − r).')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 60_000,
        'note': note,
    }


def series_from_sigma(rng):
    """Бесконечная сигма: первый член — слагаемое при нижнем пределе."""
    coeff = rng.choice([2, 3, 4, 5, 6, 8])
    ratio = rng.choice([R(1, 2), R(1, 3), R(2, 5), R(-1, 2), R(1, 4)])
    low = rng.choice([0, 1, 2])
    answer = sp.nsimplify(coeff * ratio ** low / (1 - ratio))
    return {
        'prompt': (f'Найдите $\\sum_{{i={low}}}^{{\\infty}} {coeff}\\left('
                   f'{_tex(ratio)}\\right)^{{i}}$.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 75_000,
        'note': ('Первый член — всё слагаемое при нижнем пределе, а не '
                 'множитель перед скобкой. Знаменатель — то, что возводят '
                 'в степень.'),
    }


def geometric_condition(rng):
    """Три величины в геометрической прогрессии: s² = at."""
    if rng.random() < 0.5:
        left = rng.choice([2, 3, 4, 5])
        scale = rng.choice([2, 3, 4])
        right = left * scale ** 2
        middle = left * scale
        return {
            'prompt': (f'Числа ${left}$, $w$ и ${right}$ именно в этом '
                       f'порядке образуют геометрическую прогрессию. '
                       f'Найдите все возможные значения $w$.'),
            'answer': [sp.Integer(-middle), sp.Integer(middle)],
            'check': roots_check(sp.Eq(w ** 2, left * right), var='w'),
            'budget_ms': 60_000,
            'note': ('Равные отношения дают w² = произведению соседей. '
                     'Корней два, и оба дают настоящую прогрессию — '
                     'со знаменателем одного знака и противоположного.'),
        }
    while True:
        a, b, c = rng.sample([-5, -4, -3, -2, -1, 1, 2, 3, 4, 5, 6, 7, 8], 3)
        denominator = a + c - 2 * b
        if denominator == 0:
            continue
        value, remainder = divmod(b * b - a * c, denominator)
        if remainder or abs(value) > 12 or 0 in (value + a, value + b,
                                                  value + c):
            continue
        break
    shown = [f'$k {"+" if s > 0 else "-"} {abs(s)}$' for s in (a, b, c)]
    return {
        'prompt': (f'Числа {shown[0]}, {shown[1]} и {shown[2]} именно в этом '
                   f'порядке образуют геометрическую прогрессию. '
                   f'Найдите $k$.'),
        'answer': sp.Integer(value),
        'check': exact_check(value),
        'budget_ms': 90_000,
        'note': ('Условие (k + b)² = (k + a)(k + c). Квадраты k сокращаются, '
                 'и уравнение выходит линейным — это не ошибка.'),
    }


def smallest_n(rng):
    """Наименьшее n: неравенство с n в показателе, округлённое в нужную сторону."""
    if rng.random() < 0.5:
        first = rng.choice([2, 3, 5])
        ratio = rng.choice([2, 3])
        target = rng.choice([500, 1000, 2000, 5000])
        answer = next(n for n in range(1, 200)
                      if _sum(first, ratio, n) > target)
        prompt = (f'Геометрическая последовательность имеет первый член '
                  f'${first}$ и знаменатель ${ratio}$. Найдите наименьшее '
                  f'$n$, при котором сумма первых $n$ членов больше '
                  f'${target}$.')
        note = ('Из неравенства выходит дробная граница, а ответ — целое '
                'число с правильной стороны от неё. Проверьте соседний номер.')
    else:
        price = rng.choice([12000, 20000, 30000])
        percent = rng.choice([10, 15, 20, 25])
        share = rng.choice([25, 40, 50])
        keep = 1 - R(percent, 100)
        answer = next(n for n in range(1, 200)
                      if price * keep ** n < price * R(share, 100))
        prompt = (f'Машина стоит ${price}$. Каждый год её стоимость падает '
                  f'на ${percent}\\%$. Через сколько полных лет стоимость '
                  f'впервые станет меньше ${share}\\%$ от начальной?')
        note = ('Падение на p% — это знаменатель 1 − p/100. Логарифм '
                'по основанию меньше единицы переворачивает неравенство.')
    return {
        'prompt': prompt,
        'answer': sp.Integer(answer),
        'check': exact_check(answer),
        'budget_ms': 90_000,
        'note': note,
    }


def ratio_with_x(rng):
    """Знаменатель — выражение с x: сумма ряда становится функцией."""
    c = rng.choice([2, 3, 4, 5])
    kind = rng.choice(['sum', 'even', 'radius'])
    if kind == 'sum':
        answer = 1 / (1 - c * x)
        return {
            'prompt': (f'Найдите сумму ряда $1 + {c}x + {c * c}x^2 + '
                       f'{c ** 3}x^3 + \\dots$ при $|x| < \\frac{{1}}{{{c}}}$.'),
            'answer': answer,
            'check': identity_check(answer, var='x',
                                    samples=(0.02, 0.05, 0.08, 0.11, 0.14,
                                             0.17)),
            'budget_ms': 60_000,
            'note': (f'Первый член 1, знаменатель {c}x. Формула суммы не '
                     f'знает, число r или выражение.'),
        }
    if kind == 'even':
        answer = 1 / (1 + c * x ** 2)
        return {
            'prompt': (f'Найдите сумму ряда $1 - {c}x^2 + {c * c}x^4 - \\dots$ '
                       f'при $|x| < \\frac{{1}}{{\\sqrt{{{c}}}}}$.'),
            'answer': answer,
            'check': identity_check(answer, var='x',
                                    samples=(0.05, 0.1, 0.15, 0.2, 0.25,
                                             0.3)),
            'budget_ms': 75_000,
            'note': (f'Знаменатель −{c}x², с минусом. 1 − (−{c}x²) даёт '
                     f'1 + {c}x² в знаменателе ответа.'),
        }
    answer = 1 / sp.sqrt(c)
    return {
        'prompt': (f'Ряд $1 - {c}x^2 + {c * c}x^4 - {c ** 3}x^6 + \\dots$ '
                   f'сходится при $|x| < K$. Найдите наибольшее $K$ '
                   f'в точном виде.'),
        'answer': answer,
        'check': exact_check(answer),
        'budget_ms': 75_000,
        'note': (f'Условие |r| < 1 записывается через x: |−{c}x²| < 1, то есть '
                 f'x² < 1/{c}. Спрашивают x, а не r.'),
    }


GENERATORS = {
    'A2.ratio_and_term': ratio_and_term,
    'A2.finite_sum': finite_sum,
    'A2.sum_to_infinity': sum_to_infinity,
    'A2.series_from_sigma': series_from_sigma,
    'A2.geometric_condition': geometric_condition,
    'A2.smallest_n': smallest_n,
    'A2.ratio_with_x': ratio_with_x,
}
