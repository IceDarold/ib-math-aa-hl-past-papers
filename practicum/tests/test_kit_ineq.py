"""Проверяет механику проверок из темы неравенств.

Ответ здесь — множество, и вся тема стоит на его границе. Поэтому
verify_solution_set сравнивает множества точно, вместе с концами: −5 < x < 1
и −5 ≤ x ≤ 1 — разные ответы, и markscheme платит за это разными баллами.

verify_param_set устроен иначе: он ничего не решает, а берёт ваше множество
и проверяет само условие в точках — внутри, снаружи, на границах и рядом
с ними. Ниже измеряется, что каждая из проверок принимает и что отвергает.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import _as_set, _pieces, _scan_roots

res = []
d, p, q, s_, t_, y_ = sp.symbols('d p q s_ t_ y_')
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== _as_set: одно множество, разные записи ===')
t('Interval', _as_set(Interval(-5, 1), x) == Interval(-5, 1))
t('связка неравенств', _as_set((x >= -5) & (x <= 1), x) == Interval(-5, 1))
t('объединение через |',
  _as_set((x < -10) | (x > 6), x) == Union(Interval.open(-oo, -10),
                                           Interval.open(6, oo)))
t('S.Reals', _as_set(S.Reals, x) == S.Reals)
t('не множество и не неравенство', _as_set(sp.Integer(5), x) is None)

print('\n=== verify_solution_set: что принимается ===')
t('квадратное неравенство, май 2025 TZ1',
  verify_solution_set('  −5 ≤ x ≤ 1', Interval(-5, 1), 5 * (x + 2)**2 - 5 <= 40))
t('та же связка неравенств вместо Interval',
  verify_solution_set('  связкой', (x >= -5) & (x <= 1),
                      5 * (x + 2)**2 - 5 <= 40))
t('область сужает ответ, ноябрь 2023 TZ1',
  verify_solution_set('  d > 9', Interval.open(9, oo), d**2 - 9 * d > 0,
                      var=d, domain=Interval.open(0, oo)))
t('дробно-рациональное с выколотым полюсом',
  verify_solution_set('  два куска',
                      Union(Interval.open(-oo, -10 - 2 * sqrt(31)),
                            Interval.open(-3, -10 + 2 * sqrt(31))),
                      (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('модуль',
  verify_solution_set('  |x| > 1/2',
                      Union(Interval.open(-oo, -R(1, 2)),
                            Interval.open(R(1, 2), oo)),
                      (2 * Abs(x) - 1) / (Abs(x) + 1) > 0))

print('\n=== verify_solution_set: что отвергается ===')
t('строгие концы вместо нестрогих',
  not verify_solution_set('  −5 < x < 1', Interval.open(-5, 1),
                          5 * (x + 2)**2 - 5 <= 40))
t('нестрогие вместо строгих',
  not verify_solution_set('  d ≥ 9', Interval(9, oo), d**2 - 9 * d > 0,
                          var=d, domain=Interval.open(0, oo)))
t('забыли про область d > 0',
  not verify_solution_set('  оба куска', Union(Interval.open(-oo, 0),
                                               Interval.open(9, oo)),
                          d**2 - 9 * d > 0, var=d,
                          domain=Interval.open(0, oo)))
t('потерян второй промежуток',
  not verify_solution_set('  один кусок', Interval.open(-3, -10 + 2 * sqrt(31)),
                          (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('полюс включён в ответ',
  not verify_solution_set('  с точкой −3', Union(
      Interval.open(-oo, -10 - 2 * sqrt(31)),
      Interval.Ropen(-3, -10 + 2 * sqrt(31))),
      (x**2 - 14 * x + 24) / (2 * x + 6) > x))
t('знак неравенства перепутан',
  not verify_solution_set('  снаружи', Union(Interval.open(-oo, -5),
                                             Interval.open(1, oo)),
                          5 * (x + 2)**2 - 5 <= 40))
t('пустой ответ даёт ⬜',
  not verify_solution_set('  пусто', ..., 5 * (x + 2)**2 - 5 <= 40))
t('ответ не множество',
  not verify_solution_set('  число', sp.Integer(1), 5 * (x + 2)**2 - 5 <= 40))


# --- verify_param_set -------------------------------------------------------
# Условие берётся из самой задачи: сколько у уравнения различных
# действительных корней. Дискриминант в проверке не участвует вовсе.
def two_distinct(kv):
    return len(set(sp.real_roots(sp.Poly(x**2 + kv * x + 15 - kv, x)))) == 2


ANSWER_A = Union(Interval.open(-oo, -10), Interval.open(6, oo))

print('\n=== verify_param_set: что принимается ===')
t('k < −10 или k > 6, май 2025 TZ2',
  verify_param_set('  верное множество', ANSWER_A, two_distinct))
t('то же самое связкой неравенств',
  verify_param_set('  связкой', (k < -10) | (k > 6), two_distinct))
t('знаки корней: −9/2 < k < 0, май 2022 TZ1',
  verify_param_set('  −9/2 < k < 0', Interval.open(R(-9, 2), 0),
                   lambda kv: (len(set(sp.real_roots(
                       sp.Poly(kv * x**2 - (kv + 3) * x + 2 * kv + 9, x)))) == 2
                       and (2 * kv + 9) / kv < 0) if kv != 0 else False))

print('\n=== verify_param_set: что отвергается ===')
t('концы включены, хотя при них корень один',
  not verify_param_set('  нестрогие концы',
                       Union(Interval(-oo, -10), Interval(6, oo)), two_distinct))
t('половина ответа потеряна',
  not verify_param_set('  только k > 6', Interval.open(6, oo), two_distinct))
t('лишний промежуток',
  not verify_param_set('  всё подряд', S.Reals, two_distinct))
t('граница сдвинута',
  not verify_param_set('  k > 5', Union(Interval.open(-oo, -10),
                                        Interval.open(5, oo)), two_distinct))
t('пустой ответ даёт ⬜', not verify_param_set('  пусто', ..., two_distinct))

print('\n=== verify_param_set: None и tol ===')
# None означает «здесь численно судить нельзя»: точка пропускается.
t('точки с None пропускаются, остальные проверяются',
  verify_param_set('  с пропусками', ANSWER_A,
                   lambda kv: None if abs(float(kv)) > 25 else two_distinct(kv)))
t('если годных точек почти не осталось — честный отказ',
  not verify_param_set('  всё пропущено', ANSWER_A, lambda kv: None))
# tol нужен там, где границы найдены калькулятором и округлены до 3 з.ц.
t('округлённая граница проходит при tol',
  verify_param_set('  0.178 вместо 0.177935', Interval.open(sp.Float('0.178'), 3),
                   lambda v: 0.177935152871373 < float(v) < 3,
                   window=(-1, 5), tol=0.005))
t('та же граница без tol не проходит',
  not verify_param_set('  без допуска', Interval.open(sp.Float('0.178'), 3),
                       lambda v: 0.177935152871373 < float(v) < 3,
                       window=(-1, 5)))

print('\n=== verify_nonneg_form ===')
t('квадрат, май 2021 TZ2',
  verify_nonneg_form('  (e^{k/2}−e^{−k/2})²', (exp(k / 2) - exp(-k / 2))**2,
                     exp(k) + exp(-k) - 2))
t('квадрат разности, ноябрь 2025 TZ3',
  verify_nonneg_form('  (x−y)²', (x - y_)**2, x**2 - 2 * x * y_ + y_**2))
t('сумма квадратов',
  verify_nonneg_form('  x²+y²', x**2 + y_**2, x**2 + y_**2))
t('положительный множитель перед квадратом',
  verify_nonneg_form('  3(x−1)²', 3 * (x - 1)**2, 3 * x**2 - 6 * x + 3))
t('модуль',
  verify_nonneg_form('  |x−1|', Abs(x - 1), Abs(x - 1)))
t('раскрытый вид отвергается: неотрицательность из него не видна',
  not verify_nonneg_form('  x²−2xy+y²', x**2 - 2 * x * y_ + y_**2,
                         x**2 - 2 * x * y_ + y_**2))
t('нечётная степень',
  not verify_nonneg_form('  (x−1)³', (x - 1)**3, (x - 1)**3))
t('минус перед слагаемым',
  not verify_nonneg_form('  x²−1', x**2 - 1, x**2 - 1))
t('квадрат правильный, но не тот',
  not verify_nonneg_form('  (x+y)²', (x + y_)**2, x**2 - 2 * x * y_ + y_**2))
t('пустой ответ даёт ⬜',
  not verify_nonneg_form('  пусто', ..., x**2))

print('\n=== чем это отличается от проверок A3 и A4 ===')
# check_set сверяет набор чисел, verify_solution_set — множество вместе
# с границей. Один и тот же ответ «−5 и 1» для них означает разное:
# для первой это ответ целиком, для второй — только концы.
t('check_set видит только сами числа',
  check_set('  критические значения', [-5, 1],
            digest('|'.join(sorted(sp.srepr(sp.simplify(v)) for v in (-5, 1))))))
t('verify_solution_set требует ещё и того, что между ними',
  verify_solution_set('  отрезок целиком', Interval(-5, 1),
                      5 * (x + 2)**2 - 5 <= 40)
  and not verify_solution_set('  только концы', FiniteSet(-5, 1),
                              5 * (x + 2)**2 - 5 <= 40))
# verify_factored из A4 требовала формы записи произведения; здесь тот же
# приём применён к неравенству: доказательство «≥ 0» должно быть видно из записи.
t('verify_nonneg_form — тот же спрос на форму, что verify_factored',
  verify_factored('  форма: произведение', (x - 1) * (x + 1), x**2 - 1)
  and verify_nonneg_form('  форма: квадрат', (x - 1)**2, x**2 - 2 * x + 1))

print('\n=== _scan_roots на подстановке u = ln x ===')
# Число точек пересечения y = a^x и y = log_a x при a > 1 равно числу
# решений a^x = x, а после подстановки x = e^u — числу корней u·e^{−u} = ln a.
# Так считать устойчиво: второй корень при a → 1 уходит в бесконечность по x,
# но остаётся в разумных пределах по u.
def n_cross(a):
    return len(_scan_roots(lambda u: u * math.exp(-u) - math.log(float(a)),
                           -2, 40))


t('при 1 < a < e^{1/e} пересечений два', all(n_cross(a) == 2
  for a in (1.01, 1.1, 1.2, 1.4, 1.444)))
t('при a > e^{1/e} пересечений нет', all(n_cross(a) == 0
  for a in (1.4448, 1.5, 2, 5)))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
