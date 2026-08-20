"""Проверяет механику проверок из темы треугольника.

Здесь ответ это не число, а конфигурация: длина стороны сама по себе
ничего не значит, значение имеет треугольник, частью которого она является.
Поэтому solve_triangle достраивает треугольник из данных условия,
а verify_triangle сверяет ваши части с построенным — без эталона.

Отдельно измеряется неоднозначный случай: две стороны и угол против
меньшей из них задают **два** треугольника, и проверка должна говорить
об этом вслух, а не молча принимать любой.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

res = []
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


def close(got, want, tol=1e-6):
    return abs(got - want) <= tol * max(1.0, abs(want))


print('=== solve_triangle: сколько треугольников задают данные ===')
sss = solve_triangle(a=3, b=4, c=5)
t('SSS: один треугольник', len(sss) == 1)
t('SSS: прямой угол против гипотенузы', close(sss[0]['C'], 90))
t('SSS: сумма углов 180',
  close(sss[0]['A'] + sss[0]['B'] + sss[0]['C'], 180))

sas = solve_triangle(b=12, c=7, A=25)
t('SAS: один треугольник', len(sas) == 1)
t('SAS: третья сторона по теореме косинусов',
  close(sas[0]['a'], math.sqrt(144 + 49 - 2 * 84 * math.cos(math.radians(25))),
        1e-9))

asa = solve_triangle(a=10, B=45, C=60)
t('ASA: один треугольник', len(asa) == 1 and close(asa[0]['A'], 75))
t('ASA: стороны по теореме синусов',
  close(asa[0]['b'], 10 * math.sin(math.radians(45))
        / math.sin(math.radians(75))))

aas = solve_triangle(A=45, C=60, c=10)
t('AAS: сторона против известного угла', close(aas[0]['a'], 10
  * math.sin(math.radians(45)) / math.sin(math.radians(60))))

print('\n=== неоднозначный случай ===')
ssa = solve_triangle(a=7, b=12, A=25)
t('SSA: два треугольника', len(ssa) == 2)
t('SSA: углы B дополняют друг друга до 180',
  close(ssa[0]['B'] + ssa[1]['B'], 180))
t('SSA: периметры разные',
  not close(sum(ssa[0][k] for k in 'abc'), sum(ssa[1][k] for k in 'abc')))
t('SSA: наименьший периметр у тупого B',
  min(ssa, key=lambda s: sum(s[k] for k in 'abc'))['B'] > 90)
t('SSA: обе конфигурации замыкаются',
  all(close(s['a']**2, s['b']**2 + s['c']**2
            - 2 * s['b'] * s['c'] * math.cos(math.radians(s['A'])), 1e-9)
      for s in ssa))
t('SSA без решений: синус больше единицы',
  solve_triangle(a=3, b=10, A=60) == [])
t('SSA с тупым известным углом: решение одно',
  len(solve_triangle(a=10, b=5, A=100)) == 1)
t('SSA с двумя прямыми углами невозможен',
  solve_triangle(a=10, b=10, A=90) == [])

print('\n=== данных не хватает или они противоречивы ===')
t('три угла размера не задают', solve_triangle(A=60, B=60, C=60) == [])
t('две части не задают ничего', solve_triangle(a=3, b=4) == [])
t('неравенство треугольника нарушено', solve_triangle(a=1, b=2, c=3) == [])
t('отрицательная сторона', solve_triangle(a=-3, b=4, c=5) == [])
t('сумма углов не 180', solve_triangle(a=5, A=100, B=100) == [])

print('\n=== verify_triangle: что принимается ===')
t('сторона по теореме косинусов, май 2025 TZ3',
  verify_triangle('  BC = 16.3', {'a': 16.3}, b=12, c=7, A=116))
t('угол по теореме синусов, май 2025 TZ3',
  verify_triangle('  ACB = 22.7', {'C': 22.7}, b=12, c=7, A=116))
t('несколько частей сразу',
  verify_triangle('  сторона и угол', {'a': 16.33, 'C': 22.66},
                  b=12, c=7, A=116))
t('данные в градусах по умолчанию',
  verify_triangle('  DL = 420', {'a': 419.7}, A=56, C=99, c=500))
t('неоднозначный случай: ответ подходит одному из двух',
  verify_triangle('  периметр поменьше', {'c': 6.05}, a=7, b=12, A=25))

print('\n=== verify_triangle: что отвергается ===')
t('нет: сторона не согласуется с данными',
  not verify_triangle('  BC = 15', {'a': 15}, b=12, c=7, A=116))
t('нет: угол не согласуется',
  not verify_triangle('  ACB = 30', {'C': 30}, b=12, c=7, A=116))
t('нет: в неоднозначном случае взято не то значение',
  not verify_triangle('  c = 10', {'c': 10}, a=7, b=12, A=25))
t('нет: данные треугольника не задают',
  not verify_triangle('  что угодно', {'c': 5}, a=1, b=2, c=3))
t('нет: placeholder не заполнен',
  not verify_triangle('  пусто', {'a': ...}, b=12, c=7, A=116))
# Допуск 5e−3 относительный: ответ с тремя значащими цифрами проходит,
# а округление до двух — уже нет.
t('нет: округление до двух значащих цифр',
  verify_triangle('  16.3', {'a': 16.3}, b=12, c=7, A=116)
  and not verify_triangle('  16', {'a': 16}, b=12, c=7, A=116))

print('\n=== verify_exact: точный ответ против десятичного ===')
t('площадь 12√6, ноябрь 2023',
  verify_exact('  12√6', 12 * sqrt(6), R(1, 2) * 6 * 10 * sqrt(1 - R(1, 25))))
t('эквивалентная точная запись', verify_exact('  √864', sqrt(864), 12 * sqrt(6)))
t('дробь тоже точна', verify_exact('  10/3', R(10, 3), R(10, 3)))
t('нет: десятичная запись',
  not verify_exact('  29.4', 29.3939, 12 * sqrt(6)))
t('нет: десятичная запись с двадцатью знаками',
  not verify_exact('  29.393876913398137...', sp.N(12 * sqrt(6), 20),
                   12 * sqrt(6)))
t('нет: точная, но другая',
  not verify_exact('  12√5', 12 * sqrt(5), 12 * sqrt(6)))
t('нет: placeholder', not verify_exact('  пусто', ..., 12 * sqrt(6)))

print('\n=== чем эта проверка отличается от прежних ===')
# check_num сверяет округление с хешем и о треугольнике ничего не знает:
# ответ, совпавший в трёх значащих цифрах, пройдёт, даже если он взят
# из другого треугольника. verify_triangle судит по данным условия.
t('verify_triangle ловит то, чего не видит check_num',
  check_num('  16.3 по хешу', 16.3, 3, digest(sig(16.3, 3)))
  and not verify_triangle('  16.3 в чужом треугольнике', {'a': 16.3},
                          b=12, c=7, A=100))
# verify_exact — про запись, как verify_factored в A4 и verify_vertex_form в B1.
t('verify_exact требует записи, check_num — округления',
  check_num('  29.4 по хешу', 29.3939, 3, digest(sig(29.3939, 3)))
  and not verify_exact('  29.4 как точный', 29.3939, 12 * sqrt(6)))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
