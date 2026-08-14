"""Проверяет механику проверок для доказательств.

Главное требование обратное тому, что было в комплексных числах. Там нельзя
было различать формы записи одного числа; здесь нельзя засчитывать выкладку,
которая до нужного утверждения не доходит. Поэтому основной вес теста —
негативный: измеряется, что именно проверки отвергают.

Отдельно закрепляются две вещи, на которых легко ошибиться при доработке kit:
порядок expand → simplify (обратный не сводит m·m^k к m^(k+1)) и требование
целых коэффициентов после деления в verify_divisibility.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *
from kit import digest, _agrees

res = []
n, m, q = sp.symbols('n m q', integer=True)
c = sp.Symbol('c')


def t(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


print('=== verify_induction: переход ===')
F = 1 - 1 / factorial(k + 1)
t('верный шаг проходит',
  verify_induction('  сумма', F + (k + 1) / factorial(k + 2), F))
t('уже упрощённый шаг проходит тоже',
  verify_induction('  сумма упрощённая', 1 - 1 / factorial(k + 2), F))
t('шаг без подстановки не проходит',
  not verify_induction('  гипотеза не подставлена', F, F))
t('шаг с ошибкой в индексе не проходит',
  not verify_induction('  индекс k вместо k+1', F + k / factorial(k + 1), F))

print('\n=== verify_induction: база ===')
t('верная база проходит',
  verify_induction('  база 1/2', F + (k + 1) / factorial(k + 2), F,
                   base_lhs=Rational(1, 2)))
t('неверная база не проходит',
  not verify_induction('  база 1', F + (k + 1) / factorial(k + 2), F, base_lhs=1))
t('база с другого n0',
  verify_induction('  n0 = 2', F + (k + 1) / factorial(k + 2), F,
                   n0=2, base_lhs=Rational(5, 6)))
t('незаполненная база валит проверку',
  not verify_induction('  база пуста', F + (k + 1) / factorial(k + 2), F,
                       base_lhs=...))
t('незаполненный шаг даёт ⬜', not verify_induction('  шаг пуст', ..., F))

print('\n=== verify_induction: несколько символов ===')
# n-я производная: тождество должно держаться и по k, и по x
hyp = (x**2 + 2 * k * x + k * (k - 1)) * exp(x)
t('производная гипотезы проходит', verify_induction('  d/dx', diff(hyp, x), hyp))
t('половина производной не проходит',
  not verify_induction('  без второго слагаемого', (2 * x + 2 * k) * exp(x), hyp))

# порядок expand → simplify: cancel и simplify по отдельности здесь не справляются
rec = m**k * x + c * (1 - m**k) / (1 - m)
t('рекурсия сводится только после expand',
  verify_induction('  f(f^k)', m * rec + c, rec))
t('и это не случайность: cancel сам по себе не доводит',
  sp.cancel(sp.expand((m * rec + c) - rec.subs(k, k + 1))) != 0)

print('\n=== verify_divisibility ===')
E = 5**(2 * k) - 2**(3 * k)
t('множитель 8 проходит', verify_divisibility('  m=8', E, 17, 8))
t('множитель 25 проходит тоже', verify_divisibility('  m=25', E, 17, 25))
t('множитель 1 не проходит', not verify_divisibility('  m=1', E, 17, 1))
t('чужой делитель не проходит', not verify_divisibility('  d=5', E, 5, 8))
t('незаполненный множитель даёт ⬜', not verify_divisibility('  пусто', E, 17, ...))

# то самое место, ради которого проверяются коэффициенты, а не значения:
# при m=1 разность кратна 17 при каждом целом k, но 17 из неё не вынести
rest1 = sp.expand(E.subs(k, k + 1) - E)
t('при m=1 разность всё же кратна 17 численно',
  all(int(rest1.subs(k, i)) % 17 == 0 for i in range(1, 8)))
t('но целых коэффициентов после деления не остаётся',
  any(not sp.sympify(co).is_Integer
      for co in sp.expand(rest1 / 17).as_coefficients_dict().values()))

print('\n=== verify_residue ===')
t('3n делится на 3', verify_residue('  3n', 3 * n, 3, 0))
t('3n²+2 даёт остаток 2', verify_residue('  3n²+2', 3 * n**2 + 2, 3, 2))
t('два символа перебираются оба',
  verify_residue('  (2m+1)²+(2n+1)²', (2 * m + 1)**2 + (2 * n + 1)**2, 4, 2))
t('константа проверяется один раз', verify_residue('  −1', -1, 2, 1))
t('непостоянный остаток не проходит', not verify_residue('  n²', n**2, 3, 1))
t('нецелое значение не проходит', not verify_residue('  n/2', n / 2, 2, 0))
t('неверный остаток не проходит', not verify_residue('  3n как 1', 3 * n, 3, 1))
# Для многочленов с целыми коэффициентами остаток периодичен, и отрицательные
# значения ничего нового не дают. Дают они его на степенях: 2^n чётно при n ≥ 1,
# но при n = −3 это вовсе не целое, и такое утверждение проверка отвергает.
t('отрицательные значения ловят степени',
  not verify_residue('  2^n чётно', 2**n, 2, 0))
t('а на положительных та же степень проходит',
  verify_residue('  2^n при n ≥ 1', 2**n, 2, 0, samples=(1, 2, 3, 4, 5)))
t('незаполненный остаток даёт ⬜', not verify_residue('  пусто', 3 * n, 3, ...))

print('\n=== verify_rewrite ===')
al = sp.Symbol('alpha', integer=True)
t('верный перенос проходит',
  verify_rewrite('  перенос', 2 * al**3 + 6 * al, -1, 2 * al**3 + 6 * al + 1, var=al))
t('потерянный знак не проходит',
  not verify_rewrite('  знак потерян', 2 * al**3 + 6 * al, 1,
                     2 * al**3 + 6 * al + 1, var=al))
t('деление учитывается множителем',
  verify_rewrite('  делили на 2', 2 * k**2 + 2 * k, 4 * q + 5,
                 (2 * k + 1)**2 - 8 * q - 11, var=k, factor=2))
t('без множителя то же равенство не проходит',
  not verify_rewrite('  забыли factor', 2 * k**2 + 2 * k, 4 * q + 5,
                     (2 * k + 1)**2 - 8 * q - 11, var=k))
t('незаполненные части дают ⬜',
  not verify_rewrite('  пусто', ..., ..., 2 * al**3 + 6 * al + 1, var=al))

print('\n=== check_order ===')
KEY = digest('|'.join(['b', 'd', 'f', 'a', 'e', 'g', 'c']))
t('верный порядок проходит',
  check_order('  порядок', ['B', 'D', 'F', 'A', 'E', 'G', 'C'], KEY, n=7))
t('регистр не важен',
  check_order('  строчными', ['b', 'd', 'f', 'a', 'e', 'g', 'c'], KEY, n=7))
t('пробелы не важны',
  check_order('  с пробелами', [' B ', 'D', 'F', 'A', 'E', 'G', 'C'], KEY, n=7))
t('перестановка двух шагов не проходит',
  not check_order('  D и B местами', ['D', 'B', 'F', 'A', 'E', 'G', 'C'], KEY, n=7))
t('пропуск шага виден отдельно',
  not check_order('  шесть шагов', ['B', 'D', 'F', 'A', 'E', 'G'], KEY, n=7))
t('без n длина не проверяется, но хеш не сходится',
  not check_order('  без n', ['B', 'D', 'F'], KEY))

print('\n=== _agrees: допуск масштабируется ===')
# факториалы растут быстро, и абсолютный допуск 1e-9 отверг бы верный ответ
big = factorial(k + 3) + 1
ok, note = _agrees(big, factorial(k + 3) + 1, k, (1, 2, 3, 4, 5, 6, 7))
t('большие значения не ломают допуск', ok)
ok2, _ = _agrees(big, factorial(k + 3) + 2, k, (1, 2, 3, 4, 5, 6, 7))
t('но разница на единицу всё равно видна', not ok2)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
