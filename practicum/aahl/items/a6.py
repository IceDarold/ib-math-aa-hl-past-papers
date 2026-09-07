"""Задачи на счёт для практикума A6: Муавр, корни, геометрия на плоскости.

Отличие от A5: там форма записи одного числа, здесь — что происходит
с числом при возведении в степень и извлечении корня. Поэтому и ответом
чаще бывает набор чисел, а не одно.
"""
from __future__ import annotations

import sympy as sp

from .common import complex_check, complex_set_check, exact_check, identity_check

I = sp.I
x = sp.Symbol('x')
SHARES = [sp.Rational(1, 6), sp.Rational(1, 4), sp.Rational(1, 3),
          sp.Rational(1, 2), sp.Rational(2, 3), sp.Rational(3, 4),
          sp.Rational(-1, 4), sp.Rational(-1, 3), sp.Rational(-1, 2)]


def _angle(share):
    """Угол для формулы: отрицательный берём в скобки, иначе «cos - π/2»."""
    angle = sp.nsimplify(share * sp.pi)
    text = sp.latex(angle)
    return f'\\left({text}\\right)' if share < 0 else text


def _cis(radius, share):
    angle = share * sp.pi
    return sp.nsimplify(radius * (sp.cos(angle) + I * sp.sin(angle)))


def de_moivre_power(rng):
    radius = rng.choice([1, 1, 2, 3])
    share = rng.choice(SHARES)
    power = rng.choice([3, 4, 5, 6, 8])
    base = _cis(radius, share)
    value = sp.expand(sp.simplify(_cis(radius**power, share * power)))
    angle = _angle(share)
    head = f'{radius}' if radius != 1 else ''
    return {
        'prompt': (f'Вычислите $\\left[{head}\\left(\\cos {angle} + '
                   f'i\\sin {angle}\\right)\\right]^{{{power}}}$. '
                   f'Ответ в виде $a + bi$, точный.'),
        'answer': value,
        'check': complex_check(value),
        'budget_ms': 90_000,
        'note': 'Модуль в степень, аргумент умножить.',
    }


def nth_roots(rng):
    order = rng.choice([3, 4])
    radius = rng.choice([1, 8, 16, 27]) if order == 3 else rng.choice([1, 16])
    share = rng.choice([sp.Integer(0), sp.Rational(1, 2), sp.Integer(1)])
    number = sp.expand(_cis(radius, share))
    root_radius = sp.Rational(radius)**sp.Rational(1, order)
    roots = [sp.expand(sp.simplify(
        _cis(root_radius, (share + 2 * k) / order))) for k in range(order)]
    return {
        'prompt': (f'Найдите все корни {order}-й степени из '
                   f'${sp.latex(number)}$. Ответы точные, через запятую.'),
        'answer': roots,
        'check': complex_set_check(roots),
        'budget_ms': 150_000,
        'note': f'Их ровно {order}, и они делят окружность поровну.',
    }


def roots_of_unity(rng):
    order = rng.choice([3, 4, 5, 6, 8])
    what = rng.choice(['sum', 'count', 'one'])
    if what == 'sum':
        # Сумма всех корней из единицы равна нулю при n > 1.
        want, question = sp.Integer(0), 'их сумму'
        check = exact_check(want)
    elif what == 'count':
        want, question = sp.Integer(order), 'сколько их'
        check = exact_check(want)
    else:
        want = sp.expand(sp.simplify(_cis(1, sp.Rational(2, order))))
        question = 'корень с наименьшим положительным аргументом'
        check = complex_check(want)
    return {
        'prompt': (f'Рассмотрите все корни уравнения $z^{{{order}}} = 1$. '
                   f'Найдите {question}. Ответ точный.'),
        'answer': want,
        'check': check,
        'budget_ms': 75_000,
    }


def periodicity_condition(rng):
    share = rng.choice([sp.Rational(1, 6), sp.Rational(1, 4),
                        sp.Rational(1, 3), sp.Rational(2, 3),
                        sp.Rational(3, 4), sp.Rational(5, 6)])
    target = rng.choice(['real', 'positive'])
    step = 1 if target == 'real' else 2
    smallest = None
    for n in range(1, 200):
        total = share * n
        if (total % step) == 0:
            smallest = n
            break
    angle = _angle(share)
    words = ('действительным' if target == 'real'
             else 'действительным и положительным')
    return {
        'prompt': (f'$z = \\cos {angle} + i\\sin {angle}$. '
                   f'Найдите наименьшее целое $n > 0$, при котором $z^n$ '
                   f'становится {words}.'),
        'answer': sp.Integer(smallest),
        'check': exact_check(smallest),
        'budget_ms': 90_000,
    }


def rotation_geometry(rng):
    a = rng.choice([-3, -2, -1, 1, 2, 3, 4])
    b = rng.choice([-3, -2, -1, 1, 2, 3])
    share = rng.choice([sp.Rational(1, 2), sp.Rational(-1, 2),
                        sp.Rational(1, 4), sp.Rational(1, 3),
                        sp.Rational(2, 3), sp.Integer(1)])
    point = a + b * I
    value = sp.expand(sp.simplify(point * _cis(1, share)))
    angle = sp.nsimplify(share * sp.pi)
    return {
        'prompt': (f'Точку $z = {sp.latex(point)}$ повернули вокруг начала '
                   f'координат на ${sp.latex(angle)}$ против часовой стрелки. '
                   f'В какую точку она перешла? Ответ точный, в виде $a + bi$.'),
        'answer': value,
        'check': complex_check(value),
        'budget_ms': 90_000,
        'note': 'Поворот — это умножение на число с модулем 1.',
    }


def trig_via_de_moivre(rng):
    order = rng.choice([2, 3, 4])
    which = rng.choice(['cos', 'sin'])
    if which == 'cos':
        want = sp.expand(sp.chebyshevt(order, sp.cos(x)))
        question = f'\\cos {order}x'
        hint = 'через $\\cos x$'
    else:
        want = sp.expand(sp.expand_trig(sp.sin(order * x)))
        question = f'\\sin {order}x'
        hint = 'через $\\sin x$ и $\\cos x$'
    return {
        'prompt': (f'Выразите ${question}$ {hint}.'),
        'answer': want,
        'check': identity_check(want, var='x',
                                samples=(0.3, 0.7, 1.1, 1.9, 2.6)),
        'budget_ms': 150_000,
        'note': 'Муавр и бином: раскройте (cosθ + i sinθ) в степени.',
    }


GENERATORS = {
    'A6.de_moivre_power': de_moivre_power,
    'A6.nth_roots': nth_roots,
    'A6.roots_of_unity': roots_of_unity,
    'A6.periodicity_condition': periodicity_condition,
    'A6.rotation_geometry': rotation_geometry,
    'A6.trig_via_de_moivre': trig_via_de_moivre,
}
