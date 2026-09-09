#!/usr/bin/env python3
"""Собирает данные браузерного практикума для страницы.

`classification/web/src/data/practicums.ts` когда-то держал весь список
практикумов и отставал: в репозитории было двадцать два собранных, а в файле
два. Список с тех пор переехал в службу и приходит из `practicum/map.yaml` —
единственного источника, по которому практикумы и собираются (см.
`practicum/aahl/subject.py`). В файле осталась ровно одна живая запись:
практикум, который проходится прямо в браузере, с его приёмами.

Эта одна запись всё ещё писалась руками — и точно так же отстала: числа
корпуса в ней были от старой версии карточки, а один приём из девяти
отсутствовал. Теперь она собирается отсюда, из карты и карточки приёмов,
а `check_skills.py` следит, чтобы собранное совпадало с лежащим в репозитории.

    python practicum/build_browser_practicum.py           # пересобрать
    python practicum/build_browser_practicum.py --check   # только сверить
"""

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("нужен pyyaml: pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP = os.path.join(ROOT, 'practicum/map.yaml')
TARGET = os.path.join(ROOT, 'classification/web/src/data/practicums.ts')
HUB = os.path.join(ROOT, 'classification/web/src/components/PracticumHub.tsx')

# Какой практикум проходится в браузере, решает страница: константа
# BROWSER_PRACTICUM в PracticumHub.tsx. Здесь она читается оттуда же,
# чтобы эти два места не могли разойтись молча.
MODES = ('required', 'replaces', 'speeds_up', 'checks', 'forbidden')


def browser_id():
    """Идентификатор браузерного практикума — из самой страницы."""
    found = re.search(r"const BROWSER_PRACTICUM = '([A-Z]\d)'", open(HUB).read())
    if not found:
        sys.exit('в PracticumHub.tsx не нашлась константа BROWSER_PRACTICUM')
    return found.group(1)


def entry_for(want):
    """Запись практикума из карты: заголовок, темы, ноутбук, карточка приёмов."""
    plan = yaml.safe_load(open(MAP))
    for section in plan['sections'].values():
        for entry in section.get('practicums') or ():
            if entry['id'] != want:
                continue
            topics = []
            for item in entry.get('subtopics') or ():
                topics.append(item['topic'] if isinstance(item, dict) else item)
            return entry, topics
    sys.exit(f'{want} не найден в карте практикумов')


def first_sentence(text):
    """Первое предложение триггера: в карточке он бывает на абзац."""
    text = ' '.join(str(text).split())
    cut = re.search(r'(?<=[.!?])\s', text)
    return text[:cut.start()] if cut else text


def skills_of(card_path):
    """Приёмы карточки в том виде, в каком их показывает страница."""
    card = yaml.safe_load(open(os.path.join(ROOT, card_path)))
    out = []
    for skill in card['skills']:
        mode = (skill.get('calculator') or {}).get('mode')
        if mode not in MODES:
            sys.exit(f"{card_path}: приём {skill['id']} помечен как «{mode}», "
                     f"а страница знает только {', '.join(MODES)}")
        out.append({'id': skill['id'], 'name': skill['name'],
                    'trigger': first_sentence(skill['trigger']),
                    'calculator': mode})
    return out


def quote(text):
    """Строка для TypeScript: одинарные кавычки, как во всём проекте."""
    return "'" + str(text).replace('\\', '\\\\').replace("'", "\\'") + "'"


def render():
    want = browser_id()
    entry, topics = entry_for(want)
    if not entry.get('skills'):
        sys.exit(f'{want}: в карте нет ссылки на карточку приёмов')
    skills = skills_of(entry['skills'])
    lines = [
        '// Файл собирается: python practicum/build_browser_practicum.py',
        '// Руками не править — правьте practicum/map.yaml и карточку приёмов.',
        '',
        'export interface PracticumSkill {',
        '  id: string',
        '  name: string',
        '  trigger: string',
        "  calculator: " + ' | '.join(quote(m) for m in MODES),
        '}',
        '',
        'export interface Practicum {',
        '  id: string',
        '  title: string',
        '  topics: string[]',
        '  notebook: string',
        '  skills: PracticumSkill[]',
        '}',
        '',
        '/** Единственный практикум, который проходится прямо в браузере.',
        ' *  Остальной список страница берёт у службы, а та — из',
        ' *  practicum/map.yaml: держать его ещё и здесь значило отставать. */',
        'export const practicums: Practicum[] = [',
        '  {',
        f"    id: {quote(entry['id'])},",
        f"    title: {quote(entry['title'])},",
        '    topics: [' + ', '.join(quote(t) for t in topics) + '],',
        f"    notebook: {quote(entry['notebook'])},",
        '    skills: [',
    ]
    for skill in skills:
        lines.append('      { ' + ', '.join([
            f"id: {quote(skill['id'])}",
            f"name: {quote(skill['name'])}",
            f"trigger: {quote(skill['trigger'])}",
            f"calculator: {quote(skill['calculator'])}",
        ]) + ' },')
    lines += ['    ],', '  },', ']', '']
    return '\n'.join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true',
                    help='не переписывать, а сверить с тем, что лежит')
    args = ap.parse_args()
    fresh = render()
    have = open(TARGET).read() if os.path.exists(TARGET) else ''
    if args.check:
        if fresh == have:
            print('practicums.ts совпадает со сборкой')
            return 0
        print('practicums.ts отстал от карты и карточки приёмов; '
              'пересоберите: python practicum/build_browser_practicum.py')
        return 1
    if fresh == have:
        print('practicums.ts уже собран')
        return 0
    with open(TARGET, 'w') as fh:
        fh.write(fresh)
    print(f'-> {os.path.relpath(TARGET, ROOT)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
