"""Геометрия: треугольник по данным (C1) и фигура — длина, площадь, объём (C2).
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t


# --- треугольник ------------------------------------------------------------
#
# Пятый раз серии нужен свой ответ на вопрос «когда два ответа одинаковы».
# A3 сверял значения, A4 — форму записи, A8 — множества, B1 — уравнения.
# Здесь ответ это **конфигурация**: длина стороны или величина угла сами
# по себе ничего не значат, значение имеет треугольник, частью которого
# они являются.
#
# Отсюда устройство проверки. solve_triangle достраивает треугольник
# из данных условия — и в неоднозначном случае (две стороны и угол против
# меньшей) достраивает **два**. verify_triangle не хранит эталона: он
# смотрит, согласуются ли ваши части с данными, и говорит, если данные
# допускают ещё один треугольник, а выбран не он.

# Стороны a, b, c лежат против углов A, B, C — как во всех формулах IB.
_SIDES, _ANGLES = ('a', 'b', 'c'), ('A', 'B', 'C')


def _tri_complete(sides, angles, deg):
    """Собирает решение в словарь, переводя углы обратно в градусы."""
    k = 180 / math.pi if deg else 1
    out = {}
    for name, value in zip(_SIDES, sides):
        out[name] = value
    for name, value in zip(_ANGLES, angles):
        out[name] = value * k
    return out


def solve_triangle(a=None, b=None, c=None, A=None, B=None, C=None, deg=True):
    """Достраивает треугольник по трём известным частям.

    Возвращает список решений: обычно одно, в неоднозначном случае два,
    при несовместных данных — пустой список. Углы по умолчанию
    в градусах; deg=False переключает на радианы.

    Функция нужна не только проверке. Ею удобно смотреть, сколько
    треугольников допускает условие, — а это и есть главный вопрос темы
    в вопросах вида «find the smallest possible perimeter».
    """
    k = math.pi / 180 if deg else 1
    sides = [None if v is None else float(v) for v in (a, b, c)]
    angles = [None if v is None else float(v) * k for v in (A, B, C)]
    if any(v is not None and v <= 0 for v in sides + angles):
        return []
    if sum(v is not None for v in angles) == 3 and \
            abs(sum(angles) - math.pi) > 1e-9:
        return []
    known_s = [i for i, v in enumerate(sides) if v is not None]
    known_a = [i for i, v in enumerate(angles) if v is not None]
    if len(known_s) + len(known_a) < 3 or not known_s:
        return []

    # Три угла задают форму, но не размер: треугольник не определён.
    if len(known_s) == 0:
        return []

    def by_cosine(i):
        """Угол i по трём сторонам."""
        p, q, r = sides[i], sides[(i + 1) % 3], sides[(i + 2) % 3]
        cos = (q * q + r * r - p * p) / (2 * q * r)
        return math.acos(max(-1.0, min(1.0, cos)))

    def finish_sss():
        if not all(sides):
            return []
        p, q, r = sorted(sides)
        if p + q <= r + 1e-12:
            return []
        return [_tri_complete(sides, [by_cosine(i) for i in range(3)], deg)]

    if len(known_s) == 3:
        return finish_sss()

    if len(known_s) == 2:
        missing = ({0, 1, 2} - set(known_s)).pop()
        if angles[missing] is not None:            # SAS: угол между сторонами
            q, r = sides[(missing + 1) % 3], sides[(missing + 2) % 3]
            sides[missing] = math.sqrt(q * q + r * r
                                       - 2 * q * r * math.cos(angles[missing]))
            return finish_sss()
        # SSA: угол лежит против одной из известных сторон
        i = known_a[0]
        j = [t for t in known_s if t != i]
        if i not in known_s or not j:
            return []
        j = j[0]
        ratio = sides[j] * math.sin(angles[i]) / sides[i]
        if ratio > 1 + 1e-12:
            return []
        ratio = max(-1.0, min(1.0, ratio))
        out = []
        for angle_j in {math.asin(ratio), math.pi - math.asin(ratio)}:
            rest = math.pi - angles[i] - angle_j
            if rest <= 1e-9:
                continue
            new_a = list(angles)
            new_a[j] = angle_j
            new_a[({0, 1, 2} - {i, j}).pop()] = rest
            new_s = list(sides)
            miss = ({0, 1, 2} - set(known_s)).pop()
            new_s[miss] = sides[i] * math.sin(rest if miss not in (i, j)
                                              else new_a[miss]) / math.sin(angles[i])
            out.append(_tri_complete(new_s, new_a, deg))
        out.sort(key=lambda t: t[_ANGLES[j]])
        return out

    # Одна сторона и два угла: третий угол из суммы, стороны по синусам.
    third = ({0, 1, 2} - set(known_a)).pop()
    angles[third] = math.pi - sum(angles[i] for i in known_a)
    if angles[third] <= 1e-9:
        return []
    i = known_s[0]
    for j in range(3):
        if sides[j] is None:
            sides[j] = sides[i] * math.sin(angles[j]) / math.sin(angles[i])
    return [_tri_complete(sides, angles, deg)]


def verify_triangle(label, got, tol=5e-3, deg=True, **known):
    """Найденные части треугольника проверяются достраиванием, а не эталоном.

    got — словарь того, что вы нашли: {'c': 8.24, 'B': 41.2}; known — то,
    что дано в условии. Треугольник строится из данных, и ваши части
    сверяются с ним.

    Если данные допускают два треугольника, проверка об этом скажет:
    выбор между ними — часть задачи, и его делает условие, а не алгебра.
    """
    if _blank(label, *got.values(), *known.values()):
        return False
    got = {key: float(value) for key, value in got.items()}
    solutions = solve_triangle(deg=deg, **known)
    if not solutions:
        print(f"{NO} {label}: " + _t(
            "по этим данным треугольника не существует — проверьте условие",
            "no triangle exists with this data — check the question"))
        return False

    def fits(sol):
        return all(abs(sol[key] - value) <= tol * max(1.0, abs(sol[key]))
                   for key, value in got.items() if key in sol)

    matched = [sol for sol in solutions if fits(sol)]
    if not matched:
        best = min(solutions,
                   key=lambda sol: max(abs(sol[key] - value)
                                       for key, value in got.items()))
        bad = max(got, key=lambda key: abs(best[key] - got[key]))
        print(f"{NO} {label}: " + _t(
            f"{bad} = {got[bad]:g} с данными не согласуется — треугольник "
            f"с такими частями не замыкается",
            f"{bad} = {got[bad]:g} is inconsistent with the data — "
            f"a triangle with these parts does not close"))
        return False
    shown = ', '.join(f"{key} = {value:g}" for key, value in got.items())
    if len(solutions) > 1:
        print(f"{OK} {label}: {shown} — " + _t(
            f"но данные допускают {len(solutions)} треугольника, и ваш "
            f"ответ отвечает одному из них. Условие выбирает, какой именно",
            f"but the data admits {len(solutions)} triangles and your "
            f"answer fits one of them. The question decides which"))
    else:
        print(f"{OK} {label}: {shown}")
    return True


# ------------------------------------------------------------------- фигура
#
# Пятнадцатое понятие равенства ответов. У счёта ответом было целое число,
# и проверялось оно перебором объектов; здесь ответ — длина, площадь или
# объём, и проверяется он тем же ходом, доведённым до геометрии: **фигуру
# измеряют**.
#
# Эталона снова нет. Ноутбук описывает проверке не ответ, а границу фигуры:
# из чего она сложена и где проходит. Дуга задаётся центром, радиусом и
# двумя углами; отрезок — двумя концами. Дальше площадь берётся формулой
# Грина по этой границе, длина — суммой кусков, объём тела вращения —
# теоремой Паппа. Ни одна из трёх мер не знает, каким способом её считал
# экзаменуемый, и ½r²(θ − sin θ) для неё не существует.
#
# Возражение к этому то же, что к перебору в D1: описание границы — это
# половина решения, и его видно в ячейке. Ответ тот же. Проверке передают
# **условие, переписанное на Python**: «сектор радиуса 12 с углом 2,08 и
# прямоугольник 10 на w» — это чертёж из билета, а не метод. Разложение
# фигуры на куски и правда подсказка, и самая заметная она в задании 12,
# где чертёж без подписей разобрать труднее, чем с ними. Взамен получено
# то, ради чего всё затевалось: ни один ответ этой темы не сверяется
# с записанным числом, и любая верная форма — 3549π/16, 696.844, 697 —
# проходит одинаково.
#
# Ещё одно: границу разрешено строить из собственных ответов ученика.
# В задании 12 ширина жёлоба считается из найденного им угла, в задании 13
# высота конуса — из найденной им образующей. Тогда неверный первый пункт
# не роняет второй, а это ровно то, что в схеме оценивания называется
# follow through.

_FIG_TOL = 5e-3          # три значащие цифры — столько же принимает экзамен
_FIG_EPS = 1e-7          # с такой точностью граница обязана замкнуться
_FIG_SAMPLES = 64        # столько точек берётся с каждого куска границы


def seg(start, end):
    """Кусок границы: отрезок из точки в точку."""
    return ('seg', tuple(start), tuple(end))


def arc(centre, radius, start, end):
    """Кусок границы: дуга окружности.

    centre и radius задают окружность, start и end — углы в радианах,
    отсчитанные как обычно от направления оси x. Обход идёт против
    часовой стрелки, когда end больше start, и по часовой, когда меньше;
    величина |end − start| и есть тот угол сектора, который в задаче
    называется θ.
    """
    return ('arc', tuple(centre), radius, start, end)


def undrawn(*values):
    """Пустая граница, если хоть один ответ ещё не заполнен, иначе None.

    Чертёж в этой теме постоянно строят из ответа: сектор — из найденного
    угла, конус — из найденной образующей. Пока ответа нет, строить не из
    чего, а ноутбук обязан проходиться сверху вниз и пустым. Отсюда
    короткая заглушка в начале каждой такой функции:

        def sector(radius, start, end):
            return undrawn(radius, start, end) or (seg(...), arc(...), ...)
    """
    if any(value is Ellipsis for value in values):
        return (seg((Ellipsis, Ellipsis), (Ellipsis, Ellipsis)),)
    return None


def cone(radius, height=None, slant=None):
    """Осевое сечение прямого конуса — треугольник, который вращают.

    Задаются любые две величины из трёх: радиус основания, высота,
    образующая. Третью проверка достраивает по Пифагору сама, и в
    ячейке её не видно: у задания «найдите объём» ответом является
    объём, а не высота.

    Ось вращения — ось x, и вершина конуса стоит в начале координат.
    """
    # Сечение строят из ответа предыдущего пункта, и он бывает ещё пуст.
    nothing = undrawn(radius, height, slant)
    if nothing:
        return nothing
    r = sp.sympify(radius)
    if height is None and slant is None:
        raise ValueError(_t('cone: нужна высота или образующая',
                            'cone: give a height or a slant height'))
    h = (sp.sqrt(sp.sympify(slant) ** 2 - r ** 2) if height is None
         else sp.sympify(height))
    return (seg((0, 0), (h, 0)), seg((h, 0), (h, r)), seg((h, r), (0, 0)))


def _pt(point):
    """Точка плоскости: пара чисел."""
    if not isinstance(point, (list, tuple)) or len(point) != 2:
        raise ValueError(_t('точка это пара чисел',
                            'a point is a pair of numbers'))
    return (sp.sympify(point[0]), sp.sympify(point[1]))


def _piece(item):
    """Кусок границы в разобранном виде."""
    if not isinstance(item, (list, tuple)) or not item:
        raise ValueError(_t('граница складывается из seg и arc',
                            'a boundary is made of seg and arc'))
    if item[0] == 'seg':
        return ('seg', _pt(item[1]), _pt(item[2]))
    if item[0] == 'arc':
        return ('arc', _pt(item[1]), sp.sympify(item[2]),
                sp.sympify(item[3]), sp.sympify(item[4]))
    raise ValueError(_t('кусок границы это seg или arc',
                        'a boundary piece is either seg or arc'))


def _ends(piece):
    """Начало и конец куска."""
    if piece[0] == 'seg':
        return piece[1], piece[2]
    _, (cx, cy), r, a, b = piece
    return ((cx + r * sp.cos(a), cy + r * sp.sin(a)),
            (cx + r * sp.cos(b), cy + r * sp.sin(b)))


def _at(piece, share):
    """Точка куска на доле share его длины."""
    if piece[0] == 'seg':
        (x1, y1), (x2, y2) = piece[1], piece[2]
        return (x1 + share * (x2 - x1), y1 + share * (y2 - y1))
    _, (cx, cy), r, a, b = piece
    angle = a + share * (b - a)
    return (cx + r * sp.cos(angle), cy + r * sp.sin(angle))


def _same(one, two, tol=_FIG_EPS):
    """Совпадают ли две точки численно."""
    try:
        return all(abs(float(p - q)) <= tol for p, q in zip(one, two))
    except TypeError:
        return False


def _area_term(piece):
    """Вклад куска в ½∮(x dy − y dx) — формула Грина."""
    if piece[0] == 'seg':
        (x1, y1), (x2, y2) = piece[1], piece[2]
        return (x1 * y2 - x2 * y1) / 2
    _, (cx, cy), r, a, b = piece
    return (r ** 2 * (b - a)
            + r * (cx * (sp.sin(b) - sp.sin(a))
                   - cy * (sp.cos(b) - sp.cos(a)))) / 2


def _length_term(piece):
    """Длина куска."""
    if piece[0] == 'seg':
        (x1, y1), (x2, y2) = piece[1], piece[2]
        return sp.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return piece[2] * sp.Abs(piece[4] - piece[3])


def _moment_term(piece):
    """Вклад куска в ∮ y² dx — из него теорема Паппа берёт объём."""
    if piece[0] == 'seg':
        (x1, y1), (x2, y2) = piece[1], piece[2]
        return (x2 - x1) * (y1 ** 2 + y1 * y2 + y2 ** 2) / 3
    _, (cx, cy), r, a, b = piece
    angle = sp.Dummy('angle')
    height = cy + r * sp.sin(angle)
    return sp.integrate(height ** 2 * (-r * sp.sin(angle)), (angle, a, b))


def _sector_terms(pieces):
    """Секторы и треугольники, натянутые на каждую дугу границы.

    Сегмент — это сектор без треугольника, и обе половины этой разности
    называются в схемах оценивания отдельными строками. Обе и считаем:
    ответ, равный одной из них, — не «мимо», а известная подмена.
    """
    sectors, triangles = [], []
    for piece in pieces:
        if piece[0] == 'arc':
            _, _, r, a, b = piece
            sweep = sp.Abs(b - a)
            sectors.append(r ** 2 * sweep / 2)
            triangles.append(r ** 2 * sp.Abs(sp.sin(sweep)) / 2)
    return _measure(sectors or [0]), _measure(triangles or [0])


def _chorded(pieces):
    """Та же граница, но каждая дуга заменена своей хордой."""
    out = []
    for piece in pieces:
        if piece[0] == 'seg':
            out.append(piece)
        else:
            start, end = _ends(piece)
            out.append(('seg', start, end))
    return out


def _flipped(pieces):
    """Та же граница, но каждая дуга взята с другой стороны окружности."""
    out = []
    for piece in pieces:
        if piece[0] == 'seg':
            out.append(piece)
            continue
        _, centre, r, a, b = piece
        sweep = b - a
        step = 2 * sp.pi * (1 if float(sweep) > 0 else -1)
        out.append(('arc', centre, r, a, a + sweep - step))
    return out


def _loops(parsed):
    """Куски, разложенные по замкнутым контурам.

    Контуров бывает больше одного, и это не редкость темы: пять сегментов
    вокруг вписанного пятиугольника — пять отдельных контуров, а кольцо —
    два, внешний и внутренний. Каждый следующий кусок обязан начинаться
    там, где кончился предыдущий; как только обход вернулся в начало
    контура, начинается следующий.
    """
    out, current = [], []
    for piece in parsed:
        if current and not _same(_ends(current[-1])[1], _ends(piece)[0]):
            return None
        current.append(piece)
        if _same(_ends(current[-1])[1], _ends(current[0])[0]):
            out.append(current)
            current = []
    return None if current else out


def _figure(label, pieces, closed=True):
    """Разбор границы. Возвращает список кусков или None с сообщением."""
    if not pieces:
        print(f"{NO} {label}: " + _t("граница не описана",
                                     "no boundary given"))
        return None
    try:
        parsed = [_piece(item) for item in pieces]
    except ValueError as bad:
        print(f"{NO} {label}: {bad}")
        return None
    if closed:
        if _loops(parsed) is None:
            print(f"{NO} {label}: " + _t(
                "граница не замкнулась: контур должен вернуться туда, "
                "откуда вышел, а куски — стыковаться концами",
                "the boundary does not close: a contour has to come back "
                "where it started, and the pieces have to meet end to end"))
            return None
        return parsed
    for before, after in zip(parsed, parsed[1:]):
        if not _same(_ends(before)[1], _ends(after)[0]):
            print(f"{NO} {label}: " + _t(
                "куски линии не стыкуются: конец одного не совпадает "
                "с началом следующего",
                "the line does not join up: one piece ends where the "
                "next does not begin"))
            return None
    return parsed


def _repeats(parsed, term):
    """Сколько одинаковых контуров в границе и сколько мерит один.

    Пять сегментов вокруг вписанного пятиугольника — пять одинаковых
    контуров, и самый частый промах здесь не в сегменте, а в том, что
    его забыли умножить на пять.
    """
    loops = _loops(parsed) or []
    if len(loops) < 2:
        return 0, None
    sizes = [sp.Abs(_measure([term(p) for p in loop])) for loop in loops]
    # Сравнение здесь численное: контуры пятиугольника задаются разными
    # углами, и simplify их равенство не доказывает, хотя оно очевидно.
    if any(not _near(size, sizes[0], _FIG_EPS) for size in sizes[1:]):
        return 0, None
    return len(loops), sizes[0]


def _measure(terms):
    """Сумма вкладов, приведённая к числу."""
    return sp.simplify(sp.Add(*terms))


def _near(got, want, tol):
    """Сходится ли ответ с мерой в пределах допуска."""
    try:
        one, two = float(got), float(want)
    except (TypeError, ValueError):
        return False
    return abs(one - two) <= tol * max(1.0, abs(two))


def _as_measure(label, got):
    """Ответ-мера как число, или None."""
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        value = None
    if value is None or getattr(value, 'free_symbols', set()) \
            or not value.is_number or not value.is_real:
        print(f"{NO} {label}: " + _t("длина, площадь и объём это числа",
                                     "a length, an area and a volume "
                                     "are numbers"))
        return None
    return value


def _report_measure(label, got, want, slips, tol, exact):
    """Общий разбор ответа-меры: сходится, известный промах или мимо."""
    if exact and sp.sympify(got).atoms(sp.Float):
        print(f"{NO} {label}: " + _t(
            "это десятичная запись, а вопрос просит точное значение",
            "this is a decimal, and the question asks for the exact value"))
        return False
    if _near(got, want, tol):
        print(f"{OK} {label}")
        return True
    for what, value in slips.items():
        if value is not None and _near(got, value, tol):
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t("у фигуры из условия мера другая",
                                 "the figure in the question does not "
                                 "measure that"))
    return False


def verify_area(label, got, *pieces, tol=_FIG_TOL, exact=False):
    """Ответ — площадь, и она берётся с самой фигуры.

    pieces — граница фигуры, обойдённая по кругу: arc(...) и seg(...)
    подряд, конец каждого куска в начале следующего, последний замыкается
    на первый. Площадь считается формулой Грина по этому контуру, поэтому
    ни ½r²θ, ни ½r²(θ − sin θ) проверке не нужны: она их не знает.

    Промахи называются тем же контуром. Площадь того же контура с хордами
    вместо дуг — это «сегмент забыт»; разность между ними — «взят только
    сегмент»; контур с дугами, взятыми с другой стороны окружности, —
    «перепутаны меньшая и большая часть».
    """
    if _blank(label, got, *pieces):
        return False
    answer = _as_measure(label, got)
    if answer is None:
        return False
    parsed = _figure(label, pieces)
    if parsed is None:
        return False
    want = sp.Abs(_measure([_area_term(p) for p in parsed]))
    if want == 0:
        print(f"{NO} {label}: " + _t("контур не охватывает площади",
                                     "the boundary encloses nothing"))
        return False
    chords = sp.Abs(_measure([_area_term(p) for p in _chorded(parsed)]))
    other = sp.Abs(_measure([_area_term(p) for p in _flipped(parsed)]))
    slips = {}
    if not _near(chords, want, _FIG_EPS):
        slips[_t("дуга заменена хордой: сегмент между ними не учтён",
                 "the arc has been read as a chord: the segment between "
                 "them is missing")] = chords
        slips[_t("это только сегмент, а не вся фигура",
                 "that is the segment alone, not the whole figure")] = \
            sp.Abs(want - chords)
    if not _near(other, want, _FIG_EPS):
        slips[_t("дуга взята с другой стороны окружности: меньшая часть "
                 "вместо большей или наоборот",
                 "the arc has been taken the other way round the circle: "
                 "the minor part instead of the major, or the other way")] \
            = other
    sectors, triangles = _sector_terms(parsed)
    if sectors != 0 and not _near(sectors, want, _FIG_EPS):
        slips[_t("это сектор целиком, а сегмент — сектор без треугольника",
                 "that is the whole sector, and a segment is the sector "
                 "minus the triangle")] = sectors
    if triangles != 0 and not _near(triangles, want, _FIG_EPS):
        slips[_t("это треугольник на той же хорде, а не искомая часть круга",
                 "that is the triangle on the same chord, not the part "
                 "of the circle asked for")] = triangles
    slips[_t("площадь посчитана дважды: у фигуры одна такая часть, а не две",
             "the area is counted twice: the figure has one such part, "
             "not two")] = 2 * want
    slips[_t("посчитана половина: у фигуры две такие части, а не одна",
             "only half is counted: the figure has two such parts, "
             "not one")] = want / 2
    slips[_t("угол подставлен в градусах, а формула площади требует радиан",
             "the angle went in as degrees, and the area formula needs "
             "radians")] = want * 180 / sp.pi
    slips[_t("ответ записан в градусах: в радианах он в 180/π раз меньше",
             "the answer is written in degrees: in radians it is 180/π "
             "times smaller")] = want * sp.pi / 180
    count, one = _repeats(parsed, _area_term)
    if count:
        slips[_t(f"посчитана одна такая часть, а их в фигуре {count}",
                 f"that is one such part, and the figure has {count} "
                 f"of them")] = one
    return _report_measure(label, answer, want, slips, tol, exact)


def verify_length(label, got, *pieces, tol=_FIG_TOL, exact=False):
    """Ответ — длина линии, и она берётся с самой линии.

    Куски идут подряд, но замыкаться не обязаны: так проверяется и хорда,
    и одна дуга, и ломаная. Для замкнутого контура есть verify_perimeter,
    который знает промахи периметра.
    """
    if _blank(label, got, *pieces):
        return False
    answer = _as_measure(label, got)
    if answer is None:
        return False
    parsed = _figure(label, pieces, closed=False)
    if parsed is None:
        return False
    want = _measure([_length_term(p) for p in parsed])
    other = _measure([_length_term(p) for p in _flipped(parsed)])
    chords = _measure([_length_term(p) for p in _chorded(parsed)])
    slips = {}
    if not _near(other, want, _FIG_EPS):
        slips[_t("взята дуга с другой стороны окружности: меньшая вместо "
                 "большей или наоборот",
                 "that is the arc on the other side of the circle: "
                 "the minor one instead of the major, or the other way")] \
            = other
    if not _near(chords, want, _FIG_EPS):
        slips[_t("это хорда, а не дуга: по прямой короче, чем по окружности",
                 "that is the chord, not the arc: the straight way is "
                 "shorter than the way round")] = chords
    slips[_t("угол подставлен в градусах, а длина дуги считается по радианам",
             "the angle went in as degrees, and arc length is measured "
             "in radians")] = want * 180 / sp.pi
    slips[_t("ответ записан в градусах: в радианах он в 180/π раз меньше",
             "the answer is written in degrees: in radians it is 180/π "
             "times smaller")] = want * sp.pi / 180
    slips[_t("длина удвоена", "the length is doubled")] = 2 * want
    slips[_t("взята половина линии", "that is half the line")] = want / 2
    return _report_measure(label, answer, want, slips, tol, exact)


def verify_perimeter(label, got, *pieces, tol=_FIG_TOL, exact=False):
    """Ответ — периметр, и он обходится по границе фигуры.

    Отличие от verify_length одно, и оно же главная ловушка темы: контур
    обязан замкнуться. Дуга сектора границей не является — граница это
    дуга и два радиуса, — и проверка называет пропажу прямых кусков
    отдельным сообщением.
    """
    if _blank(label, got, *pieces):
        return False
    answer = _as_measure(label, got)
    if answer is None:
        return False
    parsed = _figure(label, pieces)
    if parsed is None:
        return False
    curved = [p for p in parsed if p[0] == 'arc']
    straight = [p for p in parsed if p[0] == 'seg']
    want = _measure([_length_term(p) for p in parsed])
    slips = {}
    if curved and straight:
        slips[_t("посчитаны только дуги: в границу входят и прямые куски",
                 "only the arcs are counted: the boundary has straight "
                 "pieces too")] = _measure([_length_term(p) for p in curved])
        slips[_t("посчитаны только прямые куски: дуга тоже граница",
                 "only the straight pieces are counted: the arc is part "
                 "of the boundary too")] = \
            _measure([_length_term(p) for p in straight])
    other = _measure([_length_term(p) for p in _flipped(parsed)])
    if not _near(other, want, _FIG_EPS):
        slips[_t("дуга взята с другой стороны окружности",
                 "the arc has been taken the other way round the circle")] \
            = other
    slips[_t("угол подставлен в градусах, а длина дуги считается по радианам",
             "the angle went in as degrees, and arc length is measured "
             "in radians")] = want * 180 / sp.pi
    slips[_t("ответ записан в градусах: в радианах он в 180/π раз меньше",
             "the answer is written in degrees: in radians it is 180/π "
             "times smaller")] = want * sp.pi / 180
    count, one = _repeats(parsed, _length_term)
    if count:
        slips[_t(f"обойдена одна такая часть, а их в фигуре {count}",
                 f"that is the way round one such part, and the figure "
                 f"has {count} of them")] = one
    return _report_measure(label, answer, want, slips, tol, exact)


def verify_law(label, got, var, build, values, measure='area', tol=_FIG_TOL,
               at=None):
    """Ответ — выражение от буквы, и оно проверяется измерением фигуры.

    Экзамен просит «find the area of one of the shaded segments in terms
    of θ», и сверять такое с записанным ½r²(θ − sin θ) значило бы сверять
    запись. Проверка вместо этого берёт несколько значений θ, строит
    фигуру при каждом из них и меряет её. Любая верная форма проходит:
    2θ − 2 sin θ и 2(θ − sin θ) — одно и то же выражение.

    build(значение) возвращает границу фигуры при этом значении буквы;
    measure — что мерить: 'area', 'perimeter' или 'length'.

    at — подстановка остальных букв: {m: 2}. Экзамен просит выразить
    радиус конуса «через h и m», а мерить можно только по одной букве
    за раз, поэтому вторая закрепляется числом, и проверка идёт дважды:
    сначала при m = 2 по всем h, потом при h = 3 по всем m. Подстановка
    делается здесь, а не в ячейке: в незаполненной ячейке стоит `...`,
    и `....subs(...)` в ней не написать.

    Фигуру разрешено строить из самого ответа — «ваш θ(r), нарисованный
    сектором», — и тогда пустой остаётся не мера, а чертёж. Поэтому
    пустоту ищут и в ответе, и в первой построенной границе.

    Сообщение называет то значение, на котором разошлось, и сколько там
    на самом деле. Это подсказка, но подсказка про одно θ, а спросили
    про все, — как в verify_count_law.
    """
    if _blank(label, got, build(values[0])):
        return False
    try:
        expr = sp.sympify(got).subs(at or {})
    except (sp.SympifyError, TypeError):
        print(f"{NO} {label}: " + _t("ответ не разобран как выражение",
                                     "the answer is not an expression"))
        return False
    extra = expr.free_symbols - {var}
    if extra:
        names = ', '.join(sorted(str(s) for s in extra))
        print(f"{NO} {label}: " + _t(
            f"в ответе осталась лишняя буква: {names}",
            f"the answer still carries an extra letter: {names}"))
        return False
    if measure not in ('area', 'perimeter', 'length'):
        raise ValueError(_t("verify_law: мерить можно area, perimeter или length",
                            "verify_law: measure is area, perimeter or length"))
    for value in values:
        parsed = _figure(label, build(value), closed=measure != 'length')
        if parsed is None:
            return False
        term = _area_term if measure == 'area' else _length_term
        real = sp.Abs(_measure([term(p) for p in parsed]))
        mine = sp.simplify(expr.subs(var, value))
        if not mine.is_number or not _near(mine, real, tol):
            print(f"{NO} {label}: " + _t(
                f"при {var} = {value} фигура меряется {sig(real, 6)}, "
                f"а выражение даёт {mine}",
                f"at {var} = {value} the figure measures {sig(real, 6)}, "
                f"but the expression gives {mine}"))
            return False
    print(f"{OK} {label}")
    return True


def verify_volume(label, got, *pieces, tol=_FIG_TOL, exact=False):
    """Ответ — объём тела вращения, и он берётся с осевого сечения.

    pieces — замкнутая граница сечения; тело получается вращением этой
    фигуры вокруг оси x на полный оборот. Объём считается теоремой Паппа
    прямо по контуру, поэтому ⅓πr²h проверке неизвестно — как и то,
    что фигура вообще конус.

    Сечение обязано лежать по одну сторону от оси: иначе вращение
    накладывает тело само на себя, и объёма у такого нет.
    """
    if _blank(label, got, *pieces):
        return False
    answer = _as_measure(label, got)
    if answer is None:
        return False
    parsed = _figure(label, pieces)
    if parsed is None:
        return False
    heights = [float(_at(p, i / _FIG_SAMPLES)[1])
               for p in parsed for i in range(_FIG_SAMPLES + 1)]
    if min(heights) < -_FIG_EPS and max(heights) > _FIG_EPS:
        print(f"{NO} {label}: " + _t(
            "сечение пересекает ось вращения — такое тело само на себя "
            "накладывается",
            "the cross-section crosses the axis, and such a solid would "
            "overlap itself"))
        return False
    want = sp.pi * sp.Abs(_measure([_moment_term(p) for p in parsed]))
    if want == 0:
        print(f"{NO} {label}: " + _t("сечение не заметает объёма",
                                     "the cross-section sweeps no volume"))
        return False
    flat = sp.Abs(_measure([_area_term(p) for p in parsed]))
    slips = {_t("это площадь сечения, а не объём тела",
                "that is the area of the cross-section, not the volume "
                "of the solid"): flat,
             _t("множитель ⅓ потерян: столько занимает цилиндр той же "
                "высоты, а не конус",
                "the factor of ⅓ is missing: that is what a cylinder of "
                "the same height holds, not a cone"): 3 * want,
             _t("множитель ⅓ взят дважды", "the factor of ⅓ is applied "
                "twice"): want / 3,
             _t("объём удвоен", "the volume is doubled"): 2 * want}
    return _report_measure(label, answer, want, slips, tol, exact)
