"""Независимая проверка каждого ответа практикума D3.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не складывать P(X = k)**. Ноутбук
складывает: verify_binomial суммирует вероятности значений, Expect и Var —
k·P и квадраты отклонений, verify_trials перебирает n. Повтори тест то же
самое — подтверждено будет только то, что Python согласен сам с собой.

Поэтому накопленная вероятность здесь берётся **регуляризованной неполной
бета-функцией**: P(X ≤ k) = I₁₋ₚ(n − k, k + 1). Это тождество, а не сумма,
и сложения в нём нет. Точечная — разностью двух таких. Среднее и дисперсия —
формулами np и np(1 − p), наименьшее n — логарифмом, n по приблизительной
вероятности — делением отрезка пополам по той же бета-функции. Это ровно
те пути, которых в ноутбуке нет.

И второй якорь — числа, которые печатает схема оценивания: 0.898128…,
0.0133198…, 0.493160… Совпадение с ними подтверждает, что вопрос
переписан верно, а не только что формулы согласны с суммой.

Затем прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает.

Запуск:  python practicum/tests/verify_d3.py
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
import mpmath as mp
import sympy as sp

import build_d3 as gen

mp.mp.dps = 30
res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name])


def sig3(value):
    return f"{float(value):.3g}"


def agrees(answer, exact):
    """Ответ — это точное значение, округлённое до трёх значащих цифр."""
    return sig3(answer) == sig3(exact)


# Формулы темы, выписанные один раз и больше нигде не повторяемые.
def cdf(n, p, k):
    """P(X ≤ k) через регуляризованную неполную бета-функцию — без суммы."""
    if k < 0:
        return mp.mpf(0)
    if k >= n:
        return mp.mpf(1)
    return mp.betainc(n - k, k + 1, 0, 1 - mp.mpf(p), regularized=True)


def pdf(n, p, k):
    return cdf(n, p, k) - cdf(n, p, k - 1)


def normal_above(x, mu, sigma):
    return 1 - mp.ncdf(x, mu, sigma)


print('=== Задание 1: маффины и рис ===')
p_muffin = mp.ncdf(61, 62, 2.9)
chk('1a: p из нормального распределения — 0.365112 (markscheme)',
    abs(p_muffin - mp.mpf('0.365112')) < 1e-6)
chk('1a: P(M = 5) = 0.213666 (markscheme)', abs(pdf(12, p_muffin, 5) - mp.mpf('0.213666')) < 1e-6)
chk('1a: ответ', agrees(A('q1a'), pdf(12, p_muffin, 5)))
p_rice = 1 - mp.mpf('0.8') - normal_above(210, 204, 5)
chk('1b: P(W < w) = 1 − 0.8 − P(W > 210) = 0.0849303', abs(p_rice - mp.mpf('0.0849303')) < 1e-7)
chk('1b: ответ, и это 0.382076 (markscheme)',
    agrees(A('q1b'), pdf(10, p_rice, 1)) and abs(pdf(10, p_rice, 1) - mp.mpf('0.382076')) < 1e-6)

print('\n=== Задание 2: дождь ===')
chk('2a: P(X = 10) = 0.0418894', abs(pdf(31, 0.2, 10) - mp.mpf('0.0418894')) < 1e-7)
chk('2a: и это C(31,10)·0.2¹⁰·0.8²¹ — формула сходится с бета-функцией',
    abs(pdf(31, 0.2, 10) - mp.binomial(31, 10) * mp.mpf("0.2") ** 10 * mp.mpf("0.8") ** 21) < 1e-12)
chk('2a: ответ', agrees(A('q2a'), pdf(31, 0.2, 10)))
chk('2b: хотя бы 10 это 1 − P(X ≤ 9) = 0.0745998', abs(1 - cdf(31, 0.2, 9) - mp.mpf('0.0745998')) < 1e-7)
chk('2b: ответ', agrees(A('q2b'), 1 - cdf(31, 0.2, 9)))
chk('2b: и граница важна — 1 − P(X ≤ 10) даёт другое', not agrees(A('q2b'), 1 - cdf(31, 0.2, 10)))

print('\n=== Задание 3 и 8: яблоки ===')
p_apple = mp.ncdf(185, 175, 8) - mp.ncdf(170, 175, 8)
chk('3: premium = 62.8364% (markscheme)', abs(p_apple - mp.mpf('0.628364')) < 1e-6)
box = 1 - cdf(40, p_apple, 29)
chk('3: P(A ≥ 30) = 0.073861 (markscheme)', abs(box - mp.mpf('0.073861')) < 1e-6)
chk('3: ответ', agrees(A('q3'), box))
chk('8: P(Y = 4) при Y ~ B(10, 0.073861) = 0.003944 (markscheme)',
    abs(pdf(10, box, 4) - mp.mpf('0.003944')) < 1e-6)
chk('8: ответ', agrees(A('q8'), pdf(10, box, 4)))
chk('8: с округлённым 0.0739 выходит 0.00395 — третья цифра другая',
    sig3(pdf(10, mp.mpf('0.0739'), 4)) == '0.00395')

print('\n=== Задание 4: рейсы ===')
sigma = 7 / (mp.sqrt(2) * mp.erfinv(2 * mp.mpf('0.98') - 1))
p_late = normal_above(80, 75, sigma)
chk('4: σ из P(T > 82) = 0.02, и P(T > 80) = 0.071193', abs(p_late - mp.mpf('0.071193')) < 1e-6)
chk('4d: E = np = 4.556353 (markscheme)', abs(64 * p_late - mp.mpf('4.556353')) < 1e-5)
chk('4d: ответ', agrees(A('q4d'), 64 * p_late))
chk('4e: P(L > 6) = 1 − P(L ≤ 6) = 0.1691196 (markscheme)',
    abs(1 - cdf(64, p_late, 6) - mp.mpf('0.1691196')) < 1e-6)
chk('4e: ответ', agrees(A('q4e'), 1 - cdf(64, p_late, 6)))

print('\n=== Задание 5: дисперсия 5.75 ===')
roots = sorted(float(r) for r in sp.solve(sp.Eq(25 * sp.Symbol('p') * (1 - sp.Symbol('p')),
                                                sp.Rational(575, 100)), sp.Symbol('p')))
chk('5a: np(1 − p) = 5.75 даёт два корня', len(roots) == 2)
chk('5a: и это 0.358579, 0.641421 (markscheme)',
    abs(roots[0] - 0.358579) < 1e-6 and abs(roots[1] - 0.641421) < 1e-6)
chk('5a: ответ', sorted(sig3(v) for v in A('q5p')) == sorted(sig3(v) for v in roots))
chk('5a: корни в сумме дают единицу — p и 1 − p', abs(sum(roots) - 1) < 1e-12)
chk('5b: Var(1 − 2X) = 4·5.75', A('q5v') == 4 * sp.Rational(575, 100))

print('\n=== Задание 6: лампы ===')
at_least_one = 1 - mp.mpf('0.95') ** 30
chk('6a: 1 − 0.95³⁰ = 0.785361 (markscheme)', abs(at_least_one - mp.mpf('0.785361')) < 1e-6)
chk('6a: и бета-функция согласна', abs(at_least_one - (1 - cdf(30, 0.05, 0))) < 1e-12)
chk('6a: ответ', agrees(A('q6a'), at_least_one))
overlap = cdf(30, 0.05, 2) - cdf(30, 0.05, 0)
chk('6b: пересечение 0.597540 (markscheme)', abs(overlap - mp.mpf('0.597540')) < 1e-6)
chk('6b: ответ 0.760847', agrees(A('q6b'), overlap / at_least_one)
    and abs(overlap / at_least_one - mp.mpf('0.760847')) < 1e-6)
chk('6b: без пересечения вышло бы больше единицы', cdf(30, 0.05, 2) / at_least_one > 1)

print('\n=== Задание 7: пшеница ===')
chk('7(i): P(H = 34) = 0.0133198 (markscheme)', abs(pdf(100, 0.434, 34) - mp.mpf('0.0133198')) < 1e-7)
chk('7(i): ответ', agrees(A('q7i'), pdf(100, 0.434, 34)))
chk('7(ii): меньше 49 это ≤ 48, и P = 0.848218 (markscheme)',
    abs(cdf(100, 0.434, 48) - mp.mpf('0.848218')) < 1e-6)
chk('7(ii): ответ условия', agrees(A('q7l'), cdf(100, 0.434, 48)))
chk('7(ii): ответ 0.0157033', agrees(A('q7ii'), pdf(100, 0.434, 34) / cdf(100, 0.434, 48)))
chk('7(ii): промах из оговорки схемы — 0.0149581 при ≤ 49',
    abs(pdf(100, 0.434, 34) / cdf(100, 0.434, 49) - mp.mpf('0.0149581')) < 1e-7)

print('\n=== Задание 9: копьё ===')
p_r, p_s = normal_above(60, 56.5, 3), normal_above(60, 57.5, 1.8)
chk('9: одиночные броски 0.1216…, 0.0824… (markscheme)',
    abs(p_r - mp.mpf('0.1216725')) < 1e-7 and abs(p_s - mp.mpf('0.0824333')) < 1e-7)
q_r, q_s = 1 - (1 - p_r) ** 5, 1 - (1 - p_s) ** 5
chk('9: квалификация 0.4772…, 0.3495… (markscheme)',
    abs(q_r - mp.mpf('0.4772640')) < 1e-6 and abs(q_s - mp.mpf('0.3495884')) < 1e-6)
chk('9: ответы для каждой', agrees(A('q9r'), q_r) and agrees(A('q9s'), q_s))
only_one = q_r + q_s - 2 * q_r * q_s
chk('9: вторым путём схемы, P(A) + P(B) − 2P(A)P(B) = 0.493160', abs(only_one - mp.mpf('0.493160')) < 1e-6)
chk('9: ответ', agrees(A('q9'), only_one))

print('\n=== Задание 10: наименьшее n ===')
boundary = math.log(0.01) / math.log(0.75)
chk('10: граница из логарифма 16.0078', abs(boundary - 16.0078) < 1e-4)
chk('10: ответ — целое справа от неё', A('q10') == math.ceil(boundary) == 17)
chk('10: при 16 ещё нет, при 17 уже да (markscheme, метод 2)',
    1 - 0.75 ** 16 < 0.99 < 1 - 0.75 ** 17)

print('\n=== Задание 11: Аманда ===')
chk('11a(i): P(E ≤ 6) = 0.898128 (markscheme)', abs(cdf(50, 0.08, 6) - mp.mpf('0.898128')) < 1e-6)
chk('11a(i): ответ', agrees(A('q11a'), cdf(50, 0.08, 6)))
chk('11a(ii): 0.203654 / 0.898128 (markscheme)', abs(pdf(50, 0.08, 4) - mp.mpf('0.203654')) < 1e-6)
chk('11a(ii): ответ', agrees(A('q11c'), pdf(50, 0.08, 4) / cdf(50, 0.08, 6)))
# n по приблизительной вероятности: P(E ≤ 6) убывает по n, и нужное n
# находится делением отрезка пополам, а не перебором подряд.
lo, hi = 7, 1000
while hi - lo > 1:
    mid = (lo + hi) // 2
    if cdf(mid, 0.08, 6) > mp.mpf('0.3675'):
        lo = mid
    else:
        hi = mid
chk('11b: делением пополам — 94', hi == 94 and sig3(cdf(94, 0.08, 6)) == '0.367')
chk('11b: у соседей округление другое',
    sig3(cdf(93, 0.08, 6)) != '0.367' and sig3(cdf(95, 0.08, 6)) != '0.367')
chk('11b: ответ', A('q11n') == 94)

print('\n=== Таймер: реагент ===')
p_t = 6 / mp.pi * mp.asin(mp.mpf(1) / 8)
chk('timer: ∫₀^0.5 6/(π√(16 − x²)) dx = (6/π)·arcsin(1/8) = 0.239358 (markscheme)',
    abs(p_t - mp.mpf('0.239358')) < 1e-6)
boundary_t = mp.log(0.01) / mp.log(1 - p_t)
chk('timer (c): граница 16.8321 (markscheme)', abs(boundary_t - mp.mpf('16.8321')) < 1e-4)
chk('timer (c): ответ 17', A('qt_n') == math.ceil(boundary_t) == 17)
chk('timer (d): P(Y = 3) = 0.242430 (markscheme)', abs(pdf(10, p_t, 3) - mp.mpf('0.242430')) < 1e-6)
chk('timer (d): ответ', agrees(A('qt_3'), pdf(10, p_t, 3)))

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
os.chdir(os.path.join(ROOT, 'practicum', 'statistics'))
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
chk('с эталонами ни одного замечания об округлении', 'rounded to three' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': '0.753',                  # это P(M ≤ 5): накопленная вместо точечной
    'q1b': '0.0849',                 # вероятность одного мешка, а не одного из десяти
    'q2a': '0.967',                  # P(X ≤ 10) вместо P(X = 10)
    'q2b': '0.0327',                 # 1 − P(X ≤ 10): десять выпало
    'q3': '0.0362',                  # 1 − P(A ≤ 30): тридцать выпало
    'q4d': '5',                      # ожидаемое число округлено до целого
    'q4e': '0.304',                  # 1 − P(L ≤ 5): шесть попало в «больше шести»
    'q5p': '[0.641]',                # второй корень потерян
    'q5v': '11.5',                   # множитель не возведён в квадрат
    'q6a': '0.215',                  # противоположное событие
    'q6b': '0.598',                  # не поделили на вероятность условия
    'q7i': '0.013',                  # две значащие цифры
    'q7l': '0.890',                  # «меньше 49» взято как ≤ 49
    'q7ii': '0.0150',                # тот же промах в знаменателе
    'q8': '0.0863',                  # внешняя модель с вероятностью яблока
    'q9r': '0.122',                  # один бросок, а не хотя бы один из пяти
    'q9s': '0.0824',                 # то же
    'q9': '0.660',                   # «хотя бы одна», а не «ровно одна»
    'q10': '16',                     # граница округлена вниз
    'q11a': '0.102',                 # противоположное событие
    'q11c': '0.204',                 # не поделили
    'q11n': '93',                    # соседнее n
    'qt_n': '16.8321',               # граница из логарифма, а не число испытаний
    'qt_3': '0.800',                 # P(Y ≤ 3): накопленная вместо точечной
}
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
chk('у каждого эталона есть типовая ошибка', set(BREAK) == set(gen.ANSWERS))

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
