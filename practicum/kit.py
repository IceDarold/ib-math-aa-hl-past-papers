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


# --- асимптоты и множество значений ------------------------------------------
#
# Восьмой раз серии нужно своё понятие равенства ответов. A3 сверял значения,
# A4 — форму записи, A8 — множества, B1 — уравнения, C1 — конфигурацию,
# B2 — функцию по тому, что она отменяет, B3 — картинку по списку особенностей.
#
# Здесь ответ это **прямая**, и она верна не тогда, когда совпала с эталоном,
# а тогда, когда кривая к ней действительно приближается. Поэтому
# verify_asymptotes не сравнивает записи: он берёт вашу прямую и считает
# предел. Вертикальная — односторонний предел бесконечен; горизонтальная —
# предел на бесконечности равен вашему числу; наклонная — предел разности
# f(x) − (mx + b) равен нулю. Это ровно определение асимптоты, и ничего,
# кроме определения, здесь не нужно.
#
# Отсюда и требование записать ответ уравнением. «x = 3» это прямая, «3» это
# число, и markscheme говорит об этом прямым текстом: must be written as an
# equation with y =. Проверка принимает любую запись, которая задаёт прямую,
# и отвергает ту, которая задаёт число.
#
# verify_range устроен как verify_param_set: он ничего не решает за вас, он
# берёт ваше множество и спрашивает у самой функции, достигается ли значение.
# Внутри — должно достигаться, снаружи — не должно, и отдельно проверяется
# каждый конец: именно там стоит разница между ≤ и <, а вместе с ней балл.

_ASYMPTOTE_KINDS = ('vertical', 'horizontal', 'oblique')

def _kind_name(kind):
    """Название вида асимптоты на языке сообщений."""
    if kind == 'vertical':
        return _t("вертикальная", "vertical")
    if kind == 'horizontal':
        return _t("горизонтальная", "horizontal")
    return _t("наклонная", "oblique")


def _as_line(item, var, dep):
    """Ответ-прямая → (вид, значение) или None.

    Принимаются Eq(x, 3), Eq(2*x + 6, 0), Eq(y, 2), Eq(y, x/2 + 13/4) и любая
    равносильная запись. Голое число не принимается: это не прямая.
    """
    try:
        e = sp.sympify(item)
    except (TypeError, ValueError, sp.SympifyError):
        return None
    if isinstance(e, sp.Eq):
        expr = e.lhs - e.rhs
    elif isinstance(e, sp.core.relational.Relational):
        return None
    else:
        return None

    free = expr.free_symbols
    if dep in free:
        try:
            sols = sp.solve(sp.Eq(expr, 0), dep)
        except (NotImplementedError, TypeError, ValueError):
            return None
        if len(sols) != 1:
            return None
        line = sp.expand(sols[0])
        if dep in line.free_symbols or not (line.free_symbols <= {var}):
            return None
        slope = sp.simplify(sp.diff(line, var))
        if slope.free_symbols or not slope.is_number:
            return None
        if sp.simplify(line - (slope * var + line.subs(var, 0))) != 0:
            return None          # не прямая: x^2, 1/x и прочее
        return ('horizontal' if slope == 0 else 'oblique', sp.simplify(line))

    if var in free:
        try:
            sols = sp.solve(sp.Eq(expr, 0), var)
        except (NotImplementedError, TypeError, ValueError):
            return None
        if len(sols) != 1:
            return None
        value = sp.simplify(sols[0])
        return None if value.free_symbols else ('vertical', value)
    return None


def _show_line(kind, value, var, dep):
    return (f"{var} = {value}" if kind == 'vertical' else f"{dep} = {value}")


def _asymptote_truth(fun, var, region):
    """Все асимптоты функции, посчитанные по определению."""
    found = {k: [] for k in _ASYMPTOTE_KINDS}

    try:
        sing = sp.singularities(fun, var)
        if not isinstance(sing, sp.FiniteSet):
            sing = sing.intersect(region.closure)
        candidates = list(sing.args) if isinstance(sing, sp.FiniteSet) else []
    except (NotImplementedError, TypeError, ValueError, AttributeError):
        candidates = []
    lo, hi = _bounds(region)
    for end in (lo, hi):
        if end not in (sp.oo, -sp.oo) and end not in candidates:
            candidates.append(end)
    for c in candidates:
        if c.free_symbols or c not in region.closure:
            continue
        for side in ('+', '-'):
            try:
                lim = sp.limit(fun, var, c, side)
            except (NotImplementedError, ValueError, TypeError):
                continue
            if lim in (sp.oo, -sp.oo, sp.zoo):
                found['vertical'].append(sp.simplify(c))
                break

    for end in (hi, lo):
        if end not in (sp.oo, -sp.oo):
            continue
        try:
            lim = sp.limit(fun, var, end)
        except (NotImplementedError, ValueError, TypeError):
            continue
        if lim.is_finite:
            value = sp.simplify(lim)
            if all(sp.simplify(value - h) != 0 for h in found['horizontal']):
                found['horizontal'].append(value)
            continue
        try:
            m = sp.limit(fun / var, var, end)
            if not (m.is_finite and m != 0):
                continue
            b = sp.limit(fun - m * var, var, end)
        except (NotImplementedError, ValueError, TypeError):
            continue
        if b.is_finite:
            line = sp.simplify(m * var + b)
            if all(sp.simplify(line - o) != 0 for o in found['oblique']):
                found['oblique'].append(line)
    return found


def _approaches(fun, var, kind, value, region):
    """Проверяет по определению, что кривая приближается к этой прямой."""
    if kind == 'vertical':
        if value not in region.closure:
            return False
        for side in ('+', '-'):
            try:
                lim = sp.limit(fun, var, value, side)
            except (NotImplementedError, ValueError, TypeError):
                continue
            if lim in (sp.oo, -sp.oo, sp.zoo):
                return True
        return False
    lo, hi = _bounds(region)
    for end in (hi, lo):
        if end not in (sp.oo, -sp.oo):
            continue
        try:
            gap = sp.limit(fun - value, var, end)
        except (NotImplementedError, ValueError, TypeError):
            continue
        if gap == 0:
            return True
    return False


def verify_asymptotes(label, got, f, var=x, dep=y, kinds=_ASYMPTOTE_KINDS,
                      domain=None):
    """Асимптоты графика. Эталона нет: каждая прямая проверяется пределом.

    got — уравнение прямой или список уравнений: Eq(x, 3), Eq(y, 2),
    Eq(y, x/2 + Rational(13, 4)). Принимается любая равносильная запись,
    включая Eq(2*x + 6, 0). Не принимается число: асимптота это прямая,
    и markscheme пишет «must be written as an equation with y =».

    kinds сужает вопрос: kinds=('vertical',) для «state the equation of the
    vertical asymptote». Тогда прямые других видов считаются лишними,
    а недостающие других видов не требуются.

    Проверка идёт по определению, а не по списку. Вертикальная прямая x = c
    верна, если односторонний предел в c бесконечен; горизонтальная y = h —
    если предел на бесконечности равен h; наклонная y = mx + b — если предел
    разности f(x) − (mx + b) равен нулю. Полнота проверяется отдельно:
    пропущенная асимптота и лишняя — разные ошибки и разные баллы.
    """
    if _blank(label, got):
        return False
    if not isinstance(got, (list, tuple, set)):
        got = [got]
    bad = [k for k in kinds if k not in _ASYMPTOTE_KINDS]
    if bad:
        raise ValueError(f"verify_asymptotes: unknown kind {bad[0]}")

    fun = sp.sympify(f)
    region = _as_domain(domain, var)

    claimed = {k: [] for k in _ASYMPTOTE_KINDS}
    for item in got:
        line = _as_line(item, var, dep)
        if line is None:
            print(f"{NO} {label}: " + _t(
                f"{item} — это не уравнение прямой. Асимптота записывается "
                f"уравнением: Eq({var}, 3), Eq({dep}, 2), "
                f"Eq({dep}, {var}/2 + Rational(13, 4))",
                f"{item} is not the equation of a line. An asymptote is "
                f"written as an equation: Eq({var}, 3), Eq({dep}, 2), "
                f"Eq({dep}, {var}/2 + Rational(13, 4))"))
            return False
        kind, value = line
        if kind not in kinds:
            asked = ', '.join(_kind_name(k) for k in kinds)
            print(f"{NO} {label}: {_show_line(kind, value, var, dep)} — " + _t(
                f"{_kind_name(kind)} прямая, а спрашивают только: {asked}",
                f"a {_kind_name(kind)} line, but the question asks "
                f"only for: {asked}"))
            return False
        if not _approaches(fun, var, kind, value, region):
            print(f"{NO} {label}: " + _t(
                f"к прямой {_show_line(kind, value, var, dep)} график "
                f"не приближается",
                f"the graph does not approach the line "
                f"{_show_line(kind, value, var, dep)}"))
            return False
        claimed[kind].append(value)

    truth = _asymptote_truth(fun, var, region)
    for kind in kinds:
        for value in truth[kind]:
            if all(sp.simplify(value - c) != 0 for c in claimed[kind]):
                print(f"{NO} {label}: " + _t(
                    f"пропущена {_kind_name(kind)} асимптота "
                    f"{_show_line(kind, value, var, dep)}",
                    f"a {_kind_name(kind)} asymptote is missing: "
                    f"{_show_line(kind, value, var, dep)}"))
                return False

    shown = ', '.join(_show_line(k, v, var, dep)
                      for k in _ASYMPTOTE_KINDS for v in claimed[k])
    print(f"{OK} {label}: {shown}")
    return True


def _show_value(value):
    """Точное значение, а рядом десятичное, если по точному не видно, где оно."""
    if value.is_Integer:
        return str(value)
    return f"{value} ({float(value):.6g})"


def _attained(fun, var, region, value, window=60):
    """Достигается ли значение: True, False или None, если судить нельзя."""
    eq = sp.simplify(fun - value)
    try:
        sols = sp.solveset(sp.Eq(eq, 0), var, region)
    except (NotImplementedError, TypeError, ValueError):
        sols = sp.ConditionSet(var, sp.Eq(eq, 0), region)
    if not isinstance(sols, sp.ConditionSet):
        if sols is sp.S.EmptySet:
            return False
        return not sols.is_empty if sols.is_empty is not None else True

    lo, hi = _bounds(region)
    lo_f = -float(window) if lo == -sp.oo else float(lo)
    hi_f = float(window) if hi == sp.oo else float(hi)
    try:
        g = sp.lambdify(var, eq, 'math')
    except (TypeError, ValueError):
        return None
    return True if _scan_roots(g, lo_f, hi_f, 8000) else None


def verify_range(label, got, f, var=x, domain=None, dep=y,
                 eps=sp.Rational(1, 1000)):
    """Множество значений функции. Проверка ничего не решает за вас.

    Она берёт ваше множество и спрашивает у самой f: внутри — достигается ли
    значение, снаружи — не достигается ли. Отдельно проверяется каждый
    конец, потому что там стоит разница между ≤ и <: у −3/2 < y ≤ 2 двойка
    достигается при x = 0, а −3/2 это горизонтальная асимптота, и её
    не достигает никто.

    got — множество или неравенство: Interval(-5, oo), (y >= -5),
    Union(Interval(-oo, 1), Interval(2, oo)).
    """
    if _blank(label, got):
        return False
    mine = _as_set(got, dep)
    if mine is None:
        mine = _as_set(got, var)
    if mine is None:
        print(f"{NO} {label}: " + _t(
            "ответ должен быть множеством или неравенством — "
            "Interval(-5, oo), (y >= -5), Union(...)",
            "the answer must be a set or an inequality — "
            "Interval(-5, oo), (y >= -5), Union(...)"))
        return False

    fun = sp.sympify(f)
    region = _as_domain(domain, var)
    outside = sp.Complement(sp.S.Reals, mine)

    tests = []
    for source, want in ((mine, True), (outside, False)):
        pieces = _pieces(source)
        if pieces is None:
            print(f"{NO} {label}: " + _t(
                "такое множество проверка разобрать не умеет",
                "the check cannot take this set apart"))
            return False
        for a, b, _, _ in pieces:
            tests.extend((p, want) for p in _interior(a, b))
            # Каждая граница проверяется трижды: сама точка и по шагу eps
            # в обе стороны. Без соседей ошибка в границе проходит: если
            # истинный ответ y >= -5, а написано y >= -4, то внутренние
            # точки промежутка (-oo, -4) берутся далеко слева и о полоске
            # между -5 и -4 ничего не говорят.
            for end in (a, b):
                if not end.is_finite:
                    continue
                tests.append((end, end in mine))
                for near in (end - eps, end + eps):
                    tests.append((near, near in mine))

    skipped = 0
    seen = []
    for value, want in tests:
        if any(sp.simplify(value - other) == 0 for other in seen):
            continue
        seen.append(value)
        verdict = _attained(fun, var, region, value)
        if verdict is None:
            skipped += 1
            continue
        if verdict == want:
            continue
        if want:
            print(f"{NO} {label}: " + _t(
                f"{dep} = {_show_value(value)} входит в ваш ответ, "
                f"но уравнение f({var}) = {value} решений не имеет",
                f"{dep} = {_show_value(value)} is in your range, but the "
                f"equation f({var}) = {value} has no solution"))
        else:
            print(f"{NO} {label}: " + _t(
                f"значение {dep} = {_show_value(value)} функция принимает, "
                f"а в вашем множестве его нет",
                f"the function does take the value {dep} = {_show_value(value)}, "
                f"and your set leaves it out"))
        return False

    tail = ''
    if skipped:
        tail = _t(f"; {skipped} точек пропущено — численно не решить",
                  f"; {skipped} points skipped — numerically undecidable")
    print(f"{OK} {label}: {_show_set(mine, dep)}{tail}")
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

    tol — с какой невязкой корень считается корнем. По умолчанию 1e-6:
    корни тригонометрических уравнений пишут точными, и подстановка
    обязана давать ноль. Но там, где бумага сама просит три значащие
    цифры, такое число уравнению точно не удовлетворяет никогда, и
    требовать от него нуля значило бы отвергать ответ за то, что его
    округлили так, как велено. Тогда допуск задают явно, и он читается
    как «настолько мимо, насколько разрешает округление»: у θ = 2 sin θ
    производная около корня равна 1.64, и невязка 1e-2 — это ±0.006
    по самому углу.
    """
    if _blank(label, roots):
        return False
    residual = max(tol, 1e-6)
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
            if abs(f(float(r))) > residual:
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


def verify_model(label, got, data, var=t, sf=6, tol=None):
    """Ответ — сама модель: выражение с подставленными постоянными.

    Девятое понятие равенства ответов в серии. Модель верна не тогда, когда
    её постоянные совпали с эталонными, а тогда, когда она воспроизводит те
    данные, из которых её строили. Поэтому эталона здесь нет вовсе: каждая
    пара (вход, выход) из условия подставляется в вашу модель, и требуется
    совпадение до sf значащих цифр.

    data — список пар (t, значение) из самого условия. Значение None
    означает «здесь ничего не проверяем» и такую пару пропускает.

    По умолчанию сверка идёт до шести значащих цифр, а не до трёх: данные
    в условии точны («15000 человек», «через 8 лет на 11% меньше»), и
    трёх цифр хватило бы, чтобы принять модель, ошибающуюся на полторы
    сотни человек. Округлённое значение подаётся с явным sf.

    Ловит ровно то, на чём в этой теме теряют баллы: постоянные найдены
    верно, но отсчёт времени сдвинут (t = 27, а не t = 19), или k взято
    положительным при убывании.
    """
    if _blank(label, got, *[p for pair in data for p in pair]):
        return False
    expr = sp.sympify(got)
    free = expr.free_symbols - {var}
    if free:
        print(f"{NO} {label}: " + _t(
            f"в модели остались неизвестные постоянные: "
            f"{', '.join(sorted(map(str, free)))}",
            f"the model still has unknown constants in it: "
            f"{', '.join(sorted(map(str, free)))}"))
        return False
    bad = []
    for point, want in data:
        if want is None:
            continue
        try:
            value = complex(expr.subs(var, sp.sympify(point)).evalf())
        except (TypeError, ValueError):
            bad.append((point, _t('модель здесь не вычисляется',
                                  'the model does not evaluate there')))
            continue
        if abs(value.imag) > 1e-9:
            bad.append((point, _t('модель здесь не действительна',
                                  'the model is not real there')))
            continue
        got_v, want_v = value.real, float(sp.sympify(want))
        span = tol if tol is not None else abs(want_v) * 10.0 ** (1 - sf) + 1e-9
        if abs(got_v - want_v) > span:
            bad.append((point, _t(
                f'модель даёт {sig(got_v, sf)}, а по условию {sig(want_v, sf)}',
                f'the model gives {sig(got_v, sf)}, the question says '
                f'{sig(want_v, sf)}')))
    if bad:
        for point, why in bad:
            print(f"{NO} {label}: " + _t(f"при {var} = {point} ", f"at {var} = {point} ")
                  + why)
        return False
    print(f"{OK} {label}: {expr}")
    return True


def verify_in_terms_of(label, got, want, subs, tol=1e-9):
    """Ответ «в терминах p и q»: выражение через данные буквы.

    Проверяется двумя условиями сразу. Во-первых, в ответе не должно быть
    ничего, кроме разрешённых букв: log 24 переписанное само через себя —
    не ответ, а вопрос. Во-вторых, после подстановки истинных значений букв
    ответ обязан численно совпасть с тем, что просили выразить.

    subs — словарь {буква: её истинное значение}.
    """
    if _blank(label, got):
        return False
    expr = sp.sympify(got)
    allowed = {sp.sympify(s) for s in subs}
    extra = expr.free_symbols - allowed
    if extra:
        print(f"{NO} {label}: " + _t(
            f"ответ должен быть выражен только через "
            f"{', '.join(sorted(map(str, allowed)))}, а здесь ещё "
            f"{', '.join(sorted(map(str, extra)))}",
            f"the answer must be written using only "
            f"{', '.join(sorted(map(str, allowed)))}, but it also has "
            f"{', '.join(sorted(map(str, extra)))} in it"))
        return False
    if not expr.has(*allowed):
        print(f"{NO} {label}: " + _t(
            "в ответе нет ни одной из данных букв: вопрос просит выразить "
            "через них, а не переписать сам себя",
            "the answer uses none of the given letters: the question asks "
            "for the value in terms of them, not for a rewrite of itself"))
        return False
    value = expr.subs({sp.sympify(s): sp.sympify(v) for s, v in subs.items()})
    if abs(complex(sp.sympify(value - sp.sympify(want)).evalf())) > tol:
        print(f"{NO} {label}: {expr} — " + _t("не сходится", "no match"))
        return False
    print(f"{OK} {label}: {expr}")
    return True


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


# --------------------------------------------------------------- вероятность
#
# Тринадцатое понятие равенства ответов, и первое, где ответ — просто число
# от нуля до единицы. Сверять такое с записанным эталоном было бы ровно тем,
# чего практикумы избегают, и проверять здесь надо не число, а то, откуда оно
# берётся: вопрос о вероятности задаёт **пространство**, а пространство
# определяет ответ однозначно.
#
# Условия вопроса — «P(A) = 0,65», «P(A|B) = 1/4», «A и B независимы» — это
# уравнения на веса исходов. Проверка решает их и вычисляет то, о чём
# спрашивают, по определению. Ни верного ответа, ни неверных она не хранит:
# и те, и другие выводятся из условия.


class _Event:
    """Событие — множество атомов пространства.

    Атом это одна клетка диаграммы Венна: у двух событий их четыре
    (A∩B, A∩B′, A′∩B, A′∩B′), у трёх восемь. Любое событие, какое можно
    записать через A и B, есть объединение атомов, поэтому пересечение,
    объединение и дополнение — операции над множествами индексов, и
    алгебру событий писать не приходится.

    Кроме самих атомов событие помнит, как оно составлено (`op`, `parts`).
    Это нужно не для вычисления, а для разбора неверного ответа: «в объединении
    пересечение посчитано дважды» — промах с именем, и назвать его можно
    только зная, что спрашивали именно про объединение.
    """

    def __init__(self, space, atoms, name, op='atom', parts=()):
        self.space = space
        self.atoms = frozenset(atoms)
        self.name = name
        self.op = op
        self.parts = tuple(parts)

    def __and__(self, other):
        return _Event(self.space, self.atoms & other.atoms,
                      f"{self.name} ∩ {other.name}", 'and', (self, other))

    def __or__(self, other):
        return _Event(self.space, self.atoms | other.atoms,
                      f"{self.name} ∪ {other.name}", 'or', (self, other))

    def __invert__(self):
        return _Event(self.space, self.space.all - self.atoms,
                      f"{self.name}′", 'not', (self,))

    def __repr__(self):
        return self.name


class _Space:
    """Пространство из n событий: 2**n атомов с неизвестными весами."""

    def __init__(self, names):
        self.names = list(names)
        self.size = 2 ** len(self.names)
        self.all = frozenset(range(self.size))
        self.weights = list(sp.symbols(f'w0:{self.size}'))

    def atom_of(self, index, name):
        """Событие номер index: атомы, в двоичном номере которых стоит его бит."""
        inside = [j for j in range(self.size) if (j >> index) & 1]
        return _Event(self, inside, name)

    def mass(self, event):
        return sp.Add(*[self.weights[j] for j in sorted(event.atoms)])


def events(names):
    """События пространства: `A, B = events('A B')`.

    Дальше их пишут так, как пишет экзамен: `A & B` — пересечение,
    `A | B` — объединение, `~A` — дополнение, `P(A, given=B)` — условная
    вероятность. Чему равны эти вероятности, проверка не знает; она узнаёт
    это из условий самого вопроса.
    """
    space = _Space(names.split())
    made = [space.atom_of(i, nm) for i, nm in enumerate(space.names)]
    return made[0] if len(made) == 1 else made


class _Prob:
    """P(...) — выражение через веса атомов, помнящее, о чём спросили.

    Помнить нужно ради разбора неверного ответа. Перепутанный порядок
    в P(A|B) — промах с именем, и назвать его можно, только зная, что
    спрашивали условную вероятность, а не какое-то число вообще.

    Арифметика возвращает обычные выражения sympy, поэтому условия вида
    `P(A) = 3*P(B)` пишутся так, как они напечатаны в билете.
    """

    def __init__(self, expr, kind, args, label):
        self.expr, self.kind, self.args, self.label = expr, kind, args, label

    def _sympy_(self):
        return self.expr

    def __add__(self, other):
        return self.expr + sp.sympify(other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.expr - sp.sympify(other)

    def __rsub__(self, other):
        return sp.sympify(other) - self.expr

    def __mul__(self, other):
        return self.expr * sp.sympify(other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self.expr / sp.sympify(other)

    def __rtruediv__(self, other):
        return sp.sympify(other) / self.expr

    def __neg__(self):
        return -self.expr

    def __repr__(self):
        return self.label


def P(event, given=None):
    """Вероятность события; `given=` делает её условной.

    `P(A & B)` — вероятность пересечения, `P(A | B)` — объединения,
    `P(A, given=B)` — то, что экзамен пишет как P(A|B). Разделение
    намеренное: вертикальная черта в Python значит объединение, и
    занимать её под условную вероятность значило бы завести запись,
    которую нельзя прочесть вслух так, как она напечатана.
    """
    space = event.space
    if given is None:
        return _Prob(space.mass(event), 'plain', (event,), f"P({event})")
    joint = space.mass(event & given)
    return _Prob(joint / space.mass(given), 'given', (event, given),
                 f"P({event} | {given})")


def _as_equation(item):
    """Условие вопроса → уравнение. Пара (что, чему равно) или готовое Eq."""
    if isinstance(item, (tuple, list)):
        left, right = item
        return sp.Eq(sp.sympify(left), sp.sympify(right))
    if isinstance(item, sp.Equality):
        return item
    return sp.Eq(sp.sympify(item), 0)


_PROB_TOL = 1e-9


def _feasible(run):
    """Веса атомов годятся: все действительны и лежат в [0, 1]."""
    for value in run.values():
        try:
            number = complex(sp.N(value, 30))
        except (TypeError, ValueError):
            return False
        if abs(number.imag) > _PROB_TOL:
            return False
        if number.real < -_PROB_TOL or number.real > 1 + _PROB_TOL:
            return False
    return True


def _solve_space(space, given):
    """Веса атомов из условий вопроса. Возвращает все допустимые решения.

    Условий бывает меньше, чем атомов, и часть весов остаётся буквой.
    Это не значит, что вопрос плох: у мая 2025 TZ2 даны P(A∪B) и P(A∩B′),
    и четвёртая клетка диаграммы действительно не определена — а P(B),
    о котором спрашивают, определено, потому что от неё не зависит.
    Поэтому решение возвращается как есть, а определённость проверяется
    у самого ответа, а не у пространства.
    """
    equations = [sp.Eq(sp.Add(*space.weights), 1)]
    equations += [_as_equation(item) for item in given]
    try:
        found = sp.solve(equations, space.weights, dict=True)
    except (NotImplementedError, TypeError):
        found = []
    runs = []
    for solution in found:
        run = {w: sp.simplify(solution.get(w, w)) for w in space.weights}
        fixed = {w: v for w, v in run.items()
                 if not (v.free_symbols & set(space.weights))}
        if _feasible(fixed):
            runs.append(run)
    return runs


def _value(expr, run):
    return sp.simplify(sp.sympify(expr).subs(run))


def _same_number(one, two, tol=5e-4):
    """Числа сходятся. Допуск — три значащие цифры, как их принимает экзамен."""
    try:
        left, right = complex(sp.N(one, 30)), complex(sp.N(two, 30))
    except (TypeError, ValueError):
        return False
    if abs(left.imag) > _PROB_TOL or abs(right.imag) > _PROB_TOL:
        return False
    scale = max(1.0, abs(right.real))
    return abs(left.real - right.real) <= tol * scale


def _prob_slips(find, run):
    """Типовые промахи, собранные из самого вопроса, а не из списка.

    Каждый строится тем же определением, применённым не так, как оно
    устроено: условная вероятность в обратную сторону, объединение без
    вычитания пересечения, пересечение как произведение там, где
    независимости никто не обещал.
    """
    slips = {}
    if not isinstance(find, _Prob):
        return slips

    if find.kind == 'given':
        target, condition = find.args
        slips[_t("условная вероятность взята в обратную сторону: "
                 "посчитано P(условие | событие)",
                 "the conditional is the wrong way round: "
                 "that is P(condition | event)")] = \
            _value(P(condition, given=target), run)
        slips[_t("это вероятность пересечения — делить на вероятность "
                 "условия ещё не стали",
                 "that is the intersection: it has not been divided by "
                 "the probability of the condition")] = \
            _value(P(target & condition), run)
    else:
        event, = find.args
        if event.op == 'and':
            left, right = event.parts
            slips[_t("вероятности перемножены, а независимость в условии "
                     "не обещана",
                     "the probabilities are multiplied, but the question "
                     "never promised independence")] = \
                _value(sp.sympify(P(left)) * sp.sympify(P(right)), run)
        if event.op == 'or':
            left, right = event.parts
            slips[_t("пересечение посчитано дважды: из суммы его надо вычесть",
                     "the intersection is counted twice: the sum has to "
                     "lose it once")] = \
                _value(sp.sympify(P(left)) + sp.sympify(P(right)), run)

    slips[_t("это вероятность противоположного события",
             "that is the probability of the opposite event")] = \
        _value(1 - sp.sympify(find), run)
    # промах, который сам остался с неизвестным весом, назвать нельзя
    return {what: value for what, value in slips.items()
            if not value.free_symbols}


def _report_probability(label, got, want, slips):
    """Общий разбор ответа-вероятности: сошлось, или как именно не сошлось."""
    try:
        answer = sp.sympify(got)
    except (sp.SympifyError, TypeError):
        print(f"{NO} {label}: " + _t("ответ не разобран как число",
                                     "the answer is not a number"))
        return False
    number = complex(sp.N(answer, 30))
    if abs(number.imag) > _PROB_TOL or not -_PROB_TOL <= number.real <= 1 + _PROB_TOL:
        print(f"{NO} {label}: " + _t(
            "вероятность не бывает меньше нуля или больше единицы",
            "a probability is never below zero or above one"))
        return False
    if _same_number(answer, want):
        print(f"{OK} {label}")
        return True
    for what, value in slips.items():
        if value is not None and _same_number(answer, value):
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t(
        "не совпадает с тем, что даёт пространство из условия",
        "that is not what the space in the question gives"))
    return False


def _polytope_extreme(space, given, target, which):
    """Крайнее значение линейной величины на множестве допустимых весов.

    Условий здесь меньше, чем весов, и пространство определено не
    однозначно — вопрос ставится именно так: «наименьшее возможное
    значение P(A∩B)». Множество допустимых весов это выпуклый многогранник
    (сумма единица, равенства вопроса, каждый вес неотрицателен), а
    крайние значения линейной величины на многограннике достигаются
    в вершинах. Вершины перебираются честно: занулить подходящее число
    весов и решить оставшуюся линейную систему.
    """
    weights = space.weights
    base = [sp.Eq(sp.Add(*weights), 1)] + [_as_equation(item) for item in given]
    best = None
    free = len(weights) - len(base)
    free = max(free, 0)
    for zeros in itertools.combinations(range(len(weights)), free):
        system = base + [sp.Eq(weights[j], 0) for j in zeros]
        try:
            solution = sp.solve(system, weights, dict=True)
        except (NotImplementedError, TypeError):
            continue
        for one in solution:
            run = {w: sp.simplify(one.get(w, w)) for w in weights}
            if any(run[w].free_symbols & set(weights) for w in weights):
                continue
            if not _feasible(run):
                continue
            here = _value(target, run)
            if best is None:
                best = here
            elif which == 'min' and sp.N(here) < sp.N(best):
                best = here
            elif which == 'max' and sp.N(here) > sp.N(best):
                best = here
    return best


def verify_event(label, got, given, find, extreme=None):
    """Ответ — вероятность, а пространство задано условиями вопроса.

    `given` перечисляет то, что сказано в билете: пары (что, чему равно)
    или готовые равенства вроде `Eq(P(A & B), P(A)*P(B))` для независимости.
    Проверка решает эти условия как уравнения на веса атомов и вычисляет
    `find` по определению — эталона она не хранит.

    Когда ответ неверен, проверка не ограничивается словом «неверно». Она
    строит из того же пространства именные промахи темы — условная
    вероятность в обратную сторону, объединение без вычитания пересечения,
    независимость там, где её не обещали, — и, если написанное совпало
    с одним из них, называет его.

    `extreme='min'` или `'max'` — для вопросов, где условий заведомо мало
    и спрашивают крайнее возможное значение.
    """
    if _blank(label, got):
        return False
    space = find.args[0].space if isinstance(find, _Prob) else None
    if space is None:
        print(f"{NO} {label}: " + _t("нечего искать", "nothing to find"))
        return False

    if extreme is not None:
        want = _polytope_extreme(space, given, sp.sympify(find), extreme)
        if want is None:
            print(f"{NO} {label}: " + _t(
                "условия вопроса не дают ни одного допустимого пространства",
                "the conditions allow no valid space at all"))
            return False
        return _report_probability(label, got, want, {})

    runs = _solve_space(space, given)
    if not runs:
        print(f"{NO} {label}: " + _t(
            "условия вопроса не дают ни одного допустимого пространства",
            "the conditions allow no valid space at all"))
        return False
    wants = [_value(find, run) for run in runs]
    loose = [w for w in wants if w.free_symbols & set(space.weights)]
    if loose or (len(wants) > 1
                 and not all(_same_number(w, wants[0]) for w in wants[1:])):
        print(f"{NO} {label}: " + _t(
            "условий не хватает: они допускают разные ответы",
            "the conditions are not enough: they allow different answers"))
        return False
    return _report_probability(label, got, wants[0], _prob_slips(find, runs[0]))


def verify_independence(label, got, given, a, b):
    """Ответ — два числа, которые сравнивают, решая вопрос о независимости.

    Вердикт «зависимы» или «независимы» сам по себе — монета: угадать его
    можно и не считая. Схема оценивания и не даёт за него балла отдельно:
    R-балл зависит от предыдущего, а предыдущий стоит на вычислении
    P(A)·P(B) и P(A∩B). Поэтому в ячейке пишут именно эти два числа,
    в этом порядке, а вывод из них следует сам.
    """
    if _blank(label, got):
        return False
    if not isinstance(got, (list, tuple)) or len(got) != 2:
        print(f"{NO} {label}: " + _t(
            "нужны два числа: произведение P(A)·P(B) и вероятность P(A∩B)",
            "two numbers are wanted: the product P(A)·P(B) and P(A∩B)"))
        return False
    space = a.space
    runs = _solve_space(space, given)
    if not runs:
        print(f"{NO} {label}: " + _t(
            "условия вопроса не дают ни одного допустимого пространства",
            "the conditions allow no valid space at all"))
        return False
    run = runs[0]
    product = _value(sp.sympify(P(a)) * sp.sympify(P(b)), run)
    joint = _value(P(a & b), run)
    if not _same_number(got[0], product):
        print(f"{NO} {label}: " + _t(
            "первое число — не произведение P(A)·P(B)",
            "the first number is not the product P(A)·P(B)"))
        return False
    if not _same_number(got[1], joint):
        print(f"{NO} {label}: " + _t(
            "второе число — не вероятность пересечения P(A∩B)",
            "the second number is not the intersection P(A∩B)"))
        return False
    verdict = _t("независимы", "independent") if _same_number(product, joint) \
        else _t("зависимы", "not independent")
    print(f"{OK} {label}: " + _t(f"числа верны, и они говорят: {verdict}",
                                 f"both numbers are right, and they say: {verdict}"))
    return True


def verify_probability(label, got, space, find, given=None, total=1):
    """Ответ — вероятность, а пространство выписано исходами и весами.

    Там, где событий два или три, пространство восстанавливается из условий
    (`verify_event`). Там, где вопрос про дерево, про последовательные
    вынимания без возвращения или про равновозможные наборы, исходы проще
    перечислить: `space` — это словарь «исход → вес». Проверка складывает
    веса нужных исходов, а не сверяет число с эталоном, и первым делом
    проверяет, что все веса вместе дают единицу: неверно переписанное
    дерево ловится именно здесь.

    `find` и `given` — либо предикат на исходе, либо набор исходов.
    """
    if _blank(label, got):
        return False
    weights = {key: sp.sympify(w) for key, w in space.items()}
    whole = sp.simplify(sp.Add(*weights.values()))
    if sp.simplify(whole - total) != 0:
        print(f"{NO} {label}: " + _t(
            f"веса исходов дают {whole}, а не {total} — пространство выписано неверно",
            f"the outcomes weigh {whole}, not {total} — the space is wrong"))
        return False

    def pick(rule):
        if rule is None:
            return set(weights)
        if callable(rule):
            return {key for key in weights if rule(key)}
        return {key for key in weights if key in set(rule)}

    inside, condition = pick(find), pick(given)
    hit = sp.simplify(sp.Add(*[weights[k] for k in inside & condition]) or 0)
    base = sp.simplify(sp.Add(*[weights[k] for k in condition]) or 0)
    if base == 0:
        print(f"{NO} {label}: " + _t("условие невозможно",
                                     "the condition cannot happen"))
        return False
    want = sp.simplify(hit / base)

    slips = {}
    if given is not None:
        back = sp.Add(*[weights[k] for k in inside]) or 0
        slips[_t("условная вероятность взята в обратную сторону",
                 "the conditional is the wrong way round")] = \
            sp.simplify(hit / back) if back != 0 else None
        slips[_t("это вероятность пересечения — делить на вероятность "
                 "условия ещё не стали",
                 "that is the intersection: it has not been divided by "
                 "the probability of the condition")] = hit
    slips[_t("это вероятность противоположного события",
             "that is the probability of the opposite event")] = 1 - want
    return _report_probability(label, got, want, slips)


# ------------------------------------------------------------------- счёт
#
# Четырнадцатое понятие равенства ответов, и второе подряд, где ответ —
# просто число. У вероятности это было число между нулём и единицей, и
# проверялось оно устройством пространства. У счёта это целое число, и
# проверяется оно тем же самым, доведённым до конца: **объекты
# пересчитываются**.
#
# Эталона снова нет. Ноутбук передаёт проверке не ответ, а описание того,
# что считают: как выглядит объект и что значит «подходит». Проверка
# перебирает и считает сама. Совпало — значит, одно и то же число получено
# двумя разными путями: формулой у студента и перебором у проверки, а
# формулу перебор не знает.
#
# Перебор влезает не всегда: 15! — это 1,3·10¹², и столько объектов не
# переберёт никакой ноутбук. Тогда перечисляются не все объекты, а те, о
# ком идёт речь: в вопросе про десятерых детей за десятью партами
# ограничение касается четверых, и перебираются 5040 способов посадить
# этих четверых, а остальные шестеро дают множитель 6!. Ход тот же, каким
# считает экзаменуемый, но стоит он в проверке, а не в ответе, и на ответ
# не намекает — `each` в подписи не виден.

# Множитель 2! разобран отдельной парой сообщений ниже — про порядок
# внутри пары, — поэтому здесь двойка лишняя: до неё бы не дошло.
_COUNT_FACTORS = tuple(range(3, 11))


def _as_count(value):
    """Ответ-счёт как целое число, или None, если это не целое число."""
    try:
        number = sp.nsimplify(sp.sympify(value))
    except (sp.SympifyError, TypeError, AttributeError):
        return None
    if getattr(number, 'free_symbols', set()):
        return None
    if not number.is_number or not number.is_real:
        return None
    return int(number) if sp.Integer(int(number)) == number else None


def _count_slips(total, matched, each):
    """Типовые промахи, собранные из самого перебора, а не из списка.

    Каждый — то же множество, посчитанное не так, как просили: без
    ограничения, ровно наоборот, без множителя за неупомянутых.
    """
    want = matched * each
    slips = {}
    if matched != total:
        slips[_t("ограничение из условия не учтено: это все объекты подряд",
                 "the restriction is missing: that is every object there is")] \
            = total * each
        slips[_t("посчитано ровно то, что условие запрещает",
                 "that is the count of exactly what the question forbids")] \
            = (total - matched) * each
    if each != 1:
        slips[_t("остальные ещё не расставлены: не хватает множителя",
                 "the others have not been arranged yet: a factor is missing")] \
            = matched
    slips[_t("каждый набор посчитан дважды: порядок внутри пары "
             "здесь не различают",
             "every selection is counted twice: the order inside the pair "
             "does not count here")] = want * 2
    if want % 2 == 0:
        slips[_t("порядок внутри пары не посчитан: её можно поставить "
                 "двумя способами",
                 "the order inside the pair is missing: it can go two ways")] \
            = want // 2
    for size in _COUNT_FACTORS:
        step = sp.factorial(size)
        if want % step == 0:
            slips[_t(f"ответ меньше верного в {size}! раз: где-то потерян "
                     f"порядок внутри {size} объектов",
                     f"the answer is {size}! times too small: the order "
                     f"inside {size} objects has been dropped")] \
                = want // step
        slips[_t(f"ответ больше верного в {size}! раз: где-то посчитан "
                 f"порядок, которого в вопросе нет",
                 f"the answer is {size}! times too large: an order the "
                 f"question does not ask for has been counted")] \
            = want * step
    return slips


def verify_count(label, got, objects, keep=None, each=1):
    """Ответ — сколько объектов, и он проверяется их пересчётом.

    `objects` — то, что перебирают: любой итератор объектов или просто
    их число, когда перебирать нечего. `keep` — что значит «подходит»:
    предикат на объекте. `each` — сколько штук стоит за одним
    перечисленным объектом; он нужен там, где перебирать всё физически
    нельзя, и перечисляют только то, чего касается ограничение.

    Эталон здесь не хранится и не может: проверка складывает единицы,
    а не сверяет число с записанным.
    """
    if _blank(label, got):
        return False
    answer = _as_count(got)
    if answer is None:
        print(f"{NO} {label}: " + _t(
            "сколько-нибудь штук — это целое число",
            "a number of things is a whole number"))
        return False
    if answer < 0:
        print(f"{NO} {label}: " + _t("объектов не бывает меньше нуля",
                                     "there is no negative number of things"))
        return False

    if isinstance(objects, (int, sp.Integer)):
        if keep is not None:
            raise ValueError(_t(
                'verify_count: фильтру нужен перебор, а не готовое число',
                'verify_count: keep needs objects to enumerate, not a number'))
        total = matched = int(objects)
    else:
        total = matched = 0
        for item in objects:
            total += 1
            if keep is None or keep(item):
                matched += 1
    if total == 0:
        print(f"{NO} {label}: " + _t("перебирать нечего: объектов ноль",
                                     "nothing to enumerate: no objects at all"))
        return False

    want = matched * each
    if answer == want:
        print(f"{OK} {label}")
        return True
    for what, value in _count_slips(total, matched, each).items():
        if value == answer:
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t(
        "столько объектов не насчитывается: перебор даёт другое число",
        "the enumeration does not come to that many"))
    return False


def verify_count_law(label, got, var, count, sizes):
    """Ответ — выражение от n, и оно проверяется пересчётом при малых n.

    Экзамен просит «write down an expression for the number of ways», и
    сверять такое с записанным ⁿC₃ значило бы сверять запись. Проверка
    вместо этого берёт маленькие n, пересчитывает объекты перебором и
    смотрит, то же ли число даёт выражение. Любая верная форма проходит:
    ⁿC₃, n!/(3!(n−3)!) и n(n−1)(n−2)/6 — одно и то же выражение.

    Сообщение называет то n, на котором разошлось, и сколько объектов
    там на самом деле. Это подсказка, но подсказка про n = 5, а спросили
    про общее n — как и в verify_roots, где сообщение говорит, около
    какой точки пропажа, но не называет самого корня.
    """
    if _blank(label, got):
        return False
    try:
        expr = sp.sympify(got)
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
    for size in sizes:
        real = int(count(size))
        mine = sp.simplify(expr.subs(var, size))
        if not mine.is_number or sp.simplify(mine - real) != 0:
            print(f"{NO} {label}: " + _t(
                f"при {var} = {size} объектов {real}, "
                f"а выражение даёт {mine}",
                f"at {var} = {size} there are {real} objects, "
                f"but the expression gives {mine}"))
            return False
    print(f"{OK} {label}")
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


# ===================================================== последовательность
# Шестнадцатое понятие равенства ответов: последовательность порождается.
#
# Эталона снова нет. Проверка получает не ответ и не формулу, а правило:
# первый член и шаг. Член находится сложением шага n−1 раз, сумма —
# сложением первых n членов. Ни u₁+(n−1)d, ни n/2(2u₁+(n−1)d) внутри
# проверки не написано ни разу, и потому 2n+3, 5+2(n−1) и n+(n+3)
# проходят одинаково.
#
# Работает в обе стороны, и в этой теме обратный ход — половина заданий.
# Прямой: прогрессия известна, ответ — её член или сумма. Обратный: член
# известен из условия, а прогрессию строят из ответа, и она обязана этому
# члену отвечать. Так проверяется «найдите первый член и разность» —
# самый частый вопрос темы, у которого ответов два и оба в одной строке.

_SEQ_TOL = 5e-4          # три значащие цифры — столько же принимает экзамен
_SEQ_WALK = 4000         # дальше по прогрессии проверка не идёт
_SEQ_SAMPLES = (1, 2, 3, 5, 8)   # значения n, на которых сверяется формула


def progression(first, step):
    """Арифметическая прогрессия как правило, а не как формула.

    first — первый член, step — общая разность. Проверка не хранит из
    этого ничего, кроме пары чисел: члены она получает сложением.

    Оба аргумента разрешено брать из ещё не заполненного ответа, и тогда
    прогрессии просто нет: ноутбук обязан проходиться сверху вниз
    и пустым.
    """
    if any(v is Ellipsis for v in (first, step)):
        return ('ap', Ellipsis, Ellipsis)
    return ('ap', sp.sympify(first), sp.sympify(step))


def _run(seq, count):
    """Первые count членов прогрессии, полученные сложением."""
    if not isinstance(seq, (list, tuple)) or len(seq) != 3 or seq[0] != 'ap':
        raise ValueError(_t('последовательность задаётся progression(...)',
                            'a sequence is given by progression(...)'))
    value, out = seq[1], []
    for _ in range(count):
        out.append(value)
        value = value + seq[2]
    return out


def blank(*values):
    """Остался ли хоть в одном ответе placeholder `...`.

    Правило прогрессии в ноутбуке постоянно собирают из ответа, и
    собирать бывает ещё не из чего. Явная проверка нужна там, где
    выражение считается до вызова verify_*: `q*n**2` с Ellipsis
    внутри падает раньше, чем проверка успеет напечатать белый квадрат.
    """
    return any(value is Ellipsis for value in values)


def term(seq, n):
    """n-й член прогрессии, полученный сложением.

    Нужен там, где условие говорит не про один член: «шестой и
    двенадцатый в сумме дают двадцать четыре» — это term(mine, 6)
    и term(mine, 12), сложенные в самой ячейке.
    """
    if blank(seq[1], seq[2]):
        return Ellipsis
    return _run(seq, int(n))[-1]


def total(seq, n):
    """Сумма первых n членов прогрессии, полученная сложением."""
    if blank(seq[1], seq[2]):
        return Ellipsis
    return sp.Add(*_run(seq, int(n)))


def _index(label, n):
    """Номер члена: целое и положительное, иначе это не номер.

    Схема оценивания ноября 2025 года прощает ответ «n = 0, 13»
    отдельной оговоркой — значит, соблазн назвать номером ноль
    достаточно частый, чтобы его назвать вслух.
    """
    try:
        value = sp.sympify(n)
    except (sp.SympifyError, TypeError, AttributeError):
        value = None
    if value is None or getattr(value, 'free_symbols', set()) \
            or not value.is_number:
        print(f"{NO} {label}: " + _t("номер члена это число",
                                     "the index of a term is a number"))
        return None
    if not _near(value, sp.Integer(round(float(value))), _SEQ_TOL) \
            or float(value) < 1:
        print(f"{NO} {label}: " + _t(
            "номер считает члены: он обязан быть целым и положительным",
            "an index counts terms: it has to be a whole number, and at "
            "least one"))
        return None
    if float(value) > _SEQ_WALK:
        print(f"{NO} {label}: " + _t(
            f"дальше {_SEQ_WALK}-го члена проверка не идёт",
            f"the check does not walk past term {_SEQ_WALK}"))
        return None
    return int(round(float(value)))


def _as_value(label, got, want, what):
    """Ответ, приведённый к выражению, или None.

    Буква в ответе допустима ровно тогда, когда она есть и в самой
    прогрессии: у последовательности ln x, ⅔ln x, ⅓ln x суммы числами
    не бывают. А там, где прогрессия числовая, выражение с буквой —
    не ответ, и об этом стоит сказать прямо.
    """
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        print(f"{NO} {label}: {what}")
        return None
    free = getattr(sp.sympify(want), 'free_symbols', set())
    if getattr(value, 'free_symbols', set()) and not free:
        print(f"{NO} {label}: {what}")
        return None
    return value


def _agree(got, want, tol=_SEQ_TOL):
    """Сходится ли ответ с тем, что дала прогрессия.

    Сначала алгебраически: у логарифмических членов числа нет вовсе,
    и −90 − 25 ln 3 сравнивать с суммой можно только упрощением.
    Потом численно, с тем же допуском, что принимает экзамен.
    """
    try:
        if sp.simplify(sp.sympify(got) - sp.sympify(want)) == 0:
            return True
    except (sp.SympifyError, TypeError, AttributeError):
        return False
    return _near(got, want, tol)


def _seq_report(label, got, want, slips, tol=_SEQ_TOL):
    """Общий разбор: сходится, известный промах или мимо."""
    if _agree(got, want, tol):
        print(f"{OK} {label}")
        return True
    for what, value in slips.items():
        if value is not None and _agree(got, value, tol):
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t("у этой последовательности выходит другое",
                                 "this sequence gives something else"))
    return False


def _sampled(label, got, rule, var, values):
    """Сверка ответа-выражения: обе стороны считаются при нескольких n.

    Ответ вида u_n = 2n + 3 нельзя сверить сложением при одном номере:
    формула должна совпадать с прогрессией на всех n, а не на счастливом.
    Поэтому берётся несколько значений, и каждое проверяется отдельно.
    """
    for value in values:
        want = rule(value)
        if want is None:
            return False
        mine = sp.sympify(got).subs(var, value)
        if not _agree(mine, want):
            print(f"{NO} {label}: " + _t(
                f"при {var} = {value} последовательность даёт другое",
                f"at {var} = {value} the sequence gives something else"))
            return False
    print(f"{OK} {label}")
    return True


def verify_term(label, got, seq, n):
    """Ответ — член последовательности, и он получается сложением.

    seq строится progression(first, step); n — номер члена. Проверка
    доходит до него шагами и сравнивает с ответом; формулы n-го члена
    у неё нет.

    Обратный ход — тот же вызов, прочитанный наоборот:

        verify_term('1', 6, progression(q_u1, q_d), 7)

    это «седьмой член вашей прогрессии равен шести?», и так проверяется
    «найдите первый член и общую разность» без единого хранимого ответа.

    Если ответ содержит букву, n обязано быть этой буквой: тогда
    сравнение идёт при нескольких её значениях сразу, и «выразите u_n
    через n» проверяется тем же вызовом.
    """
    if _blank(label, got, seq, n):
        return False
    if isinstance(n, sp.Symbol):
        return _sampled(label, got, lambda i: _run(seq, i)[-1], n,
                        _SEQ_SAMPLES)
    index = _index(label, n)
    if index is None:
        return False
    terms = _run(seq, index + 1)
    want = terms[index - 1]
    answer = _as_value(label, got, want,
                       _t("член этой последовательности это число",
                          "a term of this sequence is a number"))
    if answer is None:
        return False
    slips = {_t("это следующий член: номер сдвинут на единицу",
                "that is the next term: the index is out by one"):
             terms[index],
             _t("это предыдущий член: номер сдвинут на единицу",
                "that is the previous term: the index is out by one"):
             terms[index - 2] if index > 1 else None,
             _t("шаг сделан n раз вместо n−1: первый член тоже член",
                "the step is taken n times instead of n−1: the first term "
                "is a term too"): terms[index - 1] + seq[2],
             _t("это сумма первых членов, а не сам член",
                "that is the sum of the terms, not the term itself"):
             sp.Add(*terms[:index])}
    return _seq_report(label, answer, want, slips)


def verify_total(label, got, seq, n):
    """Ответ — сумма первых n членов, и она получается сложением.

    Ни n/2(2u₁+(n−1)d), ни n/2(u₁+u_n) проверке не нужны: она честно
    складывает первые n членов прогрессии.

    Обратный ход тот же: `verify_total('1b', 0, mine, q_n)` — «сумма
    первых ваших n членов равна нулю?», и так проверяется «найдите n».
    Номер при этом обязан быть целым и положительным, и проверка это
    говорит отдельной строкой: ноль членов тоже даёт нулевую сумму,
    и схема оценивания такой ответ отдельно оговаривает.

    Ответ-формула сверяется при нескольких n, как и в verify_term.
    """
    if _blank(label, got, seq, n):
        return False
    if isinstance(n, sp.Symbol):
        return _sampled(label, got, lambda i: sp.Add(*_run(seq, i)), n,
                        _SEQ_SAMPLES)
    index = _index(label, n)
    if index is None:
        return False
    terms = _run(seq, index + 1)
    want = sp.Add(*terms[:index])
    answer = _as_value(label, got, want, _t("сумма этой последовательности "
                                            "это число",
                                            "a sum of this sequence is "
                                            "a number"))
    if answer is None:
        return False
    slips = {_t("это n-й член, а не сумма первых n",
                "that is the nth term, not the sum of the first n"):
             terms[index - 1],
             _t("сложено на один член больше",
                "one term too many has been added"): sp.Add(*terms),
             _t("сложено на один член меньше",
                "one term too few has been added"):
             sp.Add(*terms[:index - 1]) if index > 1 else None,
             _t("сумма удвоена: n/2 превратилось в n",
                "the sum is doubled: the n/2 has become n"): 2 * want,
             _t("взята половина суммы",
                "that is half of the sum"): want / 2}
    return _seq_report(label, answer, want, slips)


def verify_start(label, got, seq):
    """Ответ — несколько первых членов подряд.

    «Write down the first four terms» — вопрос на четыре балла, где
    считать нечего, а промахнуться можно в каждом. Список сверяется
    почленно, и сообщение называет номер первого расхождения, не
    называя, что там должно стоять.
    """
    if _blank(label, got, seq):
        return False
    if not isinstance(got, (list, tuple)) or not got:
        print(f"{NO} {label}: " + _t("ответ это список членов подряд",
                                     "the answer is a list of consecutive "
                                     "terms"))
        return False
    terms = _run(seq, len(got))
    for i, (mine, want) in enumerate(zip(got, terms), start=1):
        value = _as_value(label, mine, want,
                          _t("член этой последовательности это число",
                             "a term of this sequence is a number"))
        if value is None:
            return False
        if not _agree(value, want):
            print(f"{NO} {label}: " + _t(
                f"член номер {i} не такой", f"term number {i} is not that"))
            return False
    print(f"{OK} {label}")
    return True


def _differences(label, items, var, values):
    """Разности соседних членов. None, если список не годится."""
    if len(items) < 3:
        print(f"{NO} {label}: " + _t(
            "арифметическая последовательность начинается с трёх членов",
            "an arithmetic sequence starts at three terms"))
        return None
    runs = [{}] if var is None else [{var: value} for value in values]
    out = []
    for run in runs:
        row = []
        for before, after in zip(items, items[1:]):
            try:
                row.append(sp.simplify(sp.sympify(after).subs(run)
                                       - sp.sympify(before).subs(run)))
            except (sp.SympifyError, TypeError, AttributeError):
                print(f"{NO} {label}: " + _t("члены это выражения",
                                             "the terms are expressions"))
                return None
        out.append(row)
    return out


def verify_arithmetic(label, items, var=None, values=()):
    """Эти члены, в этом порядке, образуют арифметическую последовательность?

    Ответа-числа здесь нет вовсе: ответ сидит внутри самих членов.
    Экзамен спрашивает «покажите, что m, r и c образуют арифметическую
    последовательность», и ваш найденный c приходит сюда третьим членом.

    var и values — когда члены содержат букву: условие обязано
    выполняться при всех её значениях, а не при одном удачном, поэтому
    берётся несколько.
    """
    if _blank(label, *items):
        return False
    rows = _differences(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, step in enumerate(row[1:], start=2):
            if not _agree(step, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"разность между членами {i} и {i + 1} не такая, как "
                    f"между первыми двумя",
                    f"the difference between terms {i} and {i + 1} is not "
                    f"the one between the first two"))
                return False
    print(f"{OK} {label}")
    return True


def verify_step(label, got, items, var=None, values=()):
    """Ответ — общая разность, и она берётся вычитанием соседних членов.

    Сначала проверяется, что разность вообще постоянна: «найдите общую
    разность» у неарифметической последовательности ответа не имеет.
    Потом — что она равна вашей.

    items разрешено собирать из правила: [rule(1), rule(2), rule(3)] —
    так проверяется «покажите, что площади образуют арифметическую
    последовательность, и найдите разность».
    """
    if _blank(label, got, *items):
        return False
    rows = _differences(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, step in enumerate(row[1:], start=2):
            if not _agree(step, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"разность непостоянна: между членами {i} и {i + 1} она "
                    f"другая",
                    f"the difference is not constant: between terms {i} and "
                    f"{i + 1} it is different"))
                return False
    want = rows[0][0]
    if var is not None:
        for run, row in zip([{var: value} for value in values], rows):
            if not _agree(sp.sympify(got).subs(run), row[0]):
                print(f"{NO} {label}: " + _t(
                    "разность этой последовательности другая",
                    "this sequence has a different common difference"))
                return False
        print(f"{OK} {label}")
        return True
    answer = _as_value(label, got, want,
                       _t("общая разность этой последовательности это число",
                          "the common difference of this sequence is "
                          "a number"))
    if answer is None:
        return False
    slips = {_t("знак разности противоположный: она считается как "
                "следующий минус предыдущий",
                "the sign is the other way round: the difference is the "
                "next term minus the one before"): -want,
             _t("это разность через один член, а не между соседними",
                "that is the difference two terms apart, not between "
                "neighbours"): 2 * want}
    return _seq_report(label, answer, want, slips)


def verify_peak(label, got, seq, at=None, limit=None):
    """Ответ — наибольшая из сумм S₁, S₂, S₃, … , и её ищут перебором.

    Проверка складывает член за членом и запоминает наибольшую сумму.
    Знать, что S_n — квадратичная по n и что максимум приходится на
    перемену знака членов, ей для этого не нужно.

    at — номер, на котором максимум достигается, если вопрос просит и
    его. Максимум бывает достигнут дважды подряд: когда очередной член
    ровно нуль, S_{n−1} = S_n, и оба номера верны. Проверка принимает
    любой из них.
    """
    if _blank(label, got, seq):
        return False
    if at is not None and _blank(label, at):
        return False
    step = seq[2]
    if not sp.sympify(step).is_number or float(step) >= 0:
        print(f"{NO} {label}: " + _t(
            "у растущей последовательности наибольшей суммы нет",
            "a sequence that grows has no greatest sum"))
        return False
    # Шагов ровно столько, сколько нужно, чтобы члены сменили знак:
    # после этого суммы только убывают.
    span = limit or min(_SEQ_WALK,
                        int(abs(float(seq[1]) / float(step))) + 5)
    terms = _run(seq, max(span, 2))
    best, running, where = None, 0, []
    for i, value in enumerate(terms, start=1):
        running = running + value
        if best is None or float(running - best) > _SEQ_TOL:
            best, where = running, [i]
        elif _near(running, best, _SEQ_TOL):
            where.append(i)
    answer = _as_value(label, got, best, _t("сумма это число",
                                           "a sum is a number"))
    if answer is None:
        return False
    slips = {_t("это наибольший член, а не наибольшая сумма",
                "that is the largest term, not the largest sum"): terms[0],
             _t("сумма оборвана на один член раньше, чем нужно",
                "the sum stops one term short"):
             best - terms[where[0] - 1] if where[0] > 1 else None}
    if not _seq_report(label, answer, best, slips):
        return False
    if at is not None:
        index = _index(f'{label} (n)', at)
        if index is None:
            return False
        if index not in where:
            print(f"{NO} {label} (n): " + _t(
                "на этом номере сумма не наибольшая",
                "the sum is not greatest at that index"))
            return False
        print(f"{OK} {label} (n)")
    return True


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
