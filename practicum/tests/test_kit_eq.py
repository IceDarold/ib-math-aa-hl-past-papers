"""Проверяет механику проверок из темы уравнений.

Тема даёт два новых требования к проверке. Первое: ответом бывает само
уравнение, и сравнивать надо уравнения — с точностью до переноса слагаемых
и множителя-числа, но не с точностью до домножения на букву.

Второе: решение уравнения не сохраняет равносильность. Возведение в квадрат
и умножение на знаменатель добавляют корни, деление на выражение
с переменной их теряет. verify_root_set смотрит на список с обеих сторон
и различает эти два случая в сообщениях — ниже измеряется, что он ловит.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import _as_domain, _satisfies

res = []
d, m, p, q, s, a_, b_ = sp.symbols('d m p q s a_ b_')
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== verify_equation: что принимается ===')
t('ровно то же уравнение, май 2025 TZ3',
  verify_equation('  x² − (m+1)x + 2 = 0', Eq(x**2 - (m + 1) * x + 2, 0),
                  x**2 - (m + 1) * x + 2))
t('слагаемые перенесены',
  verify_equation('  всё слева', x**2 - x - 1 - (m * x - 3),
                  x**2 - (m + 1) * x + 2))
t('записано выражением, а не Eq',
  verify_equation('  без Eq', x**2 - (m + 1) * x + 2,
                  Eq(x**2 - (m + 1) * x + 2, 0)))
t('умножено на 2',
  verify_equation('  множитель 2', 2 * x**2 - 2 * (m + 1) * x + 4,
                  x**2 - (m + 1) * x + 2))
t('умножено на −1',
  verify_equation('  множитель −1', -x**2 + (m + 1) * x - 2,
                  x**2 - (m + 1) * x + 2))
t('обе части не в нуле',
  verify_equation('  x² + 2 = (m+1)x', Eq(x**2 + 2, (m + 1) * x),
                  x**2 - (m + 1) * x + 2))
t('логарифмическое приведение, ноябрь 2023 TZ2',
  verify_equation('  x² − 2dx + 9d = 0', Eq(x**2, 2 * d * x - 9 * d),
                  x**2 - 2 * d * x + 9 * d))

print('\n=== verify_equation: что отвергается ===')
t('другое уравнение',
  not verify_equation('  знак у 2', x**2 - (m + 1) * x - 2,
                      x**2 - (m + 1) * x + 2))
t('домножено на букву — множество корней меняется',
  not verify_equation('  умножили на d', d * x**2 - 2 * d**2 * x + 9 * d**2,
                      x**2 - 2 * d * x + 9 * d))
t('домножено на выражение с переменной',
  not verify_equation('  умножили на x', x**3 - 2 * d * x**2 + 9 * d * x,
                      x**2 - 2 * d * x + 9 * d))
t('уравнение сократилось в 0 = 0',
  not verify_equation('  0 = 0', Eq(x**2 + 1, x**2 + 1),
                      x**2 - (m + 1) * x + 2))
t('placeholder не заполнен',
  not verify_equation('  пусто', ..., x**2 - (m + 1) * x + 2))

print('\n=== verify_root_set: что принимается ===')
t('нуль дробной функции, май 2023 TZ1',
  verify_root_set('  x = −1', [-1], (7 * x + 7) / (2 * x - 4)))
t('квадратное с областью, май 2021 TZ1 P3',
  verify_root_set('  s = 4', [4], Eq(s**2, 4 * s), var=s,
                  domain=Interval.open(0, oo)))
t('область можно задать неравенством',
  verify_root_set('  s = 4', [4], Eq(s**2, 4 * s), var=s, domain=s > 0))
t('область можно задать парой границ',
  verify_root_set('  s = 4', [4], Eq(s**2, 4 * s), var=s, domain=(1, 10)))
t('логарифмическое, май 2021 TZ2',
  verify_root_set('  a = √17', [sqrt(17)], log(x**2 - 16),
                  domain=Interval.open(4, oo)))
t('показательное, сводится к квадратному заменой',
  verify_root_set('  x = −1', [-1], 3 * 9**x + 5 * 3**x - 2))
t('два корня, ноябрь 2023 TZ2',
  verify_root_set('  10 ± √10', [10 - sqrt(10), 10 + sqrt(10)],
                  x**2 - 20 * x + 90))
t('множеством вместо списка',
  verify_root_set('  FiniteSet', FiniteSet(10 - sqrt(10), 10 + sqrt(10)),
                  x**2 - 20 * x + 90))
t('иррациональное: корень один, второй лишний',
  verify_root_set('  x = 4', [4], sqrt(x + 5) - x + 1))
t('уравнение без корней — пустой список',
  verify_root_set('  корней нет', [], x**2 + 1))

print('\n=== verify_root_set: лишние корни ===')
# Возведение в квадрат: у √(x+5) = x − 1 после квадрата корни 4 и −1,
# но −1 даёт √4 = −2 — в исходное уравнение он не подставляется.
t('корень, появившийся при возведении в квадрат',
  not verify_root_set('  4 и −1', [4, -1], sqrt(x + 5) - x + 1))
t('корень вне области условия',
  not verify_root_set('  ±√17', [-sqrt(17), sqrt(17)], log(x**2 - 16),
                      domain=Interval.open(4, oo)))
t('отброшенный по смыслу корень записан в ответ',
  not verify_root_set('  s = 0 и 4', [0, 4], Eq(s**2, 4 * s), var=s,
                      domain=Interval.open(0, oo)))
t('корень в полюсе знаменателя',
  not verify_root_set('  x = 2', [2], (x - 2) / (x**2 - 4)))
t('один и тот же корень дважды',
  not verify_root_set('  4 и 4', [4, 4], Eq(s**2, 4 * s), var=s,
                      domain=Interval.open(0, oo)))

print('\n=== verify_root_set: потерянные корни ===')
t('найден один корень из двух',
  not verify_root_set('  только 10 + √10', [10 + sqrt(10)],
                      x**2 - 20 * x + 90))
t('деление на x потеряло корень',
  not verify_root_set('  только 4', [4], Eq(s**2, 4 * s), var=s))
t('пустой ответ там, где корни есть',
  not verify_root_set('  корней нет', [], x**2 - 20 * x + 90))
t('placeholder не заполнен',
  not verify_root_set('  пусто', [...], x**2 - 20 * x + 90))

print('\n=== _satisfies: три исхода вместо двух ===')
t('подставляется', _satisfies(x**2 - 4, x, 2) is True)
t('не подставляется', _satisfies(x**2 - 4, x, 3) is False)
t('не определено в полюсе', _satisfies(1 / (x - 2), x, 2) is None)
t('не определено под логарифмом', _satisfies(log(x - 2), x, 1) is None)
t('_as_domain: None это вся прямая', _as_domain(None, x) == S.Reals)
t('_as_domain: пара границ', _as_domain((0, 5), x) == Interval(0, 5))
t('_as_domain: неравенство', _as_domain(x > 4, x) == Interval.open(4, oo))

print('\n=== verify_vertex_form: форма записи ===')
t('май 2025 TZ1: 5(x+2)² − 5',
  verify_vertex_form('  вершинная форма', 5 * (x + 2)**2 - 5,
                     5 * (x + 1) * (x + 3)))
t('k = 0 — слагаемого может не быть',
  verify_vertex_form('  без свободного члена', 2 * (x - 3)**2,
                     2 * x**2 - 12 * x + 18))
t('раскрытая скобка формой не является',
  not verify_vertex_form('  5x² + 20x + 15', 5 * x**2 + 20 * x + 15,
                         5 * (x + 1) * (x + 3)))
t('произведение формой не является',
  not verify_vertex_form('  5(x+1)(x+3)', 5 * (x + 1) * (x + 3),
                         5 * (x + 1) * (x + 3)))
t('в квадрате не (x − h), а (2x − 3)',
  not verify_vertex_form('  (2x−3)² − 4', (2 * x - 3)**2 - 4,
                         4 * x**2 - 12 * x + 5))
t('квадрат верный, но выражение другое',
  not verify_vertex_form('  5(x+2)² − 4', 5 * (x + 2)**2 - 4,
                         5 * (x + 1) * (x + 3)))
t('четвёртая степень вместо квадрата',
  not verify_vertex_form('  (x+2)⁴', (x + 2)**4, (x + 2)**4))

print('\n=== чем новые проверки отличаются от старых ===')
# A4 требовала произведения линейных множителей, A8 — множества,
# здесь — уравнения: одно и то же содержание, три разных требования к записи.
t('verify_equation допускает множитель, verify_identity — нет',
  verify_equation('  ×2 как уравнение', 2 * x**2 - 4, x**2 - 2)
  and not verify_identity('  ×2 как тождество', 2 * x**2 - 4, x**2 - 2))
# verify_roots сканирует отрезок численно и потому просит его границы;
# verify_root_set решает уравнение точно и работает на всей прямой.
t('verify_roots просит отрезок, verify_root_set обходится без него',
  verify_roots('  на [0, 20]', [10 - sqrt(10), 10 + sqrt(10)],
               x**2 - 20 * x + 90, (0, 20))
  and verify_root_set('  на всей прямой', [10 - sqrt(10), 10 + sqrt(10)],
                      x**2 - 20 * x + 90))
# Параметрические задания темы проверяются машинкой из A8: множество значений
# буквы сверяется не с эталоном, а с самим условием задачи.
t('verify_param_set из A8 работает и здесь',
  verify_param_set('  касание при m = −1 ± 2√2',
                   FiniteSet(-1 - 2 * sqrt(2), -1 + 2 * sqrt(2)),
                   lambda mv: len(sp.roots(sp.Poly(x**2 - (mv + 1) * x + 2,
                                                   x))) == 1, var=m))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
