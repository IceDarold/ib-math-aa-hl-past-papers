"""Проверочный набор для практикумов по IB Mathematics AA HL.

Принцип: ответ проверяется по существу задачи, а не сравнением с записанным
эталоном. Решение дифференциального уравнения подставляется в само уравнение,
неявный ответ принимается в любой эквивалентной форме, числовой ответ
сверяется по хешу с округлением до требуемого числа значащих цифр.

Так в ячейке проверки не видно ответа, а эквивалентные формы записи
засчитываются — ровно как в markscheme.
"""

import hashlib
import itertools
import math

import sympy as sp

# Имена, которыми записывают ответ. Задача практикума — математика, а не синтаксис
# sympy, поэтому в ячейке пишут sin(x), pi/6, sqrt(5), а не sp.sin(x), sp.pi/6.
#
# Список явный, а не `from sympy import *`: тот тянет под тысячу имён и молча
# перекрывает встроенные (в том числе N и S), а отладка такого в чужом ноутбуке
# занимает больше времени, чем стоит вся экономия на буквах.
from sympy import (                                                  # noqa: E402
    sin, cos, tan, cot, sec, csc,
    asin, acos, atan, acot,
    sinh, cosh, tanh, asinh, acosh, atanh,
    sqrt, cbrt, root, exp, log, Abs, sign, floor, ceiling,
    Piecewise, Min, Max,
    pi, E, I, oo, zoo, nan,
    Rational, Integer, Float, S, Symbol, symbols, sympify,
    re, im, arg, conjugate, Add, Mul, Pow,
    simplify, trigsimp, expand, expand_trig, factor, cancel, together, apart,
    div, quo, rem, Poly, degree, discriminant, real_roots, fraction,
    solve, solveset, nsolve, Eq, Ne,
    Interval, Union, Intersection, Complement, FiniteSet, And, Or, Not,
    maximum, minimum,
    diff, integrate, limit, series, dsolve, Derivative, Integral, Function,
    factorial, binomial, Sum, Product, Matrix, lambdify, nsimplify,
)

# Осторожно: `re` здесь — функция sympy «действительная часть», и она перекрывает
# стандартный модуль регулярных выражений. В ноутбуке практикума это то, что нужно
# (Re(z) пишут постоянно, регулярные выражения — никогда), но в скрипте,
# которому нужен модуль re, импортируйте его после `from kit import *`.

# IB пишет arcsin и cosec там, где sympy пишет asin и csc. Принимаем обе записи:
# ответ не должен зависеть от того, в какой нотации вы привыкли писать.
arcsin, arccos, arctan, arccot = asin, acos, atan, acot
cosec = csc
ln = log

# Символы по умолчанию. Определяются после импорта sympy, чтобы при совпадении
# имён побеждали они: N здесь переменная задачи, а не функция округления.
x, y, v, t, u, C, A, B, k, N = sp.symbols('x y v t u C A B k N')

OK, NO = "✅", "❌"

# Язык сообщений проверок. Ноутбуки IB пишутся и по-русски, и по-английски;
# практикум на английском не должен печатать «не сходится» посреди работы,
# которую сдают на английском. Значение по умолчанию русское, поэтому
# ничего из уже написанного не меняется: язык переключает сам ноутбук.
_LANG = 'ru'


def language(code=None):
    """Язык сообщений: 'ru' (по умолчанию) или 'en'. Без аргумента — текущий."""
    global _LANG
    if code is None:
        return _LANG
    if code not in ('ru', 'en'):
        raise ValueError("language: 'ru' or 'en'")
    _LANG = code
    return _LANG


def _t(ru, en):
    """Один и тот же кусок сообщения на двух языках."""
    return en if _LANG == 'en' else ru



def digest(value):
    """Короткий хеш ответа. Используется при составлении заданий."""
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


def _blank(label, *values):
    """Задание ещё не решено: в ячейке остался placeholder `...`.

    Ноутбук должен проходиться сверху вниз и с пустыми заданиями — иначе
    его нельзя ни запустить целиком, ни залить туда, где ячейки исполняются
    автоматически.

    Внутрь списков и словарей смотрим рекурсивно: там, где ответ это набор,
    в ячейке стоит `[...]`, а там, где ответ это описание эскиза, — словарь
    с многоточиями внутри; снаружи ни то, ни другое от заполненного
    не отличается.
    """
    def has_gap(v):
        if v is Ellipsis:
            return True
        if isinstance(v, dict):
            return any(has_gap(i) for i in v.values())
        if isinstance(v, (list, tuple, set, frozenset)):
            return any(has_gap(i) for i in v)
        return False

    if any(has_gap(v) for v in values):
        print(f"⬜ {label}: " + _t("ответ не заполнен", "no answer yet"))
        return True
    return False


def sig(value, sf):
    """Строковая запись числа с sf значащими цифрами."""
    return f"{float(value):.{sf}g}"


def verify_ode(label, y_expr, rhs, ic=None, var=x, dep=y):
    """Проверяет, что y = y_expr решает dy/dvar = rhs и проходит через ic = (x0, y0).

    Эталонный ответ не хранится: невязка считается подстановкой в уравнение,
    поэтому любая верная форма записи проходит проверку.
    """
    if _blank(label, y_expr, rhs, *(ic or ())):
        return False
    y_expr, rhs = sp.sympify(y_expr), sp.sympify(rhs)
    resid = sp.simplify(sp.diff(y_expr, var) - rhs.subs(dep, y_expr))
    if resid != 0:
        print(f"{NO} {label}: " + _t(f"не удовлетворяет уравнению, невязка = {resid}",
                              f"does not satisfy the equation, residual = {resid}"))
        return False
    if ic is not None:
        x0, y0 = ic
        got = sp.simplify(y_expr.subs(var, sp.sympify(x0)))
        if sp.simplify(got - sp.sympify(y0)) != 0:
            print(f"{NO} {label}: " + _t(
                f"уравнение решено, но y({x0}) = {got}, а нужно {y0}",
                f"the equation is solved, but y({x0}) = {got} instead of {y0}"))
            return False
    print(f"{OK} {label}")
    return True


def verify_implicit(label, got, want, var=x, dep=y):
    """Неявный ответ F(x, y) = c. Принимается любая форма, отличающаяся множителем."""
    if _blank(label, got, want):
        return False

    def flat(e):
        e = sp.sympify(e)
        return sp.sympify(e.lhs - e.rhs) if isinstance(e, sp.Eq) else e

    g, w = flat(got), flat(want)
    ratio = sp.simplify(sp.cancel(g / w))
    if ratio == 0 or ratio.free_symbols & {var, dep}:
        print(f"{NO} {label}: " + _t(
            "не сводится к верному ответу домножением на константу",
            "is not the correct answer up to a constant factor"))
        return False
    tail = "" if ratio == 1 else _t(f" (эквивалентная форма, множитель {ratio})",
                                    f" (equivalent form, factor {ratio})")
    print(f"{OK} {label}{tail}")
    return True


def check_num(label, value, sf, want_digest):
    """Числовой ответ с округлением до sf значащих цифр."""
    if _blank(label, value):
        return False
    got = sig(value, sf)
    if digest(got) == want_digest:
        print(f"{OK} {label}: {got}")
        return True
    print(f"{NO} {label}: {got} — " + _t(
        f"не сходится (проверь округление до {sf} знач. цифр)",
        f"no match (check the rounding to {sf} s.f.)"))
    return False


def check_expr(label, got, want_digest):
    """Символьный ответ, сверяемый по хешу канонической записи."""
    if _blank(label, got):
        return False
    got = sp.sympify(got)
    if digest(sp.srepr(sp.simplify(got))) == want_digest:
        print(f"{OK} {label}: {got}")
        return True
    print(f"{NO} {label}: {got} — " + _t("не сходится", "no match"))
    return False


def _complex_canon(value, sf=6, tol=1e-9):
    """Каноническая запись комплексного числа: пара округлённых частей.

    Сравнивать комплексные ответы через srepr нельзя. sympy не приводит
    2·e^{2πi/3}, 2(cos 2π/3 + i sin 2π/3) и −1 + √3 i к общему виду:
    первое упрощается до 2·(−1)^{2/3}, второе до −1 + √3 i, и хеши расходятся.
    Верный ответ в полярной форме получил бы ❌ против декартова эталона.
    Поэтому сверяется само число, а не его запись.
    """
    z = complex(sp.N(sp.sympify(value)))
    re_ = 0.0 if abs(z.real) < tol else z.real
    im_ = 0.0 if abs(z.imag) < tol else z.imag
    return f"{sig(re_, sf)}|{sig(im_, sf)}"


def check_complex(label, got, want_digest, sf=6):
    """Комплексный ответ в любой форме записи.

    sf задаёт требуемую точность: 6 значащих цифр означает «нужна точная
    форма» (десятичное приближение не пройдёт), 3 — «достаточно трёх
    значащих цифр», как в Paper 2.
    """
    if _blank(label, got):
        return False
    if digest(_complex_canon(got, sf)) == want_digest:
        print(f"{OK} {label}: {got}")
        return True
    print(f"{NO} {label}: {got} — " + _t("не сходится", "no match"))
    return False


def check_complex_set(label, values, want_digest, sf=6):
    """Набор комплексных чисел: корни n-й степени, вершины многоугольника.

    Порядок не важен, форма записи каждого элемента тоже.
    """
    if _blank(label, values, *values):
        return False
    canon = '|'.join(sorted(_complex_canon(v, sf) for v in values))
    if digest(canon) == want_digest:
        print(f"{OK} {label}: {{{', '.join(str(v) for v in values)}}}")
        return True
    print(f"{NO} {label}: {{{', '.join(str(v) for v in values)}}} — " + _t("не сходится", "no match"))
    return False


# Точки, в которых сверяются разложения, и заполнение для прочих букв.
# Значения входят в хеш: меняя их, вы обесцениваете все записанные эталоны.
_SERIES_SAMPLES = (0.31, 0.72, 1.37, 2.13, 3.41)
_SERIES_FILL = (0.7, 1.3, 2.1, 0.4, 1.9)


def _series_canon(expr, var, sf=6, tol=1e-12):
    """Канонический вид разложения: значения в нескольких точках.

    Сравнивать записи бессмысленно. Ученик напишет 5*x/2, sympy — 2.5*x,
    а srepr у Rational(5,2) и Float(2.5) разный; сворачивать (1+x)**4 обратно
    в многочлен simplify тоже не станет. Значения же совпадают при любой
    верной записи, а разные многочлены в пяти точках не совпадают никогда.
    """
    e = sp.sympify(expr)
    free = sorted(e.free_symbols - {var}, key=str)
    out = []
    for i, s in enumerate(_SERIES_SAMPLES):
        sub = {var: sp.Float(s)}
        sub.update({f: sp.Float(_SERIES_FILL[(i + j) % len(_SERIES_FILL)])
                    for j, f in enumerate(free)})
        z = complex(sp.N(e.subs(sub)))
        re_ = 0.0 if abs(z.real) < tol else z.real
        im_ = 0.0 if abs(z.imag) < tol else z.imag
        out.append(f"{sig(re_, sf)}|{sig(im_, sf)}")
    return ';'.join(out)


def check_series(label, got, want_digest, var=x, sf=6):
    """Ответ — многочлен или отрезок ряда от var.

    Засчитывается любая эквивалентная запись: 5*x/2 и 2.5*x, порядок слагаемых,
    вынесенный за скобку множитель. Если в ответе есть другие буквы (p, q, a),
    называть их надо так же, как в условии: по ним проверка тоже подставляет
    значения.

    Чего проверка не делает: не требует раскрытых скобок. Ответ (1+x)**4
    численно равен своему разложению, и отличить их по значениям нельзя.
    """
    if _blank(label, got):
        return False
    canon = _series_canon(got, var, sf)
    if digest(canon) == want_digest:
        print(f"{OK} {label}: {sp.expand(sp.sympify(got))}")
        return True
    print(f"{NO} {label}: {sp.expand(sp.sympify(got))} — " + _t("не сходится", "no match"))
    return False


def check_set(label, values, want_digest):
    """Ответ — набор значений (корни, углы). Порядок не важен."""
    if _blank(label, values):
        return False
    items = [sp.sympify(v) for v in values]
    canon = '|'.join(sorted(sp.srepr(sp.simplify(i)) for i in items))
    if digest(canon) == want_digest:
        print(f"{OK} {label}: {{{', '.join(str(i) for i in items)}}}")
        return True
    print(f"{NO} {label}: {{{', '.join(str(i) for i in items)}}} — " + _t("не сходится", "no match"))
    return False


def verify_identity(label, got, want, var=x,
                    samples=(0.3, 0.7, 1.1, 1.9, 2.6, 3.4, 4.1, 5.2), tol=1e-9):
    """Тождество got ≡ want. Проверяет переход, а не ответ.

    В вопросах «show that» ответ напечатан в условии, прятать его бессмысленно:
    смысл задания в выкладке. Поэтому проверяется, что записанное вами
    промежуточное выражение действительно равно исходному при всех значениях.

    Символьное упрощение тригонометрии часто не доводит разность до нуля,
    хотя она тождественно нулевая, поэтому за simplify идёт численная проверка
    в нескольких точках. Особые точки (полюсы tan, ноль в знаменателе)
    пропускаются: расхождением они не считаются.
    """
    if _blank(label, got):
        return False
    diff = sp.simplify(sp.expand_trig(sp.sympify(got) - sp.sympify(want)))
    if diff == 0:
        print(f"{OK} {label}: " + _t("тождество выполняется", "identity holds"))
        return True

    checked = 0
    for s in samples:
        try:
            val = complex(diff.subs(var, sp.Float(s)).evalf())
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(val.real) and math.isfinite(val.imag)):
            continue
        checked += 1
        if abs(val) > tol:
            print(f"{NO} {label}: " + _t(
                f"при {var} = {s:g} стороны расходятся на {abs(val):.3g}",
                f"at {var} = {s:g} the two sides differ by {abs(val):.3g}"))
            return False
    if checked < 3:
        print(f"{NO} {label}: " + _t("проверить не удалось — слишком много особых точек",
                               "cannot be checked — too many singular points"))
        return False
    print(f"{OK} {label}: " + _t(
        f"тождество выполняется (проверено в {checked} точках)",
        f"identity holds (checked at {checked} points)"))
    return True


def _agrees(got, want, var, samples, tol=1e-9):
    """Совпадают ли два выражения при целых var из samples.

    Возвращает (ок, пояснение). Сначала символьно: expand, потом simplify —
    именно в этом порядке, потому что m·m^k само по себе до m^(k+1)
    не сворачивается, а после expand разность уходит в ноль.

    Численная проверка нужна для факториалов и биномов, где simplify
    до нуля доходит не всегда. Свободные символы, кроме var (в задачах
    про n-ю производную это x), заполняются числами.
    """
    d = sp.sympify(got) - sp.sympify(want)
    try:
        if sp.simplify(sp.expand(d)) == 0:
            return True, None
    except (TypeError, ValueError, AttributeError):
        pass

    free = sorted(d.free_symbols - {var}, key=str)
    fill = (0.7, 1.3, 2.1, 0.4, 1.9)
    checked = 0
    for i, s in enumerate(samples):
        sub = {var: sp.Integer(s)}
        sub.update({f: sp.Float(fill[(i + j) % len(fill)]) for j, f in enumerate(free)})
        try:
            val = complex(d.subs(sub).evalf())
            scale = abs(complex(sp.sympify(want).subs(sub).evalf()))
        except (TypeError, ValueError):
            continue
        if not (math.isfinite(val.real) and math.isfinite(val.imag)
                and math.isfinite(scale)):
            continue
        checked += 1
        if abs(val) > tol * max(1.0, scale):
            return False, _t(f"при {var} = {s} расхождение {abs(val):.3g}",
                             f"at {var} = {s} the gap is {abs(val):.3g}")
    if checked < 3:
        return False, _t("проверить не удалось: слишком много особых точек",
                         "cannot be checked: too many singular points")
    return True, _t(f"проверено в {checked} точках",
                    f"checked at {checked} points")


def verify_induction(label, got, formula, var=k, n0=1, base_lhs=None,
                     samples=(1, 2, 3, 4, 5, 6, 7)):
    """База и переход индукции разом.

    formula  — доказываемая правая часть как выражение от var.
    got      — то, что получилось в шаге после подстановки гипотезы;
               должно совпасть с formula при var → var + 1.
    base_lhs — левая часть при var = n0. Без неё база не проверяется,
               а в markscheme это отдельный балл R1, и терять его жаль.

    Прятать ответ здесь не от кого: в задачах «prove that» он напечатан
    в условии. Проверяется ровно то, за что дают баллы, — что ваш переход
    действительно приводит к утверждению для k + 1.
    """
    if _blank(label, got):
        return False
    formula = sp.sympify(formula)
    ok = True

    if base_lhs is not None:
        if base_lhs is Ellipsis:
            print(f"⬜ {label}, " + _t("база: не заполнена", "base case: not filled in"))
            ok = False
        else:
            diff = sp.simplify(sp.expand(sp.sympify(base_lhs) - formula.subs(var, n0)))
            if diff == 0:
                print(f"{OK} {label}, " + _t(
                    f"база: при {var} = {n0} стороны равны",
                    f"base case: at {var} = {n0} the two sides are equal"))
            else:
                print(f"{NO} {label}, " + _t(
                    f"база: при {var} = {n0} стороны расходятся на {diff}",
                    f"base case: at {var} = {n0} the two sides differ by {diff}"))
                ok = False

    good, note = _agrees(got, formula.subs(var, var + 1), var, samples)
    tail = f" ({note})" if note else ""
    if good:
        print(f"{OK} {label}, " + _t(
            f"переход: получено утверждение для {var} + 1{tail}",
            f"step: this is the statement for {var} + 1{tail}"))
    else:
        print(f"{NO} {label}, " + _t(
            f"переход: это не утверждение для {var} + 1 — {note}",
            f"step: this is not the statement for {var} + 1 — {note}"))
    return ok and good


def verify_divisibility(label, expr, d, mult, var=k, n0=1, samples=(1, 2, 3, 4, 5)):
    """Индукция для делимости: expr(n) кратно d при всех n ≥ n0.

    mult — множитель, с которым гипотеза входит в шаг. Проверяется, что
    expr(k+1) − mult·expr(k) делится на d **как выражение**, то есть после
    деления на d остаются целые коэффициенты.

    Требование про коэффициенты не придирка. Разность бывает кратна d при
    каждом целом k и без этого — но тогда её нельзя записать в виде d·(целое)
    одной строкой, и доказательства не получается. Markscheme даёт A1 именно
    за вынесение d за скобку.
    """
    if _blank(label, expr, mult):
        return False
    expr, d = sp.sympify(expr), sp.sympify(d)
    ok = True

    base = sp.simplify(expr.subs(var, n0))
    if sp.simplify(base / d).is_integer:
        print(f"{OK} {label}, " + _t(
            f"база: при {var} = {n0} получается {base} = {d}·{base / d}",
            f"base case: at {var} = {n0} this gives {base} = {d}·{base / d}"))
    else:
        print(f"{NO} {label}, " + _t(
            f"база: при {var} = {n0} получается {base}, а оно не кратно {d}",
            f"base case: at {var} = {n0} this gives {base}, not a multiple of {d}"))
        ok = False

    rest = sp.expand(expr.subs(var, var + 1) - sp.sympify(mult) * expr)
    quot = sp.expand(rest / d)
    bad = [c for c in quot.as_coefficients_dict().values() if not sp.sympify(c).is_Integer]
    if bad:
        print(f"{NO} {label}, " + _t(
            f"шаг: остаток {rest} на {d} нацело не делится "
            f"(после деления остаются дроби {bad})",
            f"step: the remainder {rest} is not divisible by {d} "
            f"(the division leaves the fractions {bad})"))
        return False
    for s in samples:
        if not sp.sympify(quot.subs(var, s)).is_integer:
            print(f"{NO} {label}, " + _t(
                f"шаг: при {var} = {s} частное {quot.subs(var, s)} не целое",
                f"step: at {var} = {s} the quotient {quot.subs(var, s)} "
                f"is not an integer"))
            return False
    print(f"{OK} {label}, " + _t(f"шаг: остаток равен {d}·({quot})",
                                  f"step: the remainder equals {d}·({quot})"))
    return ok


def verify_rewrite(label, left, right, original, var=x, factor=1):
    """Равенство left = right получено из original = 0 переносами и делением.

    В доказательстве от противного исходное уравнение приводят к виду, где
    у сторон разная чётность. Проверяется, что по дороге ничего не потерялось:
    factor·(left − right) обязано совпасть с original. factor нужен там, где
    равенство делили — деление на 2 возвращается умножением на 2.

    Отдельная функция, а не выражение прямо в ячейке: пока задание не решено,
    в left и right лежат многоточия, и вычитать их нельзя. Ноутбук обязан
    проходиться сверху вниз с пустыми ответами.
    """
    if _blank(label, left, right):
        return False
    return verify_identity(
        label, sp.sympify(factor) * (sp.sympify(left) - sp.sympify(right)),
        original, var=var)


def verify_residue(label, expr, mod, want, samples=(-3, -2, -1, 0, 1, 2, 3, 4, 5),
                   limit=400):
    """Остаток expr при делении на mod одинаков и равен want при всех целых символах.

    Этим проверяется почти вся некомбинаторная часть темы: «делится на 3»
    (остаток 0), «никогда не делится на 3» (остаток 2), «чётно» (mod 2, остаток 0).
    В markscheme за такой вывод стоит R1, и формулируется он теми же словами.

    Перебираются все свободные символы выражения, поэтому запись через
    два целых, как (2m+1)² + (2n+1)², проверяется без дополнительных усилий.
    """
    if _blank(label, expr, want):
        return False
    expr, mod = sp.sympify(expr), sp.sympify(mod)
    free = sorted(expr.free_symbols, key=str)
    grids = (itertools.islice(itertools.product(samples, repeat=len(free)), limit)
             if free else [()])
    checked = 0
    for combo in grids:
        val = sp.simplify(expr.subs(dict(zip(free, map(sp.Integer, combo)))))
        if not val.is_integer:
            print(f"{NO} {label}: " + _t(
                f"при {dict(zip(map(str, free), combo))} получается {val}, "
                f"а это не целое",
                f"at {dict(zip(map(str, free), combo))} this gives {val}, "
                f"which is not an integer"))
            return False
        got = int(val) % int(mod)
        if got != int(want) % int(mod):
            print(f"{NO} {label}: " + _t(
                f"при {dict(zip(map(str, free), combo))} остаток от деления "
                f"на {mod} равен {got}, а не {want}",
                f"at {dict(zip(map(str, free), combo))} the remainder mod "
                f"{mod} is {got}, not {want}"))
            return False
        checked += 1
    print(f"{OK} {label}: " + _t(
        f"остаток от деления на {mod} всегда {int(want) % int(mod)} "
        f"(проверено наборов: {checked})",
        f"the remainder mod {mod} is always {int(want) % int(mod)} "
        f"({checked} sets checked)"))
    return True


def check_order(label, seq, want_digest, n=None):
    """Ответ — порядок шагов доказательства. В отличие от check_set порядок важен."""
    if _blank(label, seq):
        return False
    items = [str(s).strip().lower() for s in seq]
    if n is not None and len(items) != n:
        print(f"{NO} {label}: " + _t(
            f"шагов должно быть {n}, а получено {len(items)}",
            f"there should be {n} steps, not {len(items)}"))
        return False
    if digest('|'.join(items)) == want_digest:
        print(f"{OK} {label}: {' → '.join(items)}")
        return True
    print(f"{NO} {label}: {' → '.join(items)} — " + _t("порядок не тот", "wrong order"))
    return False


# --- многочлены -------------------------------------------------------------
#
# Здесь проверки устроены не так, как в A3. Там ответ сверялся по значениям
# и нераскрытая скобка проходила, потому что «раскрыть» — просьба к записи,
# а не к числу. В теме многочленов ровно наоборот: «представьте в виде
# произведения линейных множителей» — это и есть задача, и ответ, равный
# исходному многочлену, но записанный одной строкой, неверен.
#
# Поэтому verify_factored и check_apart смотрят на то, что написано
# в ячейке, а не только на значение: сначала разбирают структуру записи,
# потом сверяют равенство.


def _poly_degree(expr, var):
    """Степень многочлена; None, если это не многочлен от var."""
    try:
        return sp.degree(sp.Poly(sp.expand(sp.sympify(expr)), var))
    except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError, ValueError):
        return None


def _nroots(expr, var):
    """Численные корни многочлена; None, если найти их не удалось.

    Точность приходится понижать: у кратного корня в нуле mpmath при n=20
    до сходимости не доходит и бросает NoConvergence. Ронять на этом ячейку
    нельзя — проверка обязана печатать вердикт, а не исключение.
    """
    for precision in (20, 15, 10):
        try:
            return sp.Poly(expr, var).nroots(n=precision)
        except (sp.PolynomialError, sp.GeneratorsNeeded, TypeError, ValueError):
            return None
        except Exception:                                            # noqa: BLE001
            continue                        # mpmath.NoConvergence и родня
    return None


def verify_factored(label, got, original, var=x, max_deg=1, n=None):
    """Разложение многочлена на множители: и равенство, и форма записи.

    Эталон не хранится: original — это тот же многочлен, что напечатан
    в условии, прятать его незачем. Проверяется два условия.

    Первое — структурное. Разбирается именно записанное произведение,
    без факторизации: sp.factor_list разложил бы и раскрытый многочлен,
    и проверка стала бы бессмысленной. Каждый множитель обязан иметь
    степень не выше max_deg (по умолчанию 1 — «product of linear factors»),
    кратные множители считаются столько раз, какова кратность.

    Второе — равенство: произведение должно раскрываться в original.
    """
    if _blank(label, got):
        return False
    e = sp.sympify(got)
    orig = sp.sympify(original)

    args = sp.Mul.make_args(e)
    if len(args) == 1 and not args[0].is_Pow:
        print(f"{NO} {label}: " + _t(
            "это не произведение — многочлен записан одной строкой",
            "this is not a product — the polynomial is written as one expression"))
        return False

    facs = []
    for arg in args:
        if var not in arg.free_symbols:
            continue                                   # числовой множитель
        base, exp = arg.as_base_exp()
        if not (exp.is_Integer and exp > 0):
            print(f"{NO} {label}: " + _t(f"множитель {arg} — не многочлен",
                                   f"the factor {arg} is not a polynomial"))
            return False
        d = _poly_degree(base, var)
        if d is None:
            print(f"{NO} {label}: " + _t(
                f"множитель {base} — не многочлен от {var}",
                f"the factor {base} is not a polynomial in {var}"))
            return False
        if d > max_deg:
            print(f"{NO} {label}: " + _t(
                f"множитель {base} имеет степень {d}, а нужны множители "
                f"степени не выше {max_deg} — разложение не доведено до конца",
                f"the factor {base} has degree {d}, but factors of degree "
                f"at most {max_deg} are wanted — the factorisation is "
                f"not finished"))
            return False
        facs.extend([base] * int(exp))

    if not facs:
        print(f"{NO} {label}: " + _t(f"множителей с {var} не нашлось",
                               f"no factor contains {var}"))
        return False
    if n is not None and len(facs) != n:
        print(f"{NO} {label}: " + _t(
            f"множителей должно быть {n} (кратные считаются по разу "
            f"за каждую степень), а получилось {len(facs)}",
            f"there should be {n} factors (a repeated factor counts once "
            f"per power), not {len(facs)}"))
        return False
    if sp.expand(e - orig) != 0:
        print(f"{NO} {label}: " + _t(
            f"произведение раскрывается в {sp.expand(e)}, а исходный "
            f"многочлен {sp.expand(orig)}",
            f"the product expands to {sp.expand(e)}, but the original "
            f"polynomial is {sp.expand(orig)}"))
        return False
    print(f"{OK} {label}: {e}")
    return True


def verify_division(label, quotient, remainder, dividend, divisor, var=x):
    """Деление с остатком: dividend = divisor·quotient + remainder.

    Эталона нет — восстанавливается делимое. Отдельно проверяется условие,
    без которого равенство ничего не значит: степень остатка должна быть
    строго меньше степени делителя, иначе делить можно дальше.
    """
    if _blank(label, quotient, remainder):
        return False
    quo, rem = sp.sympify(quotient), sp.sympify(remainder)
    num, den = sp.sympify(dividend), sp.sympify(divisor)

    resid = sp.expand(num - (den * quo + rem))
    if sp.simplify(resid) != 0:
        print(f"{NO} {label}: " + _t(
            f"делимое не восстанавливается, невязка = {resid}",
            f"the dividend is not recovered, residual = {resid}"))
        return False

    d_den = _poly_degree(den, var)
    d_rem = -1 if sp.simplify(rem) == 0 else _poly_degree(rem, var)
    if d_den is None or d_rem is None:
        print(f"{NO} {label}: " + _t(
            f"делитель и остаток должны быть многочленами от {var}",
            f"the divisor and the remainder must be polynomials in {var}"))
        return False
    if d_rem >= d_den:
        print(f"{NO} {label}: " + _t(
            f"остаток степени {d_rem} не ниже делителя (степень {d_den}) — "
            f"делить можно дальше",
            f"the remainder has degree {d_rem}, not below the divisor "
            f"(degree {d_den}) — the division can go further"))
        return False
    print(f"{OK} {label}: {sp.expand(num)} = ({den})·({quo}) + ({rem})")
    return True


def verify_divisible(label, poly, divisor, subs=None, var=x):
    """Многочлен делится на divisor нацело.

    Найденные значения букв подставляются в poly, и считается настоящий
    остаток. Эталон не хранится вовсе: проверяется то самое условие,
    которое стоит в задаче, а не совпадение с записанным ответом.
    """
    subs = dict(subs or {})
    if _blank(label, list(subs.values())):
        return False
    p = sp.expand(sp.sympify(poly).subs(subs))
    d = sp.sympify(divisor)
    quo, rem = sp.div(p, d, var)
    if sp.simplify(rem) != 0:
        print(f"{NO} {label}: " + _t(
            f"остаток от деления равен {sp.expand(rem)}, а должен быть нулём",
            f"the remainder is {sp.expand(rem)}, but it must be zero"))
        return False
    print(f"{OK} {label}: " + _t(
        f"{p} делится на {sp.expand(d)} нацело, частное {quo}",
        f"{p} is divisible by {sp.expand(d)}, quotient {quo}"))
    return True


def check_apart(label, got, original, var=x):
    """Разложение на простейшие дроби: и равенство, и форма записи.

    Как и с множителями, равенства мало: исходная дробь равна сама себе.
    Поэтому каждое слагаемое обязано быть простейшей дробью — числитель
    без var, знаменатель степень одного неприводимого множителя.
    Знаменатель (x+1)(2x+1) проверку не пройдёт: он не разложен.
    """
    if _blank(label, got):
        return False
    e = sp.sympify(got)
    orig = sp.sympify(original)

    for term in sp.Add.make_args(e):
        num, den = sp.fraction(sp.together(term))
        if var not in den.free_symbols:
            print(f"{NO} {label}: " + _t(
                f"слагаемое {term} — не дробь с {var} в знаменателе",
                f"the term {term} is not a fraction with {var} "
                f"in the denominator"))
            return False
        if var in num.free_symbols:
            print(f"{NO} {label}: " + _t(
                f"у слагаемого {term} числитель зависит от {var}; простейшая "
                f"дробь так не выглядит",
                f"the numerator of {term} depends on {var}; a partial "
                f"fraction does not look like that"))
            return False
        try:
            _, pieces = sp.factor_list(den, var)
        except (sp.PolynomialError, sp.GeneratorsNeeded):
            print(f"{NO} {label}: " + _t(
                f"знаменатель {den} — не многочлен от {var}",
                f"the denominator {den} is not a polynomial in {var}"))
            return False
        if len(pieces) != 1:
            print(f"{NO} {label}: " + _t(
                f"знаменатель {den} сам раскладывается на множители — дробь "
                f"не доведена до простейшей",
                f"the denominator {den} factorises further — the fraction "
                f"is not yet a partial one"))
            return False
        d = _poly_degree(pieces[0][0], var)
        if d is None or d > 1:
            print(f"{NO} {label}: " + _t(
                f"знаменатель {den} не является степенью линейного множителя",
                f"the denominator {den} is not a power of a linear factor"))
            return False

    if sp.simplify(sp.cancel(sp.together(e - orig))) != 0:
        print(f"{NO} {label}: " + _t(
            "сумма дробей не равна исходному выражению",
            "the sum of the fractions is not equal to the original expression"))
        return False
    print(f"{OK} {label}: {e}")
    return True


def verify_root_transform(label, coeffs, original, transform, var=x, tol=1e-6):
    """Корни нового многочлена — это transform от корней исходного.

    Ровно то, о чём спрашивает задача «составьте уравнение с корнями 1/α³»,
    и ровно то, что проверяется: эталонных коэффициентов нет, оба набора
    корней считаются численно и сравниваются как мультимножества.

    coeffs — коэффициенты нового многочлена по убыванию степени. Список,
    а не готовое выражение: иначе незаполненный ответ уронил бы ячейку
    ещё до входа в проверку.
    """
    if _blank(label, coeffs):
        return False
    cs = [sp.sympify(c) for c in coeffs]
    new = sum(c * var**(len(cs) - 1 - i) for i, c in enumerate(cs))
    if sp.expand(new) == 0:
        print(f"{NO} {label}: " + _t("многочлен получился нулевым",
                               "the polynomial came out as zero"))
        return False

    want = []
    roots_orig = _nroots(sp.expand(sp.sympify(original)), var)
    roots_new = _nroots(sp.expand(new), var)
    if roots_orig is None or roots_new is None:
        print(f"{NO} {label}: " + _t(
            "корни этого многочлена численно найти не удалось — "
            "проверка неприменима",
            "the roots of this polynomial could not be found numerically — "
            "the check does not apply"))
        return False
    for r in roots_orig:
        try:
            want.append(complex(sp.N(transform(r))))
        except (ZeroDivisionError, TypeError, ValueError):
            print(f"{NO} {label}: " + _t(
                f"преобразование не определено для корня {r}",
                f"the transformation is undefined at the root {r}"))
            return False
    got = [complex(v) for v in roots_new]

    if len(got) != len(want):
        print(f"{NO} {label}: " + _t(
            f"корней должно быть {len(want)}, а у многочлена {len(got)}",
            f"there should be {len(want)} roots, but the polynomial "
            f"has {len(got)}"))
        return False

    free = list(want)
    for g in got:
        near = min(range(len(free)), key=lambda i: abs(free[i] - g), default=None)
        if near is None or abs(free[near] - g) > tol * max(1.0, abs(g)):
            print(f"{NO} {label}: " + _t(
                f"корень {g:.6g} не совпадает ни с одним нужным",
                f"the root {g:.6g} matches none of the required ones"))
            return False
        free.pop(near)
    print(f"{OK} {label}: {sp.expand(new)} = 0 — " + _t(
        "корни те, что нужно", "the roots are the required ones"))
    return True


# --- неравенства ------------------------------------------------------------
#
# Третий раз тема требует своего понятия равенства ответов. В A3 сверялись
# значения, в A4 — форма записи. Здесь ответ — **множество**, и сверять надо
# множества: у неравенства нет «ответа» в виде числа, а есть граница, и
# ровно на границе стоят баллы. Строгое или нестрогое, выколота ли точка,
# где обращается в ноль знаменатель, — это и есть содержание темы.
#
# Проверок две, и различаются они не темой, а тем, откуда берётся истина.
# verify_solution_set решает неравенство сам и сравнивает множества точно.
# verify_param_set не решает ничего: он берёт ваше множество и проверяет
# в точках, что свойство выполняется ровно там, где вы обещали.


def _as_set(value, var):
    """Ответ в любой записи → множество sympy.

    Принимаются и Interval(-5, 1), и (x >= -5) & (x <= 1), и Union(...),
    и S.Reals. Запись ответа — дело вкуса, содержание одно.
    """
    v = sp.sympify(value)
    if isinstance(v, sp.Set):
        return v
    if isinstance(v, (sp.core.relational.Relational, sp.logic.boolalg.Boolean)):
        try:
            return v.as_set()
        except (NotImplementedError, ValueError, TypeError):
            return None
    return None


def _show_set(s, var):
    """Множество словами экзамена: −5 ≤ x ≤ 1 вместо Interval(-5, 1)."""
    try:
        return str(s.as_relational(var))
    except (NotImplementedError, AttributeError, TypeError):
        return str(s)


def _pieces(s):
    """Множество → список (начало, конец, открыт слева, открыт справа).

    Точка представляется вырожденным отрезком. None означает, что множество
    устроено сложнее объединения промежутков и разбирать его мы не беремся.
    """
    parts = s.args if isinstance(s, sp.Union) else (s,)
    out = []
    for p in parts:
        if p is sp.S.EmptySet:
            continue
        if isinstance(p, sp.Interval):
            out.append((p.start, p.end, bool(p.left_open), bool(p.right_open)))
        elif isinstance(p, sp.FiniteSet):
            out.extend((v, v, False, False) for v in p.args)
        else:
            return None
    return sorted(out, key=lambda t: (float(sp.N(t[0])), float(sp.N(t[1]))))


def verify_solution_set(label, got, ineq, var=x, domain=None):
    """Множество решений неравенства. Эталона нет: sympy решает его сам.

    ineq — то самое неравенство, что напечатано в условии, прятать его
    незачем. domain сужает область (n ∈ ℤ⁺, d > 0): в архиве почти всегда
    есть такое условие, и оно меняет ответ.

    Сравнение точное, вместе с концами. Ответ −5 < x < 1 против −5 ≤ x ≤ 1
    не проходит: в markscheme это разные баллы.
    """
    if _blank(label, got):
        return False
    domain = sp.S.Reals if domain is None else domain
    mine = _as_set(got, var)
    if mine is None:
        print(f"{NO} {label}: " + _t(
            "ответ должен быть множеством или неравенством — "
            "Interval(-5, 1), (x >= -5) & (x <= 1), Union(...)",
            "the answer must be a set or an inequality — "
            "Interval(-5, 1), (x >= -5) & (x <= 1), Union(...)"))
        return False

    cond = sp.sympify(ineq)
    try:
        truth = sp.Intersection(cond.as_set(), domain)
    except (NotImplementedError, ValueError, TypeError):
        truth = sp.solveset(cond, var, domain)
    if isinstance(truth, sp.ConditionSet):
        print(f"{NO} {label}: " + _t(
            "sympy не смог решить это неравенство сам — проверка неприменима",
            "sympy could not solve this inequality itself — "
            "the check does not apply"))
        return False

    # Сужать ответ областью нельзя: «d < 0 или d > 9, но d ∈ ℝ⁺, поэтому
    # d > 9» — это и есть последний балл задачи, и потерянное ограничение
    # должно быть видно как лишний кусок ответа.
    if mine == truth:
        print(f"{OK} {label}: {_show_set(truth, var)}")
        return True

    extra = sp.Complement(mine, truth)
    missing = sp.Complement(truth, mine)
    if extra is not sp.S.EmptySet:
        print(f"{NO} {label}: " + _t("лишнее", "extra") + f" — {_show_set(extra, var)}")
    if missing is not sp.S.EmptySet:
        print(f"{NO} {label}: " + _t("потеряно", "missing") + f" — {_show_set(missing, var)}")
    if isinstance(extra, sp.FiniteSet) or isinstance(missing, sp.FiniteSet):
        print("   " + _t(
            "расхождение только в отдельных точках: посмотрите, строгое "
            "неравенство или нет и не обращается ли там в ноль знаменатель",
            "the difference is in isolated points only: check whether the "
            "inequality is strict and whether the denominator vanishes there"))
    return False


def _interior(a, b):
    """Три точки строго внутри промежутка (a, b); бесконечность обрезается."""
    if a == b:
        return []
    lo = a if a.is_finite else (b - 10 if b.is_finite else sp.Integer(-10))
    hi = b if b.is_finite else (a + 10 if a.is_finite else sp.Integer(10))
    return [lo + (hi - lo) * f for f in (sp.Rational(1, 4), sp.Rational(1, 2),
                                         sp.Rational(3, 4))]


def verify_param_set(label, got, holds, var=k, window=(-30, 30),
                     eps=sp.Rational(1, 1000), tol=0):
    """Множество значений буквы, при которых выполняется свойство holds.

    Здесь проверка ничего не решает и ничего не хранит. Она берёт ваше
    множество и спрашивает у самого условия: внутри — выполняется ли,
    снаружи — не выполняется ли. Точки берутся внутри каждого промежутка,
    в каждой дырке, на каждой границе и по обе стороны от неё.

    holds(value) возвращает True, False или None. None означает «в этой
    точке численно судить нельзя» (касание, вырождение) — такая точка
    пропускается, и число пропусков печатается.

    tol > 0 нужен там, где границы найдены калькулятором и записаны с тремя
    значащими цифрами: точки ближе tol к границе не проверяются, потому что
    там ваш округлённый ответ и точная истина расходятся законно.
    """
    if _blank(label, got):
        return False
    mine = _as_set(got, var)
    if mine is None:
        print(f"{NO} {label}: " + _t("ответ должен быть множеством или неравенством",
                               "the answer must be a set or an inequality"))
        return False

    lo, hi = sp.sympify(window[0]), sp.sympify(window[1])
    box = sp.Interval(lo, hi)
    pts = []
    for part in (sp.Intersection(box, mine), sp.Complement(box, mine)):
        for a, b, _, _ in _pieces(part) or []:
            pts.extend(_interior(a, b))
    bounds = []
    for a, b, _, _ in _pieces(mine) or []:
        for pt in (a, b):
            if pt.is_finite:
                bounds.append(pt)
                pts.extend([pt, pt - eps, pt + eps])

    # Регулярная сетка поверх всего. Без неё дефект в одной точке остаётся
    # незамеченным: ответ «m > 0» вместо «m > 0, m ≠ 1» отличается от верного
    # ровно в m = 1, а туда не попадает ни одна проба, привязанная
    # к промежуткам чужого ответа.
    span = hi - lo
    step = sp.Max(1, sp.ceiling(span / 80))
    node = sp.ceiling(lo / step) * step
    while node <= hi:
        pts.append(node)
        node += step

    checked = skipped = 0
    for v in pts:
        if not (lo - 1 <= v <= hi + 1):
            continue
        if tol and any(abs(float(v - c)) <= float(tol) for c in bounds):
            skipped += 1
            continue
        want = bool(mine.contains(v))
        try:
            fact = holds(v)
        except (TypeError, ValueError, ZeroDivisionError, ArithmeticError,
                sp.PolynomialError, sp.GeneratorsNeeded):
            skipped += 1
            continue
        if fact is None:
            skipped += 1
            continue
        checked += 1
        if bool(fact) != want:
            if want:
                print(f"{NO} {label}: " + _t(
                    f"при {var} = {v} условие не выполняется, а ваше "
                    f"множество эту точку содержит",
                    f"at {var} = {v} the condition fails, but your set "
                    f"contains that point"))
            else:
                print(f"{NO} {label}: " + _t(
                    f"при {var} = {v} условие выполняется, а в ваше "
                    f"множество эта точка не входит",
                    f"at {var} = {v} the condition holds, but your set "
                    f"leaves that point out"))
            return False
    if checked < 4:
        print(f"{NO} {label}: " + _t(
            f"проверить не удалось — годных точек нашлось всего {checked}",
            f"cannot be checked — only {checked} usable points were found"))
        return False
    tail = _t(f", пропущено {skipped}", f", {skipped} skipped") if skipped else ""
    print(f"{OK} {label}: {_show_set(mine, var)} — " + _t(
        f"проверено в {checked} точках{tail}",
        f"checked at {checked} points{tail}"))
    return True


def verify_nonneg_form(label, got, expr, var=None):
    """Выражение переписано в явно неотрицательном виде.

    В доказательствах неравенств балл M1 стоит за «attempt to express as
    a square»: доказательство состоит в том, что запись становится
    очевидно неотрицательной. Поэтому проверяется и равенство исходному
    выражению, и вид записи — сумма квадратов, модулей и неотрицательных
    чисел, без слагаемых со знаком минус.

    Это та же логика, что у verify_factored в A4: там просили произведение,
    здесь просят квадрат, и в обоих случаях требование относится к записи.
    """
    if _blank(label, got):
        return False
    e = sp.sympify(got)
    target = sp.sympify(expr)

    for term in sp.Add.make_args(e):
        coeff, rest = term.as_coeff_Mul()
        if coeff.is_negative:
            print(f"{NO} {label}: " + _t(
                f"слагаемое {term} входит со знаком минус — по такой записи "
                f"неотрицательность не видна",
                f"the term {term} carries a minus sign — this form does "
                f"not show that the expression is non-negative"))
            return False
        if rest.is_number:
            if rest.is_negative:
                print(f"{NO} {label}: " + _t(f"слагаемое {term} отрицательно",
                                       f"the term {term} is negative"))
                return False
            continue
        if isinstance(rest, sp.Abs):
            continue
        base, power = rest.as_base_exp()
        if not (power.is_Integer and power > 0 and power % 2 == 0):
            print(f"{NO} {label}: " + _t(
                f"слагаемое {term} — не квадрат и не модуль; "
                f"неотрицательность из такой записи не следует",
                f"the term {term} is neither a square nor an absolute "
                f"value; this form does not make it non-negative"))
            return False

    diff = sp.simplify(sp.expand(e - target))
    if diff != 0:
        print(f"{NO} {label}: " + _t(
            f"запись неотрицательна, но исходному выражению не равна: "
            f"разность {diff}",
            f"the form is non-negative, but it is not equal to the "
            f"original expression: the difference is {diff}"))
        return False
    print(f"{OK} {label}: {e} — " + _t(
        "неотрицательно по виду и равно исходному",
        "non-negative by its form and equal to the original"))
    return True


# --- уравнения --------------------------------------------------------------
#
# Четвёртый раз тема требует своего понятия равенства ответов. A3 сверял
# значения, A4 — форму записи, A8 — множества. Здесь ответом бывает **само
# уравнение**: «show that the x-coordinates satisfy x² − 2dx + 9d = 0» — это
# два балла, и получены они до того, как решение началось. Два уравнения
# равны, если одно получается из другого переносом слагаемых и умножением
# на ненулевое число, — и только так: домножение на выражение с буквой
# меняет множество корней и равенством не является.
#
# Вторая особенность темы в том, что решение не сохраняет равносильность.
# Возведение в квадрат и умножение на знаменатель корни добавляют, деление
# на выражение с переменной — теряет. Поэтому verify_root_set смотрит на
# список корней с двух сторон: каждый ли подставляется в исходное уравнение
# (лишние) и все ли найдены (потерянные). Разница между этими двумя
# ошибками и есть содержание темы, поэтому и сообщения у них разные.


def verify_equation(label, got, want, var=x):
    """Ответ — само уравнение.

    Принимается любая запись, отличающаяся переносом слагаемых и множителем-
    числом: 2x² − 2(m+1)x + 4 = 0 и x² − (m+1)x + 2 = 0 — одно уравнение.
    Домножение на выражение с буквой не принимается: при её нуле уравнение
    вырождается, и корни у записей уже разные.

    Пишите ответ как Eq(левая, правая) или просто выражением, которое
    приравнивается к нулю.
    """
    if _blank(label, got):
        return False

    def flat(e):
        e = sp.sympify(e)
        # Eq(x² + 1, x² + 1) sympy сворачивает в True ещё до нас: обе части
        # совпали дословно, и уравнения не осталось.
        if isinstance(e, sp.logic.boolalg.BooleanAtom):
            return sp.Integer(0) if bool(e) else sp.Integer(1)
        return sp.sympify(e.lhs - e.rhs) if isinstance(e, sp.Eq) else e

    g, w = flat(got), flat(want)
    if sp.simplify(g) == 0:
        print(f"{NO} {label}: " + _t("получилось 0 = 0 — уравнение потеряно целиком",
                               "this is 0 = 0 — the whole equation is gone"))
        return False
    ratio = sp.simplify(sp.cancel(g / w))
    if ratio == 0 or ratio.has(sp.nan, sp.zoo):
        print(f"{NO} {label}: " + _t("это не то уравнение", "this is not the equation"))
        return False
    if ratio.free_symbols:
        den = sp.denom(sp.together(ratio))
        if var in ratio.free_symbols and not den.has(var):
            print(f"{NO} {label}: " + _t(
                f"домножено на {ratio} — выражение с переменной. "
                f"Оно добавляет уравнению свои корни",
                f"multiplied by {ratio} — an expression in the variable. "
                f"It adds its own roots to the equation"))
        elif var not in ratio.free_symbols:
            print(f"{NO} {label}: " + _t(
                f"домножено на {ratio} — выражение с буквой. При его нуле "
                f"уравнение вырождается, так что множество корней "
                f"меняется и уравнения не равны",
                f"multiplied by {ratio} — an expression in a parameter. "
                f"Where it vanishes the equation degenerates, so the root "
                f"set changes and the two equations are not the same"))
        else:
            print(f"{NO} {label}: " + _t(
                f"не сводится к нужному уравнению переносом слагаемых — "
                f"отношение левых частей равно {ratio}",
                f"rearranging terms does not give the required equation — "
                f"the ratio of the two sides is {ratio}"))
        return False
    tail = "" if ratio == 1 else _t(f" (эквивалентная форма, множитель {ratio})",
                                    f" (equivalent form, factor {ratio})")
    print(f"{OK} {label}: {sp.Eq(sp.expand(w), 0)}{tail}")
    return True


def _as_domain(domain, var):
    """Область из условия → множество sympy.

    Принимаются Interval(...), x > 4, (0, oo) как пара границ и None.
    """
    if domain is None:
        return sp.S.Reals
    if isinstance(domain, tuple):
        return sp.Interval(sp.sympify(domain[0]), sp.sympify(domain[1]))
    got = _as_set(domain, var)
    return sp.S.Reals if got is None else got


def _satisfies(expr, var, value, tol=1e-9):
    """Обращает ли value уравнение expr = 0 в верное равенство.

    Возвращает True, False или None — последнее означает, что в этой точке
    уравнение не определено (ноль в знаменателе, логарифм неположительного).
    """
    sub = expr.subs(var, value)
    if sub.has(sp.zoo, sp.nan, sp.oo, -sp.oo):
        return None
    exact = sp.simplify(sub)
    if exact == 0:
        return True
    if exact.has(sp.zoo, sp.nan):
        return None
    try:
        num = complex(sp.N(exact, 30))
    except (TypeError, ValueError):
        return False
    if math.isnan(num.real) or math.isinf(num.real):
        return None
    # Комплексное значение означает, что подстановка вывела за область
    # определения: логарифм отрицательного, корень из отрицательного.
    if abs(num.imag) > tol:
        return None
    return abs(num) < tol


def verify_root_set(label, got, eq, var=x, domain=None):
    """Полный список корней уравнения eq — с обеих сторон.

    Эталон не хранится. Каждый ваш корень подставляется в **исходное**
    уравнение: так ловятся лишние, которые появились при возведении
    в квадрат или умножении на знаменатель. Затем уравнение решается
    самой sympy: так ловятся потерянные.

    domain — область из условия (x > 4, s > 0). Она часть уравнения,
    а не украшение: в архиве корень чаще всего отбрасывают именно
    по области, и за это стоит отдельный балл.
    """
    if _blank(label, got):
        return False
    expr = sp.sympify(eq)
    expr = expr.lhs - expr.rhs if isinstance(expr, sp.Eq) else expr
    region = _as_domain(domain, var)
    given = list(got.args) if isinstance(got, sp.FiniteSet) else list(got)
    given = [sp.sympify(r) for r in given]

    if len(set(map(sp.srepr, [sp.nsimplify(r) if r.is_number else r
                              for r in given]))) != len(given):
        print(f"{NO} {label}: " + _t("один и тот же корень указан дважды",
                               "the same root is listed twice"))
        return False

    for r in given:
        if r.is_real is False or region.contains(r) == sp.false:
            print(f"{NO} {label}: " + _t(
                f"{r} в область условия не входит — этот корень "
                f"отбрасывают, а не записывают",
                f"{r} is outside the domain given in the question — "
                f"that root is rejected, not written down"))
            return False
        ok = _satisfies(expr, var, r)
        if ok is None:
            print(f"{NO} {label}: " + _t(
                f"при {var} = {r} уравнение не определено — ноль "
                f"в знаменателе или логарифм неположительного",
                f"at {var} = {r} the equation is undefined — a zero "
                f"denominator, or the logarithm of a non-positive number"))
            return False
        if not ok:
            print(f"{NO} {label}: " + _t(
                f"{r} исходное уравнение в верное равенство не обращает. "
                f"Такой корень появляется, когда обе части возводят "
                f"в квадрат или умножают на знаменатель",
                f"{r} does not satisfy the original equation. A root like "
                f"this appears when both sides are squared or multiplied "
                f"by a denominator"))
            return False

    truth = sp.solveset(expr, var, region)
    if truth is sp.S.EmptySet:
        truth = sp.FiniteSet()
    elif not isinstance(truth, sp.FiniteSet):
        cand = sp.solve(expr, var, dict=False)
        cand = cand if isinstance(cand, list) else [cand]
        good = []
        for c in cand:
            c = sp.sympify(c)
            if c.free_symbols or c.is_real is False:
                continue
            if region.contains(c) == sp.true and _satisfies(expr, var, c):
                good.append(c)
        if not good and not given:
            print(f"{NO} {label}: " + _t(
                "sympy не смог решить это уравнение сам — проверка "
                "неприменима",
                "sympy could not solve this equation itself — the check "
                "does not apply"))
            return False
        truth = sp.FiniteSet(*good)

    def same(one, other):
        """Совпадают ли корни. Десятичная запись считается совпадением:
        различать √17 и 4.1231056 — дело формулировки «exact value»,
        а не полноты набора."""
        if sp.simplify(one - other) == 0:
            return True
        try:
            return abs(complex(sp.N(one - other, 30))) < 1e-9
        except (TypeError, ValueError):
            return False

    missing = [r for r in truth.args if not any(same(r, g) for g in given)]
    if missing:
        shown = ', '.join(str(m) for m in sorted(missing, key=lambda v: sp.N(v)))
        print(f"{NO} {label}: " + _t(
            f"корни верны, но найдено не всё — потеряно {shown}. Так теряют "
            f"корень, когда делят обе части на выражение с переменной",
            f"the roots you list are correct, but not all of them are "
            f"there — {shown} is missing. A root is lost like this when "
            f"both sides are divided by an expression in the variable"))
        return False
    print(f"{OK} {label}: {{{', '.join(str(r) for r in given)}}}")
    return True


def verify_vertex_form(label, got, expr, var=x):
    """Квадратный трёхчлен, записанный в виде a(x − h)² + k.

    Требование относится к записи, как verify_factored в A4: ответ должен
    быть суммой одного полного квадрата и числа, а в квадрате должен стоять
    именно (x − h), а не (2x − 1) и не (√5·x + 1). Равенство исходному
    выражению проверяется отдельно.
    """
    if _blank(label, got):
        return False
    e = sp.sympify(got)
    target = sp.sympify(expr)

    square = None
    for term in sp.Add.make_args(e):
        if not term.has(var):
            continue
        coeff, rest = term.as_coeff_Mul()
        base, power = rest.as_base_exp()
        if power != 2 or sp.degree(sp.Poly(base, var)) != 1:
            print(f"{NO} {label}: " + _t(
                f"слагаемое {term} — не полный квадрат вида a(x − h)²",
                f"the term {term} is not a complete square a(x − h)²"))
            return False
        if sp.Poly(base, var).all_coeffs()[0] != 1:
            print(f"{NO} {label}: " + _t(
                f"в квадрате стоит {base}, а нужно (x − h) с единичным "
                f"коэффициентом при {var}",
                f"the square contains {base}, but it must be (x − h) with "
                f"coefficient 1 on {var}"))
            return False
        if square is not None:
            print(f"{NO} {label}: " + _t(
                f"в записи больше одного слагаемого с {var}",
                f"there is more than one term containing {var}"))
            return False
        square = term
    if square is None:
        print(f"{NO} {label}: " + _t(
            "в записи нет квадрата — это не форма a(x − h)² + k",
            "there is no square here — this is not the form a(x − h)² + k"))
        return False

    diff = sp.simplify(sp.expand(e - target))
    if diff != 0:
        print(f"{NO} {label}: " + _t(
            f"форма верная, но исходному выражению запись не равна: "
            f"разность {diff}",
            f"the form is right, but it is not equal to the original "
            f"expression: the difference is {diff}"))
        return False
    print(f"{OK} {label}: {e}")
    return True


# --- композиция и обратные функции ------------------------------------------
#
# Шестой раз серии нужен свой ответ на вопрос «когда два ответа одинаковы».
# A3 сверял значения, A4 — форму записи, A8 — множества, B1 — уравнения,
# C1 — конфигурацию. Здесь ответ это **функция**, и верна она тогда, когда
# отменяет исходную: got(f(t)) = t на области из условия. Эталона нет вовсе,
# ровно как в verify_ode, где ответ подставляли в само уравнение.
#
# Проверять приходится численно, и это не лень. Символьно ветвь корня
# не различить: sqrt(t**2) sympy до t не доводит, потому что без указания
# знака это |t|. А знак здесь и есть содержание темы — за выбор ветви
# в markscheme стоит отдельный R1.
#
# Направление выбрано одно и намеренно. got(f(t)) = t ловит неверную ветвь:
# у f(x) = sqrt(x^2 - 1) ответ -sqrt(x^2 + 1) проходит проверку
# f(got(s)) = s (там всё уходит под квадрат), а got(f(t)) = t даёт -t.
# Обратное направление такой ошибки не видит вовсе.


def _domain_points(region, count=9):
    """Точки внутри множества region; бесконечные концы обрезаются.

    Концы включаются, когда они принадлежат множеству: у обратной функции
    значение на конце области — отдельный балл, и проверять его надо.
    """
    parts = region.args if isinstance(region, sp.Union) else (region,)
    pts = []
    for part in parts:
        if isinstance(part, sp.FiniteSet):
            pts.extend(part.args)
            continue
        if not isinstance(part, sp.Interval):
            continue
        lo, hi = part.start, part.end
        lo = lo if lo.is_finite else (hi - 10 if hi.is_finite else sp.Integer(-10))
        hi = hi if hi.is_finite else (lo + 10 if lo.is_finite else sp.Integer(10))
        if lo == hi:
            pts.append(lo)
            continue
        for i in range(count):
            pts.append(lo + (hi - lo) * sp.Rational(i + 1, count + 1))
        for end, is_open in ((part.start, part.left_open), (part.end, part.right_open)):
            if end.is_finite and not is_open:
                pts.append(end)
    return pts


def verify_inverse(label, got, f, var=x, domain=None, count=9, tol=1e-7):
    """got — обратная к f. Эталон не хранится: проверяется, что got(f(t)) = t.

    domain — область f из условия. Она не украшение: у f(x) = sqrt(x^2 - 1)
    на [1, 2] обратная это +sqrt(x^2 + 1), а на [-2, -1] — минус, и различает
    их только область.

    Сначала пробуем символически, потом по точкам области. Численно —
    потому что sympy не упрощает sqrt(t**2) до t, не зная знака t,
    а знак здесь и есть содержание задачи.

    Чего проверка не делает: не проверяет, что вы верно назвали область
    самой обратной. Это отдельный ответ, и рядом стоит check_domain.
    """
    if _blank(label, got):
        return False
    e, fun = sp.sympify(got), sp.sympify(f)
    region = _as_domain(domain, var)

    back = e.subs(var, fun)
    try:
        if sp.simplify(back - var) == 0:
            print(f"{OK} {label}: " + _t(
                f"{e} — подстановка f внутрь даёт {var} тождественно",
                f"{e} — substituting f into it gives {var} identically"))
            return True
    except (TypeError, ValueError, AttributeError):
        pass

    checked = 0
    for t in _domain_points(region, count):
        try:
            inner = complex(sp.N(fun.subs(var, t), 25))
            outer = complex(sp.N(e.subs(var, sp.nsimplify(inner.real)
                                        if abs(inner.imag) < tol else inner), 25))
            want = complex(sp.N(t, 25))
        except (TypeError, ValueError, ZeroDivisionError):
            continue
        if not all(math.isfinite(v) for v in (inner.real, inner.imag,
                                              outer.real, outer.imag)):
            continue
        if abs(inner.imag) > tol or abs(outer.imag) > tol:
            continue
        checked += 1
        if abs(outer - want) > tol * max(1.0, abs(want)):
            # Подсказка про ветвь уместна только там, где ветвь есть.
            # Если знак сошёлся, а величина нет, дело в алгебре, и звать
            # ученика проверять знак корня значит сбивать его с дороги.
            flip = abs(outer + want) <= tol * max(1.0, abs(want))
            hint = _t(
                " Знак противоположный — это не та ветвь корня, "
                "а выбирает её область из условия." if flip else "",
                " The sign is the opposite one: this is the wrong branch "
                "of the root, and the domain in the question is what "
                "chooses it." if flip else "")
            print(f"{NO} {label}: " + _t(
                f"при {var} = {sp.nsimplify(t)} исходная функция даёт "
                f"{inner.real:.6g}, а ваша обратная возвращает "
                f"{outer.real:.6g} вместо {want.real:.6g}.{hint}",
                f"at {var} = {sp.nsimplify(t)} the original function gives "
                f"{inner.real:.6g}, and your inverse sends that back to "
                f"{outer.real:.6g} instead of {want.real:.6g}.{hint}"))
            return False
    if checked < 4:
        print(f"{NO} {label}: " + _t(
            f"проверить не удалось — годных точек области нашлось "
            f"всего {checked}",
            f"cannot be checked — only {checked} usable points of the "
            f"domain were found"))
        return False
    print(f"{OK} {label}: {e} — " + _t(
        f"отменяет исходную функцию, проверено в {checked} точках области",
        f"undoes the original function, checked at {checked} points "
        f"of the domain"))
    return True


def check_domain(label, got, want_digest, var=x):
    """Ответ — область определения или множество значений.

    Запись не важна: Interval(-3, 5), (x >= -3) & (x <= 5) и
    Union(Interval(0, 1), Interval(2, 3)) сверяются одинаково. А вот концы
    важны: [0, sqrt(3)] и (0, sqrt(3)) — разные ответы, и в markscheme
    это разные баллы. Поэтому check_set здесь не годится: он про наборы
    отдельных значений, а тут промежутки.
    """
    if _blank(label, got):
        return False
    s = _as_set(got, var)
    if s is None:
        print(f"{NO} {label}: " + _t(
            "ответ должен быть множеством или неравенством — "
            "Interval(0, 2), (x > 0) & (x <= 2), Interval.Lopen(0, 2)",
            "the answer must be a set or an inequality — "
            "Interval(0, 2), (x > 0) & (x <= 2), Interval.Lopen(0, 2)"))
        return False
    if digest(sp.srepr(s)) == want_digest:
        print(f"{OK} {label}: {_show_set(s, var)}")
        return True
    print(f"{NO} {label}: {_show_set(s, var)} — " + _t(
        "не сходится. Посмотрите на концы: включён конец или выколот — "
        "это отдельный балл",
        "no match. Look at the endpoints: whether an endpoint is included "
        "or excluded is a mark of its own"))
    return False


# --- преобразования графиков ------------------------------------------------
#
# Седьмой раз серии нужен свой ответ на вопрос «когда два ответа одинаковы».
# A3 сверял значения, A4 — форму записи, A8 — множества, B1 — уравнения,
# C1 — конфигурацию, B2 — функцию по тому, что она отменяет. Здесь ответом
# служит **картинка**. Проверить её можно двумя способами, потому что и
# спрашивают её в архиве двумя способами.
#
# «Describe a sequence of transformations» — ответ это **рецепт**, и верен он
# тогда, когда, выполненный над исходным графиком, даёт целевой.
# verify_transform не сравнивает ваше описание с эталонным описанием:
# он берёт ваши шаги и применяет их по очереди к исходной функции. Поэтому
# любой верный порядок проходит, а неверный — нет, и это не придирка:
# в markscheme за перепутанный порядок горизонтальных преобразований
# стоит A1A0.
#
# «Sketch the graph» — ответ это **список особенностей**: пересечения с осями,
# асимптоты, точки поворота, изломы, концы. Именно за них и платят баллы:
# «indicating any asymptotes», «clearly showing the coordinates of any points
# where f'(x) = 0». verify_sketch считает их из самой функции и сверяет
# с вашим списком в обе стороны — лишнее и пропущенное это разные ошибки.

_TRANSFORMS = ('shift_x', 'shift_y', 'stretch_x', 'stretch_y',
               'reflect_in_x_axis', 'reflect_in_y_axis')

_TRANSFORM_ALIAS = {
    'reflect_x': 'reflect_in_x_axis', 'reflect_y': 'reflect_in_y_axis',
    'reflect_in_the_x_axis': 'reflect_in_x_axis',
    'reflect_in_the_y_axis': 'reflect_in_y_axis',
    'translate_x': 'shift_x', 'translate_y': 'shift_y',
    'shift_right': 'shift_x', 'shift_up': 'shift_y',
    'stretch_horizontal': 'stretch_x', 'stretch_vertical': 'stretch_y',
}


def _as_step(step):
    """Один шаг преобразования → (имя, величина) или None.

    Принимается ('shift_x', 3), ['stretch_y', 2] и голая строка
    'reflect_in_x_axis' для отражений, у которых величины нет.
    """
    if isinstance(step, str):
        name, value = step, None
    elif isinstance(step, (tuple, list)) and len(step) == 2:
        name, value = step[0], step[1]
    elif isinstance(step, (tuple, list)) and len(step) == 1:
        name, value = step[0], None
    else:
        return None
    name = _TRANSFORM_ALIAS.get(str(name).strip().lower().replace(' ', '_'),
                                str(name).strip().lower().replace(' ', '_'))
    if name not in _TRANSFORMS:
        return None
    if name.startswith('reflect'):
        return name, None
    if value is None:
        return None
    try:
        return name, sp.sympify(value)
    except (TypeError, ValueError, sp.SympifyError):
        return None


def _apply_steps(expr, steps, var):
    """Применяет шаги по очереди к графику y = expr.

    Подстановка идёт в уже накопленное выражение, а не в исходное: именно
    так преобразования и складываются. Растяжение по горизонтали в k раз
    заменяет x на x/k — это то место, где путают k и 1/k.
    """
    cur = sp.sympify(expr)
    for name, value in steps:
        if name == 'shift_x':
            cur = cur.subs(var, var - value)
        elif name == 'shift_y':
            cur = cur + value
        elif name == 'stretch_x':
            cur = cur.subs(var, var / value)
        elif name == 'stretch_y':
            cur = value * cur
        elif name == 'reflect_in_x_axis':
            cur = -cur
        else:
            cur = cur.subs(var, -var)
    return cur


def _show_steps(steps, var=None):
    """Человеческая запись списка шагов — для сообщений проверки."""
    words = {'shift_x': _t('сдвиг по x на', 'translation in x by'),
             'shift_y': _t('сдвиг по y на', 'translation in y by'),
             'stretch_x': _t('растяжение по x в', 'horizontal stretch factor'),
             'stretch_y': _t('растяжение по y в', 'vertical stretch factor'),
             'reflect_in_x_axis': _t('отражение в оси x', 'reflection in the x-axis'),
             'reflect_in_y_axis': _t('отражение в оси y', 'reflection in the y-axis')}
    out = []
    for name, value in steps:
        out.append(words[name] if value is None else f"{words[name]} {value}")
    return ' → '.join(out)


def verify_transform(label, got, source, target, var=x,
                     samples=(1, 2, 3, 4, 5, 6, 7, 8)):
    """got — последовательность преобразований, переводящая source в target.

    Эталонного описания нет вовсе. Ваши шаги применяются к source по очереди,
    и результат сверяется с target. Отсюда два следствия, оба верные:
    любой порядок, который действительно приводит к цели, засчитывается,
    а порядок, который не приводит, — нет.

    Шаги записываются так:

        ('shift_x', h)    сдвиг на h вправо (h < 0 — влево)
        ('shift_y', k)    сдвиг на k вверх
        ('stretch_x', s)  растяжение по горизонтали в s раз
        ('stretch_y', s)  растяжение по вертикали в s раз
        'reflect_in_x_axis'
        'reflect_in_y_axis'

    Чего проверка не делает: не требует кратчайшего описания. Пять шагов,
    приводящих к цели, пройдут так же, как три. В markscheme за лишние
    верные шаги тоже не снимают.
    """
    if _blank(label, got):
        return False
    if isinstance(got, (str, tuple)) and _as_step(got) is not None:
        got = [got]                      # один шаг можно писать без списка
    if not isinstance(got, (list, tuple)) or not len(got):
        print(f"{NO} {label}: " + _t(
            "ответ — список шагов, например "
            "[('stretch_x', Rational(1, 2)), ('shift_y', pi/4)]",
            "the answer is a list of steps, for example "
            "[('stretch_x', Rational(1, 2)), ('shift_y', pi/4)]"))
        return False

    steps = []
    for raw in got:
        step = _as_step(raw)
        if step is None:
            print(f"{NO} {label}: " + _t(
                f"шаг {raw!r} не разобран. Известны: {', '.join(_TRANSFORMS)}",
                f"cannot read the step {raw!r}. "
                f"The known ones are: {', '.join(_TRANSFORMS)}"))
            return False
        steps.append(step)

    src, dst = sp.sympify(source), sp.sympify(target)
    ok, note = _agrees(_apply_steps(src, steps, var), dst, var, samples)
    if ok:
        print(f"{OK} {label}: {_show_steps(steps)} — " + _t(
            f"переводит {src} в {dst}", f"maps {src} onto {dst}"))
        return True

    # Тот же набор шагов в другом порядке. Это самая частая ошибка темы
    # и единственная, за которую markscheme снимает ровно один балл.
    if 1 < len(steps) <= 5:
        for order in itertools.permutations(steps):
            if list(order) == steps:
                continue
            if _agrees(_apply_steps(src, list(order), var), dst, var, samples)[0]:
                print(f"{NO} {label}: " + _t(
                    "шаги названы верно, но не в том порядке — в этом "
                    "порядке они дают другой график. Сдвиг до растяжения "
                    "и после него это разные вещи.",
                    "the right transformations, but not in this order — "
                    "in this order they give a different graph. A translation "
                    "before a stretch and after it are not the same thing."))
                return False

    # Растяжение перепутано со своей обратной величиной: f(kx) — это
    # растяжение в 1/k раз, и наоборот.
    for i, (name, value) in enumerate(steps):
        if not name.startswith('stretch') or value == 0:
            continue
        swapped = list(steps)
        swapped[i] = (name, 1 / value)
        if _agrees(_apply_steps(src, swapped, var), dst, var, samples)[0]:
            axis = 'x' if name.endswith('x') else 'y'
            print(f"{NO} {label}: " + _t(
                f"растяжение по {axis} взято обратным: подошло бы "
                f"{1 / value}, а не {value}. Замена x на x/s — это "
                f"растяжение в s раз, а f(kx) растягивает в 1/k."
                if axis == 'x' else
                f"растяжение по {axis} взято обратным: подошло бы "
                f"{1 / value}, а не {value}.",
                f"the {axis}-stretch is the reciprocal of the right one: "
                f"{1 / value} would fit, not {value}. Replacing x by x/s "
                f"stretches by s, so f(kx) is a stretch by 1/k."
                if axis == 'x' else
                f"the {axis}-stretch is the reciprocal of the right one: "
                f"{1 / value} would fit, not {value}."))
            return False

    # Сдвиг в другую сторону: f(x − h) двигает график вправо, а не влево.
    for i, (name, value) in enumerate(steps):
        if not name.startswith('shift'):
            continue
        flipped = list(steps)
        flipped[i] = (name, -value)
        if _agrees(_apply_steps(src, flipped, var), dst, var, samples)[0]:
            axis = 'x' if name.endswith('x') else 'y'
            print(f"{NO} {label}: " + _t(
                f"сдвиг по {axis} в другую сторону: подошло бы {-value}. "
                f"f(x − h) двигает график на h вправо."
                if axis == 'x' else
                f"сдвиг по {axis} в другую сторону: подошло бы {-value}.",
                f"the {axis}-translation goes the other way: {-value} would "
                f"fit. f(x − h) moves the graph h to the right."
                if axis == 'x' else
                f"the {axis}-translation goes the other way: "
                f"{-value} would fit."))
            return False

    tail = f" ({note})" if note else ""
    print(f"{NO} {label}: " + _t(
        f"эти шаги дают {sp.simplify(_apply_steps(src, steps, var))}, "
        f"а нужен {dst}{tail}",
        f"these steps give {sp.simplify(_apply_steps(src, steps, var))}, "
        f"and the target is {dst}{tail}"))
    return False


_SKETCH_KEYS = ('x_intercepts', 'y_intercept', 'maxima', 'minima', 'cusps',
                'vertical_asymptotes', 'horizontal_asymptotes',
                'oblique_asymptotes', 'endpoints')


def _bounds(region):
    """Концы промежутка; для неограниченных возвращает ±oo."""
    if isinstance(region, sp.Interval):
        return region.start, region.end
    return -sp.oo, sp.oo


def _num(value):
    """Число с плавающей точкой или None, если не выходит."""
    try:
        out = complex(sp.N(sp.sympify(value), 25))
    except (TypeError, ValueError, AttributeError, sp.SympifyError):
        return None
    if abs(out.imag) > 1e-9 or not math.isfinite(out.real):
        return None
    return out.real


def _sketch_extrema(fun, var, lo, hi, poles, samples=4000):
    """Точки поворота и изломы — численно, сканированием.

    Численно, потому что тема живёт на модулях: у |f| производная содержит
    sign(...), и solveset с ней не справляется. Скан работает одинаково
    для модуля, обратной величины и кусочно заданной функции.

    Возвращает список (x, y, вид), где вид — 'max', 'min', 'cusp_max'
    или 'cusp_min'.
    """
    try:
        g = sp.lambdify(var, fun, 'math')
    except (TypeError, ValueError):
        return []

    def value(t):
        try:
            out = g(t)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError):
            return None
        return out if isinstance(out, float) and math.isfinite(out) else (
            float(out) if isinstance(out, int) else None)

    lo_f = -12.0 if lo == -sp.oo else float(lo)
    hi_f = 12.0 if hi == sp.oo else float(hi)
    if not hi_f > lo_f:
        return []
    step = (hi_f - lo_f) / samples
    gap = 20 * step
    pts = []
    for i in range(samples + 1):
        t = lo_f + i * step
        if any(abs(t - p) < gap for p in poles):
            pts.append((t, None))
            continue
        pts.append((t, value(t)))

    found = []
    for (t0, v0), (t1, v1), (t2, v2) in zip(pts, pts[1:], pts[2:]):
        if None in (v0, v1, v2):
            continue
        rising, falling = v1 - v0, v2 - v1
        if rising > 0 >= falling:
            kind = 'max'
        elif rising < 0 <= falling:
            kind = 'min'
        else:
            continue
        # Уточняем тернарным поиском: на гладкой вершине он сходится
        # к самой точке, на изломе — тоже, потому что излом это максимум
        # или минимум ничуть не меньше гладкого.
        a, b = t0, t2
        for _ in range(80):
            m1, m2 = a + (b - a) / 3, b - (b - a) / 3
            f1, f2 = value(m1), value(m2)
            if f1 is None or f2 is None:
                break
            better = f1 > f2 if kind == 'max' else f1 < f2
            if better:
                b = m2
            else:
                a = m1
        tx = (a + b) / 2
        ty = value(tx)
        if ty is None:
            continue
        # Излом или гладкая вершина: у гладкой односторонние наклоны
        # стремятся к нулю, у излома — нет.
        h = max(1e-6, (hi_f - lo_f) * 1e-6)
        left, right = value(tx - h), value(tx + h)
        cusp = False
        if left is not None and right is not None:
            slopes = (abs(ty - left) / h, abs(right - ty) / h)
            cusp = min(slopes) > 1e-3
        if found and abs(found[-1][0] - tx) < 10 * step:
            continue
        found.append((tx, ty, ('cusp_' + kind) if cusp else kind))
    return found


def _sketch_facts(fun, var, region):
    """Что у функции есть на самом деле: словарь тех же ключей, что и ответ."""
    lo, hi = _bounds(region)
    facts = {k: [] for k in _SKETCH_KEYS}
    facts['y_intercept'] = None

    poles = []
    try:
        # singularities для тригонометрии возвращает бесконечное семейство
        # (ImageSet), и пересечение с областью — единственный способ
        # получить из него список точек.
        sing = sp.singularities(fun, var)
        if not isinstance(sing, sp.FiniteSet):
            sing = sing.intersect(region.closure)
        candidates = sing.args if isinstance(sing, sp.FiniteSet) else ()
        for c in candidates:
                cv = _num(c)
                if cv is None or c not in region.closure:
                    continue
                for side in ('+', '-'):
                    try:
                        lim = sp.limit(fun, var, c, side)
                    except (NotImplementedError, ValueError, TypeError):
                        continue
                    if lim in (sp.oo, -sp.oo, sp.zoo):
                        poles.append(cv)
                        facts['vertical_asymptotes'].append(cv)
                        break
    except (NotImplementedError, TypeError, ValueError, AttributeError):
        pass

    for end, sign in ((hi, 1), (lo, -1)):
        if end not in (sp.oo, -sp.oo):
            continue
        direction = sp.oo if sign > 0 else -sp.oo
        try:
            lim = sp.limit(fun, var, direction)
        except (NotImplementedError, ValueError, TypeError):
            continue
        if lim.is_finite:
            val = _num(lim)
            if val is not None and val not in facts['horizontal_asymptotes']:
                facts['horizontal_asymptotes'].append(val)
            continue
        try:
            m = sp.limit(fun / var, var, direction)
            if not (m.is_finite and m != 0):
                continue
            b = sp.limit(fun - m * var, var, direction)
        except (NotImplementedError, ValueError, TypeError):
            continue
        if b.is_finite:
            line = sp.simplify(m * var + b)
            if all(sp.simplify(line - other) != 0
                   for other in facts['oblique_asymptotes']):
                facts['oblique_asymptotes'].append(line)

    lo_f = -12.0 if lo == -sp.oo else float(lo)
    hi_f = 12.0 if hi == sp.oo else float(hi)
    try:
        g = sp.lambdify(var, fun, 'math')
        roots = [r for r in _scan_roots(g, lo_f, hi_f, 8000)
                 if all(abs(r - p) > 1e-6 for p in poles)]
    except (TypeError, ValueError):
        roots = []
    facts['x_intercepts'] = roots

    if 0 in region:
        val = _num(fun.subs(var, 0))
        if val is not None:
            facts['y_intercept'] = val

    for tx, ty, kind in _sketch_extrema(fun, var, lo, hi, poles):
        if kind == 'max':
            facts['maxima'].append((tx, ty))
        elif kind == 'min':
            facts['minima'].append((tx, ty))
        else:
            facts['cusps'].append((tx, ty))
        # Ноль, до которого график только дотрагивается, сменой знака
        # не ловится: у |f| в корне излом, а у чётного корня касание.
        # Такая точка — и вершина, и пересечение с осью сразу.
        if abs(ty) < 1e-9 and all(abs(tx - r) > 1e-6
                                  for r in facts['x_intercepts']):
            facts['x_intercepts'].append(tx)
    facts['x_intercepts'].sort()

    for end in (lo, hi):
        if end in (sp.oo, -sp.oo) or end not in region:
            continue
        val = _num(fun.subs(var, end))
        if val is None:
            continue
        facts['endpoints'].append((float(end), val))
        # Ноль ровно на конце отрезка скан не ловит: смены знака там нет,
        # а точного нуля в числах с плавающей точкой обычно тоже.
        if abs(val) < 1e-9 and all(abs(float(end) - r) > 1e-6
                                   for r in facts['x_intercepts']):
            facts['x_intercepts'].append(float(end))
    facts['x_intercepts'].sort()
    return facts


def _close(a, b, tol):
    return abs(a - b) <= max(1e-7, tol * max(1.0, abs(b)))


def _tidy(value):
    """Число для сообщения: почти-ноль печатаем нулём, а не 1.8e-15."""
    return f"{0.0 if abs(value) < 1e-9 else value:.6g}"


def _as_pair(value):
    """Точка (x, y) из ответа; одно число тоже принимается как x."""
    if isinstance(value, (tuple, list)) and len(value) == 2:
        px, py = _num(value[0]), _num(value[1])
        return None if px is None or py is None else (px, py)
    px = _num(value)
    return None if px is None else (px, None)


def verify_sketch(label, got, f, var=x, domain=None, tol=5e-3):
    """Эскиз проверяется по списку особенностей, а не по картинке.

    got — словарь; проверяются только те ключи, которые в нём есть:

        'x_intercepts'          [x, ...]
        'y_intercept'           y
        'maxima', 'minima'      [(x, y), ...] — гладкие точки поворота
        'cusps'                 [(x, y), ...] — изломы
        'vertical_asymptotes'   [x, ...]
        'horizontal_asymptotes' [y, ...]
        'oblique_asymptotes'    [выражение от var, ...]
        'endpoints'             [(x, y), ...]

    Эталон не хранится: всё считается из самой f. Поэтому ошибки бывают
    двух разных видов, и проверка их различает — названо лишнее и
    пропущено нужное. В markscheme это тоже разные баллы.

    Совпадение числовое, с точностью до трёх значащих цифр: координаты,
    снятые с калькулятора, экзамен принимает именно так. Отсюда и допуск
    5e-3 по относительной величине — ровно половина единицы третьего
    разряда. Ответ, ошибочный в четвёртой цифре, проверку пройдёт.

    Чего проверка не делает: не смотрит на форму кривой между
    особенностями. Выпуклость, монотонность и «asymptotic behaviour»
    остаются на вашей совести и на рисунке.
    """
    if _blank(label, got):
        return False
    if not isinstance(got, dict):
        print(f"{NO} {label}: " + _t(
            f"ответ — словарь; ключи: {', '.join(_SKETCH_KEYS)}",
            f"the answer is a dict; the keys are: {', '.join(_SKETCH_KEYS)}"))
        return False
    unknown = [k for k in got if k not in _SKETCH_KEYS]
    if unknown:
        print(f"{NO} {label}: " + _t(
            f"неизвестные ключи: {', '.join(unknown)}. "
            f"Известны: {', '.join(_SKETCH_KEYS)}",
            f"unknown keys: {', '.join(unknown)}. "
            f"The known ones are: {', '.join(_SKETCH_KEYS)}"))
        return False

    fun = sp.sympify(f)
    region = _as_domain(domain, var)
    facts = _sketch_facts(fun, var, region)
    turning = {'maxima': _t('максимум', 'maximum'),
               'minima': _t('минимум', 'minimum'),
               'cusps': _t('излом', 'cusp'),
               'endpoints': _t('конец', 'endpoint')}

    for key, claimed in got.items():
        if key == 'y_intercept':
            want = facts['y_intercept']
            mine = _num(claimed)
            if mine is None:
                print(f"{NO} {label}: " + _t(
                    "пересечение с осью y — это число",
                    "the y-intercept is a number"))
                return False
            if want is None:
                print(f"{NO} {label}: " + _t(
                    "ось y эта функция не пересекает: нуля нет в области",
                    "this function has no y-intercept: 0 is not in the domain"))
                return False
            if not _close(mine, want, tol):
                print(f"{NO} {label}: " + _t(
                    f"на оси y функция равна {_tidy(want)}, а не {_tidy(mine)}",
                    f"on the y-axis the function is {_tidy(want)}, not {_tidy(mine)}"))
                return False
            continue

        if not isinstance(claimed, (list, tuple, set)):
            claimed = [claimed]
        if key == 'oblique_asymptotes':
            want_lines = list(facts['oblique_asymptotes'])
            for item in claimed:
                try:
                    line = sp.sympify(item)
                except (TypeError, ValueError, sp.SympifyError):
                    line = None
                hit = next((w for w in want_lines
                            if line is not None
                            and sp.simplify(line - w) == 0), None)
                if hit is None:
                    print(f"{NO} {label}: " + _t(
                        f"наклонной асимптоты y = {item} у этой функции нет",
                        f"this function has no oblique asymptote y = {item}"))
                    return False
                want_lines.remove(hit)
            if want_lines:
                print(f"{NO} {label}: " + _t(
                    f"пропущена наклонная асимптота y = {want_lines[0]}",
                    f"an oblique asymptote is missing: y = {want_lines[0]}"))
                return False
            continue

        want_pts = [(v, None) for v in facts[key]] if key in (
            'x_intercepts', 'vertical_asymptotes', 'horizontal_asymptotes'
        ) else list(facts[key])
        left = list(want_pts)
        for item in claimed:
            pair = _as_pair(item)
            if pair is None:
                print(f"{NO} {label}: " + _t(
                    f"в {key} не разобрано значение {item!r}",
                    f"cannot read the value {item!r} in {key}"))
                return False
            px, py = pair
            hit = next((w for w in left if _close(px, w[0], tol)), None)
            if hit is None:
                # Точка поворота, названная не тем видом: это отдельная
                # ошибка и отдельное объяснение. Сверяются только вершины
                # между собой: пересечение с осью и излом бывают одной
                # и той же точкой, и это не ошибка.
                for other in (('maxima', 'minima', 'cusps', 'endpoints')
                              if key in ('maxima', 'minima', 'cusps',
                                         'endpoints') else ()):
                    if other == key:
                        continue
                    if any(_close(px, w[0], tol) for w in facts[other]):
                        print(f"{NO} {label}: " + _t(
                            f"при {var} = {_tidy(px)} у графика "
                            f"{turning.get(other, other)}, а не "
                            f"{turning.get(key, key)}",
                            f"at {var} = {_tidy(px)} the graph has a "
                            f"{turning.get(other, other)}, not a "
                            f"{turning.get(key, key)}"))
                        return False
                print(f"{NO} {label}: " + _t(
                    f"лишнее в {key}: при {var} = {_tidy(px)} этого нет",
                    f"extra in {key}: there is nothing at {var} = {_tidy(px)}"))
                return False
            if py is not None and hit[1] is not None and not _close(py, hit[1], tol):
                print(f"{NO} {label}: " + _t(
                    f"при {var} = {_tidy(hit[0])} значение {_tidy(hit[1])}, "
                    f"а не {_tidy(py)}",
                    f"at {var} = {_tidy(hit[0])} the value is {_tidy(hit[1])}, "
                    f"not {_tidy(py)}"))
                return False
            left.remove(hit)
        if left:
            miss = left[0]
            place = (f"{var} = {_tidy(miss[0])}" if miss[1] is None
                     else f"({_tidy(miss[0])}, {_tidy(miss[1])})")
            print(f"{NO} {label}: " + _t(
                f"в {key} пропущено: {place}",
                f"missing from {key}: {place}"))
            return False

    counted = ', '.join(f"{k}: {len(got[k]) if isinstance(got[k], (list, tuple, set)) else 1}"
                        for k in _SKETCH_KEYS if k in got)
    print(f"{OK} {label}: " + _t(f"все особенности на месте ({counted})",
                                 f"every feature checks out ({counted})"))
    return True


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


def verify_exact(label, got, want):
    """Точный ответ: «give your answer in the form p√q», «find the exact value».

    Принимается любая эквивалентная точная запись (3√14/5 и √126/5 — одно
    и то же число), но десятичная дробь не принимается, даже если совпадает
    во всех печатаемых знаках: «exact» — требование к записи, и markscheme
    за 4.12 вместо √17 балла не ставит.
    """
    if _blank(label, got):
        return False
    e = sp.sympify(got)
    if e.atoms(sp.Float):
        print(f"{NO} {label}: {e} — " + _t(
            "это десятичная запись, а вопрос просит точное значение: "
            "оставьте корень или дробь",
            "this is a decimal, and the question asks for the exact "
            "value: keep the surd or the fraction"))
        return False
    if sp.simplify(e - sp.sympify(want)) != 0:
        print(f"{NO} {label}: {e} — " + _t("не сходится", "no match"))
        return False
    print(f"{OK} {label}: {e}")
    return True


def verify_roots(label, roots, expr, domain, var=x, deg=False, tol=1e-9):
    """Корни уравнения expr = 0 на отрезке domain = (a, b).

    Эталона нет: каждый предложенный корень подставляется в уравнение, а
    полнота набора проверяется независимым численным сканированием отрезка.
    Поэтому засчитывается любая верная форма записи (pi/6, 30 градусов,
    0.5235987...), и отдельно ловится самая частая потеря баллов в теме —
    найденный корень при потерянных остальных.

    deg=True — корни и границы заданы в градусах.
    """
    if _blank(label, roots):
        return False
    expr = sp.sympify(expr)
    a, b = [sp.sympify(v) for v in domain]
    k = sp.pi / 180 if deg else sp.Integer(1)
    f = sp.lambdify(var, expr.subs(var, var * k), 'math')

    given = [sp.sympify(r) for r in roots]
    bad = []
    for r in given:
        if not (float(a) - tol <= float(r) <= float(b) + tol):
            bad.append((r, _t('вне области', 'outside the interval')))
            continue
        try:
            if abs(f(float(r))) > 1e-6:
                bad.append((r, _t('не обращает уравнение в ноль',
                                  'does not satisfy the equation')))
        except (ValueError, ZeroDivisionError, OverflowError):
            bad.append((r, _t('уравнение в этой точке не определено',
                              'the equation is undefined there')))
    if bad:
        for r, why in bad:
            print(f"{NO} {label}: {r} — {why}")
        return False

    found = _scan_roots(f, float(a), float(b))
    extra = len(found) - len(given)
    if extra > 0:
        miss = [c for c in found
                if all(abs(c - float(r)) > 1e-4 for r in given)]
        hint = _t(f", первый пропущенный около {miss[0]:.4f}",
                  f", the first one missing is near {miss[0]:.4f}") if miss else ""
        print(f"{NO} {label}: " + _t(
            f"корни верны, но найдено не всё — на отрезке их {len(found)}, "
            f"а у вас {len(given)}{hint}",
            f"the roots you list are correct, but not all of them are "
            f"there — the interval holds {len(found)}, you list "
            f"{len(given)}{hint}"))
        return False
    if len(set(map(str, given))) != len(given):
        print(f"{NO} {label}: " + _t("один и тот же корень указан дважды",
                               "the same root is listed twice"))
        return False
    print(f"{OK} {label}: {{{', '.join(str(r) for r in given)}}}")
    return True


def count_roots(f, a, b, samples=4000):
    """Сколько корней у функции f на [a, b] — численно, сканированием.

    Нужно там, где вопрос звучит как «сколько решений» и ответом является
    множество значений параметра: считать корни приходится в каждой
    пробной точке, и делать это должен не solve, а быстрый скан.
    """
    return len(_scan_roots(f, float(a), float(b), samples))


def _scan_roots(f, a, b, samples=4000):
    """Численно считает корни f на [a, b]: смены знака и касания нуля."""
    step = (b - a) / samples
    pts = []
    for i in range(samples + 1):
        t = a + i * step
        try:
            pts.append((t, f(t)))
        except (ValueError, ZeroDivisionError, OverflowError):
            pts.append((t, None))

    roots = []

    def add(value):
        if all(abs(value - r) > 1e-4 for r in roots):
            roots.append(value)

    for (t0, v0), (t1, v1) in zip(pts, pts[1:]):
        if v0 is None or v1 is None:
            continue
        if v0 == 0:
            add(t0)
        if v0 * v1 < 0:
            # разрыв (полюс тангенса) даёт смену знака без корня
            if abs(v0) > 1e3 and abs(v1) > 1e3:
                continue
            lo, hi = t0, t1
            for _ in range(60):
                mid = (lo + hi) / 2
                try:
                    fm = f(mid)
                except (ValueError, ZeroDivisionError, OverflowError):
                    break
                if f(lo) * fm <= 0:
                    hi = mid
                else:
                    lo = mid
            add((lo + hi) / 2)
    # касания: локальные минимумы |f|, не пойманные сменой знака
    for (t0, v0), (t1, v1), (t2, v2) in zip(pts, pts[1:], pts[2:]):
        if None in (v0, v1, v2):
            continue
        if abs(v1) < 1e-7 and abs(v1) <= abs(v0) and abs(v1) <= abs(v2):
            add(t1)
    if pts[-1][1] is not None and pts[-1][1] == 0:
        add(b)
    return sorted(roots)


def euler(f, x0, y0, h, n):
    """Метод Эйлера: возвращает список (x, y) от начальной точки до шага n."""
    pts = [(x0, y0)]
    xn, yn = x0, y0
    for _ in range(n):
        yn = yn + h * f(xn, yn)
        xn = xn + h
        pts.append((xn, yn))
    return pts


def trigger_check(answers, key):
    """Тренажёр распознавания приёма: answers — {номер: код приёма}."""
    if not any(str(v).strip() for v in answers.values()):
        print("⬜ " + _t("тренажёр: ответы не заполнены",
                         "trainer: no answers yet"))
        return False
    wrong = []
    for i, want in key.items():
        got = str(answers.get(i, "")).strip().lower()
        if digest(got) != want:
            wrong.append(i)
    if not wrong:
        print(f"{OK} " + _t(f"все {len(key)} распознаны",
                      f"all {len(key)} identified"))
        return True
    print(f"{NO} " + _t(
        f"перепроверь пункты: {', '.join(map(str, wrong))} "
        f"(верно {len(key) - len(wrong)} из {len(key)})",
        f"look again at: {', '.join(map(str, wrong))} "
        f"({len(key) - len(wrong)} of {len(key)} correct)"))
    return False
