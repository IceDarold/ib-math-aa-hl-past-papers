"""Собирает практикум C3 (тригонометрические уравнения) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

x = sp.Symbol('x')
P = sp.pi

D_LEAST = digest(sp.srepr(sp.simplify(17 * P / 6)))
D_GDC = digest(sig(1.8954942670339809, 3))
D_SINK = digest(sp.srepr(sp.simplify((-1 + sp.sqrt(5)) / 2)))

# тождества: те же приёмы в обратную сторону
D_FA = digest(sig(float(8 / sp.sqrt(5) + sp.sqrt(5) / 3), 3))
D_COS75 = digest(sp.srepr(sp.simplify((sp.sqrt(6) - sp.sqrt(2)) / 4)))
D_COT = digest(sp.srepr(sp.simplify(-sp.sqrt(5) / 2)))
D_ARCT = digest(sp.srepr(sp.simplify(P / 4)))

TRIGGER = {1: 'base', 2: 'arg', 3: 'pyth', 4: 'dbl', 5: 'fact', 6: 'tan',
           7: 'select', 8: 'gdc', 9: 'arg', 10: 'dbl', 11: 'select', 12: 'fact',
           13: 'sum', 14: 'pyth', 15: 'sum'}
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
# Practicum C3: trigonometric identities and equations 🔺

The topic where a calculator is almost never needed: the GDC share of the marks here
is **23%, the lowest in the whole archive**. Everything is done with exact values on
the unit circle. And it is the topic where marks are lost not on technique but on one
and the same thing — one root is found and the others are not.

**Material.** 43 blocks and 162 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**Two tracks in one practicum.** Tasks numbered **1–12** are equations: an equation
is given, find the roots. Tasks **T1–T5** are identities: the same identity is
applied the other way round, to prove an equality or to get an exact value. The
identities stand next to the piece of theory whose technique they turn around, and
they should be done before the neighbouring «solve»: in an exam question the «show
that» is almost always the first part and solving the equation the second.

**How to work**

1. Read the map of techniques. Nine techniques, and the first seven are about
   reducing the equation to the simplest one; the eighth is about what to do with
   the roots afterwards.
2. Solve the tasks **in order and on paper**. Draw the unit circle: in this topic
   it replaces half the working.
3. Enter the answer as a set of roots. The check substitutes each root into the
   equation **and separately checks that you have not lost the others** — it stores
   no reference answer, so `pi/6`, `30*pi/180` and `0.5235987` all count the same.
   For the identities the step is checked, not the answer: there the answer is
   printed in the question.
4. The last two blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + sin, cos, pi, sqrt, solve and the other names

language('en')                 # this notebook is in English, and so are the checks

x, theta = symbols('x theta')

print('ready; sympy', sp.__version__)
print('write the answer with the plain names: sin(pi/6) =', sin(pi/6))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | Reduces to |
| --- | --- | --- | --- |
| 1 | The reference angle and all the roots | one function, the argument is $x$ | — |
| 2 | A compound argument | $ax + b$ under the function, not $x$ | 1 |
| 3 | Addition of angles | an exact value of an angle not in the table; a sum of arctangents | 1 |
| 4 | The Pythagorean identity | the square of one function and the first power of another | 1 |
| 5 | The double angle | both $2x$ and $x$ appear | 4 |
| 6 | Factorising | a common factor, or the form $A\cdot B = 0$ | 5 |
| 7 | Reducing to a tangent | $\sin$ and $\cos$ to the same power | 6 |
| 8 | Selecting the roots | a fraction, a root, arccos, «the smallest positive» | — |
| 9 | A numerical solution | ugly coefficients, Paper 2 | 1 |

Techniques 1–7 answer the question «how do I reduce this to the simplest
equation». Technique 8 answers a different question — «which of the roots found have
the right to stay» — and so it is applied on top of any of the first seven.

The main question you ask yourself on seeing an equation: **how many different
trigonometric functions and how many different arguments does it contain?** The point
of techniques 1, 2, 4–7 is to bring both numbers down to one.

### Two directions of one technique

Techniques 3, 4 and 5 are identities, and an identity works both ways, and the exam
asks for both.

**Forwards — «solve».** The identity is used to simplify an equation and solve it.
The answer is numbers, and it has to be found.

**Backwards — «show that» and «find the exact value».** The same identity is used to
turn one expression into another. The answer is already printed in the question, and
the marks are for the step. There are sixteen such blocks in the archive, and half
of them fall on exactly the same identities as the equations.

The tasks numbered **T1–T5** below are the backwards move. They stand next to the
piece of theory whose technique they turn around, and it is worth doing them before
the neighbouring «solve». Their check is different: there is no reference answer to
compare with, so you enter an intermediate expression and `verify_identity` confirms
that it really does equal the original.

We start with the cheapest thing of all — rewriting.
""")

md(r"""
## Task T1 🟢 — everything in terms of sine and cosine

Given the function $f(x) = 4\cot x + \sin x$.

**(a)** Write $f(x)$ in terms of $\sin x$ and $\cos x$.

**(b)** Given that $\sec a = 1.5$, where $0 < a < \pi$, find $f(a)$.

The first move in half the identity questions is getting rid of `cot`, `sec` and
`cosec`, leaving only the sine and the cosine. Part (b) adds the thing that makes
these questions unpleasant: from $\sec a$ you get $\cos a$, and $\sin a$ has to be
recovered through the Pythagorean identity — **and the sign chosen from the
domain**.

*Source: May 2025 TZ1, Paper 2, Q6(a)(i) and Q6(c) (4 marks, calculator).*
""")

code(r"""
# (a) the expression in terms of sin and cos
my_f = ...

verify_identity('Task T1(a)', my_f, 4*cot(x) + sin(x))

# (b) the value of f(a), three significant figures
my_fa = ...

check_num('Task T1(b)', my_fa, 3, '""" + D_FA + r"""')
""")

md(r"""
---
## Theory 1. How many roots to expect

Before solving, it is useful to know the answer to «how many of them are there».
That is the only reliable defence against the main mistake of the topic.

On each turn of $2\pi$:

- $\sin x = k$ and $\cos x = k$ give **two** roots when $|k| < 1$, one when
  $|k| = 1$, and none when $|k| > 1$;
- $\tan x = k$ gives **one** root per period of $\pi$, that is, two in a turn of
  $2\pi$.

Then multiply by the number of turns in the domain. If the domain is $[0, 4\pi]$
there are two turns, and $\sin x = 1/2$ will have four roots, not two.

The reference angle is found with the inverse function **of the modulus of the
value**, and the sign and the quadrant are recovered by symmetry:

$$\sin x = k > 0 \Rightarrow x = \alpha,\ \pi - \alpha; \qquad
\cos x = k > 0 \Rightarrow x = \alpha,\ 2\pi - \alpha,$$

where $\alpha$ is the acute angle. For negative values the quadrants shift, and
there a drawing is more reliable than memory.
""")

md(r"""
## Task 1 🟢 — a domain wider than one turn

The graph of $f(x) = 6 + 6\cos x$ touches the $x$-axis. Find all the values of $x$
in $0 \le x \le 4\pi$ at which this happens.

Note the domain: there are two turns here.

*Source: May 2021 TZ2, Paper 1, Q10(a) (3 marks, no calculator).*
""")

code(r"""
# your answer: the list of roots
my_roots = ...

verify_roots('Task 1', my_roots, 6 + 6*cos(x), (0, 4*pi))
""")

md(r"""
## Task 2 🟢 — degrees and a compound argument

Solve $\tan(2x - 5^\circ) = 1$ for $0^\circ \le x \le 180^\circ$. Give both
solutions.

There are two catches at once. The first: the argument is not $x$, so the domain has
to be recomputed for the argument itself. The second: the tangent gives roots $\pi$
apart, not $2\pi$.

Enter the answer **in degrees**; the check allows for that.

*Source: May 2024 TZ2, Paper 1, Q1 (4 marks, no calculator).*
""")

code(r"""
my_roots = ...           # in degrees, for example [10, 100]

verify_roots('Task 2', my_roots, tan(2*x - 5*pi/180) - 1, (0, 180), deg=True)
""")

md(r"""
---
## Theory 2. A compound argument

If what stands under the function is $ax + b$, you solve **for the whole argument**
and recompute the domain for it too. The order is this:

1. Write $u = ax + b$.
2. Find what $u$ runs over while $x$ runs over its domain.
3. Solve the equation for $u$ inside the new domain.
4. Go back to $x$.

Step 2 is the one that gets skipped. If $x \in [0, \pi]$ and $u = 2x$, then
$u \in [0, 2\pi]$: the turn has doubled and there are twice as many roots. Solving
«for $x$ and then dividing» simply never produces them.

A storyline of its own is «the smallest positive value». The first roots found are
often negative, and you have to step a period forwards rather than take the first
one that turns up.
""")

md(r"""
---
## Theory 2a. Addition of angles — and how it differs from a compound argument

Two similar names for different things, and confusing them is expensive.

**A compound argument** (just above) is when $ax + b$ stands under the function with
numerical $a$ and $b$. Nothing is expanded, only the domain changes.

**Addition of angles** is when the argument is the sum of two angles, each of which
interests you separately. Then the function is expanded:

$$\sin(A \pm B) = \sin A\cos B \pm \cos A \sin B, \qquad
\cos(A \pm B) = \cos A\cos B \mp \sin A \sin B,$$

$$\tan(A \pm B) = \frac{\tan A \pm \tan B}{1 \mp \tan A \tan B}.$$

Note the signs in the cosine and the tangent: they are opposite to the sign on the
left. That is the most common slip in the topic.

What it is for in the exam — two storylines.

**Exact values outside the table.** The unit circle gives you $30^\circ$,
$45^\circ$, $60^\circ$. Everything else comes from addition: $75^\circ = 45^\circ +
30^\circ$, $15^\circ = 45^\circ - 30^\circ$. Since the answer has to be exact, a
calculator is no help here, however many digits it prints.

**Identities with the arctangent.** The formula for $\tan(A + B)$, read right to
left, adds two arctangents into one. There a caveat about the domain appears, and
that is what the mark is taken off for.
""")

md(r"""
## Task T2 🟡 — an exact value outside the table

**(a)** Using a suitable addition formula, show that
$\sin 75^\circ = \dfrac{\sqrt{2} + \sqrt{6}}{4}$.

**(b)** By the same method, find the exact value of $\cos 75^\circ$.

Part (a) is a «show that»: the answer is printed, the marks are for the working, and
there is nothing to check. Do it on paper and look at the solutions. Part (b) is the
same action, but the answer is yours now, and it will be checked.

*Source: May 2025 TZ1, Paper 1, Q11(c) (3 of 7 marks, no calculator); part (b) is
the same identity for the cosine.*
""")

code(r"""
my_cos75 = ...           # the exact value, no decimal approximations

check_expr('Task T2(b)', my_cos75, '""" + D_COS75 + r"""')
""")

md(r"""
## Task T5 🔴 — adding arctangents

**(a)** Show that for $p, q > 0$ with $pq < 1$

$$\arctan p + \arctan q \equiv \arctan\!\left(\frac{p + q}{1 - pq}\right).$$

**(b)** Hence find the exact value of $\arctan\frac{1}{2} + \arctan\frac{1}{3}$.

The idea of (a): write $A = \arctan p$, $B = \arctan q$, compute $\tan(A + B)$ with
the formula and take the arctangent back. That last step is the substantial one:
$\arctan(\tan\theta) = \theta$ holds **only when**
$-\frac{\pi}{2} < \theta < \frac{\pi}{2}$, and the conditions $p, q > 0$, $pq < 1$
are given precisely so that the sum lands there. Without that caveat the part loses
a mark.

In (b) check that the condition $pq < 1$ holds before applying the formula.

*Source: May 2021 TZ2, Paper 1, Q12(b) (4 marks, no calculator).*
""")

code(r"""
my_sum = ...             # the exact value

check_expr('Task T5(b)', my_sum, '""" + D_ARCT + r"""')
""")

md(r"""
## Task 3 🟡 — the smallest positive

Find the smallest positive value of $x$ for which

$$\cos\!\left(\frac{x}{2} + \frac{\pi}{3}\right) = \frac{1}{\sqrt{2}}.$$

Both «obvious» roots turn out to be negative — and that is the problem.

*Source: May 2022 TZ2, Paper 1, Q4 (5 marks, no calculator).*
""")

code(r"""
my_x = ...               # one exact value

check_expr('Task 3', my_x, '""" + D_LEAST + r"""')
""")

md(r"""
---
## Theory 3. How to get a quadratic equation

Two functions in one equation are reduced to one by two identities.

**The Pythagorean one**, when there is the square of one and the first power of the
other:

$$\cos^2 x = 1 - \sin^2 x, \qquad \sin^2 x = 1 - \cos^2 x.$$

**The double angle one**, when both $2x$ and $x$ appear. Choose the form to match
the function that is already standing next to it:

$$\cos 2x = 1 - 2\sin^2 x \quad (\text{with } \sin x \text{ nearby}), \qquad
\cos 2x = 2\cos^2 x - 1 \quad (\text{with } \cos x \text{ nearby}).$$

Choosing the form is the only substantial decision in this technique. Take the wrong
one and the equation ends up with both functions instead of one.

What follows is a quadratic in $\sin x$ or $\cos x$. After solving it, **always
check both roots against $[-1, 1]$**: a root like $\sin x = 2$ or $\cos x = 5/4$ is
discarded at once, and the markscheme has a separate mark for that.

The exam asks for both identities the other way round too — the next two tasks are
about that. They are useful not in themselves: in a five-part question the «show
that» is usually part (a), and the whole rest of the question leans on the form you
obtained. Miss (a) and you lose (b) and (c) as well.
""")

md(r"""
## Task T3 🟢 — the double angle backwards

Show that

$$\sin 2x + \cos 2x - 1 \equiv 2\sin x\,(\cos x - \sin x).$$

On the left there is $2x$, on the right only $x$, so the double angle formulas are
applied left to right. $\cos 2x$ has three forms; the one that works here is the one
after which the one cancels. Choose it — and then all that is left is taking out a
common factor.

Enter below the left-hand side **after the double angle formulas have been
substituted**, but before the brackets are expanded: the check will confirm that you
have not lost a factor along the way.

*Source: May 2021 TZ1, Paper 1, Q5(a) (2 marks, no calculator).*
""")

code(r"""
# the left-hand side rewritten in terms of x: replace sin 2x and cos 2x
my_left = ...

verify_identity('Task T3, the step', my_left, sin(2*x) + cos(2*x) - 1)
verify_identity('Task T3, the identity', my_left, 2*sin(x)*(cos(x) - sin(x)))
""")

md(r"""
## Task T4 🟡 — the Pythagorean identity and the quadrant

Given that $\operatorname{cosec}\theta = \dfrac{3}{2}$, with
$\dfrac{\pi}{2} \le \theta \le \dfrac{3\pi}{2}$, find the exact value of
$\cot\theta$.

Take it step by step: the cosecant gives $\sin\theta$, the Pythagorean identity
gives $\cos^2\theta$, the domain gives the **sign** of the cosine. That last step is
the task: the square root gives two values, and the right one can only be chosen by
looking at which quadrant $\theta$ is in.

A hint about the quadrant: your $\sin\theta$ is positive, and the domain starts at
$\pi/2$. That leaves exactly one quadrant.

*Source: May 2021 TZ1, Paper 1, Q6 (4 marks, no calculator).*
""")

code(r"""
my_cot = ...             # the exact value, with its sign

check_expr('Task T4', my_cot, '""" + D_COT + r"""')
""")

md(r"""
## Task 4 🟡 — the Pythagorean identity

Solve $2\cos^2 x + 5\sin x = 4$ for $0 \le x \le 2\pi$.

*Source: May 2021 TZ2, Paper 1, Q2 (7 marks, no calculator).*
""")

code(r"""
my_roots = ...

verify_roots('Task 4', my_roots, 2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi))
""")

md(r"""
## Task 5 🟡 — the double angle, with a negative part of the domain

Solve $\cos 2x = \sin x$ for $x \in [-\pi, \pi]$.

The quadratic here gives two values of the sine, and both qualify. Watch the left
half of the domain — that is the one people forget.

*Source: May 2023 TZ1, Paper 1, Q3 (6 marks, no calculator).*
""")

code(r"""
my_roots = ...

verify_roots('Task 5', my_roots, cos(2*x) - sin(x), (-pi, pi))
""")

md(r"""
## Task 6 🟡 — the double angle and an impossible root

Solve $2\cos 2\theta - 5\cos\theta + 2 = 0$ for $\pi \le \theta \le 2\pi$.

The quadratic gives two roots, but one of them cannot be a cosine. The other gives
exactly one solution in the stated domain.

*Source: May 2025 TZ3, Paper 1, Q3 (5 marks, no calculator).*
""")

code(r"""
my_roots = ...

verify_roots('Task 6', my_roots, 2*cos(2*theta) - 5*cos(theta) + 2,
             (pi, 2*pi), var=theta)
""")

md(r"""
---
## Theory 4. Do not divide, factorise

The most expensive mistake of the topic looks harmless. In the equation

$$\sin 2x = \sin x, \qquad\text{that is}\qquad 2\sin x\cos x = \sin x,$$

one wants to divide both sides by $\sin x$ and get $\cos x = 1/2$. But the division
is legitimate only when $\sin x \ne 0$, and where $\sin x = 0$ both sides of the
equation equal zero — that is, those are solutions as well, and they have just been
thrown away.

The right move is always the same: **take everything to one side and factorise.**

$$2\sin x\cos x - \sin x = 0 \;\Longrightarrow\; \sin x\,(2\cos x - 1) = 0.$$

Now both families of roots are visible: from $\sin x = 0$ and from $\cos x = 1/2$.

The rule: **never cancel an expression containing the variable**. If you really want
to — take it out as a factor and solve it separately. The check in this notebook
looks for that loss on purpose.
""")

md(r"""
## Task 7 🔴 — factorising

The graphs of $f(x) = \cos x$ and $g(x) = \sin 2x$ intersect. Find **all** the
values of $x$ in $[0, \pi]$ where that happens.

The original question asked only about two of the three points, so dividing by
$\cos x$ went unpunished there. Here all of them are wanted.

*Source: May 2024 TZ1, Paper 1, Q4(a) (3 marks, no calculator), domain widened.*
""")

code(r"""
my_roots = ...

verify_roots('Task 7', my_roots, cos(x) - sin(2*x), (0, pi))
""")

md(r"""
---
## Theory 5. Reducing to a tangent

If $\sin$ and $\cos$ appear to the same power, the equation is homogeneous and can
be divided by $\cos^n x$ — which gives an equation in the tangent:

$$\sin^2 x - 4\cos^2 x = 0 \;\Big/\; \cos^2 x \;\Longrightarrow\; \tan^2 x - 4 = 0.$$

Here the division is legitimate, but with a caveat that has to be said out loud:
**check separately whether $\cos x = 0$ is a solution**. In the example above, at
$\cos x = 0$ we get $\sin^2 x = 1 \ne 0$, so it is not, and dividing is allowed.

The second trap is taking the root. From $\tan^2 x = 4$ it follows that
$\tan x = \pm 2$, that is, **two** families of solutions. Half the marks lost in
such questions are a forgotten minus sign.
""")

md(r"""
## Task 8 🔴 — a homogeneous equation

Find the roots of $f(x) = \cos^2 x - 3\sin^2 x$ in $0 \le x \le \pi$.

*Source: November 2022, Paper 1, Q10(a) (5 marks, no calculator).*
""")

code(r"""
my_roots = ...

verify_roots('Task 8', my_roots, cos(x)**2 - 3*sin(x)**2, (0, pi))
""")

md(r"""
---
## Theory 6. Selecting the roots

A technique applied on top of the others. Four situations in which finding the roots
is only half the job.

**A fraction equals zero.** You need the numerator to be zero *while the denominator
is not*. If a root makes both vanish, it is not a solution.

**A caveat in the question.** Things like $\theta \ne \pi/4$ are not put there by
accident: that is exactly the root you will get if you solve carelessly.

**Squaring.** It always produces extraneous roots. After squaring, substituting back
into the **original** equation is compulsory — not into an intermediate one.

**Inverse functions.** The argument of $\arcsin$ and $\arccos$ has to lie in
$[-1, 1]$. In an equation with $\arccos 3x$ that immediately narrows $x$ to
$[-1/3, 1/3]$, and half the candidates drop out before any computation.
""")

md(r"""
## Task 9 🔴 — a fraction and a caveat

Solve

$$\frac{2\sin^2 2\theta - 5\sin 2\theta - 3}{\sin 2\theta - 1} = 0$$

for $0 \le \theta \le \pi$, $\theta \ne \dfrac{\pi}{4}$.

Three techniques meet here: a compound argument, a quadratic equation and selecting
the roots.

*Source: November 2021, Paper 1, Q6(b) (5 marks, no calculator).*
""")

code(r"""
my_roots = ...

verify_roots('Task 9', my_roots,
             (2*sin(2*theta)**2 - 5*sin(2*theta) - 3)/(sin(2*theta) - 1),
             (0, pi), var=theta)
""")

md(r"""
## Task 10 🔴 — an extraneous root

Solve $\arccos x + \arccos 3x = \dfrac{3\pi}{2}$.

The route: take the cosine of both sides, apply the formula for the cosine of a sum,
express the sines through $\sqrt{1 - x^2}$ and $\sqrt{1 - 9x^2}$, and square. There
will be two squarings, and both roots look equally plausible.

Substituting into the original equation leaves exactly one. Find it.

*Source: May 2025 TZ2, Paper 1, Q8(b) (6 marks, no calculator).*
""")

code(r"""
my_x = ...               # one exact value

# the check substitutes into the original equation
if my_x is Ellipsis:
    print('⬜ Task 10: the answer is not filled in')
elif abs(3*float(my_x)) > 1:
    print(f'❌ Task 10: at x = {my_x} the quantity arccos(3x) is undefined')
else:
    lhs = float(acos(my_x) + acos(3*my_x))
    ok = abs(lhs - float(3*pi/2)) < 1e-9
    print(f'{"✅" if ok else "❌"} Task 10: the left-hand side came out as '
          f'{lhs/float(pi):.4f}*pi, it should be 1.5000*pi')
""")

md(r"""
---
## The same thing on Paper 2

Everything above is Paper 1. In this topic that is how it is: 23 blocks out of 31
come with no calculator, and the GDC share of the marks here is **16%, the lowest in
the whole archive**. But when the calculator is there after all, the topic changes
beyond recognition.

Take task 4, $2\cos^2 x + 5\sin x = 4$ on $[0, 2\pi]$. On paper that is the
Pythagorean identity, a quadratic, discarding the root $\sin x = 2$ and the
reference angle — seven marks of work. With a calculator: take everything to one
side, draw the graph and read off the points where it crosses the axis.

The cell below does exactly what a GDC does.
""")

code(r"""
import matplotlib.pyplot as plt
import numpy as np

f = lambda t: 2*np.cos(t)**2 + 5*np.sin(t) - 4
grid = np.linspace(0, float(2*pi), 600)

plt.figure(figsize=(8, 3))
plt.axhline(0, color='0.6', lw=1)
plt.plot(grid, f(grid))
plt.xlabel('x'); plt.ylabel('2cos²x + 5sin x − 4'); plt.title('what a GDC shows')
plt.tight_layout(); plt.show()

# the roots by the same numerical method a calculator uses
sign = np.sign(f(grid))
for i in np.where(np.diff(sign) != 0)[0]:
    lo, hi = grid[i], grid[i+1]
    for _ in range(60):
        mid = (lo + hi)/2
        lo, hi = (lo, mid) if f(lo)*f(mid) <= 0 else (mid, hi)
    r = (lo + hi)/2
    print(f'root x ~ {r:.4f}   that is {r/np.pi:.4f}·pi')
""")

md(r"""
Three things worth taking away.

**The graph insures you against the main mistake of the topic.** A lost root is
visible to the eye: there are as many intersections on the picture as there are. If
on Paper 2 you are unsure whether you have lost a family of solutions, draw the
graph — it is cheaper than any check.

**The calculator does not give you an exact form.** In tasks 3 and 10 the answer has
to be exact — a multiple of $\pi$ in one, a radical in the other. A decimal
approximation earns no marks there, however many digits you write out. Among the
calculator papers **a fifth** of the questions are like that, so the plan «on Paper 2
I will just compute it» does not work.

**«Hence» forbids starting again.** If a part begins with *hence*, you are obliged
to lean on the previous result, and solving the equation from scratch with a
calculator earns no method marks. The wording *hence or otherwise* does.

And a technical point: watch the mode. Task 2 is set in degrees, tasks 1 and 4 in
radians. A calculator left in the wrong mode gives a plausible and wrong answer.
""")

md(r"""
## Task 11 🟡 — a numerical solution

Solve $\theta = 2\sin\theta$ and find the positive solution to three significant
figures.

There are no exact values here: the equation has no closed form. This is the only
case in the practicum where a calculator is needed.

*Source: November 2021, Paper 2, Q4(b) (1 mark).*
""")

code(r"""
my_theta = ...           # a number

check_num('Task 11', my_theta, 3, '""" + D_GDC + r"""')
""")

md(r"""
---
## Trainer: name the technique

Half the work is recognising the technique from the shape of the equation. Nothing is
solved here: for each equation, name the technique with one code.

| Code | Technique |
| --- | --- |
| `base` | the reference angle, it is already simplest |
| `sum` | addition of angles, an exact value is wanted |
| `arg` | a compound argument, recompute the domain |
| `pyth` | the Pythagorean identity → a quadratic |
| `dbl` | the double angle → a quadratic |
| `fact` | take out a factor, do not divide |
| `tan` | homogeneous, reduce to a tangent |
| `select` | the main thing here is selecting the roots |
| `gdc` | there are no exact values, compute numerically |

1. $\cos x = -1$ on $[0, 4\pi]$
2. $\tan(2x - 5^\circ) = 1$
3. $2\cos^2 x + 5\sin x = 4$
4. $\cos 2x = \sin x$
5. $\cos x = \sin 2x$
6. $\cos^2 x - 3\sin^2 x = 0$
7. $\dfrac{2\sin^2 2\theta - 5\sin 2\theta - 3}{\sin 2\theta - 1} = 0,\ \theta \ne \dfrac{\pi}{4}$
8. $\theta = 2\sin\theta$
9. $\cos\!\left(\dfrac{x}{2} + \dfrac{\pi}{3}\right) = \dfrac{1}{\sqrt{2}}$
10. $2\cos 2\theta - 5\cos\theta + 2 = 0$
11. $\arccos x + \arccos 3x = \dfrac{3\pi}{2}$
12. $\sin 2x + \cos 2x - 1 + \cos x - \sin x = 0$

The last three are from the identity track: there the question is not about roots but
about an exact value or a step. The technique is recognised in exactly the same way.

13. find the exact value of $\sin 75^\circ$
14. given $\operatorname{cosec}\theta = \frac32$ on $[\frac{\pi}{2}, \frac{3\pi}{2}]$, find $\cot\theta$
15. find the exact value of $\arctan\frac12 + \arctan\frac13$

The target is 15 out of 15 in under two and a half minutes.
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
## Task 12 🔴 — ON THE TIMER: 9 minutes

Close everything above. Paper 1 format, no calculator, 6 marks.

Given the identity $\sin 2x + \cos 2x - 1 = 2\sin x\,(\cos x - \sin x)$.

Solve $\sin 2x + \cos 2x - 1 + \cos x - \sin x = 0$ for $0 < x < 2\pi$.

The rate is 1.5 minutes per mark, that is, 9 minutes. Write the time of each attempt
into the log and come back to the task in a week and in a month.

A hint about the structure, not about the solution: there are four roots.

*Source: May 2021 TZ1, Paper 1, Q5(b) (6 marks, no calculator).*
""")

md(r"""
### Attempt log

| Date | Time | What slowed you down |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
import time
t0 = time.time()

my_roots = ...

verify_roots('Task 12', my_roots,
             sin(2*x) + cos(2*x) - 1 + cos(x) - sin(x), (0, 2*pi))
print(f'time spent: {(time.time() - t0)/60:.1f} min')
""")

md(r"""
---
# 🔑 Solutions

Check not only the answer but that no step is missing: the markscheme pays for
method. And almost every solution has a step «how many roots to expect» — it earns
no marks directly, but it is the one that stops you losing half the answer.
""")

md(r"""
## Solution T1 — everything in terms of sine and cosine

**(a)** $\cot x = \dfrac{\cos x}{\sin x}$, so
$f(x) = \dfrac{4\cos x}{\sin x} + \sin x$.

**(b)** By definition $\sec a = \dfrac{1}{\cos a}$, so
$\cos a = \dfrac{1}{1.5} = \dfrac{2}{3}$.

Then the Pythagorean identity: $\sin^2 a = 1 - \dfrac{4}{9} = \dfrac{5}{9}$. The
sign comes from the domain: on $(0, \pi)$ the sine is always positive, so
$\sin a = \dfrac{\sqrt5}{3}$ with no choice to make.

$$f(a) = \frac{4 \cdot \tfrac{2}{3}}{\tfrac{\sqrt5}{3}} + \frac{\sqrt5}{3}
= \frac{8}{\sqrt5} + \frac{\sqrt5}{3} = \frac{29\sqrt5}{15} \approx 4.32.$$

```python
my_f = 4*cos(x)/sin(x) + sin(x)
my_fa = 8/sqrt(5) + sqrt(5)/3        # 29*sqrt(5)/15
```
""")

md(r"""
## Solution T2 — an exact value outside the table

**(a)** $75^\circ = 45^\circ + 30^\circ$, and both angles are in the table:

$$\sin 75^\circ = \sin45^\circ\cos30^\circ + \cos45^\circ\sin30^\circ
= \frac{\sqrt2}{2}\cdot\frac{\sqrt3}{2} + \frac{\sqrt2}{2}\cdot\frac{1}{2}
= \frac{\sqrt6}{4} + \frac{\sqrt2}{4} = \frac{\sqrt2 + \sqrt6}{4}.$$

**(b)** The same split, the formula for the cosine — and the sign in the middle
changes to the opposite one:

$$\cos 75^\circ = \cos45^\circ\cos30^\circ - \sin45^\circ\sin30^\circ
= \frac{\sqrt6}{4} - \frac{\sqrt2}{4} = \frac{\sqrt6 - \sqrt2}{4}.$$

A sanity check: $75^\circ$ is close to $90^\circ$, so the sine should be close to one
($0.966$) and the cosine close to zero ($0.259$). And so it is. Mix the signs up and
the numbers swap places, which is visible at once.

```python
my_cos75 = (sqrt(6) - sqrt(2))/4
```
""")

md(r"""
## Solution T3 — the double angle backwards

On the right there are only first powers and the common factor $2\sin x$. So on the
left you need to produce a factor $\sin x$ and get rid of the free one.

$\sin 2x = 2\sin x\cos x$ — there is only one form.

$\cos 2x$ has three forms, and choosing between them is the only substantial step:

- $\cos 2x = 1 - 2\sin^2 x$ gives $+1$, and with the $-1$ already there it goes.
  That is the one to take;
- $\cos 2x = 2\cos^2 x - 1$ gives $-2$ as the free term;
- $\cos 2x = \cos^2 x - \sin^2 x$ gives no free term at all.

An important caveat: the other two forms are **not a mistake**. The identity holds
with any of them and you will get to the answer, just through
$2\cos^2 x - 2 = -2\sin^2 x$ — an extra step, and in the exam an extra minute. The
check in the cell accepts all three: it looks at whether your expression equals the
original, not at whether it matches a model answer.

$$\sin 2x + \cos 2x - 1 = 2\sin x\cos x + (1 - 2\sin^2 x) - 1
= 2\sin x\cos x - 2\sin^2 x = 2\sin x(\cos x - \sin x).$$

```python
my_left = 2*sin(x)*cos(x) + (1 - 2*sin(x)**2) - 1
```
""")

md(r"""
## Solution T4 — the Pythagorean identity and the quadrant

1. $\operatorname{cosec}\theta = \dfrac{1}{\sin\theta} = \dfrac{3}{2}
   \Rightarrow \sin\theta = \dfrac{2}{3}$.
2. $\cos^2\theta = 1 - \dfrac{4}{9} = \dfrac{5}{9}
   \Rightarrow \cos\theta = \pm\dfrac{\sqrt5}{3}$.
3. **Choosing the sign is the task.** The sine is positive, so $\theta$ is in the
   first or the second quadrant. The domain starts at $\pi/2$, which rules the first
   one out. The second is left, and there the cosine is negative:
   $\cos\theta = -\dfrac{\sqrt5}{3}$.
4. $\cot\theta = \dfrac{\cos\theta}{\sin\theta}
   = \dfrac{-\sqrt5/3}{2/3} = -\dfrac{\sqrt5}{2}$.

The answer $+\sqrt5/2$ is exactly the mistake the question is designed for: the
technique is all right and the mark for the domain has not been taken.

```python
my_cot = -sqrt(5)/2
```
""")

md(r"""
## Solution T5 — adding arctangents

**(a)** Write $A = \arctan p$, $B = \arctan q$; then $\tan A = p$, $\tan B = q$.

$$\tan(A + B) = \frac{\tan A + \tan B}{1 - \tan A\tan B} = \frac{p + q}{1 - pq}.$$

Now take the arctangent of both sides. That step is not always legitimate:
$\arctan(\tan\theta) = \theta$ only when
$-\frac{\pi}{2} < \theta < \frac{\pi}{2}$. Check that we are there. From $p, q > 0$
it follows that $A, B \in \left(0, \frac{\pi}{2}\right)$, and from $pq < 1$ that
$\tan A\tan B < 1$, which is exactly the condition $A + B < \frac{\pi}{2}$. So the
sum lies in $\left(0, \frac{\pi}{2}\right)$, and

$$A + B = \arctan\!\left(\frac{p + q}{1 - pq}\right).$$

The mark here is precisely for saying the caveat about the domain out loud — without
it the working is formally wrong.

**(b)** $p = \frac12$, $q = \frac13$, the product is $pq = \frac16 < 1$ — the formula
applies.

$$\arctan\frac12 + \arctan\frac13
= \arctan\frac{\tfrac12 + \tfrac13}{1 - \tfrac16}
= \arctan\frac{5/6}{5/6} = \arctan 1 = \frac{\pi}{4}.$$

```python
my_sum = pi/4
```
""")

md(r"""
## Solution 1 — a domain wider than one turn

1. Touching the axis: $6 + 6\cos x = 0$, that is, $\cos x = -1$.
2. The value has $|k| = 1$, so there is exactly **one** root per turn. The domain
   $[0, 4\pi]$ is two turns, so there are two roots.
3. $\cos x = -1$ at $x = \pi$ and, adding the period $2\pi$, at $x = 3\pi$.

```python
my_roots = [pi, 3*pi]
```
""")

md(r"""
## Solution 2 — degrees and a compound argument

1. Let $u = 2x - 5^\circ$. While $x$ runs over $[0^\circ, 180^\circ]$, $u$ runs over
   $[-5^\circ, 355^\circ]$ — almost a full turn.
2. $\tan u = 1$ at $u = 45^\circ$, and the period of the tangent is $180^\circ$, so
   also at $u = 225^\circ$. Both fall inside the domain for $u$.
3. Go back: $2x = 50^\circ \Rightarrow x = 25^\circ$;
   $2x = 230^\circ \Rightarrow x = 115^\circ$.

```python
my_roots = [25, 115]
```

Solving «for $x$ and then dividing» never produces the second root.
""")

md(r"""
## Solution 3 — the smallest positive

1. $\cos u = \dfrac{1}{\sqrt{2}}$ at $u = \pm\dfrac{\pi}{4} + 2k\pi$.
2. Here $u = \dfrac{x}{2} + \dfrac{\pi}{3}$, hence
   $x = 2u - \dfrac{2\pi}{3} = \pm\dfrac{\pi}{2} - \dfrac{2\pi}{3} + 4k\pi$.
3. At $k = 0$ we get $x = -\dfrac{\pi}{6}$ and $x = -\dfrac{7\pi}{6}$ — both
   negative.
4. Step a period forwards, $k = 1$: $x = \dfrac{23\pi}{6}$ and
   $x = \dfrac{17\pi}{6}$.
5. The smallest positive one is $\dfrac{17\pi}{6}$.

```python
my_x = 17*pi/6
```

The period in $x$ here is $4\pi$, not $2\pi$: the argument contains $x/2$. Whoever
steps by $2\pi$ gets the wrong answer.
""")

md(r"""
## Solution 4 — the Pythagorean identity

1. There is $\cos^2 x$ and the first power of $\sin x$, so replace the cosine:
   $2(1 - \sin^2 x) + 5\sin x = 4$.
2. Tidy up: $-2\sin^2 x + 5\sin x - 2 = 0$, that is,
   $2\sin^2 x - 5\sin x + 2 = 0$.
3. Factorise: $(2\sin x - 1)(\sin x - 2) = 0$.
4. Discard $\sin x = 2$: the sine does not exceed one. That leaves
   $\sin x = \dfrac{1}{2}$.
5. On the turn $[0, 2\pi]$ that is two roots: $x = \dfrac{\pi}{6}$ and
   $x = \dfrac{5\pi}{6}$.

```python
my_roots = [pi/6, 5*pi/6]
```
""")

md(r"""
## Solution 5 — the double angle

1. $\sin x$ stands nearby, so take $\cos 2x = 1 - 2\sin^2 x$.
2. $1 - 2\sin^2 x = \sin x$, that is, $2\sin^2 x + \sin x - 1 = 0$.
3. $(2\sin x - 1)(\sin x + 1) = 0$, hence $\sin x = \dfrac{1}{2}$ or
   $\sin x = -1$.
4. On $[-\pi, \pi]$: from $\sin x = \dfrac{1}{2}$ we get
   $x = \dfrac{\pi}{6},\ \dfrac{5\pi}{6}$; from $\sin x = -1$ we get
   $x = -\dfrac{\pi}{2}$.

```python
my_roots = [-pi/2, pi/6, 5*pi/6]
```

The root $-\dfrac{\pi}{2}$ is the one that gets lost: the domain covers the negative
half, while habit looks for roots in $[0, 2\pi]$.
""")

md(r"""
## Solution 6 — an impossible root

1. $\cos\theta$ stands nearby, so take $\cos 2\theta = 2\cos^2\theta - 1$.
2. $2(2\cos^2\theta - 1) - 5\cos\theta + 2 = 0$, that is,
   $4\cos^2\theta - 5\cos\theta = 0$.
3. Take out the factor: $\cos\theta\,(4\cos\theta - 5) = 0$.
4. $\cos\theta = \dfrac{5}{4} > 1$ is impossible. That leaves $\cos\theta = 0$.
5. On $[\pi, 2\pi]$ that is the single point $\theta = \dfrac{3\pi}{2}$.

```python
my_roots = [3*pi/2]
```

Note step 3: there is no free term left, and the equation factorises by taking out a
factor rather than through the quadratic formula.
""")

md(r"""
## Solution 7 — factorising instead of dividing

1. $\cos x = \sin 2x = 2\sin x\cos x$.
2. Take everything to the left: $\cos x - 2\sin x\cos x = 0$.
3. Take out the factor: $\cos x\,(1 - 2\sin x) = 0$.
4. $\cos x = 0$ on $[0, \pi]$ gives $x = \dfrac{\pi}{2}$.
5. $\sin x = \dfrac{1}{2}$ on $[0, \pi]$ gives $x = \dfrac{\pi}{6},\ \dfrac{5\pi}{6}$.

```python
my_roots = [pi/6, pi/2, 5*pi/6]
```

Divide by $\cos x$ and you are left with $\sin x = 1/2$ and two roots instead of
three. The check in the task looks for exactly that and says near which point the
loss is.
""")

md(r"""
## Solution 8 — reducing to a tangent

1. Check whether the division is allowed: at $\cos x = 0$ the expression equals
   $-3\sin^2 x = -3 \ne 0$, so $\cos x = 0$ is not a solution and dividing is
   allowed.
2. Divide by $\cos^2 x$: $1 - 3\tan^2 x = 0$, hence $\tan^2 x = \dfrac{1}{3}$.
3. Take the root with **both** signs: $\tan x = \pm\dfrac{1}{\sqrt{3}}$.
4. On $[0, \pi]$: $\tan x = \dfrac{1}{\sqrt{3}}$ gives $x = \dfrac{\pi}{6}$;
   $\tan x = -\dfrac{1}{\sqrt{3}}$ gives $x = \dfrac{5\pi}{6}$.

```python
my_roots = [pi/6, 5*pi/6]
```

Step 1 is worth saying out loud even when the answer is obvious: in questions where
$\cos x = 0$ does turn out to be a solution, skipping it costs a mark.
""")

md(r"""
## Solution 9 — a fraction and a caveat

1. A fraction is zero when the numerator is zero and the denominator is not.
2. The numerator: $2\sin^2 2\theta - 5\sin 2\theta - 3 = 0$. Write
   $s = \sin 2\theta$: $2s^2 - 5s - 3 = 0$, that is, $(2s + 1)(s - 3) = 0$.
3. $s = 3$ is impossible. That leaves $\sin 2\theta = -\dfrac{1}{2}$.
4. The denominator vanishes when $\sin 2\theta = 1$ — a different value, so the
   roots found are legitimate. The caveat $\theta \ne \pi/4$ is exactly what removes
   the point where the denominator is zero.
5. The domain: $\theta \in [0, \pi]$ means $2\theta \in [0, 2\pi]$ — a full turn.
   $\sin u = -\dfrac{1}{2}$ gives $u = \dfrac{7\pi}{6},\ \dfrac{11\pi}{6}$.
6. Go back: $\theta = \dfrac{7\pi}{12},\ \dfrac{11\pi}{12}$.

```python
my_roots = [7*pi/12, 11*pi/12]
```
""")

md(r"""
## Solution 10 — an extraneous root

1. The domain: $|3x| \le 1$ is needed, that is,
   $x \in \left[-\dfrac{1}{3}, \dfrac{1}{3}\right]$. That is worth writing out
   **before** solving.
2. Take the cosine of both sides. Let $A = \arccos x$, $B = \arccos 3x$:
   $$\cos(A + B) = \cos A\cos B - \sin A\sin B = \cos\frac{3\pi}{2} = 0.$$
3. Substitute $\cos A = x$, $\cos B = 3x$, $\sin A = \sqrt{1 - x^2}$,
   $\sin B = \sqrt{1 - 9x^2}$:
   $$3x^2 = \sqrt{(1 - x^2)(1 - 9x^2)}.$$
4. Square: $9x^4 = 1 - 10x^2 + 9x^4$, hence $x^2 = \dfrac{1}{10}$ and
   $x = \pm\dfrac{1}{\sqrt{10}}$. Both fall inside the domain from step 1.
5. **Check by substitution.** At $x = \dfrac{1}{\sqrt{10}}$:
   $\arccos(0.316) + \arccos(0.949) \approx 1.249 + 0.322 = \dfrac{\pi}{2}$ — does
   not work. At $x = -\dfrac{1}{\sqrt{10}}$:
   $\arccos(-0.316) + \arccos(-0.949) \approx 1.893 + 2.820 = \dfrac{3\pi}{2}$ —
   works.

$$\boxed{x = -\frac{1}{\sqrt{10}}}$$

```python
my_x = -1/sqrt(10)
```

Why the extraneous root appeared: at step 3 the left-hand side $3x^2$ is
non-negative, and squaring erases the sign and lets through the solution of
$\cos(A+B) = 0$ with the sum $\pi/2$ instead of $3\pi/2$.

Separately: the archive's own tags record the answer $x = \pm 1/2$ for this question.
That is wrong — at such an $x$ the quantity $\arccos 3x$ is not defined at all.
""")

md(r"""
## Solution 11 — a numerical solution

The equation $\theta = 2\sin\theta$ has no closed form. The root $\theta = 0$ is
obvious; the positive one is found numerically.

$$\theta = 1.89549\ldots \approx 1.90.$$

```python
my_theta = 1.8954942
```

The order of magnitude can be checked roughly: at $\theta = \pi/2 \approx 1.57$ the
right-hand side equals 2 and the left is smaller; at $\theta = 2$ the right equals
$2\sin 2 \approx 1.82$ and the left is larger. So the root is between them.
""")

md(r"""
## Solution 12 — the task on the timer

1. Using the given identity, replace the first three terms:
   $$2\sin x\,(\cos x - \sin x) + \cos x - \sin x = 0.$$
2. Take out the common factor $(\cos x - \sin x)$:
   $$(\cos x - \sin x)(2\sin x + 1) = 0.$$
3. The first factor: $\cos x = \sin x$, that is, $\tan x = 1$. On $(0, 2\pi)$ that
   is $x = \dfrac{\pi}{4}$ and $x = \dfrac{5\pi}{4}$.
4. The second factor: $\sin x = -\dfrac{1}{2}$. On $(0, 2\pi)$ that is
   $x = \dfrac{7\pi}{6}$ and $x = \dfrac{11\pi}{6}$.

```python
my_roots = [pi/4, 7*pi/6, 5*pi/4, 11*pi/6]
```

Three techniques work at once here: factorising, reducing to a tangent in the first
factor and the reference angle in the second. That is exactly how the topic appears
in Paper 1 — the identity is given in the previous part, and this one checks that
you can use it rather than derive it again.
""")

md(r"""
## Answers to the recognition trainer

1 `base` · 2 `arg` · 3 `pyth` · 4 `dbl` · 5 `fact` · 6 `tan` ·
7 `select` · 8 `gdc` · 9 `arg` · 10 `dbl` · 11 `select` · 12 `fact`

Two items are worth a word. The fifth is `fact`, not `dbl`: the identity
$\sin 2x = 2\sin x\cos x$ is used there, but not for the sake of a quadratic — for
the sake of a common factor. The seventh is `select`, even though it contains a
compound argument and a quadratic as well: the main thing in it is the fraction and
the caveat, and that is where the marks go.
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

out = (os.path.join(ROOT, 'practicum/geometry',
                       'practicum-c3-trigonometric-equations.ipynb'))
with open(out, 'w') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('cells:', len(cells), '->', out)
