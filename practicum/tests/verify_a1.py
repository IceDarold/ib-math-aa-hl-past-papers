"""Независимая проверка каждого ответа практикума A1.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не ходить по прогрессии**. Ноутбук
ходит: verify_term доходит до члена сложением, verify_total складывает
первые n членов, verify_peak перебирает частичные суммы. Повтори тест
то же самое — подтверждено будет только то, что Python согласен сам
с собой.

Поэтому здесь всё считается **формулами**: u₁ + (n − 1)d и
n/2 (2u₁ + (n − 1)d). Это ровно тот путь, которым идёт экзаменуемый,
и ровно тот, которого в ноутбуке нет. Совпадение формулы со сложением
и есть проверка: сложение не знает формулы, формула не знает сложения.

Там, где схема оценивания даёт два метода, посчитаны оба — и оба сверены
друг с другом до того, как сверяться с ответом.

Затем прогоняется сам ноутбук: пустым (должен пройтись сверху вниз и
напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_a1.py
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
from sympy import Rational as R, log, pi, solve, symbols

import build_a1 as gen

n, m = sp.symbols('n m')
x = sp.Symbol('x', positive=True)

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name], locals={'n': n, 'm': m, 'x': x,
                                                 'ln': sp.log, 'pi': sp.pi,
                                                 'Rational': sp.Rational})


def near(one, two, tol=5e-4):
    """Сходятся ли два числа в пределах округления до трёх значащих цифр."""
    return abs(float(sp.N(one - two, 20))) <= tol * max(1.0, abs(float(two)))


def same(one, two):
    """Совпадают ли два выражения алгебраически."""
    return sp.simplify(sp.sympify(one) - sp.sympify(two)) == 0


# Формулы темы, выписанные один раз и больше нигде не повторяемые.
def u(first, step, i):
    return first + (i - 1) * step


def S(first, step, i):
    return sp.Rational(1, 2) * i * (2 * first + (i - 1) * step)


def S_pair(first, last, i):
    """Второй вид той же формулы: n/2 (u₁ + u_n)."""
    return sp.Rational(1, 2) * i * (first + last)


print('=== Задание 1: u_n = 15 - 3n ===')
rule = lambda i: 15 - 3 * i
chk('1a: первый член это значение при n = 1, а не свободный член',
    A('q1a') == rule(1) == 12 and A('q1a') != 15)
chk('1b: при этом n член равен -33', rule(A('q1b')) == -33)
chk('и n целое и положительное', A('q1b').is_Integer and A('q1b') > 0)
chk('1c: разность это коэффициент при n', A('q1c') == rule(2) - rule(1) == -3)
chk('и прогрессия из ответов даёт ту же формулу',
    same(u(A('q1a'), A('q1c'), n), rule(n)))

print('\n=== Задание 2: u1 = 36, u5 = 12 ===')
d2 = solve(sp.Eq(u(36, sp.Symbol('d'), 5), 12), sp.Symbol('d'))[0]
chk('2 (d): четыре шага от первого члена к пятому', A('q2d') == d2 == -6)
chk('2a: тринадцатый член', A('q2a') == u(36, A('q2d'), 13) == -36)
chk('и то же от пятого члена восемью шагами — второй метод схемы',
    A('q2a') == u(12, A('q2d'), 9))
chk('2b: сумма первых n равна нулю', S(36, A('q2d'), A('q2b')) == 0)
chk('и по симметрии тот же номер: нулевой член седьмой, 6 + 1 + 6',
    A('q2b') == 13 == 6 + 1 + 6)
chk('и n = 0 схема оценивания прощает, а номером он не является',
    S(36, A('q2d'), 0) == 0 and A('q2b') != 0)

print('\n=== Задание 3: пирамида из карт ===')
chk('3c: ряд n берёт 3n - 1 карт', same(A('q3r'), 3 * n - 1))
chk('и сумма этих рядов даёт напечатанную формулу',
    same(S(A('q3r').subs(n, 1), 3, n), n * (3 * n + 1) / 2))
chk('и первый ряд это две карты', A('q3r').subs(n, 1) == 2)
chk('3a: t3', A('q3a') == S(2, 3, 3) == 15 == 2 + 5 + 8)
chk('3b: t4 это t3 плюс одиннадцать', A('q3b') == A('q3a') + 11 == 26)
chk('и то же по формуле', A('q3b') == S(2, 3, 4))
chk('а добавление десяти дало бы 25', A('q3b') != A('q3a') + 10)

print('\n=== Задание 4: u8 = S8 = 8 ===')
U, D = symbols('U D')
sol4 = solve([sp.Eq(u(U, D, 8), 8), sp.Eq(S(U, D, 8), 8)], [U, D])
chk('4: система из двух условий', sol4[U] == A('q4u') == -6
    and sol4[D] == A('q4d') == 2)
chk('и восьмой член при них равен восьми', u(A('q4u'), A('q4d'), 8) == 8)
chk('и сумма первых восьми тоже', S(A('q4u'), A('q4d'), 8) == 8)
chk('и вторым методом схемы: 4(u1 + 8) = 8',
    solve(sp.Eq(4 * (U + 8), 8), U)[0] == A('q4u'))

print('\n=== Задание 5: u7 = 6, u6 + u12 = 24 ===')
sol5 = solve([sp.Eq(u(U, D, 7), 6),
              sp.Eq(u(U, D, 6) + u(U, D, 12), 24)], [U, D])
chk('5: система из двух условий', sol5[U] == A('q5u') == -12
    and sol5[D] == A('q5d') == 3)
chk('и вторым методом схемы: 12 + 4d = 24',
    solve(sp.Eq(12 + 4 * D, 24), D)[0] == A('q5d'))
chk('и оба условия при найденных числах выполнены',
    u(A('q5u'), A('q5d'), 7) == 6
    and u(A('q5u'), A('q5d'), 6) + u(A('q5u'), A('q5d'), 12) == 24)

print('\n=== Задание 6: S_n = pn^2 - qn ===')
P, Q = symbols('P Q')
sol6 = solve([sp.Eq(P * 16 - Q * 4, 40), sp.Eq(P * 25 - Q * 5, 65)], [P, Q])
chk('6a: система из S4 и S5', sol6[P] == A('q6p') == 3
    and sol6[Q] == A('q6q') == 2)
chk('и обе суммы при них сходятся',
    A('q6p') * 16 - A('q6q') * 4 == 40 and A('q6p') * 25 - A('q6q') * 5 == 65)
chk('6b: u5 = S5 - S4', A('q6b') == 65 - 40 == 25)
chk('и то же через u1 и d — второй метод схемы',
    A('q6b') == u(A('q6p') - A('q6q'), 2 * A('q6p'), 5))

print('\n=== Задание 7: S_n = n^2 + 4n ===')
sums = lambda i: i ** 2 + 4 * i
chk('7a(i): S5', A('q7a') == sums(5) == 45)
chk('7a(ii): u6 = S6 - S5', A('q7b') == sums(6) - sums(5) == 15)
chk('7b: u1 = S1', A('q7c') == sums(1) == 5)
chk('7c: u_n = S_n - S_(n-1)', same(A('q7d'), sp.expand(sums(n) - sums(n - 1))))
chk('и то же как u1 + (n-1)d при d = 2',
    same(A('q7d'), u(A('q7c'), 2, n)))
chk('и сумма первых n этих членов возвращает S_n',
    same(S_pair(A('q7c'), A('q7d'), n), sums(n)))
chk('а S_n / n дало бы среднее, а не член',
    not same(A('q7d'), sums(n) / n))

print('\n=== Задание 8: k - 5, 3 - 2k, 5k + 3 ===')
K = symbols('K')
three = [K - 5, 3 - 2 * K, 5 * K + 3]
sol8 = solve(sp.Eq(three[1] - three[0], three[2] - three[1]), K)[0]
chk('8a(i): равные разности дают k', sol8 == A('q8k') == R(4, 5))
chk('и то же средним арифметическим — второй метод схемы',
    solve(sp.Eq((three[0] + three[2]) / 2, three[1]), K)[0] == A('q8k'))
chk('8a(ii): третий член это 5k + 3', A('q8u') == 5 * A('q8k') + 3 == 7)
chk('и первый член при этом -21/5, а не 7',
    (A('q8k') - 5) == R(-21, 5) != A('q8u'))
chk('и разность выходит 28/5',
    same((3 - 2 * A('q8k')) - (A('q8k') - 5), R(28, 5)))

print('\n=== Задание 9: средний член и площади ===')
chk('9a: средний член это среднее соседних', A('q9p') == R(9 + 1, 2) == 5)
chk('и это же 2p - q = a', 2 * A('q9p') - 1 == 9)
chk('9a: четыре первых члена при d = -4',
    list(A('q9t')) == [u(9, -4, i) for i in (1, 2, 3, 4)] == [9, 5, 1, -3])
chk('9b: R_(n+1) - R_n', same(A('q9d'), 4 * (n + 1) * pi - 4 * n * pi))
chk('и разность не зависит от n — это и есть постоянство',
    not A('q9d').free_symbols)

print('\n=== Задание 10: AS-линейные функции ===')
root = lambda slope, const: -sp.Rational(const) / slope
chk('10a: последовательность 2, 1/2, -1 имеет разность -3/2',
    A('q10d') == root(2, -1) - 2 == -1 - root(2, -1) == R(-3, 2))
Cm = A('q10c')
chk('10b: условие r - m = c - r даёт m^2 + cm + 2c = 0',
    same(sp.together(sp.expand(m ** 2 + Cm * m + 2 * Cm)), 0))
chk('и решение этого уравнения относительно c и есть ответ',
    same(solve(sp.Eq(m ** 2 + sp.Symbol('c') * m + 2 * sp.Symbol('c'), 0),
               sp.Symbol('c'))[0], Cm))
chk('и при m = 2 отсюда выходит c = -1 — функция из пункта (a)',
    Cm.subs(m, 2) == -1)
funcs = list(A('q10f'))
chk('10c: две функции с целыми m, r, c',
    {(f.coeff(x, 1), f.coeff(x, 0)) for f in funcs} == {(-4, 8), (-3, 9)})
for f in funcs:
    slope, const = f.coeff(x, 1), f.coeff(x, 0)
    chk(f'и у {sp.sstr(f)} тройка m, r, c арифметическая',
        same(root(slope, const) - slope, const - root(slope, const)))
    chk(f'и все три числа целые',
        all(sp.sympify(v).is_Integer for v in (slope, root(slope, const), const)))
chk('и c при этих m равно -m^2/(m + 2)',
    all(Cm.subs(m, f.coeff(x, 1)) == f.coeff(x, 0) for f in funcs))
chk('и третья такая функция это данная в условии -x - 1',
    Cm.subs(m, -1) == -1)

print('\n=== Задание 11: наибольшая сумма ===')
chk('11a: k-й член равен нулю', A('q11k') == 25
    and u(60, R(-5, 2), A('q11k')) == 0)
chk('11b: сумма при этом номере', near(A('q11s'), S(60, R(-5, 2), 25)))
chk('и при номере на единицу меньше она та же — член нулевой',
    S(60, R(-5, 2), 24) == S(60, R(-5, 2), 25) == A('q11s') == 750)
chk('и при 23 она уже меньше', S(60, R(-5, 2), 23) < A('q11s'))
chk('и при 26 тоже меньше', S(60, R(-5, 2), 26) < A('q11s'))
chk('и то же вторым видом формулы: 25/2 (60 + 0)',
    A('q11s') == S_pair(60, 0, 25))

print('\n=== Задание 12: целые номера ===')
chk('12a: n-й член ряда 1 + 4 + 7 + ...', same(A('q12r'), 3 * n - 2))
chk('и его сумма даёт напечатанное P5(n)',
    same(S(1, 3, n), n * (3 * n - 1) / 2))
tri = lambda i: sp.Rational(i * (i + 1), 2)
pent = lambda i: sp.Rational(i * (3 * i - 1), 2)
chk('12b: число треугольное', A('q12t') == tri(A('q12i')) == 210)
chk('и оно же пятиугольное', A('q12t') == pent(A('q12j')))
chk('и номера 20 и 12', (A('q12i'), A('q12j')) == (20, 12))
chk('и меньше него совпадений нет',
    min(v for v in {tri(i) for i in range(2, 200)}
        & {pent(j) for j in range(2, 200)}) == A('q12t'))
cards = lambda i: sp.Rational(i * (3 * i + 1), 2)
chk('12c: столько рядов даёт целое число пачек',
    cards(A('q12n')) == 52 * A('q12k') == 260)
chk('и это наименьшее такое число рядов',
    min(i for i in range(1, 300) if cards(i) % 52 == 0) == A('q12n') == 13)
chk('и пачек ровно пять, а рядов тринадцать', A('q12k') == 5 != A('q12n'))

print('\n=== Задание 13: члены-логарифмы ===')
u13 = [9 + log(9), 5 + log(3), 1 + log(1)]
chk('13a: разность соседних членов', same(A('q13d'), u13[1] - u13[0]))
chk('и вторая разность та же', same(u13[2] - u13[1], A('q13d')))
chk('и ln 9 это 2 ln 3', same(log(9), 2 * log(3)))
chk('13b: сумма первых десяти', same(A('q13s'), S(u13[0], A('q13d'), 10)))
chk('и то же вторым видом формулы',
    same(A('q13s'), S_pair(u13[0], u(u13[0], A('q13d'), 10), 10)))
chk('и в ответе есть обе части: числовая и логарифмическая',
    A('q13s').coeff(log(3)) == -25 and A('q13s').subs(log(3), 0) == -90)

print('\n=== Таймер: ряд из логарифмов ===')
Pp = symbols('Pp')
solt = solve(sp.Eq(Pp * log(x) - log(x), log(x) / 3 - Pp * log(x)), Pp)
chk('(i): равные разности дают p = 2/3', solt[0] == A('qt_p') == R(2, 3))
chk('(ii): d = (p - 1) ln x', same(A('qt_d'), (A('qt_p') - 1) * log(x)))
chk('и это -1/3 ln x', same(A('qt_d'), -log(x) / 3))
chk('(iii): сумма первых n равна ln(1/x^3)',
    same(S(log(x), A('qt_d'), A('qt_n')), log(1 / x ** 3)))
chk('и ln(1/x^3) это -3 ln x', same(log(1 / x ** 3), -3 * log(x)))
chk('и уравнение на n это n^2 - 7n - 18 = 0',
    A('qt_n') ** 2 - 7 * A('qt_n') - 18 == 0)
chk('и второй корень -2 номером не является',
    (-2) ** 2 - 7 * (-2) - 18 == 0 and A('qt_n') == 9)
chk('и первые семь членов в сумме дают ноль — второй метод схемы',
    same(S(log(x), A('qt_d'), 7), 0))
chk('и восьмой с девятым дают -3 ln x',
    same(u(log(x), A('qt_d'), 8) + u(log(x), A('qt_d'), 9), -3 * log(x)))

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: эталон проходит, пустой не падает ===')
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

with open(gen.NOTEBOOK) as fh:
    notebook_cells = [''.join(c['source']) for c in json.load(fh)['cells']
                      if c['cell_type'] == 'code']

names = set()
for source in notebook_cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
chk(f'placeholder-ов ровно столько же, сколько эталонов ({len(names)})',
    names == set(gen.ANSWERS))

TRAINER_FILL = "\n".join(
    f"    {num}: '{code}'," for num, code in sorted(gen.TRIGGER.items()))


def filled(source, override=None):
    """Ячейка с эталонами. Тренажёр распознавания заполняется отдельно:
    его ответы — коды приёмов, а не выражения, и placeholder-ом он не
    размечен."""
    out, in_trainer = [], False
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {(override or {}).get(name, gen.ANSWERS[name])}')
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


def run(cells):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in cells:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


here = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'number_algebra'))
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
    'q1a': '15',                     # это u0, а не первый член
    'q1b': '15',                     # номер на единицу меньше
    'q1c': '3',                      # знак разности
    'q2d': '6',                      # знак разности
    'q2a': '-42',                    # шаг сделан тринадцать раз вместо двенадцати
    'q2b': '0',                      # ноль членов схема прощает, номером он не является
    'q3r': '3*n + 1',                # это формула суммы, а не ряда
    'q3a': '26',                     # это t4
    'q3b': '25',                     # добавлено десять карт вместо одиннадцати
    'q4u': '6',                      # знак
    'q4d': '-2',                     # знак
    'q5u': '12',                     # знак
    'q5d': '-3',                     # знак
    'q6p': '2',                      # p и q переставлены
    'q6q': '3',                      # то же
    'q6b': '40',                     # это S4, а не u5
    'q7a': '13',                     # это u5, а не сумма первых пяти
    'q7b': '60',                     # это S6, а не u6
    'q7c': '3',                      # первый член не такой
    'q7d': '2*n + 1',                # номер сдвинут на единицу
    'q8k': '-Rational(4, 5)',        # знак
    'q8u': '-Rational(21, 5)',       # это первый член, а не третий
    'q9p': '4',                      # это разность, а не член
    'q9t': '[9, 5, 1, 3]',           # знак у четвёртого члена
    'q9d': '4',                      # π потеряно
    'q10d': 'Rational(3, 2)',        # знак
    'q10c': 'm**2/(m + 2)',          # знак
    'q10f': '[-4*x + 8, -3*x + 8]',  # вторая функция не AS-линейна
    'q11k': '24',                    # номер на единицу меньше
    'q11s': '747.5',                 # сумма оборвана на член раньше
    'q12r': '3*n - 1',               # это ряды пирамиды, а не пятиугольный
    'q12t': '190',                   # девятнадцатое треугольное, но не пятиугольное
    'q12i': '19',                    # номер не тот
    'q12j': '11',                    # номер не тот
    'q12n': '5',                     # это число пачек, а не рядов
    'q12k': '13',                    # это число рядов, а не пачек
    'q13d': '-4 + ln(3)',            # знак при логарифме
    'q13s': '-90',                   # логарифмическая часть потеряна
    'qt_p': 'Rational(1, 3)',        # это коэффициент третьего члена
    'qt_d': '-ln(x)/2',              # разность не та
    'qt_n': '-2',                    # отрицательный корень номером не бывает
}
# Прогонять весь ноутбук ради каждой из сорока одной ошибки незачем:
# состояние копится один раз, и с неверным ответом переисполняется только
# та ячейка, в которой этот ответ живёт.
snapshots, cell_of = [], {}
space = {'__name__': '__main__'}
with contextlib.redirect_stdout(io.StringIO()):
    for index, source in enumerate(notebook_cells):
        snapshots.append(dict(space))
        for line in source.split('\n'):
            found = PLACEHOLDER.match(line)
            if found:
                cell_of[found.group(1)] = index
        exec(compile(filled(source), '<cell>', 'exec'), space)
chk('у каждого эталона нашлась своя ячейка', set(cell_of) == set(gen.ANSWERS))

missed = []
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}),
                     '<cell>', 'exec'), room)
    if not [line for line in buffer.getvalue().split('\n')
            if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
