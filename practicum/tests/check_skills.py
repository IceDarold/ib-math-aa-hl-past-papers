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
  * все id блоков в карточках действительно есть в корпусе;
  * calculator.mode известен странице повторения. Слов там накопилось
    тринадцать, а словарь перевода в DrillView.tsx знал шесть, и в шапке
    карточки печаталось «калькулятор allowed» английским посреди русской
    строки. Заодно ловится `mode: no` без кавычек: YAML делает из него
    False, и до страницы доезжает не слово, а булево.

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
DRILL_VIEW = os.path.join(ROOT, 'classification/web/src/components/DrillView.tsx')


def calculator_words():
    """Ключи словаря CALCULATOR со страницы повторения."""
    with open(DRILL_VIEW) as fh:
        text = fh.read()
    head = text.find('const CALCULATOR')
    if head < 0:
        return None
    body = text[text.index('{', head) + 1:text.index('}', head)]
    return {line.split(':')[0].strip()
            for line in body.splitlines() if ':' in line}


def corpus_block_ids():
    ids = set()
    for path in glob.glob(os.path.join(ROOT, 'classification/generated/*/*/paper-*.json')):
        with open(path) as fh:
            for b in json.load(fh)['blocks']:
                ids.add(b['id'])
    return ids


def main():
    known = corpus_block_ids()
    words = calculator_words()
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
            # Двоеточие внутри фразы списка YAML не роняет, а молча делает
            # из строки отображение: «Проверить свободный член: он равен…»
            # разбирается в {'Проверить свободный член': 'он равен…'}.
            # Громкий случай ловится разбором выше, тихий — только здесь.
            for field in ('chain', 'traps'):
                for item in (s.get(field) or []):
                    if not isinstance(item, str):
                        head = (list(item)[0] if isinstance(item, dict)
                                else str(item))[:40]
                        problems.append(
                            f'{name}, приём {s.get("id")}: пункт {field} '
                            f'разобрался не в строку — «{head}…»: '
                            f'двоеточие внутри фразы, возьмите её в кавычки')
            mode = (s.get('calculator') or {}).get('mode')
            if words is not None and mode not in words:
                problems.append(
                    f'{name}, приём {s.get("id")}: calculator.mode = {mode!r} '
                    f'страница повторения перевести не умеет'
                    + (' — YAML прочитал слово как булево, возьмите его '
                       'в кавычки' if isinstance(mode, bool) else ''))
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
            for field in ('skills', 'notebook', 'archive'):
                if field in p:
                    links += 1
                    if not os.path.exists(os.path.join(ROOT, p[field])):
                        problems.append(f'map.yaml, {p["id"]}: {field} указывает '
                                        f'на несуществующий {p[field]}')
    print(f'✅ map.yaml: проверено ссылок {links}')
    if words is None:
        problems.append('в DrillView.tsx не нашёлся словарь CALCULATOR')
    else:
        print(f'✅ DrillView.tsx: слов про калькулятор {len(words)}')

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
