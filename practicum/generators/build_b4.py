"""Собирает практикум B4 (исследование функции, асимптоты, эскиз) в .ipynb.

Третий практикум серии на английском: ноутбук целиком английский, kit
переключается вызовом language('en') в установочной ячейке. Документация
репозитория (карта, PRACTICUM.md, этот заголовок) остаётся русской.

Тема даёт восьмое понятие равенства ответов: ответ здесь — прямая, и верна
она не тогда, когда совпала с эталоном, а тогда, когда кривая к ней
приближается. Отсюда verify_asymptotes, считающий предел. Рядом стоит
verify_range: он ничего не решает за ученика, а спрашивает у самой функции,
достигается ли значение, и отдельно проверяет каждый конец — там, где
стоит разница между ≤ и <, стоит и балл.

Эскизы проверяет verify_sketch из B3. Того, чего он не видит — формы кривой
между особенностями, — здесь больше, чем в B3: приём 7 целиком про форму.
Поэтому приём 7 проверяется через вторую производную, а каждое задание на
эскиз печатает рядом настоящий график.
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
x, y = sp.symbols('x y')
A_ = sp.Symbol('A', positive=True)


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_b4.py ---
D_2A = dn(-1)                                    # ноль функции (7x+7)/(2x-4)
D_5D = dn(R(4, 5))                               # y-пересечение ноября 2021
D_21A = de(-4 * sp.E)                            # f''(0) у e^(cos 2x)
D_21B = de(4 / sp.E)                             # f''(pi/2)
D_21C = de(sp.E**2)                              # во сколько раз максимум острее
D_22A = dn(0)                                    # наклон верхней ветви y^2=x^3 в нуле
D_22B = de(sp.oo)                                # и у y^2=x^3+1 в её нуле
D_22C = dset([-1, 1])                            # y-пересечения y^2=x^3+1
D_22D = dset([2])                                # x-пересечение y^2=16-8x
D_22E = dset([-1])                               # x-пересечение y^2=4+4x
D_23D = dn(1)                                    # сколько точек нулевого наклона выше оси

TRIGGER = {1: 'oblique', 2: 'range', 3: 'implicit', 4: 'asym', 5: 'count',
           6: 'bend', 7: 'rational', 8: 'sketch', 9: 'limit', 10: 'range',
           11: 'asym', 12: 'implicit', 13: 'sketch', 14: 'count', 15: 'rational'}
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
# Practicum B4: curve sketching and asymptotes

**147 marks, 62 blocks, nine techniques.** Every question in this topic
is answered by the same short list — where the curve meets the axes,
where it turns, and what it runs alongside far away — and the whole
difficulty is that the exam asks for that list in four voices that do
not look related.

**Material.** The whole of `functions.curve_sketching` and the whole of
`functions.asymptotes` from the AA HL archive, sessions May 2021 —
November 2025. Both topics entire, because the archive keeps putting
them in one question: November 2021 Paper 2 Q10 asks for the intercepts,
then the vertical asymptote, then the oblique asymptote, then the
sketch, in that order, for 11 of its 18 marks.

Twenty of the 147 marks are one question counted twice — the November
2023 session sits in the corpus as two zones and the papers are the same
paper — so the real material is about 127 marks. Every task below is a
real past-paper question, with the source given.

**This practicum is in English,** like B2 and B3. The checks speak
whichever language the notebook asks them to, and this one asks for
English in the setup cell.

**The four voices.**

> *"Write down the equation of the horizontal asymptote."* — one line,
> one mark.
>
> *"Sketch the graph of $f$ for $-50\le x\le 50$."* — the same list,
> drawn.
>
> *"Find the range of $f$."* — the same list, read off the vertical axis
> instead of the horizontal one.
>
> *"Find the set of values of $b$ for which the curve has exactly three
> $x$-axis intercepts."* — the same list with a letter in it, and what
> happens to the count as the letter moves.

**Where this sits next to B3.** B3 draws curves whose shape you are
expected to know — a parabola, $\arccos$, a rectangular hyperbola — so
the examiner can ask for them with no machine on the desk, and 64 of
B3's 107 marks are on Paper 1. Here nobody has drawn the curve for you,
and 73% of the marks carry a calculator. Same-looking topics, opposite
papers, and the reason is the seam between them.

**How the checks work here.** Two of them are new.

* `verify_asymptotes` takes the line you claim and computes the limit.
  A vertical asymptote is right when a one-sided limit is infinite; a
  horizontal one when the limit at infinity is your number; an oblique
  one when $f(x)-(ax+b)\to 0$. Nothing is compared with a stored answer,
  and **a number is not accepted where a line was asked for** — the
  markscheme says *"must be written as an equation with $y=$"*.
* `verify_range` asks the function itself. Inside your set every value
  must be attained; outside, none. Each endpoint is tested on its own,
  because that is where $\le$ and $<$ part company and where the mark
  is.

`verify_sketch` from B3 does the sketches, and it still does not look at
the curve *between* the features. That bites harder here — one whole
technique is about the shape between them — so every sketch task prints
the true curve beside your answer, and technique 7 is checked through
the second derivative instead of the picture.

**How to work**

1. Read the map of techniques first. It is arranged by **where the list
   of features comes from**.
2. Work **on paper**, axes drawn, before typing anything.
3. Exact answers where the paper is Paper 1: `Rational(13, 4)`,
   `sqrt(13)`, `pi/2`. Three significant figures where the paper is
   Paper 2 or 3 — that is what the exam accepts and what the checks
   compare.
4. An asymptote is entered as an equation: `Eq(x, 3)`,
   `Eq(y, x/2 - Rational(17, 2))`.
5. A range is entered as a set or an inequality: `(y >= -5)`,
   `Interval.Lopen(Rational(-3, 2), 2)`, `Union(...)`.
6. The last two blocks are a recognition trainer and one question on a
   timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Union, solveset, lambdify

import matplotlib.pyplot as plt
import numpy as np

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d, m = symbols('a b c d m')
n, p, q, r, s = symbols('n p q r s')
poly = Symbol('poly')


# Draw the true curve so you can compare your sketch with it. Pass
# expressions, or (expression, label) pairs; `lines` takes asymptotes as
# ('v', 3) or ('h', -2) or ('o', x/2 - 1); `marks` takes points to dot.
def show(*curves, span=(-6, 6), ylim=None, size=(7, 4), marks=(), lines=()):
    grid = np.linspace(float(span[0]), float(span[1]), 2000)
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
    for kind, where in lines:
        if kind == 'v':
            ax.axvline(float(where), color='0.55', ls='--', lw=1)
        elif kind == 'h':
            ax.axhline(float(where), color='0.55', ls='--', lw=1)
        else:
            g = lambdify(x, where, 'math')
            ax.plot(grid, [g(float(u)) for u in grid], color='0.55', ls='--', lw=1)
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
print('an asymptote:        ', Eq(y, x/2 - Rational(17, 2)))
print('a range:             ', Interval.Lopen(Rational(-3, 2), 2))
print('a sketch as features:', {'x_intercepts': [2, 12], 'minima': [(5.66, -1.34)]})
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Read the asymptotes off | «write down the equation of the vertical asymptote» | set the denominator to zero |
| 2 | Asymptote by limit | «by considering limits, show that …» | ask which limit, and where the domain stops |
| 3 | Oblique asymptote | «$y=ax+b$; find $a$ and $b$» | divide, or equate coefficients |
| 4 | Sketch a rational curve | «sketch $f$ for $-50\le x\le 50$, showing the asymptotes» | draw the asymptotes first, dashed |
| 5 | Find the range | «determine the range of $g$» | list the turning points and the horizontal asymptote |
| 6 | Sketch and label | «sketch $f$ for $-4\le x\le 3$, showing the roots and the local minimum» | write down the list of labels before drawing |
| 7 | Sketch from $f''$ | «taking into consideration the relative values of the second derivative» | compare the sizes, not just the signs |
| 8 | Sketch $y^2=f(x)$ | «sketch $y^2=x^3+1$, indicating any intersections with the axes» | the $x$-axis is a line of symmetry |
| 9 | Count the intercepts | «find the set of values of $b$ such that there are exactly three» | evaluate the curve at its stationary points |

**The ladder goes by where the list comes from.**

**Rungs 1–3 — the asymptotes on their own.** First the two you read off a
rational function without doing anything: the denominator's zero, and
the ratio of the leading coefficients. Then the ones you cannot read
off, where the answer *is* a limit — a logarithm's vertical asymptote is
the edge of its domain, and $\arcsin\frac{x^2-1}{x^2+1}$ has a
horizontal asymptote at $\tfrac{\pi}{2}$ that no ratio will give you.
Then the oblique asymptote, which is the same limit written as a
division.

**Rung 4 — the sketch of a rational curve.** Asymptotes first, then the
intercepts, then the branches. This is not advice: it is the order the
markscheme pays for, in separate marks.

**Rung 5 — the range.** The same picture read sideways. One symbol
carries the mark: a turning point is *attained* and gets $\le$, a
horizontal asymptote is not and gets $<$.

**Rungs 6–8 — curves that are not rational.** From a formula with a
calculator, labelling what you were told to label; from a second
derivative, when the question hands you the concavity and wants it
visible; and from $y^2=f(x)$, which is not a function at all and where
the symmetry does the work.

**Rung 9 — the family.** A letter in the formula and a count in the
question. The count changes exactly when a turning point crosses the
axis, which is why this comes last: it needs the whole list and one idea
more.

**What saves the most time.** Every sketch instruction in the archive
names its own markscheme. *"Stating the values of any axes
intercepts"*, *"clearly indicating any asymptotes"*, *"labelling the
coordinates of any local maximum and minimum points"*. Write that list
down before you draw anything — the marks are for the list, and the
curve joining it is usually one A1 for shape.
""")


md(r"""
---
# Part I — the asymptotes

---
## Theory 1. Three kinds of line, and one definition

An asymptote is a line the curve gets arbitrarily close to. That is the
whole definition, and every method below is a way of computing it.

**Vertical, $x=c$.** The curve runs off to $\pm\infty$ as $x\to c$ from
one side or the other. For a rational function these are the zeros of
the denominator — *after cancelling*, because a factor common to both
gives a hole, not an asymptote. For anything else they sit where the
domain stops: $\ln x$ has $x=0$, and so does $2\ln x-\ln d$ for every
value of $d$.

**Horizontal, $y=h$.** $f(x)\to h$ as $x\to+\infty$ or as
$x\to-\infty$. One side is enough — $e^x$ has $y=0$ on the left and
nothing on the right. For a rational function compare degrees:

| degrees | horizontal asymptote |
| --- | --- |
| bottom heavier | $y=0$ |
| equal | $y=\dfrac{\text{leading top}}{\text{leading bottom}}$ |
| top heavier by 1 | none — see the oblique one |
| top heavier by 2 or more | none at all |

**Oblique, $y=ax+b$.** Only when the numerator's degree is exactly one
more than the denominator's. Three routes, and the markscheme prints all
of them:

$$\frac{x^2-x-12}{2x-15} = \underbrace{\tfrac{x}{2}+\tfrac{13}{4}}_{\text{quotient}} + \underbrace{\frac{147/4}{2x-15}}_{\to\,0}$$

* **divide** — long division, and the quotient is the answer;
* **equate coefficients** — write $x^2-x-12\equiv(ax+b)(2x-15)+c$ and
  match;
* **take limits** — $a=\lim\frac{f(x)}{x}$, then
  $b=\lim\bigl(f(x)-ax\bigr)$.

**Two marks that get thrown away.** The answer must be an *equation*:
*"Do not award the final A1 if the answer is not given as an equation"*
(May 2021 TZ1). And the division must be finished: four marks are split
$a$, method, $b$, answer, and stopping at the leading term collects one
of them.

**How to check yourself.** Subtract your line from the function and let
$x$ grow. If the difference does not go to zero, the line is wrong —
which is precisely what `verify_asymptotes` does below.
""")

md(r"""
## Task 1 🟢 — the two you read off

The function $f$ is defined by $f(x)=\dfrac{2x+4}{3-x}$, for
$x\in\mathbb{R}$, $x\ne 3$.

**(a)** Write down the equation of the vertical asymptote and the
equation of the horizontal asymptote of the graph of $f$.

**(b)** Find the coordinates where the graph of $f$ crosses the $x$-axis
and the $y$-axis.

*Source: November 2021, Paper 1, Q2(a)(b) (2 + 2 marks, no calculator).*
""")

code(r"""
my1a = [...]                       # the two asymptotes, as equations
my1b = {
    'x_intercepts': [...],
    'y_intercept':  ...,
}

f1 = (2*x + 4)/(3 - x)
verify_asymptotes('Task 1(a)', my1a, f1)
verify_sketch('Task 1(b)', my1b, f1)

show(f1, span=(-6, 10), ylim=(-12, 8), lines=[('v', 3), ('h', -2)], size=(6, 3.5))
""")

md(r"""
## Task 2 🟢 — three quick reads

**(a)** The function $f$ is defined by $f(x)=\dfrac{7x+7}{2x-4}$ for
$x\in\mathbb{R}$, $x\ne 2$. Find the zero of $f(x)$, and write down the
equations of the vertical and the horizontal asymptote.

**(b)** The function $g$ is defined by $g(x)=\dfrac{3x-2}{2x+1}$ for
$x\ne-\tfrac12$. Write down the equation of the horizontal asymptote.

**(c)** The function $h$ is defined by $h(x)=\dfrac{2x+6}{3x+6}$ for
$x\ne-2$. Write down the equation of the horizontal asymptote.

*Sources: May 2023 TZ1, Paper 1, Q1(a)(b) (2 + 2 marks); May 2025 TZ2,
Paper 1, Q1(b) (1 mark); May 2024 TZ2, Paper 1, Q5(a) (1 mark). All
without a calculator.*
""")

code(r"""
my2zero = ...                      # the zero of f
my2a = [...]                       # both asymptotes of f
my2b = ...                         # the horizontal asymptote of g
my2c = ...                         # the horizontal asymptote of h

check_num('Task 2(a) zero', my2zero, 6, '""" + D_2A + r"""')
verify_asymptotes('Task 2(a)', my2a, (7*x + 7)/(2*x - 4))
verify_asymptotes('Task 2(b)', my2b, (3*x - 2)/(2*x + 1), kinds=('horizontal',))
verify_asymptotes('Task 2(c)', my2c, (2*x + 6)/(3*x + 6), kinds=('horizontal',))
""")

md(r"""
## Task 3 🟢 — a vertical asymptote with no denominator

The function $g$ is defined by $g(x)=2\ln x-\ln d$, where $x>0$ and
$d\in\mathbb{Z}^{+}$.

State the equation of the vertical asymptote to the graph of $y=g(x)$.

*Source: November 2023, Paper 1, Q10(a) (1 mark, no calculator). The
same question appears in the corpus twice, once for each zone.*
""")

code(r"""
my3 = ...                          # the vertical asymptote

verify_asymptotes('Task 3', my3, 2*log(x) - log(7),
                  domain=Interval.open(0, oo), kinds=('vertical',))

# The answer does not depend on d. Check that it does not:
for dv in (1, 7, 100):
    print(f'd = {dv:>3}:  g(0.001) = {float((2*log(x) - log(dv)).subs(x, 0.001)):.3f}')
""")

md(r"""
## Task 4 🟡 — an asymptote that only a limit will give

A function $f$ is defined by
$f(x)=\arcsin\!\left(\dfrac{x^{2}-1}{x^{2}+1}\right)$, $x\in\mathbb{R}$.

By considering limits, show that the graph of $y=f(x)$ has a horizontal
asymptote, and state its equation.

*Source: May 2021 TZ2, Paper 2, Q12(b) (2 marks).*
""")

code(r"""
my4 = ...                          # the horizontal asymptote

f4 = asin((x**2 - 1)/(x**2 + 1))
verify_asymptotes('Task 4', my4, f4, kinds=('horizontal',))

# The two steps of the argument, printed:
print('inside  ->', limit((x**2 - 1)/(x**2 + 1), x, oo))
print('outside ->', limit(f4, x, oo))
show(f4, span=(-12, 12), ylim=(-2, 2), lines=[('h', pi/2)], size=(6, 3))
""")

md(r"""
## Task 5 🟡 — intercepts, vertical, oblique

Consider the function $f(x)=\dfrac{x^{2}-x-12}{2x-15}$, $x\in\mathbb{R}$,
$x\ne\tfrac{15}{2}$.

**(a)** Find the coordinates where the graph of $f$ crosses the $x$-axis
and the $y$-axis.

**(b)** Write down the equation of the vertical asymptote.

**(c)** The oblique asymptote can be written as $y=ax+b$ where
$a,b\in\mathbb{Q}$. Find $a$ and $b$.

*Source: November 2021, Paper 2, Q10(a)(b)(c) (3 + 1 + 4 marks).*
""")

code(r"""
my5a = {
    'x_intercepts': [...],
    'y_intercept':  ...,
}
my5b = ...                         # the vertical asymptote
my5c = ...                         # the oblique asymptote, as an equation

f5 = (x**2 - x - 12)/(2*x - 15)
verify_sketch('Task 5(a)', my5a, f5)
verify_asymptotes('Task 5(b)', my5b, f5, kinds=('vertical',))
verify_asymptotes('Task 5(c)', my5c, f5, kinds=('oblique',))

# The division that produces the answer:
print(apart(f5, x))
""")

md(r"""
## Task 6 🔴 — all the asymptotes at once

The function $g$ is defined by $g(x)=\dfrac{4x^{2}-1}{3x+2}$, for
$x\in\mathbb{R}$, $x\ne-\tfrac23$.

Find the equations of **all** the asymptotes on the graph of $y=g(x)$.

*Source: May 2021 TZ1, Paper 2, Q11(e) (4 marks). The markscheme notes:
"Do not award the final A1 if the answer is not given as an equation".*
""")

code(r"""
my6 = [...]                        # every asymptote, each one an equation

g6 = (4*x**2 - 1)/(3*x + 2)
verify_asymptotes('Task 6', my6, g6)

show(g6, span=(-8, 6), ylim=(-20, 12),
     lines=[('v', -Rational(2, 3)), ('o', 4*x/3 - Rational(8, 9))], size=(6, 3.5))
""")

md(r"""
## Task 7 🟡 — the same three, on a harder fraction

Consider the function defined by $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, where
$x\in\mathbb{R}$, $x\ne-3$.

**(a)** State the equation of the vertical asymptote on the graph of $f$.

**(b)** Find the coordinates of the points where the graph of $f$ crosses
the $x$-axis.

**(c)** The graph of $f$ also has an oblique asymptote of the form
$y=ax+b$, where $a,b\in\mathbb{Q}$. Find the value of $a$ and the value
of $b$.

*Source: November 2023, Paper 2, Q11(a)(b)(c) (1 + 2 + 4 marks). This
function comes back in tasks 12 and 14.*
""")

code(r"""
my7a = ...                         # the vertical asymptote
my7b = [...]                       # the x-intercepts
my7c = ...                         # the oblique asymptote

f7 = (x**2 - 14*x + 24)/(2*x + 6)
verify_asymptotes('Task 7(a)', my7a, f7, kinds=('vertical',))
verify_sketch('Task 7(b)', {'x_intercepts': my7b}, f7)
verify_asymptotes('Task 7(c)', my7c, f7, kinds=('oblique',))
""")

md(r"""
## Task 8 🟡 — an asymptote for a whole family

Consider the curve $y=\dfrac{x\left(x^{2}-A\right)}{x^{2}+A}$, where $A$
is a positive real parameter.

Determine the equation of the oblique asymptote to the curve.

*Source: May 2025 TZ2, Paper 3, Q1(d)(ii) (1 mark). The investigation
begins with $A=16$, which is task 12(b).*
""")

code(r"""
my8 = ...                          # the oblique asymptote — one line for every A

A = Symbol('A', positive=True)
f8 = x*(x**2 - A)/(x**2 + A)
verify_asymptotes('Task 8', my8, f8, kinds=('oblique',))

# Why it does not depend on A:
print(apart(f8.subs(A, 16), x))
show((f8.subs(A, 1), 'A = 1'), (f8.subs(A, 16), 'A = 16'), (x, 'y = x'),
     span=(-12, 12), ylim=(-14, 14), size=(6, 3.5))
""")


md(r"""
---
# Part II — the picture, and the picture read sideways

---
## Theory 2. Sketching a rational curve, in the order the marks come

The markscheme for these questions is remarkably consistent. November
2023 Paper 2 Q11(d), four marks:

> *two branches with approximately correct shape* · *their vertical and
> oblique asymptotes in approximately correct positions with both
> branches showing correct asymptotic behaviour* (two marks) · *their
> axes intercepts in approximately the correct positions*

So the order is forced:

1. **Asymptotes**, dashed, labelled with their equations. They cut the
   plane into regions, and each region holds exactly one branch.
2. **Intercepts.** Numerator zero for the $x$-axis, $f(0)$ for the
   $y$-axis.
3. **Turning points**, from $f'(x)=0$ on Paper 1 or from the calculator
   on Papers 2 and 3, quoted to three significant figures.
4. **Branches**, one region at a time, each leaving towards the
   asymptotes that bound its region.

**Count the branches before you draw.** One vertical asymptote cuts the
plane into two strips and gives two branches. **Two** vertical
asymptotes give three, and $\dfrac{1}{x^{2}-2x-3}$ is exactly that
question. The single most expensive mistake in the topic is drawing two
branches where there are three, or letting branches overlap because an
asymptote was left out — May 2021 TZ1 has a note for it: *"If vertical
asymptotes are absent (or not vertical) and the branches overlap as a
consequence, award maximum A0A1A0A1A1."*

**Which side does the branch leave on?** Take the sign of the
denominator just left and just right of the asymptote, and the sign of
the numerator there. Two signs, one quotient, and the branch goes up or
down accordingly. It is faster than plotting points and it never
misleads.

---
## Theory 3. The range, and the one symbol that carries the mark

The range is the set of heights the curve reaches. Read it off the
*vertical* axis of the picture you have just drawn — and then decide,
for each end of each piece, whether the curve actually gets there.

* A **turning point** is reached. Its value belongs to the range, and
  the inequality is $\le$ or $\ge$.
* A **horizontal asymptote** is not reached. Its value does not belong,
  and the inequality is strict.

That is the entire content of the question, and the markscheme for
November 2023 Q11(e) says so by awarding **A1A0 for strict inequalities
in both** places.

**Two ways to get there.**

*From the turning points.* Sketch, find the local maximum and the local
minimum, and read off. For $\dfrac{x^{2}-14x+24}{2x+6}$ they are at
$y=-10\pm 5\sqrt3$, and because the curve has a vertical asymptote
between them the range has a **gap**:
$y\le-10-5\sqrt3$ or $y\ge-10+5\sqrt3$.

*From the discriminant.* Put $y=f(x)$ and clear the fraction. For
$g(x)=\dfrac{2x-5}{x^{2}-3}$,

$$yx^{2}-2x+(5-3y)=0,$$

which has a real solution $x$ exactly when
$\Delta=4-4y(5-3y)=12y^{2}-20y+4\ge 0$, that is
$y\le\frac{5-\sqrt{13}}{6}$ or $y\ge\frac{5+\sqrt{13}}{6}$. This route
gives the **exact** boundary; the calculator route gives $0.232$ and
$1.43$.

**Do not forget the domain.** $-\dfrac{3x-2}{2x+1}$ over all of
$\mathbb{R}$ and over $x\ge 0$ have different ranges, and the question
that restricts the domain is the one that is asked.
""")

md(r"""
## Task 9 🟢 — the first sketch

The function $f$ is defined by $f(x)=\dfrac{2x-1}{x+1}$, $x\ne-1$.

Sketch the curve $y=f(x)$, showing the asymptotes with their equations
and the intercepts with both axes.

*Source: May 2022 TZ2, Paper 1, Q3(a)(b) (2 + 3 marks, no calculator).*
""")

code(r"""
my9a = [...]                       # the asymptotes, as equations
my9b = {
    'x_intercepts': [...],
    'y_intercept':  ...,
}

f9 = (2*x - 1)/(x + 1)
verify_asymptotes('Task 9(a)', my9a, f9)
verify_sketch('Task 9(b)', my9b, f9)

show(f9, span=(-9, 7), ylim=(-10, 12), lines=[('v', -1), ('h', 2)], size=(6, 3.5))
""")

md(r"""
## Task 10 🔴 — three branches, not two

A function $f$ is defined by $f(x)=\dfrac{1}{x^{2}-2x-3}$, where
$x\in\mathbb{R}$, $x\ne-1$, $x\ne 3$.

Sketch the curve $y=f(x)$, clearly indicating any asymptotes with their
equations. State the coordinates of any local maximum or minimum points
and any points of intersection with the coordinate axes.

*Source: May 2022 TZ2, Paper 1, Q11(a) (6 marks, no calculator). The six
marks are: $y$-intercept, the two vertical asymptotes, the horizontal
asymptote, the maximum with its coordinates, and the three branches.*
""")

code(r"""
my10a = [...]                      # every asymptote
my10b = {
    'y_intercept': ...,
    'maxima':      [...],          # as (x, y)
    'minima':      [...],          # there may be none — then write []
}

f10 = 1/(x**2 - 2*x - 3)
verify_asymptotes('Task 10(a)', my10a, f10)
verify_sketch('Task 10(b)', my10b, f10)

show(f10, span=(-5, 7), ylim=(-3, 2),
     lines=[('v', -1), ('v', 3), ('h', 0)], size=(6, 3.5))
""")

md(r"""
## Task 11 🔴 — a whole Paper 2 sketch

The function $f$ is defined by $f(x)=\dfrac{2x+3}{4x^{2}-1}$, for
$x\in\mathbb{R}$, $x\ne p$, $x\ne q$.

**(a)** Find the value of $p$ and the value of $q$ — that is, write down
the vertical asymptotes, together with the horizontal one.

**(b)** Sketch the graph of $y=f(x)$ for $-3\le x\le 3$, showing the
values of any axes intercepts, the coordinates of any local maxima and
minima, and the equations of any asymptotes.

*Source: May 2021 TZ1, Paper 2, Q11(a)(d) (2 + 5 marks). Coordinates to
three significant figures.*
""")

code(r"""
my11a = [...]                      # all three asymptotes
my11b = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'maxima':       [...],
    'minima':       [...],
}

f11 = (2*x + 3)/(4*x**2 - 1)
verify_asymptotes('Task 11(a)', my11a, f11)
verify_sketch('Task 11(b)', my11b, f11, domain=Interval(-3, 3))

show(f11, span=(-3, 3), ylim=(-12, 12),
     lines=[('v', -0.5), ('v', 0.5), ('h', 0)], size=(6, 3.5))
""")

md(r"""
## Task 12 🟡 — two more, one of each kind

**(a)** Sketch the graph of $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$ for
$-50\le x\le 50$, showing clearly the asymptotes and any intersections
with the axes. Enter the intercepts and the two turning points.

**(b)** Sketch the curve $y=\dfrac{x\left(x^{2}-16\right)}{x^{2}+16}$
for $-10\le x\le 10$. State the coordinates of the points where the
curve crosses the $x$-axis, and the coordinates of the local maximum and
the local minimum.

*Sources: November 2023, Paper 2, Q11(d) (4 marks); May 2025 TZ2, Paper
3, Q1(a) (1 + 1 + 2 marks). Three significant figures.*
""")

code(r"""
my12a = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'maxima':       [...],
    'minima':       [...],
}
my12b = {
    'x_intercepts': [...],
    'maxima':       [...],
    'minima':       [...],
}

f12a = (x**2 - 14*x + 24)/(2*x + 6)
f12b = x*(x**2 - 16)/(x**2 + 16)
verify_sketch('Task 12(a)', my12a, f12a)
verify_sketch('Task 12(b)', my12b, f12b, domain=Interval(-10, 10))

show(f12a, span=(-40, 40), ylim=(-40, 20),
     lines=[('v', -3), ('o', x/2 - Rational(17, 2))], size=(6, 3.2))
show(f12b, span=(-10, 10), ylim=(-8, 8), lines=[('o', x)], size=(6, 3.2))
""")

md(r"""
## Task 13 🟢 — the range of a parabola

**(a)** The function $f$ is defined for $x\in\mathbb{R}$ by
$f(x)=6x^{2}-12x+1$. Find the range of $f$.

**(b)** Consider $f(x)=\tfrac12 x^{2}+kx+13$, where $x\in\mathbb{R}$ and
$k\in\mathbb{Z}^{+}$. For $k=5$, write down the axis of symmetry of the
graph of $f$, and determine the coordinates of the minimum point.

*Sources: May 2021 TZ2, Paper 2, Q4(a) (2 marks); November 2025 TZ3,
Paper 1, Q9(b) (3 marks, no calculator).*
""")

code(r"""
my13a = ...                        # the range, as a set or an inequality in y
my13b = [...]                      # the minimum point, as (x, y)

verify_range('Task 13(a)', my13a, 6*x**2 - 12*x + 1)
verify_sketch('Task 13(b)', {'minima': my13b}, x**2/2 + 5*x + 13)

# The axis of symmetry is the vertical line through that point, and the
# markscheme wants it written as an equation: x = -5, not -5.
""")

md(r"""
## Task 14 🔴 — the range with a gap in it

Find the range of $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, $x\ne-3$ — the
function of tasks 7 and 12.

Give the boundaries **exactly**. The paper accepts $-18.7$ and $-1.34$;
the exact values are what the algebra produces, and they are what the
next question in the paper needs.

*Source: November 2023, Paper 2, Q11(e) (4 marks). The markscheme awards
A1A0 for strict inequalities in both places.*
""")

code(r"""
my14 = ...                         # the range: a union of two pieces

verify_range('Task 14', my14, (x**2 - 14*x + 24)/(2*x + 6))
""")

md(r"""
## Task 15 🟡 — the range by discriminant

A function $g$ is defined by $g(x)=\dfrac{2x-5}{x^{2}-3}$, where
$x\in\mathbb{R}$, $x\ne\pm\sqrt3$.

Determine the range of $g$, giving the boundaries exactly.

*Source: May 2023 TZ2, Paper 2, Q8(a) (4 marks). The markscheme offers
two routes — the turning points from the calculator, or the discriminant
of $yx^{2}-2x+(5-3y)=0$ — and the second gives the exact answer.*
""")

code(r"""
my15 = ...                         # the range

g15 = (2*x - 5)/(x**2 - 3)
verify_range('Task 15', my15, g15)

# The discriminant route, printed:
print('discriminant:', factor(expand(discriminant(y*x**2 - 2*x + (5 - 3*y), x))))
print('boundaries:  ', solveset(12*y**2 - 20*y + 4, y))
""")

md(r"""
## Task 16 🟢 — the range after a reflection, on half the line

The function $f$ is defined by $f(x)=\dfrac{3x-2}{2x+1}$ for
$x\in\mathbb{R}$, $x\ne-\tfrac12$ — the function of task 2(b). The
function $g$ is defined by $g(x)=-f(x)$ for $x\ge 0$.

Find the range of $g$.

*Source: May 2025 TZ2, Paper 1, Q1(c) (3 marks, no calculator). One end
is attained and the other is not, and that is the whole question.*
""")

code(r"""
my16 = ...                         # the range of g

g16 = -(3*x - 2)/(2*x + 1)
verify_range('Task 16', my16, g16, domain=Interval(0, oo))

show(g16, span=(0, 20), ylim=(-2, 3), lines=[('h', -Rational(3, 2))], size=(6, 3))
""")


md(r"""
---
# Part III — curves nobody has drawn for you

---
## Theory 4. Sketching from a formula, and what "sketch" actually means

Read the instruction and you are reading the markscheme. November 2023
Paper 2 Q2(a), three marks for a sketch of $e^{x}-3x-4$ on
$-4\le x\le 3$:

> *A1 for approximately correct roots* · *A1 for $y$-intercept AND local
> minimum in approximately correct positions* · *A1 for approximately
> correct endpoints*

Nothing about beauty, nothing about smoothness. **Four kinds of point,
and every one of them is a mark:**

* **roots** — where the curve meets the $x$-axis;
* **the $y$-intercept** — $f(0)$, and it is free;
* **turning points** — with their coordinates written down;
* **the endpoints of the given domain** — the most commonly forgotten
  mark in the topic. If the question says $1\le x\le 2$, then $(1,f(1))$
  and $(2,f(2))$ are part of the answer.

**Two shapes that are drawn wrong from memory.**

*A cubic need not turn.* $(x-1)(x^{2}-2x+5)$ has derivative
$3x^{2}-6x+7$, whose discriminant is $36-84<0$. No stationary points at
all: the curve rises everywhere, through a non-stationary point of
inflexion at $x=1$. Drawing the usual double bend loses every mark for
shape.

*A double root touches.* $x^{3}+4x^{2}+5x+2=(x+1)^{2}(x+2)$ meets the
axis at $x=-2$ crossing, and at $x=-1$ **touching** — and that touching
point is the local minimum. Factorise before drawing.

---
## Theory 5. When the question hands you the second derivative

*"Sketch the curve of $y=f(x)$ for $0\le x\le\pi$, taking into
consideration the **relative values** of the second derivative found in
part (b)."*

The previous part has already found the stationary points and evaluated
$f''$ at each. The signs tell you maximum or minimum — that was part
(b). This part is about the **sizes**.

$f''$ measures how fast the gradient is changing, so a large
$\lvert f''\rvert$ at a turning point means a sharp, tight turn and a
small one means a long flat one. For $f(x)=e^{\cos 2x}$ on $[0,\pi]$:

| point | $f''$ | drawn as |
| --- | --- | --- |
| $(0,e)$ | $-4e\approx-10.9$ | a sharp peak |
| $(\tfrac{\pi}{2},e^{-1})$ | $4e^{-1}\approx 1.47$ | a wide shallow valley |
| $(\pi,e)$ | $-4e\approx-10.9$ | a sharp peak |

The peaks are about $e^{2}\approx 7.4$ times as curved as the valley,
and the sketch has to show it: two narrow spikes and a long flat bottom
between them, not a symmetric wave.

---
## Theory 6. $y^{2}=f(x)$ is not a function

When the equation gives $y^{2}$, every $x$ with $f(x)>0$ has **two**
points, $\pm\sqrt{f(x)}$. So:

* **the $x$-axis is a line of symmetry** — draw the top half and reflect;
* the curve exists only where $f(x)\ge 0$, which fixes the domain;
* where $f(x)=0$ the two halves meet, and **how** they meet is the
  question.

$$\frac{dy}{dx}=\pm\frac{f'(x)}{2\sqrt{f(x)}}$$

and the denominator goes to $0$ at the meeting point. If the numerator
goes to zero faster, the halves arrive flat and meet in a **cusp**; if
not, they arrive vertically and the curve crosses the axis with an
infinite gradient.

That is exactly the difference the May 2022 TZ2 investigation is built
on. For $y^{2}=x^{3}$ at the origin, $\frac{dy}{dx}=\tfrac32\sqrt{x}\to
0$: a cusp. For $y^{2}=x^{3}+1$ at $x=-1$, the gradient is infinite: a
smooth vertical crossing. Everything else about the two curves is the
same shape.

**And a sideways parabola is still a parabola.** $y^{2}=16-8x$ opens to
the **left** (larger $y^{2}$ needs smaller $x$) with its vertex at
$(2,0)$; $y^{2}=4+4x$ opens to the right with its vertex at $(-1,0)$.

---
## Theory 7. Counting intercepts across a family

$y=x^{3}+ax^{2}+b$. The constant $b$ slides the whole curve up and down
and **does not move the stationary points**, because $\frac{dy}{dx}=
3x^{2}+2ax$ has no $b$ in it. So the stationary points sit at $x=0$ and
$x=-\tfrac{2a}{3}$ for ever, and only their *heights* change.

A cubic crosses the axis:

* **three times** when the two stationary heights are on opposite sides
  of the axis;
* **exactly twice** when one of them is *on* the axis — a double root;
* **once** when both are on the same side, or when there are no
  stationary points at all.

The heights are $b$ and $\tfrac{4a^{3}}{27}+b$, so with $a=3$ they are
$b$ and $b+4$, and the whole answer falls out:

| $b$ | heights | intercepts |
| --- | --- | --- |
| $b<-4$ | both negative | 1 |
| $b=-4$ | one zero | 2 |
| $-4<b<0$ | opposite signs | 3 |
| $b=0$ | one zero | 2 |
| $b>0$ | both positive | 1 |

**The general statement.** Three intercepts means $b$ and
$\tfrac{4a^{3}}{27}+b$ have opposite signs, that is, their product is
negative:

$$b\left(\frac{4a^{3}}{27}+b\right)<0 \iff 4a^{3}b+27b^{2}<0 .$$

The exam asks you to prove the implication one way. Factorising is the
whole proof — expanding is the way to get lost.
""")

md(r"""
## Task 17 🟢 — a parabola and a quarter of a hyperbola

**(a)** The function $f$ is defined by $f(x)=5(x+1)(x+3)$, where
$x\in\mathbb{R}$. Sketch the graph of $y=f(x)$, showing the values of
any intercepts with the axes and the coordinates of the vertex.

**(b)** Consider the function $f(x)=\sqrt{x^{2}-1}$, where
$1\le x\le 2$. Sketch the curve $y=f(x)$, clearly indicating the
coordinates of the endpoints.

*Sources: May 2025 TZ1, Paper 1, Q10(b) (4 marks, no calculator);
May 2022 TZ1, Paper 2, Q10(a) (2 marks).*
""")

code(r"""
my17a = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'minima':       [...],
}
my17b = {
    'endpoints': [...],            # two points, as (x, y)
}

f17a = 5*(x + 1)*(x + 3)
f17b = sqrt(x**2 - 1)
verify_sketch('Task 17(a)', my17a, f17a)
verify_sketch('Task 17(b)', my17b, f17b, domain=Interval(1, 2))

show(f17a, span=(-6, 2), ylim=(-10, 45), size=(5.5, 3))
show(f17b, span=(1, 2), size=(5.5, 3))
""")

md(r"""
## Task 18 🟡 — two curves the calculator is for

**(a)** Consider $f_1(x)=xe^{-x}$, where $x\ge 0$. Sketch the graph of
$y=f_1(x)$, stating the coordinates of the local maximum point, the
$x$-intercept and the horizontal asymptote.

**(b)** Consider $f(x)=e^{x}-3x-4$. Sketch the graph of $f$ for
$-4\le x\le 3$, showing the roots, the $y$-intercept, the local minimum
and the endpoints.

*Sources: May 2023 TZ1, Paper 3, Q1(a) (4 marks); November 2023, Paper
2, Q2(a) (3 marks). Three significant figures.*
""")

code(r"""
my18a = {
    'x_intercepts':          [...],
    'maxima':                [...],
    'horizontal_asymptotes': [...],
}
my18b = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'minima':       [...],
    'endpoints':    [...],
}

f18a = x*exp(-x)
f18b = exp(x) - 3*x - 4
verify_sketch('Task 18(a)', my18a, f18a, domain=Interval(0, oo))
verify_sketch('Task 18(b)', my18b, f18b, domain=Interval(-4, 3))

show(f18a, span=(0, 8), size=(5.5, 3), lines=[('h', 0)])
show(f18b, span=(-4, 3), size=(5.5, 3))
""")

md(r"""
## Task 19 🟡 — two cubics that are not the usual cubic

**(a)** Sketch $y=x^{3}+4x^{2}+5x+2$, showing the intercepts with the
axes and any turning points.

**(b)** Sketch the curve $y=(x-1)\left(x^{2}-2x+5\right)$, showing the
intercepts and any turning points. *(This is the case $a=r=1$, $b=2$ of
a Paper 3 investigation into $y=(x-r)(x^{2}-2ax+a^{2}+b^{2})$.)*

Where there is nothing to report, write `[]` — that is an answer too.

*Sources: November 2022, Paper 1, Q11(b)(iv) (3 marks, no calculator);
May 2022 TZ1, Paper 3, Q2(h)(i) (2 marks).*
""")

code(r"""
my19a = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'maxima':       [...],
    'minima':       [...],
}
my19b = {
    'x_intercepts': [...],
    'y_intercept':  ...,
    'maxima':       [...],
    'minima':       [...],
}

f19a = x**3 + 4*x**2 + 5*x + 2
f19b = (x - 1)*(x**2 - 2*x + 5)
verify_sketch('Task 19(a)', my19a, f19a, domain=Interval(-3, 1))
verify_sketch('Task 19(b)', my19b, f19b, domain=Interval(-1, 3))

# Why (b) has no turning points at all:
print('derivative:  ', expand(diff(f19b, x)))
print('discriminant:', discriminant(diff(f19b, x), x))
show(f19a, span=(-3, 1), ylim=(-5, 13), size=(5.5, 3))
show(f19b, span=(-1, 3), ylim=(-18, 18), size=(5.5, 3))
""")

md(r"""
## Task 20 🔴 — the solution of a differential equation, drawn

The differential equation $\dfrac{dy}{dx}+y=x^{2}-5$ has general
solution $y=x^{2}-2x-3+Ce^{-x}$.

Sketch the curve of the particular solution which passes through the
point $(-3,2)$, for $-4\le x\le 4$, labelling the coordinates of the
local maximum and minimum points.

*Source: May 2025 TZ3, Paper 2, Q12(c) (5 marks). Find $C$ first; the
markscheme has $C=-10e^{-3}=-0.498$.*
""")

code(r"""
my20 = {
    'maxima': [...],
    'minima': [...],
}

f20 = x**2 - 2*x - 3 - 10*exp(-x - 3)
verify_sketch('Task 20', my20, f20, domain=Interval(-4, 4))

print('through (-3, 2)?', simplify(f20.subs(x, -3)))
show(f20, span=(-4, 4), size=(6, 3.2))
""")

md(r"""
## Task 21 🔴 — the shape comes from $f''$

Consider the function $f(x)=e^{\cos 2x}$, where
$-\tfrac{\pi}{4}\le x\le\tfrac{5\pi}{4}$.

**(a)** The points of zero gradient on $0\le x\le\pi$ are $(0,e)$,
$\left(\tfrac{\pi}{2},e^{-1}\right)$ and $(\pi,e)$. Find $f''(0)$ and
$f''\!\left(\tfrac{\pi}{2}\right)$ exactly.

**(b)** By how many times is the curve more sharply bent at $(0,e)$ than
at $\left(\tfrac{\pi}{2},e^{-1}\right)$? Give the ratio
$\dfrac{\lvert f''(0)\rvert}{\lvert f''(\pi/2)\rvert}$ exactly.

**(c)** Enter the features of the sketch on $0\le x\le\pi$.

*Source: November 2023, Paper 1, Q11(a)(b)(c) (5 + 4 + 3 marks, no
calculator). The word "relative" in part (c) is what part (b) here makes
explicit.*
""")

code(r"""
my21a = ...                        # f''(0)
my21b = ...                        # f''(pi/2)
my21c = ...                        # the ratio
my21d = {
    'y_intercept': ...,
    'maxima':      [...],
    'minima':      [...],
}

f21 = exp(cos(2*x))
check_expr('Task 21(a) at 0', my21a, '""" + D_21A + r"""')
check_expr('Task 21(a) at pi/2', my21b, '""" + D_21B + r"""')
check_expr('Task 21(b) ratio', my21c, '""" + D_21C + r"""')
verify_sketch('Task 21(c)', my21d, f21, domain=Interval(-pi/4, 5*pi/4))

show(f21, span=(0, pi), size=(6, 3))
""")

md(r"""
## Task 22 🟡 — curves that are not functions

**(a)** Sketch $y^{2}=x^{3}$ for $x\ge 0$, and $y^{2}=x^{3}+1$ for
$x\ge-1$, on $-2\le x,y\le 2$. Enter the features of the **upper
branch** of each: $y=\sqrt{x^{3}}$ on $0\le x\le 2$, and
$y=\sqrt{x^{3}+1}$ on $-1\le x\le 2$.

**(b)** Write down the $y$-coordinates of the two points where
$y^{2}=x^{3}+1$ crosses the $y$-axis.

**(c)** The two curves differ in how the branches meet the $x$-axis.
Find the gradient of the upper branch of $y^{2}=x^{3}$ at its
$x$-intercept, and the gradient of the upper branch of $y^{2}=x^{3}+1$
at its $x$-intercept. One of them is infinite — write `oo`.

**(d)** On the same axes, sketch $y^{2}=16-8x$ and $y^{2}=4+4x$. Write
down the $x$-intercept of each.

*Sources: May 2022 TZ2, Paper 3, Q1(a)(b) (2 + 2 + 1 + 1 marks);
November 2023, Paper 3, Q2(b) (3 marks).*
""")

code(r"""
my22a1 = {'x_intercepts': [...], 'endpoints': [...]}
my22a2 = {'x_intercepts': [...], 'y_intercept': ..., 'endpoints': [...]}
my22b = [...]                      # the two y-intercepts
my22c1 = ...                       # gradient of sqrt(x^3) at its x-intercept
my22c2 = ...                       # gradient of sqrt(x^3+1) at its x-intercept
my22d1 = [...]                     # x-intercept of y^2 = 16 - 8x
my22d2 = [...]                     # x-intercept of y^2 = 4 + 4x

up1 = sqrt(x**3)
up2 = sqrt(x**3 + 1)
verify_sketch('Task 22(a) y^2=x^3', my22a1, up1, domain=Interval(0, 2))
verify_sketch('Task 22(a) y^2=x^3+1', my22a2, up2, domain=Interval(-1, 2))
check_set('Task 22(b)', my22b, '""" + D_22C + r"""')
check_num('Task 22(c) cusp', my22c1, 6, '""" + D_22A + r"""')
check_expr('Task 22(c) vertical', my22c2, '""" + D_22B + r"""')
check_set('Task 22(d) left-opening', my22d1, '""" + D_22D + r"""')
check_set('Task 22(d) right-opening', my22d2, '""" + D_22E + r"""')

print('gradient of sqrt(x^3)   at 0 :', limit(diff(up1, x), x, 0, '+'))
print('gradient of sqrt(x^3+1) at -1:', limit(diff(up2, x), x, -1, '+'))
show((up1, 'y^2 = x^3'), (-up1, ''), (up2, 'y^2 = x^3 + 1'), (-up2, ''),
     span=(-1.2, 1.7), ylim=(-2.2, 2.2), size=(5.5, 3.4))
show((sqrt(16 - 8*x), 'y^2 = 16 - 8x'), (-sqrt(16 - 8*x), ''),
     (sqrt(4 + 4*x), 'y^2 = 4 + 4x'), (-sqrt(4 + 4*x), ''),
     span=(-1.2, 2.2), ylim=(-6, 6), size=(5.5, 3.4))
""")


md(r"""
---
## Trainer: name the technique in five seconds

Fifteen questions with no solutions. For each one write the code of the
technique — nothing else. No calculation is wanted; the point is to know
what the first move is before any drawing starts.

Codes: `asym` (read the vertical/horizontal asymptote off a rational
function) · `limit` (an asymptote that needs a limit) · `oblique` (the
oblique asymptote) · `rational` (sketch a rational curve) · `range`
(find the range) · `sketch` (sketch from a formula, labelling features)
· `bend` (sketch from the second derivative) · `implicit`
($y^{2}=f(x)$) · `count` (count intercepts across a family)

1. $f(x)=\dfrac{x^{2}+1}{x-4}$ has an asymptote $y=ax+b$. Find $a$ and $b$.
2. Determine the range of $g(x)=\dfrac{x}{x^{2}+4}$.
3. Sketch $y^{2}=9-3x$, labelling the $x$-intercept.
4. Write down the equation of the horizontal asymptote of $\dfrac{5x-1}{2x+7}$.
5. Find the values of $k$ for which $y=x^{3}-12x+k$ meets the $x$-axis exactly once.
6. Sketch $y=f(x)$ using the relative values of $f''$ found in part (b).
7. Sketch $y=\dfrac{2}{x^{2}-9}$, showing all asymptotes and intercepts.
8. Sketch $y=x^{2}e^{-x}$ for $0\le x\le 5$, stating the local maximum.
9. By considering $\lim_{x\to\infty}$, find the horizontal asymptote of $\arctan(x^{2})$.
10. Find the range of $f(x)=4-3\cos x$ for $0\le x\le\pi$.
11. State the equation of the vertical asymptote of $y=\ln(x-3)$.
12. Sketch $y^{2}=x^{3}-x$ for $x\ge 1$, indicating where it meets the axis.
13. Sketch $y=\sin x-\tfrac{x}{2}$ for $-2\pi\le x\le 2\pi$, marking the endpoints.
14. For which $c$ does $y=x^{3}+cx$ have two stationary points?
15. Sketch $y=\dfrac{3x+1}{x-2}$, giving the equations of the asymptotes.
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
## Task 23 🔴 — on the timer, 12 minutes

The opening of a Paper 3 investigation. Eight marks, target time about
12 minutes.

*This question asks you to explore some properties of the family of
curves $y=x^{3}+ax^{2}+b$, where $x\in\mathbb{R}$ and $a$, $b$ are real
parameters.*

First consider the case $a=3$.

**(a)** By systematically varying the value of $b$, find the two values
of $b$ such that the curve $y=x^{3}+3x^{2}+b$ has exactly two $x$-axis
intercepts. [2]

**(b)** Write down the set of values of $b$ such that the curve has
exactly **(i)** one $x$-axis intercept; **(ii)** three. [1 + 1]

Now the case $a=-3$.

**(c)** Write down the set of values of $b$ such that
$y=x^{3}-3x^{2}+b$ has exactly **(i)** two intercepts; **(ii)** one;
**(iii)** three. [1 + 1 + 1]

**(d)** For a curve with exactly three $x$-axis intercepts, how many of
its two points of zero gradient lie **above** the $x$-axis? [1]

*Source: November 2023, Paper 3, Q1(a)(b)(c)(d) (2 + 1 + 1 + 1 + 1 + 1 +
1 marks).*
""")

code(r"""
my23a = ...                        # the two values of b, e.g. FiniteSet(...)
my23b1 = ...                       # one intercept, a = 3
my23b2 = ...                       # three intercepts, a = 3
my23c1 = ...                       # two intercepts, a = -3
my23c2 = ...                       # one intercept, a = -3
my23c3 = ...                       # three intercepts, a = -3
my23d = ...                        # how many of the two are above the axis


# The question itself, written as a function: how many distinct points
# does y = x^3 + a x^2 + b share with the x-axis? Nothing is stored —
# every answer below is checked against this.
def crossings(a_value, count):
    def holds(b_value):
        roots = Poly(x**3 + a_value*x**2 + b_value, x).real_roots()
        return len(set(roots)) == count
    return holds


verify_param_set('Task 23(a)', my23a, crossings(3, 2), var=b)
verify_param_set('Task 23(b)(i)', my23b1, crossings(3, 1), var=b)
verify_param_set('Task 23(b)(ii)', my23b2, crossings(3, 3), var=b)
verify_param_set('Task 23(c)(i)', my23c1, crossings(-3, 2), var=b)
verify_param_set('Task 23(c)(ii)', my23c2, crossings(-3, 1), var=b)
verify_param_set('Task 23(c)(iii)', my23c3, crossings(-3, 3), var=b)
check_num('Task 23(d)', my23d, 6, '""" + D_23D + r"""')

# The exploration the question asks for. Vary b and watch the count.
for bv in (-6, -4, -2, 0, 2):
    print(f'b = {bv:>3}:  ',
          len(set(Poly(x**3 + 3*x**2 + bv, x).real_roots())), 'intercepts')
show(*[(x**3 + 3*x**2 + bv, f'b = {bv}') for bv in (-6, -4, -2, 0, 2)],
     span=(-4, 2), ylim=(-8, 8), size=(6, 3.5))
""")

md(r"""
---
# Solutions

A full discussion of every task, with the markscheme breakdown. Open it
after you have worked the task yourself: the point is not the answer but
where the marks are, and which of them a self-check cannot see.
""")


md(r"""
## Solution 1 — the two you read off

**(a)** The denominator $3-x$ vanishes at $x=3$, so the vertical
asymptote is $\;x=3$. For the horizontal one the degrees are equal, so
take the ratio of the leading coefficients: $\dfrac{2}{-1}=-2$, giving
$\;y=-2$.

That minus sign is the whole difficulty of the part. Written as
$\dfrac{2x+4}{3-x}$ the denominator's leading coefficient is $-1$, and
reading the ratio as $2$ is the standard slip. Rewriting the function as
$\dfrac{-2x-4}{x-3}$ first makes it visible.

**(b)** $f(x)=0$ when the numerator is zero: $2x+4=0$, so
$(-2,0)$. And $f(0)=\dfrac{4}{3}$, so $\left(0,\tfrac43\right)$.

**The markscheme detail.** Both asymptote marks are lost if the answer
is a number. The markscheme for the same function in other sessions
prints the note *"must be an equation with $x$"* and *"must be an
equation with $y$"* against the two A1s. `verify_asymptotes` refuses a
bare number for the same reason.
""")

md(r"""
## Solution 2 — three quick reads

**(a)** $\dfrac{7x+7}{2x-4}$. The zero is where the numerator vanishes:
$7x+7=0$, so $x=-1$. The denominator vanishes at $x=2$, so $x=2$. Equal
degrees, so $y=\tfrac72$.

**(b)** $\dfrac{3x-2}{2x+1}$: equal degrees again, $y=\tfrac32$.

**(c)** $\dfrac{2x+6}{3x+6}$: equal degrees, $y=\tfrac23$. The tempting
answer here is $y=1$, from cancelling the $6$s — which is not a legal
move and gives the wrong line. Cancel the whole factor or nothing:
$\dfrac{2(x+3)}{3(x+2)}$ has no common factor at all.

**Why these are worth doing as a set.** Three one-mark parts, three
different-looking fractions, one rule. The rule is *degrees first, then
leading coefficients*, and nothing else in the topic is faster.
""")

md(r"""
## Solution 3 — a vertical asymptote with no denominator

$g(x)=2\ln x-\ln d$ is defined for $x>0$ and for no other $x$. As
$x\to 0^{+}$, $\ln x\to-\infty$, so $g(x)\to-\infty$: the line $x=0$ is
a vertical asymptote.

**$d$ never enters.** $-\ln d$ is a constant, and a constant slides the
graph up or down. Sliding a curve vertically cannot move a vertical
asymptote. The cell prints $g(0.001)$ for three values of $d$ to make
the point: the numbers differ, the behaviour does not.

**Where the mark actually goes.** This is one mark at the start of a
fifteen-mark question, and its purpose is to check that you know a
vertical asymptote is about the *domain*, not about a fraction. Every
other vertical asymptote in this practicum comes from a denominator; this
one does not, and that is why it is here.
""")

md(r"""
## Solution 4 — an asymptote that only a limit will give

$$f(x)=\arcsin\!\left(\frac{x^{2}-1}{x^{2}+1}\right).$$

Divide top and bottom of the fraction by $x^{2}$:

$$\frac{x^{2}-1}{x^{2}+1}=\frac{1-\tfrac{1}{x^{2}}}{1+\tfrac{1}{x^{2}}}
\longrightarrow 1 \quad\text{as } x\to\pm\infty .$$

$\arcsin$ is continuous at $1$, so
$f(x)\to\arcsin 1=\tfrac{\pi}{2}$, and the horizontal asymptote is
$\;y=\tfrac{\pi}{2}$.

**Two marks, two steps, and the second is the one that is dropped.** The
inside tends to $1$ — that is the first mark. Then you must *apply the
outer function*: $\arcsin$ of the limit, not the limit itself. Answering
$y=1$ is the failure this question is built to catch.

**Why no ratio of leading coefficients would help.** $f$ is not a
rational function. Its horizontal asymptote is a genuine limit, and
$\tfrac{\pi}{2}$ appears from nowhere in the algebra — only from
evaluating $\arcsin$ at the boundary of its domain. Note also that $f$
is *even*, which the previous part of the paper asks you to show, so the
same asymptote serves both ends.
""")

md(r"""
## Solution 5 — intercepts, vertical, oblique

$f(x)=\dfrac{x^{2}-x-12}{2x-15}$.

**(a)** $x^{2}-x-12=(x-4)(x+3)$, so the $x$-intercepts are $(4,0)$ and
$(-3,0)$; $f(0)=\dfrac{-12}{-15}=\dfrac45$, so $\left(0,\tfrac45\right)$.
The markscheme's note is worth reading: *"In part (a), penalise once
only, if correct values are given instead of correct coordinates."*
Three marks, and one of them is about writing pairs.

**(b)** $2x-15=0$, so $\;x=\tfrac{15}{2}$. The markscheme adds:
*"Award A0 for $x\le\tfrac{15}{2}$"* — an inequality is not a line.

**(c)** Write $x^{2}-x-12\equiv(ax+b)(2x-15)+c$ and expand:

$$2ax^{2}+(2b-15a)x-15b+c .$$

Matching $x^{2}$: $2a=1$, so $a=\tfrac12$. Matching $x$:
$2b-15a=-1$, so $2b=-1+\tfrac{15}{2}=\tfrac{13}{2}$ and
$b=\tfrac{13}{4}$. The asymptote is $\;y=\tfrac{x}{2}+\tfrac{13}{4}$.

**Four marks, four places to stop.** The markscheme prints four methods
and each splits the same way: $a$, then a method mark for whatever
produces $b$, then $b$, then the equation. Getting $a=\tfrac12$ and
stopping — which is what happens when the long division is done in the
head — collects one mark of four.

**The sign that goes wrong.** $2b-15a=-1$. Dropping the minus on the
$15a$ gives $b=-\tfrac{13}{4}$, an answer that looks entirely
reasonable and puts the asymptote in the wrong half of the plane. The
`apart` printed by the cell shows the whole decomposition, remainder
included.
""")

md(r"""
## Solution 6 — all the asymptotes at once

$g(x)=\dfrac{4x^{2}-1}{3x+2}$.

**Vertical:** $3x+2=0$, so $x=-\tfrac23$. (Check first that the fraction
does not cancel — $4x^{2}-1=(2x-1)(2x+1)$ has no factor $3x+2$, so it
does not.)

**Horizontal:** none. The numerator's degree is $2$ and the
denominator's is $1$.

**Oblique:** degree difference exactly one, so it exists. Taking limits,

$$a=\lim_{x\to\infty}\frac{4x^{2}-1}{x(3x+2)}=\frac43,\qquad
b=\lim_{x\to\infty}\left(\frac{4x^{2}-1}{3x+2}-\frac{4x}{3}\right)=-\frac89 .$$

So $\;y=\tfrac{4x}{3}-\tfrac89$, or $1.33x-0.889$.

**"All the asymptotes" is a trap phrase.** It invites you to write down
one of each kind, and here there is no horizontal asymptote at all. The
answer $y=\tfrac43$ — the ratio of leading coefficients, applied where
the rule does not apply — is the wrong answer this question is set to
collect, and the check rejects it by the definition: $g(x)-\tfrac43$
does not go to zero, it goes to infinity.

**The markscheme's last note.** *"Do not award the final A1 if the
answer is not given as an equation."* Four marks: the vertical
asymptote, the gradient, a method for the complete equation, and the
equation itself.
""")

md(r"""
## Solution 7 — the same three, on a harder fraction

$f(x)=\dfrac{x^{2}-14x+24}{2x+6}$.

**(a)** $2x+6=0$ gives $\;x=-3$. The markscheme accepts $2x+6=0$ as the
answer too — any equation that names the line.

**(b)** $x^{2}-14x+24=(x-2)(x-12)$, so $(2,0)$ and $(12,0)$. Note
*"Award A1A0 if only $x$ values are given"*: again, coordinates.

**(c)** $a=\tfrac12$ from the leading coefficients. Then
$x^{2}-14x+24\equiv\left(\tfrac{x}{2}+b\right)(2x+6)+c$ gives, from the
$x$ coefficient, $-14=3+2b$, so $b=-\tfrac{17}{2}$ and
$\;y=\tfrac{x}{2}-\tfrac{17}{2}$.

**Compare with task 5** — the same shape of question, the same four
marks, and the arithmetic sits in the same place: the coefficient of
$x$. In task 5 it was $2b-15a=-1$; here it is $2b+3=-14$. Both times the
constant term of the divisor multiplies the leading term of the
quotient, and both times that product is what gets dropped.

**This function is not finished with you.** Task 12 draws it and task 14
finds its range, and both need exactly what has just been computed. Nine
of the question's nineteen marks come from these three parts, and the
remaining ten are built on top of them.
""")

md(r"""
## Solution 8 — an asymptote for a whole family

$y=\dfrac{x\left(x^{2}-A\right)}{x^{2}+A}=\dfrac{x^{3}-Ax}{x^{2}+A}$.

Degree $3$ over degree $2$: one more, so an oblique asymptote exists.
Divide:

$$\frac{x^{3}-Ax}{x^{2}+A}=x-\frac{2Ax}{x^{2}+A},$$

and the remainder $\dfrac{2Ax}{x^{2}+A}\to 0$ as $x\to\pm\infty$. So the
asymptote is $\;y=x$ — for **every** positive $A$.

**Why that is the point of the question.** This is part (d)(ii) of a
Paper 3 investigation, and its job is to notice that the parameter does
not appear in the answer. The curve changes shape completely between
$A=1$ and $A=16$ — the plot in the cell shows it — and yet every member
of the family runs along the same line far away. That is what makes the
family a family.

**A one-mark part with a two-line answer.** The division is worth doing
in full: the remainder $-\dfrac{2Ax}{x^{2}+A}$ is what the next part of
the paper integrates.
""")

md(r"""
## Solution 9 — the first sketch

$f(x)=\dfrac{2x-1}{x+1}$: vertical asymptote $x=-1$, horizontal
asymptote $y=2$, $x$-intercept $\tfrac12$, $y$-intercept $-1$.

Now the drawing, in the markscheme's own order:

1. Dashed lines at $x=-1$ and $y=2$. They cut the plane into four
   quadrants-of-a-sort, and the curve lives in two of them.
2. The intercepts $\left(\tfrac12,0\right)$ and $(0,-1)$ both sit in the
   region right of $x=-1$ and below $y=2$, so that branch rises from
   $-\infty$ at $x=-1^{+}$ up towards $y=2$.
3. The other branch, left of $x=-1$, must be above $y=2$: as
   $x\to-1^{-}$ the denominator is a small negative and the numerator is
   about $-3$, so the quotient is large and positive.

**The markscheme's three marks** are: *"rational function shape with two
branches in opposite quadrants, with two correctly positioned asymptotes
and asymptotic behaviour shown"*, then one each for the two intercepts.
Note that the shape mark requires the asymptotes to be *positioned*, not
merely drawn — this is a single mark that two separate errors can cost.

**The sign test, once, as a habit.** Just left of $x=-1$: numerator
$\approx-3$ (negative), denominator small negative, quotient large
positive. Just right: numerator still $\approx-3$, denominator small
positive, quotient large negative. Two signs, and both ends of the
vertical asymptote are settled without plotting a point.
""")

md(r"""
## Solution 10 — three branches, not two

$f(x)=\dfrac{1}{x^{2}-2x-3}=\dfrac{1}{(x+1)(x-3)}$.

**Asymptotes.** $x=-1$ and $x=3$ from the denominator; $y=0$ because the
numerator has lower degree.

**Intercepts.** The numerator is $1$ and never zero, so there is **no**
$x$-intercept. $f(0)=-\tfrac13$.

**Turning point.** Differentiating,
$f'(x)=-\dfrac{2x-2}{(x^{2}-2x-3)^{2}}$, which is zero at $x=1$. There
$f(1)=\dfrac{1}{1-2-3}=-\tfrac14$, so $\left(1,-\tfrac14\right)$, and it
is a local **maximum** — the middle branch opens downwards.

**Three branches.** Two vertical asymptotes cut the line into three
intervals and each carries one branch:

| region | behaviour |
| --- | --- |
| $x<-1$ | positive, from $0^{+}$ up to $+\infty$ |
| $-1<x<3$ | negative throughout, with a maximum at $\left(1,-\tfrac14\right)$ |
| $x>3$ | positive, from $+\infty$ down to $0^{+}$ |

**Why $x=1$ and not something else.** The denominator is a parabola with
axis of symmetry $x=1$, and $\tfrac1u$ is monotone in $u$, so the
turning point of $f$ sits exactly where the turning point of the
denominator does. That shortcut works for $\tfrac{1}{\text{quadratic}}$
and for very little else — the moment the numerator is not constant it
fails, as tasks 11 and 12 show.

**Six marks**, one each for: the $y$-intercept, the two vertical
asymptotes, the horizontal asymptote, the maximum *with its
coordinates*, and the three branches with correct asymptotic behaviour.
Five of the six are labels.
""")

md(r"""
## Solution 11 — a whole Paper 2 sketch

$f(x)=\dfrac{2x+3}{4x^{2}-1}=\dfrac{2x+3}{(2x-1)(2x+1)}$.

**(a)** $p$ and $q$ are $\pm\tfrac12$; the horizontal asymptote is
$y=0$ because the bottom is heavier.

**(b)** $x$-intercept at $x=-\tfrac32$; $f(0)=\dfrac{3}{-1}=-3$.

For the turning points,

$$f'(x)=\frac{2(4x^{2}-1)-(2x+3)(8x)}{(4x^{2}-1)^{2}}
=\frac{-8x^{2}-24x-2}{(4x^{2}-1)^{2}},$$

so $4x^{2}+12x+1=0$ and
$x=\dfrac{-3\pm 2\sqrt2}{2}$, that is $x=-0.0858$ and $x=-2.91$.
Evaluating: the local **maximum** is $(-0.0858,\,-2.91)$ and the local
**minimum** is $(-2.91,\,-0.0858)$.

**Look at those two points.** The coordinates are each other's, swapped.
That is not a coincidence and not something you need in the exam, but it
is worth seeing: the two stationary abscissas $u,v$ satisfy $u+v=-3$ and
$uv=\tfrac14$, and for this particular $f$ it turns out that $f(u)=v$
and $f(v)=u$. The check confirms it and the notebook prints both.

**Which is which.** The middle branch, between $x=-\tfrac12$ and
$x=\tfrac12$, runs to $-\infty$ at both ends: near $\pm\tfrac12$ the
denominator $4x^{2}-1$ is a small **negative** while the numerator is
positive. So the middle branch is a hump, and its top at
$(-0.0858,-2.91)$ is a local maximum. The left branch comes up from
$0^{-}$, dips to $-0.0858$ at $x=-2.91$, crosses the axis at
$-\tfrac32$ and runs to $+\infty$.

**Five marks, and the note that costs them.** *"If vertical asymptotes
are absent (or not vertical) and the branches overlap as a consequence,
award maximum A0A1A0A1A1."* Two of five marks gone for one omission, and
the omission is not a calculation error — it is drawing before listing.
""")

md(r"""
## Solution 12 — two more, one of each kind

**(a)** $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, from task 7. Intercepts
$(2,0)$, $(12,0)$, $(0,4)$; vertical asymptote $x=-3$; oblique asymptote
$y=\tfrac{x}{2}-\tfrac{17}{2}$.

The turning points are at $x=-3\pm 5\sqrt3$, that is $-11.7$ and $5.66$,
with values $-10\mp 5\sqrt3$: a local maximum at $(-11.7,\,-18.7)$ on
the left branch and a local minimum at $(5.66,\,-1.34)$ on the right.
**Both stationary values are negative, and the maximum is below the
minimum** — which is only possible because a vertical asymptote runs
between them. Task 14 turns that observation into the range.

**(b)** $y=\dfrac{x\left(x^{2}-16\right)}{x^{2}+16}$: zeros at
$x=-4,0,4$, and by task 8 the oblique asymptote is $y=x$. The turning
points, from the calculator, are $(-1.94,\,1.20)$ and $(1.94,\,-1.20)$.

The curve is **odd**: replacing $x$ by $-x$ negates numerator and leaves
the denominator alone. So the three zeros are symmetric about the
origin, the maximum and the minimum are reflections of one another, and
the paper's next part asks you to say so.

**On the window.** Part (a) is drawn on $-50\le x\le 50$ and part (b) on
$-10\le x\le 10$, and the difference matters: at that scale (a) looks
like two straight lines either side of $x=-3$, and the turning points
are barely visible dents. The markscheme still wants them. Sketch the
interesting region and then check it against the demanded window, not
the other way round.
""")

md(r"""
## Solution 13 — the range of a parabola

**(a)** $f(x)=6x^{2}-12x+1=6(x-1)^{2}-5$. The square is at least zero,
so $f(x)\ge-5$ with equality at $x=1$. Range: $\;y\ge-5$.

The vertex is **attained**, so the inequality is not strict. That is the
whole of the two marks, and `verify_range` tests exactly it: the value
$-5$ must have a solution to $f(x)=-5$, and it does, $x=1$.

**(b)** $f(x)=\tfrac12 x^{2}+5x+13=\tfrac12(x+5)^{2}+\tfrac12$. Axis of
symmetry $x=-5$ — *as an equation*, says the markscheme — and the
minimum point is $\left(-5,\tfrac12\right)$.

**Where the $\tfrac12$ comes from.** The leading coefficient is
$\tfrac12$, not $1$, and it is easy to lose when reading the printed
formula. The paper's own part (a) settles it: the discriminant is
$k^{2}-4\cdot\tfrac12\cdot 13=k^{2}-26$, and the question turns on
$k^{2}<26$ giving $k\le 5$. With a leading coefficient of $1$ the
discriminant would be $4k^{2}-52$ and the answer would not be $5$.

**Completing the square is the whole technique for quadratics.** Vertex,
range, axis of symmetry and the discriminant condition all fall out of
$a(x-h)^{2}+k$, and there is nothing else to know.
""")

md(r"""
## Solution 14 — the range with a gap in it

$f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, and from solution 12 the two
stationary values are

$$y=-10-5\sqrt3\approx-18.7 \quad(\text{a local maximum}),\qquad
y=-10+5\sqrt3\approx-1.34 \quad(\text{a local minimum}).$$

The left branch rises to $-18.7$ and comes back down; the right branch
falls to $-1.34$ and comes back up. Between those two values **nothing
is reached at all**. So

$$y\le-10-5\sqrt3 \quad\text{or}\quad y\ge-10+5\sqrt3 .$$

**Both inequalities are non-strict**, because both values are attained —
at $x=-3-5\sqrt3$ and $x=-3+5\sqrt3$ respectively. The markscheme is
explicit: *"Award A1A0 for strict inequalities in both."*

**The exact form.** Setting $y=f(x)$ and clearing gives
$x^{2}-(14+2y)x+(24-6y)=0$, and requiring a real $x$ needs
$(14+2y)^{2}-4(24-6y)\ge 0$, that is $4y^{2}+80y+100\ge 0$, or
$y^{2}+20y+25\ge 0$, whose roots are $-10\pm 5\sqrt3$. The calculator
route gives $-18.7$ and $-1.34$, which the paper accepts; the algebra
gives the surds, which the paper's next part needs.

**Why a rational function's range has a gap and a polynomial's does
not.** The gap is the interval between the local maximum on one side of
a vertical asymptote and the local minimum on the other. Draw a
horizontal line at $y=-10$: it misses the curve entirely. That picture
*is* the answer, and reading it off the sketch takes less time than the
discriminant.
""")

md(r"""
## Solution 15 — the range by discriminant

$g(x)=\dfrac{2x-5}{x^{2}-3}$. Put $y=g(x)$ and clear:

$$y\left(x^{2}-3\right)=2x-5 \;\Longrightarrow\;
yx^{2}-2x+(5-3y)=0 .$$

For a given $y$ this is a quadratic **in $x$**, and $y$ is in the range
exactly when it has a real solution:

$$\Delta=4-4y(5-3y)=12y^{2}-20y+4\ge 0
\;\Longleftrightarrow\; 3y^{2}-5y+1\ge 0,$$

whose roots are $\dfrac{5\pm\sqrt{13}}{6}$. So

$$y\le\frac{5-\sqrt{13}}{6}\approx 0.232
\quad\text{or}\quad
y\ge\frac{5+\sqrt{13}}{6}\approx 1.43 .$$

**The case $y=0$ needs a glance.** When $y=0$ the equation is no longer
quadratic — it is $-2x+5=0$, with the solution $x=\tfrac52$. So $0$ is
in the range, and reassuringly $0<0.232$, so the answer above already
contains it. This is the standard hole in the discriminant method and
the standard way of closing it: check the degenerate coefficient
separately.

**The other route.** The markscheme also accepts finding the two
stationary values on the calculator, $1.43425\ldots$ and
$0.232408\ldots$, and writing the answer to three significant figures.
Four marks either way — but only the discriminant produces
$\sqrt{13}$, and "determine" in an AA HL question usually means the
exact form is wanted.
""")

md(r"""
## Solution 16 — the range after a reflection, on half the line

$f(x)=\dfrac{3x-2}{2x+1}$, and $g(x)=-f(x)$ for $x\ge 0$.

On $x\ge 0$: $f(0)=-2$, and $f(x)\to\tfrac32$ as $x\to\infty$ — the
horizontal asymptote from task 2(b). $f$ is increasing throughout (no
stationary points; its only vertical asymptote is at $x=-\tfrac12$,
outside the domain). So on $[0,\infty)$ the function $f$ runs from $-2$
up towards, but never reaching, $\tfrac32$.

Negating flips that interval:

$$g(0)=2, \qquad g(x)\to-\tfrac32,$$

and $g$ decreases from $2$ towards $-\tfrac32$. Hence

$$-\tfrac32<y\le 2 .$$

**One end closed, one end open, and that is the question.** $2$ is
attained — at $x=0$, the left end of the domain. $-\tfrac32$ is a
horizontal asymptote and is never reached. Three marks: one for the
method, one for both values, one for assembling them with the right
inequalities.

**The trap is the domain.** Over all of $\mathbb{R}$, $g$ takes every
value except $-\tfrac32$, and the answer would be
$y\ne-\tfrac32$. The restriction $x\ge 0$ is doing all the work, and
`verify_range` is given the same restriction — remove it and the same
answer is wrong.
""")

md(r"""
## Solution 17 — a parabola and a quarter of a hyperbola

**(a)** $f(x)=5(x+1)(x+3)$ is already factorised: $x$-intercepts at
$-3$ and $-1$. $f(0)=5\cdot 1\cdot 3=15$. The vertex sits halfway
between the roots, at $x=-2$, where $f(-2)=5(-1)(1)=-5$. So
$(-2,-5)$, and completing the square confirms it:
$f(x)=5(x+2)^{2}-5$.

Four marks: a roughly symmetric concave-up curve, the two
$x$-intercepts, the $y$-intercept, the vertex.

**(b)** $f(x)=\sqrt{x^{2}-1}$ on $1\le x\le 2$. The endpoints are
$(1,0)$ and $\left(2,\sqrt3\right)=(2,1.73)$, and the markscheme wants
both of them written down — *"The coordinates of endpoints may be seen
on the graph or marked on the axes."*

The shape is **concave down**: it is the top-right quarter of the
hyperbola $x^{2}-y^{2}=1$, which leaves the vertex $(1,0)$ vertically
and flattens towards the asymptote $y=x$. Drawing it concave up is the
error the mark is for.

**Two marks, one of which is shape.** This is the whole of the "sketch
a curve you have been given" technique in miniature: the ends, and the
bend between them.
""")

md(r"""
## Solution 18 — two curves the calculator is for

**(a)** $f_1(x)=xe^{-x}$, $x\ge 0$. It starts at the origin, so the
$x$-intercept and the $y$-intercept are both $(0,0)$.
$f_1'(x)=e^{-x}(1-x)$, zero at $x=1$, giving the local maximum
$\left(1,e^{-1}\right)=(1,0.368)$. As $x\to\infty$ the exponential wins
and $f_1\to 0^{+}$: the horizontal asymptote is $y=0$.

Four marks: the maximum labelled, the curve through the origin, the
correct domain $x\ge 0$, and the shape with its asymptotic behaviour.
Note the third one — half of the graph is not to be drawn.

**(b)** $f(x)=e^{x}-3x-4$ on $-4\le x\le 3$.

| feature | value |
| --- | --- |
| roots | $-1.24$ and $2.42$ |
| $y$-intercept | $-3$ |
| local minimum | $(1.10,\,-4.30)$ |
| endpoints | $(-4,\,8.02)$ and $(3,\,7.09)$ |

The minimum is where $f'(x)=e^{x}-3=0$, that is $x=\ln 3=1.0986$.

**Three marks, and the third is the endpoints.** The markscheme spells
out its tolerances: *"A1 for approximately correct roots, in the
intervals $-2\le x\le-1$ and $2\le x\le 3$"*, *"A1 for $y$-intercept AND
local minimum in approximately correct positions"*, *"A1 for
approximately correct endpoints"*. A sketch missing $(-4,8.02)$ and
$(3,7.09)$ loses a third of the marks, and that is the single most
common omission in the topic.

**Why the left end is so high.** At $x=-4$ the exponential is
negligible and the curve is essentially the line $-3x-4$, worth $8$. The
curve is a straight line on the left and an exponential on the right,
and the minimum is where the two behaviours change hands.
""")

md(r"""
## Solution 19 — two cubics that are not the usual cubic

**(a)** $x^{3}+4x^{2}+5x+2=(x+1)^{2}(x+2)$. So the curve **crosses** at
$x=-2$ and **touches** at $x=-1$. $y$-intercept $2$. The touching point
is a stationary point, and since the curve comes down to it and goes
back up it is the local minimum, $(-1,0)$. The local maximum is between
the two roots: $f'(x)=3x^{2}+8x+5=(3x+5)(x+1)$, zero at
$x=-\tfrac53$, and $f\!\left(-\tfrac53\right)=\tfrac{4}{27}=0.148$.

Three marks: positive cubic shape with the $y$-intercept, the
$x$-intercept at $(-2,0)$ with a local maximum somewhere between $-2$
and $-1$, and the local minimum **at $(-1,0)$**.

**A double root is a stationary point on the axis.** That is worth
stating as a rule: if $(x-r)^{2}$ divides the polynomial, the curve
touches at $r$ and $r$ is stationary. It saves the differentiation
entirely for that point.

**(b)** $y=(x-1)\left(x^{2}-2x+5\right)$. The quadratic factor has
discriminant $4-20<0$, so the only real root is $x=1$ and the only
$x$-intercept is $(1,0)$. $y$-intercept $-5$.

Expanding, $y=x^{3}-3x^{2}+7x-5$, so $y'=3x^{2}-6x+7$ with discriminant
$36-84=-48<0$: **no stationary points at all.** The curve increases
everywhere. $y''=6x-6$ vanishes at $x=1$ and changes sign there, so
there is a non-stationary point of inflexion at $(1,0)$ — the same
point as the $x$-intercept.

**Two marks: *"a positive cubic with no stationary points and a
non-stationary point of inflexion at $x=1$"*.** Drawing the familiar
double bend answers a different question. The cell prints the derivative
and its discriminant so the claim can be checked rather than believed.

**Why this is the interesting case.** In the investigation this comes
from, $(x-r)\left(x^{2}-2ax+a^{2}+b^{2}\right)$ has one real root $r$
and complex roots $a\pm bi$, and the point of inflexion always sits at
$x=\tfrac13(2a+r)$ — two thirds of the way from $r$ to $a$. Here
$a=r=1$, so the inflexion is at $x=1$ as well, and all three coincide.
""")

md(r"""
## Solution 20 — the solution of a differential equation, drawn

The general solution is $y=x^{2}-2x-3+Ce^{-x}$. Substituting
$(-3,2)$:

$$2=9+6-3+Ce^{3}=12+Ce^{3}
\;\Longrightarrow\; C=-10e^{-3}=-0.498 .$$

So the particular solution is
$y=x^{2}-2x-3-10e^{-x-3}$, and on $-4\le x\le 4$ it has

$$\text{local maximum } (-2.70,\,2.28), \qquad
\text{local minimum } (0.899,\,-4.19).$$

**Five marks and the first is $C$.** Substituting the point is a method
mark on its own; a sketch of the general solution, or of the wrong
member of the family, scores nothing after it.

**Why the curve has a maximum at all.** $x^{2}-2x-3$ is a parabola with
a single minimum. Subtracting $10e^{-x-3}$ — huge on the left, invisible
on the right — pulls the left-hand side of the parabola violently
downwards, and the two effects together create a hump. To the right of
about $x=2$ the exponential term has vanished and the curve is
indistinguishable from the parabola.

**What the checks cannot see here.** `verify_sketch` confirms the two
turning points, and that is all the markscheme labels. It does not
confirm that the curve dives to $-6.18$ at the left endpoint, nor the
shape between. Look at the printed graph after answering: the left end
is the part that surprises people.
""")

md(r"""
## Solution 21 — the shape comes from $f''$

$f(x)=e^{\cos 2x}$.

$$f'(x)=-2\sin 2x\,e^{\cos 2x},\qquad
f''(x)=\left(4\sin^{2}2x-4\cos 2x\right)e^{\cos 2x}.$$

**(a)** At $x=0$: $\sin 0=0$, $\cos 0=1$, so
$f''(0)=-4e\approx-10.9$. At $x=\tfrac{\pi}{2}$: $\sin\pi=0$,
$\cos\pi=-1$, so $f''\!\left(\tfrac{\pi}{2}\right)=4e^{-1}\approx 1.47$.

Negative at $x=0$ and at $x=\pi$: maxima. Positive at
$x=\tfrac{\pi}{2}$: minimum. That is part (b) of the paper, four marks.

**(b)** The ratio is

$$\frac{4e}{4e^{-1}}=e^{2}\approx 7.39 .$$

**(c)** So the sketch on $0\le x\le\pi$ has two **sharp** peaks at
$(0,e)$ and $(\pi,e)$ — height $2.72$ — and one **wide shallow** valley
at $\left(\tfrac{\pi}{2},e^{-1}\right)$, height $0.368$. Not a sine
wave: the curve spends most of its length near the bottom and turns
quickly at the top.

**"Taking into consideration the relative values" is the mark.** Three
marks for the sketch, and a symmetric wave with the right stationary
points collects some of them but not all — the question has already told
you the second derivatives and is asking you to use their *sizes*.

**The general rule.** At a stationary point the curve is locally
$y\approx f(a)+\tfrac12 f''(a)(x-a)^{2}$, a parabola whose width is set
by $\lvert f''(a)\rvert$. Seven times the second derivative means a
parabola $\sqrt7\approx 2.6$ times narrower. That is what "more sharply
bent" means and it is worth carrying: the second derivative is not only
a sign test.

**Note on the domain.** The function is defined on
$-\tfrac{\pi}{4}\le x\le\tfrac{5\pi}{4}$, and $x=0$ and $x=\pi$ are
genuine interior maxima of it — they are only the ends of the *drawing*
window. The check uses the function's own domain for that reason; using
$[0,\pi]$ would classify them as endpoints and lose the point.
""")

md(r"""
## Solution 22 — curves that are not functions

**(a)** $y^{2}=x^{3}$ needs $x\ge 0$; the upper branch is
$y=\sqrt{x^{3}}=x^{3/2}$, which starts at $(0,0)$ and reaches
$\left(2,2\sqrt2\right)=(2,2.83)$. Reflect in the $x$-axis for the
lower branch.

$y^{2}=x^{3}+1$ needs $x\ge-1$; the upper branch runs from $(-1,0)$
through $(0,1)$ to $(2,3)$.

**(b)** At $x=0$, $y^{2}=1$, so $y=\pm 1$: the curve crosses the
$y$-axis at $(0,1)$ and $(0,-1)$. **Two** intercepts, because the curve
is not a function — the standard omission here is writing only the
positive one.

**(c)** Differentiating the upper branches:

$$\frac{d}{dx}\sqrt{x^{3}}=\frac{3x^{2}}{2\sqrt{x^{3}}}
=\frac{3}{2}\sqrt{x}\;\longrightarrow\;0 \quad\text{as } x\to 0^{+},$$

$$\frac{d}{dx}\sqrt{x^{3}+1}=\frac{3x^{2}}{2\sqrt{x^{3}+1}}
\;\longrightarrow\;\infty \quad\text{as } x\to(-1)^{+},$$

because at $x=-1$ the numerator is $3$ and the denominator is $0$.

So $y^{2}=x^{3}$ meets the axis with **zero** gradient on both branches
— they arrive flat from opposite sides and form a **cusp** at the
origin. $y^{2}=x^{3}+1$ meets the axis **vertically**, and the two
branches join smoothly into a single curve crossing at $(-1,0)$.

That is the answer to *"identify two key features that would distinguish
one curve from the other"*: the cusp, and the different intercepts. The
markscheme lists several acceptable pairs, including *"graphs have
different domains"* and *"$y^{2}=x^{3}+1$ has points of inflexion"* —
those inflexions being $(0,\pm 1)$, the $y$-intercepts themselves.

**Common to the whole family $y^{2}=x^{3}+b$, $b>0$:** the $x$-axis is a
line of symmetry, there is exactly one $x$-intercept at
$x=-\sqrt[3]{b}$, two $y$-intercepts at $\pm\sqrt{b}$, the gradient at
the $x$-intercept is infinite, and there is no cusp. Two of those are
worth two marks in part (c) of the paper.

**(d)** $y^{2}=16-8x$ needs $16-8x\ge 0$, that is $x\le 2$: it opens to
the **left** with vertex $(2,0)$, and crosses the $x$-axis at $x=2$.
$y^{2}=4+4x$ needs $x\ge-1$: it opens to the **right** with vertex
$(-1,0)$ and crosses at $x=-1$. Three marks: two for the shapes and
positions, one for the two $x$-intercepts.

**How to see the direction instantly.** Solve for $x$: the first is
$x=2-\tfrac{y^{2}}{8}$, a parabola in $y$ with a negative coefficient,
so it opens towards negative $x$. The second is $x=\tfrac{y^{2}}{4}-1$,
positive coefficient, opening towards positive $x$. It is the same rule
as for ordinary parabolas, with the axes swapped.
""")

md(r"""
## Solution 23 — counting intercepts across a family

$y=x^{3}+ax^{2}+b$, and $\dfrac{dy}{dx}=3x^{2}+2ax=x(3x+2a)$, which does
not contain $b$. So the stationary points are always at $x=0$ and
$x=-\tfrac{2a}{3}$, and the values there are

$$y(0)=b, \qquad y\!\left(-\tfrac{2a}{3}\right)=\frac{4a^{3}}{27}+b .$$

**With $a=3$** those heights are $b$ and $b+4$, with the maximum at
$x=-2$ (height $b+4$) and the minimum at $x=0$ (height $b$).

**(a)** Exactly two intercepts means a double root, which means one of
the two heights is zero: $b=0$ or $b+4=0$, so $\;b=-4$ and $b=0$.

**(b)(i)** One intercept when both heights have the same sign:
$\;b<-4$ or $b>0$.
**(b)(ii)** Three when they have opposite signs: $\;-4<b<0$.

**With $a=-3$** the heights are $b$ and $b-4$, the maximum now at $x=0$
and the minimum at $x=2$.

**(c)(i)** $\;b=0$ or $b=4$. **(c)(ii)** $\;b<0$ or $b>4$.
**(c)(iii)** $\;0<b<4$.

**(d)** Exactly **one**. Three intercepts requires the two stationary
points to straddle the axis, so one is above it and one below — *"one
point of zero gradient is located on either side"*, as the markscheme
puts it.

**The general condition, which is part (h) of the paper.** Three
intercepts $\iff$ the two heights have opposite signs $\iff$ their
product is negative:

$$b\left(\frac{4a^{3}}{27}+b\right)<0
\;\Longleftrightarrow\;
\frac{1}{27}\left(4a^{3}b+27b^{2}\right)<0
\;\Longleftrightarrow\;
4a^{3}b+27b^{2}<0 .$$

Five marks, and the first of them is *"attempts to factorize"*. Written
as $b\left(\tfrac{4a^{3}}{27}+b\right)<0$ the condition says its own
meaning; expanded, it says nothing.

**"By systematically varying the value of $b$" is an instruction, not a
hint.** This is a calculator paper and the examiner expects a handful of
plots. The cell does exactly that — five values of $b$, five counts —
and the pattern is visible before any algebra. The algebra then explains
what was seen, which is the shape of every Paper 3 question in this
topic.

**And why the boundary cases go in neither interval.** $b=-4$ and $b=0$
give exactly two intercepts, so they belong to the answer of (a) and to
neither of the answers in (b). Putting them into the open intervals, or
writing $\le$, is the standard way to lose one of these one-mark parts —
and `verify_param_set` tests each boundary and each side of it
separately for that reason.
""")


def build():
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.12"}},
          "nbformat": 4, "nbformat_minor": 5}
    out = os.path.join(ROOT, 'practicum', 'functions',
                       'practicum-b4-curve-sketching.ipynb')
    with open(out, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    print(f'{out}: ячеек {len(cells)}')


if __name__ == '__main__':
    build()
