"""Сообщения проверок не смешивают языки.

Практикум B2 написан по-английски, а kit общий: одна забытая строка —
и посреди английской работы печатается «не сходится». Проверок две.

Статическая разбирает модули kit через ast и ищет строковые литералы
с кириллицей, не спрятанные в первый аргумент `_t`. Она полная: видит
и то, что печатается не напрямую, а через возвращённое поясение.

Динамическая гоняет каждую печатающую функцию в режиме 'en' — успех,
провал и незаполненный ответ — и требует, чтобы в выводе не было
ни одной кириллической буквы. Она проверяет то, чего ast не знает:
что переключатель языка действительно доходит до печати.

Запуск:  python practicum/tests/check_language.py
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

# `from kit import *` приносит sympy-шный re (действительная часть) и
# перекрывает модуль регулярных выражений — про это сказано в kit/core.py.
# Поэтому настоящий re импортируется после звёздочки и под своим именем.
import re as _re                                                     # noqa: E402
import itertools                                                     # noqa: E402

# Для verify_count_law нужны своя буква и свой пересчёт: N уже занято
# символом задачи, а перебор в проверке должен быть настоящим.
N_ = sp.Symbol('n')


def _triples(size):
    return sum(1 for _ in itertools.combinations(range(size), 3))


def _blank_figure():
    """verify_law при незаполненном ответе внутри самой фигуры."""
    _ANSWER[0] = Ellipsis
    try:
        return verify_law('t', 2 * sp.pi, sp.Symbol('theta'), _from_answer,
                          (1.0,), measure='perimeter')
    finally:
        _ANSWER[0] = 2


# Границы для проверок фигуры: сектор радиуса 4 с углом 5/2 и сегмент
# радиуса 2 с углом 2. Строятся один раз — вызовов с ними два десятка.
_THETA = sp.Rational(5, 2)
_sector = (seg((0, 0), (4, 0)), arc((0, 0), 4, 0, _THETA),
           seg((4 * sp.cos(_THETA), 4 * sp.sin(_THETA)), (0, 0)))
_segment = (arc((0, 0), 2, 0, 2),
            seg((2 * sp.cos(2), 2 * sp.sin(2)), (2, 0)))

# verify_law строит фигуру заново при каждом значении буквы. TH — буква,
# _grow — сегмент радиуса 2 при этом угле, _stretch — отрезок из начала
# координат, длина которого зависит сразу от двух букв: одну из них
# закрепляет at.
TH = sp.Symbol('theta')
MM = sp.Symbol('m')


def _grow(angle):
    return (arc((0, 0), 2, 0, angle),
            seg((2 * sp.cos(angle), 2 * sp.sin(angle)), (2, 0)))


def _stretch(length):
    return (seg((0, 0), (length, 2 * length)),)


def _from_answer(angle):
    """Фигура, построенная из ответа: он приходит извне и бывает пуст."""
    return undrawn(_ANSWER[0]) or (arc((0, 0), _ANSWER[0], 0, angle),
                                   seg((_ANSWER[0] * sp.cos(angle),
                                        _ANSWER[0] * sp.sin(angle)), (0, 0)),
                                   seg((0, 0), (_ANSWER[0], 0)))


_ANSWER = [2]

CYR = _re.compile('[А-Яа-яЁё]')
KIT = os.path.join(ROOT, 'practicum', 'kit')
n = sp.Symbol('n')
problems = []


def static_scan():
    """Строки с кириллицей вне русской половины `_t`: (файл, строка, текст)."""
    out = []
    for name in sorted(os.listdir(KIT)):
        if name.endswith('.py'):
            path = os.path.join(KIT, name)
            out += [(f'kit/{name}', line, text)
                    for line, text in scan_file(io.open(path, encoding='utf-8').read())]
    return out


def scan_file(source):
    tree = ast.parse(source)
    exempt, docs = set(), set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == '_t' and node.args):
            exempt.update(id(sub) for sub in ast.walk(node.args[0]))
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
            first = node.body[0] if node.body else None
            if (isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)):
                docs.add(id(first.value))
    out = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                and CYR.search(node.value)
                and id(node) not in exempt and id(node) not in docs):
            out.append((node.lineno, node.value.strip()[:70]))
    return out


def calls():
    """Каждая печатающая функция kit: успех, провал, пустой ответ.

    Аргументы подобраны так, чтобы задеть и ветки с длинными пояснениями:
    лишний корень, потерянный корень, множитель с буквой, десятичная
    запись вместо точной, неоднозначный треугольник.
    """
    yield lambda: verify_ode('t', exp(2 * x), 2 * y)
    yield lambda: verify_ode('t', exp(x), 2 * y)
    yield lambda: verify_ode('t', ..., 2 * y)
    yield lambda: verify_implicit('t', Eq(x**2 - y**2, 4), Eq(2 * x**2 - 2 * y**2, 8))
    yield lambda: verify_implicit('t', Eq(x + y, 1), Eq(x - y, 1))
    yield lambda: check_num('t', 2.5, 3, digest(sig(2.5, 3)))
    yield lambda: check_num('t', 2.7, 3, digest(sig(2.5, 3)))
    yield lambda: check_expr('t', 2 * x, digest(sp.srepr(sp.simplify(2 * x))))
    yield lambda: check_expr('t', 3 * x, digest(sp.srepr(sp.simplify(2 * x))))
    yield lambda: check_complex('t', 1 + I, digest(kit._complex_canon(1 + I)))
    yield lambda: check_complex('t', 1 - I, digest(kit._complex_canon(1 + I)))
    yield lambda: check_complex_set('t', [I], digest(kit._complex_canon(I)))
    yield lambda: check_complex_set('t', [2 * I], digest(kit._complex_canon(I)))
    yield lambda: check_series('t', x**2, digest(kit._series_canon(x**2, x)))
    yield lambda: check_series('t', x**3, digest(kit._series_canon(x**2, x)))
    yield lambda: check_set('t', [1, 2], digest('|'.join(sorted(
        sp.srepr(sp.simplify(v)) for v in (1, 2)))))
    yield lambda: check_set('t', [1, 3], digest('|'.join(sorted(
        sp.srepr(sp.simplify(v)) for v in (1, 2)))))
    yield lambda: verify_identity('t', sin(x)**2, 1 - cos(x)**2)
    yield lambda: verify_identity('t', sin(x)**2, cos(x)**2)
    yield lambda: verify_identity('t', 1 / (x - x), 0)
    yield lambda: verify_induction('t', (k + 1) * (k + 2) / 2, k * (k + 1) / 2,
                                   base_lhs=1)
    yield lambda: verify_induction('t', k * (k + 2) / 2, k * (k + 1) / 2, base_lhs=5)
    yield lambda: verify_induction('t', ..., k * (k + 1) / 2, base_lhs=...)
    yield lambda: verify_divisibility('t', 5**(2 * k) - 2**(3 * k), 17, 8)
    yield lambda: verify_divisibility('t', 5**(2 * k) - 2**(3 * k), 17, 1)
    yield lambda: verify_divisibility('t', 5**(2 * k) - 2**(3 * k) + 1, 17, 8)
    yield lambda: verify_rewrite('t', 2 * x, 2, 2 * x - 2)
    yield lambda: verify_residue('t', (2 * k + 1)**2, 8, 1)
    yield lambda: verify_residue('t', (2 * k + 1)**2, 8, 3)
    yield lambda: verify_residue('t', sp.Rational(1, 2) * k, 2, 0)
    yield lambda: check_order('t', ['a', 'b'], digest('a|b'), n=2)
    yield lambda: check_order('t', ['b', 'a'], digest('a|b'), n=2)
    yield lambda: check_order('t', ['a'], digest('a|b'), n=2)
    yield lambda: verify_factored('t', (x + 1) * (x - 2), x**2 - x - 2, n=2)
    yield lambda: verify_factored('t', x**2 - x - 2, x**2 - x - 2)
    yield lambda: verify_factored('t', (x**2 + 1) * (x - 2), x**3 - 2 * x**2 + x - 2)
    yield lambda: verify_factored('t', (x + 1) * (x - 3), x**2 - x - 2)
    yield lambda: verify_factored('t', (x + 1) * (x - 2), x**2 - x - 2, n=3)
    yield lambda: verify_factored('t', 2 * sqrt(x) * (x - 2), x**2 - x - 2)
    yield lambda: verify_division('t', x, -3, x**2 + 1, x)
    yield lambda: verify_division('t', x, 1, x**2 + 1, x)
    yield lambda: verify_division('t', 1, x**2, x**2 + 1, x)
    yield lambda: verify_divisible('t', x**2 + A * x + 1, x + 1, subs={A: 2})
    yield lambda: verify_divisible('t', x**2 + A * x + 1, x + 1, subs={A: 3})
    yield lambda: check_apart('t', 1 / (x + 1) - 1 / (x + 2),
                              1 / ((x + 1) * (x + 2)))
    yield lambda: check_apart('t', 1 / ((x + 1) * (x + 2)),
                              1 / ((x + 1) * (x + 2)))
    yield lambda: check_apart('t', x / (x + 1), x / (x + 1))
    yield lambda: check_apart('t', 1 / (x + 1), 1 / (x + 2))
    yield lambda: check_apart('t', x + 1, x + 1)
    yield lambda: verify_root_transform('t', [1, 0, -4], x**2 - 1,
                                        lambda r: 2 * r)
    yield lambda: verify_root_transform('t', [1, 0, -9], x**2 - 1,
                                        lambda r: 2 * r)
    yield lambda: verify_root_transform('t', [1, 0], x**2 - 1, lambda r: 2 * r)
    yield lambda: verify_root_transform('t', [1, 0, -4], x**2, lambda r: 1 / r)
    yield lambda: verify_solution_set('t', Interval.open(-1, 2), x**2 - x - 2 < 0)
    yield lambda: verify_solution_set('t', Interval(-1, 2), x**2 - x - 2 < 0)
    yield lambda: verify_solution_set('t', 5, x**2 - x - 2 < 0)
    yield lambda: verify_param_set('t', Interval.open(0, oo),
                                   lambda v: bool(v > 0))
    yield lambda: verify_param_set('t', Interval.open(1, oo),
                                   lambda v: bool(v > 0))
    yield lambda: verify_param_set('t', Interval.open(-oo, 0),
                                   lambda v: bool(v > 0))
    yield lambda: verify_param_set('t', 5, lambda v: bool(v > 0))
    yield lambda: verify_param_set('t', Interval.open(0, oo), lambda v: None)
    yield lambda: verify_nonneg_form('t', (x - y)**2, x**2 - 2 * x * y + y**2)
    yield lambda: verify_nonneg_form('t', -(x - y)**2, x**2 - 2 * x * y + y**2)
    yield lambda: verify_nonneg_form('t', x**3, x**3)
    yield lambda: verify_nonneg_form('t', (x + y)**2, x**2 - 2 * x * y + y**2)
    yield lambda: verify_nonneg_form('t', x**2 + sp.Integer(-1) * 1,
                                     x**2 - 1)
    yield lambda: verify_equation('t', Eq(2 * x**2 - 2, 0), Eq(x**2 - 1, 0))
    yield lambda: verify_equation('t', Eq(x**2, x**2), Eq(x**2 - 1, 0))
    yield lambda: verify_equation('t', Eq(x**3 - x, 0), Eq(x**2 - 1, 0))
    yield lambda: verify_equation('t', Eq(A * x**2 - A, 0), Eq(x**2 - 1, 0))
    yield lambda: verify_equation('t', Eq(x + 1, 0), Eq(x**2 - 1, 0))
    yield lambda: verify_root_set('t', [2], x**2 - 4, domain=(0, 10))
    yield lambda: verify_root_set('t', [2, 2], x**2 - 4)
    yield lambda: verify_root_set('t', [-2], x**2 - 4, domain=(0, 10))
    yield lambda: verify_root_set('t', [2], x**2 - 4)
    yield lambda: verify_root_set('t', [3], x**2 - 4)
    yield lambda: verify_root_set('t', [2], 1 / (x - 2))
    yield lambda: verify_vertex_form('t', (x - 1)**2 + 2, x**2 - 2 * x + 3)
    yield lambda: verify_vertex_form('t', x**2 - 2 * x + 3, x**2 - 2 * x + 3)
    yield lambda: verify_vertex_form('t', (2 * x - 1)**2, 4 * x**2 - 4 * x + 1)
    yield lambda: verify_vertex_form('t', (x - 1)**2 + x, x**2 - x + 1)
    yield lambda: verify_vertex_form('t', (x - 1)**2 + 5, x**2 - 2 * x + 3)
    yield lambda: verify_triangle('t', {'c': 5.0}, a=3, b=4, C=90)
    yield lambda: verify_triangle('t', {'c': 9.0}, a=3, b=4, C=90)
    yield lambda: verify_triangle('t', {'c': 5.0}, a=3, b=4, c=99)
    yield lambda: verify_triangle('t', {'B': 41.8}, a=8, b=6, A=60)
    yield lambda: verify_exact('t', 2 * sqrt(6), sqrt(24))
    yield lambda: verify_exact('t', 4.89898, sqrt(24))
    yield lambda: verify_exact('t', sqrt(23), sqrt(24))
    yield lambda: verify_roots('t', [0, pi], sin(x), (0, pi))
    yield lambda: verify_roots('t', [0], sin(x), (0, pi))
    yield lambda: verify_roots('t', [1], sin(x), (0, pi))
    yield lambda: verify_roots('t', [7], sin(x), (0, pi))
    yield lambda: verify_inverse('t', sqrt(x**2 + 1), sqrt(x**2 - 1),
                                domain=Interval(1, 2))
    yield lambda: verify_inverse('t', -sqrt(x**2 + 1), sqrt(x**2 - 1),
                                domain=Interval(1, 2))
    yield lambda: verify_inverse('t', (4 * x + 7) / (2 * x + 7),
                                (7 * x + 7) / (2 * x - 4), domain=Interval(3, 9))
    yield lambda: verify_inverse('t', sqrt(x - 100), sqrt(x**2 - 1),
                                domain=Interval(1, 2))
    yield lambda: verify_inverse('t', ..., sqrt(x**2 - 1), domain=Interval(1, 2))
    yield lambda: verify_transform('t', [('shift_y', 3)], x**2, x**2 + 3)
    yield lambda: verify_transform('t', [('stretch_x', sp.Rational(1, 2)),
                                         ('shift_x', -sp.Rational(1, 2))],
                                   atan(x), atan(2 * x + 1))
    yield lambda: verify_transform('t', [('shift_x', -sp.Rational(1, 2)),
                                         ('stretch_x', sp.Rational(1, 2))],
                                   atan(x), atan(2 * x + 1))
    yield lambda: verify_transform('t', [('stretch_x', 2),
                                         ('shift_x', -sp.Rational(1, 2))],
                                   atan(x), atan(2 * x + 1))
    yield lambda: verify_transform('t', [('shift_x', -3)], x**2, (x - 3)**2)
    yield lambda: verify_transform('t', [('shift_y', -3)], x**2, x**2 + 3)
    yield lambda: verify_transform('t', [('stretch_y', 5)], x**2, x**3)
    yield lambda: verify_transform('t', [('rotate', 90)], x**2, -x**2)
    yield lambda: verify_transform('t', 5, x**2, -x**2)
    yield lambda: verify_transform('t', ..., x**2, -x**2)
    yield lambda: verify_sketch('t', {'x_intercepts': [-1, 1],
                                      'y_intercept': -1,
                                      'minima': [(0, -1)]}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'x_intercepts': [-1]}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'x_intercepts': [-1, 0, 1]}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'maxima': [(0, -1)]}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'minima': [(0, 5)]}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'y_intercept': 5}, x**2 - 1,
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'y_intercept': 5}, 1 / x,
                                domain=Interval.open(0, 2))
    yield lambda: verify_sketch('t', {'y_intercept': 'x'}, x**2 - 1)
    yield lambda: verify_sketch('t', {'cusps': [(0, 0)]}, Abs(x),
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'minima': [(0, 0)]}, Abs(x),
                                domain=Interval(-2, 2))
    yield lambda: verify_sketch('t', {'vertical_asymptotes': [0],
                                      'horizontal_asymptotes': [0]}, 1 / x)
    yield lambda: verify_sketch('t', {'oblique_asymptotes': [x]},
                                x + 1 / x)
    yield lambda: verify_sketch('t', {'oblique_asymptotes': [x + 1]},
                                x + 1 / x)
    yield lambda: verify_sketch('t', {'oblique_asymptotes': []},
                                x + 1 / x)
    yield lambda: verify_sketch('t', {'x_intercepts': ['q']}, x**2 - 1)
    yield lambda: verify_sketch('t', {'inflexions': [0]}, x**2 - 1)
    yield lambda: verify_sketch('t', [1, 2], x**2 - 1)
    yield lambda: verify_sketch('t', {'minima': ...}, x**2 - 1)
    yield lambda: check_domain('t', Interval(0, 2), digest(sp.srepr(Interval(0, 2))))
    yield lambda: check_domain('t', Interval(0, 3), digest(sp.srepr(Interval(0, 2))))
    yield lambda: check_domain('t', 5, digest(sp.srepr(Interval(0, 2))))
    yield lambda: verify_asymptotes('t', [Eq(x, -3), Eq(y, x/2 - sp.Rational(17, 2))],
                                    (x**2 - 14*x + 24)/(2*x + 6))
    yield lambda: verify_asymptotes('t', Eq(2*x + 6, 0),
                                    (x**2 - 14*x + 24)/(2*x + 6),
                                    kinds=('vertical',))
    yield lambda: verify_asymptotes('t', [Eq(x, -3)],
                                    (x**2 - 14*x + 24)/(2*x + 6))
    yield lambda: verify_asymptotes('t', [-3], (x**2 - 14*x + 24)/(2*x + 6),
                                    kinds=('vertical',))
    yield lambda: verify_asymptotes('t', [Eq(x, 3)],
                                    (x**2 - 14*x + 24)/(2*x + 6),
                                    kinds=('vertical',))
    yield lambda: verify_asymptotes('t', [Eq(y, -2)], (2*x + 4)/(3 - x),
                                    kinds=('vertical',))
    yield lambda: verify_asymptotes('t', [Eq(y, x**2)],
                                    (x**2 - 14*x + 24)/(2*x + 6))
    yield lambda: verify_asymptotes('t', ..., (2*x + 4)/(3 - x))
    yield lambda: verify_asymptotes('t', [Eq(x, 3), Eq(y, -2)],
                                    (2*x + 4)/(3 - x))
    yield lambda: verify_range('t', (y >= -5), 6*x**2 - 12*x + 1)
    yield lambda: verify_range('t', (y >= -4), 6*x**2 - 12*x + 1)
    yield lambda: verify_range('t', (y >= -6), 6*x**2 - 12*x + 1)
    yield lambda: verify_range('t', 5, 6*x**2 - 12*x + 1)
    yield lambda: verify_range('t', ..., 6*x**2 - 12*x + 1)
    yield lambda: verify_range('t', Interval.Lopen(sp.Rational(-3, 2), 2),
                               -(3*x - 2)/(2*x + 1), domain=Interval(0, oo))
    yield lambda: verify_range('t', Interval(sp.Rational(-3, 2), 2),
                               -(3*x - 2)/(2*x + 1), domain=Interval(0, oo))
    yield lambda: verify_range('t', Interval(-1, 1), sin(x) + sin(pi*x)/1000)
    yield lambda: verify_model('t', 15000 * exp(-t), [(0, 15000)])
    yield lambda: verify_model('t', 15000 * exp(-t), [(1, 15000)])
    yield lambda: verify_model('t', 15000 * exp(k * t), [(0, 15000)])
    yield lambda: verify_model('t', ..., [(0, 15000)])
    yield lambda: verify_in_terms_of('t', 3 * A, log(8, 10), {A: log(2, 10)})
    yield lambda: verify_in_terms_of('t', 2 * A, log(8, 10), {A: log(2, 10)})
    yield lambda: verify_in_terms_of('t', log(8, 10), log(8, 10), {A: log(2, 10)})
    yield lambda: verify_in_terms_of('t', 3 * A + B, log(8, 10), {A: log(2, 10)})
    yield lambda: verify_in_terms_of('t', ..., log(8, 10), {A: log(2, 10)})
    yield lambda: verify_limit('t', sp.Rational(2, 3), atan(2*x)/tan(3*x))
    yield lambda: verify_limit('t', 1, atan(2*x)/tan(3*x))
    yield lambda: verify_limit('t', x, atan(2*x)/tan(3*x))
    yield lambda: verify_limit('t', oo, atan(2*x)/tan(3*x))
    yield lambda: verify_limit('t', -k/2, (cos(x)**k - 1)/x**2)
    yield lambda: verify_limit('t', -k/2, (cos(x)**k - 1)/x**2,
                               params={k: (1, 2), A: (1,)})
    yield lambda: verify_limit('t', 1, log(x), point=0, side='+')
    yield lambda: verify_limit('t', ..., atan(2*x)/tan(3*x))
    yield lambda: verify_indeterminate('t', '0/0', sin(x), x)
    yield lambda: verify_indeterminate('t', 'oo/oo', sin(x), x)
    yield lambda: verify_indeterminate('t', '0/0', cos(x), x**2)
    yield lambda: verify_indeterminate('t', 'junk', sin(x), x)
    yield lambda: verify_indeterminate('t', ..., sin(x), x)
    # E2: ряды. Статический проход их видел, динамический — нет; добавлено
    # вместе с E3, потому что оба списка должны покрывать один и тот же kit.
    yield lambda: verify_maclaurin('t', x + x**2, exp(x)*sin(x), order=2)
    yield lambda: verify_maclaurin('t', x + x**2, exp(x)*sin(x), order=3)
    yield lambda: verify_maclaurin('t', x**2, sin(x**2), terms=2)
    yield lambda: verify_maclaurin('t', exp(x)*sin(x), exp(x)*sin(x), order=2)
    yield lambda: verify_maclaurin('t', 1 - n*x**2/2, cos(x)**n, order=2,
                                   params={n: (2, 3)})
    yield lambda: verify_maclaurin('t', ..., exp(x)*sin(x), order=2)
    yield lambda: verify_series_solution('t', 3 - 3*x, (x**2*y - y)/(x**2 + 1), 3, 1)
    yield lambda: verify_series_solution('t', 5 - 5*x, (x**2*y - y)/(x**2 + 1), 3, 1)
    yield lambda: verify_series_solution('t', ..., (x**2*y - y)/(x**2 + 1), 3, 1)
    yield lambda: verify_terms('t', 2, 1/sp.Integer(10)**k, sp.Rational(1, 1000))
    yield lambda: verify_terms('t', 5, 1/sp.Integer(10)**k, sp.Rational(1, 1000))
    yield lambda: verify_terms('t', 0, 1/sp.Integer(10)**k, sp.Rational(1, 1000))
    yield lambda: verify_terms('t', 2, 1/sp.Integer(10)**A, sp.Rational(1, 1000))
    yield lambda: verify_terms('t', ..., 1/sp.Integer(10)**k, sp.Rational(1, 1000))
    # E3: производные.
    yield lambda: verify_derivative('t', 2*x, x**2)
    yield lambda: verify_derivative('t', x**2, x**2)
    yield lambda: verify_derivative('t', cos(2*x), sin(2*x))
    yield lambda: verify_derivative('t', 2*x**2, x**2)
    yield lambda: verify_derivative('t', 2*exp(2*x)*3, exp(2*x)*(3*x - 4))
    yield lambda: verify_derivative('t', 1/(4*(1 + x)**sp.Rational(3, 2)),
                                    sqrt(1 + x), order=2)
    yield lambda: verify_derivative('t', 2*x, x**2, params={k: (1, 2)})
    yield lambda: verify_derivative('t', 2*x, x**2, params={k: (1, 2), A: (1,)})
    yield lambda: verify_derivative('t', ..., x**2)
    yield lambda: verify_stationary('t', [(0, 1)], cos(x)**2, domain=(-1, 1))
    yield lambda: verify_stationary('t', [(0, 2)], cos(x)**2, domain=(-1, 1))
    yield lambda: verify_stationary('t', [(5, 1)], cos(x)**2, domain=(-1, 1))
    yield lambda: verify_stationary('t', [(sp.Rational(1, 2), 1)], cos(x)**2,
                                    domain=(-1, 1))
    yield lambda: verify_stationary('t', [(0, 1)], cos(x)**2, domain=(-4, 4))
    yield lambda: verify_stationary('t', [1], cos(x)**2, domain=(-1, 1))
    yield lambda: verify_stationary('t', ..., cos(x)**2, domain=(-1, 1))
    yield lambda: verify_constants('t', [1], [A], [('A is one', A - 1)])
    yield lambda: verify_constants('t', [2], [A], [('A is one', A - 1)])
    yield lambda: verify_constants('t', [1, 2], [A], [('A is one', A - 1)])
    yield lambda: verify_constants('t', [1], [A], [('A is one', Eq(A, 1))])
    yield lambda: verify_constants('t', ..., [A], [('A is one', A - 1)])

    # D2: пространство восстанавливается из условий, и каждый именной
    # промах должен называться по-английски — сообщения тут длиннее всего
    # в kit, и русское слово посреди них заметили бы только глазами
    E1_, E2_ = events('A B')
    flat = [(P(E1_), sp.Rational(3, 10)), (P(E2_), sp.Rational(4, 10)),
            (P(E1_ & E2_), sp.Rational(1, 10))]
    cond = [(P(E1_), sp.Rational(1, 2)), (P(E2_), sp.Rational(1, 3)),
            (P(E1_, given=E2_), sp.Rational(1, 4))]
    yield lambda: verify_event('t', sp.Rational(3, 5), flat, P(E1_ | E2_))
    yield lambda: verify_event('t', sp.Rational(7, 10), flat, P(E1_ | E2_))
    yield lambda: verify_event('t', sp.Rational(3, 2), flat, P(E1_ | E2_))
    yield lambda: verify_event('t', sp.Rational(1, 7), flat, P(E1_ | E2_))
    yield lambda: verify_event('t', sp.Rational(2, 5), flat, P(E1_ & E2_))
    yield lambda: verify_event('t', sp.Rational(1, 6), cond,
                               P(E1_, given=E2_))
    yield lambda: verify_event('t', sp.Rational(1, 12), cond,
                               P(E1_, given=E2_))
    yield lambda: verify_event('t', sp.Rational(1, 5), flat, P(E1_ & E2_),
                               extreme='min')
    yield lambda: verify_event('t', sp.Rational(1, 5),
                               [(P(E1_), sp.Rational(3, 10)),
                                (P(E1_), sp.Rational(4, 10))], P(E2_))
    yield lambda: verify_event('t', sp.Rational(1, 5),
                               [(P(E1_), sp.Rational(3, 10))], P(E2_))
    yield lambda: verify_event('t', ..., flat, P(E1_ | E2_))
    box = {'r': sp.Rational(9, 14), 'w': sp.Rational(5, 14)}
    yield lambda: verify_probability('t', sp.Rational(9, 14), box, ['r'])
    yield lambda: verify_probability('t', sp.Rational(5, 7), box, ['r'])
    yield lambda: verify_probability('t', sp.Rational(1, 2),
                                     {'r': sp.Rational(1, 3)}, ['r'])
    yield lambda: verify_probability('t', sp.Rational(1, 2), box, ['r'],
                                     given=['q'])
    yield lambda: verify_probability('t', sp.Rational(9, 14), box, ['r'],
                                     given=['r', 'w'])
    yield lambda: verify_probability('t', ..., box, ['r'])
    yield lambda: verify_independence('t', [sp.Rational(1, 6),
                                            sp.Rational(1, 6)], cond,
                                      E1_, E2_)
    yield lambda: verify_independence('t', [1, sp.Rational(1, 6)], cond,
                                      E1_, E2_)
    yield lambda: verify_independence('t', [sp.Rational(1, 6), 1], cond,
                                      E1_, E2_)
    yield lambda: verify_independence('t', [sp.Rational(1, 6)], cond,
                                      E1_, E2_)
    yield lambda: verify_independence('t', [sp.Rational(1, 6)],
                                      [(P(E1_), sp.Rational(3, 10)),
                                       (P(E1_), sp.Rational(4, 10))],
                                      E1_, E2_)
    yield lambda: verify_independence('t', [..., ...], cond, E1_, E2_)
    yield lambda: verify_constants('t', [2], [A], [('A is one', A - 1)],
                                   domain=sp.Interval(0, 1))
    yield lambda: verify_count('t', 125, itertools.product(range(5), repeat=3))
    yield lambda: verify_count('t', 7776, itertools.product(range(6), repeat=5),
                               keep=lambda p: p[0] != p[1])
    yield lambda: verify_count('t', 1296, itertools.product(range(6), repeat=5),
                               keep=lambda p: p[0] != p[1])
    yield lambda: verify_count('t', 60, itertools.permutations(range(5)))
    yield lambda: verify_count('t', 240, itertools.permutations(range(5)))
    yield lambda: verify_count('t', 20, itertools.permutations(range(5), 2),
                               each=6)
    yield lambda: verify_count('t', 999, itertools.permutations(range(5)))
    yield lambda: verify_count('t', sp.Rational(3, 2), 10)
    yield lambda: verify_count('t', -1, 10)
    yield lambda: verify_count('t', 1, [])
    yield lambda: verify_count('t', ..., 10)
    yield lambda: verify_count_law('t', sp.binomial(N_, 3), N_, _triples,
                                   (5, 6, 7))
    yield lambda: verify_count_law('t', N_**2, N_, _triples, (5, 6, 7))
    yield lambda: verify_count_law('t', N_ * A, N_, _triples, (5, 6))
    yield lambda: verify_count_law('t', ..., N_, _triples, (5, 6))
    yield lambda: verify_area('t', 20, *_sector)
    yield lambda: verify_area('t', 8 * sp.sin(sp.Rational(5, 2)), *_sector)
    yield lambda: verify_area('t', 20 * 180 / sp.pi, *_sector)
    yield lambda: verify_area('t', 40, *_sector)
    yield lambda: verify_area('t', 999, *_sector)
    yield lambda: verify_area('t', 4, *_segment)
    yield lambda: verify_area('t', 2 * sp.sin(2), *_segment)
    yield lambda: verify_area('t', 4 * sp.pi - 2 * (2 - sp.sin(2)), *_segment)
    yield lambda: verify_area('t', 3, arc((0, 0), 2, 0, 2))
    yield lambda: verify_area('t', A, *_sector)
    yield lambda: verify_area('t', ..., *_sector)
    yield lambda: verify_area('t', 1, seg((0, 0), (1, 0)), seg((1, 0), (0, 0)))
    yield lambda: verify_perimeter('t', 18, *_sector)
    yield lambda: verify_perimeter('t', 10, *_sector)
    yield lambda: verify_perimeter('t', 8, *_sector)
    yield lambda: verify_perimeter('t', 18 * 180 / sp.pi, *_sector)
    yield lambda: verify_length('t', 5, seg((0, 0), (3, 4)))
    yield lambda: verify_length('t', 5 * 1.9, arc((0, 0), 5, 1.9, 2 * sp.pi))
    yield lambda: verify_length('t', 10, arc((0, 0), 5, 0, 1.9))
    yield lambda: verify_length('t', 5, seg((0, 0), (1, 0)), seg((5, 5), (6, 5)))
    yield lambda: verify_volume('t', 4 * sp.pi, *cone(radius=2, height=3))
    yield lambda: verify_volume('t', 12 * sp.pi, *cone(radius=2, height=3))
    yield lambda: verify_volume('t', 3, *cone(radius=2, height=3))
    yield lambda: verify_volume('t', 14.51, *cone(radius=2, slant=4), exact=True)
    yield lambda: verify_volume('t', 1, arc((0, 0), 1, 0, 2 * sp.pi))
    yield lambda: verify_volume('t', 4 * sp.pi, *cone(radius=2, slant=...))
    yield lambda: verify_law('t', 2 * TH - 2 * sp.sin(TH), TH, _grow,
                             (0.7, 1.9))
    yield lambda: verify_law('t', 2 * TH, TH, _grow, (0.7, 1.9))
    yield lambda: verify_law('t', TH * A, TH, _grow, (0.7, 1.9))
    yield lambda: verify_law('t', ..., TH, _grow, (0.7, 1.9))
    yield lambda: verify_law('t', MM * sp.sqrt(5), MM, lambda v: _stretch(v),
                             (1, 3), measure='length', at={A: 1})
    yield lambda: verify_law('t', MM * A, MM, lambda v: _stretch(v),
                             (1, 3), measure='length', at={A: 1})
    yield lambda: verify_law('t', 2 * sp.pi, TH, _from_answer, (1.0, 2.0),
                             measure='perimeter')
    yield lambda: _blank_figure()
    _ap = progression(5, 2)
    _falling = progression(60, sp.Rational(-5, 2))
    _logs = progression(9 + sp.log(9), -4 - sp.log(3))
    _c = -MM**2 / (MM + 2)
    yield lambda: verify_term('t', 13, _ap, 5)
    yield lambda: verify_term('t', 15, _ap, 5)
    yield lambda: verify_term('t', 11, _ap, 5)
    yield lambda: verify_term('t', 45, _ap, 5)
    yield lambda: verify_term('t', 2 * N_ + 3, _ap, N_)
    yield lambda: verify_term('t', 2 * N_ + 1, _ap, N_)
    yield lambda: verify_term('t', 13, _ap, N_)
    yield lambda: verify_term('t', 5, _ap, 0)
    yield lambda: verify_term('t', 5, _ap, 2.5)
    yield lambda: verify_term('t', 5, _ap, 10 ** 6)
    yield lambda: verify_term('t', 2 * MM, _ap, 5)
    yield lambda: verify_term('t', ..., _ap, 5)
    yield lambda: verify_total('t', 45, _ap, 5)
    yield lambda: verify_total('t', 13, _ap, 5)
    yield lambda: verify_total('t', 60, _ap, 5)
    yield lambda: verify_total('t', 32, _ap, 5)
    yield lambda: verify_total('t', 90, _ap, 5)
    yield lambda: verify_total('t', 22.5, _ap, 5)
    yield lambda: verify_total('t', 999, _ap, 5)
    yield lambda: verify_total('t', -90 - 25 * sp.log(3), _logs, 10)
    yield lambda: verify_total('t', ..., _ap, 5)
    yield lambda: verify_start('t', [5, 7, 9], _ap)
    yield lambda: verify_start('t', [5, 7, 8], _ap)
    yield lambda: verify_start('t', [], _ap)
    yield lambda: verify_start('t', [5, 2 * MM], _ap)
    yield lambda: verify_start('t', [...], _ap)
    yield lambda: verify_arithmetic('t', [1, 3, 5])
    yield lambda: verify_arithmetic('t', [1, 2, 4])
    yield lambda: verify_arithmetic('t', [1, 2])
    yield lambda: verify_arithmetic('t', [MM, -_c / MM, _c], MM, (1, 3))
    yield lambda: verify_arithmetic('t', [MM, MM + 1, MM + 3], MM, (1, 3))
    yield lambda: verify_arithmetic('t', [1, ..., 5])
    yield lambda: verify_step('t', 2, [1, 3, 5])
    yield lambda: verify_step('t', -2, [1, 3, 5])
    yield lambda: verify_step('t', 4, [1, 3, 5])
    yield lambda: verify_step('t', 1, [1, 2, 4])
    yield lambda: verify_step('t', 2 * MM, [1, 3, 5])
    yield lambda: verify_step('t', -_c / MM - MM, [MM, -_c / MM, _c], MM, (1, 3))
    yield lambda: verify_step('t', MM, [MM, -_c / MM, _c], MM, (1, 3))
    yield lambda: verify_step('t', ..., [1, 3, 5])
    yield lambda: verify_peak('t', 750, _falling)
    yield lambda: verify_peak('t', 747.5, _falling)
    yield lambda: verify_peak('t', 700, _falling)
    yield lambda: verify_peak('t', 750, _falling, at=25)
    yield lambda: verify_peak('t', 750, _falling, at=26)
    yield lambda: verify_peak('t', 750, progression(1, 2))
    yield lambda: verify_peak('t', ..., _falling)

    # E4: кривая и прямая. Каждая проверка гоняется через успех, промах,
    # именной промах и незаполненный ответ — ветки сообщений у них разные.
    _para = curve(Eq(y, x**2))
    _ring = curve(x**2 + y**2 - 25)
    _blank_curve = curve(...)
    yield lambda: verify_tangent('t', 4*x - 4, _para, 2)
    yield lambda: verify_tangent('t', 4*x - 3, _para, 2)
    yield lambda: verify_tangent('t', -x/4 + sp.Rational(9, 2), _para, 2)
    yield lambda: verify_tangent('t', -4*x - 4, _para, 2)
    yield lambda: verify_tangent('t', x**2, _para, 2)
    yield lambda: verify_tangent('t', Eq(x, 2), _para, 2)
    yield lambda: verify_tangent('t', 4*x - 4, _blank_curve, 2)
    yield lambda: verify_tangent('t', ..., _para, 2)
    yield lambda: verify_normal('t', -x/4 + sp.Rational(9, 2), _para, 2)
    yield lambda: verify_normal('t', 4*x - 4, _para, 2)
    yield lambda: verify_normal('t', ..., _para, 2)
    yield lambda: verify_slope('t', -x/y, _ring, domain=(-3, 3))
    yield lambda: verify_slope('t', x/y, _ring, domain=(-3, 3))
    yield lambda: verify_slope('t', y/x, _ring, domain=(-3, 3))
    yield lambda: verify_slope('t', 4, _para, at=2)
    yield lambda: verify_slope('t', A, _para, at=2)
    yield lambda: verify_slope('t', ..., _para, at=2)
    yield lambda: verify_slope('t', 4, _blank_curve, at=2)
    yield lambda: verify_where('t', 2, _para, 4, (-5, 5))
    yield lambda: verify_where('t', (2, 4), _para, 4, (-5, 5))
    yield lambda: verify_where('t', 3, _para, 4, (-5, 5))
    yield lambda: verify_where('t', 2, _para, 4, (3, 5))
    yield lambda: verify_where('t', [2, 2], _para, 4, (-5, 5))
    yield lambda: verify_where('t', [0, 2], _ring, 0, (-6, 6))
    yield lambda: verify_where('t', ..., _para, 4, (-5, 5))
    yield lambda: verify_on('t', 4, _para, 2)
    yield lambda: verify_on('t', 5, _para, 2)
    yield lambda: verify_on('t', ..., _para, 2)
    yield lambda: verify_second('t', 2, _para, 1)
    yield lambda: verify_second('t', 3, _para, 1)
    yield lambda: verify_second('t', 2, _para, 1)
    yield lambda: verify_second('t', ..., _para, 1)
    yield lambda: verify_right_angle('t', (4, -sp.Rational(1, 4)), _para,
                                     curve(Eq(y, 4 - (x - 2)/4)), 2)
    yield lambda: verify_right_angle('t', (4, 4), _para,
                                     curve(Eq(y, 4 - (x - 2)/4)), 2)
    yield lambda: verify_right_angle('t', 4, _para,
                                     curve(Eq(y, 4 - (x - 2)/4)), 2)
    yield lambda: verify_right_angle('t', ..., _para,
                                     curve(Eq(y, 4 - (x - 2)/4)), 2)
    yield lambda: verify_constant('t', 2, lambda v: curve(Eq(y, v*x**2)), 1,
                                  4, (0.5, 8))
    yield lambda: verify_constant('t', 3, lambda v: curve(Eq(y, v*x**2)), 1,
                                  4, (0.5, 8))
    yield lambda: verify_constant('t', ..., lambda v: curve(Eq(y, v*x**2)), 1,
                                  4, (0.5, 8))
    # E5: первообразная и её семейство. У каждой проверки свои ветки —
    # именной промах, потерянный делитель замены, лишняя степень ряда.
    _n = sp.Symbol('n')
    _J = sp.Function('J')
    yield lambda: verify_antiderivative('t', x**3/3, x**2)
    yield lambda: verify_antiderivative('t', x**3/3 + C, x**2)
    yield lambda: verify_antiderivative('t', x**2, x**2)
    yield lambda: verify_antiderivative('t', 2*x, x**2)
    yield lambda: verify_antiderivative('t', x**3/3 + x, x**2)
    yield lambda: verify_antiderivative('t', sin(3*x), cos(3*x))
    yield lambda: verify_antiderivative('t', x**4, x**2)
    yield lambda: verify_antiderivative('t', k, x**2, params={k: (3,)})
    yield lambda: verify_antiderivative('t', x**3 - 1, 3*x**2, through=(0, -1))
    yield lambda: verify_antiderivative('t', x**3 + 7, 3*x**2, through=(0, -1))
    yield lambda: verify_antiderivative('t', x**3 + C, 3*x**2, through=(0, -1))
    yield lambda: verify_antiderivative('t', ..., x**2)
    yield lambda: verify_integral('t', 4, 3 - 5/sqrt(x), 1, 9)
    yield lambda: verify_integral('t', -4, 3 - 5/sqrt(x), 1, 9)
    yield lambda: verify_integral('t', 5, 3 - 5/sqrt(x), 1, 9)
    yield lambda: verify_integral('t', x, 3 - 5/sqrt(x), 1, 9)
    yield lambda: verify_integral('t', 1, 1/x, 0, 1)
    yield lambda: verify_integral('t', ..., x**2, 0, 1)
    yield lambda: verify_accumulated('t', t**2/2, t, 0)
    yield lambda: verify_accumulated('t', t**2/2 + 5, t, 0)
    yield lambda: verify_accumulated('t', t**3, t, 0)
    yield lambda: verify_accumulated('t', ..., t, 0)
    yield lambda: verify_transformed('t', u**2, cos(x)*sin(x)**2, sin(x))
    yield lambda: verify_transformed('t', u**2*cos(x), cos(x)*sin(x)**2, sin(x))
    yield lambda: verify_transformed('t', x**2, cos(x)*sin(x)**2, sin(x))
    yield lambda: verify_transformed('t', u**3, cos(x)*sin(x)**2, sin(x))
    yield lambda: verify_transformed('t', ..., cos(x)*sin(x)**2, sin(x))
    yield lambda: verify_reduction('t', cos(x)**(_n - 1)*sin(x)/_n
                                   + (_n - 1)*_J(_n - 2)/_n, cos(x)**_n, _n, _J)
    yield lambda: verify_reduction('t', cos(x)**(_n - 1)*sin(x)/_n
                                   + (_n - 1)*_J(_n - 2), cos(x)**_n, _n, _J)
    yield lambda: verify_reduction('t', ..., cos(x)**_n, _n, _J)
    yield lambda: verify_termwise('t', x - x**3/3 + x**5/5, 1/(1 + x**2), 6)
    yield lambda: verify_termwise('t', 1 - x**2 + x**4, 1/(1 + x**2), 6)
    yield lambda: verify_termwise('t', x - x**3/3 + x**5/5 + x**7/7,
                                  1/(1 + x**2), 6)
    yield lambda: verify_termwise('t', x - x**3/2, 1/(1 + x**2), 6)
    yield lambda: verify_termwise('t', ..., 1/(1 + x**2), 6)
    # E6: измеренное и его измерение. Каждая ветка каждой проверки —
    # включая именованные промахи, которыми раздел и полезен.
    yield lambda: verify_region('t', 12*pi, 6 + 6*cos(x), 0, pi, 3*pi)
    yield lambda: verify_region("t", sp.Rational(9, 2), -x**2 + 9, -3*x + 9)
    yield lambda: verify_region('t', 0, sin(x), 0, 0, 2*pi)
    yield lambda: verify_region('t', -sp.Rational(9, 2), -3*x + 9, -x**2 + 9, 0, 3)
    yield lambda: verify_region('t', sp.Rational(9, 4), -x**2 + 9, -3*x + 9, 0, 3)
    yield lambda: verify_region('t', 9, -x**2 + 9, -3*x + 9, 0, 3)
    yield lambda: verify_region('t', 5, -x**2 + 9, -3*x + 9, 0, 3)
    yield lambda: verify_region('t', x, -x**2 + 9, -3*x + 9, 0, 3)
    yield lambda: verify_region('t', 1, x**2 + 1, 0)
    yield lambda: verify_region('t', 1, log(x), 0, -2, -1)
    yield lambda: verify_region('t', 1, x, 0, 0, 1, params={k: (1, 2, 3)})
    yield lambda: verify_region('t', ..., x, 0, 0, 1)
    yield lambda: verify_solid('t', pi/3, x, 0, 1)
    yield lambda: verify_solid('t', sp.Rational(1, 3), x, 0, 1)
    yield lambda: verify_solid('t', pi/2, x, 0, 1)
    yield lambda: verify_solid('t', sp.Rational(1, 2), x, 0, 1)
    yield lambda: verify_solid('t', pi, 2*y, 0, 1, inner=y, var=y, axis='y')
    yield lambda: verify_solid('t', pi/3, 2*y, 0, 1, inner=y, var=y, axis='y')
    yield lambda: verify_solid('t', 7, x, 0, 1)
    yield lambda: verify_solid('t', 1, log(x), -2, -1)
    yield lambda: verify_solid('t', 1, x, 0, 1, params={k: (1, 2, 3)})
    yield lambda: verify_solid('t', ..., x, 0, 1)
    yield lambda: verify_surface('t', 18*sqrt(5)*pi, 2*x, 0, 3)
    yield lambda: verify_surface('t', 9*sqrt(5)*pi, 2*x, 0, 3)
    yield lambda: verify_surface('t', 36*sqrt(5)*pi, 2*x, 0, 3)
    yield lambda: verify_surface('t', 3*sqrt(5), 2*x, 0, 3)
    yield lambda: verify_surface('t', 7, 2*x, 0, 3)
    yield lambda: verify_surface('t', 1, log(x), -2, -1)
    yield lambda: verify_surface('t', 1, 2*x, 0, 3, params={k: (1, 2, 3)})
    yield lambda: verify_surface('t', ..., 2*x, 0, 3)
    yield lambda: verify_travelled('t', 13, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_travelled('t', 3, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_travelled('t', -3, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_travelled('t', -13, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_travelled('t', 7, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_travelled('t', 1, log(t), -2, -1)
    yield lambda: verify_travelled('t', 1, t, 0, 1, params={k: (1, 2, 3)})
    yield lambda: verify_travelled('t', ..., t, 0, 1)
    yield lambda: verify_position('t', 3, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_position('t', 13, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_position('t', 103, 4 + 4*t - 3*t**2, 0, 3, start=100)
    yield lambda: verify_position('t', 3, 4 + 4*t - 3*t**2, 0, 3, start=100)
    yield lambda: verify_position('t', -3, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_position('t', 7, 4 + 4*t - 3*t**2, 0, 3)
    yield lambda: verify_position('t', 1, log(t), -2, -1)
    yield lambda: verify_position('t', 1, t, 0, 1, start=x)
    yield lambda: verify_position('t', 1, t, 0, 1, params={k: (1, 2, 3)})
    yield lambda: verify_position('t', ..., t, 0, 1)
    yield lambda: verify_amount('t', sp.Rational(1, 2), t, 0, 1)
    yield lambda: verify_amount('t', 100 + t**2/2, t, 0, 4, start=100)
    yield lambda: verify_amount('t', t**2/2, t, 0, 4, start=100)
    yield lambda: verify_amount('t', 7, t, 0, 1)
    yield lambda: verify_amount('t', 1, t, 0)
    yield lambda: verify_amount('t', 1, log(t), -2, -1)
    yield lambda: verify_amount('t', 1, t, 0, 1, start=x)
    yield lambda: verify_amount('t', 1, t, 0, 1, params={k: (1, 2, 3)})
    yield lambda: verify_amount('t', ..., t, 0, 1)
    yield lambda: trigger_check({1: 'a'}, {1: digest('a')})
    yield lambda: trigger_check({1: 'b'}, {1: digest('a')})
    yield lambda: trigger_check({1: ''}, {1: digest('a')})
    # биномиальное распределение, D3: все ветки разбора — граница, cdf вместо
    # pdf, условная, «ровно один из двух», внешняя модель, среднее, n
    lamps, wheat = Bin(30, 0.05), Bin(100, 0.434)
    apples = Bin(40, 0.628364)
    yield lambda: verify_binomial('t', 0.785, P(lamps >= 1))
    yield lambda: verify_binomial('t', 0.215, P(lamps >= 1))
    yield lambda: verify_binomial('t', 0.0327, P(Bin(31, 0.2) >= 10))
    yield lambda: verify_binomial('t', 0.967, P(Bin(31, 0.2) == 10))
    yield lambda: verify_binomial('t', 0.304, P(Bin(64, 0.071193) > 6))
    yield lambda: verify_binomial('t', 0.0150, P(wheat == 34, given=wheat < 49))
    yield lambda: verify_binomial('t', 0.598, P(lamps <= 2, given=lamps >= 1))
    yield lambda: verify_binomial('t', 0.0849, P(Bin(10, 0.0849303) == 1))
    yield lambda: verify_binomial('t', 0.0863, P(Bin(10, P(apples >= 30)) == 4))
    yield lambda: verify_binomial('t', 0.00395134, P(Bin(10, P(apples >= 30)) == 4))
    yield lambda: verify_binomial('t', 0.660, P((Bin(5, 0.12, 'R') >= 1) ^ (Bin(5, 0.08, 'S') >= 1)))
    yield lambda: verify_binomial('t', 0.042, P(Bin(31, 0.2) == 10))
    yield lambda: verify_binomial('t', 1.2, P(lamps >= 1))
    yield lambda: verify_binomial('t', 0.5, 0.5)
    yield lambda: verify_binomial('t', ..., P(lamps >= 1))
    yield lambda: verify_moment('t', 5, Expect(Bin(64, 0.071193)))
    yield lambda: verify_moment('t', 59.4, Expect(Bin(64, 0.071193)))
    yield lambda: verify_moment('t', 11.5, Var(1 - 2 * Bin(25, sp.Symbol('p'))),
                                given=Eq(Var(Bin(25, sp.Symbol('p'))), 5.75), var=sp.Symbol('p'))
    yield lambda: verify_moment('t', -1, Var(Bin(10, 0.3)))
    yield lambda: verify_parameter('t', [0.641], Eq(Var(Bin(25, sp.Symbol('p'))), 5.75), sp.Symbol('p'))
    yield lambda: verify_parameter('t', [0.3], Eq(Var(Bin(25, sp.Symbol('p'))), 5.75), sp.Symbol('p'))
    yield lambda: verify_trials('t', 16, lambda n: P(Bin(n, 0.25) >= 1), holds=lambda v: v > 0.99)
    yield lambda: verify_trials('t', 18, lambda n: P(Bin(n, 0.25) >= 1), holds=lambda v: v > 0.99)
    yield lambda: verify_trials('t', 16.0078, lambda n: P(Bin(n, 0.25) >= 1), holds=lambda v: v > 0.99)
    yield lambda: verify_trials('t', 93, lambda n: P(Bin(n, 0.08) <= 6), near=0.367)
    # таблица распределения, D4: отброшенный корень, диапазон, мода, среднее
    # без весов, E(X²), линейное преобразование, ряд, производящая функция
    ka, pa, qa, ra = sp.symbols('k p q r')
    tab = Dist({0: 0.41, 1: ka - 0.28, 2: 0.46, 3: 0.29 - 2 * ka ** 2})
    die = Dist({1: qa, 2: qa, 3: qa, 4: ra}, 'Y')
    three = Dist({1: 0.6 - 2 * ka, 2: 3 * ka, 3: 0.4 - ka})
    pos = sp.symbols('m', positive=True, integer=True)
    marks = Freq({20: 12, 35: pos, 40: 8})
    geo = Geo(pa)
    runner = Moments(4.723, 0.906)
    coin = Dist(Dist({0: Rational(1, 2), 1: Rational(1, 2)}) + Dist({0: 1 - pa, 1: pa}), 'Y')
    reds = Dist({0: Rational(3, 10), 1: Rational(3, 5), 2: Rational(1, 10)}, 'X')
    yield lambda: verify_letters('t', 0.3, ka, [tab])
    yield lambda: verify_letters('t', 0.2, ka, [tab])
    yield lambda: verify_letters('t', 0.5, ka, [tab])
    yield lambda: verify_letters('t', 0.55, sp.Symbol('a'), [Dist({1: 0.45, 2: sp.Symbol('a')})])
    yield lambda: verify_letters('t', [1, 2], [ka], [tab])
    yield lambda: verify_letters('t', x, ka, [tab])
    yield lambda: verify_letters('t', [-4], [pos], [marks], [Eq(Expect(marks), 30)])
    yield lambda: verify_letters('t', [195.4, 20.2], sp.symbols('a b'), [runner],
                                 [Eq(Expect(sp.Symbol('a') - sp.Symbol('b') * runner), 100),
                                  Eq(sp.Symbol('a') - 2.25 * sp.Symbol('b'), 150)], whole=True)
    yield lambda: verify_letters('t', 1, ka, [Dist({1: ka, 2: ka})], [Eq(Expect(Dist({1: ka, 2: ka})), 5)])
    yield lambda: verify_letters('t', ..., ka, [tab])
    yield lambda: verify_table_range('t', Interval(0, 1), qa, [die])
    yield lambda: verify_table_range('t', Interval.open(0, Rational(1, 3)), qa, [die])
    yield lambda: verify_table_range('t', Interval(0, 0.4), ka, [three])
    yield lambda: verify_table_range('t', Interval(3, 4), Expect(die), [die])
    yield lambda: verify_table_range('t', Interval(2, 3), Expect(die), [die])
    yield lambda: verify_table_range('t', 5, qa, [die])
    yield lambda: verify_table_range('t', Interval(0, 1), qa, [Dist({1: 0.5, 2: 0.5})])
    yield lambda: verify_mode('t', 0.46, tab, given=[], var=ka)
    yield lambda: verify_mode('t', 0, tab, given=[], var=ka)
    yield lambda: verify_moment('t', 1.5, Expect(tab), given=[], var=ka)
    yield lambda: verify_moment('t', 4.4, Var(2 - three), given=Eq(ka, 0.2), var=ka)
    yield lambda: verify_moment('t', 4.0, Var(2 - three), given=Eq(ka, 0.2), var=ka)
    yield lambda: verify_moment('t', 3, Expect(10 * three), given=Eq(ka, 0.2), var=ka)
    yield lambda: verify_moment('t', 1, Expect(three), given=Eq(ka, 5), var=ka)
    yield lambda: verify_moment('t', 3.80, Var(geo), given=Eq(Expect(geo), 2.5104), var=pa)
    yield lambda: verify_moment('t', Sum(pa * (1 - pa) ** (x - 1), (x, 1, oo)), Expect(geo))
    yield lambda: verify_moment('t', 1 / pa ** 2, Expect(geo))
    yield lambda: verify_moment('t', x, Expect(geo))
    yield lambda: verify_pgf('t', Rational(1, 10) + Rational(3, 5) * t + Rational(3, 10) * t ** 2, reds, t)
    yield lambda: verify_pgf('t', Rational(3, 10) * t + Rational(3, 5) * t ** 2 + Rational(1, 10) * t ** 3, reds, t)
    yield lambda: verify_pgf('t', Rational(3, 10) + t, reds, t)
    yield lambda: verify_pgf('t', Rational(3, 10) + Rational(1, 2) * t + Rational(1, 5) * t ** 2, reds, t)
    yield lambda: verify_pgf('t', pa * t, reds, t)
    yield lambda: verify_pgf('t', sin(t), reds, t)
    yield lambda: verify_pgf('t', Rational(1, 6) + t / 2 + t ** 2 / 3, coin, t,
                             given=Eq(P(coin == 2), Rational(1, 4)), unknowns=pa)
    yield lambda: verify_chance('t', 0.45, P(Freq({0: 6, 1: 16, 2: 18}) >= 1))
    yield lambda: verify_chance('t', 0.2, P(Dist({1: 0.5, 2: 0.5}, 'X') < Dist({1: 0.5, 2: 0.5}, 'Z')))
    # нормальное распределение, D5: площадь, её промахи, буквы модели,
    # значащие цифры, проценты, правило из условия, смесь, событие через Z
    bags = Normal(1000, 3.5 ** 2)
    sd_, mu_, bound_, rest_ = sp.symbols('s m w a')
    flights = Normal(75, sd_ ** 2, 'T')
    two_pct = [Eq(P(flights > 82), 0.02)]
    rice = Normal(204, 25, 'W')
    ruled = Normal(100, 400, 'E', rule={2: 0.95})
    choc, banana = Normal(62, 2.9 ** 2, 'C'), Normal(68, 3.4 ** 2, 'B')
    muffins = Mix({choc: 0.6, banana: 0.4}, 'muffin')
    std = Normal(0, 1, 'Z')
    left = std.map(lambda z: -z - sqrt(z ** 2 - 1), 'X1')
    right = std.map(lambda z: -z + sqrt(z ** 2 - 1), 'X2')
    free_x, free_y = Normal(7, rest_ ** 2, 'X'), Normal(19, rest_ ** 2, 'Y')
    yield lambda: verify_chance('t', 0.0766, P(bags < 995))
    yield lambda: verify_chance('t', 0.923, P(bags < 995))
    yield lambda: verify_chance('t', 0.077, P(bags < 995))
    yield lambda: verify_chance('t', 7.66, P(bags < 995))
    yield lambda: verify_chance('t', 0.3, P(bags < 995))
    yield lambda: verify_chance('t', 1.4, P(bags < 995))
    yield lambda: verify_chance('t', 0.114, P(bags < 995))
    yield lambda: verify_chance('t', 0.0766, P(bags > 1005, given=bags >= 995))
    yield lambda: verify_chance('t', 0.0829, P(bags > 1005, given=bags >= 995))
    yield lambda: verify_chance('t', 0.0712, P(flights > 80), given=two_pct, var=sd_)
    yield lambda: verify_chance('t', 0.628, P((rice > 170) & (rice < 185)), percent=True)
    yield lambda: verify_chance('t', 11.5, P(rice > 210), percent=True)
    yield lambda: verify_chance('t', 250, P(rice > 210), percent=True)
    yield lambda: verify_chance('t', 0.6827, P((free_x > 7 - rest_) & (free_x < 7 + rest_)), sf=2, free=rest_)
    yield lambda: verify_chance('t', 5, P(ruled > 140), percent=True)
    yield lambda: verify_chance('t', 2.28, P(ruled > 140), percent=True)
    yield lambda: verify_chance('t', 0.365, P(muffins < 61))
    yield lambda: verify_chance('t', 0.965, P(muffins.came_from(choc), given=muffins < 61))
    yield lambda: verify_chance('t', 0.0530, P((left > 0.5) & (right > 0.5), given=left < right))
    yield lambda: verify_chance('t', ..., P(bags < 995))
    yield lambda: verify_chance('t', x, P(bags < 995))
    yield lambda: verify_letters('t', 3.41, sd_, [flights], two_pct)
    yield lambda: verify_letters('t', -3.41, sd_, [flights], two_pct)
    yield lambda: verify_letters('t', 3.8, sd_, [flights], two_pct)
    yield lambda: verify_letters('t', 181.73, bound_, [Normal(175, 64, 'W')],
                                 [Eq(P(Normal(175, 64, 'W') > bound_), 0.2)], sf=4)
    yield lambda: verify_letters('t', 168.3, bound_, [Normal(175, 64, 'W')],
                                 [Eq(P(Normal(175, 64, 'W') > bound_), 0.2)], sf=4)
    yield lambda: verify_letters('t', 4, bound_, [free_x, free_y],
                                 [Eq(P(free_x > bound_), P(free_y > 22))], free=rest_)
    yield lambda: verify_letters('t', [97.3, 4.82], [mu_, sd_], [Normal(mu_, sd_ ** 2, 'H')],
                                 [Eq(P(Normal(mu_, sd_ ** 2, 'H') < 94.6), 0.288)])
    yield lambda: verify_moment('t', 6.28, SD(Freq({Interval.Lopen(15, 20): 31, Interval.Lopen(20, 25): 42})))
    yield lambda: verify_moment('t', 8, Expect(Bin(100, P(bags < 995))), count=True)
    # плотность, D6: площадь, константа, медиана и её промахи, мода,
    # что больше, моменты, точное значение, до цента, событие через цену
    kk, aa, bb, cc, mm = sp.Symbol('k', positive=True), *sp.symbols('a b c m')
    cube = Density({(0, 2): 3 * x ** 2 / 8}, 'X')
    arcd = Density({(0, 1): kk / sqrt(4 - 3 * x ** 2)}, 'K')
    wrong = Density({(0, 2): cc - x}, 'L')
    choco = Density({(Rational(1, 2), 3): Rational(6, 85) * (4 + 3 * x - x ** 2)}, 'C')
    steps = Density({(0, 1): x / 2, (1, Rational(5, 2)): Rational(1, 2)}, 'S')
    hump = Density({(0, 1): 12 * x ** 2 * (1 - x)}, 'H')
    uni = Density({(aa, 3 * aa): 1 / (2 * aa)}, 'U')
    shift = Density({(0, bb): aa * x * exp(x)}, 'A')
    cost = choco.map(lambda w: Piecewise((25 * w, w < 0.75), (24 * w, True)), 'spend')
    yield lambda: verify_chance('t', 0.422, P(cube < 1.5))
    yield lambda: verify_chance('t', 0.578, P(cube < 1.5))
    yield lambda: verify_chance('t', 0.844, P(cube < 1.5))
    yield lambda: verify_chance('t', 0.635, P(cost <= 48))
    yield lambda: verify_chance('t', 7 * kk ** 3 / 6, total_probability(arcd), free=kk)
    yield lambda: verify_letters('t', 3 * sqrt(3) / pi, kk, [arcd], exact=True)
    yield lambda: verify_letters('t', 1.65, kk, [arcd], exact=True)
    yield lambda: verify_letters('t', 1.8, kk, [arcd])
    yield lambda: verify_letters('t', 1.5, cc, [wrong])
    yield lambda: verify_letters('t', 1 / (bb * exp(bb) - exp(bb)), aa, [shift], free=bb)
    yield lambda: verify_letters('t', 1.82, mm, [cube], [Eq(P(cube < mm), 0.25)])
    yield lambda: verify_letters('t', 1.31, mm, [choco], [Eq(P(choco < mm), 0.5)])
    yield lambda: verify_letters('t', 5.73, mm, [choco], [Eq(P(choco < mm), 0.5)])
    yield lambda: verify_letters('t', 1.41, mm, [steps], [Eq(P(steps < mm), 0.5)])
    yield lambda: verify_letters('t', 1.5, mm, [cube], [Eq(P(cube < mm), 0.5)])
    yield lambda: verify_mode('t', Rational(2, 3), hump)
    yield lambda: verify_mode('t', Rational(16, 9), hump)
    yield lambda: verify_mode('t', 0.614, hump)
    yield lambda: verify_mode('t', 0.2, hump)
    yield lambda: verify_greater('t', 'median', hump)
    yield lambda: verify_greater('t', 'mean', hump)
    yield lambda: verify_moment('t', 2.4, Var(cube))
    yield lambda: verify_moment('t', 2, Expect(cube))
    yield lambda: verify_moment('t', 1, Expect(cube))
    yield lambda: verify_moment('t', 13 * aa ** 2 / 3, Var(uni))
    yield lambda: verify_moment('t', 1.5, Expect(cube), exact=True)
    yield lambda: verify_moment('t', 41.0, Expect(cost), places=2)
    # векторы, C5: прямая как множество точек, условия, углы, движение
    vA, vB, vC = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4)
    vD, vq, vr = unknown('D', 3), unknown('q', 2), unknown('r')
    cart = cartesian((x + 1) / 2, y, 3 - z)
    ll1 = line(vec(1, -2, 0) + lam * vec(2, 3, 1))
    ll2 = line(vec(0, 4, -8) + t * vec(1, 0, 2))
    par1, par2 = line(vec(3, 2, -1) + lam * vec(2, -2, 2)), line(vec(2, 0, 4) + mu * vec(1, -1, 1))
    sk1, sk2 = line(vec(-1, 1, -13) + lam * vec(7, 1, 2)), line(vec(2, -4, 2) + mu * vec(5, -2, -1))
    aa_ = sp.Symbol('a')
    fam = line(vec(0, 1, 2) + t * vec(aa_, 1, -1), t)
    theta_ = sp.Symbol('theta')
    circle = 15 * vec(cos(theta_), sin(theta_))
    flight = vec(19, -1, 1) + t * vec(-6, 2, 4)
    yield lambda: verify_find('t', (3, 0, 2), vD, [parallelogram(vA, vB, vC, vD)])
    yield lambda: verify_find('t', (-1, -8, -2), vD, [parallelogram(vA, vB, vC, vD)])
    yield lambda: verify_find('t', ..., vD, [parallelogram(vA, vB, vC, vD)])
    yield lambda: verify_find('t', (-2, -5, 1), vD, [midpoint(vD, vA, vB)])
    yield lambda: verify_find('t', (0, 0, 0), vD, [on(vD, vA, vC)])
    yield lambda: verify_find('t', 6, vr, [Eq(2 * vr, distance(vA, vB))])
    yield lambda: verify_find('t', (5, 12), vq, [perpendicular(vq, vec(12, -5)), length(vq, 15), vq[0] > 0])
    yield lambda: verify_find('t', (-75 / 13, -180 / 13), vq, [perpendicular(vq, vec(12, -5)), length(vq, 15), vq[0] > 0])
    yield lambda: verify_find('t', (1, 1), vq, [perpendicular(vq, vec(12, -5))])
    yield lambda: verify_find('t', 5, k, [parallel(vec(k, -2, 1) - vec(1, 2, 3), vec(4, -2, -1))])
    yield lambda: verify_find('t', (-3, -4, 9), distance(vec(6, 8, 0), vec(3, 4, 9)))
    yield lambda: verify_find('t', 106, distance(vec(6, 8, 0), vec(3, 4, 9)))
    yield lambda: verify_find('t', 10.2, distance(vec(6, 8, 0), vec(3, 4, 9)))
    yield lambda: verify_find('t', (1, 4), vec(3, 4) - vec(2, 0))
    yield lambda: verify_find('t', vec(3, 4), dot(vec(3, 4), vec(1, 1)))
    yield lambda: verify_find('t', 2, sp.Integer(1))
    yield lambda: verify_find('t', 30, Abs(unknown('s') - 1), [Eq(unknown('w'), 0)])
    yield lambda: verify_find('t', -4 + 3 * sqrt(2), aa_, [Eq(angle(cart, fam), pi / 4)], exact=True)
    yield lambda: verify_find('t', [0.243, -8.24], aa_, [Eq(angle(cart, fam), pi / 4)], exact=True)
    yield lambda: verify_find('t', -2, aa_, [no_unique_meet(cart, fam)])
    yield lambda: verify_find('t', [Rational(3, 2), 14], [aa_, sp.Symbol('b')],
                              [perpendicular(line(vec(4, 0, -1) + lam * vec(0, aa_, 1), lam),
                                             line(vec(1, 0, -sp.Symbol('b')) + mu * vec(1, 2, 3), mu)),
                               meet(line(vec(4, 0, -1) + lam * vec(0, aa_, 1), lam),
                                    line(vec(1, 0, -sp.Symbol('b')) + mu * vec(1, 2, 3), mu))])
    yield lambda: verify_find('t', 3, sp.Symbol('b'), [meet(line(vec(4, 0, -1) + lam * vec(0, -1, 1), lam),
                                                              line(vec(1, 0, -sp.Symbol('b')) + mu * vec(1, 2, 3), mu))])
    yield lambda: verify_find('t', (x, y), vec(1, 2))
    yield lambda: verify_find('t', 1, vr, [Eq(vr, vr)])
    yield lambda: verify_line('t', vec(-1, 0, 3) + lam * vec(2, 1, -1), cart)
    yield lambda: verify_line('t', vec(-1, 0, 3) + lam * vec(2, 1, 1), cart)
    yield lambda: verify_line('t', vec(1, 0, -3) + lam * vec(2, 1, -1), cart)
    yield lambda: verify_line('t', vec(3, 1, 2) + lam * vec(-1, 0, 3), cart)
    yield lambda: verify_line('t', vec(-1, 0, 3) + lam * vec(1, 1, 2), cart)
    yield lambda: verify_line('t', vec(0, 0, 0) + lam * vec(1, 1, 2), cart)
    yield lambda: verify_line('t', vec(2, -4, 2) + lam * vec(7, -6, 1), through(vec(2, -4, 2), vec(7, -6, 1)))
    yield lambda: verify_line('t', vec(-1, 0, 3), cart)
    yield lambda: verify_line('t', vec(-1, 0) + lam * vec(2, 1), cart)
    yield lambda: verify_line('t', vec(-1, 0, 3) + lam * vec(0, 0, 0), cart)
    yield lambda: verify_line('t', ..., cart)
    yield lambda: verify_meet('t', (5, 4, 2), ll1, ll2)
    yield lambda: verify_meet('t', (2, 4, -4), ll1, ll2)
    yield lambda: verify_meet('t', (3, 1, 1), ll1, ll2)
    yield lambda: verify_meet('t', (1, 4, -6), ll1, ll2)
    yield lambda: verify_meet('t', (9, 9, 9), ll1, ll2)
    yield lambda: verify_meet('t', (2, 5), ll1, ll2)
    yield lambda: verify_meet('t', (2, 5, 1, 1), ll1, ll2)
    yield lambda: verify_meet('t', 7, ll1, ll2)
    yield lambda: verify_meet('t', (1, 1, 1), par1, par2)
    yield lambda: verify_meet('t', ..., ll1, ll2)
    yield lambda: verify_relation('t', 'parallel', par1, par2)
    yield lambda: verify_relation('t', 'skew', par1, par2)
    yield lambda: verify_relation('t', 'same', par1, par2)
    yield lambda: verify_relation('t', 'parallel', sk1, sk2)
    yield lambda: verify_relation('t', 'intersecting', sk1, sk2)
    yield lambda: verify_relation('t', 'skew', ll1, ll2)
    yield lambda: verify_relation('t', 'parallel', ll1, line(vec(5, 4, 2) + mu * vec(4, 6, 2)))
    yield lambda: verify_relation('t', 'nonsense', ll1, ll2)
    yield lambda: verify_relation('t', ..., ll1, ll2)
    yield lambda: verify_pair('t', [-1, -2], sk1, sk2)
    yield lambda: verify_pair('t', [2, 5], ll1, ll2)
    yield lambda: verify_pair('t', [-1, 2], sk1, sk2)
    yield lambda: verify_pair('t', 3, sk1, sk2)
    yield lambda: verify_pair('t', [1, 1], vec(1, 2, 3), sk2)
    yield lambda: verify_pair('t', [...], sk1, sk2)
    yield lambda: verify_line_parameter('t', 3, line(vec(1, 8, -2) + mu * vec(-4, -1, 3)), vec(-11, 5, 7))
    yield lambda: verify_line_parameter('t', -3, line(vec(1, 8, -2) + mu * vec(-4, -1, 3)), vec(-11, 5, 7))
    yield lambda: verify_line_parameter('t', 1, line(vec(1, 8, -2) + mu * vec(-4, -1, 3)), vec(-11, 5, 7))
    yield lambda: verify_line_parameter('t', 1, line(vec(1, 8, -2) + mu * vec(-4, -1, 3)), vec(0, 0, 0))
    yield lambda: verify_line_parameter('t', x, line(vec(1, 8, -2) + mu * vec(-4, -1, 3)), vec(-11, 5, 7))
    yield lambda: verify_angle('t', 0.798, vec(6, 8, 0), vec(3, 4, 9), vec(6, 0, 0))
    yield lambda: verify_angle('t', 0.927, vec(6, 8, 0), vec(3, 4, 9), vec(6, 0, 0))
    yield lambda: verify_angle('t', 1.17, vec(6, 8, 0), vec(3, 4, 9), vec(6, 0, 0))
    yield lambda: verify_angle('t', 0.8, vec(6, 8, 0), vec(3, 4, 9), vec(6, 0, 0))
    yield lambda: verify_angle('t', 139.8, par1, sk1, deg=True)
    yield lambda: verify_angle('t', 40.2, line(flight, t), line(vec(1, 0, 12) + t * vec(4, 2, -2), t), deg=True)
    yield lambda: verify_angle('t', 139.8, line(flight, t), line(vec(1, 0, 12) + t * vec(4, 2, -2), t), deg=True)
    yield lambda: verify_angle('t', 0.702, line(flight, t), line(vec(1, 0, 12) + t * vec(4, 2, -2), t), deg=True)
    yield lambda: verify_angle('t', 40.2, line(flight, t), line(vec(1, 0, 12) + t * vec(4, 2, -2), t), deg=False)
    yield lambda: verify_angle('t', 2.36, vec(1, 0), vec(-1, 1))
    yield lambda: verify_angle('t', -0.707, vec(1, 0), vec(-1, 1))
    yield lambda: verify_angle('t', 0, vec(0, 0, 6), vec(0, 6, 0))
    yield lambda: verify_angle('t', 81.6, vec(40, -100, -16), 'horizontal', deg=True)
    yield lambda: verify_angle('t', 0.147, vec(40, -100, -16), 'horizontal', deg=True)
    yield lambda: verify_angle('t', 1, vec(1, 1), vec(1, 0), cosine=True)
    yield lambda: verify_angle('t', 1 / sqrt(2), vec(1, 1), vec(1, 0), cosine=True, exact=True)
    yield lambda: verify_angle('t', 0.707, vec(1, 1), vec(1, 0), cosine=True, exact=True)
    yield lambda: verify_angle('t', 1 / sqrt(2), vec(2, 2), vec(1, 0), cosine=True)
    yield lambda: verify_angle('t', -1 / sqrt(2), par1, line(vec(0, 0, 0) + lam * vec(1, 0, 0)), cosine=True)
    yield lambda: verify_angle('t', 0.5, vec(1, 1), vec(1, 0), cosine=True)
    yield lambda: verify_angle('t', 0.785, vec(1, 1), vec(1, 0), exact=True)
    yield lambda: verify_angle('t', vec(1, 1), vec(1, 1), vec(1, 0))
    yield lambda: verify_angle('t', ..., vec(1, 1), vec(1, 0))
    yield lambda: verify_bearing('t', '063', vec(4, 2, -2))
    yield lambda: verify_bearing('t', '063.4', vec(4, 2, -2))
    yield lambda: verify_bearing('t', '027', vec(4, 2, -2))
    yield lambda: verify_bearing('t', '243', vec(4, 2, -2))
    yield lambda: verify_bearing('t', '297', vec(4, 2, -2))
    yield lambda: verify_bearing('t', '100', vec(4, 2, -2))
    yield lambda: verify_bearing('t', 'north', vec(4, 2, -2))
    yield lambda: verify_bearing('t', ..., vec(4, 2, -2))
    yield lambda: verify_speed('t', sqrt(56), flight)
    yield lambda: verify_speed('t', 19.1, flight)
    yield lambda: verify_speed('t', 26.9, vec(10, 3, 0.5) + 4 * t * vec(10, -25, 0))
    yield lambda: verify_speed('t', 56, flight)
    yield lambda: verify_speed('t', 7.48, flight, exact=True)
    yield lambda: verify_speed('t', 3, flight)
    yield lambda: verify_speed('t', ..., flight)
    yield lambda: verify_extent('t', Interval(2, 28), mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_extent('t', Interval(13, 28), mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_extent('t', Interval(2, 30), mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_extent('t', Interval.open(2, 28), mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_extent('t', 28, mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_extent('t', ..., mag(vec(12, -5) + circle), theta_, Interval(0, 2 * pi))
    yield lambda: verify_optimum('t', (-24 / 13, 10 / 13), vec(12, -5) + circle, theta_, Interval(0, 2 * pi))
    yield lambda: verify_optimum('t', (-180 / 13, 75 / 13), vec(12, -5) + circle, theta_, Interval(0, 2 * pi))
    yield lambda: verify_optimum('t', (24 / 13, -10 / 13), vec(12, -5) + circle, theta_, Interval(0, 2 * pi))
    yield lambda: verify_optimum('t', 2, vec(12, -5) + circle, theta_, Interval(0, 2 * pi))
    yield lambda: verify_optimum('t', (27, -10), vec(12, -5) + circle, theta_, Interval(0, 2 * pi), 'max')
    yield lambda: verify_optimum('t', ..., vec(12, -5) + circle, theta_, Interval(0, 2 * pi))
    # плоскости, C6: плоскость и система как множества, основание, отражение
    pl1, pl2 = plane(Eq(2 * x - y + z, 4)), plane(Eq(x - 2 * y + 3 * z, 5))
    pl3 = plane(Eq(-9 * x + 3 * y - 2 * z, 32))
    tri = plane(vec(3, 0, 0), vec(0, -2, 0), vec(1, 1, -7))
    wall = plane(Eq(2 * y - z, 7))
    ray = line(vec(0, -2, 0) + lam * vec(1, 1, -1))
    mirror_plane = plane(Eq(2 * x - 2 * z, 3), name='Π3')
    kk_, bb_, dd_ = sp.symbols('k b d')
    fam_plane = plane(Eq((kk_ ** 2 - 6) * x + (2 * kk_ + 3) * y - 6 * z, sp.Symbol('q')))
    tilted = plane(vec(1, 2, 3), vec(kk_, -2, 1), vec(5, 0, 2))
    cX, im = unknown('C', 3), unknown('image', 3)
    yield lambda: print(cross(vec(1, 2, 0), vec(0, 1, 3)), tri, intersection(pl1, pl2))
    yield lambda: verify_plane('t', Eq(2 * x - 3 * y - z, 6), tri)
    yield lambda: verify_plane('t', Eq(14 * x + 21 * y - 7 * z, 42), tri)
    yield lambda: verify_plane('t', Eq(2 * x - 3 * y - z, -6), tri)
    yield lambda: verify_plane('t', Eq(2 * x - 3 * y - z, 5), tri)
    yield lambda: verify_plane('t', Eq(3 * x + 2 * y, 0), tri)
    yield lambda: verify_plane('t', Eq(x, 1), tri)
    yield lambda: verify_plane('t', vec(3, 0, 0) + lam * vec(-3, -2, 0) + mu * vec(-2, 1, -7), tri)
    yield lambda: verify_plane('t', vec(3, 0, 0) + lam * vec(-3, -2, 0) + mu * vec(-6, -4, 0), tri)
    yield lambda: verify_plane('t', vec(9, 0, 0) + lam * vec(-3, -2, 0) + mu * vec(-2, 1, -7), tri)
    yield lambda: verify_plane('t', vec(3, 0, 0) + lam * vec(-3, -2, 1) + mu * vec(-2, 1, -7), tri)
    yield lambda: verify_plane('t', 2 * x - 3 * y - z, tri)
    yield lambda: verify_plane('t', Eq(x ** 2, 1), tri)
    yield lambda: verify_plane('t', Eq(y, 1), tri)
    yield lambda: verify_plane('t', Eq(y - 2 * z, 4), tilted)
    yield lambda: verify_plane('t', 'plane', tri)
    yield lambda: verify_plane('t', ..., tri)
    yield lambda: verify_normal_vector('t', vec(2, -3, -1), tri)
    yield lambda: verify_normal_vector('t', vec(2, 3, -1), tri)
    yield lambda: verify_normal_vector('t', vec(2, -3, 1), tri)
    yield lambda: verify_normal_vector('t', vec(-3, -2, 0), tri)
    yield lambda: verify_normal_vector('t', vec(3, 0, 0), tri)
    yield lambda: verify_normal_vector('t', vec(1, 1, 1), tri)
    yield lambda: verify_normal_vector('t', vec(0, 0, 0), tri)
    yield lambda: verify_normal_vector('t', 5, tri)
    yield lambda: verify_normal_vector('t', ..., tri)
    yield lambda: verify_direction('t', vec(1, 5, 3), intersection(pl1, pl2))
    yield lambda: verify_direction('t', vec(2, -1, 1), intersection(pl1, pl2))
    yield lambda: verify_direction('t', vec(1, -5, 3), intersection(pl1, pl2))
    yield lambda: verify_direction('t', vec(1, 1, 1), intersection(pl1, pl2))
    yield lambda: verify_direction('t', vec(1, 1, 1), ray)
    yield lambda: verify_direction('t', vec(0, 0, 0), ray)
    yield lambda: verify_direction('t', vec(1, 1), ray)
    yield lambda: verify_direction('t', ..., ray)
    yield lambda: verify_intersection('t', 'none', pl1, pl2, pl3)
    yield lambda: verify_intersection('t', (1, -2, 0), pl1, pl2, pl3)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(1, 5, 3), pl1, pl2, pl3)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(1, 5, 3), pl1, pl2)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(2, -1, 1), pl1, pl2)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(1, -5, 3), pl1, pl2)
    yield lambda: verify_intersection('t', vec(0, 0, 0) + lam * vec(1, 5, 3), pl1, pl2)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(1, 1, 1), pl1, pl2)
    yield lambda: verify_intersection('t', vec(1, -2, 0) + lam * vec(0, 0, 0), pl1, pl2)
    yield lambda: verify_intersection('t', (1, -2, 0), pl1, pl2)
    yield lambda: verify_intersection('t', (9, 9, 9), pl1, pl2)
    yield lambda: verify_intersection('t', 'none', pl1, pl2)
    yield lambda: verify_intersection('t', 3, pl1, pl2)
    yield lambda: verify_intersection('t', (Rational(3, 4), Rational(-5, 4), Rational(-3, 4)), ray, mirror_plane)
    yield lambda: verify_intersection('t', (Rational(-3, 4), Rational(-11, 4), Rational(3, 4)), ray, mirror_plane)
    yield lambda: verify_intersection('t', Rational(3, 4), ray, mirror_plane)
    yield lambda: verify_intersection('t', 7, ray, mirror_plane)
    yield lambda: verify_intersection('t', 'none', ray, mirror_plane)
    yield lambda: verify_intersection('t', vec(0, -2, 0) + lam * vec(1, 1, -1), ray, mirror_plane)
    yield lambda: verify_intersection('t', (0, 0, 0), ray, mirror_plane)
    yield lambda: verify_intersection('t', (1, 1), ray, mirror_plane)
    yield lambda: verify_intersection('t', 'nonsense', ray, mirror_plane)
    yield lambda: verify_intersection('t', Eq(x, 1), pl1, pl1)
    yield lambda: verify_intersection('t', ..., ray, mirror_plane)
    yield lambda: verify_distance('t', sqrt(94) / 2, intersection(pl1, pl2), pl3)
    yield lambda: verify_distance('t', 47, intersection(pl1, pl2), pl3)
    yield lambda: verify_distance('t', 0.5, intersection(pl1, pl2), pl3)
    yield lambda: verify_distance('t', sqrt(94), intersection(pl1, pl2), pl3)
    yield lambda: verify_distance('t', 4.85, intersection(pl1, pl2), pl3, exact=True)
    yield lambda: verify_distance('t', 6.71, vec(-3, 12, 2), wall)
    yield lambda: verify_distance('t', 12.5, vec(-3, 12, 2), wall)
    yield lambda: verify_distance('t', 3.13, vec(-3, 12, 2), wall)
    yield lambda: verify_distance('t', 0, pl1, pl2)
    yield lambda: verify_distance('t', 1, pl1, pl2)
    yield lambda: verify_distance('t', 'far', vec(-3, 12, 2), wall)
    yield lambda: verify_distance('t', ..., vec(-3, 12, 2), wall)
    yield lambda: verify_find('t', (-3, 6, 5), cX, [on(cX, wall), perpendicular(cX - vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 6, 4), cX, [on(cX, wall), perpendicular(cX - vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-2, 6, 5), cX, [on(cX, wall), perpendicular(cX - vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 0, 8), im, [reflection(im, vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 6, 5), im, [reflection(im, vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 12, 2), im, [reflection(im, vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 0, 9), im, [reflection(im, vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', (-3, 2, 13), im, [reflection(im, vec(-3, 12, 2), wall)])
    yield lambda: verify_find('t', [-3, Rational(-3, 2)], [kk_, sp.Symbol('q')],
                              [perpendicular(plane(Eq(2 * x + 6 * y - 2 * z, 5)), fam_plane),
                               on(vec(2, Rational(1, 2), 1), fam_plane)])
    yield lambda: verify_find('t', [3, Rational(-3, 2)], [kk_, sp.Symbol('q')],
                              [perpendicular(plane(Eq(2 * x + 6 * y - 2 * z, 5)), fam_plane),
                               on(vec(2, Rational(1, 2), 1), fam_plane)])
    yield lambda: verify_find('t', 3, sp.Symbol('p'), [parallel(plane(Eq(2 * x + 6 * y - 2 * z, 5)),
                                                                 plane(Eq(3 * x + 9 * y + sp.Symbol('p') * z, 1)))])
    yield lambda: verify_find('t', 1, sp.Symbol('p'), [perpendicular(vec(1, 1, sp.Symbol('p')), pl1)])
    yield lambda: verify_find('t', 1, sp.Symbol('p'), [parallel(line(vec(0, 0, 0), vec(1, 1, sp.Symbol('p'))), pl1)])
    yield lambda: verify_find('t', [Rational(4, 3), 18], [bb_, dd_],
                              [meet_in_line(plane(Eq(x + y - z, -2)), plane(Eq(2 * x + bb_ * y - z, 3)),
                                            plane(Eq(x - y + 2 * z, dd_)))])
    yield lambda: verify_find('t', [1, 19], [bb_, dd_],
                              [meet_in_line(plane(Eq(x + y - z, -2)), plane(Eq(2 * x + bb_ * y - z, 3)),
                                            plane(Eq(x - y + 2 * z, dd_)))])
    yield lambda: verify_find('t', 3, sp.Symbol('a'),
                              [no_unique_meet(plane(Eq(2 * x + 6 * y - 8 * z, 13)), plane(Eq(3 * x - y + 3 * z, 12)),
                                              plane(Eq(sp.Symbol('a') * x + 12 * y - 16 * z, 1)))])
    yield lambda: verify_find('t', 5, sp.Symbol('b'), [meet(pl1, plane(Eq(4 * x - 2 * y + 2 * z, sp.Symbol('b'))))])
    yield lambda: verify_line('t', vec(Rational(3, 2), -2, Rational(-3, 2)) + mu * vec(1, 1, -1), mirror(ray, mirror_plane))

    # измерения, C7: произведение, площадь, объём, тождество, угол, расстояние
    su, sv = vec(2, 0, 1), vec(1, 3, -1)
    sw = cross(su, sv)
    cc_ = sp.Symbol('c')
    yield lambda: print(measure('triangle', vec(0, 0, 0), su, sv), distance(vec(0, 3, 4), ray))
    yield lambda: verify_cross('t', sw, su, sv)
    yield lambda: verify_cross('t', -sw, su, sv)
    yield lambda: verify_cross('t', vec(-3, -3, 6), su, sv)
    yield lambda: verify_cross('t', vec(3, 3, 6), su, sv)
    yield lambda: verify_cross('t', dot(su, sv), su, sv)
    yield lambda: verify_cross('t', vec(2, 0, -1), su, sv)
    yield lambda: verify_cross('t', vec(1, 1, 1), su, sv)
    yield lambda: verify_cross('t', 2 * sw, su, sv)
    yield lambda: verify_cross('t', vec(1, 2), su, sv)
    yield lambda: verify_cross('t', cross(vec(1, cc_, 0), sv), vec(1, cc_, 0), sv)
    yield lambda: verify_cross('t', vec(0, 0, 0), su, sv)
    yield lambda: verify_cross('t', ..., su, sv)
    sq1, sq2, sq3, sq4 = vec(0, 0, 0), vec(2, 1, 0), vec(3, 3, 0), vec(1, 2, 0)
    top = vec(0, 0, 4)
    yield lambda: verify_measure('t', 3, 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', Rational(3, 2), 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', Rational(3, 2), 'triangle', sq1, sq2, sq4)
    yield lambda: verify_measure('t', 3, 'triangle', sq1, sq2, sq4)
    yield lambda: verify_measure('t', mag(sq2) * mag(sq4), 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', 4, 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', 9, 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', 7, 'parallelogram', sq1, sq2, sq3, sq4)
    yield lambda: verify_measure('t', vec(1, 2, 3), 'triangle', sq1, sq2, sq4)
    yield lambda: verify_measure('t', 3, 'parallelogram', sq1, sq2, sq4, sq3)
    yield lambda: verify_measure('t', 1.5, 'triangle', sq1, sq2, sq4)
    yield lambda: verify_measure('t', 1.5, 'triangle', sq1, sq2, sq4, exact=True)
    yield lambda: verify_measure('t', ..., 'triangle', sq1, sq2, sq4)
    yield lambda: verify_measure('t', 2, 'pyramid', top, sq1, sq2, sq4)
    yield lambda: verify_measure('t', 6, 'pyramid', top, sq1, sq2, sq4)
    yield lambda: verify_measure('t', 12, 'pyramid', top, sq1, sq2, sq4)
    yield lambda: verify_measure('t', 4, 'pyramid', top, sq1, sq2, sq4)
    yield lambda: verify_measure('t', Rational(3, 2), 'pyramid', top, sq1, sq2, sq4)
    yield lambda: verify_measure('t', 5, 'pyramid', top, sq1, sq2, sq4)
    fa = vec(*sp.symbols('a1 a2 a3'))
    fb = vec(*sp.symbols('b1 b2 b3'))
    fL, fM, fT = sp.symbols('L M th')
    fletters = {fL: mag(fa), fM: mag(fb), fT: angle(fa, fb)}
    fsquare = dot(cross(fa, fb), cross(fa, fb))
    yield lambda: verify_formula('t', fL ** 2 * fM ** 2 * sin(fT) ** 2, fsquare, fletters)
    yield lambda: verify_formula('t', fL ** 2 * fM ** 2 * cos(fT) ** 2, fsquare, fletters)
    yield lambda: verify_formula('t', fL * fM * sin(fT), fsquare, fletters)
    yield lambda: verify_formula('t', fL * fM * x, fsquare, fletters)
    yield lambda: verify_formula('t', fL ** 2 * fM ** 2 * sin(fT), fsquare, fletters)
    yield lambda: verify_formula('t', -fL ** 2 * fM ** 2 * sin(fT) ** 2, fsquare, fletters)
    yield lambda: verify_formula('t', ..., fsquare, fletters)
    arc1, arc2 = vec(6, 0, 0), vec(0, 6, 0)
    yield lambda: verify_arc('t', 3 * pi, 6, arc1, arc2)
    yield lambda: verify_arc('t', pi / 2, 6, arc1, arc2)
    yield lambda: verify_arc('t', 90, 6, arc1, arc2)
    yield lambda: verify_arc('t', 540, 6, arc1, arc2)
    yield lambda: verify_arc('t', 6 * sqrt(2), 6, arc1, arc2)
    yield lambda: verify_arc('t', vec(1, 2, 3), 6, arc1, arc2)
    yield lambda: verify_arc('t', 9.42, 6, arc1, arc2, exact=True)
    yield lambda: verify_arc('t', 7, 6, arc1, arc2)
    yield lambda: verify_arc('t', ..., 6, arc1, arc2)
    ang1 = plane(Eq(x + 2 * y + z, 0), name='P1')
    ang2 = plane(Eq(x - y - 2 * z, 0), name='P2')
    flat = plane(Eq(z, 0), name='flat')
    slope = line(vec(0, 0, 0) + lam * vec(1, 1, 1), lam, name='L')
    yield lambda: print(angle(ang1, ang2), angle(slope, flat))
    yield lambda: verify_angle('t', 60, ang1, ang2, deg=True)
    yield lambda: verify_angle('t', 120, ang1, ang2, deg=True)
    yield lambda: verify_angle('t', Rational(1, 2), ang1, ang2, cosine=True)
    yield lambda: verify_angle('t', -Rational(1, 2), ang1, ang2, cosine=True)
    yield lambda: verify_angle('t', sp.asin(1 / sqrt(3)), slope, flat)
    yield lambda: verify_angle('t', float(sp.acos(1 / sqrt(3))), slope, flat)
    yield lambda: verify_angle('t', 1.0, slope, flat)
    axis = line(vec(0, 0, 0) + lam * vec(1, 0, 0), lam, name='L1')
    twice = line(vec(0, 0, 0) + lam * vec(2, 0, 0), lam, name='L1')
    beside = line(vec(0, 1, 0) + mu * vec(2, 0, 0), mu, name='L2')
    askew = line(vec(0, 1, 0) + mu * vec(0, 0, 1), mu, name='L3')
    crossing = line(vec(0, 0, 0) + mu * vec(0, 1, 0), mu, name='L4')
    yield lambda: verify_distance('t', 5, vec(0, 3, 4), axis)
    yield lambda: verify_distance('t', 10, vec(0, 3, 4), twice)
    yield lambda: verify_distance('t', mag(vec(3, 3, 4)), vec(3, 3, 4), axis)
    yield lambda: verify_distance('t', 3, vec(3, 3, 4), axis)
    yield lambda: verify_distance('t', mag(vec(3, 3, 4)) + 1, vec(3, 3, 4), axis)
    yield lambda: verify_distance('t', 1, axis, beside)
    yield lambda: verify_distance('t', 2, axis, beside)
    yield lambda: verify_distance('t', mag(vec(0, 1, 0)) + 7, axis, beside)
    yield lambda: verify_distance('t', 1, axis, askew)
    yield lambda: verify_distance('t', 2, axis, askew)
    yield lambda: verify_distance('t', 3, axis, crossing)
    yield lambda: verify_distance('t', vec(1, 2, 3), axis, beside)
    yield lambda: verify_distance('t', 1.0, axis, beside, exact=True)
    yield lambda: verify_distance('t', ..., axis, beside)
    ss_ = sp.Symbol('s')
    yield lambda: verify_optimum('t', 3, (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')
    yield lambda: verify_optimum('t', 3, (ss_ - 2) ** 2 + 3, ss_, Interval(0, oo), 'min')
    yield lambda: verify_optimum('t', 2, (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')
    yield lambda: verify_optimum('t', 12, (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')
    yield lambda: verify_optimum('t', 5, (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')
    yield lambda: verify_optimum('t', vec(1, 2), (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')
    yield lambda: verify_optimum('t', ..., (ss_ - 2) ** 2 + 3, ss_, Interval(0, 5), 'min')

    # форма графика, E8: точка, её вид, вогнутость, перегиб, сторона оси
    cube = x ** 3 - 6 * x ** 2 + 9 * x + 1
    flat_curve = curve(Eq(y, cube))
    yield lambda: print(stationary(cube, (-1, 5)), concavity(cube, 1),
                        nature(cube, 3), inflexions(cube, (-1, 5)),
                        crossings(cube, (-5, 5)))
    yield lambda: verify_turning('t', [(1, 5), (3, 1)], cube, domain=(-1, 5))
    yield lambda: verify_turning('t', (1, 5), cube, 'maximum', domain=(-1, 5))
    yield lambda: verify_turning('t', (1, 4), cube, 'maximum', domain=(-1, 5))
    yield lambda: verify_turning('t', (2, 3), cube, 'maximum', domain=(-1, 5))
    yield lambda: verify_turning('t', [(1, 5)], cube, domain=(-1, 5))
    yield lambda: verify_turning('t', [(1, 5), (1, 5)], cube, domain=(-1, 5))
    yield lambda: verify_turning('t', (7, 1), cube, domain=(-1, 5))
    yield lambda: verify_turning('t', 1, cube, 'maximum', domain=(-1, 5))
    yield lambda: verify_turning('t', 1, cube, 'maximum', domain=(-1, 5), coordinates=False)
    yield lambda: verify_turning('t', [], cube, domain=(-1, 5))
    yield lambda: verify_turning('t', [], x ** 3 + x, domain=(-2, 2))
    yield lambda: verify_turning('t', (1, 5), flat_curve, 'maximum', domain=(-1, 5))
    yield lambda: verify_turning('t', (5, 1), cube, domain=(-1, 5))
    yield lambda: verify_turning('t', ..., cube, domain=(-1, 5))
    yield lambda: verify_nature('t', 'maximum', cube, 1, domain=(-1, 5))
    yield lambda: verify_nature('t', 'minimum', cube, 1, domain=(-1, 5))
    yield lambda: verify_nature('t', 'inflexion', cube, 1, domain=(-1, 5))
    yield lambda: verify_nature('t', 'maximum', cube, 3, domain=(-1, 5))
    yield lambda: verify_nature('t', 'inflexion', cube, 2, domain=(-1, 5))
    yield lambda: verify_nature('t', 'minimum', cube, 2, domain=(-1, 5))
    yield lambda: verify_nature('t', ['maximum', 'minimum'], cube, [1, 3], domain=(-1, 5))
    yield lambda: verify_nature('t', ['maximum'], cube, [1, 3], domain=(-1, 5))
    yield lambda: verify_nature('t', 'sideways', cube, 1, domain=(-1, 5))
    yield lambda: verify_nature('t', 'maximum', cube, 99, domain=(-1, 5))
    yield lambda: verify_nature('t', 'minimum', x ** 4, 0, domain=(-2, 2))
    yield lambda: verify_nature('t', 'inflexion', x ** 3, 0, domain=(-2, 2))
    yield lambda: verify_nature('t', 'maximum', x ** 3 + sp.Symbol('a') * x ** 2,
                                -2 * sp.Symbol('a') / 3, domain=(-8, 8),
                                params={sp.Symbol('a'): (3, 6)})
    yield lambda: verify_nature('t', ..., cube, 1, domain=(-1, 5))
    yield lambda: verify_concavity('t', 'down', cube, 1)
    yield lambda: verify_concavity('t', 'up', cube, 1)
    yield lambda: verify_concavity('t', 'sideways', cube, 1)
    yield lambda: verify_concavity('t', ['down', 'up'], cube, [1, 3])
    yield lambda: verify_concavity('t', ['down'], cube, [1, 3])
    yield lambda: verify_concavity('t', 'up', cube, 99)
    yield lambda: verify_concavity('t', ..., cube, 1)
    yield lambda: verify_bend('t', 2, cube, domain=(-1, 5))
    yield lambda: verify_bend('t', 3, cube, domain=(-1, 5))
    yield lambda: verify_bend('t', 2.01, cube, domain=(-1, 5))
    yield lambda: verify_bend('t', (2, 3), cube, domain=(-1, 5), coordinates=True)
    yield lambda: verify_bend('t', (3, 2), cube, domain=(-1, 5), coordinates=True)
    yield lambda: verify_bend('t', (2, 9), cube, domain=(-1, 5), coordinates=True)
    yield lambda: verify_bend('t', [2, 2], cube, domain=(-1, 5))
    yield lambda: verify_bend('t', [], cube, domain=(-1, 5))
    yield lambda: verify_bend('t', [], x ** 2, domain=(-2, 2))
    yield lambda: verify_bend('t', ..., cube, domain=(-1, 5))
    yield lambda: verify_side('t', 'above', cube, 1)
    yield lambda: verify_side('t', 'below', cube, 1)
    yield lambda: verify_side('t', 'upwards', cube, 1)
    yield lambda: verify_side('t', ['above', 'above'], cube, [1, 3])
    yield lambda: verify_side('t', ['above'], cube, [1, 3])
    yield lambda: verify_side('t', 'above', cube, 99)
    yield lambda: verify_side('t', ..., cube, 1)
    cd_ = sp.Symbol('d')
    yield lambda: verify_condition('t', Or(cc_ <= 0, cd_ > 2 * cc_ ** Rational(3, 2),
                                           cd_ < -2 * cc_ ** Rational(3, 2)),
                                   lambda c, d: crossings(x ** 3 - 3 * c * x + d,
                                                          (-30, 30)) == 1,
                                   (cc_, cd_), window=(-2, 2), steps=6)
    yield lambda: verify_condition('t', Or(cc_ <= 0, cd_ > 2 * cc_ ** Rational(3, 2)),
                                   lambda c, d: crossings(x ** 3 - 3 * c * x + d,
                                                          (-30, 30)) == 1,
                                   (cc_, cd_), window=(-2, 2), steps=6)
    yield lambda: verify_condition('t', cc_ + cd_ > 0, lambda c, d: None,
                                   (cc_, cd_), window=(-2, 2), steps=6)
    yield lambda: verify_condition('t', ..., lambda c, d: True, (cc_, cd_))

    # данные, D7: сводные числа, ящик с усами, прямая, r, точка средних
    dp_, dq_ = sp.symbols('p q')
    d_pairs = Pairs([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
    d_far = Pairs([81, 175, 202, 346, 360], [15, 27, 23, 35, 46], names=('y', 'x'))
    d_table = Sample({2: 5, 3: 1, 4: 4, 5: 3, 6: 7})
    d_open = Sample({2: 5, 3: 1, 4: 4, 5: 3, 6: x})
    d_hidden = Sample([Bunch(28, average=10.5, lowest=6, highest=17), dp_, dq_])
    d_box = Box(0.24, 0.27, 0.28, 0.35, 0.46)
    d_eggs = Box(10, dp_, 40, dq_, 75)
    d_rules = [Eq(iqr(d_eggs), 20), clean(d_eggs)]
    d_lines = [Eq(A, Rational(7, 4) * B + 20), Eq(B, A / 2 - 9)]
    yield lambda: verify_summary('t', 1.58, d_table, 'deviation')
    yield lambda: verify_summary('t', 1.63, d_table, 'deviation')
    yield lambda: verify_summary('t', 2.51, d_table, 'deviation')
    yield lambda: verify_summary('t', 4, d_table, 'mean')
    yield lambda: verify_summary('t', 4, d_table, 'median')
    yield lambda: verify_summary('t', 9, d_table, 'median')
    yield lambda: verify_summary('t', 0.27, d_box, 'median')
    yield lambda: verify_summary('t', 'many', d_box, 'median')
    yield lambda: verify_summary('t', ..., d_box, 'median')
    yield lambda: verify_missing('t', 7, d_open, median=4.5)
    yield lambda: verify_missing('t', 8, d_open, median=4.5)
    yield lambda: verify_missing('t', (5, 19), d_hidden, holds=[dp_ < 6], mean=10.6, range=14)
    yield lambda: verify_missing('t', (6, 18), d_hidden, holds=[dp_ < 6], mean=10.6, range=14)
    yield lambda: verify_missing('t', (5, 19, 1), d_hidden, mean=10.6)
    yield lambda: verify_missing('t', 5, d_hidden, mean=10.6)
    yield lambda: verify_missing('t', {dp_: 5, dq_: 19}, d_hidden, median=10)
    yield lambda: verify_missing('t', ..., d_hidden, mean=10.6)
    yield lambda: verify_bound('t', 45, d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_bound('t', 60, d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_bound('t', 50, d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_bound('t', 70, d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_bound('t', 'x', d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_bound('t', 45, d_eggs, dq_, 'least', holds=[Eq(dq_, 1), Eq(dq_, 2)])
    yield lambda: verify_bound('t', ..., d_eggs, dq_, 'least', holds=d_rules)
    yield lambda: verify_fence('t', 0.47, d_box)
    yield lambda: verify_fence('t', 0.525, d_box)
    yield lambda: verify_fence('t', 0.4, d_box)
    yield lambda: verify_fence('t', 0.15, d_box)
    yield lambda: verify_fence('t', 0.43, d_box)
    yield lambda: verify_fence('t', 0.9, d_box)
    yield lambda: verify_fence('t', ..., d_box)
    yield lambda: verify_outlier('t', 'no', d_box, 0.46)
    yield lambda: verify_outlier('t', 'yes', d_box, 0.46)
    yield lambda: verify_outlier('t', 'maybe', d_box, 0.46)
    yield lambda: verify_outlier('t', ..., d_box, 0.46)
    yield lambda: verify_skew('t', 'positive', d_box)
    yield lambda: verify_skew('t', 'negative', d_box)
    yield lambda: verify_skew('t', 'odd', d_box)
    yield lambda: verify_skew('t', ..., d_box)
    yield lambda: verify_fit('t', (0.6, 2.2), d_pairs)
    yield lambda: verify_fit('t', (2.2, 0.6), d_pairs)
    yield lambda: verify_fit('t', (1, -1), d_pairs)
    yield lambda: verify_fit('t', (1.67, -3.67), d_pairs)
    yield lambda: verify_fit('t', (0.6, 3), d_pairs)
    yield lambda: verify_fit('t', (0.9, 2.2), d_pairs)
    yield lambda: verify_fit('t', (3, 9), d_pairs)
    yield lambda: verify_fit('t', 'line', d_pairs)
    yield lambda: verify_fit('t', Eq(x, 0.0935 * y + 7.43), d_far, of='x')
    yield lambda: verify_fit('t', ..., d_pairs)
    yield lambda: verify_strength('t', 0.775, d_pairs)
    yield lambda: verify_strength('t', 0.6, d_pairs)
    yield lambda: verify_strength('t', -0.775, d_pairs)
    yield lambda: verify_strength('t', 0.77, d_pairs)
    yield lambda: verify_strength('t', 1.4, d_pairs)
    yield lambda: verify_strength('t', 0.1, d_pairs)
    yield lambda: verify_strength('t', 'r', d_pairs)
    yield lambda: verify_strength('t', ..., d_pairs)
    yield lambda: verify_estimate('t', 5.2, d_pairs, 5)
    yield lambda: verify_estimate('t', 5.2, d_pairs, 5, whole=True)
    yield lambda: verify_estimate('t', 3, d_pairs, 5)
    yield lambda: verify_estimate('t', 4.67, d_pairs, 5)
    yield lambda: verify_estimate('t', 7, d_pairs, 5)
    yield lambda: verify_estimate('t', 37, d_far, 310, of='x', whole=True)
    yield lambda: verify_estimate('t', 93.5, d_lines, 42, of=B)
    yield lambda: verify_estimate('t', 12, d_lines, 42, of=B)
    yield lambda: verify_estimate('t', 'n', d_pairs, 5)
    yield lambda: verify_estimate('t', ..., d_pairs, 5)
    yield lambda: verify_change('t', 1.8, d_pairs, 3)
    yield lambda: verify_change('t', 6.6, d_pairs, 3)
    yield lambda: verify_change('t', 0.6, d_pairs, 3)
    yield lambda: verify_change('t', 9, d_pairs, 3)
    yield lambda: verify_change('t', ..., d_pairs, 3)
    yield lambda: verify_centre('t', (3, 4), d_pairs)
    yield lambda: verify_centre('t', (4, 3), d_pairs)
    yield lambda: verify_centre('t', (1, 1), d_pairs)
    yield lambda: verify_centre('t', 3, d_pairs)
    yield lambda: verify_centre('t', 34, d_lines, of=A)
    yield lambda: verify_centre('t', 8, d_lines, of=A)
    yield lambda: verify_centre('t', 50, d_lines, of=A)
    yield lambda: verify_centre('t', (1, 1), [Eq(A, B), Eq(A, B + 1)])
    yield lambda: verify_centre('t', ..., d_pairs)
    yield lambda: verify_effect('t', 'no effect', d_pairs, lambda v: v - 3)
    yield lambda: verify_effect('t', 'decreases', d_pairs, lambda v: v - 3)
    yield lambda: verify_effect('t', 'no effect', d_pairs, lambda v: -v)
    yield lambda: verify_effect('t', 'sideways', d_pairs, lambda v: v)
    yield lambda: verify_effect('t', ..., d_pairs, lambda v: v)
    yield lambda: verify_reason('t', 'extrapolation', d_pairs, 40, given='x', predict='y')
    yield lambda: verify_reason('t', 'wrong line', d_pairs, 40, given='x', predict='y')
    yield lambda: verify_reason('t', 'extrapolation', d_pairs, 4, given='y', predict='x')
    yield lambda: verify_reason('t', 'extrapolation', d_pairs, 3, given='x', predict='y')
    yield lambda: verify_reason('t', 'because', d_pairs, 3, given='x', predict='y')
    yield lambda: verify_reason('t', ..., d_pairs, 3, given='x', predict='y')
    yield lambda: check_word('t', 'convenience', digest('convenience'))
    yield lambda: check_word('t', 'quota', digest('convenience'))
    yield lambda: check_word('t', ..., digest('convenience'))


print('=== статически: строки с кириллицей вне русской половины _t ===')
leftovers = static_scan()
# Номер строки не называется `line`: это имя прямой из kit, и вызовы ниже
# его читают — на первой же найденной строке прогон падал с TypeError.
for where, row, text in leftovers:
    print(f'  {where}:{row}  {text!r}')
    problems.append(f'{where}:{row}')
print(f'найдено: {len(leftovers)}')

print('\n=== динамически: вывод в режиме en ===')
kit.language('en')
seen = 0
for call in calls():
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            call()
        except Exception as exc:                                     # noqa: BLE001
            print(f'RAISED {type(exc).__name__}: {exc}')
    out = buf.getvalue()
    seen += 1
    if not out.strip():
        problems.append(f'вызов {seen}: ничего не напечатано')
        print(f'  {seen}: ничего не напечатано')
    if CYR.search(out):
        problems.append(f'вызов {seen}: кириллица')
        print(f'  {seen}: {out.strip()}')
    if 'RAISED' in out:
        # Проверка обязана печатать вердикт, а не падать: ноутбук проходится
        # сверху вниз, и исключение здесь означало бы, что ветка не проверена.
        problems.append(f'вызов {seen}: исключение вместо вердикта')
        print(f'  {seen}: {out.strip()}')
print(f'вызовов проверено: {seen}')

kit.language('ru')
ru = io.StringIO()
with contextlib.redirect_stdout(ru):
    check_num('t', 2.7, 3, digest(sig(2.5, 3)))
if not CYR.search(ru.getvalue()):
    problems.append('режим ru перестал печатать по-русски')
print(f"\nрусский режим на месте: {ru.getvalue().strip()}")

print()
if problems:
    print(f'✗ проблем: {len(problems)}')
    for p in problems:
        print(f'   {p}')
    sys.exit(1)
print(f'✓ все {seen} вызовов в режиме en печатают только латиницей')
