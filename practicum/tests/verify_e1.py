"""Независимая проверка каждого ответа практикума E1.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение и
проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит ещё и «другим механизмом». verify_limit
из kit подходит к пределу лестницей точек и ничего не вычисляет символьно;
здесь предел берётся sympy.limit и рядом Маклорена. Совпадение двух этих
способов и есть проверка: подстановка и алгебра сошлись.

Запуск:  python practicum/tests/verify_e1.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
import kit
from kit import digest, sig

R = sp.Rational
x, t, b, n, m, c, a, F, alpha = sp.symbols('x t b n m c a F alpha')

res = []


def chk(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


def dn(value, sf=6):
    return digest(sig(value, sf))


print('=== Задача 1: подстановка и сокращение (май 2024 TZ1 P1 Q11) ===')
P = 3*x**3 + 5*x**2 + x - 1
Q = (x + 1)*(2*x + 1)
FX = P / ((x + 1)*Q)
# Множитель ищется делением, а не сверкой с готовым разложением.
chk('P(-1) = 0, значит (x+1) — множитель', P.subs(x, -1) == 0)
quot = sp.div(P, x + 1, x)[0]
chk('частное 3x^2 + 2x - 1', sp.expand(quot - (3*x**2 + 2*x - 1)) == 0)
chk('P = (x+1)^2 (3x-1)',
    sp.expand(P - (x + 1)**2*(3*x - 1)) == 0)
chk('f сокращается до (3x-1)/(2x+1)',
    sp.simplify(FX - (3*x - 1)/(2*x + 1)) == 0)
chk('предел при x -> -1 равен 4', sp.limit(FX, x, -1) == 4)
chk('а значения f при x = -1 не существует', FX.subs(x, -1) == sp.nan)

print('\n=== Задача 2: старшие степени ===')
chk('предел f на бесконечности 3/2', sp.limit(FX, x, sp.oo) == R(3, 2))
VT = R(814, 100)*t/sp.sqrt(t**2 + R(2, 10))
chk('предел v на бесконечности 8.14', sp.limit(VT, t, sp.oo) == R(407, 50))
chk('8.14 — это 407/50', sp.nsimplify(R(407, 50)) == R(407, 50)
    and abs(float(R(407, 50)) - 8.14) < 1e-12)

print('\n=== Задача 3: кривизна уходит в ноль (май 2025 TZ1 P3 Q2) ===')
KX = 2*abs(a)/(1 + (2*a*x + b)**2)**R(3, 2)
chk('предел кривизны 0 при a = 2, b = 5',
    sp.limit(KX.subs({a: 2, b: 5}), x, sp.oo) == 0)
chk('и при a = -3, b = 0',
    sp.limit(KX.subs({a: -3, b: 0}), x, sp.oo) == 0)
# Кривизна прямой равна нулю тождественно — то, к чему квадратичная и идёт.
line = sp.Abs(sp.diff(5*x + 2, x, 2))/(1 + sp.diff(5*x + 2, x)**2)**R(3, 2)
chk('у прямой кривизна ноль всюду', sp.simplify(line) == 0)

print('\n=== Задача 4: правило Лопиталя один раз (май 2021 TZ1 P1 Q8) ===')
NUM4, DEN4 = sp.atan(2*x), sp.tan(3*x)
chk('числитель идёт в 0', sp.limit(NUM4, x, 0) == 0)
chk('знаменатель идёт в 0', sp.limit(DEN4, x, 0) == 0)
after = sp.diff(NUM4, x)/sp.diff(DEN4, x)
chk('после одного применения форма уже определённая',
    sp.limit(sp.diff(DEN4, x), x, 0) != 0)
chk('предел равен 2/3', sp.simplify(after.subs(x, 0) - R(2, 3)) == 0)
chk('и sympy согласен', sp.limit(NUM4/DEN4, x, 0) == R(2, 3))

print('\n=== Задача 5: дважды и остановиться (май 2024 TZ2 P1 Q8) ===')
NUM5, DEN5 = sp.sec(x)**4 - sp.cos(x)**2, x**4 - x**2
chk('первая подстановка даёт 0/0',
    sp.limit(NUM5, x, 0) == 0 and sp.limit(DEN5, x, 0) == 0)
chk('после первого применения всё ещё 0/0',
    sp.limit(sp.diff(NUM5, x), x, 0) == 0 and sp.limit(sp.diff(DEN5, x), x, 0) == 0)
chk('после второго знаменатель равен -2', sp.diff(DEN5, x, 2).subs(x, 0) == -2)
chk('а числитель равен 6', sp.diff(NUM5, x, 2).subs(x, 0) == 6)
chk('предел равен -3',
    sp.diff(NUM5, x, 2).subs(x, 0)/sp.diff(DEN5, x, 2).subs(x, 0) == -3)
chk('и sympy согласен', sp.limit(NUM5/DEN5, x, 0) == -3)
# То, что печатает схема оценивания второй строкой, — та же вторая производная.
MS = (16*sp.sec(x)**4*sp.tan(x)**2 + 4*sp.sec(x)**6
      - 2*sp.sin(x)**2 + 2*sp.cos(x)**2)
chk('вторая строка схемы оценивания — это и есть вторая производная',
    sp.simplify(MS - sp.diff(NUM5, x, 2)) == 0)

print('\n=== Задача 6: три раунда или одна строка (май 2022 TZ1 P1 Q12) ===')
G6 = sp.exp(x)*sp.cos(x)
S6 = sp.series(G6, x, 0, 5).removeO()
chk('ряд Маклорена e^x cos x = 1 + x - x^3/3 - x^4/6',
    sp.expand(S6 - (1 + x - x**3/3 - x**4/6)) == 0)
chk('коэффициент при x^2 равен нулю', sp.expand(S6).coeff(x, 2) == 0)
chk('предел (e^x cos x - 1 - x)/x^3 равен -1/3',
    sp.limit((G6 - 1 - x)/x**3, x, 0) == -R(1, 3))
chk('ряд даёт то же самое', sp.expand(S6 - 1 - x).coeff(x, 3) == -R(1, 3))
# Лопиталь трижды — тем же ответом.
u6, v6 = G6 - 1 - x, x**3
for _ in range(3):
    u6, v6 = sp.diff(u6, x), sp.diff(v6, x)
chk('и правило Лопиталя трижды', sp.simplify(u6.subs(x, 0)/v6.subs(x, 0) + R(1, 3)) == 0)

print('\n=== Задача 7: степень наружу, параметр внутри ===')
E7 = (x**2*sp.exp(x) - x**2)**3/x**9
chk('предел (x^2 e^x - x^2)^3 / x^9 равен 1', sp.limit(E7, x, 0) == 1)
chk('он же куб предела (e^x - 1)/x',
    sp.limit((sp.exp(x) - 1)/x, x, 0)**3 == 1)
SN = sp.series(sp.cos(x)**n, x, 0, 3).removeO()
chk('ряд cos^n x = 1 - n x^2 / 2', sp.expand(SN - (1 - n*x**2/2)) == 0)
for value in (1, 2, 5, 9):
    chk(f'предел (cos^{value} x - 1)/x^2 равен -{value}/2',
        sp.limit((sp.cos(x)**value - 1)/x**2, x, 0) == -R(value, 2))

print('\n=== Задача 8: форма oo/oo (май 2023 TZ1 P3 · май 2025 TZ2 P2) ===')
AREA = (sp.exp(b) - b - 1)/sp.exp(b)
chk('числитель и знаменатель оба уходят в бесконечность',
    sp.limit(sp.exp(b) - b - 1, b, sp.oo) == sp.oo
    and sp.limit(sp.exp(b), b, sp.oo) == sp.oo)
chk('предел равен 1', sp.limit(AREA, b, sp.oo) == 1)
chk('а это и есть площадь под x e^-x от нуля до бесконечности',
    sp.integrate(x*sp.exp(-x), (x, 0, sp.oo)) == 1)
chk('предел (3x+1) e^-3x равен 0', sp.limit((3*x + 1)*sp.exp(-3*x), x, sp.oo) == 0)
# k находится из того, что плотность интегрируется в единицу.
k = sp.Symbol('k', positive=True)
total = sp.integrate(k*t*sp.exp(-3*t), (t, 0, sp.oo))
chk('интеграл плотности равен k/9', sp.simplify(total - k/9) == 0)
chk('значит k = 9', sp.solve(sp.Eq(total, 1), k) == [9])
chk('и данная в условии формула согласуется',
    sp.simplify(sp.integrate(9*t*sp.exp(-3*t), (t, 0, a))
                - 1*(1 - (3*a + 1)*sp.exp(-3*a))) == 0)
chk('хеш 8c', dn(9, 1) == kit.digest(sig(9, 1)))

print('\n=== Задача 9: постоянная, при которой предел существует ===')
K9 = sp.Symbol('K')
chk('числитель обнуляется только при k = pi/4',
    sp.solve(sp.Eq(sp.limit(sp.atan(sp.cos(x)) - K9, x, 0), 0), K9) == [sp.pi/4])
chk('при k = pi/4 предел равен -1/4',
    sp.limit((sp.atan(sp.cos(x)) - sp.pi/4)/x**2, x, 0) == -R(1, 4))
chk('при другом k предел бесконечен',
    sp.limit((sp.atan(sp.cos(x)) - 1)/x**2, x, 0) in (sp.oo, -sp.oo))
kk = sp.Symbol('kk', positive=True)
chk('предел sin^2(kx)/x^2 равен k^2',
    sp.simplify(sp.limit(sp.sin(kk*x)**2/x**2, x, 0) - kk**2) == 0)
chk('и из k^2 = 16 при k > 0 выходит k = 4',
    sp.solve(sp.Eq(sp.limit(sp.sin(kk*x)**2/x**2, x, 0), 16), kk) == [4])
chk('хеш 9c', dn(4, 1) == kit.digest(sig(4, 1)))

print('\n=== Задача 10: предел по параметру ===')
FN = m**n*x + c*(1 - m**n)/(1 - m)
# sp.limit не берёт m^n при отрицательном m: степень уходит в комплексную
# ветвь, хотя n здесь целое. Поэтому вывод идёт алгебраически — ровно так,
# как его пишут на бумаге: разность с предполагаемым пределом равна m^n,
# помноженному на постоянную, а |m|^n при |m| < 1 идёт в ноль.
nat = sp.Symbol('nat', integer=True, positive=True)
chk('разность с c/(1-m) равна m^n умножить на (x - c/(1-m))',
    sp.simplify(FN - c/(1 - m) - m**n*(x - c/(1 - m))) == 0)
for value in (R(1, 2), R(3, 4), R(9, 10)):
    chk(f'при |m| = {value} множитель m^n идёт в ноль',
        sp.limit(value**nat, nat, sp.oo) == 0)
chk('а при |m| >= 1 не идёт', sp.limit(R(5, 4)**nat, nat, sp.oo) == sp.oo)
for value in (R(1, 2), -R(3, 4), R(9, 10)):
    seq = [complex(FN.subs({m: value, c: 5, x: 3}).evalf(40, subs={n: 10**j}))
           for j in (2, 4, 6)]
    chk(f'при m = {value} последовательность садится на c/(1-m)',
        abs(seq[-1] - complex(sp.N((c/(1 - m)).subs({m: value, c: 5})))) < 1e-12)
COSTHETA = (sp.cos(1/n) + sp.sin(1/n))/sp.sqrt(2)
# n объявляется положительным: иначе norm() тащит Abs и не сворачивает
# sin^2 + cos^2 в единицу. В условии n принадлежит Z+, так что это не
# послабление, а перенос условия в объявление.
pos = sp.Symbol('pos', positive=True)
u10 = sp.Matrix([1, 1])
v10 = sp.Matrix([sp.cos(1/pos), sp.sin(1/pos)])
chk('вектор v единичный', sp.simplify(v10.norm()) == 1)
chk('cos(theta) = (cos(1/n) + sin(1/n))/sqrt 2',
    sp.simplify((u10.dot(v10)/(u10.norm()*v10.norm()))
                - COSTHETA.subs(n, pos)) == 0)
chk('предел cos(theta) равен 1/sqrt 2',
    sp.simplify(sp.limit(COSTHETA, n, sp.oo) - 1/sp.sqrt(2)) == 0)
chk('значит theta -> pi/4', sp.acos(1/sp.sqrt(2)) == sp.pi/4)
chk('хеш 10c', dn(sp.pi/4, 6) == kit.digest(sig(sp.pi/4, 6)))

print('\n=== Задача 11: Лопиталь с параметром (ноябрь 2022 P3 Q1) ===')
TOP = n*x**(n + 2) - (n + 1)*x**(n + 1) + x
F1 = TOP/(x - 1)**2
chk('числитель обнуляется при x = 1 при любом n',
    sp.simplify(TOP.subs(x, 1)) == 0)
chk('и знаменатель тоже', ((x - 1)**2).subs(x, 1) == 0)
for value in (2, 3, 7, 11):
    chk(f'при n = {value} предел равен n(n+1)/2 = {value*(value+1)//2}',
        sp.limit(F1.subs(n, value), x, 1) == R(value*(value + 1), 2))
# И то же самое напрямую: f_1(1) = 1 + 2 + ... + n.
i = sp.Symbol('i')
chk('а f_1(1) — это сумма 1 + 2 + ... + n',
    sp.simplify(sp.summation(i, (i, 1, n)) - n*(n + 1)/2) == 0)

print('\n=== Задача 12: предел по alpha и по композиции синусов ===')
G12 = (F + sp.tan(alpha))/(1 - F*sp.tan(alpha))
for value in (2, -3, R(1, 5)):
    chk(f'при f = {value} предел g равен -1/f',
        sp.simplify(sp.limit(G12.subs(F, value), alpha, sp.pi/2) + 1/value) == 0)
comp = sp.sin(x)
for depth in range(2, 8):
    comp = sp.sin(comp)
    chk(f'предел S_{depth}(x)/x равен 1', sp.limit(comp/x, x, 0) == 1)
chk('и производная композиции в нуле равна 1',
    sp.diff(sp.sin(sp.sin(sp.sin(x))), x).subs(x, 0) == 1)

print('\n=== На время: май 2025 TZ3 P1 Q9 ===')
TIMED = x*sp.sin(x)/(1 - sp.cos(x))
chk('форма 0/0',
    sp.limit(x*sp.sin(x), x, 0) == 0 and sp.limit(1 - sp.cos(x), x, 0) == 0)
chk('предел равен 2', sp.limit(TIMED, x, 0) == 2)
chk('через домножение на 1 + cos x получается x/sin x * (1 + cos x)',
    sp.simplify(TIMED - x*(1 + sp.cos(x))/sp.sin(x)) == 0)
chk('и это тоже даёт 2', sp.limit(x*(1 + sp.cos(x))/sp.sin(x), x, 0) == 2)

print('\n=== Ряды Маклорена: хеши ===')
chk('хеш 6a', kit.digest(kit._series_canon(1 + x - x**3/3 - x**4/6, x, 6))
    == kit.digest(kit._series_canon(sp.series(sp.exp(x)*sp.cos(x), x, 0, 5).removeO(), x, 6)))
chk('хеш 7b', kit.digest(kit._series_canon(1 - n*x**2/2, x, 6))
    == kit.digest(kit._series_canon(sp.series(sp.cos(x)**n, x, 0, 3).removeO(), x, 6)))

print('\n=== Тренажёр: ключи ===')
TRAINER = {
    1: ('cancel', (x**2 - 9)/(x - 3), 0, 3, 6),
    2: ('infinity', (5*x**2 - x)/(2*x**2 + 7), 0, sp.oo, R(5, 2)),
    4: ('lhopital', (sp.exp(2*x) - 1)/sp.sin(5*x), 0, 0, R(2, 5)),
    5: ('again', (1 - sp.cos(x) - x**2/2)/x**4, 0, 0, -R(1, 24)),
    6: ('series', (sp.log(1 + x) - x + x**2/2)/x**3, 0, 0, R(1, 3)),
    9: ('direct', sp.sin(x)/(1 + sp.cos(x)), 0, sp.pi/4, None),
    10: ('lhopital', x*sp.log(1 + 1/x), 0, sp.oo, 1),
    11: ('infinity', (3*x**3 + x)/(x**3 - 4*x**2), 0, -sp.oo, 3),
    12: ('series', (sp.tan(x) - x)/x**3, 0, 0, R(1, 3)),
}
for num, (code, expr, _, point, want) in TRAINER.items():
    got = sp.limit(expr, x, point)
    if want is None:
        want = sp.simplify(expr.subs(x, point))
    chk(f'тренажёр {num} ({code}): предел равен {want}', sp.simplify(got - want) == 0)
chk('тренажёр 3 (context): потолок логистической модели равен 800',
    sp.limit(800/(1 + 9*sp.exp(-R(4, 10)*t)), t, sp.oo) == 800)
chk('тренажёр 7 (finite): числитель обнуляется только при a = 2',
    sp.solve(sp.Eq(sp.limit(sp.sqrt(4 + x) - a, x, 0), 0), a) == [2])
chk('тренажёр 8 (parameter): при |m| < 1 остаётся b',
    sp.limit((m**n*a + b).subs(m, R(1, 3)), n, sp.oo) == b)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
