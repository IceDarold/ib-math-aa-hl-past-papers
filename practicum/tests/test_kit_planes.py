"""Механика секции плоскостей kit (C6): плоскость и система как множества.

verify_c6.py и check_archive_c6.py гоняют ноутбуки на настоящих вопросах.
Здесь — сама механика, на своих числах, каждое свойство отдельно:

- плоскость принимается любым кратным уравнением и векторной формой с
  любой точкой и любыми двумя направлениями, а промахи — знак средней
  компоненты, знак правой части, параллельная плоскость, вектор вдоль
  плоскости — называются каждый своим словом;
- все способы задать плоскость — уравнение, точка и нормаль, три точки,
  прямая и точка, две прямые, перпендикулярно двум плоскостям — дают одну;
- общая часть: точка, прямая, ничего, и в каждом случае неверный ответ
  получает причину, в том числе «параметр вместо точки» и «нормаль вместо
  направления»;
- условия на буквы: перпендикулярные и параллельные плоскости,
  «пересекаются по прямой», «нет единственного решения»;
- основание перпендикуляра, расстояние и отражение с их промахами;
- секция C5 векторного произведения по-прежнему не зовёт: плоскости
  подключены к её условиям через отдельные функции.

Запуск:  python practicum/tests/test_kit_planes.py
"""
import ast
import contextlib
import io
import os
import sys
import time

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


def rejects(word, fn, *args, **kwargs):
    verdict, text = said(fn, *args, **kwargs)
    return verdict is False and word in text


print('=== векторное произведение ===')
u, v = vec(2, 0, 1), vec(1, 3, -1)
w = cross(u, v)
check('cross: (−3, 3, 6)', list(w) == [-3, 3, 6])
check('cross: перпендикулярно обоим', dot(w, u) == 0 and dot(w, v) == 0)
check('cross: антикоммутативно', cross(v, u) == -w)
try:
    cross(vec(1, 2), vec(3, 4))
    check('cross: плоские векторы — ошибка', False)
except ValueError:
    check('cross: плоские векторы — ошибка', True)

print('=== плоскость — множество точек ===')
A, B, C = vec(1, 1, 0), vec(3, 1, 1), vec(1, 2, 2)          # нормаль (−1, −4, 2)
ABC = plane(A, B, C)
check('plane: через три точки — −x − 4y + 2z = −5', repr(ABC) == '-x - 4*y + 2*z = -5')
check('plane: сама плоскость', said(verify_plane, Eq(x + 4 * y - 2 * z, 5), ABC)[0])
check('plane: кратное уравнение', said(verify_plane, Eq(-3 * x - 12 * y + 6 * z, -15), ABC)[0])
check('plane: переносы через знак равенства', said(verify_plane, Eq(x + 4 * y, 5 + 2 * z), ABC)[0])
check('plane: векторная форма', said(verify_plane, A + lam * (B - A) + mu * (C - A), ABC)[0])
check('plane: векторная форма с другой точкой и направлениями',
      said(verify_plane, C + sp.Symbol('s') * (B - A + C - A) + sp.Symbol('u') * (2 * (C - B)), ABC)[0])
check('plane: знак средней компоненты', rejects('middle component', verify_plane, Eq(-x + 4 * y + 2 * z, 3), ABC))
check('plane: знак другой компоненты — без правила средней',
      rejects('z-component of the normal', verify_plane, Eq(x + 4 * y + 2 * z, 5), ABC)
      and not rejects('middle', verify_plane, Eq(x + 4 * y + 2 * z, 5), ABC))
check('plane: знак правой части', rejects('right-hand side has the wrong sign', verify_plane, Eq(x + 4 * y - 2 * z, -5), ABC))
check('plane: параллельная плоскость', rejects('parallel plane', verify_plane, Eq(x + 4 * y - 2 * z, 7), ABC))
check('plane: вектор вдоль плоскости', rejects('lies along the plane', verify_plane, Eq(2 * x + z, 2), ABC))
check('plane: выражение вместо уравнения', rejects('is an equation', verify_plane, x + 4 * y - 2 * z - 5, ABC))
check('plane: не первая степень', rejects('linear in x, y and z', verify_plane, Eq(x ** 2 + y, 5), ABC))
check('plane: параллельные направления', rejects('give a line', verify_plane, A + lam * vec(1, 0, 0) + mu * vec(2, 0, 0), ABC))
check('plane: направление не в плоскости', rejects('does not lie in the plane', verify_plane,
                                                    A + lam * (B - A) + mu * vec(1, 0, 0), ABC))
check('plane: точка векторной формы не на плоскости', rejects('is not on the plane', verify_plane,
                                                               B + C + lam * (B - A) + mu * (C - A), ABC))
check('plane: десятичные коэффициенты', said(verify_plane, Eq(0.2 * x + 0.8 * y - 0.4 * z, 1.0), ABC)[0])
check('plane: пустой ответ — ⬜', said(verify_plane, ..., ABC)[1].startswith('⬜'))

print('=== способы задать плоскость ===')
same = [
    plane(Eq(x + 4 * y - 2 * z, 5)),
    plane(A, vec(-1, -4, 2)),
    plane(line(A, B - A), C),
    plane(C, line(A, B - A)),
    plane(line(A, B - A), line(A, C - A)),
    plane(line(A, B - A), line(C, A - B)),                  # две параллельные прямые
    plane(A + lam * (B - A) + mu * (C - A)),
]
check('plane: семь способов — одна плоскость', all(said(verify_plane, Eq(x + 4 * y - 2 * z, 5), P)[0] for P in same))
P1, P2 = plane(Eq(x + y, 1)), plane(Eq(y - z, 2))
perp = plane(vec(1, 2, 3), P1, P2)
check('plane: через точку перпендикулярно двум', dot(perp.normal, P1.normal) == 0 and dot(perp.normal, P2.normal) == 0
      and perp.side(vec(1, 2, 3)) == perp.constant)
try:
    plane(A, 2 * A, 3 * A)
    check('plane: три точки на прямой — ошибка', False)
except ValueError:
    check('plane: три точки на прямой — ошибка', True)
check('plane: subs и буквы', plane(Eq(sp.Symbol('a') * x + y, 2)).subs(sp.Symbol('a'), 3).normal == vec(3, 1, 0))

print('=== нормаль и направление ===')
check('normal: кратная', said(verify_normal_vector, vec(2, 8, -4), ABC)[0])
check('normal: знак средней', rejects('middle component', verify_normal_vector, vec(-1, 4, 2), ABC))
check('normal: лежит в плоскости', rejects('lies in the plane', verify_normal_vector, B - A, ABC))
check('normal: радиус-вектор точки', rejects('position vector', verify_normal_vector, C, ABC))
check('normal: нулевой', rejects('zero vector', verify_normal_vector, vec(0, 0, 0), ABC))
Q1, Q2 = plane(Eq(x + y + z, 6)), plane(Eq(x - y + 2 * z, 5))
meet_line = intersection(Q1, Q2)
check('direction: n₁ × n₂', said(verify_direction, cross(Q1.normal, Q2.normal), meet_line)[0])
check('direction: нормаль одной плоскости', rejects('normal of the first plane', verify_direction, vec(1, 1, 1), meet_line))
check('direction: знак средней', rejects('middle component', verify_direction, vec(3, 1, -2), meet_line))
check('direction: не в плоскости', rejects('does not lie in', verify_direction, vec(1, 0, 0), meet_line))

print('=== общая часть ===')
check('intersection: две плоскости — прямая', isinstance(meet_line, type(line(A, B))))
check('intersection: направление целое', list(meet_line.direction) in ([3, -1, -2], [-3, 1, 2]))
check('intersection: прямая с любой точкой', said(verify_intersection, vec(7, 0, -1) + lam * vec(-6, 2, 4), Q1, Q2)[0])
check('intersection: общее решение через t', said(verify_intersection, vec((11 - 3 * t) / 2, (1 + t) / 2, t), Q1, Q2)[0])
check('intersection: неверное общее решение', rejects('is not on the first plane', verify_intersection,
                                                    vec(t, (1 + t) / 3, (11 - 2 * t) / 3), Q1, Q2))
check('intersection: одна точка вместо прямой', rejects('share a whole line', verify_intersection, (7, 0, -1), Q1, Q2))
check('intersection: направление-нормаль', rejects('is the normal of', verify_intersection, vec(7, 0, -1) + lam * vec(1, 1, 1), Q1, Q2))
check('intersection: точка не на второй', rejects('is not on the second plane', verify_intersection,
                                                  vec(6, 0, 0) + lam * vec(3, -1, -2), Q1, Q2))
Q3 = plane(Eq(2 * x + 3 * z, 11))                                    # сумма Q1 и Q2
Q4 = plane(Eq(2 * x + 3 * z, 12))
Q5 = plane(Eq(2 * x + 4 * z, 11))
check('intersection: три плоскости по прямой', isinstance(intersection(Q1, Q2, Q3), type(meet_line)))
check('intersection: три плоскости без общей точки', intersection(Q1, Q2, Q4) is None)
check('intersection: три плоскости в точке', list(intersection(Q1, Q2, Q5)) == [sp.Rational(11, 2), sp.Rational(1, 2), 0])
check('intersection: none', said(verify_intersection, 'none', Q1, Q2, Q4)[0])
check('intersection: none словами', said(verify_intersection, 'no common point', Q1, Q2, Q4)[0])
check('intersection: точка при none', rejects('is not on the third plane', verify_intersection, (7, 0, -1), Q1, Q2, Q4))
check('intersection: none при точке', rejects('there is a common point', verify_intersection, 'none', Q1, Q2, Q5))
check('intersection: точка', said(verify_intersection, (5.5, 0.5, 0), Q1, Q2, Q5)[0])
ray = line(vec(1, 0, 2) + lam * vec(1, 1, 1))
flat = plane(Eq(x + 2 * y - z, 4))
check('line_plane: точка (7/2, 5/2, 9/2)', said(verify_intersection, (sp.Rational(7, 2), sp.Rational(5, 2), sp.Rational(9, 2)), ray, flat)[0])
check('line_plane: λ вместо точки', rejects('value of the parameter', verify_intersection, sp.Rational(5, 2), ray, flat))
check('line_plane: знак λ', rejects('other side', verify_intersection, (sp.Rational(-3, 2), sp.Rational(-5, 2), sp.Rational(-1, 2)), ray, flat))
inside = line(vec(4, 0, 0) + lam * vec(1, 0, 1))
check('line_plane: прямая в плоскости — общая часть сама прямая',
      said(verify_intersection, vec(5, 0, 1) + mu * vec(-2, 0, -2), inside, flat)[0])
check('line_plane: параллельная — none', said(verify_intersection, 'none', line(vec(0, 0, 0) + lam * vec(1, 0, 1)), flat)[0])
check('intersection: не тот вид ответа', rejects("or 'none'", verify_intersection, 'maybe', ray, flat))

print('=== условия на буквы ===')
a, b, c, d = sp.symbols('a b c d')
check('find: перпендикулярные плоскости', said(verify_find, sp.Rational(3, 2), a,
                                             [perpendicular(plane(Eq(a * x + y - z, 0)), plane(Eq(2 * x - y + 2 * z, 1)))])[0])
check('find: параллельные плоскости', said(verify_find, -6, a,
                                        [parallel(plane(Eq(2 * x - y + 3 * z, 1)), plane(Eq(-4 * x + 2 * y + a * z, 7)))])[0])
check('find: не параллельны — названо', rejects('not multiples', verify_find, 6, a,
                                             [parallel(plane(Eq(2 * x - y + 3 * z, 1)), plane(Eq(-4 * x + 2 * y + a * z, 7)))]))
check('find: прямая перпендикулярна плоскости', said(verify_find, 2, a, [perpendicular(line(A, vec(a, 4, -2)), flat)])[0])
check('find: прямая параллельна плоскости', said(verify_find, 3, a, [parallel(line(A, vec(a, -1, 1)), flat)])[0])
system = [plane(Eq(x + y + z, 6)), plane(Eq(x - y + 2 * z, 5)), plane(Eq(2 * x + c * z, d))]
check('find: нет единственного решения', said(verify_find, 3, c, [no_unique_meet(*system)])[0])
check('find: по прямой — две буквы', said(verify_find, [3, 11], [c, d], [meet_in_line(*system)])[0])
check('find: по прямой — правая часть не та', rejects('no common point', verify_find, [3, 10], [c, d], [meet_in_line(*system)]))
check('find: по прямой — коэффициент не тот', rejects('single point', verify_find, [2, 11], [c, d], [meet_in_line(*system)]))
check('find: есть общая точка', said(verify_find, 11, d, [meet(system[0], system[1], system[2].subs(c, 3))])[0])

print('=== перпендикуляр, расстояние, отражение ===')
Q = vec(4, 1, 5)
mirror_plane = plane(Eq(2 * x - y + 2 * z, -1))
F = unknown('F', 3)
foot = [on(F, mirror_plane), perpendicular(F - Q, mirror_plane)]
check('foot: (0, 3, 1)', said(verify_find, (0, 3, 1), F, foot)[0])
check('foot: не на плоскости', rejects('is not on the plane', verify_find, (8, -1, 9), F, foot))
check('foot: не по нормали', rejects('not perpendicular to the plane', verify_find, (1, 3, 0), F, foot))
check('distance: 6', said(verify_distance, 6, Q, mirror_plane)[0])
check('distance: порядок аргументов', said(verify_distance, 6, mirror_plane, Q)[0])
check('distance: без деления на |n|', rejects('not divided out', verify_distance, 18, Q, mirror_plane))
check('distance: |λ|', rejects('parameter of the foot', verify_distance, 2, Q, mirror_plane))
check('distance: до отражения', rejects('twice the distance', verify_distance, 12, Q, mirror_plane))
check('distance: параллельные плоскости', said(verify_distance, 6, mirror_plane, plane(Eq(2 * x - y + 2 * z, 17)))[0])
check('distance: пересекающиеся — ноль', rejects('distance between them is 0', verify_distance, 3, mirror_plane, flat))
check('distance: exact', rejects('exact', verify_distance, 6.0, Q, mirror_plane, exact=True))
image = unknown('image', 3)
check('reflection: (−4, 5, −3)', said(verify_find, (-4, 5, -3), image, [reflection(image, Q, mirror_plane)])[0])
check('reflection: основание', rejects('foot of the perpendicular', verify_find, (0, 3, 1), image, [reflection(image, Q, mirror_plane)]))
check('reflection: сама точка', rejects('the point itself', verify_find, (4, 1, 5), image, [reflection(image, Q, mirror_plane)]))
check('reflection: середина не на плоскости', rejects('halfway', verify_find, (-6, 6, -5), image, [reflection(image, Q, mirror_plane)]))
check('mirror: точка', list(mirror(Q, mirror_plane)) == [-4, 5, -3])
bent = line(Q, vec(1, 2, -3))
check('mirror: прямая через M(7, 7, −4) и Q′', said(verify_line, vec(7, 7, -4) + mu * vec(-11, -2, 1), mirror(bent, mirror_plane))[0])
check('mirror: направление не отражено', rejects("original line's", verify_line, vec(7, 7, -4) + mu * vec(1, 2, -3),
                                               mirror(bent, mirror_plane)))
check('plane: плоскость по ту сторону', said(verify_plane, Eq(2 * x - y + 2 * z, -19),
                                           plane(mirror(Q, mirror_plane), mirror_plane.normal))[0])

print('=== сообщения и устройство ===')
tilted = plane(vec(1, 2, 3), vec(sp.Symbol('k'), -2, 1), vec(5, 0, 2))
verdict, text = said(verify_find, (0, 1, 1), F, [on(F, tilted), perpendicular(F, tilted)])
check('сообщение: плоскость с дробями печатается целыми', verdict is False and '/' not in text.split('gives')[0])
check('repr: 14x − 21y − 7z = 42 печатается как 2x − 3y − z = 6',
      repr(plane(vec(3, 0, 0), vec(0, -2, 0), vec(1, 1, -7))) == '2*x - 3*y - z = 6')
source = open(os.path.join(ROOT, 'practicum', 'kit', 'vectors.py')).read()
calls = {getattr(node.func, 'attr', getattr(node.func, 'id', '')) for node in ast.walk(ast.parse(source))
         if isinstance(node, ast.Call)}
check('секция векторов по-прежнему без векторного произведения', 'cross' not in calls)
kit.language('ru')
check('русские сообщения', 'параллельная плоскость' in said(verify_plane, Eq(x + 4 * y - 2 * z, 7), ABC)[1])
kit.language('en')
start = time.time()
for _ in range(3):
    said(verify_find, [3, 11], [c, d], [meet_in_line(*system)])
    said(verify_intersection, vec(7, 0, -1) + lam * vec(-6, 2, 4), Q1, Q2)
check('условия решаются быстро: шесть вызовов меньше чем за 5 с', time.time() - start < 5)

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  ({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
