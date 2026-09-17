"""Прогоняет архивный ноутбук C7 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_c6.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются фигуры вопроса:
треугольник, параллелограмм, пирамида, пара прямых, пара плоскостей.
Площадь, объём, угол, дугу и расстояние проверка меряет сама, а ближайшую
точку находит из условий. Совпадение означает согласие markscheme с
фигурами вопроса, а не с моей записью, — двадцать шесть раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
перестановка множителей, знак средней компоненты, забытая половина у
треугольника и забытая треть у пирамиды, тупой угол между нормалями,
угол вместо дуги, расстояние без деления на длину направления, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_c7.py
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

import build_archive_c7 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: перестановка множителей и знак средней компоненты, забытая
# половина у треугольника и забытая треть у пирамиды, |u||v| вместо
# |u × v|, тупой угол между нормалями, угол с нормалью вместо угла с
# плоскостью, центральный угол вместо дуги, расстояние без деления на
# длину направления.
BREAK = {
    'q1_1': 'vec(2 - 3*p, 2 + p, p**2 - 2*p)',           # знак средней компоненты
    'q1_2': 'vec(0, 36, 0)',                             # p × a
    'q2_1a': '0.326',                                    # значение p вместо величины
    'q2_1b': '2.60',                                     # половина забыта
    'q2_2a': '-12',                                      # знак m
    'q2_2b': '6*sqrt(3)',                                # взят треугольник
    'q2_3': '137.7',                                     # половина забыта
    'q2_4': '[vec(1, -2, 1), vec(-1, 2, -1)]',           # длина не подобрана
    'q3_1': '1053',                                      # треть забыта
    'q4_1a': 'A**2*B**2*cos(th)**2',                     # синус и косинус местами
    'q4_1b': 'A**2*B**2*sin(th)**2',                     # синус и косинус местами
    'q4_2': 'U*V*cos(th)**2 + U*V*sin(th)**2',           # длины не возведены в квадрат
    'q4_3a': 'sqrt(6)',                                  # площадь не удвоена
    'q4_3b': '3',                                        # корень не извлечён
    'q4_3c': '[[1, Rational(4, 5)], [Rational(7, 5), 2]]',   # пары перепутаны
    'q5_1': '120',                                       # тупой угол между нормалями
    'q5_2': '-Rational(1, 5)',                           # знак: острый угол
    'q5_3': '0.639',                                     # угол с нормалью
    'q5_4': '0',                                         # угол не тот
    'q5_5': '1.84',                                      # центральный угол вместо дуги
    'q5_6': '150.9',                                     # смежный угол
    'q6_1a': '-10 - 30*mu',                              # PN взят как OP − ON
    'q6_1b': '(Rational(11, 3), Rational(-14, 3), Rational(5, 3))',   # знак μ
    'q6_2': 'Rational(4, 3)',                            # параметр вместо точки
    'q7_1': 'sqrt(108)',                                 # не поделено на |v|
    'q7_2': 'sqrt(54)',                                  # не поделено на |v|
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
               'nothing satisfies', 'is not u × v', 'does not measure that',
               'with numbers this gives')
    if any(not any(word in line for word in generic) for line in caught):
        named += 1
    else:
        print(f'  без имени: {name}: {caught[0]}')
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
