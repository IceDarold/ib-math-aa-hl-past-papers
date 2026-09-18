"""Прогоняет архивный ноутбук E8 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_c7.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаётся сама кривая вопроса.
Точку проверка находит ходьбой, вид её — по соседям, перегиб — хордой,
сторону оси — знаком второй координаты, а множества значений параметра
спрашивает у самого свойства. Совпадение означает согласие markscheme
с кривой вопроса, а не с моей записью, — тридцать девять раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
вторая координата, взятая у производной; максимум и минимум местами;
третья значащая цифра перегиба; строгое неравенство, ставшее нестрогим;
пропущенная точка, — и проверка обязана сказать ❌. Сверх того считается,
сколько ошибок названо по имени, а не просто отвергнуто.

Ячейки для третьего прогона не перезапускаются целиком: перед каждой
запоминается пространство имён, и испорченный ответ исполняется в нём
одном. Полный прогон архива идёт около минуты, и тридцать девять полных
прогонов теста не пережить.

Запуск:  python practicum/tests/check_archive_e8.py
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

import build_archive_e8 as gen

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
    'q1_1': '(2, 0)',                                    # y взят у производной
    'q1_2': '[(0, E), (pi, E)]',                         # средняя точка потеряна
    'q1_3': '(0.709, 0.709)',                            # y не подставлен
    'q1_4': '(3, -2 - 2*sqrt(5))',                       # взят нижний корень
    'q1_5': '[(1.94, 1.20), (-1.94, -1.20)]',            # максимум и минимум местами
    'q1_6': '(6, 6)',                                    # назван x₂, а не произведение
    'q1_7': '5.7',                                       # две значащие цифры
    'q1_8': 'Interval(-1, 1)',                           # область вместо значений
    'q2_1': "['minimum', 'maximum', 'minimum']",         # знак f″ прочитан наоборот
    'q2_2a': '6*x - 2*a',                                # знак при a
    'q2_2b': "['maximum', 'minimum']",                   # P и Q местами
    'q2_3': "'minimum'",                                 # знак a не учтён
    'q2_4a': '12*x**2 - 4*(a + b)*x + a*b',              # первая производная
    'q2_4b': "'minimum'",                                # знак корня прочитан наоборот
    'q3_1': "'minimum'",                                 # + и − местами
    'q3_2a': "'inflexion'",                              # чётность перепутана
    'q3_2b': "'minimum'",                                # чётность перепутана
    'q4_1': '-1.61',                                     # третья значащая цифра
    'q4_2': '(a + 2*r)/3',                               # a и r местами
    'q4_3': 'r + Rational(1, 3)*(a - r)',                # доля наоборот
    'q4_4': '(r, r)',                                    # вторая координата не ноль
    'q4_5a': '(1, 0)',                                   # координаты местами
    'q4_5b': '(0, 1)',                                   # взята верхняя ветвь
    'q4_6': '0.394',                                     # третья значащая цифра
    'q4_7': '0.655',                                     # третья значащая цифра
    'q4_8': "'minimum'",                                 # смена знака f″ прочитана как вершина
    'q5_1': '[(0, b), (-a/3, 4*a**3/27 + b)]',           # коэффициент 2/3 потерян
    'q5_2': '[(-sqrt(c), -2*c**Rational(3, 2) + 2),\n        (sqrt(c), 2*c**Rational(3, 2) + 2)]',
    'q6_1': "['above', 'below']",                        # знак у Q не проверен
    'q6_2': '4*a**3/27 + b > 0',                         # неравенство наоборот
    'q7_1a': 'FiniteSet(1)',                             # не то значение
    'q7_1b': 'Interval(0, oo)',                          # ноль включён
    'q7_1c': 'Interval(-oo, 0)',                         # ноль включён
    'q7_2a': 'Interval.open(0, 2)',                      # граница не там
    'q7_2b': 'FiniteSet(2)',                             # граница не там
    'q7_2c': 'Interval.open(2, oo)',                     # граница не там
    'q7_3': 'Or(c <= 0, d > 2*c**Rational(3, 2))',       # второй случай потерян
    'q8_1': '[(2, 2)]',                                  # кандидат не проверен на кривой
    'q8_2': '[(0, 0)]',                                  # точка вне области
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

generic = ('the slope is not zero', 'there is no point of inflexion',
           'the answer is a word', 'could not be checked')
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
