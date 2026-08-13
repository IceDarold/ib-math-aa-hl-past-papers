"""Проверяет verify_roots на всех уравнениях будущего практикума C3."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *                       # проверки + sin, cos, pi, sqrt
from kit import digest

th = Symbol('theta')
pi = pi
ok, bad = [], []


def t(name, got, expect=True):
    (ok if got == expect else bad).append(name)


print('=== эталонные ответы (должны быть ✅) ===')
t('1', verify_roots('1. cos x = -1 на [0,4pi]', [pi, 3*pi], cos(x) + 1, (0, 4*pi)))
t('2', verify_roots('2. tan(2x-5)=1 на [0,180] град', [25, 115],
                    tan(2*x - 5*pi/180) - 1, (0, 180), deg=True))
t('4', verify_roots('4. 2cos^2x+5sinx=4 на [0,2pi]', [pi/6, 5*pi/6],
                    2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)))
t('5', verify_roots('5. cos2x=sinx на [-pi,pi]', [-pi/2, pi/6, 5*pi/6],
                    cos(2*x) - sin(x), (-pi, pi)))
t('6', verify_roots('6. 2cos2t-5cost+2=0 на [pi,2pi]', [3*pi/2],
                    2*cos(2*th) - 5*cos(th) + 2, (pi, 2*pi), var=th))
t('7', verify_roots('7. cosx=sin2x на [0,pi]', [pi/6, pi/2, 5*pi/6],
                    cos(x) - sin(2*x), (0, pi)))
t('8', verify_roots('8. cos^2x-3sin^2x=0 на [0,pi]', [pi/6, 5*pi/6],
                    cos(x)**2 - 3*sin(x)**2, (0, pi)))
t('9', verify_roots('9. (2sin^2 2t-5sin2t-3)/(sin2t-1)=0 на [0,pi]', [7*pi/12, 11*pi/12],
                    (2*sin(2*th)**2 - 5*sin(2*th) - 3)/(sin(2*th) - 1),
                    (0, pi), var=th))
t('12', verify_roots('12. sin2x+cos2x-1+cosx-sinx=0 на (0,2pi)',
                     [pi/4, 7*pi/6, 5*pi/4, 11*pi/6],
                     sin(2*x) + cos(2*x) - 1 + cos(x) - sin(x), (0, 2*pi)))

print('\n=== эквивалентные формы записи ===')
t('1-float', verify_roots('1 в десятичных', [3.141592653589793, 9.42477796076938],
                          cos(x) + 1, (0, 4*pi)))
t('4-deg', verify_roots('4 через arcsin', [asin(Rational(1, 2)), pi - asin(Rational(1, 2))],
                        2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('miss', verify_roots('потерян второй корень', [pi/6],
                       2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)), False)
t('div', verify_roots('поделили на cos x, потеряв x=pi/2', [pi/6, 5*pi/6],
                      cos(x) - sin(2*x), (0, pi)), False)
t('out', verify_roots('корень вне области', [pi/6, 5*pi/6, 13*pi/6],
                      2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)), False)
t('wrong', verify_roots('неверный корень', [pi/3, 5*pi/6],
                        2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)), False)
t('dup', verify_roots('корень указан дважды', [pi/6, pi/6],
                      2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi)), False)
t('blank', verify_roots('не заполнено', ..., cos(x) + 1, (0, 4*pi)), False)

print('\n=== арккосинусное уравнение: проверяю утверждение корпуса про x = ±1/2 ===')
f = lambdify(x, acos(x) + acos(3*x) - 3*pi/2, 'math')
for val, name in [(Rational(1, 2), '1/2'), (-Rational(1, 2), '-1/2'),
                  (1/sqrt(10), '1/sqrt(10)'), (-1/sqrt(10), '-1/sqrt(10)')]:
    try:
        print(f'  x = {name:14} невязка = {f(float(val)):+.6f}')
    except ValueError:
        print(f'  x = {name:14} arccos(3x) не определён (|3x| > 1)')

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  ({len(ok)}/{len(ok) + len(bad)})")
