"""Функции: обратная (B2), преобразования графиков (B3), асимптоты и
множество значений (B4), а с ними точное значение, корни на промежутке (C3)
и модель по данным (B5).

Здесь же `_scan_roots` — поиск корней сеткой, которым пользуются и темы
анализа.
"""

import itertools
import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _agrees, _blank, _t
from .algebra import _as_domain, _as_set, _interior, _pieces, _show_set


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


# --- точное значение, корни на промежутке, модель по данным -----------------

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
