"""Задачи на счёт для практикума A5: комплексные числа, формы записи.

Ответы почти всегда точные: тема про запись, а не про приближение.
Углы берутся только те, у которых синус и косинус точные, иначе вопрос
«найдите аргумент» становится вопросом про калькулятор.
"""
from __future__ import annotations

import sympy as sp

from .common import complex_check, exact_check

I = sp.I
NICE = [sp.Rational(1, 6), sp.Rational(1, 4), sp.Rational(1, 3),
        sp.Rational(1, 2), sp.Rational(2, 3), sp.Rational(3, 4),
        sp.Rational(5, 6), sp.Rational(-1, 6), sp.Rational(-1, 4),
        sp.Rational(-1, 3), sp.Rational(-1, 2), sp.Rational(-2, 3),
        sp.Rational(-3, 4)]


def _from_polar(radius, share):
    """r·cis(share·π) в алгебраической форме, точно."""
    angle = share * sp.pi
    return sp.nsimplify(radius * (sp.cos(angle) + I * sp.sin(angle)))


def cartesian_arithmetic(rng):
    a, b = rng.choice([1, 2, 3, 4, 5]), rng.choice([-4, -3, -2, -1, 1, 2, 3])
    c, d = rng.choice([1, 2, 3]), rng.choice([-3, -2, -1, 1, 2, 3])
    top, bottom = a + b * I, c + d * I
    value = sp.simplify(sp.expand(top / bottom))
    return {
        'prompt': (f'Запишите $\\dfrac{{{sp.latex(top)}}}{{{sp.latex(bottom)}}}$ '
                   f'в виде $a + bi$. Ответ точный.'),
        'answer': value,
        'check': complex_check(value),
        'budget_ms': 90_000,
        'note': 'Домножьте на сопряжённое знаменателю.',
    }


def equate_parts(rng):
    a, b = rng.choice([1, 2, 3, 4]), rng.choice([-3, -2, -1, 1, 2, 3])
    c, d = rng.choice([1, 2, 3]), rng.choice([-3, -2, 1, 2])
    right = sp.expand((a + b * I) * (c + d * I))
    ask = rng.choice(['x', 'y'])
    want = sp.Integer(a if ask == 'x' else b)
    return {
        'prompt': (f'Числа $x$ и $y$ действительные и '
                   f'$(x + yi)({sp.latex(c + d * I)}) = {sp.latex(right)}$. '
                   f'Найдите ${ask}$.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 90_000,
        'note': 'Раскройте скобку и приравняйте части по отдельности.',
    }


def modulus_argument(rng):
    radius = rng.choice([1, 2, 3, 4])
    share = rng.choice(NICE)
    z = _from_polar(radius, share)
    ask = rng.choice(['modulus', 'argument'])
    if ask == 'modulus':
        want, question = sp.Integer(radius), 'модуль'
    else:
        want, question = sp.nsimplify(share * sp.pi), 'аргумент (в радианах)'
    return {
        'prompt': (f'Найдите {question} числа $z = {sp.latex(z)}$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': 'Следите за четвертью: арктангенс сам её не знает.',
    }


def form_conversion(rng):
    radius = rng.choice([1, 2, 3, 4, 5])
    share = rng.choice(NICE)
    z = _from_polar(radius, share)
    angle = sp.nsimplify(share * sp.pi)
    return {
        'prompt': (f'Запишите $z = {radius if radius != 1 else ""}\\left(\\cos {sp.latex(angle)} + '
                   f'i\\sin {sp.latex(angle)}\\right)$ в виде $a + bi$. '
                   f'Ответ точный.'),
        'answer': z,
        'check': complex_check(z),
        'budget_ms': 75_000,
    }


def product_properties(rng):
    r1, r2 = rng.choice([2, 3, 4, 5]), rng.choice([2, 3, 4, 6])
    s1, s2 = rng.choice(NICE), rng.choice(NICE)
    what = rng.choice(['modulus', 'argument'])
    if what == 'modulus':
        want = sp.Integer(r1 * r2)
        question = r'\lvert z_1 z_2\rvert'
    else:
        # Аргумент произведения приводим в (−π, π]: экзамен просит главный.
        total = s1 + s2
        while total > 1:
            total -= 2
        while total <= -1:
            total += 2
        want = sp.nsimplify(total * sp.pi)
        question = r'\arg(z_1 z_2)'
    return {
        'prompt': (f'$\\lvert z_1\\rvert = {r1}$, '
                   f'$\\arg z_1 = {sp.latex(sp.nsimplify(s1 * sp.pi))}$, '
                   f'$\\lvert z_2\\rvert = {r2}$, '
                   f'$\\arg z_2 = {sp.latex(sp.nsimplify(s2 * sp.pi))}$. '
                   f'Найдите ${question}$. Ответ точный, аргумент главный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
    }


def conjugate_roots(rng):
    real = rng.choice([-2, -1, 1, 2, 3])
    imaginary = rng.choice([1, 2, 3])
    root = real + imaginary * I
    ask = rng.choice(['other', 'sum', 'product'])
    if ask == 'other':
        want = sp.conjugate(root)
        question = 'Назовите второй корень.'
        check = complex_check(want)
    elif ask == 'sum':
        want = sp.Integer(2 * real)
        question = 'Найдите сумму корней.'
        check = exact_check(want)
    else:
        want = sp.Integer(real**2 + imaginary**2)
        question = 'Найдите произведение корней.'
        check = exact_check(want)
    return {
        'prompt': (f'Квадратное уравнение с действительными коэффициентами '
                   f'имеет корень ${sp.latex(root)}$. {question} Ответ точный.'),
        'answer': want,
        'check': check,
        'budget_ms': 60_000,
    }


GENERATORS = {
    'A5.cartesian_arithmetic': cartesian_arithmetic,
    'A5.equate_parts': equate_parts,
    'A5.modulus_argument': modulus_argument,
    'A5.form_conversion': form_conversion,
    'A5.product_properties': product_properties,
    'A5.conjugate_roots': conjugate_roots,
}
