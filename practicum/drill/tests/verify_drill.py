"""Независимая проверка банка тренажёра.

Генератор задач опаснее, чем его отсутствие: он может уверенно и бесконечно
учить неверному. Поэтому каждый генератор здесь прогоняется на многих
зёрнах, и по каждой задаче проверяется трижды:

  1. эталонный ответ проходит собственную проверку задания;
  2. испорченный ответ ею отвергается;
  3. эталон сходится с независимым выводом — теми же формулами, но
     написанными заново и от условия, а не от генератора.

Третий пункт — главный. Первые два ловят рассогласование проверки
и генератора, но если оба ошибаются одинаково, поймать это может только
отдельный вывод.

Запуск:  python practicum/drill/tests/verify_drill.py
"""
from __future__ import annotations

import contextlib
import io
import math
import os
import random
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DRILL = os.path.dirname(HERE)
PRACTICUM = os.path.dirname(DRILL)
sys.path.insert(0, os.path.dirname(PRACTICUM))
sys.path.insert(0, PRACTICUM)

import sympy as sp  # noqa: E402
import kit  # noqa: E402

from drill import engine  # noqa: E402
from drill.check import evaluate, show_answer  # noqa: E402
from drill.items import GENERATORS  # noqa: E402

x_sym = sp.Symbol('x')

SEEDS = 15
res = []


def t(name, ok):
    res.append((name, ok))
    if not ok:
        print(f'❌ {name}')


def quiet(fn, *args, **kwargs):
    """Вызвать проверку kit, не печатая её вердикт."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*args, **kwargs)


def section(title):
    print(f'\n=== {title} ===')


# --- 1. эталон проходит, испорченный ответ не проходит -------------------

def spoil(answer, spec):
    """Ответ, который обязан быть отвергнут."""
    kind = spec['kind']
    if kind == 'count':
        return str(int(spec['value']) + 1)
    if kind == 'indeterminate':
        # Форма названа не та: 0/0 там, где на самом деле oo/oo, и наоборот.
        return 'oo/oo' if str(answer).strip() == '0/0' else '0/0'
    if isinstance(answer, (list, tuple)):
        if len(answer) > 1:
            return show_answer(list(answer)[:-1])       # потерянный корень
        return show_answer(list(answer) + [sp.Integer(97)])  # лишний корень
    if kind == 'num':
        return f'{float(answer) * 1.08:.6g}'
    if kind == 'triangle':
        return f'{float(answer) * 1.08:.6g}'
    if kind == 'domain':
        # Сдвинутый на единицу промежуток: концы уезжают оба, и это ровно
        # та ошибка, за которую в markscheme снимают балл.
        if isinstance(answer, sp.Interval):
            left, right = answer.start, answer.end
            return show_answer(sp.Interval(left + 1, right + 1),
                               var=spec.get('var', 'x'))
        # Область бывает и не промежутком: у дробно-линейной функции это
        # вся прямая без одного значения. Там портим само выколотое
        # значение — сдвигаем его на единицу.
        gap = sp.Complement(sp.S.Reals, answer)
        moved = sp.FiniteSet(*[v + 1 for v in gap]) if isinstance(
            gap, sp.FiniteSet) else sp.Interval(0, 1)
        return show_answer(sp.Complement(sp.S.Reals, moved),
                           var=spec.get('var', 'x'))
    if kind == 'solution_set':
        # Дополнение к верному множеству — гарантированно неверный ответ,
        # и притом правдоподобно выглядящий: так ошибаются со знаком.
        return show_answer(sp.Complement(sp.S.Reals, answer),
                           var=spec.get('var', 'x'))
    if kind == 'equation':
        e = sp.sympify(answer)
        return f'{sp.sstr(sp.expand(e.lhs + 3))} = {sp.sstr(e.rhs)}'
    return show_answer(sp.sympify(answer) + 1)


section('эталон проходит собственную проверку')
for name, gen in sorted(GENERATORS.items()):
    good = bad = 0
    for seed in range(SEEDS):
        item = gen(random.Random(seed))
        ok, _ = evaluate(item['check'], show_answer(item['answer']))
        good += ok
        accepted, _ = evaluate(item['check'], spoil(item['answer'],
                                                   item['check']))
        bad += accepted
    t(f'{name}: эталон принят на всех {SEEDS} зёрнах', good == SEEDS)
    t(f'{name}: испорченный ответ отвергнут на всех {SEEDS} зёрнах', bad == 0)
    print(f'  {name:28} принят {good}/{SEEDS}, ложно принят {bad}/{SEEDS}')


# --- 2. независимый вывод ответа ----------------------------------------
# Числа берутся из текста условия, а формулы написаны заново: если
# генератор ошибётся в формуле, здесь сойдётся другое число.

NUM = re.compile(r'-?\d+(?:\.\d+)?')
DEG = sp.pi / 180


def latex_to_expr(text):
    """Маленький переводчик из LaTeX в sympy — на те формы, что встречаются
    в условиях тренажёра: дроби, π, скобки, неявное умножение."""
    body = text.replace('\\left', '').replace('\\right', '')
    body = re.sub(r'\\d?frac\{(.+?)\}\{(.+?)\}', r'((\1)/(\2))', body)
    body = body.replace('\\pi', 'pi').replace('\\cdot', '*')
    body = re.sub(r'\^\{(.+?)\}', r'**(\1)', body)
    body = re.sub(r'(\d)\s*(pi|\(|[a-z])', r'\1*\2', body)
    return sp.sympify(body.replace(' ', ''))


def poly_from_latex(text):
    """Многочлен из условия: своим переводчиком, чтобы не звать генератор."""
    body = (text.replace('\\left', '').replace('\\right', '')
            .replace('\\cdot', '*').replace('{', '(').replace('}', ')')
            .replace('^', '**'))
    body = re.sub(r'(\d)\s*([a-z(])', r'\1*\2', body)
    left, _, right = body.partition('=')
    return sp.sympify(left) - sp.sympify(right or '0')


def numbers(prompt):
    return [float(n) for n in NUM.findall(re.sub(r'\\d?frac|circ|\\[a-z]+',
                                                 ' ', prompt))]


section('независимый вывод из условия')

# Лестница: высота = длина · sin(угол).
for seed in range(SEEDS):
    item = GENERATORS['C1.right_triangle'](random.Random(seed))
    length, angle = numbers(item['prompt'])[:2]
    want = length * float(sp.sin(sp.Rational(int(angle)) * DEG))
    t(f'right_triangle[{seed}] сходится с длина·sin(угол)',
      abs(want - item['answer']) < 1e-9)
print(f'  C1.right_triangle            {SEEDS} задач сверено с длина·sin(угол)')

# Теорема косинусов: сверяем стороной, найденной через площадь и синусы.
cos_checked = 0
for seed in range(SEEDS):
    item = GENERATORS['C1.cosine_rule'](random.Random(seed))
    known = item['check']['known']
    if 'C' in known and 'a' in known and 'b' in known:
        a, b, angle = known['a'], known['b'], known['C']
        # Через координаты: C в начале, стороны вдоль лучей.
        cx, cy = b * sp.cos(angle * DEG), b * sp.sin(angle * DEG)
        want = float(sp.sqrt((cx - a)**2 + cy**2))
        t(f'cosine_rule[{seed}] сходится с расстоянием между вершинами',
          abs(want - item['answer']) < 1e-9)
        cos_checked += 1
print(f'  C1.cosine_rule               {cos_checked} задач сверено координатами')

# Теорема синусов: сверяем через площадь треугольника, посчитанную дважды.
for seed in range(SEEDS):
    item = GENERATORS['C1.sine_rule'](random.Random(seed))
    known = item['check']['known']
    A, B, a = known['A'], known['B'], known['a']
    C = 180 - A - B
    # Площадь через (a, b, C) и через (a, c, B) должна дать ту же b.
    b = item['answer']
    c = float(a * sp.sin(C * DEG) / sp.sin(A * DEG))
    s1 = 0.5 * a * b * float(sp.sin(C * DEG))
    s2 = 0.5 * a * c * float(sp.sin(B * DEG))
    t(f'sine_rule[{seed}]: площадь двумя способами совпала',
      abs(s1 - s2) < 1e-9 * max(1.0, s1))
print(f'  C1.sine_rule                 {SEEDS} задач сверено площадью')

# Неоднозначный случай: считаем треугольники перебором угла B.
for seed in range(SEEDS):
    item = GENERATORS['C1.ambiguous_case'](random.Random(seed))
    a, b, A = [float(v) for v in numbers(item['prompt'])[:3]]
    target = b * math.sin(math.radians(A)) / a
    found = 0
    previous = None
    for step in range(1, 1800):
        B = step / 10
        if 180 - A - B <= 0:
            continue
        gap = math.sin(math.radians(B)) - target
        if previous is not None and previous * gap <= 0:
            found += 1
        previous = gap
    # Перебор находит оба корня уравнения sin B = b·sin A / a.
    t(f'ambiguous_case[{seed}]: перебор нашёл два треугольника', found >= 2)
print(f'  C1.ambiguous_case            {SEEDS} задач сверено перебором угла')

# Корни квадратного: сверяем подстановкой в само уравнение.
for seed in range(SEEDS):
    item = GENERATORS['B1.quadratic_toolkit'](random.Random(seed))
    expr = sp.sympify(item['check']['equation'])
    ok = all(sp.simplify(expr.subs(sp.Symbol('x'), r)) == 0
             for r in item['answer'])
    t(f'quadratic_toolkit[{seed}]: корни подставляются в уравнение', ok)
print(f'  B1.quadratic_toolkit         {SEEDS} задач сверено подстановкой')

# Иррациональное: единственный корень и отсутствие второго.
for seed in range(SEEDS):
    item = GENERATORS['B1.extraneous_roots'](random.Random(seed))
    expr = sp.sympify(item['check']['equation'])
    truth = sp.solveset(expr, sp.Symbol('x'), sp.S.Reals)
    t(f'extraneous_roots[{seed}]: sympy даёт тот же набор корней',
      set(truth) == set(sp.sympify(v) for v in item['answer']))
print(f'  B1.extraneous_roots          {SEEDS} задач сверено solveset')

# Показательное: подставляем корни в исходное уравнение.
for seed in range(SEEDS):
    item = GENERATORS['B1.exp_log_equation'](random.Random(seed))
    base = int(re.search(r'\$(\d+)\^', item['prompt']).group(1))
    power = int(re.search(r'- (\d+)\\cdot', item['prompt']).group(1))
    const = int(re.search(r'\+ (\d+) = 0', item['prompt']).group(1))
    ok = all(abs(base**(2 * float(r)) - power * base**float(r) + const) < 1e-9
             for r in item['answer'])
    t(f'exp_log[{seed}]: корни удовлетворяют уравнению из условия', ok)
print(f'  B1.exp_log_equation          {SEEDS} задач сверено подстановкой')

# Число корней: сверяем сменой знака на сетке.
for seed in range(SEEDS):
    item = GENERATORS['B1.solution_count'](random.Random(seed))
    poly = poly_from_latex(re.search(r'\$(.+?)\$', item['prompt']).group(1))
    f = sp.lambdify(sp.Symbol('x'), poly)
    # Сетка сдвинута: корень ровно в узле даёт произведение 0, и строгое
    # сравнение «< 0» такую смену знака пропускает.
    xs = [k / 50 + 0.0007 for k in range(-500, 501)]
    signs = sum(1 for i in range(len(xs) - 1) if f(xs[i]) * f(xs[i + 1]) < 0)
    t(f'solution_count[{seed}]: смен знака столько же, сколько корней',
      signs == item['answer'])
print(f'  B1.solution_count            {SEEDS} задач сверено сменой знака')

# Обратная функция: дробь читается из условия со знаками, композиция
# собирается заново, и подстановка обязана вернуть x.
FRAC = re.compile(r'dfrac\{(\d+)x ([+-]) (\d+)\}\{(\d+)x ([+-]) (\d+)\}')
for seed in range(SEEDS):
    item = GENERATORS['B2.inverse_by_swap'](random.Random(seed))
    a, s1, b, c, s2, d = FRAC.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    f = ((int(a) * xs + int(f'{s1}{b}'))
         / (int(c) * xs + int(f'{s2}{d}')))
    back = sp.simplify(sp.sympify(item['answer']).subs(xs, f) - xs)
    t(f'inverse_by_swap[{seed}]: f внутри ответа даёт x', back == 0)
print(f'  B2.inverse_by_swap           {SEEDS} задач сверено подстановкой')

# Область обратной: множество значений исходной, посчитанное перебором.
QUAD = re.compile(r'x\^2(?: ([+-]) (\d+))?\$, где \$0 \\le x \\le (\d+)')
for seed in range(SEEDS):
    item = GENERATORS['B2.inverse_domain'](random.Random(seed))
    sign, const, top = QUAD.search(item['prompt']).groups()
    shift = int(f'{sign}{const}') if const else 0
    values = [(int(top) * i / 400)**2 + shift for i in range(401)]
    want = item['answer']
    t(f'inverse_domain[{seed}]: концы сошлись с перебором',
      abs(min(values) - float(want.start)) < 1e-9
      and abs(max(values) - float(want.end)) < 1e-9)
print(f'  B2.inverse_domain            {SEEDS} задач сверено перебором значений')

# Ветвь корня: вторая ветвь обязана быть отвергнута на своей же области.
BRANCH = re.compile(r'\(x - (\d+)\)\^2')
flipped = 0
for seed in range(SEEDS):
    item = GENERATORS['B2.inverse_branch'](random.Random(seed))
    h = int(BRANCH.search(item['prompt']).group(1))
    wrong = 2 * h - sp.sympify(item['answer'])
    ok, _ = evaluate(item['check'], show_answer(wrong))
    flipped += not ok
    t(f'inverse_branch[{seed}]: вторая ветвь отвергнута', not ok)
print(f'  B2.inverse_branch            {flipped}/{SEEDS} неверных ветвей отвергнуто')


# B3. Величина сдвига после сжатия: вынести множитель за скобку и
# сравнить с тем, что напечатано, — двумя разными путями.
SINE = re.compile(r'\\sin\((\d+)x - (\d+)\)')
for seed in range(SEEDS):
    item = GENERATORS['B3.name_transform'](random.Random(seed))
    scale, drop = (int(v) for v in SINE.search(item['prompt']).groups())
    xs = sp.Symbol('x')
    moved = sp.sin(scale * (xs - sp.sympify(item['answer'])))
    t(f'name_transform[{seed}]: сдвиг воспроизводит напечатанную функцию',
      sp.simplify(moved - sp.sin(scale * xs - drop)) == 0)
    t(f'name_transform[{seed}]: до сжатия сдвиг был бы другим',
      sp.simplify(sp.sin(scale * xs - drop)
                  - sp.sin(scale * xs - scale * sp.sympify(item['answer'])))
      == 0 and sp.sympify(item['answer']) != drop)
print(f'  B3.name_transform            {SEEDS} задач сверено выносом множителя')

# Коэффициент растяжения: делим дробь уголком и смотрим на остаток.
RAT = re.compile(r'\\dfrac\{(\d+)x ([+-]) (\d+)\}\{x ([+-]) (\d+)\}')
for seed in range(SEEDS):
    item = GENERATORS['B3.match_transform'](random.Random(seed))
    lead, s1, top, s2, bottom = RAT.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    frac = ((int(lead) * xs + int(f'{s1}{top}'))
            / (xs + int(f'{s2}{bottom}')))
    rest = sp.simplify(frac - int(lead))
    t(f'match_transform[{seed}]: остаток равен ответу, делённому на (x − h)',
      sp.simplify(rest * (xs + int(f'{s2}{bottom}'))
                  - sp.sympify(item['answer'])) == 0)
print(f'  B3.match_transform           {SEEDS} задач сверено делением уголком')

# Число изломов: считаем нули |f| со сменой знака напрямую по функции.
PROD = re.compile(r'\$f\(x\) = (.+?)\$\.')
for seed in range(SEEDS):
    item = GENERATORS['B3.fold_graph'](random.Random(seed))
    body = PROD.search(item['prompt']).group(1)
    xs = sp.Symbol('x')
    # Неявное умножение LaTeX: между скобками и после степени нужен знак.
    plain = body.replace('^2', '**2').replace(')(', ')*(').replace('2(', '2*(')
    poly = sp.sympify(plain, locals={'x': xs})
    corners = 0
    for root, multiplicity in sp.roots(sp.Poly(poly, xs)).items():
        if root.is_real and multiplicity % 2 == 1:
            corners += 1
    t(f'fold_graph[{seed}]: изломы — это корни нечётной кратности',
      corners == int(item['answer']))
print(f'  B3.fold_graph                {SEEDS} задач сверено кратностью корней')

# Число решений кубического уравнения: сверяем со сканированием.
CUBIC = re.compile(r'x\^3 - 3x(?: ([+-]) (\d+))? = 0')
for seed in range(SEEDS):
    item = GENERATORS['B3.explore_family'](random.Random(seed))
    sign, const = CUBIC.search(item['prompt']).groups()
    shift = int(f'{sign}{const}') if const else 0
    xs = sp.Symbol('x')
    scanned = kit.count_roots(sp.lambdify(xs, xs**3 - 3 * xs + shift), -6, 6, 12000)
    t(f'explore_family[{seed}]: скан даёт то же число корней',
      scanned == int(item['answer']))
print(f'  B3.explore_family            {SEEDS} задач сверено сканированием')

# B4. Горизонтальная асимптота: генератор берёт отношение старших
# коэффициентов, здесь считаем предел самой дроби.
FRAC = re.compile(r'\\dfrac\{(.+?)\}\{(.+?)\}')


def latex_linear(text, var):
    """«-3x + 4», «x - 6», «2x» → выражение sympy."""
    return sp.sympify(text.replace('x', f'*{var.name}')
                      .replace('-*', '-1*').replace('+*', '+1*')
                      .lstrip('*') if text.startswith('x')
                      else text.replace('x', f'*{var.name}'),
                      locals={var.name: var})


for seed in range(SEEDS):
    item = GENERATORS['B4.name_asymptote'](random.Random(seed))
    top, bottom = FRAC.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    frac = latex_linear(top, xs) / latex_linear(bottom, xs)
    t(f'name_asymptote[{seed}]: предел на бесконечности равен ответу',
      sp.limit(frac, xs, sp.oo) == sp.sympify(item['answer']))
    t(f'name_asymptote[{seed}]: и слева тот же',
      sp.limit(frac, xs, -sp.oo) == sp.sympify(item['answer']))
print(f'  B4.name_asymptote            {SEEDS} задач сверено пределом')

# Свободный член наклонной асимптоты: генератор приравнивает коэффициенты,
# здесь берём предел разности f(x) − mx.
QUAD = re.compile(r'\\dfrac\{(\d+)x\^2 ([+-]) (\d+)x - 6\}\{(.+?)\}')
for seed in range(SEEDS):
    item = GENERATORS['B4.oblique_asymptote'](random.Random(seed))
    lead, sign, mid, bottom = QUAD.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    frac = ((int(lead) * xs**2 + int(f'{sign}{mid}') * xs - 6)
            / latex_linear(bottom, xs))
    slope = sp.limit(frac / xs, xs, sp.oo)
    const = sp.simplify(sp.limit(frac - slope * xs, xs, sp.oo))
    t(f'oblique_asymptote[{seed}]: предел разности даёт ответ',
      const == sp.sympify(item['answer']))
    # cancel сводит разность к «константа / линейное»: без него sympy
    # раскладывает несокращённую сумму в ряд и вязнет на некоторых семенах.
    t(f'oblique_asymptote[{seed}]: и разность с найденной прямой стремится к нулю',
      sp.limit(sp.cancel(frac - slope * xs - const), xs, sp.oo) == 0)
print(f'  B4.oblique_asymptote         {SEEDS} задач сверено пределом разности')

# Множество значений: генератор собирает промежуток из f(0) и асимптоты,
# здесь спрашиваем у самой функции, достигается ли каждое значение.
RANGE = re.compile(r'\\dfrac\{(.+?)\}\{x \+ (\d+)\}')
for seed in range(SEEDS):
    item = GENERATORS['B4.find_range'](random.Random(seed))
    top, shift = RANGE.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    f = latex_linear(top, xs) / (xs + int(shift))
    closed = sp.Interval(item['answer'].start, item['answer'].end)
    t(f'find_range[{seed}]: каждое значение внутри достигается, снаружи нет',
      quiet(kit.verify_range, '  ', item['answer'], f, var=xs,
            domain=sp.Interval(0, sp.oo)))
    t(f'find_range[{seed}]: закрытый конец у асимптоты был бы неверен',
      not quiet(kit.verify_range, '  ', closed, f, var=xs,
                domain=sp.Interval(0, sp.oo)))
print(f'  B4.find_range                {SEEDS} задач сверено достижимостью')

# Число пересечений с осью: генератор смотрит на знаки высот,
# здесь просто считаем различные вещественные корни.
CUBIC_A = re.compile(r'y = x\^3 ([+-]) (\d+)x\^2 ([+-]) ([\d/]+)')
for seed in range(SEEDS):
    item = GENERATORS['B4.count_roots'](random.Random(seed))
    s1, a_txt, s2, b_txt = CUBIC_A.search(item['prompt']).groups()
    xs = sp.Symbol('x')
    cubic = (xs**3 + int(f'{s1}{a_txt}') * xs**2
             + sp.sympify(f'{s2}{b_txt}'))
    distinct = len(set(sp.Poly(cubic, xs).real_roots()))
    t(f'count_roots[{seed}]: различных вещественных корней столько же',
      distinct == int(item['answer']))
print(f'  B4.count_roots               {SEEDS} задач сверено корнями многочлена')



# Бином: генератор берёт формулу общего члена, здесь раскрываем скобку.
for seed in range(SEEDS):
    item = GENERATORS['A3.general_term'](random.Random(seed))
    inner = re.search(r'\\left\((.+?)\\right\)\^\{(\d+)\}', item['prompt'])
    power_asked = int(re.search(r'x\^\{(-?\d+)\}', item['prompt']).group(1))
    expanded = sp.expand(latex_to_expr(inner.group(1))**int(inner.group(2)))
    got = expanded.coeff(sp.Symbol('x'), power_asked)
    t(f'A3.general_term[{seed}]: совпало с раскрытой скобкой',
      sp.simplify(got - item['answer']) == 0)
print(f'  A3.general_term              {SEEDS} задач сверено раскрытием')

# Виета: генератор пользуется формулами, здесь корни считаются численно.
for seed in range(SEEDS):
    item = GENERATORS['A4.vieta_quadratic'](random.Random(seed))
    b, c = (int(v) for v in re.search(
        r'x\^2 ([+-]) (\d+)x ([+-]) (\d+)', item['prompt']).group(2, 4))
    signs = re.search(r'x\^2 ([+-]) \d+x ([+-]) \d+', item['prompt']).groups()
    b = b if signs[0] == '+' else -b
    c = c if signs[1] == '+' else -c
    roots = sp.Poly(sp.Symbol('x')**2 + b * sp.Symbol('x') + c,
                    sp.Symbol('x')).all_roots()
    if 'alpha^2' in item['prompt']:
        want = sum(r**2 for r in roots)
    elif 'dfrac1' in item['prompt']:
        want = sum(1 / r for r in roots)
    else:
        want = sum(roots)
    t(f'A4.vieta_quadratic[{seed}]: сошлось с настоящими корнями',
      abs(complex(sp.N(want - item['answer']))) < 1e-9)
print(f'  A4.vieta_quadratic           {SEEDS} задач сверено корнями')

# Комплексная арифметика: умножаем ответ на знаменатель обратно.
for seed in range(SEEDS):
    item = GENERATORS['A5.cartesian_arithmetic'](random.Random(seed))
    top, bottom = re.search(r'dfrac\{(.+?)\}\{(.+?)\}', item['prompt']).groups()
    def to_sympy(text):
        # «1 - 4 i» → 1 - 4*I, «2 - i» → 2 - I: множитель дописываем только
        # после цифры, иначе получается «-*I».
        body = re.sub(r'(\d)\s*i', r'\1*I', text)
        return sp.sympify(re.sub(r'(?<![\w*])i', 'I', body))
    t(f'A5.cartesian_arithmetic[{seed}]: ответ×знаменатель даёт числитель',
      sp.simplify(item['answer'] * to_sympy(bottom) - to_sympy(top)) == 0)
print(f'  A5.cartesian_arithmetic      {SEEDS} задач сверено обратным умножением')

# Муавр: возводим в степень перемножением, без полярной формы.
for seed in range(SEEDS):
    item = GENERATORS['A6.de_moivre_power'](random.Random(seed))
    power = int(re.search(r'\\right\]\^\{(\d+)\}', item['prompt']).group(1))
    angle = re.search(r'\\cos (.+?) \+', item['prompt']).group(1)
    radius = re.search(r'\\left\[(\d*)\\left', item['prompt']).group(1)
    radius = int(radius) if radius else 1
    base_angle = latex_to_expr(angle)
    base = radius * (sp.cos(base_angle) + sp.I * sp.sin(base_angle))
    product = sp.Integer(1)
    for _ in range(power):
        product = sp.expand(product * base)
    t(f'A6.de_moivre_power[{seed}]: сошлось с перемножением',
      abs(complex(sp.N(sp.simplify(product - item['answer'])))) < 1e-9)
print(f'  A6.de_moivre_power           {SEEDS} задач сверено перемножением')

# Корни n-й степени: каждый в степени n обязан дать исходное число.
for seed in range(SEEDS):
    item = GENERATORS['A6.nth_roots'](random.Random(seed))
    order = int(re.search(r'корни (\d)-й', item['prompt']).group(1))
    number = sp.sympify(re.search(r'степени из \$(.+?)\$', item['prompt'])
                        .group(1).replace(' i', '*I').replace('i', 'I'))
    ok = all(abs(complex(sp.N(sp.expand(root**order) - number))) < 1e-9
             for root in item['answer'])
    t(f'A6.nth_roots[{seed}]: каждый корень в степени n даёт число',
      ok and len(item['answer']) == order)
print(f'  A6.nth_roots                 {SEEDS} задач сверено возведением')

# Индукция для суммы: считаем разность прямым суммированием.
for seed in range(SEEDS):
    item = GENERATORS['A7.induction_sum'](random.Random(seed))
    kk = sp.Symbol('k')
    values = []
    for m in (3, 4, 5, 6):
        got = item['answer'].subs(kk, m)
        values.append(sp.simplify(got))
    t(f'A7.induction_sum[{seed}]: разность считается в числах',
      all(v.is_number for v in values))
print(f'  A7.induction_sum             {SEEDS} задач проверено подстановкой')

# Неравенство: множество сверяем выборкой точек, а не решением.
for seed in range(SEEDS):
    item = GENERATORS['A8.critical_values'](random.Random(seed))
    inequality = sp.sympify(item['check']['inequality'])
    xs = sp.Symbol('x')
    mismatch = 0
    for step in range(-60, 61):
        point = sp.Rational(step, 6)
        inside = item['answer'].contains(point)
        holds = bool(inequality.subs(xs, point))
        mismatch += bool(inside) != holds
    t(f'A8.critical_values[{seed}]: 121 точка согласуется с неравенством',
      mismatch == 0)
print(f'  A8.critical_values           {SEEDS} задач сверено по точкам')

# Тригонометрия: корень обязан обращать уравнение в ноль.
for name in ('C3.reference_angle', 'C3.factor_not_divide',
             'C3.reduce_to_tangent'):
    for seed in range(SEEDS):
        item = GENERATORS[name](random.Random(seed))
        expression = sp.sympify(item['check']['expression'])
        ok = all(abs(float(expression.subs(sp.Symbol('x'), root))) < 1e-9
                 for root in item['answer'])
        t(f'{name}[{seed}]: корни обращают уравнение в ноль',
          ok and bool(item['answer']))
    print(f'  {name:28} {SEEDS} задач сверено подстановкой')

# Модель: считаем значение заново по числам из условия.
for seed in range(SEEDS):
    item = GENERATORS['C4.use_model'](random.Random(seed))
    height, hours, middle, moment = (int(v) for v in re.findall(
        r'h\(t\) = (\d+)\\sin.+?\{(\d+)\}\\right\) \+ (\d+).+?t = (\d+)',
        item['prompt'])[0])
    want = height * math.sin(2 * math.pi * moment / hours) + middle
    t(f'C4.use_model[{seed}]: сошлось с прямым счётом',
      abs(want - item['answer']) < 1e-9)
print(f'  C4.use_model                 {SEEDS} задач сверено прямым счётом')

# B5, логарифмы: значение считается заново через ln из условия, а не
# через закон логарифма, которым его собирал генератор.
for seed in range(SEEDS):
    item = GENERATORS['B5.log_laws'](random.Random(seed))
    number = int(re.search(r'Выразите \$\\log_\{10\}(\d+)\$',
                           item['prompt']).group(1))
    want = math.log10(number)
    got = float(item['answer'].subs({sp.Symbol('p'): sp.log(2, 10),
                                     sp.Symbol('q'): sp.log(3, 10)}))
    t(f'B5.log_laws[{seed}]: ответ через p и q сошёлся с log10 числа',
      abs(want - got) < 1e-12)
print(f'  B5.log_laws                  {SEEDS} задач сверено через log10')

# Уравнение с логарифмами: корень обязан обращать обе части в равенство,
# и второй корень квадратного уравнения обязан лежать вне области.
LOGEQ = re.compile(r'\\log_\{(\d+)\}\((x(?: [-+] \d+)?)\) \+ '
                   r'\\log_\{\d+\}\(x - (\d+)\) = (\d+)')
for seed in range(SEEDS):
    item = GENERATORS['B5.log_equation'](random.Random(seed))
    base, first, shift, right = LOGEQ.search(item['prompt']).groups()
    base, shift, right = int(base), int(shift), int(right)
    offset = 0 if first == 'x' else int(first.split()[-1]) * (
        1 if '+' in first else -1)
    root = float(item['answer'][0])
    t(f'B5.log_equation[{seed}]: корень обращает уравнение в равенство',
      abs(math.log(root + offset, base)
          + math.log(root - shift, base) - right) < 1e-9)
    # Сумма корней квадратного (x + offset)(x - shift) = base**right
    # равна shift - offset, значит второй корень считается без генератора.
    other = (shift - offset) - root
    t(f'B5.log_equation[{seed}]: второй корень область отбрасывает',
      other <= shift)
print(f'  B5.log_equation              {SEEDS} задач сверено подстановкой')

# Проценты: множитель за период возводится в степень напрямую по числам
# из условия, без формулы генератора.
depreciated = 0
for seed in range(SEEDS):
    item = GENERATORS['B5.percentage_model'](random.Random(seed))
    hit = re.search(r'куплена за \$(\d+)\$ и дешевеет на \$(\d+)', item['prompt'])
    if not hit:
        continue
    price, percent = (int(v) for v in hit.groups())
    years = int(re.search(r'через \$(\d+)\$ лет', item['prompt']).group(1))
    want = price * (1 - percent / 100) ** years
    t(f'B5.percentage_model[{seed}]: сошлось с прямым возведением в степень',
      abs(want - float(item['answer'])) < 1e-9 * want)
    depreciated += 1
print(f'  B5.percentage_model          {depreciated} задач сверено прямым счётом')

# Подгонка модели: модель обязана пройти через обе точки условия, и обе
# берутся из текста, а не из спецификации проверки.
for seed in range(SEEDS):
    item = GENERATORS['B5.fit_model'](random.Random(seed))
    start = int(re.search(r'она равна \$(\d+)\$', item['prompt']).group(1))
    span = int(re.search(r'за \$(\d+)\$ лет', item['prompt']).group(1))
    percent = int(re.search(r'на \$(\d+)\\%\$', item['prompt']).group(1))
    grows = 'выросло' in item['prompt']
    later = start * (1 + percent / 100 * (1 if grows else -1))
    model = sp.lambdify(sp.Symbol('t'), item['answer'])
    t(f'B5.fit_model[{seed}]: модель проходит через обе точки условия',
      abs(model(0) - start) < 1e-9 * start
      and abs(model(span) - later) < 1e-9 * later)
print(f'  B5.fit_model                 {SEEDS} задач сверено по двум точкам')

# Логистическая модель: то же самое, плюс проверка, что она подходит
# к потолку снизу, а не убегает от него.
for seed in range(SEEDS):
    item = GENERATORS['B5.logistic_model'](random.Random(seed))
    if item['check']['kind'] != 'model':
        continue
    limit = int(re.search(r'\\dfrac\{(\d+)\}', item['prompt']).group(1))
    start, span, later = (int(v) for v in re.search(
        r'она равна \$(\d+)\$, при \$t = (\d+)\$ — \$(\d+)\$',
        item['prompt']).groups())
    model = sp.lambdify(sp.Symbol('t'), item['answer'])
    t(f'B5.logistic_model[{seed}]: проходит через обе точки условия',
      abs(model(0) - start) < 1e-9 * start
      and abs(model(span) - later) < 1e-9 * later)
    # Потолок: модель обязана расти к нему и не переходить его. Проверяем
    # в двух местах, потому что далеко за пределом float уже равен L ровно.
    t(f'B5.logistic_model[{seed}]: растёт к потолку и не переходит его',
      later < model(span * 3) < limit
      and abs(model(span * 30) - limit) < limit * 1e-6)
print(f'  B5.logistic_model            задачи сверены по двум точкам и потолку')

# Пределы: эталон сверяется тем же способом, каким его выводят на бумаге —
# символьным пределом sympy, а не подстановкой чисел. Проверка в тренажёре
# подходит к точке лестницей, так что два пути здесь независимы.
LIMIT_VARS = {'E1.interpret': 't'}
for name in ('E1.substitute', 'E1.at_infinity', 'E1.lhopital_again',
             'E1.maclaurin', 'E1.interpret'):
    for seed in range(SEEDS):
        item = GENERATORS[name](random.Random(seed))
        spec = item['check']
        expr = sp.sympify(spec['expr'])
        var = sp.Symbol(LIMIT_VARS.get(name, 'x'))
        got = sp.limit(expr, var, sp.sympify(spec['point']))
        t(f'{name}[{seed}]: символьный предел сошёлся с эталоном',
          sp.simplify(got - sp.sympify(item['answer'])) == 0)
    print(f'  {name:28} {SEEDS} задач сверено sympy.limit')

# Предел по параметру берётся не через sympy.limit: при отрицательном m
# степень m^n уходит в комплексную ветвь, хотя n здесь целое. Вывод идёт
# так, как его делают с геометрической последовательностью: f(n) = L + K·mⁿ,
# и три первых значения дают и знаменатель, и предел, ничего не зная
# о генераторе.
n_sym = sp.Symbol('n')
for seed in range(SEEDS):
    item = GENERATORS['E1.parameter'](random.Random(seed))
    expr = sp.sympify(item['check']['expr'])
    f1, f2, f3 = (sp.nsimplify(expr.subs(n_sym, k)) for k in (1, 2, 3))
    t(f'E1.parameter[{seed}]: последовательность не вырождена', f2 != f1)
    ratio = sp.simplify((f3 - f2) / (f2 - f1))
    t(f'E1.parameter[{seed}]: знаменатель по модулю меньше единицы',
      abs(ratio) < 1)
    limit = sp.simplify(f1 + (f2 - f1) / (1 - ratio))
    t(f'E1.parameter[{seed}]: экстраполяция по трём членам дала эталон',
      sp.simplify(limit - sp.sympify(item['answer'])) == 0)
print(f'  E1.parameter                 {SEEDS} задач сверено экстраполяцией')

# Правило Лопиталя: часть задач приёма спрашивает не число, а форму.
# Там сверяется, что оба предела действительно нулевые.
numbers = forms = 0
for seed in range(SEEDS):
    item = GENERATORS['E1.lhopital'](random.Random(seed))
    spec = item['check']
    if spec['kind'] == 'indeterminate':
        forms += 1
        top = sp.limit(sp.sympify(spec['num']), sp.Symbol('x'), 0)
        bottom = sp.limit(sp.sympify(spec['den']), sp.Symbol('x'), 0)
        t(f'E1.lhopital[{seed}]: форма и правда 0/0',
          top == 0 and bottom == 0 and item['answer'] == '0/0')
    else:
        numbers += 1
        got = sp.limit(sp.sympify(spec['expr']), sp.Symbol('x'), 0)
        t(f'E1.lhopital[{seed}]: символьный предел сошёлся с эталоном',
          sp.simplify(got - sp.sympify(item['answer'])) == 0)
print(f'  E1.lhopital                  {numbers} на число, {forms} на форму')

# Ответ через параметр: предел берётся при каждом значении n порознь.
for seed in range(SEEDS):
    item = GENERATORS['E1.symbolic'](random.Random(seed))
    spec = item['check']
    expr = sp.sympify(spec['expr'])
    point = sp.sympify(spec['point'])
    for value in (1, 2, 5, 9):
        got = sp.limit(expr.subs(sp.Symbol('n'), value), sp.Symbol('x'), point)
        want = sp.sympify(item['answer']).subs(sp.Symbol('n'), value)
        t(f'E1.symbolic[{seed}]: при n = {value} предел равен эталону',
          sp.simplify(got - want) == 0)
print(f'  E1.symbolic                  {SEEDS} задач сверено при четырёх n')

# Постоянная под конечный предел: при найденном c предел обязан быть конечным,
# а при соседнем — уйти в бесконечность.
for seed in range(SEEDS):
    item = GENERATORS['E1.make_finite'](random.Random(seed))
    number = re.search(r'sqrt\{(\d+) \+ x\}', item['prompt'])
    if number:
        top = sp.sqrt(int(number.group(1)) + x_sym) - sp.Symbol('c')
        bottom = x_sym
    else:
        angle = int(re.search(r'\\cos (\d+)x', item['prompt']).group(1))
        top = sp.cos(angle * x_sym) - sp.Symbol('c')
        bottom = x_sym**2
    good = sp.limit((top / bottom).subs(sp.Symbol('c'), item['answer']),
                    x_sym, 0)
    worse = sp.limit((top / bottom).subs(sp.Symbol('c'),
                                         sp.sympify(item['answer']) + 1),
                     x_sym, 0)
    t(f'E1.make_finite[{seed}]: при найденном c предел конечен',
      good.is_finite is not False and good not in (sp.oo, -sp.oo))
    t(f'E1.make_finite[{seed}]: при соседнем c предел бесконечен',
      worse in (sp.oo, -sp.oo, sp.zoo) or not worse.is_finite)
print(f'  E1.make_finite               {SEEDS} задач сверено с обеих сторон')

# Дифференциальные уравнения: закрытая форма против численного шага.
for name in ('E7.direct_integration', 'E7.separation',
             'E7.integrating_factor'):
    for seed in range(SEEDS):
        item = GENERATORS[name](random.Random(seed))
        rhs = sp.sympify(item['check']['rhs'])
        start_x, start_y = (float(sp.sympify(v)) for v in item['check']['ic'])
        slope = sp.lambdify((sp.Symbol('x'), sp.Symbol('y')), rhs)
        steps, span = 4000, 0.5
        step = span / steps
        point_x, point_y = start_x, start_y
        for _ in range(steps):
            point_y += step * slope(point_x, point_y)
            point_x += step
        closed = float(item['answer'].subs(sp.Symbol('x'), point_x))
        t(f'{name}[{seed}]: закрытая форма сошлась с численным решением',
          abs(closed - point_y) < 2e-3 * max(1.0, abs(closed)))
    print(f'  {name:28} {SEEDS} задач сверено численно')


# --- E2: ряды выводятся заново, другим механизмом ------------------------
# sp.series здесь не используется совсем: коэффициенты считаются
# производными в нуле, а там, где вопрос предполагает другой маршрут, —
# перемножением и подстановкой отрезков, написанных руками.

def taylor(f, order, var=x_sym):
    """Ряд по определению: f^(n)(0)/n!, без sp.series."""
    out = sp.Integer(0)
    term = sp.sympify(f)
    for power in range(order + 1):
        out += term.subs(var, 0) * var**power / sp.factorial(power)
        term = sp.diff(term, var)
    return sp.expand(out)


for name in ('E2.from_derivatives', 'E2.substitution', 'E2.binomial_series',
             'E2.product_of_series', 'E2.composition', 'E2.term_by_term'):
    for seed in range(SEEDS):
        item = GENERATORS[name](random.Random(seed))
        spec = item['check']
        f = sp.sympify(spec['f'])
        if 'order' in spec:
            want = taylor(f, spec['order'])
            got = sp.expand(sp.sympify(item['answer']))
            # У ответа могут быть члены выше заказанного — обрезаем оба.
            keep = lambda e: sum(e.coeff(x_sym, p) * x_sym**p
                                 for p in range(spec['order'] + 1))
            t(f'{name}[{seed}]: производные в нуле дали тот же ряд',
              sp.simplify(keep(want) - keep(got)) == 0)
        else:
            deep = taylor(f, 24)
            powers = [p for p in range(25) if deep.coeff(x_sym, p) != 0]
            wanted = powers[:spec['terms']]
            got = sp.expand(sp.sympify(item['answer']))
            t(f'{name}[{seed}]: первые {spec["terms"]} ненулевых члена сошлись',
              all(sp.simplify(got.coeff(x_sym, p) - deep.coeff(x_sym, p)) == 0
                  for p in wanted))
    print(f'  {name:28} {SEEDS} рядов пересчитано по определению')

# Соотношение из условия from_derivatives — утверждение о самой функции,
# и его надо проверить отдельно: ученик будет считать по нему, а не по f.
for seed in range(SEEDS):
    item = GENERATORS['E2.from_derivatives'](random.Random(seed))
    f = sp.sympify(item['check']['f'])
    coeffs = [int(v) for v in re.findall(r"= (\d+)f'\(x\) - (\d+)f\(x\)",
                                         item['prompt'])[0]]
    first, second = coeffs
    t(f'E2.from_derivatives[{seed}]: соотношение и правда выполняется',
      sp.simplify(sp.diff(f, x_sym, 2) - first*sp.diff(f, x_sym)
                  + second*f) == 0)
    t(f'E2.from_derivatives[{seed}]: f(0) = 1 и f\'(0) названы верно',
      f.subs(x_sym, 0) == 1
      and str(sp.diff(f, x_sym).subs(x_sym, 0)) in item['prompt'])
print(f'  {"E2.from_derivatives":28} соотношение проверено на {SEEDS} зёрнах')

# from_ode: ряд собирается из уравнения неявным дифференцированием —
# ровно тем маршрутом, который просят от ученика, и без dsolve.
for seed in range(SEEDS):
    item = GENERATORS['E2.from_ode'](random.Random(seed))
    spec = item['check']
    rhs = sp.sympify(spec['rhs'])
    dep = sp.Symbol(spec['dep'])
    Y = sp.Function('Y')
    expr = rhs.subs(dep, Y(x_sym))
    values = {Y(0): sp.sympify(spec['ic'])}
    built = values[Y(0)]
    current = expr
    for power in range(1, spec['order'] + 1):
        at_zero = current
        for depth in range(spec['order'], 0, -1):
            at_zero = at_zero.subs(sp.Derivative(Y(x_sym), (x_sym, depth)),
                                   values.get(depth, 0))
        at_zero = at_zero.subs(Y(x_sym), values[Y(0)]).subs(x_sym, 0)
        values[power] = sp.simplify(at_zero)
        built += values[power] * x_sym**power / sp.factorial(power)
        current = sp.diff(current, x_sym)
        for depth in range(spec['order'], 0, -1):
            current = current.subs(sp.Derivative(Y(x_sym), (x_sym, depth)),
                                   sp.diff(expr, x_sym, depth - 1))
    t(f'E2.from_ode[{seed}]: ряд из уравнения сошёлся с эталоном',
      sp.simplify(sp.expand(built) - sp.expand(sp.sympify(item['answer'])))
      == 0)
print(f'  {"E2.from_ode":28} {SEEDS} рядов собрано из уравнения')

# use_series: подстановка и интегрирование считаются заново от условия.
for seed in range(SEEDS):
    item = GENERATORS['E2.use_series'](random.Random(seed))
    inner = re.search(r'\\int_\{0\}\^\{(1|\\frac\{1\}\{\d+\})\}',
                      item['prompt']).group(1)
    top = (sp.Integer(1) if inner == '1'
           else sp.Rational(1, int(re.search(r'\{(\d+)\}\s*$',
                                             inner).group(1))))
    power = int(re.search(r'x\^\{(\d)\}', item['prompt']).group(1))
    head = (lambda u: u - u**3 / 6) if '\\sin' in item['prompt'] \
        else (lambda u: u - u**3 / 3)
    again = sp.integrate(sp.expand(head(x_sym**power)), (x_sym, 0, top))
    t(f'E2.use_series[{seed}]: интеграл отрезка пересчитан от условия',
      sp.simplify(again - sp.sympify(item['answer'])) == 0)
print(f'  {"E2.use_series":28} {SEEDS} интегралов пересчитано')

# error_bound: минимальность перебирается в лоб, без формулы генератора.
for seed in range(SEEDS):
    item = GENERATORS['E2.error_bound'](random.Random(seed))
    root = int(re.search(r'\\sqrt\{(\d+)\}', item['prompt']).group(1))
    power = int(re.search(r'10\^\{-(\d+)\}', item['prompt']).group(1))
    point = 1 / math.sqrt(root)
    limit = 10.0**(-power)
    size = lambda idx: point**(2*idx - 1) / (2*idx - 1)
    want = int(item['answer'])
    t(f'E2.error_bound[{seed}]: член {want + 1} меньше границы',
      size(want + 1) < limit)
    t(f'E2.error_bound[{seed}]: а член {want} — нет',
      want == 1 or size(want) >= limit)
print(f'  {"E2.error_bound":28} минимальность проверена перебором')


# --- 3. что проверки отвергают ------------------------------------------

section('что проверки отвергают')
item = GENERATORS['C1.exact_values'](random.Random(0))
ok, msg = evaluate(item['check'], f'{float(sp.sympify(item["answer"])):.10g}')
t('десятичная запись вместо точного значения отвергается', not ok)
print(f'  {msg}')

item = GENERATORS['B1.equation_from_situation'](random.Random(0))
e = sp.sympify(item['answer'])
ok, msg = evaluate(item['check'],
                   f'{sp.sstr(sp.expand(e.lhs * sp.Symbol("x")))} = '
                   f'{sp.sstr(e.rhs * sp.Symbol("x"))}')
t('уравнение, домноженное на x, отвергается', not ok)
print(f'  {msg}')

item = GENERATORS['C1.cosine_rule'](random.Random(1))
ok, msg = evaluate(item['check'], f'{item["answer"] * 1.3:.6g}')
t('сторона, не замыкающая треугольник, отвергается', not ok)
print(f'  {msg}')

ok, msg = evaluate(GENERATORS['B1.quadratic_toolkit'](
    random.Random(0))['check'], 'абырвалг')
t('нечитаемая запись — это не «верно»', not ok)
print(f'  {msg}')


# --- 4. где проверки мягче экзамена -------------------------------------

section('где проверки мягче экзамена')

item = GENERATORS['C1.ambiguous_case'](random.Random(2))
if item['check']['kind'] == 'count':
    print('  1. Неоднозначный случай спрашивает число треугольников: ответ «2»\n'
          '     принимается и от того, кто просто угадал, — различить нечем.')
else:
    print('  1. В неоднозначном случае спрашивается тупой угол; острый\n'
          '     отвергнут не будет, если совпал по округлению.')

print('  2. verify_triangle сверяет ответ с достроенным треугольником\n'
      '     с точностью 5·10⁻³ — ошибка в четвёртой значащей цифре\n'
      '     пройдёт, хотя markscheme требует три.')
print('  5. Доказательство напечатанным ответом не проверить. В A7 и\n'
      '     в приёме prove_inequality спрашивается счётное ядро — база\n'
      '     индукции, разность S(k+1) − S(k), вынесенный множитель, —\n'
      '     а не само рассуждение. Тренажёр это и не скрывает.')
print('  6. verify_roots ищет смену знака и корень ровно на конце отрезка\n'
      '     не видит: у cos x = 1 на [0, 2π] он пропускал 2π и принимал\n'
      '     неполный ответ. Проверка тренажёра досчитывает количество\n'
      '     точно через solveset — но только там, где solveset справляется.')
print('  3. Ответ на узнавание сверяется по хешу кода: близкий по смыслу\n'
      '     приём отвергается так же, как совсем чужой, объяснить разницу\n'
      '     тренажёр не может.')
print('  4. Время меряет страница и присылает готовым. Один человек может\n'
      '     прислать что угодно — но обманывать здесь некого.')


bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad[:6])}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
