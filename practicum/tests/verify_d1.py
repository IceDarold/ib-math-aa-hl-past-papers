"""Независимая проверка каждого ответа практикума D1.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не перебирать**. Ноутбук считает
перебором: verify_count получает описание объекта и складывает единицы.
Повтори тест тот же перебор — подтверждено будет только то, что Python
согласен сам с собой.

Поэтому здесь всё считается **формулами**: 9·⁹P₅, 6! − 2·7·4!, 7!·3!,
¹⁵C₅·¹⁰C₅·⁵C₅/3!. Это ровно тот путь, которым идёт экзаменуемый, и
ровно тот, которого нет в ноутбуке. Совпадение формулы с перебором и
есть проверка: перебор не знает формулы, формула не знает перебора.

Там, где схема оценивания даёт два метода, посчитаны оба — и оба сверены
друг с другом до того, как сверяться с ответом.

Отдельно проверяется устройство `each`: у трёх заданий перебрать всё
физически нельзя, и перечисляются только те объекты, кого касается
ограничение. Тест берёт уменьшенную копию той же задачи, где перебрать
можно и так и так, и требует, чтобы оба счёта совпали.

Затем прогоняется сам ноутбук: пустым (должен пройтись сверху вниз и
напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_d1.py
"""
import contextlib
import io
import json
import os
import re
import sys
from itertools import combinations, permutations, product
from math import comb, factorial, perm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_d1 as gen

n_ = sp.Symbol('n')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name], locals={'n_': n_})


print('=== Задачи 1–3: три счёта, формулами ===')
chk('1a: код с повторами — 5³', A('q1a') == 5 ** 3 == 125)
chk('1b: код без повторов — ⁵P₃ = 5·4·3', A('q1b') == perm(5, 3) == 5 * 4 * 3)
chk('и они отличаются ровно тем, что второй и третий выбор беднее',
    A('q1a') - A('q1b') == 125 - 60)

chk('2a: первая цифра не ноль — 9·⁹P₅', A('q2a') == 9 * perm(9, 5))
chk('и ¹⁰P₆ = 151200 — то же без ограничения, схема даёт за него M1A0',
    perm(10, 6) == 151200 and A('q2a') != perm(10, 6))
chk('и ⁹P₆ = 60480 — ограничение, наложенное на весь набор, тоже не ответ',
    perm(9, 6) == 60480 and A('q2a') != perm(9, 6))
chk('2b: по возрастанию — ⁹C₆, и это же ⁹C₃',
    A('q2b') == comb(9, 6) == comb(9, 3) == 84)
chk('и возрастающих ровно в 6! раз меньше, чем шестёрок цифр по порядку',
    perm(9, 6) == A('q2b') * factorial(6))

chk('3: комитет — ¹⁰P₃ · ⁷C₄', A('q3') == perm(10, 3) * comb(7, 4) == 25200)
chk('и ¹⁰C₃·3!·⁷C₄ — та же запись другим порядком',
    A('q3') == comb(10, 3) * factorial(3) * comb(7, 4))
chk('а ¹⁰C₃·⁷C₄ = 4200 забывает, что должности разные',
    comb(10, 3) * comb(7, 4) == 4200 and A('q3') == 6 * 4200)

print('\n=== Задача 4: блоки на полке ===')
chk('4a: пятнадцать книг в ряд — 15!', A('q4a') == factorial(15))
chk('4b: три блока, каждый со своим порядком, и порядок самих блоков',
    A('q4b') == factorial(6) * factorial(5) * factorial(4) * factorial(3))
chk('и без последнего 3! вышло бы 2073600 — вшестеро меньше',
    A('q4b') == 6 * (factorial(6) * factorial(5) * factorial(4)))
chk('4c: четыре книги одного континента — три случая',
    A('q4c') == comb(6, 4) + comb(5, 4) + comb(4, 4) == 21)
chk('и ⁴C₄ = 1 — тот самый случай, который теряют',
    comb(4, 4) == 1 and A('q4c') - comb(4, 4) == 20)

print('\n=== Задача 5: блок и симметрия ===')
chk('5a: Джек сразу за Андреа — семь объектов, один порядок внутри',
    A('q5a') == factorial(7) == 5040)
chk('и умножение на 2! дало бы 10080, чего условие не позволяет',
    factorial(7) * 2 == 10080 and A('q5a') != 10080)
chk('5b: Джек где-то после — половина всех порядков',
    A('q5b') == factorial(8) // 2 == 20160)
chk('и то же по позициям: (7+6+…+1)·6!',
    A('q5b') == sum(range(1, 8)) * factorial(6))

print('\n=== Задача 6: блок в ряду и разбор случаев ===')
chk('6a: блок из пяти в ряду из десяти — 6 положений на 5!',
    A('q6a') == (10 - 5 + 1) * factorial(5) == 720)
chk('и 6·5! здесь случайно совпало с 6!, о чём схема и пишет «accept 6!»',
    A('q6a') == factorial(6))
chk('а в ряду из одиннадцати мест эти два числа расходятся',
    (11 - 5 + 1) * factorial(5) != factorial(6))
chk('6b: Питер с краю — 2·⁸P₄, не с краю — 8·⁷P₄',
    A('q6b') == 2 * perm(8, 4) + 8 * perm(7, 4) == 10080)
chk('и случаи покрывают все десять мест: 2 + 8',
    2 + 8 == 10)

print('\n=== Задача 7: овцы, произведение и дополнение ===')
chk('7a: 6·5·6³ — Амбер и Брауни в разные загоны',
    A('q7a') == 6 * 5 * 6 ** 3 == 5 * 6 ** 4 == 6480)
chk('и то же дополнением: 6⁵ − 6⁴',
    A('q7a') == 6 ** 5 - 6 ** 4)
# сетка три ряда на два столбца: горизонтальных пар 3, вертикальных 4
pens = [(r, c) for r in range(3) for c in range(2)]
sides = sum(1 for i, j in combinations(range(6), 2)
            if abs(pens[i][0] - pens[j][0]) + abs(pens[i][1] - pens[j][1]) == 1)
chk('7: в сетке 3×2 соседних пар 7 — три горизонтальных и четыре вертикальных',
    sides == 3 + 4 == 7)
chk('7b: 6! − 2·7·4!',
    A('q7b') == factorial(6) - 2 * sides * factorial(4) == 384)
chk('и то же случаями: 4 угловых загона по 3 свободных, 2 средних по 2',
    A('q7b') == (4 * 3 + 2 * 2) * factorial(4))

print('\n=== Задача 8: бейсбол ===')
chk('8a: девять человек в ряд — 9!', A('q8a') == factorial(9) == 362880)
chk('8b: девочки блоком — 7!·3!', A('q8b') == factorial(7) * factorial(3))
chk('и без 3! вышло бы 5040 — впятеро с лишним меньше',
    A('q8b') == 6 * factorial(7))
chk('8c: хотя бы две девочки — сложить два случая',
    A('q8c') == comb(6, 3) * comb(3, 2) + comb(6, 2) * comb(3, 3) == 75)
chk('и то же дополнением: всё минус «ни одной» минус «ровно одна»',
    A('q8c') == comb(9, 5) - comb(3, 1) * comb(6, 4) - comb(6, 5))

print('\n=== Задача 9: две парты в ряд ===')
# два ряда по пять: соседних пар в ряду 4, рядов два, порядка два
chk('9: соседних упорядоченных пар парт 16, а не 18',
    2 * 4 * 2 == 16)
chk('9a: 16·8!', A('q9a') == 16 * factorial(8) == 645120)
chk('и то же вычитанием: ряд из десяти мест минус пара через границу',
    A('q9a') == 2 * factorial(9) - 2 * factorial(8))
chk('9b: из ответа (a) вычесть два случая, а не из 10!',
    A('q9b') == A('q9a') - (8 * 12 * factorial(6) + 8 * 10 * factorial(6)))
chk('и вычитать из 10! было бы неверно: Алвин и Бобби всё ещё вместе',
    A('q9b') != factorial(10) - (8 * 12 * factorial(6) + 8 * 10 * factorial(6)))

print('\n=== Задача 10: остатки по модулю три ===')
chk('10: три из одного класса вычетов или по одному из каждого',
    A('q10') == 3 * comb(10, 3) + 10 ** 3 == 1360)
chk('и то же дополнением: ³⁰C₃ минус те, у кого сумма не делится',
    A('q10') == comb(30, 3) - comb(10, 2) * comb(10, 1) * factorial(3))

print('\n=== Задача 11: три безымянные команды ===')
chk('11: ¹⁵C₅·¹⁰C₅·⁵C₅ поделить на 3!',
    A('q11') == comb(15, 5) * comb(10, 5) * comb(5, 5) // factorial(3) == 126126)
chk('и то же без деления: ¹⁴C₄·⁹C₄·⁴C₄',
    A('q11') == comb(14, 4) * comb(9, 4) * comb(4, 4))
chk('и то же мультиномиально: 15!/(5!·5!·5!·3!)',
    A('q11') == factorial(15) // (factorial(5) ** 3 * factorial(3)))
chk('а 756756 — это команды, посчитанные как различимые',
    comb(15, 5) * comb(10, 5) == 756756 and A('q11') * 6 == 756756)

print('\n=== Задача 12 и таймер: буква внутри счёта ===')
chk('12a: ⁿC₃ и n(n−1)(n−2)/6 — одно выражение',
    sp.simplify(A('q12a') - n_ * (n_ - 1) * (n_ - 2) / 6) == 0)
chk('и при n = 9 оно даёт 84', A('q12a').subs(n_, 9) == comb(9, 3) == 84)
apart = 2 * (n_ - 2) * (n_ - 3) / 2                # ²C₁ · ⁿ⁻²C₂
# ⁿC₃ = 2 · (число способов с двумя студентами врозь); сократить на (n−2)
quad = sp.simplify(sp.expand(A('q12a') - 2 * apart) * 6 / (n_ - 2))
chk('12b: уравнение сводится к n² − 13n + 36 = 0',
    sp.simplify(quad - (n_ ** 2 - 13 * n_ + 36)) == 0)
roots12 = sorted(sp.solve(sp.Eq(n_ ** 2 - 13 * n_ + 36, 0), n_))
chk('и у него два корня, 4 и 9', roots12 == [4, 9])
chk('но при n = 4 во второй группе один студент, а нужно не меньше трёх',
    4 - 3 < 3 <= 9 - 3)
chk('поэтому ответ — множество {9}, а не {4, 9}',
    A('q12b') == sp.FiniteSet(9))

roots_t = sorted(sp.solve(sp.Eq(n_ ** 2 - 3 * n_ - 504, 0), n_))
chk('таймер: n(n−1) − (2(n−1) − 7) = 513 сводится к n² − 3n − 504 = 0',
    sp.simplify(sp.expand(n_ * (n_ - 1) - (2 * (n_ - 1) - 7) - 513)
                - (n_ ** 2 - 3 * n_ - 504)) == 0)
chk('и корни −21 и 24, из которых студентами бывает один',
    roots_t == [-21, 24] and A('qt') == sp.FiniteSet(24))
chk('и 24·23 − 39 действительно 513', 24 * 23 - (2 * 23 - 7) == 513)

print('\n=== Устройство each: уменьшенная копия, посчитанная и так и так ===')
# те же две парты в ряд, но шесть детей за шестью партами в двух рядах по три
SMALL_ROW = 3
def small_side_by_side(one, other):
    return one // SMALL_ROW == other // SMALL_ROW and abs(one - other) == 1

full = sum(1 for seat in permutations(range(6))
           if small_side_by_side(seat[0], seat[1]))
by_each = sum(1 for seat in permutations(range(6), 2)
              if small_side_by_side(seat[0], seat[1])) * factorial(4)
chk(f'полный перебор шести детей даёт {full}, перебор по двоим с множителем — то же',
    full == by_each == 2 * 2 * 2 * factorial(4))

full2 = sum(1 for seat in permutations(range(6))
            if small_side_by_side(seat[0], seat[1])
            and not small_side_by_side(seat[2], seat[3]))
by_each2 = sum(1 for seat in permutations(range(6), 4)
               if small_side_by_side(seat[0], seat[1])
               and not small_side_by_side(seat[2], seat[3])) * factorial(2)
chk(f'и с двумя ограничениями тоже: {full2}', full2 == by_each2)

# и то же для узора полки: три книги, две с одного континента
SMALL_SHELF = 'AAB'
full3 = sum(1 for line in permutations(range(3))            # книги 0,1 — «A», 2 — «B»
            if abs(line.index(0) - line.index(1)) == 1)
patterns = [p for p in sp.utilities.iterables.multiset_permutations(list(SMALL_SHELF))
            if all(c * ''.join(p).count(c) in ''.join(p) for c in 'AB')]
by_pattern = len(patterns) * factorial(2) * factorial(1)
chk(f'узор полки с множителем даёт {by_pattern}, прямой счёт слитных — {full3}',
    by_pattern == full3 == 4)

print('\n=== Карточка приёмов сходится с корпусом ===')
import yaml                                                          # noqa: E402
with open(os.path.join(ROOT, 'practicum/skills/statistics-combinatorics.yaml')) as fh:
    card = yaml.safe_load(fh)
listed = [b for s in card['skills'] for b in s['blocks']]
chk(f'блоков в карточке {len(listed)}, и ни один не повторяется',
    len(listed) == len(set(listed)) == card['corpus']['effective_blocks'])
chk('лестница перечисляет ровно те же приёмы, что и список',
    card['ladder'] == [s['id'] for s in card['skills']])

import glob                                                          # noqa: E402
marks, seen = {}, set()
for path in sorted(glob.glob(os.path.join(
        ROOT, 'classification/generated/*/*/paper-*.json'))):
    with open(path) as fh:
        paper = json.load(fh)
    for block in paper['blocks']:
        if block['id'] not in seen:
            seen.add(block['id'])
            marks[block['id']] = block.get('marks', 0)
chk(f"баллы карточки сходятся с корпусом: {sum(marks[b] for b in listed)}",
    sum(marks[b] for b in listed) == card['corpus']['effective_marks'] == 83)

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: эталон проходит, пустой не падает ===')
PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

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
os.chdir(os.path.join(ROOT, 'practicum', 'statistics'))
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
    'q1a': '60',                              # счёт без повторов вместо с повторами
    'q1b': '125',                             # и наоборот
    'q2a': '151200',                          # ¹⁰P₆: ограничение забыто
    'q2b': '60480',                           # ⁹P₆: порядок посчитан
    'q3': '4200',                             # ¹⁰C₃·⁷C₄: должности не различены
    'q4a': 'factorial(14)',                   # одна книга потеряна
    'q4b': '2073600',                         # порядок самих блоков не посчитан
    'q4c': '20',                              # случай ⁴C₄ пропущен
    'q5a': '10080',                           # блок умножен на 2!
    'q5b': '5040',                            # ответ пункта (a)
    'q6a': '120',                             # только 5!, положения блока забыты
    'q6b': '3360',                            # только первый случай
    'q7a': '7776',                            # 6⁵: ограничение забыто
    'q7b': '336',                             # посчитано запрещённое
    'q8a': '40320',                           # 8! вместо 9!
    'q8b': '5040',                            # 7! без 3!
    'q8c': '60',                              # только «ровно две девочки»
    'q9a': '725760',                          # 2·9!: границы рядов нет
    'q9b': '69120',                           # только первый случай
    'q10': '360',                             # только один класс вычетов
    'q11': '756756',                          # команды посчитаны различимыми
    'q12a': 'binomial(n_, 3)*factorial(3)',   # ⁿP₃ вместо ⁿC₃
    'q12b': '{4, 9}',                         # оставлены оба корня
    'qt': '{23}',                             # найдено N, а не n
}
# Прогонять весь ноутбук ради каждой из двадцати четырёх ошибок дорого:
# перебор в задачах 4, 8 и 11 занимает секунды. Вместо этого состояние
# копится один раз, и с неверным ответом переисполняется только та ячейка,
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
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
