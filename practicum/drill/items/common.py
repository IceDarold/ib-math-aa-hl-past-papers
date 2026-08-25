"""Описания проверок для задач на счёт.

Ответ не хранится в задании открытым текстом там, где его можно спрятать
за хеш: сервер отдаёт задание странице, и незачем присылать вместе с ним
ответ. Где проверка требует самого выражения (точное значение, уравнение
для подстановки корней), оно уходит на страницу — но такие задания и так
проверяются по существу, а не по совпадению.
"""
from __future__ import annotations

import os
import sys

PRACTICUM = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
if PRACTICUM not in sys.path:
    sys.path.insert(0, PRACTICUM)

import sympy as sp  # noqa: E402

import kit  # noqa: E402


def num_check(value, sf=3):
    """Числовой ответ с округлением до sf значащих цифр."""
    return {'kind': 'num', 'sf': sf, 'digest': kit.digest(kit.sig(value, sf))}


def exact_check(want):
    """Точное значение: десятичная запись не принимается."""
    return {'kind': 'exact', 'want': sp.srepr(sp.sympify(want))}


def expr_check(want):
    """Символьный ответ, сверяемый по канонической записи."""
    return {'kind': 'expr',
            'digest': kit.digest(sp.srepr(sp.simplify(sp.sympify(want))))}


def set_check(values):
    """Набор значений; порядок не важен."""
    canon = '|'.join(sorted(sp.srepr(sp.simplify(sp.sympify(v)))
                            for v in values))
    return {'kind': 'set', 'digest': kit.digest(canon)}


def roots_check(equation, var='x', domain=None):
    """Корни сверяются подстановкой в само уравнение, а не с эталоном."""
    spec = {'kind': 'roots', 'equation': sp.srepr(sp.sympify(equation)),
            'var': var}
    if domain is not None:
        spec['domain'] = sp.srepr(domain)
    return spec


def equation_check(want, var='x'):
    """Ответ — само уравнение, с точностью до переноса и множителя-числа."""
    return {'kind': 'equation', 'want': sp.srepr(sp.sympify(want)),
            'var': var}


def triangle_check(find, value, known):
    """Часть треугольника проверяется достраиванием из данных условия."""
    return {'kind': 'triangle', 'find': find, 'known': known,
            'expected': float(value)}


def count_check(value):
    """Ответ — целое число (сколько корней, сколько треугольников)."""
    return {'kind': 'count', 'value': int(value)}


def series_check(want, var='x', sf=6):
    """Отрезок ряда или многочлен: сверяется значениями, а не записью."""
    return {'kind': 'series', 'var': var,
            'digest': kit.digest(kit._series_canon(sp.sympify(want),
                                                   sp.Symbol(var), sf))}


def complex_check(want, sf=6):
    """Комплексное число в любой форме записи."""
    return {'kind': 'complex',
            'digest': kit.digest(kit._complex_canon(sp.sympify(want), sf))}


def complex_set_check(values, sf=6):
    """Набор комплексных чисел: корни n-й степени, вершины многоугольника."""
    canon = '|'.join(sorted(kit._complex_canon(sp.sympify(v), sf)
                            for v in values))
    return {'kind': 'complex_set', 'digest': kit.digest(canon)}


def solution_set_check(inequality, var='x', domain=None):
    """Множество решений: эталона нет, sympy решает неравенство сам."""
    spec = {'kind': 'solution_set', 'var': var,
            'inequality': sp.srepr(sp.sympify(inequality))}
    if domain is not None:
        spec['domain'] = sp.srepr(domain)
    return spec


def ode_check(rhs, ic=None, var='x', dep='y'):
    """Решение дифференциального уравнения: проверяется подстановкой."""
    spec = {'kind': 'ode', 'rhs': sp.srepr(sp.sympify(rhs)), 'var': var,
            'dep': dep}
    if ic is not None:
        spec['ic'] = [sp.srepr(sp.sympify(v)) for v in ic]
    return spec


def identity_check(want, var='x', samples=None):
    """Тождественное равенство: проверяется в точках, а не по записи."""
    spec = {'kind': 'identity', 'want': sp.srepr(sp.sympify(want)), 'var': var}
    if samples:
        spec['samples'] = list(samples)
    return spec


def factored_check(original, var='x', max_deg=1):
    """Разложение на множители: и равенство, и форма записи."""
    return {'kind': 'factored', 'original': sp.srepr(sp.sympify(original)),
            'var': var, 'max_deg': max_deg}


def apart_check(original, var='x'):
    """Простейшие дроби: и равенство, и форма записи."""
    return {'kind': 'apart', 'original': sp.srepr(sp.sympify(original)),
            'var': var}


def inverse_check(f, var='x', domain=None):
    """Ответ — обратная функция: эталона нет, f подставляется внутрь ответа."""
    spec = {'kind': 'inverse', 'f': sp.srepr(sp.sympify(f)), 'var': var}
    if domain is not None:
        spec['domain'] = sp.srepr(domain)
    return spec


def domain_check(region, var='x'):
    """Ответ — область определения или множество значений: сверяется как множество."""
    return {'kind': 'domain', 'var': var,
            'digest': kit.digest(sp.srepr(kit._as_set(region, sp.Symbol(var))))}


def poly_latex(terms, var='x'):
    """LaTeX многочлена по списку (коэффициент, степень), от старшей к младшей.

    Нужна потому, что sympy печатает слагаемые в своём порядке и член
    с буквой уезжает вперёд: `k x + x^3 - 7 x^2` вместо привычной записи.
    А склейка знаков руками в каждом генераторе — источник ошибок.
    """
    parts = []
    for coefficient, power in terms:
        c = sp.sympify(coefficient)
        if c == 0:
            continue
        negative = bool(c.is_number and c.is_negative)
        magnitude = -c if negative else c
        if power == 0:
            body = sp.latex(magnitude)
        else:
            head = '' if (c.is_number and magnitude == 1) else sp.latex(magnitude)
            body = head + (var if power == 1 else f'{var}^{{{power}}}')
        parts.append(('-' if negative else '+', body))
    if not parts:
        return '0'
    sign, body = parts[0]
    out = f'-{body}' if sign == '-' else body
    for sign, body in parts[1:]:
        out += f' {sign} {body}'
    return out


def roots_in_check(expression, domain, var='x', deg=False):
    """Корни на отрезке: сканированием, а не решением уравнения."""
    return {'kind': 'roots_in', 'var': var, 'deg': deg,
            'expression': sp.srepr(sp.sympify(expression)),
            'domain': [sp.srepr(sp.sympify(v)) for v in domain]}


def hours_word(count):
    """«4 часа», но «6 часов»: числительное согласуется с существительным."""
    if 11 <= count % 100 <= 14:
        return 'часов'
    last = count % 10
    if last == 1:
        return 'час'
    if 2 <= last <= 4:
        return 'часа'
    return 'часов'
