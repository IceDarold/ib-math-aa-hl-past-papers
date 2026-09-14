"""Собирает архивный ноутбук D6: вся тема плотности подряд.

Восемнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3, D4 и D5. Практикум учит: лестница из приёмов,
теория перед каждым, три уровня сложности, тренажёр распознавания,
задание на время. Архив не учит. Он даёт набивать руку: **вся тема
подряд, по тем же шести приёмам, без единой строчки теории**. Двадцать
девять вопросов, 114 баллов — всё, что архив спрашивает про величину с
плотностью, с мая 2021 по ноябрь 2025.

Разметка взята из карточки statistics-density.yaml: поле blocks у каждого
приёма. Дубля нет: в ноябре 2023 года плотности не спрашивали.

Части одного вопроса разнесены по своим приёмам: май 2024 TZ2 Q10 стоит
в §§ 1, 3, 4 и 5, ноябрь 2025 TZ3 Q11 — в §§ 2, 4 и 6, май 2025 TZ1 Q11 —
в §§ 1, 3, 4 и 6. Условие каждого пункта повторено целиком, насколько оно
нужно пункту, — плотность вместе с буквами, которые проверка находит сама
из того, что площадь под ней — единица.

«Show that» здесь проверяется по промежуточной строке: площадь под f как
выражение от букв — то, что приравнивают единице, — и f(9) через a и b.

Хешей нет ни одного: всякий ответ темы — площадь, буква плотности,
граница, мода или момент, и всякий проверяется самой плотностью.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_d6.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/archive-d6-density.ipynb')

ANSWERS = {
    # § 1. The area
    'q1_1': '0.239',
    'q1_2': '0.435',
    'q1_3': '0.104',
    'q1_4': '0.635',
    'q1_5': '0.406',
    # § 2. The constant
    'q2_1a': '1/sqrt(k) - 1/sqrt(16 + k)',
    'q2_1b': '0.645',
    'q2_2': '3*sqrt(3)/pi',
    'q2_3': '1/(b*exp(b) - exp(b) + 1)',
    'q2_4': '7*k**3/6',
    'q2_5a': '324*a + 72*b',
    'q2_5b': '216*a + 36*b',
    # § 3. The median, a quartile
    'q3_1a': '0.360',
    'q3_1b': '0.125',
    'q3_2': 'a + sqrt((b - a)*(c - a)/2)',
    'q3_3': '0.768',
    'q3_4': '1.03',
    'q3_5': '1.69',
    'q3_6': '4.01',
    'q3_7': '0.559',
    # § 4. The mode
    'q4_1': '1.5',
    'q4_2a': '4.5',
    'q4_2b': "'median'",
    'q4_3_mode': '7',
    'q4_3_median': '6.69',
    # § 5. The mean and the variance
    'q5_1a': '(n + 1)/(n + 2)',
    'q5_1b': '(n + 1)/((n + 2)**2*(n + 3))',
    'q5_2': 'sqrt(3)/pi',
    'q5_3': '12*(2 - sqrt(3))/pi',
    'q5_4a': '2*a',
    'q5_4b': 'a**2/3',
    'q5_5': '40.96',
    'q5_6a': '0.456',
    'q5_6b': '0.0290',
    # § 6. A second question
    'q6_1': '0.238',
    'q6_2': '0.620',
    'q6_3': '0.261',
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


CHOCOLATE = r"""$$f(x)=\begin{cases}\frac6{85}\left(4+3x-x^2\right), & 0.5\le x\le3\\ 0, & \text{otherwise.}\end{cases}$$"""

MARATHON = r"""In a marathon race, the random variable $T$ represents the time, in hours,
taken for a runner to complete the race. The probability density function
for $T$ is

$$f(t)=\begin{cases}\frac4{21}\left(1-\cos\left(\frac{4\pi}9(t-2.25)\right)\right), & 2.25\le t<4.5\\[4pt] \frac4{21}\left(1+\cos\left(\frac\pi3(t-4.5)\right)\right), & 4.5\le t\le7.5\\[4pt] 0, & \text{otherwise.}\end{cases}$$"""

MARATHON_CODE = r"""T = Density({(Rational(9, 4), Rational(9, 2)): Rational(4, 21)*(1 - cos(4*pi/9*(t - Rational(9, 4)))),
             (Rational(9, 2), Rational(15, 2)): Rational(4, 21)*(1 + cos(pi/3*(t - Rational(9, 2))))},
            'T', var=t)"""

JUMP = r"""The lengths, in metres, of jumps in a long jump competition can be modelled
by a continuous random variable $X$ with probability density function

$$f(x)=\begin{cases}a(x-3)^3+b(x-3)^2, & 3\le x\le9\\ 0, & \text{otherwise}\end{cases}$$

where $a,b\in\mathbb R$, $a,b\ne0$."""

md(r"""
# D6 archive — the probability density function, all of it

**Twenty-nine questions, 114 marks.** Every question the archive asks
about a random variable given by a probability density function, from May
2021 to November 2025, in the order of the six techniques rather than the
order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-d6-density.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The area | 5 | 13 |
| 2 | The constant | 5 | 24 |
| 3 | The median, a quartile | 7 | 27 |
| 4 | The mode | 3 | 10 |
| 5 | The mean and the variance | 6 | 30 |
| 6 | A second question around an area | 3 | 10 |

The checks are the same ones the practicum uses and they store nothing:
each is handed the density exactly as the question prints it —
`Density({interval: formula})`, zero elsewhere — and finds the area, any
letter in the density, the median, the mode and the moments itself. A
letter nobody gives a value is found from the area under $f$ being one.
Three significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** May 2024 TZ2 Q10 appears
in §§ 1, 3, 4 and 5; each part repeats what it needs.

**A *show that* is checked by its last line before the given result:** the
area under $f$ as an expression in the letters — the thing you set equal
to one — or $f(9)$ in terms of $a$ and $b$.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Density, P(), Expect, Var, SD

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. The area

**Five questions, 13 marks.** The density is known: an integral over the
right interval.
""")

md(r"""
### 1.1 — *May 2023 TZ1 Paper 2 Q11(b), 2 marks*

A continuous random variable, $X$, has a probability density function
defined by

$$f(x)=\begin{cases}\dfrac6{\pi\sqrt{16-x^2}}, & 0\le x\le2\\[4pt] 0, & \text{otherwise.}\end{cases}$$

**(b)** Find $P(X<0.5)$.

### 1.2 — *May 2024 TZ2 Paper 2 Q10(b), 2 marks*

The weight, in kilograms, of chocolates bought by a random customer can be
modelled by a continuous random variable $X$ with probability density
function

""" + CHOCOLATE + r"""

**(b)** Find $P(1\le X\le2)$.
""")

code(r"""
q1_1 = ...       # P(X < 0.5)
q1_2 = ...       # P(1 <= X <= 2)

X = Density({(0, 2): 6/(pi*sqrt(16 - x**2))}, 'X')
W = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')

verify_chance('1.1', q1_1, P(X < 0.5))
verify_chance('1.2', q1_2, P((W >= 1) & (W <= 2)))
""")

md(r"""
### 1.3 — *May 2025 TZ1 Paper 2 Q11(b), 2 marks*

""" + MARATHON + r"""

The runners who finish the race in $3.5$ hours or less are considered to be
fast runners.

**(b)** Find the probability that a runner chosen at random is a fast
runner.
""")

code(r"""
q1_3 = ...       # P(T <= 3.5)

""" + MARATHON_CODE + r"""

verify_chance('1.3', q1_3, P(T <= 3.5))
""")

md(r"""
### 1.4 — *May 2024 TZ2 Paper 2 Q10(d), 3 marks*

The weight, in kilograms, of chocolates bought by a random customer has
probability density function

""" + CHOCOLATE + r"""

The shop sells chocolates to customers at \$25 per kilogram. However, if the
weight of chocolate bought by a customer is at least $0.75$ kilograms, the
shop sells chocolate at a discounted rate of \$24 per kilogram.

**(d)** Find the probability that a randomly selected customer spends at
most \$48.

### 1.5 — *May 2023 TZ2 Paper 2 Q10(e), 4 marks*

The height, $H$ metres, of the base of a weight on a spring above the
ground is $H(t)=a\cos(7.8t)+b$, $0\le t\le10$, where $t$ is the time in
seconds after the weight is released. It is released at its minimum height
of $1$ metre and reaches a maximum height of $1.8$ metres, so that
$a=-0.4$ and $b=1.4$. A camera takes a picture of the weight at a random
time during the first five seconds of its motion.

**(e)** Find the probability that the height of the base of the weight is
greater than $1.5$ metres at the time the picture is taken.
""")

code(r"""
q1_4 = ...       # P(spend <= 48)
q1_5 = ...       # P(H > 1.5)

W = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')
spend = W.map(lambda w: Piecewise((25*w, w < 0.75), (24*w, True)), 'spend')
clock = Density({(0, 5): Rational(1, 5)}, 'T', var=t)
H = clock.map(lambda s: -0.4*cos(7.8*s) + 1.4, 'H')

verify_chance('1.4', q1_4, P(spend <= 48))
verify_chance('1.5', q1_5, P(H > 1.5))
""")

# ============================================================ § 2
md(r"""
---
# § 2. The constant

**Five questions, 24 marks.** A letter in $f$: the whole area is one.
""")

md(r"""
### 2.1 — *May 2021 TZ1 Paper 2 Q7, 7 marks*

A continuous random variable $X$ has the probability density function

$$f(x)=\begin{cases}\dfrac{x}{\sqrt{(x^2+k)^3}}, & 0\le x\le4\\[4pt] 0, & \text{otherwise}\end{cases}$$

where $k\in\mathbb R^+$.

**(a)** Show that $\sqrt{16+k}-\sqrt k=\sqrt k\,\sqrt{16+k}$.

**(b)** Find the value of $k$.

*For (a) enter the area under $f$ in terms of $k$.*
""")

code(r"""
k = symbols('k', positive=True)

q2_1a = ...      # the area under f, in terms of k
q2_1b = ...      # k

X = Density({(0, 4): x/sqrt((x**2 + k)**3)}, 'X')

verify_chance('2.1(a)', q2_1a, total_probability(X), free=k)
verify_letters('2.1(b)', q2_1b, k, [X])
""")

md(r"""
### 2.2 — *May 2022 TZ1 Paper 1 Q7(a), 4 marks*

The continuous random variable $X$ has probability density function

$$f(x)=\begin{cases}\dfrac{k}{\sqrt{4-3x^2}}, & 0\le x\le1\\[4pt] 0, & \text{otherwise.}\end{cases}$$

**(a)** Find the value of $k$.

### 2.3 — *November 2022 Paper 2 Q6(a), 5 marks*

The continuous random variable $X$ has a probability density function
$f(x)=axe^x$ for $0\le x\le b$, and $0$ otherwise, where $a,b\in\mathbb R^+$.

**(a)** Find an expression for $a$ in terms of $b$.
""")

code(r"""
k = symbols('k', positive=True)
a, b = symbols('a b', positive=True)

q2_2 = ...       # k, exact
q2_3 = ...       # a in terms of b

K = Density({(0, 1): k/sqrt(4 - 3*x**2)}, 'X')
A = Density({(0, b): a*x*exp(x)}, 'X')

verify_letters('2.2', q2_2, k, [K], exact=True)
verify_letters('2.3', q2_3, a, [A], free=b)
""")

md(r"""
### 2.4 — *May 2024 TZ1 Paper 2 Q8(a), 2 marks*

A continuous random variable $X$ has a probability density function

$$f(x)=\begin{cases}kx, & 0\le x\le k\\ 2kx-x^2, & k<x\le2k\\ 0, & \text{otherwise}\end{cases}$$

where $k>0$.

**(a)** Show that $k$ satisfies the equation $7k^3=6$.

*Enter the area under $f$ in terms of $k$.*

### 2.5 — *November 2025 TZ3 Paper 2 Q11(a), (b)(i), 6 marks*

""" + JUMP + r"""

**(a)** Show that $324a+72b=1$.

It is given that $f(9)=0$.

**(b)** **(i)** Show that $6a+b=0$.

*For (a) enter the area under $f$ in terms of $a$ and $b$; for (b)(i),
$f(9)$ in terms of $a$ and $b$.*
""")

code(r"""
k = symbols('k', positive=True)
a, b = symbols('a b')

q2_4 = ...       # the area under f, in terms of k
q2_5a = ...      # the area under f, in terms of a and b
q2_5b = ...      # f(9) in terms of a and b

B = Density({(0, k): k*x, (k, 2*k): 2*k*x - x**2}, 'X')
J = Density({(3, 9): a*(x - 3)**3 + b*(x - 3)**2}, 'X')

verify_chance('2.4', q2_4, total_probability(B), free=k)
verify_chance('2.5(a)', q2_5a, total_probability(J), free=[a, b])
verify_identity('2.5(b)(i)', q2_5b, J.pdf(9))
""")

# ============================================================ § 3
md(r"""
---
# § 3. The median, a quartile

**Seven questions, 27 marks.** A boundary with a share of the area to its
left.
""")

md(r"""
### 3.1 — *November 2021 Paper 2 Q7, 6 marks*

A continuous random variable $X$ has a probability density function
$f(x)=\arccos x$ for $0\le x\le1$, and $0$ otherwise. The median of this
distribution is $m$.

**(a)** Determine the value of $m$.

**(b)** Given that $P(\lvert X-m\rvert\le a)=0.3$, determine the value of $a$.
""")

code(r"""
q3_1a = ...      # m
q3_1b = ...      # a

m = symbols('m')
a = symbols('a', positive=True)
X = Density({(0, 1): acos(x)}, 'X')
median = Eq(P(X < m), 0.5)

verify_letters('3.1(a)', q3_1a, m, [X], [median])
verify_letters('3.1(b)', q3_1b, a, [X], [median, Eq(P((X >= m - a) & (X <= m + a)), 0.3)])
""")

md(r"""
### 3.2 — *May 2022 TZ2 Paper 1 Q8, 6 marks*

A continuous random variable $X$ has the probability density function

$$f(x)=\begin{cases}\dfrac{2}{(b-a)(c-a)}(x-a), & a\le x\le c\\[6pt] \dfrac{2}{(b-a)(b-c)}(b-x), & c<x\le b\\[6pt] 0, & \text{otherwise}\end{cases}$$

— a triangle rising from $0$ at $a$ to its peak at $c$ and back to $0$ at
$b$. Given that $c\ge\frac{a+b}2$, find an expression for the median of
$X$ in terms of $a$, $b$ and $c$.
""")

code(r"""
a, b, c, m = symbols('a b c m')

q3_2 = ...       # the median in terms of a, b, c

X = Density({(a, c): 2*(x - a)/((b - a)*(c - a)),
             (c, b): 2*(b - x)/((b - a)*(b - c))}, 'X')
triangles = [{a: 0, b: 4, c: 3}, {a: 1, b: 3, c: Rational(5, 2)}, {a: -2, b: 6, c: 5}]

verify_letters('3.2', q3_2, m, [X], [Eq(P(X < m), 0.5)], free=triangles)
""")

md(r"""
### 3.3 — *November 2022 Paper 2 Q6(b), 3 marks*

The continuous random variable $X$ has a probability density function
$f(x)=axe^x$ for $0\le x\le b$, and $0$ otherwise.

**(b)** In the case where $a=b=1$, find the median of $X$.

### 3.4 — *May 2024 TZ1 Paper 2 Q8(b), 4 marks*

A continuous random variable $X$ has the probability density function
$f(x)=kx$ for $0\le x\le k$, $f(x)=2kx-x^2$ for $k<x\le2k$, and $0$
otherwise, where $k>0$ satisfies $7k^3=6$.

**(b)** Find the median of $X$.
""")

code(r"""
q3_3 = ...       # the median when a = b = 1
q3_4 = ...       # the median

m = symbols('m')
k = symbols('k', positive=True)
X = Density({(0, 1): x*exp(x)}, 'X')
Y = Density({(0, k): k*x, (k, 2*k): 2*k*x - x**2}, 'X')

verify_letters('3.3', q3_3, m, [X], [Eq(P(X < m), 0.5)])
verify_letters('3.4', q3_4, m, [Y], [Eq(P(Y < m), 0.5)])
""")

md(r"""
### 3.5 — *May 2024 TZ2 Paper 2 Q10(c), 3 marks*

The weight, in kilograms, of chocolates bought by a random customer has
probability density function

""" + CHOCOLATE + r"""

**(c)** Find the median of $X$.

### 3.6 — *May 2025 TZ1 Paper 2 Q11(d), 3 marks*

""" + MARATHON + r"""

**(d)** Find the lower quartile of $T$.
""")

code(r"""
q3_5 = ...       # the median
q3_6 = ...       # the lower quartile

m, Q1 = symbols('m Q1')
W = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')
""" + MARATHON_CODE + r"""

verify_letters('3.5', q3_5, m, [W], [Eq(P(W < m), 0.5)])
verify_letters('3.6', q3_6, Q1, [T], [Eq(P(T < Q1), 0.25)])
""")

md(r"""
### 3.7 — *May 2025 TZ2 Paper 2 Q11(d), 2 marks*

The time, $T$, in minutes that a spinning top is in motion can be modelled
by the probability density function $f(t)=kte^{-3t}$ for $t\ge0$, and $0$
otherwise, where $k\in\mathbb Z^+$. Part (c) shows that $k=9$.

**(d)** Find the median length of time that a spinning top is in motion.

*Give the answer in minutes.*
""")

code(r"""
q3_7 = ...       # the median, in minutes

m = symbols('m')
top = Density({(0, oo): 9*t*exp(-3*t)}, 'T', var=t)

verify_letters('3.7', q3_7, m, [top], [Eq(P(top < m), 0.5)])
""")

# ============================================================ § 4
md(r"""
---
# § 4. The mode

**Three questions, 10 marks.** Where $f$ is highest — and against the
median.
""")

md(r"""
### 4.1 — *May 2024 TZ2 Paper 2 Q10(a), 2 marks*

The weight, in kilograms, of chocolates bought by a random customer has
probability density function

""" + CHOCOLATE + r"""

**(a)** Find the mode of $X$.

### 4.2 — *May 2025 TZ1 Paper 2 Q11(a)(ii)–(iii), 3 marks*

""" + MARATHON + r"""

The graph of $f$ has a maximum point at $t=4.5$, and
$\int_{2.25}^{4.5}f(t)\,\mathrm dt=\frac37$.

**(a)** **(ii)** Write down the mode of $T$. **(iii)** Determine which is
greater, the mode of $T$ or the median of $T$, justifying your answer.

*For (iii) answer `'mode'` or `'median'`.*
""")

code(r"""
q4_1 = ...       # the mode
q4_2a = ...      # the mode of T
q4_2b = ...      # 'mode' or 'median'

W = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')
""" + MARATHON_CODE + r"""

verify_mode('4.1', q4_1, W)
verify_mode('4.2(a)(ii)', q4_2a, T)
verify_greater('4.2(a)(iii)', q4_2b, T)
""")

md(r"""
### 4.3 — *November 2025 TZ3 Paper 2 Q11(c), 5 marks*

""" + JUMP + r"""

It is given that $f(9)=0$, so that $6a+b=0$.

**(c)** Show that the median of $X$ is less than the mode of $X$.

*Enter the mode and the median; the checks find $a$ and $b$ themselves.*
""")

code(r"""
a, b, m = symbols('a b m')

q4_3_mode = ...      # the mode
q4_3_median = ...    # the median

X = Density({(3, 9): a*(x - 3)**3 + b*(x - 3)**2}, 'X')
zero = [Eq(6*a + b, 0)]

verify_mode('4.3 mode', q4_3_mode, X, given=zero, var=[a, b])
verify_letters('4.3 median', q4_3_median, m, [X], zero + [Eq(P(X < m), 0.5)])
""")

# ============================================================ § 5
md(r"""
---
# § 5. The mean and the variance

**Six questions, 30 marks.** The areas under $x\,f(x)$ and $x^2f(x)$.
""")

md(r"""
### 5.1 — *May 2021 TZ2 Paper 2 Q6, 6 marks*

A continuous random variable $X$ has the probability density function
$f_n(x)=(n+1)x^n$ for $0\le x\le1$, and $0$ otherwise, where
$n\in\mathbb R$, $n\ge0$.

**(a)** Show that $\mathrm E(X)=\frac{n+1}{n+2}$.

**(b)** Show that $\mathrm{Var}(X)=\frac{n+1}{(n+2)^2(n+3)}$.

*Enter the expressions in terms of $n$; the checks try several $n$.*
""")

code(r"""
n = symbols('n', nonnegative=True)

q5_1a = ...      # E(X) in terms of n
q5_1b = ...      # Var(X) in terms of n

X = Density({(0, 1): (n + 1)*x**n}, 'X')

verify_moment('5.1(a)', q5_1a, Expect(X))
verify_moment('5.1(b)', q5_1b, Var(X))
""")

md(r"""
### 5.2 — *May 2022 TZ1 Paper 1 Q7(b), 4 marks*

The continuous random variable $X$ has probability density function
$f(x)=\dfrac{k}{\sqrt{4-3x^2}}$ for $0\le x\le1$, and $0$ otherwise.

**(b)** Find $\mathrm E(X)$.

### 5.3 — *May 2023 TZ1 Paper 2 Q11(a), 5 marks*

A continuous random variable, $X$, has probability density function
$f(x)=\dfrac6{\pi\sqrt{16-x^2}}$ for $0\le x\le2$, and $0$ otherwise.

**(a)** Find the exact value of $\mathrm E(X)$.
""")

code(r"""
q5_2 = ...       # E(X), exact
q5_3 = ...       # E(X), exact

k = symbols('k', positive=True)
K = Density({(0, 1): k/sqrt(4 - 3*x**2)}, 'X')
X = Density({(0, 2): 6/(pi*sqrt(16 - x**2))}, 'X')

verify_moment('5.2', q5_2, Expect(K), given=[], var=k, exact=True)
verify_moment('5.3', q5_3, Expect(X), exact=True)
""")

md(r"""
### 5.4 — *May 2023 TZ2 Paper 1 Q6, 5 marks*

A continuous random variable $X$ has probability density function
$f(x)=\dfrac1{2a}$ for $a\le x\le3a$, and $0$ otherwise, where $a$ is a
positive real number.

**(a)** State $\mathrm E(X)$ in terms of $a$.

**(b)** Use integration to find $\mathrm{Var}(X)$ in terms of $a$.
""")

code(r"""
a = symbols('a', positive=True)

q5_4a = ...      # E(X) in terms of a
q5_4b = ...      # Var(X) in terms of a

X = Density({(a, 3*a): 1/(2*a)}, 'X')

verify_moment('5.4(a)', q5_4a, Expect(X))
verify_moment('5.4(b)', q5_4b, Var(X))
""")

md(r"""
### 5.5 — *May 2024 TZ2 Paper 2 Q10(e), 5 marks*

The weight, in kilograms, of chocolates bought by a random customer has
probability density function

""" + CHOCOLATE + r"""

The shop sells chocolates at \$25 per kilogram, but at a discounted rate of
\$24 per kilogram when the weight is at least $0.75$ kilograms.

**(e)** Find the expected amount spent per customer. Give your answer
correct to the nearest cent.

### 5.6 — *November 2025 TZ1 Paper 2 Q11(c), 5 marks*

The probability density function of a random variable $X$ is
$f(x)=3x\arccos(x^2)$ for $0\le x\le k$, and $0$ otherwise.

**(c)** Find **(i)** $\mathrm E(X)$; **(ii)** $\mathrm{Var}(X)$.

*The checks find $k$ themselves from the area being one.*
""")

code(r"""
q5_5 = ...       # the expected amount spent, to the nearest cent
q5_6a = ...      # E(X)
q5_6b = ...      # Var(X)

W = Density({(Rational(1, 2), 3): Rational(6, 85)*(4 + 3*x - x**2)}, 'X')
spend = W.map(lambda w: Piecewise((25*w, w < 0.75), (24*w, True)), 'spend')
k = symbols('k', positive=True)
X = Density({(0, k): 3*x*acos(x**2)}, 'X')

verify_moment('5.5', q5_5, Expect(spend), places=2)
verify_moment('5.6(c)(i)', q5_6a, Expect(X), given=[], var=k)
verify_moment('5.6(c)(ii)', q5_6b, Var(X), given=[], var=k)
""")

# ============================================================ § 6
md(r"""
---
# § 6. A second question around an area

**Three questions, 10 marks.** A ratio of areas, and an interval built from
the moments.
""")

md(r"""
### 6.1 — *May 2025 TZ1 Paper 2 Q11(c), 3 marks*

""" + MARATHON + r"""

The runners who finish the race in $3.5$ hours or less are considered to be
fast runners.

**(c)** Find the probability that a fast runner chosen at random finishes the
race in $3$ hours or less.

### 6.2 — *November 2025 TZ1 Paper 2 Q11(d), 3 marks*

The probability density function of a random variable $X$ is
$f(x)=3x\arccos(x^2)$ for $0\le x\le k$, and $0$ otherwise.

**(d)** Given that $\mu=\mathrm E(X)$ and $\sigma^2=\mathrm{Var}(X)$, find
$P(\mu-\sigma<X<\mu+\sigma)$.
""")

code(r"""
q6_1 = ...       # P(T <= 3 | T <= 3.5)
q6_2 = ...       # P(mu - sigma < X < mu + sigma)

""" + MARATHON_CODE + r"""
k = symbols('k', positive=True)
X = Density({(0, k): 3*x*acos(x**2)}, 'X')
mu, sigma = Expect(X), SD(X)

verify_chance('6.1', q6_1, P(T <= 3, given=T <= 3.5))
verify_chance('6.2', q6_2, P((X > mu - sigma) & (X < mu + sigma)), given=[], var=k)
""")

md(r"""
### 6.3 — *November 2025 TZ3 Paper 2 Q11(d), 4 marks*

""" + JUMP + r"""

It is given that $f(9)=0$, so that $6a+b=0$. Matt has the final jump in the
competition. He needs to jump at least $8.52$ m to win the competition.

**(d)** Given that he jumps over $8$ m, use the model to find the probability
that he wins the competition.
""")

code(r"""
q6_3 = ...       # P(X > 8.52 | X > 8)

a, b = symbols('a b')
X = Density({(3, 9): a*(x - 3)**3 + b*(x - 3)**2}, 'X')

verify_chance('6.3', q6_3, P(X > 8.52, given=X > 8), given=[Eq(6*a + b, 0)], var=[a, b])
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

**1.1** $\int_0^{0.5}f(x)\,\mathrm dx=0.239358\ldots=\boxed{0.239}$.

**1.2** $\int_1^2f(x)\,\mathrm dx=\frac{37}{85}=0.435294\ldots=\boxed{0.435}$.

**1.3** $\int_{2.25}^{3.5}f(t)\,\mathrm dt=0.103749\ldots=\boxed{0.104}$.

**1.4** Below $0.75$ kg nobody spends more than \$18.75; from $0.75$ kg,
$24x\le48$ gives $x\le2$. $\int_{0.5}^2f(x)\,\mathrm dx=0.635294\ldots=\boxed{0.635}$.

**1.5** Above $1.5$ for $0.337978\ldots$ s in each period of $0.805536\ldots$ s,
six full periods in five seconds: $\frac{6\times0.337978\ldots}5=\boxed{0.406}$.

---

**2.1** (a) $\int_0^4\frac{x}{(x^2+k)^{3/2}}\,\mathrm dx=\boxed{\frac1{\sqrt k}-\frac1{\sqrt{16+k}}}=1$,
and multiplying by $\sqrt k\sqrt{16+k}$ gives the result. (b) $k=0.645038\ldots=\boxed{0.645}$.

**2.2** $\frac k{\sqrt3}\cdot\frac\pi3=1$: $\boxed{k=\frac{3\sqrt3}\pi}$.

**2.3** $a\big[xe^x-e^x\big]_0^b=1$: $\boxed{a=\frac1{be^b-e^b+1}}$.

**2.4** $\frac{k^3}2+\left(3k^3-\frac73k^3\right)=\boxed{\frac{7k^3}6}=1$, so $7k^3=6$.

**2.5** (a) $\Big[\frac a4(x-3)^4+\frac b3(x-3)^3\Big]_3^9=\boxed{324a+72b}=1$.
(b)(i) $f(9)=216a+36b=\boxed{216a+36b}=0$, and dividing by $36$, $6a+b=0$.

---

**3.1** (a) $m\arccos m-\sqrt{1-m^2}+1=0.5$: $m=0.360034\ldots=\boxed{0.360}$.
(b) $\int_{m-a}^{m+a}\arccos x\,\mathrm dx=0.3$: $a=0.124861\ldots=\boxed{0.125}$.

**3.2** The triangle up to $m$ has area $\frac{(m-a)^2}{(b-a)(c-a)}=\frac12$, and $m\ge a$:
$\boxed{m=a+\sqrt{\frac{(b-a)(c-a)}2}}$.

**3.3** $me^m-e^m+1=\frac12$: $m=0.768039\ldots=\boxed{0.768}$.

**3.4** $k=0.949914\ldots$; the first piece holds $\frac37$, so the median is on the second:
$m=1.02925\ldots=\boxed{1.03}$.

**3.5** $\int_{0.5}^mf(x)\,\mathrm dx=0.5$: $m=1.68701\ldots=\boxed{1.69}$ kg.

**3.6** The first piece holds $\frac37>\frac14$: $q=4.01290\ldots=\boxed{4.01}$.

**3.7** $1-(3m+1)e^{-3m}=0.5$: $m=0.559448\ldots=\boxed{0.559}$ minutes ($33.6$ seconds).

---

**4.1** The parabola $4+3x-x^2$ has its vertex at $x=1.5$: mode $\boxed{1.5}$ kg.

**4.2** (ii) $\boxed{4.5}$. (iii) $P(T<4.5)=\frac37<0.5$, so the median ($4.69$) is
greater: $\boxed{\text{median}}$.

**4.3** $a=-\frac1{108}$, $b=\frac1{18}$. The maximum of $f$ is at $(7,\ 0.296296\ldots)$:
mode $\boxed7$. The area from $3$ to $7$ is $0.592592\ldots>0.5$; the median is
$6.68563\ldots=\boxed{6.69}<7$.

---

**5.1** (a) $\int_0^1(n+1)x^{n+1}\,\mathrm dx=\boxed{\frac{n+1}{n+2}}$.
(b) $\mathrm E(X^2)=\frac{n+1}{n+3}$, and
$\frac{n+1}{n+3}-\left(\frac{n+1}{n+2}\right)^2=\boxed{\frac{n+1}{(n+2)^2(n+3)}}$.

**5.2** $k=\frac{3\sqrt3}\pi$, and $\frac{3\sqrt3}\pi\Big[-\frac13\sqrt{4-3x^2}\Big]_0^1=\boxed{\frac{\sqrt3}\pi}$.

**5.3** $\frac6\pi\Big[-\sqrt{16-x^2}\Big]_0^2=\boxed{\frac{12}\pi\left(2-\sqrt3\right)}$.

**5.4** (a) $\boxed{2a}$ by symmetry. (b) $\frac{13a^2}3-4a^2=\boxed{\frac{a^2}3}$.

**5.5** $\int_{0.5}^{0.75}25x\,f(x)\,\mathrm dx+\int_{0.75}^324x\,f(x)\,\mathrm dx=40.9576\ldots$:
$\boxed{\$40.96}$.

**5.6** $k=0.713250$. (i) $0.456309\ldots=\boxed{0.456}$.
(ii) $0.237198\ldots-0.456309\ldots^2=0.0289805\ldots=\boxed{0.0290}$.

---

**6.1** $\frac{P(T\le3)}{P(T\le3.5)}=\frac{0.0247152\ldots}{0.103749\ldots}=0.238220\ldots=\boxed{0.238}$.

**6.2** $\sigma=0.170236\ldots$; $\int_{0.286072\ldots}^{0.626545\ldots}f(x)\,\mathrm dx=0.620012\ldots=\boxed{0.620}$.

**6.3** $\frac{P(X>8.52)}{P(X>8)}=\frac{0.0344268\ldots}{0.131944\ldots}=0.260919\ldots=\boxed{0.261}$.
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
