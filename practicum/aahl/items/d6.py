"""Задачи на счёт для практикума D6: величина с плотностью.

Генераторы идут по той же лестнице, что практикум: площадь под плотностью;
константа из того, что вся площадь — единица; медиана и квартиль; мода;
среднее и дисперсия; условная вероятность.

Проверки эталона не хранят. `density_check` отдаёт странице плотность по
кускам и условия вопроса, и страница зовёт те же verify_chance,
verify_letters, verify_mode и verify_moment, что стоят в ноутбуке: площадь,
букву, медиану, моду и моменты проверка находит сама квадратурой. Эталон в
задании только для показа после попытки; считает его здесь sympy точной
первообразной — путь, которого в проверке нет.
"""
from __future__ import annotations

import sympy as sp

from .common import density_check

R = sp.Rational
x = sp.Symbol('x')


def _num(value):
    """Число для условия: 0.25, 1.5 — без хвоста из нулей."""
    return f'{float(value):g}'


def _float(value, digits=15):
    """Число эталона: точное выражение sympy — в десятичную дробь."""
    return sp.Float(sp.N(value, 30), digits)


def _tex(expr):
    return sp.latex(sp.sympify(expr))


def _power(rng):
    """f(x) = (n + 1)xⁿ/Lⁿ⁺¹ на [0, L]: формула, по которой считается всё."""
    n = rng.choice([1, 2, 3])
    L = rng.choice([2, 3, 4])
    f = (n + 1) * x ** n / R(L) ** (n + 1)
    return n, L, f


def _head(f, L):
    return (f'Величина $X$ имеет плотность $f(x)={_tex(f)}$ при $0\\le x\\le{L}$ '
            f'и $f(x)=0$ вне этого промежутка. ')


def area(rng):
    """Площадь под плотностью: меньше, больше, между."""
    n, L, f = _power(rng)
    kind = rng.choice(['<', '>', 'between'])
    a = R(rng.choice([1, 2, 3]), 4) * L
    b = a + R(L, 4)
    F = sp.integrate(f, (x, 0, sp.Symbol('q')))
    at = lambda edge: F.subs('q', edge)
    if kind == '<':
        prompt, answer, find = f'Найдите $P(X<{_num(a)})$.', at(a), ('<', 'X', a)
        note = f'Площадь от начала промежутка до {_num(a)}: ∫ f(x) dx от 0.'
    elif kind == '>':
        prompt, answer, find = f'Найдите $P(X>{_num(a)})$.', 1 - at(a), ('>', 'X', a)
        note = f'Площадь справа — до конца промежутка {L}, а не до бесконечности формулы.'
    else:
        b = min(b, L)
        prompt, answer, find = (f'Найдите $P({_num(a)}<X<{_num(b)})$.', at(b) - at(a),
                                ('between', 'X', a, b))
        note = 'Интеграл между границами; за концом промежутка плотность ноль.'
    return {
        'prompt': _head(f, L) + prompt,
        'answer': _float(answer, 15),
        'check': density_check('chance', [(0, L, f)], find=find),
        'budget_ms': 60_000,
        'note': note,
    }


def constant(rng):
    """Константа плотности: ∫ f = 1."""
    L = rng.choice([2, 3, 4])
    k = sp.Symbol('k', positive=True)
    shape = rng.choice([x ** 2, x * (L - x), L - x, x ** 3, sp.sqrt(x)])
    whole = sp.integrate(shape, (x, 0, L))
    return {
        'prompt': (f'Величина $X$ имеет плотность $f(x)=k\\left({_tex(shape)}\\right)$ при '
                   f'$0\\le x\\le{L}$ и $0$ вне этого промежутка. Найдите $k$.'),
        'answer': _float(1 / whole, 15),
        'check': density_check('letters', [(0, L, k * shape)], unknowns=[k]),
        'budget_ms': 60_000,
        'note': f'∫ от 0 до {L} равен {sp.nsimplify(whole)}·k, и он равен единице.',
    }


def quantile(rng):
    """Медиана или квартиль: доля площади слева."""
    n, L, f = _power(rng)
    q = sp.Symbol('q')
    share = rng.choice([R(1, 2), R(1, 4), R(3, 4)])
    word = {R(1, 2): 'медиану', R(1, 4): 'нижний квартиль', R(3, 4): 'верхний квартиль'}[share]
    return {
        'prompt': _head(f, L) + f'Найдите {word} $X$.',
        'answer': _float(L * share ** R(1, n + 1), 15),
        'check': density_check('letters', [(0, L, f)], conditions=[(('<', 'X', q), share)],
                               unknowns=[q]),
        'budget_ms': 60_000,
        'note': f'∫ от 0 до q f(x) dx = {share}: (q/{L})^{n + 1} = {share}.',
    }


def mode(rng):
    """Мода: где плотность наибольшая."""
    p = rng.choice([1, 2, 3])
    L = rng.choice([2, 3, 4])
    c = R((p + 1) * (p + 2), L ** (p + 2))
    f = c * x ** p * (L - x)
    return {
        'prompt': _head(f, L) + 'Найдите моду $X$.',
        'answer': _float(R(p * L, p + 1), 15),
        'check': density_check('mode', [(0, L, f)]),
        'budget_ms': 60_000,
        'note': f"Мода — x, где f′(x) = 0: {p}(L − x) = x, x = {p}·{L}/{p + 1}. Ответ — x, а не f(x).",
    }


def moments(rng):
    """Среднее или дисперсия: интегралы x·f и x²·f."""
    n, L, f = _power(rng)
    mean = sp.integrate(x * f, (x, 0, L))
    square = sp.integrate(x ** 2 * f, (x, 0, L))
    kind = rng.choice(['mean', 'var'])
    if kind == 'mean':
        return {
            'prompt': _head(f, L) + 'Найдите $\\mathrm E(X)$.',
            'answer': _float(mean, 15),
            'check': density_check('mean', [(0, L, f)]),
            'budget_ms': 60_000,
            'note': 'E(X) = ∫ x·f(x) dx по промежутку, где f задана.',
        }
    return {
        'prompt': _head(f, L) + 'Найдите $\\mathrm{Var}(X)$.',
        'answer': _float(square - mean ** 2, 15),
        'check': density_check('var', [(0, L, f)]),
        'budget_ms': 90_000,
        'note': f'Var(X) = ∫ x²f(x) dx − (E(X))²: здесь {sp.nsimplify(square)} − ({sp.nsimplify(mean)})².',
    }


def condition(rng):
    """Условная вероятность под плотностью."""
    n, L, f = _power(rng)
    a = R(rng.choice([1, 2]), 4) * L
    b = a + R(L, 4)
    F = lambda edge: (R(edge) / L) ** (n + 1)
    return {
        'prompt': _head(f, L) + (f'Известно, что $X>{_num(a)}$. Найдите вероятность того, '
                                 f'что $X>{_num(b)}$.'),
        'answer': _float((1 - F(b)) / (1 - F(a)), 15),
        'check': density_check('chance', [(0, L, f)], find=('>', 'X', b), given=('>', 'X', a)),
        'budget_ms': 90_000,
        'note': f'Событие «больше {_num(b)}» лежит внутри условия: P(X > {_num(b)})/P(X > {_num(a)}).',
    }


GENERATORS = {
    'D6.area': area,
    'D6.constant': constant,
    'D6.quantile': quantile,
    'D6.mode': mode,
    'D6.moments': moments,
    'D6.condition': condition,
}
