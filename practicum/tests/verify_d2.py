"""Независимая проверка каждого ответа практикума D2.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не решать никаких уравнений на веса
атомов**. verify_event из kit получает пространство, решая условия вопроса
как линейную (иногда квадратную) систему; если ту же систему решит и тест,
подтверждено будет только то, что sympy согласна сама с собой.

Поэтому вероятности здесь берутся **частотой**. Пишется генератор,
повторяющий историю вопроса — выбрать коробку и вынуть шар, катить кость,
пока не выпадет успех, вынуть три шара и не класть обратно, бросить три
кости, — и событие считается по 400 000 повторений. Совпадение
вычисленной вероятности с долей в длинной серии и есть проверка: это само
определение вероятности, а не другой способ её посчитать.

Там, где истории нет — задачи 1–5 и таймер дают готовые P(A), P(B),
P(A∩B) и ничего, что можно было бы разыграть, — арифметика выписана
в тесте руками, числом за числом, с указанием, откуда каждое взялось.
Это тоже два разных пути: ноутбук решает систему, тест складывает клетки.

Отдельно прогоняется сам ноутбук: пустым (должен пройтись сверху вниз
и напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_d2.py
"""
import contextlib
import io
import json
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp

import build_d2 as gen

R = sp.Rational
y_ = sp.Symbol('y')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


TRIALS = 400_000


def frequency(draw, event, given=None, trials=TRIALS, seed=20260903):
    """Доля исходов, попавших в event, среди тех, что попали в given.

    Никакой алгебры: генератор разыгрывает историю вопроса, а доля
    считается прямым счётом. Возвращает (доля, число испытаний в знаменателе).
    """
    rng = random.Random(seed)
    hit = base = 0
    for _ in range(trials):
        outcome = draw(rng)
        if given is not None and not given(outcome):
            continue
        base += 1
        if event(outcome):
            hit += 1
    return (hit / base if base else float('nan')), base


def agrees(value, share, base, sigmas=5):
    """Совпадает ли точный ответ с долей в длинной серии."""
    value = float(sp.N(sp.sympify(value), 30))
    if base == 0 or not 0 <= value <= 1:
        return False
    err = math.sqrt(max(value * (1 - value), 1e-12) / base)
    return abs(value - share) <= sigmas * err + 1e-9


def A(name):
    return sp.sympify(gen.ANSWERS[name], locals={'y_': y_})


print('=== Задачи 1–3: четыре клетки, арифметика руками ===')
# Задача 1: P(A)=0.65, P(B)=0.75, P(A∩B)=0.6 — клетки 0.05 / 0.6 / 0.15 / 0.2
cells1 = {'A only': R(65, 100) - R(6, 10), 'both': R(6, 10),
          'B only': R(75, 100) - R(6, 10)}
cells1['neither'] = 1 - sum(cells1.values())
chk('1: четыре клетки складываются в единицу и неотрицательны',
    sum(cells1.values()) == 1 and all(v >= 0 for v in cells1.values()))
chk("1a: P(A∪B) — это три клетки, кроме «ни то, ни другое»",
    A('q1a') == 1 - cells1['neither'])
chk("1b: P(A'∩B') — это ровно четвёртая клетка",
    A('q1b') == cells1['neither'])
chk('и 1 - P(A) - P(B) даёт отрицательное число, то есть не ответ',
    1 - R(65, 100) - R(75, 100) < 0)

# Задача 2: 70% спорт, 20% театр, 18% ни то ни другое
both2 = R(7, 10) + R(2, 10) - (1 - R(18, 100))       # включение-исключение
chk('2a: P(S∩T) = 0.7 + 0.2 - 0.82', A('q2a') == both2)
chk('2b: P(T∩S′) = P(T) - P(S∩T)', A('q2b') == R(2, 10) - both2)
chk('и четыре клетки снова дают единицу',
    (R(7, 10) - both2) + both2 + (R(2, 10) - both2) + R(18, 100) == 1)

# Задача 3: P(A)=1/2, P(B)=1/3, P(A|B)=1/4
both3 = R(1, 4) * R(1, 3)
chk('3a: P(A∩B) = P(A|B)·P(B)', A('q3a') == both3)
chk("3b: P(A|B') = (P(A) - P(A∩B)) / (1 - P(B))",
    A('q3b') == (R(1, 2) - both3) / (1 - R(1, 3)))
chk('и 1 - P(A|B) = 3/4 этому не равно', A('q3b') != 1 - R(1, 4))

print('\n=== Задачи 4–5: независимость даёт уравнение ===')
# Задача 4: P(A∪B)=5/8, P(A∩B′)=7/24, независимы
pb4 = R(5, 8) - R(7, 24)                              # A∪B = (A∩B′) ∪ B
chk('4a: P(B) = P(A∪B) - P(A∩B′)', A('q4a') == pb4)
pa4 = R(7, 24) / (1 - pb4)                            # P(A∩B′) = P(A)P(B′)
chk("4b: при независимости P(A'|B) = P(A') = 1 - P(A)",
    A('q4b') == 1 - pa4)
chk('и P(A) = 7/16 — то, что даёт независимость', pa4 == R(7, 16))

# Задача 5: независимы, P(A) = 3P(B), P(A∪B) = 0.68
roots5 = sorted(sp.solve(sp.Eq(3*sp.Symbol('b') + sp.Symbol('b')
                               - 3*sp.Symbol('b')**2, R(68, 100)),
                         sp.Symbol('b')))
chk('5: у квадратного уравнения два корня', len(roots5) == 2)
chk('и ровно один из них не больше единицы',
    sum(1 for r in roots5 if 0 <= r <= 1) == 1)
chk('5: ответ — именно он', A('q5') == [r for r in roots5 if 0 <= r <= 1][0])
chk('второй корень 17/15 больше единицы',
    max(roots5) == R(17, 15) and max(roots5) > 1)

print('\n=== Задача 6: коробка и шар, частотой ===')


def draw6(rng):
    box = rng.choice(['1', '2'])
    balls = ['red']*5 + ['white']*2 if box == '1' else ['red']*4 + ['white']*3
    return box, rng.choice(balls)


share, base = frequency(draw6, lambda o: o[1] == 'red')
chk(f'6a: P(red) = 9/14 совпадает с долей {share:.5f} в {base} розыгрышах',
    agrees(A('q6a'), share, base))
chk('и 5/7 с ней не совпадает', not agrees(R(5, 7), share, base))
sh_ar, ba_ar = frequency(draw6, lambda o: o[0] == '1' and o[1] == 'red')
prod6, joint6 = A('q6b')[0], A('q6b')[1]
chk(f'6b: P(A∩R) = 5/14 совпадает с долей {sh_ar:.5f}',
    agrees(joint6, sh_ar, ba_ar))
chk('и произведение P(A)·P(R) = 9/28 от неё отличается — значит, зависимы',
    not agrees(prod6, sh_ar, ba_ar) and prod6 != joint6)

print('\n=== Задача 7: первый успех, частотой ===')


def draw7(rng):
    for n in range(1, 200):
        if rng.random() < 0.1:
            return n
    return 'never'


share, base = frequency(draw7, lambda o: o == 3)
chk(f'7a: P(первый на третьем) = 0.081 совпадает с долей {share:.5f}',
    agrees(A('q7a'), share, base))
chk('и 0.9**3·0.1 = 0.0729 не совпадает',
    not agrees(R(9, 10)**3*R(1, 10), share, base))
share, base = frequency(draw7, lambda o: o != 'never' and o <= 6)
chk(f'7b: P(хотя бы один из шести) совпадает с долей {share:.5f}',
    agrees(A('q7b'), share, base))
chk('и 1 - 0.9**5 не совпадает', not agrees(1 - R(9, 10)**5, share, base))

print('\n=== Задача 8: буква внутри дерева, частотой ===')
k8 = A('q8')[0]


def draw8(rng):
    return (rng.random() < float(k8), rng.random() < float(k8)/2)


share, base = frequency(draw8, lambda o: not o[0] and not o[1])
chk(f'8: при k = {k8} доля «ни в один сезон» = {share:.5f}, а надо 5/9',
    agrees(R(5, 9), share, base))
chk('и k = 8/3 вероятностью не является', R(8, 3) > 1)

print('\n=== Задачи 9–10: полная вероятность и Байес, частотой ===')


def draw9(rng):
    who = rng.choices(['Amanda', 'Bryce', 'Carmen'], [0.55, 0.25, 0.20])[0]
    bad = {'Amanda': 0.08, 'Bryce': 0.06, 'Carmen': 0.11}[who]
    return who, 'wrong' if rng.random() < bad else 'right'


share, base = frequency(draw9, lambda o: o[1] == 'wrong')
chk(f'9a: P(неверно) = 0.081 совпадает с долей {share:.5f}',
    agrees(A('q9a'), share, base))
chk('и сумма трёх ставок без весов, 0.25, не совпадает',
    not agrees(R(25, 100), share, base))
share, base = frequency(draw9, lambda o: o[0] == 'Amanda',
                        given=lambda o: o[1] == 'wrong')
chk(f'9b: P(Amanda | неверно) совпадает с долей {share:.5f} среди {base}',
    agrees(A('q9b'), share, base))
chk('и обратная условная P(неверно | Amanda) = 0.08 не совпадает',
    not agrees(R(8, 100), share, base))


def draw10(rng):
    name = rng.choice(['A', 'B'])
    q = 0.1 if name == 'A' else 0.05
    return name, sum(1 for _ in range(10) if rng.random() < q)


share, base = frequency(draw10, lambda o: o[1] == 2)
chk(f'10a: P(ровно два брака) совпадает с долей {share:.5f}',
    agrees(A('q10a'), share, base))
share, base = frequency(draw10, lambda o: o[0] == 'A',
                        given=lambda o: o[1] == 2)
chk(f'10b: P(A | ровно два брака) совпадает с долей {share:.5f} среди {base}',
    agrees(A('q10b'), share, base))
chk('и до наблюдения шансы были 1/2 — Байес их сдвинул',
    not agrees(R(1, 2), share, base))

print('\n=== Задача 11: без возвращения, частотой ===')
y11 = int(A('q11b'))


def make_draw11(yellow):
    def draw(rng):
        box = ['Y']*yellow + ['R']*10
        rng.shuffle(box)
        return tuple(box[:3])
    return draw


share, base = frequency(make_draw11(y11), lambda o: o == ('Y', 'Y', 'Y'))
want11 = A('q11a').subs(y_, y11)
chk(f'11a: формула при y = {y11} даёт {sp.nsimplify(want11)}, '
    f'доля {share:.5f}', agrees(want11, share, base))
share2, base2 = frequency(make_draw11(y11 + 1), lambda o: o == ('Y', 'Y', 'Y'),
                          seed=777)
chk(f'11b: с одним лишним жёлтым доля {share2:.5f} вдвое больше',
    agrees(2*want11, share2, base2))
other = A('q11a').subs(y_, y11 + 1)
chk('и удвоение выполняется только при этом y',
    sp.simplify(other - 2*want11) == 0
    and sp.simplify(A('q11a').subs(y_, 6) - 2*A('q11a').subs(y_, 5)) != 0)

print('\n=== Задача 12: 216 троек, частотой ===')


def draw12(rng):
    return (rng.randint(1, 6), rng.randint(1, 6), rng.randint(1, 6))


share, base = frequency(draw12, lambda t: t[1]**2 - 4*t[0]*t[2] == 0)
chk(f'12a: P(один корень) = 5/216 совпадает с долей {share:.5f}',
    agrees(A('q12a'), share, base))
share, base = frequency(draw12, lambda t: t[1]**2 - 4*t[0]*t[2] > 0)
chk(f'12b: P(два различных) = 19/108 совпадает с долей {share:.5f}',
    agrees(A('q12b'), share, base))
chk('и 43/216 — та же доля с двумя лишними случаями — не совпадает',
    not agrees(R(43, 216), share, base))
chk('12: один корень, два корня и ни одного вместе дают единицу',
    A('q12a') + A('q12b')
    + R(sum(1 for u in range(1, 7) for v in range(1, 7) for w in range(1, 7)
            if v*v - 4*u*w < 0), 216) == 1)

print('\n=== Таймер: независимость, арифметика руками ===')
xt = sp.Symbol('xt')
roots_t = sp.solve(sp.Eq(xt, (xt + R(16, 100))*(xt + R(36, 100))), xt)
chk('таймер (a): уравнение независимости имеет один (двойной) корень',
    len(set(roots_t)) == 1)
chk('и это 0.24', A('qt_a') == roots_t[0] == R(24, 100))
chk("таймер (b): P(A'|B') = P(A') = 1 - 0.16 - 0.24",
    A('qt_b') == 1 - R(16, 100) - R(24, 100))

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: эталон проходит, пустой не падает ===')
PLACEHOLDER = re.compile(r'^(\w+) = (\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

with open(gen.NOTEBOOK) as fh:
    notebook_cells = [''.join(c['source']) for c in json.load(fh)['cells']
                      if c['cell_type'] == 'code']

names = set()
for source in notebook_cells:
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            names.add(found.group(1))
chk(f'placeholder-ов ровно столько же, сколько эталонов ({len(names)})',
    names == set(gen.ANSWERS))


TRAINER_FILL = "\n".join(
    f"    {num}: '{code}'," for num, code in sorted(gen.TRIGGER.items()))


def filled(source, override=None):
    """Ячейка с эталонами. Тренажёр распознавания заполняется отдельно:
    его ответы — коды приёмов, а не выражения, и placeholder-ом он не
    размечен."""
    out, in_trainer = [], False
    for line in source.split('\n'):
        found = PLACEHOLDER.match(line)
        if found:
            name = found.group(1)
            out.append(f'{name} = {(override or {}).get(name, gen.ANSWERS[name])}')
            continue
        if line.startswith('answers = {'):
            in_trainer = True
            out.append(line)
            out.append(TRAINER_FILL)
            continue
        if in_trainer:
            if line.startswith('}'):
                in_trainer = False
                out.append(line)
            continue
        out.append(line)
    return '\n'.join(out)


def run(cells):
    space = {'__name__': '__main__'}
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        for source in cells:
            exec(compile(source, '<cell>', 'exec'), space)
    return buffer.getvalue()


here = os.getcwd()
os.chdir(os.path.join(ROOT, 'practicum', 'statistics'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= len(names))

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': 'Rational(7, 5)',                  # пересечение не вычтено
    'q1b': 'Rational(-2, 5)',                 # 1 - P(A) - P(B)
    'q2a': 'Rational(7, 50)',                 # 0.7 + 0.2 - 0.76
    'q2b': 'Rational(1, 5)',                  # взято P(T) целиком
    'q3a': 'Rational(1, 8)',                  # P(A|B)·P(A) вместо ·P(B)
    'q3b': 'Rational(3, 4)',                  # 1 - P(A|B)
    'q4a': 'Rational(11, 24)',                # сложено вместо вычитания
    'q4b': 'Rational(7, 16)',                 # P(A) вместо P(A')
    'q5': 'Rational(17, 15)',                 # корень больше единицы
    'q6a': 'Rational(5, 7)',                  # взята одна коробка
    'q6b': '[Rational(5, 14), Rational(9, 28)]',   # числа переставлены
    'q7a': 'Rational(1, 10)',                 # без множителя 0.9**2
    'q7b': '0.531441',                        # дополнение не взято
    'q8': '[Rational(8, 3)]',                 # отброшен не тот корень
    'q9a': '0.25',                            # ставки сложены без весов
    'q9b': '0.08',                            # условная в обратную сторону
    'q10a': '0.19371',                        # взята одна машина
    'q10b': '0.0968549',                      # числитель без деления
    'q11a': 'y_**3/(y_ + 10)**3',             # знаменатель не уменьшается
    'q11b': '5',                              # соседнее целое
    'q12a': 'Rational(1, 216)',               # найден один случай из трёх
    'q12b': 'Rational(43, 216)',              # два лишних случая
    'qt_a': 'Rational(4, 25)',                # взято P(A∩B') за ответ
    'qt_b': 'Rational(2, 5)',                 # P(B') вместо P(A')
}
missed = []
for name, wrong in sorted(BREAK.items()):
    out = run([filled(source, {name: wrong}) for source in notebook_cells])
    if not [line for line in out.split('\n') if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
