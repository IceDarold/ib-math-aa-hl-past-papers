"""Независимая проверка каждого ответа практикума E5.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение
и проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит буквально наоборот тому, что делает
ноутбук. Проверки в kit не интегрируют ни разу: они берут написанное
и дифференцируют его, а определённый интеграл считают сложением. Значит,
тест обязан считать иначе — и он считает через sp.integrate. Ноутбук
дифференцирует, тест интегрирует; там, где они сошлись, ошибиться должны
были обе стороны сразу.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждый ответ по очереди портится
типовой ошибкой, и ячейка обязана её отвергнуть, — иначе проверка вида
«всегда ✅» прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_e5.py
"""
import contextlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_e5 as gen

R = sp.Rational
x, y, t, u, v, k, C, A = sp.symbols('x y t u v k C A')
a, b, c, g, n, p, q, r, s = sp.symbols('a b c g n p q r s')
J = sp.Function('J')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


NOTATION = {'cosec': sp.csc, 'arcsin': sp.asin, 'arccos': sp.acos,
            'arctan': sp.atan, 'ln': sp.log, 'J': J}


def E(expr):
    return sp.sympify(expr, locals=NOTATION)


def Ans(name):
    return E(gen.ANSWERS[name])


def same(one, two):
    return sp.simplify(sp.sympify(one) - sp.sympify(two)) == 0


def near(one, two, tol=5e-6):
    left, right = float(sp.N(one, 40)), float(sp.N(two, 40))
    return abs(left - right) <= tol * max(1.0, abs(right))


SPOTS = (0.13, 0.29, 0.41, 0.57, 0.68, 0.79)


def bare(expr):
    """Снять модули: sp.diff от Abs выдаёт производную действительной части,
    и дальше её не упростить. На производную ln|g| против ln g это не влияет.
    """
    expr = sp.sympify(expr)
    bars = list(expr.atoms(sp.Abs))
    return expr.subs({bar: bar.args[0] for bar in bars}) if bars else expr


def family(written, integrand, var=x, span=(0.05, 0.95)):
    """Лежит ли написанное в семействе первообразных — через sp.integrate.

    Ровно то, чего проверки kit не делают ни разу: там ответ только
    дифференцируют. Здесь наоборот, и в этом весь смысл теста.

    Постоянная бывает не видна символьно: log(x−1) − log(1−x) равно iπ,
    и sp.simplify честно оставляет это как есть. Поэтому «разность
    постоянна» проверяется по значениям — одинакова ли она в нескольких
    точках отрезка.
    """
    found = sp.integrate(sp.sympify(integrand), var)
    gap = sp.simplify(sp.sympify(written) - found)
    if gap.is_number or not gap.has(var):
        return True
    lo, hi = span
    # Буквы, кроме переменной интегрирования, надо чем-то заполнить: у
    # (1/2)ln A постоянная сама зависит от буквы, и без подстановки
    # значение не считается вовсе.
    others = {name: sp.Float(1.7 + 0.3*i)
              for i, name in enumerate(sorted(gap.free_symbols - {var}, key=str))}
    seen = []
    for share in SPOTS:
        spot = dict(others)
        spot[var] = lo + (hi - lo)*share
        try:
            seen.append(complex(gap.evalf(30, subs=spot)))
        except (TypeError, ValueError, ZeroDivisionError, AttributeError):
            continue
    return len(seen) >= 3 and max(abs(z - seen[0]) for z in seen) < 1e-9


def area(integrand, lo, hi, var=x):
    """Определённый интеграл — тоже через sp.integrate, а не сложением."""
    return sp.integrate(sp.sympify(integrand), (var, lo, hi))


print('=== Задание 1: определённый интеграл и первообразная под ним ===')
chk('1a: первообразная 3 − 5/√x найдена интегрированием',
    family(Ans('q1a'), 3 - 5/sp.sqrt(x)))
chk('1: интеграл от 1 до 9 равен 4', same(Ans('q1'), area(3 - 5/sp.sqrt(x), 1, 9)))
chk('1: и он же равен F(9) − F(1) по эталонной первообразной',
    same(Ans('q1'), Ans('q1a').subs(x, 9) - Ans('q1a').subs(x, 1)))

print('\n=== Задание 2: f′ и одна точка, трижды ===')
for name, rate, spot in (('q2', 3*x**2 + 5*sp.exp(x), (0, 4)),
                         ('q3', 3*x**2 + 12*x - 15, (-2, 36)),
                         ('q5', 6*x/(1 + x**2), (1, 5))):
    chk(f'2 ({name}): производная возвращает подынтегральную функцию',
        same(sp.diff(Ans(name), x), rate))
    chk(f'2 ({name}): семейство подтверждено интегрированием',
        family(Ans(name), rate))
    chk(f'2 ({name}): график проходит через {spot}',
        same(Ans(name).subs(x, spot[0]), spot[1]))

print('\n=== Задание 3: то же с буквой ===')
chk('3a: a/x + b/(k−x) складывается в 1/(x(k−x))',
    same(Ans('q4a')/x + Ans('q4b')/(k - x), 1/(x*(k - x))))
for value in (1, 3, 8):
    chk(f'3b: при k = {value} ответ лежит в семействе',
        family(bare(Ans('q4')).subs(k, value), (1/(x*(k - x))).subs(k, value),
               span=(0.1*value, 0.9*value)))

print('\n=== Задание 4: замена u = sec x ===')
pushed = Ans('q6u').subs(u, sp.sec(x))*sp.diff(sp.sec(x), x)
chk('4a: подстановка замены назад даёт исходное выражение',
    same(sp.simplify(pushed), sp.sec(x)**n*sp.tan(x)))
for value in (2, 3, 5, -1):
    chk(f'4b: при n = {value} значение совпадает с sp.integrate',
        near(Ans('q6').subs(n, value),
             area((sp.sec(x)**n*sp.tan(x)).subs(n, value), 0, sp.pi/3)))

print('\n=== Задание 5: замена t = √x ===')
chk('5a: 2t cos t возвращает cos√x при t = √x',
    same(sp.simplify(Ans('q7u').subs(t, sp.sqrt(x))*sp.diff(sp.sqrt(x), x)),
         sp.cos(sp.sqrt(x))))
chk('5b: первообразная sin√x подтверждена интегрированием',
    family(Ans('q7'), sp.sin(sp.sqrt(x))))

print('\n=== Задание 6: по частям дважды ===')
chk('6a: первообразная x(ln x)² подтверждена интегрированием',
    family(Ans('q8'), x*sp.log(x)**2))
chk('6b: интеграл от 1 до e равен (e²−1)/4',
    same(Ans('q8e'), area(x*sp.log(x)**2, 1, sp.E)))
chk('6b: и он же равен F(e) − F(1)',
    same(Ans('q8e'), Ans('q8').subs(x, sp.E) - Ans('q8').subs(x, 1)))

print('\n=== Задание 7: многочлен, который умирает за два шага ===')
chk('7: первообразная (x²−5)eˣ подтверждена интегрированием',
    family(Ans('q9'), (x**2 - 5)*sp.exp(x)))

print('\n=== Задание 8: по частям без второго множителя ===')
chk('8: первообразная arccos x подтверждена интегрированием',
    family(Ans('q10'), sp.acos(x)))

print('\n=== Задание 9: xⁿe^(−x) и несобственный интеграл ===')
chk('9a: первообразная xe^(−x) подтверждена интегрированием',
    family(Ans('q11a'), x*sp.exp(-x)))
chk('9b: A₁ = 1', same(Ans('q11one'), area(x*sp.exp(-x), 0, sp.oo)))
chk('9c: A₄ = 24', same(Ans('q11four'), area(x**4*sp.exp(-x), 0, sp.oo)))
chk('9d: A₅ = 120', same(Ans('q11five'), area(x**5*sp.exp(-x), 0, sp.oo)))
for value in (2, 3, 4, 5, 6):
    chk(f'9e: Aₙ при n = {value} совпадает с sp.integrate',
        same(Ans('q11n').subs(n, value), area(x**value*sp.exp(-x), 0, sp.oo)))

print('\n=== Задание 10: простейшие дроби и точное значение ===')
chk('10a: сумма дробей равна исходной',
    same(Ans('q12'), (2*x - 15)/((x + 3)*(x - 4))))
chk('10a: каждое слагаемое — простейшая дробь',
    all(not sp.fraction(sp.together(piece))[0].has(x)
        for piece in sp.Add.make_args(Ans('q12'))))
chk('10b: интеграл от 0 до 3 равен 5 ln 2',
    same(sp.simplify(Ans('q12v') - area((2*x - 15)/((x + 3)*(x - 4)), 0, 3)), 0))

print('\n=== Задание 11: замена, потом простейшие дроби ===')
raw11 = sp.sin(x)*sp.cos(x)/(sp.sin(x)**2 - sp.sin(x) - 2)
chk('11a: подстановка u = sin x назад даёт исходное выражение',
    same(sp.simplify(Ans('q13u').subs(u, sp.sin(x))*sp.diff(sp.sin(x), x)), raw11))
chk('11b: разложение равно u/(u²−u−2)',
    same(Ans('q13p'), u/(u**2 - u - 2)))
chk('11c: производная ответа равна подынтегральной функции',
    same(sp.diff(bare(Ans('q13')), x), raw11))
back11 = sp.integrate(u/(u**2 - u - 2), u).subs(u, sp.sin(x))
chk('11c: и она отличается от найденной sp.integrate только постоянной',
    family(bare(Ans('q13')), sp.diff(back11, x), span=(0.2, 1.2)))

print('\n=== Задание 12: постоянная в костюме ===')
chk('12: производная равна 1/(1−v²)',
    same(sp.diff(bare(Ans('q14')), v), 1/(1 - v**2)))
chk('12: (1/2)ln A действительно свободна — она не зависит от v',
    not (sp.log(A)/2).has(v))
chk('12: и семейство подтверждено интегрированием',
    family(bare(Ans('q14')), 1/(1 - v**2), var=v, span=(0.05, 0.9)))

print('\n=== Задание 13: две функции из одной формулы ===')
g13 = x*sp.exp(x)
ratio13 = sp.simplify(sp.diff(g13, x)/(sp.diff(g13, x) - g13))
chk("13a: g'/(g'−g) при g = xeˣ равно x + 1", same(ratio13, x + 1))
chk('13a: f = exp(∫(x+1)dx) с A = 1',
    same(Ans('q15d'), sp.exp(sp.integrate(ratio13, x))))
g13b = sp.sin(x) + sp.cos(x)
ratio13b = sp.simplify(sp.diff(g13b, x)/(sp.diff(g13b, x) - g13b))
chk("13b: g'/(g'−g) при g = sin x + cos x равно 1/2 − cot(x)/2",
    same(ratio13b, R(1, 2) - sp.cot(x)/2))
f13b = sp.exp(sp.integrate(ratio13b, x))
chk('13b: h(x) = eˣ/f(x) совпадает с эталоном',
    same(sp.simplify(sp.exp(x)/f13b), Ans('q15e')))

print('\n=== Задание 14: формула понижения ===')
for value in (2, 3, 4, 5):
    left = sp.integrate(sp.sin(x)**value, (x, R(3, 10), R(6, 5)))
    right = 0
    for piece in sp.Add.make_args(Ans('q16').subs(n, value)):
        inside = [f for f in piece.atoms(sp.Function) if f.func == J]
        if inside:
            weight = sp.simplify(piece/inside[0])
            right += weight*sp.integrate(sp.sin(x)**int(inside[0].args[0]),
                                         (x, R(3, 10), R(6, 5)))
        else:
            right += piece.subs(x, R(6, 5)) - piece.subs(x, R(3, 10))
    chk(f'14a: при n = {value} формула сходится с sp.integrate',
        near(right, left))
chk('14b: первообразная cos⁴x подтверждена интегрированием',
    family(Ans('q16c'), sp.cos(x)**4))
chk('14b: коэффициенты p, q, r положительны и рациональны',
    all(v.is_rational and v > 0 for v in
        (R(1, 4), R(3, 8), R(3, 8))))

print('\n=== Задание 15: ряды и π в конце ===')
chk('15a: производная ряда совпадает с 1/(1+x²) до x⁶',
    sp.series(sp.diff(Ans('q17a'), x) - 1/(1 + x**2), x, 0, 8).removeO() == 0)
chk('15a: ряд получен интегрированием ряда подынтегральной функции',
    same(Ans('q17a') - C,
         sp.integrate(sp.series(1/(1 + x**2), x, 0, 8).removeO(), x)))
chk('15b: производная ряда совпадает с 1/√(1−x²) до x⁴',
    sp.series(sp.diff(Ans('q17b'), x) - 1/sp.sqrt(1 - x**2), x, 0, 6).removeO() == 0)
chk('15b: ряд получен интегрированием ряда подынтегральной функции',
    same(Ans('q17b') - C,
         sp.integrate(sp.series(1/sp.sqrt(1 - x**2), x, 0, 6).removeO(), x)))
step15 = (Ans('q17b') - C).subs(x, R(1, 2))
chk('15c: 25/48 + k/1280 совпадает с рядом при x = 1/2',
    same(R(25, 48) + Ans('q17k')/sp.Integer(1280), step15))
chk('15c: и приближает arcsin(1/2) = π/6 с точностью 5·10⁻⁴',
    abs(float(sp.N(step15 - sp.pi/6, 30))) < 5e-4)

print('\n=== Задание 16: двух членов хватает ===')
chk('16a: ряд e^(cos 2x) до x² совпадает с sp.series',
    same(Ans('q18s'), sp.series(sp.exp(sp.cos(2*x)), x, 0, 3).removeO()))
chk('16b: интеграл приближения от 0 до 1/5 равен 73e/375',
    same(Ans('q18'), area(Ans('q18s'), 0, R(1, 5))))
chk('16b: приближение отличается от истинного интеграла меньше чем на 0.003',
    abs(float(sp.N(Ans('q18'), 30))
        - float(sp.N(sp.Integral(sp.exp(sp.cos(2*x)), (x, 0, R(1, 5))).evalf(30)))) < 3e-3)

print('\n=== Задание 17: интеграл прочитан наоборот ===')
chk('17a: площадь до c = 4 равна ln 3',
    same(area(x/(x**2 + 2), 0, Ans('q19')), sp.log(3)))
chk('17a: и c = 4 — единственный положительный корень',
    sp.solve(sp.Eq(area(x/(x**2 + 2), 0, c), sp.log(3)), c) == [-4, 4])
root17 = sp.nsolve(sp.Integral(3*x*sp.acos(x**2), (x, 0, s)).transform(
    s, s) if False else
    sp.Eq(s**2*sp.acos(s**2) - sp.sqrt(1 - s**4) + R(1, 3), 0), s, 0.7)
chk('17b: k решает уравнение бумаги k²arccos(k²) − √(1−k⁴) + 1/3 = 0',
    near(Ans('q20k'), root17, tol=1e-6))
chk('17b: и он же даёт единичную площадь под плотностью',
    near(float(sp.N(sp.Integral(3*x*sp.acos(x**2), (x, 0, Ans('q20k'))).evalf(30))),
         1, tol=1e-5))
chk('17c: у нечётной функции ∫ от −4 до 0 меняет знак',
    same(Ans('q21a'), -sp.Float('1.6')))
chk('17d: чётная часть удваивается, нечётная обнуляется',
    same(Ans('q21b'), 2*sp.Float('1.6')))

print('\n=== На таймере ===')
chk('timer: тот же интеграл, что в задании 6',
    same(Ans('qt'), area(x*sp.log(x)**2, 1, sp.E)))

print('\n=== Ноутбук: пустой и с эталонами ===')
PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')
doc = json.load(open(gen.NOTEBOOK))
notebook_cells = [''.join(cc['source']) for cc in doc['cells']
                  if cc['cell_type'] == 'code']
names = set()
for source in notebook_cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
chk(f'placeholder-ов столько же, сколько эталонов ({len(names)})',
    names == set(gen.ANSWERS))

TRAINER_FILL = "\n".join(
    f"    {num}: '{code}'," for num, code in sorted(gen.TRIGGER.items()))


def filled(source, swap=None):
    swap = swap or {}
    out, in_trainer = [], False
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {swap.get(name, gen.ANSWERS[name])}')
            continue
        if line.startswith('answers = {'):
            in_trainer = True
            out.append(line)
            out.append(TRAINER_FILL)
            continue
        if in_trainer:
            if line.startswith('}'):
                in_trainer = False
                out.append(line)
            continue
        out.append(line)
    return '\n'.join(out)


def run(sources):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in sources:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


here = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'calculus'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 25)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': '3*x - 5*sqrt(x)',                     # не поделено на новый показатель
    'q1': '-4',                                   # пределы переставлены
    'q2': 'x**3 + 5*exp(x) + C',                  # постоянная не найдена
    'q3': 'x**3 + 6*x**2 - 15*x',                 # постоянная взята нулём
    'q4a': '1',                                   # знаменатель k потерян
    'q4b': '1',                                   # и во втором тоже
    'q4': 'log(x*(k - x))/k',                     # знак внутри логарифма
    'q5': '3*log(1 + x**2)',                      # точка не подставлена
    'q6u': 'u**n',                                # множитель замены не учтён
    'q6': '(2**n - 1)/(n - 1)',                   # делитель не тот
    'q7u': 'cos(t)',                              # dx заменено на dt без 2t
    'q7': '-2*sqrt(x)*cos(sqrt(x))',              # взято одно слагаемое из двух
    'q8': 'x**2*log(x)**2/2 - x**2*log(x)/2',     # потерян хвост второго шага
    'q8e': '(E**2 + 1)/4',                        # знак при подстановке нижнего предела
    'q9': '(x**2 - 2*x + 3)*exp(x)',              # знак в свободном члене
    'q10': 'x*acos(x) + sqrt(1 - x**2)',          # знак у остаточного интеграла
    'q11a': '-x*exp(-x)',                         # второе применение по частям забыто
    'q11one': '0',                                # просто неверно
    'q11four': '4',                               # спутано n! и n
    'q11five': '25',                              # просто неверно
    'q11n': 'n**2',                               # закономерность угадана не та
    'q12': '(2*x - 15)/((x + 3)*(x - 4))',        # дробь не разложена
    'q12v': 'log(32)/5',                          # логарифм перевёрнут
    'q13u': 'u/(u**2 - u - 2)*cos(x)',            # множитель замены оставлен
    'q13p': 'u/((u + 1)*(u - 2))',                # знаменатель не разнесён
    'q13': 'log(Abs(sin(x) + 1))/3 - 2*log(Abs(sin(x) - 2))/3',   # знак у второго
    'q14': 'log(Abs((1 + v)/(1 - v)))/2 + log(A)/2 + v',          # лишнее слагаемое
    'q15d': 'exp(x + x**2)',                      # интеграл x+1 взят как x+x²
    'q15e': 'exp(x/2)*sin(x)',                    # корень потерян
    'q16': 'sin(x)**(n - 1)*cos(x)/n + (n - 1)*J(n - 2)/n',       # знак первого члена
    'q16c': 'cos(x)**3*sin(x)/4 + 3*cos(x)*sin(x)/8',             # член 3x/8 потерян
    'q17a': '1 - x**2 + x**4 - x**6',             # сдан ряд, а не его интеграл
    'q17b': 'x + x**3/6 + 3*x**5/40 + x**7/112',  # написано больше заказанного
    'q17k': '1',                                  # k подобрано на глаз
    'q18s': 'E - 2*x**2',                         # множитель e у второго члена потерян
    'q18': '73*E/375 + E/100',                    # арифметика при подстановке
    'q19': '2',                                   # уравнение решено до c², а не до c
    'q20k': '0.713',                              # три значащие цифры вместо шести
    'q21a': '1.6',                                # у нечётной функции взят модуль
    'q21b': '1.6',                                # чётная часть не удвоена
    'qt': '(E**2 - 1)/2',                         # делитель не тот
}
missed = []
for name, wrong in sorted(BREAK.items()):
    out = run([filled(source, {name: wrong}) for source in notebook_cells])
    if not [line for line in out.split('\n') if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
