"""Задачи на счёт для практикума E5: техника интегрирования.

Тема — один вопрос, заданный восемью способами: чему равна первообразная.
Генераторы идут по лестнице карточки: первый берёт её прямо из таблицы,
второй снимает постоянную точкой, третий делает замену, четвёртый и пятый
интегрируют по частям и по простейшим дробям, шестой узнаёт в частном f′/f,
седьмой строит формулу понижения, восьмой читает интеграл наоборот.

Проверки здесь новые и живут в kit вместе с практикумом. Общее у них одно:
ни одна не интегрирует. Ответ берут и дифференцируют, а определённый
интеграл считают сложением. Поэтому подсказать ответ проверка не может —
только узнать его, — и годится любая запись первообразной с любой
постоянной.
"""
from __future__ import annotations

import sympy as sp

from .common import (accumulated_check, antiderivative_check, integral_check,
                     reduction_check, termwise_check, transformed_check)

x, t, u, n = sp.symbols('x t u n')
R = sp.Rational


def _tex(expr):
    return sp.latex(expr)


def table_antiderivative(rng):
    """Первообразная прямо из таблицы: сумма степеней и экспонент."""
    a = rng.choice([2, 3, 4, 6])
    b = rng.choice([2, 3, 5])
    power = rng.choice([2, 3, 4])
    f = a*x**power + b*sp.exp(x)
    return {
        'prompt': (f'Найдите неопределённый интеграл '
                   f'$\\int \\left({_tex(f)}\\right)\\,\\mathrm{{d}}x$. '
                   f'Постоянную можно не писать.'),
        'answer': a*x**(power + 1)/(power + 1) + b*sp.exp(x),
        'check': antiderivative_check(f),
        'budget_ms': 90_000,
        'note': ('Показатель повышается на единицу, и на новый показатель '
                 'надо поделить. Проверка принимает любую постоянную — '
                 'и её отсутствие.'),
    }


def constant_from_point(rng):
    """Дана f′ и точка графика: постоянную надо найти, а не оставить буквой."""
    a = rng.choice([1, 2, 3])
    b = rng.choice([-9, -6, 6, 12])
    c = rng.choice([-15, -8, 4, 9])
    spot = rng.choice([-2, -1, 1, 2])
    rate = 3*a*x**2 + 2*b*x + c
    base = a*x**3 + b*x**2 + c*x
    height = rng.choice([-10, 5, 12, 36])
    shift = height - base.subs(x, spot)
    return {
        'prompt': (f'Производная функции $f$ равна $f\'(x) = {_tex(rate)}$, '
                   f'и график проходит через точку $({spot},\\; {height})$. '
                   f'Найдите $f(x)$.'),
        'answer': sp.expand(base + shift),
        'check': antiderivative_check(rate, through=(spot, height)),
        'budget_ms': 120_000,
        'note': ('Точку подставляют в проинтегрированное выражение, а не в '
                 'f′, и подставлять надо в такое, где +c ещё стоит.'),
    }


def substitution(rng):
    """Замена переменной: функция стоит рядом со своей производной."""
    a = rng.choice([2, 3, 4, 5])
    power = rng.choice([2, 3])
    f = 2*a*x/(1 + a*x**2)**power if power > 1 else 2*a*x/(1 + a*x**2)
    inner = 1 + a*x**2
    if power == 1:
        answer = sp.log(inner)
    else:
        answer = -1/((power - 1)*inner**(power - 1))
    return {
        'prompt': (f'Найдите $\\int {_tex(f)}\\,\\mathrm{{d}}x$ заменой '
                   f'$u = {_tex(inner)}$. Постоянную можно не писать.'),
        'answer': answer,
        'check': antiderivative_check(f, domain=(0.2, 3.0)),
        'budget_ms': 120_000,
        'note': ('Замена делит на производную: du = 2ax dx. Забыть этот '
                 'множитель — значит ошибиться ровно в постоянное число раз.'),
    }


def substitution_step(rng):
    """Сам шаг замены: подынтегральное выражение через новую переменную."""
    a = rng.choice([2, 3, 5])
    f = sp.cos(x)*sp.sin(x)**a
    return {
        'prompt': (f'В интеграле $\\int {_tex(f)}\\,\\mathrm{{d}}x$ сделана '
                   f'замена $u = \\sin x$. Запишите подынтегральное выражение '
                   f'через $u$ — так, чтобы интеграл стал $\\int \\ldots '
                   f'\\,\\mathrm{{d}}u$.'),
        'answer': u**a,
        'check': transformed_check(f, sp.sin(x), domain=(0.1, 1.2)),
        'budget_ms': 90_000,
        'note': ('du = cos x dx, и множитель cos x уходит целиком в du. '
                 'Если в ответе остался x, замена подобрана не под всё '
                 'выражение.'),
    }


def by_parts(rng):
    """Интегрирование по частям: многочлен против экспоненты."""
    a = rng.choice([1, 2, 3])
    b = rng.choice([-5, -2, 3, 4])
    rate = rng.choice([1, 2, -1])
    f = (a*x + b)*sp.exp(rate*x)
    answer = sp.simplify(sp.integrate(f, x))
    return {
        'prompt': (f'Найдите $\\int {_tex(f)}\\,\\mathrm{{d}}x$. '
                   f'Постоянную можно не писать.'),
        'answer': answer,
        'check': antiderivative_check(f),
        'budget_ms': 150_000,
        'note': ('u — тот множитель, который дифференцирование упрощает, '
                 'то есть многочлен. Знак минус перед вторым интегралом '
                 'теряют чаще всего.'),
    }


def partial_fractions(rng):
    """Простейшие дроби: знаменатель раскладывается на два линейных множителя."""
    p = rng.choice([1, 2, 3])
    q = rng.choice([4, 5, 6])
    while q == p:
        q += 1
    f = 1/((x - p)*(x + q))
    answer = (sp.log(x - p) - sp.log(x + q))/(p + q)
    return {
        'prompt': (f'Найдите $\\int \\dfrac{{1}}{{(x - {p})(x + {q})}}'
                   f'\\,\\mathrm{{d}}x$. Постоянную можно не писать.'),
        'answer': answer,
        'check': antiderivative_check(f, domain=(p + 0.4, p + 4.0)),
        'budget_ms': 150_000,
        'note': (f'A/(x−{p}) + B/(x+{q}) с A = 1/{p + q} и B = −1/{p + q}: '
                 f'числители находят подстановкой корней знаменателя.'),
    }


def reduction_formula(rng):
    """Формула понижения: показатель — буква, ответ пишется через J(m)."""
    which = rng.choice(['cos', 'sin'])
    name = '\\cos' if which == 'cos' else '\\sin'
    if which == 'cos':
        term = sp.cos(x)**n
        answer = sp.cos(x)**(n - 1)*sp.sin(x)/n + (n - 1)*sp.Function('J')(n - 2)/n
    else:
        term = sp.sin(x)**n
        answer = -sp.sin(x)**(n - 1)*sp.cos(x)/n + (n - 1)*sp.Function('J')(n - 2)/n
    return {
        'prompt': (f'Выразите $\\int {name}^n x\\,\\mathrm{{d}}x$ через '
                   f'$\\int {name}^{{n-2}} x\\,\\mathrm{{d}}x$ при $n > 1$. '
                   f'Обозначьте $\\int {name}^m x\\,\\mathrm{{d}}x$ '
                   f'через $J(m)$ и запишите правую часть.'),
        'answer': answer,
        'check': reduction_check(term, n),
        'budget_ms': 240_000,
        'note': ('Отделить один множитель, взять по частям, заменить '
                 'sin²x на 1 − cos²x — и собрать одинаковые интегралы '
                 'в одну сторону. Без сборки формула бесполезна.'),
    }


def integral_as_condition(rng):
    """Интеграл известен, найти надо предел интегрирования."""
    a = rng.choice([2, 3, 5])
    top = rng.choice([2, 3, 4])
    f = 2*a*x/(a*x**2 + 1)
    value = sp.log(a*top**2 + 1)
    return {
        'prompt': (f'Площадь под кривой $y = {_tex(f)}$ от $x = 0$ до '
                   f'$x = c$ (при $c > 0$) равна $\\ln {a*top**2 + 1}$. '
                   f'Найдите $c$.'),
        'answer': sp.Integer(top),
        'check': integral_check(f, 0, sp.Symbol('c'), value=value, tol=1e-6),
        'budget_ms': 180_000,
        'note': ('Первообразная здесь средство, а не ответ: её берут, '
                 'подставляют пределы и решают уравнение. Довести до c, '
                 'а не остановиться на c².'),
    }


def logarithmic_integration(rng):
    """Частное, узнанное как f′/f: числитель есть производная знаменателя."""
    a = rng.choice([2, 3, 5])
    which = rng.choice(['poly', 'trig'])
    if which == 'poly':
        den = x**2 + a*x + a + 1
        f = (2*x + a)/den
        answer = sp.log(den)
        window = (0.5, 4.0)
    else:
        den = sp.sin(x) + a*sp.cos(x)
        f = (sp.cos(x) - a*sp.sin(x))/den
        answer = sp.log(den)
        window = (0.2, 1.2)
    return {
        'prompt': (f'Найдите $\\int {_tex(f)}\\,\\mathrm{{d}}x$. '
                   f'Постоянную можно не писать.'),
        'answer': answer,
        'check': antiderivative_check(f, domain=window),
        'budget_ms': 120_000,
        'note': ('Числитель здесь — производная знаменателя, и весь интеграл '
                 'равен ln от модуля знаменателя. Узнать эту форму и есть '
                 'вся задача.'),
    }


def termwise_series(rng):
    """Ряд вместо первообразной: интегрировать почленно и остановиться вовремя."""
    a = rng.choice([1, 2, 3])
    upto = rng.choice([5, 7])
    series = sum((-a)**j*x**(2*j) for j in range(upto//2 + 1))
    answer = sum((-a)**j*x**(2*j + 1)/(2*j + 1) for j in range(upto//2 + 1))
    return {
        'prompt': (f'Известно, что $\\dfrac{{1}}{{1 + {a}x^2}} = '
                   f'{_tex(series)} - \\ldots$ при $|x| < 1$. Найдите '
                   f'приближение для $\\int \\dfrac{{\\mathrm{{d}}x}}'
                   f'{{1 + {a}x^2}}$ до члена со степенью $x^{{{upto}}}$ '
                   f'включительно.'),
        'answer': answer,
        'check': termwise_check(1/(1 + a*x**2), upto + 1),
        'budget_ms': 120_000,
        'note': ('Интегрировать надо ряд, а не сдавать сам ряд. И степень '
                 f'выше {upto} — не запас, а лишнее: проверка её не примет.'),
    }


def _pick(rng, first, second):
    """Два вопроса на один приём: какой достанется, решает жребий."""
    return (first if rng.random() < 0.5 else second)(rng)


GENERATORS = {
    'E5.antiderivative_and_constant':
        lambda rng: _pick(rng, table_antiderivative, constant_from_point),
    'E5.substitution':
        lambda rng: _pick(rng, substitution, substitution_step),
    'E5.by_parts': by_parts,
    'E5.partial_fractions': partial_fractions,
    'E5.logarithmic_integration': logarithmic_integration,
    'E5.reduction_formula': reduction_formula,
    'E5.termwise_series': termwise_series,
    'E5.integral_as_condition': integral_as_condition,
}
