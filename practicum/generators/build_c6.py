"""Собирает практикум C6: плоскости, их встречи с прямыми и друг с другом.

Тридцать второй практикум серии и второй по векторам. Разрез продолжает
C5: тема делится по действию, и C6 берёт всё, где плоскость — сам предмет
вопроса, — 38 баллов из 182 geometry.vectors и 98 из 216
geometry.vectors_3d. Сюда же пришли системы линейных уравнений: три их
случая — это три расположения плоскостей.

Лестница из семи приёмов. Сначала плоскость: точка и нормаль, потом
нормаль из двух направлений. Потом общая часть: прямой и плоскости, двух
плоскостей, трёх плоскостей — она же решение системы. И напоследок
перпендикуляр к плоскости: основание, расстояние, отражение.

Двадцать пятое понятие равенства ответов: **плоскость — тоже множество
точек, а система — набор плоскостей, и её решение — их общая часть**.
Уравнение принимается с любым множителем, векторная форма — с любой
точкой и любыми двумя направлениями в плоскости, общее решение системы —
в любой параметризации.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_c6.py прогоняет по нему весь ноутбук
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
    ROOT, 'practicum/geometry/practicum-c6-planes.ipynb')

TRIGGER = {1: 'plane', 2: 'normal', 3: 'line_plane', 4: 'two_planes', 5: 'three_planes',
           6: 'foot', 7: 'reflection', 8: 'plane', 9: 'normal', 10: 'line_plane',
           11: 'three_planes', 12: 'foot'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1b': '[-3, Rational(-3, 2)]',
    'q1c': '-3',
    'q2a_AB': 'vec(-3, -2, 0)',
    'q2a_AC': 'vec(-2, 1, -7)',
    'q2a_ii': 'Eq(2*x - 3*y - z, 6)',
    'q3b_i': 'vec(5, 4, 2) + lam*vec(1, -1, 1) + mu*vec(2, 1, 3)',
    'q3b_ii': '-18',
    'q3c_i': '18',
    'q3c_ii': '-6',
    'q3e': 'vec(1, 8, -2) + lam*vec(-4, -1, 3)',
    'q4': 'Eq(x - y + z, 15)',
    'q5d': 'Eq(-x + y - z, -5)',
    'q5f_L': 'vec(0, -3, 2) + lam*vec(-1, 1, -1)',
    'q5f': '(-6, 3, -4)',
    'q6_point': '(0, 2, 4)',
    'q6_direction': 'vec(-5, 10, 10)',
    'q7a': 'Eq(2*x - y - 4*z, 0)',
    'q7b': '(Rational(41, 21), Rational(-10, 21), Rational(23, 21))',
    'q8a': 'vec(-1, -1, 1)',
    'q8b': '[Rational(4, 3), 19]',
    'q9a': 'vec(Rational(17, 4) - t/2, Rational(3, 4) + 3*t/2, t)',
    'q9b': '(29, -73.5, -49.5)',
    'q9c_i': '4',
    'q9c_ii': '26',
    'q10a': "'none'",
    'q10a_value': '-15',
    'q10b': 'vec(1, -2, 0) + lam*vec(1, 5, 3)',
    'q10c': 'sqrt(94)/2',
    'q11b_L': '2*(2 + 3*s) - (-3 + 6*s)',
    'q11b_M': '2*(9 + t) - (11 + 2*t)',
    'q11c_i': '(-3, 6, 5)',
    'q11c_ii': '3*sqrt(5)',
    'q11d': '(-3, 0, 8)',
    'q12b': 'vec(-7, -7, 7)',
    'q12c_i': 'Rational(3, 4)',
    'q12c_ii': '(Rational(3, 4), Rational(-5, 4), Rational(-3, 4))',
    'q12d_i': '(Rational(3, 2), -2, Rational(-3, 2))',
    'q12d_ii': 'vec(Rational(3, 2), -2, Rational(-3, 2)) + mu*vec(Rational(3, 4), Rational(-3, 4), Rational(-3, 4))',
    'qt_i': 'Eq(y - 2*z, -4)',
    'qt_ii': '(0, Rational(-4, 5), Rational(8, 5))',
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
# C6 — Planes: where lines and planes meet

**123 marks of the archive, seven techniques, twelve tasks.** Everything the
archive asks about planes from May 2021 to November 2025: the equation of a
plane and its normal, where a line meets a plane, the line where two planes
meet, three planes — and the systems of equations they are — and the
perpendicular from a point: its foot, its length and the reflection.

Paper 2 carries 72 of the marks and Paper 1 carries 51, and on both the work
is the same: a normal, a substitution, one linear equation.

## The one idea

A plane is **a set of points**, just as a line is, and every question about
it is a question about which points belong to it.

$$\mathbf r\cdot\mathbf n=\mathbf a\cdot\mathbf n$$

is one point $\mathbf a$ of the plane and one direction $\mathbf n$ across it.
Any other point of the plane and any multiple of the normal describe **the
same plane**.

## And what follows from it

| the question asks | what it is |
|---|---|
| the equation of a plane | any point on it, any normal — up to a factor |
| where a line meets a plane | the points of the line that satisfy the plane's equation |
| the line of intersection of two planes | the points on both |
| solve a system of three equations | the points on three planes: one, a line of them, or none |
| the reflection of a point | the point as far beyond the plane as the point is in front of it |

## How the checks work

They do not know the answers. A plane is handed to them **the way the
question builds it**, and a point is handed **the conditions** that fix it:

```python
P3 = plane(R, P1, P2)            # through R, perpendicular to P1 and P2
verify_plane('4', q4, P3)

C = unknown('C', 3)
verify_find('11c(i)', q11c_i, C, [on(C, plane_P), perpendicular(C - B, plane_P)])
```

The first is *"is your equation the plane through $R$ perpendicular to both?"*
— any multiple of it passes. The second is *"is your $C$ on the plane, with
$\overrightarrow{BC}$ along the normal?"*: the check solves the conditions itself.

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| $(14,21,-7)$ for $\overrightarrow{AB}\times\overrightarrow{AC}$ | the middle component of a vector product has the wrong sign |
| the right-hand side $-\mathbf n\cdot\mathbf a$ | the right-hand side has the wrong sign |
| the normal of $\Pi_1$ as the direction of the line where $\Pi_1$ and $\Pi_2$ meet | the line lies in $\Pi_1$: its direction is across that normal |
| the value of $\lambda$ where the point is asked | put it into the line |
| the foot of the perpendicular for the reflection | the reflection is as far again beyond it |
| $\lvert\lambda\rvert$ for the distance | the distance is $\lvert\lambda\rvert\,\lvert\mathbf n\rvert$ |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | a plane and its normal | 1–4 |
| 🟡 | a line and a plane, two planes, three planes and systems | 5–9 |
| 🔴 | the perpendicular: its foot, the distance, the reflection | 10–12 |

Every task is a real past-paper question, cited.

**72 of the 123 marks are on a calculator paper, and the calculator does
almost none of the work.** It solves a system with numbers in it — the
markscheme allows that — and takes a square root. A system with a letter, a
normal, a foot and a reflection are done by hand on either paper.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, plane, cross, intersection, unknown

language('en')                 # this notebook is in English, and so are the checks

# plane(Eq(2*x - 3*y - z, 6)), plane(A, n), plane(A, B, C), plane(L1, L2), plane(L, A), plane(R, P1, P2).
# cross(u, v) is the vector product; P1.normal is the normal of the plane P1.
# A plane as an answer: Eq(2*x - 3*y - z, 6), or vec(a) + lam*vec(b) + mu*vec(c).
# intersection(P1, P2) is what the planes share: a point, a line, or None.

print('ready; sympy', sp.__version__)
A, B, C = vec(2, 1, 0), vec(0, 3, 1), vec(1, 0, 2)
print('AB × AC:          ', cross(B - A, C - A))
print('the plane ABC:    ', plane(A, B, C))
print('where it meets z = 0:', intersection(plane(A, B, C), plane(Eq(z, 0))))
""")

md(r"""
---
## Map of the seven techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | a point and a normal | *verify that $A$ lies on the plane*, *$P_2$ is perpendicular to $P_1$*, *the plane meets the axes* | $\mathbf r\cdot\mathbf n=\mathbf a\cdot\mathbf n$ |
| 2 | a normal from two directions | *the plane through $A$, $B$ and $C$*, *contains $L_1$ and $L_2$*, *perpendicular to both planes* | $\mathbf n=\mathbf u\times\mathbf v$ |
| 3 | a line and a plane | *the line meets the plane at $P$*, *verify that the line lies in the plane* | the general point of the line into the plane |
| 4 | two planes | *the line of intersection of $\Pi_1$ and $\Pi_2$* | direction $\mathbf n_1\times\mathbf n_2$, one common point |
| 5 | three planes, a system | *the point where the three planes meet*, *no unique solution*, *intersect in a line* | eliminate, look at the last row |
| 6 | the perpendicular | *the foot of the perpendicular*, *the distance from $L$ to $\Pi$*, *closest to the origin* | the line $\mathbf b+\lambda\mathbf n$ into the plane |
| 7 | the reflection | *the reflection of $B$ in the plane*, *the reflected line* | twice the step to the foot |

Techniques 1–2 build a plane. Techniques 3–5 ask what it shares with a line
and with other planes — and the answer is always a set: a point, a line,
or nothing. Techniques 6–7 walk from a point to the plane along its normal.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. A plane and its normal

## Theory: a point and a normal

A plane is fixed by **one point** $\mathbf a$ on it and **one direction**
$\mathbf n$ across it, the normal. A point $\mathbf r$ is on the plane when
$\mathbf r-\mathbf a$ is perpendicular to $\mathbf n$:

$$\mathbf r\cdot\mathbf n=\mathbf a\cdot\mathbf n$$

Through $(1,4,-2)$ with normal $(2,-1,3)$: the right-hand side is the left-hand
side worked out at the point, $2-4-6=-8$, so

$$2x-y+3z=-8$$

**The normal is read off** any Cartesian equation: the coefficients of $x$,
$y$ and $z$. Multiplying the whole equation by a number, $4x-2y+6z=-16$,
gives the same plane.

**A point is on the plane** when it satisfies the equation:
$(0,-1,-3)$ gives $0+1-9=-8$, so it is; $(1,1,1)$ gives $4$, so it is not.

**Where the plane meets an axis** the other two coordinates are zero: the
$y$-axis at $-y=-8$, the point $(0,8,0)$.

**Two planes are parallel** when their normals are multiples:
$4x-2y+6z=5$ is parallel to this one. **They are perpendicular** when their
normals are: $x+5y+z=0$ has $2-5+3=0$. Do not swap the two tests. With a
letter the test becomes an equation: $ax+2y-z=1$ is perpendicular to our
plane when $2a-2-3=0$, $a=\frac52$.

**A line normal to the plane** uses the normal as its direction:
$\mathbf r=(1,4,-2)+t(2,-1,3)$ — with "$\mathbf r=$", or the markscheme
gives A0.
""")

md(r"""
### Task 1 🟢 — *May 2024 TZ2 Paper 1 Q11(a)–(c), 8 marks*

The plane $P_1$ has equation $2x+6y-2z=5$.

**(a)** Verify that the point $A\left(2,\frac12,1\right)$ lies on the plane $P_1$.

The plane $P_2$ is given by $(k^2-6)x+(2k+3)y+pz=q$, where $p,q,k\in\mathbb R$ and $p\ne0$.

**(b)** In the case where $p=-6$, $P_2$ is perpendicular to $P_1$ and $A$ lies on $P_2$.
Find the value of $k$ and the value of $q$.

For parts (c), (d) and (e) it is now given that $P_2$ is parallel to $P_1$ with $k=3$.

**(c)** Determine the value of $p$.

*Part (a) is one substitution — do it on paper. Parts (d) and (e) are in the
archive.*
""")

code(r"""
k, p, q = symbols('k p q')

q1b = [...]      # [k, q]
q1c = ...        # p

A = vec(2, Rational(1, 2), 1)
P1 = plane(Eq(2*x + 6*y - 2*z, 5), name='P1')
P2 = plane(Eq((k**2 - 6)*x + (2*k + 3)*y + p*z, q), name='P2')

verify_find('1b', q1b, [k, q], [perpendicular(P1, P2.subs(p, -6)), on(A, P2.subs(p, -6))])
verify_find('1c', q1c, p, [parallel(P1, P2.subs(k, 3))])
""")

# ================================================================= теория 2
md(r"""
## Theory: a normal from two directions

Usually the question does not give the normal. It gives **two directions
that lie in the plane**, and the normal is the direction perpendicular to
both — their vector product:

$$\mathbf u\times\mathbf v=\begin{pmatrix}u_2v_3-u_3v_2\\u_3v_1-u_1v_3\\u_1v_2-u_2v_1\end{pmatrix}$$

**Through three points** $P(1,0,1)$, $Q(2,2,1)$, $R(1,1,4)$: the directions
are $\overrightarrow{PQ}=(1,2,0)$ and $\overrightarrow{PR}=(0,1,3)$, and

$$\overrightarrow{PQ}\times\overrightarrow{PR}=\begin{pmatrix}2\cdot3-0\cdot1\\0\cdot0-1\cdot3\\1\cdot1-2\cdot0\end{pmatrix}=\begin{pmatrix}6\\-3\\1\end{pmatrix}$$

Check it: $(6,-3,1)\cdot(1,2,0)=0$ and $(6,-3,1)\cdot(0,1,3)=0$. Then one point
fixes the right-hand side, $6-0+1=7$, and the other two points must give the
same $7$: $Q$ gives $12-6+1$. The plane is $6x-3y+z=7$.

> **The middle component is $u_3v_1-u_1v_3$.** Written the other way round it
> gives $(6,3,1)$, and $Q$ then gives $19$, not $7$ — which is why the check
> with the other points is worth its ten seconds.

| the question gives | the two directions |
|---|---|
| three points $A$, $B$, $C$ | $\overrightarrow{AB}$ and $\overrightarrow{AC}$ |
| a line and a point off it | the line's direction and the vector from a point of the line to the point |
| two lines that meet | their two directions |
| a plane perpendicular to two planes | the two normals |

**The vector form** keeps the two directions instead of the normal:

$$\mathbf r=\begin{pmatrix}1\\0\\1\end{pmatrix}+\lambda\begin{pmatrix}1\\2\\0\end{pmatrix}+\mu\begin{pmatrix}0\\1\\3\end{pmatrix}$$
""")

md(r"""
### Task 2 🟢 — *November 2021 Paper 2 Q11(a), 7 marks*

Three points $A(3,0,0)$, $B(0,-2,0)$ and $C(1,1,-7)$ lie on the plane $\Pi_1$.

**(a)** **(i)** Find the vector $\overrightarrow{AB}$ and the vector $\overrightarrow{AC}$.

**(ii)** Hence find the equation of $\Pi_1$, expressing your answer in the form
$ax+by+cz=d$, where $a,b,c,d\in\mathbb Z$.

*Enter a plane as `Eq(a*x + b*y + c*z, d)`.*
""")

code(r"""
q2a_AB = ...     # AB
q2a_AC = ...     # AC
q2a_ii = ...     # the plane: Eq(a*x + b*y + c*z, d)

A, B, C = vec(3, 0, 0), vec(0, -2, 0), vec(1, 1, -7)

verify_find('2a(i) AB', q2a_AB, B - A)
verify_find('2a(i) AC', q2a_AC, C - A)
verify_plane('2a(ii)', q2a_ii, plane(A, B, C))
""")

md(r"""
### Task 3 🟢 — *November 2025 TZ1 Paper 2 Q12(b), (c), (e), 7 marks*

The equations of two lines, $L_1$ and $L_2$, are given by:

$$L_1:\ \mathbf r_1=""" + col(5, 4, 2) + r"+s" + col(1, -1, 1) + r"""\ \text{ where } s\in\mathbb R$$

$$L_2:\ \frac{x+1}{2}=y-7=\frac{z+5}{3}$$

The position vector of the point of intersection of $L_1$ and $L_2$ is
$\begin{pmatrix}1\\8\\-2\end{pmatrix}$ *(part (a), technique 6 of C5)*.

The plane $\Pi$ contains the lines $L_1$ and $L_2$.

**(b)** **(i)** Write down the equation of $\Pi$, giving your answer in the form
$\mathbf r=\mathbf a+\lambda\mathbf b+\mu\mathbf c$ where $\lambda,\mu\in\mathbb R$.

**(ii)** Given that $\mathbf b\times\mathbf c=\begin{pmatrix}-4\\-1\\3\end{pmatrix}$, show that the
Cartesian equation of $\Pi$ is $4x+y-3z=18$.

The plane intersects the coordinate axes at $P(4.5,0,0)$, $Q(0,q,0)$ and $R(0,0,r)$.

**(c)** Write down the value of **(i)** $q$; **(ii)** $r$.

Another line, $L_3$, is normal to $\Pi$ and passes through the point of intersection
of $L_1$ and $L_2$.

**(e)** Write down an equation for $L_3$ in the form $\mathbf r_3=\mathbf m+\gamma\mathbf n$.

*For (b)(ii) enter $\mathbf a\cdot(\mathbf b\times\mathbf c)$, the right-hand side of
$\mathbf r\cdot(\mathbf b\times\mathbf c)=\mathbf a\cdot(\mathbf b\times\mathbf c)$. In (e) use `lam`
for $\gamma$. Parts (d), (f) and (g) are in C5 and C7.*
""")

code(r"""
q3b_i = ...      # vec(a) + lam*vec(b) + mu*vec(c)
q3b_ii = ...     # a · (b × c)
q3c_i = ...      # q
q3c_ii = ...     # r
q3e = ...        # L3: vec(...) + lam*vec(...)

s = symbols('s')
L1 = line(vec(5, 4, 2) + s*vec(1, -1, 1), s)
L2 = cartesian((x + 1)/2, y - 7, (z + 5)/3)
Pi = plane(L1, L2)
X = vec(1, 8, -2)                        # where L1 and L2 meet
at_q, at_r = unknown('q'), unknown('r')

verify_plane('3b(i)', q3b_i, Pi)
verify_find('3b(ii)', q3b_ii, dot(X, vec(-4, -1, 3)))
verify_find('3c(i)', q3c_i, at_q, [on(vec(0, at_q, 0), Pi)])
verify_find('3c(ii)', q3c_ii, at_r, [on(vec(0, 0, at_r), Pi)])
verify_line('3e', q3e, line(X, Pi.normal))
""")

md(r"""
### Task 4 🟢 — *May 2025 TZ1 Paper 1 Q11(b), 4 marks*

The plane $P_1$ has equation $x+2y+z=0$ and the plane $P_2$ has equation
$x-y-2z=0$. *(Part (a), the acute angle between them, is in C7.)*

A third plane $P_3$ is perpendicular to both $P_1$ and $P_2$.

The unique point of intersection of all three planes is the point $R(5,-5,5)$.

**(b)** Find the Cartesian equation of $P_3$.

*Paper 1: by hand.*
""")

code(r"""
q4 = ...         # P3: Eq(...)

P1 = plane(Eq(x + 2*y + z, 0), name='P1')
P2 = plane(Eq(x - y - 2*z, 0), name='P2')
R = vec(5, -5, 5)

verify_plane('4', q4, plane(R, P1, P2))
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. What lines and planes have in common

## Theory: a line meets a plane

Put **the general point of the line** into the equation of the plane. For
$\Pi:\ x+2y-z=4$ and $\mathbf r=(1,0,2)+\lambda(1,1,1)$ the general point is
$(1+\lambda,\ \lambda,\ 2+\lambda)$:

$$(1+\lambda)+2\lambda-(2+\lambda)=4\quad\Longrightarrow\quad2\lambda-1=4\quad\Longrightarrow\quad\lambda=\tfrac52$$

and the point is the line at that value, $\left(\frac72,\frac52,\frac92\right)$.
**The answer is the point**, not $\lambda$.

The equation in $\lambda$ is linear, and it has three possible outcomes:

| substituting gives | the line |
|---|---|
| one value of $\lambda$ | meets the plane at one point |
| $4=4$, true for every $\lambda$ | lies in the plane |
| $0=4$, true for no $\lambda$ | is parallel to the plane and never meets it |

$\mathbf r=(4,0,0)+\lambda(1,0,1)$ gives $(4+\lambda)-\lambda=4$ for every $\lambda$: it
lies in $\Pi$. $\mathbf r=(0,0,0)+\lambda(1,0,1)$ gives $0=4$: parallel, no common point.

**"Show that the line lies in the plane"** needs the identity. One point of
the line in the plane shows only that the line meets it.
""")

md(r"""
### Task 5 🟡 — *May 2025 TZ3 Paper 1 Q11(d), (f), 7 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D(3,0,2)$ form a
parallelogram, $ABCD$. The diagonals $[AC]$ and $[BD]$ intersect at the point
$E(0,-3,2)$. It is given that $\overrightarrow{AB}\times\overrightarrow{AD}=m\begin{pmatrix}-1\\1\\-1\end{pmatrix}$,
where $m\in\mathbb Z^+$. *($D$, $E$ and $m$ are parts (a)–(c): C5 and C7.)*

The plane, $P_1$, contains the parallelogram $ABCD$.

**(d)** Find the Cartesian equation of $P_1$.

A second plane, $P_2$, has Cartesian equation $5x+y-7z=1$.

The line $L$ passes through $E$ and is perpendicular to $P_1$.

The line $L$ intersects the plane $P_2$ at point $F$.

**(f)** Find the coordinates of $F$.

*For (f) enter the line $L$ too.*
""")

code(r"""
q5d = ...        # P1: Eq(...)
q5f_L = ...      # L: vec(...) + lam*vec(...)
q5f = ...        # F

A, B, C, D, E = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4), vec(3, 0, 2), vec(0, -3, 2)
P1 = plane(A, B, D, name='P1')
P2 = plane(Eq(5*x + y - 7*z, 1), name='P2')
L = line(E, P1.normal)

verify_plane('5d', q5d, P1)
verify_line('5f L', q5f_L, L)
verify_intersection('5f', q5f, L, P2)
""")

# ================================================================= теория 4
md(r"""
## Theory: where two planes meet

Two planes that are not parallel meet in **a line**. It lies in both planes,
so its direction is perpendicular to both normals:

$$\mathbf d=\mathbf n_1\times\mathbf n_2$$

For $x+y+z=6$ and $x-y+2z=5$: $(1,1,1)\times(1,-1,2)=(3,-1,-2)$.

**A point on both** — set one coordinate to zero and solve the other two.
With $y=0$: $x+z=6$ and $x+2z=5$ give $z=-1$, $x=7$. So

$$\mathbf r=\begin{pmatrix}7\\0\\-1\end{pmatrix}+\lambda\begin{pmatrix}3\\-1\\-2\end{pmatrix}$$

**Or solve the two equations with one unknown left free.** $z=t$:
$x+y=6-t$ and $x-y=5-2t$ give $x=\frac{11-3t}2$, $y=\frac{1+t}2$ — the line
$\left(\frac{11}2,\frac12,0\right)+t\left(-\frac32,\frac12,1\right)$. It is the same line: a different point,
and a direction that is $-\frac12$ of the one above.

**"Verify that the line of intersection is …"** — substitute its general point
into both equations. $x=7+3\lambda$, $y=-\lambda$, $z=-1-2\lambda$ give
$7+3\lambda-\lambda-1-2\lambda=6$ and $7+3\lambda+\lambda-2-4\lambda=5$ for every $\lambda$.
One value of $\lambda$ does not verify it: the markscheme gives (M1)A0.

> **The direction is not a normal.** A normal sticks out of its plane; the
> line lies inside both.
""")

md(r"""
### Task 6 🟡 — *May 2023 TZ2 Paper 2 Q6(a), 3 marks*

Consider the two planes

$$\Pi_1:\ 2x-y+2z=6\qquad\Pi_2:\ 4x+3y-z=2$$

Let $L$ be the line of intersection of $\Pi_1$ and $\Pi_2$.

**(a)** Verify that a vector equation of $L$ is
$\mathbf r=\begin{pmatrix}0\\2\\4\end{pmatrix}+\lambda\begin{pmatrix}1\\-2\\-2\end{pmatrix}$, where $\lambda\in\mathbb R$.

*Find both parts of the line from the planes, not from the line printed in
the question: the point of $L$ with $x=0$, and the direction as $\mathbf n_1\times\mathbf n_2$.
Part (b) is in C7.*
""")

code(r"""
q6_point = ...       # the point of L where x = 0
q6_direction = ...   # n1 × n2

P1 = plane(Eq(2*x - y + 2*z, 6), name='Π1')
P2 = plane(Eq(4*x + 3*y - z, 2), name='Π2')

verify_intersection('6 point', q6_point, P1, P2, plane(Eq(x, 0)))
verify_direction('6 direction', q6_direction, intersection(P1, P2))
""")

# ================================================================= теория 5
md(r"""
## Theory: three planes, and the system of equations they are

A system of three linear equations in $x$, $y$, $z$ **is** three planes, and
its solutions are the points on all three. So there are exactly three
answers: one point, a whole line of points, or none.

$$\begin{aligned}x+y+z&=6\\x-y+2z&=5\\2x+cz&=e\end{aligned}$$

**Eliminate.** The first two added give $2x+3z=11$. Take that from the
third: $(c-3)z=e-11$. That is the last row, and the whole question is in it.

| the last row | solutions | the planes |
|---|---|---|
| $c\ne3$ | one, $z=\frac{e-11}{c-3}$ | meet at one point |
| $c=3$ and $e=11$: $0=0$ | infinitely many | share a line |
| $c=3$ and $e\ne11$: $0=e-11$ | none | have no common point |

**"No unique solution"** asks when the coefficients of the last row vanish:
$c=3$. **"Infinitely many solutions"** asks for the right-hand side to vanish
too: $e=11$. Two different questions, and a question often asks both.

**The general solution** for $c=3$, $e=11$ is the line of the previous
theory — one unknown becomes the parameter, the others are written through it.

**A calculator solves a system with numbers**, and the markscheme accepts
*"attempt to solve using GDC"*. It cannot tell you when a row with a letter in
it vanishes — that is done by hand.

A system with no solution looks several ways in space — all three planes
parallel, two of them parallel, or three planes meeting in pairs along three
parallel lines — and the algebra says only that there is no common point.
""")

md(r"""
### Task 7 🟡 — *May 2021 TZ1 Paper 2 Q6, 5 marks*

Consider the planes $\Pi_1$ and $\Pi_2$ with the following equations.

$$\Pi_1:\ 3x+2y+z=6\qquad\Pi_2:\ x-2y+z=4$$

**(a)** Find a Cartesian equation of the plane $\Pi_3$ which is perpendicular to $\Pi_1$
and $\Pi_2$ and passes through the origin $(0,0,0)$.

**(b)** Find the coordinates of the point where $\Pi_1$, $\Pi_2$ and $\Pi_3$ intersect.

*The check for (b) builds $\Pi_3$ itself, so a slip in (a) costs (a) only.*
""")

code(r"""
q7a = ...        # Π3: Eq(...)
q7b = ...        # the point, exact

P1 = plane(Eq(3*x + 2*y + z, 6), name='Π1')
P2 = plane(Eq(x - 2*y + z, 4), name='Π2')
P3 = plane(vec(0, 0, 0), P1, P2, name='Π3')

verify_plane('7a', q7a, P3)
verify_intersection('7b', q7b, P1, P2, P3)
""")

md(r"""
### Task 8 🟡 — *May 2025 TZ2 Paper 2 Q9, 8 marks*

A line $L_1$ has vector equation $\mathbf r=\begin{pmatrix}0\\0\\2\end{pmatrix}+t\begin{pmatrix}1\\0\\1\end{pmatrix}$ where $t\in\mathbb R$.

The plane $P_1$ contains the line $L_1$ and passes through the point $(2,1,5)$.

**(a)** Show that the Cartesian equation of the plane $P_1$ is $x+y-z=-2$.

Consider the three planes

$$P_1:\ x+y-z=-2\qquad P_2:\ 2x+by-z=3\qquad P_3:\ x-y+2z=d$$

where $b,d\in\mathbb R^+$.

The three planes intersect in a line.

**(b)** Find the value of $b$ and the value of $d$.

*For (a) enter the normal you get from the line and the point, before you
compare it with the printed equation.*
""")

code(r"""
b, d = symbols('b d')

q8a = ...        # a normal of P1
q8b = [...]      # [b, d]

L1 = line(vec(0, 0, 2) + t*vec(1, 0, 1), t)
P1 = plane(Eq(x + y - z, -2), name='P1')
P2 = plane(Eq(2*x + b*y - z, 3), name='P2')
P3 = plane(Eq(x - y + 2*z, d), name='P3')

verify_normal_vector('8a', q8a, plane(L1, vec(2, 1, 5)))
verify_find('8b', q8b, [b, d], [meet_in_line(P1, P2, P3), b > 0, d > 0])
""")

md(r"""
### Task 9 🟡 — *November 2025 TZ3 Paper 2 Q7, 6 marks*

Consider the following two equations.

$$2x+6y-8z=13\qquad3x-y+3z=12$$

**(a)** Determine the general solution giving the answer in parametric form.

Consider a third equation $ax+12y-16z=k$, where $a,k\in\mathbb R$.

**(b)** In the case where $a=3$ and $k=-3$, determine the unique solution to the
system of three equations.

**(c)** **(i)** Write down the value of $a$ for which there is no unique solution to
the system of three equations.

**(ii)** Hence, write down the corresponding value of $k$ for which there is an
infinite number of solutions to the system of three equations.

*In (a) enter the solution as `vec(x, y, z)` in terms of `t`. Each equation is
a plane, and the checks treat it as one.*
""")

code(r"""
q9a = ...        # vec(x, y, z) in terms of t
q9b = ...        # (x, y, z)
q9c_i = ...      # a
q9c_ii = ...     # k

a, k = unknown('a'), unknown('k')
first = plane(Eq(2*x + 6*y - 8*z, 13))
second = plane(Eq(3*x - y + 3*z, 12))
third = plane(Eq(a*x + 12*y - 16*z, k))

verify_intersection('9a', q9a, first, second)
verify_intersection('9b', q9b, first, second, third.subs({a: 3, k: -3}))
verify_find('9c(i)', q9c_i, a, [no_unique_meet(first, second, third)])
verify_find('9c(ii)', q9c_ii, k, [meet_in_line(first, second, third)])
""")

# ================================================================= теория 6
md(r"""
---
# 🔴 Part 3. The perpendicular from a point

## Theory: the foot of the perpendicular, and the distance

From $Q(4,1,5)$ to the plane $2x-y+2z=-1$, walk **along the normal**:

$$\mathbf r=\begin{pmatrix}4\\1\\5\end{pmatrix}+\lambda\begin{pmatrix}2\\-1\\2\end{pmatrix}$$

and this line meets the plane where technique 3 says:

$$2(4+2\lambda)-(1-\lambda)+2(5+2\lambda)=-1\quad\Longrightarrow\quad17+9\lambda=-1\quad\Longrightarrow\quad\lambda=-2$$

**The foot** is the line at $\lambda=-2$: $(0,3,1)$.

**The distance** is the length of the step, $\lvert\lambda\rvert\,\lvert\mathbf n\rvert=2\cdot3=6$ —
not $\lvert\lambda\rvert=2$, which counts normals, not units.

The same number comes from $\dfrac{\lvert\mathbf n\cdot\mathbf q-d\rvert}{\lvert\mathbf n\rvert}=\dfrac{\lvert17+1\rvert}3$.
Without the division it is $18$, three times too long.

**The point of a plane closest to the origin** is the foot of the perpendicular
from $O$: the line is $\lambda\mathbf n$.

**A line parallel to a plane, or a parallel plane,** is at the same distance
from it everywhere: take any one of its points and drop the perpendicular
from there.
""")

md(r"""
### Task 10 🔴 — *May 2022 TZ1 Paper 1 Q11, 15 marks*

Consider the three planes

$$\Pi_1:\ 2x-y+z=4\qquad\Pi_2:\ x-2y+3z=5\qquad\Pi_3:\ -9x+3y-2z=32$$

**(a)** Show that the three planes do not intersect.

**(b)** **(i)** Verify that the point $P(1,-2,0)$ lies on both $\Pi_1$ and $\Pi_2$.

**(ii)** Find a vector equation of $L$, the line of intersection of $\Pi_1$ and $\Pi_2$.

**(c)** Find the distance between $L$ and $\Pi_3$.

*For (a) enter what the three planes share — a point, a line or `'none'` — and
the value of $-9x+3y-2z$ along the line where $\Pi_1$ and $\Pi_2$ meet. Paper 1:
(c) is exact.*
""")

code(r"""
q10a = ...           # a point, a line, or 'none'
q10a_value = ...     # −9x + 3y − 2z along the line where Π1 and Π2 meet
q10b = ...           # L: vec(...) + lam*vec(...)
q10c = ...           # the distance between L and Π3, exact

P1 = plane(Eq(2*x - y + z, 4), name='Π1')
P2 = plane(Eq(x - 2*y + 3*z, 5), name='Π2')
P3 = plane(Eq(-9*x + 3*y - 2*z, 32), name='Π3')
L = intersection(P1, P2)

verify_intersection('10a', q10a, P1, P2, P3)
verify_find('10a value', q10a_value, P3.side(L.at(lam)))
verify_intersection('10b(ii)', q10b, P1, P2)
verify_distance('10c', q10c, L, P3, exact=True)
""")

# ================================================================= теория 7
md(r"""
## Theory: the reflection in a plane

The foot of the perpendicular is **halfway** between a point and its
reflection. From $Q(4,1,5)$ the foot was at $\lambda=-2$; the reflection is at
**twice** that, $\lambda=-4$:

$$Q'=\begin{pmatrix}4\\1\\5\end{pmatrix}-4\begin{pmatrix}2\\-1\\2\end{pmatrix}=\begin{pmatrix}-4\\5\\-3\end{pmatrix}$$

Check it: the midpoint of $QQ'$ is $(0,3,1)$, the foot. Or directly,
$Q'=2F-Q$.

**A reflected line.** The line $\mathbf r=(4,1,5)+t(1,2,-3)$ meets the plane at
$t=3$, the point $M(7,7,-4)$, and **$M$ does not move** in the mirror. Any other
point of the line — $Q$ is one — goes to its reflection $Q'$. The reflected line
runs through $M$ and $Q'$:

$$\mathbf r=\begin{pmatrix}7\\7\\-4\end{pmatrix}+\mu\begin{pmatrix}-11\\-2\\1\end{pmatrix}$$

Its direction is not the old one: keeping $(1,2,-3)$ would give a line through
$M$ that stays on the same side.

**A parallel plane on the other side.** The plane $2x-y+2z=17$ through $Q$ is
$6$ units from $2x-y+2z=-1$. The plane $6$ units away on the other side keeps
the normal and passes through $Q'$: $2(-4)-5+2(-3)=-19$, so $2x-y+2z=-19$.
Changing the sign of $17$ gives $-17$, a plane $\frac{16}3$ units away.
""")

md(r"""
### Task 11 🔴 — *November 2023 TZ1 Paper 2 Q12(b)–(d), 13 marks*

Line $L$ is given by the vector equation
$\mathbf r_1=\begin{pmatrix}1\\2\\-3\end{pmatrix}+s\begin{pmatrix}2\\3\\6\end{pmatrix}$ where $s\in\mathbb R$.

Line $M$ is given by the vector equation
$\mathbf r_2=\begin{pmatrix}9\\9\\11\end{pmatrix}+t\begin{pmatrix}4\\1\\2\end{pmatrix}$ where $t\in\mathbb R$.

*(Part (a), where $L$ and $M$ meet, is the timed task of C5.)*

**(b)** Verify that the lines $L$ and $M$ both lie in the plane $P$ given by
$\mathbf r\cdot\begin{pmatrix}0\\2\\-1\end{pmatrix}=7$.

Point $B$ has position vector $\begin{pmatrix}-3\\12\\2\end{pmatrix}$. A line through $B$ perpendicular to
$P$ intersects $P$ at point $C$.

**(c)** **(i)** Find the position vector of $C$.

**(ii)** Hence, find $\lvert\overrightarrow{BC}\rvert$.

**(d)** Find the reflection of the point $B$ in the plane $P$.

*For (b) enter $\mathbf r\cdot(0,2,-1)$ at the general point of each line, in terms
of its parameter: the check tells you whether it is $7$ for every value.*
""")

code(r"""
q11b_L = ...     # r · (0, 2, −1) at the general point of L, in terms of s
q11b_M = ...     # the same for M, in terms of t
q11c_i = ...     # C
q11c_ii = ...    # |BC|
q11d = ...       # the reflection of B

s = symbols('s')
L = line(vec(1, 2, -3) + s*vec(2, 3, 6), s)
M = line(vec(9, 9, 11) + t*vec(4, 1, 2), t)
n = vec(0, 2, -1)
plane_P = plane(Eq(dot(vec(x, y, z), n), 7))
B = vec(-3, 12, 2)
C, image = unknown('C', 3), unknown('image', 3)

verify_find('11b L', q11b_L, dot(L.at(s), n))
verify_find('11b M', q11b_M, dot(M.at(t), n))
verify_find('11c(i)', q11c_i, C, [on(C, plane_P), perpendicular(C - B, plane_P)])
verify_distance('11c(ii)', q11c_ii, B, plane_P)
verify_find('11d', q11d, image, [reflection(image, B, plane_P)])
""")

md(r"""
### Task 12 🔴 — *November 2021 Paper 2 Q11(b)–(d), 14 marks*

Three points $A(3,0,0)$, $B(0,-2,0)$ and $C(1,1,-7)$ lie on the plane $\Pi_1$, and
$\Pi_1$ has equation $2x-3y-z=6$ *(part (a), Task 2)*.

Plane $\Pi_2$ has equation $3x-y+2z=2$.

**(b)** The line $L$ is the intersection of $\Pi_1$ and $\Pi_2$. Verify that the vector
equation of $L$ can be written as
$\mathbf r=\begin{pmatrix}0\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\1\\-1\end{pmatrix}$.

**(c)** The plane $\Pi_3$ is given by $2x-2z=3$. The line $L$ and the plane $\Pi_3$
intersect at the point $P$.

**(i)** Show that at the point $P$, $\lambda=\frac34$.

**(ii)** Hence find the coordinates of $P$.

**(d)** The point $B(0,-2,0)$ lies on $L$.

**(i)** Find the reflection of the point $B$ in the plane $\Pi_3$.

**(ii)** Hence find the vector equation of the line formed when $L$ is reflected
in the plane $\Pi_3$.

*For (b) enter $\mathbf n_1\times\mathbf n_2$. The check for (d)(ii) knows the line
$L$ and the plane $\Pi_3$, not your reflection from (d)(i).*
""")

code(r"""
q12b = ...       # n1 × n2
q12c_i = ...     # λ where L meets Π3
q12c_ii = ...    # the point where L meets Π3
q12d_i = ...     # the reflection of B
q12d_ii = ...    # the reflected line: vec(...) + mu*vec(...)

P1 = plane(Eq(2*x - 3*y - z, 6), name='Π1')
P2 = plane(Eq(3*x - y + 2*z, 2), name='Π2')
P3 = plane(Eq(2*x - 2*z, 3), name='Π3')
L = line(vec(0, -2, 0) + lam*vec(1, 1, -1))
B = vec(0, -2, 0)
at_P, image = unknown('lambda'), unknown('image', 3)

verify_direction('12b', q12b, intersection(P1, P2))
verify_find('12c(i)', q12c_i, at_P, [on(L.at(at_P), P3)])
verify_intersection('12c(ii)', q12c_ii, L, P3)
verify_find('12d(i)', q12d_i, image, [reflection(image, B, P3)])
verify_line('12d(ii)', q12d_ii, mirror(L, P3))
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you
would make first**.

| code | technique |
| --- | --- |
| `plane` | a point and a normal: an equation, a point on it, parallel or perpendicular planes |
| `normal` | a normal from two directions: the vector product |
| `line_plane` | the general point of a line into a plane |
| `two_planes` | the line where two planes meet |
| `three_planes` | three planes, a system of equations, a letter in it |
| `foot` | the perpendicular from a point: the foot, the distance |
| `reflection` | the reflection of a point or a line in a plane |

1. Find the equation of the plane through $(1,-1,2)$ with normal $(3,0,-4)$.
2. Find the equation of the plane containing the points $(0,1,1)$, $(2,0,3)$ and $(1,1,0)$.
3. Find where the line $\mathbf r=(2,1,0)+\lambda(1,-1,3)$ meets the plane $x+y+z=9$.
4. Find a vector equation of the line where $x+2y-z=1$ and $2x-y+z=7$ meet.
5. For which $c$ does the system $x+y=2$, $y+z=3$, $x+cz=1$ have no unique solution?
6. Find the distance from $(4,0,-1)$ to the plane $2x+y-2z=3$.
7. Find the image of the point $(1,2,5)$ in the plane $z=1$.
8. Show that the plane $3x-y+2z=4$ is perpendicular to the plane $x+5y+z=0$.
9. Find a normal to the plane containing $\mathbf r=\lambda(1,1,0)$ and $\mathbf r=\mu(0,1,1)$.
10. Show that the line $\mathbf r=(1,1,1)+\lambda(2,0,-1)$ lies in the plane $x+3y+2z=6$.
11. Determine whether the planes $x+y+z=1$, $x-y=0$ and $2x+z=3$ meet at a single point.
12. Find the point of the plane $x-2y+2z=18$ closest to the origin.
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
## On the clock — *November 2022 Paper 2 Q12(d), 9 marks*

**Nine marks, thirteen minutes.** Calculator allowed, no hints.

Consider the points $A(1,2,3)$, $B(k,-2,1)$ and $C(5,0,2)$, where $k\in\mathbb R$.

**(d)** For $k\ne9$, let $\Pi$ be the plane containing $A$, $B$ and $C$.

**(i)** Find the Cartesian equation of the plane $\Pi$.

**(ii)** Find the coordinates of the point on the plane $\Pi$ which is closest to the
origin $(0,0,0)$.

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_i = ...       # Π: Eq(...)
qt_ii = ...      # the point closest to the origin

k = symbols('k')
Pi = plane(vec(1, 2, 3), vec(k, -2, 1), vec(5, 0, 2))
closest = unknown('X', 3)

verify_plane('timer (i)', qt_i, Pi)
verify_find('timer (ii)', qt_ii, closest, [on(closest, Pi), perpendicular(closest, Pi)])
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** $2\cdot2+6\cdot\frac12-2\cdot1=5$.

**1 (b)** The normals are $(2,6,-2)$ and $(k^2-6,\,2k+3,\,-6)$, and perpendicular planes have
perpendicular normals:

$$2(k^2-6)+6(2k+3)+12=2k^2+12k+18=2(k+3)^2=0\quad\Longrightarrow\quad\boxed{k=-3}$$

— one value, not two. Then $P_2$ is $3x-3y-6z=q$, and $A$ on it gives
$6-\frac32-6=\boxed{q=-\frac32}$.

**1 (c)** With $k=3$ the normal is $(3,9,p)=\frac32(2,6,-2)$ when $\boxed{p=-3}$.

---

**2 (a)(i)** $\overrightarrow{AB}=\boxed{\begin{pmatrix}-3\\-2\\0\end{pmatrix}}$, $\overrightarrow{AC}=\boxed{\begin{pmatrix}-2\\1\\-7\end{pmatrix}}$

**2 (a)(ii)** $\overrightarrow{AB}\times\overrightarrow{AC}=\begin{pmatrix}(-2)(-7)-0\cdot1\\0\cdot(-2)-(-3)(-7)\\(-3)\cdot1-(-2)(-2)\end{pmatrix}=\begin{pmatrix}14\\-21\\-7\end{pmatrix}=7\begin{pmatrix}2\\-3\\-1\end{pmatrix}$,
and $A$ gives $6$: $\boxed{2x-3y-z=6}$. Check with $C$: $2+(-3)+7=6$.

---

**3 (b)(i)** $L_2$ is $(-1,7,-5)+\mu(2,1,3)$. A point of $L_1$ and the directions of both lines:

$$\boxed{\mathbf r=\begin{pmatrix}5\\4\\2\end{pmatrix}+\lambda\begin{pmatrix}1\\-1\\1\end{pmatrix}+\mu\begin{pmatrix}2\\1\\3\end{pmatrix}}$$

**3 (b)(ii)** $\mathbf a\cdot(\mathbf b\times\mathbf c)=(1,8,-2)\cdot(-4,-1,3)=-4-8-6=\boxed{-18}$, so
$-4x-y+3z=-18$, which is $4x+y-3z=18$. Any point of $\Pi$ gives the same $-18$.

**3 (c)** $x=z=0$: $y=\boxed{18}$; $x=y=0$: $-3z=18$, $\boxed{r=-6}$.

**3 (e)** $\boxed{\mathbf r_3=\begin{pmatrix}1\\8\\-2\end{pmatrix}+\gamma\begin{pmatrix}-4\\-1\\3\end{pmatrix}}$

---

**4** $\mathbf n_1\times\mathbf n_2=(1,2,1)\times(1,-1,-2)=(-4+1,\ 1+2,\ -1-2)=(-3,3,-3)=-3(1,-1,1)$.
$R$ gives $5+5+5=15$: $\boxed{x-y+z=15}$.

---

**5 (d)** $m(-1,1,-1)$ is a normal, and $A$ gives $-1-4-0=-5$: $\boxed{-x+y-z=-5}$.

**5 (f)** $L$: $\boxed{\mathbf r=\begin{pmatrix}0\\-3\\2\end{pmatrix}+\lambda\begin{pmatrix}-1\\1\\-1\end{pmatrix}}$. Into $P_2$:
$5(-\lambda)+(-3+\lambda)-7(2-\lambda)=3\lambda-17=1$, $\lambda=6$, and $F=\boxed{(-6,3,-4)}$.

---

**6** With $x=0$: $-y+2z=6$ and $3y-z=2$ give $y=2$, $z=4$ — the point $\boxed{(0,2,4)}$, and it is
on both planes. $\mathbf n_1\times\mathbf n_2=(2,-1,2)\times(4,3,-1)=\boxed{(-5,10,10)}=-5(1,-2,-2)$,
perpendicular to both normals. So $L$ is the printed line.

---

**7 (a)** $(3,2,1)\times(1,-2,1)=(4,-2,-8)=2(2,-1,-4)$, through the origin: $\boxed{2x-y-4z=0}$.

**7 (b)** Solving the three equations,
$\boxed{\left(\frac{41}{21},-\frac{10}{21},\frac{23}{21}\right)}=(1.95,-0.476,1.10)$.

---

**8 (a)** Two directions in $P_1$: $(1,0,1)$ along $L_1$ and $(2,1,5)-(0,0,2)=(2,1,3)$.
$(1,0,1)\times(2,1,3)=\boxed{(-1,-1,1)}$, and $(0,0,2)$ gives $-2$: $-x-y+z=2$, which is
$x+y-z=-2$.

**8 (b)** $P_2-2P_1$: $(b-2)y+z=7$. $P_3-P_1$: $-2y+3z=d+2$. Three times the first minus the
second: $(3b-4)y=19-d$. A line of solutions needs $0=0$:

$$\boxed{b=\tfrac43,\quad d=19}$$

---

**9 (a)** Let $z=t$. Then $x=\frac{17}4-\frac t2$, $y=\frac34+\frac{3t}2$:

$$\boxed{\begin{pmatrix}x\\y\\z\end{pmatrix}=\begin{pmatrix}17/4-t/2\\3/4+3t/2\\t\end{pmatrix}}$$

**9 (b)** Into $3x+12y-16z=-3$: $\frac{87}4+\frac t2=-3$, $t=-\frac{99}2$, so
$\boxed{(29,\ -73.5,\ -49.5)}$.

**9 (c)** $12y-16z=2(6y-8z)$, so the third equation is twice the first when $\boxed{a=4}$; then the
right-hand side must be $2\cdot13$: $\boxed{k=26}$.

---

**10 (a)** $\Pi_2-2\Pi_1$: $-3x+z=-3$. $\Pi_3+3\Pi_1$: $-3x+z=44$. The same left side, two
different right sides: no common point, $\boxed{\text{none}}$. Along the line where $\Pi_1$ and
$\Pi_2$ meet, $-9x+3y-2z=\boxed{-15}$ for every $\lambda$, never $32$.

**10 (b)** (i) $2+2+0=4$ and $1+4+0=5$. (ii) $(2,-1,1)\times(1,-2,3)=(-1,-5,-3)$:

$$\boxed{\mathbf r=\begin{pmatrix}1\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\5\\3\end{pmatrix}}$$

**10 (c)** $(1,5,3)\cdot(-9,3,-2)=0$: $L$ is parallel to $\Pi_3$. From $P$ along the normal,
$(1-9t,\,-2+3t,\,-2t)$: $-15+94t=32$, $t=\frac12$, and the distance is
$\frac12\sqrt{94}=\boxed{\frac{\sqrt{94}}2}$.

---

**11 (b)** $2(2+3s)-(-3+6s)=\boxed{7}$ and $2(9+t)-(11+2t)=\boxed{7}$, for every $s$ and every $t$.

**11 (c)** $(-3,\,12+2\lambda,\,2-\lambda)$ into $P$: $2(12+2\lambda)-(2-\lambda)=22+5\lambda=7$, $\lambda=-3$:
$\overrightarrow{OC}=\boxed{\begin{pmatrix}-3\\6\\5\end{pmatrix}}$, and
$\lvert\overrightarrow{BC}\rvert=3\,\lvert(0,2,-1)\rvert=\boxed{3\sqrt5}=6.71$.

**11 (d)** $2\lambda=-6$: $\boxed{(-3,0,8)}$.

---

**12 (b)** $(2,-3,-1)\times(3,-1,2)=\boxed{(-7,-7,7)}=-7(1,1,-1)$, and $(0,-2,0)$ is on both:
$6=6$, $2=2$.

**12 (c)** $2\lambda-2(-\lambda)=4\lambda=3$, $\boxed{\lambda=\frac34}$, and
$P=\boxed{\left(\frac34,-\frac54,-\frac34\right)}$.

**12 (d)(i)** From $B$ along $(2,0,-2)$: $(2\mu,-2,-2\mu)$ into $\Pi_3$ gives $8\mu=3$, $\mu=\frac38$ —
the foot $\left(\frac34,-2,-\frac34\right)$. Twice as far: $\boxed{\left(\frac32,-2,-\frac32\right)}$.

**12 (d)(ii)** $P$ stays, $B$ goes to $B'$: the direction $B'-P=\left(\frac34,-\frac34,-\frac34\right)$ and

$$\boxed{\mathbf r=\begin{pmatrix}3/2\\-2\\-3/2\end{pmatrix}+\mu\begin{pmatrix}3/4\\-3/4\\-3/4\end{pmatrix}}$$

---

## Timer

**(i)** $\overrightarrow{AB}=(k-1,-4,-2)$, $\overrightarrow{AC}=(4,-2,-1)$ and
$\overrightarrow{AB}\times\overrightarrow{AC}=(0,\ k-9,\ 18-2k)=(k-9)(0,1,-2)$. Since $k\ne9$ the normal is
$(0,1,-2)$, and $A$ gives $2-6$: $\boxed{y-2z=-4}$.

**(ii)** From $O$ along the normal, $(0,\lambda,-2\lambda)$: $\lambda+4\lambda=-4$, $\lambda=-\frac45$, and the
point is $\boxed{\left(0,-\frac45,\frac85\right)}=(0,-0.8,1.6)$.
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
