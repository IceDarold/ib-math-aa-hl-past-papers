#!/usr/bin/env python3
"""Собирает и публикует Kaggle-версии практикумов.

На Kaggle ноутбук лежит один, соседних файлов рядом нет, поэтому
`from kit import *` там не работает. Скрипт встраивает kit.py в ячейку
настройки и кладёт рядом kernel-metadata.json.

Источник правды — practicum/map.yaml: у готового практикума есть поля
`notebook` и `kaggle`, и публиковать можно по идентификатору, не помня путей.

    python practicum/make_kaggle.py C3 --push        # один практикум
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
import re
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


def build(entry, user, out_dir, public=False):
    """Собирает Kaggle-версию одного практикума. Возвращает путь к папке."""
    src = os.path.join(ROOT, entry['notebook'])
    slug = entry['kaggle']

    kit = open(os.path.join(ROOT, 'practicum/kit.py')).read()
    # docstring модуля не нужен: назначение уже описано в титульной ячейке
    kit_body = re.sub(r'^""".*?"""\n\n', '', kit, count=1, flags=re.S).strip()

    nb = nbformat.read(src, as_version=4)
    setup = next((c for c in nb.cells
                  if c.cell_type == 'code' and 'from kit import' in c.source), None)
    if setup is None:
        raise SystemExit(f"{entry['id']}: в ноутбуке нет ячейки с \"from kit import\"")

    tail = setup.source.split('from kit import', 1)[1].split('\n', 1)[1]
    setup.source = (
        "# Проверочный набор практикума. В репозитории это отдельный файл practicum/kit.py,\n"
        "# здесь он встроен, чтобы ноутбук работал на Kaggle самостоятельно.\n"
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


def push(out_dir):
    r = subprocess.run(['kaggle', 'kernels', 'push', '-p', out_dir],
                       capture_output=True, text=True)
    line = (r.stdout + r.stderr).strip().split('\n')[-1]
    print(f"    {line}")
    return r.returncode == 0 and 'successfully pushed' in r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('practicum', nargs='?', help='идентификатор, например C3')
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
        if a.practicum not in cmap:
            sys.exit(f'нет практикума {a.practicum} в map.yaml')
        targets = [cmap[a.practicum]]
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
