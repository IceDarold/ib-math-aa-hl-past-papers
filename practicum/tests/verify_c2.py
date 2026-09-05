"""Независимая проверка каждого ответа практикума C2.

Правило то же, что и в остальных проверках серии: ответы здесь выводятся
заново, а не переписываются из раздела решений. Если решение и проверка
совпали — значит, два разных пути привели в одно место.

Для этой темы «независимо» значит **не мерить фигуру**. Ноутбук меряет:
verify_area берёт площадь формулой Грина по контуру, verify_volume
вращает сечение теоремой Паппа. Повтори тест то же самое — подтверждено
будет только то, что Python согласен сам с собой.

Поэтому здесь всё считается **формулами**: s = rθ, ½r²θ, ½r²(θ − sin θ),
2r sin(θ/2), ⅓πr²h, πr² + πrl. Это ровно тот путь, которым идёт
экзаменуемый, и ровно тот, которого в ноутбуке нет. Совпадение формулы
с измерением и есть проверка: контурный интеграл не знает формулы,
формула не знает контурного интеграла.

Там, где схема оценивания даёт два метода, посчитаны оба — и оба сверены
друг с другом до того, как сверяться с ответом.

Затем прогоняется сам ноутбук: пустым (должен пройтись сверху вниз и
напечатать ⬜) и с эталонными ответами из ANSWERS генератора (каждая
проверка обязана сказать ✅). Плюс каждая ячейка проверяется на то,
что типовую ошибку она отвергает, — иначе проверка вида «всегда ✅»
прошла бы этот тест незамеченной.

Запуск:  python practicum/tests/verify_c2.py
"""
import contextlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
sys.path.insert(0, os.path.join(ROOT, 'practicum', 'generators'))
import sympy as sp
from sympy import Rational as R, cos, nsolve, pi, sin, sqrt

import build_c2 as gen

th = sp.Symbol('theta')

res = []


def chk(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def A(name):
    return sp.sympify(gen.ANSWERS[name], locals={'th': th})


def near(one, two, tol=5e-4):
    """Сходятся ли два числа в пределах округления до трёх значащих цифр."""
    one, two = sp.N(one, 20), sp.N(two, 20)
    return abs(float(one - two)) <= tol * max(1.0, abs(float(two)))


# Формулы темы, выписанные один раз и больше нигде не повторяемые.
def arc_length(r, angle):
    return r * angle


def sector_area(r, angle):
    return R(1, 2) * r ** 2 * angle


def triangle_area(r, angle):
    return R(1, 2) * r ** 2 * sin(angle)


def segment_area(r, angle):
    return sector_area(r, angle) - triangle_area(r, angle)


def chord(r, angle):
    return 2 * r * sin(angle / 2)


print('=== Задание 1: дуга, угол, площадь ===')
chk('1a: периметр это дуга и два радиуса', A('q1a') == 10 + 2 * 4 == 18)
chk('и одна дуга дала бы 10, а два радиуса — 8', 10 != A('q1a') != 8)
chk('1b: угол это дуга, делённая на радиус', A('q1b') == R(10, 4) == R(5, 2))
chk('и arc_length возвращает исходные 10', arc_length(4, A('q1b')) == 10)
chk('1c: площадь по ½r²θ', A('q1c') == sector_area(4, A('q1b')) == 20)
chk('и по ½rs — тот же ответ другим путём', A('q1c') == R(1, 2) * 4 * 10)
chk('а треугольник на той же хорде даёт другое число',
    not near(triangle_area(4, A('q1b')), A('q1c')))

print('\n=== Задание 2: пятиугольник ===')
chk('2a(i): пять равных углов складываются в полный оборот',
    A('q2th') == 2 * pi / 5 and sp.simplify(5 * A('q2th') - 2 * pi) == 0)
chk('2a(ii): радиус из s = rθ', sp.simplify(A('q2r') - 12 / A('q2th')) == 0)
chk('и дуга при нём снова 12', sp.simplify(arc_length(A('q2r'), A('q2th')) - 12) == 0)
chk('2b: пять сегментов', near(A('q2b'), 5 * segment_area(A('q2r'), A('q2th'))))
chk('и то же кругом минус пятиугольник — второй метод схемы',
    near(A('q2b'), pi * A('q2r') ** 2 - 5 * triangle_area(A('q2r'), A('q2th'))))
chk('один сегмент дал бы впятеро меньше',
    near(5 * segment_area(A('q2r'), A('q2th')) / 5, 13.9328))

print('\n=== Задание 3: градусы и конус ===')
chk('3a: 210° это 7π/6', sp.rad(210) == 7 * pi / 6)
chk('и площадь сектора точная', A('q3a') == sector_area(R(39, 2), 7 * pi / 6))
chk('и та же площадь долей круга — второй метод схемы',
    sp.simplify(A('q3a') - R(210, 360) * pi * R(39, 2) ** 2) == 0)
chk('и в трёх значащих цифрах это 697', near(A('q3a'), 696.844))
chk('3b: дуга сектора становится окружностью основания',
    sp.simplify(2 * pi * A('q3b') - arc_length(R(39, 2), 7 * pi / 6)) == 0)
chk('и это 91/8 = 11.375', A('q3b') == R(91, 8) and float(A('q3b')) == 11.375)
chk('а радиус сектора 19.5 стал образующей, а не радиусом основания',
    A('q3b') != R(39, 2))

print('\n=== Задание 4: хорда и больший сектор ===')
chk('4a: хорда по половинному углу', near(A('q4a'), chord(5, 1.9)))
chk('и по теореме косинусов — второй метод схемы',
    near(A('q4a'), sqrt(50 - 50 * cos(sp.Float('1.9')))))
chk('и половина хорды вдвое меньше', near(A('q4a') / 2, 5 * sin(sp.Float('0.95'))))
chk('4b: закрашен больший сектор, угол 2π − 1.9',
    near(A('q4b'), sector_area(5, 2 * pi - sp.Float('1.9'))))
chk('и то же кругом минус меньший сектор — второй метод схемы',
    near(A('q4b'), pi * 25 - sector_area(5, sp.Float('1.9'))))
chk('меньший сектор дал бы 23.75', near(sector_area(5, sp.Float('1.9')), 23.75))

print('\n=== Задание 5: треугольник, радиус, большая дуга ===')
chk('5a: радиус из площади треугольника',
    near(triangle_area(A('q5r'), sp.Float('2.51')), 26))
chk('и он равен √(52/sin 2.51)', near(A('q5r'), sqrt(52 / sin(sp.Float('2.51')))))
chk('5b: большая дуга берёт угол 2π − 2.51',
    near(A('q5b'), arc_length(A('q5r'), 2 * pi - sp.Float('2.51'))))
chk('меньшая дала бы 23.6', near(arc_length(A('q5r'), sp.Float('2.51')), 23.5554))

print('\n=== Задание 6: сегмент от θ и логотип ===')
chk('6a: сегмент это сектор без треугольника',
    sp.simplify(A('q6a') - segment_area(2, th)) == 0)
chk('и при θ = 1.9 это 1.90 см²', near(A('q6a').subs(th, 1.9), 2 * 1.9 - 2 * sin(1.9)))
chk('6b: два сегмента, вырезанные из 5 на 4, оставляют 13.4',
    near(20 - 2 * A('q6a').subs(th, A('q6b')), 13.4))
chk('и один сегмент при этом угле равен 3.3',
    near(A('q6a').subs(th, A('q6b')), R(66, 20)))
logo_eq = 20 - 2 * (2 * th - 2 * sin(th)) - sp.Float('13.4')
chk('и корень на (0, π) единственный: из любой стартовой точки один и тот же',
    all(near(sp.nsolve(logo_eq, th, guess), A('q6b'), tol=1e-4)
        for guess in (0.5, 1.5, 2.0, 2.8)))
chk('и в градусах это 135.03 — число, которое схема отвергает',
    near(sp.deg(A('q6b')), 135.030, tol=5e-4))

print('\n=== Задание 7: равные площади ===')
chk('7a: сегмент RQ равен треугольнику POR ровно при θ = 2 sin θ',
    sp.simplify(segment_area(sp.Symbol('r', positive=True), th)
                - triangle_area(sp.Symbol('r', positive=True), pi - th)
                - (sp.Symbol('r', positive=True) ** 2 / 2)
                * (th - 2 * sin(th))) == 0)
chk('7b: округление схемы отстоит от точного корня меньше чем на 0.005',
    abs(float(A('q7')[0]) - 1.89549) < 5e-3)
# Сканирование отрезка вместо solve: у θ − 2 sin θ два генератора,
# алгебраического решения нет, и единственность видна только перебором.
def sign_changes(expr, lo, hi, steps=4000):
    fun = sp.lambdify(th, expr, 'math')
    grid = [lo + (hi - lo) * i / steps for i in range(steps + 1)]
    values = [fun(v) for v in grid]
    return sum(1 for a, b in zip(values, values[1:]) if a * b < 0)


chk('и он единственный на (0.1, π)',
    sign_changes(th - 2 * sin(th), 0.1, float(pi)) == 1)
chk('и это 1.90 — три значащие цифры, как просит бумага',
    A('q7')[0] == sp.Float('1.90'))

print('\n=== Задание 8: периметр и площадь вместе ===')
r_ = sp.Symbol('r', positive=True)
eliminated = sp.simplify(sp.expand(
    (2 * r_ + (10 - 2 * r_)) * 0 + R(1, 2) * r_ * (10 - 2 * r_) - R(25, 4)) * (-4))
chk('8a: исключение θ даёт 4r² − 20r + 25',
    sp.simplify(eliminated - (4 * r_ ** 2 - 20 * r_ + 25)) == 0)
chk('и квадрат этот — полный: (2r − 5)²',
    sp.factor(4 * r_ ** 2 - 20 * r_ + 25) == (2 * r_ - 5) ** 2)
chk('8b(i): единственный корень r = 5/2', A('q8r') == R(5, 2))
chk('8b(ii): и тогда периметр даёт θ = 2',
    2 * A('q8r') + A('q8r') * A('q8th') == 10 and A('q8th') == 2)
chk('и площадь при этих r и θ равна 6.25',
    sector_area(A('q8r'), A('q8th')) == R(25, 4))

print('\n=== Задание 9: буква «C» ===')
chk('9a: разность двух секторов даёт 260 − 2.6r²',
    sp.simplify(sector_area(10, sp.Float('5.2')) - sector_area(r_, sp.Float('5.2'))
                - (260 - sp.Float('2.6') * r_ ** 2)) == 0)
chk('9b(i): радиус из 260 − 2.6r² = 64', near(260 - 2.6 * A('q9r') ** 2, 64))
chk('и точно это 14√65/13', near(A('q9r'), 14 * sqrt(65) / 13))
chk('и он меньше 10, как требует условие', A('q9r') < 10)
chk('9b(ii): периметр это две дуги и две перемычки',
    near(A('q9p'), 10 * 5.2 + A('q9r') * 5.2 + 2 * (10 - A('q9r'))))
chk('без перемычек вышло бы 97.1', near(10 * 5.2 + A('q9r') * 5.2, 97.1487))

print('\n=== Задание 10: периметр в полтора обхвата ===')
r10 = 24 * pi / (th + 2)
chk('10a: периметр сектора равен 1.5 длины окружности',
    sp.simplify((r10 * th + 2 * r10) - sp.Rational(3, 2) * 2 * pi * 8) == 0)
roots10 = sorted(sp.solve(sp.Eq(pi * 64, sector_area(r10, th)), th))
chk('10b: уравнение квадратное и корней два', len(roots10) == 2)
chk('и меньший из них острый и равен 0.411', near(A('q10'), min(roots10)))
chk('а больший, 9.73, острым не бывает', float(max(roots10)) > pi / 2)

print('\n=== Задание 11: жёлоб ===')
chk('11a: 45 = 10 + дуга + 10, и дуга это 25',
    45 - 20 == 25 and near(arc_length(12, R(25, 12)), 25))
chk('и угол в трёх значащих цифрах это 2.08', near(A('q11a'), R(25, 12), tol=2e-3))
w11 = chord(12, A('q11a'))
chk('11b: ширина по половинному углу равна 20.70', near(w11, 20.6977))
chk('и то же по теореме косинусов',
    near(w11, sqrt(2 * 144 - 2 * 144 * cos(A('q11a')))))
chk('сегмент под хордой равен 86.89', near(segment_area(12, A('q11a')), 86.8944))
chk('11b: сегмент плюс прямоугольник 10w', near(A('q11b'), segment_area(12, A('q11a')) + 10 * w11, tol=3e-3))
chk('и точный угол 25/12 даёт 294.4 — те же три значащие цифры',
    near(segment_area(12, R(25, 12)) + 10 * chord(12, R(25, 12)), 294.431)
    and near(A('q11b'), 294.431, tol=2e-3))
chk('один прямоугольник дал бы 207', near(10 * w11, 206.977))

print('\n=== Задание 12: конусы ===')
chk('12a: полная поверхность это основание и боковая часть',
    sp.solve(sp.Eq(pi * 2 ** 2 + pi * 2 * sp.Symbol('l'), 12 * pi),
             sp.Symbol('l')) == [A('q12a')])
chk('без основания вышло бы l = 6',
    sp.solve(sp.Eq(pi * 2 * sp.Symbol('l'), 12 * pi), sp.Symbol('l')) == [6])
h12 = sqrt(A('q12a') ** 2 - 4)
chk('12b: высота по Пифагору равна 2√3', sp.simplify(h12 - 2 * sqrt(3)) == 0)
chk('и объём ⅓πr²h', sp.simplify(A('q12b') - R(1, 3) * pi * 4 * h12) == 0)
chk('и ответ точный, без десятичной записи', not A('q12b').atoms(sp.Float))
chk('цилиндр той же высоты втрое больше',
    sp.simplify(pi * 4 * h12 - 3 * A('q12b')) == 0)
chk('12c: объём памятника', near(A('q12c'), R(1, 3) * pi * sp.Float('6.37262') ** 2 * 20, tol=1e-3))
chk('и округлённый радиус 6.37 даёт 850 — схема принимает оба',
    near(R(1, 3) * pi * sp.Float('6.37') ** 2 * 20, 849.84, tol=1e-3))

print('\n=== Задание 13: поливалка ===')
chk('13a: AB = 2√204 = 28.57', near(2 * sqrt(204), 28.5657, tol=1e-4))
chk('13b: полный оборот за 16 секунд это π/8 в секунду',
    sp.simplify(2 * pi / 16 - pi / 8) == 0)
chk('13c: половинный угол это arccos(14/20)',
    near(cos(sp.acos(R(14, 20))), R(7, 10)))
chk('и T это угол, делённый на скорость',
    near(A('q13c'), 2 * sp.acos(R(14, 20)) / (pi / 8)))
chk('и хорда, которую заметает этот угол, равна 28.57',
    near(chord(20, A('q13c') * pi / 8), 28.5657, tol=1e-3))
chk('13d: угол растёт линейно, α = πt/8',
    sp.simplify((pi / 8) * sp.Symbol('t') - sp.Symbol('t') * 2 * pi / 16) == 0)

print('\n=== Таймер: отношение площадей ===')
chk('P и Q вместе дают сектор',
    sp.simplify(segment_area(r_, th) + triangle_area(r_, th)
                - sector_area(r_, th)) == 0)
chk('отношение 3:5 убивает радиус и оставляет θ = 1.6 sin θ',
    near(A('qt_th') - sp.Float('1.6') * sin(A('qt_th')), 0, tol=1e-4))
chk('и сегмент при найденном r равен 12.8',
    near(segment_area(A('qt_r'), A('qt_th')), sp.Float('12.8')))
chk('и треугольник вдвое с третью больше сегмента: 5/3',
    near(triangle_area(A('qt_r'), A('qt_th')) / sp.Float('12.8'), R(5, 3)))
chk('и сектор равен 8/3 сегмента',
    near(sector_area(A('qt_r'), A('qt_th')), sp.Float('12.8') * R(8, 3)))

# ------------------------------------------------------------------ ноутбук
print('\n=== Ноутбук: эталон проходит, пустой не падает ===')
# Пробелов вокруг знака равенства бывает больше одного: в ячейке
# присваивания выровнены по столбцу, и regex обязан это терпеть.
PLACEHOLDER = re.compile(r'^(\w+)\s*=\s*(\.\.\.|\[\.\.\.\]|\{\.\.\.\})\s*(#.*)?$')

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
os.chdir(os.path.join(ROOT, 'practicum', 'geometry'))
blank = run(notebook_cells)
chk('пустой ноутбук проходится целиком', True)
chk('в пустом прогоне нет ни одной ошибки', '❌' not in blank)
chk('в пустом прогоне нет ни одного ✅', '✅' not in blank)
blanks = blank.count('⬜')
chk(f'в пустом прогоне {blanks} незаполненных ответов', blanks >= 20)

answered = run([filled(source) for source in notebook_cells])
bad_lines = [line for line in answered.split('\n') if line.startswith('❌')]
for line in bad_lines:
    print('   ' + line)
chk('с эталонными ответами ни одна проверка не провалилась', not bad_lines)
chk('пустых ответов не осталось', '⬜' not in answered)

print('\n=== Ноутбук: типовая ошибка отвергается ===')
BREAK = {
    'q1a': '10',                    # посчитана одна дуга
    'q1b': '143.2394',              # угол в градусах
    'q1c': '4.78733',               # треугольник вместо сектора
    'q2th': 'pi/5',                 # пять таких углов круг не замыкают
    'q2r': '5',                     # дуга при нём не 12 см
    'q2b': '13.9328',               # один сегмент из пяти
    'q3a': '39926.25',              # градусы подставлены в ½r²θ
    'q3b': 'Rational(39, 2)',       # радиус сектора принят за радиус основания
    'q4a': '4.06708',               # половина хорды
    'q4b': '23.75',                 # меньший сектор вместо большего
    'q5r': '6',                     # площадь треугольника не сходится
    'q5b': '23.5554',               # меньшая дуга вместо большей
    'q6a': '2*th',                  # сектор вместо сегмента
    'q6b': '135.030',               # ответ в градусах
    'q7': '[0.9]',                  # не корень
    'q8r': '5',                     # корень квадратного уравнения взят неверно
    'q8th': '4',                    # угол не сходится с периметром
    'q9r': '8',                     # площадь «C» при нём не 64
    'q9p': '97.1487',               # перемычки не посчитаны
    'q10': '0.5',                   # площади при нём не равны
    'q11a': '2.5',                  # металла на такую дугу не хватает
    'q11b': '206.977',              # один прямоугольник, без сегмента
    'q12a': '6',                    # основание в полной поверхности забыто
    'q12b': '8*sqrt(3)*pi',         # множитель ⅓ потерян
    'q12c': '2551.62',              # то же в паперовом варианте
    'q13c': '2.02546',              # половина времени
    'qt_th': '1.9',                 # сектор при нём не 8/3 сегмента
    'qt_r': '5',                    # сегмент при нём не 12.8
}
# Прогонять весь ноутбук ради каждой из двадцати восьми ошибок незачем:
# состояние копится один раз, и с неверным ответом переисполняется только
# та ячейка, в которой этот ответ живёт.
snapshots, cell_of = [], {}
space = {'__name__': '__main__'}
with contextlib.redirect_stdout(io.StringIO()):
    for index, source in enumerate(notebook_cells):
        snapshots.append(dict(space))
        for line in source.split('\n'):
            found = PLACEHOLDER.match(line)
            if found:
                cell_of[found.group(1)] = index
        exec(compile(filled(source), '<cell>', 'exec'), space)
chk('у каждого эталона нашлась своя ячейка', set(cell_of) == set(gen.ANSWERS))

missed = []
for name, wrong in sorted(BREAK.items()):
    index = cell_of[name]
    room = dict(snapshots[index])
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        exec(compile(filled(notebook_cells[index], {name: wrong}),
                     '<cell>', 'exec'), room)
    if not [line for line in buffer.getvalue().split('\n')
            if line.startswith('❌')]:
        missed.append(name)
chk(f'все {len(BREAK)} типовых ошибок отвергнуты', not missed)
if missed:
    print('   пропущены:', missed)
os.chdir(here)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
