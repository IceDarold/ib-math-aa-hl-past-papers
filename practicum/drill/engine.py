"""Выбор следующего задания.

Планируется не задача, а приём. Задача — расходный материал: в режиме
счёта она собирается заново по зерну, в режиме узнавания берётся из банка.

Вес приёма складывается из трёх вещей:

  вес = доля баллов практикума × просадка × трудность

Доля баллов взята из карточек — практикум на 222 балла экзамена весит
больше, чем практикум на 83, и повторение это учитывает. Просадка — это
`1 − R`, сколько от приёма утекло с последнего раза; она же заменила
просрочку по ящикам, и отдельного разбора «срок подошёл или нет» больше
не нужно: у свежего приёма просадка около нуля сама. Приём, который ни
разу не показывали, идёт вперёд всего остального: пробел хуже, чем
подзабытое.

Темы перемешиваются намеренно. Подряд по одной теме учить приятнее, но
именно это даёт ложное чувство усвоенного: на экзамене задача приходит
без подписи, из какого она практикума.
"""
from __future__ import annotations

import json
import os
import random
import time

from drill import memory
from drill.archive import block_page_numbers
from drill.archive import reference as archive_reference

HERE = os.path.dirname(os.path.abspath(__file__))
BANK_PATH = os.path.join(HERE, 'bank.json')

COLD_START = 1000.0     # приём без единой попытки
FLOOR = 0.01            # свежий приём в перемешку всё же попадает
MIDDLE = 5.5            # трудность приёма, взятого с первого раза


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
    if state is None or state.get('last_ts') is None:
        return COLD_START
    base = 100.0 * share.get(skill['practicum'], 0.0)
    days = max(now - state['last_ts'], 0.0) / memory.DAY
    slump = 1.0 - memory.retrievability(state.get('stability'), days)
    hardness = (state.get('difficulty') or MIDDLE) / MIDDLE
    return base * max(slump, FLOOR) * hardness


def matching_blocks(bank, skill, papers=None, marks=None, avoid=()):
    """Вопросы архива этого приёма, подходящие под отбор.

    papers — какие бумаги брать: Paper 1 без калькулятора, Paper 2 с ним,
    Paper 3 это длинные исследования. marks — вилка по цене вопроса: два
    балла и девять баллов требуют разного времени и разного нерва.
    """
    out = []
    for block_id in skill.get('blocks') or ():
        block = bank.get('archive', {}).get(block_id)
        if block is None or block_id in avoid:
            continue
        if papers and block.get('paper') not in papers:
            continue
        if marks:
            low, high = marks
            price = block.get('marks') or 0
            if not (low <= price <= (high or 99)):
                continue
        out.append(block_id)
    return out


def candidates(bank, mode, generators, practicums=None, papers=None,
               marks=None):
    """Приёмы, по которым в выбранном режиме есть чем спросить."""
    out = []
    for skill in bank['skills']:
        if practicums and skill['practicum'] not in practicums:
            continue
        has_recog = bool(bank['items_by_skill'].get(skill['id']))
        has_compute = skill['id'] in generators
        has_written = bool(matching_blocks(bank, skill, papers, marks))
        if mode == 'recognition' and has_recog:
            out.append((skill, 'recognition'))
        elif mode == 'compute' and has_compute:
            out.append((skill, 'compute'))
        elif mode == 'written' and has_written:
            out.append((skill, 'written'))
        elif mode == 'mixed' and (has_recog or has_compute):
            # Разбор письменной работы в перемешку не идёт намеренно:
            # он занимает минуты и требует бумаги, а перемешка устроена
            # для коротких заданий подряд.
            out.append((skill, 'both'))
    return out


def choose(bank, states, generators, mode='mixed', rng=None, avoid=(),
           practicums=None, only_due=False, order='schedule', papers=None,
           marks=None):
    """Возвращает (приём, вид задания). Вид «both» решается броском.

    order:
      schedule — по весу: доля баллов, просрочка, доля ошибок;
      ladder   — сплошным проходом от простого к сложному, реже виденное
                 вперёд: так закрывают пробелы, а не повторяют;
      random   — поровну, без всякого расписания.
    """
    rng = rng or random.Random()
    now = time.time()
    pool = candidates(bank, mode, generators, practicums, papers, marks)
    if not pool:
        raise LookupError(f'в режиме {mode!r} нет ни одного приёма')

    if only_due:
        due_now = [(s, k) for s, k in pool
                   if states.get(s['id']) is None
                   or states[s['id']]['due'] <= now]
        # Если просроченного не осталось — это не ошибка, а хороший день:
        # берём весь набор, чтобы сессия всё равно состоялась.
        pool = due_now or pool

    fresh = [(s, k) for s, k in pool if s['id'] not in avoid]
    pool = fresh or pool

    if order == 'ladder':
        def position(entry):
            skill = entry[0]
            state = states.get(skill['id'])
            return (state['seen'] if state else 0, skill['rung'], skill['id'])
        skill, kind = min(pool, key=position)
    elif order == 'random':
        skill, kind = rng.choice(pool)
    else:
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


def build_item(bank, generators, skill, kind, rng=None, seed=None,
               avoid_blocks=(), papers=None, marks=None):
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

    if kind == 'written':
        # Настоящий вопрос архива: показываем страницу билета картинкой,
        # проверять его будет разбор, а не sympy.
        fresh = matching_blocks(bank, skill, papers, marks, avoid_blocks)
        blocks = fresh or matching_blocks(bank, skill, papers, marks)
        if not blocks:
            raise LookupError('под этот отбор вопросов нет')
        block_id = rng.choice(blocks)
        block = bank['archive'][block_id]
        marks = block.get('marks') or 6
        shown = {
            'item': f'written:{block_id}',
            'kind': 'written',
            'skill': skill['id'],
            'practicum': skill['practicum'],
            'block': block_id,
            'reference': archive_reference(block),
            'marks': marks,
            'calculator': block.get('calculator'),
            # Не «сколько указано в корпусе плюс одна», а сколько страниц
            # вопрос занимает на самом деле: подсказка корпуса шумит.
            'pages': len(block_page_numbers(block, 'question')),
            # На экзамене примерно минута на балл; на бумаге пишут медленнее,
            # чем набирают, поэтому запас щедрее.
            'budget_ms': marks * 90_000,
        }
        return shown, {'kind': 'graded'}, None

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
