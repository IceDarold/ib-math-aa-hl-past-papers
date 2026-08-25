"""Прогоняет все проверки практикума B2 с ответами, выведенными заново.

Ответы не переписываются из раздела решений: композиции собираются
подстановкой, обратные — sp.solve по уравнению x = f(y), области — через
sp.minimum/sp.maximum и пределы на концах, численный ответ — nsolve.
Отдельно измеряется, что проверки отвергают и где они мягче экзамена.

Здесь же перепроверены пять расхождений с разметкой корпуса: удвоенная
ноябрьская сессия 2023 года и четыре формулы, у которых при извлечении
из PDF потерялась дробная черта или корень. У одной из четырёх вместе
с формулой уехал и ответ.

Проверки печатают по-английски: ноутбук английский, а сверяются здесь
ровно те же вызовы с теми же ярлыками. Комментарии остаются русскими —
это документация репозитория, а не материал ученика.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *                                                  # noqa: F403

import io                                                          # noqa: E402
import re as _re                                                   # noqa: E402
import contextlib                                                  # noqa: E402

language('en')

NB = os.path.join(ROOT, 'practicum/functions',
                  'practicum-b2-composition-inverse.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(",
                                   "check_series(", "check_domain(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a, b, c, m, n_, t_ = sp.symbols('a b c m n t')
y_ = sp.Symbol('y')


def t(name, ok):
    res.append((name, ok))


def silent(fn, *args, **kwargs):
    """Вызвать проверку, не печатая её вердикт: нас интересует только он."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = fn(*args, **kwargs)
    return out, buf.getvalue()


print('=== композиция вперёд ===')

# Задание 1(a). Касательная y = 6x − 1 при x = 4 даёт f(4); формулы f нет
# и не нужно — композиция возвращает аргумент на место.
tangent = 6 * x - 1
g1 = x**2 - 3 * x
inner1 = g1.subs(x, 4)
h4 = tangent.subs(x, inner1)
print(f'Задание 1(a): g(4) = {inner1}, значит h(4) = f({inner1}) = {h4}')
t('1a-неподвижная точка', inner1 == 4)
t('1a', check_num('Task 1(a)', h4, 6, D['Task 1(a)']))

f1b = (3 * x - 2) / (2 * x + 1)
t('1b', check_num('Task 1(b)', f1b.subs(x, 0), 6, D['Task 1(b)']))

# Задание 1(c). g(0) = 1 — этого хватает, сама g неизвестна.
f1c = sp.exp(2 * x) * (3 * x - 4)
t('1c', verify_exact('Task 1(c)', f1c.subs(x, 1), -sp.exp(2)))
# Продолжение вопроса: (f∘g)'(0) = f'(1)·g'(0).
print(f"Задание 1(c): f'(1)·g'(0) = {sp.simplify(sp.diff(f1c, x).subs(x, 1) * 2)}")
t('1c-цепное правило', sp.simplify(sp.diff(f1c, x).subs(x, 1) * 2 - 2 * sp.exp(2)) == 0)

x2 = sp.solve(sp.Eq(x + y_, 12), y_)[0]
t('1d', check_series('Task 1(d)', x * x2, D['Task 1(d)']))

# Задание 2. Композиция — подстановка, порядок читается справа налево.
k = sp.Symbol('k')
f2, g2 = x - 3, x**2 + k**2
comp2 = g2.subs(x, f2)
other2 = f2.subs(x, g2)
print(f'Задание 2: (g∘f)(x) = {sp.expand(comp2)}, а (f∘g)(x) = {sp.expand(other2)}')
t('2-порядок важен', sp.simplify(comp2 - other2) != 0)
t('2', check_series('Task 2', comp2, D['Task 2']))

# Задание 3. Композиция собирается подстановкой, тождество проверяется как
# тождество, а не как совпадение записей.
f3, g3 = 4**x, 1 + sp.log(x, 2)
comp3 = f3.subs(x, g3)
t('3', verify_identity('Task 3', comp3, 4 * x**2, samples=(0.4, 0.9, 1.6, 2.5, 4.1)))
t('3-другой порядок — прямая',
  sp.simplify(sp.expand_log(g3.subs(x, f3), force=True) - (1 + 2 * x)) == 0)

# Задание 4. Гиперболические косинус и синус; знак в тождестве плюс.
f4 = (sp.exp(t_) + sp.exp(-t_)) / 2
g4 = (sp.exp(t_) - sp.exp(-t_)) / 2
lhs4 = sp.simplify(sp.expand(f4**2 + g4**2))
print(f'Задание 4: f² + g² = {lhs4}, f(2t) = {sp.simplify(f4.subs(t_, 2 * t_))}')
t('4', verify_identity('Task 4', lhs4, f4.subs(t_, 2 * t_), var=t_))
t('4-минус даёт единицу', sp.simplify(f4**2 - g4**2) == 1)

# Задание 5. Уравнение получается подстановкой числа в композицию.
roots5 = sp.solve(sp.Eq(comp2.subs(x, 2), 10), k)
print(f'Задание 5: (g∘f)(2) = 10 даёт k ∈ {roots5}')
t('5', verify_root_set('Task 5', roots5, k**2 - 9, var=k))

# Задание 6. f неизвестна — сравниваем коэффициенты.
g6 = x**2 + x + 3
fa = a * x + b
poly6 = sp.Poly(sp.expand(g6.subs(x, fa) - (4 * x**2 - 14 * x + 15)), x)
sols6 = sp.solve(poly6.all_coeffs(), [a, b], dict=True)
funcs6 = [sp.expand(fa.subs(s)) for s in sols6]
print(f'Задание 6: система коэффициентов даёт {sols6}, то есть {funcs6}')
t('6-ровно две функции', len(funcs6) == 2)
t('6', check_set('Task 6', funcs6, D['Task 6']))

# Задание 7. Две распаковки подряд: арктангенс, затем сама g.
g7 = 1 / (x**2 - 2 * x - 3)
h7 = sp.atan(x / 2)
inner7 = sp.solve(sp.Eq(h7, sp.pi / 4), x)[0]
roots7 = sp.solve(sp.Eq(g7, inner7), x)
keep7 = [rt for rt in roots7 if rt > 3]
print(f'Задание 7: g(a) = {inner7}, корни {roots7}, в области x > 3 остаётся {keep7}')
t('7-один корень отброшен', len(roots7) == 2 and len(keep7) == 1)
t('7', verify_exact('Task 7', keep7[0], 1 + 3 * sp.sqrt(2) / 2))

print('=== чётность ===')

# Задание 8. Подстановка −x внутрь arcsin.
f8 = sp.asin((x**2 - 1) / (x**2 + 1))
t('8', verify_identity('Task 8', f8.subs(x, -x), f8))

# Задание 9. Общий член не меняется, значит и сумма не меняется.
r = sp.Symbol('r')
f9 = sp.Sum((-2 * x**2)**r, (r, 0, 3)).doit()
t('9-общий член', sp.simplify((-2 * (-x)**2)**r - (-2 * x**2)**r) == 0)
t('9', check_series('Task 9', sp.expand(f9.subs(x, -x)), D['Task 9']))

print('=== итерация ===')

# Задание 10. Композиции считаются честно, циклом, а не по формуле.
flin = m * x + c
it = [x]
for _ in range(4):
    it.append(sp.expand(flin.subs(x, it[-1])))
closed = m**n_ * x + c * (1 - m**n_) / (1 - m)
print(f'Задание 10: f² = {sp.simplify(it[2])}, f⁴ = {sp.simplify(it[4])}')
t('10a', check_series('Task 10(a)', it[2], D['Task 10(a)']))
t('10b', check_series('Task 10(b)', it[3], D['Task 10(b)']))
t('10c', check_series('Task 10(c)', it[4], D['Task 10(c)']))
t('10d', check_series('Task 10(d)', closed, D['Task 10(d)']))
# Замкнутая форма совпадает с итерацией при конкретных числах.
same = all(sp.simplify(closed.subs({n_: i, m: R(2, 3), c: 5})
                       - it[i].subs({m: R(2, 3), c: 5})) == 0
           for i in (2, 3, 4))
t('10-замкнутая форма = итерация', same)

print('=== обратная: свойство ===')

# Задание 11. Значение обратной находится решением f(x) = a.
t('11a', check_num('Task 11(a)', sp.solve(sp.Eq(4**x, 8), x)[0], 6, D['Task 11(a)']))
f11 = 4 / sp.tan(x) + sp.sin(x)
root11 = sp.nsolve(f11 - 2, 1.3)
print(f'Задание 11(b): f(x) = 2 при x = {root11}')
t('11b', check_num('Task 11(b)', root11, 3, D['Task 11(b)']))
# Обратная существует потому, что f строго убывает на (0, π).
der11 = sp.simplify(sp.diff(f11, x))
t('11b-строго убывает',
  all(der11.subs(x, v).evalf() < 0 for v in (0.2, 0.8, 1.5, 2.4, 3.0)))

# Задание 12. Данные графика: f(−3) = −1, множество значений [−3, 5].
t('12a', check_domain('Task 12(a)', sp.Interval(-3, 5), D['Task 12(a)']))
x12 = sp.solve(sp.Eq(2 * x - 7, -1), x)[0]
print(f'Задание 12(b): 2x − 7 = f(−3) = −1 даёт x = {x12}')
t('12b', check_num('Task 12(b)', x12, 6, D['Task 12(b)']))
t('12b-ловушка не совпадает с ответом', sp.solve(sp.Eq(2 * x - 7, -3), x)[0] != x12)

# Задание 13. g = g⁻¹ это g(g(x)) = x; решаем относительно a.
g13 = (a * x + 4) / (3 - x)
comp13 = sp.together(sp.simplify(g13.subs(x, g13)) - x)
a13 = sp.solve(sp.Poly(sp.numer(comp13), x).all_coeffs(), a)
print(f'Задание 13: g(g(x)) = x выполняется только при a ∈ {a13}')
t('13-единственное значение', a13 == [(-3,)])
t('13', check_num('Task 13', a13[0][0], 6, D['Task 13']))
t('13-подстановка возвращает x',
  sp.simplify(g13.subs(a, -3).subs(x, g13.subs(a, -3)) - x) == 0)

print('=== обратная: формула ===')


def invert(expr, domain=None, var=x):
    """Все ветви обратной: решаем x = f(y) относительно y."""
    return [sp.simplify(s) for s in sp.solve(sp.Eq(var, expr.subs(var, y_)), y_)]


f14 = (7 * x + 7) / (2 * x - 4)
inv14 = invert(f14)
print(f'Задание 14: обратная {inv14}')
t('14', verify_inverse('Task 14', inv14[0], f14, domain=sp.Interval.open(2, 20)))

g15 = 1 + sp.log(x, 2)
inv15 = invert(g15)
t('15', verify_inverse('Task 15', inv15[0], g15, domain=sp.Interval.open(0, 12)))
# Сдвиг влево, потом растяжение — 4^x; в обратном порядке выходит 2·4^x.
right15 = (2**(x - 1)).subs(x, x + 1).subs(x, 2 * x)
wrong15 = (2**(x - 1)).subs(x, 2 * x).subs(x, x + 1)
print(f'Задание 15: верный порядок даёт {right15}, обратный — {wrong15}')
t('15-порядок преобразований важен',
  sp.simplify(right15 - 4**x) == 0 and sp.simplify(wrong15 - 4**x) != 0)

print('=== обратная: область ===')

# Задание 16. Первая точка поворота справа от нуля: sin(x − k) = 0.
for label, kv, want in (('Task 16(a)', sp.pi / 2, sp.pi / 2),
                        ('Task 16(b)', sp.pi, sp.pi)):
    turns = sp.solveset(sp.sin(x - kv), x, sp.Interval.open(0, 4 * sp.pi))
    first = min(turns)
    print(f'{label}: повороты в {turns}, первый {first}')
    t(label, verify_exact(label, first, want))
# Символ k тот же, что в задании 2: эталон считался по нему, и лишние
# предположения (positive=True) сделали бы srepr другим.
t('16c-точка поворота', sp.simplify(sp.sin((k - sp.pi) - k)) == 0)
t('16c', check_expr('Task 16(c)', k - sp.pi, D['Task 16(c)']))

# Задание 17. Обе ветви налицо; выбирает область исходной функции.
f17 = sp.sqrt(x**2 - 1)
dom17 = sp.Interval(1, 2)
inv17 = invert(f17)
print(f'Задание 17: ветви {inv17}')
t('17-две ветви', len(inv17) == 2)
good17 = [e for e in inv17 if e.subs(x, 1).evalf() > 0]
t('17a', verify_inverse('Task 17(a)', good17[0], f17, domain=dom17))
rng17 = sp.Interval(sp.minimum(f17, x, dom17), sp.maximum(f17, x, dom17))
print(f'Задание 17: множество значений f на [1, 2] это {rng17}')
t('17b', check_domain('Task 17(b)', rng17, D['Task 17(b)']))
t('17c', check_domain('Task 17(c)', dom17, D['Task 17(c)']))

# Задание 18. Область g⁻¹ — множество значений g: один конец достигается,
# другой нет, и различие ровно в этом.
K = 1 / sp.sqrt(2)
g18 = 1 / (1 + 2 * x**2)
inv18 = [e for e in invert(g18) if e.subs(x, R(3, 4)).evalf() > 0]
t('18a', verify_inverse('Task 18(a)', inv18[0], g18,
                        domain=sp.Interval.Ropen(0, K)))
top18 = g18.subs(x, 0)
bot18 = sp.limit(g18, x, K, '-')
print(f'Задание 18: g(0) = {top18} достигается, предел в K это {bot18} — нет')
t('18-концы', top18 == 1 and bot18 == R(1, 2))
t('18b', check_domain('Task 18(b)', sp.Interval.Lopen(bot18, top18), D['Task 18(b)']))

print('=== обратная: ветвь ===')

# Задание 19. Ветвь выбирается тем, что значения g⁻¹ обязаны быть больше 3.
g19 = 1 / (x**2 - 2 * x - 3)
inv19 = invert(g19)
probe = g19.subs(x, 4)
keep19 = [e for e in inv19 if abs(complex(sp.N(e.subs(x, probe))) - 4) < 1e-9]
print(f'Задание 19: ветви {inv19}; g(4) = {probe}, возвращает 4 только {keep19}')
t('19-ровно одна ветвь', len(inv19) == 2 and len(keep19) == 1)
t('19a', verify_inverse('Task 19(a)', keep19[0], g19,
                        domain=sp.Interval.open(3, 20)))
t('19-множество значений: ноль не достигается',
  sp.limit(g19, x, sp.oo) == 0 and sp.limit(g19, x, 3, '+') is sp.oo)
t('19b', check_domain('Task 19(b)', sp.Interval.open(0, sp.oo), D['Task 19(b)']))

# Задание 20. Та же работа через arcsin; концы области берутся из пределов.
g20 = sp.asin((x**2 - 1) / (x**2 + 1))
inv20 = [e for e in invert(g20) if e.subs(x, 0).evalf() >= 0]
t('20a', verify_inverse('Task 20(a)', inv20[0], g20, domain=sp.Interval(0, sp.oo)))
left20, right20 = g20.subs(x, 0), sp.limit(g20, x, sp.oo)
print(f'Задание 20: g(0) = {left20} достигается, предел {right20} — нет')
t('20-концы', left20 == -sp.pi / 2 and right20 == sp.pi / 2)
t('20b', check_domain('Task 20(b)', sp.Interval.Ropen(left20, right20),
                      D['Task 20(b)']))

print('=== задание на таймере ===')

# 21(b)(iii). При m = 1 замкнутая форма бессмысленна; сумма — нет.
sum21 = c * sp.Sum(m**r, (r, 0, n_ - 1)).doit()
at_one = sp.simplify(x + sum21.subs(m, 1))
print(f'Задание 21(b)(iii): при m = 1 постоянная равна {sum21.subs(m, 1)}')
t('21a', check_series('Task 21(b)(iii)', at_one, D['Task 21(b)(iii)']))
# 21(d). Предел не зависит от x — потому прямая и горизонтальна.
lim21 = sp.limit(closed.subs(m, R(1, 2)), n_, sp.oo)
print(f'Задание 21(d): при m = 1/2 предел равен {lim21}, x в нём нет')
t('21-предел без x', x not in lim21.free_symbols)
t('21b', check_expr('Task 21(d)', sp.simplify(c / (1 - m)), D['Task 21(d)']))
t('21-предел = неподвижная точка',
  sp.solve(sp.Eq(flin, x), x)[0] == sp.simplify(c / (1 - m)))
# 21(e). m = −1: нечётное и чётное n дают разные функции.
odd21 = sp.simplify(closed.subs({m: -1, n_: 7}))
even21 = sp.simplify(closed.subs({m: -1, n_: 8}))
print(f'Задание 21(e): при n = 7 это {odd21}, при n = 8 это {even21}')
t('21c', check_series('Task 21(e)(i)', odd21, D['Task 21(e)(i)']))
t('21d', check_series('Task 21(e)(ii)', even21, D['Task 21(e)(ii)']))
# Замыкание темы: f² = тождественная и есть f = f⁻¹.
f_self = -x + c
t('21-самообратность', sp.simplify(f_self.subs(x, f_self) - x) == 0)

print('=== что проверки отвергают ===')

# Неверная ветвь корня — главное, ради чего направление проверки выбрано так.
wrong_branch = -sp.sqrt(x**2 + 1)
ok_wrong, _ = silent(verify_inverse, '  −√(x²+1)', wrong_branch, f17,
                     domain=dom17)
t('ветвь: неверная отвергается', ok_wrong is False)
# А проверка в обратную сторону её пропускает: под квадратом знак исчезает.
passes_other_way = all(
    abs(complex(sp.N(f17.subs(x, wrong_branch.subs(x, v)))) - complex(v)) < 1e-9
    for v in (0.2, 0.7, 1.2, 1.6))
print('ветвь: f(g(x)) = x у неверной ветви выполняется — '
      f'{passes_other_way}, поэтому проверяется g(f(t)) = t')
t('ветвь: другое направление слепо', passes_other_way is True)

# Корпусная формула задания 19 отвергается сама по себе, без эталона.
corpus19 = (1 + sp.sqrt(x**2 + 4 * x)) / x
ok19, _ = silent(verify_inverse, '  корпусная', corpus19, g19,
                 domain=sp.Interval.open(3, 20))
t('корпус 19: отвергается', ok19 is False)
# И корпусная формула задания 17 — тоже.
corpus17 = 2 / x**2 + 1
ok17, _ = silent(verify_inverse, '  корпусная', corpus17, f17, domain=dom17)
t('корпус 17: отвергается', ok17 is False)

# check_domain: запись свободна, концы — нет.
same_set, _ = silent(check_domain, '  неравенством', (x >= 0) & (x <= sp.sqrt(3)),
                     D['Task 17(b)'])
open_end, _ = silent(check_domain, '  открытый конец',
                     sp.Interval.open(0, sp.sqrt(3)), D['Task 17(b)'])
t('check_domain: неравенство и Interval — одно', same_set is True)
t('check_domain: концы строгие', open_end is False)

print('=== пределы проверок ===')

# 1. verify_inverse ничего не знает про область самой обратной.
ok_pair, _ = silent(verify_inverse, '  верная формула', sp.sqrt(x**2 + 1), f17,
                    domain=dom17)
bad_dom, _ = silent(check_domain, '  но область названа неверно',
                    sp.Interval(0, 2), D['Task 17(b)'])
print('предел 1: формула проходит, а область рядом — нет; '
      'без check_domain ошибка в области осталась бы незамеченной')
t('предел 1', ok_pair is True and bad_dom is False)

# 2. verify_identity сверяет выражения, а не рассуждение: подстановка −x
# нигде не написана, но ответ проходит.
lazy, _ = silent(verify_identity, '  сразу f(x)', f8, f8)
print('предел 2: ответом на «show that f is even» принимается сам f(x) — '
      'балл там R1, за фразу, и проверка её не видит')
t('предел 2', lazy is True)

# 3. Порядок композиции проверкой не различается: у неверного порядка
# просто другой ответ, и подсказки, в чём дело, ученик не получит.
wrong_order, _ = silent(check_series, '  (f∘g) вместо (g∘f)', other2, D['Task 2'])
t('предел 3', wrong_order is False)
print('предел 3: неверный порядок отвергается как «не сходится», '
      'без слова о порядке — за это отвечает тренажёр')

# 4. check_series подставляет числа во все прочие буквы по алфавиту, поэтому
# единственную букву можно переименовать незаметно для проверки.
renamed, _ = silent(check_series, '  с буквой p вместо k',
                    (x - 3)**2 + sp.Symbol('p')**2, D['Task 2'])
print('предел 4: та же формула с переименованной буквой проходит — '
      'проверка сверяет значения, а условие называет букву k')
t('предел 4', renamed is True)

print('=== расхождения с корпусом ===')

gen = os.path.join(ROOT, 'classification/generated')


def blocks(zone, paper):
    path = os.path.join(gen, zone, 'deepseek-v4-pro', f'paper-{paper}.json')
    return {b['id'].split('-', 3)[3]: b for b in json.load(open(path))['blocks']}


# 1. Ноябрь 2023: в корпусе две зоны, в архиве одна бумага. Прошлые
# практикумы отмечали это только для Paper 3.
# Разбиение на блоки у двух прогонов местами разное (Q10(b) в одной копии
# один блок, в другой три), поэтому сверяются вопросы и баллы, а не имена.
same_papers = []
for paper in (1, 2, 3):
    s1, s2 = blocks('2023-november-tz1', paper), blocks('2023-november-tz2', paper)
    qs1 = {key.split('-Q')[1][:2] for key in s1}
    qs2 = {key.split('-Q')[1][:2] for key in s2}
    m1 = sum(bl['marks'] for bl in s1.values())
    m2 = sum(bl['marks'] for bl in s2.values())
    same = qs1 == qs2 and m1 == m2
    same_papers.append(same)
    print(f'ноябрь 2023, Paper {paper}: вопросы и баллы совпадают — {same}, '
          f'{m1} баллов против {m2}')
t('дубль: все три бумаги удвоены', all(same_papers))

try:
    import pymupdf
    CODES = ('7106', '7111', '7107', '7112', '7108', '7113')

    def paper_text(zone, paper):
        doc = pymupdf.open(os.path.join(
            ROOT, f'AA_HL/2023/November/{zone}/Paper {paper}/question-paper.pdf'))
        raw = '\n'.join(page.get_text() for page in doc)
        # Код бумаги — единственное содержательное отличие копий; вокруг
        # тире стоит тонкий пробел, поэтому вырезается только номер.
        for code in CODES:
            raw = raw.replace(code, '####')
        return raw

    def letters(text):
        # Только буквы и цифры. В Paper 2 у двух копий по-разному
        # извлекаются скобки векторных столбцов: TZ1 теряет их совсем,
        # TZ2 отдаёт кусками из области частного использования шрифта.
        # Содержание от этого не меняется, посимвольное сравнение ломается.
        return _re.sub('[^0-9A-Za-z]+', '', text)

    same1 = paper_text('TZ1', 1) == paper_text('TZ2', 1)
    print(f'ноябрь 2023, Paper 1: тексты вопросников совпадают посимвольно '
          f'(без кода бумаги) — {same1}')
    t('дубль: вопросник Paper 1 идентичен посимвольно', same1)
    same2 = letters(paper_text('TZ1', 2)) == letters(paper_text('TZ2', 2))
    print(f'ноябрь 2023, Paper 2: посимвольно — '
          f'{paper_text("TZ1", 2) == paper_text("TZ2", 2)}, '
          f'по буквам и цифрам — {same2}')
    t('дубль: вопросник Paper 2 идентичен по содержанию', same2)
    # Своей Paper 3 у зон нет вовсе: бумага одна, в каталоге Common.
    lone = [zone for zone in ('TZ1', 'TZ2', 'Common')
            if os.path.exists(os.path.join(
                ROOT, f'AA_HL/2023/November/{zone}/Paper 3'))]
    print(f'ноябрь 2023, Paper 3: лежит только в {lone}')
    t('дубль: Paper 3 в архиве одна', lone == ['Common'])
except ImportError:                                             # pragma: no cover
    print('pymupdf не установлен — сверка PDF пропущена')

# 2. Ноябрь 2021 Q2(d): у корпуса перевёрнут знаменатель, и вместе с ним
# уехал ответ. Единственная из четырёх ошибок, где неверен и ответ.
g_corpus = (a * x + 4) / (x - 3)
comp_corpus = sp.together(sp.simplify(g_corpus.subs(x, g_corpus)) - x)
a_corpus = sp.solve(sp.Poly(sp.numer(comp_corpus), x).all_coeffs(), a)
print(f'ноябрь 2021 Q2(d): по бумаге a = -3, по корпусной записи a = '
      f'{a_corpus[0][0]}')
t('корпус: перевёрнутый знаменатель даёт другой ответ', a_corpus == [(3,)])

# 3. Май 2022 TZ1 Q10: корпусную формулу опровергает пункт (c) той же
# бумаги — объём вращения π(h³/3 + h) получается только из √(x²+1).
h_ = sp.Symbol('h', positive=True)
vol = sp.integrate(sp.sqrt(x**2 + 1)**2, (x, 0, h_))
print(f'май 2022 TZ1 Q10: ∫₀^h (f⁻¹)² dx = {sp.simplify(vol)}, '
      f'в бумаге объём равен π(h³/3 + h)')
t('корпус: объём подтверждает √(x²+1)',
  sp.simplify(vol - (h_**3 / 3 + h_)) == 0)

# 4. Май 2022 TZ2 Q11: корпусная формула не возвращает то, что положено.
print(f'май 2022 TZ2 Q11: g(4) = 1/5; бумага возвращает '
      f'{sp.nsimplify(keep19[0].subs(x, probe))}, корпус — '
      f'{float(corpus19.subs(x, probe)):.4g}')
t('корпус: формула не отменяет g',
  abs(float(corpus19.subs(x, probe)) - 4) > 1)

# 5. Май 2021 TZ2 Q12: перевёрнутая дробь ломает и асимптоту, и монотонность,
# то есть противоречит тому, что напечатано в соседних пунктах.
f_corpus = sp.asin((1 - x**2) / (1 + x**2))
print(f'май 2021 TZ2 Q12: по бумаге предел {sp.limit(f8, x, sp.oo)}, '
      f'по корпусной записи {sp.limit(f_corpus, x, sp.oo)}')
t('корпус: асимптота меняет знак',
  sp.limit(f8, x, sp.oo) == sp.pi / 2
  and sp.limit(f_corpus, x, sp.oo) == -sp.pi / 2)
dec_paper = sp.diff(f8, x).subs(x, -1.5).evalf() < 0
dec_corpus = sp.diff(f_corpus, x).subs(x, -1.5).evalf() < 0
print(f'май 2021 TZ2 Q12: убывает при x < 0 — по бумаге {dec_paper}, '
      f'по корпусной записи {dec_corpus}')
t('корпус: монотонность тоже переворачивается',
  bool(dec_paper) is True and bool(dec_corpus) is False)
# Обе версии чётны, поэтому задание 8 корпусной ошибкой не задето.
t('корпус: чётность выживает в обеих записях',
  sp.simplify(f_corpus.subs(x, -x) - f_corpus) == 0)

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
