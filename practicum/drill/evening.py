"""Вечерний набор: одна кнопка, лист заданий, одна загрузка, разбор всего.

Три режима тренажёра устроены под короткие заходы: вопрос — ответ — вопрос.
Разбор письменной работы так не работает. Бумага, ручка и полчаса тишины
плохо сочетаются с экраном, который ждёт ответа после каждой задачи, и
загрузка на каждый вопрос — это ровно то трение, из-за которого режим
не использовали.

Вечер устроен иначе. Одна кнопка выдаёт лист: все вопросы разом, одним
PDF, который открывается с телефона или печатается. Экран после этого не
нужен вовсе. Работа делается на бумаге, присылается одним сканом, и
разбор приходит на всё сразу.

Набор живёт в базе, а не в браузере: задания берут в семь вечера, а
работу присылают в десять и с другого устройства.

Меряется вечер минутами, а не числом задач. На экзамене примерно минута
на балл, так что сорок минут — это сорок баллов, а сколько это вопросов,
решает набор.
"""
from __future__ import annotations

import random
import string
import time

from drill import archive, engine

# На экзамене примерно минута на балл.
MARKS_PER_MINUTE = 1.0

# Медиана цены вопроса в архиве — три балла, и вечер из одних таких
# превращается в тринадцать мелочей. Крупные вопросы дают тот же счёт
# шестью-восемью настоящими задачами, и подписывать страницы легче.
PREFERRED = (4, 12)
SMALL = (1, 3)

# Насколько можно промахнуться мимо заказанного времени.
OVERSHOOT = 3
MAX_QUESTIONS = 12
MIN_MINUTES = 10
MAX_MINUTES = 180

ALPHABET = string.ascii_lowercase + string.digits


def new_id(rng=None):
    """Короткий ключ набора: он попадает в ссылку и на лист заданий."""
    rng = rng or random.Random()
    return ''.join(rng.choice(ALPHABET) for _ in range(8))


def _pick(bank, states, rng, used_blocks, used_skills, band):
    """Один вопрос: приём выбирает планировщик, вопрос — вилка по цене."""
    pool = engine.candidates(bank, 'written', {}, marks=band)
    if not pool:
        return None
    fresh = [(skill, kind) for skill, kind in pool
             if skill['id'] not in used_skills]
    now = time.time()
    weights = [engine.weight(skill, states.get(skill['id']), bank['share'],
                             now)
               for skill, _ in (fresh or pool)]
    skill, _ = rng.choices(fresh or pool, weights=weights, k=1)[0]
    blocks = engine.matching_blocks(bank, skill, marks=band,
                                    avoid=used_blocks)
    if not blocks:
        return None
    return skill, rng.choice(blocks)


def assemble(bank, states, minutes, rng=None):
    """Набирает вопросы примерно на заказанное время.

    Приёмы берутся тем же весом, что и в перемешке: доля баллов практикума,
    просадка, трудность. Один приём в вечер попадает один раз — вечер на
    сорок баллов должен пройти по разным местам, а не долбить одно.
    """
    rng = rng or random.Random()
    target = max(MIN_MINUTES, min(int(minutes), MAX_MINUTES)) * MARKS_PER_MINUTE
    used_blocks, used_skills, questions, total = set(), set(), [], 0

    while total < target and len(questions) < MAX_QUESTIONS:
        left = target - total
        # Пока времени много, берём крупные вопросы; под конец — те, что
        # в остаток влезают, иначе вечер всегда перебирает на пять баллов.
        band = PREFERRED if left >= PREFERRED[0] else (
            SMALL[0], max(SMALL[0], int(left) + 1))
        got = _pick(bank, states, rng, used_blocks, used_skills, band)
        if got is None and band != SMALL:
            got = _pick(bank, states, rng, used_blocks, used_skills, SMALL)
        if got is None:
            break
        skill, block_id = got
        block = bank['archive'][block_id]
        price = block.get('marks') or 0
        if total and total + price > target + OVERSHOOT:
            break
        used_blocks.add(block_id)
        used_skills.add(skill['id'])
        total += price
        questions.append({
            'n': len(questions) + 1,
            'block': block_id,
            'skill': skill['id'],
            'skill_name': skill['name'],
            'practicum': skill['practicum'],
            'marks': price,
            'paper': block.get('paper'),
            'calculator': block.get('calculator'),
            'reference': archive.reference(block),
        })

    if not questions:
        raise LookupError('не нашлось ни одного вопроса под этот набор')
    return questions, total


def minutes_for(questions):
    """Сколько времени набор просит по числу баллов."""
    return int(round(sum(q['marks'] or 0 for q in questions)
                     / MARKS_PER_MINUTE))


def split_by_question(pages, count):
    """Раскладка страниц по вопросам, когда номер прочитать не удалось.

    Не догадка, а честное «поровну по порядку»: экран подтверждения всё
    равно показывает раскладку, и поправить её — одно нажатие. Пустая
    раскладка была бы хуже: пришлось бы расставлять всё руками.
    """
    if not pages or count <= 0:
        return []
    per = max(1, round(len(pages) / count))
    out = []
    for index in range(len(pages)):
        out.append(min(count, index // per + 1))
    return out


def group_pages(pages):
    """{номер вопроса: [индексы страниц]} — в порядке страниц."""
    groups = {}
    for page in pages:
        question = page.get('question')
        if question:
            groups.setdefault(int(question), []).append(page)
    return groups
