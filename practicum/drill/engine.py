"""Выбор следующего задания.

Планируется не задача, а приём. Задача — расходный материал: в режиме
счёта она собирается заново по зерну, в режиме узнавания берётся из банка.

Вес приёма складывается из трёх вещей:

  вес = доля баллов практикума × просрочка × (1 + доля ошибок)

Доля баллов взята из карточек — практикум на 222 балла экзамена весит
больше, чем практикум на 83, и повторение это учитывает. Просрочка растёт
по ящикам Лейтнера. Приём, который ни разу не показывали, идёт вперёд
всего остального: пробел хуже, чем подзабытое.

Темы перемешиваются намеренно. Подряд по одной теме учить приятнее, но
именно это даёт ложное чувство усвоенного: на экзамене задача приходит
без подписи, из какого она практикума.
"""
from __future__ import annotations

import json
import os
import random
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, 'bank.json')

COLD_START = 1000.0     # приём без единой попытки
NOT_DUE = 0.05          # ещё не подошёл срок, но в перемешку попасть может


def load_bank(path=BANK_PATH):
    with open(path) as fh:
        bank = json.load(fh)
    bank['skills_by_id'] = {s['id']: s for s in bank['skills']}
    bank['items_by_skill'] = {}
    for item in bank['items']:
        bank['items_by_skill'].setdefault(item['skill'], []).append(item)
    bank['items_by_key'] = {item['key']: item for item in bank['items']}
    total = sum(p['marks'] or 0 for p in bank['practicums']) or 1
    bank['share'] = {p['id']: (p['marks'] or 0) / total
                     for p in bank['practicums']}
    return bank


def weight(skill, state, share, now):
    """Насколько этот приём просится следующим."""
    if state is None:
        return COLD_START
    base = 100.0 * share.get(skill['practicum'], 0.0)
    overdue = (now - state['due']) / 86400.0
    if overdue < 0:
        return base * NOT_DUE
    error_rate = state['wrong'] / max(state['seen'], 1)
    return base * (1.0 + min(overdue, 30.0)) * (1.0 + error_rate)


def candidates(bank, mode, generators):
    """Приёмы, по которым в выбранном режиме есть чем спросить."""
    out = []
    for skill in bank['skills']:
        has_recog = bool(bank['items_by_skill'].get(skill['id']))
        has_compute = skill['id'] in generators
        if mode == 'recognition' and has_recog:
            out.append((skill, 'recognition'))
        elif mode == 'compute' and has_compute:
            out.append((skill, 'compute'))
        elif mode == 'mixed' and (has_recog or has_compute):
            out.append((skill, 'both'))
    return out


def choose(bank, states, generators, mode='mixed', rng=None, avoid=()):
    """Возвращает (приём, вид задания). Вид «both» решается броском."""
    rng = rng or random.Random()
    now = time.time()
    pool = candidates(bank, mode, generators)
    if not pool:
        raise LookupError(f'в режиме {mode!r} нет ни одного приёма')

    fresh = [(s, k) for s, k in pool if s['id'] not in avoid]
    pool = fresh or pool

    weights = [weight(skill, states.get(skill['id']), bank['share'], now)
               for skill, _ in pool]
    skill, kind = rng.choices(pool, weights=weights, k=1)[0]

    if kind == 'both':
        has_recog = bool(bank['items_by_skill'].get(skill['id']))
        has_compute = skill['id'] in generators
        if has_recog and has_compute:
            # Узнавание дешевле по времени, поэтому его чуть больше.
            kind = 'recognition' if rng.random() < 0.55 else 'compute'
        else:
            kind = 'recognition' if has_recog else 'compute'
    return skill, kind


def build_item(bank, generators, skill, kind, rng=None, seed=None):
    """Собирает задание: (что показать, чем проверять, эталон).

    Эталон и описание проверки странице не отдаются — они остаются здесь
    и достаются заново, когда приходит ответ.
    """
    rng = rng or random.Random()
    if kind == 'recognition':
        pool = bank['items_by_skill'][skill['id']]
        item = rng.choice(pool)
        shown = {
            'item': item['key'],
            'kind': 'recognition',
            'skill': skill['id'],
            'practicum': item['practicum'],
            'prompt': item['prompt'],
            'options': item['options'],
            'budget_ms': item['budget_ms'],
        }
        return shown, {'kind': 'digest', 'digest': item['answer_digest']}, \
            item['answer']

    seed = rng.randrange(2**31) if seed is None else seed
    built = generators[skill['id']](random.Random(seed))
    shown = {
        'item': f'compute:{skill["id"]}:{seed}',
        'kind': 'compute',
        'skill': skill['id'],
        'practicum': skill['practicum'],
        'prompt': built['prompt'],
        'note': built.get('note'),
        'budget_ms': built['budget_ms'],
    }
    return shown, built['check'], built['answer']


def rebuild_check(bank, generators, item_key):
    """Восстанавливает проверку и эталон по ключу задания.

    Ничего не хранится между запросами: задание на счёт собирается тем же
    генератором с тем же зерном и обязано выйти таким же.
    """
    if item_key.startswith('recog:'):
        item = bank['items_by_key'].get(item_key)
        if item is None:
            raise LookupError(item_key)
        return item, {'kind': 'digest', 'digest': item['answer_digest']}, \
            item['answer']

    _, skill_id, seed = item_key.split(':', 2)
    if skill_id not in generators:
        raise LookupError(item_key)
    built = generators[skill_id](random.Random(int(seed)))
    skill = bank['skills_by_id'][skill_id]
    meta = {'key': item_key, 'kind': 'compute', 'skill': skill_id,
            'practicum': skill['practicum'], 'prompt': built['prompt'],
            'budget_ms': built['budget_ms']}
    return meta, built['check'], built['answer']
