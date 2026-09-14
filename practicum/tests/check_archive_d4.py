"""Прогоняет архивный ноутбук D4 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_d3.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются таблица и условия
вопроса: буквы находит сама проверка. Совпадение означает согласие
markscheme с таблицей, а не с моей записью, — тридцать восемь раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
отброшенный корень, клетка без суммы, выколотые концы, E(X²) вместо
дисперсии, среднее значений без весов, коэффициенты в обратном порядке, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_d4.py
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

import build_archive_d4 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: корень, при котором клетка отрицательна; диапазон по одной клетке;
# выколотые концы; среднее значений без весов; E(X²) вместо дисперсии;
# множитель не в квадрате; коэффициенты производящей функции в обратном порядке.
BREAK = {
    'q1_1a': '0.198',                # сумма без одной клетки
    'q1_1m': '0.308',                # наибольшая вероятность вместо значения
    'q1_2e': 'Eq(2*k**2 - k + 0.88, 0)',
    'q1_2k': '0.2',                  # корень, при котором P(X = 1) < 0
    'q1_3p': 'Rational(1, 4)',       # клетка ½p взята как p
    'q1_3r': 'Interval.open(0, 1)',  # концы выколоты
    'q1_3q': 'Interval(0, 1)',       # клетка без суммы
    'q1_4': 'Interval(0, 0.4)',      # граница по третьей клетке
    'q2_1': '3.5',                   # среднее значений без весов
    'q2_2': '1.5',                   # то же
    'q2_3b': 'Rational(5, 2)',       # то же
    'q2_3d': 'Interval(1, 4)',       # не тот диапазон
    'q2_4p': '0.45',                 # «хотя бы раз» как «больше одного»
    'q2_4e': '2',                    # среднее значений без весов
    'q2_4r': '15',                   # тысяча посетителей потеряна
    'q2_5': '2.5',                   # среднее значений без весов
    'q2_6': '3',                     # то же
    'q3_1': '[0.2, 0.4]',            # p и q местами
    'q3_2': '2.44587',               # корень с отрицательной клеткой
    'q3_3': '[3, 4]',                # p и q местами
    'q3_4': '[-10, 115]',            # второе решение системы
    'q3_5qr': '[Rational(3, 8), Rational(5, 24)]',
    'q3_5': 'Rational(5, 2)',        # среднее значений без весов
    'q4_1': '4.4',                   # E(X²) без вычитания
    'q4_2': '3',                     # множитель потерян
    'q4_3ab': '[195.491, 20.2183]',  # не до целого
    'q4_3v': '18.3',                 # b не в квадрате
    'q4_4': '7.4896',                # E(Y²) без вычитания
    'q5_1b': 'Sum(p*(1 - p)**(x - 1), (x, 1, oo))',   # без множителя x
    'q5_1m': '9',
    'q5_1v': '9.49',                 # стандартное отклонение
    'q5_2p': '0.4',                  # две значащие цифры
    'q5_2v': '1.19',                 # дисперсия другой модели
    'q6_1': '1',                     # G(1) вместо G′(1)
    'q6_2': 'Rational(1, 10) + Rational(3, 5)*t + Rational(3, 10)*t**2',   # жёлтые
    'q6_3p': 'Rational(1, 3)',       # вероятность орла
    'q6_3y': 'Rational(1, 3) + t/2 + t**2/6',   # коэффициенты в обратном порядке
    'q6_3z': '2.57',
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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks > 20)

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
named = 0
for name, wrong in BREAK.items():
    out = run([filled(source, {name: wrong}) for source in cells])
    caught = [line for line in out.split('\n') if line.startswith('❌')]
    t(f'{name} = {wrong} отвергнут', bool(caught))
    # проверка не просто отвергла, а назвала промах
    if any('gives something else' not in line for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
