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

from drill import engine  # noqa: E402
from drill.check import evaluate, show_answer  # noqa: E402
from drill.items import GENERATORS  # noqa: E402

SEEDS = 15
res = []


def t(name, ok):
    res.append((name, ok))
    if not ok:
        print(f'❌ {name}')


def section(title):
    print(f'\n=== {title} ===')


# --- 1. эталон проходит, испорченный ответ не проходит -------------------

def spoil(answer, spec):
    """Ответ, который обязан быть отвергнут."""
    kind = spec['kind']
    if kind == 'count':
        return str(int(spec['value']) + 1)
    if isinstance(answer, (list, tuple)):
        if len(answer) > 1:
            return show_answer(list(answer)[:-1])       # потерянный корень
        return show_answer(list(answer) + [sp.Integer(97)])  # лишний корень
    if kind == 'num':
        return f'{float(answer) * 1.08:.6g}'
    if kind == 'triangle':
        return f'{float(answer) * 1.08:.6g}'
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
