"""Проверяет механику проверок из темы показательных и логарифмических моделей.

Ответ здесь — сама модель, и это девятое понятие равенства ответов в серии.
verify_model не хранит ни постоянных, ни готового значения: он берёт вашу
модель и подставляет в неё те данные, из которых её строили. Верна она тогда,
когда воспроизводит условие, а не тогда, когда совпала с эталоном.

Такая проверка ловит ровно те две ошибки, за которые в теме теряют баллы:
время отсчитано не оттуда (t = 27, а не t = 19) и знак k при убывании.

verify_in_terms_of сторожит вопрос «выразите log 24 через p и q»: ответом
служит не число, а выражение через данные буквы, поэтому проверка требует
двух вещей сразу — что чужих букв в ответе нет и что после подстановки
истинных значений получается то самое число.

Запуск:  python practicum/tests/test_kit_model.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *

res = []
p, q, r, n = sp.symbols('p q r n')
R = sp.Rational


def T(name, ok):
    res.append((name, ok))
    print(('✅' if ok else '❌'), name)


# Ноябрь 2022, Paper 2 Q4: P = 15000 e^{kt}, за восемь лет население упало
# на 11%, спрашивают 2041 год, то есть t = 27.
K22 = sp.log(sp.Rational(89, 100)) / 8
P22 = 15000 * sp.exp(K22 * t)
DATA22 = [(0, 15000), (8, 13350), (27, 10122.3)]

# Ноябрь 2025, Paper 3 Q2(a): логистическая модель волков.
WOLVES = 200 / (1 + 4 * sp.exp(-sp.log(R(28, 13)) / 5 * t))
DATAW = [(0, 40), (5, 70), (10, 107.397)]

print('=== verify_model: что принимается ===')
T('модель из ноября 2022 воспроизводит все три числа',
  verify_model('  P(t)', P22, DATA22))
T('та же модель, записанная через 0.89^{t/8}',
  verify_model('  через степень', 15000 * (R(89, 100))**(t / 8), DATA22))
T('та же модель с округлённым k',
  verify_model('  k = −0.0145667', 15000 * sp.exp(-0.0145667 * t), DATA22))
T('логистическая модель волков',
  verify_model('  x(t)', WOLVES, DATAW))
T('логистическая, записанная эквивалентно',
  verify_model('  без дроби в показателе',
               200 / (1 + 4 * (R(13, 28))**(t / 5)), DATAW))
T('пара со значением None пропускается',
  verify_model('  только t = 0', 15000 * sp.exp(-t), [(0, 15000), (8, None)]))

print('\n=== verify_model: что отвергается ===')
T('время отсчитано от 2022, а не от 2014',
  not verify_model('  t = 19', P22, [(0, 15000), (8, 13350), (19, 10122.3)]))
T('k взято положительным при убывании',
  not verify_model('  +k', 15000 * sp.exp(-K22 * t), DATA22))
T('начальное значение не то',
  not verify_model('  P(0) = 13350', 13350 * sp.exp(K22 * t), DATA22))
T('в модели осталась неизвестная постоянная',
  not verify_model('  с буквой k', 15000 * sp.exp(k * t), [(0, 15000), (8, 13350)]))
T('логистическая с потолком 100 вместо 200',
  not verify_model('  L = 100', 100 / (1 + 4 * sp.exp(-t / 5)), DATAW))
T('незаполненный ответ не падает, а печатает ⬜',
  not verify_model('  пусто', ..., DATA22))

print('\n=== verify_model: точность ===')
T('три значащих цифры: 10100 вместо 10122 проходит',
  verify_model('  3 з.ц.', P22, [(27, 10100)], sf=3))
T('шесть значащих цифр: 10100 вместо 10122 уже нет',
  not verify_model('  6 з.ц.', P22, [(27, 10100)], sf=6))
T('явный допуск tol перебивает sf',
  verify_model('  tol = 50', P22, [(27, 10100)], sf=6, tol=50))

print('\n=== verify_in_terms_of: что принимается ===')
SUBS = {p: sp.log(2, 10), q: sp.log(3, 10)}
T('log 24 = 3p + q, май 2025 TZ3',
  verify_in_terms_of('  3p + q', 3 * p + q, sp.log(24, 10), SUBS))
T('та же сумма, записанная слагаемыми',
  verify_in_terms_of('  p+p+p+q', p + p + p + q, sp.log(24, 10), SUBS))
T('log_3 8 = 3p/q',
  verify_in_terms_of('  3p/q', 3 * p / q, sp.log(8, 3), SUBS))
T('ответ может быть без одной из букв',
  verify_in_terms_of('  log 8 = 3p', 3 * p, sp.log(8, 10), SUBS))

print('\n=== verify_in_terms_of: что отвергается ===')
T('произведение вместо суммы',
  not verify_in_terms_of('  3pq', 3 * p * q, sp.log(24, 10), SUBS))
T('переписанный сам через себя ответ не принимается',
  not verify_in_terms_of('  log 24', sp.log(24, 10), sp.log(24, 10), SUBS))
T('чужая буква в ответе',
  not verify_in_terms_of('  с r', 3 * p + r, sp.log(24, 10), SUBS))
T('незаполненный ответ печатает ⬜',
  not verify_in_terms_of('  пусто', ..., sp.log(24, 10), SUBS))

print('\n=== сообщения на английском ===')
language('en')
T('verify_model говорит по-английски',
  not verify_model('  english', 13350 * sp.exp(K22 * t), DATA22))
T('verify_in_terms_of говорит по-английски',
  not verify_in_terms_of('  english', 3 * p * q, sp.log(24, 10), SUBS))
language('ru')

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
