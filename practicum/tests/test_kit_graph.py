"""Проверяет механику проверок из темы преобразований графиков.

Тема даёт седьмое в серии понятие равенства ответов. A3 сверял значения,
A4 — форму записи, A8 — множества, B1 — уравнения, C1 — конфигурацию,
B2 — функцию по тому, что она отменяет. Здесь ответом служит **картинка**,
и спрашивают её двумя способами, поэтому и проверок две.

verify_transform: ответ это рецепт, и верен он тогда, когда, выполненный
над исходным графиком, даёт целевой. Главное, что здесь измеряется, —
что проверка различает порядок шагов. За перепутанный порядок
горизонтальных преобразований markscheme снимает ровно один балл,
и проверка обязана его замечать.

verify_sketch: ответ это список особенностей, и верен он тогда, когда
каждая названная у функции есть, а ни одной нужной не пропущено.
Измеряется, что лишнее и пропущенное — разные сообщения, и что излом
отличается от гладкой вершины.

Заодно измерено, чего проверки не делают: verify_transform не требует
кратчайшего описания, а verify_sketch не смотрит на форму кривой между
особенностями.
"""
import io
import contextlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import _as_step, _apply_steps, _sketch_facts, _as_domain

res = []
q_, p_, k_, r_ = sp.symbols('q_ p_ k_ r_')
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


def said(fn, *args, **kwargs):
    """Вердикт вместе с тем, что он напечатал."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


print('=== verify_transform: что принимается ===')
# May 2021 TZ2 P1 Q12(a): arctan x → arctan(2x+1) + π/4, порядок markscheme.
t('арктангенс, порядок markscheme',
  verify_transform('  сжатие, сдвиг, подъём',
                   [('stretch_x', R(1, 2)), ('shift_x', -R(1, 2)),
                    ('shift_y', pi / 4)],
                   atan(x), atan(2 * x + 1) + pi / 4))
# Тот же ответ другим путём: сначала сдвиг на 1 влево, потом сжатие.
# markscheme принимает оба, и проверка обязана принимать оба.
t('арктангенс, второй верный порядок',
  verify_transform('  сдвиг, сжатие, подъём',
                   [('shift_x', -1), ('stretch_x', R(1, 2)),
                    ('shift_y', pi / 4)],
                   atan(x), atan(2 * x + 1) + pi / 4))
# May 2022 TZ1 P1 Q5(a): в цели стоит буква q, и она должна пройти насквозь.
t('синус с буквой в ответе',
  verify_transform('  вправо на 3π/2, вверх на q',
                   [('shift_x', 3 * pi / 2), ('shift_y', q_)],
                   4 * sin(x) + R(5, 2),
                   4 * sin(x - 3 * pi / 2) + R(5, 2) + q_))
# November 2025 TZ1 P1 Q8(b): растяжение по вертикали и два горизонтальных.
t('тройная синусоида, ноябрь 2025 TZ1',
  verify_transform('  ×2, сжатие 1/3, влево на π/6',
                   [('stretch_y', 2), ('stretch_x', R(1, 3)),
                    ('shift_x', -pi / 6)],
                   sin(x), 2 * sin(3 * x + pi / 2)))
t('тот же ответ через сдвиг на π/2',
  verify_transform('  ×2, влево на π/2, сжатие 1/3',
                   [('stretch_y', 2), ('shift_x', -pi / 2),
                    ('stretch_x', R(1, 3))],
                   sin(x), 2 * sin(3 * x + pi / 2)))
# November 2025 TZ3 P1 Q3(b): 1/x → 2 + 14/(x−4).
t('гипербола, ноябрь 2025 TZ3',
  verify_transform('  вправо 4, ×14, вверх 2',
                   [('shift_x', 4), ('stretch_y', 14), ('shift_y', 2)],
                   1 / x, (2 * x + 6) / (x - 4)))
# Отражения записываются голой строкой: величины у них нет.
t('отражение в оси x строкой',
  verify_transform('  минус', ['reflect_in_x_axis'], x**2 - 1, 1 - x**2))
t('отражение в оси y строкой',
  verify_transform('  x → −x', ['reflect_in_y_axis'], exp(x), exp(-x)))
t('короткое имя reflect_x принимается',
  verify_transform('  синоним', ['reflect_x'], x**3, -x**3))
# Один шаг можно писать без списка.
t('один шаг без списка',
  verify_transform('  просто вверх', ('shift_y', 3), x**2, x**2 + 3))

print('\n=== verify_transform: что отвергается ===')
ok, msg = said(verify_transform, '  порядок перепутан',
               [('shift_x', -R(1, 2)), ('stretch_x', R(1, 2)),
                ('shift_y', pi / 4)],
               atan(x), atan(2 * x + 1) + pi / 4)
t('перепутанный порядок отвергнут', not ok)
t('и назван именно порядком', 'порядк' in msg or 'order' in msg)

ok, msg = said(verify_transform, '  растяжение обратное',
               [('stretch_x', 2), ('shift_x', -R(1, 2)), ('shift_y', pi / 4)],
               atan(x), atan(2 * x + 1) + pi / 4)
t('обратное растяжение отвергнуто', not ok)
t('и подсказано, что подошло бы 1/2', '1/2' in msg)

ok, msg = said(verify_transform, '  сдвиг не в ту сторону',
               [('shift_x', -3 * pi / 2), ('shift_y', q_)],
               4 * sin(x) + R(5, 2), 4 * sin(x - 3 * pi / 2) + R(5, 2) + q_)
t('сдвиг в другую сторону отвергнут', not ok)
t('и назван именно стороной', 'сторон' in msg or 'other way' in msg)

# Буква в ответе должна быть той же самой: p вместо q это другой ответ.
t('чужая буква не проходит',
  not verify_transform('  вверх на p', [('shift_x', 3 * pi / 2),
                                        ('shift_y', p_)],
                       4 * sin(x) + R(5, 2),
                       4 * sin(x - 3 * pi / 2) + R(5, 2) + q_))
# Пропущенный шаг — не порядок и не знак, сообщение должно быть общим.
ok, msg = said(verify_transform, '  забыт подъём',
               [('stretch_x', R(1, 2)), ('shift_x', -R(1, 2))],
               atan(x), atan(2 * x + 1) + pi / 4)
t('пропущенный шаг отвергнут', not ok)
t('и показано, что получилось', 'atan' in msg)
# Неизвестное имя шага — отдельная ошибка с перечнем известных.
ok, msg = said(verify_transform, '  чужое имя',
               [('rotate', 90)], x**2, -x**2)
t('неизвестный шаг отвергнут', not ok)
t('и перечислены известные', 'stretch_x' in msg)
# Пустое задание печатает ⬜ и не падает.
t('пустой ответ не падает',
  not verify_transform('  ещё не решено', ..., atan(x), atan(2 * x + 1)))
t('пустой список внутри тоже',
  not verify_transform('  список с дырой', [('shift_x', ...)],
                       atan(x), atan(2 * x + 1)))

print('\n=== verify_transform: механика шагов ===')
# Растяжение по горизонтали в s раз заменяет x на x/s. Проверяем прямо:
# именно здесь путают k и 1/k.
t('stretch_x s заменяет x на x/s',
  sp.simplify(_apply_steps(sin(x), [('stretch_x', R(1, 3))], x)
              - sin(3 * x)) == 0)
t('shift_x h двигает вправо',
  sp.simplify(_apply_steps((x)**2, [('shift_x', 2)], x) - (x - 2)**2) == 0)
t('stretch_y умножает',
  sp.simplify(_apply_steps(sin(x), [('stretch_y', 2)], x) - 2 * sin(x)) == 0)
t('reflect_in_y_axis меняет знак аргумента',
  sp.simplify(_apply_steps(log(x), [_as_step('reflect_in_y_axis')], x)
              - log(-x)) == 0)
# Шаги складываются в накопленное выражение, а не в исходное: сдвиг после
# растяжения двигает уже растянутый график.
t('шаги применяются к накопленному',
  sp.simplify(_apply_steps(sin(x), [('stretch_x', R(1, 2)),
                                    ('shift_x', pi)], x)
              - sin(2 * x - 2 * pi)) == 0)
t('_as_step понимает список',
  _as_step(['shift_y', 3]) == ('shift_y', sp.Integer(3)))
t('_as_step отвергает чужое', _as_step(('rotate', 90)) is None)
t('_as_step требует величину', _as_step('shift_x') is None)

print('\n=== verify_sketch: что принимается ===')
# November 2022 P1 Q10(c): |f| для f = cos²x − 3sin²x на [0, π].
F22 = cos(x)**2 - 3 * sin(x)**2
t('модуль тригонометрической, ноябрь 2022',
  verify_sketch('  изломы, вершина и концы',
                {'cusps': [(pi / 6, 0), (5 * pi / 6, 0)],
                 'maxima': [(pi / 2, 3)],
                 'endpoints': [(0, 1), (pi, 1)]},
                Abs(F22), domain=Interval(0, pi)))
# Та же функция без модуля: та же точка становится минимумом.
t('без модуля вершина становится минимумом',
  verify_sketch('  минимум вместо максимума', {'minima': [(pi / 2, -3)]},
                F22, domain=Interval(0, pi)))
# May 2025 TZ3 P1 Q6: f = 5x + 5 + 5/(4x+2).
F25 = 5 * x + 5 + 5 / (4 * x + 2)
t('наклонная асимптота и две вершины, май 2025 TZ3',
  verify_sketch('  A, B, асимптоты',
                {'maxima': [(-1, -R(5, 2))], 'minima': [(0, R(15, 2))],
                 'vertical_asymptotes': [-R(1, 2)],
                 'oblique_asymptotes': [5 * x + 5]}, F25))
t('у модуля наклонных асимптот две',
  verify_sketch('  обе ветви',
                {'oblique_asymptotes': [5 * x + 5, -5 * x - 5],
                 'vertical_asymptotes': [-R(1, 2)]}, Abs(F25)))
t('обратная величина: асимптота уходит в ноль',
  verify_sketch('  15/f', {'y_intercept': 2, 'maxima': [(0, 2)],
                           'minima': [(-1, -6)],
                           'horizontal_asymptotes': [0]}, 15 / F25))
# May 2024 TZ1 P1 Q10(a): рациональная с двумя асимптотами.
t('рациональная, май 2024 TZ1',
  verify_sketch('  пересечения и асимптоты',
                {'x_intercepts': [-R(1, 2)], 'y_intercept': -1,
                 'vertical_asymptotes': [2], 'horizontal_asymptotes': [4]},
                (4 * x + 2) / (x - 2)))
# May 2025 TZ2 P1 Q8(a): arccos на [−1, 1] — только концы и пересечения.
t('арккосинус, май 2025 TZ2',
  verify_sketch('  концы и y-пересечение',
                {'y_intercept': pi / 2, 'endpoints': [(-1, pi), (1, 0)],
                 'x_intercepts': [1]}, acos(x), domain=Interval(-1, 1)))
# May 2023 TZ1 P2 Q2(b): координаты с калькулятора, три значащие цифры.
T23 = 2 * tan(x) - tan(x)**3
t('три значащие цифры принимаются',
  verify_sketch('  вершины с GDC',
                {'maxima': [(0.685, 1.09)], 'minima': [(-0.685, -1.09)]},
                T23, domain=Interval(-1, 1)))
# Порядок внутри списка значения не имеет.
t('порядок точек в списке не важен',
  verify_sketch('  задом наперёд',
                {'cusps': [(5 * pi / 6, 0), (pi / 6, 0)]},
                Abs(F22), domain=Interval(0, pi)))
# Проверяются только названные ключи: остальное не спрашивают — не сверяем.
t('непроверяемые ключи не мешают',
  verify_sketch('  только асимптоты', {'vertical_asymptotes': [2]},
                (4 * x + 2) / (x - 2)))

print('\n=== verify_sketch: что отвергается ===')
ok, msg = said(verify_sketch, '  один излом забыт',
               {'cusps': [(pi / 6, 0)]}, Abs(F22), domain=Interval(0, pi))
t('пропущенная особенность отвергнута', not ok)
t('и названа пропущенной', 'пропущ' in msg or 'missing' in msg)

ok, msg = said(verify_sketch, '  лишний излом',
               {'cusps': [(pi / 6, 0), (5 * pi / 6, 0), (pi / 3, 0)]},
               Abs(F22), domain=Interval(0, pi))
t('лишняя особенность отвергнута', not ok)
t('и названа лишней', 'Лишнее' in msg or 'лишнее' in msg or 'extra' in msg)

ok, msg = said(verify_sketch, '  излом назван минимумом',
               {'minima': [(pi / 6, 0)]}, Abs(F22), domain=Interval(0, pi))
t('излом не считается гладким минимумом', not ok)
t('и сказано, что это излом', 'излом' in msg or 'cusp' in msg)

ok, msg = said(verify_sketch, '  максимум вместо минимума',
               {'maxima': [(0, R(15, 2))]}, F25)
t('минимум, названный максимумом, отвергнут', not ok)
t('и сказано, что это минимум', 'минимум' in msg or 'minimum' in msg)

ok, msg = said(verify_sketch, '  ордината не та',
               {'maxima': [(pi / 2, 2)]}, Abs(F22), domain=Interval(0, pi))
t('неверная ордината отвергнута', not ok)
t('и показано верное значение', '3' in msg)

t('неверное y-пересечение отвергнуто',
  not verify_sketch('  y-пересечение', {'y_intercept': 0},
                    (4 * x + 2) / (x - 2)))
t('чужая наклонная асимптота отвергнута',
  not verify_sketch('  не та прямая', {'oblique_asymptotes': [5 * x + 4]},
                    F25))
t('пропущенная наклонная асимптота отвергнута',
  not verify_sketch('  только одна ветвь',
                    {'oblique_asymptotes': [5 * x + 5]}, Abs(F25)))
ok, msg = said(verify_sketch, '  чужой ключ', {'inflexions': [0]}, F25)
t('неизвестный ключ отвергнут', not ok)
t('и перечислены известные', 'x_intercepts' in msg)
t('не словарь — отдельная ошибка',
  not verify_sketch('  список вместо словаря', [1, 2], F25))
t('пустой эскиз не падает',
  not verify_sketch('  ещё не решено', {'maxima': ...}, F25))
t('дыра внутри словаря тоже',
  not verify_sketch('  дыра в списке', {'maxima': [(0, ...)]}, F25))

print('\n=== verify_sketch: что считается из самой функции ===')
facts = _sketch_facts(Abs(F22), x, _as_domain(Interval(0, pi), x))
t('два излома найдены', len(facts['cusps']) == 2)
t('одна гладкая вершина найдена',
  len(facts['maxima']) == 1 and len(facts['minima']) == 0)
t('концы отрезка найдены', len(facts['endpoints']) == 2)
facts = _sketch_facts(F25, x, _as_domain(None, x))
t('вертикальная асимптота найдена',
  len(facts['vertical_asymptotes']) == 1
  and abs(facts['vertical_asymptotes'][0] + 0.5) < 1e-9)
t('наклонная асимптота найдена одна',
  len(facts['oblique_asymptotes']) == 1)
t('нулей у этой функции нет', facts['x_intercepts'] == [])
facts = _sketch_facts(15 / F25, x, _as_domain(None, x))
t('у обратной величины горизонтальная асимптота',
  facts['horizontal_asymptotes'] == [0.0])
t('и вертикальных асимптот нет', facts['vertical_asymptotes'] == [])

print('\n=== чего проверки не делают ===')
# verify_transform не требует кратчайшего описания: лишний, но верный
# шаг проходит. В markscheme за это тоже не снимают.
t('лишний верный шаг проходит',
  verify_transform('  туда и обратно',
                   [('shift_x', 1), ('shift_x', -1), ('shift_y', 3)],
                   x**2, x**2 + 3))
# verify_sketch не смотрит на форму кривой между особенностями: у двух
# разных функций с одинаковым списком особенностей вердикт одинаков.
# «Asymptotic behaviour» и выпуклость остаются на рисунке.
t('одинаковые особенности — одинаковый вердикт',
  verify_sketch('  парабола', {'x_intercepts': [-1, 1], 'y_intercept': -1},
                x**2 - 1, domain=Interval(-2, 2))
  and verify_sketch('  не парабола',
                    {'x_intercepts': [-1, 1], 'y_intercept': -1},
                    (x**2 - 1) * (1 + (x / 4)**2), domain=Interval(-2, 2)))
# verify_sketch ничего не знает про то, какой буквой названа функция,
# и про подписи на осях: рисунок он не видит вовсе.
t('область не задана — концов нет',
  _sketch_facts(acos(x), x, _as_domain(None, x))['endpoints'] == [])
# Координаты сверяются с точностью до трёх значащих цифр — так их
# принимает и экзамен. Значит, ошибка в четвёртой цифре пройдёт, и это
# не недосмотр, а измеренная граница проверки.
t('ошибка в четвёртой цифре проходит',
  verify_sketch('  1.089 вместо 1.0887', {'maxima': [(0.685, 1.089)]},
                T23, domain=Interval(-1, 1)))
t('а ошибка в третьей — нет',
  not verify_sketch('  1.1 вместо 1.0887', {'maxima': [(0.685, 1.1)]},
                    T23, domain=Interval(-1, 1)))

print('\n=== чем новая проверка отличается от старых ===')
# verify_identity сверяет два выражения, verify_transform — путь между
# ними. Одно и то же равенство они читают по-разному: тождество верно
# всегда, а последовательность шагов бывает верной или нет.
t('verify_identity не видит порядка, verify_transform видит',
  verify_identity('  сжатый синус тождественен', sin(2 * (x + pi / 4)),
                  sin(2 * x + pi / 2))
  and not verify_transform('  а шаги в этом порядке — нет',
                           [('shift_x', -pi / 4), ('stretch_x', R(1, 2))],
                           sin(x), sin(2 * x + pi / 2)))
# check_domain про множество, verify_sketch — про точки на кривой.
# Область определения и список особенностей это разные ответы.
t('check_domain и verify_sketch отвечают на разные вопросы',
  check_domain('  область arccos', Interval(-1, 1),
               digest(sp.srepr(Interval(-1, 1))))
  and verify_sketch('  а особенности — другое',
                    {'endpoints': [(-1, pi), (1, 0)]},
                    acos(x), domain=Interval(-1, 1)))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
