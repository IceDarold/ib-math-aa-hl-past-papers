"""Прогоняет все проверки практикума A8 с эталонными ответами из раздела решений.

Ответы не переписываются из решений: множества собираются из критических
значений, найденных sp.solve для **уравнений**, направление неравенства
определяется пробами, разложения строит sp.factor, точки пересечения
считаются численно. Отдельно измеряется, что проверки отвергают и где
они мягче экзамена.

Здесь же перепроверены расхождения с разметкой корпуса: перепутанный знак
в блоке мая 2022 TZ1, невозможная строка markscheme в ноябре 2025 TZ3,
неоднозначная постановка в мае 2022 TZ2, самоуничтожающаяся формула
в ноябре 2025 TZ1 и двенадцать баллов, которые к неравенствам
не относятся вовсе.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *
from kit import _scan_roots

NB = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a8-inequalities.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_series(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a, b, c, d = sp.symbols('a b c d')
m, n, p, q, s = sp.symbols('m n p q s')
T, tau = sp.symbols('T tau')


def t(name, ok):
    res.append((name, ok))


def sign_at(expr, value, var=x):
    """Знак выражения в точке — так проверяется направление неравенства."""
    return sp.sign(sp.N(expr.subs(var, value)))


print('=== решить неравенство относительно x ===')

# Задание 1: критические значения — корни уравнения, направление — по пробе.
crit1 = sorted(sp.solve(sp.Eq(5 * (x + 2)**2 - 5, 40), x))
inside1 = sign_at(5 * (x + 2)**2 - 45, sum(crit1) / 2)
outside1 = sign_at(5 * (x + 2)**2 - 45, crit1[0] - 1)
print(f'Задание 1: критические {crit1}, внутри знак {inside1}, снаружи {outside1}')
ans1 = sp.Interval(*crit1)
t('1', verify_solution_set('Задание 1', ans1, 5 * (x + 2)**2 - 5 <= 40))
t('1sign', inside1 < 0 < outside1)

# Задание 2: те же критические значения, но область режет половину ответа.
crit2 = sorted(sp.solve(sp.Eq(d**2 - 9 * d, 0), d))
print(f'Задание 2: критические {crit2}, знак при d = 10: '
      f'{sign_at(d**2 - 9 * d, 10, var=d)}')
ans2 = sp.Interval.open(crit2[-1], sp.oo)
t('2', verify_solution_set('Задание 2', ans2, d**2 - 9 * d > 0, var=d,
                           domain=sp.Interval.open(0, sp.oo)))

# Задание 3: числитель и знаменатель разбираются отдельно.
g3 = (x**2 - 14 * x + 24) / (2 * x + 6) - x
num3, den3 = sp.fraction(sp.together(g3))
zeros3 = sorted(sp.solve(sp.Eq(num3, 0), x))
poles3 = sorted(sp.solve(sp.Eq(den3, 0), x))
print(f'Задание 3: нули числителя {[sp.N(z, 6) for z in zeros3]}, '
      f'полюс {poles3}')
ans3 = sp.Union(sp.Interval.open(-sp.oo, zeros3[0]),
                sp.Interval.open(poles3[0], zeros3[1]))
t('3', verify_solution_set('Задание 3', ans3,
                           (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('3sign', sign_at(g3, -25) > 0 and sign_at(g3, -10) < 0
  and sign_at(g3, -2) > 0 and sign_at(g3, 5) < 0)

# Задание 4: f(|x|) считается подстановкой, а не догадкой.
f4 = (2 * x - 1) / (x + 1)
ans4a = sp.Interval.open(sp.solve(sp.Eq(f4, 0), x)[0], sp.oo)
even4 = sp.simplify(f4.subs(x, sp.Abs(x)))
edge4 = sp.solve(sp.Eq(2 * x - 1, 0), x)[0]        # |x| = 1/2, значит x = ±1/2
half = [-edge4, edge4]
print(f'Задание 4: f(|x|) = {even4}, нули числителя {sorted(half)}')
ans4b = sp.Union(sp.Interval.open(-sp.oo, min(half)),
                 sp.Interval.open(max(half), sp.oo))
t('4a', verify_solution_set('Задание 4(a)', ans4a, (f4 > 0) & (f4 < 2)))
t('4b', verify_solution_set('Задание 4(b)', ans4b, f4.subs(x, sp.Abs(x)) > 0))
t('4sym', ans4b == sp.imageset(sp.Lambda(x, -x), ans4b))

# Задание 5: точки пересечения — численно, концы — округлением до 3 з.ц.
h5 = 2**x - 2**(-x) - (x - 1) / (x**2 - 2 * x - 3)
f5 = sp.lambdify(x, h5, 'math')



def value5(v):
    """Значение h5 в точке; в полюсе возвращает бесконечность."""
    try:
        return f5(v)
    except ZeroDivisionError:
        return math.inf


cross5 = [v for v in _scan_roots(f5, -6, 6) if abs(value5(v)) < 1e-6]
poles5 = sorted(sp.solve(sp.Eq(x**2 - 2 * x - 3, 0), x))
print(f'Задание 5: пересечения {[round(v, 6) for v in cross5]}, '
      f'полюсы {poles5}, округление {[sig(v, 3) for v in cross5]}')
r51, r52, r53 = [sp.Float(sig(v, 3)) for v in cross5]
ans5 = sp.Union(sp.Interval.Ropen(r51, -1), sp.Interval.Ropen(r52, 3),
                sp.Interval(r53, sp.oo))


def holds5(v):
    if v == -1 or v == 3:
        return False
    return float(h5.subs(x, v).evalf()) >= 0


t('5', verify_param_set('Задание 5', ans5, holds5, var=x, window=(-6, 6),
                        eps=R(1, 100), tol=0.005))
t('5cross', len(cross5) == 3)

# Задание 6: целая часть корня и проверка обоих соседей.
cards = 14 * 52
roots6 = sorted(sp.solve(sp.Eq(n * (3 * n + 1) / 2, cards), n))
top6 = sp.floor(roots6[-1])
sum6 = lambda i: sp.Rational(i * (3 * i + 1), 2)
print(f'Задание 6: корни {[sp.N(v, 8) for v in roots6]}, целая часть {top6}, '
      f'суммы {sum6(top6)} и {sum6(top6 + 1)} при {cards}')
t('6n', check_num('Задание 6, рядов', top6, 6, D['Задание 6, рядов']))
t('6t21', check_num('Задание 6, карт на них', sum6(top6), 6,
                    D['Задание 6, карт на них']))
t('6t22', check_num('Задание 6, на один ряд больше', sum6(top6 + 1), 6,
                    D['Задание 6, на один ряд больше']))
t('6fits', sum6(top6) <= cards < sum6(top6 + 1))

print('\n=== неравенство как условие на букву ===')

# Задание 7: критические значения дискриминанта; p = 0 проверяется отдельно.
disc7 = sp.expand(sp.discriminant(3 * p * x**2 + 2 * p * x + 1 - p, x))
crit7 = sorted(sp.solve(sp.Eq(disc7, 0), p))
deg7 = sp.Poly(3 * sp.Integer(0) * x**2 + 2 * sp.Integer(0) * x + 1, x)
print(f'Задание 7: дискриминант {disc7}, критические {crit7}, '
      f'при p = 0 уравнение {deg7.as_expr()} = 0, корней '
      f'{len(sp.real_roots(deg7))}')
ans7 = sp.Union(sp.Interval.open(-sp.oo, crit7[0]),
                sp.Interval.open(crit7[-1], sp.oo))


def two_roots7(pv):
    return len(set(sp.real_roots(sp.Poly(3 * pv * x**2 + 2 * pv * x + 1 - pv,
                                         x)))) == 2


t('7', verify_param_set('Задание 7', ans7, two_roots7, var=p))
t('7zero', not two_roots7(sp.Integer(0)))

# Задание 8: множество из дискриминанта, потом целочисленное ограничение.
disc8 = sp.expand(sp.discriminant(x**2 / 2 + k * x + 13, x))
crit8 = sorted(sp.solve(sp.Eq(disc8, 0), k))
top8 = sp.floor(crit8[-1])
print(f'Задание 8: дискриминант {disc8}, границы {crit8} '
      f'({sp.N(crit8[-1], 6)}), наибольшее целое {top8}')
ans8 = sp.Interval.open(*crit8)
t('8set', verify_solution_set('Задание 8, множество', ans8, disc8 < 0, var=k))
t('8k', check_num('Задание 8, наибольшее k', top8, 6, D['Задание 8, наибольшее k']))
t('8check', sp.discriminant((x**2 / 2 + k * x + 13).subs(k, top8), x) < 0
  and sp.discriminant((x**2 / 2 + k * x + 13).subs(k, top8 + 1), x) > 0)

# Задание 9: дискриминант считает sympy, требуемое получается делением на 4.
disc9 = sp.expand(sp.discriminant(x**2 - 2 * d * x + 9 * d, x))
print(f'Задание 9: дискриминант {disc9}, после деления на 4 — '
      f'{sp.expand(disc9 / 4)}')
t('9', verify_identity('Задание 9', disc9, 4 * d**2 - 36 * d, var=d))
t('9ag', sp.expand(disc9 / 4) == d**2 - 9 * d)

# Задание 10: перебор по определению, без формулы.
faces = range(1, 7)
ac10 = sorted({av * cv for av in faces for cv in faces
               if any(bv**2 - 4 * av * cv > 0 for bv in faces)})
print(f'Задание 10: возможные ac {ac10}; произведений, меньших 9, '
      f'но недостижимых: '
      f'{sorted(set(range(1, 9)) - {av * cv for av in faces for cv in faces})}')
t('10', check_set('Задание 10', ac10, D['Задание 10']))

# Задание 11: знаки корней — критические значения дроби Виета.
prod11 = (2 * k + 9) / k
crit11 = sorted(sp.solve(sp.Eq(sp.numer(prod11), 0), k)
                + sp.solve(sp.Eq(sp.denom(prod11), 0), k))
print(f'Задание 11: произведение корней {prod11}, критические {crit11}')
ans11 = sp.Interval.open(*crit11)


def signs11(kv):
    if kv == 0:
        return False
    found = sorted(set(sp.real_roots(
        sp.Poly(kv * x**2 - (kv + 3) * x + 2 * kv + 9, x))))
    return len(found) == 2 and found[0] < 0 < found[1]


t('11', verify_param_set('Задание 11', ans11, signs11))
t('11zero', not signs11(sp.Integer(0)) and not signs11(R(-9, 2)))

print('\n=== число решений как множество параметров ===')

# Задание 12: максимум считает sympy, ответ — решение неравенства на максимум.
top12 = sp.maximum(-(6 * x**2 - 12 * x + 1) + c, x)
crit12 = sp.solve(sp.Eq(top12, 0), c)
print(f'Задание 12: max (g∘f) = {top12}, обращается в ноль при c = {crit12}')
ans12 = sp.Interval(-sp.oo, crit12[0])
t('12', verify_param_set('Задание 12', ans12,
                         lambda cv: sp.maximum(-(6 * x**2 - 12 * x + 1) + cv, x) <= 0,
                         var=c))
t('12disc', sp.solve(sp.Eq(sp.discriminant(-6 * x**2 + 12 * x - 1 + c, x), 0),
                     c) == crit12)

# Задание 13: слияние двух значений c — уравнение, а не догадка.
c13 = 1 / sp.sqrt(m) - m * sp.sqrt(m)
merge13 = [v for v in sp.solve(sp.Eq(c13, -c13), m) if v.is_real and v > 0]
print(f'Задание 13: c(m) = {c13}, два значения совпадают при m = {merge13}')
ans13_two = sp.Union(sp.Interval.open(0, merge13[0]),
                     sp.Interval.open(merge13[0], sp.oo))
ans13_one = sp.FiniteSet(*merge13)


def normals(mv):
    if mv <= 0:
        return 0
    return len({sp.simplify(1 / sp.sqrt(mv) - mv * sp.sqrt(mv)),
                sp.simplify(-1 / sp.sqrt(mv) + mv * sp.sqrt(mv))})


t('13a', verify_param_set('Задание 13(a)', ans13_two,
                          lambda mv: normals(mv) == 2, var=m))
t('13b', verify_param_set('Задание 13(b)', ans13_one,
                          lambda mv: normals(mv) == 1, var=m))
t('13merge', normals(sp.Integer(1)) == 1 and normals(sp.Integer(4)) == 2)

# Задание 14: граница — максимум функции u·e^{−u}, найденный производной.
u = sp.Symbol('u')
peak = sp.solve(sp.Eq(sp.diff(u * sp.exp(-u), u), 0), u)[0]
top14 = (u * sp.exp(-u)).subs(u, peak)
base14 = sp.exp(top14)
print(f'Задание 14: максимум u·e^(−u) при u = {peak}, равен {top14}; '
      f'граница a = {base14} = {sp.N(base14, 8)}')
ans14_two = sp.Interval.open(1, base14)
ans14_none = sp.Interval.open(base14, sp.oo)


def crossings(av):
    a_ = float(av)
    if a_ <= 1:
        return None
    if abs(math.log(a_) - math.exp(-1)) < 1e-9:
        return None
    return len(_scan_roots(lambda tv: tv * math.exp(-tv) - math.log(a_), -2, 40))


t('14a', verify_param_set('Задание 14(a)', ans14_two,
                          lambda av: crossings(av) == 2, var=a, window=(0, 4)))
t('14b', verify_param_set('Задание 14(b)', ans14_none,
                          lambda av: crossings(av) == 0, var=a, window=(0, 4)))
t('14base', sp.simplify(base14 - sp.exp(1 / sp.E)) == 0)

print('\n=== доказать неравенство ===')

# Задание 15: единица превращается в логарифм, дальше монотонность.
log15 = sp.logcombine(1 + sp.log(n, 2), force=True)
crit15 = sp.solve(sp.Eq(2 * n, n + 1), n)
print(f'Задание 15: 1 + log2(n) = {log15}, 2n = n+1 при n = {crit15}')
t('15a', verify_identity('Задание 15(a)', sp.log(2 * n, 2), 1 + sp.log(n, 2),
                         var=n))
t('15b', verify_solution_set('Задание 15(b)', sp.Interval(crit15[0], sp.oo),
                             2 * n >= n + 1, var=n))

# Задание 16: сумма считается подстановкой в v, квадрат — раскрытием.
v16 = sp.exp(T - tau) - 1
sum16 = sp.simplify(v16.subs(tau, T - k) + v16.subs(tau, T + k))
sq16 = (sp.exp(k / 2) - sp.exp(-k / 2))**2
print(f'Задание 16: v(T−k)+v(T+k) = {sum16}, квадрат раскрывается в '
      f'{sp.expand(sq16)}')
t('16a', verify_identity('Задание 16(a)', sum16, sp.exp(k) + sp.exp(-k) - 2,
                         var=k))
t('16b', verify_nonneg_form('Задание 16(b)', sq16, sum16))
t('16min', sp.minimum(sp.exp(k) + sp.exp(-k) - 2, k) == 0)

# Задание 17: возведение в квадрат и перенос — sympy, разложение — factor.
squared17 = sp.expand((x + y)**2 - 4 * x * y)
form17 = sp.factor(squared17)
print(f'Задание 17: (x+y)² − 4xy = {squared17} = {form17}')
t('17a', verify_identity('Задание 17(a)', squared17, x**2 - 2 * x * y + y**2,
                         var=x))
t('17b', verify_nonneg_form('Задание 17(b)', form17, squared17))

# Задание 18: разложение строит factor, максимум произведения — AM–GM.
tt = sp.Symbol('t')                # имя t в этом файле занято под функцию проверок
diff18 = sp.factor((tt**2 - s**2) - (2 * s * tt - s**2))
max18 = (T / n)**n
print(f'Задание 18: b − a = {diff18}; M_n(T) = {max18}')
t('18a', verify_factored('Задание 18(a)', diff18, tt**2 - 2 * s * tt, var=tt, n=2))
t('18b', check_series('Задание 18(b)', max18, D['Задание 18(b)'], var=n))
# Равенство в AM–GM достигается на равных слагаемых: их произведение и есть (T/n)^n.
t('18eq', sp.simplify(sp.prod([T / n] * 4) - (T / n)**4) == 0)

print('\n=== задание на таймере ===')
disc19 = sp.expand(sp.discriminant(x**2 + k * x + 15 - k, x))
crit19 = sorted(sp.solve(sp.Eq(disc19, 0), k))
prod19 = sp.solve(sp.Eq(15 - k, 0), k)[0]
print(f'Задание 19: дискриминант {disc19}, критические {crit19}; '
      f'произведение корней меняет знак при k = {prod19}')
ans19a = sp.Union(sp.Interval.open(-sp.oo, crit19[0]),
                  sp.Interval.open(crit19[-1], sp.oo))
ans19b = sp.Union(sp.Interval.open(-sp.oo, crit19[0]),
                  sp.Interval.open(crit19[-1], prod19))


def two_distinct19(kv):
    return len(set(sp.real_roots(sp.Poly(x**2 + kv * x + 15 - kv, x)))) == 2


def same_sign19(kv):
    found = sorted(set(sp.real_roots(sp.Poly(x**2 + kv * x + 15 - kv, x))))
    return len(found) == 2 and found[0] * found[1] > 0


t('19a', verify_param_set('Задание 19(a)', ans19a, two_distinct19))
t('19b', verify_param_set('Задание 19(b)', ans19b, same_sign19))
t('19cut', same_sign19(sp.Integer(10)) and not same_sign19(sp.Integer(20)))

print('\n=== расхождения с разметкой корпуса ===')

# 1. Май 2022 TZ1: с записанной в корпусе f ни одна точка пересечения не сходится.
bad5 = 2**(-x) - 2**x - (x - 1) / (x**2 - 2 * x - 3)
vals_bad = [float(bad5.subs(x, sp.Float(v)).evalf()) for v in cross5]
vals_good = [float(h5.subs(x, sp.Float(v)).evalf()) for v in cross5]
print(f'  f = 2^(−x) − 2^x: в точках корпуса значения '
      f'{[round(v, 3) for v in vals_bad]}, а должны быть нулями')
print(f'  f = 2^x − 2^(−x): те же точки дают '
      f'{[round(v, 9) for v in vals_good]}')
t('c1', all(abs(v) > 0.1 for v in vals_bad) and all(abs(v) < 1e-6 for v in vals_good))

# 2. Ноябрь 2025 TZ3: записанная строка markscheme полным квадратом не является.
corpus17 = x**2 - 4 * x * y + y**2
print(f'  x² − 4xy + y² раскладывается как {sp.factor(corpus17)} — не квадрат; '
      f'верная строка x² − 2xy + y² = {sp.factor(squared17)}')
t('c2', sp.factor(corpus17) == corpus17 and sp.factor(squared17) == (x - y)**2)
t('c2sq', sp.simplify(4 * x * y - (x + y)**2 + corpus17) != 0)

# 3. Май 2022 TZ2: |f(x)| > 0 не даёт записанного ответа, а f(|x|) > 0 даёт.
abs_outside = sp.solveset(sp.Abs(f4) > 0, x, sp.S.Reals)
print(f'  |f(x)| > 0 даёт {abs_outside}, а записанный ответ — {ans4b}')
t('c3', abs_outside != ans4b and sp.solveset(f4.subs(x, sp.Abs(x)) > 0, x,
                                             sp.S.Reals) == ans4b)

# 4. Ноябрь 2025 TZ1: формула из краткого описания блока тождественно нулевая.
corpus13 = 1 / sp.sqrt(m) - 1 / sp.sqrt(m)
print(f'  1/√m − 1/√m = {corpus13}; форма из markscheme: {c13}')
t('c4', corpus13 == 0 and sp.simplify(c13) != 0)

# 5. Двенадцать баллов темы неравенствами не являются вовсе.
alien = {'2025-NOV-TZ1-P1-Q06': 6, '2025-NOV-TZ3-P2-Q11-B-II': 2,
         '2025-NOV-TZ1-P3-Q01-B-I': 4}
print(f'  не неравенства: {alien}, всего {sum(alien.values())} балла из 87')
t('c5', sum(alien.values()) == 12)

print('\n=== что проверки отвергают ===')
t('n1', not verify_solution_set('концы включены, хотя неравенство строгое',
                                sp.Interval(crit2[-1], sp.oo), d**2 - 9 * d > 0,
                                var=d, domain=sp.Interval.open(0, sp.oo)))
t('n2', not verify_solution_set('забыто ограничение d > 0',
                                sp.Union(sp.Interval.open(-sp.oo, 0),
                                         sp.Interval.open(9, sp.oo)),
                                d**2 - 9 * d > 0, var=d,
                                domain=sp.Interval.open(0, sp.oo)))
t('n3', not verify_solution_set('полюс включён в ответ',
                                sp.Union(sp.Interval.open(-sp.oo, zeros3[0]),
                                         sp.Interval.Ropen(poles3[0], zeros3[1])),
                                (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('n4', not verify_solution_set('домножили на знаменатель без разбора знака',
                                sp.Interval.open(zeros3[0], zeros3[1]),
                                (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('n5', not verify_param_set('вырожденное p = 0 включено',
                             sp.Union(sp.Interval(-sp.oo, 0),
                                      sp.Interval.open(R(3, 4), sp.oo)),
                             two_roots7, var=p))
t('n6', not verify_param_set('пересечение заменено объединением',
                             ans19a, same_sign19))
t('n7', not verify_param_set('выколотая точка не выколота',
                             sp.Interval.open(0, sp.oo),
                             lambda mv: normals(mv) == 2, var=m))
t('n8', not verify_nonneg_form('раскрытый вид вместо квадрата', squared17,
                               squared17))
t('n9', not verify_factored('разность не разложена', sp.expand(diff18),
                            tt**2 - 2 * s * tt, var=tt, n=2))
t('n10', not check_num('округление вверх вместо целой части', top6 + 1, 6,
                       D['Задание 6, рядов']))

print('\n=== где проверки мягче экзамена ===')
# У округлённого конца проверка не различает строгое и нестрогое неравенство:
# точка -1.27 отличается от истинной -1.26686..., и подстановка там ничего
# не решает. На экзамене за такой конец стоит балл.
soft5 = sp.Union(sp.Interval.open(r51, -1), sp.Interval.open(r52, 3),
                 sp.Interval.Lopen(r53, sp.oo))
t('предел-1 открытый конец у округлённой границы проходит',
  verify_param_set('  все концы открыты', soft5, holds5, var=x,
                   window=(-6, 6), eps=R(1, 100), tol=0.005))
# verify_param_set смотрит только внутрь своего окна. Конец, поставленный
# далеко за его пределами, не проверяется — а на экзамене ответ «6 < k < 100»
# вместо «k > 6» неверен.
t('предел-2 конец за окном проверки не ловится',
  verify_param_set('  k < 100 вместо бесконечности', sp.Union(
      sp.Interval.open(-sp.oo, -10), sp.Interval.open(6, 100)), two_distinct19))
# Форма записи проверяется, а законность шага — нет: возводить в квадрат
# можно только при положительных частях, и об этом проверка не спросит.
t('предел-3 про положительность частей проверка не спрашивает',
  verify_nonneg_form('  квадрат без оговорок', form17, squared17))

bad = [nm for nm, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
