"""Независимая проверка каждого ответа практикума A2.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не ходить по прогрессии**. Ноутбук
ходит: verify_term доходит до члена умножением, verify_total складывает
первые n членов, verify_infinite складывает до тех пор, пока хвост
не станет мал, verify_least перебирает номера. Повтори тест то же
самое — подтверждено будет только то, что Python согласен сам с собой.

Поэтому здесь всё считается **формулами**: u₁r^(n−1), u₁(rⁿ−1)/(r−1)
и u₁/(1−r). Это ровно тот путь, которым идёт экзаменуемый, и ровно тот,
которого в ноутбуке нет. Совпадение формулы со сложением и есть
проверка: сложение не знает формулы, формула не знает сложения.

Наименьшее n тест находит логарифмом, а ноутбук — перебором, и это
второй такой же случай: схема оценивания печатает оба метода рядом
и принимает их наравне.

Затем прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_a2.py
"""
import contextlib
import io
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp
from sympy import Rational as R, expand, log, simplify, solve, sqrt, symbols

import build_a2 as gen

n, m, k, r, s, a, t_ = sp.symbols('n m k r s a t')
x = sp.Symbol('x')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name], locals={
        'n': n, 'm': m, 'k': k, 'r': r, 's': s, 'a': a, 't': t_, 'x': x,
        'sqrt': sp.sqrt, 'Rational': sp.Rational})


def near(one, two, tol=5e-4):
    """Сходятся ли два числа в пределах округления до трёх значащих цифр."""
    return abs(float(sp.N(one - two, 20))) <= tol * max(1.0, abs(float(two)))


def same(one, two):
    return sp.simplify(sp.sympify(one) - sp.sympify(two)) == 0


def sig3(value):
    return f"{float(value):.3g}"


# Формулы темы, выписанные один раз и больше нигде не повторяемые.
def u(first, ratio, i):
    return first * ratio ** (i - 1)


def S(first, ratio, i):
    return first * (ratio ** i - 1) / (ratio - 1)


def S_inf(first, ratio):
    return first / (1 - ratio)


def least(first, ratio, holds, what='total', cap=4000):
    """Наименьшее n, найденное по формуле, а не перебором сложения."""
    for i in range(1, cap):
        value = S(first, ratio, i) if what == 'total' else u(first, ratio, i)
        if holds(sp.N(value, 30)):
            return i
    return None


print('=== Задание 1: u1 = 80, u4 = 0.74088 ===')
ratio1 = sp.root(sp.Rational('0.74088') / 80, 3)
chk('1 (r): кубический корень из u4/u1', near(A('q1r'), ratio1))
chk('1 (r): и он ровно 0.21 — 0.21³ = 0.009261',
    same(sp.Rational('0.21') ** 3 * 80, sp.Rational('0.74088')))
chk('1a: второй член это u1·r', near(A('q1u'), u(80, A('q1r'), 2)))

print('\n=== Задание 2: u1 = 1, r = 10 ===')
chk('2a: S_n по формуле', same(A('q2s'), S(1, 10, n)))
chk('2a: и знаменатель именно 9', same(A('q2s'), (10 ** n - 1) / 9))
chk('2b: сумма 10 + ... + 10^n это та же формула с u1 = 10',
    same(A('q2t'), S(10, 10, n)))
# Проверка самого «show that»: сумма сумм действительно даёт печатное выражение.
sum_of_sums = (A('q2t') - n) / 9
chk('2b: сумма сумм совпадает с печатным ответом',
    same(simplify(sum_of_sums), (10 * (10 ** n - 1) - 9 * n) / 81))

print('\n=== Задание 3: рамки, площадь 20·(9/4)^(n−1) ===')
side = 4 * R(3, 2) ** (n - 1) * (5 * R(3, 2) ** (n - 1))
chk('3 (a)(i): произведение сторон даёт печатную формулу',
    same(simplify(side), 20 * R(9, 4) ** (n - 1)))
mean = S(20, R(9, 4), 10) / 10
chk('3a(ii): среднее это S10, делённое на десять',
    same(mean, A('q3p') * (R(9, 4) ** A('q3a') - 1)))
chk('3a(ii): p = 8/5 и a = 10', A('q3p') == R(8, 5) and A('q3a') == 10)
median = (u(20, R(9, 4), 5) + u(20, R(9, 4), 6)) / 2
chk('3b: медиана это среднее пятой и шестой площадей',
    same(median, A('q3q') * R(9, 4) ** 4))

print('\n=== Задание 4: сигма от i = 1 ===')
first4 = R(2, 3) * R(7, 8)
chk('4a: первый член это слагаемое при i = 1, а не множитель перед скобкой',
    A('q4u') == first4 and A('q4u') != R(2, 3))
chk('4b: S∞ по формуле', same(A('q4s'), S_inf(first4, R(7, 8))))
tail = lambda i: S_inf(first4, R(7, 8)) - S(first4, R(7, 8), i)
chk('4c: при 64 хвост меньше 0.001', tail(64) < R(1, 1000))
chk('4c: при 63 ещё нет', tail(63) > R(1, 1000))
chk('4c: ответ 64', A('q4n') == 64)
# И тот же номер логарифмом: хвост это S∞·r^n
boundary = math.log(float(R(1, 1000) / S_inf(first4, R(7, 8)))) / math.log(7 / 8)
chk('4c: логарифм даёт ту же границу 63.27', abs(boundary - 63.2675) < 1e-3)

print('\n=== Задание 5: a, s, t в геометрической прогрессии ===')
chk('5: t выводится из равенства отношений',
    same(A('q5t'), solve(sp.Eq(s / a, t_ / s), t_)[0]))
chk('5: и это то же, что s² = at', same(a * A('q5t'), s ** 2))

print('\n=== Задание 6: v2 = 5, v4 = 15 ===')
roots6 = sorted(solve(sp.Eq(u(5, r, 3), 15), r), key=str)
chk('6d: оба корня', sorted(A('q6r'), key=str) == roots6)
chk('6d: их ровно два и они противоположны', len(A('q6r')) == 2
    and same(sum(A('q6r')), 0))
chk('6e: v99 = 5r^97 отрицательно только при отрицательном r',
    sp.sign(u(5, A('q6n'), 98)) == -1)
chk('6e: v5 = v2·r³', same(A('q6v'), u(5, A('q6n'), 4)))
chk('6e: и это −15√3', same(A('q6v'), -15 * sqrt(3)))

print('\n=== Задание 7: k = 12 ===')
printed = [k - 5, 3 - 2 * k, 5 * k + 3]
here = [expr.subs(k, 12) for expr in printed]
chk('7(i): члены при k = 12', A('q7t') == here == [7, -21, 63])
chk('7(i) r: отношения равны', simplify(here[1] / here[0] - here[2] / here[1]) == 0)
chk('7(i) r: и равны −3', A('q7r') == here[1] / here[0] == -3)
chk('7(ii): |r| ≥ 1, суммы нет', abs(A('q7r')) >= 1)

print('\n=== Задание 8: u1 = 50, u4 = 86.4 ===')
ratio8 = sp.root(sp.Rational('86.4') / 50, 3)
chk('8 (r): кубический корень', near(A('q8r'), ratio8) and A('q8r') == 1.2)
chk('8: при 27 сумма больше 33500', S(50, R('1.2'), 27) > 33500)
chk('8: при 26 ещё нет', S(50, R('1.2'), 26) < 33500)
chk('8: ответ 27', A('q8n') == 27)
chk('8: логарифм даёт 26.90',
    abs(math.log(135) / math.log(1.2) - 26.9045) < 1e-3)

print('\n=== Задание 9: машина ===')
chk('9a: 15% потери оставляют 85%',
    A('q9a') == R('0.85') * 35000 == 29750)
value10 = u(A('q9a'), R('0.89'), 10)
chk('9b: десять лет это девять шагов от первого года',
    A('q9b') == round(float(value10)) == 10423)
chk('9b: и это не 0.89 в десятой степени',
    round(float(29750 * R('0.89') ** 10)) != A('q9b'))
chk('9c: при 20 годах меньше 3500', u(29750, R('0.89'), 20) < 3500)
chk('9c: при 19 ещё нет', u(29750, R('0.89'), 19) > 3500)
chk('9c: ответ 20', A('q9n') == 20)

print('\n=== Задание 10: периодическая дробь ===')
chk('10a: сигма от k = 0, первый член это сам множитель',
    same(A('q10s'), S_inf(R(53, 1000), R(1, 100))))
chk('10a: и это 53/990', A('q10s') == R(53, 990))
chk('10b: голова плюс хвост', same(A('q10f'), R(1, 5) + A('q10s')))
chk('10b: числитель и знаменатель взаимно просты',
    math.gcd(A('q10f').p, A('q10f').q) == 1)
chk('10b: и дробь действительно 0.2535353…',
    str(sp.N(A('q10f'), 12)).startswith('0.253535353'))

print('\n=== Задание 11: 1 + x + ... + x^n ===')
chk('11: слагаемых n + 1', same(A('q11n'), n + 1))
chk('11: сумма по формуле с n + 1 слагаемым',
    same(simplify(A('q11s') - S(1, x, n + 1)), 0))
for i in (2, 3, 4):
    chk(f'11: при n = {i} сумма совпадает с раскрытой',
        same(simplify(A('q11s').subs(n, i)),
             sum(x ** j for j in range(i + 1))))

print('\n=== Задание 12: знаменатель с x ===')
chk('12(i): f4 это пять слагаемых от r = 0 до 4',
    same(A('q12f'), sum((-2 * x ** 2) ** j for j in range(5))))
chk('12(i): и на один член больше, чем f3',
    same(expand(A('q12f') - sum((-2 * x ** 2) ** j for j in range(4))),
         16 * x ** 8))
chk('12(ii): S∞ при r = −x²', same(A('q12s'), S_inf(1, -x ** 2)))
chk('12(ii): знаменатель именно 1 + x²', same(A('q12s'), 1 / (1 + x ** 2)))

print('\n=== Задание 13: частица ===')
u1, u2, u3 = 1.80645, 1.46729, 1.19181
chk('13(i): отношение соседних членов', sig3(A('q13r')) == sig3(u2 / u1))
chk('13(i): и оно же между вторым и третьим',
    abs(u2 / u1 - u3 / u2) < 5e-4)
chk('13(i): это 2^(−3/10)', abs(float(u2 / u1) - 2 ** -0.3) < 5e-4)
whole = 2 * S_inf(sp.Float(u1), sp.Float(u2 / u1))
chk('13(ii): полный путь это удвоенная сумма', sig3(A('q13d')) == sig3(whole))
chk('13(ii): и он больше удвоенного первого максимума', A('q13d') > 2 * u1)

print('\n=== Таймер: второй корень ===')
condition = sp.Eq((3 - 2 * k) ** 2, (k - 5) * (5 * k + 3))
chk('timer (i): условие сводится к k² − 10k − 24 = 0',
    same(expand(condition.lhs - condition.rhs), -(k ** 2 - 10 * k - 24)))
chk('timer (i): корни 12 и −2', sorted(solve(condition, k)) == [-2, 12])
timer_terms = [expr.subs(k, A('qt_k')) for expr in printed]
chk('timer (ii): члены при k = −2', A('qt_t') == timer_terms == [-7, 7, -7])
chk('timer (ii): знаменатель −1', A('qt_r') == timer_terms[1] / timer_terms[0])
chk('timer (iii): при r = −1 члены гасятся парами',
    A('qt_s') == 0 and sum(u(-7, -1, i) for i in range(1, 2 * 5 + 1)) == 0)

print('\n=== Ноутбук: пустой и с эталонами ===')
with open(gen.NOTEBOOK) as fh:
    notebook = json.load(fh)
notebook_cells = [''.join(c['source']) for c in notebook['cells']
                  if c['cell_type'] == 'code']

PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')
TRAINER_FILL = '    ' + ', '.join(
    f"{i}: {gen.TRIGGER[i]!r}" for i in sorted(gen.TRIGGER)) + ','


def filled(source, override=None):
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


here_dir = os.getcwd()
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
    'q1r': '0.42',                   # знаменатель удвоен вместо возведения в куб
    'q1u': '3.528',                  # это третий член
    'q2s': '(10**n - 1)/10',         # делено на r, а не на r − 1
    'q2t': '(10**n - 1)/9',          # множитель 10 потерян
    'q3p': 'Rational(16, 5)',        # делить на десять забыто
    'q3a': '9',                      # показатель на единицу меньше
    'q3q': 'Rational(65, 4)',        # медиана не поделена пополам
    'q4u': 'Rational(2, 3)',         # множитель перед скобкой принят за u1
    'q4s': 'Rational(14, 45)',       # в знаменателе 1 + r вместо 1 − r
    'q4n': '63',                     # номер на единицу меньше
    'q5t': 'a**2/s',                 # отношение перевёрнуто
    'q6r': '[sqrt(3)]',              # отрицательный корень потерян
    'q6n': 'sqrt(3)',                # выбран положительный, а v99 отрицателен
    'q6v': '15*sqrt(3)',             # знак
    'q7t': '[7, -21, -63]',          # знак у третьего члена
    'q7r': '3',                      # знак знаменателя
    'q8r': '1.728',                  # это r³, а не r
    'q8n': '26',                     # округлено вниз
    'q9a': '5250',                   # посчитаны 15%, а не оставшиеся 85%
    'q9b': '9276',                   # первый год посчитан дважды
    'q9n': '19',                     # номер на единицу меньше
    'q10s': 'Rational(53, 999)',     # знаменатель 999 вместо 990
    'q10f': 'Rational(253, 990)',    # голова дроби взята как 0.253
    'q11n': 'n',                     # слагаемых сосчитано на одно меньше
    'q11s': '(x**n - 1)/(x - 1)',    # та же ошибка в ответе
    'q12f': '1 - 2*x**2 + 4*x**4 - 8*x**6',   # это f3, а не f4
    'q12s': '1/(1 - x**2)',          # знак знаменателя потерян
    'q13r': '1.23',                  # отношение перевёрнуто
    'q13d': '9.62',                  # путь не удвоен
    'qt_k': '12',                    # второй корень тот же, что первый
    'qt_r': '1',                     # знак знаменателя
    'qt_t': '[-7, 7, 7]',            # знак у третьего члена
    'qt_s': '-7',                    # это первый член, а не сумма
}
# Прогонять весь ноутбук ради каждой ошибки незачем: состояние копится
# один раз, и с неверным ответом переисполняется только та ячейка,
# в которой этот ответ живёт.
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
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
