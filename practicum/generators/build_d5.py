"""Собирает практикум D5: нормальное распределение и обратная задача.

Двадцать девятый практикум серии и пятый по статистике. Собран из двух
тем корпуса: нормальная половина statistics.continuous_random_variables
(плотность и медиана — это D6) и два балла statistics.probability из
ноябрьской бумаги 2023 года, где сумма трёх площадей размечена как
вероятность. Почти вся тема на Paper 2: калькулятор здесь нужен честно,
и баллы за метод стоят не на счёте, а на том, какую площадь считать.

Лестница из шести приёмов идёт по тому, что неизвестно. Сначала
площадь при известной модели. Потом площади, которые складываются без
калькулятора: симметрия, дополнение, правило из условия. Потом граница
по площади, одна буква модели, две буквы. Напоследок условие внутри:
условная вероятность, смесь двух кривых и событие, заданное через другую
величину.

Двадцать второе понятие равенства ответов: **вероятность — это площадь**.
Проверка знает только кривую и складывает площадь под ней там, где
событие выполняется; границы, σ и μ она находит сама из условий вопроса
и отбрасывает решения с неположительным σ. Ни функции ошибок, ни
обратной нормальной внутри нет.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_d5.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/statistics/practicum-d5-normal.ipynb')

TRIGGER = {1: 'area', 2: 'boundary', 3: 'sigma', 4: 'symmetry', 5: 'both',
           6: 'condition', 7: 'area', 8: 'sigma', 9: 'condition', 10: 'boundary',
           11: 'symmetry', 12: 'both'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '0.266',
    'q1c': '62.8',
    'q2a': '10',
    'q2b': '0.68',
    'q2c': '0.84',
    'q3a': '2.5',
    'q3b': 'Rational(1, 6)',
    'q4a': '0.115',
    'q4b': '0.0849',
    'q4c': '197',
    'q5m': '27.5',
    'q5s': '6.26',
    'q5b': '8.4',
    'q6': '0.208',
    'q7': '6.43',
    'q8a': '0.278',
    'q8b': '[97.3, 4.82]',
    'q8d': '3.57',
    'q9a': '0.674',
    'q9b': '[175, 7.32]',
    'q10a': '3.41',
    'q10b': '0.0712',
    'q10c': '0.719',
    'q11a': '0.365',
    'q11ci': '0.227',
    'q11cii': '0.965',
    'q11d': '1.47',
    'q12g': '0.317',
    'q12h': '0.167',
    'qt_a': '0.0668',
    'qt_b': '1.28',
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
# D5 — The normal distribution, forwards and backwards

**97 marks of the archive, six techniques, twelve tasks.** Everything the
archive asks about a normally distributed variable, from May 2021 to
November 2025: an area, areas that add up without a calculator, a
boundary found from an area, the mean or the standard deviation found
from one area or two, and a condition inside.

Almost all of it is on Paper 2. The calculator really is needed — and
still does only the last step.

## The one idea

A normal variable has no table. It has a **curve**, and

> **a probability is the area under the curve, above the values where
> the event happens.**

$P(X<a)$ is the area to the left of $a$; $P(a<X<b)$ the area between;
$P(X>b)$ the area to the right. There is no area above a single value,
so $P(X\le a)=P(X<a)$: the markscheme does not care about $<$ against
$\le$, and neither do the checks.

## And the idea that carries the rest

Every harder question is the same area **read backwards**. The
calculator's `normalcdf` goes from a boundary to an area; `invNorm` goes
from an area to a boundary. When the boundary is known and $\sigma$ is
not, the standardised boundary

$$z=\frac{x-\mu}{\sigma}$$

is the bridge: `invNorm` gives $z$, and $x=\mu+z\sigma$ is one equation
for the unknown. Two unknowns need two areas.

## How the checks work

They do not know the answers. Each check is handed **the model and the
facts** the question gives:

```python
T = Normal(75, sigma**2, 'T')
verify_letters('10a', 3.41, sigma, [T], [Eq(P(T > 82), 0.02)])
```

is *"your $\sigma$: does the area to the right of 82 come out as 0.02?"*
The check finds $\sigma$ itself, from the curve alone — no z-tables, no
inverse normal inside — and compares. `Normal(mean, variance)` takes the
**variance**, as IB writes $N(\mu,\sigma^2)$.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| the area on the other side | the opposite event |
| $P(X<185)$ for $P(170<X<185)$ | one boundary is lost |
| $\sigma^2$ typed where $\sigma$ belongs | the second number of $N(\mu,\sigma^2)$ is the variance |
| the height of the curve | a probability is an area, not a height |
| $P(A\cap B)$ for $P(A\mid B)$ | not divided by the condition |
| $\sigma<0$ from the equation | a standard deviation is positive |
| $0.6827$ when two figures are asked | the question asks for 2 significant figures |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the area, and areas that add up without a calculator | 1–3 |
| 🟡 | a boundary from an area; $\sigma$, then $\mu$ and $\sigma$ | 4–9 |
| 🔴 | a condition inside: given, a mixture, an event about another quantity | 10–12 |

Every task is a real past-paper question, cited.

**90 of these 97 marks are on a calculator paper, and the number is
honest.** Nobody integrates $e^{-x^2/2}$ by hand. But the method marks sit
on the sketch and the sentence *"P(W < w) = 1 − 0.8 − 0.115"*, not on the
button.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Normal, Mix, Freq, P(), SD

language('en')                 # this notebook is in English, and so are the checks

# Normal(mean, variance, name) is X ~ N(mean, variance) — the variance, as IB writes it.
# Comparisons are events, P() finds their area; & is "and", | is "or".
#     L = Normal(420, 30**2, 'L')
#     P(L < 400), P((L > 400) & (L < 460)), P(L > 460, given=L > 420)
# Letters are allowed in the model: Normal(m, s**2) — the checks find them.

print('ready; sympy', sp.__version__)
L = Normal(420, 30**2, 'L')
print('the model:              ', L)
print('P(L < 400):             ', sympify(P(L < 400)))
print('P(400 < L < 460):       ', sympify(P((L > 400) & (L < 460))))
""")

md(r"""
---
## Map of the six techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the area | $\mu$ and $\sigma$ given; *find the probability*, *percentage*, *expected number* | `normalcdf` over the right interval |
| 2 | areas that add up | Paper 1; *95 % within two standard deviations*; areas given, one missing | symmetry, total $=1$, the rule in the question |
| 3 | a boundary from an area | *find $w$ such that*, *the top 20 %*, *quartile*, *$k$ standard deviations* | `invNorm` from the area to the **left** |
| 4 | one parameter | $\sigma$ (or $\mu$) unknown, one area given | $z=\frac{x-\mu}{\sigma}$, one equation |
| 5 | two parameters | $\mu$ and $\sigma$ both unknown, two areas given | two $z$ equations, a linear system |
| 6 | a condition inside | *given that*, two kinds mixed, an event about another quantity | a ratio of areas; a sum of weighted areas; an interval of $Z$ |

Technique 1 is the whole topic read forwards. Technique 2 is technique 1
with no calculator: the areas come from symmetry. Techniques 3–5 read it
backwards, and each adds one unknown. Technique 6 puts a second question
around the area.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. The area

## Theory: an area over the right interval

A battery lasts $L$ hours, with $L\sim N(420,\ 30^2)$.

**Draw it first.** A bell centred at $420$, and the region the question
names shaded. Then the calculator:

| question | region | calculator |
|---|---|---|
| lasts less than 400 hours | left of $400$ | `normalcdf(-1E99, 400, 420, 30)` $=0.252$ |
| between 400 and 460 hours | between | `normalcdf(400, 460, 420, 30)` $=0.656$ |
| more than 460 hours | right of $460$ | `normalcdf(460, 1E99, 420, 30)` $=0.0912$ |

The calculator wants the **standard deviation**, $30$ — not the variance
$900$. The model is written $N(\mu,\sigma^2)$, and the second number in
it is squared.

**"More than" and "at least" are the same area.** A single value has no
area, so $P(L\ge460)=P(L>460)$. This is the opposite of D3, where
$X\ge10$ and $X>10$ differed by a whole bar.

**Expected number.** Of $250$ batteries, the expected number lasting more
than $460$ hours is $250\times0.0912\ldots=22.8$. It is a mean, so it need
not be whole — but *"estimate the number"* is also answered with the
whole number $23$.

**A percentage** is the same area times $100$: $9.12\,\%$.

> **Three significant figures, not three decimal places.** $0.0912$ has
> three significant figures; $0.091$ has two, and on Paper 2 that is an
> A0.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ2 Paper 2 Q10(a), (c), 4 marks*

At Adam's Apple Orchard the weights of apples, $W$, in grams, are normally
distributed with a mean $175$ grams and standard deviation $8$ grams.

**(a)** Find the probability that a randomly chosen apple weighs less than
$170$ grams.

All orchards classify an apple as premium when its weight is between $170$
and $185$ grams.

**(c)** Find the percentage of apples that are classified as premium at
Adam's Apple Orchard.

*Part (b) of this question is a boundary, and part (f) has two unknowns —
they are in the archive.*
""")

code(r"""
q1a = ...        # P(W < 170)
q1c = ...        # the percentage of premium apples

W = Normal(175, 8**2, 'W')

verify_chance('1a', q1a, P(W < 170))
verify_chance('1c', q1c, P((W > 170) & (W < 185)), percent=True)
""")

# ================================================================= теория 2
md(r"""
## Theory: areas that add up without a calculator

On Paper 1 there is no `normalcdf`, and the question is built so that you
need none. Three facts do the work.

**Symmetry.** The curve is symmetric about $\mu$: half the area is on
each side, and the area beyond $\mu+d$ equals the area below $\mu-d$.

**The total is one.** If $P(X<a)=0.3$ and $P(X>b)=0.1$, then
$P(a<X<b)=1-0.3-0.1=0.6$ — no model needed at all.

**The rule for whole standard deviations.** For every normal curve,

| within | area |
|---|---|
| $\mu\pm\sigma$ | $\approx0.68$ |
| $\mu\pm2\sigma$ | $\approx0.95$ |
| $\mu\pm3\sigma$ | $\approx0.997$ |

For $X\sim N(50,\ 4^2)$: $62$ is three standard deviations above the
mean, so by symmetry $P(X>62)\approx\frac{1-0.997}2=0.0015$. And an
interval that is not symmetric is two halves: $46$ is one standard
deviation below, $58$ two above, so
$P(46<X<58)\approx\frac{0.68}2+\frac{0.95}2=0.815$.

> **When the question gives the rule, use the question's rule.** *"You may
> assume 95 % lie within two standard deviations"* means $0.95$ exactly,
> even though the curve gives $0.9545$. The markscheme's answer is built
> on the question's number.

**The same number of standard deviations, the same area.** If
$X\sim N(50,\ \sigma^2)$ and $Y\sim N(80,\ \sigma^2)$, then
$P(Y>86)=P(X>b)$ needs $b$ to be as far above $50$ as $86$ is above $80$:
$b=56$, whatever $\sigma$ is. With different $\sigma$ you compare
$\frac{x-\mu}{\sigma}$ instead of $x-\mu$.
""")

md(r"""
### Task 2 🟢 — *May 2025 TZ3 Paper 1 Q5, 6 marks*

The random variables $X$ and $Y$ are normally distributed with
$X\sim N(7,\ a^2)$ and $Y\sim N(19,\ a^2)$, where $a>0$.

**(a)** Find $b$ such that $P(X>b)=P(Y>22)$.

**(b)** Write down the approximate value of $P(7-a<X<7+a)$, correct to two
significant figures.

**(c)** Given that $a=3$, calculate the approximate value of $P(Y<22)$,
correct to two significant figures.

*Paper 1. The checks for (a) and (b) try several values of $a$: your
answer must not depend on it.*
""")

code(r"""
q2a = ...        # b
q2b = ...        # P(7 - a < X < 7 + a), two significant figures
q2c = ...        # P(Y < 22) when a = 3, two significant figures

a, b = symbols('a b')
X = Normal(7, a**2, 'X')
Y = Normal(19, a**2, 'Y')

verify_letters('2a', q2a, b, [X, Y], [Eq(P(X > b), P(Y > 22))], free=a)
verify_chance('2b', q2b, P((X > 7 - a) & (X < 7 + a)), sf=2, free=a)
verify_chance('2c', q2c, P(Normal(19, 3**2, 'Y') < 22), sf=2)
""")

md(r"""
### Task 3 🟢 — *May 2024 TZ2 Paper 1 Q6, 5 marks*

A farmer grows two types of apples — cooking apples and eating apples. The
weights of the apples, in grams, can be modelled as normal distributions
with the following parameters.

| apple type | mean | standard deviation |
|---|---|---|
| eating | $100$ g | $20$ g |
| cooking | $140$ g | $40$ g |

For each type of apple you can assume that $95\,\%$ of the weights are
within two standard deviations of the mean.

**(a)** Find the percentage of eating apples that have a weight greater
than $140$ g.

The farmer grows a large number of apples of which $80\,\%$ are eating
apples. Both types of apples are picked and randomly mixed together in a
cleaning machine. After cleaning, the machine separates out those that
have a weight greater than $140$ g into a container.

**(b)** An apple is randomly selected from this container. Find the
probability that it is an eating apple. Give your answer in the form
$\frac cd$, where $c,d\in\mathbb{Z}^+$.

*`rule={2: 0.95}` is the question's own sentence: the checks take areas
from it, not from the curve. Part (b) is technique 6 on Paper 1 — try it
now, it is fractions; `Mix` is explained in Part 3.*
""")

code(r"""
q3a = ...        # the percentage of eating apples over 140 g
q3b = ...        # P(eating | over 140 g), as Rational(c, d)

eating = Normal(100, 20**2, 'eating', rule={2: 0.95})
cooking = Normal(140, 40**2, 'cooking', rule={2: 0.95})
apple = Mix({eating: 0.8, cooking: 0.2}, 'apple')

verify_chance('3a', q3a, P(eating > 140), percent=True)
verify_chance('3b', q3b, P(apple.came_from(eating), given=apple > 140))
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. Backwards: the boundary, then the parameters

## Theory: a boundary from an area

`invNorm(area, μ, σ)` returns the value with that area **to its left**.
Everything else is translated into that first:

| the question says | area to the left | for $L\sim N(420,\ 30^2)$ |
|---|---|---|
| $10\,\%$ last less than $w$ | $0.1$ | $w=381.6$ |
| $10\,\%$ last more than $w$ | $1-0.1=0.9$ | $w=458.4$ |
| the lower quartile | $0.25$ | $Q_1=399.8$ |
| the upper quartile | $0.75$ | $Q_3=440.2$ |

The quartiles are symmetric about the mean, so the interquartile range is
$Q_3-Q_1=40.5$.

**When the area is not given directly, find it first.** If $70\,\%$ of the
batteries last between $w$ and $460$ hours, the area to the left of $w$
is $1-0.7-P(L>460)=1-0.7-0.0912=0.2088$ — technique 2 — and only then
`invNorm`.

**"$k$ standard deviations above the mean"** is the boundary $\mu+k\sigma$.
For *every* normal curve the area beyond it is the same, so $k$ is read
from $N(0,1)$: the area above $k$ is $0.05$ when $k=1.645$.

> **Four significant figures when asked.** *"Correct to four significant
> figures"* is a separate instruction, and the markscheme writes *must be
> 4 sf*. $181.73$ is not an answer to it.
""")

md(r"""
### Task 4 🟡 — *May 2023 TZ2 Paper 2 Q3(a)–(c), 6 marks*

The weights, $W$ grams, of bags of rice packaged in a factory can be
modelled by a normal distribution with mean $204$ grams and standard
deviation $5$ grams.

**(a)** A bag of rice is selected at random. Find the probability that it
weighs more than $210$ grams.

According to this model, $80\,\%$ of the bags of rice weigh between $w$
grams and $210$ grams.

**(b)** Find the probability that a randomly selected bag of rice weighs
less than $w$ grams.

**(c)** Find the value of $w$.

*The checks for (b) and (c) find $w$ themselves from the 80 % sentence,
so a slip in (a) costs (a) only.*
""")

code(r"""
q4a = ...        # P(W > 210)
q4b = ...        # P(W < w)
q4c = ...        # w

w = symbols('w')
W = Normal(204, 5**2, 'W')
eighty = [Eq(P((W > w) & (W < 210)), 0.8)]

verify_chance('4a', q4a, P(W > 210))
verify_chance('4b', q4b, P(W < w), given=eighty, var=w)
verify_letters('4c', q4c, w, [W], eighty)
""")

md(r"""
### Task 5 🟡 — *November 2025 TZ1 Paper 2 Q5, 5 marks*

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

*The quartile letters in the check are just names: the check finds them
from the model it builds out of the table.*
""")

code(r"""
q5m = ...        # the mean
q5s = ...        # the standard deviation
q5b = ...        # the interquartile range, two significant figures

data = Freq({Interval.Lopen(15, 20): 31, Interval.Lopen(20, 25): 42,
             Interval.Lopen(25, 30): 61, Interval.Lopen(30, 35): 46,
             Interval.Lopen(35, 40): 29}, 'y')
Y = Normal(Expect(data), Var(data), 'Y')
Q1, Q3, R = symbols('Q1 Q3 R')
quartiles = [Eq(P(Y < Q1), 0.25), Eq(P(Y < Q3), 0.75), Eq(R, Q3 - Q1)]

verify_moment('5a(i)', q5m, Expect(data))
verify_moment('5a(ii)', q5s, SD(data))
verify_letters('5b', q5b, R, [Y], quartiles, sf=2)
""")

# ================================================================= теория 4
md(r"""
## Theory: one unknown parameter

When $\sigma$ is unknown, `invNorm` cannot take it as an argument. Go
through $Z\sim N(0,1)$ instead: the same area sits to the left of $z$ on
the standard curve and to the left of $x$ on yours, and

$$z=\frac{x-\mu}{\sigma}\qquad\Longrightarrow\qquad x=\mu+z\sigma$$

**One area, one boundary.** $X\sim N(90,\ \sigma^2)$ and $P(X>100)=0.05$.
The area to the left of $100$ is $0.95$, so $z=1.645$ (from `invNorm(0.95)`),
and

$$\frac{100-90}{\sigma}=1.6449\ \Longrightarrow\ \sigma=6.08$$

**A symmetric interval.** $90\,\%$ lie within $12$ of the mean $60$: the
two tails share $10\,\%$, so $5\,\%$ is above $72$, the area to the left of
$72$ is $0.95$, and $\frac{12}{\sigma}=1.6449$ gives $\sigma=7.30$. Halve
the outside, never the inside.

**An interquartile range.** The quartiles are $\mu\pm0.6745\sigma$ (the
$z$ with area $0.75$ to its left is $0.6745$), so an interquartile range of
$16$ means $2\times0.6745\,\sigma=16$ and $\sigma=11.9$.

> **The calculator can also just solve it.** Graph
> $y=\texttt{normalcdf}(-10^{99},100,90,x)$ against $y=0.95$ and intersect:
> the markscheme accepts that route with a sketch. It is the same equation.

A negative root never survives: a standard deviation is positive.
""")

md(r"""
### Task 6 🟡 — *May 2023 TZ1 Paper 2 Q4, 5 marks*

A company manufactures metal tubes for bicycle frames. The diameters of
the tubes, $D$ mm, are normally distributed with mean $32$ and standard
deviation $s$. The interquartile range of the diameters is $0.28$.

Find the value of $s$.
""")

code(r"""
q6 = ...         # s

s, Q1, Q3 = symbols('s Q1 Q3')
D = Normal(32, s**2, 'D')
spread = [Eq(P(D < Q1), 0.25), Eq(P(D < Q3), 0.75), Eq(Q3 - Q1, 0.28)]

verify_letters('6', q6, s, [D], spread)
""")

md(r"""
### Task 7 🟡 — *May 2025 TZ1 Paper 2 Q4(c), 3 marks*

The heights, $H$ cm, of adults in a group can be modelled by a normal
distribution with mean $163$ cm and standard deviation $s$ cm.

It is found that $88\,\%$ of the group have a height between $153$ cm and
$173$ cm.

**(c)** Find the value of $s$.

*Parts (a) and (b) of this question are about regression lines — that is
D7.*
""")

code(r"""
q7 = ...         # s

s = symbols('s')
H = Normal(163, s**2, 'H')

verify_letters('7', q7, s, [H], [Eq(P((H > 153) & (H < 173)), 0.88)])
""")

# ================================================================= теория 5
md(r"""
## Theory: two unknown parameters

Two areas, two boundaries, two equations. $X\sim N(\mu,\ \sigma^2)$ with
$P(X<30)=0.2$ and $P(X>45)=0.1$:

- the area to the left of $30$ is $0.2$, so $z_1=-0.8416$ and
  $\mu-0.8416\sigma=30$;
- the area to the left of $45$ is $1-0.1=0.9$, so $z_2=1.2816$ and
  $\mu+1.2816\sigma=45$.

Subtract: $2.1232\sigma=15$, so $\sigma=7.06$ and $\mu=35.9$.

> **The equations are in $z$, not in probabilities.** $\mu+0.2\sigma=30$ is
> the most common wrong system, and the markscheme's M1 says *"that involve
> z-values rather than probabilities"*.

**The unknowns can be hidden in the story.** *"The mean is 20 more and
the standard deviation is half as big"* is a second model
$N(\mu+20,\ (\sigma/2)^2)$ with the **same** two letters — each area about
either model is one more equation.

**Areas can be given in relation to each other.** *"Twice as many below
$a$ as above $b$"* and *"80 % between"* are two equations in the two tail
areas: with $x$ below and $2x$ above, $x+0.8+2x=1$. Solve for the areas
first (technique 2), then turn each into a $z$.
""")

md(r"""
### Task 8 🟡 — *November 2023 TZ1 Paper 2 Q10(a), (b), (d), 10 marks*

A farmer is growing a field of wheat plants. The height, $H$ cm, of each
plant can be modelled by a normal distribution with mean $m$ and standard
deviation $s$.

It is known that $P(H<94.6)=0.288$ and $P(H>98.1)=0.434$.

**(a)** Find the probability that the height of a randomly selected plant
is between $94.6$ cm and $98.1$ cm.

**(b)** Find the value of $m$ and the value of $s$.

In another field, the farmer is growing the same variety of wheat, but is
using a different fertilizer. The heights of these plants, $F$ cm, are
normally distributed with mean $98.6$ and standard deviation $d$. The
farmer finds the interquartile range to be $4.82$ cm.

**(d)** Find the value of $d$.

*Part (c) is binomial — it is in D3.*
""")

code(r"""
q8a = ...        # P(94.6 < H < 98.1)
q8b = [...]      # [m, s]
q8d = ...        # d

m, s, d, Q1, Q3 = symbols('m s d Q1 Q3')
H = Normal(m, s**2, 'H')
wheat = [Eq(P(H < 94.6), 0.288), Eq(P(H > 98.1), 0.434)]
F = Normal(98.6, d**2, 'F')
spread = [Eq(P(F < Q1), 0.25), Eq(P(F < Q3), 0.75), Eq(Q3 - Q1, 4.82)]

verify_chance('8a', q8a, P((H > 94.6) & (H < 98.1)), given=wheat, var=[m, s])
verify_letters('8b', q8b, [m, s], [H], wheat)
verify_letters('8d', q8d, d, [F], spread)
""")

md(r"""
### Task 9 🟡 — *November 2025 TZ3 Paper 2 Q4, 7 marks*

A garden centre sells seeds for two varieties of sunflowers: large and
giant.

The heights of large sunflowers are normally distributed with mean $m$ and
standard deviation $s$. It is known that $25\,\%$ of large sunflowers have
a height of over $180$ cm.

**(a)** Given that $m+As=180$, where $A\in\mathbb{R}$, find the value of $A$.

The heights of giant sunflowers are also normally distributed. The giant
sunflowers have a mean height that is $35$ cm more than that of the large
sunflowers and a standard deviation that is double that of the large
sunflowers. It is known that $98\,\%$ of giant sunflowers have a height
greater than $180$ cm.

**(b)** Determine $m$ and $s$.

*In (a) $m$ and $s$ are not known yet, and $A$ does not depend on them: the
check tries several $s$.*
""")

code(r"""
q9a = ...        # A
q9b = [...]      # [m, s]

m, s, A = symbols('m s A')
large = Normal(m, s**2, 'large')
giant = Normal(m + 35, (2*s)**2, 'giant')

verify_letters('9a', q9a, A, [large], [Eq(P(large > 180), 0.25), Eq(m + A*s, 180)], free=s)
verify_letters('9b', q9b, [m, s], [large, giant],
               [Eq(P(large > 180), 0.25), Eq(P(giant > 180), 0.98)])
""")

# ================================================================= теория 6
md(r"""
---
# 🔴 Part 3. A condition inside

## Theory: given, mixed, and an event about another quantity

**Given that.** The condition is the new whole; the event is the part of
it that also happens:

$$P(L>460\mid L>420)=\frac{P(L>460\ \text{and}\ L>420)}{P(L>420)}=\frac{0.0912}{0.5}=0.182$$

Draw both regions. The numerator is the **overlap** — here the event lies
inside the condition, so it is the event itself; when it does not (*"less
than 470, given more than 440"*), the numerator is the area between 440 and
470.

**Two kinds mixed.** $70\,\%$ of batteries are type A, $L\sim N(420,\ 30^2)$,
and $30\,\%$ type B, $N(380,\ 25^2)$. A battery picked at random lasts less
than $400$ hours with probability

$$0.7\times0.2525+0.3\times0.7881=0.413$$

— a tree with a normal area on each branch. Backwards (Bayes), the chance
that a battery under $400$ hours is type A is $\frac{0.7\times0.2525}{0.413}=0.428$.
In a check, `Mix({A: 0.7, B: 0.3}, 'battery')` is that tree, and
`battery.came_from(A)` is the branch.

**An event about another quantity.** $Z\sim N(0,1)$ and the equation
$x^2-2Zx+4=0$. Translate every statement into an interval of $Z$:

- real roots: $4Z^2-16\ge0$, so $Z\le-2$ or $Z\ge2$, with probability
  $0.0455$;
- the larger root $Z+\sqrt{Z^2-4}$ is less than $5$: this needs $Z<5$ and
  $Z^2-4<(5-Z)^2$, that is $Z<2.9$ — so, together with real roots,
  $Z\le-2$ or $2\le Z<2.9$.

Squaring an inequality is only safe when both sides are non-negative —
check that, or you add an interval that does not belong.
""")

md(r"""
### Task 10 🔴 — *May 2021 TZ2 Paper 2 Q10(a)–(c), 9 marks*

The flight times, $T$ minutes, between two cities can be modelled by a
normal distribution with a mean of $75$ minutes and a standard deviation of
$\sigma$ minutes.

**(a)** Given that $2\,\%$ of the flight times are longer than $82$ minutes,
find the value of $\sigma$.

**(b)** Find the probability that a randomly selected flight will have a
flight time of more than $80$ minutes.

**(c)** Given that a flight between the two cities takes longer than $80$
minutes, find the probability that it takes less than $82$ minutes.

*Parts (d) and (e) are binomial — D3. The checks for (b) and (c) find
$\sigma$ themselves.*
""")

code(r"""
q10a = ...       # sigma
q10b = ...       # P(T > 80)
q10c = ...       # P(T < 82 | T > 80)

sigma = symbols('sigma')
T = Normal(75, sigma**2, 'T')
two_percent = [Eq(P(T > 82), 0.02)]

verify_letters('10a', q10a, sigma, [T], two_percent)
verify_chance('10b', q10b, P(T > 80), given=two_percent, var=sigma)
verify_chance('10c', q10c, P(T < 82, given=T > 80), given=two_percent, var=sigma)
""")

md(r"""
### Task 11 🔴 — *May 2022 TZ1 Paper 2 Q11(a), (c), (d), 14 marks*

A bakery makes two types of muffins: chocolate muffins and banana muffins.

The weights, $C$ grams, of the chocolate muffins are normally distributed
with a mean of $62$ g and standard deviation of $2.9$ g.

**(a)** Find the probability that a randomly selected chocolate muffin
weighs less than $61$ g.

The weights, $B$ grams, of the banana muffins are normally distributed
with a mean of $68$ g and standard deviation of $3.4$ g.

Each day $60\,\%$ of the muffins made are chocolate. On a particular day, a
muffin is randomly selected from all those made at the bakery.

**(c)** **(i)** Find the probability that the randomly selected muffin
weighs less than $61$ g. **(ii)** Given that a randomly selected muffin
weighs less than $61$ g, find the probability that it is chocolate.

The machine that makes the chocolate muffins is adjusted so that the mean
weight of the chocolate muffins remains the same but their standard
deviation changes to $\sigma$ g. The machine that makes the banana muffins
is not adjusted. The probability that the weight of a randomly selected
muffin from these machines is less than $61$ g is now $0.157$.

**(d)** Find the value of $\sigma$.

*Part (b) is binomial — D3.*
""")

code(r"""
q11a = ...       # P(C < 61)
q11ci = ...      # P(muffin < 61)
q11cii = ...     # P(chocolate | muffin < 61)
q11d = ...       # sigma

C = Normal(62, 2.9**2, 'C')
B = Normal(68, 3.4**2, 'B')
muffin = Mix({C: 0.6, B: 0.4}, 'muffin')

sigma = symbols('sigma')
adjusted = Normal(62, sigma**2, 'C')
now = Mix({adjusted: 0.6, B: 0.4}, 'muffin')

verify_chance('11a', q11a, P(C < 61))
verify_chance('11c(i)', q11ci, P(muffin < 61))
verify_chance('11c(ii)', q11cii, P(muffin.came_from(C), given=muffin < 61))
verify_letters('11d', q11d, sigma, [adjusted], [Eq(P(now < 61), 0.157)])
""")

md(r"""
### Task 12 🔴 — *May 2024 TZ2 Paper 3 Q2(g)–(h), 10 marks*

In parts (g) and (h), consider a randomly generated quadratic function,
$f(x)=x^2+2Zx+1$, where the continuous random variable $Z\sim N(0,1)$.

**(g)** Find the probability that the graph of $f$ has two $x$-intercepts.

The continuous random variables, $X_1$ and $X_2$, represent the
$x$-intercepts of the graph of $f$ where $X_1=-Z-\sqrt{Z^2-1}$ and
$X_2=-Z+\sqrt{Z^2-1}$.

**(h)** Given that the graph of $f$ has two $x$-intercepts, $X_1$ and $X_2$,
find the probability that both $X_1$ and $X_2$ are greater than $0.5$.

*The check does not know the intervals of $Z$. It walks along the axis,
works out $X_1$ and $X_2$ at each $Z$, and finds where the event starts
and stops. Two distinct intercepts is `X1 < X2`: when $Z^2<1$ there are
none, and at $Z^2=1$ they coincide.*
""")

code(r"""
q12g = ...       # P(two x-intercepts)
q12h = ...       # P(both > 0.5 | two x-intercepts)

Z = Normal(0, 1, 'Z')
X1 = Z.map(lambda z: -z - sqrt(z**2 - 1), 'X1')
X2 = Z.map(lambda z: -z + sqrt(z**2 - 1), 'X2')
two = X1 < X2

verify_chance('12g', q12g, P(two))
verify_chance('12h', q12h, P((X1 > 0.5) & (X2 > 0.5), given=two))
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `area` | the model is known: find an area |
| `symmetry` | no calculator: symmetry, total one, the whole-$\sigma$ rule |
| `boundary` | the model is known: find the boundary from an area |
| `sigma` | one parameter unknown, one area given |
| `both` | the mean and the standard deviation both unknown |
| `condition` | given that, two kinds mixed, or an event about another quantity |

1. Rods have lengths $N(150,\ 0.4^2)$ cm. Find the probability that a rod is longer than $150.5$ cm.
2. Marks in a test are $N(62,\ 9^2)$; the top $5\,\%$ get a distinction. Find the lowest mark for a distinction.
3. Bottles are filled with a mean of $500$ ml, and $3\,\%$ contain less than $495$ ml. Find the standard deviation.
4. $X\sim N(20,\ 3^2)$ and $P(X<17)\approx0.16$. Without a calculator, write down $P(17<X<23)$.
5. $10\,\%$ of parcels weigh less than $2$ kg and $25\,\%$ weigh more than $5$ kg. Find the mean and the standard deviation.
6. Race times are $N(48,\ 5^2)$ minutes. Given that a runner finishes in under $50$ minutes, find the probability that they finish in under $45$.
7. Egg weights are $N(60,\ 4^2)$ g. Estimate how many of $300$ eggs weigh between $55$ and $65$ g.
8. A normal distribution has mean $12$ and interquartile range $3$. Find $\sigma$.
9. $30\,\%$ of a shop's bananas come from a farm with weights $N(120,\ 10^2)$ g, the rest from a farm with $N(130,\ 12^2)$ g. Find the probability that a banana weighs more than $125$ g.
10. Find the upper quartile of $N(80,\ 6^2)$.
11. $X\sim N(\mu,\ \sigma^2)$ and $Y\sim N(\mu+10,\ \sigma^2)$. Find $c$ such that $P(X<c)=P(Y<25)$, in terms of $\mu$ — without a calculator.
12. $P(X<40)=0.3$ and $P(X<55)=0.8$ for a normal $X$. Find its mean.
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
## On the clock — *May 2024 TZ1 Paper 2 Q3, 4 marks*

**Four marks, five minutes.** Calculator allowed, no hints.

The random variable $X$ is normally distributed with mean $10$ and
standard deviation $2$.

**(a)** Find the probability that $X$ is more than $1.5$ standard deviations
above the mean.

The probability that $X$ is more than $k$ standard deviations above the
mean is $0.1$, where $k\in\mathbb{R}$.

**(b)** Find the value of $k$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_a = ...       # P(X more than 1.5 standard deviations above the mean)
qt_b = ...       # k

k = symbols('k')
X = Normal(10, 2**2, 'X')

verify_chance('timer (a)', qt_a, P(X > 10 + 1.5*2))
verify_letters('timer (b)', qt_b, k, [X], [Eq(P(X > 10 + k*2), 0.1)])
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** The region left of $170$:
$P(W<170)=\texttt{normalcdf}(-10^{99},170,175,8)=0.265985\ldots=\boxed{0.266}$

**1 (c)** $P(170<W<185)=0.628364\ldots$, so $\boxed{62.8\,\%}$.

The markscheme accepts $26.6\,\%$ in (a) as well; a probability is still
the better form there.

---

**2 (a)** $22$ is $3$ above the mean of $Y$, and both curves have the same
standard deviation $a$: the same area lies above $7+3$. $\boxed{b=10}$.
The markscheme's line is $\frac{b-7}a=\frac{22-19}a$.

**2 (b)** $\mu\pm\sigma$ holds about $68\,\%$: $\boxed{0.68}$.

**2 (c)** With $a=3$, $22=19+3$ is one standard deviation above the mean.
Above it lies $\frac{1-0.68}2=0.16$, so

$$P(Y<22)\approx1-0.16=\boxed{0.84}$$

---

**3 (a)** $140=100+2\times20$. Outside $\mu\pm2\sigma$ is $5\,\%$, split equally:
$\boxed{2.5\,\%}$ above.

**3 (b)** For cooking apples $140$ **is** the mean, so half of them are
over $140$. The container holds

$$0.8\times0.025+0.2\times0.5=0.02+0.1=0.12$$

of all apples, and the eating ones among them are $0.02$:

$$P(\text{eating}\mid>140)=\frac{0.02}{0.12}=\boxed{\tfrac16}$$

---

**4 (a)** $P(W>210)=0.115069\ldots=\boxed{0.115}$

**4 (b)** Below $w$, between, above $210$ make up the whole:

$$P(W<w)=1-0.8-0.115069\ldots=0.0849302\ldots=\boxed{0.0849}$$

**4 (c)** $w=\texttt{invNorm}(0.0849302\ldots,204,5)=197.136\ldots=\boxed{197}$

---

**5 (a)** Mid-interval values $17.5,\ 22.5,\ 27.5,\ 32.5,\ 37.5$ with the
frequencies, $\sum f=209$: mean $\boxed{27.5}$, standard deviation
$6.26374\ldots=\boxed{6.26}$ (the calculator's $\sigma_x$, which divides by
$n$; $s_x=6.28$ divides by $n-1$).

**5 (b)** With $Y\sim N(27.5,\ 6.26374\ldots^2)$: $Q_1=\texttt{invNorm}(0.25)=23.2751\ldots$
and $Q_3=\texttt{invNorm}(0.75)=31.7248\ldots$, so

$$\text{IQR}=8.44965\ldots=\boxed{8.4}$$

---

**6** Half the interquartile range each side of the mean:
$Q_3=32+0.14=32.14$, with area $0.75$ to its left. So $z=0.674489\ldots$ and

$$\frac{32.14-32}{s}=0.674489\ldots\ \Longrightarrow\ s=0.207564\ldots=\boxed{0.208}\ \text{mm}$$

---

**7** The interval is $163\pm10$, symmetric: $6\,\%$ below $153$ and $6\,\%$
above $173$. The area to the left of $173$ is $0.94$, $z=1.55477\ldots$, and

$$\frac{10}{s}=1.55477\ldots\ \Longrightarrow\ s=6.43181\ldots=\boxed{6.43}$$

---

**8 (a)** $P(94.6<H<98.1)=1-0.288-0.434=\boxed{0.278}$

**8 (b)** Areas to the left: $0.288$ below $94.6$, and $1-0.434=0.566$ below
$98.1$. So $z_1=-0.559236\ldots$, $z_2=0.166199\ldots$:

$$m-0.559236\ldots s=94.6,\qquad m+0.166199\ldots s=98.1$$

Subtracting, $0.725436\ldots s=3.5$: $s=4.82468\ldots$, $m=97.2981\ldots$
$\boxed{m=97.3,\ s=4.82}$

**8 (d)** $Q_3=98.6+2.41=101.01$ has area $0.75$ to its left:
$\frac{2.41}d=0.674489\ldots$, so $d=3.57307\ldots=\boxed{3.57}$.

---

**9 (a)** $25\,\%$ above $180$ is $75\,\%$ below: $z=0.674489\ldots$, and
$180=m+0.674489\ldots s$ — which is $m+As=180$ with $\boxed{A=0.674}$.

**9 (b)** Giant: $N(m+35,\ (2s)^2)$. $98\,\%$ above $180$ is $2\,\%$ below, so
$z=-2.05374\ldots$:

$$\frac{180-(m+35)}{2s}=-2.05374\ldots\ \Longrightarrow\ m-4.10749\ldots s=145$$

With $m+0.674489\ldots s=180$: $4.78198\ldots s=35$, so $s=7.31913\ldots$ and
$m=175.063\ldots$ $\boxed{m=175,\ s=7.32}$

---

**10 (a)** $2\,\%$ above $82$ is $98\,\%$ below: $z=2.05374\ldots$, and

$$\frac{82-75}\sigma=2.05374\ldots\ \Longrightarrow\ \sigma=3.40840\ldots=\boxed{3.41}$$

**10 (b)** $P(T>80)=0.0711929\ldots=\boxed{0.0712}$

**10 (c)** The overlap of *"less than 82"* and *"more than 80"* is between
80 and 82:

$$P(T<82\mid T>80)=\frac{P(80<T<82)}{P(T>80)}=\frac{0.0511929\ldots}{0.0711929\ldots}=0.719073\ldots=\boxed{0.719}$$

---

**11 (a)** $P(C<61)=0.365111\ldots=\boxed{0.365}$

**11 (c)(i)** $P(B<61)=0.0197555\ldots$, and on the tree

$$0.6\times0.365111\ldots+0.4\times0.0197555\ldots=0.226969\ldots=\boxed{0.227}$$

**11 (c)(ii)** $\dfrac{0.6\times0.365111\ldots}{0.226969\ldots}=0.965183\ldots=\boxed{0.965}$

The markscheme wants the recognition *in context* — *"P(chocolate | weight
< 61)"* — not just $P(A\mid B)$.

**11 (d)** The tree again, with the new chocolate area unknown:

$$0.6\,P(C<61)+0.4\times0.0197555\ldots=0.157\ \Longrightarrow\ P(C<61)=0.248496\ldots$$

Then $z=-0.679229\ldots$ and $\frac{61-62}\sigma=-0.679229\ldots$:
$\sigma=1.47225\ldots=\boxed{1.47}$ g.

---

**12 (g)** Two intercepts when the discriminant is positive:
$4Z^2-4>0$, so $Z<-1$ or $Z>1$:

$$P(|Z|>1)=1-0.682689\ldots=0.317310\ldots=\boxed{0.317}$$

**12 (h)** $X_2>X_1$, so both exceed $0.5$ when $X_1>0.5$:
$-Z-\sqrt{Z^2-1}>0.5$ means $\sqrt{Z^2-1}<-Z-0.5$. The right side must be
positive, so $Z<-0.5$ — with two intercepts, $Z<-1$ — and squaring,
$Z^2-1<Z^2+Z+0.25$, so $Z>-1.25$. The event is $-1.25<Z<-1$:

$$\frac{P(-1.25<Z<-1)}{P(|Z|>1)}=\frac{0.0530054\ldots}{0.317310\ldots}=0.167046\ldots=\boxed{0.167}$$

The markscheme gives separate marks for $-1.25$ and for the inequality;
$-1.25<Z$ alone loses the last of them.

---

## Timer

**(a)** $10+1.5\times2=13$: $P(X>13)=0.0668072\ldots=\boxed{0.0668}$

**(b)** The area above $k$ standard deviations is the same on every normal
curve: $P(Z>k)=0.1$, so $k=\texttt{invNorm}(0.9)=1.28155\ldots=\boxed{1.28}$.
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
