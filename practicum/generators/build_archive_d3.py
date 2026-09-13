"""Собирает архивный ноутбук D3: вся тема биномиального распределения подряд.

Пятнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6 и A2. Практикум учит: лестница из приёмов, теория перед
каждым, три уровня сложности, тренажёр распознавания, задание на время.
Архив не учит. Он даёт набивать руку: **вся тема подряд, по тем же шести
приёмам, без единой строчки теории**. Двадцать вопросов, 62 балла — всё,
что архив спрашивает про X ~ B(n, p) с мая 2021 по май 2025.

Разметка взята из карточки statistics-binomial.yaml: поле blocks у каждого
приёма. Ноябрьский дубль 2023 года входит один раз, копией TZ1; из-за
него в карточке 23 блока, а здесь 20 вопросов.

Тема маленькая, и практикум забрал почти все её вопросы, так что архив
почти совпадает с ним по составу. Отличается он порядком — строго по
приёмам, по одному вопросу за раз, — отсутствием теории и подсказок, и
тем, что части одного вопроса разнесены по своим приёмам: майский 2023
TZ1 Q11 стоит в § 1 пунктом (d) и в § 6 пунктом (c).

Где p получено из нормального распределения или из интеграла, оно дано
числом, и об этом сказано в условии: как его получить — D5 и D6.

Хешей в ноутбуке нет ни одного: всякий ответ темы — вероятность события,
среднее, дисперсия или число испытаний, и всякий получается сложением
по значениям распределения.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_d3.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/archive-d3-binomial.ipynb')

ANSWERS = {
    # § 1. One value
    'q1_1': '0.214',
    'q1_2': '0.382',
    'q1_3': '0.0419',
    'q1_4': '0.242',
    # § 2. A run of values
    'q2_1': '0.0746',
    'q2_2': '0.169',
    'q2_3': '0.0739',
    'q2_4': '0.898',
    'q2_5': '0.785',
    # § 3. Mean and variance
    'q3_1': '4.56',
    'q3_2': '[0.641, 0.359]',
    'q3_3': '23',
    # § 4. A condition inside one distribution
    'q4_1': '0.761',
    'q4_2': '0.227',
    'q4_3i': '0.0133',
    'q4_3l': '0.848',
    'q4_3': '0.0157',
    # § 5. Binomial on top of something
    'q5_1': '0.00394',
    'q5_2r': '0.477',
    'q5_2s': '0.350',
    'q5_2': '0.493',
    # § 6. Unknown n
    'q6_1': '17',
    'q6_2': '17',
    'q6_3': '94',
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
# D3 archive — the binomial distribution, all of it

**Twenty questions, 62 marks.** Every question the archive asks about
$X\sim B(n,p)$, from May 2021 to May 2025, in the order of the six
techniques rather than the order of the papers.

No theory. No worked examples. Open it, answer twenty questions, close
it. The theory is in the practicum, `practicum-d3-binomial.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | One value | 4 | 8 |
| 2 | A run of values | 5 | 13 |
| 3 | Mean and variance | 3 | 8 |
| 4 | A condition inside one distribution | 3 | 13 |
| 5 | Binomial on top of something | 2 | 9 |
| 6 | Unknown $n$ | 3 | 11 |

Answers go on one line each, to three significant figures. The checks
are the same ones the practicum uses and they store nothing: each is
handed the model and the event — `P(flights > 6)` — and adds up
$P(X=k)$ over the values that belong to it. When an answer is wrong
because a boundary moved, the check says which boundary.

**Every probability that comes from somewhere else is given.** Seven of
these questions take $p$ from a normal distribution or an integral in an
earlier part. Those parts are D5's and D6's; here the number is in the
question.

**The November 2023 paper appears once**, although the archive holds it
twice as TZ1 and TZ2.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Bin, P(), Expect, Var, binompdf, binomcdf

language('en')                 # this notebook is in English, and so are the checks

p = symbols('p')               # the probability of success, when it is the unknown

print('ready; sympy', sp.__version__)
print('X ~ B(8, 0.7): P(X = 6) =', binompdf(8, 0.7, 6), ' P(X <= 6) =', binomcdf(8, 0.7, 6))
""")

# ============================================================ § 1
md(r"""
---
# § 1. One value

**Four questions, 8 marks.** *Exactly $k$*: name the model, then one
button.
""")

md(r"""
### 1.1 — *May 2022 TZ1 Paper 2 Q11(b), 2 marks*

The weights of chocolate muffins are normally distributed with mean
$62$ g and standard deviation $2.9$ g, so that the probability that a
randomly selected chocolate muffin weighs less than $61$ g is
$0.365112\ldots$

In a random selection of $12$ chocolate muffins, find the probability
that exactly $5$ weigh less than $61$ g.

### 1.2 — *May 2023 TZ2 Paper 2 Q3(d), 2 marks*

The weights of bags of rice are normally distributed, and $80\%$ of the
bags weigh between $w$ grams and $210$ grams, so that the probability
that a randomly selected bag weighs less than $w$ grams is
$0.0849303\ldots$

Ten bags of rice are selected at random. Find the probability that
exactly one of the bags weighs less than $w$ grams.
""")

code(r"""
q1_1 = ...       # P(exactly 5 of 12 muffins under 61 g)
q1_2 = ...       # P(exactly 1 of 10 bags under w g)

muffins = Bin(12, 0.365112)
bags = Bin(10, 0.0849303)

verify_binomial('1.1', q1_1, P(muffins == 5))
verify_binomial('1.2', q1_2, P(bags == 1))
""")

md(r"""
### 1.3 — *May 2024 TZ1 Paper 2 Q6(a), 2 marks*

In Happyland, the weather on any given day is independent of the weather
on any other day. On any day in May, the probability of rain is $0.2$.
May has $31$ days. Find the probability that it rains on exactly $10$
days in May.

### 1.4 — *May 2023 TZ1 Paper 2 Q11(d), 2 marks*

Each laboratory trial is independent, and a trial is a success with
probability $0.239358\ldots$ (the probability, from part (b), that the
amount of reagent used is less than $0.5$ ml).

Ten trials were conducted. Find the probability that exactly three trials
were successful.
""")

code(r"""
q1_3 = ...       # P(exactly 10 rainy days)
q1_4 = ...       # P(exactly 3 successes in 10 trials)

rain = Bin(31, 0.2)
trials = Bin(10, 0.239358)

verify_binomial('1.3', q1_3, P(rain == 10))
verify_binomial('1.4', q1_4, P(trials == 3))
""")

# ============================================================ § 2
md(r"""
---
# § 2. A run of values

**Five questions, 13 marks.** *At most*, *at least*, *more than* — turned
into $P(X\le k)$ by you, not by the calculator.
""")

md(r"""
### 2.1 — *May 2024 TZ1 Paper 2 Q6(b), 2 marks*

*(Happyland, as in 1.3.)* Find the probability that it rains on at least
$10$ days in May.

### 2.2 — *May 2021 TZ2 Paper 2 Q10(e), 3 marks*

The flight times between two cities are normally distributed, and the
probability that a flight takes more than $80$ minutes is
$0.0711930\ldots$ On a particular day, there are $64$ flights scheduled
between these two cities.

Find the probability that more than $6$ of the flights on this particular
day will have a flight time of more than $80$ minutes.
""")

code(r"""
q2_1 = ...       # P(at least 10 rainy days)
q2_2 = ...       # P(more than 6 late flights)

rain = Bin(31, 0.2)
flights = Bin(64, 0.0711930)

verify_binomial('2.1', q2_1, P(rain >= 10))
verify_binomial('2.2', q2_2, P(flights > 6))
""")

md(r"""
### 2.3 — *May 2025 TZ2 Paper 2 Q10(d), 3 marks*

At Adam's Apple Orchard an apple is *premium* when its weight is between
$170$ and $185$ grams, and $62.8364\ldots\%$ of apples are premium. Boxes
are filled with randomly chosen left-over apples; each box contains $40$
apples.

Find the probability that a randomly chosen box contains at least $30$
premium apples.

### 2.4 — *May 2025 TZ3 Paper 2 Q11(a)(i), 2 marks*

Amanda enters data from surveys into a database; the accuracy of any
survey entered is independent of all others, and she enters $8\%$ of the
surveys inaccurately. On a particular day Amanda enters data from $50$
surveys.

Find the probability that Amanda entered at most six surveys
inaccurately.
""")

code(r"""
q2_3 = ...       # P(at least 30 premium apples in a box of 40)
q2_4 = ...       # P(at most 6 inaccurate out of 50)

box = Bin(40, 0.628364)
surveys = Bin(50, 0.08)

verify_binomial('2.3', q2_3, P(box >= 30))
verify_binomial('2.4', q2_4, P(surveys <= 6))
""")

md(r"""
### 2.5 — *November 2021 Paper 2 Q3(a), 3 marks*

A factory manufactures lamps. It is known that the probability that a
lamp is found to be defective is $0.05$. A random sample of $30$ lamps is
tested.

Find the probability that there is at least one defective lamp in the
sample.
""")

code(r"""
q2_5 = ...       # P(at least one defective lamp)

lamps = Bin(30, 0.05)

verify_binomial('2.5', q2_5, P(lamps >= 1))
""")

# ============================================================ § 3
md(r"""
---
# § 3. Mean and variance

**Three questions, 8 marks.** $np$, $np(1-p)$, $a^2\,\mathrm{Var}(X)$ —
and $p$ worked back from a variance.
""")

md(r"""
### 3.1 — *May 2021 TZ2 Paper 2 Q10(d), 3 marks*

*(The flights of 2.2.)* Find the expected number of flights that will
have a flight time of more than $80$ minutes.
""")

code(r"""
q3_1 = ...       # the expected number of late flights

flights = Bin(64, 0.0711930)

verify_moment('3.1', q3_1, Expect(flights))
""")

md(r"""
### 3.2 — *November 2023 TZ1 Paper 2 Q6(a), 3 marks*

The random variable $X$ is such that $X\sim B(25,\,p)$ and
$\mathrm{Var}(X)=5.75$. Find the possible values of $p$.

### 3.3 — *November 2023 TZ1 Paper 2 Q6(b), 2 marks*

The random variable $Y$ is such that $Y=1-2X$. Find $\mathrm{Var}(Y)$.
""")

code(r"""
q3_2 = [...]     # every possible value of p
q3_3 = ...       # Var(Y)

condition = Eq(Var(Bin(25, p)), 5.75)

verify_parameter('3.2', q3_2, condition, p)
verify_moment('3.3', q3_3, Var(1 - 2 * Bin(25, p)), given=condition, var=p)
""")

# ============================================================ § 4
md(r"""
---
# § 4. A condition inside one distribution

**Three questions, 13 marks.** *Given that…*, with both events about the
same count. The numerator is the overlap of two ranges.
""")

md(r"""
### 4.1 — *November 2021 Paper 2 Q3(b), 4 marks*

*(The lamps of 2.5.)* Given that there is at least one defective lamp in
the sample, find the probability that there are at most two defective
lamps.

### 4.2 — *May 2025 TZ3 Paper 2 Q11(a)(ii), 3 marks*

*(Amanda's $50$ surveys of 2.4.)* Given that at most six surveys were
entered inaccurately, find the probability that exactly four surveys
were entered inaccurately.
""")

code(r"""
q4_1 = ...       # P(at most two defective | at least one defective)
q4_2 = ...       # P(exactly four inaccurate | at most six inaccurate)

lamps = Bin(30, 0.05)
surveys = Bin(50, 0.08)

verify_binomial('4.1', q4_1, P(lamps <= 2, given=lamps >= 1))
verify_binomial('4.2', q4_2, P(surveys == 4, given=surveys <= 6))
""")

md(r"""
### 4.3 — *November 2023 TZ1 Paper 2 Q10(c), 6 marks*

The height of a wheat plant is greater than $98.1$ cm with probability
$0.434$. The farmer measures $100$ randomly selected plants. Any plant
with a height greater than $98.1$ cm is considered ready to harvest.
Heights of plants are independent of each other.

**(i)** Find the probability that exactly $34$ plants are ready to
harvest.
**(ii)** Given that fewer than $49$ plants are ready to harvest, find the
probability that exactly $34$ plants are ready to harvest.

*Write down the probability of the condition as well.*
""")

code(r"""
q4_3i = ...      # P(exactly 34 ready)
q4_3l = ...      # P(fewer than 49 ready)
q4_3 = ...       # P(exactly 34 ready | fewer than 49 ready)

plants = Bin(100, 0.434)

verify_binomial('4.3(i)', q4_3i, P(plants == 34))
verify_binomial('4.3(ii) condition', q4_3l, P(plants < 49))
verify_binomial('4.3(ii)', q4_3, P(plants == 34, given=plants < 49))
""")

# ============================================================ § 5
md(r"""
---
# § 5. Binomial on top of something

**Two questions, 9 marks.** Decide what one trial is, inside and outside.
""")

md(r"""
### 5.1 — *May 2025 TZ2 Paper 2 Q10(e), 2 marks*

*(The boxes of 2.3.)* If $10$ of these boxes are randomly selected, find
the probability that exactly $4$ boxes have at least $30$ premium apples.
""")

code(r"""
q5_1 = ...       # P(exactly 4 of 10 boxes have at least 30 premium apples)

box = Bin(40, 0.628364)
boxes = Bin(10, P(box >= 30))

verify_binomial('5.1', q5_1, P(boxes == 4))
""")

md(r"""
### 5.2 — *May 2022 TZ2 Paper 2 Q8, 7 marks*

Rachel and Sophia are competing in a javelin-throwing competition. The
distances thrown by Rachel are normally distributed with mean $56.5$ m and
standard deviation $3$ m, and those thrown by Sophia with mean $57.5$ m
and standard deviation $1.8$ m; so for one throw

$$P(\text{Rachel}\ge60)=0.1216725\ldots,\qquad P(\text{Sophia}\ge60)=0.0824333\ldots$$

In the first round of competition, each competitor must have five throws.
To qualify for the next round of competition, a competitor must record at
least one throw of $60$ metres or greater in the first round.

Find the probability that only one of Rachel or Sophia qualifies for the
next round of competition.
""")

code(r"""
q5_2r = ...      # P(Rachel qualifies)
q5_2s = ...      # P(Sophia qualifies)
q5_2 = ...       # P(only one of them qualifies)

rachel = Bin(5, 0.1216725, 'R')
sophia = Bin(5, 0.0824333, 'S')

verify_binomial('5.2 Rachel', q5_2r, P(rachel >= 1))
verify_binomial('5.2 Sophia', q5_2s, P(sophia >= 1))
verify_binomial('5.2', q5_2, P((rachel >= 1) ^ (sophia >= 1)))
""")

# ============================================================ § 6
md(r"""
---
# § 6. Unknown $n$

**Three questions, 11 marks.** Logarithms where they work, a table where
they do not, and a whole number at the end either way.
""")

md(r"""
### 6.1 — *May 2024 TZ2 Paper 2 Q5, 5 marks*

Consider a random variable $X$ such that $X\sim B(n,\,0.25)$. Determine
the least value of $n$ such that $P(X\ge1)>0.99$.

### 6.2 — *May 2023 TZ1 Paper 2 Q11(c), 3 marks*

*(The laboratory trials of 1.4, each a success with probability
$0.239358\ldots$)* Determine the least number of trials required to be
$99\%$ sure of at least one success.
""")

code(r"""
q6_1 = ...       # the least n
q6_2 = ...       # the least number of trials

verify_trials('6.1', q6_1, lambda n: P(Bin(n, 0.25) >= 1), holds=lambda value: value > 0.99)
verify_trials('6.2', q6_2, lambda n: P(Bin(n, 0.239358) >= 1),
              holds=lambda value: value >= 0.99)
""")

md(r"""
### 6.3 — *May 2025 TZ3 Paper 2 Q11(b), 3 marks*

On a different day Amanda *(of 2.4)* enters data from $n$ surveys, each
inaccurate with probability $0.08$. On this day, the probability that at
most six surveys were entered inaccurately is approximately $0.367$.

Find the value of $n$.
""")

code(r"""
q6_3 = ...       # n

verify_trials('6.3', q6_3, lambda n: P(Bin(n, 0.08) <= 6), near=0.367)
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

**1.1** $M\sim B(12,\,0.365112\ldots)$, and $P(M=5)=0.213666\ldots=\boxed{0.214}$.
The M1 is for writing the model.

**1.2** $L\sim B(10,\,0.0849303\ldots)$, and $P(L=1)=0.382076\ldots=\boxed{0.382}$.

**1.3** $X\sim B(31,\,0.2)$:
$P(X=10)=\binom{31}{10}(0.2)^{10}(0.8)^{21}=0.0418894\ldots=\boxed{0.0419}$.
Without working, $0.042$ scores (M1)A0.

**1.4** $Y\sim B(10,\,0.239358\ldots)$, and $P(Y=3)=0.242430\ldots=\boxed{0.242}$.

---

**2.1** *At least 10* is everything but $0,\dots,9$:
$P(X\ge10)=1-P(X\le9)=1-0.925400\ldots=\boxed{0.0746}$.
$1-P(X\le10)=0.0327$ is *more than 10*.

**2.2** *More than 6* starts at $7$:
$P(L>6)=1-P(L\le6)=1-0.830880\ldots=\boxed{0.169}$.

**2.3** $A\sim B(40,\,0.628364\ldots)$:
$P(A\ge30)=1-P(A\le29)=0.073861\ldots=\boxed{0.0739}$.

**2.4** $E\sim B(50,\,0.08)$: $P(E\le6)=0.898128\ldots=\boxed{0.898}$.

**2.5** $D\sim B(30,\,0.05)$: $P(D\ge1)=1-0.95^{30}=0.785361\ldots=\boxed{0.785}$.

---

**3.1** $E(L)=np=64\times0.0711930\ldots=4.55635\ldots=\boxed{4.56}$
flights. An expected number is not rounded to a whole one.

**3.2** $25p(1-p)=5.75$, so $25p^2-25p+5.75=0$ and
$p=\tfrac12\pm\tfrac{\sqrt2}{10}$:
$\boxed{p=0.641\ \text{or}\ 0.359}$. A1A1 — both are needed, and they
add to one because $p$ and $1-p$ give the same variance.

**3.3** $\mathrm{Var}(1-2X)=(-2)^2\,\mathrm{Var}(X)=4\times5.75=\boxed{23}$.

---

**4.1** The values in both *at least one* and *at most two* are $1$ and $2$:

$$P(D\le2\mid D\ge1)=\frac{P(D=1)+P(D=2)}{P(D\ge1)}
=\frac{0.597540\ldots}{0.785361\ldots}=\boxed{0.761}$$

Recognition of the conditional must be shown in context, not as a bare
$P(A\mid B)$.

**4.2** *Exactly four* lies inside *at most six*:

$$P(E=4\mid E\le6)=\frac{0.203654\ldots}{0.898128\ldots}=\boxed{0.227}$$

**4.3 (i)** $H\sim B(100,\,0.434)$: $P(H=34)=0.0133198\ldots=\boxed{0.0133}$.

**(ii)** *Fewer than 49* is $H\le48$, and $P(H\le48)=\boxed{0.848}$. Then

$$P(H=34\mid H<49)=\frac{0.0133198\ldots}{0.848218\ldots}=\boxed{0.0157}$$

Using $P(H\le49)=0.890474\ldots$ gives $0.0149581$, and the markscheme
names it: (A0)(M1)(A1)A0.

---

**5.1** A trial is now a box: $Y\sim B(10,\,0.073861\ldots)$ and
$P(Y=4)=0.003944\ldots=\boxed{0.00394}$.

**5.2** Each competitor qualifies with at least one long throw in five:

$$P(N_R\ge1)=1-(1-0.1216725\ldots)^5=\boxed{0.477},\qquad
P(N_S\ge1)=1-(1-0.0824333\ldots)^5=\boxed{0.350}$$

Only one of them:

$$\begin{aligned}&0.477264\ldots\times0.650412\ldots\\
+\ &0.349588\ldots\times0.522736\ldots=\boxed{0.493}\end{aligned}$$

*At least one* would be $0.660$ — the case where both qualify is not
*only one*.

---

**6.1** $1-0.75^{\,n}>0.99$, so $0.75^{\,n}<0.01$ and
$n>\dfrac{\ln0.01}{\ln0.75}=16.0078\ldots$: $\boxed{n=17}$. By table,
$n=16$ gives $0.989977\ldots$ and $n=17$ gives $0.992483\ldots$

**6.2** $1-(0.760641\ldots)^{\,n}\ge0.99$ gives $n\ge16.8321\ldots$:
$\boxed{17}$ trials. By table, $n=16$ gives $0.987443\ldots$ and $n=17$
gives $0.990448\ldots$

**6.3** $P(E\le6)$ for $E\sim B(n,\,0.08)$ falls as $n$ grows: $n=93$
gives $0.378$, $n=94$ gives $0.367$, $n=95$ gives $0.356$.
$\boxed{n=94}$. The markscheme's M1 is for any correct value of
$P(E\le6)$ with $n\ne50$ — the table is the method.
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
