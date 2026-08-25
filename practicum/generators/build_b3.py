"""Собирает практикум B3 (преобразования графиков) в формате .ipynb.

Второй практикум серии на английском: ноутбук целиком английский, kit
переключается вызовом language('en') в установочной ячейке. Документация
репозитория (карта, PRACTICUM.md, этот заголовок) остаётся русской.

Тема живёт на картинках, а картинку проверить нельзя. Поэтому здесь два
новых вида проверки: verify_transform выполняет описанную последовательность
преобразований и смотрит, получился ли целевой график, а verify_sketch
сверяет список особенностей эскиза с тем, что у функции есть на самом деле.
Всё, чего они не видят — форма кривой между особенностями, — печатается
рядом настоящим графиком: ноутбук рисует то, что вы должны были нарисовать.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
import kit
from kit import digest, sig

sq = sp.sqrt
R = sp.Rational
x, y, t, n = sp.symbols('x y t n')
k_, r_, q_, m_ = sp.symbols('k r q m', positive=True)


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dser(expr, var=x, sf=6):
    return digest(kit._series_canon(expr, var, sf))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


def ddom(region, var=x):
    return digest(sp.srepr(kit._as_set(region, var)))


def dorder(items):
    return digest('|'.join(str(i).strip().lower() for i in items))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_b3.py ---
D_1A = dn(6)                                     # f(2) с графика
D_1B = dn(-2)                                    # (f∘f)(2) = f(6)
D_1C = dn(-0.375)                                # наклон прямой через B и C
D_1D = dn(0)                                     # ордината B у общей кривой
D_3B = dset([r_ / k_, -r_ / k_])                 # x-пересечения полуэллипса
D_7A = dn(R(1, 2))                               # горизонтальное растяжение k
D_7B = dn(-3)                                    # вертикальный сдвиг c
D_8A = dn(2)                                     # A
D_8B = dn(6)                                     # B
D_10A = dn(-0.743, 3)                            # первая точка после отражения
D_10B = dn(0.331, 3)
D_10C = dn(-0.538, 3)                            # вторая точка после отражения
D_10D = dn(1.84, 3)
D_12B = ddom(sp.Union(sp.FiniteSet(0), sp.Interval.Ropen(4, 9)))
D_17A = de(sp.pi / (2 * q_))                     # m через q
D_18A = dser(2 * sp.tan(x) - sp.tan(x)**3)       # (f∘g)(x)
D_19B = ddom(sp.Union(sp.Interval.open(-sp.oo, 4), sp.Interval.open(4, sp.oo)))
D_19C = dn(R(-25, 4))                            # ордината вершины g
D_20A = dset([-1, 1])                            # x-пересечения гиперболы
D_20B = dset([x, -x])                            # уравнения асимптот
D_21B = dorder([1, 2, 0])                        # p, q, r
D_21C = dn(2)                                    # число решений при m > 0
D_22B = dorder([1, 0, 2, 1, 2, 0])               # таблица для нечётных и чётных n

TRIGGER = {1: 'name', 2: 'fold', 3: 'sketch', 4: 'read', 5: 'family',
           6: 'match', 7: 'sym', 8: 'asym', 9: 'apply', 10: 'fold',
           11: 'name', 12: 'sketch', 13: 'sym', 14: 'family', 15: 'asym'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

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
# Practicum B3: transformations of graphs

**107 marks, 37 blocks, nine techniques.** A graph is the one answer in
the syllabus you cannot write down as a number — and the exam has
exactly two ways of asking for it.

**Material.** The whole of `functions.graphing` from the AA HL archive,
sessions May 2021 — November 2025. Two of those marks are one question
counted twice: the November 2023 session sits in the corpus as two
zones, and the papers are the same paper. Every task below is a real
past-paper question, with the source given.

**This practicum is in English,** like B2. The checks speak whichever
language the notebook asks them to, and this one asks for English in the
setup cell.

**The main idea.** The exam asks you to **name** what moves the graph —
"describe a sequence of transformations that maps $y=\sin\theta$ onto
$\dots$" — and then your answer is a *recipe*, and the marks are for
the recipe running correctly. Or it asks you to **draw**, and then your
answer is a *list of features*.

No sketch is ever marked on its beauty. Read the instructions in the
archive and they are always the same phrases:

> *"stating the values of any axes intercepts"* · *"clearly indicating
> any asymptotes"* · *"showing the coordinates of any points where
> $f'(x)=0$"* · *"with their equations"*

Those phrases **are** the markscheme. The curve drawn between them is
one A1 for shape.

**How the checks work here.** Two of them are new.

* `verify_transform` takes your sequence of transformations, applies it
  to the source function and looks at what comes out. Nothing is
  compared with a stored description, so **any order that works is
  accepted and any order that does not is rejected** — which is the
  point: the markscheme awards A1**A0** for the right pair of horizontal
  transformations given in the wrong order.
* `verify_sketch` takes the list of features your sketch claims and
  computes each of them from the function itself. Missing and extra are
  different messages, because in the markscheme they are different
  marks.

Neither one can see the shape of the curve between the features. So
every sketch task prints the true curve next to your answer: look at it
after you have drawn yours, not before.

**How to work**

1. Read the map of techniques first. It is arranged by **what you are
   given**, and that turns out to be the whole structure of the topic.
2. Work **on paper**, with a pencil and the axes drawn. Then enter the
   features.
3. Exact answers: `pi/6`, `sqrt(6)/2`, `Rational(15, 2)`. Round only
   where the question says "3 s.f." — and coordinates read off a
   calculator are compared at exactly that precision.
4. A sketch is entered as a dictionary. Only the keys you fill in are
   checked, and the task says which ones the markscheme pays for.
5. The last two blocks are a recognition trainer and one question on
   a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Piecewise, solveset, lambdify

import matplotlib.pyplot as plt
import numpy as np

language('en')                 # this notebook is in English, and so are the checks

a, b, c, m, p, q = symbols('a b c m p q')
r, s, w = symbols('r s w')
theta = Symbol('theta')


# Draw the true curve so you can compare your sketch with it. Pass
# expressions, or (expression, label) pairs; `marks` takes points (x, y)
# to dot on the picture — the features you were asked for.
def show(*curves, span=(-6, 6), ylim=None, size=(7, 4), marks=()):
    grid = np.linspace(float(span[0]), float(span[1]), 1500)
    fig, ax = plt.subplots(figsize=size)
    for item in curves:
        expr, name = item if isinstance(item, tuple) else (item, None)
        g = lambdify(x, expr, 'math')
        vals = []
        for u in grid:
            try:
                v = float(g(float(u)))
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                v = float('nan')
            vals.append(v if abs(v) < 1e6 else float('nan'))
        ax.plot(grid, vals, lw=1.7, label=name or f'y = {expr}')
    for point in marks:
        ax.plot(float(point[0]), float(point[1]), 'o', ms=5, color='0.2')
    ax.axhline(0, color='0.6', lw=.8)
    ax.axvline(0, color='0.6', lw=.8)
    ax.grid(alpha=.3)
    if ylim:
        ax.set_ylim(float(ylim[0]), float(ylim[1]))
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


print('ready; sympy', sp.__version__)
print('a transformation step: ', ('stretch_x', Rational(1, 2)))
print('a sketch as features:  ', {'x_intercepts': [1], 'maxima': [(0, 3)]})
print('a domain as a set:     ', Interval.Ropen(-pi/2, pi/2))
print('a graph as a formula:  ', Piecewise((4, x <= 0), (6 - (x - 2)**2/2, True)))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Read a value off a graph | a printed curve, «write down the value of $f(2)$» | go up to the curve, then across |
| 2 | Apply a translation or a stretch | «let $g(x)=\tfrac12 f(x)+1$; sketch $g$» | move the labelled points, one at a time |
| 3 | Name the sequence | «describe a sequence of transformations that maps … onto …» | write the target so the source is visible inside it |
| 4 | Find the parameters | «$g$ is obtained by a stretch factor $k$ then a translation of $c$; find $k$ and $c$» | apply the named steps with their letters, then compare |
| 5 | Use the symmetry | «show that $f$ is odd», «using the line of symmetry $y=x$» | write $f(-x)$ out in full; or swap the coordinates |
| 6 | Fold the graph | «sketch $y=\lvert f(x)\rvert$», «$y=f(\lvert x\rvert)$», «$y=\tfrac{15}{f(x)}$» | find the zeros of $f$ — every corner sits at one |
| 7 | Sketch a curve you know | «sketch $y=\arccos x$, indicating the end points» | name the shape, then the intercepts and turning points |
| 8 | Sketch with asymptotes | «label any asymptotes with their equations» | denominator zero first, then the limit at infinity |
| 9 | Explore a family | «use your GDC to explore $y=f_n(x)$ for $n=3$ and $n=5$» | plot two or three members, not one |

**The ladder goes by what you are given, and that is the whole topic.**

**Rungs 1–4 — a graph is given, and something moves it.** Read it, apply
a stretch to it, name the sequence that produced it, find the numbers in
that sequence. These are the *rigid* transformations: they move points
without bending anything, and the only difficulty is bookkeeping —
direction, factor, order.

**Rungs 5–6 — a graph is given, and something folds it.** Symmetry
first, then the two transformations that act on the *value* rather than
the position: $\lvert f(x)\rvert$, $f(\lvert x\rvert)$ and
$\tfrac1{f(x)}$. These bend. They create corners where there were none,
and **every one of those corners sits at a zero of $f$.**

**Rungs 7–9 — no graph is given, and you draw it.** From a formula whose
shape you know; from a formula with asymptotes, where the asymptotes
come first and the curve follows; and across a whole family, where the
calculator draws and your job is to see what stays the same.

Seen from far enough away it is one idea three times: **a graph is its
list of features.** Rungs 1–4 move the list, rungs 5–6 rewrite it,
rungs 7–9 compute it from nothing.

**What saves the most time.** Before drawing anything, write down what
the question told you to label. That list is the answer; the curve is
the packaging.
""")

md(r"""
---
# Part I — a graph is given, and something moves it

---
## Theory 1. The four rigid transformations, and the two that get inverted

Start from $y=f(x)$.

| Written | What happens | Careful |
| --- | --- | --- |
| $f(x)+k$ | translation $k$ **up** | the obvious one |
| $f(x-h)$ | translation $h$ **right** | the sign reads backwards |
| $a\,f(x)$ | vertical stretch, factor $a$ | the obvious one |
| $f\!\left(\frac{x}{s}\right)$ | horizontal stretch, factor $s$ | so $f(kx)$ is a stretch by $\tfrac1k$ |
| $-f(x)$ | reflection in the $x$-axis | |
| $f(-x)$ | reflection in the $y$-axis | |

**Everything that touches $x$ behaves backwards,** and that is not a
coincidence: to find the new $y$ at a point you have to ask where that
point *came from*, which is the inverse of the motion. Two lost marks
live here and they are the two most reliable in the topic:
$f(2x)$ called "a stretch by 2", and $f(x-3)$ called "3 to the left".

**Order matters, and here is the smallest example.** Take $f(x)=x^2$.

* Stretch horizontally by $\tfrac12$, then translate $1$ right:
  $x^2 \to (2x)^2 \to (2(x-1))^2 = (2x-2)^2$.
* Translate $1$ right, then stretch horizontally by $\tfrac12$:
  $x^2 \to (x-1)^2 \to (2x-1)^2$.

Different curves. The markscheme for November 2025 TZ1 says so in as
many words: *"Award A1A0 for correct horizontal transformations
specified in the wrong order."*

**How to check yourself in the exam.** Apply your own description, in
your own order, to the source function on the page. If it does not
produce the printed target, the description is wrong — and that is
exactly what `verify_transform` does below.
""")

md(r"""
## Task 1 🟢 — reading things off a graph

The graph of $y=f(x)$ for $-4\le x\le 6$ consists of a horizontal
segment at $y=4$ for $-4\le x\le 0$, and a parabola with vertex $(2,6)$
for $0\le x\le 6$. That is the formula in the cell below; in the paper
it is a picture.

**(a)** Write down the value of $f(2)$.

**(b)** Write down the value of $(f\circ f)(2)$.

Now a different question. The curve $y=x^4-3x^3+3x$ has points of
inflexion at $\mathrm{B}$ and $\mathrm{C}$, where $\mathrm{B}=(0,0)$ and
$\mathrm{C}=(1.5,\,-0.5625)$.

**(c)** Show that the line through $\mathrm{B}$ and $\mathrm{C}$ is
$y=-0.375x$. Enter its gradient.

**(d)** The general curve of the investigation is $y=x^4-mx^3+nx$, and
its points of inflexion are at $x=0$ and $x=\tfrac{m}{2}$. Write down
the $y$-coordinate of $\mathrm{B}$.

*Sources: May 2021 TZ1, Paper 1, Q1(a) (2 marks, no calculator);
May 2024 TZ1, Paper 3, Q2(c) and Q2(f)(i) (2 + 1 marks).*
""")

code(r"""
f1 = Piecewise((4, x <= 0), (6 - (x - 2)**2/2, True))    # the printed graph
show((f1, 'y = f(x)'), span=(-4, 6), marks=[(2, 6), (6, -2)])

my1a = ...               # f(2)
my1b = ...               # (f ∘ f)(2)
my1c = ...               # the gradient of BC
my1d = ...               # the y-coordinate of B

check_num('Task 1(a)', my1a, 6, '""" + D_1A + r"""')
check_num('Task 1(b)', my1b, 6, '""" + D_1B + r"""')
check_num('Task 1(c)', my1c, 6, '""" + D_1C + r"""')
check_num('Task 1(d)', my1d, 6, '""" + D_1D + r"""')
""")

md(r"""
## Task 2 🟢 — apply a stretch and a translation

Same $f$ as in task 1. Let

$$g(x) = \tfrac12 f(x) + 1, \qquad -4 \le x \le 6 .$$

Sketch $g$ **on paper**, then enter its features: the coordinates of its
local maximum, the coordinates of both endpoints of the domain, and any
$x$-intercepts.

*Source: May 2021 TZ1, Paper 1, Q1(b) (3 marks, no calculator).*
""")

code(r"""
g2 = f1/2 + 1

my2 = {
    'maxima':       [...],          # [(x, y)]
    'endpoints':    [...],          # [(x, y), (x, y)]
    'x_intercepts': [...],          # [x, ...]
}

verify_sketch('Task 2', my2, g2, domain=Interval(-4, 6))
show((f1, 'y = f(x)'), (g2, 'y = g(x)'), span=(-4, 6))
""")

md(r"""
---
## Theory 2. Describing a sequence, and why the order is a mark

The question prints two formulas and wants the words between them.
There is a mechanical way to produce those words, and it never fails.

**Write the target so that the source is visible inside it.** For
$y=\arctan(2x+1)+\tfrac{\pi}{4}$ the source is $\arctan x$, so factor
the inside:

$$\arctan\bigl(2(x+\tfrac12)\bigr)+\tfrac{\pi}{4}.$$

Now peel from the inside out: $x \to 2x$ is a horizontal stretch by
$\tfrac12$; then $x \to x+\tfrac12$ is a translation $\tfrac12$ **left**;
then $+\tfrac{\pi}{4}$ is a translation up.

**Or peel in the other order** — $\arctan(2x+1)$ is also
$\arctan x$ with $x\to x+1$ first and then $x\to 2x$. Both descriptions
are correct, and the markscheme takes either. What it will not take is
the stretch by $\tfrac12$ followed by a translation of $\tfrac12$ left:
that gives $\arctan(2x+\tfrac12)$.

**The vocabulary is marked too.** November 2025 TZ3 says it outright:
*"the transformations may be described using terms such as translate or
shift, and dilate or stretch. Do not accept 'move'."* And a
transformation is described by **direction and amount**, or by **factor**
— "a translation" alone earns nothing.

**In this notebook** you write the sequence as a list, and the check
runs it:

```python
[('stretch_x', Rational(1, 2)), ('shift_x', -Rational(1, 2)), ('shift_y', pi/4)]
```

* `('shift_x', h)` — $h$ to the right ($h<0$ means left)
* `('shift_y', k)` — $k$ up
* `('stretch_x', s)` — horizontal stretch, factor $s$
* `('stretch_y', s)` — vertical stretch, factor $s$
* `'reflect_in_x_axis'`, `'reflect_in_y_axis'`
""")

md(r"""
## Task 3 🟢 — the stretch that inverts

Let $f(x)=\sqrt{r^2-x^2}$ for $-r\le x\le r$ — the upper half of a
circle of radius $r$. The graph of $y=f(x)$ is transformed into the
graph of $y=f(kx)$, where $k>0$. This forms a semi-ellipse.

**(a)** Describe this geometric transformation.

**(b)** Write down the $x$-intercepts of $y=f(kx)$ in terms of $r$ and
$k$.

Enter the transformation as a one-element list. Both letters are already
defined as positive symbols.

*Source: November 2022, Paper 3, Q2(e)(i) and (ii) (2 + 1 marks).*
""")

code(r"""
r, k = symbols('r k', positive=True)     # both are positive in the question
semi = sqrt(r**2 - x**2)

my3a = [...]             # the sequence of transformations
my3b = [...]             # the x-intercepts

verify_transform('Task 3(a)', my3a, semi, sqrt(r**2 - k**2*x**2))
check_set('Task 3(b)', my3b, '""" + D_3B + r"""')
show((semi.subs(r, 2), 'r = 2, k = 1'), (sqrt(4 - 4*x**2), 'r = 2, k = 2'),
     span=(-2.2, 2.2), size=(6, 3))
""")

md(r"""
## Task 4 🟢 — two transformations of a sine

Consider $f(x)=4\sin x + 2.5$ and

$$g(x) = 4\sin\!\left(x - \tfrac{3\pi}{2}\right) + 2.5 + q,$$

where $x\in\mathbb{R}$ and $q>0$. The graph of $g$ is obtained by two
transformations of the graph of $f$. Describe these two transformations.

Keep the letter $q$ in your answer — it is already defined.

*Source: May 2022 TZ1, Paper 1, Q5(a) (2 marks, no calculator).*
""")

code(r"""
q = Symbol('q', positive=True)
f4 = 4*sin(x) + Rational(5, 2)
g4 = 4*sin(x - 3*pi/2) + Rational(5, 2) + q

my4 = [...]              # the two transformations, in order

verify_transform('Task 4', my4, f4, g4)
""")

md(r"""
## Task 5 🟡 — a sequence of three

The following diagram shows the graph of
$y=\arctan(2x+1)+\tfrac{\pi}{4}$ for $x\in\mathbb{R}$, with asymptotes
at $y=-\tfrac{\pi}{4}$ and $y=\tfrac{3\pi}{4}$.

Describe a sequence of transformations that transforms the graph of
$y=\arctan x$ to this graph.

*Source: May 2021 TZ2, Paper 1, Q12(a) (3 marks, no calculator).*
""")

code(r"""
my5 = [...]              # the sequence, in the order you would write it

verify_transform('Task 5', my5, atan(x), atan(2*x + 1) + pi/4)
show((atan(x), 'y = arctan x'), (atan(2*x + 1) + pi/4, 'the target'),
     span=(-6, 6), size=(6, 3))
""")

md(r"""
---
## Theory 3. When the sequence is named and the numbers are not

The other half of this rung is the question the other way round: the
examiner tells you *which* transformations were used and asks for their
values. The method is the same move, run backwards.

$$f(x)=e^{x}-3x-4, \qquad g(x)=e^{2x}-6x-7 .$$

*"The graph of $g$ is obtained from the graph of $f$ by a horizontal
stretch with scale factor $k$, followed by a vertical translation of $c$
units. Find $k$ and $c$."*

Apply the named steps with their letters still in place:

$$f\!\left(\tfrac{x}{k}\right)+c
= e^{x/k}-\tfrac{3x}{k}-4+c .$$

Now compare with $g$. The exponent gives $\tfrac{x}{k}=2x$, so
$k=\tfrac12$; then $-\tfrac{3x}{1/2}=-6x$ agrees, and $-4+c=-7$ gives
$c=-3$. **Match the exponent first and the constant last** — the usual
lost mark is finding $k$ from the exponential and forgetting that the
linear term has to agree too.

**Rational targets need one extra move first.** A function like
$\dfrac{2x+6}{x-4}$ shows nothing until you divide out:

$$\frac{2x+6}{x-4} = \frac{2(x-4)+14}{x-4} = 2 + \frac{14}{x-4}.$$

Now every transformation from $y=\tfrac1x$ is visible at once —
translate $4$ right, stretch vertically by $14$, translate $2$ up — and
the two constants are the two asymptotes, $x=4$ and $y=2$. **The
asymptotes and the translations are the same two numbers**, which is why
the markscheme gives a mark for either.
""")

md(r"""
## Task 6 🔴 — an identity first, then the sequence

**(a)** Show that $\sin 3\theta \equiv 3\sin\theta - 4\sin^{3}\theta$.

Enter the line you get from the angle-sum formula, before the double
angle identities are used — that is, $\sin(2\theta+\theta)$ expanded
once. The check confirms your line really is $\sin 3\theta$.

**(b)** Hence describe a sequence of transformations that maps the graph
of $y=\sin\theta$ onto the graph of

$$y = 6\sin\!\left(\theta+\tfrac{\pi}{6}\right)
- 8\sin^{3}\!\left(\theta+\tfrac{\pi}{6}\right).$$

Write your steps in `x`, not `theta`.

*Source: November 2025 TZ1, Paper 1, Q8 (4 + 4 marks, no calculator).
The corpus records the target of (b) as a fraction that does not appear
in the paper; the solution says what happened.*
""")

code(r"""
target6 = 6*sin(x + pi/6) - 8*sin(x + pi/6)**3

my6a = ...               # sin(2x + x) expanded by the angle-sum formula
my6b = [...]             # the sequence of transformations

verify_identity('Task 6(a)', my6a, sin(3*x))
verify_transform('Task 6(b)', my6b, sin(x), target6)
show((sin(x), 'y = sin x'), (target6, 'the target'), span=(-pi, pi), size=(6, 3))
""")

md(r"""
## Task 7 🟡 — find the stretch and the translation

Consider the function $f(x)=e^{x}-3x-4$. The function $g$ is defined by
$g(x)=e^{2x}-6x-7$.

The graph of $g$ is obtained from the graph of $f$ by a horizontal
stretch with scale factor $k$, followed by a vertical translation of $c$
units. Find the value of $k$ and the value of $c$.

*Source: November 2023 TZ1, Paper 2, Q2(b) (2 marks). The same question
is in the corpus a second time as November 2023 TZ2 — the two zones of
that session are one paper.*
""")

code(r"""
my7a = ...               # k
my7b = ...               # c

check_num('Task 7, k', my7a, 6, '""" + D_7A + r"""')
check_num('Task 7, c', my7b, 6, '""" + D_7B + r"""')
""")

md(r"""
## Task 8 🔴 — from the hyperbola $y=\frac1x$

The following diagram shows the graph of $y=\dfrac{Ax+B}{x-4}$, where
$x\in\mathbb{R}$, $x\ne 4$ and $A,B\in\mathbb{Z}$. The graph passes
through the points $\mathrm{P}(-10,\,1)$ and $\mathrm{Q}(3,\,-12)$.

**(a)** Determine the value of $A$ and the value of $B$.

**(b)** Describe a sequence of transformations that would map the graph
of $y=\dfrac1x$ onto this graph.

*Source: November 2025 TZ3, Paper 1, Q3 (3 + 5 marks, no calculator).*
""")

code(r"""
my8a = ...               # A
my8b = ...               # B
my8c = [...]             # the sequence from y = 1/x

check_num('Task 8, A', my8a, 6, '""" + D_8A + r"""')
check_num('Task 8, B', my8b, 6, '""" + D_8B + r"""')
verify_transform('Task 8(b)', my8c, 1/x, (2*x + 6)/(x - 4))
show((1/x, 'y = 1/x'), ((2*x + 6)/(x - 4), 'the target'),
     span=(-12, 16), ylim=(-14, 18), size=(6, 3.5))
""")

md(r"""
---
# Part II — a graph is given, and something folds it

---
## Theory 4. Symmetry, and the mark that is a sentence

$$f \text{ is even} \iff f(-x)=f(x) \iff \text{mirror in the } y\text{-axis},$$
$$f \text{ is odd} \iff f(-x)=-f(x) \iff \text{half-turn about the origin}.$$

**"Show that $f$ is odd" is worth two marks and one of them is the last
line.** The algebra is one substitution:

$$f(x)=\frac{1}{2^{x}}-2^{x}
\ \Longrightarrow\ f(-x)=2^{x}-2^{-x}=-\left(2^{-x}-2^{x}\right)=-f(x),$$

and the mark that gets lost is the sentence **"therefore $f$ is odd"**.
Write $f(-x)$ out in full before simplifying anything — most of the lost
M1s are people who simplified in their head and produced a line that
does not obviously come from $f(-x)$.

**On a graph the same fact is a drawing instruction.** If you are given
$y=f(\lvert x\rvert)$ and told $f$ is odd, then the right-hand side of
the picture *is* $f$, and the left-hand side is that half turned through
$180°$ about the origin. Not reflected in the $y$-axis — that is what
even does, and the two are easy to swap under time pressure.

**A third symmetry appears in implicit curves: $y=x$.** If a curve is
symmetric in $y=x$, then reflecting any point swaps its coordinates, and
that turns horizontal tangents into vertical ones. A one-mark question
that needs no calculation at all — provided you notice that *both*
coordinates swap.
""")

md(r"""
## Task 9 🟢 — two "show that"s

**(a)** Consider $f(x)=\dfrac{1}{2^{x}}-2^{x}$, $x\in\mathbb{R}$. Show
that $f$ is an odd function.

**(b)** A function $f$ is defined by $f(x)=x\sqrt{1-x^{2}}$ where
$-1\le x\le 1$. Show that $f$ is an odd function.

For each one, enter $f(-x)$ — written out, then simplified as far as you
like. The check confirms it equals $-f(x)$.

*Sources: May 2022 TZ1, Paper 2, Q6(a) (2 marks); May 2022 TZ2, Paper 1,
Q6(a) (2 marks).*
""")

code(r"""
f9a = 1/2**x - 2**x
f9b = x*sqrt(1 - x**2)

my9a = ...               # f(−x) for the first function
my9b = ...               # f(−x) for the second

verify_identity('Task 9(a)', my9a, -f9a)
verify_identity('Task 9(b)', my9b, -f9b)
show((f9b, 'y = x sqrt(1 - x^2)'), span=(-1, 1), size=(5.5, 3))
""")

md(r"""
## Task 10 🟢 — the line of symmetry $y=x$

Consider the curve $C$ defined by $e^{x+y}=x^{2}+y^{2}$. The curve has a
line of symmetry $y=x$. There are two points on $C$ where the tangent is
horizontal; they are $\mathrm{P}(0.331,\,-0.743)$ and
$\mathrm{Q}(1.84,\,-0.538)$.

Using the line of symmetry, write down the coordinates of the points on
$C$ where the tangent is **vertical**. Give each coordinate to 3 s.f.

*Source: May 2024 TZ1, Paper 2, Q11(c) (1 mark).*
""")

code(r"""
my10a = ...              # x of the first vertical-tangent point
my10b = ...              # y of the first
my10c = ...              # x of the second
my10d = ...              # y of the second

check_num('Task 10, first x',  my10a, 3, '""" + D_10A + r"""')
check_num('Task 10, first y',  my10b, 3, '""" + D_10B + r"""')
check_num('Task 10, second x', my10c, 3, '""" + D_10C + r"""')
check_num('Task 10, second y', my10d, 3, '""" + D_10D + r"""')
""")

md(r"""
---
## Theory 5. The three folds, and where the corners come from

These three do not move points; they act on the **value**. Each one has
a rule and a corner.

**$y=\lvert f(x)\rvert$** — everything below the axis is reflected up,
everything above is untouched. So the graph never goes below the axis,
and at **every zero of $f$ where $f$ changes sign there is a sharp
corner (a cusp)**, because the curve arrives with one gradient and
leaves with minus that gradient. The markscheme asks for these by name:
*"sharp points (cusps) at the $x$-intercepts."*

An asymptote gets folded too. If a branch that had the oblique asymptote
$y=5x+5$ lies below the axis and gets reflected, the reflected branch
has the asymptote $y=-5x-5$. Draw it; it is a mark.

**$y=f(\lvert x\rvert)$** — the left half is **discarded** and replaced
by a mirror image of the right half. The graph becomes even. Note which
half survives: the right one. Whatever $f$ did for $x<0$ is gone.

**$y=\dfrac{1}{f(x)}$** — the one that trades zeros for asymptotes:

| $f$ | $1/f$ |
| --- | --- |
| zero | vertical asymptote |
| vertical asymptote | tends to zero |
| $\pm 1$ | $\pm 1$ — the fixed points |
| local maximum, $f>0$ | local minimum |
| $\to \pm\infty$ | $\to 0$, so $y=0$ is a horizontal asymptote |

Two things go wrong here. The first is doing the trade only one way —
turning zeros into asymptotes and then leaving the old vertical
asymptote in place, where the new graph in fact goes to zero. The second
is the sign: near a vertical asymptote of $f$ the reciprocal approaches
$0$ from **above on one side and below on the other**, so the curve
crosses the level $y=0$ there without the point belonging to it.

**All three questions in the archive start from a picture, not a
formula.** In this notebook the picture is handed to you as a formula
that reproduces it — otherwise nothing could be checked. On paper you
will have only the picture, and the features are what you must extract
from it.
""")

md(r"""
## Task 11 🟡 — the modulus of a trigonometric function

The function $f$ is defined by $f(x)=\cos^{2}x - 3\sin^{2}x$,
$0\le x\le\pi$.

**(a)** Find the roots of the equation $f(x)=0$.

**(b)** Find $f'(x)$, and hence the coordinates of the point on the
graph of $y=f(x)$ where $f'(x)=0$.

**(c)** Sketch the graph of $y=\lvert f(x)\rvert$, clearly showing the
coordinates of any points where $f'(x)=0$ and any points where the graph
meets the coordinate axes.

For (c), give the cusps, the smooth maximum and both endpoints of the
domain.

*Source: November 2022, Paper 1, Q10(a)(b)(c) (5 + 7 + 4 marks, no
calculator). The corpus records the function with its squares lost, as
$\cos 2x - 3\sin 2x$; the solution shows how the markscheme settles it.*
""")

code(r"""
f11 = cos(x)**2 - 3*sin(x)**2

my11a = [...]            # the roots of f(x) = 0 on [0, pi]
my11b = ...              # f'(x)
my11c = {
    'cusps':     [...],          # [(x, y), ...]
    'maxima':    [...],          # [(x, y)]
    'endpoints': [...],          # [(x, y), (x, y)]
}

verify_root_set('Task 11(a)', my11a, f11, domain=(0, pi))
verify_identity('Task 11(b)', my11b, diff(f11, x))
verify_sketch('Task 11(c)', my11c, Abs(f11), domain=Interval(0, pi))
show((f11, 'y = f(x)'), (Abs(f11), 'y = |f(x)|'), span=(0, pi), size=(6, 3))
""")

md(r"""
## Task 12 🔴 — $\lvert f(\lvert x\rvert)\rvert$, and slicing the result

Part of the graph of a function $f$ is printed: it has a $y$-intercept
at $(0,3)$, an $x$-intercept at $(a,0)$ with $a>0$, and a horizontal
asymptote $y=-2$. It is flat at $y=3$ to the left of the origin and
decreases from there.

For $x\ge 0$ that graph is $f(x)=\dfrac{5}{1+x^{2}}-2$, and that is all
$g$ needs. Consider $g(x)=\bigl\lvert f(\lvert x\rvert)\bigr\rvert$.

**(a)** Sketch the graph of $y=g(x)$, labelling any axis intercepts and
giving the equation of the asymptote. Enter the intercepts, the
$y$-intercept, the smooth maximum, the cusps and the horizontal
asymptote.

**(b)** Find the possible values of $k$ such that $\bigl(g(x)\bigr)^{2}=k$
has exactly **two** solutions.

*Source: May 2023 TZ1, Paper 1, Q8 (4 + 3 marks, no calculator).*
""")

code(r"""
f12 = 5/(1 + x**2) - 2                   # the printed graph, for x ≥ 0
g12 = Abs(f12)                           # = |f(|x|)|, since f here is already even

my12a = {
    'x_intercepts':          [...],
    'y_intercept':           ...,
    'maxima':                [...],
    'cusps':                 [...],
    'horizontal_asymptotes': [...],
}
my12b = ...              # the set of values of k

verify_sketch('Task 12(a)', my12a, g12)
check_domain('Task 12(b)', my12b, '""" + D_12B + r"""')
show((f12, 'y = f(x), x ≥ 0'), (g12, 'y = g(x)'), span=(-4, 4), size=(6, 3))
""")

md(r"""
## Task 13 🔴 — folding a graph with an oblique asymptote

The graph of $f$ has a local maximum at $\mathrm{A}\left(-1,\,-\tfrac52\right)$,
a local minimum at $\mathrm{B}\left(0,\,\tfrac{15}{2}\right)$, a vertical
asymptote at $x=-\tfrac12$ and an oblique asymptote $y=5x+5$.

Those four facts determine $f$ completely, and it is

$$f(x) = 5x+5+\frac{5}{4x+2}.$$

Sketch the graph of $y=\lvert f(x)\rvert$, clearly indicating any
asymptotes. Enter the two local minima of the result, the vertical
asymptote, and **both** oblique asymptotes.

*Source: May 2025 TZ3, Paper 1, Q6(a) (4 marks, no calculator). The
corpus records A and B with the wrong signs and puts the maximum on the
asymptote; the solution reconstructs the function.*
""")

code(r"""
f13 = 5*x + 5 + 5/(4*x + 2)

my13 = {
    'minima':              [...],        # [(x, y), (x, y)]
    'vertical_asymptotes': [...],
    'oblique_asymptotes':  [...],        # expressions in x
}

verify_sketch('Task 13', my13, Abs(f13))
show((f13, 'y = f(x)'), (Abs(f13), 'y = |f(x)|'), span=(-3, 2), ylim=(-12, 18),
     size=(6, 4))
""")

md(r"""
## Task 14 🔴 — the reciprocal of the same graph

Same $f$. Sketch the graph of

$$y = \frac{15}{f(x)},$$

clearly indicating any asymptotes and intercepts with the axes.

Enter the $y$-intercept, the local maximum, the local minimum and the
horizontal asymptote. Then think about the question the check will not
ask you: **where did the vertical asymptote go?**

*Source: May 2025 TZ3, Paper 1, Q6(b) (3 marks, no calculator).*
""")

code(r"""
my14 = {
    'y_intercept':           ...,
    'maxima':                [...],
    'minima':                [...],
    'horizontal_asymptotes': [...],
}

verify_sketch('Task 14', my14, 15/f13)
show((15/f13, 'y = 15/f(x)'), span=(-4, 3), ylim=(-8, 4), size=(6, 3.5))
""")

md(r"""
---
# Part III — no graph is given, and you draw it

---
## Theory 6. What a sketch is worth, feature by feature

The instruction always names what to label, and the naming is the
markscheme. A four-mark sketch is typically:

* **A1** the shape — sinusoidal, parabolic, two branches, concave down;
* **A1** the intercepts, with values;
* **A1** the turning points, with **both** coordinates;
* **A1** the domain — where the curve starts and stops.

**Both coordinates.** "Maximum at $x=\tfrac{3m}{2}$" is half an answer.
The markscheme writes $\left(\tfrac{3m}{2},\,3\right)$ and pays for the
pair.

**The domain is a feature.** On $0\le x\le 6m$ the curve stops at $6m$,
and stopping is worth a mark. Restricted-domain questions almost always
put the endpoints where they can be checked: $\arccos x$ on $[-1,1]$ has
endpoints $(-1,\pi)$ and $(1,0)$, and those two points are the answer.

**For a stretched trigonometric function, get the period first.** With
$g(x)=3\sin\!\left(\tfrac{2qx}{3}\right)$ the amplitude is $3$ and the
period is

$$T=\frac{2\pi}{2q/3}=\frac{3\pi}{q},$$

and everything else — the zeros at $0,\tfrac{T}{2},T$, the maximum a
quarter of a period in — follows from $T$ alone. The lost mark is
computing the period from the wrong coefficient, or inverting the
stretch.

**When the question comes with a calculator,** the GDC draws the curve
and the marks are for reading it correctly: coordinates to 3 s.f.,
labelled, on the printed axes, stopped at the right place. That is why
the checks below compare coordinates at exactly three significant
figures.
""")

md(r"""
## Task 15 🟢 — two inverse-trigonometric graphs

**(a)** Consider $f(x)=\arccos x$ for $-1\le x\le 1$. Sketch the graph
of $y=f(x)$, clearly indicating the $y$-intercept and the coordinates of
the end points.

**(b)** A function $g$ is defined by
$g(x)=\arcsin\!\left(\dfrac{x^{2}-1}{x^{2}+1}\right)$ for $x\ge 0$, and
its inverse is

$$g^{-1}(x)=\sqrt{\frac{1+\sin x}{1-\sin x}},
\qquad -\frac{\pi}{2}\le x < \frac{\pi}{2}.$$

Sketch the graph of $y=g^{-1}(x)$, indicating any asymptotes with their
equations and the values of any axis intercepts.

*Sources: May 2025 TZ2, Paper 1, Q8(a) (2 marks, no calculator);
May 2021 TZ2, Paper 2, Q12(f) (3 marks). The formula for $g^{-1}$ is
B2's task 20 — here only the picture is wanted.*
""")

code(r"""
ginv = sqrt((1 + sin(x))/(1 - sin(x)))

my15a = {
    'y_intercept': ...,
    'endpoints':   [...],
}
my15b = {
    'y_intercept':         ...,
    'x_intercepts':        [...],
    'vertical_asymptotes': [...],
}

verify_sketch('Task 15(a)', my15a, acos(x), domain=Interval(-1, 1))
verify_sketch('Task 15(b)', my15b, ginv, domain=Interval.Ropen(-pi/2, pi/2))
show((acos(x), 'y = arccos x'), span=(-1, 1), size=(5.5, 3))
show((ginv, 'y = g inverse'), span=(-pi/2, pi/2 - 0.02), ylim=(0, 12), size=(5.5, 3))
""")

md(r"""
## Task 16 🟢 — a parabola in context

A particle $\mathrm{P}$ moves along the $x$-axis. Its velocity is
$v\,\mathrm{m\,s^{-1}}$ at time $t$ seconds, where

$$v(t) = 4 + 4t - 3t^{2}, \qquad 0 \le t \le 3 .$$

Sketch a graph of $v$ against $t$, clearly showing any points of
intersection with the axes.

Enter the $t$-intercept, the $v$-intercept, the vertex, and both
endpoints of the domain. (Everything is in `x` here — the check does not
know the letter is called $t$.)

*Source: November 2021, Paper 1, Q10(b) (4 marks, no calculator). The
corpus puts the right-hand endpoint at $(3,-5)$; check it yourself.*
""")

code(r"""
v16 = 4 + 4*x - 3*x**2

my16 = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'maxima':       [...],
    'endpoints':    [...],
}

verify_sketch('Task 16', my16, v16, domain=Interval(0, 3))
show((v16, 'v against t'), span=(0, 3), size=(5.5, 3))
""")

md(r"""
## Task 17 🟡 — a sine with two stretches

The function $f$ is defined by $f(x)=\sin qx$, where $q>0$. The graph of
$f$ for $0\le x\le 4m$ has $x$-intercepts at $x=0$, $2m$ and $4m$.

**(a)** Find an expression for $m$ in terms of $q$.

The function $g$ is defined by
$g(x)=3\sin\!\left(\dfrac{2qx}{3}\right)$ for $0\le x\le 6m$.

**(b)** Sketch the graph of $g$.

The check works the concrete case $q=1$, so $m=\tfrac{\pi}{2}$ and the
domain is $[0,3\pi]$. On the exam your answer stays in terms of $m$ —
which is the point of part (a).

*Source: May 2023 TZ1, Paper 1, Q5 (2 + 4 marks, no calculator).*
""")

code(r"""
q = Symbol('q', positive=True)
g17 = 3*sin(2*x/3)               # g with q = 1

my17a = ...              # m in terms of q
my17b = {
    'x_intercepts': [...],
    'maxima':       [...],
    'minima':       [...],
    'endpoints':    [...],
}

check_expr('Task 17(a)', my17a, '""" + D_17A + r"""')
verify_sketch('Task 17(b)', my17b, g17, domain=Interval(0, 3*pi))
show((sin(x), 'y = f(x), q = 1'), (g17, 'y = g(x)'), span=(0, 3*pi), size=(6.5, 3))
""")

md(r"""
## Task 18 🟡 — a composite, drawn with a calculator

The functions $f$ and $g$ are defined by $f(x)=2x-x^{3}$ and
$g(x)=\tan x$.

**(a)** Find $(f\circ g)(x)$.

**(b)** Sketch the graph of $y=(f\circ g)(x)$ for $-1\le x\le 1$,
writing down and clearly labelling the coordinates of any local maximum
or minimum points.

Give the coordinates to 3 s.f., the way the GDC reports them.

*Source: May 2023 TZ1, Paper 2, Q2 (2 + 3 marks).*
""")

code(r"""
my18a = ...              # (f ∘ g)(x)
my18b = {
    'maxima':       [...],
    'minima':       [...],
    'x_intercepts': [...],
}

check_series('Task 18(a)', my18a, '""" + D_18A + r"""')
verify_sketch('Task 18(b)', my18b, 2*tan(x) - tan(x)**3, domain=Interval(-1, 1))
show((2*tan(x) - tan(x)**3, 'y = (f o g)(x)'), span=(-1, 1), size=(5.5, 3))
""")

md(r"""
---
## Theory 7. Asymptotes come first, then the curve

For a rational function the sketch has a fixed order of operations, and
doing it in any other order costs time.

1. **Vertical asymptotes.** Set the denominator to zero. For
   $f(x)=\dfrac{4x+2}{x-2}$ that is $x=2$.
2. **Behaviour at infinity.** Divide out, or take the limit. Here
   $f(x)=4+\dfrac{10}{x-2}$, so $y=4$.
3. **Intercepts.** Numerator zero gives $x=-\tfrac12$; $f(0)=-1$.
4. **Which side of what.** You now have a grid of four regions and four
   numbers; the two branches are forced.
5. **The range comes free.** The horizontal asymptote is the value never
   reached: the range of $f$ is $y\ne 4$.

**"Label any asymptotes with their equations"** — the equations, not
dashed lines. That instruction is quoted verbatim in the archive and it
is an A1 of its own.

**The rectangular hyperbola $x^{2}-y^{2}=1$ is the same drill without a
function.** Intercepts at $(\pm1,0)$; no $y$-intercept; and rearranging
to $y=\pm\sqrt{x^{2}-1}$ shows that for large $\lvert x\rvert$ the
curve is $\pm\lvert x\rvert$, so the asymptotes are $y=x$ and $y=-x$.
Two branches, and the asymptotes are part of the answer even though no
point of the curve lies on them.
""")

md(r"""
## Task 19 🔴 — a rational function, its range and a vertex

Consider $f(x)=\dfrac{4x+2}{x-2}$, $x\ne 2$.

**(a)** Sketch the graph of $y=f(x)$, indicating the values of any axis
intercepts and labelling any asymptotes with their equations.

**(b)** Write down the range of $f$.

Now consider $g(x)=x^{2}+bx+c$. The graph of $g$ has an axis of symmetry
at $x=2$, and the two roots of $g(x)=0$ are $-\tfrac12$ and $p$, where
$p=\tfrac92$.

**(c)** Find the $y$-coordinate of the vertex of the graph of $y=g(x)$.

*Source: May 2024 TZ1, Paper 1, Q10(a)(b)(e) (5 + 1 + 2 marks, no
calculator).*
""")

code(r"""
f19 = (4*x + 2)/(x - 2)

my19a = {
    'x_intercepts':          [...],
    'y_intercept':           ...,
    'vertical_asymptotes':   [...],
    'horizontal_asymptotes': [...],
}
my19b = ...              # the range of f, as a set or an inequality
my19c = ...              # the y-coordinate of the vertex of g

verify_sketch('Task 19(a)', my19a, f19)
check_domain('Task 19(b)', my19b, '""" + D_19B + r"""')
check_num('Task 19(c)', my19c, 6, '""" + D_19C + r"""')
show((f19, 'y = f(x)'), span=(-8, 12), ylim=(-14, 22), size=(6, 3.5))
""")

md(r"""
## Task 20 🟡 — the rectangular hyperbola

The point $\bigl(f(\theta),\,g(\theta)\bigr)$, where
$f(z)=\tfrac{e^{z}+e^{-z}}{2}$ and $g(z)=\tfrac{e^{z}-e^{-z}}{2}$,
traces a curve with equation $x^{2}-y^{2}=1$. This hyperbola has two
asymptotes.

Sketch the graph of $x^{2}-y^{2}=1$, stating the coordinates of any axis
intercepts and the equation of each asymptote.

**(a)** The $x$-intercepts, as a set.
**(b)** The two asymptotes, as a set of expressions in `x`.
**(c)** The upper branch for $x\ge 1$ is $y=\sqrt{x^{2}-1}$. Enter its
endpoint and its oblique asymptote.

*Source: November 2021, Paper 3, Q1(f) (4 marks).*
""")

code(r"""
branch = sqrt(x**2 - 1)

my20a = [...]            # the x-intercepts of the hyperbola
my20b = [...]            # the two asymptotes, as expressions
my20c = {
    'endpoints':          [...],
    'oblique_asymptotes': [...],
}

check_set('Task 20(a)', my20a, '""" + D_20A + r"""')
check_set('Task 20(b)', my20b, '""" + D_20B + r"""')
verify_sketch('Task 20(c)', my20c, branch, domain=Interval(1, oo))
show((branch, 'upper branch'), (-branch, 'lower branch'), (x, 'y = x'),
     (-x, 'y = -x'), span=(-5, 5), ylim=(-5, 5), size=(5.5, 4))
""")

md(r"""
---
## Theory 8. Exploring a family

The Paper 3 questions of this topic all have the same shape: a formula
with a letter in it, and a question that asks for a **count**. How many
local maxima. How many points of inflexion with zero gradient. How many
intersection points. The calculator is not decoration here — it is the
method.

**Plot two or three members, never one.** $f_n(x)=x^{n}(2-x)^{n}$ looks
entirely different for $n$ odd and $n$ even, and a student who tries
$n=3$ alone will describe half the family.

**The parameter's range splits where the picture changes.** For
$y=\log_a x$ against $y=x$: below $a=1$ the logarithm is decreasing and
there is exactly one crossing; just above $1$ it rises steeply enough to
cross twice; past about $1.44$ it never catches the line at all. Three
intervals, three counts — and the boundary between the second and the
third is the tangency, which a later part of that question finds exactly.

**A point where $f''=0$ is not automatically a point of inflexion.** The
concavity has to *change*. For $x^{n}(2-x)^{n}$ with $n$ even, $f''$
vanishes at $x=0$ and $x=2$, and those are minima — the curve touches
the axis and comes back. With $n$ odd the same two points really are
inflexions with zero gradient. This is the single most reliable way to
get the table wrong.

**Say what stays the same.** Every member of that family has its maximum
at $x=1$, whatever $n$ is. Noticing that is usually what the next part
of the question is about.
""")

md(r"""
## Task 21 🟡 — counting, three times

**(a)** Sketch $y=\log_2 x$, stating the value of the non-zero
$x$-intercept and its vertical asymptote.

**(b)** The table gives three intervals for $a$. By investigating the
graph of $y=\log_a x$ against the line $y=x$, write down $p$, $q$, $r$.

| Interval | Number of intersection points |
| --- | --- |
| $0<a<1$ | $p$ |
| $1<a<1.4$ | $q$ |
| $1.5<a<2$ | $r$ |

**(c)** A function $f$ is defined by $f(x)=\dfrac{2(x+3)}{3(x+2)}$,
$x\ne -2$, and $g(x)=mx+1$. Write down the number of solutions to
$f(x)=g(x)$ for $m>0$.

*Sources: May 2023 TZ2, Paper 3, Q1(a) and Q1(d) (4 + 4 marks);
May 2024 TZ2, Paper 1, Q5(b)(i) (1 mark).*
""")

code(r"""
my21a = {
    'x_intercepts':        [...],
    'vertical_asymptotes': [...],
}
my21b = [...]            # p, q, r — in that order
my21c = ...              # the number of solutions

verify_sketch('Task 21(a)', my21a, log(x, 2), domain=Interval.open(0, oo))
check_order('Task 21(b)', my21b, '""" + D_21B + r"""', n=3)
check_num('Task 21(c)', my21c, 6, '""" + D_21C + r"""')

# The counting of (b) and (c), done by machine — try it after you have
# answered, and change the numbers to see the boundaries move.
for base in (0.5, 1.2, 1.8):
    print(f'a = {base}: ', count_roots(lambdify(x, log(x, base) - x), 0.001, 30))
for slope in (0.2, 1, 5):
    print(f'm = {slope}: ',
          count_roots(lambdify(x, 2*(x + 3)/(3*(x + 2)) - (slope*x + 1)), -50, 50, 20000))
show((log(x, 2), 'y = log2 x'), (log(x, 10), 'y = log10 x'), (x, 'y = x'),
     span=(0.05, 5), ylim=(-4, 5), size=(6, 3.5))
""")

md(r"""
---
## Trainer: name the technique in five seconds

Fifteen questions with no solutions. For each one write the code of the
technique — nothing else. No calculation is wanted; the point is to find
the first move before the drawing starts.

Codes: `read` (read a value off a graph) · `apply` (apply a translation
or a stretch) · `name` (name the sequence) · `match` (find the
parameters) · `sym` (use the symmetry) · `fold` ($\lvert f\rvert$,
$f(\lvert x\rvert)$, $1/f$) · `sketch` (sketch a curve you know) ·
`asym` (sketch with asymptotes) · `family` (explore a family)

1. Describe a sequence of transformations mapping $y=e^{x}$ onto $y=3e^{x-2}$.
2. Given the graph of $f$, sketch $y=\lvert f(x)\rvert$.
3. Sketch $y=2\cos 3x$ for $0\le x\le 2\pi$, labelling the maxima.
4. From the diagram, write down the value of $f(-1)$.
5. Use your GDC to explore $y=x^{n}-nx$ for $n=2,3,4$ and count the turning points.
6. $g(x)=af(x)+b$ maps the graph of $f$ onto the printed graph. Find $a$ and $b$.
7. Show that $f(x)=x^{3}\cos x$ is an odd function.
8. Sketch $y=\dfrac{3x-1}{x+4}$, labelling the asymptotes with their equations.
9. On the axes above, sketch $y=f(2x)-1$.
10. Sketch $y=\dfrac{1}{f(x)}$ given the graph of $f$.
11. Describe the transformation taking $y=\ln x$ to $y=\ln(5x)$.
12. Sketch $y=\arctan x$, stating the equations of its asymptotes.
13. The curve is symmetric in $y=x$ and passes through $(2,7)$. Write down another point on it.
14. For which values of $c$ does $y=x^{3}-3x+c$ meet the $x$-axis three times?
15. From the graph, write down the coordinates of the local minimum.
""")

code(r"""
answers = {
    1: '',   2: '',   3: '',   4: '',   5: '',
    6: '',   7: '',   8: '',   9: '',  10: '',
   11: '',  12: '',  13: '',  14: '',  15: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + r""")
""")

md(r"""
---
## Task 22 🔴 — on the timer, 14 minutes

The opening of a Paper 3 investigation. Nine marks, target time about
14 minutes.

*This question asks you to explore the behaviour and some key features
of the function $f_n(x)=x^{n}(a-x)^{n}$, where $a\in\mathbb{Z}^{+}$ and
$n\in\mathbb{Z}^{+}$. In parts (a) and (b), only consider the case
$a=2$.*

**(a)** Consider $f_1(x)=x(2-x)$. Sketch the graph of $y=f_1(x)$,
stating the values of any axes intercepts and the coordinates of any
local maximum or minimum points. [3]

**(b)** Consider $f_n(x)=x^{n}(2-x)^{n}$, $n>1$. Use your graphic
display calculator to explore the graph of $y=f_n(x)$ for the odd values
$n=3$ and $n=5$, and for the even values $n=2$ and $n=4$. Hence complete
the table. [6]

| | local maxima | local minima | inflexions with zero gradient |
| --- | --- | --- | --- |
| $n=3$ and $n=5$ | | | |
| $n=2$ and $n=4$ | | | |

Enter the six numbers reading across, odd row first.

*Source: May 2021 TZ2, Paper 3, Q1(a)(b) (3 + 6 marks).*
""")

code(r"""
my22a = {
    'x_intercepts': [...],
    'maxima':       [...],
}
my22b = [...]            # six numbers: odd row, then even row

verify_sketch('Task 22(a)', my22a, x*(2 - x), domain=Interval(-1, 3))
check_order('Task 22(b)', my22b, '""" + D_22B + r"""', n=6)

# The exploration itself. Change n and look before you answer.
for power in (2, 3, 4, 5):
    show((x**power*(2 - x)**power, f'n = {power}'), span=(-0.4, 2.4), size=(4.5, 2.4))
""")

md(r"""
---
# Solutions

A full discussion of every task, with the markscheme breakdown. Open it
after you have worked the task yourself: the point is not the answer but
where the marks are, and which of them a self-check cannot see.
""")

md(r"""
## Solution 1 — reading things off a graph

**(a)** From the picture, at $x=2$ the parabola is at its vertex, so
$f(2)=6$.

**(b)** $(f\circ f)(2)=f\bigl(f(2)\bigr)=f(6)$, and the curve ends at
$(6,-2)$, so the answer is $-2$. Two readings, and the first answer is
the second input — that is the entire question. The reliable error is
reading $6$ off the *horizontal* axis on the second pass.

**(c)** The gradient of $\mathrm{BC}$ is

$$\frac{-0.5625-0}{1.5-0} = -0.375,$$

and since $\mathrm{B}$ is the origin the line is $y=-0.375x$ with no
intercept to find. In the paper this is a "show that", so both marks are
for the two lines above, not for the answer.

**(d)** $y=x^{4}-mx^{3}+nx$ gives
$\dfrac{d^{2}y}{dx^{2}}=12x^{2}-6mx=6x(2x-m)$, which vanishes at $x=0$
and $x=\tfrac{m}{2}$. At $x=0$ the curve itself is $y=0$, so
$\mathrm{B}=(0,0)$ whatever $m$ and $n$ are.

**Why a one-mark question is worth having.** Parts (g) and (h) of that
investigation are algebra in $m$ and $n$, and every one of them starts
from $\mathrm{B}=(0,0)$. A question that looks free is often the one the
rest of the page rests on.
""")

md(r"""
## Solution 2 — apply a stretch and a translation

$g=\tfrac12 f+1$ is two vertical transformations, so every
$x$-coordinate stays exactly where it is and only the heights change:

$$y \mapsto \tfrac{y}{2}+1 .$$

Take the labelled points of $f$ one at a time.

| on $f$ | on $g$ |
| --- | --- |
| $(-4,4)$ | $(-4,3)$ |
| $(0,4)$ | $(0,3)$ |
| $(2,6)$ — maximum | $(2,4)$ — maximum |
| $(6,-2)$ | $(6,0)$ |

So the horizontal segment drops from $y=4$ to $y=3$, the vertex moves
from $(2,6)$ to $(2,4)$, and the right-hand end lands **on** the axis —
which is why $x=6$ is now an $x$-intercept and was not one before. The
markscheme awards its three marks for the flat piece at the right
height, the correct parabola shape with the vertex in place, and the
endpoints.

**The trap this question is built for** is redrawing the curve by eye.
Halve the heights and add one, point by point, and there is nothing to
get wrong; sketch first and check later, and the vertex lands at
$(1,4)$ or $(2,3)$.

**A note on the check.** `verify_sketch` accepted $x=6$ both as an
endpoint and as an $x$-intercept, because it is both. That is deliberate
— a zero the graph only touches, or reaches exactly at the end of its
domain, belongs to two lists at once.
""")

md(r"""
## Solution 3 — the stretch that inverts

**(a)** $y=f(kx)$ replaces $x$ by $kx$, and replacing $x$ by $kx$ is a
horizontal stretch with **scale factor $\tfrac1k$** — a dilation from
the $y$-axis. Both marks are there: one for naming the transformation,
one for the factor.

Why $\tfrac1k$ and not $k$: the new curve reaches at $x$ whatever the
old one reached at $kx$, so the point that was at $x=r$ is now at
$x=\tfrac{r}{k}$. With $k=2$ everything moves *closer* to the axis — a
stretch by $\tfrac12$.

**(b)** $f(kx)=0$ when $r^{2}-k^{2}x^{2}=0$, so
$x=\pm\dfrac{r}{k}$ — exactly the old intercepts $\pm r$ scaled by
$\tfrac1k$, as they must be.

**What this question is really for.** It is the setup for a surface of
revolution: the semi-ellipse is spun to make an ellipsoid, and part (v)
fits it to the Earth. The transformation is one line, and it is the line
the rest of the question is built on.
""")

md(r"""
## Solution 4 — two transformations of a sine

$$f(x)=4\sin x + 2.5, \qquad
g(x)=4\sin\!\left(x-\tfrac{3\pi}{2}\right)+2.5+q .$$

Inside the sine, $x$ became $x-\tfrac{3\pi}{2}$: a **horizontal
translation of $\tfrac{3\pi}{2}$ to the right**. Outside, $+q$: a
**vertical translation of $q$ upwards**. One mark each.

These two commute — they touch different coordinates — so the order is
free here, and `verify_transform` accepts both. That is not generosity;
it is what running the recipe actually shows.

**Where the marks go missing.** Writing "a translation of $\tfrac{3\pi}{2}$"
without saying which way, or writing "$\tfrac{3\pi}{2}$ to the left"
because the formula has a minus sign in it. $f(x-h)$ moves right; the
sign in the bracket is the opposite of the direction on the page, every
time.

**And a warning about vocabulary.** November 2025 TZ3 spells it out:
*translate*, *shift*, *dilate* and *stretch* are accepted; *move* is
not. A perfectly correct description in the wrong words scores zero.
""")

md(r"""
## Solution 5 — a sequence of three

Factor the argument so that $\arctan x$ is visible inside the target:

$$\arctan(2x+1)+\frac{\pi}{4}
= \arctan\!\Bigl(2\bigl(x+\tfrac12\bigr)\Bigr)+\frac{\pi}{4}.$$

Reading outwards from $x$:

1. horizontal stretch, scale factor $\tfrac12$ ($x\to 2x$);
2. horizontal translation $\tfrac12$ to the **left**;
3. vertical translation $\tfrac{\pi}{4}$ **up**.

**The other correct route** does the translation first, and then it is a
whole unit, not a half:

$$\arctan x \xrightarrow{\ 1 \text{ left}\ } \arctan(x+1)
\xrightarrow{\ \text{stretch } \tfrac12\ } \arctan(2x+1).$$

Both descriptions earn all three marks. What earns two is the pair
*stretch by $\tfrac12$, then $\tfrac12$ left* written in the other
order, giving $\arctan\!\left(2x+\tfrac12\right)$ — and that is the
mistake the check names for you.

**A cross-check that costs nothing.** The printed asymptotes are
$y=-\tfrac{\pi}{4}$ and $y=\tfrac{3\pi}{4}$. Since $\arctan$ has
asymptotes $\pm\tfrac{\pi}{2}$, and $-\tfrac{\pi}{2}+\tfrac{\pi}{4}
=-\tfrac{\pi}{4}$ while $\tfrac{\pi}{2}+\tfrac{\pi}{4}=\tfrac{3\pi}{4}$,
the vertical translation is confirmed by the diagram before you write
anything. Horizontal transformations leave those asymptotes alone, which
is why the diagram cannot help with steps 1 and 2.
""")

md(r"""
## Solution 6 — an identity first, then the sequence

**(a)** Angle-sum on $\sin(2\theta+\theta)$:

$$\sin 3\theta = \sin 2\theta\cos\theta + \cos 2\theta\sin\theta$$

is the M1A1. Then the double-angle identities and
$\cos^{2}\theta = 1-\sin^{2}\theta$:

$$= 2\sin\theta\cos^{2}\theta + \left(1-2\sin^{2}\theta\right)\sin\theta
= 2\sin\theta\left(1-\sin^{2}\theta\right) + \sin\theta - 2\sin^{3}\theta
= 3\sin\theta - 4\sin^{3}\theta .$$

**(b)** Put $\varphi=\theta+\tfrac{\pi}{6}$. The target is
$6\sin\varphi - 8\sin^{3}\varphi = 2\left(3\sin\varphi -
4\sin^{3}\varphi\right) = 2\sin 3\varphi$, so

$$y = 2\sin\!\left(3\theta+\tfrac{\pi}{2}\right)
= 2\sin\!\left(3\left(\theta+\tfrac{\pi}{6}\right)\right).$$

Three transformations, and the markscheme splits them 1 + 2:

* **A1** vertical stretch, factor $2$ — seen anywhere;
* **A2** horizontal stretch, factor $\tfrac13$, **followed by**
  horizontal translation $\tfrac{\pi}{6}$ to the left. Or: translation
  $\tfrac{\pi}{2}$ to the left **followed by** the stretch by $\tfrac13$.

And then, in the markscheme's own words: *"Award A1A0 for correct
horizontal transformations specified in the wrong order."* Both
orderings of $\tfrac13$ and a shift are written above, and they use
**different shifts** — $\tfrac{\pi}{6}$ after the stretch,
$\tfrac{\pi}{2}$ before it. Getting that pairing right is the second A1.

**A note on the corpus.** The archive metadata records the target of (b)
as $\dfrac{8\sin^{3}\theta+6\sin\theta}{6\sin\theta}$ — a fraction that
does not appear in the paper. It cancels to
$1+\tfrac43\sin^{2}\theta$, which has period $\pi$ and is not a sine
wave at all, so no sequence of stretches and translations reaches it
from $\sin\theta$. Curiously, the recorded *answer* — stretch $2$,
stretch $\tfrac13$, shift $\tfrac{\pi}{6}$ left — is right for the real
question. The error was found by trying to verify the answer rather than
by reading the question, which is the argument for checks that run
rather than compare.
""")

md(r"""
## Solution 7 — find the stretch and the translation

Apply the named steps with their letters in place:

$$f\!\left(\frac{x}{k}\right)+c
= e^{x/k}-\frac{3x}{k}-4+c .$$

Compare with $g(x)=e^{2x}-6x-7$:

* the exponent: $\dfrac{x}{k}=2x$, so $k=\tfrac12$;
* the linear term: $-\dfrac{3x}{1/2}=-6x$ ✓ — this one has to be
  *checked*, not solved;
* the constant: $-4+c=-7$, so $c=-3$.

The shortcut, if you see it: $g(x)=e^{2x}-6x-7=f(2x)-3$, and $f(2x)$ is
a horizontal stretch by $\tfrac12$. Same two answers, one line.

**Where the mark goes.** With only two marks there is no room: $k$ and
$c$, one each. The common wrong pair is $k=2$ (the stretch inverted) and
$c=-3$, which scores 1.

**A note on the corpus.** This question is in the archive twice —
November 2023 TZ1 and November 2023 TZ2 — because the whole session sits
there as two zones and the papers are the same paper. Two of B3's 107
marks are this duplicate. B2 established the duplication for the session
as a whole; this is the second topic where it lands.
""")

md(r"""
## Solution 8 — from the hyperbola $y=\frac1x$

**(a)** Substitute the two points into $y=\dfrac{Ax+B}{x-4}$:

$$\mathrm{P}(-10,1):\quad \frac{-10A+B}{-14}=1 \implies -10A+B=-14,$$
$$\mathrm{Q}(3,-12):\quad \frac{3A+B}{-1}=-12 \implies 3A+B=12 .$$

Subtracting, $13A=26$, so $A=2$ and $B=6$.

**(b)** Divide out before doing anything else:

$$\frac{2x+6}{x-4}=\frac{2(x-4)+14}{x-4}=2+\frac{14}{x-4}.$$

Now read it right to left from $y=\tfrac1x$:

1. horizontal translation $4$ to the right — and that is the vertical
   asymptote $x=4$;
2. vertical stretch, scale factor $14$;
3. vertical translation $2$ up — and that is the horizontal asymptote
   $y=2$.

The markscheme gives a mark for *either* recognising the asymptote or
naming the translation, in both directions, because **they are the same
fact**. Then A1 for the sequence, with the note: *"y-axis transformations
must be seen in the order above"* — stretch before shift. Stretching
after the shift would multiply the $2$ as well.

**The alternative it also accepts** is the stretch by $14$ followed by
the translation through the vector $\binom{4}{2}$ — one motion instead
of two, and the ordering problem disappears.
""")

md(r"""
## Solution 9 — two "show that"s

**(a)** $f(x)=2^{-x}-2^{x}$, so

$$f(-x)=2^{x}-2^{-x}=-\left(2^{-x}-2^{x}\right)=-f(x),$$

**therefore $f$ is odd.** Two marks: A1 for a correct $f(-x)$, A1 for
reaching $-f(x)$ **and saying so**.

**(b)** $f(x)=x\sqrt{1-x^{2}}$ on $[-1,1]$:

$$f(-x)=(-x)\sqrt{1-(-x)^{2}}=-x\sqrt{1-x^{2}}=-f(x),$$

therefore $f$ is odd. The square kills the sign inside the root, and the
factor in front carries it — that is the whole content.

**What the check cannot see.** `verify_identity` compares two
expressions. It confirms your line equals $-f(x)$; it cannot confirm
that your line came from substituting $-x$, and it certainly cannot see
the closing sentence. On this rung the last mark is an **R1 for a
sentence**, and no self-check in this notebook will ever award or
withhold it. Write it anyway — that is the mark.

**Where part (b) goes next.** The same question asks for the range,
$a\le y\le b$. Differentiating gives stationary points at
$x=\pm\tfrac{1}{\sqrt2}$ and $f\!\left(\tfrac{1}{\sqrt2}\right)=\tfrac12$,
so the range is $-\tfrac12\le y\le\tfrac12$ — and the oddness you just
proved is why the two ends are negatives of each other. That part is
classified under stationary points and belongs to E1.
""")

md(r"""
## Solution 10 — the line of symmetry $y=x$

Reflecting in $y=x$ swaps the two coordinates of every point. It also
swaps the two kinds of tangent: a tangent that was horizontal becomes
vertical, and vice versa.

So the images of $\mathrm{P}(0.331,\,-0.743)$ and
$\mathrm{Q}(1.84,\,-0.538)$ are

$$(-0.743,\ 0.331) \quad\text{and}\quad (-0.538,\ 1.84),$$

and those are the points with vertical tangents. **One mark, no
calculation.**

**Why it is only one mark and still worth practising.** Parts (a) and
(b) of that question are nine marks of implicit differentiation and a
numerical solve. Part (c) is free — *if* you read the sentence "the
curve has a line of symmetry $y=x$" as an instruction rather than as
scenery. Every year some candidates redo the whole calculation with
$\tfrac{dx}{dy}=0$.

**The markscheme's own warning:** *"Do not award FT from (b) if only one
coordinate pair is given."* Both points, or nothing.
""")

md(r"""
## Solution 11 — the modulus of a trigonometric function

**(a)** The fastest route is the double-angle identity:

$$f(x)=\cos^{2}x-3\sin^{2}x
= \frac{1+\cos 2x}{2}-3\cdot\frac{1-\cos 2x}{2}
= 2\cos 2x - 1 .$$

So $f(x)=0$ gives $\cos 2x=\tfrac12$, and on $0\le x\le\pi$ that is
$2x=\tfrac{\pi}{3},\tfrac{5\pi}{3}$, hence

$$x=\frac{\pi}{6},\qquad x=\frac{5\pi}{6}.$$

The markscheme also accepts $\tan^{2}x=\tfrac13$ — and warns that
dropping the $\pm$ and giving only $\tfrac{\pi}{6}$ costs two of the
five marks.

**(b)** $f'(x)=-4\sin 2x$, which vanishes at $x=0,\tfrac{\pi}{2},\pi$.
Only $\tfrac{\pi}{2}$ is interior, and $f\!\left(\tfrac{\pi}{2}\right)
=2\cos\pi-1=-3$. The point is $\left(\tfrac{\pi}{2},\,-3\right)$.

**(c)** Now fold. $\lvert f\rvert$ reflects the middle arch upwards:

* endpoints $(0,1)$ and $(\pi,1)$ — $f$ is $1$ at both ends;
* **cusps** at $\left(\tfrac{\pi}{6},0\right)$ and
  $\left(\tfrac{5\pi}{6},0\right)$ — the zeros of $f$, where the curve
  arrives with one gradient and leaves with minus it;
* a **smooth** maximum at $\left(\tfrac{\pi}{2},\,3\right)$ — the old
  minimum $-3$ turned over.

Four marks: the shape, the cusps, the maximum, the endpoints. Drawing
the cusps as smooth turns is the classic loss — the markscheme names
"sharp points" explicitly.

**A note on the corpus.** The archive records the function as
$\cos 2x-3\sin 2x$: the superscripts were flattened when the PDF became
text, and the result reads as a different, entirely plausible function.
The markscheme settles it in its own working — it reduces the equation
to $\cos 2x=\tfrac12$ and prints the roots $\tfrac{\pi}{6}$ and
$\tfrac{5\pi}{6}$, which are the roots of $\cos^{2}x-3\sin^{2}x$. The
recorded version would give $\tfrac{\pi}{12}$ and $\tfrac{7\pi}{12}$.
Same species as the five errors B2 found: what the extraction loses is
always a bar, a radical or an exponent.
""")

md(r"""
## Solution 12 — $\lvert f(\lvert x\rvert)\rvert$, and slicing the result

**(a)** Two folds, in this order:

1. $f(\lvert x\rvert)$ — keep $x\ge 0$, mirror it into $x<0$. The graph
   becomes even, with a smooth maximum at $(0,3)$ because the curve
   arrives at the axis flat.
2. $\lvert\cdot\rvert$ — reflect what is below the axis upwards. The
   tail that approached $y=-2$ now approaches $y=2$, and the crossings
   at $\pm a$ become cusps.

So: $y$-intercept $(0,3)$, a smooth maximum there, $x$-intercepts at
$\pm a$ with **sharp points**, and the horizontal asymptote $y=2$ on
both sides. With the model $f(x)=\dfrac{5}{1+x^{2}}-2$ used here,
$a=\sqrt{\tfrac32}=\tfrac{\sqrt6}{2}\approx 1.22$.

The markscheme's four marks: the right-hand shape with correct
asymptotic behaviour at $y=2$; the reflection into $x<0$ with the smooth
maximum at $(0,3)$; the labelled intercept at $(-a,0)$; the labelled
asymptote $y=2$, with cusps.

**(b)** $\bigl(g(x)\bigr)^{2}=k$ means $g(x)=\sqrt{k}$, and $g\ge 0$, so
count how often a horizontal line at height $c=\sqrt{k}$ meets the
graph. The graph runs $3$ down to $0$ at $\pm a$ and back up towards $2$
without reaching it:

| $c$ | crossings |
| --- | --- |
| $0$ | $2$ — the two cusps |
| $0<c<2$ | $4$ |
| $2\le c<3$ | $2$ |
| $c=3$ | $1$ — the maximum |

Exactly two solutions when $c=0$ or $2\le c<3$, that is

$$k=0 \quad\text{or}\quad 4\le k<9 .$$

**The half-open end is the whole question.** At $k=9$ the line touches
the maximum once, not twice; at $k=4$ it grazes the asymptote level and
still cuts the two outer tails twice. A1 for $k=0$, A2 for the interval,
and the markscheme's fallback A1 is for having $4$ and $9$ written down
anywhere.
""")

md(r"""
## Solution 13 — folding a graph with an oblique asymptote

**Reconstructing $f$.** An oblique asymptote $y=5x+5$ and a vertical
asymptote $x=-\tfrac12$ mean

$$f(x)=5x+5+\frac{\lambda}{x+\tfrac12},$$

and $f(0)=\tfrac{15}{2}$ gives $5+2\lambda=\tfrac{15}{2}$, so
$\lambda=\tfrac54$:

$$f(x)=5x+5+\frac{5}{4x+2}.$$

Check: $f'(x)=5-\dfrac{5/4}{\left(x+\tfrac12\right)^{2}}=0$ at
$x=0$ and $x=-1$, and $f(-1)=-\tfrac52$. Both printed points confirmed.

**The fold.** $\lvert f\rvert$ leaves the right branch alone — it is
positive throughout, with its minimum $\left(0,\tfrac{15}{2}\right)$ —
and turns the left branch over. The left branch was negative, with a
maximum $\left(-1,-\tfrac52\right)$; reflected, that becomes a
**minimum** at $\left(-1,\tfrac52\right)$.

The asymptotes fold with it. The left branch was asymptotic to
$y=5x+5$; reflected, it is asymptotic to $y=-5x-5$. And $x=-\tfrac12$
stays, on both sides, now going to $+\infty$ in both directions.

Four marks, and the markscheme spends one of them on that reflected
oblique asymptote — *"drawn in approximately correct position (equation
is not required)"*. Leaving it out is the standard loss on this rung.

**A note on the corpus.** The archive records $\mathrm{A}$ as
$\left(-\tfrac12,\tfrac52\right)$ and $\mathrm{B}$ as
$\left(0,-\tfrac{15}{2}\right)$ — both signs wrong and one abscissa
wrong. The recorded version is internally impossible: it puts the local
maximum at $x=-\tfrac12$, which is where the vertical asymptote is. The
paper's numbers, read from the page, are what pin the function down, and
without the function this task could not be checked at all.
""")

md(r"""
## Solution 14 — the reciprocal of the same graph

Trade zeros for asymptotes, and turning points for turning points.

* $f$ has **no real zeros**: $f(x)=0$ gives $20x^{2}+30x+15=0$, whose
  discriminant is $900-1200<0$. So $y=\tfrac{15}{f}$ has **no vertical
  asymptote at all**.
* $f\to\pm\infty$ at $x=-\tfrac12$ and at both ends, so
  $\tfrac{15}{f}\to 0$ everywhere: $y=0$ is a horizontal asymptote,
  and near $x=-\tfrac12$ the curve dives to $0$ from below on the left
  and comes back from above on the right.
* The minimum $f=\tfrac{15}{2}$ at $x=0$ becomes the **maximum**
  $\tfrac{15}{15/2}=2$: the point $(0,2)$, which is also the
  $y$-intercept.
* The maximum $f=-\tfrac52$ at $x=-1$ becomes the **minimum**
  $\tfrac{15}{-5/2}=-6$: the point $(-1,-6)$.

Three marks: axes intercepts in about the right place, local extrema in
about the right place, asymptotic behaviour to $y=0$ on both sides.

**Where did the vertical asymptote go?** It became a zero — almost. The
curve approaches the height $0$ from both sides at $x=-\tfrac12$, but
$x=-\tfrac12$ is not in the domain, so the point itself is missing. That
half-completed trade is the mistake this rung is built to catch, and the
archive metadata for this very question falls into it: it records
"vertical asymptote remains $x=-\tfrac12$", which the markscheme never
asks for and the function does not have.
""")

md(r"""
## Solution 15 — two inverse-trigonometric graphs

**(a)** $\arccos$ runs from $(-1,\pi)$ down to $(1,0)$, decreasing,
through $\left(0,\tfrac{\pi}{2}\right)$ — and that is the entire
two-mark answer: A1 for the shape on the right domain, A1 for the three
labelled points. The single reliable error is drawing $\arcsin$ instead,
which rises.

**(b)** Feature by feature, from
$g^{-1}(x)=\sqrt{\dfrac{1+\sin x}{1-\sin x}}$ on
$-\tfrac{\pi}{2}\le x<\tfrac{\pi}{2}$:

* at $x=-\tfrac{\pi}{2}$: $\sin x=-1$, so the numerator vanishes and
  $g^{-1}=0$ — the graph starts **on** the axis, so that endpoint is
  also the $x$-intercept;
* at $x=0$: $\sqrt{\tfrac{1}{1}}=1$, the $y$-intercept;
* as $x\to\tfrac{\pi}{2}^{-}$: $\sin x\to 1$, the denominator vanishes,
  $g^{-1}\to+\infty$ — the vertical asymptote $x=\tfrac{\pi}{2}$;
* increasing throughout, with range $[0,\infty)$.

Three marks: the curve on the right domain, the intercept, the asymptote
**with its equation**.

**Why the domain has that shape.** $g$ maps $[0,\infty)$ onto
$\left[-\tfrac{\pi}{2},\tfrac{\pi}{2}\right)$ — closed at the bottom
because $g(0)=\arcsin(-1)$ is attained, open at the top because
$\tfrac{x^{2}-1}{x^{2}+1}\to 1$ without arriving. Domain and range swap
for the inverse, and the half-openness swaps with them. That is B2's
rung 8; here it arrives as a fact and the drawing is the work.
""")

md(r"""
## Solution 16 — a parabola in context

$v(t)=4+4t-3t^{2}$ on $0\le t\le 3$, and $-3<0$ so it is concave down.

* $v$-intercept: $v(0)=4$.
* $t$-intercepts: $3t^{2}-4t-4=0$ gives $t=2$ and $t=-\tfrac23$; the
  second is outside the domain and is **rejected**, which is a mark.
* Vertex: $v'(t)=4-6t=0$ at $t=\tfrac23$, and
  $v\!\left(\tfrac23\right)=4+\tfrac83-\tfrac43=\tfrac{16}{3}\approx 5.33$.
* Right-hand end: $v(3)=4+12-27=-11$.

Four marks: the two intercepts, the vertex, and the concave-down shape
running from $(0,4)$ to $(3,-11)$.

**The physics is the reason the domain matters.** The particle is moving
forward until $t=2$ and backward after it, which is why the next part —
the total distance travelled — has to be integrated in two pieces. A
sketch that runs past $t=3$, or that stops at the $t$-axis, loses the
question as well as the mark.

**A note on the corpus.** The archive records the right-hand endpoint as
$(3,-5)$. It is $(3,-11)$; the rest of the recorded method is right.
""")

md(r"""
## Solution 17 — a sine with two stretches

**(a)** $f(x)=\sin qx$ has $x$-intercepts at $0,2m,4m$, so a **full
period** is $4m$:

$$\frac{2\pi}{q}=4m \implies m=\frac{\pi}{2q}.$$

The markscheme also accepts the route through the first maximum,
$\sin qm=1$. Two marks.

**(b)** $g(x)=3\sin\!\left(\dfrac{2qx}{3}\right)$:

* amplitude $3$;
* period $\dfrac{2\pi}{2q/3}=\dfrac{3\pi}{q}=6m$ — so the whole domain
  $[0,6m]$ is **exactly one period**;
* zeros at $0$, $3m$, $6m$;
* maximum at $\left(\tfrac{3m}{2},\,3\right)$, minimum at
  $\left(\tfrac{9m}{2},\,-3\right)$.

The markscheme is explicit that the curve must be *"an approximate
sinusoidal shape"* before any other mark is awarded, and then A1 for the
amplitude, A1 for the domain, A1 for the max, min and intercepts
together.

**Compared with $f$, $g$ is a horizontal stretch by $\tfrac32$ and a
vertical stretch by $3$** — the note in the markscheme says the
horizontal factor $\tfrac32$ *"may be earned by seeing a period of $6m$,
half period of $3m$, or the correct $x$-coordinate of the maximum"*.
Three different ways to show you know one number.

**On the check.** It runs the concrete case $q=1$, so $m=\tfrac{\pi}{2}$
and the domain is $[0,3\pi]$; the coordinates come out as
$\left(\tfrac{3\pi}{4},3\right)$ and $\left(\tfrac{9\pi}{4},-3\right)$,
which are $\tfrac{3m}{2}$ and $\tfrac{9m}{2}$. In the exam the answer
stays in $m$, and there is no machine to substitute for you — which is
exactly what part (a) is preparing.
""")

md(r"""
## Solution 18 — a composite, drawn with a calculator

**(a)** $(f\circ g)(x)=f(\tan x)=2\tan x-\tan^{3}x$. Two marks, and the
order is the mark: $g$ first, because it sits next to the bracket.

**(b)** On $-1\le x\le 1$ the GDC gives

$$\text{maximum } (0.685,\ 1.09), \qquad
\text{minimum } (-0.685,\ -1.09),$$

with the curve passing through the origin, crossing again near
$x=\pm0.955$ (where $\tan^{2}x=2$), and ending at about
$(\pm1,\ \mp0.663)$.

The function is **odd** — $\tan$ is odd and both powers are odd — which
is why the two turning points are exact negatives of each other. Noticing
that halves the calculator work and doubles the confidence.

Three marks: the odd shape through the origin, the endpoints, the two
labelled points.

**Precision is the mark here.** The true maximum is at $x=0.68472\ldots$
with $y=1.08866\ldots$, and the markscheme wants three significant
figures. `verify_sketch` compares at exactly that precision, so $1.09$
passes and $1.1$ does not — which is also, honestly, its limit: an
answer wrong in the fourth digit would pass too.
""")

md(r"""
## Solution 19 — a rational function, its range and a vertex

**(a)** In the fixed order:

1. vertical asymptote: $x-2=0$, so $x=2$;
2. behaviour at infinity:
   $f(x)=\dfrac{4(x-2)+10}{x-2}=4+\dfrac{10}{x-2}$, so $y=4$;
3. $x$-intercept: $4x+2=0$, so $x=-\tfrac12$;
4. $y$-intercept: $f(0)=\tfrac{2}{-2}=-1$;
5. two branches, upper right and lower left, neither crossing either
   asymptote.

Five marks — one of them purely for writing $x=2$ and $y=4$ **as
equations** next to the dashed lines.

**(b)** The horizontal asymptote is the value the function never takes,
so the range is $y\ne 4$, i.e. $\mathbb{R}\setminus\{4\}$. One mark, and
it is free once the sketch is right — which is why part (a) comes first.

**(c)** The axis of symmetry is halfway between the roots:
$\tfrac12\left(-\tfrac12+p\right)=2$ gives $p=\tfrac92$. Then

$$g(x)=\left(x+\tfrac12\right)\left(x-\tfrac92\right)
= x^{2}-4x-\tfrac94,$$

so $b=-4$, $c=-\tfrac94$, and the vertex is at $x=2$ with

$$g(2)=4-8-\tfrac94=-\tfrac{25}{4}.$$

**The shortcut worth knowing:** the vertex sits on the axis of symmetry,
which you were *given*. You never need to complete the square — just
substitute $x=2$.
""")

md(r"""
## Solution 20 — the rectangular hyperbola

**(a)** $y=0$ gives $x^{2}=1$, so the intercepts are $(\pm1,0)$. There
is no $y$-intercept: $x=0$ would need $y^{2}=-1$.

**(b)** Rearranged, $y=\pm\sqrt{x^{2}-1}$, and for large $\lvert x\rvert$

$$\sqrt{x^{2}-1}=\lvert x\rvert\sqrt{1-\tfrac{1}{x^{2}}}\to\lvert x\rvert,$$

so the asymptotes are $y=x$ and $y=-x$. Equivalently, $x^{2}-y^{2}=0$ is
the degenerate member of the family $x^{2}-y^{2}=k$.

**(c)** The branch $y=\sqrt{x^{2}-1}$ for $x\ge 1$ starts at $(1,0)$
with a **vertical** tangent and rises to the asymptote $y=x$ from below.
The other three quarters follow by symmetry — the curve is symmetric in
both axes.

Four marks: two branches in the right quadrants, the intercepts stated,
both asymptote equations, the asymptotic behaviour.

**The trap is thinking the asymptotes are not part of the answer.** They
contain no point of the curve, and the question still asks for *"the
equation of each asymptote"*. Draw them dashed and label them.

**Where this comes from.** $f(z)=\cosh z$ and $g(z)=\sinh z$, and
$\cosh^{2}-\sinh^{2}=1$ is exactly this hyperbola — the identity part
(e) of the same question has just proved. The exam never names them.
""")

md(r"""
## Solution 21 — counting, three times

**(a)** $y=\log_2 x$: domain $x>0$, vertical asymptote $x=0$, passing
through $(1,0)$, increasing and concave down. $\log_{10}x$ has the same
three features and lies **below** $\log_2 x$ for $x>1$ and **above** it
for $0<x<1$ — they cross only at $(1,0)$. Four marks, and one of them is
for that relative position.

**(b)** Against $y=x$:

* $0<a<1$: the logarithm decreases from $+\infty$, the line increases —
  exactly **one** crossing. $p=1$.
* $1<a<1.4$: the logarithm rises fast enough near the origin to get
  above the line and then falls back below it — **two** crossings.
  $q=2$.
* $1.5<a<2$: it never catches the line — **none**. $r=0$.

The boundary between the second and third cases is the value of $a$ for
which $y=x$ is a *tangent*; part (e) of that question finds it exactly,
$a=e^{1/e}\approx 1.444$, which is why the table skips the interval
$1.4$ to $1.5$.

**(c)** $f(x)=g(x)$ with $f(x)=\dfrac{2(x+3)}{3(x+2)}$ and $g(x)=mx+1$:

$$2(x+3)=3(x+2)(mx+1) \implies 3mx^{2}+(1+6m)x=0
\implies x\bigl(3mx+1+6m\bigr)=0 .$$

So $x=0$ always, and $x=-\dfrac{1+6m}{3m}$, which for $m>0$ is a second,
different root (and never $-2$). **Two solutions.**

That the line passes through $(0,1)$, which is on the curve, is the
whole trick: $x=0$ is a solution for *every* $m$, so the count is
"one always, plus one more". The later parts of the question use the
same factorisation to find where the two roots collide.
""")

md(r"""
## Solution 22 — the timed task

**(a)** $f_1(x)=x(2-x)$ is a downward parabola with roots $0$ and $2$,
so:

* $x$-intercepts $(0,0)$ and $(2,0)$; $y$-intercept $(0,0)$;
* vertex halfway between the roots, at $x=1$, with $f_1(1)=1$;
* local **maximum** $(1,1)$.

Three marks: shape, intercepts, the labelled maximum. Giving "maximum at
$x=1$" without the height is the half answer that scores half.

**(b)** $f_n(x)=x^{n}(2-x)^{n}=\bigl(x(2-x)\bigr)^{n}$ — it is the
parabola raised to the $n$-th power, which is the fastest way to see the
answer without a calculator at all.

* **$n$ odd** ($3$, $5$): raising to an odd power keeps the sign, so the
  curve is negative outside $[0,2]$ and positive inside. It rises through
  $x=0$, peaks at $x=1$, falls through $x=2$. At $0$ and $2$ the root is
  of odd multiplicity $\ge 3$, so the curve *flattens and passes
  through*: gradient zero, concavity changing — points of inflexion with
  zero gradient. **1 maximum, 0 minima, 2 inflexions.**
* **$n$ even** ($2$, $4$): the power kills the sign, so $f_n\ge 0$
  everywhere and touches zero at $0$ and $2$. Those are **minima**.
  **1 maximum, 2 minima, 0 inflexions.**

Six marks, one per cell.

**The trap, and it is a good one.** For $n$ even, $f''$ *does* vanish at
$x=0$ and $x=2$ — the root has multiplicity $4$ or more. A candidate who
tests $f''=0$ and stops will write $2$ in the inflexion column. A point
of inflexion needs the concavity to **change**, and at a minimum it does
not. Plot $n=2$ and $n=3$ side by side and the difference is
unmistakable; that is what "use your graphic display calculator to
explore" is asking for.

**What stays the same across the family** is the maximum at $x=1$ —
which is what part (c) onwards is about, generalised to
$f_n(x)=x^{n}(a-x)^{n}$ with its maximum at $x=\tfrac{a}{2}$.
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

OUT = os.path.join(ROOT, 'practicum/functions',
                   'practicum-b3-transformations.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)

print(f'записано {OUT}: {len(cells)} ячеек')
