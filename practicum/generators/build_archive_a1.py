"""Собирает архивный ноутбук A1: вся тема арифметических прогрессий подряд.

Десятый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1 и C2.
Практикум учит: лестница из приёмов, теория перед каждым, три уровня
сложности, тренажёр распознавания, задание на время. Он берёт из корпуса
не всё, а то, на чём приём виден лучше всего.

Этот не учит. Он даёт набивать руку: **вся тема подряд, по тем же
девяти приёмам, без единой строчки теории**. Сорок семь вопросов,
135 баллов — ровно то, что архив спрашивает про арифметические
последовательности с мая 2021 по ноябрь 2025.

Разметка взята из карточки number-algebra-sequences.yaml: поле blocks
у каждого приёма. Никакой отдельной разметки формат не заводит.

Три места, где тема заставила формат подвинуться.

**Вопрос, разрезанный между практикумами.** Майский 2023 TZ1 вопрос 10
и майский 2025 TZ3 вопрос 10 начинаются арифметической
последовательностью и кончаются геометрической. Здесь они обрываются
на середине, и в самом ноутбуке об этом сказано прямым текстом:
оставшиеся пункты уходят в A2.

**Три вопроса проверить нельзя.** «State in words», «sketch a diagram»
и «write down an expression in sigma notation» — у них нет ячейки,
а в разборе выписано то, что принимает схема оценивания.

**Один хеш из пятидесяти одного.** Сумма квадратов 1 + 4 + 9 — не
арифметическая последовательность, и проверке её сложением не получить.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_a1.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/number_algebra/archive-a1-arithmetic-sequences.ipynb')

ANSWERS = {
    # § 1. Which term is it
    'q1_1': '12',
    'q1_2': '16',
    'q1_3': '-3',
    'q1_4': '25',
    'q1_5d': '-6',
    'q1_5': '-36',
    # § 2. Add the first n
    'q2_1': 'n',
    'q2_2': '14',
    'q2_4': '55',
    'q2_5': '26',
    'q2_6': '25',
    'q2_9': '3*n - 2',
    'q2_10': '15',
    'q2_11': '26',
    'q2_12': '3*n - 1',
    'q2_13': '13',
    # § 3. Two facts, two unknowns
    'q3_1u': '-6',
    'q3_1d': '2',
    'q3_2u': '-12',
    'q3_2d': '3',
    'q3_3p': '3',
    'q3_3q': '2',
    # § 4. From the sum back to the terms
    'q4_1s': '45',
    'q4_1u': '15',
    'q4_2': '5',
    'q4_3': '2*n + 3',
    'q4_4': '25',
    # § 5. The constant difference as a condition
    'q5_1': 'Rational(4, 5)',
    'q5_2': '7',
    'q5_3': '(a + q)/2',
    'q5_4': '2*p - 1',
    'q5_5': '[9, 5, 1, -3]',
    'q5_6': '4*pi',
    # § 6. Quantities with no index
    'q6_1': 'Rational(-3, 2)',
    'q6_2': '-m**2/(m + 2)',
    'q6_3': '-2',
    'q6_4': 'b - a',
    'q6_5': '-(a**2 - a*b + b)/(2*a)',
    'q6_6': 'Rational(-1, 2)',
    'q6_7': '[2*x**2 - 2, -2*x**2 + 2]',
    'q6_8': '(2*b - 1)/4',
    'q6_9b': '[(-5 + 2*sqrt(5))/2, (-5 - 2*sqrt(5))/2]',
    'q6_9c': '[(-9 + 4*sqrt(5))/2, (-9 - 4*sqrt(5))/2]',
    # § 7. The greatest sum
    'q7_1': '750',
    'q7_2d': '-6.32',
    'q7_2': '547.04',
    # § 8. n has to be a whole number
    'q8_1': '210',
    'q8_1i': '20',
    'q8_1j': '12',
    'q8_2': '13',
    'q8_2k': '5',
    'q8_3': '[-4*x + 8, -3*x + 9]',
    # § 9. Terms that are logarithms
    'q9_1p': 'Rational(2, 3)',
    'q9_1d': '-ln(x)/3',
    'q9_1n': '9',
    'q9_2d': '-4 - ln(3)',
    'q9_2s': '-90 - 25*ln(3)',
}

# Единственный хеш ноутбука: сумма квадратов 1 + 4 + 9 арифметической
# последовательностью не является, и сложением проверке её не получить.
SQUARES = digest('14')

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
# A1 archive — arithmetic sequences and sums, all of it

**Forty-seven questions, 135 marks.** Every question the archive asks
about arithmetic sequences, from May 2021 to November 2025, in the order
of the nine techniques rather than the order of the papers.

No theory. No worked examples. Open it, answer fifty questions, close it.
The theory is in the practicum, `practicum-a1-arithmetic-sequences.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Which term is it | 5 | 11 |
| 2 | Add the first $n$ | 13 | 22 |
| 3 | Two facts, two unknowns | 3 | 15 |
| 4 | From $S_n$ back to $u_n$ | 4 | 11 |
| 5 | The constant difference as a condition | 6 | 16 |
| 6 | Quantities with no index | 9 | 25 |
| 7 | The greatest sum | 2 | 7 |
| 8 | $n$ has to be a whole number | 3 | 10 |
| 9 | Terms that are logarithms | 2 | 18 |

Answers go on one line each. The checks are the same ones the practicum
uses and they store nothing: a progression is handed over as a rule — a
first term and a step — and the check walks it.

**Three questions have no cell.** *State in words*, *sketch a diagram*
and *write down an expression in sigma notation* cannot be checked by
anything; what the markscheme accepts for them is written out in the
solutions at the end.

**Two questions stop in the middle.** May 2023 TZ1 Q10 and May 2025 TZ3
Q10 begin arithmetic and finish geometric. Their later parts are in the
A2 archive, and it is said again where it happens.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + progression, term, total, ln, pi, ...

language('en')                 # this notebook is in English, and so are the checks

n = symbols('n')               # the index: every one of these papers calls it n
a, b, d, m, p, q = symbols('a b d m p q')
x = symbols('x', positive=True)   # every paper here says x > 1
                               # k already comes from kit


# Every progression below may be built from an answer you have not written
# yet. The helpers return an empty progression in that case, so the
# notebook runs top to bottom while it is still blank.

def terms(rule):
    # the progression whose nth term is rule(n)
    try:
        first, second = rule(1), rule(2)
    except TypeError:
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
    return progression(first, second - 2 * first)


def by_n(expr):
    # the progression whose nth term is your expression in n
    return terms(lambda i: expr.subs(n, i) if expr is not Ellipsis else ...)


def triple(slope, constant):
    # the AS-linear definition: the slope, the root, the constant
    return ([Ellipsis] * 3 if blank(slope, constant)
            else [slope, -constant / slope, constant])


def five_of(quad):
    # the AS-quadratic definition: a, r1, b, r2, c
    if blank(quad):
        return [Ellipsis] * 5
    # x is declared positive above, and a positive x hides the negative
    # root; the roots of a quadratic are found on a letter that carries
    # no such promise
    z = symbols('z')
    here = quad.subs(x, z)
    lead, middle, last = Poly(here, z).all_coeffs()
    roots = sorted(solve(here, z), key=float)
    if float(middle) < float(lead):
        roots = roots[::-1]            # the sequence runs downhill
    return [lead, roots[0], middle, roots[1], last]


print('ready; sympy', sp.__version__)
print('a progression:', progression(3, 2), '→ term 5 is', term(progression(3, 2), 5))
""")

# ============================================================ § 1
md(r"""
---
# § 1. Which term is it

**Five questions, 11 marks.** $u_n=u_1+(n-1)d$, read forwards and
backwards.
""")

md(r"""
### 1.1 — *May 2022 TZ2 Paper 1 Q1(a), 1 mark*

The $n$th term of an arithmetic sequence is given by $u_n=15-3n$.
State the value of the first term, $u_1$.

### 1.2 — *May 2022 TZ2 Paper 1 Q1(b), 2 marks*

Given that the $n$th term of this sequence is $-33$, find the value of $n$.

### 1.3 — *May 2022 TZ2 Paper 1 Q1(c), 2 marks*

Find the common difference, $d$.
""")

code(r"""
q1_1 = ...       # the first term
q1_2 = ...       # the value of n for which the term is -33
q1_3 = ...       # the common difference

mine = progression(q1_1, q1_3)

verify_term('1.1, 1.3', 15 - 3 * n, mine, n)
verify_term('1.2', -33, mine, q1_2)
""")

md(r"""
### 1.4 — *May 2021 TZ2 Paper 2 Q2(a), 2 marks*

An arithmetic sequence has first term $60$ and common difference $-2.5$.
Given that the $k$th term of the sequence is zero, find the value of $k$.
""")

code(r"""
q1_4 = ...       # the index of the zero term

verify_term('1.4', 0, progression(60, -2.5), q1_4)
""")

md(r"""
### 1.5 — *November 2025 TZ1 Paper 1 Q1(a), 4 marks*

The 1st and 5th terms of an arithmetic sequence are $36$ and $12$
respectively. Find the 13th term of this arithmetic sequence.
""")

code(r"""
q1_5d = ...      # the common difference
q1_5 = ...       # the 13th term

mine = progression(36, q1_5d)

verify_term('1.5 (d)', 12, mine, 5)
verify_term('1.5', q1_5, mine, 13)
""")

# ============================================================ § 2
md(r"""
---
# § 2. Add the first $n$

**Thirteen questions, 22 marks.** $S_n=\frac n2(u_1+u_n)$, and the
recurring trick of the exam: what is being added is itself an arithmetic
sequence, and finding *that* is the whole of the work.
""")

md(r"""
### 2.1 — *November 2022 Paper 3 Q1(a), 1 mark*

This question investigates series of the form
$\sum_{i=1}^n i^q=1^q+2^q+3^q+\dots+n^q$ where $n,q\in\mathbb Z^+$.
When $q=1$, the series is arithmetic.

Show that $\displaystyle\sum_{i=1}^n i=\tfrac12n(n+1)$.

*A "show that": the printed formula is the question's, so what is asked
here is the sequence being added — its $n$th term.*
""")

code(r"""
q2_1 = ...       # the nth term of the series being added, in terms of n

verify_total('2.1', n * (n + 1) / 2, by_n(q2_1), n)
""")

md(r"""
### 2.2 — *November 2022 Paper 3 Q1(b)(i), 1 mark*

Consider the case when $q=2$. The following table gives values of $n^2$
and $\sum_{i=1}^n i^2$ for $n=1,2,3$:

| $n$ | $n^2$ | $\sum_{i=1}^n i^2$ |
|---|---|---|
| 1 | 1 | 1 |
| 2 | 4 | 5 |
| 3 | 9 | $p$ |

Write down the value of $p$.

*The only hashed answer in the notebook: $1+4+9$ is not an arithmetic
sequence, and the check cannot walk it.*
""")

code("""
q2_2 = ...       # the value of p

check_num('2.2', q2_2, 2, '""" + SQUARES + """')
""")

md(r"""
### 2.3 — *November 2022 Paper 3 Q1(d)(iii), 1 mark*

Using sigma notation, write down an expression for $f_q(1)$, where
$f_q(x)=\sum_{i=1}^n i^q x^i$.

*No cell: the answer is a piece of notation, and nothing here can check
notation. It is written out in the solutions.*
""")

md(r"""
### 2.4 — *May 2022 TZ1 Paper 3 Q1(a)(i), 2 marks*

For an $r$-sided regular polygon, the $n$th polygonal number $P_r(n)$ is
given by

$$P_r(n)=\frac{(r-2)n^2-(r-4)n}{2}$$

For triangular numbers, verify that $P_3(n)=\dfrac{n(n+1)}{2}$.

*Substituting $r=3$ is the mark. What is asked here instead is the
triangular number the formula then produces at $n=10$ — the same
substitution, with something to check.*
""")

code(r"""
q2_4 = ...       # the 10th triangular number

verify_total('2.4', q2_4, terms(lambda i: i), 10)
""")

md(r"""
### 2.5 — *May 2022 TZ1 Paper 3 Q1(a)(ii), 2 marks*

The number $351$ is a triangular number. Determine which one it is.
""")

code(r"""
q2_5 = ...       # which triangular number 351 is

verify_total('2.5', 351, terms(lambda i: i), q2_5)
""")

md(r"""
### 2.6 — *May 2022 TZ1 Paper 3 Q1(b)(i), 2 marks*

Show that $P_3(n)+P_3(n+1)\equiv(n+1)^2$.

*A "show that" again. What is asked here is the value both sides take at
$n=4$ — the case the next question draws.*
""")

code(r"""
q2_6 = ...       # the value of P3(4) + P3(5)

tri = terms(lambda i: i)                     # 1 + 2 + 3 + ... is triangular
odds = terms(lambda i: 2 * i - 1)            # 1 + 3 + 5 + ... is square

verify_total('2.6 (as a square)', q2_6, odds, 5)
verify_total('2.6 (as two triangles)',
             ... if blank(q2_6) else q2_6 - total(tri, 5), tri, 4)
""")

md(r"""
### 2.7 — *May 2022 TZ1 Paper 3 Q1(b)(ii), 1 mark*

State, in words, what the identity given in part (b)(i) shows for two
consecutive triangular numbers.

*No cell: the answer is a sentence. What the markscheme accepts is in
the solutions.*

### 2.8 — *May 2022 TZ1 Paper 3 Q1(b)(iii), 1 mark*

For $n=4$, sketch a diagram clearly showing your answer to part (b)(ii).

*No cell: the answer is a picture. The markscheme's own diagram is in the
solutions.*
""")

md(r"""
### 2.9 — *May 2022 TZ1 Paper 3 Q1(d), 3 marks*

The $n$th pentagonal number can be represented by the arithmetic series

$$P_5(n)=1+4+7+\dots+(3n-2)$$

Hence show that $P_5(n)=\dfrac{n(3n-1)}{2}$ for $n\in\mathbb Z^+$.
""")

code(r"""
q2_9 = ...       # the nth term of the series being added, in terms of n

verify_total('2.9', n * (3 * n - 1) / 2, by_n(q2_9), n)
""")

md(r"""
### 2.10 — *May 2025 TZ1 Paper 2 Q10(a), 1 mark*

Rectangular playing cards are stacked in the shape of a pyramid with $n$
rows: a one-row pyramid is two cards, a two-row pyramid is seven. Let
$t_n$ be the number of cards used. Write down $t_3$.

### 2.11 — *May 2025 TZ1 Paper 2 Q10(b), 2 marks*

Find $t_4$.

### 2.12 — *May 2025 TZ1 Paper 2 Q10(c), 3 marks*

Show that $t_n=\dfrac{n(3n+1)}{2}$.

*Same shape as 2.9: what is asked is the number of cards row $n$ takes
on its own.*
""")

code(r"""
q2_12 = ...      # the number of cards in row n alone, in terms of n
q2_10 = ...      # t3
q2_11 = ...      # t4

rows = by_n(q2_12)

verify_total('2.12', n * (3 * n + 1) / 2, rows, n)
verify_total('2.10', q2_10, rows, 3)
verify_total('2.11', q2_11, rows, 4)
""")

md(r"""
### 2.13 — *November 2025 TZ1 Paper 1 Q1(b), 2 marks*

The sum of the first $n$ terms of the arithmetic sequence of question 1.5
is zero. Find the value of $n$.
""")

code(r"""
q2_13 = ...      # the number of terms whose sum is zero

verify_total('2.13', 0, progression(36, -6), q2_13)
""")

# ============================================================ § 3
md(r"""
---
# § 3. Two facts, two unknowns

**Three questions, 15 marks.** Neither $u_1$ nor $d$ is given, and the
paper hands you exactly two facts about them. Every check below is
backwards: the answers go inside the progression, and the question's own
numbers come back out.
""")

md(r"""
### 3.1 — *May 2021 TZ1 Paper 1 Q2, 5 marks*

Consider an arithmetic sequence where $u_8=S_8=8$. Find the value of the
first term, $u_1$, and the value of the common difference, $d$.
""")

code(r"""
q3_1u = ...      # the first term
q3_1d = ...      # the common difference

mine = progression(q3_1u, q3_1d)

verify_term('3.1 (u8)', 8, mine, 8)
verify_total('3.1 (S8)', 8, mine, 8)
""")

md(r"""
### 3.2 — *November 2025 TZ3 Paper 1 Q1, 5 marks*

The 7th term of an arithmetic sequence is $6$. The sum of the 6th term
and the 12th term is $24$. Find the first term and the common difference.
""")

code(r"""
q3_2u = ...      # the first term
q3_2d = ...      # the common difference

mine = progression(q3_2u, q3_2d)
rest = ... if blank(q3_2u, q3_2d) else 24 - term(mine, 12)

verify_term('3.2 (u7)', 6, mine, 7)
verify_term('3.2 (u6 + u12)', rest, mine, 6)
""")

md(r"""
### 3.3 — *November 2023 TZ1 Paper 1 Q3(a), 5 marks*

The sum of the first $n$ terms of an arithmetic sequence is given by
$S_n=pn^2-qn$, where $p$ and $q$ are positive constants. It is given that
$S_4=40$ and $S_5=65$. Find the value of $p$ and the value of $q$.

*The same paper was set in two zones that November, word for word. It is
counted once.*
""")

code(r"""
q3_3p = ...      # p
q3_3q = ...      # q

mine = sums(lambda i: q3_3p * i ** 2 - q3_3q * i)

verify_total('3.3 (S4)', 40, mine, 4)
verify_total('3.3 (S5)', 65, mine, 5)
""")

# ============================================================ § 4
md(r"""
---
# § 4. From $S_n$ back to $u_n$

**Four questions, 11 marks.** $u_1=S_1$ and $u_n=S_n-S_{n-1}$.
""")

md(r"""
### 4.1 — *May 2023 TZ1 Paper 1 Q10(a), 4 marks*

Consider the arithmetic sequence $u_1,u_2,u_3,\dots$. The sum of the
first $n$ terms of this sequence is given by $S_n=n^2+4n$.

**(i)** Find the sum of the first five terms.
**(ii)** Given that $S_6=60$, find $u_6$.

### 4.2 — *May 2023 TZ1 Paper 1 Q10(b), 2 marks*

Find $u_1$.

### 4.3 — *May 2023 TZ1 Paper 1 Q10(c), 3 marks*

Hence or otherwise, write an expression for $u_n$ in terms of $n$.

*Parts (d) and (e) of this question turn to a geometric sequence and are
in the A2 archive.*
""")

code(r"""
q4_1s = ...      # S5
q4_1u = ...      # u6
q4_2 = ...       # u1
q4_3 = ...       # u_n, in terms of n

given = sums(lambda i: i ** 2 + 4 * i)

verify_total('4.1(i)', q4_1s, given, 5)
verify_term('4.1(ii)', q4_1u, given, 6)
verify_term('4.2', q4_2, given, 1)
verify_term('4.3', q4_3, given, n)
""")

md(r"""
### 4.4 — *November 2023 TZ1 Paper 1 Q3(b), 2 marks*

For the sequence of question 3.3, find the value of $u_5$.
""")

code(r"""
q4_4 = ...       # u5

verify_term('4.4', q4_4, sums(lambda i: 3 * i ** 2 - 2 * i), 5)
""")

# ============================================================ § 5
md(r"""
---
# § 5. The constant difference as a condition

**Six questions, 16 marks.** $u_2-u_1=u_3-u_2$, imposed to find a letter
or verified to prove a family arithmetic.
""")

md(r"""
### 5.1 — *May 2025 TZ3 Paper 1 Q10(a)(i), 3 marks*

Consider the sequence $\{u_n\}$ whose first three terms are
$u_1=k-5$, $u_2=3-2k$ and $u_3=5k+3$, where $k\in\mathbb R$. Consider the
case when $\{u_n\}$ is arithmetic. Find the value of $k$.

### 5.2 — *May 2025 TZ3 Paper 1 Q10(a)(ii), 2 marks*

Hence, or otherwise, find $u_3$.

*Parts (b) and (c) of this question take the same three terms and make
them geometric. They are in the A2 archive.*
""")

code(r"""
q5_1 = ...       # the value of k
q5_2 = ...       # the third term

three = ([Ellipsis] * 3 if blank(q5_1)
         else [q5_1 - 5, 3 - 2 * q5_1, 5 * q5_1 + 3])

verify_arithmetic('5.1', three)
verify_term('5.2', q5_2, terms(lambda i: three[i - 1]), 3)
""")

md(r"""
### 5.3 — *May 2024 TZ2 Paper 1 Q10(a), 2 marks*

Consider the arithmetic sequence $a,\,p,\,q,\dots$, where
$a,p,q\neq0$. Show that $2p-q=a$.

*A "show that": what is asked here is the same identity solved for the
middle term.*
""")

code(r"""
q5_3 = ...       # p in terms of a and q

verify_arithmetic('5.3', [a, q5_3, q])
""")

md(r"""
### 5.4 — *May 2024 TZ2 Paper 1 Q10(c), 2 marks*

The first term of both that arithmetic sequence and a geometric sequence
$a,s,t,\dots$ is $a$. It is given that $q=t=1$. Show that $p>\tfrac12$.

*The reasoning runs through $a$: with $q=1$ the identity of 5.3 gives $a$
in terms of $p$, and $a=s^2>0$ finishes it. What is asked here is that
expression for $a$.*
""")

code(r"""
q5_4 = ...       # a in terms of p, when q = 1

verify_arithmetic('5.4', [q5_4, p, 1])
""")

md(r"""
### 5.5 — *May 2024 TZ2 Paper 1 Q10(d), 4 marks*

Consider the case where $a=9$, $s>0$ and $q=t=1$. Write down the first
four terms of **(i)** the arithmetic sequence; **(ii)** the geometric
sequence.

*Only part (i) is here. The geometric four are in the A2 archive.*
""")

code(r"""
q5_5 = [...]     # the first four terms of the arithmetic sequence

verify_start('5.5', q5_5, terms(lambda i: [9, 5, 1][i - 1]
                                if not blank(q5_5) else ...))
verify_arithmetic('5.5 (arithmetic)', q5_5)
""")

md(r"""
### 5.6 — *May 2023 TZ2 Paper 1 Q12(d), 3 marks*

The regions bounded by the curve $y=\cos\sqrt x$ and the $x$-axis are
$R_1,R_2,R_3,\dots$, and part (c) of the paper gives their areas as
$R_n=4n\pi$. Hence, show that the areas form an arithmetic sequence.

*What is asked here is the common difference, and the check refuses to
look at it before the difference is constant.*
""")

code(r"""
q5_6 = ...       # the common difference of the areas

verify_step('5.6', q5_6, [4 * i * pi for i in (1, 2, 3, 4)])
""")

# ============================================================ § 6
md(r"""
---
# § 6. Quantities with no index

**Nine questions, 25 marks — one Paper 3 investigation from end to end.**
May 2023 TZ2 Paper 3 Q2 puts a coefficient, a root and a constant into
arithmetic sequence and builds thirty-one marks on that one condition.

Throughout: $L(x)=mx+c$ with root $r$ is **AS-linear** when $m,r,c$ in
that order are in arithmetic sequence; $Q(x)=ax^2+bx+c$ with roots
$r_1,r_2$ is **AS-quadratic** when $a,r_1,b,r_2,c$ in that order are.
""")

md(r"""
### 6.1 — *May 2023 TZ2 Paper 3 Q2(a), 2 marks*

Show that $L(x)=2x-1$ is an AS-linear function.

*What is asked is the common difference of the sequence it makes.*
""")

code(r"""
q6_1 = ...       # the common difference of the sequence made by 2x - 1

verify_step('6.1', q6_1, triple(2, -1))
""")

md(r"""
### 6.2 — *May 2023 TZ2 Paper 3 Q2(b)(ii), 4 marks*

Given that $L(x)=mx+c$ is an AS-linear function, show that
$L(x)=mx-\dfrac{m^2}{m+2}$.

*What is asked is $c$ in terms of $m$. Your expression goes into the
triple $(m,\,-c/m,\,c)$, and the triple has to be arithmetic at every $m$
the check tries.*
""")

code(r"""
q6_2 = ...       # c in terms of m

verify_arithmetic('6.2', triple(m, q6_2), m, (1, 3, -5))
""")

md(r"""
### 6.3 — *May 2023 TZ2 Paper 3 Q2(b)(iii), 1 mark*

State any further restrictions on the value of $m$ (beyond $m,c\neq0$).

*Hashed: the answer is the one value of $m$ at which your expression from
6.2 has no value, and there is no sequence left to walk.*
""")

code("""
q6_3 = ...       # the excluded value of m

check_num('6.3', q6_3, 2, '""" + digest('-2') + """')
""")

md(r"""
### 6.4 — *May 2023 TZ2 Paper 3 Q2(e)(i), 1 mark*

Let $Q(x)=ax^2+bx+c$ have roots $r_1,r_2$, and suppose $Q$ is
AS-quadratic. Write down an expression for $r_2-r_1$ in terms of $a$
and $b$.
""")

code(r"""
q6_4 = ...       # r2 - r1, in terms of a and b

# your gap, spread over the five quantities a, r1, b, r2, c
chain = ([Ellipsis] * 5 if blank(q6_4)
         else [a, a + q6_4 / 2, b, b + q6_4 / 2, b + q6_4])

verify_arithmetic('6.4', chain)
""")

md(r"""
### 6.5 — *May 2023 TZ2 Paper 3 Q2(e)(ii), 2 marks*

Use your answers to parts (d)(i) and (e)(i) to show that
$r_1=\dfrac{a^2-ab-b}{2a}$.

*Part (d)(i) of the paper is Vieta's $r_1+r_2=-\dfrac ba$. What is asked
here is $r_2$, which the printed $r_1$ and that relation pin down
together.*
""")

code(r"""
q6_5 = ...       # r2, in terms of a and b

# Vieta, from part (d)(i) of the same paper: r1 + r2 = -b/a
pair = ... if blank(q6_5) else q6_5 + (a ** 2 - a * b - b) / (2 * a)

verify_exact('6.5', pair, -b / a)
""")

md(r"""
### 6.6 — *May 2023 TZ2 Paper 3 Q2(e)(iii), 3 marks*

Use the result from part (e)(ii) to show that $b=0$ or $a=-\tfrac12$.

*What is asked is the second of those: the value of $a$ at which
$a,r_1,b$ is arithmetic whatever $b$ is.*
""")

code(r"""
q6_6 = ...       # the value of a that works for every b

root_one = ... if blank(q6_6) else (q6_6 ** 2 - q6_6 * b - b) / (2 * q6_6)

verify_arithmetic('6.6', [q6_6, root_one, b], b, (1, 2, 5))
""")

md(r"""
### 6.7 — *May 2023 TZ2 Paper 3 Q2(f), 5 marks*

Consider the case where $b=0$. Determine the two AS-quadratic functions
that satisfy this condition.
""")

code(r"""
q6_7 = [...]     # the two quadratics, as expressions in x

for got in q6_7:
    verify_arithmetic('6.7', five_of(got))
""")

md(r"""
### 6.8 — *May 2023 TZ2 Paper 3 Q2(g)(i), 2 marks*

Now consider the case where $a=-\tfrac12$. Find an expression for $r_1$
in terms of $b$.
""")

code(r"""
q6_8 = ...       # r1 in terms of b

verify_arithmetic('6.8', [Rational(-1, 2), q6_8, b], b, (1, 3, -5))
""")

md(r"""
### 6.9 — *May 2023 TZ2 Paper 3 Q2(g)(ii), 5 marks*

Hence or otherwise, determine the exact values of $b$ and $c$ such that
AS-quadratic functions are formed. Give your answers in the form
$\dfrac{-p\pm q\sqrt s}{2}$ where $p,q,s\in\mathbb Z^+$.
""")

code(r"""
q6_9b = [...]    # the two values of b
q6_9c = [...]    # the two values of c, in the same order

for got_b, got_c in zip(q6_9b, q6_9c):
    quad = (... if blank(got_b, got_c)
            else -x ** 2 / 2 + got_b * x + got_c)
    verify_arithmetic('6.9', five_of(quad))
    verify_exact('6.9 (exact)', got_b, got_b)   # a decimal earns nothing here
""")

# ============================================================ § 7
md(r"""
---
# § 7. The greatest sum

**Two questions, 7 marks.** The sum grows exactly while the terms are
positive.
""")

md(r"""
### 7.1 — *May 2021 TZ2 Paper 2 Q2(b), 3 marks*

For the sequence of question 1.4 — first term $60$, common difference
$-2.5$ — let $S_n$ denote the sum of the first $n$ terms. Find the
maximum value of $S_n$.
""")

code(r"""
q7_1 = ...       # the maximum value of Sn

verify_peak('7.1', q7_1, progression(60, -2.5))
""")

md(r"""
### 7.2 — *May 2025 TZ2 Paper 2 Q7(b), 4 marks*

A geometric sequence has first term $80$ and fourth term $0.74088$; its
second term is $16.8$. The first two terms of this geometric sequence are
also the first term and eleventh term respectively of an arithmetic
sequence. Let $S_n$ denote the sum of the first $n$ terms of the
arithmetic sequence. Find the greatest value of $S_n$, giving your answer
to two decimal places.

*Part (a) — finding the second term of the geometric sequence — is in
the A2 archive.*
""")

code(r"""
q7_2d = ...      # the common difference of the arithmetic sequence
q7_2 = ...       # the greatest value of Sn

mine = progression(80, q7_2d)

verify_term('7.2 (d)', 16.8, mine, 11)
verify_peak('7.2', q7_2, mine)
""")

# ============================================================ § 8
md(r"""
---
# § 8. $n$ has to be a whole number

**Three questions, 10 marks.** The only place in the topic where algebra
does not work and every markscheme says *uses a table of values*.
""")

md(r"""
### 8.1 — *May 2022 TZ1 Paper 3 Q1(e), 5 marks*

By using a suitable table of values or otherwise, determine the smallest
positive integer, greater than $1$, that is both a triangular number and
a pentagonal number.

*Which triangular number and which pentagonal number it is are asked for
too: without them the check has nothing to test but the answer itself.*
""")

code(r"""
q8_1 = ...       # the number
q8_1i = ...      # which triangular number it is
q8_1j = ...      # which pentagonal number it is

verify_total('8.1 (triangular)', q8_1, terms(lambda i: i), q8_1i)
verify_total('8.1 (pentagonal)', q8_1, terms(lambda i: 3 * i - 2), q8_1j)
""")

md(r"""
### 8.2 — *May 2025 TZ1 Paper 2 Q10(e), 2 marks*

A complete pyramid stack of playing cards is created using cards taken
from full packs of $52$ with no cards left over. Find the minimum number
of rows in this stack.

*How many packs it uses is asked for the same reason. That yours is the
**smallest** such stack the check cannot confirm — the table is what
earns that mark.*
""")

code(r"""
q8_2 = ...       # the minimum number of rows
q8_2k = ...      # how many full packs of 52 that stack uses

cards = ... if blank(q8_2k) else 52 * q8_2k

verify_total('8.2', cards, terms(lambda i: 3 * i - 1), q8_2)
""")

md(r"""
### 8.3 — *May 2023 TZ2 Paper 3 Q2(c), 3 marks*

There are only three **integer** sets of values of $m$, $r$ and $c$ that
form an AS-linear function. One of these is $L(x)=-x-1$. Use part (b) to
determine the other two AS-linear functions with integer values of $m$,
$r$ and $c$.
""")

code(r"""
q8_3 = [...]     # the other two AS-linear functions, as expressions in x

for got in q8_3:
    made = (triple(got.coeff(x, 1), got.coeff(x, 0))
            if got is not Ellipsis else [...])
    # rounding leaves a whole number alone and moves any other, so the
    # check reports which of m, r, c is not an integer
    rounded = ([...] if blank(made[0])
               else [floor(v + Rational(1, 2)) for v in made])

    verify_arithmetic('8.3', made)
    verify_start('8.3 (whole numbers)', rounded,
                 progression(made[0], made[1] - made[0])
                 if not blank(made[0]) else progression(..., ...))
""")

# ============================================================ § 9
md(r"""
---
# § 9. Terms that are logarithms

**Two questions, 18 marks** — and both are Paper 1, where a decimal
brings nothing at all.
""")

md(r"""
### 9.1 — *May 2022 TZ1 Paper 1 Q10(b), 12 marks*

Consider the series $\ln x+p\ln x+\tfrac13\ln x+\dots$, where
$x\in\mathbb R$, $x>1$ and $p\in\mathbb R$, $p\neq0$. Now consider the
case where the series is arithmetic with common difference $d$.

**(i)** Show that $p=\tfrac23$.
**(ii)** Write down $d$ in the form $k\ln x$, where $k\in\mathbb Q$.
**(iii)** The sum of the first $n$ terms of the series is
$\ln\!\left(\dfrac1{x^3}\right)$. Find the value of $n$.

*Part (a) of the paper takes the same series and makes it geometric. It
is in the A2 archive.*
""")

code(r"""
q9_1p = ...      # p
q9_1d = ...      # the common difference, in the form k*ln(x)
q9_1n = ...      # the number of terms

three = [...] if blank(q9_1p) else [ln(x), q9_1p * ln(x), ln(x) / 3]

verify_arithmetic('9.1(i)', three)
verify_step('9.1(ii)', q9_1d, three)
verify_total('9.1(iii)', ln(1 / x ** 3), progression(ln(x), q9_1d), q9_1n)
""")

md(r"""
### 9.2 — *May 2024 TZ2 Paper 1 Q10(e), 6 marks*

The arithmetic and the geometric sequences of question 5.5 are used to
form a new arithmetic sequence $u_n$, whose first three terms are

$$u_1=9+\ln 9,\qquad u_2=5+\ln 3,\qquad u_3=1+\ln 1$$

**(i)** Find the common difference of the new sequence in terms of
$\ln 3$.
**(ii)** Show that $\displaystyle\sum_{i=1}^{10}u_i=-90-25\ln 3$.
""")

code(r"""
q9_2d = ...      # the common difference
q9_2s = ...      # the sum of the first ten terms

verify_step('9.2(i)', q9_2d, [9 + ln(9), 5 + ln(3), 1 + ln(1)])
verify_total('9.2(ii)', q9_2s, progression(9 + ln(9), q9_2d), 10)
verify_exact('9.2 (exact)', q9_2s, -90 - 25 * ln(3))
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1. Which term is it

**1.1** $u_1=15-3(1)=\boxed{12}$. Not $15$: that is $u_0$.

**1.2** $15-3n=-33\Rightarrow 3n=48\Rightarrow\boxed{n=16}$.

**1.3** $u_2-u_1=9-12=\boxed{-3}$; the coefficient of $n$ is the common
difference, and the markscheme accepts *"recognize gradient is $-3$"*
alone.

**1.4** $60-2.5(k-1)=0\Rightarrow k-1=24\Rightarrow\boxed{k=25}$.

**1.5** Four steps from $u_1$ to $u_5$: $12=36+4d\Rightarrow d=-6$. Then
$u_{13}=36+12(-6)=\boxed{-36}$, or $u_5+8(-6)=12-48=-36$.

---

## § 2. Add the first $n$

**2.1** The series is $1+2+3+\dots$, so its $n$th term is $\boxed{n}$,
and $S_n=\frac n2(1+n)=\frac12n(n+1)$.

**2.2** $p=1+4+9=\boxed{14}$.

**2.3** $f_q(1)=1^q+2^q+\dots+n^q$, so
$$f_q(1)=\boxed{\sum_{i=1}^n i^q}$$
The markscheme also accepts $\sum_{i=1}^n 1^i i^q$.

**2.4** Substituting $r=3$:
$$P_3(n)=\frac{(3-2)n^2-(3-4)n}{2}=\frac{n^2+n}{2}=\frac{n(n+1)}{2}$$
and at $n=10$ that is $\frac{10\cdot11}{2}=\boxed{55}$.

The markscheme is explicit that numerical verification earns nothing —
the substitution has to be shown.

**2.5** $\frac{n(n+1)}{2}=351\Rightarrow n^2+n-702=0\Rightarrow
(n-26)(n+27)=0$, so $\boxed{n=26}$. Giving *"$n=-27,26$"* is marked
wrong: an index is positive.

**2.6** $P_3(4)+P_3(5)=10+15=\boxed{25}=5^2$, which is $(n+1)^2$ at
$n=4$. In general
$$P_3(n)+P_3(n+1)=\frac{n(n+1)}{2}+\frac{(n+1)(n+2)}{2}
=\frac{(n+1)(2n+2)}{2}=(n+1)^2$$

**2.7** *The sum of the $n$th and $(n+1)$th triangular numbers is the
$(n+1)$th square number.* That sentence is the whole mark.

**2.8** The markscheme's diagram is a $5\times5$ square split by its
diagonal:

```
X X X X X
O X X X X
O O X X X
O O O X X
O O O O X
```

fifteen X's (the 5th triangular number), ten O's (the 4th), twenty-five
in all (the 5th square number). Any equivalent picture showing
$P_3(4)$, $P_3(5)$ and $P_4(5)$ is accepted.

**2.9** The series $1+4+7+\dots$ has $u_1=1$ and $d=3$, so its $n$th term
is $\boxed{3n-2}$ and
$$P_5(n)=\frac n2\bigl(1+(3n-2)\bigr)=\frac{n(3n-1)}{2}$$

**2.10** $t_3=2+5+8=\boxed{15}$.

**2.11** $t_4=15+11=\boxed{26}$. The fourth row is eleven cards, not ten.

**2.12** Row $n$ takes $\boxed{3n-1}$ cards — two more slanted and one
more horizontal than the row above — so
$t_n=\frac n2\bigl(2+(3n-1)\bigr)=\frac n2(3n+1)$.

**2.13** $\frac n2(36+u_n)=0$ with $n\neq0$ needs $u_n=-36$, which by 1.5
is the 13th term: $\boxed{n=13}$. By symmetry:
$36+30+\dots+0+\dots-30-36$ has $6+1+6$ terms.

The markscheme condones $n=0,13$. Zero terms do add to zero — but an
index counts terms.

---

## § 3. Two facts, two unknowns

**3.1** $u_1+7d=8$ and $\frac82(2u_1+7d)=8$, that is $2u_1+7d=2$.
Subtracting, $u_1=-6$; then $7d=14$ and $d=2$.

$$\boxed{u_1=-6,\quad d=2}$$

Shorter: $S_8=4(u_1+u_8)=4(u_1+8)=8$ gives $u_1=-6$ at once, because
$u_8$ is already known.

**3.2** $u_1+6d=6$, and $u_6+u_{12}=(6-d)+(6+5d)=12+4d=24$, so $d=3$ and
$u_1=6-18=-12$.

$$\boxed{u_1=-12,\quad d=3}$$

Measuring $u_6$ and $u_{12}$ from the known $u_7$ rather than from $u_1$
is the markscheme's second method and three lines shorter.

**3.3** $16p-4q=40$ and $25p-5q=65$, that is $4p-q=10$ and $5p-q=13$.
Subtracting, $\boxed{p=3}$, then $\boxed{q=2}$.

Or through $u_1$ and $d$: $S_4=2(2u_1+3d)=40$ and
$S_5=\frac52(2u_1+4d)=65$ give $u_1=1$, $d=6$, and
$S_n=\frac n2(2+6(n-1))=3n^2-2n$.

---

## § 4. From $S_n$ back to $u_n$

**4.1(i)** $S_5=25+20=\boxed{45}$.

**(ii)** $u_6=S_6-S_5=60-45=\boxed{15}$.

**4.2** $u_1=S_1=1+4=\boxed{5}$.

**4.3** $u_n=S_n-S_{n-1}=(n^2+4n)-\bigl((n-1)^2+4(n-1)\bigr)=\boxed{2n+3}$.

Or through $d$: $u_2=S_2-S_1=12-5=7$, so $d=7-5=2$ and
$u_n=5+2(n-1)$. Same answer, and
the check accepts either — it walks the sequence rather than reading the
expression.

**4.4** $u_5=S_5-S_4=65-40=\boxed{25}$. Nothing about $p$ and $q$ is
needed; this is the fastest mark on that paper.

---

## § 5. The constant difference as a condition

**5.1** $(3-2k)-(k-5)=(5k+3)-(3-2k)$ gives $8-3k=7k$, so
$\boxed{k=\tfrac45}$. The mean form is quicker:
$\frac{(k-5)+(5k+3)}{2}=3-2k\Rightarrow 3k-1=3-2k$.

**5.2** $u_3=5\left(\tfrac45\right)+3=\boxed{7}$. The three terms are
$-\tfrac{21}5,\ \tfrac75,\ 7$, with difference $\tfrac{28}5$.

**5.3** $p-a=q-p$, so $\boxed{p=\dfrac{a+q}{2}}$ — which rearranges to
$2p-q=a$.

**5.4** With $q=1$: $a=2p-1$, so $\boxed{a=2p-1}$. Since $a=s^2$ and
$s>0$, $a>0$, hence $2p-1>0$ and $p>\tfrac12$.

**5.5** $a=9$, $q=1$, so $p=\frac{9+1}{2}=5$ and $d=-4$:

$$\boxed{9,\ 5,\ 1,\ -3}$$

(The geometric four are $9,3,1,\tfrac13$ — A2.)

**5.6** $R_{n+1}-R_n=4(n+1)\pi-4n\pi=\boxed{4\pi}$, **which does not
depend on $n$, so the difference is constant.** That last clause is the
R1, and the markscheme awards M0 for checking $R_3$ and $R_2$ instead.

---

## § 6. Quantities with no index

**6.1** $L(x)=2x-1$ has $m=2$, $c=-1$, $r=\tfrac12$. The sequence
$2,\tfrac12,-1$ has $d=\boxed{-\tfrac32}$ both ways, so it is arithmetic.

**6.2** With $r=-\dfrac cm$, the condition $r-m=c-r$ gives
$-\dfrac{2c}{m}=c+m$, so $m^2+cm+2c=0$ and

$$c=\boxed{-\frac{m^2}{m+2}}$$

**6.3** $c$ has no value at $m+2=0$, so $\boxed{m\neq-2}$.

**6.4** In $a,r_1,b,r_2,c$ the gap $r_2-r_1$ spans two steps, and so does
$b-a$:

$$r_2-r_1=\boxed{b-a}$$

**6.5** Vieta gives $r_1+r_2=-\dfrac ba$, so with the printed $r_1$,

$$r_2=-\frac ba-\frac{a^2-ab-b}{2a}=\boxed{-\frac{a^2-ab+b}{2a}}$$

and eliminating $r_2$ from $r_2-r_1=b-a$ gives
$2r_1=-\dfrac ba-(b-a)=\dfrac{a^2-ab-b}{a}$, which is the printed result.

**6.6** For $a,r_1,b$ to be arithmetic, $r_1-a=b-r_1$, and substituting
the printed $r_1$ gives

$$\frac{b(2a+1)}{a}=0\Longrightarrow b=0\ \text{ or }\ a=\boxed{-\tfrac12}$$

**6.7** With $b=0$: the sequence $a,r_1,0,r_2,c$ is symmetric about zero,
so $r_1=\frac a2$, $r_2=-\frac a2$ and $c=-a$. Vieta's product then gives
$r_1r_2=\frac ca$, that is $-\frac{a^2}{4}=-1$, so $a=\pm2$:

$$\boxed{Q(x)=2x^2-2},\qquad \boxed{Q(x)=-2x^2+2}$$

with sequences $2,1,0,-1,-2$ and $-2,-1,0,1,2$.

**6.8** With $a=-\tfrac12$, $r_1$ is the mean of $a$ and $b$:

$$r_1=\frac{-\tfrac12+b}{2}=\boxed{\frac{2b-1}{4}}$$

**6.9** Substituting $r_1$ into $Q(r_1)=0$ with $a=-\tfrac12$ gives
$c=\dfrac{4b+1}{2}$ and then $4b^2+20b+5=0$:

$$b=\boxed{\frac{-5\pm2\sqrt5}{2}},\qquad c=\boxed{\frac{-9\pm4\sqrt5}{2}}$$

Decimals earn nothing here — the question says *exact values*.

---

## § 7. The greatest sum

**7.1** The terms are positive to the 24th and zero at the 25th, so
$S_{24}=S_{25}$ and both are greatest:

$$S_{25}=\frac{25}{2}(60+0)=\boxed{750}$$

**7.2** $u_1=80$ and $u_{11}=16.8$, so $10d=-63.2$ and $d=-6.32$. The
terms stay positive while $80-6.32(n-1)>0$, that is $n<13.66$, so
$n=13$:

$$S_{13}=\frac{13}{2}\bigl(160-6.32\times12\bigr)=\boxed{547.04}$$

A table of $S_n$ finds it faster, but the value must be taken by
substituting $n=13$: the markscheme rejects the graph's vertex
$(13.1582\ldots,\,547.119\ldots)$ by name.

---

## § 8. $n$ has to be a whole number

**8.1** Two tables side by side:

| $n$ | $P_3(n)$ | | $m$ | $P_5(m)$ |
|---|---|---|---|---|
| 19 | 190 | | 11 | 176 |
| **20** | **210** | | **12** | **210** |
| 21 | 231 | | 13 | 247 |

$$\boxed{210}$$

the $\boxed{20}$th triangular number and the $\boxed{12}$th pentagonal
number. The markscheme gives all five marks for $210$ seen anywhere.

**8.2** $t_n=2,7,15,26,40,57,77,100,126,155,187,222,\boxed{260}$, and
$260=5\times52$, so $\boxed{13}$ rows and $\boxed{5}$ packs. Solving
$t_n=52$ instead is marked M0A0; answering $5$ instead of $13$ loses the
mark too.

**8.3** $c=-\dfrac{m^2}{m+2}$ is an integer when $m+2$ divides $m^2$.
Since $m^2=(m-2)(m+2)+4$, that means $m+2$ divides $4$, so
$m\in\{-1,-3,0,-4,2,-6\}$. Discarding $m=0$ and checking $r=-c/m$
integer as well leaves three, one of which is the given $L(x)=-x-1$:

$$\boxed{L(x)=-4x+8},\qquad \boxed{L(x)=-3x+9}$$

with sequences $-4,2,8$ and $-3,3,9$.

---

## § 9. Terms that are logarithms

**9.1(i)** $p\ln x-\ln x=\tfrac13\ln x-p\ln x$. Since $x>1$, $\ln x$
divides out: $p-1=\tfrac13-p$, so $\boxed{p=\tfrac23}$.

**(ii)** $d=\left(\tfrac23-1\right)\ln x=\boxed{-\tfrac13\ln x}$.

**(iii)** $\ln\!\left(\dfrac1{x^3}\right)=-3\ln x$ — the minus sign is the
mark. Then

$$\frac n2\left(2-\frac{n-1}{3}\right)\ln x=-3\ln x
\Longrightarrow n(7-n)=-18\Longrightarrow n^2-7n-18=0$$

$$(n-9)(n+2)=0\Longrightarrow\boxed{n=9}$$

The markscheme's second method needs no algebra: the terms are
$\ln x,\tfrac23\ln x,\tfrac13\ln x,0,-\tfrac13\ln x,-\tfrac23\ln x,
-\ln x,\dots$, the first seven cancel to nothing, and the 8th and 9th add
to $-3\ln x$.

**9.2(i)** $\ln 9=2\ln 3$ and $\ln 1=0$, so the terms are $9+2\ln 3$,
$5+\ln 3$, $1$:

$$d=(5-9)+(1-2)\ln 3=\boxed{-4-\ln 3}$$

**(ii)**
$$S_{10}=5\bigl(2(9+2\ln 3)+9(-4-\ln 3)\bigr)=5(-18-5\ln 3)
=\boxed{-90-25\ln 3}$$

Both halves are needed. Dropping the logarithms because $\ln 1=0$ loses
the $-25\ln 3$.
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
