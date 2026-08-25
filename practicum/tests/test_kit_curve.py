"""Проверяет механику проверок из темы исследования функции.

Тема даёт восьмое в серии понятие равенства ответов. A3 сверял значения,
A4 — форму записи, A8 — множества, B1 — уравнения, C1 — конфигурацию,
B2 — функцию по тому, что она отменяет, B3 — картинку по списку
особенностей. Здесь ответом служит **прямая**, и верна она не тогда, когда
совпала с эталоном, а тогда, когда кривая к ней действительно приближается.

verify_asymptotes: каждая названная прямая проверяется пределом — по самому
определению асимптоты, а не по списку. Измеряется, что число вместо
уравнения не проходит (markscheme: «must be written as an equation with
y ='), что прямая, к которой график не приближается, отвергается,
и что пропущенная асимптота — отдельное сообщение и отдельный балл.

verify_range: проверка ничего не решает за вас, она спрашивает у самой
функции, достигается ли значение. Измеряется главное, ради чего тема
существует, — что ≤ и < различаются, и что сдвинутая граница не проходит.

Заодно измерено, чего проверки не делают: verify_asymptotes ничего не
знает о том, как асимптота найдена, а verify_range пропускает значения,
о которых не может судить, и говорит, сколько их было.
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
from kit import _as_line, _asymptote_truth, _attained, _as_domain

res = []
R = sp.Rational
d_ = sp.Symbol('d', positive=True)


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


def said(fn, *args, **kwargs):
    """Вердикт вместе с тем, что он напечатал."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


# Функции архива, на которых всё и меряется.
F_NOV21 = (x**2 - x - 12) / (2*x - 15)          # ноябрь 2021 P2 Q10
F_NOV23 = (x**2 - 14*x + 24) / (2*x + 6)        # ноябрь 2023 P2 Q11
F_MAY21 = (4*x**2 - 1) / (3*x + 2)              # май 2021 TZ1 P2 Q11(e)
F_HYP = (2*x + 4) / (3 - x)                     # ноябрь 2021 P1 Q2
F_TWO = 1 / (x**2 - 2*x - 3)                    # май 2022 TZ2 P1 Q11(a)

print('=== verify_asymptotes: что принимается ===')
t('вертикальная и наклонная у ноября 2021',
  verify_asymptotes('  x = 15/2 и y = x/2 + 13/4',
                    [Eq(x, R(15, 2)), Eq(y, x/2 + R(13, 4))], F_NOV21))
t('тот же ответ уравнением знаменателя',
  verify_asymptotes('  2x - 15 = 0', Eq(2*x - 15, 0), F_NOV21,
                    kinds=('vertical',)))
t('тот же ответ, записанный иначе',
  verify_asymptotes('  y - x/2 = 13/4', [Eq(x, R(15, 2)), Eq(y - x/2, R(13, 4))],
                    F_NOV21))
t('порядок прямых не важен',
  verify_asymptotes('  сначала наклонная',
                    [Eq(y, x/2 + R(13, 4)), Eq(x, R(15, 2))], F_NOV21))
t('вертикальная и горизонтальная у гиперболы',
  verify_asymptotes('  x = 3 и y = -2', [Eq(x, 3), Eq(y, -2)], F_HYP))
t('две вертикальные и одна горизонтальная',
  verify_asymptotes('  x = -1, x = 3, y = 0',
                    [Eq(x, -1), Eq(x, 3), Eq(y, 0)], F_TWO))
t('наклонная у мая 2021',
  verify_asymptotes('  y = 4x/3 - 8/9',
                    [Eq(x, -R(2, 3)), Eq(y, 4*x/3 - R(8, 9))], F_MAY21))
t('вертикальная логарифма — граница области, а не ноль знаменателя',
  verify_asymptotes('  x = 0', Eq(x, 0), 2*log(x) - log(d_),
                    domain=Interval.open(0, oo), kinds=('vertical',)))
t('горизонтальная арксинуса — только через предел',
  verify_asymptotes('  y = pi/2', Eq(y, pi/2), asin((x**2 - 1)/(x**2 + 1)),
                    kinds=('horizontal',)))
t('одна прямая без списка',
  verify_asymptotes('  x = -3', Eq(x, -3), F_NOV23, kinds=('vertical',)))

print('\n=== verify_asymptotes: что отвергается ===')
out, text = said(verify_asymptotes, '  просто -3', [-3], F_NOV23,
                 kinds=('vertical',))
t('число вместо уравнения не проходит', not out and 'not the equation' in text
  or not out and 'не уравнение' in text)
out, text = said(verify_asymptotes, '  x = 3', [Eq(x, 3)], F_NOV23,
                 kinds=('vertical',))
t('прямая не на месте: график к ней не приближается',
  not out and ('не приближается' in text or 'does not approach' in text))
out, text = said(verify_asymptotes, '  только вертикальная', [Eq(x, -3)], F_NOV23)
t('пропущенная наклонная — отдельное сообщение',
  not out and ('пропущена' in text or 'missing' in text))
out, text = said(verify_asymptotes, '  y = 1/2', [Eq(x, -3), Eq(y, R(1, 2))],
                 F_NOV23)
t('горизонтальная вместо наклонной отвергается', not out)
out, text = said(verify_asymptotes, '  y = x/2', [Eq(x, -3), Eq(y, x/2)], F_NOV23)
t('верный наклон с потерянным свободным членом отвергается', not out)
out, text = said(verify_asymptotes, '  y = 4/3', [Eq(y, R(4, 3))], F_MAY21,
                 kinds=('horizontal',))
t('отношение старших коэффициентов у неправильной дроби — не асимптота',
  not out)
out, text = said(verify_asymptotes, '  y = -2', [Eq(y, -2)], F_HYP,
                 kinds=('vertical',))
t('ответ не того вида, чем спрашивали',
  not out and ('спрашивают только' in text or 'asks' in text))
out, text = said(verify_asymptotes, '  одна из двух', [Eq(x, -1), Eq(y, 0)], F_TWO)
t('пропущенная вторая вертикальная отвергается', not out)
t('пустой ответ не падает, а печатает пробел',
  not verify_asymptotes('  ещё не решено', [...], F_NOV23))
out, text = said(verify_asymptotes, '  y = x^2', [Eq(y, x**2)], F_NOV23)
t('парабола не прямая', not out)

print('\n=== verify_asymptotes: чего проверка не делает ===')
# Проверка смотрит на прямую, а не на путь к ней. Деление в столбик,
# приравнивание коэффициентов и предел разности дают один и тот же ответ,
# и в markscheme это три равноправных метода.
t('способ получения асимптоты проверке не виден',
  verify_asymptotes('  делением', [Eq(x, -3), Eq(y, x/2 - R(17, 2))], F_NOV23)
  and verify_asymptotes('  пределом', [Eq(x, -3), Eq(y, x/2 - R(17, 2))],
                        F_NOV23))
# Наклонная и горизонтальная — это одна и та же проверка предела разности,
# и проверка не спорит о названии: y = 2 у функции с нулевым наклоном
# принимается и как горизонтальная, и в списке всех асимптот.
t('название вида берётся из самой прямой, а не со слов',
  _as_line(Eq(y, 2), x, y)[0] == 'horizontal'
  and _as_line(Eq(y, x/2 + 1), x, y)[0] == 'oblique'
  and _as_line(Eq(x, 2), x, y)[0] == 'vertical')
# Асимптота на одном конце — асимптота. y = 0 у e^x есть только слева,
# и это правильный ответ.
t('односторонней асимптоты достаточно',
  verify_asymptotes('  y = 0 у экспоненты', Eq(y, 0), exp(x),
                    kinds=('horizontal',)))

print('\n=== _asymptote_truth: что считается истиной ===')
truth = _asymptote_truth(F_NOV23, x, _as_domain(None, x))
t('у неправильной дроби вертикальная и наклонная, горизонтальной нет',
  truth['vertical'] == [-3] and not truth['horizontal']
  and len(truth['oblique']) == 1
  and sp.simplify(truth['oblique'][0] - (x/2 - R(17, 2))) == 0)
truth = _asymptote_truth(F_TWO, x, _as_domain(None, x))
t('у 1/(x^2-2x-3) две вертикальные и одна горизонтальная',
  sorted(truth['vertical']) == [-1, 3] and truth['horizontal'] == [0]
  and not truth['oblique'])
truth = _asymptote_truth(2*log(x) - log(d_), x, _as_domain(Interval.open(0, oo), x))
t('у логарифма вертикальная на границе области',
  truth['vertical'] == [0] and not truth['horizontal'])

print('\n=== verify_range: что принимается ===')
t('множество значений квадратичной',
  verify_range('  y >= -5', (y >= -5), 6*x**2 - 12*x + 1))
t('то же самое промежутком',
  verify_range('  Interval(-5, oo)', Interval(-5, oo), 6*x**2 - 12*x + 1))
t('разрыв в множестве значений неправильной дроби',
  verify_range('  y <= -10-5sqrt3 или y >= -10+5sqrt3',
               Union(Interval(-oo, -10 - 5*sqrt(3)),
                     Interval(-10 + 5*sqrt(3), oo)), F_NOV23))
t('множество значений через дискриминант',
  verify_range('  (5±sqrt13)/6', Union(Interval(-oo, (5 - sqrt(13))/6),
                                       Interval((5 + sqrt(13))/6, oo)),
               (2*x - 5)/(x**2 - 3)))
t('полуоткрытый ответ: асимптота не достигается, а максимум достигается',
  verify_range('  -3/2 < y <= 2', Interval.Lopen(R(-3, 2), 2),
               -(3*x - 2)/(2*x + 1), domain=Interval(0, oo)))
t('ограниченная область — ограниченное множество значений',
  verify_range('  0 <= y <= sqrt(3)', Interval(0, sqrt(3)),
               sqrt(x**2 - 1), domain=Interval(1, 2)))

print('\n=== verify_range: что отвергается ===')
out, text = said(verify_range, '  y >= -4', (y >= -4), 6*x**2 - 12*x + 1)
t('граница сдвинута внутрь: потерянные значения находятся',
  not out and ('принимает' in text or 'does take' in text))
out, text = said(verify_range, '  y >= -6', (y >= -6), 6*x**2 - 12*x + 1)
t('граница сдвинута наружу: лишние значения находятся',
  not out and ('решений не имеет' in text or 'no solution' in text))
out, text = said(verify_range, '  строгое неравенство',
                 Union(Interval.open(-oo, -10 - 5*sqrt(3)),
                       Interval.open(-10 + 5*sqrt(3), oo)), F_NOV23)
t('строгое вместо нестрогого не проходит: это разные баллы', not out)
out, text = said(verify_range, '  -3/2 <= y <= 2', Interval(R(-3, 2), 2),
                 -(3*x - 2)/(2*x + 1), domain=Interval(0, oo))
t('горизонтальная асимптота включена в ответ — не проходит', not out)
out, text = said(verify_range, '  все действительные', sp.S.Reals, F_NOV23)
t('разрыв потерян', not out)
out, text = said(verify_range, '  просто число', 5, F_NOV23)
t('число вместо множества не проходит', not out)
t('пустой ответ не падает', not verify_range('  ещё не решено', ..., F_NOV23))

print('\n=== verify_range: чего проверка не делает ===')
# Проверка ничего не знает про дискриминант, вершину и производную:
# она спрашивает у функции, достигается ли значение. Поэтому ответ,
# полученный любым из трёх способов markscheme, проходит одинаково.
t('способ получения множества значений проверке не виден',
  verify_range('  через вершину', (y >= -5), 6*x**2 - 12*x + 1)
  and verify_range('  через дискриминант', (y >= -5), 6*x**2 - 12*x + 1))
# Значение, о котором нельзя судить, пропускается, а не роняет проверку,
# и число пропусков печатается.
out, text = said(verify_range, '  трансцендентное уравнение',
                 Interval(-1, 1), sin(x) + sin(pi*x)/1000)
t('неразрешимые точки пропускаются и считаются',
  ('пропущено' in text or 'skipped' in text) or out)
# Множество значений и множество решений неравенства — разные вопросы,
# и отвечают на них разные проверки.
t('verify_range и verify_solution_set спрашивают о разном',
  verify_range('  значения квадратичной', (y >= -5), 6*x**2 - 12*x + 1)
  and verify_solution_set('  а решения неравенства', Interval(0, 2),
                          6*x**2 - 12*x + 1 <= 1))

print('\n=== _attained: чем меряется достижимость ===')
region = _as_domain(None, x)
t('значение внутри разрыва не достигается',
  _attained(F_NOV23, x, region, sp.Integer(-10)) is False)
t('значение вне разрыва достигается',
  _attained(F_NOV23, x, region, sp.Integer(0)) is True)
t('горизонтальная асимптота не достигается',
  _attained(-(3*x - 2)/(2*x + 1), x, _as_domain(Interval(0, oo), x),
            R(-3, 2)) is False)
t('вершина параболы достигается',
  _attained(6*x**2 - 12*x + 1, x, region, sp.Integer(-5)) is True)

print('\n=== новое и старое отвечают на разные вопросы ===')
# verify_sketch считает асимптоты числами в списке особенностей;
# verify_asymptotes требует уравнение прямой. В экзамене это разные баллы:
# «write down the equations of the asymptotes» и «sketch, clearly
# indicating any asymptotes» спрашивают разное.
t('verify_sketch берёт число, verify_asymptotes требует уравнение',
  verify_sketch('  асимптоты в эскизе',
                {'vertical_asymptotes': [-3]}, F_NOV23)
  and not said(verify_asymptotes, '  а тут нужна прямая', [-3], F_NOV23,
               kinds=('vertical',))[0]
  and verify_asymptotes('  вот прямая', Eq(x, -3), F_NOV23,
                        kinds=('vertical',)))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
