"""Ищет разобранные в теории примеры, которые решают идущую следом задачу.

Практикум устроен так: блок теории, потом задача на тот же приём. Если
в теории разобран ровно тот пример, который задача просит решить, задача
перестаёт быть задачей — остаётся подставить числа. Поймать это глазами
трудно: теория пишется в LaTeX, задача проверяется выражением sympy, и
одно и то же выражение выглядит по-разному.

Тест смотрит на это с двух сторон.

**Сторона первая — ответ.** Каждое выражение, которое задача передаёт
проверке, и каждый эталон из ANSWERS переводятся в LaTeX; обе записи
очищаются от всего необязательного — пробелов, скобок группировки,
\\left и \\right, \\mathrm, tfrac против frac — и получившаяся строка
ищется в блоках теории, стоящих раньше по ноутбуку.

**Сторона вторая — условие.** Из теории и из условия задачи вынимаются
все формулы между долларами, приводятся к тому же виду и сравниваются
как строки, в обе стороны: длинная выкладка теории, внутри которой сидит
условие задачи, ловится так же, как короткая формула теории, стоящая
в длинном условии. Эта половина и находит случаи, где теория проводит
выкладку до числа, которого в аргументах проверки нет вовсе.

Условие самой задачи теорией не считается: там подынтегральное выражение
обязано стоять, на то оно и условие. Теорией считается блок, чей
заголовок начинается с Theory, Теория, Map of techniques или Карта
приёмов — заголовки в серии двуязычны, и знать надо оба написания,
иначе тест молча объявляет чистыми одиннадцать практикумов, которых
не читал.

Тренажёр распознавания из сравнения исключён: он нарочно повторяет
условия всех заданий подряд, и это его работа, а не утечка.

Чего тест не видит: пересказ своими словами и разбор, совпадающий
с задачей по числам, но не по записи. Поэтому зелёный прогон здесь —
необходимое условие, а не достаточное.

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
# Для формул, взятых прямо из текста, порог выше: в записи условия куда
# больше служебных символов, и короткий кусок совпадает случайно.
SHOWN_FLOOR = 18

THEORY = re.compile(r'^#+\s*(Theory|Теория|Map of techniques|Карта приёмов)', re.M)
TASK = re.compile(r'^#+\s*(Task|Задание)', re.M)
# Решения стоят после всех задач и повторяют теорию по определению.
DONE = re.compile(r'^#+\s*(Solutions?|Решения?|Ответы|🔑)', re.M)
DRILL = re.compile(r'(Trainer|Тренажёр)', re.I)
MATH = re.compile(r'\$\$(.+?)\$\$|\$([^$]+?)\$', re.S)

JUNK = ('\\mathrm', '\\displaystyle', '\\left', '\\right', '\\cdot',
        '\\quad', '\\qquad', '\\text', '\\,', '\;', '\\!', '\\:', '\\ ')


def flat(text):
    """Запись формулы без всего, что можно написать двумя способами."""
    text = text.replace('\\dfrac', '\\frac').replace('\\tfrac', '\\frac')
    for junk in JUNK:
        text = text.replace(junk, '')
    return re.sub(r'[\s{}]', '', text)


def written(expr):
    """Выражение так, как его напечатали бы в теории."""
    try:
        return flat(sp.latex(sp.sympify(expr)))
    except (sp.SympifyError, TypeError, ValueError, AttributeError,
            RecursionError, SyntaxError):
        return ''


def worked(short):
    """Разбор узнаётся по числам.

    Формула из одних букв — словарь темы: $H(t)=a\\sin(b(t-c))+d$ обязана
    стоять и в теории, и в условии, иначе про модель нечего сказать.
    Разобранный пример отличается тем, что в нём есть **конкретные
    числа** — и показатели степени тут не в счёт: $\\alpha^2+\\beta^2$ это
    по-прежнему общая запись, а $\\tfrac12 f(x)+1$ уже нет.
    """
    return any(ch.isdigit() for ch in re.sub(r'[\^_]\d+', '', short))


def formulas(text):
    """Формулы ячейки: нормализованная запись и то, как она напечатана."""
    out = []
    for match in MATH.finditer(text):
        raw = match.group(1) or match.group(2) or ''
        # Многострочная выкладка — это несколько утверждений подряд,
        # и совпасть с задачей может любое из них по отдельности.
        for part in re.split(r'\\\\|&=', raw):
            short = flat(part)
            if len(short) >= SHOWN_FLOOR and worked(short):
                out.append((short, ' '.join(part.split())[:88]))
    return out


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
    found, seen, theory, checked = [], '', [], 0
    mode = 'head'
    for cell in cells:
        source = ''.join(cell['source'])
        head = re.search(r'^#+\s*(.+)$', source, re.M)
        title = head.group(1)[:50] if head else ''
        if cell['cell_type'] == 'markdown':
            if DONE.search(source):
                mode = 'done'
            elif THEORY.search(source):
                mode = 'theory'
            elif TASK.search(source):
                mode = 'task'
            if mode == 'theory':
                seen += '\n' + flat(source)
                theory += formulas(source)
                continue
        if mode != 'task':
            continue
        if cell['cell_type'] == 'markdown':
            if DRILL.search(title):
                mode = 'done'
                continue
            asked = flat(source)
            mine = [short for short, _ in formulas(source)]
            for short, shown in theory:
                if short in asked or any(short in one for one in mine):
                    found.append((title, shown))
            continue
        wanted = list(pieces(source))
        for name in re.findall(r'^(\w+) = \.\.\.', source, re.M):
            if name in answers:
                wanted.append(answers[name])
        for raw in wanted:
            shown = written(raw)
            checked += 1
            if len(shown) >= FLOOR and shown in seen:
                found.append((title, raw))
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
        seen, unique = set(), []
        for where, what in found:
            if (where, what) not in seen:
                seen.add((where, what))
                unique.append((where, what))
        mark = '✅' if not unique else '❌'
        print(f'{mark} {name}: сверено выражений {checked}, '
              f'разобрано в теории заранее {len(unique)}')
        for where, what in unique:
            print(f'     {where}\n       {what}')
            problems.append(f'{name}: {what}')
    if problems:
        print(f'\nтеория решает задачу за ученика в {len(problems)} местах')
        return 1
    print('\nни один разбор в теории не решает соседнюю задачу')
    return 0


if __name__ == '__main__':
    sys.exit(main())
