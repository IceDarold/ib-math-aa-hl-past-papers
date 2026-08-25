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
import glob
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


ARCHIVE = 'AA_HL'


def paper_dir(session, zone, paper):
    """Каталог бумаги в архиве по полям корпуса.

    У ноябрьской сессии 2023 года корпус держит Paper 3 двумя зональными
    копиями, хотя бумага одна и лежит в Common. Каталогов TZ1/TZ2 для неё
    не существует, поэтому при промахе пробуем Common — это то же самое
    дублирование, что отмечено в corpus_issues карточек B1 и C1.
    """
    month, year = session.split()
    base = os.path.join(ARCHIVE, year, month)
    # Разметка архива неоднородна: у ноября 2025 между зоной и бумагой стоит
    # ещё уровень языка, а зональные копии общей Paper 3 живут в Common.
    candidates = [
        os.path.join(base, zone, f'Paper {paper}'),
        os.path.join(base, zone, 'English', f'Paper {paper}'),
        os.path.join(base, 'Common', f'Paper {paper}'),
    ]
    for candidate in candidates:
        if os.path.isfile(os.path.join(ROOT, candidate, 'question-paper.pdf')):
            return candidate
    return candidates[0]


def corpus_blocks():
    """Метаданные всех блоков корпуса: бумага, страницы, баллы."""
    out = {}
    pattern = os.path.join(ROOT, 'classification/generated/*/*/paper-*.json')
    for path in sorted(glob.glob(pattern)):
        with open(path) as fh:
            paper = json.load(fh)
        folder = paper_dir(paper['session'], paper['zone'], paper['paper'])
        for block in paper['blocks']:
            out.setdefault(block['id'], {
                'session': paper['session'],
                'zone': paper['zone'],
                'paper': paper['paper'],
                'question': block.get('question'),
                'part': block.get('part'),
                'marks': block.get('marks'),
                'calculator': paper.get('calculator'),
                'source_pages': block.get('source_pages'),
                'markscheme_pages': block.get('markscheme_pages'),
                'dir': folder,
            })
    return out


def flatten(text):
    """Многострочное поле карточки в одну строку: в вёрстке переносы свои."""
    return re.sub(r'\s+', ' ', str(text)).strip()


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
    # B2 написан по-английски, и заголовок тренажёра там Trainer.
    cells = [''.join(c['source']) for c in nb['cells']
             if c['cell_type'] == 'markdown'
             and ('Тренажёр' in ''.join(c['source'])
                  or 'Trainer' in ''.join(c['source']))]
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

    corpus = corpus_blocks()
    skills, items, practicums, uncovered = [], [], [], []
    archive = {}

    for entry in ready_practicums():
        pid = entry['id']
        with open(os.path.join(ROOT, entry['skills'])) as fh:
            card = yaml.safe_load(fh)
        ladder = card['ladder']
        by_id = {s['id']: s for s in card['skills']}
        card_corpus = card.get('corpus', {})
        marks = card_corpus.get('marks')

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
            'marks': marks,
            'blocks': card_corpus.get('blocks'),
        })

        for rung, skill_id in enumerate(ladder, start=1):
            skill = by_id[skill_id]
            skills.append({
                'id': f'{pid}.{skill_id}',
                'practicum': pid,
                'name': skill['name'],
                'rung': skill.get('rung', rung),
                'trigger': flatten(skill['trigger']),
                # Ход и ловушки показываются после попытки: ход всегда,
                # ловушки при ошибке. В карточке они и написаны как разбор,
                # который стоит прочесть, а не как справка.
                'chain': [flatten(step) for step in skill.get('chain', [])],
                'traps': [flatten(trap) for trap in skill.get('traps', [])],
                'calculator': skill['calculator']['mode'],
                'practicum_marks': marks,
                # Блоки архива, на которых приём построен: по ним режим
                # разбора достаёт настоящий вопрос и страницу схемы.
                'blocks': [b for b in (skill.get('blocks') or [])
                           if b in corpus],
            })
            for block in skill.get('blocks') or []:
                if block in corpus and block not in archive:
                    archive[block] = dict(corpus[block],
                                          skill=f'{pid}.{skill_id}')

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
        'version': 2,
        'archive': archive,
        'practicums': practicums,
        'skills': skills,
        'items': items,
        'uncovered_skills': uncovered,
    }
    out = os.path.join(HERE, 'bank.json')
    with open(out, 'w') as fh:
        json.dump(bank, fh, ensure_ascii=False, indent=1)
        fh.write('\n')

    have_pdf = sum(1 for b in archive.values()
                   if os.path.isfile(os.path.join(ROOT, b['dir'],
                                                  'question-paper.pdf')))
    print(f'практикумов {len(practicums)}, приёмов {len(skills)}, '
          f'условий на узнавание {len(items)}')
    print(f'блоков архива с привязкой к приёму: {len(archive)}, '
          f'из них с PDF на месте: {have_pdf}')
    if uncovered:
        print(f'без единого условия на узнавание ({len(uncovered)}): '
              f'{", ".join(uncovered)}')
    print(f'-> {os.path.relpath(out, ROOT)}')


if __name__ == '__main__':
    build()
