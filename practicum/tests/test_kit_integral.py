"""Проверки E5: первообразная и её семейство — и доказательство, что внутри
них нет интегрирования.

Восемнадцатое понятие равенства ответов держится на одном утверждении:
проверка ответ **узнаёт**, а вычислить его не может. Утверждение легко
обронить при правке — одна строка sp.integrate, и раздел станет обычной
сверкой с sympy, ничего внешне не изменив. Поэтому в конце файла стоит
разбор kit/integral.py через ast: в разделе не должно быть ни вызова
integrate, ни Integral, ни quad из чужой библиотеки, а сложение обязано
оставаться сложением — внутри функции, которая делит отрезок, нет ни одного
обращения к sympy.

Остальное — обычные тесты: верный ответ принимается в любой записи,
постоянная свободна в любом костюме, типовой промах отвергается и
называется по имени, незаполненный ответ даёт ⬜ и не роняет ноутбук.

Запуск:  python practicum/tests/test_kit_integral.py
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
a_, n_, m_ = sp.symbols('a n m')
J = sp.Function('J')

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


print('--- первообразная: семейство, а не выражение ---')
t('простая степень', say(verify_antiderivative, 'A', x**3/3, x**2)[0])
t('и она же с постоянной', say(verify_antiderivative, 'A', x**3/3 + 7, x**2)[0])
t('и с буквой вместо постоянной',
  say(verify_antiderivative, 'A', x**3/3 + C, x**2)[0])
t('постоянная в виде логарифма тоже свободна',
  say(verify_antiderivative, 'A', x**3/3 + log(A)/2, x**2)[0])
t('развёрнутая и свёрнутая записи — одно и то же',
  say(verify_antiderivative, 'A', (log(x) - log(k - x))/k, 1/(x*(k - x)),
      domain=(0.1, 0.9), params={k: (1,)})[0]
  and say(verify_antiderivative, 'A', log(x/(k - x))/k, 1/(x*(k - x)),
          domain=(0.1, 0.9), params={k: (1,)})[0])
t('модуль под логарифмом не мешает',
  say(verify_antiderivative, 'A', log(Abs(x)), 1/x, domain=(0.2, 3.0))[0])
t('по частям', say(verify_antiderivative, 'A', x*acos(x) - sqrt(1 - x**2),
                   acos(x), domain=(-0.9, 0.9))[0])
t('с буквой в показателе',
  say(verify_antiderivative, 'A', sec(x)**n_/n_, sec(x)**n_*tan(x),
      domain=(0.1, 1.0), params={n_: (2, 3, 5)})[0])

print('--- и промахи, названные по имени ---')
ok, msg = say(verify_antiderivative, 'A', sin(3*x), cos(3*x))
t('потерянный делитель замены назван', not ok and 'в 3 раз' in msg)
ok, msg = say(verify_antiderivative, 'A', x**2, x**2)
t('неинтегрированная функция названа', not ok and 'сама подынтегральная' in msg)
ok, msg = say(verify_antiderivative, 'A', 2*x, x**2)
t('продифференцированная вместо проинтегрированной названа',
  not ok and 'продифференцирована' in msg)
ok, msg = say(verify_antiderivative, 'A', x**3/3 + x, x**2)
t('лишнее линейное слагаемое названо', not ok and 'постоянную 1' in msg)
ok, msg = say(verify_antiderivative, 'A', k, x**2, params={k: (3,)})
t('ответ без переменной интегрирования назван',
  not ok and 'не зависит от x' in msg)
t('просто неверный ответ отвергается',
  not say(verify_antiderivative, 'A', x**4, x**2)[0])

print('--- постоянная, снятая точкой ---')
t('точка проходит', say(verify_antiderivative, 'A', x**3 + 5*exp(x) - 1,
                        3*x**2 + 5*exp(x), through=(0, 4))[0])
ok, msg = say(verify_antiderivative, 'A', x**3 + 5*exp(x) + 7,
              3*x**2 + 5*exp(x), through=(0, 4))
t('чужая постоянная отвергается', not ok and 'не проходит через точку' in msg)
ok, msg = say(verify_antiderivative, 'A', x**3 + 5*exp(x) + C,
              3*x**2 + 5*exp(x), through=(0, 4))
t('оставленная буквой постоянная названа', not ok and 'осталась буквой' in msg)

print('--- определённый интеграл: сложение, а не первообразная ---')
t('целое значение', say(verify_integral, 'A', 4, 3 - 5/sqrt(x), 1, 9)[0])
t('точная запись', say(verify_integral, 'A', 5*log(2),
                       (2*x - 15)/((x + 3)*(x - 4)), 0, 3)[0])
t('десятичная запись того же числа',
  say(verify_integral, 'A', 3.4657, (2*x - 15)/((x + 3)*(x - 4)), 0, 3)[0])
t('с буквой', say(verify_integral, 'A', (2**n_ - 1)/n_, sec(x)**n_*tan(x),
                  0, pi/3, params={n_: (2, 3, 5)})[0])
t('бесконечный верхний предел', say(verify_integral, 'A', 24, x**4*exp(-x),
                                    0, oo)[0])
ok, msg = say(verify_integral, 'A', -4, 3 - 5/sqrt(x), 1, 9)
t('переставленные пределы названы', not ok and 'переставлены' in msg)
t('неверное число отвергается',
  not say(verify_integral, 'A', 5, 3 - 5/sqrt(x), 1, 9)[0])
t('предел интегрирования тоже бывает ответом',
  say(verify_integral, 'A', log(3), x/(x**2 + 2), 0, 4)[0]
  and not say(verify_integral, 'A', log(3), x/(x**2 + 2), 0, 5)[0])

print('--- накопленное: обе половины основной теоремы ---')
t('верное накопление',
  say(verify_accumulated, 'A', k*(1 - (3*a_ + 1)*exp(-3*a_))/9,
      k*sp.Symbol("t")*exp(-3*sp.Symbol("t")), 0,
      upper=a_, params={k: (1, 4)})[0])
ok, msg = say(verify_accumulated, 'A', k*(1 - (3*a_ + 1)*exp(-3*a_))/9 + 5,
              k*sp.Symbol('t')*exp(-3*sp.Symbol('t')), 0, upper=a_,
              params={k: (1,)})
t('потерянный нижний предел назван', not ok and 'нижний предел' in msg)
ok, msg = say(verify_accumulated, 'A', k*(1 - (a_ + 1)*exp(-3*a_))/9,
              k*sp.Symbol('t')*exp(-3*sp.Symbol('t')), 0, upper=a_,
              params={k: (1,)})
t('неверная первообразная отвергается', not ok)

print('--- замена переменной ---')
t('законная замена', say(verify_transformed, 'A', u**(n_ - 1),
                         sec(x)**n_*tan(x), sec(x), domain=(0.1, 1.0))[0])
ok, msg = say(verify_transformed, 'A', u**n_, sec(x)**n_*tan(x), sec(x),
              domain=(0.1, 1.0))
t('без множителя замены отвергается', not ok)
ok, msg = say(verify_transformed, 'A', u/(u**2 - u - 2)*cos(x),
              sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2), sin(x))
t('оставленный множитель замены отвергается', not ok)
ok, msg = say(verify_transformed, 'A', x/(x**2 - x - 2),
              sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2), sin(x))
t('ответ, оставшийся в x, назван', not ok and 'осталось' in msg)
ok, msg = say(verify_transformed, 'A', u/(u**2 - u - 2)*u,
              sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2), sin(x))
t('чужое выражение отвергается', not ok)

print('--- формула понижения ---')
t('несобранная формула верна',
  say(verify_reduction, 'A',
      cos(x)**(n_ - 1)*sin(x) + (n_ - 1)*J(n_ - 2) - (n_ - 1)*J(n_),
      cos(x)**n_, n_, J)[0])
t('собранная формула верна',
  say(verify_reduction, 'A',
      cos(x)**(n_ - 1)*sin(x)/n_ + (n_ - 1)*J(n_ - 2)/n_, cos(x)**n_, n_, J)[0])
t('та же формула для синуса',
  say(verify_reduction, 'A',
      -sin(x)**(n_ - 1)*cos(x)/n_ + (n_ - 1)*J(n_ - 2)/n_,
      sin(x)**n_, n_, J)[0])
ok, msg = say(verify_reduction, 'A',
              cos(x)**(n_ - 1)*sin(x)/n_ + (n_ - 1)*J(n_ - 2), cos(x)**n_, n_, J)
t('несобранный делитель отвергается', not ok and 'стороны не равны' in msg)

print('--- почленное интегрирование ряда ---')
t('ряд арктангенса', say(verify_termwise, 'A',
                         x - x**3/3 + x**5/5 - x**7/7 + C, 1/(1 + x**2), 8)[0])
ok, msg = say(verify_termwise, 'A', 1 - x**2 + x**4 - x**6, 1/(1 + x**2), 8)
t('сданный вместо интеграла ряд назван', not ok and 'ряд самой' in msg)
ok, msg = say(verify_termwise, 'A', x - x**3/3 + x**5/5 - x**7/7 + x**9/9,
              1/(1 + x**2), 8)
t('лишняя степень названа', not ok and 'степень 9' in msg)
ok, msg = say(verify_termwise, 'A', x - x**3/2 + x**5/5, 1/(1 + x**2), 6)
t('расхождение названо по члену', not ok and 'расходится' in msg)

print('--- пустой ответ ---')
for name, call in (
        ('verify_antiderivative', lambda: verify_antiderivative('A', ..., x**2)),
        ('verify_integral', lambda: verify_integral('A', ..., x**2, 0, 1)),
        ('verify_integral с пустым пределом',
         lambda: verify_integral('A', 1, x**2, 0, ...)),
        ('verify_accumulated', lambda: verify_accumulated('A', ..., x, 0)),
        ('verify_transformed', lambda: verify_transformed('A', ..., x, x**2)),
        ('verify_reduction',
         lambda: verify_reduction('A', ..., cos(x)**n_, n_, J)),
        ('verify_termwise', lambda: verify_termwise('A', ..., 1/(1 + x**2), 6))):
    ok, msg = say(call)
    t(f'{name}: пустой ответ даёт ⬜', not ok and msg.startswith('⬜'))

print('--- узнавать, а не вычислять ---')
source = open(os.path.join(ROOT, 'practicum/kit/integral.py')).read()
start = source.index('# ================================================= '
                     'первообразная и её семья')
finish = source.index('# ============================================== '
                      'измеренное и его измерение')
section = source[start:finish]
tree = ast.parse(section[section.index('def _numeric('):])
calls = [node.func for node in ast.walk(tree) if isinstance(node, ast.Call)]
names = {node.attr for node in calls if isinstance(node, ast.Attribute)}
names |= {node.id for node in calls if isinstance(node, ast.Name)}
t('в разделе не вызывается integrate', 'integrate' not in names)
t('и не вызывается Integral', 'Integral' not in names)
t('в разделе нет ни одного Integral даже в тексте',
  'Integral' not in section)
t('и никакой чужой квадратуры', not {'quad', 'trapz', 'simps', 'romberg',
                                     'fixed_quad'} & names)
t('nsolve тоже не зовётся: уравнения здесь не решают',
  'nsolve' not in names and 'solve' not in names and 'solveset' not in names)
# Сложение обязано остаться сложением: внутри деления отрезка нет sympy.
step = [node for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == '_simpson'][0]
t('шаг квадратуры обходится без sympy',
  not any(isinstance(node, ast.Attribute) and getattr(node.value, 'id', '') == 'sp'
          for node in ast.walk(step)))
# А дифференцирование, наоборот, обязано быть: им проверка и узнаёт ответ.
t('дифференцирование в разделе есть — это и есть проверка', 'diff' in names)

print(f'\n{"ВСЁ ВЕРНО" if not failed else "ПРОВАЛЫ"}  ({passed}/{passed + failed})')
sys.exit(1 if failed else 0)
