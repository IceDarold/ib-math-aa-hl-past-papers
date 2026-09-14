"""Проверяет устройство пакета kit: модули, импорты между ними, склейку для Kaggle.

kit разложен по темам на модули, но снаружи остаётся одним набором:
ноутбук пишет `from kit import *`, тренажёр зовёт `kit._curve_roots`, а на
Kaggle make_kaggle.py склеивает модули обратно в одну ячейку. Всё это
держится на нескольких правилах, и нарушение каждого видно не сразу:

- модуль, не вписанный в MODULES, в ноутбуке работает (его импортирует
  сосед), а в склейке для Kaggle его нет;
- одно имя в двух модулях в пакете разрешается одним способом, а в склейке,
  где выигрывает последнее определение, — другим;
- импорт имени из модуля дальше по списку в шапке файла ломает импорт, а
  в склейке ломает порядок определений.

Запуск:  python practicum/tests/test_kit_package.py
"""
import ast
import io
import os
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import kit
import make_kaggle

ok, bad = [], []


def check(name, got, expect=True):
    (ok if got == expect else bad).append(name)
    if got != expect:
        print(f'  ПРОВАЛ {name}')


FOLDER = os.path.join(ROOT, 'practicum', 'kit')
order = [module.__name__.split('.')[-1] for module in kit.MODULES]
files = sorted(name[:-3] for name in os.listdir(FOLDER)
               if name.endswith('.py') and name != '__init__.py')

print('=== модули ===')
check('every-file-in-MODULES', sorted(order) == files)
check('core-first', order[0] == 'core')

print('=== имена ===')
owner = {}
for module in order:
    tree = ast.parse(open(os.path.join(FOLDER, module + '.py')).read())
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            defined = [node.name]
        elif isinstance(node, ast.Assign):
            defined = [n.id for target in node.targets for n in ast.walk(target)
                       if isinstance(n, ast.Name)]
        else:
            continue
        for name in defined:
            if owner.setdefault(name, module) != module:
                print(f'  {name}: {owner[name]} и {module}')
                check(f'one-home-{name}', False)
check('names-found', len(owner) > 300)
# Всё, что определено в модулях, видно снаружи — с подчёркиванием и без.
check('all-reachable', all(hasattr(kit, name) for name in owner))
check('star-is-public', all(not name.startswith('_') for name in kit.__all__))
check('no-submodule-in-star', not set(order) & set(kit.__all__))

print('=== импорты между модулями ===')
for module in order:
    source = open(os.path.join(FOLDER, module + '.py')).read()
    body = ast.parse(source).body
    last_definition = max(node.lineno for node in body
                          if isinstance(node, (ast.FunctionDef, ast.ClassDef)))
    for node in body:
        if not (isinstance(node, ast.ImportFrom) and node.level == 1):
            continue
        here, there = order.index(module), order.index(node.module)
        names = [alias.name for alias in node.names]
        if node.lineno < last_definition:
            # В шапке — только модули раньше этого.
            check(f'{module}: {node.module} в шапке раньше по списку', there < here)
        else:
            # В конце — только ссылки вперёд.
            check(f'{module}: {node.module} в конце дальше по списку', there > here)
        if names != ['*']:
            check(f'{module}: {node.module} даёт свои имена',
                  all(owner.get(name) == node.module for name in names))
        else:
            check(f'{module}: звёздочка только из core', node.module == 'core')

print('=== склейка для Kaggle ===')
glued = make_kaggle.glued_kit()
check('glued-has-no-relative-import', 'from .' not in glued)
space = {}
exec(compile(make_kaggle.compact(glued), '<kaggle>', 'exec'), space)
check('glued-same-public', {n for n in space if not n.startswith('_')} == set(kit.__all__))
check('glued-same-private', all(name in space for name in owner))
check('glued-fits-kaggle', len(make_kaggle.compact(glued).encode()) < 900_000)
# Склейка — живой набор, а не только имена: вероятность под плотностью.
X = space['Density']({(0, 2): 3 * space['x'] ** 2 / 8}, 'X')
with redirect_stdout(io.StringIO()):
    check('glued-accepts', space['verify_chance']('p', 0.125, space['P'](X < 1)))
    check('glued-rejects', space['verify_chance']('p', 0.25, space['P'](X < 1)), False)

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
