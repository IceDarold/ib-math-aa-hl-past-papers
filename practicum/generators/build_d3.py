"""Собирает практикум D3: биномиальное распределение.

Двадцать седьмой практикум серии и третий по статистике. Как и A2,
собран из двух тем корпуса сразу, но по другой причине: там одна тема
продолжала другую, здесь одну тему разметка разрезала пополам. Вопросы
про X ~ B(n, p) лежат почти поровну в statistics.probability и
statistics.discrete_random_variables, и граница между ними случайна —
две соседние части одного вопроса бывают в разных темах.

Лестница из шести приёмов идёт по тому, что делают с распределением.
Сначала берут одно значение, потом диапазон — и здесь вся трудность
темы: перевести «more than 6» в то, что умеет калькулятор. Потом
описывают распределение целиком средним и дисперсией. Потом режут его
условием. Потом ставят поверх другого. Напоследок неизвестным становится
само n.

Двадцатое понятие равенства ответов: **распределение складывается по
значениям**. Проверка знает только P(X = k) и складывает: вероятность
события — по значениям, при которых оно выполняется, среднее — по k·P,
наименьшее n — перебором. Ни np, ни 1 − (1 − p)ⁿ внутри нет. Событие
при этом помнит, из каких сравнений собрано, и неверный ответ разбирается
по границам: какая сдвинута и в какую сторону.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_d3.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/statistics/practicum-d3-binomial.ipynb')

TRIGGER = {1: 'exact', 2: 'cumulative', 3: 'mean', 4: 'conditional',
           5: 'nested', 6: 'trials', 7: 'cumulative', 8: 'mean',
           9: 'nested', 10: 'conditional', 11: 'exact', 12: 'trials'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '0.214',
    'q1b': '0.382',
    'q2a': '0.0419',
    'q2b': '0.0746',
    'q3': '0.0739',
    'q4d': '4.56',
    'q4e': '0.169',
    'q5p': '[0.641, 0.359]',
    'q5v': '23',
    'q6a': '0.785',
    'q6b': '0.761',
    'q7i': '0.0133',
    'q7l': '0.848',
    'q7ii': '0.0157',
    'q8': '0.00394',
    'q9r': '0.477',
    'q9s': '0.350',
    'q9': '0.493',
    'q10': '17',
    'q11a': '0.898',
    'q11c': '0.227',
    'q11n': '94',
    'qt_n': '17',
    'qt_3': '0.242',
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
# D3 — The binomial distribution

**62 marks of the archive, six techniques, eleven tasks.** Everything the
archive asks about $X\sim B(n,p)$ from May 2021 to May 2025. All of it is
on Paper 2, and all of it is a calculator question — which is exactly why
people lose marks here: the calculator does the sum and does not check
what it was asked to sum.

## The one idea

A binomial variable counts successes.

> **The same trial, repeated a fixed number of times, independently, with
> the same chance of success each time.** $X$ is how many successes.

Four conditions, and each one is a question you can ask of the story:
is there a fixed $n$? only two outcomes per trial? does $p$ stay the
same? does one trial tell you nothing about the next? If all four are
yes, then

$$P(X=k)=\binom nk\,p^{\,k}(1-p)^{\,n-k},\qquad k=0,1,\dots,n$$

— $p^k(1-p)^{n-k}$ is one particular order of $k$ successes and $n-k$
failures, and $\binom nk$ counts the orders.

## And the idea that carries the marks

Your calculator has two buttons for this: **binompdf** gives $P(X=k)$,
and **binomcdf** gives $P(X\le k)$ — *at most*, and nothing else. Every
other phrase in a question has to be turned into one of those two by you:

> *more than 6* is $X\ge7$, which is $1-P(X\le6)$. *Fewer than 49* is
> $X\le48$. *At least 10* is $1-P(X\le9)$.

The calculator will happily compute $1-P(X\le10)$ for *at least 10*. It
is a correct number. It is the answer to a different question.

## How the checks work

They do not know the answers. Each check is handed **the model and the
event**, written the way the paper writes them:

```python
flights = Bin(64, 0.0711930)
verify_binomial('4e', 0.169, P(flights > 6))
```

is *"your number: is it the probability that more than six of 64 flights
are late?"* The check knows only $P(X=k)$, and adds it up over
$k=7,8,\dots,64$. $np$, $np(1-p)$ and $1-(1-p)^n$ appear nowhere in it —
the mean is a sum of $k\,P(X=k)$, and the least $n$ is found by trying
$n=1,2,3,\dots$

In your own cells, the calculator is there too: `binompdf(n, p, k)` and
`binomcdf(n, p, k)`, or `binomcdf(n, p, a, b)` for $P(a\le X\le b)$ the way
a Casio does it.

When you are wrong the check says **how** — and above all, **which
boundary**:

| what you wrote | what the check says |
|---|---|
| $1-P(X\le5)$ for *more than 6* | «X > 6» starts at 7, and this counts 6 as well |
| $1-P(X\le10)$ for *at least 10* | «X ≥ 10» includes 10 itself |
| $P(X\le10)$ for *exactly 10* | cdf where pdf was wanted |
| $P(X\le49)$ for *fewer than 49* | the boundary is off (in the condition) |
| the model with $1-p$ | success and failure are swapped |
| *at least one of the two* for *exactly one* | the case where both happen does not belong here |
| $0.042$ | two significant figures: (M1)A0 without working |

A number computed from a probability you rounded to three figures on the
way is **accepted, with a remark** — the markscheme does the same.

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the model is given; one value, then a run of values | 1–3 |
| 🟡 | describe the distribution, or cut it with a condition | 4–7 |
| 🔴 | a binomial on top of something else, or $n$ unknown | 8–11 |

Every task is a real past-paper question, cited.

**100% of these marks are on a calculator paper, and the number is
honest.** $P(X\le6)$ for $B(50,0.08)$ is seven terms nobody adds by hand,
and the markscheme writes *use of tables* as a method. What the
calculator cannot do is the translation — and that is where the method
marks sit.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Bin, P(), Expect, Var, binompdf, binomcdf

language('en')                 # this notebook is in English, and so are the checks

p = symbols('p')               # the probability of success, when it is the unknown


# Bin(n, p) is X ~ B(n, p). Comparisons on it are events, and P() adds them up:
#     X = Bin(8, 0.7)
#     P(X == 6), P(X <= 6), P(X == 3, given=X <= 4)
# Expect(X) and Var(X) are E(X) and Var(X) — the letter E is taken by e = 2.718...

print('ready; sympy', sp.__version__)
X = Bin(8, 0.7)
print('the model:            ', X)
print('P(X = 6):             ', binompdf(8, 0.7, 6))
print('P(X <= 6):            ', binomcdf(8, 0.7, 6))
print('the same, as an event:', float(sympify(P(X <= 6))))
""")

md(r"""
---
## Map of the six techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | one value | *exactly $k$* | binompdf |
| 2 | a run of values | *at most*, *at least*, *more than*, *fewer than* | binomcdf, with the boundary moved by you |
| 3 | mean and variance | *expected number*, $\mathrm{Var}$, a variance given | $np$, $np(1-p)$, $a^2\mathrm{Var}(X)$ |
| 4 | a condition inside one distribution | *given that* — and both events are about the same $X$ | $\frac{P(\text{overlap})}{P(\text{condition})}$ |
| 5 | binomial on top of something | a *box*, a *competitor*, a *day* that succeeds when something inside it does | model inside, model outside |
| 6 | unknown $n$ | *least number of trials*, *find $n$* | logs, or a table |

Techniques 1 and 2 are one skill: reading an event off the words. Every
later technique uses technique 2 somewhere, which is why it has the most
tasks. Technique 3 is the only one where the answer is not a probability.
Techniques 4 and 5 are D2's conditional probability and tree, with the
binomial supplying the numbers. Technique 6 turns the question around.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Reading the event off the words

## Theory: is it binomial, and one value

A basketball player makes a free throw with probability $0.7$, and takes
$8$ of them. Fixed number of trials, two outcomes, the same $p$,
independent throws — so the number made is

$$X\sim B(8,\,0.7),\qquad P(X=6)=\binom86(0.7)^6(0.3)^2=28\times0.117649\times0.09=0.296$$

On the calculator that is `binompdf(8, 0.7, 6)`.

**Write the model down before the number.** *"$X\sim B(8,0.7)$"* is the
method mark. With it, a correct number scores both marks; without it,
the markscheme says *"if no working shown, award (M1)A0"* for a
two-significant-figure answer, and sometimes for a three-figure one.

> **Not everything that counts is binomial.** Drawing cards without
> replacement changes $p$ each time. *"Until the first success"* has no
> fixed $n$ — that is D2's first success. The four questions above are
> worth asking every time, and the exam sometimes asks you to state them.

**Where $p$ comes from.** In half the questions in this topic, $p$ is the
answer to an earlier part — a normal probability, an integral, a
percentage. Carry it **unrounded**. $p=0.365$ instead of $0.365112$
changes the fourth figure of the answer, and the fourth figure is
sometimes the third.
""")

md(r"""
### Task 1 🟢 — *May 2022 TZ1 Paper 2 Q11(b) and May 2023 TZ2 Paper 2 Q3(d), 4 marks*

**(a)** The weights of chocolate muffins are normally distributed, and
part (a) of the question finds that the probability that a randomly
selected muffin weighs less than $61$ g is $0.365112\ldots$

In a random selection of $12$ chocolate muffins, find the probability
that exactly $5$ weigh less than $61$ g.

**(b)** The weights of bags of rice are normally distributed, and the
earlier parts of the question find that the probability that a bag
weighs less than $w$ grams is $0.0849303\ldots$

Ten bags of rice are selected at random. Find the probability that
exactly one of the bags weighs less than $w$ grams.

*The normal probabilities are D5's work and are given here. What is
yours is the model: name it, then press one button.*
""")

code(r"""
q1a = ...        # P(exactly 5 of the 12 muffins weigh less than 61 g)
q1b = ...        # P(exactly 1 of the 10 bags weighs less than w g)

muffins = Bin(12, 0.365112)
bags = Bin(10, 0.0849303)

verify_binomial('1a', q1a, P(muffins == 5))
verify_binomial('1b', q1b, P(bags == 1))
""")

# ================================================================= теория 2
md(r"""
## Theory: a run of values, and moving the boundary yourself

Take $Y\sim B(20,\,0.3)$. Draw the values it can take, and mark what each
phrase means:

| the question says | the event | on the calculator | value |
|---|---|---|---|
| at most 5 | $Y\le5$ | `binomcdf(20, 0.3, 5)` | $0.416$ |
| fewer than 5 | $Y\le4$ | `binomcdf(20, 0.3, 4)` | $0.238$ |
| at least 5 | $Y\ge5$ | `1 - binomcdf(20, 0.3, 4)` | $0.762$ |
| more than 5 | $Y\ge6$ | `1 - binomcdf(20, 0.3, 5)` | $0.584$ |
| at least one | $Y\ge1$ | `1 - binompdf(20, 0.3, 0)` | $0.999$ |

Read the rows as pairs. *At least 5* and *fewer than 5* are complements:
together they cover $0,1,\dots,20$ once. *More than 5* and *at most 5*
are complements. That is the whole rule:

> **To get "at least $k$", subtract "at most $k-1$" from one.** The
> boundary moves by one because $k$ itself belongs to *at least $k$*, and
> $1-P(Y\le k)$ has thrown it away.

**"At least one" is always a complement**, and it is the one case where
the calculator is not needed: $1-(0.7)^{20}$. Adding $P(Y=1)+\dots+P(Y=20)$
gets the same number more slowly and loses a term more often.

**Write the inequality on its own line.** $P(X\ge10)=1-P(X\le9)$ is a line
of working, and the markscheme gives it M1 by itself. The number that
follows is the A1.
""")

md(r"""
### Task 2 🟢 — *May 2024 TZ1 Paper 2 Q6(a)–(b), 4 marks*

In Happyland, the weather on any given day is independent of the weather
on any other day. On any day in May, the probability of rain is $0.2$.
May has $31$ days. Find the probability that

**(a)** it rains on exactly $10$ days in May;
**(b)** it rains on at least $10$ days in May.

*Part (c) of this question — the first rainy day being the tenth — is not
binomial at all: there is no fixed number of trials. It is in D2.*
""")

code(r"""
q2a = ...        # P(exactly 10 rainy days)
q2b = ...        # P(at least 10 rainy days)

rain = Bin(31, 0.2)

verify_binomial('2a', q2a, P(rain == 10))
verify_binomial('2b', q2b, P(rain >= 10))
""")

md(r"""
### Task 3 🟢 — *May 2025 TZ2 Paper 2 Q10(d), 3 marks*

At Adam's Apple Orchard the weights of apples are normally distributed,
and an apple is *premium* when its weight is between $170$ and $185$
grams. Part (c) of the question finds that $62.8364\ldots\%$ of apples are
premium.

Boxes are filled with randomly chosen apples. Each box contains $40$
apples.

**(d)** Find the probability that a randomly chosen box contains at least
$30$ premium apples.

*Keep your answer: task 8 is the next part of this question, and it uses
it.*
""")

code(r"""
q3 = ...         # P(at least 30 premium apples in a box of 40)

box = Bin(40, 0.628364)

verify_binomial('3', q3, P(box >= 30))
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. Describing the distribution, and cutting it

## Theory: mean, variance, and working backwards from them

A quiz has $40$ multiple-choice questions with four options each, and a
student guesses every one. The number right is $X\sim B(40,\,0.25)$, and

$$E(X)=np=10,\qquad \mathrm{Var}(X)=np(1-p)=40\times0.25\times0.75=7.5$$

$E(X)$ is an **expected number**, not a number that will happen: it does
not have to be a whole number, and rounding it to one loses the mark.

**A variable built from $X$.** Say each right answer scores $+3$ and each
wrong one $-1$. The score is $S=3X-(40-X)=4X-40$, and

$$E(S)=4E(X)-40=0,\qquad \mathrm{Var}(S)=4^2\,\mathrm{Var}(X)=120$$

> **The constant goes, the multiplier is squared.** Adding $40$ to every
> score moves the distribution without spreading it. Multiplying by $4$
> spreads it four times — and variance is measured in squares.

**Backwards.** If $X\sim B(50,\,p)$ and $\mathrm{Var}(X)=8$, then
$50p(1-p)=8$, that is $50p^2-50p+8=0$, and

$$p=0.2\quad\text{or}\quad p=0.8$$

**Both.** $p(1-p)$ does not change when $p$ and $1-p$ swap places —
counting failures instead of successes spreads out exactly as much. A
question that gives only the variance cannot tell the two apart, and
neither should your answer.
""")

md(r"""
### Task 4 🟡 — *May 2021 TZ2 Paper 2 Q10(d)–(e), 6 marks*

The flight times between two cities are normally distributed, and the
earlier parts of the question find that the probability that a randomly
selected flight takes more than $80$ minutes is $0.0711930\ldots$

On a particular day, there are $64$ flights scheduled between these two
cities.

**(d)** Find the expected number of flights that will have a flight time
of more than $80$ minutes.
**(e)** Find the probability that more than $6$ of the flights on this
particular day will have a flight time of more than $80$ minutes.

*Two "more than"s in one question, and they are not the same kind. The
first is inside the definition of a success; the second is the boundary
of the event.*
""")

code(r"""
q4d = ...        # the expected number of late flights
q4e = ...        # P(more than 6 late flights)

flights = Bin(64, 0.0711930)

verify_moment('4d', q4d, Expect(flights))
verify_binomial('4e', q4e, P(flights > 6))
""")

md(r"""
### Task 5 🟡 — *November 2023 TZ1 Paper 2 Q6, 5 marks*

The random variable $X$ is such that $X\sim B(25,\,p)$ and
$\mathrm{Var}(X)=5.75$.

**(a)** Find the possible values of $p$.

The random variable $Y$ is such that $Y=1-2X$.

**(b)** Find $\mathrm{Var}(Y)$.

*The check for (a) builds the variance of $B(25,p)$ by adding over all
$26$ values, solves it itself, and compares both roots with yours. The
check for (b) does not use your $p$ at all — it works from the question's
own condition, so a slip in (a) costs you (a) only.*
""")

code(r"""
q5p = [...]      # every possible value of p
q5v = ...        # Var(Y)

condition = Eq(Var(Bin(25, p)), 5.75)

verify_parameter('5a', q5p, condition, p)
verify_moment('5b', q5v, Var(1 - 2 * Bin(25, p)), given=condition, var=p)
""")

# ================================================================= теория 4
md(r"""
## Theory: a condition inside one distribution

*"Given that…"* is D2's conditional probability, unchanged:

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}$$

What is new is that $A$ and $B$ are both **ranges of the same $X$**, and
the overlap has to be found on the number line, not on a Venn diagram.

For $Y\sim B(12,\,0.4)$:

$$P(Y\ge2\mid Y\le5)=\frac{P(2\le Y\le5)}{P(Y\le5)}=\frac{0.646}{0.665}=0.971$$

The numerator is not $P(Y\ge2)$. Values $6,7,\dots,12$ are in
$Y\ge2$ but not in $Y\le5$, and they have no business in the fraction.
When one event sits entirely inside the other — $P(Y=3\mid Y\le4)$ — the
overlap is just the smaller event:

$$P(Y=3\mid Y\le4)=\frac{P(Y=3)}{P(Y\le4)}=\frac{0.142}{0.438}=0.324$$

> **Name the events in context.** The markscheme writes, every time,
> *"recognition must be shown in context either in words or symbols but
> not just $P(A\mid B)$"*. $P(Y=3\mid Y\le4)$ is context. $P(A\mid B)$ is
> not, and scores M0.

**The condition has its own boundary**, and it is translated exactly as
in Part 1. A numerator that is right and a denominator that includes one
value too many is a wrong answer by a few per cent — close enough to look
fine, and the markscheme has a note naming that exact mistake.
""")

md(r"""
### Task 6 🟡 — *November 2021 Paper 2 Q3, 7 marks*

A factory manufactures lamps. It is known that the probability that a
lamp is found to be defective is $0.05$. A random sample of $30$ lamps is
tested.

**(a)** Find the probability that there is at least one defective lamp in
the sample.
**(b)** Given that there is at least one defective lamp in the sample,
find the probability that there are at most two defective lamps.

*If your (b) comes out bigger than one, the numerator has more in it than
the overlap. Look at which values are in both events.*
""")

code(r"""
q6a = ...        # P(at least one defective)
q6b = ...        # P(at most two defective | at least one defective)

lamps = Bin(30, 0.05)

verify_binomial('6a', q6a, P(lamps >= 1))
verify_binomial('6b', q6b, P(lamps <= 2, given=lamps >= 1))
""")

md(r"""
### Task 7 🟡 — *November 2023 TZ1 Paper 2 Q10(c), 6 marks*

A farmer is growing a field of wheat plants. It is known that the
probability that the height of a plant is greater than $98.1$ cm is
$0.434$.

The farmer measures $100$ randomly selected plants. Any plant with a
height greater than $98.1$ cm is considered ready to harvest. Heights of
plants are independent of each other.

**(i)** Find the probability that exactly $34$ plants are ready to
harvest.
**(ii)** Given that fewer than $49$ plants are ready to harvest, find the
probability that exactly $34$ plants are ready to harvest.

*Write down the probability of the condition on its own as well. The
markscheme gives it an A1 "seen anywhere" — and it is the number that
goes wrong.*
""")

code(r"""
q7i = ...        # P(exactly 34 ready)
q7l = ...        # P(fewer than 49 ready)
q7ii = ...       # P(exactly 34 ready | fewer than 49 ready)

plants = Bin(100, 0.434)

verify_binomial('7(i)', q7i, P(plants == 34))
verify_binomial('7(ii) condition', q7l, P(plants < 49))
verify_binomial('7(ii)', q7ii, P(plants == 34, given=plants < 49))
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 3. Binomial on top of something, and $n$ as the unknown

## Theory: when a success is itself a probability

A seed germinates with probability $0.9$. Seeds are sold in packets of
$20$, and a packet is *good* if at least $18$ of its seeds germinate. A
shop has $6$ packets. What is the probability that exactly $5$ are good?

Two binomials, one inside the other, and the whole question is deciding
**what one trial is**:

- **inside**, a trial is a seed: $G\sim B(20,\,0.9)$, and a packet is good
  with probability $q=P(G\ge18)=0.677$;
- **outside**, a trial is a packet: $K\sim B(6,\,q)$, and
  $P(K=5)=0.276$.

The mistake is to reach the outside model with the inside $p$ —
$B(6,\,0.9)$ — which answers a question about six seeds.

> **Carry $q$ unrounded.** It is an answer, so it is tempting to round it;
> it is also the $p$ of the next model, where the rounding is raised to
> the fifth power.

**"Exactly one of the two."** Two people, each with their own model, each
succeeding or not independently. It is a tree with two branches, and only
the two mixed paths count:

$$P(\text{exactly one})=P(A)\big(1-P(B)\big)+P(B)\big(1-P(A)\big)$$

*At least one* would add the path where both succeed. *$P(A)+P(B)$* adds
it twice.
""")

md(r"""
### Task 8 🔴 — *May 2025 TZ2 Paper 2 Q10(e), 2 marks*

*(This continues task 3: a box of $40$ apples, each premium with
probability $0.628364\ldots$)*

**(e)** If $10$ of these boxes are randomly selected, find the
probability that exactly $4$ boxes have at least $30$ premium apples.

*Build the outside model from the inside one. The check accepts an answer
built from your rounded task 3 — with a remark.*
""")

code(r"""
q8 = ...         # P(exactly 4 of the 10 boxes have at least 30 premium apples)

box = Bin(40, 0.628364)
boxes = Bin(10, P(box >= 30))        # a trial is now a box

verify_binomial('8', q8, P(boxes == 4))
""")

md(r"""
### Task 9 🔴 — *May 2022 TZ2 Paper 2 Q8, 7 marks*

Rachel and Sophia are competing in a javelin-throwing competition. The
distances thrown by each are normally distributed, and a single throw
reaches $60$ m with probability $0.1216725\ldots$ for Rachel and
$0.0824333\ldots$ for Sophia.

In the first round of competition, each competitor must have five throws.
To qualify for the next round of competition, a competitor must record at
least one throw of $60$ metres or greater in the first round.

Find the probability that only one of Rachel or Sophia qualifies for the
next round of competition.

*Seven marks and no parts, so make your own: first the probability that
each of them qualifies, then the combination.*
""")

code(r"""
q9r = ...        # P(Rachel qualifies)
q9s = ...        # P(Sophia qualifies)
q9 = ...         # P(only one of them qualifies)

rachel = Bin(5, 0.1216725, 'R')      # the number of Rachel's throws of 60 m or more
sophia = Bin(5, 0.0824333, 'S')

verify_binomial('9 Rachel', q9r, P(rachel >= 1))
verify_binomial('9 Sophia', q9s, P(sophia >= 1))
verify_binomial('9', q9, P((rachel >= 1) ^ (sophia >= 1)))   # ^ is "exactly one of"
""")

# ================================================================= теория 6
md(r"""
## Theory: the least $n$, and $n$ from a table

A game gives a prize with probability $0.1$ on each go. How many goes
make the probability of at least one prize greater than $0.95$?

$$P(X\ge1)=1-0.9^{\,n}>0.95\ \Longrightarrow\ 0.9^{\,n}<0.05\
\Longrightarrow\ n>\frac{\ln0.05}{\ln0.9}=28.43\ldots$$

and so $n=29$. Two things to watch in that line:

- **dividing by $\ln0.9$ flips the inequality**, because $\ln0.9<0$. Do it
  without flipping and you get $n<28.43$, which is nonsense for a
  *least* $n$;
- **$28.43$ is not the answer.** $n$ counts goes. The answer is the whole
  number on the correct side of the boundary — and checking both
  neighbours takes ten seconds: $1-0.9^{28}=0.9477$ (not yet),
  $1-0.9^{29}=0.9529$ (enough).

> **On a calculator paper you do not need logs.** The May 2024 markscheme
> prints *METHOD 2 (TABLE ONLY APPROACH)* next to the logarithm method,
> with the same five marks. A table of $1-0.9^n$ against $n$ is also the
> only way that works when the event is not "at least one".

**$n$ from an approximate probability.** If $X\sim B(n,\,0.1)$ and
$P(X\le2)\approx0.485$, no logarithm helps: $P(X\le2)$ is three terms,
each with its own power of $n$. Tabulate it — $n=26$ gives $0.511$,
$n=27$ gives $0.485$, $n=28$ gives $0.459$ — and read off $n=27$.
""")

md(r"""
### Task 10 🔴 — *May 2024 TZ2 Paper 2 Q5, 5 marks*

Consider a random variable $X$ such that $X\sim B(n,\,0.25)$.

Determine the least value of $n$ such that $P(X\ge1)>0.99$.

*The check finds the least $n$ the way the table does: by trying
$n=1,2,3,\dots$ If you hand it the boundary from a logarithm, it will
tell you why that is not yet the answer.*
""")

code(r"""
q10 = ...        # the least n

verify_trials('10', q10, lambda n: P(Bin(n, 0.25) >= 1), holds=lambda value: value > 0.99)
""")

md(r"""
### Task 11 🔴 — *May 2025 TZ3 Paper 2 Q11(a)–(b), 8 marks*

Amanda enters data from surveys into a database. It can be assumed that
the accuracy of any survey entered is independent of all other surveys
entered. From previous records, it is known that Amanda enters $8\%$ of
the surveys inaccurately.

**(a)** On a particular day Amanda enters data from $50$ surveys.

**(i)** Find the probability that Amanda entered at most six surveys
inaccurately.
**(ii)** Given that at most six surveys were entered inaccurately, find
the probability that exactly four surveys were entered inaccurately.

On a different day Amanda enters data from $n$ surveys. On this day, the
probability that at most six surveys were entered inaccurately is
approximately $0.367$.

**(b)** Find the value of $n$.

*Three techniques in one question: a run of values, a condition, and $n$
from a table. In (b) the answer is not the least $n$ of anything — it is
the $n$ whose probability rounds to $0.367$.*
""")

code(r"""
q11a = ...       # P(at most six inaccurate out of 50)
q11c = ...       # P(exactly four | at most six)
q11n = ...       # n

surveys = Bin(50, 0.08)

verify_binomial('11a(i)', q11a, P(surveys <= 6))
verify_binomial('11a(ii)', q11c, P(surveys == 4, given=surveys <= 6))
verify_trials('11b', q11n, lambda n: P(Bin(n, 0.08) <= 6), near=0.367)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `exact` | *exactly $k$*: one value, binompdf |
| `cumulative` | *at most*, *at least*, *more than*, *fewer than* |
| `mean` | *expected number*, a mean or a variance, or $p$ from one |
| `conditional` | *given that*, and both events are about the same count |
| `nested` | a success is itself a probability, or *exactly one of two* |
| `trials` | $n$ is the unknown |

1. A test has $15$ questions with four options each, all guessed. Find the probability of exactly $7$ right.
2. $5\%$ of bolts are faulty. In a box of $200$, find the probability that at most $8$ are faulty.
3. $X\sim B(n,p)$ with $E(X)=12$ and $\mathrm{Var}(X)=3$. Find $n$ and $p$.
4. A spinner shows red with probability $0.35$ and is spun $20$ times. Given that red appears at least $5$ times, find the probability that it appears exactly $7$ times.
5. Each egg in a carton of $12$ is cracked with probability $0.02$, and a carton with more than one cracked egg is rejected. Find the probability that exactly $3$ of $50$ cartons are rejected.
6. How many times must a fair die be rolled for the probability of at least one six to exceed $0.9$?
7. A seed germinates with probability $0.85$. Of $30$ seeds, find the probability that more than $25$ germinate.
8. A fair coin is tossed $400$ times. Find the standard deviation of the number of heads.
9. Two archers shoot $6$ arrows each and hit with probabilities $0.6$ and $0.75$. Find the probability that exactly one of them hits at least $5$ times.
10. $X\sim B(10,0.3)$. Find $P(X=2\mid X<4)$.
11. A bulb is defective with probability $0.03$. In a sample of $25$, find the probability that exactly one is defective.
12. $X\sim B(n,0.2)$ and $P(X\le3)\approx0.411$. Find $n$.
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
## On the clock — *May 2023 TZ1 Paper 2 Q11(c)–(d), 5 marks*

**Five marks, seven minutes.** No hints this time.

A laboratory trial uses an amount of reagent $X$ whose probability density
function gives $P(X<0.5)=0.239358\ldots$ Each laboratory trial is
independent. A trial is considered a success when $X<0.5$.

**(c)** Determine the least number of trials required to be $99\%$ sure of
at least one success.

Ten trials were conducted.

**(d)** Find the probability that exactly three trials were successful.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_n = ...       # the least number of trials
qt_3 = ...       # P(exactly three successes in ten)

success = 0.239358

verify_trials('timer (c)', qt_n, lambda n: P(Bin(n, success) >= 1),
              holds=lambda value: value >= 0.99)
verify_binomial('timer (d)', qt_3, P(Bin(10, success) == 3))
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** Let $M$ be the number of the $12$ muffins weighing less than
$61$ g. Twelve independent muffins, each light with the same probability:

$$M\sim B(12,\,0.365112\ldots),\qquad P(M=5)=0.213666\ldots=\boxed{0.214}$$

**1 (b)** Let $L$ be the number of the ten bags lighter than $w$:

$$L\sim B(10,\,0.0849303\ldots),\qquad P(L=1)=0.382076\ldots=\boxed{0.382}$$

In both, the M1 is for the model. The markscheme accepts it as
*"recognition of binomial eg $B(12,0.365\ldots)$"* — written, not
implied by the number.

---

**2 (a)** Let $X$ be the number of rainy days. $X\sim B(31,\,0.2)$:

$$P(X=10)=\binom{31}{10}(0.2)^{10}(0.8)^{21}=0.0418894\ldots=\boxed{0.0419}$$

**2 (b)** *At least 10* is everything except $0,\dots,9$:

$$P(X\ge10)=1-P(X\le9)=1-0.925400\ldots=\boxed{0.0746}$$

$1-P(X\le10)=0.0327$ is the answer to *more than 10*. And the markscheme
note is worth reading: *"If no working shown, award (M1)A0 for 0.075
(2 sf)"* — the third figure is not decoration.

---

**3** Let $A$ be the number of premium apples in a box. $A\sim B(40,\,0.628364\ldots)$:

$$P(A\ge30)=1-P(A\le29)=\boxed{0.0739}$$

The markscheme gives (A1) for the model with both parameters, separately
from the M1 for recognising it — three marks on one button.

---

**4 (d)** Let $L$ be the number of late flights. $L\sim B(64,\,0.0711930\ldots)$:

$$E(L)=np=64\times0.0711930\ldots=4.55635\ldots=\boxed{4.56}\ \text{flights}$$

Not $5$, and not $4$: an expected number is a mean.

**4 (e)** *More than 6* starts at $7$:

$$P(L>6)=P(L\ge7)=1-P(L\le6)=1-0.830880\ldots=\boxed{0.169}$$

$1-P(L\le5)=0.304$ counts six late flights as "more than six".

---

**5 (a)** $\mathrm{Var}(X)=np(1-p)$:

$$25p(1-p)=5.75\Longrightarrow 25p^2-25p+5.75=0\Longrightarrow
p=\frac{25\pm\sqrt{625-575}}{50}=\frac12\pm\frac{\sqrt2}{10}$$

$$\boxed{p=0.641\ \text{or}\ p=0.359}$$

A1A1, one for each. They add to one, and that is not a coincidence: $p$
and $1-p$ give the same variance.

**5 (b)** The constant goes, the multiplier is squared:

$$\mathrm{Var}(Y)=\mathrm{Var}(1-2X)=(-2)^2\,\mathrm{Var}(X)=4\times5.75=\boxed{23}$$

Whichever $p$ it was — part (b) does not need to know.

---

**6 (a)** Let $D$ be the number of defective lamps. $D\sim B(30,\,0.05)$:

$$P(D\ge1)=1-P(D=0)=1-0.95^{30}=\boxed{0.785}$$

**6 (b)** Both events are about $D$. The values that are *at least one*
**and** *at most two* are $1$ and $2$:

$$P(D\le2\mid D\ge1)=\frac{P(1\le D\le2)}{P(D\ge1)}
=\frac{0.338903\ldots+0.258636\ldots}{0.785361\ldots}
=\frac{0.597540\ldots}{0.785361\ldots}=\boxed{0.761}$$

$\frac{P(D\le2)}{P(D\ge1)}=\frac{0.812178}{0.785361}=1.03$ is the
numerator with $D=0$ still in it — and a probability above one is the
loudest signal this topic gives you.

---

**7 (i)** Let $H$ be the number of plants ready. $H\sim B(100,\,0.434)$:

$$P(H=34)=0.0133198\ldots=\boxed{0.0133}$$

**7 (ii)** *Fewer than 49* is $H\le48$:

$$P(H<49)=P(H\le48)=\boxed{0.848}$$

The overlap of *exactly 34* and *fewer than 49* is just $H=34$:

$$P(H=34\mid H<49)=\frac{0.0133198\ldots}{0.848218\ldots}=\boxed{0.0157}$$

The markscheme names the trap in a note: *"If the candidate finds
$P(X\le49)=0.890474\ldots$ and uses that to calculate
$P(34\mid X<49)=0.0149581\ldots$ award (A0)(M1)(A1)A0."* One value too
many in the denominator costs two of the four marks.

---

**8** A trial is now a box, succeeding with the probability from task 3.
Let $Y$ be the number of the ten boxes with at least $30$ premium apples:

$$Y\sim B(10,\,0.0738617\ldots),\qquad P(Y=4)=0.00394413\ldots=\boxed{0.00394}$$

With $0.0739$ carried instead, the answer is $0.00395$ — accepted as
follow-through, but it is the kind of difference that sometimes is not.
Using $B(10,\,0.628)$, the apple's probability instead of the box's,
answers a question about ten apples.

---

**9** For one competitor, qualifying means at least one of five throws
reaches $60$ m. Let $N_R\sim B(5,\,0.1216725\ldots)$ and
$N_S\sim B(5,\,0.0824333\ldots)$ count their long throws:

$$P(N_R\ge1)=1-(1-0.1216725\ldots)^5=\boxed{0.477}\qquad
P(N_S\ge1)=1-(1-0.0824333\ldots)^5=\boxed{0.350}$$

Only one qualifies — Rachel and not Sophia, or Sophia and not Rachel:

$$\begin{aligned}&0.477264\ldots\times0.650412\ldots\\
+\ &0.349588\ldots\times0.522736\ldots\\
=\ &0.493160\ldots=\boxed{0.493}\end{aligned}$$

Or, as the markscheme's second route: $P(A)+P(B)-2P(A)P(B)$. The
$2$ is what separates *exactly one* from *at least one*, whose answer
$0.660$ is one subtraction short.

---

**10** $P(X\ge1)=1-P(X=0)=1-0.75^{\,n}$:

$$1-0.75^{\,n}>0.99\Longrightarrow0.75^{\,n}<0.01\Longrightarrow
n>\frac{\ln0.01}{\ln0.75}=16.0078\ldots$$

$$\boxed{n=17}$$

The neighbours, as the table method prints them: $n=16$ gives
$0.989977\ldots<0.99$, and $n=17$ gives $0.992483\ldots>0.99$. A boundary
of $16.0078$ is so close to $16$ that rounding to the nearest is the
natural mistake, and this question is built to catch it.

---

**11 (a)(i)** Let $E$ be the number of inaccurate surveys.
$E\sim B(50,\,0.08)$:

$$P(E\le6)=0.898128\ldots=\boxed{0.898}$$

**11 (a)(ii)** *Exactly four* lies inside *at most six*, so the overlap is
$E=4$:

$$P(E=4\mid E\le6)=\frac{P(E=4)}{P(E\le6)}=\frac{0.203654\ldots}{0.898128\ldots}=\boxed{0.227}$$

**11 (b)** Now $E\sim B(n,\,0.08)$, and $P(E\le6)$ falls as $n$ grows.
Tabulate around where it crosses $0.367$:

| $n$ | $93$ | $94$ | $95$ |
|---|---|---|---|
| $P(E\le6)$ | $0.378$ | $0.367$ | $0.356$ |

$$\boxed{n=94}$$

The markscheme gives M1 for *"at least one correct value of $P(E\le6)$
for a value of $n$, where $n\ne50$"* — the table is the method.

---

## Timer

**(c)** Let $Y\sim B(n,\,0.239358\ldots)$ count the successes.

$$P(Y\ge1)=1-(1-0.239358\ldots)^{\,n}\ge0.99\Longrightarrow
n\ge\frac{\ln0.01}{\ln0.760641\ldots}=16.8321\ldots$$

$$\boxed{17\ \text{trials}}$$

By table: $n=16$ gives $0.987443\ldots$, $n=17$ gives $0.990448\ldots$
With $0.239$ instead of $0.239358\ldots$ the boundary is $16.8612$ and
the table values $0.987348$, $0.990371$ — the markscheme lists both, and
the answer does not move.

**(d)** $Y\sim B(10,\,0.239358\ldots)$:

$$P(Y=3)=0.242430\ldots=\boxed{0.242}$$
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
