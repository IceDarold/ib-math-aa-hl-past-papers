#!/usr/bin/env python3
"""Собирает и публикует Kaggle-версии практикумов.

На Kaggle ноутбук лежит один, соседних файлов рядом нет, поэтому
`from kit import *` там не работает. Скрипт склеивает модули пакета kit
в одну ячейку настройки и кладёт рядом kernel-metadata.json.

Источник правды — practicum/map.yaml: у готового практикума есть поля
`notebook` и `kaggle`, и публиковать можно по идентификатору, не помня путей.

    python practicum/make_kaggle.py C3 --push        # один практикум
    python practicum/make_kaggle.py B4:archive       # архивный ноутбук темы
    python practicum/make_kaggle.py --all --push     # все со status: ready
    python practicum/make_kaggle.py C3               # только собрать, не заливать

Ноутбуки помечаются приватными: задания содержат условия из past papers IB,
и сам репозиторий приватный по той же причине. Публиковать открыто —
осознанное решение, флаг --public.

Нужен токен Kaggle. У нового формата (строка вида KGA...) это файл
~/.kaggle/access_token или переменная KAGGLE_API_TOKEN; старый формат
username+key в ~/.kaggle/kaggle.json свежий CLI уже не принимает.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import warnings

import nbformat

try:
    import yaml
except ImportError:
    sys.exit("нужен pyyaml: pip install pyyaml")

warnings.simplefilter('ignore')

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_URL = 'https://github.com/IceDarold/ib-math-aa-hl-past-papers'
DEFAULT_USER = 'artemkonukhov'


def load_map():
    with open(os.path.join(ROOT, 'practicum/map.yaml')) as fh:
        cmap = yaml.safe_load(fh)
    out = {}
    for sec in cmap['sections'].values():
        for p in sec['practicums']:
            out[p['id']] = p
    return out


def glued_kit():
    """Пакет kit одним текстом: модули в порядке kit.MODULES, без импортов между ними.

    В одном пространстве имён импорты `from .core import ...` не нужны, а
    ссылки вперёд между модулями статистики разрешаются сами: имена зовутся
    только изнутри функций, к моменту вызова все они уже определены. Порядок
    берётся из __init__.py разбором, без импорта: sympy здесь не нужен.
    """
    import ast
    folder = os.path.join(ROOT, 'practicum/kit')
    init = ast.parse(open(os.path.join(folder, '__init__.py')).read())
    order = next([name.id for name in node.value.elts] for node in init.body
                 if isinstance(node, ast.Assign) and node.targets[0].id == 'MODULES')
    parts = []
    for module in order:
        source = open(os.path.join(folder, module + '.py')).read()
        lines = source.splitlines(keepends=True)
        body, drop = ast.parse(source).body, set()
        for node in body:
            local = isinstance(node, ast.ImportFrom) and node.level == 1
            doc = (node is body[0] and isinstance(node, ast.Expr)
                   and isinstance(node.value, ast.Constant))
            if local or doc:
                drop.update(range(node.lineno, node.end_lineno + 1))
        parts.append(''.join(line for number, line in enumerate(lines, start=1)
                             if number not in drop).strip('\n') + '\n')
    return '\n\n'.join(parts)


def compact(source):
    """Код kit без комментариев и docstring-ов — для ячейки Kaggle.

    Kaggle не принимает ноутбук больше мегабайта, а kit с секцией плотности
    (D6) его перерос. Код не переписывается: удаляются только комментарии, а
    docstring заменяется пустой строкой, так что синтаксис остаётся тем же,
    что в репозитории, и не зависит от версии Python на Kaggle. Пустые строки
    убираются, кроме тех, что внутри многострочных строковых литералов.
    """
    import io
    import tokenize
    lines = source.splitlines(keepends=True)
    cuts, keep_lines = [], set()
    previous = tokenize.NEWLINE
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        kind, _, start, end, _ = token
        if kind == tokenize.COMMENT:
            cuts.append((start, end, ''))
        elif kind == tokenize.STRING and previous in (tokenize.NEWLINE, tokenize.INDENT,
                                                      tokenize.DEDENT, tokenize.NL):
            cuts.append((start, end, "''"))
        elif kind == tokenize.STRING and end[0] > start[0]:
            keep_lines.update(range(start[0] + 1, end[0] + 1))
        if kind not in (tokenize.COMMENT, tokenize.NL):
            previous = kind
    for (row, col), (end_row, end_col), text in reversed(cuts):
        head = lines[row - 1][:col]
        rest = lines[end_row - 1][end_col:]
        lines[row - 1:end_row] = [head + text + rest]
        shift = end_row - row
        if shift:
            keep_lines = {n if n <= row else n - shift for n in keep_lines}
    out = []
    for number, line in enumerate(lines, start=1):
        if number in keep_lines:
            out.append(line)
        elif line.strip():
            out.append(line.rstrip() + '\n')
    return ''.join(out)


def build(entry, user, out_dir, public=False):
    """Собирает Kaggle-версию одного практикума. Возвращает путь к папке."""
    src = os.path.join(ROOT, entry['notebook'])
    slug = entry['kaggle']

    # docstring-и модулей не нужны: назначение уже описано в титульной ячейке
    kit_body = compact(glued_kit()).strip()

    nb = nbformat.read(src, as_version=4)
    setup = next((c for c in nb.cells
                  if c.cell_type == 'code' and 'from kit import' in c.source), None)
    if setup is None:
        raise SystemExit(f"{entry['id']}: в ноутбуке нет ячейки с \"from kit import\"")

    tail = setup.source.split('from kit import', 1)[1].split('\n', 1)[1]
    setup.source = (
        "# Проверочный набор практикума. В репозитории это пакет practicum/kit/,\n"
        "# здесь его модули склеены, чтобы ноутбук работал на Kaggle самостоятельно.\n"
        f"# Исходник: {REPO_URL}\n\n"
        + kit_body + "\n" + tail.replace("import sympy as sp\n", "", 1)
    )

    nb.cells[0].source = nb.cells[0].source.replace(
        "Метки сложности:",
        "Ноутбук самодостаточен: проверочный набор встроен в ячейку настройки.\n"
        "Исходная версия и остальные практикумы — в репозитории проекта.\n\n"
        "Метки сложности:",
    )

    os.makedirs(out_dir, exist_ok=True)
    name = f'{slug}.ipynb'
    _, nb = nbformat.validator.normalize(nb)
    nbformat.validate(nb)
    nbformat.write(nb, os.path.join(out_dir, name))

    meta = {
        "id": f"{user}/{slug}",
        "title": slug,          # совпадает со slug, иначе Kaggle предупреждает
        "code_file": name,
        "language": "python",
        "kernel_type": "notebook",
        "is_private": not public,
        "enable_gpu": False,
        "enable_tpu": False,
        "enable_internet": False,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
    }
    with open(os.path.join(out_dir, 'kernel-metadata.json'), 'w') as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)

    print(f"  собран {entry['id']}: {len(nb.cells)} ячеек -> {out_dir}")
    print(f"    id {meta['id']}, приватный: {meta['is_private']}")
    return out_dir


def kaggle_cli():
    """Путь к kaggle: он ставится в тот же venv, что и sympy.

    Голым именем его звать нельзя: venv практикума активируют не всегда,
    и тогда subprocess не находит команду, хотя python рядом с ней. Ищем
    сначала возле текущего интерпретатора, потом по PATH.
    """
    nearby = os.path.join(os.path.dirname(sys.executable), 'kaggle')
    if os.path.isfile(nearby) and os.access(nearby, os.X_OK):
        return nearby
    return shutil.which('kaggle') or 'kaggle'


def push(out_dir):
    r = subprocess.run([kaggle_cli(), 'kernels', 'push', '-p', out_dir],
                       capture_output=True, text=True)
    line = (r.stdout + r.stderr).strip().split('\n')[-1]
    print(f"    {line}")
    return r.returncode == 0 and 'successfully pushed' in r.stdout


def as_archive(entry):
    """Архивный ноутбук практикума: та же тема, другая бумага.

    B4:archive — это весь корпус темы подряд, по приёмам, без теории.
    В map.yaml он лежит рядом с практикумом, в полях archive и
    kaggle_archive, потому что тема одна и разъезжаться им незачем.
    """
    if not (entry.get('archive') and entry.get('kaggle_archive')):
        sys.exit(f"{entry['id']}: в map.yaml нет полей archive/kaggle_archive")
    copy = dict(entry)
    copy['id'] = entry['id'] + ':archive'
    copy['notebook'] = entry['archive']
    copy['kaggle'] = entry['kaggle_archive']
    return copy


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('practicum', nargs='?',
                    help='идентификатор, например C3 или B4:archive')
    ap.add_argument('--all', action='store_true', help='все практикумы со status: ready')
    ap.add_argument('--push', action='store_true', help='залить на Kaggle после сборки')
    ap.add_argument('--user', default=DEFAULT_USER)
    ap.add_argument('--out', default=os.path.join(ROOT, 'build/kaggle'))
    ap.add_argument('--public', action='store_true',
                    help='снять пометку приватности; см. предупреждение в docstring')
    a = ap.parse_args()

    cmap = load_map()
    if a.all:
        targets = [p for p in cmap.values() if p.get('status') == 'ready']
    elif a.practicum:
        name, _, kind = a.practicum.partition(':')
        if name not in cmap:
            sys.exit(f'нет практикума {name} в map.yaml')
        if kind and kind != 'archive':
            sys.exit(f'непонятный вид ноутбука: {kind}')
        targets = [as_archive(cmap[name]) if kind else cmap[name]]
    else:
        sys.exit('укажите практикум или --all')

    missing = [p['id'] for p in targets if not (p.get('notebook') and p.get('kaggle'))]
    if missing:
        sys.exit(f"в map.yaml нет полей notebook/kaggle у: {', '.join(missing)}")

    print(f'практикумов к публикации: {len(targets)}')
    failed = []
    for entry in targets:
        out_dir = os.path.join(a.out, entry['kaggle'])
        build(entry, a.user, out_dir, a.public)
        if a.push and not push(out_dir):
            failed.append(entry['id'])

    if failed:
        sys.exit(f"\nне залились: {', '.join(failed)}")
    if a.push:
        print('\nвсе залиты')
    else:
        print(f'\nсобрано без заливки; для заливки добавьте --push')


if __name__ == '__main__':
    main()
