"""Задачи на счёт для практикума B4: исследование функции и асимптоты.

Практикум английский, а тренажёр русский, и это не противоречие: коды
приёмов общие, а условия задач пишутся на языке того, кто их читает.

Тема отвечает прямыми и картинками, а ни то, ни другое в поле ввода не
наберёшь. Поэтому каждая задача спрашивает **одно число или одно
множество**, и всегда то самое, за которое в markscheme стоит балл:
свободный член наклонной асимптоты, число ветвей, конец отрезка, оба
пересечения с осью y, число пересечений с осью x. Ни один из этих
ответов не читается с картинки — их надо посчитать.
"""
from __future__ import annotations

import sympy as sp

from .common import count_check, domain_check, exact_check, set_check

x = sp.Symbol('x')
R = sp.Rational


def _sign(value):
    return '+' if value >= 0 else '-'


def _lin(coef, const):
    """Строка «ax + b» с правильными знаками и без единичного коэффициента."""
    head = f'{"-" if coef == -1 else ("" if coef == 1 else coef)}x'
    if const == 0:
        return head
    return f'{head} {_sign(const)} {abs(const)}'


def name_asymptote(rng):
    """Приём 1: горизонтальная асимптота — отношение старших коэффициентов."""
    a = rng.choice([2, 3, 5, -2, -3, 7])
    c = rng.choice([2, 3, 4, -3, 5])
    b = rng.choice([-7, -3, 1, 4, 9])
    d = rng.choice([-6, -2, 3, 8])
    while R(a, c) == R(b, d):
        d = rng.choice([-6, -2, 3, 8, 11])
    return {
        'prompt': (f'$f(x) = \\dfrac{{{_lin(a, b)}}}{{{_lin(c, d)}}}$. '
                   f'Чему равно $y$ в уравнении горизонтальной асимптоты?'),
        'answer': R(a, c),
        'check': exact_check(R(a, c)),
        'budget_ms': 30_000,
        'note': ('Степени равны, значит отношение старших коэффициентов. '
                 'Свободные члены на асимптоту не влияют вовсе.'),
    }


def asymptote_by_limit(rng):
    """Приём 2: асимптота, которую даёт только предел."""
    a = rng.choice([2, 3, 4, 6])
    c = rng.choice([-5, -1, 0, 2, 7])
    b = rng.choice([2, 3, 5])
    tail = '' if c == 0 else f' {_sign(c)} {abs(c)}'
    want = a * sp.pi / 2 + c
    return {
        'prompt': (f'$f(x) = {a}\\arctan({b}x){tail}$. '
                   f'Чему равно $y$ в уравнении горизонтальной асимптоты '
                   f'при $x \\to +\\infty$?'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 45_000,
        'note': ('Сначала предел внутри: bx → +∞. Потом внешняя функция: '
                 'arctan от бесконечности это π/2, а не бесконечность.'),
    }


def oblique_asymptote(rng):
    """Приём 3: свободный член наклонной — то, на чём деление бросают."""
    a = rng.choice([1, 2, 3, 4])
    c = rng.choice([1, 2, 3])
    e = rng.choice([-9, -4, 2, 5, 6])
    b = rng.choice([-8, -3, 1, 7, 12])
    slope = R(a, c)
    const = R(b - slope * e, c)
    while const == 0:
        b += 3
        const = R(b - slope * e, c)
    return {
        'prompt': (f'$f(x) = \\dfrac{{{a}x^2 {_sign(b)} {abs(b)}x - 6}}'
                   f'{{{_lin(c, e)}}}$ имеет наклонную асимптоту $y = mx + k$. '
                   f'Найдите $k$.'),
        'answer': const,
        'check': exact_check(const),
        'budget_ms': 75_000,
        'note': ('m = a/c из старших членов, дальше приравняйте коэффициенты '
                 'при x: b = k·c + m·e. Свободный член −6 в ответ не входит.'),
    }


def sketch_rational(rng):
    """Приём 4: ветвей на одну больше, чем вертикальных асимптот."""
    kind = rng.choice(['two', 'two', 'one', 'none'])
    if kind == 'two':
        p, q = sorted(rng.sample([-4, -2, -1, 1, 3, 5], 2))
        bottom = f'(x {_sign(-p)} {abs(p)})(x {_sign(-q)} {abs(q)})'
        walls = 2
    elif kind == 'one':
        p = rng.choice([-3, -1, 2, 4])
        bottom = f'(x {_sign(-p)} {abs(p)})^2'
        walls = 1
    else:
        c = rng.choice([1, 4, 9, 16])
        bottom = f'x^2 + {c}'
        walls = 0
    top = rng.choice([1, 2, 5, 7])
    return {
        'prompt': (f'$f(x) = \\dfrac{{{top}}}{{{bottom}}}$. '
                   f'Сколько ветвей у графика $y = f(x)$?'),
        'answer': sp.Integer(walls + 1),
        'check': count_check(walls + 1),
        'budget_ms': 45_000,
        'note': ('Вертикальные асимптоты режут прямую на куски, и на каждом '
                 'куске ровно одна ветвь. Кратный корень знаменателя — '
                 'одна асимптота, а не две.'),
    }


def find_range(rng):
    """Приём 5: один конец достигается, другой — асимптота."""
    a = rng.choice([-4, -2, 2, 3, 5])
    d = rng.choice([1, 2, 4, 5])
    b = rng.choice([-9, -6, 3, 8, 12])
    while R(b, d) == a:
        b += 5
    low, high = sorted([R(b, d), sp.Integer(a)])
    region = (sp.Interval.Ropen(low, high) if R(b, d) < a
              else sp.Interval.Lopen(low, high))
    return {
        'prompt': (f'$f(x) = \\dfrac{{{_lin(a, b)}}}{{x + {d}}}$ при '
                   f'$x \\ge 0$. Запишите множество значений $f$.'),
        'answer': region,
        'check': domain_check(region, var='y'),
        'budget_ms': 90_000,
        'note': ('f(0) достигается, горизонтальная асимптота y = a — нет. '
                 'Функция монотонна на [0, ∞), так что между ними она '
                 'проходит всё.'),
    }


def sketch_labelled(rng):
    """Приём 6: конец отрезка — самый забываемый балл темы."""
    a = rng.choice([2, 3, 4])
    b = rng.choice([1, 2, 3, 5])
    end = rng.choice([-2, -1, 1, 2])
    want = sp.Integer(end)**3 - a * sp.Integer(end)**2 + b
    return {
        'prompt': (f'Эскиз $y = x^3 - {a}x^2 + {b}$ строят на отрезке, '
                   f'правый конец которого $x = {end}$. Условие требует '
                   f'указать координаты концов. Найдите ординату этого конца.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 30_000,
        'note': ('Подстановка, и больше ничего. Балл за концы отрезка '
                 'теряют не потому, что не умеют считать, а потому, '
                 'что их не отмечают.'),
    }


def sketch_curvature(rng):
    """Приём 7: размер второй производной задаёт остроту поворота."""
    a = rng.choice([2, 3, 5, 7])
    b = rng.choice([2, 3, 4])
    c = rng.choice([-3, 0, 1, 6])
    tail = '' if c == 0 else f' {_sign(c)} {abs(c)}'
    want = -a * b**2
    return {
        'prompt': (f'$f(x) = {a}\\cos({b}x){tail}$. В точке $x = 0$ у графика '
                   f'максимум. Найдите $f\'\'(0)$.'),
        'answer': sp.Integer(want),
        'check': exact_check(want),
        'budget_ms': 45_000,
        'note': ('f\'\' = −ab²cos(bx). Знак говорит, что это максимум; '
                 'величина говорит, насколько остро график в нём повёрнут.'),
    }


def sketch_implicit(rng):
    """Приём 8: пересечений с осью y два, а не одно."""
    k = rng.choice([4, 9, 16, 25, 36])
    a = rng.choice([2, 3, 4, -2, -5])
    root = sp.sqrt(k)
    return {
        'prompt': (f'Кривая задана уравнением $y^2 = {k} {_sign(a)} {abs(a)}x$. '
                   f'Запишите все ординаты точек её пересечения с осью $y$.'),
        'answer': [-root, root],
        'check': set_check([-root, root]),
        'budget_ms': 45_000,
        'note': ('При x = 0 остаётся y² = k, и корней два. Кривая не функция: '
                 'ось x — её ось симметрии.'),
    }


def count_roots(rng):
    """Приём 9: высоты стационарных точек решают всё."""
    a = rng.choice([3, -3, 6, -6])
    hump = R(4 * a**3, 27)
    lo, hi = sorted([sp.Integer(0), hump])
    b = rng.choice([lo - 5, lo, (lo + hi) / 2, hi, hi + 7])
    b = sp.nsimplify(b)
    heights = (b, hump + b)
    if any(h == 0 for h in heights):
        count = 2
    elif heights[0] * heights[1] < 0:
        count = 3
    else:
        count = 1
    return {
        'prompt': (f'Сколько раз кривая $y = x^3 {_sign(a)} {abs(a)}x^2 '
                   f'{_sign(b)} {sp.nsimplify(abs(b))}$ пересекает ось $x$?'),
        'answer': sp.Integer(count),
        'check': count_check(count),
        'budget_ms': 90_000,
        'note': ('Стационарные точки при x = 0 и x = −2a/3, высоты b и '
                 '4a³/27 + b. Три пересечения — когда высоты разных знаков, '
                 'два — когда одна из них ноль.'),
    }


GENERATORS = {
    'B4.name_asymptote': name_asymptote,
    'B4.asymptote_by_limit': asymptote_by_limit,
    'B4.oblique_asymptote': oblique_asymptote,
    'B4.sketch_rational': sketch_rational,
    'B4.find_range': find_range,
    'B4.sketch_labelled': sketch_labelled,
    'B4.sketch_curvature': sketch_curvature,
    'B4.sketch_implicit': sketch_implicit,
    'B4.count_roots': count_roots,
}
