"""Сила приёма: стойкость, свежесть и число на карте.

Ящики Лейтнера отвечали на один вопрос — показывать сегодня или нет.
Карта приёмов требует большего: насколько приём отточен, а это две разные
величины, и путать их нельзя.

**Стойкость** `S` — через сколько дней приём просядет до девяноста
процентов. Растёт от повторений, сама по себе не падает.

**Свежесть** `R` — сколько от стойкости осталось сейчас. Падает со
временем по степенному закону, при `t = S` даёт ровно 0.9.

Число в квадрате — произведение одного на другое. Только свежесть врёт
наутро после занятия: приём, повторённый вчера впервые, и приём, который
отрабатывали полгода, оба покажут сто. Только стойкость врёт в другую
сторону: она не знает, что три месяца ничего не повторяли.

Всё здесь — чистые функции от `(S, D, когда отвечали)`. Ничего не
пересчитывается по расписанию: карта затухает правильно, даже если её
не открывать полгода.
"""
from __future__ import annotations

import math

# Через сколько дней приём считается отточенным до конца. Экзамен в мае,
# и приём, который держится четыре месяца, до него доживёт.
HORIZON = 120.0

# Общий множитель прироста. Подобран так, чтобы повторение точно в срок
# на ранней лестнице примерно удваивало стойкость.
GAIN = 25.0

# Первая встреча: с какой стойкости начинается приём.
FIRST_STABILITY = {'again': 0.4, 'hard': 0.9, 'good': 2.3, 'easy': 5.0}
FIRST_DIFFICULTY = {'again': 7.9, 'hard': 6.7, 'good': 5.5, 'easy': 4.3}

# Оценка меняет прирост.
GRADE_BUMP = {'hard': 0.6, 'good': 1.0, 'easy': 1.3}
GRADE_RANK = {'again': 1, 'hard': 2, 'good': 3, 'easy': 4}

# Свидетельства весят по-разному. Узнавание — выбор из шести-девяти
# кнопок, и одиннадцать-семнадцать процентов попаданий там даёт слепое
# тыканье. Счёт ответ набирают руками. Разбор письменной работы ближе
# всего к экзамену и весит больше всех.
KIND_WEIGHT = {'recognition': 0.6, 'compute': 1.0, 'written': 1.4}

# Разбор письменной работы оценивается не временем, а долей баллов:
# секундомер там меряет, как быстро человек пишет от руки, и знания
# это не показывает.
WRITTEN_BANDS = ((0.9, 'easy'), (0.7, 'good'), (0.5, 'hard'))

MIN_STABILITY = 0.5
MAX_STABILITY = 3650.0
MIN_GROWTH = 1.05       # повторение не бывает совсем даром
LAPSE_KEEP = 0.6        # переучивать быстрее, чем учить
DAY = 86400.0


def retrievability(stability, days):
    """Сколько осталось от стойкости через `days` дней.

    Степенной закон, а не показательный: у забывания длинный хвост, и на
    больших сроках показательный обрывает его слишком рано.
    """
    if not stability or stability <= 0:
        return 0.0
    return 1.0 / (1.0 + max(days, 0.0) / (9.0 * stability))


def maturity(stability):
    """Насколько приём приблизился к горизонту. Логарифм, а не доля:
    первые дни стойкости стоят дороже, чем сотые."""
    if not stability or stability <= 0:
        return 0.0
    return min(1.0, math.log1p(stability) / math.log1p(HORIZON))


def score(stability, days):
    """Число в квадрате, 0…100. Свежесть, умноженная на глубину."""
    return 100.0 * retrievability(stability, days) * maturity(stability)


def grade(ok, ms, budget_ms):
    """Оценка попытки по верности и времени.

    Время до сих пор писалось в журнал и не использовалось никем.
    Верно-но-втрое-дольше-бюджета — это не то же знание, что верно и в
    срок: на экзамене второе стоит баллов, а первое их стоит.
    """
    if not ok:
        return 'again'
    if not budget_ms or budget_ms <= 0:
        return 'good'
    if ms > budget_ms:
        return 'hard'
    if ms <= 0.4 * budget_ms:
        return 'easy'
    return 'good'


def grade_written(earned, available):
    """Оценка письменной работы по доле набранных баллов."""
    if not available:
        return None
    share = max(earned or 0, 0) / float(available)
    for edge, mark in WRITTEN_BANDS:
        if share >= edge:
            return mark
    return 'again'


def first_state(mark):
    """Приём, который видят впервые."""
    return FIRST_STABILITY[mark], FIRST_DIFFICULTY[mark]


def next_difficulty(difficulty, mark):
    """Трудность ползёт от оценок и понемногу тянется обратно к середине.

    Без возврата к середине один плохой день навсегда метит приём как
    трудный, и он потом годами получает прирост меньше заслуженного.
    """
    moved = difficulty - 1.0 * (GRADE_RANK[mark] - 3)
    moved = 0.95 * moved + 0.05 * 5.0
    return min(10.0, max(1.0, moved))


def next_stability(stability, difficulty, days, mark, kind='compute'):
    """Стойкость после ответа.

    Прирост пропорционален `1 − R`: дорого стоит повторение, сделанное
    тогда, когда приём уже поплыл. Повторение сразу после предыдущего
    почти ничего не даёт — отсюда сам собой берётся эффект интервала,
    и зубрёжку не нужно запрещать отдельно, она просто не работает.

    Множитель `S^-0.3` гасит прирост у того, что и так держится долго:
    поднять с двух дней до пяти легко, с двухсот до пятисот — нет.
    """
    if mark == 'again':
        # Не в ноль: приём со стойкостью в шестьдесят дней падает до пяти,
        # а не до одного. Ящики Лейтнера роняли и то и другое одинаково.
        return max(MIN_STABILITY, LAPSE_KEEP * math.sqrt(stability))
    fresh = retrievability(stability, days)
    growth = 1.0 + (GAIN
                    * ((11.0 - difficulty) / 9.0)
                    * stability ** -0.3
                    * (1.0 - fresh)
                    * GRADE_BUMP[mark]
                    * KIND_WEIGHT.get(kind, 1.0))
    return min(MAX_STABILITY, stability * max(growth, MIN_GROWTH))


def step(stability, difficulty, last_ts, now, mark, kind='compute'):
    """Новое состояние приёма по готовой оценке.

    Возвращает `(стойкость, трудность)`. `stability is None` — приём
    видят впервые.
    """
    if stability is None or last_ts is None:
        return first_state(mark)
    days = max(now - last_ts, 0.0) / DAY
    difficulty = next_difficulty(difficulty, mark)
    return next_stability(stability, difficulty, days, mark, kind), difficulty


def advance(stability, difficulty, last_ts, now, *, ok, ms, budget_ms,
            kind='compute'):
    """То же по итогу попытки в тренажёре. Оценку выводит из времени."""
    mark = grade(ok, ms, budget_ms)
    stability, difficulty = step(stability, difficulty, last_ts, now, mark,
                                 kind)
    return stability, difficulty, mark


def due_at(last_ts, stability):
    """Когда приём просядет до девяноста процентов. По построению `S`
    это и есть срок, поэтому никаких таблиц интервалов больше нет —
    и потолка в двадцать один день тоже."""
    return last_ts + stability * DAY


def snapshot(state, now):
    """Всё, что карта показывает про один приём.

    `state is None` — ни одной попытки. Это не ноль: «не начинал» и
    «забыл» — разные болезни, и на карте у них разный цвет.
    """
    if state is None or state.get('last_ts') is None:
        return {'score': None, 'stability': None, 'retrievability': None,
                'difficulty': None, 'days_since': None, 'due_in_days': None}
    stability = state.get('stability') or 0.0
    days = max(now - state['last_ts'], 0.0) / DAY
    due = due_at(state['last_ts'], stability)
    return {
        'score': round(score(stability, days)),
        'stability': round(stability, 1),
        'retrievability': round(retrievability(stability, days), 3),
        'difficulty': round(state.get('difficulty') or 5.0, 1),
        'days_since': round(days, 1),
        'due_in_days': round((due - now) / DAY, 2),
    }
