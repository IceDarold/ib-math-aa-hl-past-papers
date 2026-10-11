"""Дифференциальные уравнения первого порядка (E7): решение, поле, приближение.
"""

import math

import mpmath as mp
import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t, _vanishes
from .tangent import _rounds_to, _say


# ================================================================ поле
# Тридцатое понятие равенства ответов: **решение узнают подстановкой, а
# приближение — тем же шагом, которым его строили**.
#
# Уравнение — это поле наклонов: в каждой точке плоскости оно говорит, под
# каким углом через неё проходит решение. Больше в условии ничего нет, и
# проверке больше ничего не нужно. Записанное решение она подставляет в
# уравнение и смотрит на невязку; неявный ответ она проходит ногами по самой
# кривой, подбирая постоянную так, чтобы кривая прошла через взятую точку, и
# сравнивая её наклон с тем, который требует поле. Поэтому засчитывается
# любая верная форма записи — и явная, и неявная, и домноженная на что
# угодно, — ровно как в markscheme.
#
# Значение решения в точке проверка не берёт из замкнутой формы: формы может
# и не быть. Она идёт по полю от начального условия до нужного x с двадцатью
# пятью знаками (mpmath.odefun, метод Тейлора с адаптивным шагом). Так
# проверяются и те вопросы, где интеграл не берётся.
#
# Приближение Эйлера проверка строит сама: тем же шагом, из той же точки, по
# тому же полю, без округлений по дороге. Отсюда она знает и то, чего в
# ответе не видно, — занижает ломаная или завышает: она сравнивает конец
# ломаной с тем, куда приходит само решение. Знак ошибки не вспоминают по
# вогнутости, его измеряют; а вогнутость, которую спрашивают как
# обоснование, считается из поля: y″ = f_x + f·f_y вдоль решения.

_FIELD_DPS = 25                        # столько знаков у счёта по полю
_TOL = mp.mpf(10) ** -15         # допуск решателя
_ZERO = 1e-7                     # невязка, которая ещё считается нулём
_SCAN = 400                      # точек в просмотре y при поиске точки кривой
_STEP_CAP = 4000                 # больше шагов Эйлера в вопросе не бывает
_SPOTS = (0.6, 1.4, 2.3, 0.9, 1.8)          # x, на которых кривую пробуют
_HEIGHTS = (0.5, 1.7, 2.6, -0.8, 3.4)       # y для тех же проб
_SENSE = {'under': ('under', 'underestimate', 'below', 'less'),
          'over': ('over', 'overestimate', 'above', 'greater')}
_BEND = {'up': ('up', 'concave up', 'upwards'),
         'down': ('down', 'concave down', 'downwards')}

_SOLVED = {}                     # решения задач Коши, посчитанные в этом прогоне


def _mp_number(value):
    """Число sympy как число mpmath, без потери знаков по дороге."""
    return mp.mpf(sp.N(sp.sympify(value), _FIELD_DPS + 5).__str__())


def _side(label, got, words, names):
    """Ответ-слово: какую из сторон он называет. None, если ни одну."""
    said = str(got).strip().strip('\'"').lower()
    for key, spellings in words.items():
        if said in spellings:
            return key
    print(f"{NO} {label}: {said} — " + _t(
        f"ответ здесь одно из слов {names}", f"the answer here is one of {names}"))
    return None


def _field(rhs, var, dep):
    """Правая часть как функция (x, y) для счёта с mpmath."""
    rhs = sp.sympify(rhs)
    spare = sorted(rhs.free_symbols - {var, dep}, key=str)
    if spare:
        raise ValueError(_t(
            'в правой части осталась буква ' + ', '.join(map(str, spare))
            + ': подставьте её значение, иначе поле не числовое',
            'the right-hand side still has the letter '
            + ', '.join(map(str, spare))
            + ' in it: put its value in, or the field is not a number'))
    quick = sp.lambdify((var, dep), rhs, 'mpmath')

    def value(here, there):
        # Точность здесь не поднимают: решатель mpmath сам ведёт счёт с
        # запасом и по дороге сверяет шаги. Поднятая внутри поля точность
        # ломает ему оценку ошибки, и адаптивный шаг уходит в сторону.
        return mp.mpf(quick(here, there))

    return value


def _curve_of(rhs, ic, var, dep):
    """Решение задачи Коши как функция x. Считается один раз на прогон."""
    key = (sp.srepr(sp.sympify(rhs)), str(sp.sympify(ic[0])), str(sp.sympify(ic[1])),
           str(var), str(dep))
    if key in _SOLVED:
        return _SOLVED[key]
    field = _field(rhs, var, dep)
    start, height = _mp_number(ic[0]), _mp_number(ic[1])
    with mp.workdps(_FIELD_DPS):
        ahead = mp.odefun(lambda s, u: [field(s, u[0])], start, [height], tol=_TOL)
        back = mp.odefun(lambda s, u: [-field(2 * start - s, u[0])], start, [height],
                         tol=_TOL)

    def curve(where):
        where = _mp_number(where)
        with mp.workdps(_FIELD_DPS):
            if where >= start:
                return ahead(where)[0]
            return back(2 * start - where)[0]

    _SOLVED[key] = curve
    return curve


def _bend_at(rhs, where, height, var, dep):
    """y″ в точке поля: f_x + f·f_y. Вогнутость решения, не считая решения."""
    rhs = sp.sympify(rhs)
    second = sp.diff(rhs, var) + rhs * sp.diff(rhs, dep)
    return float(sp.N(second.subs({var: sp.Float(str(where)),
                                   dep: sp.Float(str(height))})))


def _told(value, digits, whole):
    """Как ответ выглядит в требуемой записи."""
    if whole:
        return str(int(round(float(value))))
    return f"{float(value):.{digits}g}"


def _number_agrees(got, want, digits, whole):
    """Сходится ли число с тем, что даёт модель."""
    try:
        got = float(sp.N(sp.sympify(got)))
        want = float(want)
    except (TypeError, ValueError, AttributeError):
        return False
    # Промах может быть и неопределённостью: подстановка в особую точку даёт
    # nan, и сравнивать его с ответом нечем.
    if not (math.isfinite(got) and math.isfinite(want)):
        return False
    if whole:
        return int(round(got)) == int(round(want))
    return _rounds_to(got, want, digits)


def _why_number(got, want, digits, whole, blames):
    """Чем мог оказаться неверный ответ. blames: (значение, объяснение)."""
    for value, blame in blames:
        if value is None:
            continue
        if _number_agrees(got, value, digits, whole):
            return blame
    try:
        number = float(sp.N(sp.sympify(got)))
        want = float(want)
    except (TypeError, ValueError, AttributeError):
        return None
    if not (math.isfinite(number) and math.isfinite(want)):
        return None
    if _number_agrees(-number, want, digits, whole):
        return _t("знак потерян", "the sign is lost")
    for power in (1, 2, 3, -1, -2, -3):
        if _number_agrees(number * 10.0 ** power, want, digits, whole):
            return _t("запятая стоит не на том разряде",
                      "the decimal point is in the wrong place")
    if whole and number in (math.floor(want), math.ceil(want)):
        return _t("округлено не до ближайшего целого",
                  "not rounded to the nearest whole number")
    if not whole and _rounds_to(number, want, max(digits - 2, 1)):
        return _t(f"не хватает точности: округление до {digits} знач. цифр",
                  f"not accurate enough: round to {digits} s.f.")
    return None


def _number_verdict(label, got, want, digits, whole, blames=()):
    """Сообщение о числовом ответе, который проверка умеет посчитать сама."""
    if _number_agrees(got, want, digits, whole):
        print(f"{OK} {label}: {_told(got, digits, whole)}")
        return True
    blame = _why_number(got, want, digits, whole, list(blames))
    tail = f" — {blame}" if blame else " — " + _t("не сходится", "no match")
    print(f"{NO} {label}: {_told(got, digits, whole)}{tail}")
    return False


# ================================================================ решение

def put(expr, **letters):
    """Выражение, в котором буквы заменены ответами предыдущих пунктов.

    В экзаменационном вопросе поздние пункты опираются на ранние, и проверка
    должна опираться на них так же: подставляется ответ студента, а не эталон.
    Пока ответ не заполнен, подставлять нечего — и всё выражение остаётся
    незаполненным, чтобы ноутбук проходился сверху вниз и пустым.
    """
    values = dict(letters)
    if expr is Ellipsis or any(value is Ellipsis for value in values.values()):
        return Ellipsis
    places = {sp.Symbol(name): sp.sympify(value) for name, value in values.items()}
    return sp.sympify(expr).subs(places)


def verify_family(label, got, rhs, ic=None, var=x, dep=y, par=None,
                    params=None, span=None, points=None):
    """Неявный ответ F(x, y) = c как решение уравнения dy/dx = rhs.

    Эталон не хранится: проверка идёт по самой кривой. В нескольких точках
    она подбирает постоянную так, чтобы кривая прошла через точку, и
    сравнивает наклон кривой в ней с тем, который требует уравнение.
    Поэтому проходит любая запись одного и того же семейства: x² + y² = k,
    y² = k − x² и (x² + y²)² = k — одни и те же кривые.

    par    — буква семейства (постоянная интегрирования); обычно находится сама
    params — буквы условия и их числовые значения для счёта
    ic     — начальное условие, которому кривая обязана удовлетворять
    """
    if _blank(label, got, rhs):
        return False
    shape = sp.sympify(got)
    if isinstance(shape, sp.Eq):
        shape = shape.lhs - shape.rhs
    rhs = sp.sympify(rhs)
    params = {sp.sympify(name): sp.Float(str(value))
              for name, value in (params or {}).items()}
    if dep not in shape.free_symbols:
        print(f"{NO} {label}: " + _t(
            f"в ответе нет {dep}: это не кривая на плоскости",
            f"the answer has no {dep} in it: this is not a curve"))
        return False
    if par is None:
        spare = sorted(shape.free_symbols - {var, dep} - set(params)
                       - rhs.free_symbols, key=str)
        par = spare[0] if len(spare) == 1 else None

    slope = -sp.diff(shape, var) / sp.diff(shape, dep)
    spots = list(points) if points else [(here, there) for here in _SPOTS
                                         for there in _HEIGHTS]
    if span is not None and not points:
        low, high = (float(sp.N(sp.sympify(edge))) for edge in span)
        spots = [spot for spot in spots if low < spot[0] < high]
    flipped = agreed = 0
    for here, there in spots:
        if agreed >= 3:
            break
        place = {var: sp.Float(str(here)), dep: sp.Float(str(there)), **params}
        if par is not None:
            try:
                roots = sp.solve(shape.subs(place), par)
            except (TypeError, ValueError, NotImplementedError):
                continue
            roots = [r for r in roots if r.is_real is not False]
            if not roots:
                continue
            place[par] = sp.Float(str(sp.N(roots[0])))
        elif abs(float(sp.N(shape.subs(place)))) > _ZERO:
            found = _height_on(shape, place, var, dep)
            if found is None:
                continue
            place[dep] = sp.Float(str(found))
            there = float(found)
        try:
            here_slope = complex(sp.N(slope.subs(place)))
            want = complex(sp.N(rhs.subs(place)))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if not (math.isfinite(here_slope.real) and math.isfinite(want.real)):
            continue
        size = max(1.0, abs(want))
        if abs(here_slope - want) <= _ZERO * size:
            agreed += 1
        elif abs(here_slope + want) <= _ZERO * size:
            flipped += 1
        else:
            print(f"{NO} {label}: " + _t(
                f"в точке ({_say(here)}, {_say(there)}) кривая идёт с наклоном "
                f"{_say(here_slope.real)}, а уравнение требует {_say(want.real)}",
                f"at ({_say(here)}, {_say(there)}) the curve has slope "
                f"{_say(here_slope.real)} while the equation asks for "
                f"{_say(want.real)}"))
            return False
    if flipped and not agreed:
        print(f"{NO} {label}: " + _t("наклон всюду противоположный по знаку",
                                     "the slope has the opposite sign everywhere"))
        return False
    if agreed < 2:
        print(f"{NO} {label}: " + _t(
            "проверить не удалось: кривая не проходит через пробные точки",
            "cannot be checked: the curve misses the sample points"))
        return False
    if ic is not None:
        here, there = ic
        rest = shape.subs({var: sp.sympify(here), dep: sp.sympify(there), **params})
        if not _vanishes(rest, par or var):
            print(f"{NO} {label}: " + _t(
                f"семейство верное, но через ({_say(here)}, {_say(there)}) "
                f"не проходит ни при какой постоянной",
                f"the family is right, but no constant takes it through "
                f"({_say(here)}, {_say(there)})"))
            return False
    print(f"{OK} {label}")
    return True


def _height_on(shape, place, var, dep):
    """y, при котором точка лежит на кривой: просмотр с переменой знака."""
    quick = sp.lambdify(dep, shape.subs({name: value for name, value in place.items()
                                         if name != dep}), 'math')
    step, last, last_value = 20.0 / _SCAN, None, None
    for index in range(_SCAN + 1):
        there = -10.0 + index * step
        try:
            value = float(quick(there))
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            last = None
            continue
        if not math.isfinite(value):
            last = None
            continue
        if last is not None and last_value * value < 0:
            low, high = last, there
            for _ in range(80):
                middle = (low + high) / 2
                try:
                    middle_value = float(quick(middle))
                except (TypeError, ValueError, ZeroDivisionError):
                    break
                if middle_value * last_value <= 0:
                    high = middle
                else:
                    low, last_value = middle, middle_value
            return (low + high) / 2
        last, last_value = there, value
    return None


def verify_solved(label, got, rhs, ic, at, var=x, dep=y, digits=3, whole=False,
                  euler=None):
    """Значение решения задачи Коши в точке at.

    Замкнутая форма не нужна: проверка идёт по полю от начального условия до
    точки at. Отсюда она знает и типовые промахи — ответ, оставшийся
    начальным значением, и ответ, в котором взята скорость вместо величины.

    euler — шаг, которым тот же вопрос просил приблизить ответ раньше. Тогда
    проверка узнаёт и самый частый промах в таких парах: вместо точного
    значения переписано приближение.
    """
    if _blank(label, got, rhs, *ic):
        return False
    curve = _curve_of(rhs, ic, var, dep)
    want = curve(at)
    field = _field(rhs, var, dep)
    broken = None
    if euler is not None:
        with mp.workdps(_FIELD_DPS):
            size = _mp_number(euler)
            count = int(mp.nint((_mp_number(at) - _mp_number(ic[0])) / size))
            here, there = _mp_number(ic[0]), _mp_number(ic[1])
            for _ in range(max(count, 0)):
                there = there + size * field(here, there)
                here = here + size
            broken = float(there)
    return _number_verdict(label, got, want, digits, whole, blames=[
        (broken, _t(f"это ломаная Эйлера с шагом {euler}, а не точное значение",
                    f"this is Euler's broken line with step {euler}, not the "
                    f"exact value")),
        (float(sp.N(sp.sympify(ic[1]))),
         _t("это начальное значение, а не значение в точке",
            "this is the starting value, not the value at the point")),
        (float(field(_mp_number(at), want)),
         _t("это скорость в точке, а не сама величина",
            "this is the rate at the point, not the quantity itself")),
    ])


def verify_field(label, got, rhs, at, var=x, dep=y, digits=3):
    """Наклон, который уравнение даёт в точке: правая часть, посчитанная там."""
    if _blank(label, got, rhs, *at):
        return False
    here, there = at
    place = {var: sp.sympify(here), dep: sp.sympify(there)}
    want = float(sp.N(sp.sympify(rhs).subs(place)))
    swapped = None
    try:
        swapped = float(sp.N(sp.sympify(rhs).subs({var: sp.sympify(there),
                                                   dep: sp.sympify(here)})))
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return _number_verdict(label, got, want, digits, False, blames=[
        (float(sp.N(sp.sympify(there))),
         _t("это сама величина в точке, а не наклон поля в ней",
            "this is the quantity itself, not the slope of the field there")),
        (swapped, _t("x и y перепутаны местами", "x and y are the other way round")),
    ])


def verify_letter(label, got, model, unknown, at, var=x, dep=y, digits=3, span=None):
    """Буква модели, найденная по одному наблюдению.

    model — либо выражение для dep (y = f(x) с буквой), либо соотношение,
    которое обязано выполняться; at — наблюдение: пара (x, y) или набор
    подстановок. Проверка сама решает уравнение относительно буквы, поэтому
    эталон не хранится и любая запись ответа проходит.
    """
    if _blank(label, got, model):
        return False
    model = sp.sympify(model)
    unknown = sp.sympify(unknown)
    if isinstance(at, dict):
        place = {sp.sympify(name): sp.sympify(value) for name, value in at.items()}
        left = model.lhs - model.rhs if isinstance(model, sp.Eq) else model
        equation = left.subs(place)
    else:
        here, there = at
        equation = model.subs(var, sp.sympify(here)) - sp.sympify(there)
    roots = []
    try:
        roots = [r for r in sp.solve(equation, unknown) if r.is_real is not False]
    except (TypeError, ValueError, NotImplementedError):
        roots = []
    if not roots and span is not None:
        found = _scan_for(equation, unknown, span)
        roots = [sp.Float(str(found))] if found is not None else []
    if not roots:
        raise ValueError(_t(
            f'{label}: уравнение модели не решается относительно {unknown} — '
            f'проверять нечем',
            f'{label}: the model equation cannot be solved for {unknown}, so '
            f'there is nothing to check against'))
    for root in roots:
        if _number_agrees(got, float(sp.N(root)), digits, False):
            print(f"{OK} {label}: {_told(got, digits, False)}")
            return True
    want = float(sp.N(roots[0]))
    blame = _why_number(got, want, digits, False, [])
    tail = f" — {blame}" if blame else ""
    if not blame:
        try:
            miss = _say(float(sp.N(equation.subs(unknown, sp.sympify(got)))))
        except (TypeError, ValueError, AttributeError):
            miss = None
        tail = " — " + (_t(f"при этом значении модель промахивается на {miss}",
                           f"with this value the model misses by {miss}")
                        if miss is not None else
                        _t("не сходится", "no match"))
    print(f"{NO} {label}: {_told(got, digits, False)}{tail}")
    return False


def _scan_for(equation, unknown, span):
    """Корень уравнения на промежутке: просмотр с переменой знака."""
    low, high = (float(sp.N(sp.sympify(edge))) for edge in span)
    quick = sp.lambdify(unknown, equation, 'math')
    step = (high - low) / _SCAN
    last = last_value = None
    for index in range(_SCAN + 1):
        here = low + index * step
        try:
            value = float(quick(here))
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            last = None
            continue
        if not math.isfinite(value):
            last = None
            continue
        if last is not None and last_value * value < 0:
            left, right = last, here
            for _ in range(80):
                middle = (left + right) / 2
                middle_value = float(quick(middle))
                if middle_value * last_value <= 0:
                    right = middle
                else:
                    left, last_value = middle, middle_value
            return (left + right) / 2
        last, last_value = here, value
    return None


# ================================================================ подстановка
def verify_substitution(label, got, rhs, var=x, dep=y, ratio=v):
    """Во что подстановка y = vx обращает уравнение: x·dv/dx = h(v).

    Проверка делает подстановку сама и сравнивает с ответом как с функцией
    от v. Типовой промах — потерянное слагаемое v из производной
    произведения — она называет по имени.
    """
    if _blank(label, got, rhs):
        return False
    rhs = sp.sympify(rhs)
    moved = sp.simplify(rhs.subs(dep, ratio * var))
    want = sp.simplify(moved - ratio)
    if _vanishes(sp.sympify(got) - want, ratio):
        print(f"{OK} {label}")
        return True
    if _vanishes(sp.sympify(got) - moved, ratio):
        print(f"{NO} {label}: " + _t(
            "потеряно слагаемое v: производная произведения vx даёт v + x·dv/dx",
            "the term v is missing: differentiating vx gives v + x·dv/dx"))
        return False
    if var in sp.sympify(got).free_symbols:
        print(f"{NO} {label}: " + _t(
            f"в ответе осталось {var}: после подстановки оно должно сократиться",
            f"the answer still has {var} in it: it should cancel after the "
            f"substitution"))
        return False
    print(f"{NO} {label}: " + _t("не то, во что обращается уравнение",
                                 "not what the equation turns into"))
    return False


def verify_factor(label, got, rhs, var=x, dep=y):
    """Интегрирующий множитель уравнения dy/dx = rhs, линейного по y.

    Множитель узнаётся по своему свойству, а не по формуле: I годится, если
    I′ = −P·I, где P — коэффициент при y. Поэтому проходит любой множитель,
    отличающийся постоянной, — как и в markscheme.
    """
    if _blank(label, got, rhs):
        return False
    rhs = sp.sympify(rhs)
    coefficient = sp.simplify(sp.diff(rhs, dep))
    if dep in coefficient.free_symbols:
        raise ValueError(_t(
            f'{label}: уравнение не линейно по {dep} — интегрирующего '
            f'множителя у него нет',
            f'{label}: the equation is not linear in {dep}, so it has no '
            f'integrating factor'))
    factor = sp.sympify(got)
    if dep in factor.free_symbols:
        print(f"{NO} {label}: " + _t(
            f"множитель зависит от {dep}: он должен быть функцией одного {var}",
            f"the factor depends on {dep}: it must be a function of {var} alone"))
        return False
    if _vanishes(sp.diff(factor, var) + coefficient * factor, var):
        print(f"{OK} {label}")
        return True
    if _vanishes(sp.diff(factor, var) - coefficient * factor, var):
        print(f"{NO} {label}: " + _t(
            "знак P(x) взят наоборот: уравнение сначала приводят к виду "
            "dy/dx + P·y = Q",
            "the sign of P(x) is the other way round: first put the equation "
            "in the form dy/dx + P·y = Q"))
        return False
    print(f"{NO} {label}: " + _t(
        "домножение на это не делает левую часть производной произведения",
        "multiplying by this does not turn the left side into the derivative "
        "of a product"))
    return False


def verify_directions(label, got, rhs, var=x, dep=y, slope=None, digits=3):
    """Наклоны прямых y = mx, вдоль которых поле даёт нулевой наклон."""
    if _blank(label, got, rhs):
        return False
    slope = sp.Symbol('m') if slope is None else sp.sympify(slope)
    rhs = sp.sympify(rhs)
    roots = sp.solve(sp.Eq(sp.numer(sp.together(rhs.subs(dep, slope * var))), 0), slope)
    want = sorted({sp.nsimplify(r) for r in roots if r.is_real is not False},
                  key=lambda r: float(sp.N(r)))
    said = got if isinstance(got, (list, tuple, set)) else [got]
    said = sorted(said, key=lambda r: float(sp.N(sp.sympify(r))))
    if len(said) != len(want):
        print(f"{NO} {label}: " + _t(
            f"таких наклонов {len(want)}, а названо {len(said)}",
            f"there are {len(want)} such slopes; the answer names {len(said)}"))
        return False
    for mine, truth in zip(said, want):
        if not _number_agrees(mine, float(sp.N(truth)), max(digits, 6), False):
            print(f"{NO} {label}: {_say(mine)} — " + _t(
                "вдоль этой прямой поле не даёт нулевого наклона",
                "the field does not give a zero slope along this line"))
            return False
    print(f"{OK} {label}: " + ', '.join(str(m) for m in said))
    return True


# ================================================================ приближение
def verify_euler(label, got, rhs, ic, step, at, var=x, dep=y, digits=3,
                 whole=False, report='value'):
    """Ломаная Эйлера с шагом step от ic до at — посчитанная заново.

    report='value' — само приближение; report='sense' — занижает оно или
    завышает (ответ при этом слово 'under' или 'over'); report='error' —
    насколько ломаная промахнулась. Во всех трёх случаях проверка сравнивает
    конец ломаной с тем, куда по полю приходит решение.

    Промежуточные значения не округляются ни разу: именно на этом в
    markscheme теряют последнюю значащую цифру, и проверка называет такой
    промах по имени, а не просто отвергает ответ.
    """
    if _blank(label, got, rhs, *ic):
        return False
    field = _field(rhs, var, dep)
    start, height = _mp_number(ic[0]), _mp_number(ic[1])
    size = _mp_number(step)
    target = _mp_number(at)
    with mp.workdps(_FIELD_DPS):
        count = (target - start) / size
        rounded = int(mp.nint(count))
        if rounded <= 0 or abs(count - rounded) > mp.mpf('1e-9'):
            raise ValueError(_t(
                f'{label}: шаг {step} не делит промежуток от {ic[0]} до {at} '
                f'на целое число шагов',
                f'{label}: a step of {step} does not divide the way from '
                f'{ic[0]} to {at} into whole steps'))
        if rounded > _STEP_CAP:
            raise ValueError(_t(
                f'{label}: {rounded} шагов — это не экзаменационный вопрос, '
                f'а задача для машины',
                f'{label}: {rounded} steps is not an exam question but a job '
                f'for a machine'))
        walk = [height]
        here, there = start, height
        for _ in range(rounded):
            there = there + size * field(here, there)
            here = here + size
            walk.append(there)
    truth = _curve_of(rhs, ic, var, dep)(at)
    if report == 'sense':
        said = _side(label, got, _SENSE, "'under', 'over'")
        if said is None:
            return False
        want = 'under' if walk[-1] < truth else 'over'
        if said == want:
            print(f"{OK} {label}: {said}")
            return True
        print(f"{NO} {label}: {said} — " + _t(
            f"ломаная приходит в {_say(float(walk[-1]))}, а решение в "
            f"{_say(float(truth))}: приближение {'ниже' if want == 'under' else 'выше'}",
            f"the broken line arrives at {_say(float(walk[-1]))} while the "
            f"solution arrives at {_say(float(truth))}: the approximation is "
            f"{'below' if want == 'under' else 'above'}"))
        return False
    if report == 'error':
        gap = abs(float(walk[-1] - truth))
        return _number_verdict(label, got, gap, digits, whole, blames=[
            (float(truth - walk[-1]), _t("знак разности взят наоборот",
                                         "the difference is the other way round")),
            (float(truth), _t("это само точное значение, а не ошибка",
                              "this is the exact value itself, not the error")),
        ])
    if report != 'value':
        raise ValueError(_t(
            f"{label}: report бывает 'value', 'sense' или 'error'",
            f"{label}: report is one of 'value', 'sense', 'error'"))
    rough = _rounded_walk(field, start, height, size, rounded, digits)
    return _number_verdict(label, got, float(walk[-1]), digits, whole, blames=[
        (float(truth), _t("это точное значение, а не приближение Эйлера",
                          "this is the exact value, not Euler's approximation")),
        (float(walk[-2]) if len(walk) > 1 else None,
         _t("шагов на один меньше, чем нужно", "one step short")),
        (float(rough) if rough is not None else None,
         _t("промежуточные значения округлены — округлять можно только итог",
            "the intermediate values are rounded — only the final value is")),
    ])


def _rounded_walk(field, start, height, size, count, digits):
    """Ломаная, посчитанная с округлением на каждом шаге: типовой промах."""
    with mp.workdps(_FIELD_DPS):
        here, there = start, height
        for _ in range(count):
            there = there + size * field(here, there)
            here = here + size
            try:
                there = mp.mpf(f"{float(there):.{digits}g}")
            except (ValueError, OverflowError):
                return None
        return there


def verify_curvature(label, got, rhs, ic, at, var=x, dep=y):
    """Вогнутость решения: 'up' или 'down', посчитанная из самого поля.

    y″ = f_x + f·f_y вдоль решения. Если at — промежуток, он просматривается
    целиком: ответ про вогнутость на отрезке годится, только когда знак на
    нём один.
    """
    if _blank(label, got, rhs, *ic):
        return False
    said = _side(label, got, _BEND, "'up', 'down'")
    if said is None:
        return False
    curve = _curve_of(rhs, ic, var, dep)
    if isinstance(at, (tuple, list)):
        low, high = (float(sp.N(sp.sympify(edge))) for edge in at)
        spots = [low + (high - low) * part / 8 for part in range(1, 8)]
    else:
        spots = [float(sp.N(sp.sympify(at)))]
    signs = []
    for spot in spots:
        signs.append(_bend_at(rhs, spot, float(curve(spot)), var, dep))
    if min(signs) < 0 < max(signs):
        print(f"{NO} {label}: " + _t(
            "на этом промежутке вогнутость меняется, одним словом не ответить",
            "the concavity changes on this interval, one word cannot say it"))
        return False
    want = 'up' if signs[0] > 0 else 'down'
    if said == want:
        print(f"{OK} {label}: {said}")
        return True
    print(f"{NO} {label}: {said} — " + _t(
        f"y″ = {_say(signs[0])} вдоль решения, значит выгиб "
        f"{'вверх' if want == 'up' else 'вниз'}",
        f"y″ = {_say(signs[0])} along the solution, so the curve bends {want}"))
    return False


def verify_inflexion(label, got, rhs, ic, span, var=x, dep=y, digits=3):
    """Наклон прямой y = mx, на которой лежит точка перегиба решения.

    Перегиб ищется по полю: там, где y″ = f_x + f·f_y меняет знак вдоль
    решения. Ответ — отношение y/x в этой точке, в любой записи.
    """
    if _blank(label, got, rhs, *ic):
        return False
    curve = _curve_of(rhs, ic, var, dep)
    low, high = (float(sp.N(sp.sympify(edge))) for edge in span)
    step = (high - low) / 200
    last = last_value = None
    found = None
    for index in range(201):
        here = low + index * step
        try:
            value = _bend_at(rhs, here, float(curve(here)), var, dep)
        except (TypeError, ValueError, ZeroDivisionError):
            last = None
            continue
        if not math.isfinite(value):
            last = None
            continue
        if last is not None and last_value * value < 0:
            left, right = last, here
            for _ in range(60):
                middle = (left + right) / 2
                middle_value = _bend_at(rhs, middle, float(curve(middle)), var, dep)
                if middle_value * last_value <= 0:
                    right = middle
                else:
                    left, last_value = middle, middle_value
            found = (left + right) / 2
            break
        last, last_value = here, value
    if found is None:
        raise ValueError(_t(
            f'{label}: на промежутке {span} решение не перегибается — '
            f'проверять нечего',
            f'{label}: the solution has no point of inflexion on {span}, so '
            f'there is nothing to check'))
    want = float(curve(found)) / found
    return _number_verdict(label, got, want, max(digits, 4), False, blames=[
        (1 / want if want else None,
         _t("отношение перевёрнуто: спрашивают y/x",
            "the ratio is upside down: the question asks for y/x")),
        (found, _t("это x точки перегиба, а не отношение y/x",
                   "this is the x of the point, not the ratio y/x")),
        (float(curve(found)), _t("это y точки перегиба, а не отношение y/x",
                                 "this is the y of the point, not the ratio y/x")),
    ])


# ================================================================ система
def verify_system(label, got, system, var=t, ic=None):
    """Пара функций как решение системы: подстановка в оба уравнения.

    system — словарь {величина: правая часть}; got — те же величины в том же
    порядке. Проверка подставляет пару в каждое уравнение и говорит, какое
    из них не выполняется.
    """
    if _blank(label, *(got if isinstance(got, (tuple, list)) else [got])):
        return False
    system = {sp.sympify(name): sp.sympify(rhs) for name, rhs in system.items()}
    said = got if isinstance(got, (tuple, list)) else [got]
    if len(said) != len(system):
        print(f"{NO} {label}: " + _t(
            f"в системе {len(system)} уравнения, а функций названо {len(said)}",
            f"the system has {len(system)} equations; the answer names "
            f"{len(said)} functions"))
        return False
    place = {name: sp.sympify(value) for name, value in zip(system, said)}
    for name, rhs in system.items():
        resid = sp.diff(place[name], var) - rhs.subs(place)
        if not _vanishes(resid, var):
            print(f"{NO} {label}: " + _t(
                f"уравнение для {name} не выполняется, невязка "
                f"{sp.simplify(resid)}",
                f"the equation for {name} does not hold, residual "
                f"{sp.simplify(resid)}"))
            return False
    if ic is not None:
        for name, (here, there) in ic.items():
            name = sp.sympify(name)
            value = place[name].subs(var, sp.sympify(here))
            if not _vanishes(value - sp.sympify(there), var):
                print(f"{NO} {label}: " + _t(
                    f"{name}({here}) = {sp.simplify(value)}, а нужно {there}",
                    f"{name}({here}) = {sp.simplify(value)} instead of {there}"))
                return False
    print(f"{OK} {label}")
    return True


def verify_eliminated(label, got, system, dep, var=t):
    """Коэффициенты (p, q) в d²y/dt² = p·dy/dt + q·y, полученные из системы.

    Проверка исключает вторую величину сама: дифференцирует уравнение для y
    по системе и сравнивает с p·dy/dt + q·y как тождество по обеим величинам.
    """
    if _blank(label, *(got if isinstance(got, (tuple, list)) else [got])):
        return False
    system = {sp.sympify(name): sp.sympify(rhs) for name, rhs in system.items()}
    dep = sp.sympify(dep)
    first = system[dep]
    second = sum(sp.diff(first, name) * rhs for name, rhs in system.items())
    said = tuple(sp.sympify(value) for value in got)
    if len(said) != 2:
        print(f"{NO} {label}: " + _t("ответ здесь пара (p, q)",
                                     "the answer here is a pair (p, q)"))
        return False
    lean, weight = said
    resid = sp.expand(second - (lean * first + weight * dep))
    if resid == 0:
        print(f"{OK} {label}: p = {lean}, q = {weight}")
        return True
    if sp.expand(second - (weight * first + lean * dep)) == 0:
        print(f"{NO} {label}: " + _t("коэффициенты перепутаны местами",
                                     "the two coefficients are the other way round"))
        return False
    print(f"{NO} {label}: " + _t(
        f"остаётся {resid}, а должно оставаться ноль",
        f"this leaves {resid} instead of nothing"))
    return False


def verify_second_order(label, got, coeffs, var=t, letters=0):
    """Второй порядок: либо показатели λ, либо само общее решение.

    coeffs — (a, b, c) уравнения a·y″ + b·y′ + c·y = 0. Список чисел
    проверяется как набор показателей (и обязан быть полным), выражение —
    подстановкой в уравнение.
    """
    if _blank(label, *(got if isinstance(got, (list, tuple)) else [got])):
        return False
    lead, slope, weight = (sp.sympify(c) for c in coeffs)
    power = sp.Symbol('lambda')
    roots = sorted(sp.solve(lead * power**2 + slope * power + weight, power),
                   key=lambda r: sp.re(sp.N(r)))
    if isinstance(got, (list, tuple, set)):
        said = sorted((sp.sympify(value) for value in got),
                      key=lambda r: sp.re(sp.N(r)))
        if len(said) != len(roots):
            print(f"{NO} {label}: " + _t(
                f"таких показателей {len(roots)}, а названо {len(said)}",
                f"there are {len(roots)} such powers; the answer names "
                f"{len(said)}"))
            return False
        for mine, truth in zip(said, roots):
            if sp.simplify(mine - truth) != 0:
                print(f"{NO} {label}: {mine} — " + _t(
                    f"при этом показателе уравнение даёт "
                    f"{sp.simplify((lead*power**2 + slope*power + weight).subs(power, mine))}"
                    f", а не ноль",
                    f"with this power the equation gives "
                    f"{sp.simplify((lead*power**2 + slope*power + weight).subs(power, mine))}"
                    f", not zero"))
                return False
        print(f"{OK} {label}: " + ', '.join(str(r) for r in said))
        return True
    shape = sp.sympify(got)
    if letters and len(shape.free_symbols - {var}) < letters:
        print(f"{NO} {label}: " + _t(
            f"в ответе {len(shape.free_symbols - {var})} букв, а общее решение "
            f"второго порядка несёт {letters}",
            f"the answer carries {len(shape.free_symbols - {var})} letters "
            f"where the general solution of a second-order equation "
            f"carries {letters}"))
        return False
    if var not in shape.free_symbols:
        print(f"{NO} {label}: " + _t(
            f"в ответе нет {var}: решение — функция времени",
            f"the answer has no {var} in it: a solution is a function of {var}"))
        return False
    resid = (lead * sp.diff(shape, var, 2) + slope * sp.diff(shape, var)
             + weight * shape)
    if _vanishes(resid, var):
        print(f"{OK} {label}")
        return True
    print(f"{NO} {label}: " + _t(
        f"не удовлетворяет уравнению, невязка {sp.simplify(resid)}",
        f"does not satisfy the equation, residual {sp.simplify(resid)}"))
    return False
