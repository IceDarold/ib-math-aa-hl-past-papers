"""Форма графика (E8): стационарные точки, вогнутость, перегиб.
"""

import itertools
import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .functions import count_roots
from .derivative import _param_runs, _PREC
from .tangent import (
    _CUR_TOL, _as_places, _branch, _heights, _hunt, _rounds_to, _say, _slope,
    _snap, _stands, _wrote, curve,
)


# =================================================================== форма
# Двадцать седьмое понятие равенства ответов: **вид точки решают соседи, а не
# вторая производная**.
#
# Максимум — точка, рядом с которой кривая ниже с обеих сторон. Минимум —
# выше с обеих. Перегиб — место, где меняется сторона, в которую кривая
# выгнута. Ни в одном из трёх определений производной нет, и проверка берёт
# именно их: она идёт по кривой шагами и смотрит на соседей.
#
# Так и должно быть в этой теме. Вторая производная — только признак, и
# признак неполный: у x⁴ в нуле она ноль, а минимум там есть, и ровно на
# этом стоит самый дорогой вопрос темы (май 2021 TZ2 Paper 3, пункт (g)).
# Проверка, которая берёт вторую производную, повторяет ход ученика и
# вместе с ним молчит там, где тот ошибается; проверка, которая смотрит на
# соседей, отвечает всегда.
#
# Вогнутость меряется хордой: если середина хорды выше самой кривой, кривая
# выгнута вверх (concave up, «держит воду»). Это второе разностное
# отношение, и второй производной в нём не написано.

_BEND_SHARE = (0.2, 0.06, 0.02)   # доли масштаба, на которых смотрят соседей
_BEND_NOISE = 1e-13               # мельче этого разность высот — шум счёта
_FLAT_GRID = 240                  # столько x просматривается при поиске точек
_NATURE_WORDS = ('maximum', 'minimum', 'inflexion', 'neither')
_SIDE_WORDS = ('above', 'below', 'on')
_TURN_TOL = 1e-3                  # столько прощается координате точки
_SPAN = 1.0                       # масштаб окрестности, когда он не известен


def _as_curve(f, var=x, dep=y):
    """И формула, и кривая из E4 приходят сюда одним объектом."""
    if isinstance(f, tuple) and f and f[0] == 'curve':
        return f
    return curve(sp.Eq(dep, sp.sympify(f)), var, dep)


def _bent_curve(f):
    return isinstance(f, tuple) and bool(f) and f[0] == 'curve'


def _window_of(domain):
    """Отрезок из условия; без него — то, что видно вокруг нуля."""
    if domain is None:
        return -10.0, 10.0
    lo, hi = domain
    lo = -10.0 if lo in (-sp.oo, -math.inf) else float(sp.N(sp.sympify(lo), _PREC))
    hi = 10.0 if hi in (sp.oo, math.inf) else float(sp.N(sp.sympify(hi), _PREC))
    return lo, hi


def _place_on(cur, at):
    """Точка кривой по названному x — или по готовой паре координат."""
    if isinstance(at, (tuple, list, sp.Tuple)) and len(at) == 2:
        place = tuple(float(sp.N(sp.sympify(v), _PREC)) for v in at)
        return place if _stands(cur, place) else _snap(cur, place)
    here = float(sp.N(sp.sympify(at), _PREC))
    heights = _heights(cur, here)
    return None if not heights else (here, heights[0])


def _height(cur, here, near):
    """Высота кривой при x = here, на той же ветви, что и near."""
    spot = _branch(cur, here, near)
    return None if spot is None else spot[1]


def _neighbours(cur, place, width):
    """Высоты кривой слева и справа от точки на расстоянии width."""
    return (_height(cur, place[0] - width, place[1]),
            _height(cur, place[0] + width, place[1]))


def _noise(place):
    """Разность высот меньше этой — шум счёта, а не разность."""
    return max(_BEND_NOISE, 1e-13 * abs(place[1]))


def nature(f, at, var=x, dep=y, span=_SPAN):
    """Как ведёт себя кривая в точке: слово, полученное у соседей.

    Возвращает 'maximum', 'minimum', 'inflexion' или 'neither'. Точка не
    обязана быть стационарной: 'neither' — честный ответ там, где кривая
    просто идёт мимо, и 'inflexion' — там, где она меняет сторону выгиба.

    span — масштаб окрестности: на нём берутся три ширины окна. Меньше
    его брать незачем, а больше опасно, если рядом стоит вторая вершина.
    """
    cur = _as_curve(f, var, dep)
    place = _place_on(cur, at)
    if place is None:
        return None
    verdicts = []
    for share in _BEND_SHARE:
        left, right = _neighbours(cur, place, span * share)
        if left is None or right is None:
            continue
        room = _noise(place)
        verdicts.append((0 if abs(left - place[1]) <= room
                         else (1 if left > place[1] else -1),
                         0 if abs(right - place[1]) <= room
                         else (1 if right > place[1] else -1)))
    if not verdicts:
        return None
    if all(one < 0 and two < 0 for one, two in verdicts):
        return 'maximum'
    if all(one > 0 and two > 0 for one, two in verdicts):
        return 'minimum'
    return 'inflexion' if _turns_bend(cur, place, span) else 'neither'


def _bendiness(cur, place, width):
    """Насколько середина хорды выше кривой: > 0 — выгиб вверх (concave up)."""
    left, right = _neighbours(cur, place, width)
    if left is None or right is None:
        return None
    return (left + right) / 2 - place[1]


def _turns_bend(cur, place, span=_SPAN):
    """Меняется ли сторона выгиба при переходе через точку."""
    step = span * _BEND_SHARE[1]
    left = _branch(cur, place[0] - step, place[1])
    right = _branch(cur, place[0] + step, place[1])
    if left is None or right is None:
        return False
    one = _bendiness(cur, left, step / 3)
    two = _bendiness(cur, right, step / 3)
    if one is None or two is None:
        return False
    return one * two < 0


def concavity(f, at, var=x, dep=y, span=_SPAN):
    """В какую сторону выгнута кривая: 'up', 'down' или 'straight'.

    Меряется хордой: середина хорды над кривой — выгиб вверх. Годится и
    там, где второй производной нет вовсе.
    """
    cur = _as_curve(f, var, dep)
    place = _place_on(cur, at)
    if place is None:
        return None
    votes = []
    for share in _BEND_SHARE:
        value = _bendiness(cur, place, span * share)
        if value is None:
            continue
        votes.append(0 if abs(value) <= _noise(place) * 10
                     else (1 if value > 0 else -1))
    if not votes:
        return None
    if all(vote > 0 for vote in votes):
        return 'up'
    if all(vote < 0 for vote in votes):
        return 'down'
    return 'straight'


def _walk_along(cur, lo, hi, grid=_FLAT_GRID):
    """Проход по отрезку одной ветвью: (x, y, наклон) в каждом узле.

    Узлы сдвинуты на полшага, чтобы сетка не попадала ровно в центр
    симметричной картинки: там разность обращается в точный ноль, и
    смена знака, которую ищут дальше, не случается вовсе.
    """
    out, last = [], None
    for i in range(grid):
        here = lo + (hi - lo) * (i + 0.5) / grid
        heights = _heights(cur, here)
        if not heights:
            out.append(None)
            last = None
            continue
        height = (heights[0] if last is None
                  else min(heights, key=lambda v: abs(v - last)))
        lean = _slope(cur, (here, height))
        out.append(None if lean is None or lean is sp.oo
                   else (here, height, float(lean)))
        last = height
    return out


def _touch_points(cur, lo, hi, grid=_FLAT_GRID):
    """Точки, где наклон касается нуля, не меняя знака: горизонтальный перегиб.

    Просмотр смен знака их не видит — у x³ наклон 3x² нуля не пересекает.
    Здесь ищется локальный минимум |наклона| и уточняется делением
    отрезка в золотом отношении; принимается он только там, где наклон
    на порядки меньше всего, что встретилось на отрезке.
    """
    walk = _walk_along(cur, lo, hi, grid)
    seen = [item[2] for item in walk if item is not None]
    if not seen:
        return []
    room = 1e-7 * max(1.0, max(abs(value) for value in seen))
    out = []
    for left, here, right in zip(walk, walk[1:], walk[2:]):
        if left is None or here is None or right is None:
            continue
        if abs(here[2]) > min(abs(left[2]), abs(right[2])):
            continue
        if left[2] * right[2] < 0:
            continue                       # это смена знака, её видит просмотр
        low, high, guess = left[0], right[0], here[1]

        def steep(where, near):
            spot = _branch(cur, where, near)
            if spot is None:
                return None, near
            lean = _slope(cur, spot)
            return (None if lean is None or lean is sp.oo
                    else abs(float(lean))), spot[1]

        for _ in range(60):
            one, two = low + (high - low) / 3, high - (high - low) / 3
            first, near = steep(one, guess)
            second, guess = steep(two, near)
            if first is None or second is None:
                break
            if first <= second:
                high = two
            else:
                low = one
        spot = _branch(cur, (low + high) / 2, guess)
        if spot is None:
            continue
        lean = _slope(cur, spot)
        if lean is None or lean is sp.oo or abs(float(lean)) > room:
            continue
        out.append(spot)
    return out


def _merged(places, step):
    """Соседи, неразличимые по высоте, — это одна точка, и стоит она посередине.

    У очень плоской точки — xⁿ(a−x)ⁿ при n = 5 — наклон оказывается нулём на
    целой окрестности, и просмотр находит там две-три «смены знака» подряд,
    все на одной высоте с точностью до последнего бита. Разные вершины так
    близко по высоте не сходятся никогда, и порог берётся по ней, а не по x.
    """
    out = []
    for spot in sorted(places):
        if out and spot[0] - out[-1][-1][0] <= 2 * step \
                and abs(spot[1] - out[-1][-1][1]) <= 1e-12 * (
                    1 + max(abs(spot[1]), abs(out[-1][-1][1]))):
            out[-1].append(spot)
        else:
            out.append([spot])
    return [group[0] if len(group) == 1
            else (sum(item[0] for item in group) / len(group),
                  sum(item[1] for item in group) / len(group))
            for group in out]


def _spans_of(places, lo, hi):
    """Масштаб окрестности каждой точки: до соседки и до края отрезка."""
    out = []
    for i, place in enumerate(places):
        gaps = [abs(place[0] - other[0]) for j, other in enumerate(places)
                if j != i]
        gaps += [abs(place[0] - lo), abs(place[0] - hi), _SPAN]
        out.append(max(1e-6, min(gap for gap in gaps if gap > 1e-9) / 2.5))
    return out


def stationary(f, domain=None, var=x, dep=y):
    """Все точки кривой с нулевым наклоном: просмотр, а не решение.

    Возвращает список троек (x, y, слово). Полнота берётся ходьбой по
    отрезку из условия — тем же просмотром, которым E4 ищет точки
    заданного наклона.
    """
    cur = _as_curve(f, var, dep)
    lo, hi = _window_of(domain)
    places = _merged(_hunt(cur, 0.0, lo, hi, _FLAT_GRID), (hi - lo) / _FLAT_GRID)
    for spot in _merged(_touch_points(cur, lo, hi), (hi - lo) / _FLAT_GRID):
        if all(abs(spot[0] - a) > 1e-3 for a, _ in places):
            places.append(spot)
    # Просмотр ищет смены знака и потому не видит концов отрезка, а вопрос
    # закрытым отрезком ставится часто.
    for edge in (lo, hi):
        for height in _heights(cur, edge):
            lean = _slope(cur, (edge, height))
            if lean is None or lean is sp.oo or abs(float(lean)) > 1e-7:
                continue
            if all(abs(edge - a) > 1e-3 or abs(height - b) > 1e-3
                   for a, b in places):
                places.append((edge, height))
    places.sort()
    spans = _spans_of(places, lo, hi)
    return [(a, b, nature(cur, (a, b), var, dep, span))
            for (a, b), span in zip(places, spans)]


def inflexions(f, domain=None, var=x, dep=y):
    """Все точки перегиба: там, где хорда переходит на другую сторону."""
    cur = _as_curve(f, var, dep)
    lo, hi = _window_of(domain)
    width = (hi - lo) / 400
    out, previous, last = [], None, None
    for i in range(_FLAT_GRID):
        here = lo + (hi - lo) * (i + 0.5) / _FLAT_GRID
        heights = _heights(cur, here)
        if not heights:
            previous = last = None
            continue
        height = (heights[0] if last is None
                  else min(heights, key=lambda v: abs(v - last)))
        value = _bendiness(cur, (here, height), width)
        if value is not None and previous is not None and previous * value < 0:
            left, right, edge = here - (hi - lo) / _FLAT_GRID, here, previous
            guess = last
            for _ in range(60):
                mid = (left + right) / 2
                spot = _branch(cur, mid, guess)
                if spot is None:
                    break
                middle = _bendiness(cur, spot, width)
                if middle is None:
                    break
                if edge * middle <= 0:
                    right = mid
                else:
                    left, edge, guess = mid, middle, spot[1]
            spot = _sharper(cur, _branch(cur, (left + right) / 2, guess), width)
            if spot is not None and all(abs(spot[0] - a) > 1e-4 for a, _ in out):
                out.append(spot)
        previous, last = value, height
    return out


def _sharper(cur, spot, width):
    """Уточняет перегиб более узкой хордой.

    У второй разности своя погрешность порядка квадрата ширины: хорда
    шириной 0.005 ставит перегиб на 10⁻⁵ в сторону. Найденное место
    пересчитывается хордой вдесятеро уже, и ошибка падает во сто раз.
    """
    if spot is None:
        return None
    narrow = width / 10
    left, right = spot[0] - 2 * width, spot[0] + 2 * width
    edge = _bendiness(cur, _branch(cur, left, spot[1]) or spot, narrow)
    other = _bendiness(cur, _branch(cur, right, spot[1]) or spot, narrow)
    if edge is None or other is None or edge * other >= 0:
        return spot
    guess = spot[1]
    for _ in range(60):
        mid = (left + right) / 2
        place = _branch(cur, mid, guess)
        if place is None:
            break
        middle = _bendiness(cur, place, narrow)
        if middle is None:
            break
        if edge * middle <= 0:
            right = mid
        else:
            left, edge, guess = mid, middle, place[1]
    return _branch(cur, (left + right) / 2, guess) or spot


def crossings(f, domain=None, var=x):
    """Сколько разных точек оси пересекает кривая на отрезке из условия.

    Нужно там, где вопрос звучит «сколько пересечений с осью» и ответом
    является множество значений буквы: считать приходится в каждой пробной
    точке. Касание — это одно пересечение, а не два и не ноль, и потому у
    многочлена кратности сначала убираются, а корни считаются точно:
    просмотр как раз касание и теряет, а весь вопрос стоит на нём.
    """
    expr = sp.sympify(f)
    lo, hi = _window_of(domain)
    try:
        poly = sp.Poly(expr, var)
        if poly.degree() > 0 and all(number.is_number for number in poly.all_coeffs()):
            plain = sp.Poly(sp.quo(poly, sp.gcd(poly, poly.diff(var))), var)
            return plain.count_roots(sp.Rational(lo).limit_denominator(10 ** 6),
                                     sp.Rational(hi).limit_denominator(10 ** 6))
    except (sp.PolynomialError, sp.GeneratorsNeeded, NotImplementedError,
            TypeError, ValueError):
        pass
    fast = sp.lambdify(var, expr, 'math')

    def value(here):
        try:
            out = fast(here)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        return out if isinstance(out, (int, float)) and math.isfinite(out) else None

    return count_roots(value, lo, hi)


# ------------------------------------------------------------ сами проверки

def _runs_of(params):
    """Числовые подстановки для букв семейства."""
    return _param_runs(params)


def _put(item, run):
    """Подстановка чисел вместо букв — в формулу, в точку или в кривую."""
    if not run:
        return item
    if isinstance(item, str):
        return item
    if _bent_curve(item):
        return curve(item[1].subs(run), item[2], item[3])
    if isinstance(item, (list, tuple, sp.Tuple)):
        return [_put(part, run) for part in item]
    try:
        return sp.sympify(item).subs(run)
    except (TypeError, ValueError, AttributeError, sp.SympifyError):
        return item


def _run_words(run):
    """Хвост сообщения: при каких значениях букв проверка споткнулась."""
    if not run:
        return ''
    body = ', '.join(f"{letter} = {value}" for letter, value in run.items())
    return _t(f" (при {body})", f" (at {body})")


def _word_of(value, allowed):
    """Ответ-слово: приводится к списку допустимых, иначе None."""
    word = (value if isinstance(value, str) else str(value)).strip().lower()
    word = {'max': 'maximum', 'min': 'minimum', 'local maximum': 'maximum',
            'local minimum': 'minimum', 'maximum point': 'maximum',
            'minimum point': 'minimum', 'inflection': 'inflexion',
            'point of inflexion': 'inflexion', 'point of inflection': 'inflexion',
            'none': 'neither', 'no': 'neither', 'yes': 'inflexion',
            }.get(word, word)
    if word in allowed:
        return word
    return None


def _word_slip(mine, want):
    """Отчего слово оказалось не тем."""
    if want == 'minimum' and mine == 'maximum':
        return _t("кривая рядом с этой точкой выше, а не ниже: это минимум",
                  "the curve is higher next to this point, not lower: it is a minimum")
    if want == 'maximum' and mine == 'minimum':
        return _t("кривая рядом с этой точкой ниже, а не выше: это максимум",
                  "the curve is lower next to this point, not higher: it is a maximum")
    if want == 'inflexion' and mine in ('maximum', 'minimum'):
        return _t("с одной стороны кривая выше, с другой ниже — это не вершина, "
                  "а перегиб: наклон здесь знака не меняет",
                  "the curve is higher on one side and lower on the other — this is not "
                  "a turning point but an inflexion: the slope does not change sign here")
    if want in ('maximum', 'minimum') and mine == 'inflexion':
        return _t(f"вогнутость здесь не меняется, а кривая с обеих сторон стоит "
                  f"по одну сторону от точки — это "
                  f"{'максимум' if want == 'maximum' else 'минимум'}",
                  f"the concavity does not change here, and the curve is on the same "
                  f"side of the point both ways — this is a {want}")
    if want == 'neither':
        return _t("в этой точке наклон не ноль и вогнутость не меняется",
                  "the slope is not zero at this point and the concavity does not change")
    return None


def _words_of(label, got, places, allowed, what):
    """Ответ-слова приводятся к списку ровно той же длины, что и точки."""
    mine = got if isinstance(got, (list, tuple)) else [got]
    if len(mine) != len(places):
        print(f"{NO} {label}: " + _t(
            f"точек {len(places)}, а слов {len(mine)}",
            f"there are {len(places)} points and {len(mine)} words"))
        return None
    out = []
    for item in mine:
        word = _word_of(item, allowed)
        if word is None:
            print(f"{NO} {label}: " + _t(
                f"ответ — слово ({what}), а не {item!r}",
                f"the answer is a word ({what}), not {item!r}"))
            return None
        out.append(word)
    return out


def _at_list(at):
    """Одна точка или список точек — всегда список."""
    if isinstance(at, list):
        return at
    return [at]


def verify_nature(label, got, f, at, var=x, dep=y, domain=None, params=None):
    """Ответ — вид точки: слово, проверенное соседями.

    at — точка или список точек; got — слово или столько же слов. f —
    формула, кривая или список формул: список означает, что утверждение
    сделано о целом семействе, и тогда каждый его член проходится отдельно.

    Внутри нет ни первой производной, ни второй. Максимум узнаётся тем, что
    кривая рядом ниже, перегиб — тем, что она меняет сторону выгиба. Поэтому
    проверка отвечает и там, где вторая производная равна нулю.
    """
    if _blank(label, got):
        return False
    family = f if isinstance(f, list) else [f]
    places = _at_list(at)
    words = _words_of(label, got, places,
                      _NATURE_WORDS, 'maximum, minimum, inflexion, neither')
    if words is None:
        return False
    for run in _runs_of(params):
        for shape in family:
            here = _as_curve(_put(shape, run), var, dep)
            found = stationary(here, _put(domain, run), var, dep)
            for word, spot in zip(words, places):
                place = _place_on(here, _put(spot, run))
                if place is None:
                    print(f"{NO} {label}: " + _t(
                        f"кривой в точке {_say(spot)} нет",
                        f"the curve has no point at {_say(spot)}") + _run_words(run))
                    return False
                near = [item for item in found
                        if abs(item[0] - place[0]) < _TURN_TOL]
                truth = near[0][2] if near else nature(here, place, var, dep)
                if truth != word:
                    why = _word_slip(word, truth)
                    print(f"{NO} {label}: " + (why or _t(
                        f"в точке {_say(place[0])} это {truth}",
                        f"at {_say(place[0])} this is a {truth}")) + _run_words(run))
                    return False
    print(f"{OK} {label}: " + ', '.join(words))
    return True


def verify_concavity(label, got, f, at, var=x, dep=y, params=None):
    """Ответ — сторона выгиба: 'up' или 'down', проверенная хордой."""
    if _blank(label, got):
        return False
    places = _at_list(at)
    words = _words_of(label, got, places, ('up', 'down', 'straight'), 'up, down')
    if words is None:
        return False
    for run in _runs_of(params):
        here = _as_curve(_put(f, run), var, dep)
        for word, spot in zip(words, places):
            truth = concavity(here, _put(spot, run), var, dep)
            if truth is None:
                print(f"{NO} {label}: " + _t(
                    f"кривой в точке {_say(spot)} нет",
                    f"the curve has no point at {_say(spot)}") + _run_words(run))
                return False
            if truth != word:
                print(f"{NO} {label}: " + _t(
                    f"хорда около {_say(spot)} лежит по другую сторону: выгиб {truth}",
                    f"the chord next to {_say(spot)} lies on the other side: the "
                    f"curve bends {truth}") + _run_words(run))
                return False
    print(f"{OK} {label}: " + ', '.join(words))
    return True


def _turn_slip(place, found, cur, coordinates):
    """Отчего названная точка не стационарная."""
    here, there = place
    if coordinates and any(_rounds_to(there, spot[0]) and _rounds_to(here, spot[1])
                           for spot in found):
        return _t("координаты переставлены местами",
                  "the two coordinates are the other way round")
    heights = _heights(cur, here)
    if coordinates and heights and all(abs(there - h) > _TURN_TOL for h in heights):
        return _t(f"при x = {_say(here)} кривая проходит через "
                  f"y = {_say(heights[0])}, а не {_say(there)}",
                  f"at x = {_say(here)} the curve passes through "
                  f"y = {_say(heights[0])}, not {_say(there)}")
    lean = _slope(cur, (here, heights[0] if heights else there))
    if lean is not None and lean is not sp.oo:
        return _t(f"наклон в этой точке {_say(lean)}, а не ноль",
                  f"the slope at this point is {_say(lean)}, not zero")
    if found:
        return _t(f"ближайшая точка нулевого наклона стоит при "
                  f"x = {found[0][0]:.4f}",
                  f"the nearest point of zero slope stands at x = {found[0][0]:.4f}")
    return None


def _raw_places(got, coordinates):
    """Ответ так, как он записан: для печати, без подстановки чисел."""
    items = got if isinstance(got, (list, tuple, sp.Tuple)) else [got]
    if coordinates and isinstance(got, (tuple, list, sp.Tuple)) and len(got) == 2 \
            and not any(isinstance(v, (tuple, list, sp.Tuple)) for v in got):
        items = [got]                 # это одна точка, а не два числа
    out = []
    for item in items:
        if isinstance(item, (tuple, list, sp.Tuple)):
            out.append(tuple(sp.sympify(value) for value in item))
        else:
            out.append((sp.sympify(item), None))
    return out


def _shown(written, coordinates):
    return (', '.join(f"({_wrote(a)}, {_wrote(b)})" for a, b in written)
            if coordinates else ', '.join(_wrote(a) for a, _ in written))


def verify_turning(label, got, f, kind=None, var=x, dep=y, domain=None,
                   coordinates=True, params=None):
    """Ответ — точки нулевого наклона: и те, и все, и с обеими координатами.

    Пустой список — тоже ответ, и именно он стоит в вопросах «покажите, что
    стационарных точек нет». Проверка тогда проходит отрезок и убеждается,
    что ни одной такой точки там действительно нет.

    kind='maximum' (или 'minimum') оставляет только вершины нужного вида:
    так спрошено там, где просят локальный минимум, а не все точки сразу.
    """
    empty = isinstance(got, (list, tuple)) and len(got) == 0
    if not empty and _blank(label, got):
        return False
    for run in _runs_of(params):
        here = _as_curve(_put(f, run), var, dep)
        window = _put(domain, run)
        found = stationary(here, window, var, dep)
        if kind:
            found = [spot for spot in found if spot[2] == kind]
        if empty:
            mine = []
        else:
            mine, _ = _as_places(label, _put(got, run), here, coordinates)
            if mine is None:
                return False
        lo, hi = _window_of(window)
        seen = []
        for place in mine:
            if not lo - _CUR_TOL <= place[0] <= hi + _CUR_TOL:
                print(f"{NO} {label}: " + _t(
                    f"точка {_say(place[0])} лежит вне отрезка из условия",
                    f"{_say(place[0])} is outside the interval in the question")
                    + _run_words(run))
                return False
            # Совпадение меряется тремя значащими цифрами, а не абсолютным
            # порогом: 0.655 против 0.65600 — это другая третья цифра, и
            # экзамен такой ответ не принимает.
            near = [spot for spot in found if _rounds_to(place[0], spot[0])]
            if not near:
                why = _turn_slip(place, found, here, coordinates)
                print(f"{NO} {label}: " + (why or _t(
                    f"в точке {_say(place[0])} наклон не ноль",
                    f"the slope is not zero at {_say(place[0])}")) + _run_words(run))
                return False
            spot = near[0]
            if coordinates and not _rounds_to(place[1], spot[1]):
                print(f"{NO} {label}: " + _t(
                    f"первая координата верна, вторая нет: при x = {_say(spot[0])} "
                    f"кривая стоит на высоте {_say(spot[1])}",
                    f"the first coordinate is right and the second is not: at "
                    f"x = {_say(spot[0])} the curve stands at {_say(spot[1])}")
                    + _run_words(run))
                return False
            if any(abs(spot[0] - was) < _TURN_TOL for was in seen):
                print(f"{NO} {label}: " + _t("одна и та же точка названа дважды",
                                             "the same point is named twice")
                      + _run_words(run))
                return False
            seen.append(spot[0])
        if len(found) > len(seen):
            miss = [spot for spot in found
                    if all(abs(spot[0] - was) > _TURN_TOL for was in seen)]
            if not seen:
                print(f"{NO} {label}: " + _t(
                    f"такая точка есть: около x = {_say(miss[0][0])}",
                    f"there is such a point: near x = {_say(miss[0][0])}")
                    + _run_words(run))
                return False
            print(f"{NO} {label}: " + _t(
                f"названные точки верны, но найдено не всё — их {len(found)}, "
                f"а у вас {len(seen)}, первая пропущенная около x = {miss[0][0]:.4f}",
                f"the points you list are right, but not all of them are there — "
                f"there are {len(found)}, you list {len(seen)}, the first one missing "
                f"is near x = {miss[0][0]:.4f}") + _run_words(run))
            return False
    if empty:
        print(f"{OK} {label}: " + _t("таких точек нет", "there are none"))
        return True
    print(f"{OK} {label}: {_shown(_raw_places(got, coordinates), coordinates)}")
    return True


def verify_bend(label, got, f, var=x, dep=y, domain=None, coordinates=False,
                params=None):
    """Ответ — точки перегиба, найденные сменой стороны хорды.

    Второй производной внутри нет: перегиб — это место, где кривая
    перестаёт быть выгнутой в одну сторону и начинает в другую, и хорда
    видит это сама.
    """
    empty = isinstance(got, (list, tuple)) and len(got) == 0
    if not empty and _blank(label, got):
        return False
    for run in _runs_of(params):
        here = _as_curve(_put(f, run), var, dep)
        found = inflexions(here, _put(domain, run), var, dep)
        if empty:
            mine = []
        else:
            mine, _ = _as_places(label, _put(got, run), here, coordinates)
            if mine is None:
                return False
        seen = []
        for place in mine:
            # Совпадение меряется тремя значащими цифрами, а не абсолютным
            # порогом: 0.655 против 0.65600 — это другая третья цифра, и
            # экзамен такой ответ не принимает.
            near = [spot for spot in found if _rounds_to(place[0], spot[0])]
            if not near:
                close = [spot for spot in found
                         if abs(spot[0] - place[0]) < 0.05 * max(1.0, abs(place[0]))]
                swapped = coordinates and any(
                    _rounds_to(place[1], spot[0]) and _rounds_to(place[0], spot[1])
                    for spot in found)
                word = concavity(here, place, var, dep)
                why = (_t("координаты переставлены местами",
                          "the two coordinates are the other way round") if swapped else
                       _t("рядом с этим ответом настоящий перегиб есть — проверь "
                          "третью значащую цифру",
                          "there is a real point of inflexion next to that answer: "
                          "check the third significant figure") if close else
                       _t(f"около x = {_say(place[0])} кривая выгнута в одну и ту же "
                          f"сторону ({word}) — вогнутость там не меняется",
                          f"next to x = {_say(place[0])} the curve bends the same way "
                          f"({word}) — the concavity does not change there")
                       if word in ('up', 'down') or close else None)
                print(f"{NO} {label}: " + (why or _t(
                    f"в точке {_say(place[0])} перегиба нет",
                    f"there is no point of inflexion at {_say(place[0])}"))
                    + _run_words(run))
                return False
            spot = near[0]
            if coordinates and not _rounds_to(place[1], spot[1]):
                print(f"{NO} {label}: " + _t(
                    f"первая координата верна, вторая нет: при x = {_say(spot[0])} "
                    f"кривая стоит на высоте {_say(spot[1])}",
                    f"the first coordinate is right and the second is not: at "
                    f"x = {_say(spot[0])} the curve stands at {_say(spot[1])}")
                    + _run_words(run))
                return False
            if any(abs(spot[0] - was) < _TURN_TOL for was in seen):
                print(f"{NO} {label}: " + _t("одна и та же точка названа дважды",
                                             "the same point is named twice")
                      + _run_words(run))
                return False
            seen.append(spot[0])
        if len(found) > len(seen):
            miss = [spot for spot in found
                    if all(abs(spot[0] - was) > _TURN_TOL for was in seen)]
            print(f"{NO} {label}: " + _t(
                f"перегибов здесь {len(found)}, а названо {len(seen)}, первый "
                f"пропущенный около x = {miss[0][0]:.4f}",
                f"there are {len(found)} points of inflexion here and {len(seen)} "
                f"are named, the first one missing is near x = {miss[0][0]:.4f}")
                + _run_words(run))
            return False
    if empty:
        print(f"{OK} {label}: " + _t("перегибов нет", "there are none"))
        return True
    print(f"{OK} {label}: {_shown(_raw_places(got, coordinates), coordinates)}")
    return True


def verify_side(label, got, f, at, var=x, dep=y, params=None):
    """Ответ — по какую сторону оси стоит точка: 'above' или 'below'.

    Отдельный балл экзамена и отдельный от вида точки вопрос: максимум
    бывает и ниже оси, минимум — и выше.
    """
    if _blank(label, got):
        return False
    places = _at_list(at)
    words = _words_of(label, got, places, _SIDE_WORDS, 'above, below')
    if words is None:
        return False
    for run in _runs_of(params):
        here = _as_curve(_put(f, run), var, dep)
        for word, spot in zip(words, places):
            place = _place_on(here, _put(spot, run))
            if place is None:
                print(f"{NO} {label}: " + _t(
                    f"кривой в точке {_say(spot)} нет",
                    f"the curve has no point at {_say(spot)}") + _run_words(run))
                return False
            truth = ('on' if abs(place[1]) < 1e-9
                     else 'above' if place[1] > 0 else 'below')
            if truth != word:
                print(f"{NO} {label}: " + _t(
                    f"вторая координата здесь {_say(place[1])}, и точка стоит {truth}",
                    f"the second coordinate here is {_say(place[1])}, so the point "
                    f"is {truth} the axis") + _run_words(run))
                return False
    print(f"{OK} {label}: " + ', '.join(words))
    return True


# --------------------------------------------------- условие на две буквы

def _grid_of(letters, window, steps):
    """Сетка значений букв: по ней сверяются ответ-условие и само свойство."""
    lo, hi = window
    values = [sp.Rational(round(1000 * (lo + (hi - lo) * i / steps)), 1000)
              for i in range(steps + 1)]
    return [dict(zip(letters, point))
            for point in itertools.product(values, repeat=len(letters))]


def verify_condition(label, got, holds, letters, window=(-3, 3), steps=12,
                     skip=None):
    """Ответ — условие на несколько букв; проверяется самим свойством.

    verify_param_set спрашивает одну букву, и там можно перебрать
    промежутки. Здесь букв несколько, и берётся сетка: в каждом узле ответ
    ученика говорит «да» или «нет», а свойство holds — как обстоит дело на
    самом деле. Расхождение печатается вместе с узлом, в котором нашлось.

    holds(**values) возвращает True, False или None; None — «здесь судить
    нельзя» (вырождение, касание), такой узел пропускается. skip(**values)
    убирает узлы, о которых вопрос не спрашивает.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    letters = list(letters)
    checked = skipped = 0
    for point in _grid_of(letters, window, steps):
        named = {str(letter): value for letter, value in point.items()}
        if skip is not None and skip(**named):
            continue
        said = claim.subs(point)
        if said not in (sp.true, sp.false, True, False):
            skipped += 1
            continue
        said = bool(said)
        try:
            fact = holds(**named)
        except (TypeError, ValueError, ZeroDivisionError, ArithmeticError,
                sp.PolynomialError, sp.GeneratorsNeeded):
            skipped += 1
            continue
        if fact is None:
            skipped += 1
            continue
        checked += 1
        if bool(fact) != said:
            body = ', '.join(f"{letter} = {value}" for letter, value in named.items())
            print(f"{NO} {label}: " + (_t(
                f"при {body} свойство выполняется, а условие его не пускает",
                f"at {body} the property does hold, and the condition shuts it out")
                if fact else _t(
                f"при {body} условие говорит «да», а свойства там нет",
                f"at {body} the condition says yes, and the property is not there")))
            return False
    if checked < 4:
        print(f"{NO} {label}: " + _t(
            "условие не удалось проверить ни в одном узле",
            "the condition could not be checked at any point"))
        return False
    tail = _t(f", пропущено {skipped}", f", {skipped} skipped") if skipped else ''
    print(f"{OK} {label}: {claim}"
          + _t(f" (проверено узлов {checked}{tail})",
               f" ({checked} points checked{tail})"))
    return True
