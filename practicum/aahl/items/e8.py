"""Задачи на счёт для практикума E8: стационарные точки, вогнутость, перегиб.

Генераторы идут по лестнице карточки: найти точку с обеими координатами;
назвать её вид по второй производной; назвать его же по смене знака первой —
там, где вторая молчит; найти перегиб; проделать то же с буквой вместо числа;
сказать, по какую сторону оси стоит точка; найти множество значений параметра
по числу точек или пересечений; пересчитать, сколько точек на промежутке.

Проверки эталона не хранят. `shape_check` отдаёт странице саму кривую, и
страница зовёт те же verify_turning, verify_nature, verify_bend, verify_side
и verify_param_set, что стоят в ноутбуке: вид точки там решают соседи,
перегиб — хорда, а множество значений буквы спрашивается у самого свойства.
Эталон в задании только для показа после попытки; строится он здесь
целочисленной арифметикой от ответа к условию.
"""
from __future__ import annotations

import sympy as sp

from .common import shape_check

x, y = sp.symbols('x y')
R = sp.Rational


def _tex(expr):
    return sp.latex(sp.sympify(expr))


def _pair(rng):
    """Две целые точки нулевого наклона: их сумма чётна, и кубика целая."""
    while True:
        first = rng.randint(-4, 2)
        second = first + rng.choice([2, 4, 6])
        if abs(first) + abs(second) <= 8:
            return first, second


def _cubic(first, second, shift):
    """Кубика, у которой f′ = 3(x − first)(x − second)."""
    return (x ** 3 - R(3, 2) * (first + second) * x ** 2
            + 3 * first * second * x + shift)


def find(rng):
    """Найти стационарную точку: обе координаты."""
    first, second = _pair(rng)
    shift = rng.randint(-6, 6)
    f = sp.expand(_cubic(first, second, shift))
    wanted = rng.choice(['maximum', 'minimum'])
    at = first if wanted == 'maximum' else second
    word = 'максимума' if wanted == 'maximum' else 'минимума'
    return {
        'prompt': (f'Найдите координаты локального {word} кривой '
                   f'$y = {_tex(f)}$. Ответ — пара чисел.'),
        'answer': (sp.Integer(at), sp.nsimplify(f.subs(x, at))),
        'check': shape_check('turning', sp.Eq(y, f), which=wanted,
                             domain=(first - 3, second + 3)),
        'budget_ms': 105_000,
        'note': 'Вторую координату берут у самой функции, а не у производной.',
    }


def classify(rng):
    """Вид точки по второй производной."""
    first, second = _pair(rng)
    shift = rng.randint(-6, 6)
    f = sp.expand(_cubic(first, second, shift))
    at = rng.choice([first, second])
    return {
        'prompt': (f'У кривой $y = {_tex(f)}$ наклон равен нулю при $x = {at}$. '
                   f'Это локальный максимум или локальный минимум? '
                   f'Ответ одним словом: maximum или minimum.'),
        'answer': 'maximum' if at == first else 'minimum',
        'check': shape_check('nature', sp.Eq(y, f), at=[at],
                             domain=(first - 3, second + 3)),
        'budget_ms': 75_000,
        'note': 'f″ < 0 — максимум: кривая выгнута вниз. Знак читают именно так.',
    }


def sign(rng):
    """Вид точки там, где вторая производная молчит."""
    at = rng.randint(-3, 3)
    power = rng.choice([3, 4])
    scale = rng.choice([-2, -1, 1, 2])
    shift = rng.randint(-5, 5)
    f = sp.expand(scale * (x - at) ** power + shift)
    if power % 2:
        answer = 'inflexion'
    else:
        answer = 'minimum' if scale > 0 else 'maximum'
    return {
        'prompt': (f'У кривой $y = {_tex(f)}$ и первая, и вторая производная '
                   f'равны нулю при $x = {at}$. Что там за точка? Ответ одним '
                   f'словом: maximum, minimum или inflexion.'),
        'answer': answer,
        'check': shape_check('nature', sp.Eq(y, f), at=[at],
                             domain=(at - 2, at + 2)),
        'budget_ms': 90_000,
        'note': 'Вторая производная здесь ноль и не говорит ничего: смотрят на знак первой.',
    }


def inflexion(rng):
    """Точка перегиба кубики."""
    lead = rng.choice([1, 2, 3])
    place = rng.choice([R(-2), R(-1), R(-1, 2), R(1, 2), R(1), R(2)])
    tail = rng.randint(-5, 5)
    linear = rng.randint(-6, 6)
    # Кубика с перегибом ровно в place: y = lead(x − place)³ + linear·x + tail.
    f = sp.expand(lead * (x - place) ** 3 + linear * x + tail)
    return {
        'prompt': (f'Найдите $x$-координату точки перегиба кривой '
                   f'$y = {_tex(f)}$. Ответ точный.'),
        'answer': place,
        'check': shape_check('bend', sp.Eq(y, f),
                             domain=(place - 4, place + 4)),
        'budget_ms': 90_000,
        'note': 'f″ = 0 и смена знака: у кубики это ровно одна точка.',
    }


def family(rng):
    """Стационарная точка семейства с буквой."""
    lead = rng.choice([1, 2])
    shift = rng.randint(-5, 5)
    a = sp.Symbol('a')
    f = lead * x ** 3 + a * x ** 2 + shift
    top = -2 * a / (3 * lead)
    height = sp.nsimplify(4 * a ** 3 / (27 * lead ** 2) + shift)
    return {
        'prompt': (f'Кривая $y = {_tex(f)}$, где $a > 0$. Найдите координаты '
                   f'её локального максимума в виде выражений через $a$.'),
        'answer': (sp.nsimplify(top), height),
        'check': shape_check('turning', sp.Eq(y, f), which='maximum',
                             domain=(-8, 8),
                             params={a: [3, 1, 2, 6]}),
        'budget_ms': 135_000,
        'note': 'Буква ведёт себя как число: продифференцировать, решить, подставить обратно.',
    }


def side(rng):
    """По какую сторону оси стоит стационарная точка."""
    step = rng.choice([-2, -1, 1, 2])
    lead = 3 * step
    shift = rng.randint(-6, 6)
    while 4 * step ** 3 + shift == 0:
        shift = rng.randint(-6, 6)
    f = sp.expand(x ** 3 + lead * x ** 2 + shift)
    at = sp.Integer(-2 * step)
    height = 4 * step ** 3 + shift
    return {
        'prompt': (f'У кривой $y = {_tex(f)}$ наклон равен нулю при $x = 0$ и '
                   f'при $x = {at}$. Вторая из этих точек стоит выше или ниже '
                   f'оси $x$? Ответ одним словом: above или below.'),
        'answer': 'above' if height > 0 else 'below',
        'check': shape_check('side', sp.Eq(y, f), at=[at]),
        'budget_ms': 75_000,
        'note': 'Вид точки о стороне оси не говорит: считают саму вторую координату.',
    }


def count(rng):
    """Множество значений буквы: по числу точек или по числу пересечений."""
    k = sp.Symbol('k')
    if rng.random() < 0.5:
        shift = rng.randint(-5, 5)
        f = x ** 3 + k * x + shift
        want, kinds = rng.choice([
            ('одну точку локального максимума и одну локального минимума',
             ['maximum', 'minimum']),
            ('ни одной точки нулевого наклона', []),
        ])
        return {
            'prompt': (f'При каких значениях $k$ кривая $y = {_tex(f)}$ имеет '
                       f'{want}? Ответ — неравенство.'),
            'answer': (sp.Interval.open(-sp.oo, 0) if kinds
                       else sp.Interval.open(0, sp.oo)),
            'check': shape_check('tally', sp.Eq(y, f), letter='k', kinds=kinds,
                                 domain=(-5, 5), window=(-4, 4)),
            'budget_ms': 120_000,
            'note': 'Сколько точек — это сколько корней у 3x² + k = 0.',
        }
    lead = rng.choice([1, 3])
    f = x ** 3 - 3 * lead ** 2 * x + k
    edge = 2 * lead ** 3
    times = rng.choice([1, 3])
    answer = (sp.Interval.open(-edge, edge) if times == 3
              else sp.Union(sp.Interval.open(-sp.oo, -edge),
                            sp.Interval.open(edge, sp.oo)))
    return {
        'prompt': (f'При каких значениях $k$ кривая $y = {_tex(f)}$ пересекает '
                   f'ось $x$ ровно {times} раз{"а" if times == 3 else ""}? '
                   f'Ответ — неравенство.'),
        'answer': answer,
        'check': shape_check('meets', sp.Eq(y, f), letter='k', times=times,
                             window=(-edge - 2, edge + 2)),
        'budget_ms': 135_000,
        'note': 'Решают знаки двух стационарных значений: вершины по одну сторону оси или по разные.',
    }


def none(rng):
    """Сколько точек нулевого наклона на промежутке — иногда ни одной."""
    if rng.random() < 0.5:
        lead = rng.choice([1, 2, 3])
        tail = rng.randint(-5, 5)
        f = sp.expand(x ** 3 + lead * x + tail)
        return {
            'prompt': (f'Сколько точек с нулевым наклоном у кривой '
                       f'$y = {_tex(f)}$ при $-5 \\le x \\le 5$? '
                       f'Ответ — целое число.'),
            'answer': sp.Integer(0),
            'check': shape_check('count', sp.Eq(y, f), domain=(-5, 5)),
            'budget_ms': 75_000,
            'note': '3x² + k = 0 при k > 0 корней не имеет — и точек нет ни одной.',
        }
    first, second = _pair(rng)
    shift = rng.randint(-6, 6)
    f = sp.expand(_cubic(first, second, shift))
    lo, hi = first - 3, second + 3
    return {
        'prompt': (f'Сколько точек с нулевым наклоном у кривой '
                   f'$y = {_tex(f)}$ при ${lo} \\le x \\le {hi}$? '
                   f'Ответ — целое число.'),
        'answer': sp.Integer(2),
        'check': shape_check('count', sp.Eq(y, f), domain=(lo, hi)),
        'budget_ms': 75_000,
        'note': 'Считают корни производной, попавшие внутрь промежутка.',
    }


GENERATORS = {
    'E8.find': find,
    'E8.classify': classify,
    'E8.sign': sign,
    'E8.inflexion': inflexion,
    'E8.family': family,
    'E8.side': side,
    'E8.count': count,
    'E8.none': none,
}
