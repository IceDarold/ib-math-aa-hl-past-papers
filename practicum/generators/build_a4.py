"""Собирает практикум A4 (многочлены) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig, _series_canon, _complex_canon

I = sp.I
sq = sp.sqrt
R = sp.Rational
x, z, w, v, k = sp.symbols('x z w v k')
a, b, c, d, m, n, p, q, r = sp.symbols('a b c d m n p q r')


def ds(expr, var=x):
    return digest(_series_canon(expr, var))


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


def dcset(values):
    return digest('|'.join(sorted(_complex_canon(val) for val in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_a4.py ---
D_P1 = dn(0)
D_P2, D_Q2 = de(-3), de(9)
D_QS3 = dset([-7, 11])
D_Q3, D_R3 = de(-7), de(3)
D_B6 = ds(3 * a - 7, var=a)
D_A6N, D_B6N, D_C6N = dn(4), dn(5), dn(2)
D_P8 = ds((2 * k + 9) / k, var=k)
D_PQ9 = ds(p**3 + q**3, var=p)
D_AB10 = ds(k**2 / 4, var=k)
D_K10 = de(2 * sq(6))
D_M11 = dn(9)
D_R11 = dcset([3 * I, -3 * I, 4])
D_SQ13 = ds(p**2 - 2 * q, var=p)
D_DIF13 = ds(2 * p**2 - 6 * q, var=p)
D_P13, D_3Q13 = dn(49), dn(51)
D_Q13 = dn(12)
D_SQ14 = ds(p**2 - 2 * q, var=p)
D_P14, D_2Q14 = dn(4), dn(6)
D_ROOT14 = dn(-1)
D_PC14, D_3QC14 = dn(100), dn(102)
D_S17 = de(R(7, 2))
D_P17 = dn(1)
D_AB17 = dn(2)
D_A17, D_B17 = dn(1), dn(2)

TRIGGER = {1: 'factor', 2: 'vieta2', 3: 'apart', 4: 'mult', 5: 'sym',
           6: 'transform', 7: 'div', 8: 'conj', 9: 'vieta3', 10: 'factor',
           11: 'apart', 12: 'sym', 13: 'mult', 14: 'vieta2', 15: 'conj'}
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
# Practicum A4: polynomials

**145 marks, 50 blocks, nine techniques.** The widest topic of section A and the
only one where Paper 3 weighs more than Paper 2: 62 marks on Paper 1, 34 on Paper 2,
49 on Paper 3.

**Material.** 50 blocks and 145 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**The main idea of the topic.** A polynomial can be read from two sides — by its
coefficients and by its roots — and the whole topic consists of moving between those
two readings.

* Coefficients → roots: the factor theorem, division, factorising.
* Roots → coefficients: Vieta's formulas, symmetric sums.

In nearly every question you have to work out which way to go. The sign is simple:
if the roots **do not have to be found** — «find the product of the solutions»,
«show that $a^2 = 3b$» — then the way is from the roots to the coefficients, and
Vieta will save you a page.

**How to work**

1. Read the map of techniques. Techniques 1–3 are coefficients → roots, 4–8 are
   roots → coefficients, and 9 stands apart and leads into integration.
2. Work **on paper**. Long division and substitution into the factor theorem are
   hand work, and all the M1s are for them.
3. Enter the answer in whichever form suits you — except in the tasks where the
   question demands a particular **form**. There the check looks at the form too,
   and the task says so.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + factor, apart, solve, sqrt, I and the rest

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d = symbols('a b c d')
m, n, p, q, r = symbols('m n p q r')
z, w = symbols('z w')

print('ready; sympy', sp.__version__)
print('factorise:              ', factor(3*x**3 + 5*x**2 + x - 1))
print('divide with remainder:  ', div(2*x**2 - 5*x - 3, x - 1, x))
print('partial fractions:      ', apart(1/((x + 1)*(2*x + 1)), x))
print('roots numerically:      ', Poly(x**3 - 7*x**2 + 12*x + 1, x).nroots())
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | A factor and a remainder | «show that $(x-a)$ is a factor», «the remainder is …» | compute $P(a)$ |
| 2 | Division with a remainder | «express in the form $Q(x) + \frac{R}{d(x)}$» | long division or matching |
| 3 | A repeated root | «divisible by $(x+1)^2$», «repeated root» | $P(a)=0$ **and** $P'(a)=0$ |
| 4 | Vieta for a quadratic | «roots $\alpha,\beta$», $\alpha^2+\beta^2$, the roots are not asked for | $\alpha+\beta=-\frac ba$, $\alpha\beta=\frac ca$ |
| 5 | Vieta for a cubic and above | «write down the sum of the roots», a relation between the roots is given | the three symmetric sums |
| 6 | Complex roots in pairs | the coefficients are real, one root is imaginary | write down the conjugate |
| 7 | Symmetric sums | $\alpha^2+\beta^2+\gamma^2$ in terms of $p$ and $q$ | $(\alpha+\beta+\gamma)^2$ |
| 8 | An equation with new roots | «whose roots are $\frac1{\alpha^3}$», «$\frac1{z_i}$» | the substitution $w=\frac1z$, or Vieta |
| 9 | Partial fractions | «express in partial fractions» | the identity and convenient values of $x$ |

The ladder rests on two supports. Techniques 1–3 go from the coefficients to the
roots: substitute — find a factor — divide — get the other roots. Techniques 4–8 go
back the other way: the roots are not found at all, and you work with their sums and
products, because those are expressed through the coefficients immediately.

Technique 9 stands apart. It says nothing about the roots, but it turns a fraction
into a sum that can be integrated — and in the archive it is almost always part (a)
of a long integration question.

**What saves the most time.** Before computing, look at whether the roots are asked
for. Questions like «find the product of the solutions», «show that $a^2-3b=0$»,
«find $q$ and $r$» are solved without finding a single root. Whoever starts with the
formula for the roots of a cubic loses not marks but time — and with it everything
else.
""")

md(r"""
---
## Where the calculator is in this topic

Formally 83 marks out of 145 are on calculator papers, that is, 57%. That is exactly
the middle of the archive and a figure that misleads.

| | marks | of which really need a GDC |
| --- | --- | --- |
| Paper 1 | 62 | — |
| Paper 2 | 34 | 0 |
| Paper 3 | 49 | 4 |

The real work for a calculator in this topic is worth **four marks**: running
through the integers $q$ in task 13(e) and solving a system of three linear
equations in one block from November 2022. Everything else is algebra, done the same
way on either paper.

The reason is in how the topic is built. A calculator can find roots, and the
questions here are about what is tied to the roots **without finding them**. The
equation $x^3-7x^2+qx+1=0$ with the letter $q$ a calculator will not solve, while
Vieta does it in a line.

Where a GDC does help:

* **Check a factorisation.** Expand the product found and compare — ten seconds and
  three marks saved.
* **Run through integers.** «The smallest integer $q$ for which …» — straight
  searching on a graph or in a table; the markscheme accepts that explicitly.
* **Find an integer root of a quartic.** Drawing the graph and seeing it cross the
  axis at $x=-1$ is faster than trying the divisors of the constant term.

Where it is useless and harmful: wherever there is a letter in the question. And in
this topic a letter is almost everywhere.
""")

md(r"""
---
## Theory 1. A root, a factor, a remainder

The base of the whole left half of the topic is the **remainder theorem**:

$$\text{the remainder on dividing } P(x) \text{ by } (x-a) \;=\; P(a).$$

It is proved in one line. Write the division with a remainder:
$P(x) = (x-a)Q(x) + R$, where $R$ is a constant because the degree of the remainder
is less than the degree of the divisor. Put $x=a$: the first term vanishes and
$P(a) = R$ is left.

Hence the **factor theorem** — the same fact with $R=0$:

$$(x-a) \text{ is a factor of } P(x) \iff P(a) = 0.$$

**Careful with a factor that is not monic.** For $(2x+1)$ the root is $-\frac12$,
not $-1$ and not $-2$. The general rule: the factor $(\alpha x+\beta)$ corresponds
to $P\!\left(-\frac{\beta}{\alpha}\right)=0$. That loses marks more often than
anything else in the theorem.

**How it looks in a question.** There are usually two conditions, and each gives an
equation:

| In the question | The equation |
| --- | --- |
| $(x+4)$ is a factor of $f$ | $f(-4)=0$ |
| the remainder is $7$ when divided by $(x-2)$ | $f(2)=7$ |
| $f$ is divisible by $(x-5)^2$ | $f(5)=0$ **and** $f'(5)=0$ |

Two letters — two conditions — a linear system. There is nothing harder in this
technique, and it brings 26 marks of the archive.
""")

code(r"""
# A warm-up (not a task): the remainder theorem on a live example.
f = 3*x**3 + 5*x**2 + x - 1
for a0 in [-2, -1, 0, 1, 2]:
    print(f'dividing by (x - {a0:2d}):  remainder {div(f, x - a0, x)[1]},'
          f'   f({a0:2d}) = {f.subs(x, a0)}')
""")

md(r"""
## Task 1 🟢 — a factor in one substitution

Given the polynomial $P(x) = 3x^3 + 5x^2 + x - 1$, show that $(x+1)$ is a factor of
$P(x)$.

Enter the value that shows it.

*Source: May 2024 TZ1, Paper 1, Q11(a) (2 marks, no calculator).*
""")

code(r"""
my1 = ...                # the value that turns the factor theorem into a check

check_num('Task 1', my1, 6, '""" + D_P1 + r"""')
""")

md(r"""
## Task 2 🟢 — two conditions, two letters

Given $f(x) = 2x^4 - 6x^3 + px^2 + qx - 2$. It is known that $(x-1)$ is a factor of
$f(x)$ and that the remainder on dividing $f(x)$ by $(x-3)$ is $-2$. Find $p$ and
$q$.

*Source: May 2025 TZ3, Paper 2, Q2 (5 marks, calculator).*
""")

code(r"""
my2_p = ...
my2_q = ...

check_expr('Task 2, p', my2_p, '""" + D_P2 + r"""')
check_expr('Task 2, q', my2_q, '""" + D_Q2 + r"""')
""")

md(r"""
## Task 3 🟡 — when the system has two solutions

Given $P(x) = 2x^2 + qx + r$. The remainder on dividing by $(x+1)$ is 12, and the
roots $\alpha$ and $\beta$ of the polynomial are **real** and satisfy
$\alpha^2 + \beta^2 = \dfrac{37}{4}$. Find $q$ and $r$.

First enter **both** values of $q$ that the system gives. Then the single one that
survives the check of the condition, and the $r$ that goes with it.

*Source: November 2025 TZ3, Paper 2, Q6 (7 marks, calculator).*
""")

code(r"""
my3_all = [...]          # both roots of the equation in q
my3_q = ...              # the one that satisfies the question
my3_r = ...

check_set('Task 3, the candidates', my3_all, '""" + D_QS3 + r"""')
check_expr('Task 3, q', my3_q, '""" + D_Q3 + r"""')
check_expr('Task 3, r', my3_r, '""" + D_R3 + r"""')
""")

md(r"""
---
## Theory 2. Division and factorising

Division with a remainder for polynomials works as it does for integers:

$$P(x) = d(x)\,Q(x) + R(x), \qquad \deg R < \deg d.$$

The condition on the degree is not a formality but part of the definition. While the
degree of the remainder is not less than the degree of the divisor, the division can
go on and the writing is simply unfinished. The check in this practicum watches for
that separately.

**Three ways to divide.** All three are legitimate; the markscheme accepts any.

*Long division.* Slow, but it needs no guessing and always works.

*Matching coefficients.* Write $3x^2+7x-2 = (x+2)(Ax+B) + R$, expand, equate the
coefficients and get $A=3$, $B=1$, $R=-4$. For division by a linear factor that is
usually faster than long division.

*Synthetic division.* For division by $(x-a)$ — a table of one row.

**Factorising is a different requirement already.** «Express $P(x)$ as a product of
three linear factors» asks not for a value but for a **form of writing**. The answer
$3x^3+5x^2+x-1$ equals the right answer but earns no mark: there is no factorisation
in it.

The order of work: find one root by substitution (the candidates are the divisors of
the constant term divided by the divisors of the leading one), divide, and factorise
what is left by the ordinary school methods.
""")

md(r"""
## Task 4 🟢 — separate the whole part

Show that for $x \ne 1$

$$\frac{2x^2 - 5x - 3}{x-1} = 2x - 3 - \frac{6}{x-1}.$$

Enter the quotient and the remainder of the division of $2x^2-5x-3$ by $(x-1)$.

*Source: November 2021, Paper 1, Q6(a) (2 marks, no calculator).*
""")

code(r"""
my4_quo = ...            # the quotient
my4_rem = ...            # the remainder

verify_division('Task 4', my4_quo, my4_rem, 2*x**2 - 5*x - 3, x - 1)
""")

md(r"""
## Task 5 🟢 — three linear factors

The same $P(x) = 3x^3 + 5x^2 + x - 1$ as in task 1. Express it as a product of three
linear factors.

What is checked here is the **form of the writing**: an answer equal to $P(x) $ but
not written as a product does not count.

*Source: May 2024 TZ1, Paper 1, Q11(b) (3 marks, no calculator).*
""")

code(r"""
my5 = ...                # a product of three brackets

verify_factored('Task 5', my5, 3*x**3 + 5*x**2 + x - 1, n=3)
""")

md(r"""
## Task 6 🟡 — the factor is given as a quadratic

The polynomial $P(x) = x^3 + ax^2 + bx + c$ is divisible by $x^2 + 3x + 2$. The
numbers $a$, $b$, $c$ are distinct and belong to $\{1,2,3,4,5\}$.

**(i)** Express $b$ in terms of $a$.
**(ii)** Show that only one set works.
**(iii)** Factorise the resulting $P(x)$ into linear factors.

*Source: November 2022, Paper 1, Q11(b) (9 marks, no calculator).*
""")

code(r"""
my6_b = ...              # an expression in terms of a
my6_a, my6_bn, my6_cn = ..., ..., ...
my6_factored = ...       # a product of linear factors

check_series('Task 6(i)', my6_b, '""" + D_B6 + r"""', var=a)
check_num('Task 6(ii), a', my6_a, 6, '""" + D_A6N + r"""')
check_num('Task 6(ii), b', my6_bn, 6, '""" + D_B6N + r"""')
check_num('Task 6(ii), c', my6_cn, 6, '""" + D_C6N + r"""')
verify_factored('Task 6(iii)', my6_factored, x**3 + 4*x**2 + 5*x + 2, n=3)
""")

md(r"""
---
## Theory 3. A repeated root

If $(x-a)^2$ divides $P(x)$, then $a$ is a root not only of $P$ but of $P'$. It is
checked by differentiating directly: from $P = (x-a)^2 S(x)$ we get

$$P'(x) = 2(x-a)S(x) + (x-a)^2 S'(x),$$

and both terms contain $(x-a)$. Hence the working rule:

$$(x-a)^2 \mid P(x) \iff P(a) = 0 \;\text{ and }\; P'(a) = 0.$$

One condition has become two — exactly as many as are needed to find two letters.

**The second route, with no derivative.** Write $P(x) = (x-a)^2\left(x^2 + \alpha x
+ \beta\right)$, expand and equate coefficients. Longer, but it needs no
differentiation and on Paper 1 is sometimes safer.

**What a repeated root looks like on a graph.** The graph touches the $x$-axis
rather than crossing it. A multiplicity of 3 crosses it, but with a horizontal
tangent. On Paper 2 that is a way of seeing the answer before any algebra.
""")

md(r"""
## Task 7 🟡 — divisible by the square of a bracket

Find $p$ and $q$ for which the polynomial

$$x^4 + px^3 - 2x^2 + qx - 3$$

is divisible by $(x+1)^2$.

The check here stores nothing: your values are substituted into the polynomial and
the real remainder of the division is computed.

*Source: May 2025 TZ2, Paper 1, Q7 (5 marks, no calculator).*
""")

code(r"""
my7_p = ...
my7_q = ...

verify_divisible('Task 7', x**4 + p*x**3 - 2*x**2 + q*x - 3, (x + 1)**2,
                 {p: my7_p, q: my7_q})
""")

md(r"""
---
## Theory 4. Vieta's formulas

The second half of the topic. Expand the brackets in a polynomial written through
its roots:

$$(x-\alpha)(x-\beta)(x-\gamma) = x^3 - (\alpha+\beta+\gamma)x^2
+ (\alpha\beta+\beta\gamma+\gamma\alpha)x - \alpha\beta\gamma.$$

Comparing with $x^3 + px^2 + qx + s$ gives three equalities at once. The general
rule for $a_nx^n + \dots + a_0$:

$$\sum \alpha_i = -\frac{a_{n-1}}{a_n}, \qquad
\sum_{i<j} \alpha_i\alpha_j = \frac{a_{n-2}}{a_n}, \qquad \dots, \qquad
\prod \alpha_i = (-1)^n \frac{a_0}{a_n}.$$

The signs alternate. For a quadratic $ax^2+bx+c$:

$$\alpha + \beta = -\frac ba, \qquad \alpha\beta = \frac ca.$$

**Three places where marks are lost.**

*The leading coefficient is forgotten.* For $3x^2+7x-2$ the sum of the roots is
$-\frac73$, not $-7$. Dividing by $a$ is compulsory.

*The sign is confused.* The sum carries a minus, and so does the product for a
cubic. It is easier to remember through the alternation: $-,+,-,+$ starting from the
sum.

*The roots are hunted.* If the question asks for $\alpha^2+\beta^2$ or the product
of the solutions, the roots are not needed. The identity

$$\alpha^2+\beta^2 = (\alpha+\beta)^2 - 2\alpha\beta$$

does the work, and in various wrappers it brings most of the marks of the
technique.
""")

md(r"""
## Task 8 🟢 — the product of the roots with a letter

Write down an expression for the product of the roots of the equation

$$kx^2 - (k+3)x + 2k + 9 = 0$$

in terms of $k$.

*Source: May 2022 TZ1, Paper 2, Q8(a) (1 mark, calculator).*
""")

code(r"""
my8 = ...                # the product of the roots in terms of k

check_series('Task 8', my8, '""" + D_P8 + r"""', var=k)
""")

md(r"""
---
## Theory 5. An equation with new roots

The question sounds like this: an equation has roots $\alpha,\beta$; write the
equation whose roots are $\frac1{\alpha^3}$ and $\frac1{\beta^3}$ — **without
finding $\alpha$ and $\beta$**.

**Route one: substitution.** If the new root is $w = f(z)$, express $z$ in terms of
$w$ and substitute into the original equation. For $w = z+2$ that is $z = w-2$:

$$z^2 - 6z + 5 = 0 \;\Longrightarrow\; (w-2)^2 - 6(w-2) + 5 = 0
\;\Longrightarrow\; w^2 - 10w + 21 = 0.$$

Three lines, and it is the best way when the transformation can be inverted
explicitly. Checking yourself is easy: the roots were $1$ and $5$, and they have
become $3$ and $7$.

**Route two: through Vieta.** Compute the sum and the product of the new roots in
terms of the old ones, then assemble the equation $x^2 - Sx + P = 0$. It is needed
when substitution leads to trouble — for example when the new roots are powers of
the old ones:

$$\alpha^2+\beta^2 = (\alpha+\beta)^2 - 2\alpha\beta,
\qquad \alpha^2\beta^2 = (\alpha\beta)^2 .$$

Both parts are expressed through the sum and the product, that is, through the
coefficients, and no root had to be found. For higher powers the same thing works:
the sum of powers is reduced to the sum and the product by a suitable identity, and
it is exactly such an identity that the exam usually asks you to prove as a separate
part — not for decoration, but because without it the second route does not go
through.

**The check in the notebook is built on the substance.** There are no reference
coefficients: the roots of your equation are computed numerically and compared with
the transformed roots of the original. So an equation multiplied by any number
passes too — its roots are the same, and the markscheme accepts it as well.
""")

md(r"""
## Task 9 🟡 — an identity and a new equation

**(a)** Prove the identity $(p+q)^3 - 3pq(p+q) \equiv p^3 + q^3$. Enter the
difference of the two expanded parts of the left-hand side.

**(b)** The equation $2x^2 - 5x + 1 = 0$ has roots $\alpha$ and $\beta$. Find $m$
and $n$ such that the roots of $x^2 + mx + n = 0$ are $\frac1{\alpha^3}$ and
$\frac1{\beta^3}$. Finding $\alpha$ and $\beta$ is not allowed.

*Source: November 2021, Paper 2, Q6 (8 marks, calculator).*
""")

code(r"""
my9_a = ...              # (p+q)**3 - 3*p*q*(p+q), both brackets expanded
my9_m = ...
my9_n = ...

check_series('Task 9(a)', my9_a, '""" + D_PQ9 + r"""', var=p)
verify_root_transform('Task 9(b)', [1, my9_m, my9_n],
                      2*x**2 - 5*x + 1, lambda t: 1/t**3)
""")

md(r"""
## Task 10 🟡 — a relation between the roots is given

The equation

$$x^3 - kx^2 + \tfrac{k^2}{2}\,x - 3k = 0, \qquad k > 0,$$

has roots $\alpha$, $\beta$ and $\alpha+\beta$.

First express $\alpha\beta$ in terms of $k$, then find $k$.

*Source: May 2021 TZ2, Paper 1, Q7 (5 marks, no calculator).* The question is given
in a consistent form; the discrepancy with the archive's tags is dealt with in the
solution.
""")

code(r"""
my10_ab = ...            # alpha*beta in terms of k
my10_k = ...             # the value of k

check_series('Task 10, alpha*beta', my10_ab, '""" + D_AB10 + r"""', var=k)
check_expr('Task 10, k', my10_k, '""" + D_K10 + r"""')
""")

md(r"""
---
## Theory 6. Complex roots come in pairs

If **all the coefficients** of a polynomial are real and $z_0$ is a root of it, then
$\overline{z_0}$ is a root as well. The reason is one line: conjugation commutes
with addition and multiplication, so

$$\overline{P(z_0)} = P\!\left(\overline{z_0}\right),$$

and if the left-hand side is zero, so is the right. The condition about real
coefficients is essential: $z - i$ has only one root.

**What follows immediately.**

* Non-real roots always come in an even number.
* A cubic with real coefficients **always has a real root** — there are three of
  them and an even number of non-real ones. Another way of saying the same: the
  graph of a cubic goes to $-\infty$ and $+\infty$, so it crosses the axis.
* A pair $z_0, \overline{z_0}$ gives a real quadratic factor
  $z^2 - 2\operatorname{Re}(z_0)\,z + |z_0|^2$. For $1\pm i$ that is $z^2-2z+2$.

**How this works together with Vieta.** A pair of conjugate roots contributes
$2\operatorname{Re}(z_0)$ to the sum — a real number — and $|z_0|^2 > 0$ to the
product. The imaginary parts cancel and Vieta's equations stay real. That is exactly
why such questions are solved with no complex working at all.
""")

md(r"""
## Task 11 🔴 — find the parameter and all the roots

The polynomial

$$P(z) = z^3 - \frac{36}{m}z^2 + mz - 4m, \qquad m \in \mathbb{R},\; m > 0,$$

has a factor $z - 3i$. Find $m$ and all the roots of $P$.

*Source: May 2023 TZ1, Paper 1, Q7 (6 marks, no calculator).*
""")

code(r"""
my11_m = ...
my11_roots = [...]       # all three roots

check_num('Task 11, m', my11_m, 6, '""" + D_M11 + r"""')
check_complex_set('Task 11, the roots', my11_roots, '""" + D_R11 + r"""')
""")

md(r"""
## Task 12 🟡 — an equation for the reciprocal roots

The equation $z^4 + 2z^2 + 4 = 0$ has roots $z_1, z_2, z_3, z_4$. Find $p$, $q$,
$r$ such that the numbers $\frac1{z_1}, \dots, \frac1{z_4}$ satisfy the equation

$$pw^4 + qw^2 + r = 0.$$

*Source: May 2025 TZ2, Paper 1, Q12(d) (3 marks, no calculator).*
""")

code(r"""
my12_p, my12_q, my12_r = ..., ..., ...

verify_root_transform('Task 12', [my12_p, 0, my12_q, 0, my12_r],
                      z**4 + 2*z**2 + 4, lambda s: 1/s, var=z)
""")

md(r"""
---
## Theory 7. Symmetric sums and the reality of the roots

The prettiest construction in the topic, and all of it comes from one technique: **a
symmetric combination of the roots is squared and Vieta's formulas are recognised in
it.** The square of a sum always gives the same thing:

$$\left(\textstyle\sum \alpha_i\right)^2
= \sum \alpha_i^2 + 2\sum_{i<j}\alpha_i\alpha_j ,$$

and both sums on the right are coefficients. So the sum of the squares of the roots
is expressed through the coefficients, and no root has to be found.

**The same technique works not only for the roots themselves.** Take the reciprocals
for a cubic $x^3+px^2+qx+r$. By Vieta

$$\sum\frac{1}{\alpha} = \frac{q}{-r}, \qquad
\sum_{i<j}\frac{1}{\alpha_i\alpha_j} = \frac{-p}{-r} = \frac{p}{r},$$

and the same squaring gives

$$\sum\frac{1}{\alpha^2}
= \left(\frac{q}{-r}\right)^2 - 2\cdot\frac{p}{r}
= \frac{q^2 - 2pr}{r^2}.$$

Check it on $x^3-6x^2+11x-6$, whose roots are $1,2,3$: the formula gives
$\frac{121-72}{36}=\frac{49}{36}$, and that is exactly $1+\frac14+\frac19$.

**Where this leads.** If you square not the sum of the roots but their pairwise
**differences** and add them, the left-hand side is a sum of squares — and for real
numbers that is non-negative. On the right, after Vieta is substituted, an
expression in two coefficients is left. The result is a criterion that can be
checked in your head and that shows that the roots are not all real. Deriving it is
the work of task 13, and it is worth doing rather than reading.

**What the criterion does not give.** The converse is false: the opposite inequality
does **not** imply that all the roots are real. The sum of the squares of the
differences is then non-negative, but it is a complex sum, and its non-negativity
guarantees nothing. The counterexample is task 13 as well.

**For a polynomial of the fourth degree** the same identity works word for word, but
there are four squares in it rather than three, and the constant in the criterion
changes with their number. Carrying the number over from the cubic case to the
quartic one is the most frequent mistake in this question.
""")

md(r"""
## Task 13 🔴 — the Paper 3 investigation, the cubic case

Let $\alpha, \beta, \gamma$ be the roots of $x^3 + px^2 + qx + r = 0$.

**(b)(i)** Express $\alpha^2+\beta^2+\gamma^2$ in terms of $p$ and $q$.
**(b)(ii)** Express $(\alpha-\beta)^2+(\beta-\gamma)^2+(\gamma-\alpha)^2$ in terms
of $p$ and $q$.
**(d)** For $x^3 - 7x^2 + qx + 1 = 0$ with $q = 17$, enter $p^2$ and $3q$.
**(e)(i)** Find the smallest integer $q > 0$ for which $p^2 \ge 3q$ and yet the
roots are still not all real.

*Source: May 2022 TZ2, Paper 3, Q2(a)–(e) (15 marks, calculator).*
""")

code(r"""
my13_sq = ...            # alpha^2+beta^2+gamma^2 in terms of p and q
my13_dif = ...           # the sum of the squares of the differences, in p and q
my13_p2 = ...            # p^2 for x^3 - 7x^2 + 17x + 1
my13_3q = ...            # 3q for the same one
my13_q = ...             # the smallest integer q from part (e)

check_series('Task 13(b)(i)',  my13_sq,  '""" + D_SQ13 + r"""', var=p)
check_series('Task 13(b)(ii)', my13_dif, '""" + D_DIF13 + r"""', var=p)
check_num('Task 13(d), p^2', my13_p2, 6, '""" + D_P13 + r"""')
check_num('Task 13(d), 3q', my13_3q, 6, '""" + D_3Q13 + r"""')
check_num('Task 13(e)', my13_q, 6, '""" + D_Q13 + r"""')
""")

code(r"""
# Part (e) is the one place where a calculator is genuinely needed.
# The condition p^2 >= 3q at p = -7 gives q <= 16; we look at where the roots
# stop being all real.
for q0 in range(1, 17):
    found = Poly(x**3 - 7*x**2 + q0*x + 1, x).nroots()
    n_real = sum(1 for s in found if abs(im(s)) < 1e-9)
    print(f'q = {q0:2d}:  real roots {n_real}',
          '  <-- counterexample' if n_real < 3 else '')
""")

md(r"""
## Task 14 🔴 — the Paper 3 investigation, the fourth degree

A continuation of the same question. Now $\alpha,\beta,\gamma,\delta$ are the roots
of $x^4 + px^3 + qx^2 + \dots = 0$.

**(f)(i)** Express $\alpha^2+\beta^2+\gamma^2+\delta^2$ in terms of $p$ and $q$.
**(g)** For $x^4 - 2x^3 + 3x^2 - 4x + 5 = 0$, enter $p^2$ and $2q$.
**(h)(ii)** Write down the integer root of $x^4 - 9x^3 + 24x^2 + 22x - 12 = 0$.
**(h)(iii)** Divide that polynomial by $(x + 1)$ and enter the quotient and the
remainder; then $p^2$ and $3q$ for the cubic factor obtained.

*Source: May 2022 TZ2, Paper 3, Q2(f)–(h) (12 marks, calculator).*
""")

code(r"""
my14_sq = ...            # the sum of the squares of four roots, in p and q
my14_p2, my14_2q = ..., ...
my14_root = ...          # the integer root of the quartic
my14_quo, my14_rem = ..., ...
my14_pc2, my14_3qc = ..., ...

QUART = x**4 - 9*x**3 + 24*x**2 + 22*x - 12

check_series('Task 14(f)(i)', my14_sq, '""" + D_SQ14 + r"""', var=p)
check_num('Task 14(g), p^2', my14_p2, 6, '""" + D_P14 + r"""')
check_num('Task 14(g), 2q', my14_2q, 6, '""" + D_2Q14 + r"""')
check_num('Task 14(h)(ii)', my14_root, 6, '""" + D_ROOT14 + r"""')
verify_division('Task 14(h)(iii)', my14_quo, my14_rem, QUART, x + 1)
check_num('Task 14(h)(iii), p^2', my14_pc2, 6, '""" + D_PC14 + r"""')
check_num('Task 14(h)(iii), 3q', my14_3qc, 6, '""" + D_3QC14 + r"""')
""")

md(r"""
---
## Theory 8. Partial fractions

A technique that says nothing about the roots, but without which half the integrals
do not go through. A proper fraction with a factorisable denominator is split into a
sum:

$$\frac{1}{(x-2)(3x+1)} = \frac{A}{x-2} + \frac{B}{3x+1}.$$

Multiply both sides by the denominator:

$$1 = A(3x+1) + B(x-2).$$

From there two routes, both worth full marks.

*Substituting convenient values.* $x = 2$ kills the second term: $1 = 7A$, hence
$A = \frac17$. $x = -\frac13$ kills the first: $1 = -\frac73 B$, hence
$B = -\frac37$. Faster, safer, and with almost nowhere to go wrong.

*Equating coefficients.* $3A + B = 0$ and $A - 2B = 1$. Longer, but it works where
there are no convenient values.

**A repeated factor needs two terms.** For $(x+1)^2$ in the denominator you write

$$\frac{A}{x+1} + \frac{B}{(x+1)^2},$$

not a single fraction. If you write a single one, the system turns out inconsistent
— a reliable sign that a term has been forgotten.

**The check in the notebook looks at the form.** Every term has to be a partial
fraction: a numerator with no $x$, a denominator that is a power of a single linear
factor. The answer $\frac{1}{(x+1)(2x+1)}$ equals itself but is not a
decomposition, and the check will reject it — exactly as an examiner would.
""")

md(r"""
## Task 15 🟢 — two decompositions in one line

**(a)** Decompose $\dfrac{1}{x(k-x)}$ into a sum of the form
$\dfrac{a}{x} + \dfrac{b}{k-x}$.

**(b)** Decompose $\dfrac{1}{1-4v^2}$ into a sum of the form
$\dfrac{A}{1-2v} + \dfrac{B}{1+2v}$.

*Sources: May 2021 TZ1, Paper 2, Q12(a) (3 marks) and November 2025 TZ3, Paper 2,
Q12(c) (2 marks), both with a calculator.*
""")

code(r"""
my15_a = ...             # a sum of two fractions, in terms of k
my15_b = ...             # a sum of two fractions, in terms of v

check_apart('Task 15(a)', my15_a, 1/(x*(k - x)))
check_apart('Task 15(b)', my15_b, 1/(1 - 4*v**2), var=v)
""")

md(r"""
## Task 16 🟡 — a repeated factor in the denominator

Let $Q(x) = (x+1)(2x+1)$.

**(c)** Decompose $\dfrac{1}{Q(x)}$ into partial fractions.

**(d)** Decompose into partial fractions

$$\frac{1 - \dfrac{x}{Q(x)}}{(1+x)(2x+1)}.$$

In the second part the denominator, once tidied, turns out to be a square, and there
will be four terms.

*Source: May 2024 TZ1, Paper 1, Q11(c)–(d) (5 marks, no calculator).* The
right-hand side of part (d) is recorded with errors in the archive's tags; the
working is in the solution.
""")

code(r"""
Q = (x + 1)*(2*x + 1)

my16_c = ...             # the decomposition of 1/Q(x)
my16_d = ...             # the decomposition of the expression from part (d)

check_apart('Task 16(c)', my16_c, 1/Q)
check_apart('Task 16(d)', my16_d, (1 - x/Q)/((1 + x)*(2*x + 1)))
""")

md(r"""
---
## Trainer: name the technique in five seconds

Below are fifteen statements with no solutions. For each one write the code of the
technique — and nothing else. Nothing has to be computed; the aim is for the first
move to be found before the computing starts.

The codes: `factor` (a factor and a remainder) · `div` (division with a remainder) ·
`mult` (a repeated root) · `vieta2` (Vieta, a quadratic) · `vieta3` (Vieta, degree
above two) · `conj` (complex roots in pairs) · `sym` (symmetric sums) ·
`transform` (an equation with new roots) · `apart` (partial fractions)

1. Show that $(x-2)$ is a factor of $x^3-3x^2+4x-4$.
2. The equation $3x^2+7x-2=0$ has roots $\alpha,\beta$. Find $\alpha^2+\beta^2$.
3. Write $\dfrac{5}{(x-1)(x+4)}$ as a sum of two fractions.
4. For which $a$ does the polynomial $x^3+ax+2$ have a repeated root?
5. The roots of $x^3+px^2+qx+r$ are real. What can be said about $p^2$ and $3q$?
6. The equation with roots $\alpha+1$ and $\beta+1$, where $\alpha,\beta$ are the roots of a given one.
7. Write $\dfrac{x^3+1}{x-2}$ in the form $Q(x)+\dfrac{R}{x-2}$.
8. A polynomial with real coefficients has the root $2-5i$. What else is known?
9. Write down the sum of the roots of $4x^5-3x^4+x-7=0$.
10. The remainder on dividing $f(x)$ by $(x-3)$ is 5. Find $f(3)$.
11. Decompose $\dfrac{2x+1}{x^2(x-3)}$ into partial fractions.
12. For $x^4+px^3+qx^2+\dots$ express $\sum\alpha_i^2$ in terms of $p$ and $q$.
13. The graph of $y=P(x)$ touches the $x$-axis at $x=4$. What does that give?
14. Find the product of the solutions of the equation $2x^2=5x-1$.
15. The equation $z^3-1=0$ has the root $z=1$. Find the others.
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
## Task 17 🔴 — on the timer, 12 minutes

A whole Paper 1 question with no calculator. Seven marks, target time about 12
minutes.

The cubic polynomial $g(x) = 2x^3 - 7x^2 + dx - e$ has roots $\alpha$, $\beta$,
$\gamma$.

**(a)** Write down $\alpha + \beta + \gamma$.

**(b)** The same $\alpha,\beta,\gamma$ are roots of the polynomial
$h(z) = 2z^5 - 11z^4 + rz^3 + sz^2 + tz - 20$, and $z = \rho + 3i$ is a root of it
too. Show that $\rho = 1$.

**(c)** Given that $h\!\left(\frac12\right) = 0$, that $\alpha,\beta$ are positive
and real with $\alpha < \beta$, and that $\gamma$ is rational, find $\alpha\beta$
and then $\alpha$ and $\beta$.

*Source: May 2024 TZ2, Paper 1, Q7 (7 marks, no calculator).*
""")

code(r"""
my17_sum = ...           # alpha + beta + gamma
my17_rho = ...           # the value of rho
my17_ab = ...            # alpha*beta
my17_alpha, my17_beta = ..., ...

check_expr('Task 17(a)', my17_sum, '""" + D_S17 + r"""')
check_num('Task 17(b)', my17_rho, 6, '""" + D_P17 + r"""')
check_num('Task 17(c), alpha*beta', my17_ab, 6, '""" + D_AB17 + r"""')
check_num('Task 17(c), alpha', my17_alpha, 6, '""" + D_A17 + r"""')
check_num('Task 17(c), beta', my17_beta, 6, '""" + D_B17 + r"""')
""")

md(r"""
---
# Solutions

Below is a full working of every task with the markscheme's marking. Open them after
you have solved on your own: the working explains not only the answer but what
exactly the marks are given for.
""")

md(r"""
## Solution 1 — a factor in one substitution

By the factor theorem $(x+1)$ divides $P(x)$ if and only if $P(-1) = 0$. Compute:

$$P(-1) = 3(-1)^3 + 5(-1)^2 + (-1) - 1 = -3 + 5 - 1 - 1 = 0.
\qquad \blacksquare$$

```python
my1 = 0
```

**The marking.** M1 for substituting $x=-1$ (the expression itself has to be
visible, not just the result), A1 for the zero with the conclusion «therefore
$(x+1)$ is a factor». Long division with a zero remainder is accepted as an
equal.

**About the wording.** This is a «show that» question: the answer is printed in the
question and the mark is for the working. Writing «$P(-1)=0$, QED» with no
computation scores zero. The concluding sentence at the end is compulsory: without
it the computing is visible but the answer to the question asked is not.
""")

md(r"""
## Solution 2 — two conditions, two letters

$(x-1)$ is a factor, so $f(1) = 0$:

$$2 - 6 + p + q - 2 = 0 \;\Longrightarrow\; p + q = 6.$$

The remainder on dividing by $(x-3)$ is $-2$, so $f(3) = -2$:

$$2\cdot81 - 6\cdot27 + 9p + 3q - 2 = -2
\;\Longrightarrow\; 162 - 162 + 9p + 3q = 0
\;\Longrightarrow\; 3p + q = 0.$$

Subtract the first from the second: $2p = -6$, hence $p = -3$ and $q = 9$.

```python
my2_p = -3
my2_q = 9
```

**The marking.** M1 for applying the factor theorem, A1 for the first equation, M1
for applying the remainder theorem, A1 for the second equation, A1 for both values.
Five marks, and three of them are for the equations being written at all.

**About the calculator.** This is Paper 2 and the system is allowed to be solved on
a GDC. But it still has to be written down by hand, and a system of two linear
equations is solved in your head faster than it is typed in. The calculator belongs
here as a check: substitute the $p,q$ found and confirm that $f(1)=0$.
""")

md(r"""
## Solution 3 — when the system has two solutions

The remainder on dividing by $(x+1)$ is $P(-1)$:

$$2 - q + r = 12 \;\Longrightarrow\; r - q = 10.$$

By Vieta $\alpha+\beta = -\frac q2$ and $\alpha\beta = \frac r2$. Then

$$\alpha^2+\beta^2 = (\alpha+\beta)^2 - 2\alpha\beta
= \frac{q^2}{4} - r = \frac{37}{4}.$$

Substitute $r = q + 10$:

$$\frac{q^2}{4} - q - 10 = \frac{37}{4}
\;\Longrightarrow\; q^2 - 4q - 40 = 37
\;\Longrightarrow\; q^2 - 4q - 77 = 0.$$

Factorise: $(q-11)(q+7) = 0$, hence $q = 11$ or $q = -7$.

**Do both work?** Check the discriminant of $2x^2+qx+r$:

* $q = -7$, $r = 3$: $D = 49 - 24 = 25 > 0$, the roots $3$ and $\frac12$ are real.
* $q = 11$, $r = 21$: $D = 121 - 168 = -47 < 0$, the roots are not real.

The question requires real roots, so $q = -7$, $r = 3$ remain.

```python
my3_all = [-7, 11]
my3_q = -7
my3_r = 3
```

**The marking.** M1 for the remainder theorem, A1 for $r-q=10$, M1 for the identity
$\alpha^2+\beta^2 = (\alpha+\beta)^2-2\alpha\beta$, A1 for the second equation, M1
for solving the system, A1A1 for $q$ and $r$.

**Why this task is marked 🟡.** The algebra is simple and the trap is at the end: the
quadratic in $q$ gives two roots, and the second looks no worse than the first. It
is discarded only by checking the discriminant. In the archive's own tags the second
root is not mentioned at all — and that is the case where the working of the question
is shorter than the truth about it.

**A general rule.** Whenever the system in the letters has turned out quadratic,
compute both solutions and check each against the question. A condition «the roots
are real», «$k>0$», «$n \in \mathbb{Z}^+$» is not in the question for decoration —
it is the selection.
""")

md(r"""
## Solution 4 — separate the whole part

Divide by long division. $2x^2 : x = 2x$; multiply $2x(x-1) = 2x^2-2x$; subtract:

$$2x^2-5x-3 - (2x^2-2x) = -3x - 3.$$

Then $-3x : x = -3$; multiply $-3(x-1) = -3x+3$; subtract:

$$-3x-3 - (-3x+3) = -6.$$

The quotient is $2x-3$ and the remainder $-6$. So

$$\frac{2x^2-5x-3}{x-1} = 2x - 3 - \frac{6}{x-1}. \qquad \blacksquare$$

```python
my4_quo = 2*x - 3
my4_rem = -6
```

**The marking.** The markscheme comes at this block from the other side: M1 for
bringing the right-hand side to a common denominator, A1 for the numerators
matching. Both directions are accepted, and the second is sometimes faster —
multiplying $2x-3-\frac6{x-1}$ by $(x-1)$ is easier than dividing.

**Why separate the whole part at all.** For the sake of integration. The fraction
$\frac{2x^2-5x-3}{x-1}$ does not integrate as it is, while $2x-3-\frac6{x-1}$
integrates in a line. The same technique for the same reason stands at the start of
half the questions in section E5.

**About the degree of the remainder.** The check in the notebook watches separately
that the degree of the remainder is less than the degree of the divisor. The answer
«quotient $2x$, remainder $-3x-3$» is arithmetically right — the sum recovers the
dividend — but it is not a division: the dividing can go on.
""")

md(r"""
## Solution 5 — three linear factors

From task 1 we know that $(x+1)$ is a factor. Divide:

$$3x^3+5x^2+x-1 = (x+1)\left(3x^2+2x-1\right).$$

The quadratic factorises the ordinary way. Look for two numbers with product
$3\cdot(-1) = -3$ and sum $2$: they are $3$ and $-1$.

$$3x^2+2x-1 = 3x^2+3x-x-1 = 3x(x+1) - (x+1) = (x+1)(3x-1).$$

So

$$P(x) = (x+1)^2(3x-1). \qquad \blacksquare$$

```python
my5 = (x + 1)**2*(3*x - 1)
```

**The marking.** M1 for dividing by $(x+1)$, A1 for the quadratic quotient, A1 for
the final product. Three marks.

**What matters here is that $(x+1)$ came out twice.** The root $-1$ is repeated, and
the graph of $P$ touches the $x$-axis there rather than crossing it. Technique 3
deals with such cases from the other side — when the multiplicity is given in the
question and the coefficients are what have to be found.

**About the form of the answer.** The question asks for **a product of three linear
factors**, and that is a requirement on the writing. The check `verify_factored`
parses exactly what is in the cell and does not factorise the answer itself:
`3*x**3 + 5*x**2 + x - 1` equals the right answer but gets ❌. That is exactly what
an examiner would do.

It also shows how this topic differs from A3. There `check_series` accepted an
unexpanded bracket, because the question asked for an expansion and numerically a
bracket equals its expansion. Here the question asks for the reverse — and so does
the check.
""")

md(r"""
## Solution 6 — the factor is given as a quadratic

**(i)** Factorise the divisor: $x^2+3x+2 = (x+1)(x+2)$. So $P(-1)=0$ and
$P(-2)=0$:

$$-1 + a - b + c = 0, \qquad -8 + 4a - 2b + c = 0.$$

Subtract the first from the second to remove $c$:

$$-7 + 3a - b = 0 \;\Longrightarrow\; b = 3a - 7. \qquad \blacksquare$$

**(ii)** From the first equation $c = 1 - a + b = 1 - a + 3a - 7 = 2a - 6$. Run
through $a \in \{1,\dots,5\}$:

| $a$ | $b = 3a-7$ | $c = 2a-6$ | does it work? |
| --- | --- | --- | --- |
| 1 | $-4$ | $-4$ | no, outside the set |
| 2 | $-1$ | $-2$ | no, outside the set |
| 3 | 2 | 0 | no, $0 \notin \{1,\dots,5\}$ |
| 4 | 5 | 2 | **yes** |
| 5 | 8 | 4 | no, $8$ is outside the set |

The only set: $a=4$, $b=5$, $c=2$, and all three are distinct. $\blacksquare$

**(iii)** $P(x) = x^3+4x^2+5x+2 = (x^2+3x+2)(x+1) = (x+1)^2(x+2)$.

```python
my6_b = 3*a - 7
my6_a, my6_bn, my6_cn = 4, 5, 2
my6_factored = (x + 1)**2*(x + 2)
```

**The marking.** (i): M1 for factorising the divisor, M1 for applying the factor
theorem, A1A1 for the two equations, M1 for eliminating $c$, A1 for $b=3a-7$. (ii):
M1 for the search with the conditions checked, A1 for uniqueness. (iii): A1.

**Where marks are lost.** In part (ii) the markscheme requires exactly that **all
the cases are checked**: the answer «$a=4$» with no table gets M0A0, because
uniqueness has not been shown. That is the same kind of requirement as the R1 in A7
— the mark is for the completeness of the reasoning, not for the right number.

**A small thing worth a mark.** Checking that $a$, $b$, $c$ really are **distinct**:
the question says «distinct». The row $a=3$ falls away not because of a repeat but
because $c=0$ is not in the set — but both conditions have to be checked.
""")

md(r"""
## Solution 7 — divisible by the square of a bracket

Write $f(x) = x^4+px^3-2x^2+qx-3$. Divisibility by $(x+1)^2$ means

$$f(-1) = 0 \quad\text{and}\quad f'(-1) = 0.$$

The first condition:

$$1 - p - 2 - q - 3 = 0 \;\Longrightarrow\; p + q = -4.$$

Differentiate: $f'(x) = 4x^3+3px^2-4x+q$. The second condition:

$$-4 + 3p + 4 + q = 0 \;\Longrightarrow\; 3p + q = 0.$$

Subtract: $2p = 4$, hence $p = 2$ and $q = -6$.

Check: $x^4+2x^3-2x^2-6x-3 = (x+1)^2(x^2-3)$. $\blacksquare$

```python
my7_p = 2
my7_q = -6
```

**The marking.** M1 for the condition $f(-1)=0$, A1 for the first equation, M1 for
differentiating and $f'(-1)=0$, A1 for the second equation, A1 for both values.

**A second route, if you would rather not recall the derivative.** Write

$$x^4+px^3-2x^2+qx-3 = (x+1)^2\left(x^2 + \alpha x + \beta\right)$$

and equate coefficients. The constant term gives $\beta = -3$ at once, the
coefficient of $x^3$ gives $\alpha + 2 = p$, and the one of $x^2$ gives
$\beta + 2\alpha + 1 = -2$, hence $\alpha = 0$ and $p = 2$. The same number of
lines, and the markscheme accepts it.

**About the check in the notebook.** There is no reference answer here at all. Your
$p$ and $q$ are substituted into the polynomial and `sp.div` computes the real
remainder of the division by $(x+1)^2$. That is exactly the condition stated in the
question, and no written-down «right answer» is needed for it.
""")

md(r"""
## Solution 8 — the product of the roots with a letter

For $ax^2+bx+c=0$ the product of the roots is $\frac ca$. Here $a = k$ and
$c = 2k+9$, so

$$\alpha\beta = \frac{2k+9}{k}.$$

```python
my8 = (2*k + 9)/k
```

**The marking.** A1. One mark, and the question is the first part of a long task —
a gift that must not be left on the table.

**What comes next.** Such parts almost always lead to a condition like «the product
of the roots is 4» or «the roots are reciprocal». Then $\frac{2k+9}{k}$ is equated
to something and $k$ is found — with not a single root.

**A small thing.** The answer can also be written as $2 + \frac9k$; the check
compares values and will take either form. So will an examiner.
""")

md(r"""
## Solution 9 — an identity and a new equation

**(a)** Expand the cube:

$$(p+q)^3 = p^3 + 3p^2q + 3pq^2 + q^3.$$

Expand the second term:

$$3pq(p+q) = 3p^2q + 3pq^2.$$

Subtract — the middle terms cancel:

$$(p+q)^3 - 3pq(p+q) = p^3 + q^3. \qquad \blacksquare$$

**(b)** By Vieta for $2x^2-5x+1=0$:

$$\alpha + \beta = \frac52, \qquad \alpha\beta = \frac12.$$

The new roots are $\frac1{\alpha^3}$ and $\frac1{\beta^3}$. Their product:

$$n = \frac{1}{(\alpha\beta)^3} = \frac{1}{(1/2)^3} = 8.$$

Their sum:

$$\frac1{\alpha^3}+\frac1{\beta^3} = \frac{\alpha^3+\beta^3}{(\alpha\beta)^3}.$$

The numerator comes from the identity in part (a):

$$\alpha^3+\beta^3 = \left(\frac52\right)^3 - 3\cdot\frac12\cdot\frac52
= \frac{125}{8} - \frac{15}{4} = \frac{125 - 30}{8} = \frac{95}{8}.$$

So the sum of the new roots is $\frac{95/8}{1/8} = 95$. In the equation
$x^2+mx+n=0$ the sum of the roots is $-m$, so

$$m = -95, \qquad n = 8. \qquad \blacksquare$$

```python
my9_a = p**3 + 3*p**2*q + 3*p*q**2 + q**3 - (3*p**2*q + 3*p*q**2)
my9_m = -95
my9_n = 8
```

**The marking.** (a): M1 for expanding the cube, A1 for the result. (b): M1 for
Vieta on the original equation, A1 for $n=8$, M1 for expressing the sum through
$\alpha^3+\beta^3$, M1 for applying part (a), A1 for $\frac{95}8$, A1 for
$m=-95$.

**Why part (a) comes first.** It is the tool for (b). Almost every two-part question
in this topic is built that way: the first part prepares an identity, the second
applies it. On seeing «hence» or «use the result from part (a)», do not start again —
substitute.

**The sign of $m$.** The most frequent lost mark: finding the sum 95 and writing
$m=95$. In $x^2+mx+n$ the sum of the roots is $-m$, not $m$. You can check on any
familiar equation: $x^2-3x+2$ has roots 1 and 2, the sum is 3, and the coefficient
is $-3$.

**About the check.** `verify_root_transform` stores neither $m$ nor $n$. It takes the
roots of the original equation numerically, cubes them, inverts them and compares
with the roots of yours. So the equation $8x^2-760x+64=0$ — the same one multiplied
by 8 — passes too: its roots are the same.
""")

md(r"""
## Solution 10 — a relation between the roots is given

The roots: $\alpha$, $\beta$, $\alpha+\beta$. Write Vieta for
$x^3 - kx^2 + \frac{k^2}{2}x - 3k = 0$.

**The sum of the roots** is $k$:

$$\alpha + \beta + (\alpha+\beta) = 2(\alpha+\beta) = k
\;\Longrightarrow\; \alpha+\beta = \frac k2.$$

**The sum of the pairwise products** is $\frac{k^2}{2}$:

$$\alpha\beta + \alpha(\alpha+\beta) + \beta(\alpha+\beta)
= \alpha\beta + (\alpha+\beta)^2 = \frac{k^2}{2}.$$

Substitute $(\alpha+\beta)^2 = \frac{k^2}4$:

$$\alpha\beta = \frac{k^2}{2} - \frac{k^2}{4} = \frac{k^2}{4}.$$

**The product of the roots** is $3k$:

$$\alpha\beta(\alpha+\beta) = \frac{k^2}{4}\cdot\frac k2 = \frac{k^3}{8} = 3k.$$

With $k>0$ divide by $k$:

$$\frac{k^2}{8} = 3 \;\Longrightarrow\; k^2 = 24 \;\Longrightarrow\;
k = 2\sqrt6. \qquad \blacksquare$$

```python
my10_ab = k**2/4
my10_k = 2*sqrt(6)
```

**The marking.** M1 for the sum of the roots, A1 for $\alpha+\beta=\frac k2$, M1 for
the product of the roots, M1 for the substitution, A1 for $k=2\sqrt6$.

**About the question.** In the archive's tags the equation is written as
$x^3-kx^2+3k=0$, and with that equation the answer $2\sqrt6$ does not exist: from
$\frac{k^3}8 = -3k$ one gets $k^2 = -24$. The constant term has to give the product
of the roots as $+3k$, and the middle coefficient has to agree with
$\alpha\beta = \frac{k^2}4$; the equation above does both and leads exactly to the
answer recorded in the archive. The details are in the technique card, section
`corpus_issues`.

**What the task teaches.** The condition «the third root equals the sum of the other
two» gives nothing by itself — it starts working only when it is substituted into
all three of Vieta's formulas at once. One formula is never enough: there are three
unknowns here ($\alpha$, $\beta$, $k$).
""")

md(r"""
## Solution 11 — find the parameter and all the roots

We are given that $z-3i$ is a factor, so $3i$ is a root. The coefficients of $P$ are
real (for real $m$), so $-3i$ is a root too. Let the third root be $\rho$.

**The product of the roots** for $z^3 - \frac{36}{m}z^2 + mz - 4m$ is $4m$:

$$(3i)(-3i)\rho = 9\rho = 4m.$$

**The sum of the roots** is $\frac{36}{m}$:

$$3i + (-3i) + \rho = \rho = \frac{36}{m}.$$

Substitute the second into the first:

$$9\cdot\frac{36}{m} = 4m \;\Longrightarrow\; 324 = 4m^2
\;\Longrightarrow\; m^2 = 81 \;\Longrightarrow\; m = 9$$

(we take the positive root because $m>0$). Then $\rho = \frac{36}{9} = 4$, and the
roots of $P$ are $3i$, $-3i$, $4$. $\blacksquare$

```python
my11_m = 9
my11_roots = [3*I, -3*I, 4]
```

**The marking.** A1 for «$3i$ is a root», A1 for «$-3i$ is a root too», M1 for
attempting to equate the sum or the product, (A1) for $m=9$, A1 for the third root
4. A separate note in the markscheme: with no explicit mention of the roots the
maximum is A0A0(M1)(M1)(A1)A1 — that is, two marks are lost simply because it was
not said which numbers are taken to be roots.

**A check with the middle coefficient.** The sum of the pairwise products is $m$:

$$(3i)(-3i) + \left(3i + (-3i)\right)\rho = 9 + 0 = 9.$$

And indeed $m=9$. That is a spare equation, of which one would have been enough — a
useful free check.

**The second route.** Write $P(z) = (z-3i)(z+3i)(z-\rho) = (z^2+9)(z-\rho)$, expand
to $z^3 - \rho z^2 + 9z - 9\rho$ and compare the coefficients with the original. The
same thing comes out; the markscheme accepts it too. Note that the pair of conjugate
roots gave a real factor $z^2+9$ straight away — no complex numbers appear after
that.
""")

md(r"""
## Solution 12 — an equation for the reciprocal roots

Let $w = \frac1z$, that is, $z = \frac1w$. Substitute into the original equation:

$$\frac1{w^4} + \frac2{w^2} + 4 = 0.$$

Multiply by $w^4$ (legitimate: $w=0$ cannot be a root, because $z$ is finite):

$$1 + 2w^2 + 4w^4 = 0 \;\Longrightarrow\; 4w^4 + 2w^2 + 1 = 0.$$

So $p=4$, $q=2$, $r=1$. $\blacksquare$

```python
my12_p, my12_q, my12_r = 4, 2, 1
```

**The marking.** M1 for the substitution $w=\frac1z$, M1 for multiplying by $w^4$,
A1 for the triple of coefficients.

**Why substitution and not Vieta.** There are four roots here, and computing
$\sum \frac1{z_i}$, $\sum_{i<j} \frac1{z_iz_j}$ and so on means four symmetric sums
instead of two lines. The rule is simple: if the new root is expressed through the
old one **explicitly and invertibly**, go by substitution. Vieta is needed when the
inversion does not work out or the transformation is awkwardly non-linear — like
$\frac1{\alpha^3}$ in task 9.

**A pretty consequence.** The coefficients of the new equation are the coefficients
of the old one the other way round: $1,2,4 \to 4,2,1$. That always happens under
$z \to \frac1z$, and it is a handy check on the answer.
""")

md(r"""
## Solution 13 — the Paper 3 investigation, the cubic case

**(b)(i)** Square the sum of the roots:

$$(\alpha+\beta+\gamma)^2 = \alpha^2+\beta^2+\gamma^2
+ 2(\alpha\beta+\beta\gamma+\gamma\alpha).$$

By Vieta $\alpha+\beta+\gamma = -p$ and
$\alpha\beta+\beta\gamma+\gamma\alpha = q$, so
$p^2 = \left(\alpha^2+\beta^2+\gamma^2\right) + 2q$ and

$$\alpha^2+\beta^2+\gamma^2 = p^2 - 2q. \qquad \blacksquare$$

**(b)(ii)** Expand the sum of the squares of the differences:

$$(\alpha-\beta)^2+(\beta-\gamma)^2+(\gamma-\alpha)^2
= 2\left(\alpha^2+\beta^2+\gamma^2\right)
- 2(\alpha\beta+\beta\gamma+\gamma\alpha).$$

Substitute the result of (b)(i) and $q$:

$$= 2\left(p^2-2q\right) - 2q = 2p^2 - 6q. \qquad \blacksquare$$

**(c)** Suppose $p^2 < 3q$. Then $2p^2 - 6q < 0$, that is, the sum of the squares of
the differences is negative. If all three roots were real, every square would be
non-negative and so would the sum. A contradiction: the roots are not all real.
$\blacksquare$

**(d)** For $x^3-7x^2+17x+1=0$ we have $p=-7$, $q=17$:

$$p^2 = 49, \qquad 3q = 51, \qquad 49 < 51.$$

By part (c) at least one root is not real. $\blacksquare$

**(e)(i)** The condition $p^2 \ge 3q$ at $p=-7$ gives $q \le 16$. Run through the
integers $q$ from 1 to 16 on the calculator: up to $q=11$ all three roots are real,
and at $q=12$ only one is. Answer: $q = 12$.

**(e)(ii)** For a cubic with real coefficients the non-real roots come in conjugate
pairs, so there are 0 or 2 of them, and at least one root is always real.

```python
my13_sq = p**2 - 2*q
my13_dif = 2*p**2 - 6*q
my13_p2, my13_3q = 49, 51
my13_q = 12
```

**The marking.** (b)(i): M1 for squaring the sum, A1 for the expansion, A1 for the
result. (b)(ii): M1M1A1 likewise. (c): M1 for $2p^2-6q<0$, R1 for the conclusion.
(d): M1 for computing both numbers, A1 for the comparison and the conclusion.
(e)(i): M1 for the search, A1 for $q=12$. (e)(ii): R1.

**The main idea of the question.** Statement (c) is an implication one way. In part
(e) Noah believes the converse holds too: «if $p^2 \ge 3q$ then all the roots are
real». That is false, and $q=12$ is a counterexample: $49 \ge 36$ and the roots are
not all real. Realising that a counterexample is what is wanted is half the solution;
after that the calculator does the work.

**Why the converse could not have been true.** The condition $2p^2-6q \ge 0$ says
only that the *sum* of the squares of the differences is non-negative. For complex
numbers a square can be negative, and the terms are able to compensate for each
other. A one-sided criterion is an ordinary thing: it catches only the obvious
cases.

**Where the calculator is here.** Part (e)(i) is the only place in the topic where a
GDC does the work rather than checks it. Running through sixteen values by hand
would have taken all the time left.
""")

md(r"""
## Solution 14 — the Paper 3 investigation, the fourth degree

**(f)(i)** The same identity, only with four terms:

$$(\alpha+\beta+\gamma+\delta)^2 = \sum \alpha_i^2
+ 2\sum_{i<j}\alpha_i\alpha_j.$$

By Vieta the left-hand side is $p^2$ and the second sum is $q$, so

$$\alpha^2+\beta^2+\gamma^2+\delta^2 = p^2 - 2q. \qquad \blacksquare$$

**(f)(ii)** If $p^2 < 2q$, the sum of the squares is negative, which is impossible
for real numbers. The condition: $p^2 < 2q$.

**(g)** For $x^4-2x^3+3x^2-4x+5$: $p=-2$, $q=3$, so $p^2 = 4$ and $2q = 6$. Since
$4 < 6$, at least one root is not real. $\blacksquare$

**(h)(i)** For $x^4-9x^3+24x^2+22x-12$: $p=-9$, $q=24$, so $p^2 = 81$ and
$2q = 48$. Here $81 > 48$ and the criterion is silent — nothing can be concluded
from it.

**(h)(ii)** The candidates for integer roots are the divisors of the constant term:
$\pm1, \pm2, \pm3, \pm4, \pm6, \pm12$. Substitute $x=-1$:

$$1 + 9 + 24 - 22 - 12 = 0.$$

The integer root is $-1$.

**(h)(iii)** Divide by $(x+1)$; the remainder is zero and the quotient is

$$x^3 - 10x^2 + 34x - 12.$$

For that cubic $p=-10$, $q=34$, so $p^2 = 100$, $3q = 102$. Since $100 < 102$, by
part (c) the cubic factor has a non-real root — and therefore so does the quartic.
$\blacksquare$

```python
my14_sq = p**2 - 2*q
my14_p2, my14_2q = 4, 6
my14_root = -1
my14_quo, my14_rem = x**3 - 10*x**2 + 34*x - 12, 0
my14_pc2, my14_3qc = 100, 102
```

**The marking.** (f)(i): M1A1A1. (f)(ii): A1. (g): A1. (h)(i): A1 for the conclusion
«nothing can be said». (h)(ii): A1. (h)(iii): M1 for the factorisation, A1 for the
cubic factor, M1 for applying the criterion, A1 for the conclusion.

**A two instead of a three.** For a cubic the criterion is $p^2 < 3q$, for a quartic
$p^2 < 2q$. The number does not come out of nowhere: in the cubic case the sum of
the squares of the **differences** was compared (which brought the factor 2 and the
coefficient 6), while in the fourth degree it is the sum of the squares of the roots
directly, $p^2-2q$. Different identities, different constants. Substituting the
wrong number is the most frequent mistake in this question.

**Part (h)(i) is worth a mark for the word «nothing».** The answer «all the roots
are real» scores zero: the criterion is one-sided, and at $p^2 > 2q$ it asserts
nothing. Being able to say «that does not follow» is an exam skill of its own.

**Technique 1 inside Paper 3.** Part (h) is the ordinary factor theorem and division
inserted in the middle of an investigation. The whole of Paper 3 is built that way: a
long storyline made of short standard steps.
""")

md(r"""
## Solution 15 — two decompositions in one line

**(a)** Write the identity and multiply by $x(k-x)$:

$$\frac{1}{x(k-x)} = \frac ax + \frac{b}{k-x}
\;\Longrightarrow\; 1 = a(k-x) + bx.$$

Put $x=0$: $1 = ak$, hence $a = \frac1k$.
Put $x=k$: $1 = bk$, hence $b = \frac1k$.

$$\frac{1}{x(k-x)} = \frac{1}{kx} + \frac{1}{k(k-x)}.$$

**(b)** The denominator factorises: $1-4v^2 = (1-2v)(1+2v)$. Multiply:

$$1 = A(1+2v) + B(1-2v).$$

Put $v=\frac12$: $1 = 2A$, hence $A = \frac12$.
Put $v=-\frac12$: $1 = 2B$, hence $B = \frac12$.

$$\frac{1}{1-4v^2} = \frac{1}{2(1-2v)} + \frac{1}{2(1+2v)}.$$

```python
my15_a = 1/(k*x) + 1/(k*(k - x))
my15_b = Rational(1, 2)/(1 - 2*v) + Rational(1, 2)/(1 + 2*v)
```

**The marking.** (a): M1 for the identity after multiplying, M1 for the substitution
or for equating coefficients, A1 for both values. (b): M1A1.

**Why substitution is faster.** Equating coefficients in (a) gives the system
$-a+b=0$ and $ak=1$ — not hard either, but two steps instead of one. Substituting
$x=0$ and $x=k$ kills one term at a time. The rule: take the values that make the
denominators vanish.

**Where this leads.** Both blocks are the first parts of integration questions. In
the May 2021 block $\frac{1}{x(k-x)}$ is integrated next — the logistic equation
from E7; in the November 2025 block $\frac{1}{1-4v^2}$ in a problem about motion with
resistance. Partial fractions are almost never the goal; they are the first step.
""")

md(r"""
## Solution 16 — a repeated factor in the denominator

**(c)** Write the identity and multiply by $Q(x) = (x+1)(2x+1)$:

$$1 = A(2x+1) + B(x+1).$$

Put $x=-1$: $1 = -A$, hence $A = -1$.
Put $x=-\frac12$: $1 = \frac B2$, hence $B = 2$.

$$\frac{1}{Q(x)} = -\frac{1}{x+1} + \frac{2}{2x+1}.$$

**(d)** Notice that $(1+x)(2x+1)$ is the same $Q(x)$. So the expression equals

$$\frac{1 - \frac{x}{Q}}{Q} = \frac{Q - x}{Q^2}.$$

Compute the numerator: $Q - x = 2x^2+3x+1-x = 2x^2+2x+1$. The denominator is
$Q^2 = (x+1)^2(2x+1)^2$. Decompose into partial fractions; each repeated factor
gives two terms:

$$\frac{2x^2+2x+1}{(x+1)^2(2x+1)^2}
= \frac{2}{x+1} + \frac{1}{(x+1)^2} - \frac{4}{2x+1} + \frac{2}{(2x+1)^2}.$$

```python
my16_c = -1/(x + 1) + 2/(2*x + 1)
my16_d = 2/(x + 1) + 1/(x + 1)**2 - 4/(2*x + 1) + 2/(2*x + 1)**2
```

**The marking.** (c): M1 for the identity, M1 for the substitution or the system, A1
for $A$ and $B$. (d): M1 for using the result of (c), A1 for the outcome.

**A fast route to (d).** From (c) we know
$\frac1Q = -\frac1{x+1}+\frac2{2x+1}$. Then
$\frac{Q-x}{Q^2} = \frac1Q - \frac{x}{Q^2}$, and all that is left is squaring the
decomposition already known. That is how part (d) really is solved «hence», in two
lines — which is what (c) stands before it for.

**About repeated factors.** For $(x+1)^2$ in the denominator **both** terms are
needed, $\frac{A}{x+1}$ and $\frac{B}{(x+1)^2}$. If only the second is written, the
system turns out inconsistent — and that is a reliable sign of an omission, not a
reason to hunt for an arithmetic slip.

**About the archive's tags.** The right-hand side of this part is recorded there as
$1 - \frac4{2x+1} - \frac2{x+1} + \frac2{(2x+1)^2}$. Checking in sympy shows that
this is not equal to the left-hand side: $\frac2{x+1}$ should carry a plus, and
instead of the free one there should be $\frac1{(x+1)^2}$. The working is in the
technique card, section `corpus_issues`.
""")

md(r"""
## Solution 17 — the task on the timer

**(a)** For $g(x) = 2x^3-7x^2+dx-e$ the sum of the roots is $-\frac{-7}{2}$:

$$\alpha+\beta+\gamma = \frac72.$$

**(b)** The coefficients of $h$ are real, so together with $\rho+3i$ the number
$\rho-3i$ is a root as well. In all $h$ has five roots:
$\alpha, \beta, \gamma, \rho+3i, \rho-3i$. Their sum is $-\frac{-11}{2} = \frac{11}2$:

$$\frac72 + (\rho+3i) + (\rho-3i) = \frac{11}2
\;\Longrightarrow\; \frac72 + 2\rho = \frac{11}2
\;\Longrightarrow\; \rho = 1. \qquad \blacksquare$$

**(c)** The product of the five roots is $-\frac{-20}{2} = 10$. From
$h\!\left(\frac12\right)=0$ and the condition «$\gamma$ is rational» it follows that
$\gamma = \frac12$. The conjugate pair gives

$$(1+3i)(1-3i) = 1 + 9 = 10.$$

So

$$10 \cdot \alpha\beta \cdot \frac12 = 10 \;\Longrightarrow\; \alpha\beta = 2.$$

From (a) $\alpha+\beta = \frac72 - \frac12 = 3$. Numbers with sum 3 and product 2
are the roots of $u^2-3u+2=0$, that is, 1 and 2. Since $\alpha<\beta$, we get
$\alpha=1$, $\beta=2$. $\blacksquare$

```python
my17_sum = Rational(7, 2)
my17_rho = 1
my17_ab = 2
my17_alpha, my17_beta = 1, 2
```

**The marking.** (a): A1. (b): A1 for the conjugate root, M1 for the sum of the five
roots, A1 for $\rho=1$. (c): M1 for the product of the five roots, A1 for
$\alpha\beta=2$, A1 for the pair of values.

**How it looks in time.** Seven marks in twelve minutes, and almost all the time
goes on two careful applications of Vieta to a fifth degree. Not one root is found by
honestly solving an equation — nor could it be: $h$ is of the fifth degree with
three letters.

**The key move in (c).** Noticing that $\frac12$ is $\gamma$. The question says
«$\gamma$ is rational», while $\alpha,\beta$ are positive and real; the root
$\frac12$ from $h\left(\frac12\right)=0$ has to be one of the three, and the
rationality points at $\gamma$. Without that step the product cannot be split up.

**A check on the answer.** $\alpha+\beta+\gamma = 1+2+\frac12 = \frac72$ — it agrees
with part (a). Such a check takes five seconds and catches almost any arithmetic
slip in (c).
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

OUT = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a4-polynomials.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
