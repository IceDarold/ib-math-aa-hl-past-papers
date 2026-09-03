"""Задачи на счёт для практикума D2: вероятность.

Тема — один вопрос, заданный по-разному: в каком пространстве мы считаем?
Генераторы держатся того же разреза, что и лестница: первые три работают
на готовой диаграмме Венна, четвёртый и пятый строят дерево и повторные
испытания, шестой и седьмой проходят построенное вниз и вверх, восьмой
и девятый строят пространство счётом, десятый ищет в нём букву.

Проверки эталона не хранят. `space_check` получает пространство
выписанным — имя исхода и его вес — и складывает веса нужных исходов;
`independence_check` считает P(A)·P(B) и P(A∩B) из того же пространства.
Событие в конечном пространстве это набор его исходов, поэтому предикатов
здесь нет: имена сериализуются как есть.

Пространства собираются так, чтобы ответы выходили дробями с небольшим
знаменателем: тренажёр на счёт, а не на арифметику с десятыми.
"""
from __future__ import annotations

import sympy as sp

from .common import independence_check, num_check, space_check

R = sp.Rational


def _venn(both, only_a, only_b):
    """Четыре клетки диаграммы Венна как пространство с именами."""
    return {'AB': both, 'Ab': only_a, 'aB': only_b,
            'ab': 1 - both - only_a - only_b}


A_NAMES = ['AB', 'Ab']
B_NAMES = ['AB', 'aB']
NOT_A = ['aB', 'ab']
NOT_B = ['Ab', 'ab']


def _pct(value):
    """Проценты человеческой записью: 1/5 → «20 %». В условии про станки
    доли читаются процентами легче, чем дробями."""
    return f'{int(sp.Rational(value) * 100)} %'


def _balls(count):
    """«1 шар», «3 шара», «5 шаров» — иначе условие читается как черновик."""
    tail = count % 10, count % 100
    if tail[0] == 1 and tail[1] != 11:
        return 'шар'
    if tail[0] in (2, 3, 4) and tail[1] not in (12, 13, 14):
        return 'шара'
    return 'шаров'


def _coloured(count, one, many):
    """«1 белый шар», «2 белых шара», «5 белых шаров».

    Существительное у каждого цвета своё. Общее на двоих («6 красных и
    1 белых шар») сходится только пока оба числа одной формы, а среди
    коробок есть и «один».
    """
    tail = count % 10, count % 100
    single = tail[0] == 1 and tail[1] != 11
    return f'{count} {one if single else many} {_balls(count)}'


def event_algebra(rng):
    """Четыре клетки: правило сложения, дополнение, де Морган."""
    both = R(rng.choice([1, 2, 3]), 10)
    only_a = R(rng.choice([1, 2, 3]), 10)
    only_b = R(rng.choice([1, 2, 3]), 10)
    if both + only_a + only_b >= 1:
        only_b = R(1, 10)
    space = _venn(both, only_a, only_b)
    want, find, text = rng.choice([
        ('union', A_NAMES + B_NAMES + [], 'P(A \\cup B)'),
        ('neither', ['ab'], "P(A' \\cap B')"),
        ('only_b', ['aB'], "P(B \\cap A')"),
    ])
    find = sorted(set(find)) if want != 'union' else ['AB', 'Ab', 'aB']
    return {
        'prompt': (f'$P(A) = {sp.latex(both + only_a)}$, '
                   f'$P(B) = {sp.latex(both + only_b)}$ и '
                   f'$P(A \\cap B) = {sp.latex(both)}$. '
                   f'Найдите ${text}$.'),
        'answer': sum(space[n] for n in find),
        'check': space_check(space, find),
        'budget_ms': 60_000,
        'note': ('Четыре клетки складываются в единицу. Всё остальное — '
                 'сумма каких-то из них, и формулы нужны только чтобы '
                 'клетки заполнить.'),
    }


def conditional(rng):
    """Условная вероятность: делить на вероятность условия."""
    both = R(1, rng.choice([6, 8, 12]))
    only_a = R(1, rng.choice([3, 4, 6]))
    only_b = R(1, rng.choice([4, 6, 8]))
    if both + only_a + only_b >= 1:
        only_a, only_b = R(1, 6), R(1, 6)
    space = _venn(both, only_a, only_b)
    which = rng.choice(['a_given_b', 'b_given_a', 'a_given_not_b'])
    find, given, text = {
        'a_given_b': (A_NAMES, B_NAMES, 'P(A \\mid B)'),
        'b_given_a': (B_NAMES, A_NAMES, 'P(B \\mid A)'),
        'a_given_not_b': (A_NAMES, NOT_B, "P(A \\mid B')"),
    }[which]
    hit = sum(space[n] for n in set(find) & set(given))
    base = sum(space[n] for n in given)
    return {
        'prompt': (f'$P(A \\cap B) = {sp.latex(both)}$, '
                   f'$P(A \\cap B\') = {sp.latex(only_a)}$ и '
                   f'$P(A\' \\cap B) = {sp.latex(only_b)}$. '
                   f'Найдите ${text}$.'),
        'answer': hit / base,
        'check': space_check(space, find, given=given),
        'budget_ms': 90_000,
        'note': ('Знаменатель — вероятность того, что дано, а не того, '
                 'что ищут. Перепутать их — главный промах темы.'),
    }


def independence(rng):
    """Независимость: два числа, а вердикт следует из них."""
    pa = R(rng.choice([1, 2, 3]), 4)
    pb = R(rng.choice([1, 2, 3]), 5)
    same = rng.choice([True, False])
    both = pa*pb if same else pa*pb + R(1, 20)
    if both > min(pa, pb) or pa + pb - both > 1:
        both = pa*pb
    space = _venn(both, pa - both, pb - both)
    return {
        'prompt': (f'$P(A) = {sp.latex(pa)}$, $P(B) = {sp.latex(pb)}$ и '
                   f'$P(A \\cap B) = {sp.latex(both)}$. Независимы ли $A$ '
                   f'и $B$? Напишите два числа через запятую: сначала '
                   f'$P(A)\\cdot P(B)$, потом $P(A \\cap B)$.'),
        'answer': [pa*pb, both],
        'check': independence_check(space, A_NAMES, B_NAMES),
        'budget_ms': 90_000,
        'note': ('Вердикт без чисел схема оценивания не засчитывает: '
                 '«Both conclusion and reasoning are required».'),
    }


def tree(rng):
    """Дерево: вдоль ветви умножаем, между ветвями складываем."""
    red1, white1 = rng.choice([(5, 2), (3, 4), (6, 1)])
    red2, white2 = rng.choice([(4, 3), (2, 5), (1, 6)])
    n1, n2 = red1 + white1, red2 + white2
    space = {'1red': R(1, 2)*R(red1, n1), '1white': R(1, 2)*R(white1, n1),
             '2red': R(1, 2)*R(red2, n2), '2white': R(1, 2)*R(white2, n2)}
    return {
        'prompt': (f'В первой коробке {_coloured(red1, "красный", "красных")}'
                   f' и {_coloured(white1, "белый", "белых")}, во второй '
                   f'{_coloured(red2, "красный", "красных")} и '
                   f'{_coloured(white2, "белый", "белых")}. Коробку выбирают '
                   f'наугад и вынимают один шар. Найдите вероятность того, '
                   f'что он красный.'),
        'answer': space['1red'] + space['2red'],
        'check': space_check(space, ['1red', '2red']),
        'budget_ms': 90_000,
        'note': ('Вероятность пути — произведение вдоль него, вероятность '
                 'события — сумма по путям.'),
    }


def first_success(rng):
    """Повторные испытания: первый успех на n-м, показатель n − 1."""
    p = R(rng.choice([1, 2, 3]), 10)
    n = rng.choice([3, 4, 5, 6])
    depth = 60
    space = {k: p*(1 - p)**(k - 1) for k in range(1, depth + 1)}
    space['later'] = (1 - p)**depth
    kind = rng.choice(['exactly', 'at_least_one'])
    if kind == 'exactly':
        find = [n]
        prompt = (f'Испытание повторяется независимо, вероятность успеха '
                  f'в каждом ${sp.latex(p)}$. Найдите вероятность того, '
                  f'что первый успех придётся на {n}-е испытание.')
    else:
        find = list(range(1, n + 1))
        prompt = (f'Испытание повторяется независимо, вероятность успеха '
                  f'в каждом ${sp.latex(p)}$. Найдите вероятность того, '
                  f'что за первые {n} испытаний будет хотя бы один успех.')
    return {
        'prompt': prompt,
        'answer': sum(space[k] for k in find),
        'check': space_check(space, find),
        'budget_ms': 90_000,
        'note': ('Первый успех на n-м — это (n − 1) неудача и успех: '
                 'показатель на единицу меньше номера. «Хотя бы один» — '
                 'через дополнение.'),
    }


def _parts(rng):
    """Разбиение совокупности на две-три части со своими долями брака."""
    count = rng.choice([2, 3])
    shares = {2: [R(1, 2), R(1, 2)], 3: [R(1, 2), R(3, 10), R(1, 5)]}[count]
    rates = [R(rng.choice([1, 2, 3, 4]), 10) for _ in range(count)]
    names = ['A', 'B', 'C'][:count]
    space = {}
    for name, share, rate in zip(names, shares, rates):
        space[name + '+'] = share*rate
        space[name + '-'] = share*(1 - rate)
    return names, shares, rates, space


def total_probability(rng):
    """Полная вероятность: доля части на то, что внутри неё."""
    names, shares, rates, space = _parts(rng)
    listing = ', '.join(
        f'станок {n} делает {_pct(s)} изделий и бракует {_pct(r)} из них'
        for n, s, r in zip(names, shares, rates))
    find = [n + '+' for n in names]
    return {
        'prompt': (f'На заводе {listing}. Найдите вероятность того, '
                   f'что наугад взятое изделие бракованное.'),
        'answer': sum(space[n] for n in find),
        'check': space_check(space, find),
        'budget_ms': 90_000,
        'note': ('Каждая часть входит со своим весом. Сложить доли брака '
                 'без весов — стандартный неверный ответ.'),
    }


def bayes(rng):
    """Байес: известно следствие, спрашивают причину."""
    names, shares, rates, space = _parts(rng)
    listing = ', '.join(
        f'станок {n} делает {_pct(s)} изделий и бракует {_pct(r)} из них'
        for n, s, r in zip(names, shares, rates))
    find = [names[0] + '+']
    given = [n + '+' for n in names]
    base = sum(space[n] for n in given)
    return {
        'prompt': (f'На заводе {listing}. Изделие оказалось бракованным. '
                   f'Найдите вероятность того, что его сделал станок '
                   f'{names[0]}.'),
        'answer': space[find[0]] / base,
        'check': space_check(space, find, given=given),
        'budget_ms': 120_000,
        'note': ('Числитель — один путь, знаменатель — полная вероятность '
                 'следствия. Обратная условная здесь выглядит правдоподобно '
                 'и неверна.'),
    }


def without_replacement(rng):
    """Без возвращения: уменьшается и знаменатель, и числитель."""
    good = rng.choice([3, 4, 5, 6])
    bad = rng.choice([2, 3, 4, 5])
    take = rng.choice([2, 3])
    total = good + bad
    space = {}
    for hits in range(take + 1):
        weight = R(1, 1)
        for i in range(hits):
            weight *= R(good - i, total - i)
        for j in range(take - hits):
            weight *= R(bad - j, total - hits - j)
        space[hits] = weight * sp.binomial(take, hits)
    scale = sum(space.values())
    space = {k: v/scale for k, v in space.items()}
    return {
        'prompt': (f'В коробке {_coloured(good, "жёлтый", "жёлтых")} и '
                   f'{_coloured(bad, "красный", "красных")}. '
                   f'Вынимают {take} {_balls(take)} подряд, не возвращая. '
                   f'Найдите вероятность того, что все они жёлтые.'),
        'answer': space[take],
        'check': space_check(space, [take]),
        'budget_ms': 90_000,
        'note': ('На каждом шаге уменьшаются оба: и сколько нужных '
                 'осталось, и сколько всего.'),
    }


def counting_space(rng):
    """Перебор равновозможных исходов: сколько подходит из скольких."""
    faces = rng.choice([4, 6])
    target = rng.choice(['sum', 'max', 'equal'])
    space = {(u, v): R(1, faces**2)
             for u in range(1, faces + 1) for v in range(1, faces + 1)}
    if target == 'sum':
        goal = rng.choice([faces, faces + 1, faces + 2])
        find = [k for k in space if sum(k) == goal]
        text = f'сумма выпавших чисел равна {goal}'
    elif target == 'max':
        goal = rng.choice([2, 3, faces - 1])
        find = [k for k in space if max(k) == goal]
        text = f'наибольшее из выпавших чисел равно {goal}'
    else:
        find = [k for k in space if k[0] == k[1]]
        text = 'выпали одинаковые числа'
    named = {f'{u},{v}': w for (u, v), w in space.items()}
    return {
        'prompt': (f'Две правильные {faces}-гранные кости бросают один раз. '
                   f'Найдите вероятность того, что {text}.'),
        'answer': sum(space[k] for k in find),
        'check': space_check(named, [f'{u},{v}' for u, v in find]),
        'budget_ms': 90_000,
        'note': (f'Исходов {faces**2}, и они упорядочены: (1,2) и (2,1) — '
                 f'разные броски.'),
    }


def unknown_probability(rng):
    """Буква внутри вероятности: составить уравнение и отбраковать корень."""
    k = R(1, rng.choice([2, 3, 4]))
    half = rng.choice([True, False])
    second = k/2 if half else k
    target = (1 - k)*(1 - second)
    shown = sp.nsimplify(target)
    return {
        'prompt': ('Событие происходит в первый раз с вероятностью $k$, '
                   + ('во второй — с вероятностью $\\frac{k}{2}$'
                      if half else 'и во второй тоже с вероятностью $k$')
                   + f', независимо. Вероятность того, что оно не '
                     f'произойдёт ни разу, равна ${sp.latex(shown)}$. '
                     f'Найдите $k$.'),
        'answer': k,
        'check': num_check(float(k), sf=4),
        'budget_ms': 120_000,
        'note': ('У квадратного уравнения два корня, и второй больше '
                 'единицы. Отбросить его — отдельный балл, и его дают '
                 'за сказанную вслух причину.'),
    }


GENERATORS = {
    'D2.event_algebra': event_algebra,
    'D2.conditional': conditional,
    'D2.independence': independence,
    'D2.tree': tree,
    'D2.first_success': first_success,
    'D2.total_probability': total_probability,
    'D2.bayes': bayes,
    'D2.without_replacement': without_replacement,
    'D2.counting_space': counting_space,
    'D2.unknown_probability': unknown_probability,
}
