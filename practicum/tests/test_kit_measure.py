"""Проверки E6: измеренное и его измерение — и доказательство, что внутри
них нет ни одной производной.

Девятнадцатое понятие равенства ответов держится на том, что проверка
меряет заново и меряет по определению меры: площадь — суммой полос,
объём — стопкой дисков, поверхность — набором усечённых конусов, путь —
полной вариацией положения. Утверждение легко обронить при правке: одна
строка sp.diff в проверке поверхности, и вместо длины звена появится
√(1 + (dy/dx)²) — то есть та самая формула, которую ученик и должен был
применить. Поэтому в конце файла стоит разбор kit.py через ast.

Раздел E5 умеет только дифференцировать и не берёт ни одного интеграла.
Раздел E6 умеет только складывать и не берёт ни одной производной.
Обе половины основной теоремы, и ни одна не умеет работы другой —
это и проверяется двумя ast-разборами, здесь и в test_kit_integral.

Запуск:  python practicum/tests/test_kit_measure.py
"""
import ast
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
import kit
from kit import *                                                    # noqa: F403

R = sp.Rational
k_ = sp.Symbol('k')
t_ = sp.Symbol('t')            # t занято проверялкой тестов ниже

passed = failed = 0


def t(name, ok):
    global passed, failed
    if ok:
        passed += 1
    else:
        failed += 1
        print(f'FAIL: {name}')


def say(fn, *args, **kwargs):
    """Вердикт и напечатанное сообщение."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        ok = fn(*args, **kwargs)
    return bool(ok), buffer.getvalue().strip()


print('--- площадь: сумма полос, а не интеграл ---')
t('площадь под кривой точно',
  say(verify_region, 'A', 12*pi, 6 + 6*cos(x), 0, pi, 3*pi)[0])
t('она же тремя цифрами',
  say(verify_region, 'A', 37.7, 6 + 6*cos(x), 0, pi, 3*pi)[0])
t('площадь между прямой и параболой, пределы ищутся сами',
  say(verify_region, 'A', R(9, 2), -x**2 + 9, -3*x + 9)[0])
t('и с явными пределами тот же ответ',
  say(verify_region, 'A', R(9, 2), -x**2 + 9, -3*x + 9, 0, 3)[0])
t('область, где кривые меняются местами, считается целиком',
  say(verify_region, 'A', 4, sin(x), 0, 0, 2*pi)[0])
ok, msg = say(verify_region, 'A', 0, sin(x), 0, 0, 2*pi)
t('и нуль там отвергается как интеграл', not ok and 'интеграл' in msg)
ok, msg = say(verify_region, 'A', -R(9, 2), -3*x + 9, -x**2 + 9, 0, 3)
t('вычтено наоборот — сказано именно это', not ok and 'наоборот' in msg)
ok, msg = say(verify_region, 'A', R(9, 4), -x**2 + 9, -3*x + 9, 0, 3)
t('половина области названа половиной', not ok and 'половина' in msg)
t('несходящийся ответ отвергается',
  not say(verify_region, 'A', 5, -x**2 + 9, -3*x + 9, 0, 3)[0])

print('--- объём: стопка дисков ---')
t('вращение вокруг оси x',
  say(verify_solid, 'A', pi*(2 - sqrt(2))/4, sqrt(x*sin(x**2)), 0, sqrt(pi)/2)[0])
t('вращение вокруг оси y',
  say(verify_solid, 'A', 2*pi*(E**2 + 8*E - 1), 2 + exp(y/4), 0, 4,
      var=y, axis='y')[0])
t('кольцо между двумя кривыми',
  say(verify_solid, 'A', pi, 2*y, 0, 1, inner=y, var=y)[0])
ok, msg = say(verify_solid, 'A', (2 - sqrt(2))/4, sqrt(x*sin(x**2)),
              0, sqrt(pi)/2)
t('потерянное π названо по имени', not ok and 'π' in msg)
ok, msg = say(verify_solid, 'A', pi/3, 2*y, 0, 1, inner=y, var=y)
t('разность радиусов вместо разности квадратов названа',
  not ok and 'квадрат' in msg)
ok, msg = say(verify_solid, 'A', R(1, 2), 2*y, 0, 1, inner=y, var=y)
t('площадь вместо объёма названа площадью', not ok and 'площадь' in msg)
t('обратный ход: ответ ученика стоит верхним пределом',
  say(verify_solid, 'A', pi/3, x, 0, 1)[0])

print('--- поверхность: набор усечённых конусов ---')
t('конус даёт πrl', say(verify_surface, 'A', 18*sqrt(5)*pi, 2*x, 0, 3)[0])
t('сфера даёт 4πr²',
  say(verify_surface, 'A', 16*pi, sqrt(4 - x**2), -2, 2)[0])
t('и с буквой вместо радиуса',
  say(verify_surface, 'A', 4*pi*k_**2, sqrt(k_**2 - x**2), -k_, k_,
      params={k_: (2, 3)})[0])
ok, msg = say(verify_surface, 'A', 9*sqrt(5)*pi, 2*x, 0, 3)
t('π вместо 2π названо', not ok and 'вдвое' in msg)
ok, msg = say(verify_surface, 'A', 3*sqrt(5), 2*x, 0, 3)
t('потерянный множитель y назван длиной кривой',
  not ok and 'длина' in msg)

print('--- путь и перемещение: две меры одного движения ---')
t('путь по скорости со сменой знака',
  say(verify_travelled, 'A', 37.1, t_*sin(t_) - 3, 0, 10)[0])
t('и точный путь многочлена',
  say(verify_travelled, 'A', 13, 4 + 4*t_ - 3*t_**2, 0, 3)[0])
ok, msg = say(verify_travelled, 'A', -22.2, t_*sin(t_) - 3, 0, 10)
t('перемещение вместо пути названо перемещением',
  not ok and 'перемещение' in msg)
t('перемещение со знаком',
  say(verify_position, 'A', -2.13, 2*sin(0.5*t_) + 0.3*t_ - 2, 0, 10)[0])
t('положение с начальным значением',
  say(verify_position, 'A', R(88, 27), 4 + 4*t_ - 3*t_**2, 0, R(2, 3))[0])
ok, msg = say(verify_position, 'A', 37.1, t_*sin(t_) - 3, 0, 10)
t('путь вместо перемещения назван путём', not ok and 'путь' in msg)
ok, msg = say(verify_position, 'A', 2, t_, 0, 2, start=100)
t('неприбавленное начальное значение названо',
  not ok and 'начальное' in msg)

print('--- накопление: числом и функцией времени ---')
t('накопленное число',
  say(verify_amount, 'A', 180000, 50*cos(2*pi*t_/5) + 3000, 0, 60)[0])
t('накопленное выражением от времени',
  say(verify_amount, 'A', 700 - 600*exp(-t_/10) - R(5, 2)*t_**2,
      60*exp(-t_/10) - 5*t_, 0, 20, start=100)[0])
ok, msg = say(verify_amount, 'A', 600 - 600*exp(-t_/10) - R(5, 2)*t_**2,
              60*exp(-t_/10) - 5*t_, 0, 20, start=100)
t('потерянное начальное значение названо', not ok and 'начальное' in msg)
t('выражение, совпавшее в одной точке, всё равно отвергается',
  not say(verify_amount, 'A', 100 + 60*t_ - R(5, 2)*t_**2,
          60*exp(-t_/10) - 5*t_, 0, 20, start=100)[0])

print('--- пустой ответ ---')
for name, call in (
        ('verify_region', lambda: verify_region('A', ..., x, 0, 0, 1)),
        ('verify_region с пустой границей',
         lambda: verify_region('A', 1, ..., 0, 0, 1)),
        ('verify_solid', lambda: verify_solid('A', ..., x, 0, 1)),
        ('verify_solid с пустым пределом',
         lambda: verify_solid('A', 1, x, 0, ...)),
        ('verify_surface', lambda: verify_surface('A', ..., 2*x, 0, 3)),
        ('verify_travelled', lambda: verify_travelled('A', ..., t_, 0, 1)),
        ('verify_position', lambda: verify_position('A', ..., t_, 0, 1)),
        ('verify_amount', lambda: verify_amount('A', ..., t_, 0, 1))):
    ok, msg = say(call)
    t(f'{name}: пустой ответ даёт ⬜', not ok and msg.startswith('⬜'))

print('--- мерить, а не дифференцировать ---')
source = open(os.path.join(ROOT, 'practicum/kit.py')).read()
start = source.index('# ============================================== '
                     'измеренное и его измерение')
finish = source.index('def trigger_check(answers, key):')
section = source[start:finish]
tree = ast.parse(section[section.index('def _pace('):])
calls = [node.func for node in ast.walk(tree) if isinstance(node, ast.Call)]
names = {node.attr for node in calls if isinstance(node, ast.Attribute)}
names |= {node.id for node in calls if isinstance(node, ast.Name)}
t('производная в разделе не берётся ни разу', 'diff' not in names)
t('и Derivative не поминается даже в тексте', 'Derivative' not in section)
t('интегрирования тоже нет', 'integrate' not in names and 'Integral' not in names)
t('и никакой чужой квадратуры', not {'quad', 'trapz', 'simps', 'romberg',
                                     'fixed_quad'} & names)
t('уравнения здесь не решают',
  not {'solve', 'nsolve', 'solveset', 'roots', 'real_roots'} & names)
# Длина звена обязана быть настоящей длиной звена, а не √(1 + (dy/dx)²)·Δx.
skin = [node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == '_frustums'][0]
inside = {node.attr for node in ast.walk(skin)
          if isinstance(node, ast.Attribute)}
t('поверхность набирается по настоящей длине звена', 'hypot' in inside)
t('и внутри неё нет ни производной, ни интеграла',
  not {'diff', 'integrate', 'Integral'} & inside)
# Пересечения ищутся делением пополам, а не решением уравнения.
meet = [node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == '_crossings'][0]
t('пересечения ищутся делением пополам',
  not {'solve', 'nsolve', 'solveset'} &
  {node.attr for node in ast.walk(meet) if isinstance(node, ast.Attribute)})

print(f'\n{"ВСЁ ВЕРНО" if not failed else "ПРОВАЛЫ"}  ({passed}/{passed + failed})')
