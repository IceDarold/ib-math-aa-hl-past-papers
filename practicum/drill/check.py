"""Разбор введённого ответа и проверка его настоящими проверками из kit.

Тренажёр не сравнивает строки. Ученик пишет ответ так, как написал бы на
бумаге, — `2sqrt(6)`, `5/2`, `x=1, x=4`, — а дальше работает ровно тот же
код, что и в практикумах: check_num, verify_exact, verify_root_set,
verify_triangle. Значит «верно» в тренажёре и «верно» в ноутбуке означают
одно и то же, и второго набора правил не заводится.

kit печатает разбор в stdout и возвращает bool. Здесь вывод перехватывается
и отдаётся на страницу как есть: сообщение «это десятичная запись, а вопрос
просит точное значение» стоит показать целиком.
"""
from __future__ import annotations

import io
import os
import re
import sys
from contextlib import redirect_stdout

PRACTICUM = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PRACTICUM not in sys.path:
    sys.path.insert(0, PRACTICUM)

import sympy as sp  # noqa: E402
from sympy.parsing.sympy_parser import (  # noqa: E402
    convert_xor, implicit_multiplication_application, parse_expr,
    standard_transformations)

import kit  # noqa: E402

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application, convert_xor)

# То, что пишут от руки, но sympy не понимает.
REPLACEMENTS = (
    ('π', 'pi'),
    ('∞', 'oo'),
    ('−', '-'),      # типографский минус
    ('·', '*'),
    ('×', '*'),
    ('^', '**'),     # convert_xor сделает то же, но до наших скобок
)

NO_ROOTS = {'нет', 'нет корней', 'нету', 'пусто', 'none', 'no roots', '∅', '{}'}


class BadInput(Exception):
    """Ввод не разобрался — это не неверный ответ, а нечитаемая запись."""


# √ пишут без скобок: √6, √(x+1), 2√6. Скобки дописываются здесь,
# иначе неявное умножение превратит √6 в произведение sqrt на 6.
ROOT_SIGN = re.compile(r'√\s*(\([^()]*\)|\d+(?:\.\d+)?|[A-Za-z]\w*)')


def _clean(raw):
    text = str(raw).strip()
    for old, new in REPLACEMENTS:
        text = text.replace(old, new)
    text = ROOT_SIGN.sub(lambda m: f'sqrt({m.group(1).strip("()")})', text)
    if '√' in text:
        raise BadInput('после √ непонятно, что стоит под корнем — '
                       'поставьте скобки')
    text = re.sub(r'\s+', ' ', text)
    return text


def parse_one(raw):
    """Одно выражение."""
    text = _clean(raw)
    if not text:
        raise BadInput('пусто')
    try:
        return parse_expr(text, transformations=TRANSFORMS, evaluate=True)
    except Exception as exc:  # noqa: BLE001 — сообщение уходит на страницу
        raise BadInput(f'не разобрал запись: {exc}') from exc


def parse_many(raw):
    """Набор значений: «1, 4» или «{1, 4}». Пустой ответ — список без корней."""
    text = _clean(raw)
    if text.lower().strip('.') in NO_ROOTS:
        return []
    text = text.strip()
    if text.startswith('{') and text.endswith('}'):
        text = text[1:-1]
    parts = [p for p in re.split(r'[,;]', text) if p.strip()]
    if not parts:
        raise BadInput('пусто')
    return [parse_one(p) for p in parts]


def parse_equation(raw):
    """Ответ-уравнение: «x^2 - 3x = 10»."""
    text = _clean(raw)
    if text.count('=') != 1:
        raise BadInput('нужно уравнение с одним знаком равенства')
    left, right = text.split('=')
    return sp.Eq(parse_one(left), parse_one(right))


def _capture(fn, *args, **kwargs):
    """Запускает проверку из kit и забирает её печать."""
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        ok = fn(*args, **kwargs)
    message = buffer.getvalue().strip()
    # Метка ответа в тренажёре не нужна: на странице и так видно, что это ответ.
    message = re.sub(r'^([✅❌⬜])\s*Ответ:?\s*', r'\1 ', message)
    return bool(ok), message


def evaluate(spec, raw):
    """Проверяет ответ по описанию из задания.

    Возвращает (верно, сообщение). BadInput наверх не пробрасывается:
    нечитаемая запись — это тоже ответ «нет», но с другим объяснением.
    """
    kind = spec['kind']
    try:
        if kind == 'num':
            value = parse_one(raw)
            return _capture(kit.check_num, 'Ответ', float(value),
                            spec.get('sf', 3), spec['digest'])

        if kind == 'exact':
            return _capture(kit.verify_exact, 'Ответ', parse_one(raw),
                            sp.sympify(spec['want']))

        if kind == 'expr':
            return _capture(kit.check_expr, 'Ответ', parse_one(raw),
                            spec['digest'])

        if kind == 'set':
            return _capture(kit.check_set, 'Ответ', parse_many(raw),
                            spec['digest'])

        if kind == 'roots':
            return _capture(kit.verify_root_set, 'Ответ', parse_many(raw),
                            sp.sympify(spec['equation']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            domain=(sp.sympify(spec['domain'])
                                    if spec.get('domain') else None))

        if kind == 'equation':
            return _capture(kit.verify_equation, 'Ответ', parse_equation(raw),
                            sp.sympify(spec['want']),
                            var=sp.Symbol(spec.get('var', 'x')))

        if kind == 'triangle':
            value = parse_one(raw)
            got = {spec['find']: float(value)}
            known = {k: float(v) for k, v in spec['known'].items()}
            return _capture(kit.verify_triangle, 'Ответ', got, **known)

        if kind == 'count':
            value = parse_one(raw)
            ok = sp.simplify(value - sp.Integer(spec['value'])) == 0
            return ok, (f'{kit.OK} Ответ: {value}' if ok
                        else f'{kit.NO} Ответ: {value} — не сходится')

    except BadInput as exc:
        return False, f'{kit.NO} {exc}'

    raise ValueError(f'неизвестный вид проверки: {kind!r}')


def show_answer(value, sf=3):
    """Читаемая запись эталона — её показывают уже после попытки."""
    if isinstance(value, (list, tuple)):
        return ', '.join(show_answer(v, sf) for v in value) or 'нет корней'
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        # Ответ на узнавание — код приёма, а не выражение: sympify превратил
        # бы `div` в функцию деления.
        return value
    if isinstance(value, float):
        return f'{value:.{sf}g}'
    if isinstance(value, int):
        return str(value)
    expr = sp.sympify(value)
    if isinstance(expr, sp.Eq):
        return f'{sp.sstr(expr.lhs)} = {sp.sstr(expr.rhs)}'
    if expr.atoms(sp.Float):
        return f'{float(expr):.{sf}g}'
    return sp.sstr(expr)
