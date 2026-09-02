"""Задачи на счёт для практикума E3: техника дифференцирования.

Тема — один вопрос, заданный по-разному: что за правило здесь работает?
Отвечают на него, глядя на форму записи, а не на смысл функции. Генераторы
держатся того же разреза, что и лестница: первые пять выбирают правило
(степень, таблица, цепь, произведение, частное), шестой и седьмой доводят
результат до нужного вида и повторяют, восьмой оставляет в ответе букву,
девятый читает готовую производную.

Две проверки здесь новые и живут в kit вместе с практикумом.
`derivative_check` эталона не хранит: он дифференцирует функцию из условия
сам. Когда ответ неверен, он строит из той же функции именные промахи —
цепное правило без внутреннего множителя, произведение как u′v′, частное
с перевёрнутым знаком, непонижённый показатель — и называет тот, с которым
совпало написанное. `constants_check` подставляет числа в условия самого
вопроса, потому что буквы стоят внутри функции и подставлять их некуда.
"""
from __future__ import annotations

import sympy as sp

from .common import (constants_check, derivative_check, identity_check,
                     num_check, roots_check, solution_set_check)

x, t, n = sp.symbols('x t n')
a, b, c = sp.symbols('a b c')
R = sp.Rational


def _tex(expr):
    return sp.latex(expr)


def power_rule(rng):
    """Сумма степеней: понизить показатель, постоянную выбросить."""
    p = rng.choice([2, 3, 4, 5])
    q = rng.choice([2, 3, 4])
    d = rng.choice([1, 2, 3, 5])
    f = x**4 - p*x**3 + q*x - d
    return {
        'prompt': (f'Найдите $f\'(x)$ для $f(x) = {_tex(f)}$.'),
        'answer': sp.diff(f, x),
        'check': derivative_check(f),
        'budget_ms': 60_000,
        'note': ('Почленно: показатель вниз на единицу и вперёд множителем. '
                 'Свободное слагаемое исчезает целиком.'),
    }


def standard_derivatives(rng):
    """Таблица: sec, cosec, cot, tan — и два минуса в ней."""
    p = rng.choice([2, 3, 4, 5])
    q = rng.choice([2, 3, 6])
    kind = rng.choice(['sec', 'csc', 'tan'])
    f = {'sec': p*sp.sec(t) - q*sp.tan(t),
         'csc': p*sp.csc(t) + q*sp.cot(t),
         'tan': p*sp.tan(t) - q*sp.sec(t)}[kind]
    return {
        'prompt': (f'Найдите $\\frac{{\\mathrm{{d}}f}}{{\\mathrm{{d}}t}}$ '
                   f'для $f(t) = {_tex(f)}$.'),
        'answer': sp.diff(f, t),
        'check': derivative_check(f, var='t'),
        'budget_ms': 90_000,
        'note': ('$\\sec$ — единственная из трёх без минуса. У $\\csc$ и '
                 '$\\cot$ он есть, и теряется чаще всего именно он.'),
    }


def chain_rule(rng):
    """Что-то внутри скобки: внешняя производная умножается на внутреннюю."""
    p = rng.choice([2, 3, 4])
    q = rng.choice([1, 2, 3])
    outer, name = rng.choice([
        (lambda u: sp.exp(u), 'exp'),
        (lambda u: sp.sqrt(u), 'sqrt'),
        (lambda u: sp.log(u), 'log'),
        (lambda u: sp.sin(u), 'sin'),
    ])
    inner = p*x**2 + q if name != 'log' else p*x**2 + q + 1
    f = outer(inner)
    return {
        'prompt': f'Найдите $f\'(x)$ для $f(x) = {_tex(f)}$.',
        'answer': sp.diff(f, x),
        'check': derivative_check(f),
        'budget_ms': 90_000,
        'note': ('Производная внешней функции, внутренняя остаётся внутри, '
                 'и всё это умножается на производную внутренней.'),
    }


def product_rule(rng):
    """Два движущихся множителя: два слагаемых, а не одно."""
    p = rng.choice([2, 3, 4])
    q = rng.choice([2, 3, 5])
    d = rng.choice([1, 2, 4])
    f = sp.exp(p*x)*(q*x - d)
    return {
        'prompt': (f'Найдите $f\'(x)$ для $f(x) = {_tex(f)}$ и приведите '
                   f'ответ к виду с вынесенным общим множителем.'),
        'answer': sp.simplify(sp.diff(f, x)),
        'check': derivative_check(f),
        'budget_ms': 90_000,
        'note': ('$u\'v + uv\'$, и слагаемых обязано быть два. Внутри '
                 'первого — ещё и цепное правило.'),
    }


def quotient_rule(rng):
    """Движущееся сверху и снизу: порядок в числителе не переставляется."""
    p = rng.choice([2, 3, 5])
    q = rng.choice([1, 2, 4])
    d = rng.choice([2, 3, 4])
    f = (p*x + q)/(d*x**2 - 1)
    return {
        'prompt': f'Найдите $f\'(x)$ для $f(x) = {_tex(f)}$.',
        'answer': sp.simplify(sp.diff(f, x)),
        'check': derivative_check(f),
        'budget_ms': 120_000,
        'note': ('$\\frac{u\'v - uv\'}{v^2}$ — именно в этом порядке. '
                 'Переставив числитель, получите ровно минус ответ.'),
    }


def to_printed_form(rng):
    """Сумма двух дробей, которую надо свести к одной."""
    p = rng.choice([2, 3, 4])
    f = 1/(p - x)**2
    g = x**2
    want = sp.simplify(f*sp.diff(g, x) + g*sp.diff(f, x))
    return {
        'prompt': (f'Даны $f(x) = {_tex(f)}$ и $g(x) = {_tex(g)}$. '
                   f'Запишите $f(x)g\'(x) + g(x)f\'(x)$ одной дробью.'),
        'answer': want,
        'check': identity_check(want),
        'budget_ms': 150_000,
        'note': (f'Общий знаменатель здесь $({p} - x)^3$, а не '
                 f'$({p} - x)^5$: первый знаменатель делит второй.'),
    }


def higher_derivatives(rng):
    """Вторая производная: форма первой решает, сколько это займёт."""
    p = rng.choice([1, 2, 3])
    kind = rng.choice(['root', 'expcos'])
    f = sp.sqrt(1 + p*x) if kind == 'root' else sp.exp(p*x)*sp.cos(x)
    return {
        'prompt': f'Найдите $f\'\'(x)$ для $f(x) = {_tex(f)}$.',
        'answer': sp.simplify(sp.diff(f, x, 2)),
        'check': derivative_check(f, order=2),
        'budget_ms': 150_000,
        'note': ('Первую производную стоит оставить в виде со степенью: '
                 'через дробь второй шаг втрое длиннее.'),
    }


def with_parameter(rng):
    """Буква внутри функции: правило то же, конец другой."""
    p = rng.choice([2, 3, 4])
    f = sp.sqrt(a**2 - p**2*x**2)
    return {
        'prompt': (f'Найдите $\\frac{{\\mathrm{{d}}y}}{{\\mathrm{{d}}x}}$ '
                   f'для $y = {_tex(f)}$, в терминах $x$ и $a$.'),
        'answer': sp.diff(f, x),
        'check': derivative_check(f, params={a: (5, 7, 9)}),
        'budget_ms': 120_000,
        'note': ('$a$ — постоянная и не дифференцируется. А вот множитель '
                 f'${p**2}$ из внутренней производной остаётся.'),
    }


def read_derivative(rng):
    """Производная уже есть: где она ноль и какого знака."""
    p = rng.choice([1, 2, 3])
    q = rng.choice([2, 4, 6])
    prime = 3*x**2 + 2*p*x - q*(p + q)
    if rng.random() < 0.5:
        return {
            'prompt': (f'Производная функции $f$ равна '
                       f'$f\'(x) = {_tex(prime)}$. При каких $x$ у графика '
                       f'$y = f(x)$ горизонтальная касательная?'),
            'answer': sorted(sp.solve(prime, x), key=lambda v: float(v)),
            'check': roots_check(prime, domain=(-40, 40)),
            'budget_ms': 120_000,
            'note': 'Горизонтальная касательная — это $f\'(x) = 0$.',
        }
    return {
        'prompt': (f'Производная функции $f$ равна '
                   f'$f\'(x) = {_tex(prime)}$. При каких $x$ функция $f$ '
                   f'убывает?'),
        'answer': sp.solveset(prime < 0, x, sp.S.Reals),
        'check': solution_set_check(prime < 0),
        'budget_ms': 150_000,
        'note': ('Убывает — это $f\'(x) < 0$, неравенство, а не уравнение. '
                 'Корни только размечают промежутки.'),
    }


GENERATORS = {
    'E3.power_rule': power_rule,
    'E3.standard_derivatives': standard_derivatives,
    'E3.chain_rule': chain_rule,
    'E3.product_rule': product_rule,
    'E3.quotient_rule': quotient_rule,
    'E3.to_printed_form': to_printed_form,
    'E3.higher_derivatives': higher_derivatives,
    'E3.with_parameter': with_parameter,
    'E3.read_derivative': read_derivative,
}
