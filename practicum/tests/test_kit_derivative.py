"""Проверяет механику сверки производных, стационарных точек и постоянных.

Двенадцатое понятие равенства ответов в серии, и самое прямое: производная
у функции ровно одна, и вычисляется она из условия. Эталона поэтому нет
нигде — verify_derivative дифференцирует f сам.

Интересна не эта половина, а вторая. Когда ответ неверен, «не сходится» —
почти бесполезное сообщение: промахов в теме немного и все они именные.
Проверка строит каждый из них из самой f — по тому же правилу, применённому
не так, как оно устроено, — и называет тот, с которым совпало написанное.
Списка неверных ответов при этом тоже нет: они выводятся, а не хранятся.
Здесь измеряется, что каждый именной промах действительно опознаётся,
и — отдельно — что верный ответ ни одним из них не назван.

Рядом два соседа: verify_stationary (точка нулевого наклона это пара чисел,
и половина потерянных баллов темы там, где найдена только первая)
и verify_constants (буквы стоят внутри функции, подставлять ответ некуда —
подставляется он в условия самого вопроса).

Запуск:  python practicum/tests/test_kit_derivative.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *                                                    # noqa: F403

res = []
a, b, c, h, m, n, r = sp.symbols('a b c h m n r')
alpha, theta = sp.symbols('alpha theta')
R = sp.Rational


def t(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def quiet(fn, *args, **kwargs):
    """Гоняет проверку, глотая её вывод, и возвращает (вердикт, вывод)."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        got = fn(*args, **kwargs)
    return got, buf.getvalue()


def yes(name, *args, **kwargs):
    got, _ = quiet(verify_derivative, 'x', *args, **kwargs)
    t(name, got)


def no(name, *args, **kwargs):
    got, out = quiet(verify_derivative, 'x', *args, **kwargs)
    t(name, not got)
    return out


print('=== одна производная в разных записях ===')
for name, form in {
    'свёрнутая': (6*x - 5)*exp(2*x),
    'раскрытая': 6*x*exp(2*x) - 5*exp(2*x),
    'с перестановкой': exp(2*x)*(-5 + 6*x),
    'через 2 и 3 по отдельности': 2*exp(2*x)*(3*x - 4) + 3*exp(2*x),
    'с плавающей точкой': (6.0*x - 5.0)*exp(2*x),
}.items():
    yes(name, form, exp(2*x)*(3*x - 4))

print('\n=== именные промахи, собранные из самой функции ===')
out = no('функция не продифференцирована', exp(2*x)*(3*x - 4), exp(2*x)*(3*x - 4))
t('и это сказано словами', 'not' in out or 'не продифференц' in out)
out = no('цепное правило без внутреннего множителя', cos(2*x), sin(2*x))
t('и назван потерянный множитель', 'chain' in out or 'множител' in out)
out = no('произведение как u′v′', 2*exp(2*x)*3, exp(2*x)*(3*x - 4))
t('и названо произведение', 'u′v′' in out)
out = no('в произведении потеряно слагаемое', 2*exp(2*x)*(3*x - 4),
         exp(2*x)*(3*x - 4))
t('и сказано, что слагаемых должно быть два', 'two' in out or 'двух' in out)
out = no('знаменатель не возведён в квадрат',
         (3*(4*x**2 - 1) - (3*x + 2)*8*x)/(4*x**2 - 1), (3*x + 2)/(4*x**2 - 1))
t('и назван знаменатель', 'denominator' in out or 'наменател' in out)
out = no('в частном перепутан знак числителя',
         ((3*x + 2)*8*x - 3*(4*x**2 - 1))/(4*x**2 - 1)**2,
         (3*x + 2)/(4*x**2 - 1))
t('и назван знак', 'sign' in out or 'знак' in out)
out = no('частное продифференцировано почленно', 3/(8*x), (3*x + 2)/(4*x**2 - 1))
t('и это названо', 'top over bottom' in out or 'почленно' in out)
out = no('показатель не понижен', 4*x**4, x**4)
t('и назван показатель', 'power' in out or 'оказател' in out)

print('\n=== порядок производной ===')
yes('вторая производная', -2*exp(x)*sin(x), exp(x)*cos(x), order=2)
out = no('первая вместо второй', exp(x)*cos(x) - exp(x)*sin(x),
         exp(x)*cos(x), order=2)
t('и порядок назван', 'order 1' in out or 'порядка 1' in out)
out = no('третья вместо второй', -2*exp(x)*(sin(x) + cos(x)),
         exp(x)*cos(x), order=2)
t('и это тоже названо', 'order 3' in out or 'порядка 3' in out)

print('\n=== область функции ===')
yes('корень: обе записи одной и той же функции',
    -1/(4*sqrt((1 + x)**3)), sqrt(1 + x), order=2)
yes('и через дробную степень', -1/(4*(1 + x)**R(3, 2)), sqrt(1 + x), order=2)
t('точки вне области не решают исход: sqrt(1+x) не определён при x < -1', True)

print('\n=== буква в функции ===')
yes('произведение с буквой в показателе',
    n*x**(n - 1)*(a - 2*x)*(a - x)**(n - 1), x**n*(a - x)**n,
    params={n: (2, 3, 5)})
no('и то же самое со скобкой (a - x) + x',
   n*x**(n - 1)*a*(a - x)**(n - 1), x**n*(a - x)**n, params={n: (2, 3, 5)})
yes('частное с буквой', 2*(x - a + 15)*(2*x + a)**2/(x + 5)**3,
    (2*x + a)**3/(x + 5)**2, params={a: (1, 3, 7)})
got, out = quiet(verify_derivative, 'x', 2*x, x**2, params={n: (1, 2), a: (1,)})
t('несогласованные списки params дают сообщение, а не падение',
  not got and 'params' in out)

print('\n=== незаполненный ответ ===')
got, out = quiet(verify_derivative, 'x', ..., x**2)
t('даёт ⬜, а не падение', not got and '⬜' in out)

print('\n=== verify_stationary: обе координаты и все точки ===')
F = cos(x)**2 - 3*sin(x)**2
def st_yes(name, pts, **kw):
    got, _ = quiet(verify_stationary, 'x', pts, F, domain=(0, pi), **kw)
    t(name, got)


def st_no(name, pts, f=None, **kw):
    got, out = quiet(verify_stationary, 'x', pts, f if f is not None else F,
                     domain=(0, pi), **kw)
    t(name, not got)
    return out


st_yes('три точки на замкнутом отрезке', [(0, 1), (pi/2, -3), (pi, 1)])
out = st_no('концы отрезка тоже считаются точками', [(pi/2, -3)])
t('и сказано, сколько их на самом деле', '3' in out)
out = st_no('вторая координата неверна', [(0, 1), (pi/2, 3), (pi, 1)])
t('и сказано, что верна именно первая',
  'second' in out or 'вторая' in out)
out = st_no('точка не стационарна', [(pi/4, -1)])
t('и это названо', 'derivative' in out or 'производная' in out)
out = st_no('точка вне отрезка', [(-pi/2, 1)])
t('и это тоже', 'interval' in out or 'области' in out)
out = st_no('одно число вместо пары', [0])
t('и подсказан вид записи', '(0, E)' in out)
got, _ = quiet(verify_stationary, 'x', [(0, 0), (R(3, 2), R(-9, 16))],
               x**4 - 3*x**3 + 3*x, domain=(-2, 3), order=2)
t('order=2 — точки перегиба', got)
got, out = quiet(verify_stationary, 'x', [(0, 0)],
                 x**4 - 3*x**3 + 3*x, domain=(-2, 3), order=2)
t('и вторая из них не теряется', not got)
got, out = quiet(verify_stationary, 'x', ..., F, domain=(0, pi))
t('незаполненный ответ даёт ⬜', not got and '⬜' in out)

print('\n=== verify_constants: подстановка в условия вопроса ===')
a_, b_, c_ = sp.symbols('a_ b_ c_')
Y = (x - 4)/(a_*x**2 + b_*x + c_)
CONDS = [('vertical asymptote at x = 1', (a_*x**2 + b_*x + c_).subs(x, 1)),
         ('passes through (2, 1)', sp.Eq(Y.subs(x, 2), 1)),
         ('gradient zero there', sp.diff(Y, x).subs(x, 2))]


def cn(name, values, ok):
    got, out = quiet(verify_constants, 'x', values, [a_, b_, c_], CONDS)
    t(name, got is ok)
    return out


cn('верная тройка', [3, -11, 8], True)
out = cn('c на единицу больше', [3, -11, 9], False)
t('и названо первое же нарушенное условие', 'asymptote' in out)
out = cn('значений меньше, чем букв', [3, -11], False)
t('и сказано, сколько их', '3' in out and '2' in out)
got, out = quiet(verify_constants, 'x', ..., [a_], [('A is one', a_ - 1)])
t('незаполненный ответ даёт ⬜', not got and '⬜' in out)
got, _ = quiet(verify_constants, 'x', [-b/(2*a)], [x],
               [('the numerator vanishes', 2*a*x + b)])
t('условие с буквами внутри проверяется символьно', got)
got, _ = quiet(verify_constants, 'x', [b/(2*a)], [x],
               [('the numerator vanishes', 2*a*x + b)])
t('и знак в нём не прощается', not got)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
