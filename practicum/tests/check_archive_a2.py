"""Прогоняет архивный ноутбук A2 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_a1.py, и по той же причине: в архивном
ноутбуке нет ни одного разбора, который проверялся бы отдельно, — вся
его правильность в том, что ответ из раздела Solutions проходит проверку
в ячейке. Тест берёт сам ноутбук, подставляет в каждый placeholder эталон
из ANSWERS генератора и требует, чтобы каждая проверка сказала ✅.

Заодно проверяется главное свойство формата: пустой ноутбук проходится
сверху вниз без единого исключения и печатает ⬜. Без этого его нельзя
залить на Kaggle, где ячейки исполняются автоматически.

Эталоны в ANSWERS взяты из markschemes, и здесь не записан ни один
из них: проверкам передаётся правило — первый член и знаменатель, —
а член и сумма получаются умножением и сложением. Формулы u₁r^(n−1)
у них нет. Совпадение в этом тесте поэтому означает согласие markscheme
с самим умножением, а не с моей записью, — тридцать три раза подряд.

Число проверок и число ответов здесь не совпадают, и это не сбой.
У 1.1, 1.2, 5.3, 5.5, 6.1 и 7.1 ответов больше, чем проверок: знаменатель
и член пишутся порознь, а сверяются вместе. У 1.2 наоборот — один список
членов и три проверки на нём. Разница считается один раз и сверяется
числом.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
знаменатель перевёрнут, знак потерян, номер округлён не в ту сторону,
первый год посчитан дважды, — и проверка обязана сказать ❌. BREAK
держит ошибку для каждого из тридцати пяти ответов.

Запуск:  python practicum/tests/check_archive_a2.py
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

import build_archive_a2 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: знаменатель перевёрнут, знак при извлечении корня потерян,
# первый год модели посчитан дважды, номер округлён не в ту сторону,
# сумма спутана с членом.
BREAK = {
    'q1_1r': '0.42',                 # знаменатель удвоен вместо корня
    'q1_1': '3.528',                 # это третий член
    'q1_2t': '[7, -21, -63]',        # знак у третьего члена
    'q1_2r': '3',                    # знак знаменателя
    'q1_3': 'Rational(65, 4)',       # медиана не поделена пополам
    'q1_4': '5250',                  # посчитаны 15%, а не оставшиеся 85%
    'q1_5': '9276',                  # первый год посчитан дважды
    'q2_1': '(10**n - 1)/10',        # делено на r, а не на r − 1
    'q2_2': '(10**n - 1)/9',         # множитель 10 потерян
    'q2_3p': 'Rational(16, 5)',      # делить на десять забыто
    'q2_3a': '9',                    # показатель на единицу меньше
    'q3_1': 'Rational(14, 45)',      # в знаменателе 1 + r вместо 1 − r
    'q3_3r': '1.23',                 # отношение перевёрнуто
    'q3_3d': '9.62',                 # путь не удвоен
    'q3_4p': '[sqrt(3)/3]',          # отрицательный корень потерян
    'q3_4x': 'exp(3)',               # показатель не тот
    'q4_1': 'Rational(2, 3)',        # множитель перед скобкой принят за u1
    'q4_2': 'Rational(53, 999)',     # знаменатель 999 вместо 990
    'q4_3': 'Rational(253, 990)',    # голова дроби взята как 0.253
    'q5_1': 'a**2/s',                # отношение перевёрнуто
    'q5_2': '[sqrt(3)]',             # отрицательный корень потерян
    'q5_3n': 'sqrt(3)',              # выбран положительный, а v99 отрицателен
    'q5_3': '15*sqrt(3)',            # знак
    'q5_5k': '12',                   # второй корень тот же, что первый
    'q5_5t': '[-7, 7, 7]',           # знак у третьего члена
    'q5_5r': '1',                    # знак знаменателя
    'q5_6': '-7',                    # это первый член, а не сумма
    'q6_1r': '1.728',                # это r³, а не r
    'q6_1': '26',                    # округлено вниз
    'q6_2': '63',                    # номер на единицу меньше
    'q6_3': '19',                    # номер на единицу меньше
    'q7_1n': 'n',                    # слагаемых сосчитано на одно меньше
    'q7_1': '(x**n - 1)/(x - 1)',    # та же ошибка в ответе
    'q7_2': '1/(1 - x**2)',          # знак знаменателя потерян
    'q7_3': '1 - 2*x**2 + 4*x**4 - 8*x**6',   # это f3, а не f4
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
# первая ячейка — установочная: import из practicum/number_algebra
os.chdir(os.path.join(ROOT, 'practicum', 'number_algebra'))

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
    # проверка не просто отвергла, а назвала промах: последовательности
    # строятся одна из другой, поэтому смотрим на все ❌ этого прогона
    if any('gives something else' not in line for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
