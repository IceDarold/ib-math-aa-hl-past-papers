"""Задачи на счёт для практикума B3: преобразования графиков.

Практикум английский, а тренажёр русский, и это не противоречие: коды
приёмов общие, а условия задач пишутся на языке того, кто их читает.

Тема отвечает картинками, а картинку в поле ввода не наберёшь. Поэтому
каждая задача спрашивает **одно число**, и всегда то самое, за которое
в markscheme стоит балл: величину сдвига после сжатия, ординату вершины
после растяжения, число изломов, коэффициент перед дробью, период,
множество значений. Ни один из этих ответов нельзя угадать по форме
кривой — их надо посчитать.
"""
from __future__ import annotations

import sympy as sp

from .common import count_check, domain_check, exact_check

x = sp.Symbol('x')
R = sp.Rational


def _sign(value):
    return '+' if value >= 0 else '-'


def read_graph(rng):
    """Приём 1: значение и композиция значений, снятые с графика."""
    a = rng.choice([-4, -3, -2, 2, 3, 4])
    b = rng.choice([-5, -1, 1, 5, 6])
    c = rng.choice([-6, -2, 0, 3, 7])
    return {
        'prompt': (f'На графике $y = f(x)$ отмечены точки '
                   f'$({a},\\, {b})$ и $({b},\\, {c})$. '
                   f'Найдите $(f \\circ f)({a})$.'),
        'answer': sp.Integer(c),
        'check': exact_check(c),
        'budget_ms': 30_000,
        'note': 'Первое прочтение даёт вход для второго.',
    }


def apply_transform(rng):
    """Приём 2: вертикальные преобразования двигают только ординату."""
    px = rng.choice([-3, -2, -1, 1, 2, 3])
    py = rng.choice([-6, -4, 2, 5, 8])
    s = rng.choice([R(1, 2), 2, 3, -1])
    d = rng.choice([-4, -2, 1, 3, 5])
    shown = f'\\frac{{1}}{{2}}' if s == R(1, 2) else ('-' if s == -1 else f'{s}')
    return {
        'prompt': (f'График $f$ имеет максимум в точке $({px},\\, {py})$. '
                   f'Пусть $g(x) = {shown} f(x) {_sign(d)} {abs(d)}$. '
                   f'Найдите ординату соответствующей точки графика $g$.'),
        'answer': sp.sympify(s * py + d),
        'check': exact_check(s * py + d),
        'budget_ms': 45_000,
        'note': 'Абсцисса не меняется: оба преобразования вертикальные.',
    }


def name_transform(rng):
    """Приём 3: величина сдвига зависит от того, что сделали раньше."""
    b = rng.choice([2, 3, 4, 5])
    c = rng.choice([1, 2, 3, 5, 7])
    return {
        'prompt': (f'График $y = \\sin x$ переводится в график '
                   f'$y = \\sin({b}x - {c})$ сжатием по горизонтали '
                   f'в $\\tfrac{{1}}{{{b}}}$ раз, **а затем** сдвигом вправо. '
                   f'На сколько сдвиг?'),
        'answer': R(c, b),
        'check': exact_check(R(c, b)),
        'budget_ms': 60_000,
        'note': ('Вынесите множитель за скобку: sin(bx − c) = sin(b(x − c/b)). '
                 'Если сдвигать до сжатия, сдвиг был бы на c.'),
    }


def match_transform(rng):
    """Приём 4: деление уголком показывает все три преобразования разом."""
    a = rng.choice([2, 3, 5, 7])
    h = rng.choice([-5, -3, -2, 2, 3, 4])
    lift = rng.choice([6, 10, 14, 21, 26])
    # (a·x + b)/(x − h) = a + (b + a·h)/(x − h), поэтому числитель считается
    # назад от нужного коэффициента растяжения, а не вперёд от него.
    b = lift - a * h
    while b == 0:
        lift += 4
        b = lift - a * h
    return {
        'prompt': (f'$y = \\dfrac{{{a}x {_sign(b)} {abs(b)}}}{{x {_sign(-h)} '
                   f'{abs(h)}}}$ получается из $y = \\dfrac1x$ сдвигом, '
                   f'растяжением по вертикали и сдвигом. '
                   f'Найдите коэффициент растяжения.'),
        'answer': sp.Integer(lift),
        'check': exact_check(lift),
        'budget_ms': 75_000,
        'note': 'Разделите уголком: получится a + m/(x − h), и m — ответ.',
    }


def use_symmetry(rng):
    """Приём 5: чётность и нечётность как правило подстановки."""
    odd = rng.choice([True, False])
    a = rng.choice([2, 3, 4, 5, 6])
    v = rng.choice([-9, -7, -3, 4, 6, 8])
    word = 'нечётной' if odd else 'чётной'
    return {
        'prompt': (f'Функция $f$ является {word}, и $f({a}) = {v}$. '
                   f'Найдите $f(-{a})$.'),
        'answer': sp.Integer(-v if odd else v),
        'check': exact_check(-v if odd else v),
        'budget_ms': 30_000,
        'note': 'Нечётная: поворот на 180° вокруг начала. Чётная: зеркало в оси y.',
    }


def fold_graph(rng):
    """Приём 6: излом рождается только в корне нечётной кратности."""
    roots = rng.sample([-3, -2, -1, 1, 2, 3], 3)
    squared = rng.choice([0, 1, 2, None])
    factors, cusps = [], 0
    for i, root in enumerate(sorted(roots)):
        power = 2 if i == squared else 1
        cusps += (power == 1)
        piece = f'(x {_sign(-root)} {abs(root)})'
        factors.append(piece if power == 1 else piece + '^2')
    return {
        'prompt': (f'$f(x) = {"".join(factors)}$. '
                   f'Сколько изломов у графика $y = |f(x)|$?'),
        'answer': sp.Integer(cusps),
        'check': count_check(cusps),
        'budget_ms': 60_000,
        'note': ('В корне чётной кратности график касается оси и излома '
                 'не даёт: он там уже минимум.'),
    }


def sketch_standard(rng):
    """Приём 7: период считается по коэффициенту, а не по амплитуде."""
    amp = rng.choice([2, 3, 4, 5])
    b = sp.sympify(rng.choice([2, 3, 4, R(1, 2), R(2, 3), R(3, 2)]))
    shown = f'{b}' if b.is_Integer else sp.latex(b)
    return {
        'prompt': (f'Найдите период функции $y = {amp}\\sin({shown}x)$.'),
        'answer': sp.simplify(2 * sp.pi / b),
        'check': exact_check(2 * sp.pi / b),
        'budget_ms': 45_000,
        'note': 'Амплитуда на период не влияет вовсе.',
    }


def sketch_asymptotic(rng):
    """Приём 8: горизонтальная асимптота и есть недостающее значение."""
    a = rng.choice([2, 3, 4, 5, -2, -3])
    b = rng.choice([-9, -5, -1, 1, 7, 11])
    h = rng.choice([-4, -2, 2, 3, 5])
    return {
        'prompt': (f'$f(x) = \\dfrac{{{a}x {_sign(b)} {abs(b)}}}'
                   f'{{x {_sign(-h)} {abs(h)}}}$, $x \\ne {h}$. '
                   f'Запишите множество значений $f$.'),
        'answer': sp.Complement(sp.S.Reals, sp.FiniteSet(a)),
        'check': domain_check(sp.Complement(sp.S.Reals, sp.FiniteSet(a))),
        'budget_ms': 60_000,
        'note': 'Горизонтальная асимптота — это то значение, которого нет.',
    }


def explore_family(rng):
    """Приём 9: сколько решений — вопрос о том, где картинка меняется."""
    c = rng.choice([-4, -3, -2, -1, 0, 1, 2, 3, 4])
    count = 3 if abs(c) < 2 else (2 if abs(c) == 2 else 1)
    tail = '' if c == 0 else f' {_sign(c)} {abs(c)}'
    return {
        'prompt': (f'Сколько корней у уравнения $x^3 - 3x{tail} = 0$?'),
        'answer': sp.Integer(count),
        'check': count_check(count),
        'budget_ms': 75_000,
        'note': ('У y = x³ − 3x максимум 2 при x = −1 и минимум −2 при x = 1; '
                 'прямая y = −c режет её трижды, только пока лежит между ними.'),
    }


GENERATORS = {
    'B3.read_graph': read_graph,
    'B3.apply_transform': apply_transform,
    'B3.name_transform': name_transform,
    'B3.match_transform': match_transform,
    'B3.use_symmetry': use_symmetry,
    'B3.fold_graph': fold_graph,
    'B3.sketch_standard': sketch_standard,
    'B3.sketch_asymptotic': sketch_asymptotic,
    'B3.explore_family': explore_family,
}
