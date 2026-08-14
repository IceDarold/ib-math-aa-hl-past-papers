"""Проверяет механику сверки разложений.

Разложение нельзя сверять по записи. Ученик напишет 5*x/2, Python при делении
даст 2.5, а srepr у Rational(5,2) и Float(2.5) разный; свернуть (1+x)**4
обратно в многочлен simplify не станет. Поэтому check_series сверяет значения
в нескольких точках.

Здесь измеряется и то, что проверка принимает, и то, что она отвергает,
и отдельно — где она мягче экзамена.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import digest, _series_canon, _SERIES_SAMPLES

res = []
p, q, n, r = sp.symbols('p q n r')
th = sp.Symbol('theta', real=True)
R = sp.Rational


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== одно разложение в разных записях ===')
W = digest(_series_canon(1 + 4 * x + 6 * x**2 + 4 * x**3 + x**4, x))
forms = {
    'по возрастанию': 1 + 4 * x + 6 * x**2 + 4 * x**3 + x**4,
    'по убыванию': x**4 + 4 * x**3 + 6 * x**2 + 4 * x + 1,
    'с плавающей точкой': 1.0 + 4.0 * x + 6.0 * x**2 + 4.0 * x**3 + x**4,
    'частично свёрнутое': (1 + x)**2 * (1 + 2 * x + x**2),
}
for name, f in forms.items():
    t(f'{name} проходит', check_series(f'  {name}', f, W))

print('\n=== рациональное против десятичного ===')
W9 = digest(_series_canon(1 + R(5, 2) * x - R(25, 8) * x**2 + R(125, 16) * x**3, x))
t('дроби проходят',
  check_series('  5/2, 25/8, 125/16',
               1 + R(5, 2) * x - R(25, 8) * x**2 + R(125, 16) * x**3, W9))
t('те же числа десятичными проходят',
  check_series('  2.5, 3.125, 7.8125',
               1 + 2.5 * x - 3.125 * x**2 + 7.8125 * x**3, W9))
t('округлённые до трёх цифр — нет',
  not check_series('  2.5, 3.13, 7.81', 1 + 2.5 * x - 3.13 * x**2 + 7.81 * x**3, W9))

print('\n=== что должно отвергаться ===')
t('потерянный член', not check_series('  без x³', 1 + R(5, 2) * x - R(25, 8) * x**2, W9))
t('лишний член',
  not check_series('  с x⁴', 1 + R(5, 2) * x - R(25, 8) * x**2
                   + R(125, 16) * x**3 + x**4, W9))
t('перепутанный знак',
  not check_series('  +25/8', 1 + R(5, 2) * x + R(25, 8) * x**2 + R(125, 16) * x**3, W9))
t('внутренний множитель не возведён в степень',
  not check_series('  без пятёрки', 1 + R(5, 2) * x - R(1, 8) * x**2 + R(1, 16) * x**3, W9))

print('\n=== несколько букв ===')
W13 = digest(_series_canon(1 + (p - q) * x + (q**2 - p * q) * x**2, x))
t('другая группировка проходит',
  check_series('  q(q−p)', 1 + (p - q) * x + q * (q - p) * x**2, W13))
t('перепутанный знак при x² — нет',
  not check_series('  (pq−q²)', 1 + (p - q) * x + (p * q - q**2) * x**2, W13))
t('буквы переставлены местами — нет',
  not check_series('  (q−p)x', 1 + (q - p) * x + (q**2 - p * q) * x**2, W13))

print('\n=== переменная не x ===')
WT = digest(_series_canon(sp.cos(th)**5 - 10 * sp.cos(th)**3 * sp.sin(th)**2
                          + 5 * sp.cos(th) * sp.sin(th)**4, th))
t('запись через sin и cos проходит',
  check_series('  как в markscheme',
               sp.cos(th)**5 - 10 * sp.cos(th)**3 * sp.sin(th)**2
               + 5 * sp.cos(th) * sp.sin(th)**4, WT, var=th))
t('свёрнутая пифагоровым тождеством проходит',
  check_series('  через один cos',
               16 * sp.cos(th)**5 - 20 * sp.cos(th)**3 + 5 * sp.cos(th), WT, var=th))
t('мнимая часть вместо действительной — нет',
  not check_series('  Im вместо Re',
                   5 * sp.cos(th)**4 * sp.sin(th) - 10 * sp.cos(th)**2 * sp.sin(th)**3
                   + sp.sin(th)**5, WT, var=th))

print('\n=== пустой ответ ===')
t('многоточие даёт ⬜', not check_series('  пусто', ..., W))

print('\n=== где проверка мягче экзамена ===')
# 1. Нераскрытая скобка численно равна своему разложению, и различить их
#    по значениям нельзя. В условии сказано «expand», но проверка это примет.
t('нераскрытая скобка проходит', check_series('  (1+x)^4', (1 + x)**4, W))
# 2. cos(5θ) численно равен своей развёрнутой форме. На экзамене за такой
#    ответ баллов не дадут: просили выразить через sinθ и cosθ.
t('cos(5θ) проходит вместо разложения',
  check_series('  cos(5*theta)', sp.cos(5 * th), WT, var=th))

print('\n=== устройство канона ===')
t('точек ровно пять', len(_SERIES_SAMPLES) == 5)
t('точки различны', len(set(_SERIES_SAMPLES)) == len(_SERIES_SAMPLES))
# многочлены степени 4 совпадают в 5 точках только если совпадают тождественно
diff = sp.Poly(1 + 4 * x + 6 * x**2 + 4 * x**3 + x**4
               - (1 + 4 * x + 6 * x**2 + 4 * x**3 + 1.0001 * x**4), x)
t('различие в пятом знаке видно',
  not check_series('  x⁴ с коэффициентом 1.0001',
                   1 + 4 * x + 6 * x**2 + 4 * x**3 + 1.0001 * x**4, W))
t('канон детерминирован',
  _series_canon(1 + (p - q) * x, x) == _series_canon(1 + (p - q) * x, x))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
