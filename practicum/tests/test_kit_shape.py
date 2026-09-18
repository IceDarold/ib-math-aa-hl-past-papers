"""Механика секции формы графика kit (E8): вид точки решают соседи.

verify_e8.py и check_archive_e8.py гоняют ноутбуки на настоящих вопросах.
Здесь — сама механика, на своих числах, каждое свойство отдельно:

- stationary находит все точки нулевого наклона, включая ту, где наклон
  нуля только касается: у x³ просмотр смен знака её не видит вовсе;
- nature отвечает и там, где вторая производная равна нулю: у x⁴ в нуле
  минимум, у x⁵ — перегиб, и различают их соседи;
- concavity меряет выгиб хордой, а не второй производной;
- inflexions находит смену стороны выгиба и уточняет её узкой хордой;
- verify_turning требует обе координаты, полноту набора и отрезок из
  условия, принимает пустой ответ там, где точек нет, и называет своим
  словом переставленные координаты и вторую координату, взятую мимо;
- verify_bend отличает третью значащую цифру от настоящего перегиба;
- verify_side отделяет сторону оси от вида точки;
- verify_condition спрашивает свойство в узлах сетки и называет узел,
  в котором ответ с ним разошёлся;
- crossings считает касание оси за одно пересечение, а не за два и не за
  ноль: просмотр по знакам его теряет, и потому у многочлена кратности
  убираются точно;
- имена E8 не ломают E3 и E4: verify_stationary из секции производной и
  verify_second из секции касательной остались на месте.

Запуск:  python practicum/tests/test_kit_shape.py
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
import kit
from kit import *                                                    # noqa: F403

language('en')
ok, bad = [], []


def check(name, got, expect=True):
    (ok if got == expect else bad).append(name)
    if got != expect:
        print(f'  ПРОВАЛ {name}')


def said(fn, *args, **kwargs):
    """(вердикт, напечатанное)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        verdict = fn('t', *args, **kwargs)
    return verdict, buffer.getvalue()


def accepts(fn, *args, **kwargs):
    return said(fn, *args, **kwargs)[0] is True


def rejects(word, fn, *args, **kwargs):
    verdict, text = said(fn, *args, **kwargs)
    return verdict is False and word in text


def places(found):
    return [round(spot[0], 4) for spot in found]


cube = x**3 - 6*x**2 + 9*x + 1            # вершины (1, 5) и (3, 1), перегиб x = 2

print('=== stationary: просмотр находит всё ===')
found = stationary(cube, (-1, 5))
check('две точки', len(found) == 2)
check('там, где нужно', places(found) == [1.0, 3.0])
check('и та, и другая названы', [spot[2] for spot in found] == ['maximum', 'minimum'])
check('высоты с самой кривой',
      [round(spot[1], 4) for spot in found] == [5.0, 1.0])
check('у x³ наклон нуля только касается, и точка всё равно найдена',
      len(stationary(x**3, (-2, 2))) == 1)
check('и названа перегибом', stationary(x**3, (-2, 2))[0][2] == 'inflexion')
check('у x³ + x точек нет вовсе', stationary(x**3 + x, (-2, 2)) == [])
check('конец отрезка тоже виден',
      places(stationary(x**2, (0, 3))) == [0.0])

print('=== nature: там, где вторая производная молчит ===')
check('у x⁴ в нуле минимум', nature(x**4, 0) == 'minimum')
check('у x⁵ в нуле перегиб', nature(x**5, 0) == 'inflexion')
check('у x³ в нуле перегиб', nature(x**3, 0) == 'inflexion')
check('точка мимо вершин и перегиба — ни то, ни другое',
      nature(cube, sp.Rational(3, 2)) == 'neither')
check('вершина узнаётся по соседям', nature(cube, 1) == 'maximum')
check('и вторая тоже', nature(cube, 3) == 'minimum')
check('кривая из E4 проходится так же',
      nature(curve(Eq(y, cube)), 1) == 'maximum')

print('=== concavity: хордой, а не второй производной ===')
check('слева от перегиба вниз', concavity(cube, 1) == 'down')
check('справа вверх', concavity(cube, 3) == 'up')
check('у |x| в нуле вогнутость вверх, хотя производной там нет',
      concavity(sp.Abs(x), 0) == 'up')

print('=== inflexions ===')
check('у кубики один перегиб', len(inflexions(cube, (-1, 5))) == 1)
check('и стоит он ровно посередине',
      abs(inflexions(cube, (-1, 5))[0][0] - 2) < 1e-6)
check('у параболы перегибов нет', inflexions(x**2, (-2, 2)) == [])
check('узкая хорда уточняет место',
      abs(inflexions(x**3 - 3*x, (-2, 2))[0][0]) < 1e-7)

print('=== crossings: касание — одно пересечение ===')
check('три разных корня', crossings(x**3 - 3*x, (-5, 5)) == 3)
check('касание считается один раз', crossings(x**3 - 3*x + 2, (-5, 5)) == 2)
check('и с другой стороны тоже', crossings(x**3 - 3*x - 2, (-5, 5)) == 2)
check('один корень', crossings(x**3 - 3*x + 5, (-5, 5)) == 1)
check('тройной корень — тоже один', crossings(x**3, (-5, 5)) == 1)
check('не многочлен считается просмотром',
      crossings(sp.sin(x), (-4, 4)) == 3)

print('=== verify_turning ===')
check('пара координат', accepts(verify_turning, (1, 5), cube, 'maximum', domain=(-1, 5)))
check('обе точки списком',
      accepts(verify_turning, [(1, 5), (3, 1)], cube, domain=(-1, 5)))
check('вторая координата мимо',
      rejects('the second is not', verify_turning, (1, 4), cube, 'maximum',
              domain=(-1, 5)))
check('координаты переставлены',
      rejects('other way round', verify_turning, (5, 1), cube, domain=(-1, 5)))
check('наклон там не ноль',
      rejects('not zero', verify_turning, (2, 3), cube, domain=(-1, 5)))
check('найдено не всё',
      rejects('not all of them', verify_turning, [(1, 5)], cube, domain=(-1, 5)))
check('одна и та же точка дважды',
      rejects('named twice', verify_turning, [(1, 5), (1, 5)], cube, domain=(-1, 5)))
check('вне отрезка из условия',
      rejects('outside the interval', verify_turning, (7, 1), cube, domain=(-1, 5)))
check('только x, если координат не просят',
      accepts(verify_turning, 1, cube, 'maximum', domain=(-1, 5), coordinates=False))
check('пустой ответ там, где точек нет',
      accepts(verify_turning, [], x**3 + x, domain=(-2, 2)))
check('пустой ответ там, где точка есть',
      rejects('there is such a point', verify_turning, [], cube, domain=(-1, 5)))
check('три значащие цифры принимаются',
      accepts(verify_turning, (1.00, 5.00), cube, 'maximum', domain=(-1, 5)))
check('четвёртая уже нет',
      rejects('the second is not', verify_turning, (1, 5.01), cube, 'maximum',
              domain=(-1, 5)))
a_ = sp.Symbol('a')
check('семейство проходится при каждом значении буквы',
      accepts(verify_turning, [(0, 0), (-2*a_/3, 4*a_**3/27)], x**3 + a_*x**2,
              domain=(-8, 8), params={a_: (3, 6, 1)}))
check('и ошибка в семействе называется',
      rejects('passes through', verify_turning, [(0, 0), (-a_/3, 4*a_**3/27)],
              x**3 + a_*x**2, domain=(-8, 8), params={a_: (3, 6, 1)}))
check('незаполненный ответ', said(verify_turning, ..., cube, domain=(-1, 5))[0] is False)

print('=== verify_nature ===')
check('слово', accepts(verify_nature, 'maximum', cube, 1, domain=(-1, 5)))
check('короткая запись тоже', accepts(verify_nature, 'max', cube, 1, domain=(-1, 5)))
check('минимум вместо максимума',
      rejects('it is a maximum', verify_nature, 'minimum', cube, 1, domain=(-1, 5)))
check('перегиб вместо вершины',
      rejects('this is a maximum', verify_nature, 'inflexion', cube, 1, domain=(-1, 5)))
check('вершина вместо перегиба',
      rejects('not a turning point', verify_nature, 'minimum', x**3, 0,
              domain=(-2, 2)))
check('список слов', accepts(verify_nature, ['maximum', 'minimum'], cube, [1, 3],
                             domain=(-1, 5)))
check('слов меньше, чем точек',
      rejects('2 points and 1 words', verify_nature, ['maximum'], cube, [1, 3],
              domain=(-1, 5)))
check('не слово вовсе',
      rejects('the answer is a word', verify_nature, 'sideways', cube, 1,
              domain=(-1, 5)))
check('вторая производная молчит, а проверка отвечает',
      accepts(verify_nature, 'minimum', x**4, 0, domain=(-2, 2)))
check('и на нечётной степени тоже',
      accepts(verify_nature, 'inflexion', x**5, 0, domain=(-2, 2)))

print('=== verify_concavity ===')
check('вниз', accepts(verify_concavity, 'down', cube, 1))
check('вверх', accepts(verify_concavity, 'up', cube, 3))
check('перепутано', rejects('the other side', verify_concavity, 'up', cube, 1))
check('оба сразу', accepts(verify_concavity, ['down', 'up'], cube, [1, 3]))

print('=== verify_bend ===')
check('перегиб', accepts(verify_bend, 2, cube, domain=(-1, 5)))
check('третья значащая цифра мимо',
      rejects('third significant figure', verify_bend, 2.01, cube, domain=(-1, 5)))
check('далеко мимо',
      rejects('does not change', verify_bend, 4, cube, domain=(-1, 5)))
check('с координатами', accepts(verify_bend, (2, 3), cube, domain=(-1, 5),
                                coordinates=True))
check('координаты переставлены',
      rejects('other way round', verify_bend, (3, 2), cube, domain=(-1, 5),
              coordinates=True))
check('вторая координата мимо',
      rejects('the second is not', verify_bend, (2, 9), cube, domain=(-1, 5),
              coordinates=True))
check('перегибов нет вовсе', accepts(verify_bend, [], x**2, domain=(-2, 2)))
check('а здесь есть',
      rejects('are named', verify_bend, [], cube, domain=(-1, 5)))

print('=== verify_side ===')
check('выше оси', accepts(verify_side, 'above', cube, 1))
check('ниже оси', accepts(verify_side, 'below', x**3 - 6*x**2 + 9*x - 6, 3))
check('перепутано',
      rejects('is above the axis', verify_side, 'below', cube, 1))
check('оба сразу', accepts(verify_side, ['above', 'above'], cube, [1, 3]))
check('не слово', rejects('the answer is a word', verify_side, 'sideways', cube, 1))

print('=== verify_condition ===')
c_, d_ = sp.symbols('c d')


def once(c, d):
    return crossings(x**3 - 3*c*x + d, (-30, 30)) == 1


check('условие схемы проходит',
      accepts(verify_condition, Or(c_ <= 0, d_ > 2*c_**Rational(3, 2),
                                   d_ < -2*c_**Rational(3, 2)),
              once, (c_, d_), window=(-2, 2), steps=8))
check('потерянный случай называется узлом',
      rejects('the property does hold', verify_condition,
              Or(c_ <= 0, d_ > 2*c_**Rational(3, 2)),
              once, (c_, d_), window=(-2, 2), steps=8))
check('лишний случай тоже',
      rejects('the property is not there', verify_condition, sp.S.true,
              once, (c_, d_), window=(-2, 2), steps=8))
check('свойство, о котором судить нельзя',
      rejects('could not be checked', verify_condition, c_ + d_ > 0,
              lambda c, d: None, (c_, d_), window=(-2, 2), steps=6))

print('=== соседние секции не сломаны ===')
check('E8: verify_turning и verify_nature — из секции формы',
      kit.verify_turning.__module__.endswith('shape')
      and kit.verify_nature.__module__.endswith('shape'))
check('E3: verify_stationary остался в секции производной',
      kit.verify_stationary.__module__.endswith('derivative'))
check('E4: verify_second остался в секции касательной',
      kit.verify_second.__module__.endswith('tangent'))
check('E3: verify_stationary работает по-прежнему',
      accepts(verify_stationary, [(1, 5), (3, 1)], cube, domain=(-1, 5)))
check('E4: verify_where работает по-прежнему',
      accepts(verify_where, [(0, 1), (4, 5)], curve(Eq(y, cube)), 9, (-1, 5)))

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
