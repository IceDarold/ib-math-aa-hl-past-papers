"""Проверяет механику проверок из темы композиции и обратных функций.

Тема даёт шестое в серии понятие равенства ответов. A3 сверял значения,
A4 — форму записи, A8 — множества, B1 — уравнения, C1 — конфигурацию.
Здесь ответ это **функция**, и верна она тогда, когда отменяет исходную:
эталона нет вовсе, как в verify_ode.

Главное, что здесь измеряется, — что проверка ловит неверную ветвь корня.
Ветвь выбирает область из условия, за этот выбор в markscheme стоит
отдельный R1, и именно на нём проверка обязана срабатывать.

Заодно измерено, чего проверка не делает: она ничего не знает про область
самой обратной, и рядом обязан стоять check_domain.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import _domain_points

res = []
a_, c_, m_ = sp.symbols('a_ c_ m_')
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== verify_inverse: что принимается ===')
# May 2023 TZ1 P1 Q1(c): рациональная функция, обратная считается алгеброй.
t('рациональная, май 2023 TZ1',
  verify_inverse('  f⁻¹ = (4x+7)/(2x−7)', (4 * x + 7) / (2 * x - 7),
                 (7 * x + 7) / (2 * x - 4), domain=Interval(3, 9)))
# May 2022 TZ1 P2 Q10(b): здесь ветвь выбирается областью 1 ≤ x ≤ 2.
t('корень, май 2022 TZ1',
  verify_inverse('  f⁻¹ = √(x²+1)', sqrt(x**2 + 1), sqrt(x**2 - 1),
                 domain=Interval(1, 2)))
# May 2025 TZ2 P1 Q10(b): показательная и логарифм — обратные друг другу.
t('логарифм и степень, май 2025 TZ2',
  verify_inverse('  g⁻¹ = 2^(x−1)', 2**(x - 1), 1 + log(x, 2),
                 domain=Interval(R(1, 4), 8)))
# May 2022 TZ2 P1 Q11(b): выделение полного квадрата, область x > 3.
t('дробь с полным квадратом, май 2022 TZ2',
  verify_inverse('  g⁻¹ = 1 + √(4x²+x)/x', 1 + sqrt(4 * x**2 + x) / x,
                 1 / (x**2 - 2 * x - 3), domain=Interval.open(3, oo)))
# May 2025 TZ1 P2 Q12(d): область не замкнута справа, K = 1/√2.
t('полузакрытая область, май 2025 TZ1',
  verify_inverse('  g⁻¹ = √((1−x)/(2x))', sqrt((1 - x) / (2 * x)),
                 1 / (1 + 2 * x**2), domain=Interval.Ropen(0, 1 / sqrt(2))))
# May 2021 TZ2 P2 Q12(d): обратная к arcsin-конструкции.
t('арксинус, май 2021 TZ2',
  verify_inverse('  g⁻¹ = √((1+sin x)/(1−sin x))',
                 sqrt((1 + sin(x)) / (1 - sin(x))),
                 asin((x**2 - 1) / (x**2 + 1)), domain=Interval(0, 6)))
t('эквивалентная запись той же функции',
  verify_inverse('  (x + √(4x²+x))/x', (x + sqrt(4 * x**2 + x)) / x,
                 1 / (x**2 - 2 * x - 3), domain=Interval.open(3, oo)))

print('\n=== verify_inverse: что отвергается ===')
t('не та ветвь корня — тот самый R1',
  not verify_inverse('  −√(x²+1)', -sqrt(x**2 + 1), sqrt(x**2 - 1),
                     domain=Interval(1, 2)))
t('не та ветвь у арксинуса',
  not verify_inverse('  минус', -sqrt((1 + sin(x)) / (1 - sin(x))),
                     asin((x**2 - 1) / (x**2 + 1)), domain=Interval(0, 6)))
t('дробь перевёрнута',
  not verify_inverse('  (1−sin x)/(1+sin x)',
                     sqrt((1 - sin(x)) / (1 + sin(x))),
                     asin((x**2 - 1) / (x**2 + 1)), domain=Interval(0, 6)))
t('знак в знаменателе — обычная описка',
  not verify_inverse('  (4x+7)/(2x+7)', (4 * x + 7) / (2 * x + 7),
                     (7 * x + 7) / (2 * x - 4), domain=Interval(3, 9)))
t('сама функция вместо обратной',
  not verify_inverse('  f вместо f⁻¹', sqrt(x**2 - 1), sqrt(x**2 - 1),
                     domain=Interval(1, 2)))
t('обратная перепутана с 1/f',
  not verify_inverse('  1/f', 1 / sqrt(x**2 - 1), sqrt(x**2 - 1),
                     domain=Interval(1, 2)))
t('запись из корпуса для мая 2022 TZ2 не проходит',
  not verify_inverse('  (1+√(x²+4x))/x', (1 + sqrt(x**2 + 4 * x)) / x,
                     1 / (x**2 - 2 * x - 3), domain=Interval.open(3, oo)))
t('незаполненный ответ даёт ⬜, а не падение',
  not verify_inverse('  пусто', ..., sqrt(x**2 - 1), domain=Interval(1, 2)))

print('\n=== направление проверки выбрано не случайно ===')
# f(got(s)) = s неверную ветвь пропускает: минус уходит под квадрат.
# got(f(t)) = t её ловит. Поэтому проверка идёт именно в эту сторону.
wrong = -sqrt(x**2 + 1)
forward = sp.simplify(sqrt(wrong**2 - 1) - x)          # f(got(x)) − x
t('f(g(x)) = x минус не различает',
  sp.simplify(forward.subs(x, R(3, 2))) == 0)
t('g(f(x)) = x минус различает',
  sp.simplify(wrong.subs(x, sqrt(sp.Rational(9, 4) - 1)) - R(3, 2)) != 0)

print('\n=== область из условия участвует в ответе ===')
# Та же формула, другая область — и обратная становится другой.
t('на [1, 2] верна +√(x²+1)',
  verify_inverse('  плюс', sqrt(x**2 + 1), sqrt(x**2 - 1),
                 domain=Interval(1, 2)))
t('на [−2, −1] верна −√(x²+1)',
  verify_inverse('  минус', -sqrt(x**2 + 1), sqrt(x**2 - 1),
                 domain=Interval(-2, -1)))
t('и наоборот: плюс на отрицательной области не проходит',
  not verify_inverse('  плюс слева', sqrt(x**2 + 1), sqrt(x**2 - 1),
                     domain=Interval(-2, -1)))

print('\n=== _domain_points: концы берутся тогда, когда входят ===')
pts = _domain_points(Interval(1, 2))
t('замкнутый промежуток даёт оба конца', 1 in pts and 2 in pts)
pts = _domain_points(Interval.open(1, 2))
t('открытый не даёт ни одного', 1 not in pts and 2 not in pts)
pts = _domain_points(Interval.Ropen(0, 1))
t('полуоткрытый даёт только левый', 0 in pts and 1 not in pts)
t('бесконечный конец обрезается',
  all(sp.N(p) <= 14 for p in _domain_points(Interval.open(3, oo))))

print('\n=== check_domain: запись не важна, концы важны ===')
D_GRAPH = digest(sp.srepr(Interval(-3, 5)))
D_SQRT3 = digest(sp.srepr(Interval(0, sqrt(3))))
D_HALF = digest(sp.srepr(Interval.Lopen(R(1, 2), 1)))
t('интервалом', check_domain('  [−3, 5]', Interval(-3, 5), D_GRAPH))
t('неравенством', check_domain('  −3 ≤ x ≤ 5', (x >= -3) & (x <= 5), D_GRAPH))
t('иррациональный конец',
  check_domain('  [0, √3]', Interval(0, sqrt(3)), D_SQRT3))
t('тот же конец десятичной записью не проходит',
  not check_domain('  [0, 1.73]', Interval(0, 1.73), D_SQRT3))
t('выколотый левый конец, май 2025 TZ1',
  check_domain('  1/2 < x ≤ 1', (x > R(1, 2)) & (x <= 1), D_HALF))
t('замкнутый вместо выколотого — другой ответ',
  not check_domain('  [1/2, 1]', Interval(R(1, 2), 1), D_HALF))
t('открытый справа — тоже другой',
  not check_domain('  (1/2, 1)', Interval.open(R(1, 2), 1), D_HALF))
t('не множество вовсе',
  not check_domain('  число', 5, D_GRAPH))
t('незаполненный ответ даёт ⬜', not check_domain('  пусто', ..., D_GRAPH))

print('\n=== чем новая проверка отличается от старых ===')
# check_set — про наборы отдельных значений, check_domain — про промежутки
# с концами. Один и тот же ответ они читают по-разному.
t('check_set видит набор, check_domain — промежуток',
  check_set('  {−3, 5}', [-3, 5],
            digest('|'.join(sorted(sp.srepr(sp.simplify(v))
                                   for v in (-3, 5)))))
  and check_domain('  [−3, 5]', Interval(-3, 5), D_GRAPH))
# verify_inverse ничего не знает про область самой обратной: это отдельный
# ответ, и рядом обязан стоять check_domain. Измеряем предел прямо.
t('verify_inverse не проверяет область обратной',
  verify_inverse('  формула верна', sqrt(x**2 + 1), sqrt(x**2 - 1),
                 domain=Interval(1, 2))
  and not check_domain('  а область названа неверно', Interval(0, 5),
                       D_SQRT3))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
