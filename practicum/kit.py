"""Проверочный набор для практикумов по IB Mathematics AA HL.

Принцип: ответ проверяется по существу задачи, а не сравнением с записанным
эталоном. Решение дифференциального уравнения подставляется в само уравнение,
неявный ответ принимается в любой эквивалентной форме, числовой ответ
сверяется по хешу с округлением до требуемого числа значащих цифр.

Так в ячейке проверки не видно ответа, а эквивалентные формы записи
засчитываются — ровно как в markscheme.
"""

import hashlib
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
    simplify, trigsimp, expand, expand_trig, factor, cancel, together, apart,
    solve, solveset, nsolve, Eq, Ne,
    diff, integrate, limit, series, dsolve, Derivative, Integral, Function,
    factorial, binomial, Sum, Product, Matrix, lambdify, nsimplify,
)

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
