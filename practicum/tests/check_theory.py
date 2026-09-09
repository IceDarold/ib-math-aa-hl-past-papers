"""Ищет разобранные в теории примеры, которые решают идущую следом задачу.

Практикум устроен так: блок теории, потом задача на тот же приём. Если
в теории разобран ровно тот пример, который задача просит решить, задача
перестаёт быть задачей — остаётся подставить числа. Поймать это глазами
трудно: теория пишется в LaTeX, задача проверяется выражением sympy, и
одно и то же выражение выглядит по-разному.

Тест сводит их к одному виду. Каждое выражение, которое задача передаёт
проверке, и каждый эталонный ответ из ANSWERS переводятся в LaTeX, обе
записи очищаются от всего необязательного — пробелов, скобок группировки,
\\left и \\right, \\mathrm, tfrac против frac, — и получившаяся строка ищется
в тексте блоков теории, идущих раньше по ноутбуку.

Условие самой задачи при этом не считается теорией: там подынтегральное
выражение обязано стоять, на то оно и условие. Теорией считается блок,
чей заголовок начинается с Theory или Map of techniques.

Образец правильного блока — Theory 6 в E5: формула понижения разобрана
для косинуса, а задача просит построить её для синуса. Тот же приём,
другая функция.

Запуск:  python practicum/tests/check_theory.py
"""
import ast
import glob
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))

import sympy as sp

# Короткие выражения совпадают у всех и ни о чём не говорят: x^2 стоит
# в каждом втором абзаце. Порог подобран так, чтобы ловить дробь целиком
# и не ловить одночлен.
FLOOR = 14

THEORY = re.compile(r'^#+\s*(Theory|Map of techniques)', re.M)


def flat(text):
    """Запись формулы без всего, что можно написать двумя способами."""
    text = text.replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac')
    text = text.replace('\\mathrm', '').replace('\\displaystyle', '')
    text = text.replace('\\left', '').replace('\\right', '')
    text = re.sub(r'\\[,;!:]', '', text)
    return re.sub(r'[\s{}]', '', text)


def written(expr):
    """Выражение так, как его напечатали бы в теории."""
    try:
        return flat(sp.latex(sp.sympify(expr)))
    except (sp.SympifyError, TypeError, ValueError, AttributeError,
            RecursionError, SyntaxError):
        return ''


def pieces(source):
    """Все выражения, которые ячейка передаёт проверкам."""
    out = []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return out
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, 'id', '') or getattr(node.func, 'attr', '')
        if not name.startswith(('verify_', 'check_')):
            continue
        for arg in node.args[1:] + [kw.value for kw in node.keywords]:
            text = ast.get_source_segment(source, arg)
            if text and not text.startswith('...'):
                out.append(text)
    return out


def notebook_of(gen):
    """Путь к ноутбуку: имя поля у генераторов серии разное."""
    for name in dir(gen):
        value = getattr(gen, name)
        if isinstance(value, str) and value.endswith('.ipynb'):
            return value
    # У части генераторов путь собирается внутри функции и наружу не торчит.
    # Тогда имя файла берётся из исходника, а сам файл ищется по репозиторию.
    source = open(gen.__file__).read()
    for base in re.findall(r"'([\w-]+\.ipynb)'", source):
        found = glob.glob(os.path.join(ROOT, 'practicum', '*', base))
        if found:
            return found[0]
    return None


def leaks(module_name):
    """Совпадения «разобрано в теории — спрошено в задаче» для одного практикума."""
    gen = importlib.import_module(module_name)
    path = notebook_of(gen)
    if path is None:
        return None, 0
    # ANSWERS есть не у всех: у ранних практикумов эталоны лежат в самом
    # ноутбуке. Выражения, которые задача передаёт проверке, есть везде,
    # и их одних уже хватает, чтобы поймать разобранный заранее пример.
    answers = getattr(gen, 'ANSWERS', {})
    with open(path) as fh:
        cells = json.load(fh)['cells']
    found, seen_theory, checked = [], '', 0
    for cell in cells:
        source = ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            if THEORY.search(source):
                seen_theory += '\n' + flat(source)
            continue
        wanted = list(pieces(source))
        for name in re.findall(r'^(\w+) = \.\.\.', source, re.M):
            if name in answers:
                wanted.append(answers[name])
        for raw in wanted:
            shown = written(raw)
            checked += 1
            if len(shown) >= FLOOR and shown in seen_theory:
                found.append((raw, shown))
    return found, checked


def main():
    problems = []
    names = sorted(os.path.basename(p)[:-3]
                   for p in glob.glob(os.path.join(ROOT, 'practicum/generators',
                                                   'build_[a-z][0-9].py')))
    for name in names:
        found, checked = leaks(name)
        if found is None:
            print(f'—  {name}: пропущен, ноутбук не найден')
            continue
        mark = '✅' if not found else '❌'
        print(f'{mark} {name}: сверено выражений {checked}, '
              f'разобрано в теории заранее {len(found)}')
        for raw, shown in found:
            print(f'     {raw}')
            print(f'     как {shown[:90]}')
            problems.append(f'{name}: {raw}')
    if problems:
        print(f'\nтеория решает задачу за ученика в {len(problems)} местах')
        return 1
    print('\nни один разбор в теории не решает соседнюю задачу')
    return 0


if __name__ == '__main__':
    sys.exit(main())
