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


def parse_one(raw, extra=None):
    """Одно выражение.

    extra — имена, которых в sympy нет: у формулы понижения ответ пишется
    через функцию-заглушку J(m), и без неё запись не разберётся.
    """
    text = _clean(raw)
    if not text:
        raise BadInput('пусто')
    try:
        return parse_expr(text, local_dict=extra or {},
                          transformations=TRANSFORMS, evaluate=True)
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

        if kind == 'inverse':
            var = sp.Symbol(spec.get('var', 'x'))
            return _capture(kit.verify_inverse, 'Ответ', parse_one(raw),
                            sp.sympify(spec['f']), var=var,
                            domain=(sp.sympify(spec['domain'])
                                    if spec.get('domain') else None))

        if kind == 'domain':
            var = sp.Symbol(spec.get('var', 'x'))
            return _capture(kit.check_domain, 'Ответ',
                            parse_solution_set(raw, var), spec['digest'],
                            var=var)

        if kind == 'model':
            data = [(sp.sympify(point),
                     None if value is None else sp.sympify(value))
                    for point, value in spec['data']]
            return _capture(kit.verify_model, 'Ответ', parse_one(raw), data,
                            var=sp.Symbol(spec.get('var', 't')),
                            sf=spec.get('sf', 6))

        if kind == 'in_terms_of':
            subs = {sp.Symbol(name): sp.sympify(value)
                    for name, value in spec['subs'].items()}
            return _capture(kit.verify_in_terms_of, 'Ответ', parse_one(raw),
                            sp.sympify(spec['want']), subs)

        if kind == 'limit':
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            return _capture(kit.verify_limit, 'Ответ', parse_one(raw),
                            sp.sympify(spec['expr']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            point=sp.sympify(spec['point']),
                            side=spec.get('side'),
                            params=params or None,
                            tol=spec.get('tol', 1e-6))

        if kind == 'indeterminate':
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            return _capture(kit.verify_indeterminate, 'Ответ', raw.strip(),
                            sp.sympify(spec['num']), sp.sympify(spec['den']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            point=sp.sympify(spec['point']),
                            side=spec.get('side'),
                            params=params or None)

        if kind == 'maclaurin':
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            return _capture(kit.verify_maclaurin, 'Ответ', parse_one(raw),
                            sp.sympify(spec['f']),
                            order=spec.get('order'), terms=spec.get('terms'),
                            var=sp.Symbol(spec.get('var', 'x')),
                            params=params or None)

        if kind == 'series_solution':
            return _capture(kit.verify_series_solution, 'Ответ',
                            parse_one(raw), sp.sympify(spec['rhs']),
                            sp.sympify(spec['ic']), spec['order'],
                            var=sp.Symbol(spec.get('var', 'x')),
                            dep=sp.Symbol(spec.get('dep', 'y')))

        if kind == 'terms':
            return _capture(kit.verify_terms, 'Ответ', parse_one(raw),
                            sp.sympify(spec['term']),
                            sp.sympify(spec['bound']),
                            var=sp.Symbol(spec.get('var', 'k')),
                            strict=spec.get('strict', True))

        if kind == 'derivative':
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            return _capture(kit.verify_derivative, 'Ответ', parse_one(raw),
                            sp.sympify(spec['f']),
                            var=sp.Symbol(spec.get('var', 'x')),
                            order=spec.get('order', 1),
                            params=params or None)

        if kind == 'shape':
            return _shape_kind(spec, raw)

        if kind == 'data':                      # данные и регрессия, D7
            return _data_kind(spec, raw)

        if kind == 'rates':                     # скорости и наилучшее, E9
            return _rates_kind(spec, raw)

        if kind in ('tangent', 'normal', 'slope', 'where', 'second',
                    'constant'):
            var, dep = sp.Symbol(spec['var']), sp.Symbol(spec['dep'])
            shape = sp.sympify(spec['rule'])
            here = kit.curve(shape, var=var, dep=dep)
            spot = sp.sympify(spec['at']) if spec.get('at') else None
            domain = ([sp.sympify(v) for v in spec['domain']]
                      if spec.get('domain') else None)

            if kind in ('tangent', 'normal'):
                check = kit.verify_tangent if kind == 'tangent' else kit.verify_normal
                return _capture(check, 'Ответ', parse_one(raw), here, spot)

            if kind == 'slope':
                return _capture(kit.verify_slope, 'Ответ', parse_one(raw),
                                here, at=spot, domain=domain)

            if kind == 'second':
                return _capture(kit.verify_second, 'Ответ', parse_one(raw),
                                here, spot)

            if kind == 'where':
                values = parse_many(raw)
                got = values if len(values) > 1 else values[0]
                return _capture(kit.verify_where, 'Ответ', got, here,
                                sp.sympify(spec['slope']), domain,
                                coordinates=spec.get('coordinates', False))

            letter = sp.Symbol(spec['letter'])
            build = lambda value: kit.curve(shape.subs(letter, value),
                                            var=var, dep=dep)
            values = parse_many(raw)
            return _capture(kit.verify_constant, 'Ответ',
                            values if len(values) > 1 else values[0],
                            build, spot, sp.sympify(spec['slope']),
                            [sp.sympify(v) for v in spec['window']])

        if kind in ('antiderivative', 'integral', 'accumulated',
                    'transformed', 'reduction', 'termwise'):
            var = sp.Symbol(spec.get('var', 'x'))
            shape = sp.sympify(spec['f']) if 'f' in spec else None
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            domain = ([sp.sympify(v) for v in spec['domain']]
                      if spec.get('domain') else None)

            if kind == 'antiderivative':
                through = ([sp.sympify(v) for v in spec['through']]
                           if spec.get('through') else None)
                return _capture(kit.verify_antiderivative, 'Ответ',
                                parse_one(raw), shape, var=var, domain=domain,
                                params=params or None, through=through)

            if kind == 'integral':
                # Обратный ход: значение интеграла известно, а ответом
                # служит верхний предел — он и уходит в b.
                if spec.get('value'):
                    return _capture(kit.verify_integral, 'Ответ',
                                    sp.sympify(spec['value']), shape,
                                    sp.sympify(spec['a']), parse_one(raw),
                                    var=var, params=params or None,
                                    tol=spec.get('tol'))
                return _capture(kit.verify_integral, 'Ответ', parse_one(raw),
                                shape, sp.sympify(spec['a']),
                                sp.sympify(spec['b']), var=var,
                                params=params or None, tol=spec.get('tol'))

            if kind == 'accumulated':
                return _capture(kit.verify_accumulated, 'Ответ',
                                parse_one(raw), shape,
                                sp.sympify(spec['lower']), var=var,
                                upper=sp.sympify(spec['upper']),
                                params=params or None, domain=domain)

            if kind == 'transformed':
                return _capture(kit.verify_transformed, 'Ответ',
                                parse_one(raw), shape,
                                sp.sympify(spec['sub']), var=var,
                                new=sp.Symbol(spec.get('new', 'u')),
                                domain=domain)

            if kind == 'termwise':
                return _capture(kit.verify_termwise, 'Ответ', parse_one(raw),
                                shape, spec['upto'], var=var)

            # reduction: формула записывается через функцию-заглушку J(m),
            # и разбирать ответ надо с ней в пространстве имён.
            of = sp.Function(spec.get('of', 'J'))
            index = sp.Symbol(spec['index'])
            got = parse_one(raw, extra={spec.get('of', 'J'): of})
            return _capture(kit.verify_reduction, 'Ответ', got,
                            sp.sympify(spec['term']), index, of, var=var,
                            span=tuple(spec['span']),
                            values=tuple(spec['values']))

        # E6: измеренное и его измерение. Проверки не берут производных;
        # они меряют область, тело, поверхность или путь заново.
        if kind in ('region', 'solid', 'surface', 'travelled', 'position',
                    'amount'):
            var = sp.Symbol(spec.get('var', 'x'))
            params = {sp.Symbol(name): [sp.sympify(v) for v in values]
                      for name, values in (spec.get('params') or {}).items()}
            digits = spec.get('digits', 3)
            edge = lambda name: (sp.sympify(spec[name]) if spec.get(name)
                                 else None)

            if kind == 'region':
                extra = ({'window': tuple(sp.sympify(v)
                                          for v in spec['window'])}
                         if spec.get('window') else {})
                return _capture(kit.verify_region, 'Ответ', parse_one(raw),
                                sp.sympify(spec['top']),
                                sp.sympify(spec['bottom']),
                                edge('a'), edge('b'), var=var,
                                params=params or None, digits=digits, **extra)

            if kind == 'solid':
                # Обратный ход: объём известен, ответом служит предел.
                if spec.get('value'):
                    return _capture(kit.verify_solid, 'Ответ',
                                    sp.sympify(spec['value']),
                                    sp.sympify(spec['outer']),
                                    sp.sympify(spec['a']), parse_one(raw),
                                    inner=sp.sympify(spec['inner']), var=var,
                                    axis=spec.get('axis', 'x'),
                                    params=params or None, digits=digits)
                return _capture(kit.verify_solid, 'Ответ', parse_one(raw),
                                sp.sympify(spec['outer']),
                                sp.sympify(spec['a']), sp.sympify(spec['b']),
                                inner=sp.sympify(spec['inner']), var=var,
                                axis=spec.get('axis', 'x'),
                                params=params or None, digits=digits)

            if kind == 'surface':
                return _capture(kit.verify_surface, 'Ответ', parse_one(raw),
                                sp.sympify(spec['curve']),
                                sp.sympify(spec['a']), sp.sympify(spec['b']),
                                var=var, params=params or None, digits=digits)

            if kind == 'travelled':
                return _capture(kit.verify_travelled, 'Ответ', parse_one(raw),
                                sp.sympify(spec['v']), sp.sympify(spec['a']),
                                sp.sympify(spec['b']), var=var,
                                params=params or None, digits=digits)

            if kind == 'position':
                return _capture(kit.verify_position, 'Ответ', parse_one(raw),
                                sp.sympify(spec['v']), sp.sympify(spec['a']),
                                sp.sympify(spec['b']), var=var,
                                start=sp.sympify(spec['start']),
                                params=params or None, digits=digits)

            at = (tuple(sp.sympify(v) for v in spec['at'])
                  if spec.get('at') else None)
            return _capture(kit.verify_amount, 'Ответ', parse_one(raw),
                            sp.sympify(spec['rate']), sp.sympify(spec['a']),
                            edge('b'), var=var,
                            start=sp.sympify(spec['start']), at=at,
                            params=params or None, digits=digits)

        if kind == 'constants':
            unknowns = [sp.Symbol(name) for name in spec['unknowns']]
            conditions = [(what, sp.sympify(cond))
                          for what, cond in spec['conditions']]
            values = parse_many(raw) if len(unknowns) > 1 else [parse_one(raw)]
            return _capture(kit.verify_constants, 'Ответ', values,
                            unknowns, conditions)

        if kind == 'space':
            space = {name: sp.sympify(w) for name, w in spec['space']}
            given = spec.get('given')
            return _capture(kit.verify_probability, 'Ответ', parse_one(raw),
                            space, set(spec['find']),
                            given=set(given) if given else None)

        if kind == 'independence':
            space = {name: sp.sympify(w) for name, w in spec['space']}
            first, second = set(spec['a']), set(spec['b'])
            whole = sum(space.values())
            product = (sum(space[n] for n in first)
                       * sum(space[n] for n in second) / whole**2)
            joint = sum(space[n] for n in first & second) / whole
            values = parse_many(raw)
            if len(values) != 2:
                return False, (f'{kit.NO} нужны два числа: произведение '
                               f'P(A)·P(B) и вероятность P(A∩B)')
            if sp.simplify(values[0] - product) != 0:
                return False, (f'{kit.NO} первое число — не произведение '
                               f'P(A)·P(B)')
            if sp.simplify(values[1] - joint) != 0:
                return False, (f'{kit.NO} второе число — не вероятность '
                               f'пересечения P(A∩B)')
            verdict = 'независимы' if product == joint else 'зависимы'
            return True, f'{kit.OK} числа верны, и они говорят: {verdict}'

        if kind in ('binomial', 'moment', 'parameter', 'trials'):
            return _binomial_kind(kind, spec, raw)

        if kind == 'table':
            return _table_kind(spec, raw)

        if kind == 'bell':                      # нормальное распределение, D5
            return _normal_kind(spec, raw)

        if kind == 'density':                   # плотность формулой, D6
            return _density_kind(spec, raw)

        if kind == 'vector':                    # векторы и прямые C5, плоскости C6
            return _vector_kind(spec, raw)

        if kind == 'count':
            value = parse_one(raw)
            ok = sp.simplify(value - sp.Integer(spec['value'])) == 0
            return ok, (f'{kit.OK} Ответ: {value}' if ok
                        else f'{kit.NO} Ответ: {value} — не сходится')

    except BadInput as exc:
        return False, f'{kit.NO} {exc}'

    raise ValueError(f'неизвестный вид проверки: {kind!r}')


_COMPARE = {'==': lambda X, k: X == k, '<': lambda X, k: X < k,
            '<=': lambda X, k: X <= k, '>': lambda X, k: X > k,
            '>=': lambda X, k: X >= k}
_HOLDS = {'>': lambda v, t: v > t, '>=': lambda v, t: v >= t,
          '<': lambda v, t: v < t, '<=': lambda v, t: v <= t}


def _draw_model(packed):
    """Bin(...) из описания задания; p бывает событием над другой моделью."""
    n, p = packed
    if isinstance(p, list) and p and p[0] == 'inner':
        inner = kit.Bin(p[1][0], sp.sympify(p[1][1]), 'A')
        return kit.Bin(n, kit.P(_draw_event(p[2], {'A': inner})))
    return kit.Bin(n, sp.sympify(p))


def _draw_event(tree, variables):
    """Событие kit из дерева сравнений."""
    head = tree[0]
    if head == 'leaf':
        return _COMPARE[tree[2]](variables[tree[1]], tree[3])
    if head == 'not':
        return ~_draw_event(tree[1], variables)
    left, right = _draw_event(tree[1], variables), _draw_event(tree[2], variables)
    return {'and': left & right, 'or': left | right, 'xor': left ^ right}[head]


def _binomial_kind(kind, spec, raw):
    """Биномиальное распределение, D3: те же проверки, что в ноутбуке."""
    if kind == 'binomial':
        variables = {}
        for name, packed in spec['model'].items():
            variables[name] = _draw_model(packed)
            variables[name].name = name
        given = spec.get('given')
        find = kit.P(_draw_event(spec['event'], variables),
                     given=_draw_event(given, variables) if given else None)
        return _capture(kit.verify_binomial, 'Ответ', parse_one(raw), find)
    if kind == 'moment':
        X = kit.Bin(spec['n'], sp.sympify(spec['p']))
        linear = sp.sympify(spec['a']) * X + sp.sympify(spec['b'])
        what = kit.Expect(linear) if spec['what'] == 'mean' else kit.Var(linear)
        return _capture(kit.verify_moment, 'Ответ', parse_one(raw), what)
    if kind == 'parameter':
        p = sp.Symbol('p')
        condition = sp.Eq(kit.Var(kit.Bin(spec['n'], p)),
                          sp.sympify(spec['variance']))
        return _capture(kit.verify_parameter, 'Ответ', parse_many(raw),
                        condition, p)
    # trials
    p, rel, k = sp.sympify(spec['p']), spec['rel'], spec['k']
    family = lambda n: kit.P(_COMPARE[rel](kit.Bin(n, p), k))
    if spec.get('holds'):
        sign, level = spec['holds'][0], sp.sympify(spec['holds'][1])
        return _capture(kit.verify_trials, 'Ответ', parse_one(raw), family,
                        holds=lambda value: _HOLDS[sign](value, level))
    return _capture(kit.verify_trials, 'Ответ', parse_one(raw), family,
                    near=float(sp.sympify(spec['near'])))


def _table_letters(spec):
    """Буквы задания с их допущениями: частота целая и не отрицательная."""
    return {name: sp.Symbol(name, **flags) for name, flags in spec.get('letters', {}).items()}


def _table_build(spec):
    """Величины задания и условия вопроса — те же объекты, что в ноутбуке D4."""
    letters = _table_letters(spec)

    def read(text):
        return sp.sympify(text, locals=letters)

    variables = {}
    for name, packed in spec['tables'].items():
        table = {read(value): read(chance) for value, chance in packed['cells']}
        maker = kit.Freq if packed['counts'] else kit.Dist
        variables[name] = maker(table, name)
    if spec.get('geo'):
        variables['X'] = kit.Geo(read(spec['geo']), 'X')
    conditions = []
    for kind, name, value in spec.get('conditions', []):
        X = variables[name]
        left = {'mean': lambda: kit.Expect(X), 'var': lambda: kit.Var(X),
                'size': lambda: X.size}[kind]()
        conditions.append(sp.Eq(left, read(value)))
    return letters, variables, conditions, read


def _table_kind(spec, raw):
    """Дискретная величина по таблице, D4: те же проверки, что в ноутбуке."""
    letters, variables, conditions, read = _table_build(spec)
    what = spec['what']
    tables = list(variables.values())
    if what == 'letters':
        unknowns = [letters.get(name, sp.Symbol(name)) for name in spec['unknowns']]
        values = parse_many(raw) if len(unknowns) > 1 else parse_one(raw)
        return _capture(kit.verify_letters, 'Ответ', values, unknowns, tables,
                        conditions, whole=spec.get('whole', False))
    if what == 'range':
        letter = letters.get(spec['var'], sp.Symbol(spec['var']))
        return _capture(kit.verify_table_range, 'Ответ',
                        parse_solution_set(raw, letter), letter, tables)
    X = variables[spec['target']]
    free = kit._letters_in(tables, [])
    given = conditions if (conditions or free) else None
    if what in ('mean', 'var'):
        linear = read(spec['a']) * X + read(spec['b'])
        find = kit.Expect(linear) if what == 'mean' else kit.Var(linear)
        return _capture(kit.verify_moment, 'Ответ', parse_one(raw), find,
                        given=given, var=free or None, tables=tables)
    if what == 'mode':
        return _capture(kit.verify_mode, 'Ответ', parse_one(raw), X,
                        given=given, var=free or None)
    # pgf
    return _capture(kit.verify_pgf, 'Ответ', parse_one(raw), X, sp.Symbol('t'),
                    given=given, unknowns=free or None)


def _normal_kind(spec, raw):
    """Нормальная величина, D5: те же проверки, что в ноутбуке."""
    def read(text):
        return sp.sympify(text)

    rules = {name: {float(k): float(read(v)) for k, v in rule}
             for name, rule in spec.get('rules', {}).items()}
    models = {name: kit.Normal(read(m), read(v), name, rule=rules.get(name))
              for name, (m, v) in spec['models'].items()}

    def event(packed):
        kind, name, *bounds = packed
        X, bounds = models[name], [read(b) for b in bounds]
        if kind == '<':
            return X < bounds[0]
        if kind == '>':
            return X > bounds[0]
        return (X > bounds[0]) & (X < bounds[1])

    conditions = [sp.Eq(kit.P(event(e)), read(value)) for e, value in spec['conditions']]
    free = sp.Symbol(spec['free']) if spec.get('free') else None
    variables = list(models.values())
    if spec['what'] == 'letters':
        unknowns = [sp.Symbol(name) for name in spec['unknowns']]
        values = parse_many(raw) if len(unknowns) > 1 else parse_one(raw)
        return _capture(kit.verify_letters, 'Ответ', values,
                        unknowns if len(unknowns) > 1 else unknowns[0], variables,
                        conditions, sf=spec.get('sf'), free=free)
    given = event(spec['given']) if spec.get('given') else None
    find = kit.P(event(spec['find']), given=given)
    letters = kit._letters_in(variables, conditions)
    letters = [u for u in letters if u != free]
    return _capture(kit.verify_chance, 'Ответ', parse_one(raw), find,
                    given=conditions or None, var=letters or None, sf=spec.get('sf'),
                    percent=spec.get('percent', False), free=free)


def _density_kind(spec, raw):
    """Величина с плотностью, D6: те же проверки, что в ноутбуке."""
    var = sp.Symbol(spec['var'])
    X = kit.Density({(sp.sympify(lo), sp.sympify(hi)): sp.sympify(f)
                     for lo, hi, f in spec['pieces']}, spec.get('name', 'X'), var=var)

    def event(packed):
        kind, _, *bounds = packed
        bounds = [sp.sympify(b) for b in bounds]
        if kind == '<':
            return X < bounds[0]
        if kind == '>':
            return X > bounds[0]
        return (X > bounds[0]) & (X < bounds[1])

    conditions = [sp.Eq(kit.P(event(e)), sp.sympify(value)) for e, value in spec['conditions']]
    letters = list(X.letters)
    exact = spec.get('exact', False)
    if spec['what'] == 'letters':
        unknowns = [sp.sympify(u) for u in spec['unknowns']]
        values = parse_many(raw) if len(unknowns) > 1 else parse_one(raw)
        return _capture(kit.verify_letters, 'Ответ', values,
                        unknowns if len(unknowns) > 1 else unknowns[0], [X],
                        conditions, exact=exact)
    if spec['what'] == 'mode':
        return _capture(kit.verify_mode, 'Ответ', parse_one(raw), X,
                        given=[] if letters else None, var=letters or None)
    if spec['what'] in ('mean', 'var'):
        what = kit.Expect(X) if spec['what'] == 'mean' else kit.Var(X)
        return _capture(kit.verify_moment, 'Ответ', parse_one(raw), what,
                        given=[] if letters else None, var=letters or None, exact=exact)
    given = event(spec['given']) if spec.get('given') else None
    find = kit.P(event(spec['find']), given=given)
    return _capture(kit.verify_chance, 'Ответ', parse_one(raw), find,
                    given=[] if letters else None, var=letters or None)


_RELATION_RU = {'параллельны': 'parallel', 'параллельные': 'parallel',
                'пересекаются': 'intersecting', 'пересекающиеся': 'intersecting',
                'скрещиваются': 'skew', 'скрещивающиеся': 'skew',
                'совпадают': 'same'}
LINE_TEXT = re.compile(r'^\s*(?:[a-zA-Z]\s*=)?\s*\(([^()]*)\)\s*\+\s*([^\s(*]+)\s*\*?\s*\(([^()]*)\)\s*$')


def parse_line(raw):
    """Прямая, как её пишут: «r = (1, -2, 0) + λ(2, 3, 1)»."""
    text = _clean(raw).replace('λ', 'lam').replace('μ', 'mu').replace('τ', 'tau')
    found = LINE_TEXT.match(text)
    if not found:
        raise BadInput('прямую пишут так: r = (x, y, z) + λ(a, b, c)')
    point = [parse_one(v) for v in found.group(1).split(',')]
    direction = [parse_one(v) for v in found.group(3).split(',')]
    letter = {'lam': kit.lam, 'mu': kit.mu}.get(found.group(2)) or sp.Symbol(found.group(2))
    return kit.vec(*point) + letter * kit.vec(*direction)


def _vector_kind(spec, raw):
    """Векторы и прямые, C5: те же проверки, что в ноутбуке."""
    parts = {name: kit.vec(*[sp.sympify(v) for v in values])
             for name, values in spec['parts'].items()}
    what = spec['what']

    def point():
        values = parse_many(raw)
        return tuple(values)

    def two_lines():
        return (kit.line(parts['p1'], parts['d1']), kit.line(parts['p2'], parts['d2']))

    if what in ('midpoint', 'vertex'):
        unknown = kit.unknown('X', len(parts['A']))
        fact = (kit.midpoint(unknown, parts['A'], parts['B']) if what == 'midpoint'
                else kit.parallelogram(parts['A'], parts['B'], parts['C'], unknown))
        return _capture(kit.verify_find, 'Ответ', point(), unknown, [fact])
    if what == 'distance':
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), kit.distance(parts['A'], parts['B']))
    if what == 'dot':
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), kit.dot(parts['u'], parts['v']))
    if what == 'perpendicular':
        letter = sp.Symbol(spec['letter'])
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), letter,
                        [kit.perpendicular(parts['u'], parts['v'])])
    if what == 'angle':
        return _capture(kit.verify_angle, 'Ответ', parse_one(raw), parts['u'], parts['v'], deg=True)
    if what == 'vertex_angle':
        return _capture(kit.verify_angle, 'Ответ', parse_one(raw), parts['P'], parts['V'], parts['Q'], deg=True)
    if what == 'line':
        return _capture(kit.verify_line, 'Ответ', parse_line(raw), kit.line(parts['point'], parts['direction']))
    if what == 'line_angle':
        return _capture(kit.verify_angle, 'Ответ', parse_one(raw), *two_lines(), deg=True)
    if what == 'meet':
        return _capture(kit.verify_meet, 'Ответ', point(), *two_lines())
    if what == 'relation':
        word = str(raw).strip().lower().rstrip('.')
        return _capture(kit.verify_relation, 'Ответ', _RELATION_RU.get(word, word), *two_lines())
    if what == 'speed':
        return _capture(kit.verify_speed, 'Ответ', parse_one(raw),
                        parts['r0'] + kit.t * parts['v'])
    if what == 'bearing':
        return _capture(kit.verify_bearing, 'Ответ', str(raw).strip(), parts['v'])
    return _plane_kind(spec, parts, raw, point)


_NONE_RU = {'нет', 'нет общих точек', 'нет общей точки', 'нет решений', 'пусто', '∅'}


def _plane_kind(spec, parts, raw, point):
    """Плоскости, C6: плоскость и система — множества, проверки из ноутбука."""
    what = spec['what']

    def surface(normal, constant):
        return kit.plane(kit.Eq(kit.dot(kit.vec(kit.x, kit.y, kit.z), parts[normal]), parts[constant][0]))

    def answer_set():
        text = _clean(raw).lower().strip('.')
        if text in _NONE_RU:
            return 'none'
        if '+' in text and ('λ' in raw or 'lam' in text or 'mu' in text or 'μ' in raw or 't(' in text):
            return parse_line(raw)
        values = point()
        return values[0] if len(values) == 1 else values

    if what == 'plane':
        return _capture(kit.verify_plane, 'Ответ', parse_equation(raw), kit.plane(parts['point'], parts['normal']))
    if what == 'perpendicular_planes':
        letter = sp.Symbol(spec['letter'])
        origin = kit.vec(0, 0, 0)
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), letter,
                        [kit.perpendicular(kit.plane(origin, parts['n1']), kit.plane(origin, parts['n2']))])
    if what == 'three_points':
        return _capture(kit.verify_plane, 'Ответ', parse_equation(raw), kit.plane(parts['A'], parts['B'], parts['C']))
    if what == 'line_plane':
        return _capture(kit.verify_intersection, 'Ответ', answer_set(), kit.line(parts['p'], parts['d']),
                        surface('n', 'c'))
    if what == 'two_planes':
        return _capture(kit.verify_intersection, 'Ответ', answer_set(), surface('n1', 'c1'), surface('n2', 'c2'))
    if what == 'three_planes':
        return _capture(kit.verify_intersection, 'Ответ', answer_set(), surface('n1', 'c1'), surface('n2', 'c2'),
                        surface('n3', 'c3'))
    if what == 'no_unique':
        letter = sp.Symbol(spec['letter'])
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), letter,
                        [kit.no_unique_meet(surface('n1', 'c1'), surface('n2', 'c2'), surface('n3', 'c3'))])
    if what == 'foot':
        where = kit.unknown('F', 3)
        wall = surface('n', 'c')
        return _capture(kit.verify_find, 'Ответ', point(), where,
                        [kit.on(where, wall), kit.perpendicular(where - parts['q'], wall)])
    if what == 'plane_distance':
        return _capture(kit.verify_distance, 'Ответ', parse_one(raw), parts['q'], surface('n', 'c'))
    if what == 'reflection':
        image = kit.unknown('Q', 3)
        return _capture(kit.verify_find, 'Ответ', point(), image, [kit.reflection(image, parts['q'], surface('n', 'c'))])
    return _space_kind(spec, parts, raw, point)


def _space_kind(spec, parts, raw, point):
    """Измерения, C7: величину меряет фигура вопроса, проверки из ноутбука."""
    what = spec['what']

    def surface(normal):
        return kit.plane(kit.vec(0, 0, 0), parts[normal])

    if what == 'cross':
        return _capture(kit.verify_cross, 'Ответ', point(), parts['u'], parts['v'])
    if what == 'area_triangle':
        return _capture(kit.verify_measure, 'Ответ', parse_one(raw), 'triangle',
                        parts['A'], parts['B'], parts['C'], exact=True)
    if what == 'area_parallelogram':
        return _capture(kit.verify_measure, 'Ответ', parse_one(raw), 'parallelogram',
                        parts['A'], parts['B'], parts['C'], parts['D'], exact=True)
    if what == 'volume':
        return _capture(kit.verify_measure, 'Ответ', parse_one(raw), 'pyramid',
                        parts['S'], parts['A'], parts['B'], parts['C'])
    if what == 'lagrange':
        size = kit.unknown('L')
        product, known = parts['dot'][0], parts['known'][0]
        if spec['letter'] == 'u':
            across = parts['cross'][0]
            rule = kit.Eq(product ** 2 + across ** 2, size ** 2 * known ** 2)
        else:
            rule = kit.Eq(product ** 2 + size ** 2, known ** 2 * parts['other'][0] ** 2)
        return _capture(kit.verify_find, 'Ответ', parse_one(raw), size, [rule, size > 0])
    if what == 'plane_angle':
        return _capture(kit.verify_angle, 'Ответ', parse_one(raw), surface('n1'), surface('n2'),
                        cosine=True, exact=True)
    if what == 'line_plane_angle':
        return _capture(kit.verify_angle, 'Ответ', parse_one(raw),
                        kit.line(kit.vec(0, 0, 0), parts['d']), surface('n'), deg=True)
    if what == 'sphere_arc':
        return _capture(kit.verify_arc, 'Ответ', parse_one(raw), parts['radius'][0],
                        parts['u'], parts['v'])
    if what == 'closest':
        where = kit.unknown('N', 3)
        track = kit.line(parts['p'], parts['d'])
        return _capture(kit.verify_find, 'Ответ', point(), where,
                        [kit.on(where, track), kit.perpendicular(where - parts['q'], track)])
    if what == 'line_distance':
        track = kit.line(parts['p'], parts['d'])
        other = kit.line(parts['p2'], parts['d2']) if 'p2' in parts else parts['q']
        return _capture(kit.verify_distance, 'Ответ', parse_one(raw), track, other, exact=True)
    raise ValueError(f'неизвестный вопрос о векторах: {what!r}')


def _data_kind(spec, raw):
    """Данные, D7: прямую находит поиск по дну суммы квадратов."""
    what = spec['what']

    def numbers(name):
        return [sp.sympify(v) for v in spec[name]]

    if what == 'missing':
        values = parse_many(raw)
        got = values if len(values) > 1 else values[0]
        given = {key: sp.sympify(v) for key, v in spec['given'].items()}
        return _capture(kit.verify_missing, 'Ответ', got, kit.Sample(numbers('items')),
                        **given)
    if what == 'fence':
        return _capture(kit.verify_fence, 'Ответ', parse_one(raw), kit.Box(*numbers('box')))
    if what == 'centre':
        lines = [sp.Eq(sp.Symbol(lhs), sp.sympify(k) * sp.Symbol('x' if lhs == 'y' else 'y')
                       + sp.sympify(c)) for lhs, k, c in spec['lines']]
        values = parse_many(raw)
        return _capture(kit.verify_centre, 'Ответ', tuple(values), lines,
                        order=(sp.Symbol('x'), sp.Symbol('y')))
    pairs = kit.Pairs(numbers('xs'), numbers('ys'))
    if what == 'strength':
        return _capture(kit.verify_strength, 'Ответ', parse_one(raw), pairs)
    if what == 'fit':
        values = parse_many(raw)
        return _capture(kit.verify_fit, 'Ответ', tuple(values) if len(values) == 2
                        else values[0], pairs)
    if what == 'estimate':
        return _capture(kit.verify_estimate, 'Ответ', parse_one(raw), pairs,
                        sp.sympify(spec['at']), of=spec.get('of'))
    scale, shift = sp.sympify(spec['scale']), sp.sympify(spec['shift'])
    return _capture(kit.verify_effect, 'Ответ', raw.strip(), pairs,
                    lambda value: scale * value + shift)


def _rates_kind(spec, raw):
    """Скорости и наилучшее, E9: скорость меряют сдвигом, наилучшее — просмотром."""
    what = spec['what']
    t = sp.Symbol('t')
    if what == 'rate':
        return _capture(kit.verify_rate, 'Ответ', parse_one(raw), sp.sympify(spec['f']),
                        sp.sympify(spec['at']))
    if what in ('when', 'extreme'):
        span = tuple(sp.sympify(v) for v in spec['span'])
        path = kit.particle(v=sp.sympify(spec['v']), span=span)
        if what == 'when':
            return _capture(kit.verify_when, 'Ответ', parse_one(raw), path, spec['event'],
                            spec.get('which', 1))
        return _capture(kit.verify_extreme, 'Ответ', parse_one(raw), path, spec['quantity'],
                        spec.get('sense', 'max'))
    if what == 'related':
        rates = {kit.dt(sp.Symbol(name)): sp.sympify(value)
                 for name, value in spec['rates'].items()}
        where = {sp.Symbol(name): tuple(sp.sympify(v) for v in ends)
                 for name, ends in (spec.get('where') or {}).items()}
        return _capture(kit.verify_related, 'Ответ', parse_one(raw),
                        [sp.sympify(e) for e in spec['relations']],
                        [sp.sympify(e) for e in spec['at']], rates,
                        kit.dt(sp.Symbol(spec['want'])), where=where or None,
                        size=spec.get('size', False))
    var = sp.Symbol(spec.get('var', 'x'))
    lo, hi, open_lo, open_hi = spec['domain']
    lo, hi = sp.sympify(lo), sp.sympify(hi)
    domain = sp.Interval(lo, hi, open_lo, open_hi)
    body = sp.sympify(spec['f'])
    if spec.get('rate'):
        body = kit.rate_of(body, var)
    report = spec.get('report', 'value')
    if report not in ('value', 'place'):
        report = sp.sympify(report)
    return _capture(kit.verify_best, 'Ответ', parse_one(raw), body, domain,
                    spec.get('sense', 'max'), var=var, report=report,
                    integer=spec.get('integer', False), exact=spec.get('exact', False))


def _shape_kind(spec, raw):
    """Форма графика, E8: вид точки решают соседи, перегиб — хорда."""
    what = spec['what']
    var, dep = sp.Symbol(spec.get('curve', spec['var'])), sp.Symbol(spec['dep'])
    shape = sp.sympify(spec['rule'])
    here = kit.curve(shape, var=var, dep=dep)
    domain = ([sp.sympify(v) for v in spec['domain']]
              if spec.get('domain') else None)
    params = {sp.Symbol(name): [sp.sympify(v) for v in values]
              for name, values in (spec.get('params') or {}).items()} or None
    at = [sp.sympify(v) for v in spec['at']] if spec.get('at') else None

    if what == 'turning':
        values = parse_many(raw)
        got = values if len(values) > 1 else values[0]
        return _capture(kit.verify_turning, 'Ответ', got, here,
                        spec.get('which'), var=var, dep=dep, domain=domain,
                        coordinates=spec.get('coordinates', True), params=params)
    if what == 'nature':
        words = _words(raw, len(at))
        return _capture(kit.verify_nature, 'Ответ', words, here,
                        at if len(at) > 1 else at[0], var=var, dep=dep,
                        domain=domain, params=params)
    if what == 'side':
        words = _words(raw, len(at))
        return _capture(kit.verify_side, 'Ответ', words, here,
                        at if len(at) > 1 else at[0], var=var, dep=dep,
                        params=params)
    if what == 'bend':
        values = parse_many(raw)
        got = values if len(values) > 1 else values[0]
        return _capture(kit.verify_bend, 'Ответ', got, here, var=var, dep=dep,
                        domain=domain, coordinates=spec.get('coordinates', False),
                        params=params)
    if what == 'count':
        found = kit.stationary(here, domain, var=var, dep=dep)
        said = parse_one(raw)
        if said == len(found):
            return True, f'{kit.OK} {said}'
        return False, (f'{kit.NO} на этом промежутке кривая горизонтальна '
                       f'{len(found)} раз, а не {int(said)}')

    letter = sp.Symbol(spec['letter'])
    window = ([sp.sympify(v) for v in spec['window']]
              if spec.get('window') else (-4, 4))

    # Условие записано как F(x, y) = 0, то есть y − f(x); сама f нужна
    # и счёту пересечений, и просмотру стационарных точек.
    formula = -shape.subs(dep, 0)

    def holds(value):
        if spec.get('positive') and value <= 0:
            return None                    # вопрос спрашивает только о c > 0
        now = formula.subs(letter, value)
        if what == 'meets':
            return kit.crossings(now, (-30, 30)) == spec['times']
        return [word for _, _, word in
                kit.stationary(now, domain, var=var)] == list(spec['kinds'])

    return _capture(kit.verify_param_set, 'Ответ',
                    parse_solution_set(raw, letter), holds, var=letter,
                    window=tuple(window))


def _words(raw, count):
    """Ответ-слова тренажёра: «maximum, minimum» или одно слово."""
    parts = [piece.strip().strip("'\"") for piece in
             re.split(r'[,;]|\bи\b|\band\b', _clean(raw)) if piece.strip()]
    return parts if count > 1 else (parts[0] if parts else '')


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
    if expr.has(sp.gamma):
        # sympy сводит факториал к гамма-функции, и (k+1)! превращается
        # в gamma(k+2). Проверке это безразлично, а ученику показывать
        # так нельзя: в школьной программе гамма-функции нет.
        expr = expr.rewrite(sp.factorial)
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
