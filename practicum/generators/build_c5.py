"""Собирает практикум C5: векторы, прямые и углы между ними.

Тридцать первый практикум серии и первый по векторам. Тема разрезана по
действию, а не по разметке: geometry.vectors и geometry.vectors_3d делят
вопросы не по тому, что с векторами делают, и C5 берёт из обеих всё, что
обходится без плоскости и без векторного произведения, — 96 баллов из 182
и 52 из 216.

Лестница из восьми приёмов идёт от точки к движению. Сначала точки и
отрезки: AB = b − a, середина, четвёртая вершина, длина. Потом скалярное
произведение и угол между векторами. Потом прямая: её уравнение, угол
между двумя прямыми, их общая точка и вопрос, есть ли она вообще. И
напоследок движение по прямой — скорость, курс, время в точке.

Двадцать четвёртое понятие равенства ответов: **прямая — множество
точек, а точка — там, где выполнены условия вопроса**. Уравнение прямой
принимается с любой её точкой и любым параллельным направлением; искомое,
заданное словами, проверка находит сама из условий, записанных как в
билете: parallelogram(A, B, C, D), perpendicular(q, a), meet(L1, L2).

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_c5.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/geometry/practicum-c5-vectors.ipynb')

TRIGGER = {1: 'points', 2: 'scalar', 3: 'angle', 4: 'line', 5: 'line_angle',
           6: 'meet', 7: 'skew', 8: 'motion', 9: 'points', 10: 'scalar',
           11: 'line', 12: 'motion'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '(3, 0, 2)',
    'q1b': '(0, -3, 2)',
    'q2a': 'Interval(2, 28)',
    'q2b': 'vec(Rational(-24, 13), Rational(10, 13))',
    'q2c': 'vec(Rational(75, 13), Rational(180, 13))',
    'q3a_OM': 'a + k*c',
    'q3a_MC': '(1 - k)*c - a',
    'q3b': '2*(1 - 2*k)*la**2*cos(theta) - la**2 + 4*k*(1 - k)*la**2',
    'q4a': '10.3',
    'q4b': '0.798',
    'q5a_i': '-5*p - 42',
    'q5a_ii': '-8*p - 54',
    'q5b': '4.79',
    'q6a': 'vec(1, -2, 0) + lam*vec(2, 3, 1)',
    'q6b': '(5, 4, 2)',
    'q7a': 'vec(-1, 0, 3) + lam*vec(2, 1, -1)',
    'q7b': '[-4 + 3*sqrt(2), -4 - 3*sqrt(2)]',
    'q7c_k': '2',
    'q7c_A': '(a/(a - 2), (a - 1)/(a - 2), (2*a - 5)/(a - 2))',
    'q8a': 'vec(-1, 1, -13) + lam*vec(7, 1, 2)',
    'q8b': 'vec(2, -4, 2) + mu*vec(5, -2, -1)',
    'q8c': "'skew'",
    'q8c_pair': '[-1, -2]',
    'q9': '[Rational(-3, 2), 14]',
    'q10a_AB': 'vec(k - 1, -4, -2)',
    'q10a_AC': 'vec(4, -2, -1)',
    'q10b': '9',
    'q10ci': 'vec(1, 2, 3) + lam*vec(4, -2, -1)',
    'q10cii': "'skew'",
    'q10cii_pair': '[Rational(1, 4), Rational(1, 2)]',
    'q11a': "'063'",
    'q11b_A': '7.48',
    'q11b_B': '4.90',
    'q11c': '40.2',
    'q11d_i': '(7, 3, 9)',
    'q11d_ii': '0.5',
    'q12a': '108',
    'q12b': '8.45',
    'qt_pair': '[2, -1]',
    'qt': '(5, 8, 9)',
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
# C5 — Vectors: points, lines and the angles between them

**137 marks of the archive, eight techniques, twelve tasks.** Everything the
archive asks about vectors without a plane and without a vector product,
from May 2021 to November 2025: points and lengths, the scalar product, the
angle between two vectors, the equation of a line, the angle between two
lines, where two lines meet — and whether they meet at all — and motion
along a line.

Paper 1 and Paper 2 share it almost equally, 58 and 71 marks, and on both
the work is the same: a system of two equations and a check of the third.

## The one idea

A line is **a set of points**, and every question about it is a question
about which points belong to it.

$$\mathbf r=\mathbf a+\lambda\mathbf b$$

is one point $\mathbf a$ of the line and one step $\mathbf b$ along it. Any
other point of the line and any multiple of the step describe **the same
line**.

## And what follows from it

| the question asks | what it is |
|---|---|
| a vector equation of a line | any point on it, any direction along it |
| the angle between two lines | the angle between the directions, the acute one |
| the point of intersection | a point that belongs to both sets |
| *show that the lines are skew* | no common point, and the directions are not parallel |

## How the checks work

They do not know the answers. A line is handed to them **the way the
question prints it**, and a point is handed **the conditions** that fix it:

```python
L1 = cartesian((x + 1)/2, y, 3 - z)
verify_line('7a', q7a, L1)

D = unknown('D', 3)
verify_find('1a', q1a, D, [parallelogram(A, B, C, D)])
```

The first is *"is your line the set of points $(x+1)/2=y=3-z$?"* — any point
of it and any parallel direction pass. The second is *"does your $D$ make
$ABCD$ a parallelogram?"*: the check solves the condition itself.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| the point $(-1,2,0)$ for $\frac{x-1}2=\frac{y+2}3=z$ | the point has the wrong signs |
| the position vector of $B$ as the direction | not a step along the line |
| $\lambda$ of one line put into the other | each line has its own parameter |
| the obtuse angle between the directions | between lines, take the acute one |
| the angle between $\overrightarrow{OB}$ and $\overrightarrow{OC}$ | the angle at $V$ is between the edges from $V$ |
| *skew* for parallel lines | parallel lines are not skew |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | points and lengths, the scalar product | 1–3 |
| 🟡 | angles, the equation of a line, intersection | 4–7 |
| 🔴 | parallel, meeting or skew; motion along a line | 8–12 |

Every task is a real past-paper question, cited.

**79 of the 137 marks are on a calculator paper, and the calculator does
little of the work.** It extracts a square root, takes an inverse cosine,
solves one equation for $p$. The equation of a line, the intersection and
*skew* are the same system of equations on either paper.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, line, cartesian, through, unknown

language('en')                 # this notebook is in English, and so are the checks

# vec(1, -4, 0) is a vector or a point; dot(u, v), mag(v), distance(A, B), angle(u, v).
# A line: line(vec(1, 2, -3) + s*vec(2, 3, 6)), through(A, B), cartesian((x - 1)/2, y, 3 - z).
# lam and mu are the Greek letters λ and μ; z is the third coordinate.
# unknown('D', 3) is a point the question asks for, and the checks find it themselves.

print('ready; sympy', sp.__version__)
A, B = vec(2, -1, 3), vec(6, 1, -1)
print('AB:          ', B - A)
print('|AB|:        ', mag(B - A))
print('the line AB: ', through(A, B))
""")

md(r"""
---
## Map of the eight techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | points and lengths | *find the coordinates of $D$*, *find $BV$*, *the centre and the radius* | $\overrightarrow{AB}=\mathbf b-\mathbf a$, $\lvert\mathbf v\rvert$ |
| 2 | the scalar product | *perpendicular*, *a right angle*, *$\overrightarrow{OM}\cdot\overrightarrow{MC}=0$* | $\mathbf a\cdot\mathbf b=a_1b_1+a_2b_2+a_3b_3=0$ |
| 3 | the angle between vectors | *the size of $B\hat VC$*, *the angle between $\mathbf p$ and $\mathbf n$* | $\cos\theta=\dfrac{\mathbf a\cdot\mathbf b}{\lvert\mathbf a\rvert\lvert\mathbf b\rvert}$ |
| 4 | the equation of a line | *find a vector equation of $L_1$*, *passes through $A$ and $B$* | a point and a direction |
| 5 | the angle between lines | *the acute angle between the lines* | the directions only, $\lvert\cos\theta\rvert$ |
| 6 | the point of intersection | *find where $L_1$ and $L_2$ intersect* | two parameters, two equations, the third checked |
| 7 | parallel, meeting or skew | *do not intersect*, *show that the lines are skew*, *perpendicular and intersect* | directions first, then the system |
| 8 | motion along a line | *speed*, *bearing*, *the time between the arrivals*, *the angle of descent* | $\mathbf r=\mathbf r_0+t\mathbf v$ |

Techniques 1–3 are about vectors alone. Techniques 4–7 put a vector to work
as the direction of a line: first the line itself, then two lines at once.
Technique 8 is a line walked in time.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Points, lengths and the scalar product

## Theory: from points to vectors

Take $A(2,-1,3)$, $B(6,1,-1)$ and $C(3,4,0)$.

**A vector between two points is the end minus the start:**

$$\overrightarrow{AB}=\mathbf b-\mathbf a=\begin{pmatrix}4\\2\\-4\end{pmatrix},\qquad \lvert\overrightarrow{AB}\rvert=\sqrt{16+4+16}=6$$

$\overrightarrow{BA}$ is the same vector the other way: $-\overrightarrow{AB}$.

**The midpoint** of $[AB]$ is the average of the ends, $(4,0,1)$ — not half of
$\overrightarrow{AB}$, which is a step, not a place.

**A parallelogram $ABCD$** has its vertices in order, so
$\overrightarrow{AB}=\overrightarrow{DC}$: the fourth vertex is
$\mathbf d=\mathbf a+\mathbf c-\mathbf b=(-1,2,4)$. The order matters:
$\mathbf a+\mathbf b-\mathbf c$ is also a parallelogram, but its vertices
read $ABDC$.

**Three points on one line** give parallel vectors. $P(1,0,2)$, $Q(3,1,5)$,
$R(r,3,11)$: $\overrightarrow{PR}=(r-1,\,3,\,9)$ must be $3\overrightarrow{PQ}=(6,3,9)$,
so $r=7$.

**A length and a direction.** With $\lvert\mathbf a\rvert=5$ and
$\lvert\mathbf b\rvert=10$, $\lvert\mathbf a+\mathbf b\rvert$ is largest when
$\mathbf b$ points the same way as $\mathbf a$ ($15$) and smallest when it
points the opposite way ($5$). In a *given that it is a minimum* question
the answer is the vector $\mathbf a+\mathbf b$, not $\mathbf b$.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ3 Paper 1 Q11(a), (b), 4 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D$ form a
parallelogram, $ABCD$, where $D$ is diagonally opposite $B$.

**(a)** Find the coordinates of $D$.

The diagonals of the parallelogram, $[AC]$ and $[BD]$, intersect at point $E$.

**(b)** Find the coordinates of $E$.

*The check for (b) finds $D$ itself, so a slip in (a) costs (a) only.*
""")

code(r"""
q1a = ...        # D, as (x, y, z)
q1b = ...        # E

A, B, C = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4)
D, E = unknown('D', 3), unknown('E', 3)

verify_find('1a', q1a, D, [parallelogram(A, B, C, D)])
verify_find('1b', q1b, E, [parallelogram(A, B, C, D), on(E, A, C), on(E, B, D)])
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ1 Paper 2 Q7, 9 marks*

Consider the vectors $\mathbf a$ and $\mathbf b$ such that
$\mathbf a=\begin{pmatrix}12\\-5\end{pmatrix}$ and $\lvert\mathbf b\rvert=15$.

**(a)** Find the possible range of values for $\lvert\mathbf a+\mathbf b\rvert$.

Consider the vector $\mathbf p$ such that $\mathbf p=\mathbf a+\mathbf b$.

**(b)** Given that $\lvert\mathbf a+\mathbf b\rvert$ is a minimum, find $\mathbf p$.

Consider the vector $\mathbf q$ such that $\mathbf q=\begin{pmatrix}x\\y\end{pmatrix}$,
where $x,y\in\mathbb R^+$.

**(c)** Find $\mathbf q$ such that $\lvert\mathbf q\rvert=\lvert\mathbf b\rvert$ and $\mathbf q$
is perpendicular to $\mathbf a$.

*In (a) answer `Interval(lowest, highest)`. The checks let $\mathbf b$ run round
the whole circle of radius $15$.*
""")

code(r"""
q2a = ...        # Interval(lowest, highest)
q2b = ...        # p, as vec(...)
q2c = ...        # q, as vec(...)

theta = symbols('theta')
a = vec(12, -5)
b = 15*vec(cos(theta), sin(theta))      # every b with |b| = 15
q = unknown('q', 2)

verify_extent('2a', q2a, mag(a + b), theta, Interval(0, 2*pi))
verify_optimum('2b', q2b, a + b, theta, Interval(0, 2*pi), 'min')
verify_find('2c', q2c, q, [perpendicular(q, a), length(q, 15), q[0] > 0, q[1] > 0])
""")

# ================================================================= теория 2
md(r"""
## Theory: the scalar product

**By components** it is a number, not a vector:

$$\mathbf u\cdot\mathbf v=u_1v_1+u_2v_2+u_3v_3$$

For $\mathbf u=(2,-1,3)$ and $\mathbf v=(4,5,-1)$ it is $8-5-3=0$: **zero
means perpendicular**, and that is the whole content of *perpendicular* and
*a right angle* in a question.

**A perpendicular vector of a given length.** Perpendicular to $(8,15)$ is
the direction $(15,-8)$ — swap and change one sign. Its length is $17$; for
a length of $34$ double it: $(30,-16)$, or $(-30,16)$ if the question wants
the other one. Two conditions, two unknowns, and the question's
restriction picks the sign.

**With letters for vectors** expand like brackets, remembering
$\mathbf a\cdot\mathbf a=\lvert\mathbf a\rvert^2$ and
$\mathbf a\cdot\mathbf b=\lvert\mathbf a\rvert\lvert\mathbf b\rvert\cos\theta$:

$$(\mathbf a+\mathbf b)\cdot(\mathbf a-\mathbf b)=\lvert\mathbf a\rvert^2-\lvert\mathbf b\rvert^2$$

— so the diagonals of a rhombus, where $\lvert\mathbf a\rvert=\lvert\mathbf b\rvert$,
are perpendicular.

**A right angle at a vertex** uses the vectors **from that vertex**. For
$C(1,1)$, $A(4,5)$, $B(5,-2)$: $\overrightarrow{CA}=(3,4)$,
$\overrightarrow{CB}=(4,-3)$, and $12-12=0$.
""")

md(r"""
### Task 3 🟢 — *May 2023 TZ2 Paper 1 Q9(a), (b), 5 marks*

The following diagram shows parallelogram $OABC$ with $\overrightarrow{OA}=\mathbf a$,
$\overrightarrow{OC}=\mathbf c$ and $\lvert\mathbf c\rvert=2\lvert\mathbf a\rvert$, where
$\lvert\mathbf a\rvert\ne0$. *(In the diagram $O$ and $C$ are the bottom side,
$A$ and $B$ the top side, and the angle $O\hat MC$ is marked as a right angle.)*

The angle between $\overrightarrow{OA}$ and $\overrightarrow{OC}$ is $\theta$, where $0<\theta<\pi$.

Point $M$ is on $[AB]$ such that $\overrightarrow{AM}=k\overrightarrow{AB}$, where
$0\le k\le1$ and $\overrightarrow{OM}\cdot\overrightarrow{MC}=0$.

**(a)** Express $\overrightarrow{OM}$ and $\overrightarrow{MC}$ in terms of $\mathbf a$ and $\mathbf c$.

**(b)** Hence, use a vector method to show that
$\lvert\mathbf a\rvert^2(1-2k)\big(2\cos\theta-(1-2k)\big)=0$.

*For (b) enter $\overrightarrow{OM}\cdot\overrightarrow{MC}$ in terms of $\lvert\mathbf a\rvert$
(`la`), $\theta$ and $k$ — the line before you factorise. The checks draw the
parallelogram for several $\lvert\mathbf a\rvert$, $\theta$ and $k$. Part (c) is in C3.*
""")

code(r"""
la, theta = symbols('|a| theta', positive=True)
a = la*vec(1, 0)
c = 2*la*vec(cos(theta), sin(theta))    # |c| = 2|a|, and the angle between them is theta

q3a_OM = ...     # OM in terms of a and c
q3a_MC = ...     # MC in terms of a and c
q3b = ...        # OM · MC in terms of la, theta and k

O = vec(0, 0)
B, M = unknown('B', 2), unknown('M', 2)
figure = [parallelogram(O, a, B, c, names='OABC'), Eq(M - a, k*(B - a))]

verify_find('3a OM', q3a_OM, M - O, figure)
verify_find('3a MC', q3a_MC, c - M, figure)
verify_find('3b', q3b, dot(M - O, c - M), figure)
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. Angles, lines and where they meet

## Theory: the angle between two vectors

$$\cos\theta=\frac{\mathbf a\cdot\mathbf b}{\lvert\mathbf a\rvert\,\lvert\mathbf b\rvert},\qquad 0\le\theta\le\pi$$

**The angle at a vertex uses the edges from that vertex.** For the triangle
$P(1,0,0)$, $Q(0,2,0)$, $R(0,0,3)$ the angle at $P$ is between
$\overrightarrow{PQ}=(-1,2,0)$ and $\overrightarrow{PR}=(-1,0,3)$:

$$\cos Q\hat PR=\frac{1}{\sqrt5\sqrt{10}}=0.141,\qquad Q\hat PR=81.9^\circ$$

The position vectors $\overrightarrow{OQ}$ and $\overrightarrow{OR}$ are
perpendicular, and $90^\circ$ is the angle at the origin — not at $P$.

**Divide by both lengths.** $\mathbf a\cdot\mathbf b$ alone is not
$\cos\theta$; it is $\cos\theta$ times two lengths.

**A letter inside a vector** turns the formula into an equation. When two
angles are equal, set the **cosines** equal. Squaring both sides is
tempting and dangerous: it also solves "the cosines are equal in size and
opposite in sign", and that extra root answers a different question.

**Units.** Paper 2 accepts radians or degrees unless the question names
one; three significant figures either way.
""")

md(r"""
### Task 4 🟡 — *November 2023 TZ1 Paper 2 Q1, 6 marks*

The following diagram shows a pyramid with vertex $V$ and rectangular base
$OABC$.

Point $B$ has coordinates $(6,8,0)$, point $C$ has coordinates $(6,0,0)$ and
point $V$ has coordinates $(3,4,9)$.

**(a)** Find $BV$.

**(b)** Find the size of $B\hat VC$.
""")

code(r"""
q4a = ...        # BV
q4b = ...        # the angle BVC

B, C, V = vec(6, 8, 0), vec(6, 0, 0), vec(3, 4, 9)

verify_find('4a', q4a, distance(B, V))
verify_angle('4b', q4b, B, V, C)
""")

md(r"""
### Task 5 🟡 — *May 2025 TZ3 Paper 2 Q6, 8 marks*

Consider the vectors $\mathbf a=\begin{pmatrix}-5\\7\end{pmatrix}$,
$\mathbf b=\begin{pmatrix}-8\\9\end{pmatrix}$ and
$\mathbf c=\begin{pmatrix}p\\-6\end{pmatrix}$, where $p\in\mathbb R$.

**(a)** Find an expression, in terms of $p$, for **(i)** $\mathbf a\cdot\mathbf c$;
**(ii)** $\mathbf b\cdot\mathbf c$.

The angle between $\mathbf a$ and $\mathbf c$ is equal to the angle between
$\mathbf b$ and $\mathbf c$.

**(b)** Find the value of $p$.
""")

code(r"""
p = symbols('p')

q5a_i = ...      # a · c in terms of p
q5a_ii = ...     # b · c in terms of p
q5b = ...        # p

a, b, c = vec(-5, 7), vec(-8, 9), vec(p, -6)

verify_find('5a(i)', q5a_i, dot(a, c))
verify_find('5a(ii)', q5a_ii, dot(b, c))
verify_find('5b', q5b, p, [Eq(angle(a, c), angle(b, c))])
""")

# ================================================================= теория 4
md(r"""
## Theory: the equation of a line

$$\mathbf r=\mathbf a+\lambda\mathbf b$$

— a point $\mathbf a$ on the line and a direction $\mathbf b$ along it.

**Through two points** $A(2,0,-1)$ and $B(5,1,1)$: the direction is
$\overrightarrow{AB}=(3,1,2)$, the point is either of them:

$$\mathbf r=\begin{pmatrix}2\\0\\-1\end{pmatrix}+\lambda\begin{pmatrix}3\\1\\2\end{pmatrix}$$

The position vector $(5,1,1)$ is a place on the line, not a step along it.

**From the Cartesian form** set every part equal to $\lambda$:

$$\frac{x+3}{2}=\frac{y-1}{5}=4-z=\lambda\quad\Longrightarrow\quad x=-3+2\lambda,\; y=1+5\lambda,\; z=4-\lambda$$

so the point is $(-3,1,4)$ — **the signs flip** — and the direction is
$(2,5,-1)$: in $4-z$ the coefficient of $z$ is $-1$.

**A point on a line** gives one value of the parameter. Is $(8,2,3)$ on the
line through $A$ and $B$? $2+3\lambda=8$ gives $\lambda=2$, and the other two
components agree: $0+2=2$, $-1+4=3$. Yes, at $\lambda=2$.

> **Write "$\mathbf r=$".** The markscheme gives A0 for the vector without it.
""")

md(r"""
### Task 6 🟡 — *May 2025 TZ2 Paper 1 Q2, 5 marks*

The line $L_1$ is defined by the Cartesian equation $\dfrac{x-1}{2}=\dfrac{y+2}{3}=z$.

**(a)** Find a vector equation of $L_1$.

A second line $L_2$ is defined by the vector equation
$\mathbf r=\begin{pmatrix}0\\4\\-8\end{pmatrix}+t\begin{pmatrix}1\\0\\2\end{pmatrix}$, where $t\in\mathbb R$.

**(b)** Find the coordinates of the point where $L_1$ and $L_2$ intersect.

*Enter a line as `vec(point) + lam*vec(direction)`.*
""")

code(r"""
q6a = ...        # a vector equation of L1
q6b = ...        # the point of intersection

L1 = cartesian((x - 1)/2, (y + 2)/3, z)
L2 = line(vec(0, 4, -8) + t*vec(1, 0, 2))

verify_line('6a', q6a, L1)
verify_meet('6b', q6b, L1, L2)
""")

# ================================================================= теория 5
md(r"""
## Theory: the angle between two lines

The angle between two lines is the angle between **their directions** — the
points on them do not enter at all — and it is the **acute** one:

$$\cos\theta=\frac{\lvert\mathbf d_1\cdot\mathbf d_2\rvert}{\lvert\mathbf d_1\rvert\,\lvert\mathbf d_2\rvert}$$

For directions $(1,2,2)$ and $(2,-1,-2)$: $\mathbf d_1\cdot\mathbf d_2=-4$ and both
lengths are $3$. The formula without the modulus gives $116.4^\circ$ — the
angle between the arrows; the lines meet at $180^\circ-116.4^\circ=63.6^\circ$.

**A letter in a direction.** The acute angle between $(1,1,0)$ and $(0,1,c)$
is $60^\circ$:

$$\frac{1}{\sqrt2\sqrt{1+c^2}}=\frac12\quad\Longrightarrow\quad 1+c^2=2\quad\Longrightarrow\quad c=\pm1$$

The modulus becomes a square, and **both** roots are answers: the question
asked for an acute angle, and each of them gives one.

## Theory: where two lines meet

**Give each line its own parameter.** Even if the question calls both $t$,
the point of intersection is reached at different values.

$L_1:\ \mathbf r=(1,2,0)+\lambda(1,-1,2)$ and $L_2:\ \mathbf r=(4,0,7)+\mu(0,1,1)$.

1. **Equate the components** — three equations, two unknowns:
   $1+\lambda=4$, $\;2-\lambda=\mu$, $\;2\lambda=7+\mu$.
2. **Solve two of them:** $\lambda=3$, $\mu=-1$.
3. **Check the third:** $2\cdot3=6$ and $7+(-1)=6$ — it holds, so the lines meet.
4. **Substitute into the right line:** $\lambda=3$ into $L_1$ gives $(4,-1,6)$.

Putting $\lambda=3$ into $L_2$ gives $(4,3,10)$ — a point, but not on $L_1$.

**A letter in a direction** makes the parameter a fraction in that letter;
the value that makes its denominator zero is the one where the lines have
no unique point.
""")

md(r"""
### Task 7 🟡 — *May 2021 TZ1 Paper 1 Q11, 19 marks*

Consider the line $L_1$ defined by the Cartesian equation $\dfrac{x+1}{2}=y=3-z$.

**(a)** **(i)** Show that the point $(-1,0,3)$ lies on $L_1$.
**(ii)** Find a vector equation of $L_1$.

Consider a second line $L_2$ defined by the vector equation
$\mathbf r=\begin{pmatrix}0\\1\\2\end{pmatrix}+t\begin{pmatrix}a\\1\\-1\end{pmatrix}$,
where $t\in\mathbb R$ and $a\in\mathbb R$.

**(b)** Find the possible values of $a$ when the acute angle between $L_1$ and $L_2$ is $45^\circ$.

It is given that the lines $L_1$ and $L_2$ have a unique point of intersection, $A$, when $a\ne k$.

**(c)** Find the value of $k$, and find the coordinates of the point $A$ in terms of $a$.

*Paper 1: (b) wants exact values, all of them. The check for (c) tries several $a$.*
""")

code(r"""
a = symbols('a')

q7a = ...        # a vector equation of L1
q7b = [...]      # all possible values of a, exact
q7c_k = ...      # k
q7c_A = ...      # A in terms of a

L1 = cartesian((x + 1)/2, y, 3 - z)
L2 = line(vec(0, 1, 2) + t*vec(a, 1, -1), t)

verify_line('7a', q7a, L1)
verify_find('7b', q7b, a, [Eq(angle(L1, L2), pi/4)], exact=True)
verify_find('7c k', q7c_k, a, [no_unique_meet(L1, L2)])
verify_meet('7c A', q7c_A, L1, L2)
""")

# ================================================================= теория 6
md(r"""
---
# 🔴 Part 3. Parallel, meeting or skew — and motion along a line

## Theory: three ways two lines can sit

In a plane two lines either meet or are parallel. In space there is a third
way: **skew** — not parallel, and still no common point.

**Look at the directions first.** $(1,-1,2)$ and $(-2,2,-4)$ are multiples:
the lines are parallel (or the same line, if a point of one lies on the
other), and there is nothing to solve.

**Not parallel — solve two components, test the third.**
$L_1:\ \mathbf r=(1,2,0)+\lambda(1,-1,2)$ and $L_3:\ \mathbf r=(2,0,1)+\mu(1,1,0)$:

$$1+\lambda=2+\mu,\qquad 2-\lambda=\mu\quad\Longrightarrow\quad\lambda=\tfrac32,\ \mu=\tfrac12$$

and the third component: $2\lambda=3$ but $1=1$. It fails: no common point.

> **Skew needs both reasons.** The markscheme gives R1 for *not parallel*
> and R1 for the contradiction. Parallel lines never meet either — and they
> are not skew.

**Conditions with letters.** *Perpendicular* is
$\mathbf d_1\cdot\mathbf d_2=0$; *intersect* is "the system of components has a
solution". Write both and solve them together: the scalar product usually
gives one letter at once, and the components give the rest.
""")

md(r"""
### Task 8 🔴 — *November 2025 TZ3 Paper 1 Q10(a)–(c), 8 marks*

The point $P(-1,1,-13)$ lies on the line $L_1$. The line $L_1$ has a direction
vector $\begin{pmatrix}7\\1\\2\end{pmatrix}$.

**(a)** Write down a vector equation for $L_1$ in the form $\mathbf r=\mathbf a+\lambda\mathbf b$.

**(b)** Find a vector equation for line $L_2$ in the form $\mathbf s=\mathbf c+\mu\mathbf d$,
given that $L_2$ passes through the points $A(2,-4,2)$ and $B(7,-6,1)$.

**(c)** Show that $L_1$ and $L_2$ are skew.

*For (c) name the relation — `'parallel'`, `'intersecting'` or `'skew'` — and
enter $[\lambda,\mu]$ found from two of the component equations of **your**
lines from (a) and (b). The check tells you what the third component does.*
""")

code(r"""
q8a = ...        # L1: vec(...) + lam*vec(...)
q8b = ...        # L2: vec(...) + mu*vec(...)
q8c = ...        # 'parallel', 'intersecting' or 'skew'
q8c_pair = [...] # [lam, mu] from two of the component equations

point_P = vec(-1, 1, -13)
A, B = vec(2, -4, 2), vec(7, -6, 1)
L1, L2 = line(point_P, vec(7, 1, 2)), through(A, B)

verify_line('8a', q8a, L1)
verify_line('8b', q8b, L2)
verify_relation('8c', q8c, L1, L2)
verify_pair('8c pair', q8c_pair, q8a, q8b)
""")

md(r"""
### Task 9 🔴 — *May 2025 TZ1 Paper 1 Q6, 6 marks*

The line $L_1$ has vector equation $\mathbf r=4\mathbf i-\mathbf k+\lambda(a\mathbf j+\mathbf k)$, where $a,\lambda\in\mathbb R$.

The line $L_2$ has vector equation $\mathbf r=\mathbf i-b\mathbf k+\mu(\mathbf i+2\mathbf j+3\mathbf k)$, where $b,\mu\in\mathbb R$.

The lines $L_1$ and $L_2$ are perpendicular and intersect at a unique point.

Find the value of $a$ and the value of $b$.
""")

code(r"""
a, b = symbols('a b')

q9 = [...]       # [a, b]

L1 = line(vec(4, 0, -1) + lam*vec(0, a, 1), lam)
L2 = line(vec(1, 0, -b) + mu*vec(1, 2, 3), mu)

verify_find('9', q9, [a, b], [perpendicular(L1, L2), meet(L1, L2)])
""")

md(r"""
### Task 10 🔴 — *November 2022 Paper 2 Q12(a)–(c), 13 marks*

Consider the points $A(1,2,3)$, $B(k,-2,1)$ and $C(5,0,2)$, where $k\in\mathbb R$.

**(a)** Write down $\overrightarrow{AB}$ and $\overrightarrow{AC}$.

**(b)** Given that the points $A$, $B$ and $C$ lie on a straight line, show that $k=9$.

**(c)** For $k=9$, let $L_1$ be the line passing through $A$, $B$ and $C$.

**(i)** Find a vector equation of the line $L_1$.

**(ii)** Line $L_2$ has the equation $\dfrac{x-1}{2}=\dfrac y3=1-z$. Show that the lines $L_1$
and $L_2$ are skew.

*For (b) enter the value of $k$ that the collinearity gives. For (c)(ii) the
parameter of $L_2$ is the common value $\mu$ of its three parts.*
""")

code(r"""
q10a_AB = ...        # AB in terms of k
q10a_AC = ...        # AC
q10b = ...           # k
q10ci = ...          # L1: vec(...) + lam*vec(...)
q10cii = ...         # 'parallel', 'intersecting' or 'skew'
q10cii_pair = [...]  # [lam, mu] from two of the component equations

A, B, C = vec(1, 2, 3), vec(k, -2, 1), vec(5, 0, 2)
L2 = cartesian((x - 1)/2, y/3, 1 - z)

verify_find('10a AB', q10a_AB, B - A)
verify_find('10a AC', q10a_AC, C - A)
verify_find('10b', q10b, k, [parallel(B - A, C - A)])
verify_line('10c(i)', q10ci, through(A, C))
verify_relation('10c(ii)', q10cii, through(A, C), L2)
verify_pair('10c(ii) pair', q10cii_pair, q10ci, L2)
""")

# ================================================================= теория 7
md(r"""
## Theory: a line walked in time

$$\mathbf r=\mathbf r_0+t\,\mathbf v$$

is where a ship or an aircraft is at time $t$: it starts at $\mathbf r_0$ and
moves by $\mathbf v$ every unit of time.

**Speed** is $\lvert\mathbf v\rvert$ — everything that multiplies $t$, numbers
in front included. A ship at $\mathbf r=(2,-3)+t(3,4)$ km moves at $5$ km/h;
at $\mathbf r=(2,-3)+2t(3,4)$ it moves at $10$. The position vector
$(2,-3)$ says nothing about speed.

**A bearing** is read from the horizontal components, east and north,
measured **from north, clockwise**, in three figures. The ship goes $3$ east
and $4$ north each hour: $\arctan\frac34=36.9^\circ$ from north, so $037^\circ$ —
not $053^\circ$, which is the angle from east.

**Two paths that cross** are two lines. Where they cross is technique 6 with
**two times**, $t_1$ and $t_2$; setting $\mathbf r_A(t)=\mathbf r_B(t)$ with one
$t$ asks whether they collide. The time between their arrivals at the
crossing is $\lvert t_1-t_2\rvert$, in the units of $t$.

**Climbing or descending.** A drone with velocity $(6,-8,0)$ m/s starts to
descend at $3$ m/s with its horizontal velocity unchanged: its velocity is
$(6,-8,-3)$. The angle with the horizontal compares the vertical part with
the horizontal speed $10$: $\arctan\frac3{10}=16.7^\circ$.
""")

md(r"""
### Task 11 🔴 — *May 2022 TZ2 Paper 2 Q11(a)–(d), 15 marks*

Two airplanes, $A$ and $B$, have position vectors with respect to an origin $O$
given respectively by

$$\mathbf r_A=\begin{pmatrix}19\\-1\\1\end{pmatrix}+t\begin{pmatrix}-6\\2\\4\end{pmatrix}$$

$$\mathbf r_B=\begin{pmatrix}1\\0\\12\end{pmatrix}+t\begin{pmatrix}4\\2\\-2\end{pmatrix}$$

where $t$ represents the time in minutes and $0\le t\le2.5$.

Entries in each column vector give the displacement east of $O$, the
displacement north of $O$ and the distance above sea level, all measured in
kilometres.

**(a)** Find the three-figure bearing on which airplane $B$ is travelling.

**(b)** Show that airplane $A$ travels at a greater speed than airplane $B$.

**(c)** Find the acute angle between the two airplanes' lines of flight. Give
your answer in degrees.

The two airplanes' lines of flight cross at point $P$.

**(d)** **(i)** Find the coordinates of $P$.
**(ii)** Determine the length of time between the first airplane arriving at $P$
and the second airplane arriving at $P$.

*In (a) enter the bearing as a string of three figures. For (b) enter both
speeds. Part (e), the minimum distance, is optimisation — E9.*
""")

code(r"""
q11a = ...       # the bearing of B, a string of three figures
q11b_A = ...     # the speed of A, km per minute
q11b_B = ...     # the speed of B
q11c = ...       # the acute angle, degrees
q11d_i = ...     # the point where the paths cross
q11d_ii = ...    # the time between the arrivals, minutes

rA = vec(19, -1, 1) + t*vec(-6, 2, 4)
rB = vec(1, 0, 12) + t*vec(4, 2, -2)
t1, t2, crossing = unknown('t1'), unknown('t2'), unknown('crossing', 3)

verify_bearing('11a', q11a, velocity(rB))
verify_speed('11b A', q11b_A, rA)
verify_speed('11b B', q11b_B, rB)
verify_angle('11c', q11c, line(rA, t), line(rB, t), deg=True)
verify_meet('11d(i)', q11d_i, line(rA, t), line(rB, t))
verify_find('11d(ii)', q11d_ii, Abs(t1 - t2), [Eq(rA.subs(t, t1), crossing), Eq(rB.subs(t, t2), crossing)])
""")

md(r"""
### Task 12 🔴 — *May 2025 TZ1 Paper 2 Q7, 5 marks*

At 09:00 a helicopter is located at a point $(10,3,0.5)$ relative to a point $O$ on
horizontal ground. The $x$-direction is due east, the $y$-direction is due north
and the $z$-direction is vertically upwards.

All distances are measured in kilometres.

The helicopter is flying at a constant height.

The helicopter's position relative to the point $O$ is given by
$\mathbf r=\begin{pmatrix}10\\3\\0.5\end{pmatrix}+4t\begin{pmatrix}10\\-25\\0\end{pmatrix}$, where $t$
represents the time in hours since 09:00.

**(a)** Find the speed of the helicopter.

At 10:00 the helicopter begins to descend.

During descent the helicopter's vertical height decreases at a constant rate
of $16\text{ km h}^{-1}$ and its horizontal velocity remains unchanged.

The angle of descent, $\beta$, is defined as the angle between the helicopter's
direction of travel and the horizontal.

**(b)** Find $\beta$, giving your answer in degrees.
""")

code(r"""
q12a = ...       # the speed, km/h
q12b = ...       # beta, degrees

r = vec(10, 3, 0.5) + 4*t*vec(10, -25, 0)
descending = velocity(r) + vec(0, 0, -16)    # the horizontal velocity unchanged, the height falls 16 km/h

verify_speed('12a', q12a, r)
verify_angle('12b', q12b, descending, 'horizontal', deg=True)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `points` | points and lengths: a vector between points, a midpoint, a vertex |
| `scalar` | the scalar product: perpendicular, a right angle |
| `angle` | the angle between two vectors |
| `line` | the equation of a line |
| `line_angle` | the angle between two lines |
| `meet` | the point where two lines meet |
| `skew` | parallel, intersecting or skew; conditions on letters |
| `motion` | speed, bearing and time along a line |

1. Find the coordinates of the midpoint of $[PQ]$, where $P(2,5,-1)$ and $Q(4,-3,7)$.
2. $\mathbf u=(3,-2,1)$ and $\mathbf v=(p,4,2)$ are perpendicular. Find $p$.
3. Find the angle between the vectors $(1,2,2)$ and $(2,0,-1)$.
4. A line passes through $(0,3,-2)$ and $(4,1,5)$. Write down its vector equation.
5. Find the acute angle between $\mathbf r=(1,0,1)+\lambda(2,1,2)$ and $\mathbf r=(0,5,0)+\mu(1,-2,2)$.
6. Find the point of intersection of $\mathbf r=(1,1,0)+\lambda(1,0,2)$ and $\mathbf r=(3,2,5)+\mu(0,-1,1)$.
7. Determine whether $\mathbf r=(2,0,1)+\lambda(1,3,-1)$ and $\mathbf r=(0,1,4)+\mu(2,1,1)$ are parallel, intersecting or skew.
8. A boat's position at time $t$ hours is $\mathbf r=(4,-1)+t(5,12)$ km. Find its speed.
9. $ABCD$ is a parallelogram with $A(1,1)$, $B(4,2)$ and $C(6,5)$. Find $D$.
10. Show that the triangle with vertices $(0,0,0)$, $(2,1,2)$ and $(1,-2,0)$ has a right angle.
11. Find a vector equation of the line $\frac{x-3}{4}=\frac{y+1}{-2}=\frac z5$.
12. An aircraft flies with velocity $(300,400,0)$ km/h, east and north. Find the bearing of its course.
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
## On the clock — *November 2023 TZ1 Paper 2 Q12(a), 5 marks*

**Five marks, seven minutes.** Calculator allowed, no hints.

Line $L$ is given by the vector equation
$\mathbf r_1=\begin{pmatrix}1\\2\\-3\end{pmatrix}+s\begin{pmatrix}2\\3\\6\end{pmatrix}$ where $s\in\mathbb R$.

Line $M$ is given by the vector equation
$\mathbf r_2=\begin{pmatrix}9\\9\\11\end{pmatrix}+t\begin{pmatrix}4\\1\\2\end{pmatrix}$ where $t\in\mathbb R$.

**(a)** Show that lines $L$ and $M$ intersect at a point $A$ and find the position
vector of $A$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_pair = [...]  # [s, t] from two of the component equations
qt = ...         # the position vector of A

s = symbols('s')
L = line(vec(1, 2, -3) + s*vec(2, 3, 6), s)
M = line(vec(9, 9, 11) + t*vec(4, 1, 2), t)

verify_pair('timer [s, t]', qt_pair, L, M)
verify_meet('timer A', qt, L, M)
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** $ABCD$ in order means $\overrightarrow{BC}=\overrightarrow{AD}$:
$\overrightarrow{BC}=(2,4,2)$, so $D=A+(2,4,2)=\boxed{(3,0,2)}$.

**1 (b)** The diagonals of a parallelogram bisect each other: $E$ is the midpoint
of $[AC]$, $\left(\frac{1-1}2,\frac{-4-2}2,\frac{0+4}2\right)=\boxed{(0,-3,2)}$.

---

**2 (a)** $\lvert\mathbf a\rvert=\sqrt{144+25}=13$. The longest $\mathbf a+\mathbf b$ has $\mathbf b$
along $\mathbf a$, $13+15=28$; the shortest has it against $\mathbf a$, $15-13=2$:

$$\boxed{2\le\lvert\mathbf a+\mathbf b\rvert\le28}$$

**2 (b)** At the minimum $\mathbf b=-\frac{15}{13}\mathbf a$, so
$\mathbf p=\mathbf a+\mathbf b=-\frac2{13}\mathbf a=\boxed{\begin{pmatrix}-24/13\\10/13\end{pmatrix}}=\begin{pmatrix}-1.85\\0.769\end{pmatrix}$.

**2 (c)** Perpendicular to $(12,-5)$ is the direction $(5,12)$, of length $13$; with
$x,y>0$ and length $15$:

$$\mathbf q=\frac{15}{13}\begin{pmatrix}5\\12\end{pmatrix}=\boxed{\begin{pmatrix}75/13\\180/13\end{pmatrix}}=\begin{pmatrix}5.77\\13.8\end{pmatrix}$$

---

**3 (a)** $\overrightarrow{AB}=\overrightarrow{OC}=\mathbf c$, so
$\overrightarrow{OM}=\mathbf a+k\mathbf c$ and
$\overrightarrow{MC}=\mathbf c-(\mathbf a+k\mathbf c)=\boxed{(1-k)\mathbf c-\mathbf a}$.

**3 (b)** Expanding,
$\overrightarrow{OM}\cdot\overrightarrow{MC}=(1-2k)\,\mathbf a\cdot\mathbf c-\lvert\mathbf a\rvert^2+k(1-k)\lvert\mathbf c\rvert^2$.
With $\lvert\mathbf c\rvert^2=4\lvert\mathbf a\rvert^2$ and $\mathbf a\cdot\mathbf c=2\lvert\mathbf a\rvert^2\cos\theta$:

$$\boxed{2(1-2k)\lvert\mathbf a\rvert^2\cos\theta-\lvert\mathbf a\rvert^2+4k(1-k)\lvert\mathbf a\rvert^2}=\lvert\mathbf a\rvert^2\big(2(1-2k)\cos\theta-(1-2k)^2\big)$$

and this is $\lvert\mathbf a\rvert^2(1-2k)\big(2\cos\theta-(1-2k)\big)=0$.

---

**4 (a)** $BV=\sqrt{3^2+4^2+9^2}=\sqrt{106}=10.2956\ldots=\boxed{10.3}$

**4 (b)** From $V$: $\overrightarrow{VB}=(3,4,-9)$, $\overrightarrow{VC}=(3,-4,-9)$, and
$\overrightarrow{VB}\cdot\overrightarrow{VC}=9-16+81=74$:

$$\cos B\hat VC=\frac{74}{\sqrt{106}\sqrt{106}}=\frac{74}{106},\qquad B\hat VC=0.798037\ldots=\boxed{0.798}\ (45.7^\circ)$$

---

**5 (a)** $\mathbf a\cdot\mathbf c=-5p-42$ and $\mathbf b\cdot\mathbf c=-8p-54$.

**5 (b)** $\lvert\mathbf a\rvert=\sqrt{74}$, $\lvert\mathbf b\rvert=\sqrt{145}$, and $\lvert\mathbf c\rvert$ cancels:

$$\frac{-5p-42}{\sqrt{74}}=\frac{-8p-54}{\sqrt{145}}\quad\Longrightarrow\quad p=4.78727\ldots=\boxed{4.79}$$

---

**6 (a)** $\frac{x-1}2=\frac{y+2}3=z=\lambda$ gives $x=1+2\lambda$, $y=-2+3\lambda$, $z=\lambda$:

$$\boxed{\mathbf r=\begin{pmatrix}1\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}2\\3\\1\end{pmatrix}}$$

**6 (b)** $1+2\lambda=t$, $-2+3\lambda=4$, $\lambda=-8+2t$: the second gives $\lambda=2$,
the first $t=5$, and the third holds, $2=-8+10$. So $\boxed{(5,4,2)}$.

---

**7 (a)** **(i)** $\frac{-1+1}2=0=3-3$. **(ii)**
$\boxed{\mathbf r=\begin{pmatrix}-1\\0\\3\end{pmatrix}+\lambda\begin{pmatrix}2\\1\\-1\end{pmatrix}}$ — from
$x=-1+2\lambda$, $y=\lambda$, $z=3-\lambda$.

**7 (b)** $(2,1,-1)\cdot(a,1,-1)=2a+2$, the lengths are $\sqrt6$ and $\sqrt{a^2+2}$:

$$\frac{\lvert2a+2\rvert}{\sqrt6\sqrt{a^2+2}}=\frac1{\sqrt2}\;\Rightarrow\;4a^2+8a+4=3a^2+6\;\Rightarrow\;a^2+8a-2=0\;\Rightarrow\;\boxed{a=-4\pm3\sqrt2}$$

**7 (c)** $-1+2\lambda=at$, $\lambda=1+t$, $3-\lambda=2-t$. The last two agree, and the first
becomes $1+2t=at$, so $t=\frac1{a-2}$: no solution when $a=2$, $\boxed{k=2}$. Then

$$A=\left(\frac a{a-2},\ 1+\frac1{a-2},\ 2-\frac1{a-2}\right)=\boxed{\left(\frac a{a-2},\ \frac{a-1}{a-2},\ \frac{2a-5}{a-2}\right)}$$

---

**8 (a)** $\boxed{\mathbf r=\begin{pmatrix}-1\\1\\-13\end{pmatrix}+\lambda\begin{pmatrix}7\\1\\2\end{pmatrix}}$

**8 (b)** $\overrightarrow{AB}=(5,-2,-1)$: $\boxed{\mathbf s=\begin{pmatrix}2\\-4\\2\end{pmatrix}+\mu\begin{pmatrix}5\\-2\\-1\end{pmatrix}}$

**8 (c)** $\frac57\ne\frac{-2}1$: not parallel. The first two components:
$-1+7\lambda=2+5\mu$ and $1+\lambda=-4-2\mu$, so $\boxed{\lambda=-1,\ \mu=-2}$. The third:
$-13+2(-1)=-15$ but $2-(-2)=4$. No common point and not parallel: $\boxed{\text{skew}}$.

---

**9** The directions $(0,a,1)$ and $(1,2,3)$ are perpendicular: $2a+3=0$, $a=-\frac32$.
Equating components: $4=1+\mu$ gives $\mu=3$; $-\frac32\lambda=2\mu=6$ gives $\lambda=-4$;
$-1+\lambda=-b+3\mu$ gives $-5=-b+9$. So $\boxed{a=-\frac32,\ b=14}$.

---

**10 (a)** $\overrightarrow{AB}=\boxed{\begin{pmatrix}k-1\\-4\\-2\end{pmatrix}}$,
$\overrightarrow{AC}=\boxed{\begin{pmatrix}4\\-2\\-1\end{pmatrix}}$

**10 (b)** On one line, $\overrightarrow{AB}=2\overrightarrow{AC}$: $k-1=8$, $\boxed{k=9}$.

**10 (c)(i)** $\boxed{\mathbf r=\begin{pmatrix}1\\2\\3\end{pmatrix}+\lambda\begin{pmatrix}4\\-2\\-1\end{pmatrix}}$

**10 (c)(ii)** $L_2$: $x=1+2\mu$, $y=3\mu$, $z=1-\mu$. The directions $(4,-2,-1)$ and $(2,3,-1)$ are
not multiples. $1+4\lambda=1+2\mu$ and $2-2\lambda=3\mu$ give $\boxed{\lambda=\frac14,\ \mu=\frac12}$, and the
third fails: $3-\frac14=2.75\ne1-\frac12=0.5$. $\boxed{\text{skew}}$

---

**11 (a)** $B$ moves $4$ east and $2$ north: $\arctan\frac42=63.4^\circ$ from north, $\boxed{063^\circ}$.

**11 (b)** $\lvert(-6,2,4)\rvert=\sqrt{56}=\boxed{7.48}$ km/min and $\lvert(4,2,-2)\rvert=\sqrt{24}=\boxed{4.90}$ km/min.

**11 (c)** $\cos\theta=\frac{-24+4-8}{\sqrt{56}\sqrt{24}}=-0.7637\ldots$, $\theta=139.8^\circ$, and the acute angle is
$180^\circ-139.8^\circ=\boxed{40.2^\circ}$.

**11 (d)(i)** $19-6t_1=1+4t_2$, $-1+2t_1=2t_2$, $1+4t_1=12-2t_2$: $t_1=2$, $t_2=\frac32$, and
$P=\boxed{(7,3,9)}$.

**11 (d)(ii)** $\lvert t_1-t_2\rvert=\boxed{0.5}$ minutes — 30 seconds.

---

**12 (a)** The velocity is $4(10,-25,0)=(40,-100,0)$: speed $\sqrt{11600}=20\sqrt{29}=107.703\ldots=\boxed{108}$ km/h.

**12 (b)** $\tan\beta=\frac{16}{20\sqrt{29}}$, so $\beta=8.44984\ldots=\boxed{8.45^\circ}$.

---

## Timer

$1+2s=9+4t$ and $2+3s=9+t$ give $s=2$, $t=-1$; the third component agrees,
$-3+12=9=11-2$. So $\overrightarrow{OA}=\boxed{\begin{pmatrix}5\\8\\9\end{pmatrix}}$.
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
