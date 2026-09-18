"""Собирает практикум E8: стационарные точки, вогнутость, перегиб.

Тридцать четвёртый практикум серии. Тема calculus.stationary_points целиком:
43 блока и 114 баллов, 39 блоков и 101 балл после вычета ноябрьского 2023
дубля. Внутри верхней границы гранулярности, и разрезать её незачем.

Лестница из восьми приёмов идёт по тому, что спрашивают о точке: найти её,
определить вид двумя разными способами, найти перегиб, найти точки семейства
с буквой, сказать, где они лежат, посчитать, сколько их при каком параметре,
и показать, что их нет вовсе.

Двадцать седьмое понятие равенства ответов: **вид точки решают соседи, а не
вторая производная**. Максимум — место, рядом с которым кривая ниже с обеих
сторон; перегиб — место, где меняется сторона выгиба. Проверка идёт по кривой
шагами и смотрит; ни первой производной, ни второй внутри неё нет.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e8.py прогоняет по нему весь ноутбук и требует, чтобы
каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/calculus/practicum-e8-stationary-points.ipynb')

TRIGGER = {1: 'find', 2: 'classify', 3: 'sign', 4: 'inflexion', 5: 'family',
           6: 'side', 7: 'count', 8: 'none', 9: 'find', 10: 'inflexion',
           11: 'classify', 12: 'count'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1': '(2, Rational(-64, 3))',
    'q2a': '(0.709, 0.640)',
    'q2b': '[(-1.94, 1.20), (1.94, -1.20)]',
    'q3b': "'maximum'",
    'q3d': "'inflexion'",
    'q4a': '[(0, E), (pi/2, exp(-1)), (pi, E)]',
    'q4b': "['maximum', 'minimum', 'maximum']",
    'q5': 'Interval(Rational(-1, 2), Rational(1, 2))',
    'q6a': '-1.60',
    'q6b': '0.656',
    'q7e': '[(0, b), (-2*a/3, 4*a**3/27 + b)]',
    'q7f_i': "['minimum', 'maximum']",
    'q7f_ii': "['above', 'above']",
    'q7g': '4*a**3/27 + b < 0',
    'q8_i': '24*x - 4*(a + b)',
    'q8_ii': "'maximum'",
    'q9c_i': 'FiniteSet(0)',
    'q9c_ii': 'Interval.open(0, oo)',
    'q9c_iii': 'Interval.open(-oo, 0)',
    'q9d': '[(-sqrt(c), 2*c**Rational(3, 2) + 2),\n        (sqrt(c), -2*c**Rational(3, 2) + 2)]',
    'q10e_i': 'Interval.open(0, 1)',
    'q10e_ii': 'FiniteSet(1)',
    'q10e_iii': 'Interval.open(1, oo)',
    'q10f': 'Or(c <= 0, d > 2*c**Rational(3, 2), d < -2*c**Rational(3, 2))',
    'q11d': '[]',
    'q11e': 'sqrt((2*sqrt(3) - 3)/3)',
    'q12_i': "'minimum'",
    'q12_ii': "'inflexion'",
    'qt': '[]',
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
# E8 — Stationary points, concavity, inflexion

**101 marks of the archive, eight techniques, twelve tasks.** Everything the
archive asks about the shape of a graph from May 2021 to November 2025: where
the gradient is zero, what kind of point sits there, where the curve changes
the way it bends, what happens when the function carries a letter, and how to
show that there is no such point at all.

## The one idea

A stationary point is not a formula. It is a **place on the curve**, and three
questions can be asked about it, in this order:

1. **Where is it?** — solve $f'(x)=0$, and then go back to $f$ for the second
   coordinate. Two marks, and the second one is lost more often than the first.
2. **What kind is it?** — a maximum, a minimum, or a point of inflexion with
   zero gradient.
3. **Where does it lie?** — above or below the $x$-axis. This is a different
   question from the second, and it carries its own mark.

## And what decides the kind

$$f''(a)<0\ \Rightarrow\ \text{maximum},\qquad f''(a)>0\ \Rightarrow\ \text{minimum}$$

and when $f''(a)=0$ **this test says nothing at all**. Not "inflexion" — nothing.
Both $y=x^4$ (a minimum at the origin) and $y=x^3$ (an inflexion at the origin)
have $f''(0)=0$.

What always works is looking at the neighbours:

| the curve next to $a$ | the point at $a$ |
|---|---|
| lower on both sides | a maximum |
| higher on both sides | a minimum |
| higher one side, lower the other, and $f'(a)=0$ | an inflexion with zero gradient |

And a point of inflexion, stationary or not, is where the curve **stops bending
one way and starts bending the other**.

## How the checks work

They do not know the answers, and they do not differentiate. A curve is handed
to them the way the question names it, and the check **walks along it**:

```python
verify_turning('1', q1, f, 'minimum', domain=(0, 5))
verify_nature('4b', q4b, f, [0, pi/2, pi])
verify_bend('6a', q6a, f, domain=(-3, -0.55))
```

The first is *"is that the only local minimum of this curve with $x>0$?"* —
the check finds every place where the curve is flat and compares. The second
is *"what kind of point is each of these?"* — the check looks at the
neighbours. The third measures the bend with a chord.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| $(2,-64)$ | the first coordinate is right and the second is not |
| one point where there are two | not all of them are there, the first missing one is near … |
| `'minimum'` at a maximum | the curve is lower next to this point, not higher |
| $-1.61$ for the inflexion | there is a real point of inflexion next to that answer: check the third figure |
| $c\ge 0$ instead of $c>0$ | at $c=0$ the condition says yes, and the property is not there |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | find the point, name its kind | 1–4 |
| 🟡 | the range, the inflexion, a letter in the function | 5–8 |
| 🔴 | conditions on a parameter, implicit curves, parity | 9–12 |

Every task is a real past-paper question, cited.

**70 of the 101 marks are on a calculator paper, and the calculator earns
about 13 of them.** Two thirds of this topic lives in Paper 3 investigations,
where the answer is a letter, a word or an inequality — and none of the three
has a button.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + curve, stationary, nature, crossings

language('en')                 # this notebook is in English, and so are the checks

# stationary(f, domain) — every place where the curve is flat, with its kind.
# nature(f, at) — 'maximum', 'minimum', 'inflexion' or 'neither'.
# concavity(f, at) — 'up' or 'down', measured with a chord.
# inflexions(f, domain) — every place where the bend changes side.
# crossings(f, domain) — how many different points of the x-axis the curve meets.
# curve(Eq(...)) — a curve given by an equation, walked the same way.

print('ready; sympy', sp.__version__)
sample = x**3 - 6*x**2 + 9*x + 1
print('flat places:   ', stationary(sample, (-1, 5)))
print('bend at x = 1: ', concavity(sample, 1), ' at x = 3:', concavity(sample, 3))
""")

md(r"""
---
## Map of the eight techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | find the point | *find the coordinates of the local minimum*, *where the gradient is zero* | $f'(x)=0$, then back to $f$ |
| 2 | name the kind | *using the second derivative, show that …*, *determine whether each point is a maximum or a minimum* | the sign of $f''$ at the point |
| 3 | the sign of $f'$ | *state, with a reason, whether …*, *by considering the sign of $f'(-1)$* | $f'$ changes sign, or it does not |
| 4 | the inflexion | *find the $x$-coordinate of the point of inflexion* | $f''=0$ **and** the concavity changes |
| 5 | a family | *show that the curve has a point of zero gradient at $P(0,b)$* | the same work, with a letter instead of a number |
| 6 | which side | *state whether each point is above or below the $x$-axis* | the sign of the stationary value |
| 7 | how many | *find the set of values of $c$ such that …* | count the flat places, or the crossings |
| 8 | there are none | *show that the curve has no local maximum or minimum points* | $f'(x)=0$ has no solution in the domain |

Techniques 1–4 are one point read four ways. Technique 5 changes nothing but
the alphabet. Techniques 6–8 are all the same question in disguise: **how many
of these points are there, and where do they sit** — and the answer is a set,
an inequality or the empty list.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Find it, and name it

## Theory: the two coordinates

Take $f(x)=x^3-6x^2+9x+1$. Then $f'(x)=3x^2-12x+9=3(x-1)(x-3)$, so the graph is
flat at $x=1$ and at $x=3$. That is **half the answer**. A point has two
coordinates, and the second one comes from $f$, never from $f'$:

$$f(1)=1-6+9+1=5,\qquad f(3)=27-54+27+1=1$$

so the stationary points are $(1,5)$ and $(3,1)$.

> **The mark that goes missing.** "Find the coordinates of the local minimum
> point" is two marks in nearly every paper: one for $x$, one for $y$. Writing
> $x=3$ and stopping loses the second. Writing $f'(3)=0$ as the second
> coordinate loses it too — that number is zero at every stationary point and
> says nothing.

**Which of them is which?** Between $x=1$ and $x=3$ the factor $(x-1)$ is
positive and $(x-3)$ is negative, so $f'<0$ there: the curve goes down from
$(1,5)$ to $(3,1)$. The first is a maximum, the second a minimum.

**A restricted domain adds its own flat places.** On a closed interval the
smallest and largest values of $f$ can sit at the ends, where $f'$ is not zero
at all. The question will say which it wants: *stationary points* means
$f'=0$; *the range* means the ends count too.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ1 Paper 1 Q1, 5 marks*

Consider the function

$$f(x)=\frac{4x^3}{3}-16x,\qquad x\in\mathbb R$$

The graph of $y=f(x)$ has a local minimum point at $(p,q)$ where $p>0$.

Find the value of $p$ and the value of $q$.

*Enter the point as a pair. The answer is exact — no calculator was allowed.*
""")

code(r"""
q1 = ...         # the point (p, q)

f = 4*x**3/3 - 16*x

verify_turning('1', q1, f, 'minimum', domain=(0, 6))
""")

# ================================================================= теория 2
md(r"""
## Theory: when the calculator does the finding

Two marks, one screen. `fMin`, `fMax` or the graph's own *maximum* command
gives both coordinates at once, and the answer is written to three significant
figures.

For $y=\dfrac{x}{x^2+4}$ on $-6\le x\le 6$ the calculator returns $(2,0.25)$
and $(-2,-0.25)$ — and here the exact values happen to be short, which is the
exception. Usually they are not, and the paper asks for three figures on
purpose.

**Two things the screen will not tell you.**

* **Which is which.** The calculator labels a maximum on the piece of graph it
  can see. On a curve with two humps, the *local* maximum you are asked about
  may not be the highest point on the screen.
* **Whether you found them all.** Zoom out before you answer. A stationary
  point outside the window is still in the domain.

> **Round only at the end.** Feed the calculator's own stored value back into
> $f$ for the second coordinate; typing in the rounded $x$ can move the third
> significant figure of $y$.
""")

md(r"""
### Task 2 🟢 — *November 2022 Paper 2 Q2(a) and May 2025 TZ2 Paper 3 Q1(a)(iii), 4 marks*

**(a)** The function $f$ is defined as $f(x)=\ln(xe^x+1)-x^4$ for $0\le x\le 2$.
The graph of $f$ has a local maximum at point $A$. Find the coordinates of $A$.

**(b)** Consider the curve given by

$$y=\frac{x\left(x^2-16\right)}{x^2+16}$$

State the coordinates of the local maximum point and the coordinates of the
local minimum point.

*Three significant figures throughout. In (b) give both points as a list.*
""")

code(r"""
q2a = ...        # the coordinates of A
q2b = [...]      # the local maximum and the local minimum

first = log(x*exp(x) + 1) - x**4
second = x*(x**2 - 16)/(x**2 + 16)

verify_turning('2(a)', q2a, first, 'maximum', domain=(0, 2))
verify_turning('2(b)', q2b, second, domain=(-10, 10))
""")

# ================================================================= теория 3
md(r"""
## Theory: the sign of $f'$, read off a diagram

Sometimes the derivative is never computed at all — you are handed its sign.

$$\begin{array}{c|ccc}
x & \cdots\ \ -1\ \ \cdots & \ \ 2\ \ & \cdots\\\hline
f'(x) & - & 0 & +
\end{array}$$

The gradient goes from negative to positive at $x=2$: the curve falls, flattens
and rises, so $x=2$ carries a **local minimum**. That is the whole argument, and
in the markscheme it is worth as much as the word itself — *state, with a
reason* means the reason is a separate mark.

**The same reading for $f''$.** Where $f''$ changes sign the curve changes the
side it bends to, and that is a **point of inflexion**.

> **$f''(c)=0$ is not a reason.** A markscheme that asks for a point of
> inflexion awards R0 for "because $f''(c)=0$", and awards the mark for
> "because $f''$ changes sign at $c$". The curve $y=x^4$ is the reason why:
> $f''(0)=0$ and the origin is a minimum, not an inflexion.

The three words to have ready: *changes from positive to negative* (maximum),
*from negative to positive* (minimum), *changes sign* (inflexion).
""")

md(r"""
### Task 3 🟢 — *November 2025 TZ1 Paper 1 Q9(b) and (d), 4 marks*

The function $f$ has a derivative given by $f'(x)=3x^2+12x-15$.

The graph of $y=f(x)$ has horizontal tangents at the points where $x=a$ and
$x=b$, with $a<b$; part (a) gives $a=-5$ and $b=1$. The sign of $f'$ in the
three intervals they cut is

$$\begin{array}{ccccc}
+ & \ \ a\ \ & - & \ \ b\ \ & +
\end{array}$$

**(b)** State, with a reason, whether there is a local maximum point or a local
minimum point on the graph of $y=f(x)$ at $x=a$.

The second derivative $f''(x)$ is zero at $x=c$; part (c) gives $c=-2$, and the
sign of $f''$ on either side of it is $-$ then $+$.

**(d)** State, with a reason, whether there is a point of inflexion on the graph
of $y=f(x)$ at $x=c$.

*Enter one word each: `'maximum'`, `'minimum'`, `'inflexion'` or `'neither'`.
Only $f'$ is given, so the cell rebuilds an $f$ from it — the shape does not
depend on the constant.*
""")

code(r"""
q3b = ...        # the kind of point at x = a
q3d = ...        # the kind of point at x = c

slope = 3*x**2 + 12*x - 15
shape = integrate(slope, x)          # any antiderivative: the shape is the same

verify_nature('3(b)', q3b, shape, -5, domain=(-9, 5))
verify_nature('3(d)', q3d, shape, -2, domain=(-9, 5))
""")

# ================================================================= теория 4
md(r"""
## Theory: the second derivative, and where it goes quiet

Take $f(x)=x^4-8x^2$. Then $f'(x)=4x^3-16x=4x(x^2-4)$, flat at $x=0$ and
$x=\pm2$, and $f''(x)=12x^2-16$:

$$f''(0)=-16<0\ \Rightarrow\ \text{maximum},\qquad
f''(\pm2)=32>0\ \Rightarrow\ \text{minimum}$$

Three marks, three substitutions. **Write down the value, not just the sign** —
markschemes for this technique say *the values for the second derivative must be
correct in order to award the R marks*.

**And now the case the test cannot do.** For $g(x)=x^4$ we get $g'(0)=0$ and
$g''(0)=0$. The test is silent, and the answer is still a minimum — $x^4>0$ on
both sides of the origin. For $h(x)=x^5$, again $h'(0)=h''(0)=0$, and this time
the origin is a point of inflexion with zero gradient.

| | $x^4$ | $x^5$ |
|---|---|---|
| $f''(0)$ | $0$ | $0$ |
| left of $0$ | above | below |
| right of $0$ | above | above |
| the origin is | a minimum | an inflexion |

The neighbours separate the two cases; the second derivative does not. That is
why the checks in this notebook walk the curve.
""")

md(r"""
### Task 4 🟢 — *November 2023 TZ2 Paper 1 Q11(a) and (b), 9 marks*

Consider the function

$$f(x)=e^{\cos 2x},\qquad -\frac{\pi}{4}\le x\le\frac{5\pi}{4}$$

**(a)** Find the coordinates of the points on the curve $y=f(x)$ where the
gradient is zero.

**(b)** Using the second derivative at each point found in part (a), show that
the curve $y=f(x)$ has two local maximum points and one local minimum point.

*Exact coordinates in (a) — this is Paper 1. In (b) give the three kinds as a
list, in the same order as the points.*
""")

code(r"""
q4a = [...]      # every point where the gradient is zero
q4b = [...]      # the kind of each, in the same order

f = exp(cos(2*x))
window = (-pi/4, 5*pi/4)

verify_turning('4(a)', q4a, f, domain=window)
verify_nature('4(b)', q4b, f, [0, pi/2, pi], domain=window)
""")

# ================================================================= теория 5
md(r"""
---
# 🟡 Part 2. The range, the bend, and a letter in the function

## Theory: stationary points give the range

The range of $f$ on a closed interval is decided by four numbers at most: the
two ends and the stationary values between them.

For $f(x)=x\sqrt{4-x^2}$ on $-2\le x\le 2$ — a different function from the one
below, and a shorter one —

$$f'(x)=\sqrt{4-x^2}-\frac{x^2}{\sqrt{4-x^2}}=\frac{4-2x^2}{\sqrt{4-x^2}}$$

which is zero when $x=\pm\sqrt2$, and $f(\pm\sqrt2)=\pm2$. At the ends
$f(\pm2)=0$. So the range is $-2\le y\le 2$.

**Three separate marks live here:** the differentiation (product and chain
rules together), the solving, and the substitution back into $f$. Stopping at
$x=\pm\sqrt2$ answers a question nobody asked.

> **A quotient that is zero.** $\dfrac{4-2x^2}{\sqrt{4-x^2}}=0$ needs only the
> numerator to vanish — but the denominator must still be alive there. At
> $x=\pm2$ the fraction is undefined, not zero, and those are ends of the
> domain, not stationary points.
""")

md(r"""
### Task 5 🟡 — *May 2022 TZ2 Paper 1 Q6(b), 6 marks*

A function $f$ is defined by

$$f(x)=x\sqrt{1-x^2},\qquad -1\le x\le 1$$

The range of $f$ is $a\le y\le b$, where $a,b\in\mathbb R$.

Find the value of $a$ and the value of $b$.

*Enter the range itself, as an interval: `Interval(a, b)`. Exact values.*
""")

code(r"""
q5 = ...         # the range, as an interval

f = x*sqrt(1 - x**2)

verify_range('5', q5, f, domain=Interval(-1, 1))
""")

# ================================================================= теория 6
md(r"""
## Theory: the point of inflexion

A point of inflexion is where the curve **changes the side it bends to**. Two
things must both be true, and the second is the one that carries the mark:

$$f''(x)=0\qquad\text{and}\qquad f''\ \text{changes sign there}$$

Take $f(x)=\dfrac{x}{x^2+1}$. A little work gives
$f''(x)=\dfrac{2x(x^2-3)}{(x^2+1)^3}$, which vanishes at $x=0$ and
$x=\pm\sqrt3$ — and at each of the three the sign really does change, so all
three are points of inflexion.

**On a calculator paper there is a shorter route, and the markscheme names it:**
graph $\dfrac{dy}{dx}$ and find *its* maximum or minimum. Where the gradient is
steepest or flattest, the curve is turning over — that is the inflexion, and one
screen gives it.

$$\text{inflexion of } f \iff \text{stationary point of } f' \iff \text{zero of } f''$$

> **A zero of $f''$ need not be an inflexion.** For $f(x)=x^4$, $f''(0)=0$ and
> the curve bends upward on both sides. The sign has to turn over, not merely
> touch zero.
""")

md(r"""
### Task 6 🟡 — *May 2021 TZ1 Paper 2 Q11(c) and May 2023 TZ2 Paper 2 Q12(e), 4 marks*

**(a)** The function $f$ is defined by

$$f(x)=\frac{3x+2}{4x^2-1},\qquad x\ne\pm\tfrac12$$

The graph of $y=f(x)$ has exactly one point of inflexion. Find its
$x$-coordinate.

**(b)** The graph of

$$y=x\sqrt{\frac{9x^4-1}{2}},\qquad \frac{\sqrt3}{3}<x<1$$

has a point of inflexion at the point $P$. By sketching the graph of an
appropriate derivative of $y$, determine the $x$-coordinate of $P$.

*Three significant figures. The $x$-coordinate only — that is all the question
asks for.*
""")

code(r"""
q6a = ...        # the x-coordinate of the point of inflexion
q6b = ...        # the x-coordinate of the inflexion of the second curve

first = (3*x + 2)/(4*x**2 - 1)
second = x*sqrt((9*x**4 - 1)/2)

verify_bend('6(a)', q6a, first, domain=(-4, -0.55))
verify_bend('6(b)', q6b, second, domain=(sqrt(3)/3 + 0.001, 1))
""")

# ================================================================= теория 7
md(r"""
## Theory: the same work with a letter

Nothing changes when a parameter replaces a number — except that the answer is
an expression and the words *show that* appear.

Take $y=x^3+kx$ for $k<0$. Then $\dfrac{dy}{dx}=3x^2+k$, which is zero when
$x=\pm\sqrt{-k/3}$, and substituting back,

$$y=\left(\pm\sqrt{-\tfrac k3}\right)^3+k\left(\pm\sqrt{-\tfrac k3}\right)
=\pm\left(-\tfrac k3\right)^{3/2}\mp k\sqrt{-\tfrac k3}
=\mp\tfrac{2k}{3}\sqrt{-\tfrac k3}$$

**The sign of $k$ is the whole question.** For $k<0$ there are two stationary
points; for $k>0$ the equation $3x^2=-k$ has no real solution and there are
none; for $k=0$ the two merge into one, and it is an inflexion with zero
gradient.

**Classifying a family.** $\dfrac{d^2y}{dx^2}=6x$, so the point at $x=-\sqrt{-k/3}$
has $\frac{d^2y}{dx^2}<0$ and is a maximum, and the one at $+\sqrt{-k/3}$ is a
minimum. Notice what was needed: not the value of $k$, only its sign.

> **"Show that" means arrive at the printed line.** The markscheme gives AG for
> the last step only if it is written out. A correct expression obtained but
> never simplified into the form asked for loses the mark.
""")

md(r"""
### Task 7 🟡 — *November 2023 Paper 3 Q1(e), (f) and (g)(ii), 10 marks*

This question explores the family of curves

$$y=x^3+ax^2+b,\qquad x\in\mathbb R,\ a\ne 0,\ b\in\mathbb R$$

**(e)** Show that the curve has a point of zero gradient at $P(0,b)$ and a point
of zero gradient at $Q\left(-\dfrac{2a}{3},\ \dfrac{4a^3}{27}+b\right)$.

**(f)** Consider the points $P$ and $Q$ for $a>0$ and $b>0$.

&nbsp;&nbsp;**(i)** Determine whether each point is a local maximum or a local minimum.

&nbsp;&nbsp;**(ii)** Determine whether each point is located above or below the $x$-axis.

**(g)** Consider the points $P$ and $Q$ for $a<0$ and $b>0$. State the conditions
on $a$ and $b$ that determine when $Q$ is below the $x$-axis.

*In (e) give both points as a list, in terms of `a` and `b`. In (f) give two
words each, $P$ first. In (g) write the condition as an inequality.*
""")

code(r"""
a, b = symbols('a b')

q7e = [...]      # the two points of zero gradient, in terms of a and b
q7f_i = [...]    # 'maximum' or 'minimum' for the two points, in order
q7f_ii = [...]   # 'above' or 'below' for the two points, in order
q7g = ...        # the condition on a and b for Q to be below the axis

y_curve = x**3 + a*x**2 + b
positive = {a: (3, 1, 2, 6), b: (1, 2, 5, 1)}      # a > 0, b > 0

verify_turning('7(e)', q7e, y_curve, domain=(-8, 4), params=positive)
verify_nature('7(f)(i)', q7f_i, y_curve, [0, -2*a/3], domain=(-8, 4), params=positive)
verify_side('7(f)(ii)', q7f_ii, y_curve, [0, -2*a/3], params=positive)

def below(a, b):
    place = [spot for spot in stationary(x**3 + a*x**2 + b, (-20, 20))
             if abs(spot[0]) > 1e-6]                # this is Q, the one away from 0
    return None if not place else place[0][1] < 0

verify_condition('7(g)', q7g, below, symbols('a b'), window=(-3, -0.25), steps=10)
""")

# ================================================================= теория 8
md(r"""
## Theory: showing a maximum when everything is a letter

Two kinds of question look alike and are not.

**"Determine whether"** wants the sign of $f''$ at the point and a word.

**"Use $f''$ to show that there is a local maximum at $x=m$"** wants the sign
established *for every allowed value of the letters*, and that usually means
simplifying $f''(m)$ until its sign is visible.

Take $V=x(6-2x)(k-2x)$ with $k>3$, so that $V'=12x^2-4(3+k)x+6k$ and
$V''=24x-4(3+k)$. The smaller root of $V'=0$ is

$$x_m=\frac{(3+k)-\sqrt{9-3k+k^2}}{6}$$

and substituting it,

$$V''(x_m)=24\cdot\frac{(3+k)-\sqrt{9-3k+k^2}}{6}-4(3+k)=-4\sqrt{9-3k+k^2}$$

A square root is never negative, so $V''(x_m)<0$ **whatever $k$ is**, and the
point is a maximum. The $(3+k)$ cancelling is the whole trick: what is left
carries its sign on its face.

> **A local maximum is not automatically the largest value.** On a closed
> interval the ends must still be checked. Here $V=0$ at both ends and $V>0$
> inside, so the local maximum is the global one — and that is a separate mark
> in the markscheme.
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ3 Paper 3 Q2(d), 5 marks*

A rectangular sheet of cardboard measures $a$ cm by $b$ cm, where $a<b$. A
square of side $x$ cm is cut from each corner and the sheet is folded into an
open-topped box, so that

$$V=x(a-2x)(b-2x),\qquad 0\le x\le\frac a2$$

Part (c) gives that the only solutions of $\dfrac{dV}{dx}=0$ are

$$x=\frac{(a+b)\pm\sqrt{a^2-ab+b^2}}{6}
\qquad\text{and}\qquad x_m=\frac{(a+b)-\sqrt{a^2-ab+b^2}}{6}$$

is the one inside $0\le x\le\frac a2$.

**(i)** Find an expression for $\dfrac{d^2V}{dx^2}$.

**(ii)** Use it to show that there is a local maximum of $V$ at $x=x_m$.

*In (ii) enter one word.*
""")

code(r"""
a, b = symbols('a b', positive=True)

q8_i = ...       # d²V/dx² in terms of a, b and x
q8_ii = ...      # the kind of point at x_m

V = x*(a - 2*x)*(b - 2*x)
x_m = ((a + b) - sqrt(a**2 - a*b + b**2))/6
sheets = {a: (3, 2, 4, 5), b: (5, 7, 9, 6)}        # a < b, both positive

verify_derivative('8(i)', q8_i, V, order=2)
verify_nature('8(ii)', q8_ii, V, x_m, domain=(0, a/2), params=sheets)
""")

# ================================================================= теория 9
md(r"""
---
# 🔴 Part 3. How many, and where

## Theory: counting the flat places

"For which values of the parameter does the graph have two stationary points?"
is not a question about points at all. It is a question about **how many
solutions $f'(x)=0$ has**, and it is answered by the discriminant.

For $f(x)=x^3+px^2+3x$ we get $f'(x)=3x^2+2px+3$, a quadratic, and

$$\Delta=4p^2-36$$

| $\Delta$ | the equation $f'=0$ | the graph |
|---|---|---|
| $>0$, that is $|p|>3$ | two roots | one maximum and one minimum |
| $=0$, that is $p=\pm3$ | one repeated root | one inflexion with zero gradient |
| $<0$, that is $|p|<3$ | no real roots | no point where the gradient is zero |

Read the middle row carefully. A repeated root of $f'$ means $f'$ **touches**
zero without crossing it, so the gradient keeps its sign on both sides: the
curve flattens for an instant and goes on. That is precisely a point of
inflexion with zero gradient, and it is why the three rows above are the
three answers the exam wants.

> **Write the answer as a set.** *The set of values of $p$* is $|p|>3$, or
> $p<-3$ or $p>3$ — not "$p=4$ works". One example is not a set.
""")

md(r"""
### Task 9 🔴 — *May 2021 TZ1 Paper 3 Q1(c) and (d), 8 marks*

This question explores cubic polynomials of the form $x^3-3cx+d$. Consider

$$f(x)=x^3-3cx+2,\qquad x\in\mathbb R,\ c\in\mathbb R$$

Part (b) gives $f'(x)=3x^2-3c$.

**(c)** Hence, or otherwise, find the set of values of $c$ such that the graph
of $y=f(x)$ has

&nbsp;&nbsp;**(i)** a point of inflexion with zero gradient;

&nbsp;&nbsp;**(ii)** one local maximum point and one local minimum point;

&nbsp;&nbsp;**(iii)** no points where the gradient is equal to zero.

**(d)** Given that the graph of $y=f(x)$ has one local maximum point and one
local minimum point, show that the $y$-coordinate of the local maximum point is
$2c^{3/2}+2$ and that the $y$-coordinate of the local minimum point is
$-2c^{3/2}+2$.

*In (c) enter sets: `FiniteSet(0)`, `Interval.open(0, oo)`, and so on. In (d)
give both points, maximum first, in terms of `c`.*
""")

code(r"""
c = symbols('c')

q9c_i = ...      # the set of c with an inflexion of zero gradient
q9c_ii = ...     # the set of c with one maximum and one minimum
q9c_iii = ...    # the set of c with no point of zero gradient
q9d = [...]      # the local maximum and the local minimum, in terms of c

family = x**3 - 3*c*x + 2

def kinds(value):
    return [word for _, _, word in stationary(family.subs(c, value), (-5, 5))]

verify_param_set('9(c)(i)', q9c_i, lambda v: kinds(v) == ['inflexion'],
                 var=c, window=(-4, 4))
verify_param_set('9(c)(ii)', q9c_ii, lambda v: kinds(v) == ['maximum', 'minimum'],
                 var=c, window=(-4, 4))
verify_param_set('9(c)(iii)', q9c_iii, lambda v: kinds(v) == [],
                 var=c, window=(-4, 4))

verify_turning('9(d)', q9d, x**3 - 3*c*x + 2, domain=(-4, 4),
               params={c: (1, 4, Rational(1, 4), 2)})
""")

# ================================================================ теория 10
md(r"""
## Theory: from the stationary values to the number of roots

A cubic crosses the $x$-axis once, twice or three times, and the stationary
values decide which. Let the maximum value be $M$ and the minimum value be $m$,
with $M>m$:

| | the graph meets the axis |
|---|---|
| $m>0$ or $M<0$ (both vertices on one side) | once |
| $m=0$ or $M=0$ (a vertex sits on the axis) | twice |
| $m<0<M$ (the vertices straddle the axis) | three times |

The middle row is the one to think about. A vertex on the axis is a **repeated
root**: the curve touches there instead of crossing, and touching counts as one
intersection, not two and not none.

**For $y=x^3-3x+k$** the vertices are at $x=\mp1$ with values $k+2$ and $k-2$,
so the three rows read $|k|>2$, $|k|=2$, $|k|<2$.

**And when the vertices themselves move.** If both $c$ and $d$ vary in
$x^3-3cx+d$, the case $c\le0$ has to be handled first and separately: there are
no vertices at all, the curve is increasing throughout, and one crossing is
forced whatever $d$ is. Only for $c>0$ does the comparison above begin.

> **State the case, not only the answer.** Six marks of a Paper 3 went on
> exactly this question, and the markscheme gives at most half of them if
> "$c>0$" is never written down.
""")

md(r"""
### Task 10 🔴 — *May 2021 TZ1 Paper 3 Q1(e) and (f), 12 marks*

Still with $f(x)=x^3-3cx+2$, and with the $y$-coordinates of the vertices found
in task 9.

**(e)** Hence, for $c>0$, find the set of values of $c$ such that the graph of
$y=f(x)$ has

&nbsp;&nbsp;**(i)** exactly one $x$-axis intercept;

&nbsp;&nbsp;**(ii)** exactly two $x$-axis intercepts;

&nbsp;&nbsp;**(iii)** exactly three $x$-axis intercepts.

Now consider $g(x)=x^3-3cx+d$ for $x\in\mathbb R$, where $c,d\in\mathbb R$.

**(f)** Find all conditions on $c$ and $d$ such that the graph of $y=g(x)$ has
exactly one $x$-axis intercept.

*In (f) write one condition joining the cases: `Or(..., ..., ...)`.*
""")

code(r"""
c, d = symbols('c d')

q10e_i = ...     # the set of c with exactly one x-axis intercept
q10e_ii = ...    # the set of c with exactly two
q10e_iii = ...   # the set of c with exactly three
q10f = ...       # all conditions on c and d for exactly one intercept

def meets(value, times):
    if value <= 0:
        return None                      # part (e) speaks only of c > 0
    return crossings(x**3 - 3*value*x + 2, (-30, 30)) == times

verify_param_set('10(e)(i)', q10e_i, lambda v: meets(v, 1), var=c, window=(0, 4))
verify_param_set('10(e)(ii)', q10e_ii, lambda v: meets(v, 2), var=c, window=(0, 4))
verify_param_set('10(e)(iii)', q10e_iii, lambda v: meets(v, 3), var=c, window=(0, 4))

def once(c, d):
    return crossings(x**3 - 3*c*x + d, (-30, 30)) == 1

verify_condition('10(f)', q10f, once, symbols('c d'), window=(-3, 3), steps=12)
""")

# ================================================================ теория 11
md(r"""
## Theory: a curve that is not a function

When the curve is given by an equation in $x$ and $y$, the gradient comes from
implicit differentiation, and everything else is unchanged.

For $x^2+xy+y^2=7$,

$$2x+y+x\frac{dy}{dx}+2y\frac{dy}{dx}=0
\qquad\Longrightarrow\qquad
\frac{dy}{dx}=-\frac{2x+y}{x+2y}$$

**A fraction is zero when its numerator is** — and its denominator is not. So
$y=-2x$, and substituting into the curve, $x^2-2x^2+4x^2=7$, giving
$x=\pm\sqrt{7/3}$ and two stationary points.

**And a fraction is never zero when its numerator cannot be.** That is how
*show that there are no stationary points* is done: set the numerator to zero
and find that no point of the curve satisfies it — either because the equation
has no real solution, or because its solutions are outside the domain the
question states.

> **The domain does the work.** Half the marks of such a question are for
> noticing that the candidate solutions are excluded. "$y=\pm2$, and the
> question says $-2<y<2$, so there are none" is the whole argument, and the
> last clause is the mark.
""")

md(r"""
### Task 11 🔴 — *May 2022 TZ2 Paper 3 Q1(d)(ii) and (e), 8 marks*

Consider the curve $y^2=x^3+x$ for $x\ge 0$. Part (d)(i) gives

$$\frac{dy}{dx}=\pm\frac{3x^2+1}{2\sqrt{x^3+x}},\qquad x>0$$

**(d)(ii)** Hence deduce that the curve $y^2=x^3+x$ has no local minimum or
maximum points.

**(e)** The curve has two points of inflexion which, by symmetry, share an
$x$-coordinate. Find the value of that $x$-coordinate, giving your answer in the
form

$$x=\sqrt{\frac{p\sqrt3+q}{r}},\qquad p,q,r\in\mathbb Z$$

*In (d)(ii) an empty list is the answer: there are no such points. In (e) the
upper branch $y=\sqrt{x^3+x}$ carries the inflexion — give the exact value.*
""")

code(r"""
q11d = [...]     # every local maximum or minimum on the curve
q11e = ...       # the x-coordinate of the points of inflexion

shape = curve(Eq(y**2, x**3 + x))
branch = sqrt(x**3 + x)                  # the upper half, where the question looks

verify_turning('11(d)(ii)', q11d, shape, domain=(0.01, 4))
verify_bend('11(e)', q11e, branch, domain=(0.01, 2))
""")

# ================================================================ теория 12
md(r"""
## Theory: an argument that runs on parity alone

The hardest questions of this topic never evaluate anything. They establish the
**sign** of the gradient on either side of a point and read off the kind.

Suppose $g_n'(x)=n\,x^{\,n-1}\left(b^2+x^2\right)$ with $b>0$ and $n>1$, and
suppose it is already known that $g_n'(1)>0$ and that $g_n'(0)=0$. What happens
at the origin depends on $g_n'(-1)$:

$$g_n'(-1)=n(-1)^{\,n-1}\left(b^2+1\right)$$

The factor $b^2+1$ is positive, so the sign is the sign of $(-1)^{n-1}$:

* **$n$ even** $\Rightarrow n-1$ odd $\Rightarrow (-1)^{n-1}=-1$, so
  $g_n'(-1)<0$. The gradient is negative to the left of the origin and positive
  to the right: the curve falls, flattens, rises — a **local minimum**.
* **$n$ odd** $\Rightarrow n-1$ even $\Rightarrow (-1)^{n-1}=+1$, so
  $g_n'(-1)>0$. The gradient is positive on both sides and zero at the origin:
  the curve flattens and goes on — an **inflexion with zero gradient**.

Nothing was computed. The second derivative was never written, and for a good
reason: at the origin it is zero for every $n>2$, and the test would have said
nothing either way.

> **One $x$ on each side is enough**, provided there is no other stationary
> point in between — and that is what a given value such as $g_n'(1)>0$ is for.
> It fixes the sign on the whole stretch to the right of the origin.
""")

md(r"""
### Task 12 🔴 — *May 2021 TZ2 Paper 3 Q1(g), 5 marks*

This question explores the family

$$f_n(x)=x^n(a-x)^n,\qquad a\in\mathbb Z^+,\ n\in\mathbb Z^+,\ n>1$$

Earlier parts give $f_n'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}$, the three solutions of
$f_n'(x)=0$, and the fact that $f_n'\!\left(\frac a4\right)>0$.

By using that fact and considering the sign of $f_n'(-1)$, show that the point
$(0,0)$ on the graph of $y=f_n(x)$ is

**(i)** a local minimum point for even values of $n$, where $n>1$;

**(ii)** a point of inflexion with zero gradient for odd values of $n$, where
$n>1$.

*One word each. The check runs the claim over several even and several odd $n$
and over several values of $a$: a statement about a family has to hold for the
family.*
""")

code(r"""
n, a = symbols('n a', positive=True)

q12_i = ...      # the kind of point at the origin for even n
q12_ii = ...     # the kind of point at the origin for odd n

f_n = x**n*(a - x)**n

verify_nature('12(i)', q12_i, f_n, 0, domain=(-1, a + 1),
              params={n: (2, 4, 2, 4), a: (2, 2, 3, 5)})
verify_nature('12(ii)', q12_ii, f_n, 0, domain=(-1, a + 1),
              params={n: (3, 5, 3, 5), a: (2, 2, 3, 5)})
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would make
first**.

| code | technique |
| --- | --- |
| `find` | find the stationary point, both coordinates |
| `classify` | name its kind from the second derivative |
| `sign` | name its kind from the sign of the first derivative |
| `inflexion` | find where the concavity changes |
| `family` | the same work with a letter in the function |
| `side` | is the point above or below the $x$-axis |
| `count` | for which values of the parameter are there that many |
| `none` | show that no such point exists |

1. Find the coordinates of the local minimum of $y=x^3-3x$.
2. Given $f''(2)=-5$ and $f'(2)=0$, what kind of point is at $x=2$?
3. $f'$ changes from negative to positive at $x=4$. What kind of point is there?
4. Find the $x$-coordinate of the point of inflexion of $y=xe^{-x}$.
5. Show that $y=x^3+kx^2$ has a stationary point at $x=-\frac{2k}{3}$.
6. The local minimum of a cubic has $y=-7$. State whether it lies above or below the axis.
7. Find the values of $m$ for which $y=x^3+mx$ has no stationary point.
8. Show that $y=\dfrac{1}{x}$ has no local maximum or minimum for $x>0$.
9. Find every point where the gradient of $y=\sin x+\cos x$ is zero on $[0,2\pi]$.
10. Where does $y=x^4-6x^2$ change from concave down to concave up?
11. $\dfrac{d^2y}{dx^2}=6x+4$ at a stationary point $x=1$. Maximum or minimum?
12. For which $p$ does $y=x^4+px^2$ have exactly three stationary points?
""")

code("""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + """)
""")

# =================================================================== таймер
md(r"""
---
## On the clock — *November 2022 Paper 1 Q7, 7 marks*

**Seven marks, ten minutes.** No calculator, no hints.

Consider the curve with equation

$$(x^2+y^2)y^2=4x^2,\qquad x\ge 0,\ -2<y<2$$

Show that the curve has no local maximum or local minimum points for $x>0$.

*The answer is the list of such points, and it is empty. Write out the
implicit differentiation on paper first — that is where six of the seven marks
are.*

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt = [...]       # every local maximum or minimum with x > 0

shape = curve(Eq((x**2 + y**2)*y**2, 4*x**2))

verify_turning('timer', qt, shape, domain=(0.01, 8))
""")

# ================================================================== решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1** $f'(x)=4x^2-16$, which is zero at $x=\pm2$; the question wants $p>0$, so
$p=2$. Then

$$q=f(2)=\frac{4\cdot8}{3}-32=\frac{32}{3}-32=\boxed{-\frac{64}{3}}$$

$f''(x)=8x$ and $f''(2)=16>0$, so it really is the minimum.

---

**2 (a)** The calculator gives the local maximum of $\ln(xe^x+1)-x^4$ on
$[0,2]$ at $\boxed{(0.709,\ 0.640)}$ $(0.708519\ldots,\ 0.639580\ldots)$.

**2 (b)** The curve $y=\dfrac{x(x^2-16)}{x^2+16}$ has
$\boxed{(-1.94,\ 1.20)}$ as its local maximum and $\boxed{(1.94,\ -1.20)}$ as
its local minimum $(\pm1.94347\ldots,\ \mp1.20113\ldots)$.

Note the shape: the maximum is the *left* one, because the curve comes up from
below on the far left.

---

**3 (b)** $f'$ changes from positive to negative at $x=a$, so the curve rises
and then falls: $\boxed{\text{a local maximum}}$. (Equivalently
$f''(-5)=6(-5)+12=-18<0$.)

**3 (d)** $f''$ changes sign at $x=c$, so the concavity changes:
$\boxed{\text{yes, a point of inflexion}}$. Saying only "$f''(c)=0$" earns R0 —
that is true at $x=0$ for $y=x^4$ as well, and there the origin is a minimum.

---

**4 (a)** $f'(x)=-2\sin 2x\,e^{\cos 2x}$, which is zero when $\sin 2x=0$, that
is $2x=0,\pi,2\pi$ and $x=0,\frac\pi2,\pi$ inside $-\frac\pi4\le x\le\frac{5\pi}4$:

$$\boxed{(0,e)},\qquad\boxed{\left(\tfrac\pi2,\tfrac1e\right)},\qquad\boxed{(\pi,e)}$$

**4 (b)** $f''(x)=\left(4\sin^2 2x-4\cos 2x\right)e^{\cos 2x}$, so

$$f''(0)=-4e<0,\qquad f''\!\left(\tfrac\pi2\right)=\tfrac4e>0,\qquad f''(\pi)=-4e<0$$

that is $\boxed{\text{maximum, minimum, maximum}}$.

---

**5** With the product and chain rules,

$$f'(x)=\sqrt{1-x^2}-\frac{x^2}{\sqrt{1-x^2}}=\frac{1-2x^2}{\sqrt{1-x^2}}$$

which vanishes at $x=\pm\frac{1}{\sqrt2}$, where
$f\left(\pm\frac1{\sqrt2}\right)=\pm\frac1{\sqrt2}\cdot\frac1{\sqrt2}=\pm\frac12$.
At the ends $f(\pm1)=0$, so

$$a=-\tfrac12,\qquad b=\tfrac12,\qquad\boxed{-\tfrac12\le y\le\tfrac12}$$

---

**6 (a)** Graphing $f'$ and finding its local minimum (or solving $f''=0$) gives
$\boxed{x=-1.60}$ $(-1.59537\ldots)$.

**6 (b)** Graphing $\dfrac{d^2y}{dx^2}$ and reading off its zero gives
$\boxed{x=0.656}$ $(0.655996\ldots)$.

---

**7 (e)** $\dfrac{dy}{dx}=3x^2+2ax=x(3x+2a)$, zero at $x=0$ and $x=-\frac{2a}3$.
At $x=0$, $y=b$, so $P(0,b)$. At $x=-\frac{2a}3$,

$$y=-\frac{8a^3}{27}+a\cdot\frac{4a^2}{9}+b=-\frac{8a^3}{27}+\frac{12a^3}{27}+b
=\boxed{\frac{4a^3}{27}+b}$$

**7 (f)(i)** $\dfrac{d^2y}{dx^2}=6x+2a$. At $x=0$ it is $2a>0$, so $P$ is a
$\boxed{\text{minimum}}$; at $x=-\frac{2a}3$ it is $-4a+2a=-2a<0$, so $Q$ is a
$\boxed{\text{maximum}}$.

**7 (f)(ii)** $b>0$ puts $P$ $\boxed{\text{above}}$ the axis, and
$\frac{4a^3}{27}+b>0$ puts $Q$ $\boxed{\text{above}}$ it too.

**7 (g)** $Q$ is below the axis exactly when its $y$-coordinate is negative:

$$\boxed{\frac{4a^3}{27}+b<0}$$

---

**8 (i)** $V=4x^3-2(a+b)x^2+abx$, so $\dfrac{dV}{dx}=12x^2-4(a+b)x+ab$ and

$$\boxed{\frac{d^2V}{dx^2}=24x-4(a+b)}$$

**8 (ii)** Substituting $x_m$,

$$\frac{d^2V}{dx^2}\bigg|_{x_m}=24\cdot\frac{(a+b)-\sqrt{a^2-ab+b^2}}{6}-4(a+b)
=-4\sqrt{a^2-ab+b^2}<0$$

so $x_m$ gives a $\boxed{\text{local maximum}}$. The $(a+b)$ cancels and what is
left is negative for every $a$ and $b$.

---

**9 (c)** $f'(x)=3x^2-3c=0$ means $x^2=c$.

* One repeated root, and the gradient touches zero without crossing:
  $\boxed{c=0}$.
* Two distinct roots: $\boxed{c>0}$.
* No real roots: $\boxed{c<0}$.

**9 (d)** $x=\pm\sqrt c$, and the maximum is the left one:

$$f(-\sqrt c)=-c^{3/2}+3c^{3/2}+2=\boxed{2c^{3/2}+2}$$
$$f(\sqrt c)=c^{3/2}-3c^{3/2}+2=\boxed{-2c^{3/2}+2}$$

---

**10 (e)** The minimum value is $-2c^{3/2}+2$ and the maximum value
$2c^{3/2}+2>0$ always, so everything hangs on the minimum.

* One intercept — the minimum is above the axis: $-2c^{3/2}+2>0$, that is
  $c^{3/2}<1$ and $\boxed{0<c<1}$.
* Two intercepts — the minimum sits on the axis: $\boxed{c=1}$.
* Three intercepts — the minimum is below the axis: $\boxed{c>1}$.

**10 (f)** Two cases.

*Case $c\le0$.* Then $g'(x)=3x^2-3c\ge0$ for every $x$, so $g$ never turns and
crosses the axis exactly once — for any $d$ at all.

*Case $c>0$.* The vertices are $\left(-\sqrt c,\ 2c^{3/2}+d\right)$ and
$\left(\sqrt c,\ -2c^{3/2}+d\right)$, and one intercept means they lie on the
same side of the axis:

$$-2c^{3/2}+d>0\quad\text{or}\quad 2c^{3/2}+d<0$$

$$\boxed{c\le0,\quad\text{or}\quad d>2c^{3/2},\quad\text{or}\quad d<-2c^{3/2}}$$

---

**11 (d)(ii)** A quotient is zero only when its numerator is, and
$3x^2+1\ge1>0$ for every real $x$. So $\dfrac{dy}{dx}$ is never zero and there
are $\boxed{\text{no local maxima or minima}}$.

**11 (e)** Differentiating $2y\dfrac{dy}{dx}=3x^2+1$ again,

$$2\left(\frac{dy}{dx}\right)^2+2y\frac{d^2y}{dx^2}=6x$$

At an inflexion $\dfrac{d^2y}{dx^2}=0$, so $\left(\dfrac{dy}{dx}\right)^2=3x$,
that is

$$\frac{(3x^2+1)^2}{4(x^3+x)}=3x
\quad\Longrightarrow\quad 12x^2+12x^4=9x^4+6x^2+1
\quad\Longrightarrow\quad 3x^4+6x^2-1=0$$

A quadratic in $x^2$: $x^2=\dfrac{-6+\sqrt{48}}{6}=\dfrac{2\sqrt3-3}{3}$, and
since $x>0$,

$$x=\boxed{\sqrt{\frac{2\sqrt3-3}{3}}}\approx0.393$$

so $p=2$, $q=-3$, $r=3$.

---

**12 (i)** $f_n'(-1)=n(-1)^{n-1}(a+2)(a+1)^{n-1}$. For even $n$ the exponent
$n-1$ is odd, so $(-1)^{n-1}=-1$ and $f_n'(-1)<0$; with $f_n'(0)=0$ and
$f_n'\!\left(\frac a4\right)>0$ the gradient runs $-,0,+$ across the origin, so
$(0,0)$ is a $\boxed{\text{local minimum}}$.

**12 (ii)** For odd $n$ the exponent $n-1$ is even, so $(-1)^{n-1}=+1$ and
$f_n'(-1)>0$; the gradient runs $+,0,+$ and the curve flattens without turning:
$(0,0)$ is a $\boxed{\text{point of inflexion with zero gradient}}$.

The second derivative is useless here — at the origin it vanishes for every
$n>2$, whatever the parity.

---

## Timer

Differentiating $(x^2+y^2)y^2=4x^2$ implicitly, that is
$x^2y^2+y^4=4x^2$,

$$2xy^2+2x^2y\frac{dy}{dx}+4y^3\frac{dy}{dx}=8x$$

At a local maximum or minimum $\dfrac{dy}{dx}=0$, so $2xy^2=8x$ and

$$x=0\quad\text{or}\quad y^2=4$$

The question says $x>0$ and $-2<y<2$, so $x=0$ is excluded and $y=\pm2$ is
excluded. No candidate survives, and the curve has
$\boxed{\text{no local maximum or minimum points}}$ for $x>0$.
""")


def build():
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
    os.makedirs(os.path.dirname(NOTEBOOK), exist_ok=True)
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    n_code = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f"{NOTEBOOK}: {len(cells)} ячеек, из них {n_code} с кодом, "
          f"эталонов {len(ANSWERS)}")


if __name__ == '__main__':
    build()
