"""Проверяет механику kit.data: сводные числа, ящик с усами, прямую и r.

Тест ноутбука (verify_d7.py) сверяет ответы тринадцати заданий. Здесь —
то, на чём эти проверки стоят и что в заданиях не видно:

- прямая, найденная поиском по дну суммы квадратов, совпадает с формулой
  Sxy/Sxx на случайных наборах — и насколько точно;
- квартили считаются так, как их считает GDC в IB: при нечётном n медиана
  не входит ни в одну половину;
- «выбросов нет» — это неравенство, и его решение — отрезок;
- r не меняется от сдвига и растяжения и меняет знак от отражения;
- набор с невидимой частью (Bunch) отдаёт сумму и края, но не медиану.

Запуск:  python practicum/tests/test_kit_data.py
"""
import contextlib
import io
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp

import kit
from kit import (Bunch, Box, Pairs, Sample, centre, clean, deviation, fence, fit,
                 iqr, mean, median, quartiles, size, skew, spread, strength)

kit.language('en')
ok, bad = [], []


def check(name, got, expect=True):
    (ok if got == expect else bad).append(name)
    if got != expect:
        print(f'  ПРОВАЛ {name}: {got!r}')


def said(call, *args, **kwargs):
    """Что проверка напечатала, и приняла ли ответ."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        verdict = call(*args, **kwargs)
    return verdict, buffer.getvalue()


def formula(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    sxx = sum((a - mx) ** 2 for a in xs)
    syy = sum((b - my) ** 2 for b in ys)
    return sxy / sxx, my - sxy / sxx * mx, sxy / (sxx * syy) ** 0.5


print('=== поиск против формулы ===')
random.seed(7)
worst = 0.0
for trial in range(40):
    n = random.randint(4, 14)
    shift = random.choice([0, 50, 1000])          # далёкие x — худший случай поиска
    xs = [shift + random.uniform(0, 30) for _ in range(n)]
    ys = [random.uniform(-5, 5) + random.choice([-2, 0.3, 1.7]) * a for a in xs]
    a, b = fit(Pairs(xs, ys))
    fa, fb, fr = formula(xs, ys)
    worst = max(worst, abs(a - fa) / max(1, abs(fa)), abs(b - fb) / max(1, abs(fb)))
    check(f'r совпал с формулой, набор {trial}', abs(strength(Pairs(xs, ys)) - fr) < 1e-7)
# Дно параболы по её значениям видно лишь с точностью √ε ≈ 10⁻⁸ от масштаба;
# трём значащим цифрам нужно 5·10⁻⁴ — запас больше двух порядков.
check('наклон и свободный член совпали с формулой до 10⁻⁵', worst < 1e-5)
print(f'  наибольшее расхождение с формулой: {worst:.1e}')

print('=== две прямые ===')
demo = Pairs([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
a, b = fit(demo)
c, d = fit(demo, of='x')
check('y на x: 0.6x + 2.2', (round(a, 6), round(b, 6)) == (0.6, 2.2))
check('x на y: y − 1', (round(c, 6), round(d, 6)) == (1.0, -1.0))
check('x на y — не обращённая y на x', abs(c - 1 / a) > 0.1)
check('обе проходят через точку средних',
      abs(a * 3 + b - 4) < 1e-7 and abs(c * 4 + d - 3) < 1e-7)
check('точка средних точная', centre(demo) == (3, 4))
check('r² — произведение наклонов двух прямых', abs(strength(demo) ** 2 - a * c) < 1e-7)

print('=== r ===')
down = Pairs([1, 2, 3, 4], [8, 6, 5, 1])
check('знак r — знак наклона', strength(down) < 0 and fit(down)[0] < 0)
moved = Pairs([v * 3 + 100 for v in [1, 2, 3, 4, 5]], [2, 4, 5, 4, 5])
check('сдвиг и растяжение не меняют r', abs(strength(moved) - strength(demo)) < 1e-9)
flipped = Pairs([-v for v in [1, 2, 3, 4, 5]], [2, 4, 5, 4, 5])
check('отражение меняет знак r', abs(strength(flipped) + strength(demo)) < 1e-9)
line = Pairs([1, 2, 3], [5, 7, 9])
check('точки на прямой: r = 1', abs(strength(line) - 1) < 1e-9)
flat = Pairs([1, 2, 3], [4, 4, 4])
try:
    strength(flat)
    check('у ровного y r не определён', False)
except ValueError:
    check('у ровного y r не определён', True)

print('=== одна величина ===')
odd = Sample([1, 3, 5, 7, 9, 11, 13])
check('медиана нечётного набора', median(odd) == 7)
check('квартили без медианы в половинах', quartiles(odd) == (3, 11))
even = Sample([2, 4, 6, 8, 10, 12])
check('медиана чётного — середина двух', median(even) == 7)
check('квартили чётного', quartiles(even) == (4, 10))
check('IQR', iqr(even) == 6)
table = Sample({1: 3, 2: 5, 3: 2})
check('таблица частот: n', size(table) == 10)
check('таблица частот: медиана 2', median(table) == 2)
check('таблица частот: среднее 1.9', mean(table) == sp.Rational(19, 10))
check('таблица частот: σ = 0.7', deviation(table) == sp.Rational(7, 10))
check('размах', spread(odd) == 12)
check('3.3 хранится точно', mean(Sample([3.3, 6.9])) == sp.Rational(51, 10))

p = sp.Symbol('p')
check('буква в наборе даёт выражение', mean(Sample([12, 15, p, 18, 20])) == (65 + p) / 5)
with_bunch = Sample([Bunch(28, average=10.5, lowest=6, highest=17), 5, 19])
check('Bunch: n', size(with_bunch) == 30)
check('Bunch: среднее', mean(with_bunch) == sp.Rational(53, 5))
check('Bunch: размах', spread(with_bunch) == 14)
try:
    median(with_bunch)
    check('Bunch не отдаёт медиану', False)
except ValueError:
    check('Bunch не отдаёт медиану', True)
x = sp.Symbol('x')
try:
    median(Sample({2: 5, 6: x}))
    check('буква в частоте не даёт медианы', False)
except ValueError:
    check('буква в частоте не даёт медианы', True)

print('=== ящик с усами ===')
box = Box(3, 8, 11, 14, 25)
check('границы', fence(box) == (-1, 23))
check('25 за границей: выбросы есть', clean(box) is sp.false)
check('без выброса — есть', clean(Box(3, 8, 11, 14, 22)) is sp.true)
check('хвост справа', skew(Box(3, 8, 10, 14, 25)) == 'positive')
check('у этой коробки хвоста нет', skew(box) == 'none')
check('хвост слева', skew(Box(0, 2, 8, 9, 10)) == 'negative')
check('симметрия', skew(Box(0, 2, 5, 8, 10)) == 'none')
L, U = sp.symbols('L U')
eggs = Box(5, L, 20, U, 44)
region = kit._possible(eggs, U, [sp.Eq(iqr(eggs), 12), clean(eggs)])
# 44 ≤ U + 18 даёт U ≥ 26; нижняя граница даёт U ≤ 35, а L ≤ 20 (квартиль
# не заходит за медиану) — U ≤ 32. Последнее условие в задаче не написано.
check('«нет выбросов» даёт отрезок', region == sp.Interval(26, 32))

print('=== проверки: пустые, неверные формы ===')
verdict, text = said(kit.verify_fit, 't', ..., demo)
check('пустой ответ — ⬜', not verdict and '⬜' in text)
verdict, text = said(kit.verify_fit, 't', 'bad', demo)
check('не прямая — отказ с объяснением', not verdict and 'pair' in text)
verdict, text = said(kit.verify_fit, 't', sp.Eq(sp.Symbol('y'), 0.6 * sp.Symbol('x') + 2.2), demo)
check('прямая уравнением принимается', verdict)
verdict, text = said(kit.verify_fit, 't', (1, -1), demo, of='x')
check('x на y парой принимается', verdict)
verdict, text = said(kit.verify_strength, 't', 1.2, demo)
check('|r| > 1 названо', not verdict and 'never more than 1' in text)
verdict, text = said(kit.verify_strength, 't', 0.77, demo)
check('две цифры названы', not verdict and 'three significant' in text)
verdict, text = said(kit.verify_estimate, 't', 5.2, demo, 5)
check('подстановка принята', verdict)
verdict, text = said(kit.verify_estimate, 't', 5, demo, 5, whole=True)
check('целое принято', verdict)
verdict, text = said(kit.verify_missing, 't', 15, Sample([12, 15, p, 18, 20]), mean=16)
check('обратный ход принят', verdict)
verdict, text = said(kit.verify_missing, 't', (1, 2), Sample([12, 15, p, 18, 20]), mean=16)
check('лишнее число названо', not verdict and 'unknowns' in text)
verdict, text = said(kit.verify_bound, 't', 26, eggs, U, 'least',
                     holds=[sp.Eq(iqr(eggs), 12), clean(eggs)])
check('наименьшее U принято', verdict)
verdict, text = said(kit.verify_bound, 't', 30, eggs, U, 'least',
                     holds=[sp.Eq(iqr(eggs), 12), clean(eggs)])
check('середина отрезка названа', not verdict and 'smaller' in text)
verdict, text = said(kit.verify_bound, 't', 32, eggs, U, 'largest',
                     holds=[sp.Eq(iqr(eggs), 12), clean(eggs)])
check('наибольшее U принято', verdict)
verdict, text = said(kit.verify_outlier, 't', 'maybe', box, 25)
check('слово не yes/no — отказ', not verdict and "'yes' or 'no'" in text)
verdict, text = said(kit.verify_reason, 't', 'extrapolation', demo, 3, given='x', predict='y')
check('внутри данных и та прямая — ход годится', not verdict and 'fine here' in text)
verdict, text = said(kit.verify_effect, 't', 'no effect', demo, lambda v: 2 * v + 1)
check('растяжение: no effect', verdict)
verdict, text = said(kit.verify_effect, 't', 'no effect', demo, lambda v: -v)
check('отражение: r меняется', not verdict)
verdict, text = said(kit.verify_centre, 't', (3, 4), demo)
check('точка средних по данным', verdict)

print('=== в kit у каждого имени один дом ===')
check('verify_line остался у векторов', kit.verify_line.__module__ == 'kit.vectors')
check('Freq остался у таблицы', kit.Freq.__module__ == 'kit.table')
check('mean живёт в data', kit.mean.__module__ == 'kit.data')

print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(ok)}/{len(ok) + len(bad)})')
sys.exit(1 if bad else 0)
