"""Собирает практикум D6: непрерывная величина с плотностью.

Тридцатый практикум серии и шестой по статистике. Собран из трёх тем
корпуса: вторая половина statistics.continuous_random_variables — всё,
где у величины не нормальная кривая, а плотность формулой (нормальная
половина — D5), десять баллов statistics.expected_value, где среднее
берут интегралом, и четырнадцать баллов statistics.probability: условные
вероятности под плотностью и доля времени в синусоидальной модели.

Лестница из шести приёмов идёт по тому, что делают с плотностью.
Сначала площадь над промежутком. Потом буква, которую даёт вся площадь,
равная единице. Потом граница по доле площади — медиана и квартиль, —
и мода, которая не площадь, а вершина. Напоследок интегралы от x·f и
x²·f и второй вопрос вокруг площади: условная вероятность и промежуток
μ ± σ из найденных моментов.

Двадцать третье понятие равенства ответов: **всё — интеграл одной
плотности**. Проверка знает только формулу по кускам; вероятность,
медиану, моду, среднее и дисперсию она получает из неё сама, буквы
плотности находит из того, что площадь под ней — единица, и отбрасывает
решения, при которых плотность где-то отрицательна.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_d6.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/statistics/practicum-d6-density.ipynb')

TRIGGER = {1: 'constant', 2: 'area', 3: 'quantile', 4: 'mode', 5: 'moments',
           6: 'condition', 7: 'area', 8: 'constant', 9: 'quantile', 10: 'moments',
           11: 'mode', 12: 'condition'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1e': '0.406',
    'q2a': '3*sqrt(3)/pi',
    'q3a': '1/sqrt(k) - 1/sqrt(16 + k)',
    'q3b': '0.645',
    'q4a': '1/(b*exp(b) - exp(b) + 1)',
    'q4b': '0.768',
    'q5a': '7*k**3/6',
    'q5b': '1.03',
    'q6a': '0.360',
    'q6b': '0.125',
    'q7': 'a + sqrt((b - a)*(c - a)/2)',
    'q8ai': 'Rational(3, 7)',
    'q8aii': '4.5',
    'q8aiii': "'median'",
    'q8b': '0.104',
    'q8d': '4.01',
    'q9a': '2*a',
    'q9b': 'a**2/3',
    'q10ci': '0.456',
    'q10cii': '0.0290',
    'q10d': '0.620',
    'q11d': '0.635',
    'q11e': '40.96',
    'q12a': '324*a + 72*b',
    'q12bii': '[Rational(-1, 108), Rational(1, 18)]',
    'q12c_mode': '7',
    'q12c_median': '6.69',
    'q12d': '0.261',
    'qt_a': '12*(2 - sqrt(3))/pi',
    'qt_b': '0.239',
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
# D6 — Continuous random variables: the density does everything

**114 marks of the archive, six techniques, twelve tasks.** Everything the
archive asks about a random variable given by a probability density
function, from May 2021 to November 2025: an area, the constant that makes
the whole area one, the median and the quartiles, the mode, the mean and
the variance, and a second question around an area.

Almost all of it is on Paper 2 — and a quarter of that is algebra the
calculator never touches: *show that* from $\int f=1$, formulas in $n$,
an exact $\mathrm E(X)$.

## The one idea

A continuous random variable has no table. It has a **density** $f$, zero
outside the interval the question gives, and

> **a probability is the area under $f$, above the values where the event
> happens.**

$$P(a<X<b)=\int_a^b f(x)\,\mathrm dx$$

A single value has no area, so $P(X\le a)=P(X<a)$.

## And what follows from it

Every other question is the same area, used differently:

| the question asks | what it is |
|---|---|
| the constant $k$ | the whole area is $1$ |
| the median, a quartile | the boundary with $\frac12$, $\frac14$ of the area to its left |
| the mode | where $f$ is **highest** — not an area at all |
| $\mathrm E(X)$, $\mathrm{Var}(X)$ | the areas under $x\,f(x)$ and $x^2f(x)$ |

## How the checks work

They do not know the answers. Each check is handed **the density** and
the facts the question gives:

```python
X = Density({(0, 4): x/sqrt((x**2 + k)**3)}, 'X')
verify_letters('3b', 0.645, k, [X])
```

is *"your $k$: is the area under $f$ one?"* — the check adds $\int f=1$
by itself, finds $k$, and compares. `Density({interval: formula})` is the
density exactly as the question prints it, *"0 otherwise"* included.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| the area on the other side | the opposite event |
| $\int_0^m$ when $f$ starts at $0.5$ | the formula does not apply left of $0.5$ |
| a root outside the interval | that root is rejected |
| $\mathrm E(X^2)$ for the variance | the square of the mean is not subtracted |
| $f(1.5)=0.441$ for the mode | the mode is the $x$, not the height |
| $1.65$ on Paper 1 | the question asks for the exact value |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the area, and the constant that makes it one | 1–3 |
| 🟡 | the median and quartiles, the mode | 4–8 |
| 🔴 | the mean and the variance; a second question around an area | 9–12 |

Every task is a real past-paper question, cited.

**95 of these 114 marks are on a calculator paper, and the number
flatters.** 29 of the 95 are algebra: *show that*, $\mathrm E(X)$ in terms
of $n$, an exact value. The calculator really works on the other 66 — an
integral nobody does by hand, a median equation with $\arccos$ in it.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Density, P(), Expect, Var, SD

language('en')                 # this notebook is in English, and so are the checks

# Density({interval: formula}, name) is f, and 0 outside the intervals.
# Comparisons are events, P() finds their area; & is "and", | is "or".
#     X = Density({(0, 2): 3*x**2/8}, 'X')
#     P(X < 1.5), P((X > 0.5) & (X < 1.5)), P(X > 1.5, given=X > 1)
# Expect(X), Var(X), SD(X) are integrals. Letters are allowed: the checks find them.

print('ready; sympy', sp.__version__)
X = Density({(0, 2): 3*x**2/8}, 'X')
print('the model:      ', X)
print('P(X < 1.5):     ', sympify(P(X < 1.5)))
print('E(X):           ', sympify(Expect(X)))
""")

md(r"""
---
## Map of the six techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the area | $f$ fully known; *find the probability*, *at most \$48*, *a random time* | $\int f$ over the right interval |
| 2 | the constant | $k$, $a$, $b$ in $f$ and nothing else said; *show that $324a+72b=1$* | $\int f=1$ over the whole interval |
| 3 | the median, a quartile | *find the median*, *the lower quartile*, *$P(\lvert X-m\rvert\le a)=0.3$* | $\int_{\text{start}}^m f=\frac12$ |
| 4 | the mode | *find the mode*, *which is greater, the mode or the median* | the maximum of $f$ |
| 5 | the mean and the variance | $\mathrm E(X)$, $\mathrm{Var}(X)$, *the expected amount spent* | $\int x f$, $\int x^2 f-\mu^2$ |
| 6 | a second question | *given that*, *$P(\mu-\sigma<X<\mu+\sigma)$* | a ratio of areas; moments first |

Technique 1 is the whole topic read forwards. Techniques 2 and 3 read it
backwards: the area is known, a letter is not. Technique 4 is the one place
where the answer is not an area. Techniques 5 and 6 integrate something
else, or put a question around the area.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. The area, and the constant that makes it one

## Theory: an area under a formula

Take $f(x)=\frac38x^2$ for $0\le x\le2$, and $0$ otherwise.

**Draw it first,** and shade what the question names. Then integrate
over the shaded interval — and only where $f$ is given:

$$P(X<1.5)=\int_0^{1.5}\tfrac38x^2\,\mathrm dx=\Big[\tfrac18x^3\Big]_0^{1.5}=\tfrac{27}{64}=0.422$$

$P(X<3)$ is $1$, not $\frac{27}{8}$: beyond $2$ the density is zero, and the
formula no longer applies.

**On a calculator paper** the integral is `fnInt`; the method mark is for
writing $\int_0^{1.5}f(x)\,\mathrm dx$ with the right limits.

**A piecewise density** is integrated piece by piece: the area up to a
point on the second piece is the whole first piece plus part of the
second.

**An event about another quantity** is translated into an interval of
$X$ first. Postage on a parcel of $X$ kg is \$4 per kg below $1.5$ kg and
\$3 per kg from $1.5$ kg. *"Postage at most \$5"* is $4X\le5$ on the
first rate, so $X\le1.25$; **and** $3X\le5$ on the second, so
$1.5\le X\le\frac53$. Two intervals — and $X\le\frac54$ alone loses the
second.

**A random time** is the simplest density of all: a moment chosen at
random in the first $T$ seconds has $f(t)=\frac1T$, and the probability of
anything is the fraction of the time it holds.
""")

md(r"""
### Task 1 🟢 — *May 2023 TZ2 Paper 2 Q10(e), 4 marks*

A weight suspended on a spring is pulled down and released, so that it
moves up and down vertically.

The height, $H$ metres, of the base of the weight above the ground can be
modelled by the function $H(t)=a\cos(7.8t)+b$, for $a,b\in\mathbb R$ and
$0\le t\le10$, where $t$ is the time in seconds after the weight is
released.

The weight is released when its base is at a minimum height of $1$ metre
above the ground, and it reaches a maximum height of $1.8$ metres above the
ground. In part (b) this gives $a=-0.4$ and $b=1.4$.

A camera is set to take a picture of the weight at a random time during the
first five seconds of its motion.

**(e)** Find the probability that the height of the base of the weight is
greater than $1.5$ metres at the time the picture is taken.

*Parts (a)–(d) are a sinusoidal model — C4. The check does not know
where $H>1.5$: it walks along $[0,5]$ and finds where it starts and
stops.*
""")

code(r"""
q1e = ...        # P(H > 1.5) at a random time in the first five seconds

T = Density({(0, 5): Rational(1, 5)}, 'T', var=t)
H = T.map(lambda s: -0.4*cos(7.8*s) + 1.4, 'H')

verify_chance('1e', q1e, P(H > 1.5))
""")

# ================================================================= теория 2
md(r"""
## Theory: the whole area is one

A density with a letter in it has exactly one fact about the letter
that the question need not state: **the area under $f$ is one.**

$f(x)=k(4-x^2)$ for $0\le x\le2$:

$$\int_0^2k(4-x^2)\,\mathrm dx=k\Big[4x-\tfrac13x^3\Big]_0^2=\tfrac{16}3k=1\quad\Longrightarrow\quad k=\tfrac3{16}$$

**Write "$=1$".** The markscheme gives a method mark for it, and a
*show that* without it collapses: the working proves nothing.

**The integral is the work.** Substitution for $\frac{x}{(x^2+c)^{3/2}}$
or $\frac{c}{\sqrt{1-x^2}}$ ($\arcsin$ appears), parts for $x\,e^{x}$,
piece by piece when the density is piecewise — and then the limits,
which may themselves be letters: for $f(x)=cx$ on $[0,c]$ the area is
$\frac{c^3}2$.

**Two letters need two facts.** $f(x)=px+q$ on $[0,2]$ with $f(2)=0$:
the area gives $2p+2q=1$, the value gives $2p+q=0$, so $q=1$ and
$p=-\frac12$. One equation for two letters has infinitely many answers.

> **Paper 1 wants the exact value.** $\frac{3}{16}$, $\frac{2}{\pi}$ —
> not $0.1875$, not $0.637$.
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ1 Paper 1 Q7(a), 4 marks*

The continuous random variable $X$ has probability density function

$$f(x)=\begin{cases}\dfrac{k}{\sqrt{4-3x^2}}, & 0\le x\le1\\[4pt] 0, & \text{otherwise.}\end{cases}$$

**(a)** Find the value of $k$.

*Paper 1: the exact value. Part (b), $\mathrm E(X)$, is in the archive.*
""")

code(r"""
q2a = ...        # k, exact

k = symbols('k', positive=True)
X = Density({(0, 1): k/sqrt(4 - 3*x**2)}, 'X')

verify_letters('2a', q2a, k, [X], exact=True)
""")

md(r"""
### Task 3 🟢 — *May 2021 TZ1 Paper 2 Q7, 7 marks*

A continuous random variable $X$ has the probability density function $f$
given by

$$f(x)=\begin{cases}\dfrac{x}{\sqrt{(x^2+k)^3}}, & 0\le x\le4\\[4pt] 0, & \text{otherwise}\end{cases}$$

where $k\in\mathbb R^+$.

**(a)** Show that $\sqrt{16+k}-\sqrt k=\sqrt k\,\sqrt{16+k}$.

**(b)** Find the value of $k$.

*For (a) enter the area under $f$ as an expression in $k$ — the line just
before you set it equal to $1$. The check tries several $k$.*
""")

code(r"""
k = symbols('k', positive=True)

q3a = ...        # the area under f, in terms of k
q3b = ...        # k

X = Density({(0, 4): x/sqrt((x**2 + k)**3)}, 'X')

verify_chance('3a', q3a, total_probability(X), free=k)
verify_letters('3b', q3b, k, [X])
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. The median, the quartiles, the mode

## Theory: a boundary from a share of the area

The median $m$ has half the area to its left; the lower quartile a
quarter; the upper quartile three quarters.

$$\int_{\text{start}}^{m}f(x)\,\mathrm dx=\frac12$$

For $f(x)=\frac38x^2$ on $[0,2]$: $\frac18m^3=\frac12$, so $m=\sqrt[3]4=1.59$;
the lower quartile is $\sqrt[3]2=1.26$.

**The lower limit is where $f$ starts.** If $f$ lives on $[0.8,3]$, the
median equation starts at $0.8$ — integrating the formula from $0$ adds
an area that is not there.

**Piecewise: find the piece first.** $f(x)=\frac x2$ on $[0,1]$ and
$f(x)=\frac12$ on $[1,2.5]$. The first piece holds $\frac14$ — less than a
half, so the median is on the second piece:

$$\tfrac14+\tfrac12(m-1)=\tfrac12\quad\Longrightarrow\quad m=1.5$$

Using the first formula everywhere, $\frac{m^2}4=\frac12$, gives $\sqrt2$ —
a number, but not the median.

**Keep only the root on its piece.** A quadratic median equation has two
roots, and one of them lies outside the interval: the markscheme gives a
mark for rejecting it.

**Around the median.** $P(\lvert X-m\rvert\le d)$ is the area from $m-d$ to
$m+d$ — one more equation, now for $d$.
""")

md(r"""
### Task 4 🟡 — *November 2022 Paper 2 Q6, 8 marks*

The continuous random variable $X$ has a probability density function
given by

$$f(x)=\begin{cases}axe^x, & 0\le x\le b\\ 0, & \text{otherwise}\end{cases}$$

where $a,b\in\mathbb R^+$.

**(a)** Find an expression for $a$ in terms of $b$.

**(b)** In the case where $a=b=1$, find the median of $X$.

*In (a) the answer contains $b$: the check tries several $b$.*
""")

code(r"""
a, b = symbols('a b', positive=True)
m = symbols('m')

q4a = ...        # a in terms of b
q4b = ...        # the median when a = b = 1

X = Density({(0, b): a*x*exp(x)}, 'X')
X1 = Density({(0, 1): x*exp(x)}, 'X')

verify_letters('4a', q4a, a, [X], free=b)
verify_letters('4b', q4b, m, [X1], [Eq(P(X1 < m), 0.5)])
""")

md(r"""
### Task 5 🟡 — *May 2024 TZ1 Paper 2 Q8, 6 marks*

A continuous random variable $X$ has a probability density function $f$
given by

$$f(x)=\begin{cases}kx, & 0\le x\le k\\ 2kx-x^2, & k<x\le2k\\ 0, & \text{otherwise}\end{cases}$$

where $k>0$.

**(a)** Show that $k$ satisfies the equation $7k^3=6$.

**(b)** Find the median of $X$.

*For (a) enter the area under $f$ in terms of $k$. In (b) the check finds
$k$ itself from the area being one.*
""")

code(r"""
k = symbols('k', positive=True)
m = symbols('m')

q5a = ...        # the area under f, in terms of k
q5b = ...        # the median

X = Density({(0, k): k*x, (k, 2*k): 2*k*x - x**2}, 'X')

verify_chance('5a', q5a, total_probability(X), free=k)
verify_letters('5b', q5b, m, [X], [Eq(P(X < m), 0.5)])
""")

md(r"""
### Task 6 🟡 — *November 2021 Paper 2 Q7, 6 marks*

A continuous random variable $X$ has a probability density function given
by

$$f(x)=\begin{cases}\arccos x, & 0\le x\le1\\ 0, & \text{otherwise}\end{cases}$$

The median of this distribution is $m$.

**(a)** Determine the value of $m$.

**(b)** Given that $P(\lvert X-m\rvert\le a)=0.3$, determine the value of $a$.

*The check for (b) finds $m$ itself, so a slip in (a) costs (a) only.*
""")

code(r"""
q6a = ...        # m
q6b = ...        # a

m = symbols('m')
a = symbols('a', positive=True)
X = Density({(0, 1): acos(x)}, 'X')
median = Eq(P(X < m), 0.5)

verify_letters('6a', q6a, m, [X], [median])
verify_letters('6b', q6b, a, [X], [median, Eq(P((X >= m - a) & (X <= m + a)), 0.3)])
""")

md(r"""
### Task 7 🟡 — *May 2022 TZ2 Paper 1 Q8, 6 marks*

A continuous random variable $X$ has the probability density function

$$f(x)=\begin{cases}\dfrac{2}{(b-a)(c-a)}(x-a), & a\le x\le c\\[6pt] \dfrac{2}{(b-a)(b-c)}(b-x), & c<x\le b\\[6pt] 0, & \text{otherwise}\end{cases}$$

The graph of $y=f(x)$ for $a\le x\le b$ is a triangle: it rises from $0$
at $x=a$ to its peak at $x=c$ and falls back to $0$ at $x=b$.

Given that $c\ge\frac{a+b}2$, find an expression for the median of $X$ in
terms of $a$, $b$ and $c$.

*Paper 1. The check tries several triangles with $c\ge\frac{a+b}2$ and
compares your expression with the median of each.*
""")

code(r"""
a, b, c, m = symbols('a b c m')

q7 = ...         # the median in terms of a, b, c

X = Density({(a, c): 2*(x - a)/((b - a)*(c - a)),
             (c, b): 2*(b - x)/((b - a)*(b - c))}, 'X')
triangles = [{a: 0, b: 4, c: 3}, {a: 1, b: 3, c: Rational(5, 2)}, {a: -2, b: 6, c: 5}]

verify_letters('7', q7, m, [X], [Eq(P(X < m), 0.5)], free=triangles)
""")

# ================================================================= теория 4
md(r"""
## Theory: the mode is a peak, not an area

The mode is the value of $x$ where $f$ is **largest**. Find it from the
graph, from $f'(x)=0$, or from the axis of symmetry of a parabola — and
remember the ends of the interval.

- $f(x)=\frac38x^2$ on $[0,2]$ increases: the mode is at the end, $x=2$.
- $f(x)=12x^2(1-x)$ on $[0,1]$: $f'(x)=24x-36x^2=0$ at $x=\frac23$.

**The answer is the $x$.** $f(\frac23)=\frac{16}9$ is the height of the
peak, and the markscheme gives no accuracy mark for it.

**Mode against median — without the median.** Compute the area to the
left of the mode. For $12x^2(1-x)$ it is $4x^3-3x^4$ at $\frac23$, which is
$\frac{16}{27}>\frac12$: half the area is reached **before** the mode, so
the median is less than the mode. That one inequality is the reason the
markscheme's R1 asks for.
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ1 Paper 2 Q11(a), (b), (d), 9 marks*

In a marathon race, the random variable $T$ represents the time, in hours,
taken for a runner to complete the race. No runner completes the race in
less than $2.25$ hours, and no runner completes it in more than $7.5$
hours.

The probability density function for $T$ is modelled by $f$, defined by

$$f(t)=\begin{cases}\frac4{21}\left(1-\cos\left(\frac{4\pi}9(t-2.25)\right)\right), & 2.25\le t<4.5\\[4pt] \frac4{21}\left(1+\cos\left(\frac\pi3(t-4.5)\right)\right), & 4.5\le t\le7.5\\[4pt] 0, & \text{otherwise.}\end{cases}$$

The graph of $f$ has a maximum point at $t=4.5$.

**(a)** **(i)** Find the value of $\int_{2.25}^{4.5}f(t)\,\mathrm dt$.
**(ii)** Write down the mode of $T$.
**(iii)** Determine which is greater, the mode of $T$ or the median of $T$,
justifying your answer.

The runners who finish the race in $3.5$ hours or less are considered to be
fast runners.

**(b)** Find the probability that a runner chosen at random is a fast
runner.

**(d)** Find the lower quartile of $T$.

*For (a)(iii) answer `'mode'` or `'median'`. Part (c) is technique 6 — it
is in the archive; (e) and (f) are $\mathrm E(a-bT)$ — D4.*
""")

code(r"""
q8ai = ...       # the integral from 2.25 to 4.5
q8aii = ...      # the mode
q8aiii = ...     # 'mode' or 'median' — which is greater
q8b = ...        # P(fast runner)
q8d = ...        # the lower quartile

Q1 = symbols('Q1')
T = Density({(Rational(9, 4), Rational(9, 2)): Rational(4, 21)*(1 - cos(4*pi/9*(t - Rational(9, 4)))),
             (Rational(9, 2), Rational(15, 2)): Rational(4, 21)*(1 + cos(pi/3*(t - Rational(9, 2))))},
            'T', var=t)

verify_chance('8a(i)', q8ai, P(T < 4.5))
verify_mode('8a(ii)', q8aii, T)
verify_greater('8a(iii)', q8aiii, T)
verify_chance('8b', q8b, P(T <= 3.5))
verify_letters('8d', q8d, Q1, [T], [Eq(P(T < Q1), 0.25)])
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 3. The mean, the variance, and a second question

## Theory: the mean and the variance are integrals too

In D4 the mean was $\sum x\,P(X=x)$. With a density the sum becomes an
integral, over the interval where $f$ lives:

$$\mathrm E(X)=\int x\,f(x)\,\mathrm dx,\qquad \mathrm{Var}(X)=\int x^2f(x)\,\mathrm dx-\big(\mathrm E(X)\big)^2$$

For $f(x)=\frac38x^2$ on $[0,2]$:

$$\mathrm E(X)=\int_0^2\tfrac38x^3\,\mathrm dx=1.5,\qquad \mathrm E(X^2)=\int_0^2\tfrac38x^4\,\mathrm dx=2.4,\qquad \mathrm{Var}(X)=2.4-1.5^2=0.15$$

> **$\mathrm E(X^2)$ is not the variance.** $2.4$ is the most common wrong
> answer here, and a markscheme gives it $(M1)A0A0A0$.

**Letters stay letters.** For $f(x)=\frac1{3c}$ on $[c,4c]$ the mean is
$\frac{5c}2$ by symmetry, and $\mathrm E(X^2)=\int_c^{4c}\frac{x^2}{3c}\,\mathrm dx=7c^2$.

**An exact value** needs the substitution: $\int\frac{x}{\sqrt{9-x^2}}\,\mathrm dx=-\sqrt{9-x^2}$.

**The mean of something else.** $\mathrm E(g(X))=\int g(x)\,f(x)\,\mathrm dx$.
The postage from Theory 1 is $4x$ below $1.5$ kg and $3x$ from $1.5$ kg, so
the expected postage is two integrals, one for each rate:

$$\int_{\text{start}}^{1.5}4x\,f(x)\,\mathrm dx+\int_{1.5}^{\text{end}}3x\,f(x)\,\mathrm dx$$

Multiplying $\mathrm E(X)$ by one rate is wrong on both pieces.
""")

md(r"""
### Task 9 🔴 — *May 2023 TZ2 Paper 1 Q6, 5 marks*

A continuous random variable $X$ has probability density function $f$
defined by

$$f(x)=\begin{cases}\dfrac1{2a}, & a\le x\le3a\\[4pt] 0, & \text{otherwise}\end{cases}$$

where $a$ is a positive real number.

**(a)** State $\mathrm E(X)$ in terms of $a$.

**(b)** Use integration to find $\mathrm{Var}(X)$ in terms of $a$.

*The checks try several values of $a$.*
""")

code(r"""
a = symbols('a', positive=True)

q9a = ...        # E(X) in terms of a
q9b = ...        # Var(X) in terms of a

X = Density({(a, 3*a): 1/(2*a)}, 'X')

verify_moment('9a', q9a, Expect(X))
verify_moment('9b', q9b, Var(X))
""")

# ================================================================= теория 6
md(r"""
## Theory: a second question around an area

**Given that.** The condition is the new whole; the event is the part of it
that also happens. For $f(x)=\frac38x^2$ on $[0,2]$:

$$P(X>1.5\mid X>1)=\frac{P(X>1.5)}{P(X>1)}=\frac{1-\frac{27}{64}}{1-\frac18}=0.661$$

Here the event lies inside the condition, so the overlap is the event
itself. When it does not, the numerator is the area of the overlap.

**An interval built from the moments.** $P(\mu-\sigma<X<\mu+\sigma)$ needs
the moments first: $\mu=1.5$, $\sigma=\sqrt{0.15}=0.387$, and then the area
from $1.113$ to $1.887$ is $0.668$.

> **$\sigma$, not $\sigma^2$.** The interval is one *standard deviation*
> each side; $\mu\pm0.15$ is a different, narrower question.
""")

md(r"""
### Task 10 🔴 — *November 2025 TZ1 Paper 2 Q11(c), (d), 8 marks*

The probability density function of a random variable $X$ is given by

$$f(x)=\begin{cases}3x\arccos(x^2), & 0\le x\le k\\ 0, & \text{otherwise.}\end{cases}$$

In part (b), $k$ is found from $k^2\arccos(k^2)-\sqrt{1-k^4}+\frac13=0$.

**(c)** Find **(i)** $\mathrm E(X)$; **(ii)** $\mathrm{Var}(X)$.

**(d)** Given that $\mu=\mathrm E(X)$ and $\sigma^2=\mathrm{Var}(X)$, find
$P(\mu-\sigma<X<\mu+\sigma)$.

*Parts (a) and (b) are integration — E5 and E6. The checks find $k$
themselves from the area being one.*
""")

code(r"""
q10ci = ...      # E(X)
q10cii = ...     # Var(X)
q10d = ...       # P(mu - sigma < X < mu + sigma)

k = symbols('k', positive=True)
X = Density({(0, k): 3*x*acos(x**2)}, 'X')
mu, sigma = Expect(X), SD(X)

verify_moment('10c(i)', q10ci, Expect(X), given=[], var=k)
verify_moment('10c(ii)', q10cii, Var(X), given=[], var=k)
verify_chance('10d', q10d, P((X > mu - sigma) & (X < mu + sigma)), given=[], var=k)
""")

md(r"""
### Task 11 🔴 — *May 2024 TZ2 Paper 2 Q10(d), (e), 8 marks*

A shop sells chocolates. The weight, in kilograms, of chocolates bought by
a random customer can be modelled by a continuous random variable $X$ with
probability density function $f$ defined by

$$f(x)=\begin{cases}\frac6{85}\left(4+3x-x^2\right), & 0.5\le x\le3\\ 0, & \text{otherwise.}\end{cases}$$

The shop sells chocolates to customers at \$25 per kilogram.

However, if the weight of chocolate bought by a customer is at least $0.75$
kilograms, the shop sells chocolate at a discounted rate of \$24 per
kilogram.

**(d)** Find the probability that a randomly selected customer spends at
most \$48.

**(e)** Find the expected amount spent per customer. Give your answer
correct to the nearest cent.

*Parts (a)–(c) — the mode, an area, the median — are in the archive.*
""")

code(r"""
q11d = ...       # P(spend <= 48)
q11e = ...       # the expected amount spent, to the nearest cent

X = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')
spend = X.map(lambda w: Piecewise((25*w, w < 0.75), (24*w, True)), 'spend')

verify_chance('11d', q11d, P(spend <= 48))
verify_moment('11e', q11e, Expect(spend), places=2)
""")

md(r"""
### Task 12 🔴 — *November 2025 TZ3 Paper 2 Q11(a), (b)(ii), (c), (d), 15 marks*

The lengths, in metres, of jumps in a long jump competition can be modelled
by a continuous random variable $X$ with probability density function $f$
defined by:

$$f(x)=\begin{cases}0, & x<3\\ a(x-3)^3+b(x-3)^2, & 3\le x\le9\\ 0, & x>9\end{cases}$$

where $a,b\in\mathbb R$, $a,b\ne0$.

**(a)** Show that $324a+72b=1$.

It is given that $f(9)=0$. In part (b)(i) this becomes $6a+b=0$.

**(b)** **(ii)** Determine the value of $a$ and the value of $b$.

**(c)** Show that the median of $X$ is less than the mode of $X$.

Matt has the final jump in the competition. He needs to jump at least
$8.52$ m to win the competition.

**(d)** Given that he jumps over $8$ m, use the model to find the probability
that he wins the competition.

*For (a) enter the area under $f$ in terms of $a$ and $b$. For (c) enter
the mode and the median; the check also wants the median to three
figures. The checks for (c) and (d) find $a$ and $b$ themselves.*
""")

code(r"""
a, b, m = symbols('a b m')

q12a = ...           # the area under f, in terms of a and b
q12bii = [...]       # [a, b]
q12c_mode = ...      # the mode
q12c_median = ...    # the median
q12d = ...           # P(X > 8.52 | X > 8)

X = Density({(3, 9): a*(x - 3)**3 + b*(x - 3)**2}, 'X')
zero = [Eq(6*a + b, 0)]

verify_chance('12a', q12a, total_probability(X), free=[a, b])
verify_letters('12b(ii)', q12bii, [a, b], [X], zero)
verify_mode('12c mode', q12c_mode, X, given=zero, var=[a, b])
verify_letters('12c median', q12c_median, m, [X], zero + [Eq(P(X < m), 0.5)])
verify_chance('12d', q12d, P(X > 8.52, given=X > 8), given=zero, var=[a, b])
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `area` | the density is known: find an area |
| `constant` | a letter in $f$, found from the whole area being one |
| `quantile` | a median or a quartile: a share of the area |
| `mode` | the mode, or the mode against the median |
| `moments` | the mean or the variance |
| `condition` | given that, or an interval built from the moments |

1. $f(x)=cx^3$ for $0\le x\le2$, and $0$ otherwise. Find $c$.
2. $f(x)=\frac12\sin x$ for $0\le x\le\pi$. Find the probability that $X$ is greater than $\frac\pi3$.
3. $f(x)=2x$ for $0\le x\le1$. Find the value of $x$ below which half of the distribution lies.
4. $f(x)=\frac34(1-x^2)$ for $-1\le x\le1$. Write down the most likely value of $X$.
5. $f(x)=\frac2{x^2}$ for $1\le x\le2$. Find $\mathrm E(X)$.
6. $f(x)=\frac18x$ for $0\le x\le4$. Given that $X>1$, find the probability that $X>3$.
7. A bus arrives at a random moment in the next $12$ minutes. Find the probability that you wait more than $8$ minutes.
8. $f(x)=p+qx$ for $0\le x\le4$, with $f(4)=0$. Find $p$ and $q$.
9. $f(x)=\frac1{9}x^2$ for $0\le x\le3$. Find the upper quartile.
10. $f(x)=e^{-x}$ for $x\ge0$. Find $\mathrm{Var}(X)$.
11. $f(x)=xe^{-x}$ for $x\ge0$. Show that the median is greater than the mode.
12. $f(x)=\frac32x^2$ for $-1\le x\le1$. Find $P(\mu-\sigma<X<\mu+\sigma)$.
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
## On the clock — *May 2023 TZ1 Paper 2 Q11(a), (b), 7 marks*

**Seven marks, nine minutes.** Calculator allowed, no hints.

A continuous random variable, $X$, has a probability density function
defined by

$$f(x)=\begin{cases}\dfrac6{\pi\sqrt{16-x^2}}, & 0\le x\le2\\[4pt] 0, & \text{otherwise.}\end{cases}$$

**(a)** Find the exact value of $\mathrm E(X)$.

**(b)** Find $P(X<0.5)$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_a = ...       # E(X), exact
qt_b = ...       # P(X < 0.5)

X = Density({(0, 2): 6/(pi*sqrt(16 - x**2))}, 'X')

verify_moment('timer (a)', qt_a, Expect(X), exact=True)
verify_chance('timer (b)', qt_b, P(X < 0.5))
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (e)** $H(t)=-0.4\cos(7.8t)+1.4$ starts at its minimum. It first reaches
$1.5$ at $t=0.233779\ldots$ and comes back down through $1.5$ at
$t=0.571757\ldots$, so in each period it is above $1.5$ for
$0.337978\ldots$ s. The period is $\frac{2\pi}{7.8}=0.805536\ldots$ s, and the
first five seconds hold six full periods; in the unfinished seventh the
weight does not get back above $1.5$ before $t=5$. So

$$P(H>1.5)=\frac{6\times0.337978\ldots}5=\frac{2.02787\ldots}5=0.405574\ldots=\boxed{0.406}$$

---

**2 (a)** $\int\frac{k}{\sqrt{4-3x^2}}\,\mathrm dx=\frac k{\sqrt3}\arcsin\left(\frac{\sqrt3}2x\right)$,
and between $0$ and $1$ that is $\frac k{\sqrt3}\cdot\frac\pi3$. Setting it equal to $1$:

$$k=\frac{3\sqrt3}{\pi}\qquad\boxed{k=\tfrac{3\sqrt3}\pi}$$

---

**3 (a)** With $u=x^2+k$: $\int\frac{x}{(x^2+k)^{3/2}}\,\mathrm dx=-(x^2+k)^{-1/2}$, so
the area is

$$\boxed{\frac1{\sqrt k}-\frac1{\sqrt{16+k}}}=1$$

and multiplying by $\sqrt k\sqrt{16+k}$ gives $\sqrt{16+k}-\sqrt k=\sqrt k\sqrt{16+k}$.

**3 (b)** Solving on the calculator: $k=0.645038\ldots=\boxed{0.645}$.

---

**4 (a)** By parts, $\int_0^b axe^x\,\mathrm dx=a\big[xe^x-e^x\big]_0^b=a(be^b-e^b+1)=1$:

$$\boxed{a=\frac1{be^b-e^b+1}}$$

**4 (b)** With $a=b=1$: $\int_0^m xe^x\,\mathrm dx=me^m-e^m+1=\frac12$, so
$m=0.768039\ldots=\boxed{0.768}$.

---

**5 (a)** $\int_0^kkx\,\mathrm dx+\int_k^{2k}(2kx-x^2)\,\mathrm dx=\frac{k^3}2+\left(3k^3-\frac73k^3\right)=\boxed{\frac{7k^3}6}$,
and this is $1$, so $7k^3=6$.

**5 (b)** $k=0.949914\ldots$, and the first piece holds $\frac{k^3}2=\frac37<\frac12$,
so the median is on the second piece:

$$\frac37+\Big[kx^2-\tfrac13x^3\Big]_k^m=\frac12\quad\Longrightarrow\quad m=1.02925\ldots=\boxed{1.03}$$

The markscheme warns that $\int_0^mkx\,\mathrm dx=0.5$ happens to give $1.03$
as well — but $m>k$, the first formula does not apply there, and that route
scores M1A0M0A0. No check on a number can see the difference.

---

**6 (a)** $\int_0^m\arccos x\,\mathrm dx=m\arccos m-\sqrt{1-m^2}+1=0.5$, so
$m=0.360034\ldots=\boxed{0.360}$.

**6 (b)** $P(m-a\le X\le m+a)=\int_{m-a}^{m+a}\arccos x\,\mathrm dx=0.3$, and the
calculator gives $a=0.124861\ldots=\boxed{0.125}$.

---

**7** Since $c\ge\frac{a+b}2$, the median is on the rising side. The area up
to $m$ is a triangle with base $m-a$ and height $f(m)$:

$$\frac12(m-a)\cdot\frac{2(m-a)}{(b-a)(c-a)}=\frac{(m-a)^2}{(b-a)(c-a)}=\frac12$$

so $m=a\pm\sqrt{\frac{(b-a)(c-a)}2}$, and $m\ge a$ rejects the minus sign:

$$\boxed{m=a+\sqrt{\frac{(b-a)(c-a)}2}}$$

---

**8 (a)(i)** $\int_{2.25}^{4.5}f(t)\,\mathrm dt=\frac4{21}\times2.25=\boxed{\frac37}=0.429$ —
the cosine integrates to zero over the half wave.

**8 (a)(ii)** The maximum is at $t=4.5$: mode $\boxed{4.5}$.

**8 (a)(iii)** $P(T<4.5)=\frac37<0.5$: half the area is reached only after
$4.5$, so the **median** is greater ($4.69$). $\boxed{\text{median}}$

**8 (b)** $\int_{2.25}^{3.5}f(t)\,\mathrm dt=0.103749\ldots=\boxed{0.104}$

**8 (d)** $\int_{2.25}^{q}f(t)\,\mathrm dt=0.25$ on the first piece (it holds
$\frac37>\frac14$), so $q=4.01290\ldots=\boxed{4.01}$.

---

**9 (a)** The density is constant on $[a,3a]$: by symmetry
$\mathrm E(X)=\boxed{2a}$.

**9 (b)** $\mathrm E(X^2)=\int_a^{3a}\frac{x^2}{2a}\,\mathrm dx=\Big[\frac{x^3}{6a}\Big]_a^{3a}=\frac{13a^2}3$, so

$$\mathrm{Var}(X)=\frac{13a^2}3-(2a)^2=\boxed{\frac{a^2}3}$$

---

**10 (c)** With $k=0.713250$: $\mathrm E(X)=\int_0^k3x^2\arccos(x^2)\,\mathrm dx=0.456309\ldots=\boxed{0.456}$;
$\mathrm E(X^2)=0.237198\ldots$, so $\mathrm{Var}(X)=0.237198\ldots-0.456309\ldots^2=0.0289805\ldots=\boxed{0.0290}$.

**10 (d)** $\sigma=0.170236\ldots$, so the interval is from $0.286072\ldots$ to
$0.626549\ldots$:

$$\int_{0.286072\ldots}^{0.626549\ldots}f(x)\,\mathrm dx=0.620012\ldots=\boxed{0.620}$$

---

**11 (d)** Below $0.75$ kg nobody spends more than $25\times0.75=\$18.75$. From
$0.75$ kg the price is $24x\le48$, so $x\le2$. The event is $0.5\le x\le2$:

$$\int_{0.5}^2f(x)\,\mathrm dx=0.635294\ldots=\boxed{0.635}$$

Solving $25x\le48$ instead gives $x\le1.92$ and $0.601$ — the discounted rate
applies there.

**11 (e)** Two integrals, one for each rate:

$$\int_{0.5}^{0.75}25x\,f(x)\,\mathrm dx+\int_{0.75}^{3}24x\,f(x)\,\mathrm dx=1.51482\ldots+39.4428\ldots=40.9576\ldots$$

so $\boxed{\$40.96}$.

---

**12 (a)** $\int_3^9\big(a(x-3)^3+b(x-3)^2\big)\,\mathrm dx=\Big[\frac a4(x-3)^4+\frac b3(x-3)^3\Big]_3^9=324a+72b$,
and that is $1$. $\boxed{324a+72b}$

**12 (b)(ii)** $324a+72b=1$ and $6a+b=0$: $\boxed{a=-\frac1{108},\ b=\frac1{18}}$
$(-0.00926,\ 0.0556)$.

**12 (c)** The maximum of $f$ on $[3,9]$ is at $(7,\ 0.296296\ldots)$: mode
$\boxed{7}$. The area from $3$ to $7$ is $0.592592\ldots>0.5$, so the median is
below $7$; solving $\int_3^mf(x)\,\mathrm dx=0.5$ gives
$m=6.68563\ldots=\boxed{6.69}$.

**12 (d)** Winning, $X>8.52$, lies inside the condition $X>8$:

$$P(X>8.52\mid X>8)=\frac{P(X>8.52)}{P(X>8)}=\frac{0.0344268\ldots}{0.131944\ldots}=0.260919\ldots=\boxed{0.261}$$

The markscheme accepts $0.263$ from $a$ and $b$ rounded to three figures.

---

## Timer

**(a)** $\mathrm E(X)=\int_0^2\frac{6x}{\pi\sqrt{16-x^2}}\,\mathrm dx=\frac6\pi\Big[-\sqrt{16-x^2}\Big]_0^2=\frac6\pi\big(4-\sqrt{12}\big)=\boxed{\frac{12}\pi\big(2-\sqrt3\big)}$

**(b)** $P(X<0.5)=\int_0^{0.5}f(x)\,\mathrm dx=0.239358\ldots=\boxed{0.239}$
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
