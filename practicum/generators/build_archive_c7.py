"""Собирает архивный ноутбук C7: все измерения темы подряд.

Двадцать первый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3, D4, D5, D6, C5 и C6. Практикум учит: лестница из
приёмов, теория перед каждым, три уровня сложности, тренажёр распознавания,
задание на время. Архив не учит. Он даёт набивать руку: **вся тема подряд,
по тем же семи приёмам, без единой строчки теории**. Двадцать вопросов,
99 баллов.

Разметка взята из карточки geometry-vectors-product.yaml: поле blocks у
каждого приёма. Ноябрь 2023 года стоит в корпусе дважды, TZ1 и TZ2 одной
бумаги; здесь он один раз. Девять баллов доли — поворот гиперболы ноября
2021 Q1(g) и площадь на диаграмме Аргана мая 2025 TZ2 Q12(c) — сюда не
входят: векторов в них нет, и в карточке они записаны в leftovers.

Части одного вопроса разнесены по своим приёмам: ноябрь 2023 Q8 — в §§ 1 и
2, май 2024 TZ1 Q12 — в §§ 2 и 4, май 2025 TZ2 Paper 3 Q2 — в §§ 1 и 5,
ноябрь 2025 TZ1 Q12 — в §§ 2 и 3, май 2025 TZ3 Q11 — в §§ 2 и 5. Условие
каждого пункта повторено целиком, насколько оно нужно пункту.

«Show that» здесь проверяется по промежуточной строке: само векторное
произведение до сравнения с напечатанным, угол до того, как он назван
прямым, левая часть тождества, записанная через длины и угол.

Хешей нет ни одного: всякий ответ темы — вектор, площадь, объём, угол,
точка или расстояние, и всякий меряется самой фигурой вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_c7.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/geometry/archive-c7-measuring.ipynb')

ANSWERS = {
    # § 1. The vector product
    'q1_1': 'vec(2 - 3*p, -2 - p, p**2 - 2*p)',
    'q1_2': 'vec(0, -36, 0)',
    # § 2. Area
    'q2_1a': '6.75',
    'q2_1b': '1.30',
    'q2_2a': '12',
    'q2_2b': '12*sqrt(3)',
    'q2_3': '68.8',
    'q2_4': '[vec(5*sqrt(66)/33, -10*sqrt(66)/33, 5*sqrt(66)/33),\n            '
            'vec(-5*sqrt(66)/33, 10*sqrt(66)/33, -5*sqrt(66)/33)]',
    # § 3. Volume
    'q3_1': '351',
    # § 4. The identity
    'q4_1a': 'A**2*B**2*sin(th)**2',
    'q4_1b': 'A**2*B**2*cos(th)**2',
    'q4_2': 'U**2*V**2*cos(th)**2 + U**2*V**2*sin(th)**2',
    'q4_3a': '2*sqrt(6)',
    'q4_3b': 'sqrt(3)',
    'q4_3c': '[[1, 2], [Rational(7, 5), Rational(4, 5)]]',
    # § 5. Angles with a plane
    'q5_1': '60',
    'q5_2': 'Rational(1, 5)',
    'q5_3': '0.932',
    'q5_4': '90',
    'q5_5': '11.1',
    'q5_6': '29.1',
    # § 6. The closest point
    'q6_1a': '10 + 30*mu',
    'q6_1b': '(Rational(1, 3), Rational(-10, 3), Rational(7, 3))',
    'q6_2': '(Rational(4, 3), Rational(-2, 3), Rational(4, 3))',
    # § 7. The distance to a line
    'q7_1': '3*sqrt(6)',
    'q7_2': '3*sqrt(2)',
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
    return (r'\begin{pmatrix}' + r'\\'.join(str(i) for i in items) + r'\end{pmatrix}')


md(r"""
# C7 archive — measuring in space, all of it

**Twenty questions, 99 marks.** Every question the archive measures with
vectors, from May 2021 to November 2025, in the order of the seven techniques
rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-c7-measuring.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The vector product | 2 | 6 |
| 2 | Area | 4 | 19 |
| 3 | Volume | 1 | 4 |
| 4 | The identity | 3 | 19 |
| 5 | Angles with a plane | 6 | 30 |
| 6 | The closest point on a line | 2 | 12 |
| 7 | The distance to a line | 2 | 9 |

The checks are the same ones the practicum uses and they store nothing: each
is handed the figure exactly as the question names it —
`verify_measure('...', q, 'triangle', A, B, C)`, `verify_cross('...', q, B - A, C - A)`,
`verify_distance('...', q, l1, l2)`, `verify_angle('...', q, P1, P2)` — and a point the
question describes in words is handed **the conditions** that fix it:
`on(N, L)`, `perpendicular(N - point_P, L)`. Three significant figures, unless the
question asks otherwise.

**Parts of one question are split by technique.** November 2023 Q8 appears in
§§ 1 and 2; May 2024 TZ1 Q12 in §§ 2 and 4; the Paper 3 sphere of May 2025 TZ2
in §§ 1 and 5. Each part repeats what it needs.

**A *show that* is checked by the line before the given result:** the vector
product itself before it is compared with the printed column, the angle before
it is called right, the left-hand side of the identity written with lengths and
the angle.

Enter a vector as `vec(a, b, c)` or `(a, b, c)`; `lam` and `mu` are $\lambda$
and $\mu$.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, cross, measure, plane, unknown

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. The vector product

**Two questions, 6 marks.** Two vectors in, one vector out — with a letter in
the components and without.
""")

md(r"""
### 1.1 — *November 2023 TZ1 Paper 2 Q8(a), 4 marks*

Three points are given by $A(0,p,2)$, $B(1,1,1)$ and $C(p,0,4)$, where $p$ is a
positive constant.

Show that $\overrightarrow{AB}\times\overrightarrow{AC}=""" + col('2-3p', '-2-p', 'p^2-2p') + r"""$.

*Enter the product you computed, before comparing it with the printed column.*
""")

code(r"""
p = symbols('p', positive=True)
A, B, C = vec(0, p, 2), vec(1, 1, 1), vec(p, 0, 4)

q1_1 = ...       # AB × AC

verify_cross('1.1', q1_1, B - A, C - A)
""")

md(r"""
### 1.2 — *May 2025 TZ2 Paper 3 Q2(c)(i), 2 marks*

A sphere of radius 6 is centred at the origin $O$; lengths are in thousands of
kilometres. The North Pole $P$ and a point $A$ on the equator have position
vectors $\mathbf p=""" + col(0, 0, 6) + r"$ and $\mathbf a=" + col(6, 0, 0) + r"""$.

Find the vector $\mathbf a\times\mathbf p$.
""")

code(r"""
a, p_pole = vec(6, 0, 0), vec(0, 0, 6)

q1_2 = ...       # a × p

verify_cross('1.2', q1_2, a, p_pole)
""")

# ============================================================ § 2
md(r"""
---
# § 2. Area

**Four questions, 19 marks.** The length of a vector product is the area of the
parallelogram on its two factors; a triangle is half of it. With a letter in
the points the area becomes a function, and *smallest* means its minimum.
""")

md(r"""
### 2.1 — *November 2023 TZ1 Paper 2 Q8(b), (c), 5 marks*

Continuing 1.1, with $A(0,p,2)$, $B(1,1,1)$, $C(p,0,4)$ and $p>0$:

**(a)** Hence, find the smallest possible value of $|\overrightarrow{AB}\times\overrightarrow{AC}|^2$.

**(b)** Hence, find the smallest possible area of triangle $ABC$.

*Three significant figures.*
""")

code(r"""
p = symbols('p', positive=True)
A, B, C = vec(0, p, 2), vec(1, 1, 1), vec(p, 0, 4)
product = cross(B - A, C - A)

q2_1a = ...      # the smallest |AB × AC|²
q2_1b = ...      # the smallest area of ABC

verify_optimum('2.1(a)', q2_1a, dot(product, product), p, Interval(0, oo), 'min')
verify_optimum('2.1(b)', q2_1b, measure('triangle', A, B, C), p, Interval(0, oo), 'min')
""")

md(r"""
### 2.2 — *May 2025 TZ3 Paper 1 Q11(c), 4 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D(3,0,2)$ form a
parallelogram $ABCD$, where $D$ is diagonally opposite $B$.

**(a)** Given that $\overrightarrow{AB}\times\overrightarrow{AD}=m""" + col(-1, 1, -1) + r"""$,
where $m\in\mathbb Z^+$, find the value of $m$.

**(b)** Hence, find the area of parallelogram $ABCD$.

*Give (b) exactly.*
""")

code(r"""
m = symbols('m')
A, B, C, D = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4), vec(3, 0, 2)

q2_2a = ...      # m
q2_2b = ...      # the area of ABCD

verify_find('2.2(a)', q2_2a, m, [Eq(cross(B - A, D - A), m*vec(-1, 1, -1))])
verify_measure('2.2(b)', q2_2b, 'parallelogram', A, B, C, D, exact=True)
""")

md(r"""
### 2.3 — *November 2025 TZ1 Paper 2 Q12(d), 5 marks*

The plane $\Pi$ has Cartesian equation $4x+y-3z=18$ and meets the coordinate axes
at $P(4.5,0,0)$, $Q(0,18,0)$ and $R(0,0,-6)$.

Use a vector method to find the area of the triangle $PQR$.

*Three significant figures.*
""")

code(r"""
point_P, Q, R = vec(Rational(9, 2), 0, 0), vec(0, 18, 0), vec(0, 0, -6)

q2_3 = ...       # the area of PQR

verify_measure('2.3', q2_3, 'triangle', point_P, Q, R)
""")

md(r"""
### 2.4 — *May 2024 TZ1 Paper 2 Q12(c), 5 marks*

A triangle $ABC$ has vertices $A(0,1,2)$, $B(1,2,3)$ and $C(3,2,1)$, and
$\mathbf u=\overrightarrow{AB}$, $\mathbf v=\overrightarrow{AC}$. Consider a new point
$D$, and let $\mathbf w=\overrightarrow{CD}$.

It is given that $\mathbf u\cdot\mathbf w=\mathbf v\cdot\mathbf w=0$ and that the area
of triangle $ACD$ is $5$ square units.

Find the possible vectors for $\mathbf w$.

*Enter both, as a list of two vectors.*
""")

code(r"""
A, B, C = vec(0, 1, 2), vec(1, 2, 3), vec(3, 2, 1)
u, v = B - A, C - A
w = unknown('w', 3)
D = C + w

q2_4 = [...]     # both possible w

verify_find('2.4', q2_4, w, [perpendicular(w, u), perpendicular(w, v),
                             Eq(measure('triangle', A, C, D), 5)])
""")

# ============================================================ § 3
md(r"""
---
# § 3. Volume

**One question, 4 marks.** A pyramid is a third of base times height — or a
sixth of the determinant of its three edges from the apex.
""")

md(r"""
### 3.1 — *November 2025 TZ1 Paper 2 Q12(g), 4 marks*

Continuing 2.3: the plane $\Pi$ meets the axes at $P(4.5,0,0)$, $Q(0,18,0)$ and
$R(0,0,-6)$, and the line $L_3$, normal to $\Pi$ through $(1,8,-2)$, contains the
point $S(-11,5,7)$ at $\gamma=3$.

Hence, find the volume of pyramid $PQRS$.

*The answer is a whole number.*
""")

code(r"""
point_P, Q, R = vec(Rational(9, 2), 0, 0), vec(0, 18, 0), vec(0, 0, -6)
S = vec(-11, 5, 7)

q3_1 = ...       # the volume of PQRS

verify_measure('3.1', q3_1, 'pyramid', S, point_P, Q, R, exact=True)
""")

# ============================================================ § 4
md(r"""
---
# § 4. The identity

**Three questions, 19 marks.** $(\mathbf u\cdot\mathbf v)^2+|\mathbf u\times\mathbf v|^2=|\mathbf u|^2|\mathbf v|^2$
— and the length it hands you when nobody gives it.
""")

md(r"""
### 4.1 — *May 2021 TZ2 Paper 1 Q5, 4 marks*

Given any two non-zero vectors $\mathbf a$ and $\mathbf b$, show that
$|\mathbf a\times\mathbf b|^2=|\mathbf a|^2|\mathbf b|^2-(\mathbf a\cdot\mathbf b)^2$.

*Enter the two ends of the proof: the left-hand side and the last term of the
right-hand side, each written with $A=|\mathbf a|$, $B=|\mathbf b|$ and $\theta$.
Use `th` for $\theta$.*
""")

code(r"""
A, B, th = symbols('A B th')
a = vec(*symbols('a1 a2 a3'))            # any two vectors, in components
b = vec(*symbols('b1 b2 b3'))
letters = {A: mag(a), B: mag(b), th: angle(a, b)}

q4_1a = ...      # |a × b|², written with A, B and th
q4_1b = ...      # (a · b)², written with A, B and th

verify_formula('4.1(a)', q4_1a, dot(cross(a, b), cross(a, b)), letters)
verify_formula('4.1(b)', q4_1b, dot(a, b)**2, letters)
""")

md(r"""
### 4.2 — *May 2024 TZ1 Paper 2 Q12(a), 2 marks*

Consider the non-zero vectors $\mathbf u$ and $\mathbf v$, and let $\theta$ be the
angle between them. Using the definitions of $\mathbf u\cdot\mathbf v$ and
$\mathbf u\times\mathbf v$ in terms of $|\mathbf u|$, $|\mathbf v|$ and $\theta$,
show that $(\mathbf u\cdot\mathbf v)^2+|\mathbf u\times\mathbf v|^2=|\mathbf u|^2|\mathbf v|^2$.

*Enter the left-hand side written with $U=|\mathbf u|$, $V=|\mathbf v|$ and `th` —
before you simplify it.*
""")

code(r"""
U, V, th = symbols('U V th')
one = vec(*symbols('m1 m2 m3'))          # any two vectors, in components
two = vec(*symbols('n1 n2 n3'))

q4_2 = ...       # (u · v)² + |u × v|², written with U, V and th

verify_formula('4.2', q4_2, dot(one, two)**2 + dot(cross(one, two), cross(one, two)),
               {U: mag(one), V: mag(two), th: angle(one, two)})
""")

md(r"""
### 4.3 — *May 2024 TZ1 Paper 2 Q12(b), 13 marks*

A triangle $ABC$ has vertices $A(0,1,2)$, $B(p,q,3)$ and $C(3,2,1)$, with
$p,q\in\mathbb R$. The vectors are $\mathbf u=\overrightarrow{AB}$ and
$\mathbf v=\overrightarrow{AC}$. It is given that $\mathbf u\cdot\mathbf v=3$ and that
the area of triangle $ABC$ is $\sqrt6$.

**(a)** Find the value of $|\mathbf u\times\mathbf v|$.

**(b)** Hence, or otherwise, find the value of $|\mathbf u|$.

**(c)** Hence, or otherwise, find the possible values of $p$ and the corresponding
values of $q$.

*For (c) enter both pairs, as `[[p, q], [p, q]]`.*
""")

code(r"""
p, q = unknown('p'), unknown('q')         # the two the question asks for
A, B, C = vec(0, 1, 2), vec(p, q, 3), vec(3, 2, 1)
u, v = B - A, C - A
given = [Eq(measure('triangle', A, B, C), sqrt(6)), Eq(dot(u, v), 3)]

q4_3a = ...      # |u × v|
q4_3b = ...      # |u|
q4_3c = [...]    # [[p, q], [p, q]]

verify_find('4.3(a)', q4_3a, mag(cross(u, v)), given)
verify_find('4.3(b)', q4_3b, mag(u), given)
verify_find('4.3(c)', q4_3c, [p, q], given)
""")

# ============================================================ § 5
md(r"""
---
# § 5. Angles with a plane

**Six questions, 30 marks.** A plane has no direction, only a normal: the angle
between two planes is the acute angle between their normals, and the angle a line
makes with a plane is what is left of a right angle. On a sphere the same rule
appears between two vector products.
""")

md(r"""
### 5.1 — *May 2025 TZ1 Paper 1 Q11(a), 6 marks*

The plane $P_1$ has equation $x+2y+z=0$ and the plane $P_2$ has equation
$x-y-2z=0$. The acute angle between the planes $P_1$ and $P_2$ is $\theta$.

Show that $\theta=60°$.

*Enter the angle in degrees.*
""")

code(r"""
P1 = plane(Eq(x + 2*y + z, 0), name='P1')
P2 = plane(Eq(x - y - 2*z, 0), name='P2')

q5_1 = ...       # θ in degrees

verify_angle('5.1', q5_1, P1, P2, deg=True)
""")

md(r"""
### 5.2 — *May 2025 TZ3 Paper 1 Q11(e), 3 marks*

The plane $P_1$ contains the parallelogram $ABCD$ of 2.2 and has equation
$-x+y-z=-5$. A second plane $P_2$ has equation $5x+y-7z=1$. The acute angle
between $P_1$ and $P_2$ is $\theta$.

Show that $\cos\theta=\frac15$.

*Exactly.*
""")

code(r"""
P1 = plane(Eq(-x + y - z, -5), name='P1')
P2 = plane(Eq(5*x + y - 7*z, 1), name='P2')

q5_2 = ...       # cos θ

verify_angle('5.2', q5_2, P1, P2, cosine=True, exact=True)
""")

md(r"""
### 5.3 — *May 2023 TZ1 Paper 2 Q8, 7 marks*

The angle between a line and a plane is $\alpha$, where $\alpha\in\mathbb R$,
$0<\alpha<\frac\pi2$. The equation of the line is
$\dfrac{x-1}{3}=\dfrac{y+2}{2}=5-z$, and the equation of the plane is
$4x+(\cos\alpha)y+(\sin\alpha)z=1$.

Find the value of $\alpha$.

*Three significant figures, in radians.*
""")

code(r"""
alpha = symbols('alpha', positive=True)
L = cartesian((x - 1)/3, (y + 2)/2, 5 - z)
Pi = plane(Eq(4*x + cos(alpha)*y + sin(alpha)*z, 1))

q5_3 = ...       # α in radians

verify_find('5.3', q5_3, alpha, [Eq(angle(L, Pi), alpha)])
""")

md(r"""
### 5.4 — *May 2025 TZ2 Paper 3 Q2(c)(ii), 3 marks*

On the sphere of 1.2, with $\mathbf p=(0,0,6)$, $\mathbf n=(0,6,0)$ and
$\mathbf a=(6,0,0)$: $P$, $N$ and $A$, and the arcs joining them, form a spherical
triangle, and the angle at the vertex $A$ is defined as the angle between
$\mathbf a\times\mathbf p$ and $\mathbf a\times\mathbf n$.

Show that the angle at vertex $A$ in the spherical triangle is $90°$.

*Enter the angle in degrees.*
""")

code(r"""
a, p_pole, n = vec(6, 0, 0), vec(0, 0, 6), vec(0, 6, 0)

q5_4 = ...       # the angle at A, in degrees

verify_angle('5.4', q5_4, cross(a, p_pole), cross(a, n), deg=True)
""")

md(r"""
### 5.5 — *May 2025 TZ2 Paper 3 Q2(e), 5 marks*

On the same sphere, Moscow $M$ has $\mathbf m=""" + col(0, r'6\cos\theta', r'6\sin\theta') + r"$ with $\theta=57.3°$, and Bogotá $B$ has $\mathbf b=" + col(r'6\sin120°', r'6\cos120°', 0) + r"""$.

Find the shortest distance from Bogotá to Moscow on the sphere.

*In thousands of kilometres, three significant figures.*
""")

code(r"""
theta = 57.3*pi/180                       # 57.3 degrees, from part (d)
b = vec(6*sin(2*pi/3), 6*cos(2*pi/3), 0)  # 120 degrees west of Nairobi
m = vec(0, 6*cos(theta), 6*sin(theta))

q5_5 = ...       # the distance along the sphere

verify_arc('5.5', q5_5, 6, b, m)
""")

md(r"""
### 5.6 — *May 2025 TZ2 Paper 3 Q2(f), 6 marks*

The bearing from $B$ to $M$ is the angle at the vertex $B$ in the spherical triangle
$BMP$ — that is, by the method of 5.4, the angle between $\mathbf b\times\mathbf m$
and $\mathbf b\times\mathbf p$.

Using the method from part (c), find the bearing from Bogotá to Moscow.

*In degrees, three significant figures.*
""")

code(r"""
theta = 57.3*pi/180
b = vec(6*sin(2*pi/3), 6*cos(2*pi/3), 0)
m = vec(0, 6*cos(theta), 6*sin(theta))
p_pole = vec(0, 0, 6)

q5_6 = ...       # the bearing, in degrees

verify_angle('5.6', q5_6, cross(b, m), cross(b, p_pole), deg=True)
""")

# ============================================================ § 6
md(r"""
---
# § 6. The closest point on a line

**Two questions, 12 marks.** The point of a line nearest a given point is the
one where the segment to it crosses the line at a right angle.
""")

md(r"""
### 6.1 — *November 2025 TZ3 Paper 1 Q10(d), (e), 7 marks*

The point $P(-1,1,-13)$ lies on the line $L_1$. The line $L_2$ passes through
$A(2,-4,2)$ and $B(7,-6,1)$, so $\mathbf s=""" + col(2, -4, 2) + r"+\mu" + col(5, -2, -1) + r"""$.
The point $N$ lies on $L_2$.

**(a)** Find $\overrightarrow{PN}\cdot\overrightarrow{AB}$ in terms of $\mu$.

**(b)** Given that $N$ is the point on $L_2$ that lies closest to $P$, find the
coordinates of $N$.

*Use `mu` for $\mu$; give (b) exactly.*
""")

code(r"""
point_P, A, B = vec(-1, 1, -13), vec(2, -4, 2), vec(7, -6, 1)
L2 = line(A + mu*(B - A), mu, name='L2')
N = unknown('N', 3)

q6_1a = ...      # PN · AB, in terms of mu
q6_1b = ...      # N

verify_find('6.1(a)', q6_1a, dot(L2.at(mu) - point_P, B - A))
verify_find('6.1(b)', q6_1b, N, [on(N, L2), perpendicular(N - point_P, L2)])
""")

md(r"""
### 6.2 — *May 2023 TZ2 Paper 2 Q6(b), 5 marks*

$L$ is the line of intersection of the planes $\Pi_1:2x-y+2z=6$ and
$\Pi_2:4x+3y-z=2$, and a vector equation of it is
$\mathbf r=""" + col(0, 2, 4) + r"+\lambda" + col(1, -2, -2) + r"""$.

Find the coordinates of the point $P$ on $L$ that is nearest to the origin.

*Exactly.*
""")

code(r"""
L = line(vec(0, 2, 4) + lam*vec(1, -2, -2), lam, name='L')
closest = unknown('N', 3)

q6_2 = ...       # the point of L nearest to the origin

verify_find('6.2', q6_2, closest, [on(closest, L), perpendicular(closest, L)])
""")

# ============================================================ § 7
md(r"""
---
# § 7. The distance to a line

**Two questions, 9 marks.** The shortest distance to a line is the length of the
perpendicular — $|\overrightarrow{AP}\times\mathbf v|/|\mathbf v|$, and dividing by
$|\mathbf v|$ is not optional.
""")

md(r"""
### 7.1 — *May 2023 TZ1 Paper 1 Q12(c), 4 marks*

Two lines $L_1$ and $L_2$ meet at $P$, and $A(2t,8,3)$ lies on $L_2$, where $t>0$.
The acute angle between the lines is $\frac\pi3$, the direction vector of $L_1$ is
$(1,1,0)$, and $\overrightarrow{PA}=(2t,0,3+t)$. Parts (a) and (b) give $t=3$, so
$P(0,8,-3)$ and $A(6,8,3)$.

Hence or otherwise, find the shortest distance from $A$ to $L_1$.

*Exactly.*
""")

code(r"""
L1 = line(vec(0, 8, -3) + lam*vec(1, 1, 0), lam, name='L1')
A = vec(6, 8, 3)

q7_1 = ...       # the shortest distance from A to L1

verify_distance('7.1', q7_1, A, L1, exact=True)
""")

md(r"""
### 7.2 — *May 2021 TZ2 Paper 1 Q8(b), 5 marks*

The lines $l_1$ and $l_2$ have vector equations

$$l_1:\ \mathbf r_1=""" + col(3, 2, -1) + r"+\lambda" + col(2, -2, 2) + r"\qquad l_2:\ \mathbf r_2=" + col(2, 0, 4) + r"+\mu" + col(1, -1, 1) + r"""$$

Part (a) shows that $l_1$ and $l_2$ do not intersect.

Find the minimum distance between $l_1$ and $l_2$.

*Exactly.*
""")

code(r"""
l1 = line(vec(3, 2, -1) + lam*vec(2, -2, 2), lam, name='l1')
l2 = line(vec(2, 0, 4) + mu*vec(1, -1, 1), mu, name='l2')

q7_2 = ...       # the minimum distance between l1 and l2

verify_distance('7.2', q7_2, l1, l2, exact=True)
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1

**1.1** $\overrightarrow{AB}=(1,1-p,-1)$, $\overrightarrow{AC}=(p,-p,2)$:
$\boxed{(2-3p,\ -2-p,\ p^2-2p)}$.

**1.2** $(6,0,0)\times(0,0,6)=\boxed{(0,-36,0)}$.

---

## § 2

**2.1 (a)** $(2-3p)^2+(2+p)^2+(p^2-2p)^2=p^4-4p^3+14p^2-8p+8$, least at
$p=0.3264\ldots$: $\boxed{6.75}$. **(b)** $\frac12\sqrt{6.75257\ldots}=\boxed{1.30}$ units².

**2.2 (a)** $(-4,-2,2)\times(2,4,2)=(-12,12,-12)$: $\boxed{m=12}$.
**(b)** $12\sqrt3=\boxed{12\sqrt3}\approx20.8$.

**2.3** $\overrightarrow{PQ}\times\overrightarrow{PR}=(-108,-27,81)$, so
$\frac12\sqrt{18954}=\boxed{68.8}$.

**2.4** $\mathbf w\parallel\mathbf u\times\mathbf v=(-2,4,-2)$, and
$\frac12|\mathbf v||\mathbf w|=5$ gives $|\mathbf w|=\frac{10}{\sqrt{11}}$:
$\boxed{\pm\frac{5\sqrt{66}}{33}(1,-2,1)}\approx\pm(1.23,-2.46,1.23)$.

---

## § 3

**3.1** Height $3|(-4,-1,3)|=\sqrt{234}$, base $68.8$:
$\frac13\cdot\frac12\sqrt{18954}\cdot\sqrt{234}=\boxed{351}$.

---

## § 4

**4.1 (a)** $\boxed{A^2B^2\sin^2\theta}$. **(b)** $\boxed{A^2B^2\cos^2\theta}$, and
$A^2B^2\sin^2\theta=A^2B^2(1-\cos^2\theta)=A^2B^2-A^2B^2\cos^2\theta$.

**4.2** $\boxed{U^2V^2\cos^2\theta+U^2V^2\sin^2\theta}=U^2V^2$.

**4.3 (a)** $|\mathbf u\times\mathbf v|=2\cdot\sqrt6=\boxed{2\sqrt6}\approx4.90$.
**(b)** $|\mathbf v|^2=11$ and $3^2+24=11|\mathbf u|^2$: $\boxed{|\mathbf u|=\sqrt3}\approx1.73$.
**(c)** $3p+q=5$ and $p^2+(q-1)^2=2$ give $5p^2-12p+7=0$:
$\boxed{p=1,q=2}$ or $\boxed{p=\frac75,q=\frac45}$.

---

## § 5

**5.1** $(1,2,1)\cdot(1,-1,-2)=-3$, both lengths $\sqrt6$: $\cos\theta=\frac36=\frac12$,
$\boxed{\theta=60°}$.

**5.2** $(-1,1,-1)\cdot(5,1,-7)=3$, lengths $\sqrt3$ and $5\sqrt3$:
$\boxed{\cos\theta=\frac15}$.

**5.3** $(3,2,-1)$ and $(4,\cos\alpha,\sin\alpha)$, lengths $\sqrt{14}$ and $\sqrt{17}$:
$12+2\cos\alpha-\sin\alpha=\sqrt{238}\sin\alpha$, so $\boxed{\alpha=0.932}$.

**5.4** $\mathbf a\times\mathbf n=(0,0,36)$ and $(0,-36,0)\cdot(0,0,36)=0$: $\boxed{90°}$.

**5.5** $\cos\widehat{BOM}=\frac{-9.721}{36}$, $\widehat{BOM}=1.844$ rad, arc
$6\times1.844=\boxed{11.1}$ thousand km.

**5.6** $\mathbf b\times\mathbf m=(-15.15,-26.23,16.84)$,
$\mathbf b\times\mathbf p=(-18,-31.18,0)$: $\cos\beta=0.8740$, $\boxed{029.1°}$.

---

## § 6

**6.1 (a)** $\overrightarrow{PN}=(3+5\mu,-5-2\mu,15-\mu)$ and
$\overrightarrow{AB}=(5,-2,-1)$: $\boxed{10+30\mu}$.
**(b)** $\mu=-\frac13$: $\boxed{N\left(\frac13,-\frac{10}3,\frac73\right)}$.

**6.2** $\overrightarrow{OP}\cdot(1,-2,-2)=9\lambda-12=0$, $\lambda=\frac43$:
$\boxed{P\left(\frac43,-\frac23,\frac43\right)}$.

---

## § 7

**7.1** $|\overrightarrow{PA}|=6\sqrt2$ and $d=6\sqrt2\sin\frac\pi3=\boxed{3\sqrt6}=\sqrt{54}$.

**7.2** Parallel: $\overrightarrow{AB}=(-1,-2,5)$, $\overrightarrow{AB}\times(1,-1,1)=(3,6,3)$,
$d=\frac{\sqrt{54}}{\sqrt3}=\boxed{3\sqrt2}=\sqrt{18}$.
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
