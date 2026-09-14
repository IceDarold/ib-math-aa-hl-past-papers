"""Пределы (E1), ряды Маклорена (E2) и производная (E3).

`_PREC` и `_param_runs` отсюда берут и остальные темы анализа.
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _SERIES_FILL, _t
from .functions import _scan_roots


# --- пределы ----------------------------------------------------------------

_LADDER = (1, 2, 3, 4, 5, 6, 7, 8)
_PREC = 60


def _param_runs(params):
    """{n: (2, 3, 7)} -> [{n: 2}, {n: 3}, {n: 7}]. Списки идут параллельно."""
    if not params:
        return [{}]
    names = list(params)
    columns = [tuple(params[name]) for name in names]
    width = len(columns[0])
    if any(len(col) != width for col in columns):
        raise ValueError(_t('params: списки значений должны быть одной длины',
                            'params: the value lists must all be the same length'))
    return [{names[i]: columns[i][j] for i in range(len(names))}
            for j in range(width)]


def _approach(point, side):
    """Лестницы точек, подходящих к point, по сторонам: {сторона: [(имя, точка)]}.

    Каждая лестница идёт от грубой ступени к тонкой, и решает всегда самая
    тонкая: сходимость видна на ней, а не в среднем по лестнице.
    """
    if point in (sp.oo, -sp.oo):
        sign = 1 if point == sp.oo else -1
        return {str(point): [(f'{sign * 10**j}', sp.Integer(sign * 10**j))
                             for j in _LADDER]}
    base = sp.sympify(point)
    sides = ('+', '-') if side is None else (side,)
    out = {}
    for s in sides:
        step = 1 if s == '+' else -1
        out[s] = [(f'{base} {"+" if step > 0 else "-"} 1e-{j}',
                   base + sp.Rational(step, 10**j)) for j in _LADDER]
    return out


def _sample(expr, var, place):
    """Значение expr в точке place с запасом разрядов. None — не вычислилось."""
    try:
        # evalf(subs=...) считает численно и не раскрывает точную подстановку:
        # (1/2)**10**8 при обычном subs — целое на тридцать миллионов цифр,
        # и лестница на бесконечности зависает на первой же ступени.
        value = expr.evalf(_PREC, subs={var: place})
    except (TypeError, ValueError, ZeroDivisionError, NotImplementedError,
            AttributeError, OverflowError):
        return None
    if value.has(sp.zoo, sp.nan) or not value.is_number:
        return None
    try:
        cvalue = complex(value)
    except (TypeError, ValueError):
        return None
    if cvalue != cvalue or abs(cvalue.imag) > 1e-12 * max(1.0, abs(cvalue.real)):
        return None
    return cvalue.real


def _walk(expr, var, point, side):
    """Значения по каждой стороне: {сторона: [(имя, значение)]}, грубые впереди."""
    out = {}
    for name, rungs in _approach(point, side).items():
        seen = [(place_name, _sample(expr, var, place))
                for place_name, place in rungs]
        out[name] = [(place_name, value) for place_name, value in seen
                     if value is not None]
    return out


def verify_limit(label, got, expr, var=x, point=0, side=None, params=None,
                 tol=1e-6):
    """Ответ — предел: проверяется приближением, а не сверкой с числом.

    Десятое понятие равенства ответов в серии. У предела нет значения,
    которое можно взять и сравнить: он определён тем, к чему выражение
    подходит. Поэтому проверка и подходит — подставляет в само выражение
    из условия точки, приближающиеся к point, и требует, чтобы названное
    число оказалось тем, к чему эти значения сходятся. Эталона не хранится
    вовсе: ошибиться вместе с проверкой нельзя, потому что сверять не с чем.

    Двусторонняя по умолчанию, и обе стороны обязаны сойтись в одно.
    side='+' или '-' — когда выражение живёт только с одной стороны.
    point принимает oo и -oo.

    params={n: (2, 3, 7)} — когда ответ выражен через параметр: прогон идёт
    при каждом его значении, и предел обязан сойтись при всех.

    Считает всегда самая тонкая ступень лестницы, а не средняя: у медленной
    дроби вроде (3x-1)/(2x+1) на x = 10^5 ошибка ещё 10^-5, и по ней ответ
    не отличить от соседнего.

    Ловит две вещи, на которых теряют баллы. Первая: подстановку вместо
    предела — ответ, в котором осталась переменная, отвергается сразу.
    Вторая: остановку на полпути — после одного применения правила Лопиталя
    форма нередко всё ещё 0/0, и число, снятое с этой строки, не сходится.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    expr = sp.sympify(expr)
    if claim.has(var):
        print(f"{NO} {label}: " + _t(
            f"в ответе осталась {var}: предел — число (или выражение через "
            f"параметры), а не выражение от {var}",
            f"the answer still has {var} in it: a limit is a number (or an "
            f"expression in the parameters), not an expression in {var}"))
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        here = expr.subs(run) if run else expr
        want = claim.subs(run) if run else claim
        where = ('' if not run else ' ' + _t('при ', 'at ')
                 + ', '.join(f'{name} = {value}' for name, value in run.items()))
        free = want.free_symbols
        if free:
            print(f"{NO} {label}: " + _t(
                f"в ответе остались неизвестные: "
                f"{', '.join(sorted(map(str, free)))}",
                f"the answer still has unknowns in it: "
                f"{', '.join(sorted(map(str, free)))}"))
            return False
        for name, seen in _walk(here, var, point, side).items():
            if len(seen) < 3:
                print(f"{NO} {label}: " + _t(
                    f"выражение не удаётся вычислить рядом с {var} = {point}",
                    f"the expression cannot be evaluated near {var} = {point}")
                    + where)
                return False
            place, value = seen[-1]
            if want in (sp.oo, -sp.oo):
                sign = 1 if want == sp.oo else -1
                if sign * value < 1e6 or sign * value < abs(seen[0][1]):
                    print(f"{NO} {label}: " + _t(
                        f"значения не уходят в {want}: при {place} выражение "
                        f"равно {sig(value, 6)}",
                        f"the values do not run off to {want}: at {place} the "
                        f"expression is {sig(value, 6)}") + where)
                    return False
                continue
            target = float(want)
            span = tol * max(1.0, abs(target))
            error, coarse = abs(value - target), abs(seen[0][1] - target)
            if error > span or error > coarse + span:
                print(f"{NO} {label}: " + _t(
                    f"при {place} выражение равно {sig(value, 6)}, а не "
                    f"{sig(target, 6)}: значения сходятся не туда",
                    f"at {place} the expression is {sig(value, 6)}, not "
                    f"{sig(target, 6)}: the values are not settling there")
                    + where)
                return False
    print(f"{OK} {label}: {claim}")
    return True


_FORMS = {'0/0': '0/0',
          'oo/oo': 'oo/oo', 'inf/inf': 'oo/oo', '∞/∞': 'oo/oo'}


def _tendency(expr, var, point, side, run):
    """Куда идёт выражение: 'zero', 'infinite', 'finite'. None — не видно."""
    expr = sp.sympify(expr).subs(run) if run else sp.sympify(expr)
    verdicts = set()
    for _, seen in _walk(expr, var, point, side).items():
        if len(seen) < 3:
            return None
        first, last = abs(seen[0][1]), abs(seen[-1][1])
        if last < 1e-6 and last <= first:
            verdicts.add('zero')
        elif last > 1e5 and last >= first:
            verdicts.add('infinite')
        else:
            verdicts.add('finite')
    return verdicts.pop() if len(verdicts) == 1 else None


def verify_indeterminate(label, got, num, den, var=x, point=0, side=None,
                         params=None):
    """Ответ — сама неопределённость: '0/0' или 'oo/oo'.

    «Show that the limit is in indeterminate form» стоит в архиве отдельным
    баллом, и балл этот за проверку, а не за вычисление: без неё правило
    Лопиталя неприменимо, а второе его применение без повторной проверки —
    стандартная потеря баллов. Поэтому числитель и знаменатель проходят
    лестницу порознь, и названная форма обязана совпасть с тем, что видно.
    """
    if _blank(label, got):
        return False
    claim = _FORMS.get(str(got).strip().replace(' ', '').lower())
    if claim is None:
        print(f"{NO} {label}: " + _t(
            f"форма записывается строкой '0/0' или 'oo/oo', а не {got!r}",
            f"the form is written as the string '0/0' or 'oo/oo', not {got!r}"))
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    word = {'zero': '0', 'infinite': 'oo',
            'finite': _t('конечному числу', 'a finite number')}
    for run in runs:
        where = ('' if not run else ' ' + _t('при ', 'at ')
                 + ', '.join(f'{name} = {value}' for name, value in run.items()))
        top = _tendency(num, var, point, side, run)
        bottom = _tendency(den, var, point, side, run)
        if top is None or bottom is None:
            print(f"{NO} {label}: " + _t(
                f"не удаётся проследить поведение рядом с {var} = {point}",
                f"cannot follow the behaviour near {var} = {point}") + where)
            return False
        actual = {('zero', 'zero'): '0/0',
                  ('infinite', 'infinite'): 'oo/oo'}.get((top, bottom))
        if actual is None:
            print(f"{NO} {label}: " + _t(
                f"неопределённости нет: числитель идёт к {word[top]}, "
                f"знаменатель к {word[bottom]}",
                f"there is no indeterminate form here: the numerator goes to "
                f"{word[top]} and the denominator to {word[bottom]}") + where)
            return False
        if actual != claim:
            print(f"{NO} {label}: " + _t(
                f"форма на самом деле {actual}: числитель идёт к {word[top]}, "
                f"знаменатель к {word[bottom]}",
                f"the form is actually {actual}: the numerator goes to "
                f"{word[top]} and the denominator to {word[bottom]}") + where)
            return False
    print(f"{OK} {label}: {claim}")
    return True


# --- ряды Маклорена ----------------------------------------------------------

_TAIL_SAMPLES = (0.017, -0.023, 0.031, -0.041)
_SERIES_DEPTH = 40


def _plural(count):
    """Номер русской формы существительного: 0 — «член», 1 — «члена», 2 — «членов».

    Сами слова живут внутри `_t`, иначе check_language видит кириллицу
    в литерале и справедливо ругается: строка вне `_t` рано или поздно
    напечатается посреди английского ноутбука.
    """
    tail = count % 10
    if count % 100 in (11, 12, 13, 14):
        return 2
    return {1: 0, 2: 1, 3: 1, 4: 1}.get(tail, 2)


def _poly_terms(expr, var):
    """[(степень, коэффициент)] по возрастанию. None — это не многочлен."""
    e = sp.expand(sp.sympify(expr))
    try:
        poly = sp.Poly(e, var)
    except (sp.PolynomialError, sp.GeneratorsNeeded):
        return None
    if not e.free_symbols or var not in e.free_symbols:
        # Постоянная — тоже многочлен, нулевой степени.
        return [(0, e)] if e != 0 else []
    out = [(int(power[0]), coeff) for power, coeff in
           zip(poly.monoms(), poly.coeffs()) if coeff != 0]
    return sorted(out)


def _first_terms(f, var, count, run):
    """Степени первых count ненулевых членов ряда f. None — не разложилось.

    Считается по самой функции из условия: «первые два ненулевых члена» —
    требование к f, а не к ответу, и глубина, на которую надо разложить,
    известна только ей. У sin(x²) это x² и x⁶, у 4x·sin(x²)cos(x²) — x³
    и x⁷; фиксированной глубины, годной для всех, не существует.
    """
    here = sp.sympify(f).subs(run) if run else sp.sympify(f)
    depth = 4
    while depth <= _SERIES_DEPTH:
        try:
            head = sp.expand(sp.series(here, var, 0, depth).removeO())
        except (ValueError, TypeError, NotImplementedError,
                sp.PoleError, ZeroDivisionError):
            return None
        powers = [power for power, coeff in (_poly_terms(head, var) or [])
                  if sp.simplify(coeff) != 0]
        if len(powers) >= count:
            return powers[:count]
        depth *= 2
    return None


def _tail_order(f, got, var, need, run):
    """Наименьшая степень, на которой ответ расходится с f. None — сходится.

    Разность f − P должна обнуляться до need включительно. Сначала честное
    разложение; если в остатке что-то осталось, оно ещё раз проверяется
    численно — simplify не всегда доводит верный ответ до нуля, а значения
    в нескольких точках доводят.
    """
    here = sp.sympify(f).subs(run) if run else sp.sympify(f)
    claim = sp.sympify(got).subs(run) if run else sp.sympify(got)
    try:
        tail = sp.expand(sp.series(here - claim, var, 0, need + 1).removeO())
    except (ValueError, TypeError, NotImplementedError,
            sp.PoleError, ZeroDivisionError):
        return 'unreadable'
    for power, coeff in (_poly_terms(tail, var) or []):
        if power > need:
            continue
        if sp.simplify(coeff) == 0:
            continue
        rest = coeff.free_symbols
        if rest:
            continue                      # с буквой внутри решает прогон по params
        if all(abs(complex((coeff * var**power).evalf(
                _PREC, subs={var: place}))) < 1e-40 for place in _TAIL_SAMPLES):
            continue
        return power
    return None


def verify_maclaurin(label, got, f, order=None, terms=None, var=x, params=None):
    """Ответ — отрезок ряда Маклорена: проверяется прилеганием, не сверкой.

    Одиннадцатое понятие равенства ответов в серии. Ряд Маклорена — это не
    какой-то многочлен, который надо угадать, а единственный многочлен
    данной степени, прилегающий к функции в нуле теснее всех остальных:
    разность f − P обязана обнулиться до заказанной степени включительно.
    Отсюда и проверка. Она берёт функцию из условия, вычитает написанное
    и смотрит, с какой степени начинается остаток. Эталона не хранится:
    сверять не с чем, потому что верный ответ определён самой f.

    order=k — «up to and including the term in x^k»: разность обязана быть
    o(x^k). terms=k — «the first k non-zero terms»: глубина берётся из самой
    f, потому что у sin(x²) это x² и x⁶, а у 4x·sin(x²)cos(x²) — x³ и x⁷,
    и одной глубины на всех не существует.

    params={n: (2, 5, 8)} — когда в ответе стоит буква: прогон идёт при
    каждом её значении.

    Чего проверка не делает: не отвергает лишние верные члены сверх
    заказанных — ни при order, ни при terms. Схема оценивания их тоже
    не отвергает и говорит это прямым текстом: «condone presence of any
    additional terms once the first two correct terms are seen».
    """
    if _blank(label, got):
        return False
    if (order is None) == (terms is None):
        raise ValueError(_t('нужно ровно одно из order и terms',
                            'give exactly one of order and terms'))
    claim = sp.sympify(got)
    shape = _poly_terms(claim, var)
    if shape is None:
        print(f"{NO} {label}: " + _t(
            f"ответ должен быть многочленом от {var}: ряд обрывают, а не "
            f"оставляют функцию как есть",
            f"the answer has to be a polynomial in {var}: a series is cut "
            f"short, not left as the function itself"))
        return False
    try:
        runs = _param_runs(params)
    except ValueError as why:
        print(f"{NO} {label}: {why}")
        return False
    for run in runs:
        where = ('' if not run else ' ' + _t('при ', 'at ')
                 + ', '.join(f'{name} = {value}' for name, value in run.items()))
        need = order
        if terms is not None:
            powers = _first_terms(f, var, terms, run)
            if powers is None:
                print(f"{NO} {label}: " + _t(
                    "не удаётся разложить функцию из условия",
                    "the function from the question cannot be expanded")
                    + where)
                return False
            need = powers[-1]
            here = [power for power, coeff in shape
                    if sp.simplify(coeff.subs(run) if run else coeff) != 0]
            # Лишние верные члены не отвергаются: схема оценивания мая 2024
            # пишет об этом прямо — «condone presence of any additional terms
            # once the first two correct terms are seen». Недостача ловится
            # и без счёта, остатком, но сказать про неё счётом понятнее.
            if len(here) < terms:
                print(f"{NO} {label}: " + _t(
                    f"в ответе {len(here)} "
                    + ('ненулевой член', 'ненулевых члена',
                       'ненулевых членов')[_plural(len(here))]
                    + f", а просят {terms}",
                    f"the answer has {len(here)} non-zero "
                    f"term{'' if len(here) == 1 else 's'} and the "
                    f"question asks for {terms}") + where)
                return False
        bad = _tail_order(f, claim, var, need, run)
        if bad == 'unreadable':
            print(f"{NO} {label}: " + _t(
                "не удаётся разложить функцию из условия",
                "the function from the question cannot be expanded") + where)
            return False
        if bad is not None:
            power = _t(f'свободный член', 'constant term') if bad == 0 else (
                _t(f'член с {var}^{bad}', f'the {var}^{bad} term')
                if bad > 1 else _t(f'член с {var}', f'the {var} term'))
            print(f"{NO} {label}: " + _t(
                f"{power} расходится с функцией; всё, что ниже, сходится",
                f"{power} does not agree with the function; everything "
                f"below it does") + where)
            return False
    print(f"{OK} {label}: {sp.expand(claim)}")
    return True


def verify_series_solution(label, got, rhs, ic, order, var=x, dep=y):
    """Ответ — начало ряда Маклорена для решения уравнения dy/dvar = rhs.

    Функции здесь нет вовсе: она задана уравнением и начальным условием,
    и формулы для неё может не существовать в замкнутом виде. Поэтому
    и проверять приходится не прилеганием к функции, а самим уравнением.

    Многочлен P — начало ряда решения до x^order включительно тогда и только
    тогда, когда P(0) равно начальному условию и невязка P′ − rhs(P)
    обнуляется до x^(order−1). Оценка тугая: ошибись P в члене x^k, и
    невязка сломается ровно на x^(k−1).

    Эталона нет: и уравнение, и начальное условие стоят в самом вопросе.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    if _poly_terms(claim, var) is None:
        print(f"{NO} {label}: " + _t(
            f"ответ должен быть многочленом от {var}",
            f"the answer has to be a polynomial in {var}"))
        return False
    start = sp.simplify(claim.subs(var, 0))
    if sp.simplify(start - sp.sympify(ic)) != 0:
        print(f"{NO} {label}: " + _t(
            f"свободный член равен {start}, а начальное условие — {ic}",
            f"the constant term is {start}, but the initial condition is {ic}"))
        return False
    bad = _tail_order(sp.sympify(rhs).subs(dep, claim), sp.diff(claim, var),
                      var, order - 1, {})
    if bad == 'unreadable':
        print(f"{NO} {label}: " + _t("не удаётся разложить невязку",
                                     "the residual cannot be expanded"))
        return False
    if bad is not None:
        power = bad + 1
        print(f"{NO} {label}: " + _t(
            f"уравнению удовлетворяет не всё: первым расходится член "
            f"с {var}^{power}",
            f"the equation is not satisfied all the way: the first term that "
            f"goes wrong is the {var}^{power} one"))
        return False
    print(f"{OK} {label}: {sp.expand(claim)}")
    return True


def verify_terms(label, got, term, bound, var=k, strict=True):
    """Ответ — сколько членов ряда нужно взять, чтобы ошибка влезла в bound.

    У знакочередующегося ряда с убывающими по модулю членами ошибка от
    обрыва не превосходит первого отброшенного члена. Поэтому «сколько
    членов» — это наименьшее n, при котором |term(n+1)| укладывается
    в границу, и проверка спрашивает ровно это: границу обязано выполнять
    n, и обязано нарушать n − 1. Эталона нет, term и bound стоят в условии.

    Ошибка здесь всегда одна и та же — на единицу: границу примеряют
    к n-му члену вместо (n+1)-го. Проверка её называет, не называя ответа.
    """
    if _blank(label, got):
        return False
    claim = sp.sympify(got)
    if not claim.is_Integer or claim < 1:
        print(f"{NO} {label}: " + _t(
            "число членов — целое положительное",
            "a number of terms is a positive whole number"))
        return False
    term = sp.sympify(term)
    spare = term.free_symbols - {sp.sympify(var)}
    if spare:
        print(f"{NO} {label}: " + _t(
            f"в формуле члена остались буквы, кроме номера: "
            f"{', '.join(sorted(map(str, spare)))} — укажите var",
            f"the term formula still has letters other than the index in "
            f"it: {', '.join(sorted(map(str, spare)))} — pass var"))
        return False
    limit = abs(complex(sp.sympify(bound).evalf(_PREC)))
    count = int(claim)

    def fits(n):
        """Укладывается ли в границу ошибка от n членов, то есть член n+1."""
        size = abs(complex(term.subs(var, n + 1).evalf(_PREC)))
        return size < limit if strict else size <= limit

    if not fits(count):
        print(f"{NO} {label}: " + _t(
            f"{count} членов не хватает: первый отброшенный член ещё больше "
            f"границы — это и есть оценка ошибки",
            f"{count} terms are not enough: the first term left out is still "
            f"bigger than the bound, and that term is the error estimate"))
        return False
    if count > 1 and fits(count - 1):
        print(f"{NO} {label}: " + _t(
            f"{count} членов больше, чем нужно: граница выполняется и на "
            f"меньшем числе. Проверьте, к какому члену её примеряете — "
            f"ошибка от n членов оценивается членом номер n + 1",
            f"{count} terms is more than needed: the bound already holds "
            f"with fewer. Check which term you are testing — the error from "
            f"n terms is bounded by term number n + 1"))
        return False
    print(f"{OK} {label}: {count}")
    return True


# --- производная: ответ проверяется дифференцированием, а не сверкой -------
#
# Двенадцатое понятие равенства ответов в серии, и самое простое из всех:
# производная у функции ровно одна, и получить её умеет сам sympy. Эталона
# поэтому не хранится нигде — проверка берёт f из условия и дифференцирует.
#
# Интереснее другое. Когда ответ неверен, «не сходится» — почти бесполезное
# сообщение: в этой теме промахов немного и все они именные. Забыт множитель
# внутренней функции. Произведение продифференцировано как u′v′. В частном
# перепутан знак числителя. Степень не понижена. Проверка строит каждый из
# этих промахов из самой f — по тому же правилу, применённому не так, как
# оно устроено, — и, если написанное совпало с одним из них, называет его.
# Списка неверных ответов при этом тоже нет: они выводятся, а не хранятся.

_DERIV_SAMPLES = (0.37, -0.53, 0.91, -1.27, 1.63, 2.41)


def _same_function(claim, want, var, run=None, tol=1e-8):
    """Совпадают ли два выражения как функции: сначала символьно, потом в точках."""
    try:
        diff_expr = sp.sympify(claim) - sp.sympify(want)
    except (TypeError, ValueError, sp.SympifyError):
        return False
    if run:
        diff_expr = diff_expr.subs(run)
    try:
        if sp.simplify(diff_expr) == 0:
            return True
    except (TypeError, ValueError, AttributeError, NotImplementedError):
        pass
    free = sorted(diff_expr.free_symbols - {var}, key=str)
    checked = 0
    for i, point in enumerate(_DERIV_SAMPLES):
        sub = {var: sp.Float(point)}
        sub.update({f: sp.Float(_SERIES_FILL[(i + j) % len(_SERIES_FILL)])
                    for j, f in enumerate(free)})
        try:
            here = complex(sp.sympify(want).subs(sub).evalf(_PREC))
            there = complex(sp.sympify(claim).subs(sub).evalf(_PREC))
            gap = complex(diff_expr.subs(sub).evalf(_PREC))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        scale = abs(here)
        if not (math.isfinite(gap.real) and math.isfinite(gap.imag)
                and math.isfinite(scale)):
            continue
        # Точки вне области функции пропускаются: у sqrt(1 + x) при x < −1
        # обе записи комплексны и ветвь корня у них разная, хотя на своей
        # области это одна и та же функция. Вопрос ставится на области,
        # и проверять надо там же.
        if abs(here.imag) > 1e-9 or abs(there.imag) > 1e-9:
            continue
        checked += 1
        if abs(gap) > tol * max(1.0, scale):
            return False
    return checked >= 2


def _no_chain(g, var):
    """Внешняя производная без множителя-внутренней: sin(2x) -> cos(2x)."""
    if g.is_Function and len(g.args) == 1:
        inside = g.args[0]
        if inside != var and inside.has(var):
            z = sp.Dummy('z')
            return sp.diff(g.func(z), z).subs(z, inside)
    if g.is_Pow:
        base, power = g.args
        if base != var and base.has(var) and not power.has(var):
            return power * base ** (power - 1)
    return None


def _slips(f, var, order):
    """Типовые промахи, собранные из самой f, а не из списка.

    Каждый промах — это правило, применённое не так, как оно устроено.
    Вернётся список (что случилось, выражение); сравнение с написанным
    делает вызывающий.
    """
    out = []
    f = sp.sympify(f)
    if order == 1:
        out.append((_t('функция не продифференцирована',
                       'nothing has been differentiated'), f))
    else:
        out.append((_t(f'это производная порядка {order - 1}, а не {order}',
                       f'this is the derivative of order {order - 1}, '
                       f'not {order}'), sp.diff(f, var, order - 1)))
        out.append((_t(f'это производная порядка {order + 1}',
                       f'this is the derivative of order {order + 1}'),
                    sp.diff(f, var, order + 1)))
    # Промахи последнего шага дифференцирования: до него всё могло быть верно.
    g = sp.diff(f, var, order - 1) if order > 1 else f
    outer = _no_chain(g, var)
    if outer is not None:
        out.append((_t('потерян множитель — производная внутренней функции',
                       'the chain factor is missing: the inside function has '
                       'to be differentiated too'), outer))
    num, den = sp.fraction(sp.together(g))
    if den.has(var):
        dn, dd = sp.diff(num, var), sp.diff(den, var)
        out.append((_t('в частном перепутан знак числителя',
                       'the sign in the quotient rule numerator is the wrong '
                       'way round'), (num * dd - dn * den) / den ** 2))
        out.append((_t('знаменатель не возведён в квадрат',
                       'the denominator has not been squared'),
                    (dn * den - num * dd) / den))
        out.append((_t('частное продифференцировано почленно',
                       'the quotient has been differentiated top over bottom'),
                    dn / dd))
    else:
        parts = [p for p in sp.Mul.make_args(g) if p.has(var)]
        if len(parts) == 2:
            u, v = parts
            const = g / (u * v)
            out.append((_t('произведение продифференцировано как u′v′',
                           'the product has been differentiated as u′v′'),
                        const * sp.diff(u, var) * sp.diff(v, var)))
            out.append((_t('в произведении потеряно одно из двух слагаемых',
                           'one of the two terms of the product rule is '
                           'missing'), const * sp.diff(u, var) * v))
            out.append((_t('в произведении потеряно одно из двух слагаемых',
                           'one of the two terms of the product rule is '
                           'missing'), const * u * sp.diff(v, var)))
    if g.is_Pow and g.args[0] == var and not g.args[1].has(var):
        out.append((_t('показатель не понижен на единицу',
                       'the power has not been dropped by one'),
                    g.args[1] * var ** g.args[1]))
    return out


def verify_derivative(label, got, f, var=x, order=1, params=None):
    """Ответ — производная: проверка дифференцирует f сама.

    Двенадцатое понятие равенства ответов в серии. Эталона здесь нет,
    потому что он не нужен: производная у функции одна, и вычисляется
    она из условия. Засчитывается любая эквивалентная запись — свёрнутая,
    развёрнутая, с вынесенным множителем: сравниваются функции, а не строки.

    order=2 — вторая производная, order=3 — третья.
    params={n: (2, 3, 7)} — когда в функции стоит буква и ответ зависит
    от неё: прогон идёт при каждом значении.

    Когда ответ неверен, проверка не ограничивается словом «неверно».
    Она строит из самой f горстку типовых промахов — цепное правило без
    внутреннего множителя, произведение как u′v′, частное с перевёрнутым
    знаком, непонижённый показатель — и, если написанное совпало с одним
    из них, называет его. Ни верного ответа, ни неверных проверка при
    этом не хранит: и те, и другие выводятся из условия.
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
    want = sp.diff(f, var, order)
    for run in runs:
        where = ('' if not run else ' ' + _t('при ', 'at ')
                 + ', '.join(f'{name} = {value}' for name, value in run.items()))
        if _same_function(claim, want, var, run):
            continue
        for why, slip in _slips(f, var, order):
            if _same_function(claim, slip, var, run):
                print(f"{NO} {label}: {why}" + where)
                return False
        print(f"{NO} {label}: " + _t(
            "не совпадает с производной функции из условия",
            "this is not the derivative of the function in the question")
            + where)
        return False
    print(f"{OK} {label}: {claim}")
    return True


def verify_stationary(label, got, f, var=x, domain=None, order=1, tol=5e-3):
    """Ответ — точки, где производная равна нулю: обе координаты и все точки.

    Эталона нет: у каждой пары (a, b) проверяется, что f′(a) = 0 и что
    b = f(a), а полнота набора — независимым сканированием производной
    по отрезку из условия. Это ловит обе потери баллов приёма: найдена
    точка, но не найдена вторая координата, и найдены не все точки.

    domain = (a, b) — отрезок из условия; без него берётся то, что даёт
    сканирование на [−10, 10]. order=2 — точки перегиба: там обращается
    в ноль вторая производная, а координата по-прежнему берётся у самой f.
    """
    if _blank(label, got):
        return False
    f = sp.sympify(f)
    lo, hi = ((-10, 10) if domain is None
              else (float(sp.sympify(domain[0])), float(sp.sympify(domain[1]))))
    prime = sp.diff(f, var, order)
    try:
        fp = sp.lambdify(var, prime, 'math')
        fv = sp.lambdify(var, f, 'math')
    except (TypeError, ValueError, NameError):
        print(f"{NO} {label}: " + _t("функцию из условия не удаётся вычислить",
                                     "the question's function cannot be evaluated"))
        return False
    given = []
    for item in got:
        try:
            a, b = item
        except (TypeError, ValueError):
            print(f"{NO} {label}: " + _t(
                "каждая точка записывается парой координат, например (0, E)",
                "each point is written as a pair of coordinates, e.g. (0, E)"))
            return False
        given.append((sp.sympify(a), sp.sympify(b)))
    for a, b in given:
        av = float(a.evalf(_PREC))
        if not lo - tol <= av <= hi + tol:
            print(f"{NO} {label}: {a} — " + _t("вне области из условия",
                                               "outside the interval given"))
            return False
        if abs(fp(av)) > 1e-6 * max(1.0, abs(av)):
            print(f"{NO} {label}: " + _t(
                f"при {var} = {a} производная не равна нулю",
                f"the derivative is not zero at {var} = {a}")
                + ('' if order == 1 else _t(f" (порядка {order})",
                                            f" (of order {order})")))
            return False
        if abs(float(b.evalf(_PREC)) - fv(av)) > tol:
            print(f"{NO} {label}: " + _t(
                f"первая координата верна, вторая нет: при {var} = {a} "
                f"функция принимает другое значение",
                f"the first coordinate is right and the second is not: the "
                f"function takes a different value at {var} = {a}"))
            return False
    found = _scan_roots(fp, lo, hi)
    # Сканирование ищет смены знака и потому не видит концов отрезка,
    # а у cos²x − 3sin²x на [0, π] две из трёх точек нулевого наклона
    # стоят ровно на концах. Без этого «найдено не всё» молчало бы
    # именно там, где вопрос ставится закрытым отрезком.
    for edge in (lo, hi):
        try:
            flat = abs(fp(edge)) < 1e-9 * max(1.0, abs(edge))
        except (ValueError, ZeroDivisionError, OverflowError):
            flat = False
        if flat and all(abs(edge - c) > 1e-3 for c in found):
            found.append(edge)
    found.sort()
    if len(found) > len(given):
        miss = [c for c in found
                if all(abs(c - float(a.evalf(_PREC))) > 1e-3 for a, _ in given)]
        hint = _t(f", первая пропущенная около {miss[0]:.4f}",
                  f", the first one missing is near {miss[0]:.4f}") if miss else ""
        print(f"{NO} {label}: " + _t(
            f"точки верны, но найдено не всё — на отрезке их {len(found)}, "
            f"а у вас {len(given)}{hint}",
            f"the points you list are right, but not all of them are there — "
            f"the interval holds {len(found)}, you list {len(given)}{hint}"))
        return False
    print(f"{OK} {label}: "
          + ', '.join(f"({a}, {b})" for a, b in given))
    return True


def verify_constants(label, got, unknowns, conditions, tol=1e-9, domain=None):
    """Ответ — постоянные, найденные из условий на кривую.

    Подставлять здесь не во что: буквы стоят внутри самой функции, и
    единственное, что делает их верными, — это условия из вопроса
    (асимптота там-то, кривая проходит через такую-то точку, производная
    в ней равна нулю). Проверка подставляет написанные числа в каждое
    из этих условий и называет то, которое не выполнилось.

    conditions — список пар (что это за условие, выражение или Eq),
    каждое из которых обязано обратиться в ноль.

    tol — с какой точностью. По умолчанию условие обязано выполниться
    точно: буквы в кривой ищут точными. Но там, где вопрос сам просит
    три значащие цифры («find an estimate for p»), точного нуля не будет
    никогда, и требовать его значило бы отвергать верный ответ за то,
    что его округлили так, как просили.

    domain — где буква вообще имеет право лежать. Обычно нигде, и поле
    пустует. Но когда буква стоит внутри вероятности, условиям вопроса
    удовлетворяют оба корня квадратного уравнения, а ответом является
    один: у мая 2024 TZ2 и k = 1/3, и k = 8/3 обращают (1−k)(1−k/2)
    в 5/9, и второй отброшен ровно за то, что вероятностью не бывает.
    Схема оценивания даёт за эту фразу отдельный балл, и проверка,
    которая её не знает, засчитала бы неверный ответ.
    """
    if _blank(label, got):
        return False
    values = [sp.sympify(v) for v in got]
    names = [sp.sympify(u) for u in unknowns]
    if len(values) != len(names):
        print(f"{NO} {label}: " + _t(
            f"постоянных {len(names)}, а значений {len(values)}",
            f"there are {len(names)} constants and {len(values)} values"))
        return False
    run = dict(zip(names, values))
    if domain is not None:
        outside = [(n, v) for n, v in run.items()
                   if domain.contains(v) is not sp.true]
        if outside:
            n, v = outside[0]
            print(f"{NO} {label}: " + _t(
                f"{n} = {v} лежит вне {domain} — таким это число быть не может",
                f"{n} = {v} lies outside {domain}, and it cannot"))
            return False
    for what, condition in conditions:
        residual = (condition.lhs - condition.rhs
                    if isinstance(condition, sp.Equality) else sp.sympify(condition))
        try:
            left = sp.simplify(residual.subs(run))
            ok = (left == 0) or abs(complex(left.evalf(_PREC))) < tol
        except (TypeError, ValueError, ZeroDivisionError):
            ok = False
        if not ok:
            print(f"{NO} {label}: " + _t(f"не выполнено условие «{what}»",
                                         f"the condition «{what}» fails"))
            return False
    print(f"{OK} {label}: "
          + ', '.join(f"{n} = {v}" for n, v in zip(names, values)))
    return True
