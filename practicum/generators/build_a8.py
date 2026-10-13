"""Собирает практикум A8 (неравенства) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig, _series_canon

sq = sp.sqrt
R = sp.Rational
x, y, k, n, u = sp.symbols('x y k n u')
a, b, c, d, m, p, q, s, T = sp.symbols('a b c d m p q s T')


def ds(expr, var=x):
    return digest(_series_canon(expr, var))


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_a8.py ---
D_N6, D_T21, D_T22 = dn(21), dn(672), dn(737)
D_K8 = dn(5)
D_AC10 = dset([1, 2, 3, 4, 5, 6, 8])
D_M18 = ds((T / n)**n, var=n)

TRIGGER = {1: 'crit', 2: 'disc', 3: 'rat', 4: 'prove', 5: 'abs',
           6: 'vieta', 7: 'gdc', 8: 'disc', 9: 'count', 10: 'crit',
           11: 'prove', 12: 'rat', 13: 'disc', 14: 'gdc', 15: 'abs'}
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
# Practicum A8: inequalities

**87 marks, 31 blocks, eight techniques.** The smallest topic of section A — and the
most scattered: an inequality is almost never a whole question, it is one part
inside somebody else's.

**Material.** 31 blocks and 87 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**The main idea of the topic.** An inequality has no numerical answer. The answer is
a **set**, and the whole substance of the topic is in its boundary: where the
boundary comes from and whether it belongs to the answer.

That is also how the practicum is built. An inequality arrives from three sides:

* it is **solved** — then the answer is a set of $x$ (techniques 1–4);
* it arises as a **condition on a letter** — then the answer is a set of values of
  the parameter (techniques 5–7);
* it is **proved** — then there is no set at all (technique 8).

**How to work**

1. Read the map of techniques. Telling those three sides apart matters more than
   remembering any single technique.
2. Work **on paper**. The table of signs and the critical values are hand work, and
   all the M1s are for them.
3. Enter the answer as a set: `Interval(-2, 6)`, `(x >= -2) & (x <= 6)`,
   `Union(Interval.open(-oo, -10), Interval.open(3, oo))` — whichever suits. The
   check compares sets, not writings.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Union, solveset, real_roots

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d = symbols('a b c d')
m, n, p, q, s = symbols('m n p q s')
T = Symbol('T')                # the sum in task 18; the letter S is already taken

print('ready; sympy', sp.__version__)
print('solve an inequality: ', solveset(x**2 + 4*x - 5 <= 0, x, S.Reals))
print('the same, but d > 0: ', solveset(d**2 - 9*d > 0, d, Interval.open(0, oo)))
print('the answer as a set: ', Union(Interval.open(-oo, -10), Interval.open(3, oo)))
print('roots for a condition:', real_roots(Poly(x**2 - 3*x + 2, x)))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Critical values and the sign | «solve $f(x)\le c$» for a polynomial | everything to one side, the zeros, the table of signs |
| 2 | A rational inequality | «solve $f(x) > x$», there is a fraction in it | one fraction, the zeros of the numerator **and** the denominator |
| 3 | A modulus | $\lvert\,\cdot\,\rvert$ in the question, «sketch $\lvert f\rvert$» | remove the modulus by two cases, or from a sketch |
| 4 | Numerically, on the GDC | Paper 2, ugly numbers, «3 s.f.» | find the intersections, assemble the intervals |
| 5 | The discriminant as a condition | «two distinct real roots», «no real roots» | $\Delta>0$, $\Delta=0$, $\Delta<0$ — and solve for the letter |
| 6 | The signs of the roots | «one positive and one negative root», «both roots» | $\alpha\beta=\frac ca$, $\alpha+\beta=-\frac ba$ |
| 7 | The number of solutions as a set | «exactly two», «for all $x$», «at least one» | find where the solutions merge or disappear |
| 8 | Prove an inequality | «show that … $\ge$ …», «prove by contradiction» | take everything to one side and complete the square |

The ladder goes by **where the answer lives**. Techniques 1–4 solve an inequality in
$x$: the answer is a set on the number line, and the work is in finding its
boundaries and including or excluding them correctly.

Techniques 5–7 turn the question round. The inequality is no longer asked for — it
is obtained: «for which $k$ does the equation have two roots» turns into
$\Delta>0$, that is, into an inequality **in the letter**. Solving that you already
know how to do with technique 1; the new thing here is only the first step, the
translation of the question's wording into an inequality.

Technique 8 stands apart: proving an inequality is not the same as solving one.
There is no set in the answer, there is a chain whose last step has to be obvious.

**What saves the most time.** Before computing, look at what is being asked about —
$x$ or the letter. Half the marks lost in this topic are the roles confused: people
solve in $x$ where the answer should be a set of values of $k$.
""")

md(r"""
---
## Where the calculator is in this topic

Formally 49 marks out of 87 are on calculator papers, that is, 56%. As in the other
topics of section A, the figure deceives.

| | marks | of which really need a GDC |
| --- | --- | --- |
| Paper 1 | 38 | — |
| Paper 2 | 29 | 7 |
| Paper 3 | 20 | 2 |

Nine marks out of 87 — that is all the work there is for a calculator: one
inequality with an exponential and a fraction (task 5), one integer answer (task 6)
and one reading off a graph in an investigation (task 14). Everything else on the
«calculator» papers is algebra: the discriminant, Vieta, proof by contradiction. A
proof on Paper 2 is not shortened by a calculator by a single line.

Where a GDC does help:

* **Find the intersections.** The only way to solve
  $2^x-2^{-x}\ge\frac{x-1}{x^2-2x-3}$ in the four minutes allowed.
* **Check a boundary.** Substitute a point slightly left and slightly right of the
  end found into the original inequality — five seconds, and you know which way the
  interval goes.
* **Run through integers.** «The largest integer $n$ for which …» — a table of
  values; the markscheme explicitly accepts checking the two neighbouring $n$.

Where it is useless: wherever there is a letter in the question. The equation
$x^2+kx+15-k=0$ a calculator will not solve, while the discriminant does it in a
line.

**The hardest thing in a calculator question in this topic is not the computing but
the writing.** A GDC gives three intersections; the marks are for three intervals
and for which ends belong to them.
""")

md(r"""
---
## Theory 1. The answer is a set

An equation asks «where it is equal», an inequality «where it is greater». The
answer to the second question is almost never a point: it is a union of intervals,
and it has to be written out in full.

**The working order.** It is the same throughout the topic:

1. Take everything to one side: $f(x) \ge 0$.
2. Find the **critical values** — the zeros of $f$ and the points where $f$ is
   undefined.
3. Between neighbouring critical values the sign of $f$ is constant — so one test
   point per interval is enough.
4. Collect the intervals wanted and decide for each end whether it belongs.

Point 3 is the substance of the method: the sign changes only where the function
vanishes or breaks, nowhere else.

**What must not be done.** Multiplying or dividing an inequality by an expression
whose sign is unknown. $\frac1x > 1$ is not equivalent to $1 > x$: for negative $x$
the left-hand side is negative and the inequality would have flipped. That mistake
costs every mark of the question, because the answer comes out looking plausible.

**About the ends.** The rule is simple: an end that came from a **zero** of the
function belongs to the answer if and only if the inequality is non-strict; an end
that came from a **break** never belongs.

**Three ways of writing the answer.** IB accepts any:

$$-2 \le x \le 6, \qquad [-2,\;6], \qquad \{x : -2\le x\le 6\}.$$

What it does not accept is a mixture. The writing «$x<-10,\;x>3$» with a comma reads
as «both at once», that is, as the empty set. Write «or» or $\cup$.
""")

code(r"""
# A warm-up (not a task): why the sign changes only at the critical points.
f = (x - 1)*(x + 2)
for pt in [-3, -2, -1, 0, 1, 2]:
    val = f.subs(x, pt)
    mark = '+' if val > 0 else ('0' if val == 0 else '-')
    print(f'x = {pt:2d}:  f = {str(val):>3},  sign {mark}')
print('the solution of f(x) < 0:', solveset(f < 0, x, S.Reals))
""")

md(r"""
## Task 1 🟢 — a whole quadratic inequality

For $f(x) = 5(x+2)^2 - 5$, solve the inequality $f(x) \le 40$.

Enter the answer as a set: `Interval(a, b)` or `(x >= a) & (x <= b)`.

*Source: May 2025 TZ1, Paper 1, Q10(c) (4 marks, no calculator).*
""")

code(r"""
my1 = ...                # the solution set

verify_solution_set('Task 1', my1, 5*(x + 2)**2 - 5 <= 40)
""")

md(r"""
## Task 2 🟢 — when the domain changes the answer

Given that $d$ is a positive real number and $d^2 - 9d > 0$, find the set of
possible values of $d$.

Note: without the condition $d \in \mathbb{R}^+$ the answer would be different, and
the last mark of the question is precisely for it.

*Source: November 2023 TZ1, Paper 1, Q10(b)(iii) (2 marks, no calculator).*
""")

code(r"""
my2 = ...                # the set of values of d

verify_solution_set('Task 2', my2, d**2 - 9*d > 0,
                    var=d, domain=Interval.open(0, oo))
""")

md(r"""
---
## Theory 2. A fraction: do not touch the denominator

The inequality $\dfrac{A(x)}{B(x)} > 0$ is solved by exactly the order of theory 1,
with one amendment: the critical values become **the zeros of the numerator and the
zeros of the denominator**.

The reason is that a fraction changes sign in both cases — passing through zero and
passing through a break. The zeros of the denominator are always **excluded**: the
expression is undefined there, and they belong to the answer neither for a strict
nor for a non-strict inequality.

**Two legitimate routes.**

*Everything into one fraction.* From $f(x) > x$ make $f(x) - x > 0$, bring it to a
common denominator, factorise numerator and denominator and build a table of signs.
The route is one line longer and needs no caveats at all.

*Case analysis.* For $B(x)>0$ multiply by the denominator as it is, for $B(x)<0$
flip the sign. Each of the two solutions is intersected with its own condition. The
route is shorter but needs care: the intersection is forgotten more often than the
algebra goes wrong.

**About a third route.** Multiplying by $B^2$ is legitimate too ($B^2>0$ always),
but the degree doubles, and instead of a quadratic inequality you get one of the
fourth degree. On Paper 1 that is a bad deal.

**What the exam checks.** In both archive blocks with a rational inequality the
marking is the same: A1 for the critical values, then an A1 for each interval.
Finding the boundaries is not enough — every piece of the answer has to be
presented.
""")

md(r"""
## Task 3 🟡 — a rational inequality

Given $f(x) = \dfrac{x^2 - 14x + 24}{2x + 6}$, solve the inequality $f(x) > x$.

The answer here is exact, with surds: $\sqrt{31}$ is written `sqrt(31)`.

*Source: November 2023 TZ2, Paper 2, Q11(f) (4 marks, calculator); the same
question word for word is November 2023 TZ1, Paper 2, Q11(f).*
""")

code(r"""
my3 = ...                # the solution set

verify_solution_set('Task 3', my3, (x**2 - 14*x + 24)/(2*x + 6) > x)
""")

md(r"""
---
## Theory 3. A modulus

A modulus is removed by its definition, and there are exactly two ways.

**By cases.** $|A| = A$ where $A \ge 0$, and $|A| = -A$ where $A<0$. Solve in each
case and intersect with the condition of the case.

**By the ready equivalences.** For $b>0$:

$$|A| < b \iff -b < A < b, \qquad |A| > b \iff A < -b \ \text{ or } \ A > b.$$

The first gives one interval, the second two. Confusing them is the most frequent
mistake, and it is easy to spot: if the answer to «$|A|>b$» came out as a single
piece, something is wrong.

**$f(|x|)$ and $|f(x)|$ are different things.** The difference shows on the graph:

* $|f(x)|$ reflects upwards everything that was below the $x$-axis;
* $f(|x|)$ throws away the left half of the graph and replaces it with the mirror
  image of the right half.

So the answer for $f(|x|)$ is always symmetric about zero, while for $|f(x)|$ it
generally is not. What appears in the archive is $f(|x|)$, and the symmetry of the
answer serves as a check: an answer that is not symmetric here is certainly wrong.
""")

md(r"""
## Task 4 🟡 — two questions from one graph

Given $f(x) = \dfrac{2x-1}{x+1}$.

**(a)** Solve $0 < f(x) < 2$.
**(b)** Solve $f(|x|) > 0$.

In part (b) it pays to work out what $f(|x|)$ equals first and only then solve.

*Source: May 2022 TZ2, Paper 1, Q3(c) and Q3(d) (1 + 2 marks, no calculator).*
""")

code(r"""
f4 = (2*x - 1)/(x + 1)

my4_a = ...              # the solution set of 0 < f(x) < 2
my4_b = ...              # the solution set of f(|x|) > 0

verify_solution_set('Task 4(a)', my4_a, (f4 > 0) & (f4 < 2))
verify_solution_set('Task 4(b)', my4_b, f4.subs(x, Abs(x)) > 0)
""")

md(r"""
---
## Theory 4. When the calculator does the solving

The sign of a calculator question is simple: the inequality holds functions of
different kinds — an exponential and a fraction, a logarithm and a polynomial. Such
equations have no general solution, and the markscheme does not ask for one: it asks
for the intersections to three significant figures.

**The working order.**

1. Draw both sides as two functions and find every intersection.
2. Mark the points where the expression is **undefined** — the zeros of
   denominators, the edges of a logarithm's domain. They are not solutions, but they
   are boundaries of intervals.
3. Between neighbouring marked points the sign is constant: check one point inside
   each interval.
4. Assemble the answer and decide about each end.

**The rounding trap.** Suppose an intersection is at $-2.41834\ldots$; to three
significant figures that is $-2.42$, and the rounding has shifted the end of the
interval outwards from the true one. In the exam such a writing is correct and
accepted, but on substituting, $-2.42$ itself no longer satisfies the inequality. Do
not be alarmed: check a little inside the interval, not at the rounded end
itself.

**An integer answer.** The question «the largest $n$ for which …», once the
inequality is solved, needs one more step: take the integer part **and check the two
neighbouring values**. The markscheme gives a mark precisely for the check — it cuts
off the off-by-one error, the most frequent one in this place.
""")

md(r"""
## Task 5 🔴 — an inequality only a GDC can solve

Given $f(x) = 2^{x} - 2^{-x}$ and $g(x) = \dfrac{x-1}{x^2-2x-3}$, where $x \ne -1$
and $x \ne 3$, solve the inequality $f(x) \ge g(x)$.

Write the ends found by the calculator to three significant figures. The check knows
about the rounding and will not quibble near the boundaries — but it checks
everything else, including the excluded points.

*Source: May 2022 TZ1, Paper 2, Q6(b) (4 marks, calculator).*
""")

code(r"""
h5 = 2**x - 2**(-x) - (x - 1)/(x**2 - 2*x - 3)


def holds5(v):
    '''Does f(x) >= g(x) hold at the point v.'''
    if v == -1 or v == 3:            # the function is undefined there
        return False
    return float(h5.subs(x, v).evalf()) >= 0


my5 = ...                # a union of intervals: Union(...)

verify_param_set('Task 5', my5, holds5, var=x, window=(-6, 6),
                 eps=Rational(1, 100), tol=0.005)
""")

md(r"""
## Task 6 🟡 — an integer answer

Rows are built out of cards: the first row has 2 cards and each next row is 3 cards
longer than the previous one, so $n$ rows take $\dfrac{n(3n+1)}{2}$ cards. There are
14 full packs of 52 cards.

Find the largest number of rows that can be built, and write down the totals of
cards for that number of rows and for one more — that is how the answer is
checked.

*Source: May 2025 TZ1, Paper 2, Q10(d) (3 marks, calculator).*
""")

code(r"""
my6_n = ...              # the largest whole number of rows
my6_t21 = ...            # how many cards that number of rows takes
my6_t22 = ...            # how many one more row would take

check_num('Task 6, the rows', my6_n, 6, '""" + D_N6 + r"""')
check_num('Task 6, the cards for them', my6_t21, 6, '""" + D_T21 + r"""')
check_num('Task 6, one row more', my6_t22, 6, '""" + D_T22 + r"""')
""")

md(r"""
---
## Theory 5. The discriminant as a condition on a letter

Here the topic turns round. Until now the inequality was given; now it has to be
**obtained** from the wording of the question, and its source is almost always the
discriminant.

$$\Delta > 0 \iff \text{two distinct real roots},$$
$$\Delta = 0 \iff \text{one (repeated) root},$$
$$\Delta < 0 \iff \text{no real roots}.$$

After that $\Delta$ is an expression in the letter, and the inequality in the letter
is solved with technique 1. All the work is in the first step: translating the words
of the question into one of the three signs.

**Careful with the word «quadratic».** The formula $\Delta = b^2-4ac$ assumes
$a \ne 0$. If the leading coefficient contains the letter, the case $a=0$ has to be
treated separately — the equation stops being quadratic. In the archive that case is
not an exotic one but part of the answer: the value of the letter that kills the
leading coefficient usually has to be excluded not because the discriminant failed
but because the equation degenerated into something else — linear, and sometimes
impossible altogether.

**How the condition sounds in a question.**

| In the question | The condition on $\Delta$ |
| --- | --- |
| two distinct real roots | $\Delta>0$ |
| the graph touches the $x$-axis | $\Delta=0$ |
| no real roots · the graph does not cross | $\Delta<0$ |
| the line is tangent to the curve | $\Delta=0$ after substituting |
| two distinct points of intersection | $\Delta>0$ after substituting |

The last two rows are the same technique hidden in geometry: substitute the line
into the curve, get a quadratic and look at its discriminant.

**After the inequality there is sometimes one more step.** «The largest integer»,
«$k \in \mathbb{Z}^+$», «how many values» — solving the inequality here is the
second-to-last line, not the answer.
""")

md(r"""
## Task 7 🟡 — a letter in the leading coefficient

For which values of $p$ does the equation

$$3px^2 + 2px + 1 - p = 0$$

have two distinct real roots?

The check does not use the discriminant: it substitutes your values of $p$ and
honestly counts how many distinct real roots the equation has. So it will notice the
degenerate case $p=0$.

*Source: November 2021, Paper 1, Q7(a) (5 marks, no calculator).*
""")

code(r"""
def two_roots7(pv):
    '''How many distinct real roots the equation has at p = pv.'''
    return len(set(real_roots(Poly(3*pv*x**2 + 2*pv*x + 1 - pv, x)))) == 2


my7 = ...                # the set of values of p

verify_param_set('Task 7', my7, two_roots7, var=p)
""")

md(r"""
## Task 8 🟢 — from an inequality to the largest integer

The function $f(x) = \tfrac12 x^2 + kx + 13$ has no real roots, and $k$ is a
positive integer. Find the set of values of $k$ for which there are no roots, and
the largest integer $k$.

*Source: November 2025 TZ3, Paper 1, Q9(a) (2 marks, no calculator).*
""")

code(r"""
my8_set = ...            # the set of values of k (not yet integers)
my8_k = ...              # the largest positive integer k

verify_solution_set('Task 8, the set', my8_set,
                    discriminant(x**2/2 + k*x + 13, x) < 0, var=k)
check_num('Task 8, the largest k', my8_k, 6, '""" + D_K8 + r"""')
""")

md(r"""
## Task 9 🟡 — a «show that» about the discriminant

A line meets a curve at two distinct points, and after the substitution the equation

$$x^2 - 2dx + 9d = 0$$

is obtained. Show that $d^2 - 9d > 0$.

Enter the discriminant of that equation — the expression from which, after dividing
by 4, the required inequality comes.

*Source: November 2023 TZ1, Paper 1, Q10(b)(ii) (3 marks, no calculator).*
""")

code(r"""
my9 = ...                # the discriminant of the equation

verify_identity('Task 9', my9, 4*d**2 - 36*d, var=d)
""")

md(r"""
## Task 10 🟡 — an integer restriction on top of an inequality

The numbers $a$, $b$, $c$ independently take integer values from 1 to 6. The graph
of $y = ax^2 + bx + c$ crosses the $x$-axis at two distinct points.

Find all the possible values of the product $ac$.

Think about why 7 is not in the answer, even though it satisfies the inequality.

*Source: May 2024 TZ2, Paper 3, Q2(d) (3 marks, calculator).*
""")

code(r"""
my10 = [...]             # all the possible values of ac

check_set('Task 10', my10, '""" + D_AC10 + r"""')
""")

md(r"""
---
## Theory 6. The signs of the roots

When the question is not about the roots themselves but about their **signs**, the
roots do not have to be found. Everything is visible from Vieta's formulas for
$ax^2+bx+c=0$:

$$\alpha\beta = \frac ca, \qquad \alpha+\beta = -\frac ba.$$

Hence a table worth remembering whole:

| Requirement | Conditions |
| --- | --- |
| one root positive, the other negative | $\alpha\beta<0$ |
| both roots positive | $\alpha\beta>0$, $\alpha+\beta>0$, $\Delta\ge 0$ |
| both roots negative | $\alpha\beta>0$, $\alpha+\beta<0$, $\Delta\ge 0$ |
| the roots have the same sign | $\alpha\beta>0$, $\Delta>0$ |

**Why the first row has only one condition.** If $\frac ca<0$ then
$\Delta = b^2-4ac > 0$ automatically: $-4ac$ is positive. Requiring the roots to be
real separately is unnecessary, and the markscheme gives nothing extra for it.

**Why the other rows need $\Delta$.** The conditions $\alpha\beta>0$ and
$\alpha+\beta>0$ hold for a pair of complex conjugate roots with a positive real
part as well. Without the discriminant the answer comes out wider than the right
one.

**An intersection, not a union.** When there are several conditions, the answer is
their **intersection**. In task 19 that is laid out in two parts: first the set from
the discriminant, then the intersection with the condition on the sign.
""")

md(r"""
## Task 11 🟢 — one root positive, the other negative

For which values of $k$ does the equation

$$kx^2 - (k+3)x + 2k + 9 = 0$$

have one positive and one negative root?

*Source: May 2022 TZ1, Paper 2, Q8(b) (3 marks, calculator).*
""")

code(r"""
def signs11(kv):
    '''One root negative and the other positive — at k = kv.'''
    if kv == 0:
        return False                 # the equation has stopped being quadratic
    found = sorted(set(real_roots(Poly(kv*x**2 - (kv + 3)*x + 2*kv + 9, x))))
    return len(found) == 2 and found[0] < 0 < found[1]


my11 = ...               # the set of values of k

verify_param_set('Task 11', my11, signs11)
""")

md(r"""
---
## Theory 7. «For all $x$» and «exactly two solutions»

The third turn of the topic: the question is not about the roots and not about their
signs but about the **number** of solutions — and the answer turns out to be a set
of values of the parameter again.

**«True for all $x$».** The condition $F(x) \le 0$ for all $x$ is equivalent to a
single inequality:

$$\max_{x} F(x) \le 0.$$

For a quadratic $F$ the maximum is at the vertex, and the most convenient thing is
to complete the square: $-2(x+3)^2 + 7 + k$ has maximum $7+k$, attained at $x=-3$,
so the condition becomes $7+k\le 0$. A second route is through the discriminant: «a
downward parabola does not rise above the axis» is $\Delta \le 0$. Both are
accepted.

**«Exactly $N$ solutions».** The thought that works is this: the number of solutions
changes only where the solutions **merge** (a touching) or **disappear** (leave the
domain). So:

1. find those special values of the parameter — they are the boundaries of the
   answer;
2. between them the number of solutions is constant, so one point per interval is
   enough to check.

Hence the typical shape of the answer: an interval with a **point removed**. That
removed point is exactly the value of the parameter at which two solutions merged
into one, and so it is not in the answer to «exactly two», while it makes up the
whole answer to «exactly one». Two questions, two answers, and the same point plays
opposite roles in them.

**About writing the answer.** «$m \in \mathbb{R}^+,\ m \ne 2$» and
«$0<m<2$ or $m>2$» are the same thing, and the markscheme accepts both. But «$m>0$»
with no caveat is a different answer and a different mark.
""")

md(r"""
## Task 12 🟡 — «for all $x$»

Given $f(x) = 6x^2 - 12x + 1$ and $g(x) = -x + c$. It is known that
$(g \circ f)(x) \le 0$ for all $x \in \mathbb{R}$.

Find the set of possible values of $c$.

*Source: May 2021 TZ2, Paper 2, Q4(b) (4 marks, calculator).*
""")

code(r"""
def never_positive(cv):
    '''Is it true that (g o f)(x) <= 0 for all x — at c = cv.'''
    return maximum(-(6*x**2 - 12*x + 1) + cv, x) <= 0


my12 = ...               # the set of values of c

verify_param_set('Task 12', my12, never_positive, var=c)
""")

md(r"""
## Task 13 🔴 — as many solutions as there are normals

A Paper 3 investigation. It has been shown that a normal to the curve $H$ with
gradient $m$ exists if and only if

$$c = \frac{1}{\sqrt m} - m\sqrt m \qquad\text{or}\qquad
c = -\frac{1}{\sqrt m} + m\sqrt m,$$

and each value of $c$ corresponds to its own normal.

**(a)** Find the set of values of $m$ for which there are exactly two normals.
**(b)** Find the set of values of $m$ for which there is exactly one normal.

The answer in (b) is a single point: `FiniteSet(...)`.

*Source: November 2025 TZ1, Paper 3, Q1(b)(ii), (c)(i), (c)(ii) (4 marks,
calculator).*
""")

code(r"""
def normals(mv):
    '''How many different normals correspond to the gradient m = mv.'''
    if mv <= 0:
        return 0                     # sqrt(m) is undefined
    return len({simplify(1/sqrt(mv) - mv*sqrt(mv)),
                simplify(-1/sqrt(mv) + mv*sqrt(mv))})


my13_two = ...           # exactly two normals
my13_one = ...           # exactly one normal

verify_param_set('Task 13(a)', my13_two, lambda mv: normals(mv) == 2, var=m)
verify_param_set('Task 13(b)', my13_one, lambda mv: normals(mv) == 1, var=m)
""")

md(r"""
## Task 14 🔴 — the number of intersections

A Paper 3 investigation. The graphs of $y = a^x$ and $y = \log_a x$ with $a > 1$ are
considered.

**(a)** For which $a$ do the graphs meet at two points?
**(b)** For which $a$ do they not meet at all?

The answer is exact: the boundary is expressed through $\mathrm{e}$.

*Source: May 2023 TZ2, Paper 3, Q1(f)(i) and (f)(ii) (2 marks, calculator).*
""")

code(r"""
import math

# For a > 1 the two curves are inverses of each other and both increasing, so every
# intersection lies on the line y = x, and the question reduces to the number of
# solutions of a^x = x. The substitution x = e^u turns it into u*e^{-u} = ln a:
# that way the second root does not run off to infinity as a -> 1 and stays visible.
def crossings(av):
    '''How many intersections the graphs have at a = av.'''
    a_ = float(av)
    if a_ <= 1:
        return None                  # the base has to be greater than 1
    if abs(math.log(a_) - math.exp(-1)) < 1e-9:
        return None                  # a touching: nobody counts numerically here
    return count_roots(lambda t_: t_*math.exp(-t_) - math.log(a_), -2, 40)


my14_two = ...           # two intersections
my14_none = ...          # none at all

verify_param_set('Task 14(a)', my14_two, lambda av: crossings(av) == 2,
                 var=a, window=(0, 4))
verify_param_set('Task 14(b)', my14_none, lambda av: crossings(av) == 0,
                 var=a, window=(0, 4))
""")

md(r"""
---
## Theory 8. Proving an inequality

Proving is not the same as solving. There is no set in the answer; there is a chain,
and its last step has to be obvious.

**The general rule.** «Prove $A \ge B$» means «prove $A - B \ge 0$», and the
non-negativity has to be **visible from the writing**. Hence four moves, and all
four appear in the archive.

*Completing the square.* The most frequent. The expression
$a^2+b^2+c^2-ab-bc-ca$ says nothing, while the equal
$\tfrac12\left[(a-b)^2+(b-c)^2+(c-a)^2\right]$ says everything. The M1 is precisely
for attempting to write the expression as a sum of squares.

*Monotonicity.* $n^2 \ge 2n-1$ is obvious, it is $(n-1)^2\ge0$; apply the increasing
function $y=\sqrt{x}$ and get $n \ge \sqrt{2n-1}$. The key word in the marking is
«increasing»: without a reference to monotonicity the step is not credited.

*A known inequality.* The triangle inequality $|a+b| \le |a| + |b|$, the arithmetic
mean against the geometric mean, the condition for equality. On Paper 3 such an
inequality is first proved and then applied — in that order, not the other way
round.

*By contradiction.* Suppose the opposite and derive something plainly false —
usually «a square is negative»: supposing $x^2 + 1 < 2x$ leads to $(x-1)^2 < 0$. The
R1 is for the explicit sentence about the contradiction, not for the working.

**About AG.** If the answer is printed in the question («show that … $\ge$ …»), the
marks are for the derivation, not for the answer. The last line has to be a
conclusion: «a square is non-negative, therefore …». Without it the last mark is
taken off even with correct algebra.

**What is checked in this practicum.** The check requires a **non-negative
writing**: it will not accept the expanded form $4a^2+12ab+9b^2$, although it equals
$(2a+3b)^2$. That is the same requirement on the form as `verify_factored` in
practicum A4 — there a product was asked for, here a square.
""")

md(r"""
## Task 15 🟢 — monotonicity

Show that $1 + \log_2 n \ge \log_2(n+1)$ for $n \in \mathbb{Z}^+$.

**(a)** Enter the expression the left-hand side reduces to, so that two logarithms
can be compared.
**(b)** Enter the set on which the remaining inequality $2n \ge n+1$ holds.

*Source: May 2025 TZ1, Paper 1, Q8(a) (2 marks, no calculator).*
""")

code(r"""
my15_log = ...           # what to replace 1 + log_2(n) with
my15_set = ...           # where 2n >= n + 1 holds

verify_identity('Task 15(a)', my15_log, 1 + log(n, 2), var=n)
verify_solution_set('Task 15(b)', my15_set, 2*n >= n + 1, var=n)
""")

md(r"""
## Task 16 🟡 — complete the square

The velocity of a particle is given by $v(\tau) = \mathrm{e}^{\,T-\tau} - 1$, where
$T$ is a fixed moment of time. Show that

$$v(T-k) + v(T+k) \ge 0$$

for all $k$.

**(a)** Enter the sum $v(T-k)+v(T+k)$ in simplified form.
**(b)** Write the same thing in a form from which the non-negativity is obvious.

*Source: May 2021 TZ2, Paper 1, Q11(e) (3 marks, no calculator).*
""")

code(r"""
my16_sum = ...           # the sum after simplifying
my16_sq = ...            # the same thing as a square

verify_identity('Task 16(a)', my16_sum, exp(k) + exp(-k) - 2, var=k)
verify_nonneg_form('Task 16(b)', my16_sq, exp(k) + exp(-k) - 2)
""")

md(r"""
## Task 17 🟡 — by contradiction

Prove by contradiction that $\sqrt{xy} \le \dfrac{x+y}{2}$ for all
$x, y \in \mathbb{R}^+$.

**(a)** Suppose the opposite and square both sides. Enter the expression $F$ for
which the resulting statement has the form $0 > F$.
**(b)** Write $F$ in a form from which the contradiction is visible.

*Source: November 2025 TZ3, Paper 2, Q9 (5 marks, calculator).*
""")

code(r"""
my17_expr = ...          # F after squaring and rearranging
my17_sq = ...            # F as a square

verify_identity('Task 17(a)', my17_expr, x**2 - 2*x*y + y**2, var=x)
verify_nonneg_form('Task 17(b)', my17_sq, x**2 - 2*x*y + y**2)
""")

md(r"""
## Task 18 🟡 — two short deductions from Paper 3

**(a)** Given that $a = 2st - s^2$ and $b = t^2 - s^2$, where $s, t \in
\mathbb{R}^+$, and that $a < b$, show that $t > 2s$.

Enter the difference $b - a$ **as a product** — the conclusion comes out of it in
one line.

**(b)** The numbers $x_1,\dots,x_n$ are positive, their sum is $T$, and by the
AM–GM inequality their product does not exceed $\left(\frac{T}{n}\right)^n$. Write
down the largest possible value of the product, $M_n(T)$.

*Sources: May 2025 TZ3, Paper 3, Q2(f) (2 marks) and May 2023 TZ1, Paper 3,
Q2(d)(ii) (4 marks), both calculator papers.*
""")

code(r"""
my18_diff = ...          # b - a as a product
my18_max = ...           # M_n(T)

verify_factored('Task 18(a)', my18_diff, t**2 - 2*s*t, var=t, n=2)
check_series('Task 18(b)', my18_max, '""" + D_M18 + r"""', var=n)
""")

md(r"""
---
## Trainer: name the technique in five seconds

Below are fifteen statements with no solutions. For each one write the code of the
technique — and nothing else. Nothing has to be computed; the aim is for the first
move to be found before the computing starts.

The codes: `crit` (critical values and the sign) · `rat` (a rational inequality) ·
`abs` (a modulus) · `gdc` (numerically on the GDC) · `disc` (the discriminant as a
condition) · `vieta` (the signs of the roots) · `count` (the number of solutions) ·
`prove` (prove an inequality)

1. Solve $x^2 - 4x - 5 \le 0$.
2. For which $k$ does $x^2 + kx + 9 = 0$ have two distinct real roots?
3. Solve $\dfrac{x-1}{x+2} \ge 0$.
4. Prove that $a^2 + b^2 \ge 2ab$.
5. Solve $|2x - 3| < 5$.
6. For which $m$ are both roots of $x^2 - mx + 4 = 0$ positive?
7. Solve $2^x \ge x + 3$ (Paper 2).
8. For which $c$ does the line $y = x + c$ not meet the parabola $y = x^2$?
9. Find all $a$ for which $|x^2-4| = a$ has exactly three solutions.
10. Solve $x^3 > x$.
11. Show that $\dfrac{x+y}{2} \ge \sqrt{xy}$ for $x,y>0$.
12. Solve $\dfrac{x^2-1}{x-3} < 0$.
13. For which $k$ is $kx^2 + 2x + k$ positive for all $x$?
14. Find the largest integer $n$ for which $\dfrac{n(n+1)}{2} < 100$.
15. From the graph of $f$, solve $f(|x|) > 0$.
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
## Task 19 🔴 — on the timer, 12 minutes

A whole Paper 1 question with no calculator. Seven marks, target time about 12
minutes.

Given the equation $x^2 + kx + 15 - k = 0$.

**(a)** Find all the values of $k$ for which the equation has two distinct real
roots.

**(b)** Find all the values of $k$ for which those two roots are either both
positive or both negative.

*Source: May 2025 TZ2, Paper 1, Q5 (5 + 2 marks, no calculator).*
""")

code(r"""
def two_distinct19(kv):
    '''Two distinct real roots at k = kv.'''
    return len(set(real_roots(Poly(x**2 + kv*x + 15 - kv, x)))) == 2


def same_sign19(kv):
    '''Two distinct real roots of the same sign at k = kv.'''
    found = sorted(set(real_roots(Poly(x**2 + kv*x + 15 - kv, x))))
    return len(found) == 2 and found[0]*found[1] > 0


my19_a = ...             # the set from part (a)
my19_b = ...             # the set from part (b)

verify_param_set('Task 19(a)', my19_a, two_distinct19)
verify_param_set('Task 19(b)', my19_b, same_sign19)
""")

md(r"""
---
# Solutions

Below is a full working of every task with the markscheme's marking. Open them after
you have solved on your own: the working explains not only the answer but what
exactly the marks are given for.
""")

md(r"""
## Solution 1 — a whole quadratic inequality

Expand and take everything to one side:

$$5(x+2)^2 - 5 \le 40 \iff 5x^2 + 20x + 15 \le 40
\iff x^2+4x-5\le0 \iff (x+5)(x-1)\le 0.$$

The critical values are $x=-5$ and $x=1$. The parabola opens upwards and lies below
the axis between the roots:

$$-5 \le x \le 1.$$

The ends belong: the inequality is non-strict and at those points the left-hand side
equals the right.

```python
my1 = Interval(-5, 1)
```

**The marking.** A1 for reducing to $(x+2)^2\le9$ or $x^2+4x-5\le0$, M1 for
attempting to find the critical values, A1 for $x=-5$ and $x=1$, A1 for the answer as
a set.

**The fast route.** From the form $5(x+2)^2-5\le40$ at once $(x+2)^2\le9$, that is,
$|x+2|\le3$, that is, $-3\le x+2\le3$. The answer comes out in one line, with no
expanding.

**Where the mark goes.** Writing $x \le -5$ or $x \ge 1$ — the side is confused. The
check takes a second: put $x=0$ in. You get $-5\le0$, which is true, so zero is in
the answer, so the answer is the interval between the roots and not everything
else.
""")

md(r"""
## Solution 2 — when the domain changes the answer

$$d^2 - 9d > 0 \iff d(d-9) > 0.$$

The critical values are $d=0$ and $d=9$. The parabola opens upwards and lies above
the axis outside the roots:

$$d<0 \quad\text{or}\quad d>9.$$

Now recall the condition $d \in \mathbb{R}^+$. The first half falls away
entirely:

$$d > 9.$$

```python
my2 = Interval.open(9, oo)
```

**The marking.** M1 for $d(d-9)>0$, or for a sketch, or for checking the signs, or
for $d^2>9d$; A1 for $d>9$.

**Why it could not be divided by $d$ straight away.** The temptation is this:
$d^2>9d$, divide by $d$, get $d>9$. The answer is right, but only because $d>0$ was
given. Without that condition dividing by $d$ is an error and half the answer is
lost. Get into the habit of stating the sign of the divisor out loud: that statement
is what the mark is for here.

**What the practicum checks.** The check compares your answer with the solution set
**without** narrowing by the domain — so a forgotten condition $d>0$ shows up as the
extra piece $d<0$.
""")

md(r"""
## Solution 3 — a rational inequality

Everything to one side and to a common denominator:

$$\frac{x^2-14x+24}{2x+6} - x > 0
\iff \frac{x^2-14x+24-x(2x+6)}{2x+6} > 0
\iff \frac{-x^2-20x+24}{2(x+3)} > 0.$$

Multiply by $-1$ and flip the sign:

$$\frac{x^2+20x-24}{x+3} < 0.$$

The critical values: the zeros of the numerator $x = -10 \pm 2\sqrt{31}$ (that is
$-21.1355\ldots$ and $1.1355\ldots$) and the zero of the denominator $x=-3$. The
table of signs on four intervals:

| interval | numerator | denominator | fraction |
| --- | --- | --- | --- |
| $x<-10-2\sqrt{31}$ | $+$ | $-$ | $-$ |
| $-10-2\sqrt{31}<x<-3$ | $-$ | $-$ | $+$ |
| $-3<x<-10+2\sqrt{31}$ | $-$ | $+$ | $-$ |
| $x>-10+2\sqrt{31}$ | $+$ | $+$ | $+$ |

The negative ones are wanted:

$$x < -10-2\sqrt{31} \quad\text{or}\quad -3 < x < -10+2\sqrt{31}.$$

```python
my3 = Union(Interval.open(-oo, -10 - 2*sqrt(31)),
            Interval.open(-3, -10 + 2*sqrt(31)))
```

**The marking.** A1 for either of the numbers $-21.1$ or $1.14$ appearing; then
A1A1A1 for the pieces of the answer: for $x<-21.1$, for the right ends $-3$ and
$1.14$, and for the interval between them.

**Why $-3$ is excluded.** It is the zero of the denominator and $f$ is undefined
there. Such an end belongs to the answer for no sign of inequality at all.

**The temptation to avoid.** Multiplying both sides by $2x+6$ and solving
$x^2-14x+24 > x(2x+6)$. For $x<-3$ the denominator is negative, the inequality
flips, and instead of two intervals one comes out. The answer looks convincing and
costs all four marks.

**The same question twice.** In November 2023 it stood in both TZ1 and TZ2 — word
for word, with the same numbers. The marking of the two zones is identical.
""")

md(r"""
## Solution 4 — two questions from one graph

$f(x) = \dfrac{2x-1}{x+1}$.

**(a)** It is convenient to rewrite it: $f(x) = 2 - \dfrac{3}{x+1}$.

The right inequality $f(x)<2$ means $-\frac{3}{x+1}<0$, that is, $x+1>0$, that is,
$x>-1$. It holds on the whole right part and nowhere to the left.

The left inequality $f(x)>0$ means $\frac{2x-1}{x+1}>0$: the critical values are
$\frac12$ and $-1$, and the fraction is positive for $x<-1$ and for $x>\frac12$.

Intersecting: $x > \frac12$.

**(b)** First work out what $f(|x|)$ is:

$$f(|x|) = \frac{2|x|-1}{|x|+1}.$$

The denominator is always positive, so the sign is decided by the numerator:

$$2|x|-1>0 \iff |x| > \tfrac12 \iff x<-\tfrac12 \ \text{ or } \ x>\tfrac12.$$

```python
my4_a = Interval.open(Rational(1, 2), oo)
my4_b = Union(Interval.open(-oo, -Rational(1, 2)),
              Interval.open(Rational(1, 2), oo))
```

**The marking.** (a): A1, the answer is read off the graph and any writing is
accepted. (b): M1 for a sketch or for solving $2x-1=0$ and arriving at the critical
points $\pm\frac12$, A1 for the answer.

**A check by symmetry.** For $f(|x|)$ the answer has to be symmetric about zero —
the function is even by construction. If it came out asymmetric, the mistake has
been found before any algebra was checked.

**About the archive's tags.** This block is tagged `formula_extraction_uncertain`,
and for a reason: the extract from the markscheme talks about sketching $|f(x)|$,
while the answer recorded in the same place, $x<-\frac12$ or $x>\frac12$,
corresponds to $f(|x|)>0$. Through $|f(x)|$ it cannot be obtained: $|f(x)|>0$ means
only $x \ne \frac12$. The practicum uses the statement that agrees with the answer;
the working is in the technique card.
""")

md(r"""
## Solution 5 — an inequality only a GDC can solve

Find the intersections of $y=f(x)$ and $y=g(x)$ on the calculator:

$$x = -1.26686\ldots,\qquad x = 0.177935\ldots,\qquad x = 3.06167\ldots$$

that is, $-1.27$, $0.178$ and $3.06$ to three significant figures. Add to them the
points where $g$ is undefined: $x=-1$ and $x=3$ (there $x^2-2x-3 = (x+1)(x-3)$
vanishes).

The five marked points split the line into six intervals. Check one point in each
(the values of $f-g$):

| interval | test | $f-g$ |
| --- | --- | --- |
| $x<-1.27$ | $-2$ | $-3.15$ |
| $-1.27<x<-1$ | $-1.2$ | $+0.76$ |
| $-1<x<0.178$ | $0$ | $-0.33$ |
| $0.178<x<3$ | $1$ | $+1.5$ |
| $3<x<3.06$ | $3.01$ | $-42$ |
| $x>3.06$ | $4$ | $+15.3$ |

Collect the intervals with the sign $+$, including the intersection ends (the
inequality is non-strict) and excluding the poles:

$$-1.27 \le x < -1 \quad\text{or}\quad 0.178 \le x < 3
\quad\text{or}\quad x \ge 3.06.$$

```python
my5 = Union(Interval.Ropen(-1.27, -1),
            Interval.Ropen(0.178, 3),
            Interval(3.06, oo))
```

**The marking.** M1 for attempting to find at least one intersection, A1 for all
three values, then A1A1A1 — a mark for each of the three intervals of the answer.

**Three of the four marks are for the writing.** The calculator does the computing;
the candidate's work is in understanding where the inequality holds and which ends
belong. That is the substance of the question.

**Why the ends differ.** $-1.27$ came from an intersection of the graphs — there
$f=g$, the inequality is non-strict and the end belongs. $-1$ came from a zero of
the denominator — nothing is defined there and the end is excluded. Both situations
stand side by side in one answer, and they have to be told apart each time afresh.

**About the check in the practicum.** It tries points inside your intervals and in
the gaps between them, and does not quibble at the boundaries: an end rounded to
three figures legitimately differs from the exact one. So the check here is more
lenient than the exam — in the exam $-1.27 < x$ instead of $-1.27 \le x$ costs a
mark.

**About the archive's tags.** The archive records $f(x)=2^{-x}-2^{x}$. With such an
$f$ none of the three intersections comes out: substituting gives $f=-g$ rather than
$f=g$. The sign was confused in the extraction, and the right writing is
$f(x)=2^{x}-2^{-x}$; with it both the points and the whole answer reproduce. The
check is in `verify_a8.py`.
""")

md(r"""
## Solution 6 — an integer answer

There are $14 \cdot 52 = 728$ cards in all. The condition:

$$\frac{n(3n+1)}{2} \le 728 \iff 3n^2 + n - 1456 \le 0.$$

Solve it as an equation: $n = \dfrac{-1 \pm \sqrt{1 + 4\cdot3\cdot1456}}{6}
= \dfrac{-1 \pm \sqrt{17473}}{6}$, and the positive root is $n = 21.8642\ldots$

So $n \le 21.86$ and the largest integer is $n = 21$.

Check both neighbouring values:

$$\frac{21 \cdot 64}{2} = 672 \le 728, \qquad
\frac{22 \cdot 67}{2} = 737 > 728.$$

```python
my6_n = 21
my6_t21 = 672
my6_t22 = 737
```

**The marking.** M1 for attempting to solve $\frac{n(3n+1)}2 \le 728$; A1 for
$n=21.8642\ldots$ **or** for the pair $t_{21}=672$, $t_{22}=737$; A1 for the answer
21.

**Two roads, the same marks.** The markscheme accepts both solving the inequality
and searching directly: compute the total for 21 and for 22 and see where it passed
728. The second route is faster on a GDC and needs no surds.

**Where the mark goes.** Writing $21.9$ — not noticing that the question is about a
number of rows, and a number of rows is not a fraction. More often still, rounding
up to 22: the rounding here is not by the rules of arithmetic but by the sense of the
question, and it is always down.
""")

md(r"""
## Solution 7 — a letter in the leading coefficient

The equation is quadratic when $3p \ne 0$. Compute the discriminant:

$$\Delta = (2p)^2 - 4\cdot 3p \cdot (1-p) = 4p^2 - 12p + 12p^2
= 16p^2 - 12p.$$

Two distinct real roots means $\Delta>0$:

$$16p^2 - 12p > 0 \iff 4p(4p-3) > 0.$$

The critical values are $p=0$ and $p=\frac34$; the parabola opens upwards:

$$p<0 \quad\text{or}\quad p>\tfrac34.$$

The case $p=0$ is excluded anyway: at $p=0$ the equation becomes $1=0$ and has no
roots at all.

```python
my7 = Union(Interval.open(-oo, 0), Interval.open(Rational(3, 4), oo))
```

**The marking.** M1 for using the discriminant, A1 for $16p^2-12p>0$, M1 for
attempting to find the critical values, M1 for realising that the sign wanted is
$>$, A1 for the answer.

**Why the boundary $p=0$ is not excluded twice.** Two independent considerations
exclude it: there $\Delta=0$ (so there would be one root) and there the equation is
not quadratic. The coincidence is convenient but not to be relied on: in other
questions the degenerate case falls **inside** the set found from the discriminant,
and it has to be thrown out separately.

**How the check catches that.** It does not compute the discriminant at all. For
every test $p$ it takes the equation and counts how many distinct real roots it has.
At $p=0$ there are none, and an attempt to include that point in the answer will be
noticed.
""")

md(r"""
## Solution 8 — from an inequality to the largest integer

The discriminant of $f(x) = \frac12x^2 + kx + 13$:

$$\Delta = k^2 - 4\cdot\tfrac12\cdot13 = k^2 - 26.$$

There are no real roots when $\Delta<0$:

$$k^2 < 26 \iff -\sqrt{26} < k < \sqrt{26}.$$

Since $\sqrt{26} = 5.0990\ldots$ and $k$ is a positive integer, the largest $k$ that
works is 5.

```python
my8_set = Interval.open(-sqrt(26), sqrt(26))
my8_k = 5
```

**The marking.** A1 for the right discriminant $k^2-26$, M1 for realising that the
sign wanted is $<$; the answer $k=5$ is printed in the question (AG).

**Careful with AG.** Since the answer is given, the mark is for the derivation.
Writing «$k=5$, QED» scores zero. Both lines are needed: the discriminant and the
condition on its sign.

**Why not 5.099.** The question is about an integer $k$, and the solution set of the
inequality is the second-to-last step here. That two-storey structure is the topic's
signature: first an inequality, then one more condition on top of it.
""")

md(r"""
## Solution 9 — a «show that» about the discriminant

Two distinct points of intersection mean that the quadratic $x^2-2dx+9d=0$ has two
distinct real roots, that is, $\Delta>0$:

$$\Delta = (-2d)^2 - 4\cdot1\cdot9d = 4d^2 - 36d.$$

The condition $4d^2-36d>0$, after dividing by 4, gives what was required:

$$d^2 - 9d > 0. \qquad \blacksquare$$

```python
my9 = 4*d**2 - 36*d
```

**The marking.** A1 for writing the discriminant $(-2d)^2-4\cdot1\cdot9d$, M1 for
the sentence «the discriminant is positive», A1 for $4d^2-36d>0$; the step to
$d^2-9d>0$ is AG.

**What is really being tested here.** Not losing factors. $(-2d)^2 = 4d^2$, not
$-4d^2$ and not $2d^2$; $4\cdot1\cdot9d = 36d$. Either mistake gives an
outwardly similar inequality from which the required one does not follow.

**The link with task 2.** It is the same question, parts (b)(ii) and (b)(iii) of one
block: here the inequality is obtained, there it is solved. The order in the
practicum is reversed on purpose — first you should learn to solve them, and only
then find out where such inequalities come from.
""")

md(r"""
## Solution 10 — an integer restriction on top of an inequality

Two distinct points of intersection with the $x$-axis mean $\Delta>0$:

$$b^2 - 4ac > 0 \iff ac < \frac{b^2}{4}.$$

The numbers run from 1 to 6, so the largest $b^2$ is 36 and

$$ac < 9.$$

What is left is to see which values the product $ac$ can take at all. Both factors
are integers from 1 to 6, so the possibilities are

$$1,\,2,\,3,\,4,\,5,\,6,\,8,\,9,\,10,\,12,\dots$$

The number 7 is not among them: 7 is prime and cannot be split into two factors from
1 to 6. So the answer is

$$ac \in \{1,\,2,\,3,\,4,\,5,\,6,\,8\}.$$

```python
my10 = [1, 2, 3, 4, 5, 6, 8]
```

**The marking.** M1 for $b^2-4ac>0$, A1 for $b^2 \le 36$ or for $ac \le 8$, A1 for
the full list.

**Two restrictions, not one.** The inequality gives $ac<9$, but the answer is
shorter: the fact that $ac$ is a product of two numbers from $\{1,\dots,6\}$ is also
at work. Missing the second restriction is easy, and the mark for the full list is
then lost.

**A check on the answer.** For each value in the list it pays to name a pair:
$8 = 2\cdot4$, $6 = 1\cdot 6 = 2\cdot 3$, while for 7 there is no pair. That is the
check the A1 stands for.
""")

md(r"""
## Solution 11 — one root positive, the other negative

Roots of different signs means their product is negative:

$$\alpha\beta = \frac{2k+9}{k} < 0.$$

That is a rational inequality, technique 2. The critical values: $k=-\frac92$ (the
zero of the numerator) and $k=0$ (the zero of the denominator). The fraction is
negative between them:

$$-\frac92 < k < 0.$$

```python
my11 = Interval.open(Rational(-9, 2), 0)
```

**The marking.** M1 for realising that the product of the roots is negative; A1 for
$\frac{2k+9}{k}<0$ and the critical values $0$ and $-\frac92$; A1 for the answer.

**Why no discriminant is needed.** If $\frac ca<0$ then $-4ac>0$ and
$\Delta = b^2-4ac>0$ automatically. The roots are real by themselves and no separate
condition has to be written. That is the only row of the table in theory 6 where
this happens.

**Why $k=0$ is excluded.** There the equation stops being quadratic: what is left is
$-3x+9=0$, with the single root $x=3$. Not «one positive and one negative» but one
root only. Both ends of the answer are excluded, for different reasons, and that is
worth saying out loud.

**How the check sees it.** It substitutes test values of $k$, finds the roots and
looks at their signs — exactly what the question asks about. Vieta's formula takes no
part in the check.
""")

md(r"""
## Solution 12 — «for all $x$»

Build the composition:

$$(g\circ f)(x) = g\bigl(6x^2-12x+1\bigr) = -(6x^2-12x+1) + c
= -6x^2 + 12x - 1 + c.$$

That is a downward parabola, so «$\le 0$ for all $x$» is equivalent to «the maximum
is $\le 0$». Complete the square:

$$-6x^2+12x-1+c = -6(x-1)^2 + 5 + c.$$

The maximum is $5+c$, attained at $x=1$. The condition:

$$5 + c \le 0 \iff c \le -5.$$

```python
my12 = Interval(-oo, -5)
```

**The marking.** A1 for the composition in the form $-6(x-1)^2+5+c$, M1 for moving
to the range or for computing $g(-5)$, A1 for $5+c\le0$, A1 for the answer.

**Three legitimate routes, all with full marks.**

*Through the vertex*, as above.

*Through the discriminant.* A downward parabola does not rise above the axis exactly
when $\Delta \le 0$: $144 - 4\cdot(-6)(c-1) \le 0$, hence $120+24c\le0$, that is,
$c\le-5$.

*Through the range.* The range of $f$ is $[-5,\infty)$, because
$f(x) = 6(x-1)^2-5$. The function $g$ is decreasing, so the greatest value of
$g(f(x))$ is attained at the smallest $f$, that is, it equals $g(-5) = 5+c$.

**Why the end belongs.** At $c=-5$ the maximum is zero and the inequality is
non-strict: $(g\circ f)(1) = 0 \le 0$. The answer is a ray with its end included,
and the check tells the difference.
""")

md(r"""
## Solution 13 — as many solutions as there are normals

The two expressions for $c$ differ only in sign:

$$c_1 = \frac1{\sqrt m} - m\sqrt m, \qquad c_2 = -c_1.$$

**(a)** There are two normals when $c_1 \ne c_2$, that is, $c_1 \ne 0$, and when
both expressions exist at all, that is, $m>0$.

$$c_1 = 0 \iff \frac1{\sqrt m} = m\sqrt m \iff 1 = m^2 \iff m = 1$$

(the root $m=-1$ falls away, $m>0$). So

$$m>0,\ m \ne 1.$$

**(b)** There is exactly one normal precisely when the two values have merged:
$m = 1$.

```python
my13_two = Union(Interval.open(0, 1), Interval.open(1, oo))
my13_one = FiniteSet(1)
```

**The marking.** (b)(ii): A1 for $m \in \mathbb{R}^+$. (c)(i): A1 for $m=1$.
(c)(ii): A1A1 — a mark for $0<m<1$ and a mark for $m>1$.

**Where the inequality is here.** At first sight there is none: the question is
about a number. But the answer is a set of values of the parameter, and it is
obtained by exactly the move of theory 7: find the values at which the solutions
merge ($m=1$) or disappear ($m\le0$), and throw them out.

**About the removed point.** The answer $m>0$ with no caveat $m\ne1$ is a different
answer and a different mark. The marking records that directly: (c)(ii) carries two
marks, one for each piece.

**About the archive's tags.** In the short description of the block the formula is
recorded as $c = \frac{1}{m^{1/2}} - \frac{1}{m^{1/2}}$, that is, identically zero.
The extract from the markscheme given in the same place has
$c = \pm\left(\frac1{\sqrt m} - m\sqrt m\right)$ — that is the right writing, and it
is the one the practicum uses.
""")

md(r"""
## Solution 14 — the number of intersections

For $a>1$ the functions $y=a^x$ and $y=\log_a x$ are inverses of each other and both
increasing. The graphs of increasing inverse functions are symmetric about the line
$y=x$, and they can only meet **on** that line. So the number of intersections equals
the number of solutions of

$$a^x = x.$$

Take logarithms: $x\ln a = \ln x$. The substitution $x = \mathrm{e}^u$ turns that
into

$$u\,\mathrm{e}^{-u} = \ln a.$$

On the left is a function with a single maximum: the derivative
$(1-u)\mathrm{e}^{-u}$ vanishes at $u=1$ and the maximum is $\mathrm{e}^{-1}$. So:

* for $\ln a < \frac1{\mathrm e}$ — two solutions;
* for $\ln a = \frac1{\mathrm e}$ — one (a touching);
* for $\ln a > \frac1{\mathrm e}$ — none.

The condition $\ln a < \frac1{\mathrm e}$ means $a < \mathrm{e}^{1/\mathrm e}$.
Together with $a>1$:

$$\textbf{(a)}\quad 1 < a < \mathrm{e}^{1/\mathrm e}, \qquad
\textbf{(b)}\quad a > \mathrm{e}^{1/\mathrm e}.$$

```python
my14_two = Interval.open(1, exp(1/E))
my14_none = Interval.open(exp(1/E), oo)
```

**The marking.** (f)(i): A1, with the explicit note that
$a<\mathrm{e}^{1/\mathrm e}$ without the left boundary scores zero. (f)(ii): A1; an
approximate value is accepted only as follow through, and then in the narrow
corridor $1.4 \le a \le 1.5$.

**The answer has to be exact.** $\mathrm{e}^{1/\mathrm e} = 1.4446\ldots$, and 1.44
cannot be written: the question asks for the «exact set». That is a common feature of
Paper 3 — the investigation leads to a pretty constant, and that constant is the
answer.

**Two marks for two lines — and half a page of work before them.** Part (f) itself is
worth only 2 marks but leans on the whole preceding investigation. The practicum
gives the statement ready-made; in the exam you arrive at it through parts (a)–(e).

**About the numerical check.** Counting the roots of $a^x=x$ directly in $x$ is
awkward: as $a\to1^+$ the second root runs off to infinity (at $a=1.01$ it is around
1600). After the substitution $x=\mathrm{e}^u$ both roots stay within
$u \in [-2, 40]$ and the scan works stably. That is why the check in the notebook
counts in $u$.
""")

md(r"""
## Solution 15 — monotonicity

Turn the one into a logarithm and add:

$$1 + \log_2 n = \log_2 2 + \log_2 n = \log_2 (2n).$$

Now both sides are logarithms to the same base, and they can be compared by
comparing the arguments. The function $\log_2$ is **increasing**, so

$$\log_2(2n) \ge \log_2(n+1) \iff 2n \ge n+1 \iff n \ge 1.$$

For $n \in \mathbb{Z}^+$ that always holds. $\blacksquare$

```python
my15_log = log(2*n, 2)
my15_set = Interval(1, oo)
```

**The marking.** A1 for $1+\log_2 n = \log_2(2n)$, R1 for $2n \ge n+1$ or for
comparing the logarithms; the result is AG.

**What the R1 is for.** Not for the inequality $2n\ge n+1$ itself but for the step
from it to the logarithms. Formally that is an appeal to the monotonicity of
$\log_2$, and without it the deduction is incomplete: for a decreasing function the
sign would have flipped.

**Where this leads.** The block is part (a) of a question about induction: the
inequality proved is then used in the step. That is how inequalities live in the
archive — as a service part inside somebody else's topic.
""")

md(r"""
## Solution 16 — complete the square

Compute the sum. From $v(\tau) = \mathrm{e}^{\,T-\tau}-1$:

$$v(T-k) = \mathrm{e}^{k}-1, \qquad v(T+k) = \mathrm{e}^{-k}-1,$$

$$v(T-k)+v(T+k) = \mathrm{e}^{k} + \mathrm{e}^{-k} - 2.$$

By itself that expression says nothing. Notice that
$\mathrm{e}^{k} = \left(\mathrm{e}^{k/2}\right)^2$ and unfold the square of a
difference:

$$\left(\mathrm{e}^{k/2} - \mathrm{e}^{-k/2}\right)^2
= \mathrm{e}^{k} - 2 + \mathrm{e}^{-k}.$$

That is the same thing. A square is non-negative, therefore

$$v(T-k)+v(T+k) \ge 0. \qquad \blacksquare$$

```python
my16_sum = exp(k) + exp(-k) - 2
my16_sq = (exp(k/2) - exp(-k/2))**2
```

**The marking.** A1 for the sum $\mathrm{e}^{k}+\mathrm{e}^{-k}-2$, M1 for
attempting to write it as a square, A1 for the square itself; the conclusion $\ge0$
is AG.

**A second route, also complete.** Investigate
$F(k)=\mathrm{e}^k+\mathrm{e}^{-k}-2$ for a minimum:
$F'(k)=\mathrm{e}^k-\mathrm{e}^{-k}=0$ at $k=0$, $F(0)=0$, so $F\ge0$. The
markscheme gives the same three marks for it (A1M1R1). On Paper 1 the route through
the square is shorter, but if the square was not spotted, the derivative saves the
day.

**Why the check does not accept the expanded form.** `verify_nonneg_form` requires a
writing from which the non-negativity is visible: a sum of squares, moduli and
non-negative numbers, with no terms carrying a minus. The writing
$\mathrm{e}^k+\mathrm{e}^{-k}-2$ equals the right answer but contains no proof —
exactly as in A4 an expanded polynomial equals its factorisation but earns nothing
for «product of linear factors».
""")

md(r"""
## Solution 17 — by contradiction

Suppose the opposite:

$$\sqrt{xy} > \frac{x+y}{2}.$$

Both sides are positive ($x,y>0$), so squaring is an equivalence:

$$xy > \frac{(x+y)^2}{4} \iff 4xy > x^2+2xy+y^2 \iff 0 > x^2-2xy+y^2.$$

On the right is a perfect square:

$$0 > (x-y)^2.$$

The square of a real number is never negative. A contradiction, therefore the
original supposition is false and

$$\sqrt{xy} \le \frac{x+y}{2}. \qquad \blacksquare$$

```python
my17_expr = x**2 - 2*x*y + y**2
my17_sq = (x - y)**2
```

**The marking.** M1 for supposing the opposite, M1 for attempting to square, A1 for
$0 > x^2-2xy+y^2$, A1 for $0>(x-y)^2$, R1 for the explicit sentence «a square cannot
be negative, a contradiction».

**A mark for a sentence.** The R1 here is not for the working but for the conclusion
in words. Reaching $0>(x-y)^2$ and stopping is a lost mark: formally the
contradiction has not been presented.

**Why the squaring is legitimate.** Both sides are positive, and only for that
reason the sign is kept. In proofs by contradiction that is the step where rigour is
most often lost: an inequality whose sides have unknown sign must not be squared.

**About the archive's tags.** The extract from the markscheme has
$0 > x^2-4xy+y^2$. That does not come out: $4xy > (x+y)^2$ gives
$0 > x^2-2xy+y^2$. And the next line of the extract, $0>(x-y)^2$, agrees precisely
with $-2xy$: the expression $x^2-4xy+y^2$ is not a perfect square at all. It looks
like a coefficient lost in the extraction; the check is in `verify_a8.py`.
""")

md(r"""
## Solution 18 — two short deductions from Paper 3

**(a)** Substitute and subtract:

$$b - a = (t^2-s^2) - (2st-s^2) = t^2 - 2st = t(t-2s).$$

We are given $a<b$, that is, $b-a>0$, that is, $t(t-2s)>0$. Since
$t \in \mathbb{R}^+$, divide by $t$ and the sign is kept:

$$t - 2s > 0 \iff t > 2s. \qquad \blacksquare$$

**(b)** By the AM–GM inequality, for positive $x_1,\dots,x_n$ with sum $T$

$$\sqrt[n]{x_1x_2\cdots x_n} \le \frac{x_1+\cdots+x_n}{n} = \frac Tn,$$

and raising to the $n$-th power

$$x_1x_2\cdots x_n \le \left(\frac Tn\right)^n.$$

Equality is attained when all the $x_i$ are equal, that is, at $x_i = \frac Tn$ —
such a set exists and gives the right sum. So the upper bound is attained and

$$M_n(T) = \left(\frac Tn\right)^n.$$

```python
my18_diff = t*(t - 2*s)
my18_max = (T/n)**n
```

**The marking.** (a): A1 for $2st-s^2 < t^2-s^2$, R1 for dividing by $t>0$ with the
statement about the sign; $t>2s$ is AG. (b): A1 for $\sum x_i = T$, M1 for applying
AM–GM, M1 for raising to the power, R1 for the condition of equality; the result is
AG.

**Both marks in (a) are for the caveats.** The algebra there is one line: the $s^2$
cancels. The marks are for saying why dividing by $t$ is allowed — and that is the
whole part.

**Why (b) needs the condition for equality.** Without it only
$M_n(T) \le \left(\frac Tn\right)^n$ has been proved, while equality is what is
asked. The R1 is precisely for presenting a set on which the bound is attained.

**A check from another practicum.** Part (a) is checked by `verify_factored` — the
very function from A4. The requirement is the same: the answer has to be a
**product**, because the conclusion $t>2s$ comes exactly from the product and not
from $t^2-2st$.
""")

md(r"""
## Solution 19 — the task on the timer

**(a)** The discriminant of $x^2+kx+15-k=0$:

$$\Delta = k^2 - 4(15-k) = k^2 + 4k - 60.$$

Two distinct real roots means $\Delta>0$:

$$k^2+4k-60 > 0 \iff (k-6)(k+10) > 0.$$

The critical values are $-10$ and $6$, and the parabola opens upwards:

$$k < -10 \quad\text{or}\quad k > 6.$$

**(b)** Roots of the same sign means their product is positive:

$$\alpha\beta = 15 - k > 0 \iff k < 15.$$

Intersect with the answer to (a):

$$k<-10 \quad\text{or}\quad 6 < k < 15.$$

```python
my19_a = Union(Interval.open(-oo, -10), Interval.open(6, oo))
my19_b = Union(Interval.open(-oo, -10), Interval.open(6, 15))
```

**The marking.** (a): M1 for $\Delta>0$, A1 for $k^2+4k-60$, M1 for attempting to
solve the quadratic inequality, A1 for the critical values, A1 for the answer. (b):
M1 for realising that the product of the roots is positive, A1 for the answer.

**How it looks in time.** Seven marks in twelve minutes, and almost all the time
goes on part (a): five of the seven marks are for solving one quadratic inequality
carefully.

**The key move in (b).** Not computing the roots. The condition «both positive or
both negative» is exactly «the product is positive», and the product is known at
once: $\frac ca = 15-k$. The sum of the roots is not needed here at all — it would
be needed if both positive were asked about separately.

**Why an intersection and not a union.** The condition in (b) is added to the
condition in (a), not substituted for it: the roots still have to be real and
distinct. The piece $k<-10$ survived whole (there $15-k>25>0$), while the right one
was trimmed from $k>6$ to $6<k<15$.

**A check on the answer in five seconds.** Take $k=10$: the equation
$x^2+10x+5=0$, roots $-5\pm\sqrt{20}$, both negative — it agrees. Take $k=20$:
$x^2+20x-5=0$, product $-5<0$, roots of different signs — it does not agree, and
rightly so, $20>15$.
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

OUT = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a8-inequalities.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
