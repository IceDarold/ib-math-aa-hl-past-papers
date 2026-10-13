"""Собирает практикум B1 (уравнения) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

sq = sp.sqrt
R = sp.Rational
x, y, k, n, u = sp.symbols('x y k n u')
a, b, c, d, m, p, q, s, w = sp.symbols('a b c d m p q s w')


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_b1.py ---
D_Y1 = dn(R(3, 2))
D_P3 = dn(-1)
D_P4, D_B4, D_C4 = dn(R(9, 2)), dn(-4), dn(R(-9, 4))
D_B7 = dset([5, 6, 8, 12])
D_N7 = dn(2)
D_X13 = dn(5.56619, 3)
D_T13, D_G13 = dn(3.34881, 3), dn(22.2444, 3)
D_QP19 = de(2 * sp.sqrt(10))
D_M14 = dset([-1 - 2 * sq(2), -1 + 2 * sq(2)])

TRIGGER = {1: 'zero', 2: 'quad', 3: 'explog', 4: 'disc', 5: 'extra',
           6: 'meet', 7: 'count', 8: 'form', 9: 'gdc', 10: 'quad',
           11: 'extra', 12: 'disc', 13: 'explog', 14: 'count', 15: 'meet'}
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
# Practicum B1: equations

**222 marks, 73 blocks, nine techniques.** The largest topic of the archive after
differential equations — and the least conspicuous: a question rarely calls itself
by this name, yet an equation is solved in almost every one.

**Material.** 73 blocks and 222 marks from the AA HL archive, sessions May 2021 —
November 2025 (six of those marks are one and the same November 2023 question, which
made it into the corpus twice). Every task below is a real past-paper question,
cited.

**The main idea of the topic.** More often than not the equation is not given but
**built**: half the marks of the topic are earned before the solving begins. «Show
that the $x$-coordinates satisfy $x^2 - 2dx + 9d = 0$» is four marks, and not one of
them is for the roots.

The second half of the idea is about the roots themselves. Solving an equation is a
chain of steps, and not every step is an equivalence:

* squaring both sides, multiplying by a denominator, «removing the logarithms» —
  roots are **added**;
* dividing both sides by an expression with the variable — roots are **lost**;
* the domain from the question ($x>4$, $s>0$, $q \ne 0$) throws out the surplus at
  the very end, and there is a separate mark for it.

Hence how the practicum is built. Techniques 1–2 solve what is already written as an
equation. Techniques 3–6 build the equation: out of the question's situation, out of
an intersection of graphs, out of a substitution. Techniques 7–9 turn the question
round: the equation is given with a letter, and what is asked is for which values of
the letter it has a given number of roots.

**How to work**

1. Read the map of techniques. Telling «solve» from «build» matters more than
   remembering any single technique.
2. Work **on paper**. Enter the exact answer: `sqrt(17)`, `Rational(9, 2)`,
   `-1 + 2*sqrt(2)` — rounding only where the question says «3 s.f.».
3. Enter roots **as a complete list**: `[4]`, `[10 - sqrt(10), 10 + sqrt(10)]`. The
   check looks both for extra ones and for lost ones.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + solveset, Interval, real_roots

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d = symbols('a b c d')
m, p, q, s, w = symbols('m p q s w')

print('ready; sympy', sp.__version__)
print('solve an equation:     ', solveset(x**2 - 20*x + 90, x, S.Reals))
print('the same, but x > 10:  ', solveset(x**2 - 20*x + 90, x, Interval.open(10, oo)))
print('an equation as answer: ', Eq(x**2 - (m + 1)*x + 2, 0))
print('how many roots:        ', len(solveset(x**2 - 4*x + 4, x, S.Reals)))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | A zero of a function | «find the zero», «where the graph crosses the axes» | set the numerator to zero, put $x=0$ |
| 2 | A quadratic | «in the form $a(x-h)^2+k$», «vertex», «axis of symmetry» | complete the square or take the mean of the roots |
| 3 | Build the equation | «show that … satisfies …», «hence show that» | write both quantities and equate them |
| 4 | Extra and lost roots | a fraction, a root, a logarithm, a domain in the question | after solving, put every root back in |
| 5 | A substitution and the log laws | $a^{2x}$ next to $a^x$, several logarithms | put $a^x=A$, bring the logarithms to one base |
| 6 | An intersection of graphs | «meet», «intersect», «the line and the curve» | equate the right-hand sides and reduce to zero |
| 7 | Numerically, on the GDC | Paper 2, ugly numbers, «3 s.f.» | draw both sides and take the intersection |
| 8 | The discriminant as a condition | «tangent», «exactly one solution», «two distinct» | $\Delta$ in the letter, then the sign |
| 9 | The number of solutions | «how many solutions», «exactly two intercepts» | find where the roots merge or disappear |

The ladder goes by **what exactly is given**. Techniques 1–2 work with an equation
already written: that is the easiest quarter of the topic and almost all of its
Paper 1 in the easy questions.

Techniques 3–6 are the heart of the topic. There is no equation in the question,
there is a situation: the area equals the perimeter, the vertex lies on a line, two
curves meet. The work is in writing the equation down, bringing it to standard form
and not losing roots along the way.

Techniques 7–9 turn the question round. The equation is given with a letter and the
roots do not have to be found — what has to be understood is how many there are and
when. The answer here is a set of values of the letter, and from there everything
from A8 applies.

**What saves the most time.** Before solving, look at whether solving is being
asked for. «Show that», «hence show», «find the value of $k$ such that» are three
different questions, and the roots are only needed in the first.
""")

md(r"""
---
## Theory 1. A zero of a function and the intercepts

The most frequent question in the topic and the shortest. Two different questions
that are easy to confuse:

$$\text{the } y\text{-intercept}: \quad x = 0, \ \text{evaluate } f(0);$$
$$\text{the } x\text{-intercepts}: \quad f(x) = 0, \ \text{solve.}$$

For a fraction $f(x) = \dfrac{u(x)}{v(x)}$ the rule is: the fraction equals zero if
and only if **the numerator is zero and the denominator is not**. So $f(x)=0$ is
solved as $u(x)=0$, and every root found has to be checked against the denominator.

**Careful with the form of the answer.** «Find the zero» expects a number, «find the
coordinates» a pair. The mark for $(3, 0)$ will not be given to somebody who wrote 3,
if the question says coordinates.
""")

md(r"""
## Task 1 🟢 — zeros and intercepts

**(a)** Find the zero of the function $f(x) = \dfrac{7x+7}{2x-4}$.

**(b)** For the function $g(x) = 1 - \dfrac{1}{x-2}$, find the coordinates of the
points where the graph meets the axes.

*Sources: May 2023 TZ1, Paper 1, Q1(a) (2 marks) and May 2023 TZ2, Paper 1, Q1(b)
(2 marks), both no calculator.*
""")

code(r"""
my1a = [...]             # the zeros of f, as a list
my1b_x = [...]           # the x-coordinates where g meets the x-axis
my1b_y = ...             # the y-coordinate where g meets the y-axis

verify_root_set('Task 1(a)', my1a, (7*x + 7)/(2*x - 4))
verify_root_set('Task 1(b), the x-axis', my1b_x, 1 - 1/(x - 2))
check_num('Task 1(b), the y-axis', my1b_y, 6, '""" + D_Y1 + r"""')
""")

md(r"""
---
## Theory 2. A quadratic: four writings of one thing

A quadratic is written in four ways, and each question wants its own:

$$ax^2+bx+c \quad\text{(the coefficients)}, \qquad
a(x-h)^2+k \quad\text{(the vertex)},$$
$$a(x-x_1)(x-x_2) \quad\text{(the roots)}, \qquad
\Delta = b^2-4ac \quad\text{(how many roots)}.$$

Moving between them is the technique:

| What is asked | Which writing answers it |
| --- | --- |
| the vertex, the greatest or least value | $a(x-h)^2+k$ |
| the axis of symmetry | $x = h = -\dfrac{b}{2a}$ = the mean of the roots |
| the roots, the $x$-intercepts | $a(x-x_1)(x-x_2)$ |
| how many roots, a touching | $\Delta$ |

**The axis of symmetry is the mean of the roots.** That is the most underrated fact
of the topic: it lets you find the second root from the first and the vertex, with no
solving at all. If the roots are $3$ and $p$ and the axis of symmetry is $x=-1$, then
$\frac{3 + p}{2} = -1$, hence $p = -5$ — one line instead of factorising.

**Completing the square is a requirement on the writing.** «Write in the form
$a(x-h)^2+k$» checks not the value but the form: the answer $2x^2-12x+7$ is
numerically equal to $2(x-3)^2-11$, but it earns no mark. Inside the square there has
to be exactly $(x-h)$, with a one in front of $x$.
""")

md(r"""
## Task 2 🟢 — the vertex form

Write $f(x) = 5(x+1)(x+3)$ in the form $a(x-h)^2+k$.

The check looks at the form of the writing, not only at the equality: an expanded
bracket is numerically equal to the answer but is not the form.

*Source: May 2025 TZ1, Paper 1, Q10(a) (4 marks, no calculator).*
""")

code(r"""
my2 = ...                # f(x) in the form a(x - h)^2 + k

verify_vertex_form('Task 2', my2, 5*(x + 1)*(x + 3))
""")

md(r"""
## Task 3 🟡 — a vertex on a line

The functions are given by

$$f(x) = -x^2+4x+p, \qquad g(x) = x^2+qx-1,$$

where $p$ and $q$ are **non-zero** constants. The vertex of the graph of $f$ is the
point $A$, the vertex of the graph of $g$ is the point $B$, and both lie on the line
$y = 2x-1$.

**(a)** Show that $p = -1$.

**(b)** Find the value of $q$.

In part (b) a quadratic in $q$ comes out, and one of its two roots does not go into
the answer. Think about which condition of the question throws it out — and why
without that condition it would have been perfectly legitimate.

*Source: November 2025 TZ1, Paper 1, Q4 (3 + 5 marks, no calculator).*
""")

code(r"""
my3_p = ...              # the value of p
my3_q = [...]            # the values of q, as a list

check_num('Task 3(a)', my3_p, 6, '""" + D_P3 + r"""')
verify_root_set('Task 3(b)', my3_q, q**2 - 4*q, var=q,
                domain=Complement(S.Reals, FiniteSet(0)))
""")

md(r"""
## Task 4 🟡 — from the roots and the axis of symmetry

The function $g(x) = x^2+bx+c$ has a graph symmetric about the line $x = 2$, and the
roots of $g(x)=0$ are $-\frac12$ and $p$.

**(a)** Show that $p = \frac92$.

**(b)** Find $b$ and $c$.

*Source: May 2024 TZ1, Paper 1, Q10(c)(d) (1 + 3 marks, no calculator).*
""")

code(r"""
my4_p = ...              # the second root
my4_b = ...              # the coefficient of x
my4_c = ...              # the constant term

check_num('Task 4(a)', my4_p, 6, '""" + D_P4 + r"""')
check_num('Task 4(b), b', my4_b, 6, '""" + D_B4 + r"""')
check_num('Task 4(b), c', my4_c, 6, '""" + D_C4 + r"""')
""")

md(r"""
---
## Theory 3. The equation that has to be built

Here the real topic begins. There is no equation in the question — there is a
situation, and the first move is to write two quantities down and equate them.

The format of the question is almost always the same: **«show that»**. The answer is
printed in the question, and the marks are for the road to it. Of the seven marks of
a typical such part, not one is for the roots.

**What the road looks like.**

1. Write both quantities separately — for a rectangle with sides $a$ and $b$ that is
   $A = ab$ and $P = 2a+2b$ — an A1 for that, sometimes A1A1.
2. Equate them — M1.
3. Bring it to the form given in the question — a chain of M1s, one for each
   substantial step.
4. Write what was required and stop — the last A1, and it is **not** given if the
   answer from the question is simply written down.

**About AG.** The answer is given, so the examiner reads only the working. The rule
is simple: if what is printed does not follow from your lines, there are no marks,
even when the last line matches the question word for word.

**Careful: bringing it to the required form can also fail to be an equivalence.**
Multiplying both sides by a bracket with a letter in it allows the case where that
bracket is zero — and in the original writing there was no such case. In the exam
that is rarely penalised, but in the check below the equations are compared honestly:
moving terms and a **numerical** factor are allowed, a factor with a letter is not.
""")

md(r"""
## Task 5 🟢 — the area equals the perimeter

For a square of side $s$ the numerical value of the area equals the numerical value
of the perimeter. Find $s$.

The equation comes out in two lines. The whole substance of the task is what to do
with the second root.

*Source: May 2021 TZ1, Paper 3, Q2(a) (3 marks, calculator).*
""")

code(r"""
my5 = [...]              # the values of s, as a list

verify_root_set('Task 5', my5, Eq(s**2, 4*s), var=s,
                domain=Interval.open(0, oo))
""")

md(r"""
## Task 6 🔴 — the same for a right-angled triangle

A right-angled triangle has legs $a$ and $b$ and hypotenuse $\sqrt{a^2+b^2}$, and
again the area is numerically equal to the perimeter.

**(a)** Equating the area and the perimeter, isolate the root and square both sides.
Write down the resulting equation (everything on one side, zero on the other).

**(b)** Show that $a = \dfrac{8}{b-4} + 4$.

Between (a) and (b) stands the step this task is here for: both sides are divided by
$ab$. That is a division by an expression with the variables, and it is legitimate
only because $a>0$ and $b>0$ — otherwise that is how roots get lost.

*Source: May 2021 TZ1, Paper 3, Q2(f) (7 marks, calculator).*
""")

code(r"""
my6_sq = ...             # the equation after squaring
my6_a = ...              # the expression for a in terms of b

verify_equation('Task 6(a)', my6_sq,
                a**2*b**2/4 - a**2*b - a*b**2 + 2*a*b, var=a)
verify_identity('Task 6(b)', my6_a, 8/(b - 4) + 4, var=b)
""")

md(r"""
---
## Theory 4. Extra and lost roots

Solving an equation is a chain of steps, and not every step is an equivalence. A
table worth keeping in your head whole:

| Step | What happens to the roots | What to do |
| --- | --- | --- |
| square both sides | they are added | put every root into the original |
| multiply by a denominator | the zeros of the denominator are added | check that the denominator is not zero |
| «remove» the logarithms | the ones where the argument was $\le 0$ are added | check the domain |
| divide by an expression with $x$ | they are **lost** | take out a factor, do not divide |
| raise to an even power | they are added | the same as with squaring |

The first three mistakes show up on substituting, the last one does not: a lost root
leaves no trace, and the only way to notice it is not to do the division at all.

**The rule.** Instead of «divide both sides by $t$» in the equation $t^2 = 6t$ write
$t^2-6t=0$, $t(t-6)=0$, and both roots, $0$ and $6$, are there. Then look at which
of them satisfies the question.

**The domain is part of the equation.** $x>4$, $s>0$, $q\ne0$ are in the question not
for decoration: almost always it is exactly they that throw out the extra root, and
there is a separate A1 for it. And it is the domain that throws it out, not the
algebra: the root is legitimate in itself, it is simply not about this question.
""")

md(r"""
## Task 7 🟡 — the integer solutions of a rational equation

A continuation of task 6: $a = \dfrac{8}{b-4} + 4$, with the sides $a$ and $b$
positive integers.

**(a)** Find all the integers $b$ for which $a$ is an integer too and both sides are
positive.

**(b)** How many **different** right-angled triangles does that give?

The difference between (a) and (b) is the substance of the task.

*Source: May 2021 TZ1, Paper 3, Q2(g)(i) (3 marks, calculator).*
""")

code(r"""
my7_b = [...]            # all the integers b that work
my7_n = ...              # how many different triangles

check_set('Task 7(a)', my7_b, '""" + D_B7 + r"""')
check_num('Task 7(b)', my7_n, 6, '""" + D_N7 + r"""')
""")

md(r"""
## Task 8 🟡 — a logarithm and its domain

The graph of $f(x) = \ln(x^2-16)$ meets the $x$-axis at the point $A(\alpha, 0)$,
where $x > 4$. Find the exact value of $\alpha$.

*Source: May 2021 TZ2, Paper 1, Q4(a) (3 marks, no calculator).*
""")

code(r"""
my8 = [...]              # the values of alpha, as a list

verify_root_set('Task 8', my8, log(x**2 - 16),
                domain=Interval.open(4, oo))
""")

md(r"""
---
## Theory 5. A substitution and the log laws

Exponential and logarithmic equations are solved not as exponential ones but as
**algebraic ones after a substitution**. Two cases cover almost the whole archive.

**Quadratic in $a^x$.** If the equation contains $a^{2x}$ (which is $(a^2)^x$) and
$a^x$, the substitution $A = a^x$ turns it into a quadratic:

$$4^x - 6\cdot 2^x + 8 = 0 \ \Longrightarrow\
A^2-6A+8=0, \quad A = 2^x > 0.$$

The condition $A>0$ here is not a formality but half the task: a negative root of the
quadratic is discarded **before** going back to $x$.

**One logarithm on the left, one on the right.** The logarithms are collected into
one on each side and the arguments are equated:

$$\log_a M = \log_a N \iff M = N \ \ (M, N > 0).$$

The tools for the collecting are three laws and the change of base:

$$\log_a M^n = n\log_a M, \quad
\log_a M + \log_a N = \log_a MN, \quad
\log_a M - \log_a N = \log_a \tfrac MN,$$
$$\log_a b = \frac{\log_c b}{\log_c a}, \qquad
\text{in particular } \frac{1}{\log_b a} = \log_a b.$$

The last formula is the most useful and the least conspicuous: the fraction
$\frac{3}{\log_5 2}$ is $3\log_2 5$, that is, $\log_2 125$, that is, a term that can
be taken under a common logarithm. Whenever a logarithm stands **in a denominator**,
look at it that way: it is most likely a rearranged base rather than a fraction.

**The domain.** «Removing the logarithms» is not an equivalence: it forgets that the
arguments were positive. So at the end the roots are put back in.
""")

md(r"""
## Task 9 🟢 — quadratic in $3^x$

Solve the equation

$$3 \cdot 9^x + 5 \cdot 3^x - 2 = 0.$$

*Source: May 2024 TZ2, Paper 1, Q2 (5 marks, no calculator).*
""")

code(r"""
my9 = [...]              # the solutions, as a list

verify_root_set('Task 9', my9, 3*9**x + 5*3**x - 2)
""")

md(r"""
## Task 10 🔴 — three log laws in a row

Solve the equation

$$\log_3 \sqrt{x} = \frac{1}{2\log_2 3} + \log_3 (4x^3), \qquad x > 0.$$

Three of the five marks here are for three separate actions: the change of base,
taking the exponent out, combining the logarithms. Start with the fraction.

*Source: November 2021, Paper 1, Q3 (5 marks, no calculator).*
""")

code(r"""
my10 = [...]             # the solutions, as a list

verify_root_set('Task 10', my10,
                log(sqrt(x), 3) - 1/(2*log(3, 2)) - log(4*x**3, 3),
                domain=Interval.open(0, oo))
""")

md(r"""
---
## Theory 6. An intersection of graphs

«The line and the curve meet», «the graphs intersect» — that is always one and the
same equation:

$$f(x) = g(x) \iff f(x) - g(x) = 0.$$

What comes next depends on what is asked:

| The question | What to do |
| --- | --- |
| «show that they meet when $\ldots=0$» | bring it to the required form and stop |
| «find the points of intersection» | solve and **give $y$ back**: the answer is coordinates |
| «find the value of $k$ such that they are tangent» | $\Delta=0$, technique 8 |
| «how many points of intersection» | technique 9 |

**Two traps of the format.** The first: stopping at $x$ when the points are asked
for. The second: solving the wrong equation — «$f$ and $g$ meet on the $x$-axis»
means not $f=g$ but $f=0$ and $g=0$ at once.

**About equivalence.** Bringing $f=g$ to standard form is moving terms, and it is
safe. The danger starts where both sides are multiplied by a denominator: in
$\frac{x+1}{x-3} = kx$, after multiplying, the root $x=3$ appears, which the original
equation does not have — there that point is excluded altogether.
""")

md(r"""
## Task 11 🟡 — a «show that» about an intersection

The curve $y = x^2-x-1$ and the line $y = mx-3$ meet. Show that at the points of
intersection

$$x^2 - (m+1)x + 2 = 0.$$

Enter the whole equation: `Eq(left-hand side, right-hand side)`, or simply the
expression that is set equal to zero.

*Source: May 2025 TZ3, Paper 1, Q4(a) (2 marks, no calculator).*
""")

code(r"""
my11 = ...               # the equation of the points of intersection

verify_equation('Task 11', my11, x**2 - (m + 1)*x + 2)
""")

md(r"""
## Task 12 🔴 — two families of curves

One family of curves is given by $y^2 = 4a^2-4ax$ and a second by
$y^2 = 4b^2+4bx$, where $a$ and $b$ are positive.

Solving these equations simultaneously, show that the curves meet at the points
$M(a-b,\ 2\sqrt{ab})$ and $N(a-b,\ -2\sqrt{ab})$.

The first move is to equate the right-hand sides: $y^2$ is the same, so the
expressions on the right are the same too. After that only $x$ is left in the
equation.

*Source: November 2023, Paper 3, Q2(c) (6 marks, calculator; the same question
appears in both time zones).*
""")

code(r"""
my12_x = ...             # the common x-coordinate of M and N
my12_y = ...             # the y-coordinate of M (the positive one)

check_expr('Task 12, x', my12_x, '""" + de(a - b) + r"""')
check_expr('Task 12, y', my12_y, '""" + de(2 * sq(a * b)) + r"""')
""")

md(r"""
---
## Theory 7. A numerical solution: what a GDC can and cannot do

On Paper 2 the equation most often does not solve by hand at all: an exponential
against a polynomial, a sine against a line, the difference of two models. The
technique is one: draw both sides and take the intersection — or type it into the
solver and get a root.

**Three things a GDC does not do for you.**

1. **Choosing the root.** An equation from a model almost always has several
   solutions, and one of them fits the meaning: «the first time»,
   «$0 \le t \le 6$», «$x>0$». The domain in the question is part of the task.
2. **Accuracy.** The answer is written to three significant figures, but
   intermediate values in later parts are taken unrounded. Round early and you lose
   an A1 in the next part, not in this one.
3. **Writing the method down.** «Solutions found from a graphic display calculator
   should be supported by suitable working» — the equation you solved and at least a
   sketch have to be left on the paper. A bare answer earns no M1.

**What not to do.** Typing into the GDC what can be done in your head. A quadratic
with integer roots, $\ln(x^2-16)=0$, $3^x = \frac13$ — all of that is faster by hand,
and on Paper 1 there is no calculator at all.
""")

md(r"""
## Task 13 🟢 — two numerical solutions

**(a)** The curve $f(x) = 90e^{-0.5x}$ meets the line $y = x$ at the point $P$. Find
the $x$-coordinate of $P$ to three significant figures.

**(b)** A tortoise crawls south from a point $A$, and its distance is described by
the function $g(t) = 0.05t^2 + 1.1t + 18$. The edge of the water is described by the
function

$$d(t) = \frac{20\sin\frac{\pi t}{8}}{\sin\left(2.37 - \frac{\pi t}{8}\right)}.$$

Find the time $t$ at which the water first reaches the tortoise, and the distance
from $A$ at which that happens. Both answers to three significant figures.

*Sources: May 2021 TZ1, Paper 2, Q10(a) (2 marks) and May 2024 TZ2, Paper 2, Q11(g)
(4 marks), both calculator papers.*
""")

code(r"""
my13_x = ...             # the x-coordinate of the intersection
my13_t = ...             # the time of the meeting, s
my13_g = ...             # the distance from A, m

check_num('Task 13(a)', my13_x, 3, '""" + D_X13 + r"""')
check_num('Task 13(b), the time', my13_t, 3, '""" + D_T13 + r"""')
check_num('Task 13(b), the place', my13_g, 3, '""" + D_G13 + r"""')
""")

md(r"""
---
## Theory 8. The discriminant as a condition on a letter

Here the topic turns round. Until now the equation was being solved; now its roots
are not needed at all — what is needed is how many there are. For a quadratic
everything is visible from the discriminant:

$$\Delta > 0 \iff \text{two distinct roots}, \qquad
\Delta = 0 \iff \text{one}, \qquad
\Delta < 0 \iff \text{none}.$$

After that $\Delta$ is an expression in the letter, and what comes out is an
equation or an inequality **in the letter**, that is, the work of A8.

**How the condition sounds in a question.**

| In the question | The condition on $\Delta$ |
| --- | --- |
| two distinct real roots · meets the curve twice | $\Delta>0$ |
| tangent to the curve · touches · exactly one solution | $\Delta=0$ |
| does not meet · no real solutions | $\Delta<0$ |
| at least one real solution | $\Delta\ge0$ |

**Three caveats, each worth a mark.**

1. **The equation has to be quadratic.** If the leading coefficient contains the
   letter, the case where it is zero is treated separately: the equation becomes
   linear and has exactly one root.
2. **A substitution narrows the domain.** After the substitution $A=a^x$ the roots
   come out for $A$, while they are wanted for $x$ — and only positive $A$ will do.
   If a logarithm of the letter stands in the coefficients, it demands the positivity
   of its own argument separately. The discriminant knows about neither, and both
   restrictions have to be added by hand.
3. **«Exactly one solution» and «$\Delta=0$» are not the same thing.** An equation
   with a fraction can lose a root at a pole, and one with a substitution can lose it
   on the way back to $x$. What has to be counted are the solutions of the original
   problem.

The checks in this section are built accordingly: they do not compute a discriminant
but take your set of values of the letter and at every test point ask the equation
itself how many solutions it has.
""")

md(r"""
## Task 14 🟡 — a tangent

A continuation of task 11: the curve $y = x^2-x-1$, the line $y = mx-3$, and at the
points of intersection $x^2-(m+1)x+2=0$.

Find all the values of $m$ for which the line is tangent to the curve.

There are two checks here, and that is not duplication. The first takes each of your
values and asks the equation how many roots it has — but sampling cannot notice a
**missing** isolated value, least of all an irrational one. The second compares the
set as a whole.

*Source: May 2025 TZ3, Paper 1, Q4(b) (5 marks, no calculator).*
""")

code(r"""
def one_root14(mv):
    '''Does x^2 - (m+1)x + 2 have exactly one real root at m = mv.'''
    return len(solveset(x**2 - (mv + 1)*x + 2, x, S.Reals)) == 1


my14 = ...               # the set of values of m

verify_param_set('Task 14, by substance', my14, one_root14, var=m)
check_set('Task 14, both values', my14, '""" + D_M14 + r"""')
""")

md(r"""
## Task 15 🔴 — a substitution, the discriminant and the domain

Find all the values of $k$ for which the equation

$$e^{2x} + \ln k = 3e^x$$

has at least one real solution.

The discriminant alone is not enough here: the answer is bounded on both sides, and
the second bound does not come from it.

*Source: May 2023 TZ1, Paper 1, Q4 (6 marks, no calculator).*
""")

code(r"""
def has_root15(kv):
    '''Does the equation have a real solution at k = kv.'''
    if kv <= 0:
        return None          # ln k is undefined: there is nothing to judge
    return solveset(Eq(exp(2*x) + log(kv), 3*exp(x)), x, S.Reals) != S.EmptySet


my15 = ...               # the set of values of k

verify_param_set('Task 15', my15, has_root15)
""")

md(r"""
## Task 16 🔴 — one solution and two solutions

The function $f(x) = \dfrac{2x+6}{3x+6}$ is defined for $x \ne -2$, and the line is
given by $g(x) = mx+1$, where $m \ne 0$.

**(a)** Find the value of $m$ for which the equation $f(x) = g(x)$ has exactly one
solution.

**(b)** Find all $m$ for which the equation $f(x)=g(x)$ has exactly two solutions
with $x \ge 0$.

The condition $m \ne 0$ is at work here: at $m=0$ there is also exactly one solution,
and without that caveat the answer to (a) would be different. The check knows about
the caveat and skips the point $m=0$.

*Source: May 2024 TZ2, Paper 1, Q5(b)(ii)(iii) (4 + 2 marks, no calculator).*
""")

code(r"""
def solutions16(mv, region=S.Reals):
    '''The solutions of f(x) = g(x) at m = mv in the given region.'''
    return solveset(Eq((2*x + 6)/(3*x + 6), mv*x + 1), x, region)


def one_solution16(mv):
    if mv == 0:
        return None          # the question says m != 0
    return len(solutions16(mv)) == 1


def two_nonneg16(mv):
    if mv == 0:
        return None
    return len(solutions16(mv, Interval(0, oo))) == 2


my16_a = ...             # the value of m from part (a), as a set
my16_b = ...             # the set of values of m from part (b)

verify_param_set('Task 16(a)', my16_a, one_solution16, var=m)
verify_param_set('Task 16(b)', my16_b, two_nonneg16, var=m)
""")

md(r"""
## Task 17 🔴 — a range through the discriminant

Find the range of the function

$$f(x) = \frac{x^2-14x+24}{2x+6}.$$

The technique is not obvious and is worth knowing: write $y = f(x)$, clear the
fraction and look at the resulting equality as a **quadratic equation in $x$** with
the parameter $y$. A value of $y$ is attained exactly when that equation has a
root.

Write the answer exactly, with surds.

*Source: November 2023 TZ1, Paper 2, Q11(e) (4 marks, calculator).*
""")

code(r"""
def attained17(yv):
    '''Does f take the value yv.'''
    return solveset(Eq((x**2 - 14*x + 24)/(2*x + 6), yv), x, S.Reals) != S.EmptySet


my17 = ...               # the range of f

verify_param_set('Task 17', my17, attained17, var=y)
""")

md(r"""
---
## Theory 9. How many solutions

The last technique of the topic and the least like the others: here nothing is
solved at all. The question «for which values of the parameter are there exactly so
many solutions» is almost always solved with a picture.

**The basic picture.** The equation $f(x) = k$ is the horizontal line $y=k$ and the
graph $y=f(x)$. The number of solutions equals the number of intersections, and it
changes exactly when the line passes through a **local maximum or minimum**. Hence
the recipe:

1. find the stationary points of $f$ and the values of $f$ at them;
2. those values are the boundaries; between them the number of solutions is
   constant;
3. at the boundaries themselves the line touches, and two solutions merge into one.

Take $f(x) = x^4-4x^2$. The stationary points are $x=0$ with value $0$ and
$x=\pm\sqrt2$ with value $-4$. So $f(x)=k$ has no solutions for $k<-4$; two at
$k=-4$ (the minima touch); four for $-4<k<0$; three at $k=0$ (the line passes
through the local maximum); and two again for $k>0$. Five answers, and all five are
read off one picture on which two numbers are marked — $0$ and $-4$.

**A second kind of picture — parity.** If the function is even, every solution
$x_0 \ne 0$ comes paired with $-x_0$, and an odd number of solutions is only possible
through the zero. So questions of the form «exactly four solutions» are often solved
not by computing but by the sentence «$n$ is even».

**What to write in the answer.** The answer is a set of values of the parameter, with
all the caveats about strictness: at a boundary the number of solutions is different,
and the signs $<$ or $\le$ here are not decoration.
""")

md(r"""
## Task 18 🔴 — a family of curves

**(a)** Find the two values of $b$ for which the curve $y = x^3+3x^2+b$ meets the
$x$-axis at exactly two points.

**(b)** Write down the set of values of $b$ for which the curve $y = x^3+3x^2+b$ has
exactly one $x$-intercept, and the set for which it has three.

**(c)** The same for the curve $y = x^3-3x^2+b$: the sets for two, one and three
intercepts.

**(d)** The equation $x^4(2-x)^4 = k$. Find all $k$ for which it has exactly four
solutions.

*Sources: November 2023, Paper 3, Q1(a)(b)(c) (2+2+3 marks) and May 2021 TZ2,
Paper 3, Q1(h) (5 marks), both calculator papers.*
""")

code(r"""
def intercepts18(bv, av):
    '''How many distinct x-intercepts y = x^3 + a x^2 + b has.'''
    return len(set(real_roots(Poly(x**3 + av*x**2 + bv, x))))


def four_roots18(kv):
    '''Does x^4(2 - x)^4 = k have exactly four solutions.'''
    left = lambdify(x, x**4*(2 - x)**4 - kv, 'math')
    return count_roots(left, -3, 5) == 4


my18_a = ...             # the two values of b: exactly two intercepts, a = 3
my18_b1 = ...            # the set of b: one intercept, a = 3
my18_b3 = ...            # the set of b: three intercepts, a = 3
my18_c2 = ...            # the two values of b: exactly two intercepts, a = -3
my18_c1 = ...            # the set of b: one intercept, a = -3
my18_c3 = ...            # the set of b: three intercepts, a = -3
my18_d = ...             # the set of k: exactly four solutions

verify_param_set('Task 18(a)', my18_a,
                 lambda bv: intercepts18(bv, 3) == 2, var=b)
verify_param_set('Task 18(b), one', my18_b1,
                 lambda bv: intercepts18(bv, 3) == 1, var=b)
verify_param_set('Task 18(b), three', my18_b3,
                 lambda bv: intercepts18(bv, 3) == 3, var=b)
verify_param_set('Task 18(c), two', my18_c2,
                 lambda bv: intercepts18(bv, -3) == 2, var=b)
verify_param_set('Task 18(c), one', my18_c1,
                 lambda bv: intercepts18(bv, -3) == 1, var=b)
verify_param_set('Task 18(c), three', my18_c3,
                 lambda bv: intercepts18(bv, -3) == 3, var=b)
verify_param_set('Task 18(d)', my18_d, four_roots18)
""")

md(r"""
---
## Trainer: name the technique in five seconds

Below are fifteen statements with no solutions. For each one write the code of the
technique — and nothing else. Nothing has to be computed; the aim is for the first
move to be found before the computing starts.

The codes: `zero` (a zero of a function) · `quad` (a quadratic) · `form` (build the
equation) · `extra` (extra and lost roots) · `explog` (a substitution and
logarithms) · `meet` (an intersection of graphs) · `gdc` (numerically) ·
`disc` (the discriminant as a condition) · `count` (the number of solutions)

1. Find the coordinates of the points where $y = \dfrac{x-5}{x+1}$ meets the axes.
2. Write $x^2-6x+11$ in the form $(x-h)^2+k$.
3. Solve $\log_2 x + \log_2(x-2) = 3$.
4. For which $c$ is the line $y = 2x+c$ tangent to the parabola $y = x^2$?
5. Solve $\sqrt{x+7} = x+1$.
6. Find the points of intersection of $y = x^2$ and $y = 3x-2$.
7. How many solutions does $|x^2-4| = 3$ have?
8. The area of a rectangle with sides $x$ and $x+3$ equals its perimeter. Form the equation.
9. Solve $e^{\sin t} = 2t$ for $0 \le t \le 3$ (Paper 2).
10. Find the axis of symmetry of $y = 2x^2-12x+7$.
11. Solve $\dfrac{1}{x-1} + \dfrac{1}{x+1} = 1$.
12. For which $k$ does $kx^2+4x+k=0$ have no real roots?
13. Solve $4^x - 5\cdot2^x + 4 = 0$.
14. For which $a$ does $x^3-3x+a=0$ have exactly three solutions?
15. Show that $y = mx$ and $x^2+y^2 = 9$ meet when $x^2(1+m^2) = 9$.
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
## Task 19 🔴 — on the timer, 21 minutes

A whole Paper 1 question with no calculator. Fourteen marks, target time about 21
minutes.

The functions are given by

$$f(x) = \ln(2x-9), \qquad g(x) = 2\ln x - \ln d,$$

where $d$ is a positive constant. The graphs of $f$ and $g$ meet at two distinct
points.

**(b)(i)** Show that the $x$-coordinates of the points of intersection satisfy the
equation $x^2-2dx+9d = 0$. [4]

**(b)(ii)** Hence show that $d^2-9d>0$. Enter the discriminant — the expression from
which the required inequality comes by dividing by 4. [3]

**(b)(iii)** Find the set of possible values of $d$. [2]

**(c)** For $d = 10$ the graphs meet at the points with $x = p$ and $x = q$, where
$p<q$. Find $q-p$ in the form $a\sqrt{b}$, where $a, b$ are positive integers. [5]

*Source: November 2023 TZ2, Paper 1, Q10(b)(c) (9 + 5 marks, no calculator).*
""")

code(r"""
my19_eq = ...            # the equation from part (b)(i)
my19_disc = ...          # the discriminant from part (b)(ii)
my19_d = ...             # the set of values of d from part (b)(iii)
my19_roots = [...]       # the roots at d = 10
my19_qp = ...            # q - p

verify_equation('Task 19(b)(i)', my19_eq, x**2 - 2*d*x + 9*d)
verify_identity('Task 19(b)(ii)', my19_disc, 4*d**2 - 36*d, var=d)
verify_solution_set('Task 19(b)(iii)', my19_d, d**2 - 9*d > 0, var=d,
                    domain=Interval.open(0, oo))
verify_root_set('Task 19(c), the roots', my19_roots, x**2 - 20*x + 90)
check_expr('Task 19(c), q - p', my19_qp, '""" + D_QP19 + r"""')
""")

md(r"""
---
# Solutions

Below is a full working of every task with the markscheme's marking. Open them after
you have solved on your own: the working explains not only the answer but what
exactly the marks are given for.
""")

md(r"""
## Solution 1 — zeros and intercepts

**(a)** A fraction is zero when the numerator is zero and the denominator is not:

$$7x+7 = 0 \iff x = -1, \qquad 2\cdot(-1)-4 = -6 \ne 0.$$

**(b)** The $y$-axis is $x=0$:

$$g(0) = 1 - \frac{1}{0-2} = 1 + \frac12 = \frac32
\ \Longrightarrow\ \left(0,\ \tfrac32\right).$$

The $x$-axis is $g(x)=0$:

$$1 = \frac{1}{x-2} \iff x-2 = 1 \iff x = 3
\ \Longrightarrow\ (3,\ 0).$$

```python
my1a = [-1]
my1b_x = [3]
my1b_y = Rational(3, 2)
```

**The marking.** (a): M1 for realising that $f(x)=0$ is wanted, A1 for $x=-1$. (b):
A1 for $(0, \frac32)$, A1 for $(3, 0)$.

**About the word coordinates.** In (b) coordinates are asked for, and the answer
«$3$ and $\frac32$» earns no mark: pairs are wanted. That is not an examiner's
quibble but the difference between «a zero of a function» and «a point on a
graph».

**The denominator is always checked.** Here it does not interfere, but the habit is
needed: for $\frac{x-2}{x^2-4}$ the numerator vanishes at $x=2$, where the fraction
is undefined altogether, and the function has no zeros.
""")

md(r"""
## Solution 2 — the vertex form

Expand and complete the square:

$$5(x+1)(x+3) = 5(x^2+4x+3) = 5\left[(x+2)^2 - 4 + 3\right]
= 5(x+2)^2 - 5.$$

Shorter — through the symmetry: the roots are $-1$ and $-3$, the axis of symmetry is
midway, $h = \frac{-1-3}{2} = -2$, and $k = f(-2) = 5\cdot1\cdot(-1) = -5$.

```python
my2 = 5*(x + 2)**2 - 5
```

**The marking.** A1 for $a=5$, M1 for an attempt (expanding and completing the
square **or** taking the mean of the roots), A1 for $h=-2$, A1 for the finished
writing.

**The second route is faster.** The roots are visible at once, the axis of symmetry
is their mean, and the value at the vertex is one substitution. There is no need to
expand the brackets at all.

**Why the check looks at the form.** The question says «write in the form», and that
is a requirement on the writing, like «as a product of linear factors» in A4. The
answer $5x^2+20x+15$ equals the same number but is not the form: neither the vertex
nor the least value is visible in it.
""")

md(r"""
## Solution 3 — a vertex on a line

**(a)** For $f(x) = -x^2+4x+p$ the vertex is at
$x = -\frac{b}{2a} = -\frac{4}{2\cdot(-1)} = 2$. On the line at that point
$y = 2\cdot2-1 = 3$, and on the parabola $f(2) = -4+8+p = p+4$. So

$$p + 4 = 3 \iff p = -1. \qquad \blacksquare$$

**(b)** For $g(x) = x^2+qx-1$ the vertex is at $x = -\frac q2$, and

$$g\left(-\tfrac q2\right) = \frac{q^2}{4} - \frac{q^2}{2} - 1
= -\frac{q^2}{4} - 1.$$

On the line at the same point $y = 2\left(-\frac q2\right) - 1 = -q-1$. Equate:

$$-\frac{q^2}{4} - 1 = -q - 1 \iff \frac{q^2}{4} = q
\iff q^2 - 4q = 0 \iff q(q-4) = 0.$$

The roots are $q=0$ and $q=4$. By the question $q$ is a non-zero constant, so
$q = 4$.

```python
my3_p = -1
my3_q = [4]
```

**The marking.** (a): A1 for the $x$-coordinate of the vertex, M1 for the
substitution, $p=-1$ is AG. (b): A1 for $-\frac q2$, M1 for substituting into the
line, M1 for substituting into $g$, A1 for $q^2-4q=0$, A1 for $q=4$ with the
caveat.

**The discarded root is legitimate here.** At $q=0$ the vertex of the parabola
$y = x^2-1$ is the point $(0,-1)$, and it **does** lie on the line $y=2x-1$. The
mathematics does not discard it — the question's phrase «$p$ and $q$ are non-zero
constants» does. That is why the check has
`domain=Complement(S.Reals, FiniteSet(0))`: the domain is taken from the question,
not from the equation.

**Do not divide by $q$.** From $\frac{q^2}{4} = q$ that way you get $q=4$ — the
right answer and a lost root. In the exam it gets away with it until the lost root
turns out to be the one wanted; the habit is a bad one.
""")

md(r"""
## Solution 4 — from the roots and the axis of symmetry

**(a)** The axis of symmetry runs midway between the roots:

$$\frac{-\frac12 + p}{2} = 2 \iff -\frac12 + p = 4 \iff p = \frac92.
\qquad \blacksquare$$

**(b)** Knowing both roots and the leading coefficient 1:

$$g(x) = \left(x+\tfrac12\right)\left(x-\tfrac92\right)
= x^2 - 4x - \tfrac94,$$

that is, $b = -4$, $c = -\frac94$.

```python
my4_p = Rational(9, 2)
my4_b = -4
my4_c = Rational(-9, 4)
```

**The marking.** (a): 1 mark, the answer is AG. (b): M1 for writing it through the
roots or for using the axis of symmetry, A1 for $b$, A1 for $c$.

**Three roads to $b$ and $c$.** Through the product of brackets; through
$b = -2h = -4$ and substituting one root; through the system of two equations
$g(-\frac12)=0$, $g(\frac92)=0$. The first is shorter, but it pays to check with the
second: $b$ has to equal $-2\cdot2$.

**Vieta's formulas are the same fact.** $x_1+x_2 = -b$ gives
$-\frac12+\frac92 = 4 = -b$, and $x_1x_2 = c$ gives
$-\frac12\cdot\frac92 = -\frac94 = c$. That is A4, and here the join of the two
topics shows: the axis of symmetry is the mean of the roots, that is,
$-\frac{b}{2}$.
""")

md(r"""
## Solution 5 — the area equals the perimeter

The area is $s^2$, the perimeter $4s$, and by the question they are equal:

$$s^2 = 4s \iff s^2 - 4s = 0 \iff s(s-4) = 0.$$

The roots are $s=0$ and $s=4$. The side of a square is positive, so

$$s = 4.$$

```python
my5 = [4]
```

**The marking.** A1 for $A=s^2$ and $P=4s$, M1 for equating them, A1 for $s=4$. And
the markscheme's note word for word: **A1M1A0** if both values, $s=4$ and $s=0$, are
written in the answer.

**The mark is for the discarding.** This is the clearest example in the topic: all
the algebra here is half a line, and the third mark is for the zero not reaching the
answer. The check is built the same way: `domain=Interval.open(0, oo)`.

**Do not divide by $s$.** The temptation is strong: $s^2=4s \Rightarrow s=4$ in one
line. The answer matches, but the method is wrong — that is how a root gets lost, and
in the next task it would cost the solution.
""")

md(r"""
## Solution 6 — the same for a right-angled triangle

**(a)** The area and the perimeter:

$$A = \frac12 ab, \qquad P = a + b + \sqrt{a^2+b^2}.$$

Equate them and isolate the root:

$$\frac12 ab = a+b+\sqrt{a^2+b^2}
\iff \sqrt{a^2+b^2} = \frac12 ab - a - b.$$

Square both sides:

$$a^2+b^2 = \frac{a^2b^2}{4} + a^2 + b^2 - a^2b - ab^2 + 2ab,$$

and after cancelling $a^2+b^2$

$$\frac{a^2b^2}{4} - a^2 b - ab^2 + 2ab = 0.$$

**(b)** Every term is divisible by $ab$, and $ab > 0$, so dividing is allowed:

$$\frac{ab}{4} - a - b + 2 = 0 \iff ab - 4a - 4b + 8 = 0
\iff a(b-4) = 4b - 8.$$

What is left is separating the whole part:

$$a = \frac{4b-8}{b-4} = \frac{4(b-4)+8}{b-4} = \frac{8}{b-4} + 4.
\qquad \blacksquare$$

```python
my6_sq = a**2*b**2/4 - a**2*b - a*b**2 + 2*a*b
my6_a = 8/(b - 4) + 4
```

**The marking.** A1A1 for $A$ and $P$ separately, M1 for equating them, M1 for
isolating the root, M1 for attempting to square, A1 for the intermediate
simplification, A1 for the required form (AG). And the note: verifying the given
answer by substitution earns at most A1A1M1M1M0A0A0.

**Why dividing by $ab$ is legitimate here.** Because $a$ and $b$ are side lengths
and both are positive. Without that caveat the step is wrong: dividing by an
expression with variables means declaring it non-zero.

**Squaring adds roots, and that is not frightening here.** Formally a second branch
appears ($\frac12ab-a-b$ could have been negative), but the answer is not a number
but a formula, and a formula has no surplus roots. The checking will have to be done
in the next task, when concrete triangles start coming out of the formula.

**About «verifying».** The markscheme's note about the maximum marks for verifying is
common to every AG question: substituting the finished answer and seeing that it
works is not a derivation.
""")

md(r"""
## Solution 7 — the integer solutions of a rational equation

From $a = \frac{8}{b-4} + 4$ it is clear that $a$ is an integer if and only if
$b-4$ divides 8. The sides are positive, so the positive divisors are the ones of
interest:

$$b - 4 \in \{1, 2, 4, 8\} \ \Longrightarrow\ b \in \{5, 6, 8, 12\},$$

and correspondingly

$$a = 12,\ 8,\ 6,\ 5.$$

The negative divisors give $b \le 3$ and $a \le 0$ — not a triangle.

There are four pairs but two triangles: $(a,b) = (12,5)$ and $(5,12)$ are one and the
same triangle with sides $5, 12, 13$, and $(8,6)$ and $(6,8)$ are the triangle
$6, 8, 10$.

```python
my7_b = [5, 6, 8, 12]
my7_n = 2
```

**The marking.** M1 for a method (running through $b$ or the divisibility
property), A1 for $(5,12,13)$, A1 for $(6,8,10)$. And the note: A1A0 if one triangle
is found in full, or two sides of each.

**The equation is symmetric, the question is not.** The formula does not tell the
legs apart, so its solutions come in pairs. The question asks about triangles, and
turning four solutions into two is a separate step, which is what the marks are for
here.

**Why divisors rather than a search.** A search is accepted too, but it is endless
unless you notice that $\frac{8}{b-4}$ decreases: already at $b=13$ the fraction is
below 1 and will never be an integer again. Divisibility gives the finite list at
once.

**Familiar numbers.** $(5,12,13)$ and $(6,8,10)$ are Pythagorean triples, and the
second is $(3,4,5)$ doubled. That it is precisely these that came out follows from
the condition $A=P$ and is no coincidence: $(3,4,5)$ has area 6 and perimeter 12, so
doubling the sides doubles the perimeter and quadruples the area, and they become
equal.
""")

md(r"""
## Solution 8 — a logarithm and its domain

The graph meets the $x$-axis where $f(x)=0$:

$$\ln(x^2-16) = 0 \iff x^2-16 = e^0 = 1 \iff x^2 = 17
\iff x = \pm\sqrt{17}.$$

By the question $x>4$, and $\sqrt{17} = 4.123\ldots > 4$, so

$$\alpha = \sqrt{17}.$$

```python
my8 = [sqrt(17)]
```

**The marking.** M1 for $\ln(x^2-16)=0$, A1 for $x^2=17$ or $x=\pm\sqrt{17}$, A1 for
$\alpha=\sqrt{17}$.

**Both marks after the M1 are about selection.** The middle one for there being two
roots, the last one for one of them going into the answer. Writing $\sqrt{17}$
straight away without showing the $\pm$ loses an A1: the work does not show that a
choice was made.

**The exact value.** «Exact value» means a surd: $4.12$ does not count. On Paper 1
there is no calculator anyway, but the habit of rounding survives to the exam.

**The domain here is double.** The expression $\ln(x^2-16)$ itself requires
$|x|>4$, and $-\sqrt{17}$ does not contradict that — it is thrown out by the
question's separate condition $x>4$. Two different restrictions, and both have to be
kept in mind.
""")

md(r"""
## Solution 9 — quadratic in $3^x$

Notice that $9^x = (3^2)^x = (3^x)^2$ and put $A = 3^x$:

$$3A^2 + 5A - 2 = 0 \iff (3A-1)(A+2) = 0
\iff A = \frac13 \ \text{or}\ A = -2.$$

An exponential is positive, so $A=-2$ is discarded, and from
$3^x = \frac13 = 3^{-1}$ we get

$$x = -1.$$

```python
my9 = [-1]
```

**The marking.** M1 for recognising a quadratic in $3^x$, M1 for attempting to solve
the quadratic, A1 for the factorisation or the formula, A1 for $3^x=\frac13$ (and
$3^x=-2$), A1 for $x=-1$.

**The discarding here is free but named.** The markscheme accepts the answer
«$x=-1$ and $x=\log_3(-2)$» — the second writing is meaningless but tolerated. Any
other extra root, though, kills the last mark.

**Where the substitution breaks.** A frequent mistake is to solve the quadratic and
stop: $A=\frac13$ is not the answer, the question was about $x$. The way back
$3^x = \frac13 \Rightarrow x = -1$ is the last A1.
""")

md(r"""
## Solution 10 — three log laws in a row

Start with the fraction. By the change of base
$\frac{1}{\log_2 3} = \log_3 2$, so

$$\frac{1}{2\log_2 3} = \frac12\log_3 2 = \log_3 \sqrt2.$$

Now there are two logarithms to base 3 on the right, and they combine:

$$\log_3 \sqrt x = \log_3 \sqrt2 + \log_3 (4x^3)
= \log_3\left(4\sqrt2\, x^3\right).$$

Logarithms to the same base are equal — so the arguments are equal:

$$\sqrt x = 4\sqrt2\, x^3.$$

Square:

$$x = 32x^6 \iff 32x^5 = 1 \iff x^5 = \frac{1}{32}
\iff x = \frac12.$$

```python
my10 = [Rational(1, 2)]
```

**The marking.** M1 for attempting the change of base, M1 for taking the exponent
out, M1 for combining the logarithms, A1 for $x^5 = \frac1{32}$, A1 for
$x=\frac12$.

**The three M1s are not for the order but for the fact.** The markscheme says
directly: the three methods may be applied in any order and at any point of the
solution. Attempts are counted, not the sequence.

**The fraction is a hint.** $\frac{1}{2\log_2 3}$ looks like something superfluous,
while in fact it is the only place where the change of base is needed, and the
solution starts from it. The form is worth remembering:
$\frac{1}{\log_b a} = \log_a b$.

**About the squaring.** The step is not an equivalence, but it is safe here: $x>0$ by
the question and both sides are positive. The root $x=\frac12$ passes the check:
$\sqrt{0.5} = 0.7071$, $4\sqrt2\cdot0.125 = 0.7071$.
""")

md(r"""
## Solution 11 — a «show that» about an intersection

Points of intersection have the same $x$ and the same $y$, so the right-hand sides
are equal:

$$x^2-x-1 = mx-3.$$

Take everything to the left:

$$x^2-x-1-mx+3 = 0 \iff x^2 - (m+1)x + 2 = 0. \qquad \blacksquare$$

```python
my11 = Eq(x**2 - (m + 1)*x + 2, 0)
```

**The marking.** M1 for equating $y = mx-3$ and $y = x^2-x-1$, A1 for any correct
intermediate writing ($x^2-x-1-(mx-3)=0$ or $mx-x^2+x+2=0$); the result is AG.

**Two marks for two lines.** That is the whole of part (a), and there is nothing in
it but moving terms. Even so it cannot be skipped: the whole question stands on that
equation afterwards.

**What the check accepts.** Any writing that differs by moving terms and a numerical
factor: $2x^2-2(m+1)x+4=0$ passes. But one multiplied by $x$ does not: such an
equation has acquired the root $x=0$, which the original did not have.
""")

md(r"""
## Solution 12 — two families of curves

Both equations have $y^2$ on the left, so the right-hand sides are equal:

$$4a^2-4ax = 4b^2+4bx.$$

Collect the $x$ on one side and the rest on the other:

$$4a^2-4b^2 = 4bx+4ax \iff 4(a-b)(a+b) = 4x(a+b).$$

The numbers $a$ and $b$ are positive, so $a+b>0$ and it can be divided out:

$$x = a - b.$$

Substitute back into the first equation:

$$y^2 = 4a^2 - 4a(a-b) = 4a^2-4a^2+4ab = 4ab
\ \Longrightarrow\ y = \pm2\sqrt{ab}.$$

Those are exactly the points $M(a-b,\ 2\sqrt{ab})$ and $N(a-b,\ -2\sqrt{ab})$.
$\blacksquare$

```python
my12_x = a - b
my12_y = 2*sqrt(a*b)
```

**The marking.** M1 for equating, M1 for attempting to solve for $x$, A1 for
$x = a-b$, M1 for the substitution, A1 for $y^2=4ab$, A1 for both signs of the root;
the coordinates are AG.

**Factorising rather than dividing.** $4a^2-4b^2 = 4x(a+b)$ factorises into
$4(a-b)(a+b) = 4x(a+b)$, and from there the cancellation is visible with no caveats
about signs. The same move as in task 5: factorising is safer than dividing.

**Both signs are compulsory.** There are two points, and the second comes not «by
symmetry» but from the fact that $y^2 = 4ab$ has two roots. Losing the minus loses an
A1.

**Why such a question is on Paper 3.** It is the first step of an investigation about
orthogonal families: later in the same question the angle between the curves at $M$ is
computed. The intersection here is not the goal but the entrance to the topic.
""")

md(r"""
## Solution 13 — two numerical solutions

**(a)** The equation $90e^{-0.5x} = x$ does not solve by hand. Draw
$y = 90e^{-0.5x}$ and $y = x$ and take the intersection:

$$x = 5.56619\ldots \approx 5.57.$$

**(b)** The water reaches the tortoise when the distances coincide, that is, when
$w(t) = g(t) - d(t) = 0$:

$$w(t) = 0.05t^2+1.1t+18 -
\frac{20\sin\frac{\pi t}{8}}{\sin\left(2.37-\frac{\pi t}{8}\right)}.$$

The first root is $t = 3.34881\ldots \approx 3.35$ s. Substitute the **unrounded**
value into $g$:

$$g(3.34881\ldots) = 22.2444\ldots \approx 22.2 \text{ m from } A.$$

```python
my13_x = 5.56619
my13_t = 3.34881
my13_g = 22.2444
```

**The marking.** (a): M1 for attempting to find the intersection of the graph of $f$
and the line $y=x$, A1 for 5.57. (b)(i): A1 for the expression for $w$; (b)(ii): M1
for attempting to solve $w=0$, A1 for $t=3.35$, A1 for 22.2.

**The first root, not any root.** $w=0$ has a second root as well, around
$t = 12.8$: the water arrives, retreats and comes back — the tide is periodic. The
word «first» in the question is part of the task; without it the answer would be
ambiguous. The model also has a discontinuity around $t = 6.04$, where the
denominator vanishes; the sign change there is a pole, not a root, and the calculator
will not warn you.

**Round at the end, not in the middle.** Substituting $t=3.35$ instead of
$3.34881$ gives 22.2461 instead of 22.2444 — here the third significant figure
happened to survive, but that is exactly luck. The rule is simple: round only the
answer you write, and take intermediate values from the calculator's memory.

**What has to be left on the paper.** «Solutions found from a graphic display
calculator should be supported by suitable working»: the equation written out and a
sketch of the graphs. A bare figure from the calculator is zero for method.
""")

md(r"""
## Solution 14 — a tangent

A tangent means exactly one root of the intersection equation, that is,
$\Delta = 0$:

$$\Delta = \big(-(m+1)\big)^2 - 4\cdot1\cdot2 = (m+1)^2 - 8 = 0.$$

Hence

$$(m+1)^2 = 8 \iff m+1 = \pm2\sqrt2 \iff m = -1 \pm 2\sqrt2.$$

```python
my14 = FiniteSet(-1 - 2*sqrt(2), -1 + 2*sqrt(2))
```

**The marking.** A1 for substituting into the discriminant, A1 for
$(m+1)^2-4(1)(2)$, A1 for the condition $\Delta=0$, A1A1 for both values of $m$.

**A second route — through the derivative.** A tangent means both the function and
the gradient agree: $2x-1 = m$, hence $x = \frac{m+1}{2}$, and substituting into the
equation gives the same thing. The markscheme accepts both, but the discriminant is
shorter.

**Two answers, two marks.** A1A1 — a mark for each value. Writing only the positive
root loses exactly half.

**How the check catches that.** It does not compute a discriminant; for every test
$m$ it asks the equation how many distinct real roots it has. So an answer obtained
by any method counts, and a surplus value is noticed.
""")

md(r"""
## Solution 15 — a substitution, the discriminant and the domain

The substitution $A = e^x$ turns the equation into a quadratic:

$$A^2 - 3A + \ln k = 0.$$

A real solution in $A$ exists when

$$\Delta = 9 - 4\ln k \ge 0 \iff \ln k \le \frac94 \iff k \le e^{9/4}.$$

The second restriction does not come from the discriminant: $\ln k$ is defined only
for $k>0$. In all

$$0 < k \le e^{9/4}.$$

```python
my15 = Interval.Lopen(0, exp(Rational(9, 4)))
```

**The marking.** M1 for recognising a quadratic in $e^x$, A1 for
$A^2-3A+\ln k=0$, M1 for $\Delta \ge 0$, A1 for $9-4\ln k$, A1 for
$\ln k \le \frac94$, A1 for the answer $0<k\le e^{9/4}$.

**The check about $A>0$.** Formally the quadratic also has to have a **positive**
root: $A=e^x$ is never negative. Here that holds by itself — the product of the
roots is $\ln k$, and for $\ln k<0$ one root is positive, while for
$0 \le \ln k \le \frac94$ both are (their sum is 3). In other questions that check
cannot be skipped.

**The sign $\le$, not $<$.** At $k = e^{9/4}$ the discriminant is zero and there is
one root — but there is one, and «at least one» is what is asked. The boundary
belongs.

**How the check catches that.** For every test $k$ it computes the roots of the
original equation numerically; for $k \le 0$ it returns None, because $\ln k$ is
undefined there and there is nothing to judge. The skipped points are printed at the
end — that is an honest part of the check's answer, not a silence.
""")

md(r"""
## Solution 16 — one solution and two solutions

Multiply by the denominator $3x+6$:

$$2x+6 = (mx+1)(3x+6) = 3mx^2 + 6mx + 3x + 6,$$

and after cancelling

$$3mx^2 + (6m+1)x = 0 \iff x\big(3mx + 6m + 1\big) = 0.$$

The roots are $x = 0$ and $x = -\dfrac{6m+1}{3m}$ (for $m\ne0$).

**(a)** Exactly one solution comes when the roots coincide:

$$-\frac{6m+1}{3m} = 0 \iff 6m+1 = 0 \iff m = -\frac16.$$

**(b)** Two solutions with $x \ge 0$ means $x=0$ and the second root strictly
greater than zero:

$$-\frac{6m+1}{3m} > 0.$$

A rational inequality: the critical values are $m=-\frac16$ and $m=0$, and between
them the fraction is positive:

$$-\frac16 < m < 0.$$

```python
my16_a = FiniteSet(Rational(-1, 6))
my16_b = Interval.open(Rational(-1, 6), 0)
```

**The marking.** (a): M1 for reducing to a quadratic, A1 for
$3mx^2+(6m+1)x=0$, M1 for the condition «one solution», A1 for $m=-\frac16$. (b): A2
for the answer; A1 if only $m>-\frac16$ or only $m<0$ was found.

**The discriminant need not be computed here.** $\Delta = (6m+1)^2$, and it is zero
exactly at $m=-\frac16$ — but the same is visible from the factorisation
$x(3mx+6m+1)$ with no formula at all. The factorisation also gives both roots at
once, and they are needed in (b).

**About $m \ne 0$.** At $m=0$ the equation becomes $x=0$ — also exactly one
solution. The question's condition excludes that case, and without it the answer to
(a) would be «$m=-\frac16$ or $m=0$». The check knows about the caveat and skips the
point $m=0$: the domain is taken from the question.

**About $x=-2$.** Multiplying by a denominator usually adds a root, and it has to be
checked. Here $x=-2$ turned out not to be one: substituting into $x(3mx+6m+1)$ gives
$-2\cdot(-6m+6m+1) = -2 \ne 0$ for any $m$. Lucky, but you still have to look.

**One more route for (a).** One solution means a tangent, which means
$m = f'(0)$. The derivative $f'(x) = -\frac{2}{3(x+2)^2}$ at zero equals
$-\frac16$ — the same answer in two lines, if derivatives have been covered.
""")

md(r"""
## Solution 17 — a range through the discriminant

Write $y = f(x)$ and clear the fraction:

$$y = \frac{x^2-14x+24}{2x+6} \iff 2xy + 6y = x^2-14x+24,$$

that is,

$$x^2 - (14+2y)x + (24-6y) = 0.$$

Look at this as a quadratic equation **in $x$**: the value $y$ is attained if and
only if it has a real root, that is, when

$$\Delta = (14+2y)^2 - 4(24-6y) \ge 0.$$

Expand:

$$196 + 56y + 4y^2 - 96 + 24y = 4y^2 + 80y + 100 \ge 0
\iff y^2 + 20y + 25 \ge 0.$$

The critical values:

$$y = \frac{-20 \pm \sqrt{400-100}}{2} = -10 \pm 5\sqrt3,$$

and the parabola opens upwards, so

$$y \le -10-5\sqrt3 \quad\text{or}\quad y \ge -10+5\sqrt3,$$

numerically $y \le -18.7$ or $y \ge -1.34$.

```python
my17 = Union(Interval(-oo, -10 - 5*sqrt(3)),
             Interval(-10 + 5*sqrt(3), oo))
```

**The marking.** A1 for $-10-5\sqrt3$ or $-10+5\sqrt3$ appearing, M1 for attempting
to write the range, A1A1 for both pieces of the answer.

**Why the technique works.** «$y$ belongs to the range» and «the equation $f(x)=y$
has a solution» are one and the same statement. The second is checked with the
discriminant, and the whole trick is swapping the roles: the unknown here is $x$ and
the parameter is $y$.

**A gap in the middle is normal.** A rational function with a vertical asymptote has
a graph of two branches: one goes up, the other down, and between the local maximum
and the local minimum there are no values. The ends belong to the answer: there the
equation has a (double) root.

**A check with a calculator.** On Paper 2 the same numbers come off the graph: the
local maximum $-18.7$, the local minimum $-1.34$. But the answer is worth writing
exactly, with surds — the markscheme accepts either, and the exact writing is
safer.
""")

md(r"""
## Solution 18 — a family of curves

**(a)** For $y = x^3+3x^2+b$ the derivative is $3x^2+6x = 3x(x+2)$, the stationary
points are $x=0$ and $x=-2$, and the values there are

$$y(0) = b, \qquad y(-2) = -8+12+b = 4+b.$$

Exactly two $x$-intercepts happen when one of those points lies **on** the axis:
$b=0$ or $4+b=0$, that is,

$$b = 0 \quad\text{or}\quad b = -4.$$

**(b)** Three intercepts — when the maximum and the minimum are on opposite sides of
the axis: $-4 < b < 0$. One — when they are on the same side: $b<-4$ or $b>0$.

**(c)** For $y = x^3-3x^2+b$ the stationary points are $x=0$ and $x=2$, with values
$b$ and $-4+b$. Similarly: two intercepts at $b=0$ or $b=4$; three for $0<b<4$; one
for $b<0$ or $b>4$.

**(d)** Write $u = x(2-x)$. Then the equation becomes $u^4 = k$. The function $u$
takes every value from $-\infty$ to 1, and every value $u<1$ is attained twice, while
$u=1$ is attained once.

$$u^4 = k \iff u = \pm\sqrt[4]{k} \quad (k>0).$$

Four solutions in $x$ come when **both** values of $u$ are attained twice, that is,
when $\sqrt[4]{k} < 1$:

$$0 < k < 1.$$

In general (the markscheme's condition): $n$ is even and
$0 < k < \left(\frac a2\right)^{2n}$.

```python
my18_a = FiniteSet(-4, 0)
my18_b1 = Union(Interval.open(-oo, -4), Interval.open(0, oo))
my18_b3 = Interval.open(-4, 0)
my18_c2 = FiniteSet(0, 4)
my18_c1 = Union(Interval.open(-oo, 0), Interval.open(4, oo))
my18_c3 = Interval.open(0, 4)
my18_d = Interval.open(0, 1)
```

**The marking.** (a): M1 for trying values of $b$ or for considering the case
$b=0$, A1 for both values. (b), (c): an A1 for each set. (d): M1 for considering the
parity of $n$, A1 for «$n$ is even», A1 for the lower bound, A1 for the upper one, A1
for the strict signs.

**A question about a picture, not about formulas.** Paper 3 suggests it directly,
«by systematically varying the value of $b$»: look at the family on the GDC and see
what happens. The stationary points are needed in order to write the boundaries
exactly.

**The strict signs are a separate mark.** In (d) the markscheme gives an A1
precisely for both inequalities being strict. At the boundaries the number of
solutions is different: at $k=0$ there are two (double touchings), at $k=1$ three.

**The parity in (d).** For odd $n$ the function $x^n(2-x)^n$ behaves differently and
four solutions never happen. That is the only place in the practicum where the answer
comes not from computing but from a conversation about parity — and in the archive
such places always carry a separate M1.
""")

md(r"""
## Solution 19 — the task on the timer

**(b)(i)** Equate and collect the logarithms:

$$\ln(2x-9) = 2\ln x - \ln d = \ln x^2 - \ln d = \ln\frac{x^2}{d}.$$

Logarithms are equal — the arguments are equal:

$$2x-9 = \frac{x^2}{d} \iff d(2x-9) = x^2 \iff x^2 - 2dx + 9d = 0.
\qquad \blacksquare$$

**(b)(ii)** Two distinct points of intersection mean two distinct roots, that is,
$\Delta>0$:

$$\Delta = (-2d)^2 - 4\cdot1\cdot9d = 4d^2 - 36d > 0,$$

and after dividing by 4

$$d^2 - 9d > 0. \qquad \blacksquare$$

**(b)(iii)** Factorise: $d(d-9)>0$, with critical values 0 and 9. By the question
$d>0$, so the left piece falls away and what is left is

$$d > 9.$$

**(c)** At $d=10$ the equation becomes

$$x^2 - 20x + 90 = 0 \iff x = \frac{20 \pm \sqrt{400-360}}{2}
= 10 \pm \sqrt{10}.$$

So $p = 10-\sqrt{10}$, $q = 10+\sqrt{10}$ and

$$q - p = 2\sqrt{10}.$$

```python
my19_eq = Eq(x**2 - 2*d*x + 9*d, 0)
my19_disc = 4*d**2 - 36*d
my19_d = Interval.open(9, oo)
my19_roots = [10 - sqrt(10), 10 + sqrt(10)]
my19_qp = 2*sqrt(10)
```

**The marking.** (b)(i): M1 for equating, M1 for the power law, M1 for the quotient
law, A1 for the correct logarithmic equality; the result is AG. (b)(ii): A1 for the
discriminant, M1 for «$\Delta>0$», A1 — AG. (b)(iii): M1 for solving $d(d-9)>0$, A1
for $d>9$. (c): A1 for $x^2-20x+90=0$, M1 for attempting to solve, A1 for both
roots, M1 for the subtraction, A1 for $2\sqrt{10}$.

**How it looks in time.** Fourteen marks in 21 minutes, and the first four are pure
work with logarithms. If that does not come out within five minutes, there is no
point going on: the whole question stands on the equation from (b)(i).

**The condition $d>0$ works twice.** The first time so that $\ln d$ exists at all,
the second time in (b)(iii), where it cuts off the piece $d<0$. Without it the answer
would be «$d<0$ or $d>9$», and that is exactly the mark that is lost most often.

**A check on the answer in five seconds.** Take $d=10>9$: the roots are
$10\pm\sqrt{10} \approx 6.84$ and $13.16$. Both are greater than $4.5$, so
$2x-9>0$ and the logarithm is defined — it agrees. Take $d=5$: $x^2-10x+45=0$, the
discriminant $100-180<0$, no intersections — and indeed $5 < 9$.

**Where $2x-9>0$ came from.** The domain of $f$ is $x>4.5$ and the domain of $g$ is
$x>0$. For $d>9$ the roots of $x^2-2dx+9d=0$ fall into the intersection of the
domains automatically: the product of the roots is $9d>0$ and the sum is $2d>0$, so
both are positive, and $2x-9>0$ follows from the fact that the equation came from an
equality of logarithms in the first place.
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

OUT = os.path.join(ROOT, 'practicum/functions', 'practicum-b1-equations.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
