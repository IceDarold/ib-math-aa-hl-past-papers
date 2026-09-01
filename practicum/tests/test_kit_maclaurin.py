"""Проверяет механику сверки рядов Маклорена и оценки числа членов.

Одиннадцатое понятие равенства ответов в серии, и самое своевольное:
у ряда Маклорена нет эталона, с которым его можно было бы сверить, потому
что он определён самой функцией. Ряд до x^k — это единственный многочлен,
у которого разность с функцией обнуляется до x^k включительно. Отсюда и
проверка: verify_maclaurin вычитает написанное из функции и смотрит,
с какой степени начинается остаток.

Здесь измеряется и то, что проверка принимает, и то, что она отвергает,
и отдельно — где она мягче экзамена, а где строже.

Заодно проверяются два соседа: verify_series_solution (ряд решения
дифференциального уравнения — функции нет вовсе, есть уравнение) и
verify_terms (сколько членов знакочередующегося ряда нужно взять).

Запуск:  python practicum/tests/test_kit_maclaurin.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import *                                                    # noqa: F403

res = []
a, m, n = sp.symbols('a m n')
R = sp.Rational


def t(name, ok):
    res.append((name, bool(ok)))
    print(('✅' if ok else '❌'), name)


def quiet(fn, *args, **kwargs):
    """Гоняет проверку, глотая её вывод, и возвращает вердикт."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        got = fn(*args, **kwargs)
    return got, buf.getvalue()


def yes(name, *args, **kwargs):
    got, _ = quiet(verify_maclaurin, 'x', *args, **kwargs)
    t(name, got)


def no(name, *args, **kwargs):
    got, out = quiet(verify_maclaurin, 'x', *args, **kwargs)
    t(name, not got)
    return out


print('=== order: одно разложение в разных записях ===')
for name, form in {
    'по возрастанию': x + x**2 + x**3/3,
    'по убыванию': x**3/3 + x**2 + x,
    'с плавающей точкой': 1.0*x + 1.0*x**2 + 0.3333333333333333*x**3,
    'частично свёрнутое': x*(1 + x + x**2/3),
    'с Rational': x + x**2 + Rational(1, 3)*x**3,
}.items():
    yes(name, form, exp(x)*sin(x), order=3)

print('\n=== order: что отвергается ===')
out = no('пропущен последний член', x + x**2, exp(x)*sin(x), order=3)
t('и сказано, какой именно член', 'x^3' in out)
out = no('неверен средний член', x + 2*x**2 + x**3/3, exp(x)*sin(x), order=3)
t('назван самый низкий из неверных', 'x^2' in out)
no('неверен свободный член', 1 + x, exp(x)*sin(x), order=3)
no('вместо ряда оставлена функция', exp(x)*sin(x), exp(x)*sin(x), order=3)
no('вместо ряда — другая функция', sin(x), exp(x)*sin(x), order=3)
got, out = quiet(verify_maclaurin, 'x', ..., exp(x)*sin(x), order=3)
t('незаполненный ответ даёт ⬜, а не падение', not got and '⬜' in out)

print('\n=== order: где проверка мягче экзамена ===')
yes('лишние верные члены принимаются', x + x**2 + x**3/3 - x**5/30,
    exp(x)*sin(x), order=3)
t('и это совпадает со схемой оценивания мая 2024', True)
no('но лишний неверный член — нет', x + x**2 + x**3/3 + x**4,
   exp(x)*sin(x), order=4)

print('\n=== terms: «первые k ненулевых членов» ===')
yes('два ненулевых члена sin(x^2)', x**2 - x**6/6, sin(x**2), terms=2)
out = no('одного мало', x**2, sin(x**2), terms=2)
t('и сказано, сколько их', '1 non-zero term' in out or '1 ненулевой' in out)
yes('три верных — тоже принимается', x**2 - x**6/6 + x**10/120,
    sin(x**2), terms=2)
no('второй член неверен', x**2 - x**6/3, sin(x**2), terms=2)
yes('глубина берётся из функции, а не фиксирована',
    4*x**3 - 8*x**7/3, 4*x*sin(x**2)*cos(x**2), terms=2)
t('у sin(x^2) вторые члены на x^6, а тут на x^7 — глубина разная', True)
no('почленный квадрат ловится', x**4 - x**12/36, sin(x**2)**2, terms=2)

print('\n=== буква в ответе ===')
yes('ряд с параметром a', 1 + a*x/2 + 3*a**2*x**2/8, (1 - a*x)**R(-1, 2),
    order=2, params={a: (1, 2, -3)})
out = no('и он же с потерянной тройкой', 1 + a*x/2 + a**2*x**2/8,
         (1 - a*x)**R(-1, 2), order=2, params={a: (1, 2, -3)})
t('в сообщении названо, при каком значении буквы', 'a = ' in out)
yes('ряд cos^n x', 1 - n*x**2/2, cos(x)**n, order=2, params={n: (2, 3, 7)})
no('он же без деления на 2', 1 - n*x**2, cos(x)**n, order=2,
   params={n: (2, 3, 7)})

print('\n=== множитель e в коэффициентах ===')
yes('e^(cos 2x) с вынесенной e', E*(1 - 2*x**2 + 8*x**4/3), exp(cos(2*x)),
    order=4)
no('и он же без e', 1 - 2*x**2 + 8*x**4/3, exp(cos(2*x)), order=4)

print('\n=== verify_series_solution: функции нет, есть уравнение ===')
RHS = (x**2*y - y)/(x**2 + 1)


def ode_yes(name, got_expr, **kw):
    got, _ = quiet(verify_series_solution, 'x', got_expr, RHS, 3, 3, **kw)
    t(name, got)


def ode_no(name, got_expr, **kw):
    got, out = quiet(verify_series_solution, 'x', got_expr, RHS, 3, 3, **kw)
    t(name, not got)
    return out


ode_yes('верный отрезок ряда', 3 - 3*x + 3*x**2/2 + 3*x**3/2)
out = ode_no('забыто деление на 3!', 3 - 3*x + 3*x**2/2 + 9*x**3)
t('назван член, с которого поехало', 'x^3' in out)
out = ode_no('забыто деление на 2!', 3 - 3*x + 3*x**2 + 3*x**3/2)
t('и здесь тоже', 'x^2' in out)
out = ode_no('не то начальное условие', 5 - 5*x + 5*x**2/2 + 5*x**3/2)
t('про начальное условие сказано отдельно', '3' in out)
ode_no('y как константа при дифференцировании', 3 - 3*x + 3*x**2/2)
got, _ = quiet(verify_series_solution, 'x',
               3*exp(x - 2*atan(x)), RHS, 3, 3)
t('точное решение — не многочлен, и это названо', not got)
# Оно и не должно проходить: вопрос просит отрезок ряда, а не решение.
series_of_exact = sp.expand(sp.series(3*sp.exp(x - 2*sp.atan(x)), x, 0, 4)
                            .removeO())
ode_yes('а его разложение — проходит', series_of_exact)

print('\n=== verify_terms: на единицу вокруг границы ===')
k = sp.Symbol('k')
TERM = (1/sqrt(3))**(2*k - 1) / (2*k - 1)


def terms_verdict(guess, **kw):
    got, out = quiet(verify_terms, 'x', guess, TERM, R(1, 10000), **kw)
    return got, out


t('шесть членов — то, что нужно', terms_verdict(6)[0])
got, out = terms_verdict(5)
t('пяти мало', not got)
t('и сказано, что отброшенный член ещё велик',
  'not enough' in out or 'не хватает' in out)
got, out = terms_verdict(7)
t('семи много', not got)
t('и подсказано, к какому члену примерять границу',
  'n + 1' in out)
got, out = quiet(verify_terms, 'x', R(5, 2), TERM, R(1, 10000))
t('дробное число членов отвергается', not got)
got, out = quiet(verify_terms, 'x', 0, TERM, R(1, 10000))
t('ноль членов отвергается', not got)
got, out = quiet(verify_terms, 'x', ..., TERM, R(1, 10000))
t('незаполненный ответ даёт ⬜', not got and '⬜' in out)

INTEGRAL = sp.integrate(x**(2*k - 1)/(2*k - 1), (x, 0, 1/sp.sqrt(3)))
got, _ = quiet(verify_terms, 'x', 7, INTEGRAL, 1e-6, strict=False)
t('нестрогая граница: семь членов на 1e-6', got)
got, _ = quiet(verify_terms, 'x', 6, INTEGRAL, 1e-6, strict=False)
t('шести не хватает', not got)

print('\n=== строгая и нестрогая граница расходятся на точном попадании ===')
j = sp.Symbol('j')
EXACT_TERM = 1 / sp.Integer(10)**j          # член j равен 10^-j
got_strict, _ = quiet(verify_terms, 'x', 2, EXACT_TERM, R(1, 1000), var=j)
got_loose, _ = quiet(verify_terms, 'x', 2, EXACT_TERM, R(1, 1000), var=j,
                     strict=False)
t('при равенстве строгая граница не выполняется', not got_strict)
t('а нестрогая выполняется', got_loose)

# Формула члена, записанная не в том аргументе, должна дать сообщение,
# а не падение: в ноутбуке индекс называется k, и перепутать его легко.
got, out = quiet(verify_terms, 'x', 2, EXACT_TERM, R(1, 1000))
t('чужая буква в формуле члена — сообщение, а не исключение',
  not got and ('var' in out))

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
