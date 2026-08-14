"""Проверяет механику проверок из темы многочленов.

Главное отличие от A3: здесь форма записи входит в задачу. «Представьте
в виде произведения линейных множителей» — просьба не к числу, а к записи,
и ответ, равный исходному многочлену, но записанный одной строкой, неверен.
Поэтому verify_factored и check_apart сначала разбирают структуру записи
и только потом сверяют равенство.

Здесь измеряется и то, что проверки принимают, и то, что они отвергают.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import digest, _series_canon

res = []
p, q, m, n_, v, w, z = sp.symbols('p q m n_ v w z')
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


P11 = 3 * x**3 + 5 * x**2 + x - 1          # 2024 May TZ1 P1 Q11
P22 = x**3 + 4 * x**2 + 5 * x + 2          # 2022 Nov P1 Q11

print('=== verify_factored: что принимается ===')
t('верное разложение на три линейных',
  verify_factored('  (x+1)²(3x−1)', (x + 1)**2 * (3 * x - 1), P11, n=3))
t('тот же ответ с вынесенной тройкой',
  verify_factored('  3(x+1)²(x−1/3)', 3 * (x + 1)**2 * (x - R(1, 3)), P11, n=3))
t('порядок множителей не важен',
  verify_factored('  (3x−1)(x+1)²', (3 * x - 1) * (x + 1)**2, P11, n=3))
t('кратный множитель записан дважды, а не степенью',
  verify_factored('  (x+1)(x+1)(3x−1)', (x + 1) * (x + 1) * (3 * x - 1), P11, n=3))
t('второй многочлен архива',
  verify_factored('  (x+1)²(x+2)', (x + 1)**2 * (x + 2), P22, n=3))
t('минус перед скобками',
  verify_factored('  −(x+1)(x−2)', -(x + 1) * (x - 2), -x**2 + x + 2))
t('квадратичный множитель при max_deg=2',
  verify_factored('  (x+1)(x²+9)', (x + 1) * (x**2 + 9),
                  x**3 + x**2 + 9 * x + 9, max_deg=2))

print('\n=== verify_factored: что отвергается ===')
t('раскрытый многочлен — не произведение',
  not verify_factored('  3x³+5x²+x−1', P11, P11, n=3))
t('разложение не доведено до конца',
  not verify_factored('  (x+1)(3x²+2x−1)', (x + 1) * (3 * x**2 + 2 * x - 1), P11))
t('произведение не равно исходному',
  not verify_factored('  (x+1)²(3x−2)', (x + 1)**2 * (3 * x - 2), P11, n=3))
t('множителей меньше, чем просили',
  not verify_factored('  (x+1)(x+2)', (x + 1) * (x + 2), x**2 + 3 * x + 2, n=3))
t('отрицательная степень множителя',
  not verify_factored('  (x+1)⁻¹…', (x + 1)**-1 * (3 * x - 1), P11))
t('пустой ответ даёт ⬜', not verify_factored('  пусто', ..., P11))

print('\n=== verify_division ===')
t('2x²−5x−3 = (x−1)(2x−3) − 6',
  verify_division('  верно', 2 * x - 3, -6, 2 * x**2 - 5 * x - 3, x - 1))
t('неверное частное',
  not verify_division('  2x−4', 2 * x - 4, -6, 2 * x**2 - 5 * x - 3, x - 1))
t('остаток той же степени, что делитель',
  not verify_division('  недоделено', 2 * x, -3 * x - 3,
                      2 * x**2 - 5 * x - 3, x - 1))
t('деление на квадратный множитель с линейным остатком',
  verify_division('  на (x+1)²', x - 1, 4 * x + 4,
                  sp.expand((x + 1)**2 * (x - 1) + 4 * x + 4), (x + 1)**2))
t('пустой ответ даёт ⬜',
  not verify_division('  пусто', ..., ..., 2 * x**2 - 5 * x - 3, x - 1))

print('\n=== verify_divisible: эталона нет вообще ===')
F7 = x**4 + p * x**3 - 2 * x**2 + q * x - 3          # 2025 May TZ2 P1 Q7
t('p=2, q=−6 делает (x+1)² делителем',
  verify_divisible('  верно', F7, (x + 1)**2, {p: 2, q: -6}))
t('p=2, q=−5 — уже нет',
  not verify_divisible('  почти', F7, (x + 1)**2, {p: 2, q: -5}))
t('нули не подходят', not verify_divisible('  нули', F7, (x + 1)**2, {p: 0, q: 0}))
t('пустой ответ даёт ⬜',
  not verify_divisible('  пусто', F7, (x + 1)**2, {p: ..., q: ...}))

print('\n=== check_apart ===')
Q11 = 1 / ((x + 1) * (2 * x + 1))
t('разложение из markscheme',
  check_apart('  −1/(x+1)+2/(2x+1)', -1 / (x + 1) + 2 / (2 * x + 1), Q11))
t('исходная дробь сама себе не равна по форме',
  not check_apart('  1/((x+1)(2x+1))', Q11, Q11))
t('перепутанные знаки',
  not check_apart('  1/(x+1)−2/(2x+1)', 1 / (x + 1) - 2 / (2 * x + 1), Q11))
t('числитель зависит от x',
  not check_apart('  x/(x+1)+…', x / (x + 1) + (1 - x) / (2 * x + 1), Q11))
t('буква в числителе разрешена',
  check_apart('  1/(kx)+1/(k(k−x))', 1 / (k * x) + 1 / (k * (k - x)),
              1 / (x * (k - x))))
t('другая переменная',
  check_apart('  ½/(1−2v)+½/(1+2v)',
              R(1, 2) / (1 - 2 * v) + R(1, 2) / (1 + 2 * v),
              1 / (1 - 4 * v**2), var=v))
REP = (2 / (x + 1) + 1 / (x + 1)**2 - 4 / (2 * x + 1) + 2 / (2 * x + 1)**2)
t('кратный множитель в знаменателе',
  check_apart('  с (x+1)² и (2x+1)²', REP, sp.together(REP)))
t('пустой ответ даёт ⬜', not check_apart('  пусто', ..., Q11))

print('\n=== verify_root_transform ===')
BASE = 2 * x**2 - 5 * x + 1                    # 2021 Nov P2 Q6
t('x²−95x+8 имеет корни 1/α³',
  verify_root_transform('  m=−95, n=8', [1, -95, 8], BASE, lambda r: 1 / r**3))
t('знак m перепутан',
  not verify_root_transform('  m=95', [1, 95, 8], BASE, lambda r: 1 / r**3))
t('умножение всего уравнения на 8 корней не меняет',
  verify_root_transform('  8x²−760x+64', [8, -760, 64], BASE, lambda r: 1 / r**3))
QUART = z**4 + 2 * z**2 + 4                    # 2025 May TZ2 P1 Q12
t('4w⁴+2w²+1 — уравнение для 1/z',
  verify_root_transform('  p=4,q=2,r=1', [4, 0, 2, 0, 1], QUART,
                        lambda r: 1 / r, var=z))
t('коэффициенты переставлены',
  not verify_root_transform('  p=1,q=2,r=4', [1, 0, 2, 0, 4], QUART,
                            lambda r: 1 / r, var=z))
t('степень не та',
  not verify_root_transform('  кубическое', [1, 0, 0, 1], QUART,
                            lambda r: 1 / r, var=z))
t('пустой ответ даёт ⬜',
  not verify_root_transform('  пусто', [1, ..., ...], BASE, lambda r: 1 / r**3))

print('\n=== чем эти проверки отличаются от check_series ===')
# check_series приняла бы нераскрытую скобку: она сверяет значения.
# verify_factored, наоборот, требует именно скобок — и обе правы,
# потому что в A3 просили раскрыть, а здесь просят разложить.
t('check_series принимает разложенный вид',
  check_series('  3x³+5x²+x−1', P11, digest(_series_canon(P11, x))))
t('check_series принимает и произведение',
  check_series('  (x+1)²(3x−1)', (x + 1)**2 * (3 * x - 1),
               digest(_series_canon(P11, x))))
t('verify_factored различает их',
  verify_factored('  форма важна', (x + 1)**2 * (3 * x - 1), P11, n=3)
  and not verify_factored('  форма важна', P11, P11, n=3))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
