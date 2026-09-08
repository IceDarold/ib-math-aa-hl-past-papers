"""Задачи на счёт для практикума E4: касательная, нормаль, неявное дифференцирование.

Тема — одно понятие, взятое с двух концов: наклон кривой в точке есть наклон
прямой, которая её там держит. Генераторы идут по лестнице карточки: первые
два строят прямую по точке, третий ищет точку по наклону, четвёртый и пятый
делают то же самое с кривой, заданной уравнением, шестой дифференцирует
соотношение второй раз, седьмой ставит прямой угол, восьмой достаёт из
касания постоянную.

Проверки здесь новые и живут в kit вместе с практикумом. Общее у них одно:
ни одна не дифференцирует. Наклон берётся ходьбой по кривой — точка слева,
точка справа, и секущая через них, — а «кривая» значит и y = f(x), и
F(x, y) = 0 без различия. Поэтому эталона нет нигде, и годится любая
запись прямой.
"""
from __future__ import annotations

import sympy as sp

from .common import (constant_check, second_check, slope_check,
                     tangent_check, where_check)

x, y, t = sp.symbols('x y t')
R = sp.Rational


def _tex(expr):
    return sp.latex(expr)


def _line(slope, point):
    """Прямая через точку с данным наклоном."""
    return sp.expand(slope * (x - point[0]) + point[1])


def tangent_line(rng):
    """Касательная в известной точке: наклон с производной, высота с кривой."""
    a = rng.choice([1, 2, 3])
    b = rng.choice([-5, -3, -2, 2, 3])
    c = rng.choice([-4, -1, 1, 4, 6])
    at = rng.choice([-2, -1, 1, 2, 3])
    f = a*x**3 + b*x + c
    slope = sp.diff(f, x).subs(x, at)
    return {
        'prompt': (f'Найдите уравнение касательной к кривой '
                   f'$y = {_tex(f)}$ в точке, где $x = {at}$. '
                   f'Ответ — выражение через $x$.'),
        'answer': _line(slope, (at, f.subs(x, at))),
        'check': tangent_check(sp.Eq(y, f), at),
        'budget_ms': 120_000,
        'note': ('Наклон берётся у производной, высота — у самой кривой. '
                 'Прямая с верным наклоном, но не через ту точку, — '
                 'самый частый способ потерять этот вопрос.'),
    }


def normal_line(rng):
    """Нормаль: минус обратная величина, а не просто минус."""
    a = rng.choice([1, 2, 4])
    b = rng.choice([-6, -4, 3, 5])
    at = rng.choice([-3, -2, -1, 1, 2])
    f = a*x**2 + b*x + 7
    slope = sp.diff(f, x).subs(x, at)
    while slope == 0:
        at += 1
        slope = sp.diff(f, x).subs(x, at)
    return {
        'prompt': (f'Найдите уравнение нормали к кривой $y = {_tex(f)}$ '
                   f'в точке, где $x = {at}$. Ответ — выражение через $x$.'),
        'answer': _line(-1/slope, (at, f.subs(x, at))),
        'check': tangent_check(sp.Eq(y, f), at, normal=True),
        'budget_ms': 120_000,
        'note': ('Наклон нормали — $-1/m$, а не $-m$. У касательной с '
                 'наклоном 2 нормаль идёт с $-\\tfrac12$.'),
    }


def point_from_gradient(rng):
    """Наклон дан — найти точку. У параболы такая точка ровно одна."""
    a = rng.choice([1, 2, 3])
    b = rng.choice([-7, -5, -1, 3, 6])
    m = rng.choice([-4, -2, 1, 2, 5])
    f = a*x**2 + b*x - 2
    at = sp.Rational(m - b, 2*a)
    return {
        'prompt': (f'Касательная к кривой $y = {_tex(f)}$ имеет наклон '
                   f'${m}$. Найдите абсциссу точки касания.'),
        'answer': at,
        'check': where_check(sp.Eq(y, f), m, (-20, 20)),
        'budget_ms': 120_000,
        'note': ('Приравнять производную к числу и решить. Если корней '
                 'вышло больше одного, лишние отсекает область из условия.'),
    }


def implicit_derivative(rng):
    """Кривая задана уравнением: в ответе остаются обе буквы."""
    a = rng.choice([1, 2, 3, 4])
    b = rng.choice([1, 2, 5, 9])
    c = rng.choice([4, 9, 16, 25])
    shape = a*x**2 + b*y**2 - c
    edge = float(sp.sqrt(sp.Rational(c, a)))
    return {
        'prompt': (f'Кривая задана уравнением ${_tex(sp.Eq(a*x**2 + b*y**2, c))}$. '
                   f'Найдите $\\frac{{\\mathrm{{d}}y}}{{\\mathrm{{d}}x}}$ '
                   f'через $x$ и $y$.'),
        'answer': -a*x/(b*y),
        'check': slope_check(shape, domain=(0.1 * edge, 0.8 * edge)),
        'budget_ms': 150_000,
        'note': ('Производная $y^2$ по $x$ — это $2y\\frac{\\mathrm{d}y}'
                 '{\\mathrm{d}x}$, а не $2y$. Обе буквы в ответе — это '
                 'законченный ответ.'),
    }


def implicit_tangent(rng):
    """Касательная к окружности в точке решётки: обе координаты сразу."""
    px, py, r = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13),
                            (8, 15, 17), (15, 8, 17), (7, 24, 25)])
    px *= rng.choice([1, -1])
    py *= rng.choice([1, -1])
    shape = x**2 + y**2 - r**2
    return {
        'prompt': (f'Кривая задана уравнением $x^2 + y^2 = {r**2}$. Найдите '
                   f'уравнение касательной к ней в точке $({px},\\,{py})$. '
                   f'Ответ — выражение через $x$.'),
        'answer': _line(sp.Rational(-px, py), (px, py)),
        'check': tangent_check(shape, (px, py)),
        'budget_ms': 150_000,
        'note': ('Наклон здесь $-x/y$, и чтобы он стал числом, нужны обе '
                 'координаты точки, а не одна.'),
    }


def second_implicit(rng):
    """Вторая производная соотношения: у окружности она равна −r²/y³."""
    px, py, r = rng.choice([(3, 4, 5), (4, 3, 5), (5, 12, 13), (12, 5, 13),
                            (8, 15, 17), (15, 8, 17)])
    py *= rng.choice([1, -1])
    shape = x**2 + y**2 - r**2
    return {
        'prompt': (f'Кривая задана уравнением $x^2 + y^2 = {r**2}$. Найдите '
                   f'значение $\\frac{{\\mathrm{{d}}^2y}}{{\\mathrm{{d}}x^2}}$ '
                   f'в точке $({px},\\,{py})$.'),
        'answer': sp.Rational(-r**2, py**3),
        'check': second_check(shape, (px, py)),
        'budget_ms': 180_000,
        'note': ('Продифференцировать соотношение ещё раз, помня, что и $y$, '
                 'и $\\frac{\\mathrm{d}y}{\\mathrm{d}x}$ — функции от $x$. '
                 'У окружности выходит $-r^2/y^3$.'),
    }


def right_angles(rng):
    """Прямой угол как условие: наклон второй кривой — минус обратный."""
    a = rng.choice([1, 2, 3])
    at = rng.choice([-3, -2, -1, 1, 2, 3])
    f = a*x**2
    slope = sp.diff(f, x).subs(x, at)
    other = -1/slope
    point = (at, f.subs(x, at))
    return {
        'prompt': (f'Кривая $C_1$ задана уравнением $y = {_tex(f)}$. Кривая '
                   f'$C_2$ проходит через точку $({at},\\,{_tex(point[1])})$ '
                   f'и пересекает $C_1$ там под прямым углом. Найдите '
                   f'$\\frac{{\\mathrm{{d}}y}}{{\\mathrm{{d}}x}}$ для $C_2$ '
                   f'в этой точке.'),
        'answer': other,
        # Проверка строит прямую с искомым наклоном через ту же точку и меряет
        # её наклон ходьбой — эталона по-прежнему нет нигде.
        'check': slope_check(sp.Eq(y, _line(other, point)), at=at),
        'budget_ms': 120_000,
        'note': ('Прямой угол значит $m_1m_2 = -1$. Показать, что наклоны '
                 'просто различны, — это не то же самое.'),
    }


def tangency_condition(rng):
    """Касание как условие: постоянная сидит внутри кривой."""
    h = sp.Symbol('h')
    at = rng.choice([1, 2, 3, 4])
    slope = rng.choice([-6, -4, -2, 2, 4, 6])
    shape = y + (x - h)**2
    return {
        'prompt': (f'Кривая задана уравнением $y = -(x - h)^2$, где $h$ — '
                   f'постоянная. Касательная к ней при $x = {at}$ имеет '
                   f'наклон ${slope}$. Найдите $h$.'),
        'answer': sp.Rational(2*at + slope, 2),
        'check': constant_check(shape, 'h', at, slope, (-20, 20)),
        'budget_ms': 120_000,
        'note': ('Подставлять ответ некуда: буква стоит внутри кривой. '
                 'Условие даёт уравнение на неё — $-2(x - h) = m$ при данном '
                 '$x$.'),
    }


GENERATORS = {
    'E4.tangent_line': tangent_line,
    'E4.normal_line': normal_line,
    'E4.point_from_gradient': point_from_gradient,
    'E4.implicit_derivative': implicit_derivative,
    'E4.implicit_tangent': implicit_tangent,
    'E4.second_implicit': second_implicit,
    'E4.right_angles': right_angles,
    'E4.tangency_condition': tangency_condition,
}
