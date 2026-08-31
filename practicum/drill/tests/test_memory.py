"""Проверка модели силы приёма.

Формулы легко подобрать так, что числа выглядят правдоподобно, а формы
неверны. Здесь проверяются именно формы: что повторение позже стоит
дороже, чем раньше; что зубрёжка почти ничего не даёт; что ошибка
роняет, но не в ноль; что число не показывает сто наутро после первой
встречи. Числовые границы взяты с запасом — подкрутка постоянных не
должна ронять набор, а вот смена знака должна.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from drill import memory  # noqa: E402

passed = failed = 0


def t(name, ok):
    global passed, failed
    print(('  ✅ ' if ok else '  ❌ ') + name)
    if ok:
        passed += 1
    else:
        failed += 1


def ladder(marks, kind='compute', gap=None):
    """Прогон повторений: gap=None — точно в срок, иначе столько дней."""
    stability = difficulty = None
    last, now = None, 0.0
    for mark in marks:
        step = (stability if gap is None else gap) or 0.0
        now = 0.0 if last is None else last + step * memory.DAY
        stability, difficulty = memory.step(stability, difficulty, last, now,
                                            mark, kind)
        last = now
    return stability, difficulty


print('=== свежесть ===')
t('при t = S свежесть ровно 0.9',
  abs(memory.retrievability(10.0, 10.0) - 0.9) < 1e-9)
t('в момент ответа свежесть единица',
  memory.retrievability(10.0, 0.0) == 1.0)
t('свежесть падает монотонно',
  all(memory.retrievability(10.0, d) > memory.retrievability(10.0, d + 1)
      for d in range(0, 200)))
t('стойче — значит падает медленнее',
  memory.retrievability(60.0, 30.0) > memory.retrievability(6.0, 30.0))
t('без стойкости свежести нет', memory.retrievability(None, 1.0) == 0.0)

print('\n=== число в квадрате ===')
t('приём, взятый впервые, не показывает сто',
  memory.score(*memory.first_state('good')[:1], 0.0) < 30)
t('отточенный приём показывает почти сто',
  memory.score(memory.HORIZON, 0.0) > 95)
t('число падает от простоя',
  memory.score(20.0, 0.0) > memory.score(20.0, 30.0))
t('глубокий приём после месяца лучше свежего после месяца',
  memory.score(60.0, 30.0) > memory.score(3.0, 30.0))
t('нулевая стойкость даёт ноль', memory.score(0.0, 0.0) == 0.0)
t('число не выходит за сто',
  all(memory.score(s, 0.0) <= 100.0 for s in (1, 10, 120, 1000, 3650)))

print('\n=== оценка по времени ===')
t('неверно — это always again', memory.grade(False, 1, 10_000) == 'again')
t('верно и вчетверо быстрее бюджета — easy',
  memory.grade(True, 3_000, 10_000) == 'easy')
t('верно в бюджете — good', memory.grade(True, 7_000, 10_000) == 'good')
t('верно, но дольше бюджета — hard',
  memory.grade(True, 14_000, 10_000) == 'hard')
t('без бюджета оценка не выдумывается',
  memory.grade(True, 99_000, 0) == 'good')

print('\n=== разбор письменной работы ===')
t('почти всё взято — easy', memory.grade_written(9, 9) == 'easy')
t('больше семи десятых — good', memory.grade_written(6, 8) == 'good')
t('половина — hard', memory.grade_written(3, 6) == 'hard')
t('меньше половины — again', memory.grade_written(2, 6) == 'again')
t('без баллов оценки нет', memory.grade_written(0, 0) is None)

print('\n=== эффект интервала ===')
spaced, _ = ladder(['good'] * 5)
crammed, _ = ladder(['good'] * 5, gap=1.0)
t('пять повторений в срок дают куда больше пяти подряд',
  spaced > 3 * crammed)
t('повторение вплотную почти не поднимает стойкость',
  memory.next_stability(60.0, 5.5, 0.0, 'good')
  < 60.0 * memory.MIN_GROWTH + 1e-9)
t('позднее повторение поднимает сильнее, чем раннее',
  memory.next_stability(60.0, 5.5, 180.0, 'good')
  > memory.next_stability(60.0, 5.5, 60.0, 'good'))
t('прирост затухает с ростом стойкости',
  memory.next_stability(5.0, 5.5, 5.0, 'good') / 5.0
  > memory.next_stability(200.0, 5.5, 200.0, 'good') / 200.0)

print('\n=== оценка меняет прирост ===')
base = memory.next_stability(10.0, 5.5, 10.0, 'good')
t('easy поднимает выше good',
  memory.next_stability(10.0, 5.5, 10.0, 'easy') > base)
t('hard поднимает ниже good',
  memory.next_stability(10.0, 5.5, 10.0, 'hard') < base)
t('трудный приём поднимается меньше лёгкого',
  memory.next_stability(10.0, 9.0, 10.0, 'good')
  < memory.next_stability(10.0, 2.0, 10.0, 'good'))

print('\n=== вес свидетельства ===')
recog, _ = ladder(['good'] * 6, kind='recognition')
compute, _ = ladder(['good'] * 6, kind='compute')
written, _ = ladder(['good'] * 6, kind='written')
t('узнавание поднимает медленнее счёта', recog < compute)
t('счёт медленнее письменной работы', compute < written)
t('шесть узнаваний не дотягивают до горизонта', recog < memory.HORIZON)

print('\n=== ошибка ===')
t('ошибка роняет стойкость',
  memory.next_stability(60.0, 5.5, 60.0, 'again') < 60.0)
t('но не в ноль',
  memory.next_stability(60.0, 5.5, 60.0, 'again') > 3.0)
t('переучивать легче, чем учить с нуля',
  memory.next_stability(60.0, 5.5, 60.0, 'again')
  > memory.FIRST_STABILITY['good'])
t('глубокий приём после ошибки падает выше мелкого',
  memory.next_stability(200.0, 5.5, 1.0, 'again')
  > memory.next_stability(4.0, 5.5, 1.0, 'again'))
t('стойкость не уходит ниже пола',
  memory.next_stability(0.5, 5.5, 1.0, 'again') >= memory.MIN_STABILITY)

print('\n=== трудность ===')
t('ошибка делает приём труднее',
  memory.next_difficulty(5.5, 'again') > 5.5)
t('лёгкий ответ делает приём легче',
  memory.next_difficulty(5.5, 'easy') < 5.5)
t('трудность не выходит за края',
  all(1.0 <= memory.next_difficulty(d, m) <= 10.0
      for d in (1.0, 5.5, 10.0) for m in memory.GRADE_RANK))
t('трудность тянется обратно к середине',
  memory.next_difficulty(10.0, 'good') < 10.0
  and memory.next_difficulty(1.0, 'good') > 1.0)

print('\n=== срок ===')
stability, _ = ladder(['good'] * 4)
t('срок — это сама стойкость',
  abs(memory.due_at(0.0, stability) - stability * memory.DAY) < 1e-6)
t('потолка в двадцать один день больше нет',
  ladder(['good'] * 8)[0] > 21.0)
t('в срок свежесть как раз девять десятых',
  abs(memory.retrievability(stability, stability) - 0.9) < 1e-9)

print('\n=== снимок для карты ===')
t('без попыток снимок пустой, а не нулевой',
  memory.snapshot(None, 0.0)['score'] is None)
t('состояние без времени ответа тоже пустое',
  memory.snapshot({'stability': 5.0, 'last_ts': None}, 0.0)['score'] is None)
snap = memory.snapshot({'stability': 20.0, 'difficulty': 5.5,
                        'last_ts': 0.0}, 10 * memory.DAY)
t('снимок считает число, стойкость и срок',
  snap['score'] > 0 and snap['stability'] == 20.0
  and abs(snap['days_since'] - 10.0) < 1e-6
  and abs(snap['due_in_days'] - 10.0) < 1e-6)

print(f'\n{passed} проверок пройдено, {failed} провалено')
sys.exit(1 if failed else 0)
