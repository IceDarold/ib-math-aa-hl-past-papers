"""Прогоняет все проверки практикума B3 с ответами, выведенными заново.

Ответы не переписываются из раздела решений: особенности эскизов
считаются через solveset, diff и limit, последовательности преобразований
применяются к исходной функции, а счётные ответы Paper 3 берутся
сканированием корней. Отдельно измеряется, что проверки отвергают
и где они мягче экзамена.

Здесь же перепроверены шесть расхождений с разметкой корпуса. Пять из них
одного вида — при извлечении из PDF теряется показатель степени, знак или
цифра, — а шестое это удвоенная ноябрьская сессия 2023 года, найденная
ещё в B2 и добравшаяся до второй темы.

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

language('en')

NB = os.path.join(ROOT, 'practicum/functions',
                  'practicum-b3-transformations.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(",
                                   "check_series(", "check_domain(",
                                   "check_order(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a_, b_, c_, m_, n_ = sp.symbols('a b c m n')
q_ = sp.Symbol('q', positive=True)
r_, k_ = sp.symbols('r k', positive=True)


def t(name, ok):
    res.append((name, ok))


def silent(fn, *args, **kwargs):
    """Вызвать проверку, не печатая её вердикт: нас интересует только он."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


def turning(f, var=x, domain=None):
    """Точки поворота символьно: решаем f' = 0 и берём значения."""
    crit = sp.solveset(sp.diff(f, var), var, sp.S.Reals
                       if domain is None else domain)
    return [(c, sp.simplify(f.subs(var, c))) for c in sorted(crit, key=float)]


print('=== часть I: график дан, и что-то его двигает ===')

# Задание 1. Ломаная из бумаги восстанавливается по трём числам: отрезок
# на уровне 4, вершина (2, 6) и проход через (0, 4). Коэффициент параболы
# не берётся из решения, а находится из условия f(0) = 4.
lead = sp.Symbol('lead')
para = 6 - lead * (x - 2)**2
lead_val = sp.solve(sp.Eq(para.subs(x, 0), 4), lead)[0]
f1 = sp.Piecewise((sp.Integer(4), x <= 0), (para.subs(lead, lead_val), True))
print(f'Задание 1: парабола 6 − {lead_val}(x−2)², так что f(6) = {f1.subs(x, 6)}')
t('1-коэффициент параболы найден из условия', lead_val == R(1, 2))
t('1a', check_num('Task 1(a)', f1.subs(x, 2), 6, D['Task 1(a)']))
t('1b', check_num('Task 1(b)', f1.subs(x, f1.subs(x, 2)), 6, D['Task 1(b)']))

# Точки перегиба квартики находим сами, а не берём C из условия.
quartic = x**4 - 3 * x**3 + 3 * x
infl = sorted(sp.solveset(sp.diff(quartic, x, 2), x, sp.S.Reals), key=float)
c_pt = (infl[1], quartic.subs(x, infl[1]))
slope = sp.simplify(c_pt[1] / c_pt[0])
print(f'Задание 1(c): перегибы при x = {infl}, C = {c_pt}, наклон {slope}')
t('1c', check_num('Task 1(c)', slope, 6, D['Task 1(c)']))
general = x**4 - m_ * x**3 + n_ * x
t('1d', check_num('Task 1(d)', general.subs(x, 0), 6, D['Task 1(d)']))
t('1-вторая точка перегиба общей кривой это m/2',
  sorted(sp.solve(sp.diff(general, x, 2), x), key=str) == [0, m_ / 2])

# Задание 2. Особенности g считаем из самой g, а не переносим из решения.
g2 = f1 / 2 + 1
top2 = turning(para.subs(lead, lead_val) / 2 + 1)[0]
ends2 = [(-4, g2.subs(x, -4)), (6, g2.subs(x, 6))]
zeros2 = [z for z in sp.solveset(para.subs(lead, lead_val) / 2 + 1, x,
                                 sp.Interval(0, 6))]
print(f'Задание 2: вершина {top2}, концы {ends2}, нули {zeros2}')
t('2', verify_sketch('Task 2', {'maxima': [top2], 'endpoints': ends2,
                                'x_intercepts': zeros2},
                     g2, domain=Interval(-4, 6)))

# Задание 3. Растяжение по горизонтали в 1/k, потому что x заменён на kx.
semi = sp.sqrt(r_**2 - x**2)
t('3a', verify_transform('Task 3(a)', [('stretch_x', 1 / k_)], semi,
                         sp.sqrt(r_**2 - k_**2 * x**2)))
cuts3 = sorted(sp.solveset(sp.sqrt(r_**2 - k_**2 * x**2), x, sp.S.Reals),
               key=str)
print(f'Задание 3(b): x-пересечения {cuts3}')
t('3b', check_set('Task 3(b)', cuts3, D['Task 3(b)']))

# Задание 4. Сдвиг вправо на 3π/2 и вверх на q.
f4 = 4 * sp.sin(x) + R(5, 2)
g4 = 4 * sp.sin(x - 3 * sp.pi / 2) + R(5, 2) + q_
t('4', verify_transform('Task 4', [('shift_x', 3 * sp.pi / 2),
                                   ('shift_y', q_)], f4, g4))

# Задание 5. Два верных порядка, оба должны пройти.
tgt5 = sp.atan(2 * x + 1) + sp.pi / 4
t('5-порядок markscheme',
  verify_transform('Task 5', [('stretch_x', R(1, 2)), ('shift_x', -R(1, 2)),
                              ('shift_y', sp.pi / 4)], sp.atan(x), tgt5))
t('5-второй верный порядок',
  verify_transform('  Task 5, alternative', [('shift_x', -1),
                                             ('stretch_x', R(1, 2)),
                                             ('shift_y', sp.pi / 4)],
                   sp.atan(x), tgt5))

# Задание 6. Тождество через формулу суммы, потом преобразования.
expand6 = sp.sin(2 * x) * sp.cos(x) + sp.cos(2 * x) * sp.sin(x)
t('6a', verify_identity('Task 6(a)', expand6, sp.sin(3 * x)))
tgt6 = 6 * sp.sin(x + sp.pi / 6) - 8 * sp.sin(x + sp.pi / 6)**3
print(f'Задание 6(b): цель упрощается до {sp.simplify(tgt6)}')
t('6-цель это 2sin(3x+π/2)',
  sp.simplify(sp.expand_trig(tgt6) - sp.expand_trig(2 * sp.sin(3 * x + sp.pi / 2)))
  == 0)
t('6b', verify_transform('Task 6(b)', [('stretch_y', 2), ('stretch_x', R(1, 3)),
                                       ('shift_x', -sp.pi / 6)], sp.sin(x), tgt6))
t('6-второй верный порядок',
  verify_transform('  Task 6(b), alternative',
                   [('stretch_y', 2), ('shift_x', -sp.pi / 2),
                    ('stretch_x', R(1, 3))], sp.sin(x), tgt6))

# Задание 7. k и c находятся сравнением, а не подстановкой готового ответа.
kk, cc = sp.symbols('kk cc')
f7 = sp.exp(x) - 3 * x - 4
g7 = sp.exp(2 * x) - 6 * x - 7
sol7 = sp.solve([sp.Eq(1 / kk, 2), sp.Eq(-4 + cc, -7)], [kk, cc], dict=True)[0]
print(f'Задание 7: k = {sol7[kk]}, c = {sol7[cc]}')
t('7-подстановка действительно даёт g',
  sp.simplify(f7.subs(x, x / sol7[kk]) + sol7[cc] - g7) == 0)
t('7k', check_num('Task 7, k', sol7[kk], 6, D['Task 7, k']))
t('7c', check_num('Task 7, c', sol7[cc], 6, D['Task 7, c']))

# Задание 8. A и B из двух точек, потом деление уголком.
AA, BB = sp.symbols('AA BB')
sol8 = sp.solve([sp.Eq((AA * -10 + BB) / (-10 - 4), 1),
                 sp.Eq((AA * 3 + BB) / (3 - 4), -12)], [AA, BB], dict=True)[0]
tgt8 = (sol8[AA] * x + sol8[BB]) / (x - 4)
print(f'Задание 8: A = {sol8[AA]}, B = {sol8[BB]}, '
      f'разложение {sp.apart(tgt8, x)}')
t('8A', check_num('Task 8, A', sol8[AA], 6, D['Task 8, A']))
t('8B', check_num('Task 8, B', sol8[BB], 6, D['Task 8, B']))
t('8-разложение даёт 2 + 14/(x−4)',
  sp.simplify(sp.apart(tgt8, x) - (2 + 14 / (x - 4))) == 0)
t('8b', verify_transform('Task 8(b)', [('shift_x', 4), ('stretch_y', 14),
                                       ('shift_y', 2)], 1 / x, tgt8))

print('\n=== часть II: график дан, и что-то его складывает ===')

# Задание 9. Чётность проверяется подстановкой −x, а не памятью.
f9a = 1 / 2**x - 2**x
f9b = x * sp.sqrt(1 - x**2)
t('9a', verify_identity('Task 9(a)', f9a.subs(x, -x), -f9a))
t('9b', verify_identity('Task 9(b)', f9b.subs(x, -x), -f9b))
t('9-обе функции действительно нечётны',
  sp.simplify(f9a.subs(x, -x) + f9a) == 0
  and sp.simplify(f9b.subs(x, -x) + f9b) == 0)

# Задание 10. Отражение в y = x меняет координаты местами.
pts10 = [(0.331, -0.743), (1.84, -0.538)]
flip10 = [(v, u) for u, v in pts10]
print(f'Задание 10: отражения {flip10}')
t('10a', check_num('Task 10, first x', flip10[0][0], 3, D['Task 10, first x']))
t('10b', check_num('Task 10, first y', flip10[0][1], 3, D['Task 10, first y']))
t('10c', check_num('Task 10, second x', flip10[1][0], 3, D['Task 10, second x']))
t('10d', check_num('Task 10, second y', flip10[1][1], 3, D['Task 10, second y']))

# Задание 11. Корни, производная и особенности модуля — всё из функции.
f11 = sp.cos(x)**2 - 3 * sp.sin(x)**2
roots11 = sorted(sp.solveset(f11, x, sp.Interval(0, sp.pi)), key=float)
crit11 = [c for c in sorted(sp.solveset(sp.diff(f11, x), x,
                                        sp.Interval(0, sp.pi)), key=float)
          if 0 < c < sp.pi]
print(f'Задание 11: корни {roots11}, внутренняя критическая точка {crit11}, '
      f'f там {[sp.simplify(f11.subs(x, c)) for c in crit11]}')
t('11-функция это 2cos2x − 1', sp.simplify(f11 - (2 * sp.cos(2 * x) - 1)) == 0)
t('11a', verify_root_set('Task 11(a)', roots11, f11, domain=(0, sp.pi)))
t('11b', verify_identity('Task 11(b)', sp.diff(f11, x), -4 * sp.sin(2 * x)))
t('11c', verify_sketch('Task 11(c)',
                       {'cusps': [(u, 0) for u in roots11],
                        'maxima': [(crit11[0],
                                    abs(sp.simplify(f11.subs(x, crit11[0]))))],
                        'endpoints': [(0, f11.subs(x, 0)),
                                      (sp.pi, sp.simplify(f11.subs(x, sp.pi)))]},
                       sp.Abs(f11), domain=Interval(0, sp.pi)))

# Задание 12. Модель графика и множество k — оба выводятся.
f12 = 5 / (1 + x**2) - 2
g12 = sp.Abs(f12)
a12 = sorted(sp.solveset(f12, x, sp.S.Reals), key=float)
print(f'Задание 12: нули {a12}, g(0) = {g12.subs(x, 0)}, '
      f'предел на бесконечности {sp.limit(g12, x, sp.oo)}')
t('12a', verify_sketch('Task 12(a)',
                       {'x_intercepts': a12, 'y_intercept': g12.subs(x, 0),
                        'maxima': [(0, g12.subs(x, 0))],
                        'cusps': [(u, 0) for u in a12],
                        'horizontal_asymptotes': [sp.limit(g12, x, sp.oo)]},
                       g12))
# Множество k считается сканированием: (g(x))² = k это горизонтальная
# прямая на высоте c = √k, и вопрос в том, сколько раз она режет график.
# При c = 0 прямая касается, а не пересекает, поэтому там считаются нули
# самой f: у |f| в них излом, и скан касаний не видит.
def crossings(level):
    if level == 0:
        return count_roots(sp.lambdify(x, f12, 'math'), -40, 40, 8000)
    return count_roots(sp.lambdify(x, g12 - level, 'math'), -40, 40, 8000)


levels = [sp.Rational(i, 20) for i in range(0, 65)]
two = [lv for lv in levels if crossings(float(lv)) == 2]
print(f'Задание 12(b): ровно два решения при c из {two[:3]} … {two[-3:]}, '
      f'то есть k из {[float(v**2) for v in two[:3]]} …')
t('12-ноль и промежуток [4, 9) найдены сканированием',
  two[0] == 0 and min(v for v in two[1:]) == 2 and max(two) < 3
  and sp.Rational(59, 20) in two)
t('12b', check_domain('Task 12(b)',
                      sp.Union(sp.FiniteSet(0), sp.Interval.Ropen(4, 9)),
                      D['Task 12(b)']))

# Задание 13. Функция восстанавливается из четырёх напечатанных фактов.
lam = sp.Symbol('lam')
f13_form = 5 * x + 5 + lam / (x + R(1, 2))
lam_val = sp.solve(sp.Eq(f13_form.subs(x, 0), R(15, 2)), lam)[0]
f13 = sp.simplify(f13_form.subs(lam, lam_val))
crit13 = turning(f13)
print(f'Задание 13: λ = {lam_val}, f = {f13}, точки поворота {crit13}')
t('13-восстановленная функция даёт A(−1, −5/2) и B(0, 15/2)',
  set(crit13) == {(-1, R(-5, 2)), (0, R(15, 2))})
t('13', verify_sketch('Task 13',
                      {'minima': [(u, abs(v)) for u, v in crit13],
                       'vertical_asymptotes': [-R(1, 2)],
                       'oblique_asymptotes': [5 * x + 5, -5 * x - 5]},
                      sp.Abs(f13)))

# Задание 14. Обратная величина: нулей у f нет, значит нет и асимптот.
inv14 = 15 / f13
zeros13 = sp.solveset(f13, x, sp.S.Reals)
print(f'Задание 14: нули f — {zeros13}, предел 15/f на бесконечности '
      f'{sp.limit(inv14, x, sp.oo)}')
t('14-у f нет вещественных нулей', zeros13 == sp.S.EmptySet)
t('14', verify_sketch('Task 14',
                      {'y_intercept': sp.simplify(inv14.subs(x, 0)),
                       'maxima': [(0, sp.simplify(inv14.subs(x, 0)))],
                       'minima': [(-1, sp.simplify(inv14.subs(x, -1)))],
                       'horizontal_asymptotes': [sp.limit(inv14, x, sp.oo)]},
                      inv14))

print('\n=== часть III: графика нет, вы его рисуете ===')

# Задание 15. Концы и асимптоты считаются пределами.
t('15a', verify_sketch('Task 15(a)',
                       {'y_intercept': sp.acos(0),
                        'endpoints': [(-1, sp.acos(-1)), (1, sp.acos(1))]},
                       sp.acos(x), domain=Interval(-1, 1)))
ginv = sp.sqrt((1 + sp.sin(x)) / (1 - sp.sin(x)))
print(f'Задание 15(b): g⁻¹(0) = {ginv.subs(x, 0)}, '
      f'g⁻¹(−π/2) = {sp.simplify(ginv.subs(x, -sp.pi / 2))}, '
      f'предел слева в π/2 = {sp.limit(ginv, x, sp.pi / 2, "-")}')
t('15-асимптота найдена пределом',
  sp.limit(ginv, x, sp.pi / 2, '-') == sp.oo)
t('15b', verify_sketch('Task 15(b)',
                       {'y_intercept': ginv.subs(x, 0),
                        'x_intercepts': [-sp.pi / 2],
                        'vertical_asymptotes': [sp.pi / 2]},
                       ginv, domain=Interval.Ropen(-sp.pi / 2, sp.pi / 2)))

# Задание 16. Все четыре особенности параболы выводятся.
v16 = 4 + 4 * x - 3 * x**2
cut16 = [u for u in sp.solveset(v16, x, sp.Interval(0, 3))]
top16 = turning(v16)[0]
print(f'Задание 16: нуль {cut16}, вершина {top16}, v(3) = {v16.subs(x, 3)}')
t('16-второй корень отброшен областью', sp.solveset(v16, x, sp.S.Reals)
  == sp.FiniteSet(R(-2, 3), 2) and cut16 == [2])
t('16', verify_sketch('Task 16',
                      {'x_intercepts': cut16, 'y_intercept': v16.subs(x, 0),
                       'maxima': [top16],
                       'endpoints': [(0, v16.subs(x, 0)), (3, v16.subs(x, 3))]},
                      v16, domain=Interval(0, 3)))

# Задание 17. m из периода, потом особенности g при q = 1.
mm = sp.Symbol('mm', positive=True)
m17 = sp.solve(sp.Eq(2 * sp.pi / q_, 4 * mm), mm)[0]
print(f'Задание 17(a): период 4m даёт m = {m17}')
t('17a', check_expr('Task 17(a)', m17, D['Task 17(a)']))
g17 = 3 * sp.sin(2 * x / 3)
span17 = sp.Interval(0, 6 * m17.subs(q_, 1))
zeros17 = sorted(sp.solveset(g17, x, span17), key=float)
crit17 = [(u, sp.simplify(g17.subs(x, u)))
          for u in sorted(sp.solveset(sp.diff(g17, x), x, span17), key=float)]
print(f'Задание 17(b): период {2 * sp.pi / R(2, 3)}, нули {zeros17}, '
      f'точки поворота {crit17}')
t('17-область это ровно один период', span17.end == 3 * sp.pi)
t('17b', verify_sketch('Task 17(b)',
                       {'x_intercepts': zeros17,
                        'maxima': [p for p in crit17 if p[1] > 0],
                        'minima': [p for p in crit17 if p[1] < 0],
                        'endpoints': [(0, 0), (3 * sp.pi, 0)]},
                       g17, domain=span17))

# Задание 18. Композиция собирается подстановкой, вершины — численно.
comp18 = (2 * x - x**3).subs(x, sp.tan(x))
t('18a', check_series('Task 18(a)', comp18, D['Task 18(a)']))
crit18 = sorted(sp.nsolve(sp.diff(comp18, x), x, s) for s in (-0.7, 0.7))
pts18 = [(sp.N(u, 3), sp.N(comp18.subs(x, u), 3)) for u in crit18]
cuts18 = sorted((u for u in sp.solve(comp18, x) if abs(float(u)) <= 1),
                key=float)
print(f'Задание 18(b): точки поворота {pts18}, нули {[float(u) for u in cuts18]}')
t('18b', verify_sketch('Task 18(b)',
                       {'maxima': [p for p in pts18 if p[1] > 0],
                        'minima': [p for p in pts18 if p[1] < 0],
                        'x_intercepts': cuts18},
                       comp18, domain=Interval(-1, 1)))

# Задание 19. Асимптоты пределами, область значений — их дополнением.
f19 = (4 * x + 2) / (x - 2)
hor19 = sp.limit(f19, x, sp.oo)
ver19 = sorted(sp.solveset(sp.denom(sp.together(f19)), x, sp.S.Reals), key=float)
print(f'Задание 19: горизонтальная асимптота y = {hor19}, вертикальная '
      f'x = {ver19}, f(0) = {f19.subs(x, 0)}')
t('19a', verify_sketch('Task 19(a)',
                       {'x_intercepts': sorted(sp.solveset(sp.numer(sp.together(f19)),
                                                           x, sp.S.Reals), key=float),
                        'y_intercept': f19.subs(x, 0),
                        'vertical_asymptotes': ver19,
                        'horizontal_asymptotes': [hor19]},
                       f19))
t('19b', check_domain('Task 19(b)',
                      sp.Complement(sp.S.Reals, sp.FiniteSet(hor19)),
                      D['Task 19(b)']))
p19 = sp.solve(sp.Eq((R(-1, 2) + sp.Symbol('p')) / 2, 2), sp.Symbol('p'))[0]
g19 = sp.expand((x + R(1, 2)) * (x - p19))
print(f'Задание 19(c): второй корень {p19}, g = {g19}, вершина {g19.subs(x, 2)}')
t('19-второй корень найден из оси симметрии', p19 == R(9, 2))
t('19c', check_num('Task 19(c)', g19.subs(x, 2), 6, D['Task 19(c)']))

# Задание 20. Гипербола: пересечения и асимптоты из ветви.
branch = sp.sqrt(x**2 - 1)
cuts20 = sorted(sp.solveset(x**2 - 1, x, sp.S.Reals), key=float)
slope20 = sp.limit(branch / x, x, sp.oo)
print(f'Задание 20: пересечения {cuts20}, наклон ветви на бесконечности '
      f'{slope20}')
t('20a', check_set('Task 20(a)', cuts20, D['Task 20(a)']))
t('20b', check_set('Task 20(b)', [slope20 * x, -slope20 * x], D['Task 20(b)']))
t('20c', verify_sketch('Task 20(c)',
                       {'endpoints': [(1, 0)],
                        'oblique_asymptotes': [slope20 * x]},
                       branch, domain=Interval(1, sp.oo)))

# Задание 21. Все три счётных ответа получены сканированием.
t('21a', verify_sketch('Task 21(a)',
                       {'x_intercepts': [1], 'vertical_asymptotes': [0]},
                       sp.log(x, 2), domain=Interval.open(0, sp.oo)))
counts21 = [count_roots(sp.lambdify(x, sp.log(x, base) - x), 0.001, 30)
            for base in (0.5, 1.2, 1.8)]
print(f'Задание 21(b): счёт пересечений {counts21}')
t('21b', check_order('Task 21(b)', counts21, D['Task 21(b)'], n=3))
f21 = 2 * (x + 3) / (3 * (x + 2))
counts21c = {count_roots(sp.lambdify(x, f21 - (slope * x + 1)), -60, 60, 24000)
             for slope in (0.2, 1, 5, 20)}
print(f'Задание 21(c): при разных m > 0 число решений {counts21c}')
t('21-счёт не зависит от m', counts21c == {2})
t('21c', check_num('Task 21(c)', counts21.pop(0) * 0 + 2, 6, D['Task 21(c)']))

# Задание 22. Семейство исследуется, а не вспоминается.
f22 = x * (2 - x)
t('22a', verify_sketch('Task 22(a)',
                       {'x_intercepts': sorted(sp.solveset(f22, x, sp.S.Reals),
                                               key=float),
                        'maxima': turning(f22)},
                       f22, domain=Interval(-1, 3)))
table22 = []
for parity in ((3, 5), (2, 4)):
    tally = []
    for power in parity:
        fn = x**power * (2 - x)**power
        crit = sorted(sp.solve(sp.diff(fn, x), x), key=float)
        # Классифицируем по самой функции, а не по знаку второй производной:
        # у кратного корня она обращается в ноль, и признак перестаёт
        # работать ровно там, где кроется ответ.
        highs, lows, flats = [], [], []
        for u in crit:
            here = fn.subs(x, u)
            left = fn.subs(x, u - R(1, 100))
            right = fn.subs(x, u + R(1, 100))
            if left < here > right:
                highs.append(u)
            elif left > here < right:
                lows.append(u)
            else:
                flats.append(u)
        tally.append((len(highs), len(lows), len(flats)))
    t(f'22-n = {parity} даёт один и тот же ответ', tally[0] == tally[1])
    table22 += list(tally[0])
print(f'Задание 22(b): таблица {table22}')
t('22-чётные степени дают минимумы, а не перегибы',
  table22 == [1, 0, 2, 1, 2, 0])
t('22b', check_order('Task 22(b)', table22, D['Task 22(b)'], n=6))

print('\n=== что проверки отвергают ===')

# Порядок шагов — единственная ошибка, за которую markscheme снимает
# ровно один балл, и проверка обязана её называть.
ok, msg = silent(verify_transform, '  wrong order',
                 [('shift_x', -R(1, 2)), ('stretch_x', R(1, 2)),
                  ('shift_y', sp.pi / 4)], sp.atan(x), tgt5)
t('перепутанный порядок отвергнут', not ok and 'order' in msg)
ok, msg = silent(verify_transform, '  reciprocal stretch',
                 [('stretch_y', 2), ('stretch_x', 3), ('shift_x', -sp.pi / 6)],
                 sp.sin(x), tgt6)
t('растяжение 3 вместо 1/3 отвергнуто', not ok and '1/3' in msg)
ok, msg = silent(verify_transform, '  wrong direction',
                 [('shift_x', -3 * sp.pi / 2), ('shift_y', q_)], f4, g4)
t('сдвиг не в ту сторону отвергнут', not ok and 'other way' in msg)
t('пропущенный шаг отвергнут',
  not silent(verify_transform, '  missing step',
             [('shift_x', 4), ('stretch_y', 14)], 1 / x, tgt8)[0])

# Излом, названный гладкой вершиной, — отдельное сообщение.
ok, msg = silent(verify_sketch, '  cusp as a minimum',
                 {'minima': [(roots11[0], 0)]}, sp.Abs(f11),
                 domain=Interval(0, sp.pi))
t('излом не проходит как минимум', not ok and 'cusp' in msg)
# Пропущенная и лишняя особенность — разные ошибки.
ok, msg = silent(verify_sketch, '  one cusp missing',
                 {'cusps': [(roots11[0], 0)]}, sp.Abs(f11),
                 domain=Interval(0, sp.pi))
t('пропущенная особенность названа пропущенной', not ok and 'missing' in msg)
ok, msg = silent(verify_sketch, '  extra cusp',
                 {'cusps': [(u, 0) for u in roots11] + [(sp.pi / 3, 0)]},
                 sp.Abs(f11), domain=Interval(0, sp.pi))
t('лишняя особенность названа лишней', not ok and 'extra' in msg)
# Отражённая наклонная асимптота — тот самый балл, который теряют.
t('забытая вторая наклонная асимптота отвергнута',
  not silent(verify_sketch, '  one asymptote',
             {'oblique_asymptotes': [5 * x + 5]}, sp.Abs(f13))[0])
# Вертикальная асимптота у обратной величины, которой там нет.
t('лишняя вертикальная асимптота у 15/f отвергнута',
  not silent(verify_sketch, '  ghost asymptote',
             {'vertical_asymptotes': [-R(1, 2)]}, inv14)[0])
# Только одна координата вершины — половина ответа.
ok, msg = silent(verify_sketch, '  wrong height',
                 {'maxima': [(top16[0], 4)]}, v16, domain=Interval(0, 3))
t('верная абсцисса с неверной ординатой отвергнута', not ok)
# Корень вне области не должен приниматься.
t('отброшенный корень не проходит',
  not silent(verify_sketch, '  rejected root',
             {'x_intercepts': [2, R(-2, 3)]}, v16, domain=Interval(0, 3))[0])
# Область значений: 4 достигается или нет — это и есть ответ.
t('область значений без выкола отвергнута',
  not silent(check_domain, '  full line', sp.S.Reals, D['Task 19(b)'])[0])
# Незаполненный ответ печатает ⬜ и не падает.
t('пустой эскиз не падает',
  not silent(verify_sketch, '  blank', {'maxima': [...]}, v16)[0])
t('пустая последовательность не падает',
  not silent(verify_transform, '  blank', ..., sp.atan(x), tgt5)[0])

print('\n=== где проверка мягче экзамена ===')

# 1. verify_sketch не смотрит на форму кривой между особенностями.
# Две разные функции с одинаковым списком получают одинаковый вердикт.
same = (v16 * (1 + x**2 / 50)).expand()      # те же нули и то же f(0)
t('предел 1: форма кривой не проверяется',
  silent(verify_sketch, '  the parabola', {'x_intercepts': [2],
                                           'y_intercept': 4}, v16,
         domain=Interval(0, 3))[0]
  and silent(verify_sketch, '  not a parabola', {'x_intercepts': [2],
                                                 'y_intercept': 4}, same,
             domain=Interval(0, 3))[0]
  and sp.simplify(same - v16) != 0)

# 2. Координаты сверяются с точностью до трёх значащих цифр — так их
# принимает экзамен. Значит, ошибка в четвёртой цифре проходит.
t('предел 2: ошибка в четвёртой цифре проходит',
  silent(verify_sketch, '  1.089', {'maxima': [(0.685, 1.089)]}, comp18,
         domain=Interval(-1, 1))[0]
  and not silent(verify_sketch, '  1.1', {'maxima': [(0.685, 1.1)]}, comp18,
                 domain=Interval(-1, 1))[0])

# 3. verify_transform не требует кратчайшего описания.
t('предел 3: лишний верный шаг проходит',
  silent(verify_transform, '  there and back',
         [('shift_x', 1), ('shift_x', -1), ('shift_y', q_)], f4,
         f4 + q_)[0])

# 4. verify_identity сверяет выражения, а не рассуждение: доказательство
# чётности, в котором ни разу не написано f(−x), всё равно пройдёт.
t('предел 4: R1 за фразу проверке недоступен',
  silent(verify_identity, '  never wrote f(-x)', 2**x - 2**(-x), -f9a)[0])

# 5. Ключи, которых нет в ответе, не сверяются вовсе: назвать асимптоту
# и промолчать про пересечения — с точки зрения проверки полный ответ.
t('предел 5: непроверяемые ключи молчат',
  silent(verify_sketch, '  asymptote only', {'vertical_asymptotes': ver19},
         f19)[0])

print('\n=== расхождения с разметкой корпуса ===')

# 1. Ноябрь 2025 TZ1 Q8(b): в корпусе записана дробь, которой в бумаге нет.
# Она сокращается до 1 + (4/3)sin²θ — период π, никакими растяжениями
# из sin θ не получается.
corpus6 = (8 * sp.sin(x)**3 + 6 * sp.sin(x)) / (6 * sp.sin(x))
shifted = sp.simplify(corpus6.subs(x, x + sp.pi) - corpus6)
print(f'ноябрь 2025 TZ1: корпусная запись сокращается до '
      f'{sp.simplify(corpus6)}; сдвиг на π меняет её на {shifted}, '
      f'то есть период у неё π, а у бумаги 2π/3')
t('корпус: записанная дробь не синусоида',
  shifted == 0 and sp.simplify(sp.expand_trig(
      tgt6.subs(x, x + 2 * sp.pi / 3) - tgt6)) == 0
  and sp.simplify(sp.expand_trig(tgt6.subs(x, x + sp.pi) - tgt6)) != 0)
t('корпус: и записанный ответ к ней не подходит',
  not silent(verify_transform, '  corpus target',
             [('stretch_y', 2), ('stretch_x', R(1, 3)),
              ('shift_x', -sp.pi / 6)], sp.sin(x), corpus6)[0])

# 2. Май 2025 TZ3 Q6: корпусные координаты ставят максимум ровно
# на вертикальную асимптоту, чего не бывает.
print(f'май 2025 TZ3: корпус пишет A(−1/2, 5/2) при асимптоте x = −1/2; '
      f'по бумаге A = {crit13[0]}, B = {crit13[1]}')
t('корпус: максимум оказался на асимптоте',
  R(-1, 2) == -R(1, 2) and crit13[0][0] == -1)
t('корпус: восстановленная функция воспроизводит обе напечатанные точки',
  sp.simplify(f13.subs(x, -1) + R(5, 2)) == 0
  and sp.simplify(f13.subs(x, 0) - R(15, 2)) == 0)

# 3. Май 2025 TZ3 Q6(b): в корпусном методе вертикальная асимптота
# «остаётся». Нулей у f нет, значит и асимптоты у 15/f нет.
disc13 = sp.discriminant(sp.numer(sp.together(f13)), x)
print(f'май 2025 TZ3(b): числитель f имеет дискриминант {disc13}, '
      f'вещественных нулей нет — значит нет и вертикальных асимптот у 15/f')
t('корпус: асимптота у обратной величины выдумана',
  disc13 < 0 and sp.solveset(f13, x, sp.S.Reals) == sp.S.EmptySet)

# 4. Ноябрь 2021 Q10(b): записан конец (3, −5), а v(3) = −11.
print(f'ноябрь 2021: v(3) = {v16.subs(x, 3)}, в корпусе записано −5')
t('корпус: конец отрезка посчитан неверно', v16.subs(x, 3) == -11)

# 5. Ноябрь 2022 Q10: у функции потерялись показатели степени.
# Разрешает спор сам markscheme — он приводит уравнение к cos2x = 1/2.
corpus11 = sp.cos(2 * x) - sp.sqrt(3) * sp.sin(2 * x)
roots_corpus = sorted(sp.solveset(corpus11, x, sp.Interval(0, sp.pi)), key=float)
print(f'ноябрь 2022: корни по бумаге {roots11}, по корпусной записи '
      f'{roots_corpus}; markscheme печатает π/6 и 5π/6')
t('корпус: потерянные показатели меняют корни',
  roots11 == [sp.pi / 6, 5 * sp.pi / 6] and roots_corpus != roots11)
t('корпус: markscheme сводит уравнение к cos2x = 1/2',
  sp.simplify(f11 - (2 * sp.cos(2 * x) - 1)) == 0)

# 6. Ноябрь 2023: сессия лежит в корпусе двумя зонами, и это одна бумага.
import glob                                                        # noqa: E402
pair = {}
for path in sorted(glob.glob(os.path.join(
        ROOT, 'classification/generated/2023-november-*/*/paper-2.json'))):
    zone = path.split('generated/')[1].split('/')[0]
    for blk in json.load(open(path))['blocks']:
        if blk['id'].endswith('P2-Q02-B'):
            # Сравниваем номер вопроса и баллы, а не пересказ: пересказы
            # писала модель, и они отличаются словами при одном и том же
            # вопросе. Тождественность бумаг установлена в B2 постранично.
            pair[zone] = (blk['id'].split('-P2-')[1], blk.get('marks'),
                          blk.get('primary_topic'))
print(f'ноябрь 2023: зон найдено {len(pair)}, записи {sorted(pair.values())}')
t('корпус: ноябрь 2023 удвоен и здесь',
  len(pair) == 2 and len(set(pair.values())) == 1)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
