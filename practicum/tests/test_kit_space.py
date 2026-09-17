"""Механика секции измерений kit (C7): величину меряет фигура, а не формула.

verify_c7.py и check_archive_c7.py гоняют ноутбуки на настоящих вопросах.
Здесь — сама механика, на своих числах, каждое свойство отдельно:

- verify_cross требует вектор целиком, а не с точностью до множителя, и
  называет своим словом перестановку множителей, знак средней компоненты,
  скалярное произведение и покомпонентное умножение;
- measure меряет треугольник, параллелограмм и пирамиду по вершинам, и
  verify_measure знает пропущенную половину, пропущенную треть, |u||v|
  вместо |u × v| и площадь основания вместо объёма;
- verify_formula сверяет запись через длины и угол подстановкой чисел в
  символические векторы, а не сравнением с эталоном;
- verify_arc отличает дугу от угла, от градусов и от хорды;
- verify_angle с плоскостями: острый угол между ними и то, что осталось
  от прямого угла с нормалью, — и обе подсказки;
- verify_distance с прямыми: точка и прямая, параллельные прямые,
  пересекающиеся и скрещивающиеся;
- verify_optimum с числом вместо вектора отдаёт само наименьшее значение,
  в том числе на бесконечном промежутке;
- имена C7 не ломают C1 и C2: verify_area и verify_volume из секции фигур
  остались на месте и работают по-прежнему.

Запуск:  python practicum/tests/test_kit_space.py
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


print('=== векторное произведение ===')
u, v = vec(2, 0, 1), vec(1, 3, -1)
w = cross(u, v)
check('verify_cross: сам продукт', accepts(verify_cross, w, u, v))
check('verify_cross: список тоже', accepts(verify_cross, (-3, 3, 6), u, v))
check('verify_cross: кратное не годится — у произведения своя длина',
      rejects('length', verify_cross, 2 * w, u, v))
check('verify_cross: v × u', rejects('swapping the factors', verify_cross, -w, u, v))
check('verify_cross: знак средней компоненты',
      rejects('middle component', verify_cross, vec(-3, -3, 6), u, v))
check('verify_cross: знак крайней компоненты',
      rejects('x-component', verify_cross, vec(3, 3, 6), u, v))
check('verify_cross: скалярное произведение',
      rejects('scalar product', verify_cross, dot(u, v), u, v))
check('verify_cross: покомпонентное умножение',
      rejects('one by one', verify_cross, vec(2, 0, -1), u, v))
check('verify_cross: чужой вектор — не перпендикулярен',
      rejects('perpendicular', verify_cross, vec(1, 1, 1), u, v))
check('verify_cross: число вместо вектора',
      rejects('three numbers', verify_cross, 7, u, v))
letter = symbols('c')
check('verify_cross: с буквой', accepts(verify_cross, cross(vec(1, letter, 0), v),
                                        vec(1, letter, 0), v))
check('verify_cross: пустой ответ не считается ошибкой',
      said(verify_cross, Ellipsis, u, v)[0] is False)

print('=== площадь и объём ===')
A, B, C, D = vec(0, 0, 0), vec(2, 1, 0), vec(3, 3, 0), vec(1, 2, 0)
check('measure: параллелограмм на (2, 1) и (1, 2) — 3', measure('parallelogram', A, B, C, D) == 3)
check('measure: треугольник — половина', measure('triangle', A, B, D) == sp.Rational(3, 2))
check('verify_measure: площадь параллелограмма',
      accepts(verify_measure, 3, 'parallelogram', A, B, C, D))
check('verify_measure: половина — это треугольник',
      rejects('the triangle on the two sides', verify_measure, sp.Rational(3, 2),
              'parallelogram', A, B, C, D))
check('verify_measure: у треугольника забыта половина',
      rejects('the half is missing', verify_measure, 3, 'triangle', A, B, D))
check('verify_measure: |u||v| вместо |u × v|',
      rejects('|u||v|', verify_measure, mag(B - A) * mag(D - A), 'parallelogram', A, B, C, D))
check('verify_measure: скалярное произведение',
      rejects('scalar product', verify_measure, 4, 'parallelogram', A, B, C, D))
check('verify_measure: вершины не по кругу',
      rejects('not in order', verify_measure, 3, 'parallelogram', A, B, D, C))
check('verify_measure: не число', rejects('is a number', verify_measure, vec(1, 2, 3),
                                          'triangle', A, B, D))
check('verify_measure: три цифры годятся', accepts(verify_measure, 1.5, 'triangle', A, B, D))
check('verify_measure: точного ответа просят точно',
      rejects('decimal', verify_measure, 1.5, 'triangle', A, B, D, exact=True))

S = vec(0, 0, 4)
check('measure: пирамида — 4/3 · ... ', measure('pyramid', S, A, B, D) == 2)
check('verify_measure: объём пирамиды', accepts(verify_measure, 2, 'pyramid', S, A, B, D))
check('verify_measure: забыта треть', rejects('third is missing', verify_measure, 6,
                                              'pyramid', S, A, B, D))
check('verify_measure: параллелепипед', rejects('parallelepiped', verify_measure, 12,
                                                'pyramid', S, A, B, D))
check('verify_measure: площадь основания вместо объёма',
      rejects('area of the base', verify_measure, sp.Rational(3, 2), 'pyramid', S, A, B, D))
try:
    measure('cube', A, B, C, D)
    check('measure: неизвестная фигура — ошибка', False)
except ValueError:
    check('measure: неизвестная фигура — ошибка', True)
try:
    measure('triangle', A, B, C, D)
    check('measure: не то число вершин — ошибка', False)
except ValueError:
    check('measure: не то число вершин — ошибка', True)

print('=== запись через длины и угол ===')
a = vec(*symbols('a1 a2 a3'))
b = vec(*symbols('b1 b2 b3'))
L, M, TH = symbols('L M th')
letters = {L: mag(a), M: mag(b), TH: angle(a, b)}
square = dot(cross(a, b), cross(a, b))
check('verify_formula: L²M²sin²θ', accepts(verify_formula, L**2 * M**2 * sin(TH)**2,
                                           square, letters))
check('verify_formula: та же величина иначе',
      accepts(verify_formula, L**2 * M**2 - L**2 * M**2 * cos(TH)**2, square, letters))
check('verify_formula: синус и косинус местами',
      rejects('swapped', verify_formula, L**2 * M**2 * cos(TH)**2, square, letters))
check('verify_formula: корень вместо величины',
      rejects('square', verify_formula, L * M * sin(TH), square, letters))
check('verify_formula: лишняя буква',
      rejects('the answer uses', verify_formula, L * M * x, square, letters))
check('verify_formula: просто мимо',
      rejects('with numbers this gives', verify_formula, L**2 * M**2 * sin(TH), square, letters))

print('=== дуга на сфере ===')
first, second = vec(6, 0, 0), vec(0, 6, 0)
check('verify_arc: четверть окружности радиуса 6', accepts(verify_arc, 3 * pi, 6, first, second))
check('verify_arc: сам угол', rejects('central angle itself', verify_arc, pi / 2, 6,
                                      first, second))
check('verify_arc: угол в градусах', rejects('in degrees', verify_arc, 90, 6, first, second))
check('verify_arc: хорда', rejects('chord', verify_arc, 6 * sqrt(2), 6, first, second))
check('verify_arc: не число', rejects('is a number', verify_arc, vec(1, 2, 3), 6,
                                      first, second))

print('=== углы с плоскостью ===')
P1 = plane(Eq(x + 2*y + z, 0), name='P1')
P2 = plane(Eq(x - y - 2*z, 0), name='P2')
check('angle: между плоскостями — острый', sp.simplify(angle(P1, P2) - pi / 3) == 0)
check('verify_angle: 60 градусов', accepts(verify_angle, 60, P1, P2, deg=True))
check('verify_angle: тупой угол между нормалями',
      rejects('obtuse angle between the normals', verify_angle, 120, P1, P2, deg=True))
check('verify_angle: косинус', accepts(verify_angle, Rational(1, 2), P1, P2, cosine=True))
flat = plane(Eq(z, 0), name='flat')
L = line(vec(0, 0, 0) + lam*vec(1, 1, 1), lam, name='L')
check('angle: прямая и плоскость — дополнение',
      sp.simplify(angle(L, flat) - sp.asin(1 / sqrt(3))) == 0)
check('verify_angle: прямая и плоскость', accepts(verify_angle, sp.asin(1 / sqrt(3)), L, flat))
check('verify_angle: угол с нормалью',
      rejects('angle between the line and the normal', verify_angle,
              float(sp.acos(1 / sqrt(3))), L, flat))
check('angle: порядок не важен', sp.simplify(angle(flat, L) - angle(L, flat)) == 0)

print('=== расстояния до прямой ===')
L1 = line(vec(0, 0, 0) + lam*vec(1, 0, 0), lam, name='L1')
check('distance: точка и прямая', sp.simplify(distance(vec(0, 3, 4), L1) - 5) == 0)
check('distance: порядок не важен', distance(L1, vec(0, 3, 4)) == distance(vec(0, 3, 4), L1))
check('verify_distance: точка и прямая', accepts(verify_distance, 5, vec(0, 3, 4), L1))
check('verify_distance: не поделено на |d|',
      rejects('not divided out', verify_distance, 5 * 2, vec(0, 3, 4),
              line(vec(0, 0, 0) + lam*vec(2, 0, 0), lam)))
check('verify_distance: длина до точки из уравнения',
      rejects('point of the line written in its equation', verify_distance,
              mag(vec(3, 3, 4)), vec(3, 3, 4), L1))
check('verify_distance: длина проекции',
      rejects('projection onto the line', verify_distance, 3, vec(3, 3, 4), L1))

L2 = line(vec(0, 1, 0) + mu*vec(2, 0, 0), mu, name='L2')
check('distance: параллельные прямые', sp.simplify(distance(L1, L2) - 1) == 0)
check('verify_distance: параллельные прямые', accepts(verify_distance, 1, L1, L2))
L3 = line(vec(0, 1, 0) + mu*vec(0, 0, 1), mu, name='L3')
check('distance: скрещивающиеся прямые', sp.simplify(distance(L1, L3) - 1) == 0)
crossing = line(vec(0, 0, 0) + mu*vec(0, 1, 0), mu, name='crossing')
check('distance: пересекающиеся прямые — ноль', sp.simplify(distance(L1, crossing)) == 0)
check('verify_distance: пересекающиеся прямые',
      rejects('the lines meet', verify_distance, 3, L1, crossing))
check('verify_distance: не число', rejects('is a number', verify_distance, vec(1, 2, 3), L1, L2))

print('=== наименьшее значение величины ===')
letter = symbols('s')
check('verify_optimum: число, а не вектор',
      accepts(verify_optimum, 3, (letter - 2)**2 + 3, letter, Interval(0, 5), 'min'))
check('verify_optimum: бесконечный промежуток',
      accepts(verify_optimum, 3, (letter - 2)**2 + 3, letter, Interval(0, oo), 'min'))
check('verify_optimum: бесконечный слева',
      accepts(verify_optimum, 3, (letter + 2)**2 + 3, letter, Interval(-oo, 0), 'min'))
check('verify_optimum: бесконечный с обеих сторон',
      accepts(verify_optimum, 3, (letter - 2)**2 + 3, letter, Interval(-oo, oo), 'min'))
check('verify_optimum: точка вместо значения',
      rejects('value of s at which', verify_optimum, 2, (letter - 2)**2 + 3, letter,
              Interval(0, 5), 'min'))
check('verify_optimum: другой конец',
      rejects('at the other end', verify_optimum, 12, (letter - 2)**2 + 3, letter,
              Interval(0, 5), 'min'))
check('verify_optimum: вектор по-прежнему вектор',
      accepts(verify_optimum, vec(2, 3), vec(letter, 3), letter, Interval(0, 5), 'min',
              of=lambda item: (item[0] - 2)**2))

print('=== соседние секции не задеты ===')
check('C1: verify_area из секции фигур на месте',
      kit.verify_area.__module__.endswith('geometry'))
check('C2: verify_volume из секции фигур на месте',
      kit.verify_volume.__module__.endswith('geometry'))
check('C7: verify_measure и verify_cross — из секции измерений',
      kit.verify_measure.__module__.endswith('space')
      and kit.verify_cross.__module__.endswith('space'))
check('C6: verify_distance с плоскостью по-прежнему в секции плоскостей',
      kit.verify_distance.__module__.endswith('planes'))
plane_far = plane(Eq(x + 2*y + 2*z, 0), name='far')
check('C6: расстояние до плоскости не сломано',
      accepts(verify_distance, 2, vec(2, 2, 0), plane_far))

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  "
      f"({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
