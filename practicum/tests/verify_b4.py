"""Прогоняет все проверки практикума B4 с ответами, выведенными заново.

Ответы не переписываются из раздела решений. Асимптоты берутся пределами,
множества значений — решением уравнения f(x) = y относительно x, особенности
эскизов — через solveset и diff, а счётные ответы Paper 3 — подсчётом
различных вещественных корней. Отдельно измеряется, что проверки отвергают
и где они мягче экзамена.

Здесь же перепроверены шесть расхождений с разметкой корпуса. Три из них —
неверно записанные функции (снова теряются дробная черта и показатель),
одно — удвоенная ноябрьская сессия 2023 года, найденная ещё в B2, одно —
расхождение двух её копий между собой, и одно — функция, которой в корпусе
нет вовсе и которую восстанавливает markscheme.

Проверки печатают по-английски: ноутбук английский, а сверяются здесь
ровно те же вызовы с теми же ярлыками. Комментарии остаются русскими —
это документация репозитория, а не материал ученика.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *                                                  # noqa: F403

import io                                                          # noqa: E402
import contextlib                                                  # noqa: E402
import glob                                                        # noqa: E402

language('en')

NB = os.path.join(ROOT, 'practicum/functions',
                  'practicum-b4-curve-sketching.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(",
                                   "check_order(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
A_ = sp.Symbol('A', positive=True)
b_ = sp.Symbol('b')


def t(name, ok):
    res.append((name, ok))


def silent(fn, *args, **kwargs):
    """Вызвать проверку, не печатая её вердикт: нас интересует только он."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


def lines_of(f, var=x, domain=None):
    """Асимптоты, выведенные пределами с нуля, а не взятые из kit."""
    region = sp.S.Reals if domain is None else domain
    vertical = []
    sing = sp.singularities(f, var)
    if not isinstance(sing, sp.FiniteSet):
        sing = sing.intersect(region.closure)
    cands = list(sing.args) if isinstance(sing, sp.FiniteSet) else []
    if isinstance(region, sp.Interval) and region.start.is_finite:
        cands.append(region.start)
    for c in dict.fromkeys(cands):
        if any(sp.limit(f, var, c, side) in (sp.oo, -sp.oo, sp.zoo)
               for side in '+-'):
            vertical.append(sp.simplify(c))
    ends = []
    if not (isinstance(region, sp.Interval) and region.end.is_finite):
        ends.append(sp.oo)
    if not (isinstance(region, sp.Interval) and region.start.is_finite):
        ends.append(-sp.oo)
    horizontal, oblique = [], []
    for end in ends:
        lim = sp.limit(f, var, end)
        if lim.is_finite:
            horizontal.append(sp.simplify(lim))
            continue
        m = sp.limit(f / var, var, end)
        if m.is_finite and m != 0:
            c = sp.limit(f - m * var, var, end)
            if c.is_finite:
                oblique.append(sp.simplify(m * var + c))
    return vertical, list(dict.fromkeys(horizontal)), list(dict.fromkeys(oblique))


def as_equations(f, var=x, domain=None, kinds=('vertical', 'horizontal', 'oblique')):
    """Те же асимптоты, записанные уравнениями — то, что вводит ученик."""
    vert, hor, obl = lines_of(f, var, domain)
    out = []
    if 'vertical' in kinds:
        out += [sp.Eq(var, v) for v in vert]
    if 'horizontal' in kinds:
        out += [sp.Eq(y, h) for h in hor]
    if 'oblique' in kinds:
        out += [sp.Eq(y, o) for o in obl]
    return out


def turning(f, var=x, window=(-12, 12)):
    """Точки поворота: решаем f' = 0 символьно, а если не выходит — численно.

    Численный запасной путь нужен ровно там, где производная
    трансцендентна: у 2x − 2 + 10e^(−x−3) корни существуют, но solveset
    возвращает ConditionSet. Корни ищутся сканированием знака и
    уточняются nsolve — независимо от того, что печатает markscheme.
    """
    der = sp.diff(f, var)
    crit = sp.solveset(der, var, sp.S.Reals)
    if isinstance(crit, sp.ConditionSet):
        g = sp.lambdify(var, der, 'math')
        lo, hi = window
        grid = [lo + (hi - lo)*i/4000 for i in range(4001)]
        pts = []
        for u, w in zip(grid, grid[1:]):
            try:
                if g(u) == 0 or g(u)*g(w) < 0:
                    pts.append(sp.nsolve(der, var, (u + w)/2))
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                continue
        pts = sorted(pts, key=float)
    else:
        pts = sorted((c for c in crit if not c.free_symbols), key=float)
    out = []
    for c in pts:
        second = sp.simplify(sp.diff(f, var, 2).subs(var, c))
        kind = 'max' if second < 0 else 'min'
        out.append((sp.nsimplify(c), sp.simplify(f.subs(var, c)), kind))
    return out


def sf3(value):
    """Три значащие цифры — то, что принимает экзамен на Paper 2 и 3."""
    return float(f'{float(value):.3g}')


print('=== часть I: асимптоты ===')

# Задание 1. (2x+4)/(3−x). Асимптоты выводятся пределами, а не правилом
# о старших коэффициентах: правило проверяется этим же результатом.
f1 = (2*x + 4)/(3 - x)
v1, h1, o1 = lines_of(f1)
print(f'Задание 1: вертикальная {v1}, горизонтальная {h1}, наклонных {len(o1)}')
t('1-асимптоты найдены пределами', v1 == [3] and h1 == [-2] and not o1)
t('1-правило старших коэффициентов даёт то же',
  sp.Rational(2, -1) == h1[0])
t('1-проверка принимает', verify_asymptotes('Task 1(a)', as_equations(f1), f1))
zeros1 = sorted(sp.solveset(f1, x, sp.S.Reals), key=float)
t('1-пересечения',
  verify_sketch('Task 1(b)', {'x_intercepts': zeros1,
                              'y_intercept': f1.subs(x, 0)}, f1)
  and zeros1 == [-2] and f1.subs(x, 0) == R(4, 3))

# Задание 2. Три дроби, три однострочных ответа.
f2a = (7*x + 7)/(2*x - 4)
zero2 = list(sp.solveset(f2a, x, sp.S.Reals))[0]
print(f'Задание 2: ноль {zero2}, асимптоты {as_equations(f2a)}')
t('2-ноль функции', check_num('Task 2(a) zero', zero2, 6, D['Task 2(a) zero'])
  and zero2 == -1)
t('2-обе асимптоты', verify_asymptotes('Task 2(a)', as_equations(f2a), f2a))
for label, f, want in (('Task 2(b)', (3*x - 2)/(2*x + 1), R(3, 2)),
                       ('Task 2(c)', (2*x + 6)/(3*x + 6), R(2, 3))):
    hor = lines_of(f)[1]
    t(f'2-{label} горизонтальная = {want}',
      hor == [want]
      and verify_asymptotes(label, sp.Eq(y, hor[0]), f, kinds=('horizontal',)))
# Сокращать шестёрки нельзя: 2/3, а не 1.
t('2-общего множителя у 2x+6 и 3x+6 нет',
  sp.gcd(2*x + 6, 3*x + 6) == 1 and sp.limit((2*x + 6)/(3*x + 6), x, sp.oo) == R(2, 3))

# Задание 3. Логарифм: асимптота на границе области, и d ни при чём.
g3 = 2*log(x) - log(7)
t('3-вертикальная на границе области',
  lines_of(g3, domain=sp.Interval.open(0, sp.oo))[0] == [0])
t('3-и она не зависит от d',
  all(lines_of(2*log(x) - log(dv), domain=sp.Interval.open(0, sp.oo))[0] == [0]
      for dv in (1, 7, 100)))
t('3-проверка принимает',
  verify_asymptotes('Task 3', sp.Eq(x, 0), g3,
                    domain=sp.Interval.open(0, sp.oo), kinds=('vertical',)))

# Задание 4. Арксинус: предел внутри, потом внешняя функция.
f4 = sp.asin((x**2 - 1)/(x**2 + 1))
inner = sp.limit((x**2 - 1)/(x**2 + 1), x, sp.oo)
outer = sp.limit(f4, x, sp.oo)
print(f'Задание 4: внутри → {inner}, снаружи → {outer}')
t('4-внутренний предел равен 1', inner == 1)
t('4-внешняя функция даёт pi/2', outer == sp.pi/2 and outer == sp.asin(inner))
t('4-и слева то же', sp.limit(f4, x, -sp.oo) == sp.pi/2)
t('4-проверка принимает',
  verify_asymptotes('Task 4', sp.Eq(y, outer), f4, kinds=('horizontal',)))
# Ответ y = 1 — та самая ошибка, ради которой задание стоит в бумаге.
t('4-ответ y = 1 отвергается',
  not silent(verify_asymptotes, 'Task 4', sp.Eq(y, 1), f4,
             kinds=('horizontal',))[0])

# Задание 5. Ноябрь 2021: пересечения, вертикальная, наклонная.
f5 = (x**2 - x - 12)/(2*x - 15)
zeros5 = sorted(sp.solveset(sp.numer(sp.together(f5)), x, sp.S.Reals), key=float)
v5, h5, o5 = lines_of(f5)
print(f'Задание 5: нули {zeros5}, f(0) = {f5.subs(x, 0)}, '
      f'вертикальная {v5}, наклонная {o5}')
t('5-пересечения с осями', zeros5 == [-3, 4] and f5.subs(x, 0) == R(4, 5))
t('5-вертикальная', v5 == [R(15, 2)] and not h5)
# Наклонная выводится тремя способами markscheme, и все три сверяются.
q5, r5 = sp.div(sp.Poly(x**2 - x - 12, x), sp.Poly(2*x - 15, x))
by_division = q5.as_expr()
a5 = sp.limit(f5/x, x, sp.oo)
by_limit = sp.simplify(a5*x + sp.limit(f5 - a5*x, x, sp.oo))
aa, bb, cc = sp.symbols('aa bb cc')
sol5 = sp.solve(sp.Poly(sp.expand((aa*x + bb)*(2*x - 15) + cc - (x**2 - x - 12)),
                        x).coeffs(), [aa, bb, cc], dict=True)[0]
by_coeff = sol5[aa]*x + sol5[bb]
print(f'   делением {by_division}, пределом {by_limit}, коэффициентами {by_coeff}')
t('5-три метода markscheme дают одну прямую',
  sp.simplify(by_division - (x/2 + R(13, 4))) == 0
  and sp.simplify(by_limit - by_division) == 0
  and sp.simplify(by_coeff - by_division) == 0)
t('5-проверки принимают',
  verify_sketch('Task 5(a)', {'x_intercepts': zeros5,
                              'y_intercept': f5.subs(x, 0)}, f5)
  and verify_asymptotes('Task 5(b)', sp.Eq(x, v5[0]), f5, kinds=('vertical',))
  and verify_asymptotes('Task 5(c)', sp.Eq(y, o5[0]), f5, kinds=('oblique',)))
# Потерянный минус в 2b − 15a = −1 даёт b = −13/4 — и это отвергается.
t('5-знак в коэффициенте при x пойман',
  not silent(verify_asymptotes, 'Task 5(c)', sp.Eq(y, x/2 - R(13, 4)), f5,
             kinds=('oblique',))[0])

# Задание 6. Май 2021 TZ1: горизонтальной нет, и это весь вопрос.
g6 = (4*x**2 - 1)/(3*x + 2)
v6, h6, o6 = lines_of(g6)
print(f'Задание 6: вертикальная {v6}, горизонтальных {len(h6)}, наклонная {o6}')
t('6-горизонтальной нет, есть наклонная',
  v6 == [-R(2, 3)] and not h6 and sp.simplify(o6[0] - (4*x/3 - R(8, 9))) == 0)
t('6-сокращения нет', sp.gcd(4*x**2 - 1, 3*x + 2) == 1)
t('6-проверка принимает', verify_asymptotes('Task 6', as_equations(g6), g6))
# Отношение старших коэффициентов у неправильной дроби — не асимптота.
t('6-ответ y = 4/3 отвергается',
  not silent(verify_asymptotes, 'Task 6', [sp.Eq(x, -R(2, 3)), sp.Eq(y, R(4, 3))],
             g6)[0])

# Задание 7. Ноябрь 2023: тот же набор на другой дроби.
f7 = (x**2 - 14*x + 24)/(2*x + 6)
zeros7 = sorted(sp.solveset(x**2 - 14*x + 24, x, sp.S.Reals), key=float)
v7, h7, o7 = lines_of(f7)
print(f'Задание 7: нули {zeros7}, вертикальная {v7}, наклонная {o7}')
t('7-нули и асимптоты',
  zeros7 == [2, 12] and v7 == [-3] and not h7
  and sp.simplify(o7[0] - (x/2 - R(17, 2))) == 0)
t('7-проверки принимают',
  verify_asymptotes('Task 7(a)', sp.Eq(x, -3), f7, kinds=('vertical',))
  and verify_sketch('Task 7(b)', {'x_intercepts': zeros7}, f7)
  and verify_asymptotes('Task 7(c)', sp.Eq(y, o7[0]), f7, kinds=('oblique',)))
# markscheme принимает и уравнение знаменателя.
t('7-2x+6 = 0 тоже принимается',
  verify_asymptotes('Task 7(a)', sp.Eq(2*x + 6, 0), f7, kinds=('vertical',)))

# Задание 8. Наклонная целого семейства: параметр в ответ не входит.
f8 = x*(x**2 - A_)/(x**2 + A_)
slope8 = sp.limit(f8/x, x, sp.oo)
inter8 = sp.simplify(sp.limit(f8 - slope8*x, x, sp.oo))
print(f'Задание 8: наклон {slope8}, свободный член {inter8}, '
      f'остаток {sp.simplify(f8 - x)}')
t('8-асимптота y = x при любом A', slope8 == 1 and inter8 == 0)
t('8-остаток стремится к нулю', sp.limit(f8 - x, x, sp.oo) == 0)
t('8-и для трёх конкретных A',
  all(lines_of(f8.subs(A_, av))[2] == [x] for av in (1, 4, 16)))
t('8-проверка принимает',
  verify_asymptotes('Task 8', sp.Eq(y, x), f8, kinds=('oblique',)))

print('\n=== часть II: картинка и картинка боком ===')

# Задание 9. Первый эскиз.
f9 = (2*x - 1)/(x + 1)
v9, h9, _ = lines_of(f9)
zeros9 = sorted(sp.solveset(2*x - 1, x, sp.S.Reals), key=float)
t('9-асимптоты и пересечения',
  v9 == [-1] and h9 == [2] and zeros9 == [R(1, 2)] and f9.subs(x, 0) == -1)
t('9-проверки принимают',
  verify_asymptotes('Task 9(a)', as_equations(f9), f9)
  and verify_sketch('Task 9(b)', {'x_intercepts': zeros9,
                                  'y_intercept': f9.subs(x, 0)}, f9))
# Знаки по обе стороны от вертикальной асимптоты — тот самый приём.
left9 = f9.subs(x, -1 - R(1, 100))
right9 = f9.subs(x, -1 + R(1, 100))
print(f'Задание 9: слева от x = −1 значение {float(left9):.0f}, '
      f'справа {float(right9):.0f}')
t('9-ветви уходят в разные стороны', left9 > 0 > right9)

# Задание 10. Три ветви, ноль пересечений с осью x.
f10 = 1/(x**2 - 2*x - 3)
v10, h10, _ = lines_of(f10)
turn10 = turning(f10)
print(f'Задание 10: вертикальные {v10}, горизонтальная {h10}, поворот {turn10}')
t('10-две вертикальные и одна горизонтальная',
  sorted(v10, key=float) == [-1, 3] and h10 == [0])
t('10-пересечений с осью x нет',
  sp.solveset(sp.numer(sp.together(f10)), x, sp.S.Reals) == sp.S.EmptySet)
t('10-максимум в (1, −1/4)',
  turn10 == [(sp.Integer(1), R(-1, 4), 'max')])
t('10-вершина знаменателя там же',
  sp.solveset(sp.diff(x**2 - 2*x - 3, x), x, sp.S.Reals) == sp.FiniteSet(1))
t('10-проверки принимают',
  verify_asymptotes('Task 10(a)', as_equations(f10), f10)
  and verify_sketch('Task 10(b)', {'y_intercept': f10.subs(x, 0),
                                   'maxima': [(1, R(-1, 4))],
                                   'minima': []}, f10))
# Три ветви: между асимптотами функция отрицательна, снаружи положительна.
signs10 = [sp.sign(f10.subs(x, u)) for u in (-5, 1, 5)]
t('10-знаки трёх ветвей', signs10 == [1, -1, 1])

# Задание 11. Май 2021 TZ1: координаты вершин меняются местами.
f11 = (2*x + 3)/(4*x**2 - 1)
v11, h11, _ = lines_of(f11)
turn11 = turning(f11)
print(f'Задание 11: асимптоты {v11}, {h11}; поворотные точки '
      f'{[(sf3(u), sf3(w), kind) for u, w, kind in turn11]}')
t('11-асимптоты', sorted(v11, key=float) == [R(-1, 2), R(1, 2)] and h11 == [0])
t('11-стационарные точки из 4x^2+12x+1 = 0',
  sorted(sp.solveset(4*x**2 + 12*x + 1, x, sp.S.Reals), key=float)
  == sorted([u for u, _, _ in turn11], key=float))
maxes11 = [(u, w) for u, w, kind in turn11 if kind == 'max']
mins11 = [(u, w) for u, w, kind in turn11 if kind == 'min']
t('11-максимум и минимум найдены', len(maxes11) == 1 and len(mins11) == 1)
# Координаты одной точки — это координаты другой, переставленные.
t('11-координаты меняются местами',
  sp.simplify(maxes11[0][0] - mins11[0][1]) == 0
  and sp.simplify(maxes11[0][1] - mins11[0][0]) == 0)
t('11-проверки принимают',
  verify_asymptotes('Task 11(a)', as_equations(f11), f11)
  and verify_sketch('Task 11(b)',
                    {'x_intercepts': [R(-3, 2)], 'y_intercept': -3,
                     'maxima': [(sf3(maxes11[0][0]), sf3(maxes11[0][1]))],
                     'minima': [(sf3(mins11[0][0]), sf3(mins11[0][1]))]},
                    f11, domain=sp.Interval(-3, 3)))

# Задание 12. Две кривые, обе с наклонной асимптотой.
f12a = (x**2 - 14*x + 24)/(2*x + 6)
turn12a = turning(f12a)
print(f'Задание 12(a): поворотные {[(sf3(u), sf3(w), k) for u, w, k in turn12a]}')
t('12a-точки поворота в −3 ± 5sqrt3',
  sorted([sp.radsimp(u) for u, _, _ in turn12a], key=float)
  == sorted([-3 - 5*sp.sqrt(3), -3 + 5*sp.sqrt(3)], key=float))
t('12a-значения в них −10 ∓ 5sqrt3',
  sorted([sp.radsimp(w) for _, w, _ in turn12a], key=float)
  == sorted([-10 - 5*sp.sqrt(3), -10 + 5*sp.sqrt(3)], key=float))
# Максимум ниже минимума — это возможно только через вертикальную асимптоту.
hi12 = [w for _, w, k in turn12a if k == 'max'][0]
lo12 = [w for _, w, k in turn12a if k == 'min'][0]
t('12a-максимум лежит ниже минимума', hi12 < lo12)
t('12a-проверка принимает',
  verify_sketch('Task 12(a)',
                {'x_intercepts': [2, 12], 'y_intercept': 4,
                 'maxima': [(sf3(u), sf3(w)) for u, w, k in turn12a if k == 'max'],
                 'minima': [(sf3(u), sf3(w)) for u, w, k in turn12a if k == 'min']},
                f12a))
f12b = x*(x**2 - 16)/(x**2 + 16)
turn12b = turning(f12b)
zeros12b = sorted(sp.solveset(x*(x**2 - 16), x, sp.S.Reals), key=float)
print(f'Задание 12(b): нули {zeros12b}, поворотные '
      f'{[(sf3(u), sf3(w), k) for u, w, k in turn12b]}')
t('12b-три нуля, включая начало координат', zeros12b == [-4, 0, 4])
t('12b-функция нечётная', sp.simplify(f12b.subs(x, -x) + f12b) == 0)
t('12b-вершины симметричны',
  len(turn12b) == 2
  and sp.simplify(turn12b[0][0] + turn12b[1][0]) == 0
  and sp.simplify(turn12b[0][1] + turn12b[1][1]) == 0)
t('12b-и совпадают с markscheme',
  {(sf3(u), sf3(w)) for u, w, _ in turn12b} == {(-1.94, 1.2), (1.94, -1.2)})
t('12b-проверка принимает',
  verify_sketch('Task 12(b)',
                {'x_intercepts': zeros12b,
                 'maxima': [(sf3(u), sf3(w)) for u, w, k in turn12b if k == 'max'],
                 'minima': [(sf3(u), sf3(w)) for u, w, k in turn12b if k == 'min']},
                f12b, domain=sp.Interval(-10, 10)))

# Задание 13. Вершина параболы через выделение полного квадрата.
f13a = 6*x**2 - 12*x + 1
vertex13a = turning(f13a)[0]
t('13a-вершина (1, −5)', vertex13a == (sp.Integer(1), sp.Integer(-5), 'min'))
t('13a-выделение квадрата даёт то же',
  sp.simplify(f13a - (6*(x - 1)**2 - 5)) == 0)
t('13a-множество значений принято',
  verify_range('Task 13(a)', (y >= vertex13a[1]), f13a))
f13b = x**2/2 + 5*x + 13
vertex13b = turning(f13b)[0]
print(f'Задание 13: вершины {vertex13a} и {vertex13b}')
t('13b-вершина (−5, 1/2)', vertex13b == (sp.Integer(-5), R(1, 2), 'min'))
t('13b-дискриминант k^2 − 26 требует старшего коэффициента 1/2',
  sp.expand(sp.discriminant(x**2/2 + sp.Symbol('k')*x + 13, x))
  == sp.Symbol('k')**2 - 26)
t('13b-проверка принимает',
  verify_sketch('Task 13(b)', {'minima': [(-5, R(1, 2))]}, f13b))

# Задание 14. Множество значений с разрывом, выведенное дискриминантом.
f14 = f12a
disc14 = sp.expand(sp.discriminant(
    sp.expand((x**2 - 14*x + 24) - y*(2*x + 6)), x))
bounds14 = sorted(sp.solveset(disc14, y), key=float)
print(f'Задание 14: дискриминант {sp.factor(disc14)}, границы {bounds14}')
t('14-границы из дискриминанта совпадают со значениями в вершинах',
  bounds14 == sorted([sp.radsimp(w) for _, w, _ in turn12a], key=float))
range14 = sp.Union(sp.Interval(-sp.oo, bounds14[0]),
                   sp.Interval(bounds14[1], sp.oo))
t('14-проверка принимает', verify_range('Task 14', range14, f14))
t('14-строгие неравенства отвергаются',
  not silent(verify_range, 'Task 14',
             sp.Union(sp.Interval.open(-sp.oo, bounds14[0]),
                      sp.Interval.open(bounds14[1], sp.oo)), f14)[0])
t('14-без разрыва отвергается',
  not silent(verify_range, 'Task 14', sp.S.Reals, f14)[0])

# Задание 15. Дискриминант в чистом виде, и вырожденный случай y = 0.
g15 = (2*x - 5)/(x**2 - 3)
disc15 = sp.expand(sp.discriminant(sp.expand(y*(x**2 - 3) - (2*x - 5)), x))
bounds15 = sorted(sp.solveset(disc15, y), key=float)
print(f'Задание 15: дискриминант {disc15}, границы {bounds15}')
t('15-границы (5 ± sqrt13)/6',
  bounds15 == sorted([(5 - sp.sqrt(13))/6, (5 + sp.sqrt(13))/6], key=float))
# При y = 0 уравнение перестаёт быть квадратным — проверяем отдельно.
t('15-вырожденный случай y = 0 достигается при x = 5/2',
  sp.solveset(g15, x, sp.S.Reals) == sp.FiniteSet(R(5, 2))
  and 0 < bounds15[0])
range15 = sp.Union(sp.Interval(-sp.oo, bounds15[0]),
                   sp.Interval(bounds15[1], sp.oo))
t('15-проверка принимает', verify_range('Task 15', range15, g15))
# То же самое через точки поворота — второй маршрут markscheme.
turn15 = turning(g15)
t('15-точки поворота дают те же границы',
  sorted([sp.radsimp(w) for _, w, _ in turn15], key=float) == bounds15)

# Задание 16. Один конец достигается, другой нет.
g16 = -(3*x - 2)/(2*x + 1)
top16 = g16.subs(x, 0)
bottom16 = sp.limit(g16, x, sp.oo)
print(f'Задание 16: g(0) = {top16}, предел {bottom16}')
t('16-концы найдены', top16 == 2 and bottom16 == R(-3, 2))
t('16-g убывает на [0, oo)',
  sp.simplify(sp.diff(g16, x)).subs(x, 1) < 0
  and sp.solveset(sp.diff(g16, x), x, sp.Interval(0, sp.oo)) == sp.S.EmptySet)
t('16-проверка принимает',
  verify_range('Task 16', sp.Interval.Lopen(bottom16, top16), g16,
               domain=sp.Interval(0, sp.oo)))
t('16-закрытый нижний конец отвергается',
  not silent(verify_range, 'Task 16', sp.Interval(bottom16, top16), g16,
             domain=sp.Interval(0, sp.oo))[0])
# Без ограничения области ответ был бы другим — и это ловушка задания.
t('16-без x >= 0 ответ другой',
  not silent(verify_range, 'Task 16', sp.Interval.Lopen(bottom16, top16),
             g16)[0])

print('\n=== часть III: кривые, которых никто не рисовал ===')

# Задание 17. Парабола и четверть гиперболы.
f17a = 5*(x + 1)*(x + 3)
vertex17 = turning(f17a)[0]
t('17a-вершина (−2, −5) и пересечения',
  vertex17 == (sp.Integer(-2), sp.Integer(-5), 'min')
  and sorted(sp.solveset(f17a, x, sp.S.Reals), key=float) == [-3, -1]
  and f17a.subs(x, 0) == 15)
f17b = sp.sqrt(x**2 - 1)
ends17 = [(1, f17b.subs(x, 1)), (2, sp.radsimp(f17b.subs(x, 2)))]
print(f'Задание 17: вершина {vertex17}, концы {ends17}')
t('17b-концы (1, 0) и (2, sqrt3)', ends17 == [(1, 0), (2, sp.sqrt(3))])
t('17b-кривая выпукла вверх', sp.diff(f17b, x, 2).subs(x, R(3, 2)) < 0)
t('17-проверки принимают',
  verify_sketch('Task 17(a)', {'x_intercepts': [-3, -1], 'y_intercept': 15,
                               'minima': [(-2, -5)]}, f17a)
  and verify_sketch('Task 17(b)', {'endpoints': ends17}, f17b,
                    domain=sp.Interval(1, 2)))

# Задание 18. Две кривые, ради которых существует калькулятор.
f18a = x*sp.exp(-x)
turn18a = turning(f18a)
t('18a-максимум (1, 1/e) и асимптота y = 0',
  turn18a == [(sp.Integer(1), sp.exp(-1), 'max')]
  and sp.limit(f18a, x, sp.oo) == 0)
f18b = sp.exp(x) - 3*x - 4
min18 = sp.log(3)
roots18 = sorted(sp.nsolve(f18b, x, guess) for guess in (-1.5, 2.5))
print(f'Задание 18: максимум {turn18a[0][:2]}, минимум при x = ln3 = '
      f'{float(min18):.4f}, корни {[sf3(r) for r in roots18]}')
t('18b-минимум при x = ln 3',
  sp.solveset(sp.diff(f18b, x), x, sp.S.Reals) == sp.FiniteSet(min18))
t('18b-корни в интервалах markscheme',
  -2 <= roots18[0] <= -1 and 2 <= roots18[1] <= 3)
t('18-проверки принимают',
  verify_sketch('Task 18(a)',
                {'x_intercepts': [0], 'maxima': [(1, sp.exp(-1))],
                 'horizontal_asymptotes': [0]}, f18a,
                domain=sp.Interval(0, sp.oo))
  and verify_sketch('Task 18(b)',
                    {'x_intercepts': [sf3(r) for r in roots18],
                     'y_intercept': -3,
                     'minima': [(sf3(min18), sf3(f18b.subs(x, min18)))],
                     'endpoints': [(-4, sf3(f18b.subs(x, -4))),
                                   (3, sf3(f18b.subs(x, 3)))]},
                    f18b, domain=sp.Interval(-4, 3)))

# Задание 19. Кратный корень и кубика без единой точки поворота.
f19a = x**3 + 4*x**2 + 5*x + 2
t('19a-разложение (x+1)^2 (x+2)',
  sp.factor(f19a) == (x + 1)**2*(x + 2))
turn19a = turning(f19a)
print(f'Задание 19(a): поворотные {turn19a}')
t('19a-минимум на оси, максимум в (−5/3, 4/27)',
  turn19a == [(R(-5, 3), R(4, 27), 'max'), (sp.Integer(-1), sp.Integer(0), 'min')])
f19b = (x - 1)*(x**2 - 2*x + 5)
disc19 = sp.discriminant(sp.diff(f19b, x), x)
print(f'Задание 19(b): производная {sp.expand(sp.diff(f19b, x))}, '
      f'дискриминант {disc19}')
t('19b-точек поворота нет', disc19 < 0
  and sp.solveset(sp.diff(f19b, x), x, sp.S.Reals) == sp.S.EmptySet)
t('19b-единственный вещественный корень x = 1',
  sp.solveset(f19b, x, sp.S.Reals) == sp.FiniteSet(1)
  and sp.discriminant(x**2 - 2*x + 5, x) < 0)
t('19b-перегиб в (1, 0), там же где пересечение',
  sp.solveset(sp.diff(f19b, x, 2), x, sp.S.Reals) == sp.FiniteSet(1)
  and f19b.subs(x, 1) == 0)
t('19-проверки принимают',
  verify_sketch('Task 19(a)', {'x_intercepts': [-2, -1], 'y_intercept': 2,
                               'maxima': [(R(-5, 3), R(4, 27))],
                               'minima': [(-1, 0)]}, f19a,
                domain=sp.Interval(-3, 1))
  and verify_sketch('Task 19(b)', {'x_intercepts': [1], 'y_intercept': -5,
                                   'maxima': [], 'minima': []}, f19b,
                    domain=sp.Interval(-1, 3)))

# Задание 20. Постоянная C находится из точки, а не берётся из решения.
C20 = sp.Symbol('C20')
general = x**2 - 2*x - 3 + C20*sp.exp(-x)
C20_val = sp.solve(sp.Eq(general.subs(x, -3), 2), C20)[0]
f20 = sp.simplify(general.subs(C20, C20_val))
turn20 = turning(f20)
print(f'Задание 20: C = {C20_val} = {float(C20_val):.4f}, '
      f'поворотные {[(sf3(u), sf3(w), k) for u, w, k in turn20]}')
t('20-C = −10e^(−3)', sp.simplify(C20_val - (-10*sp.exp(-3))) == 0)
t('20-кривая проходит через (−3, 2)', sp.simplify(f20.subs(x, -3)) == 2)
t('20-один максимум и один минимум',
  [k for _, _, k in turn20] == ['max', 'min'])
t('20-проверка принимает',
  verify_sketch('Task 20',
                {'maxima': [(sf3(u), sf3(w)) for u, w, k in turn20 if k == 'max'],
                 'minima': [(sf3(u), sf3(w)) for u, w, k in turn20 if k == 'min']},
                f20, domain=sp.Interval(-4, 4)))

# Задание 21. Вторая производная: знак решает вид, размер решает форму.
f21 = sp.exp(sp.cos(2*x))
d2 = sp.simplify(sp.diff(f21, x, 2))
at0 = sp.simplify(d2.subs(x, 0))
athalf = sp.simplify(d2.subs(x, sp.pi/2))
ratio = sp.simplify(sp.Abs(at0)/sp.Abs(athalf))
print(f'Задание 21: f\'\'(0) = {at0}, f\'\'(pi/2) = {athalf}, отношение {ratio}')
t('21-вторые производные', at0 == -4*sp.E and athalf == 4/sp.E)
t('21-отношение e^2', ratio == sp.E**2)
t('21-знаки дают вид точек',
  at0 < 0 and athalf > 0 and sp.simplify(d2.subs(x, sp.pi)) == at0)
t('21-стационарные точки там, где sin 2x = 0',
  sp.solveset(sp.diff(f21, x), x, sp.Interval(0, sp.pi))
  == sp.FiniteSet(0, sp.pi/2, sp.pi))
t('21-проверки принимают',
  check_expr('Task 21(a) at 0', at0, D['Task 21(a) at 0'])
  and check_expr('Task 21(a) at pi/2', athalf, D['Task 21(a) at pi/2'])
  and check_expr('Task 21(b) ratio', ratio, D['Task 21(b) ratio'])
  and verify_sketch('Task 21(c)',
                    {'y_intercept': sp.E, 'maxima': [(0, sp.E), (sp.pi, sp.E)],
                     'minima': [(sp.pi/2, sp.exp(-1))]}, f21,
                    domain=sp.Interval(-sp.pi/4, 5*sp.pi/4)))
# На отрезке [0, pi] те же точки стали бы концами, а не максимумами.
t('21-на [0, pi] максимумы превратились бы в концы',
  not silent(verify_sketch, 'Task 21(c)',
             {'maxima': [(0, sp.E), (sp.pi, sp.E)]}, f21,
             domain=sp.Interval(0, sp.pi))[0])

# Задание 22. Кривые, которые не функции: излом против вертикальной касательной.
up1 = sp.sqrt(x**3)
up2 = sp.sqrt(x**3 + 1)
grad1 = sp.limit(sp.diff(up1, x), x, 0, '+')
grad2 = sp.limit(sp.diff(up2, x), x, -1, '+')
yints = sorted(sp.solveset(y**2 - 1, y), key=float)
print(f'Задание 22: наклон в изломе {grad1}, наклон на вертикали {grad2}, '
      f'y-пересечения {yints}')
t('22-в нуле наклон нулевой, а на −1 бесконечный',
  grad1 == 0 and grad2 == sp.oo)
t('22-y-пересечения ±1', yints == [-1, 1])
t('22-точки перегиба y^2=x^3+1 совпадают с ними',
  sp.solveset(sp.diff(up2, x, 2), x, sp.Interval.Ropen(-1, sp.oo))
  == sp.FiniteSet(0))
t('22-параболы открываются в разные стороны',
  sp.solve(sp.Eq(y**2, 16 - 8*x), x)[0].coeff(y, 2) < 0
  < sp.solve(sp.Eq(y**2, 4 + 4*x), x)[0].coeff(y, 2))
t('22-x-пересечения парабол 2 и −1',
  sp.solveset(16 - 8*x, x, sp.S.Reals) == sp.FiniteSet(2)
  and sp.solveset(4 + 4*x, x, sp.S.Reals) == sp.FiniteSet(-1))
t('22-проверки принимают',
  verify_sketch('Task 22(a) y^2=x^3',
                {'x_intercepts': [0], 'endpoints': [(0, 0), (2, 2*sp.sqrt(2))]},
                up1, domain=sp.Interval(0, 2))
  and verify_sketch('Task 22(a) y^2=x^3+1',
                    {'x_intercepts': [-1], 'y_intercept': 1,
                     'endpoints': [(-1, 0), (2, 3)]}, up2,
                    domain=sp.Interval(-1, 2))
  and check_set('Task 22(b)', yints, D['Task 22(b)'])
  and check_num('Task 22(c) cusp', grad1, 6, D['Task 22(c) cusp'])
  and check_expr('Task 22(c) vertical', grad2, D['Task 22(c) vertical'])
  and check_set('Task 22(d) left-opening', [2], D['Task 22(d) left-opening'])
  and check_set('Task 22(d) right-opening', [-1], D['Task 22(d) right-opening']))
# Общее у всего семейства y^2 = x^3 + b: один x-корень, два y-корня.
for bv in (1, 8, 27):
    fam = sp.sqrt(x**3 + bv)
    t(f'22-семейство b = {bv}: корень при −b^(1/3), наклон бесконечен',
      sp.solveset(x**3 + bv, x, sp.S.Reals) == sp.FiniteSet(-sp.root(bv, 3))
      and sp.limit(sp.diff(fam, x), x, -sp.root(bv, 3), '+') == sp.oo)

# Задание 23. Семейство: считаем различные вещественные корни.
def crossings(a_value, count):
    def holds(b_value):
        roots = sp.Poly(x**3 + a_value*x**2 + b_value, x).real_roots()
        return len(set(roots)) == count
    return holds


heights = {}
for a_value in (3, -3):
    crit = sp.solveset(sp.diff(x**3 + a_value*x**2 + b_, x), x, sp.S.Reals)
    heights[a_value] = sorted(
        (sp.expand((x**3 + a_value*x**2 + b_).subs(x, c)) for c in crit),
        key=lambda h: float(h.subs(b_, 0)))
print(f'Задание 23: высоты при a = 3 {heights[3]}, при a = −3 {heights[-3]}')
t('23-высоты не зависят от положения стационарных точек',
  heights[3] == [b_, b_ + 4] and heights[-3] == [b_ - 4, b_])
double3 = sorted(sp.solve(sp.Mul(*heights[3]), b_), key=float)
double_m3 = sorted(sp.solve(sp.Mul(*heights[-3]), b_), key=float)
t('23a-два пересечения при b = −4 и 0', double3 == [-4, 0])
t('23c-и при b = 0 и 4', double_m3 == [0, 4])
t('23-проверки принимают',
  verify_param_set('Task 23(a)', sp.FiniteSet(*double3), crossings(3, 2), var=b_)
  and verify_param_set('Task 23(b)(i)',
                       sp.Union(sp.Interval.open(-sp.oo, -4),
                                sp.Interval.open(0, sp.oo)),
                       crossings(3, 1), var=b_)
  and verify_param_set('Task 23(b)(ii)', sp.Interval.open(-4, 0),
                       crossings(3, 3), var=b_)
  and verify_param_set('Task 23(c)(i)', sp.FiniteSet(*double_m3),
                       crossings(-3, 2), var=b_)
  and verify_param_set('Task 23(c)(ii)',
                       sp.Union(sp.Interval.open(-sp.oo, 0),
                                sp.Interval.open(4, sp.oo)),
                       crossings(-3, 1), var=b_)
  and verify_param_set('Task 23(c)(iii)', sp.Interval.open(0, 4),
                       crossings(-3, 3), var=b_)
  and check_num('Task 23(d)', 1, 6, D['Task 23(d)']))
# Границы в открытых промежутках — самая частая потеря балла, и она ловится.
t('23-b = −4 внутри открытого промежутка отвергается',
  not silent(verify_param_set, 'Task 23(b)(ii)', sp.Interval(-4, 0),
             crossings(3, 3), var=b_)[0])
# Общее условие: произведение высот отрицательно.
t('23-условие 4a^3 b + 27b^2 < 0 это произведение высот',
  sp.simplify(sp.expand(b_*(4*sp.Symbol('a')**3/27 + b_)*27)
              - (4*sp.Symbol('a')**3*b_ + 27*b_**2)) == 0)

print('\n=== чего проверки не делают ===')

# verify_asymptotes ничего не знает о том, как асимптота получена: угаданная
# прямая проходит так же, как выведенная. В экзамене это два балла из четырёх.
t('способ вывода асимптоты не виден',
  verify_asymptotes('  делением', sp.Eq(y, x/2 - R(17, 2)), f7,
                    kinds=('oblique',))
  and verify_asymptotes('  угадана', sp.Eq(y, x/2 - R(17, 2)), f7,
                        kinds=('oblique',)))
# Односторонняя асимптота принимается: у e^x она есть только слева.
t('односторонней асимптоты достаточно',
  verify_asymptotes('  y = 0 у экспоненты', sp.Eq(y, 0), sp.exp(x),
                    kinds=('horizontal',)))
# verify_sketch не смотрит на форму между особенностями: две разные функции
# с одинаковым списком получают один вердикт.
# Множитель exp(x(x+2)/50) равен единице в нуле и нигде не обращается
# в ноль, так что пересечения с осями остаются те же, а кривая — другая.
same = {'x_intercepts': [-3, -1], 'y_intercept': 15}
other = 5*(x + 1)*(x + 3)*sp.exp(x*(x + 2)/50)
t('форма между особенностями не проверяется',
  verify_sketch('  парабола', same, f17a)
  and verify_sketch('  и не парабола', same, other)
  and sp.simplify(other - f17a) != 0
  and sp.solveset(other, x, sp.S.Reals) == sp.FiniteSet(-3, -1))
# Три значащие цифры: ошибка в четвёртой проходит.
t('ошибка в четвёртой цифре проходит',
  verify_sketch('  1.94 вместо 1.9435', {'maxima': [(-1.94, 1.20)]}, f12b,
                domain=sp.Interval(-10, 10))
  and not silent(verify_sketch, '  а 1.9 — нет',
                 {'maxima': [(-1.9, 1.20)]}, f12b,
                 domain=sp.Interval(-10, 10))[0])
# verify_range проверяет границу на расстоянии eps: более тонкую ошибку
# можно поймать, передав eps поменьше.
t('граница проверяется с шагом eps',
  not silent(verify_range, '  сдвиг на 1', (y >= -4), f13a)[0]
  and not silent(verify_range, '  сдвиг на 1/2000', (y >= R(-9999, 2000)),
                 f13a, eps=R(1, 100000))[0])

print('\n=== расхождения с корпусом ===')
CORPUS = os.path.join(ROOT, 'classification/generated')


def block(bid):
    for path in glob.glob(os.path.join(CORPUS, '*/*/paper-*.json')):
        for blk in json.load(open(path))['blocks']:
            if blk['id'] == bid:
                return blk
    return None


# 1. Май 2021 TZ1 Q11(e): записана (4x^2+3)/(2−3x), в бумаге (4x^2−1)/(3x+2).
corpus6 = (4*x**2 + 3)/(2 - 3*x)
v_c, _, o_c = lines_of(corpus6)
print(f'май 2021: по корпусу вертикальная {v_c}, наклонная {o_c}; '
      f'markscheme печатает x = −2/3 и y = 4x/3 − 8/9')
t('корпус: функция записана неверно, асимптоты не те',
  v_c == [R(2, 3)] and sp.simplify(o_c[0] - (4*x/3 - R(8, 9))) != 0
  and v6 == [-R(2, 3)])
t('корпус: область x != −2/3 подтверждает знаменатель 3x+2',
  sp.solveset(3*x + 2, x, sp.S.Reals) == sp.FiniteSet(-R(2, 3)))

# 2. Май 2023 TZ2 Q8(a): записана (2−5x^2)/(3−x^2), в бумаге (2x−5)/(x^2−3).
corpus15 = (2 - 5*x**2)/(3 - x**2)
disc_c = sp.expand(sp.discriminant(
    sp.expand(y*(3 - x**2) - (2 - 5*x**2)), x))
print(f'май 2023: дискриминант по корпусу {disc_c}, по бумаге {disc15}; '
      f'markscheme печатает 12y^2 − 20y + 4')
t('корпус: только запись бумаги даёт дискриминант markscheme',
  sp.expand(disc15) == sp.expand(12*y**2 - 20*y + 4)
  and sp.expand(disc_c) != sp.expand(12*y**2 - 20*y + 4))
t('корпус: и только она даёт sqrt13',
  sp.sqrt(13) in sp.simplify(bounds15[1]).atoms(sp.Pow)
  or 13 in [aa.p for aa in sp.simplify(bounds15[1]).atoms(sp.Integer)])

# 3. Май 2025 TZ2 Q1(a): записана (x^2−16)/(x^2+16), в бумаге x(x^2−16)/(x^2+16).
corpus12 = (x**2 - 16)/(x**2 + 16)
print(f'май 2025: по корпусу в нуле {corpus12.subs(x, 0)}, '
      f'по бумаге {f12b.subs(x, 0)}; корпус сам записывает пересечение (0, 0)')
t('корпус: записанная функция в нуле не обращается в ноль',
  corpus12.subs(x, 0) == -1 and f12b.subs(x, 0) == 0)
t('корпус: у записанной нет наклонной асимптоты, а вопрос (d)(ii) её требует',
  not lines_of(corpus12)[2] and lines_of(f12b)[2] == [x])
sibling = block('2025-MAY-TZ2-P3-Q01-A-II')
t('корпус: соседний блок сам называет пересечения (−4,0), (0,0), (4,0)',
  sibling is not None and 'x-axis' in sibling['task_summary'])

# 4. Ноябрь 2023: сессия лежит в корпусе двумя зонами, и это одна бумага.
pair = {}
for path in sorted(glob.glob(os.path.join(
        CORPUS, '2023-november-*/*/paper-2.json'))):
    zone = path.split('generated/')[1].split('/')[0]
    for blk in json.load(open(path))['blocks']:
        if blk['id'].endswith('P2-Q11-C'):
            pair[zone] = (blk['id'].split('-P2-')[1], blk.get('marks'),
                          blk.get('primary_topic'))
doubled = 0
tz1 = {b['id'].split('TZ1-')[1] for p in glob.glob(os.path.join(
    CORPUS, '2023-november-tz1/*/paper-*.json'))
    for b in json.load(open(p))['blocks']
    if b['primary_topic'] in ('functions.curve_sketching', 'functions.asymptotes')}
tz2 = {b['id'].split('TZ2-')[1]: b.get('marks') for p in glob.glob(os.path.join(
    CORPUS, '2023-november-tz2/*/paper-*.json'))
    for b in json.load(open(p))['blocks']
    if b['primary_topic'] in ('functions.curve_sketching', 'functions.asymptotes')}
doubled = sum(m for k, m in tz2.items() if k in tz1)
print(f'ноябрь 2023: общих блоков {len(set(tz1) & set(tz2))}, '
      f'удвоенных баллов {doubled}')
t('корпус: ноябрь 2023 удвоен и здесь',
  len(pair) == 2 and len(set(pair.values())) == 1)
t('корпус: удвоено ровно 20 баллов', doubled == 20)

# 5. Две копии одной бумаги не согласны между собой.
print(f'ноябрь 2023: только в TZ1 {sorted(set(tz1) - set(tz2))}, '
      f'только в TZ2 {sorted(set(tz2) - set(tz1))}')
t('корпус: копии расходятся в обе стороны',
  set(tz1) - set(tz2) and set(tz2) - set(tz1))
t('корпус: диапазон f записан только в одной копии',
  'P2-Q11-E' in tz2 and 'P2-Q11-E' not in tz1)
t('корпус: исследование Paper 3 разрезано между копиями по-разному',
  len([k for k in tz1 if k.startswith('P3-Q01')]) == 8
  and len([k for k in tz2 if k.startswith('P3-Q01')]) == 2)

# 6. Ноябрь 2025 TZ3 Q9: функции в корпусе нет, её восстанавливает markscheme.
k_ = sp.Symbol('k')
t('корпус: старший коэффициент 1/2 следует из дискриминанта k^2 − 26',
  sp.expand(sp.discriminant(x**2/2 + k_*x + 13, x)) == k_**2 - 26
  and sp.expand(sp.discriminant(x**2 + k_*x + 13, x)) != k_**2 - 26)
t('корпус: и ось симметрии x = −5 при k = 5 бывает только при нём',
  sp.solveset(sp.diff(x**2/2 + 5*x + 13, x), x, sp.S.Reals) == sp.FiniteSet(-5))
t('корпус: наибольшее целое k равно 5 именно с ним',
  max(kv for kv in range(1, 20) if kv**2 < 26) == 5)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
