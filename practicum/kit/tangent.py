"""Касательная и нормаль: кривая, по которой проверка идёт шагами (E4).
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .functions import _tidy
from .geometry import _near
from .derivative import _param_runs, _PREC


# ========================================================= кривая и прямая
# Семнадцатое понятие равенства ответов: касательная держится кривой.
#
# Эталона снова нет, но нет здесь и формулы. Кривая задаётся условием на
# пару чисел — F(x, y) = 0, — и «y = f(x)» это частный случай, а не другой
# случай. Проверка не решает условие относительно y и не дифференцирует
# его: она идёт по кривой. Рядом с точкой берётся x на шаг левее и на шаг
# правее, для каждого из них решается F(x, ·) = 0 у самой точки, и наклон
# получается секущей через две найденные точки. Ни dy/dx = −F_x/F_y, ни
# правила дифференцирования внутри проверки не написаны ни разу.
#
# Отсюда и определение касательной: прямая проходит через точку кривой
# и имеет тот же наклон, что и сама кривая, — то есть кривая её держится.
# Нормаль — та же проверка с произведением наклонов, равным −1. Обратный
# ход: «где наклон равен m» — это тоже ход по кривой, и полнота набора
# берётся просмотром, а не решением уравнения.

_CUR_TOL = 5e-4          # три значащие цифры — столько же принимает экзамен
_CUR_STEP = 1e-3         # ширина шага вдоль кривой
_CUR_STEEP = 1.0         # круче — идём по y, а не по x: так лучше обусловлено
_CUR_WINDOW = (-60, 60)  # где ищется вторая координата точки
_CUR_GRID = 240          # столько x просматривается при поиске всех точек


def _wrote(value):
    """Ответ так, как он записан: точное — символом, десятичное — числом."""
    value = sp.sympify(value)
    return _say(value) if value.is_Float else str(value)


def _say(value):
    """Число или выражение для сообщения проверки."""
    try:
        return _tidy(float(sp.N(sp.sympify(value), _PREC)))
    except (TypeError, ValueError, AttributeError):
        return str(value)


def curve(relation, var=x, dep=y):
    """Кривая как условие на пару чисел, а не как формула для y.

    Принимает и Eq(y, x**2 - 1), и Eq(x**2 + y**2, 4), и просто выражение,
    которое должно обращаться в ноль. Разницы между «функция» и «кривая,
    заданная уравнением» для проверки нет: обе она проходит ногами.
    """
    if relation is Ellipsis:
        return ('curve', Ellipsis, var, dep)
    shape = sp.sympify(relation)
    if isinstance(shape, sp.Eq):
        shape = shape.lhs - shape.rhs
    shape = sp.together(shape)
    # Если условие разрешается относительно y — а это половина вопросов
    # темы, — вторую координату берём прямо, не разыскивая её по отрезку.
    plain = None
    if shape.has(dep):
        try:                              # y = f(x): самый частый случай
            flat = sp.Poly(shape, dep)
            if flat.degree() == 1:
                lead, rest = flat.all_coeffs()
                if not lead.has(dep) and lead != 0:
                    plain = sp.together(-rest / lead)
        except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError):
            plain = None
    return ('curve', shape, var, dep, plain)


_BENT_CACHE = {}


def _bent(cur):
    """Условие кривой числовой функцией двух аргументов."""
    _, shape, var, dep = cur[:4]
    known = _BENT_CACHE.get((shape, var, dep))
    if known is not None:
        return known
    fast = sp.lambdify((var, dep), shape, 'math')

    def value(a, b):
        try:
            out = fast(a, b)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        out = complex(out) if isinstance(out, complex) else out
        if isinstance(out, complex):
            if abs(out.imag) > 1e-12:
                return None
            out = out.real
        return out if math.isfinite(out) else None

    if len(_BENT_CACHE) > 4000:
        _BENT_CACHE.clear()
    _BENT_CACHE[(shape, var, dep)] = value
    return value


def _heights(cur, here):
    """Все y, при которых точка (here, y) лежит на кривой."""
    plain = cur[4] if len(cur) > 4 else None
    if plain is not None:
        try:
            value = complex(sp.N(plain.subs(cur[2], sp.Float(here)), _PREC))
        except (TypeError, ValueError):
            return []
        if abs(value.imag) > 1e-9 or not math.isfinite(value.real):
            return []
        return [value.real]
    shape = _bent(cur)
    kept = []
    for value in _settle(lambda t: shape(here, t), *_CUR_WINDOW):
        if all(abs(value - seen) > 1e-6 for seen in kept):
            kept.append(value)
    return kept


def _settle(fun, lo, hi, samples=800):
    """Корни функции одной переменной: смена знака и деление пополам.

    Ни производных, ни начального приближения: только знаки. Годится и
    там, где выражение не определено на части отрезка — такие точки
    просто рвут просмотр, а не роняют его.
    """
    out, last, where = [], None, None
    for i in range(samples + 1):
        point = lo + (hi - lo) * i / samples
        here = fun(point)
        if here is None:
            last = where = None
            continue
        if here == 0:
            out.append(point)
        elif last is not None and last * here < 0:
            left, right, edge = where, point, last
            for _ in range(80):
                mid = (left + right) / 2
                middle = fun(mid)
                if middle is None:
                    break
                if edge * middle <= 0:
                    right = mid
                else:
                    left, edge = mid, middle
            out.append((left + right) / 2)
        last, where = here, point
    return out


def _root_near(fun, start, scale=1.0):
    """Корень рядом со start: секущая от него, без производных."""
    step = max(abs(start), scale, 1.0) * 1e-7
    here, there = start, start + step
    below, above = fun(here), fun(there)
    if below is None or above is None:
        return None
    first = abs(below)
    for _ in range(60):
        if above == below:
            break
        nxt = there - above * (there - here) / (above - below)
        if not math.isfinite(nxt) or abs(nxt - start) > 1e4 * max(scale, 1.0):
            return None
        value = fun(nxt)
        if value is None:
            return None
        here, below, there, above = there, above, nxt, value
        if abs(there - here) <= 1e-16 * max(1.0, abs(there)):
            break
    # Сошлись, если остаток упал на порядки против начального. Мерить его
    # абсолютным порогом нельзя: у одной кривой F идёт единицами, у другой
    # тысячными, и общего числа для обеих не существует.
    room = max(1e-12, 1e-9 * first)
    return there if above is not None and abs(above) <= room else None


def _beside(cur, place, step, axis='x'):
    """Соседняя точка кривой: шаг по одной оси, вторая координата — с кривой."""
    shape = _bent(cur)
    here, there = place
    if axis == 'x':
        moved = here + step
        found = _root_near(lambda t: shape(moved, t), there, max(abs(there), 1.0))
        return None if found is None else (moved, found)
    moved = there + step
    found = _root_near(lambda t: shape(t, moved), here, max(abs(here), 1.0))
    return None if found is None else (found, moved)


def _lean(cur, place, step, axis='x'):
    """Наклон секущей через две соседние точки кривой."""
    ahead = _beside(cur, place, step, axis)
    behind = _beside(cur, place, -step, axis)
    if ahead is None or behind is None:
        return None
    run, rise = ahead[0] - behind[0], ahead[1] - behind[1]
    if axis == 'x':
        return rise / run if run else None
    return run / rise if rise else None      # это dx/dy, а не dy/dx


def _slope(cur, place, step=_CUR_STEP):
    """Наклон кривой в точке, полученный ходьбой по ней.

    Шаг берётся дважды, целиком и вчетверо меньше: если два ответа
    разошлись, точка стоит там, где секущая ещё ничего не говорит —
    у полюса, на изломе или на конце области, — и наклон не выдаётся
    вовсе. Та же осторожность стоит в тесте практикума E3.

    Крутой участок проходится по y: dx/dy там мало и считается точнее,
    а вертикальная касательная получается честным oo вместо 10¹⁵.
    """
    sideways = _lean(cur, place, step, 'y')
    if sideways is not None and abs(sideways) < 1 / _CUR_STEEP:
        fine = _lean(cur, place, step / 4, 'y')
        if fine is None or abs(fine - sideways) > 1e-4 * max(1.0, abs(fine)):
            return None
        best = (16 * fine - sideways) / 15          # уточнение по Ричардсону
        return sp.oo if abs(best) < 1e-12 else 1 / best
    rough = _lean(cur, place, step, 'x')
    if rough is None:
        return None
    fine = _lean(cur, place, step / 4, 'x')
    if fine is None or abs(fine - rough) > 1e-4 * max(1.0, abs(fine)):
        return None
    return (16 * fine - rough) / 15                 # уточнение по Ричардсону


def _stands(cur, place, tol=1e-7):
    """Лежит ли точка на кривой."""
    value = _bent(cur)(*place)
    return value is not None and abs(value) <= tol * max(1.0, abs(place[1]))


def _room(value, digits=3):
    """Половина единицы последней значащей цифры: столько прощает округление."""
    value = abs(float(value))
    if value == 0:
        return 0.5 * 10.0 ** (-digits)
    return 0.5 * 10.0 ** (math.floor(math.log10(value)) - digits + 1)


def _rounds_to(got, want, digits=3):
    """Годится ли got как want, записанный с digits значащими цифрами.

    Экзамен принимает 0.331 там, где на самом деле 0.331078, и 1.84 там,
    где 1.84273. Половина единицы третьей значащей цифры — это 0.0005
    у первого числа и 0.005 у второго, поэтому один допуск на оба не
    годится: он берётся от самого числа.
    """
    got, want = float(got), float(want)
    if got == want:
        return True
    # Допуск берётся по большему из двух: ответ «0» покрывает и 10⁻²³,
    # и это не поблажка, а то, что значит «нуль с тремя цифрами».
    room = max(_room(got, digits), _room(want, digits))
    return abs(got - want) <= room * 1.001


def _snap(cur, place, digits=3):
    """Настоящая точка кривой, которую ответ называет с округлением.

    Ответ «(0.331, −0.743)» не лежит на кривой ни при какой проверке на
    равенство: это три значащие цифры настоящей точки. Проверка находит
    точку кривой при том же x и убеждается, что вторая координата ответа
    округляется в неё же. Дальше меряется наклон в настоящей точке —
    там, где его и спрашивали.
    """
    if _stands(cur, place):
        return place
    shape = _bent(cur)
    here, there = place
    found = _root_near(lambda t: shape(here, t), there, max(abs(there), 1.0))
    if found is not None and _rounds_to(there, found, digits):
        return (here, found)
    found = _root_near(lambda t: shape(t, there), here, max(abs(here), 1.0))
    if found is not None and _rounds_to(here, found, digits):
        return (found, there)
    return None


def _pair(value):
    """Пара ли это координат. sp.Tuple приезжает из тренажёра, где точка
    доходит до проверки через srepr, а не питоновским кортежем."""
    return isinstance(value, (tuple, list, sp.Tuple))


def _only_point(cur, at):
    """Та же точка, что и у _place, но молча: нужна при просмотре окна."""
    if _pair(at):
        try:
            pair = tuple(float(sp.N(sp.sympify(v), _PREC)) for v in at)
        except (TypeError, ValueError):
            return None
        return pair if _stands(cur, pair) else None
    try:
        here = float(sp.N(sp.sympify(at), _PREC))
    except (TypeError, ValueError):
        return None
    kept = _heights(cur, here)
    return (here, kept[0]) if len(kept) == 1 else None


def _place(label, cur, at):
    """Точка кривой: пара чисел, либо один x, если вторая координата одна."""
    _, _, var, dep = cur[:4]
    if _pair(at):
        pair = tuple(float(sp.N(sp.sympify(v), _PREC)) for v in at)
        if not _stands(cur, pair):
            print(f"{NO} {label}: " + _t(
                f"точка ({_say(at[0])}, {_say(at[1])}) не лежит на кривой",
                f"the point ({_say(at[0])}, {_say(at[1])}) is not on the "
                f"curve"))
            return None
        return pair
    here = float(sp.N(sp.sympify(at), _PREC))
    kept = _heights(cur, here)
    if len(kept) != 1:
        print(f"{NO} {label}: " + _t(
            f"при {var} = {_say(at)} кривая проходит через "
            f"{len(kept)} точек — назови обе координаты",
            f"the curve has {len(kept)} points at {var} = {_say(at)} — "
            f"name both coordinates"))
        return None
    return (here, kept[0])


def _straight(got, var=x, dep=y):
    """Прямая, записанная как угодно: (наклон, свободный член) или ('up', c)."""
    item = sp.sympify(got)
    if isinstance(item, sp.Eq):
        left, right = item.lhs, item.rhs
        gap = sp.expand(left - right)
        if not gap.has(dep):                      # вертикальная прямая x = c
            roots = sp.solve(sp.Eq(gap, 0), var)
            return ('up', roots[0]) if len(roots) == 1 else None
        answer = sp.solve(sp.Eq(gap, 0), dep)
        if len(answer) != 1:
            return None
        item = answer[0]
    item = sp.expand(item)
    if item.has(dep):
        return None
    try:
        shape = sp.Poly(item, var)
    except sp.PolynomialError:
        return None
    if shape.degree() > 1:
        return None                               # это не прямая
    coeffs = shape.all_coeffs()
    slope = coeffs[0] if len(coeffs) == 2 else sp.Integer(0)
    return (sp.simplify(slope), sp.simplify(coeffs[-1]))


def _show_straight(line, var=x, dep=y):
    """Прямая словами ответа, а не парой чисел."""
    if line[0] == 'up':
        return f"{var} = {_say(line[1])}"
    return f"{dep} = {sp.simplify(line[0] * var + line[1])}"


def _runs(params):
    """Наборы значений букв: та же машинка, что у производной."""
    return _param_runs(params)


def _fix(item, run):
    """Подставить буквы в кривую, точку или выражение."""
    if run is None or not run:
        return item
    # Ключ берётся как есть: Symbol('a', positive=True) и Symbol('a') —
    # разные символы, и подстановка по имени тихо не срабатывает.
    swap = {name if isinstance(name, sp.Symbol) else sp.Symbol(str(name)): value
            for name, value in run.items()}
    if isinstance(item, tuple) and item and item[0] == 'curve':
        return curve(sp.sympify(item[1]).subs(swap), item[2], item[3])
    if _pair(item):
        return type(item)(sp.sympify(v).subs(swap) for v in item)
    return sp.sympify(item).subs(swap)


def _where_words(run):
    if not run:
        return ''
    return ' ' + _t('при ', 'at ') + ', '.join(
        f'{name} = {value}' for name, value in run.items())


def _sample_points(cur, domain=None, count=5):
    """Несколько точек кривой, на которых наклон считается уверенно."""
    _, _, var, _ = cur[:4]
    lo, hi = (-4.0, 4.0) if domain is None else (float(sp.sympify(domain[0])),
                                                 float(sp.sympify(domain[1])))
    shape = _bent(cur)
    out = []
    for i in range(1, 61):
        here = lo + (hi - lo) * i / 61
        for there in _heights(cur, here):
            lean = _slope(cur, (here, there))
            if lean is None or lean is sp.oo or abs(float(lean)) > 50:
                continue
            out.append(((here, there), float(lean)))
            break
        if len(out) >= count:
            break
    return out


def verify_slope(label, got, cur, at=None, domain=None, params=None):
    """Ответ — наклон кривой: сверяется с ходьбой по самой кривой.

    Семнадцатое понятие равенства ответов. Ни производной, ни формулы
    dy/dx = −F_x/F_y проверка не берёт: она находит на кривой точку слева
    и точку справа и считает наклон секущей через них.

    at — точка, если спрошен наклон в точке; без неё ответ считается
    выражением через x и y, и тогда он сверяется в нескольких точках
    самой кривой. Это и есть смысл «в терминах x и y»: одна запись
    обязана давать верный наклон везде, где кривая проходит.
    """
    if _blank(label, got, at):
        return False
    if cur[1] is Ellipsis:
        # Одна незаполненная ячейка — один пустой квадрат: если ответ уже
        # напечатал его, второй раз про ту же строку говорить незачем.
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    _, _, var, dep = cur[:4]
    claim = sp.sympify(got)
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        here = _fix(cur, run)
        spots = ([( _place(label, here, _fix(at, run)), None)] if at is not None
                 else [(p, m) for p, m in _sample_points(here, domain)])
        if not spots or spots[0][0] is None:
            if at is None:
                print(f"{NO} {label}: " + _t(
                    "не нашлось ни одной точки кривой, где наклон считается",
                    "no point of the curve was usable for a slope"))
            return False
        for place, known in spots:
            want = known if known is not None else _slope(here, place)
            if want is None:
                continue
            mine = claim.subs(run or {}).subs({var: sp.Float(place[0]),
                                              dep: sp.Float(place[1])})
            try:
                mine = float(sp.N(mine, _PREC))
            except (TypeError, ValueError):
                print(f"{NO} {label}: " + _t(
                    "наклон — это число в каждой точке кривой; в ответе "
                    "осталось что-то, что числом не становится",
                    "a slope is a number at every point of the curve; the "
                    "answer does not become one"))
                return False
            if _near(mine, want, _CUR_TOL):
                continue
            if _near(mine, -1 / want if want else sp.oo, _CUR_TOL):
                print(f"{NO} {label}: " + _t(
                    "это наклон нормали, а не касательной",
                    "that is the slope of the normal, not of the tangent")
                    + _where_words(run))
                return False
            if _near(-mine, want, _CUR_TOL):
                print(f"{NO} {label}: " + _t("потерян знак",
                                             "the sign is the wrong way round")
                    + _where_words(run))
                return False
            print(f"{NO} {label}: " + _t(
                f"в точке ({_say(place[0])}, {_say(place[1])}) кривая идёт "
                f"с наклоном {_say(want)}, а не {_say(mine)}",
                f"at ({_say(place[0])}, {_say(place[1])}) the curve runs "
                f"at {_say(want)}, not at {_say(mine)}") + _where_words(run))
            return False
    print(f"{OK} {label}: {claim}")
    return True


def _line_report(label, line, cur, place, want, kind, run):
    """Общий разбор для касательной и нормали."""
    _, _, var, dep = cur[:4]
    target = want if kind == 'tangent' else (
        sp.oo if want == 0 else (0 if want is sp.oo else -1 / want))
    if line[0] == 'up':
        if target is sp.oo and _near(line[1], place[0], _CUR_TOL):
            print(f"{OK} {label}: {_show_straight(line, var, dep)}")
            return True
        print(f"{NO} {label}: " + _t(
            "вертикальная прямая здесь не подходит",
            "a vertical line does not fit here") + _where_words(run))
        return False
    slope, free = (float(sp.N(line[0], _PREC)), float(sp.N(line[1], _PREC)))
    height = slope * place[0] + free
    if not _near(height, place[1], _CUR_TOL) and abs(height - place[1]) > _CUR_TOL:
        if _near(slope, float(target) if target is not sp.oo else 0, _CUR_TOL):
            print(f"{NO} {label}: " + _t(
                f"наклон верный, но прямая не проходит через точку кривой "
                f"({_say(place[0])}, {_say(place[1])})",
                f"the slope is right, but the line misses the point "
                f"({_say(place[0])}, {_say(place[1])}) of the curve")
                + _where_words(run))
            return False
        print(f"{NO} {label}: " + _t(
            f"прямая не проходит через точку ({_say(place[0])}, "
            f"{_say(place[1])})",
            f"the line does not pass through ({_say(place[0])}, "
            f"{_say(place[1])})") + _where_words(run))
        return False
    if target is sp.oo:
        print(f"{NO} {label}: " + _t(
            f"здесь прямая вертикальна, наклона у неё нет",
            "the line is vertical here and has no slope") + _where_words(run))
        return False
    if _near(slope, float(target), _CUR_TOL):
        return True
    other = want if kind == 'normal' else (
        sp.oo if want == 0 else -1 / want)
    if other is not sp.oo and _near(slope, float(other), _CUR_TOL):
        print(f"{NO} {label}: " + _t(
            "это нормаль, а не касательная" if kind == 'tangent'
            else "это касательная, а не нормаль",
            "that is the normal, not the tangent" if kind == 'tangent'
            else "that is the tangent, not the normal") + _where_words(run))
        return False
    if kind == 'normal' and want != 0 and _near(slope, -float(want), _CUR_TOL):
        print(f"{NO} {label}: " + _t(
            "у нормали наклон минус обратный, а не просто со знаком минус",
            "the normal takes minus the reciprocal, not just the minus sign")
            + _where_words(run))
        return False
    if _near(-slope, float(target), _CUR_TOL):
        print(f"{NO} {label}: " + _t(
            "наклон взят с обратным знаком, а не обратный по величине",
            "the sign has been flipped where the reciprocal was needed")
            + _where_words(run))
        return False
    print(f"{NO} {label}: " + _t(
        f"кривая идёт здесь с наклоном {_say(want)}, и прямой полагается "
        f"наклон {_say(target)}, а не {_say(slope)}",
        f"the curve runs at {_say(want)} here, so the line needs slope "
        f"{_say(target)}, not {_say(slope)}") + _where_words(run))
    return False


def _line_check(label, got, cur, at, kind, params):
    if _blank(label, got, at):
        return False
    if cur[1] is Ellipsis:
        # Одна незаполненная ячейка — один пустой квадрат: если ответ уже
        # напечатал его, второй раз про ту же строку говорить незачем.
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    _, _, var, dep = cur[:4]
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    shown = None
    for run in runs:
        line = _straight(_fix(got, run), var, dep)
        if line is None:
            print(f"{NO} {label}: " + _t(
                "это не уравнение прямой", "that is not the equation of a line"))
            return False
        here = _fix(cur, run)
        place = _place(label, here, _fix(at, run))
        if place is None:
            return False
        want = _slope(here, place)
        if want is None:
            print(f"{NO} {label}: " + _t(
                "в этой точке наклон кривой не определяется",
                "the curve has no usable slope at that point"))
            return False
        if not _line_report(label, line, here, place, want, kind, run):
            return False
        shown = shown or _show_straight(_straight(sp.sympify(got), var, dep)
                                        or line, var, dep)
    print(f"{OK} {label}: {shown}")
    return True


def verify_tangent(label, got, cur, at, params=None):
    """Ответ — касательная: прямая, которой кривая держится.

    Проверяется ровно определение и ничего сверх него: точка касания лежит
    и на кривой, и на прямой, а наклон прямой совпадает с наклоном самой
    кривой, полученным ходьбой по ней. Записать ответ можно как угодно —
    выражением 30*x - 97, равенством Eq(y, 30*x - 97) — сравниваются
    прямые, а не строки.
    """
    return _line_check(label, got, cur, at, 'tangent', params)


def verify_normal(label, got, cur, at, params=None):
    """Ответ — нормаль: та же проверка, но произведение наклонов равно −1.

    Отдельная проверка, а не флаг, по одной причине: самый частый промах
    темы — сдать касательную вместо нормали или взять −m вместо −1/m,
    и назвать этот промах можно, только зная, что спрошено.
    """
    return _line_check(label, got, cur, at, 'normal', params)


def _branch(cur, here, near):
    """Точка кривой при данном x, ближайшая к near: продолжение той же ветви."""
    shape = _bent(cur)
    found = _root_near(lambda t: shape(here, t), near, max(abs(near), 1.0))
    return None if found is None else (here, found)


def _hunt(cur, target, lo, hi, grid=_CUR_GRID):
    """Все точки кривой, где наклон равен target: просмотр, а не решение.

    Идём по x слева направо, на каждом шаге собираем точки кривой и
    продолжаем каждую ветвь в ближайшую точку следующего шага. Там, где
    разность «наклон минус искомое» сменила знак, между шагами стоит
    ответ, и он уточняется делением пополам вдоль той же ветви.
    """
    shape, out = _bent(cur), []
    previous = []
    for i in range(grid + 1):
        here = lo + (hi - lo) * i / grid
        current = []
        for root in _heights(cur, here):
            lean = _slope(cur, (here, root))
            gap = (None if lean is None or lean is sp.oo
                   else float(lean) - float(target))
            current.append((root, gap))
        for was, gone in previous:
            if gone is None or not current:
                continue
            root, gap = min(current, key=lambda pair: abs(pair[0] - was))
            if gap is None or abs(root - was) > 20 * (hi - lo) / grid:
                continue
            if gone * gap > 0:
                continue
            left, right, edge = here - (hi - lo) / grid, here, gone
            guess = was
            for _ in range(60):
                mid = (left + right) / 2
                spot = _branch(cur, mid, guess)
                if spot is None:
                    break
                lean = _slope(cur, spot)
                if lean is None or lean is sp.oo:
                    break
                value = float(lean) - float(target)
                if edge * value <= 0:
                    right = mid
                else:
                    left, edge, guess = mid, value, spot[1]
            spot = _branch(cur, (left + right) / 2, guess)
            # Различать точки надо по обеим координатам: у окружности
            # обе горизонтальные касательные стоят при x = 0.
            if spot is not None and all(abs(spot[0] - seen[0]) > 1e-4
                                        or abs(spot[1] - seen[1]) > 1e-4
                                        for seen in out):
                out.append(spot)
        previous = current
    return out


def _as_places(label, got, cur, coordinates):
    """Ответ приводится к списку точек: пара, число или список того и другого."""
    _, _, var, dep = cur[:4]
    items = got if isinstance(got, (list, tuple, set, sp.Tuple)) else [got]
    if coordinates and _pair(got) and len(got) == 2 \
            and not any(_pair(v) for v in got):
        items = [got]                 # это одна точка, а не два числа
    out, written = [], []
    for item in items:
        if _pair(item):
            out.append(tuple(float(sp.N(sp.sympify(v), _PREC)) for v in item))
            written.append(tuple(sp.sympify(v) for v in item))
            continue
        if coordinates:
            print(f"{NO} {label}: " + _t(
                "у точки две координаты — назови обе",
                "a point has two coordinates: name both"))
            return None, None
        here = float(sp.N(sp.sympify(item), _PREC))
        written.append((sp.sympify(item), None))
        roots = _heights(cur, here)
        if len(roots) != 1:
            print(f"{NO} {label}: " + _t(
                f"при {var} = {_say(here)} кривая проходит через "
                f"{len(roots)} точек",
                f"the curve has {len(roots)} points at {var} = {_say(here)}"))
            return None, None
        out.append((here, roots[0]))
    return out, written


def _pin(cur, place, target, digits=3):
    """Настоящая точка кривой с нужным наклоном, названная с округлением.

    Ответ вроде (1.84, −0.538) не лежит на кривой ни при каком допуске:
    округлены обе координаты сразу, и при x = 1.84 кривая идёт уже не там.
    Поэтому проверка не подставляет ответ, а ищет рядом с ним настоящее
    решение — точку, где наклон кривой равен искомому, — и смотрит,
    округляется ли оно в ответ. Ширина поиска берётся из самого ответа:
    столько, сколько могло съесть округление.
    """
    here, there = place
    span = 3 * max(_room(here, digits), 1e-9)
    guess = [there]

    def gap(step):
        spot = _branch(cur, step, guess[0])
        if spot is None:
            return None
        lean = _slope(cur, spot)
        if lean is None or lean is sp.oo:
            return None
        guess[0] = spot[1]
        return float(lean) - float(target)

    for root in sorted(_settle(gap, here - span, here + span, 80),
                       key=lambda t: abs(t - here)):
        spot = _branch(cur, root, there)
        if spot is None:
            continue
        if _rounds_to(here, spot[0], digits) and _rounds_to(there, spot[1],
                                                            digits):
            return spot
    return None


def verify_where(label, got, cur, slope, domain, coordinates=True,
                 params=None):
    """Ответ — точки кривой с заданным наклоном. Обратный ход темы.

    Проверяются три вещи, и каждая из них отдельный балл экзамена: точка
    лежит на кривой, кривая идёт через неё с нужным наклоном, и точек
    названо столько же, сколько их на отрезке из условия. Полнота берётся
    просмотром кривой, а не решением уравнения: искать нечего — наклон
    в каждой точке уже умеет считаться ходьбой.

    coordinates=False — когда вопрос просит только x; вторая координата
    тогда берётся с кривой, и «нашёл x, но не назвал y» перестаёт быть
    ошибкой, потому что y и не спрашивали.
    """
    if _blank(label, got):
        return False
    if cur[1] is Ellipsis:
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        here = _fix(cur, run)
        target = float(sp.N(_fix(slope, run), _PREC))
        mine, written = _as_places(label, got, here, coordinates)
        if mine is None:
            return False
        lo, hi = (float(sp.sympify(domain[0])), float(sp.sympify(domain[1])))
        exact = []
        for place in mine:
            true = _pin(here, place, target)
            if true is None:
                near = _snap(here, place)
                if near is None:
                    print(f"{NO} {label}: " + _t(
                        f"точка ({_say(place[0])}, {_say(place[1])}) не лежит "
                        f"на кривой",
                        f"({_say(place[0])}, {_say(place[1])}) is not on the "
                        f"curve") + _where_words(run))
                    return False
                lean = _slope(here, near)
                if lean is not None and lean is not sp.oo \
                        and _rounds_to(float(lean), target):
                    print(f"{NO} {label}: " + _t(
                        "рядом с этим ответом настоящего решения нет — "
                        "проверь третью значащую цифру",
                        "there is no exact solution next to that answer: "
                        "check the third significant figure")
                        + _where_words(run))
                    return False
                shown = (_t('вертикальна', 'vertical') if lean is sp.oo
                         else _say(lean) if lean is not None
                         else _t('не определён', 'undefined'))
                print(f"{NO} {label}: " + _t(
                    f"в точке ({_say(place[0])}, {_say(place[1])}) наклон "
                    f"{shown}, а нужен {_say(target)}",
                    f"at ({_say(place[0])}, {_say(place[1])}) the slope is "
                    f"{shown}, not {_say(target)}") + _where_words(run))
                return False
            if any(abs(true[0] - seen[0]) < 1e-6 and abs(true[1] - seen[1]) < 1e-6
                   for seen in exact):
                print(f"{NO} {label}: " + _t(
                    "одна и та же точка названа дважды",
                    "the same point is named twice") + _where_words(run))
                return False
            exact.append(true)
            if not lo - _CUR_TOL <= true[0] <= hi + _CUR_TOL:
                print(f"{NO} {label}: " + _t(
                    f"точка ({_say(true[0])}, {_say(true[1])}) лежит вне "
                    f"отрезка из условия",
                    f"({_say(true[0])}, {_say(true[1])}) is outside the "
                    f"interval in the question") + _where_words(run))
                return False
        every = _hunt(here, target, lo, hi)
        if len(every) > len(exact):
            print(f"{NO} {label}: " + _t(
                f"таких точек на отрезке {len(every)}, а названо {len(exact)}",
                f"there are {len(every)} such points on the interval, and "
                f"{len(mine)} are named") + _where_words(run))
            return False
    shown = (', '.join(f"({_wrote(a)}, {_wrote(b)})" for a, b in written)
             if coordinates else ', '.join(_wrote(a) for a, _ in written))
    print(f"{OK} {label}: {shown}")
    return True


def verify_on(label, got, cur, at, params=None):
    """Ответ — вторая координата точки кривой: точка обязана на ней лежать.

    Балл, который в этой теме дают отдельно и теряют чаще прочих. «Найдите
    f(4), если y = 6x − 1 касается графика в x = 4» — это не про наклон
    вовсе: точка касания лежит и на прямой, и на кривой, и потому одно
    число берётся с другой линии.
    """
    if _blank(label, got, at):
        return False
    if cur[1] is Ellipsis:
        # Одна незаполненная ячейка — один пустой квадрат: если ответ уже
        # напечатал его, второй раз про ту же строку говорить незачем.
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        here = _fix(cur, run)
        try:
            place = (float(sp.N(_fix(at, run), _PREC)),
                     float(sp.N(_fix(got, run), _PREC)))
        except (TypeError, ValueError):
            print(f"{NO} {label}: " + _t("это не число",
                                         "that is not a number"))
            return False
        if _snap(here, place) is not None:
            continue
        near = min(_heights(here, place[0]),
                   key=lambda v: abs(v - place[1]), default=None)
        tail = ('' if near is None else _t(
            f", кривая проходит там через {_say(near)}",
            f"; the curve passes through {_say(near)} there"))
        print(f"{NO} {label}: " + _t(
            f"точка ({_say(place[0])}, {_say(place[1])}) не лежит на кривой",
            f"({_say(place[0])}, {_say(place[1])}) is not on the curve")
            + tail + _where_words(run))
        return False
    print(f"{OK} {label}: {sp.sympify(got)}")
    return True


def _lean_at(build, value, at, target):
    """Насколько наклон кривой, построенной по value, отличается от нужного."""
    here = build(sp.Float(value) if not isinstance(value, sp.Basic) else value)
    place = _only_point(here, at)
    if place is None:
        return None
    lean = _slope(here, place)
    if lean is None or lean is sp.oo:
        return None
    return float(lean) - float(target)


def _pin_value(build, near, at, target, digits=3):
    """Настоящее значение постоянной, названное с округлением.

    То же, что _pin делает с точкой: у постоянной, подобранной под наклон,
    третья значащая цифра сдвигает наклон куда сильнее, чем саму букву,
    и сравнивать надо буквы, а не наклоны.
    """
    span = 3 * max(_room(near, digits), 1e-9)
    for root in sorted(_settle(lambda v: _lean_at(build, v, at, target),
                               near - span, near + span, 40),
                       key=lambda v: abs(v - near)):
        if _rounds_to(near, root, digits):
            return root
    return None


def verify_constant(label, got, build, at, slope, window, params=None):
    """Ответ — постоянная, подобранная под наклон: касание как уравнение.

    Восьмой приём темы устроен так, что подставлять ответ некуда: буква
    сидит внутри самой кривой. Поэтому проверка строит кривую из ответа
    и меряет её наклон в точке из условия — ходьбой, как и всё в этом
    разделе. Полнота набора берётся просмотром окна: постоянная пробегает
    его, и всякая смена знака у разности «наклон минус нужный» — ещё
    один ответ.

    build — как из значения буквы получается кривая: обычно
    lambda v: curve(Eq(y, ...v...)).
    """
    if _blank(label, got):
        return False
    values = list(got) if isinstance(got, (list, tuple, set, sp.Tuple)) else [got]
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        target = float(sp.N(_fix(slope, run), _PREC))
        spot = _fix(at, run)
        seen = []
        for item in values:
            near = float(sp.N(_fix(item, run), _PREC))
            true = _pin_value(build, near, spot, target)
            if true is None:
                gap = _lean_at(build, near, spot, target)
                shown = (_t('не определён', 'undefined') if gap is None
                         else _say(gap + target))
                print(f"{NO} {label}: " + _t(
                    f"при этом значении наклон в точке {shown}, "
                    f"а нужен {_say(target)}",
                    f"at that value the slope at the point is {shown}, "
                    f"not {_say(target)}") + _where_words(run))
                return False
            if any(abs(true - was) < 1e-6 for was in seen):
                print(f"{NO} {label}: " + _t(
                    "одно и то же значение названо дважды",
                    "the same value is named twice") + _where_words(run))
                return False
            seen.append(true)
        lo, hi = float(sp.sympify(window[0])), float(sp.sympify(window[1]))
        every, last, steps = 0, None, _CUR_GRID // 2
        for i in range(steps + 1):
            gap = _lean_at(build, lo + (hi - lo) * i / steps, spot, target)
            if gap is not None and last is not None and last * gap < 0:
                every += 1
            last = gap
        if every > len(seen):
            print(f"{NO} {label}: " + _t(
                f"таких значений {every}, а названо {len(seen)}",
                f"there are {every} such values, and {len(seen)} are named")
                + _where_words(run))
            return False
    print(f"{OK} {label}: " + ', '.join(_wrote(v) for v in values))
    return True


def verify_second(label, got, cur, at, params=None):
    """Ответ — вторая производная кривой, посчитанная второй разностью.

    Соотношение дифференцируется дважды на бумаге, а проверка вместо
    этого делает три шага по кривой: слева, в точке и справа. Вторая
    разность делится на квадрат шага, и то же считается вдвое меньшим
    шагом — расхождение двух ответов означает, что мерить здесь нечего.
    """
    if _blank(label, got, at):
        return False
    if cur[1] is Ellipsis:
        # Одна незаполненная ячейка — один пустой квадрат: если ответ уже
        # напечатал его, второй раз про ту же строку говорить незачем.
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        here = _fix(cur, run)
        place = _place(label, here, _fix(at, run))
        if place is None:
            return False
        pair = []
        for step in (2e-2, 1e-2):
            ahead = _beside(here, place, step)
            behind = _beside(here, place, -step)
            if ahead is None or behind is None:
                print(f"{NO} {label}: " + _t(
                    "по кривой отсюда не пройти",
                    "the curve cannot be walked from here"))
                return False
            pair.append((ahead[1] - 2 * place[1] + behind[1]) / step ** 2)
        want = (4 * pair[1] - pair[0]) / 3          # уточнение по Ричардсону
        _, _, var, dep = here[:4]
        mine = sp.sympify(_fix(got, run)).subs({var: sp.Float(place[0]),
                                                dep: sp.Float(place[1])})
        try:
            mine = float(sp.N(mine, _PREC))
        except (TypeError, ValueError):
            print(f"{NO} {label}: " + _t(
                "вторая производная — число в каждой точке кривой; в ответе "
                "осталось что-то, что числом не становится",
                "a second derivative is a number at every point of the curve; "
                "the answer does not become one"))
            return False
        if _near(mine, want, 1e-3):
            continue
        first = _slope(here, place)
        if first is not None and first is not sp.oo \
                and _near(mine, float(first), _CUR_TOL):
            print(f"{NO} {label}: " + _t(
                "это первая производная, а не вторая",
                "that is the first derivative, not the second")
                + _where_words(run))
            return False
        print(f"{NO} {label}: " + _t(
            f"кривая изгибается здесь как {_say(want)}, а не {_say(mine)}",
            f"the curve bends here at {_say(want)}, not at {_say(mine)}")
            + _where_words(run))
        return False
    print(f"{OK} {label}: {sp.sympify(got)}")
    return True


def verify_right_angle(label, got, first, second, at, params=None):
    """Ответ — два наклона в общей точке двух кривых; их произведение −1.

    Три условия, и каждое из них балл схемы оценивания: точка лежит на
    обеих кривых, каждый наклон отвечает своей кривой, произведение равно
    −1. Проверка не считает ни одной производной: оба наклона она
    получает ходьбой по своей кривой.
    """
    if _blank(label, got, at):
        return False
    if first[1] is Ellipsis or second[1] is Ellipsis:
        print(f"⬜ {label}: " + _t("кривая не задана", "no curve yet"))
        return False
    if not _pair(got) or len(got) != 2:
        print(f"{NO} {label}: " + _t(
            "нужны два наклона — по одному на кривую",
            "two slopes are needed, one for each curve"))
        return False
    try:
        runs = _runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        place = None
        leans = []
        for cur, claim in zip((first, second), got):
            here = _fix(cur, run)
            place = _place(label, here, _fix(at, run))
            if place is None:
                return False
            want = _slope(here, place)
            if want is None or want is sp.oo:
                print(f"{NO} {label}: " + _t(
                    "в общей точке наклон одной из кривых не определяется",
                    "one of the curves has no usable slope at the shared point"))
                return False
            mine = float(sp.N(_fix(claim, run), _PREC))
            if not _near(mine, float(want), _CUR_TOL):
                print(f"{NO} {label}: " + _t(
                    f"одна из кривых идёт здесь с наклоном {_say(want)}, "
                    f"а не {_say(mine)}",
                    f"one of the curves runs at {_say(want)} here, "
                    f"not at {_say(mine)}") + _where_words(run))
                return False
            leans.append(mine)
        product = leans[0] * leans[1]
        if not _near(product, -1.0, 1e-3):
            print(f"{NO} {label}: " + _t(
                f"произведение наклонов {_say(product)}, а прямой угол "
                f"требует −1",
                f"the slopes multiply to {_say(product)}, and a right angle "
                f"needs −1") + _where_words(run))
            return False
    print(f"{OK} {label}: " + _t(
        f"наклоны {_say(sp.sympify(got[0]))} и {_say(sp.sympify(got[1]))}, "
        f"произведение −1",
        f"slopes {_say(sp.sympify(got[0]))} and {_say(sp.sympify(got[1]))}, "
        f"product −1"))
    return True
