"""Независимая проверка каждого ответа практикума E4.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение
и проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит наоборот тому, что делает ноутбук.
Проверки в kit ходят по кривой: берут точку слева, точку справа и считают
наклон секущей через них. Значит, тест обязан считать иначе — и он считает
символьно, через sp.diff и sp.solve. Ноутбук ходит, тест дифференцирует;
там, где они сошлись, ошибиться должны были обе стороны сразу.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждый ответ по очереди портится
типовой ошибкой, и ячейка обязана её отвергнуть, — иначе проверка вида
«всегда ✅» прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_e4.py
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

import build_e4 as gen

R = sp.Rational
x, y, t, k = sp.symbols('x y t k')
a, b, c, h, m, r, S = sp.symbols('a b c h m r S')
Y = sp.Function('y')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


NOTATION = {'cosec': sp.csc, 'arcsin': sp.asin, 'arccos': sp.acos,
            'arctan': sp.atan, 'ln': sp.log}


def E(expr):
    return sp.sympify(expr, locals=NOTATION)


def A(name):
    return E(gen.ANSWERS[name])


def implicit(relation, var=x, dep=y):
    """dy/dx из соотношения — символьно, через sp.diff и sp.solve.

    Ровно то, чего проверки kit не делают ни разу: там наклон берётся
    ходьбой по кривой. Здесь наоборот, и в этом весь смысл теста.
    """
    left = relation.lhs - relation.rhs if isinstance(relation, sp.Eq) else relation
    swapped = left.subs(dep, Y(var))
    answer = sp.solve(sp.Eq(sp.diff(swapped, var), 0), sp.Derivative(Y(var), var))
    return sp.simplify(answer[0].subs(Y(var), dep))


def same(one, two):
    return sp.simplify(sp.sympify(one) - sp.sympify(two)) == 0


def near(one, two, tol=5e-3):
    return abs(float(sp.N(one, 40)) - float(sp.N(two, 40))) <= tol * max(
        1.0, abs(float(sp.N(two, 40))))


print('=== Задание 1: касательная, которую дали, и касательная, которую строят ===')
chk("1a: f'(4) — это наклон прямой y = 6x - 1",
    same(A('q1a'), sp.diff(6*x - 1, x)))
chk('1b: f(4) читается с той же прямой',
    same(A('q1b'), (6*x - 1).subs(x, 4)))
inner = x**2 - 3*x
chk('1c: h(4) = f(g(4)) = f(4), потому что g(4) = 4',
    inner.subs(x, 4) == 4)
chk("1c: h'(4) = f'(4)·g'(4) = 6·5",
    sp.diff(inner, x).subs(x, 4) * 6 == 30)
chk('1c: касательная проходит через (4, 23) с наклоном 30',
    same(A('q1c').subs(x, 4), 23) and same(sp.diff(A('q1c'), x), 30))

print('\n=== Задание 2: касательная с буквами ===')
g2 = (x - r)*(x**2 - 2*a*x + a**2 + b**2)
chk('2a: g(a) = b²(a − r)', same(g2.subs(x, a), b**2*(a - r)))
chk("2a: g'(a) = b²", same(sp.diff(g2, x).subs(x, a), b**2))
tangent2 = sp.diff(g2, x).subs(x, a)*(x - a) + g2.subs(x, a)
chk('2a: эталон совпадает с касательной, посчитанной символьно',
    same(A('q2'), tangent2))
chk('2b: эта касательная обращается в ноль ровно при x = r',
    sp.solve(sp.Eq(tangent2.subs(b, 2), 0), x) == [r])

print('\n=== Задание 3: нормаль ===')
f3 = x**2/2 + 5*x + 13
chk('3: точка касания (−3, 5/2)', f3.subs(x, -3) == R(5, 2))
chk("3: f'(−3) = 2", sp.diff(f3, x).subs(x, -3) == 2)
chk('3: нормаль имеет наклон −1/2 и проходит через точку',
    same(sp.diff(A('q3'), x), -R(1, 2)) and same(A('q3').subs(x, -3), R(5, 2)))

print('\n=== Задание 4: нормаль с буквой ===')
chk("4: касательная к 1/x при x = t имеет наклон −1/t²",
    same(sp.diff(1/x, x).subs(x, t), -1/t**2))
chk('4: произведение наклонов равно −1',
    same(A('q4') * (-1/t**2), -1))

print('\n=== Задание 5: лишний корень ===')
roots5 = sp.solve(sp.Eq(sp.diff(sp.log(x**2 - 16), x), R(1, 3)), x)
chk('5: уравнение f′ = 1/3 имеет корни −2 и 8', sorted(roots5) == [-2, 8])
chk('5: в области x > 4 остаётся один', A('q5') == 8 and 8 > 4 > -2)

print('\n=== Задание 6: точные координаты ===')
f6 = 90*sp.exp(-x/2)
xs6 = sp.solve(sp.Eq(sp.diff(f6, x), -1), x)
chk('6: x-координата совпадает с решением f′ = −1',
    same(A('q6')[0], xs6[0]))
chk('6: y-координата — значение самой функции там',
    same(A('q6')[1], f6.subs(x, xs6[0])))
chk('6: и она равна ровно 2', sp.simplify(f6.subs(x, xs6[0])) == 2)

print('\n=== Задание 7: угол вместо наклона ===')
f7 = (2*x + a)**3/(x + 5)**2
target7 = sp.tan(70*sp.pi/180)
poly7 = sp.expand(sp.numer(sp.together(sp.diff(f7, x).subs(x, 1) - target7)))
roots7 = [sp.re(v) for v in sp.nroots(sp.Poly(poly7, a)) if abs(sp.im(v)) < 1e-9]
positive7 = sorted(v for v in roots7 if v > 0)
chk('7: положительных корней ровно два', len(positive7) == 2)
chk('7: эталоны совпадают с ними до трёх значащих цифр',
    all(near(claim, true) for claim, true in zip(A('q7'), positive7)))
chk('7: наклон при этих a действительно tan 70°',
    all(near(sp.diff(f7, x).subs({x: 1, a: v}), target7, 1e-2)
        for v in positive7))

print('\n=== Задание 8: эллипс ===')
chk('8: эталон совпадает с dy/dx, полученной sp.diff и sp.solve',
    same(A('q8'), implicit(sp.Eq(4*x**2 + y**2 - 24*x + 4*y + 20, 0))))

print('\n=== Задание 9: логарифм произведения ===')
spiral = sp.Eq(y, x - x*y*sp.log(x*y))
d9 = implicit(spiral)
chk('9a: эталон совпадает с символьной dy/dx', same(A('q9a'), d9))
printed9 = (sp.Derivative(Y(x), x)
            + (x*sp.Derivative(Y(x), x) + Y(x))*(1 + sp.log(x*Y(x))) - 1)
chk('9a: и напечатанное в бумаге равенство при ней выполняется',
    sp.simplify(printed9.subs(sp.Derivative(Y(x), x),
                              d9.subs(y, Y(x)))) == 0)
chk('9b: при x = 1 кривая даёт ровно один положительный y, и он равен 1',
    abs(sp.nsolve(sp.Eq(1 - y*sp.log(y), y), y, 1.0) - 1) < 1e-12)
chk('9b: наклон там нулевой, и касательная горизонтальна',
    sp.simplify(d9.subs({x: 1, y: 1})) == 0 and same(A('q9b'), 1))

print('\n=== Задание 10: e^(x+y) = x² + y² ===')
loop = sp.Eq(sp.exp(x + y), x**2 + y**2)
d10 = implicit(loop)
chk('10a: эталон совпадает с символьной dy/dx', same(A('q10a'), d10))
# Горизонтальная касательная: числитель в ноль, затем обратно в кривую.
line10 = sp.log(2*x) - x
shown10 = sp.expand(-(sp.exp(x + line10) - x**2 - line10**2))
chk('10b: подстановка y = ln(2x) − x даёт напечатанное уравнение',
    sp.simplify(shown10 - (2*x**2 + sp.log(2*x)**2
                           - 2*x*sp.log(2*x) - 2*x)) == 0)
found10 = [sp.nsolve(shown10, x, guess) for guess in (0.3, 1.8)]
chk('10b: оба корня совпадают с эталонами до трёх значащих цифр',
    all(near(claim[0], true) and near(claim[1], line10.subs(x, true))
        for claim, true in zip(A('q10b'), found10)))
chk('10b: в обеих точках символьный наклон равен нулю',
    all(abs(float(sp.N(d10.subs({x: v, y: line10.subs(x, v)}), 30))) < 1e-9
        for v in found10))
sym10 = sp.nsolve(sp.exp(2*x) - 2*x**2, x, -0.5)
chk('10c: точка с наклоном −1 лежит на y = x и совпадает с эталоном',
    near(A('q10d')[0], sym10) and near(A('q10d')[1], sym10))
chk('10c: символьный наклон там равен −1',
    near(d10.subs({x: sym10, y: sym10}), -1, 1e-6))

print('\n=== Задание 11: вторая производная соотношения ===')
relation = (x**2 + x*Y(x))*sp.Derivative(Y(x), x) - (x**2 + x*Y(x) - 3*Y(x)**2)
d11 = sp.solve(sp.Eq(relation, 0), sp.Derivative(Y(x), x))[0]
chk("11a: y'(1) = −17/10", sp.simplify(d11.subs({x: 1, Y(x): R(3, 2)}))
    == A('q11a'))
second11 = sp.solve(sp.Eq(sp.diff(relation, x), 0),
                    sp.Derivative(Y(x), x, 2))[0]
yp, yy = sp.symbols('yp yy')
flat11 = second11.subs({sp.Derivative(Y(x), x): yp, Y(x): yy})
printed11 = (2*x + yy - x*yp**2 - (x + 7*yy)*yp) / (x**2 + x*yy)
chk('11b: напечатанное в бумаге соотношение совпадает с продифференцированным',
    sp.simplify(flat11 - printed11) == 0)
chk("11b: y''(1) = 1008/125",
    sp.nsimplify(flat11.subs({x: 1, yy: R(3, 2), yp: R(-17, 10)}))
    == A('q11b'))
solved11 = sp.Eq(x**6*(2*y - x)**3, 2*(x + 2*y))
chk('11: точка (1, 3/2) лежит на решении из пункта (d)',
    sp.simplify(solved11.lhs.subs({x: 1, y: R(3, 2)})
                - solved11.rhs.subs({x: 1, y: R(3, 2)})) == 0)
chk('11: и наклон этого решения там тот же −17/10',
    sp.simplify(implicit(solved11).subs({x: 1, y: R(3, 2)})) == A('q11a'))

print('\n=== Задание 12: перпендикулярные касательные ===')
root12 = sp.nsolve(sp.cos(x) - sp.tan(x), x, 0.6)
chk('12: точка встречи удовлетворяет cos²k = sin k',
    abs(float(sp.N(sp.cos(root12)**2 - sp.sin(root12), 30))) < 1e-12)
chk('12: эталоны совпадают с производными cos и tan там',
    near(A('q12f').subs(k, root12), sp.diff(sp.cos(x), x).subs(x, root12))
    and near(A('q12g').subs(k, root12), sp.diff(sp.tan(x), x).subs(x, root12)))
chk('12: произведение равно −1',
    near(A('q12f').subs(k, root12) * A('q12g').subs(k, root12), -1, 1e-9))
chk('12: и sin k действительно (√5 − 1)/2',
    near(sp.sin(root12), (sp.sqrt(5) - 1)/2, 1e-9))

print('\n=== Задание 13: два семейства ===')
chk('13a: у прямой y = mx наклон m, и через координаты это y/x',
    same(A('q13a').subs(y, m*x), m))
first13 = sp.Eq(y**2, 4*a**2 - 4*a*x)
second13 = sp.Eq(y**2, 4*b**2 + 4*b*x)
place13 = {x: a - b, y: 2*sp.sqrt(a*b)}
chk('13b: M лежит на обеих кривых',
    sp.simplify((first13.lhs - first13.rhs).subs(place13)) == 0
    and sp.simplify((second13.lhs - second13.rhs).subs(place13)) == 0)
chk('13b: эталоны совпадают с символьными наклонами в M',
    same(A('q13f'), sp.simplify(implicit(first13).subs(place13)))
    and same(A('q13g'), sp.simplify(implicit(second13).subs(place13))))
chk('13b: произведение равно −1',
    sp.simplify(A('q13f') * A('q13g') - (-1)) == 0)

print('\n=== Задание 14: общая касательная ===')
f14 = -(x - h)**2 + 2*k
g14 = sp.exp(x - 2) + k
pair14 = sp.solve([sp.Eq(sp.diff(f14, x).subs(x, 3), sp.diff(g14, x).subs(x, 3)),
                   sp.Eq(f14.subs(x, 3), g14.subs(x, 3))], [h, k], dict=True)[0]
chk('14a: h из равенства наклонов', same(A('q14h'), pair14[h]))
chk('14b: k из равенства значений', same(A('q14k'), pair14[k]))
chk('14b: и это не (2e + e²)/4, как пишет корпус',
    not same(A('q14k'), (2*sp.E + sp.E**2)/4))
chk('14b: численно 4.566, а не 3.21', near(A('q14k'), 4.56555, 1e-4))

print('\n=== Задание 15: прямая дана, кривая неизвестна ===')
pair15 = sp.solve([sp.Eq(sp.diff(sp.log(x)/sp.log(a), x), 1),
                   sp.Eq(sp.log(x)/sp.log(a), x)], [x, a], dict=True)[0]
chk('15: P = (e, e)', same(A('q15x'), pair15[x]) and same(A('q15y'), pair15[x]))
chk('15: a = e^(1/e)', same(A('q15a'), pair15[a]))
chk('15: и оно попадает в 1.4 ≤ a ≤ 1.5',
    1.4 <= float(sp.N(A('q15a'), 30)) <= 1.5)

print('\n=== На таймере ===')
f16 = sp.exp(2*x)*(3*x - 4)
chk("timer (a): f'(x) = e^(2x)(6x − 5)", same(A('qt_a'), sp.diff(f16, x)))
root16 = sp.nsolve(sp.diff(f16, x) - 1, x, 0.9)
chk('timer (b): x совпадает с решением f′ = 1', near(A('qt_b')[0], root16))
chk('timer (b): y — значение самой f, а не f′',
    near(A('qt_b')[1], f16.subs(x, root16)))

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
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 20)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': '-6',                                  # знак наклона
    'q1b': '17',                                  # f(4) взято как g(4) + 13
    'q1c': '30*x - 100',                          # прямая мимо точки касания
    'q2': 'b**2*(x + r)',                         # знак у r
    'q2r': '-r',                                  # то же в ответе про R
    'q3': '2*x + Rational(17, 2)',                # сдана касательная вместо нормали
    'q4': '-t**2',                                # взято −m, а не −1/m
    'q5': '[8, -2]',                              # лишний корень вне области
    'q6': '(2*log(45), 90*exp(-log(45)/2))',      # y взят не с кривой
    'q7': '[2.73]',                               # найдено одно значение из двух
    'q8': '4*(3 - x)/(y - 2)',                    # знак в знаменателе
    'q9a': '(1 - y*(1 + log(x*y)))/(1 + x*log(x*y))',   # потеряна единица в скобке
    'q9b': 'x',                                   # прямая с верной точкой, но не касательная
    'q10a': '(2*x - exp(x + y))/(exp(x + y) + 2*y)',    # знак в знаменателе
    'q10b': '[(0.331, -0.743)]',                  # найдена одна точка из двух
    'q10d': '(-0.451, 0.451)',                    # вторая координата не с кривой
    'q11a': 'Rational(-4, 10)',                   # арифметика при подстановке
    'q11b': 'Rational(-17, 10)',                  # сдана первая производная вместо второй
    'q12f': 'sin(k)',                             # минус у производной косинуса
    'q12g': 'sec(k)',                             # квадрат потерян
    'q13a': 'x/y',                                # перевёрнуто
    'q13f': 'a/sqrt(a*b)',                        # минус потерян
    'q13g': 'b/sqrt(a*b) + 1',                    # просто неверно
    'q14h': '3 - E/2',                            # знак при переносе
    'q14k': '(2*E + E**2)/4',                     # версия корпуса, а не бумаги
    'q15x': 'E**2',                               # точка не та, хотя на вид похожа
    'q15y': '1',                                  # точка не на прямой y = x
    'q15a': 'Rational(3, 2)',                     # a подобрано на глаз
    'qt_a': 'exp(2*x)*(6*x - 4)',                 # одно слагаемое произведения
    'qt_b': '(0.863, 0.863)',                     # подставлено в f', а не в f
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
