"""Прогоняет архивный ноутбук C2 целиком: пустым и с эталонными ответами.

Устроен так же, как check_archive_e2.py, check_archive_e3.py и
check_archive_d2.py, и по той же причине: в архивном ноутбуке нет ни
одного разбора, который проверялся бы отдельно, — вся его правильность
в том, что ответ из раздела Solutions проходит проверку в ячейке. Тест
берёт сам ноутбук, подставляет в каждый placeholder эталон из ANSWERS
генератора и требует, чтобы каждая проверка сказала ✅.

Заодно проверяется главное свойство формата: пустой ноутбук проходится
сверху вниз без единого исключения и печатает ⬜. Без этого его нельзя
залить на Kaggle, где ячейки исполняются автоматически.

Эталоны в ANSWERS взяты из markschemes, и здесь не записан ни один из
них: проверкам передаётся граница фигуры, и площадь берётся формулой
Грина по контуру, длина — суммой кусков, объём — теоремой Паппа. Формул
темы у них нет ни одной. Совпадение в этом тесте поэтому означает
согласие markscheme с самой геометрией, а не с моей записью, — сорок
раз подряд.

Проверок на одну больше, чем ответов: у шести вопросов ответ один,
а мер у фигуры две (радиус и периметр «C», периметр и площадь сектора),
и у двух — выражение от двух букв, которое меряется дважды. Поэтому
тест сверяет число ✅ с числом ⬜, а число placeholder-ов — с ANSWERS.

И третий прогон, которого у восьми предыдущих архивов не было: каждый
ответ по очереди заменяется типовой ошибкой — дуга вместо угла, сектор
вместо сегмента, потерянная треть конуса, — и проверка обязана сказать ❌.
Двух прогонов хватало, пока проверки были старые и обкатанные; здесь вся
геометрия новая, а проверка, которая всё принимает, ничего не стоит.
BREAK держит ошибку для каждого из тридцати девяти ответов.

Запуск:  python practicum/tests/check_archive_c2.py
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

import build_archive_c2 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного: q1_2r  = ...
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: дуга принята за хорду, взята меньшая часть вместо большей,
# половина хорды записана как хорда, потерян множитель ⅓, посчитан один
# сегмент из пяти, градусы подставлены в формулу для радиан.
BREAK = {
    'q1_1': '10',                  # длина дуги вместо угла
    'q1_2th': '2*pi/6',            # шесть частей вместо пяти
    'q1_2r': '12',                 # дуга вместо радиуса
    'q1_3': '6000*pi',             # полуокружность вместо четверти
    'q1_4': '1',                   # ответ оставлен в радианах
    'q1_5': '23.5560',             # малая дуга вместо большой
    'q1_6': '2.92',                # 45 = 12*theta + 10, один бортик забыт
    'q2_1': 'pi/16',               # оборот принят за pi
    'q2_2': '2.02546',             # взят половинный угол
    'q2_3': 'pi*t/16',             # то же вдвое меньше
    'q3_1': '10',                  # только дуга, без двух радиусов
    'q4_1': '23.75',               # меньший сектор вместо большего
    'q4_2': '40',                  # забыта одна вторая
    'q4_3': '38036.0',             # градусы подставлены как есть
    'q5_1': '4.06708',             # половина хорды
    'q5_2': '14.2828',             # половина хорды
    'q6_1t': 'sin(th)',            # забыта одна вторая
    'q6_1s': 'th/2',               # сектор вместо сегмента
    'q6_2': '2*th',                # сектор вместо сегмента
    'q7_1': '206.977',             # только прямоугольник, без сегмента
    'q7_2': '260 - 2.6*r',         # r вместо r^2
    'q7_3': '13.9328',             # один сегмент из пяти
    'q8_1': '1.65',                # theta - sin(theta), а не theta
    'q8_2r': '5.0',
    'q8_2p': '97.1487',            # только дуги, без двух торцов
    'q8_3': '(10 - 2*r)',          # не поделено на r
    'q8_4r': '5',                  # корень удвоен
    'q8_4th': '1',
    'q8_5th': '1.0',
    'q8_5r': '8.0',
    'q8_6': '24*pi/(th + 1)',      # потерян один радиус в периметре
    'q8_7': '0.8',
    'q9_1': '6',                   # взята только боковая поверхность
    'q9_2': '8*sqrt(3)*pi',        # потеряна треть
    'q9_3': '18*sqrt(5)*pi',       # потеряна треть
    'q9_4': 'm/h',
    'q9_5': 'h*(1 + m**2)',        # забыт корень
    'q9_6': '2552',                # потеряна треть
    'q9_7': '22.75',               # диаметр вместо радиуса
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
# первая ячейка — установочная: import из practicum/geometry
os.chdir(os.path.join(ROOT, 'practicum', 'geometry'))

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
t(f'проверок прошло столько же, сколько было пустых ({blanks})',
  answered.count('✅') == blanks)

print('--- каждый ответ по очереди испорчен ---')
t(f'ошибка заготовлена для каждого ответа ({len(gen.ANSWERS)})',
  set(BREAK) == set(gen.ANSWERS))
named = 0
for name, wrong in BREAK.items():
    out = run([filled(source, {name: wrong}) for source in cells])
    caught = [line for line in out.split('\n') if line.startswith('❌')]
    t(f'{name} = {wrong} отвергнут', bool(caught))
    # проверка не просто отвергла, а назвала промах. Портится один ответ,
    # но упасть может и следующая за ним проверка — фигуры строятся друг
    # из друга, — поэтому смотрим на все ❌ этого прогона.
    if any('does not measure that' not in line for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
