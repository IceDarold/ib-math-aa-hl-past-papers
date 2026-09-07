"""Задачи на счёт для практикума C4: синусоидальные модели.

Четыре коэффициента модели a·sin(b(x − c)) + d читаются с графика или из
описания, и почти все ошибки темы — это подстановка не того из них.
Поэтому большинство заданий спрашивает ровно один коэффициент.
"""
from __future__ import annotations

import sympy as sp

from .common import exact_check, hours_word, num_check, roots_in_check

x = sp.Symbol('x')
PI = sp.pi


def period_from_coefficient(rng):
    if rng.random() < 0.5:
        b = rng.choice([2, 3, 4, 6])
        want = sp.nsimplify(2 * PI / b)
        return {
            'prompt': (f'У функции $f(x) = \\sin({b}x)$ найдите период. '
                       f'Ответ точный.'),
            'answer': want,
            'check': exact_check(want),
            'budget_ms': 45_000,
        }
    hours = rng.choice([4, 6, 8, 12, 24])
    want = sp.nsimplify(2 * PI / hours)
    return {
        'prompt': (f'Прилив повторяется каждые ${hours}$ {hours_word(hours)}, модель имеет '
                   f'вид $h(t) = a\\sin(b(t - c)) + d$. Найдите $b$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
    }


def amplitude_and_midline(rng):
    low = rng.choice([-4, -2, 0, 1, 2, 3])
    height = rng.choice([2, 3, 4, 5, 6, 8])
    high = low + 2 * height
    ask = rng.choice(['amplitude', 'midline'])
    want = sp.Integer(height if ask == 'amplitude' else low + height)
    question = 'амплитуду' if ask == 'amplitude' else 'среднюю линию'
    return {
        'prompt': (f'Функция вида $a\\sin(b(x - c)) + d$ принимает наибольшее '
                   f'значение ${high}$ и наименьшее ${low}$. Найдите '
                   f'{question}. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'Полуразность и полусумма крайних значений.',
    }


def amplitude_sign(rng):
    height = rng.choice([2, 3, 4, 5])
    middle = rng.choice([0, 1, 2, 5, 10])
    starts_low = rng.random() < 0.5
    want = sp.Integer(-height if starts_low else height)
    where = 'наименьшего' if starts_low else 'наибольшего'
    tail = f' + {middle}' if middle else ''
    return {
        'prompt': (f'Модель $a\\sin(bx){tail}$ в момент $x = 0$ идёт '
                   f'от {where} значения, а размах равен ${2 * height}$. '
                   f'Найдите $a$ вместе со знаком.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'Синус в нуле равен нулю — знак определяет, куда пойдёт график '
                'сразу после нуля.',
    }


def phase_shift(rng):
    b = rng.choice([1, 2, 3])
    # Максимум синуса при b(x − c) = π/2, значит c = x_max − π/(2b).
    # Берём только те вершины, при которых сдвиг выходит неотрицательным:
    # иначе вопрос пришлось бы оговаривать, а он должен быть коротким.
    peak = rng.choice([share for share in (sp.Rational(1, 6),
                                           sp.Rational(1, 4),
                                           sp.Rational(1, 3),
                                           sp.Rational(1, 2))
                       if share >= sp.Rational(1, 2 * b)])
    want = sp.nsimplify(peak * PI - PI / (2 * b))
    inner = f'{b}(x - c)' if b != 1 else 'x - c'
    return {
        'prompt': (f'Функция $f(x) = \\sin\\big({inner}\\big)$ достигает '
                   f'максимума при $x = {sp.latex(sp.nsimplify(peak * PI))}$. '
                   f'Найдите $c$. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 90_000,
    }


def build_model(rng):
    height = rng.choice([2, 3, 4, 5])
    middle = rng.choice([5, 6, 8, 10, 12])
    hours = rng.choice([6, 12, 24])
    ask = rng.choice(['a', 'b', 'd'])
    if ask == 'a':
        want = sp.Integer(height)
    elif ask == 'd':
        want = sp.Integer(middle)
    else:
        want = sp.nsimplify(2 * PI / hours)
    return {
        'prompt': (f'Глубина колеблется от ${middle - height}$ до '
                   f'${middle + height}$ метров, полный цикл занимает '
                   f'${hours}$ {hours_word(hours)}. Модель $h(t) = a\\sin(bt) + d$. '
                   f'Найдите ${ask}$. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
    }


def use_model(rng):
    height = rng.choice([2, 3, 4])
    middle = rng.choice([5, 6, 8, 10])
    hours = rng.choice([6, 12])
    moment = rng.choice([1, 2, 3, 4, 5])
    value = float(height * sp.sin(2 * PI * moment / hours) + middle)
    return {
        'prompt': (f'Глубина задана как $h(t) = {height}\\sin\\left('
                   f'\\dfrac{{2\\pi t}}{{{hours}}}\\right) + {middle}$, где '
                   f'$t$ в часах. Найдите глубину при $t = {moment}$. '
                   f'Три значащие цифры.'),
        'answer': value,
        'check': num_check(value, 3),
        'budget_ms': 60_000,
    }


def threshold_interval(rng):
    height = rng.choice([3, 4, 5])
    middle = rng.choice([6, 8, 10])
    hours = rng.choice([12, 24])
    threshold = middle + rng.choice([1, 2])
    expression = height * sp.sin(2 * PI * x / hours) + middle - threshold
    roots = sorted(sp.solveset(expression, x, sp.Interval(0, hours)),
                   key=float)
    return {
        'prompt': (f'Для $h(t) = {height}\\sin\\left(\\dfrac{{2\\pi t}}'
                   f'{{{hours}}}\\right) + {middle}$ найдите все моменты на '
                   f'$0 \\le t \\le {hours}$, когда глубина равна '
                   f'${threshold}$. Через запятую, точные значения.'),
        'answer': roots,
        'check': roots_in_check(expression, (0, hours)),
        'budget_ms': 150_000,
        'note': 'Корней на полном периоде обычно два.',
    }


def bounds_argument(rng):
    height = rng.choice([2, 3, 4, 5])
    middle = rng.choice([1, 4, 7, 9])
    ask = rng.choice(['max', 'min'])
    want = sp.Integer(middle + height if ask == 'max' else middle - height)
    question = 'наибольшее' if ask == 'max' else 'наименьшее'
    return {
        'prompt': (f'Найдите {question} значение функции '
                   f'$f(x) = {height}\\cos(3x - 1) + {middle}$. Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 60_000,
        'note': 'Косинус не выходит за ±1, что бы ни стояло внутри.',
    }


GENERATORS = {
    'C4.period_from_coefficient': period_from_coefficient,
    'C4.amplitude_and_midline': amplitude_and_midline,
    'C4.amplitude_sign': amplitude_sign,
    'C4.phase_shift': phase_shift,
    'C4.build_model': build_model,
    'C4.use_model': use_model,
    'C4.threshold_interval': threshold_interval,
    'C4.bounds_argument': bounds_argument,
}
