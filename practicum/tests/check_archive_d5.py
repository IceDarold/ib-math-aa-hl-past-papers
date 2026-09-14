"""Прогоняет архивный ноутбук D5 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_d4.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются модель и условия
вопроса: площадь, границу, σ и μ находит сама проверка. Совпадение
означает согласие markscheme с кривой, а не с моей записью, — тридцать
пять раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
площадь с другой стороны, потерянная граница, отрицательный корень σ,
пересечение вместо условной, одна часть смеси, лишние значащие цифры, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_d5.py
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

import build_archive_d5 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: площадь с другой стороны от границы, одна граница из двух,
# процент вместо вероятности, отрицательный корень σ, уравнение в
# вероятностях вместо z, пересечение вместо условной, одна часть смеси.
BREAK = {
    'q1_1a': '0.923',                # площадь с другой стороны
    'q1_1b': '92.3',                 # не отвергнутые
    'q1_2': '0.929',                 # площадь с другой стороны
    'q1_3': '0.635',                 # то же
    'q1_4': '0.426',                 # то же
    'q1_5': '0.885',                 # то же
    'q1_6': '0.933',                 # то же
    'q1_7a': '0.734',                # то же
    'q1_7c': '0.628',                # вероятность вместо процента
    'q2_1': '0.28',                  # две значащие цифры
    'q2_2': '0.2',                   # 1 − 0.8 без хвоста за 210
    'q2_3': '5',                     # оба хвоста
    'q2_4a': '4',                    # сдвиг не в ту сторону
    'q2_4b': '0.6827',               # просили две значащие цифры
    'q2_4c': '0.16',                 # хвост вместо остального
    'q3_1': '199.8',                 # invNorm(0.2)
    'q3_2': '168.3',                 # invNorm(0.2) вместо invNorm(0.8)
    'q3_3': '2.56',                  # расстояние, а не число σ
    'q3_4': '-0.674',                # не та сторона
    'q3_5m': '26.5',                 # не то среднее
    'q3_5s': '6.28',                 # делили на n − 1
    'q3_5b': '8.45',                 # просили две значащие цифры
    'q3_6': '61.8',                  # граница b вместо a
    'q4_1': '-3.41',                 # отрицательный корень
    'q4_2': '0.14',                  # половина IQR — это не σ
    'q4_3': '7.15',                  # весь IQR поделён на z
    'q4_4': '10',                    # половина интервала — это не σ
    'q4_5': '2.9',                   # σ не менялось
    'q5_1': '[97.3, -4.82]',         # отрицательный корень
    'q5_2': '177.5',                 # середина между 170 и 185
    'q5_3': '[175, 14.6]',           # 2s вместо s
    'q6_1': '0.0766',                # не поделено на условие
    'q6_2': '0.0512',                # то же
    'q6_3g': '0.683',                # внутри, а не снаружи
    'q6_3h': '0.0530',               # не поделено на условие
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
    generic = ('gives something else', 'condition fails', 'does not meet the conditions',
               'no valid model')
    if any(not any(word in line for word in generic) for line in caught):
        named += 1
    else:
        print(f'  без имени: {name}: {caught[0]}')
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
