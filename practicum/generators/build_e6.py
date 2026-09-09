"""Собирает практикум E6: площади, объёмы вращения, накопление.

Тринадцатый практикум серии и вторая половина темы
calculus.integration_applications. Лестница из восьми приёмов идёт по тому,
что меряют: 1–2 — плоскую область, 3–5 — тело вращения, 6 — его обёртку,
7–8 — движение и накопление.

Девятнадцатое понятие равенства ответов: измеренное узнаётся повторным
измерением, а не повторением выкладки. Ответ здесь — число, и число это
что-то меряет. Сверять его со вторым таким же, полученным той же формулой,
бессмысленно: совпадут и две одинаковые ошибки. Поэтому раздел kit меряет
заново и меряет по определению меры: площадь — суммой тонких полос, объём —
стопкой дисков, поверхность — набором усечённых конусов, путь — полной
вариацией положения.

Отсюда главное свойство раздела: он не берёт производных ни одной, тогда
как раздел E5 не берёт ни одного интеграла. Две половины основной теоремы,
и ни одна не умеет работы другой.

Шесть новых проверок. `verify_region` — площадь как сумма полос |верх − низ|,
с пределами, которые она при нужде находит делением пополам сама.
`verify_solid` — объём как стопка дисков и колец. `verify_surface` —
поверхность как набор усечённых конусов, по настоящей длине звена, без
dy/dx. `verify_travelled` — путь как полная вариация положения, без поиска
нулей скорости. `verify_position` — перемещение и положение с начальным
значением. `verify_amount` — накопленное числом или выражением от времени.

Теория здесь разбирается на других примерах, чем задачи рядом: разобранный
пример решает задачу за ученика, и тогда ему остаётся подставить числа.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e6.py прогоняет по нему весь ноутбук и требует,
чтобы каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e6-areas-volumes.ipynb')

TRIGGER = {1: 'voly', 2: 'motion', 3: 'under', 4: 'skin', 5: 'between',
           6: 'ring', 7: 'accum', 8: 'volx', 9: 'motion', 10: 'between',
           11: 'voly', 12: 'accum'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1': '8*pi',
    'q2': '-3',
    'q3': 'Rational(23, 3)',
    'q4': '4*pi*n',
    'q5': 'Rational(9, 2)',
    'q6': 'Rational(1, 4)',
    'q7': 'Rational(1, 3)',
    'q8': 'Rational(1, 6)',
    'q9': 'pi/2',
    'q10': '3*pi**2/16',
    'q11': '3*pi*r**4/4',
    'q12': '21*pi',
    'q13': '17*pi/15',
    'q14': 'pi*h**3/6',
    'q15': '6',
    'q16': '12*sqrt(10)*pi',
    'q17': '4*pi*r**2',
    'q18': '30*pi',
    'q19': '3',
    'q20': '13',
    'q21': '37.1',
    'q22': '-22.2',
    'q23': 'v0 - log(1 + v0)',
    'q25': '700 - 600*exp(-t/10) - 5*t**2/2',
    'q26': '15.1',
    'q27': '567',
    'q28': 'Rational(32, 3)',
    'q29': 'Rational(1280, 3)',
    'q30': '480',
    'q31': 'Rational(160, 3)',
    'q32': '4',
    'q33': '5',
    'qt': '27*pi/2',
}

cells = []


def _lines(src):
    text = src.strip('\n')
    return [line + '\n' for line in text.split('\n')[:-1]] + [text.split('\n')[-1]]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Practicum E6: areas, volumes of revolution, accumulation

**197 marks, 46 blocks, eight techniques.** One question runs through all of
them: *what does this integral measure?* Every technique here is a way of
turning a picture into a definite integral — and the marks are almost never
in the integration.

**Material.** The half of `calculus.integration_applications` in the AA HL
archive where the answer is a measurement, sessions May 2021 — November 2025.
The whole topic is 354 marks — twice what a practicum may hold — so it is cut
in two by what the question asks for: *find $\int x(\ln x)^2\,\mathrm{d}x$* is
E5, *find the area* is here. The two halves share functions freely: in
`May 2025 TZ1 Paper 1 Q12`, part (c) asks for $\int\cos^4x\,\mathrm{d}x$ and
belongs to E5, part (d) uses it for a volume and belongs here.

**This practicum is in English,** like B2 to B5 and E1 to E5. The checks speak
whichever language the notebook asks them to, and this one asks for English in
the setup cell.

**The one thing to carry out of here.**

> A measurement is not a formula, it is a **quantity**. The integral you write
> down is a claim about what you are adding up — thin strips, thin discs, thin
> frustums, tiny displacements. When an answer here is wrong it is almost never
> because the integration failed; it is because the thing being added up was
> the wrong thing.

So the habit worth building is: **before integrating, say out loud what one
slice looks like.** A strip of width $\mathrm{d}x$ and height (top $-$ bottom).
A disc of radius $R$ and thickness $\mathrm{d}y$. If you can say the slice,
the integral writes itself; if you cannot, no amount of algebra will save it.

**Where the calculator sits.** This is the mirror image of E5. There, 55% of
the marks were Paper 1 and the calculator was useless — it does not do
substitution. Here **119 of the 197 marks carry a calculator** and 106 are
Paper 2, because measuring is exactly what a GDC is good at. Which means the
marks move: they are in setting the integral up and in reading *total distance*
rather than *displacement*, not in evaluating anything.

**How to use this notebook.** Fill in each `...` and run the cell. A check
prints ✅, ❌ with a reason, or ⬜ if you have not answered yet. Nothing here
stores the answer: every check measures the region, the solid or the path
itself and compares. That also means a check can tell you *which* mistake you
made — it knows what the displacement is, so it can recognise it when you hand
it in as a distance.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, log, Eq

language('en')                 # this notebook is in English, and so are the checks

a, b, c, h, m, n, q, r, s, w, v0 = symbols('a b c h m n q r s w v0')
                               # x, y, t, u, v, A, C, k already come from kit

print('ready; sympy', sp.__version__)
print('a region:   between y =', 6 - x**2, 'and y =', x)
print('its area:   ', Rational(125, 6))
print('a solid:    y =', 2 - x, 'turned about the x-axis, 0 <= x <= 2')
print('its volume: ', 8*pi/3)
""")

md(r"""
---
## Map of techniques

| # | Technique | What is being measured | The slice |
| --- | --- | --- | --- |
| 1 | Area under a curve | region between one curve and an axis | strip, height $\|y\|$ |
| 2 | Area between curves | region between two graphs | strip, height $\|$top $-$ bottom$\|$ |
| 3 | Volume about the $x$-axis | solid from turning a region | disc, radius $y$, thickness $\mathrm{d}x$ |
| 4 | Volume about the $y$-axis | the same, turned the other way | disc, radius $x$, thickness $\mathrm{d}y$ |
| 5 | Washer, or volume as a condition | solid with a hole; or a solid of known size | washer, radii $R$ and $r$ |
| 6 | Surface of revolution | the skin, not the filling | frustum, slant $\mathrm{d}l$ |
| 7 | Displacement and distance | where a point got to; how far it went | tiny move $v\,\mathrm{d}t$ |
| 8 | Accumulated change | how much has arrived | tiny amount $R'\,\mathrm{d}t$ |

**The ladder goes by what is being measured, and each rung is harder to
picture than the last, not harder to integrate.**

**Rungs 1–2 — a flat region.** Fifty-three marks. Nineteen of the 22 marks on
rung 1 are Paper 1, and the answers there are exact: $12\pi$, $4\pi n$,
$4+\tfrac12\ln\tfrac37$.

**Rungs 3–5 — a solid.** Seventy-five marks, the largest block of the topic.
Rung 4 is where the algebra lives: turning about the $y$-axis means expressing
$x$ through $y$ before any integral exists at all.

**Rung 6 — the surface.** Thirteen marks, all of them one Paper 3 investigation
from November 2022. The formula is printed in the question; the work is
simplifying the radical.

**Rungs 7–8 — motion and accumulation.** Sixty-one marks, and 42 of them carry
a calculator. Rung 7 is one distinction repeated twelve times, and rung 8 is
almost entirely story problems.

**The four facts the whole topic runs on.**

$$A=\int_a^b |f(x)-g(x)|\,\mathrm{d}x \qquad
V=\pi\int_a^b y^2\,\mathrm{d}x \quad\text{or}\quad \pi\int_c^d x^2\,\mathrm{d}y$$

$$A_{\text{surface}}=2\pi\int y\sqrt{1+\left(\frac{\mathrm{d}y}{\mathrm{d}x}\right)^2}\,\mathrm{d}x
\qquad
\text{distance}=\int_{t_1}^{t_2}|v(t)|\,\mathrm{d}t$$

Everything else in these 197 marks is deciding which one you are looking at,
and what its limits are.
""")

# ================================================================== Part I
md(r"""
---
# Part I — flat regions

## Theory 1. Area is not the integral

$\int_a^b f$ is a **signed** quantity: the parts of the curve below the axis
come in negative and cancel the parts above. Area is not signed. When a
question says *area*, and the curve crosses the axis between the limits, those
are two different numbers and only one of them is worth marks.

**A worked case.** Take $y=x^3-x$ on $[-1,1]$. It is odd, so

$$\int_{-1}^{1}(x^3-x)\,\mathrm{d}x=0,$$

and yet the region between the curve and the axis plainly has some area. The
curve crosses at $x=-1,0,1$, so the area is taken piece by piece:

$$A=\left|\int_{-1}^{0}(x^3-x)\,\mathrm{d}x\right|
+\left|\int_{0}^{1}(x^3-x)\,\mathrm{d}x\right|
=\frac14+\frac14=\frac12 .$$

Zero and one half. The integral answered a different question.

**So the routine for *area* is always three steps:**

1. find where the curve meets the axis **inside the limits**;
2. integrate over each piece separately;
3. add the **absolute values**.

**The word to watch for is *total*.** *Find the total area* and *find
$\int_0^4 f$* are different instructions, and in `November 2022 Paper 2 Q2(c)`
the word *total* is the whole difference between 4.61 and something smaller.

**A note on how the checks in this notebook behave.** They do not integrate.
They chop the interval into thin strips, measure each one and add up — which
is what an area *is*. That is why a check can tell you that what you handed in
is the signed integral: it computes both and recognises the other one.
""")

md(r"""
## Task 1 🟢 — the same curve, two questions

*Modelled on May 2021 TZ2 Paper 1 Q10(b), 5 marks · no calculator,
and November 2022 Paper 2 Q2(c), 3 marks · calculator*

**(a)** The curve $y=4+4\cos x$ lies above the $x$-axis. Find the area of the
region enclosed by the curve and the $x$-axis between $x=\pi$ and $x=3\pi$.

**(b)** Now the curve $y=x^2-4$ on $0\le x\le 3$. Find
$\displaystyle\int_0^3(x^2-4)\,\mathrm{d}x$.

**(c)** Find the **total area** of the region enclosed by $y=x^2-4$, the
$x$-axis and the line $x=3$.

Parts (b) and (c) are the same curve over the same interval. If your two
answers are equal, one of them is wrong.
""")

code(r"""
q1 = ...         # (a) the area between pi and 3pi
q2 = ...         # (b) the value of the integral from 0 to 3
q3 = ...         # (c) the total area

verify_region('1a', q1, 4 + 4*cos(x), 0, pi, 3*pi)
verify_integral('1b', q2, x**2 - 4, 0, 3)            # a signed total: no modulus
verify_region('1c', q3, x**2 - 4, 0, 0, 3)
""")

md(r"""
## Task 2 🔴 — an area that depends on which arch you take

*May 2023 TZ2 Paper 1 Q12(c), 7 marks · no calculator*

The curve $y=\cos\sqrt x$ crosses the $x$-axis where $\sqrt x$ is an odd
multiple of $\tfrac\pi2$. Write $x_n=\left(\dfrac{(2n-1)\pi}{2}\right)^2$ for
$n=1,2,3,\dots$, so that consecutive zeros are $x_n$ and $x_{n+1}$, and let
$R_n$ be the region between the curve and the axis over $x_n\le x\le x_{n+1}$.

Find the area of $R_n$ in terms of $n$.

The antiderivative $2\sqrt x\sin\sqrt x+2\cos\sqrt x$ is E5's business and you
may take it as given. What is asked here is the *area*, so the sign of what
comes out of the limits is not the answer — its size is.
""")

code(r"""
q4 = ...         # the area of R_n, in terms of n

# the check measures the region for four different n at once
verify_region('2', q4, cos(sqrt(x)), 0,
              ((2*n - 1)*pi/2)**2, ((2*n + 1)*pi/2)**2,
              params={n: (1, 2, 3, 4)})
""")

md(r"""
## Theory 2. Two curves, and the limits you are not given

For a region between two graphs the slice is a strip of height
(top $-$ bottom), and the limits are wherever the two graphs meet. Almost
always the question does not give them; finding them is the first mark.

**A worked case.** The region enclosed by $y=6-x^2$ and $y=x$. They meet where

$$6-x^2=x\quad\Longrightarrow\quad x^2+x-6=0\quad\Longrightarrow\quad x=-3,\ 2,$$

and between those the parabola is on top, so

$$A=\int_{-3}^{2}\bigl((6-x^2)-x\bigr)\,\mathrm{d}x
=\left[6x-\frac{x^3}{3}-\frac{x^2}{2}\right]_{-3}^{2}=\frac{125}{6}.$$

**Three things go wrong here, in order of frequency.**

**Subtracting the wrong way round.** The answer comes out negative and gets
handed in negative. An area never is.

**Not noticing that the curves swap.** If top and bottom change places inside
the interval, one integral is not enough: split at the crossing, or integrate
$|f-g|$.

**Rounding the limits.** On Paper 2 the crossings often come from the GDC as
$4.8062\ldots$ Round the *answer* to three significant figures, never the
limits — an error in a limit is multiplied by the height of the strip there.

**The special case worth knowing.** A region bounded by $y=f(x)$ and
$y=f^{-1}(x)$ is symmetric about the line $y=x$, because the two graphs are
reflections of each other in it. So it is enough to measure the half on one
side of $y=x$ and double — and in `May 2021 TZ1 Paper 2 Q10(e)` that doubling
*is* the whole two marks.
""")

md(r"""
## Task 3 🟢 — find the limits first

*Modelled on November 2025 TZ1 Paper 1 Q3(b), 4 marks, and
May 2024 TZ1 Paper 1 Q4(b), 4 marks · both no calculator*

**(a)** Find the area of the region enclosed by the line $y=-3x+9$ and the
parabola $y=-x^2+9$.

**(b)** Find the area of the region enclosed by $y=\cos x$ and $y=\sin 2x$
between $x=\dfrac{\pi}{2}$ and $x=\dfrac{5\pi}{6}$.

In (a) you are given no limits at all — that is the point. In (b) you are given
them, and the question is whether one of the curves overtakes the other in
between.
""")

code(r"""
q5 = ...         # (a)
q6 = ...         # (b)

# no limits passed: the check finds where the two graphs meet, by bisection
verify_region('3a', q5, -x**2 + 9, -3*x + 9)
verify_region('3b', q6, cos(x), sin(2*x), pi/2, 5*pi/6)
""")

md(r"""
## Task 4 🟡 — a curve and its own inverse

*Modelled on May 2021 TZ1 Paper 2 Q10(d)(e), 7 marks, and
May 2025 TZ1 Paper 2 Q12(e), 4 marks · calculator*

Let $f(x)=x^2$ for $x\ge 0$. Its inverse is $f^{-1}(x)=\sqrt x$, and the two
graphs enclose a region.

**(a)** Find the area of that region.

**(b)** The line $y=x$ cuts the region in two. Find the area of the half that
lies **above** $y=x$.

Part (b) has a one-line answer and a five-line answer, and they give the same
number. Worth finding the one-line one.
""")

code(r"""
q7 = ...         # (a) the whole region
q8 = ...         # (b) the half above y = x

verify_region('4a', q7, sqrt(x), x**2, 0, 1)
verify_region('4b', q8, sqrt(x), x, 0, 1)
""")

# ================================================================= Part II
md(r"""
---
# Part II — solids

## Theory 3. The disc, and what gets squared

Turn a region about an axis and slice the solid perpendicular to that axis.
Each slice is a disc: radius = the distance from the axis to the curve,
thickness = $\mathrm{d}x$. Its volume is $\pi R^2\,\mathrm{d}x$, and the
solid's volume is their sum.

$$V=\pi\int_a^b\bigl(f(x)\bigr)^2\,\mathrm{d}x$$

**A worked case, and a familiar answer.** Take $y=2-x$ on $0\le x\le 2$ turned
about the $x$-axis. That is a cone of radius 2 and height 2, and

$$V=\pi\int_0^2(2-x)^2\,\mathrm{d}x=\pi\left[-\frac{(2-x)^3}{3}\right]_0^2
=\frac{8\pi}{3},$$

which is exactly $\tfrac13\pi r^2h$ with $r=h=2$. The formula you learned in
geometry is this integral, done once.

**Where the marks are lost.**

**The $\pi$.** Written down at the start and dropped somewhere in the middle.
A check in this notebook will tell you when your answer is $V/\pi$ — that is
how common it is.

**$(f(x))^2$, not $f(x^2)$.** Square the whole function, including its
coefficient, before integrating anything.

**Squaring after integrating.** $\left(\int f\right)^2$ and $\int f^2$ are not
the same number and never were.

**The limits belong to the axis you are turning about.** For the $x$-axis they
are $x$-values, even when the region was described to you by its $y$-values.
""")

md(r"""
## Task 5 🟡 — two solids about the $x$-axis

*Modelled on May 2024 TZ1 Paper 1 Q6, 6 marks, and
May 2025 TZ1 Paper 1 Q12(d), 4 marks · both no calculator*

**(a)** The region under $y=\sqrt{x\sin x^2}$ for
$0\le x\le\sqrt{\tfrac\pi2}$ is rotated through $2\pi$ about the $x$-axis.
Find the volume of the solid formed.

**(b)** The region under $y=\cos^2 x$ for $0\le x\le\dfrac\pi2$ is rotated
through $2\pi$ about the $x$-axis. Find the volume.

In (a) the square undoes the square root and leaves an integrand that a
substitution finishes. In (b) squaring gives $\cos^4x$, which is E5's
$\tfrac{3\pi}{8}$ over a full period — here you need it over a quarter of one.
""")

code(r"""
q9 = ...         # (a)
q10 = ...        # (b)

verify_solid('5a', q9, sqrt(x*sin(x**2)), 0, sqrt(pi/2))
verify_solid('5b', q10, cos(x)**2, 0, pi/2)
""")

md(r"""
## Theory 4. About the $y$-axis: the algebra comes first

Turning about the $y$-axis means slicing horizontally. The disc now has radius
$x$ and thickness $\mathrm{d}y$:

$$V=\pi\int_c^d x^2\,\mathrm{d}y .$$

Nothing in that expression is a function of $x$. So before there is an integral
at all, the curve has to be rewritten as $x$ in terms of $y$, and the limits
have to be $y$-values.

**A worked case.** The region between $y=x^2$, the $y$-axis and $y=4$, turned
about the $y$-axis. Rewrite: $x^2=y$. Then

$$V=\pi\int_0^4 y\,\mathrm{d}y=\pi\left[\frac{y^2}{2}\right]_0^4=8\pi .$$

Note how little work the integral was, and that all of it happened after the
rewriting. Note also that $x^2$ was wanted, not $x$ — so the square root that
solving would have produced was never needed. When the curve gives you $x^2$
directly, do not take a root only to square it again.

**When the rewrite needs the inverse.** $y=3\ln(x-1)$ becomes
$x=1+\mathrm{e}^{y/3}$, and then $x^2=\left(1+\mathrm{e}^{y/3}\right)^2$ has
**three** terms. Expanding
$\left(p+q\right)^2$ as $p^2+q^2$ is a marked error and a common one.

**Choosing the branch.** $x^2=16y$ has two roots. The region tells you which:
if it lies to the right of the axis, $x=+4\sqrt y$.
""")

md(r"""
## Task 6 🟡 — about the $y$-axis, with and without letters

*Modelled on May 2025 TZ3 Paper 1 Q7, 6 marks · no calculator,
and May 2022 TZ1 Paper 2 Q10(c), 5 marks · calculator*

**(a)** The curve $x^2+y^3=r^3$, where $r>0$, is drawn for $0\le y\le r$ and
$x\ge 0$. The region between it and the $y$-axis is rotated through $2\pi$
about the $y$-axis. Find the volume in terms of $r$.

**(b)** The curve $x^2-y^2=4$ with $x>0$ is drawn for $0\le y\le 3$. The region
between it and the $y$-axis is rotated through $2\pi$ about the $y$-axis. Find
the volume.

Both are here to make the same point: $x^2$ is what the formula wants, and both
equations hand it over without any inverse function being needed.
""")

code(r"""
q11 = ...        # (a) in terms of r
q12 = ...        # (b)

# the radius is written as a function of y, so var=y and the limits are y-values
verify_solid('6a', q11, sqrt(r**3 - y**3), 0, r, var=y, axis='y',
             params={r: (1, 2, 3)})
verify_solid('6b', q12, sqrt(y**2 + 4), 0, 3, var=y, axis='y')
""")

md(r"""
## Theory 5. Two radii, and reading the volume backwards

When the solid has a hole, the slice is a washer: an outer disc with an inner
one removed. Its volume is $\pi R^2\,\mathrm{d}y-\pi r^2\,\mathrm{d}y$, so

$$V=\pi\int_c^d\left(R^2-r^2\right)\mathrm{d}y .$$

**The error this invites** is $\pi\int (R-r)^2$. It is not the same thing, and
it is never right. A worked case: the region between $y=x$ and $y=x^2$ turned
about the $x$-axis. Here $R=x$, $r=x^2$, and

$$V=\pi\int_0^1\left(x^2-x^4\right)\mathrm{d}x=\pi\left(\frac13-\frac15\right)
=\frac{2\pi}{15},$$

whereas $\pi\int_0^1(x-x^2)^2\,\mathrm{d}x=\dfrac{\pi}{30}$ — four times too
small. Subtract the squares, not the radii.

**Reading it backwards.** Half the marks on this rung are questions where the
volume is *given* and something else is asked: the radius $k$ that makes a bowl
hold 300 cm³, the depth $h$ that makes it hold 285. Nothing changes except the
last line: write the volume as an expression, set it equal to the number, solve.

**And one result worth carrying around.** A sphere of radius $r$ with a
cylindrical hole of height $h$ drilled straight through the middle leaves a
ring whose volume is $\dfrac{\pi h^3}{6}$ — **with no $r$ in it at all**. Two
rings of the same height have the same volume whether they came from a marble
or from a planet. `May 2023 TZ1 Paper 1 Q9` is that fact, and the $r$
cancelling is the moment the question is designed around.
""")

md(r"""
## Task 7 🟡 — a washer, and a ring with no radius in it

*Modelled on November 2025 TZ1 Paper 2 Q8, 6 marks · calculator,
and May 2023 TZ1 Paper 1 Q9, 7 marks · no calculator*

**(a)** The region enclosed by $x=2y$ and $x=y^2$ for $0\le y\le 1$ is rotated
through $2\pi$ about the $y$-axis. Find the volume of the solid formed.

**(b)** A sphere of radius $r$ has a cylindrical hole of height $h$ bored
through its centre, along the $y$-axis, leaving a ring. Show — by finding it —
that the volume of the ring is $\dfrac{\pi h^3}{6}$, and then find the value of
$h$ for which the ring has volume $36\pi$.

For (b): the sphere is $x^2+y^2=r^2$, the hole has radius
$\sqrt{r^2-\tfrac{h^2}{4}}$, and the ring runs from $y=-\tfrac h2$ to
$y=\tfrac h2$. Write your formula for the volume in terms of $h$ — the check
will try it on three different spheres at once, which is the only honest way to
show that $r$ really is gone.
""")

code(r"""
q13 = ...        # (a)
q14 = ...        # (b) the volume of the ring, in terms of h
q15 = ...        # (b) the h that makes the ring 36*pi

verify_solid('7a', q13, 2*y, 0, 1, inner=y**2, var=y, axis='y')
verify_solid('7b', q14, sqrt(r**2 - y**2), -h/2, h/2,
             inner=sqrt(r**2 - h**2/4), var=y, axis='y',
             params={r: (5, 7, 9), h: (4, 6, 8)})
verify_solid('7c', 36*pi, sqrt(r**2 - y**2),
             ... if blank(q15) else -q15/2, ... if blank(q15) else q15/2,
             inner=... if blank(q15) else sqrt(r**2 - q15**2/4),
             var=y, axis='y', params={r: (5, 7, 9)})
""")

# ================================================================ Part III
md(r"""
---
# Part III — the surface, and motion

## Theory 6. The skin: a sum of frustums

Volume adds up discs. Surface area adds up **rings of skin**, and a thin ring
of skin is the side of a frustum: radius $y$, slant length $\mathrm{d}l$. Since
$\mathrm{d}l=\sqrt{\mathrm{d}x^2+\mathrm{d}y^2}
=\sqrt{1+\left(\frac{\mathrm{d}y}{\mathrm{d}x}\right)^2}\,\mathrm{d}x$,

$$A=2\pi\int_{x_1}^{x_2} y\sqrt{1+\left(\frac{\mathrm{d}y}{\mathrm{d}x}\right)^2}\,\mathrm{d}x .$$

**You are given this formula in the question.** All thirteen marks of this rung
are one Paper 3 investigation, and it prints the formula for you. The work is
never remembering it; the work is that the expression under the root always
collapses, and you have to make it collapse.

**A worked case.** The paraboloid from $y=\sqrt{2x}$, $0\le x\le 2$. Here
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\dfrac{1}{\sqrt{2x}}$, so

$$y\sqrt{1+\frac{1}{2x}}=\sqrt{2x}\cdot\frac{\sqrt{2x+1}}{\sqrt{2x}}=\sqrt{2x+1},$$

and the whole thing becomes
$A=2\pi\int_0^2\sqrt{2x+1}\,\mathrm{d}x=\dfrac{2\pi\left(5\sqrt5-1\right)}{3}$.
Notice that the $y$ outside and the denominator inside the root cancelled each
other exactly. They always do — that is why the formula is usable at all.

**The two errors.** Dropping the $y$ leaves you with the **length** of the
curve, which is a perfectly good number and the wrong one. Writing $\pi$ for
$2\pi$ halves the answer.

**How the checks here work, and why it matters.** `verify_surface` does not use
your formula, or any formula. It chops the curve into short segments, spins
each one into a frustum, and adds up their sides. There is no
$\mathrm{d}y/\mathrm{d}x$ anywhere in it — the check never differentiates
anything. So when it agrees with you, that is genuinely a second measurement
and not the same calculation run twice.
""")

md(r"""
## Task 8 🟡 — cone, sphere, and a slice of sphere

*Modelled on November 2022 Paper 3 Q2(a)(b)(d), 9 marks · calculator*

The surface formed by rotating $y=f(x)$, $x_1\le x\le x_2$, through $360°$
about the $x$-axis has area
$A=2\pi\displaystyle\int_{x_1}^{x_2}y\sqrt{1+\left(\frac{\mathrm{d}y}{\mathrm{d}x}\right)^2}\,\mathrm{d}x$.

**(a)** The line $y=3x$, $0\le x\le 2$, generates a cone. Find its curved
surface area, exactly.

**(b)** The semicircle $y=\sqrt{r^2-x^2}$, $-r\le x\le r$, generates a sphere.
Show by integration that its surface area is $4\pi r^2$.

**(c)** Now take $r=5$ and rotate only the arc from $x=1$ to $x=4$. Find the
area of the band of sphere this sweeps out.

Do (c) before you decide it needs the calculator. The answer to (b) makes the
integrand for (c) the simplest one in this notebook, and the result — that a
band of a sphere depends only on its **width**, not on where you cut it — is
Archimedes' theorem, and it is why a sphere and its circumscribed cylinder have
the same surface area.
""")

code(r"""
q16 = ...        # (a) exact
q17 = ...        # (b) in terms of r
q18 = ...        # (c) exact

verify_surface('8a', q16, 3*x, 0, 2)
verify_surface('8b', q17, sqrt(r**2 - x**2), -r, r, params={r: (2, 3, 5)})
verify_surface('8c', q18, sqrt(25 - x**2), 1, 4)
""")

md(r"""
## Theory 7. Displacement and distance are different questions

Given a velocity $v(t)$:

$$\text{displacement from }t_1\text{ to }t_2=\int_{t_1}^{t_2}v\,\mathrm{d}t,
\qquad
\text{distance travelled}=\int_{t_1}^{t_2}|v|\,\mathrm{d}t .$$

They agree only while $v$ keeps one sign. The moment the point turns round,
they part company — and the whole rung is that one distinction, asked twelve
times across the archive.

**A worked case.** $v=t-2$ on $0\le t\le 3$. The point moves backwards until
$t=2$ and forwards after. Displacement:

$$\int_0^3(t-2)\,\mathrm{d}t=\left[\frac{t^2}{2}-2t\right]_0^3=-\frac32 .$$

Distance: split at $t=2$, where $v=0$:

$$\int_0^2(2-t)\,\mathrm{d}t+\int_2^3(t-2)\,\mathrm{d}t=2+\frac12=\frac52 .$$

Ending up $1.5$ to the left of where it started, having travelled $2.5$.

**The routine for distance.**

1. Solve $v(t)=0$ inside the interval. **All** the roots — on Paper 2 a GDC
   graph is faster and safer than algebra.
2. Split at each root.
3. Add the absolute values. On a calculator paper, $\int|v|$ in one line does
   all three for you.

**Position, as opposed to displacement.** *Where is the point at $t=5$* needs
the starting position too: $s(5)=s(0)+\int_0^5 v$. The initial condition is
given precisely so that you use it, and forgetting it is a whole mark.

**How the checks here work.** `verify_travelled` never solves $v=0$. It walks
the interval in tiny steps, and at each step adds how far the point moved. That
is what distance *is* — the finding of the roots is your job, not the
measurement's. And because the check computes both numbers, it can tell you
when you have handed in the displacement instead.
""")

md(r"""
## Task 9 🟢 — one velocity, two answers

*Modelled on November 2021 Paper 1 Q10(a)(c), 12 marks · no calculator,
and May 2021 TZ1 Paper 2 Q4(b), 2 marks · calculator*

**(a)** A particle has velocity $v(t)=4+4t-3t^2$ m s⁻¹ and starts at the
origin. Find its displacement after 3 seconds.

**(b)** Find the total distance it has travelled in those 3 seconds.

**(c)** A second particle has $v(t)=t\sin t-3$ m s⁻¹. Find the total distance
it travels in the first 10 seconds, and its displacement over the same time.
Give both to three significant figures.

In (c) the velocity changes sign more than once. Graph it before you integrate
anything.
""")

code(r"""
q19 = ...        # (a)
q20 = ...        # (b)
q21 = ...        # (c) distance
q22 = ...        # (c) displacement

verify_position('9a', q19, 4 + 4*t - 3*t**2, 0, 3)
verify_travelled('9b', q20, 4 + 4*t - 3*t**2, 0, 3)
verify_travelled('9c', q21, t*sin(t) - 3, 0, 10)
verify_position('9d', q22, t*sin(t) - 3, 0, 10)
""")

md(r"""
## Task 10 🔴 — the same thing with letters in it

*May 2021 TZ2 Paper 1 Q11(b), 7 marks · no calculator*

A particle is launched at $t=0$ with velocity $v_0>0$ and decelerates
according to

$$v(t)=(1+v_0)\mathrm{e}^{-t}-1 .$$

It comes to rest at $t=T$, and at that moment its displacement from the start
is greatest.

Show that $\mathrm{e}^{T}=1+v_0$, and hence find the maximum displacement
$s_{\max}$ in terms of $v_0$.

The first half is an equation, not an integral. The second half is one integral
with a limit you just found — and the algebra at the end collapses further than
you expect, so keep going until nothing cancels any more.
""")

code(r"""
q23 = ...        # s_max, in terms of v0

verify_position('10', q23, (1 + v0)*exp(-t) - 1, 0, log(1 + v0),
                params={v0: (1, 3, 7)})
""")

# ================================================================= Part IV
md(r"""
---
# Part IV — accumulation

## Theory 8. Rate in, amount out

If something arrives at a rate $R'(t)$, the amount that has arrived between
$t=a$ and $t=b$ is $\int_a^b R'(t)\,\mathrm{d}t$, and the amount *present* is
that plus whatever was there at the start:

$$R(b)=R(a)+\int_a^b R'(t)\,\mathrm{d}t .$$

This is the same integral as displacement, wearing different words. All twenty
marks of this rung are Paper 2, and all of them are stories.

**A worked case.** A tank holds 10 litres and water runs in at $3+t$ litres per
minute. After 4 minutes it holds

$$10+\int_0^4(3+t)\,\mathrm{d}t=10+\left[3t+\frac{t^2}{2}\right]_0^4=10+20=30
\text{ litres.}$$

The 10 is not decoration. Dropping it is the single commonest error on this
rung, and it is exactly the "$+c$" of E5 in a new costume: the initial
condition is given so that the constant can be found.

**Three habits that pay here.**

**Read the window.** *During any 60-second period* means $\int_0^{60}$, not
$\int_0^{\text{end of the storm}}$.

**Compare amounts, never rates.** *Does it overflow* is a question about two
volumes. Produce both numbers and put them side by side; an argument about
which rate is bigger scores nothing.

**A periodic rate often integrates to nothing.** $\int_0^{60}\cos\frac{2\pi
t}{5}\,\mathrm{d}t=0$ because 60 seconds is exactly twelve periods. When the
numbers are chosen that neatly, that is a hint, not a coincidence.
""")

md(r"""
## Task 11 🟡 — a gutter, and whether it copes

*Modelled on May 2023 TZ1 Paper 2 Q10(b)(c), 12 marks · calculator*

A trough 40 cm long has a parabolic cross-section: the region between
$y=x^2$ and $y=4$, with $x$ and $y$ in centimetres.

**(a)** Find the area of the cross-section.

**(b)** Find the volume the trough can hold.

During a shower, rain enters the trough at a rate of
$8+4\cos\dfrac{\pi t}{4}$ cm³ per second, where $t$ is in seconds.

**(c)** Find the volume of rain that enters during a 60-second shower.

**(d)** By how much does the trough overflow? Give the amount, in cm³.

Part (d) wants a number, not a yes or a no — that is what "justify your answer"
means when the mark scheme says it.
""")

code(r"""
q28 = ...        # (a) cross-section, cm^2
q29 = ...        # (b) capacity, cm^3
q30 = ...        # (c) rain in 60 s, cm^3
q31 = ...        # (d) the excess, cm^3

verify_region('11a', q28, 4, x**2, -2, 2)
# a trough is a prism: its volume is the cross-section accumulated along 40 cm,
# so (b) is checked against your own (a) -- the "hence" in the question
verify_amount('11b', q29, ... if blank(q28) else q28, 0, 40, var=w)
verify_amount('11c', q30, 8 + 4*cos(pi*t/4), 0, 60)
# and (d) against your own (b): excess + capacity must be the rain that fell
verify_amount('11d', ... if blank(q31, q29) else q31 + q29,
              8 + 4*cos(pi*t/4), 0, 60)
""")

md(r"""
## Task 12 🔴 — a plane and a car on the same runway

*November 2025 TZ1 Paper 2 Q10(c)(e), 10 marks · calculator*

An aeroplane lands on a runway 100 m in front of a stationary car. At the
instant it lands the car starts moving in the same direction. For $t\ge 0$
their velocities in m s⁻¹ are

$$v_{\text{air}}=60\mathrm{e}^{-0.1t},\qquad v_{\text{car}}=5t .$$

Let $d(t)$ be the distance between the car and the back of the aeroplane.

**(a)** Given $d(0)=100$, find $d(t)$.

**(b)** Find how long it takes the car to reach the back of the aeroplane.
Give your answer to three significant figures.

**(c)** Find the distance the car has travelled by then, to three significant
figures.

In (a) the plane is pulling away and the car is closing in, so the gap changes
at $v_{\text{air}}-v_{\text{car}}$ — get that sign right and the rest is one
integral. Check your $d$ by putting $t=0$ into it before you go on.
""")

code(r"""
q25 = ...        # (a) d(t)
q26 = ...        # (b) the time, 3 s.f.
q27 = ...        # (c) the distance, 3 s.f.

# (a) is checked at four moments at once: a wrong d cannot match at all of them
verify_amount('12a', q25, 60*exp(-t/10) - 5*t, 0, 20, start=100)
check_num('12b', q26, 3, '8dccabdc7331')
check_num('12c', q27, 3, '97a6d21df7c5')
""")

md(r"""
## Task 13 🟡 — the measurement read backwards

*Modelled on May 2021 TZ2 Paper 2 Q11(b), 2 marks, and
May 2022 TZ2 Paper 2 Q6, 5 marks · calculator*

**(a)** The region under $y=\sqrt x$ from $x=0$ to $x=k$ is rotated through
$2\pi$ about the $x$-axis. The solid has volume $8\pi$. Find $k$.

**(b)** The area under $y=\dfrac1x$ from $x=1$ to $x=c$ is $\ln 5$. Find $c$.

Both are one line of setting up and one line of solving. They are here because
half of rung 5's marks look like this, and because it is worth seeing that
nothing about the measurement changes when the unknown moves to the limit.
""")

code(r"""
q32 = ...        # (a) k
q33 = ...        # (b) c

# your answer goes in as the upper limit, and the known measurement is checked
verify_solid('13a', 8*pi, sqrt(x), 0, q32)
verify_region('13b', log(5), 1/x, 0, 1, q33)
""")

# ============================================================== the trainer
md(r"""
---
## Trainer — which measurement is it?

Twelve questions in words only. For each, name the rung you would use. No
integration: the skill being drilled is reading the picture out of the sentence,
which is where the marks in this topic actually are.

| code | rung |
| --- | --- |
| `under` | area under one curve |
| `between` | area between two graphs |
| `volx` | volume about the $x$-axis |
| `voly` | volume about the $y$-axis |
| `ring` | washer, or volume given and a parameter wanted |
| `skin` | surface of revolution |
| `motion` | displacement or distance from a velocity |
| `accum` | accumulated amount from a rate |

1. *The curve $y=4\ln(x-2)$ for $0\le y\le 4$ is rotated $360°$ about the
   $y$-axis. Find the volume.*
2. *Find the total distance travelled by $P$ between $t=0$ and $t=5$.*
3. *Find the total area enclosed by the graph of $f$, the $x$-axis and the line
   $x=2$.*
4. *Using $A=2\pi\int y\sqrt{1+(\mathrm{d}y/\mathrm{d}x)^2}\,\mathrm{d}x$, show
   that $A=\pi rl$.*
5. *Find the area of the region enclosed by the graphs of $f$ and $g$ between
   $x=a$ and $x=b$.*
6. *A bowl is formed by rotating the given arc about the $y$-axis. Find the
   height $h$ at which it holds 285 cm³.*
7. *Water is added at a constant rate of 0.4 m³ s⁻¹. Find the time to fill the
   container.*
8. *The region enclosed by $y=f(x)$, the $x$-axis and the $y$-axis is rotated
   through $2\pi$ about the $x$-axis. Find the volume.*
9. *Find the displacement of the particle relative to $O$ when $t=10$.*
10. *Find the shaded area bounded by the curve, the normal $L$ and the
    $y$-axis.*
11. *Find the volume of the solid formed when the curve is rotated $360°$ about
    the $y$-axis between $y=y_A$ and $y=y_B$.*
12. *Find how far Lucy is from the finishing line when Fiona completes 200 m.*
""")

code(r"""
answers = {
    1: '',   2: '',   3: '',   4: '',
    5: '',   6: '',   7: '',   8: '',
    9: '',  10: '',  11: '',  12: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## On the timer — 6 minutes

*Paper 2 pace: a 6-mark question of this kind should take six minutes,
including reading it.*

The region enclosed by $y=\sqrt x$ and $y=\dfrac x3$ is rotated through $2\pi$
about the $x$-axis. Find the volume of the solid formed, exactly.

Two curves, so a washer; and no limits, so they come first.
""")

code(r"""
qt = ...         # the volume, exact

verify_solid('timer', qt, sqrt(x), 0, 9, inner=x/3)
""")

md(r"""
---
## What to take away

**Eight rungs, one question: what is one slice?** Every formula in this topic
is a slice summed up, and every formula is recoverable from the picture in
about ten seconds. That is worth more than remembering four of them.

**The two words that carry the most marks in the topic are *total* and
*displacement*.** *Total area* means add the absolute values; *total distance*
means $\int|v|$; *displacement* means do not. Twelve of the 46 blocks turn on
this alone, and no algebra is involved in any of them.

**Turning about the $y$-axis is an algebra question wearing a calculus hat.**
Express $x$ through $y$, get the $y$-limits, and only then write $\pi\int x^2$.
Thirty marks live there, 24 of them on Paper 2.

**When the volume is given, nothing changes but the last line.** Write the same
integral, set it equal, solve. It is the same rung, read backwards.

**Where the archive actually puts the marks.** 197 marks over 46 blocks:
53 for flat regions, 75 for solids, 13 for a surface, 61 for motion and
accumulation. 119 marks carry a calculator, and Paper 2 alone holds 106 — the
mirror image of E5, where 86 of 157 marks were Paper 1. The reason is the same
in both directions: a GDC will not find you an antiderivative, and it will
always find you a number.

**And the habit from E5 still applies, in reverse.** There you could check
every answer by differentiating it. Here you can check every answer by asking
whether it is the right *size*: a volume that comes out smaller than the
cylinder around it, a distance shorter than the displacement, an area that
comes out negative — all of these are wrong on sight, before any arithmetic.
Sanity is a cheaper check than accuracy, and in this topic it catches more.
""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

with open(NOTEBOOK, 'w') as fh:
    json.dump(notebook, fh, ensure_ascii=False, indent=1)
    fh.write('\n')

slots = sum(src.count(' = ...') + src.count(': ...,')
            for cell in cells if cell['cell_type'] == 'code'
            for src in [''.join(cell['source'])])
checks = sum(''.join(cell['source']).count('verify_')
             + ''.join(cell['source']).count('check_num(')
             + ''.join(cell['source']).count('trigger_check(')
             for cell in cells if cell['cell_type'] == 'code')
print(f'{NOTEBOOK}: {len(cells)} ячеек, '
      f'{sum(1 for c in cells if c["cell_type"] == "code")} кодовых, '
      f'{slots} мест под ответ, {checks} проверок')
print(f'ANSWERS: {len(ANSWERS)} ключей')
