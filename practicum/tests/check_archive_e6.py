"""Прогоняет архивный ноутбук E6 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_e5.py, и по той же причине: в архивном
ноутбуке нет ни одного разбора, который проверялся бы отдельно, — вся его
правильность в том, что ответ из markscheme проходит проверку в ячейке.

Три прогона, и каждый ловит своё.

Пустой. Ноутбук обязан пройтись сверху вниз без единого исключения
и напечатать ⬜ на каждую проверку. Без этого его нельзя залить на Kaggle,
где ячейки исполняются при заливке.

С эталонами. Каждый ответ подставляется из ANSWERS генератора, и каждая
проверка обязана сказать ✅. Для этой темы совпадение значит больше, чем
обычно: проверка меряет область, тело, поверхность или путь заново, а
эталон взят из markscheme, — значит, сошлись бумага и измерение.

С ошибками. Каждый ответ по очереди портится типовым промахом темы —
перемещение вместо пути, потерянное π, несдвоенная симметричная область, —
и проверка обязана сказать ❌.

Эталонов, которые проверка не может вывести сама, три из сорока семи:
7.7, 7.8 и 8.3, где формула не восстанавливается из PDF и вопрос задан
от чисел markscheme. Они сверяются по хешу.

Запуск:  python practicum/tests/check_archive_e6.py
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

import build_archive_e6 as gen

PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Мест для ответа 47, проверок столько же.
EXTRA = 0

# Типовой промах на каждый ответ: не случайные выражения, а то, чем тема
# ошибается — и что называют markschemes.
BREAK = {
    'q1_1': '6*pi',                    # взята половина промежутка
    'q1_2': '3.36',                    # интеграл вместо площади
    'q1_3': '4*pi',                    # зависимость от n потеряна
    'q1_4': '4 + log(7/3)/2',          # логарифм перевёрнут
    'q2_1': '3.04',                    # область удвоена раньше времени
    'q2_2': '1.52',                    # симметрия не использована
    'q2_3': '-Rational(1, 4)',         # вычтено наоборот
    'q2_4': '-0.240',                  # вычтено наоборот
    'q2_5': 'E - 1/E',                 # нижняя кривая не учтена
    'q2_6': '0.318',                   # сдана половина области
    'q2_7': '-Rational(9, 2)',         # вычтено наоборот
    'q2_8': '-Rational(63, 4)',        # вычтено наоборот
    'q3_1': '15*k**2/34',              # π потеряно
    'q3_2': '52.5',                    # π потеряно
    'q3_3': '(2 - sqrt(2))/4',         # π потеряно
    'q3_4': '3*pi**2/16',              # взята половина промежутка
    'q4_1': 'pi*(h + h**3)',           # делитель 3 потерян
    'q4_2': '2*sqrt(3)',               # π потеряно
    'q4_3': 'pi*(sqrt(3) + pi/3 + 4*log(2))',   # π вместо π/3 в среднем члене
    'q4_4': '2*pi*(E**2 + 8*E)',       # свободный член потерян
    'q4_5': '59.4',                    # взята вся кривая, а не левая ветвь
    'q4_6': '8*pi*r**4/5',             # степень r не та
    'q4_7': '27.2',                    # π потеряно
    'q5_1': '7.36',                    # решено до k², а не до k
    'q5_2': '3.21',                    # взят не тот корень
    'q5_3': '6',                       # решено до h³, а не до h
    'q5_4': '57',                      # π потеряно
    'q6_1': '9*sqrt(5)*pi',            # π вместо 2π
    'q6_2': 'pi*m*sqrt(1 + m**2)*h',   # степень h не та
    'q6_3': '2*pi*r**2',               # π вместо 2π
    'q6_4': '109',                     # π вместо 2π
    'q7_1': '-22.2',                   # перемещение вместо пути
    'q7_2': 'v0 + log(1 + v0)',        # знак второго слагаемого
    'q7_3': 'Rational(44, 27)',        # арифметика при подстановке
    'q7_4': '3',                       # перемещение вместо пути
    'q7_5': '2.85',                    # взят один кусок из двух
    'q7_6': '6.54',                    # взят один кусок из двух
    'q7_7': '5.73',                    # округление не то
    'q7_8': '7.69',                    # округление не то
    'q7_9': '2.13',                    # знак перемещения
    'q7_10': '1.0',                    # просто неверно
    'q7_11': '570',                    # взято округлённое время
    'q7_12': '6.87',                   # куски сложены не те
    'q8_1': '5*sqrt(3)*pi/2',          # делитель не тот
    'q8_2': '176300',                  # сдана ёмкость, а не дождь
    'q8_3': '4.22',                    # округление не то
    'q8_4': '100 - 600*exp(-t/10) - 5*t**2/2',   # постоянная не найдена
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
    swap = swap or {}
    out = []
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {swap.get(name, gen.ANSWERS[name])}')
            continue
        out.append(line)
    return '\n'.join(out)


def run(sources):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in sources:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


cells = code_cells()
names = set()
for source in cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
t(f'мест под ответ столько же, сколько эталонов ({len(names)})',
  names == set(gen.ANSWERS))

here = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'calculus'))

print('--- пустой прогон ---')
blank = run(cells)
t('пустой ноутбук проходится целиком', True)
t('в пустом прогоне нет ошибок', '❌' not in blank)
t('и нет ни одной галочки', '✅' not in blank)
blanks = blank.count('⬜')
t(f'пустых квадратов {blanks}', blanks == len(gen.ANSWERS))

print('--- прогон с эталонами ---')
answered = run([filled(source) for source in cells])
bad = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad:
    print('  ' + line)
t('ни одна проверка не провалилась', not bad)
t('пустых ответов не осталось', '⬜' not in answered)
t(f'галочек столько же, сколько пустых квадратов ({blanks})',
  answered.count('✅') == blanks + EXTRA)

print('--- каждый ответ по очереди испорчен ---')
t(f'ошибка заготовлена для каждого ответа ({len(gen.ANSWERS)})',
  set(BREAK) == set(gen.ANSWERS))
named = 0
for name, wrong in BREAK.items():
    out = run([filled(source, {name: wrong}) for source in cells])
    caught = [line for line in out.split('\n') if line.startswith('❌')]
    t(f'{name} = {wrong} отвергнут', bool(caught))
    if any('does not match the measurement' not in line and 'no match' not in line
           for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')
os.chdir(here)

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
