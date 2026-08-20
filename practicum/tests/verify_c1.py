"""Прогоняет все проверки практикума C1 с эталонными ответами из раздела решений.

Ответы не переписываются из решений: треугольники достраиваются
solve_triangle из данных условия, точные значения выводит sympy, численные
считаются перебором и nsolve. Отдельно измеряется, что проверки отвергают
и где они мягче экзамена.

Здесь же перепроверены расхождения с разметкой корпуса: невозможная
пифагорова тройка в блоке ноября 2022, ноябрьская Paper 3 2023 года,
попавшая в корпус дважды, и четырнадцать баллов, которые к треугольнику
не относятся вовсе.
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
R = sp.Rational
from kit import *

NB = os.path.join(ROOT, 'practicum/geometry', 'practicum-c1-triangle.ipynb')
nb = json.load(open(NB))
D = {}
for cell in nb['cells']:
    for line in ''.join(cell['source']).split('\n'):
        if any(f in line for f in ("check_num(", "check_set(", "check_expr(")):
            D[line.split("'")[1]] = line.split("'")[-2]

res = []
a, b, c, d = sp.symbols('a b c d')
alpha, beta, theta = sp.symbols('alpha beta theta')


def t(name, ok):
    res.append((name, ok))


print('=== прямоугольный треугольник ===')

# Задание 1: уравнение составляется по чертежу, дальше только арифметика.
r1 = sp.symbols('r1', positive=True)
rad1 = float(sp.solve(sp.Eq(sp.tan(sp.rad(58)), (20 - R(9, 5)) / (5 + r1)), r1)[0])
vol1 = float(sp.pi * rad1**2 * 20 / 3)
print(f'Задание 1: вертикальный катет 18.2, радиус {rad1:.5f}, объём {vol1:.4f}')
t('1a', check_num('Задание 1(a)', rad1, 3, D['Задание 1(a)']))
t('1b', check_num('Задание 1(b)', vol1, 3, D['Задание 1(b)']))
# Округлённый радиус даёт другую третью значащую цифру объёма.
t('1round', sig(math.pi * 6.37**2 * 20 / 3, 3) != sig(vol1, 3))

# Задание 2: расстояние между точками и половина диагонали основания.
vx2 = (sp.Matrix([1, 7, 0]) - sp.Matrix([-3, 4, 2])).norm()
ac2 = sp.sqrt(5**2 + 5**2)
ang2 = float(sp.deg(sp.atan(vx2 / (ac2 / 2))))
print(f'Задание 2: VX = {vx2}, AC = {ac2}, угол {ang2:.4f}')
t('2a', verify_exact('Задание 2(a)', vx2, sp.sqrt(29)))
t('2b', verify_exact('Задание 2(b)', ac2, 5 * sp.sqrt(2)))
t('2c', check_num('Задание 2(c)', ang2, 3, D['Задание 2(c)']))
# Ошибка «взял всю диагональ вместо половины» даёт заметно другой угол.
t('2half', abs(float(sp.deg(sp.atan(vx2 / ac2))) - ang2) > 5)

print('\n=== от описания к чертежу ===')

# Задание 3: направление 034° и восток дают угол при J вычитанием.
angle_j = 90 - 34
angle_d = 180 - angle_j - 25
tri3 = solve_triangle(A=angle_j, B=25, c=500)[0]
print(f'Задание 3: DJL = {angle_j}, JDL = {angle_d}, DL = {tri3["a"]:.4f}')
t('3a', check_num('Задание 3(a)', angle_d, 3, D['Задание 3(a)']))
t('3b', verify_triangle('Задание 3(b)', {'a': tri3['a']}, B=25, C=angle_d, c=500))
# Против самого большого угла лежит самая длинная сторона.
t('3longest', tri3['c'] > tri3['a'] > tri3['b'])

print('\n=== теорема косинусов и теорема синусов ===')

tri4 = solve_triangle(b=12, c=7, A=116)[0]
print(f'Задание 4: BC = {tri4["a"]:.5f}, задание 5: ACB = {tri4["C"]:.5f}')
t('4', verify_triangle('Задание 4', {'a': tri4['a']}, b=12, c=7, A=116))
t('5', verify_triangle('Задание 5', {'C': tri4['C']}, b=12, c=7, A=116))
t('4cos', abs(tri4['a']**2 - (144 + 49 - 168 * math.cos(math.radians(116)))) < 1e-9)
# Угол против не самой длинной стороны тупым быть не может.
t('5arcsin', tri4['C'] < 90)

tri6 = solve_triangle(a=154, b=90, c=150)[0]
theta6 = (180 - tri6['A']) / 2
h6 = 150 * math.sin(math.radians(theta6))
print(f'Задание 6: APB = {tri6["A"]:.5f}, theta = {theta6:.5f}, h = {h6:.5f}')
t('6a', verify_triangle('Задание 6(a)', {'A': tri6['A']}, a=154, b=90, c=150))
t('6b', check_num('Задание 6(b)', h6, 3, D['Задание 6(b)']))
t('6lower', 90 * math.sin(math.radians(theta6)) < h6)

# Задание 7: общая диагональ записывается дважды.
cos_alpha = sp.solve(sp.Eq(4 + 16 - 16 * sp.cos(alpha),
                           36 + 64 - 96 * sp.cos(beta)), sp.cos(alpha))[0]
print(f'Задание 7: cos α = {cos_alpha}')
t('7', verify_identity('Задание 7', cos_alpha, 6 * sp.cos(beta) - 5, var=beta,
                       samples=(0.2, 0.4, 0.6, 0.8)))
# Из связи следует ограничение cos β ≥ 2/3, которое понадобится в задании 17.
t('7bound', abs(float(sp.acos(R(2, 3))) - 0.8410686705679302) < 1e-9)

qr8 = sp.simplify(sp.radsimp(5 * sp.sin(sp.rad(45)) / sp.sin(sp.rad(75))))
print(f'Задание 8: QR = {qr8} = {float(qr8):.5f}')
t('8', verify_exact('Задание 8', qr8, 5 * sp.sqrt(3) - 5))
t('8less', float(qr8) < 5)

tsym = sp.Symbol('t')
ads9 = sp.pi - sp.Float('0.7754') - sp.pi * tsym / 8
pole9 = float(sp.solve(sp.Eq(ads9, 0), tsym)[0])
print(f'Задание 9: ADS(0) = {float(ads9.subs(tsym, 0)):.5f}, знаменатель '
      f'обнуляется при t = {pole9:.4f} (с округлённой 2,37 — при 6,0352)')
t('9', verify_identity('Задание 9', ads9,
                       sp.pi - 0.7754 - sp.pi * tsym / 8, var=tsym,
                       samples=(0.5, 1.5, 2.5, 3.5)))
# Тот самый разрыв модели, который нашёлся в B1 при поиске корня w(t) = 0.
# В экзаменационной записи константа округлена до 2,37, и разрыв смещается.
t('9pole', abs(pole9 - 6.0255) < 1e-3
  and abs(2.37 * 8 / math.pi - 6.0352) < 1e-3)

print('\n=== неоднозначный случай ===')

tri10 = solve_triangle(a=7, b=12, A=25)
sides10 = sorted(s['c'] for s in tri10)
perim10 = min(7 + 12 + s['c'] for s in tri10)
small = min(tri10, key=lambda s: s['c'])
print(f'Задание 10: два треугольника, AB = {[round(v, 4) for v in sides10]}, '
      f'наименьший периметр {perim10:.5f}')
t('10two', len(tri10) == 2)
t('10a1', verify_triangle('Задание 10, первый', {'c': sides10[0]},
                          a=7, b=12, A=25))
t('10a2', verify_triangle('Задание 10, второй', {'c': sides10[1]},
                          a=7, b=12, A=25))
t('10b', check_num('Задание 10(b)', perim10, 3, D['Задание 10(b)']))
# Те же два корня получаются из квадратного уравнения теоремы косинусов.
ab = sp.Symbol('ab', positive=True)
quad10 = sp.solve(sp.Eq(49, 144 + ab**2 - 24 * ab * sp.cos(sp.rad(25))), ab)
print(f'   те же корни из теоремы косинусов: {[round(float(v), 4) for v in quad10]}')
t('10quad', all(any(abs(float(v) - s) < 1e-6 for s in sides10) for v in quad10))
t('10obtuse', small['B'] > 90 and small['C'] < 90)

print('\n=== площадь ===')

sin11 = sp.sqrt(1 - R(1, 5)**2)
area11 = sp.simplify(R(1, 2) * 6 * 10 * sin11)
print(f'Задание 11: sin A = {sin11}, площадь {area11}')
t('11', verify_exact('Задание 11', area11, 12 * sp.sqrt(6)))
t('11sign', sin11 > 0)

u12, v12, w12 = (1, sp.sqrt(3)), (-2, 0), (1, -sp.sqrt(3))
area12 = sp.simplify((u12[1] - w12[1]) * (u12[0] - v12[0]) / 2)
print(f'Задание 12: основание {u12[1] - w12[1]}, высота {u12[0] - v12[0]}, '
      f'площадь {area12}')
t('12', verify_exact('Задание 12', area12, 3 * sp.sqrt(3)))
# Тот же ответ по формуле половины произведения сторон на синус угла.
side12 = sp.sqrt((u12[0] - v12[0])**2 + (u12[1] - v12[1])**2)
t('12alt', sp.simplify(R(1, 2) * side12**2 * sp.sin(sp.pi / 3) - area12) == 0)

legs13 = (a, (a**2 - 1) / 2)
hyp13 = (a**2 + 1) / 2
area13 = sp.simplify(legs13[0] * legs13[1] / 2)
print(f'Задание 13: катеты {legs13}, гипотенуза {hyp13}, площадь {area13}')
t('13pyth', sp.simplify(legs13[0]**2 + legs13[1]**2 - hyp13**2) == 0)
t('13a', verify_identity('Задание 13(a)', legs13[0]**2 + legs13[1]**2,
                         hyp13**2, var=a, samples=(1.5, 2, 3, 5)))
t('13b', verify_identity('Задание 13(b)', area13, a * (a**2 - 1) / 4, var=a,
                         samples=(1.5, 2, 3, 5)))
# При a = 3 и a = 5 получаются тройки (3,4,5) и (5,12,13).
t('13triples', [int(v.subs(a, 3)) for v in (legs13[1], hyp13)] == [4, 5]
  and [int(v.subs(a, 5)) for v in (legs13[1], hyp13)] == [12, 13])

mid14 = (R(6 + 3, 2), 3 * sp.sqrt(3) / 2)
slope14 = sp.simplify(mid14[1] / mid14[0])
b14 = (6, sp.simplify(6 * slope14))
area14 = sp.simplify(2 * R(1, 2) * 6 * b14[1])
print(f'Задание 14: середина {mid14}, наклон {slope14}, B{b14}, площадь {area14}')
t('14a', verify_identity('Задание 14(a)', slope14 * x, x / sp.sqrt(3), var=x))
t('14b', verify_exact('Задание 14(b)', area14, 12 * sp.sqrt(3)))
# Наклон 1/√3 — это 30°, биссектриса угла между осью x и лучом на C(60°).
t('14angle', abs(float(sp.deg(sp.atan(slope14))) - 30) < 1e-9)

print('\n=== точные значения ===')

xx = sp.Symbol('xx', positive=True)
x15 = sp.solve(sp.Eq(100, xx**2 + (2 * xx)**2 - 2 * xx * 2 * xx * R(3, 4)), xx)[0]
sin15 = sp.sqrt(1 - R(3, 4)**2)
area15 = sp.simplify(R(1, 2) * x15 * 2 * x15 * sin15)
print(f'Задание 15: x = {x15}, sin C = {sin15}, площадь {area15}')
t('15p', check_num('Задание 15, p', 25, 6, D['Задание 15, p']))
t('15q', check_num('Задание 15, q', 7, 6, D['Задание 15, q']))
t('15area', sp.simplify(area15 - 25 * sp.sqrt(7) / 2) == 0)
# Площадь зависит только от x², извлекать корень было необязательно.
t('15square', sp.simplify(x15**2 - 50) == 0)

print('\n=== треугольник с буквой ===')

theta16 = sp.atan((x + 2) / 6) - sp.atan(x / 6)
print(f'Задание 16: θ(1) = {float(theta16.subs(x, 1)):.5f}, '
      f'θ(10) = {float(theta16.subs(x, 10)):.5f}')
t('16', verify_identity('Задание 16', theta16,
                        sp.atan((x + 2) / 6) - sp.atan(x / 6), var=x,
                        samples=(0.5, 1, 2, 4)))
# Разность, а не сумма: с удалением угол обзора убывает.
t('16decreasing', float(theta16.subs(x, 10)) < float(theta16.subs(x, 1)))

area17 = 4 * sp.sin(sp.acos(6 * sp.cos(beta) - 5)) + 24 * sp.sin(beta)
f17 = sp.lambdify(beta, area17, 'math')
hi17 = float(sp.acos(R(2, 3)))
best = max((f17(hi17 * i / 20000), hi17 * i / 20000) for i in range(1, 20000))
brahma = sp.sqrt((10 - 2) * (10 - 4) * (10 - 6) * (10 - 8))
print(f'Задание 17: максимум {best[0]:.6f} при β = {math.degrees(best[1]):.3f}°, '
      f'формула Брахмагупты даёт {sp.simplify(brahma)} = {float(brahma):.6f}')
t('17a', check_num('Задание 17(a)', best[0], 3, D['Задание 17(a)']))
t('17b', verify_exact('Задание 17(b)', sp.simplify(brahma), 8 * sp.sqrt(6)))
t('17same', abs(best[0] - float(brahma)) < 1e-4)
# В точке максимума четырёхугольник вписанный: α + β = 180°.
alpha17 = math.degrees(math.acos(6 * math.cos(best[1]) - 5))
t('17cyclic', abs(alpha17 + math.degrees(best[1]) - 180) < 0.05)

l18 = R(3, 4) / sp.cos(alpha) + 6 / sp.sin(alpha)
print(f'Задание 18: L(π/4) = {float(l18.subs(alpha, sp.pi / 4)):.5f}')
t('18', verify_identity('Задание 18', l18,
                        R(3, 4) * sp.sec(alpha) + 6 * sp.csc(alpha), var=alpha,
                        samples=(0.4, 0.8, 1.2, 1.5)))
# Минимум длины достигается при α = arctan 2 — продолжение того же вопроса.
t('18min', any(abs(float(v) - float(sp.atan(2))) < 1e-9
               for v in sp.solve(sp.diff(l18, alpha), alpha) if v.is_real))

print('\n=== задание на таймере ===')

bc19 = sp.simplify(5 * sp.sin(2 * theta) / sp.sin(theta))
cos19 = sp.solve(sp.Eq(bc19, 6 * sp.sqrt(2)), sp.cos(theta))[0]
sin19 = sp.sqrt(1 - cos19**2)
dc = sp.Symbol('dc', positive=True)
dc19 = sp.solve(sp.Eq(R(1, 2) * 6 * sp.sqrt(2) * dc * sin19, 2 * sp.sqrt(14)), dc)[0]
print(f'Задание 19: BC = {bc19}, cos θ = {cos19}, sin θ = {sp.simplify(sin19)}, '
      f'DC = {dc19}')
t('19a', verify_identity('Задание 19(a)', bc19, 10 * sp.cos(theta), var=theta,
                         samples=(0.3, 0.5, 0.7, 0.9)))
t('19b', verify_exact('Задание 19(b)', sp.simplify(sin19), sp.sqrt(7) / 5))
t('19c', verify_exact('Задание 19(c)', dc19, R(10, 3)))
t('19cos', sp.simplify(cos19 - 3 * sp.sqrt(2) / 5) == 0)

print('\n=== тренажёр ===')
KEY = {1: 'cos', 2: 'area', 3: 'right', 4: 'ambig', 5: 'sin',
       6: 'exact', 7: 'view', 8: 'model', 9: 'cos', 10: 'area',
       11: 'right', 12: 'sin', 13: 'exact', 14: 'ambig', 15: 'model'}
src = next(''.join(cell['source']) for cell in nb['cells']
           if 'trigger_check(' in ''.join(cell['source']))
t('trigger', all(digest(v) in src for v in KEY.values()))
t('trigger-count', src.count(': ') >= 15)

print('\n=== что проверки отвергают ===')
t('нет: сторона из другого треугольника',
  not verify_triangle('  BC = 16.3 при A = 100', {'a': 16.3}, b=12, c=7, A=100))
t('нет: угол не согласуется',
  not verify_triangle('  ACB = 30', {'C': 30}, b=12, c=7, A=116))
t('нет: в неоднозначном случае взят чужой корень',
  not verify_triangle('  c = 10', {'c': 10}, a=7, b=12, A=25))
t('нет: данные треугольника не задают',
  not verify_triangle('  что угодно', {'c': 5}, a=1, b=2, c=3))
t('нет: десятичная запись вместо точной',
  not verify_exact('  29.4', sp.Float('29.3939', 6), 12 * sp.sqrt(6)))
t('нет: точное, но другое число',
  not verify_exact('  12√5', 12 * sp.sqrt(5), 12 * sp.sqrt(6)))
t('нет: округление до двух значащих цифр',
  not verify_triangle('  16', {'a': 16}, b=12, c=7, A=116))
t('нет: взята вся диагональ вместо половины',
  not check_num('  37.3 вместо 56.7', float(sp.deg(sp.atan(vx2 / ac2))), 3,
                D['Задание 2(c)']))

print('\n=== где проверки мягче экзамена ===')
# 1. verify_triangle судит по данным условия, а не по вопросу: если данные
#    допускают два треугольника, проходит любой из них.
t('предел 1: в неоднозначном случае проходит любой из двух',
  verify_triangle('  c = 15.7', {'c': 15.7}, a=7, b=12, A=25)
  and verify_triangle('  c = 6.05', {'c': 6.05}, a=7, b=12, A=25))
# 2. Допуск относительный (5e−3): три значащие цифры и четыре проходят
#    одинаково, хотя markscheme просит ровно три.
t('предел 2: 16.33 и 16.3 проходят одинаково',
  verify_triangle('  16.33', {'a': 16.33}, b=12, c=7, A=116)
  and verify_triangle('  16.3', {'a': 16.3}, b=12, c=7, A=116))
# 3. verify_exact следит за точностью записи, но не за формой: 5√175/2
#    равно 25√7/2 и проходит, хотя q обязано быть свободным от квадратов.
t('предел 3: q не свободно от квадратов, но проходит',
  verify_exact('  5√175/2', 5 * sp.sqrt(175) / 2, 25 * sp.sqrt(7) / 2))
# 4. verify_identity сверяет значения в точках, а не запись: ответ через
#    sec и cosec и ответ через 1/cos и 1/sin неразличимы.
t('предел 4: sec и 1/cos для проверки одно и то же',
  verify_identity('  через sec', R(3, 4) * sp.sec(alpha) + 6 * sp.csc(alpha),
                  R(3, 4) / sp.cos(alpha) + 6 / sp.sin(alpha), var=alpha,
                  samples=(0.4, 0.8, 1.2)))

print('\n=== расхождения с разметкой корпуса ===')
rows = {}
for path in sorted(glob.glob(os.path.join(
        ROOT, 'classification/generated/*/*/paper-*.json'))):
    for block in json.load(open(path))['blocks']:
        rows.setdefault(block['id'], block)

# 1. Ноябрь 2022, Paper 1, Q3: в корпусе стороны записаны с делением на 2a.
q3 = rows['2022-NOV-COMMON-P1-Q03-B']
wrong = [a, (a**2 - 1) / (2 * a), (a**2 + 1) / (2 * a)]
right = [a, (a**2 - 1) / 2, (a**2 + 1) / 2]
resid_wrong = sp.simplify(wrong[0]**2 + wrong[1]**2 - wrong[2]**2)
resid_right = sp.simplify(right[0]**2 + right[1]**2 - right[2]**2)
print(f'ноябрь 2022 Q3: в корпусе «{q3["task_summary"][:72]}…»')
print(f'  невязка Пифагора при делении на 2a: {resid_wrong}; при делении '
      f'на 2: {resid_right}')
t('корпус: тройка с 2a не пифагорова', resid_wrong != 0)
t('корпус: тройка с 2 пифагорова', resid_right == 0)
t('корпус: в описании блока стоит 2a', '2a)' in q3['task_summary'])
# Площади различаются множителем a: a(a²−1)/4 против (a²−1)/4.
t('корпус: площади различаются множителем a',
  sp.simplify(right[0] * right[1] / 2 / (wrong[0] * wrong[1] / 2) - a) == 0)

# 2. Ноябрьская Paper 3 2023 года лежит в корпусе дважды.
tz1 = json.load(open(os.path.join(
    ROOT, 'classification/generated/2023-november-tz1/deepseek-v4-pro/paper-3.json')))
tz2 = json.load(open(os.path.join(
    ROOT, 'classification/generated/2023-november-tz2/deepseek-v4-pro/paper-3.json')))
both1 = [bl['id'][13:] for bl in tz1['blocks']
         if bl['primary_topic'] == 'geometry.trigonometry']
both2 = [bl['id'][13:] for bl in tz2['blocks']
         if bl['primary_topic'] == 'geometry.trigonometry']
print(f'ноябрь 2023 Paper 3: в теме треугольника {both1} и {both2}, '
      f'бумага одна (Common)')
t('дубль: один и тот же блок в обеих копиях', both1 == both2 == ['P3-Q02-A-II'])
t('дубль: своих Paper 3 у зон нет',
  not os.path.exists(os.path.join(ROOT, 'AA_HL/2023/November/TZ1/Paper 3'))
  and os.path.isdir(os.path.join(ROOT, 'AA_HL/2023/November/Common/Paper 3')))

# 3. Блоки, которые к треугольнику не относятся.
alien = ['2025-MAY-TZ3-P2-Q12-D', '2025-NOV-TZ1-P1-Q10-D',
         '2025-NOV-TZ1-P3-Q01-A-II', '2023-NOV-TZ1-P3-Q02-A-II',
         '2023-NOV-TZ2-P3-Q02-A-II', '2025-MAY-TZ2-P1-Q06-A']
marks_alien = sum(rows[i]['marks'] for i in alien)
print(f'не про треугольник: {len(alien)} блоков, {marks_alien} баллов')
t('чужие блоки лежат в теме',
  all(rows[i]['primary_topic'] == 'geometry.trigonometry' for i in alien))
t('чужих баллов четырнадцать', marks_alien == 14)
t('ни синусов, ни косинусов, ни площади ни в одном',
  not any(set(rows[i]['method_tags']) & {'sine_rule', 'cosine_rule',
                                         'area_of_triangle'} for i in alien))

# 4. Неоднозначный случай: в описании блока выбор назван «acute case».
q10 = rows['2021-NOV-COMMON-P2-Q02']
print(f'ноябрь 2021 Q2: в корпусе «…{q10["task_summary"][-58:]}»')
t('корпус: у треугольника с наименьшим периметром угол B тупой',
  small['B'] > 90 and 'acute case' in q10['task_summary'])

bad = [name for name, ok in res if not ok]
print(f'\n{"ВСЁ ВЕРНО" if not bad else "ПРОВАЛЫ: " + str(bad)}  '
      f'({len(res) - len(bad)}/{len(res)})')
sys.exit(1 if bad else 0)
