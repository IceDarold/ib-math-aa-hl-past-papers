"""Собирает практикум B2 (композиция и обратные функции) в формате .ipynb.

Первый практикум серии на английском: ноутбук целиком английский, а kit
переключается вызовом language('en') в установочной ячейке. Документация
репозитория (карта, PRACTICUM.md, этот заголовок) остаётся русской.
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
x, y, t, k, n, r = sp.symbols('x y t k n r')
a, b, c, m, p, q = sp.symbols('a b c m p q')


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


def dser(expr, var=x, sf=6):
    return digest(kit._series_canon(expr, var, sf))


def ddom(region, var=x):
    return digest(sp.srepr(kit._as_set(region, var)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_b2.py ---
D_1A = dn(23)                                   # h(4) = f(g(4)) = f(4)
D_1B = dn(-2)                                   # f(0) для (3x−2)/(2x+1)
D_1D = dser(x * (12 - x))                       # произведение как функция x1
D_2 = dser((x - 3)**2 + k**2)                   # (g∘f)(x)
D_6 = dset([2*x - 4, -2*x + 3])                 # две функции f
D_9 = dser(1 - 2*x**2 + 4*x**4 - 8*x**6)        # f3(−x)
D_10A = dser(m**2*x + c*(1 + m))                # f²
D_10B = dser(m**3*x + c*(1 + m + m**2))         # f³
D_10C = dser(m**4*x + c*(1 + m + m**2 + m**3))  # f⁴
D_10D = dser(m**n*x + c*(1 - m**n)/(1 - m))     # fⁿ
D_11A = dn(R(3, 2))                             # f⁻¹(8) при f(x) = 4^x
D_11B = dn(1.31837, 3)                          # f⁻¹(2) по GDC
D_12A = ddom(sp.Interval(-3, 5))                # область f⁻¹ с графика
D_12B = dn(3)                                   # f⁻¹(2x−7) = −3
D_13 = dn(-3)                                   # g = g⁻¹
D_16C = de(k - sp.pi)                           # наибольшее a через k
D_17B = ddom(sp.Interval(0, sq(3)))             # область f⁻¹
D_17C = ddom(sp.Interval(1, 2))                 # множество значений f⁻¹
D_18 = ddom(sp.Interval.Lopen(R(1, 2), 1))      # область g⁻¹
D_19 = ddom(sp.Interval.open(0, sp.oo))         # область g⁻¹
D_20 = ddom(sp.Interval.Ropen(-sp.pi/2, sp.pi/2))
D_21A = dser(x + n*c)                           # fⁿ при m = 1
D_21B = de(c/(1 - m))                           # предельная прямая L
D_21C = dser(-x + c)                            # fⁿ при m = −1, n нечётно
D_21D = dser(x)                                 # fⁿ при m = −1, n чётно

TRIGGER = {1: 'build', 2: 'swap', 3: 'prop', 4: 'comp', 5: 'even',
           6: 'dom', 7: 'iter', 8: 'ceq', 9: 'branch', 10: 'dom',
           11: 'swap', 12: 'iter', 13: 'ceq', 14: 'even', 15: 'prop'}
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
# Practicum B2: composition and inverse functions

**113 marks, 40 blocks, nine techniques.** Two ideas that are one line of
algebra each — and the exam pays for neither of them. It pays for the
**order** in which you compose, and for the **domain** on which the
inverse is allowed to live.

**Material.** 40 blocks and 113 marks from the AA HL archive, sessions
May 2021 — May 2025. Five of those marks are one question counted twice:
the whole November 2023 session sits in the corpus as two zones, and the
papers are the same paper. Every task below is a real past-paper
question, with the source given.

**This practicum is in English.** The first ten were in Russian; the
checks now speak whichever language the notebook asks them to, and this
one asks for English in the setup cell below.

**The main idea.** Composition chains two functions; the inverse is the
chain run backwards. Written down, both are short. The marks are
somewhere else.

* **Order.** $(f \circ g)(x)$ means $g$ first. The M1 is for composing
  in the right order, and roughly half the composite questions in the
  archive are built so that the wrong order gives a different, plausible
  answer.
* **Domain.** An inverse exists only where the function is one-to-one.
  So the question first asks for the largest $a$ that keeps it so; then
  domain and range **swap**, so the domain of $f^{-1}$ is the range of
  $f$; and if the algebra ends in a square root, one branch is the
  inverse and the other is a different function. That last step is an
  R1 — a sentence, not a formula — and it is the mark most often lost.

**How to work**

1. Read the map of techniques first. Rungs 1–5 run forwards, rungs 6–9
   run backwards, and the two halves meet at the end.
2. Work **on paper**. Enter exact answers: `sqrt(2)`, `Rational(3, 2)`,
   `1 + 3*sqrt(2)/2`. Round only where the question says "3 s.f.".
3. Domains and ranges are entered as sets or inequalities:
   `Interval(0, sqrt(3))`, `(x > 0)`, `Interval.Lopen(Rational(1,2), 1)`.
   The notation is free; the endpoints are not.
4. An inverse is checked by **undoing**, not against a stored answer.
   The check substitutes $f$ into what you wrote and asks for $x$ back.
5. The last two blocks are a recognition trainer and one question on
   a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + solveset, Interval, real_roots

language('en')                 # this notebook is in English, and so are the checks

a, b, c, m, p, q = symbols('a b c m p q')
n, r, t = symbols('n r t')

print('ready; sympy', sp.__version__)
print('compose:            ', (lambda f, g: f.subs(x, g))(x**2 + 1, 3*x - 2))
print('inverse by hand:    ', solve(Eq(y, (7*x + 7)/(2*x - 4)), x))
print('a domain as a set:  ', Interval.Lopen(Rational(1, 2), 1))
print('sin of an arcsin:   ', simplify(sin(asin((x**2 - 1)/(x**2 + 1)))))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Evaluate a composite | «find $(f\circ g)(a)$», «find $h(4)$ where $h(x)=f(g(x))$» | evaluate the inner function at the number |
| 2 | Build the composite | «write down an expression for $(g\circ f)(x)$», «show that $(f\circ g)(x)=\dots$» | substitute the whole inner expression, in brackets |
| 3 | The composite as an equation | «given $(g\circ f)(2)=10$, find $k$», «find the two possible $f$» | build the composite, then set it equal |
| 4 | Substitute $-x$ | «show that $f$ is an even function» | write $f(-x)$ in full and simplify |
| 5 | Compose $f$ with itself | «$f^n(x)$», «self-composite», «suggest an expression» | compute $f^2$ and $f^3$, keep the pattern visible |
| 6 | The defining property | «find $f^{-1}(8)$», «solve $f^{-1}(2x-7)=-3$», «$g=g^{-1}$» | turn it around: $f^{-1}(a)=b$ **is** $f(b)=a$ |
| 7 | Swap and solve | «find an expression for $f^{-1}(x)$» | write $y=f(x)$, interchange $x$ and $y$ |
| 8 | Existence and domain | «largest $a$ for which $f^{-1}$ exists», «state the domain of $f^{-1}$» | find where $f$ turns; then range of $f$ = domain of $f^{-1}$ |
| 9 | Choosing the branch | a $\pm$ appears, and «justifying your answer» | range of $f^{-1}$ = domain of $f$ — that is what chooses |

The ladder runs in two directions. Rungs 1–3 go **forwards**: evaluate a
composite, write one down, then set it equal to something and solve.
Rung 4 is the smallest composite there is, $f(-x)$, and rung 5 composes
$f$ with itself until a pattern appears.

Rungs 6–9 go **backwards**. First the defining property, which answers
most inverse questions without ever finding the inverse. Then the swap
that produces the formula. Then the domain the formula is allowed to
live on. Then the choice of branch, which is where the R1 sits.

**The loop closes at the end.** A function is its own inverse exactly
when $f\circ f$ is the identity, and exactly when its graph is symmetric
in $y=x$. Task 13 finds such a function by algebra; the timed task meets
the same fact again as the case $m=-1$ of a Paper 3 investigation.

**What saves the most time.** Before composing, look at which function
is written next to the bracket. Before finding an inverse, look at
whether the question actually wants the formula — half the time it wants
one value, and $f^{-1}(a)=b \iff f(b)=a$ gets it in one line.
""")

md(r"""
---
## Theory 1. Composition, and why the order is the mark

$(f \circ g)(x)$ means $f(g(x))$: **the function written next to the
bracket goes first.** The notation reads right to left, which is exactly
why it is worth a mark.

$$(f \circ g)(x) = f(g(x)), \qquad (g \circ f)(x) = g(f(x)).$$

These are different functions. With $f(x)=x-3$ and $g(x)=x^2$:

$$(g \circ f)(x) = (x-3)^2, \qquad (f \circ g)(x) = x^2 - 3.$$

**Evaluating at a point.** Work inwards out, and carry a *number*, not
an expression:

$$h(4) = f(g(4)), \quad g(4) = 4^2 - 3\cdot 4 = 4, \quad
h(4) = f(4).$$

That last line is the whole point of the question: you never need a
formula for $f$, only its value at 4.

**A worked example of the same move.** In May 2025 TZ1 Paper 3 a
probability distribution is packed into the polynomial

$$G(t) = \tfrac{1}{16}t + \tfrac{3}{16}t^2 + \tfrac{5}{16}t^3
+ \tfrac{7}{16}t^4,$$

and the question asks for $G(1)$. Substituting gives
$\frac{1+3+5+7}{16} = 1$ — the probabilities add to one. One mark, one
substitution, and the answer was predictable before any arithmetic.

**Composition and the chain rule are the same picture.** If a later part
asks for $(f\circ g)'(0)$, that is $f'(g(0)) \cdot g'(0)$ — the inner
derivative is a factor, not a decoration. B2 stops at the value; the
derivative belongs to E3.
""")

md(r"""
## Task 1 🟢 — evaluating composites

**(a)** The function $f$ is defined for all $x \in \mathbb{R}$, and the
line $y = 6x - 1$ is the tangent to the graph of $f$ at $x = 4$. Given
$g(x) = x^2 - 3x$ and $h(x) = f(g(x))$, find $h(4)$.

**(b)** The function $f$ is defined by $f(x) = \dfrac{3x-2}{2x+1}$,
$x \ne -\frac12$. Write down the value of $f(0)$.

**(c)** The function $f$ is defined by $f(x) = e^{2x}(3x-4)$. A function
$g$ satisfies $g(0) = 1$ and $g'(0) = 2$. Find the exact value of
$(f \circ g)(0)$.

**(d)** Two numbers $x_1, x_2 \in \mathbb{R}^+$ satisfy $x_1 + x_2 = 12$.
Write their product as a function $f$ of $x_1$ only. (Enter it in `x`.)

*Sources: November 2021, Paper 1, Q5(c) (2 marks); May 2025 TZ2, Paper 1,
Q1(a) (1 mark); November 2022, Paper 2, Q11(d)(i) (2 marks); May 2023
TZ1, Paper 3, Q2(a) (2 marks).*
""")

code(r"""
my1a = ...               # h(4)
my1b = ...               # f(0)
my1c = ...               # (f ∘ g)(0), exact
my1d = ...               # the product as a function of x

check_num('Task 1(a)', my1a, 6, '""" + D_1A + r"""')
check_num('Task 1(b)', my1b, 6, '""" + D_1B + r"""')
verify_exact('Task 1(c)', my1c, -exp(2))
check_series('Task 1(d)', my1d, '""" + D_1D + r"""')
""")

md(r"""
---
## Theory 2. Building the composite

Substituting a number was arithmetic. Substituting an **expression** is
where brackets start earning marks:

$$g(x) = x^2 + k^2, \quad f(x) = x - 3
\ \Longrightarrow\ (g \circ f)(x) = (x-3)^2 + k^2.$$

Write the bracket first, expand second. The most common lost mark in
this rung is $(x-3)^2$ turned into $x^2 - 9$, or into $x^2 - 3$.

**"Show that" is a different kind of question.** The answer is printed
in the question, so the marks are for the road to it. A typical
three-mark chain:

$$(f \circ g)(x) = 4^{\,1 + \log_2 x}
= 4 \cdot 4^{\log_2 x}
= 4 \cdot 2^{2\log_2 x}
= 4 \cdot \left(2^{\log_2 x}\right)^2
= 4x^2 .$$

M1 for attempting the composite, A1 for splitting the exponent, A1 for
landing on $4x^2$. Writing $4x^2$ straight from the question earns
nothing.

**Composites hide inside identities too.** $f(t) = \frac{e^t+e^{-t}}{2}$
and $g(t) = \frac{e^t-e^{-t}}{2}$ satisfy
$\big(f(t)\big)^2 + \big(g(t)\big)^2 = f(2t)$, and the proof is nothing
but substituting the definitions and collecting. Those two functions are
$\cosh$ and $\sinh$; the exam does not name them, and does not need to.
""")

md(r"""
## Task 2 🟢 — write down the composite

Consider $f(x) = x - 3$ and $g(x) = x^2 + k^2$, where $k$ is a real
constant. Write down an expression for $(g \circ f)(x)$.

Keep the letter $k$ in your answer — the check substitutes values for it
too.

*Source: November 2023, Paper 1, Q1(a) (2 marks, no calculator).*
""")

code(r"""
my2 = ...                # (g ∘ f)(x), in x and k

check_series('Task 2', my2, '""" + D_2 + r"""')
""")

md(r"""
## Task 3 🟡 — a "show that" with logarithms

The functions are $f(x) = 4^x$, $x \in \mathbb{R}$, and
$g(x) = 1 + \log_2 x$, $x \in \mathbb{R}^+$.

Show that $(f \circ g)(x) = 4x^2$.

Enter the composite **before** you simplify it — the unsimplified
$4^{\,1+\log_2 x}$, written in code as `4**(1 + log(x, 2))`. The check
compares it with $4x^2$ as functions, which is exactly what a "show
that" claims.

*Source: May 2025 TZ2, Paper 1, Q10(c) (3 marks, no calculator).*
""")

code(r"""
my3 = ...                # (f ∘ g)(x) as it comes out, before simplifying

verify_identity('Task 3', my3, 4*x**2, samples=(0.4, 0.9, 1.6, 2.5, 4.1))
""")

md(r"""
## Task 4 🟡 — a composite identity

The functions $f$ and $g$ are defined for $t \in \mathbb{R}$ by

$$f(t) = \frac{e^{t} + e^{-t}}{2}, \qquad
g(t) = \frac{e^{t} - e^{-t}}{2}.$$

Show that $\big(f(t)\big)^2 + \big(g(t)\big)^2 = f(2t)$.

Enter the left-hand side, written out with the definitions substituted
and collected as far as you can take it. Use `t`, not `x`.

*Source: November 2021, Paper 3, Q1(b) (3 marks).*
""")

code(r"""
my4 = ...                # (f(t))² + (g(t))², simplified

verify_identity('Task 4', my4, (exp(2*t) + exp(-2*t))/2, var=t)
""")

md(r"""
---
## Theory 3. The composite is given a value — that is an equation

The moment a composite is set equal to a number, the question stops
being about composition and becomes an equation. The technique is the
join:

1. build the composite,
2. set it equal to the given value,
3. solve — and then check every root against the domain in the question.

$$(g \circ f)(2) = 10 \ \Longrightarrow\ (2-3)^2 + k^2 = 10
\ \Longrightarrow\ k^2 = 9 \ \Longrightarrow\ k = \pm 3 .$$

Both signs. "The possible values" is plural on purpose, and $k^2 = 9$ is
where the answer is decided.

**When $f$ itself is unknown.** If $f(x) = ax+b$ and the composite is
given as a polynomial, compare coefficients:

$$(g \circ f)(x) = (ax+b)^2 + (ax+b) + 3 = 4x^2 - 14x + 15 .$$

From $x^2$: $a^2 = 4$, so $a = \pm 2$. From $x$: $2ab + a = -14$, which
pairs each $a$ with its own $b$. Two functions come out, not one, and
the constant term is the check that both work.

**When the domain throws a root away.** In a question with $x > 3$ in
the definition, a quadratic gives two roots and one of them is smaller
than 3. Rejecting it is a mark; forgetting to look is the single most
expensive habit in this rung.
""")

md(r"""
## Task 5 🟢 — the composite pinned at a point

With $f(x) = x - 3$ and $g(x) = x^2 + k^2$ as in task 2, it is given
that $(g \circ f)(2) = 10$. Find the possible values of $k$.

Enter them as a list.

*Source: November 2023, Paper 1, Q1(b) (3 marks, no calculator).*
""")

code(r"""
my5 = [...]              # the possible values of k, as a list

verify_root_set('Task 5', my5, k**2 - 9, var=k)
""")

md(r"""
## Task 6 🔴 — find the function, not the number

The functions $f$ and $g$ are defined for $x \in \mathbb{R}$ by

$$f(x) = ax + b \ \ (a, b \in \mathbb{R}), \qquad g(x) = x^2 + x + 3 .$$

Find the **two** possible functions $f$ such that
$(g \circ f)(x) = 4x^2 - 14x + 15$.

Enter both expressions in a list; the order does not matter.

*Source: May 2023 TZ2, Paper 1, Q5 (7 marks, no calculator).*
""")

code(r"""
my6 = [..., ...]         # the two functions f, as expressions in x

check_set('Task 6', my6, '""" + D_6 + r"""')
""")

md(r"""
## Task 7 🔴 — a composite equal to an angle

A function $g$ is defined by $g(x) = \dfrac{1}{x^2 - 2x - 3}$, where
$x \in \mathbb{R}$, $x > 3$. A function $h$ is defined by
$h(x) = \arctan \dfrac{x}{2}$, where $x \in \mathbb{R}$.

Given that $(h \circ g)(a) = \dfrac{\pi}{4}$, find the value of $a$.
Give your answer in the form $p + \dfrac{q}{2}\sqrt{r}$, where
$p, q, r \in \mathbb{Z}^+$.

The domain $x > 3$ is not decoration here.

*Source: May 2022 TZ2, Paper 1, Q11(c) (7 marks, no calculator).*
""")

code(r"""
my7 = ...                # the value of a, exact

verify_exact('Task 7', my7, 1 + 3*sqrt(2)/2)
""")

md(r"""
---
## Theory 4. Substituting $-x$: the smallest composite there is

$f(-x)$ is $f$ composed with the function $x \mapsto -x$, and it answers
the only symmetry question the exam asks:

$$f(-x) = f(x) \ \Rightarrow\ f \text{ is even (symmetric in the } y
\text{-axis)},$$
$$f(-x) = -f(x) \ \Rightarrow\ f \text{ is odd (symmetric about the
origin)}.$$

**The mark is the sentence.** These questions are marked R1 or AG:
arriving at $f(-x) = f(x)$ and stopping is not the answer. "Therefore
$f$ is even" is.

**Write the brackets.** $f(-x)$ means replacing every $x$, brackets
included: $(-x)^2 = x^2$, $(-x)^3 = -x^3$, $(-x)^4 = x^4$. In
$\arcsin\dfrac{x^2-1}{x^2+1}$ every $x$ appears squared, so $f(-x)$ is
the same expression, character for character — and that is the proof.

**Inside a sum, the claim is about every term.** For

$$f_n(x) = \sum_{r=0}^{n} \left(-2x^2\right)^r ,$$

each term contains $(-x)^2 = x^2$, so each term is unchanged, so the sum
is unchanged. Checking $r = 0$ and $r = 1$ and writing "and so on" is
worth less than one line about the general term.
""")

md(r"""
## Task 8 🟢 — show that it is even

A function $f$ is defined by
$f(x) = \arcsin \dfrac{x^2 - 1}{x^2 + 1}$, $x \in \mathbb{R}$.

Show that $f$ is an even function.

Enter $f(-x)$, written out and simplified; the check compares it with
$f(x)$ as functions. Then read the solution for the part the check
cannot see — the sentence that earns the mark.

*Source: May 2021 TZ2, Paper 2, Q12(a) (1 mark).*
""")

code(r"""
my8 = ...                # f(−x), simplified

verify_identity('Task 8', my8, asin((x**2 - 1)/(x**2 + 1)))
""")

md(r"""
## Task 9 🟡 — even for every $n$

Consider the family of functions

$$f_n(x) = \sum_{r=0}^{n} \left(-2x^2\right)^{r},
\qquad x \in \mathbb{R}, \ n \in \mathbb{N}.$$

Show that $f_n$ is an even function for all values of $n$.

The general argument is one line and belongs in your written work. For
the check, write out $f_3(-x)$ as a polynomial in ascending powers of
$x$ — if the substitution is done correctly it will be $f_3(x)$ itself.

*Source: May 2025 TZ1, Paper 2, Q12(a) (3 marks).*
""")

code(r"""
my9 = ...                # f₃(−x), expanded

check_series('Task 9', my9, '""" + D_9 + r"""')
""")

md(r"""
---
## Theory 5. Composing $f$ with itself

$f^2$ means $f \circ f$, **not** $(f(x))^2$. The notation is unfortunate
and the exam knows it — Paper 3 investigations state the convention
explicitly before using it:

$$f^{2}(x) = f(f(x)), \qquad f^{3}(x) = f(f(f(x))), \qquad
f^{n}(x) = \underbrace{f(f(\cdots f(x)\cdots))}_{n \text{ times}} .$$

For a linear $f(x) = mx + c$ the pattern appears immediately, provided
you do not simplify it away:

$$f^{2}(x) = m(mx+c)+c = m^2x + c(1+m),$$
$$f^{3}(x) = m\big(m^2x + c(1+m)\big)+c = m^3x + c(1+m+m^2),$$
$$f^{4}(x) = m^4x + c(1+m+m^2+m^3).$$

Two separate stories: the coefficient of $x$ is just $m^n$, and the
constant is a geometric sum. Closing it,

$$f^{n}(x) = m^{n}x + c\,(1 + m + \cdots + m^{n-1})
= m^{n}x + c\,\frac{1-m^{n}}{1-m}, \qquad m \ne 1 .$$

**Three cases, and the exam asks about all of them.**

* $m = 1$: the closed form is $\frac00$ and useless. Go back to the sum:
  $1+1+\cdots+1 = n$, so $f^{n}(x) = x + nc$. The graph slides.
* $-1 < m < 1$: $m^n \to 0$, so $f^{n}(x) \to \dfrac{c}{1-m}$ for every
  $x$. The family of lines flattens onto the horizontal line
  $y = \dfrac{c}{1-m}$ — which is the fixed point of $f$.
* $m = -1$: $(-1)^n$ alternates. For odd $n$, $f^{n}(x) = -x + c$; for
  even $n$, $f^{n}(x) = x$. The function is **self-inverse**, and
  $f \circ f$ being the identity is precisely what that means.

That last case is the loop of this practicum closing: composition run
twice and coming back to $x$ is the same statement as $f = f^{-1}$.
""")

md(r"""
## Task 10 🟡 — the self-composite of a linear function

Consider the linear function $f(x) = mx + c$, where $x \in \mathbb{R}$
and $m, c \in \mathbb{R}$.

**(a)** Show that $f^{2}(x) = m^{2}x + c(1+m)$.

**(b)** Show that $f^{3}(x) = m^{3}x + c(1+m+m^{2})$.

**(c)** Write down an expression for $f^{4}(x)$.

**(d)** Suggest a similar expression for $f^{n}(x)$, $n \in
\mathbb{Z}^{+}$, with $m \ne 1$. Write the constant part as a **single
fraction**.

*Source: May 2025 TZ3, Paper 3, Q1(a)(b)(i)(ii) (3 + 2 + 1 + 2 marks).
Part (c) of that question proves the formula by induction — that is A7's
work, and this practicum stops at finding it.*
""")

code(r"""
my10a = ...              # f²(x)
my10b = ...              # f³(x)
my10c = ...              # f⁴(x)
my10d = ...              # fⁿ(x), constant as one fraction

check_series('Task 10(a)', my10a, '""" + D_10A + r"""')
check_series('Task 10(b)', my10b, '""" + D_10B + r"""')
check_series('Task 10(c)', my10c, '""" + D_10C + r"""')
check_series('Task 10(d)', my10d, '""" + D_10D + r"""')
""")

md(r"""
---
## Theory 6. The defining property, and how to avoid finding the inverse

Everything about $f^{-1}$ follows from one sentence:

$$f^{-1}(a) = b \quad \Longleftrightarrow \quad f(b) = a .$$

Read left to right it is a definition; read right to left it is a
technique. Most inverse questions in the archive ask for **one value**,
and the value comes out without ever writing the formula:

$$f(x) = 4^{x}, \quad f^{-1}(8) = ? \ \Longrightarrow\ 4^{x} = 8
\ \Longrightarrow\ 2^{2x} = 2^{3} \ \Longrightarrow\ x = \tfrac32 .$$

**Three corollaries, each worth marks somewhere in the archive.**

* **Reflection.** $(a,b)$ on $y=f(x)$ means $(b,a)$ on $y=f^{-1}(x)$.
  The graphs are mirror images in the line $y = x$, so anything
  symmetric in that line — a maximum distance, a point of intersection
  with $y=x$ — is shared by both.
* **Nested.** $f^{-1}(\text{something}) = b$ becomes
  $\text{something} = f(b)$. In $f^{-1}(2x-7) = -3$ the inner bracket
  equals $f(-3)$, **not** $-3$. That single confusion is the whole
  difficulty of the question.
* **Self-inverse.** $g = g^{-1}$ can be attacked two ways: find $g^{-1}$
  and equate, or compute $g(g(x))$ and set it equal to $x$. Both are in
  the markscheme; the second is usually shorter.

**On a calculator.** $f^{-1}(2)$ where $f(x) = 4\cot x + \sin x$ is the
one place in this whole topic where a GDC does real work: solve
$f(x) = 2$ on $0 < x < \pi$ and read $x = 1.32$. Everywhere else the
"calculator" papers still want exact answers.
""")

md(r"""
## Task 11 🟢 — one value of the inverse, two ways

**(a)** The function $f$ is defined by $f(x) = 4^{x}$, $x \in
\mathbb{R}$. Find $f^{-1}(8)$, expressing your answer in the form
$\dfrac{p}{q}$ with $p, q \in \mathbb{Z}$.

**(b)** The function $f$ is defined by $f(x) = 4\cot x + \sin x$, where
$0 < x < \pi$. Find the value of $f^{-1}(2)$, correct to 3 significant
figures.

Part (b) is the calculator question of this practicum. Part (a) is not:
$\log_4 8$ is exact and a decimal earns nothing.

*Sources: May 2025 TZ2, Paper 1, Q10(a) (3 marks, no calculator);
May 2025 TZ1, Paper 2, Q6(b) (1 mark, calculator).*
""")

code(r"""
my11a = ...              # f⁻¹(8), exact
my11b = ...              # f⁻¹(2), 3 s.f.

check_num('Task 11(a)', my11a, 6, '""" + D_11A + r"""')
check_num('Task 11(b)', my11b, 3, '""" + D_11B + r"""')
""")

md(r"""
## Task 12 🟡 — reading the inverse off a graph

The graph of $y = f(x)$ is drawn for $-6 \le x \le 5$. From the diagram
in the paper: $f$ is one-to-one on that interval, $f(-3) = -1$, the
least value of $f$ is $-3$ and the greatest is $5$, both attained.

**(a)** State the domain of $f^{-1}$.

**(b)** Find the value of $x$ that satisfies $f^{-1}(2x - 7) = -3$.

Enter the domain as a set or an inequality, for instance
`Interval(-3, 5)` or `(x >= -3) & (x <= 5)`.

*Source: May 2025 TZ3, Paper 1, Q2(b)(c) (1 + 3 marks, no calculator).*
""")

code(r"""
my12a = ...              # domain of f⁻¹
my12b = ...              # the value of x

check_domain('Task 12(a)', my12a, '""" + D_12A + r"""')
check_num('Task 12(b)', my12b, 6, '""" + D_12B + r"""')
""")

md(r"""
## Task 13 🔴 — a function equal to its own inverse

The function $g$ is defined by

$$g(x) = \frac{ax+4}{3-x}, \qquad x \in \mathbb{R},\ x \ne 3,\
a \in \mathbb{R} .$$

Given that $g(x) = g^{-1}(x)$, determine the value of $a$.

Two routes are in the markscheme. Find $g^{-1}$ and equate it to $g$, or
compute $g(g(x))$ and set it equal to $x$. Try the second: it turns the
question into "which $a$ makes $g \circ g$ the identity", and that is
rung 5 in disguise.

*Source: November 2021, Paper 1, Q2(d) (4 marks, no calculator).*
""")

code(r"""
my13 = ...               # the value of a

check_num('Task 13', my13, 6, '""" + D_13 + r"""')
""")

md(r"""
---
## Theory 7. Swap, then make $y$ the subject

The formula for an inverse comes from one honest procedure:

1. write $y = f(x)$;
2. **interchange** $x$ and $y$ — this is the mark, and it is the step
   most often skipped;
3. solve the new equation for $y$;
4. call the result $f^{-1}(x)$.

For a rational function, step 3 is always the same three moves —
multiply out, collect every $y$ on one side, factorise:

$$x = \frac{7y+7}{2y-4} \Rightarrow 2xy - 4x = 7y + 7
\Rightarrow y(2x-7) = 4x+7
\Rightarrow f^{-1}(x) = \frac{4x+7}{2x-7} .$$

For a logarithm or an exponential, step 3 is one application of the
opposite operation:

$$x = 1 + \log_2 y \Rightarrow \log_2 y = x - 1
\Rightarrow g^{-1}(x) = 2^{\,x-1} .$$

**Check by undoing.** Substitute $f$ into your answer and you must get
$x$ back. This is not an optional flourish — it is how the checks in
this notebook work, and it catches every algebra slip in the collect-and-
factorise step:

$$f^{-1}(f(t)) = t \quad\text{for every } t \text{ in the domain of } f.$$

**Notation.** The answer is $f^{-1}(x) = \ldots$, not $x = \ldots$ and
not $y = \ldots$. And $f^{-1}$ is never $\dfrac{1}{f}$; the notation is
borrowed, the meaning is not.
""")

md(r"""
## Task 14 🟢 — the inverse of a rational function

The function $f$ is defined by
$f(x) = \dfrac{7x+7}{2x-4}$ for $x \in \mathbb{R}$, $x \ne 2$.

Find $f^{-1}(x)$, the inverse function of $f$.

The check substitutes $f$ into whatever you write and requires $x$ back,
so an equivalent form is accepted and an algebra slip is not.

*Source: May 2023 TZ1, Paper 1, Q1(c) (3 marks, no calculator).*
""")

code(r"""
my14 = ...               # f⁻¹(x)

verify_inverse('Task 14', my14, (7*x + 7)/(2*x - 4),
               domain=Interval.open(2, 20))
""")

md(r"""
## Task 15 🟡 — inverse of a logarithm, and what it does to the graph

The function $g$ is defined by $g(x) = 1 + \log_2 x$, where
$x \in \mathbb{R}^{+}$.

**(a)** Find an expression for $g^{-1}(x)$.

**(b)** Describe a sequence of transformations that maps the graph of
$y = g^{-1}(x)$ onto the graph of $y = f(x)$, where $f(x) = 4^{x}$.

Part (b) is not checked here — naming transformations in the right order
is B3's technique. Write your answer down, then compare it with the
solution; the order is the whole mark.

*Source: May 2025 TZ2, Paper 1, Q10(b) (4 marks, no calculator).*
""")

code(r"""
my15 = ...               # g⁻¹(x)

verify_inverse('Task 15', my15, 1 + log(x, 2), domain=Interval.open(0, 12))
""")

md(r"""
---
## Theory 8. Where an inverse exists, and on which domain

**Existence.** $f$ has an inverse exactly when it is one-to-one: no
horizontal line meets the graph twice. A function that turns — a
parabola, a cosine — is one-to-one only up to its turning point, so the
question becomes "where does $f$ turn?"

$$f(x) = \cos(x-k), \quad 0 \le x \le a .$$

The graph is a cosine wave shifted right by $k$. Starting from $x=0$ it
is monotonic until the first turning point, and that point is where
$f'(x) = -\sin(x-k)$ first vanishes for $x>0$. For $\pi < k < 2\pi$ that
happens at $x = k - \pi$, so $a = k-\pi$ is the largest domain that
keeps an inverse.

**The swap.** Once the inverse exists, its domain and range are the
range and domain of the original — swapped, both of them:

$$\text{domain}(f^{-1}) = \text{range}(f), \qquad
\text{range}(f^{-1}) = \text{domain}(f).$$

Copying the domain of $f$ across is the standard mistake, and it is
usually visible: an inverse whose domain is the same as $f$'s is
suspicious unless the function is self-inverse.

**So you have to be able to read a range.** In May 2025 TZ2 Paper 1,
$f(x) = \frac{3x-2}{2x+1}$ and $g(x) = -f(x)$ on $x \ge 0$. Reflecting
in the $x$-axis sends the horizontal asymptote $y = \frac32$ to
$y = -\frac32$ and the value $f(0) = -2$ to $g(0) = 2$; $g$ decreases
from $2$ towards $-\frac32$ without reaching it, so the range is
$-\frac32 < y \le 2$. Reading ranges properly is B4's subject; here it
is a prerequisite, because the range of $f$ is the answer to "state the
domain of $f^{-1}$".

**Endpoints are marks.** $[0,\sqrt3]$ and $(0,\sqrt3)$ are different
answers. Whether an endpoint is attained follows from whether the
original attains it — $f$ on the closed $[1,2]$ has a closed range.
""")

md(r"""
## Task 16 🟡 — the largest domain that keeps an inverse

Let $f(x) = \cos(x-k)$, where $0 \le x \le a$ and $a, k \in
\mathbb{R}^{+}$.

**(a)** For $k = \dfrac{\pi}{2}$, find the largest value of $a$ for
which $f^{-1}$ exists.

**(b)** Find the largest such $a$ when $k = \pi$.

**(c)** Find the largest such $a$ when $\pi < k < 2\pi$, giving your
answer in terms of $k$.

Sketch each case before answering — one picture settles all three.
Answers are exact.

*Source: November 2022, Paper 1, Q8 (2 + 1 + 2 marks, no calculator).*
""")

code(r"""
my16a = ...              # largest a for k = π/2
my16b = ...              # largest a for k = π
my16c = ...              # largest a for π < k < 2π, in terms of k

verify_exact('Task 16(a)', my16a, pi/2)
verify_exact('Task 16(b)', my16b, pi)
check_expr('Task 16(c)', my16c, '""" + D_16C + r"""')
""")

md(r"""
## Task 17 🔴 — inverse, domain and range together

Consider the function $f(x) = \sqrt{x^2 - 1}$, where $1 \le x \le 2$.

**(a)** Show that the inverse function of $f$ is
$f^{-1}(x) = \sqrt{x^2+1}$.

**(b)** State the domain of $f^{-1}$.

**(c)** State the range of $f^{-1}$.

Enter the inverse in (a) — the check will substitute $f$ into it. For
(b) and (c) enter sets: `Interval(0, sqrt(3))`, `Interval(1, 2)`.

*Source: May 2022 TZ1, Paper 2, Q10(b) (5 marks). The corpus records
a different formula for this answer; the paper is what is used here, and
the reason is in the solution.*
""")

code(r"""
my17a = ...              # f⁻¹(x)
my17b = ...              # domain of f⁻¹
my17c = ...              # range of f⁻¹

verify_inverse('Task 17(a)', my17a, sqrt(x**2 - 1), domain=Interval(1, 2))
check_domain('Task 17(b)', my17b, '""" + D_17B + r"""')
check_domain('Task 17(c)', my17c, '""" + D_17C + r"""')
""")

md(r"""
## Task 18 🔴 — justify existence, then find it

The function $g$ is defined by

$$g(x) = \frac{1}{1+2x^2}, \qquad 0 \le x < K,
\quad\text{where } K = \frac{1}{\sqrt2}.$$

**(a)** Justify that $g^{-1}$ exists.

**(b)** Find $g^{-1}(x)$, giving its domain.

Part (a) is an R1 — one sentence, no algebra — and there is nothing to
type; write it down and compare with the solution. For (b), enter the
expression and the domain.

*Source: May 2025 TZ1, Paper 2, Q12(d) (6 marks). $g$ is the limit of
the family $f_n$ from task 9, and $K$ is where that series stops
converging.*
""")

code(r"""
my18a = ...              # g⁻¹(x)
my18b = ...              # domain of g⁻¹

verify_inverse('Task 18(a)', my18a, 1/(1 + 2*x**2),
               domain=Interval.Ropen(0, 1/sqrt(2)))
check_domain('Task 18(b)', my18b, '""" + D_18 + r"""')
""")

md(r"""
---
## Theory 9. Choosing the branch — the R1 at the end of the root

Whenever the swap ends in $y^2 = \text{something}$, the algebra offers
two functions and only one of them is the inverse:

$$y = \pm\sqrt{\text{something}} .$$

**What chooses.** The values of $f^{-1}$ are the inputs of $f$, so

$$\text{range}(f^{-1}) = \text{domain}(f),$$

and you keep the branch whose values lie in the domain of $f$. If $f$
was defined on $x > 3$, then $f^{-1}$ must take values above 3, and the
negative root cannot. If $f$ was defined on $x \ge 0$, the positive root
survives.

Note which set decides: the **range** of $f^{-1}$, not its domain. They
are different sets, and only one of them is about the sign.

**Say it.** The mark is R1, awarded for the sentence "the negative root
is rejected because the domain of $g$ is $x>3$". A correct final formula
with no reason loses it.

**Why checking by $f(f^{-1}(x)) = x$ will not save you.** Take
$f(x)=\sqrt{x^2-1}$ on $[1,2]$ and the wrong branch
$g(x) = -\sqrt{x^2+1}$. Then

$$f(g(x)) = \sqrt{\left(-\sqrt{x^2+1}\right)^2 - 1} = \sqrt{x^2} = x$$

for $x \ge 0$ — the square erases the sign, and the wrong branch passes.
Compose the other way and it fails at once:

$$g(f(t)) = -\sqrt{t^2-1+1} = -t \ne t .$$

That is why every inverse in this notebook is checked as
$f^{-1}(f(t)) = t$, and it is the same asymmetry the R1 is testing.
""")

md(r"""
## Task 19 🔴 — completing the square inside an inverse

A function $g$ is defined by

$$g(x) = \frac{1}{x^2-2x-3}, \qquad x \in \mathbb{R}, \ x > 3 .$$

**(a)** Show that $g^{-1}(x) = 1 + \dfrac{\sqrt{4x^2+x}}{x}$.

**(b)** State the domain of $g^{-1}$.

Completing the square is the move: $y^2-2y-3 = (y-1)^2-4$. Then say
out loud which branch you keep and why — and remember that
$\sqrt{\frac{4x+1}{x}} = \frac{\sqrt{4x^2+x}}{x}$ only because $x > 0$.

*Source: May 2022 TZ2, Paper 1, Q11(b) (7 marks, no calculator).*
""")

code(r"""
my19a = ...              # g⁻¹(x)
my19b = ...              # domain of g⁻¹

verify_inverse('Task 19(a)', my19a, 1/(x**2 - 2*x - 3),
               domain=Interval.open(3, 20))
check_domain('Task 19(b)', my19b, '""" + D_19 + r"""')
""")

md(r"""
## Task 20 🔴 — an inverse through arcsin

A function $g$ is defined by

$$g(x) = \arcsin \frac{x^2-1}{x^2+1}, \qquad x \in \mathbb{R},\ x \ge 0
$$

— the function of task 8, restricted to $x \ge 0$ so that an inverse
exists.

**(a)** Find an expression for $g^{-1}(x)$, justifying your answer.

**(b)** State the domain of $g^{-1}$.

Apply $\sin$ to both sides after the swap, then solve for $y^2$. The
justification in (a) is the R1 of this rung.

*Source: May 2021 TZ2, Paper 2, Q12(d)(e) (5 + 1 marks).*
""")

code(r"""
my20a = ...              # g⁻¹(x)
my20b = ...              # domain of g⁻¹

verify_inverse('Task 20(a)', my20a, asin((x**2 - 1)/(x**2 + 1)),
               domain=Interval(0, oo))
check_domain('Task 20(b)', my20b, '""" + D_20 + r"""')
""")

md(r"""
---
## Trainer: name the technique in five seconds

Fifteen questions with no solutions. For each one write the code of the
technique — nothing else. No calculation is wanted; the point is to find
the first move before the arithmetic starts.

Codes: `comp` (evaluate a composite) · `build` (build the composite) ·
`ceq` (composite set equal to something) · `even` (substitute $-x$) ·
`iter` (compose $f$ with itself) · `prop` (the defining property of the
inverse) · `swap` (swap and solve) · `dom` (existence and domain) ·
`branch` (choose the branch)

1. Given $f(x) = 2x+1$ and $g(x) = x^2$, write down $(g \circ f)(x)$.
2. $f(x) = 3x-5$. Find $f^{-1}(x)$.
3. Given $f(x) = x^3+x$, find $f^{-1}(10)$.
4. $h(x) = x^2-4x$ and $k(x) = \sqrt{x}$. Find $(k \circ h)(6)$.
5. Show that $f(x) = x^4-3x^2+1$ is an even function.
6. $f(x) = \ln(x-2)$, $x>2$, has range $\mathbb{R}$. State the domain of $f^{-1}$.
7. $f(x) = mx+c$. Find $f(f(x))$.
8. $(f \circ g)(x) = x^2+6x+7$ and $g(x) = x+3$. Find $f(x)$.
9. $g(y) = y^2-6y$ for $y \le 3$. Find $g^{-1}$, justifying your choice of sign.
10. $f(x) = x^2-6x+5$, $0 \le x \le a$. Find the largest $a$ for which $f^{-1}$ exists.
11. $f(x) = \dfrac{x+2}{x-1}$, $x \ne 1$. Find $f^{-1}(x)$.
12. $f(x) = \dfrac1x$, $x \ne 0$. Find $f^{3}(x)$.
13. $f(x) = x-1$ and $g(x) = x^2+a$, and $(g \circ f)(3) = 7$. Find $a$.
14. Show that $f(x) = \dfrac{x}{x^2+1}$ is an odd function.
15. The graph of $f$ passes through $(2,7)$. Write down a point on the graph of $f^{-1}$.
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
## Task 21 🔴 — on the timer, 17 minutes

Part of a Paper 3 investigation. Eleven marks, target time about 17
minutes. You have already met the setup in task 10, so nothing here is
repeated: this is what the investigation does with the formula once it
has it.

For $f(x) = mx+c$ it is given that

$$f^{n}(x) = m^{n}x + c\,\frac{1-m^{n}}{1-m}, \qquad m \ne 1 .$$

**(b)(iii)** By using your expression from part (b)(ii), or otherwise,
find an expression in terms of $n$ for $f^{n}(x)$ when $m = 1$. [3]

**(d)** Now let $-1 < m < 1$. As $n \to \infty$, the family of graphs
$y = f^{n}(x)$ approaches the graph of a straight line $L$. Determine
the equation of $L$, giving your answer in terms of $c$ and $m$.
Enter the right-hand side only. [4]

**(e)(i)** Now let $m = -1$. Show that $f^{n}(x) = -x + c$ when $n$ is
odd. Enter $f^{n}(x)$ for odd $n$. [2]

**(e)(ii)** Find an expression for $f^{n}(x)$ when $n$ is even. [2]

*Source: May 2025 TZ3, Paper 3, Q1(b)(iii)(d)(e) (3 + 4 + 2 + 2 marks).
Part (d) is a limit, which belongs to E-series work; it is here because
the investigation asks for it in the same breath.*
""")

code(r"""
my21a = ...              # fⁿ(x) when m = 1
my21b = ...              # the right-hand side of the equation of L
my21c = ...              # fⁿ(x) when m = −1 and n is odd
my21d = ...              # fⁿ(x) when m = −1 and n is even

check_series('Task 21(b)(iii)', my21a, '""" + D_21A + r"""')
check_expr('Task 21(d)', my21b, '""" + D_21B + r"""')
check_series('Task 21(e)(i)', my21c, '""" + D_21C + r"""')
check_series('Task 21(e)(ii)', my21d, '""" + D_21D + r"""')
""")

md(r"""
---
# Solutions

A full discussion of every task, with the markscheme breakdown. Open it
after you have worked the task yourself: the point is not the answer but
where the marks are, and which of them a self-check cannot see.
""")

md(r"""
## Solution 1 — evaluating composites

**(a)** The tangent to $f$ at $x=4$ is $y = 6x-1$, so the point of
tangency is on both graphs:

$$f(4) = 6\cdot 4 - 1 = 23 \qquad (\text{and } f'(4) = 6).$$

Then $g(4) = 4^2 - 3\cdot4 = 4$, so

$$h(4) = f(g(4)) = f(4) = 23 .$$

**(b)** $f(0) = \dfrac{3\cdot0-2}{2\cdot0+1} = -2 .$

**(c)** $(f\circ g)(0) = f(g(0)) = f(1) = e^{2}(3-4) = -e^{2}
\approx -7.39 .$

**(d)** From $x_1+x_2 = 12$ we get $x_2 = 12-x_1$, so the product is

$$f(x_1) = x_1(12-x_1) .$$

```python
my1a = 23
my1b = -2
my1c = -exp(2)
my1d = x*(12 - x)
```

**Marks.** (a) M1 for writing $h(4)=f(g(4))$, A1 for 23. (b) A1
(the pair $(0,-2)$ is accepted). (c) M1 for composing in the correct
order, A1 for $-e^2$. (d) M1 for $x_2 = 12-x_1$, A1 for the product.

**The joke in (a).** $g(4) = 4$: the inner function sends 4 back to
itself. So the only thing you ever need to know about $f$ is $f(4)$, and
the tangent line hands it over. Candidates who set out to find a formula
for $f$ lost the question to the clock.

**What comes next in (a).** Part (d) of that question asks for the
tangent to $h$ at $x=4$. That needs $h'(4) = f'(g(4))\,g'(4) =
6 \cdot 5 = 30$, giving $y = 30(x-4)+23$. Composition and the chain rule
are the same picture seen twice.

**What comes next in (c).** The following part asks for
$(f\circ g)'(0) = f'(g(0))\,g'(0) = f'(1)\cdot 2$. With
$f'(x) = e^{2x}(6x-5)$ that is $2e^{2} \approx 14.8$ — and the factor
$g'(0)=2$ is precisely the mark.
""")

md(r"""
## Solution 2 — write down the composite

$(g\circ f)$ means $f$ first:

$$(g\circ f)(x) = g(x-3) = (x-3)^2 + k^2 = x^2-6x+9+k^2 .$$

```python
my2 = (x - 3)**2 + k**2
```

**Marks.** M1 for attempting the composite, A1 for the expression. Both
the bracketed and the expanded form are accepted.

**The other order is a different function.** $(f\circ g)(x) =
g(x)-3 = x^2+k^2-3$. It is just as plausible on the page and worth
nothing.

**Brackets.** $(x-3)^2$ is $x^2-6x+9$. The two ways to lose the A1 here
are $x^2-9$ and $x^2-3$, and both come from substituting without
writing the bracket first.
""")

md(r"""
## Solution 3 — a "show that" with logarithms

$$(f\circ g)(x) = f\big(1+\log_2 x\big) = 4^{\,1+\log_2 x}
= 4\cdot 4^{\log_2 x} .$$

Now rewrite base 4 as base 2:

$$4^{\log_2 x} = \left(2^{2}\right)^{\log_2 x} = 2^{\,2\log_2 x}
= \left(2^{\log_2 x}\right)^{2} = x^{2},$$

so $(f\circ g)(x) = 4x^{2}$, as required.

```python
my3 = 4**(1 + log(x, 2))
```

**Marks.** M1 for attempting the composite, A1 for splitting the
exponent as $4\cdot4^{\log_2 x}$, A1 for landing on $4x^2$.

**The natural-log route.** $4^{\log_2 x} = e^{\ln 4 \cdot \log_2 x}
= e^{2\ln 2 \cdot \frac{\ln x}{\ln 2}} = e^{2\ln x} = x^2$. Same three
lines, no cleverness needed.

**Order, again.** $(g\circ f)(x) = 1 + \log_2\left(4^{x}\right)
= 1 + 2x$ — a straight line, not a parabola. The two composites of these
two functions could hardly look less alike, and that is why the M1 is
for the order.

**Why enter the unsimplified form?** Because a "show that" is a claim
about a transition, not about an answer. The check compares your
starting expression with the printed result as *functions*; if they
agree everywhere, your first line was right, and the rest is exponent
arithmetic you can see on the page.
""")

md(r"""
## Solution 4 — a composite identity

Substituting the definitions and putting everything over 4:

$$\big(f(t)\big)^2 + \big(g(t)\big)^2
= \frac{\left(e^{t}+e^{-t}\right)^2 + \left(e^{t}-e^{-t}\right)^2}{4}.$$

Expanding, the cross terms cancel:

$$= \frac{\left(e^{2t}+2+e^{-2t}\right)+\left(e^{2t}-2+e^{-2t}\right)}{4}
= \frac{2e^{2t}+2e^{-2t}}{4}
= \frac{e^{2t}+e^{-2t}}{2} = f(2t).$$

```python
my4 = (exp(2*t) + exp(-2*t))/2
```

**Marks.** METHOD 1: M1 for substituting $f$ and $g$, M1 for the single
fraction, A1 for the simplification — then AG. METHOD 2 runs backwards
from $f(2t) = \frac{(e^t)^2+(e^{-t})^2}{2}$ and is worth the same;
mixtures of the two are accepted.

**What these functions are.** $f = \cosh$ and $g = \sinh$, and the
identity is $\cosh^2 t + \sinh^2 t = \cosh 2t$. The exam does not name
them and does not have to — everything follows from the two exponentials.

**Careful which identity.** The famous one is
$\cosh^2 - \sinh^2 = 1$, with a minus. Here the sign is plus and the
answer is $f(2t)$, not 1. Reaching for the remembered identity instead
of expanding is the way to lose all three marks.
""")

md(r"""
## Solution 5 — the composite pinned at a point

Substitute $x=2$ into the composite from task 2:

$$(2-3)^2 + k^2 = 10 \ \Longrightarrow\ 1 + k^2 = 10
\ \Longrightarrow\ k^2 = 9 \ \Longrightarrow\ k = \pm 3 .$$

```python
my5 = [-3, 3]
```

**Marks.** M1 for substituting $x=2$ into *their* composite and setting
it equal to 10, (A1) for $k^2=9$, A1 for $k=\pm3$.

**Both signs.** $k$ is a real constant with no sign restriction, and the
question says "values", plural. $k^2=9$ is where the answer is decided,
and stopping at $k=3$ costs the final A1.

**The M1 follows your own work.** If task 2 came out wrong, this mark is
still available — the examiner substitutes into whatever composite you
wrote. Which is another reason to write the composite down as a separate
line rather than in your head.
""")

md(r"""
## Solution 6 — find the function, not the number

With $f(x) = ax+b$,

$$(g\circ f)(x) = (ax+b)^2 + (ax+b) + 3
= a^2x^2 + (2ab+a)x + \left(b^2+b+3\right).$$

Comparing with $4x^2-14x+15$:

$$a^2 = 4 \Rightarrow a = \pm2, \qquad 2ab + a = -14 .$$

Each $a$ carries its own $b$:

$$a=2:\ 4b+2 = -14 \Rightarrow b = -4, \qquad
a=-2:\ -4b-2 = -14 \Rightarrow b = 3 .$$

The constant term checks both: $(-4)^2-4+3 = 15$ and $3^2+3+3 = 15$.

$$f(x) = 2x-4 \qquad\text{or}\qquad f(x) = -2x+3 .$$

```python
my6 = [2*x - 4, -2*x + 3]
```

**Marks.** M1 for attempting $(g\circ f)(x)$, A1 for the expanded form,
M1 for equating corresponding terms, A1 for $a=\pm2$, M1 for using
$2ab+a=-14$ to pair the values, A1A1 for the two functions.

**Pairing is the whole difficulty.** $a=\pm2$ and $b\in\{-4,3\}$ is not
the answer: it suggests four functions, and only two of them work. The
equation $2ab+a=-14$ is what ties each $a$ to its own $b$, and the mark
scheme gives that step its own M1.

**The constant term is free verification.** It was never used to find
anything, so if it comes out as 15 for both pairs, the work is right.
Two lines of arithmetic, and the question is closed.
""")

md(r"""
## Solution 7 — a composite equal to an angle

$$(h\circ g)(a) = h(g(a)) = \arctan\frac{g(a)}{2} = \frac{\pi}{4}
\ \Longrightarrow\ \frac{g(a)}{2} = \tan\frac{\pi}{4} = 1
\ \Longrightarrow\ g(a) = 2 .$$

Now unwind $g$:

$$\frac{1}{a^2-2a-3} = 2 \Rightarrow a^2-2a-3 = \frac12
\Rightarrow 2a^2-4a-7 = 0,$$

$$a = \frac{4 \pm \sqrt{16+56}}{4} = \frac{4\pm\sqrt{72}}{4}
= \frac{4 \pm 6\sqrt2}{4} = 1 \pm \frac{3}{2}\sqrt2 .$$

The domain of $g$ is $x>3$, and $1-\frac32\sqrt2 \approx -1.12$ is not
in it. So

$$a = 1 + \frac{3}{2}\sqrt2 \approx 3.12 .$$

```python
my7 = 1 + 3*sqrt(2)/2
```

**Marks.** M1 for attempting $(h\circ g)(a)$, A1 for
$\arctan\frac{g(a)}{2}$, M1 for solving for $g(a)$, A1 for $g(a)=2$,
then A1 for the quadratic, M1 for solving it and A1 for the surd form.

**Two unwrappings, one after the other.** First $\arctan$ (apply
$\tan$), then $g$ (multiply up). Each is a step the markscheme pays for
separately, and neither needs the formula for $g^{-1}$ — although
$a = g^{-1}(2)$ is an accepted route, and task 19 finds that formula.

**$\sqrt{72}$ has to be simplified.** The answer is required in the form
$p + \frac{q}{2}\sqrt r$ with positive integers, so
$\frac{4+\sqrt{72}}{4}$ is not yet an answer:
$\sqrt{72} = 6\sqrt2$ gives $1+\frac32\sqrt2$, that is $p=1$, $q=3$,
$r=2$.

**The rejected root is a mark.** Not because it is ugly, but because
$g$ was only ever defined for $x>3$. Writing "reject $1-\frac32\sqrt2$
since $a>3$" is the sentence the examiner is looking for.
""")

md(r"""
## Solution 8 — show that it is even

$$f(-x) = \arcsin\frac{(-x)^2-1}{(-x)^2+1}
= \arcsin\frac{x^2-1}{x^2+1} = f(x),$$

**therefore $f$ is an even function.**

```python
my8 = asin((x**2 - 1)/(x**2 + 1))
```

**Marks.** R1, and it is for the conclusion. A sketch showing symmetry
in the $y$-axis, with the symmetry indicated, is also accepted.

**Every $x$ appears squared.** That is the entire content: $(-x)^2 =
x^2$, so nothing in the expression changes. When a function is built
only from even powers of $x$, its parity is visible before any algebra.

**What the check cannot see.** It compares $f(-x)$ with $f(x)$ as
expressions and says they agree. The mark is for writing the sentence
"therefore $f$ is even" on your paper. No self-check in this notebook can
award an R1; that is what the solutions are for.

**A note on the archive.** The corpus records this function upside down,
as $\arcsin\frac{1-x^2}{1+x^2}$. Parity survives the misprint — both
versions are even — but the inverse does not, which is why task 20 uses
the function as the paper prints it.
""")

md(r"""
## Solution 9 — even for every $n$

Write the sum out for $n=3$:

$$f_3(x) = \sum_{r=0}^{3}\left(-2x^2\right)^r
= 1 - 2x^2 + 4x^4 - 8x^6 .$$

Now the general argument, which is what the three marks are for.
Replacing $x$ by $-x$ inside the general term,

$$\left(-2(-x)^2\right)^{r} = \left(-2x^2\right)^{r},$$

so **every** term of the sum is unchanged, and therefore

$$f_n(-x) = \sum_{r=0}^{n}\left(-2(-x)^2\right)^{r}
= \sum_{r=0}^{n}\left(-2x^2\right)^{r} = f_n(x)$$

for every $n$. Hence $f_n$ is even.

```python
my9 = 1 - 2*x**2 + 4*x**4 - 8*x**6
```

**Marks.** M1 for attempting to replace $x$ by $-x$, A1 for a correct
expression for $f_n(-x)$, A1 for reaching $f_n(x)$ — then AG.

**"For all values of $n$" is the point.** Checking $n=3$ is an example,
not a proof. The one line about the general term does every $n$ at once,
and it is shorter than writing out a single case.

**Where this family goes.** $f_n$ is a geometric series with ratio
$-2x^2$; it converges exactly when $|2x^2|<1$, that is
$|x| < \frac{1}{\sqrt2}$, and its sum is $\frac{1}{1+2x^2}$. That
function, on $0\le x < \frac{1}{\sqrt2}$, is the $g$ of task 18 — and
$K = \frac{1}{\sqrt2}$ is where the series stops converging.
""")

md(r"""
## Solution 10 — the self-composite of a linear function

**(a)** $f^{2}(x) = f(f(x)) = m(mx+c)+c = m^{2}x + mc + c
= m^{2}x + c(1+m).$

**(b)** $f^{3}(x) = f\big(f^{2}(x)\big) = m\big(m^{2}x+c(1+m)\big)+c
= m^{3}x + cm + cm^{2} + c = m^{3}x + c\left(1+m+m^{2}\right).$

**(c)** The pattern is now visible:
$f^{4}(x) = m^{4}x + c\left(1+m+m^{2}+m^{3}\right).$

**(d)** In general

$$f^{n}(x) = m^{n}x + c\left(1+m+\cdots+m^{n-1}\right)
= m^{n}x + c\,\frac{1-m^{n}}{1-m}, \qquad m \ne 1 .$$

```python
my10a = m**2*x + c*(1 + m)
my10b = m**3*x + c*(1 + m + m**2)
my10c = m**4*x + c*(1 + m + m**2 + m**3)
my10d = m**n*x + c*(1 - m**n)/(1 - m)
```

**Marks.** (a) M1 for attempting $f^2$, A1 for $m(mx+c)+c$, A1 for
$m^2x+cm+c$, then AG. (b) M1 and A1, then AG. (c) A1, equivalent forms
accepted. (d) A1 for $m^{n}x$ and A1 for the constant — the two halves
are marked separately, because they are two different observations.

**Do not tidy too early.** $f^2(x) = m^2x + mc + c$ is where the pattern
lives; collapsing it to a single number for particular $m$ and $c$
destroys the question. The instruction "show that $f^2(x) = m^2x+c(1+m)$"
is telling you which grouping to keep.

**Two sequences, not one.** The coefficient of $x$ is a plain geometric
sequence $m^n$. The constant is a geometric *sum*, and closing it with
$\frac{1-m^{n}}{1-m}$ is A2's formula doing the work. Recognising that
the constant is a sum is what makes part (d) two marks rather than one.

**The exclusion $m\ne1$ is real.** At $m=1$ the closed form reads
$\frac{0}{0}$. The sum itself is fine — it is $1+1+\cdots+1 = n$ — which
is exactly what the timed task asks about.

**And the proof?** Part (c) of the original question proves the formula
by induction, for eight marks. That is A7's technique; this practicum
stops at finding the pattern, which is the harder half to teach and the
easier half to do.
""")

md(r"""
## Solution 11 — one value of the inverse, two ways

**(a)** $f^{-1}(8)$ is the $x$ with $f(x)=8$:

$$4^{x} = 8 \iff 2^{2x} = 2^{3} \iff 2x = 3 \iff x = \frac32 .$$

Equivalently $f^{-1}(8) = \log_4 8 = \frac{\ln 8}{\ln 4}
= \frac{3\ln2}{2\ln2} = \frac32$.

**(b)** $f^{-1}(2)$ is the solution of $4\cot x + \sin x = 2$ on
$0<x<\pi$. On a GDC, $x = 1.31837\ldots \approx 1.32$.

```python
my11a = Rational(3, 2)
my11b = 1.32
```

**Marks.** (a) A1 for turning the question into $4^x=8$ (or into
$\log_4 8$), M1 for using a common base or a change of base, A1 for
$\frac32$. (b) A1 for 1.32.

**Neither part needs the inverse function.** $f^{-1}(a)=b \iff f(b)=a$
turns both into ordinary equations. Deriving $f^{-1}(x) = \log_4 x$
first is not wrong, just longer; deriving an inverse for
$4\cot x + \sin x$ is not possible at all.

**Why does $f^{-1}$ even exist in (b)?** Because

$$f'(x) = \cos x - \frac{4}{\sin^{2}x} < 0
\quad\text{for } 0<x<\pi,$$

since $\frac{4}{\sin^2 x} \ge 4$ while $\cos x \le 1$. So $f$ is
strictly decreasing on the whole interval, hence one-to-one. The
question does not ask, but this is the reasoning rung 8 makes explicit.

**The one honest calculator mark in this practicum.** Everything else in
the "calculator" papers of this topic wants an exact expression. Here
the answer genuinely is a decimal, and it wants three significant
figures.
""")

md(r"""
## Solution 12 — reading the inverse off a graph

**(a)** The domain of $f^{-1}$ is the range of $f$. From the graph $f$
takes every value from $-3$ to $5$ and attains both, so

$$\text{domain}\left(f^{-1}\right) = -3 \le x \le 5 .$$

**(b)** Apply $f$ to both sides of $f^{-1}(2x-7) = -3$:

$$2x-7 = f(-3) = -1 \ \Longrightarrow\ 2x = 6 \ \Longrightarrow\ x = 3 .$$

```python
my12a = Interval(-3, 5)
my12b = 3
```

**Marks.** (a) A1; interval notation $[-3,5]$ is accepted. (b) M1 for
$2x-7 = f(-3)$ (or for $f^{-1}(-1)=-3$), A1 for $2x-7=-1$, A1 for $x=3$.

**The trap in (b).** Setting $2x-7 = -3$ gives $x=2$ and no marks. The
$-3$ on the right of $f^{-1}(\cdots) = -3$ is an *output* of $f^{-1}$,
so it is an *input* of $f$; the thing equal to $2x-7$ is $f(-3)$.
Writing the property out in full before substituting anything is the way
to keep this straight.

**Why (a) is one mark and not three.** Because on this rung the work is
reading a range, not computing one. The graph does it for you. In a
question without a picture — task 17, task 18 — finding the range is
most of the work, and the marks move accordingly.
""")

md(r"""
## Solution 13 — a function equal to its own inverse

**METHOD 2 (shorter).** $g = g^{-1}$ says exactly that
$g(g(x)) = x$. Compute:

$$g(g(x)) = \frac{a\cdot\frac{ax+4}{3-x}+4}{3-\frac{ax+4}{3-x}}
= \frac{a(ax+4)+4(3-x)}{3(3-x)-(ax+4)}
= \frac{\left(a^{2}-4\right)x + 4a+12}{-(a+3)x+5}.$$

Setting that equal to $x$ and clearing the denominator,

$$\left(a^{2}-4\right)x + 4a + 12 = -(a+3)x^{2} + 5x .$$

The coefficient of $x^{2}$ must vanish: $a+3 = 0$, so $a = -3$. The
other two coefficients agree with that value ($a^2-4 = 5$ and
$4a+12 = 0$), which confirms it.

**METHOD 1.** Swap and solve: $y = \frac{ax+4}{3-x}$ gives
$3y - xy = ax+4$, so $x(a+y) = 3y-4$ and

$$g^{-1}(x) = \frac{3x-4}{x+a} .$$

Equating $\frac{ax+4}{3-x} \equiv \frac{3x-4}{x+a}$ and comparing
coefficients gives $a=-3$ again.

```python
my13 = -3
```

**Marks.** METHOD 1: M1 for attempting $x$ in terms of $y$, A1 for the
rearrangement, A1 for $g^{-1}$, A1 for $a=-3$. METHOD 2: M1 for
attempting $g(g(x))$ and equating to $x$, A1 for the composite, A1 for
the cleared equation, A1 for equating coefficients of $x^2$.

**Check it.** With $a=-3$, $g(x) = \frac{4-3x}{3-x}$. Then $g(0) =
\frac43$ and $g\!\left(\frac43\right) = \frac{4-4}{3-\frac43} = 0$. The
pair $(0,\frac43)$ and $(\frac43,0)$ is the reflection in $y=x$ that
self-inverse means.

**A fact worth carrying.** For any $g(x) = \frac{\alpha x+\beta}
{\gamma x+\delta}$, the composite $g(g(x))$ is the identity exactly when
$\alpha + \delta = 0$ (or $g$ is already the identity). Here
$\alpha = a$ and $\delta = 3$, so $a=-3$ in one line. The exam will not
give marks for quoting it, but it tells you in advance what the answer
must be.

**And a warning about the archive.** The corpus records this function
with its denominator reversed, as $\frac{ax+4}{x-3}$. That is a
different question, and it has a different answer: $a = +3$. This is the
one place in the topic where a mangled formula also carries a mangled
answer, and the only defence is to derive the value rather than
remember it.
""")

md(r"""
## Solution 14 — the inverse of a rational function

Write $y = f(x)$, interchange $x$ and $y$, and solve:

$$x = \frac{7y+7}{2y-4} \ \Longrightarrow\ x(2y-4) = 7y+7
\ \Longrightarrow\ 2xy - 4x = 7y + 7,$$
$$2xy - 7y = 4x + 7 \ \Longrightarrow\ y(2x-7) = 4x+7,$$
$$f^{-1}(x) = \frac{4x+7}{2x-7}, \qquad x \ne \frac72 .$$

```python
my14 = (4*x + 7)/(2*x - 7)
```

**Marks.** M1 for interchanging $x$ and $y$ (seen anywhere), A1 for
correct working with the $y$ terms on the same side, A1 for the final
expression.

**The three moves never change.** Multiply out, collect every $y$ on one
side, factorise. The factorisation is the step people skip, and without
it there is a $y$ left on the right and the "answer" is not a function.

**Where does $x \ne \frac72$ come from?** It is the value that kills the
new denominator, and it is $f$'s horizontal asymptote: $f(x) \to
\frac{7}{2}$ as $x\to\pm\infty$, so $\frac72$ is the one value $f$ never
takes, hence the one value $f^{-1}$ cannot be given. The excluded point
of an inverse is always the asymptote of the original.

**Check by undoing.** $f^{-1}(f(t))$: substitute and everything cancels
back to $t$. That is what the check in the cell above does, symbolically
here — for a rational function `simplify` finishes the job on its own.
""")

md(r"""
## Solution 15 — inverse of a logarithm, and what it does to the graph

**(a)** $x = 1 + \log_2 y \Rightarrow \log_2 y = x-1
\Rightarrow g^{-1}(x) = 2^{\,x-1}.$

**(b)** Write the target in base 2: $f(x) = 4^{x} = 2^{2x}$. Starting
from $y = 2^{\,x-1}$:

$$2^{\,x-1} \ \xrightarrow{\ \text{translate 1 left}\ } \ 2^{\,x}
\ \xrightarrow{\ \text{horizontal stretch, factor } \frac12\ } \
2^{\,2x} = 4^{x}.$$

```python
my15 = 2**(x - 1)
```

**Marks.** M1 for interchanging $x$ and $y$, A1 for $g^{-1}(x)=2^{x-1}$,
A1 for one correct transformation, A1 for both in the correct order.

**The order carries the last mark.** Do the stretch first and
$2^{x-1}$ becomes $2^{2x-1}$; translating left by 1 then gives
$2^{2x+1}$, which is $2\cdot 4^{x}$, not $4^x$. Two correct
transformations in the wrong order are worth one mark out of two.

**Why $g^{-1}$ is an exponential.** Because $g$ was a logarithm, and the
two are inverse operations. The "$1+$" outside the logarithm becomes the
"$-1$" in the exponent — an outside shift on $g$ turns into an inside
shift on $g^{-1}$, which is the reflection in $y=x$ doing its work.

**Naming transformations is B3.** The check above only looks at the
formula. Getting the sequence and its order right is a technique of its
own, and this question is where the two topics touch.
""")

md(r"""
## Solution 16 — the largest domain that keeps an inverse

**(a)** $k = \frac{\pi}{2}$: $f(x) = \cos\left(x-\frac\pi2\right)
= \sin x$, which increases on $\left[0,\frac\pi2\right]$ and turns at
$\frac\pi2$. So $a = \dfrac{\pi}{2}$.

**(b)** $k = \pi$: $f(x) = \cos(x-\pi) = -\cos x$, which increases on
$[0,\pi]$ and turns at $\pi$. So $a = \pi$.

**(c)** $\pi < k < 2\pi$: differentiate,
$f'(x) = -\sin(x-k)$, and at the left endpoint
$f'(0) = -\sin(-k) = \sin k < 0$, so $f$ starts by decreasing. It keeps
decreasing until $f'$ vanishes, that is until $\sin(x-k)=0$; the first
such $x>0$ is $x - k = -\pi$, i.e. $x = k-\pi$, which lies in
$(0,\pi)$. So $a = k - \pi$.

```python
my16a = pi/2
my16b = pi
my16c = k - pi
```

**Marks.** (a) A2 (A1A0 for a correct sketch with the wrong $a$).
(b) A1. (c) A1 for a sketch showing the wave decreasing as it crosses
the $y$-axis, A1 for $a = k-\pi$.

**One picture answers all three.** $\cos(x-k)$ is the cosine wave slid
$k$ to the right. Draw it, mark $x=0$, and read off where the curve
first turns to the right of that mark. Every part of this question is
that one reading.

**"Largest $a$", not "largest interval".** The domain is forced to start
at 0. There are longer intervals on which $\cos(x-k)$ is one-to-one —
they just do not begin where the question begins.

**Endpoints are safe here.** At the turning point the function is still
one-to-one on the closed interval: it takes each value once and stops.
Including $x = a$ is correct, and the markscheme prints it.
""")

md(r"""
## Solution 17 — inverse, domain and range together

**(a)** $y = \sqrt{x^2-1}$; interchange and solve:

$$x = \sqrt{y^2-1} \Rightarrow x^2 = y^2-1 \Rightarrow y^2 = x^2+1
\Rightarrow y = \sqrt{x^2+1},$$

the positive root because the values of $f^{-1}$ lie in $[1,2]$, the
domain of $f$.

**(b)** The domain of $f^{-1}$ is the range of $f$. On $[1,2]$ the
function $\sqrt{x^2-1}$ increases from $f(1)=0$ to $f(2)=\sqrt3$, both
attained, so

$$\text{domain}\left(f^{-1}\right) = \left[0,\sqrt3\right].$$

**(c)** The range of $f^{-1}$ is the domain of $f$, that is $[1,2]$.

```python
my17a = sqrt(x**2 + 1)
my17b = Interval(0, sqrt(3))
my17c = Interval(1, 2)
```

**Marks.** M1 for interchanging (seen anywhere), A1 for $x^2 = y^2-1$,
A1 for $y = \sqrt{x^2+1}$, then AG; A1 for the domain, A1 for the range.

**The wrong branch passes the wrong test.** $-\sqrt{x^2+1}$ satisfies
$f\big(g(x)\big) = \sqrt{\left(-\sqrt{x^2+1}\right)^2-1} = x$ for
$x\ge0$: the square erases the sign. Composed the other way it fails
immediately, $g(f(t)) = -t$. This is the question that fixed the
direction of the check used throughout this notebook.

**Closed brackets, both ends.** $f$ is defined on a closed interval and
is continuous, so it attains both $0$ and $\sqrt3$. Writing
$\left(0,\sqrt3\right)$ costs the mark, and the difference is not a
technicality — it is whether $f^{-1}(0)$ is defined.

**A note on the archive.** The corpus records this answer as
$f^{-1}(x) = \frac{2}{x^2}+1$, and the function itself as
$\sqrt{\frac{2}{x-1}}$; neither survived the extraction from the PDF.
The paper settles it twice over: the printed inverse is $\sqrt{x^2+1}$,
and part (c) of the same question gives the volume of revolution about
the $y$-axis as $\pi\left(\frac{h^3}{3}+h\right)$, which is exactly
$\pi\int_0^h \left(x^2+1\right)\,\mathrm{d}x$.
""")

md(r"""
## Solution 18 — justify existence, then find it

**(a)** On $[0,K)$,

$$g'(x) = -\frac{4x}{\left(1+2x^2\right)^2} < 0 \quad\text{for } x>0,$$

so $g$ is strictly decreasing: it has no turning point, it takes each
value once, it is one-to-one, and therefore $g^{-1}$ exists.

**(b)** Interchange and solve:

$$x = \frac{1}{1+2y^2} \Rightarrow 1+2y^2 = \frac1x
\Rightarrow y^2 = \frac{1-x}{2x} \Rightarrow
g^{-1}(x) = \sqrt{\frac{1-x}{2x}},$$

the positive root because the values of $g^{-1}$ lie in $[0,K)$.

For the domain, find the range of $g$: at $x=0$, $g=1$ (attained), and
as $x \to K^{-} = \frac{1}{\sqrt2}$ we get $2x^2 \to 1$ and
$g \to \frac12$, never reaching it. So the range of $g$ is
$\left(\frac12, 1\right]$ and

$$\text{domain}\left(g^{-1}\right) = \frac12 < x \le 1 .$$

```python
my18a = sqrt((1 - x)/(2*x))
my18b = Interval.Lopen(Rational(1, 2), 1)
```

**Marks.** (a) A1 for "$g$ is one-to-one", R1 for the reason — strictly
decreasing, or no points of zero gradient. (b) M1 for rearranging and
swapping, A1 for $y^2 = \frac{1-x}{2x}$, A1 for the positive root, A1
for the domain.

**Two marks for a sentence.** Part (a) has no algebra in it at all. The
A1 is the claim, the R1 is the reason, and a candidate who jumps
straight to the formula in (b) loses both.

**The endpoints come from opposite ends.** $x=1$ is included because
$g(0)=1$ is attained; $x=\frac12$ is excluded because $K$ itself is not
in the domain of $g$. One closed, one open, and each traceable to a
specific end of the original interval.

**Where this $g$ came from.** It is the sum of the series $f_n$ of task
9, and $K=\frac{1}{\sqrt2}$ is the radius of convergence. The same
question walks from a family of polynomials to a rational function to
its inverse — which is the reason Paper 2 question 12 is worth 20 marks.
""")

md(r"""
## Solution 19 — completing the square inside an inverse

Interchange $x$ and $y$ in $g$ and complete the square:

$$x = \frac{1}{y^2-2y-3} \Rightarrow y^2-2y-3 = \frac1x
\Rightarrow (y-1)^2 - 4 = \frac1x
\Rightarrow (y-1)^2 = \frac{1+4x}{x}.$$

Take the square root — both branches, then choose:

$$y - 1 = \pm\sqrt{\frac{4x+1}{x}}.$$

The domain of $g$ is $x>3$, so the **values** of $g^{-1}$ must exceed 3;
the negative root gives values below 1 and is rejected. Hence

$$g^{-1}(x) = 1 + \sqrt{\frac{4x+1}{x}}
= 1 + \frac{\sqrt{4x^2+x}}{x},$$

the last step being legal because $x>0$.

For the domain: on $x>3$ the expression $x^2-2x-3$ increases from 0
(at $x=3$, excluded) to $\infty$, so $g$ decreases from $+\infty$
towards 0, attaining neither. The range of $g$ is $(0,\infty)$, so

$$\text{domain}\left(g^{-1}\right) = x > 0 .$$

```python
my19a = 1 + sqrt(4*x**2 + x)/x
my19b = Interval.open(0, oo)
```

**Marks.** M1 for interchanging, M1 for completing the square (or the
quadratic formula), A1 for $(y-1)^2-4$, A1 for
$(y-1)^2 = \frac1x + 4$, A1 for the $\pm$ line, R1 for rejecting the
negative branch using $x>3$; then A1 for the domain.

**The R1 is a whole mark for one sentence.** Not "take the positive
root" — *why*: because $g$ was defined only for $x>3$, so $g^{-1}$ can
only produce values greater than 3.

**Why $\sqrt{\frac{4x+1}{x}} = \frac{\sqrt{4x^2+x}}{x}$.** Multiply
inside by $\frac{x}{x}$: $\sqrt{\frac{4x^2+x}{x^2}} =
\frac{\sqrt{4x^2+x}}{|x|}$, and $|x|=x$ because the domain is $x>0$.
On a domain containing negative numbers this step would be false.

**A note on the archive.** The corpus records the answer as
$\frac{1+\sqrt{x^2+4x}}{x}$ — the bar and the root read one character
too far. Test it: $g(4) = \frac15$, so $g^{-1}\!\left(\frac15\right)$
must be 4. The paper's formula gives 4; the corpus's gives about 9.58.
The check in the cell above rejects the corpus form on its own, without
being told what the right answer is — which is the whole reason an
inverse is verified by undoing rather than by comparison.
""")

md(r"""
## Solution 20 — an inverse through arcsin

Interchange, then apply $\sin$ to both sides:

$$x = \arcsin\frac{y^2-1}{y^2+1} \Rightarrow
\sin x = \frac{y^2-1}{y^2+1}
\Rightarrow \sin x\left(y^2+1\right) = y^2-1 .$$

Collect the $y^2$ terms:

$$y^2\left(\sin x - 1\right) = -1-\sin x \Rightarrow
y^2 = \frac{1+\sin x}{1-\sin x} .$$

The domain of $g$ is $x\ge0$, so the values of $g^{-1}$ are
non-negative, and the positive root is taken:

$$g^{-1}(x) = \sqrt{\frac{1+\sin x}{1-\sin x}} .$$

For the domain, find the range of $g$: at $x=0$ the fraction is $-1$, so
$g(0) = -\frac\pi2$, attained; as $x\to\infty$ the fraction tends to 1
from below, so $g \to \frac\pi2$ without reaching it. Hence

$$\text{domain}\left(g^{-1}\right) = -\frac\pi2 \le x < \frac\pi2 .$$

```python
my20a = sqrt((1 + sin(x))/(1 - sin(x)))
my20b = Interval.Ropen(-pi/2, pi/2)
```

**Marks.** M1 for $x = \arcsin\frac{y^2-1}{y^2+1}$, A1 for applying
$\sin$ and clearing, A1 for $y^2 = \frac{1+\sin x}{1-\sin x}$, R1 for
taking the positive root with a reason, A1 for the expression; then A1
for the domain. Interval notations $[-\frac\pi2,\frac\pi2)$ and
$[-1.57, 1.57)$ are accepted.

**The excluded endpoint is visible in the formula.** At $x=\frac\pi2$
the denominator $1-\sin x$ is zero. The domain and the algebra agree,
which is a good sign that both are right.

**Why $f$ had to be cut down to $g$.** The $f$ of task 8 is even, so it
is two-to-one and has no inverse; restricting to $x\ge0$ throws away the
mirror half. That restriction is what makes the positive root the right
one — parity and branch choice are the same fact seen from two sides.

**A note on the archive.** The corpus records the function upside down,
as $\arcsin\frac{1-x^2}{1+x^2}$. With that version the horizontal
asymptote would be $y=-\frac\pi2$ and $f$ would be increasing for
$x<0$ — both contradicting what the paper prints in the parts before
this one. The markscheme settles it a third time: it gives
$y^2 = \frac{1+\sin x}{1-\sin x}$, which is what the paper's version
produces and the corpus's version does not.
""")

md(r"""
## Solution 21 — the timed task

**(b)(iii) $m=1$.** The closed form is useless here — it reads
$\frac{0}{0}$. Go back to the sum it came from:

$$f^{n}(x) = 1^{n}x + c\left(1+1+\cdots+1\right) = x + nc .$$

Or directly: $f(x)=x+c$, so $f^2(x) = x+2c$, and each composition adds
another $c$.

**(d) $-1<m<1$.** Then $m^{n}\to0$, so

$$f^{n}(x) = m^{n}x + c\,\frac{1-m^{n}}{1-m}
\ \longrightarrow\ 0 + \frac{c}{1-m}.$$

The limit does not depend on $x$: every point of every graph is pulled
to the same height, so the family approaches the horizontal line

$$L: \quad y = \frac{c}{1-m}.$$

**(e)(i) $m=-1$, $n$ odd.**

$$f^{n}(x) = (-1)^{n}x + c\,\frac{1-(-1)^{n}}{1-(-1)}
= (-1)^{n}x + c\,\frac{1-(-1)^{n}}{2}.$$

For odd $n$, $(-1)^n = -1$, so $f^{n}(x) = -x + c\cdot\frac{2}{2}
= -x+c$, as required.

**(e)(ii) $n$ even.** Then $(-1)^n = 1$, so
$f^{n}(x) = x + c\cdot\frac{0}{2} = x$.

```python
my21a = x + n*c
my21b = c/(1 - m)
my21c = -x + c
my21d = x
```

**Marks.** (b)(iii): M1 for substituting $m=1$ into their $f^n$, A1 for
$x + c(1+1+\cdots+1)$, A1 for $x+nc$ — or the same three by iterating
$f(x)=x+c$ directly. (d): M1 for $m^n\to0$, A1A1 for the limit, A1 for
writing it as the equation of a line. (e)(i): A1 for the substituted
form, R1 for $(-1)^n=-1$ when $n$ is odd — then AG. (e)(ii): M1 for
evidence that an even $n$ was considered, A1 for $f^n(x)=x$.

**$L$ is the fixed point.** Solving $f(x)=x$ gives $mx+c=x$, that is
$x = \frac{c}{1-m}$ — the same number. Iterating a contraction pulls
every starting point to the fixed point, which is what the picture of
flattening graphs is showing.

**Answer with an equation, not a number.** Part (d) asks for the
equation of $L$. "$\frac{c}{1-m}$" alone is not a line;
"$y = \frac{c}{1-m}$" is, and the last A1 is for exactly that.

**And here the practicum closes its loop.** For $m=-1$ and even $n$,
$f^n$ is the identity — in particular $f\circ f = \text{id}$, which is
the definition of $f = f^{-1}$. Check it directly: $f(x) = -x+c$ and

$$f(f(x)) = -(-x+c)+c = x .$$

So $y=-x+c$ is a self-inverse function, and it must be symmetric in the
line $y=x$ — which it is, being perpendicular to it. Task 13 found
another self-inverse function by algebra; the two questions are the same
question, one asked in Paper 1 and one inside a Paper 3 investigation.

**On the clock.** Eleven marks in about seventeen minutes, and the
substitutions are short. The time goes into (d): reading "the family of
graphs approaches a straight line" as "take the limit of $f^n(x)$ and
notice that $x$ disappears" is the step being tested, and it is worth
sitting still for thirty seconds before writing.

**What was left out.** Part (c) of this investigation proves the
formula for $f^n$ by induction, for eight marks — that belongs to A7,
and part (d) is a limit, which is why it sits slightly outside this
practicum's ladder.
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
                   'practicum-b2-composition-inverse.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
