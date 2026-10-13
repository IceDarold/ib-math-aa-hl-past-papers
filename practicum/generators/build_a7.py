"""Собирает практикум A7 (доказательство: индукция, прямое, от противного) в .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

# --- эталонные ответы; каждый проверен в practicum/tests/verify_a7.py ---
#
# Их здесь мало, и это свойство темы, а не недоработка: в «prove that» ответ
# напечатан в условии, прятать нечего. Почти все проверки ниже сверяют переход
# и остаток, а не итог, и эталона не требуют.
ORDER8 = ['b', 'd', 'f', 'a', 'e', 'g', 'c']
D_ORDER8 = digest('|'.join(ORDER8))
D_MARKS8 = digest(sig(1, 6))

TRIGGER = {1: 'repr', 2: 'sum', 3: 'direct', 4: 'div', 5: 'contra', 6: 'deriv',
           7: 'contra', 8: 'rec', 9: 'ineq', 10: 'repr', 11: 'contra', 12: 'sum',
           13: 'direct', 14: 'rec', 15: 'ineq'}
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
# Practicum A7: proof — induction, direct, by contradiction

The most «paper» topic of the archive: **106 marks out of 160 are Paper 1**, and
another 48 fall on Paper 3, where the calculator is lying next to you but is useless
in the proof itself. There is nothing to compute here at all.

**Material.** 28 blocks and 160 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**What makes this topic different from all the others.** In every other practicum
the answer has to be found, and it can be hidden behind a hash. Here the answer is
**printed in the question**: «prove that», «show that», «hence show that». The marks
are not for the result but for the road to it and for how that road is written
down. Hence:

- the checks below confirm the **step** — that your working really does lead where
  you say it does;
- the check is not responsible for the part in words, and that is a matter of
  principle: an R1 is given for a sentence, and a notebook will not read it. What
  the solutions do carry is the wording from the markscheme — compare yours with it
  word for word;
- the theory sections say separately **where exactly two of the seven marks are
  free**, and why they get lost so regularly.

**How to work**

1. Read the map of techniques. The first three are proofs without induction, the
   fourth sets up the frame of induction, and the other five fill that frame in.
2. Work **on paper and in words**. That is not a pose here: half the marks are given
   for sentences rather than formulas.
3. Into the cell goes whatever came out of the key step. The check will say whether
   it leads to the required statement.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + factorial, binomial, exp, log and the rest

language('en')                 # this notebook is in English, and so are the checks

n, m, p, q, r, s = symbols('n m p q r s', integer=True)
al = Symbol('alpha', integer=True)
a, b, c = symbols('a b c')     # not integers: in task 2 a is an ordinary number

# k comes from kit and there is no need to redefine it: the induction checks work
# with that symbol by default, and Symbol('k', integer=True) is a different symbol.

print('ready; sympy', sp.__version__)
print('the factorial and the binomial are here:', factorial(k + 1), binomial(k + 1, 2))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Direct proof | «show that A = B», both sides written out | transform one side |
| 2 | Representing integers | «consecutive», «odd», «divisible by» | give the integer a letter: $2m+1$, $n-1$ |
| 3 | By contradiction | «prove that there is no», «never», «cannot» | write «suppose the opposite» |
| 4 | The skeleton of induction | «prove by induction» | the four compulsory lines |
| 5 | Induction for a sum | $\sum_{r=1}^{n}$ in the statement | split off the $(k+1)$-th term |
| 6 | Induction for divisibility | «divisible by $d$ for all $n$» | write the hypothesis as $=ds$ |
| 7 | Induction for the $n$-th derivative | $f^{(n)}(x)$, $\frac{d^n}{dx^n}$ | differentiate the hypothesis |
| 8 | Induction for a recursion | $u_{n+1}=\dots$, $f^{n}$, $I_n$ via $I_{n-1}$ | apply the recursion to the hypothesis |
| 9 | Induction for an inequality | «prove that $n > \dots$ for all $n$» | continue the chain from the hypothesis |

There is one ladder here, although it looks like two. Techniques 1–3 are proofs
without induction, and they come first not only because they are easier: **the
inductive step is itself a direct proof**, and technique 6 is built entirely on
technique 2. Without learning to write three lines without induction you will not
write the seven with it.

Techniques 5–9 differ from one another in exactly one thing: what they do to the
hypothesis. Add a term, subtract a multiple, differentiate, substitute into the
recursion, continue the inequality. Everything else in them is identical down to the
last comma — and that is good news, because «everything else» is worth two marks out
of seven.
""")

md(r"""
---
## Theory 1. Direct proof: where to go when the answer is already written

In a question «show that $A = B$» both sides are given. The temptation is to write
$A = B$, then transform both halves and be pleased when they meet. That must not be
done: you have started from what you were asked to prove.

The right form: **take one side and turn it into the other**, never once using the
equality you are proving. On the page it looks like a chain that starts with $A$ and
ends with $= B$.

Which side to take is a free choice, and the markscheme recognises that explicitly.
The statement «show that $(a+b)^2 - (a-b)^2 = 4ab$» is worked two ways: METHOD 1
expands both brackets on the left and collects terms, METHOD 2 sees a difference of
two squares on the left and factorises it into
$\bigl((a+b)+(a-b)\bigr)\bigl((a+b)-(a-b)\bigr)$. Both get full marks, and the
second is shorter. A practical rule: **start from the side with more going on in
it** — collapsing is easier than guessing an expansion.

One line from the markscheme worth remembering word for word: *«Do not award final
A1 unless all previous working is correct»*. The last mark in a direct proof is for
the chain meeting up as a whole. A missing sign in the middle takes off not one mark
but two.
""")

md(r"""
## Task 1 🟢 — a difference of two squares

Prove that the difference of the squares of two consecutive integers equals the sum
of those integers.

Take the numbers $n$ and $n+1$ and simplify $(n+1)^2 - n^2$. Into the cell put what
came out after simplifying — the check will compare it with the sum $n + (n+1)$.

*Source: May 2021 TZ2, Paper 1, Q1 (4 marks, no calculator).*
""")

code(r"""
my1 = ...                # the result of simplifying (n+1)^2 - n^2

verify_identity('Task 1', my1, n + (n + 1), var=n)
""")

md(r"""
## Task 2 🟢 — an identity with a fraction

Prove that for all $a \ne 0$

$$\left(\frac{a^2-1}{2a}\right)^2 + 1 = \left(\frac{a^2+1}{2a}\right)^2.$$

Expand the left-hand side, bring it to a single fraction and enter the result. It
should match the right-hand side.

*Source: November 2022, Paper 1, Q3(a) (3 marks, no calculator).*
""")

code(r"""
my2 = ...                # the left-hand side as a single fraction

verify_identity('Task 2', my2, ((a**2 + 1) / (2 * a))**2, var=a)
""")

md(r"""
---
## Theory 2. Representing integers: how to give a number a letter

Almost every statement in this topic is about «some» integer: an even one, an odd
one, three in a row. The proof begins by giving such a number a letter — and from
there it is ordinary algebra.

| Condition | How it is written |
| --- | --- |
| an arbitrary even number | $2m$ |
| an arbitrary odd number | $2m+1$ |
| three consecutive integers | $n-1,\; n,\; n+1$ |
| two consecutive ones | $n,\; n+1$ |
| a multiple of three | $3m$ |
| any integer, by remainder mod 3 | $3m,\; 3m+1,\; 3m+2$ |

An odd number of consecutive integers is more convenient written symmetrically, from
the middle: for five the sum $(n-2)+(n-1)+n+(n+1)+(n+2) = 5n$ comes out in one line,
while from $n, n+1, \ldots, n+4$ you would have to fuss with $5n+10$.

**The trap that costs a mark.** If the statement has two integers in it and they are
independent, they need **different letters**. Writing «let $a = 2m+1$ and
$b = 2m+1$» proves the statement only in the case $a = b$. The markscheme has a
separate A1 for that: *«Then $a = 2m+1$ and $b = 2n+1$»* — with different letters,
and it is not a quibble about presentation.

This mistake — and this one alone in the whole practicum — the check cannot catch,
and it is worth understanding why. Take a simpler statement: the sum of two odd
numbers is even. The writing $(2m+1)+(2m+1) = 4m+2$ gives an even number just as
well as the honest $(2m+1)+(2n+1) = 2(m+n+1)$: the arithmetic works out, because in
the special case $a = b$ the statement is indeed true. What is incomplete here is
the **reasoning**, and the completeness of reasoning cannot be computed from
remainders. Watch for it yourself.

**How a conclusion comes out of a representation.** You have brought the expression
to the form $5k^2 + 3$ — and then you say it in words: $5k^2$ is divisible by 5 and
3 is not, so the whole sum is never divisible by 5. That is the R1. Below,
`verify_residue` checks such conclusions: it runs through integer values and
confirms that the remainder really is always the same.
""")

md(r"""
## Task 3 🟢 — three in a row

Prove that the sum of any three consecutive integers is divisible by 3.

*Source: May 2022 TZ2, Paper 1, Q2(a) (2 marks, no calculator).*
""")

code(r"""
my3 = ...                # the simplified sum (n-1) + n + (n+1)

verify_identity('Task 3, the working', my3, (n - 1) + n + (n + 1), var=n)
verify_residue('Task 3, the conclusion', my3, 3, 0)
""")

md(r"""
## Task 4 🟡 — but the sum of the squares never is

Prove that the sum of the squares of three consecutive integers is **never**
divisible by 3.

The word «never» is the hint: bring it to the form «a multiple of three plus a
remainder» and show that the remainder is not zero. On the second line enter that
remainder.

*Source: May 2022 TZ2, Paper 1, Q2(b) (4 marks, no calculator).*
""")

code(r"""
my4 = ...                # the simplified sum (n-1)^2 + n^2 + (n+1)^2
rest4 = ...              # the remainder on division by 3

verify_identity('Task 4, the working', my4, (n - 1)**2 + n**2 + (n + 1)**2, var=n)
verify_residue('Task 4, the conclusion', my4, 3, rest4)
""")

md(r"""
---
## Theory 3. Proof by contradiction

The scheme is always the same:

1. **Suppose the opposite** — and write down what exactly is being supposed.
2. From that supposition, derive by working a statement that is plainly false.
3. So the supposition is wrong, and the original statement is true.

The first step is an M1, and it is awarded **for writing the supposition down**, not
for intending it. In the markscheme it looks literally like this: *«M1 for assuming
there exists some $\alpha \in \mathbb{Z}$ such that …»* — with the whole supposed
equality written out. Whoever started straight into the working did not get that
mark.

**Where the contradiction comes from.** Three sources appear in the archive, and it
is useful to know them in advance:

| Source | What it looks like | Example from the archive |
| --- | --- | --- |
| parity | one side is even, the other is not | $(2a+1)^2 = 2b$ |
| divisibility | the remainders do not match | $3(\dots)+1$ is not divisible by 3 |
| a sign or a bound | a square is negative, a value is below the minimum | $(2x-1)^2 < 0$ |

The third deserves a word of its own. In May 2025 the task was to prove that
$\frac{1}{x(1-x)} \ge 4$ for $0 < x < 1$. The markscheme gives **three** ways:
suppose $< 4$ and reduce it to $(2x-1)^2 < 0$; find the minimum through partial
fractions; find the minimum with the derivative. All three get full marks — a
contradiction may be mined wherever it is convenient, as long as the supposition is
written down and the conclusion drawn explicitly.

**The trap.** A proof does not end with a formula. A final sentence is needed: «this
is a contradiction, so the supposition is wrong». The last R1 is for it, and in
three questions out of four it is a mark of its own.
""")

md(r"""
## Task 5 🟡 — not both odd

The numbers $a$ and $b$ are integers, and $a^2 + b^2$ is divisible by 4. Prove that
$a$ and $b$ cannot both be odd.

Suppose the opposite, write both numbers with **different** letters, expand and
bring the result to the form «a multiple of four plus a remainder».

*Source: May 2022 TZ1, Paper 1, Q8 (6 marks, no calculator).*
""")

code(r"""
my5 = ...                # the expanded sum (2m+1)^2 + (2n+1)^2
rest5 = ...              # the remainder on division by 4

verify_identity('Task 5, the working', my5, (2 * m + 1)**2 + (2 * n + 1)**2, var=m)
verify_residue('Task 5, the conclusion', my5, 4, rest5)
""")

md(r"""
## Task 6 🔴 — an equation with no integer roots

Prove that the equation $2\alpha^3 + 6\alpha + 1 = 0$ has no integer roots.

Suppose that an integer root $\alpha$ exists and move the constant term to the
right. On the left there will be an expression whose parity is obvious, on the right
a number of the other parity.

*Source: May 2022 TZ2, Paper 1, Q9 (5 marks, no calculator).*
""")

code(r"""
left6 = ...              # the left-hand side after moving the term
right6 = ...             # the right-hand side after moving the term

verify_rewrite('Task 6, the rearrangement', left6, right6, 2 * al**3 + 6 * al + 1, var=al)
verify_residue('Task 6, on the left', left6, 2, 0)
verify_residue('Task 6, on the right', right6, 2, 1)
""")

md(r"""
## Task 7 🔴 — parity after a substitution

Prove that there are no integers $p$ and $q$ for which $p^2 - 8q - 11 = 0$.

There are two steps of reasoning in a row here. First, from $p^2 = 8q+11$ it follows
that $p^2$ is odd, and so $p$ itself is odd. Only after that does it make sense to
write $p = 2k+1$: there is no need to substitute $2k$ and $2k+1$ in turn, half the
cases have already been cut away.

Substitute, expand and bring it to an equality of two sides of different parity.

*Source: May 2023 TZ1, Paper 2, Q9 (6 marks, with a calculator — which is of no
help whatsoever here).*
""")

code(r"""
left7 = ...              # the left-hand side of the final equality
right7 = ...             # the right-hand side of the final equality

verify_rewrite('Task 7, the equivalence', left7, right7,
               (2 * k + 1)**2 - 8 * q - 11, var=k, factor=2)
verify_residue('Task 7, on the left', left7, 2, 0)
verify_residue('Task 7, on the right', right7, 2, 1)
""")

md(r"""
---
## Theory 4. The skeleton of induction, and where the marks are in it

From here half the practicum is about one single template. It is worth learning word
for word: it gives **two marks out of seven with no mathematics at all**, and those
two marks are lost more often than any others in the topic.

The four compulsory parts:

| Part | What is written | Mark |
| --- | --- | --- |
| **Base** | «at $n = 1$: the left-hand side $=\dots$, the right-hand side $=\dots$, they are equal» | R1 or A1 |
| **Hypothesis** | «suppose the statement is true for $n = k$, that is, $\dots$» | M1 |
| **Step** | «consider $n = k+1$» and the working to the required form | M1 + the A1s |
| **Conclusion** | «true for $n=1$; $P(k)$ implies $P(k+1)$; so it is true for all $n \in \mathbb{Z}^+$» | R1 |

Three remarks from the markscheme, each worth a mark:

**«M1 not awarded for mere "let $n = k$"».** The hypothesis has to be written out in
full, with the formula. The words «let $n = k$» are not a mark: you have supposed
nothing, you have renamed a letter.

**«Award R0 for not starting at $n = 2$».** The base is checked where the statement
begins. If the question says «for all $n \ge 2$», substituting $n = 1$ earns
nothing. In May 2021 the formula for $f^{(n)}$ only made sense from $n = 2$, and a
base at $n = 1$ scored zero.

**«Only award R1 if 4 of the previous 6 marks have been awarded».**
The final mark has a threshold. Writing the first and the last line and leaving the
middle empty will not do: a conclusion with no working is not credited. That note
stands in the markscheme of nearly every question in the topic.

Hence a practical conclusion that runs against intuition: **if the step does not
come out, write all four parts anyway.** The base and the hypothesis earn their
marks regardless of how the algebra ended.
""")

md(r"""
## Task 8 🟢 — assemble a proof out of lines

Below are seven lines of one proof by induction, shuffled. Put them in the right
order.

| Label | Line |
| --- | --- |
| **A** | substitute the hypothesis into the part singled out |
| **B** | check: at $n = 1$ the left-hand side equals the right-hand side |
| **C** | so it is true at $n = 1$, and $P(k)$ implies $P(k+1)$; by induction it is true for all $n \in \mathbb{Z}^+$ |
| **D** | suppose the statement is true for $n = k$, that is, $\dots$ |
| **E** | bring to a common denominator and simplify |
| **F** | consider $n = k+1$ and split off the sum of the first $k$ terms |
| **G** | this is exactly the statement at $n = k+1$ |

The second part is about the marking. The question is worth **7 marks**: A1 for the
base, M1 for the hypothesis, M1 for considering $n = k+1$, three A1s for the
working, R1 for the conclusion, and that last R1 is awarded only if four of the
previous six have been. How many marks does a script get in which **only lines B and
C** are written and there is no middle?
""")

code(r"""
my8 = ...                # for example ['A', 'B', 'C', 'D', 'E', 'F', 'G']
marks8 = ...             # how many marks out of 7

check_order('Task 8, the order', my8, '""" + D_ORDER8 + r"""', n=7)
check_num('Task 8, the marks', marks8, 6, '""" + D_MARKS8 + r"""')
""")

md(r"""
---
## Theory 5. Induction for a sum

The most frequent kind in the archive: 41 marks out of 112. The statement looks like

$$\sum_{r=1}^{n} a_r = S(n),$$

and the whole step is one line, worth remembering:

$$\sum_{r=1}^{k+1} a_r \;=\; \underbrace{\sum_{r=1}^{k} a_r}_{\text{the hypothesis goes here}} \;+\; a_{k+1}.$$

Split off the last term, put $S(k)$ in place of the sum — and from there it is pure
algebra: bring to a common denominator and recognise $S(k+1)$ in the result.

**Where people stumble.** Not on the idea but on the algebra with factorials. It is
useful to remember that the factorial of the next index comes by multiplication:
$(k+1)! = (k+1)\cdot k!$. So for two fractions whose denominators differ by one
index, the common denominator is the larger one, and the smaller fraction is
multiplied by exactly one factor, not by anything more complicated. Half the marks
lost in this technique are a multiplication «just in case» by a product of two
brackets.

**How to check yourself.** It pays to write the target expression $S(k+1)$ in the
margin **before** starting to simplify. Then you can see where to collapse to, and
you do not have to guess whether you have simplified enough. That is what
`verify_induction` does below: you enter what you got, and it compares it with
$S(k+1)$.
""")

md(r"""
## Task 9 🟢 — a sum with factorials

Prove by induction that for all $n \ge 1$

$$\sum_{r=1}^{n} \frac{r}{(r+1)!} = 1 - \frac{1}{(n+1)!}.$$

Into the cell put the expression you got after substituting the hypothesis and
splitting off the $(k+1)$-th term, and also the value of the left-hand side at
$n = 1$.

*Source: May 2023 TZ2, Paper 1, Q7 (7 marks, no calculator).*
""")

code(r"""
step9 = ...              # what came out in the step: S(k) + a_{k+1}
base9 = ...              # the left-hand side at n = 1

verify_induction('Task 9', step9, 1 - 1 / factorial(k + 1), base_lhs=base9)
""")

md(r"""
## Task 10 🟡 — a sum of binomial coefficients

Prove by induction that for all $n \in \mathbb{Z}^+$

$$\sum_{r=1}^{n} \binom{r}{1} = \binom{n+1}{2}.$$

The technique is the one from task 9, but the algebra goes through the factorials of
binomials. The markscheme gives two equally valid routes: cancel the factorials, or
go straight to a common denominator.

*Source: May 2024 TZ1, Paper 1, Q7 (7 marks, no calculator).*
""")

code(r"""
step10 = ...             # S(k) + the next term
base10 = ...             # the left-hand side at n = 1

verify_induction('Task 10', step10, binomial(k + 1, 2), base_lhs=base10)
""")

md(r"""
---
## Theory 6. Induction for divisibility

The statement «$E(n)$ is divisible by $d$ for all $n$» differs from a sum in that
there is no equality — and the hypothesis has to be written by you:

$$\text{suppose } E(k) = d\,s, \quad s \in \mathbb{Z}.$$

The letter $s$ is compulsory here: without it the hypothesis cannot be used.

Then the mechanics. Compute $E(k+1)$, and in it you have to **see $E(k)$**. For
that, $E(k+1)$ is split into a multiple of the hypothesis plus a remainder. On
$E(n) = 3^{2n} - 1$, which is divisible by 8:

$$3^{2(k+1)} - 1 = 9\cdot 3^{2k} - 1
= 9\underbrace{\left(3^{2k} - 1\right)}_{= \,8s} + 8 .$$

The factor 9 is not chosen at random: it is the coefficient with which $3^{2k}$ sits
inside $3^{2(k+1)}$, and after the hypothesis is taken out, exactly what is left of
the one remains. When there are two terms with exponents, the coefficient of either
will do: then one term disappears and the other stays in the remainder. The
markscheme recognises both routes (EITHER/OR), and so does the check below.

**What exactly is checked.** The remainder has to be divisible by $d$ **as an
expression**, that is, after dividing, integer coefficients must be left. The
requirement is not a formality: a difference may well be a multiple of $d$ at every
integer $k$ without it, but then it cannot be written as $d\cdot(\text{an integer})$
in one line, and there is no proof. The A1 in the markscheme is precisely for taking
$d$ outside the bracket.
""")

md(r"""
## Task 11 🟡 — divisibility by 17

Prove by induction that $5^{2n} - 2^{3n}$ is divisible by 17 for all
$n \in \mathbb{Z}^+$.

Enter the expression itself and the factor with which the hypothesis enters the
step.

*Source: November 2023 TZ1, Paper 1, Q6 (7 marks, no calculator). The same question
is repeated word for word in TZ2 of the same session.*
""")

code(r"""
expr11 = ...             # the expression E(n), written in terms of k
mult11 = ...             # the factor multiplying the hypothesis

verify_divisibility('Task 11', expr11, 17, mult11)
""")

md(r"""
---
## Theory 7. Induction for the $n$-th derivative

38 marks of the archive — more than divisibility and inequalities together. The
format is always the same: $f(x)$ is given, a formula for $f^{(n)}(x)$ is given,
prove it by induction.

The step here is simpler than in sums: **the hypothesis is differentiated**. If
$f^{(k)}(x) = g(k, x)$, then

$$f^{(k+1)}(x) = \frac{d}{dx}\,f^{(k)}(x) = \frac{d}{dx}\,g(k, x),$$

and what is left is to show that the result is $g(k+1, x)$.

**Two places where marks are lost.**

*The base.* What has to be checked is not $f(x)$ but the **first derivative**: the
statement about $f^{(n)}$ at $n = 1$ is $f'(x)$. And if the formula only makes sense
from $n = 2$ (in May 2021 that was the case), the base is taken at $n = 2$, else
R0.

*The algebra after differentiating.* The derivative comes out in an
«unrecognisable» form and has to be brought to a form with $k+1$. In questions with
factorials that is two or three A1s of its own: for example,
$\frac{(2k-1)!}{(k-1)!}$ is turned into $\frac{2(2k-3)!}{(k-2)!}$ by hand. Write the
target expression out in advance — without it there is no telling what to collapse
to.
""")

md(r"""
## Task 12 🟡 — the $n$-th derivative of a product

Prove by induction that for $f(x) = x^2 e^x$ and all $n \in \mathbb{Z}^+$

$$\frac{d^n}{dx^n}\left(x^2 e^x\right) = \left(x^2 + 2nx + n(n-1)\right)e^x.$$

In the step, differentiate the hypothesis with the product rule. Into the cell put
the result of the differentiation — simplifying it all the way is not necessary, the
check will compare it with the formula at $k+1$ itself.

*Source: November 2021, Paper 1, Q11(a) (7 marks, no calculator).*
""")

code(r"""
hyp12 = (x**2 + 2 * k * x + k * (k - 1)) * exp(x)     # the hypothesis: f^(k)(x)

step12 = ...             # the derivative of the hypothesis with respect to x
base12 = ...             # f'(x), that is, the left-hand side at n = 1

verify_induction('Task 12', step12, hyp12, base_lhs=base12)
""")

md(r"""
---
## Theory 8. Induction for a recursion

The last kind: a statement about $u_n$, $f^n$ or $I_n$, where the next term is
expressed through the previous one. The step is to apply the recursion to the
hypothesis.

The difference from the $n$-th derivative is only in which action is applied:

| What is given | The step |
| --- | --- |
| $u_{n+1} = g(u_n)$ | substitute the hypothesis into $g$ |
| $f^{n+1}(x) = f\!\left(f^{n}(x)\right)$ | substitute the hypothesis inside $f$ |
| $I_n$ via $I_{n-1}$ (integration by parts) | integrate by parts and recognise $I_{k}$ |

In the second case there is a fork: $f^{k+1} = f(f^k)$ or $f^{k+1} = f^k(f)$. The
May 2025 markscheme gives both as EITHER/OR — count the one in which the
substitution looks simpler. Usually that is the first: the outer $f$ is applied to a
ready expression rather than the other way round.

The third case is a pretty one: in May 2023 the task was to prove
$\int_0^{\infty} x^n e^{-x}\,dx = n!$. Integration by parts turns $I_{k+1}$ into
$(k+1)I_k$, the hypothesis gives $I_k = k!$, and together that is $(k+1)!$.
Induction here is not decoration but the only way: the recursion does not close up
without it.
""")

md(r"""
## Task 13 🔴 — the composition of a linear function

Let $f(x) = mx + c$, where $m \ne 1$. By $f^{n}$ we denote the $n$-fold composition
of $f$ with itself. Prove by induction that for all $n \in \mathbb{Z}^+$

$$f^{n}(x) = m^n x + \frac{c\left(1 - m^n\right)}{1 - m}.$$

In the step, apply $f$ to the hypothesis: $f^{k+1}(x) = f\!\left(f^{k}(x)\right)$.

*Source: May 2025 TZ3, Paper 3, Q1(c) (8 marks, with a calculator — but all the
work here is by hand).*
""")

code(r"""
hyp13 = m**k * x + c * (1 - m**k) / (1 - m)           # the hypothesis: f^k(x)

step13 = ...             # f applied to the hypothesis
base13 = ...             # f^1(x)

verify_induction('Task 13', step13, hyp13, base_lhs=base13)
""")

md(r"""
---
## Where the calculator is in this topic

The short answer: **nowhere**. And this is the only topic of the archive about which
that can be said without reservations.

Formally the «with a calculator» share here is 34%, but the breakdown explains the
figure completely:

| Paper | Marks | Calculator |
| --- | --- | --- |
| Paper 1 | 106 | none |
| Paper 3 | 48 | lying next to you |
| Paper 2 | 6 | lying next to you |

All 48 marks of Paper 3 are parts `(c)`, `(f)` of long investigations, where the
calculator is needed in the neighbouring parts while the proof itself is written by
hand. The single Paper 2 question is the proof by contradiction about
$p^2 - 8q - 11$, where there is nothing to compute either.

**What the calculator does do — before the proof, not instead of it:**

- *check the statement at a couple of values of $n$.* If the formula does not work
  at $n = 3$, there is nothing to prove — look for the mistake in the question or in
  your own writing of it;
- *disprove.* For «disprove» one counterexample is enough, and finding one is
  something a calculator is excellent at;
- *check the arithmetic of the base.* Put $n = 1$ into a divisibility statement and
  confirm that the number really is divisible — three seconds and one guaranteed
  mark.

What it never does: **checking at $n = 1, \dots, 100$ is not a proof.** The
statement that $n^2 + n + 41$ is prime gives primes for every $n$ from 0 to 39 and a
composite number at $n = 40$. That is where the whole topic comes from.
""")

code(r"""
# what a calculator can do: check a formula before you prove it
formula = 1 - 1 / factorial(n + 1)
for i in range(1, 6):
    left = sum(Rational(j, factorial(j + 1)) for j in range(1, i + 1))
    print(f'n = {i}:  sum = {left},  formula = {formula.subs(n, i)},'
          f'  {"agrees" if left == formula.subs(n, i) else "DOES NOT agree"}')

print()
# and what it cannot: agreement in the first few values proves nothing
bad = n**2 + n + 41
print('n^2 + n + 41 at n = 0..5:', [bad.subs(n, i) for i in range(6)],
      '— all prime')
print('and at n = 40:', bad.subs(n, 40), '= 41 * 41')
""")

md(r"""
---
## Trainer: name the technique

The technique is chosen before anything is written. For each statement, name the
technique with one code:

`direct` · `repr` · `contra` · `sum` · `div` · `deriv` · `rec` · `ineq`

| # | Statement |
| --- | --- |
| 1 | Prove that the sum of three consecutive integers is divisible by 3 |
| 2 | Prove by induction that $\sum_{r=1}^{n} r\cdot r! = (n+1)! - 1$ |
| 3 | Show that $(a+b)^2 - (a-b)^2 = 4ab$ |
| 4 | Prove that $7^n - 4^n$ is divisible by 3 for all $n \in \mathbb{Z}^+$ |
| 5 | Prove that $\sqrt{2}$ is irrational |
| 6 | Prove by induction that $\frac{d^n}{dx^n}(xe^x) = (x+n)e^x$ |
| 7 | Prove that $x^3 + x + 1 = 0$ has no rational root |
| 8 | $u_{n+1} = 3u_n + 1$, $u_1 = 1$. Prove that $u_n = \frac{3^n - 1}{2}$ |
| 9 | Prove that $n! > 2^n$ for all $n \ge 4$ |
| 10 | Show that the sum of the squares of two consecutive integers is odd |
| 11 | Prove that if $n^2$ is even then $n$ is even |
| 12 | Prove by induction that $\sum_{r=1}^{n} \frac{1}{r(r+1)} = \frac{n}{n+1}$ |
| 13 | Show that $\cos^3\theta = \frac{3\cos\theta + \cos 3\theta}{4}$ |
| 14 | $f(x) = \frac{x}{1+x}$. Prove that $f^{n}(x) = \frac{x}{1+nx}$ |
| 15 | Prove that $2^n > n^2$ for all $n \ge 5$ |
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
## Task 14 🔴 — ON THE TIMER: 8 minutes

A whole exam format. Set a timer and write on paper, including all the parts in
words.

**(a)** Show that $1 + \log_2 k \ge \log_2(k+1)$ for all $k \in \mathbb{Z}^+$.

**(b)** Prove by induction that $n > \log_2 n$ for all $n \in \mathbb{Z}^+$.

A hint for (b): adding one to the hypothesis $k > \log_2 k$ gives
$k + 1 > 1 + \log_2 k$, and then part (a) comes in. This is the only step in the
practicum where induction works with an inequality, and the chain is assembled out
of two links.

Into the cell put the left-hand side of the inequality from part (a), written as a
single logarithm.

*Source: May 2025 TZ1, Paper 1, Q8 (5 marks for part (b), no calculator).*
""")

code(r"""
# set a timer for 8 minutes

my14 = ...               # 1 + log_2(k), written as a single logarithm

verify_identity('Task 14', my14, log(2 * k) / log(2), var=k,
                samples=(1, 2, 3, 5, 8, 13))

# and the inequality 2k >= k+1 for k >= 1 is checked in one line
print('2k - (k+1) at k = 1..5:', [(2 * i - (i + 1)) for i in range(1, 6)])
""")

md(r"""
### Attempt log

Fill it in after checking against the solution — one line per part.

| Part | In time | Technique named right | What cost a mark |
| --- | --- | --- | --- |
| (a) |  |  |  |
| (b) |  |  |  |

For this topic the log is worth an extra column: **were all four parts of the
induction written in words.** The algebra here goes wrong less often than the pen
forgets the conclusion.
""")

md(r"""
---
# 🔑 Solutions

What follows are the worked solutions. Read them after you have solved: peeking is
more harmful in proofs than anywhere else, because «I got the idea» and «I can write
it down» are different skills here, and the marks are for the second.
""")

md(r"""
## Solution 1 — a difference of two squares

Take two consecutive integers $n$ and $n+1$ and compute the difference of the
squares **in the right order** — the larger minus the smaller:

$$(n+1)^2 - n^2 = n^2 + 2n + 1 - n^2 = 2n + 1.$$

What is left is to recognise the sum of the original numbers in $2n+1$:

$$2n + 1 = n + (n+1). \qquad \blacksquare$$

The second route from the markscheme — factorise the difference of two squares
straight away:

$$(n+1)^2 - n^2 = \bigl((n+1) - n\bigr)\bigl((n+1) + n\bigr) = 1\cdot(2n+1).$$

```python
my1 = 2*n + 1
```

**The marking.** M1 for attempting to subtract the squares, A1A1 for the right order
and the right expansion (or for the right factorisation), A1 for the final line
$= n + (n+1)$. The markscheme note: the last A1 is not awarded if anything above it
is wrong.

**Where marks are lost.** The order of the subtraction.
$n^2 - (n+1)^2 = -(2n+1)$ — and there is nothing left to prove.
""")

md(r"""
## Solution 2 — an identity with a fraction

Expand the left-hand side, as METHOD 1 suggests:

$$\left(\frac{a^2-1}{2a}\right)^2 + 1
= \frac{a^4 - 2a^2 + 1}{4a^2} + \frac{4a^2}{4a^2}
= \frac{a^4 + 2a^2 + 1}{4a^2}.$$

The numerator is a perfect square:

$$\frac{\left(a^2+1\right)^2}{4a^2} = \left(\frac{a^2+1}{2a}\right)^2. \qquad \blacksquare$$

```python
my2 = (a**4 + 2*a**2 + 1) / (4*a**2)
```

**The marking.** M1 for attempting to expand, A1 for bringing it to the common
denominator $4a^2$, A1 for collapsing into a square.

**On the choice of side.** METHOD 2 in the markscheme goes from the right-hand side
and arrives at the left — the same three marks. Note that the one has to be written
as $\frac{4a^2}{4a^2}$: that is the step the A1 is given for.
""")

md(r"""
## Solution 3 — three in a row

Call the middle term $n$; then the three consecutive integers are $n-1$, $n$,
$n+1$. Their sum:

$$(n-1) + n + (n+1) = 3n,$$

and $3n$ is divisible by 3 for any integer $n$. $\blacksquare$

```python
my3 = 3*n
```

**The marking.** A1 for writing the sum, A1 for $3n$ with the conclusion «divisible
by 3». Two marks in all — and both go almost for free if you start with $n$, $n+1$,
$n+2$: the sum $3n+3$ is divisible by 3 as well, but the extra step of taking the
three out gives an extra chance to go wrong.
""")

md(r"""
## Solution 4 — the sum of the squares is never divisible by 3

The same three numbers, but squared:

$$(n-1)^2 + n^2 + (n+1)^2
= n^2 - 2n + 1 + n^2 + n^2 + 2n + 1 = 3n^2 + 2.$$

The term $3n^2$ is divisible by 3 and 2 is not. So on division by 3 the sum always
leaves remainder 2 and is never divisible by 3. $\blacksquare$

```python
my4 = 3*n**2 + 2
rest4 = 2
```

**The marking.** A1 for writing the sum, M1 for expanding at least one square, A1
for $3n^2+2$, R1 for the conclusion about the remainder. The last mark is the one in
words, and it is worth a quarter of the question.

**Why this is not induction.** The statement is about «all $n$», and there is no
induction: representing three consecutive integers covers every case at once.
Induction is needed where the $n$-th statement leans on the $(n-1)$-th, and here
each one stands by itself.
""")

md(r"""
## Solution 5 — not both odd

**Suppose the opposite:** let $a$ and $b$ both be odd. Then there are integers $m$
and $n$ such that $a = 2m+1$, $b = 2n+1$ — **different** letters, because the
numbers are independent.

$$a^2 + b^2 = (2m+1)^2 + (2n+1)^2 = 4m^2 + 4m + 1 + 4n^2 + 4n + 1
= 4\left(m^2 + m + n^2 + n\right) + 2.$$

The first term is divisible by 4, the second is not. So on division by 4 the number
$a^2+b^2$ leaves remainder 2 and is not divisible by 4. That contradicts the
question, so the supposition is wrong: $a$ and $b$ cannot both be odd.
$\blacksquare$

```python
my5 = 4*(m**2 + m + n**2 + n) + 2
rest5 = 2
```

**The marking.** M1 for the supposition itself, A1 for $a = 2m+1$, $b = 2n+1$, A1
for the expansion, (A1) for collapsing to $4(\dots)+2$, R1 for «divisible by 4, and
2 is not», R1 for the word «contradiction». **Two of the six marks are for two
sentences.**

**Where marks are lost.** One letter for both numbers. And the final sentence:
stopping at $4(\dots)+2$ means not getting the last R1.
""")

md(r"""
## Solution 6 — an equation with no integer roots

**Suppose** there exists an integer $\alpha$ with $2\alpha^3 + 6\alpha + 1 = 0$.
Rearranging:

$$2\alpha^3 + 6\alpha = -1.$$

On the left, $2\left(\alpha^3 + 3\alpha\right)$ — an even number for any integer
$\alpha$. On the right, $-1$ — odd. An even number does not equal an odd one: a
contradiction. So there are no integer roots. $\blacksquare$

```python
left6 = 2*al**3 + 6*al
right6 = -1
```

**The marking.** M1 for the supposition, M1 for attempting to rearrange, A1 for the
correct $2\alpha^3+6\alpha = -1$, R1 for «the left-hand side is even», R1 for the
contradiction.

**The second route.** The markscheme also accepts the analysis through the
derivative: $f'(x) = 6x^2 + 6 > 0$, so $f$ is strictly increasing and there is one
root; $f(-1) = -7$, $f(0) = 1$, so it lies strictly between $-1$ and $0$, and there
are no integers there. Five marks as well. Worth noticing: here the contradiction is
mined from bounds rather than from parity — and both times the task is the same
one.
""")

md(r"""
## Solution 7 — parity after a substitution

**Suppose** there are integers $p$ and $q$ with $p^2 - 8q - 11 = 0$, that is,

$$p^2 = 8q + 11.$$

**The first step of the reasoning.** The right-hand side is $2(4q+5)+1$ — odd, so
$p^2$ is odd, and so $p$ is odd. That is an R1 of its own, and without it the
substitution $p = 2k+1$ is unjustified.

**The second step.** Let $p = 2k+1$, $k \in \mathbb{Z}$:

$$(2k+1)^2 = 8q + 11 \;\Longrightarrow\; 4k^2 + 4k + 1 = 8q + 11
\;\Longrightarrow\; 4k^2 + 4k = 8q + 10.$$

Divide by 2:

$$2k^2 + 2k = 4q + 5.$$

The left-hand side is even, the right-hand side odd — a contradiction. So no such
integers $p$ and $q$ exist. $\blacksquare$

```python
left7 = 2*k**2 + 2*k
right7 = 4*q + 5
```

**The marking.** M1 for the supposition, R1 for the conclusion «$p$ is odd», M1 for
$p = 2k+1$, (A1) for the substitution, A1 for the equality with different parities,
R1 for the contradiction.

**Why the check has `factor=2`.** Dividing by 2 is a legitimate step, but after it
the equality no longer matches the original literally. Multiplying back returns you
to $(2k+1)^2 - 8q - 11$, and that is how it is checked that nothing was lost along
the way.

**Where marks are lost.** Skipping the first step. Without it you have to treat
$p = 2k$ separately — not an error, but an extra half of the work, and on Paper 2
the time is counted.
""")

md(r"""
## Solution 8 — assemble a proof out of lines

The right order: **B → D → F → A → E → G → C**.

| Place | Label | What it is |
| --- | --- | --- |
| 1 | B | the base |
| 2 | D | the hypothesis |
| 3 | F | considering $n = k+1$ |
| 4 | A | substituting the hypothesis |
| 5 | E | the algebra |
| 6 | G | the statement at $k+1$ recognised |
| 7 | C | the conclusion |

The boundaries are rigid: the base is always first, the conclusion always last, and
the hypothesis has to stand before its own substitution. Inside the working (E) the
order is free, but G has to come after it — otherwise you are announcing the result
before you have got it.

**On the marks: the answer is 1.**

Line B is the A1 for the base, and it is awarded. Line C is the R1 for the
conclusion, and it is **not**: the markscheme requires four of the previous six
marks, and one has been earned. One mark out of seven in total.

```python
my8 = ['B', 'D', 'F', 'A', 'E', 'G', 'C']
marks8 = 1
```

**Why know this.** It gives a rule that runs against intuition. The threshold
applies only to the final R1; the base and the hypothesis have no thresholds. So if
the step does not come out, you should still write the base, the hypothesis and
«consider $n = k+1$» — that is A1 + M1 + M1, three marks out of seven for
remembering the template. Empty space gives nothing.
""")

md(r"""
## Solution 9 — a sum with factorials

**Base.** At $n = 1$ the left-hand side is $\frac{1}{2!} = \frac{1}{2}$ and the
right-hand side $1 - \frac{1}{2!} = \frac{1}{2}$. Equal.

**Hypothesis.** Suppose that at $n = k$

$$\sum_{r=1}^{k} \frac{r}{(r+1)!} = 1 - \frac{1}{(k+1)!}.$$

**Step.** Split off the last term and substitute the hypothesis:

$$\sum_{r=1}^{k+1} \frac{r}{(r+1)!}
= \left(1 - \frac{1}{(k+1)!}\right) + \frac{k+1}{(k+2)!}.$$

The common denominator is $(k+2)! = (k+2)(k+1)!$:

$$= 1 - \frac{k+2}{(k+2)!} + \frac{k+1}{(k+2)!}
= 1 - \frac{(k+2) - (k+1)}{(k+2)!}
= 1 - \frac{1}{(k+2)!},$$

and that is exactly the statement at $n = k+1$.

**Conclusion.** True at $n = 1$; the truth at $n = k$ implies the truth at
$n = k+1$; so by induction it is true for all $n \ge 1$. $\blacksquare$

```python
step9 = 1 - 1/factorial(k + 1) + (k + 1)/factorial(k + 2)
base9 = Rational(1, 2)
```

**The marking.** R1 base, M1 hypothesis, (M1) for splitting the sum, A1 for the
substitution, A1 for the intermediate simplification, A1 for the final form, R1
conclusion (any four of the previous marks needed).

**The key place** is $(k+2)! = (k+2)(k+1)!$. Without that equality the fractions do
not add and the work comes to a halt.
""")

md(r"""
## Solution 10 — a sum of binomial coefficients

**Base.** At $n = 1$: on the left $\binom{1}{1} = 1$, on the right
$\binom{2}{2} = 1$.

**Hypothesis.** $\sum_{r=1}^{k} \binom{r}{1} = \binom{k+1}{2}$.

**Step.**

$$\sum_{r=1}^{k+1} \binom{r}{1} = \binom{k+1}{2} + \binom{k+1}{1}
= \frac{(k+1)k}{2} + (k+1) = \frac{(k+1)(k+2)}{2} = \binom{k+2}{2}.$$

That is the statement at $n = k+1$. $\blacksquare$

```python
step10 = binomial(k + 1, 2) + binomial(k + 1, 1)
base10 = 1
```

**The marking.** R1 base, M1 hypothesis, M1 for splitting the sum, A1 for
$\binom{k+1}{2} + \binom{k+1}{1}$, M1 for the simplification (by either of the
markscheme's routes), A1 for $\binom{k+2}{2}$, R1 conclusion.

**What is really going on.** $\binom{r}{1} = r$, so what is being proved is the
familiar $1 + 2 + \dots + n = \frac{n(n+1)}{2}$, only written binomially. Noticing
that is useful as a check on yourself, but **it is not worth writing in the
answer**: the question asks for induction, and switching to the formula for the sum
of an arithmetic sequence does not replace it.

**The identity behind the scenes.** The step
$\binom{k+1}{2} + \binom{k+1}{1} = \binom{k+2}{2}$ is Pascal's rule. Knowing it is
not compulsory, the factorials give the same thing, but with it the line comes out in
one move.
""")

md(r"""
## Solution 11 — divisibility by 17

**Base.** At $n = 1$: $5^2 - 2^3 = 25 - 8 = 17$, divisible by 17.

**Hypothesis.** Suppose that at $n = k$

$$5^{2k} - 2^{3k} = 17s, \quad s \in \mathbb{Z}.$$

**Step.**

$$5^{2(k+1)} - 2^{3(k+1)} = 25\cdot 5^{2k} - 8\cdot 2^{3k}.$$

Add and subtract $8\cdot 5^{2k}$ to collect the hypothesis:

$$= 8\left(5^{2k} - 2^{3k}\right) + 17\cdot 5^{2k}
= 8\cdot 17s + 17\cdot 5^{2k}
= 17\left(8s + 5^{2k}\right).$$

The bracket is an integer, so the expression is divisible by 17. $\blacksquare$

```python
expr11 = 5**(2*k) - 2**(3*k)
mult11 = 8
```

**The marking.** A1 base, M1 hypothesis, M1 for considering $n = k+1$, A1 for
expanding the powers, A1 for $17s$ appearing, A1 for taking the 17 out, R1
conclusion (4 of the 6 needed).

**The second route.** The hypothesis can be collected with the factor 25:

$$25\cdot 5^{2k} - 8\cdot 2^{3k} = 25\left(5^{2k} - 2^{3k}\right) + 17\cdot 2^{3k}.$$

The check accepts `mult11 = 25` too — the markscheme gives both as EITHER/OR.

**Why only those two factors work.** Take, say, 1: you get
$24\cdot 5^{2k} - 7\cdot 2^{3k}$. That number **really is** a multiple of 17 at
every integer $k$ — but the factor 17 cannot be seen in such a writing, it cannot be
taken outside a bracket, and there is no proof. The check looks for exactly that:
after dividing by 17, integer coefficients have to be left.

**A small point about notation.** $5^{2k} = 25^k$ and $2^{3k} = 8^k$; the markscheme
allows either form. With $25^k - 8^k$ the step is sometimes quicker to see:
$25^{k+1} - 8^{k+1} = 25\cdot 25^k - 8\cdot 8^k$, and then the same thing.
""")

md(r"""
## Solution 12 — the $n$-th derivative of a product

**Base.** At $n = 1$ the left-hand side is $f'(x)$:

$$\frac{d}{dx}\left(x^2 e^x\right) = 2x e^x + x^2 e^x = \left(x^2 + 2x\right)e^x.$$

The right-hand side at $n = 1$: $\left(x^2 + 2\cdot 1\cdot x + 1\cdot 0\right)e^x
= \left(x^2+2x\right)e^x$. They match.

**Hypothesis.** At $n = k$:
$\;\dfrac{d^k}{dx^k}\left(x^2e^x\right) = \left(x^2 + 2kx + k(k-1)\right)e^x$.

**Step.** Differentiate the hypothesis with the product rule:

$$\frac{d^{k+1}}{dx^{k+1}}\left(x^2e^x\right)
= \frac{d}{dx}\left[\left(x^2 + 2kx + k(k-1)\right)e^x\right]
= (2x + 2k)e^x + \left(x^2 + 2kx + k(k-1)\right)e^x.$$

Collect:

$$= \left(x^2 + 2kx + 2x + 2k + k(k-1)\right)e^x
= \left(x^2 + 2(k+1)x + (k+1)k\right)e^x,$$

and that is the formula at $n = k+1$. $\blacksquare$

```python
step12 = diff(hyp12, x)
base12 = diff(x**2 * exp(x), x)
```

**The marking.** A1 for the left-hand side of the base, A1 for the right-hand side,
M1 for the hypothesis, M1 for differentiating, A1A1 for bringing it to the form with
$k+1$, R1 conclusion.

**The key place** is recognising $(k+1)k$ in $2k + k(k-1)$:

$$2k + k^2 - k = k^2 + k = k(k+1).$$

Without that collapse the formula at $k+1$ is not visible, and the last A1s are not
awarded.

**About the base.** Check the **first derivative**, not the function itself. In May
2021 a similar question had a formula that only made sense from $n = 2$, and the
markscheme warns directly: *«Award R0 for not starting at $n = 2$»*. The first thing
to look at is which $n$ the statement is actually stated from.
""")

md(r"""
## Solution 13 — the composition of a linear function

**Base.** At $n = 1$ the formula gives
$m^1 x + \frac{c(1-m^1)}{1-m} = mx + c = f(x)$. True.

**Hypothesis.** At $n = k$:
$\;f^{k}(x) = m^k x + \dfrac{c\left(1-m^k\right)}{1-m}$.

**Step.** Apply $f$ to the hypothesis:

$$f^{k+1}(x) = f\!\left(f^{k}(x)\right)
= m\left(m^k x + \frac{c\left(1-m^k\right)}{1-m}\right) + c
= m^{k+1}x + \frac{cm\left(1-m^k\right)}{1-m} + c.$$

Bring the last two terms to a common denominator:

$$\frac{cm - cm^{k+1} + c(1-m)}{1-m}
= \frac{cm - cm^{k+1} + c - cm}{1-m}
= \frac{c\left(1 - m^{k+1}\right)}{1-m}.$$

So $f^{k+1}(x) = m^{k+1}x + \frac{c\left(1-m^{k+1}\right)}{1-m}$ — the formula at
$n = k+1$. $\blacksquare$

```python
step13 = m*hyp13 + c
base13 = m*x + c
```

**The marking.** R1 base, M1 hypothesis, M1 for $f(f^k(x))$, A1 for the
substitution, M1 for the common denominator, A1 for the collapse, A1 for the final
form, R1 conclusion.

**The fork.** The markscheme gives EITHER $f\!\left(f^k(x)\right)$ OR
$f^k\!\left(f(x)\right)$ — both M1. The first is usually shorter: the outer $f$ is
linear, and the substitution comes down to «multiply by $m$, add $c$». The second
requires substituting $mx+c$ for $x$ inside a bulky formula.

**A third route from the markscheme** — recognise a geometric sequence:
$f^{n}(x) = m^n x + c\left(1 + m + \dots + m^{n-1}\right)$, and the sum in the
bracket equals $\frac{1-m^n}{1-m}$. That also shows, incidentally, where the
condition $m \ne 1$ in the question came from: at $m = 1$ the denominator vanishes,
while the composition itself gives $f^n(x) = x + nc$.
""")

md(r"""
## Solution 14 — the task on the timer

**(a)** One is $\log_2 2$, so

$$1 + \log_2 k = \log_2 2 + \log_2 k = \log_2 (2k).$$

For $k \ge 1$ we have $2k \ge k+1$ (which is equivalent to $k \ge 1$), and $\log_2$
is increasing, so

$$\log_2(2k) \ge \log_2(k+1), \quad\text{that is,}\quad
1 + \log_2 k \ge \log_2(k+1). \qquad \blacksquare$$

**(b) Base.** At $n = 1$: $\log_2 1 = 0$ and $1 > 0$. True.

**Hypothesis.** At $n = k$: $\;k > \log_2 k$.

**Step.** Add one to both sides:

$$k + 1 > 1 + \log_2 k.$$

By part (a) the right-hand side is at least $\log_2(k+1)$, so

$$k + 1 > 1 + \log_2 k \ge \log_2(k+1)
\;\Longrightarrow\; k+1 > \log_2(k+1),$$

and that is the statement at $n = k+1$.

**Conclusion.** True at $n = 1$; $n = k$ implies $n = k+1$; so it is true for all
$n \in \mathbb{Z}^+$. $\blacksquare$

```python
my14 = log(2*k)/log(2)
```

**The marking of (b).** R1 for the base, M1 for the hypothesis, M1 for
$k+1 > 1 + \log_2 k$, A1 for applying part (a), R1 for the conclusion. Five marks.

**What is special here.** The only case in the topic where the hypothesis is an
inequality. The mechanics are the same, but **two** relations have to be joined: the
strict $>$ from the hypothesis and the non-strict $\ge$ from part (a). The chain
$a > b \ge c$ gives $a > c$ — the strictness survives, and that is worth checking
with your eyes before writing the conclusion.

**What part (a) is for.** It is not decoration: without it there is no way to get
$k+1 > \log_2(k+1)$ from $k+1 > 1 + \log_2 k$. The word «hence» in a question always
means that the previous part must be used — and its absence costs an A1.
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

OUT = os.path.join(ROOT, 'practicum/number_algebra', 'practicum-a7-proof.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
