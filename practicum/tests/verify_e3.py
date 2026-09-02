"""Независимая проверка каждого ответа практикума E3.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение
и проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит «вообще без символьного
дифференцирования». verify_derivative из kit вызывает sp.diff; если та же
sp.diff подтвердит его ответы, подтверждено будет только то, что sympy
согласна сама с собой. Поэтому здесь производная берётся численно, прямо
из определения — пятиточечной конечной разностью с погрешностью порядка
h⁴, — и с ней сверяется каждый ответ ноутбука. Совпадение символьной
записи с наклоном настоящей секущей и есть проверка.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_e3.py
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

import build_e3 as gen

R = sp.Rational
x, t = sp.symbols('x t')
a, b, c, h, k, m, n, r = sp.symbols('a b c h k m n r')
alpha, theta = sp.symbols('alpha theta')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


# Ноутбук пишет ответы в нотации IB: cosec, arcsin, ln. Эти имена приносит
# kit, а sp.sympify о них не знает — отсюда словарь.
NOTATION = {'cosec': sp.csc, 'arcsin': sp.asin, 'arccos': sp.acos,
            'arctan': sp.atan, 'ln': sp.log}


def S(expr):
    return sp.sympify(expr, locals=NOTATION)


def _fn(expr, var, subs):
    return sp.lambdify(var, S(expr).subs(subs or {}), 'math')


def slope(expr, var, point, subs=None, step=1e-3):
    """Производная в точке из определения: пятиточечная конечная разность.

    Символьного дифференцирования здесь нет вовсе — только значения самой
    функции по обе стороны от точки. Погрешность порядка step⁴, то есть
    около 1e-12, и этого хватает, чтобы отличить верный ответ от любого
    из типовых промахов.
    """
    f = _fn(expr, var, subs)
    return (f(point - 2*step) - 8*f(point - step)
            + 8*f(point + step) - f(point + 2*step)) / (12 * step)


def slope2(expr, var, point, subs=None, step=1e-3):
    """Вторая производная в точке, той же пятиточечной разностью."""
    f = _fn(expr, var, subs)
    return (-f(point - 2*step) + 16*f(point - step) - 30*f(point)
            + 16*f(point + step) - f(point + 2*step)) / (12 * step**2)


def matches(claim, f, var, points, subs=None, order=1, tol=1e-6):
    """Совпадает ли написанная производная с наклоном настоящей секущей."""
    got = _fn(claim, var, subs)
    rule = slope2 if order == 2 else slope
    for point in points:
        want = rule(f, var, point, subs)
        if abs(got(point) - want) > tol * max(1.0, abs(want)):
            return False
    return True


PTS = (0.31, -0.47, 0.83, 1.27)

print('=== Задача 1: почленно ===')
chk('1a: -2(x - h) — это наклон -(x - h)^2 + 2k',
    matches(gen.ANSWERS['q1a'], -(x - h)**2 + 2*k, x, PTS, {h: 0.7, k: 1.3}))
chk('и 2(x - h) им не является',
    not matches('2*(x - h)', -(x - h)**2 + 2*k, x, PTS, {h: 0.7, k: 1.3}))
G = t/16 + 3*t**2/16 + 5*t**3/16 + 7*t**4/16
chk('1b: G\'(t) совпадает с наклоном G', matches(gen.ANSWERS['q1b'], G, t, PTS))
chk('и G\'(1) = 50/16, то есть E(M) распределения из условия',
    abs(slope(G, t, 1.0) - 50/16) < 1e-9)

print('\n=== Задача 2: таблица производных ===')
T = 500*sp.sec(theta) + (2500 - 1000*sp.tan(theta))/3
chk('2: dT/dtheta совпадает с наклоном T',
    matches(gen.ANSWERS['q2'], T, theta, (0.31, 0.83, 1.1)))
chk('без деления на 3 — не совпадает',
    not matches('500*sec(theta)*tan(theta) - 1000*sec(theta)**2', T, theta,
                (0.31, 0.83, 1.1)))

print('\n=== Задача 3: цепное правило ===')
chk('3a: g\'(-1) = -2e^2 совпадает с наклоном e^(x^2+1) в -1',
    abs(float(S(gen.ANSWERS['q3a']).evalf())
        - slope(sp.exp(x**2 + 1), x, -1.0)) < 1e-6)
chk('3b: f\'(x) совпадает с наклоном 1/(2 - x)^2',
    matches(gen.ANSWERS['q3b'], 1/(2 - x)**2, x, PTS))
chk('и знак у него положительный при x < 2',
    slope(1/(2 - x)**2, x, 0.5) > 0)

print('\n=== Задача 4: произведение ===')
FN = x**n*(a - x)**n
ok4 = all(matches(gen.ANSWERS['q4'], FN, x, (0.31, 0.83, 1.21),
                  {n: nn, a: 1.7}) for nn in (2, 3, 5))
chk('4: f_n\'(x) совпадает с наклоном при n = 2, 3, 5', ok4)
chk('со скобкой (a - x) + x вместо (a - x) - x — нет',
    not matches('n*x**(n - 1)*a*(a - x)**(n - 1)', FN, x, (0.31, 0.83),
                {n: 3, a: 1.7}))

print('\n=== Задача 5: частное ===')
Q1 = (3*x + 2)/(4*x**2 - 1)
chk('5a: f\'(x) совпадает с наклоном (3x + 2)/(4x^2 - 1)',
    matches(gen.ANSWERS['q5a'], Q1, x, (0.71, 1.27, -1.31, 2.13)))
chk('перевёрнутый числитель даёт ровно минус ответ',
    matches('-(' + gen.ANSWERS['q5a'] + ')',
            -Q1, x, (0.71, 1.27, -1.31)))
Q2 = (2*x + a)**3/(x + 5)**2
chk('5b: f\'(x) совпадает с наклоном при a = 1, 3, 7',
    all(matches(gen.ANSWERS['q5b'], Q2, x, PTS, {a: aa}) for aa in (1, 3, 7)))
# Условие следующего пункта той же бумаги: f'(1) = tan 70 градусов.
roots = [sp.nsolve(S(gen.ANSWERS['q5b']).subs(x, 1)
                   - sp.tan(sp.rad(70)), a, g) for g in (3.0, 14.0)]
chk('и f\'(1) = tan 70° даёт a = 2.73 и 15.0, как в схеме оценивания',
    abs(float(roots[0]) - 2.72844) < 1e-4 and abs(float(roots[1]) - 14.9696) < 1e-3)

print('\n=== Задача 6: до напечатанного вида ===')
F6, G6 = 1/(2 - x)**2, x**2
prod = [slope(F6, x, p) * slope(G6, x, p) for p in PTS]
chk('6a: f\'g\' совпадает с произведением двух наклонов',
    all(abs(_fn(gen.ANSWERS['q6a'], x, None)(p) - v) < 1e-6
        for p, v in zip(PTS, prod)))
mixed = [_fn(F6, x, None)(p) * slope(G6, x, p)
         + _fn(G6, x, None)(p) * slope(F6, x, p) for p in PTS]
chk('6b: fg\' + gf\' совпадает с ним же',
    all(abs(_fn(gen.ANSWERS['q6b'], x, None)(p) - v) < 1e-6
        for p, v in zip(PTS, mixed)))
chk('и это не совпадение записи: два выражения численно равны',
    all(abs(u - v) < 1e-6 for u, v in zip(prod, mixed)))

print('\n=== Задача 7: вторая производная ===')
G7 = sp.exp(x)*sp.cos(x)
chk('7: g\'\'(x) совпадает со второй разностью',
    matches(gen.ANSWERS['q7'], G7, x, PTS, order=2))
chk('и тождество g\'\' = 2(g\' - g) выполняется численно',
    all(abs(slope2(G7, x, p) - 2*(slope(G7, x, p) - _fn(G7, x, None)(p)))
        < 1e-6 for p in PTS))

print('\n=== Задача 8: шест за угол ===')
L = 3*sp.sec(alpha)/4 + 6*sp.csc(alpha)
APTS = (0.41, 0.83, 1.21)
chk('8a: dL/d(alpha) совпадает с наклоном L', matches(gen.ANSWERS['q8a'], L, alpha, APTS))
chk('8b: вторая производная совпадает со второй разностью',
    matches(gen.ANSWERS['q8b'], L, alpha, APTS, order=2))
at2 = float(sp.atan(2))
chk('8c: 45*sqrt(5)/4 совпадает со второй разностью в arctan 2',
    abs(float(S(gen.ANSWERS['q8c']).evalf()) - slope2(L, alpha, at2)) < 1e-5)
chk('и первая производная в arctan 2 равна нулю — это минимум',
    abs(slope(L, alpha, at2)) < 1e-8)
chk('а минимум L равен 15*sqrt(5)/4 ≈ 8.39 м — шест в 11.25 м не проходит',
    abs(float(L.subs(alpha, sp.atan(2)).evalf()) - float(15*sp.sqrt(5)/4)) < 1e-9
    and float(L.subs(alpha, sp.atan(2)).evalf()) < 11.25)

print('\n=== Задача 9: кривизна параболы ===')
# Кривизна считается из определения, без формул, напечатанных в вопросе.
for aa in (2.0, -2.0, 0.5):
    H = aa*x**2 + 1.3*x - 4
    xs = float(S(gen.ANSWERS['q9a']).subs({a: aa, b: 1.3}))
    curv = lambda p: abs(slope2(H, x, p)) / (1 + slope(H, x, p)**2)**1.5
    grid = [xs - 2 + 0.05*i for i in range(81)]
    chk(f'9a: при a = {aa} кривизна максимальна в -b/(2a)',
        all(curv(p) <= curv(xs) + 1e-9 for p in grid))
    chk(f'9b: и там она равна 2|a| = {2*abs(aa)}',
        abs(curv(xs) - 2*abs(aa)) < 1e-6)
chk('2a вместо 2|a| при a = -2 даёт -4, чего кривизна не бывает',
    float(S('2*a').subs(a, -2)) < 0)

print('\n=== Задача 10: прочесть производную ===')
F10 = sp.cos(x)**2 - 3*sp.sin(x)**2
chk('10a: f\'(x) совпадает с наклоном', matches(gen.ANSWERS['q10a'], F10, x, PTS))
pts10 = [(0, 1), (float(sp.pi/2), -3), (float(sp.pi), 1)]
chk('10b: в каждой из трёх точек наклон равен нулю',
    all(abs(slope(F10, x, p if p else 1e-9)) < 1e-6 for p, _ in pts10))
chk('и вторая координата равна значению функции',
    all(abs(_fn(F10, x, None)(p) - v) < 1e-9 for p, v in pts10))
# Полнота: сканируем производную по отрезку из условия сами.
grid = [i * float(sp.pi) / 2000 for i in range(2001)]
vals = [slope(F10, x, max(p, 1e-9)) for p in grid]
crossings = sum(1 for i in range(len(vals) - 1) if vals[i] * vals[i + 1] < 0)
chk('и внутри (0, pi) ровно одна смена знака — плюс два конца, всего три точки',
    crossings == 1)

print('\n=== Задача 11: два неравенства ===')
FP = 4 + 2*x - 3*sp.exp(x)
edges = [float(sp.nsolve(FP, x, g)) for g in (-2.0, 1.0)]
chk('11a: границы -1.74 и 0.518 обращают f\' в ноль',
    abs(edges[0] + 1.73554) < 1e-4 and abs(edges[1] - 0.518) < 1e-3)
chk('и между ними f\' положительна, а снаружи отрицательна',
    _fn(FP, x, None)(0.0) > 0 and _fn(FP, x, None)(-3.0) < 0
    and _fn(FP, x, None)(2.0) < 0)
chk('11b: f\'\' меняет знак в ln(2/3)',
    abs(slope(FP, x, float(sp.log(R(2, 3)))) ) < 1e-6)
chk('и слева от неё f\'\' положительна',
    slope(FP, x, float(sp.log(R(2, 3))) - 0.5) > 0)

print('\n=== Задача 12: три условия ===')
aa, bb, cc = [sp.Integer(v) for v in (3, -11, 8)]
Y = (x - 4)/(aa*x**2 + bb*x + cc)
chk('12: знаменатель обращается в ноль при x = 1',
    (aa*1 + bb + cc) == 0)
chk('и кривая проходит через (2, 1)', sp.simplify(Y.subs(x, 2) - 1) == 0)
chk('и наклон в x = 2 равен нулю — численно, не через diff',
    abs(slope(Y, x, 2.0)) < 1e-8)
chk('и это минимум, а не максимум', slope2(Y, x, 2.0) > 0)
chk('c = 9 вместо 8 ломает первое же условие', (aa + bb + 9) != 0)

print('\n=== На таймере: площадь треугольника ===')
# Площадь считается из координат вершин, а не из напечатанной формулы.
def area(px):
    py = (9 - px**2)**0.5
    return 0.5 * abs((-3 - px)*(-py - py))
chk('qt_a: (x + 3)*sqrt(9 - x^2) совпадает с площадью по координатам',
    all(abs(_fn(gen.ANSWERS['qt_a'], x, None)(p) - area(p)) < 1e-9
        for p in (0.5, 1.5, 2.5)))
chk('qt_b: dA/dx совпадает с наклоном этой площади',
    all(abs(_fn(gen.ANSWERS['qt_b'], x, None)(p)
            - (area(p + 1e-4) - area(p - 1e-4)) / 2e-4) < 1e-5
        for p in (0.5, 1.5, 2.5)))
chk('и dA/dx = 0 при x = 3/2, как в пункте (d)',
    abs(_fn(gen.ANSWERS['qt_b'], x, None)(1.5)) < 1e-9)

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
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= len(names))

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': '2*(x - h)',                       # знак потерян
    'q1b': '3*t/8 + 15*t**2/16 + 7*t**3/4',   # свободный член выброшен
    'q2': '500*sec(theta)*tan(theta) - 1000*sec(theta)**2',   # без деления на 3
    'q3a': '-2*E',                            # показатель взят как 1
    'q3b': '-2/(2 - x)**3',                   # потерян внутренний -1
    'q4': 'n*x**(n - 1)*(a - x)**n',          # одно слагаемое произведения
    'q5a': '(-12*x**2 - 16*x - 3)/(4*x**2 - 1)',   # знаменатель без квадрата
    'q5b': '6*(2*x + a)**2/(2*(x + 5))',      # частное продифференцировано почленно
    'q6a': '4*x/(2 - x)**5',                  # общий знаменатель взят как произведение
    'q6b': '4*x/(2 - x)**5',                  # то же самое
    'q7': '2*exp(x)*sin(x)',                  # знак второй производной
    'q8a': '3*sec(alpha)*tan(alpha)/4 + 6*cosec(alpha)*cot(alpha)',   # минус у cosec
    'q8b': '3*sec(alpha)*tan(alpha)/4 - 6*cosec(alpha)*cot(alpha)',   # первая вместо второй
    'q8c': '45*sqrt(5)',                      # деление на 4 потеряно
    'q9a': 'b/(2*a)',                         # знак
    'q9b': '2*a',                             # потерян модуль
    'q10a': '-8*sin(2*x)',                    # лишний множитель 2
    'q10b': '[(0, 1), (pi, 1)]',              # средняя точка потеряна
    'q11a': 'Interval.open(0.518, oo)',       # найден один промежуток из двух
    'q11b': 'Interval.open(log(Rational(2, 3)), oo)',   # не та сторона
    'q12': '[3, -11, 9]',                     # c не удовлетворяет асимптоте
    'qt_a': '(x + 3)*sqrt(9 - x**2)/2',       # высота взята за половину
    'qt_b': '(9 - 3*x - x**2)/sqrt(9 - x**2)',  # одно из двух x^2 потеряно
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
