"""Задачи на счёт для практикума E1: пределы и правило Лопиталя.

Тема — один вопрос, заданный много раз: куда идёт выражение? Отвечают на
него подстановкой. Когда подстановка даёт число, работа окончена; когда
она даёт 0/0 или ∞/∞, начинается всё остальное. Генераторы держатся этого
разреза: первые два приёма закрываются подстановкой, следующие три —
правилом Лопиталя и рядом Маклорена, последние четыре уводят предел
в сторону от x.

Две проверки здесь новые и живут в kit вместе с практикумом. `limit_check`
эталона не хранит вовсе: он берёт выражение из условия, подходит к точке
лестницей и смотрит, туда ли садятся значения. `indeterminate_check`
сторожит балл за «покажите, что форма неопределённая» — смотрит на
числитель и знаменатель порознь и не верит на слово.
"""
from __future__ import annotations

import sympy as sp

from .common import (exact_check, indeterminate_check, limit_check,
                     num_check, poly_latex)

x, t, n = sp.symbols('x t n')
R = sp.Rational


def _frac(top, bottom):
    return f'\\frac{{{top}}}{{{bottom}}}'


def substitute(rng):
    """0/0 от общего множителя: сократить и подставить."""
    root = rng.choice([-3, -2, -1, 1, 2, 3])
    a, b = rng.choice([1, 2, 3]), rng.choice([-4, -1, 1, 5, 7])
    c, d = rng.choice([1, 2, 4]), rng.choice([-3, -1, 2, 3])
    while c * root + d == 0:
        d += 1
    top = sp.expand((x - root) * (a * x + b))
    bottom = sp.expand((x - root) * (c * x + d))
    expr = top / bottom
    want = sp.Rational(a * root + b, c * root + d)
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{x \\to {root}}} '
                   f'{_frac(sp.latex(top), sp.latex(bottom))}$. Ответ точный.'),
        'answer': want,
        'check': limit_check(expr, point=root),
        'budget_ms': 75_000,
        'note': (f'Подстановка даёт 0/0: и верх, и низ делятся на '
                 f'$(x - {root})$. Сократить и подставить снова.'),
    }


def at_infinity(rng):
    """Старшая степень: поделить на неё верх и низ."""
    if rng.random() < 0.5:
        deg = rng.choice([1, 2, 3])
        a, c = rng.choice([2, 3, 5, 7]), rng.choice([2, 3, 4, 6])
        b, d = rng.choice([-5, -1, 4, 9]), rng.choice([-7, -2, 1, 8])
        # Младший член берётся на степень ниже старшего: при deg = 1
        # слагаемое b*x слилось бы со старшим и отношение поехало бы.
        top = a * x**deg + b * x**(deg - 1)
        bottom = c * x**deg + d
        want = R(a, c)
        note = (f'Степени верха и низа совпадают, значит предел — отношение '
                f'старших коэффициентов, {a}/{c}.')
    else:
        a = rng.choice([2, 5, 8, 11])
        b = rng.choice([1, 3, 7, 10])
        top = a * x
        bottom = sp.sqrt(x**2 + b)
        want = sp.Integer(a)
        note = (f'Под корнем $x^2 + {b}$ ведёт себя как $x^2$, значит корень '
                f'ведёт себя как $x$: степени совпадают.')
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{x \\to \\infty}} '
                   f'{_frac(sp.latex(top), sp.latex(bottom))}$. Ответ точный.'),
        'answer': want,
        'check': limit_check(top / bottom, point=sp.oo),
        'budget_ms': 75_000,
        'note': note,
    }


def lhopital(rng):
    """Правило один раз — или назвать форму, не считая ничего."""
    a, b = rng.choice([2, 3, 4, 5]), rng.choice([2, 3, 5, 7])
    top, bottom, want = rng.choice([
        (sp.sin(a * x), sp.tan(b * x), R(a, b)),
        (sp.atan(a * x), sp.sin(b * x), R(a, b)),
        (sp.exp(a * x) - 1, sp.sin(b * x), R(a, b)),
        (sp.sin(a * x), sp.exp(b * x) - 1, R(a, b)),
    ])
    if rng.random() < 0.3:
        return {
            'prompt': (f'Какова форма предела '
                       f'$\\displaystyle\\lim_{{x \\to 0}} '
                       f'{_frac(sp.latex(top), sp.latex(bottom))}$ '
                       f'при подстановке? Ответ строкой: 0/0 или oo/oo.'),
            'answer': '0/0',
            'check': indeterminate_check(top, bottom),
            'budget_ms': 45_000,
            'note': 'Подставить 0 порознь в числитель и в знаменатель.',
        }
    return {
        'prompt': (f'По правилу Лопиталя найдите '
                   f'$\\displaystyle\\lim_{{x \\to 0}} '
                   f'{_frac(sp.latex(top), sp.latex(bottom))}$. Ответ точный.'),
        'answer': want,
        'check': limit_check(top / bottom),
        'budget_ms': 90_000,
        'note': ('Назвать форму, продифференцировать верх и низ порознь, '
                 'подставить. Знак lim писать на каждой строке.'),
    }


def lhopital_again(rng):
    """Знаменатель x^2: одного раунда не хватает."""
    a = rng.choice([1, 2, 3, 4])
    top, want, note = rng.choice([
        (1 - sp.cos(a * x), R(a**2, 2),
         f'После первого раунда снова 0/0: ${a}\\sin {a}x$ над $2x$.'),
        (sp.cos(a * x) - 1, -R(a**2, 2),
         f'После первого раунда снова 0/0: $-{a}\\sin {a}x$ над $2x$.'),
        (sp.exp(a * x) - 1 - a * x, R(a**2, 2),
         f'После первого раунда снова 0/0: $ {a}e^{{{a}x}} - {a}$ над $2x$.'),
    ])
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{x \\to 0}} '
                   f'{_frac(sp.latex(top), "x^{2}")}$. Ответ точный.'),
        'answer': want,
        'check': limit_check(top / x**2),
        'budget_ms': 105_000,
        'note': note + ' Форму проверять заново перед каждым применением.',
    }


def maclaurin(rng):
    """Высокая степень внизу: ряд быстрее правила."""
    a = rng.choice([1, 2, 3])
    if rng.random() < 0.5:
        top = sp.exp(a * x) - 1 - a * x - (a * x)**2 / 2
        want = R(a**3, 6)
        note = (f'$e^{{{a}x}} = 1 + {a}x + \\frac{{({a}x)^2}}{{2}} + '
                f'\\frac{{({a}x)^3}}{{6}} + \\dots$ — из условия вычтены '
                f'ровно первые три члена.')
        expr = top / x**3
        shown = _frac(sp.latex(top), 'x^{3}')
    else:
        k = rng.choice([2, 3])
        top = (x * sp.exp(a * x) - x)**k
        want = sp.Integer(a**k)
        note = (f'$x^{{{2 * k}}} = (x^{{2}})^{{{k}}}$: вынести степень '
                f'наружу и остаться с $\\left(\\frac{{e^{{{a}x}} - 1}}'
                f'{{x}}\\right)^{{{k}}}$.')
        expr = top / x**(2 * k)
        shown = _frac(sp.latex(top), f'x^{{{2 * k}}}')
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{x \\to 0}} {shown}$ '
                   f'рядом Маклорена. Ответ точный.'),
        'answer': want,
        'check': limit_check(expr),
        'budget_ms': 120_000,
        'note': note,
    }


def make_finite(rng):
    """Постоянная подбирается так, чтобы предел был конечным."""
    if rng.random() < 0.5:
        a = rng.choice([4, 9, 16, 25, 36])
        want = sp.Integer(int(sp.sqrt(a)))
        top = f'\\sqrt{{{a} + x}} - c'
        note = (f'Знаменатель идёт в ноль, значит и числитель обязан: '
                f'$c = \\sqrt{{{a}}}$.')
        bottom = 'x'
    else:
        a = rng.choice([1, 2, 3, 4])
        want = sp.Integer(1)
        top = f'\\cos {a}x - c'
        note = 'Знаменатель идёт в ноль, значит и числитель: $c = \\cos 0 = 1$.'
        bottom = 'x^{2}'
    return {
        'prompt': (f'Предел $\\displaystyle\\lim_{{x \\to 0}} '
                   f'{_frac(top, bottom)}$ конечен. Найдите $c$. '
                   f'Ответ точный.'),
        'answer': want,
        'check': exact_check(want),
        'budget_ms': 75_000,
        'note': note,
    }


def parameter(rng):
    """Стрелка стоит под параметром, а не под x."""
    num, den = rng.choice([(1, 2), (1, 3), (2, 3), (3, 4), (1, 5), (2, 5)])
    sign = rng.choice([1, -1])
    m = R(sign * num, den)
    c = rng.choice([2, 3, 5, 7, 12])
    # При a = c/(1 - m) степень m^n сокращается начисто и выражение
    # оказывается постоянным: приём исчезает вместе с ней.
    a = rng.choice([v for v in (2, 4, 6) if v != c / (1 - m)])
    expr = m**n * a + c * (1 - m**n) / (1 - m)
    want = sp.nsimplify(c / (1 - m))
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{n \\to \\infty}}'
                   f'\\left({sp.latex(m)}^{{\\,n}} \\cdot {a} + {c}\\,'
                   f'\\frac{{1 - {sp.latex(m)}^{{\\,n}}}}'
                   f'{{1 - {sp.latex(m)}}}\\right)$. Ответ точный.'),
        'answer': want,
        'check': limit_check(expr, var='n', point=sp.oo),
        'budget_ms': 90_000,
        'note': (f'Движется только ${sp.latex(m)}^n$, и при модуле меньше '
                 f'единицы он идёт в ноль. Остаётся ${c}/(1 - m)$.'),
    }


def symbolic(rng):
    """Параметр сидит внутри выражения: ответ выйдет формулой от n."""
    if rng.random() < 0.5:
        expr = (x**n - 1) / (x - 1)
        want = n
        point = 1
        shown = _frac('x^{n} - 1', 'x - 1')
        where = 'x \\to 1'
        note = ('Форма 0/0 при любом $n$. Один раунд правила: '
                '$nx^{n-1}$ над $1$, и при $x = 1$ это $n$.')
    else:
        power = rng.choice([2, 4])
        expr = (sp.cos(x)**n - 1) / x**power
        want = -n / 2 if power == 2 else -n / 2
        if power == 4:
            expr = (sp.cos(x)**n - 1) / x**2
            power = 2
        point = 0
        shown = _frac('\\cos^{n} x - 1', 'x^{2}')
        where = 'x \\to 0'
        note = ('$\\cos^n x = 1 - \\frac{n x^2}{2} + \\dots$ — только два '
                'первых члена бинома и переживают деление на $x^2$.')
    return {
        'prompt': (f'Найдите $\\displaystyle\\lim_{{{where}}} {shown}$ '
                   f'через $n$, где $n \\in \\mathbb{{Z}}^{{+}}$.'),
        'answer': want,
        'check': limit_check(expr, point=point, params={n: (1, 2, 5, 9)}),
        'budget_ms': 105_000,
        'note': note,
    }


def interpret(rng):
    """Предел как утверждение о модели: назвать значение, к которому идёт."""
    if rng.random() < 0.5:
        limit = rng.choice([400, 800, 1500, 2500, 5000])
        c = rng.choice([3, 4, 9, 19])
        k = rng.choice([R(2, 10), R(3, 10), R(4, 10), R(5, 10)])
        expr = limit / (1 + c * sp.exp(-k * t))
        story = (f'Численность популяции моделируется как '
                 f'$P(t) = \\dfrac{{{limit}}}{{1 + {c}e^{{-{sp.latex(k)}t}}}}$, '
                 f'где $t$ — годы.')
        note = (f'$e^{{-kt}} \\to 0$, знаменатель идёт к единице. Это потолок '
                f'модели: численность к нему подходит, но не достигает.')
        want = sp.Integer(limit)
    else:
        top = rng.choice([R(714, 100), R(814, 100), R(912, 100)])
        b = rng.choice([R(2, 10), R(3, 10), R(5, 10)])
        expr = top * t / sp.sqrt(t**2 + b)
        story = (f'Скорость бегуньи на дистанции моделируется как '
                 f'$v(t) = \\dfrac{{{sp.latex(top)}\\,t}}'
                 f'{{\\sqrt{{t^2 + {sp.latex(b)}}}}}$, где $t$ — секунды.')
        note = ('Степени верха и низа совпадают. На экзамене за этим пунктом '
                'идёт второй: сказать, почему бегунья этой скорости не '
                'достигает — забег кончается раньше.')
        want = top
    return {
        'prompt': (f'{story} К какому значению идёт модель при '
                   f'$t \\to \\infty$? Ответ точный.'),
        'answer': want,
        'check': limit_check(expr, var='t', point=sp.oo),
        'budget_ms': 75_000,
        'note': note,
    }


GENERATORS = {
    'E1.substitute': substitute,
    'E1.at_infinity': at_infinity,
    'E1.lhopital': lhopital,
    'E1.lhopital_again': lhopital_again,
    'E1.maclaurin': maclaurin,
    'E1.make_finite': make_finite,
    'E1.parameter': parameter,
    'E1.symbolic': symbolic,
    'E1.interpret': interpret,
}
