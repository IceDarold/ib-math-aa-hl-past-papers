"""Собирает практикум A2: геометрические прогрессии и бесконечные суммы.

Двадцать шестой практикум серии и первый, собранный из двух тем
корпуса сразу: number_algebra.geometric_sequences целиком плюс остаток
number_algebra.sequences после A1 — те вопросы, что начинаются
арифметической последовательностью и кончаются геометрической.

Лестница из семи приёмов идёт по тому, чем оказывается знаменатель.
Сначала он просто число и берётся делением. Потом решает, есть ли
у ряда сумма вообще. Потом прячется в сигму. Потом сам становится
неизвестным в уравнении на букву. Напоследок перестаёт быть числом
и делается выражением с x — и тогда сумма ряда оказывается функцией.

Проверки те же, что в A1, и продолжают то же понятие равенства
ответов: **последовательность порождается**. Новое здесь — второй род
правила. `geometric(first, ratio)` передаёт первый член и знаменатель,
и члены получаются умножением. Ни u₁r^(n−1), ни u₁(rⁿ−1)/(r−1), ни
u₁/(1−r) внутри проверки не написано ни разу.

Отсюда же и то, чего в A1 быть не могло. `verify_infinite` складывает
члены, пока хвост не станет мал, — и у расходящегося ряда складывать
негде. Условие |r| < 1 поэтому не записано отдельным правилом: проверка
упирается в него сама и говорит те же слова, что сказал бы экзаменатор.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_a2.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/number_algebra/practicum-a2-geometric-sequences.ipynb')

TRIGGER = {1: 'ratio', 2: 'infinite', 3: 'condition', 4: 'least',
           5: 'sigma', 6: 'sum', 7: 'letter', 8: 'infinite',
           9: 'condition', 10: 'least', 11: 'ratio', 12: 'letter'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1r': '0.21',
    'q1u': '16.8',
    'q2s': '(10**n - 1)/9',
    'q2t': '10*(10**n - 1)/9',
    'q3p': 'Rational(8, 5)',
    'q3a': '10',
    'q3q': 'Rational(65, 2)',
    'q4u': 'Rational(7, 12)',
    'q4s': 'Rational(14, 3)',
    'q4n': '64',
    'q5t': 's**2/a',
    'q6r': '[-sqrt(3), sqrt(3)]',
    'q6n': '-sqrt(3)',
    'q6v': '-15*sqrt(3)',
    'q7t': '[7, -21, 63]',
    'q7r': '-3',
    'q8r': '1.2',
    'q8n': '27',
    'q9a': '29750',
    'q9b': '10423',
    'q9n': '20',
    'q10s': 'Rational(53, 990)',
    'q10f': 'Rational(251, 990)',
    'q11n': 'n + 1',
    'q11s': '(x**(n + 1) - 1)/(x - 1)',
    'q12f': '1 - 2*x**2 + 4*x**4 - 8*x**6 + 16*x**8',
    'q12s': '1/(1 + x**2)',
    'q13r': '0.812',
    'q13d': '19.2',
    'qt_k': '-2',
    'qt_r': '-1',
    'qt_t': '[-7, 7, -7]',
    'qt_s': '0',
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
# A2 — Geometric sequences and infinite sums

**77 marks of the archive, seven techniques, thirteen tasks.** Everything
the archive asks about geometric sequences from November 2021 to
November 2025 — including the halves of questions that A1 had to leave
behind, because the exam likes to start a question arithmetic and finish
it geometric.

## The one idea

A geometric sequence differs from an arithmetic one by a single word.

> **From each term to the next you multiply by the same thing.**

$$u_n=u_1r^{\,n-1}$$

is *"you have multiplied by $r$ exactly $n-1$ times"*, and the $-1$ is
the same count of steps that it was in A1, lost just as often.

The sum comes out of one trick. Write $S_n$, write $rS_n$ underneath,
and subtract: everything in the middle cancels.

$$
\begin{array}{rcl}
S_n &=& u_1+u_1r+u_1r^2+\dots+u_1r^{\,n-1}\\
rS_n &=& \qquad\ \ u_1r+u_1r^2+\dots+u_1r^{\,n-1}+u_1r^{\,n}
\end{array}
$$

$$S_n-rS_n=u_1-u_1r^{\,n}\qquad\Longrightarrow\qquad
S_n=\frac{u_1\left(r^{\,n}-1\right)}{r-1}$$

## The other idea, which arithmetic sequences do not have

If $|r|<1$ the terms shrink, the tail can be made smaller than any
number you name, and the **infinite** series has a sum:

$$S_\infty=\frac{u_1}{1-r}\qquad\text{when }|r|<1$$

If $|r|\ge1$ it has none. That is not a footnote. Half the questions in
this topic are about which of the two you are in, and *"state a reason
why the sum of an infinite number of terms does not exist"* is a
question the exam asks in those words.

## And a third, which is where the marks go

The ratio is found by **dividing**, and dividing gives a **quadratic**
whenever the unknown sits inside the terms. A quadratic has two roots,
and something else in the question chooses between them: a sign, a
convergence condition, an index that has to be whole.

> $r^2=9$ has two answers. Writing $r=3$ costs a mark, by name: the
> markscheme awards *M1A1A0 for $\sqrt{\,\cdot\,}$ with no $\pm$*.

## How the checks work

They do not know the answers, and they do not know the formulas. Each
check is handed **the rule** — a first term and a ratio — and multiplies:

```python
verify_term('1 (r)', 0.74088, geometric(80, q1r), 4)
```

is *"your ratio: is the fourth term of that sequence $0.74088$?"* The
term is reached by multiplying three times. $u_1r^{\,n-1}$ appears
nowhere.

The infinite sum is the same idea taken as far as it goes:
`verify_infinite` adds term after term until the tail stops mattering.
So a series that does not shrink cannot be summed by it at all — and
when you hand it one, it says so in the examiner's own words.

**The checks run in both directions**, as they did in A1: forward when
the sequence is known and the answer is a term or a sum, backward when
the answer is inside `geometric(...)` and the number in the line came
from the question.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| $u_1r^{\,n}$ | that is the next term: the index is out by one |
| $u_1/u_2$ | the ratio is upside down |
| $3$ where $-3$ was meant | the sign is gone: an alternating sequence has a negative ratio |
| $S_\infty$ where $S_n$ was asked | that is the sum of the whole sequence, not of the first $n$ |
| $u_1/(1+r)$ | the denominator is $1+r$ instead of $1-r$ |
| $n$ one too small | at that index the condition does not hold yet |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the sequence is given; walk it | 1–4 |
| 🟡 | the ratio is what you are looking for | 5–7 |
| 🔴 | the ratio is not a number, or $n$ is the unknown | 8–13 |

Every task is a real past-paper question, cited.

**52% of these marks are on a calculator paper, and for once the number
is close to honest.** The smallest-$n$ questions are genuinely solved by
a table of values — the markscheme lists *table*, *sketch* and
*logarithms* side by side — and the November 2025 particle needs a GDC
to find the three maxima it then asks you to divide.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + geometric, term, total, infinite, ...

language('en')                 # this notebook is in English, and so are the checks

n = symbols('n')               # the index: every one of these papers calls it n
m = symbols('m')               # a second index, for the timer
r = symbols('r')               # the ratio, when it is the unknown
a, s, t = symbols('a s t')     # letters that stay letters
x = symbols('x')               # the ratio is allowed to be an expression in x
                               # k already comes from kit


# Every sequence below may be built from an answer you have not written
# yet. geometric() returns an empty rule in that case, so the notebook
# runs top to bottom while it is still blank and the checks print ⬜.

def ratios(rule):
    # the geometric sequence whose nth term is rule(n)
    try:
        first, second = rule(1), rule(2)
    except TypeError:                      # an answer inside the rule is blank
        return geometric(..., ...)
    if blank(first, second) or first == 0:
        return geometric(..., ...)
    return geometric(first, second / first)


print('ready; sympy', sp.__version__)
print('a geometric sequence:', geometric(3, 2))
print('its 5th term:        ', term(geometric(3, 2), 5))
print('S5:                  ', total(geometric(3, 2), 5))
# the infinite sum is reached by adding, so it arrives as a long fraction
print('and all of 1, ½, ¼, …:', float(infinite(geometric(1, Rational(1, 2)))))
""")

md(r"""
---
## Map of the seven techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the ratio and a term | two terms given, or a percentage | $u_n=u_1r^{\,n-1}$ |
| 2 | add the first $n$ | *sum*, a $\Sigma$ with a top limit | $S_n=\frac{u_1(r^n-1)}{r-1}$ |
| 3 | the infinite sum | $S_\infty$, *converges*, *forever* | $\frac{u_1}{1-r}$, and $\lvert r\rvert<1$ first |
| 4 | a series written as $\Sigma$ | no term is written out at all | read off $u_1$ and $r$ |
| 5 | three quantities in ratio | *form a geometric sequence*, a letter inside | $s^2=at$ |
| 6 | the smallest $n$ | *smallest*, *least*, *how many years* | logs, or a table |
| 7 | the ratio is an expression | $1+x+x^2+\dots$, a $\Sigma$ with $x$ inside | the same formulas, in letters |

Techniques 1–3 are the three formulas, and 3 carries the condition that
makes it legal. Technique 4 is reading, not computing: the work is
seeing $u_1$ and $r$ in a notation that hides them. Technique 5 is where
the topic stops being arithmetic in disguise — dividing produces a
quadratic, and quadratics have two answers. Technique 6 is the exam's
favourite way of forcing an integer out of a continuous answer, and
technique 7 is everything above with $r$ that is not a number.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Walking the sequence

## Theory: the ratio, and how many times it is applied

Take the sequence $11,\ 44,\ 176,\ 704,\dots$ Each term is four times the
one before, so $r=4$, and

$$u_5=11\cdot4^{\,4}=2816$$

Four multiplications, not five: between $u_1$ and $u_5$ there are four
steps. The exponent is the **number of steps**, and everything in this
part is that sentence applied twice.

**The ratio is found by dividing, and the division may skip terms.**
If you are given $u_2=44$ and $u_5=2816$, then between them there are
three steps:

$$u_5=u_2r^{\,3}\Longrightarrow r^{\,3}=\frac{2816}{44}=64\Longrightarrow r=4$$

> **Odd root, one answer. Even root, two.** $r^3=64$ gives $r=4$ and
> nothing else. But $r^2=9$ gives $r=3$ **and** $r=-3$, and the question
> that follows almost always wants the second one.

**Percentages are ratios wearing a coat.** *Increases by 3%* is
$r=1.03$; *decreases by 40%* is $r=0.6$. The only difficulty is the
numbering: if $u_1$ is the value after the first year, then the value
after $n$ years is $u_n=u_1r^{\,n-1}$, and writing $r^{\,n}$ counts the
first year twice.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ2 Paper 2 Q7(a), 3 marks*

A geometric sequence has first term $80$ and fourth term $0.74088$.

**(a)** Find the second term.

*Write the ratio down as well as the term. A wrong ratio and a wrong
second term are two different mistakes, and it is worth knowing which
one you made.*
""")

code(r"""
q1r = ...        # the common ratio
q1u = ...        # the second term

mine = geometric(80, q1r)                    # the first term is given

verify_term('1 (r)', 0.74088, mine, 4)       # is the 4th term of yours 0.74088?
verify_term('1a', q1u, mine, 2)
""")

# ================================================================= теория 2
md(r"""
## Theory: adding the first $n$, and counting them

The subtraction at the top of this notebook gives

$$S_n=\frac{u_1\left(r^{\,n}-1\right)}{r-1}
=\frac{u_1\left(1-r^{\,n}\right)}{1-r}$$

Those are the same formula: multiply top and bottom of one by $-1$ and
you get the other. Use whichever keeps the numbers positive — with
$r>1$ the first, with $r<1$ the second — but never mix the top of one
with the bottom of the other.

For $11+44+176+704$ that is $u_1=11$, $r=4$, four terms:

$$S_4=\frac{11\left(4^4-1\right)}{4-1}=\frac{11\cdot255}{3}=935$$

> **Count the terms, do not assume them.** The number of terms is what
> the formula's exponent is, and it is not always the last index you can
> see. In $1+x+x^2+\dots+x^{\,n}$ there are $n+1$ terms, because the
> first one is $x^0$. There is a mark for saying so.

**A sum of sums is still a sum.** If $S_1+S_2+\dots+S_n$ is asked, write
each $S_k$ out first: it usually splits into a geometric series plus
something trivial, and the geometric half is what this formula is for.
""")

md(r"""
### Task 2 🟢 — *May 2024 TZ1 Paper 1 Q5, 5 marks*

Consider a geometric sequence with first term $1$ and common ratio $10$.
$S_n$ is the sum of the first $n$ terms of the sequence.

**(a)** Find an expression for $S_n$ in the form $\dfrac{a^{\,n}-1}{b}$,
where $a,b\in\mathbb Z^+$.

**(b)** Hence, show that
$S_1+S_2+S_3+\dots+S_n=\dfrac{10\left(10^{\,n}-1\right)-9n}{81}$.

*Part (b) is a "show that", so there is nothing to hand over at the end
of it. What is asked instead is the step that carries the marks: after
writing $S_k=\frac{10^k-1}{9}$, the sum splits into $\frac19\sum10^k$
minus $\frac19\sum1$, and only the first half is geometric. **Write down
that first half**, $10+100+\dots+10^{\,n}$, in terms of $n$.*
""")

code(r"""
q2s = ...        # S_n, in terms of n
q2t = ...        # the value of 10 + 100 + 1000 + ... + 10**n, in terms of n

mine = geometric(1, 10)

verify_total('2a', q2s, mine, n)
verify_total('2b', q2t, geometric(10, 10), n)   # the same ratio, ten times bigger
""")

md(r"""
### Task 3 🟢 — *May 2025 TZ1 Paper 1 Q5, 8 marks*

Consider a sequence of ten rectangular picture frames
$F_1,F_2,\dots,F_{10}$. Frame $F_1$ has width $4$ cm and height $5$ cm.
The width and height of frame $F_n$ are each increased by $50\%$ to give
the width and height of $F_{n+1}$, for $1\le n\le9$.

**(a) (i)** Show that the area of frame $F_n$ is
$20\left(\tfrac94\right)^{\,n-1}$ cm².
**(ii)** Hence find the **mean** area of the ten frames, in the form
$p\left(\left(\tfrac94\right)^{a}-1\right)$ cm², where
$p\in\mathbb Q^+$, $a\in\mathbb Z^+$.
**(b)** Find the **median** area of the ten frames, in the form
$q\left(\tfrac94\right)^{4}$ cm², where $q\in\mathbb Q^+$.

*Both sides grow by the same factor, so the area grows by its square —
that is where $\tfrac94$ comes from, and (a)(i) is that sentence.*

*Ten areas have no middle one: the median sits between the fifth and the
sixth. The check uses that directly — your median, doubled and added to
the first four areas, has to be the sum of the first six.*
""")

code(r"""
q3p = ...        # p
q3a = ...        # a
q3q = ...        # q

areas = geometric(20, Rational(9, 4))        # from (a)(i)

# ten of your means make the total of ten areas
from_mean = ... if blank(q3p, q3a) else 10 * q3p * (Rational(9, 4) ** q3a - 1)
# the first four areas plus twice your median make the first six
from_median = (... if blank(q3q)
               else total(areas, 4) + 2 * q3q * Rational(9, 4) ** 4)

verify_total('3a(ii)', from_mean, areas, 10)
verify_total('3b', from_median, areas, 6)
""")

# ================================================================= теория 3
md(r"""
## Theory: adding all of them, when that is allowed

Let $n$ grow in $S_n=\dfrac{u_1(1-r^{\,n})}{1-r}$. If $|r|<1$ then
$r^{\,n}\to0$, the bracket goes to $1$, and

$$S_\infty=\frac{u_1}{1-r}$$

If $|r|\ge1$ the terms do not shrink and there is no such number. Both
halves of that are examinable, and the second one more often than the
first.

$$45+18+7.2+\dots\quad r=0.4,\quad S_\infty=\frac{45}{1-0.4}=75$$

> **The condition is $|r|<1$, not $r<1$.** With $r=-3$ the terms are
> $7,-21,63,\dots$ — they grow, and $-3$ is certainly less than one.
> Writing the condition without the modulus signs is the standard way
> of losing that mark.

**"Show that the series converges"** is answered by naming $|r|$ and
comparing it with $1$ — in one line, for **both** values of $r$ if the
question produced two. Leaving out the second one is R0.

**Total distance is not the sum of the distances.** A particle that
swings out to $u_1$ and back to the start has travelled $2u_1$ in that
interval. If the question asks how far it travels altogether, the
sequence to sum is $2u_1,2u_2,\dots$
""")

md(r"""
### Task 4 🟢 — *November 2021 Paper 2 Q5, 9 marks*

The sum of the first $n$ terms of a geometric sequence is given by

$$S_n=\sum_{i=1}^{n}\frac23\left(\frac78\right)^{i}$$

**(a)** Find the first term of the sequence, $u_1$.
**(b)** Find $S_\infty$.
**(c)** Find the least value of $n$ such that $S_\infty-S_n<0.001$.

*The $\Sigma$ starts at $i=1$, so the first term is the whole summand at
$i=1$ — not the fraction standing in front of the bracket. That is
technique 4 arriving early, and it is worth two marks here.*

*In (c) the check walks the sequence and stops at the first $n$ where
your own $S_\infty$ satisfies the condition — so a wrong (b) costs you
(b) only.*
""")

code(r"""
q4u = ...        # the first term
q4s = ...        # the sum to infinity, exactly
q4n = ...        # the least n with S_inf - S_n < 0.001

mine = geometric(q4u, Rational(7, 8))        # the ratio is visible in the sigma

verify_term('4a', Rational(2, 3) * Rational(7, 8) ** 2, mine, 2)
verify_infinite('4b', q4s, mine, exact=True)
verify_least('4c', q4n, mine, lambda partial: q4s - partial < Rational(1, 1000))
""")

# ================================================================= теория 4
md(r"""
---
# 🟡 Part 2. When the ratio is what you are looking for

## Theory: three quantities in a geometric sequence

*"$a$, $s$, $t$ form a geometric sequence"* is not a list. It is one
equation, and it says the two ratios are equal:

$$\frac sa=\frac ts\qquad\Longrightarrow\qquad s^2=at$$

The middle term squared is the product of its neighbours — the same
statement as *"$s$ is the geometric mean of $a$ and $t$"*. Whenever
three things are said to be in geometric sequence, write that line
first; everything else in the question comes out of it.

**With a letter inside, it becomes a quadratic.** For $11,\ w,\ 44$:

$$w^2=11\cdot44=484\Longrightarrow w=\pm22$$

and both are real sequences: $11,22,44$ with $r=2$, and $11,-22,44$
with $r=-2$.

**Sometimes it collapses to a linear equation instead**, and that is not
a mistake — it is the quadratic terms cancelling. For $h-1,\ h+1,\ h+5$:

$$(h+1)^2=(h-1)(h+5)\Longrightarrow h^2+2h+1=h^2+4h-5
\Longrightarrow h=3$$

giving $2,4,8$. Expand both sides before deciding what kind of equation
you have.

> **The difference is not the ratio.** Equating $u_2-u_1$ with
> $u_3-u_2$ tests for an *arithmetic* sequence. The exam puts both
> conditions in one question precisely to see which one you write.
""")

md(r"""
### Task 5 🟡 — *May 2024 TZ2 Paper 1 Q10(b), 2 marks*

Consider the geometric sequence $a,\ s,\ t\dots$, where
$a,s,t\neq0$.

**(b)** Show that $s^2=at$.

*A "show that" with nothing to hand over — so write the third term
instead. Given $a$ and $s$, what must $t$ be?*
""")

code(r"""
q5t = ...        # the third term, in terms of a and s

verify_geometric('5', [a, s, q5t])
""")

md(r"""
### Task 6 🟡 — *May 2023 TZ1 Paper 1 Q10 (d)–(e), 5 marks*

*(Parts (a)–(c) of this question are arithmetic and are in A1. They
establish that the sequence $u_n$ has $u_1=5$ and $u_6=15$.)*

Consider a geometric sequence $v_n$, where $v_2=u_1$ and $v_4=u_6$.

**(d)** Find the possible values of the common ratio, $r$.
**(e)** Given that $v_{99}<0$, find $v_5$.

*The check for (d) is built out of the sequence itself: it takes your
$r$, walks two steps from $v_2$, and asks whether it lands on $15$ —
then solves that same condition itself to see whether you have missed
one.*
""")

code(r"""
q6r = [...]      # both possible values of the common ratio
q6n = ...        # the one that makes v99 negative
q6v = ...        # v5

# v2 is the first term the question gives us, so this sequence starts there:
# its 3rd term is v4.
verify_root_set('6d', q6r, Eq(term(geometric(5, r), 3), 15), var=r)
verify_term('6e', q6v, geometric(5, q6n), 4)
""")

md(r"""
### Task 7 🟡 — *May 2025 TZ3 Paper 1 Q10(b), 4 marks*

Consider the sequence $\{u_n\}$ whose first three terms are

$$u_1=k-5,\qquad u_2=3-2k,\qquad u_3=5k+3,\qquad k\in\mathbb R$$

Consider the case where $k=12$.

**(i)** Show that the first three terms of $\{u_n\}$ form a geometric
sequence.
**(ii)** Given that $\{u_n\}$ is geometric, state a reason why the sum
of an infinite number of terms of this sequence does not exist.

*Part (ii) has no cell: it is one sentence, and the sentence is in the
solutions. For (i), write the three terms out and the ratio you got by
dividing them — the check compares your terms with the question's own
expressions at $k=12$, and separately asks whether they are geometric.*
""")

code(r"""
q7t = [...]      # the first three terms when k = 12
q7r = ...        # the common ratio

printed = [k - 5, 3 - 2 * k, 5 * k + 3]      # the question's own expressions

verify_start('7(i)', q7t, ratios(lambda i: printed[i - 1].subs(k, 12)))
verify_geometric('7(i) geometric', q7t)
verify_ratio('7(i) r', q7r, q7t)
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 3. The smallest $n$, and ratios that are not numbers

## Theory: forcing an integer out

*"Find the least value of $n$ such that …"* is never solved by solving.
The inequality gives a fractional boundary, and the answer is the
integer on the correct side of it.

$$2\cdot3^{\,n}>5000\ \Longrightarrow\ 3^{\,n}>2500\ \Longrightarrow\
n>\frac{\ln 2500}{\ln 3}=7.122\ldots\ \Longrightarrow\ n=8$$

Three ways to lose this:

- **rounding the wrong way.** $n>7.122$ rounds *up*. Had the inequality
  been $<$, it would round *down*, and the boundary itself would need
  checking;
- **taking logs of a shrinking ratio without flipping.** $\ln r<0$ when
  $|r|<1$, and dividing by it reverses the inequality;
- **using $u_n$ where the question said $S_n$.** The November 2021
  markscheme awards **M0** for that by name.

> On a calculator paper you do not have to take logs at all. The
> markscheme lists *sketch* **OR** *table of values* **OR** *algebraic
> manipulation involving logarithms* as equals. A table is often faster,
> and it never flips a sign the wrong way.

**Check the neighbour.** Whatever route you took, evaluate at $n$ and at
$n-1$. Two numbers, ten seconds, and the answer is either confirmed or
off by one — which is the only way this question is ever wrong.
""")

md(r"""
### Task 8 🔴 — *November 2022 Paper 2 Q3, 5 marks*

A geometric sequence has a first term of $50$ and a fourth term of
$86.4$. The sum of the first $n$ terms of the sequence is $S_n$.

Find the smallest value of $n$ such that $S_n>33\,500$.
""")

code(r"""
q8r = ...        # the common ratio
q8n = ...        # the smallest n with S_n > 33500

mine = geometric(50, q8r)

verify_term('8 (r)', 86.4, mine, 4)
verify_least('8', q8n, mine, lambda partial: partial > 33500)
""")

md(r"""
### Task 9 🔴 — *May 2024 TZ1 Paper 2 Q1, 7 marks*

Darren buys a car for $\$35\,000$. The value of the car decreases by
$15\%$ in the first year.

**(a)** Find the value of the car at the end of the first year.

After the first year, the value decreases by $11\%$ in each subsequent
year.

**(b)** Find the value of Darren's car $10$ years after he buys it,
giving your answer to the nearest dollar.

**(c)** When Darren has owned the car for $n$ complete years, its value
is less than $10\%$ of its original value. Find the least value of $n$.

*The first year is different from all the others, so it is not part of
the geometric sequence — it produces the sequence's **first term**.
After that the ratio is $0.89$ and the value after $n$ years is the
$n$th term, not the $(n+1)$th.*
""")

code(r"""
q9a = ...        # the value after one year
q9b = ...        # the value after ten years, to the nearest dollar
q9n = ...        # the least number of complete years

mine = geometric(q9a, 0.89)                  # your first term, the stated ratio

verify_term('9a', 35000 * 0.85, mine, 1)
verify_term('9b', q9b, mine, 10)
verify_least('9c', q9n, mine, lambda value: value < 3500, what='term')
""")

# ================================================================= теория 6
md(r"""
## Theory: reading a series that was never written out

A $\Sigma$ hides both numbers you need, and neither is where it looks.

$$\sum_{i=1}^{\infty}\left(\frac25\right)^{i}
=\frac25+\frac4{25}+\frac8{125}+\dots$$

- **the first term** is the whole summand evaluated at the *lower
  limit* — here $\tfrac25$, and if the limit had been $i=0$ it would be
  $1$;
- **the ratio** is what changes from one summand to the next, which is
  whatever is being raised to the power — here $\tfrac25$ again, but
  only by coincidence.

$$S_\infty=\frac{2/5}{1-2/5}=\frac23$$

> A constant in front of the bracket is **not** the first term. In
> $\sum_{i=1}^{\infty}c\,\rho^{\,i}$ the first term is $c\rho$, and
> reading it as $c$ is worth two marks in task 4.

**Repeating decimals are geometric series**, and that is the whole
technique behind writing them as fractions. $0.\overline{4}$ is
$\tfrac4{10}+\tfrac4{100}+\dots$ with $r=\tfrac1{10}$, giving
$\tfrac{4/10}{9/10}=\tfrac49$. When only part of the decimal repeats,
split it: the non-repeating head is a separate fraction, added on at the
end.
""")

md(r"""
### Task 10 🔴 — *November 2025 TZ1 Paper 2 Q6, 5 marks*

Consider the infinite series
$\displaystyle\sum_{k=0}^{\infty}\left(\frac{53}{1000}\right)
\left(\frac1{100}\right)^{k}$.

**(a)** Find the exact value of $S_\infty$.

Let $0.2\overline{53}$ represent the repeating decimal
$0.2535353\ldots$

**(b)** Use your answer from part (a) to express $0.2\overline{53}$ as a
fraction whose numerator and denominator have no common factors.

*This $\Sigma$ starts at $k=0$, so here the constant in front **is** the
first term. Compare with task 4, where it was not.*

*In (b) the check subtracts the head of the decimal from your fraction
and asks whether what is left is the series — so the two answers are
tied together, and (b) cannot accidentally be right if (a) is wrong.*
""")

code(r"""
q10s = ...       # the exact sum to infinity
q10f = ...       # 0.2535353... as a fraction in lowest terms

series = geometric(Rational(53, 1000), Rational(1, 100))

verify_infinite('10a', q10s, series, exact=True)
verify_infinite('10b', ... if blank(q10f) else q10f - Rational(1, 5),
                series, exact=True)
""")

# ================================================================= теория 7
md(r"""
## Theory: when the ratio is an expression

Nothing in the three formulas needs $r$ to be a number. In

$$1+\frac x3+\frac{x^2}9+\dots$$

the ratio is $\tfrac x3$, and everything goes through unchanged:

$$S_n=\frac{1-(x/3)^{\,n}}{1-x/3},\qquad
S_\infty=\frac1{1-x/3}=\frac3{3-x}\ \text{ for }|x|<3$$

Two things change, and both carry marks.

**The convergence condition becomes a set of $x$.** $|r|<1$ is an
inequality in $x$ once you substitute, and it is $x$ the question asks
about: $\left|\tfrac x3\right|<1$ means $-3<x<3$.

**The excluded value has to be named.** $S_n$ divides by $r-1$, so
$r=1$ is not allowed, and a question about $1+x+x^2+\dots+x^{\,n}$ says
*"for $x\ne1$"* for that reason. Saying it back is part of the answer.

> **Watch the sign inside the ratio.** For $1-x^2+x^4-\dots$ the ratio
> is $-x^2$, not $x^2$, and $1-(-x^2)$ is $1+x^2$. Half the marks in
> this technique are that one minus sign.
""")

md(r"""
### Task 11 🔴 — *November 2022 Paper 3 Q1(e), 2 marks*

By considering $f(x)=1+x+x^2+\dots+x^{\,n}$ as a geometric series, for
$x\ne1$, show that

$$f(x)=\frac{x^{\,n+1}-1}{x-1}$$

*Two marks, and one of them is **R1 for a clear indication of how many
terms there are**. Write that number down first.*
""")

code(r"""
q11n = ...       # how many terms the series has, in terms of n
q11s = ...       # the sum of that many terms

verify_total('11', q11s, geometric(1, x), q11n, var=x, values=(2, 3, Rational(1, 2)))
""")

md(r"""
### Task 12 🔴 — *May 2025 TZ1 Paper 2 Q12(b) and November 2025 TZ3 Paper 3 Q2(a), 4 marks*

**(i)** Consider $f_n(x)=\displaystyle\sum_{r=0}^{n}\left(-2x^2\right)^{r}$.
Given that $f_3(x)=1-2x^2+4x^4-8x^6$, write down a similar expression
for $f_4(x)$ in ascending powers of $x$.

**(ii)** Given $|x|<1$, find the sum to infinity of the geometric series
$1-x^2+x^4-x^6+\dots$

*In (i) the ratio is $-2x^2$ and the sum is finite — count the terms
from $r=0$. In (ii) it is $-x^2$ and the sum is infinite, so the answer
is a function of $x$.*
""")

code(r"""
q12f = ...       # f4(x), in ascending powers of x
q12s = ...       # the sum to infinity of 1 - x^2 + x^4 - ...

verify_total('12(i)', q12f, geometric(1, -2 * x ** 2), 5,
             var=x, values=(2, Rational(1, 3)))
verify_infinite('12(ii)', q12s, geometric(1, -x ** 2),
                var=x, values=(Rational(1, 2), Rational(1, 3)))
""")

md(r"""
### Task 13 🔴 — *November 2025 TZ3 Paper 2 Q10(e), 5 marks*

A particle $P$ moves in a straight line so that its displacement from a
fixed point O at time $t$ is $s(t)=2^{\left(1-\frac t5\right)}
\sin\!\left(\frac{2\pi t}3\right)$, $t\ge0$. It passes through O every
$T$ seconds.

A sequence $u_1,u_2,u_3\dots$ is formed where $u_1,u_2,u_3\dots$ are the
largest **distances** from O in each of the intervals $0<t<T$,
$T<t<2T$, $2T<t<3T$ respectively. Earlier parts of the question give

$$u_1=1.80645,\qquad u_2=1.46729,\qquad u_3=1.19181$$

It is known that $u_1,u_2,u_3\dots$ form a geometric sequence.

**(i)** Determine the value of the common ratio $r$.
**(ii)** Calculate the **total distance** travelled by the particle if
it were to continue to move in this way indefinitely.

*In each interval the particle goes out to its farthest point and comes
back, so it covers twice that distance. The check sums a sequence whose
first term is $2u_1$ — which is exactly the modelling step the
markscheme gives its third mark for.*
""")

code(r"""
q13r = ...       # the common ratio, to three significant figures
q13d = ...       # the total distance travelled

out_and_back = geometric(2 * 1.80645, 1.46729 / 1.80645)   # out and back each time

verify_ratio('13(i)', q13r, [1.80645, 1.46729, 1.19181])
verify_infinite('13(ii)', q13d, out_and_back)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `ratio` | two terms, or a percentage; divide to get $r$ |
| `sum` | a finite number of terms is being added |
| `infinite` | $S_\infty$, *forever*, or *why does it not exist* |
| `sigma` | the series is written only as a $\Sigma$ |
| `condition` | *form a geometric sequence*, with a letter inside |
| `least` | *smallest $n$*, *how many years*; round an integer out |
| `letter` | the ratio is an expression in $x$ |

1. A geometric sequence has $u_1=6$ and $u_4=48$. Find $u_2$.
2. Find $9+3+1+\tfrac13+\dots$ continued forever.
3. The numbers $p$, $p+4$ and $4p$ form a geometric sequence. Find $p$.
4. A colony doubles every day and starts at $200$. After how many days does it pass a million?
5. Evaluate $\displaystyle\sum_{i=1}^{\infty}\frac74\left(\frac13\right)^{i}$.
6. Find $2+6+18+\dots+2\cdot3^{\,9}$.
7. For which $x$ does $1+4x+16x^2+\dots$ have a sum?
8. A ball rebounds to $60\%$ of its height each bounce. Explain why the total distance is finite.
9. The terms $u_1=m-1$, $u_2=m+3$, $u_3=5m-3$ are geometric. Find $m$.
10. A savings account grows by $4\%$ a year from $\$500$. When does it first exceed $\$800$?
11. A sequence has $u_3=20$ and $u_6=2.5$. Find the common ratio.
12. Write $\displaystyle\sum_{k=0}^{\infty}\left(\frac{x}{2}\right)^{k}$ as a rational function.
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
## On the clock — *May 2025 TZ3 Paper 1 Q10(c), 7 marks*

**Seven marks, ten minutes.** No hints this time.

The sequence $\{u_n\}$ has first three terms

$$u_1=k-5,\qquad u_2=3-2k,\qquad u_3=5k+3,\qquad k\in\mathbb R$$

The sequence is geometric for a second value of $k$ (the first, $k=12$,
was task 7).

**(i)** Show that $k^2-10k-24=0$.
**(ii)** Find the first three terms of $\{u_n\}$ for this second value
of $k$.
**(iii)** Hence, write down the value of $S_{2m}$, the sum of the first
$2m$ terms, for this second value of $k$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_k = ...       # the second value of k
qt_r = ...       # the common ratio it gives
qt_t = [...]     # the first three terms
qt_s = ...       # S_2m

printed = [k - 5, 3 - 2 * k, 5 * k + 3]      # the question's own expressions

verify_root_set('timer (i)', [12, qt_k], Eq(k ** 2 - 10 * k - 24, 0), var=k)
verify_geometric('timer (ii)', qt_t)
verify_start('timer (ii) terms', qt_t,
             ratios(lambda i: printed[i - 1].subs(k, qt_k)
                    if not blank(qt_k) else ...))
verify_total('timer (iii)', qt_s, geometric(qt_t[0], qt_r), 2 * m)
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1** From $u_1$ to $u_4$ there are three steps:

$$80r^3=0.74088\Longrightarrow r^3=0.0092610\Longrightarrow
\boxed{r=0.21}$$

The cube root is exact — $0.21^3=0.009261$ — which is the paper telling
you the ratio is a tidy number and you have not slipped. Then

$$u_2=80(0.21)=\boxed{16.8}$$

---

**2 (a)** $u_1=1$, $r=10$, so

$$S_n=\frac{1\left(10^{\,n}-1\right)}{10-1}=\boxed{\frac{10^{\,n}-1}{9}}$$

that is $a=10$, $b=9$.

**2 (b)** Sum those:

$$\sum_{k=1}^{n}S_k=\sum_{k=1}^{n}\frac{10^{k}-1}{9}
=\frac19\left(\sum_{k=1}^{n}10^{k}-\sum_{k=1}^{n}1\right)$$

The first sum is geometric with first term $10$, ratio $10$ and $n$
terms:

$$\sum_{k=1}^{n}10^{k}=\frac{10\left(10^{\,n}-1\right)}{9}$$

and the second is just $n$. So

$$\frac19\left(\frac{10\left(10^{\,n}-1\right)}9-n\right)
=\frac{10\left(10^{\,n}-1\right)-9n}{81}$$

The two nines multiplying into $81$ is the whole point of the given
form; if your denominator is $9$, you have divided once instead of
twice.

---

**3 (a)(i)** Width and height are both geometric with ratio $\tfrac32$,
so

$$\text{area of }F_n=4\left(\tfrac32\right)^{n-1}\times
5\left(\tfrac32\right)^{n-1}=20\left(\tfrac94\right)^{n-1}$$

**(ii)** The areas are geometric with $u_1=20$, $r=\tfrac94$:

$$S_{10}=\frac{20\left(\left(\tfrac94\right)^{10}-1\right)}{\tfrac94-1}
=16\left(\left(\tfrac94\right)^{10}-1\right)$$

and the mean is a tenth of that:

$$\frac{16}{10}\left(\left(\tfrac94\right)^{10}-1\right)
=\boxed{\tfrac85\left(\left(\tfrac94\right)^{10}-1\right)}$$

so $p=\tfrac85$ and $\boxed{a=10}$. Forgetting to divide by ten is the
standard loss here — the question says *mean*, not *total*.

**3 (b)** Ten values have no middle one, so the median is the mean of
the 5th and the 6th:

$$\frac{20\left(\tfrac94\right)^{4}+20\left(\tfrac94\right)^{5}}{2}
=\frac{20\left(\tfrac94\right)^{4}\left(1+\tfrac94\right)}{2}
=\boxed{\tfrac{65}2\left(\tfrac94\right)^{4}}$$

Factoring $\left(\tfrac94\right)^4$ out of both terms is what turns the
answer into the demanded form; expanding instead gives a correct number
in the wrong shape, and the shape is what is marked.

---

**4 (a)** The summand at $i=1$:

$$u_1=\frac23\cdot\frac78=\frac{14}{24}=\boxed{\frac7{12}}$$

Not $\tfrac23$. The $\tfrac78$ is inside the sum, so it belongs to every
term including the first.

**4 (b)** $r=\tfrac78$, and $\left|\tfrac78\right|<1$:

$$S_\infty=\frac{7/12}{1-7/8}=\frac{7/12}{1/8}=\boxed{\frac{14}3}$$

**4 (c)** What is left after $n$ terms is itself a geometric series, so

$$S_\infty-S_n=\frac{14}3-\frac{\tfrac7{12}\left(1-\left(\tfrac78\right)^n\right)}
{\tfrac18}<0.001$$

Solving — by table, sketch or logarithms — gives $n>63.267\ldots$, so

$$\boxed{n=64}$$

Check the neighbours, which is what the markscheme prints:
$S_\infty-S_{63}=0.001036$ (too big) and $S_\infty-S_{64}=0.000906$
(small enough). Solving $S_\infty-u_n<0.001$ instead of $S_\infty-S_n$
scores **M0** — the difference between a term and a sum, again.

---

**5** Equal ratios:

$$\frac sa=\frac ts\Longrightarrow s^2=at\Longrightarrow
\boxed{t=\frac{s^2}a}$$

Two marks, and the second is for a correct equation before the
rearrangement — $\left(\tfrac sa\right)^2=\tfrac ta$ counts, $s^2=at$
written straight down does not.

---

**6 (d)** $v_2=5$ and $v_4=15$ are two steps apart:

$$v_4=v_2r^2\Longrightarrow 5r^2=15\Longrightarrow r^2=3
\Longrightarrow \boxed{r=\pm\sqrt3}$$

The markscheme is explicit: $\sqrt3$ alone, with no working, is
**M1A1A0**.

**6 (e)** $v_{99}=v_2r^{97}$, and $97$ is odd, so the sign of $v_{99}$
is the sign of $r$. Negative means $r=-\sqrt3$, and then

$$v_5=v_2r^3=5\left(-\sqrt3\right)^3=5\left(-3\sqrt3\right)
=\boxed{-15\sqrt3}$$

which is $-\tfrac{45}{\sqrt3}$ in the markscheme's form — the same
number.

---

**7 (i)** With $k=12$ the terms are

$$u_1=7,\qquad u_2=-21,\qquad u_3=63$$

$$\frac{-21}{7}=-3,\qquad \frac{63}{-21}=-3$$

Equal, so the three terms are geometric with $\boxed{r=-3}$.

**7 (ii)** $|r|=3\ge1$, so the terms do not shrink and the infinite sum
does not exist. Saying *"$r<1$ is false"* is not enough on its own: the
condition is on $|r|$, and $-3<1$ is true.

---

**8** From $u_1$ to $u_4$, three steps:

$$50r^3=86.4\Longrightarrow r^3=1.728\Longrightarrow r=1.2$$

$$S_n=\frac{50\left(1.2^{\,n}-1\right)}{0.2}=250\left(1.2^{\,n}-1\right)
>33\,500$$

$$1.2^{\,n}>135\Longrightarrow n>\frac{\ln135}{\ln1.2}=26.9045\ldots
\Longrightarrow\boxed{n=27}$$

The neighbours: $S_{26}=28\,368.8$ and $S_{27}=34\,092.6$. Rounding
$26.9$ down is the only mistake available here, and it is the common
one.

---

**9 (a)** A $15\%$ loss leaves $85\%$:

$$0.85\times35\,000=\boxed{\$29\,750}$$

**9 (b)** From then on the ratio is $0.89$, and $29\,750$ is the value
after **one** year, so ten years later is nine more steps:

$$29\,750\times0.89^{\,9}=\boxed{\$10\,423}$$

Using $0.89^{10}$ counts the first year twice and gives $\$9276$.

**9 (c)** $10\%$ of the original is $\$3500$:

$$29\,750\times0.89^{\,n-1}<3500\Longrightarrow n>19.364\ldots
\Longrightarrow\boxed{n=20}$$

At $n=19$ the car is worth $\$3651.80$ — still too much — and at
$n=20$ it is $\$3250.10$. The finance app on a GDC answers the whole
thing with $I\%=-11$, $PV=-29750$, $FV=3500$.

---

**10 (a)** This $\Sigma$ starts at $k=0$, so the first term is the
constant itself and the ratio is $\tfrac1{100}$:

$$S_\infty=\frac{53/1000}{1-1/100}=\frac{53}{1000}\cdot\frac{100}{99}
=\boxed{\frac{53}{990}}$$

which is $0.0535353\ldots$ — the repeating tail of the decimal in (b).

**10 (b)** Split the decimal at the point where repetition starts:

$$0.2535353\ldots=0.2+0.0535353\ldots=\frac15+\frac{53}{990}
=\frac{198}{990}+\frac{53}{990}=\boxed{\frac{251}{990}}$$

$251$ is prime, so nothing cancels. Trying to write the whole decimal as
a single series instead — with $\tfrac{253}{1000}$ as a first term —
does not work: the $2$ does not repeat.

---

**11** The series runs $x^0,x^1,\dots,x^{\,n}$, so there are
$\boxed{n+1}$ terms, with $u_1=1$ and $r=x$:

$$f(x)=\frac{1\left(x^{\,n+1}-1\right)}{x-1}=\boxed{\frac{x^{\,n+1}-1}{x-1}}$$

The **R1** is for the count. Writing $\tfrac{x^{\,n}-1}{x-1}$ — the
formula applied with $n$ terms — is the mistake the mark exists to
catch.

---

**12 (i)** $f_4$ has one more term than $f_3$, and the next power of
$-2x^2$ is $\left(-2x^2\right)^4=16x^8$:

$$f_4(x)=\boxed{1-2x^2+4x^4-8x^6+16x^8}$$

Five terms, because $r$ runs from $0$ to $4$.

**12 (ii)** Here $u_1=1$ and $r=-x^2$, and $|x|<1$ makes $|r|<1$:

$$S_\infty=\frac1{1-\left(-x^2\right)}=\boxed{\frac1{1+x^2}}$$

The sign is the whole question. Reading the ratio as $x^2$ gives
$\tfrac1{1-x^2}$, which is the sum of a different series.

---

**13 (i)** Divide any two consecutive terms:

$$r=\frac{1.46729}{1.80645}=0.812252\ldots\Longrightarrow\boxed{r=0.812}$$

Dividing $u_3$ by $u_1$ gives $r^2$, not $r$ — take the square root if
you go that way.

**13 (ii)** Each interval takes the particle out to $u_i$ and back, so
the distance covered in it is $2u_i$:

$$\text{total}=2\sum_{i=1}^{\infty}u_i
=2\cdot\frac{1.80645}{1-0.812252}=2(9.62167)=\boxed{19.2\ \text{cm}}$$

The markscheme gives a mark for the doubling on its own, and warns
against any answer smaller than $2u_1=3.61$ — which is what you get if
the ratio came out wrong.

---

## Timer

**(i)** Geometric means the two ratios are equal:

$$\frac{3-2k}{k-5}=\frac{5k+3}{3-2k}\Longrightarrow (3-2k)^2=(k-5)(5k+3)$$

$$9-12k+4k^2=5k^2-22k-15\Longrightarrow k^2-10k-24=0$$

**(ii)** $(k-12)(k+2)=0$, and $k=12$ was task 7, so
$\boxed{k=-2}$. The terms are

$$u_1=-2-5=-7,\qquad u_2=3+4=7,\qquad u_3=-10+3=-7$$

$$\boxed{-7,\ 7,\ -7}$$

with $r=-1$. Substituting $k$ into the wrong expression is the standard
slip; $u_3$ is $5k+3$, not $3-2k$.

**(iii)** With $r=-1$ the terms cancel in pairs:

$$(-7+7)+(-7+7)+\dots$$

and $2m$ terms make exactly $m$ such pairs, so

$$\boxed{S_{2m}=0}$$

No formula is needed, and using one is worse than useless: $r=-1$ makes
$\tfrac{u_1(r^{2m}-1)}{r-1}$ a fraction $\tfrac{0}{-2}$, which is right
but tells you nothing about why.
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
