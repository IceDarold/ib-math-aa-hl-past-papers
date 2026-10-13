"""Собирает практикум A3 (биномиальная теорема) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig, _series_canon

I, P = sp.I, sp.pi
sq = sp.sqrt
R = sp.Rational
x, n, r, p, q, h, a, b, z = sp.symbols('x n r p q h a b z')
th = sp.Symbol('theta', real=True)


def ds(expr, var=x):
    return digest(_series_canon(expr, var))


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(v)) for v in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_a3.py ---
D_E1 = ds(1 + 4 * x + 6 * x**2 + 4 * x**3 + x**4)
D_B2 = dn(21)
D_K3 = dset([sq(3), -sq(3)])
D_N4 = dn(7)
D_POW5 = ds(3 * n - 4 * r, var=n)
D_N5 = dset([4, 8, 12])
D_N6 = dn(8)
D_K6 = de(R(3, 2))
D_A7 = de(R(1, 2))
D_B7 = de(sp.Integer(2))
D_X8 = dset([1, 5])
D_H9 = dn(R(7, 5))
D_E10 = ds(1 + R(5, 2) * x - R(25, 8) * x**2 + R(125, 16) * x**3)
D_E11A = ds(1 - x**2 + x**4 - x**6)
D_E11B = ds(1 + x**2 / 2 + 3 * x**4 / 8)
D_A12 = de(R(-1, 3))
D_B12 = de(R(1, 6))
D_R12 = dn(1)
D_E13 = ds(1 + (p - q) * x + (q**2 - p * q) * x**2)
D_RE14 = ds(sp.cos(th)**5 - 10 * sp.cos(th)**3 * sp.sin(th)**2
            + 5 * sp.cos(th) * sp.sin(th)**4, var=th)
D_IM14 = ds(5 * sp.cos(th)**4 * sp.sin(th) - 10 * sp.cos(th)**2 * sp.sin(th)**3
            + sp.sin(th)**5, var=th)
D_E15 = ds(2 + 12 * z**2 + 2 * z**4, var=z)
D_Z15 = dset([-3 + 2 * sq(2), -3 - 2 * sq(2)])
D_Q16 = de(R(5, 4))
D_P16 = de(R(15, 4))
D_X16 = de(R(1, 25))
D_V16 = de(R(23, 21))
D_Y16 = de(R(1, 20))

TRIGGER = {1: 'term', 2: 'frac', 3: 'expand', 4: 'equate', 5: 'complex',
           6: 'term', 7: 'seq', 8: 'frac', 9: 'approx', 10: 'expand',
           11: 'equate', 12: 'term', 13: 'seq', 14: 'complex', 15: 'frac'}
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
# Practicum A3: the binomial theorem

The most mechanical topic of the archive and one of the most profitable: **109 marks
for seven techniques**, six of which come down to one formula for the general term.
Paper 1 — 77 marks, Paper 2 — 32, the calculator share 29%.

**Material.** 24 blocks and 109 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**The main idea of the topic.** The brackets almost never have to be expanded. The
question is always about **one** term of the expansion, and it is found at once, with
the formula for the general term, rather than by writing out every term. A student
who expands $(ax+1/x^2)^9$ in full is not making a mistake — they simply run out of
time.

**How to work**

1. Read the map of techniques. Techniques 1–4 are about positive integer powers,
   5–6 about fractional and negative ones, 7 is the join with complex numbers.
2. Work **on paper**. The general term is written once and carefully; all the rest
   of the work is arithmetic with powers.
3. Enter the answer in whichever form suits you. Expansions are compared **by
   value**, not by writing: `5*x/2` and `2.5*x` count the same, and the order of the
   terms does not matter.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + binomial, factorial, sqrt, I and the rest

language('en')                 # this notebook is in English, and so are the checks

n, r, p, q, h = symbols('n r p q h')
a, b = symbols('a b')
z = Symbol('z')
th = Symbol('theta', real=True)

print('ready; sympy', sp.__version__)
print('the binomial coefficient is binomial:', binomial(7, 2),
      '  and you can expand like this:', expand((1 + x)**4))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Expand in full | «expand and simplify», $n \le 5$ | Pascal's triangle |
| 2 | The general term | «the coefficient of $x^k$», «the constant term» | write $T_{r+1}$ |
| 3 | Equate coefficients | the expansion is given, the letters are unknown | two equations in two letters |
| 4 | Coefficients as a sequence | «arithmetic mean», «geometric sequence» | express three coefficients |
| 5 | A fractional or negative exponent | $(1+x)^{1/2}$, $(1-x)^{-1}$, $\frac{1}{\sqrt{\cdot}}$ | the general formula, the series is infinite |
| 6 | A product of series and an approximation | «up to $x^2$», «use to approximate» | multiply out and cut |
| 7 | The binomial and complex numbers | $(\cos\theta + i\sin\theta)^n$, $(1+z)^4$ | expand and split the parts |

The ladder rests on technique 2. The formula for the general term

$$T_{r+1} = \binom{n}{r}\,a^{\,n-r} b^{\,r}$$

is the topic: technique 1 is its special case, when there are few terms and writing
them all out is simpler; technique 3 applies it twice and compares; technique 4
applies it three times and looks at the relation; technique 5 continues it to
non-integer $n$; technique 6 multiplies two such series; technique 7 substitutes $i$
into it.

**What saves the most time.** The question is almost always about one term. What is
hunted for is not the expansion but the **index** $r$: equate the power of $x$ in the
general term to the one wanted, find $r$, substitute back. Three lines instead of
nine terms.
""")

md(r"""
---
## Theory 1. The formula and the triangle

For a positive integer $n$

$$(a+b)^n = \sum_{r=0}^{n} \binom{n}{r} a^{\,n-r} b^{\,r}
= a^n + \binom{n}{1}a^{n-1}b + \binom{n}{2}a^{n-2}b^2 + \dots + b^n,$$

where $\displaystyle\binom{n}{r} = \frac{n!}{r!\,(n-r)!}$.

Two properties that save time:

**Symmetry.** $\binom{n}{r} = \binom{n}{n-r}$. There is no point computing
$\binom{9}{7}$ — it is $\binom{9}{2} = 36$. In the exam the same thing means that
the term wanted can be hunted from either end: in the expansion of a tenth power the
indices $r = 2$ and $r = 8$ give the same binomial coefficient, and the one nearer
the edge is easier to compute.

**Pascal's triangle.** Each row comes from adding the neighbours in the previous
one:

```
n=0                1
n=1              1   1
n=2            1   2   1
n=3          1   3   3   1
n=4        1   4   6   4   1
n=5      1   5  10  10   5   1
n=6    1   6  15  20  15   6   1
n=7  1   7  21  35  35  21   7   1
```

Up to $n = 7$ a row is quicker to write out than factorials are to compute, and on
Paper 1 that is a legitimate method: the markscheme accepts «lists terms from row 7
of Pascal's triangle» directly. Above $n = 7$ — the formula.

**Where a mark is lost.** In $(a+b)^n$ the letter $a$ may turn out to be anything.
In $(5+x^3)^6$ the first term is 5, and its power $5^{\,6-r}$ does not go anywhere;
in $(x-3)^7$ the second term is negative, and the sign $(-1)^r$ has to appear in the
answer.
""")

md(r"""
## Task 1 🟢 — expand it all the way

Expand and simplify $(1+x)^4$.

*Source: May 2025 TZ1, Paper 1, Q2(b) (2 marks, no calculator).*
""")

code(r"""
my1 = ...                # the polynomial; the order of the terms does not matter

check_series('Task 1', my1, '""" + D_E1 + r"""')
""")

md(r"""
## Task 2 🟢 — one coefficient

In the expansion of $(x+1)^7$ the coefficient of $x^5$ is $b$. Show that $b = 21$.

Writing out the Pascal row or computing $\binom{7}{2}$ — both routes earn the
mark.

*Source: May 2022 TZ2, Paper 1, Q5(a) (2 marks, no calculator).*
""")

code(r"""
my2 = ...                # the value of b

check_num('Task 2', my2, 6, '""" + D_B2 + r"""')
""")

md(r"""
---
## Theory 2. The general term: do not expand, hunt the index

The key technique of the topic, 27 marks of the archive directly and another 50
inside the other techniques. The term of the expansion of $(a+b)^n$ with index $r+1$
is

$$T_{r+1} = \binom{n}{r}\,a^{\,n-r} b^{\,r}, \qquad r = 0, 1, \dots, n.$$

The order of work is always the same:

1. Write the general term, putting whatever is in the bracket in place of $a$ and
   $b$.
2. Collect all the powers of $x$ into one: the exponent turns out to be a **linear
   function of $r$**.
3. Equate that exponent to the one wanted and find $r$.
4. Substitute $r$ back and compute the coefficient.

An example on $\left(2x^2 + \dfrac{3}{x}\right)^n$. The general term:

$$\binom{n}{r}\left(2x^2\right)^{n-r}\left(\frac{3}{x}\right)^{r}
= \binom{n}{r}\,2^{\,n-r}3^{\,r}\, x^{2(n-r)} x^{-r}
= \binom{n}{r}\,2^{\,n-r}3^{\,r}\, x^{\,2n-3r}.$$

The exponent $2n - 3r$ is the whole substance of the question. Need the constant
term? Then $2n - 3r = 0$. Need $x^4$? Then $2n - 3r = 4$. The numerical factors from
the brackets do not go anywhere meanwhile: they sit in the coefficient but do not
affect the exponent, and confusing those two roles is the most expensive mistake in
the technique.

**Three places where marks are lost.**

*The numbering.* The term has index $r+1$, not $r$. «The third term» is $r = 2$.
Confusing them costs a mark and usually the whole question.

*A term versus a coefficient.* «The coefficient of $x^5$» is the number in front of
$x^5$, without the $x^5$ itself. «The term in $x^5$» has the power with it. Read
what is asked.

*A fractional $r$.* If the equation gives $r = 5/3$, there **is** no term with such
a power, and that is often the answer («it does not exist» or «only for such $n$»).
$r$ must not be rounded.
""")

md(r"""
## Task 3 🟢 — find the letter in the bracket

In the expansion of $(x + k)^7$ the coefficient of $x^5$ is 63. Find all the
possible values of $k$.

*Source: May 2021 TZ2, Paper 1, Q3 (5 marks, no calculator).*
""")

code(r"""
my3 = [...]              # all the values of k

check_set('Task 3', my3, '""" + D_K3 + r"""')
""")

md(r"""
## Task 4 🟡 — find the exponent

In the expansion of $\left(3 + x^2\right)^{n+1}$ the coefficient of $x^4$ is 20412.
Find $n$.

Here the first term of the bracket is the number 3, and its power enters the
coefficient. The final equation is solved by trial or on the calculator: this is
Paper 2.

*Source: May 2021 TZ1, Paper 2, Q5 (5 marks, calculator).*
""")

code(r"""
my4 = ...                # the value of n

check_num('Task 4', my4, 6, '""" + D_N4 + r"""')

# the calculator is in place here: look at how the left-hand side grows
for i in range(4, 10):
    print(f'n = {i}:  C(n+1,2)*3^(n-1) =', binomial(i + 1, 2) * 3**(i - 1))
""")

md(r"""
## Task 5 🟡 — when a constant term exists at all

Find all the positive integers $n$ for which the expansion of
$\left(x^3 - \dfrac{1}{8x}\right)^n$ has a constant term.

First enter the power of $x$ in the general term — an expression in $n$ and $r$.
Then the three smallest values of $n$ that work.

*Source: May 2022 TZ1, Paper 1, Q6 (5 marks, no calculator).*
""")

code(r"""
my5_pow = ...            # the power of x in the general term, in terms of n and r
my5_n = [...]            # the three smallest positive n

check_series('Task 5, the exponent', my5_pow, '""" + D_POW5 + r"""', var=n)
check_set('Task 5, the values of n', my5_n, '""" + D_N5 + r"""')
""")

md(r"""
---
## Theory 3. Equating coefficients

If the expansion is already written in the question and there are letters in the
bracket, the work goes the other way round: the coefficients computed with the
formula are equated to the given ones and the system is solved.

The scheme on $(1+cx)^n$:

$$(1+cx)^n = 1 + \binom{n}{1}cx + \binom{n}{2}c^2x^2 + \dots
= 1 + ncx + \frac{n(n-1)}{2}c^2x^2 + \dots$$

Given $1 + 20x + 45c^2x^2$. Equate:

$$nc = 20, \qquad \frac{n(n-1)}{2}c^2 = 45c^2.$$

The second equation **cancels by $c^2$** — and that is the main move of the
question: what is left is $n(n-1) = 90$, a clean equation in one unknown.

**Selecting the roots.** $n^2 - n - 90 = 0$ gives $n = 10$ and $n = -9$. The second
root is discarded because the question says $n \in \mathbb{Z}^+$. There is a mark
for the selection, and «forgot to look at the question» is the most frequent way of
losing it in the whole topic.

**Symmetry against extra work.** If the same $x^k$ is hunted in two expansions of
different degrees, the indices $r$ in them are different, but
$\binom{n}{r} = \binom{n}{n-r}$ lets you compute from the end where the binomial
coefficient is smaller.
""")

md(r"""
## Task 6 🟡 — two coefficients, two letters

The expansion of $(1+kx)^n$ begins like this:

$$(1+kx)^n = 1 + 12x + 28k^2x^2 + \dots,$$

where $n \in \mathbb{Z}^+$ and $k \in \mathbb{R}$. Find $n$ and $k$.

*Source: November 2023 TZ1, Paper 1, Q5 (6 marks, no calculator). The same question
is repeated word for word in TZ2 of the same session.*
""")

code(r"""
my6_n = ...              # the value of n
my6_k = ...              # the value of k

check_num('Task 6, n', my6_n, 6, '""" + D_N6 + r"""')
check_expr('Task 6, k', my6_k, '""" + D_K6 + r"""')
""")

md(r"""
## Task 7 🔴 — a system out of two expansions

The numbers $a$ and $b$ are positive. In the expansion of $\left(ax^3+b\right)^8$
the coefficient of $x^6$ is 448, and in the expansion of $\left(ax^3+b\right)^{10}$
the coefficient of $x^6$ is 2880. Find $a$ and $b$.

Note which factor enters squared and which to a high power: $x^6$ means that $ax^3$
has been taken **twice**.

*Source: May 2023 TZ1, Paper 2, Q5 (7 marks, calculator).*
""")

code(r"""
my7_a = ...
my7_b = ...

check_expr('Task 7, a', my7_a, '""" + D_A7 + r"""')
check_expr('Task 7, b', my7_b, '""" + D_B7 + r"""')
""")

md(r"""
---
## Theory 4. Coefficients as a sequence

A small but regular kind: three coefficients of the expansion are tied by a
condition from another topic — an arithmetic mean, a geometric sequence. The work
splits in two, and both halves are easy:

1. Write the three coefficients wanted with the formula for the general term.
2. Write the condition tying them and solve the resulting equation.

The conditions that turn up:

| Wording | Equation |
| --- | --- |
| the third term is the arithmetic mean of the second and the fourth | $2T_3 = T_2 + T_4$ |
| the three coefficients form a geometric sequence | $\dfrac{T_3}{T_2} = \dfrac{T_4}{T_3}$ |

**The trap that costs the last mark.** The equations here come from dividing by $x$
or by $h$, and the root $0$ turns up almost every time. It is extraneous: at $x = 0$
the expansion degenerates, at $h = 0$ there is no sequence. The markscheme says so
in plain words — «award final A0 for obtaining $x = 0$». Look at the question: it
almost certainly says $x \ne 0$ or $h > 0$.
""")

md(r"""
## Task 8 🟡 — the arithmetic mean

In the expansion of $(x+1)^7$, written in descending powers of $x$, the third term
is the arithmetic mean of the second and the fourth. Find all the possible values of
$x$, given that $x \ne 0$.

You have already found the coefficient of $x^5$ in task 2. The neighbouring ones
will be needed as well.

*Source: May 2022 TZ2, Paper 1, Q5(b) (5 marks, no calculator).*
""")

code(r"""
my8 = [...]              # all the values of x that work

check_set('Task 8', my8, '""" + D_X8 + r"""')
""")

md(r"""
## Task 9 🟡 — a geometric sequence

In the expansion of $(x+h)^8$ in descending powers of $x$ the coefficients of $x^7$,
$x^6$ and $x^4$ are $a$, $b$ and $d$ respectively. Given that $a$, $b$, $d$ form a
geometric sequence and $h > 0$, find $h$.

Note the gap: $x^7$, $x^6$ and $x^4$ are taken, not three in a row.

*Source: May 2023 TZ2, Paper 2, Q4 (7 marks, calculator).*
""")

code(r"""
my9 = ...                # the value of h

check_num('Task 9', my9, 6, '""" + D_H9 + r"""')
""")

md(r"""
---
## Theory 5. A fractional or negative exponent

The second half of the topic. The formula continues to any real $m$, but it looks
different — there are no factorials any more, because $\left(\frac12\right)!$ does
not exist:

$$(1+x)^m = 1 + mx + \frac{m(m-1)}{2!}x^2 + \frac{m(m-1)(m-2)}{3!}x^3 + \dots$$

The numerator is the product of $m$, $m-1$, $m-2$, …, the denominator the factorial
of the index. For a positive integer $m$ the product sooner or later hits zero and
the series stops; for a fractional or negative $m$ it is **infinite**, and the
answer carries as many terms as are asked for.

**Two compulsory conditions.**

*The form $(1+\dots)^m$.* The formula works only when the first term is a one. An
expression $\dfrac{1}{2-qx}$ is first brought to the needed form:

$$\frac{1}{2-qx} = \frac{1}{2}\left(1 - \frac{q}{2}x\right)^{-1}.$$

Forgetting to take the two out means losing the whole expansion.

*The interval of convergence.* The series makes sense only for $|x| < 1$. If the
bracket has $ax$ in it, the condition becomes $|ax| < 1$, that is,

$$|x| < \frac{1}{|a|}.$$

That is a mark of its own, and it costs one line. In November 2021 a whole A1 stood
for the answer «$|x| < 1$» — for one line that half the candidates do not write.

**How to compute without mistakes.** The coefficients are taken one at a time,
without trying to collapse a general formula. For $(1+3x)^{1/3}$:

$$1,\qquad \tfrac13(3x),\qquad \frac{\frac13\left(-\frac23\right)}{2}(3x)^2,
\qquad \frac{\frac13\left(-\frac23\right)\left(-\frac53\right)}{6}(3x)^3,$$

that is, $1 + x - x^2 + \frac53x^3 - \dots$ The bracket $(3x)$ is raised to the
power as a whole — forgetting to raise the three is the most frequent mistake in the
technique, and it shows at once: the coefficients come out suspiciously small.
""")

md(r"""
## Task 10 🟢 — a fractional exponent

Find the first four terms of the expansion of $(1+5x)^{1/2}$ in ascending powers of
$x$.

*Source: May 2025 TZ2, Paper 1, Q11(a) (4 marks, no calculator).*
""")

code(r"""
my10 = ...               # four terms, as a polynomial

check_series('Task 10', my10, '""" + D_E10 + r"""')
""")

md(r"""
## Task 11 🟢 — a negative exponent, twice

**(a)** Show that the first four terms of the expansion of $\left(1+x^2\right)^{-1}$
are $1 - x^2 + x^4 - x^6$.

**(b)** Expand $\dfrac{1}{\sqrt{1-x^2}}$ up to and including the term in $x^4$.

In both cases the role of the «$x$» of the formula is played by $x^2$ — substitute
it whole, together with its sign.

*Source: November 2025 TZ1, Paper 1, Q10(a)(i) and Q10(b)(i) (3 and 4 marks, no
calculator).*
""")

code(r"""
my11a = ...              # the expansion of (1 + x^2)^(-1) up to x^6
my11b = ...              # the expansion of 1/sqrt(1 - x^2) up to x^4

check_series('Task 11 (a)', my11a, '""" + D_E11A + r"""')
check_series('Task 11 (b)', my11b, '""" + D_E11B + r"""')
""")

md(r"""
## Task 12 🔴 — a difference of two series

Given that for $a \ne 0$

$$(1+ax)^{-1/2} - (1-x)^{1/2} = 4bx + bx^2 + \dots$$

**(a)** Find $a$ and $b$.

**(b)** For which $x$ does the expansion make sense?

Expand each bracket up to $x^2$, subtract and equate the coefficients. The system is
solved by substitution and has **two** solutions — for the third time in a row in
this practicum one of them is cut off by the wording of the question rather than by
algebra.

*Source: November 2021, Paper 1, Q9 (6 + 1 marks, no calculator).*
""")

code(r"""
my12_a = ...
my12_b = ...
my12_r = ...             # the bound: the expansion holds for |x| < ...

check_expr('Task 12, a', my12_a, '""" + D_A12 + r"""')
check_expr('Task 12, b', my12_b, '""" + D_B12 + r"""')
check_num('Task 12, the bound', my12_r, 6, '""" + D_R12 + r"""')
""")

md(r"""
---
## Theory 6. A product of series and an approximation

**Multiply out and cut.** If the expansion of a product is asked for up to $x^2$,
each bracket is expanded up to $x^2$, they are multiplied and **everything above
$x^2$ is thrown away**. Computing terms that will go anyway is wasted time:

$$(1-2x)\left(1 + \tfrac12 x - \tfrac18 x^2\right)
= 1 - \tfrac32 x - \tfrac98 x^2 + \underbrace{\dots}_{\text{into the bin}}$$

— here the second bracket is the expansion of $\sqrt{1+x}$, and everything above
$x^2$ was thrown away before the multiplication.

A useful check: the degree of the result is no higher than required, and there are
exactly as many terms as were asked for.

**An approximation by a number.** An expansion is a polynomial; a number can be put
into it and an approximation of the original expression obtained. The order:

1. Equate the expression under the root to the number wanted and find $x$.
2. Put that $x$ into the expansion.
3. Check that $x$ lies in the interval of convergence.

An example: to approximate $\sqrt[3]{1.06}$ through $(1+3x)^{1/3}$, solve
$1+3x = 1.06$, hence $x = 0.02$.

**Where the accuracy comes from.** The tail that was thrown away is the smaller the
smaller $|x|$ is: the next term is proportional to the next power of $x$, and at
$x = 0.02$ it is many times smaller than at twice that $x$. Hence the standard
question «why is this approximation worse» and the standard answer: **the $x$ being
substituted is larger**.

The extreme case is worth distinguishing. If the $x$ found falls outside
$|x| < \frac{1}{|a|}$, the approximation is not «less accurate» — it makes no sense
at all, the series diverges.
""")

md(r"""
## Task 13 🟡 — a product of two series

Find the expansion of $\dfrac{1+px}{1+qx}$ in ascending powers of $x$ up to and
including the term in $x^2$.

The denominator is $(1+qx)^{-1}$. Call the letters in the answer `p` and `q`.

*Source: May 2025 TZ2, Paper 1, Q11(b) (3 marks, no calculator).*
""")

code(r"""
my13 = ...               # the expansion up to x^2, in terms of p and q

check_series('Task 13', my13, '""" + D_E13 + r"""')
""")

md(r"""
---
## Theory 7. The binomial and complex numbers

The join with A5 and A6. If $i$ is put into the binomial, the expansion splits into
a real and an imaginary part, and that gives trigonometric identities.

$$(\cos\theta + i\sin\theta)^n
= \sum_{r=0}^{n}\binom{n}{r}\cos^{\,n-r}\theta\;\left(i\sin\theta\right)^{r}.$$

The powers of $i$ go round with period 4:

$$i^0=1,\quad i^1=i,\quad i^2=-1,\quad i^3=-i,\quad i^4=1,\;\dots$$

So the even $r$ give the real part with signs $+,-,+,-$ and the odd ones the
imaginary part with the same signs. Collecting them separately gives $a+bi$.

**What it is for.** By de Moivre's theorem the same thing equals
$\cos n\theta + i\sin n\theta$. Equating the parts gives the multiple-angle
formulas — the very technique by which $\sin 5\theta$ is proved in A6. Here the
first half of the work is done; the second lives there.

**The second storyline** is a substitution of the form $z = i\tan\theta$. Then
$z^2 = -\tan^2\theta$, and an equation left with only even powers of $z$ turns into
an equation in $\tan^2\theta$. That is how exact values of tangents of angles not in
the table are mined; which angle comes out is decided by the degree of the binomial
in the question.
""")

md(r"""
## Task 14 🔴 — expand with the imaginary unit

Expand $(\cos\theta + i\sin\theta)^5$ with the binomial theorem and write the result
in the form $a + bi$, where $a$ and $b$ are expressed in terms of $\sin\theta$ and
$\cos\theta$.

Call the variable `th` — it is set up in the setup cell.

*Source: November 2023 TZ1, Paper 1, Q12(a) (4 marks, no calculator). The same
question is repeated in TZ2 of the same session.*
""")

code(r"""
my14_a = ...             # the real part
my14_b = ...             # the imaginary part (without the factor i)

check_series('Task 14, Re', my14_a, '""" + D_RE14 + r"""', var=th)
check_series('Task 14, Im', my14_b, '""" + D_IM14 + r"""', var=th)
""")

md(r"""
## Task 15 🔴 — an exact value of a tangent

Let $z = i\tan\dfrac{\pi}{8}$. From the earlier parts of the question it is known
that for this $z$ we have $(1+z)^4 + (1-z)^4 = 0$.

**(a)** Expand $(1+z)^4 + (1-z)^4$ with the binomial theorem.

**(b)** Solve the resulting equation for $z^2$.

**(c)** Hence show that $\tan\dfrac{\pi}{8} = \sqrt{3-2\sqrt2}$.

While expanding, note that the odd powers cancel and only the even ones are left.
That is what makes the equation quadratic in $z^2$.

*Source: November 2025 TZ3, Paper 1, Q11(d) (7 marks, no calculator).*
""")

code(r"""
my15_e = ...             # (1+z)^4 + (1-z)^4 expanded
my15_z = [...]           # both values of z^2

check_series('Task 15, the expansion', my15_e, '""" + D_E15 + r"""', var=z)
check_set('Task 15, z^2', my15_z, '""" + D_Z15 + r"""')

# part (c) is checked numerically: both sides have to agree
print('tan(pi/8)       =', tan(pi/8).evalf(10))
print('sqrt(3-2*sqrt2) =', sqrt(3 - 2*sqrt(2)).evalf(10))
""")

md(r"""
---
## Where the calculator is in this topic

29% of the marks of the topic are Paper 2, and unlike in many topics of the archive
that is not a formality: the calculator does concrete work here, but only on the
last step.

**What it does.**

- *Solves the equation you have arrived at.* An equation of the form
  $\binom{m}{2}\,a^{\,m-2} = N$, in which the unknown sits both in the binomial
  coefficient and in the exponent, has no analytic solution at all: it is solved by
  trial or graphically, and the markscheme allows that directly. Task 4 leads to
  exactly such an equation.
- *Computes $\binom{n}{r}$.* The `nCr` function is on any GDC, and on Paper 2 there
  is no point computing factorials by hand.
- *Solves systems.* In task 7 the system in $a$ and $b$ can be solved graphically —
  the markscheme accepts «solve their system algebraically **or graphically**».

**What it does not do.** The general term. The power of $x$ in the general term and
the index $r$ are hand work on both papers, and that is exactly where all the M1s
are. The calculator joins in after the equation has been written.

**What it does not do at all.** Expansions with a fractional exponent — all 77 marks
of Paper 1, and half the topic. A GDC does not expand a series with a non-integer
power, and even if it did, an answer with no working earns no marks.
""")

code(r"""
# what the trial from task 4 looks like and why it is legitimate here
print('trial over n:')
for i in range(5, 9):
    print(f'  n = {i}: {binomial(i + 1, 2) * 3**(i - 1)}')

# and a check on an expansion: compare a piece of the series with the function
approximation = 1 + Rational(5, 2)*x - Rational(25, 8)*x**2 + Rational(125, 16)*x**3
for v in (0.01, 0.04, 0.1, 0.19):
    exact = float(sqrt(1 + 5*v))
    approx = float(approximation.subs(x, v))
    print(f'x = {v:<5} exact {exact:.6f}  approximately {approx:.6f}  '
          f'error {abs(exact - approx):.2e}')
""")

md(r"""
---
## Trainer: name the technique

The technique is chosen from one look at the question. For each one, name the
technique with a single code:

`expand` · `term` · `equate` · `seq` · `frac` · `approx` · `complex`

| # | Statement |
| --- | --- |
| 1 | Find the coefficient of $x^{12}$ in the expansion of $\left(2x^2 - \frac{1}{x}\right)^9$ |
| 2 | Expand $(1-3x)^{-2}$ up to and including the term in $x^3$ |
| 3 | Expand and simplify $(2+x)^5$ |
| 4 | In the expansion of $(1+cx)^m$ the first three terms are $1+20x+150x^2$. Find $c$ and $m$ |
| 5 | Expand $(\cos\theta+i\sin\theta)^4$ and hence show that $\cos 4\theta = 8\cos^4\theta-8\cos^2\theta+1$ |
| 6 | Find the term independent of $x$ in $\left(x^2+\frac{3}{x}\right)^{12}$ |
| 7 | The coefficients of $x^2$, $x^3$, $x^4$ in $(1+x)^n$ form an arithmetic sequence. Find $n$ |
| 8 | Find the first three terms of $\frac{1}{\sqrt{4+x}}$ in ascending powers of $x$ |
| 9 | Use your expansion with $x = 0.02$ to estimate $\sqrt[3]{1.06}$ |
| 10 | Write down the expansion of $(a+b)^3$ |
| 11 | In the expansion of $(1+ax)^n$ the coefficients of $x$ and $x^2$ are 15 and 90. Find $a$ and $n$ |
| 12 | Find the constant term in the expansion of $\left(3x - \frac{2}{x^2}\right)^{15}$ |
| 13 | The second, third and fifth coefficients of $(1+y)^n$ are in geometric progression |
| 14 | By expanding $(1+i)^{10}$, find its real part |
| 15 | State the values of $x$ for which the expansion of $(1+4x)^{-1/3}$ is valid |
""")

code(r"""
answers = {
    1: '',  2: '',  3: '',  4: '',  5: '',
    6: '',  7: '',  8: '',  9: '', 10: '',
   11: '', 12: '', 13: '', 14: '', 15: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## Task 16 🔴 — ON THE TIMER: 15 minutes

A continuation of tasks 10 and 13: the same two expansions, but now they are
compared and put to work. A whole exam format, 10 marks.

The expansions of $(1+5x)^{1/2}$ and $\dfrac{1+px}{1+qx}$ agree in their first three
terms.

**(c)** Show that $q = \dfrac54$, and find $p$.

**(d)** Using the approximation $\sqrt{1+5x} \approx \dfrac{1+px}{1+qx}$, find an
approximate value of $\sqrt{1.2}$ as a fraction. Then find the $x$ that would be
needed to approximate $\dfrac{\sqrt5}{2}$, and explain why that approximation would
be worse.

*Source: May 2025 TZ2, Paper 1, Q11(c) and Q11(d) (4 + 6 marks, no calculator).*
""")

code(r"""
# set a timer for 15 minutes

my16_q = ...             # the value of q
my16_p = ...             # the value of p
my16_x = ...             # the x for approximating sqrt(1.2)
my16_v = ...             # the approximation itself, as a fraction
my16_y = ...             # the x needed for sqrt(5)/2

check_expr('Task 16, q', my16_q, '""" + D_Q16 + r"""')
check_expr('Task 16, p', my16_p, '""" + D_P16 + r"""')
check_expr('Task 16, x for sqrt(1.2)', my16_x, '""" + D_X16 + r"""')
check_expr('Task 16, the approximation', my16_v, '""" + D_V16 + r"""')
check_expr('Task 16, x for sqrt(5)/2', my16_y, '""" + D_Y16 + r"""')
""")

md(r"""
### Attempt log

Fill it in after checking against the solution — one line per part.

| Part | In time | Technique named right | What cost a mark |
| --- | --- | --- | --- |
| (c) |  |  |  |
| (d) |  |  |  |

For this topic the log is worth a column **«how many terms of the expansion I wrote
that were not needed»**. The right answer is none: in a topic where everything is
done with the general term, extra terms are pure lost time.
""")

md(r"""
---
# 🔑 Solutions

What follows are the worked solutions. Read them after you have solved.
""")

md(r"""
## Solution 1 — expand it all the way

Row $n = 4$ of Pascal's triangle: 1, 4, 6, 4, 1. So

$$(1+x)^4 = 1 + 4x + 6x^2 + 4x^3 + x^4. \qquad \blacksquare$$

```python
my1 = 1 + 4*x + 6*x**2 + 4*x**3 + x**4
```

**The marking.** M1 for attempting to find the coefficients (a Pascal row, the
formula or multiplying out $(1+2x+x^2)^2$), A1 for the right answer.

**Three legitimate routes** — the markscheme accepts all of them: the row of the
triangle, substitution into the binomial formula, squaring $(1+x)^2$. At $n = 4$ the
triangle is the quickest.
""")

md(r"""
## Solution 2 — one coefficient

The term in $x^5$ in $(x+1)^7$ comes when the one is taken twice:

$$\binom{7}{2}x^5\cdot 1^2 = 21x^5,$$

so $b = 21$. $\blacksquare$

```python
my2 = 21
```

**The marking.** M1 for recognising the term wanted ($\binom72$ or $\binom75$), A1
for computing it correctly. The second route is to write out row 7 of Pascal's
triangle (1, 7, 21, 35, 35, 21, 7, 1) and read the 21 off directly; the markscheme
gives the same two marks for that.

**Why $\binom72$ and not $\binom75$.** Both are right:
$\binom72 = \binom75 = 21$. The two is easier to compute — two factors instead of
five.
""")

md(r"""
## Solution 3 — find the letter in the bracket

The general term of $(x+k)^7$:

$$T_{r+1} = \binom{7}{r}x^{\,7-r}k^{\,r}.$$

We want $x^5$, so $7-r = 5$, that is, $r = 2$:

$$\binom{7}{2}x^5k^2 = 21k^2x^5.$$

Equate the coefficient to 63:

$$21k^2 = 63 \;\Longrightarrow\; k^2 = 3 \;\Longrightarrow\; k = \pm\sqrt3. \qquad \blacksquare$$

```python
my3 = [sqrt(3), -sqrt(3)]
```

**The marking.** M1 for using the general term, A1 for the right term, A1 for
$\binom72 = 21$, A1 for $21k^2 = 63$, A1 for both values of $k$.

**Where marks are lost.** The last one: the markscheme writes «M1A1A1A1**A0** for
$k = 3$ only» — losing the negative root costs exactly one mark, but it always
costs it. The equation $k^2 = 3$ has two solutions, and there is nothing in the
question to cut the negative one off.
""")

md(r"""
## Solution 4 — find the exponent

The general term of $\left(3+x^2\right)^{n+1}$:

$$T_{r+1} = \binom{n+1}{r}\,3^{\,n+1-r}\left(x^2\right)^{r}
= \binom{n+1}{r}3^{\,n+1-r}x^{2r}.$$

We want $x^4$, so $2r = 4$, that is, $r = 2$. The coefficient:

$$\binom{n+1}{2}\cdot 3^{\,n-1} = \frac{n(n+1)}{2}\cdot 3^{\,n-1}.$$

Equate it to 20412:

$$\frac{n(n+1)}{2}\cdot 3^{\,n-1} = 20412.$$

Analytically that cannot be solved: $n$ sits both in the base and in the exponent.
Try values — the left-hand side grows fast:

| $n$ | value |
| --- | --- |
| 5 | 1215 |
| 6 | 5103 |
| **7** | **20412** |
| 8 | 78732 |

So $n = 7$. $\blacksquare$

```python
my4 = 7
```

**The marking.** M1 for the product of the binomial coefficient, the power of the
three and the power of $x^2$; A1 for the right term; M1 for equating to 20412;
A1A1 for the solution and $n = 7$.

**The second route.** Take the three out:
$(3+x^2)^{n+1} = 3^{n+1}\left(1+\frac{x^2}{3}\right)^{n+1}$. The same answer, but the
arithmetic is a little cleaner — the powers of three are not smeared across the
terms.

**About the calculator.** This is Paper 2, and trying values here is not an
admission of defeat but a method. The markscheme accepts both a table of values and
an intersection of graphs.
""")

md(r"""
## Solution 5 — when a constant term exists at all

The general term:

$$T_{r+1} = \binom{n}{r}\left(x^3\right)^{n-r}\left(-\frac{1}{8x}\right)^{r}
= \binom{n}{r}\left(-\frac18\right)^{r}x^{\,3(n-r)-r}
= \binom{n}{r}\left(-\frac18\right)^{r}x^{\,3n-4r}.$$

A constant term is $x^0$:

$$3n - 4r = 0 \;\Longrightarrow\; r = \frac{3n}{4}.$$

Now the main thing: $r$ has to be an **integer** and lie in $0 \le r \le n$. The
fraction $\frac{3n}{4}$ is an integer exactly when $n$ is a multiple of 4 (three is
not divisible by 4). So

$$n = 4, 8, 12, \dots \quad\text{that is,}\quad n = 4m,\; m \in \mathbb{Z}^+. \qquad \blacksquare$$

```python
my5_pow = 3*n - 4*r
my5_n = [4, 8, 12]
```

**The marking.** M1 for the general term, M1 for understanding that a constant term
is the zeroth power, A1 for $3n-4r=0$ or $r = 3n/4$, A1 for one correct $n$ or for
«$r$ is a multiple of 3», A1 for the general answer $n = 4m$.

**Checking the condition $r \le n$.** At $n = 4m$ we get $r = 3m$, and $3m \le 4m$
for every positive $m$ — any multiple of four will do, with no upper bound.

**Where marks are lost.** Stopping at $r = \frac{3n}{4}$ without drawing the
conclusion about integrality. That is exactly half the question: writing the
equation is easy, and realising that a fractional $r$ means no such term exists is
what is being tested.
""")

md(r"""
## Solution 6 — two coefficients, two letters

The expansion:

$$(1+kx)^n = 1 + \binom{n}{1}kx + \binom{n}{2}k^2x^2 + \dots
= 1 + nkx + \frac{n(n-1)}{2}k^2x^2 + \dots$$

Compare with the given $1 + 12x + 28k^2x^2$:

$$nk = 12, \qquad \frac{n(n-1)}{2}k^2 = 28k^2.$$

In the second equation the $k^2$ cancels — that is the main move:

$$\frac{n(n-1)}{2} = 28 \;\Longrightarrow\; n^2 - n - 56 = 0
\;\Longrightarrow\; (n-8)(n+7) = 0.$$

The question says $n \in \mathbb{Z}^+$, so $n = 8$, and then
$k = \frac{12}{8} = \frac32$. $\blacksquare$

```python
my6_n = 8
my6_k = Rational(3, 2)
```

**The marking.** M1 for applying the binomial theorem, A1 for $nk = 12$, A1 for
$\frac{n(n-1)}{2} = 28$, M1 for attempting the quadratic, A1 for $n = 8$, A1 for
$k = \frac32$.

**Why cancelling by $k^2$ is legitimate.** If $k$ were 0, the expansion would be
just 1 and the term $12x$ would not appear. So $k \ne 0$ and dividing is allowed.

**The second route.** $\binom{n}{2} = 28$ — that is the row of Pascal's triangle
whose third element is 28. Row $n = 8$: 1, 8, 28, 56, … The answer is read off with
no quadratic, and the markscheme accepts it.
""")

md(r"""
## Solution 7 — a system out of two expansions

The general term of $\left(ax^3+b\right)^m$:

$$T_{r+1} = \binom{m}{r}\left(ax^3\right)^{m-r}b^{\,r}
= \binom{m}{r}a^{\,m-r}b^{\,r}x^{\,3(m-r)}.$$

We want $x^6$, so $3(m-r) = 6$, that is, $m - r = 2$: the factor $ax^3$ is taken
**twice** and $b$ all the other times. The coefficient is
$\binom{m}{2}a^2b^{\,m-2}$.

For $m = 8$: $\;\binom82 a^2b^6 = 28a^2b^6 = 448 \;\Rightarrow\; a^2b^6 = 16$.

For $m = 10$: $\;\binom{10}{2}a^2b^8 = 45a^2b^8 = 2880 \;\Rightarrow\; a^2b^8 = 64$.

Divide the second by the first:

$$b^2 = 4 \;\Longrightarrow\; b = 2 \quad (b > 0),$$

and back: $a^2\cdot 64 = 16$, hence $a^2 = \frac14$ and $a = \frac12$. $\blacksquare$

```python
my7_a = Rational(1, 2)
my7_b = 2
```

**The marking.** M1 for the product of the binomial coefficient and the powers, A1
for the right term ($r = 2$ or $r = 6$ by symmetry), A1A1 for both equations, M1 for
attempting to solve the system, A1A1 for $a$ and $b$.

**What is easiest to mix up here.** Which letter is squared. The power of $x$ comes
only from $ax^3$, and since $x^6$ is wanted, that factor has been taken twice — so
$a^2$, not $a^6$. You can check yourself on the powers: $b$ should be left with the
power $m-2$, that is, 6 and 8, and dividing the equations should give exactly
$b^2$.

**About the division.** The technique is general and worth remembering: two power
systems are divided one by the other so that one of the letters cancels. Here $a^2$
goes at once and $b^2 = 4$ is left in one line.

**About the calculator.** Paper 2, and the markscheme allows the system to be solved
graphically. But dividing the equations is shorter than any graph.
""")

md(r"""
## Solution 8 — the arithmetic mean

The expansion of $(x+1)^7$ in descending powers begins

$$x^7 + 7x^6 + 21x^5 + 35x^4 + \dots$$

The second, third and fourth terms are $7x^6$, $21x^5$, $35x^4$. The condition:

$$21x^5 = \frac{7x^6 + 35x^4}{2}.$$

Multiply by 2 and divide by $7x^4$ (allowed, since $x \ne 0$):

$$42x^5 = 7x^6 + 35x^4 \;\Longrightarrow\; 6x = x^2 + 5
\;\Longrightarrow\; x^2 - 6x + 5 = 0.$$

Factorise: $(x-1)(x-5) = 0$, so $x = 1$ or $x = 5$. $\blacksquare$

```python
my8 = [1, 5]
```

**The marking.** A1 for $a = 7$, A1 for the right equation, A1 for the quadratic, M1
for attempting to solve it, A1 for both roots.

**The trap, named in the markscheme in plain words.** «Award final A0 for obtaining
$x = 0$, $x = 1$, $x = 5$». If you did not dare divide by $x^4$ and expanded
everything as $x^6 - 6x^5 + 5x^4 = 0$, the $x^4$ comes out as a factor and presents
you with the root $x = 0$. It is extraneous: the question says $x \ne 0$, and an
extra root in the answer costs a mark.

**How not to be caught.** Before solving, look at which $x$ makes the equation
degenerate and cross that value out straight away.
""")

md(r"""
## Solution 9 — a geometric sequence

The expansion of $(x+h)^8$ in descending powers of $x$:

$$x^8 + \binom81 hx^7 + \binom82 h^2x^6 + \binom83 h^3x^5 + \binom84 h^4x^4 + \dots$$

So

$$a = \binom81 h = 8h, \qquad b = \binom82 h^2 = 28h^2,
\qquad d = \binom84 h^4 = 70h^4.$$

Three numbers form a geometric sequence when the ratios of neighbours are equal:

$$\frac{b}{a} = \frac{d}{b} \;\Longrightarrow\;
\frac{28h^2}{8h} = \frac{70h^4}{28h^2}
\;\Longrightarrow\; \frac{7h}{2} = \frac{5h^2}{2}.$$

Hence $7h = 5h^2$, that is, $h(5h-7) = 0$ and $h = \frac75 = 1.4$ (the root $h = 0$
is discarded, since $h > 0$). $\blacksquare$

```python
my9 = Rational(7, 5)
```

**The marking.** M1 for using the expansion, A1A1A1 for $a$, $b$, $d$, M1 for
recognising the constant ratio, A1 for the right equation, A1 for $h = 1.4$.

**About the gap.** The coefficients of $x^7$, $x^6$ and $x^4$ are taken — not three
in a row. That is not a typo in the question: it is those three that form the
sequence, and $\binom83$ takes no part in it. Three marks out of seven stand simply
for taking the three right coefficients.

**About the root $h = 0$.** It appears the same way as in task 8 and is discarded
for the same reason: the question says $h > 0$. Two questions in a row with the same
trap is no coincidence — it is IB's favourite way of checking whether you read the
constraints.
""")

md(r"""
## Solution 10 — a fractional exponent

The general formula with $m = \frac12$ and «$x$» being $5x$:

$$(1+5x)^{1/2} = 1 + \tfrac12(5x)
+ \frac{\tfrac12\left(-\tfrac12\right)}{2!}(5x)^2
+ \frac{\tfrac12\left(-\tfrac12\right)\left(-\tfrac32\right)}{3!}(5x)^3 + \dots$$

Compute them one at a time:

$$\tfrac12\cdot 5x = \frac52 x, \qquad
\frac{-\tfrac14}{2}\cdot 25x^2 = -\frac{25}{8}x^2, \qquad
\frac{\tfrac38}{6}\cdot 125x^3 = \frac{125}{16}x^3.$$

So

$$(1+5x)^{1/2} = 1 + \frac52 x - \frac{25}{8}x^2 + \frac{125}{16}x^3 + \dots
\qquad \blacksquare$$

```python
my10 = 1 + Rational(5, 2)*x - Rational(25, 8)*x**2 + Rational(125, 16)*x**3
```

**The marking.** M1 for applying the formula with $m = \frac12$, A1 for the right
substitution in at least three terms, A1A1 for the right answer.

**The most frequent mistake in the technique.** Raising only the $x$ to the power
and forgetting the five: writing $-\frac18 x^2$ instead of $-\frac{25}{8}x^2$. It is
**the whole bracket** $5x$ that goes into the formula.

**A check on the spot.** Put $x = 0.01$ in: the exact value is
$\sqrt{1.05} = 1.024695$, and the expansion gives $1.024695$. Agreement to six
figures means the coefficients are right. That is a legitimate way of checking
yourself in ten seconds, and it works on both papers.
""")

md(r"""
## Solution 11 — a negative exponent, twice

**(a)** The formula with $m = -1$ and «$x$» being $x^2$:

$$\left(1+x^2\right)^{-1} = 1 + (-1)x^2
+ \frac{(-1)(-2)}{2!}\left(x^2\right)^2
+ \frac{(-1)(-2)(-3)}{3!}\left(x^2\right)^3 + \dots$$

$$= 1 - x^2 + x^4 - x^6 + \dots \qquad \blacksquare$$

This is a geometric sequence with ratio $-x^2$ — as it should be:
$\frac{1}{1-t} = 1+t+t^2+\dots$ at $t = -x^2$.

**(b)** Here $m = -\frac12$ and «$x$» is $-x^2$ (the minus goes inside the
bracket!):

$$\left(1-x^2\right)^{-1/2} = 1 + \left(-\tfrac12\right)\left(-x^2\right)
+ \frac{\left(-\tfrac12\right)\left(-\tfrac32\right)}{2!}\left(-x^2\right)^2 + \dots$$

$$= 1 + \frac12 x^2 + \frac38 x^4 + \dots \qquad \blacksquare$$

```python
my11a = 1 - x**2 + x**4 - x**6
my11b = 1 + x**2/2 + 3*x**4/8
```

**The marking.** (a) M1 for building the expansion to four terms with $m=-1$, A1 for
the third term, A1 for the fourth. (b) M1 for the expansion with $m=-\frac12$, (A1)
for the first two terms, (A1) for the third, A1 for the answer.

**About the signs.** In (b) every coefficient came out positive, although $m$ is
negative — because the minuses from $m(m-1)$ and from $\left(-x^2\right)^r$ cancel
each other at even $r$. Easy to check: $\frac{1}{\sqrt{1-x^2}}$ is greater than one
for any $x \ne 0$, so every correction has to be positive.

**About the form.** Part (b) looks like $\frac{1}{\sqrt{1-x^2}}$ in the question.
The first move is to rewrite it as $\left(1-x^2\right)^{-1/2}$; until the exponent is
outside, the formula does not apply.
""")

md(r"""
## Solution 12 — a difference of two series

**(a)** Expand each bracket up to $x^2$.

$$(1+ax)^{-1/2} = 1 - \frac{a}{2}x + \frac{3a^2}{8}x^2 + \dots$$

$$(1-x)^{1/2} = 1 - \frac12 x - \frac18 x^2 + \dots$$

Subtract — the ones cancel:

$$(1+ax)^{-1/2} - (1-x)^{1/2}
= \frac{1-a}{2}x + \frac{3a^2+1}{8}x^2 + \dots$$

Equate to $4bx + bx^2$:

$$\frac{1-a}{2} = 4b, \qquad \frac{3a^2+1}{8} = b.$$

From the first, $1-a = 8b$; from the second, $3a^2+1 = 8b$. So

$$1 - a = 3a^2 + 1 \;\Longrightarrow\; 3a^2 + a = 0
\;\Longrightarrow\; a(3a+1) = 0.$$

Both roots have to be treated honestly, because **both satisfy the system**.

At $a = 0$ we get $b = \frac18$, and that is not an extraneous root: the left-hand
side becomes $1 - (1-x)^{1/2} = \frac{x}{2} + \frac{x^2}{8} + \dots$, and the right
at $b = \frac18$ is $\frac{x}{2} + \frac{x^2}{8}$ — they agree identically. The
algebra does not cut that root off.

What cuts it off is the condition $a \ne 0$: at $a = 0$ the first bracket degenerates
into a one, and no expansion with exponent $-\frac12$ is left in the question. So

$$a = -\frac13, \qquad b = \frac{1-a}{8} = \frac{1}{6}. \qquad \blacksquare$$

**(b)** Both expansions require $|x| < 1$: for $(1-x)^{1/2}$ that is the condition
$|x|<1$ directly, and for $(1+ax)^{-1/2}$ with $a = -\frac13$ it is $|x| < 3$. The
intersection gives **$|x| < 1$**. $\blacksquare$

```python
my12_a = Rational(-1, 3)
my12_b = Rational(1, 6)
my12_r = 1
```

**The marking.** M1 for attempting an expansion with a negative fractional exponent,
A1 for the first expansion, A1 for the second, M1 for equating coefficients, M1 for
solving the system, A1 for the answer. Part (b) is an A1 of its own.

**About part (b).** One mark for one line — and it is skipped more often than any
other in the topic. The convergence condition has to be written whenever the
exponent is not an integer, even if nobody asked for it as a separate part: an
expansion without its domain is incomplete.

**How to compute the bound.** The general rule: $(1+cx)^m$ converges for $|cx|<1$,
that is, $|x| < \frac{1}{|c|}$. When there are several brackets, take the
**strictest** of the bounds. Here $(1-x)^{1/2}$ gives $|x|<1$ and
$\left(1-\frac{x}{3}\right)^{-1/2}$ gives $|x|<3$; the first wins.

**The same thought for the third time.** In tasks 8 and 9 the extra root was
discarded by the question ($x \ne 0$, $h > 0$), and here by the condition
$a \ne 0$. The difference is that there the root was extraneous (it came from a
division), while here it is genuine: it does satisfy the system. All the more reason
to read the constraints — the algebra will not make the choice for you.
""")

md(r"""
## Solution 13 — a product of two series

Expand the denominator as a power with exponent $-1$:

$$(1+qx)^{-1} = 1 - qx + q^2x^2 - \dots$$

Multiply by the numerator and keep only what is no higher than $x^2$:

$$(1+px)\left(1 - qx + q^2x^2\right)
= 1 - qx + q^2x^2 + px - pqx^2 + \underbrace{pq^2x^3}_{\text{thrown away}}$$

$$= 1 + (p-q)x + \left(q^2-pq\right)x^2 + \dots \qquad \blacksquare$$

```python
my13 = 1 + (p - q)*x + (q**2 - p*q)*x**2
```

**The marking.** A1 for three right terms of the expansion of $(1+qx)^{-1}$, M1 for
attempting to multiply, A1 for the answer.

**About economy.** There is no point expanding the denominator past $x^2$:
multiplying by $px$ raises the degree, and everything surplus goes anyway. The rule
is simple — if the answer is wanted up to $x^k$, each factor is expanded up to $x^k$
too, no further.

**A check on yourself.** The coefficient of $x^2$ can be written as $q(q-p)$ — the
same quantity, and the check will accept it: values are compared, not writings.
""")

md(r"""
## Solution 14 — expand with the imaginary unit

By the binomial theorem with $n = 5$:

$$(\cos\theta + i\sin\theta)^5 = \sum_{r=0}^{5}\binom{5}{r}
\cos^{\,5-r}\theta\;\left(i\sin\theta\right)^{r}.$$

The coefficients are row 5 of Pascal's triangle: 1, 5, 10, 10, 5, 1. The powers of
$i$: $1, i, -1, -i, 1, i$. Writing the six terms out:

$$\cos^5\theta
+ 5i\cos^4\theta\sin\theta
- 10\cos^3\theta\sin^2\theta
- 10i\cos^2\theta\sin^3\theta
+ 5\cos\theta\sin^4\theta
+ i\sin^5\theta.$$

Collect them separately:

$$a = \cos^5\theta - 10\cos^3\theta\sin^2\theta + 5\cos\theta\sin^4\theta,$$

$$b = 5\cos^4\theta\sin\theta - 10\cos^2\theta\sin^3\theta + \sin^5\theta.
\qquad \blacksquare$$

```python
my14_a = cos(th)**5 - 10*cos(th)**3*sin(th)**2 + 5*cos(th)*sin(th)**4
my14_b = 5*cos(th)**4*sin(th) - 10*cos(th)**2*sin(th)**3 + sin(th)**5
```

**The marking.** M1 for attempting the binomial expansion (one term with the product
of a binomial coefficient, a power of $i\sin\theta$ and a power of $\cos\theta$ is
enough), A1 for the right real part, A1 for the right imaginary part. Four marks in
all — and half of them for care with signs.

**A mnemonic for the signs.** Even $r$ go into the real part, odd ones into the
imaginary, and inside each the signs alternate $+,-,+$. You can check at
$\theta = 0$: then $a = 1$, $b = 0$, as they should be, since
$(\cos 0 + i\sin 0)^5 = 1$.

**What comes next.** By de Moivre the same quantity equals
$\cos5\theta + i\sin5\theta$. Equating the parts gives $\cos5\theta = a$ and
$\sin5\theta = b$ — the multiple-angle formulas. That second half of the work is
dealt with in A6, the technique «trigonometric identities via de Moivre».

**About the check.** The comparison goes by value, so it will also accept the answer
`cos(5*th)` — numerically that is the same thing. In the exam it must not be written
that way: the question asks for an expression in $\sin\theta$ and $\cos\theta$, and
$\cos5\theta$ is exactly what is being proved.
""")

md(r"""
## Solution 15 — an exact value of a tangent

**(a)** Expand both brackets with the binomial theorem:

$$(1+z)^4 = 1 + 4z + 6z^2 + 4z^3 + z^4,$$
$$(1-z)^4 = 1 - 4z + 6z^2 - 4z^3 + z^4.$$

On adding, the odd powers cancel:

$$(1+z)^4 + (1-z)^4 = 2 + 12z^2 + 2z^4. \qquad \blacksquare$$

**(b)** By the question this equals zero:

$$2z^4 + 12z^2 + 2 = 0 \;\Longrightarrow\; z^4 + 6z^2 + 1 = 0.$$

A quadratic in $z^2$:

$$z^2 = \frac{-6 \pm \sqrt{36-4}}{2} = \frac{-6 \pm 4\sqrt2}{2} = -3 \pm 2\sqrt2.$$

**(c)** Substitute $z = i\tan\frac{\pi}{8}$, hence
$z^2 = -\tan^2\frac{\pi}{8}$:

$$-\tan^2\frac{\pi}{8} = -3 \pm 2\sqrt2
\;\Longrightarrow\; \tan^2\frac{\pi}{8} = 3 \mp 2\sqrt2.$$

What is left is choosing the sign. $3+2\sqrt2 \approx 5.83$, and its root is
$\approx 2.41$; $3-2\sqrt2 \approx 0.17$, and its root is $\approx 0.414$. The angle
$\frac{\pi}{8}$ is smaller than $\frac{\pi}{4}$, so $\tan\frac{\pi}{8} < 1$. Only
the smaller one fits:

$$\tan\frac{\pi}{8} = \sqrt{3-2\sqrt2}. \qquad \blacksquare$$

```python
my15_e = 2 + 12*z**2 + 2*z**4
my15_z = [-3 + 2*sqrt(2), -3 - 2*sqrt(2)]
```

**The marking.** M1 for the binomial expansion, A1 for $2+12z^2+2z^4$, M1 for
attempting the quadratic, A1 for $z^2 = -3\pm2\sqrt2$, M1 for substituting
$z = i\tan\frac\pi8$, A1 for $\tan^2\frac\pi8 = 3\mp2\sqrt2$, R1 for justifying the
choice of root.

**The last mark is in words.** The R1 is not for a computation but for the sentence
«$\tan\frac{\pi}{8}$ is the smaller positive root». Without it the proof is
incomplete: you found two candidates and did not say why one was taken. It is the
same R1 as in A7.

**A pretty side fact.** $3-2\sqrt2 = \left(\sqrt2-1\right)^2$, so
$\tan\frac\pi8 = \sqrt2-1$. The form from the question and this one are the same
number; the markscheme asked for $\sqrt{3-2\sqrt2}$, but recognising the perfect
square is useful as a check.
""")

md(r"""
## Solution 16 — the task on the timer

**(c)** The first three terms from task 10:

$$(1+5x)^{1/2} = 1 + \frac52 x - \frac{25}{8}x^2 + \dots$$

The first three terms from task 13:

$$\frac{1+px}{1+qx} = 1 + (p-q)x + \left(q^2-pq\right)x^2 + \dots$$

Equate them:

$$p - q = \frac52, \qquad q^2 - pq = -\frac{25}{8}.$$

From the first, $p = q + \frac52$. Substitute into the second:

$$q^2 - q\left(q+\frac52\right) = -\frac52 q = -\frac{25}{8}
\;\Longrightarrow\; q = \frac54. \qquad \blacksquare$$

Then $p = \frac54 + \frac52 = \frac{15}{4}$.

**(d)** To approximate $\sqrt{1.2}$ we need $1+5x = 1.2$, hence

$$x = \frac{0.2}{5} = \frac{1}{25}.$$

Substitute into $\frac{1+px}{1+qx}$ with $p = \frac{15}{4}$, $q = \frac54$:

$$\frac{1 + \frac{15}{4}\cdot\frac{1}{25}}{1 + \frac54\cdot\frac{1}{25}}
= \frac{1 + \frac{3}{20}}{1 + \frac{1}{20}}
= \frac{\frac{23}{20}}{\frac{21}{20}} = \frac{23}{21}.$$

For comparison: $\frac{23}{21} = 1.095238$, while $\sqrt{1.2} = 1.095445$.

Now $\frac{\sqrt5}{2} = \sqrt{\frac54} = \sqrt{1.25}$, so we need $1+5x = 1.25$ and

$$x = \frac{0.25}{5} = \frac{1}{20}.$$

Since $\frac{1}{20} > \frac{1}{25}$, the value substituted is larger, the tail of
the series thrown away is larger, and the approximation comes out less accurate.
$\blacksquare$

```python
my16_q = Rational(5, 4)
my16_p = Rational(15, 4)
my16_x = Rational(1, 25)
my16_v = Rational(23, 21)
my16_y = Rational(1, 20)
```

**The marking.** (c): M1 for equating coefficients, A1 for one right equation, M1
for attempting to solve, A1 for $q = \frac54$ (the answer is given in the question,
so it is AG — «answer given», and the working has to be complete). (d): M1 for
finding $x$, A1 for $x = \frac1{25}$, M1 for the substitution, A1 for
$\frac{23}{21}$, A1 for $x = \frac1{20}$, R1 for the comparison.

**About AG.** In part (c) the answer is printed in the question. That means it
cannot be copied: every step has to be visible, and the last mark is given only for
complete working. Exactly as in A7.

**Where people go wrong in (d).** They read $\frac{\sqrt5}{2}$ as $\sqrt{\frac52}$.
The difference matters: $\frac{\sqrt5}{2} = \sqrt{1.25}$ gives $x = \frac1{20}$,
while $\sqrt{2.5}$ would require $1+5x = 2.5$, that is, $x = 0.3$. But the interval
of convergence here is $|5x| < 1$, that is, $|x| < 0.2$ — and $0.3$ does not fall
inside it. The answer would then be not «less accurate» but «the expansion does not
apply at all». It is worth being able to tell those two cases apart: outside the
interval of convergence, talk of accuracy loses its meaning.
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

OUT = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a3-binomial.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
