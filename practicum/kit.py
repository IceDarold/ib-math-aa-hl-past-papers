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
    solve, solveset, nsolve, Eq, Ne,
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
    """
    if any(v is Ellipsis for v in values):
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
