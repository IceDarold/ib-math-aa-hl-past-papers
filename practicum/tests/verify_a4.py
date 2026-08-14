"""Прогоняет все проверки практикума A4 с эталонными ответами из раздела решений.

Ответы не переписываются из решений: системы решаются заново через sp.solve,
разложения на множители и на простейшие дроби строятся sympy, корни считаются
численно. Отдельно измеряется, что проверки отвергают, и где они мягче экзамена.

Здесь же перепроверены три расхождения с разметкой корпуса: несовместное
условие в блоке мая 2021 TZ2, второе решение системы в ноябре 2025 TZ3
и искажённая правая часть в мае 2024 TZ1.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *

NB = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a4-polynomials.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_expr(", "check_set(",
                                   "check_series(", "check_complex_set(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a, b, c, d = sp.symbols('a b c d')
m, n, p, q, r = sp.symbols('m n p q r')
z, w = sp.symbols('z w')
al, be, ga, de_ = sp.symbols('alpha beta gamma delta')


def t(name, ok):
    res.append((name, ok))


print('=== множитель и остаток ===')
P11 = 3 * x**3 + 5 * x**2 + x - 1
print(f'P(x) = {P11},  P(-1) = {P11.subs(x, -1)}')
t('1', check_num('Задание 1', P11.subs(x, -1), 6, D['Задание 1']))

f2 = 2 * x**4 - 6 * x**3 + p * x**2 + q * x - 2
sol2 = sp.solve([f2.subs(x, 1), f2.subs(x, 3) + 2], [p, q], dict=True)[0]
print(f'Задание 2: {sol2}')
t('2p', check_expr('Задание 2, p', sol2[p], D['Задание 2, p']))
t('2q', check_expr('Задание 2, q', sol2[q], D['Задание 2, q']))

# Задание 3: остаток 12 при делении на (x+1) и alpha²+beta² = 37/4.
P3 = 2 * x**2 + q * x + r
eq_rem = sp.Eq(P3.subs(x, -1), 12)
eq_sq = sp.Eq((q**2 / 4) - r, R(37, 4))          # (a+b)² − 2ab при a=2
sol3 = sp.solve([eq_rem, eq_sq], [q, r], dict=True)
qs = sorted(s[q] for s in sol3)
print(f'Задание 3: система даёт {[(s[q], s[r]) for s in sol3]}')
t('3set', check_set('Задание 3, кандидаты', qs, D['Задание 3, кандидаты']))
real = [s for s in sol3
        if sp.discriminant(P3.subs({q: s[q], r: s[r]}), x) > 0]
print(f'  с действительными корнями остаётся {[(s[q], s[r]) for s in real]}')
t('3only', len(real) == 1)
t('3q', check_expr('Задание 3, q', real[0][q], D['Задание 3, q']))
t('3r', check_expr('Задание 3, r', real[0][r], D['Задание 3, r']))

print('\n=== деление и разложение ===')
quo4, rem4 = sp.div(2 * x**2 - 5 * x - 3, x - 1, x)
print(f'Задание 4: частное {quo4}, остаток {rem4}')
t('4', verify_division('Задание 4', quo4, rem4, 2 * x**2 - 5 * x - 3, x - 1))

fac5 = sp.factor(P11)
print(f'Задание 5: {fac5}')
t('5', verify_factored('Задание 5', fac5, P11, n=3))

# Задание 6: P = x³+ax²+bx+c делится на (x+1)(x+2), a,b,c различны из {1..5}.
P6 = x**3 + a * x**2 + b * x + c
lin = sp.solve([P6.subs(x, -1), P6.subs(x, -2)], [b, c], dict=True)[0]
print(f'Задание 6(i): b = {sp.expand(lin[b])}, c = {sp.expand(lin[c])}')
t('6b', check_series('Задание 6(i)', lin[b], D['Задание 6(i)'], var=a))
good = [(a0, lin[b].subs(a, a0), lin[c].subs(a, a0)) for a0 in range(1, 6)
        if lin[b].subs(a, a0) in range(1, 6) and lin[c].subs(a, a0) in range(1, 6)
        and len({a0, lin[b].subs(a, a0), lin[c].subs(a, a0)}) == 3]
print(f'Задание 6(ii): подходит {good}')
t('6uniq', len(good) == 1)
a0, b0, c0 = good[0]
t('6a', check_num('Задание 6(ii), a', a0, 6, D['Задание 6(ii), a']))
t('6bn', check_num('Задание 6(ii), b', b0, 6, D['Задание 6(ii), b']))
t('6cn', check_num('Задание 6(ii), c', c0, 6, D['Задание 6(ii), c']))
P6v = P6.subs({a: a0, b: b0, c: c0})
t('6f', verify_factored('Задание 6(iii)', sp.factor(P6v), P6v, n=3))

# Задание 7: делимость на (x+1)² через P(−1)=0 и P'(−1)=0.
f7 = x**4 + p * x**3 - 2 * x**2 + q * x - 3
sol7 = sp.solve([f7.subs(x, -1), sp.diff(f7, x).subs(x, -1)], [p, q], dict=True)[0]
print(f'\nЗадание 7: {sol7};  частное {sp.div(f7.subs(sol7), (x + 1)**2, x)[0]}')
t('7', verify_divisible('Задание 7', f7, (x + 1)**2, {p: sol7[p], q: sol7[q]}))

print('\n=== Виета ===')
prod8 = (2 * k + 9) / k
t('8', check_series('Задание 8', prod8, D['Задание 8'], var=k))

id9 = sp.expand((p + q)**3 - 3 * p * q * (p + q))
print(f'Задание 9(a): {id9}')
t('9a', check_series('Задание 9(a)', id9, D['Задание 9(a)'], var=p))
# Коэффициенты нового уравнения считаются через Виета, а не переписываются.
S9, P9 = R(5, 2), R(1, 2)
cube9 = S9**3 - 3 * P9 * S9
m9, n9 = -(cube9 / P9**3), 1 / P9**3
print(f'Задание 9(b): a³+b³ = {cube9}, m = {m9}, n = {n9}')
t('9b', verify_root_transform('Задание 9(b)', [1, m9, n9],
                              2 * x**2 - 5 * x + 1, lambda s: 1 / s**3))

# Задание 10: корни alpha, beta, alpha+beta у x³ − kx² + (k²/2)x − 3k.
# Три формулы Виета записываются через S = alpha+beta и Pp = alpha*beta:
# сумма корней 2S = k, сумма попарных произведений Pp + S² = k²/2,
# произведение Pp·S = 3k. Ответ выводится, а не переписывается.
S10, Pp10 = sp.symbols('S Pp')
sum10 = sp.solve(sp.Eq(2 * S10, k), S10)[0]
ab10 = sp.solve(sp.Eq(Pp10 + sum10**2, k**2 / 2), Pp10)[0]
sol10 = [s for s in sp.solve(sp.Eq(ab10 * sum10, 3 * k), k) if s.is_real and s > 0]
print(f'Задание 10: alpha+beta = {sum10}, alpha*beta = {ab10}, k = {sol10}')
t('10ab', check_series('Задание 10, alpha*beta', ab10,
                       D['Задание 10, alpha*beta'], var=k))
t('10k', check_expr('Задание 10, k', sol10[0], D['Задание 10, k']))
# и обратная проверка: при таком k корни действительно alpha, beta, alpha+beta
k10 = sol10[0]
r10 = sorted(sp.Poly(sp.expand(x**3 - k10 * x**2 + k10**2 / 2 * x - 3 * k10),
                     x).nroots(), key=lambda s: sp.re(s))
t('10roots', abs(complex(r10[0] + r10[1] - r10[2])) < 1e-9
  or abs(complex(r10[0] + r10[2] - r10[1])) < 1e-9
  or abs(complex(r10[1] + r10[2] - r10[0])) < 1e-9)

# Задание 11: P(z) = z³ − (36/m)z² + mz − 4m, множитель z − 3i.
P11z = z**3 - (36 / m) * z**2 + m * z - 4 * m
m11 = [s for s in sp.solve(P11z.subs(z, 3 * sp.I), m) if s.is_real and s > 0]
print(f'\nЗадание 11: m = {m11}')
t('11m', check_num('Задание 11, m', m11[0], 6, D['Задание 11, m']))
roots11 = sp.Poly(sp.expand(P11z.subs(m, m11[0])), z).nroots()
print(f'  корни: {roots11}')
t('11r', check_complex_set('Задание 11, корни', roots11, D['Задание 11, корни']))

# Задание 12: подстановка w = 1/z в z⁴+2z²+4.
tr12 = sp.simplify(sp.expand((z**4 + 2 * z**2 + 4).subs(z, 1 / w) * w**4))
cf12 = sp.Poly(tr12, w).all_coeffs()
print(f'Задание 12: {tr12}, коэффициенты {cf12}')
t('12', verify_root_transform('Задание 12', cf12, z**4 + 2 * z**2 + 4,
                              lambda s: 1 / s, var=z))

print('\n=== симметричные суммы ===')
sq13 = sp.expand((al + be + ga)**2 - 2 * (al * be + be * ga + ga * al))
t('13algebra', sp.expand(sq13 - (al**2 + be**2 + ga**2)) == 0)
print(f'alpha²+beta²+gamma² = {sq13}  ->  p²−2q')
t('13sq', check_series('Задание 13(b)(i)', p**2 - 2 * q, D['Задание 13(b)(i)'], var=p))
dif13 = sp.expand((al - be)**2 + (be - ga)**2 + (ga - al)**2)
t('13dif_algebra',
  sp.expand(dif13 - (2 * (al**2 + be**2 + ga**2)
                     - 2 * (al * be + be * ga + ga * al))) == 0)
t('13dif', check_series('Задание 13(b)(ii)', 2 * p**2 - 6 * q,
                        D['Задание 13(b)(ii)'], var=p))
C13 = x**3 - 7 * x**2 + 17 * x + 1
p13 = sp.Poly(C13, x).all_coeffs()[1]
q13 = sp.Poly(C13, x).all_coeffs()[2]
print(f'Задание 13(d): p = {p13}, p² = {p13**2}, 3q = {3 * q13}')
t('13p2', check_num('Задание 13(d), p²', p13**2, 6, D['Задание 13(d), p²']))
t('13q3', check_num('Задание 13(d), 3q', 3 * q13, 6, D['Задание 13(d), 3q']))
cand = [q0 for q0 in range(1, 17)
        if sum(1 for s in sp.Poly(x**3 - 7 * x**2 + q0 * x + 1, x).nroots()
               if abs(sp.im(s)) < 1e-9) < 3]
print(f'Задание 13(e): контрпримеры {cand}, наименьший {cand[0]}')
t('13e', check_num('Задание 13(e)', cand[0], 6, D['Задание 13(e)']))

sq14 = sp.expand((al + be + ga + de_)**2
                 - 2 * sum(u * v for i, u in enumerate([al, be, ga, de_])
                           for v in [al, be, ga, de_][i + 1:]))
t('14algebra', sp.expand(sq14 - (al**2 + be**2 + ga**2 + de_**2)) == 0)
t('14sq', check_series('Задание 14(f)(i)', p**2 - 2 * q,
                       D['Задание 14(f)(i)'], var=p))
Q14 = x**4 - 2 * x**3 + 3 * x**2 - 4 * x + 5
cf14 = sp.Poly(Q14, x).all_coeffs()
print(f'Задание 14(g): p = {cf14[1]}, q = {cf14[2]}, p² = {cf14[1]**2}, '
      f'2q = {2 * cf14[2]}')
t('14p2', check_num('Задание 14(g), p²', cf14[1]**2, 6, D['Задание 14(g), p²']))
t('142q', check_num('Задание 14(g), 2q', 2 * cf14[2], 6, D['Задание 14(g), 2q']))
QUART = x**4 - 9 * x**3 + 24 * x**2 + 22 * x - 12
ints = [i for i in range(-12, 13) if i and QUART.subs(x, i) == 0]
print(f'Задание 14(h)(ii): целые корни {ints}')
t('14root', check_num('Задание 14(h)(ii)', ints[0], 6, D['Задание 14(h)(ii)']))
quo14, rem14 = sp.div(QUART, x + 1, x)
print(f'Задание 14(h)(iii): частное {quo14}, остаток {rem14}')
t('14div', verify_division('Задание 14(h)(iii)', quo14, rem14, QUART, x + 1))
cfc = sp.Poly(quo14, x).all_coeffs()
t('14pc', check_num('Задание 14(h)(iii), p²', cfc[1]**2, 6,
                    D['Задание 14(h)(iii), p²']))
t('143qc', check_num('Задание 14(h)(iii), 3q', 3 * cfc[2], 6,
                     D['Задание 14(h)(iii), 3q']))
t('14criterion', cfc[1]**2 < 3 * cfc[2])

print('\n=== простейшие дроби ===')
ap15a = sp.apart(1 / (x * (k - x)), x)
print(f'Задание 15(a): {ap15a}')
t('15a', check_apart('Задание 15(a)', ap15a, 1 / (x * (k - x))))
ap15b = sp.apart(1 / (1 - 4 * v**2), v)
print(f'Задание 15(b): {ap15b}')
t('15b', check_apart('Задание 15(b)', ap15b, 1 / (1 - 4 * v**2), var=v))

Q16 = (x + 1) * (2 * x + 1)
ap16c = sp.apart(1 / Q16, x)
print(f'Задание 16(c): {ap16c}')
t('16c', check_apart('Задание 16(c)', ap16c, 1 / Q16))
expr16 = (1 - x / Q16) / ((1 + x) * (2 * x + 1))
ap16d = sp.apart(sp.simplify(expr16), x)
print(f'Задание 16(d): {ap16d}')
t('16d', check_apart('Задание 16(d)', ap16d, expr16))

print('\n=== задание на таймере ===')
g17 = 2 * x**3 - 7 * x**2 + d * x - sp.Symbol('e')
s17 = -sp.Poly(g17, x).all_coeffs()[1] / sp.Poly(g17, x).all_coeffs()[0]
print(f'Задание 17(a): {s17}')
t('17a', check_expr('Задание 17(a)', s17, D['Задание 17(a)']))
rho = sp.symbols('rho')
sol17 = sp.solve(sp.Eq(s17 + 2 * rho, R(11, 2)), rho)
print(f'Задание 17(b): rho = {sol17}')
t('17b', check_num('Задание 17(b)', sol17[0], 6, D['Задание 17(b)']))
# произведение пяти корней = 10; пара сопряжённых даёт 10, gamma = 1/2
ab17 = sp.solve(sp.Eq(10 * sp.Symbol('P') * R(1, 2), 10), sp.Symbol('P'))[0]
print(f'Задание 17(c): alpha*beta = {ab17}')
t('17ab', check_num('Задание 17(c), alpha*beta', ab17, 6,
                    D['Задание 17(c), alpha*beta']))
pair = sorted(sp.solve(sp.Symbol('u')**2 - (s17 - R(1, 2)) * sp.Symbol('u') + ab17))
print(f'  alpha, beta = {pair}')
t('17a2', check_num('Задание 17(c), alpha', pair[0], 6, D['Задание 17(c), alpha']))
t('17b2', check_num('Задание 17(c), beta', pair[1], 6, D['Задание 17(c), beta']))

print('\n=== расхождения с разметкой корпуса ===')
# 1. Май 2021 TZ2: уравнение x³ − kx² + 3k = 0 несовместно с ответом 2√6.
bad10 = sp.solve(sp.Eq(k**3 / 8, -3 * k), k)
print(f'  x³−kx²+3k: k³/8 = −3k даёт {bad10} — положительных действительных нет')
t('c1', not any(s.is_real and s > 0 for s in bad10))
t('c1fix', sp.simplify(sp.solve(sp.Eq(k**3 / 8, 3 * k), k)[-1] - 2 * sp.sqrt(6)) == 0)

# 2. Ноябрь 2025 TZ3: система на q квадратная, корней два.
print(f'  2x²+qx+r: оба решения {[(s[q], s[r]) for s in sol3]}, '
      f'дискриминанты '
      f'{[sp.discriminant(P3.subs({q: s[q], r: s[r]}), x) for s in sol3]}')
t('c2', len(sol3) == 2)

# 3. Май 2024 TZ1: записанная в корпусе правая часть пункта (d) не равна левой.
corpus16 = 1 - 4 / (2 * x + 1) - 2 / (x + 1) + 2 / (2 * x + 1)**2
gap = sp.simplify(expr16 - corpus16)
print(f'  разность с записью корпуса: {sp.cancel(gap)} (не ноль)')
t('c3', sp.simplify(gap) != 0)
t('c3fix', sp.simplify(expr16 - (2 / (x + 1) + 1 / (x + 1)**2
                                 - 4 / (2 * x + 1) + 2 / (2 * x + 1)**2)) == 0)

print('\n=== что проверки отвергают ===')
t('n1', not verify_factored('раскрытый ответ вместо произведения', P11, P11, n=3))
t('n2', not verify_factored('разложение не доведено до конца',
                            (x + 1) * (3 * x**2 + 2 * x - 1), P11))
t('n3', not verify_division('делить можно дальше', 2 * x, -3 * x - 3,
                            2 * x**2 - 5 * x - 3, x - 1))
t('n4', not verify_divisible('p и q перепутаны местами', f7, (x + 1)**2,
                             {p: sol7[q], q: sol7[p]}))
t('n5', not check_apart('дробь не разложена', 1 / Q16, 1 / Q16))
t('n6', not check_apart('пропущено слагаемое с квадратом',
                        2 / (x + 1) - 4 / (2 * x + 1) + 2 / (2 * x + 1)**2, expr16))
t('n7', not verify_root_transform('знак m перепутан', [1, -m9, n9],
                                  2 * x**2 - 5 * x + 1, lambda s: 1 / s**3))
rejected = [s[q] for s in sol3 if s[q] != real[0][q]][0]
t('n8', not check_expr('второй корень системы взят без проверки на вещественность',
                       rejected, D['Задание 3, q']))
t('n9', not check_series('для квартики взят коэффициент 3 вместо 2',
                         p**2 - 3 * q, D['Задание 14(f)(i)'], var=p))

print('\n=== где проверки мягче экзамена ===')
# Уравнение, умноженное на константу, имеет те же корни — и markscheme
# его принимает, и verify_root_transform тоже.
t('предел-1 масштабированное уравнение проходит',
  verify_root_transform('  умноженное на 8', [8, 8 * m9, 8 * n9],
                        2 * x**2 - 5 * x + 1, lambda s: 1 / s**3))
# check_series сверяет значения, поэтому нераскрытая скобка в задании 9(a)
# пройдёт — а там как раз просили раскрыть.
t('предел-2 нераскрытое в 9(a) проходит',
  check_series('  (p+q)³ − 3pq(p+q) как есть', (p + q)**3 - 3 * p * q * (p + q),
               D['Задание 9(a)'], var=p))

bad = [nm for nm, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
