"""Прогоняет архивный ноутбук C6 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_d6.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются плоскости, прямые и
условия вопроса: основание перпендикуляра, отражение, общую точку плоскостей
и буквы, при которых они сходятся по прямой, проверка находит сама.
Совпадение означает согласие markscheme с плоскостями вопроса, а не с моей
записью, — сорок шесть раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
знак средней компоненты векторного произведения, нормаль вместо
направления, параметр вместо точки, основание вместо отражения, |λ|
вместо расстояния, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_c6.py
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

import build_archive_c6 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: знак средней компоненты векторного произведения, знак правой
# части, нормаль одной плоскости вместо направления прямой пересечения,
# λ вместо точки, основание перпендикуляра вместо отражения, |λ| вместо
# |λ|·|n|, одна точка вместо общей прямой.
BREAK = {
    'q1_1a': '-5',                                    # знак
    'q1_1b': '[-3, Rational(3, 2)]',                  # знак q
    'q1_1c': '3',                                     # нормали не кратны
    'q1_2c_i': '-18',                                 # знак
    'q1_2c_ii': '6',                                  # знак
    'q1_2e': 'vec(1, 8, -2) + lam*vec(1, -1, 1)',     # направление прямой в плоскости
    'q2_1': 'Eq(4*x + 2*y - 8*z, 0)',                 # знак средней компоненты
    'q2_2_AB': 'vec(3, 2, 0)',                        # BA
    'q2_2_AC': 'vec(2, -1, 7)',                       # CA
    'q2_2': 'Eq(14*x + 21*y - 7*z, 42)',              # знак средней компоненты
    'q2_3': 'vec(1, 1, 0)',                           # направление L1
    'q2_4': 'Eq(x + y + z, 5)',                       # знак средней компоненты
    'q2_5': 'vec(2, 1, 5)',                           # радиус-вектор точки
    'q2_6': 'Eq(-x + y - z, 5)',                      # знак правой части
    'q2_7_i': 'vec(5, 4, 2) + lam*vec(1, -1, 1) + mu*vec(-1, 7, -5)',   # точка L2 вместо направления
    'q2_7_ii': '18',                                  # знак
    'q2_8': 'Eq(-123*x + 6*y + 9*z, 0)',              # знак средней компоненты
    'q3_1_i': 'Rational(3, 2)',                       # 2λ = 3
    'q3_1_ii': 'Rational(3, 4)',                      # λ вместо точки
    'q3_2_L': '2*(2 + 3*s) + (-3 + 6*s)',             # знак компоненты нормали
    'q3_2_M': '2*(9 + t) + (11 + 2*t)',               # то же
    'q3_3_L': 'vec(0, -3, 2) + lam*vec(5, 1, -7)',    # нормаль P2
    'q3_3': '(6, -9, 8)',                             # знак λ
    'q4_1': 'vec(2, -3, -1)',                         # нормаль Π1
    'q4_2': 'vec(1, -2, 0) + lam*vec(1, -5, 3)',      # знак средней компоненты
    'q4_3_point': '(0, 2, -4)',                       # знак z
    'q4_3_direction': 'vec(4, 3, -1)',                # нормаль Π2
    'q5_1': '(Rational(41, 21), Rational(10, 21), Rational(23, 21))',   # знак y
    'q5_2': '(1, -2, 0)',                             # точка двух плоскостей
    'q5_2_value': '15',                               # знак
    'q5_3': '[Rational(4, 3), 18]',                   # d не тот
    'q5_4a': '(0, Rational(27, 2), Rational(17, 2))', # одна точка
    'q5_4b': '(29, 73.5, -49.5)',                     # знак y
    'q5_4c_i': '3',                                   # a из (b)
    'q5_4c_ii': '13',                                 # k не удвоено
    'q6_1': '47',                                     # не поделено на |n|
    'q6_2_i': 'Eq(y + 2*z, 8)',                       # знак компоненты нормали
    'q6_2_ii': '(0, 0.8, -1.6)',                      # знак
    'q6_3_i': '(-3, 18, -1)',                         # λ = +3
    'q6_3_ii': '3',                                   # |λ| вместо |λ||n|
    'q6_4_i': '(3, Rational(7, 2), 0)',               # точка по другую сторону
    'q6_4_ii': '11',                                  # квадрат
    'q7_1_i': '(Rational(3, 4), -2, Rational(-3, 4))',   # основание
    'q7_1_ii': 'vec(Rational(3, 2), -2, Rational(-3, 2)) + mu*vec(1, 1, -1)',   # направление не отражено
    'q7_2': '(-3, 6, 5)',                             # основание
    'q7_3': 'Eq(x + 3*y - z, Rational(-5, 2))',       # знак правой части P1
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
    generic = ('does not meet the conditions', 'something else', 'a condition does not hold',
               'nothing satisfies')
    if any(not any(word in line for word in generic) for line in caught):
        named += 1
    else:
        print(f'  без имени: {name}: {caught[0]}')
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
