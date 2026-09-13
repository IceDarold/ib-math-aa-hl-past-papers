"""Прогоняет архивный ноутбук D3 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_a2.py, и по той же причине: в архивном
ноутбуке нет ни одного разбора, который проверялся бы отдельно, — вся
его правильность в том, что ответ из раздела Solutions проходит проверку
в ячейке. Тест берёт сам ноутбук, подставляет в каждый placeholder эталон
из ANSWERS генератора и требует, чтобы каждая проверка сказала ✅.

Заодно проверяется главное свойство формата: пустой ноутбук проходится
сверху вниз без единого исключения и печатает ⬜. Без этого его нельзя
залить на Kaggle, где ячейки исполняются автоматически.

Эталоны в ANSWERS взяты из markschemes, а проверкам передаётся модель
и событие: вероятность получается сложением P(X = k) по значениям.
Совпадение здесь поэтому означает согласие markscheme с самим
распределением, а не с моей записью, — двадцать четыре раза подряд.

Проверок ровно столько же, сколько ответов: у каждого ответа своя строка
проверки, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
граница сдвинута, cdf вместо pdf, условная не поделена, у внешней модели
вероятность внутреннего испытания, n округлено вниз, — и проверка обязана
сказать ❌. Сверх того считается, сколько ошибок названо по имени, а не
просто отвергнуто.

Запуск:  python practicum/tests/check_archive_d3.py
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

import build_archive_d3 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: граница «хотя бы» и «больше» сдвинута на единицу, накопленная
# вероятность вместо точечной, «меньше 49» взято как ≤ 49, условная не
# поделена, «хотя бы одна» вместо «ровно одной», граница из логарифма.
BREAK = {
    'q1_1': '0.753',                 # P(M ≤ 5): накопленная вместо точечной
    'q1_2': '0.0849',                # вероятность одного мешка
    'q1_3': '0.967',                 # P(X ≤ 10) вместо P(X = 10)
    'q1_4': '0.800',                 # P(Y ≤ 3) вместо P(Y = 3)
    'q2_1': '0.0327',                # 1 − P(X ≤ 10): десять выпало
    'q2_2': '0.304',                 # 1 − P(L ≤ 5): шесть попало
    'q2_3': '0.0362',                # 1 − P(A ≤ 30): тридцать выпало
    'q2_4': '0.102',                 # противоположное событие
    'q2_5': '0.215',                 # противоположное событие
    'q3_1': '5',                     # ожидаемое число округлено до целого
    'q3_2': '[0.641]',               # второй корень потерян
    'q3_3': '11.5',                  # множитель не возведён в квадрат
    'q4_1': '0.598',                 # не поделили на вероятность условия
    'q4_2': '0.204',                 # то же
    'q4_3i': '0.013',                # две значащие цифры
    'q4_3l': '0.890',                # «меньше 49» взято как ≤ 49
    'q4_3': '0.0150',                # тот же промах в знаменателе
    'q5_1': '0.0863',                # внешняя модель с вероятностью яблока
    'q5_2r': '0.122',                # один бросок вместо пяти
    'q5_2s': '0.0824',               # то же
    'q5_2': '0.660',                 # «хотя бы одна» вместо «ровно одной»
    'q6_1': '16',                    # граница округлена вниз
    'q6_2': '16.8321',               # граница из логарифма вместо числа
    'q6_3': '93',                    # соседнее n
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
