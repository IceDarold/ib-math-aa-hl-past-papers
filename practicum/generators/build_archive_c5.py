"""Собирает архивный ноутбук C5: вся тема векторов без плоскостей подряд.

Девятнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3, D4, D5 и D6. Практикум учит: лестница из приёмов,
теория перед каждым, три уровня сложности, тренажёр распознавания,
задание на время. Архив не учит. Он даёт набивать руку: **вся тема
подряд, по тем же восьми приёмам, без единой строчки теории**. Тридцать
два вопроса, 137 баллов — всё, что архив спрашивает про векторы без
плоскости и без векторного произведения, с мая 2021 по ноябрь 2025.

Разметка взята из карточки geometry-vectors.yaml: поле blocks у каждого
приёма. Ноябрь 2023 года стоит в корпусе дважды, TZ1 и TZ2 одной бумаги;
здесь он один раз.

Части одного вопроса разнесены по своим приёмам: ноябрь 2025 TZ3 Q10 —
в §§ 4 и 7, май 2021 TZ1 Q11 — в §§ 4, 5 и 6, ноябрь 2022 Q12 — в §§ 1 и 7,
май 2022 TZ1 Q7 — в §§ 1 и 2. Условие каждого пункта повторено целиком,
насколько оно нужно пункту.

«Show that» здесь проверяется по промежуточной строке: скалярное
произведение до разложения на множители, косинус угла через t, значение
параметра в данной точке, два параметра из двух компонент.

Хешей нет ни одного: всякий ответ темы — точка, вектор, прямая, угол или
буква, и всякий проверяется самими точками и прямыми вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_c5.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/geometry/archive-c5-vectors.ipynb')

ANSWERS = {
    # § 1. Points and lengths
    'q1_1a': '(3, 0, 2)',
    'q1_1b': '(0, -3, 2)',
    'q1_2a': '(-1, 3, -2)',
    'q1_2b': '3',
    'q1_3': '10.3',
    'q1_4': 'sqrt(29)',
    'q1_5_AB': 'vec(k - 1, -4, -2)',
    'q1_5_AC': 'vec(4, -2, -1)',
    'q1_5b': '9',
    'q1_6a': 'Interval(2, 28)',
    'q1_6b': 'vec(Rational(-24, 13), Rational(10, 13))',
    'q1_7_OM': 'a + k*c',
    'q1_7_MC': '(1 - k)*c - a',
    # § 2. The scalar product
    'q2_1': 'vec(Rational(75, 13), Rational(180, 13))',
    'q2_2': '(1 - 2*k)*2*la**2*cos(theta) - la**2 + 4*k*(1 - k)*la**2',
    'q2_3_i': '-5*p - 42',
    'q2_3_ii': '-8*p - 54',
    'q2_4_C': '(-k*t, -k/t)',
    'q2_4_CA': 'vec(2*k*t, 2*k/t)',
    'q2_4_CB': 'vec(k*t - k/t**3, k/t - k*t**3)',
    # § 3. The angle between two vectors
    'q3_1': '0.798',
    'q3_2': '(cos(1/n) + sin(1/n))/sqrt(2)',
    'q3_3': 'pi/2',
    'q3_4': '4.79',
    # § 4. The equation of a line
    'q4_1': 'vec(-1, 0, 3) + lam*vec(2, 1, -1)',
    'q4_2': 'vec(1, -2, 0) + lam*vec(2, 3, 1)',
    'q4_3a': 'vec(-1, 1, -13) + lam*vec(7, 1, 2)',
    'q4_3b': 'vec(2, -4, 2) + mu*vec(5, -2, -1)',
    'q4_4': '3',
    # § 5. The angle between two lines
    'q5_1': '[-4 + 3*sqrt(2), -4 - 3*sqrt(2)]',
    'q5_2': '40.2',
    'q5_3': '2*t/(sqrt(2)*sqrt(4*t**2 + (3 + t)**2))',
    # § 6. Where two lines meet
    'q6_1': '(5, 4, 2)',
    'q6_2': '-4',
    'q6_3_pair': '[2, -1]',
    'q6_3': '(5, 8, 9)',
    'q6_4_k': '2',
    'q6_4_A': '(a/(a - 2), (a - 1)/(a - 2), (2*a - 5)/(a - 2))',
    # § 7. Parallel, meeting or skew
    'q7_1': "'parallel'",
    'q7_2': "'skew'",
    'q7_2_pair': '[-1, -2]',
    'q7_3_line': 'vec(1, 2, 3) + lam*vec(4, -2, -1)',
    'q7_3': "'skew'",
    'q7_3_pair': '[Rational(1, 4), Rational(1, 2)]',
    'q7_4': '[Rational(-3, 2), 14]',
    # § 8. Motion along a line
    'q8_1a': "'063'",
    'q8_1b_A': 'sqrt(56)',
    'q8_1b_B': 'sqrt(24)',
    'q8_1d_i': '(7, 3, 9)',
    'q8_1d_ii': '0.5',
    'q8_2a': '108',
    'q8_2b': '8.45',
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


AIRPLANES = r"""Two airplanes, $A$ and $B$, have position vectors with respect to an origin
$O$ given respectively by

$$\mathbf r_A=""" + col(19, -1, 1) + r"+t" + col(-6, 2, 4) + r"""$$

$$\mathbf r_B=""" + col(1, 0, 12) + r"+t" + col(4, 2, -2) + r"""$$

where $t$ represents the time in minutes and $0\le t\le2.5$. Entries in each
column vector give the displacement east of $O$, the displacement north of
$O$ and the distance above sea level, all measured in kilometres."""

md(r"""
# C5 archive — vectors, lines and angles, all of it

**Thirty-two questions, 137 marks.** Every question the archive asks about
vectors without a plane and without a vector product, from May 2021 to
November 2025, in the order of the eight techniques rather than the order
of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-c5-vectors.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Points and lengths | 7 | 21 |
| 2 | The scalar product | 4 | 17 |
| 3 | The angle between two vectors | 4 | 14 |
| 4 | The equation of a line | 4 | 11 |
| 5 | The angle between two lines | 3 | 16 |
| 6 | Where two lines meet | 4 | 18 |
| 7 | Parallel, meeting or skew | 4 | 24 |
| 8 | Motion along a line | 2 | 16 |

The checks are the same ones the practicum uses and they store nothing:
each is handed the points and lines exactly as the question prints them —
`vec(1, -4, 0)`, `cartesian((x + 1)/2, y, 3 - z)`, `through(A, B)` — and a
point or a letter the question asks for is handed **the conditions** that
fix it, `parallelogram(A, B, C, D)`, `perpendicular(q, a)`, `meet(L1, L2)`.
A line is accepted with any point on it and any parallel direction. Three
significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** November 2025 TZ3 Q10
appears in §§ 4 and 7; each part repeats what it needs.

**A *show that* is checked by the line before the given result:** the
scalar product before it is factorised, the cosine in terms of $t$, the
parameter at the given point, the two parameters from two components.

Enter a line as `vec(point) + lam*vec(direction)`; `lam` and `mu` are $\lambda$
and $\mu$.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, line, cartesian, through, unknown

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. Points and lengths

**Seven questions, 21 marks.** A vector between two points, a midpoint, a
vertex, a length.
""")

md(r"""
### 1.1 — *May 2025 TZ3 Paper 1 Q11(a), (b), 4 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D$ form a
parallelogram, $ABCD$, where $D$ is diagonally opposite $B$.

**(a)** Find the coordinates of $D$.

The diagonals of the parallelogram, $[AC]$ and $[BD]$, intersect at point $E$.

**(b)** Find the coordinates of $E$.
""")

code(r"""
A, B, C = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4)
D, E = unknown('D', 3), unknown('E', 3)

q1_1a = ...      # D
q1_1b = ...      # E

verify_find('1.1(a)', q1_1a, D, [parallelogram(A, B, C, D)])
verify_find('1.1(b)', q1_1b, E, [parallelogram(A, B, C, D), on(E, A, C), on(E, B, D)])
""")

md(r"""
### 1.2 — *November 2022 Paper 1 Q2(a), 4 marks*

Consider a circle with a diameter $AB$, where $A$ has coordinates $(1,4,0)$ and
$B$ has coordinates $(-3,2,-4)$.

**(a)** Find **(i)** the coordinates of the centre of the circle; **(ii)** the radius
of the circle.
""")

code(r"""
A, B = vec(1, 4, 0), vec(-3, 2, -4)
centre, r = unknown('M', 3), unknown('r')

q1_2a = ...      # the centre
q1_2b = ...      # the radius

verify_find('1.2(a)(i)', q1_2a, centre, [midpoint(centre, A, B)])
verify_find('1.2(a)(ii)', q1_2b, r, [Eq(2*r, distance(A, B))])
""")

md(r"""
### 1.3 — *November 2023 TZ1 Paper 2 Q1(a), 2 marks*

A pyramid has vertex $V$ and rectangular base $OABC$. Point $B$ has
coordinates $(6,8,0)$ and point $V$ has coordinates $(3,4,9)$.

**(a)** Find $BV$.

### 1.4 — *May 2025 TZ2 Paper 2 Q2(a), 2 marks*

A square-based right-pyramid has vertex $V(1,7,0)$. Point $X(-3,4,2)$ is the
centre of the base $ABCD$.

**(a)** Find $VX$.
""")

code(r"""
q1_3 = ...       # BV
q1_4 = ...       # VX

verify_find('1.3', q1_3, distance(vec(6, 8, 0), vec(3, 4, 9)))
verify_find('1.4', q1_4, distance(vec(1, 7, 0), vec(-3, 4, 2)))
""")

md(r"""
### 1.5 — *November 2022 Paper 2 Q12(a), (b), 3 marks*

Consider the points $A(1,2,3)$, $B(k,-2,1)$ and $C(5,0,2)$, where $k\in\mathbb R$.

**(a)** Write down $\overrightarrow{AB}$ and $\overrightarrow{AC}$.

**(b)** Given that the points $A$, $B$ and $C$ lie on a straight line, show that $k=9$.

*For (b) enter the value of $k$ that the line gives.*
""")

code(r"""
A, B, C = vec(1, 2, 3), vec(k, -2, 1), vec(5, 0, 2)

q1_5_AB = ...    # AB
q1_5_AC = ...    # AC
q1_5b = ...      # k

verify_find('1.5(a) AB', q1_5_AB, B - A)
verify_find('1.5(a) AC', q1_5_AC, C - A)
verify_find('1.5(b)', q1_5b, k, [parallel(B - A, C - A)])
""")

md(r"""
### 1.6 — *May 2022 TZ1 Paper 2 Q7(a), (b), 4 marks*

Consider the vectors $\mathbf a$ and $\mathbf b$ such that $\mathbf a=""" + col(12, -5) + r"""$ and
$\lvert\mathbf b\rvert=15$.

**(a)** Find the possible range of values for $\lvert\mathbf a+\mathbf b\rvert$.

Consider the vector $\mathbf p$ such that $\mathbf p=\mathbf a+\mathbf b$.

**(b)** Given that $\lvert\mathbf a+\mathbf b\rvert$ is a minimum, find $\mathbf p$.

*In (a) answer `Interval(lowest, highest)`.*
""")

code(r"""
theta = symbols('theta')
a = vec(12, -5)
b = 15*vec(cos(theta), sin(theta))      # every b with |b| = 15

q1_6a = ...      # Interval(lowest, highest)
q1_6b = ...      # p

verify_extent('1.6(a)', q1_6a, mag(a + b), theta, Interval(0, 2*pi))
verify_optimum('1.6(b)', q1_6b, a + b, theta, Interval(0, 2*pi), 'min')
""")

md(r"""
### 1.7 — *May 2023 TZ2 Paper 1 Q9(a), 2 marks*

The diagram shows parallelogram $OABC$ with $\overrightarrow{OA}=\mathbf a$, $\overrightarrow{OC}=\mathbf c$
and $\lvert\mathbf c\rvert=2\lvert\mathbf a\rvert$, where $\lvert\mathbf a\rvert\ne0$. The angle between
$\overrightarrow{OA}$ and $\overrightarrow{OC}$ is $\theta$, where $0<\theta<\pi$.

Point $M$ is on $[AB]$ such that $\overrightarrow{AM}=k\overrightarrow{AB}$, where $0\le k\le1$ and
$\overrightarrow{OM}\cdot\overrightarrow{MC}=0$.

**(a)** Express $\overrightarrow{OM}$ and $\overrightarrow{MC}$ in terms of $\mathbf a$ and $\mathbf c$.
""")

code(r"""
la, theta = symbols('|a| theta', positive=True)
a = la*vec(1, 0)
c = 2*la*vec(cos(theta), sin(theta))    # |c| = 2|a|, the angle between them is theta
O = vec(0, 0)
B, M = unknown('B', 2), unknown('M', 2)
figure = [parallelogram(O, a, B, c, names='OABC'), Eq(M - a, k*(B - a))]

q1_7_OM = ...    # OM in terms of a and c
q1_7_MC = ...    # MC in terms of a and c

verify_find('1.7 OM', q1_7_OM, M - O, figure)
verify_find('1.7 MC', q1_7_MC, c - M, figure)
""")

# ============================================================ § 2
md(r"""
---
# § 2. The scalar product

**Four questions, 17 marks.** Perpendicular means zero; with letters,
expand like brackets.
""")

md(r"""
### 2.1 — *May 2022 TZ1 Paper 2 Q7(c), 5 marks*

Consider the vectors $\mathbf a=""" + col(12, -5) + r"""$ and $\mathbf b$ with $\lvert\mathbf b\rvert=15$, and the
vector $\mathbf q=""" + col('x', 'y') + r"""$, where $x,y\in\mathbb R^+$.

**(c)** Find $\mathbf q$ such that $\lvert\mathbf q\rvert=\lvert\mathbf b\rvert$ and $\mathbf q$ is perpendicular to $\mathbf a$.
""")

code(r"""
a = vec(12, -5)
q = unknown('q', 2)

q2_1 = ...       # q

verify_find('2.1', q2_1, q, [perpendicular(q, a), length(q, 15), q[0] > 0, q[1] > 0])
""")

md(r"""
### 2.2 — *May 2023 TZ2 Paper 1 Q9(b), 3 marks*

Parallelogram $OABC$ has $\overrightarrow{OA}=\mathbf a$, $\overrightarrow{OC}=\mathbf c$, $\lvert\mathbf c\rvert=2\lvert\mathbf a\rvert$ and the
angle $\theta$ between them. $M$ is on $[AB]$ with $\overrightarrow{AM}=k\overrightarrow{AB}$ and
$\overrightarrow{OM}\cdot\overrightarrow{MC}=0$.

**(b)** Hence, use a vector method to show that $\lvert\mathbf a\rvert^2(1-2k)\big(2\cos\theta-(1-2k)\big)=0$.

*Enter $\overrightarrow{OM}\cdot\overrightarrow{MC}$ in terms of $\lvert\mathbf a\rvert$ (`la`), $\theta$ and $k$ — the line
before you factorise.*
""")

code(r"""
la, theta = symbols('|a| theta', positive=True)
a = la*vec(1, 0)
c = 2*la*vec(cos(theta), sin(theta))
O = vec(0, 0)
B, M = unknown('B', 2), unknown('M', 2)
figure = [parallelogram(O, a, B, c, names='OABC'), Eq(M - a, k*(B - a))]

q2_2 = ...       # OM · MC in terms of la, theta and k

verify_find('2.2', q2_2, dot(M - O, c - M), figure)
""")

md(r"""
### 2.3 — *May 2025 TZ3 Paper 2 Q6(a), 3 marks*

Consider the vectors $\mathbf a=""" + col(-5, 7) + r"""$, $\mathbf b=""" + col(-8, 9) + r"""$ and
$\mathbf c=""" + col('p', -6) + r"""$, where $p\in\mathbb R$.

**(a)** Find an expression, in terms of $p$, for **(i)** $\mathbf a\cdot\mathbf c$; **(ii)** $\mathbf b\cdot\mathbf c$.
""")

code(r"""
p = symbols('p')
a, b, c = vec(-5, 7), vec(-8, 9), vec(p, -6)

q2_3_i = ...     # a · c
q2_3_ii = ...    # b · c

verify_find('2.3(i)', q2_3_i, dot(a, c))
verify_find('2.3(ii)', q2_3_ii, dot(b, c))
""")

md(r"""
### 2.4 — *November 2025 TZ1 Paper 3 Q1(f), 6 marks*

The curve $F$ has equation $y=\dfrac{k^2}x$ where $x\in\mathbb R$, $x\ne0$ and $k\in\mathbb R$, $k\ne0$.

The point $A\left(kt,\dfrac kt\right)$, where $t\in\mathbb R$, $t\ne\pm1$, lies on $F$. The line normal
to $F$ at $A$ intersects $F$ again at point $B$; in part (e)(ii) this gives
$B\left(-\dfrac k{t^3},-kt^3\right)$.

From $A$, the line passing through the origin $O$ intersects $F$ again at
point $C$. Points $A$, $B$ and $C$ form triangle $ABC$.

**(f)** Prove that $B\hat CA$ is a right angle.

*Enter $C$ and the vectors $\overrightarrow{CA}$ and $\overrightarrow{CB}$ in terms of $k$ and $t$. The proof is
that their scalar product simplifies to zero.*
""")

code(r"""
k, t = symbols('k t', positive=True)
A, B = vec(k*t, k/t), vec(-k/t**3, -k*t**3)
C = unknown('C', 2)
curve_and_line = [on(C, vec(0, 0), A), Eq(C[0]*C[1], k**2), Ne(C, A)]

q2_4_C = ...     # C
q2_4_CA = ...    # CA
q2_4_CB = ...    # CB

verify_find('2.4 C', q2_4_C, C, curve_and_line)
verify_find('2.4 CA', q2_4_CA, A - C, curve_and_line)
verify_find('2.4 CB', q2_4_CB, B - C, curve_and_line)
""")

# ============================================================ § 3
md(r"""
---
# § 3. The angle between two vectors

**Four questions, 14 marks.** $\cos\theta=\dfrac{\mathbf a\cdot\mathbf b}{\lvert\mathbf a\rvert\lvert\mathbf b\rvert}$, from the vertex.
""")

md(r"""
### 3.1 — *November 2023 TZ1 Paper 2 Q1(b), 4 marks*

A pyramid has vertex $V$ and rectangular base $OABC$. Point $B$ has
coordinates $(6,8,0)$, point $C$ has coordinates $(6,0,0)$ and point $V$ has
coordinates $(3,4,9)$.

**(b)** Find the size of $B\hat VC$.
""")

code(r"""
q3_1 = ...       # the angle BVC

verify_angle('3.1', q3_1, vec(6, 8, 0), vec(3, 4, 9), vec(6, 0, 0))
""")

md(r"""
### 3.2 — *November 2022 Paper 2 Q7(a), 3 marks*

Consider the vectors $\mathbf u=\mathbf i+\mathbf j$ and $\mathbf v=\left(\cos\frac1n\right)\mathbf i+\left(\sin\frac1n\right)\mathbf j$, where
$n\in\mathbb Z^+$. Let $\theta$ be the angle between $\mathbf u$ and $\mathbf v$.

**(a)** Find an expression for $\cos\theta$ in terms of $n$.
""")

code(r"""
n = symbols('n', positive=True, integer=True)

q3_2 = ...       # cos(theta) in terms of n

verify_angle('3.2', q3_2, vec(1, 1), vec(cos(1/n), sin(1/n)), cosine=True)
""")

md(r"""
### 3.3 — *May 2025 TZ2 Paper 3 Q2(b)(i), 2 marks*

The Earth is modelled as a sphere with its centre at the origin $O$. The North
Pole $P$ has position vector $\mathbf p=""" + col(0, 0, 6) + r"""$ and Nairobi $N$ has position vector
$\mathbf n=""" + col(0, 6, 0) + r"""$.

**(b)** **(i)** Use the scalar product to find the angle between $\mathbf p$ and $\mathbf n$.

### 3.4 — *May 2025 TZ3 Paper 2 Q6(b), 5 marks*

Consider the vectors $\mathbf a=""" + col(-5, 7) + r"""$, $\mathbf b=""" + col(-8, 9) + r"""$ and
$\mathbf c=""" + col('p', -6) + r"""$, where $p\in\mathbb R$. The angle between $\mathbf a$ and $\mathbf c$ is equal to
the angle between $\mathbf b$ and $\mathbf c$.

**(b)** Find the value of $p$.
""")

code(r"""
p = symbols('p')
a, b, c = vec(-5, 7), vec(-8, 9), vec(p, -6)

q3_3 = ...       # the angle between p and n
q3_4 = ...       # p

verify_angle('3.3', q3_3, vec(0, 0, 6), vec(0, 6, 0))
verify_find('3.4', q3_4, p, [Eq(angle(a, c), angle(b, c))])
""")

# ============================================================ § 4
md(r"""
---
# § 4. The equation of a line

**Four questions, 11 marks.** A point on it, a direction along it — and
"$\mathbf r=$".
""")

md(r"""
### 4.1 — *May 2021 TZ1 Paper 1 Q11(a), 4 marks*

Consider the line $L_1$ defined by the Cartesian equation $\dfrac{x+1}2=y=3-z$.

**(a)** **(i)** Show that the point $(-1,0,3)$ lies on $L_1$. **(ii)** Find a vector
equation of $L_1$.

### 4.2 — *May 2025 TZ2 Paper 1 Q2(a), 2 marks*

The line $L_1$ is defined by the Cartesian equation $\dfrac{x-1}2=\dfrac{y+2}3=z$.

**(a)** Find a vector equation of $L_1$.
""")

code(r"""
q4_1 = ...       # a vector equation of (x + 1)/2 = y = 3 - z
q4_2 = ...       # a vector equation of (x - 1)/2 = (y + 2)/3 = z

verify_line('4.1', q4_1, cartesian((x + 1)/2, y, 3 - z))
verify_line('4.2', q4_2, cartesian((x - 1)/2, (y + 2)/3, z))
""")

md(r"""
### 4.3 — *November 2025 TZ3 Paper 1 Q10(a), (b), 3 marks*

The point $P(-1,1,-13)$ lies on the line $L_1$. The line $L_1$ has a direction vector
$""" + col(7, 1, 2) + r"""$.

**(a)** Write down a vector equation for $L_1$ in the form $\mathbf r=\mathbf a+\lambda\mathbf b$.

**(b)** Find a vector equation for line $L_2$ in the form $\mathbf s=\mathbf c+\mu\mathbf d$, given that
$L_2$ passes through the points $A(2,-4,2)$ and $B(7,-6,1)$.
""")

code(r"""
q4_3a = ...      # L1: vec(...) + lam*vec(...)
q4_3b = ...      # L2: vec(...) + mu*vec(...)

verify_line('4.3(a)', q4_3a, line(vec(-1, 1, -13), vec(7, 1, 2)))
verify_line('4.3(b)', q4_3b, through(vec(2, -4, 2), vec(7, -6, 1)))
""")

md(r"""
### 4.4 — *November 2025 TZ1 Paper 2 Q12(f), 2 marks*

The line $L_3$ is normal to the plane $\Pi$ and passes through the point of
intersection of $L_1$ and $L_2$. In part (e) its equation is
$\mathbf r_3=""" + col(1, 8, -2) + r"+\gamma" + col(-4, -1, 3) + r"""$.

**(f)** Given that the point $S(-11,5,7)$ lies on the line $L_3$, find $\gamma$.
""")

code(r"""
gamma = symbols('gamma')
L3 = line(vec(1, 8, -2) + gamma*vec(-4, -1, 3))

q4_4 = ...       # gamma

verify_line_parameter('4.4', q4_4, L3, vec(-11, 5, 7))
""")

# ============================================================ § 5
md(r"""
---
# § 5. The angle between two lines

**Three questions, 16 marks.** The directions only, and the acute angle.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 1 Q11(b), 8 marks*

Consider the line $L_1$ defined by $\dfrac{x+1}2=y=3-z$ and a second line $L_2$
defined by $\mathbf r=""" + col(0, 1, 2) + r"+t" + col('a', 1, -1) + r"""$, where $t\in\mathbb R$ and $a\in\mathbb R$.

**(b)** Find the possible values of $a$ when the acute angle between $L_1$ and
$L_2$ is $45^\circ$.

*Paper 1: exact values, all of them.*
""")

code(r"""
a = symbols('a')
L1 = cartesian((x + 1)/2, y, 3 - z)
L2 = line(vec(0, 1, 2) + t*vec(a, 1, -1), t)

q5_1 = [...]     # all possible values of a

verify_find('5.1', q5_1, a, [Eq(angle(L1, L2), pi/4)], exact=True)
""")

md(r"""
### 5.2 — *May 2022 TZ2 Paper 2 Q11(c), 4 marks*

""" + AIRPLANES + r"""

**(c)** Find the acute angle between the two airplanes' lines of flight. Give
your answer in degrees.
""")

code(r"""
rA = vec(19, -1, 1) + t*vec(-6, 2, 4)
rB = vec(1, 0, 12) + t*vec(4, 2, -2)

q5_2 = ...       # the acute angle, degrees

verify_angle('5.2', q5_2, line(rA, t), line(rB, t), deg=True)
""")

md(r"""
### 5.3 — *May 2023 TZ1 Paper 1 Q12(a), 4 marks*

Two lines, $L_1$ and $L_2$, intersect at point $P$. Point $A(2t,8,3)$, where $t>0$,
lies on $L_2$.

The acute angle between the two lines is $\dfrac\pi3$.

The direction vector of $L_1$ is $""" + col(1, 1, 0) + r"""$, and $\overrightarrow{PA}=""" + col('2t', 0, '3+t') + r"""$.

**(a)** Show that $4t=\sqrt{10t^2+12t+18}$.

*Enter $\cos\theta$ in terms of $t$, before you set it equal to $\frac12$.*
""")

code(r"""
t = symbols('t', positive=True)

q5_3 = ...       # cos of the angle between the lines, in terms of t

verify_angle('5.3', q5_3, line(vec(0, 0, 0), vec(1, 1, 0)), line(vec(0, 0, 0), vec(2*t, 0, 3 + t)), cosine=True)
""")

# ============================================================ § 6
md(r"""
---
# § 6. Where two lines meet

**Four questions, 18 marks.** Two parameters, two equations, the third
checked.
""")

md(r"""
### 6.1 — *May 2025 TZ2 Paper 1 Q2(b), 3 marks*

The line $L_1$ is defined by the Cartesian equation $\dfrac{x-1}2=\dfrac{y+2}3=z$. A second
line $L_2$ is defined by the vector equation $\mathbf r=""" + col(0, 4, -8) + r"+t" + col(1, 0, 2) + r"""$, where $t\in\mathbb R$.

**(b)** Find the coordinates of the point where $L_1$ and $L_2$ intersect.
""")

code(r"""
q6_1 = ...       # the point of intersection

verify_meet('6.1', q6_1, cartesian((x - 1)/2, (y + 2)/3, z), line(vec(0, 4, -8) + t*vec(1, 0, 2)))
""")

md(r"""
### 6.2 — *November 2025 TZ1 Paper 2 Q12(a), 3 marks*

The equations of two lines, $L_1$ and $L_2$, are given by

$$L_1:\ \mathbf r_1=""" + col(5, 4, 2) + r"+s" + col(1, -1, 1) + r"""\ \text{where } s\in\mathbb R,\qquad L_2:\ \frac{x+1}2=y-7=\frac{z+5}3$$

**(a)** Show that the position vector of the point of intersection of $L_1$ and $L_2$
is $""" + col(1, 8, -2) + r"""$.

*Enter the value of $s$ at the point of intersection.*
""")

code(r"""
s = symbols('s')

q6_2 = ...       # s at the point of intersection

verify_line_parameter('6.2', q6_2, line(vec(5, 4, 2) + s*vec(1, -1, 1), s), vec(1, 8, -2))
""")

md(r"""
### 6.3 — *November 2023 TZ1 Paper 2 Q12(a), 5 marks*

Line $L$ is given by the vector equation $\mathbf r_1=""" + col(1, 2, -3) + r"+s" + col(2, 3, 6) + r"""$ where $s\in\mathbb R$.

Line $M$ is given by the vector equation $\mathbf r_2=""" + col(9, 9, 11) + r"+t" + col(4, 1, 2) + r"""$ where $t\in\mathbb R$.

**(a)** Show that lines $L$ and $M$ intersect at a point $A$ and find the position
vector of $A$.
""")

code(r"""
s = symbols('s')
L = line(vec(1, 2, -3) + s*vec(2, 3, 6), s)
M = line(vec(9, 9, 11) + t*vec(4, 1, 2), t)

q6_3_pair = [...]    # [s, t] from two of the component equations
q6_3 = ...           # the position vector of A

verify_pair('6.3 [s, t]', q6_3_pair, L, M)
verify_meet('6.3 A', q6_3, L, M)
""")

md(r"""
### 6.4 — *May 2021 TZ1 Paper 1 Q11(c), 7 marks*

Consider the line $L_1$ defined by $\dfrac{x+1}2=y=3-z$ and the line $L_2$ defined by
$\mathbf r=""" + col(0, 1, 2) + r"+t" + col('a', 1, -1) + r"""$, where $t\in\mathbb R$ and $a\in\mathbb R$.

It is given that the lines $L_1$ and $L_2$ have a unique point of intersection, $A$, when $a\ne k$.

**(c)** Find the value of $k$, and find the coordinates of the point $A$ in terms of $a$.
""")

code(r"""
a = symbols('a')
L1 = cartesian((x + 1)/2, y, 3 - z)
L2 = line(vec(0, 1, 2) + t*vec(a, 1, -1), t)

q6_4_k = ...     # k
q6_4_A = ...     # A in terms of a

verify_find('6.4 k', q6_4_k, a, [no_unique_meet(L1, L2)])
verify_meet('6.4 A', q6_4_A, L1, L2)
""")

# ============================================================ § 7
md(r"""
---
# § 7. Parallel, meeting or skew

**Four questions, 24 marks.** Directions first; then two components and the
third.

Answer the relation with one word: `'parallel'`, `'intersecting'` or `'skew'`.
""")

md(r"""
### 7.1 — *May 2021 TZ2 Paper 1 Q8(a), 3 marks*

The lines $l_1$ and $l_2$ have the following vector equations where $\lambda,\mu\in\mathbb R$.

$$l_1:\ \mathbf r_1=""" + col(3, 2, -1) + r"+\lambda" + col(2, -2, 2) + r""",\qquad l_2:\ \mathbf r_2=""" + col(2, 0, 4) + r"+\mu" + col(1, -1, 1) + r"""$$

**(a)** Show that $l_1$ and $l_2$ do not intersect.

*Enter the reason they do not: the relation between the lines.*
""")

code(r"""
q7_1 = ...       # the relation between l1 and l2

verify_relation('7.1', q7_1, line(vec(3, 2, -1) + lam*vec(2, -2, 2)), line(vec(2, 0, 4) + mu*vec(1, -1, 1)))
""")

md(r"""
### 7.2 — *November 2025 TZ3 Paper 1 Q10(c), 5 marks*

The point $P(-1,1,-13)$ lies on the line $L_1$, which has direction vector $""" + col(7, 1, 2) + r"""$:
$\mathbf r=""" + col(-1, 1, -13) + r"+\lambda" + col(7, 1, 2) + r"""$. The line $L_2$ passes through $A(2,-4,2)$ and
$B(7,-6,1)$: $\mathbf s=""" + col(2, -4, 2) + r"+\mu" + col(5, -2, -1) + r"""$.

**(c)** Show that $L_1$ and $L_2$ are skew.

*Enter the relation, and $[\lambda,\mu]$ found from two of the component equations.*
""")

code(r"""
L1 = line(vec(-1, 1, -13) + lam*vec(7, 1, 2))
L2 = line(vec(2, -4, 2) + mu*vec(5, -2, -1))

q7_2 = ...           # the relation
q7_2_pair = [...]    # [lam, mu]

verify_relation('7.2', q7_2, L1, L2)
verify_pair('7.2 [λ, μ]', q7_2_pair, L1, L2)
""")

md(r"""
### 7.3 — *November 2022 Paper 2 Q12(c), 10 marks*

Consider the points $A(1,2,3)$, $B(k,-2,1)$ and $C(5,0,2)$, where $k\in\mathbb R$.

**(c)** For $k=9$, let $L_1$ be the line passing through $A$, $B$ and $C$.

**(i)** Find a vector equation of the line $L_1$.

**(ii)** Line $L_2$ has the equation $\dfrac{x-1}2=\dfrac y3=1-z$. Show that the lines $L_1$
and $L_2$ are skew.

*For (ii) the parameter of $L_2$ is the common value $\mu$ of its three parts, and
$[\lambda,\mu]$ comes from your line in (i).*
""")

code(r"""
A, C = vec(1, 2, 3), vec(5, 0, 2)
L2 = cartesian((x - 1)/2, y/3, 1 - z)

q7_3_line = ...      # L1: vec(...) + lam*vec(...)
q7_3 = ...           # the relation
q7_3_pair = [...]    # [lam, mu]

verify_line('7.3(c)(i)', q7_3_line, through(A, C))
verify_relation('7.3(c)(ii)', q7_3, through(A, C), L2)
verify_pair('7.3(c)(ii) [λ, μ]', q7_3_pair, q7_3_line, L2)
""")

md(r"""
### 7.4 — *May 2025 TZ1 Paper 1 Q6, 6 marks*

The line $L_1$ has vector equation $\mathbf r=4\mathbf i-\mathbf k+\lambda(a\mathbf j+\mathbf k)$, where $a,\lambda\in\mathbb R$.

The line $L_2$ has vector equation $\mathbf r=\mathbf i-b\mathbf k+\mu(\mathbf i+2\mathbf j+3\mathbf k)$, where $b,\mu\in\mathbb R$.

The lines $L_1$ and $L_2$ are perpendicular and intersect at a unique point.

Find the value of $a$ and the value of $b$.
""")

code(r"""
a, b = symbols('a b')
L1 = line(vec(4, 0, -1) + lam*vec(0, a, 1), lam)
L2 = line(vec(1, 0, -b) + mu*vec(1, 2, 3), mu)

q7_4 = [...]     # [a, b]

verify_find('7.4', q7_4, [a, b], [perpendicular(L1, L2), meet(L1, L2)])
""")

# ============================================================ § 8
md(r"""
---
# § 8. Motion along a line

**Two questions, 16 marks.** $\mathbf r=\mathbf r_0+t\mathbf v$: speed, bearing, two times.
""")

md(r"""
### 8.1 — *May 2022 TZ2 Paper 2 Q11(a), (b), (d), 11 marks*

""" + AIRPLANES + r"""

**(a)** Find the three-figure bearing on which airplane $B$ is travelling.

**(b)** Show that airplane $A$ travels at a greater speed than airplane $B$.

The two airplanes' lines of flight cross at point $P$.

**(d)** **(i)** Find the coordinates of $P$. **(ii)** Determine the length of time
between the first airplane arriving at $P$ and the second airplane arriving at $P$.

*In (a) enter the bearing as a string of three figures; for (b) both speeds.*
""")

code(r"""
rA = vec(19, -1, 1) + t*vec(-6, 2, 4)
rB = vec(1, 0, 12) + t*vec(4, 2, -2)
t1, t2, crossing = unknown('t1'), unknown('t2'), unknown('crossing', 3)

q8_1a = ...      # the bearing of B
q8_1b_A = ...    # the speed of A
q8_1b_B = ...    # the speed of B
q8_1d_i = ...    # the point where the paths cross
q8_1d_ii = ...   # the time between the arrivals, minutes

verify_bearing('8.1(a)', q8_1a, velocity(rB))
verify_speed('8.1(b) A', q8_1b_A, rA)
verify_speed('8.1(b) B', q8_1b_B, rB)
verify_meet('8.1(d)(i)', q8_1d_i, line(rA, t), line(rB, t))
verify_find('8.1(d)(ii)', q8_1d_ii, Abs(t1 - t2), [Eq(rA.subs(t, t1), crossing), Eq(rB.subs(t, t2), crossing)])
""")

md(r"""
### 8.2 — *May 2025 TZ1 Paper 2 Q7, 5 marks*

At 09:00 a helicopter is located at a point $(10,3,0.5)$ relative to a point $O$ on
horizontal ground. The $x$-direction is due east, the $y$-direction is due north
and the $z$-direction is vertically upwards. All distances are measured in
kilometres.

The helicopter is flying at a constant height. Its position relative to $O$ is
given by $\mathbf r=""" + col(10, 3, 0.5) + r"+4t" + col(10, -25, 0) + r"""$, where $t$ represents the time in hours
since 09:00.

**(a)** Find the speed of the helicopter.

At 10:00 the helicopter begins to descend. During descent the helicopter's
vertical height decreases at a constant rate of $16\text{ km h}^{-1}$ and its
horizontal velocity remains unchanged. The angle of descent, $\beta$, is defined
as the angle between the helicopter's direction of travel and the horizontal.

**(b)** Find $\beta$, giving your answer in degrees.
""")

code(r"""
r = vec(10, 3, 0.5) + 4*t*vec(10, -25, 0)
descending = velocity(r) + vec(0, 0, -16)

q8_2a = ...      # the speed, km/h
q8_2b = ...      # beta, degrees

verify_speed('8.2(a)', q8_2a, r)
verify_angle('8.2(b)', q8_2b, descending, 'horizontal', deg=True)
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

Each answer is the one in the markscheme; the working is the shortest that
earns the marks.

---

## § 1

**1.1 (a)** $\overrightarrow{BC}=(2,4,2)=\overrightarrow{AD}$: $D=\boxed{(3,0,2)}$.
**(b)** The midpoint of $[AC]$: $\boxed{(0,-3,2)}$.

**1.2 (a)(i)** The midpoint of $[AB]$: $\boxed{(-1,3,-2)}$. **(ii)** $AB=\sqrt{16+4+16}=6$,
and the radius is half of it: $\boxed{3}$.

**1.3** $BV=\sqrt{9+16+81}=\sqrt{106}=\boxed{10.3}$.

**1.4** $VX=\sqrt{16+9+4}=\boxed{\sqrt{29}}=5.39$.

**1.5 (a)** $\overrightarrow{AB}=\boxed{(k-1,-4,-2)}$, $\overrightarrow{AC}=\boxed{(4,-2,-1)}$.
**(b)** On one line, $\overrightarrow{AB}=2\overrightarrow{AC}$: $k-1=8$, $\boxed{k=9}$.

**1.6 (a)** $\lvert\mathbf a\rvert=13$: $\boxed{2\le\lvert\mathbf a+\mathbf b\rvert\le28}$.
**(b)** $\mathbf b=-\frac{15}{13}\mathbf a$, so $\mathbf p=-\frac2{13}\mathbf a=\boxed{\left(-\frac{24}{13},\frac{10}{13}\right)}=(-1.85,\,0.769)$.

**1.7** $\overrightarrow{AB}=\mathbf c$: $\overrightarrow{OM}=\boxed{\mathbf a+k\mathbf c}$, $\overrightarrow{MC}=\boxed{(1-k)\mathbf c-\mathbf a}$.

---

## § 2

**2.1** Perpendicular to $(12,-5)$ is $(5,12)$, length $13$; scaled to $15$ with $x,y>0$:
$\boxed{\left(\frac{75}{13},\frac{180}{13}\right)}=(5.77,\,13.8)$.

**2.2** $(\mathbf a+k\mathbf c)\cdot((1-k)\mathbf c-\mathbf a)=(1-2k)\,\mathbf a\cdot\mathbf c-\lvert\mathbf a\rvert^2+k(1-k)\lvert\mathbf c\rvert^2$, and with
$\lvert\mathbf c\rvert^2=4\lvert\mathbf a\rvert^2$, $\mathbf a\cdot\mathbf c=2\lvert\mathbf a\rvert^2\cos\theta$:

$$\boxed{2(1-2k)\lvert\mathbf a\rvert^2\cos\theta-\lvert\mathbf a\rvert^2+4k(1-k)\lvert\mathbf a\rvert^2}=\lvert\mathbf a\rvert^2(1-2k)\big(2\cos\theta-(1-2k)\big)$$

**2.3** **(i)** $\boxed{-5p-42}$ **(ii)** $\boxed{-8p-54}$

**2.4** $C$ is on the line $OA$ and on $F$, and it is not $A$: $\boxed{C\left(-kt,-\frac kt\right)}$. Then
$\overrightarrow{CA}=\boxed{\left(2kt,\frac{2k}t\right)}$, $\overrightarrow{CB}=\boxed{\left(kt-\frac k{t^3},\ \frac kt-kt^3\right)}$, and

$$\overrightarrow{CA}\cdot\overrightarrow{CB}=2k^2t^2-\frac{2k^2}{t^2}+\frac{2k^2}{t^2}-2k^2t^2=0$$

with $\overrightarrow{CB}\ne\mathbf 0$ since $t\ne\pm1$: $B\hat CA$ is a right angle.

---

## § 3

**3.1** $\overrightarrow{VB}=(3,4,-9)$, $\overrightarrow{VC}=(3,-4,-9)$: $\cos B\hat VC=\frac{74}{106}$, $B\hat VC=\boxed{0.798}$ $(45.7^\circ)$.

**3.2** $\mathbf u\cdot\mathbf v=\cos\frac1n+\sin\frac1n$, $\lvert\mathbf u\rvert=\sqrt2$, $\lvert\mathbf v\rvert=1$: $\boxed{\cos\theta=\dfrac{\cos\frac1n+\sin\frac1n}{\sqrt2}}$.

**3.3** $\mathbf p\cdot\mathbf n=0$: $\boxed{\frac\pi2}$ $(90^\circ)$.

**3.4** $\dfrac{-5p-42}{\sqrt{74}}=\dfrac{-8p-54}{\sqrt{145}}$: $p=4.78727\ldots=\boxed{4.79}$.

---

## § 4

**4.1 (i)** $\frac{-1+1}2=0=3-3$. **(ii)** $\boxed{\mathbf r=(-1,0,3)+\lambda(2,1,-1)}$

**4.2** $\boxed{\mathbf r=(1,-2,0)+\lambda(2,3,1)}$

**4.3 (a)** $\boxed{\mathbf r=(-1,1,-13)+\lambda(7,1,2)}$ **(b)** $\boxed{\mathbf s=(2,-4,2)+\mu(5,-2,-1)}$

**4.4** $-11=1-4\gamma$, $5=8-\gamma$, $7=-2+3\gamma$: $\boxed{\gamma=3}$. With the direction $(4,1,-3)$ it
would be $-3$.

---

## § 5

**5.1** $\dfrac{\lvert2a+2\rvert}{\sqrt6\sqrt{a^2+2}}=\dfrac1{\sqrt2}$ gives $a^2+8a-2=0$: $\boxed{a=-4\pm3\sqrt2}$.

**5.2** $\cos\theta=\frac{-28}{\sqrt{56}\sqrt{24}}=-0.7637\ldots$, $\theta=139.8^\circ$; acute: $\boxed{40.2^\circ}$.

**5.3** $\boxed{\cos\theta=\dfrac{2t}{\sqrt2\sqrt{(2t)^2+(3+t)^2}}}=\frac12$, so $4t=\sqrt2\sqrt{5t^2+6t+9}=\sqrt{10t^2+12t+18}$.

---

## § 6

**6.1** $-2+3\lambda=4$: $\lambda=2$, $t=5$: $\boxed{(5,4,2)}$.

**6.2** $L_2$: $x=-1+2t$, $y=7+t$, $z=-5+3t$; $5+s=-1+2t$, $4-s=7+t$ give $t=1$, $\boxed{s=-4}$, and
$(5,4,2)-4(1,-1,1)=(1,8,-2)$.

**6.3** $1+2s=9+4t$ and $2+3s=9+t$: $\boxed{s=2,\ t=-1}$; the third agrees, $9=9$. $\boxed{A(5,8,9)}$.

**6.4** $1+2t=at$ gives $t=\frac1{a-2}$: $\boxed{k=2}$, and $\boxed{A\left(\frac a{a-2},\frac{a-1}{a-2},\frac{2a-5}{a-2}\right)}$.

---

## § 7

**7.1** $(2,-2,2)=2(1,-1,1)$: $\boxed{\text{parallel}}$, and $(3,2,-1)$ is not on $l_2$ — the first two
components give $5=2$.

**7.2** Not parallel; $\boxed{\lambda=-1,\ \mu=-2}$ from the first two, and $-15\ne4$: $\boxed{\text{skew}}$.

**7.3 (i)** $\boxed{\mathbf r=(1,2,3)+\lambda(4,-2,-1)}$ **(ii)** $\boxed{\lambda=\frac14,\ \mu=\frac12}$, and $2.75\ne0.5$;
the directions are not multiples: $\boxed{\text{skew}}$.

**7.4** $2a+3=0$; then $\mu=3$, $\lambda=-4$: $\boxed{a=-\frac32,\ b=14}$.

---

## § 8

**8.1 (a)** $\boxed{063^\circ}$. **(b)** $\sqrt{56}=\boxed{7.48}>\sqrt{24}=\boxed{4.90}$ km/min.
**(d)(i)** $t_1=2$, $t_2=\frac32$: $\boxed{P(7,3,9)}$. **(ii)** $\boxed{0.5}$ minutes.

**8.2 (a)** $4\sqrt{725}=20\sqrt{29}=\boxed{108}$ km/h. **(b)** $\tan\beta=\frac{16}{20\sqrt{29}}$: $\boxed{\beta=8.45^\circ}$.
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
