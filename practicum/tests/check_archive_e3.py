"""Прогоняет архивный ноутбук E3 целиком: пустым и с эталонными ответами.

Устроен так же, как check_archive_e1.py и check_archive_e2.py, и по той же
причине: в архивном ноутбуке нет ни одного разбора, который проверялся бы
отдельно, — вся его правильность в том, что ответ из раздела Solutions
проходит проверку в ячейке. Тест берёт сам ноутбук, подставляет в каждый
placeholder эталон из ANSWERS генератора и требует, чтобы каждая проверка
сказала ✅.

Заодно проверяется главное свойство формата: пустой ноутбук проходится
сверху вниз без единого исключения и печатает ⬜. Без этого его нельзя
залить на Kaggle, где ячейки исполняются автоматически.

Эталоны в ANSWERS взяты из markschemes. Записанный эталон здесь всего
в трёх местах из пятидесяти пяти: хеш набора корней в 9.1, 2|a| в 8.3
и 1/r в 7.6. Остальные проверки эталона не хранят — verify_derivative
дифференцирует функцию из условия, verify_stationary сканирует производную
по отрезку, verify_constants подставляет числа в условия вопроса,
verify_param_set опрашивает неравенство в пробных точках. Для них
совпадение здесь означает согласие markscheme с самой задачей,
а не с моей записью.

Запуск:  python practicum/tests/check_archive_e3.py
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

import build_archive_e3 as gen

PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

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


def filled(source):
    """Ячейка с подставленными эталонными ответами."""
    out = []
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            if name not in gen.ANSWERS:
                raise AssertionError(f'нет эталона для {name}')
            out.append(f'{name} = {gen.ANSWERS[name]}')
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
t(f'в пустом прогоне {blanks} незаполненных ответов', blanks > 20)

print('--- ноутбук с эталонными ответами ---')
answered = run([filled(source) for source in cells])
bad = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad:
    print('  ' + line)
t('ни одна проверка не провалилась', not bad)
t('пустых ответов не осталось', '⬜' not in answered)
t(f'проверок прошло столько же, сколько было пустых ({blanks})',
  answered.count('✅') == blanks)

print(f'\n{blanks} ⬜ пустых, {answered.count("✅")} ✅ отвеченных, '
      f'{len(bad)} ❌')
print(f'{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
