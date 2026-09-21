"""Задачи на счёт для практикума D7: описательная статистика, регрессия, корреляция.

Генераторы идут по лестнице карточки: пропавшее значение по среднему;
граница выброса по ящику с усами; r по данным; прямая по данным;
подстановка в неё; предсказание x по y — другой прямой; точка средних как
пересечение двух прямых; что делает с r сдвиг и растяжение данных.

Проверки эталона не хранят. `data_check` отдаёт странице сами данные, и
страница зовёт те же verify_missing, verify_fence, verify_strength,
verify_fit, verify_estimate, verify_centre и verify_effect, что стоят в
ноутбуке: прямую там находит поиск по дну суммы квадратов, а r — доля
объяснённого разброса. Эталон в задании только для показа после попытки;
строится он здесь формулами и дробями.
"""
from __future__ import annotations

from fractions import Fraction

import sympy as sp

from .common import data_check

R = sp.Rational


def _row(values):
    return ', '.join(str(v) for v in values)


def _cloud(rng, size=6):
    """Целые данные с заметной, но не идеальной линейной связью.

    При |r| около единицы две прямые регрессии почти совпадают, а r² почти
    равен r: промахи «не та прямая» и «r² вместо r» перестают отличаться от
    верного ответа в трёх цифрах. Поэтому облако берётся с 0.75 ≤ |r| ≤ 0.95.
    """
    while True:
        xs = sorted(rng.sample(range(1, 16), size))
        slope = rng.choice([-3, -2, 2, 3, 4])
        cut = rng.randint(10, 40)
        ys = [slope * x + cut + rng.randint(-9, 9) for x in xs]
        if len(set(ys)) > 1 and 0.75 <= abs(_formula(xs, ys)[2]) <= 0.95:
            return xs, ys


def _formula(xs, ys):
    """a, b, r учебными формулами в дробях — только для показа эталона."""
    xs = [Fraction(v) for v in xs]
    ys = [Fraction(v) for v in ys]
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, float(sxy) / (float(sxx) * float(syy)) ** 0.5


def _sig(value):
    return float(f'{float(value):.3g}')


def summary(rng):
    """Пропавшее значение по среднему: сумма = n · среднее."""
    size = rng.randint(5, 8)
    values = [rng.randint(5, 30) for _ in range(size)]
    where = rng.randrange(size)
    missing = values[where]
    total = sum(values)
    shown = ['p' if i == where else str(v) for i, v in enumerate(values)]
    mean = R(total, size)
    return {
        'prompt': (f'Среднее набора {", ".join(shown)} равно '
                   f'${sp.latex(mean)}$. Найдите $p$.'),
        'answer': sp.Integer(missing),
        'check': data_check('missing', items=[sp.Symbol('p') if i == where else v
                                              for i, v in enumerate(values)],
                            given={'mean': mean}),
        'budget_ms': 60_000,
        'note': 'Сумма = n · среднее: из неё вычитают всё, что известно.',
    }


def outlier(rng):
    """Наибольшее значение, которое ещё не выброс: Q3 + 1.5 · IQR."""
    lower = rng.randint(4, 20)
    upper = lower + 2 * rng.randint(2, 8)
    middle = rng.randint(lower + 1, upper - 1)
    lowest = lower - rng.randint(1, 4)
    highest = upper + rng.randint(1, 20)
    box = (lowest, lower, middle, upper, highest)
    return {
        'prompt': (f'Ящик с усами: минимум {lowest}, $Q_1 = {lower}$, медиана '
                   f'{middle}, $Q_3 = {upper}$, максимум {highest}. Найдите '
                   f'наибольшее значение, которое не было бы выбросом.'),
        'answer': sp.Integer(upper) + R(3, 2) * (upper - lower),
        'check': data_check('fence', box=box),
        'budget_ms': 60_000,
        'note': 'Граница — Q3 + 1.5·IQR, от квартиля, а не от медианы.',
    }


def strength(rng):
    """r по данным."""
    xs, ys = _cloud(rng)
    return {
        'prompt': (f'Данные: $x$ = {_row(xs)}; $y$ = {_row(ys)}. Найдите '
                   f'коэффициент корреляции Пирсона $r$ (три значащие цифры).'),
        'answer': _sig(_formula(xs, ys)[2]),
        'check': data_check('strength', xs=xs, ys=ys),
        'budget_ms': 90_000,
        'note': 'Нужен r, а не r²: калькулятор печатает оба строкой рядом.',
    }


def fit(rng):
    """Прямая y на x по данным."""
    xs, ys = _cloud(rng)
    slope, cut, _ = _formula(xs, ys)
    return {
        'prompt': (f'Данные: $x$ = {_row(xs)}; $y$ = {_row(ys)}. Найдите '
                   f'$a$ и $b$ в прямой регрессии $y = ax + b$. Ответ — пара.'),
        'answer': (_sig(slope), _sig(cut)),
        'check': data_check('fit', xs=xs, ys=ys),
        'budget_ms': 90_000,
        'note': 'Порядок пары — (a, b): наклон, потом свободный член.',
    }


def predict(rng):
    """Подстановка в прямую y на x внутри данных."""
    xs, ys = _cloud(rng)
    # Обе прямые проходят через точку средних, и у x̄ промах «не та прямая»
    # неотличим от верного ответа: точку берут подальше от середины.
    centre = sum(xs) / len(xs)
    at = rng.choice([v for v in range(xs[0] + 1, xs[-1]) if abs(v - centre) >= 3]
                    or [xs[-1] - 1])
    slope, cut, _ = _formula(xs, ys)
    return {
        'prompt': (f'Данные: $x$ = {_row(xs)}; $y$ = {_row(ys)}. По прямой '
                   f'регрессии $y$ на $x$ оцените $y$ при $x = {at}$.'),
        'answer': _sig(slope * at + cut),
        'check': data_check('estimate', xs=xs, ys=ys, at=at),
        'budget_ms': 90_000,
        'note': 'Подставляют в неокруглённую прямую, округляют в конце.',
    }


def direction(rng):
    """Предсказание x по y — прямой x на y."""
    xs, ys = _cloud(rng)
    centre = sum(ys) / len(ys)
    spread = max(ys) - min(ys)
    at = rng.choice([v for v in range(min(ys) + 1, max(ys))
                     if abs(v - centre) >= spread / 4] or [max(ys) - 1])
    back, other, _ = _formula(ys, xs)
    return {
        'prompt': (f'Данные: $x$ = {_row(xs)}; $y$ = {_row(ys)}. Оцените $x$ '
                   f'при $y = {at}$ подходящей прямой регрессии.'),
        'answer': _sig(back * at + other),
        'check': data_check('estimate', xs=xs, ys=ys, at=at, of='x'),
        'budget_ms': 105_000,
        'note': 'Предсказывают x — прямая x на y, а не y на x, решённая относительно x.',
    }


def centre(rng):
    """Точка средних — пересечение двух прямых регрессии."""
    mx, my = rng.randint(2, 20), rng.randint(2, 20)
    one = rng.choice([R(1, 2), R(3, 4), 2, 3, R(3, 2)])
    # Произведение наклонов двух прямых регрессии — это r², и оно меньше
    # единицы: иначе прямые параллельны или таких данных не бывает.
    two = rng.choice([k for k in (R(1, 4), R(1, 3), R(2, 5), R(1, 5)) if one * k < 1])
    lines = (('y', one, my - one * mx), ('x', two, mx - two * my))
    shown = ' и '.join(f'${lhs} = {sp.latex(k)}{"x" if lhs == "y" else "y"} '
                       f'{"+" if c >= 0 else "-"} {sp.latex(abs(c))}$'
                       for lhs, k, c in lines)
    return {
        'prompt': (f'Прямые регрессии {shown}. Найдите $(\\bar x, \\bar y)$. '
                   f'Ответ — пара.'),
        'answer': (sp.Integer(mx), sp.Integer(my)),
        'check': data_check('centre', lines=lines),
        'budget_ms': 90_000,
        'note': 'Обе прямые проходят через точку средних — это их общая точка.',
    }


def cause(rng):
    """Что делает с r пересчёт одной переменной."""
    xs, ys = _cloud(rng, 5)
    scale = rng.choice([2, 3, 10, -1, -2])
    shift = rng.randint(-20, 20)
    _, _, r = _formula(xs, ys)
    moved = r if scale > 0 else -r
    word = ('no effect' if scale > 0 else
            ('decreases' if moved < r else 'increases'))
    change = (f'умножили на {scale}' + (f' и прибавили {shift}' if shift >= 0
                                         else f' и вычли {-shift}'))
    return {
        'prompt': (f'Данные: $x$ = {_row(xs)}; $y$ = {_row(ys)}. Каждое $x$ '
                   f'{change}. Как изменится $r$? Ответ: no effect, increases '
                   f'или decreases.'),
        'answer': word,
        'check': data_check('effect', xs=xs, ys=ys, scale=scale, shift=shift),
        'budget_ms': 60_000,
        'note': 'Сдвиг и растяжение не меняют r; отражение меняет его знак.',
    }


GENERATORS = {
    'D7.summary': summary,
    'D7.outlier': outlier,
    'D7.strength': strength,
    'D7.fit': fit,
    'D7.predict': predict,
    'D7.direction': direction,
    'D7.centre': centre,
    'D7.cause': cause,
}
