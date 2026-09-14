"""Собирает архивный ноутбук D4: вся тема дискретных величин подряд.

Шестнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2 и D3. Практикум учит: лестница из приёмов, теория перед
каждым, три уровня сложности, тренажёр распознавания, задание на время.
Архив не учит. Он даёт набивать руку: **вся тема подряд, по тем же шести
приёмам, без единой строчки теории**. Двадцать четыре вопроса, 104 балла —
всё, что архив спрашивает про дискретную величину, кроме биномиальной,
с мая 2021 по ноябрь 2025.

Разметка взята из карточки statistics-discrete.yaml: поле blocks у каждого
приёма. Ноябрьский дубль 2023 года входит один раз, копией TZ1.

Практикум и здесь забрал почти все вопросы темы, и архив отличается от
него порядком — строго по приёмам — и тем, что части одного вопроса
разнесены по своим приёмам. Сильнее всего это видно на мае 2021 TZ1 Q10:
(a) и (c) стоят в § 1, (b) и (d) в § 2, (e) в § 3. Условие каждого
пункта повторено целиком, чтобы вопрос читался без соседнего.

Хешей нет ни одного: всякий ответ темы — буква таблицы, диапазон,
среднее, дисперсия или многочлен, и всякий проверяется самой таблицей.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_d4.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/archive-d4-discrete.ipynb')

ANSWERS = {
    # § 1. The table must be a distribution
    'q1_1a': '0.154',
    'q1_1m': '2',
    'q1_2e': 'Eq(2*k**2 - k + 0.12, 0)',
    'q1_2k': '0.3',
    'q1_3p': 'Rational(2, 7)',
    'q1_3r': 'Interval(0, 1)',
    'q1_3q': 'Interval(0, Rational(1, 3))',
    'q1_4': 'Interval(0, 0.3)',
    # § 2. The mean
    'q2_1': '2.44',
    'q2_2': '1.27',
    'q2_3b': 'Rational(16, 7)',
    'q2_3d': 'Interval(2, 4)',
    'q2_4p': '0.85',
    'q2_4e': '1.5',
    'q2_4r': '150',
    'q2_5': '3.125',
    'q2_6': '2.5104',
    # § 3. Two letters, two conditions
    'q3_1': '[0.4, 0.2]',
    'q3_2': '0.553',
    'q3_3': '[4, 3]',
    'q3_4': '[45, 5]',
    'q3_5qr': '[Rational(5, 24), Rational(3, 8)]',
    'q3_5': 'Rational(11, 4)',
    # § 4. Spread, and a variable built from X
    'q4_1': '0.4',
    'q4_2': '30',
    'q4_3ab': '[195, 20]',
    'q4_3v': '370',
    'q4_4': '1.19',
    # § 5. A first success
    'q5_1b': 'Sum(x*p*(1 - p)**(x - 1), (x, 1, oo))',
    'q5_1m': '10',
    'q5_1v': '90',
    'q5_2p': '0.398',
    'q5_2v': '3.79',
    # § 6. A generating function
    'q6_1': '3.125',
    'q6_2': 'Rational(3, 10) + Rational(3, 5)*t + Rational(1, 10)*t**2',
    'q6_3p': 'Rational(2, 3)',
    'q6_3y': 'Rational(1, 6) + t/2 + t**2/3',
    'q6_3z': '1.97',
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
# D4 archive — discrete random variables, all of it

**Twenty-four questions, 104 marks.** Every question the archive asks about
a discrete random variable that is not binomial, from May 2021 to November
2025, in the order of the six techniques rather than the order of the
papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-d4-discrete.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The table must be a distribution | 4 | 14 |
| 2 | The mean | 6 | 19 |
| 3 | Two letters, two conditions | 5 | 28 |
| 4 | Spread, and a variable built from $X$ | 4 | 16 |
| 5 | A first success | 2 | 9 |
| 6 | A generating function | 3 | 18 |

The checks are the same ones the practicum uses and they store nothing:
each is handed the table and the conditions of the question, finds the
letters itself, and throws away the roots that break a cell. Exact values
on Paper 1 questions — `Rational(2, 7)`, `Interval(0, Rational(1, 3))` —
and three significant figures elsewhere.

**Parts of one question are split by technique.** May 2021 TZ1 Q10 appears
in §§ 1, 2 and 3; each part repeats the table it needs.

**The November 2023 paper appears once**, although the archive holds it
twice as TZ1 and TZ2.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Dist, Freq, Geo, Moments, P(), Expect, Var, Pgf

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. The table must be a distribution

**Four questions, 14 marks.** Every cell in $[0,1]$, the cells add up to
one — and a root that breaks a cell is rejected, with the reason.
""")

md(r"""
### 1.1 — *May 2025 TZ3 Paper 2 Q3(a), 3 marks*

The number of times, $X$, each customer visits a supermarket in a week is
given by the following probability distribution.

| $x$ | $1$ | $2$ | $3$ | $4$ | $5$ | $\ge6$ |
|---|---|---|---|---|---|---|
| $P(X=x)$ | $1.5a$ | $2a$ | $0.281$ | $a$ | $0.026$ | $0$ |

**(i)** Find the value of $a$. **(ii)** Write down the mode of $X$.
""")

code(r"""
q1_1a = ...      # a
q1_1m = ...      # the mode

a = symbols('a')
visits = Dist({1: 1.5*a, 2: 2*a, 3: 0.281, 4: a, 5: 0.026, 6: 0})

verify_letters('1.1(i)', q1_1a, a, [visits])
verify_mode('1.1(ii)', q1_1m, visits, given=[], var=a)
""")

md(r"""
### 1.2 — *May 2022 TZ1 Paper 2 Q3(a)–(b), 4 marks*

A discrete random variable, $X$, has the following probability
distribution:

| $x$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x)$ | $0.41$ | $k-0.28$ | $0.46$ | $0.29-2k^2$ |

**(a)** Show that $2k^2-k+0.12=0$. **(b)** Find the value of $k$, giving a
reason for your answer.
""")

code(r"""
k = symbols('k')

q1_2e = ...      # the equation, as Eq(...)
q1_2k = ...      # k

X = Dist({0: 0.41, 1: k - 0.28, 2: 0.46, 3: 0.29 - 2*k**2})

verify_equation('1.2(a)', q1_2e, Eq(total_probability(X), 1), var=k)
verify_letters('1.2(b)', q1_2k, k, [X])
""")

md(r"""
### 1.3 — *May 2021 TZ1 Paper 1 Q10(a), (c), 5 marks*

A biased four-sided die, A, is rolled, and $X$ is the score.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $p$ | $p$ | $p$ | $\frac12p$ |

**(a)** Find the value of $p$.

A second biased four-sided die, B, is rolled, and $Y$ is the score.

| $y$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(Y=y)$ | $q$ | $q$ | $q$ | $r$ |

**(c)** **(i)** State the range of possible values of $r$. **(ii)** Hence,
find the range of possible values of $q$.
""")

code(r"""
q1_3p = ...      # p, exactly
q1_3r = ...      # the range of r, as an Interval
q1_3q = ...      # the range of q

p, q, r = symbols('p q r')
X = Dist({1: p, 2: p, 3: p, 4: p/2}, 'X')
Y = Dist({1: q, 2: q, 3: q, 4: r}, 'Y')

verify_letters('1.3(a)', q1_3p, p, [X])
verify_table_range('1.3(c)(i)', q1_3r, r, [Y])
verify_table_range('1.3(c)(ii)', q1_3q, q, [Y])
""")

md(r"""
### 1.4 — *November 2025 TZ3 Paper 1 Q7(a), 2 marks*

The discrete random variable $X$ has the following probability
distribution:

| $x$ | $1$ | $2$ | $3$ |
|---|---|---|---|
| $P(X=x)$ | $0.6-2a$ | $3a$ | $0.4-a$ |

Find the range of possible values of $a$.
""")

code(r"""
q1_4 = ...       # the range of a

a = symbols('a')
X = Dist({1: 0.6 - 2*a, 2: 3*a, 3: 0.4 - a})

verify_table_range('1.4', q1_4, a, [X])
""")

# ============================================================ § 2
md(r"""
---
# § 2. The mean

**Six questions, 19 marks.** Each value times its own probability.
""")

md(r"""
### 2.1 — *May 2025 TZ3 Paper 2 Q3(b), 2 marks*

*(The supermarket of 1.1.)* Find the mean of $X$.

### 2.2 — *May 2022 TZ1 Paper 2 Q3(c), 2 marks*

*(The table of 1.2.)* Hence, find $E(X)$.
""")

code(r"""
q2_1 = ...       # the mean number of visits
q2_2 = ...       # E(X) for the table of 1.2

a, k = symbols('a k')
visits = Dist({1: 1.5*a, 2: 2*a, 3: 0.281, 4: a, 5: 0.026, 6: 0})
X = Dist({0: 0.41, 1: k - 0.28, 2: 0.46, 3: 0.29 - 2*k**2})

verify_moment('2.1', q2_1, Expect(visits), given=[], var=a)
verify_moment('2.2', q2_2, Expect(X), given=[], var=k)
""")

md(r"""
### 2.3 — *May 2021 TZ1 Paper 1 Q10(b), (d), 5 marks*

*(The dice A and B of 1.3.)*

**(b)** Hence, find the value of $E(X)$.

**(d)** Hence, find the range of possible values for $E(Y)$.
""")

code(r"""
q2_3b = ...      # E(X), exactly
q2_3d = ...      # the range of E(Y), as an Interval

p, q, r = symbols('p q r')
X = Dist({1: p, 2: p, 3: p, 4: p/2}, 'X')
Y = Dist({1: q, 2: q, 3: q, 4: r}, 'Y')

verify_moment('2.3(b)', q2_3b, Expect(X), given=[], var=p)
verify_table_range('2.3(d)', q2_3d, Expect(Y), [Y])
""")

md(r"""
### 2.4 — *May 2023 TZ1 Paper 1 Q2, 6 marks*

On a Monday at an amusement park, a sample of $40$ visitors was randomly
selected as they were leaving the park. They were asked how many times
that day they had been on a ride called The Dragon.

| number of times on The Dragon | $0$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|---|
| frequency | $6$ | $16$ | $13$ | $2$ | $3$ |

It can be assumed that this sample is representative of all visitors to
the park for the following day.

**(a)** For the following day, Tuesday, estimate **(i)** the probability
that a randomly selected visitor will ride The Dragon; **(ii)** the
expected number of times a visitor will ride The Dragon.

It is known that $1000$ visitors will attend the amusement park on
Tuesday. The Dragon can carry a maximum of $10$ people each time it runs.

**(b)** Estimate the minimum number of times The Dragon must run to
satisfy demand.
""")

code(r"""
q2_4p = ...      # P(a visitor rides)
q2_4e = ...      # the expected number of rides per visitor
q2_4r = ...      # the minimum number of runs

rides = Freq({0: 6, 1: 16, 2: 13, 3: 2, 4: 3})

verify_chance('2.4(a)(i)', q2_4p, P(rides >= 1))
verify_moment('2.4(a)(ii)', q2_4e, Expect(rides))
verify_moment('2.4(b)', q2_4r, Expect(rides * 1000 / 10))
""")

md(r"""
### 2.5 — *May 2025 TZ1 Paper 3 Q1(a), 2 marks*

Two unbiased tetrahedral dice with faces labelled $1$, $2$, $3$ and $4$ are
thrown, and $M$ is the maximum of the two scores.

| $m$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(M=m)$ | $\frac1{16}$ | $\frac3{16}$ | $\frac5{16}$ | $\frac7{16}$ |

Find $E(M)$.

### 2.6 — *May 2024 TZ1 Paper 3 Q1(g)(ii), 2 marks*

In a computer game, $Y$ is the number of actions until the first boost
occurs, with

| $y$ | $1$ | $2$ | $3$ | $4$ | $5$ |
|---|---|---|---|---|---|
| $P(Y=y)$ | $0.2$ | $0.32$ | $0.288$ | $0.1536$ | $0.0384$ |

Show that $E(Y)=2.5104$.
""")

code(r"""
q2_5 = ...       # E(M)
q2_6 = ...       # E(Y)

throws = {(i, j): Rational(1, 16) for i in range(1, 5) for j in range(1, 5)}
M = Dist(throws, 'M', rule=max)
Y = Dist({1: 0.2, 2: 0.32, 3: 0.288, 4: 0.1536, 5: 0.0384}, 'Y')

verify_moment('2.5', q2_5, Expect(M))
verify_moment('2.6', q2_6, Expect(Y))
""")

# ============================================================ § 3
md(r"""
---
# § 3. Two letters, two conditions

**Five questions, 28 marks.** One equation from the sum, one from the
fact the question adds — then the roots the table allows.
""")

md(r"""
### 3.1 — *May 2022 TZ2 Paper 1 Q10(a), 5 marks*

A biased four-sided die is rolled, and $X$ is the result.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $p$ | $0.3$ | $q$ | $0.1$ |

It is known that $E(X)=2$. Show that $p=0.4$ and $q=0.2$.

### 3.2 — *November 2023 TZ1 Paper 2 Q5, 5 marks*

The following table shows the probability distribution of a discrete
random variable $X$, where $a,k\in\mathbb{R}^+$.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $k$ | $k^2$ | $a$ | $k^3$ |

Given that $E(X)=2.3$, find the value of $a$.
""")

code(r"""
q3_1 = [...]     # [p, q]
q3_2 = ...       # a

p, q = symbols('p q')
X = Dist({1: p, 2: 0.3, 3: q, 4: 0.1})
a, k = symbols('a k')
W = Dist({1: k, 2: k**2, 3: a, 4: k**3})

verify_letters('3.1', q3_1, [p, q], [X], [Eq(Expect(X), 2)])
verify_letters('3.2', q3_2, a, [W], [Eq(Expect(W), 2.3)])
""")

md(r"""
### 3.3 — *May 2024 TZ1 Paper 1 Q1(a), 5 marks*

Claire rolls a six-sided die $16$ times. The scores obtained are shown in
the following frequency table.

| score | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ |
|---|---|---|---|---|---|---|
| frequency | $p$ | $q$ | $4$ | $2$ | $0$ | $3$ |

It is given that the mean score is $3$. Find the value of $p$ and the
value of $q$.

### 3.4 — *May 2025 TZ2 Paper 2 Q8, 7 marks*

The marks obtained by students in a class quiz are shown in the following
table where $p,q\in\mathbb{Z}^+$.

| marks | $20$ | $35$ | $p$ |
|---|---|---|---|
| frequency | $12$ | $q$ | $8$ |

The mean and variance of the marks are $31$ and $124$ respectively. Find
the value of $p$ and the value of $q$.
""")

code(r"""
q3_3 = [...]     # [p, q]
q3_4 = [...]     # [p, q]

p, q = symbols('p q', integer=True, nonnegative=True)
rolls = Freq({1: p, 2: q, 3: 4, 4: 2, 5: 0, 6: 3})
verify_letters('3.3', q3_3, [p, q], [rolls], [Eq(rolls.size, 16), Eq(Expect(rolls), 3)])

p, q = symbols('p q', positive=True, integer=True)
quiz = Freq({20: 12, 35: q, p: 8})
verify_letters('3.4', q3_4, [p, q], [quiz], [Eq(Expect(quiz), 31), Eq(Var(quiz), 124)])
""")

md(r"""
### 3.5 — *May 2021 TZ1 Paper 1 Q10(e), 6 marks*

*(The dice A and B of 1.3.)* Agnes and Barbara play a game using these
dice. Agnes rolls die A once and Barbara rolls die B once. The probability
that Agnes' score is less than Barbara's score is $\frac12$.

Find the value of $E(Y)$.
""")

code(r"""
q3_5qr = [...]   # [q, r]
q3_5 = ...       # E(Y)

p, q, r = symbols('p q r')
X = Dist({1: p, 2: p, 3: p, 4: p/2}, 'X')
Y = Dist({1: q, 2: q, 3: q, 4: r}, 'Y')
game = [Eq(P(X < Y), Rational(1, 2))]

verify_letters('3.5 q, r', q3_5qr, [q, r], [X, Y], game)
verify_moment('3.5', q3_5, Expect(Y), given=game, var=[p, q, r], tables=[X])
""")

# ============================================================ § 4
md(r"""
---
# § 4. Spread, and a variable built from $X$

**Four questions, 16 marks.** $E(X^2)-E(X)^2$; the constant goes, the
multiplier is squared.
""")

md(r"""
### 4.1 — *November 2025 TZ3 Paper 1 Q7(b), 6 marks*

*(The table of 1.4.)* In the case where $a=0.2$, determine
$\mathrm{Var}(2-X)$.

### 4.2 — *May 2024 TZ1 Paper 1 Q1(b), 1 mark*

*(Claire's scores of 3.3.)* Each of Claire's scores is multiplied by $10$
in order to determine the final score for a game she is playing. Write
down the mean final score.
""")

code(r"""
q4_1 = ...       # Var(2 - X)
q4_2 = ...       # the mean final score

a = symbols('a')
X = Dist({1: 0.6 - 2*a, 2: 3*a, 3: 0.4 - a})
p, q = symbols('p q', integer=True, nonnegative=True)
rolls = Freq({1: p, 2: q, 3: 4, 4: 2, 5: 0, 6: 3})
claire = [Eq(rolls.size, 16), Eq(Expect(rolls), 3)]

verify_moment('4.1', q4_1, Var(2 - X), given=Eq(a, 0.2), var=a)
verify_moment('4.2', q4_2, Expect(10 * rolls), given=claire, var=[p, q])
""")

md(r"""
### 4.3 — *May 2025 TZ1 Paper 2 Q11(e)–(f), 7 marks*

The random variable $T$ is the time, in hours, taken for a runner to
complete a marathon. No runner completes the race in less than $2.25$
hours. Each runner's time is converted to a score $a-bt$, where $t$ is
their time in hours and $a,b>0$, and $P$ is the score of a runner. It is
given that $E(P)=100$ and the maximum possible score is $150$.

**(e)** Use $E(T)=4.723$ to determine the value of $a$ and the value of
$b$, giving your answers to the nearest integer.

**(f)** Given also that $\mathrm{Var}(T)=0.906$, find $\mathrm{Var}(P)$.

### 4.4 — *May 2024 TZ1 Paper 3 Q1(g)(iii), 2 marks*

*(The table of $Y$ in 2.6.)* Find $\mathrm{Var}(Y)$.
""")

code(r"""
q4_3ab = [...]   # [a, b]
q4_3v = ...      # the variance of the score
q4_4 = ...       # Var(Y)

a, b = symbols('a b', positive=True)
T = Moments(4.723, 0.906, 'T')
score = [Eq(Expect(a - b*T), 100), Eq(a - b*2.25, 150)]
Y = Dist({1: 0.2, 2: 0.32, 3: 0.288, 4: 0.1536, 5: 0.0384}, 'Y')

verify_letters('4.3(e)', q4_3ab, [a, b], [T], score, whole=True)
verify_moment('4.3(f)', q4_3v, Var(a - b*T), given=score, var=[a, b])
verify_moment('4.4', q4_4, Var(Y))
""")

# ============================================================ § 5
md(r"""
---
# § 5. A first success

**Two questions, 9 marks.** Values $1,2,3,\dots$ with no end — the mean
is still a weighted sum.
""")

md(r"""
### 5.1 — *May 2024 TZ1 Paper 3 Q1(b)–(d), 6 marks*

Each time a player performs an action, the probability that it is
*boosted* is $p$, where $0<p<1$, independently.

**(b)** **(i)** Explain why the probability that the first boost occurs on
the $x$th action is $p(1-p)^{x-1}$. Let $X$ be the number of actions until
the first boost occurs. **(ii)** Hence, write down an expression, using
sigma notation, for $E(X)$ in terms of $x$ and $p$.

**(c)** **(ii)** Given that $\sum_{n=1}^\infty nar^{n-1}=\frac{a}{(1-r)^2}$,
show that $E(X)=\frac1p$.

It can be shown that $\mathrm{Var}(X)=\frac{1-p}{p^2}$.

**(d)** Find $E(X)$ and $\mathrm{Var}(X)$ when $p=0.1$.
""")

code(r"""
p = symbols('p')

q5_1b = ...      # E(X) as a sum, with Sum(..., (x, 1, oo))
q5_1m = ...      # E(X) when p = 0.1
q5_1v = ...      # Var(X) when p = 0.1

verify_moment('5.1(b)(ii)', q5_1b, Expect(Geo(p)))
verify_moment('5.1(d) E(X)', q5_1m, Expect(Geo(0.1)))
verify_moment('5.1(d) Var(X)', q5_1v, Var(Geo(0.1)))
""")

md(r"""
### 5.2 — *May 2024 TZ1 Paper 3 Q1(h), 3 marks*

*(The first model of 5.1, and the second model $Y$ of 2.6 with
$E(Y)=2.5104$ and $\mathrm{Var}(Y)=1.18749\ldots$)*

**(i)** Use $E(X)=\frac1p$ to find the value of $p$ for which $E(X)=E(Y)$.
**(ii)** Find $\mathrm{Var}(X)$ for this value of $p$. **(iii)** Hence
determine, with a reason, which model provides a more consistent
experience for the player with respect to boosted actions.
""")

code(r"""
q5_2p = ...      # p
q5_2v = ...      # Var(X)

p = symbols('p')
X = Geo(p, 'X')
Y = Dist({1: 0.2, 2: 0.32, 3: 0.288, 4: 0.1536, 5: 0.0384}, 'Y')
same_mean = Eq(Expect(X), Expect(Y))

verify_letters('5.2(i)', q5_2p, p, [X], [same_mean])
verify_moment('5.2(ii)', q5_2v, Var(X), given=same_mean, var=p)
""")

# ============================================================ § 6
md(r"""
---
# § 6. A generating function

**Three questions, 18 marks.** The coefficient of $t^x$ is $P(X=x)$.
""")

md(r"""
### 6.1 — *May 2025 TZ1 Paper 3 Q1(c)(ii), 3 marks*

*(The maximum $M$ of 2.5.)* The distribution of $M$ is represented by
$G(t)=\sum_{m=1}^4P(M=m)t^m=\frac1{16}t+\frac3{16}t^2+\frac5{16}t^3+\frac7{16}t^4$.
Part (c)(i) finds $G'(t)$. Hence, show that $G'(1)=E(M)$.

### 6.2 — *May 2025 TZ1 Paper 3 Q1(d), 5 marks*

A bag contains two red balls and three yellow balls. Two balls are
selected at random without replacement. $X$ is the total number of red
balls selected, and $G_X(t)=\sum_{x=0}^2P(X=x)t^x$. Show that
$G_X(t)=\frac3{10}+\frac35t+\frac1{10}t^2$, making it clear how the
coefficients have been determined.
""")

code(r"""
q6_1 = ...       # G'(1)
q6_2 = ...       # G_X(t)

throws = {(i, j): Rational(1, 16) for i in range(1, 5) for j in range(1, 5)}
M = Dist(throws, 'M', rule=max)
balls = 'RRYYY'
draws = {(i, j): Rational(1, 20) for i in range(5) for j in range(5) if i != j}
X = Dist(draws, 'X', rule=lambda pair: (balls[pair[0]] == 'R') + (balls[pair[1]] == 'R'))

verify_moment("6.1 G'(1)", q6_1, Expect(M))
verify_pgf('6.2', q6_2, X, t)
""")

md(r"""
### 6.3 — *May 2025 TZ1 Paper 3 Q1(e)–(f), 10 marks*

*(The bag of 6.2.)* An unbiased coin and a biased coin are tossed. The
probability of obtaining a tail on the biased coin is $p$. $Y$ is the total
number of tails obtained from tossing both coins, and
$G_Y(t)=\sum_{y=0}^2P(Y=y)t^y$.

**(e)** Given that the coefficient of $t^2$ in $G_Y(t)$ is $\frac13$, find
**(i)** the value of $p$; **(ii)** an expression for $G_Y(t)$.

$Z$ is the sum of $X$ and $Y$, and $G_Z(t)=G_X(t)G_Y(t)$.

**(f)** Given that $G_Z'(1)=E(Z)$, find $E(Z)$.
""")

code(r"""
q6_3p = ...      # p
q6_3y = ...      # G_Y(t)
q6_3z = ...      # E(Z)

balls = 'RRYYY'
draws = {(i, j): Rational(1, 20) for i in range(5) for j in range(5) if i != j}
X = Dist(draws, 'X', rule=lambda pair: (balls[pair[0]] == 'R') + (balls[pair[1]] == 'R'))
p = symbols('p')
Y = Dist(Dist({0: Rational(1, 2), 1: Rational(1, 2)}, 'fair') + Dist({0: 1 - p, 1: p}, 'biased'), 'Y')
top = Eq(P(Y == 2), Rational(1, 3))

verify_letters('6.3(e)(i)', q6_3p, p, [Y], [top])
verify_pgf('6.3(e)(ii)', q6_3y, Y, t, given=top, unknowns=p)
verify_moment('6.3(f)', q6_3z, Expect(X + Y), given=top, var=p)
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

**1.1** $4.5a+0.307=1$, $a=\boxed{0.154}$; probabilities $0.231, 0.308, 0.281, 0.154, 0.026$, mode $\boxed{2}$.

**1.2** $0.88+k-2k^2=1$ gives $\boxed{2k^2-k+0.12=0}$; $k=0.2$ or $0.3$, and
$k=0.2$ makes $P(X=1)=-0.08<0$: $\boxed{k=0.3}$.

**1.3** $\frac72p=1$, $\boxed{p=\frac27}$. $\boxed{0\le r\le1}$; $q=\frac{1-r}3$, so $\boxed{0\le q\le\frac13}$.

**1.4** $0.6-2a\ge0$, $3a\ge0$, $0.4-a\ge0$: $\boxed{0\le a\le0.3}$.

---

**2.1** $0.231+0.616+0.843+0.616+0.13=\boxed{2.44}$ ($2.436$ exact).

**2.2** With $k=0.3$: $0+0.02+0.92+0.33=\boxed{1.27}$.

**2.3** $E(X)=8p=\boxed{\frac{16}7}$. $E(Y)=6q+4r=4-6q$, so $\boxed{2\le E(Y)\le4}$.

**2.4** $\frac{34}{40}=\boxed{0.85}$; $\frac{60}{40}=\boxed{1.5}$; $\frac{1000\times1.5}{10}=\boxed{150}$.

**2.5** $\frac{1+6+15+28}{16}=\boxed{3.125}$.

**2.6** $0.2+0.64+0.864+0.6144+0.192=2.5104$ ✓

---

**3.1** $p+q=0.6$ and $p+3q=1$: $\boxed{p=0.4,\ q=0.2}$.

**3.2** $k^3-k^2-2k+0.7=0$; only $k=0.315870\ldots$ keeps every cell in
$[0,1]$, and $a=1-k-k^2-k^3=\boxed{0.553}$.

**3.3** $p+q=7$ and $p+2q+38=48$: $\boxed{p=4,\ q=3}$.

**3.4** $q=95-2p$ from the mean; the variance gives $p=45$ or $p=-10$, and
$p\in\mathbb{Z}^+$: $\boxed{p=45,\ q=5}$.

**3.5** $P(X<Y)=3p(q+r)=\frac67(q+r)=\frac12$, with $3q+r=1$: $q=\frac5{24}$,
$r=\frac38$, $E(Y)=4-6q=\boxed{\frac{11}4}$.

---

**4.1** $\mathrm{Var}(2-X)=\mathrm{Var}(X)=E(X^2)-E(X)^2=4.4-4=\boxed{0.4}$.

**4.2** $10\times3=\boxed{30}$.

**4.3** $a-4.723b=100$, $a-2.25b=150$: $b=20.2183\ldots$, $a=195.491\ldots$,
$\boxed{a=195,\ b=20}$. $\mathrm{Var}(P)=b^2\times0.906=370.356\ldots=\boxed{370}$.

**4.4** $E(Y^2)=7.4896$, $\mathrm{Var}(Y)=7.4896-2.5104^2=\boxed{1.19}$.

---

**5.1** (i) $x-1$ actions not boosted, then one boosted. (ii)
$\boxed{\sum_{x=1}^\infty xp(1-p)^{x-1}}$. (c)(ii) $a=p$, $r=1-p$:
$\frac{p}{p^2}=\frac1p$. (d) $\boxed{E(X)=10,\ \mathrm{Var}(X)=90}$.

**5.2** (i) $p=\frac1{2.5104}=\boxed{0.398}$. (ii) $\frac{1-p}{p^2}=\boxed{3.79}$.
(iii) The means are equal and $\mathrm{Var}(Y)=1.19<3.79$: the second model.

---

**6.1** $G'(1)=\frac{1+6+15+28}{16}=3.125=E(M)$ ✓

**6.2** $P(X=0)=\frac35\cdot\frac24=\frac3{10}$,
$P(X=1)=\frac25\cdot\frac34+\frac35\cdot\frac24=\frac35$,
$P(X=2)=\frac25\cdot\frac14=\frac1{10}$.

**6.3** (e)(i) $\frac12p=\frac13$, $\boxed{p=\frac23}$. (ii) $\boxed{G_Y(t)=\frac16+\frac12t+\frac13t^2}$.
(f) $E(Z)=G_X'(1)+G_Y'(1)=\frac45+\frac76=\frac{59}{30}=\boxed{1.97}$.
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
    n_q = sum(1 for c in cells if c['cell_type'] == 'markdown'
              for line in c['source'] if line.startswith('### '))
    print(f"{NOTEBOOK}: {len(cells)} ячеек, из них {n_code} с кодом, "
          f"вопросов {n_q}, эталонов {len(ANSWERS)}")


if __name__ == '__main__':
    build()
