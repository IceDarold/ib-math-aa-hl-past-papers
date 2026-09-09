"""Прогоняет архивный ноутбук E5 целиком: пустым, с эталонами и с ошибками.

Устроен так же, как check_archive_a1.py и check_archive_e4.py, и по той же
причине: в архивном ноутбуке нет ни одного разбора, который проверялся бы
отдельно, — вся его правильность в том, что ответ из раздела Solutions
проходит проверку в ячейке.

Три прогона, и каждый ловит своё.

Пустой. Ноутбук обязан пройтись сверху вниз без единого исключения
и напечатать ⬜ на каждую проверку. Без этого его нельзя залить на Kaggle,
где ячейки исполняются при заливке.

С эталонами. Каждый ответ подставляется из ANSWERS генератора, и каждая
проверка обязана сказать ✅.

С ошибками. Каждый ответ по очереди портится типовым промахом темы —
потерянный делитель замены, знак у второго слагаемого по частям, логарифм
там, где нужна обратная величина, — и проверка обязана сказать ❌. Без этого
прогона проверка вида «всегда ✅» прошла бы тест незамеченной.

Эталонов в ANSWERS два из сорока шести: 8.3a и 8.3b, где функция задана
только графиком и подынтегрального выражения нет вовсе. Остальные проверки
эталона не хранят — они дифференцируют написанное и сравнивают с условием, —
и для них совпадение здесь означает согласие markscheme с самой задачей,
а не с моей записью.

Запуск:  python practicum/tests/check_archive_e5.py
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

import build_archive_e5 as gen

PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

# Мест для ответа 46, проверок столько же: каждая ячейка сдаёт свой ответ
# в свою проверку, и на один незаполненный ответ приходится ровно один ⬜.
EXTRA = 0

# Типовой промах на каждый ответ. Все они из markschemes и из разборов:
# это не случайные выражения, а то, чем тема ошибается.
BREAK = {
    'q1_1a': '3*x - 5*sqrt(x)',                 # не поделено на новый показатель
    'q1_1b': '-4',                              # пределы переставлены
    'q1_2': 'Rational(4, 21)',                  # забыта ширина отрезка
    'q1_3': 'x**3 + 5*exp(x) + C',              # постоянная не найдена
    'q1_4': 'x**3 + 6*x**2 - 15*x',             # постоянная взята нулём
    'q1_5': 'log(x*(k - x))/k',                 # знак второго логарифма
    'q2_1a': 'u**n',                            # множитель замены не учтён
    'q2_1b': '(2**n - 1)/(n - 1)',              # делитель не тот
    'q2_2': '3*log(1 + x**2)',                  # точка не подставлена
    'q2_3a': 'cos(t)',                          # dx заменено на dt без 2t
    'q2_3b': '2*t*sin(t) - 2*cos(t)',           # знак второго слагаемого
    'q3_1': 'x**2*log(x)**2/2 - x**2*log(x)/2',  # хвост второго шага потерян
    'q3_2': '2*log(2)**2 - 2*log(2) + 1',       # нижний предел не вычтен
    'q3_3': '(x**2 - 2*x + 3)*exp(x)',          # знак свободного члена
    'q3_4': 'x*acos(x) + sqrt(1 - x**2)',       # знак остаточного интеграла
    'q3_5': 'x*atan(x) + log(1 + x**2)/2',      # тот же знак
    'q3_6a': '-t*exp(-3*t)/3 - exp(-3*t)/3',    # делитель второго слагаемого
    'q3_6b': '3',                               # k подобрано на глаз
    'q3_7': '-x*exp(-x)',                       # второй шаг по частям забыт
    'q3_8': '0',                                # предел взят наугад
    'q3_9': '4',                                # спутано n! и n
    'q3_10': '25',                              # просто неверно
    'q4_1a': 'u/(u**2 - u - 2)*cos(x)',         # множитель замены оставлен
    'q4_1b': 'u/((u + 1)*(u - 2))',             # знаменатель не разнесён
    'q4_1c': 'log(Abs(sin(x) + 1))/3 - 2*log(Abs(sin(x) - 2))/3',  # знак
    'q4_2a': '(2*x - 15)/((x + 3)*(x - 4))',    # дробь не разложена
    'q4_2b': 'log(32)/5',                       # логарифм перевёрнут
    'q4_3a': '4/(2*x + 1) - 2/(x + 1)',         # кратному множителю одна дробь
    'q4_3b': '2*log(Abs(2*x + 1)) - 2*log(Abs(x + 1)) - log(Abs(x + 1))',
                                                # логарифм вместо обратной
    'q4_4': 'log(Abs((1 + v)/(1 - v)))/2 + log(A)/2 + v',   # лишнее слагаемое
    'q5_1': '2*log(Abs(x - 2))',                # знак производной степени −2
    'q5_2': 'exp(x + x**2)',                    # интеграл x+1 взят как x+x²
    'q5_3': 'exp(x/2)*sin(x)',                  # корень потерян
    'q6_1': 'cos(x)**(n - 1)*sin(x) + (n - 1)*J(n - 2) + (n - 1)*J(n)',  # знак
    'q6_2': 'cos(x)**(n - 1)*sin(x)/n + (n - 1)*J(n - 2)',   # не поделено на n
    'q6_3': 'cos(x)**3*sin(x)/4 + 3*cos(x)*sin(x)/8',        # член 3x/8 потерян
    'q7_1a': 'E - 2*x**2',                      # множитель e потерян
    'q7_1b': '5*E/12 + E/100',                  # арифметика при подстановке
    'q7_2': '1 - x**2 + x**4 - x**6',           # сдан ряд, а не его интеграл
    'q7_3': 'x + x**3/6 + 3*x**5/40 + x**7/112',   # больше заказанного
    'q7_4': '1',                                # k подобрано на глаз
    'q7_5': '0.158',                            # три знака вместо шести
    'q8_1': '2',                                # решено до c², а не до c
    'q8_2': '0.713',                            # три значащие цифры из шести
    'q8_3a': '1.6',                             # у нечётной функции взят модуль
    'q8_3b': '1.6',                             # чётная часть не удвоена
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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks > 30)

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
    if any('is not the integrand' not in line and 'no match' not in line
           for line in caught):
        named += 1
print(f'из {len(BREAK)} ошибок названы по имени {named}')

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
