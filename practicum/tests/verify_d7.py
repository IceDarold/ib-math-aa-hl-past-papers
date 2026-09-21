"""Независимая проверка каждого ответа практикума D7.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **по формулам и точно**. Проверки
ноутбука ищут прямую поиском по дну суммы квадратов, а r берут как долю
объяснённого разброса. Тест делает ровно обратное — считает в точных
дробях учебные формулы

    a = Sxy / Sxx,   b = ȳ − a·x̄,   r = Sxy / √(Sxx·Syy)

где Sxy = Σ(x − x̄)(y − ȳ). Медиану и стандартное отклонение берёт модуль
statistics из стандартной библиотеки, а крайнее значение квартиля — перебор
по сетке с шагом 1/100, без неравенств.

Второй якорь — числа схем: (5, 19), 7, 1.58, 45, 25, 0.28, 0.47, 1.01 и
2.45, 0.981, 81, 0.805 и 2.88, 0.978, 8.52, 0.433 и 4.50, 12.3, (15, 11),
0.884, 1.37 и 64.5, 6.83, 0.0935 и 7.43, 36, 0.901, 86, 16, 17 и 20, 12,
34, 157, 160 и 20.9.

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора и
по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_d7.py
"""
import contextlib
import io
import json
import os
import re
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_d7 as gen

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    """Эталон из генератора — в пространстве имён ноутбука."""
    import kit
    return eval(gen.ANSWERS[name], dict(vars(kit)))


def near(value, anchor):
    """Совпадение с числом схемы до всех его напечатанных цифр."""
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


def exact(values):
    return [sp.Rational(str(v)) for v in values]


def formulas(xs, ys):
    """a, b, r и точка средних — учебными формулами, в точных дробях."""
    xs, ys = exact(xs), exact(ys)
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    slope = sxy / sxx
    return slope, my - slope * mx, sxy / sp.sqrt(sxx * syy), (mx, my)


print('=== Задача 1: Эйден и Бретт ===')
pair = sp.solve([sp.Eq(28 * sp.Rational(21, 2) + sp.Symbol('A') + sp.Symbol('B'), 318),
                 sp.Eq(sp.Symbol('B') - sp.Symbol('A'), 14)], dict=True)[0]
got = (pair[sp.Symbol('A')], pair[sp.Symbol('B')])
chk('сумма двоих 318 − 294 = 24, разность 14', got == (5, 19))
chk('Эйден ниже 6, Бретт выше 17 — размах действительно B − A', got[0] < 6 and got[1] > 17)
chk('эталон совпал', tuple(A('q1')) == got)

print('\n=== Задача 2: таблица частот ===')
table = {2: 5, 3: 1, 4: 4, 5: 3}
fits = [x for x in range(0, 60)
        if statistics.median([v for v, f in {**table, 6: x}.items() for _ in range(f)]) == 4.5]
chk('медиана 4.5 только при x = 7', fits == [7])
hours = [v for v, f in {**table, 6: 7}.items() for _ in range(f)]
chk('схема: σ = 1.58', near(statistics.pstdev(hours), '1.58'))
chk('а s с делением на n − 1 — 1.63, другое', near(statistics.stdev(hours), '1.63'))
chk('эталон совпал', A('q2a') == 7 and near(A('q2b'), '1.58'))

print('\n=== Задача 3: наименьшие квартили без выбросов ===')
ok_u = [u / 100 for u in range(4000, 7501)
        if 75 <= u / 100 + 30 and 10 >= (u / 100 - 20) - 30 and u / 100 - 20 <= 40]
chk('перебор: U от 45 до 60', ok_u[0] == 45 and ok_u[-1] == 60)
chk('эталон: U = 45, L = 25', A('q3a') == 45 and A('q3b') == 25)

print('\n=== Задача 4: ящик сна ===')
q1_, med, q3_ = 0.27, 0.28, 0.35
fence_hi = q3_ + 1.5 * (q3_ - q1_)
chk('схема: верхняя граница 0.47', near(fence_hi, '0.47'))
chk('0.46 не выброс', 0.46 < fence_hi)
chk('медиана ближе к Q1: хвост справа', med - q1_ < q3_ - med)
chk('эталон совпал', A('q4a') == 0.28 and near(A('q4b_fence'), '0.47')
    and A('q4b') == 'no' and A('q4c') == 'positive')

print('\n=== Задача 5: математика и естествознание ===')
a5, b5, r5, _ = formulas([64, 68, 72, 75, 80, 82, 85, 86], [67, 72, 77, 76, 84, 83, 89, 91])
chk('схема: a = 1.01, b = 2.45', near(a5, '1.01') and near(b5, '2.45'))
chk('схема: r = 0.981', near(r5, '0.981'))
chk('схема: 81', round(float(a5 * 78 + b5)) == 81)
chk('эталон совпал', A('q5a') == (1.01, 2.45) and A('q5b') == 0.981 and A('q5c') == 81)

print('\n=== Задача 6: кофейня ===')
a6, b6, r6, _ = formulas([3, 9, 11, 10, 5], [6, 10, 12, 11, 6])
chk('схема: a = 0.805, b = 2.88', near(a6, '0.805') and near(b6, '2.88'))
chk('схема: r = 0.978', near(r6, '0.978'))
chk('схема: 8.52', near(a6 * 7 + b6, '8.52'))
chk('эталон совпал', A('q6a') == (0.805, 2.88) and A('q6a_r') == 0.978
    and near(A('q6b'), '0.805') and A('q6c') == 8.52)

print('\n=== Задача 7: опыт ===')
a7, b7, _, m7 = formulas([3.3, 6.9, 11.9, 13.4, 17.8, 19.6, 21.8, 25.3],
                         [6.3, 8.1, 8.4, 11.6, 10.3, 12.9, 13.1, 17.3])
chk('схема: a = 0.433, b = 4.50', near(a7, '0.433') and near(b7, '4.50'))
chk('схема: 12.3', near(a7 * 18 + b7, '12.3'))
chk('схема: средние ровно (15, 11)', m7 == (15, 11))
chk('эталон совпал', A('q7a') == (0.433, 4.50) and A('q7b') == 12.3 and A('q7c') == (15, 11))

print('\n=== Задача 8: фортепиано ===')
a8, b8, r8, _ = formulas([28, 13, 45, 33, 17, 29, 39, 36],
                         [115, 82, 120, 116, 79, 101, 110, 121])
chk('схема: r = 0.884', near(r8, '0.884'))
chk('схема: a = 1.37, b = 64.5', near(a8, '1.37') and near(b8, '64.5'))
chk('схема: 5a = 6.83', near(5 * a8, '6.83'))
chk('эталон совпал', A('q8a') == 0.884 and A('q8b') == (1.37, 64.5) and A('q8c') == 6.83)

print('\n=== Задача 9: мороженое ===')
# x на y: предсказывают мороженое по детям — дети стоят на месте «x» формулы
a9, b9, _, _ = formulas([81, 175, 202, 346, 360], [15, 27, 23, 35, 46])
children = sp.Rational(-6, 10) * 25 ** 2 + 23 * 25 + 110
chk('схема: x = 0.0935y + 7.43', near(a9, '0.0935') and near(b9, '7.43'))
chk('модель: 310 детей', children == 310)
chk('схема: 36', round(float(a9 * children + b9)) == 36)
c9, d9, _, _ = formulas([15, 27, 23, 35, 46], [81, 175, 202, 346, 360])
chk('а обращённая прямая y на x дала бы 37', round(float((310 - d9) / c9)) == 37)
got = A('q9b')
chk('эталон совпал', near(got.rhs.coeff(sp.Symbol('y')), '0.0935') and A('q9c') == 36)

print('\n=== Задача 10: два теста ===')
xs10 = [52, 71, 100, 93, 81, 80, 88, 100, 70, 61]
ys10 = [58, 80, 92, 98, 90, 82, 100, 100, 65, 74]
a10, b10, r10, _ = formulas(xs10, ys10)
chk('схема: r = 0.901', near(r10, '0.901'))
chk('в условии прямая y = 0.822x + 18.4', near(a10, '0.822') and near(b10, '18.4'))
chk('Пауло: 10 вне [52, 100]', not (min(xs10) <= 10 <= max(xs10)))
chk('Джованни: 90 внутри [58, 100]', min(ys10) <= 90 <= max(ys10))
c10, d10, _, _ = formulas(ys10, xs10)
chk('схема: x на y даёт 85.6 → 86', round(float(c10 * 90 + d10)) == 86)
chk('а решённая y на x — 87', round((90 - 18.4) / 0.822) == 87)
chk('эталон совпал', A('q10a') == 0.901 and A('q10b') == 'extrapolation'
    and A('q10c_i') == 'wrong line' and A('q10c_ii') == 86)

print('\n=== Задача 11: p и q ===')
chk('схема: ȳ = 2.1875·7 + 0.6875 = 16', sp.Rational('2.1875') * 7 + sp.Rational('0.6875') == 16)
p, q = sp.symbols('p q')
found = sp.solve([sp.Eq(9 + 13 + p + q + 21, 80), sp.Eq(q - p, 3)], [p, q])
chk('схема: p = 17, q = 20', found == {p: 17, q: 20})
a11, b11, _, _ = formulas([5, 6, 6, 8, 10], [9, 13, 17, 20, 21])
chk('и с ними данные дают ту самую прямую', a11 == sp.Rational('2.1875')
    and b11 == sp.Rational('0.6875'))
chk('эталон совпал', A('q11a') == 16 and A('q11b') == (17, 20))

print('\n=== Задача 12: бассейн ===')
chk('схема: граница 10 + 1.5·4 = 16', 10 + sp.Rational(3, 2) * (10 - 6) == 16)
chk('схема: c = 42/2 − 9 = 12', sp.Rational(42, 2) - 9 == 12)
a_, c_ = sp.symbols('a c')
meet = sp.solve([sp.Eq(a_, sp.Rational(7, 4) * c_ + 20), sp.Eq(c_, a_ / 2 - 9)], [a_, c_])
chk('схема: ā = 34 (и c̄ = 8)', meet == {a_: 34, c_: 8})
chk('эталон совпал', A('q12a') == 16 and A('q12b_i') == 12 and A('q12b_ii') == 34)

print('\n=== Задача 13: слова ===')
h = [28, 13, 45, 33, 17, 29, 39, 36]
D = [115, 82, 120, 116, 79, 101, 110, 121]
chk('r не меняется от сдвига всех h', formulas([v - 3 for v in h], D)[2] == formulas(h, D)[2])
chk('после плохого сна медиана 0.35 = Q3 после хорошего', 0.35 == q3_)
chk('эталоны — те, что дают хеши',
    gen.digest(A('q13a')) == gen.D_13A and gen.digest(A('q13c')) == gen.D_13C
    and gen.digest(A('q13d')) == gen.D_13D and A('q13b') == 'no effect')

print('\n=== Таймер: размах рук и стопа ===')
chk('схема: A = 2.89·19.8 + 99.3 = 156.522 → 157',
    near(sp.Rational('2.89') * sp.Rational('19.8') + sp.Rational('99.3'), '157'))
A_, F_ = sp.symbols('A F')
meet = sp.solve([sp.Eq(F_, sp.Rational('0.335') * A_ - sp.Rational('32.6')),
                 sp.Eq(A_, sp.Rational('2.89') * F_ + sp.Rational('99.3'))], [A_, F_])
chk('схема: Ā = 160, F̄ = 20.9', near(meet[A_], '160') and near(meet[F_], '20.9'))
chk('эталон совпал', A('qt_a') == 157 and A('qt_b') == (160, 20.9))

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: пустой и с эталонами ===')
BREAK_D7 = {
    'q1': '(6, 18)',                     # сумма та же, но Эйден уже не ниже 6
    'q2a': '8',
    'q2b': '1.63',                       # деление на n − 1
    'q3a': '60',                         # другой край
    'q3b': '40',
    'q4a': '0.27',
    'q4b_fence': '0.525',                # 1.5 · Q3
    'q4b': "'yes'",
    'q4c': "'negative'",
    'q5a': '(2.45, 1.01)',               # a и b переставлены
    'q5b': '0.963',                      # r²
    'q5c': '81.4',                       # не целое
    'q6a': '(1.19, -3.09)',              # прямая x на y
    'q6a_r': '-0.978',
    'q6b': '2.88',
    'q6c': '5.12',                       # подстановка y = 7
    'q7a': '(0.433, 4.60)',
    'q7b': '12.5',                       # x на y, решённая относительно y
    'q7c': '(11, 15)',
    'q8a': '0.781',                      # r²
    'q8b': '(1.37, 64.6)',
    'q8c': '322.6',                      # 5b вместо 5a
    'q9b': 'Eq(x, 0.106*y + 4.41)',      # y на x, решённая относительно x
    'q9c': '37',
    'q10a': '0.812',
    'q10b': "'wrong line'",
    'q10c_i': "'extrapolation'",
    'q10c_ii': '87',
    'q11a': '15.3',
    'q11b': '(16, 21)',
    'q12a': '15',                        # 1.5 · Q3
    'q12b_i': '93.5',                    # подставлено не в ту прямую
    'q12b_ii': '8',                      # среднее детей, а не взрослых
    'q13a': "'a'",
    'q13b': "'decreases'",
    'q13c': "'b'",
    'q13d': "'systematic'",
    'qt_a': '-26.0',                     # не та прямая
    'qt_b': '(20.9, 160)',
}

with open(gen.NOTEBOOK) as fh:
    notebook = json.load(fh)
notebook_cells = [''.join(cell['source']) for cell in notebook['cells']
                  if cell['cell_type'] == 'code']

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
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 39)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
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
chk('у каждого эталона есть типовая ошибка', set(BREAK_D7) == set(gen.ANSWERS))

# Ответы-слова, выбранные из списка, называются по-своему: там «не тот
# ответ» и есть имя промаха — сказать больше хешу нечего.
generic = ('is a different number', 'something else at', 'not this one')
missed, named = [], 0
for name, wrong in sorted(BREAK_D7.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}), '<cell>', 'exec'), room)
    rejected = [line for line in buffer.getvalue().split('\n') if line.startswith('❌')]
    if not rejected:
        missed.append(name)
        continue
    if not any(word in rejected[0] for word in generic):
        named += 1
        print(f'   {name}: {rejected[0]}')
    else:
        print(f'   без имени: {name}: {rejected[0]}')
chk(f'все {len(BREAK_D7)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
print(f'   названы по имени {named} из {len(BREAK_D7)}')
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
