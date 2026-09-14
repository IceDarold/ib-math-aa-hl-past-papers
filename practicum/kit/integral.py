"""Первообразная и её семья (E5) и измеренное — площадь, объём, путь (E6).
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .derivative import _param_runs, _PREC
from .tangent import _rounds_to, _say, _where_words, _wrote


# ================================================= первообразная и её семья
# Восемнадцатое понятие равенства ответов: первообразная узнаётся по своей
# производной.
#
# У производной ответ один. У первообразной ответа нет вовсе — есть семейство:
# F и F + 7 верны одинаково, и экзамен принимает обе записи. Сверять поэтому
# не с чем, и хранить нечего. Раздел написан так, что вычислить ответ он
# не может в принципе: внутри нет ни одного интегрирования — ни sympy,
# ни своего. Проверка умеет ровно одно — взять написанное и
# продифференцировать. Совпала производная с подынтегральной функцией —
# написанное лежит в семействе; постоянная исчезает сама, как бы она ни была
# одета: +c, +ln A, +(1/2)ln A.
#
# Это сильнее, чем у производной (E3): там проверка ответ вычисляла и могла
# бы его напечатать. Здесь она умеет только узнавать.
#
# Определённый интеграл — число, и берётся оно не первообразной, а сложением:
# адаптивным Симпсоном по самому подынтегральному выражению. Бесконечный
# предел проходится лестницей, как в verify_limit: 10, 20, 40, ... — пока
# два соседних значения не сойдутся.
#
# Отсюда и остальное. «Покажите, что ∫ от a до s равен G(s)» — это G′(s) = f(s)
# и G(a) = 0, основная теорема, и снова без интегрирования. Замена переменной —
# это g(u(x))·u′(x) = f(x), проверяется подстановкой вперёд. Формула понижения —
# численное тождество между интегралами, проверенное при нескольких n. Ряд
# вместо первообразной — совпадение производной с рядом подынтегральной
# функции до нужной степени.

_ANTI_TOL = 5e-4          # три значащие цифры — столько же принимает экзамен
_QUAD_TOL = 1e-11         # точность квадратуры
_QUAD_DEPTH = 60          # глубина деления отрезка
_QUAD_EDGE = 1e-9         # отступ от края, если на самом краю не считается
_FAR = (10, 20, 40, 80, 160, 320)   # лестница к бесконечному пределу
_ANTI_PLACES = (0.31, -0.47, 0.83, 1.29, -1.11, 1.87, 2.33, -2.71, 3.19)


def _numeric(expr, var, run=None):
    """Выражение числовой функцией одной переменной. None там, где не считается."""
    expr = sp.sympify(expr)
    if run:
        expr = expr.subs(_swap(run))
    try:
        fast = sp.lambdify(var, expr, 'math')
    except Exception:            # noqa: BLE001 — печатники sympy падают по-разному
        # Не всякое выражение lambdify переводит в код: Derivative(re(...)),
        # который приезжает из производной модуля, ему неизвестен. Тогда
        # считаем через evalf — медленнее, но всегда.
        fast = None

    def value(point):
        out = None
        if fast is not None:
            try:
                out = fast(point)
            except (ValueError, ZeroDivisionError, OverflowError, TypeError,
                    ArithmeticError):
                out = None
        if out is None:
            try:
                out = complex(expr.evalf(20, subs={var: point}))
            except (TypeError, ValueError, ZeroDivisionError, AttributeError,
                    OverflowError, NotImplementedError):
                return None
        if isinstance(out, complex):
            if abs(out.imag) > 1e-12 * max(1.0, abs(out.real)):
                return None
            out = out.real
        try:
            out = float(out)
        except (TypeError, ValueError):
            return None
        return out if math.isfinite(out) else None

    return value


def _unbar(expr):
    """Снять модули: у ln|g| и ln g производная одна и та же.

    Ответ темы почти всегда записывают с модулем — так его печатает
    markscheme, — а sp.diff от Abs выдаёт производную действительной части,
    которую дальше не посчитать. Для сравнения производных модуль лишний.
    """
    expr = sp.sympify(expr)
    bars = [piece for piece in expr.atoms(sp.Abs)]
    return expr.subs({bar: bar.args[0] for bar in bars}) if bars else expr


def _swap(run):
    """Словарь подстановки букв: ключ-символ берётся как есть."""
    return {name if isinstance(name, sp.Symbol) else sp.Symbol(str(name)): value
            for name, value in (run or {}).items()}


def _edge(fn, point, inward):
    """Значение у края отрезка: на самом краю функции часто нет (ln 0, 1/√0)."""
    here = fn(point)
    if here is not None:
        return point, here
    for j in range(1, 8):
        near = point + inward * _QUAD_EDGE * 10 ** j
        here = fn(near)
        if here is not None:
            return near, here
    return point, None


def _simpson(fn, left, right, f_left, f_mid, f_right, whole, depth):
    """Адаптивный Симпсон: делим отрезок, пока половинки не сойдутся с целым.

    Ни первообразной, ни sympy — только значения функции и арифметика.
    """
    mid = (left + right) / 2
    lq, rq = (left + mid) / 2, (mid + right) / 2
    f_lq, f_rq = fn(lq), fn(rq)
    if f_lq is None or f_rq is None:
        return None
    step = (right - left) / 12
    part_left = step * (f_left + 4 * f_lq + f_mid)
    part_right = step * (f_mid + 4 * f_rq + f_right)
    both = part_left + part_right
    if depth <= 0 or abs(both - whole) <= 15 * _QUAD_TOL * max(1.0, abs(both)):
        return both + (both - whole) / 15
    a_side = _simpson(fn, left, mid, f_left, f_lq, f_mid, part_left, depth - 1)
    b_side = _simpson(fn, mid, right, f_mid, f_rq, f_right, part_right, depth - 1)
    if a_side is None or b_side is None:
        return None
    return a_side + b_side


def _sum_up(fn, left, right):
    """Определённый интеграл сложением. None — подынтегральная функция не далась."""
    if right < left:
        got = _sum_up(fn, right, left)
        return None if got is None else -got
    if right == left:
        return 0.0
    left, f_left = _edge(fn, left, +1)
    right, f_right = _edge(fn, right, -1)
    if f_left is None or f_right is None:
        return None
    mid = (left + right) / 2
    f_mid = fn(mid)
    if f_mid is None:
        return None
    whole = (right - left) / 6 * (f_left + 4 * f_mid + f_right)
    return _simpson(fn, left, right, f_left, f_mid, f_right, whole, _QUAD_DEPTH)


def _area(f, var, left, right, run=None):
    """Число ∫ f от left до right. Бесконечный предел проходится лестницей."""
    fn = _numeric(f, var, run)
    left = sp.sympify(left).subs(_swap(run)) if run else sp.sympify(left)
    right = sp.sympify(right).subs(_swap(run)) if run else sp.sympify(right)
    if right in (sp.oo, -sp.oo) or left in (sp.oo, -sp.oo):
        return _far_away(fn, left, right)
    try:
        return _sum_up(fn, float(left), float(right))
    except (TypeError, ValueError):
        return None


def _far_away(fn, left, right):
    """Интеграл до бесконечности: лестница отодвигаемых пределов."""
    if left in (sp.oo, -sp.oo) and right in (sp.oo, -sp.oo):
        return None
    if left in (sp.oo, -sp.oo):
        got = _far_away(fn, right, left)
        return None if got is None else -got
    try:
        near = float(left)
    except (TypeError, ValueError):
        return None
    sign = 1 if right == sp.oo else -1
    seen = []
    for step in _FAR:
        got = _sum_up(fn, near, near + sign * step)
        if got is None:
            break
        seen.append(got)
        if len(seen) >= 2 and abs(seen[-1] - seen[-2]) <= _ANTI_TOL * max(
                1.0, abs(seen[-1])):
            return seen[-1]
    return None


def _alike(claim, want, var, domain=None, run=None, tol=1e-7):
    """Одна ли это функция: сначала символьно, потом в точках области."""
    try:
        gap = sp.sympify(claim) - sp.sympify(want)
    except (TypeError, ValueError, sp.SympifyError):
        return False
    if run:
        gap = gap.subs(_swap(run))
    try:
        if sp.simplify(gap) == 0:
            return True
    except (TypeError, ValueError, AttributeError, NotImplementedError,
            RecursionError):
        pass
    if gap.free_symbols - {var}:
        return False
    here = _numeric(gap, var)
    scale = _numeric(want if not run else sp.sympify(want).subs(_swap(run)), var)
    checked = 0
    for point in _places(domain):
        value = here(point)
        if value is None:
            continue
        size = scale(point)
        checked += 1
        if abs(value) > tol * max(1.0, abs(size or 0.0)):
            return False
    return checked >= 3


def _places(domain=None):
    """Точки, в которых сравниваются функции."""
    if domain is None:
        return _ANTI_PLACES
    lo, hi = float(sp.sympify(domain[0])), float(sp.sympify(domain[1]))
    return tuple(lo + (hi - lo) * (i + 0.5) / len(_ANTI_PLACES)
                 for i in range(len(_ANTI_PLACES)))


def _factor_off(claim, f, var, domain, run):
    """Во сколько раз производная написанного отличается от нужной функции.

    Возвращает постоянную c, если (claim)′ = c·f, и None иначе. Это самый
    частый промах темы: ∫cos 3x dx записывают как sin 3x — забыт делитель,
    который приносит внутренняя функция.
    """
    rate = sp.diff(sp.sympify(claim), var)
    try:
        ratio = sp.simplify(sp.cancel(sp.together(rate / sp.sympify(f))))
    except (TypeError, ValueError, AttributeError, NotImplementedError,
            RecursionError, ZeroDivisionError):
        return None
    if run:
        ratio = ratio.subs(_swap(run))
    if ratio.has(var) or not ratio.is_number:
        return None
    return None if ratio == 1 else ratio


def _anti_slips(claim, f, var, domain, run):
    """Промахи темы, собранные из самой f. Возвращает объяснение или None."""
    f = sp.sympify(f)
    if sp.simplify(sp.diff(sp.sympify(claim), var)) == 0:
        return _t(f'написанное не зависит от {var}: продифференцировать его '
                  f'по переменной интегрирования нечего',
                  f'your answer does not depend on {var}: there is nothing to '
                  f'differentiate with respect to the variable of integration')
    if _alike(claim, f, var, domain, run):
        return _t('это сама подынтегральная функция: интегрировать её ещё надо',
                  'this is the integrand itself — it has not been integrated')
    if _alike(claim, sp.diff(f, var), var, domain, run):
        return _t('функция продифференцирована, а не проинтегрирована',
                  'the function has been differentiated, not integrated')
    times = _factor_off(claim, f, var, domain, run)
    if times is not None:
        return _t(
            f'производная вашего ответа ровно в {times} раз отличается от '
            f'подынтегральной функции: при замене внутренней функции '
            f'появляется постоянный множитель, и его легко потерять',
            f'the derivative of your answer is exactly {times} times the '
            f'integrand: the inside function brings a constant factor, '
            f'and it is easy to lose')
    gap = sp.simplify(sp.diff(sp.sympify(claim), var) - f)
    if run:
        gap = gap.subs(_swap(run))
    if gap.is_number and gap != 0:
        return _t(
            f'производная вашего ответа отличается от подынтегральной функции '
            f'на постоянную {gap}: лишнее слагаемое, линейное по {var}',
            f'the derivative of your answer differs from the integrand by the '
            f'constant {gap}: there is a spare term linear in {var}')
    return None


def verify_antiderivative(label, got, f, var=x, domain=None, params=None,
                          through=None):
    """Ответ — первообразная: проверка дифференцирует написанное.

    Восемнадцатое понятие равенства ответов. Эталона нет и быть не может:
    первообразных бесконечно много, они отличаются постоянной. Проверка
    берёт написанное, дифференцирует его и сравнивает с подынтегральной
    функцией из условия. Постоянная при этом исчезает сама — и +c, и +ln A,
    и (1/2)ln A равно годятся, потому что производная у них ноль.

    Сама проинтегрировать проверка не умеет: внутри раздела интегрирования
    нет ни одного. Она умеет только узнать первообразную, если её принесли.

    domain=(a, b) — где сравнивать, если функция определена не всюду.
    params={n: (2, 3, 5)} — прогон при каждом значении буквы.
    through=(x0, y0) — «дана f′ и точка графика, найдите f»: свобода
    постоянной тогда снимается, и ответ обязан ещё и пройти через точку.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    f = sp.sympify(f)
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    bare = _unbar(claim)
    for run in runs:
        if _alike(sp.diff(bare, var), f, var, domain, run):
            continue
        why = _anti_slips(bare, f, var, domain, run)
        if why is None:
            why = _t('производная написанного не равна подынтегральной функции',
                     'the derivative of your answer is not the integrand')
        print(f"{NO} {label}: {why}{_where_words(run)}")
        return False
    if through is not None:
        spot, height = sp.sympify(through[0]), sp.sympify(through[1])
        for run in runs:
            here = _number(claim.subs(var, spot), run)
            if here is None:
                print(f"{NO} {label}: " + _t(
                    'производная верна, но постоянная интегрирования так '
                    'и осталась буквой: точка на графике дана как раз '
                    'затем, чтобы её найти',
                    'the derivative is right, but the constant of integration '
                    'is still a letter: the point on the graph was given in '
                    'order to find it') + _where_words(run))
                return False
            if abs(here - (_number(height, run) or 0)) > _ANTI_TOL:
                print(f"{NO} {label}: " + _t(
                    f'производная верна, но график не проходит через точку '
                    f'({spot}, {height}): при {var} = {spot} написанное даёт '
                    f'{_say(here)}. Постоянную интегрирования надо было '
                    f'найти, а не оставить',
                    f'the derivative is right, but the graph misses the point '
                    f'({spot}, {height}): at {var} = {spot} your answer gives '
                    f'{_say(here)}. The constant of integration had to be '
                    f'found, not left')
                    + _where_words(run))
                return False
    print(f"{OK} {label}: {claim}")
    return True


def verify_integral(label, got, f, a, b, var=x, params=None, tol=None):
    """Ответ — число определённого интеграла: считается сложением, не формулой.

    Значение берётся адаптивным Симпсоном прямо по подынтегральному
    выражению из условия; первообразная не ищется и не хранится. Ответ
    принимается в любой записи — 2*(E - 1/E) и 4.7008 сравниваются числами.

    b=oo — интеграл до бесконечности: пределы отодвигаются лестницей,
    пока два соседних значения не сойдутся.
    """
    if _blank(label, got, f, a, b):
        return False
    claim = sp.sympify(got)
    tol = _ANTI_TOL if tol is None else tol
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        want = _area(f, var, a, b, run)
        if want is None:
            print(f"{NO} {label}: " + _t(
                'подынтегральное выражение не считается на этом отрезке',
                'the integrand cannot be evaluated over this interval')
                + _where_words(run))
            return False
        value = _number(claim, run)
        if value is None:
            print(f"{NO} {label}: " + _t(
                f'{claim} — это не число', f'{claim} is not a number')
                + _where_words(run))
            return False
        if abs(value - want) <= tol * max(1.0, abs(want)):
            continue
        if abs(value + want) <= tol * max(1.0, abs(want)):
            print(f"{NO} {label}: " + _t(
                'знак противоположный: пределы переставлены местами',
                'the sign is the wrong way round: the limits have been swapped')
                + _where_words(run))
            return False
        print(f"{NO} {label}: " + _t(
            'не сходится с интегралом из условия',
            'this does not match the integral in the question')
            + _where_words(run))
        return False
    print(f"{OK} {label}: {_wrote(claim)}")
    return True


def _number(value, run=None):
    """Число из ответа, в какой бы записи оно ни было."""
    try:
        value = sp.sympify(value)
        if run:
            value = value.subs(_swap(run))
        out = complex(value.evalf(_PREC))
    except (TypeError, ValueError, AttributeError, ZeroDivisionError):
        return None
    if abs(out.imag) > 1e-9 * max(1.0, abs(out.real)):
        return None
    return out.real if math.isfinite(out.real) else None


def verify_accumulated(label, got, f, lower, var=t, upper=None, params=None,
                       domain=None):
    """Ответ — накопленное с начала: ∫ от lower до s, записанное функцией s.

    Проверяется основной теоремой, а не интегрированием: производная
    написанного по верхнему пределу обязана равняться подынтегральной
    функции в этой точке, а в самой точке lower написанное обязано быть
    нулём. Обе половины нужны: первая ловит неверную первообразную,
    вторая — потерянный нижний предел.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    upper = var if upper is None else sp.sympify(upper)
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    rate = sp.sympify(f).subs(var, upper) if upper != var else sp.sympify(f)
    for run in runs:
        if not _alike(sp.diff(_unbar(claim), upper), rate, upper, domain, run):
            print(f"{NO} {label}: " + _t(
                'производная написанного по верхнему пределу не равна '
                'подынтегральной функции',
                'differentiating your answer with respect to the upper limit '
                'does not give the integrand') + _where_words(run))
            return False
        start = _number(claim.subs(upper, sp.sympify(lower)), run)
        if start is None or abs(start) > _ANTI_TOL:
            print(f"{NO} {label}: " + _t(
                f'при верхнем пределе {lower} интеграл обязан быть нулём, '
                f'а написанное даёт {_say(start) if start is not None else claim}: '
                f'потерян нижний предел',
                f'with upper limit {lower} the integral has to be zero, but '
                f'your answer gives '
                f'{_say(start) if start is not None else claim}: '
                f'the lower limit has been dropped') + _where_words(run))
            return False
    print(f"{OK} {label}: {claim}")
    return True


def verify_transformed(label, got, f, sub, var=x, new=u, domain=None):
    """Ответ — подынтегральное выражение после замены переменной.

    Замена законна, когда g(u(x))·u′(x) = f(x): проверка подставляет замену
    вперёд и сравнивает с исходным выражением. Интегрировать для этого
    не нужно — и не приходится.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    sub = sp.sympify(sub)
    if claim.has(var) and not claim.has(new):
        print(f"{NO} {label}: " + _t(
            f'после замены выражение должно быть записано через {new}, '
            f'а в нём осталось {var}',
            f'after the substitution the integrand has to be written in {new}, '
            f'but {var} is still there'))
        return False
    pushed = _unbar(claim).subs(new, sub) * sp.diff(sub, var)
    if not _alike(pushed, f, var, domain):
        if _alike(_unbar(claim).subs(new, sub), f, var, domain):
            print(f"{NO} {label}: " + _t(
                'потерян множитель замены: dx выражается через du, и это '
                'делит на производную замены',
                'the substitution factor is missing: dx has to be written in '
                'terms of du, which divides by the derivative of the '
                'substitution'))
            return False
        print(f"{NO} {label}: " + _t(
            'подстановка замены обратно не даёт исходного выражения',
            'putting the substitution back does not return the original '
            'integrand'))
        return False
    print(f"{OK} {label}: {claim}")
    return True


def verify_reduction(label, got, term, index, of, var=x, span=(0.3, 1.2),
                     values=(2, 3, 4, 5)):
    """Ответ — формула понижения: тождество между интегралами.

    got записывается через of(m) — «интеграл от term при index = m» — и
    обычные слагаемые вне интеграла. Проверка при каждом n из values
    считает обе стороны на отрезке span сложением: слагаемые с of(m)
    берутся квадратурой, остальные подставляются в пределы. Первообразная
    ни разу не ищется, поэтому формулу проверка узнаёт, но не выводит.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    lo, hi = float(sp.sympify(span[0])), float(sp.sympify(span[1]))
    cache = {}

    def whole(power):
        key = sp.nsimplify(power)
        if key not in cache:
            cache[key] = _area(sp.sympify(term).subs(index, key), var, lo, hi)
        return cache[key]

    for n_value in values:
        want = whole(n_value)
        if want is None:
            print(f"{NO} {label}: " + _t(
                f'интеграл при {index} = {n_value} не считается',
                f'the integral with {index} = {n_value} cannot be evaluated'))
            return False
        total = 0.0
        for piece in sp.Add.make_args(claim.subs(index, n_value)):
            inside = [f for f in piece.atoms(sp.Function) if f.func == of]
            if len(inside) > 1:
                print(f"{NO} {label}: " + _t(
                    f'в слагаемом {piece} больше одного интеграла',
                    f'the term {piece} holds more than one integral'))
                return False
            if inside:
                weight = sp.simplify(piece / inside[0])
                if weight.has(var) or weight.has(of):
                    print(f"{NO} {label}: " + _t(
                        f'множитель при интеграле в {piece} зависит от {var}',
                        f'the factor in front of the integral in {piece} '
                        f'depends on {var}'))
                    return False
                part = whole(inside[0].args[0])
                if part is None:
                    print(f"{NO} {label}: " + _t(
                        f'интеграл {inside[0]} не считается',
                        f'the integral {inside[0]} cannot be evaluated'))
                    return False
                total += float(weight) * part
            else:
                edge = _numeric(piece, var)
                top, bottom = edge(hi), edge(lo)
                if top is None or bottom is None:
                    print(f"{NO} {label}: " + _t(
                        f'слагаемое {piece} не считается на концах отрезка',
                        f'the term {piece} cannot be evaluated at the ends '
                        f'of the interval'))
                    return False
                total += top - bottom
        if abs(total - want) > _ANTI_TOL * max(1.0, abs(want)):
            print(f"{NO} {label}: " + _t(
                f'при {index} = {n_value} стороны не равны: слева {_say(want)}, '
                f'справа {_say(total)}',
                f'with {index} = {n_value} the two sides differ: '
                f'{_say(want)} against {_say(total)}'))
            return False
    print(f"{OK} {label}: {claim}")
    return True


def verify_termwise(label, got, f, upto, var=x):
    """Ответ — интеграл ряда: первообразной в конечном виде нет.

    Проверяется тем же вопросом, что и обычная первообразная, но с точностью
    до нужной степени: производная написанного обязана совпасть с рядом
    подынтегральной функции до члена степени upto − 1 включительно.
    Постоянная так же свободна, а вот лишние степени — нет: ответ длиннее
    заказанного проверка не принимает.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    f = sp.sympify(f)
    try:
        gap = sp.series(sp.diff(_unbar(claim), var) - f, var, 0, upto).removeO()
    except (TypeError, ValueError, NotImplementedError, sp.PoleError):
        print(f"{NO} {label}: " + _t(
            'ряд для этой разности не строится',
            'the series for this difference cannot be built'))
        return False
    if sp.simplify(sp.expand(gap)) != 0:
        if _alike(claim, sp.series(f, var, 0, upto).removeO(), var):
            print(f"{NO} {label}: " + _t(
                'это ряд самой подынтегральной функции: его ещё надо '
                'проинтегрировать почленно',
                'this is the series of the integrand itself — it still has to '
                'be integrated term by term'))
            return False
        print(f"{NO} {label}: " + _t(
            f'производная написанного расходится с рядом подынтегральной '
            f'функции уже в члене {sp.expand(gap).as_ordered_terms()[0]}',
            f'the derivative of your answer already parts from the series of '
            f'the integrand at the term '
            f'{sp.expand(gap).as_ordered_terms()[0]}'))
        return False
    order = _degree_in(claim, var)
    if order is not None and order > upto:
        print(f"{NO} {label}: " + _t(
            f'в ответе есть степень {order}, а заказана степень {upto}',
            f'the answer carries a power {order} where {upto} was asked for'))
        return False
    print(f"{OK} {label}: {claim}")
    return True


def _degree_in(expr, var):
    """Старшая степень var в выражении. None — это не многочлен."""
    try:
        return int(sp.Poly(expr, var).degree())
    except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError, ValueError):
        return None


# ============================================== измеренное и его измерение
# Девятнадцатое понятие равенства ответов: измеренное узнаётся повторным
# измерением, а не повторением выкладки.
#
# Ответ здесь — число, и число это что-то меряет: площадь области, объём
# тела, длину пройденного пути. Сверять такое число со вторым таким же,
# полученным той же формулой, бессмысленно: совпадут и две одинаковые
# ошибки. Поэтому раздел меряет заново — и меряет по определению меры,
# а не по формуле из справочника.
#
# Площадь области — сумма тонких полос между двумя границами. Объём тела
# вращения — сумма объёмов тонких дисков πR²Δ, и кольца πR²Δ − πr²Δ.
# Площадь поверхности вращения — сумма боковых поверхностей усечённых
# конусов π(y₁+y₂)·Δl, где Δl — настоящая длина звена; производной кривой
# в этой сумме нет вовсе. Путь — полная вариация положения: точка идёт
# мелким шагом, и складывается, насколько она сдвинулась на каждом.
#
# Отсюда главное свойство раздела: он не берёт производных. Ни одной.
# У соседнего раздела (E5) обратное правило — он не берёт интегралов
# ни одного; он умеет только дифференцировать. Вместе эти два раздела —
# две половины основной теоремы, и ни одна не умеет работы другой.
#
# Раздел не решает и уравнений. Точка, где кривые пересекаются, ищется
# делением пополам по смене знака; момент, где скорость меняет знак,
# не ищется совсем — идущая мелким шагом точка проходит его сама.
# Ученик обязан разбить отрезок нулями скорости; проверка обязана
# просто пройти путь.
#
# Сравнение чисел идёт округлением: экзамен принимает три значащие цифры,
# и проверка принимает ровно столько же — 176000 годится там, где на самом
# деле 176323. Там, где ответ обязан быть точным, digits поднимают.

_STRIPS = 400             # с чего начинается дробление отрезка
_STRIP_STEPS = 8          # сколько раз его удваивать
_STRIP_TOL = 1e-9         # когда две соседние ступени считаются сошедшимися
_CROSS_SCAN = 720         # узлов при поиске пересечений
_CROSS_HALVES = 60        # делений пополам на каждое пересечение


def _pace(f, var, a, b, run=None, steps=_STRIPS):
    """Прогулка по отрезку мелким шагом: сдвиг на каждом шаге отдельно.

    Шаг i — это f в его середине, умноженная на ширину шага. Дальше из
    этого списка складывается что угодно: площадь — суммой модулей,
    перемещение — суммой со знаком, путь — суммой модулей сдвигов.
    Одна прогулка, много мер.
    """
    value = _numeric(f, var, run)
    lo, hi = _number(a, run), _number(b, run)
    if lo is None or hi is None:
        return None
    width = (hi - lo) / steps
    out = []
    for i in range(steps):
        here = value(lo + (i + 0.5) * width)
        if here is None:
            return None
        out.append(here * width)
    return out


def _sum_slabs(shape, f, var, a, b, run=None):
    """Мера по всё более мелкому дроблению, пока две ступени не сойдутся.

    shape говорит, что складывать: 'signed' — полосы со знаком,
    'total' — их модули. Дробление удваивается, пока соседние суммы
    не перестанут расходиться.
    """
    was = None
    steps = _STRIPS
    for _ in range(_STRIP_STEPS):
        slabs = _pace(f, var, a, b, run, steps)
        if slabs is None:
            return None
        now = sum(slabs) if shape == 'signed' else sum(abs(s) for s in slabs)
        if was is not None and abs(now - was) <= _STRIP_TOL * (1.0 + abs(now)):
            return now
        was = now
        steps *= 2
    return was


def _spread(top, bottom, var, a, b, run=None, shape='total'):
    """Площадь между двумя границами: сумма полос |верх − низ|.

    Какая граница выше, проверка не выясняет и выяснять не должна:
    модуль на каждой полосе делает это сам, полоса за полосой.
    Поэтому смена мест внутри отрезка ничего не ломает.
    """
    gap = sp.sympify(top) - sp.sympify(bottom)
    return _sum_slabs(shape, gap, var, a, b, run)


def _discs(outer, inner, var, a, b, run=None):
    """Объём тела вращения: сумма тонких дисков и колец.

    Радиус — расстояние от оси до кривой, то есть модуль значения;
    вычитается всегда квадрат внутреннего радиуса, а не сам радиус.
    """
    big, small = sp.sympify(outer), sp.sympify(inner)
    ring = sp.pi * (big ** 2 - small ** 2)
    return _sum_slabs('signed', ring, var, a, b, run)


def _frustums(curve, var, a, b, run=None, steps=_STRIPS):
    """Площадь поверхности вращения: сумма боковых поверхностей усечённых конусов.

    У усечённого конуса с радиусами y₁ и y₂ и образующей Δl боковая
    поверхность равна π(y₁ + y₂)Δl. Δl здесь — настоящая длина звена
    ломаной, √(Δx² + Δy²); производной кривой в этой сумме нет.
    Это и есть определение площади поверхности, а не формула для неё.
    """
    value = _numeric(curve, var, run)
    lo, hi = _number(a, run), _number(b, run)
    if lo is None or hi is None:
        return None
    was = None
    for _ in range(_STRIP_STEPS):
        width = (hi - lo) / steps
        here, tall = lo, value(lo)
        if tall is None:
            return None
        total = 0.0
        for i in range(1, steps + 1):
            there = lo + i * width
            high = value(there)
            if high is None:
                return None
            total += math.pi * (tall + high) * math.hypot(there - here, high - tall)
            here, tall = there, high
        if was is not None and abs(total - was) <= _STRIP_TOL * (1.0 + abs(total)):
            return total
        was = total
        steps *= 2
    return was


def _crossings(top, bottom, var, window, run=None):
    """Где две границы встречаются: смена знака и деление пополам.

    Уравнение top = bottom не решается — раздел уравнений не решает.
    Разность считается в узлах сетки, и там, где она меняет знак,
    место встречи зажимается делением пополам.
    """
    gap = _numeric(sp.sympify(top) - sp.sympify(bottom), var, run)
    lo, hi = _number(window[0], run), _number(window[1], run)
    if lo is None or hi is None:
        return []
    step = (hi - lo) / _CROSS_SCAN
    found = []
    here, was = lo, gap(lo)
    for i in range(1, _CROSS_SCAN + 1):
        there = lo + i * step
        now = gap(there)
        if was is not None and now is not None and was * now <= 0:
            if was == 0:
                found.append(here)
            elif now != 0 or i == _CROSS_SCAN:
                left, right = here, there
                for _ in range(_CROSS_HALVES):
                    mid = 0.5 * (left + right)
                    value = gap(mid)
                    if value is None:
                        break
                    if (was > 0) == (value > 0):
                        left = mid
                    else:
                        right = mid
                found.append(0.5 * (left + right))
        here, was = there, now
    tidy = []
    for place in found:
        if not tidy or abs(place - tidy[-1]) > 10 * step:
            tidy.append(place)
    return tidy


def _fits(claim, want, digits):
    """Число сходится с измеренным — с точностью, с какой оно записано."""
    return _rounds_to(claim, want, digits) or \
        abs(claim - want) <= 1e-9 * max(1.0, abs(want))


def _measured(label, got, want, run, digits, named=()):
    """Общий хвост всех проверок раздела: сверить число и назвать промах.

    named — список (значение, объяснение): если ответ сходится не
    с измеренным, а с одним из них, печатается объяснение, а не «не
    сходится». Так проверка отличает потерянное π от перепутанной оси.
    """
    value = _number(got, run)
    if value is None:
        print(f"{NO} {label}: " + _t(f'{got} — это не число',
                                     f'{got} is not a number') + _where_words(run))
        return False
    if _fits(value, want, digits):
        return True
    for other, why in named:
        if other is not None and _fits(value, other, digits):
            print(f"{NO} {label}: {why}{_where_words(run)}")
            return False
    print(f"{NO} {label}: " + _t(
        'не сходится с тем, что вышло при измерении',
        'this does not match the measurement') + _where_words(run))
    return False


def verify_region(label, got, top, bottom=0, a=None, b=None, var=x,
                params=None, digits=3, window=(-8, 8)):
    """Ответ — площадь: она измеряется полосами, а не берётся формулой.

    Девятнадцатое понятие равенства ответов. Проверка складывает тонкие
    полосы |верх − низ| по отрезку и сравнивает сумму с ответом. Какая
    из границ выше, она не выясняет: модуль стоит на каждой полосе
    отдельно, поэтому область, где кривые меняются местами, считается
    правильно сама собой.

    a и b можно не давать: тогда пределы берутся от первой до последней
    встречи границ внутри window — проверка находит их делением пополам
    по смене знака, а не решением уравнения.

    Именованные промахи: сумма со знаком вместо суммы модулей (куски под
    осью вычлись), противоположный знак (вычтено наоборот), половина
    (область симметрична, а удвоить забыли).
    """
    # Пределы тоже проверяются на пустоту: в обратном чтении задачи ответ
    # ученика стоит именно пределом, и пустым он не должен ронять ячейку.
    if _blank(label, got, top, bottom, *[edge for edge in (a, b)
                                         if edge is not None]):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        lo, hi = a, b
        if lo is None or hi is None:
            meet = _crossings(top, bottom, var, window, run)
            if len(meet) < 2:
                print(f"{NO} {label}: " + _t(
                    'границы области не пересекаются там, где её ищут',
                    'the boundaries do not meet where the region is looked for')
                    + _where_words(run))
                return False
            lo, hi = meet[0], meet[-1]
        want = _spread(top, bottom, var, lo, hi, run)
        if want is None:
            print(f"{NO} {label}: " + _t(
                'область не измеряется: граница не считается на этом отрезке',
                'the region cannot be measured: a boundary fails on this interval')
                + _where_words(run))
            return False
        signed = _spread(top, bottom, var, lo, hi, run, shape='signed')
        named = []
        # Разность знак не меняла, а сумма вышла со знаком минус — значит
        # вычли наоборот, и это другой промах, чем «куски под осью».
        if signed is not None and abs(abs(signed) - want) > 1e-9 * max(1.0, want):
            named.append((signed, _t(
                'это интеграл, а не площадь: куски под осью вычлись вместо '
                'того, чтобы прибавиться. Площадь складывают по модулю',
                'this is the integral, not the area: the pieces below the axis '
                'were subtracted instead of added. Area adds up in absolute value')))
        named += [
            (-want, _t('знак противоположный: вычтено наоборот, а площадь '
                       'отрицательной не бывает',
                       'the sign is the wrong way round: the subtraction went '
                       'the other way, and an area is never negative')),
            (want / 2, _t('это ровно половина измеренного. Если область '
                          'симметрична относительно y = x и вы считали '
                          'половину — её надо удвоить',
                          'this is exactly half of what was measured. If the '
                          'region is symmetric about y = x and you measured '
                          'one half, it has to be doubled')),
            (2 * want, _t('это ровно вдвое больше измеренного',
                          'this is exactly twice what was measured')),
        ]
        if not _measured(label, got, want, run, digits, named):
            return False
    print(f"{OK} {label}: {_wrote(sp.sympify(got))}")
    return True


def verify_solid(label, got, outer, a, b, inner=0, var=x, axis='x',
                  params=None, digits=3):
    """Ответ — объём тела вращения: он складывается из дисков.

    Проверка режет тело плоскостями, перпендикулярными оси, и складывает
    πR²Δ — а для кольца πR²Δ − πr²Δ. Формулы V = π∫y²dx внутри нет:
    есть стопка дисков, из которой она и получается.

    outer — расстояние от оси до дальней границы как функция var, inner —
    до ближней. Вокруг оси y это значит, что outer выражают через y
    и берут var=y: проверке всё равно, какая буква, ей нужен радиус.

    Именованные промахи: потерянное π, невозведённый в квадрат радиус,
    разность радиусов вместо разности квадратов, площадь вместо объёма.
    """
    if _blank(label, got, outer, a, b, inner):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        want = _discs(outer, inner, var, a, b, run)
        if want is None:
            print(f"{NO} {label}: " + _t(
                'тело не измеряется: радиус не считается на этом отрезке',
                'the solid cannot be measured: the radius fails on this interval')
                + _where_words(run))
            return False
        flat = _spread(outer, inner, var, a, b, run)
        plain = _sum_slabs('signed', sp.pi * (sp.sympify(outer) - sp.sympify(inner)),
                           var, a, b, run)
        gap = _sum_slabs('signed', sp.pi * (sp.sympify(outer) - sp.sympify(inner)) ** 2,
                         var, a, b, run)
        named = [
            (want / math.pi, _t(
                'π потеряно: сложены квадраты радиусов, а диск это πR²',
                'π has been dropped: you added squares of radii, but a disc is πR²')),
            (plain, _t(
                'радиус не возведён в квадрат: у диска площадь πR², а не πR',
                'the radius was not squared: a disc has area πR², not πR')),
            (flat, _t(
                'это площадь области, а не объём тела: диски не набраны',
                'this is the area of the region, not the volume of the solid')),
        ]
        if sp.sympify(inner) != 0:
            named.append((gap, _t(
                'вычтены радиусы, а не их квадраты: кольцо это π(R² − r²), '
                'а не π(R − r)²',
                'the radii were subtracted, not their squares: a washer is '
                'π(R² − r²), not π(R − r)²')))
        if not _measured(label, got, want, run, digits, named):
            return False
    turn = _t('вокруг оси ', 'about the ') + str(axis)
    print(f"{OK} {label}: {_wrote(sp.sympify(got))} ({turn})")
    return True


def verify_surface(label, got, curve, a, b, var=x, params=None, digits=3):
    """Ответ — площадь поверхности вращения: она набирается усечёнными конусами.

    Кривая ломается на звенья, каждое звено при вращении даёт усечённый
    конус с боковой поверхностью π(y₁ + y₂)·Δl, и они складываются.
    Δl берётся как длина звена, √(Δx² + Δy²); ни dy/dx, ни корня
    √(1 + (dy/dx)²) в проверке нет. Формула из условия проверяется тем,
    что даёт тот же ответ, а не тем, что переписана.

    Именованные промахи: 2π заменено на π, y забыт под интегралом
    (осталась длина дуги), посчитана половина поверхности.
    """
    if _blank(label, got, curve, a, b):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        want = _frustums(curve, var, a, b, run)
        if want is None:
            print(f"{NO} {label}: " + _t(
                'поверхность не измеряется: кривая не считается на этом отрезке',
                'the surface cannot be measured: the curve fails on this interval')
                + _where_words(run))
            return False
        length = _arc_of(curve, var, a, b, run)
        named = [
            (want / 2, _t(
                'вдвое меньше: у поверхности вращения множитель 2π, а не π — '
                'или посчитана половина кривой',
                'half the value: a surface of revolution carries 2π, not π — '
                'or only half the curve was taken')),
            (2 * want, _t('вдвое больше: поверхность посчитана дважды',
                          'twice the value: the surface has been counted twice')),
            (length, _t(
                'это длина кривой, а не площадь поверхности: множитель y '
                'под интегралом потерян',
                'this is the length of the curve, not the area of the surface: '
                'the factor y has been dropped')),
        ]
        if not _measured(label, got, want, run, digits, named):
            return False
    print(f"{OK} {label}: {_wrote(sp.sympify(got))}")
    return True


def _arc_of(curve, var, a, b, run=None, steps=_STRIPS):
    """Длина кривой ломаной: нужна, чтобы узнать промах «y потерян»."""
    value = _numeric(curve, var, run)
    lo, hi = _number(a, run), _number(b, run)
    if lo is None or hi is None:
        return None
    width = (hi - lo) / steps
    here, tall = lo, value(lo)
    if tall is None:
        return None
    total = 0.0
    for i in range(1, steps + 1):
        there = lo + i * width
        high = value(there)
        if high is None:
            return None
        total += math.hypot(there - here, high - tall)
        here, tall = there, high
    return total


def verify_travelled(label, got, v, a, b, var=t, params=None, digits=3):
    """Ответ — пройденный путь: точка идёт мелким шагом, сдвиги складываются.

    Путь — полная вариация положения, и проверка меряет именно её:
    отрезок времени дробится, на каждом шаге считается, насколько точка
    сдвинулась, и складываются модули сдвигов. Момент, когда скорость
    меняет знак, не ищется вовсе — идущая точка проходит его сама.
    Ученик обязан этот момент найти; проверка обязана просто пройти.

    Именованный промах здесь главный в теме: если ответ сходится
    с перемещением, значит модуль не поставлен.
    """
    if _blank(label, got, v, a, b):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        want = _sum_slabs('total', v, var, a, b, run)
        shift = _sum_slabs('signed', v, var, a, b, run)
        if want is None or shift is None:
            print(f"{NO} {label}: " + _t(
                'путь не измеряется: скорость не считается на этом отрезке',
                'the path cannot be measured: the velocity fails on this interval')
                + _where_words(run))
            return False
        named = []
        if abs(shift - want) > 1e-9 * max(1.0, want):
            named.append((shift, _t(
                'это перемещение, а не путь: куски назад вычлись. Путь '
                'складывают по модулю — ∫|v|dt, а не ∫v dt',
                'this is the displacement, not the distance: the backwards '
                'pieces cancelled. Distance adds up in absolute value — '
                '∫|v|dt, not ∫v dt')))
            named.append((-abs(shift), _t(
                'это перемещение со знаком минус: путь не бывает отрицательным',
                'this is the displacement with a minus sign: a distance is '
                'never negative')))
        named.append((-want, _t('путь не бывает отрицательным',
                                'a distance is never negative')))
        if not _measured(label, got, want, run, digits, named):
            return False
    print(f"{OK} {label}: {_wrote(sp.sympify(got))}")
    return True


def verify_position(label, got, v, a, b, var=t, start=0, params=None, digits=3):
    """Ответ — перемещение или положение: сумма сдвигов со знаком.

    start=0 — это перемещение за время от a до b. start=s(a) — это
    положение в момент b, и тогда начальное значение прибавляется:
    «s(0) = 0» в условии сказано затем, чтобы его подставили.

    Именованный промах, обратный предыдущему: если ответ сходится
    с путём, значит модуль поставлен там, где его не просили.
    """
    if _blank(label, got, v, a, b, start):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        shift = _sum_slabs('signed', v, var, a, b, run)
        if shift is None:
            print(f"{NO} {label}: " + _t(
                'перемещение не измеряется: скорость не считается на этом отрезке',
                'the displacement cannot be measured: the velocity fails here')
                + _where_words(run))
            return False
        first = _number(start, run)
        if first is None:
            print(f"{NO} {label}: " + _t(
                'начальное положение не число', 'the starting position is not a number')
                + _where_words(run))
            return False
        want = first + shift
        path = _sum_slabs('total', v, var, a, b, run)
        named = []
        if path is not None and abs(path - abs(shift)) > 1e-9 * max(1.0, path):
            named.append((first + path, _t(
                'это пройденный путь, а не перемещение: модуль поставлен '
                'там, где его не просили',
                'this is the distance travelled, not the displacement: the '
                'absolute value was taken where it was not asked for')))
        if first != 0:
            named.append((shift, _t(
                'начальное положение не прибавлено: его дали затем, чтобы '
                'найти постоянную интегрирования',
                'the starting position has not been added: it was given in '
                'order to fix the constant of integration')))
        named.append((-want, _t('знак противоположный: пределы переставлены',
                                'the sign is the wrong way round: the limits '
                                'have been swapped')))
        if not _measured(label, got, want, run, digits, named):
            return False
    print(f"{OK} {label}: {_wrote(sp.sympify(got))}")
    return True


def verify_amount(label, got, rate, a, b=None, var=t, start=0, at=None,
                  params=None, digits=3):
    """Ответ — накопленное по скорости накопления: числом или функцией времени.

    Накопленное к моменту s — это start плюс сумма полос скорости
    от a до s. Если ответ записан выражением от var («find d(t)»),
    он проверяется в нескольких моментах сразу: совпасть случайно
    в четырёх точках выражение не может.

    at=(t₁, t₂, …) — где сверять. По умолчанию четыре точки внутри
    отрезка; b нужен только затем, чтобы их расставить.
    """
    if _blank(label, got, rate, a, start, *([] if b is None else [b])):
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    claim = sp.sympify(got)
    moments = at
    if moments is None:
        if b is None:
            print(f"{NO} {label}: " + _t('не сказано, к какому моменту считать',
                                         'no moment to accumulate up to'))
            return False
        lo, hi = _number(a, runs[0]), _number(b, runs[0])
        if lo is None or hi is None:
            print(f"{NO} {label}: " + _t('отрезок времени не число',
                                         'the time interval is not a number'))
            return False
        moments = (hi,) if not claim.has(var) else \
            tuple(lo + (hi - lo) * share for share in (0.23, 0.51, 0.78, 1.0))
    for run in runs:
        first = _number(start, run)
        if first is None:
            print(f"{NO} {label}: " + _t('начальное значение не число',
                                         'the starting amount is not a number')
                  + _where_words(run))
            return False
        for moment in moments:
            piled = _sum_slabs('signed', rate, var, a, moment, run)
            if piled is None:
                print(f"{NO} {label}: " + _t(
                    'накопленное не измеряется: скорость не считается',
                    'the amount cannot be measured: the rate fails here')
                    + _where_words(run))
                return False
            want = first + piled
            here = claim.subs(var, sp.Float(moment, 20)) if claim.has(var) else claim
            named = [(piled, _t(
                'начальное значение не прибавлено: d(0) дали затем, чтобы '
                'найти постоянную',
                'the starting amount has not been added: d(0) was given in '
                'order to find the constant'))] if first != 0 else []
            mark = label if len(moments) == 1 else f'{label} ({var} = {_say(moment)})'
            if not _measured(mark, here, want, run, digits, named):
                return False
    print(f"{OK} {label}: {_wrote(claim)}")
    return True
