"""Задачи на счёт для практикума E6: площади, объёмы вращения, накопление.

Тема — один вопрос, заданный восемью способами: что этот интеграл меряет.
Генераторы идут по лестнице карточки: первый и второй меряют плоскую
область, третий, четвёртый и пятый — тело вращения, шестой — его обёртку,
седьмой и восьмой — движение и накопление.

Проверки живут в kit вместе с практикумом, и общее у них одно: ни одна
не берёт производной. Площадь складывается из полос, объём из дисков,
поверхность из усечённых конусов, путь из шагов. Поэтому проверка меряет
заново, а не повторяет выкладку ученика, и совпадение с ней — это второе
измерение, а не второй прогон той же формулы.
"""
from __future__ import annotations

import sympy as sp

from .common import (amount_check, position_check, region_check, solid_check,
                     surface_check, travelled_check)

x, y, t = sp.symbols('x y t')
R = sp.Rational


def _tex(expr):
    return sp.latex(expr)


def area_under_curve(rng):
    """Полная площадь под кривой, которая пересекает ось внутри отрезка."""
    a = rng.choice([1, 2, 3])
    b = a + rng.choice([1, 2])
    f = x**2 - a**2
    whole = (sp.integrate(a**2 - x**2, (x, 0, a))
             + sp.integrate(f, (x, a, b)))
    return {
        'prompt': (f'Кривая $y = {_tex(f)}$ пересекает ось $x$ внутри '
                   f'отрезка $0 \\le x \\le {b}$. Найдите **полную** площадь '
                   f'области между кривой, осью $x$ и прямой $x = {b}$.'),
        'answer': whole,
        'check': region_check(f, 0, 0, b),
        'budget_ms': 120_000,
        'note': ('Площадь и интеграл здесь разные числа: кусок под осью '
                 'в интеграле вычитается, а в площади прибавляется. '
                 'Разбейте отрезок нулём кривой и сложите модули.'),
    }


def area_between_curves(rng):
    """Площадь между параболой и прямой: пределы даёт пересечение."""
    a = rng.choice([1, 2, 3])
    c = rng.choice([4, 6, 9, 12])
    top = c - x**2
    bottom = a*x
    left, right = sorted(sp.solve(sp.Eq(top, bottom), x))
    whole = sp.integrate(top - bottom, (x, left, right))
    return {
        'prompt': (f'Найдите площадь области, заключённой между параболой '
                   f'$y = {_tex(top)}$ и прямой $y = {_tex(bottom)}$.'),
        'answer': sp.simplify(whole),
        'check': region_check(top, bottom, window=(-8, 8)),
        'budget_ms': 150_000,
        'note': ('Пределов в условии нет — их даёт уравнение '
                 f'${_tex(top)} = {_tex(bottom)}$. Вычитать надо верхнюю '
                 'минус нижнюю, иначе площадь выйдет со знаком минус.'),
    }


def volume_about_x(rng):
    """Объём вращения вокруг оси x: диски по квадрату функции."""
    a = rng.choice([1, 2, 3])
    b = rng.choice([1, 2, 4])
    f = sp.sqrt(a*x + b)
    top = rng.choice([1, 2, 3])
    whole = sp.pi*sp.integrate(a*x + b, (x, 0, top))
    return {
        'prompt': (f'Область под кривой $y = {_tex(f)}$ при '
                   f'$0 \\le x \\le {top}$ вращают на $2\\pi$ вокруг оси '
                   f'$x$. Найдите объём полученного тела точно.'),
        'answer': sp.simplify(whole),
        'check': solid_check(f, 0, top),
        'budget_ms': 120_000,
        'note': ('Возводить в квадрат надо функцию, и множитель $\\pi$ '
                 'стоит перед интегралом, а не появляется в конце.'),
    }


def volume_about_y(rng):
    """Объём вращения вокруг оси y: x выражают через y до всякого интеграла."""
    a = rng.choice([1, 2, 3])
    top = rng.choice([1, 2, 3])
    radius = sp.sqrt(a*y**2 + 1)
    whole = sp.pi*sp.integrate(a*y**2 + 1, (y, 0, top))
    return {
        'prompt': (f'Кривая задана уравнением $x^2 - {a}y^2 = 1$ при '
                   f'$x > 0$. Область между ней и осью $y$ при '
                   f'$0 \\le y \\le {top}$ вращают на $2\\pi$ вокруг оси '
                   f'$y$. Найдите объём тела точно.'),
        'answer': sp.simplify(whole),
        'check': solid_check(radius, 0, top, var='y', axis='y'),
        'budget_ms': 150_000,
        'note': ('Формуле нужен $x^2$, и уравнение кривой отдаёт его сразу: '
                 'извлекать корень, чтобы потом возвести в квадрат, незачем. '
                 'Пределы — по $y$.'),
    }


def volume_as_condition(rng):
    """Объём известен, найти надо предел интегрирования."""
    a = rng.choice([1, 2, 4])
    top = rng.choice([2, 3, 4])
    known = sp.pi*a*top**2/2
    return {
        'prompt': (f'Область под кривой $y = \\sqrt{{{a}x}}$ от $x = 0$ '
                   f'до $x = k$ вращают на $2\\pi$ вокруг оси $x$. Объём '
                   f'полученного тела равен ${_tex(known)}$. Найдите $k$.'),
        'answer': top,
        'check': solid_check(sp.sqrt(a*x), 0, x, value=known),
        'budget_ms': 120_000,
        'note': ('Тот же интеграл, прочитанный наоборот: запишите объём '
                 'через $k$, приравняйте к данному числу и решите. '
                 'Отрицательный корень отбрасывается.'),
    }


def surface_of_revolution(rng):
    """Площадь поверхности конуса по формуле из условия."""
    m = rng.choice([1, 2, 3, 4])
    h = rng.choice([1, 2, 3])
    whole = sp.pi*m*sp.sqrt(1 + m**2)*h**2
    return {
        'prompt': (f'Прямую $y = {m}x$ при $0 \\le x \\le {h}$ вращают '
                   f'на $360^\\circ$ вокруг оси $x$. Площадь полученной '
                   f'поверхности равна $A = 2\\pi\\int_0^{{{h}}} y\\,'
                   f'\\sqrt{{1 + (\\mathrm{{d}}y/\\mathrm{{d}}x)^2}}\\,'
                   f'\\mathrm{{d}}x$. Найдите $A$ точно.'),
        'answer': sp.simplify(whole),
        'check': surface_check(m*x, 0, h),
        'budget_ms': 120_000,
        'note': ('Подкоренное выражение здесь постоянное, и множитель $y$ '
                 'терять нельзя: без него выйдет длина отрезка, а не '
                 'площадь поверхности.'),
    }


def displacement(rng):
    """Перемещение по скорости: интеграл со знаком."""
    a = rng.choice([2, 4, 6])
    b = rng.choice([3, 6, 9])
    top = rng.choice([2, 3])
    v = a + b*t - 3*t**2
    whole = sp.integrate(v, (t, 0, top))
    return {
        'prompt': (f'Скорость точки равна $v(t) = {_tex(v)}$ м/с. Найдите '
                   f'её **перемещение** за первые ${top}$ секунд.'),
        'answer': sp.simplify(whole),
        'check': position_check(v, 0, top),
        'budget_ms': 90_000,
        'note': ('Перемещение — это интеграл скорости со знаком: куски '
                 'назад вычитаются. Модуль здесь не нужен.'),
    }


def distance(rng):
    """Пройденный путь: отрезок разбивают нулём скорости."""
    a = rng.choice([2, 3, 4])
    v = t - a
    top = a + rng.choice([1, 2, 3])
    whole = (sp.integrate(a - t, (t, 0, a)) + sp.integrate(v, (t, a, top)))
    return {
        'prompt': (f'Скорость точки равна $v(t) = {_tex(v)}$ м/с. Найдите '
                   f'**путь**, пройденный ею за первые ${top}$ секунд.'),
        'answer': sp.simplify(whole),
        'check': travelled_check(v, 0, top),
        'budget_ms': 120_000,
        'note': (f'Скорость меняет знак при $t = {a}$. Путь складывают '
                 'по модулю: до этого момента точка шла назад, после — '
                 'вперёд, и оба куска прибавляются.'),
    }


def accumulated_change(rng):
    """Накопленное по скорости накопления, с начальным значением."""
    start = rng.choice([10, 20, 50])
    a = rng.choice([2, 3, 4])
    top = rng.choice([2, 4, 6])
    rate = a + t
    whole = start + sp.integrate(rate, (t, 0, top))
    return {
        'prompt': (f'В баке было ${start}$ литров воды. Вода прибывает '
                   f'со скоростью ${_tex(rate)}$ литров в минуту. Сколько '
                   f'литров будет в баке через ${top}$ минут?'),
        'answer': sp.simplify(whole),
        'check': amount_check(rate, 0, top, start=start),
        'budget_ms': 90_000,
        'note': (f'Начальные ${start}$ литров надо прибавить: они даны '
                 'затем, чтобы найти постоянную интегрирования.'),
    }


def _pick(rng, first, second):
    """Два вопроса на один приём: какой достанется, решает жребий."""
    return (first if rng.random() < 0.5 else second)(rng)


GENERATORS = {
    'E6.area_under_curve': area_under_curve,
    'E6.area_between_curves': area_between_curves,
    'E6.volume_about_x': volume_about_x,
    'E6.volume_about_y': volume_about_y,
    'E6.volume_between_and_condition': volume_as_condition,
    'E6.surface_of_revolution': surface_of_revolution,
    'E6.displacement_and_distance':
        lambda rng: _pick(rng, displacement, distance),
    'E6.accumulated_change': accumulated_change,
}
