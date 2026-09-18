"""Собирает архивный ноутбук E8: вся тема стационарных точек подряд.

Двадцать второй ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3, D4, D5, D6, C5, C6 и C7. Практикум учит: лестница
из приёмов, теория перед каждым, три уровня сложности, тренажёр
распознавания, задание на время. Архив не учит. Он даёт набивать руку:
**вся тема подряд, по тем же восьми приёмам, без единой строчки теории**.
Тридцать один вопрос, 100 баллов.

Разметка взята из карточки calculus-stationary-points.yaml: поле blocks у
каждого приёма. Ноябрь 2023 года стоит в корпусе дважды, TZ1 и TZ2 одной
бумаги; здесь он один раз. Один балл доли — пункт (d)(iii) майского 2025
TZ2 Paper 3, где касательная параллельна наклонной асимптоте, — сюда не
входит: стационарной точки в нём нет, и в карточке он записан в leftovers.

Части одного вопроса разнесены по своим приёмам: майский 2021 TZ1 Paper 3
Q1 — в §§ 5, 6 и 7; ноябрьский 2023 Paper 3 Q1 — в §§ 2, 5 и 6; майский
2022 TZ1 Paper 3 Q2 — целиком в § 4; майский 2022 TZ2 Paper 3 Q1 — в §§ 4
и 8. Условие каждого пункта повторено целиком, насколько оно нужно пункту.

«Show that» здесь проверяется по существу: точка обязана оказаться
стационарной у самой кривой, вид её — тем, что кривая рядом ниже или выше,
перегиб — тем, что хорда перешла на другую сторону.

Хешей нет ни одного: всякий ответ темы — точка, слово, множество или
неравенство, и всякий проверяется самой кривой вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_e8.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/calculus/archive-e8-stationary-points.ipynb')

ANSWERS = {
    # § 1. Find the point
    'q1_1': '(2, Rational(-64, 3))',
    'q1_2': '[(0, E), (pi/2, exp(-1)), (pi, E)]',
    'q1_3': '(0.709, 0.640)',
    'q1_4': '(3, -2 + 2*sqrt(5))',
    'q1_5': '[(-1.94, 1.20), (1.94, -1.20)]',
    'q1_6': '(6, 36)',
    'q1_7': '5.74',
    'q1_8': 'Interval(Rational(-1, 2), Rational(1, 2))',
    # § 2. Name the kind from the second derivative
    'q2_1': "['maximum', 'minimum', 'maximum']",
    'q2_2a': '6*x + 2*a',
    'q2_2b': "['minimum', 'maximum']",
    'q2_3': "'maximum'",
    'q2_4a': '24*x - 4*(a + b)',
    'q2_4b': "'maximum'",
    # § 3. Name the kind from the sign of the first derivative
    'q3_1': "'maximum'",
    'q3_2a': "'minimum'",
    'q3_2b': "'inflexion'",
    # § 4. The point of inflexion
    'q4_1': '-1.60',
    'q4_2': '(2*a + r)/3',
    'q4_3': 'r + Rational(2, 3)*(a - r)',
    'q4_4': '(r, 0)',
    'q4_5a': '(0, 1)',
    'q4_5b': '(0, -1)',
    'q4_6': 'sqrt((2*sqrt(3) - 3)/3)',
    'q4_7': '0.656',
    'q4_8': "'inflexion'",
    # § 5. A family with a letter
    'q5_1': '[(0, b), (-2*a/3, 4*a**3/27 + b)]',
    'q5_2': '[(-sqrt(c), 2*c**Rational(3, 2) + 2),\n        (sqrt(c), -2*c**Rational(3, 2) + 2)]',
    # § 6. Which side of the axis
    'q6_1': "['above', 'above']",
    'q6_2': '4*a**3/27 + b < 0',
    # § 7. How many
    'q7_1a': 'FiniteSet(0)',
    'q7_1b': 'Interval.open(0, oo)',
    'q7_1c': 'Interval.open(-oo, 0)',
    'q7_2a': 'Interval.open(0, 1)',
    'q7_2b': 'FiniteSet(1)',
    'q7_2c': 'Interval.open(1, oo)',
    'q7_3': 'Or(c <= 0, d > 2*c**Rational(3, 2), d < -2*c**Rational(3, 2))',
    # § 8. There are none
    'q8_1': '[]',
    'q8_2': '[]',
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
# E8 archive — stationary points, all of them

**Thirty-one questions, 100 marks.** Every question the archive asks about the
shape of a graph, from May 2021 to November 2025, in the order of the eight
techniques rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-e8-stationary-points.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Find the point | 8 | 27 |
| 2 | Name the kind from $f''$ | 4 | 13 |
| 3 | Name the kind from the sign of $f'$ | 2 | 7 |
| 4 | The point of inflexion | 8 | 18 |
| 5 | A family with a letter | 2 | 9 |
| 6 | Which side of the axis | 2 | 2 |
| 7 | How many | 3 | 16 |
| 8 | There are none | 2 | 8 |

The checks are the same ones the practicum uses and they store nothing. Each
is handed the curve exactly as the question names it and then **walks along
it**: `verify_turning` finds every flat place and compares, `verify_nature`
looks at the neighbours, `verify_bend` measures the bend with a chord,
`verify_side` reads the sign of the second coordinate, `verify_param_set` and
`verify_condition` ask the property itself at a grid of values. Three
significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** The Paper 3 cubic of May 2021
TZ1 appears in §§ 5, 6 and 7; the Paper 3 family of November 2023 in §§ 2, 5
and 6; the implicit curve of May 2022 TZ2 in §§ 4 and 8. Each part repeats what
it needs.

**A *show that* is checked by substance, not by the printed line:** a point
claimed to be stationary has to be flat on the curve itself, a point claimed to
be a maximum has to have the curve lower on both sides, a point claimed to be
an inflexion has to have the chord change sides.

Answers that are words go in quotes: `'maximum'`, `'minimum'`, `'inflexion'`,
`'above'`, `'below'`. Sets go as `FiniteSet(0)`, `Interval.open(0, oo)`.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + curve, stationary, nature, crossings

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ================================================================ § 1
md(r"""
---
# § 1. Find the point

**Eight questions, 27 marks.** Solve $f'(x)=0$, then go back to $f$ for the
second coordinate. Both coordinates carry marks, and so does finding *every*
such point.
""")

md(r"""
### 1.1 — *May 2025 TZ1 Paper 1 Q1, 5 marks*

Consider $f(x)=\dfrac{4x^3}{3}-16x$ for $x\in\mathbb R$. The graph of $y=f(x)$
has a local minimum point at $(p,q)$ where $p>0$.

Find the value of $p$ and the value of $q$.
""")

code(r"""
q1_1 = ...       # the point (p, q)

verify_turning('1.1', q1_1, 4*x**3/3 - 16*x, 'minimum', domain=(0, 6))
""")

md(r"""
### 1.2 — *November 2023 TZ2 Paper 1 Q11(a), 5 marks*

Consider $f(x)=e^{\cos 2x}$, where $-\dfrac{\pi}{4}\le x\le\dfrac{5\pi}{4}$.

Find the coordinates of the points on the curve $y=f(x)$ where the gradient is
zero.
""")

code(r"""
q1_2 = [...]     # every point of zero gradient

verify_turning('1.2', q1_2, exp(cos(2*x)), domain=(-pi/4, 5*pi/4))
""")

md(r"""
### 1.3 — *November 2022 Paper 2 Q2(a), 2 marks*

The function $f$ is defined as $f(x)=\ln(xe^x+1)-x^4$ for $0\le x\le2$. The
graph of $f$ has a local maximum at point $A$.

Find the coordinates of $A$.
""")

code(r"""
q1_3 = ...       # the coordinates of A

verify_turning('1.3', q1_3, log(x*exp(x) + 1) - x**4, 'maximum', domain=(0, 2))
""")

md(r"""
### 1.4 — *May 2025 TZ2 Paper 2 Q12(c), 3 marks*

The curve $C$ has equation $4x^2+y^2-24x+4y+20=0$, and its domain is
$3-\sqrt5\le x\le 3+\sqrt5$. The curve has a maximum point at $A$.

Find $(x_A,y_A)$, the coordinates of $A$.
""")

code(r"""
q1_4 = ...       # the coordinates of A

shape = curve(Eq(4*x**2 + y**2 - 24*x + 4*y + 20, 0))

verify_turning('1.4', q1_4, shape, 'maximum', domain=(3 - sqrt(5), 3 + sqrt(5)))
""")

md(r"""
### 1.5 — *May 2025 TZ2 Paper 3 Q1(a)(iii), 2 marks*

Consider the curve given by $y=\dfrac{x\left(x^2-16\right)}{x^2+16}$.

State the coordinates of the local maximum point and the coordinates of the
local minimum point.
""")

code(r"""
q1_5 = [...]     # the local maximum and the local minimum

verify_turning('1.5', q1_5, x*(x**2 - 16)/(x**2 + 16), domain=(-10, 10))
""")

md(r"""
### 1.6 — *May 2023 TZ1 Paper 3 Q2(b), 2 marks*

Consider two numbers $x_1,x_2\in\mathbb R^+$ with $x_1+x_2=12$, so that their
product is $f(x_1)=x_1(12-x_1)$.

**(i)** Find the value of $x_1$ for which the function is maximum.

**(ii)** Hence show that the maximum product of $x_1$ and $x_2$ is $36$.

*Enter both as one point: the value of $x_1$ and the product there.*
""")

code(r"""
q1_6 = ...       # (the best x₁, the product there)

verify_turning('1.6', q1_6, x*(12 - x), 'maximum', domain=(0, 12))
""")

md(r"""
### 1.7 — *November 2023 TZ1 Paper 2 Q4(a), 2 marks*

A particle moves along a straight line. Its displacement, $s$ metres, from a
fixed point $O$ after time $t$ seconds is given by

$$s(t)=4.3\sin\left(\sqrt{3t+5}\right),\qquad 0\le t\le 10$$

The particle first comes to rest after $q$ seconds. Find the value of $q$.
""")

code(r"""
q1_7 = ...       # the value of q

verify_turning('1.7', q1_7, 4.3*sin(sqrt(3*t + 5)), var=t, domain=(0, 10),
               coordinates=False)
""")

md(r"""
### 1.8 — *May 2022 TZ2 Paper 1 Q6(b), 6 marks*

A function $f$ is defined by $f(x)=x\sqrt{1-x^2}$ where $-1\le x\le 1$. The
range of $f$ is $a\le y\le b$, where $a,b\in\mathbb R$.

Find the value of $a$ and the value of $b$.

*Enter the range as an interval.*
""")

code(r"""
q1_8 = ...       # the range of f

verify_range('1.8', q1_8, x*sqrt(1 - x**2), domain=Interval(-1, 1))
""")

# ================================================================ § 2
md(r"""
---
# § 2. Name the kind from $f''$

**Four questions, 13 marks.** Substitute the stationary point into the second
derivative and read the sign. Markschemes for this technique want the value,
not only the sign.
""")

md(r"""
### 2.1 — *November 2023 TZ2 Paper 1 Q11(b), 4 marks*

For $f(x)=e^{\cos 2x}$ on $-\dfrac{\pi}{4}\le x\le\dfrac{5\pi}{4}$, using the
second derivative at each point found in part (a), show that the curve
$y=f(x)$ has two local maximum points and one local minimum point.

*Give the three kinds as a list, in the order $x=0,\ \frac\pi2,\ \pi$.*
""")

code(r"""
q2_1 = [...]     # the kind of each point

verify_nature('2.1', q2_1, exp(cos(2*x)), [0, pi/2, pi], domain=(-pi/4, 5*pi/4))
""")

md(r"""
### 2.2 — *November 2023 Paper 3 Q1(f)(i), 3 marks*

Consider the family of curves $y=x^3+ax^2+b$ with $a\ne0$. Its points of zero
gradient are $P(0,b)$ and $Q\left(-\frac{2a}{3},\ \frac{4a^3}{27}+b\right)$.
Consider them for $a>0$ and $b>0$.

Find an expression for $\dfrac{d^2y}{dx^2}$ and hence determine whether each
point is a local maximum or a local minimum.

*Two answers: the second derivative, and the two kinds with $P$ first.*
""")

code(r"""
a, b = symbols('a b')

q2_2a = ...      # d²y/dx²
q2_2b = [...]    # the kind of each point, in order

family = x**3 + a*x**2 + b
positive = {a: (3, 1, 2, 6), b: (1, 2, 5, 1)}      # a > 0, b > 0

verify_derivative('2.2a', q2_2a, family, order=2)
verify_nature('2.2b', q2_2b, family, [0, -2*a/3], domain=(-8, 4), params=positive)
""")

md(r"""
### 2.3 — *November 2023 Paper 3 Q1(g)(i), 1 mark*

For the same family, consider the points $P$ and $Q$ for $a<0$ and $b>0$.

State whether $P$ is a local maximum or a local minimum.
""")

code(r"""
q2_3 = ...       # the kind of the point at the origin when a < 0

negative = {a: (-3, -1, -2, -6), b: (1, 2, 5, 1)}  # a < 0, b > 0

verify_nature('2.3', q2_3, x**3 + a*x**2 + b, 0, domain=(-4, 8), params=negative)
""")

md(r"""
### 2.4 — *May 2025 TZ3 Paper 3 Q2(d), 5 marks*

A box is folded from an $a\times b$ sheet with squares of side $x$ cut from the
corners, so that $V=x(a-2x)(b-2x)$ for $0\le x\le\frac a2$, where $a<b$. The
only solutions of $\frac{dV}{dx}=0$ are
$x=\dfrac{(a+b)\pm\sqrt{a^2-ab+b^2}}{6}$, and

$$x_m=\frac{(a+b)-\sqrt{a^2-ab+b^2}}{6}$$

is the one inside the interval.

Use $\dfrac{d^2V}{dx^2}$ to show that there is a local maximum of $V$ at
$x=x_m$.

*Two answers: the second derivative, and the kind of point.*
""")

code(r"""
a, b = symbols('a b', positive=True)

q2_4a = ...      # d²V/dx²
q2_4b = ...      # the kind of point at x_m

V = x*(a - 2*x)*(b - 2*x)
x_m = ((a + b) - sqrt(a**2 - a*b + b**2))/6
sheets = {a: (3, 2, 4, 5), b: (5, 7, 9, 6)}        # a < b, both positive

verify_derivative('2.4a', q2_4a, V, order=2)
verify_nature('2.4b', q2_4b, V, x_m, domain=(0, a/2), params=sheets)
""")

# ================================================================ § 3
md(r"""
---
# § 3. Name the kind from the sign of $f'$

**Two questions, 7 marks.** The gradient changes from $+$ to $-$, or it does
not change at all. This is the technique that still works when $f''$ is zero.
""")

md(r"""
### 3.1 — *November 2025 TZ1 Paper 1 Q9(b), 2 marks*

The function $f$ has a derivative given by $f'(x)=3x^2+12x-15$, and the graph
of $y=f(x)$ has horizontal tangents where $x=a=-5$ and $x=b=1$. The sign of
$f'$ on the three intervals they cut is $+$, then $-$, then $+$.

State, with a reason, whether there is a local maximum point or a local minimum
point on the graph of $y=f(x)$ at $x=a$.
""")

code(r"""
q3_1 = ...       # the kind of point at x = a

shape = integrate(3*x**2 + 12*x - 15, x)     # any antiderivative will do

verify_nature('3.1', q3_1, shape, -5, domain=(-9, 5))
""")

md(r"""
### 3.2 — *May 2021 TZ2 Paper 3 Q1(g), 5 marks*

Consider $f_n(x)=x^n(a-x)^n$ for $a\in\mathbb Z^+$ and $n\in\mathbb Z^+$, $n>1$.
Earlier parts give $f_n'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}$ and the fact that
$f_n'\!\left(\frac a4\right)>0$.

By using that fact and considering the sign of $f_n'(-1)$, show that the point
$(0,0)$ on the graph of $y=f_n(x)$ is

**(i)** a local minimum point for even values of $n$, where $n>1$;

**(ii)** a point of inflexion with zero gradient for odd values of $n$, where
$n>1$.
""")

code(r"""
n, a = symbols('n a', positive=True)

q3_2a = ...      # the kind of point at the origin for even n
q3_2b = ...      # the kind of point at the origin for odd n

f_n = x**n*(a - x)**n

verify_nature('3.2(i)', q3_2a, f_n, 0, domain=(-1, a + 1),
              params={n: (2, 4, 2, 4), a: (2, 2, 3, 5)})
verify_nature('3.2(ii)', q3_2b, f_n, 0, domain=(-1, a + 1),
              params={n: (3, 5, 3, 5), a: (2, 2, 3, 5)})
""")

# ================================================================ § 4
md(r"""
---
# § 4. The point of inflexion

**Eight questions, 18 marks.** $f''=0$ **and** the concavity changes. On a
calculator paper the shortest route is a stationary point of $f'$.
""")

md(r"""
### 4.1 — *May 2021 TZ1 Paper 2 Q11(c), 2 marks*

The function $f$ is defined by $f(x)=\dfrac{3x+2}{4x^2-1}$ for $x\ne\pm\frac12$.
The graph of $y=f(x)$ has exactly one point of inflexion.

Find the $x$-coordinate of the point of inflexion.
""")

code(r"""
q4_1 = ...       # the x-coordinate of the point of inflexion

verify_bend('4.1', q4_1, (3*x + 2)/(4*x**2 - 1), domain=(-4, -0.55))
""")

md(r"""
### 4.2 — *May 2022 TZ1 Paper 3 Q2(g)(i), 2 marks*

Consider the curve $y=(x-r)(x^2-2ax+a^2+b^2)$ for $a\ne r$ and $b>0$. It has a
point of inflexion at $P$.

Show that the $x$-coordinate of $P$ is $\dfrac13(2a+r)$. You are not required to
demonstrate a change in concavity.
""")

code(r"""
a, r, b = symbols('a r b')

q4_2 = ...       # the x-coordinate of the inflexion, in terms of a and r

cubic = (x - r)*(x**2 - 2*a*x + a**2 + b**2)
shapes = {a: (4, 2, 5, 1), r: (1, -2, 0, 3), b: (1, 4, 2, 2)}

verify_bend('4.2', q4_2, cubic, domain=(-8, 8), params=shapes)
""")

md(r"""
### 4.3 — *May 2022 TZ1 Paper 3 Q2(g)(ii), 1 mark*

The points $A(a,g(a))$ and $R(r,0)$ lie on the same curve.

Hence describe numerically the horizontal position of the point $P$ relative to
the horizontal positions of the points $R$ and $A$.

*Enter the $x$-coordinate of $P$ written as $r+k(a-r)$, that is as a fraction
$k$ of the way from $R$ to $A$.*
""")

code(r"""
q4_3 = ...       # the same x-coordinate written as r + k(a − r)

verify_bend('4.3', q4_3, cubic, domain=(-8, 8), params=shapes)
""")

md(r"""
### 4.4 — *May 2022 TZ1 Paper 3 Q2(h)(ii), 1 mark*

Consider the special case where $a=r$ and $b>0$.

State, in terms of $r$, the coordinates of the point $P$.
""")

code(r"""
q4_4 = ...       # the coordinates of the inflexion when a = r

same = (x - r)*(x**2 - 2*r*x + r**2 + b**2)

verify_bend('4.4', q4_4, same, domain=(-8, 8), coordinates=True,
            params={r: (1, -2, 3), b: (2, 1, 4)})
""")

md(r"""
### 4.5 — *May 2022 TZ2 Paper 3 Q1(b)(i), 1 mark*

Write down the coordinates of the two points of inflexion on the curve
$y^2=x^3+1$, where $x\ge-1$.

*The two branches are checked separately: give the upper one first.*
""")

code(r"""
q4_5a = ...      # the point of inflexion on y = +√(x³ + 1)
q4_5b = ...      # the point of inflexion on y = −√(x³ + 1)

verify_bend('4.5(a)', q4_5a, sqrt(x**3 + 1), domain=(-0.99, 3), coordinates=True)
verify_bend('4.5(b)', q4_5b, -sqrt(x**3 + 1), domain=(-0.99, 3), coordinates=True)
""")

md(r"""
### 4.6 — *May 2022 TZ2 Paper 3 Q1(e), 7 marks*

The curve $y^2=x^3+x$, $x\ge0$, has two points of inflexion which, by the
symmetry of the curve, share an $x$-coordinate.

Find the value of this $x$-coordinate, giving your answer in the form
$x=\sqrt{\dfrac{p\sqrt3+q}{r}}$ where $p,q,r\in\mathbb Z$.

*Exact value. The upper branch $y=\sqrt{x^3+x}$ carries it.*
""")

code(r"""
q4_6 = ...       # the x-coordinate of the points of inflexion

verify_bend('4.6', q4_6, sqrt(x**3 + x), domain=(0.01, 2))
""")

md(r"""
### 4.7 — *May 2023 TZ2 Paper 2 Q12(e), 2 marks*

The graph of $y=x\sqrt{\dfrac{9x^4-1}{2}}$ for $\dfrac{\sqrt3}{3}<x<1$ has a
point of inflexion at $P$.

By sketching the graph of an appropriate derivative of $y$, determine the
$x$-coordinate of $P$.
""")

code(r"""
q4_7 = ...       # the x-coordinate of the inflexion

verify_bend('4.7', q4_7, x*sqrt((9*x**4 - 1)/2), domain=(sqrt(3)/3 + 0.001, 1))
""")

md(r"""
### 4.8 — *November 2025 TZ1 Paper 1 Q9(d), 2 marks*

The function $f$ has $f'(x)=3x^2+12x-15$, and its second derivative is zero at
$x=c=-2$. The sign of $f''$ on either side of $c$ is $-$ then $+$.

State, with a reason, whether there is a point of inflexion on the graph of
$y=f(x)$ at $x=c$.
""")

code(r"""
q4_8 = ...       # the kind of point at x = c

verify_nature('4.8', q4_8, integrate(3*x**2 + 12*x - 15, x), -2, domain=(-9, 5))
""")

# ================================================================ § 5
md(r"""
---
# § 5. A family with a letter

**Two questions, 9 marks.** The same work, with a parameter instead of a
number, and the words *show that* at the end.
""")

md(r"""
### 5.1 — *November 2023 Paper 3 Q1(e), 5 marks*

Consider the family of curves $y=x^3+ax^2+b$ for $x\in\mathbb R$, $a\ne0$ and
$b\in\mathbb R$.

Show that the curve has a point of zero gradient at $P(0,b)$ and a point of
zero gradient at $Q\left(-\dfrac{2a}{3},\ \dfrac{4a^3}{27}+b\right)$.

*Enter both points as a list, in terms of `a` and `b`.*
""")

code(r"""
a, b = symbols('a b')

q5_1 = [...]     # the two points of zero gradient

verify_turning('5.1', q5_1, x**3 + a*x**2 + b, domain=(-8, 4),
               params={a: (3, 1, 2, 6), b: (1, 2, 5, 1)})
""")

md(r"""
### 5.2 — *May 2021 TZ1 Paper 3 Q1(d), 4 marks*

Consider $f(x)=x^3-3cx+2$ for $x\in\mathbb R$, where $c$ is a parameter. Given
that the graph of $y=f(x)$ has one local maximum point and one local minimum
point, show that

**(i)** the $y$-coordinate of the local maximum point is $2c^{3/2}+2$;

**(ii)** the $y$-coordinate of the local minimum point is $-2c^{3/2}+2$.

*Enter both points, maximum first, in terms of `c`.*
""")

code(r"""
c = symbols('c')

q5_2 = [...]     # the local maximum and the local minimum

verify_turning('5.2', q5_2, x**3 - 3*c*x + 2, domain=(-4, 4),
               params={c: (1, 4, Rational(1, 4), 2)})
""")

# ================================================================ § 6
md(r"""
---
# § 6. Which side of the axis

**Two questions, 2 marks.** A different question from the kind of point, and a
mark of its own.
""")

md(r"""
### 6.1 — *November 2023 Paper 3 Q1(f)(ii), 1 mark*

For the family $y=x^3+ax^2+b$ with $a>0$ and $b>0$, determine whether each of
$P(0,b)$ and $Q\left(-\frac{2a}{3},\frac{4a^3}{27}+b\right)$ is located above or
below the $x$-axis.
""")

code(r"""
q6_1 = [...]     # 'above' or 'below' for the two points, in order

verify_side('6.1', q6_1, x**3 + a*x**2 + b, [0, -2*a/3],
            params={a: (3, 1, 2, 6), b: (1, 2, 5, 1)})
""")

md(r"""
### 6.2 — *November 2023 Paper 3 Q1(g)(ii), 1 mark*

For the same family with $a<0$ and $b>0$, state the conditions on $a$ and $b$
that determine when $Q$ is below the $x$-axis.
""")

code(r"""
q6_2 = ...       # the condition on a and b

def below(a, b):
    place = [spot for spot in stationary(x**3 + a*x**2 + b, (-20, 20))
             if abs(spot[0]) > 1e-6]              # this is Q, the one away from 0
    return None if not place else place[0][1] < 0

verify_condition('6.2', q6_2, below, symbols('a b'), window=(-3, -0.25), steps=10)
""")

# ================================================================ § 7
md(r"""
---
# § 7. How many

**Three questions, 16 marks.** Not a question about points but about counting:
how many solutions $f'(x)=0$ has, and how many times the curve meets the axis.
""")

md(r"""
### 7.1 — *May 2021 TZ1 Paper 3 Q1(c), 4 marks*

For $f(x)=x^3-3cx+2$, with $f'(x)=3x^2-3c$, find the set of values of $c$ such
that the graph of $y=f(x)$ has

**(i)** a point of inflexion with zero gradient;

**(ii)** one local maximum point and one local minimum point;

**(iii)** no points where the gradient is equal to zero.
""")

code(r"""
c = symbols('c')

q7_1a = ...      # a point of inflexion with zero gradient
q7_1b = ...      # one local maximum and one local minimum
q7_1c = ...      # no points of zero gradient

family = x**3 - 3*c*x + 2

def kinds(value):
    return [word for _, _, word in stationary(family.subs(c, value), (-5, 5))]

verify_param_set('7.1(i)', q7_1a, lambda v: kinds(v) == ['inflexion'],
                 var=c, window=(-4, 4))
verify_param_set('7.1(ii)', q7_1b, lambda v: kinds(v) == ['maximum', 'minimum'],
                 var=c, window=(-4, 4))
verify_param_set('7.1(iii)', q7_1c, lambda v: kinds(v) == [], var=c, window=(-4, 4))
""")

md(r"""
### 7.2 — *May 2021 TZ1 Paper 3 Q1(e), 6 marks*

Hence, for $c>0$, find the set of values of $c$ such that the graph of
$y=f(x)=x^3-3cx+2$ has

**(i)** exactly one $x$-axis intercept;

**(ii)** exactly two $x$-axis intercepts;

**(iii)** exactly three $x$-axis intercepts.
""")

code(r"""
q7_2a = ...      # exactly one x-axis intercept
q7_2b = ...      # exactly two
q7_2c = ...      # exactly three

def meets(value, times):
    if value <= 0:
        return None                      # the question speaks only of c > 0
    return crossings(x**3 - 3*value*x + 2, (-30, 30)) == times

verify_param_set('7.2(i)', q7_2a, lambda v: meets(v, 1), var=c, window=(0, 4))
verify_param_set('7.2(ii)', q7_2b, lambda v: meets(v, 2), var=c, window=(0, 4))
verify_param_set('7.2(iii)', q7_2c, lambda v: meets(v, 3), var=c, window=(0, 4))
""")

md(r"""
### 7.3 — *May 2021 TZ1 Paper 3 Q1(f), 6 marks*

Consider the function $g(x)=x^3-3cx+d$ for $x\in\mathbb R$, where
$c,d\in\mathbb R$.

Find all conditions on $c$ and $d$ such that the graph of $y=g(x)$ has exactly
one $x$-axis intercept, explaining your reasoning.

*Write one condition joining the cases: `Or(..., ..., ...)`.*
""")

code(r"""
c, d = symbols('c d')

q7_3 = ...       # all conditions on c and d

def once(c, d):
    return crossings(x**3 - 3*c*x + d, (-30, 30)) == 1

verify_condition('7.3', q7_3, once, symbols('c d'), window=(-3, 3), steps=12)
""")

# ================================================================ § 8
md(r"""
---
# § 8. There are none

**Two questions, 8 marks.** Set the gradient to zero and find that nothing on
the curve satisfies it — either because the equation has no real solution, or
because its solutions lie outside the domain the question states.
""")

md(r"""
### 8.1 — *November 2022 Paper 1 Q7, 7 marks*

Consider the curve with equation $(x^2+y^2)y^2=4x^2$ where $x\ge0$ and
$-2<y<2$.

Show that the curve has no local maximum or local minimum points for $x>0$.

*The answer is the list of such points, and it is empty.*
""")

code(r"""
q8_1 = [...]     # every local maximum or minimum with x > 0

shape = curve(Eq((x**2 + y**2)*y**2, 4*x**2))

verify_turning('8.1', q8_1, shape, domain=(0.01, 8))
""")

md(r"""
### 8.2 — *May 2022 TZ2 Paper 3 Q1(d)(ii), 1 mark*

For the curve $y^2=x^3+x$ with $x\ge0$, part (d)(i) gives

$$\frac{dy}{dx}=\pm\frac{3x^2+1}{2\sqrt{x^3+x}},\qquad x>0$$

Hence deduce that the curve $y^2=x^3+x$ has no local minimum or maximum points.
""")

code(r"""
q8_2 = [...]     # every local maximum or minimum on the curve

verify_turning('8.2', q8_2, curve(Eq(y**2, x**3 + x)), domain=(0.01, 4))
""")

# ============================================================== решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1

**1.1** $f'(x)=4x^2-16=0$ gives $x=\pm2$; with $p>0$, $p=2$ and
$q=\frac{32}{3}-32=\boxed{-\frac{64}{3}}$.

**1.2** $f'(x)=-2\sin2x\,e^{\cos2x}=0$ when $\sin2x=0$, that is
$x=0,\frac\pi2,\pi$ inside the interval:
$\boxed{(0,e),\ \left(\frac\pi2,\frac1e\right),\ (\pi,e)}$.

**1.3** From the calculator, $A=\boxed{(0.709,0.640)}$
$(0.708519\ldots,0.639580\ldots)$.

**1.4** Implicitly, $8x+2y\frac{dy}{dx}-24+4\frac{dy}{dx}=0$, so
$\frac{dy}{dx}=\frac{4(3-x)}{y+2}$, which is zero at $x=3$. Then
$36+y^2-72+4y+20=0$, that is $y^2+4y-16=0$ and $y=-2\pm2\sqrt5$. The maximum
takes the upper root: $\boxed{(3,\,-2+2\sqrt5)}\approx(3,2.47)$.

**1.5** $\boxed{(-1.94,1.20)}$ is the local maximum and $\boxed{(1.94,-1.20)}$
the local minimum $(\pm1.94347\ldots,\mp1.20113\ldots)$.

**1.6** $f(x_1)=12x_1-x_1^2$ is greatest at $x_1=\boxed{6}$ by symmetry, and
$f(6)=6\cdot6=\boxed{36}$.

**1.7** $s'(t)=\dfrac{4.3\cdot3\cos\sqrt{3t+5}}{2\sqrt{3t+5}}=0$ when
$\cos\sqrt{3t+5}=0$. Inside $0\le t\le10$ the only solution is
$\sqrt{3t+5}=\frac{3\pi}{2}$, giving $\boxed{q=5.74}$ $(5.73553\ldots)$.

**1.8** $f'(x)=\dfrac{1-2x^2}{\sqrt{1-x^2}}=0$ at $x=\pm\frac1{\sqrt2}$, where
$f=\pm\frac12$; at the ends $f(\pm1)=0$. So
$\boxed{-\frac12\le y\le\frac12}$.

---

## § 2

**2.1** $f''(x)=\left(4\sin^22x-4\cos2x\right)e^{\cos2x}$, so $f''(0)=-4e<0$,
$f''\!\left(\frac\pi2\right)=\frac4e>0$ and $f''(\pi)=-4e<0$:
$\boxed{\text{maximum, minimum, maximum}}$.

**2.2** $\dfrac{d^2y}{dx^2}=\boxed{6x+2a}$. At $x=0$ it is $2a>0$, so $P$ is a
$\boxed{\text{minimum}}$; at $x=-\frac{2a}{3}$ it is $-2a<0$, so $Q$ is a
$\boxed{\text{maximum}}$.

**2.3** With $a<0$ the value at $x=0$ is $2a<0$, so $P$ is a
$\boxed{\text{maximum}}$.

**2.4** $V=4x^3-2(a+b)x^2+abx$, so
$\dfrac{d^2V}{dx^2}=\boxed{24x-4(a+b)}$, and at $x_m$

$$24\cdot\frac{(a+b)-\sqrt{a^2-ab+b^2}}{6}-4(a+b)=-4\sqrt{a^2-ab+b^2}<0$$

so $x_m$ gives a $\boxed{\text{local maximum}}$.

---

## § 3

**3.1** $f'$ changes from positive to negative at $x=a$, so the curve rises and
then falls: $\boxed{\text{a local maximum}}$.

**3.2** $f_n'(-1)=n(-1)^{n-1}(a+2)(a+1)^{n-1}$, and $(a+2)$ and $(a+1)^{n-1}$
are positive.

**(i)** For even $n$, $n-1$ is odd and $(-1)^{n-1}=-1$, so $f_n'(-1)<0$; with
$f_n'(0)=0$ and $f_n'\!\left(\frac a4\right)>0$ the gradient runs $-,0,+$ and
$(0,0)$ is a $\boxed{\text{local minimum}}$.

**(ii)** For odd $n$, $n-1$ is even and $f_n'(-1)>0$; the gradient runs $+,0,+$
and $(0,0)$ is a $\boxed{\text{point of inflexion with zero gradient}}$.

---

## § 4

**4.1** The local minimum of $f'$ (or the zero of $f''$) is at
$\boxed{x=-1.60}$ $(-1.59537\ldots)$.

**4.2** $g'(x)=2(x-r)(x-a)+x^2-2ax+a^2+b^2$, so
$g''(x)=2(x-a)+2(x-r)+2x-2a=6x-2r-4a$, which vanishes at
$\boxed{x=\frac13(2a+r)}$.

**4.3** $\frac13(2a+r)=r+\frac23(a-r)$, so $P$ is
$\boxed{\frac23}$ of the horizontal distance from $R$ to $A$.

**4.4** With $a=r$ the formula gives $x=\frac13(2r+r)=r$, and
$g(r)=(r-r)\left((r-r)^2+b^2\right)=0$: $\boxed{P(r,0)}$.

**4.5** The curve is $y=\pm\sqrt{x^3+1}$, and each branch bends the other way
across $x=0$: $\boxed{(0,1)}$ and $\boxed{(0,-1)}$.

**4.6** Differentiating $2y\frac{dy}{dx}=3x^2+1$ again,
$2\left(\frac{dy}{dx}\right)^2+2y\frac{d^2y}{dx^2}=6x$, so at an inflexion
$\left(\frac{dy}{dx}\right)^2=3x$ and

$$\frac{(3x^2+1)^2}{4(x^3+x)}=3x\ \Longrightarrow\ 3x^4+6x^2-1=0
\ \Longrightarrow\ x^2=\frac{2\sqrt3-3}{3}$$

$$x=\boxed{\sqrt{\frac{2\sqrt3-3}{3}}}\approx0.393\qquad(p=2,\ q=-3,\ r=3)$$

**4.7** The zero of $\frac{d^2y}{dx^2}$ is at $\boxed{x=0.656}$
$(0.655996\ldots)$.

**4.8** $f''$ changes sign at $x=c$, so the concavity changes:
$\boxed{\text{yes, a point of inflexion}}$. "Because $f''(c)=0$" alone earns R0.

---

## § 5

**5.1** $\frac{dy}{dx}=3x^2+2ax=x(3x+2a)$, zero at $x=0$ and $x=-\frac{2a}{3}$.
At $x=0$, $y=b$; at $x=-\frac{2a}{3}$,

$$y=-\frac{8a^3}{27}+\frac{4a^3}{9}+b=\boxed{\frac{4a^3}{27}+b}$$

**5.2** $f'(x)=3x^2-3c=0$ gives $x=\pm\sqrt c$, and the maximum is the left one:

$$f(-\sqrt c)=-c^{3/2}+3c^{3/2}+2=\boxed{2c^{3/2}+2},\qquad
f(\sqrt c)=\boxed{-2c^{3/2}+2}$$

---

## § 6

**6.1** $b>0$ puts $P$ above the axis, and $\frac{4a^3}{27}+b>0$ for $a>0$ puts
$Q$ above it too: $\boxed{\text{above, above}}$.

**6.2** $Q$ is below the axis exactly when its $y$-coordinate is negative:
$\boxed{\frac{4a^3}{27}+b<0}$.

---

## § 7

**7.1** $3x^2=3c$ means $x^2=c$.

**(i)** One repeated root, the gradient touching zero: $\boxed{c=0}$.
**(ii)** Two distinct roots: $\boxed{c>0}$.
**(iii)** No real roots: $\boxed{c<0}$.

**7.2** The maximum value $2c^{3/2}+2$ is always positive, so the minimum value
decides.

**(i)** $-2c^{3/2}+2>0$, that is $\boxed{0<c<1}$.
**(ii)** $-2c^{3/2}+2=0$, that is $\boxed{c=1}$.
**(iii)** $-2c^{3/2}+2<0$, that is $\boxed{c>1}$.

**7.3** For $c\le0$ the derivative $3x^2-3c$ is never negative, so $g$ never
turns and meets the axis once whatever $d$ is. For $c>0$ the vertices are
$\left(-\sqrt c,2c^{3/2}+d\right)$ and $\left(\sqrt c,-2c^{3/2}+d\right)$, and
one intercept means both lie on the same side:

$$\boxed{c\le0,\quad\text{or}\quad d>2c^{3/2},\quad\text{or}\quad d<-2c^{3/2}}$$

---

## § 8

**8.1** Writing the equation as $x^2y^2+y^4=4x^2$ and differentiating,

$$2xy^2+2x^2y\frac{dy}{dx}+4y^3\frac{dy}{dx}=8x$$

At a maximum or minimum $\frac{dy}{dx}=0$, so $2xy^2=8x$ and $x=0$ or
$y=\pm2$. The domain says $x>0$ and $-2<y<2$, so nothing survives:
$\boxed{\text{there are none}}$.

**8.2** $\frac{dy}{dx}=0$ needs $3x^2+1=0$, and $3x^2+1\ge1$ for every real
$x$. So $\boxed{\text{there are none}}$.
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
