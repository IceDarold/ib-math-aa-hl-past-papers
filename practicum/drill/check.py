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


SPLIT_OR = re.compile(r'\s*(?:\bor\b|\bили\b|∪|\bU\b|\|\|)\s*', re.I)
CHAINED = re.compile(r'^(.+?)(<=|>=|<|>)(.+?)(<=|>=|<|>)(.+)$')
RELATION = re.compile(r'(<=|>=|<|>)')


def _relation(text, var):
    """Одно неравенство. Цепочку −2 < x < 3 разбирает в пересечение."""
    chain = CHAINED.match(text)
    if chain:
        left, op1, middle, op2, right = chain.groups()
        first = _relation(f'{left}{op1}{middle}', var)
        second = _relation(f'{middle}{op2}{right}', var)
        return sp.And(first, second)
    if not RELATION.search(text):
        raise BadInput(f'{text.strip()!r} — это не неравенство')
    return parse_expr(text, transformations=TRANSFORMS, evaluate=True)


def parse_solution_set(raw, var):
    """Ответ-неравенство: «x < -2 or x > 3», «-2 <= x <= 3», «x >= 1».

    Экзамен пишет ответ неравенствами, а не интервалами sympy, поэтому
    разбираем то, что пишут от руки. Куски соединяются «or», «или», «U»
    или знаком объединения.
    """
    text = _clean(raw)
    if not text:
        raise BadInput('пусто')
    if text.lower() in ('нет решений', 'нет', 'пусто', 'none'):
        return sp.EmptySet
    if text.lower() in ('все', 'все x', 'любое x', 'r', 'вся прямая'):
        return sp.S.Reals
    if '&' in text or '|' in text:
        # Запись самого sympy: (-1 < x) & (x < 4). Её печатает и наш же
        # показ эталона, так что принимать её надо.
        try:
            return parse_expr(text, transformations=TRANSFORMS, evaluate=True)
        except Exception as exc:  # noqa: BLE001
            raise BadInput(f'не разобрал неравенство: {exc}') from exc
    pieces = [piece for piece in SPLIT_OR.split(text) if piece.strip()]
    try:
        parts = [_relation(piece, var) for piece in pieces]
    except BadInput:
        raise
    except Exception as exc:  # noqa: BLE001
        raise BadInput(f'не разобрал неравенство: {exc}') from exc
    return sp.Or(*parts) if len(parts) > 1 else parts[0]


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

        if kind == 'roots_in':
            # Тригонометрическое уравнение solveset отдаёт бесконечным
            # семейством; verify_roots вместо этого сканирует отрезок.
            var = sp.Symbol(spec.get('var', 'x'))
            expression = sp.sympify(spec['expression'])
            low, high = (sp.sympify(v) for v in spec['domain'])
            claimed = parse_many(raw)
            ok, message = _capture(kit.verify_roots, 'Ответ', claimed,
                                   expression, (low, high), var=var,
                                   deg=spec.get('deg', False))
            if ok:
                # Скан ищет смену знака и потому не видит корень ровно
                # на конце отрезка: сменить знак ему там негде. Досчитываем
                # точно — иначе пропущенный 2π проходит как верный ответ.
                truth = sp.solveset(expression, var, sp.Interval(low, high))
                if isinstance(truth, sp.FiniteSet) and len(truth) != len(claimed):
                    return False, (f'{kit.NO} корни верны, но найдено не всё — '
                                   f'на отрезке их {len(truth)}, а у вас '
                                   f'{len(claimed)}: посмотрите на концы')
            return ok, message

        if kind == 'solution_set':
            var = sp.Symbol(spec.get('var', 'x'))
            return _capture(kit.verify_solution_set, 'Ответ',
                            parse_solution_set(raw, var),
                            sp.sympify(spec['inequality']), var=var,
                            domain=(sp.sympify(spec['domain'])
                                    if spec.get('domain') else None))

        if kind == 'series':
            return _capture(kit.check_series, 'Ответ', parse_one(raw),
                            spec['digest'], var=sp.Symbol(spec.get('var', 'x')))

        if kind == 'complex':
            return _capture(kit.check_complex, 'Ответ', parse_one(raw),
                            spec['digest'])

        if kind == 'complex_set':
            return _capture(kit.check_complex_set, 'Ответ', parse_many(raw),
                            spec['digest'])

        if kind == 'ode':
            return _capture(kit.verify_ode, 'Ответ', parse_one(raw),
                            sp.sympify(spec['rhs']),
                            ic=tuple(sp.sympify(v) for v in spec['ic'])
                            if spec.get('ic') else None,
                            var=sp.Symbol(spec.get('var', 'x')),
                            dep=sp.Symbol(spec.get('dep', 'y')))

        if kind == 'identity':
            return _capture(kit.verify_identity, 'Ответ', parse_one(raw),
                            sp.sympify(spec['want']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            samples=tuple(spec['samples'])
                            if spec.get('samples') else
                            (0.3, 0.7, 1.1, 1.9, 2.6, 3.4, 4.1, 5.2))

        if kind == 'factored':
            return _capture(kit.verify_factored, 'Ответ', parse_one(raw),
                            sp.sympify(spec['original']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            max_deg=spec.get('max_deg', 1))

        if kind == 'apart':
            return _capture(kit.check_apart, 'Ответ', parse_one(raw),
                            sp.sympify(spec['original']),
                            var=sp.Symbol(spec.get('var', 'x')))

        if kind == 'count':
            value = parse_one(raw)
            ok = sp.simplify(value - sp.Integer(spec['value'])) == 0
            return ok, (f'{kit.OK} Ответ: {value}' if ok
                        else f'{kit.NO} Ответ: {value} — не сходится')

    except BadInput as exc:
        return False, f'{kit.NO} {exc}'

    raise ValueError(f'неизвестный вид проверки: {kind!r}')


def show_answer(value, sf=3, var='x'):
    """Читаемая запись эталона — её показывают уже после попытки."""
    if isinstance(value, (list, tuple)):
        return ', '.join(show_answer(v, sf, var) for v in value) or 'нет корней'
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
    if isinstance(value, sp.Set):
        return show_set(value, var)
    expr = sp.sympify(value)
    if isinstance(expr, sp.Eq):
        return f'{sp.sstr(expr.lhs)} = {sp.sstr(expr.rhs)}'
    if expr.atoms(sp.Float):
        return f'{float(expr):.{sf}g}'
    return sp.sstr(expr)


def _interval_text(interval, var):
    """Один промежуток словами экзамена: -2 < x <= 3, x > 5."""
    left, right = interval.start, interval.end
    left_sign = '<' if interval.left_open else '<='
    right_sign = '<' if interval.right_open else '<='
    if left == -sp.oo and right == sp.oo:
        return 'любое ' + var
    if left == -sp.oo:
        return f'{var} {right_sign} {sp.sstr(right)}'
    if right == sp.oo:
        return f'{var} {">" if interval.left_open else ">="} {sp.sstr(left)}'
    return (f'{sp.sstr(left)} {left_sign} {var} {right_sign} {sp.sstr(right)}')


def show_set(value, var='x'):
    """Множество решений так, как его пишут в ответе, а не как печатает sympy."""
    if value is sp.EmptySet or value == sp.EmptySet:
        return 'нет решений'
    if value == sp.S.Reals:
        return f'любое {var}'
    pieces = value.args if isinstance(value, sp.Union) else [value]
    out = []
    for piece in pieces:
        if isinstance(piece, sp.Interval):
            out.append(_interval_text(piece, var))
        elif isinstance(piece, sp.FiniteSet):
            out += [f'{var} = {sp.sstr(point)}' for point in piece.args]
        else:
            out.append(sp.sstr(piece))
    return ' or '.join(out)
