"""Проверяет карточки приёмов: разбор YAML, лестницы, ссылки, номера блоков.

Карточки — нормализующий слой между разметкой корпуса и ноутбуками, и читает
их машина, а не только человек. Дважды случалось, что файл вообще не
разбирался: двоеточие внутри фразы («два разных случая: при одном…») делает
из строки отображение, и YAML падает. Пока никто карточки не открывал
программно, ошибка жила незамеченной.

Что проверяется:
  * каждый файл разбирается;
  * ladder перечисляет ровно те же приёмы, что и skills (у заготовок
    с полем status: stub лестницы может не быть);
  * у приёма заполнены обязательные поля, включая trigger — он главный,
    его нельзя достать из разметки автоматически;
  * ссылки skills: и notebook: из map.yaml указывают на существующие файлы;
  * все id блоков в карточках действительно есть в корпусе.

Запуск:  python practicum/tests/check_skills.py
"""

import glob
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit('нужен pyyaml: pip install pyyaml')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

REQUIRED = ('id', 'name', 'trigger', 'chain', 'traps', 'calculator', 'raw_tags', 'blocks')


def corpus_block_ids():
    ids = set()
    for path in glob.glob(os.path.join(ROOT, 'classification/generated/*/*/paper-*.json')):
        with open(path) as fh:
            for b in json.load(fh)['blocks']:
                ids.add(b['id'])
    return ids


def main():
    known = corpus_block_ids()
    if not known:
        sys.exit('корпус пуст: classification/generated не найден')
    problems = []

    for path in sorted(glob.glob(os.path.join(ROOT, 'practicum/skills/*.yaml'))):
        name = os.path.basename(path)
        try:
            with open(path) as fh:
                card = yaml.safe_load(fh)
        except yaml.YAMLError as exc:
            mark = getattr(exc, 'problem_mark', None)
            where = f', строка {mark.line + 1}' if mark else ''
            problems.append(f'{name}: не разбирается{where} — '
                            f'скорее всего двоеточие внутри фразы, возьмите её в кавычки')
            print(f'❌ {name}: YAML не разбирается')
            continue

        skills = card.get('skills') or []
        ids = [s.get('id') for s in skills]
        stub = card.get('status') == 'stub'

        for s in skills:
            for field in REQUIRED:
                if not s.get(field):
                    problems.append(f'{name}, приём {s.get("id")}: пустое поле {field}')
            for bid in (s.get('blocks') or []):
                if bid not in known:
                    problems.append(f'{name}, приём {s.get("id")}: блока {bid} нет в корпусе')

        ladder = card.get('ladder')
        if ladder is None:
            if not stub:
                problems.append(f'{name}: нет ladder, а карточка не помечена status: stub')
        elif set(ladder) != set(ids):
            diff = set(ladder) ^ set(ids)
            problems.append(f'{name}: ladder и skills расходятся по {sorted(diff)}')

        dup = [i for i in set(ids) if ids.count(i) > 1]
        if dup:
            problems.append(f'{name}: приёмы с одинаковым id {sorted(dup)}')

        print(f'{"✅" if not problems else "…"} {name}: приёмов {len(ids)}'
              f'{", stub" if stub else ""}')

    with open(os.path.join(ROOT, 'practicum/map.yaml')) as fh:
        cmap = yaml.safe_load(fh)
    links = 0
    for sec in cmap['sections'].values():
        for p in sec['practicums']:
            for field in ('skills', 'notebook'):
                if field in p:
                    links += 1
                    if not os.path.exists(os.path.join(ROOT, p[field])):
                        problems.append(f'map.yaml, {p["id"]}: {field} указывает '
                                        f'на несуществующий {p[field]}')
    print(f'✅ map.yaml: проверено ссылок {links}')

    if problems:
        print('\nнайдено:')
        for p in problems:
            print('  ', p)
        print(f'\nпроблем: {len(problems)}')
        return 1
    print('\nкарточки приёмов согласованы')
    return 0


if __name__ == '__main__':
    sys.exit(main())
