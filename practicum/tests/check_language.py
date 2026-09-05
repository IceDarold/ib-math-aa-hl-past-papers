"""Сообщения проверок не смешивают языки.

Практикум B2 написан по-английски, а kit.py общий: одна забытая строка —
и посреди английской работы печатается «не сходится». Проверок две.

Статическая разбирает kit.py через ast и ищет строковые литералы
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
# перекрывает модуль регулярных выражений — про это сказано в самом kit.py.
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
KIT = os.path.join(ROOT, 'practicum', 'kit.py')
n = sp.Symbol('n')
problems = []


def static_scan():
    """Строки с кириллицей вне русской половины `_t`."""
    tree = ast.parse(io.open(KIT, encoding='utf-8').read())
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
    yield lambda: trigger_check({1: 'a'}, {1: digest('a')})
    yield lambda: trigger_check({1: 'b'}, {1: digest('a')})
    yield lambda: trigger_check({1: ''}, {1: digest('a')})


print('=== статически: строки с кириллицей вне русской половины _t ===')
leftovers = static_scan()
for line, text in leftovers:
    print(f'  kit.py:{line}  {text!r}')
    problems.append(f'kit.py:{line}')
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
