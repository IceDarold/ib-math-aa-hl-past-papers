"""Механика проверок вероятности: verify_event, verify_probability,
verify_independence.

Практикум D2 проверяется в verify_d2.py — там сверяются ответы. Здесь
сверяется сама машинка: что пространство действительно восстанавливается
из условий вопроса, что каждый именной промах узнаётся и называется
своим именем, что неверно выписанное дерево ловится по сумме весов,
и что незаполненный ответ печатает ⬜, а не падает.

Запуск:  python practicum/tests/test_kit_probability.py
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import (Eq, Interval, Rational, events, language, P, sympify,
                 verify_constants, verify_event, verify_independence,
                 verify_probability)

# Сообщения сверяются по-английски: практикумы серии печатают их так,
# и ловить формулировку надо в том языке, в котором её увидит студент.
# Перевод проверяется отдельно, в конце.
language('en')

R = Rational
res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def say(call, *args, **kw):
    """Что проверка напечатала."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        call(*args, **kw)
    return buf.getvalue().strip()


def ok(text):
    return text.startswith('✅')


def no(text, fragment=''):
    return text.startswith('❌') and fragment in text


def blank(text):
    return text.startswith('⬜')


print('=== пространство восстанавливается из условий ===')
A, B = events('A B')
plain = [(P(A), R(65, 100)), (P(B), R(75, 100)), (P(A & B), R(6, 10))]
chk('P(A∪B) считается по определению',
    ok(say(verify_event, '1', R(4, 5), plain, P(A | B))))
chk("P(A'∩B') тоже",
    ok(say(verify_event, '2', R(1, 5), plain, P(~A & ~B))))
chk('условная вероятность в условии решается как уравнение',
    ok(say(verify_event, '3', R(1, 12),
           [(P(A), R(1, 2)), (P(B), R(1, 3)), (P(A, given=B), R(1, 4))],
           P(A & B))))
chk('независимость как условие — тоже уравнение, и квадратное',
    ok(say(verify_event, '4', R(24, 100),
           [Eq(P(A & B), P(A)*P(B)),
            (P(A & ~B), R(16, 100)), (P(~A & B), R(36, 100))],
           P(A & B))))
chk('корень больше единицы отбрасывается сам',
    ok(say(verify_event, '5', R(1, 5),
           [Eq(P(A & B), P(A)*P(B)), Eq(sympify(P(A)), 3*sympify(P(B))),
            (P(A | B), R(68, 100))], P(B))))

print('\n=== условий не хватает — и это разные случаи ===')
loose = [(P(A), R(3, 10)), (P(B), R(8, 10))]
chk('когда ответ не определён, так и сказано',
    no(say(verify_event, '6', R(24, 100), loose, P(A & B)),
       'not enough'))
chk('а когда определён, лишние степени свободы не мешают',
    ok(say(verify_event, '7', R(1, 3),
           [(P(A | B), R(5, 8)), (P(A & ~B), R(7, 24))], P(B))))
chk('крайнее значение ищется по вершинам многогранника (min)',
    ok(say(verify_event, '8', R(1, 10), loose, P(A & B), extreme='min')))
chk('и (max)',
    ok(say(verify_event, '9', R(3, 10), loose, P(A & B), extreme='max')))
chk('противоречивые условия названы противоречивыми',
    no(say(verify_event, '10', R(1, 2),
           [(P(A), R(3, 10)), (P(A), R(4, 10)),
            (P(B), R(1, 2)), (P(A & B), R(1, 10))], P(B)),
       'no valid space'))

print('\n=== именные промахи ===')
cond = [(P(A), R(1, 2)), (P(B), R(1, 3)), (P(A, given=B), R(1, 4))]
# P(A|B) = 1/4, а P(B|A) = (1/12)/(1/2) = 1/6 — ровно тот же числитель
# и другой знаменатель, то есть промах, а не другое число наугад
chk('перевёрнутая условная названа перевёрнутой',
    no(say(verify_event, '11', R(1, 6), cond, P(A, given=B)),
       'wrong way round'))
chk('пересечение вместо частного названо пересечением',
    no(say(verify_event, '12', R(1, 12), cond, P(A, given=B)),
       'has not been divided'))
chk('независимость там, где её не обещали',
    no(say(verify_event, '13', R(1, 6),
           [(P(A), R(1, 2)), (P(B), R(1, 3)), (P(A, given=B), R(1, 4))],
           P(A & B)),
       'never promised independence'))
# у plain сумма P(A) + P(B) = 1,4 больше единицы, и её отвергает
# граница диапазона раньше разбора; поэтому промах показан на другой тройке
small = [(P(A), R(3, 10)), (P(B), R(4, 10)), (P(A & B), R(1, 10))]
chk('в объединении пересечение посчитано дважды',
    no(say(verify_event, '14', R(7, 10), small, P(A | B)),
       'counted twice'))
chk('дополнение названо дополнением',
    no(say(verify_event, '15', R(4, 5), plain, P(~A & ~B)),
       'opposite event'))
chk('число вне [0, 1] отвергается до всякого разбора',
    no(say(verify_event, '16', R(3, 2), plain, P(A | B)),
       'never below zero or above one'))
chk('просто неверный ответ называется просто неверным',
    no(say(verify_event, '17', R(1, 7), plain, P(A | B)),
       'not what the space'))

print('\n=== пространство, выписанное исходами ===')
boxes = {('1', 'red'): R(5, 14), ('1', 'white'): R(2, 14),
         ('2', 'red'): R(4, 14), ('2', 'white'): R(3, 14)}
chk('сумма весов проверяется первой',
    no(say(verify_probability, '18', R(9, 14),
           {('1', 'red'): R(5, 14), ('1', 'white'): R(2, 14),
            ('2', 'red'): R(4, 14)}, lambda o: o[1] == 'red'),
       'the space is wrong'))
chk('вероятность события — сумма весов',
    ok(say(verify_probability, '19', R(9, 14), boxes, lambda o: o[1] == 'red')))
chk('условная — отношение сумм',
    ok(say(verify_probability, '20', R(5, 9), boxes,
           lambda o: o[0] == '1', given=lambda o: o[1] == 'red')))
chk('перевёрнутая условная и здесь названа',
    no(say(verify_probability, '21', R(5, 7), boxes,
           lambda o: o[0] == '1', given=lambda o: o[1] == 'red'),
       'wrong way round'))
chk('несобранное частное названо пересечением',
    no(say(verify_probability, '22', R(5, 14), boxes,
           lambda o: o[0] == '1', given=lambda o: o[1] == 'red'),
       'has not been divided'))
chk('невозможное условие названо невозможным',
    no(say(verify_probability, '23', R(1, 2), boxes,
           lambda o: True, given=lambda o: o[1] == 'green'),
       'cannot happen'))
chk('набор исходов принимается наравне с предикатом',
    ok(say(verify_probability, '24', R(9, 14), boxes,
           [('1', 'red'), ('2', 'red')])))

print('\n=== независимость: два числа, а не вердикт ===')
may = [(P(~A), R(3, 4)), (P(A | B), R(3, 4)), (P(B, given=A), R(2, 3))]
chk('верная пара принимается и вердикт назван',
    'independent' in say(verify_independence, '25', [R(1, 6), R(1, 6)],
                         may, A, B))
chk('зависимые события тоже называются',
    'not independent' in say(verify_independence, '26',
                             [R(96, 1000), R(12, 100)],
                             [(P(A), R(48, 100)), (P(B), R(2, 10)),
                              (P(B, given=A), R(25, 100))], A, B))
chk('переставленные числа отвергаются',
    no(say(verify_independence, '27', [R(12, 100), R(96, 1000)],
           [(P(A), R(48, 100)), (P(B), R(2, 10)),
            (P(B, given=A), R(25, 100))], A, B),
       'first number'))
chk('одного числа мало',
    no(say(verify_independence, '28', [R(1, 6)], may, A, B), 'two numbers'))

print('\n=== буква, которая обязана быть вероятностью ===')
k = sp.Symbol('k')
both = [('не гнездится ни в один сезон', Eq((1 - k)*(1 - k/2), R(5, 9)))]
chk('без domain оба корня уравнения проходят',
    ok(say(verify_constants, '29', [R(8, 3)], [k], both)))
chk('с domain второй корень отвергается за то, что он не вероятность',
    no(say(verify_constants, '30', [R(8, 3)], [k], both,
           domain=Interval(0, 1)), 'lies outside'))
chk('а верный проходит и с ним',
    ok(say(verify_constants, '31', [R(1, 3)], [k], both,
           domain=Interval(0, 1))))

print('\n=== незаполненный ответ печатает ⬜, а не падает ===')
chk('verify_event', blank(say(verify_event, '32', ..., plain, P(A | B))))
chk('verify_probability',
    blank(say(verify_probability, '33', ..., boxes, lambda o: True)))
chk('verify_independence',
    blank(say(verify_independence, '34', [..., ...], may, A, B)))

print('\n=== сообщения переводятся ===')
language('ru')
russian = say(verify_event, '35', R(1, 6), cond, P(A, given=B))
language('en')
english = say(verify_event, '36', R(1, 6), cond, P(A, given=B))
chk('в русском режиме сообщение по-русски', 'обратную сторону' in russian)
chk('в английском — по-английски', 'wrong way round' in english)
language('ru')

bad = [name for name, good in res if not good]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
