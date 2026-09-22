"""Проверяет механику kit.rates: скорость сдвигом, связанные скорости, наилучшее.

Тест ноутбука (verify_e9.py) сверяет ответы четырнадцати заданий. Здесь —
то, на чём эти проверки стоят и что в заданиях не видно:

- скорость, измеренная сдвигом времени, совпадает с производной на
  случайных функциях — и насколько точно;
- в модуле нет ни одного символьного дифференцирования: ни diff, ни
  Derivative, ни idiff — это разбор кода, а не обещание в комментарии;
- «стоит» и «разворачивается» различаются: касание нуля без смены знака;
- наибольшее ищется и на концах, и среди целых;
- связанная скорость не зависит от того, куда поставлена незакреплённая
  величина, а если зависит — проверка отказывается считать.

Запуск:  python practicum/tests/test_kit_rates.py
"""
import ast
import contextlib
import io
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp

import kit
from kit import (Eq, Interval, dt, particle, rate_of, symbols, verify_best, verify_related,
                 verify_when, t, x)

kit.language('en')
ok, bad = [], []


def check(name, got, expect=True):
    (ok if got == expect else bad).append(name)
    if got != expect:
        print(f'  ПРОВАЛ {name}: {got!r}')


def said(call, *args, **kwargs):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        verdict = call(*args, **kwargs)
    return verdict, buffer.getvalue()


print('=== скорость сдвигом против производной ===')
random.seed(9)
worst = 0.0
pieces = [lambda a: sp.sin(a * t), lambda a: sp.exp(a * t / 3), lambda a: t ** 3 - a * t,
          lambda a: sp.log(t + a), lambda a: sp.sqrt(t ** 2 + a)]
for trial in range(40):
    a = random.uniform(0.5, 3)
    f = random.choice(pieces)(a) * random.choice([1, -2, 0.3]) + random.choice(pieces)(a)
    at = random.uniform(0.2, 4)
    want = float(sp.diff(f, t).subs(t, at))
    got = float(rate_of(f)(at))
    worst = max(worst, abs(got - want) / max(1, abs(want)))
check('сдвиг совпал с производной до 10⁻¹⁵ на 40 функциях', worst < 1e-15)
print(f'  наибольшее расхождение: {worst:.1e}')
acc = rate_of(rate_of(t ** 4))
check('скорость скорости — вторая производная', abs(float(acc(2)) - 48) < 1e-9)
edge = rate_of(sp.sqrt(t))
check('у края области мерят с той стороны, где величина есть',
      abs(float(edge(1e-3)) - 0.5 / math.sqrt(1e-3)) < 1e-6)
check('где величины нет, скорости нет', rate_of(sp.sqrt(t))(-1) is None)
combo = rate_of(t ** 2) - rate_of(3 * t)
check('скорости складываются и вычитаются', abs(float(combo(5)) - 7) < 1e-12)

print('=== в модуле нет дифференцирования ===')
tree = ast.parse(open(os.path.join(ROOT, 'practicum/kit/rates.py')).read())
names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | \
        {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
check('ни diff, ни Derivative, ни idiff', names & {'diff', 'Derivative', 'idiff'} == set())

print('=== стоит и разворачивается ===')
touch = particle(v=(t - 2) ** 2 * (t - 5), span=(0, 6))
check('стоит дважды', len(kit._event_moments(touch, 'rest')) == 2)
check('разворачивается один раз', [round(float(m), 9) for m in kit._event_moments(touch, 'turn')]
      == [5.0])
verdict, text = said(verify_when, 't', 2, touch, 'turn')
check('остановка без разворота названа', not verdict and 'keeps its sign' in text)
verdict, text = said(verify_when, 't', 5, touch, 'turn')
check('разворот принят', verdict)
verdict, text = said(verify_when, 't', [2, 5], touch, 'rest', 'all')
check('все остановки списком', verdict)
verdict, text = said(verify_when, 't', [5, 2, 7], touch, 'turn')
check('лишние значения названы', not verdict and 'extra values' in text)

print('=== наибольшее: концы и целые ===')
verdict, _ = said(verify_best, 'b', 6, 3 - x ** 2, (0, 3), 'max', report=abs(3 - x ** 2))
check('модуль больше всего на конце', verdict is False)
fn = kit._quantity_of(sp.Abs(3 - x ** 2), x)
place, value = kit._optimum(fn, 0, 3, 'max')
check('конец отрезка — лучшая точка', float(place) == 3 and float(value) == 6)
place, value = kit._optimum(kit._quantity_of(x * (1 - x), x), 0, 1, 'max', True, True)
check('вершина внутри открытого промежутка', abs(float(place) - 0.5) < 1e-20)
n = sp.Symbol('n')
place, value = kit._optimum(kit._quantity_of(n * sp.Rational(85, 100) ** n, n), 1, 30, 'max',
                            integer=True)
check('целое: n = 6, а не вершина 6.15', place == 6)
verdict, text = said(verify_best, 'w', 6.15, n * sp.Rational(85, 100) ** n, (1, 30), 'max',
                     var=n, report='place', integer=True)
check('вершина вместо целого названа', not verdict and 'whole number' in text)
try:
    said(verify_best, 'o', 1, x ** 2, Interval.open(-1, 1), 'max')
    check('у x² на (−1, 1) наибольшего нет — отказ', False)
except ValueError:
    check('у x² на (−1, 1) наибольшего нет — отказ', True)

print('=== связанные скорости ===')
V, h, y, theta = symbols('V h y theta')
verdict, _ = said(verify_related, 'c', sp.Rational(2, 9), Eq(V, x ** 3), Eq(V, 27), {dt(V): 6},
                  dt(x), where={x: (0, 10)}, exact=True)
check('куб: ds/dt = 2/9 точно', verdict)
verdict, text = said(verify_related, 'c', sp.Rational(1, 27), Eq(V, x ** 3), Eq(V, 27),
                     {dt(V): 6}, dt(x), where={x: (0, 10)})
check('dx/dV без dV/dt названо', not verdict and 'multiply by' in text)
value, _, _, free = kit._related_value([Eq(y, x + 50 * sp.cot(theta))], [Eq(y - x, 10)],
                                       [Eq(dt(y), 2 * dt(x)), Eq(dt(theta), -0.1)], dt(x),
                                       {theta: (0, sp.pi / 2)})
check('лодки: одна величина не закреплена', len(free) == 1)
again = kit._related_value([Eq(y, x + 50 * sp.cot(theta))], [Eq(y - x, 10)],
                           [Eq(dt(y), 2 * dt(x)), Eq(dt(theta), -0.1)], dt(x),
                           {theta: (0, sp.pi / 2)}, pin_value=37)[0]
check('и ответ от него не зависит', abs(value - again) < 1e-30)
try:
    said(verify_related, 'u', 1, Eq(y, x * theta), Eq(theta, 1), {dt(x): 1}, dt(y))
    check('незакреплённый момент — отказ', False)
except ValueError:
    check('незакреплённый момент — отказ', True)
try:
    said(verify_related, 'm', 1, Eq(V, h ** 2), Eq(V, 4), {dt(V): 1}, dt(h))
    check('два состояния без where — отказ', False)
except ValueError:
    check('два состояния без where — отказ', True)

print('=== в kit у каждого имени один дом ===')
check('distance остался у векторов', kit.distance.__module__ == 'kit.vectors')
check('verify_optimum остался у векторов', kit.verify_optimum.__module__ == 'kit.vectors')
check('rate_of живёт в rates', kit.rate_of.__module__ == 'kit.rates')

print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(ok)}/{len(ok) + len(bad)})')
sys.exit(1 if bad else 0)
