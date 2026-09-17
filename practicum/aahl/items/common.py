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


def model_check(data, var='t', sf=6):
    """Ответ — модель: подставляются данные условия, эталона нет вовсе.

    Шесть значащих цифр, а не три: данные в условии точны, и трёх хватило
    бы, чтобы принять модель, промахнувшуюся на 150 из 15000.
    """
    return {'kind': 'model', 'var': var, 'sf': sf,
            'data': [[sp.srepr(sp.sympify(point)),
                      None if value is None else sp.srepr(sp.sympify(value))]
                     for point, value in data]}


def in_terms_of_check(want, subs):
    """Ответ выражают через данные буквы: чужих в нём быть не должно."""
    return {'kind': 'in_terms_of', 'want': sp.srepr(sp.sympify(want)),
            'subs': {str(name): sp.srepr(sp.sympify(value))
                     for name, value in subs.items()}}


def limit_check(expr, var='x', point=0, side=None, params=None, tol=1e-6):
    """Ответ — предел: эталона нет, проверка подходит к точке лестницей.

    point записывается строкой, чтобы в банк ушли и oo, и pi/2.
    params — {буква: список значений}, когда ответ выражен через параметр.
    """
    spec = {'kind': 'limit', 'expr': sp.srepr(sp.sympify(expr)), 'var': var,
            'point': sp.srepr(sp.sympify(point)), 'tol': tol}
    if side is not None:
        spec['side'] = side
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def maclaurin_check(f, order=None, terms=None, var='x', params=None):
    """Ответ — отрезок ряда Маклорена: эталона нет, проверка вычитает его из f.

    order — «до члена с x^k включительно», terms — «первые k ненулевых
    членов». Ровно одно из двух, как и в kit.
    """
    spec = {'kind': 'maclaurin', 'f': sp.srepr(sp.sympify(f)), 'var': var}
    if order is not None:
        spec['order'] = int(order)
    if terms is not None:
        spec['terms'] = int(terms)
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def series_solution_check(rhs, ic, order, var='x', dep='y'):
    """Ответ — начало ряда решения уравнения: подставляется в само уравнение."""
    return {'kind': 'series_solution', 'rhs': sp.srepr(sp.sympify(rhs)),
            'ic': sp.srepr(sp.sympify(ic)), 'order': int(order),
            'var': var, 'dep': dep}


def terms_check(term, bound, var='k', strict=True):
    """Ответ — сколько членов ряда нужно взять: границу примеряют к n и n+1."""
    return {'kind': 'terms', 'term': sp.srepr(sp.sympify(term)),
            'bound': sp.srepr(sp.sympify(bound)), 'var': var,
            'strict': bool(strict)}


def derivative_check(f, var='x', order=1, params=None):
    """Ответ — производная: эталона нет, проверка дифференцирует f сама.

    Она же называет именной промах, если написанное совпало с одним из них:
    потерянный множитель цепного правила, произведение как u′v′,
    перевёрнутый знак в частном, непонижённый показатель.
    """
    spec = {'kind': 'derivative', 'f': sp.srepr(sp.sympify(f)),
            'var': var, 'order': int(order)}
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def _curve_spec(rule, var='x', dep='y'):
    """Кривая для проверки: условие F(x, y) = 0 в переносимом виде."""
    rule = sp.sympify(rule)
    if isinstance(rule, sp.Eq):
        rule = rule.lhs - rule.rhs
    return sp.srepr(rule), var, dep


def tangent_check(rule, at, normal=False, var='x', dep='y'):
    """Ответ — касательная (или нормаль): прямая, которой кривая держится.

    Эталона нет: проверка идёт по кривой из условия и сравнивает наклоны.
    Любая запись прямой проходит — выражение, равенство, точка со скобками.
    """
    shape, var, dep = _curve_spec(rule, var, dep)
    return {'kind': 'normal' if normal else 'tangent', 'rule': shape,
            'var': var, 'dep': dep, 'at': sp.srepr(sp.sympify(at))}


def slope_check(rule, at=None, domain=None, var='x', dep='y'):
    """Ответ — наклон кривой: сверяется ходьбой по ней, а не эталоном."""
    shape, var, dep = _curve_spec(rule, var, dep)
    spec = {'kind': 'slope', 'rule': shape, 'var': var, 'dep': dep}
    if at is not None:
        spec['at'] = sp.srepr(sp.sympify(at))
    if domain is not None:
        spec['domain'] = [sp.srepr(sp.sympify(v)) for v in domain]
    return spec


def where_check(rule, slope, domain, coordinates=False, var='x', dep='y'):
    """Ответ — точки кривой с заданным наклоном; полнота набора тоже."""
    shape, var, dep = _curve_spec(rule, var, dep)
    return {'kind': 'where', 'rule': shape, 'var': var, 'dep': dep,
            'slope': sp.srepr(sp.sympify(slope)),
            'domain': [sp.srepr(sp.sympify(v)) for v in domain],
            'coordinates': bool(coordinates)}


def second_check(rule, at, var='x', dep='y'):
    """Ответ — вторая производная: три шага по кривой вместо повторного
    дифференцирования."""
    shape, var, dep = _curve_spec(rule, var, dep)
    return {'kind': 'second', 'rule': shape, 'var': var, 'dep': dep,
            'at': sp.srepr(sp.sympify(at))}


def constant_check(rule, letter, at, slope, window, var='x', dep='y'):
    """Ответ — постоянная внутри кривой, подобранная под наклон.

    rule содержит букву letter; проверка подставляет в неё ответ, строит
    кривую и меряет наклон в точке. Полнота — просмотром окна window.
    """
    shape, var, dep = _curve_spec(rule, var, dep)
    return {'kind': 'constant', 'rule': shape, 'var': var, 'dep': dep,
            'letter': str(letter), 'at': sp.srepr(sp.sympify(at)),
            'slope': sp.srepr(sp.sympify(slope)),
            'window': [sp.srepr(sp.sympify(v)) for v in window]}


def antiderivative_check(f, var='x', domain=None, params=None, through=None):
    """Ответ — первообразная: эталона нет, проверка дифференцирует написанное.

    Постоянная свободна в любом костюме; through=(x0, y0) её снимает, когда
    в условии дана точка графика.
    """
    spec = {'kind': 'antiderivative', 'f': sp.srepr(sp.sympify(f)), 'var': var}
    if domain is not None:
        spec['domain'] = [sp.srepr(sp.sympify(v)) for v in domain]
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    if through is not None:
        spec['through'] = [sp.srepr(sp.sympify(v)) for v in through]
    return spec


def integral_check(f, a, b, var='x', params=None, tol=None, value=None):
    """Ответ — число определённого интеграла: считается сложением, не формулой.

    value задаёт обратный ход: интеграл известен, а ответом служит верхний
    предел. Тогда написанное подставляется на место b, а сверяется value.
    """
    spec = {'kind': 'integral', 'f': sp.srepr(sp.sympify(f)), 'var': var,
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b))}
    if value is not None:
        spec['value'] = sp.srepr(sp.sympify(value))
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    if tol is not None:
        spec['tol'] = float(tol)
    return spec


def accumulated_check(f, lower, upper, var='t', params=None, domain=None):
    """Ответ — накопленное с начала: G′(s) = f(s) и G(a) = 0."""
    spec = {'kind': 'accumulated', 'f': sp.srepr(sp.sympify(f)), 'var': var,
            'lower': sp.srepr(sp.sympify(lower)),
            'upper': sp.srepr(sp.sympify(upper))}
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    if domain is not None:
        spec['domain'] = [sp.srepr(sp.sympify(v)) for v in domain]
    return spec


def transformed_check(f, sub, var='x', new='u', domain=None):
    """Ответ — подынтегральное выражение после замены: g(u(x))·u′(x) = f(x)."""
    spec = {'kind': 'transformed', 'f': sp.srepr(sp.sympify(f)),
            'sub': sp.srepr(sp.sympify(sub)), 'var': var, 'new': new}
    if domain is not None:
        spec['domain'] = [sp.srepr(sp.sympify(v)) for v in domain]
    return spec


def reduction_check(term, index, of='J', var='x', span=(0.3, 1.2),
                    values=(2, 3, 4, 5)):
    """Ответ — формула понижения: численное тождество между интегралами."""
    return {'kind': 'reduction', 'term': sp.srepr(sp.sympify(term)),
            'index': str(index), 'of': str(of), 'var': var,
            'span': [float(v) for v in span],
            'values': [int(v) for v in values]}


def termwise_check(f, upto, var='x'):
    """Ответ — интеграл ряда: производная сходится с рядом до степени upto − 1."""
    return {'kind': 'termwise', 'f': sp.srepr(sp.sympify(f)),
            'upto': int(upto), 'var': var}


def constants_check(unknowns, conditions):
    """Ответ — постоянные, найденные из условий на кривую.

    conditions — список пар (что это за условие, выражение или Eq),
    каждое из которых после подстановки обязано обратиться в ноль.
    """
    return {'kind': 'constants',
            'unknowns': [str(u) for u in unknowns],
            'conditions': [[what, sp.srepr(sp.sympify(cond))]
                           for what, cond in conditions]}


def space_check(space, find, given=None):
    """Вероятность считается по выписанному пространству, а не по эталону.

    space — словарь «имя исхода → вес», find и given — списки имён.
    Событие в конечном пространстве это набор его исходов, поэтому
    никакого языка предикатов заводить не нужно: имена сериализуются
    как есть и уезжают на страницу вместе с заданием. Эталона среди них
    нет — ответ проверка выводит сама, складывая веса.
    """
    spec = {'kind': 'space',
            'space': [[name, sp.srepr(sp.sympify(w))]
                      for name, w in space.items()],
            'find': list(find)}
    if given is not None:
        spec['given'] = list(given)
    return spec


def independence_check(space, a, b):
    """Ответ — два числа: P(A)·P(B) и P(A∩B). Вердикт следует из них."""
    return {'kind': 'independence',
            'space': [[name, sp.srepr(sp.sympify(w))]
                      for name, w in space.items()],
            'a': list(a), 'b': list(b)}


def binomial_check(model, event, given=None):
    """Вероятность события над биномиальными величинами — сложением, без эталона.

    model — словарь «имя → (n, p)»; p бывает и событием над другой моделью:
    `(10, ('inner', (40, 0.628364), ['leaf', 'A', '>=', 30]))` — коробка,
    в которой не меньше тридцати яблок. event и given — деревья сравнений
    ['leaf', имя, '>=', k], ['and', …], ['or', …], ['xor', …], ['not', …].
    Страница пересобирает из них Bin(...) и P(...) и зовёт тот же
    verify_binomial, что стоит в ноутбуке D3.
    """
    def pack(value):
        n, p = value
        if isinstance(p, tuple) and p and p[0] == 'inner':
            return [int(n), ['inner', pack(p[1]), p[2]]]
        return [int(n), sp.srepr(sp.sympify(p))]

    spec = {'kind': 'binomial',
            'model': {name: pack(value) for name, value in model.items()},
            'event': event}
    if given is not None:
        spec['given'] = given
    return spec


def moment_check(what, n, p, a=1, b=0):
    """E(aX + b) или Var(aX + b) для X ~ B(n, p); what — 'mean' или 'var'."""
    return {'kind': 'moment', 'what': what, 'n': int(n),
            'p': sp.srepr(sp.sympify(p)), 'a': sp.srepr(sp.sympify(a)),
            'b': sp.srepr(sp.sympify(b))}


def parameter_check(n, variance):
    """Все p, при которых у B(n, p) данная дисперсия. Корни ищет проверка."""
    return {'kind': 'parameter', 'n': int(n),
            'variance': sp.srepr(sp.sympify(variance))}


def trials_check(p, rel, k, holds=None, near=None):
    """Число испытаний: наименьшее n, при котором P(X rel k) holds, или n,
    при котором она примерно равна near. holds — пара ('>', 0.99)."""
    spec = {'kind': 'trials', 'p': sp.srepr(sp.sympify(p)), 'rel': rel,
            'k': int(k)}
    if holds is not None:
        spec['holds'] = [holds[0], sp.srepr(sp.sympify(holds[1]))]
    if near is not None:
        spec['near'] = sp.srepr(sp.sympify(near))
    return spec


def table_check(what, tables, target=None, unknowns=(), conditions=(), letters=None,
                a=1, b=0, var=None, geo=None, whole=False):
    """Вопрос о дискретной величине, заданной таблицей, D4.

    tables — словарь «имя → (таблица, частоты ли)», таблица — «значение →
    вероятность», буквы внутри разрешены. what — что спрашивают: 'letters'
    (буквы unknowns), 'mean' и 'var' (от aX + b величины target), 'range'
    (диапазон буквы var), 'mode', 'pgf'. conditions — пары вида
    ('mean', имя, число), ('var', имя, число), ('size', имя, число).
    letters — допущения о буквах: {'f': {'integer': True, 'nonnegative': True}}.
    geo — p для величины «первый успех»: тогда таблиц нет, target = 'X'.

    Эталона в описании нет: страница пересобирает Dist, Freq, Geo и зовёт
    те же verify_letters, verify_moment, verify_table_range, verify_mode и
    verify_pgf, что стоят в ноутбуке.
    """
    packed = {}
    for name, (table, counts) in tables.items():
        packed[name] = {'counts': bool(counts),
                        'cells': [[sp.srepr(sp.sympify(value)), sp.srepr(sp.sympify(chance))]
                                  for value, chance in table.items()]}
    spec = {'kind': 'table', 'what': what, 'tables': packed,
            'target': target, 'unknowns': [str(u) for u in unknowns],
            'conditions': [[kind, name, sp.srepr(sp.sympify(value))]
                           for kind, name, value in conditions],
            'letters': {str(k): dict(v) for k, v in (letters or {}).items()},
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b))}
    if var is not None:
        spec['var'] = str(var)
    if geo is not None:
        spec['geo'] = sp.srepr(sp.sympify(geo))
    if whole:
        spec['whole'] = True
    return spec


def normal_check(what, models, find=None, given=None, conditions=(), unknowns=(),
                 sf=None, percent=False, free=None, rules=None):
    """Вопрос о нормальной величине, D5.

    models — словарь «имя → (среднее, дисперсия)», буквы разрешены. События
    записываются списками: ('<', 'X', 170), ('>', 'X', 185), ('between', 'X',
    170, 185). what — 'chance' (ответ — площадь события find, при условии
    given, если оно есть) или 'letters' (ответ — буквы unknowns). conditions —
    пары (событие, площадь): так вопрос задаёт σ, μ или границу.
    free — буква, от которой ответ не зависит. rules — правило из условия:
    {'X': {2: 0.95}} — «95 % в пределах двух стандартных отклонений».

    Эталона в описании нет: страница пересобирает Normal и события и зовёт
    те же verify_chance и verify_letters, что стоят в ноутбуке.
    """
    def event(item):
        kind, name, *bounds = item
        return [kind, name] + [sp.srepr(sp.sympify(b)) for b in bounds]

    spec = {'kind': 'bell', 'what': what,
            'models': {name: [sp.srepr(sp.sympify(m)), sp.srepr(sp.sympify(v))]
                       for name, (m, v) in models.items()},
            'conditions': [[event(e), sp.srepr(sp.sympify(value))] for e, value in conditions],
            'unknowns': [str(u) for u in unknowns]}
    if find is not None:
        spec['find'] = event(find)
    if given is not None:
        spec['given'] = event(given)
    if sf is not None:
        spec['sf'] = sf
    if percent:
        spec['percent'] = True
    if free is not None:
        spec['free'] = str(free)
    if rules:
        spec['rules'] = {name: [[str(k), sp.srepr(sp.sympify(v))] for k, v in rule.items()]
                         for name, rule in rules.items()}
    return spec


def density_check(what, pieces, var='x', find=None, given=None, conditions=(), unknowns=(),
                  exact=False, name='X'):
    """Вопрос о величине с плотностью, D6.

    pieces — список (левый край, правый край, формула), вне них плотность
    ноль; буквы разрешены. События — как у normal_check: ('<', 'X', 1.5),
    ('>', 'X', 2), ('between', 'X', 0.5, 1.5). what — 'chance' (площадь
    события find, при условии given), 'letters' (буквы unknowns: константа
    плотности из того, что площадь — единица, или граница по conditions),
    'mode', 'mean' или 'var'.

    Эталона в описании нет: страница пересобирает Density и события и зовёт
    те же verify_chance, verify_letters, verify_mode и verify_moment, что
    стоят в ноутбуке.
    """
    def event(item):
        kind, label, *bounds = item
        return [kind, label] + [sp.srepr(sp.sympify(b)) for b in bounds]

    spec = {'kind': 'density', 'what': what, 'var': var, 'name': name,
            'pieces': [[sp.srepr(sp.sympify(lo)), sp.srepr(sp.sympify(hi)), sp.srepr(sp.sympify(f))]
                       for lo, hi, f in pieces],
            'conditions': [[event(e), sp.srepr(sp.sympify(value))] for e, value in conditions],
            'unknowns': [sp.srepr(u) for u in unknowns]}
    if find is not None:
        spec['find'] = event(find)
    if given is not None:
        spec['given'] = event(given)
    if exact:
        spec['exact'] = True
    return spec


def vector_check(what, letter=None, **parts):
    """Вопрос о векторах, C5, и о плоскостях, C6.

    what — что спрашивают: 'midpoint', 'vertex', 'distance', 'dot',
    'perpendicular', 'angle', 'vertex_angle', 'line', 'line_angle', 'meet',
    'relation', 'speed', 'bearing'; для плоскостей — 'plane',
    'perpendicular_planes', 'three_points', 'line_plane', 'two_planes',
    'three_planes', 'no_unique', 'foot', 'plane_distance', 'reflection'
    (правая часть уравнения плоскости — список из одного числа); об измерениях,
    C7 — 'cross', 'area_triangle', 'area_parallelogram', 'volume', 'lagrange'
    (letter говорит, что ищут: 'u' или 'cross'), 'plane_angle',
    'line_plane_angle', 'sphere_arc', 'closest', 'line_distance'.
    parts — точки и направления списками
    чисел (в 'perpendicular' одна компонента — буква letter).

    Эталона в описании нет: страница пересобирает векторы, прямые, плоскости и
    фигуры и зовёт те же verify_find, verify_line, verify_meet, verify_relation,
    verify_angle, verify_speed, verify_bearing, verify_plane, verify_cross,
    verify_measure, verify_arc и verify_distance, что стоят в ноутбуках.
    """
    spec = {'kind': 'vector', 'what': what,
            'parts': {name: [sp.srepr(sp.sympify(v)) for v in values]
                      for name, values in parts.items()}}
    if letter is not None:
        spec['letter'] = letter
    return spec


def indeterminate_check(num, den, var='x', point=0, side=None, params=None):
    """Ответ — сама неопределённость: '0/0' или 'oo/oo', проверяется порознь."""
    spec = {'kind': 'indeterminate', 'num': sp.srepr(sp.sympify(num)),
            'den': sp.srepr(sp.sympify(den)), 'var': var,
            'point': sp.srepr(sp.sympify(point))}
    if side is not None:
        spec['side'] = side
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
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


# ================================================ E6: измеренное и измерение
# Шесть проверок темы площадей и объёмов. Общее у них то же, что и у E5,
# только с другой стороны: ни одна не берёт производной. Площадь меряется
# полосами, объём — дисками, поверхность — усечёнными конусами, путь —
# полной вариацией положения.

def region_check(top, bottom=0, a=None, b=None, var='x', params=None,
                 digits=3, window=None):
    """Ответ — площадь: она меряется полосами |верх − низ|.

    a и b можно не задавать: тогда проверка сама находит, где границы
    встречаются, делением пополам внутри window.
    """
    spec = {'kind': 'region', 'top': sp.srepr(sp.sympify(top)),
            'bottom': sp.srepr(sp.sympify(bottom)), 'var': var,
            'digits': digits}
    if a is not None:
        spec['a'] = sp.srepr(sp.sympify(a))
    if b is not None:
        spec['b'] = sp.srepr(sp.sympify(b))
    if window is not None:
        spec['window'] = [sp.srepr(sp.sympify(v)) for v in window]
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def solid_check(outer, a, b, inner=0, var='x', axis='x', params=None,
                digits=3, value=None):
    """Ответ — объём тела вращения: стопка дисков и колец.

    value задаёт обратный ход: объём известен, а ответом служит предел
    интегрирования — он и уходит в b.
    """
    spec = {'kind': 'solid', 'outer': sp.srepr(sp.sympify(outer)),
            'inner': sp.srepr(sp.sympify(inner)), 'var': var, 'axis': axis,
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b)),
            'digits': digits}
    if value is not None:
        spec['value'] = sp.srepr(sp.sympify(value))
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def surface_check(curve, a, b, var='x', params=None, digits=3):
    """Ответ — площадь поверхности вращения: набор усечённых конусов."""
    spec = {'kind': 'surface', 'curve': sp.srepr(sp.sympify(curve)),
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b)),
            'var': var, 'digits': digits}
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def travelled_check(v, a, b, var='t', params=None, digits=3):
    """Ответ — пройденный путь: полная вариация положения."""
    spec = {'kind': 'travelled', 'v': sp.srepr(sp.sympify(v)),
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b)),
            'var': var, 'digits': digits}
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def position_check(v, a, b, var='t', start=0, params=None, digits=3):
    """Ответ — перемещение или положение: сумма сдвигов со знаком."""
    spec = {'kind': 'position', 'v': sp.srepr(sp.sympify(v)),
            'a': sp.srepr(sp.sympify(a)), 'b': sp.srepr(sp.sympify(b)),
            'start': sp.srepr(sp.sympify(start)), 'var': var, 'digits': digits}
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec


def amount_check(rate, a, b=None, var='t', start=0, at=None, params=None,
                 digits=3):
    """Ответ — накопленное: числом или выражением от времени."""
    spec = {'kind': 'amount', 'rate': sp.srepr(sp.sympify(rate)),
            'a': sp.srepr(sp.sympify(a)),
            'start': sp.srepr(sp.sympify(start)), 'var': var, 'digits': digits}
    if b is not None:
        spec['b'] = sp.srepr(sp.sympify(b))
    if at is not None:
        spec['at'] = [sp.srepr(sp.sympify(v)) for v in at]
    if params:
        spec['params'] = {str(name): [sp.srepr(sp.sympify(v)) for v in values]
                          for name, values in params.items()}
    return spec
