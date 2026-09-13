"""Задачи на счёт для практикума D3: биномиальное распределение.

Тема держится на переводе слов в событие над X ~ B(n, p), и генераторы
идут по тому же разрезу, что и лестница: одно значение; диапазон,
названный словами «не больше», «меньше», «хотя бы», «больше»; среднее
и дисперсия; условие внутри одного распределения; биномиальное поверх
другого; неизвестное n.

Проверки эталона не хранят. `binomial_check` отдаёт странице модель и
событие деревом сравнений, и страница зовёт тот же verify_binomial, что
стоит в ноутбуке: он складывает P(X = k) по значениям и, если ответ
неверен, называет сдвинутую границу. Эталон в задании только для показа
после попытки.

Числа подобраны так, чтобы вероятность не была ни почти нулём, ни почти
единицей: k берётся рядом с np. Иначе «не больше» и «меньше» дают один и
тот же ответ до третьей цифры, и тренировать нечего.
"""
from __future__ import annotations

import sympy as sp

from .common import (binomial_check, moment_check, parameter_check,
                     trials_check)

import kit

R = sp.Rational
PROBS = ['0.15', '0.2', '0.25', '0.3', '0.35', '0.4', '0.6', '0.65', '0.7',
         '0.75', '0.8', '0.85']


def _p(rng, pool=PROBS):
    return R(rng.choice(pool))


def _dec(value):
    """Десятичная запись для условия: 0.35, а не 7/20."""
    return f'{float(value):g}'


def _chance(event):
    """Вероятность события kit числом — для эталона, который увидят после попытки."""
    return sp.Float(sp.N(sp.sympify(event), 15), 15)


def _near_mean(rng, n, p, spread=1):
    """k рядом с np — там, где вероятности не вырождаются."""
    centre = int(round(float(n * p)))
    return max(1, min(n - 1, centre + rng.randint(-spread, spread)))


STORIES = [
    ('Семя всходит с вероятностью ${p}$, семена всходят независимо. '
     'Посеяно ${n}$ семян.', 'взойдёт', 'взойдёт хотя бы одно'),
    ('Баскетболист попадает штрафной бросок с вероятностью ${p}$, броски '
     'независимы. Он бросает ${n}$ раз.', 'попаданий будет',
     'будет хотя бы одно попадание'),
    ('Деталь оказывается бракованной с вероятностью ${p}$ независимо от других. '
     'Проверяют ${n}$ деталей.', 'бракованных окажется',
     'окажется хотя бы одна бракованная'),
]


NOUNS = {'взойдёт': 'взошедших семян', 'попаданий будет': 'попаданий',
         'бракованных окажется': 'бракованных деталей'}


def _story(rng, n, p):
    """Условие, глагол для «ровно k» и оборот для «хотя бы один»."""
    text, verb, one = rng.choice(STORIES)
    return text.replace('{p}', _dec(p)).replace('{n}', str(n)), verb, one


def exact_value(rng):
    """Ровно k: узнать модель и взять вероятность одного значения."""
    n = rng.randint(8, 25)
    p = _p(rng)
    k = _near_mean(rng, n, p)
    story, verb, _ = _story(rng, n, p)
    X = kit.Bin(n, p)
    return {
        'prompt': f'{story} Найдите вероятность того, что {verb} ровно ${k}$.',
        'answer': _chance(kit.P(X == k)),
        'check': binomial_check({'X': (n, p)}, ['leaf', 'X', '==', k]),
        'budget_ms': 60_000,
        'note': (f'X ~ B({n}; {_dec(p)}) и P(X = {k}) — binompdf. Накопленная '
                 f'P(X ≤ {k}) здесь ответ на другой вопрос.'),
    }


PHRASES = {
    '<=': ('не больше ${k}$', 'X ≤ {k} — это ровно то, что даёт binomcdf.'),
    '<': ('меньше ${k}$', 'меньше {k} — это X ≤ {km}: само {k} сюда не входит.'),
    '>=': ('не меньше ${k}$', 'не меньше {k} — это 1 − P(X ≤ {km}): {k} остаётся '
           'в событии, а вычитается всё, что меньше.'),
    '>': ('больше ${k}$', 'больше {k} — это 1 − P(X ≤ {k}): событие начинается '
          'с {kp}.'),
}


def cumulative(rng):
    """Диапазон словами: граница переводится в P(X ≤ k) руками."""
    n = rng.randint(10, 40)
    p = _p(rng)
    X = kit.Bin(n, p)
    story, verb, _ = _story(rng, n, p)
    rel = rng.choice(['<=', '<', '>=', '>', 'one'])
    if rel == 'one':
        p = _p(rng, ['0.02', '0.03', '0.05', '0.08', '0.1'])
        X = kit.Bin(n, p)
        story, _, one = _story(rng, n, p)
        return {
            'prompt': f'{story} Найдите вероятность того, что {one}.',
            'answer': _chance(kit.P(X >= 1)),
            'check': binomial_check({'X': (n, p)}, ['leaf', 'X', '>=', 1]),
            'budget_ms': 60_000,
            'note': (f'Хотя бы один — через дополнение: 1 − P(X = 0) = '
                     f'1 − {_dec(1 - p)}^{n}.'),
        }
    k = _near_mean(rng, n, p, spread=2)
    phrase, why = PHRASES[rel]
    words = phrase.format(k=k)
    event = {'<=': X <= k, '<': X < k, '>=': X >= k, '>': X > k}[rel]
    return {
        'prompt': f'{story} Найдите вероятность того, что {verb} {words}.',
        'answer': _chance(kit.P(event)),
        'check': binomial_check({'X': (n, p)}, ['leaf', 'X', rel, k]),
        'budget_ms': 75_000,
        'note': why.format(k=k, km=k - 1, kp=k + 1),
    }


# Дисперсии, при которых оба корня p — десятичные дроби в одну-две цифры.
VARIANCES = [(50, '8'), (25, '4'), (20, '3.2'), (100, '21'), (40, '9.6'),
             (64, '12'), (30, '6.3'), (80, '12.8')]


def mean_variance(rng):
    """Среднее, дисперсия линейной величины и p по дисперсии."""
    kind = rng.choice(['mean', 'linear', 'parameter'])
    if kind == 'parameter':
        n, variance = rng.choice(VARIANCES)
        v = R(variance)
        roots = sorted(sp.solve(sp.Eq(n * sp.Symbol('p') * (1 - sp.Symbol('p')), v),
                                sp.Symbol('p')))
        return {
            'prompt': (f'Случайная величина $X \\sim B({n},\\ p)$, и '
                       f'$\\mathrm{{Var}}(X) = {variance}$. Найдите все возможные '
                       f'значения $p$.'),
            'answer': [sp.Float(r, 15) for r in roots],
            'check': parameter_check(n, v),
            'budget_ms': 90_000,
            'note': ('np(1 − p) = данному — квадратное уравнение на p. Корни '
                     'в сумме дают единицу: p и 1 − p дают одну дисперсию.'),
        }
    n = rng.choice([20, 24, 30, 40, 50, 60, 64])
    p = _p(rng)
    if kind == 'mean':
        story, verb, _ = _story(rng, n, p)
        return {
            'prompt': f'{story} Найдите ожидаемое число {NOUNS[verb]}.',
            'answer': sp.Float(n * p, 15),
            'check': moment_check('mean', n, p),
            'budget_ms': 45_000,
            'note': (f'E(X) = np = {n}·{_dec(p)}. Ожидаемое число не обязано '
                     f'быть целым и не округляется.'),
        }
    a = rng.choice([2, 3, -2, -3])
    b = rng.choice([1, 5, -4, 10])
    shown = (f'{b} {"+" if a > 0 else "-"} {abs(a)}X')
    return {
        'prompt': (f'$X \\sim B({n},\\ {_dec(p)})$ и $Y = {shown}$. Найдите '
                   f'$\\mathrm{{Var}}(Y)$.'),
        'answer': sp.Float(a * a * n * p * (1 - p), 15),
        'check': moment_check('var', n, p, a, b),
        'budget_ms': 60_000,
        'note': (f'Var(aX + b) = a²·Var(X): постоянная {b} уходит, множитель '
                 f'{a} возводится в квадрат. Var(X) = np(1 − p).'),
    }


def conditional_binomial(rng):
    """Условие внутри одного распределения: числитель — пересечение диапазонов."""
    n = rng.randint(10, 20)
    p = _p(rng, ['0.2', '0.25', '0.3', '0.35', '0.4', '0.45', '0.5'])
    X = kit.Bin(n, p)
    centre = int(round(float(n * p)))
    kind = rng.choice(['inside', 'at_least_one', 'overlap'])
    head = (f'Стрелок попадает в мишень с вероятностью ${_dec(p)}$, выстрелы '
            f'независимы. Он делает ${n}$ выстрелов.')
    if kind == 'inside':
        upper = centre + rng.randint(1, 2)
        exact = max(0, upper - rng.randint(1, 3))
        return {
            'prompt': (f'{head} Известно, что попаданий не больше ${upper}$. '
                       f'Найдите вероятность того, что их ровно ${exact}$.'),
            'answer': _chance(kit.P(X == exact, given=X <= upper)),
            'check': binomial_check({'X': (n, p)}, ['leaf', 'X', '==', exact],
                                    given=['leaf', 'X', '<=', upper]),
            'budget_ms': 90_000,
            'note': (f'X = {exact} целиком внутри X ≤ {upper}, поэтому пересечение '
                     f'— само X = {exact}. Делить на P(X ≤ {upper}).'),
        }
    if kind == 'at_least_one':
        upper = max(2, centre)
        return {
            'prompt': (f'{head} Известно, что было хотя бы одно попадание. '
                       f'Найдите вероятность того, что попаданий не больше '
                       f'${upper}$.'),
            'answer': _chance(kit.P(X <= upper, given=X >= 1)),
            'check': binomial_check({'X': (n, p)}, ['leaf', 'X', '<=', upper],
                                    given=['leaf', 'X', '>=', 1]),
            'budget_ms': 90_000,
            'note': (f'Пересечение X ≤ {upper} и X ≥ 1 — это 1 ≤ X ≤ {upper}: '
                     f'P(X ≤ {upper}) − P(X = 0). Без вычитания дробь больше, '
                     f'чем надо.'),
        }
    lower = max(1, centre - 1)
    upper = centre + rng.randint(1, 3)
    return {
        'prompt': (f'{head} Известно, что попаданий меньше ${upper + 1}$. '
                   f'Найдите вероятность того, что их не меньше ${lower}$.'),
        'answer': _chance(kit.P(X >= lower, given=X < upper + 1)),
        'check': binomial_check({'X': (n, p)}, ['leaf', 'X', '>=', lower],
                                given=['leaf', 'X', '<', upper + 1]),
        'budget_ms': 105_000,
        'note': (f'Меньше {upper + 1} — это X ≤ {upper}. Пересечение с X ≥ {lower} '
                 f'— значения от {lower} до {upper}.'),
    }


def nested(rng):
    """Биномиальное поверх другого: успех — сам событие над моделью."""
    if rng.random() < 0.5:
        seed_p = _p(rng, ['0.8', '0.85', '0.9'])
        inside = rng.choice([10, 12, 15, 20])
        need = inside - rng.choice([1, 2])
        packets = rng.choice([5, 6, 8, 10])
        A = kit.Bin(inside, seed_p)
        good = kit.P(A >= need)
        K = kit.Bin(packets, good)
        exact = max(1, min(packets - 1, int(round(float(sp.sympify(good)) * packets))))
        return {
            'prompt': (f'Семя всходит с вероятностью ${_dec(seed_p)}$. В пакете '
                       f'${inside}$ семян, и пакет считается хорошим, если '
                       f'взошло не меньше ${need}$. Взяли ${packets}$ пакетов. '
                       f'Найдите вероятность того, что хороших ровно ${exact}$.'),
            'answer': _chance(kit.P(K == exact)),
            'check': binomial_check(
                {'K': (packets, ('inner', (inside, seed_p),
                                 ['leaf', 'A', '>=', need]))},
                ['leaf', 'K', '==', exact]),
            'budget_ms': 120_000,
            'note': (f'Внутри испытание — семя: q = P(A ≥ {need}) для '
                     f'A ~ B({inside}; {_dec(seed_p)}). Снаружи испытание — пакет: '
                     f'B({packets}; q). Держите q полностью.'),
        }
    shots = rng.choice([4, 5, 6])
    first, second = sorted({_p(rng, ['0.1', '0.15', '0.2', '0.25', '0.3']),
                            _p(rng, ['0.35', '0.4', '0.45', '0.5'])})
    need = rng.choice([1, 2])
    R_, S_ = kit.Bin(shots, first, 'R'), kit.Bin(shots, second, 'S')
    words = 'хотя бы одно' if need == 1 else 'хотя бы два'
    return {
        'prompt': (f'Два стрелка делают по ${shots}$ выстрелов и попадают '
                   f'независимо с вероятностями ${_dec(first)}$ и '
                   f'${_dec(second)}$. Стрелок проходит дальше, если у него '
                   f'{words} попадани{"е" if need == 1 else "я"}. Найдите '
                   f'вероятность того, что дальше пройдёт ровно один из двоих.'),
        'answer': _chance(kit.P((R_ >= need) ^ (S_ >= need))),
        'check': binomial_check({'R': (shots, first), 'S': (shots, second)},
                                ['xor', ['leaf', 'R', '>=', need],
                                 ['leaf', 'S', '>=', need]]),
        'budget_ms': 120_000,
        'note': ('Ровно один — P(A)(1 − P(B)) + P(B)(1 − P(A)). «Хотя бы один» '
                 'добавил бы случай, когда проходят оба.'),
    }


def unknown_trials(rng):
    """Неизвестное n: наименьшее — логарифмом или таблицей, по вероятности — таблицей."""
    if rng.random() < 0.5:
        p = _p(rng, ['0.05', '0.1', '0.15', '0.2', '0.3'])
        level = _p(rng, ['0.9', '0.95', '0.99'])
        answer = next(n for n in range(1, 500)
                      if 1 - (1 - p) ** n > level)
        return {
            'prompt': (f'Каждая попытка успешна с вероятностью ${_dec(p)}$ '
                       f'независимо от других. Найдите наименьшее число попыток, '
                       f'при котором вероятность хотя бы одного успеха больше '
                       f'${_dec(level)}$.'),
            'answer': sp.Integer(answer),
            'check': trials_check(p, '>=', 1, holds=('>', level)),
            'budget_ms': 90_000,
            'note': (f'1 − {_dec(1 - p)}ⁿ > {_dec(level)}: логарифм даёт дробную '
                     f'границу, и ответ — целое справа от неё. Логарифм числа '
                     f'меньше единицы отрицателен: знак переворачивается.'),
        }
    p = _p(rng, ['0.05', '0.1', '0.2'])
    top = rng.choice([1, 2, 3])
    while True:
        n = rng.randint(top + 6, 60)
        exact = float(sp.sympify(kit.P(kit.Bin(n, p) <= top)))
        if not 0.1 <= exact <= 0.9:
            continue              # у почти нуля и почти единицы таблица не читается
        value = kit.sig(exact, 3)
        neighbours = {kit.sig(sp.sympify(kit.P(kit.Bin(m, p) <= top)), 3)
                      for m in (n - 1, n + 1)}
        if value not in neighbours:
            break
    return {
        'prompt': (f'$X \\sim B(n,\\ {_dec(p)})$, и $P(X \\le {top}) \\approx '
                   f'{value}$. Найдите $n$.'),
        'answer': sp.Integer(n),
        'check': trials_check(p, '<=', top, near=R(value)),
        'budget_ms': 120_000,
        'note': ('Логарифм здесь не поможет: P(X ≤ k) — несколько слагаемых. '
                 'Таблица значений по n, и ответ — то n, где вероятность '
                 'округляется до данной.'),
    }


GENERATORS = {
    'D3.exact_value': exact_value,
    'D3.cumulative': cumulative,
    'D3.mean_variance': mean_variance,
    'D3.conditional_binomial': conditional_binomial,
    'D3.nested': nested,
    'D3.unknown_trials': unknown_trials,
}
