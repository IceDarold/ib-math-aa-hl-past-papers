"""Прогоняет архивный ноутбук E7 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_e9.py: вся правильность архивного
ноутбука в том, что ответ из раздела Solutions проходит проверку в ячейке.
Тест подставляет в каждый placeholder эталон из ANSWERS генератора и
требует, чтобы каждая проверка сказала ✅.

Эталоны взяты из markschemes, а проверкам передаётся сама модель вопроса —
уравнение и начальное условие, больше ничего. Явное решение подставляется в
уравнение, неявное проходится ногами по кривой, значение в точке берётся
счётом по полю, ломаная Эйлера строится заново тем же шагом. Совпадение
означает согласие markscheme с полем наклонов, а не с моей записью, —
шестьдесят девять раз подряд.

Проверок ровно столько же, сколько ответов, и EXTRA равен нулю.

Третий прогон: каждый ответ по очереди заменяется типовой ошибкой —
потерянная постоянная интегрирования; знак в показателе; точное значение
вместо приближения Эйлера и наоборот; шаг недосчитан; множитель
перевёрнут; вогнутость наоборот, — и проверка обязана сказать ❌. Сверх
того считается, сколько ошибок названо по имени, а не просто отвергнуто.

Запуск:  python practicum/tests/check_archive_e7.py
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

import build_archive_e7 as gen

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
    'q1_1': 'sin(x - pi/4)',                 # постоянная интегрирования потеряна
    'q1_2': '6780000',                       # начальное значение, а не значение в 2026
    'q2_1': 'exp(-t) - 1',                   # v0 потеряна по дороге
    'q2_2': '4 + 2*exp(-x/10)',              # знак постоянной
    'q2_3': 'Eq(x**2 - y**2, k)',            # знак: это ортогональная к своей же
    'q2_4a': '4',                            # знак
    'q2_4b': '4 - pi',                       # знак
    'q2_5a': '200',                          # сама величина, а не её скорость
    'q2_5b': "'c'",                          # «предел» вместо «равновесия»
    'q2_5c': '200*exp(-A*exp(a*t))',         # знак в показателе
    'q2_5d': 'log(160)',                     # 200 - 40 вместо 200/40
    'q2_5e': '0.427',                        # не поделено на 5 шагов
    'q2_5f': '100',                          # округление вниз вместо ближайшего
    'q3_1a': '1200*k/((k - 1200)*exp(t/5) + 1200)',   # знак в показателе
    'q3_1b': '2850',                         # три значащих цифры вместо четырёх
    'q3_2a': 'Eq(k*t, log(pop*(N - pop)/(P0*(N - P0))))',  # дроби перепутаны
    'q3_2b': 'log(9)/5',                     # ln 9 не поделён надвое
    'q3_3a': '(8*x + x**4)/(4 + x**3)',      # знак в знаменателе
    'q3_3b': '10.7',                         # приближение Эйлера вместо точного
    'q3_3c': "'c'",                          # вогнутость вместо асимптоты
    'q3_4a': '3*exp(x + 2*atan(x))',         # знак у арктангенса
    'q3_4b': '2.58046',                      # Эйлер вместо точного
    'q4_1': 'v**2 - 2',                      # слагаемое v потеряно
    'q4_2a': 'Eq(y**2, 4*x**2*(1 + log(x)))',  # знак логарифма
    'q4_2b': '[sqrt(2)]',                    # один наклон из двух
    'q4_3a': 'x*sqrt((9*x**4 + 1)/2)',       # знак постоянной
    'q4_3b': '2.65',                         # Эйлер вместо точного
    'q4_3c': 'sqrt(3)',                      # отношение перевёрнуто
    'q4_4a': '(y + x)/(y - x)',              # дробь перевёрнута
    'q4_4b': 'Eq(log(1 + (y/x)**2)/2 + atan(y/x) - log(x), D)',   # знак ln|x|
    'q4_5': 'Eq(x**2 + 2*x*y - y**2, 4)',    # знак среднего слагаемого
    'q4_6a': 'Eq(x**2, A*(x - y)/(x + y))',  # дробь перевёрнута
    'q4_6b': 'x*(A - x**2)/(x**2 + A)',      # знак числителя
    'q4_7': 'Eq(x**6*(2*y - x)**3, 2*(x - 2*y))',   # знак справа
    'q5_1': 'log(2*x)/x - 1/x',              # постоянная потеряна
    'q5_2': '3*exp(x) + x + 1',              # знаки после деления на множитель
    'q5_3a': 'sqrt(tan(x))',                 # множитель перевёрнут
    'q5_3b': 'x*sqrt(cot(x))',               # то же в решении
    'q5_3c': '1.98',                         # Эйлер вместо точного
    'q5_3d': "'a'",                          # слова без ссылки на знаки слагаемых
    'q5_4': 'x**2 - 2*x - 3',                # постоянная потеряна: частное решение
    'q5_5': '(pi - x*cot(x) + log(sin(x)))/x**2',   # множитель x**2 вместо x**3
    'q6_1': '27.3',                          # точное значение вместо ломаной
    'q6_2': '2.58786',                       # точное значение
    'q6_3': '2.71',                          # точное значение
    'q6_4a': '2.079',                        # шагов на один меньше
    'q6_4b': '0.00479',                      # запятая на разряд не там
    'q6_5': '2.53',                          # точное значение
    'q6_6': '1.12',                          # точное значение
    'q6_7a': '101',                          # Гомперц без эмиграции
    'q6_7b': "'d'",                          # Эйлер объявлен точным
    'q6_8a': '1.7',                          # знак
    'q6_8b': '1.20',                         # точное значение
    'q7_1': "'down'",                        # вогнутость наоборот
    'q7_2': "'down'",                        # то же
    'q7_3a': "'d'",                          # придуманная особенность
    'q7_3b': "'down'",                       # вогнутость наоборот
    'q7_4a': "'under'",                      # знак ошибки наоборот
    'q7_4b': "'a'",                          # «округляет вверх» вместо наклона
    'q7_5': "'down'",                        # вогнутость наоборот
    'q8_1': 'exp(t)',                        # постоянная потеряна
    'q8_2': '-A*t*exp(t)',                   # вторая постоянная потеряна
    'q8_3': '(0, 2)',                        # коэффициенты перепутаны
    'q8_4': 'exp(2*t)',                      # постоянная потеряна
    'q8_5': 'B*exp(2*t)/2',                  # постоянная потеряна
    'q8_6': 'B*exp(2*t)/2 + C',              # знак
    'q8_7': '(3, 2)',                        # коэффициенты перепутаны
    'q8_8': '[3]',                           # один показатель из двух
    'q8_9': 'F*exp(3*t)',                    # вторая постоянная потеряна
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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 69)

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

# Отвергнуть мало — промах надо назвать. Безымянными считаются только эти
# ответы проверок: «не то» и «проверить не удалось». Шесть ответов темы —
# выбор формулировки, и про неверную букву сказать действительно нечего.
generic = ('no match', 'not this one', 'not what the equation turns into',
           'cannot be checked')
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
