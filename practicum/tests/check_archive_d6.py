"""Прогоняет архивный ноутбук D6 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_d5.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаются плотность и условия
вопроса: площадь, букву плотности, медиану, моду и моменты находит сама
проверка. Совпадение означает согласие markscheme с формулой, а не с моей
записью, — тридцать семь раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
площадь с другой стороны, десятичная дробь вместо точного значения,
корень вне промежутка, E(X²) за дисперсию, высота вершины за моду,
пересечение вместо условной, —
и проверка обязана сказать ❌. Сверх того считается, сколько ошибок названо
по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_d6.py
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

import build_archive_d6 as gen

# присваивания в ноутбуке выровнены по столбцу, поэтому пробелов
# вокруг «=» бывает больше одного
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Насколько ✅ в заполненном прогоне больше, чем ⬜ в пустом.
EXTRA = 0

# Типовая ошибка для каждого ответа. Выбраны те, что действительно
# делают: площадь с другой стороны, интеграл от нуля, корень вне
# промежутка, E(X²) за дисперсию, высота за моду, точное значение
# десятичной дробью, пересечение вместо условной.
BREAK = {
    'q1_1': '0.761',                 # площадь с другой стороны
    'q1_2': '0.565',                 # то же
    'q1_3': '0.896',                 # медленные бегуны
    'q1_4': '0.601',                 # 25x ≤ 48 для всех весов
    'q1_5': '0.594',                 # ниже 1.5, а не выше
    'q2_1a': '1/sqrt(16 + k) - 1/sqrt(k)',   # пределы наоборот
    'q2_1b': '0.65',                 # две значащие цифры
    'q2_2': '1.65',                  # десятичная дробь на Paper 1
    'q2_3': '1/(b*exp(b) - exp(b))', # потеряно значение на нижнем пределе
    'q2_4': '7*k**3/3',              # не та первообразная
    'q2_5a': '216*a + 36*b',         # f(9), а не площадь
    'q2_5b': '6*a + b',              # поделено раньше, чем спрашивают
    'q3_1a': '0.393',                # среднее вместо медианы
    'q3_1b': '0.25',                 # 2a вместо a
    'q3_2': 'a - sqrt((b - a)*(c - a)/2)',   # не отброшен корень
    'q3_3': '-1.68',                 # корень вне [0, 1]
    'q3_4': '2.55',                  # корень вне [0, 2k]
    'q3_5': '1.31',                  # интеграл от нуля
    'q3_6': '5.41',                  # верхний квартиль
    'q3_7': '33.6',                  # секунды, а не минуты
    'q4_1': '0.441',                 # высота вершины
    'q4_2a': '0.381',                # то же
    'q4_2b': "'mode'",               # не та сторона
    'q4_3_mode': '0.296',            # высота вершины
    'q4_3_median': '10.5',           # корень вне [3, 9]
    'q5_1a': '1',                    # ∫ f вместо ∫ x f
    'q5_1b': '(n + 1)/(n + 3)',      # E(X²) без вычитания
    'q5_2': '0.551',                 # десятичная дробь на Paper 1
    'q5_3': '1.02',                  # десятичная дробь вместо точного
    'q5_4a': '1',                    # ∫ f вместо ∫ x f
    'q5_4b': '13*a**2/3',            # E(X²) без вычитания
    'q5_5': '41.0',                  # не до цента
    'q5_6a': '0.254',                # ∫ x dx без плотности
    'q5_6b': '0.237',                # E(X²) без вычитания
    'q6_1': '0.0247',                # не поделено на условие
    'q6_2': '0.380',                 # площадь вне промежутка
    'q6_3': '0.0344',                # не поделено на условие
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
               'no valid model', 'no match', 'differ by')
    if any(not any(word in line for word in generic) for line in caught):
        named += 1
    else:
        print(f'  без имени: {name}: {caught[0]}')
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
