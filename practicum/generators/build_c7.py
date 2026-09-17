"""Собирает практикум C7: чем и как в пространстве меряют.

Тридцать третий практикум серии и третий, последний по векторам. Разрез
тот же, что у C5 и C6, — по действию: C5 взял то, что делается без
плоскости и без векторного произведения, C6 — то, где плоскость сама
предмет вопроса, C7 — остаток, и остаток оказался однородным. Здесь
векторами меряют: площадь, объём, угол, расстояние.

Лестница из семи приёмов. Сначала само векторное произведение, потом
две величины, которые оно даёт прямо, — площадь и объём. Четвёртый
приём, тождество |a × b|² = |a|²|b|² − (a · b)², связывает его со
скалярным. Последние три меряют то, что видно не сразу: угол с
плоскостью, ближайшую точку прямой, расстояние до прямой.

Двадцать шестое понятие равенства ответов: **величину меряет фигура, а
не формула**. В ячейке стоит сам треугольник, сама пирамида, сама пара
прямых из билета, и проверка меряет их; каким ходом получено число, ей
безразлично.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_c7.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/geometry/practicum-c7-measuring.ipynb')

TRIGGER = {1: 'cross', 2: 'area', 3: 'volume', 4: 'identity', 5: 'angle',
           6: 'closest', 7: 'distance', 8: 'area', 9: 'angle', 10: 'cross',
           11: 'distance', 12: 'identity'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1_i': 'vec(0, -36, 0)',
    'q1_ii': '90',
    'q2a': 'vec(2 - 3*p, -2 - p, p**2 - 2*p)',
    'q2b': '6.75',
    'q2c': '1.30',
    'q3_i': '12',
    'q3_ii': '12*sqrt(3)',
    'q4': '68.8',
    'q5': '351',
    'q6_i': 'A**2*B**2*sin(th)**2',
    'q6_ii': 'A**2*B**2*cos(th)**2',
    'q7a': 'U**2*V**2*cos(th)**2 + U**2*V**2*sin(th)**2',
    'q7b_i': '2*sqrt(6)',
    'q7b_ii': 'sqrt(3)',
    'q7b_iii': '[[1, 2], [Rational(7, 5), Rational(4, 5)]]',
    'q8a': '60',
    'q8b': 'Rational(1, 5)',
    'q9': '0.932',
    'q10_i': '11.1',
    'q10_ii': '29.1',
    'q11a': '10 + 30*mu',
    'q11b': '(Rational(1, 3), Rational(-10, 3), Rational(7, 3))',
    'q11c': '(Rational(4, 3), Rational(-2, 3), Rational(4, 3))',
    'q12a': '3*sqrt(6)',
    'q12b': '3*sqrt(2)',
    'qt': '[vec(5*sqrt(66)/33, -10*sqrt(66)/33, 5*sqrt(66)/33),\n           vec(-5*sqrt(66)/33, 10*sqrt(66)/33, -5*sqrt(66)/33)]',
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


def col(*items):
    return r'\begin{pmatrix}' + r'\\'.join(str(i) for i in items) + r'\end{pmatrix}'


md(r"""
# C7 — Measuring in space: the vector product

**108 marks of the archive, seven techniques, twelve tasks.** Everything the
archive measures with vectors from May 2021 to November 2025: the vector
product itself, the area of a triangle and of a parallelogram, the volume of
a pyramid, the identity that ties the two products together, the angle a line
or a plane makes with a plane, the point of a line closest to a given point,
and the shortest distance to a line.

This is the third and last practicum on vectors. C5 took the points, the
lines and the angles between them; C6 took the planes. What is left is one
thing: **measuring**.

## The one idea

A scalar product measures **how much two vectors agree**; a vector product
measures **how much they do not**.

$$\mathbf u\cdot\mathbf v=|\mathbf u||\mathbf v|\cos\theta\qquad
|\mathbf u\times\mathbf v|=|\mathbf u||\mathbf v|\sin\theta$$

The first is a number, the second is a vector — perpendicular to both, and as
long as the parallelogram they span is wide.

## And what follows from it

| the question asks | what it is |
|---|---|
| the area of a parallelogram | $\lvert\mathbf u\times\mathbf v\rvert$, the two sides from one corner |
| the area of a triangle | half of it |
| the volume of a pyramid | a third of base times height — or a sixth of a determinant |
| $\lvert\mathbf u\rvert$ from $\mathbf u\cdot\mathbf v$ and the area | $(\mathbf u\cdot\mathbf v)^2+\lvert\mathbf u\times\mathbf v\rvert^2=\lvert\mathbf u\rvert^2\lvert\mathbf v\rvert^2$ |
| the angle between two planes | the angle between their normals, taken acute |
| the angle between a line and a plane | what is left of a right angle with the normal |
| the shortest distance to a line | $\lvert\overrightarrow{AP}\times\mathbf v\rvert/\lvert\mathbf v\rvert$ |

## How the checks work

They do not know the answers. A figure is handed to them **the way the
question names it**, and the check measures it:

```python
verify_measure('4', q4, 'triangle', point_P, Q, R)
verify_cross('2a', q2a, B - A, C - A)
verify_distance('12b', q12b, l1, l2)
```

The first is *"is that the area of the triangle PQR?"* — the check builds the
edges and measures. The second wants the vector product itself, not a
multiple of it: unlike a normal, $\mathbf u\times\mathbf v$ has its own
length and its own direction.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| $(2-3p,\,2+p,\,p^2-2p)$ | the middle component of a vector product has the wrong sign |
| $12\sqrt3$ for the triangle | the half is missing: a triangle is half the parallelogram |
| $1053$ for the pyramid | that is the volume of the prism: a pyramid is a third of it |
| $120°$ between two planes | that is the obtuse angle between the normals |
| $0.639$ for the angle with a plane | that is the angle with the normal |
| $\sqrt{54}$ for the distance between two lines | $\lvert\mathbf v\rvert$ is not divided out |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the product and what it measures | 1–4 |
| 🟡 | the volume, the identity, the angle between planes | 5–8 |
| 🔴 | angles with a line, the closest point, the distance | 9–12 |

Every task is a real past-paper question, cited.

**77 of the 114 marks are on a calculator paper, and here — unlike in C5 and
C6 — it works.** Three significant figures in an area, a volume, an angle or
a distance are the ordinary answer of this topic, not the exception.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, cross, measure, plane, unknown

language('en')                 # this notebook is in English, and so are the checks

# cross(u, v) is the vector product; dot(u, v) the scalar one; mag(v) the length.
# measure('triangle', A, B, C), measure('parallelogram', A, B, C, D),
# measure('pyramid', S, A, B, C) — the figure named by its vertices.
# angle(u, v) works for vectors, lines and planes; distance(A, L) is the shortest one.
# verify_arc(label, got, r, u, v) is the way along a sphere of radius r.

print('ready; sympy', sp.__version__)
u, v = vec(2, -1, 3), vec(1, 4, 0)
print('u × v:            ', cross(u, v))
print('perpendicular?    ', dot(cross(u, v), u), dot(cross(u, v), v))
print('area of that triangle:', measure('triangle', vec(0, 0, 0), u, v))
""")

md(r"""
---
## Map of the seven techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the vector product | *show that $\overrightarrow{AB}\times\overrightarrow{AC}=\ldots$*, *find $\mathbf a\times\mathbf p$* | one determinant, three components |
| 2 | area | *the area of parallelogram ABCD*, *use a vector method to find the area* | $\lvert\mathbf u\times\mathbf v\rvert$, halved for a triangle |
| 3 | volume | *find the volume of pyramid PQRS* | a third of base times height |
| 4 | the identity | *show that $(\mathbf u\cdot\mathbf v)^2+\lvert\mathbf u\times\mathbf v\rvert^2=\lvert\mathbf u\rvert^2\lvert\mathbf v\rvert^2$*, *hence find $\lvert\mathbf u\rvert$* | $\cos^2\theta+\sin^2\theta=1$ |
| 5 | angles with a plane | *the acute angle between the planes*, *the angle between a line and a plane* | the normal, and an acute answer |
| 6 | the closest point | *the point on $L$ nearest to the origin*, *find $\overrightarrow{PN}\cdot\overrightarrow{AB}$* | $\overrightarrow{PN}\cdot\mathbf d=0$ |
| 7 | the distance to a line | *the shortest distance from A to $L_1$*, *the minimum distance between $l_1$ and $l_2$* | $\lvert\overrightarrow{AP}\times\mathbf v\rvert/\lvert\mathbf v\rvert$ |

Techniques 1–3 climb: a product, its length, a determinant of three.
Technique 4 walks back to the scalar product and brings a length with it.
Techniques 5–7 all say the same thing in three shapes — **the shortest way
out is the perpendicular one**.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. The product and what it measures

## Theory: the vector product

Two vectors in space have a third one standing across both of them:

$$\mathbf u\times\mathbf v=\begin{pmatrix}u_2v_3-u_3v_2\\u_3v_1-u_1v_3\\u_1v_2-u_2v_1\end{pmatrix}$$

For $\mathbf u=(2,-1,3)$ and $\mathbf v=(1,4,0)$:

$$\mathbf u\times\mathbf v=\begin{pmatrix}(-1)(0)-(3)(4)\\(3)(1)-(2)(0)\\(2)(4)-(-1)(1)\end{pmatrix}=\begin{pmatrix}-12\\3\\9\end{pmatrix}$$

**Check it in two seconds.** The product is perpendicular to both factors:
$(-12,3,9)\cdot(2,-1,3)=-24-3+27=0$ and $(-12,3,9)\cdot(1,4,0)=-12+12=0$.
A sign slip almost never survives this test.

> **The middle component is $u_3v_1-u_1v_3$**, the other way round from its
> neighbours. Written as $u_1v_3-u_3v_1$ it gives $(-12,-3,9)$, and the check
> above fails at once: $(-12,-3,9)\cdot(2,-1,3)=-24+3+27=6$.

**Three things it is not.**

* Not a number. $\mathbf u\cdot\mathbf v=2-4+0=-2$ is the scalar product; the
  vector product is a vector.
* Not the components multiplied one by one: $(2,-4,0)$ is nothing.
* Not defined up to a factor. A normal of a plane may be scaled freely; here
  the length matters, because it is what measures:
  $$|\mathbf u\times\mathbf v|=|\mathbf u||\mathbf v|\sin\theta$$

**The order matters:** $\mathbf v\times\mathbf u=-(\mathbf u\times\mathbf v)$.
""")

md(r"""
### Task 1 🟢 — *May 2025 TZ2 Paper 3 Q2(c), 5 marks*

A sphere of radius 6 is centred at the origin $O$; lengths are in thousands of
kilometres. The North Pole $P$, a point $N$ on the equator and a second equatorial
point $A$ have position vectors

$$\mathbf p=""" + col(0, 0, 6) + r",\qquad \mathbf n=" + col(0, 6, 0) + r",\qquad \mathbf a=" + col(6, 0, 0) + r"""$$

$P$, $N$ and $A$, and the arcs joining them, form a spherical triangle. **The angle
at the vertex $A$ is defined as the angle between the vectors $\mathbf a\times\mathbf p$
and $\mathbf a\times\mathbf n$.**

**(i)** Find the vector $\mathbf a\times\mathbf p$.

**(ii)** Show that the angle at the vertex $A$ in the spherical triangle is $90°$.

*For (ii) enter the angle in degrees. Parts (a), (b), (d) belong to C1, C5 and C2;
(e) and (f) are task 10.*
""")

code(r"""
q1_i = ...       # a × p
q1_ii = ...      # the angle at A, in degrees

a, p_pole, n = vec(6, 0, 0), vec(0, 0, 6), vec(0, 6, 0)

verify_cross('1(i)', q1_i, a, p_pole)
verify_angle('1(ii)', q1_ii, cross(a, p_pole), cross(a, n), deg=True)
""")

# ================================================================= теория 2
md(r"""
## Theory: the area

$|\mathbf u\times\mathbf v|=|\mathbf u||\mathbf v|\sin\theta$ is exactly base
times height — **the area of the parallelogram** on $\mathbf u$ and $\mathbf v$.
A triangle is half of it.

Take $A(1,0,2)$, $B(3,1,2)$, $C(2,-1,5)$. The two edges from $A$ are
$\overrightarrow{AB}=(2,1,0)$ and $\overrightarrow{AC}=(1,-1,3)$, and

$$\overrightarrow{AB}\times\overrightarrow{AC}=\begin{pmatrix}(1)(3)-(0)(-1)\\(0)(1)-(2)(3)\\(2)(-1)-(1)(1)\end{pmatrix}=\begin{pmatrix}3\\-6\\-3\end{pmatrix}$$

$$|\overrightarrow{AB}\times\overrightarrow{AC}|=\sqrt{9+36+9}=\sqrt{54}=3\sqrt6$$

so the parallelogram on those edges has area $3\sqrt6$ and the triangle $ABC$ has
area $\frac{3\sqrt6}{2}$.

**Two edges from one corner.** In a parallelogram $ABCD$ the vertices go round,
so the sides from $A$ are $\overrightarrow{AB}$ and $\overrightarrow{AD}$ — not
$\overrightarrow{AC}$, which is a diagonal.

**$|\mathbf u||\mathbf v|$ is not the area** unless the angle is right:
$|\overrightarrow{AB}||\overrightarrow{AC}|=\sqrt5\cdot\sqrt{11}=\sqrt{55}$, and
$\sqrt{54}$ is smaller — by exactly the factor $\sin\theta$.

**With a letter in the points**, the area is a function of it, and *smallest
area* means the smallest value of that function. Square first: minimise
$|\mathbf u\times\mathbf v|^2$, which is a polynomial, and take the root at the
very end.
""")

md(r"""
### Task 2 🟢 — *November 2023 TZ1 Paper 2 Q8, 9 marks*

Three points are given by $A(0,p,2)$, $B(1,1,1)$ and $C(p,0,4)$, where $p$ is a
positive constant.

**(a)** Show that $\overrightarrow{AB}\times\overrightarrow{AC}=""" + col('2-3p', '-2-p', 'p^2-2p') + r"""$.

**(b)** Hence, find the smallest possible value of $|\overrightarrow{AB}\times\overrightarrow{AC}|^2$.

**(c)** Hence, find the smallest possible area of triangle $ABC$.

*Give (b) and (c) to three significant figures.*
""")

code(r"""
p = symbols('p', positive=True)

q2a = ...        # AB × AC
q2b = ...        # the smallest value of |AB × AC|²
q2c = ...        # the smallest area of ABC

A, B, C = vec(0, p, 2), vec(1, 1, 1), vec(p, 0, 4)
product = cross(B - A, C - A)

verify_cross('2a', q2a, B - A, C - A)
verify_optimum('2b', q2b, dot(product, product), p, Interval(0, oo), 'min')
verify_optimum('2c', q2c, measure('triangle', A, B, C), p, Interval(0, oo), 'min')
""")

md(r"""
### Task 3 🟢 — *May 2025 TZ3 Paper 1 Q11(c), 4 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D$ form a parallelogram
$ABCD$, where $D$ is diagonally opposite $B$. *(Part (a), technique 3 of C5,
gives $D(3,0,2)$.)*

**(i)** Given that $\overrightarrow{AB}\times\overrightarrow{AD}=m""" + col(-1, 1, -1) + r"""$,
where $m\in\mathbb Z^+$, find the value of $m$.

**(ii)** Hence, find the area of parallelogram $ABCD$.

*Give (ii) exactly.*
""")

code(r"""
m = symbols('m')

q3_i = ...       # m
q3_ii = ...      # the area of ABCD

A, B, C, D = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4), vec(3, 0, 2)

verify_find('3(i)', q3_i, m, [Eq(cross(B - A, D - A), m*vec(-1, 1, -1))])
verify_measure('3(ii)', q3_ii, 'parallelogram', A, B, C, D, exact=True)
""")

md(r"""
### Task 4 🟢 — *November 2025 TZ1 Paper 2 Q12(d), 5 marks*

The plane $\Pi$ has Cartesian equation $4x+y-3z=18$ *(part (b), technique 2 of C6)*.
It meets the coordinate axes at $P(4.5,0,0)$, $Q(0,q,0)$ and $R(0,0,r)$, where
$q=18$ and $r=-6$ *(part (c), technique 1 of C6)*.

**(d)** Use a vector method to find the area of the triangle $PQR$.

*Three significant figures.*
""")

code(r"""
q4 = ...         # the area of PQR

point_P, Q, R = vec(Rational(9, 2), 0, 0), vec(0, 18, 0), vec(0, 0, -6)

verify_measure('4', q4, 'triangle', point_P, Q, R)
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. The volume, the identity, the angle

## Theory: the volume of a pyramid

A pyramid on a triangular base is **a third of base times height**:

$$V=\tfrac13\,S_{\text{base}}\cdot h$$

The base area is technique 2. The height is the distance from the apex to the
**plane** of the base — measured along the normal, not to a corner.

Take the triangle $A(1,0,2)$, $B(3,1,2)$, $C(2,-1,5)$ again and the apex
$S(1,1,6)$. The three edges from $S$ are

$$\overrightarrow{SA}=\begin{pmatrix}0\\-1\\-4\end{pmatrix},\quad
\overrightarrow{SB}=\begin{pmatrix}2\\0\\-4\end{pmatrix},\quad
\overrightarrow{SC}=\begin{pmatrix}1\\-2\\-1\end{pmatrix}$$

and the shortest road to the volume is one determinant:

$$V=\frac16\left|\det\begin{pmatrix}0&-1&-4\\2&0&-4\\1&-2&-1\end{pmatrix}\right|=\frac{18}{6}=3$$

The two routes are the same thing. The determinant is the volume of the
**parallelepiped** on the three edges; a pyramid is a sixth of it, because the
base is half a parallelogram and the height enters with a third.

| what you computed | what it is |
|---|---|
| the determinant | the parallelepiped: six pyramids |
| base $\times$ height | the prism: three pyramids |
| $\frac12\lvert\mathbf u\times\mathbf v\rvert\cdot h$ | twice the pyramid — the $\frac13$ is missing |

**If the apex sits on a normal line** $\mathbf r=\mathbf m+\gamma\mathbf n$ at a
known $\gamma$, the height is $|\gamma|\,|\mathbf n|$ — not $|\gamma|$.
""")

md(r"""
### Task 5 🟡 — *November 2025 TZ1 Paper 2 Q12(g), 4 marks*

Continuing task 4: the line $L_3$ is normal to $\Pi$ and passes through
$(1,8,-2)$, so $\mathbf r_3=""" + col(1, 8, -2) + r"+\gamma" + col(-4, -1, 3) + r"""$.
The point $S(-11,5,7)$ lies on $L_3$ at $\gamma=3$ *(parts (e), (f), techniques
1 and 6 of C5–C6)*.

**(g)** Hence, find the volume of pyramid $PQRS$.

*The base $PQR$ is the triangle of task 4. Give the answer exactly — it is a
whole number.*
""")

code(r"""
q5 = ...         # the volume of PQRS

point_P, Q, R = vec(Rational(9, 2), 0, 0), vec(0, 18, 0), vec(0, 0, -6)
S = vec(-11, 5, 7)

verify_measure('5', q5, 'pyramid', S, point_P, Q, R, exact=True)
""")

# ================================================================= теория 4
md(r"""
## Theory: the identity that joins the two products

The two products see the same angle from two sides:

$$\mathbf u\cdot\mathbf v=|\mathbf u||\mathbf v|\cos\theta,\qquad
|\mathbf u\times\mathbf v|=|\mathbf u||\mathbf v|\sin\theta$$

Square both and add. The Pythagorean identity does the rest:

$$(\mathbf u\cdot\mathbf v)^2+|\mathbf u\times\mathbf v|^2
=|\mathbf u|^2|\mathbf v|^2(\cos^2\theta+\sin^2\theta)=|\mathbf u|^2|\mathbf v|^2$$

The same statement written the other way is
$|\mathbf u\times\mathbf v|^2=|\mathbf u|^2|\mathbf v|^2-(\mathbf u\cdot\mathbf v)^2$,
and one line takes you from either to the other.

**What it is for.** It gives a length that nobody handed you. If
$\mathbf a\cdot\mathbf b=12$, $|\mathbf a\times\mathbf b|=5$ and $|\mathbf b|=13$, then

$$12^2+5^2=|\mathbf a|^2\cdot13^2\quad\Longrightarrow\quad
|\mathbf a|^2=\frac{169}{169}=1\quad\Longrightarrow\quad|\mathbf a|=1$$

Three habits are worth having here.

* The scalar product carries $\cos$, the vector product $\sin$. Swapping them
  is the commonest slip on the page.
* **Both terms are squared.** $\mathbf u\cdot\mathbf v+|\mathbf u\times\mathbf v|$
  is not $|\mathbf u||\mathbf v|$.
* The identity gives $|\mathbf u|^2$; the question usually wants $|\mathbf u|$.

A Cartesian proof — expand both sides in components — is allowed, but the
markscheme warns that a half-finished one scores nothing.
""")

md(r"""
### Task 6 🟡 — *May 2021 TZ2 Paper 1 Q5, 4 marks*

Given any two non-zero vectors $\mathbf a$ and $\mathbf b$, show that
$|\mathbf a\times\mathbf b|^2=|\mathbf a|^2|\mathbf b|^2-(\mathbf a\cdot\mathbf b)^2$.

*The proof is two lines on paper. Enter its two ends: the left-hand side and
the last term of the right-hand side, each written with $A=|\mathbf a|$,
$B=|\mathbf b|$ and $\theta$ — and then read the identity off
$\sin^2\theta=1-\cos^2\theta$. Use `th` for $\theta$.*
""")

code(r"""
A, B, th = symbols('A B th')

q6_i = ...       # |a × b|², written with A, B and th
q6_ii = ...      # (a · b)², written with A, B and th

a = vec(*symbols('a1 a2 a3'))            # any two vectors, in components
b = vec(*symbols('b1 b2 b3'))
letters = {A: mag(a), B: mag(b), th: angle(a, b)}

verify_formula('6(i)', q6_i, dot(cross(a, b), cross(a, b)), letters)
verify_formula('6(ii)', q6_ii, dot(a, b)**2, letters)
""")

md(r"""
### Task 7 🟡 — *May 2024 TZ1 Paper 2 Q12(a), (b), 15 marks*

Consider the non-zero vectors $\mathbf u$ and $\mathbf v$, and let $\theta$ be the
angle between them.

**(a)** Using the definitions of $\mathbf u\cdot\mathbf v$ and
$\mathbf u\times\mathbf v$ in terms of $|\mathbf u|$, $|\mathbf v|$ and $\theta$,
show that $(\mathbf u\cdot\mathbf v)^2+|\mathbf u\times\mathbf v|^2=|\mathbf u|^2|\mathbf v|^2$.

A triangle $ABC$ has vertices $A(0,1,2)$, $B(p,q,3)$ and $C(3,2,1)$, with
$p,q\in\mathbb R$. The vectors are $\mathbf u=\overrightarrow{AB}$ and
$\mathbf v=\overrightarrow{AC}$. It is given that $\mathbf u\cdot\mathbf v=3$ and
that the area of triangle $ABC$ is $\sqrt6$.

**(b)** **(i)** Find the value of $|\mathbf u\times\mathbf v|$.
**(ii)** Hence, or otherwise, find the value of $|\mathbf u|$.
**(iii)** Hence, or otherwise, find the possible values of $p$ and the
corresponding values of $q$.

*For (a) enter the left-hand side written with $U=|\mathbf u|$, $V=|\mathbf v|$
and `th` — before you simplify it. For (b)(iii) enter both pairs, as
`[[p, q], [p, q]]`. Part (c) is the task on the clock.*
""")

code(r"""
U, V, th = symbols('U V th')
p, q = unknown('p'), unknown('q')         # the two the question asks for

q7a = ...        # (u · v)² + |u × v|², written with U, V and th
q7b_i = ...      # |u × v|
q7b_ii = ...     # |u|
q7b_iii = [...]  # both pairs: [[p, q], [p, q]]

one = vec(*symbols('m1 m2 m3'))          # any two vectors, for part (a)
two = vec(*symbols('n1 n2 n3'))
verify_formula('7a', q7a, dot(one, two)**2 + dot(cross(one, two), cross(one, two)),
               {U: mag(one), V: mag(two), th: angle(one, two)})

A, B, C = vec(0, 1, 2), vec(p, q, 3), vec(3, 2, 1)
u, v = B - A, C - A
given = [Eq(measure('triangle', A, B, C), sqrt(6)), Eq(dot(u, v), 3)]

verify_find('7b(i)', q7b_i, mag(cross(u, v)), given)
verify_find('7b(ii)', q7b_ii, mag(u), given)
verify_find('7b(iii)', q7b_iii, [p, q], given)
""")

# ================================================================= теория 5
md(r"""
## Theory: angles with a plane

A plane has no direction of its own — it has a normal, and every angle with a
plane is computed through it.

**Two planes.** The angle between them is the angle between the normals. Take
$2x-y+2z=5$ and $x+2y+2z=1$: the normals are $(2,-1,2)$ and $(1,2,2)$,

$$\cos\theta=\frac{|(2,-1,2)\cdot(1,2,2)|}{3\cdot3}=\frac{|2-2+4|}{9}=\frac49
\quad\Longrightarrow\quad\theta=63.6°$$

The bars matter: without them a negative scalar product gives the obtuse
angle, and the question almost always asks for the acute one. If your answer
came out above $90°$, subtract it from $180°$.

**A line and a plane.** Here the normal points the wrong way, and the angle
you want is what is left of a right angle:

$$\sin\alpha=\frac{|\mathbf d\cdot\mathbf n|}{|\mathbf d||\mathbf n|}$$

For the line with direction $(1,2,2)$ and the plane $x-y+z=4$:
$\sin\alpha=\dfrac{|1-2+2|}{3\sqrt3}=\dfrac{1}{3\sqrt3}$, so $\alpha=11.1°$.

> Sine for a line and a plane, cosine for two planes. One formula, two names,
> because in the first case the normal is $90°$ off the thing you measure.

**On a sphere** the same rule appears in disguise: the angle between two arcs
is the angle between the planes of their great circles, that is between
$\mathbf a\times\mathbf p$ and $\mathbf a\times\mathbf n$ — vector products
again. And an arc of angle $\theta$ on a sphere of radius $r$ has length
$r\theta$, with $\theta$ **in radians**.
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ1 Paper 1 Q11(a) and May 2025 TZ3 Paper 1 Q11(e), 9 marks*

**(a)** *(TZ1)* The plane $P_1$ has equation $x+2y+z=0$ and the plane $P_2$ has
equation $x-y-2z=0$. The acute angle between $P_1$ and $P_2$ is $\theta$. Show
that $\theta=60°$.

**(b)** *(TZ3)* The plane $\Pi_1$ has equation $-x+y-z=-5$ and the plane $\Pi_2$
has equation $5x+y-7z=1$. The acute angle between $\Pi_1$ and $\Pi_2$ is
$\theta$. Show that $\cos\theta=\frac15$.

*In (a) enter the angle in degrees; in (b) enter the cosine, exactly.*
""")

code(r"""
q8a = ...        # θ in degrees
q8b = ...        # cos θ

P1 = plane(Eq(x + 2*y + z, 0), name='P1')
P2 = plane(Eq(x - y - 2*z, 0), name='P2')
Pi1 = plane(Eq(-x + y - z, -5), name='Pi1')
Pi2 = plane(Eq(5*x + y - 7*z, 1), name='Pi2')

verify_angle('8a', q8a, P1, P2, deg=True)
verify_angle('8b', q8b, Pi1, Pi2, cosine=True, exact=True)
""")

# ================================================================= часть 3
md(r"""
---
# 🔴 Part 3. The hard angles, and where the perpendicular lands

The first two tasks here are technique 5 again — the same normal, the same
acute answer — on the two questions where the archive makes it hard: a letter
inside the plane, and a triangle drawn on a sphere. Then the last two
techniques, and both say the same thing: **the shortest way out is the
perpendicular one.**
""")

md(r"""
### Task 9 🔴 — *May 2023 TZ1 Paper 2 Q8, 7 marks*

The angle between a line and a plane is $\alpha$, where
$0<\alpha<\frac\pi2$. The equation of the line is

$$\frac{x-1}{3}=\frac{y+2}{2}=5-z$$

and the equation of the plane is $4x+(\cos\alpha)y+(\sin\alpha)z=1$.

Find the value of $\alpha$.

*Three significant figures, in radians — the markscheme gives A0 for degrees.
The equation in $\alpha$ is one for the calculator.*
""")

code(r"""
alpha = symbols('alpha', positive=True)

q9 = ...         # α in radians

L = cartesian((x - 1)/3, (y + 2)/2, 5 - z)
Pi = plane(Eq(4*x + cos(alpha)*y + sin(alpha)*z, 1))

verify_find('9', q9, alpha, [Eq(angle(L, Pi), alpha)])
""")

md(r"""
### Task 10 🔴 — *May 2025 TZ2 Paper 3 Q2(e), (f), 11 marks*

Continuing task 1, on the same sphere of radius 6 (thousands of kilometres),
centred at $O$, with the North Pole $\mathbf p=(0,0,6)$:

Moscow $M$ has $\mathbf m=""" + col(0, r'6\cos\theta', r'6\sin\theta') + r"$ where $\theta=57.3°$, and Bogotá $B$ has $\mathbf b=" + col(r'6\sin120°', r'6\cos120°', 0) + r"""$.

**(e)** Find the shortest distance from Bogotá to Moscow on the sphere.

**(f)** The bearing from $B$ to $M$ is the angle at the vertex $B$ in the
spherical triangle $BMP$ — that is, by the method of part (c), the angle between
$\mathbf b\times\mathbf m$ and $\mathbf b\times\mathbf p$. Find the bearing
from Bogotá to Moscow.

*Give (e) in thousands of kilometres and (f) in degrees, both to three
significant figures.*
""")

code(r"""
q10_i = ...      # the distance along the sphere, in thousands of km
q10_ii = ...     # the bearing, in degrees

theta = 57.3*pi/180                       # 57.3 degrees, from part (d)
b = vec(6*sin(2*pi/3), 6*cos(2*pi/3), 0)  # 120 degrees west of Nairobi
m = vec(0, 6*cos(theta), 6*sin(theta))
p_pole = vec(0, 0, 6)

verify_arc('10(e)', q10_i, 6, b, m)
verify_angle('10(f)', q10_ii, cross(b, m), cross(b, p_pole), deg=True)
""")

# ================================================================= теория 6
md(r"""
---
## Theory: the closest point on a line

Every point of a line is $\mathbf c+\mu\mathbf d$. The one closest to a given
point $P$ is the one where the segment to it **crosses the line at a right
angle**:

$$\overrightarrow{PN}\cdot\mathbf d=0$$

That is one linear equation in one unknown, and it always has exactly one root.

Take $P(6,1,3)$ and $L:\ \mathbf r=(1,0,2)+\mu(2,1,-2)$. The general point is
$N(1+2\mu,\ \mu,\ 2-2\mu)$, so

$$\overrightarrow{PN}=\begin{pmatrix}2\mu-5\\\mu-1\\-2\mu-1\end{pmatrix},\qquad
\overrightarrow{PN}\cdot\begin{pmatrix}2\\1\\-2\end{pmatrix}=9\mu-9$$

Setting it to zero gives $\mu=1$ and $N(3,1,0)$.

**Three warnings.**

* The answer is the **point**, not $\mu$. Put $\mu$ back into the line.
* The scalar product is taken with the **direction**, not with the position
  vector of $N$ — unless the given point is the origin, where the two happen
  to coincide. *"Nearest to the origin"* is the one case where
  $\overrightarrow{ON}\cdot\mathbf d=0$ is the whole condition.
* $\overrightarrow{PN}=\overrightarrow{ON}-\overrightarrow{OP}$, end minus
  start. The other way round flips the sign of every term and sends $\mu$ the
  wrong way.

Minimising $|\overrightarrow{PN}|^2$ by calculus gives the same $\mu$; the
markscheme accepts both, and the dot product is shorter.
""")

md(r"""
### Task 11 🔴 — *November 2025 TZ3 Paper 1 Q10(d), (e) and May 2023 TZ2 Paper 2 Q6(b), 12 marks*

**(a)** *(November 2025 TZ3)* The point $P(-1,1,-13)$ lies on $L_1$. The line $L_2$
passes through $A(2,-4,2)$ and $B(7,-6,1)$, so
$\mathbf s=""" + col(2, -4, 2) + r"+\mu" + col(5, -2, -1) + r"""$, and the point $N$
lies on $L_2$. Find $\overrightarrow{PN}\cdot\overrightarrow{AB}$ in terms of $\mu$.

**(b)** Given that $N$ is the point on $L_2$ that lies closest to $P$, find the
coordinates of $N$.

**(c)** *(May 2023 TZ2)* $L$ is the line of intersection of $\Pi_1:2x-y+2z=6$ and
$\Pi_2:4x+3y-z=2$, and a vector equation of it is
$\mathbf r=""" + col(0, 2, 4) + r"+\lambda" + col(1, -2, -2) + r"""$ *(part (a),
technique 4 of C6)*. Find the coordinates of the point $P$ on $L$ that is nearest
to the origin.

*In (a) use `mu` for $\mu$; give (b) and (c) exactly.*
""")

code(r"""
q11a = ...       # PN · AB, in terms of mu
q11b = ...       # N
q11c = ...       # the point of L nearest to the origin

point_P, A, B = vec(-1, 1, -13), vec(2, -4, 2), vec(7, -6, 1)
L2 = line(A + mu*(B - A), mu, name='L2')
N = unknown('N', 3)

verify_find('11(a)', q11a, dot(L2.at(mu) - point_P, B - A))
verify_find('11(b)', q11b, N, [on(N, L2), perpendicular(N - point_P, L2)])

L = line(vec(0, 2, 4) + lam*vec(1, -2, -2), lam, name='L')
closest = unknown('N', 3)

verify_find('11(c)', q11c, closest, [on(closest, L), perpendicular(closest, L)])
""")

# ================================================================= теория 7
md(r"""
## Theory: the distance to a line

The shortest distance from a point to a line is the length of the
perpendicular — and the vector product measures it directly:

$$d=\frac{|\overrightarrow{AP}\times\mathbf v|}{|\mathbf v|}$$

where $A$ is **any** point of the line and $\mathbf v$ its direction. The
numerator is $|\overrightarrow{AP}||\mathbf v|\sin\theta$; dividing by
$|\mathbf v|$ leaves $|\overrightarrow{AP}|\sin\theta$, which is exactly the
height of $P$ above the line.

From the origin to $\mathbf r=(1,2,2)+\lambda(0,1,0)$:
$\overrightarrow{AP}=(-1,-2,-2)$ and

$$\frac{|(-1,-2,-2)\times(0,1,0)|}{|(0,1,0)|}=\frac{|(2,0,-1)|}{1}=\sqrt5$$

**Dividing by $|\mathbf v|$ is not optional.** It is the single most common
loss of a mark here: $|\overrightarrow{AP}\times\mathbf v|$ on its own is the
area of a parallelogram, not a length.

**Two parallel lines.** Pick a point on each; the distance between the lines is
the distance from one of them to the other line. For
$l_1:\mathbf r=\lambda(1,1,1)$ and $l_2:\mathbf r=(1,0,0)+\mu(2,2,2)$ the
directions are multiples, so the lines are parallel, and

$$d=\frac{|(1,0,0)\times(1,1,1)|}{|(1,1,1)|}=\frac{|(0,-1,1)|}{\sqrt3}=\frac{\sqrt2}{\sqrt3}=\frac{\sqrt6}{3}$$

**Check that they are parallel first.** If they are not, the two lines either
meet — distance zero — or are skew, and the archive has never asked for that.

Two other routes reach the same number and the markscheme takes them: if the
angle $\theta$ between $\overrightarrow{AP}$ and the line is known,
$d=|\overrightarrow{AP}|\sin\theta$; and minimising $|\overrightarrow{AB}|^2$
over the parameter, or setting $\overrightarrow{AB}\cdot\mathbf v=0$, gives the
foot of the perpendicular and then the distance.
""")

md(r"""
### Task 12 🔴 — *May 2023 TZ1 Paper 1 Q12(c) and May 2021 TZ2 Paper 1 Q8(b), 9 marks*

**(a)** *(May 2023 TZ1)* Two lines $L_1$ and $L_2$ meet at $P$, and $A(2t,8,3)$ lies
on $L_2$. The acute angle between the lines is $\frac\pi3$, the direction vector of
$L_1$ is $(1,1,0)$, and $\overrightarrow{PA}=(2t,0,3+t)$. Parts (a) and (b)
*(technique 5 of C5)* give $t=3$, so $P(0,8,-3)$ and $A(6,8,3)$. Hence or
otherwise, find the shortest distance from $A$ to $L_1$.

**(b)** *(May 2021 TZ2)* The lines $l_1$ and $l_2$ have vector equations

$$l_1:\ \mathbf r_1=""" + col(3, 2, -1) + r"+\lambda" + col(2, -2, 2) + r"\qquad l_2:\ \mathbf r_2=" + col(2, 0, 4) + r"+\mu" + col(1, -1, 1) + r"""$$

Part (a) *(technique 7 of C5)* shows that they do not intersect. Find the minimum
distance between $l_1$ and $l_2$.

*Both answers are exact.*
""")

code(r"""
q12a = ...       # the shortest distance from A to L1
q12b = ...       # the minimum distance between l1 and l2

L1 = line(vec(0, 8, -3) + lam*vec(1, 1, 0), lam, name='L1')
A = vec(6, 8, 3)
verify_distance('12(a)', q12a, A, L1, exact=True)

l1 = line(vec(3, 2, -1) + lam*vec(2, -2, 2), lam, name='l1')
l2 = line(vec(2, 0, 4) + mu*vec(1, -1, 1), mu, name='l2')
verify_distance('12(b)', q12b, l1, l2, exact=True)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `cross` | the vector product itself: compute it, or check it |
| `area` | the area of a triangle or a parallelogram |
| `volume` | the volume of a pyramid |
| `identity` | $(\mathbf u\cdot\mathbf v)^2+\lvert\mathbf u\times\mathbf v\rvert^2=\lvert\mathbf u\rvert^2\lvert\mathbf v\rvert^2$ |
| `angle` | an angle with a plane, through its normal |
| `closest` | the point of a line closest to a given point |
| `distance` | the shortest distance to a line |

1. Find $(1,0,-2)\times(3,1,1)$.
2. Find the area of the triangle with vertices $(0,0,0)$, $(1,2,0)$, $(0,3,4)$.
3. A pyramid has base $(0,0,0)$, $(2,0,0)$, $(0,3,0)$ and apex $(0,0,5)$. Find its volume.
4. Given $\mathbf u\cdot\mathbf v=6$, $|\mathbf u\times\mathbf v|=8$ and $|\mathbf v|=2$, find $|\mathbf u|$.
5. Find the acute angle between $x+y=1$ and $x-z=4$.
6. Find the point of $\mathbf r=\lambda(1,2,2)$ closest to $(3,0,0)$.
7. Find the distance from $(1,1,1)$ to the line $\mathbf r=\mu(0,0,1)$.
8. Find the area of the parallelogram with sides $(2,1,0)$ and $(0,1,3)$ from one corner.
9. Find the angle the line $\mathbf r=\lambda(1,1,1)$ makes with the plane $z=0$.
10. Show that $(\mathbf a\times\mathbf b)\cdot\mathbf a=0$ for all $\mathbf a$ and $\mathbf b$.
11. Two parallel lines pass through $(0,0,0)$ and $(1,1,0)$ with direction $(0,0,1)$. How far apart are they?
12. Show that $|\mathbf a\times\mathbf b|\le|\mathbf a||\mathbf b|$.
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
## On the clock — *May 2024 TZ1 Paper 2 Q12(c), 5 marks*

**Five marks, seven minutes.** Calculator allowed, no hints.

A triangle $ABC$ has vertices $A(0,1,2)$, $B(1,2,3)$ and $C(3,2,1)$, and
$\mathbf u=\overrightarrow{AB}$, $\mathbf v=\overrightarrow{AC}$. Consider a new
point $D$, and let $\mathbf w=\overrightarrow{CD}$.

It is given that $\mathbf u\cdot\mathbf w=\mathbf v\cdot\mathbf w=0$ and that the
area of triangle $ACD$ is $5$ square units.

Find the possible vectors for $\mathbf w$.

*Enter both, as a list of two vectors.*

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt = [...]       # both possible w

A, B, C = vec(0, 1, 2), vec(1, 2, 3), vec(3, 2, 1)
u, v = B - A, C - A
w = unknown('w', 3)
D = C + w

verify_find('timer', qt, w, [perpendicular(w, u), perpendicular(w, v),
                             Eq(measure('triangle', A, C, D), 5)])
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (i)** $\mathbf a\times\mathbf p=(6,0,0)\times(0,0,6)=\begin{pmatrix}0\cdot6-0\cdot0\\0\cdot0-6\cdot6\\6\cdot0-0\cdot0\end{pmatrix}=\boxed{\begin{pmatrix}0\\-36\\0\end{pmatrix}}$

**1 (ii)** $\mathbf a\times\mathbf n=(6,0,0)\times(0,6,0)=(0,0,36)$, and
$(0,-36,0)\cdot(0,0,36)=0$, so the angle is $\boxed{90°}$.

---

**2 (a)** $\overrightarrow{AB}=(1,1-p,-1)$ and $\overrightarrow{AC}=(p,-p,2)$, so

$$\overrightarrow{AB}\times\overrightarrow{AC}=\begin{pmatrix}(1-p)(2)-(-1)(-p)\\(-1)(p)-(1)(2)\\(1)(-p)-(1-p)(p)\end{pmatrix}=\boxed{\begin{pmatrix}2-3p\\-2-p\\p^2-2p\end{pmatrix}}$$

**2 (b)** $(2-3p)^2+(2+p)^2+(p^2-2p)^2=p^4-4p^3+14p^2-8p+8$. Its derivative
$4p^3-12p^2+28p-8$ vanishes at $p=0.3264\ldots$, and the value there is
$\boxed{6.75}$ $(6.75257\ldots)$.

**2 (c)** Area $=\frac12|\overrightarrow{AB}\times\overrightarrow{AC}|=\frac12\sqrt{6.75257\ldots}=\boxed{1.30}$ units².

---

**3 (i)** $\overrightarrow{AB}=(-4,-2,2)$, $\overrightarrow{AD}=(2,4,2)$, and
$\overrightarrow{AB}\times\overrightarrow{AD}=(-4-8,\ 4+8,\ -16+4)=(-12,12,-12)=12(-1,1,-1)$,
so $\boxed{m=12}$.

**3 (ii)** The area is that length: $12\,|(-1,1,-1)|=\boxed{12\sqrt3}\approx20.8$.

---

**4** $\overrightarrow{PQ}=(-4.5,18,0)$ and $\overrightarrow{PR}=(-4.5,0,-6)$, so
$\overrightarrow{PQ}\times\overrightarrow{PR}=(-108,-27,81)$ and

$$\text{area}=\tfrac12\sqrt{108^2+27^2+81^2}=\tfrac12\sqrt{18954}=\boxed{68.8}$$

---

**5** $S$ is at $\gamma=3$ on the normal line, so the height is
$3\,|(-4,-1,3)|=3\sqrt{26}=\sqrt{234}$, and

$$V=\tfrac13\cdot\tfrac12\sqrt{18954}\cdot\sqrt{234}=\boxed{351}$$

The determinant route is shorter: the edges from $S$ are $(15.5,-5,-7)$,
$(11,13,-7)$, $(11,-5,-13)$, whose determinant is $-2106$, and $2106/6=351$.

---

**6 (i)** $|\mathbf a\times\mathbf b|=|\mathbf a||\mathbf b|\sin\theta$, so
$\boxed{|\mathbf a\times\mathbf b|^2=A^2B^2\sin^2\theta}$.

**6 (ii)** $\mathbf a\cdot\mathbf b=|\mathbf a||\mathbf b|\cos\theta$, so
$\boxed{(\mathbf a\cdot\mathbf b)^2=A^2B^2\cos^2\theta}$. Then

$$A^2B^2\sin^2\theta=A^2B^2(1-\cos^2\theta)=A^2B^2-A^2B^2\cos^2\theta
=|\mathbf a|^2|\mathbf b|^2-(\mathbf a\cdot\mathbf b)^2$$

---

**7 (a)** $\boxed{U^2V^2\cos^2\theta+U^2V^2\sin^2\theta}=U^2V^2(\cos^2\theta+\sin^2\theta)=U^2V^2$.

**7 (b)(i)** Area $=\frac12|\mathbf u\times\mathbf v|=\sqrt6$, so
$|\mathbf u\times\mathbf v|=\boxed{2\sqrt6}\approx4.90$.

**7 (b)(ii)** $\mathbf v=(3,1,-1)$, $|\mathbf v|^2=11$, and the identity gives
$3^2+(2\sqrt6)^2=|\mathbf u|^2\cdot11$, that is $33=11|\mathbf u|^2$ and
$|\mathbf u|=\boxed{\sqrt3}\approx1.73$.

**7 (b)(iii)** $\mathbf u=(p,q-1,1)$. From $\mathbf u\cdot\mathbf v=3$:
$3p+q-1-1=3$, so $q=5-3p$. From $|\mathbf u|^2=3$: $p^2+(q-1)^2+1=3$. Substituting,
$p^2+(4-3p)^2=2$, that is $10p^2-24p+14=0$ and $5p^2-12p+7=0$:

$$\boxed{p=1,\ q=2}\qquad\text{or}\qquad\boxed{p=\tfrac75,\ q=\tfrac45}$$

---

**8 (a)** The normals are $(1,2,1)$ and $(1,-1,-2)$, both of length $\sqrt6$, and
their scalar product is $1-2-2=-3$:

$$\cos\theta=\frac{|-3|}{6}=\frac12\quad\Longrightarrow\quad\boxed{\theta=60°}$$

Without the bars $\cos\theta=-\frac12$ and $\theta=120°$; the acute angle is $180°-120°$.

**8 (b)** The normals are $(-1,1,-1)$ and $(5,1,-7)$, of lengths $\sqrt3$ and
$\sqrt{75}=5\sqrt3$, with scalar product $-5+1+7=3$:

$$\cos\theta=\frac{3}{\sqrt3\cdot5\sqrt3}=\frac{3}{15}=\boxed{\frac15}$$

---

**9** The direction of the line is $(3,2,-1)$ and the normal of the plane is
$(4,\cos\alpha,\sin\alpha)$, of lengths $\sqrt{14}$ and $\sqrt{16+1}=\sqrt{17}$. The
angle between them is $\frac\pi2-\alpha$, so

$$\cos\left(\tfrac\pi2-\alpha\right)=\sin\alpha=\frac{12+2\cos\alpha-\sin\alpha}{\sqrt{14}\sqrt{17}}$$

that is $12+2\cos\alpha-\sin\alpha=\sqrt{238}\,\sin\alpha$, and the calculator gives
$\boxed{\alpha=0.932}$ $(0.932389\ldots)$. In degrees it is $54.4°$ — and the
markscheme gives A0 for that.

---

**10 (e)** $\mathbf b=(5.196,-3,0)$ and $\mathbf m=(0,3.240,5.050)$, both of length 6:

$$\cos\widehat{BOM}=\frac{\mathbf b\cdot\mathbf m}{36}=\frac{-9.721}{36}=-0.2700
\quad\Longrightarrow\quad\widehat{BOM}=105.7°=1.844\text{ rad}$$

and the arc is $r\theta=6\times1.844=\boxed{11.1}$ thousand km.

**10 (f)** $\mathbf b\times\mathbf m=(-15.15,-26.23,16.84)$ and
$\mathbf b\times\mathbf p=(-18,-31.18,0)$, so

$$\cos\beta=\frac{1090.6}{34.66\times36}=0.8740\quad\Longrightarrow\quad\boxed{\beta=029.1°}$$

---

**11 (a)** $\overrightarrow{AB}=(5,-2,-1)$ and
$\overrightarrow{ON}=(2+5\mu,\,-4-2\mu,\,2-\mu)$, so
$\overrightarrow{PN}=(3+5\mu,\,-5-2\mu,\,15-\mu)$ and

$$\overrightarrow{PN}\cdot\overrightarrow{AB}=5(3+5\mu)-2(-5-2\mu)-(15-\mu)=\boxed{10+30\mu}$$

**11 (b)** $10+30\mu=0$ gives $\mu=-\frac13$ and
$N=\boxed{\left(\frac13,-\frac{10}3,\frac73\right)}$.

**11 (c)** Here the given point is the origin, so the condition is
$\overrightarrow{OP}\cdot\mathbf d=0$ with $\overrightarrow{OP}=(\lambda,\,2-2\lambda,\,4-2\lambda)$:

$$\lambda-2(2-2\lambda)-2(4-2\lambda)=9\lambda-12=0\quad\Longrightarrow\quad\lambda=\tfrac43$$

and $P=\boxed{\left(\frac43,-\frac23,\frac43\right)}$.

---

**12 (a)** $\overrightarrow{PA}=(6,0,6)$, so $|\overrightarrow{PA}|=6\sqrt2$ and

$$d=|\overrightarrow{PA}|\sin\tfrac\pi3=6\sqrt2\cdot\tfrac{\sqrt3}2=\boxed{3\sqrt6}=\sqrt{54}$$

The product route agrees: $(6,0,6)\times(1,1,0)=(-6,6,6)$, of length $\sqrt{108}$,
divided by $|(1,1,0)|=\sqrt2$.

**12 (b)** $(2,-2,2)=2(1,-1,1)$, so the lines are parallel. With $A(3,2,-1)$ on
$l_1$ and $B(2,0,4)$ on $l_2$, $\overrightarrow{AB}=(-1,-2,5)$ and
$\overrightarrow{AB}\times(1,-1,1)=(3,6,3)$:

$$d=\frac{|(3,6,3)|}{|(1,-1,1)|}=\frac{\sqrt{54}}{\sqrt3}=\sqrt{18}=\boxed{3\sqrt2}$$

---

## Timer

$\mathbf u=(1,1,1)$ and $\mathbf v=(3,1,-1)$. A vector perpendicular to both is
along $\mathbf u\times\mathbf v=(-2,4,-2)$, that is along $(1,-2,1)$, so
$\mathbf w=k(1,-2,1)$.

Since $\mathbf w\perp\mathbf v$, the area of $ACD$ is
$\frac12|\mathbf v||\mathbf w|=\frac{\sqrt{11}}2|\mathbf w|=5$, giving
$|\mathbf w|=\frac{10}{\sqrt{11}}$. As $|(1,-2,1)|=\sqrt6$,

$$|k|=\frac{10}{\sqrt{66}}=\frac{5\sqrt{66}}{33}\approx1.231$$

$$\mathbf w=\boxed{\pm\frac{5\sqrt{66}}{33}\begin{pmatrix}1\\-2\\1\end{pmatrix}}
\approx\pm\begin{pmatrix}1.23\\-2.46\\1.23\end{pmatrix}$$
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
