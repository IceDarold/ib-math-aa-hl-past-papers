"""Прогоняет все проверки практикума A7 с эталонными ответами из раздела решений.

Ответы не переписываются из решений. Суммы считаются напрямую сложением
слагаемых и сверяются с замкнутой формулой, производные берутся sympy,
делимость проверяется перебором, а не разложением из текста. Отдельно
измеряется, что проверки отвергают: для темы доказательств это важнее,
чем обычно, потому что здесь принимается любая верная запись перехода.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

NB = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a7-proof.ipynb')
nb = json.load(open(NB))
src = {i: ''.join(c['source']) for i, c in enumerate(nb['cells'])}
D = {}
for s in src.values():
    for line in s.split('\n'):
        if any(f in line for f in ("check_num(", "check_order(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
n, m, p, q, r = sp.symbols('n m p q r', integer=True)
al = sp.Symbol('alpha', integer=True)
a, b, c = sp.symbols('a b c')


def t(name, ok):
    res.append((name, ok))


print('=== прямые доказательства ===')
# задание 1: разность считается, а не переписывается
d1 = sp.expand((n + 1)**2 - n**2)
print(f'(n+1)² − n² = {d1}')
t('1', verify_identity('Задание 1', d1, n + (n + 1), var=n))
t('1-факторизация', verify_identity('Задание 1 через разложение',
                                    sp.factor((n + 1)**2 - n**2), n + (n + 1), var=n))

d2 = sp.simplify(((a**2 - 1) / (2 * a))**2 + 1)
print(f'левая часть задания 2 = {d2}')
t('2', verify_identity('Задание 2', d2, ((a**2 + 1) / (2 * a))**2, var=a))
t('2-обратный путь', verify_identity('Задание 2 из правой части',
                                     sp.expand(((a**2 + 1) / (2 * a))**2),
                                     ((a**2 - 1) / (2 * a))**2 + 1, var=a))

print('\n=== представление целых ===')
s3 = sp.expand((n - 1) + n + (n + 1))
s4 = sp.expand((n - 1)**2 + n**2 + (n + 1)**2)
print(f'сумма трёх подряд = {s3};  сумма квадратов = {s4}')
t('3-выкладка', verify_identity('Задание 3, выкладка', s3, (n - 1) + n + (n + 1), var=n))
t('3-вывод', verify_residue('Задание 3, вывод', s3, 3, 0))
t('4-выкладка', verify_identity('Задание 4, выкладка', s4,
                                (n - 1)**2 + n**2 + (n + 1)**2, var=n))
t('4-вывод', verify_residue('Задание 4, вывод', s4, 3, 2))

# остаток берётся перебором, а не из решения
rests = {int(s4.subs(n, i)) % 3 for i in range(-20, 21)}
print(f'остатки суммы квадратов по модулю 3 при n = −20..20: {rests}')
t('4-остаток единственный', rests == {2})

print('\n=== от противного ===')
s5 = sp.expand((2 * m + 1)**2 + (2 * n + 1)**2)
print(f'(2m+1)² + (2n+1)² = {s5}')
t('5-выкладка', verify_identity('Задание 5, выкладка', s5,
                                (2 * m + 1)**2 + (2 * n + 1)**2, var=m))
t('5-вывод', verify_residue('Задание 5, вывод', s5, 4, 2))
r5 = {(int(2 * i + 1)**2 + int(2 * j + 1)**2) % 4 for i in range(-8, 9) for j in range(-8, 9)}
print(f'остатки по модулю 4 для нечётных a, b: {r5}')
t('5-остаток единственный', r5 == {2})

left6, right6 = 2 * al**3 + 6 * al, sp.Integer(-1)
t('6-перенос', verify_rewrite('Задание 6, перенос', left6, right6,
                              2 * al**3 + 6 * al + 1, var=al))
t('6-слева', verify_residue('Задание 6, слева', left6, 2, 0))
t('6-справа', verify_residue('Задание 6, справа', right6, 2, 1))
# у уравнения и правда нет целых корней: проверяем независимо
roots6 = sp.solve(2 * al**3 + 6 * al + 1, al)
print(f'корни 2α³+6α+1: {[sp.N(v, 6) for v in roots6 if sp.im(sp.N(v)) == 0]}')
t('6-целых корней нет', not any(sp.sympify(v).is_integer for v in roots6))

left7, right7 = 2 * k**2 + 2 * k, 4 * q + 5
t('7-равносильность', verify_rewrite('Задание 7, равносильность', left7, right7,
                                     (2 * k + 1)**2 - 8 * q - 11, var=k, factor=2))
t('7-слева', verify_residue('Задание 7, слева', left7, 2, 0))
t('7-справа', verify_residue('Задание 7, справа', right7, 2, 1))
# p² − 8q − 11 = 0 не имеет целых решений: перебор подтверждает
hits = [(i, j) for i in range(-60, 61) for j in range(-60, 61) if i * i - 8 * j - 11 == 0]
print(f'целые решения p² − 8q − 11 = 0 при |p|,|q| ≤ 60: {hits}')
t('7-решений нет', hits == [])

print('\n=== скелет ===')
order = ['B', 'D', 'F', 'A', 'E', 'G', 'C']
t('8-порядок', check_order('Задание 8, порядок', order, D['Задание 8, порядок'], n=7))
t('8-баллы', check_num('Задание 8, баллы', 1, 6, D['Задание 8, баллы']))

print('\n=== индукция ===')
# задание 9: сумма складывается напрямую и сверяется с формулой
F9 = 1 - 1 / factorial(k + 1)
direct9 = [sum(Rational(j, sp.factorial(j + 1)) for j in range(1, i + 1)) for i in range(1, 8)]
formula9 = [F9.subs(k, i) for i in range(1, 8)]
print(f'сумма напрямую: {direct9[:4]} ...\nформула        : {formula9[:4]} ...')
t('9-формула верна', direct9 == formula9)
t('9', verify_induction('Задание 9', F9 + (k + 1) / factorial(k + 2), F9,
                        base_lhs=Rational(1, 2)))

F10 = binomial(k + 1, 2)
direct10 = [sum(sp.binomial(j, 1) for j in range(1, i + 1)) for i in range(1, 8)]
t('10-формула верна', direct10 == [F10.subs(k, i) for i in range(1, 8)])
t('10', verify_induction('Задание 10', F10 + binomial(k + 1, 1), F10, base_lhs=1))

E11 = 5**(2 * k) - 2**(3 * k)
vals = [int(E11.subs(k, i)) for i in range(1, 9)]
print(f'\n5^2n − 2^3n при n = 1..8: {vals}')
t('11-делится', all(v % 17 == 0 for v in vals))
t('11', verify_divisibility('Задание 11', E11, 17, 8))
t('11-второй путь', verify_divisibility('Задание 11 с множителем 25', E11, 17, 25))

hyp12 = (x**2 + 2 * k * x + k * (k - 1)) * exp(x)
# формула сверяется с настоящими производными, а не с текстом решения
ok12 = all(sp.simplify(sp.diff(x**2 * exp(x), x, i) - hyp12.subs(k, i)) == 0
           for i in range(1, 6))
print(f'формула n-й производной совпала с diff при n = 1..5: {ok12}')
t('12-формула верна', ok12)
t('12', verify_induction('Задание 12', diff(hyp12, x), hyp12,
                         base_lhs=diff(x**2 * exp(x), x)))

hyp13 = m**k * x + c * (1 - m**k) / (1 - m)
f13 = sp.Lambda(x, m * x + c)
comp = x
ok13 = True
for i in range(1, 6):
    comp = f13(comp)
    ok13 = ok13 and sp.simplify(sp.expand(comp - hyp13.subs(k, i))) == 0
print(f'композиция f^n совпала с формулой при n = 1..5: {ok13}')
t('13-формула верна', ok13)
t('13', verify_induction('Задание 13', m * hyp13 + c, hyp13, base_lhs=m * x + c))

print('\n=== задание на таймере ===')
t('14', verify_identity('Задание 14', log(2 * k) / log(2), log(2 * k) / log(2),
                        var=k, samples=(1, 2, 3, 5, 8, 13)))
t('14-развёрнутая форма', verify_identity('Задание 14 как 1 + log k / log 2',
                                          1 + log(k) / log(2), log(2 * k) / log(2),
                                          var=k, samples=(1, 2, 3, 5, 8, 13)))
t('14-неравенство', all(2 * i >= i + 1 for i in range(1, 50)))

print('\n=== тренажёр ===')
KEY = eval([l.split('KEY = ')[1] for s in src.values() for l in s.split('\n')
            if l.startswith('KEY = ')][0])
good = {1: 'repr', 2: 'sum', 3: 'direct', 4: 'div', 5: 'contra', 6: 'deriv',
        7: 'contra', 8: 'rec', 9: 'ineq', 10: 'repr', 11: 'contra', 12: 'sum',
        13: 'direct', 14: 'rec', 15: 'ineq'}
t('trigger', trigger_check(good, KEY))
print('  порча пункта 8:', end=' ')
t('trigger-neg', not trigger_check({**good, 8: 'sum'}, KEY))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('n1', not verify_identity('порядок вычитания перепутан',
                            sp.expand(n**2 - (n + 1)**2), n + (n + 1), var=n))
t('n2', not verify_residue('сумма квадратов якобы делится на 3', s4, 3, 0))
# Одну букву на оба нечётных числа проверка не ловит и поймать не может:
# 2(2m+1)² = 8m²+8m+2 тоже даёт остаток 2 по модулю 4. Такое «доказательство»
# верно для частного случая a = b и неполно как доказательство, а различить
# полноту рассуждения арифметикой нельзя. Фиксируем поведение, чтобы оно
# не выглядело недосмотром; в ноутбуке про это сказано прямо.
t('n3-одна буква проходит арифметику',
  verify_residue('одна буква на оба нечётных числа',
                 sp.expand(2 * (2 * m + 1)**2), 4, 2))
t('n3-две буквы дают то же', sp.expand(s5.subs(n, m)) == sp.expand(2 * (2 * m + 1)**2))
t('n3b', not verify_rewrite('при переносе потерян знак', left6, 1,
                            2 * al**3 + 6 * al + 1, var=al))
t('n3c', not verify_rewrite('деление на 2 не учтено', left7, right7,
                            (2 * k + 1)**2 - 8 * q - 11, var=k))
t('n4', not check_order('база не первой', ['D', 'B', 'F', 'A', 'E', 'G', 'C'],
                        D['Задание 8, порядок'], n=7))
t('n5', not check_num('вывод засчитан без выкладки', 2, 6, D['Задание 8, баллы']))
t('n6', not verify_induction('слагаемое взято с индексом k, а не k+1',
                             F9 + k / factorial(k + 1), F9))
t('n7', not verify_induction('база проверена не там',
                             F9 + (k + 1) / factorial(k + 2), F9, base_lhs=1))
t('n8', not verify_divisibility('множитель, не собирающий гипотезу', E11, 17, 1))
t('n9', not verify_induction('продифференцирован только первый множитель',
                             (2 * x + 2 * k) * exp(x), hyp12))
t('n10', not verify_induction('в шаге забыли прибавить c', m * hyp13, hyp13,
                              base_lhs=m * x + c))

bad = [n_ for n_, ok in res if not ok]
print(f'\n{"ВСЁ ПРОШЛО" if not bad else "ПРОВАЛЫ: " + str(bad)}  ({len(res) - len(bad)}/{len(res)})')
