#!/usr/bin/env python3
"""Проверяет карту практикумов против корпуса классификации.

Считает, сколько баллов архива приходится на каждый практикум, и сообщает:
  * практикумы вне диапазона гранулярности (60–200 баллов), кроме
    помеченных полем exception;
  * темы корпуса, не попавшие ни в один практикум;
  * темы, доли которых не складываются в единицу.

Запуск:  python practicum/check_map.py
"""

import collections
import glob
import json
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("нужен pyyaml: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_MARKS, MAX_MARKS = 60, 200


def load_corpus():
    """Баллы и блоки по темам. Один и тот же id встречается один раз."""
    marks, blocks, calc = collections.Counter(), collections.Counter(), collections.Counter()
    seen = set()
    files = sorted(glob.glob(os.path.join(ROOT, 'classification/generated/*/*/paper-*.json')))
    for path in files:
        with open(path) as fh:
            paper = json.load(fh)
        for b in paper['blocks']:
            if b['id'] in seen:
                continue
            seen.add(b['id'])
            marks[b['primary_topic']] += b.get('marks', 0)
            blocks[b['primary_topic']] += 1
            if paper.get('calculator') == 'yes':
                calc[b['primary_topic']] += b.get('marks', 0)
    return marks, blocks, calc, len(files)


def parts(practicum):
    """Нормализует subtopics в список (тема, доля)."""
    for item in practicum['subtopics']:
        if isinstance(item, dict):
            yield item['topic'], float(item.get('share', 1.0))
        else:
            yield item, 1.0


def main():
    marks, blocks, calc, n_files = load_corpus()
    if not marks:
        sys.exit("корпус пуст: classification/generated не найден")

    with open(os.path.join(ROOT, 'practicum/map.yaml')) as fh:
        cmap = yaml.safe_load(fh)

    rows, shares, missing = [], collections.defaultdict(float), []

    for sec in cmap['sections'].values():
        for p in sec['practicums']:
            total = nb = cm = 0.0
            for topic, share in parts(p):
                if topic not in marks:
                    missing.append((p['id'], topic))
                    continue
                total += marks[topic] * share
                nb += blocks[topic] * share
                cm += calc[topic] * share
                shares[topic] += share
            pct = round(100 * cm / total) if total else 0
            rows.append((p['id'], p['title'], round(total), round(nb), pct,
                         p.get('status', ''), p.get('exception')))

    print(f"корпус: {n_files} бумаг, {sum(blocks.values())} блоков, "
          f"{sum(marks.values())} баллов, {len(marks)} тем\n")
    calc_total = sum(calc.values())
    print(f"из них с калькулятором: {calc_total} баллов "
          f"({round(100 * calc_total / sum(marks.values()))}%)\n")
    print(f"{'id':>4}  {'баллов':>7}  {'блоков':>7}  {'GDC':>5}  тема")
    print('-' * 82)

    problems = []
    for pid, title, total, nb, pct, status, exc in rows:
        flag = ''
        if total < MIN_MARKS or total > MAX_MARKS:
            why = 'мало' if total < MIN_MARKS else 'много'
            if exc:
                flag = f'  ← {why}, есть обоснование'
            else:
                flag = f'  ← {why}'
                problems.append(f"{pid}: {total} баллов — {why}")
        tail = f" [{status}]" if status else ''
        print(f"{pid:>4}  {total:7d}  {nb:7d}  {pct:4d}%  {title}{tail}{flag}")

    print(f"\nвсего практикумов: {len(rows)}")

    uncovered = sorted(set(marks) - set(shares))
    if uncovered:
        print("\nтемы вне карты:")
        for topic in uncovered:
            print(f"  {marks[topic]:5d}m  {topic}")
        problems += [f"тема вне карты: {t}" for t in uncovered]

    bad_share = {t: s for t, s in shares.items() if abs(s - 1.0) > 1e-6}
    if bad_share:
        print("\nдоли темы не складываются в единицу:")
        for topic, s in sorted(bad_share.items()):
            print(f"  {topic}: {s:g}")
        problems += [f"доли {t} = {s:g}" for t, s in bad_share.items()]

    if missing:
        print("\nтемы из карты, которых нет в корпусе:")
        for pid, topic in missing:
            print(f"  {pid}: {topic}")
        problems += [f"{pid}: темы {t} нет в корпусе" for pid, t in missing]

    if problems:
        print(f"\nпроблем: {len(problems)}")
        return 1
    print("\nкарта согласована с корпусом")
    return 0


if __name__ == '__main__':
    sys.exit(main())
