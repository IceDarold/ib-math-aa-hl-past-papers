"""Собирает практикум A1: арифметические прогрессии и суммы.

Одиннадцатый практикум серии на английском и первый в секции A из тех,
где тема корпуса берётся не целиком: в number_algebra.sequences лежат обе
прогрессии сразу, и разрез между A1 и A2 идёт по вопросу, а не по теме.

Лестница из девяти приёмов идёт по тому, что в задаче неизвестно.
Сначала прогрессия известна, а спрашивают её член или сумму. Потом
наоборот: член и сумма даны, а прогрессию ищут — и почти всегда это
система из двух линейных уравнений на u₁ и d. Потом прогрессия
перестаёт быть списком и становится условием: «эти три величины
образуют арифметическую последовательность» — уравнение на букву,
которая в них сидит. Напоследок три случая, где номер обязан быть
целым, сумма — наибольшей, а члены оказываются логарифмами.

Проверка здесь одна новая, и она же шестнадцатое понятие равенства
ответов в серии: **последовательность порождается**.

Эталона нет. Ноутбук передаёт проверке не ответ и не формулу, а правило:
первый член и шаг. `verify_term` доходит до нужного члена сложением,
`verify_total` складывает первые n членов, `verify_peak` перебирает
частичные суммы. Ни u₁ + (n − 1)d, ни n/2(2u₁ + (n − 1)d) внутри
проверки не написано ни разу, и потому 2n + 3, 5 + 2(n − 1) и n + (n + 3)
проходят одинаково.

Работает в обе стороны, и в этой теме обратный ход — половина заданий.
Прямой: прогрессия известна, ответ — её член. Обратный: член известен
из условия, а прогрессию строят из ответа, и она обязана этому члену
отвечать. Так проверяется «найдите первый член и общую разность» —
самый частый вопрос темы, у которого ответов два и оба в одной строке.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_a1.py прогоняет по нему весь ноутбук
и требует, чтобы каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/number_algebra/practicum-a1-arithmetic-sequences.ipynb')

TRIGGER = {1: 'term', 2: 'sum', 3: 'two', 4: 'back', 5: 'difference',
           6: 'coefficients', 7: 'peak', 8: 'integer', 9: 'log',
           10: 'two', 11: 'sum', 12: 'difference'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '12',
    'q1b': '16',
    'q1c': '-3',
    'q2d': '-6',
    'q2a': '-36',
    'q2b': '13',
    'q3r': '3*n - 1',
    'q3a': '15',
    'q3b': '26',
    'q4u': '-6',
    'q4d': '2',
    'q5u': '-12',
    'q5d': '3',
    'q6p': '3',
    'q6q': '2',
    'q6b': '25',
    'q7a': '45',
    'q7b': '15',
    'q7c': '5',
    'q7d': '2*n + 3',
    'q8k': 'Rational(4, 5)',
    'q8u': '7',
    'q9p': '5',
    'q9t': '[9, 5, 1, -3]',
    'q9d': '4*pi',
    'q10d': 'Rational(-3, 2)',
    'q10c': '-m**2/(m + 2)',
    'q10f': '[-4*x + 8, -3*x + 9]',
    'q11k': '25',
    'q11s': '750',
    'q12r': '3*n - 2',
    'q12t': '210',
    'q12i': '20',
    'q12j': '12',
    'q12n': '13',
    'q12k': '5',
    'q13d': '-4 - ln(3)',
    'q13s': '-90 - 25*ln(3)',
    'qt_p': 'Rational(2, 3)',
    'qt_d': '-ln(x)/3',
    'qt_n': '9',
}

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
# A1 — Arithmetic sequences and sums

**135 marks of the archive, nine techniques, thirteen tasks.** Everything
the archive asks about arithmetic sequences — the terms, the sums, and
the three Paper 3 investigations built on top of them.

## The one idea

An arithmetic sequence is not a formula. It is one sentence:

> **From each term to the next you add the same thing.**

Everything in the topic comes out of that sentence in one line, and
coming out is quicker than remembering.

$$u_n=u_1+(n-1)d$$

reads *"you have added $d$ exactly $n-1$ times"*. The $-1$ is not a
quirk of the notation; it is the count of steps. Between the first term
and the seventh there are six steps, not seven, and that off-by-one is
the single most expensive slip in the topic.

$$S_n=\frac n2\,(u_1+u_n)$$

is the story about Gauss. Write the sum forwards, write it again
backwards underneath, and add column by column: every column gives
$u_1+u_n$, and there are $n$ of them. So twice the sum is $n(u_1+u_n)$.
Substituting $u_n=u_1+(n-1)d$ turns it into the other printed form,
$S_n=\frac n2\bigl(2u_1+(n-1)d\bigr)$ — the same formula, not a second one.

## The other idea

After that, the topic stops being about formulas at all.

> **A progression is two numbers, $u_1$ and $d$. Almost every question
> gives you two facts about them.**

*"The 5th term is 11, and the 3rd and 9th add to 20."* Two facts, two
unknowns, two linear equations — and solving those you have been able to
do since school. The work is writing them down, not solving them.

## How the checks work

They do not know the answers, and they do not know the formulas. Each
check is handed **the rule** — a first term and a step — and walks:

```python
verify_term('4', 8, progression(q4u, q4d), 8)
```

is *"your first term and your common difference: is the eighth term of
that sequence equal to 8?"* The term is reached by adding $d$ seven
times. $u_1+(n-1)d$ appears nowhere, so any correct form of an
answer passes: $2n+3$, $5+2(n-1)$ and $n+(n+3)$ are the same answer.

**The checks run in both directions, and you will use both.**

| direction | what is known | what carries your answer |
|---|---|---|
| forward | the progression | the term, or the sum |
| backward | the term, or the sum | the progression |

The line above is backward: nothing on it is your answer except what is
inside `progression(...)`, and the 8 came from the question. That is how
*find the first term and the common difference* gets checked without a
single answer being stored.

A consequence worth having: **progressions may be built from your own
earlier answers.** In task 6 the sums come from your $p$ and $q$; in
task 3 the rows come from your rule for one row. A wrong first part
therefore costs you the first part only — which is what a markscheme
calls follow through.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| $u_1+nd$ | the step is taken $n$ times instead of $n-1$ |
| the term next door | the index is out by one |
| $u_n$ where $S_n$ was asked | that is the term, not the sum |
| $n(u_1+u_n)$ | the sum is doubled: the $n/2$ has become $n$ |
| $u_1-u_2$ | the sign is the other way round |
| $n=0$ | an index counts terms: it has to be at least one |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the progression is given; walk it | 1–3 |
| 🟡 | the progression is what you are looking for | 4–10 |
| 🔴 | $n$ itself is the unknown, and it is not free | 11–13 |

Every task is a real past-paper question, cited.

**47% of these marks are on a calculator paper, and the number lies in
both directions.** Twenty-five of those marks are one Paper 3
investigation that is pure algebra — the paper simply allows a
calculator. The other way round, task 12 cannot be done without one:
"the smallest number that is both triangular and pentagonal" is not an
equation, and every markscheme for it says *uses a table of values*.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + progression, term, total, ln, pi, ...

language('en')                 # this notebook is in English, and so are the checks

n = symbols('n')               # the index: every one of these papers calls it n
d, p, q, m = symbols('d p q m')   # letters that stay letters
x = symbols('x', positive=True)   # every paper here says x > 1, and saying so
                               # is what lets ln(1/x**3) become -3*ln(x)
                               # k already comes from kit


# Every progression below may be built from an answer you have not written
# yet. The two helpers return an empty progression in that case, so the
# notebook runs top to bottom while it is still blank and the checks print
# a white square.

def terms(rule):
    # the progression whose nth term is rule(n)
    try:
        first, second = rule(1), rule(2)
    except TypeError:                      # an answer inside the rule is blank
        return progression(..., ...)
    if blank(first, second):
        return progression(..., ...)
    return progression(first, second - first)


def sums(rule):
    # the progression whose first n terms add up to rule(n)
    try:
        first, second = rule(1), rule(2)
    except TypeError:
        return progression(..., ...)
    if blank(first, second):
        return progression(..., ...)
    # the first term is S1, and the second is S2 - S1, so the step is
    # S2 - 2*S1: nothing here knows the formula for a sum
    return progression(first, second - 2 * first)


print('ready; sympy', sp.__version__)
print('a progression:', progression(3, 2))
print('its 5th term: ', term(progression(3, 2), 5))
print('and S5:       ', total(progression(3, 2), 5))
""")

md(r"""
---
## Map of the nine techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | which term is it | $u_1$ and $d$ known, a term or an index asked | $u_n=u_1+(n-1)d$ |
| 2 | add the first $n$ | the word *sum*, a $\Sigma$, something piling up | $S_n=\frac n2(u_1+u_n)$ |
| 3 | two facts, two unknowns | neither $u_1$ nor $d$ is given | two linear equations |
| 4 | from $S_n$ back to $u_n$ | the question says $S$, the answer wants $u$ | $u_n=S_n-S_{n-1}$ |
| 5 | the constant difference as a condition | a letter inside the terms, or *show that … is arithmetic* | $u_2-u_1=u_3-u_2$ |
| 6 | quantities with no index | a coefficient, a root and a constant put in sequence | the same condition, on letters |
| 7 | the greatest sum | *maximum* beside $S_n$, and $d<0$ | the terms turn negative |
| 8 | $n$ has to be a whole number | *smallest*, *no cards left over* | a table, not an equation |
| 9 | terms that are logarithms | $\ln x+p\ln x+\dots$ | log laws first, then technique 2 |

Techniques 1–2 are the two formulas. Technique 3 is the topic's real
question and technique 4 is it read backwards. Technique 5 turns the
progression from a list into a condition, and technique 6 is the same
condition applied to things that have no index at all. The last three are
what the exam does when the algebra stops: 7 needs the sign of the terms,
8 needs a table, 9 needs the log laws before anything else.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Walking the progression

## Theory: two formulas, and where they come from

**The term.** Adding $d$ once takes you from $u_1$ to $u_2$; adding it
$n-1$ times takes you to $u_n$:

$$u_n=u_1+(n-1)d$$

When the paper hands you the sequence already written as a formula in
$n$ — *"$u_n=4n+3$"* — read it the same way. It is linear in $n$, the
coefficient of $n$ **is** the common difference, and the constant term is
$u_0$, which is not a term of the sequence at all.

> The mark that goes missing here: for $u_n=4n+3$ the first term is
> $7$, not $3$.

**The sum.** Write $S_n$ forwards and backwards and add:

$$
\begin{array}{ccccc}
S_n &=& u_1 &+& (u_1+d) &+& \dots &+& u_n\\
S_n &=& u_n &+& (u_n-d) &+& \dots &+& u_1
\end{array}
$$

Every column adds to $u_1+u_n$, and there are $n$ columns, so

$$2S_n=n(u_1+u_n)\qquad\Longrightarrow\qquad S_n=\frac n2(u_1+u_n)$$

Substitute $u_n$ and you get the other printed form. Which one is shorter
depends on what you were given: $u_n$ known → the first, $d$ known →
the second.

### The sum is not the term

$1+2+3+\dots+n=\frac{n(n+1)}{2}$ is a **sum**. Its $n$th term is $n$.
The whole of Part 1 rests on keeping those two apart, because the exam
puts them in the same sentence: *"the $n$th triangular number is
$\frac{n(n+1)}{2}$"* — a triangular number is a sum, and the thing being
summed is the sequence $1,2,3,\dots$
""")

md(r"""
### Task 1 🟢 — *May 2022 TZ2 Paper 1 Q1, 5 marks*

The $n$th term of an arithmetic sequence is given by $u_n=15-3n$.

**(a)** State the value of the first term, $u_1$.
**(b)** Given that the $n$th term of this sequence is $-33$, find the
value of $n$.
**(c)** Find the common difference, $d$.

*The check builds a progression out of your $u_1$ and your $d$ together
and asks whether it reproduces $15-3n$. Only one pair does, so (a) and
(c) are pinned by the same line.*
""")

code(r"""
q1a = ...        # the first term
q1b = ...        # the value of n for which the term is -33
q1c = ...        # the common difference

mine = progression(q1a, q1c)                 # your first term, your step

verify_term('1a, 1c', 15 - 3 * n, mine, n)   # does it come out as 15 - 3n?
verify_term('1b', -33, mine, q1b)            # and is your n where it reaches -33?
""")

md(r"""
### Task 2 🟢 — *November 2025 TZ1 Paper 1 Q1, 6 marks*

The 1st and 5th terms of an arithmetic sequence are $36$ and $12$
respectively.

**(a)** Find the 13th term of this arithmetic sequence.

The sum of the first $n$ terms of this arithmetic sequence is zero.

**(b)** Find the value of $n$.

*The common difference is asked here too, although the paper does not:
a wrong $d$ and a wrong 13th term are two different mistakes, and it is
worth knowing which one you made.*

*In (b) there is a second answer the markscheme condones and the check
does not: the sum of **no** terms is also zero. An index counts terms.*
""")

code(r"""
q2d = ...        # the common difference
q2a = ...        # the 13th term
q2b = ...        # the number of terms whose sum is zero

mine = progression(36, q2d)                  # the first term is given

verify_term('2 (d)', 12, mine, 5)            # is the 5th term of yours 12?
verify_term('2a', q2a, mine, 13)
verify_total('2b', 0, mine, q2b)
""")

md(r"""
### Task 3 🟢 — *May 2025 TZ1 Paper 2 Q10 (a)–(c), 6 marks*

Rectangular playing cards are stacked in the shape of a pyramid with $n$
rows. Some cards are placed horizontally and some are stacked at an
angle of $60^\circ$ to the horizontal. A pyramid with one row is two
cards; a pyramid with two rows is seven; a pyramid with three rows adds
another row below that.

Let $t_n$ be the number of cards in a pyramid with $n$ rows.

**(a)** Write down $t_3$.
**(b)** Find $t_4$.
**(c)** Show that $t_n=\dfrac{n(3n+1)}{2}$.

*Part (c) is a "show that", so the answer is printed in the question and
there is nothing to hand over. What is asked instead is the step before
it: **how many cards row $n$ takes on its own**. That is the sequence
being summed, and once you have it, (c) is one substitution.*

*Row 1 is two cards. Each row below adds the same number more than the
row above — that is what makes the total an arithmetic series.*
""")

code(r"""
q3r = ...        # the number of cards in row n alone, in terms of n
q3a = ...        # t3
q3b = ...        # t4

rows = terms(lambda i: q3r.subs(n, i) if q3r is not Ellipsis else ...)

verify_total('3c', n * (3 * n + 1) / 2, rows, n)   # your rows add up to that
verify_total('3a', q3a, rows, 3)
verify_total('3b', q3b, rows, 4)
""")

# ================================================================= теория 2
md(r"""
---
# 🟡 Part 2. Finding the progression

## Theory: two facts are two equations

A progression is two numbers. Everything the paper tells you about it is
a fact about those two numbers, and each fact is one equation.

| what the paper says | the equation |
|---|---|
| the 5th term is 11 | $u_1+4d=11$ |
| $S_{10}=75$ | $\tfrac{10}2\bigl(2u_1+9d\bigr)=75$ |
| the 3rd and 9th add to 20 | $(u_1+2d)+(u_1+8d)=20$ |
| $u_6=S_3$ | $u_1+5d=\tfrac32(2u_1+2d)$ |

Write both, solve, substitute back. That last step is not optional: it
costs ten seconds and catches every sign slip you are going to make.

> **The trap is using one fact twice.** *"$u_5=S_5=20$"* looks like one
> statement and is two: the fifth term is 20, **and** the first five
> terms add to 20. Use only one of them and the system has no unique
> solution.

## Theory: from the sum back to the terms

Sometimes the paper gives $S_n$ as a formula and asks for the terms. Two
lines do the whole job:

$$u_1=S_1,\qquad u_n=S_n-S_{n-1}$$

The first because the sum of one term is that term. The second because
$S_n$ and $S_{n-1}$ differ by exactly what the $n$th term added.

$$S_n=3n^2-n\ \Longrightarrow\ u_n=(3n^2-n)-\bigl(3(n-1)^2-(n-1)\bigr)=6n-4$$

> $u_n$ is **not** $S_n/n$. That is the average of the terms.

A quadratic $S_n$ is the fingerprint of an arithmetic sequence, and the
coefficients say which one: if $S_n=an^2+bn$ then $d=2a$, because the
gap between consecutive terms of a quadratic grows by twice its leading
coefficient. You never have to remember that — $S_2-2S_1$ gives it in one
line — but seeing it once explains why the sum comes out quadratic at all.
""")

md(r"""
### Task 4 🟡 — *May 2021 TZ1 Paper 1 Q2, 5 marks*

Consider an arithmetic sequence where $u_8=S_8=8$. Find the value of the
first term, $u_1$, and the value of the common difference, $d$.

*Both checks are backward: nothing in them is an answer except what sits
inside `progression(...)`, and both eights came from the question.*
""")

code(r"""
q4u = ...        # the first term
q4d = ...        # the common difference

mine = progression(q4u, q4d)

verify_term('4 (u8)', 8, mine, 8)            # is the 8th term of yours 8?
verify_total('4 (S8)', 8, mine, 8)           # and do the first eight add to 8?
""")

md(r"""
### Task 5 🟡 — *November 2025 TZ3 Paper 1 Q1, 5 marks*

The 7th term of an arithmetic sequence is $6$. The sum of the 6th term
and the 12th term is $24$.

Find the first term and the common difference.

*The second condition is not a partial sum — it is two particular terms
added — so the cell reads it out with `term(...)` and hands the check
what is left over.*
""")

code(r"""
q5u = ...        # the first term
q5d = ...        # the common difference

mine = progression(q5u, q5d)

# the second condition names two terms, not a sum: take one of them off
# the 24 and ask the check about the other
rest = ... if blank(q5u, q5d) else 24 - term(mine, 12)

verify_term('5 (u7)', 6, mine, 7)
verify_term('5 (u6 + u12)', rest, mine, 6)
""")

md(r"""
### Task 6 🟡 — *November 2023 TZ1 Paper 1 Q3, 7 marks*

The sum of the first $n$ terms of an arithmetic sequence is given by
$S_n=pn^2-qn$, where $p$ and $q$ are positive constants.

It is given that $S_4=40$ and $S_5=65$.

**(a)** Find the value of $p$ and the value of $q$.
**(b)** Find the value of $u_5$.

*`sums(...)` turns your formula for the sums into the progression behind
it: the first term is $S_1$, and the step is $S_2-2S_1$. Both parts are
then checked against the question's own 40 and 65.*
""")

code(r"""
q6p = ...        # p
q6q = ...        # q
q6b = ...        # the fifth term

mine = sums(lambda i: q6p * i ** 2 - q6q * i)

verify_total('6a (S4)', 40, mine, 4)
verify_total('6a (S5)', 65, mine, 5)
verify_term('6b', q6b, mine, 5)
""")

md(r"""
### Task 7 🟡 — *May 2023 TZ1 Paper 1 Q10 (a)–(c), 9 marks*

Consider the arithmetic sequence $u_1,u_2,u_3,\dots$. The sum of the
first $n$ terms of this sequence is given by $S_n=n^2+4n$.

**(a)** **(i)** Find the sum of the first five terms.
**(ii)** Given that $S_6=60$, find $u_6$.
**(b)** Find $u_1$.
**(c)** Hence or otherwise, write an expression for $u_n$ in terms of $n$.

*Here $S_n$ is given, so the progression behind it is not your answer —
it is the question's. All four parts are checked forward against it, and
(c) is checked at several values of $n$ at once: a formula has to be
right everywhere, not at one lucky index.*
""")

code(r"""
q7a = ...        # S5
q7b = ...        # u6
q7c = ...        # u1
q7d = ...        # u_n, in terms of n

given = sums(lambda i: i ** 2 + 4 * i)       # the sums the question gives

verify_total('7a(i)', q7a, given, 5)
verify_term('7a(ii)', q7b, given, 6)
verify_term('7b', q7c, given, 1)
verify_term('7c', q7d, given, n)
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 3. The progression as a condition

## Theory: one equation, read two ways

Up to here the sequence has been something you walk along. Now it becomes
something you **impose**, and the whole of Part 3 is one equation:

$$u_2-u_1=u_3-u_2$$

Read it forwards and it is a test: compute both sides and see whether
they agree. Read it as an equation in a letter and it is a tool: it
picks out the value of that letter for which the sequence *is*
arithmetic.

The same statement rearranges into the form the markschemes prefer:

$$u_2=\frac{u_1+u_3}{2}$$

— **the middle term is the average of its neighbours.** Three quantities
are in arithmetic sequence exactly when the middle one is their mean.

### Showing it holds for every $n$ is a different job

*"Show that $R_1,R_2,R_3,\dots$ form an arithmetic sequence"* is not
answered by checking three of them. The markscheme is explicit:

> *"Award M0 for consideration of special cases, for example $R_3$
> and $R_2$."*

What is wanted is $u_{n+1}-u_n$ in general, and then the sentence that
earns the last mark: **and this does not depend on $n$, so the difference
is constant.** Doing the algebra and not saying that costs an R1.

## Theory: quantities that have no index

The last step of the topic drops the sequence entirely. Take
$L(x)=mx+c$ and let $r$ be its root. The paper calls $L$ *AS-linear*
when $m$, $r$ and $c$ — **in that order** — are in arithmetic sequence.

There are no $u_1$, no $u_5$, no $n$ anywhere. There is one condition,

$$r-m=c-r,$$

and everything else is algebra: substitute the root of $L$ in terms of
$m$ and $c$, clear the fraction, and a single equation in two letters
comes out. That equation carries the rest of a thirty-one-mark
investigation, and deriving it is the first thing the investigation asks
for.

> Order matters, and it is the first thing to check. $m,r,c$ and $m,c,r$
> give different equations and different answers.
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ3 Paper 1 Q10 (a), 5 marks*

Consider the sequence $\{u_n\}$ whose first three terms are

$$u_1=k-5,\qquad u_2=3-2k,\qquad u_3=5k+3,\qquad k\in\mathbb R$$

Consider the case when $\{u_n\}$ is arithmetic.

**(a)** **(i)** Find the value of $k$.
**(ii)** Hence, or otherwise, find $u_3$.

*The first check has no answer of its own in it: your $k$ goes into the
three terms, and the question is whether they then have a constant
difference. The second walks the progression those terms define and asks
for its third member.*
""")

code(r"""
q8k = ...        # the value of k
q8u = ...        # the third term


def at(value):
    # the three terms of the question, at your k
    return [Ellipsis] * 3 if blank(value) else [value - 5,
                                                3 - 2 * value,
                                                5 * value + 3]


three = at(q8k)

verify_arithmetic('8a(i)', three)
verify_term('8a(ii)', q8u, terms(lambda i: three[i - 1]), 3)
""")

md(r"""
### Task 9 🟡 — *May 2024 TZ2 Paper 1 Q10 (a),(d)(i), 4 marks, and May 2023 TZ2 Paper 1 Q12 (d), 3 marks*

**Part one.** Consider the arithmetic sequence $a,\,p,\,q,\dots$, where
$a,p,q\neq0$. It is given that $q=1$ and $a=9$.

**(a)** Find $p$, and write down the first four terms of the sequence.

*(The paper asks first for the identity $2p-q=a$, which is the same
condition rearranged: the middle term is the mean of its neighbours.)*

**Part two.** The regions bounded by the curve $y=\cos\sqrt x$ and the
$x$-axis are $R_1,R_2,R_3,\dots$, and their areas turn out to be
$R_n=4n\pi$.

**(b)** Show that the areas form an arithmetic sequence, and find the
common difference.

*`verify_step` refuses to answer the second question before the first:
it checks that the difference is constant, and only then that it is
yours.*
""")

code(r"""
q9p = ...        # the second term p, when a = 9 and q = 1
q9t = [...]      # the first four terms
q9d = ...        # the common difference of the areas R1, R2, R3, ...

verify_arithmetic('9a (p)', [9, q9p, 1])     # 9, your p, 1 — a constant step?
verify_start('9a (terms)', q9t, terms(lambda i: [9, q9p, 1][i - 1]))
verify_step('9b', q9d, [4 * i * pi for i in (1, 2, 3, 4)])
""")

md(r"""
### Task 10 🟡 — *May 2023 TZ2 Paper 3 Q2 (a),(b)(ii),(c), 9 marks*

Consider $L(x)=mx+c$ for $x\in\mathbb R$, where $m,c\in\mathbb R$ and
$m,c\neq0$. Let $r\in\mathbb R$ be the root of $L(x)=0$, so that
$r=-\dfrac cm$.

If $m$, $r$ and $c$, **in that order**, are in arithmetic sequence, then
$L$ is said to be an **AS-linear function**.

**(a)** Show that $L(x)=2x-1$ is an AS-linear function, by giving the
common difference of the sequence it makes.
**(b)** Given that $L(x)=mx+c$ is AS-linear, show that
$$L(x)=mx-\frac{m^2}{m+2}$$
by finding $c$ in terms of $m$.
**(c)** There are only three **integer** sets of values of $m$, $r$ and
$c$ that form an AS-linear function. One of them is $L(x)=-x-1$. Use
part (b) to determine the other two.

*Part (b) is checked without $c$ ever being compared to anything: your
expression goes into the triple $(m,\,-c/m,\,c)$, and the triple has to
be arithmetic at every $m$ the check tries. Part (c) is checked the same
way, one function at a time, with the extra demand that all three
numbers come out whole.*
""")

code(r"""
q10d = ...       # the common difference of the sequence made by L(x) = 2x - 1
q10c = ...       # c in terms of m
q10f = [...]     # the other two AS-linear functions, as expressions in x


def triple(slope, constant):
    # the sequence the definition makes: the slope, the root, the constant
    return ([Ellipsis] * 3 if blank(slope, constant)
            else [slope, -constant / slope, constant])


verify_step('10a', q10d, triple(2, -1))
verify_arithmetic('10b', triple(m, q10c), m, (1, 3, -5))

for got in q10f:
    verify_arithmetic('10c', triple(got.coeff(x, 1), got.coeff(x, 0))
                      if got is not Ellipsis else [...])
""")

# ================================================================= теория 4
md(r"""
---
# 🔴 Part 4. When $n$ is the unknown

## Theory: the sum stops growing

$S_n$ is a quadratic in $n$, so if $d<0$ it has a maximum. You can find
it by completing the square, and you will get a fractional $n$ — which
is no answer at all, because $n$ counts terms.

The honest route needs no quadratic:

> **The sum grows exactly while the terms are positive.**

So solve $u_n\ge0$, take the largest whole $n$, and substitute. If some
term is exactly zero, two consecutive sums are equal and both indices are
correct answers.

### The same question on Paper 1 and on Paper 2

*The sum of the first $n$ terms is zero* is Paper 1, and it is one line
of algebra: $\frac n2(u_1+u_n)$ vanishes only when $u_n=-u_1$, so the last
term is the first one reflected, and the index follows in one step.

*Find the maximum value of $S_n$* is Paper 2, and a table of
$S_n$ answers it in ten seconds. But the value must then be taken by
substituting the whole $n$ back into the formula, not read off the
graph's vertex: the markscheme deducts the final mark for
$(13.1582\ldots,\,547.119\ldots)$ by name.

## Theory: when $n$ must be a whole number and nothing else

Some questions cannot be turned into an equation at all:

- *the smallest number greater than 1 that is both triangular and pentagonal*
- *the fewest rows so that the cards come from whole packs of 52*

Both are conditions on integers, and algebra does not solve those. Every
markscheme in the archive for this kind of question says the same thing:
**uses a table of values**. Build the table, read it, stop.

> The commonest slip is answering a nearby question. *"How many rows so
> that no cards are left over"* is not *"how many packs"* — two different
> numbers, and only one of them is asked for.
""")

md(r"""
### Task 11 🔴 — *May 2021 TZ2 Paper 2 Q2, 5 marks*

An arithmetic sequence has first term $60$ and common difference $-2.5$.

**(a)** Given that the $k$th term of the sequence is zero, find the value
of $k$.

Let $S_n$ denote the sum of the first $n$ terms of the sequence.

**(b)** Find the maximum value of $S_n$.

*`verify_peak` finds the greatest sum by adding term after term and
keeping the best. Because $u_{25}=0$, two consecutive sums are equal here
and both indices are right — the check accepts either.*
""")

code(r"""
q11k = ...       # the index of the zero term
q11s = ...       # the maximum value of Sn

mine = progression(60, -2.5)

verify_term('11a', 0, mine, q11k)            # is the term at your k zero?
verify_peak('11b', q11s, mine)
""")

md(r"""
### Task 12 🔴 — *May 2022 TZ1 Paper 3 Q1 (d),(e), 8 marks, and May 2025 TZ1 Paper 2 Q10 (e), 2 marks*

**Part one.** The $n$th pentagonal number can be represented by the
arithmetic series

$$P_5(n)=1+4+7+\dots+(3n-2)$$

**(a)** Show that $P_5(n)=\dfrac{n(3n-1)}{2}$, by giving the $n$th term
of the series being added.

**(b)** By using a suitable table of values or otherwise, determine the
smallest positive integer, greater than $1$, that is both a triangular
number and a pentagonal number, **and say which triangular number and
which pentagonal number it is**. (The $n$th triangular number is
$P_3(n)=\dfrac{n(n+1)}{2}$.)

**Part two.** A complete pyramid stack of playing cards with $n$ rows
uses $t_n=\dfrac{n(3n+1)}{2}$ cards. A stack is built from full packs of
$52$ with no cards left over.

**(c)** Find the minimum number of rows in this stack, **and how many
full packs it uses**.

*Part (a) is a "show that", so what is asked is again the sequence being
summed. Parts (b) and (c) are the two questions in the archive that
algebra cannot answer, and both are checked backwards: your number is put
back into the sequence, and the check asks whether it lands where you
said. The two positions and the pack count are asked for that reason —
without them there is nothing to check against but the answer itself.*

*What the check cannot do is confirm that yours is the **smallest**.
It will accept the 40th triangular number that is also pentagonal just
as happily. That mark is yours; the table is what earns it.*
""")

code(r"""
q12r = ...       # the nth term of the pentagonal series, in terms of n
q12t = ...       # the smallest number > 1 that is both triangular and pentagonal
q12i = ...       # which triangular number that is
q12j = ...       # which pentagonal number that is
q12n = ...       # the minimum number of rows
q12k = ...       # how many full packs of 52 that stack uses

pent = terms(lambda i: q12r.subs(n, i) if q12r is not Ellipsis else ...)
tri = terms(lambda i: i)                     # 1 + 2 + 3 + ... is the triangular one
rows = terms(lambda i: 3 * i - 1)            # the card rows, from task 3
cards = ... if blank(q12k) else 52 * q12k

verify_total('12a', n * (3 * n - 1) / 2, pent, n)
verify_total('12b (triangular)', q12t, tri, q12i)
verify_total('12b (pentagonal)', q12t, pent, q12j)
verify_total('12c', cards, rows, q12n)       # whole packs, and no cards over
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 5. Terms that are logarithms

## Theory: the log laws come first

Nothing about the sequence changes when its terms are logarithms. What
changes is that you cannot compare them until they are written the same
way.

$$2+\ln 8,\qquad 6+\ln 2,\qquad 10+\ln\tfrac12$$

look like three unrelated things until $\ln 8=3\ln 2$ and
$\ln\tfrac12=-\ln 2$ turn them into

$$2+3\ln 2,\qquad 6+\ln 2,\qquad 10-\ln 2$$

and now the difference is visible: $4-2\ln 2$, the same both times.

Three laws do all the work in this topic:

$$\ln a^k=k\ln a,\qquad \ln\frac1{a}=-\ln a,\qquad \ln 1=0$$

> The second one is where the marks go. $\ln\dfrac1{x^3}$ is
> $-3\ln x$, not $3\ln x$, and the minus sign is the whole answer.

### Then the sum, and $\ln x$ cancels

When every term carries a factor of $\ln x$, so does the sum — and if
the equation you are solving has $\ln x$ on both sides, it divides out
and leaves a plain equation in $n$. That is the point of the whole
construction: the logarithm is scaffolding, and the question underneath
is a quadratic.

> A last check that costs nothing: an arithmetic sequence has a constant
> **difference**. If you find yourself dividing consecutive terms, you
> have started answering a geometric question.
""")

md(r"""
### Task 13 🔴 — *May 2024 TZ2 Paper 1 Q10 (e), 6 marks*

The first three terms of an arithmetic sequence $u_n$ are

$$u_1=9+\ln 9,\qquad u_2=5+\ln 3,\qquad u_3=1+\ln 1$$

**(a)** Find the common difference of the sequence in terms of $\ln 3$.
**(b)** Show that $\displaystyle\sum_{i=1}^{10}u_i=-90-25\ln 3$.

*Part (b) is a "show that", and the printed answer is used as the
question's own number: the check builds the progression out of your
first term and your common difference, adds ten of them, and compares
with $-90-25\ln 3$. Write $d$ wrongly and only that line fails.*
""")

code(r"""
q13d = ...       # the common difference, in terms of ln 3
q13s = ...       # the sum of the first ten terms

mine = progression(9 + ln(9), q13d)          # the first term is given

verify_step('13a', q13d, [9 + ln(9), 5 + ln(3), 1 + ln(1)])
verify_total('13b', q13s, mine, 10)
verify_exact('13b (exact)', q13s, -90 - 25 * ln(3))
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `term` | $u_1$ and $d$ are known; use $u_n=u_1+(n-1)d$ |
| `sum` | something is being added up; use $S_n=\frac n2(u_1+u_n)$ |
| `two` | neither $u_1$ nor $d$ is given; write two equations |
| `back` | $S_n$ is given as a formula; use $u_n=S_n-S_{n-1}$ |
| `difference` | impose or prove $u_2-u_1=u_3-u_2$ |
| `coefficients` | named quantities with no index put in sequence |
| `peak` | the greatest sum; the terms turn negative |
| `integer` | $n$ has to be whole; build a table |
| `log` | the terms are logarithms; use the log laws first |

1. An arithmetic sequence has $u_1=7$ and $d=4$. Find the 20th term.
2. Find $1+2+3+\dots+100$.
3. An arithmetic sequence has $u_4=11$ and $u_9=26$. Find $u_1$ and $d$.
4. The sum of the first $n$ terms is $S_n=3n^2-2n$. Find $u_5$.
5. The sequence $k+1$, $2k$, $7k-6$ is arithmetic. Find $k$.
6. $L(x)=mx+c$ has root $r$, and $m$, $r$, $c$ are in arithmetic sequence. Find $c$ in terms of $m$.
7. An arithmetic sequence has $u_1=80$ and $d=-6.32$. Find the greatest value of $S_n$.
8. Find the smallest $n$ for which $\tfrac12n(3n+1)$ is a multiple of $52$.
9. The first three terms are $\ln x$, $\tfrac23\ln x$, $\tfrac13\ln x$. Find the common difference.
10. The 8th term of an arithmetic sequence equals the sum of its first eight terms, and both are 8. Find $u_1$.
11. A pyramid of cards has 2 cards in the top row and 3 more in each row below. How many cards in six rows?
12. Show that the areas $R_n=4n\pi$ form an arithmetic sequence.
""")

code("""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + """)
""")

# ================================================================= таймер
md(r"""
---
## On the clock — *May 2022 TZ1 Paper 1 Q10 (b), 12 marks*

**Twelve marks, eighteen minutes.** No hints this time.

Consider the series

$$\ln x+p\ln x+\tfrac13\ln x+\dots$$

where $x\in\mathbb R$, $x>1$ and $p\in\mathbb R$, $p\neq0$.

Consider the case where the series is **arithmetic** with common
difference $d$.

**(i)** Show that $p=\tfrac23$.
**(ii)** Write down $d$ in the form $k\ln x$, where $k\in\mathbb Q$.
**(iii)** The sum of the first $n$ terms of the series is
$\ln\!\left(\dfrac1{x^3}\right)$. Find the value of $n$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_p = ...       # p
qt_d = ...       # the common difference, in the form k*ln(x)
qt_n = ...       # the number of terms

mine = progression(ln(x), qt_d)              # the first term is given
three = [...] if blank(qt_p) else [ln(x), qt_p * ln(x), ln(x) / 3]

verify_arithmetic('timer (i)', three)
verify_step('timer (ii)', qt_d, three)
verify_total('timer (iii)', ln(1 / x ** 3), mine, qt_n)
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** $u_1=15-3(1)=\boxed{12}$.

The trap is answering $15$. That is $u_0$, and the sequence starts at
$n=1$.

**1 (b)** $15-3n=-33\Longrightarrow 3n=48\Longrightarrow \boxed{n=16}$.

**1 (c)** Two consecutive terms differ by the coefficient of $n$:

$$u_2-u_1=(15-6)-(15-3)=\boxed{-3}$$

The markscheme accepts *"recognize gradient is $-3$"* on its own — the
sequence is a linear function of $n$, and its gradient is $d$.

---

**2 (a)** From $u_1=36$ to $u_5=12$ there are **four** steps:

$$12=36+4d\Longrightarrow d=\boxed{-6}$$

Then eight more steps to the 13th term:

$$u_{13}=u_5+8(-6)=12-48=\boxed{-36}$$

or, equally, $u_{13}=36+12(-6)=-36$.

**2 (b)** $S_n=\dfrac n2\bigl(u_1+u_n\bigr)=0$ with $n\neq0$ forces
$u_1+u_n=0$, so $u_n=-36$ — and by (a) that is the 13th term:

$$\boxed{n=13}$$

The symmetric way is prettier: $36+30+\dots+0+\dots-30-36$. Everything
cancels in pairs around the zero term, and the zero term is the 7th, so
there are $6+1+6=13$ terms.

*The markscheme condones $n=0,13$. The check does not, and says why: an
index counts terms.*

---

**3 (c)** Row 1 takes 2 cards. Every row below takes 3 more than the row
above — two more slanted cards and one more horizontal. So

$$\text{row }n=3n-1\qquad(2,\,5,\,8,\,11,\dots)$$

and $t_n$ is the sum of that arithmetic series:

$$t_n=\frac n2\bigl(2+(3n-1)\bigr)=\frac n2(3n+1)$$

**3 (a)** $t_3=2+5+8=\boxed{15}$.

**3 (b)** $t_4=15+11=\boxed{26}$.

The mistake worth naming: adding $10$ instead of $11$. The fourth row has
$3(4)-1=11$ cards, not $10$.

---

**4** Two facts, two equations:

$$u_1+7d=8,\qquad \frac82\bigl(2u_1+7d\bigr)=8$$

The second gives $2u_1+7d=2$. Subtracting the first,

$$u_1=2-8=-6,\qquad 7d=8-(-6)=14\Longrightarrow d=2$$

$$\boxed{u_1=-6,\quad d=2}$$

Faster still: $S_8=\frac82(u_1+u_8)=4(u_1+8)=8$ gives $u_1=-6$ in one
line, because $u_8$ is already known to be 8.

---

**5** $u_7=6$ gives $u_1+6d=6$. For the second condition, either expand
both terms,

$$(u_1+5d)+(u_1+11d)=24\Longrightarrow 2u_1+16d=24\Longrightarrow u_1+8d=12,$$

or notice that $u_6$ and $u_{12}$ sit one step below and five steps above
$u_7$:

$$u_6=6-d,\quad u_{12}=6+5d\Longrightarrow 12+4d=24\Longrightarrow d=3$$

Then $u_1=6-6(3)=\boxed{-12}$, $\boxed{d=3}$.

The second route is the markscheme's METHOD 2 and it is three lines
shorter. Measuring from a term you already know, rather than from $u_1$,
is worth having as a habit.

---

**6 (a)** $S_4=16p-4q=40$ and $S_5=25p-5q=65$, that is

$$4p-q=10,\qquad 5p-q=13$$

Subtracting, $p=3$; then $q=4(3)-10=2$.

$$\boxed{p=3,\quad q=2}$$

**6 (b)** $u_5=S_5-S_4=65-40=\boxed{25}$.

Nothing about $p$ and $q$ is needed for (b) at all. It is the fastest
mark on the paper and the one most often done the long way.

---

**7 (a)(i)** $S_5=25+20=\boxed{45}$.

**(ii)** $u_6=S_6-S_5=60-45=\boxed{15}$.

**7 (b)** $u_1=S_1=1+4=\boxed{5}$.

**7 (c)** $u_n=S_n-S_{n-1}$:

$$\bigl(n^2+4n\bigr)-\bigl((n-1)^2+4(n-1)\bigr)=n^2+4n-n^2+2n-1-4n+4=\boxed{2n+3}$$

Or through $d$: $u_2=S_2-S_1=(4+8)-5=7$, so $d=7-5=2$ and
$u_n=5+2(n-1)=2n+3$.
The check accepts both forms, and $n+(n+3)$ as well — it walks the
sequence, it does not read the expression.

---

**8 (a)(i)** Arithmetic means the two gaps are equal:

$$(3-2k)-(k-5)=(5k+3)-(3-2k)$$
$$8-3k=7k\Longrightarrow 10k=8\Longrightarrow k=\boxed{\tfrac45}$$

The mean form is quicker: $\dfrac{(k-5)+(5k+3)}{2}=3-2k$ gives
$3k-1=3-2k$ in one step.

**(ii)** $u_3=5\left(\tfrac45\right)+3=\boxed{7}$.

The terms are $-\tfrac{21}5,\ \tfrac75,\ 7$ — a common difference of
$\tfrac{28}5$. Substituting $k$ into the wrong expression is the
standard slip here; $u_3$ is $5k+3$.

---

**9 (a)** In $a,p,q$ the middle term is the mean:

$$p=\frac{a+q}{2}=\frac{9+1}{2}=\boxed{5}$$

which is the identity $2p-q=a$ rearranged. The common difference is
$-4$, so the first four terms are

$$\boxed{9,\ 5,\ 1,\ -3}$$

**9 (b)** $R_{n+1}-R_n=4(n+1)\pi-4n\pi=\boxed{4\pi}$.

This does not depend on $n$, **so the difference is constant and the
areas form an arithmetic sequence** — that sentence is the R1, and the
markscheme awards M0 for checking $R_3$ and $R_2$ instead.

---

**10 (a)** $L(x)=2x-1$ has $m=2$, $c=-1$ and root $r=\tfrac12$. The
sequence $2,\ \tfrac12,\ -1$ has

$$d=\tfrac12-2=-1-\tfrac12=\boxed{-\tfrac32}$$

Equal both ways, so it is arithmetic and $L$ is AS-linear.

**10 (b)** With $r=-\dfrac cm$, the condition $r-m=c-r$ becomes

$$-\frac cm-m=c+\frac cm$$
$$-2\frac cm=c+m\Longrightarrow -2c=cm+m^2\Longrightarrow m^2+cm+2c=0$$

Solve for $c$:

$$c(m+2)=-m^2\Longrightarrow c=\boxed{-\frac{m^2}{m+2}}$$

and so $L(x)=mx-\dfrac{m^2}{m+2}$. The restriction that comes with it is
$m\neq-2$, and it is worth its own mark.

**10 (c)** $c$ is an integer exactly when $m+2$ divides $m^2$. Since
$m^2=(m-2)(m+2)+4$, that means $m+2$ divides $4$:

$$m+2\in\{\pm1,\pm2,\pm4\}\Longrightarrow m\in\{-1,-3,0,-4,2,-6\}$$

Discard $m=0$, and check which give integer $r=-c/m$ as well. The three
that survive are $m=-1$ (the one given, $L(x)=-x-1$) and

$$\boxed{L(x)=-4x+8,\qquad L(x)=-3x+9}$$

with sequences $-4,2,8$ and $-3,3,9$ — differences $6$ and $6$.

---

**11 (a)** $u_k=60-2.5(k-1)=0$ gives $2.5(k-1)=60$, so $k-1=24$ and

$$\boxed{k=25}$$

**11 (b)** The terms are positive up to the 24th, zero at the 25th and
negative after, so the sum is greatest at $n=24$ **and** at $n=25$ — both
give the same total:

$$S_{25}=\frac{25}{2}(60+0)=\boxed{750}$$

A table of $S_n$ on the GDC gets there faster, but read the *value* off
the table, not off the graph: the vertex of the parabola sits at a
fractional $n$, and that answer is explicitly not accepted.

---

**12 (a)** The series $1+4+7+\dots$ has $u_1=1$ and $d=3$, so its $n$th
term is

$$\boxed{3n-2}$$

and the sum is

$$P_5(n)=\frac n2\bigl(1+(3n-2)\bigr)=\frac{n(3n-1)}{2}$$

**12 (b)** Two tables side by side:

| $n$ | $P_3(n)$ | | $m$ | $P_5(m)$ |
|---|---|---|---|---|
| 18 | 171 | | 10 | 145 |
| 19 | 190 | | 11 | 176 |
| **20** | **210** | | **12** | **210** |
| 21 | 231 | | 13 | 247 |

$$\boxed{210}$$

the 20th triangular number and the 12th pentagonal number. Stopping the
table too early is the whole difficulty: nothing smaller than 210 works,
and 1 is excluded by the question.

**12 (c)** $t_n=\tfrac12n(3n+1)$ has to be a multiple of $52$:

$$2,\ 7,\ 15,\ 26,\ 40,\ 57,\ 77,\ 100,\ 126,\ 155,\ 187,\ 222,\ \boxed{260}$$

and $260=5\times52$ at $n=13$, so the answer is $\boxed{13}$ rows.

Two ways to lose this mark: solving $t_n=52$ (which the markscheme
rejects by name), and answering $5$ — the number of packs, not the number
of rows.

---

**13 (a)** Rewrite every term over $\ln 3$:

$$u_1=9+2\ln 3,\qquad u_2=5+\ln 3,\qquad u_3=1+0$$

$$d=u_2-u_1=(5-9)+(1-2)\ln 3=\boxed{-4-\ln 3}$$

and $u_3-u_2=(1-5)+(0-1)\ln 3$ gives the same, as it must.

**13 (b)**

$$S_{10}=\frac{10}{2}\bigl(2u_1+9d\bigr)
=5\Bigl(2(9+2\ln 3)+9(-4-\ln 3)\Bigr)$$
$$=5\bigl(18+4\ln 3-36-9\ln 3\bigr)=5(-18-5\ln 3)=\boxed{-90-25\ln 3}$$

Both halves of the answer are needed. Cancelling the logarithms early —
because $\ln 1=0$ — loses the $-25\ln 3$ entirely.

---

## Timer

**(i)** Arithmetic means the two gaps are equal:

$$p\ln x-\ln x=\tfrac13\ln x-p\ln x$$

Since $x>1$, $\ln x\neq0$ and it divides out:

$$p-1=\tfrac13-p\Longrightarrow 2p=\tfrac43\Longrightarrow p=\boxed{\tfrac23}$$

**(ii)** $d=p\ln x-\ln x=\left(\tfrac23-1\right)\ln x=\boxed{-\tfrac13\ln x}$.

**(iii)** First the right-hand side, and this is where the marks are:

$$\ln\!\left(\frac1{x^3}\right)=\ln x^{-3}=-3\ln x$$

Now the sum:

$$S_n=\frac n2\Bigl(2\ln x+(n-1)\left(-\tfrac13\ln x\right)\Bigr)=-3\ln x$$

Divide by $\ln x$ — it is on both sides, and this is the point of the
whole construction:

$$\frac n2\left(2-\frac{n-1}{3}\right)=-3
\Longrightarrow \frac n2\cdot\frac{7-n}{3}=-3
\Longrightarrow n(7-n)=-18$$

$$n^2-7n-18=0\Longrightarrow (n-9)(n+2)=0\Longrightarrow \boxed{n=9}$$

$n=-2$ is discarded: an index counts terms.

The markscheme's second method is worth seeing, because it needs no
algebra at all. The terms are

$$\ln x,\ \tfrac23\ln x,\ \tfrac13\ln x,\ 0,\ -\tfrac13\ln x,\
-\tfrac23\ln x,\ -\ln x,\ -\tfrac43\ln x,\ -\tfrac53\ln x,\dots$$

The first seven cancel in pairs around the zero and sum to nothing. The
8th and 9th add to $-3\ln x$, which is exactly what was wanted. So
$n=9$ — and that symmetry is the same one that answered task 2(b).
""")


def build():
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
    os.makedirs(os.path.dirname(NOTEBOOK), exist_ok=True)
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    n_code = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f"{NOTEBOOK}: {len(cells)} ячеек, из них {n_code} с кодом, "
          f"эталонов {len(ANSWERS)}")


if __name__ == '__main__':
    build()
