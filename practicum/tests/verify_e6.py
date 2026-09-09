"""Независимая проверка каждого ответа практикума E6.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново из условия, а не переписываются из раздела решений. Если решение
и проверка совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит буквально наоборот тому, что делает
ноутбук. Проверки в kit не интегрируют и не дифференцируют: они меряют —
складывают полосы, диски, усечённые конусы и шаги. Значит, тест обязан
считать формулой, и он считает через sp.integrate: площадь как
∫|f − g|, объём как π∫R², поверхность как 2π∫y√(1 + (dy/dx)²), путь как
∫|v|. Ноутбук меряет, тест интегрирует; там, где они сошлись, ошибиться
должны были обе стороны сразу.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждый ответ по очереди портится
типовой ошибкой, и ячейка обязана её отвергнуть.

Запуск:  python practicum/tests/verify_e6.py
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

import build_e6 as gen

R = sp.Rational
x, y, t, u, v, k, C, A = sp.symbols('x y t u v k C A')
a, b, c, h, m, n, q, r, s, w, v0 = sp.symbols('a b c h m n q r s w v0')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅ ' if ok else '❌ ') + name)


def same(name, got, want, digits=None):
    """Ответ ноутбука и ответ, полученный интегрированием, — одно число."""
    got, want = sp.sympify(got), sp.sympify(want)
    if digits is None:
        chk(name, sp.simplify(got - want) == 0)
        return
    lo, hi = float(sp.N(got, 20)), float(sp.N(want, 20))
    chk(f'{name} (до {digits} знач. цифр)',
        f'{lo:.{digits}g}' == f'{hi:.{digits}g}')


def area(top, bottom, lo, hi, var=x):
    """Площадь формулой: ∫|верх − низ|, с разбиением по пересечениям."""
    gap = sp.sympify(top) - sp.sympify(bottom)
    cuts = [p for p in sp.solve(sp.Eq(gap, 0), var)
            if p.is_real and sp.N(lo) < sp.N(p) < sp.N(hi)]
    edges = [sp.sympify(lo)] + sorted(cuts, key=lambda p: float(sp.N(p))) + [sp.sympify(hi)]
    return sum(abs(sp.integrate(gap, (var, edges[i], edges[i + 1])))
               for i in range(len(edges) - 1))


def solid(outer, lo, hi, inner=0, var=x):
    return sp.pi * sp.integrate(sp.sympify(outer) ** 2 - sp.sympify(inner) ** 2,
                                (var, lo, hi))


def biggest(roots):
    """Наибольший действительный корень: у h³ = 216 их три, годится один."""
    real = [p for p in roots if sp.im(sp.N(p)) == 0]
    return max(real, key=lambda p: sp.re(sp.N(p)))


def surface(curve, lo, hi, var=x):
    curve = sp.sympify(curve)
    slant = sp.sqrt(1 + sp.diff(curve, var) ** 2)
    return sp.simplify(2 * sp.pi * sp.integrate(curve * slant, (var, lo, hi)))


print('=== Ответы, выведенные заново через sp.integrate ===')
G = gen.ANSWERS

same('1a площадь под 4+4cos x от π до 3π', G['q1'],
     area(4 + 4*sp.cos(x), 0, sp.pi, 3*sp.pi))
same('1b знаковый интеграл x²−4 на [0,3]', G['q2'],
     sp.integrate(x**2 - 4, (x, 0, 3)))
same('1c полная площадь того же', G['q3'], area(x**2 - 4, 0, 0, 3))

lo_n = ((2*n - 1)*sp.pi/2)**2
hi_n = ((2*n + 1)*sp.pi/2)**2
ok = True
for value in (1, 2, 3, 4):
    want = abs(sp.integrate(sp.cos(sp.sqrt(x)),
                            (x, lo_n.subs(n, value), hi_n.subs(n, value))))
    ok = ok and sp.simplify(sp.sympify(G['q4']).subs(n, value) - want) == 0
chk('2 площадь R_n равна 4πn при n = 1, 2, 3, 4', ok)

same('3a между −x²+9 и −3x+9', G['q5'], area(-x**2 + 9, -3*x + 9, 0, 3))
same('3b между cos x и sin 2x', G['q6'],
     area(sp.cos(x), sp.sin(2*x), sp.pi/2, 5*sp.pi/6))
same('4a между x² и √x', G['q7'], area(sp.sqrt(x), x**2, 0, 1))
same('4b половина над y = x', G['q8'], area(sp.sqrt(x), x, 0, 1))

same('5a объём √(x sin x²) вокруг x', G['q9'],
     solid(sp.sqrt(x*sp.sin(x**2)), 0, sp.sqrt(sp.pi/2)))
same('5b объём cos²x вокруг x', G['q10'], solid(sp.cos(x)**2, 0, sp.pi/2))
same('6a объём x²+y³=r³ вокруг y', G['q11'],
     solid(sp.sqrt(r**3 - y**3), 0, r, var=y))
same('6b объём x²−y²=4 вокруг y', G['q12'],
     solid(sp.sqrt(y**2 + 4), 0, 3, var=y))
same('7a кольцо между x=2y и x=y²', G['q13'],
     solid(2*y, 0, 1, inner=y**2, var=y))
ring = sp.simplify(solid(sp.sqrt(r**2 - y**2), -h/2, h/2,
                         inner=sp.sqrt(r**2 - h**2/4), var=y))
same('7b объём кольца равен πh³/6 и от r не зависит', G['q14'], ring)
chk('7b в объёме кольца действительно нет r', r not in ring.free_symbols)
same('7c h, при котором кольцо равно 36π', G['q15'],
     biggest(sp.solve(sp.Eq(ring, 36*sp.pi), h)))

same('8a поверхность конуса y=3x на [0,2]', G['q16'], surface(3*x, 0, 2))
rp = sp.Symbol('r', positive=True)      # знак радиуса нужен sympy для корня
same('8b поверхность сферы', sp.sympify(G['q17']).subs(r, rp),
     surface(sp.sqrt(rp**2 - x**2), -rp, rp))
same('8c пояс сферы радиуса 5 от x=1 до x=4', G['q18'],
     surface(sp.sqrt(25 - x**2), 1, 4))

same('9a перемещение 4+4t−3t² за 3 с', G['q19'],
     sp.integrate(4 + 4*t - 3*t**2, (t, 0, 3)))
same('9b путь за те же 3 с', G['q20'], area(4 + 4*t - 3*t**2, 0, 0, 3, var=t))
same('9c путь t sin t − 3 за 10 с', G['q21'],
     sp.Integral(abs(t*sp.sin(t) - 3), (t, 0, 10)).evalf(15), digits=3)
same('9d перемещение за те же 10 с', G['q22'],
     sp.integrate(t*sp.sin(t) - 3, (t, 0, 10)), digits=3)
same('10 наибольшее перемещение', G['q23'],
     sp.simplify(sp.integrate((1 + v0)*sp.exp(-t) - 1, (t, 0, sp.log(1 + v0)))))

same('11a сечение жёлоба', G['q28'], area(4, x**2, -2, 2))
same('11b ёмкость жёлоба', G['q29'], 40 * sp.sympify(G['q28']))
same('11c дождь за 60 с', G['q30'],
     sp.integrate(8 + 4*sp.cos(sp.pi*t/4), (t, 0, 60)))
same('11d перелив', G['q31'],
     sp.sympify(G['q30']) - sp.sympify(G['q29']))

gap_t = 100 + sp.integrate(60*sp.exp(-u/10) - 5*u, (u, 0, t))
same('12a d(t)', G['q25'], sp.simplify(gap_t))
meet = sp.nsolve(gap_t, t, 15)
same('12b момент встречи', G['q26'], meet, digits=3)
same('12c путь машины к этому моменту', G['q27'],
     sp.integrate(5*t, (t, 0, meet)), digits=3)

same('13a k, при котором объём равен 8π', G['q32'],
     biggest(sp.solve(sp.Eq(solid(sp.sqrt(x), 0, k), 8*sp.pi), k)))
same('13b c, при котором площадь равна ln 5', G['q33'],
     biggest(sp.solve(sp.Eq(sp.integrate(1/x, (x, 1, c)), sp.log(5)), c)))
same('таймер: кольцо между √x и x/3', G['qt'],
     solid(sp.sqrt(x), 0, 9, inner=x/3))

print('\n=== Ноутбук ===')
with open(gen.NOTEBOOK) as fh:
    doc = json.load(fh)

PLACEHOLDER = re.compile(r'^(\w+) = \.\.\.')
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
    'q1': '4*pi',                        # взята половина промежутка
    'q2': '3',                           # знак потерян
    'q3': '-3',                          # сдан интеграл вместо площади
    'q4': '4*pi',                        # зависимость от n потеряна
    'q5': '-Rational(9, 2)',             # вычтено наоборот
    'q6': '-Rational(1, 4)',             # вычтено наоборот
    'q7': 'Rational(1, 6)',              # сдана половина области
    'q8': 'Rational(1, 3)',              # сдана вся область вместо половины
    'q9': 'Rational(1, 2)',              # π потеряно
    'q10': '3*pi**2/8',                  # взят полный период вместо четверти
    'q11': '3*r**4/4',                   # π потеряно
    'q12': '21',                         # π потеряно
    'q13': '8*pi/15',                    # вычтены радиусы, а не их квадраты
    'q14': 'pi*h**3/3',                  # делитель не тот
    'q15': '3',                          # уравнение решено неверно
    'q16': '6*sqrt(10)*pi',              # π вместо 2π
    'q17': '2*pi*r**2',                  # π вместо 2π
    'q18': '15*pi',                      # π вместо 2π
    'q19': '13',                         # сдан путь вместо перемещения
    'q20': '3',                          # сдано перемещение вместо пути
    'q21': '-22.2',                      # сдано перемещение вместо пути
    'q22': '37.1',                       # сдан путь вместо перемещения
    'q23': 'v0 + log(1 + v0)',           # знак второго слагаемого
    'q25': '100 - 600*exp(-t/10) - 5*t**2/2',   # постоянная не найдена
    'q26': '15.0',                       # округление не то
    'q27': '570',                        # взято округлённое время вместо точного
    'q28': '-Rational(32, 3)',           # вычтено наоборот
    'q29': 'Rational(32, 3)',            # не умножено на длину жёлоба
    'q30': '0',                          # проинтегрирован один косинус
    'q31': 'Rational(1280, 3)',          # сдана ёмкость вместо перелива
    'q32': '2',                          # решено до k², а не до k
    'q33': 'log(5)',                     # сдан сам интеграл вместо предела
    'qt': '81*pi/2',                     # внутренний радиус не вычтен
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
