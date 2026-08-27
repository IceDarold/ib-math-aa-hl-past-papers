"""Следит за тем, чтобы в ноутбуках писали sin(x), а не sp.sin(x).

Запись ответа — часть задания. Если в одном практикуме ответ вводят как
`sp.sqrt(5)/2`, а в другом как `sqrt(5)/2`, студент тратит внимание на
синтаксис вместо математики. Проверяются и ячейки с кодом, и блоки ```python
в решениях: списывают чаще всего именно оттуда.

Единственное разрешённое `sp.` — строка версии в ячейке настройки: там `sp`
нужен как запасной выход к остальной sympy. Строка эта печатается на языке
ноутбука, поэтому в списке разрешённых её русский и английский варианты.

Запуск:  python practicum/tests/check_notation.py
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

ALLOWED = ("print('готово; sympy', sp.__version__)",
           "print('ready; sympy', sp.__version__)")

# P как имя pi: в E7 та же буква стоит в формулах за численность популяции,
# поэтому ищем её только в коде, а не в тексте
BANNED = [
    (re.compile(r'\bsp\.'), 'sp.', 'пишите sin(x), pi, sqrt(5) — они приходят из kit'),
    (re.compile(r'\bP\b'), 'P как pi', 'pi теперь есть под своим именем'),
    (re.compile(r'\bsympy\.'), 'sympy.', 'то же самое'),
]
FENCE = re.compile(r'```python\n(.*?)```', re.S)


def code_fragments(cell):
    """Куски настоящего кода из ячейки: сама ячейка или ```python в решении."""
    src = ''.join(cell['source'])
    if cell['cell_type'] == 'code':
        yield src
    else:
        yield from FENCE.findall(src)


def main():
    notebooks = sorted(glob.glob(os.path.join(ROOT, 'practicum/*/practicum-*.ipynb'))
                       + glob.glob(os.path.join(ROOT, 'practicum/*/archive-*.ipynb')))
    if not notebooks:
        sys.exit('ноутбуков не найдено')

    problems = []
    for path in notebooks:
        name = os.path.basename(path)
        nb = json.load(open(path))
        hits = 0
        for i, cell in enumerate(nb['cells']):
            for frag in code_fragments(cell):
                for line in frag.split('\n'):
                    if line.strip() in ALLOWED:
                        continue
                    for rx, what, hint in BANNED:
                        if rx.search(line):
                            hits += 1
                            problems.append(f'{name}, ячейка {i}: {what} — {hint}\n'
                                            f'    {line.strip()}')
        print(f'{"✅" if not hits else "❌"} {name}: {len(nb["cells"])} ячеек, '
              f'нарушений {hits}')

    if problems:
        print('\nнайдено:')
        for p in problems:
            print(' ', p)
        print(f'\nнарушений: {len(problems)}')
        return 1
    print('\nзапись ответов единообразна во всех практикумах')
    return 0


if __name__ == '__main__':
    sys.exit(main())
