"""Механика проверок счёта: verify_count и verify_count_law.

Практикум D1 проверяется в verify_d1.py — там сверяются ответы. Здесь
сверяется сама машинка: что перебор действительно считает то, что описано,
что каждый именной промах узнаётся и называется своим именем, что
устройство `each` не даёт себя обмануть, и что незаполненный ответ
печатает ⬜, а не падает.

Отдельно проверяется главное свойство: проверка не хранит эталона.
Один и тот же ответ проходит или не проходит в зависимости только от
описания объектов, а не от того, что записано в вызове рядом.

Запуск:  python practicum/tests/test_kit_count.py
"""
import contextlib
import io
import os
import sys
from math import factorial

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import (Rational, binomial, combinations, factorial as kit_factorial,
                 language, multiset_permutations, permutations, product,
                 symbols, verify_count, verify_count_law)

# Сообщения сверяются по-английски: практикумы серии печатают их так,
# и ловить формулировку надо в том языке, в котором её увидит студент.
# Перевод проверяется отдельно, в конце.
language('en')

n = symbols('n')
res = []


def chk(name, ok_):
    res.append((name, bool(ok_)))
    print(('✅' if ok_ else '❌'), name)


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


print('=== verify_count: перебор считает то, что описано ===')
chk('всё подряд без ограничения',
    ok(say(verify_count, '1', 125, product(range(5), repeat=3))))
chk('и число вместо перебора принимается тоже',
    ok(say(verify_count, '2', 125, 125)))
chk('с ограничением',
    ok(say(verify_count, '3', 60, product(range(5), repeat=3),
           keep=lambda t: len(set(t)) == 3)))
chk('перебор идёт по объектам, а не по подсказке в вызове',
    ok(say(verify_count, '4', 84, permutations(range(10), 6),
           keep=lambda d: d[0] != 0 and list(d) == sorted(d))))

print('\n=== verify_count: промахи названы по именам ===')
sheep = lambda: product(range(6), repeat=5)
chk('ограничение забыто',
    no(say(verify_count, '5', 7776, sheep(), keep=lambda t: t[0] != t[1]),
       'the restriction is missing'))
chk('посчитано запрещённое',
    no(say(verify_count, '6', 1296, sheep(), keep=lambda t: t[0] != t[1]),
       'the question forbids'))
girls = lambda: permutations(range(5))
chk('порядок внутри пары посчитан дважды',
    no(say(verify_count, '7', 240, girls()),
       'counted twice'))
chk('порядок внутри пары не посчитан',
    no(say(verify_count, '8', 60, girls()),
       'can go two ways'))
chk('ответ меньше верного в 3! раз',
    no(say(verify_count, '9', 4200, permutations(range(10), 3),
           keep=None, each=35),
       '3! times too small'))
chk('ответ больше верного в 3! раз',
    no(say(verify_count, '10', 756756, [None] * 126126),
       '3! times too large'))
chk('а просто мимо — без имени, и без подсказки, сколько на самом деле',
    say(verify_count, '11', 999, sheep()).endswith('does not come to that many'))

print('\n=== verify_count: что ответом быть не может ===')
chk('дробный ответ',
    no(say(verify_count, '12', Rational(3, 2), 10), 'whole number'))
chk('отрицательный ответ',
    no(say(verify_count, '13', -5, 10), 'negative number'))
chk('незаполненный ответ печатает ⬜, а не падает',
    blank(say(verify_count, '14', ..., sheep())))
chk('перебирать нечего',
    no(say(verify_count, '15', 0, []), 'nothing to enumerate'))

print('\n=== verify_count: устройство each ===')
# два ряда по три, шесть детей; ограничение касается двоих
def side_by_side(one, other):
    return one // 3 == other // 3 and abs(one - other) == 1

full = sum(1 for seat in permutations(range(6))
           if side_by_side(seat[0], seat[1]))
chk(f'полный перебор шести детей даёт {full}',
    ok(say(verify_count, '16', full, permutations(range(6)),
           keep=lambda s: side_by_side(s[0], s[1]))))
chk('и перебор по двоим с множителем 4! даёт то же самое',
    ok(say(verify_count, '17', full, permutations(range(6), 2),
           keep=lambda s: side_by_side(s[0], s[1]), each=factorial(4))))
chk('а забытый множитель называется своим именем',
    no(say(verify_count, '18', full // factorial(4), permutations(range(6), 2),
           keep=lambda s: side_by_side(s[0], s[1]), each=factorial(4)),
       'a factor is missing'))
def refuses_keep_without_objects():
    try:
        verify_count('19', 1, 10, keep=lambda item: True)
    except ValueError:
        return True
    return False

chk('фильтру нужен перебор, а не готовое число',
    refuses_keep_without_objects())

# узор с повторами: две книги одного сорта и одна другого
patterns = [p for p in multiset_permutations(list('AAB'))
            if all(c * ''.join(p).count(c) in ''.join(p) for c in 'AB')]
chk('узор с повторами и множителем сходится с прямым перебором',
    ok(say(verify_count, '20', 4, multiset_permutations(list('AAB')),
           keep=lambda p: all(c * ''.join(p).count(c) in ''.join(p)
                              for c in 'AB'),
           each=factorial(2)))
    and len(patterns) == 2)

print('\n=== verify_count_law: выражение сверяется пересчётом ===')
triples = lambda size: sum(1 for _ in combinations(range(size), 3))
chk('ⁿC₃ проходит',
    ok(say(verify_count_law, '21', binomial(n, 3), n, triples, (5, 6, 7, 8))))
chk('и n(n−1)(n−2)/6 — то же выражение, записанное иначе',
    ok(say(verify_count_law, '22', n * (n - 1) * (n - 2) / 6, n, triples,
           (5, 6, 7, 8))))
chk('и n!/(3!(n−3)!) тоже',
    ok(say(verify_count_law, '23',
           kit_factorial(n) / (kit_factorial(3) * kit_factorial(n - 3)),
           n, triples, (5, 6, 7, 8))))
chk('ⁿP₃ отвергается с указанием n, на котором разошлось',
    no(say(verify_count_law, '24', binomial(n, 3) * 6, n, triples, (5, 6, 7, 8)),
       'at n = 5'))
chk('лишняя буква в ответе называется',
    no(say(verify_count_law, '25', binomial(n, 3) * symbols('m'), n, triples,
           (5, 6)), 'extra letter'))
chk('незаполненный ответ печатает ⬜',
    blank(say(verify_count_law, '26', ..., n, triples, (5, 6))))

print('\n=== эталона не хранится ===')
# один и тот же ответ проходит или нет в зависимости только от описания
same = 60
chk('60 верно для размещений из пяти по три',
    ok(say(verify_count, '27', same, permutations(range(5), 3))))
chk('и неверно для сочетаний из пяти по три',
    no(say(verify_count, '28', same, combinations(range(5), 3))))

print('\n=== язык сообщений ===')
language('ru')
russian = say(verify_count, '29', 7776, sheep(), keep=lambda t: t[0] != t[1])
language('en')
english = say(verify_count, '30', 7776, sheep(), keep=lambda t: t[0] != t[1])
chk('в русском режиме сообщение по-русски', 'ограничение' in russian)
chk('в английском — по-английски', 'restriction' in english)
language('ru')

bad = [name for name, good in res if not good]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
