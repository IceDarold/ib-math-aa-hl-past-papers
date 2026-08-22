#!/usr/bin/env python3
"""Собирает банк тренажёра из готовых практикумов.

Единственный источник правды — сами ноутбуки и карточки приёмов. Условия
для режима «узнавание» уже написаны: в конце каждого практикума стоит
тренажёр распознавания, и здесь его пункты просто вынимаются оттуда
вместе с ключом из генератора.

Форматов тренажёра в архиве два. Ранний (A3, A7) — таблица «| # | Условие |»
и отдельная табличка кодов; поздний — нумерованный список и легенда строкой.
Разбираются оба.

Результат — bank.json, который читает сервер. Файл коммитится: на боевой
машине сервер не должен зависеть ни от генераторов, ни от sympy при старте,
а расхождение банка с практикумом видно в диффе.

Запуск:  python practicum/drill/build_bank.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRACTICUM = os.path.dirname(HERE)
ROOT = os.path.dirname(PRACTICUM)

import yaml  # noqa: E402


def digest(value):
    """Тот же короткий хеш, что и kit.digest: ключи тренажёра сходятся."""
    return hashlib.sha256(str(value).encode()).hexdigest()[:12]


ITEM_ROW = re.compile(r'^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*$', re.M)
ITEM_NUM = re.compile(r'^(\d+)\.\s+(.*)$')
CODE_IN_HEAD = re.compile(r'`(\w+)`')
SPLIT_ITEMS = re.compile(r'^(?:\d+\.\s|\|\s*\d+\s*\|)', re.M)


def ready_practicums():
    """Практикумы со статусом ready из карты, в порядке карты."""
    with open(os.path.join(PRACTICUM, 'map.yaml')) as fh:
        cmap = yaml.safe_load(fh)
    out = []
    for section in cmap['sections'].values():
        for entry in section['practicums']:
            if entry.get('status') == 'ready':
                out.append(entry)
    return out


def trigger_key(practicum_id):
    """Ключ тренажёра из генератора: {номер: код приёма}.

    Читаем через ast, а не импортом: импорт генератора собирает ноутбук.
    """
    path = os.path.join(PRACTICUM, 'generators',
                        f'build_{practicum_id.lower()}.py')
    tree = ast.parse(open(path).read())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                getattr(t, 'id', None) == 'TRIGGER' for t in node.targets):
            return {int(k): v for k, v in ast.literal_eval(node.value).items()}
    raise SystemExit(f'{practicum_id}: в генераторе нет TRIGGER')


def trainer_cell(notebook_path):
    """Последняя markdown-ячейка с тренажёром распознавания."""
    with open(notebook_path) as fh:
        nb = json.load(fh)
    cells = [''.join(c['source']) for c in nb['cells']
             if c['cell_type'] == 'markdown'
             and 'Тренажёр' in ''.join(c['source'])]
    if not cells:
        raise SystemExit(f'{notebook_path}: тренажёр не найден')
    return cells[-1]


def parse_trainer(text):
    """Возвращает (коды из легенды, {номер: условие})."""
    head = SPLIT_ITEMS.split(text, maxsplit=1)[0]
    legend = list(dict.fromkeys(CODE_IN_HEAD.findall(head)))

    rows = ITEM_ROW.findall(text)
    if rows:
        return legend, {int(n): t.strip() for n, t in rows}

    items, current = {}, None
    for line in text.split('\n'):
        hit = ITEM_NUM.match(line)
        if hit:
            current = int(hit.group(1))
            items[current] = hit.group(2).strip()
        elif current is not None and line.strip():
            items[current] += ' ' + line.strip()
        elif not line.strip():
            current = None
    return legend, items


def build():
    with open(os.path.join(HERE, 'codes.yaml')) as fh:
        codes_map = yaml.safe_load(fh)

    skills, items, practicums, uncovered = [], [], [], []

    for entry in ready_practicums():
        pid = entry['id']
        with open(os.path.join(ROOT, entry['skills'])) as fh:
            card = yaml.safe_load(fh)
        ladder = card['ladder']
        by_id = {s['id']: s for s in card['skills']}
        corpus = card.get('corpus', {})

        mapping = codes_map.get(pid)
        if not mapping:
            raise SystemExit(f'{pid}: нет раздела в codes.yaml')

        legend, conditions = parse_trainer(
            trainer_cell(os.path.join(ROOT, entry['notebook'])))
        key = trigger_key(pid)

        for code in legend:
            if code not in mapping:
                raise SystemExit(f'{pid}: код {code!r} из легенды не описан '
                                 f'в codes.yaml')
        for code, spec in mapping.items():
            if spec['skill'] not in ladder:
                raise SystemExit(f'{pid}: код {code!r} показывает на приём '
                                 f'{spec["skill"]!r}, которого нет в лестнице')

        touched = {spec['skill'] for spec in mapping.values()}
        uncovered += [f'{pid}.{rung}' for rung in ladder if rung not in touched]

        practicums.append({
            'id': pid,
            'title': entry['title'],
            'section': pid[0],
            'notebook': entry['notebook'],
            'marks': corpus.get('marks'),
            'blocks': corpus.get('blocks'),
        })

        for rung, skill_id in enumerate(ladder, start=1):
            skill = by_id[skill_id]
            skills.append({
                'id': f'{pid}.{skill_id}',
                'practicum': pid,
                'name': skill['name'],
                'rung': skill.get('rung', rung),
                'trigger': re.sub(r'\s+', ' ', skill['trigger']).strip(),
                'calculator': skill['calculator']['mode'],
                'practicum_marks': corpus.get('marks'),
            })

        options = [{'code': c, 'name': mapping[c]['name']} for c in legend]
        for number, prompt in sorted(conditions.items()):
            code = key.get(number)
            if code is None:
                raise SystemExit(f'{pid}: у пункта {number} нет ключа')
            if code not in mapping:
                raise SystemExit(f'{pid}: ключ пункта {number} — код {code!r}, '
                                 f'которого нет в codes.yaml')
            items.append({
                'key': f'recog:{pid}:{number}',
                'kind': 'recognition',
                'practicum': pid,
                'skill': f'{pid}.{mapping[code]["skill"]}',
                'prompt': prompt,
                'options': options,
                'answer': code,
                'answer_digest': digest(code),
                'budget_ms': 8000,
            })

    bank = {
        'version': 1,
        'practicums': practicums,
        'skills': skills,
        'items': items,
        'uncovered_skills': uncovered,
    }
    out = os.path.join(HERE, 'bank.json')
    with open(out, 'w') as fh:
        json.dump(bank, fh, ensure_ascii=False, indent=1)
        fh.write('\n')

    print(f'практикумов {len(practicums)}, приёмов {len(skills)}, '
          f'условий на узнавание {len(items)}')
    if uncovered:
        print(f'без единого условия на узнавание ({len(uncovered)}): '
              f'{", ".join(uncovered)}')
    print(f'-> {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    build()
