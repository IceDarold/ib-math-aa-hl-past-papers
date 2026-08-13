"""Проверяет verify_roots на всех уравнениях будущего практикума C3."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import verify_roots, check_expr, digest

x, th = sp.symbols('x theta')
P = sp.pi
ok, bad = [], []


def t(name, got, expect=True):
    (ok if got == expect else bad).append(name)


print('=== эталонные ответы (должны быть ✅) ===')
t('1', verify_roots('1. cos x = -1 на [0,4pi]', [P, 3*P], sp.cos(x) + 1, (0, 4*P)))
t('2', verify_roots('2. tan(2x-5)=1 на [0,180] град', [25, 115],
                    sp.tan(2*x - 5*P/180) - 1, (0, 180), deg=True))
t('4', verify_roots('4. 2cos^2x+5sinx=4 на [0,2pi]', [P/6, 5*P/6],
                    2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)))
t('5', verify_roots('5. cos2x=sinx на [-pi,pi]', [-P/2, P/6, 5*P/6],
                    sp.cos(2*x) - sp.sin(x), (-P, P)))
t('6', verify_roots('6. 2cos2t-5cost+2=0 на [pi,2pi]', [3*P/2],
                    2*sp.cos(2*th) - 5*sp.cos(th) + 2, (P, 2*P), var=th))
t('7', verify_roots('7. cosx=sin2x на [0,pi]', [P/6, P/2, 5*P/6],
                    sp.cos(x) - sp.sin(2*x), (0, P)))
t('8', verify_roots('8. cos^2x-3sin^2x=0 на [0,pi]', [P/6, 5*P/6],
                    sp.cos(x)**2 - 3*sp.sin(x)**2, (0, P)))
t('9', verify_roots('9. (2sin^2 2t-5sin2t-3)/(sin2t-1)=0 на [0,pi]', [7*P/12, 11*P/12],
                    (2*sp.sin(2*th)**2 - 5*sp.sin(2*th) - 3)/(sp.sin(2*th) - 1),
                    (0, P), var=th))
t('12', verify_roots('12. sin2x+cos2x-1+cosx-sinx=0 на (0,2pi)',
                     [P/4, 7*P/6, 5*P/4, 11*P/6],
                     sp.sin(2*x) + sp.cos(2*x) - 1 + sp.cos(x) - sp.sin(x), (0, 2*P)))

print('\n=== эквивалентные формы записи ===')
t('1-float', verify_roots('1 в десятичных', [3.141592653589793, 9.42477796076938],
                          sp.cos(x) + 1, (0, 4*P)))
t('4-deg', verify_roots('4 через arcsin', [sp.asin(sp.Rational(1, 2)), P - sp.asin(sp.Rational(1, 2))],
                        2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)))

print('\n=== типовые ошибки (должны быть ❌) ===')
t('miss', verify_roots('потерян второй корень', [P/6],
                       2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)), False)
t('div', verify_roots('поделили на cos x, потеряв x=pi/2', [P/6, 5*P/6],
                      sp.cos(x) - sp.sin(2*x), (0, P)), False)
t('out', verify_roots('корень вне области', [P/6, 5*P/6, 13*P/6],
                      2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)), False)
t('wrong', verify_roots('неверный корень', [P/3, 5*P/6],
                        2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)), False)
t('dup', verify_roots('корень указан дважды', [P/6, P/6],
                      2*sp.cos(x)**2 + 5*sp.sin(x) - 4, (0, 2*P)), False)
t('blank', verify_roots('не заполнено', ..., sp.cos(x) + 1, (0, 4*P)), False)

print('\n=== арккосинусное уравнение: проверяю утверждение корпуса про x = ±1/2 ===')
f = sp.lambdify(x, sp.acos(x) + sp.acos(3*x) - 3*sp.pi/2, 'math')
for val, name in [(sp.Rational(1, 2), '1/2'), (-sp.Rational(1, 2), '-1/2'),
                  (1/sp.sqrt(10), '1/sqrt(10)'), (-1/sp.sqrt(10), '-1/sqrt(10)')]:
    try:
        print(f'  x = {name:14} невязка = {f(float(val)):+.6f}')
    except ValueError:
        print(f'  x = {name:14} arccos(3x) не определён (|3x| > 1)')

print(f"\n{'ВСЁ ВЕРНО' if not bad else 'ПРОВАЛЫ: ' + str(bad)}  ({len(ok)}/{len(ok) + len(bad)})")
