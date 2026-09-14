"""Собирает практикум D4: дискретные случайные величины и математическое ожидание.

Двадцать восьмой практикум серии и четвёртый по статистике. Собран из трёх
тем корпуса: statistics.discrete_random_variables без биномиального,
statistics.expected_value без плотности и производящая функция из
statistics.probability. Первая тема статистики, стоящая на трёх бумагах
почти поровну: две пятых баллов на Paper 1, треть — два исследования
Paper 3.

Лестница из шести приёмов идёт по тому, что известно о таблице. Сначала
таблица с одной буквой, и работа — её собственные правила. Потом среднее.
Потом букв две, и вопрос даёт второе условие. Потом разброс и величина,
построенная из X. Напоследок Paper 3: распределение без последнего
значения и распределение, записанное многочленом.

Двадцать первое понятие равенства ответов: **таблица сама себе условие**.
Проверка не хранит ни одной буквы: она решает правила таблицы (клетки
в [0, 1], сумма единица) вместе с условиями вопроса и отбрасывает корни,
при которых клетка перестаёт быть вероятностью, — называя клетку.
Среднее, дисперсия, мода и производящая функция складываются по той же
таблице.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_d4.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/statistics/practicum-d4-discrete.ipynb')

TRIGGER = {1: 'table', 2: 'mean', 3: 'unknowns', 4: 'spread', 5: 'series',
           6: 'pgf', 7: 'unknowns', 8: 'table', 9: 'spread', 10: 'mean',
           11: 'pgf', 12: 'series'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '0.154',
    'q1m': '2',
    'q1b': '2.44',
    'q2a': 'Eq(2*k**2 - k + 0.12, 0)',
    'q2b': '0.3',
    'q2c': '1.27',
    'q3p': '0.85',
    'q3e': '1.5',
    'q3r': '150',
    'q4sum': 'Eq(p + q, 0.6)',
    'q4mean': 'Eq(p + 3*q, 1)',
    'q4': '[0.4, 0.2]',
    'q5': '0.553',
    'q6a': 'Rational(2, 7)',
    'q6b': 'Rational(16, 7)',
    'q6r': 'Interval(0, 1)',
    'q6q': 'Interval(0, Rational(1, 3))',
    'q6d': 'Interval(2, 4)',
    'q6qr': '[Rational(5, 24), Rational(3, 8)]',
    'q6e': 'Rational(11, 4)',
    'q7a': 'Interval(0, 0.3)',
    'q7b': '0.4',
    'q8': '[45, 5]',
    'q9ab': '[195, 20]',
    'q9v': '370',
    'q10b': 'Sum(x*p*(1 - p)**(x - 1), (x, 1, oo))',
    'q10m': '10',
    'q10v': '90',
    'q10ey': '2.5104',
    'q10vy': '1.19',
    'q10p': '0.398',
    'q10vx': '3.79',
    'q11a': '3.125',
    'q11g': 'Rational(1, 16) + Rational(3, 8)*t + Rational(15, 16)*t**2 + Rational(7, 4)*t**3',
    'q11c': '3.125',
    'q11d': 'Rational(3, 10) + Rational(3, 5)*t + Rational(1, 10)*t**2',
    'q11p': 'Rational(2, 3)',
    'q11y': 'Rational(1, 6) + t/2 + t**2/3',
    'q11z': '1.97',
    'qt_pq': '[4, 3]',
    'qt_b': '30',
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
# D4 — Discrete random variables and expectation

**104 marks of the archive, six techniques, eleven tasks.** Everything the
archive asks about a discrete random variable that is *not* binomial, from
May 2021 to November 2025: tables with letters in them, means, variances,
a variable built from another, and the two Paper 3 investigations that
derive the rules themselves.

This is the first statistics topic spread over all three papers: about
two fifths of the marks are on Paper 1, a third on Paper 3.

## The one idea

A discrete random variable is a **table**: the values it can take, and
the probability of each.

> **A table is a distribution only if every probability is between $0$
> and $1$, and all of them together add up to $1$.**

That sentence is the whole of the first technique. When a table has a
letter in it, those two rules are the equations and inequalities for the
letter — the question does not need to state them, and usually does not.
And a letter that solves the equation but makes one cell negative is not
an answer: the markscheme gives a separate mark for saying so.

## And the idea that carries the rest

Everything else about $X$ is a **weighted sum over the table**:

$$E(X)=\sum x\,P(X=x),\qquad \mathrm{Var}(X)=\sum\big(x-E(X)\big)^2P(X=x)=E(X^2)-E(X)^2$$

A frequency table is a table too, with probabilities $f/\sum f$. A
generating function is the table again, written as a polynomial.

## How the checks work

They do not know the answers. Each check is handed **the table and the
conditions** the question gives:

```python
X = Dist({0: 0.41, 1: k - 0.28, 2: 0.46, 3: 0.29 - 2*k**2})
verify_letters('2b', 0.3, k, [X])
```

is *"your $k$: does it make this table a distribution?"* The check solves
the table's own rules itself, throws away the roots that break a cell,
and compares. `Expect(X)` and `Var(X)` add up over the table; `P(X < Y)`
adds up over pairs of values.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| a root that makes a cell negative | which cell, and what it equals |
| $0<q<1$ for a probability | the ends belong: a probability can be $0$ or $1$ |
| a range from one cell alone | the cells also add up to one |
| $E(X^2)$ for the variance | the square of the mean has not been subtracted |
| $b\,\mathrm{Var}(T)$ for $\mathrm{Var}(a-bT)$ | the multiplier has not been squared |
| the largest probability for the mode | the mode is the value that has it |
| $G(t)$ with coefficients reversed | the opposite count |

A number built from a letter you rounded on the way — $p=0.398$, $b=20$ —
is **accepted, with a remark**, as the markscheme accepts it.

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | one letter in a table, and the mean | 1–3 |
| 🟡 | two letters and two conditions; spread and a variable built from $X$ | 4–9 |
| 🔴 | Paper 3: no last value, and the table as a polynomial | 10–11 |

Every task is a real past-paper question, cited.

**63 of these 104 marks are on a calculator paper, and the number
flatters the calculator.** On Paper 3 the generating function is
fractions and the mean of the first-success variable is $1/p$. Real GDC
work is about a dozen marks: a cubic, and a system from a mean and a variance.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Dist, Freq, Geo, P(), Expect, Var, Pgf

language('en')                 # this notebook is in English, and so are the checks

# Dist({value: probability}) is a table; letters are allowed inside.
# Freq({value: frequency}) is a frequency table read as a distribution.
# Comparisons are events, P() adds them up; Expect and Var add up over the table.
#     X = Dist({1: 0.2, 2: 0.5, 3: 0.3})
#     P(X >= 2), Expect(X), Var(5 - 2*X)
# The letter E is taken by e = 2.718..., so the mean is Expect(X).

print('ready; sympy', sp.__version__)
X = Dist({1: 0.2, 2: 0.5, 3: 0.3})
print('the table:        ', X)
print('P(X >= 2):        ', sympify(P(X >= 2)))
print('E(X), Var(X):     ', sympify(Expect(X)), sympify(Var(X)))
print('G(t):             ', Pgf(X, t))
""")

md(r"""
---
## Map of the six techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | a table must be a distribution | a letter in the table, *find $k$*, *range of $r$* | sum $=1$, every cell in $[0,1]$ |
| 2 | the mean | $E(X)$, *mean*, *expected number* | $\sum x\,P(X=x)$ |
| 3 | two letters, two conditions | two unknowns and one more fact: $E(X)$, a variance, $P(X<Y)$ | a system |
| 4 | spread, and a variable built from $X$ | $\mathrm{Var}$, $2-X$, *multiplied by 10*, $a-bt$ | $E(X^2)-E(X)^2$, $a^2\mathrm{Var}(X)$ |
| 5 | a first success | *until the first*: values $1,2,3,\dots$ with no end | a series |
| 6 | a generating function | $G(t)=\sum P(X=x)t^x$ | the table as a polynomial |

Techniques 1 and 2 are read straight off the table. Technique 3 is
technique 1 with one equation too few, and the question supplies it.
Technique 4 is technique 2 applied to $X^2$ or to $aX+b$. Techniques 5
and 6 are Paper 3: the same sums, where the table has no end or has been
turned into a polynomial.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. The table

## Theory: the two rules, and a letter inside

A game spinner scores $X$ points, with

| $x$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x)$ | $0.25$ | $k^2$ | $1-1.6k$ | $k-0.2$ |

**Rule two gives the equation.** The four cells add to one:

$$0.25+k^2+1-1.6k+k-0.2=1\ \Longrightarrow\ k^2-0.6k+0.05=0\ \Longrightarrow\ k=0.1\ \text{or}\ k=0.5$$

**Rule one decides between the roots.** Put each back into *every* cell:

- $k=0.1$ makes $P(X=3)=0.1-0.2=-0.1$. Not a probability — rejected;
- $k=0.5$ gives $0.25,\ 0.25,\ 0.2,\ 0.3$. All in $[0,1]$, sum $1$.

> **Write the reason.** *"$k=0.1$ is rejected because $P(X=3)<0$"* is a
> mark of its own (R1). The number $0.5$ without it is not the full
> answer.

**A range instead of a value.** If a table is $m,\ 3m,\ 1-4m$ for
$x=1,2,3$, the sum is already one for every $m$, and only rule one is
left: $m\ge0$, $3m\le1$, $1-4m\ge0$, so

$$0\le m\le\tfrac14$$

Both ends belong: a probability *can* be $0$. And the range comes from
**all** the cells together — $3m\le1$ alone would allow $m=\tfrac13$,
where the last cell is $-\tfrac13$.

**The mode** is the value with the largest probability — for the spinner,
$x=3$. Not $0.3$: that is its probability.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ3 Paper 2 Q3(a)–(b), 5 marks*

A supermarket analyses the shopping habits of its customers. The number
of times, $X$, each customer visits the supermarket in a week is given by
the following probability distribution.

| $x$ | $1$ | $2$ | $3$ | $4$ | $5$ | $\ge6$ |
|---|---|---|---|---|---|---|
| $P(X=x)$ | $1.5a$ | $2a$ | $0.281$ | $a$ | $0.026$ | $0$ |

**(a)** **(i)** Find the value of $a$. **(ii)** Write down the mode of $X$.

**(b)** Find the mean of $X$.

*The mean check does not use your $a$: it finds $a$ from the table itself,
so a slip in (a)(i) costs you (a)(i) only.*
""")

code(r"""
q1a = ...        # a
q1m = ...        # the mode of X
q1b = ...        # the mean of X

a = symbols('a')
visits = Dist({1: 1.5*a, 2: 2*a, 3: 0.281, 4: a, 5: 0.026, 6: 0})   # 6 stands for "6 or more"

verify_letters('1a(i)', q1a, a, [visits])
verify_mode('1a(ii)', q1m, visits, given=[], var=a)
verify_moment('1b', q1b, Expect(visits), given=[], var=a)
""")

# ================================================================= теория 2
md(r"""
## Theory: the mean is a weighted sum

For the spinner above, with $k=0.5$:

$$E(X)=0\times0.25+1\times0.25+2\times0.2+3\times0.3=1.55$$

Every value is multiplied by **its own** probability. $\frac{0+1+2+3}{4}=1.5$
is the average of the values — the mean of a spinner that lands on each
value equally often, which this one does not.

$E(X)$ need not be a value $X$ can take, and need not be a whole number:
it is where the table balances.

**A frequency table is a distribution.** A football team's goals in
$20$ matches:

| goals | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| matches | $4$ | $7$ | $6$ | $3$ |

Read each frequency as a probability by dividing by $20$. The estimated
probability of scoring in a match is $\frac{7+6+3}{20}=0.8$, and the
expected number of goals is

$$\frac{0\times4+1\times7+2\times6+3\times3}{20}=\frac{28}{20}=1.4$$

Over a season of $38$ matches that is $38\times1.4=53.2$ goals expected —
the mean scales with the number of matches.

> **"Expected" is not "will happen".** $53.2$ goals is a fine expected
> value. But *"how many buses must run"* asks for a whole number, and it
> is rounded **up**: a bus for part of the demand still has to run.
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ1 Paper 2 Q3, 6 marks*

A discrete random variable, $X$, has the following probability
distribution:

| $x$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x)$ | $0.41$ | $k-0.28$ | $0.46$ | $0.29-2k^2$ |

**(a)** Show that $2k^2-k+0.12=0$.

**(b)** Find the value of $k$, giving a reason for your answer.

**(c)** Hence, find $E(X)$.

*For (a), write the equation itself, as `Eq(left, right)`: any
rearrangement of it is accepted.*
""")

code(r"""
k = symbols('k')

q2a = ...        # the equation for k
q2b = ...        # k
q2c = ...        # E(X)

X = Dist({0: 0.41, 1: k - 0.28, 2: 0.46, 3: 0.29 - 2*k**2})

verify_equation('2a', q2a, Eq(total_probability(X), 1), var=k)
verify_letters('2b', q2b, k, [X])
verify_moment('2c', q2c, Expect(X), given=[], var=k)
""")

md(r"""
### Task 3 🟢 — *May 2023 TZ1 Paper 1 Q2, 6 marks*

On a Monday at an amusement park, a sample of $40$ visitors was randomly
selected as they were leaving the park. They were asked how many times
that day they had been on a ride called The Dragon. This information is
summarized in the following frequency table.

| number of times on The Dragon | $0$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|---|
| frequency | $6$ | $16$ | $13$ | $2$ | $3$ |

It can be assumed that this sample is representative of all visitors to
the park for the following day.

**(a)** For the following day, Tuesday, estimate
**(i)** the probability that a randomly selected visitor will ride The Dragon;
**(ii)** the expected number of times a visitor will ride The Dragon.

It is known that $1000$ visitors will attend the amusement park on
Tuesday. The Dragon can carry a maximum of $10$ people each time it runs.

**(b)** Estimate the minimum number of times The Dragon must run to
satisfy demand.
""")

code(r"""
q3p = ...        # P(a visitor rides The Dragon)
q3e = ...        # the expected number of rides per visitor
q3r = ...        # the minimum number of runs

rides = Freq({0: 6, 1: 16, 2: 13, 3: 2, 4: 3})

verify_chance('3a(i)', q3p, P(rides >= 1))
verify_moment('3a(ii)', q3e, Expect(rides))
verify_moment('3b', q3r, Expect(rides * 1000 / 10))
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. Two letters, and ranges

## Theory: one equation is not enough for two letters

A table with two unknowns,

| $x$ | $0$ | $1$ | $2$ | $3$ |
|---|---|---|---|---|
| $P(X=x)$ | $a$ | $b$ | $0.3$ | $0.1$ |

gives only $a+b=0.6$ from its sum. The question has to add a fact — say
$E(X)=1.05$ — and that fact is the second equation:

$$\begin{aligned}a+b&=0.6\\ 0\cdot a+1\cdot b+2(0.3)+3(0.1)&=1.05\end{aligned}
\qquad\Longrightarrow\qquad b=0.15,\quad a=0.45$$

Then rule one again: both cells in $[0,1]$. With squares and cubes of the
letter in the table, the system is not linear, and on Paper 2 the
calculator solves it — but it returns **every** root, and choosing among
them is still yours.

**A frequency table with unknown frequencies** is the same question. A
dice game recorded $14$ scores: $1$ occurred $f$ times, $2$ five times, $3$
$g$ times, and the mean score was $2.5$:

$$f+5+g=14,\qquad \frac{f+10+3g}{14}=2.5\ \Longrightarrow\ g=8,\ f=1$$

Here rule one reads differently: frequencies are **whole numbers**, not
below zero — and not below one, if the question says so.

**The second fact can be about two variables.** If $X$ and $Y$ are
independent, $P(X<Y)$ is a sum over pairs of values:

$$P(X<Y)=\sum_{x<y}P(X=x)\,P(Y=y)$$

— list the pairs where the first is smaller; the ties $x=y$ are not in it.

**Ranges.** When the question gives no second fact, a second letter is
*not* determined — and *"the range of possible values"* is what is asked.
Use the sum to write every cell in one letter, then apply rule one to each
cell. With $m,\ 3m,\ 1-4m$ from Part 1, $E(X)=m+6m+3-12m=3-5m$, and as
$m$ runs over $0\le m\le\frac14$:

$$\tfrac74\le E(X)\le3$$
""")

md(r"""
### Task 4 🟡 — *May 2022 TZ2 Paper 1 Q10(a), 5 marks*

A biased four-sided die with faces labelled $1$, $2$, $3$ and $4$ is rolled
and the result recorded. Let $X$ be the result obtained when the die is
rolled. The probability distribution for $X$ is given in the following
table where $p$ and $q$ are constants.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $p$ | $0.3$ | $q$ | $0.1$ |

For this probability distribution, it is known that $E(X)=2$.

**(a)** Show that $p=0.4$ and $q=0.2$.

*A "show that" is marked on the equations, so the equations are what you
hand in — one from the sum, one from the mean — and then the values they
give.*
""")

code(r"""
p, q = symbols('p q')

q4sum = ...      # the equation from the sum of the probabilities
q4mean = ...     # the equation from E(X) = 2
q4 = [...]       # [p, q]

X = Dist({1: p, 2: 0.3, 3: q, 4: 0.1})

verify_equation('4 sum', q4sum, Eq(total_probability(X), 1), var=p)
verify_equation('4 mean', q4mean, Eq(Expect(X), 2), var=p)
verify_letters('4', q4, [p, q], [X], [Eq(Expect(X), 2)])
""")

md(r"""
### Task 5 🟡 — *November 2023 TZ1 Paper 2 Q5, 5 marks*

The following table shows the probability distribution of a discrete
random variable $X$, where $a,k\in\mathbb{R}^+$.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $k$ | $k^2$ | $a$ | $k^3$ |

Given that $E(X)=2.3$, find the value of $a$.

*The cubic has three roots, and the calculator will show you all of them.
The check solves for $a$ and $k$ together and knows which roots the table
allows.*
""")

code(r"""
q5 = ...         # a

a, k = symbols('a k')
X = Dist({1: k, 2: k**2, 3: a, 4: k**3})

verify_letters('5', q5, a, [X], [Eq(Expect(X), 2.3)])
""")

md(r"""
### Task 6 🟡 — *May 2021 TZ1 Paper 1 Q10, 16 marks*

A biased four-sided die, A, is rolled. Let $X$ be the score obtained when
die A is rolled. The probability distribution for $X$ is given in the
following table.

| $x$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(X=x)$ | $p$ | $p$ | $p$ | $\frac12p$ |

**(a)** Find the value of $p$.

**(b)** Hence, find the value of $E(X)$.

A second biased four-sided die, B, is rolled. Let $Y$ be the score
obtained when die B is rolled. The probability distribution for $Y$ is
given in the following table.

| $y$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(Y=y)$ | $q$ | $q$ | $q$ | $r$ |

**(c)** **(i)** State the range of possible values of $r$. **(ii)** Hence,
find the range of possible values of $q$.

**(d)** Hence, find the range of possible values for $E(Y)$.

Agnes and Barbara play a game using these dice. Agnes rolls die A once and
Barbara rolls die B once. The probability that Agnes' score is less than
Barbara's score is $\frac12$.

**(e)** Find the value of $E(Y)$.

*A Paper 1 question, so exact values: `Rational(2, 7)`, and ranges as
`Interval(...)`. In (e) find $q$ and $r$ on the way — the markscheme gives
them a mark each.*
""")

code(r"""
q6a = ...        # p
q6b = ...        # E(X)
q6r = ...        # the range of r, as an Interval
q6q = ...        # the range of q
q6d = ...        # the range of E(Y)
q6qr = [...]     # [q, r] in part (e)
q6e = ...        # E(Y) in part (e)

p, q, r = symbols('p q r')
X = Dist({1: p, 2: p, 3: p, 4: p/2}, 'X')
Y = Dist({1: q, 2: q, 3: q, 4: r}, 'Y')
game = [Eq(P(X < Y), Rational(1, 2))]      # X and Y are independent

verify_letters('6a', q6a, p, [X])
verify_moment('6b', q6b, Expect(X), given=[], var=p)
verify_table_range('6c(i)', q6r, r, [Y])
verify_table_range('6c(ii)', q6q, q, [Y])
verify_table_range('6d', q6d, Expect(Y), [Y])
verify_letters('6e q, r', q6qr, [q, r], [X, Y], game)
verify_moment('6e', q6e, Expect(Y), given=game, var=[p, q, r], tables=[X])
""")

# ================================================================= теория 4
md(r"""
## Theory: variance, and a variable built from $X$

Variance is the mean squared distance from the mean. Take

| $x$ | $-1$ | $0$ | $2$ |
|---|---|---|---|
| $P(X=x)$ | $0.25$ | $0.5$ | $0.25$ |

$E(X)=-0.25+0+0.5=0.25$, and the quick way to the variance is through
$E(X^2)$ — the same weighted sum, with the values squared:

$$E(X^2)=1\times0.25+0+4\times0.25=1.25,\qquad
\mathrm{Var}(X)=E(X^2)-E(X)^2=1.25-0.0625=1.1875$$

Two things go wrong here, and both are one line short: handing in
$E(X^2)=1.25$ as the variance, and subtracting $E(X)=0.25$ instead of its
square.

**A variable built from $X$.** A prize is $Y=5-3X$ tokens. Then

$$E(Y)=5-3E(X)=4.25,\qquad \mathrm{Var}(Y)=(-3)^2\,\mathrm{Var}(X)=9\times1.1875=10.6875$$

> **Adding moves the table, multiplying stretches it.** The $5$ shifts
> every value and the spread is untouched. The $-3$ stretches by $3$ —
> and a variance is in squared units, so by $9$. The sign disappears:
> $\mathrm{Var}(-X)=\mathrm{Var}(X)$.

**When only $E$ and $\mathrm{Var}$ are known.** A city's daily temperature
$C$ in °C has $E(C)=20$ and $\mathrm{Var}(C)=4$. In Fahrenheit,
$F=1.8C+32$, so $E(F)=68$ and $\mathrm{Var}(F)=1.8^2\times4=12.96$ — no
table needed, because a linear change needs only those two numbers.

**For a frequency table** the variance divides by $\sum f$, like the
mean: it describes the data, not an estimate from a sample of it.
""")

md(r"""
### Task 7 🟡 — *November 2025 TZ3 Paper 1 Q7, 8 marks*

The discrete random variable $X$ has the following probability
distribution:

| $x$ | $1$ | $2$ | $3$ |
|---|---|---|---|
| $P(X=x)$ | $0.6-2a$ | $3a$ | $0.4-a$ |

**(a)** Find the range of possible values of $a$.

**(b)** In the case where $a=0.2$, determine $\mathrm{Var}(2-X)$.

*Part (a) is technique 1 — here the sum is one for every $a$, so only the
cells decide. Part (b) is six marks for what the theory above does in two
lines; the markscheme's first method starts with $\mathrm{Var}(2-X)=\mathrm{Var}(X)$.*
""")

code(r"""
q7a = ...        # the range of a, as an Interval
q7b = ...        # Var(2 - X)

a = symbols('a')
X = Dist({1: 0.6 - 2*a, 2: 3*a, 3: 0.4 - a})

verify_table_range('7a', q7a, a, [X])
verify_moment('7b', q7b, Var(2 - X), given=Eq(a, 0.2), var=a)
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ2 Paper 2 Q8, 7 marks*

The marks obtained by students in a class quiz are shown in the following
table where $p,q\in\mathbb{Z}^+$.

| marks | $20$ | $35$ | $p$ |
|---|---|---|---|
| frequency | $12$ | $q$ | $8$ |

The mean and variance of the marks are $31$ and $124$ respectively. Find
the value of $p$ and the value of $q$.

*Here one letter is a frequency and the other is a value — the table does
not mind. The system has two solutions; the question's $\mathbb{Z}^+$ rules
one of them out.*
""")

code(r"""
q8 = [...]       # [p, q]

p, q = symbols('p q', positive=True, integer=True)
quiz = Freq({20: 12, 35: q, p: 8})

verify_letters('8', q8, [p, q], [quiz], [Eq(Expect(quiz), 31), Eq(Var(quiz), 124)])
""")

md(r"""
### Task 9 🟡 — *May 2025 TZ1 Paper 2 Q11(e)–(f), 7 marks*

In a marathon race, the random variable $T$ represents the time, in hours,
taken for a runner to complete the race. No runner completes the race in
less than $2.25$ hours, and no runner completes it in more than $7.5$
hours.

Each runner's time is converted to a score which is calculated as
$a-bt$, where $t$ represents their time in hours, and $a,b>0$. Consider
the random variable $P$ which represents the score of a runner. It is
given that $E(P)=100$ and the maximum possible score is $150$.

**(e)** Use $E(T)=4.723$ to determine the value of $a$ and the value of
$b$, giving your answers to the nearest integer.

**(f)** Given also that $\mathrm{Var}(T)=0.906$, find $\mathrm{Var}(P)$.

*$T$ is continuous, and its density is D6's work — but $E(T)$ and
$\mathrm{Var}(T)$ are given, and a linear change needs nothing else. The
check stands $T$ in for two equally likely values with that mean and that
variance.*
""")

code(r"""
q9ab = [...]     # [a, b], to the nearest integer
q9v = ...        # the variance of the score

a, b = symbols('a b', positive=True)
T = Moments(4.723, 0.906, 'T')
fastest = 2.25                              # no runner is faster
score = [Eq(Expect(a - b*T), 100), Eq(a - b*fastest, 150)]

verify_letters('9e', q9ab, [a, b], [T], score, whole=True)
verify_moment('9f', q9v, Var(a - b*T), given=score, var=[a, b])
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 3. Paper 3: no last value, and the table as a polynomial

## Theory: a first success

Roll a fair die until the first six. $X$, the number of rolls, can be
$1,2,3,\dots$ with no largest value:

$$P(X=x)=\left(\tfrac56\right)^{x-1}\tfrac16$$

— $x-1$ failures, then the success. The table has no end, but it is still
a table, and the mean is still the weighted sum:

$$E(X)=\sum_{x=1}^{\infty}x\left(\tfrac56\right)^{x-1}\tfrac16$$

**How to add it up.** Start from a sum you know (A2):
$1+r+r^2+r^3+\dots=\frac1{1-r}$ for $|r|<1$. Differentiate both sides with
respect to $r$, term by term on the left:

$$1+2r+3r^2+4r^3+\dots=\frac1{(1-r)^2}$$

The left side is exactly the shape of the mean, with $r=\frac56$:

$$E(X)=\tfrac16\left(1+2\cdot\tfrac56+3\left(\tfrac56\right)^2+\dots\right)
=\tfrac16\cdot\frac1{(1/6)^2}=6$$

A six every six rolls, on average — which is what you expected, and now it
is proved. Task 10 makes the same move with a letter instead of
$\frac16$. The variance takes a second derivative; the exam gives its
formula, and for the die it is $30$.

> **Two models with the same mean are compared by their variance.** The
> smaller variance is the more *consistent* experience: the first success
> arrives closer to the same time, every time.
""")

md(r"""
### Task 10 🔴 — *May 2024 TZ1 Paper 3 Q1(b)–(d), (g)(ii)–(h), 13 marks*

In a new computer game, each time a player performs an action, there is a
random chance that the action will be *boosted*. In the first model, the
probability that an action will be boosted is constant.

**(b)** Suppose the probability that an action will be boosted is $p$,
where $0<p<1$. **(i)** Explain why the probability that the first boost
occurs on the $x$th action is $p(1-p)^{x-1}$. Let $X$ be the number of
actions until the first boost occurs. **(ii)** Hence, write down an
expression, using sigma notation, for $E(X)$ in terms of $x$ and $p$.

**(c)** Part (c)(i) shows that $\sum_{n=1}^\infty nar^{n-1}=\frac{a}{(1-r)^2}$.
**(ii)** Hence, show that $E(X)=\frac1p$.

It can be shown that $\mathrm{Var}(X)=\frac{1-p}{p^2}$.

**(d)** Find $E(X)$ and $\mathrm{Var}(X)$ when $p=0.1$.

In the designer's second model, the probability of a boost starts at
$0.2$ and rises by $0.2$ after every action that is not boosted. Let $Y$ be
the number of actions until the first boost occurs. Part (g)(i) finds the
probability distribution of $Y$:

| $y$ | $1$ | $2$ | $3$ | $4$ | $5$ |
|---|---|---|---|---|---|
| $P(Y=y)$ | $0.2$ | $0.32$ | $0.288$ | $0.1536$ | $0.0384$ |

**(g)** **(ii)** Show that $E(Y)=2.5104$. **(iii)** Find $\mathrm{Var}(Y)$.

**(h)** **(i)** Use the expression given in (c)(ii) to find the value of $p$
for which $E(X)=E(Y)$. **(ii)** Find $\mathrm{Var}(X)$ for this value of $p$.
**(iii)** Hence determine, with a reason, which model provides a more
consistent experience for the player with respect to boosted actions.

*(b)(i), (c)(ii) and (h)(iii) are words — they are in the solutions. The
check for (b)(ii) evaluates your sum at several values of $p$; write it
with `Sum(..., (x, 1, oo))`.*
""")

code(r"""
p = symbols('p')

q10b = ...       # E(X) as a sum, in x and p
q10m = ...       # E(X) when p = 0.1
q10v = ...       # Var(X) when p = 0.1
q10ey = ...      # E(Y)
q10vy = ...      # Var(Y)
q10p = ...       # p with E(X) = E(Y)
q10vx = ...      # Var(X) for that p

X = Geo(p, 'X')                             # the first boost, first model
Y = Dist({1: 0.2, 2: 0.32, 3: 0.288, 4: 0.1536, 5: 0.0384}, 'Y')
same_mean = Eq(Expect(X), Expect(Y))

verify_moment('10b(ii)', q10b, Expect(X))
verify_moment('10d E(X)', q10m, Expect(Geo(0.1)))
verify_moment('10d Var(X)', q10v, Var(Geo(0.1)))
verify_moment('10g(ii)', q10ey, Expect(Y))
verify_moment('10g(iii)', q10vy, Var(Y))
verify_letters('10h(i)', q10p, p, [X], [same_mean])
verify_moment('10h(ii)', q10vx, Var(X), given=same_mean, var=p)
""")

# ================================================================= теория 6
md(r"""
## Theory: a generating function

Write a table as a polynomial: the probability of $x$ becomes the
coefficient of $t^x$. A spinner scoring $0$, $1$, $2$ with probabilities
$\frac12,\frac13,\frac16$ has

$$G(t)=\tfrac12+\tfrac13t+\tfrac16t^2$$

Nothing is lost — the table can be read back off the coefficients — and
three facts come for free:

- **$G(1)=1$**, because at $t=1$ the polynomial is the sum of the table;
- **$G'(1)=E(X)$**: $G'(t)=\sum x\,P(X=x)\,t^{x-1}$, and at $t=1$ that is
  the weighted sum. Here $G'(t)=\frac13+\frac13t$, so $E(X)=\frac23$;
- **for independent $X$ and $Y$, $G_{X+Y}=G_X\,G_Y$.** Multiplying out
  collects every pair of scores whose sum is the power of $t$.

Spin twice and add: $G(t)^2=\frac14+\frac13t+\frac{5}{18}t^2+\frac19t^3+\frac1{36}t^4$,
and $E=2\times\frac23=\frac43$ — with $E(X+Y)=E(X)+E(Y)$ there is no need
to multiply out at all.

> **The coefficients are built, not guessed.** Each is a probability from
> the experiment — a tree, or combinations — and the markscheme gives no
> marks for coefficients stated without that working.
""")

md(r"""
### Task 11 🔴 — *May 2025 TZ1 Paper 3 Q1(a), (c)–(f), 22 marks*

Two unbiased tetrahedral (four-sided) dice with faces labelled $1$, $2$, $3$
and $4$ are thrown and the scores recorded. The random variable $M$ denotes
the maximum of these two scores.

| $m$ | $1$ | $2$ | $3$ | $4$ |
|---|---|---|---|---|
| $P(M=m)$ | $\frac1{16}$ | $\frac3{16}$ | $\frac5{16}$ | $\frac7{16}$ |

**(a)** Find $E(M)$.

The distribution of $M$ is represented by
$G(t)=\frac1{16}t+\frac3{16}t^2+\frac5{16}t^3+\frac7{16}t^4$.

**(c)** **(i)** Find $G'(t)$. **(ii)** Hence, show that $G'(1)=E(M)$.

A bag contains two red balls and three yellow balls. Two balls are
selected at random without replacement from the bag. The random variable
$X$ denotes the total number of red balls selected, and $G_X(t)=\sum_{x=0}^2P(X=x)t^x$.

**(d)** Show that $G_X(t)=\frac3{10}+\frac35t+\frac1{10}t^2$, making it
clear how the coefficients of $G_X(t)$ have been determined.

An unbiased coin and a biased coin are tossed. The probability of
obtaining a tail on the biased coin is $p$. The random variable $Y$
denotes the total number of tails obtained from tossing both coins, and
$G_Y(t)=\sum_{y=0}^2P(Y=y)t^y$.

**(e)** Given that the coefficient of $t^2$ in $G_Y(t)$ is $\frac13$, find
**(i)** the value of $p$; **(ii)** an expression for $G_Y(t)$.

The random variable $Z$ denotes the sum of $X$ and $Y$, and
$G_Z(t)=G_X(t)\,G_Y(t)$.

**(f)** For random variable $Z$, it can be shown that $G_Z'(1)=E(Z)$. Use
this result to find $E(Z)$.

*No check below holds a coefficient. $M$ is built from the sixteen throws,
$X$ from the twenty ordered draws, $Y$ as the sum of two coins.*
""")

code(r"""
q11a = ...       # E(M)
q11g = ...       # G'(t)
q11c = ...       # G'(1)
q11d = ...       # G_X(t)
q11p = ...       # p
q11y = ...       # G_Y(t)
q11z = ...       # E(Z)

throws = {(i, j): Rational(1, 16) for i in range(1, 5) for j in range(1, 5)}
M = Dist(throws, 'M', rule=max)

balls = 'RRYYY'
draws = {(i, j): Rational(1, 20) for i in range(5) for j in range(5) if i != j}
X = Dist(draws, 'X', rule=lambda pair: (balls[pair[0]] == 'R') + (balls[pair[1]] == 'R'))

p = symbols('p')
fair = Dist({0: Rational(1, 2), 1: Rational(1, 2)}, 'fair')     # 1 is a tail
biased = Dist({0: 1 - p, 1: p}, 'biased')
Y = Dist(fair + biased, 'Y')
top = Eq(P(Y == 2), Rational(1, 3))

verify_moment('11a', q11a, Expect(M))
verify_derivative('11c(i)', q11g, Pgf(M, t), var=t)
verify_moment("11c(ii) G'(1)", q11c, Expect(M))
verify_pgf('11d', q11d, X, t)
verify_letters('11e(i)', q11p, p, [Y], [top])
verify_pgf('11e(ii)', q11y, Y, t, given=top, unknowns=p)
verify_moment('11f', q11z, Expect(X + Y), given=top, var=p)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `table` | a letter in a table: the sum and the cells |
| `mean` | a mean, an expected number, a weighted sum |
| `unknowns` | two unknowns and one more fact about the distribution |
| `spread` | a variance, or a variable built from $X$ |
| `series` | until the first success: values with no end |
| `pgf` | a generating function |

1. $P(X=x)=cx$ for $x=1,2,3,4$. Find $c$.
2. A shop sells $0$, $1$, $2$ or $3$ cakes an hour with probabilities $0.1,0.3,0.4,0.2$. Find the expected number of cakes sold in an eight-hour day.
3. A table has cells $a$, $0.2$, $b$, $0.3$ for $x=0,1,2,3$ and $E(X)=1.5$. Find $a$ and $b$.
4. $E(X)=3$ and $\mathrm{Var}(X)=2$. Find $\mathrm{Var}(4-3X)$.
5. A basketball player shoots until she scores, each shot scoring with probability $0.35$. Find the expected number of shots.
6. $G(t)=\frac14(1+t)^2$. Find $P(X=1)$ and $E(X)$.
7. The frequencies $3$, $f$, $g$, $2$ of the scores $1,2,3,4$ total $15$, and the mean score is $2.4$. Find $f$ and $g$.
8. A table has cells $0.5-k$, $2k$, $0.5-k$. State the range of possible values of $k$.
9. Each score in a data set is multiplied by $5$ and then $3$ is subtracted. The old standard deviation was $1.2$. Find the new variance.
10. $X$ takes the values $-2$, $0$, $3$ with probabilities $0.3,0.5,0.2$. Find $E(X)$.
11. Two independent variables have $G_X(t)=0.4+0.6t$ and $G_Y(t)=0.7+0.3t$. Find the distribution of $X+Y$.
12. A machine fails each day with probability $0.02$, independently. Find the variance of the number of days up to and including the first failure.
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
## On the clock — *May 2024 TZ1 Paper 1 Q1, 6 marks*

**Six marks, seven minutes.** No calculator, no hints.

Claire rolls a six-sided die $16$ times. The scores obtained are shown in
the following frequency table.

| score | $1$ | $2$ | $3$ | $4$ | $5$ | $6$ |
|---|---|---|---|---|---|---|
| frequency | $p$ | $q$ | $4$ | $2$ | $0$ | $3$ |

It is given that the mean score is $3$.

**(a)** Find the value of $p$ and the value of $q$.

Each of Claire's scores is multiplied by $10$ in order to determine the
final score for a game she is playing.

**(b)** Write down the mean final score.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_pq = [...]    # [p, q]
qt_b = ...       # the mean final score

p, q = symbols('p q', integer=True, nonnegative=True)
rolls = Freq({1: p, 2: q, 3: 4, 4: 2, 5: 0, 6: 3})
claire = [Eq(rolls.size, 16), Eq(Expect(rolls), 3)]

verify_letters('timer (a)', qt_pq, [p, q], [rolls], claire)
verify_moment('timer (b)', qt_b, Expect(10 * rolls), given=claire, var=[p, q])
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)(i)** The cells add to one:

$$1.5a+2a+0.281+a+0.026+0=1\ \Longrightarrow\ 4.5a=0.693\ \Longrightarrow\ \boxed{a=0.154}$$

**1 (a)(ii)** The probabilities are $0.231,\ 0.308,\ 0.281,\ 0.154,\ 0.026$:
the largest belongs to $x=2$, so the mode is $\boxed{2}$ visits.

**1 (b)**

$$E(X)=1(0.231)+2(0.308)+3(0.281)+4(0.154)+5(0.026)=2.436=\boxed{2.44}$$

The markscheme prints $2.436$ as exact: every cell is known to three
decimal places, so the mean is too.

---

**2 (a)**

$$0.41+(k-0.28)+0.46+(0.29-2k^2)=1\ \Longrightarrow\ 0.88+k-2k^2=1
\ \Longrightarrow\ \boxed{2k^2-k+0.12=0}$$

**2 (b)** $k=\dfrac{1\pm\sqrt{1-0.96}}{4}=\dfrac{1\pm0.2}{4}$, so $k=0.3$ or
$k=0.2$. But $k=0.2$ makes $P(X=1)=0.2-0.28=-0.08<0$, which is not a
probability. $\boxed{k=0.3}$ — and the sentence about $P(X=1)$ is the R1.

**2 (c)** With $k=0.3$ the table is $0.41,\ 0.02,\ 0.46,\ 0.11$:

$$E(X)=0+0.02+0.92+0.33=\boxed{1.27}$$

---

**3 (a)(i)** $34$ of the $40$ rode at least once: $\dfrac{34}{40}=\boxed{0.85}$.

**3 (a)(ii)**

$$\frac{0(6)+1(16)+2(13)+3(2)+4(3)}{40}=\frac{60}{40}=\boxed{1.5}$$

**3 (b)** $1000\times1.5=1500$ rides expected, at $10$ a run: $\boxed{150}$ runs.

---

**4** From the sum: $p+0.3+q+0.1=1$, so $\boxed{p+q=0.6}$.
From the mean: $p+0.6+3q+0.4=2$, so $\boxed{p+3q=1}$.

Subtracting, $2q=0.4$: $\boxed{q=0.2,\ p=0.4}$. The markscheme gives the two
equations two marks each, independently, and one for solving them.

---

**5** Two equations:

$$k+k^2+a+k^3=1,\qquad k+2k^2+3a+4k^3=2.3$$

Eliminate $a$ ($a=1-k-k^2-k^3$): $k^3-k^2-2k+0.7=0$, with roots
$k=0.315870\ldots$, $-1.18538\ldots$ and $1.86951\ldots$ Only the first
leaves every cell in $[0,1]$ — the cell $P(X=1)=k$ is negative for the
second and above one for the third — and it gives

$$a=1-k-k^2-k^3=0.552839\ldots=\boxed{0.553}$$

The markscheme note: $a=2.44587$ or $a=-10.8987$ from the other roots
scores the method and loses the answer, and $0.55$ loses it too.

---

**6 (a)** $3p+\frac12p=1$: $\boxed{p=\frac27}$.

**6 (b)** $E(X)=p(1+2+3)+4\cdot\frac12p=8p=\boxed{\frac{16}7}$.

**6 (c)(i)** $r$ is a probability: $\boxed{0\le r\le1}$.

**6 (c)(ii)** $3q=1-r$, so $q=\frac{1-r}3$, and as $r$ runs from $1$ to $0$:
$\boxed{0\le q\le\frac13}$.

**6 (d)** $E(Y)=q+2q+3q+4r=6q+4(1-3q)=4-6q$, and over $0\le q\le\frac13$:
$\boxed{2\le E(Y)\le4}$.

**6 (e)** Agnes' score is less than Barbara's in the pairs
$(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)$:

$$P(X<Y)=p(2q+r)+p(q+r)+p\,r=3p(q+r)=\tfrac67(q+r)=\tfrac12$$

so $q+r=\frac7{12}$. With $3q+r=1$: $2q=\frac5{12}$, $\boxed{q=\frac5{24}}$,
$\boxed{r=\frac38}$, and

$$E(Y)=4-6\cdot\tfrac5{24}=\boxed{\tfrac{11}4}$$

---

**7 (a)** Every cell at least zero: $0.6-2a\ge0$, $3a\ge0$, $0.4-a\ge0$.
Together, $\boxed{0\le a\le0.3}$ — the middle condition is $a\le0.4$, and
it is the first cell that binds. The sum is $1$ for every $a$.

**7 (b)** $\mathrm{Var}(2-X)=(-1)^2\mathrm{Var}(X)=\mathrm{Var}(X)$. With $a=0.2$
the table is $0.2,\ 0.6,\ 0.2$: $E(X)=2$ by symmetry,
$E(X^2)=0.2+2.4+1.8=4.4$, and

$$\mathrm{Var}(2-X)=4.4-2^2=\boxed{0.4}$$

---

**8** $\sum f=20+q$. Mean:

$$\frac{240+35q+8p}{20+q}=31\ \Longrightarrow\ 4q+8p=380\ \Longrightarrow\ q=95-2p$$

Variance, through the squared deviations from $31$:

$$\frac{12(11)^2+16q+8(p-31)^2}{20+q}=124$$

Substituting $q=95-2p$ gives a quadratic in $p$ with roots $p=45$ and
$p=-10$. The question says $p\in\mathbb{Z}^+$: $\boxed{p=45,\ q=5}$. The
markscheme note: giving both pairs scores A1A0.

---

**9 (e)** $E(P)=a-bE(T)$, so $a-4.723b=100$. The best score belongs to the
fastest time, $t=2.25$: $a-2.25b=150$. Subtracting, $2.473b=50$:

$$b=20.2183\ldots,\quad a=195.491\ldots\qquad\boxed{a=195,\ b=20}$$

**9 (f)** $\mathrm{Var}(P)=(-b)^2\mathrm{Var}(T)=20.2183\ldots^2\times0.906=370.356\ldots=\boxed{370}$

With $b=20$ carried from (e) the answer is $362$ — the markscheme accepts
anything from $362$ to $370$. The check accepts it too, with a remark.

---

**10 (b)(i)** The first boost on the $x$th action means $x-1$ actions not
boosted, each with probability $1-p$, then one boosted: $p(1-p)^{x-1}$.

**10 (b)(ii)** $\boxed{E(X)=\displaystyle\sum_{x=1}^\infty x\,p(1-p)^{x-1}}$

**10 (c)(ii)** This is $\sum nar^{n-1}$ with $a=p$, $r=1-p$:

$$E(X)=\frac{p}{\big(1-(1-p)\big)^2}=\frac{p}{p^2}=\frac1p$$

**10 (d)** $E(X)=\boxed{10}$, $\mathrm{Var}(X)=\dfrac{0.9}{0.01}=\boxed{90}$.

**10 (g)(ii)** $0.2+2(0.32)+3(0.288)+4(0.1536)+5(0.0384)=2.5104$ ✓

**10 (g)(iii)** $E(Y^2)=0.2+4(0.32)+9(0.288)+16(0.1536)+25(0.0384)=7.4896$, so

$$\mathrm{Var}(Y)=7.4896-2.5104^2=1.18749\ldots=\boxed{1.19}$$

**10 (h)(i)** $\dfrac1p=2.5104$: $p=0.398342\ldots=\boxed{0.398}$

**10 (h)(ii)** $\mathrm{Var}(X)=\dfrac{1-0.398342\ldots}{0.398342\ldots^2}=3.79170\ldots=\boxed{3.79}$

(The markscheme accepts $3.80$, from $p=0.398$.)

**10 (h)(iii)** The means are equal and $\mathrm{Var}(Y)=1.19<3.79=\mathrm{Var}(X)$:
the **second model** is more consistent.

---

**11 (a)** $E(M)=\dfrac{1+6+15+28}{16}=\dfrac{50}{16}=\boxed{3.125}$

**11 (c)(i)** $G'(t)=\boxed{\frac1{16}+\frac38t+\frac{15}{16}t^2+\frac74t^3}$

**11 (c)(ii)** $G'(1)=\dfrac{1+6+15+28}{16}=3.125=E(M)$ ✓

**11 (d)** Two draws without replacement, from $2$ red and $3$ yellow:

$$P(X=0)=\tfrac35\cdot\tfrac24=\tfrac3{10},\qquad
P(X=1)=\tfrac25\cdot\tfrac34+\tfrac35\cdot\tfrac24=\tfrac35,\qquad
P(X=2)=\tfrac25\cdot\tfrac14=\tfrac1{10}$$

and these are the coefficients: $\boxed{G_X(t)=\frac3{10}+\frac35t+\frac1{10}t^2}$.

**11 (e)(i)** Two tails needs a tail on both: $\frac12p=\frac13$, so $\boxed{p=\frac23}$.

**11 (e)(ii)** $P(Y=0)=\frac12\cdot\frac13=\frac16$,
$P(Y=1)=\frac12\cdot\frac13+\frac12\cdot\frac23=\frac12$:

$$\boxed{G_Y(t)=\tfrac16+\tfrac12t+\tfrac13t^2}$$

With $p=\frac13$ instead, the coefficients come out reversed — the heads,
not the tails.

**11 (f)** $G_Z'(1)=G_X'(1)+G_Y'(1)$, because $G_X(1)=G_Y(1)=1$:

$$E(Z)=\left(\tfrac35+\tfrac2{10}\right)+\left(\tfrac12+\tfrac23\right)=\tfrac45+\tfrac76=\tfrac{59}{30}=\boxed{1.97}$$

---

## Timer

**(a)** Sixteen rolls: $p+q+9=16$, so $p+q=7$. Mean three:
$p+2q+12+8+18=48$, so $p+2q=10$. Hence $\boxed{q=3,\ p=4}$.

**(b)** Every score multiplied by $10$ multiplies the mean by $10$: $\boxed{30}$.
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
