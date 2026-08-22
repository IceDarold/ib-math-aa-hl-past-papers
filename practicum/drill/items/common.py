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
