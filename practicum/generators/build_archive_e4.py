"""Собирает архивный ноутбук E4: касательная и нормаль, вся тема подряд.

Одиннадцатый ноутбук в формате, опробованном на B4, C3, B5, E1, E2, E3, D2,
D1, C2 и A1. Практикум E4 учит — лестница, теория, уровни, тренажёр. Этот
не учит, он даёт набивать руку: вопрос, ячейка для ответа с мгновенной
проверкой, разбор в конце.

Внутри — та часть calculus.differentiation, где производная работает
наклоном: 32 вопроса и 126 баллов, разложенные по восьми приёмам карточки
calculus-tangents.yaml. Тридцать третий блок — зональный дубль ноябрьской
2023 Paper 3, и он стоит один раз, с оговоркой на месте.

Проверки те же, что в практикуме, и все они ходят по кривой: наклон берётся
секущей через две соседние точки самой кривой, а не дифференцированием.
Кривая при этом бывает и функцией, и уравнением — для проверки это один
и тот же случай, и в этом всё устройство темы.

Эталон хранится в одном месте из тридцати двух: x = S/e в 4.5, где кривая
зависит от буквы S и подставить в неё нечего. Всё остальное проверка
получает из условия.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_e4.py прогоняет весь ноутбук
с заполненными ответами и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e4-tangents.ipynb')

# Единственный хеш темы. Кривая g(x) = (S/x)^x зависит от буквы S, ходить
# по ней при каждом S дорого, а подставлять ответ некуда: он сам с буквой.
S = sp.Symbol('S')
D_45 = digest(sp.srepr(sp.simplify(S / sp.E)))

ANSWERS = {
    # 1. Касательная в известной точке
    'q1_1': '6',
    'q1_2': '23',
    'q1_3': '30*x - 97',
    'q1_4': '-3*pi*sin(pi*k/50)/10',
    'q1_5': 'b**2*(x - r)',
    'q1_6': 'r',
    # 2. Нормаль
    'q2_1': '1 - x/2',
    'q2_2': 't**2',
    # 3. Наклон дан — найти точку
    'q3_1': '(2*log(45), 2)',
    'q3_2': '8',
    'q3_3': '(0.863, -7.93)',
    'q3_4': '[2.73, 15.0]',
    # 4. Кривая задана уравнением
    'q4_1': '(1 - y*(1 + log(x*y)))/(1 + x*(1 + log(x*y)))',
    'q4_2': '(3*x**2 + 1)/(2*y)',
    'q4_3': '(2*x - exp(x + y))/(exp(x + y) - 2*y)',
    'q4_4': '4*(3 - x)/(y + 2)',
    'q4_5': 'S*exp(-1)',
    # 5. Касательная к такой кривой
    'q5_1': '1',
    'q5_2': '-3*x/2 - Rational(5, 2)',
    'q5_3': '[(0.331, -0.743), (1.84, -0.538)]',
    'q5_4': '(-0.451, -0.451)',
    # 6. Продифференцировать соотношение ещё раз
    'q6_1': 'k**2*y*(1 - y/N)*(1 - 2*y/N)',
    'q6_2': '-3',
    'q6_3': '3',
    'q6_4': ('(2*x + y - x*((x**2 + x*y - 3*y**2)/(x**2 + x*y))**2'
             ' - (x + 7*y)*(x**2 + x*y - 3*y**2)/(x**2 + x*y))/(x**2 + x*y)'),
    'q6_5': 'Rational(1008, 125)',
    # 7. Прямой угол как условие
    'q7_1': '-sin(k)',
    'q7_2': 'sec(k)**2',
    'q7_3': 'y/x',
    'q7_4': '-a/sqrt(a*b)',
    'q7_5': 'b/sqrt(a*b)',
    # 8. Касание как условие
    'q8_1': '(E + 6)/2',
    'q8_2': 'E + E**2/4',
    'q8_3': '3',
    'q8_4': '1',
    'q8_5': '4',
    'q8_6': 'E',
    'q8_7': 'E',
    'q8_8': 'E**(1/E)',
}

cells = []


def _lines(src):
    parts = src.strip('\n').split('\n')
    return [pp + '\n' for pp in parts[:-1]] + parts[-1:]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Archive E4 — implicit differentiation, tangents and normals

**Every question in the topic, one after another.** No theory, no ladder, no
levels: the practicum has all of that. This is for sitting down and working
through the material until the moves stop needing thought.

**32 questions, 126 marks, May 2021 — November 2025.** The part of
`calculus.differentiation` where the derivative works as a *gradient* — the
tangent, the normal, *parallel to*, *at an angle of*, and every curve given by
an equation rather than a formula.

Grouped by the eight techniques of
[`calculus-tangents.yaml`](../skills/calculus-tangents.yaml), in the order of
the practicum's ladder. Within a group the questions run from short to long.

**How to use this.** Read the question, write the answer in the cell, run it.
The check answers at once. Solutions are at the bottom — all of them, in
order; use them when you are stuck or when you are done, not in between.

**What the checks do.** They walk along the curve. Given a point, each check
steps a little to the left and a little to the right, solves the curve's own
equation for the other coordinate each time, and takes the gradient of the
line through the two points it found. There is no differentiation inside them
and no stored answer: any form of a correct line or a correct gradient passes.

One consequence to know before you start: **a 3 s.f. answer is checked as a
3 s.f. answer.** $(1.84,-0.538)$ is not on the curve — no rounded point is —
so the check looks for the real solution next door and asks whether your
digits round to it.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, log, Eq

language('en')                 # this notebook is in English, and so are the checks

a, b, c, h, m, r, S = symbols('a b c h m r S')   # letters that stay letters
                                                 # x, y, t, k, N come from kit


def shape(build, *answers):
    # A curve built out of your own answers, blank while they are blank.
    return curve(...) if blank(*answers) else curve(build())


print('ready; sympy', sp.__version__)
""")

# ------------------------------------------------------------------ 1
md(r"""
---
# 1. The tangent at a known point

*Five questions, 14 marks.* The point is named; the gradient comes from the
derivative and the height comes from the curve. The whole difficulty is
remembering that those are two different places.
""")

md(r"""
## 1.1 — 1.3 · November 2021 Paper 1 Q5(a)(b)(d) · 5 marks · no calculator

The function $f$ is defined for all $x\in\mathbb{R}$. The line $y=6x-1$ is the
tangent to the graph of $f$ at $x=4$.

**1.1** Write down the value of $f'(4)$. *[1]*

**1.2** Find $f(4)$. *[1]*

The function $g$ is defined for all $x\in\mathbb{R}$, where $g(x)=x^2-3x$, and
$h(x)=f\bigl(g(x)\bigr)$.

**1.3** Hence find the equation of the tangent to the graph of $h$ at $x=4$.
*[3]*
""")

code(r"""
q1_1 = ...       # f'(4)
q1_2 = ...       # f(4)
q1_3 = ...       # the tangent to h at x = 4, as an expression in x

given = curve(Eq(y, 6*x - 1))
verify_slope('1.1', q1_1, given, at=4)
verify_on('1.2', q1_2, given, 4)

# f is unknown, so the check tries four functions that all match f(4) = 23 and
# f'(4) = 6, composes each with g, and wants the same tangent every time.
inner = x**2 - 3*x
verify_tangent('1.3', q1_3, curve(Eq(y, 6*inner - 1 + c*(inner - 4)**2)), 4,
               params={c: (0, 2, -3, 5)})
""")

md(r"""
## 1.4 · May 2025 TZ1 Paper 2 Q5(a) · 3 marks · calculator

Consider $h(x)=15\cos\Bigl(\dfrac{\pi x}{50}\Bigr)+15$, where $0\le x\le50$.
The tangent $T_k$ to the curve $y=h(x)$ at the point $\bigl(k,h(k)\bigr)$ is
shown on the diagram in the paper.

Find the gradient of $T_k$ in terms of $k$. *[3]*
""")

code(r"""
q1_4 = ...       # the gradient of T_k, in terms of k

hill = curve(Eq(y, 15*cos(pi*x/50) + 15))
verify_slope('1.4', q1_4, hill, at=k, params={k: (5, 12, 25, 40)})
""")

md(r"""
## 1.5 — 1.6 · May 2022 TZ1 Paper 3 Q2(d)(ii) · 6 marks · Paper 3

Consider $g(x)=(x-r)(x^2-2ax+a^2+b^2)$ for $x\in\mathbb{R}$, where
$r,a\in\mathbb{R}$ and $b\in\mathbb{R}$, $b>0$. From part (d)(i),
$$g'(x)=2(x-r)(x-a)+x^2-2ax+a^2+b^2 .$$

**1.5** Find the equation of the tangent to the curve $y=g(x)$ at the point
$\mathrm{A}\bigl(a,g(a)\bigr)$, as an expression in $x$.

**1.6** Hence give the $x$-coordinate of the point $\mathrm{R}$ where this
tangent meets the $x$-axis. *[6 for the two]*
""")

code(r"""
q1_5 = ...       # the tangent at A, in terms of x, a, b and r
q1_6 = ...       # the x-coordinate of R

letters = {a: (1, 2, -1, 3), b: (2, 1, 3, 1), r: (-2, 0, 4, 1)}
verify_tangent('1.5', q1_5, curve(Eq(y, (x - r)*(x**2 - 2*a*x + a**2 + b**2))),
               a, params=letters)
verify_on('1.6', 0, shape(lambda: Eq(y, q1_5), q1_5), q1_6, params=letters)
""")

# ------------------------------------------------------------------ 2
md(r"""
---
# 2. The normal

*Two questions, 7 marks.* One step differs from the tangent, and it is
$-1/m$, not $-m$.
""")

md(r"""
## 2.1 · November 2025 TZ3 Paper 1 Q9(c) · 5 marks · no calculator

Consider $f(x)=\tfrac12x^2+kx+13$, where $x\in\mathbb{R}$ and
$k\in\mathbb{Z}^{+}$; for this part $k=5$. The line $L$ is normal to the curve
at $x=-3$.

Show that the equation of $L$ is $y=-\tfrac12x+1$, by writing it down as an
expression in $x$. *[5]*
""")

code(r"""
q2_1 = ...       # the normal at x = -3, as an expression in x

verify_normal('2.1', q2_1, curve(Eq(y, x**2/2 + 5*x + 13)), -3)
""")

md(r"""
## 2.2 · November 2025 TZ1 Paper 3 Q1(a)(i) · 2 marks · Paper 3

The curve $H$ has equation $y=\dfrac1x$, where $x\in\mathbb{R}$, $x\ne0$.
A line $N$ is normal to $H$ at $x=t$.

Show that the gradient of $N$ is $t^2$, by writing that gradient down. *[2]*
""")

code(r"""
q2_2 = ...       # the gradient of N, in terms of t

# You hand in a gradient; the check builds the normal through the point out of
# it and holds that line against the curve.
line = ... if blank(q2_2) else q2_2*(x - t) + 1/t
verify_normal('2.2', line, curve(Eq(y, 1/x)), t, params={t: (0.5, 1, 2, 3)})
""")

# ------------------------------------------------------------------ 3
md(r"""
---
# 3. The gradient is given, the point is not

*Four questions, 17 marks.* Convert the condition to a number, set $f'$ equal
to it, and then be careful about two things: the domain, and whether the
question wanted one coordinate or two.
""")

md(r"""
## 3.1 · May 2021 TZ1 Paper 2 Q10(b) · 4 marks · calculator

Consider $f(x)=90\mathrm{e}^{-0.5x}$ for $x\in\mathbb{R}^{+}$. The line $L$ has
gradient $-1$ and is tangent to the graph of $f$ at the point $\mathrm{Q}$.

Find the **exact** coordinates of $\mathrm{Q}$. *[4]*
""")

code(r"""
q3_1 = ...       # (x, y), exact

verify_where('3.1', q3_1, curve(Eq(y, 90*exp(-x/2))), -1, (0.01, 20))
""")

md(r"""
## 3.2 · May 2021 TZ2 Paper 1 Q4(b) · 6 marks · no calculator

Consider $f(x)=\ln(x^2-16)$ for $x>4$. The line $L$ is the tangent to the graph
of $f$ at the point $\mathrm{B}$, and the gradient of $L$ is $\tfrac13$.

Find the $x$-coordinate of $\mathrm{B}$. *[6]*
""")

code(r"""
q3_2 = ...       # the x-coordinate of B — a list, if you think there is more than one

verify_where('3.2', q3_2, curve(Eq(y, log(x**2 - 16))), Rational(1, 3),
             (4.01, 30), coordinates=False)
""")

md(r"""
## 3.3 · November 2022 Paper 2 Q11(b) · 3 marks · calculator

The function $f$ is defined by $f(x)=\mathrm{e}^{2x}(3x-4)$, where
$x\in\mathbb{R}$.

Find the coordinates of the point on the graph of $y=f(x)$ where the tangent
is parallel to the line $y=x$. Give your answer to 3 significant figures. *[3]*
""")

code(r"""
q3_3 = ...       # (x, y), 3 s.f.

verify_where('3.3', q3_3, curve(Eq(y, exp(2*x)*(3*x - 4))), 1, (-2, 3))
""")

md(r"""
## 3.4 · May 2025 TZ3 Paper 2 Q5(b) · 4 marks · calculator

Consider $f(x)=\dfrac{(2x+a)^3}{(x+5)^2}$, where $x\ne-5$ and
$a\in\mathbb{R}^{+}$. When $x=1$, the tangent to the graph of $f$ makes an
angle of $70^\circ$ with the horizontal.

Find the two possible values of $a$, to 3 significant figures. *[4]*
""")

code(r"""
q3_4 = ...       # both values, as a list

verify_constant('3.4', q3_4, lambda v: curve(Eq(y, (2*x + v)**3/(x + 5)**2)),
                1, tan(70*pi/180), (0.1, 25))
""")

# ------------------------------------------------------------------ 4
md(r"""
---
# 4. The curve is an equation

*Five questions, 21 marks.* $y$ is a function of $x$ whether or not anyone
wrote it that way, so every $y$ that gets differentiated brings a
$\frac{\mathrm{d}y}{\mathrm{d}x}$ out with it. The answer keeps both letters,
and that is a finished answer.
""")

md(r"""
## 4.1 · November 2021 Paper 2 Q8(a) · 3 marks · calculator

Consider the curve $C$ given by $y=x-xy\ln(xy)$, where $x>0$, $y>0$.

The exam asks you to show that
$$\frac{\mathrm{d}y}{\mathrm{d}x}+\Bigl(x\frac{\mathrm{d}y}{\mathrm{d}x}+y\Bigr)
\bigl(1+\ln(xy)\bigr)=1 .$$
Do that, and then write $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ as an expression in
$x$ and $y$. *[3]*
""")

code(r"""
q4_1 = ...       # dy/dx, in terms of x and y

verify_slope('4.1', q4_1, curve(Eq(y, x - x*y*log(x*y))), domain=(0.4, 1.6))
""")

md(r"""
## 4.2 · May 2022 TZ2 Paper 3 Q1(d)(i) · 3 marks · Paper 3

Consider the curve $y^2=x^3+x$ for $x\ge0$.

The exam asks you to show that
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\pm\dfrac{3x^2+1}{2\sqrt{x^3+x}}$ for $x>0$.
Do that, and write $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ in terms of $x$ **and**
$y$ — which is the line the $\pm$ comes from. *[3]*
""")

code(r"""
q4_2 = ...       # dy/dx, in terms of x and y

verify_slope('4.2', q4_2, curve(Eq(y**2, x**3 + x)), domain=(0.3, 3))
""")

md(r"""
## 4.3 · May 2024 TZ1 Paper 2 Q11(a) · 5 marks · calculator

The curve $C$ is defined by the equation $\mathrm{e}^{x+y}=x^2+y^2$ and has a
line of symmetry $y=x$.

Show that
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\dfrac{2x-\mathrm{e}^{x+y}}{\mathrm{e}^{x+y}-2y}$,
by writing it down. *[5]*
""")

code(r"""
q4_3 = ...       # dy/dx, in terms of x and y

verify_slope('4.3', q4_3, curve(Eq(exp(x + y), x**2 + y**2)), domain=(0.2, 2))
""")

md(r"""
## 4.4 · May 2025 TZ2 Paper 2 Q12(a) · 4 marks · calculator

The curve $C$ has equation $4x^2+y^2-24x+4y+20=0$.

Use implicit differentiation to show that
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\dfrac{4(3-x)}{y+2}$, by writing it down.
*[4]*
""")

code(r"""
q4_4 = ...       # dy/dx, in terms of x and y

verify_slope('4.4', q4_4, curve(4*x**2 + y**2 - 24*x + 4*y + 20),
             domain=(1.5, 4.5))
""")

md(r"""
## 4.5 · May 2023 TZ1 Paper 3 Q2(h) · 6 marks · Paper 3

Consider the function $g$ defined by
$$\ln\bigl(g(x)\bigr)=x\ln\Bigl(\frac{S}{x}\Bigr),\qquad x\in\mathbb{R}^{+},$$
where $S$ is a positive constant. The graph of $y=g(x)$ has a maximum at the
point $\mathrm{A}$.

Find, in terms of $S$, the $x$-coordinate of $\mathrm{A}$. *[6]*

*This is the one question of the topic whose curve carries a letter the check
cannot walk past, so its answer is held against a hash and not against the
curve.*
""")

code(r"""
q4_5 = ...       # the x-coordinate of A, in terms of S

check_expr('4.5', q4_5, '""" + D_45 + r"""')
""")

# ------------------------------------------------------------------ 5
md(r"""
---
# 5. A tangent to such a curve

*Four questions, 20 marks.* To turn $\frac{\mathrm{d}y}{\mathrm{d}x}$ into a
number you need both coordinates, and the second one comes from the curve's
own equation. Backwards, setting a fraction to zero means setting its
numerator to zero — one equation in two unknowns, and the curve is the other.
""")

md(r"""
## 5.1 · November 2021 Paper 2 Q8(b) · 5 marks · calculator

For the curve $C$ given by $y=x-xy\ln(xy)$ with $x>0$, $y>0$, find the equation
of the tangent to $C$ at the point where $x=1$, as an expression in $x$. *[5]*
""")

code(r"""
q5_1 = ...       # the tangent at x = 1, as an expression in x

verify_tangent('5.1', q5_1, curve(Eq(y, x - x*y*log(x*y))), (1, 1))
""")

md(r"""
## 5.2 · May 2022 TZ2 Paper 3 Q1(f)(i) · 2 marks · Paper 3

Let $C$ be the curve $y^2=x^3+2$ for $x\ge-\sqrt[3]{2}$. The rational point
$\mathrm{P}(-1,-1)$ lies on $C$.

Find the equation of the tangent to $C$ at $\mathrm{P}$, as an expression in
$x$. *[2]*
""")

code(r"""
q5_2 = ...       # the tangent at the rational point, as an expression in x

verify_tangent('5.2', q5_2, curve(Eq(y**2, x**3 + 2)), (-1, -1))
""")

md(r"""
## 5.3 · May 2024 TZ1 Paper 2 Q11(b) · 9 marks · calculator

There are two points on $C:\ \mathrm{e}^{x+y}=x^2+y^2$ where the tangent is
horizontal, labelled $\mathrm{P}$ and $\mathrm{Q}$.

Show that their $x$-coordinates satisfy
$2x^2+\bigl(\ln(2x)\bigr)^2-2x\ln(2x)-2x=0$, and hence find the coordinates of
$\mathrm{P}$ and of $\mathrm{Q}$, to 3 significant figures. *[9]*
""")

code(r"""
q5_3 = ...       # [(x, y), (x, y)] — both points

verify_where('5.3', q5_3, curve(Eq(exp(x + y), x**2 + y**2)), 0, (0.05, 3))
""")

md(r"""
## 5.4 · May 2024 TZ1 Paper 2 Q11(d) · 4 marks · calculator

Find the coordinates of the point on the same curve $C$ where the tangent has
gradient $-1$, to 3 significant figures. *[4]*
""")

code(r"""
q5_4 = ...       # (x, y)

verify_where('5.4', q5_4, curve(Eq(exp(x + y), x**2 + y**2)), -1, (-1, 0.5))
""")

# ------------------------------------------------------------------ 6
md(r"""
---
# 6. Differentiating the relation again

*Four questions, 15 marks.* There is no $y=f(x)$ to differentiate twice, so
the thing that gets differentiated a second time is the equation. Both $y$ and
$\frac{\mathrm{d}y}{\mathrm{d}x}$ are functions of $x$ while you do it.
""")

md(r"""
## 6.1 · May 2022 TZ2 Paper 2 Q12(b) · 4 marks · calculator

The population $P$ of a species of marsupial is modelled by the logistic
differential equation
$$\frac{\mathrm{d}P}{\mathrm{d}t}=kP\Bigl(1-\frac{P}{N}\Bigr),$$
where $t$ is time in years and $k$, $N$ are positive constants.

Show that
$\dfrac{\mathrm{d}^2P}{\mathrm{d}t^2}=k^2P\Bigl(1-\dfrac{P}{N}\Bigr)
\Bigl(1-\dfrac{2P}{N}\Bigr)$, by writing the second derivative down in terms
of $P$, $k$ and $N$. *[4]*

*Write $P$ as `y` — that is the letter the check reads off the curve.*
""")

code(r"""
q6_1 = ...       # the second derivative, in terms of y (the population), k and N

# A solution of that equation with P(0) = 2, for three different pairs (k, N).
# Nothing about the identity depends on which one, and the check insists on it.
grown = curve(Eq(y, N/(1 + (N/2 - 1)*exp(-k*t))), var=t)
verify_second('6.1', q6_1, grown, 0.7, params={k: (1, 1, 2), N: (10, 6, 5)})
""")

md(r"""
## 6.2 — 6.3 · May 2023 TZ1 Paper 2 Q12(b) · 5 marks · calculator

Consider the differential equation
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{x^2y-y}{x^2+1},\qquad y>0,
\qquad y=3 \text{ when } x=0 .$$

**6.2** Write down the value of $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ when $x=0$.

**6.3** Show that $\dfrac{\mathrm{d}^2y}{\mathrm{d}x^2}=3$ when $x=0$, by
writing that value down. *[5 for the two]*

*Part (d) solves the equation; its solution is $y=3\mathrm{e}^{x-2\arctan x}$,
and that is the curve the checks walk.*
""")

code(r"""
q6_2 = ...       # dy/dx at x = 0
q6_3 = ...       # the second derivative at x = 0

solved = curve(Eq(y, 3*exp(x - 2*atan(x))))
verify_slope('6.2', q6_2, solved, at=0)
verify_second('6.3', q6_3, solved, 0)
""")

md(r"""
## 6.4 — 6.5 · November 2025 TZ3 Paper 2 Q12(b) · 6 marks · calculator

Consider the homogeneous differential equation
$$\bigl(x^2+xy\bigr)\frac{\mathrm{d}y}{\mathrm{d}x}=x^2+xy-3y^2,
\qquad x>0,\ y>\tfrac{x}{2},$$
with $y=\tfrac32$ when $x=1$.

**6.4** Show that
$$\bigl(x^2+xy\bigr)\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2x+y-x\Bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)^{2}
-(x+7y)\frac{\mathrm{d}y}{\mathrm{d}x},$$
and hence write $\dfrac{\mathrm{d}^2y}{\mathrm{d}x^2}$ as an expression in $x$
and $y$ alone, by substituting $\frac{\mathrm{d}y}{\mathrm{d}x}$ from the
original equation.

**6.5** Find the value of $\dfrac{\mathrm{d}^2y}{\mathrm{d}x^2}$ when $x=1$.
*[6 for the two]*

*Part (d) solves the equation and gets $x^{6}(2y-x)^{3}=2(x+2y)$; that is the
curve below.*
""")

code(r"""
q6_4 = ...       # the second derivative, in terms of x and y
q6_5 = ...       # its value at x = 1, exactly

homogeneous = curve(Eq(x**6*(2*y - x)**3, 2*(x + 2*y)))
verify_second('6.4', q6_4, homogeneous, 1.4)
verify_second('6.5', q6_5, homogeneous, (1, Rational(3, 2)))
""")

# ------------------------------------------------------------------ 7
md(r"""
---
# 7. A right angle as a condition

*Four questions, 14 marks.* Nothing is being found; something is being shown.
The point has to be on both curves, each gradient has to be its own curve's,
and the product has to be $-1$ — three claims, three marks.
""")

md(r"""
## 7.1 — 7.2 · May 2023 TZ2 Paper 1 Q8(b) · 3 marks · no calculator

The functions $f$ and $g$ are defined by $f(x)=\cos x$ for
$0\le x\le\tfrac{\pi}{2}$ and $g(x)=\tan x$ for $0\le x<\tfrac{\pi}{2}$. The
curves meet at $\mathrm{P}$, whose $x$-coordinate is $k$, and part (a)
established that $\cos^2k=\sin k$.

Show that the two tangents at $\mathrm{P}$ meet at right angles, by writing
down **7.1** $f'(k)$ and **7.2** $g'(k)$. *[3]*
""")

code(r"""
q7_1 = ...       # f'(k)
q7_2 = ...       # g'(k)

meet = nsolve(cos(x) - tan(x), x, 0.6)
verify_right_angle('7.1-7.2', (q7_1, q7_2), curve(Eq(y, cos(x))),
                   curve(Eq(y, tan(x))), (k, cos(k)), params={k: (meet,)})
""")

md(r"""
## 7.3 · November 2023 Paper 3 Q2(a)(i) · 1 mark · Paper 3

Consider the family of straight lines $L$ with equation $y=mx$, where $m$ is a
parameter. Each member of $L$ meets every member of another family of curves
$C$ at right angles. You are not asked to consider $x=0$.

Write down an expression for the gradient of $L$ in terms of $x$ and $y$. *[1]*
""")

code(r"""
q7_3 = ...       # the gradient of L, in terms of x and y

verify_slope('7.3', q7_3, curve(Eq(y, m*x)), domain=(0.5, 3),
             params={m: (2, -1, 0.5)})
""")

md(r"""
## 7.4 — 7.5 · November 2023 Paper 3 Q2(d) · 5 marks · Paper 3

A family of curves has equation $y^2=4a^2-4ax$, where $a>0$; a second family
has $y^2=4b^2+4bx$, where $b>0$. Part (c) showed that they meet at
$\mathrm{M}\bigl(a-b,\,2\sqrt{ab}\bigr)$.

Show that at $\mathrm{M}$ the two curves intersect at right angles, by writing
down **7.4** the gradient of the first and **7.5** the gradient of the second,
each in terms of $a$ and $b$. *[5]*

*The corpus this notebook is built from carries this question twice, once for
each zone. The paper is one paper — November 2023 Paper 3 is Common — so it is
here once.*
""")

code(r"""
q7_4 = ...       # dy/dx of y^2 = 4a^2 - 4ax at M
q7_5 = ...       # dy/dx of y^2 = 4b^2 + 4bx at M

verify_right_angle('7.4-7.5', (q7_4, q7_5),
                   curve(Eq(y**2, 4*a**2 - 4*a*x)),
                   curve(Eq(y**2, 4*b**2 + 4*b*x)),
                   (a - b, 2*sqrt(a*b)), params={a: (2, 3, 5), b: (1, 2, 4)})
""")

# ------------------------------------------------------------------ 8
md(r"""
---
# 8. Touching as a condition

*Five questions, 23 marks.* The tangent is in the question and is not the
answer. *Common tangent* is worth two equations; *parallel* is worth one;
*is a tangent to* can be shown either way, and a double root is the faster of
the two.
""")

md(r"""
## 8.1 — 8.2 · May 2021 TZ1 Paper 1 Q4(b)(c) · 6 marks · no calculator

Consider $f(x)=-(x-h)^2+2k$ and $g(x)=\mathrm{e}^{x-2}+k$, where
$h,k\in\mathbb{R}$. The graphs of $f$ and $g$ have a common tangent at $x=3$.

**8.1** Show that $h=\dfrac{\mathrm{e}+6}{2}$, by writing $h$ down. *[3]*

**8.2** Hence show that $k=\mathrm{e}+\dfrac{\mathrm{e}^2}{4}$, by writing $k$
down. *[3]*
""")

code(r"""
q8_1 = ...       # h
q8_2 = ...       # k

verify_constant('8.1', q8_1, lambda v: curve(Eq(y, -(x - v)**2)), 3, E, (0, 8))
verify_on('8.2', ... if blank(q8_2) else E + q8_2,
          shape(lambda: Eq(y, -(x - q8_1)**2 + 2*q8_2), q8_1, q8_2), 3)
""")

md(r"""
## 8.3 · May 2022 TZ1 Paper 1 Q4 · 5 marks · no calculator

Consider the curve $y=(2x-1)\mathrm{e}^{kx}$, where $x\in\mathbb{R}$ and
$k\in\mathbb{Q}$. The tangent to the curve at $x=1$ is parallel to the line
$y=5\mathrm{e}^{k}x$.

Find the value of $k$. *[5]*
""")

code(r"""
q8_3 = ...       # k

# The letter sits in the curve, so the curve is rebuilt from your answer. The
# gradient it must have at x = 1 is the gradient of the given line — which
# also depends on your k, and that is exactly the shape of the question.
verify_constant('8.3', q8_3, lambda v: curve(Eq(y, (2*x - 1)*exp(v*x))),
                1, ... if blank(q8_3) else 5*exp(q8_3), (0.5, 8))
""")

md(r"""
## 8.4 — 8.5 · May 2022 TZ1 Paper 3 Q2(b) · 4 marks · Paper 3

Consider $f(x)=(x-1)(x^2-8x+17)$ for $x\in\mathbb{R}$.

Show that the line $y=x-1$ is tangent to the curve $y=f(x)$ at the point
$\mathrm{A}(4,3)$ — first **8.4** by the gradient of $f$ at $\mathrm{A}$, and
then **8.5** the other way, by the $x$-coordinate at which $f(x)-(x-1)$ has a
repeated root. *[4]*
""")

code(r"""
q8_4 = ...       # f'(4)
q8_5 = ...       # the repeated root of f(x) - (x - 1) = 0

cubic = curve(Eq(y, (x - 1)*(x**2 - 8*x + 17)))
verify_slope('8.4', q8_4, cubic, at=4)
# The second way, checked as what it means: at a repeated root of f(x) - (x-1)
# the line y = x - 1 does not cross the curve, it touches it.
verify_tangent('8.5', x - 1, cubic, q8_5)
""")

md(r"""
## 8.6 — 8.8 · May 2023 TZ2 Paper 3 Q1(e) · 8 marks · Paper 3

For $1.4\le a\le1.5$, a value of $a$ exists such that the line $y=x$ is a
tangent to the graph of $y=\log_a x$ at a point $\mathrm{P}$.

Find the **exact** coordinates of $\mathrm{P}$ (**8.6**, **8.7**) and the
**exact** value of $a$ (**8.8**). *[8]*
""")

code(r"""
q8_6 = ...       # the x-coordinate of the tangency point, exactly
q8_7 = ...       # the y-coordinate of the tangency point, exactly
q8_8 = ...       # a, exactly

# Everything the question gave comes back out: the curve is built from your a,
# the point is yours, and the line y = x is the one line you were handed.
verify_tangent('8.6-8.8', x, shape(lambda: Eq(y, log(x)/log(q8_8)), q8_8),
               (q8_6, q8_7))
""")

# ------------------------------------------------------------- решения
md(r"""
---
# Solutions

## 1.1 — 1.3 · November 2021 Paper 1 Q5

**1.1** The gradient of the tangent *is* the derivative at the point of
contact: $f'(4)=6$. **A1**

**1.2** The point of contact lies on the tangent as well as on the curve, so
$f(4)=6\cdot4-1=23$. **A1**

**1.3** $h'(x)=f'\bigl(g(x)\bigr)g'(x)$. Now $g(4)=16-12=4$ — which is exactly
where we know something about $f$ — and $g'(4)=2\cdot4-3=5$, so
$$h'(4)=f'(4)\cdot5=30,\qquad h(4)=f\bigl(g(4)\bigr)=f(4)=23 .$$
Hence $y-23=30(x-4)$, that is $y=30x-97$. **M1A1A1**

## 1.4 · May 2025 TZ1 Paper 2 Q5(a)

Chain rule on the cosine; the $+15$ contributes nothing.
$$h'(x)=-15\sin\Bigl(\frac{\pi x}{50}\Bigr)\cdot\frac{\pi}{50}
=-\frac{3\pi}{10}\sin\Bigl(\frac{\pi x}{50}\Bigr),$$
so the gradient of $T_k$ is $-\dfrac{3\pi}{10}\sin\Bigl(\dfrac{\pi k}{50}\Bigr)$.
**M1A1A1**

The mark scheme splits the two A1s as *the $-15\sin$* and *the factor
$\pi/50$*, which tells you where the marks actually go: the inside derivative
is half the question.

## 1.5 — 1.6 · May 2022 TZ1 Paper 3 Q2(d)(ii)

$$g(a)=(a-r)\bigl(a^2-2a^2+a^2+b^2\bigr)=b^2(a-r),\qquad
g'(a)=0+a^2-2a^2+a^2+b^2=b^2 .$$
The first factor of $g'$ vanishes at $x=a$, which is why $g'(a)$ is so clean.
Then
$$y-b^2(a-r)=b^2(x-a)\;\Longrightarrow\;y=b^2(x-r),$$
and setting $y=0$ with $b>0$ gives $x=r$. **A1A1M1A1M1R1**

## 2.1 · November 2025 TZ3 Paper 1 Q9(c)

$f(-3)=\tfrac92-15+13=\tfrac52$, and $f'(x)=x+5$ gives $f'(-3)=2$. The normal
has gradient $-\tfrac12$:
$$y-\tfrac52=-\tfrac12(x+3)\;\Longrightarrow\;y=-\tfrac12x+1 .$$
**A1A1A1M1A1**

## 2.2 · November 2025 TZ1 Paper 3 Q1(a)(i)

$y=x^{-1}$ so $\frac{\mathrm{d}y}{\mathrm{d}x}=-x^{-2}$, which at $x=t$ is
$-\tfrac1{t^2}$. The normal is the negative reciprocal:
$$m_N=\frac{-1}{-1/t^2}=t^2 .\qquad\textbf{M1A1}$$

## 3.1 · May 2021 TZ1 Paper 2 Q10(b)

$f'(x)=-45\mathrm{e}^{-0.5x}=-1$ gives $\mathrm{e}^{-0.5x}=\tfrac1{45}$, so
$x=2\ln45$, and then
$$y=90\mathrm{e}^{-\ln45}=\frac{90}{45}=2 .$$
$\mathrm{Q}=(2\ln45,\,2)$. **A1M1A1A1**

The clean $2$ is your check that nothing was rounded on the way.
$2\ln45=\ln2025$ is the same answer.

## 3.2 · May 2021 TZ2 Paper 1 Q4(b)

$$\frac{2x}{x^2-16}=\frac13\;\Longrightarrow\;x^2-6x-16=0
\;\Longrightarrow\;(x-8)(x+2)=0 .$$
The domain is $x>4$, so $x=8$. **M1A1M1A1M1A1**

The mark scheme is explicit: *award A0 if the final answer includes additional
solutions.* Listing $-2$ as well is not a partial answer, it is a wrong one.

## 3.3 · November 2022 Paper 2 Q11(b)

$f'(x)=\mathrm{e}^{2x}(6x-5)$, and *parallel to $y=x$* means that equals $1$.
Nothing algebraic solves $\mathrm{e}^{2x}(6x-5)=1$; the calculator gives
$x=0.863$, and then
$$y=\mathrm{e}^{1.726}\bigl(3(0.863)-4\bigr)=-7.93 .$$
**M1A1A1** Substitute back into $f$, not into $f'$.

## 3.4 · May 2025 TZ3 Paper 2 Q5(b)

$$f'(x)=\frac{2(2x+a)^2(x+15-a)}{(x+5)^3},\qquad
f'(1)=\frac{(2+a)^2(16-a)}{108}=\tan70^\circ .$$
So $(2+a)^2(16-a)\approx296.7$, and the cubic gives $a=2.73$ and
$a=14.97\approx15.0$ (the third root is negative). **M1A1A1A1**

A line at $70^\circ$ has gradient $\tan70^\circ\approx2.75$ — not $70$.

## 4.1 · November 2021 Paper 2 Q8(a)

Write $w=xy$, so $w'=y+x\frac{\mathrm{d}y}{\mathrm{d}x}$ and
$\frac{\mathrm{d}}{\mathrm{d}x}(w\ln w)=w'(\ln w+1)$. Differentiating
$y=x-xy\ln(xy)$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}
=1-\Bigl(y+x\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)\bigl(1+\ln(xy)\bigr),$$
which is the printed line rearranged. Solving,
$$\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{1-y\bigl(1+\ln(xy)\bigr)}{1+x\bigl(1+\ln(xy)\bigr)} .$$
**M1A1A1**

*A note on the corpus this notebook is built from: it prints the required line
as $(1+\ln(xy))\frac{\mathrm{d}y}{\mathrm{d}x}+(1+\frac{y}{x})=0$, which does
not follow from the curve at all. The paper's line is the one above, and its
own mark scheme ends "$\dots=1$ leading to AG".*

## 4.2 · May 2022 TZ2 Paper 3 Q1(d)(i)

$$2y\frac{\mathrm{d}y}{\mathrm{d}x}=3x^2+1
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{3x^2+1}{2y},$$
and since $y=\pm\sqrt{x^3+x}$ on this curve,
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\pm\frac{3x^2+1}{2\sqrt{x^3+x}} .$$
**M1A1A1**

The $\pm$ is the curve having two branches, not an ambiguity in the algebra:
$\frac{3x^2+1}{2y}$ is single-valued at every point and the sign is decided by
which branch the point is on. That is why part (d)(ii) can conclude there are
no turning points — the numerator never vanishes.

## 4.3 · May 2024 TZ1 Paper 2 Q11(a)

$$\mathrm{e}^{x+y}\Bigl(1+\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)
=2x+2y\frac{\mathrm{d}y}{\mathrm{d}x}
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{2x-\mathrm{e}^{x+y}}{\mathrm{e}^{x+y}-2y}.$$
The chain rule on the left brings out the whole bracket, and forgetting the
$1$ inside it is the standard way to lose this. **M1A1A1M1A1**

## 4.4 · May 2025 TZ2 Paper 2 Q12(a)

$$8x+2y\frac{\mathrm{d}y}{\mathrm{d}x}-24+4\frac{\mathrm{d}y}{\mathrm{d}x}=0
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{24-8x}{2y+4}
=\frac{4(3-x)}{y+2}.$$
**M1A1A1A1**

The $4y$ term differentiates to $4\frac{\mathrm{d}y}{\mathrm{d}x}$, not to $4$.

## 4.5 · May 2023 TZ1 Paper 3 Q2(h)

$\ln g(x)=x\ln\bigl(\tfrac{S}{x}\bigr)=x(\ln S-\ln x)$. Differentiate both
sides — the left by the chain rule, the right by the product rule:
$$\frac{g'(x)}{g(x)}=\ln S-\ln x-1=\ln\Bigl(\frac{S}{x}\Bigr)-1 .$$
Since $g(x)\neq0$, the maximum has $g'(x)=0$, so
$$\ln\Bigl(\frac{S}{x}\Bigr)=1\;\Longrightarrow\;\frac{S}{x}=\mathrm{e}
\;\Longrightarrow\;x=\frac{S}{\mathrm{e}} .$$
**M1M1M1A1M1A1**

This is implicit differentiation used on a function that *is* explicit —
$g(x)=(S/x)^x$ — because no rule applies to $x$ in the base and the exponent
at once. That choice is the question.

*The corpus writes this function as $g(x)=\ln\bigl((S/x)^x\bigr)$, which is
$\ln g$, not $g$. The $x$-coordinate of the maximum happens to survive the
mistake; part (i) of the same question does not.*

## 5.1 · November 2021 Paper 2 Q8(b)

At $x=1$ the curve's own equation says $y=1-y\ln y$, whose only positive
solution is $y=1$. Then $\ln(xy)=0$ and
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{1-1\cdot1}{1+1\cdot1}=0 ,$$
so the tangent is $y=1$. **M1A1M1A1A1**

There is no formula for $y$ to substitute into. The second coordinate has to
come from the curve, and that is the whole of rung 5.

## 5.2 · May 2022 TZ2 Paper 3 Q1(f)(i)

$2y\frac{\mathrm{d}y}{\mathrm{d}x}=3x^2$, so at $\mathrm{P}(-1,-1)$
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{3(-1)^2}{2(-1)}=-\frac32,$$
and $y+1=-\tfrac32(x+1)$, that is $y=-\tfrac32x-\tfrac52$. **M1A1**

Two marks, and the reason this question exists is part (f)(ii): that tangent
meets the curve again at another *rational* point, which is how rational
points on elliptic curves are generated.

## 5.3 · May 2024 TZ1 Paper 2 Q11(b)

Horizontal means the numerator vanishes: $\mathrm{e}^{x+y}=2x$, so
$x+y=\ln(2x)$ and $y=\ln(2x)-x$. Putting that back into the curve,
$$2x=x^2+\bigl(\ln(2x)-x\bigr)^2
\;\Longrightarrow\;2x^2+\bigl(\ln 2x\bigr)^2-2x\ln 2x-2x=0 .$$
The calculator gives $x=0.331$ and $x=1.842$, and $y=\ln(2x)-x$ gives
$$\mathrm{P}=(0.331,\,-0.743),\qquad\mathrm{Q}=(1.84,\,-0.538).$$

Setting the whole fraction to zero rather than its numerator is the standard
loss here; finding one point and stopping is the other.

## 5.4 · May 2024 TZ1 Paper 2 Q11(d)

Gradient $-1$ means $2x-\mathrm{e}^{x+y}=-\bigl(\mathrm{e}^{x+y}-2y\bigr)$,
which simplifies to $x=y$ — the line of symmetry the question drew for you.
Then $\mathrm{e}^{2x}=2x^2$, so $x=-0.451$ and the point is
$(-0.451,\,-0.451)$.

## 6.1 · May 2022 TZ2 Paper 2 Q12(b)

Differentiate $\frac{\mathrm{d}P}{\mathrm{d}t}=kP-\frac{kP^2}{N}$ with respect
to $t$, remembering that $P$ is a function of $t$:
$$\frac{\mathrm{d}^2P}{\mathrm{d}t^2}
=k\frac{\mathrm{d}P}{\mathrm{d}t}-\frac{2kP}{N}\frac{\mathrm{d}P}{\mathrm{d}t}
=k\frac{\mathrm{d}P}{\mathrm{d}t}\Bigl(1-\frac{2P}{N}\Bigr).$$
Now substitute the original equation back into itself:
$$\frac{\mathrm{d}^2P}{\mathrm{d}t^2}
=k^2P\Bigl(1-\frac{P}{N}\Bigr)\Bigl(1-\frac{2P}{N}\Bigr).\qquad\textbf{M1A1A1A1}$$

That second bracket is what makes the next part work: growth is fastest where
$\frac{\mathrm{d}^2P}{\mathrm{d}t^2}=0$ with $P\neq0,N$, that is at
$P=\tfrac{N}{2}$.

## 6.2 — 6.3 · May 2023 TZ1 Paper 2 Q12(b)

**6.2** Substitute straight in: $\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{0-9}{0+1}=-3$. **A1**

**6.3** Differentiate the equation, by the quotient rule on the right and
implicitly throughout:
$$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=\frac{\bigl(2xy+x^2\frac{\mathrm{d}y}{\mathrm{d}x}
-\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)(x^2+1)
-(x^2y-y)(2x)}{(x^2+1)^2}.$$
At $x=0$, $y=3$, $\frac{\mathrm{d}y}{\mathrm{d}x}=-3$ this is
$$\frac{(0+0+3)(1)-(-3)(0)}{1}=3 .\qquad\textbf{M1M1A1A1}$$

The $-\frac{\mathrm{d}y}{\mathrm{d}x}$ inside the bracket comes from
differentiating the $-y$ in the numerator, and it is the term that gets lost.

## 6.4 — 6.5 · November 2025 TZ3 Paper 2 Q12(b)

Differentiate $\bigl(x^2+xy\bigr)\frac{\mathrm{d}y}{\mathrm{d}x}
=x^2+xy-3y^2$ throughout, using $\frac{\mathrm{d}}{\mathrm{d}x}(xy)
=y+x\frac{\mathrm{d}y}{\mathrm{d}x}$ on both sides:
$$\Bigl(2x+y+x\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)\frac{\mathrm{d}y}{\mathrm{d}x}
+\bigl(x^2+xy\bigr)\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2x+y+x\frac{\mathrm{d}y}{\mathrm{d}x}-6y\frac{\mathrm{d}y}{\mathrm{d}x}.$$
Collecting the first-derivative terms on the right gives
$$\bigl(x^2+xy\bigr)\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2x+y-x\Bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)^{2}
-(x+7y)\frac{\mathrm{d}y}{\mathrm{d}x},$$
and substituting $\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{x^2+xy-3y^2}{x^2+xy}$ turns it into an expression in $x$ and $y$ alone.
**A1M1A1A1**

**6.5** At $x=1$, $y=\tfrac32$ the first derivative is
$\frac{1+\frac32-\frac{27}{4}}{1+\frac32}=-\frac{17}{10}$, so
$$\tfrac52\cdot\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2+\tfrac32-(-1.7)^2-\bigl(1+\tfrac{21}{2}\bigr)(-1.7)=20.16,$$
$$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}=8.064=\frac{1008}{125}.\qquad\textbf{M1A1}$$

*The corpus prints that relation with $+2x\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$
where the paper has $-x\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$. The
paper's version gives $8.064$, which is what the mark scheme prints next.*

## 7.1 — 7.2 · May 2023 TZ2 Paper 1 Q8(b)

$f'(k)=-\sin k$ and $g'(k)=\sec^2k=\dfrac{1}{\cos^2k}=\dfrac{1}{\sin k}$,
using the given $\cos^2k=\sin k$. So
$$f'(k)\,g'(k)=-\sin k\cdot\frac{1}{\sin k}=-1,$$
and the tangents are perpendicular. **A1A1R1**

Without that substitution the product is $-\sin k\sec^2k$ and stays a function
of $k$; the identity from part (a) is the entire question.

## 7.3 · November 2023 Paper 3 Q2(a)(i)

A point $(x,y)$ on $y=mx$ has $m=\dfrac{y}{x}$, so the gradient of $L$ is
$\dfrac{y}{x}$. **A1**

One mark, and the whole 31-mark investigation turns on it: written in $x$ and
$y$, the family's gradient goes straight into the perpendicularity condition,
and $\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{x}{y}$ integrates to
$x^2+y^2=k$ — circles cutting every line through the origin square.

## 7.4 — 7.5 · November 2023 Paper 3 Q2(d)

$$y^2=4a^2-4ax\;\Longrightarrow\;2y\frac{\mathrm{d}y}{\mathrm{d}x}=-4a
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{2a}{y},$$
$$y^2=4b^2+4bx\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{2b}{y} .$$
At $\mathrm{M}$, where $y=2\sqrt{ab}$, these are $-\dfrac{a}{\sqrt{ab}}$ and
$\dfrac{b}{\sqrt{ab}}$, whose product is $-\dfrac{ab}{ab}=-1$. **M1A1M1A1A1**

Both curves are written as $y^2=\dots$, so implicit differentiation is not a
stylistic choice: solving for $y$ puts a square root and a $\pm$ into
everything.

## 8.1 — 8.2 · May 2021 TZ1 Paper 1 Q4(b)(c)

**8.1** $f'(x)=-2(x-h)$ and $g'(3)=\mathrm{e}$, so a common tangent at $x=3$
needs
$$-2(3-h)=\mathrm{e}\;\Longrightarrow\;h=3+\frac{\mathrm{e}}{2}
=\frac{\mathrm{e}+6}{2}. \qquad\textbf{A1M1A1}$$

**8.2** And the values agree there too:
$$-(3-h)^2+2k=\mathrm{e}+k .$$
With $3-h=-\tfrac{\mathrm{e}}{2}$ the left side is
$-\tfrac{\mathrm{e}^2}{4}+2k$, so
$$k=\mathrm{e}+\frac{\mathrm{e}^2}{4}\approx4.57 .\qquad\textbf{M1A1A1}$$

*The corpus prints $k=\frac{2\mathrm{e}+\mathrm{e}^2}{4}\approx3.21$ here. It
is wrong; the paper's value is the one above.*

## 8.3 · May 2022 TZ1 Paper 1 Q4

Product rule:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=(2x-1)k\mathrm{e}^{kx}+2\mathrm{e}^{kx}
=\mathrm{e}^{kx}(2kx-k+2),$$
so at $x=1$ the gradient is $\mathrm{e}^{k}(k+2)$. Parallel to
$y=5\mathrm{e}^{k}x$ means that equals $5\mathrm{e}^{k}$, and since
$\mathrm{e}^{k}\neq0$,
$$k+2=5\;\Longrightarrow\;k=3 .\qquad\textbf{M1A1A1M1A1}$$

Saying $\mathrm{e}^{k}\neq0$ out loud is the difference between cancelling and
dividing by something that might be zero.

## 8.4 — 8.5 · May 2022 TZ1 Paper 3 Q2(b)

**Method 1.** $f(4)=3\cdot1=3$, so $\mathrm{A}$ is on the curve, and the line
gives $4-1=3$ as well. Then
$$f'(x)=(x^2-8x+17)+(x-1)(2x-8),\qquad f'(4)=1+3(0)=1,$$
which is the gradient of $y=x-1$. Same point, same gradient: tangent. **M1A1**

**Method 2.** $f(x)-(x-1)=(x-1)(x^2-8x+17)-(x-1)=(x-1)(x^2-8x+16)
=(x-1)(x-4)^2$, so $x=4$ is a **double** root, and a double root is what
touching means. **R1**

The second method is faster on a cubic and needs no calculus at all — worth
having when the algebra factors as cleanly as it does here.

## 8.6 — 8.8 · May 2023 TZ2 Paper 3 Q1(e)

Write $y=\log_a x=\dfrac{\ln x}{\ln a}$. Tangency to $y=x$ needs two things.
The gradient:
$$\frac{1}{x\ln a}=1\;\Longrightarrow\;x=\frac{1}{\ln a},$$
and the point on both:
$$\frac{\ln x}{\ln a}=x .$$
Substituting the first into the second gives
$\ln\bigl(\tfrac1{\ln a}\bigr)=1$, so $\tfrac1{\ln a}=\mathrm{e}$ and
$$x=\mathrm{e},\qquad\mathrm{P}=(\mathrm{e},\mathrm{e}),\qquad
a=\mathrm{e}^{1/\mathrm{e}}\approx1.4447 .$$
**A1M1A1M1A1A1M1A1**

The $1.4\le a\le1.5$ is a check on the answer, not a route to it. And once
$x=\mathrm{e}$ is known, $\mathrm{P}$ needs no more work: it is on $y=x$.

---
### Where these 32 questions came from

| technique | questions | marks |
| --- | --- | --- |
| 1. The tangent at a known point | 5 | 14 |
| 2. The normal | 2 | 7 |
| 3. The gradient is given, the point is not | 4 | 17 |
| 4. The curve is an equation | 5 | 21 |
| 5. A tangent to such a curve | 4 | 20 |
| 6. Differentiating the relation again | 4 | 15 |
| 7. A right angle as a condition | 3 | 9 |
| 8. Touching as a condition | 5 | 23 |

Section 7 shows nine marks rather than fourteen because the corpus counts the
November 2023 Paper 3 question twice — once per zone — and the paper is one
paper, printed as Common. It is here once.

Ten of the 32 come from Paper 3, and between them they carry 42 marks: this
material lives inside long investigations, where a tangent is one step of
twenty-eight and never the point of the question.
""")


def build():
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    os.makedirs(os.path.dirname(NOTEBOOK), exist_ok=True)
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    codes = sum(1 for cc in cells if cc['cell_type'] == 'code')
    print(f'{NOTEBOOK}: {len(cells)} ячеек, из них {codes} с кодом')


if __name__ == '__main__':
    build()
