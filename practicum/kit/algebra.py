"""Алгебра: многочлены (A4), неравенства (A8), уравнения (B1).

Три понятия равенства ответов: форма записи, множество, уравнение.
"""

import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t


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
