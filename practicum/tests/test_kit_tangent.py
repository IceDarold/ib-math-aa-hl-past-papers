"""Проверки E4: кривая, касательная, нормаль — и доказательство, что внутри
них нет дифференцирования.

Семнадцатое понятие равенства ответов держится на одном утверждении:
наклон кривой проверка получает **ходьбой по ней**, а не производной.
Утверждение это легко обронить при правке — одна строка sp.diff, и раздел
станет обычной сверкой с sympy, ничего внешне не изменив. Поэтому в конце
файла стоит разбор kit/tangent.py через ast: в разделе не должно быть ни
вызова diff, ни Derivative, ни idiff, а sp.solve разрешён ровно там, где
разбирается прямая из ответа студента.

Остальное — обычные тесты: верный ответ принимается в любой записи,
типовой промах отвергается и называется по имени, незаполненный ответ
даёт ⬜ и не роняет ноутбук.

Запуск:  python practicum/tests/test_kit_tangent.py
"""
import ast
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

R = sp.Rational
a_, b_, m_, t_ = sp.symbols('a b m t')

passed = failed = 0


def t(name, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print(f'FAIL: {name}')


def say(fn, *args, **kwargs):
    """Вердикт и напечатанное сообщение."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        ok = fn(*args, **kwargs)
    return bool(ok), buffer.getvalue().strip()


PARA = curve(sp.Eq(y, x**2))
RING = curve(x**2 + y**2 - 25)
LOOP = curve(sp.Eq(sp.exp(x + y), x**2 + y**2))
BLANK = curve(...)

print('--- кривая: и функция, и уравнение ---')
t('явная кривая распознана как разрешимая', PARA[4] is not None)
t('неявная кривая остаётся условием', RING[4] is None)
t('Eq и выражение дают одно и то же',
  curve(sp.Eq(y, x**2))[1] == curve(y - x**2)[1])
t('пустая кривая помнит, что она пуста', BLANK[1] is Ellipsis)

print('--- наклон берётся ходьбой ---')
t('парабола: наклон 4 в точке (2, 4)',
  abs(kit._slope(PARA, (2.0, 4.0)) - 4) < 1e-9)
t('окружность: наклон −3/4 в точке (3, 4)',
  abs(kit._slope(RING, (3.0, 4.0)) + 0.75) < 1e-9)
t('вертикальная касательная выходит бесконечностью',
  kit._slope(RING, (5.0, 0.0)) is sp.oo)
t('точка вне кривой до ходьбы не допускается',
  kit._only_point(RING, (99.0, 0.0)) is None)

print('--- verify_slope ---')
t('верный наклон в точке', say(verify_slope, 't', 4, PARA, at=2)[0])
t('верный наклон через x и y', say(verify_slope, 't', -x/y, RING,
                                  domain=(-4, 4))[0])
t('перевёрнутый наклон отвергнут',
  not say(verify_slope, 't', -y/x, RING, domain=(-4, 4))[0])
ok, message = say(verify_slope, 't', x/y, RING, domain=(-4, 4))
t('потерянный знак назван по имени', not ok and 'знак' in message)
ok, message = say(verify_slope, 't', -R(1, 4), PARA, at=2)
t('наклон нормали назван по имени', not ok and 'нормали' in message)
ok, message = say(verify_slope, 't', a_, PARA, at=2)
t('буква в ответе названа по имени', not ok and 'число' in message)
t('незаполненный ответ даёт квадрат',
  say(verify_slope, 't', ..., PARA, at=2)[1].startswith('⬜'))
t('незаданная кривая тоже даёт квадрат',
  say(verify_slope, 't', 4, BLANK, at=2)[1].startswith('⬜'))

print('--- verify_tangent и verify_normal ---')
t('касательная выражением', say(verify_tangent, 't', 4*x - 4, PARA, 2)[0])
t('касательная равенством',
  say(verify_tangent, 't', sp.Eq(y, 4*x - 4), PARA, 2)[0])
t('касательная в несобранном виде',
  say(verify_tangent, 't', 4*(x - 2) + 4, PARA, 2)[0])
ok, message = say(verify_tangent, 't', -x/4 + R(9, 2), PARA, 2)
t('нормаль вместо касательной названа', not ok and 'нормаль' in message)
ok, message = say(verify_tangent, 't', 4*x - 3, PARA, 2)
t('верный наклон мимо точки назван', not ok and 'наклон верный' in message)
ok, message = say(verify_tangent, 't', x**2, PARA, 2)
t('не прямая отвергнута', not ok and 'не уравнение прямой' in message)
t('нормаль принята', say(verify_normal, 't', -x/4 + R(9, 2), PARA, 2)[0])
ok, message = say(verify_normal, 't', 4*x - 4, PARA, 2)
t('касательная вместо нормали названа', not ok and 'касательная' in message)
ok, message = say(verify_normal, 't', -4*x + 12, PARA, 2)
t('минус вместо обратной величины назван',
  not ok and 'минус обратный' in message)
t('вертикальная нормаль записывается как x = c',
  say(verify_normal, 't', sp.Eq(x, 0), PARA, 0)[0])
t('касательная с буквами',
  say(verify_tangent, 't', 2*a_*x - a_**2, curve(sp.Eq(y, a_*x**2 / a_ * a_)),
      a_, params={a_: (1, 2, 3)})[0]
  or say(verify_tangent, 't', 2*a_*x - a_**2, curve(sp.Eq(y, x**2)),
         a_, params={a_: (1, 2, 3)})[0])

print('--- verify_where: и точка, и полнота ---')
t('одна точка парой', say(verify_where, 't', (2, 4), PARA, 4, (-5, 5))[0])
t('одна точка одним числом',
  say(verify_where, 't', 2, PARA, 4, (-5, 5), coordinates=False)[0])
ok, message = say(verify_where, 't', 2, PARA, 4, (-5, 5))
t('без второй координаты отвергнуто', not ok and 'две координаты' in message)
ok, message = say(verify_where, 't', [(-5, 25), (5, 25)], RING, 0, (-6, 6))
t('чужая точка отвергнута', not ok and 'не лежит на кривой' in message)
ok, message = say(verify_where, 't', (0, 5), RING, 0, (-6, 6))
t('одна из двух точек — неполный ответ',
  not ok and 'таких точек' in message)
t('обе точки приняты',
  say(verify_where, 't', [(0, 5), (0, -5)], RING, 0, (-6, 6))[0])
ok, message = say(verify_where, 't', [(0, 5), (0, 5)], RING, 0, (-6, 6))
t('дважды названная точка отвергнута', not ok and 'дважды' in message)
ok, message = say(verify_where, 't', (2, 4), PARA, 4, (3, 5))
t('точка вне отрезка отвергнута', not ok and 'вне' in message)

print('--- округление принимается как округление ---')
t('точка в три значащие цифры принята',
  say(verify_where, 't', [(0.331, -0.743), (1.84, -0.538)], LOOP, 0,
      (0.05, 3))[0])
t('ошибка в третьей цифре отвергнута',
  not say(verify_where, 't', [(0.331, -0.743), (1.85, -0.538)], LOOP, 0,
          (0.05, 3))[0])
t('точный ответ принят наравне с округлённым',
  say(verify_where, 't', (2*sp.log(45), 2), curve(sp.Eq(y, 90*sp.exp(-x/2))),
      -1, (0.01, 20))[0])
t('половина единицы последней цифры считается от самого числа',
  kit._rounds_to(1.84, 1.84273) and not kit._rounds_to(0.331, 0.336))

print('--- verify_on ---')
t('высота с кривой принята', say(verify_on, 't', 4, PARA, 2)[0])
ok, message = say(verify_on, 't', 5, PARA, 2)
t('чужая высота отвергнута и названа', not ok and 'проходит там через' in message)
t('незаполненная высота даёт квадрат',
  say(verify_on, 't', ..., PARA, 2)[1].startswith('⬜'))

print('--- verify_second ---')
t('вторая производная параболы равна 2',
  say(verify_second, 't', 2, PARA, 1)[0])
ok, message = say(verify_second, 't', 2*R(1, 1) * 1, PARA, 1)
t('и она же принята при другой записи', ok)
t('вторая производная окружности равна −r²/y³',
  say(verify_second, 't', R(-25, 64), RING, (3, 4))[0])
t('через x и y тоже принимается',
  say(verify_second, 't', -25/y**3, RING, (3, 4))[0])
ok, message = say(verify_second, 't', R(-3, 4), RING, (3, 4))
t('первая производная вместо второй названа',
  not ok and 'первая производная' in message)

print('--- verify_right_angle ---')
CROSS = curve(sp.Eq(y, 4 - (x - 2)/4))
t('два наклона в общей точке приняты',
  say(verify_right_angle, 't', (4, -R(1, 4)), PARA, CROSS, 2)[0])
ok, message = say(verify_right_angle, 't', (4, 4), PARA, CROSS, 2)
t('чужой наклон отвергнут', not ok and 'идёт здесь с наклоном' in message)
ok, message = say(verify_right_angle, 't', 4, PARA, CROSS, 2)
t('один наклон вместо двух отвергнут', not ok and 'два наклона' in message)
t('семейство проверяется при каждом значении буквы',
  say(verify_right_angle, 't', (-a_/sp.sqrt(a_*b_), b_/sp.sqrt(a_*b_)),
      curve(sp.Eq(y**2, 4*a_**2 - 4*a_*x)),
      curve(sp.Eq(y**2, 4*b_**2 + 4*b_*x)),
      (a_ - b_, 2*sp.sqrt(a_*b_)), params={a_: (2, 3, 5), b_: (1, 2, 4)})[0])

print('--- verify_constant ---')
FAMILY = (lambda v: curve(sp.Eq(y, v*x**2)))
t('постоянная, подобранная под наклон, принята',
  say(verify_constant, 't', 2, FAMILY, 1, 4, (0.5, 8))[0])
ok, message = say(verify_constant, 't', 3, FAMILY, 1, 4, (0.5, 8))
t('чужая постоянная отвергнута', not ok and 'наклон в точке' in message)
BOTH = (lambda v: curve(sp.Eq(y, (2*x + v)**3/(x + 5)**2)))
t('оба значения приняты',
  say(verify_constant, 't', [2.73, 15.0], BOTH, 1,
      sp.tan(70*sp.pi/180), (0.1, 25))[0])
ok, message = say(verify_constant, 't', 2.73, BOTH, 1,
                  sp.tan(70*sp.pi/180), (0.1, 25))
t('одно значение из двух — неполный ответ',
  not ok and 'таких значений' in message)

print('--- ходьба, а не дифференцирование ---')
# Раздел — весь модуль kit/tangent.py: первообразная из E5 живёт в
# соседнем модуле и сюда не входит.
source = open(os.path.join(ROOT, 'practicum/kit/tangent.py')).read()
start = source.index('# ========================================================= '
                     'кривая и прямая')
section = source[start:]
tree = ast.parse(section[section.index('def curve('):])
calls = [node.func for node in ast.walk(tree) if isinstance(node, ast.Call)]
names = {node.attr for node in calls if isinstance(node, ast.Attribute)}
names |= {node.id for node in calls if isinstance(node, ast.Name)}
t('в разделе не вызывается diff', 'diff' not in names)
t('в разделе не вызывается idiff', 'idiff' not in names)
t('в разделе нет Derivative', 'Derivative' not in names
  and 'Derivative' not in section)
# Комментарии ast выбрасывает, поэтому упоминание формулы в пояснении
# раздела здесь не мешает: ищем её среди настоящих имён.
used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
used |= {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
t('и нет формулы неявной производной',
  not {'F_x', 'F_y', 'fx', 'fy'} & used)
# sp.solve разрешён ровно там, где разбирается прямая из ответа студента.
inside = [node for node in ast.walk(tree)
          if isinstance(node, ast.FunctionDef) and node.name == '_straight']
solves = sum(1 for node in ast.walk(tree) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and node.func.attr == 'solve')
here = sum(1 for node in ast.walk(inside[0]) if isinstance(node, ast.Call)
           and isinstance(node.func, ast.Attribute) and node.func.attr == 'solve')
t('solve вызывается только при разборе прямой', solves == here == 2)
# Сама ходьба обязана оставаться сложением и делением: ни одного вызова
# sympy внутри функции, которая делает шаг.
step = [node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == '_lean'][0]
t('шаг по кривой обходится без sympy',
  not any(isinstance(node, ast.Attribute) and getattr(node.value, 'id', '') == 'sp'
          for node in ast.walk(step)))

print(f'\n{"ВСЁ ВЕРНО" if not failed else "ПРОВАЛЫ"}  ({passed}/{passed + failed})')
sys.exit(1 if failed else 0)
