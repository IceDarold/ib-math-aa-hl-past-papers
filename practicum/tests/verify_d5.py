"""Независимая проверка каждого ответа практикума D5.

Правило серии: ответы выводятся заново, а не переписываются из решений.
Если решение и проверка совпали — два разных пути привели в одно место.

Для этой темы «независимо» значит **не складывать площадь так, как её
складывает ноутбук**. Ноутбук берёт площадь квадратурой Гаусса — Лежандра
под самой кривой, а буквы модели находит методом Ньютона по площадям.

Тест идёт другим путём — тем, что написан в схемах оценивания. Площадь —
statistics.NormalDist, то есть функция ошибок; граница — её обратная
функция; σ и μ — через z-значения и формулы, выписанные руками: σ = (x − μ)/z,
система двух линейных уравнений по Крамеру. Правило «95 % в пределах двух
σ» — точными дробями. Интервал Z в задании 12 — решённым неравенством,
а не проходом по оси.

Второй якорь — числа схем оценивания: 0.265985…, 197.136…, 0.207564…,
97.2981… и 4.82468…, 175.063… и 7.31913…, 3.408401…, 0.71907…, 1.47225…,
0.317310…

Затем ноутбук прогоняется пустым, с эталонами из ANSWERS генератора
и по разу на каждый испорченный ответ.

Запуск:  python practicum/tests/verify_d5.py
"""
import contextlib
import io
import json
import os
import re
import sys
from fractions import Fraction as F
from statistics import NormalDist

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_d5 as gen

res = []
Z = NormalDist()


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name])


def sig(value, sf=3):
    return f"{float(value):.{sf}g}"


def agrees(answer, exact, sf=3):
    return sig(answer, sf) == sig(exact, sf)


def near(value, anchor):
    """Совпадение с числом схемы оценивания до всех его напечатанных цифр.

    Схема печатает начало числа с многоточием, 0.265985…, — то есть
    обрезает, а не округляет. Поэтому допуск — единица последнего разряда.
    """
    places = len(anchor.split('.')[1]) if '.' in anchor else 0
    return abs(float(value) - float(anchor)) < 10 ** -places


print('=== Задание 1: яблоки Адама ===')
W1 = NormalDist(175, 8)
chk('1a: P(W < 170) = 0.265985 (markscheme)', near(W1.cdf(170), '0.265985'))
chk('1a: ответ', agrees(A('q1a'), W1.cdf(170)))
premium = W1.cdf(185) - W1.cdf(170)
chk('1c: P(170 < W < 185) = 0.628364 (markscheme)', near(premium, '0.628364'))
chk('1c: ответ в процентах', agrees(A('q1c'), 100 * premium))

print('\n=== Задание 2: без калькулятора ===')
for a in (0.7, 2.0, 5.0):
    X, Y = NormalDist(7, a), NormalDist(19, a)
    chk(f'2a: при a = {a} P(X > 10) = P(Y > 22)', abs((1 - X.cdf(10)) - (1 - Y.cdf(22))) < 1e-12)
chk('2a: ответ', A('q2a') == 10)
chk('2b: μ ± σ — 0.682689…, до двух цифр 0.68', sig(Z.cdf(1) - Z.cdf(-1), 2) == '0.68' == sig(A('q2b'), 2))
chk('2c: 1 − 0.32/2 = 0.84 по правилу, и кривая даёт 0.841345', sig(1 - F(32, 100) / 2, 2) == '0.84'
    and sig(NormalDist(19, 3).cdf(22), 2) == '0.84' and A('q2c') == sp.Float('0.84'))

print('\n=== Задание 3: правило из условия ===')
tail = (1 - F(95, 100)) / 2
chk('3a: хвост за двумя σ — (1 − 0.95)/2 = 2.5 % (markscheme)', tail == F(1, 40) and A('q3a') == sp.Float('2.5'))
chk('3a: кривая дала бы 2.275 % — ответ не с кривой', sig(100 * (1 - NormalDist(100, 20).cdf(140))) == '2.28')
eating = F(8, 10) * tail
cooking = F(2, 10) * F(1, 2)            # у кулинарных 140 — само среднее
chk('3b: 0.8·0.025 / (0.8·0.025 + 0.2·0.5) = 1/6 (markscheme)', eating / (eating + cooking) == F(1, 6)
    and A('q3b') == sp.Rational(1, 6))

print('\n=== Задание 4: рис ===')
W4 = NormalDist(204, 5)
above = 1 - W4.cdf(210)
chk('4a: P(W > 210) = 0.115069 (markscheme)', near(above, '0.115069') and agrees(A('q4a'), above))
below = 1 - 0.8 - above
# схема печатает здесь 0.084930… и ниже 0.0849302… — последняя цифра от
# округлённого 0.115069; точное значение 0.08493033
chk('4b: 1 − 0.8 − 0.115069 = 0.084930 (markscheme)', near(below, '0.084930') and agrees(A('q4b'), below))
w4 = W4.inv_cdf(below)
chk('4c: w = 197.136 (markscheme)', near(w4, '197.136') and agrees(A('q4c'), w4))
chk('4c: и между w и 210 — ровно 0.8', abs(W4.cdf(210) - W4.cdf(w4) - 0.8) < 1e-12)

print('\n=== Задание 5: сгруппированные данные ===')
mids = [F(35, 2), F(45, 2), F(55, 2), F(65, 2), F(75, 2)]
freq = [31, 42, 61, 46, 29]
n5 = sum(freq)
mean5 = sum(m * f for m, f in zip(mids, freq)) / n5
var5 = sum(f * (m - mean5) ** 2 for m, f in zip(mids, freq)) / n5
chk('5a(i): среднее 27.5 (markscheme)', mean5 == F(55, 2) and A('q5m') == sp.Float('27.5'))
chk('5a(ii): σ = 6.26374, делится на n (markscheme)', near(float(var5) ** 0.5, '6.26374')
    and agrees(A('q5s'), float(var5) ** 0.5))
Y5 = NormalDist(float(mean5), float(var5) ** 0.5)
chk('5b: квартили 23.2751 и 31.7248 (markscheme)', near(Y5.inv_cdf(0.25), '23.2751') and near(Y5.inv_cdf(0.75), '31.7248'))
iqr5 = Y5.inv_cdf(0.75) - Y5.inv_cdf(0.25)
chk('5b: IQR = 8.44965, до двух цифр 8.4 (markscheme)', near(iqr5, '8.44965') and agrees(A('q5b'), iqr5, 2)
    and sig(A('q5b'), 2) == '8.4')

print('\n=== Задание 6: трубки ===')
z75 = Z.inv_cdf(0.75)
s6 = 0.14 / z75
chk('6: z = 0.674489 (markscheme)', near(z75, '0.674489'))
chk('6: s = 0.14/z = 0.207564 (markscheme)', near(s6, '0.207564') and agrees(A('q6'), s6))
D6 = NormalDist(32, s6)
chk('6: и IQR этой модели 0.28', abs(D6.inv_cdf(0.75) - D6.inv_cdf(0.25) - 0.28) < 1e-12)

print('\n=== Задание 7: рост ===')
s7 = 10 / Z.inv_cdf(0.94)
chk('7: z = 1.55477, s = 6.43181 (markscheme)', near(Z.inv_cdf(0.94), '1.55477') and near(s7, '6.43181'))
chk('7: ответ', agrees(A('q7'), s7))
H7 = NormalDist(163, s7)
chk('7: и между 153 и 173 — 0.88', abs(H7.cdf(173) - H7.cdf(153) - 0.88) < 1e-12)

print('\n=== Задание 8: пшеница ===')
chk('8a: 1 − 0.288 − 0.434 = 0.278 (markscheme)', F(1) - F(288, 1000) - F(434, 1000) == F(278, 1000)
    and A('q8a') == sp.Float('0.278'))
z1, z2 = Z.inv_cdf(0.288), Z.inv_cdf(1 - 0.434)
chk('8b: z = −0.559236 и 0.166199 (markscheme)', near(z1, '-0.559236') and near(z2, '0.166199'))
# m + z1·s = 94.6, m + z2·s = 98.1 — по Крамеру
det = 1 * z2 - z1 * 1
m8 = (94.6 * z2 - z1 * 98.1) / det
s8 = (1 * 98.1 - 94.6 * 1) / det
chk('8b: по Крамеру m = 97.2981, s = 4.82468 (markscheme)', near(m8, '97.2981') and near(s8, '4.82468'))
chk('8b: ответ', agrees(A('q8b')[0], m8) and agrees(A('q8b')[1], s8))
H8 = NormalDist(m8, s8)
chk('8b: и площади модели — 0.288 и 0.434', abs(H8.cdf(94.6) - 0.288) < 1e-12 and abs(1 - H8.cdf(98.1) - 0.434) < 1e-12)
d8 = 2.41 / z75
chk('8d: d = 2.41/z = 3.57307 (markscheme)', near(d8, '3.57307') and agrees(A('q8d'), d8))

print('\n=== Задание 9: подсолнухи ===')
zg = Z.inv_cdf(0.02)
chk('9a: A = z(0.75) = 0.674489 (markscheme)', agrees(A('q9a'), z75))
# m + z75·s = 180 и (m + 35) + zg·2s = 180
det9 = 1 * (2 * zg) - z75 * 1
m9 = (180 * 2 * zg - z75 * 145) / det9
s9 = (1 * 145 - 180 * 1) / det9
chk('9b: z = −2.05374, m = 175.063, s = 7.31913 (markscheme)', near(zg, '-2.05374') and near(m9, '175.063')
    and near(s9, '7.31913'))
chk('9b: ответ', agrees(A('q9b')[0], m9) and agrees(A('q9b')[1], s9))
chk('9b: и у гигантских 98 % выше 180', abs(1 - NormalDist(m9 + 35, 2 * s9).cdf(180) - 0.98) < 1e-12)

print('\n=== Задание 10: перелёты ===')
z98 = Z.inv_cdf(0.98)
sigma10 = 7 / z98
chk('10a: z = 2.0537, σ = 3.408401 (markscheme)', near(z98, '2.0537') and near(sigma10, '3.408401'))
chk('10a: ответ', agrees(A('q10a'), sigma10))
T10 = NormalDist(75, sigma10)
over80 = 1 - T10.cdf(80)
chk('10b: P(T > 80) = 0.071193 (markscheme)', near(over80, '0.071193') and agrees(A('q10b'), over80))
cond10 = (T10.cdf(82) - T10.cdf(80)) / over80
# схема печатает 0.719075, точное 0.7190735: шестая цифра — от округлённых
# 0.051193 и 0.071193, поэтому якорь — пять цифр
chk('10c: 0.051193/0.071193 = 0.71907 (markscheme)', near(T10.cdf(82) - T10.cdf(80), '0.051193')
    and near(cond10, '0.71907') and agrees(A('q10c'), cond10))

print('\n=== Задание 11: кексы ===')
C11, B11 = NormalDist(62, 2.9), NormalDist(68, 3.4)
chk('11a: P(C < 61) = 0.365112 (markscheme)', near(C11.cdf(61), '0.365112') and agrees(A('q11a'), C11.cdf(61)))
total11 = 0.6 * C11.cdf(61) + 0.4 * B11.cdf(61)
chk('11c(i): P(B < 61) = 0.0197555, итог 0.226969 (markscheme)', near(B11.cdf(61), '0.0197555')
    and near(total11, '0.226969') and agrees(A('q11ci'), total11))
bayes11 = 0.6 * C11.cdf(61) / total11
chk('11c(ii): 0.965183 (markscheme)', near(bayes11, '0.965183') and agrees(A('q11cii'), bayes11))
needed = (0.157 - 0.4 * B11.cdf(61)) / 0.6
sigma11 = -1 / Z.inv_cdf(needed)
chk('11d: P(C < 61) = 0.248496, z = −0.679229, σ = 1.47225 (markscheme)', near(needed, '0.248496')
    and near(Z.inv_cdf(needed), '-0.679229') and near(sigma11, '1.47225'))
chk('11d: ответ', agrees(A('q11d'), sigma11))

print('\n=== Задание 12: случайная парабола ===')
two = 2 * Z.cdf(-1)
chk('12g: P(|Z| > 1) = 0.317310 (markscheme)', near(two, '0.317310') and agrees(A('q12g'), two))
# X1 > 0.5: √(Z² − 1) < −Z − 0.5, правая часть положительна, возводим: Z > −1.25
edge = sp.solve(sp.Eq(-sp.Symbol('z') - 0.5, sp.sqrt(sp.Symbol('z') ** 2 - 1)), sp.Symbol('z'))
chk('12h: граница X₁ = 0.5 — единственный корень z = −1.25', [float(e) for e in edge] == [-1.25])
for probe, inside in ((-1.1, True), (-1.3, False), (-0.9, False), (1.5, False)):
    x1 = -probe - (probe * probe - 1) ** 0.5 if probe * probe > 1 else None
    x2 = -probe + (probe * probe - 1) ** 0.5 if probe * probe > 1 else None
    holds = x1 is not None and x1 > 0.5 and x2 > 0.5
    chk(f'12h: при Z = {probe} событие {"выполнено" if inside else "не выполнено"}', holds == inside)
both12 = Z.cdf(-1) - Z.cdf(-1.25)
chk('12h: P(−1.25 < Z < −1) = 0.053005 (markscheme)', near(both12, '0.053005'))
chk('12h: 0.053005/0.317310 = 0.167 (markscheme)', agrees(both12 / two, 0.167) and agrees(A('q12h'), both12 / two))

print('\n=== Таймер ===')
X13 = NormalDist(10, 2)
chk('timer (a): P(X > 13) = 0.0668072 (markscheme)', near(1 - X13.cdf(13), '0.0668072') and agrees(A('qt_a'), 1 - X13.cdf(13)))
chk('timer (b): k = z(0.9) = 1.28155 (markscheme)', near(Z.inv_cdf(0.9), '1.28155') and agrees(A('qt_b'), Z.inv_cdf(0.9)))

BREAK_D5 = {
    'q1a': '0.734',                  # площадь с другой стороны
    'q1c': '0.628',                  # вероятность вместо процента
    'q2a': '4',                      # 7 − 3: сдвиг не в ту сторону
    'q2b': '0.6827',                 # просили две значащие цифры
    'q2c': '0.16',                   # хвост вместо остального
    'q3a': '5',                      # оба хвоста
    'q3b': 'Rational(1, 40)',        # P(> 140 | eating) — в обратную сторону
    'q4a': '0.885',                  # площадь с другой стороны
    'q4b': '0.2',                    # 1 − 0.8 без хвоста за 210
    'q4c': '199.8',                  # invNorm(0.2) — не та площадь
    'q5m': '26.5',                   # не то среднее
    'q5s': '6.28',                   # делили на n − 1
    'q5b': '8.45',                   # просили две значащие цифры
    'q6': '0.14',                    # половина IQR — это не σ
    'q7': '10',                      # половина интервала — это не σ
    'q8a': '0.28',                   # две значащие цифры
    'q8b': '[97.3, -4.82]',          # отрицательный корень
    'q8d': '7.15',                   # весь IQR поделён на z
    'q9a': '-0.674',                 # не та сторона
    'q9b': '[175, 14.6]',            # 2s вместо s
    'q10a': '-3.41',                 # отрицательный корень
    'q10b': '0.929',                 # площадь с другой стороны
    'q10c': '0.0512',                # не поделено на условие
    'q11a': '0.635',                 # площадь с другой стороны
    'q11ci': '0.365',                # только шоколадные
    'q11cii': '0.219',               # не поделено на условие
    'q11d': '2.9',                   # σ не менялось
    'q12g': '0.683',                 # внутри, а не снаружи
    'q12h': '0.0530',                # не поделено на условие
    'qt_a': '0.933',                 # площадь с другой стороны
    'qt_b': '2.56',                  # расстояние в сантиметрах, а не в σ
}

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
chk('с эталонами ни одного замечания', 'rounded on the way' not in answered
    and 'accepts it' not in answered and 'accepts both' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = BREAK_D5
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

missed, named = [], 0
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}),
                     '<cell>', 'exec'), room)
    rejected = [line for line in buffer.getvalue().split('\n') if line.startswith('❌')]
    if not rejected:
        missed.append(name)
        continue
    generic = ('gives something else', 'does not meet the conditions', 'condition fails',
               'no valid model')
    if not any(word in rejected[0] for word in generic):
        named += 1
    else:
        print(f'   без имени: {name}: {rejected[0]}')
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
print(f'   названы по имени {named} из {len(BREAK)}')
os.chdir(here_dir)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
