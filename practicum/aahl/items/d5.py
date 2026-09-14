"""Задачи на счёт для практикума D5: нормальное распределение.

Генераторы идут по той же лестнице, что практикум: площадь при известной
модели; площади, которые складываются без калькулятора; граница по
площади; σ по одной площади; μ и σ по двум; условие внутри.

Проверки эталона не хранят. `normal_check` отдаёт странице модель
N(μ, σ²) и условия вопроса на площади, и страница зовёт те же
verify_chance и verify_letters, что стоят в ноутбуке: площадь проверка
складывает сама под кривой, а σ, μ и границу находит сама. Эталон
в задании только для показа после попытки; считает его здесь функция
ошибок из statistics.NormalDist — путь, которого в проверке нет.
"""
from __future__ import annotations

from statistics import NormalDist

import sympy as sp

from .common import normal_check

R = sp.Rational
Z = NormalDist()


def _num(value):
    """Число для условия: 0.25, 175, 3.5 — без хвоста из нулей."""
    return f'{float(value):g}'


def _model(rng):
    """Правдоподобная модель: среднее и стандартное отклонение «из жизни»."""
    story, unit, mean, spread = rng.choice([
        ('Масса пакета муки', 'г', rng.choice([500, 750, 1000]), rng.choice([4, 5, 6, 8])),
        ('Время поездки', 'мин', rng.choice([35, 42, 48, 55]), rng.choice([3, 4, 5, 6])),
        ('Рост саженца', 'см', rng.choice([60, 72, 85]), rng.choice([6, 7, 9])),
        ('Длина болта', 'мм', rng.choice([40, 50, 64]), rng.choice([0.4, 0.5, 0.8])),
    ])
    return story, unit, mean, spread


def _off(rng, spread):
    """Сдвиг границы от среднего: не целое число σ, чтобы правило не помогало."""
    return round(spread * rng.choice([0.6, 0.8, 1.3, 1.7, 2.2]), 3)


def area(rng):
    """Площадь: меньше, больше, между, процент."""
    story, unit, mean, spread = _model(rng)
    X = NormalDist(mean, spread)
    kind = rng.choice(['<', '>', 'between', 'percent'])
    model = {'X': (mean, sp.Float(spread) ** 2)}
    head = (f'{story} $X$ ({unit}) распределена нормально: '
            f'$X\\sim N({_num(mean)},\\ {_num(spread)}^2)$. ')
    if kind == '<':
        edge = mean - _off(rng, spread)
        return {
            'prompt': head + f'Найдите $P(X<{_num(edge)})$.',
            'answer': sp.Float(X.cdf(edge), 15),
            'check': normal_check('chance', model, find=('<', 'X', edge)),
            'budget_ms': 60_000,
            'note': 'Площадь слева от границы. В калькулятор — стандартное '
                    'отклонение, а не дисперсия.',
        }
    if kind == '>':
        edge = mean + _off(rng, spread)
        return {
            'prompt': head + f'Найдите $P(X>{_num(edge)})$.',
            'answer': sp.Float(1 - X.cdf(edge), 15),
            'check': normal_check('chance', model, find=('>', 'X', edge)),
            'budget_ms': 60_000,
            'note': 'Площадь справа: normalcdf от границы до 10⁹⁹. «Больше» и '
                    '«не меньше» — одна площадь.',
        }
    lo, hi = mean - _off(rng, spread), mean + _off(rng, spread)
    between = X.cdf(hi) - X.cdf(lo)
    if kind == 'between':
        return {
            'prompt': head + f'Найдите $P({_num(lo)}<X<{_num(hi)})$.',
            'answer': sp.Float(between, 15),
            'check': normal_check('chance', model, find=('between', 'X', lo, hi)),
            'budget_ms': 60_000,
            'note': 'Площадь между границами — обе в одном normalcdf.',
        }
    return {
        'prompt': head + (f'Какой процент значений лежит между ${_num(lo)}$ и '
                          f'${_num(hi)}$?'),
        'answer': sp.Float(100 * between, 15),
        'check': normal_check('chance', model, find=('between', 'X', lo, hi), percent=True),
        'budget_ms': 60_000,
        'note': 'Та же площадь, умноженная на 100: спрашивают процент.',
    }


def symmetry(rng):
    """Без калькулятора: правило из условия, симметрия, сумма площадей."""
    kind = rng.choice(['rule', 'sum'])
    if kind == 'rule':
        mean, spread = rng.choice([(50, 4), (80, 5), (120, 10), (30, 2)])
        many, share = rng.choice([(1, R(68, 100)), (2, R(95, 100))])
        side = rng.choice(['>', '<'])
        edge = mean + many * spread if side == '>' else mean - many * spread
        word = 'одного стандартного отклонения' if many == 1 else 'двух стандартных отклонений'
        model = {'X': (mean, spread ** 2)}
        return {
            'prompt': (f'$X\\sim N({mean},\\ {spread}^2)$. Считайте, что '
                       f'${int(share * 100)}\\,\\%$ значений лежат в пределах {word} от '
                       f'среднего. Без калькулятора найдите $P(X{side}{edge})$.'),
            'answer': (1 - share) / 2,
            'check': normal_check('chance', model, find=(side, 'X', edge),
                                  rules={'X': {many: share}}),
            'budget_ms': 45_000,
            'note': (f'Вне μ ± {many}σ лежит {int((1 - share) * 100)} %, и хвосты '
                     f'равны: по половине. Число — из условия, а не с кривой.'),
        }
    low = R(rng.randint(150, 320), 1000)
    high = R(rng.randint(150, 320), 1000)
    a = rng.choice([40, 55, 72])
    b = a + rng.choice([6, 9, 12])
    m, s = sp.symbols('m s')
    model = {'X': (m, s ** 2)}
    return {
        'prompt': (f'Величина $X$ распределена нормально с неизвестными $\\mu$ и '
                   f'$\\sigma$. Известно, что $P(X<{a})={_num(low)}$ и '
                   f'$P(X>{b})={_num(high)}$. Найдите $P({a}<X<{b})$.'),
        'answer': sp.Float(1 - low - high, 15),
        'check': normal_check('chance', model, find=('between', 'X', a, b),
                              conditions=[(('<', 'X', a), low), (('>', 'X', b), high)]),
        'budget_ms': 40_000,
        'note': 'Три площади вместе — единица. Ни μ, ни σ для этого не нужны.',
    }


def boundary(rng):
    """Граница по площади: больше w, меньше w, квартиль."""
    story, unit, mean, spread = _model(rng)
    X = NormalDist(mean, spread)
    w = sp.Symbol('w')
    model = {'X': (mean, sp.Float(spread) ** 2)}
    head = (f'{story} $X$ ({unit}) распределена нормально: '
            f'$X\\sim N({_num(mean)},\\ {_num(spread)}^2)$. ')
    kind = rng.choice(['more', 'less', 'quartile'])
    if kind == 'quartile':
        upper = rng.choice([True, False])
        share = R(3, 4) if upper else R(1, 4)
        return {
            'prompt': head + f'Найдите {"верхний" if upper else "нижний"} квартиль $X$.',
            'answer': sp.Float(X.inv_cdf(float(share)), 15),
            'check': normal_check('letters', model, conditions=[(('<', 'X', w), share)],
                                  unknowns=[w]),
            'budget_ms': 60_000,
            'note': f'Квартиль — граница с площадью {_num(share)} слева: invNorm({_num(share)}).',
        }
    share = R(rng.choice([5, 10, 15, 20, 30]), 100)
    if kind == 'more':
        return {
            'prompt': head + (f'${int(share * 100)}\\,\\%$ значений больше $w$. '
                              f'Найдите $w$.'),
            'answer': sp.Float(X.inv_cdf(1 - float(share)), 15),
            'check': normal_check('letters', model, conditions=[(('>', 'X', w), share)],
                                  unknowns=[w]),
            'budget_ms': 60_000,
            'note': (f'invNorm знает только площадь слева: «больше w с вероятностью '
                     f'{_num(share)}» — это {_num(1 - share)} слева.'),
        }
    return {
        'prompt': head + f'${int(share * 100)}\\,\\%$ значений меньше $w$. Найдите $w$.',
        'answer': sp.Float(X.inv_cdf(float(share)), 15),
        'check': normal_check('letters', model, conditions=[(('<', 'X', w), share)],
                              unknowns=[w]),
        'budget_ms': 60_000,
        'note': f'Площадь слева дана прямо: invNorm({_num(share)}, μ, σ).',
    }


def one_parameter(rng):
    """σ по одной площади: хвост или симметричный промежуток."""
    story, unit, mean, spread = _model(rng)
    s = sp.Symbol('s')
    model = {'X': (mean, s ** 2)}
    kind = rng.choice(['tail', 'interval'])
    if kind == 'tail':
        share = R(rng.choice([2, 5, 10, 15]), 100)
        edge = mean + _off(rng, spread)
        sigma = (edge - mean) / Z.inv_cdf(1 - float(share))
        return {
            'prompt': (f'{story} $X$ ({unit}) распределена нормально со средним '
                       f'${_num(mean)}$ и стандартным отклонением $s$. '
                       f'${int(share * 100)}\\,\\%$ значений больше ${_num(edge)}$. '
                       f'Найдите $s$.'),
            'answer': sp.Float(sigma, 15),
            'check': normal_check('letters', model, conditions=[(('>', 'X', edge), share)],
                                  unknowns=[s]),
            'budget_ms': 90_000,
            'note': (f'Площадь слева от {_num(edge)} — {_num(1 - share)}; z = '
                     f'invNorm({_num(1 - share)}), и ({_num(edge)} − {_num(mean)})/s = z.'),
        }
    share = R(rng.choice([80, 88, 90, 95]), 100)
    half = _off(rng, spread)
    sigma = half / Z.inv_cdf((1 + float(share)) / 2)
    return {
        'prompt': (f'{story} $X$ ({unit}) распределена нормально со средним '
                   f'${_num(mean)}$ и стандартным отклонением $s$. '
                   f'${int(share * 100)}\\,\\%$ значений лежат между '
                   f'${_num(mean - half)}$ и ${_num(mean + half)}$. Найдите $s$.'),
        'answer': sp.Float(sigma, 15),
        'check': normal_check('letters', model,
                              conditions=[(('between', 'X', mean - half, mean + half), share)],
                              unknowns=[s]),
        'budget_ms': 90_000,
        'note': (f'Промежуток симметричен: вне него по {_num((1 - share) / 2)} с каждой '
                 f'стороны, слева от верхней границы {_num((1 + share) / 2)}.'),
    }


def two_parameters(rng):
    """μ и σ по двум площадям."""
    story, unit, mean, spread = _model(rng)
    X = NormalDist(mean, spread)
    lo = round(X.inv_cdf(rng.choice([0.1, 0.2, 0.3])), 1)
    hi = round(X.inv_cdf(rng.choice([0.75, 0.85, 0.9])), 1)
    below = round(X.cdf(lo), 3)
    above = round(1 - X.cdf(hi), 3)
    z1, z2 = Z.inv_cdf(below), Z.inv_cdf(1 - above)
    s_value = (hi - lo) / (z2 - z1)
    m_value = lo - z1 * s_value
    m, s = sp.symbols('m s')
    return {
        'prompt': (f'{story} $X$ ({unit}) распределена нормально с неизвестными '
                   f'средним $m$ и стандартным отклонением $s$. Известно, что '
                   f'$P(X<{_num(lo)})={_num(below)}$ и $P(X>{_num(hi)})={_num(above)}$. '
                   f'Найдите $m$ и $s$ (через запятую).'),
        'answer': [sp.Float(m_value, 15), sp.Float(s_value, 15)],
        'check': normal_check('letters', {'X': (m, s ** 2)},
                              conditions=[(('<', 'X', lo), R(str(below))),
                                          (('>', 'X', hi), R(str(above)))],
                              unknowns=[m, s]),
        'budget_ms': 150_000,
        'note': (f'Два z: invNorm({_num(below)}) и invNorm({_num(round(1 - above, 3))}). '
                 f'Уравнения m + z·s = граница — в z, а не в вероятностях.'),
    }


def condition(rng):
    """Условная вероятность под кривой."""
    story, unit, mean, spread = _model(rng)
    X = NormalDist(mean, spread)
    model = {'X': (mean, sp.Float(spread) ** 2)}
    first = mean + _off(rng, spread) * rng.choice([-1, 1]) * 0.5
    second = first + _off(rng, spread)
    kind = rng.choice(['inside', 'overlap'])
    if kind == 'inside':
        answer = (1 - X.cdf(second)) / (1 - X.cdf(first))
        find, words = ('>', 'X', second), f'больше ${_num(second)}$'
        note = (f'Событие «больше {_num(second)}» лежит внутри условия целиком, '
                f'и числитель — оно само.')
    else:
        answer = (X.cdf(second) - X.cdf(first)) / (1 - X.cdf(first))
        find, words = ('<', 'X', second), f'меньше ${_num(second)}$'
        note = (f'Числитель — пересечение: между {_num(first)} и {_num(second)}, '
                f'а не всё «меньше {_num(second)}».')
    return {
        'prompt': (f'{story} $X$ ({unit}) распределена нормально: '
                   f'$X\\sim N({_num(mean)},\\ {_num(spread)}^2)$. Известно, что '
                   f'значение больше ${_num(first)}$. Найдите вероятность, что оно '
                   f'{words}.'),
        'answer': sp.Float(answer, 15),
        'check': normal_check('chance', model, find=find, given=('>', 'X', first)),
        'budget_ms': 90_000,
        'note': note,
    }


GENERATORS = {
    'D5.area': area,
    'D5.symmetry': symmetry,
    'D5.boundary': boundary,
    'D5.one_parameter': one_parameter,
    'D5.two_parameters': two_parameters,
    'D5.condition': condition,
}
