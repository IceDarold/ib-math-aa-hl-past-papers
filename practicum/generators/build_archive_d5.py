"""Собирает архивный ноутбук D5: вся тема нормального распределения подряд.

Семнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3 и D4. Практикум учит: лестница из приёмов, теория
перед каждым, три уровня сложности, тренажёр распознавания, задание на
время. Архив не учит. Он даёт набивать руку: **вся тема подряд, по тем же
шести приёмам, без единой строчки теории**. Двадцать восемь вопросов,
97 баллов — всё, что архив спрашивает про нормальную величину, с мая 2021
по ноябрь 2025.

Разметка взята из карточки statistics-normal.yaml: поле blocks у каждого
приёма. Ноябрьский дубль 2023 года входит один раз, копией TZ1.

Части одного вопроса разнесены по своим приёмам сильнее, чем в D4: май
2025 TZ2 Q10 стоит в § 1 пунктами (a) и (c), в § 3 пунктом (b) и в § 5
пунктом (f); ноябрь 2023 Q10 — в §§ 2, 4 и 5. Условие каждого пункта
повторено целиком, насколько оно нужно пункту, — включая предложения,
из которых проверка находит σ, если пункт сам его не ищет.

Хешей нет ни одного: всякий ответ темы — площадь, граница или буква
модели, и всякий проверяется самой кривой.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_d5.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/archive-d5-normal.ipynb')

ANSWERS = {
    # § 1. The area
    'q1_1a': '0.0766',
    'q1_1b': '7.66',
    'q1_2': '0.0712',
    'q1_3': '0.365',
    'q1_4': '0.574',
    'q1_5': '0.115',
    'q1_6': '0.0668',
    'q1_7a': '0.266',
    'q1_7c': '62.8',
    # § 2. Areas that add up
    'q2_1': '0.278',
    'q2_2': '0.0849',
    'q2_3': '2.5',
    'q2_4a': '10',
    'q2_4b': '0.68',
    'q2_4c': '0.84',
    # § 3. A boundary from an area
    'q3_1': '197',
    'q3_2': '181.7',
    'q3_3': '1.28',
    'q3_4': '0.674',
    'q3_5m': '27.5',
    'q3_5s': '6.26',
    'q3_5b': '8.4',
    'q3_6': '22.2',
    # § 4. One parameter
    'q4_1': '3.41',
    'q4_2': '0.208',
    'q4_3': '3.57',
    'q4_4': '6.43',
    'q4_5': '1.47',
    # § 5. Two parameters
    'q5_1': '[97.3, 4.82]',
    'q5_2': '176',
    'q5_3': '[175, 7.32]',
    # § 6. A condition inside
    'q6_1': '0.0829',
    'q6_2': '0.719',
    'q6_3g': '0.317',
    'q6_3h': '0.167',
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
# D5 archive — the normal distribution, all of it

**Twenty-eight questions, 97 marks.** Every question the archive asks
about a normally distributed variable, from May 2021 to November 2025, in
the order of the six techniques rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-d5-normal.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The area | 7 | 17 |
| 2 | Areas that add up | 4 | 11 |
| 3 | A boundary from an area | 6 | 18 |
| 4 | One parameter | 5 | 19 |
| 5 | Two parameters | 3 | 15 |
| 6 | A condition inside | 3 | 17 |

The checks are the same ones the practicum uses and they store nothing:
each is handed the model and the facts of the question, finds the area
under the curve itself, and finds any unknown boundary, $\sigma$ or $\mu$
itself. `Normal(mean, variance)` takes the **variance**, as IB writes
$N(\mu,\sigma^2)$. Three significant figures, unless the question asks
for two or four.

**Parts of one question are split by technique.** May 2025 TZ2 Q10 appears
in §§ 1, 3 and 5; each part repeats what it needs. When a part uses a
$\sigma$ found in an earlier part, the check finds that $\sigma$ from the
question's own sentence, so an earlier slip does not follow you.

**The November 2023 paper appears once**, although the archive holds it
twice as TZ1 and TZ2.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Normal, Mix, Freq, P(), SD

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. The area

**Seven questions, 17 marks.** The model is known: shade the region, then
the area.
""")

md(r"""
### 1.1 — *May 2021 TZ1 Paper 2 Q2(a)–(b), 3 marks*

A company produces bags of sugar whose masses, in grams, can be modelled
by a normal distribution with mean $1000$ and standard deviation $3.5$. A
bag of sugar is rejected for sale if its mass is less than $995$ grams.

**(a)** Find the probability that a bag selected at random is rejected.

**(b)** Estimate the number of bags which will be rejected from a random
sample of $100$ bags.
""")

code(r"""
q1_1a = ...      # P(rejected)
q1_1b = ...      # the estimated number rejected out of 100

sugar = Normal(1000, 3.5**2, 'X')

verify_chance('1.1(a)', q1_1a, P(sugar < 995))
verify_moment('1.1(b)', q1_1b, Expect(Bin(100, P(sugar < 995))), count=True)
""")

md(r"""
### 1.2 — *May 2021 TZ2 Paper 2 Q10(b), 2 marks*

The flight times, $T$ minutes, between two cities can be modelled by a
normal distribution with a mean of $75$ minutes and a standard deviation of
$\sigma$ minutes, and $2\,\%$ of the flight times are longer than $82$
minutes. Part (a) finds $\sigma$ — it is question 4.1 below.

**(b)** Find the probability that a randomly selected flight will have a
flight time of more than $80$ minutes.
""")

code(r"""
q1_2 = ...       # P(T > 80)

sigma = symbols('sigma')
T = Normal(75, sigma**2, 'T')

verify_chance('1.2', q1_2, P(T > 80), given=[Eq(P(T > 82), 0.02)], var=sigma)
""")

md(r"""
### 1.3 — *May 2022 TZ1 Paper 2 Q11(a), 2 marks*

The weights, $C$ grams, of the chocolate muffins made by a bakery are
normally distributed with a mean of $62$ g and standard deviation of
$2.9$ g.

**(a)** Find the probability that a randomly selected chocolate muffin
weighs less than $61$ g.

### 1.4 — *November 2022 Paper 2 Q10(a), 2 marks*

The time worked, $T$, in hours per week by employees of a large company is
normally distributed with a mean of $42$ and standard deviation $10.7$.

**(a)** Find the probability that an employee selected at random works more
than $40$ hours per week.
""")

code(r"""
q1_3 = ...       # P(C < 61)
q1_4 = ...       # P(T > 40)

verify_chance('1.3', q1_3, P(Normal(62, 2.9**2, 'C') < 61))
verify_chance('1.4', q1_4, P(Normal(42, 10.7**2, 'T') > 40))
""")

md(r"""
### 1.5 — *May 2023 TZ2 Paper 2 Q3(a), 2 marks*

The weights, $W$ grams, of bags of rice packaged in a factory can be
modelled by a normal distribution with mean $204$ grams and standard
deviation $5$ grams.

**(a)** A bag of rice is selected at random. Find the probability that it
weighs more than $210$ grams.

### 1.6 — *May 2024 TZ1 Paper 2 Q3(a), 2 marks*

The random variable $X$ is normally distributed with mean $10$ and
standard deviation $2$.

**(a)** Find the probability that $X$ is more than $1.5$ standard deviations
above the mean.
""")

code(r"""
q1_5 = ...       # P(W > 210)
q1_6 = ...       # P(X more than 1.5 standard deviations above the mean)

X = Normal(10, 2**2, 'X')

verify_chance('1.5', q1_5, P(Normal(204, 5**2, 'W') > 210))
verify_chance('1.6', q1_6, P(X > 10 + 1.5*2))
""")

md(r"""
### 1.7 — *May 2025 TZ2 Paper 2 Q10(a), (c), 4 marks*

At Adam's Apple Orchard the weights of apples, $W$, in grams, are normally
distributed with a mean $175$ grams and standard deviation $8$ grams.

**(a)** Find the probability that a randomly chosen apple weighs less than
$170$ grams.

All orchards classify an apple as premium when its weight is between $170$
and $185$ grams.

**(c)** Find the percentage of apples that are classified as premium at
Adam's Apple Orchard.
""")

code(r"""
q1_7a = ...      # P(W < 170)
q1_7c = ...      # the percentage of premium apples

W = Normal(175, 8**2, 'W')

verify_chance('1.7(a)', q1_7a, P(W < 170))
verify_chance('1.7(c)', q1_7c, P((W > 170) & (W < 185)), percent=True)
""")

# ============================================================ § 2
md(r"""
---
# § 2. Areas that add up

**Four questions, 11 marks.** Symmetry, the total of one, and the rule for
whole standard deviations — seven of these marks are on Paper 1.
""")

md(r"""
### 2.1 — *November 2023 TZ1 Paper 2 Q10(a), 2 marks*

The height, $H$ cm, of each wheat plant can be modelled by a normal
distribution with mean $m$ and standard deviation $s$. It is known that
$P(H<94.6)=0.288$ and $P(H>98.1)=0.434$.

**(a)** Find the probability that the height of a randomly selected plant
is between $94.6$ cm and $98.1$ cm.

### 2.2 — *May 2023 TZ2 Paper 2 Q3(b), 2 marks*

The weights, $W$ grams, of bags of rice can be modelled by a normal
distribution with mean $204$ grams and standard deviation $5$ grams.
According to this model, $80\,\%$ of the bags of rice weigh between $w$
grams and $210$ grams.

**(b)** Find the probability that a randomly selected bag of rice weighs
less than $w$ grams.
""")

code(r"""
q2_1 = ...       # P(94.6 < H < 98.1)
q2_2 = ...       # P(W < w)

m, s, w = symbols('m s w')
H = Normal(m, s**2, 'H')
wheat = [Eq(P(H < 94.6), 0.288), Eq(P(H > 98.1), 0.434)]
W = Normal(204, 5**2, 'W')

verify_chance('2.1', q2_1, P((H > 94.6) & (H < 98.1)), given=wheat, var=[m, s])
verify_chance('2.2', q2_2, P(W < w), given=[Eq(P((W > w) & (W < 210)), 0.8)], var=w)
""")

md(r"""
### 2.3 — *May 2024 TZ2 Paper 1 Q6(a), 1 mark*

The weights of eating apples, in grams, can be modelled as a normal
distribution with mean $100$ g and standard deviation $20$ g. You can assume
that $95\,\%$ of the weights are within two standard deviations of the mean.

**(a)** Find the percentage of eating apples that have a weight greater
than $140$ g.

### 2.4 — *May 2025 TZ3 Paper 1 Q5, 6 marks*

The random variables $X$ and $Y$ are normally distributed with
$X\sim N(7,\ a^2)$ and $Y\sim N(19,\ a^2)$, where $a>0$.

**(a)** Find $b$ such that $P(X>b)=P(Y>22)$.

**(b)** Write down the approximate value of $P(7-a<X<7+a)$, correct to two
significant figures.

**(c)** Given that $a=3$, calculate the approximate value of $P(Y<22)$,
correct to two significant figures.
""")

code(r"""
q2_3 = ...       # the percentage over 140 g
q2_4a = ...      # b
q2_4b = ...      # P(7 - a < X < 7 + a), two significant figures
q2_4c = ...      # P(Y < 22) when a = 3, two significant figures

a, b = symbols('a b')
X = Normal(7, a**2, 'X')
Y = Normal(19, a**2, 'Y')

verify_chance('2.3', q2_3, P(Normal(100, 20**2, 'E', rule={2: 0.95}) > 140), percent=True)
verify_letters('2.4(a)', q2_4a, b, [X, Y], [Eq(P(X > b), P(Y > 22))], free=a)
verify_chance('2.4(b)', q2_4b, P((X > 7 - a) & (X < 7 + a)), sf=2, free=a)
verify_chance('2.4(c)', q2_4c, P(Normal(19, 3**2, 'Y') < 22), sf=2)
""")

# ============================================================ § 3
md(r"""
---
# § 3. A boundary from an area

**Six questions, 18 marks.** Translate into the area to the left, then
`invNorm`.
""")

md(r"""
### 3.1 — *May 2023 TZ2 Paper 2 Q3(c), 2 marks*

The weights, $W$ grams, of bags of rice can be modelled by a normal
distribution with mean $204$ grams and standard deviation $5$ grams, and
$80\,\%$ of the bags weigh between $w$ grams and $210$ grams.

**(c)** Find the value of $w$.

### 3.2 — *May 2025 TZ2 Paper 2 Q10(b), 2 marks*

The weights of apples, $W$, in grams, are normally distributed with a mean
$175$ grams and standard deviation $8$ grams.

**(b)** It is found that $20\,\%$ of the apples weigh more than $w$ grams.
Find $w$, correct to four significant figures.

### 3.3 — *May 2024 TZ1 Paper 2 Q3(b), 2 marks*

The random variable $X$ is normally distributed with mean $10$ and standard
deviation $2$. The probability that $X$ is more than $k$ standard deviations
above the mean is $0.1$, where $k\in\mathbb{R}$.

**(b)** Find the value of $k$.
""")

code(r"""
q3_1 = ...       # w for the rice
q3_2 = ...       # w for the apples, four significant figures
q3_3 = ...       # k

w, k = symbols('w k')
rice = Normal(204, 5**2, 'W')
apples = Normal(175, 8**2, 'W')
X = Normal(10, 2**2, 'X')

verify_letters('3.1', q3_1, w, [rice], [Eq(P((rice > w) & (rice < 210)), 0.8)])
verify_letters('3.2', q3_2, w, [apples], [Eq(P(apples > w), 0.2)], sf=4)
verify_letters('3.3', q3_3, k, [X], [Eq(P(X > 10 + k*2), 0.1)])
""")

md(r"""
### 3.4 — *November 2025 TZ3 Paper 2 Q4(a), 3 marks*

The heights of large sunflowers are normally distributed with mean $m$ and
standard deviation $s$. It is known that $25\,\%$ of large sunflowers have a
height of over $180$ cm.

**(a)** Given that $m+As=180$, where $A\in\mathbb{R}$, find the value of $A$.
""")

code(r"""
q3_4 = ...       # A

m, s, A = symbols('m s A')
large = Normal(m, s**2, 'large')

verify_letters('3.4', q3_4, A, [large], [Eq(P(large > 180), 0.25), Eq(m + A*s, 180)], free=s)
""")

md(r"""
### 3.5 — *November 2025 TZ1 Paper 2 Q5, 5 marks*

Consider the following grouped data set.

| class | frequency |
|---|---|
| $15<y\le20$ | $31$ |
| $20<y\le25$ | $42$ |
| $25<y\le30$ | $61$ |
| $30<y\le35$ | $46$ |
| $35<y\le40$ | $29$ |

**(a)** Find an estimate for **(i)** the mean; **(ii)** the standard
deviation.

The data can be approximated by a normal distribution.

**(b)** Use this information and your mean and standard deviation found in
part (a) to find an approximate value for the interquartile range correct
to two significant figures.
""")

code(r"""
q3_5m = ...      # the mean
q3_5s = ...      # the standard deviation
q3_5b = ...      # the interquartile range, two significant figures

data = Freq({Interval.Lopen(15, 20): 31, Interval.Lopen(20, 25): 42,
             Interval.Lopen(25, 30): 61, Interval.Lopen(30, 35): 46,
             Interval.Lopen(35, 40): 29}, 'y')
Y = Normal(Expect(data), Var(data), 'Y')
Q1, Q3, R = symbols('Q1 Q3 R')

verify_moment('3.5(a)(i)', q3_5m, Expect(data))
verify_moment('3.5(a)(ii)', q3_5s, SD(data))
verify_letters('3.5(b)', q3_5b, R, [Y], [Eq(P(Y < Q1), 0.25), Eq(P(Y < Q3), 0.75), Eq(R, Q3 - Q1)], sf=2)
""")

md(r"""
### 3.6 — *November 2022 Paper 2 Q10(d), 4 marks*

The time worked, $T$, in hours per week by employees of a large company is
normally distributed with a mean of $42$ and standard deviation $10.7$.

It is known that $P(a\le T\le b)=0.904$ and that $P(T>b)=2P(T<a)$, where $a$
and $b$ are numbers of hours worked per week. An employee who works fewer
than $a$ hours per week is considered to be a part-time employee.

**(d)** Find the maximum time, in hours per week, that an employee can work
and still be considered part-time.
""")

code(r"""
q3_6 = ...       # a

a, b = symbols('a b')
T = Normal(42, 10.7**2, 'T')

verify_letters('3.6', q3_6, a, [T], [Eq(P((T >= a) & (T <= b)), 0.904), Eq(P(T > b), 2*P(T < a))])
""")

# ============================================================ § 4
md(r"""
---
# § 4. One parameter

**Five questions, 19 marks.** One letter in the model, one area: through
$z=\frac{x-\mu}\sigma$.
""")

md(r"""
### 4.1 — *May 2021 TZ2 Paper 2 Q10(a), 3 marks*

The flight times, $T$ minutes, between two cities can be modelled by a
normal distribution with a mean of $75$ minutes and a standard deviation of
$\sigma$ minutes.

**(a)** Given that $2\,\%$ of the flight times are longer than $82$ minutes,
find the value of $\sigma$.

### 4.2 — *May 2023 TZ1 Paper 2 Q4, 5 marks*

A company manufactures metal tubes for bicycle frames. The diameters of
the tubes, $D$ mm, are normally distributed with mean $32$ and standard
deviation $s$. The interquartile range of the diameters is $0.28$.

Find the value of $s$.
""")

code(r"""
q4_1 = ...       # sigma
q4_2 = ...       # s

sigma, s, Q1, Q3 = symbols('sigma s Q1 Q3')
T = Normal(75, sigma**2, 'T')
D = Normal(32, s**2, 'D')

verify_letters('4.1', q4_1, sigma, [T], [Eq(P(T > 82), 0.02)])
verify_letters('4.2', q4_2, s, [D], [Eq(P(D < Q1), 0.25), Eq(P(D < Q3), 0.75), Eq(Q3 - Q1, 0.28)])
""")

md(r"""
### 4.3 — *November 2023 TZ1 Paper 2 Q10(d), 3 marks*

In another field, the farmer is growing the same variety of wheat, but is
using a different fertilizer. The heights of these plants, $F$ cm, are
normally distributed with mean $98.6$ and standard deviation $d$. The farmer
finds the interquartile range to be $4.82$ cm.

**(d)** Find the value of $d$.

### 4.4 — *May 2025 TZ1 Paper 2 Q4(c), 3 marks*

The heights, $H$ cm, of adults in a group can be modelled by a normal
distribution with mean $163$ cm and standard deviation $s$ cm. It is found
that $88\,\%$ of the group have a height between $153$ cm and $173$ cm.

**(c)** Find the value of $s$.
""")

code(r"""
q4_3 = ...       # d
q4_4 = ...       # s

d, s, Q1, Q3 = symbols('d s Q1 Q3')
F = Normal(98.6, d**2, 'F')
H = Normal(163, s**2, 'H')

verify_letters('4.3', q4_3, d, [F], [Eq(P(F < Q1), 0.25), Eq(P(F < Q3), 0.75), Eq(Q3 - Q1, 4.82)])
verify_letters('4.4', q4_4, s, [H], [Eq(P((H > 153) & (H < 173)), 0.88)])
""")

md(r"""
### 4.5 — *May 2022 TZ1 Paper 2 Q11(d), 5 marks*

A bakery makes two types of muffins. The weights of the banana muffins are
normally distributed with a mean of $68$ g and standard deviation of $3.4$ g.
Each day $60\,\%$ of the muffins made are chocolate.

The machine that makes the chocolate muffins is adjusted so that the mean
weight of the chocolate muffins is $62$ g but their standard deviation
changes to $\sigma$ g. The machine that makes the banana muffins is not
adjusted. The probability that the weight of a randomly selected muffin
from these machines is less than $61$ g is now $0.157$.

**(d)** Find the value of $\sigma$.
""")

code(r"""
q4_5 = ...       # sigma

sigma = symbols('sigma')
chocolate = Normal(62, sigma**2, 'C')
banana = Normal(68, 3.4**2, 'B')
muffin = Mix({chocolate: 0.6, banana: 0.4}, 'muffin')

verify_letters('4.5', q4_5, sigma, [chocolate], [Eq(P(muffin < 61), 0.157)])
""")

# ============================================================ § 5
md(r"""
---
# § 5. Two parameters

**Three questions, 15 marks.** Two areas, two $z$-values, two linear
equations.
""")

md(r"""
### 5.1 — *November 2023 TZ1 Paper 2 Q10(b), 5 marks*

The height, $H$ cm, of each wheat plant can be modelled by a normal
distribution with mean $m$ and standard deviation $s$. It is known that
$P(H<94.6)=0.288$ and $P(H>98.1)=0.434$.

**(b)** Find the value of $m$ and the value of $s$.

### 5.2 — *May 2025 TZ2 Paper 2 Q10(f), 6 marks*

An apple is classified as premium when its weight is between $170$ and
$185$ grams. At a neighbouring orchard the weights of apples, $M$, in grams,
are normally distributed with mean $m$ and standard deviation $s$. It is
known that:

- $82\,\%$ of their apples are classified as premium;
- the percentage of apples that weigh less than $170$ grams is twice the
  percentage of apples that weigh more than $185$ grams.

**(f)** Find the value of $m$.
""")

code(r"""
q5_1 = [...]     # [m, s]
q5_2 = ...       # m

m, s = symbols('m s')
H = Normal(m, s**2, 'H')
M = Normal(m, s**2, 'M')

verify_letters('5.1', q5_1, [m, s], [H], [Eq(P(H < 94.6), 0.288), Eq(P(H > 98.1), 0.434)])
verify_letters('5.2', q5_2, m, [M], [Eq(P((M > 170) & (M < 185)), 0.82), Eq(P(M < 170), 2*P(M > 185))])
""")

md(r"""
### 5.3 — *November 2025 TZ3 Paper 2 Q4(b), 4 marks*

The heights of large sunflowers are normally distributed with mean $m$ and
standard deviation $s$, and $25\,\%$ of large sunflowers have a height of
over $180$ cm.

The giant sunflowers have a mean height that is $35$ cm more than that of
the large sunflowers and a standard deviation that is double that of the
large sunflowers. Their heights are also normally distributed, and $98\,\%$
of giant sunflowers have a height greater than $180$ cm.

**(b)** Determine $m$ and $s$.
""")

code(r"""
q5_3 = [...]     # [m, s]

m, s = symbols('m s')
large = Normal(m, s**2, 'large')
giant = Normal(m + 35, (2*s)**2, 'giant')

verify_letters('5.3', q5_3, [m, s], [large, giant], [Eq(P(large > 180), 0.25), Eq(P(giant > 180), 0.98)])
""")

# ============================================================ § 6
md(r"""
---
# § 6. A condition inside

**Three questions, 17 marks.** A ratio of areas, and an event about another
quantity turned into an interval of $Z$.
""")

md(r"""
### 6.1 — *May 2021 TZ1 Paper 2 Q2(c), 3 marks*

The masses of bags of sugar, in grams, can be modelled by a normal
distribution with mean $1000$ and standard deviation $3.5$. A bag is
rejected for sale if its mass is less than $995$ grams.

**(c)** Given that a bag is not rejected, find the probability that it has
a mass greater than $1005$ grams.

### 6.2 — *May 2021 TZ2 Paper 2 Q10(c), 4 marks*

The flight times, $T$ minutes, between two cities can be modelled by a
normal distribution with a mean of $75$ minutes and a standard deviation of
$\sigma$ minutes, and $2\,\%$ of the flight times are longer than $82$ minutes.

**(c)** Given that a flight between the two cities takes longer than $80$
minutes, find the probability that it takes less than $82$ minutes.
""")

code(r"""
q6_1 = ...       # P(X > 1005 | not rejected)
q6_2 = ...       # P(T < 82 | T > 80)

sugar = Normal(1000, 3.5**2, 'X')
sigma = symbols('sigma')
T = Normal(75, sigma**2, 'T')

verify_chance('6.1', q6_1, P(sugar > 1005, given=sugar >= 995))
verify_chance('6.2', q6_2, P(T < 82, given=T > 80), given=[Eq(P(T > 82), 0.02)], var=sigma)
""")

md(r"""
### 6.3 — *May 2024 TZ2 Paper 3 Q2(g)–(h), 10 marks*

Consider a randomly generated quadratic function, $f(x)=x^2+2Zx+1$, where
the continuous random variable $Z\sim N(0,1)$.

**(g)** Find the probability that the graph of $f$ has two $x$-intercepts.

The continuous random variables, $X_1$ and $X_2$, represent the
$x$-intercepts of the graph of $f$ where $X_1=-Z-\sqrt{Z^2-1}$ and
$X_2=-Z+\sqrt{Z^2-1}$.

**(h)** Given that the graph of $f$ has two $x$-intercepts, $X_1$ and $X_2$,
find the probability that both $X_1$ and $X_2$ are greater than $0.5$.
""")

code(r"""
q6_3g = ...      # P(two x-intercepts)
q6_3h = ...      # P(both > 0.5 | two x-intercepts)

Z = Normal(0, 1, 'Z')
X1 = Z.map(lambda z: -z - sqrt(z**2 - 1), 'X1')
X2 = Z.map(lambda z: -z + sqrt(z**2 - 1), 'X2')

verify_chance('6.3(g)', q6_3g, P(X1 < X2))
verify_chance('6.3(h)', q6_3h, P((X1 > 0.5) & (X2 > 0.5), given=X1 < X2))
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

**1.1** $P(X<995)=0.0765637\ldots=\boxed{0.0766}$; $100\times0.0766=\boxed{7.66}$,
and the markscheme accepts $8$ bags.

**1.2** $\sigma=\frac7{2.05374\ldots}=3.40840\ldots$, and $P(T>80)=\boxed{0.0712}$.

**1.3** $P(C<61)=0.365111\ldots=\boxed{0.365}$.

**1.4** $P(T>40)=0.574136\ldots=\boxed{0.574}$.

**1.5** $P(W>210)=0.115069\ldots=\boxed{0.115}$.

**1.6** $10+1.5\times2=13$: $P(X>13)=0.0668072\ldots=\boxed{0.0668}$.

**1.7** $P(W<170)=\boxed{0.266}$; $P(170<W<185)=0.628364\ldots$, $\boxed{62.8\,\%}$.

---

**2.1** $1-0.288-0.434=\boxed{0.278}$.

**2.2** $1-0.8-0.115069\ldots=\boxed{0.0849}$.

**2.3** $140=\mu+2\sigma$; outside $\mu\pm2\sigma$ is $5\,\%$, half of it above: $\boxed{2.5\,\%}$.

**2.4** (a) $22$ is $3$ above $19$, so $b=7+3=\boxed{10}$. (b) $\boxed{0.68}$.
(c) $22=19+3$ is one standard deviation up: $1-\frac{0.32}2=\boxed{0.84}$.

---

**3.1** $w=\texttt{invNorm}(0.0849302\ldots,204,5)=197.136\ldots=\boxed{197}$.

**3.2** Area to the left $0.8$: $w=181.732\ldots=\boxed{181.7}$.

**3.3** $P(Z>k)=0.1$: $k=\texttt{invNorm}(0.9)=\boxed{1.28}$.

**3.4** $P(Z<A)=0.75$: $A=\boxed{0.674}$.

**3.5** Mid-interval values, $\sum f=209$: mean $\boxed{27.5}$, $\sigma=6.26374\ldots=\boxed{6.26}$.
Quartiles of $N(27.5,\ 6.26374^2)$: $23.2751\ldots$ and $31.7248\ldots$, IQR $8.44965\ldots=\boxed{8.4}$.

**3.6** With $P(T<a)=x$: $x+0.904+2x=1$, $x=0.032$, and
$a=\texttt{invNorm}(0.032,42,10.7)=22.1816\ldots=\boxed{22.2}$ (the markscheme also accepts $22.1$).

---

**4.1** $\frac{82-75}\sigma=2.05374\ldots$: $\sigma=3.40840\ldots=\boxed{3.41}$.

**4.2** $Q_3=32.14$: $\frac{0.14}s=0.674489\ldots$, $s=0.207564\ldots=\boxed{0.208}$.

**4.3** $Q_3=101.01$: $\frac{2.41}d=0.674489\ldots$, $d=3.57307\ldots=\boxed{3.57}$.

**4.4** $6\,\%$ above $173$: $\frac{10}s=1.55477\ldots$, $s=6.43181\ldots=\boxed{6.43}$.

**4.5** $0.6\,P(C<61)+0.4\times0.0197555\ldots=0.157$ gives $P(C<61)=0.248496\ldots$;
$z=-0.679229\ldots$, $\frac{61-62}\sigma=z$, $\sigma=1.47225\ldots=\boxed{1.47}$.

---

**5.1** $m-0.559236\ldots s=94.6$ and $m+0.166199\ldots s=98.1$:
$\boxed{m=97.3,\ s=4.82}$.

**5.2** Outside the premium range is $18\,\%$, split two to one:
with $P(M>185)=x$, $2x+0.82+x=1$, so $P(M<170)=0.12$ and $P(M>185)=0.06$. $z=-1.17498\ldots$ and $1.55477\ldots$:
$m-1.17498\ldots s=170$, $m+1.55477\ldots s=185$, so $s=5.49498\ldots$ and
$m=176.456\ldots=\boxed{176}$.

**5.3** $m+0.674489\ldots s=180$ and $\frac{180-(m+35)}{2s}=-2.05374\ldots$:
$s=7.31913\ldots$, $m=175.063\ldots$, $\boxed{m=175,\ s=7.32}$.

---

**6.1** $\frac{P(X>1005)}{P(X\ge995)}=\frac{0.0765637\ldots}{0.923436\ldots}=\boxed{0.0829}$.

**6.2** $\frac{P(80<T<82)}{P(T>80)}=\frac{0.0511929\ldots}{0.0711929\ldots}=\boxed{0.719}$.

**6.3** (g) $4Z^2-4>0$: $P(|Z|>1)=\boxed{0.317}$. (h) $X_1>0.5$ needs $Z<-1$ and
$Z>-1.25$: $\frac{0.0530054\ldots}{0.317310\ldots}=\boxed{0.167}$.
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
