"""Общее для всех тем: имена ноутбука, язык сообщений, хеш и первые проверки.

Отсюда приходит всё, что ноутбук получает через `from kit import *`, но что
не относится ни к одной теме: sin, pi, sqrt и прочие имена sympy, символы
x, y, t, k, язык проверок, digest и sig. Здесь же проверки первых
практикумов — число по хешу, выражение, комплексное число (A5, A6),
бином (A3), тождество, индукция и делимость (A7), решение дифференциального
уравнения подстановкой (E7) — и тренажёр распознавания приёма.

Каждый модуль пакета начинается с `from .core import *`: эти имена в kit
общие так же, как в ноутбуке.
"""

import cmath
import contextlib
import hashlib
import io
import itertools
import math

import sympy as sp

# Перебор пишется в ноутбуке комбинаторики так же часто, как sin в
# тригонометрии, и по той же причине идёт в общие имена: permutations,
# а не itertools.permutations. Пользуется ими проверка, а не студент —
# перебор ей и заменяет эталон.
from itertools import (                                              # noqa: E402
    permutations, combinations, combinations_with_replacement, product,
)
# Перестановки набора с повторами itertools не умеет: permutations считает
# одинаковые буквы разными и выдаёт 15! кортежей там, где различных узоров
# 630630. Эта — умеет.
from sympy.utilities.iterables import multiset_permutations          # noqa: E402

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

    # Прочие буквы (a в ответе a/(1 - r)^2) заполняются числами, иначе разность
    # не сводится к числу и проверка молча говорит «слишком много особых точек»,
    # то есть отвечает «не знаю» на каждый ответ с параметром.
    spare = sorted(diff.free_symbols - {var}, key=str)
    checked = 0
    for i, s in enumerate(samples):
        fill = {f: sp.Float(_SERIES_FILL[(i + j) % len(_SERIES_FILL)])
                for j, f in enumerate(spare)}
        try:
            val = complex(diff.subs({var: sp.Float(s), **fill}).evalf())
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
