"""Механика проверок фигуры: verify_area, verify_perimeter, verify_length,
verify_volume, verify_law.

Практикум C2 проверяется в verify_c2.py — там сверяются ответы заданий.
Здесь сверяется сама машинка: что мера действительно берётся с границы,
что каждый именной промах узнаётся и называется своим именем, что
незамкнутый контур площади не даёт, и что незаполненный ответ печатает
⬜, а не падает.

Главное свойство то же, что у verify_count: эталона проверка не хранит.
Одно и то же число проходит или не проходит в зависимости только от
описания границы, а формул темы — ½r²θ, ½r²(θ − sin θ), ⅓πr²h — в ней нет.
Поэтому каждая мера здесь сверяется с известным ответом школьной формулы,
посчитанным независимо: круг, кольцо, сектор, сегмент, конус, шар,
цилиндр, тор.

Запуск:  python practicum/tests/test_kit_figure.py
"""
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import (Rational, arc, cone, cos, language, pi, seg, sin, sqrt,
                 symbols, undrawn, verify_area, verify_law, verify_length,
                 verify_perimeter, verify_volume)

TH, MM = symbols('theta m')

# Сообщения сверяются по-английски: практикумы серии печатают их так.
language('en')

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


def sector(r, theta):
    """Сектор: два радиуса и дуга между ними."""
    return (seg((0, 0), (r, 0)), arc((0, 0), r, 0, theta),
            seg((r * cos(theta), r * sin(theta)), (0, 0)))


def segment(r, theta):
    """Сегмент: дуга и стягивающая её хорда."""
    return (arc((0, 0), r, 0, theta),
            seg((r * cos(theta), r * sin(theta)), (r, 0)))


print('=== площадь берётся с границы ===')

# Круг: πr². Радиус 3 → 9π.
chk('круг радиуса 3 даёт 9π',
    ok(say(verify_area, '1', 9 * pi, arc((0, 0), 3, 0, 2 * pi))))
chk('и не даёт 6π — это длина, а не площадь',
    no(say(verify_area, '2', 6 * pi, arc((0, 0), 3, 0, 2 * pi))))

# Сектор: ½r²θ. r = 4, θ = 5/2 → 20.
chk('сектор 4 и 5/2 даёт 20', ok(say(verify_area, '3', 20, *sector(4, Rational(5, 2)))))
chk('десятичная запись той же площади проходит',
    ok(say(verify_area, '4', 20.0, *sector(4, Rational(5, 2)))))
chk('треугольник вместо сектора назван по имени',
    no(say(verify_area, '5', 8 * sin(Rational(5, 2)), *sector(4, Rational(5, 2))),
       'read as a chord'))

# Сегмент: ½r²(θ − sin θ). r = 2, θ = 2 → 2(2 − sin 2) = 2.1814…
seg_area = 2 * (2 - sin(2))
chk('сегмент 2 и 2 даёт ½r²(θ − sin θ)',
    ok(say(verify_area, '6', seg_area, *segment(2, 2))))
chk('сектор вместо сегмента назван по имени',
    no(say(verify_area, '7', 4.0, *segment(2, 2)), 'whole sector'))
chk('треугольник вместо сегмента назван по имени',
    no(say(verify_area, '8', 2 * sin(2), *segment(2, 2)), 'triangle on the same chord'))
chk('сегмент с другой стороны окружности назван по имени',
    no(say(verify_area, '9', 4 * pi - seg_area, *segment(2, 2)),
       'other way round the circle'))

# Кольцевой сектор: ½θ(R² − r²). Именно так устроена буква «C».
def ring(r_in, r_out, theta):
    return (seg((r_in, 0), (r_out, 0)), arc((0, 0), r_out, 0, theta),
            seg((r_out * cos(theta), r_out * sin(theta)),
                (r_in * cos(theta), r_in * sin(theta))),
            arc((0, 0), r_in, theta, 0))


chk('кольцевой сектор даёт ½θ(R² − r²)',
    ok(say(verify_area, '10', Rational(1, 2) * 2 * (100 - 16), *ring(4, 10, 2))))

# Градусы вместо радиан: площадь выходит в 180/π раз больше.
chk('угол в градусах назван по имени',
    no(say(verify_area, '11', 20 * 180 / pi, *sector(4, Rational(5, 2))),
       'degrees'))

print('\n=== контур обязан замкнуться ===')
chk('дуга без хорды площади не даёт',
    no(say(verify_area, '12', 3, arc((0, 0), 2, 0, 2)), 'does not close'))
chk('куски вразнобой площади не дают',
    no(say(verify_area, '13', 3, seg((0, 0), (1, 0)), seg((5, 5), (0, 0))),
       'does not close'))
chk('а для длины замыкаться не нужно',
    ok(say(verify_length, '14', 5, seg((0, 0), (3, 4)))))
chk('разрыв в линии всё равно назван',
    no(say(verify_length, '15', 5, seg((0, 0), (1, 0)), seg((5, 5), (6, 5))),
       'does not join up'))

print('\n=== периметр обходит границу целиком ===')
chk('периметр сектора это дуга и два радиуса',
    ok(say(verify_perimeter, '16', 18, *sector(4, Rational(5, 2)))))
chk('одна дуга вместо периметра названа по имени',
    no(say(verify_perimeter, '17', 10, *sector(4, Rational(5, 2))),
       'only the arcs'))
chk('два радиуса вместо периметра названы по имени',
    no(say(verify_perimeter, '18', 8, *sector(4, Rational(5, 2))),
       'only the straight pieces'))
chk('длина окружности сходится с 2πr',
    ok(say(verify_perimeter, '19', 6 * pi, arc((0, 0), 3, 0, 2 * pi))))

print('\n=== длина линии ===')
chk('хорда сходится с 2r sin(θ/2)',
    ok(say(verify_length, '20', 2 * 5 * sin(Rational(19, 20)),
           seg((5, 0), (5 * cos(1.9), 5 * sin(1.9))))))
chk('большая дуга сходится с r(2π − θ)',
    ok(say(verify_length, '21', 5 * (2 * pi - 1.9), arc((0, 0), 5, 1.9, 2 * pi))))
chk('меньшая дуга вместо большей названа по имени',
    no(say(verify_length, '22', 5 * 1.9, arc((0, 0), 5, 1.9, 2 * pi)),
       'other side of the circle'))
chk('хорда вместо дуги названа по имени',
    no(say(verify_length, '23', 2 * 5 * sin(Rational(19, 20)),
           arc((0, 0), 5, 0, 1.9)), 'chord, not the arc'))

print('\n=== несколько одинаковых контуров ===')
five = []
for k in range(5):
    a0, a1 = k * 2 * pi / 5, (k + 1) * 2 * pi / 5
    five += [arc((0, 0), 3, a0, a1),
             seg((3 * cos(a1), 3 * sin(a1)), (3 * cos(a0), 3 * sin(a0)))]
one = Rational(9, 2) * (2 * pi / 5 - sin(2 * pi / 5))
chk('пять сегментов дают впятеро больше одного',
    ok(say(verify_area, '24', 5 * one, *five)))
chk('один сегмент из пяти назван по имени',
    no(say(verify_area, '25', one, *five), 'and the figure has 5'))

print('\n=== объём тела вращения ===')
chk('конус радиуса 2 и высоты 3 даёт ⅓πr²h',
    ok(say(verify_volume, '26', 4 * pi, *cone(radius=2, height=3))))
chk('конус можно задать образующей вместо высоты',
    ok(say(verify_volume, '27', 8 * sqrt(3) * pi / 3, *cone(radius=2, slant=4))))
chk('цилиндр вместо конуса назван по имени',
    no(say(verify_volume, '28', 12 * pi, *cone(radius=2, height=3)),
       'factor of ⅓ is missing'))
chk('площадь сечения вместо объёма названа по имени',
    no(say(verify_volume, '29', 3, *cone(radius=2, height=3)),
       'area of the cross-section'))
chk('шар радиуса 3 даёт 4πr³/3',
    ok(say(verify_volume, '30', 36 * pi,
           seg((-3, 0), (3, 0)), arc((0, 0), 3, 0, pi))))
chk('цилиндр радиуса 2 и высоты 5 даёт πr²h',
    ok(say(verify_volume, '31', 20 * pi,
           seg((0, 0), (5, 0)), seg((5, 0), (5, 2)),
           seg((5, 2), (0, 2)), seg((0, 2), (0, 0)))))
# Тор: 2π²Rr². Круг радиуса 1 с центром в (0, 3) → 2π²·3·1 = 6π².
chk('тор сходится с теоремой Паппа',
    ok(say(verify_volume, '32', 6 * pi ** 2, arc((0, 3), 1, 0, 2 * pi))))
chk('сечение через ось названо по имени',
    no(say(verify_volume, '33', 1, arc((0, 0), 1, 0, 2 * pi)),
       'crosses the axis'))

print('\n=== точная форма ===')
chk('десятичная запись не принимается там, где просят точное значение',
    no(say(verify_volume, '34', 14.5103, *cone(radius=2, slant=4), exact=True),
       'decimal'))
chk('а корень принимается',
    ok(say(verify_volume, '35', 8 * sqrt(3) * pi / 3,
           *cone(radius=2, slant=4), exact=True)))

print('\n=== незаполненный ответ ===')
chk('пустой ответ печатает ⬜',
    blank(say(verify_area, '36', ..., *sector(4, 2))))
chk('пустая граница печатает ⬜',
    blank(say(verify_length, '37', 5, seg((0, 0), (..., 4)))))
chk('конус без образующей печатает ⬜',
    blank(say(verify_volume, '38', 4 * pi, *cone(radius=2, slant=...))))

print('\n=== ответ-выражение: verify_law ===')
# Фигура строится заново при каждом значении буквы, и сверяется не запись,
# а мера. Любая верная форма проходит.


def grow(theta):
    return segment(2, theta)


chk('2θ − 2 sin θ — площадь сегмента радиуса 2',
    ok(say(verify_law, '43', 2 * TH - 2 * sin(TH), TH, grow, (0.7, 1.9, 2.8))))
chk('и 2(θ − sin θ) — то же самое',
    ok(say(verify_law, '44', 2 * (TH - sin(TH)), TH, grow, (0.7, 1.9, 2.8))))
chk('а сектор 2θ — нет',
    no(say(verify_law, '45', 2 * TH, TH, grow, (0.7, 1.9, 2.8)),
       'theta = 0.7'))
chk('лишняя буква названа',
    no(say(verify_law, '46', TH * MM, TH, grow, (0.7, 1.9)), 'extra letter'))

# at закрепляет вторую букву: «выразите через h и m» иначе не проверить.
chk('at подставляет вторую букву',
    ok(say(verify_law, '47', MM * sqrt(5) * TH, TH,
           lambda v: (seg((0, 0), (v, 2 * v)),), (1, 3, 7),
           measure='length', at={MM: 1})))
chk('и без неё ответ отвергнут как двухбуквенный',
    no(say(verify_law, '48', MM * sqrt(5) * TH, TH,
           lambda v: (seg((0, 0), (v, 2 * v)),), (1, 3, 7),
           measure='length'), 'extra letter'))

# Границу разрешено строить из самого ответа: тогда пустым бывает чертёж,
# а не мера, и пустоту надо увидеть всё равно.
ANSWER = [2]


def from_answer(theta):
    return undrawn(ANSWER[0]) or sector(ANSWER[0], theta)


chk('фигура из ответа: периметр сектора радиуса 2',
    ok(say(verify_law, '49', 4 + 2 * TH, TH, from_answer, (1.0, 2.0),
           measure='perimeter')))
ANSWER[0] = Ellipsis
chk('незаполненный ответ внутри фигуры печатает ⬜',
    blank(say(verify_law, '50', 4 + 2 * TH, TH, from_answer, (1.0,),
              measure='perimeter')))
ANSWER[0] = 2

print('\n=== эталона нет ===')
# Одно и то же число проходит или нет в зависимости только от границы.
chk('20 верно для сектора 4 и 5/2',
    ok(say(verify_area, '39', 20, *sector(4, Rational(5, 2)))))
chk('и неверно для сектора того же радиуса с углом 2',
    no(say(verify_area, '40', 20, *sector(4, 2))))

print('\n=== язык сообщений ===')
language('ru')
russian = say(verify_perimeter, '41', 10, *sector(4, Rational(5, 2)))
language('en')
english = say(verify_perimeter, '42', 10, *sector(4, Rational(5, 2)))
chk('в русском режиме сообщение по-русски', 'только дуги' in russian)
chk('в английском — по-английски', 'only the arcs' in english)
language('ru')

bad = [name for name, good in res if not good]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
