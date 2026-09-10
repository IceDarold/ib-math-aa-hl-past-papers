#!/usr/bin/env python3
"""Показывает числа, которые стоят и в теории, и в решении задачи.

Это **не** тест: он ничего не проваливает и не может. Это лупа к
`check_theory.py`, и нужна она потому, что у того есть слепое пятно.

`check_theory.py` сравнивает **формулы**. Но самый неприятный вид утечки
формулы не содержит вовсе: теория ведёт разбор словами и доводит его
до числа — «$2\\times{}^8P_4=3360$ … итого 10080», — а условие задачи
сформулировано текстом, и совпадать в нём нечему. Так в D1 теория
напечатала ответы четырёх заданий подряд, и формульная проверка была
при этом зелёной.

Скрипт берёт все числа длиной от трёх знаков из блоков теории и все
числа из блоков решений того же ноутбука и печатает пересечение.

**Читать глазами обязательно.** Совпадение числа — повод посмотреть,
а не приговор: $720$ это и ответ задачи, и просто $6!$; $180$ — это
градусы; $256$ в тренажёре стоит по делу. Смотреть надо на то, **чем
число является в теории**: если это результат доведённой до конца
выкладки, а в решении — ответ, то это утечка. Если это сумма углов
треугольника, номер сессии или размер выборки из условия — нет.

Запуск:  python practicum/tests/find_theory_numbers.py [A4 ...]
"""
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

THEORY = re.compile(r'^#+\s*(Theory|Теория|Map of techniques|Карта приёмов)', re.M)
TASK = re.compile(r'^#+\s*(Task|Задание)', re.M)
DONE = re.compile(r'^#+\s*(Solutions?|Решения?|Ответы|🔑)', re.M)
NUM = re.compile(r'\d[\d\s,\\]*\.?\d*')
YEAR = re.compile(r'^(19|20)\d\d$')
FLOOR = 3


def numbers(text):
    """Числа ячейки без разделителей разрядов; годы отброшены."""
    found = set()
    for match in NUM.finditer(text):
        raw = re.sub(r'[\s,\\]', '', match.group(0)).rstrip('.')
        if len(raw.replace('.', '')) >= FLOOR and not YEAR.match(raw):
            found.add(raw)
    return found


def shared(path):
    """Числа, встреченные и в теории, и в решениях: (число, ячейка теории)."""
    cells = json.load(open(path))['cells']
    mode, theory, solved = 'head', {}, set()
    for i, cell in enumerate(cells):
        source = ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            if DONE.search(source):
                mode = 'solution'
            elif THEORY.search(source):
                mode = 'theory'
            elif TASK.search(source):
                mode = 'task'
        if mode == 'theory' and cell['cell_type'] == 'markdown':
            for value in numbers(source):
                theory.setdefault(value, i)
        elif mode == 'solution':
            solved |= numbers(source)
    both = set(theory) & solved
    return sorted(((value, theory[value]) for value in both),
                  key=lambda pair: (-len(pair[0]), pair[0]))


def main():
    wanted = {name.lower() for name in sys.argv[1:]}
    paths = sorted(glob.glob(os.path.join(ROOT, 'practicum/*/practicum-*.ipynb')))
    total = 0
    for path in paths:
        code = os.path.basename(path)[10:12]
        if wanted and code not in wanted:
            continue
        rows = shared(path)
        total += len(rows)
        if rows:
            print(f'{os.path.basename(path)[:-6]}:')
            for value, cell in rows:
                print(f'    {value:>12}   теория[{cell}]')
    print(f'\nсовпадений: {total} — каждое надо посмотреть глазами, '
          f'см. заголовок файла')
    return 0


if __name__ == '__main__':
    sys.exit(main())
