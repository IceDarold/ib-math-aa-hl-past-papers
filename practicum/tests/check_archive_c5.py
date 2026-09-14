"""Прогоняет архивный ноутбук C5 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_d6.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются точки, прямые и
условия вопроса: четвёртую вершину, точку пересечения, букву и угол
проверка находит сама. Совпадение означает согласие markscheme с точками
вопроса, а не с моей записью, — пятьдесят два раза подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
вершина не в том порядке, радиус-вектор вместо направления, знак точки
из декартовой формы, параметр одной прямой в другой, тупой угол, курс от
востока, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_c5.py
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

import build_archive_c5 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: вершина не в том порядке, середина за половину вектора, вектор
# вместо длины, радиус-вектор вместо направления, знак из декартовой формы,
# параметр одной прямой в другой, тупой угол, курс от востока.
BREAK = {
    'q1_1a': '(-1, -8, -2)',                      # D = a + b − c
    'q1_1b': '(-1, -5, 1)',                       # середина AB
    'q1_2a': '(-2, -1, -2)',                      # половина AB, а не середина
    'q1_2b': '6',                                 # весь диаметр
    'q1_3': '(-3, -4, 9)',                        # вектор вместо длины
    'q1_4': '29',                                 # без корня
    'q1_5_AB': 'vec(1 - k, 4, 2)',                # BA
    'q1_5_AC': 'vec(-4, 2, 1)',                   # CA
    'q1_5b': '5',                                 # k − 1 = 4
    'q1_6a': 'Interval(13, 28)',                  # наименьшее — |a|
    'q1_6b': 'vec(Rational(-180, 13), Rational(75, 13))',   # b, а не a + b
    'q1_7_OM': 'a + k*a',                         # AB принят за a
    'q1_7_MC': 'a - (1 - k)*c',                   # CM
    'q2_1': 'vec(5, 12)',                         # не растянут до 15
    'q2_2': '(1 - 2*k)*2*la**2*cos(theta) - la**2 + k*(1 - k)*la**2',   # |c|² = |a|²
    'q2_3_i': '5*p - 42',                         # знак −5
    'q2_3_ii': '(-8*p, -54)',                     # вектор вместо числа
    'q2_4_C': '(k*t, k/t)',                       # это сама A
    'q2_4_CA': 'vec(-2*k*t, -2*k/t)',             # AC
    'q2_4_CB': 'vec(k/t**3 - k*t, k*t**3 - k/t)', # BC
    'q3_1': '0.927',                              # угол между OB и OC
    'q3_2': 'cos(1/n) + sin(1/n)',                # не поделено на |u||v|
    'q3_3': '0',                                  # cos θ вместо θ
    'q3_4': '4.8',                                # две значащие цифры
    'q4_1': 'vec(-1, 0, 3) + lam*vec(2, 1, 1)',   # 3 − z: знак
    'q4_2': 'vec(-1, 2, 0) + lam*vec(2, 3, 1)',   # знаки точки
    'q4_3a': 'vec(7, 1, 2) + lam*vec(-1, 1, -13)',   # местами
    'q4_3b': 'vec(2, -4, 2) + mu*vec(7, -6, 1)',  # радиус-вектор B
    'q4_4': '-3',                                 # другое направление
    'q5_1': '[-4 + 3*sqrt(2)]',                   # потерян корень
    'q5_2': '139.8',                              # тупой
    'q5_3': '2*t/sqrt(4*t**2 + (3 + t)**2)',      # одна длина
    'q6_1': '(2, 4, -4)',                         # λ в L2
    'q6_2': '1',                                  # t вместо s
    'q6_3_pair': '[-1, 2]',                       # местами
    'q6_3': '(17, 11, 15)',                       # s в M
    'q6_4_k': '-2',                               # знак
    'q6_4_A': '(2/(a - 2) - 1, 1/(a - 2), (3*a - 7)/(a - 2))',   # t в L1
    'q7_1': "'skew'",                             # параллельные — не скрещиваются
    'q7_2': "'intersecting'",                     # третья не проверена
    'q7_2_pair': '[-1, 2]',                       # знак μ
    'q7_3_line': 'vec(1, 2, 3) + lam*vec(5, 0, 2)',   # радиус-вектор C
    'q7_3': "'parallel'",                         # направления не кратны
    'q7_3_pair': '[Rational(1, 4), Rational(-1, 2)]',   # знак μ
    'q7_4': '[Rational(3, 2), 14]',               # знак a
    'q8_1a': "'027'",                             # от востока
    'q8_1b_A': '19.1',                            # длина положения
    'q8_1b_B': '12.0',                            # то же
    'q8_1d_i': '(9, 4, 8)',                       # t₁ в r_B
    'q8_1d_ii': '30',                             # секунды
    'q8_2a': '26.9',                              # потерян множитель 4
    'q8_2b': '0.147',                             # радианы
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
