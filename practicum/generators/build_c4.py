"""Собирает практикум C4 (синусоидальные модели) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

t = sp.Symbol('t')
P = sp.pi

# --- точные значения ответов, из которых считаются хеши ---
_per_cos = 2 * P / sp.Rational(78, 10)                      # период a·cos(7.8t) + b
_h12 = sp.Rational(23, 10) * sp.sin(P / 6 * sp.Rational(21, 2)) + sp.Rational(9, 2)
_u = sp.asin(sp.Rational(5, 23))                            # порог 5 м у прилива
_hours = 2 * (6 - 12 * _u / P)

D_PER_COS = digest(sig(float(_per_cos), 3))                 # 0.806
D_PER_TAN = digest(sp.srepr(sp.simplify(P / 2)))            # точное pi/2
D_AMP = digest(sig(2.3, 3))
D_MID = digest(sig(4.5, 3))
D_B_TIDE = digest(sp.srepr(sp.simplify(P / 6)))
D_A_W = digest(sig(-0.4, 3))
D_B_W = digest(sig(1.4, 3))
D_C_TIDE = digest(sig(1.5, 3))
D_A_FW = digest(sig(-55, 3))
D_C_FW = digest(sig(65, 3))
D_B_FW = digest(sp.srepr(sp.simplify(P / 10)))
D_A_TAN = digest(sp.srepr(sp.simplify(-sp.sqrt(3) / 2)))
D_B_TAN = digest(sp.srepr(sp.simplify(sp.Rational(11, 2))))
D_H12 = digest(sig(float(_h12), 3))                         # 2.87
D_COUNT = digest(sig(6, 3))
D_HOURS = digest(sig(float(_hours), 3))                     # 10.3
D_C_FOLK = digest(sig(float(sp.Rational(2, 3)), 3))         # 0.667
D_R = digest(sig(15, 3))

TRIGGER = {1: 'per', 2: 'per', 3: 'amp', 4: 'per', 5: 'sign', 6: 'phase',
           7: 'build', 8: 'build', 9: 'use', 10: 'use', 11: 'thresh',
           12: 'phase', 13: 'bound', 14: 'bound', 15: 'sign'}
TRIGGER_KEY = {i: digest(v) for i, v in TRIGGER.items()}

cells = []


def _lines(src):
    parts = src.strip('\n').split('\n')
    return [p + '\n' for p in parts[:-1]] + parts[-1:]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Practicum C4: sinusoidal models 🌊

The topic opposite to trigonometric equations. There 77% of the marks came with no
calculator; here **87% come with one**: 72 marks out of 83 sit on Paper 2 and
Paper 3, leaving 11 without a calculator. There is almost nothing to compute; the
whole job is turning a description in words into a formula and then reading that
formula.

**Material.** 34 blocks and 83 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**What the topic is about.** Tides, a Ferris wheel, a mass on a spring, a growing
plant. In every case the same formula with four parameters:

$$H(t) = a\sin\bigl(b(t - c)\bigr) + d$$

and the whole exam question is seven parts around it: find each parameter, compute a
value, solve an inequality, shift the model. The question is almost always long and
connected, so a mistake in the first part costs half the marks of the whole thing.

**How to work**

1. Read the map of techniques. The first five are about assembling the model, the
   last three about using it.
2. Keep a drawing at hand. In this topic the graph is not an illustration but a
   tool: almost everything that gets asked can be read off it.
3. The answers are decimal nearly everywhere, **three significant figures**, as
   Paper 2 requires. Where an exact form is needed, the question says so.
4. The last blocks are a section about Paper 1, a recognition trainer and one
   question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + sin, cos, tan, pi, sqrt and the other names

language('en')                 # this notebook is in English, and so are the checks

import matplotlib.pyplot as plt
import numpy as np

t = Symbol('t')

print('ready; sympy', sp.__version__)
print('write the answer with the plain names: pi/6 =', pi/6)
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | Gives |
| --- | --- | --- | --- |
| 1 | Period and coefficient | «period», «between high tides», «repeats every» | $b$ |
| 2 | Amplitude and midline | the maximum and the minimum are given | $a$, $d$ |
| 3 | The sign of the amplitude | «starts at its lowest point» | the sign of $a$ |
| 4 | Phase shift | the time of the first maximum is known | $c$ |
| 5 | Assembling the model | a description in words, all the parameters at once | everything |
| 6 | Reading the model | «find the height at 12:00», «how many times» | a value |
| 7 | A threshold and a total time | «how many hours above 5 metres» | an interval |
| 8 | Bounding by ±1 | «prove that it is always above» | an inequality |

Techniques 1–5 answer the question «how do I get the formula». Techniques 6–8
answer «what do I do with it now». The eighth stands apart: it is the only one that
needs no calculator, and nearly every question on it is from Paper 1.

The main thing to understand about this topic: **the question is long and
connected.** A typical block in the archive is seven parts in a row about one and
the same tide, and the parameters found in parts (a)–(d) are used in (e)–(g). That
is exactly why a mistake in the amplitude costs not two marks but eight.
""")

md(r"""
---
## Theory 1. The four parameters and what each one does

$$H(t) = a\sin\bigl(b(t - c)\bigr) + d$$

| Parameter | What it means | How to find it |
| --- | --- | --- |
| $a$ | the amplitude, half the swing | $\dfrac{\max - \min}{2}$ |
| $d$ | the midline it oscillates about | $\dfrac{\max + \min}{2}$ |
| $b$ | the horizontal squeeze | $\dfrac{2\pi}{T}$, where $T$ is the period |
| $c$ | the shift to the right in time | from the time of the first maximum |

A check that catches half the mistakes: $a$ and $d$ **do not depend** on the
period, and $b$ and $c$ **do not depend** on the heights. If finding $b$ needed the
maximum, something has gone wrong.

The cell below shows what each parameter does. Change the numbers and look.
""")

code(r"""
grid = np.linspace(0, 24, 600)
model = lambda a, b, c, d: a*np.sin(b*(grid - c)) + d

fig, ax = plt.subplots(2, 2, figsize=(11, 5), sharex=True, sharey=True)
base = dict(a=2.3, b=np.pi/6, c=1.5, d=4.5)

for axis, (name, values, label) in zip(ax.flat, [
        ('a', [1.0, 2.3, 3.5], 'amplitude: stretches vertically'),
        ('d', [3.0, 4.5, 6.0], 'midline: moves up and down'),
        ('b', [np.pi/12, np.pi/6, np.pi/3], 'coefficient b: squeezes in time'),
        ('c', [0.0, 1.5, 3.0], 'shift c: moves to the right')]):
    for v in values:
        axis.plot(grid, model(**{**base, name: v}), lw=1.4, label=f'{name} = {v:.3g}')
    axis.set_title(label, fontsize=9)
    axis.legend(fontsize=7); axis.grid(alpha=.3)

fig.suptitle('H(t) = a·sin(b(t − c)) + d', fontsize=10)
plt.tight_layout(); plt.show()
""")

md(r"""
## Task 1 🟢 — the period from the coefficient

The height of a mass on a spring is given by $H(t) = a\cos(7.8t) + b$, where $t$ is
in seconds.

Find the period of this function. Three significant figures.

*Source: May 2023 TZ2, Paper 2, Q10(a) (2 marks, calculator).*
""")

code(r"""
my_period = ...

check_num('Task 1', my_period, 3, '""" + D_PER_COS + r"""')
""")

md(r"""
## Task 2 🟢 — and now a tangent

Given the function $f(x) = a\tan(2x) + b$, write down its period.

Give the answer **exactly**, in terms of $\pi$.

This task comes right after the first one for a reason. The sine and the cosine have
period $\dfrac{2\pi}{b}$, the tangent $\dfrac{\pi}{b}$: the tangent repeats twice as
often. The formula $2\pi/b$ applied to a tangent gives an answer exactly twice too
big, and that is one of the cheapest lost marks in the topic.

*Source: May 2025 TZ1, Paper 2, Q2(a) (1 mark, calculator).*
""")

code(r"""
my_period_tan = ...          # the exact value, for example pi/4

check_expr('Task 2', my_period_tan, '""" + D_PER_TAN + r"""')
""")

md(r"""
---
## Theory 2. Amplitude and midline

Both are read off the maximum and the minimum, and both are one line of
arithmetic:

$$a = \frac{\max - \min}{2}, \qquad d = \frac{\max + \min}{2}.$$

The meaning is clear from the picture: $d$ is the level everything oscillates about,
and $a$ is how far the graph goes from it. The sum gives the maximum, the difference
the minimum, and that is a ready-made check: $d + a$ has to equal the maximum.

Hence a second way, which the markscheme accepts as readily as the formulas: write
the system $d + a = \max$, $d - a = \min$ and solve it. It is longer, but if the
formulas have slipped away it saves the day.
""")

md(r"""
## Task 3 🟢 — the amplitude and midline of a tide

The height of the water in a harbour is modelled as

$$H(t) = a\sin\bigl(b(t - c)\bigr) + d,$$

where $t$ is the time in hours after midnight. The lowest water level is 2.2 m and
the highest 6.8 m.

Find $a$ and $d$.

*Source: November 2021, Paper 2, Q9(b) and Q9(c) (4 marks, calculator).*
""")

code(r"""
my_a = ...
my_d = ...

check_num('Task 3, a', my_a, 3, '""" + D_AMP + r"""')
check_num('Task 3, d', my_d, 3, '""" + D_MID + r"""')
""")

md(r"""
## Task 4 🟢 — the coefficient from the period

The same tide. Consecutive high tides are 12 hours apart.

Show that $b = \dfrac{\pi}{6}$.

Enter the answer **exactly**. This is a «show that»: the answer is printed in the
question, and the mark is for writing $b = 2\pi/12$ rather than simply copying the
result.

*Source: November 2021, Paper 2, Q9(a) (1 mark, calculator).*
""")

code(r"""
my_b = ...                   # the exact value

check_expr('Task 4', my_b, '""" + D_B_TIDE + r"""')
""")

md(r"""
---
## Theory 3. When the amplitude is negative

The formula $a = \dfrac{\max - \min}{2}$ gives the **size** of the amplitude, always
positive. But in the answer $a$ is sometimes negative, and that is not a slip.

Where the sign comes from. Take a model with no shift: $H(t) = a\cos(bt) + d$. At
$t = 0$ the cosine equals one, so $H(0) = a + d$:

- if $a > 0$, the motion **starts at the maximum**;
- if $a < 0$, the motion **starts at the minimum**.

So the phrase «the mass is released from its lowest point» or «the capsule starts at
the bottom» is a statement about the sign. A minus in front of the amplitude flips
the graph, and it is the way of saying «we start at the bottom» without introducing
the shift $c$.

The check takes a second: put $t = 0$ in and see whether you get the maximum or the
minimum from the question.
""")

md(r"""
## Task 5 🟡 — the sign of the amplitude

A mass hangs on a spring. Its height above the surface is given by

$$H(t) = a\cos(7.8t) + b.$$

The mass is **released from its lowest point**. The lowest height is 1 m, the
highest 1.8 m.

Find $a$ and $b$.

*Source: May 2023 TZ2, Paper 2, Q10(b) (3 marks, calculator).*
""")

code(r"""
my_a5 = ...                  # watch the sign
my_b5 = ...

check_num('Task 5, a', my_a5, 3, '""" + D_A_W + r"""')
check_num('Task 5, b', my_b5, 3, '""" + D_B_W + r"""')
""")

md(r"""
---
## Theory 4. The phase shift

$c$ answers the question «when», and it is found from the time at which an extremum
you know about happened.

The key is where the unshifted sine has its maximum. $\sin u$ has its maximum at
$u = \dfrac{\pi}{2}$, that is, **a quarter of a period** after the start. So
$a\sin\bigl(b(t - c)\bigr)$ with positive $a$ reaches its maximum when

$$b(t - c) = \frac{\pi}{2} \quad\Longleftrightarrow\quad t = c + \frac{T}{4}.$$

Hence the rule in one line: **$c$ = the time of the first maximum minus a quarter of
the period.**

A second way, which the markscheme accepts just as well: put the point of maximum
$(t_{\max}, H_{\max})$ into the model and solve the resulting equation for $c$. It is
safer when you are not sure whether what you have is a maximum or a minimum, but it
needs care in picking the smallest positive root — the equation
$\sin(\cdot) = 1$ has infinitely many.
""")

md(r"""
## Task 6 🟡 — the smallest shift

The same tide: $H(t) = 2.3\sin\bigl(\frac{\pi}{6}(t - c)\bigr) + 4.5$. The first
high tide (the maximum) is at 04:30, that is, at $t = 4.5$.

Find the smallest possible value of $c$.

*Source: November 2021, Paper 2, Q9(d) (3 marks, calculator).*
""")

code(r"""
my_c = ...

check_num('Task 6', my_c, 3, '""" + D_C_TIDE + r"""')
""")

md(r"""
## Task 7 🔴 — the whole model

A Ferris wheel has a diameter of 110 metres. The lowest point of a capsule is 10
metres above the ground. One full revolution takes 20 minutes. At $t = 0$ the
capsule is **at its lowest point**.

The height of the capsule is modelled as $h(t) = a\cos(bt) + c$, where $t$ is in
minutes.

Find $a$, $b$ and $c$.

Four techniques work at once here. The order that saves time: the swing gives the
size of the amplitude, the words «at its lowest point» give the sign, the lowest
point plus the swing give the midline, the period gives $b$.

*Source: May 2021 TZ1, Paper 2, Q3 (5 marks, calculator).*
""")

code(r"""
my_a7 = ...
my_b7 = ...                  # the exact value, in terms of pi
my_c7 = ...

check_num('Task 7, a', my_a7, 3, '""" + D_A_FW + r"""')
check_expr('Task 7, b', my_b7, '""" + D_B_FW + r"""')
check_num('Task 7, c', my_c7, 3, '""" + D_C_FW + r"""')
""")

md(r"""
## Task 8 🟡 — the parameters from two points

The maximum and the minimum are not always given. Sometimes two points of the graph
are given instead, and then the parameters come out of a system of equations.

The graph of $f(x) = a\tan(2x) + b$ passes through the points
$\left(\dfrac{\pi}{12},\, 5\right)$ and $\left(\dfrac{\pi}{3},\, 7\right)$.

Find $a$ and $b$. The answers are **exact**.

Put both points in, get two linear equations in $a$ and $b$ and solve the system.
You will need the exact values of $\tan\frac{\pi}{6}$ and $\tan\frac{2\pi}{3}$ —
both are on the unit circle.

*Source: May 2025 TZ1, Paper 2, Q2(b) (3 marks, calculator).*
""")

code(r"""
my_a8 = ...                  # the exact value
my_b8 = ...                  # the exact value

check_expr('Task 8, a', my_a8, '""" + D_A_TAN + r"""')
check_expr('Task 8, b', my_b8, '""" + D_B_TAN + r"""')
""")

md(r"""
---
## Theory 5. The model is assembled — what is done with it

From here the questions split into three kinds, and all three are done with a
calculator.

**A value at a given time.** Put $t$ in and compute. The only subtlety is the mode
of the calculator: the argument here is always in radians, because $b$ contains
$\pi$.

**A time from a given value.** Solve $H(t) = k$. The equation is trigonometric,
there are many roots, and the one asked for is wanted: the first, the smallest
positive, the one in the stated interval. Draw the graph and pick it off the
picture.

**Counting events.** «How many times in 5 seconds was the mass at its highest
point» — here you count periods: the maxima come one period apart, and you have to
work out how many fit into the interval. Careful at the ends: if a maximum falls
exactly on a boundary, you have to decide whether it counts, rather than hoping the
division comes out whole.
""")

md(r"""
## Task 9 🟢 — the height at a given time

The tide from tasks 3–6 is fully assembled:

$$H(t) = 2.3\sin\!\left(\frac{\pi}{6}(t - 1.5)\right) + 4.5.$$

Find the height of the water at 12:00. Three significant figures.

*Source: November 2021, Paper 2, Q9(e) (2 marks, calculator).*
""")

code(r"""
my_h12 = ...

check_num('Task 9', my_h12, 3, '""" + D_H12 + r"""')
""")

md(r"""
## Task 10 🟡 — how many times

Back to the mass on the spring: $H(t) = -0.4\cos(7.8t) + 1.4$, time in seconds.

How many times in the first 5 seconds does the mass reach its greatest height?

The answer is a whole number. Solving the equation for its roots takes longer here
than working out where the first maximum is and how far apart they come.

*Source: May 2023 TZ2, Paper 2, Q10(c) (2 marks, calculator).*
""")

code(r"""
my_count = ...

check_num('Task 10', my_count, 3, '""" + D_COUNT + r"""')
""")

md(r"""
---
## Theory 6. A threshold and a total time

The question «for how many hours in the day was the water above 5 metres» is the
inequality $H(t) > k$, and it is solved in three steps.

1. Solve the **equation** $H(t) = k$ and find all the roots in the interval
   wanted.
2. Work out between which roots the function is above the threshold — on the graph
   that is immediate, and without a graph the intervals are easy to swap.
3. Add up the lengths of the intervals that qualify.

The third step is the one people skip. What is asked is not «when» but «how much
time in total», and over a day the interval usually comes round twice, so the answer
is twice the length of one. The question says «total», not «find the times».
""")

md(r"""
## Task 11 🔴 — the total time above a threshold

The tide $H(t) = 2.3\sin\!\left(\frac{\pi}{6}(t - 1.5)\right) + 4.5$, with $t$ in
hours after midnight.

Find the **total** time in 24 hours during which the height of the water is above 5
metres. Three significant figures.

*Source: November 2021, Paper 2, Q9(f) (3 marks, calculator).*
""")

code(r"""
my_hours = ...

check_num('Task 11', my_hours, 3, '""" + D_HOURS + r"""')
""")

md(r"""
## Task 12 🟡 — shifting the model in time

In a neighbouring harbour the high tides happen **50 minutes earlier** than in the
first one. Everything else is the same.

Find the value of $c$ for the model of the neighbouring harbour. Three significant
figures.

Careful with the units: in the model the time is in hours and the shift is given in
minutes. And with the sign: «earlier» is a shift to the left, so $c$ becomes
**smaller**.

*Source: November 2021, Paper 2, Q9(g) (2 marks, calculator).*
""")

code(r"""
my_c_folk = ...

check_num('Task 12', my_c_folk, 3, '""" + D_C_FOLK + r"""')
""")

md(r"""
---
## Where Paper 1 is in this topic

In practicum C3 this section was about what the calculator changes. Here the
conversation is the other way round: **the calculator is nearly always there**, 72
marks out of 83 are Paper 2 and 3. The remaining 11 marks are the more interesting
ones, because the questions there are built on a completely different principle.

What the archive shows: **Paper 1 never asks you to find the parameters of a
model.** Not one question. Nobody is made to compute an amplitude and a period
without a calculator — that is arithmetic, and it is tested on Paper 2. Instead they
ask about what a calculator cannot help with:

- **a period in letters.** «$f(x) = \sin(qx)$ crosses the axis at $0$, $2m$, $4m$.
  Express $m$ in terms of $q$» — the answer is $m = \dfrac{\pi}{2q}$, with not a
  single number in the whole solution;
- **parity.** «Show that $f(x) = \dfrac{\sin^2(kx)}{x^2}$ is even» — substitute
  $-x$ and use the fact that the sine is odd;
- **bounding by $\pm 1$.** That is what the next piece of theory is about, and the
  question on the timer as well.

The practical conclusion: **do not train hand computation in this topic.** Train
reasoning about the parameters in general form — that is what earns the marks where
there is no calculator.

Technically, on Paper 2 watch one thing: the calculator has to be in **radians**.
Every model in this topic has $\pi$ in the coefficient, and degree mode gives a
plausible wrong answer that gives nothing away.
""")

md(r"""
---
## Theory 7. Bounding by ±1

The technique that replaces computation with reasoning. It rests on a single fact:

$$-1 \le \sin(\text{anything}) \le 1.$$

The argument does not matter: an arbitrarily complicated expression inside the sine
changes nothing. So if a function has a term $\sin(\ldots)$ in it, you always know
the bounds of its contribution without solving a single equation.

**On a real question.** The heights of two plants are modelled as
$h_A(t) = \sin(2t + 6) + 9t + 27$ and $h_B(t) = 8t + 32$. Prove that for $t > 6$
plant A is always the taller.

Computing the intersection points is pointless — «always» is not proved by numerical
roots. Instead take the difference:

$$h_A(t) - h_B(t) = \sin(2t + 6) + t - 5.$$

For $t > 6$ we have $t - 5 > 1$. And the sine is never less than $-1$. So the whole
difference is strictly greater than $1 - 1 = 0$, that is, $h_A > h_B$. Proved, with
not one computation.

The shape of the argument is always the same: **separate the sine from the rest,
bound the sine by a constant, show that the rest has enough to spare.**
""")

md(r"""
---
## Trainer: name the technique

Nothing is solved here: for each wording, name the technique with one code. Half the
work in this topic is seeing which of the four parameters is being asked about.

| Code | Technique |
| --- | --- |
| `per` | the period and the coefficient b |
| `amp` | the amplitude and the midline |
| `sign` | the sign of the amplitude, starting at the top or the bottom |
| `phase` | the phase shift c |
| `build` | assemble the whole model |
| `use` | compute a value or count events |
| `thresh` | a threshold, an inequality, a total time |
| `bound` | bounding by ±1, a proof |

1. «Find the period of $H(t) = a\cos(7.8t) + b$»
2. «Write down the period of $f(x) = a\tan(2x) + b$»
3. «The lowest height is 2.2 m, the highest 6.8 m. Find $a$ and $d$»
4. «Consecutive high tides are 12 hours apart. Show that $b = \pi/6$»
5. «The mass is released from its lowest point. Find $a$»
6. «The first high tide is at 04:30. Find the smallest $c$»
7. «Diameter 110 m, one revolution 20 minutes, starts at the bottom. Find $a$, $b$, $c$»
8. «The graph passes through $(\pi/12, 5)$ and $(\pi/3, 7)$. Find $a$ and $b$»
9. «Find the height of the water at 12:00»
10. «How many times in the first 5 seconds was the mass at its highest point»
11. «For how many hours in total in a day is the level above 5 metres»
12. «In the neighbouring harbour the tides are 50 minutes earlier. Find $c$»
13. «Prove that for $t > 6$ plant A is always taller than plant B»
14. «Given that $g(x) \ge 7$ for all $x$, find the smallest $r$»
15. «The capsule starts at the top. What will the sign of $a$ be?»

The target is 15 out of 15 in under two minutes.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '',
    9: '', 10: '', 11: '', 12: '', 13: '', 14: '', 15: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## Task 13 🔴 — ON THE TIMER: 8 minutes

Close everything above. Paper 1 format, **no calculator**, 5 marks.

Given the function

$$g(x) = 4\sin\!\left(x - \frac{3\pi}{2}\right) + 2.5 + q,$$

where $q$ is a constant. The graph of $g$ crosses the $y$-axis at the point
$(0, r)$.

Given that $g(x) \ge 7$ for all values of $x$, find the **smallest possible** value
of $r$.

A hint about the structure, not about the solution: there are two different steps
here. First the condition «for all $x$» turns into an inequality on $q$ — that is
technique 8. Then the smallest admissible $q$ goes into $g(0)$. Both steps are
short; the only long solution is the one that swaps them round.

*Source: May 2022 TZ1, Paper 1, Q5(b) (5 marks, no calculator).*
""")

code(r"""
# set a timer for 8 minutes
my_r = ...

check_num('Task 13', my_r, 3, '""" + D_R + r"""')
""")

md(r"""
### Attempt log

Fill it in right after the timer, while you still remember the train of thought.

| Question | Answer |
| --- | --- |
| Did you finish inside 8 minutes? | |
| Where did you start — with $g(0)$ or with bounding the sine? | |
| Where did the time go? | |
| Which step turned out not to be obvious? | |

If you started with $g(0)$, got $r = 6.5 + q$ and then did not know what to do with
$q$ — that is normal and means only that the steps are worth swapping round. The
markscheme credits both orders.
""")

md(r"""
---
# 🔑 Solutions

Check not only the answer but that no step is missing: the markscheme pays for
method. And in this topic especially — the question is long, the parts lean on one
another, and a step lost at the start costs marks right to the end.
""")

md(r"""
## Solution 1 — the period from the coefficient

For $a\cos(bt) + b$ the period is $\dfrac{2\pi}{|b|}$; here $b = 7.8$:

$$T = \frac{2\pi}{7.8} = 0.805536\ldots \approx 0.806\ \text{s}.$$

```python
my_period = 2*pi/7.8
```
""")

md(r"""
## Solution 2 — the period of a tangent

The tangent has half the period: $\dfrac{\pi}{|b|}$, not $\dfrac{2\pi}{|b|}$. At
$b = 2$:

$$T = \frac{\pi}{2}.$$

Why: $\tan$ repeats every $\pi$, because its period is already $\pi$ at $b = 1$ —
the graph runs off to infinity and comes back twice in one turn of the circle. The
answer $\pi$ (that is, $2\pi/2$) is what you get by applying the sine formula to a
tangent.

```python
my_period_tan = pi/2
```
""")

md(r"""
## Solution 3 — the amplitude and the midline

$$a = \frac{6.8 - 2.2}{2} = \frac{4.6}{2} = 2.3, \qquad
d = \frac{6.8 + 2.2}{2} = \frac{9}{2} = 4.5.$$

Check: $d + a = 4.5 + 2.3 = 6.8$ — that is the maximum; $d - a = 2.2$ — the
minimum.

```python
my_a = (6.8 - 2.2)/2
my_d = (6.8 + 2.2)/2
```
""")

md(r"""
## Solution 4 — the coefficient from the period

The period is $T = 12$ hours, because that is the gap between consecutive high
tides.

$$b = \frac{2\pi}{T} = \frac{2\pi}{12} = \frac{\pi}{6}.$$

The mark here is for the line $b = 2\pi/12$: in a «show that» the answer is already
printed, and copying it with no intermediate step gets no credit.

```python
my_b = 2*pi/12                # = pi/6
```
""")

md(r"""
## Solution 5 — the sign of the amplitude

The size of the amplitude and the midline are found as usual:

$$|a| = \frac{1.8 - 1}{2} = 0.4, \qquad b = \frac{1.8 + 1}{2} = 1.4.$$

Now the sign. The model is $H(t) = a\cos(7.8t) + b$; at $t = 0$ the cosine equals
one, so $H(0) = a + b$. The question says the mass is released from its **lowest**
point, so $H(0) = 1$, the minimum:

$$a + 1.4 = 1 \;\Longrightarrow\; a = -0.4.$$

```python
my_a5 = -0.4
my_b5 = 1.4
```

The answer $a = +0.4$ is exactly the mistake the question is designed for: the
arithmetic is right and the phrase about the lowest point has not been used.
""")

md(r"""
## Solution 6 — the smallest shift

**Way 1, through the quarter period.** The period is 12 hours, a quarter is 3
hours. The maximum of the sine comes a quarter of a period after $t = c$, so

$$c = 4.5 - 3 = 1.5.$$

**Way 2, by substitution.** Put the point of maximum $(4.5,\ 6.8)$ in:

$$2.3\sin\!\left(\frac{\pi}{6}(4.5 - c)\right) + 4.5 = 6.8
\;\Longrightarrow\; \sin\!\left(\frac{\pi}{6}(4.5 - c)\right) = 1.$$

Hence $\frac{\pi}{6}(4.5 - c) = \frac{\pi}{2} + 2\pi k$, that is,
$4.5 - c = 3 + 12k$ and $c = 1.5 - 12k$. The smallest positive one is at $k = 0$,
that is, $c = 1.5$.

The second way is longer, but it is the one that shows where the word «smallest»
comes from: there are infinitely many solutions, one period apart.

```python
my_c = 1.5
```
""")

md(r"""
## Solution 7 — the whole model

Four steps, one mark each.

1. **The size of the amplitude** is half the diameter: $|a| = 110/2 = 55$.
2. **The sign.** At $t = 0$ the cosine equals one, $h(0) = a + c$. The capsule
   starts at the bottom, so that is the minimum, so $a = -55$.
3. **The midline.** The lowest point is at a height of 10 and the swing upwards is
   110, so the centre of the wheel is at $10 + 55 = 65$, that is, $c = 65$.
4. **The period** is 20 minutes: $b = \dfrac{2\pi}{20} = \dfrac{\pi}{10}$.

Check: $h(0) = -55 + 65 = 10$ — the lowest point, as it should be.
$h(10) = -55\cos(\pi) + 65 = 55 + 65 = 120$ — the highest point, and
$120 - 10 = 110$ is the diameter.

```python
my_a7 = -55
my_b7 = 2*pi/20               # = pi/10
my_c7 = 65
```
""")

md(r"""
## Solution 8 — the parameters from two points

Put both points into $f(x) = a\tan(2x) + b$.

The first: $x = \dfrac{\pi}{12}$, so $2x = \dfrac{\pi}{6}$ and
$\tan\dfrac{\pi}{6} = \dfrac{1}{\sqrt3}$:

$$\frac{a}{\sqrt3} + b = 5.$$

The second: $x = \dfrac{\pi}{3}$, so $2x = \dfrac{2\pi}{3}$ and
$\tan\dfrac{2\pi}{3} = -\sqrt3$:

$$-a\sqrt3 + b = 7.$$

Subtract the first from the second:

$$-a\sqrt3 - \frac{a}{\sqrt3} = 2
\;\Longrightarrow\; -a\cdot\frac{3 + 1}{\sqrt3} = 2
\;\Longrightarrow\; a = -\frac{\sqrt3}{2}.$$

Substitute back: $b = 5 - \dfrac{a}{\sqrt3} = 5 + \dfrac{1}{2} = \dfrac{11}{2}$.

```python
my_a8 = -sqrt(3)/2
my_b8 = Rational(11, 2)
```

The negative $a$ here has nothing to do with «starting at the bottom» from task 5:
a tangent has neither a maximum nor a minimum. The sign is simply what the system
made it.
""")

md(r"""
## Solution 9 — the height at a given time

12:00 means $t = 12$:

$$H(12) = 2.3\sin\!\left(\frac{\pi}{6}\cdot 10.5\right) + 4.5
= 2.3\sin(1.75\pi) + 4.5.$$

$\sin(1.75\pi) = -\dfrac{\sqrt2}{2} \approx -0.7071$, so

$$H(12) \approx 2.3 \cdot (-0.7071) + 4.5 = 2.87365\ldots \approx 2.87\ \text{m}.$$

```python
my_h12 = 2.3*sin(pi/6*(12 - 1.5)) + 4.5
```

If you got something near 6.8, the calculator is in degrees.
""")

md(r"""
## Solution 10 — how many times

The period is $T = \dfrac{2\pi}{7.8} \approx 0.8055$ s.

The model $H(t) = -0.4\cos(7.8t) + 1.4$ starts at the minimum, so the first maximum
falls at **half** a period: $t \approx 0.4028$. After that the maxima come a full
period apart:

$$0.403,\quad 1.21,\quad 2.01,\quad 2.82,\quad 3.62,\quad 4.43,\quad 5.24,\ \ldots$$

The first six fall inside $[0, 5]$. Answer: **6 times**.

```python
my_count = 6
```

A common mistake is to divide $5$ by the period and take the integer part:
$5/0.8055 = 6.207$, which happens to give the right 6. Happens to — because with a
start at the maximum the same count would give 7 (the maximum at $t = 0$ counts
too). Count from the position of the first maximum, not by dividing.
""")

md(r"""
## Solution 11 — the total time above a threshold

Solve the equation $2.3\sin\!\left(\frac{\pi}{6}(t - 1.5)\right) + 4.5 = 5$:

$$\sin\!\left(\frac{\pi}{6}(t - 1.5)\right) = \frac{0.5}{2.3} = 0.21739\ldots$$

In the interval $[0, 24]$ there are four roots:

$$t \approx 1.9185,\quad 7.0815,\quad 13.9185,\quad 19.0815.$$

The water is above 5 metres between the first and the second root and between the
third and the fourth (between the second and the third it is low tide). Both bands
have the same length:

$$2\,(7.0815 - 1.9185) = 2 \cdot 5.1630 = 10.3258\ldots \approx 10.3\ \text{hours}.$$

```python
my_hours = 2*(7.08147 - 1.91852)
```

The factor of 2 is the whole question. An answer of 5.16 means one band out of two
has been found.
""")

md(r"""
## Solution 12 — shifting the model in time

50 minutes in hours: $\dfrac{50}{60} = \dfrac{5}{6}$ of an hour.

The tides are **earlier** — the graph shifts to the left, so $c$ decreases:

$$c_{\text{new}} = 1.5 - \frac{5}{6} = \frac{3}{2} - \frac{5}{6}
= \frac{9 - 5}{6} = \frac{2}{3} \approx 0.667.$$

The model of the neighbouring harbour:
$H(t) = 2.3\sin\!\left(\frac{\pi}{6}\left(t - \frac{2}{3}\right)\right) + 4.5$.

```python
my_c_folk = 1.5 - 50/60
```

Two traps, both on level ground: putting 50 in instead of 5/6, and adding instead of
subtracting. The check takes a second — the first high tide should come out at
$\frac{2}{3} + 3 = 3\frac{2}{3}$ hours, that is, at 03:40, which is exactly 50
minutes earlier than 04:30.
""")

md(r"""
## Solution 13 — the task on the timer

**Step 1: turn the condition «for all $x$» into an inequality on $q$.**

The smallest value of $4\sin\left(x - \frac{3\pi}{2}\right)$ is $-4$, because the
sine is never less than $-1$. So the smallest value of the whole function is
$-4 + 2.5 + q$. The requirement $g(x) \ge 7$ for all $x$ is exactly a requirement on
the minimum:

$$-4 + 2.5 + q \ge 7 \;\Longrightarrow\; q \ge 8.5.$$

**Step 2: put the smallest admissible $q = 8.5$ into $g(0)$.**

$$r = g(0) = 4\sin\!\left(-\frac{3\pi}{2}\right) + 2.5 + 8.5.$$

$\sin\left(-\frac{3\pi}{2}\right) = +1$, so

$$r = 4 + 2.5 + 8.5 = 15.$$

```python
my_r = 15
```

**The elegant way,** which the markscheme also accepts. Notice that
$4\sin\left(x - \frac{3\pi}{2}\right) = 4\cos x$. Then $g(x) = 4\cos x + 2.5 + q$,
and the point $x = 0$ is a **maximum**, not an arbitrary point. Hence at once: the
minimum lies $2 \cdot 4 = 8$ below the maximum, the minimum has to be no lower than
7, so the maximum is no lower than $7 + 8 = 15$.

The second way is shorter precisely because it starts by recognising the shift by
$\frac{3\pi}{2}$ — the very thing practicum C3 was about.
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = os.path.join(ROOT, 'practicum/functions',
                   'practicum-c4-sinusoidal-models.ipynb')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
print(f'cells: {len(cells)} -> {out}')
