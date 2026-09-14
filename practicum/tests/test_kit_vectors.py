"""Механика секции векторов kit (C5): прямая как множество, условия, углы.

verify_c5.py и check_archive_c5.py гоняют ноутбуки на настоящих вопросах.
Здесь — сама механика, на своих числах, каждое свойство отдельно:

- прямая принимается с любой своей точкой, любым параллельным
  направлением и любым именем параметра, и каждый из пяти промахов
  называется своим словом;
- декартова форма, через две точки, точка и направление — одна прямая;
- точка пересечения, «параметры вместо точки», параметр не той прямой;
- отношение двух прямых — все четыре случая в обе стороны;
- условия решаются все сразу, ограничения отбрасывают решения, два корня
  требуются оба, а корень, добавленный возведением в квадрат, — нет;
- угол при вершине, между прямыми, с горизонталью, градусы и радианы;
- курс, скорость, промежуток значений и крайний вектор;
- в секции нет векторного произведения: C5 его не спрашивает, и
  проверка им не пользуется.

Запуск:  python practicum/tests/test_kit_vectors.py
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


print('=== прямая — множество точек ===')
L = through(vec(2, 0, -1), vec(5, 1, 1))
check('line: сама прямая', said(verify_line, vec(2, 0, -1) + lam * vec(3, 1, 2), L)[0])
check('line: другая точка той же прямой', said(verify_line, vec(8, 2, 3) + lam * vec(3, 1, 2), L)[0])
check('line: направление, умноженное на −2', said(verify_line, vec(2, 0, -1) + lam * vec(-6, -2, -4), L)[0])
check('line: параметр s вместо λ', said(verify_line, vec(5, 1, 1) + sp.Symbol('s') * vec(3, 1, 2), L)[0])
check('line: дробное направление', said(verify_line, vec(2, 0, -1) + mu * vec(1, sp.Rational(1, 3), sp.Rational(2, 3)), L)[0])
check('line: параллельная прямая', rejects('parallel line', verify_line, vec(0, 0, 0) + lam * vec(3, 1, 2), L))
check('line: радиус-вектор вместо направления', rejects('position vector', verify_line, vec(2, 0, -1) + lam * vec(5, 1, 1), L))
check('line: точка и направление местами', rejects('swapped', verify_line, vec(3, 1, 2) + lam * vec(2, 0, -1), L))
cart = cartesian((x + 3) / 2, (y - 1) / 5, 4 - z)
check('cartesian: точка (−3, 1, 4), направление (2, 5, −1)',
      list(cart.point) == [-3, 1, 4] and list(cart.direction) == [2, 5, -1])
check('line: знаки точки из декартовой формы', rejects('wrong signs', verify_line, vec(3, -1, -4) + lam * vec(2, 5, -1), cart))
check('line: знак компоненты при 4 − z', rejects('wrong sign', verify_line, vec(-3, 1, 4) + lam * vec(2, 5, 1), cart))
check('line: не прямая — две буквы', rejects('a point plus one parameter', verify_line,
                                           vec(1, 2, 0) + lam * vec(1, 0, 0) + mu * vec(0, 1, 0), cart))
check('line: не прямая — λ²', rejects('a point plus one parameter', verify_line, vec(1, 2, 0) + lam ** 2 * vec(1, 0, 0), cart))
check('line: нулевое направление — это точка', rejects('a point plus one parameter', verify_line, vec(-3, 1, 4) + lam * vec(0, 0, 0), cart))
try:
    cartesian(x * y, y, z)
    check('cartesian: нелинейная часть — ошибка', False)
except ValueError:
    check('cartesian: нелинейная часть — ошибка', True)
check('line(point, direction) = through', said(verify_line, vec(5, 1, 1) + lam * vec(3, 1, 2),
                                               line(vec(2, 0, -1), vec(3, 1, 2)))[0])
family = line(vec(0, 1, 2) + t * vec(sp.Symbol('a'), 1, -1), t)
check('line: ответ с буквой вопроса', said(verify_line, vec(0, 1, 2) + lam * vec(-2 * sp.Symbol('a'), -2, 2), family)[0])

print('=== пересечение ===')
L1 = line(vec(1, 2, 0) + lam * vec(1, -1, 2))
L2 = line(vec(4, 0, 7) + mu * vec(0, 1, 1))
check('meet: (4, −1, 6)', said(verify_meet, (4, -1, 6), L1, L2)[0])
check('meet: vec тоже годится', said(verify_meet, vec(4, -1, 6), L1, L2)[0])
check('meet: λ = 3 подставлено в L2', rejects('own parameter', verify_meet, (4, 3, 10), L1, L2))
check('meet: параметры вместо точки', rejects('those are the parameters', verify_meet, (3, -1), L1, L2))
check('meet: точка только первой прямой', rejects('first line, but not on the second', verify_meet, (1, 2, 0), L1, L2))
check('meet: точка ни одной', rejects('neither', verify_meet, (9, 9, 9), L1, L2))
L3 = line(vec(2, 0, 1) + mu * vec(1, 1, 0))
check('meet: у скрещивающихся нет точки', rejects('no single common point', verify_meet, (0, 0, 0), L1, L3))
aa = sp.Symbol('a')
F1 = cartesian((x + 1) / 2, y, 3 - z)
check('meet: ответ через a', said(verify_meet, (aa / (aa - 2), (aa - 1) / (aa - 2), (2 * aa - 5) / (aa - 2)), F1, family)[0])
check('meet: округлённая точка', said(verify_meet, (4.0, -1.0, 6.0), L1, L2)[0])

print('=== отношение прямых ===')
P1, P2 = line(vec(1, 0, 0) + lam * vec(1, -1, 2)), line(vec(0, 0, 0) + mu * vec(-2, 2, -4))
S1 = line(vec(3, -2, 4) + mu * vec(2, -2, 4))
check('relation: параллельны', said(verify_relation, 'parallel', P1, P2)[0])
check('relation: пересекаются', said(verify_relation, 'intersecting', L1, L2)[0])
check('relation: скрещиваются', said(verify_relation, 'skew', L1, L3)[0])
check('relation: совпадают', said(verify_relation, 'same', P1, S1)[0])
check('relation: слово intersect', said(verify_relation, 'intersect', L1, L2)[0])
check('relation: skew для параллельных', rejects('not skew', verify_relation, 'skew', P1, P2))
check('relation: intersecting для скрещивающихся', rejects('does not hold', verify_relation, 'intersecting', L1, L3))
check('relation: parallel для скрещивающихся', rejects('not multiples', verify_relation, 'parallel', L1, L3))
check('relation: skew для пересекающихся', rejects('meet at (4, -1, 6)', verify_relation, 'skew', L1, L2))
check('relation: parallel для одной прямой', rejects('one line', verify_relation, 'parallel', P1, S1))

print('=== два параметра из двух компонент ===')
check('pair: компоненты 1 и 2', said(verify_pair, [sp.Rational(3, 2), sp.Rational(1, 2)], L1, L3)[0])
# компоненты 1 и 3: 1 + λ = 2 + μ, 2λ = 1 — λ = 1/2, μ = −1/2
verdict, text = said(verify_pair, [sp.Rational(1, 2), sp.Rational(-1, 2)], L1, L3)
check('pair: компоненты 1 и 3, и третья названа', verdict and 'does not' in text)
check('pair: у пересекающихся сходится и третья', 'meet' in said(verify_pair, [3, -1], L1, L2)[1])
check('pair: ни одна пара не сходится', rejects('no two', verify_pair, [0, 0], L1, L3))
check('pair: прямые из ответа ученика', said(verify_pair, [3, -1], vec(1, 2, 0) + lam * vec(1, -1, 2),
                                             vec(4, 0, 7) + mu * vec(0, 1, 1))[0])

print('=== условия и искомое ===')
A, B, C = vec(2, -1, 3), vec(6, 1, -1), vec(3, 4, 0)
D = unknown('D', 3)
check('find: четвёртая вершина ABCD', said(verify_find, (-1, 2, 4), D, [parallelogram(A, B, C, D)])[0])
check('find: вершина ABDC названа', rejects('not a parallelogram', verify_find, (5, 4, 0), D, [parallelogram(A, B, C, D)]))
check('find: середина', said(verify_find, (4, 0, 1), D, [midpoint(D, A, B)])[0])
check('find: половина вектора вместо середины', rejects('halfway', verify_find, (2, 1, -2), D, [midpoint(D, A, B)]))
q = unknown('q', 2)
cond = [perpendicular(q, vec(8, 15)), length(q, 34), q[0] > 0]
check('find: перпендикулярный вектор длины 34', said(verify_find, (30, -16), q, cond)[0])
check('find: второе решение отброшено ограничением', rejects('restriction', verify_find, (-30, 16), q, cond))
check('find: длина не та', rejects('length is 17', verify_find, (15, -8), q, cond))
check('find: округлённый ответ', said(verify_find, (30.0, -16.0), q, cond)[0])
r_ = sp.Symbol('r')
PQ, PR = vec(3, 1, 5) - vec(1, 0, 2), vec(r_, 3, 11) - vec(1, 0, 2)
check('find: буква из «на одной прямой»', said(verify_find, 7, r_, [parallel(PR, PQ)])[0])
check('find: буква — не кратны', rejects('not multiples', verify_find, 5, r_, [parallel(PR, PQ)]))
c_ = sp.Symbol('c')
two = [Eq(angle(line(vec(0, 0, 0), vec(1, 1, 0)), line(vec(0, 0, 0), vec(0, 1, c_))), pi / 3)]
check('find: два корня, оба', said(verify_find, [1, -1], c_, two)[0])
check('find: один корень из двух', rejects('one is missing', verify_find, 1, c_, two))
check('find: лишний корень', rejects('does not hold: 1.249', verify_find, [1, -1, 2], c_, two))
pp = sp.Symbol('p')
same_angle = [Eq(angle(vec(-5, 7), vec(pp, -6)), angle(vec(-8, 9), vec(pp, -6)))]
verdict, text = said(verify_find, 4.79, pp, same_angle)
check('find: равные углы — один корень', verdict)
squared = sp.solve(sp.Eq((-5 * pp - 42) ** 2 / 74, (-8 * pp - 54) ** 2 / 145), pp)
extra = [root for root in squared if abs(float(root) - 4.787) > 0.01]
check('find: корень квадрата уравнения не принимается', len(extra) == 1 and said(verify_find, float(extra[0]), pp, same_angle)[0] is False)
check('find: exact отвергает десятичную', rejects('exact', verify_find, [1.0, -1.0], c_, two, exact=True))
check('find: две значащие цифры', rejects('two significant', verify_find, 4.8, pp, same_angle))
check('find: вектор вместо длины', rejects('its length', verify_find, (4, 2, -4), distance(A, B)))
check('find: без корня', rejects('square root', verify_find, 36, distance(A, B)))
check('find: обратный вектор', rejects('other way round', verify_find, (-4, -2, 4), B - A))
check('find: лишние буквы', rejects('letters', verify_find, (x, 2, -4), B - A))
check('find: условий не хватает', rejects('not enough', verify_find, (1, 1), q, [perpendicular(q, vec(1, -1))]))
aa, bb = sp.symbols('a b')
M1, M2 = line(vec(4, 0, -1) + lam * vec(0, aa, 1), lam), line(vec(1, 0, -bb) + mu * vec(1, 2, 3), mu)
check('find: две буквы — перпендикулярны и пересекаются',
      said(verify_find, [sp.Rational(-3, 2), 14], [aa, bb], [perpendicular(M1, M2), meet(M1, M2)])[0])
check('find: при этих буквах не пересекаются',
      rejects('do not meet', verify_find, [sp.Rational(-3, 2), 13], [aa, bb], [perpendicular(M1, M2), meet(M1, M2)]))
check('find: нет единственной точки', said(verify_find, 2, sp.Symbol('a'), [no_unique_meet(F1, family)])[0])
k_, t_ = sp.symbols('k t', positive=True)
Ahyp = vec(k_ * t_, k_ / t_)
Cpt = unknown('C', 2)
hyp = [on(Cpt, vec(0, 0), Ahyp), Eq(Cpt[0] * Cpt[1], k_ ** 2), Ne(Cpt, Ahyp)]
check('find: C ≠ A выбирает второе пересечение', said(verify_find, (-k_ * t_, -k_ / t_), Cpt, hyp)[0])
check('find: C = A отброшено', rejects('restriction', verify_find, (k_ * t_, k_ / t_), Cpt, hyp))

print('=== угол ===')
Pv, Qv, Rv = vec(1, 0, 0), vec(0, 2, 0), vec(0, 0, 3)
check('angle: при вершине P, 81.9°', said(verify_angle, 81.9, Qv, Pv, Rv, deg=True)[0])
check('angle: радианы при deg=None', said(verify_angle, 1.43, Qv, Pv, Rv)[0])
check('angle: радиус-векторы', rejects('position vectors', verify_angle, 90, Qv, Pv, Rv, deg=True))
check('angle: радианы вместо градусов', rejects('radians', verify_angle, 1.43, Qv, Pv, Rv, deg=True))
D1, D2 = line(vec(0, 0, 0), vec(1, 2, 2)), line(vec(0, 0, 0), vec(2, -1, -2))
check('angle: между прямыми острый, 63.6°', said(verify_angle, 63.6, D1, D2, deg=True)[0])
check('angle: тупой угол направлений', rejects('obtuse', verify_angle, 116.4, D1, D2, deg=True))
check('angle: векторы — тупой годится', said(verify_angle, 116.4, vec(1, 2, 2), vec(2, -1, -2), deg=True)[0])
check('angle: cos вместо угла', rejects('cos θ', verify_angle, -0.444, vec(1, 2, 2), vec(2, -1, -2)))
check('angle: с горизонталью', said(verify_angle, 16.7, vec(6, -8, -3), 'horizontal', deg=True)[0])
check('angle: с вертикалью', rejects('vertical', verify_angle, 73.3, vec(6, -8, -3), 'horizontal', deg=True))
check('angle: косинус через букву', said(verify_angle, 1 / (sp.sqrt(2) * sp.sqrt(1 + c_ ** 2)),
                                         vec(1, 1, 0), vec(0, 1, c_), cosine=True)[0])
check('angle: косинус без деления', rejects('scalar product', verify_angle, sp.Integer(1), vec(1, 1, 0), vec(0, 1, c_), cosine=True))
check('angle: точный угол', said(verify_angle, pi / 2, vec(2, -1, 3), vec(4, 5, -1), exact=True)[0])

print('=== движение ===')
ship = vec(2, -3) + t * vec(3, 4)
check('bearing: 037', said(verify_bearing, '037', vec(3, 4))[0])
check('bearing: целое 37', said(verify_bearing, 37, vec(3, 4))[0])
check('bearing: от востока', rejects('from east', verify_bearing, '053', vec(3, 4)))
check('bearing: 036.9', rejects('whole degrees', verify_bearing, '036.9', vec(3, 4)))
check('bearing: обратное направление', rejects('opposite', verify_bearing, '217', vec(3, 4)))
check('speed: 5', said(verify_speed, 5, ship)[0])
check('speed: 10 при 2t', said(verify_speed, 10, vec(2, -3) + 2 * t * vec(3, 4))[0])
check('speed: потерян множитель 2', rejects('factor of 2', verify_speed, 5, vec(2, -3) + 2 * t * vec(3, 4)))
check('speed: длина начальной точки', rejects('starting point', verify_speed, sp.sqrt(13), ship))
tp = sp.Symbol('t', positive=True)
check('speed: t с условием positive', said(verify_speed, 5, vec(2, -3) + tp * vec(3, 4))[0])
theta = sp.Symbol('theta')
around = mag(vec(3, 4) + 10 * vec(cos(theta), sin(theta)))
check('extent: 5 ≤ … ≤ 15', said(verify_extent, Interval(5, 15), around, theta, Interval(0, 2 * pi))[0])
check('extent: нижний конец — |a|', rejects('goes below', verify_extent, Interval(10, 15), around, theta, Interval(0, 2 * pi)))
check('extent: открытый промежуток', rejects('closed', verify_extent, Interval.open(5, 15), around, theta, Interval(0, 2 * pi)))
check('optimum: −a при минимуме', said(verify_optimum, (-3, -4), vec(3, 4) + 10 * vec(cos(theta), sin(theta)),
                                        theta, Interval(0, 2 * pi))[0])
check('optimum: b вместо a + b', rejects('length 10', verify_optimum, (-6, -8), vec(3, 4) + 10 * vec(cos(theta), sin(theta)),
                                          theta, Interval(0, 2 * pi)))

print('=== устройство секции ===')
source = open(os.path.join(ROOT, 'practicum', 'kit', 'vectors.py')).read()
tree = ast.parse(source)
calls = {getattr(node.func, 'attr', getattr(node.func, 'id', '')) for node in ast.walk(tree)
         if isinstance(node, ast.Call)}
check('в секции нет векторного произведения', 'cross' not in calls)
check('незаполненный ответ — ⬜', '⬜' in said(verify_line, ..., L)[1] and said(verify_find, ..., D)[1].startswith('⬜'))
kit.language('ru')
check('русские сообщения', 'параллельная прямая' in said(verify_line, vec(0, 0, 0) + lam * vec(3, 1, 2), L)[1])
kit.language('en')
start = time.time()
for _ in range(3):
    said(verify_find, [sp.Rational(-3, 2), 14], [aa, bb], [perpendicular(M1, M2), meet(M1, M2)])
    said(verify_find, (-k_ * t_, -k_ / t_), Cpt, hyp)
check('условия решаются быстро: шесть вызовов меньше чем за 5 с', time.time() - start < 5)

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  ({len(ok)}/{len(ok) + len(bad)})")
sys.exit(1 if bad else 0)
