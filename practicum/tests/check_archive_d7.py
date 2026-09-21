"""Прогоняет архивный ноутбук D7 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_e8.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются сами данные вопроса.
Прямую проверка находит поиском по дну суммы квадратов, r — долей
объяснённого разброса, пропавшее значение — тем, что ставит ответ в набор
и пересчитывает. Совпадение означает согласие markscheme с данными
вопроса, а не с моей записью, — сорок восемь раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой, и
проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени. Четыре ответа-слова, проверяемые хешем, по имени не называются
и названы быть не могут.

Запуск:  python practicum/tests/check_archive_d7.py
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

import build_archive_d7 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: σ с делением на n − 1; r² вместо r; a и b местами; прямая x на y
# там, где нужна y на x, и наоборот; граница выброса как 1.5 · Q3; другой
# край отрезка допустимых квартилей; координаты средней точки местами.
BREAK = {
    'q1_1a': "'d'",
    'q1_1b': '(6, 18)',                   # Эйден не ниже 6
    'q1_2a': '8',
    'q1_2b': '1.63',                      # деление на n − 1
    'q1_3': '(16, 21)',
    'q1_4a': '6.54',
    'q1_4b_i': '13.8',
    'q1_4b_ii': '18.6',
    'q2_1a': '60',                        # другой край
    'q2_1b': '40',
    'q2_2': '15',                         # 1.5 · Q3
    'q2_3a': '0.27',                      # нижний квартиль
    'q2_3b_fence': '0.525',
    'q2_3b': "'yes'",
    'q2_3c': "'negative'",
    'q3_1': '0.956',                      # r²
    'q3_2': '0.781',                      # r²
    'q3_3': '-0.981',
    'q3_4': '0.90',                       # две цифры
    'q3_5': '0.910',                      # r²
    'q4_1a': '(4.50, 0.433)',             # местами
    'q4_1d': '(11, 15)',
    'q4_2': '(1.37, 64.6)',
    'q4_3': '(1.01, 2.54)',
    'q4_4': '(0.508, -3.13)',             # d на h
    'q4_5': '(40.2, 1.98)',
    'q5_1': '12.5',                       # x на y, решённая относительно y
    'q5_2b': '2.88',                      # свободный член
    'q5_2c': '5.12',                      # подставлено y = 7
    'q5_3': '322.6',                      # 5b
    'q5_4': '81.4',                       # не целое
    'q5_5': '38.7',                       # a·d без b
    'q5_6': '-26.0',                      # не та прямая
    'q5_7': '39.5',                       # a·x без b
    'q6_1b': 'Eq(x, 0.106*y + 4.41)',     # y на x, решённая относительно x
    'q6_1c': '37',
    'q6_2b': "'wrong line'",
    'q6_2c_i': "'extrapolation'",
    'q6_2c_ii': '87',
    'q7_1': '(11, 15)',
    'q7_2': '15.3',                       # без свободного члена
    'q7_3': '(20.9, 160)',
    'q7_4_i': '93.5',                     # не та прямая
    'q7_4_ii': '8',                       # среднее детей
    'q8_1': "'a'",
    'q8_2': "'decreases'",
    'q8_3': "'b'",
    'q8_4': "'systematic'",
}

passed = failed = 0


def t(name, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print(f'FAIL: {name}')


def code_cells():
    with open(gen.NOTEBOOK) as fh:
        doc = json.load(fh)
    return [''.join(cell['source']) for cell in doc['cells']
            if cell['cell_type'] == 'code']


def filled(source, swap=None):
    """Ячейка с подставленными эталонными ответами.

    swap подменяет один из них ошибкой: так устроен третий прогон.
    """
    swap = swap or {}
    out = []
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            if name not in gen.ANSWERS:
                raise AssertionError(f'нет эталона для {name}')
            out.append(f'{name} = {swap.get(name, gen.ANSWERS[name])}')
        else:
            out.append(line)
    return '\n'.join(out)


def run(cells):
    """Исполняет ячейки подряд в одном пространстве имён, ловя вывод."""
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in cells:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


cells = code_cells()
# первая ячейка — установочная: import из practicum/statistics
os.chdir(os.path.join(ROOT, 'practicum', 'statistics'))

print('--- пустой ноутбук ---')
blank = run(cells)
t('пустой ноутбук проходится целиком', True)
names = set()
for source in cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
t(f'placeholder-ов ровно столько же, сколько эталонов ({len(names)})',
  names == set(gen.ANSWERS))
t('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
t('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks > 30)

print('--- ноутбук с эталонными ответами ---')
answered = run([filled(source) for source in cells])
bad = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad:
    print('  ' + line)
t('ни одна проверка не провалилась', not bad)
t('пустых ответов не осталось', '⬜' not in answered)
t(f'проверок столько же, сколько пустых мест ({blanks})',
  answered.count('✅') == blanks + EXTRA)

print('--- каждый ответ по очереди испорчен ---')
t(f'ошибка заготовлена для каждого ответа ({len(gen.ANSWERS)})',
  set(BREAK) == set(gen.ANSWERS))

snapshots, cell_of = [], {}
space = {'__name__': '__main__'}
with contextlib.redirect_stdout(io.StringIO()):
    for index, source in enumerate(cells):
        snapshots.append(dict(space))
        for line in source.split('\n'):
            found = PLACEHOLDER.match(line)
            if found:
                cell_of[found.group(1)] = index
        exec(compile(filled(source), '<cell>', 'exec'), space)
t('у каждого эталона нашлась своя ячейка', set(cell_of) == set(gen.ANSWERS))

# «не тот ответ» у слова из списка и есть его имя: хешу больше сказать нечего
generic = ('is a different number', 'something else at', 'not this one')
named = 0
for name, wrong in sorted(BREAK.items()):
    room = dict(snapshots[cell_of[name]])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(cells[cell_of[name]], {name: wrong}), '<cell>', 'exec'),
             room)
    caught = [line for line in buffer.getvalue().split('\n') if line.startswith('❌')]
    t(f'{name} = {wrong.splitlines()[0]} отвергнут', bool(caught))
    if caught and not any(word in caught[0] for word in generic):
        named += 1
    elif caught:
        print(f'  без имени: {name}: {caught[0]}')
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{"ВСЁ ВЕРНО" if not failed else "ПРОВАЛЫ: " + str(failed)}  '
      f'({passed}/{passed + failed})')
sys.exit(1 if failed else 0)
