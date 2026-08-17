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


def digest(value):
    """Короткий хеш ответа. Используется при составлении заданий."""
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


def _blank(label, *values):
    """Задание ещё не решено: в ячейке остался placeholder `...`.

    Ноутбук должен проходиться сверху вниз и с пустыми заданиями — иначе
    его нельзя ни запустить целиком, ни залить туда, где ячейки исполняются
    автоматически.

    Внутрь списков смотрим рекурсивно: там, где ответ это набор, в ячейке
    стоит `[...]`, и снаружи такой список от заполненного не отличается.
    """
    def has_gap(v):
        if v is Ellipsis:
            return True
        if isinstance(v, (list, tuple, set, frozenset)):
            return any(has_gap(i) for i in v)
        return False

    if any(has_gap(v) for v in values):
        print(f"⬜ {label}: ответ не заполнен")
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
        print(f"{NO} {label}: не удовлетворяет уравнению, невязка = {resid}")
        return False
    if ic is not None:
        x0, y0 = ic
        got = sp.simplify(y_expr.subs(var, sp.sympify(x0)))
        if sp.simplify(got - sp.sympify(y0)) != 0:
            print(f"{NO} {label}: уравнение решено, но y({x0}) = {got}, а нужно {y0}")
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
        print(f"{NO} {label}: не сводится к верному ответу домножением на константу")
        return False
    tail = "" if ratio == 1 else f" (эквивалентная форма, множитель {ratio})"
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
    print(f"{NO} {label}: {got} — не сходится (проверь округление до {sf} знач. цифр)")
    return False


def check_expr(label, got, want_digest):
    """Символьный ответ, сверяемый по хешу канонической записи."""
    if _blank(label, got):
        return False
    got = sp.sympify(got)
    if digest(sp.srepr(sp.simplify(got))) == want_digest:
        print(f"{OK} {label}: {got}")
        return True
    print(f"{NO} {label}: {got} — не сходится")
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
    print(f"{NO} {label}: {got} — не сходится")
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
    print(f"{NO} {label}: {{{', '.join(str(v) for v in values)}}} — не сходится")
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
    print(f"{NO} {label}: {sp.expand(sp.sympify(got))} — не сходится")
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
    print(f"{NO} {label}: {{{', '.join(str(i) for i in items)}}} — не сходится")
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
        print(f"{OK} {label}: тождество выполняется")
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
            print(f"{NO} {label}: при {var} = {s:g} стороны расходятся на {abs(val):.3g}")
            return False
    if checked < 3:
        print(f"{NO} {label}: проверить не удалось — слишком много особых точек")
        return False
    print(f"{OK} {label}: тождество выполняется (проверено в {checked} точках)")
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
            return False, f"при {var} = {s} расхождение {abs(val):.3g}"
    if checked < 3:
        return False, "проверить не удалось: слишком много особых точек"
    return True, f"проверено в {checked} точках"


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
            print(f"⬜ {label}, база: не заполнена")
            ok = False
        else:
            diff = sp.simplify(sp.expand(sp.sympify(base_lhs) - formula.subs(var, n0)))
            if diff == 0:
                print(f"{OK} {label}, база: при {var} = {n0} стороны равны")
            else:
                print(f"{NO} {label}, база: при {var} = {n0} стороны расходятся на {diff}")
                ok = False

    good, note = _agrees(got, formula.subs(var, var + 1), var, samples)
    tail = f" ({note})" if note else ""
    if good:
        print(f"{OK} {label}, переход: получено утверждение для {var} + 1{tail}")
    else:
        print(f"{NO} {label}, переход: это не утверждение для {var} + 1 — {note}")
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
        print(f"{OK} {label}, база: при {var} = {n0} получается {base} = {d}·{base / d}")
    else:
        print(f"{NO} {label}, база: при {var} = {n0} получается {base}, а оно не кратно {d}")
        ok = False

    rest = sp.expand(expr.subs(var, var + 1) - sp.sympify(mult) * expr)
    quot = sp.expand(rest / d)
    bad = [c for c in quot.as_coefficients_dict().values() if not sp.sympify(c).is_Integer]
    if bad:
        print(f"{NO} {label}, шаг: остаток {rest} на {d} нацело не делится "
              f"(после деления остаются дроби {bad})")
        return False
    for s in samples:
        if not sp.sympify(quot.subs(var, s)).is_integer:
            print(f"{NO} {label}, шаг: при {var} = {s} частное {quot.subs(var, s)} не целое")
            return False
    print(f"{OK} {label}, шаг: остаток равен {d}·({quot})")
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
            print(f"{NO} {label}: при {dict(zip(map(str, free), combo))} "
                  f"получается {val}, а это не целое")
            return False
        got = int(val) % int(mod)
        if got != int(want) % int(mod):
            print(f"{NO} {label}: при {dict(zip(map(str, free), combo))} остаток "
                  f"от деления на {mod} равен {got}, а не {want}")
            return False
        checked += 1
    print(f"{OK} {label}: остаток от деления на {mod} всегда {int(want) % int(mod)} "
          f"(проверено наборов: {checked})")
    return True


def check_order(label, seq, want_digest, n=None):
    """Ответ — порядок шагов доказательства. В отличие от check_set порядок важен."""
    if _blank(label, seq):
        return False
    items = [str(s).strip().lower() for s in seq]
    if n is not None and len(items) != n:
        print(f"{NO} {label}: шагов должно быть {n}, а получено {len(items)}")
        return False
    if digest('|'.join(items)) == want_digest:
        print(f"{OK} {label}: {' → '.join(items)}")
        return True
    print(f"{NO} {label}: {' → '.join(items)} — порядок не тот")
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
        print(f"{NO} {label}: это не произведение — многочлен записан одной строкой")
        return False

    facs = []
    for arg in args:
        if var not in arg.free_symbols:
            continue                                   # числовой множитель
        base, exp = arg.as_base_exp()
        if not (exp.is_Integer and exp > 0):
            print(f"{NO} {label}: множитель {arg} — не многочлен")
            return False
        d = _poly_degree(base, var)
        if d is None:
            print(f"{NO} {label}: множитель {base} — не многочлен от {var}")
            return False
        if d > max_deg:
            print(f"{NO} {label}: множитель {base} имеет степень {d}, "
                  f"а нужны множители степени не выше {max_deg} — "
                  f"разложение не доведено до конца")
            return False
        facs.extend([base] * int(exp))

    if not facs:
        print(f"{NO} {label}: множителей с {var} не нашлось")
        return False
    if n is not None and len(facs) != n:
        print(f"{NO} {label}: множителей должно быть {n} (кратные считаются "
              f"по разу за каждую степень), а получилось {len(facs)}")
        return False
    if sp.expand(e - orig) != 0:
        print(f"{NO} {label}: произведение раскрывается в {sp.expand(e)}, "
              f"а исходный многочлен {sp.expand(orig)}")
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
        print(f"{NO} {label}: делимое не восстанавливается, невязка = {resid}")
        return False

    d_den = _poly_degree(den, var)
    d_rem = -1 if sp.simplify(rem) == 0 else _poly_degree(rem, var)
    if d_den is None or d_rem is None:
        print(f"{NO} {label}: делитель и остаток должны быть многочленами от {var}")
        return False
    if d_rem >= d_den:
        print(f"{NO} {label}: остаток степени {d_rem} не ниже делителя "
              f"(степень {d_den}) — делить можно дальше")
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
        print(f"{NO} {label}: остаток от деления равен {sp.expand(rem)}, "
              f"а должен быть нулём")
        return False
    print(f"{OK} {label}: {p} делится на {sp.expand(d)} нацело, частное {quo}")
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
            print(f"{NO} {label}: слагаемое {term} — не дробь с {var} в знаменателе")
            return False
        if var in num.free_symbols:
            print(f"{NO} {label}: у слагаемого {term} числитель зависит от {var}; "
                  f"простейшая дробь так не выглядит")
            return False
        try:
            _, pieces = sp.factor_list(den, var)
        except (sp.PolynomialError, sp.GeneratorsNeeded):
            print(f"{NO} {label}: знаменатель {den} — не многочлен от {var}")
            return False
        if len(pieces) != 1:
            print(f"{NO} {label}: знаменатель {den} сам раскладывается на множители — "
                  f"дробь не доведена до простейшей")
            return False
        d = _poly_degree(pieces[0][0], var)
        if d is None or d > 1:
            print(f"{NO} {label}: знаменатель {den} не является степенью "
                  f"линейного множителя")
            return False

    if sp.simplify(sp.cancel(sp.together(e - orig))) != 0:
        print(f"{NO} {label}: сумма дробей не равна исходному выражению")
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
        print(f"{NO} {label}: многочлен получился нулевым")
        return False

    want = []
    for r in sp.Poly(sp.expand(sp.sympify(original)), var).nroots(n=20):
        try:
            want.append(complex(sp.N(transform(r))))
        except (ZeroDivisionError, TypeError, ValueError):
            print(f"{NO} {label}: преобразование не определено для корня {r}")
            return False
    got = [complex(v) for v in sp.Poly(sp.expand(new), var).nroots(n=20)]

    if len(got) != len(want):
        print(f"{NO} {label}: корней должно быть {len(want)}, а у многочлена {len(got)}")
        return False

    free = list(want)
    for g in got:
        near = min(range(len(free)), key=lambda i: abs(free[i] - g), default=None)
        if near is None or abs(free[near] - g) > tol * max(1.0, abs(g)):
            print(f"{NO} {label}: корень {g:.6g} не совпадает ни с одним нужным")
            return False
        free.pop(near)
    print(f"{OK} {label}: {sp.expand(new)} = 0 — корни те, что нужно")
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
        print(f"{NO} {label}: ответ должен быть множеством или неравенством — "
              f"Interval(-5, 1), (x >= -5) & (x <= 1), Union(...)")
        return False

    cond = sp.sympify(ineq)
    try:
        truth = sp.Intersection(cond.as_set(), domain)
    except (NotImplementedError, ValueError, TypeError):
        truth = sp.solveset(cond, var, domain)
    if isinstance(truth, sp.ConditionSet):
        print(f"{NO} {label}: sympy не смог решить это неравенство сам — "
              f"проверка неприменима")
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
        print(f"{NO} {label}: лишнее — {_show_set(extra, var)}")
    if missing is not sp.S.EmptySet:
        print(f"{NO} {label}: потеряно — {_show_set(missing, var)}")
    if isinstance(extra, sp.FiniteSet) or isinstance(missing, sp.FiniteSet):
        print("   расхождение только в отдельных точках: посмотрите, "
              "строгое неравенство или нет и не обращается ли там в ноль "
              "знаменатель")
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
        print(f"{NO} {label}: ответ должен быть множеством или неравенством")
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
                print(f"{NO} {label}: при {var} = {v} условие не выполняется, "
                      f"а ваше множество эту точку содержит")
            else:
                print(f"{NO} {label}: при {var} = {v} условие выполняется, "
                      f"а в ваше множество эта точка не входит")
            return False
    if checked < 4:
        print(f"{NO} {label}: проверить не удалось — годных точек нашлось "
              f"всего {checked}")
        return False
    tail = f", пропущено {skipped}" if skipped else ""
    print(f"{OK} {label}: {_show_set(mine, var)} — проверено в {checked} "
          f"точках{tail}")
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
            print(f"{NO} {label}: слагаемое {term} входит со знаком минус — "
                  f"по такой записи неотрицательность не видна")
            return False
        if rest.is_number:
            if rest.is_negative:
                print(f"{NO} {label}: слагаемое {term} отрицательно")
                return False
            continue
        if isinstance(rest, sp.Abs):
            continue
        base, power = rest.as_base_exp()
        if not (power.is_Integer and power > 0 and power % 2 == 0):
            print(f"{NO} {label}: слагаемое {term} — не квадрат и не модуль; "
                  f"неотрицательность из такой записи не следует")
            return False

    diff = sp.simplify(sp.expand(e - target))
    if diff != 0:
        print(f"{NO} {label}: запись неотрицательна, но исходному выражению "
              f"не равна: разность {diff}")
        return False
    print(f"{OK} {label}: {e} — неотрицательно по виду и равно исходному")
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
            bad.append((r, 'вне области'))
            continue
        try:
            if abs(f(float(r))) > 1e-6:
                bad.append((r, 'не обращает уравнение в ноль'))
        except (ValueError, ZeroDivisionError, OverflowError):
            bad.append((r, 'уравнение в этой точке не определено'))
    if bad:
        for r, why in bad:
            print(f"{NO} {label}: {r} — {why}")
        return False

    found = _scan_roots(f, float(a), float(b))
    extra = len(found) - len(given)
    if extra > 0:
        miss = [c for c in found
                if all(abs(c - float(r)) > 1e-4 for r in given)]
        hint = f", первый пропущенный около {miss[0]:.4f}" if miss else ""
        print(f"{NO} {label}: корни верны, но найдено не всё — "
              f"на отрезке их {len(found)}, а у вас {len(given)}{hint}")
        return False
    if len(set(map(str, given))) != len(given):
        print(f"{NO} {label}: один и тот же корень указан дважды")
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
        print("⬜ тренажёр: ответы не заполнены")
        return False
    wrong = []
    for i, want in key.items():
        got = str(answers.get(i, "")).strip().lower()
        if digest(got) != want:
            wrong.append(i)
    if not wrong:
        print(f"{OK} все {len(key)} распознаны")
        return True
    print(f"{NO} перепроверь пункты: {', '.join(map(str, wrong))} "
          f"(верно {len(key) - len(wrong)} из {len(key)})")
    return False
