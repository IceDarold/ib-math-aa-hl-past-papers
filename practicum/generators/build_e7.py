"""Собирает практикум E7 (дифференциальные уравнения) в формате .ipynb."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

x, y = sp.symbols('x y')

# --- ответы, из которых считаются хеши (в ноутбук попадают только хеши) ---
D_EULER = digest(sig(2.0980199, 4))          # 2.098
D_ERR = digest(sig(0.000478749, 3))          # 0.000479
D_EULER2 = digest(sig(10.6958, 3))           # 10.7
D_A = digest(sp.srepr(sp.simplify(sp.Integer(-4))))
D_B = digest(sp.srepr(sp.simplify(-4 - sp.pi)))
D_K = digest(sp.srepr(sp.simplify(sp.log(3)/5)))
D_M = digest('|'.join(sorted(sp.srepr(sp.simplify(m)) for m in [sp.sqrt(2), -sp.sqrt(2)])))

TRIGGER = {
    1: 'int', 2: 'sep', 3: 'if', 4: 'hom', 5: 'pf', 6: 'sep',
    7: 'if', 8: 'hom', 9: 'int', 10: 'eu', 11: 'pf', 12: 'sep',
}
TRIGGER_KEY = {i: digest(v) for i, v in TRIGGER.items()}

cells = []


def _lines(src):
    """nbformat: каждая строка source, кроме последней, оканчивается на \\n."""
    parts = src.strip('\n').split('\n')
    return [p + '\n' for p in parts[:-1]] + parts[-1:]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Practicum E7: first-order differential equations 🧮

This is not a retelling of the theory, it is a recognition trainer. In the exam a
differential equation is not solved by remembering the formula for the integrating
factor; it is solved because within a few seconds, from the shape of the right-hand
side, you know which of the seven techniques to switch on.

**Material.** 69 blocks and 275 marks from the AA HL archive, sessions May 2021 —
November 2025; 64 blocks and 255 marks of them are workable — November 2023 is a
duplicate, Paper 2 TZ1 and TZ2 turned out to be the same paper, and Paper 3 of that
session is shared. Every task below is a real past-paper question, cited. Workable
blocks by paper: Paper 1 — 9, Paper 2 — 32, Paper 3 — 23. The whole topic in a row,
with no theory, is in the archive notebook
`archive-e7-differential-equations.ipynb`: 37 questions and 255 marks.

**How to work**

1. Read the map of techniques. It is a ladder: each technique reduces to the
   previous one or widens it.
2. Solve the tasks **in order and on paper**. The cell is there only so that you can
   type in the answer you got.
3. Do not open the solutions until you have been stuck twice.
4. The checks store no reference answer: yours is substituted back into the original
   equation. So any correct form passes — as in the markscheme.
5. The last two blocks are a recognition trainer and one question on a timer.
   Come back to them in a week and in a month, writing the time into the log.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + exp, log, sqrt, Eq, diff and the other names

language('en')                 # this notebook is in English, and so are the checks

x, y, v, t, C = symbols('x y v t C')

print('ready; sympy', sp.__version__)
print('write the answer with the plain names: exp(1) =', exp(1))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | Reduces to |
| --- | --- | --- | --- |
| 1 | Direct integration | no $y$ on the right | — |
| 2 | Separation of variables | the right-hand side splits into $f(x)\,g(y)$ | 1 |
| 3 | Separation + partial fractions | after separating, the denominator factorises | 2 |
| 4 | Homogeneous, $y = vx$ | the right-hand side depends only on $y/x$ | 2 or 3 |
| 5 | Integrating factor | it rearranges to $y' + P(x)y = Q(x)$ | — |
| 6 | Euler's method | a step $h$ is given, an approximation is asked for | — |
| 7 | The sign of Euler's error | «is it an under- or an overestimate» | 6 |

Techniques 1–4 are one branch: each reduces the problem to the previous one.
Technique 5 stands apart: separation of variables fails in a linear equation,
because $Q(x)$ gets in the way of collecting $y$ on one side. Techniques 6–7 are the
numerical branch, and in the papers they almost always come as a pair: first compute,
then explain the sign of the error.

The main question you ask yourself on seeing an equation:
**does $y$ appear on the right-hand side, and if it does — does it separate from $x$?**
The three answers to that question give you techniques 1, 2 and 4–5.
""")

md(r"""
---
## Theory 1. What «solve» means, and where the constant goes

To solve $\dfrac{dy}{dx} = f(x, y)$ is to find a function that turns the equation into
an identity. Without an initial condition there is a family of such functions, and the
arbitrary constant is not a formality but the parameter of the family. The initial
condition picks one curve out of the family.

The order of work is rigid: **integrate first, substitute the condition afterwards.**
Substituting before integrating is the most common way of losing marks in this topic.

The simplest case: no $y$ on the right. Then the equation is not really differential
at all, it is an antiderivative problem.
""")

md(r"""
## Task 1 🟢 — direct integration

Solve $\dfrac{dy}{dx} = \cos\!\left(x - \dfrac{\pi}{4}\right)$ given that the curve
passes through the point $\left(\dfrac{3\pi}{4},\, 2\right)$. Give the answer in the
form $y = f(x)$.

*Source: November 2021, Paper 1, Q1 (4 marks, no calculator).*
""")

code(r"""
# your answer here: y as an expression in x
my_y = ...

verify_ode('Task 1', my_y, cos(x - pi/4), ic=(3*pi/4, 2))
""")

md(r"""
## Task 2 🟢 — separation in its pure form

Solve $\dfrac{dy}{dx} = -\dfrac{x}{y}$ and show that the family of curves has the form
$x^2 + y^2 = k$.

The answer here is implicit, and that is fine: the question does not ask you to make
$y$ explicit. Enter the answer as `Eq(left_hand_side, right_hand_side)`.

*Source: November 2023 TZ1, Paper 3, Q2(a)(iii) (2 marks).*
""")

code(r"""
K = Symbol('k')
my_family = ...          # for example Eq(x**2 + y**2, K)

verify_implicit('Task 2', my_family, Eq(x**2 + y**2, K))
""")

md(r"""
## Task 3 🟢 — separation with a logarithm

Solve $\dfrac{dy}{dx} = \dfrac{4 - y}{10}$ with $y(0) = 2$ and show that
$y = 4 - 2e^{-x/10}$.

Notice two things. First: the integral $\int \dfrac{dy}{4 - y}$ gives $-\ln|4-y|$, and
that minus sign is easy to lose. Second: the modulus comes off legitimately, because
the initial condition $y(0) = 2 < 4$ fixes the sign $4 - y > 0$, and by continuity it
is kept.

*Source: November 2023 TZ1, Paper 2, Q9(b) (5 marks). The same question is repeated
word for word in November 2023 TZ2 — a useful signal that the technique counts as a
load-bearing one.*
""")

code(r"""
my_y = ...

verify_ode('Task 3', my_y, (4 - y)/10, ic=(0, 2))
""")

md(r"""
---
## Theory 2. Separation of variables when the factor is hidden

Separation works if the right-hand side splits into a product $f(x)\,g(y)$. What makes
the exam versions hard is that the product is not visible straight away:

- $y\tan^2 x$ — already a product, but the integral in $x$ does not go through until
  the square is rewritten as $\sec^2 x - 1$;
- $\dfrac{x^2}{x - 1}\cdot y^3$ — the factor multiplying $y^3$ has to be divided out
  first, otherwise the integral in $x$ does not go through;
- $y\,(4 - y^2)$ — the product is there, but the integral in $y$ needs partial
  fractions, and that is already technique 3.

The general rule: separating the variables is half the job, and usually the easy half.
The hard part stands after the integral sign, and you have to look at it **before**
the variables are separated: if the integral will not go through, you should be looking
for another technique, not finding that out halfway through the working.

In other words, technique 2 is almost never tested on its own: behind it stands the
integration technique from practicum E5. Separation is only the first move.
""")

md(r"""
## Task 4 🟡 — separation plus a power reduction

Solve $\dfrac{dy}{dx} = y^2\cos^2 x$. The solution can be written in the form
$y = \dfrac{a}{2x + \sin 2x + b}$.

**(a)** Find $a$.
**(b)** Given that $y = 1$ when $x = \dfrac{\pi}{2}$, find $b$.

*Source: November 2025 TZ1, Paper 1, Q7 (6 + 2 marks, no calculator).*
""")

code(r"""
my_a = ...
my_b = ...

check_expr('Task 4(a), a', my_a, '""" + D_A + r"""')
check_expr('Task 4(b), b', my_b, '""" + D_B + r"""')

# the full check: the assembled solution must satisfy the equation and the condition
if my_a is not Ellipsis and my_b is not Ellipsis:
    verify_ode('Task 4, the whole solution',
               my_a/(2*x + sin(2*x) + my_b), y**2*cos(x)**2, ic=(pi/2, 1))
""")

md(r"""
---
## Theory 3. Partial fractions and the logistic model

When separation leaves a fraction on the left whose denominator factorises, the
integral goes through partial fractions and gives a **difference of logarithms**.
What has to come next is worth a mark of its own in the exam: the difference of
logarithms is collapsed into the logarithm of a ratio,

$$\ln|u| - \ln|w| = \ln\left|\frac{u}{w}\right|,$$

and only then does exponentiating give a meaningful answer. Whoever integrates but
does not collapse gets stuck halfway.

Here is the whole thing on the equation $\dfrac{dy}{dx} = y^2 - 4$:

$$\frac{1}{y^2-4} = \frac14\left(\frac{1}{y-2} - \frac{1}{y+2}\right)
\;\Longrightarrow\;
\frac14\ln\left|\frac{y-2}{y+2}\right| = x + c .$$

Split, integrate, **collapse into one logarithm** — and only now exponentiate.
The splitting is mechanical work; the mark is for putting the difference of
logarithms back together afterwards.

The same move serves growth models with a ceiling: there too the denominator
factorises into two linear factors, and the split is built the same way.
""")

md(r"""
## Task 5 🟡 — the logistic equation

A population is described by $\dfrac{dP}{dt} = \dfrac{kP(N - P)}{N}$, where $N$ is the
carrying capacity and $P = P_0$ at $t = 0$.

**(a)** Show that $kt = \ln\!\left[\dfrac{P}{N - P}\cdot\dfrac{N - P_0}{P_0}\right]$.

**(b)** Given that at $t = 10$ we have $P = 3P_0$ and $N = 4P_0$, find $k$.

Part (a) is a «show that», checked on paper: compare it with the solution.
Enter part (b) as an exact expression.

*Source: May 2022 TZ2, Paper 2, Q12(e)–(f) (7 + 2 marks).*
""")

code(r"""
my_k = ...            # an exact expression

check_expr('Task 5(b), k', my_k, '""" + D_K + r"""')
""")

md(r"""
---
## Theory 4. The homogeneous equation and the substitution $y = vx$

The right-hand side depends only on the ratio $y/x$ — numerator and denominator have
the same degree of homogeneity:

$$\frac{x^2 + y^2}{xy}, \qquad \frac{2y - 5x}{2x + 3y}, \qquad
\frac{y}{x} + \mathrm{e}^{\,y/x}.$$

The substitution $y = vx$ turns such an equation into a separable one. There is only
one place where people go wrong here — the product rule:

$$y = vx \;\Longrightarrow\; \frac{dy}{dx} = v + x\frac{dv}{dx}.$$

The term $v$ gets lost regularly. After the substitution the equation always
rearranges to $x\dfrac{dv}{dx} = h(v)$, that is, to technique 2 or 3. The last step is
the **substitution back**, $v = y/x$; an answer in terms of $v$ earns no marks.
""")

md(r"""
## Task 6 🟡 — a homogeneous equation

Solve $\dfrac{dy}{dx} = \dfrac{x - y}{x + y}$ with $y(2) = 0$, using the substitution
$y = vx$, and show that the solution has the form $x^2 - 2xy - y^2 = 4$.

*Source: May 2025 TZ1, Paper 1, Q9 (8 marks, no calculator).*
""")

code(r"""
my_curve = ...        # Eq(..., ...)

verify_implicit('Task 6', my_curve, Eq(x**2 - 2*x*y - y**2, 4))
""")

md(r"""
---
## Theory 5. The integrating factor

The equation is linear in $y$ if it rearranges to

$$\frac{dy}{dx} + P(x)\,y = Q(x).$$

The variables cannot be separated here: the term $Q(x)$ stops you collecting $y$ on
one side. The technique is to multiply through by $I(x) = e^{\int P\,dx}$, after which
the left-hand side becomes the derivative of a product:

$$I\frac{dy}{dx} + IP\,y = \frac{d}{dx}\bigl(I\,y\bigr),$$

because $I' = PI$ by construction. From there the equation integrates directly.

Three places where marks are lost:

1. The equation has not been put into the standard form, and the sign of $P(x)$ is
   taken wrongly. In $\dfrac{dy}{dx} - 3y = \mathrm{e}^{x}$ we have $P = -3$, not
   $+3$, and the factor is $\mathrm{e}^{-3x}$.
2. The right-hand side needs integration by parts, and that is where people stop.
3. The constant is brought in before the division by $I$: it has to stay outside,
   $y = \dfrac{1}{I}\left(\int IQ\,dx + C\right)$.

The factor is not always an exponential: in May 2024 TZ2 the integrating factor turns
out to be $\cot x$, because $e^{\frac{1}{2}\ln(\cot^2 x)} = \cot x$.
""")

md(r"""
## Task 7 🟡 — a linear equation

Solve $\dfrac{dy}{dx} - y = x$ with $y(0) = 2$. Give the answer in the form
$y = f(x)$.

*Source: May 2024 TZ1, Paper 2, Q7 (7 marks).*
""")

code(r"""
my_y = ...

verify_ode('Task 7', my_y, y + x, ic=(0, 2))
""")

md(r"""
## Task 8 🔴 — a linear equation with a polynomial on the right

Solve $\dfrac{dy}{dx} + y = x^2 - 5$ and show that the solution is written as
$y = x^2 - 2x - 3 + Ce^{-x}$.

There is no initial condition, so the constant stays in the answer — the check allows
for that. The integral $\int (x^2 - 5)e^{x}\,dx$ takes two integrations by parts.

*Source: May 2025 TZ3, Paper 2, Q12(b) (4 marks).*
""")

code(r"""
my_y = ...            # with the arbitrary constant C

verify_ode('Task 8', my_y, x**2 - 5 - y)
""")

md(r"""
---
## Theory 6. Euler's method and the sign of the error

The numerical branch. The iteration

$$y_{n+1} = y_n + h\,f(x_n, y_n)$$

walks along the tangent to the solution at the current point. Everything else that
gets asked follows from that.

**How many steps.** From $x_0$ to the target, exactly $(x_{\text{target}} - x_0)/h$
steps. Being out by one here costs every mark of the part.

**Rounding.** Intermediate values are not rounded — only the final one, and as a rule
to **significant figures**, not decimal places. The wordings «to 4 significant
figures» and «to 6 significant figures» turn up in this topic constantly.

**The sign of the error.** The tangent to a curve that is concave up lies **below**
it, so when $y'' > 0$ Euler's method **underestimates**. When $y'' < 0$ it
overestimates. In the exam it is not enough to name the answer: the mark is for
referring to the concavity or to the sign of the second derivative.

**A separate storyline — «why is the approximation poor».** That is not about the
sign, it is about the gradient changing sharply over the interval; such an
approximation is crude regardless of concavity.
""")

md(r"""
## Task 9 🔴 — Euler and the absolute error

Given $\dfrac{dy}{dx} = \dfrac{4 - y}{10}$ with $y(0) = 2$.

**(a)** Use Euler's method with step $h = 0.1$ to find an approximation to $y(0.5)$,
to four significant figures.
**(b)** You found the exact solution in Task 3. Find the absolute error of the
approximation, to three significant figures.
**(c)** Does the method under- or overestimate? Justify it.

*Source: November 2023 TZ1, Paper 2, Q9(a), (c) (3 + 1 marks).*
""")

code(r"""
# (a) work the table out on paper, here only compare
my_approx = ...

check_num('Task 9(a)', my_approx, 4, '""" + D_EULER + r"""')

# (b)
my_error = ...
check_num('Task 9(b)', my_error, 3, '""" + D_ERR + r"""')

# (c) write the answer in words for yourself; compare it with the solution at the end
""")

code(r"""
# once you have handed in (a): this is what the whole table looks like
for xi, yi in euler(lambda a, b: (4 - b)/10, 0.0, 2.0, 0.1, 5):
    print(f'x = {xi:.1f}   y = {yi:.7f}')
""")

md(r"""
## Task 10 🔴 — a whole exam chain

Given $\dfrac{dy}{dx} = \dfrac{y^2 - 2x^2}{x^2}$ with $y(1) = 3$.

**(a)** Use Euler's method with step $h = 0.1$ to find an approximation to $y(1.5)$,
to three significant figures.
**(b)** Show that the substitution $y = vx$ brings the equation to the form
$x\dfrac{dv}{dx} = v^2 - v - 2$.
**(c)** Solve the resulting equation and find the exact value of $y(1.5)$.
**(d)** Explain why the approximation in part (a) turned out to be so poor.

This is three techniques chained into one question: Euler, the homogeneous
substitution, partial fractions. That is exactly how the topic appears in Paper 2.
Part (d) is not about concavity: look at what happens to the solution as it
approaches $x = 1.5$.

*Source: May 2022 TZ1, Paper 2, Q12 (4 + 3 + 12 marks).*
""")

code(r"""
my_approx = ...

check_num('Task 10(a)', my_approx, 3, '""" + D_EULER2 + r"""')

# (b) check the substitution symbolically: put y = v(x)*x into both sides
vx = Function('v')(x)
left = diff(vx*x, x)
right = ((vx*x)**2 - 2*x**2)/x**2
print('after the substitution:', simplify(solve(Eq(left, right), diff(vx, x))[0]*x))
""")

md(r"""
---
## What the calculator does here, and what it does not

This topic is the opposite of trigonometric equations: **82% of the marks carry a
calculator**, and there are only six Paper 1 questions. But the role of the calculator
here is completely different, and counting on it as a solver is a mistake.

**It will not give you a closed form.** No GDC separates variables or builds an
integrating factor. Everything you did in tasks 1–8 has to be done by hand on any
paper.

**What it will do is check an answer in half a minute.** This is an underrated move
towards the end of the time: run Euler's method with a small step from the same
initial condition and compare it with your formula. If they agree in the first few
significant figures, the solution is almost certainly right.

Let us check somebody else's solution that way — not one from this practicum:
$\dfrac{dy}{dx} = y - x$ with $y(0) = 2$, answer $y = e^{x} + x + 1$.
""")

code(r"""
import math

my_solution = lambda t: math.exp(t) + t + 1            # the formula being checked
approx = euler(lambda a, b: b - a, 0.0, 2.0, 0.001, 1000)[-1][1]

print(f'Euler, step 0.001:  y(1) ~ {approx:.5f}')
print(f'your formula:       y(1) = {my_solution(1):.5f}')
print(f'difference:         {abs(approx - my_solution(1)):.5f}')
print('agrees to three significant figures — exactly the accuracy Paper 2 asks for'
      if abs(approx - my_solution(1)) < 0.01 else 'disagrees, look for the mistake')
""")

md(r"""
Euler's method is first order, so its error shrinks in proportion to the step, and you
should not expect every digit to agree. Agreement in three significant figures is
enough to catch a sign error, a lost term or a wrong constant.

**Where the calculator is completely useless.** Homogeneous equations with the
substitution $y = vx$: five of the seven questions in the archive are «show that»,
where the answer is already written in the question and the marks are for the
derivation. There the calculator helps with nothing at all.

**And where it is compulsory.** All seven Euler's method questions are Paper 2. The
iteration is convenient to enter as a recurrence or a table; do not round the
intermediate values, or the last significant figure will not come out.
""")

md(r"""
---
## Trainer: name the technique

Half the work in the exam is recognising the technique from the shape of the equation.
There are no computations here: for each equation, name the technique with one code.

| Code | Technique |
| --- | --- |
| `int` | direct integration |
| `sep` | separation of variables |
| `pf` | separation + partial fractions |
| `hom` | homogeneous, $y = vx$ |
| `if` | integrating factor |
| `eu` | Euler's method |

1. $\dfrac{dy}{dx} = \cos\!\left(x - \dfrac{\pi}{4}\right)$
2. $\dfrac{dy}{dx} = \dfrac{4 - y}{10}$
3. $\dfrac{dy}{dx} - y = x$
4. $\dfrac{dy}{dx} = \dfrac{y^2 - 2x^2}{xy}$
5. $\dfrac{dP}{dt} = \dfrac{kP(N - P)}{N}$
6. $\dfrac{dy}{dx} = y^2\cos^2 x$
7. $\dfrac{dy}{dx} + y = x^2 - 5$
8. $\dfrac{dy}{dx} = \dfrac{y - x}{y + x}$
9. $\dfrac{dP}{dt} = 104000\,e^{-0.0145t}$, find $P(4)$ given $P(0)$
10. $\dfrac{dy}{dx} = \dfrac{x + 2}{x + y}$, estimate $y(2)$ with step $0.25$ from the
    point $(1, 0)$
11. $x\dfrac{dv}{dx} = v^2 - v - 2$
12. $\dfrac{dy}{dx} = -\dfrac{x}{y}$

The target is 12 out of 12 in under two minutes.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## Task 11 🔴 — ON THE TIMER: 15 minutes

Close everything above. Paper 1 format, no calculator, 10 marks.

Consider $\dfrac{dy}{dx} = \dfrac{y^2 - 2x^2}{xy}$ for $x > 0$, with $y(1) = 2$.

**(a)** Using the substitution $y = vx$, show that $y^2 = 4x^2(1 - \ln x)$. *(8)*
**(b)** The tangent to the curve is horizontal at the point where $y = mx$. Find $m$.
*(2)*

The exam rate is about 1.5 minutes per mark, that is 15 minutes for the whole
question. Write the time of each attempt into the log below and come back to the task
in a week and in a month: the goal is not to solve it once but to make it automatic.

*Source: November 2022, Paper 1, Q9 (8 + 2 marks, no calculator).*
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

my_y = ...            # the explicit branch of the solution through (1, 2)
my_m = ...            # both values as a list, for example [sqrt(2), -sqrt(2)]

verify_ode('11(a)', my_y, (y**2 - 2*x**2)/(x*y), ic=(1, 2))

check_set('11(b)', my_m, '""" + D_M + r"""')
print(f'time spent: {(time.time() - t0)/60:.1f} min')
""")

md(r"""
---
# 🔑 Solutions

Each solution is the chain of steps that earns the marks. Check not only the answer
but that no step is missing: the markscheme pays for method.
""")

md(r"""
## Solution 1 — direct integration

There is no $y$ on the right, so this is an antiderivative problem.

1. $y = \int\cos\!\left(x - \frac{\pi}{4}\right)dx = \sin\!\left(x - \frac{\pi}{4}\right) + c$.
2. Substitute $\left(\frac{3\pi}{4}, 2\right)$: $\sin\frac{\pi}{2} + c = 2$, that is, $1 + c = 2$.
3. $c = 1$, hence $y = \sin\!\left(x - \frac{\pi}{4}\right) + 1$.

```python
my_y = sin(x - pi/4) + 1
```
""")

md(r"""
## Solution 2 — separation in its pure form

1. $y\,dy = -x\,dx$.
2. $\dfrac{y^2}{2} = -\dfrac{x^2}{2} + c$.
3. Multiply by 2: $x^2 + y^2 = k$, where $k = 2c$.

The answer is implicit and stays that way: this is a family of circles.

```python
my_family = Eq(x**2 + y**2, K)
```
""")

md(r"""
## Solution 3 — separation with a logarithm

1. $\displaystyle\int\frac{dy}{4 - y} = \int\frac{dx}{10}$.
2. $-\ln|4 - y| = \dfrac{x}{10} + c$.
3. The condition $(0, 2)$: $-\ln 2 = c$.
4. $\ln\left|\dfrac{4-y}{2}\right| = -\dfrac{x}{10}$, and since $y < 4$ the modulus comes off.
5. $4 - y = 2e^{-x/10}$, that is, $y = 4 - 2e^{-x/10}$.

```python
my_y = 4 - 2*exp(-x/10)
```
""")

md(r"""
## Solution 4 — separation plus a power reduction

1. $\displaystyle\int y^{-2}\,dy = \int\cos^2 x\,dx$.
2. On the left, $-\dfrac{1}{y}$. On the right, apply $\cos^2 x = \dfrac{1 + \cos 2x}{2}$:
   $\displaystyle\int\frac{1 + \cos 2x}{2}dx = \frac{1}{2}\left(x + \frac{\sin 2x}{2}\right) + c$.
3. $-\dfrac{1}{y} = \dfrac{2x + \sin 2x}{4} + c$.
4. Hence $y = \dfrac{-4}{2x + \sin 2x + 4c}$, so $a = -4$.
5. The condition $y\left(\frac{\pi}{2}\right) = 1$: $1 = \dfrac{-4}{\pi + 0 + b}$, hence $b = -4 - \pi$.

```python
my_a = -4
my_b = -4 - pi
```

The minus sign in $a$ is the place where this question sifts: lose the minus when
integrating $y^{-2}$ and everything afterwards still works out, with a wrong answer.
""")

md(r"""
## Solution 5 — the logistic equation

**(a)**

1. Separate: $\displaystyle\int\frac{N}{P(N - P)}\,dP = \int k\,dt$.
2. Partial fractions: $\dfrac{N}{P(N-P)} = \dfrac{1}{P} + \dfrac{1}{N - P}$.
3. Integrate: $\ln P - \ln(N - P) = kt + c$.
4. Collapse: $\ln\dfrac{P}{N - P} = kt + c$.
5. The condition $t = 0$, $P = P_0$: $c = \ln\dfrac{P_0}{N - P_0}$.
6. $kt = \ln\dfrac{P}{N-P} - \ln\dfrac{P_0}{N-P_0}
   = \ln\!\left[\dfrac{P}{N-P}\cdot\dfrac{N - P_0}{P_0}\right]$.

**(b)** Substitute $t = 10$, $P = 3P_0$, $N = 4P_0$:

$$10k = \ln\left[\frac{3P_0}{P_0}\cdot\frac{3P_0}{P_0}\right] = \ln 9,
\qquad k = \frac{\ln 9}{10} = \frac{\ln 3}{5}.$$

```python
my_k = log(3)/5
```
""")

md(r"""
## Solution 6 — a homogeneous equation

1. $y = vx$, so $\dfrac{dy}{dx} = v + x\dfrac{dv}{dx}$.
2. Substitute: $v + x\dfrac{dv}{dx} = \dfrac{x - vx}{x + vx} = \dfrac{1 - v}{1 + v}$.
3. $x\dfrac{dv}{dx} = \dfrac{1 - v}{1 + v} - v = \dfrac{1 - 2v - v^2}{1 + v}$.
4. Separate: $\dfrac{1 + v}{1 - 2v - v^2}\,dv = \dfrac{dx}{x}$.
5. The numerator on the left is half the derivative of the denominator with a minus
   sign: $\dfrac{d}{dv}(1 - 2v - v^2) = -2 - 2v$. Hence
   $-\dfrac{1}{2}\ln|1 - 2v - v^2| = \ln|x| + c$.
6. Exponentiate: $1 - 2v - v^2 = \dfrac{A}{x^2}$.
7. Substitute back $v = y/x$ and multiply by $x^2$: $x^2 - 2xy - y^2 = A$.
8. The condition $y(2) = 0$: $4 = A$, that is, $x^2 - 2xy - y^2 = 4$.

```python
my_curve = Eq(x**2 - 2*x*y - y**2, 4)
```

Step 5 is the one worth keeping the technique «the numerator is the derivative of the
denominator» in mind for: without it the integral goes off into partial fractions with
irrational roots, and the question stops being solvable in the time allowed.
""")

md(r"""
## Solution 7 — the integrating factor

1. Standard form: $\dfrac{dy}{dx} - y = x$, so $P = -1$, $Q = x$.
2. $I = e^{\int -1\,dx} = e^{-x}$.
3. Multiply through: $\dfrac{d}{dx}\left(y\,e^{-x}\right) = x e^{-x}$.
4. By parts: $\displaystyle\int x e^{-x}dx = -x e^{-x} - e^{-x} + C$.
5. $y e^{-x} = -(x + 1)e^{-x} + C$, hence $y = -(x+1) + Ce^{x}$.
6. The condition $y(0) = 2$: $-1 + C = 2$, that is, $C = 3$.
7. $y = 3e^{x} - x - 1$.

```python
my_y = 3*exp(x) - x - 1
```
""")

md(r"""
## Solution 8 — linear with a polynomial on the right

1. $P = 1$, $Q = x^2 - 5$, the factor is $I = e^{x}$.
2. $\dfrac{d}{dx}\left(y e^{x}\right) = (x^2 - 5)e^{x}$.
3. Twice by parts: $\displaystyle\int x^2 e^{x}dx = e^{x}(x^2 - 2x + 2)$, so
   $\displaystyle\int (x^2 - 5)e^{x}dx = e^{x}(x^2 - 2x - 3)$.
4. $y e^{x} = e^{x}(x^2 - 2x - 3) + C$.
5. Divide by $e^x$; the constant stays outside: $y = x^2 - 2x - 3 + Ce^{-x}$.

```python
my_y = x**2 - 2*x - 3 + C*exp(-x)
```
""")

md(r"""
## Solution 9 — Euler and the absolute error

**(a)** The iteration $y_{n+1} = y_n + 0.1\cdot\dfrac{4 - y_n}{10}$ from $(0, 2)$,
five steps to $x = 0.5$:

| $x$ | $y$ |
| --- | --- |
| 0.0 | 2 |
| 0.1 | 2.02 |
| 0.2 | 2.0398 |
| 0.3 | 2.059404 |
| 0.4 | 2.078810 |
| 0.5 | 2.098022 |

Answer: $2.098$ (4 s.f.).

**(b)** The exact value is $y(0.5) = 4 - 2e^{-0.05} = 2.0975435\ldots$
The absolute error is $|2.0980199 - 2.0975435| = 0.000479$.

**(c)** $y'' = -\dfrac{1}{100}(4 - y) < 0$ when $y < 4$, the curve is concave down and
the tangents lie above it — the method **overestimates**. That agrees with the
approximation coming out larger than the exact value.

```python
my_approx = 2.0980199
my_error  = 0.000478749
```
""")

md(r"""
## Solution 10 — a whole exam chain

**(a)** $y_{n+1} = y_n + 0.1\cdot\dfrac{y_n^2 - 2x_n^2}{x_n^2}$ from $(1, 3)$:
$3.7 \to 4.6314 \to 5.9210 \to 7.7954 \to 10.6958$. Answer $10.7$.

**(b)** $y = vx$, $\dfrac{dy}{dx} = v + x\dfrac{dv}{dx}$, and the right-hand side is
$\dfrac{v^2x^2 - 2x^2}{x^2} = v^2 - 2$. Hence $x\dfrac{dv}{dx} = v^2 - 2 - v$, that
is, $x\dfrac{dv}{dx} = v^2 - v - 2$.

**(c)** The denominator factorises: $v^2 - v - 2 = (v - 2)(v + 1)$.

1. $\dfrac{dv}{(v-2)(v+1)} = \dfrac{dx}{x}$.
2. Partial fractions: $\dfrac{1}{(v-2)(v+1)} = \dfrac{1}{3}\left(\dfrac{1}{v-2} - \dfrac{1}{v+1}\right)$.
3. $\dfrac{1}{3}\left(\ln|v-2| - \ln|v+1|\right) = \ln|x| + c$.
4. The condition: at $x = 1$ we have $y = 3$, so $v = 3$, and $\dfrac{1}{3}\ln\dfrac{1}{4} = c$.
5. Collapse and exponentiate: $\dfrac{v - 2}{v + 1} = \dfrac{x^3}{4}$.
6. Go back to $v = y/x$ and make $y$ explicit.

**(d)** The solution has a vertical asymptote near $x = 1.5$: as
$\dfrac{v-2}{v+1} \to 1$ the denominator goes to zero. The gradient grows without
bound, and a step of $0.1$ along the tangent cannot keep up with the curve. This is
**not** a question about the sign of the error — here it is the speed at which the
gradient changes, not the concavity.
""")

md(r"""
## Solution 11 — the task on the timer

**(a)**

1. $y = vx$, $\dfrac{dy}{dx} = v + x\dfrac{dv}{dx}$.
2. The right-hand side: $\dfrac{v^2x^2 - 2x^2}{x\cdot vx} = \dfrac{v^2 - 2}{v}$.
3. $x\dfrac{dv}{dx} = \dfrac{v^2 - 2}{v} - v = -\dfrac{2}{v}$.
4. Separate: $v\,dv = -\dfrac{2}{x}\,dx$.
5. $\dfrac{v^2}{2} = -2\ln x + c$.
6. The condition $y(1) = 2$ gives $v = 2$: $2 = c$.
7. $\dfrac{v^2}{2} = 2 - 2\ln x$, so $v^2 = 4(1 - \ln x)$.
8. Substitute back $v = y/x$: $y^2 = 4x^2(1 - \ln x)$.

**(b)** The tangent is horizontal where $\dfrac{dy}{dx} = 0$, that is, where the
numerator vanishes: $y^2 - 2x^2 = 0$, hence $y = \pm\sqrt{2}\,x$ and $m = \pm\sqrt{2}$.

Part (b) takes half a minute and does not need the result of (a) — in the exam you
take it first if time is short.

```python
my_y = 2*x*sqrt(1 - log(x))
my_m = [sqrt(2), -sqrt(2)]
```
""")

md(r"""
## Answers to the trainer

1 `int` · 2 `sep` · 3 `if` · 4 `hom` · 5 `pf` · 6 `sep` ·
7 `if` · 8 `hom` · 9 `int` · 10 `eu` · 11 `pf` · 12 `sep`

Item 6 is worth a word of its own: it is `sep`, not `pf`, even though the integral on
the right needs a power reduction. Partial fractions are needed when the fraction
appears **on the left**, in the variable $y$. Item 11 is already the result of the
substitution $y = vx$ from item 4: that is how the topic is built, the techniques nest
inside one another.
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

out = os.path.join(ROOT, 'practicum/calculus',
                   'practicum-e7-differential-equations.ipynb')
with open(out, 'w') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('cells:', len(cells), '->', out)
