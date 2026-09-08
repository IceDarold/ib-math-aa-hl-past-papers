"""Прогоняет архивный ноутбук E4 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_a1.py, и по той же причине: в архивном
ноутбуке нет ни одного разбора, который проверялся бы отдельно, — вся его
правильность в том, что ответ из раздела Solutions проходит проверку
в ячейке.

Три прогона, и каждый ловит своё.

Пустой. Ноутбук обязан пройтись сверху вниз без единого исключения
и напечатать ⬜ на каждую проверку. Без этого его нельзя залить на Kaggle,
где ячейки исполняются при заливке.

С эталонами. Каждый ответ подставляется из ANSWERS генератора, и каждая
проверка обязана сказать ✅.

С ошибками. Каждый ответ по очереди портится типовым промахом темы —
касательная вместо нормали, −m вместо −1/m, найдена одна точка из двух,
знак в знаменателе, — и проверка обязана сказать ❌. Без этого прогона
проверка вида «всегда ✅» прошла бы тест незамеченной.

Эталоны в ANSWERS взяты из markschemes. Записанный эталон здесь один
из тридцати двух: x = S/e в 4.5, где кривая зависит от буквы и ходить
по ней не выйдет. Остальные проверки эталона не хранят — они идут по
кривой из условия, — и для них совпадение здесь означает согласие
markscheme с самой задачей, а не с моей записью.

Запуск:  python practicum/tests/check_archive_e4.py
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

import build_archive_e4 as gen

PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Мест для ответа 39, а проверок 35: четыре вопроса сдают по два и по три
# ответа в одну проверку — пара наклонов в общей точке, точка и постоянная
# при ней. Пустых квадратов при этом ровно столько же, сколько проверок:
# на одну незаполненную ячейку приходится один ⬜, а не два.
EXTRA = 0

# Типовой промах на каждый ответ. Все они из markschemes и из разборов:
# это не случайные числа, а то, чем тема ошибается.
BREAK = {
    'q1_1': '-6',                       # знак наклона
    'q1_2': '17',                       # f(4) взято не с прямой
    'q1_3': '30*x - 100',               # прямая мимо точки касания
    'q1_4': '-15*sin(pi*k/50)',         # потерян множитель pi/50
    'q1_5': 'b**2*(x + r)',             # знак у r
    'q1_6': '-r',                       # то же в ответе про R
    'q2_1': '2*x + Rational(17, 2)',    # сдана касательная вместо нормали
    'q2_2': '-t**2',                    # взято −m, а не −1/m
    'q3_1': '(2*log(45), 90*exp(-log(45)/2))',   # y не досчитан
    'q3_2': '[8, -2]',                  # лишний корень вне области
    'q3_3': '(0.863, 0.863)',           # подставлено в f', а не в f
    'q3_4': '[2.73]',                   # найдено одно значение из двух
    'q4_1': '(1 - y*(1 + log(x*y)))/(1 + x*log(x*y))',   # потеряна единица
    'q4_2': '(3*x**2 + 1)/y',           # двойка потеряна
    'q4_3': '(2*x - exp(x + y))/(exp(x + y) + 2*y)',     # знак в знаменателе
    'q4_4': '4*(3 - x)/(y - 2)',        # знак в знаменателе
    'q4_5': 'S*E',                      # e не туда
    'q5_1': 'x',                        # прямая через точку, но не касательная
    'q5_2': '-3*x/2 + Rational(5, 2)',  # знак свободного члена
    'q5_3': '[(0.331, -0.743)]',        # найдена одна точка из двух
    'q5_4': '(-0.451, 0.451)',          # вторая координата не с кривой
    'q6_1': 'k**2*y*(1 - y/N)',         # второй множитель потерян
    'q6_2': '3',                        # знак
    'q6_3': '-3',                       # сдана первая производная
    'q6_4': ('(2*x + y + x*((x**2 + x*y - 3*y**2)/(x**2 + x*y))**2'
             ' - (x + 7*y)*(x**2 + x*y - 3*y**2)/(x**2 + x*y))/(x**2 + x*y)'),
    'q6_5': 'Rational(-17, 10)',        # сдана первая производная вместо второй
    'q7_1': 'sin(k)',                   # минус у производной косинуса
    'q7_2': 'sec(k)',                   # квадрат потерян
    'q7_3': 'x/y',                      # перевёрнуто
    'q7_4': 'a/sqrt(a*b)',              # минус потерян
    'q7_5': 'b/sqrt(a*b) + 1',          # просто неверно
    'q8_1': '3 - E/2',                  # знак при переносе
    'q8_2': '(2*E + E**2)/4',           # версия корпуса, а не бумаги
    'q8_3': '2',                        # k подобрано на глаз
    'q8_4': '3',                        # сдано значение f, а не наклон
    'q8_5': '1',                        # простой корень вместо двойного
    'q8_6': 'E**2',                     # точка не та, хотя на вид похожа
    'q8_7': '1',                        # точка не на прямой y = x
    'q8_8': 'Rational(3, 2)',           # a подобрано на глаз
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
    """Ячейка с подставленными эталонными ответами."""
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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks > 20)

print('--- ноутбук с эталонными ответами ---')
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
    if any('not the derivative' not in line and 'no match' not in line
           for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
