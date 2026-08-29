"""Прогоняет все проверки практикума B5 с ответами, выведенными заново.

Ответы не переписываются из раздела решений. Логарифмы считаются самой
sympy из определения, постоянные моделей — решением уравнения по данным
из условия, корни — solveset. Отдельно измеряется, что проверки отвергают:
сдвинутый отсчёт времени, вычитание инфляции вместо деления, посторонний
корень логарифмического уравнения, перевёрнутое неравенство.

Здесь же перепроверены расхождения с разметкой корпуса: один блок темы
mathematical_models к показательным и логарифмическим моделям отношения
не имеет, ещё один описывает квадратичную модель.

Проверки печатают по-английски: ноутбук английский, а сверяются здесь
ровно те же вызовы с теми же ярлыками. Комментарии остаются русскими —
это документация репозитория, а не материал ученика.

Запуск:  python practicum/tests/verify_b5.py
"""
import contextlib
import glob
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *                                                  # noqa: F403

R = sp.Rational
language('en')

NB = os.path.join(ROOT, 'practicum/functions',
                  'practicum-b5-exponential-log-models.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a_, b_, n_, p_, q_ = sp.symbols('a b n p q')
S_, T_, v0_ = sp.symbols('S T v0', positive=True)


def chk(name, verdict):
    res.append((name, verdict))
    if not verdict:
        print('FAIL:', name)


def kit_digest(value, sf):
    """Хеш ответа так же, как его считает check_num."""
    return digest(sig(value, sf))


def silent(fn, *args, **kwargs):
    """Вызвать проверку, не печатая её вердикт: нас интересует только он."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


def ok(fn, *args, **kwargs):
    return silent(fn, *args, **kwargs)[0]


def says(fn, *args, **kwargs):
    return silent(fn, *args, **kwargs)[1]


print('=== хеши из ноутбука прочитаны ===')
print(' '.join(sorted(D)))
chk('хешей ровно десять', len(D) == 10)

# ---------------------------------------------------------------- Часть I
print('\n=== Задание 1: законы логарифма ===')
# log_10 24 выводится, а не переписывается: 24 = 2^3 * 3.
lg = lambda z: sp.log(z, 10)
chk('1a: 3p + q — это и есть log 24',
  sp.simplify(3 * lg(2) + lg(3) - lg(24)) == 0)
chk('1a: проверка принимает 3p + q',
  ok(verify_in_terms_of, '1a', 3 * p_ + q_, lg(24), {p_: lg(2), q_: lg(3)}))
chk('1a: и отвергает 3pq',
  not ok(verify_in_terms_of, '1a', 3 * p_ * q_, lg(24), {p_: lg(2), q_: lg(3)}))
chk('1a: и отвергает переписанный сам через себя ответ',
  not ok(verify_in_terms_of, '1a', lg(24), lg(24), {p_: lg(2), q_: lg(3)}))
chk('1b: 1 + log_2 n = log_2 2n',
  ok(verify_identity, '1b', sp.log(2 * n_, 2), 1 + sp.log(n_, 2), var=n_))
chk('1b: log_2(n+1) не годится',
  not ok(verify_identity, '1b', sp.log(n_ + 1, 2), 1 + sp.log(n_, 2), var=n_))
chk('1b: и неравенство 2n >= n+1 верно при n >= 1',
  sp.solveset(2 * n_ - (n_ + 1) >= 0, n_, sp.S.Reals) == sp.Interval(1, sp.oo))

print('\n=== Задание 2: смена основания ===')
chk('2a: log_3 8 = 3p/q',
  sp.simplify(3 * lg(2) / lg(3) - sp.log(8, 3)) == 0)
chk('2a: проверка принимает 3p/q',
  ok(verify_in_terms_of, '2a', 3 * p_ / q_, sp.log(8, 3), {p_: lg(2), q_: lg(3)}))
chk('2a: и отвергает перевёрнутую дробь',
  not ok(verify_in_terms_of, '2a', q_ / (3 * p_), sp.log(8, 3),
         {p_: lg(2), q_: lg(3)}))
# log_10 a = 1/3, значит a = 10^{1/3}; обе величины считаются из этого.
A10 = sp.Integer(10)**R(1, 3)
chk('2b: log_10 (1/a) = -1/3', sp.simplify(lg(1 / A10) + R(1, 3)) == 0)
chk('2c: log_1000 a = 1/9', sp.simplify(sp.log(A10, 1000) - R(1, 9)) == 0)
chk('2b: проверка принимает -1/3', ok(verify_exact, '2b', -R(1, 3), -R(1, 3)))
chk('2b: десятичная запись не принимается',
  not ok(verify_exact, '2b', -0.333333, -R(1, 3)))

print('\n=== Задания 3 и 4: логарифмические уравнения ===')
eq3 = 3 * sp.log(10 * x, 8) - sp.log(x, 4) - 1
chk('3: корень выводится решением, а не берётся из разбора',
  sp.solveset(eq3, x, sp.Interval.open(0, sp.oo)) == sp.FiniteSet(R(1, 25)))
chk('3: проверка принимает [1/25]',
  ok(verify_roots, '3', [R(1, 25)], eq3, (0.0001, 100)))
chk('3: и отвергает 1/5 — остановку на sqrt(x)',
  not ok(verify_roots, '3', [R(1, 5)], eq3, (0.0001, 100)))
eq4 = sp.Eq(sp.log(x * (x**2 - 1), 2) - 1,
            sp.log((x**2 - 8 * x + 7) * (x + 1), 2))
chk('4a: разложение x^2-8x+7 = (x-7)(x-1)',
  sp.factor(x**2 - 8 * x + 7) == (x - 7) * (x - 1))
chk('4a: проверка отвергает нераскрытый ответ',
  not ok(verify_factored, '4a', x**2 - 8 * x + 7, x**2 - 8 * x + 7, n=2))
chk('4b: тождество части (a) действительно выполняется',
  sp.simplify(x / (x**2 - 8 * x + 7) * (x**2 - 1) / (x + 1) - x / (x - 7)) == 0)
chk('4b: x = 14 — корень', sp.simplify(eq4.lhs.subs(x, 14) - eq4.rhs.subs(x, 14)) == 0)
chk('4b: проверка принимает [14]',
  ok(verify_root_set, '4b', [14], eq4, domain=sp.Interval.open(7, sp.oo)))
chk('4b: и отвергает список с корнем вне области',
  not ok(verify_root_set, '4b', [14, -1], eq4, domain=sp.Interval.open(7, sp.oo)))

# --------------------------------------------------------------- Часть II
print('\n=== Задание 5: законы показателей ===')
chk('5a: e^{-T} = 1/(1+v0), а не 1+v0',
  ok(verify_identity, '5a', 1 / (1 + v0_), 1 / (1 + v0_), var=v0_)
  and not ok(verify_identity, '5a', 1 + v0_, 1 / (1 + v0_), var=v0_))
# v(T-k) считается подстановкой, а не переписыванием ответа.
vt = (1 + v0_) * sp.exp(-t) - 1
vTk = vt.subs(t, T_ - k).subs(v0_, sp.exp(T_) - 1)
chk('5b: v(T-k) действительно сводится к e^k - 1',
  sp.simplify(vTk - (sp.exp(k) - 1)) == 0)
vTk2 = vt.subs(t, T_ + k).subs(v0_, sp.exp(T_) - 1)
chk('5b: и v(T+k) — к e^{-k} - 1',
  sp.simplify(vTk2 - (sp.exp(-k) - 1)) == 0)
chk('5b: проверка принимает точный ответ',
  ok(verify_exact, '5b', sp.exp(-k) - 1, sp.exp(-k) - 1))
chk('5b: и отвергает e^k - 1 — забытую замену знака',
  not ok(verify_exact, '5b', sp.exp(k) - 1, sp.exp(-k) - 1))

print('\n=== Задание 6: период полураспада ===')
k6 = list(sp.solveset(sp.Eq(100 * sp.exp(-k * 5730), 50), k, sp.S.Reals))[0]
chk('6a: k выводится из условия и равен ln2/5730', sp.simplify(k6 - sp.log(2) / 5730) == 0)
t6 = list(sp.solveset(sp.Eq(100 * sp.exp(-k6 * t), 75), t, sp.S.Reals))[0]
chk('6b: время до 75 единиц равно 5730 ln(4/3)/ln 2',
  sp.simplify(t6 - 5730 * sp.log(R(4, 3)) / sp.log(2)) == 0)
chk('6b: округление до десятка даёт 2380',
  10 * round(float(t6) / 10) == 2380 and D['6b'] == kit_digest(2380, 3))
model6 = 100 * sp.exp(-k6 * t)
chk('6c: модель воспроизводит 100, 50 и 25',
  ok(verify_model, '6c', model6, [(0, 100), (5730, 50), (11460, 25)]))
chk('6c: та же модель как 100*2^{-t/5730}',
  ok(verify_model, '6c', 100 * 2**(-t / 5730), [(0, 100), (5730, 50), (11460, 25)]))
chk('6c: со знаком плюс в показателе — нет',
  not ok(verify_model, '6c', 100 * sp.exp(k6 * t), [(0, 100), (5730, 50)]))

print('\n=== Задания 7 и 8: проценты ===')
car = 30000 * R(85, 100)**10
chk('7a: 30000*0.85^10 = 5906.23...', abs(float(car) - 5906.23) < 0.005)
chk('7a: хеш ноутбука отвечает этому числу', D['7a'] == kit_digest(car, 6))
real = R(1015, 1000) / R(1008, 1000)
n7 = sp.log(R(11, 10)) / sp.log(real)
chk('7b: точный множитель — частное 1.015/1.008',
  abs(float(real) - 1.00694) < 1e-5)
chk('7b: первый месяц выше 55000 — четырнадцатый',
  sp.ceiling(n7) == 14 and 50000 * float(real)**13 < 55000 < 50000 * float(real)**14)
chk('7b: METHOD 1 markscheme — разность 0.7% — даёт тот же месяц',
  sp.ceiling(sp.log(R(11, 10)) / sp.log(R(1007, 1000))) == 14
  and abs(float(sp.log(R(11, 10)) / sp.log(R(1007, 1000))) - 13.6633) < 1e-3)
chk('7b: и её крайние значения совпадают с напечатанными в markscheme',
  abs(50000 * 1.007**13 - 54746.09) < 0.01
  and abs(50000 * 1.007**14 - 55129.31) < 0.01)
chk('7b: 164 месяца получаются, если 0.7% принять за годовую ставку',
  sp.ceiling(sp.log(R(11, 10)) / sp.log(1 + R(7, 12000))) == 164)
chk('7b: хеш ноутбука отвечает 14', D['7b'] == kit_digest(14, 2))
chk('8a: квартальная ставка равна 1/100', sp.Rational(4, 400) == R(1, 100))
chk('8b: 1000*1.01^4 округляется до 1041',
  round(float(1000 * R(101, 100)**4)) == 1041 and D['8b'] == kit_digest(1041, 4))
chk('8c: 1000*(1 + 4(0.1) + 10(0.01) + 20(0.001)) = 1520',
  1000 * (1 + 4 * R(1, 10) + 10 * R(1, 100) + 20 * R(1, 1000)) == 1520
  and D['8c'] == kit_digest(1520, 3))
chk('8c: точное значение 1000/0.9^4 всё же 1524, ряд обрезан',
  abs(float(1000 / R(9, 10)**4) - 1524.16) < 0.01)

print('\n=== Задание 9: логистическая модель ===')
C9 = list(sp.solveset(sp.Eq(200 / (1 + sp.Symbol('C0')), 40),
                      sp.Symbol('C0'), sp.S.Reals))[0]
chk('9a: C = 4 выводится из x(0) = 40', C9 == 4)
k9 = list(sp.solveset(sp.Eq(200 / (1 + 4 * sp.exp(-5 * k)), 70), k, sp.S.Reals))[0]
chk('9b: k = (1/5)ln(28/13)', sp.simplify(k9 - sp.log(R(28, 13)) / 5) == 0)
chk('9b: и это 0.153 с тремя значащими цифрами',
  abs(float(k9) - 0.153451) < 1e-5 and D['9b'] == kit_digest(k9, 3))
model9 = 200 / (1 + 4 * sp.exp(-k9 * t))
chk('9c: модель воспроизводит 40 и 70',
  ok(verify_model, '9c', model9, [(0, 40), (5, 70), (10, 107.397)]))
chk('9d: x(10) округляется до 107',
  round(float(model9.subs(t, 10))) == 107 and D['9d'] == kit_digest(107, 3))
chk('9: при большом t модель подходит к 200 снизу',
  180 < float(model9.subs(t, 40)) < 200)
chk('9: с потерянным знаком k она вместо этого падает',
  float((200 / (1 + 4 * sp.exp(k9 * t))).subs(t, 40)) < 1)

# -------------------------------------------------------------- Часть III
print('\n=== Задание 10: композиция ===')
f10 = 5 * (x + 1) * (x + 3)
chk('10a: (f o g)(x) = 5(ln x + 1)(ln x + 3)',
  sp.simplify(f10.subs(x, sp.log(x)) - 5 * (sp.log(x) + 1) * (sp.log(x) + 3)) == 0)
chk('10b: множество решений — [e^-5, e]',
  sp.solveset(f10.subs(x, sp.log(x)) <= 40, x, sp.Interval.open(0, sp.oo))
  == sp.Interval(sp.exp(-5), sp.E))
chk('10b: проверка принимает Interval(exp(-5), E)',
  ok(verify_solution_set, '10b', sp.Interval(sp.exp(-5), sp.E),
     f10.subs(x, sp.log(x)) <= 40, domain=sp.Interval.open(0, sp.oo)))
chk('10b: и отвергает -e^5 вместо e^-5',
  not ok(verify_solution_set, '10b', sp.Interval(-sp.exp(5), sp.E),
         f10.subs(x, sp.log(x)) <= 40, domain=sp.Interval.open(0, sp.oo)))
dom10 = sp.Union(sp.Interval.open(-sp.oo, -3), sp.Interval.open(-1, sp.oo))
chk('10c: область g o f — два открытых луча',
  sp.solveset(f10 > 0, x, sp.S.Reals) == dom10)
chk('10c: проверка принимает объединение',
  ok(verify_solution_set, '10c', dom10, f10 > 0))
chk('10c: и отвергает внутренность параболы',
  not ok(verify_solution_set, '10c', sp.Interval.open(-3, -1), f10 > 0))

print('\n=== Задание 11: логарифмическая шкала ===')
loud = lambda inten: 10 * sp.log(inten * 10**12, 10)
chk('11: шкала согласована с условием — 10^-6 даёт ровно 60',
  sp.simplify(loud(sp.Integer(10)**-6) - 60) == 0)
chk('11a: удвоенная интенсивность равна 2*10^-6',
  ok(verify_exact, '11a', 2 * R(1, 10**6), 2 * R(1, 10**6)))
L2 = loud(2 * sp.Integer(10)**-6)
chk('11b: громкость S2 равна 60 + 10 log 2, то есть 63.0',
  sp.simplify(L2 - (60 + 10 * sp.log(2, 10))) == 0
  and abs(float(L2) - 63.0102) < 1e-3 and D['11b'] == kit_digest(L2, 3))
chk('11b: удвоение интенсивности прибавляет около 3 децибел, а не удваивает',
  abs(float(L2) - 60 - 3.0103) < 1e-3)
I0 = sp.Symbol('I0', positive=True)
I3 = list(sp.solveset(sp.Eq(loud(I0), 115), I0, sp.Interval.open(0, sp.oo)))[0]
chk('11c: интенсивность грома равна 10^{-1/2}',
  sp.simplify(I3 - sp.Integer(10)**R(-1, 2)) == 0
  and D['11c'] == kit_digest(I3, 3))

print('\n=== Задание 12: логарифм, за которым стоит степень ===')
chk('12a: M_3(12) = 64, M_4(12) = 81, M_5(12) = 12^5/5^5',
  (R(12, 3))**3 == 64 and (R(12, 4))**4 == 81
  and (R(12, 5))**5 == R(248832, 3125))
chk('12a: и пятое значение действительно 79.6',
  abs(float(R(12, 5)**5) - 79.62624) < 1e-5)
chk('12a: максимум сидит между n = 4 и n = 5, около S/e',
  4 < float(12 / sp.E) < 5)
xp = sp.Symbol('x', positive=True)
chk('12b: g(x) = (S/x)^x решает ln(g) = x ln(S/x)',
  sp.simplify(sp.log((S_ / xp)**xp) - xp * sp.log(S_ / xp)) == 0)
chk('12b: проверка принимает (S/x)^x',
  ok(verify_identity, '12b', (S_ / x)**x, sp.exp(x * sp.log(S_ / x)), var=x))
chk('12b: и отвергает (x/S)^x',
  not ok(verify_identity, '12b', (x / S_)**x, sp.exp(x * sp.log(S_ / x)), var=x))

print('\n=== Задание на время: ноябрь 2022 ===')
kT = list(sp.solveset(sp.Eq(15000 * sp.exp(8 * k), 13350), k, sp.S.Reals))[0]
chk('t: k = ln(0.89)/8', sp.simplify(kT - sp.log(R(89, 100)) / 8) == 0)
modelT = 15000 * sp.exp(kT * t)
chk('t: модель воспроизводит 15000 и 13350',
  ok(verify_model, 'timed', modelT, [(0, 15000), (8, 13350)]))
chk('t: P(27) = 10122.3, три значащих цифры дают 10100',
  abs(float(modelT.subs(t, 27)) - 10122.3) < 0.1
  and D['timed answer'] == kit_digest(modelT.subs(t, 27), 3))
chk('t: отсчёт от 2022 вместо 2014 даёт другое число',
  abs(float(modelT.subs(t, 19)) - float(modelT.subs(t, 27))) > 1000)
chk('t: множитель 0.11 вместо 0.89 модель не проходит',
  not ok(verify_model, 'timed', 15000 * sp.exp(sp.log(R(11, 100)) / 8 * t),
         [(0, 15000), (8, 13350)]))

print('\n=== сообщения проверок называют беду, но не ответ ===')
msg = says(verify_model, 'x', 15000 * sp.exp(-kT * t), [(0, 15000), (8, 13350)])
chk('verify_model называет точку, где модель разошлась', 't = 8' in msg)
msg = says(verify_root_set, 'x', [14, -1], eq4, domain=sp.Interval.open(7, sp.oo))
chk('verify_root_set объясняет, что корень вне области', 'domain' in msg)

print('\n=== замечания к корпусу ===')
blocks = {}
for path in sorted(glob.glob(os.path.join(
        ROOT, 'classification/generated/*/*/paper-*.json'))):
    for blk in json.load(open(path))['blocks']:
        blocks.setdefault(blk['id'], blk)
b = blocks['2025-NOV-TZ3-P1-Q08-A']
chk('корпус: пляжный блок помечен mathematical_models',
  b['primary_topic'] == 'functions.mathematical_models')
chk('корпус: и ни показательной, ни логарифмической функции в нём нет',
  'sec' in b['task_summary'] and 'log' not in b['task_summary'].lower()
  and 'exp' not in b['task_summary'].lower())
b = blocks['2023-MAY-TZ1-P2-Q03-A']
chk('корпус: модель парка квадратичная, а не показательная',
  'quadratic' in b['task_summary'].lower())

TOPICS = {'functions.logarithmic_functions', 'functions.exponential_models',
          'functions.mathematical_models', 'number_algebra.exponential_models'}
mine = [b for b in blocks.values() if b['primary_topic'] in TOPICS]
chk('корпус: тема даёт 37 блоков и 85 баллов',
  len(mine) == 37 and sum(b.get('marks', 0) for b in mine) == 85)

bad = [name for name, verdict in res if not verdict]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
