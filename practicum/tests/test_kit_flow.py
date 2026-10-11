"""Проверяет механику kit.flow: поле, подстановка, кривая ногами, ломаная.

Тест архива (check_archive_e7.py) сверяет шестьдесят девять ответов. Здесь —
то, на чём эти проверки стоят и чего в ответах не видно:

- в модуле ни разу не вызывается dsolve: проверка не решает уравнение, она
  подставляет в него — это разбор кода, а не обещание в комментарии;
- счёт по полю совпадает с замкнутой формой там, где форма известна, и
  работает в обе стороны по x;
- ломаная Эйлера совпадает с итерацией, посчитанной руками, и не округляет
  по дороге;
- знак ошибки Эйлера согласован с вогнутостью решения: занижает там, где
  выгиб вверх, и завышает там, где вниз;
- неявный ответ проходит в любой эквивалентной записи, а семейство, которое
  лишь касается верного в одной точке, отвергается;
- потерянная постоянная интегрирования отличает частное решение от общего;
- интегрирующий множитель годится с любой постоянной;
- отказы: шаг не делит промежуток, в поле осталась буква, уравнение не
  линейно, перегиба на промежутке нет.

Запуск:  python practicum/tests/test_kit_flow.py
"""
import ast
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import mpmath as mp
import sympy as sp

import kit
from kit import (Eq, cos, exp, log, put, sin, sqrt, symbols, t, verify_curvature,
                 verify_euler, verify_factor, verify_family, verify_inflexion,
                 verify_letter, verify_ode, verify_second_order, verify_solved,
                 verify_substitution, verify_system, x, y)

kit.language('en')
A, B, C, D, F, G, Y, a, k, m, v, w = symbols('A B C D F G Y a k m v w')
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


print('=== проверка не решает уравнение, а подставляет в него ===')
source = open(os.path.join(ROOT, 'practicum/kit/flow.py')).read()
tree = ast.parse(source)
called = {node.func.attr for node in ast.walk(tree)
          if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
called |= {node.func.id for node in ast.walk(tree)
           if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
for name in ('dsolve', 'idiff', 'odesimp'):
    check(f'{name} в модуле не вызывается', name not in called)
check('sp.diff вызывается (невязка берётся подстановкой)', 'diff' in called)

print('=== счёт по полю против замкнутой формы ===')
cases = [
    ('dy/dx = y',            y,              (0, 1),  2.0,  sp.exp(2)),
    ('dy/dx = (4-y)/10',     (4 - y) / 10,   (0, 2),  5.0,  4 - 2 * sp.exp(-sp.Rational(1, 2))),
    ('dy/dx = x + y',        x + y,          (0, 2),  1.5,  3 * sp.exp(sp.Rational(3, 2)) - 2.5),
    ('назад по x',           x + y,          (0, 2),  -1.0, 3 * sp.exp(-1) + 0.0),
    ('dy/dx = cos x',        cos(x),         (0, 0),  1.0,  sp.sin(1)),
]
worst = 0.0
for name, rhs, start, where, want in cases:
    got = float(kit.flow._curve_of(rhs, start, x, y)(where))
    want = float(sp.N(want))
    worst = max(worst, abs(got - want) / max(abs(want), 1.0))
    check(f'поле: {name}', abs(got - want) <= 1e-12 * max(abs(want), 1.0))
print(f'  худшее относительное расхождение {worst:.2e}')

print('=== ломаная Эйлера против итерации руками ===')
here, there = 0.0, 2.0
for _ in range(5):
    there += 0.1 * (4 - there) / 10
    here += 0.1
check('пять шагов (4-y)/10 из (0, 2)', abs(there - 2.0980199) < 1e-7)
check('проверка берёт ту же ломаную',
      said(verify_euler, 'e', round(there, 4), (4 - y) / 10, (0, 2), 0.1, 0.5,
           digits=4)[0])
verdict, words = said(verify_euler, 'e', 2.098, (4 - y) / 10, (0, 2), 0.1, 0.5,
                      digits=4, report='error')
check('ошибка ломаной — не ноль', not verdict and '0.000479' not in words)
check('и она же названа верно',
      said(verify_euler, 'e', 0.000479, (4 - y) / 10, (0, 2), 0.1, 0.5,
           report='error')[0])
verdict, words = said(verify_euler, 'e', 2.1, (4 - y) / 10, (0, 2), 0.1, 0.5, digits=4)
check('округление по дороге названо по имени', 'rounded' in words or 'accurate' in words)

print('=== знак ошибки согласован с вогнутостью ===')
for name, rhs, start, step, where, sense, bend in (
        ('выгиб вверх', (x ** 2 * y - y) / (x ** 2 + 1), (0, 3), 0.03, 0.15, 'under', 'up'),
        ('выгиб вниз', 2 * x / (x ** 2 + y), (1, 0), 0.25, 2, 'over', 'down')):
    check(f'{name}: ломаная {sense}',
          said(verify_euler, 's', sense, rhs, start, step, where, report='sense')[0])
    check(f'{name}: вогнутость {bend}',
          said(verify_curvature, 'b', bend, rhs, start, (start[0], where))[0])
    other = 'over' if sense == 'under' else 'under'
    check(f'{name}: обратный знак отвергнут',
          said(verify_euler, 's', other, rhs, start, step, where, report='sense')[0],
          False)

print('=== неявный ответ проходится ногами ===')
for name, shape in (('x² + y² = k', Eq(x ** 2 + y ** 2, k)),
                    ('y² = k − x²', Eq(y ** 2, k - x ** 2)),
                    ('(x² + y²)² = k', Eq((x ** 2 + y ** 2) ** 2, k)),
                    ('без Eq, как выражение', x ** 2 + y ** 2 - k)):
    check(f'та же окружность: {name}', said(verify_family, 'f', shape, -x / y)[0])
check('знак наоборот отвергнут',
      said(verify_family, 'f', Eq(x ** 2 - y ** 2, k), -x / y)[0], False)
verdict, words = said(verify_family, 'f', Eq(x ** 2 + y ** 2, 9), -x / y, ic=(2, 0))
check('семейство верное, постоянная чужая — отвергнуто', not verdict)
check('и сказано, что дело в постоянной', 'constant' in words)
check('ответ без y отвергнут', said(verify_family, 'f', Eq(x ** 2, k), -x / y)[0], False)

print('=== постоянная интегрирования — часть ответа ===')
check('общее решение проходит', said(verify_ode, 'g', x ** 2 - 2 * x - 3 + C * exp(-x),
                                     x ** 2 - y - 5, letters=1)[0])
verdict, words = said(verify_ode, 'g', x ** 2 - 2 * x - 3, x ** 2 - y - 5, letters=1)
check('частное решение не проходит', not verdict)
check('и промах назван', 'constant of integration' in words)
check('без letters то же частное решение принимается',
      said(verify_ode, 'g', x ** 2 - 2 * x - 3, x ** 2 - y - 5)[0])
check('второй порядок: одна экспонента из двух не проходит',
      said(verify_second_order, 'o', F * exp(3 * t), (1, -2, -3), letters=2)[0], False)

print('=== интегрирующий множитель с любой постоянной ===')
field = y / sin(2 * x) + sqrt(sp.tan(x))
for factor in (sqrt(sp.cot(x)), 5 * sqrt(sp.cot(x)), -sqrt(sp.cot(x)) / 3):
    check(f'множитель {factor}', said(verify_factor, 'i', factor, field)[0])
check('перевёрнутый множитель отвергнут',
      said(verify_factor, 'i', sqrt(sp.tan(x)), field)[0], False)

print('=== подстановка y = vx ===')
check('x·dv/dx = v² − v − 2',
      said(verify_substitution, 'u', v ** 2 - v - 2, (y ** 2 - 2 * x ** 2) / x ** 2)[0])
verdict, words = said(verify_substitution, 'u', v ** 2 - 2,
                      (y ** 2 - 2 * x ** 2) / x ** 2)
check('потерянное v названо', not verdict and 'term v is missing' in words)

print('=== отказы ===')
for name, call, args, kwargs in (
        ('шаг не делит промежуток', verify_euler,
         ('e', 1, y, (0, 1), 0.3, 1), {}),
        ('шагов больше, чем в вопросе', verify_euler,
         ('e', 1, y, (0, 1), 0.0001, 1), {}),
        ('в поле осталась буква', verify_solved,
         ('s', 1, a * y, (0, 1), 1), {}),
        ('уравнение не линейно по y', verify_factor,
         ('i', x, y ** 2 + x), {}),
        ('перегиба на промежутке нет', verify_inflexion,
         ('p', 1, y, (0, 1), (0.1, 0.9)), {}),
        ('report не из трёх', verify_euler,
         ('e', 1, y, (0, 1), 0.5, 1), {'report': 'guess'}),
        ('модель не решается относительно буквы', verify_letter,
         ('l', 1, exp(k * x) + log(k) + sin(k), k, (1, 0)), {})):
    try:
        said(call, *args, **kwargs)
        check(name, False)
    except ValueError:
        check(name, True)

print('=== незаполненный ответ ===')
check('put на пустом ответе остаётся пустым', put(x + A, A=Ellipsis) is Ellipsis)
check('put подставляет ответ', put(x + A, A=2) == x + 2)
verdict, words = said(verify_solved, 's', Ellipsis, y, (0, 1), 1)
check('пустой ответ — не провал проверки', not verdict and '⬜' in words)
verdict, words = said(verify_ode, 'g', x, Ellipsis)
check('пустая модель — тоже', not verdict and '⬜' in words)

print('=== в kit у каждого имени один дом ===')
check('verify_curvature живёт в flow', kit.verify_curvature.__module__ == 'kit.flow')
check('verify_bend остался у shape', kit.verify_bend.__module__ == 'kit.shape')
check('verify_fit остался у data', kit.verify_fit.__module__ == 'kit.data')
check('verify_ode остался в core', kit.verify_ode.__module__ == 'kit.core')

print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(ok)}/{len(ok) + len(bad)})')
sys.exit(1 if bad else 0)
