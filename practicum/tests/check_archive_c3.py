"""Прогоняет архивный ноутбук C3 целиком: пустым и с эталонными ответами.

Устроен так же, как check_archive_b4.py, и по той же причине: в архивном
ноутбуке нет ни одного разбора, который проверялся бы отдельно, — вся его
правильность в том, что ответ из раздела Solutions проходит проверку
в ячейке. Тест берёт сам ноутбук, подставляет в каждый placeholder эталон
из ANSWERS генератора и требует, чтобы каждая проверка сказала ✅.

Заодно проверяется главное свойство формата: пустой ноутбук проходится
сверху вниз без единого исключения и печатает ⬜. Без этого его нельзя
залить на Kaggle, где ячейки исполняются автоматически.

Эталоны в ANSWERS взяты из markschemes; сами проверки эталонов не хранят
(кроме восьми хешей, где ответ округлён до трёх значащих цифр и подставить
его некуда), так что совпадение здесь означает согласие markscheme с самим
уравнением.

Запуск:  python practicum/tests/check_archive_c3.py
"""
import contextlib
import io
import json
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))

import build_archive_c3 as gen

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
# первая ячейка — установочная: import из practicum/geometry
os.chdir(os.path.join(ROOT, 'practicum', 'geometry'))
plt.show = lambda *a, **k: plt.close('all')

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
t(f'проверок прошло столько же, сколько было пустых ({blanks})',
  answered.count('✅') == blanks)

print(f'\n{passed}/{passed + failed}')
sys.exit(1 if failed else 0)
