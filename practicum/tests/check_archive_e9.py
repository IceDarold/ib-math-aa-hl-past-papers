"""Прогоняет архивный ноутбук E9 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_e8.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаётся сама модель вопроса:
частица — скоростью или перемещением, связь величин — уравнением,
картинка треугольника — вершинами, модель оптимизации — формулой и её
областью. Ускорение проверка меряет сдвигом времени, связанную скорость —
тем, что связь не ломается, наибольшее — просмотром всего промежутка.
Совпадение означает согласие markscheme с моделью вопроса, а не с моей
записью, — сорок шесть раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
скорость вместо ускорения; первый разворот вместо второго; модуль
скорости со знаком; dh/dV без dV/dt; D² вместо D; вершина вместо целого, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок
названо по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_e9.py
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

import build_archive_e9 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: вторая координата взята у производной, а не у функции; найдена
# одна точка из трёх; максимум и минимум перепутаны; перегиб назван
# третьей цифрой мимо; строгое неравенство стало нестрогим; условие
# развёрнуто наоборот.
BREAK = {
    'q1_1': '3.15',                                      # сама высота, а не скорость
    'q1_2': '1.60',                                      # скорость v(7), а не ускорение
    'q1_3': '[2.26]',                                    # один момент из двух
    'q1_4': '0.252',                                     # скорость равна 4, а не ускорение
    'q1_5': '4.71',                                      # ноль скорости, а не ускорения
    'q1_6': '5.86',                                      # время, когда быстрее растёт A
    'q1_7': '0.996',                                     # знак потерян
    'q1_8': "'c'",                                       # «growth per year» схема не берёт
    'q2_1': '9.09',                                      # второй корень
    'q2_2': '1.62',                                      # s = 0 вместо v = 0: особый случай схемы
    'q2_3a': '6.12',                                     # второй разворот
    'q2_3b': 'Interval(6.12, 10)',                       # где перемещение убывает
    'q2_4': '0',                                         # скорость в момент разворота
    'q2_5': '0',                                         # скорость в момент разворота
    'q2_6': '-0.986',                                    # первый разворот
    'q3_1': '0',                                         # ускорение в вершине v
    'q3_2': '0.406',                                     # момент вместо значения
    'q3_3': '-2.72',                                     # модуль скорости со знаком
    'q3_4a': '0.718',                                    # момент вместо значения
    'q3_4b': '2.79',                                     # вершина v внутри, а не начало
    'q3_4c': '1.81',                                     # наибольшее вместо наименьшего
    'q3_4d': '-1.07',                                    # знак
    'q4_1': '30.0',                                      # десятичная на бумаге без калькулятора
    'q4_2': '0.0281',                                    # dr/dV без dV/dt
    'q4_3': '0.133',                                     # dh/dV без dV/dt
    'q4_4': '153',                                       # цепочка перевёрнута
    'q5_1': '-5.2',                                      # скорость со знаком
    'q5_2': '-425',                                      # скорость со знаком
    'q5_3': '0.724',                                     # знак убывания потерян
    'q6_1': '3*sqrt(3)/2',                               # это Q, а не R
    'q6_2': 'asin(Rational(2, 3))',                      # угол вместо синуса
    'q6_3a': "'down'",                                   # вогнутость наоборот
    'q6_3b': 'atan(2)',                                  # место вместо значения
    'q6_4': "'yes'",                                     # шест сравнили не с тем
    'q6_5': "'c'",                                       # вторая производная — только локально
    'q7_1': '0',                                         # x = 0 вне области
    'q7_2': '1.03',                                      # D² вместо D
    'q7_3': '2.60',                                      # корень лишний
    'q8_1': '0',                                         # начало вместо вершины скорости
    'q8_2a': '0',                                        # наибольший радиус, конец
    'q8_2b': '1.76',                                     # место вместо радиуса
    'q8_3': 'N',                                         # другой ноль d²P/dt²
    'q8_4': 'N/2',                                       # место вместо значения
    'q9_1': '(82.6, 4.41)',                              # вершина вместо целого
    'q9_2': '(1570, 7.36)',                              # вершина вместо целого
    'q9_3': '9.48*10**15',                               # вершина вместо целого
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
# первая ячейка — установочная: import из practicum/calculus
os.chdir(os.path.join(ROOT, 'practicum', 'calculus'))

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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 46)

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

generic = ('is something else', 'is not true', 'does not hold', 'value is elsewhere',
           'the number is something else', 'only something no longer', 'not this one')
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
