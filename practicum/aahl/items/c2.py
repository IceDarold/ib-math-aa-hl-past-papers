"""Задачи на счёт для практикума C2: радианная мера, сектор, объёмные тела.

Тема — одно определение и его следствия: угол это дуга, делённая на
радиус. Генераторы держатся того же разреза, что и лестница: первые
четыре меряют готовую фигуру, пятый и шестой её сначала разрезают,
седьмой складывает из кусков, восьмой идёт в обратную сторону — мера
дана, найти фигуру, — девятый выводит круг из плоскости.

Ответ здесь почти всегда десятичный, и число значащих цифр — часть
задачи: экзамен просит три, и `num_check(..., sf=3)` требует ровно
столько же. Там, где ответ выходит точным (угол 2.5, периметр 18),
округление до трёх цифр его не портит.

Числа подбираются так, чтобы ответ брался с калькулятором за один шаг.
Тренируется решение о том, что мерить, а не арифметика.
"""
from __future__ import annotations

import math

from .common import num_check

SECOND = ('секунда', 'секунды', 'секунд')
RADIAN = ('радиан', 'радиана', 'радиан')


def _form(count, forms):
    """Форма существительного после числа: 1 секунда, 2 секунды, 5 секунд."""
    one, few, many = forms
    tail = count % 10, count % 100
    if tail[0] == 1 and tail[1] != 11:
        return one
    if tail[0] in (2, 3, 4) and tail[1] not in (12, 13, 14):
        return few
    return many


def _n(count, forms):
    """«$16$ секунд» — число в формуле, существительное в нужной форме."""
    return f'${count}$ {_form(count, forms)}'


def _num(value, digits=2):
    """Число в условии: без хвоста нулей и без экспоненты."""
    text = f'{round(float(value), digits):g}'
    return text


def _rad(value):
    """«$2.5$ радиана» — после дробного числа родительный единственного,
    после целого обычное склонение: 1 радиан, 2 радиана, 5 радиан.

    Отдельный помощник нужен по той же причине, что _form в D1: писать
    «$4$ радиан» — ровно та же ошибка, что «7 участника».
    """
    number = float(value)
    if number != int(number):
        return f'${_num(value)}$ {RADIAN[1]}'
    return _n(int(number), RADIAN)


ROUNDING = 'Ответ дайте с точностью до трёх значащих цифр.'


def radian_arc(rng):
    """Радианная мера: угол это дуга, делённая на радиус."""
    kind = rng.choice(['angle', 'arc', 'radius', 'degrees'])
    radius = rng.choice([4, 5, 6, 8, 9, 10, 12])
    if kind == 'angle':
        arc = rng.choice([7, 9, 10, 12, 15, 18, 21])
        answer = arc / radius
        prompt = (f'Дуга окружности радиуса ${radius}$ см имеет длину '
                  f'${arc}$ см. Найдите угол, который она стягивает '
                  f'в центре, в радианах.')
        note = ('Радианная мера и есть это отношение: угол — во сколько '
                'раз дуга длиннее радиуса. Формулу s = rθ не нужно '
                'помнить отдельно, она и есть определение.')
    elif kind == 'arc':
        angle = rng.choice([0.6, 0.9, 1.2, 1.5, 1.9, 2.4, 2.8])
        answer = radius * angle
        prompt = (f'Радиус окружности равен ${radius}$ см, а угол '
                  f'в центре — {_rad(angle)}. Найдите длину дуги, '
                  f'которую он стягивает. {ROUNDING}')
        note = ('s = rθ. Если бы угол был дан в градусах, подставлять '
                'его сюда было бы нельзя: в формуле стоит отношение длин, '
                'а не градусы.')
    elif kind == 'radius':
        angle = rng.choice([0.8, 1.25, 1.6, 2.5, 3.2])
        arc = round(radius * angle, 4)
        answer = arc / angle
        prompt = (f'Дуга длиной ${_num(arc, 4)}$ см стягивает в центре угол '
                  f'{_rad(angle)}. Найдите радиус окружности. '
                  f'{ROUNDING}')
        note = 'Из s = rθ радиус находится делением: r = s/θ.'
    else:
        degrees = rng.choice([40, 75, 120, 150, 210, 300])
        answer = radius * degrees * math.pi / 180
        prompt = (f'Радиус окружности равен ${radius}$ см, а угол '
                  f'в центре — ${degrees}^\\circ$. Найдите длину дуги. '
                  f'{ROUNDING}')
        note = ('Сначала градусы в радианы: умножить на π/180. Подставить '
                'градусы прямо в s = rθ — ошибка ровно в 57 раз.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 45_000,
        'note': note,
    }


def angular_rate(rng):
    """Угол, растущий во времени: полный оборот за период."""
    period = rng.choice([8, 10, 12, 15, 16, 20, 24])
    kind = rng.choice(['rate', 'time', 'arc'])
    if kind == 'rate':
        answer = 2 * math.pi / period
        prompt = (f'Стрелка делает один полный оборот за '
                  f'{_n(period, SECOND)}. На какой угол в радианах она '
                  f'поворачивается за одну секунду? {ROUNDING}')
        note = ('Полный оборот это 2π, и он проходится за период: '
                'ω = 2π/T. Дальше угол растёт линейно, α = ωt.')
    elif kind == 'time':
        angle = rng.choice([0.5, 1.2, 2.0, 2.5, 3.0, 4.0])
        answer = angle * period / (2 * math.pi)
        prompt = (f'Стрелка делает один полный оборот за '
                  f'{_n(period, SECOND)}. За сколько секунд она '
                  f'повернётся на угол {_rad(angle)}? {ROUNDING}')
        note = ('Время это угол, делённый на скорость: t = α/ω, где '
                'ω = 2π/T. Числитель и знаменатель обязаны быть в одних '
                'единицах — в радианах.')
    else:
        radius = rng.choice([3, 5, 8, 10])
        seconds = rng.choice([2, 3, 5, 7])
        answer = radius * 2 * math.pi * seconds / period
        prompt = (f'Колесо радиуса ${radius}$ см делает один оборот за '
                  f'{_n(period, SECOND)}. Какой путь пройдёт точка на его '
                  f'ободе за {_n(seconds, SECOND)}? {ROUNDING}')
        note = ('Сначала угол: α = 2πt/T. Потом дуга: s = rα. Путь точки '
                'обода — это и есть длина пройденной ею дуги.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 60_000,
        'note': note,
    }


def sector_perimeter(rng):
    """Периметр сектора: дуга и два радиуса, а не одна дуга."""
    kind = rng.choice(['plain', 'angle', 'radius'])
    radius = rng.choice([4, 5, 6, 7, 9, 12])
    angle = rng.choice([0.7, 1.1, 1.4, 2.0, 2.5, 3.0])
    if kind == 'plain':
        answer = radius * angle + 2 * radius
        prompt = (f'Найдите периметр сектора радиуса ${radius}$ см с углом '
                  f'{_rad(angle)} в центре. {ROUNDING}')
        note = ('Периметр обходит всю границу: дуга rθ и два радиуса. '
                'Самая частая потеря балла в теме — посчитать одну дугу.')
    elif kind == 'angle':
        perimeter = round(radius * angle + 2 * radius, 4)
        answer = perimeter / radius - 2
        prompt = (f'Периметр сектора радиуса ${radius}$ см равен '
                  f'${_num(perimeter, 4)}$ см. Найдите угол в центре, '
                  f'в радианах. {ROUNDING}')
        note = ('Из P = rθ + 2r сначала вычитают два радиуса и только '
                'потом делят: θ = (P − 2r)/r.')
    else:
        perimeter = round(radius * angle + 2 * radius, 4)
        answer = perimeter / (angle + 2)
        prompt = (f'Периметр сектора равен ${_num(perimeter, 4)}$ см, '
                  f'а угол в центре — {_rad(angle)}. Найдите '
                  f'радиус. {ROUNDING}')
        note = ('P = rθ + 2r = r(θ + 2), и радиус выносится за скобку: '
                'r = P/(θ + 2).')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 60_000,
        'note': note,
    }


def sector_area(rng):
    """Площадь сектора: половина квадрата радиуса на угол."""
    kind = rng.choice(['plain', 'reflex', 'degrees'])
    radius = rng.choice([4, 5, 6, 8, 9, 11])
    if kind == 'plain':
        angle = rng.choice([0.8, 1.3, 1.9, 2.2, 2.7])
        answer = radius ** 2 * angle / 2
        prompt = (f'Найдите площадь сектора радиуса ${radius}$ см с углом '
                  f'{_rad(angle)} в центре. {ROUNDING}')
        note = ('A = ½r²θ. Формула получается из доли круга: сектор это '
                'θ/2π от πr².')
    elif kind == 'reflex':
        angle = rng.choice([1.1, 1.6, 2.0, 2.4])
        answer = radius ** 2 * (2 * math.pi - angle) / 2
        prompt = (f'Точки $A$ и $B$ лежат на окружности радиуса '
                  f'${radius}$ см с центром $O$, и угол $A\\hat{{O}}B$ '
                  f'равен {_rad(angle)}. Найдите площадь '
                  f'большего из двух секторов. {ROUNDING}')
        note = ('Большему сектору отвечает не тот угол, что подписан на '
                'чертеже, а 2π минус он. Второй путь: весь круг πr² минус '
                'меньший сектор — ответ тот же.')
    else:
        degrees = rng.choice([45, 100, 135, 200, 240, 315])
        answer = radius ** 2 * (degrees * math.pi / 180) / 2
        prompt = (f'Найдите площадь сектора радиуса ${radius}$ см с углом '
                  f'${degrees}^\\circ$ в центре. {ROUNDING}')
        note = ('Либо перевести угол в радианы и взять ½r²θ, либо взять '
                'долю круга: (градусы/360)·πr². Схема оценивания '
                'принимает оба.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 45_000,
        'note': note,
    }


def chord_half_angle(rng):
    """Хорда и половинный угол: перпендикуляр из центра делит всё пополам."""
    kind = rng.choice(['chord', 'angle', 'distance'])
    radius = rng.choice([5, 6, 8, 10, 12, 13])
    if kind == 'chord':
        angle = rng.choice([0.9, 1.3, 1.8, 2.1, 2.6])
        answer = 2 * radius * math.sin(angle / 2)
        prompt = (f'Точки $A$ и $B$ лежат на окружности радиуса '
                  f'${radius}$ см, и угол $A\\hat{{O}}B$ равен '
                  f'{_rad(angle)}. Найдите длину хорды $[AB]$. '
                  f'{ROUNDING}')
        note = ('Перпендикуляр из центра делит хорду и угол пополам, и '
                'остаётся прямоугольный треугольник: AB = 2r sin(θ/2). '
                'Теорема косинусов даёт то же число.')
    elif kind == 'angle':
        angle = rng.choice([0.9, 1.3, 1.8, 2.1, 2.6])
        chord = round(2 * radius * math.sin(angle / 2), 4)
        answer = 2 * math.asin(chord / (2 * radius))
        prompt = (f'Хорда длиной ${_num(chord, 4)}$ см стягивает '
                  f'окружность радиуса ${radius}$ см. Найдите угол, под '
                  f'которым она видна из центра, в радианах. {ROUNDING}')
        note = ('sin(θ/2) = (AB/2)/r, откуда θ = 2 arcsin(AB/2r). '
                'Удвоение — отдельный балл: arcsin даёт половину угла.')
    else:
        distance = rng.choice([3, 4, 5, 7, 9])
        distance = min(distance, radius - 1)
        answer = 2 * math.acos(distance / radius)
        prompt = (f'Расстояние от центра окружности радиуса ${radius}$ см '
                  f'до хорды равно ${distance}$ см. Найдите угол, под '
                  f'которым эта хорда видна из центра, в радианах. '
                  f'{ROUNDING}')
        note = ('cos(θ/2) = d/r, откуда θ = 2 arccos(d/r). Это тот самый '
                'ход, которым в майской задаче 2024 года находят время '
                'полива отрезка пути.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 75_000,
        'note': note,
    }


def segment_area(rng):
    """Площадь сегмента: сектор без треугольника."""
    radius = rng.choice([4, 5, 6, 8, 10, 12])
    angle = rng.choice([1.0, 1.4, 1.9, 2.3, 2.8, 3.1])
    kind = rng.choice(['segment', 'segment', 'major'])
    if kind == 'segment':
        answer = radius ** 2 * (angle - math.sin(angle)) / 2
        prompt = (f'Хорда стягивает в окружности радиуса ${radius}$ см '
                  f'угол {_rad(angle)}. Найдите площадь меньшего '
                  f'из двух сегментов, на которые она делит круг. '
                  f'{ROUNDING}')
        note = ('Сегмент это сектор без треугольника: '
                '½r²θ − ½r² sin θ = ½r²(θ − sin θ). Три числа в одной '
                'строке, и схема оценивания различает все три.')
    else:
        answer = radius ** 2 * (2 * math.pi - angle + math.sin(angle)) / 2
        prompt = (f'Хорда стягивает в окружности радиуса ${radius}$ см '
                  f'угол {_rad(angle)}. Найдите площадь большего '
                  f'из двух сегментов, на которые она делит круг. '
                  f'{ROUNDING}')
        note = ('Больший сегмент — это больший сектор плюс тот же '
                'треугольник: ½r²(2π − θ) + ½r² sin θ. Или весь круг '
                'минус меньший сегмент.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 75_000,
        'note': note,
    }


def composite_region(rng):
    """Составная область: разрезать на части, у которых мера известна."""
    kind = rng.choice(['ring', 'polygon', 'square'])
    if kind == 'ring':
        inner = rng.choice([3, 4, 5, 6])
        outer = inner + rng.choice([2, 3, 4, 5])
        angle = rng.choice([1.2, 1.8, 2.5, 4.0, 5.2])
        answer = angle * (outer ** 2 - inner ** 2) / 2
        prompt = (f'Две окружности с общим центром имеют радиусы '
                  f'${inner}$ см и ${outer}$ см. Найдите площадь части '
                  f'кольца между ними, отвечающей углу {_rad(angle)} '
                  f'в центре. {ROUNDING}')
        note = ('Это разность двух секторов с одним и тем же углом: '
                '½θR² − ½θr² = ½θ(R² − r²). Угол общий, и терять его '
                'нельзя ни в одном из двух слагаемых.')
    elif kind == 'polygon':
        sides = rng.choice([5, 6, 7, 8])
        radius = rng.choice([4, 5, 6, 9, 10])
        step = 2 * math.pi / sides
        answer = sides * radius ** 2 * (step - math.sin(step)) / 2
        prompt = (f'В окружность радиуса ${radius}$ см вписан правильный '
                  f'${sides}$-угольник. Найдите суммарную площадь частей '
                  f'круга, лежащих вне многоугольника. {ROUNDING}')
        note = ('Таких частей столько же, сколько сторон, и каждая — '
                'сегмент при угле 2π/n. Множитель n и есть тот балл, '
                'который теряют чаще всего.')
    else:
        side = rng.choice([6, 8, 10, 12])
        answer = side ** 2 - math.pi * side ** 2 / 4
        prompt = (f'Из квадрата со стороной ${side}$ см вырезали четверть '
                  f'круга радиуса ${side}$ см с центром в одной из его '
                  f'вершин. Найдите площадь остатка. {ROUNDING}')
        note = ('Квадрат минус сектор с углом π/2: a² − ¼πa². Разрез '
                'делается на чертеже, и после него считать уже нечего.')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 90_000,
        'note': note,
    }


def unknown_from_conditions(rng):
    """Мера дана, фигура — нет: две связи сводятся к одному уравнению."""
    kind = rng.choice(['quadratic', 'quadratic', 'ratio'])
    if kind == 'quadratic':
        # У 2r² − Pr + 2A = 0 корни перемножаются в A и складываются в P/2,
        # поэтому второй корень это A/r, и он тоже задаёт настоящий сектор.
        # Условие обязано выбрать один из двух — как в экзаменационной
        # задаче, где лишний корень отбрасывают по смыслу, а не по алгебре.
        while True:
            radius = rng.choice([3, 4, 5, 6, 8, 9])
            angle = rng.choice([0.5, 1.0, 1.5, 2.5, 3.0, 4.0])
            perimeter = radius * (angle + 2)
            area = radius ** 2 * angle / 2
            other = area / radius
            if other <= 0 or abs(other - radius) < 0.5:
                continue
            twin = perimeter / other - 2
            if not 0 < twin < 2 * math.pi or abs(twin - angle) < 0.5:
                continue
            break
        side = 'больше' if angle > twin else 'меньше'
        edge = round((angle + twin) / 2, 2)
        answer = radius
        prompt = (f'Периметр сектора равен ${_num(perimeter, 4)}$ см, '
                  f'а его площадь — ${_num(area, 4)}$ см$^2$. Известно, '
                  f'что угол сектора {side} {_rad(edge)}. Найдите '
                  f'радиус. {ROUNDING}')
        note = ('Из периметра rθ = P − 2r; подставив это в площадь '
                '½r·(rθ), получают 2r² − Pr + 2A = 0. Корня два, и оба '
                'дают настоящий сектор — выбирает между ними условие '
                'задачи, а не арифметика.')
        budget = 150_000
    else:
        first, second = rng.choice([(2, 5), (1, 2), (3, 5), (4, 5), (5, 4)])
        # ½r²(θ − sin θ) : ½r² sin θ = first : second, радиус сокращается,
        # и остаётся θ = (1 + first/second)·sin θ.
        factor = 1 + first / second
        low, high = 1e-6, math.pi
        for _ in range(200):
            mid = (low + high) / 2
            if mid - factor * math.sin(mid) < 0:
                low = mid
            else:
                high = mid
        answer = (low + high) / 2
        prompt = (f'Хорда делит сектор на сегмент и треугольник, и их '
                  f'площади относятся как ${first}:{second}$. Найдите '
                  f'угол сектора в радианах. {ROUNDING}')
        note = ('½r²(θ − sin θ) : ½r² sin θ — радиус сокращается, и '
                'остаётся θ = (1 + k) sin θ, где k это отношение. '
                'Алгебраически такое не решается: только графиком или '
                'решателем.')
        budget = 150_000
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': budget,
        'note': note,
    }


def cone_from_circle(rng):
    """Конус: дуга сектора становится окружностью основания."""
    kind = rng.choice(['base', 'volume', 'surface', 'slant'])
    if kind == 'base':
        slant = rng.choice([6, 9, 12, 15, 18])
        angle = rng.choice([1.5, 2.0, 2.5, 3.0, 3.5])
        answer = slant * angle / (2 * math.pi)
        prompt = (f'Из бумаги вырезан сектор радиуса ${slant}$ см с углом '
                  f'{_rad(angle)} и свёрнут в конус без '
                  f'основания. Найдите радиус основания. {ROUNDING}')
        note = ('При сворачивании дуга становится окружностью основания: '
                'lθ = 2πR. Радиус самого сектора стал образующей, а не '
                'радиусом основания — это и путают.')
    elif kind == 'volume':
        radius = rng.choice([2, 3, 4, 5, 6])
        height = rng.choice([5, 7, 9, 12, 15])
        answer = math.pi * radius ** 2 * height / 3
        prompt = (f'Радиус основания конуса равен ${radius}$ см, '
                  f'а высота — ${height}$ см. Найдите объём. {ROUNDING}')
        note = ('V = ⅓πR²h. Без трети получился бы цилиндр той же высоты '
                '— ровно втрое больше.')
    elif kind == 'surface':
        radius = rng.choice([2, 3, 4, 5, 6])
        slant = radius + rng.choice([2, 3, 4, 6])
        answer = math.pi * radius ** 2 + math.pi * radius * slant
        prompt = (f'Радиус основания конуса равен ${radius}$ см, '
                  f'а образующая — ${slant}$ см. Найдите площадь полной '
                  f'поверхности. {ROUNDING}')
        note = ('Полная поверхность это основание плюс боковая часть: '
                'πR² + πRl. Забыть основание — потерять πR².')
    else:
        radius = rng.choice([3, 4, 5, 6, 8])
        height = rng.choice([4, 6, 9, 12, 15])
        answer = math.hypot(radius, height)
        prompt = (f'Радиус основания конуса равен ${radius}$ см, '
                  f'а высота — ${height}$ см. Найдите образующую. '
                  f'{ROUNDING}')
        note = ('Радиус, высота и образующая — катеты и гипотенуза '
                'осевого сечения: l² = R² + h².')
    return {
        'prompt': prompt,
        'answer': answer,
        'check': num_check(answer, sf=3),
        'budget_ms': 60_000,
        'note': note,
    }


GENERATORS = {
    'C2.radian_arc': radian_arc,
    'C2.angular_rate': angular_rate,
    'C2.sector_perimeter': sector_perimeter,
    'C2.sector_area': sector_area,
    'C2.chord_half_angle': chord_half_angle,
    'C2.segment_area': segment_area,
    'C2.composite_region': composite_region,
    'C2.unknown_from_conditions': unknown_from_conditions,
    'C2.cone_from_circle': cone_from_circle,
}
