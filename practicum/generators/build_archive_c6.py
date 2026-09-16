"""Собирает архивный ноутбук C6: вся тема плоскостей подряд.

Двадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2, A1,
E4, E5, E6, A2, D3, D4, D5, D6 и C5. Практикум учит: лестница из приёмов,
теория перед каждым, три уровня сложности, тренажёр распознавания,
задание на время. Архив не учит. Он даёт набивать руку: **вся тема
подряд, по тем же семи приёмам, без единой строчки теории**. Двадцать
два вопроса, 123 балла — всё, что архив спрашивает про плоскости, с мая
2021 по ноябрь 2025.

Разметка взята из карточки geometry-vectors-3d.yaml: поле blocks у
каждого приёма. Ноябрь 2023 года стоит в корпусе дважды, TZ1 и TZ2 одной
бумаги; здесь он один раз. Две системы уравнений из чужих тем (ноябрь
2025 TZ1 P1 Q6 в A8, ноябрь 2022 P3 Q1(b)(iii) в A4) сюда не входят:
первая стоит в практикуме заданием на время.

Части одного вопроса разнесены по своим приёмам: ноябрь 2021 Q11 — в
§§ 2, 3, 4 и 7, май 2022 TZ1 Q11 — в §§ 4, 5 и 6, май 2024 TZ2 Q11 — в
§§ 1, 6 и 7, ноябрь 2023 Q12 — в §§ 3, 6 и 7. Условие каждого пункта
повторено целиком, насколько оно нужно пункту.

«Show that» и «verify» здесь проверяются по промежуточной строке: левая
часть уравнения в точке, r · n в общей точке прямой, нормаль до сравнения
с напечатанным уравнением, точка прямой пересечения при x = 0.

Хешей нет ни одного: всякий ответ темы — плоскость, нормаль, точка, прямая,
расстояние или буква, и всякий проверяется самими плоскостями вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_c6.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/geometry/archive-c6-planes.ipynb')

ANSWERS = {
    # § 1. A point and a normal
    'q1_1a': '5',
    'q1_1b': '[-3, Rational(-3, 2)]',
    'q1_1c': '-3',
    'q1_2c_i': '18',
    'q1_2c_ii': '-6',
    'q1_2e': 'vec(1, 8, -2) + lam*vec(-4, -1, 3)',
    # § 2. A normal from two directions
    'q2_1': 'Eq(2*x - y - 4*z, 0)',
    'q2_2_AB': 'vec(-3, -2, 0)',
    'q2_2_AC': 'vec(-2, 1, -7)',
    'q2_2': 'Eq(2*x - 3*y - z, 6)',
    'q2_3': 'vec(1, -1, -1)',
    'q2_4': 'Eq(x - y + z, 15)',
    'q2_5': 'vec(1, 1, -1)',
    'q2_6': 'Eq(-x + y - z, -5)',
    'q2_7_i': 'vec(5, 4, 2) + lam*vec(1, -1, 1) + mu*vec(2, 1, 3)',
    'q2_7_ii': '-18',
    'q2_8': 'Eq(-123*x - 6*y + 9*z, 0)',
    # § 3. A line and a plane
    'q3_1_i': 'Rational(3, 4)',
    'q3_1_ii': '(Rational(3, 4), Rational(-5, 4), Rational(-3, 4))',
    'q3_2_L': '2*(2 + 3*s) - (-3 + 6*s)',
    'q3_2_M': '2*(9 + t) - (11 + 2*t)',
    'q3_3_L': 'vec(0, -3, 2) + lam*vec(-1, 1, -1)',
    'q3_3': '(-6, 3, -4)',
    # § 4. Two planes
    'q4_1': 'vec(-7, -7, 7)',
    'q4_2': 'vec(1, -2, 0) + lam*vec(-1, -5, -3)',
    'q4_3_point': '(0, 2, 4)',
    'q4_3_direction': 'vec(-5, 10, 10)',
    # § 5. Three planes and systems
    'q5_1': '(Rational(41, 21), Rational(-10, 21), Rational(23, 21))',
    'q5_2': "'none'",
    'q5_2_value': '-15',
    'q5_3': '[Rational(4, 3), 19]',
    'q5_4a': 'vec(t, Rational(27, 2) - 3*t, Rational(17, 2) - 2*t)',
    'q5_4b': '(29, -73.5, -49.5)',
    'q5_4c_i': '4',
    'q5_4c_ii': '26',
    # § 6. The perpendicular
    'q6_1': 'sqrt(94)/2',
    'q6_2_i': 'Eq(y - 2*z, -4)',
    'q6_2_ii': '(0, -0.8, 1.6)',
    'q6_3_i': '(-3, 6, 5)',
    'q6_3_ii': '6.71',
    'q6_4_i': '(1, Rational(-5, 2), 2)',
    'q6_4_ii': 'sqrt(11)',
    # § 7. The reflection
    'q7_1_i': '(Rational(3, 2), -2, Rational(-3, 2))',
    'q7_1_ii': 'vec(Rational(3, 2), -2, Rational(-3, 2)) + mu*vec(1, -1, -1)',
    'q7_2': '(-3, 0, 8)',
    'q7_3': 'Eq(x + 3*y - z, Rational(27, 2))',
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
# C6 archive — planes, all of it

**Twenty-two questions, 123 marks.** Every question the archive asks about
planes, from May 2021 to November 2025, in the order of the seven techniques
rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-c6-planes.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | A point and a normal | 2 | 12 |
| 2 | A normal from two directions | 8 | 29 |
| 3 | A line and a plane | 3 | 11 |
| 4 | Two planes | 3 | 10 |
| 5 | Three planes and systems | 4 | 16 |
| 6 | The perpendicular: foot and distance | 4 | 29 |
| 7 | The reflection | 3 | 16 |

The checks are the same ones the practicum uses and they store nothing:
each is handed the planes and lines exactly as the question prints them —
`plane(Eq(2*x - y + z, 4))`, `plane(A, B, C)`, `line(vec(0, -2, 0) + lam*vec(1, 1, -1))` —
and a point or a letter the question asks for is handed **the conditions**
that fix it: `on(C, P)`, `perpendicular(C - B, P)`, `reflection(image, B, P)`,
`meet_in_line(P1, P2, P3)`. A plane is accepted as any multiple of its
equation or in vector form; a line with any point on it and any parallel
direction. Three significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** November 2021 Q11
appears in §§ 2, 3, 4 and 7; each part repeats what it needs.

**A *show that* or *verify* is checked by the line before the given result:**
the left-hand side at the point, $\mathbf r\cdot\mathbf n$ at the general point
of a line, the normal before it is compared with the printed equation.

Enter a plane as `Eq(a*x + b*y + c*z, d)` and a line as
`vec(point) + lam*vec(direction)`; `lam` and `mu` are $\lambda$ and $\mu$.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + vec, plane, cross, intersection, unknown

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ============================================================ § 1
md(r"""
---
# § 1. A point and a normal

**Two questions, 12 marks.** A point on a plane, parallel and perpendicular
planes, where a plane meets the axes, a line along the normal.
""")

md(r"""
### 1.1 — *May 2024 TZ2 Paper 1 Q11(a)–(c), 8 marks*

The plane $P_1$ has equation $2x+6y-2z=5$.

**(a)** Verify that the point $A\left(2,\frac12,1\right)$ lies on the plane $P_1$.

The plane $P_2$ is given by $(k^2-6)x+(2k+3)y+pz=q$, where $p,q,k\in\mathbb R$ and $p\ne0$.

**(b)** In the case where $p=-6$, $P_2$ is perpendicular to $P_1$ and $A$ lies on $P_2$.
Find the value of $k$ and the value of $q$.

For parts (c), (d) and (e) it is now given that $P_2$ is parallel to $P_1$ with $k=3$.

**(c)** Determine the value of $p$.

*For (a) enter the left-hand side of $P_1$ worked out at $A$.*
""")

code(r"""
k, p, q = symbols('k p q')
A = vec(2, Rational(1, 2), 1)
P1 = plane(Eq(2*x + 6*y - 2*z, 5), name='P1')
P2 = plane(Eq((k**2 - 6)*x + (2*k + 3)*y + p*z, q), name='P2')

q1_1a = ...      # 2x + 6y − 2z at A
q1_1b = [...]    # [k, q]
q1_1c = ...      # p

verify_find('1.1(a)', q1_1a, P1.side(A))
verify_find('1.1(b)', q1_1b, [k, q], [perpendicular(P1, P2.subs(p, -6)), on(A, P2.subs(p, -6))])
verify_find('1.1(c)', q1_1c, p, [parallel(P1, P2.subs(k, 3))])
""")

md(r"""
### 1.2 — *November 2025 TZ1 Paper 2 Q12(c), (e), 4 marks*

The plane $\Pi$ has Cartesian equation $4x+y-3z=18$. The lines $L_1$ and $L_2$ lie in
$\Pi$ and intersect at the point with position vector $\begin{pmatrix}1\\8\\-2\end{pmatrix}$.

The plane intersects the coordinate axes at $P(4.5,0,0)$, $Q(0,q,0)$ and $R(0,0,r)$.

**(c)** Write down the value of **(i)** $q$; **(ii)** $r$.

Another line, $L_3$, is normal to $\Pi$ and passes through the point of intersection
of $L_1$ and $L_2$.

**(e)** Write down an equation for $L_3$ in the form $\mathbf r_3=\mathbf m+\gamma\mathbf n$.

*Use `lam` for $\gamma$.*
""")

code(r"""
Pi = plane(Eq(4*x + y - 3*z, 18))
X = vec(1, 8, -2)
at_q, at_r = unknown('q'), unknown('r')

q1_2c_i = ...    # q
q1_2c_ii = ...   # r
q1_2e = ...      # L3: vec(...) + lam*vec(...)

verify_find('1.2(c)(i)', q1_2c_i, at_q, [on(vec(0, at_q, 0), Pi)])
verify_find('1.2(c)(ii)', q1_2c_ii, at_r, [on(vec(0, 0, at_r), Pi)])
verify_line('1.2(e)', q1_2e, line(X, Pi.normal))
""")

# ============================================================ § 2
md(r"""
---
# § 2. A normal from two directions

**Eight questions, 29 marks.** Three points, a line and a point, two lines,
a plane perpendicular to two planes — and the vector product that turns two
directions into a normal.
""")

md(r"""
### 2.1 — *May 2021 TZ1 Paper 2 Q6(a), 3 marks*

Consider the planes $\Pi_1$ and $\Pi_2$ with the following equations.

$$\Pi_1:\ 3x+2y+z=6\qquad\Pi_2:\ x-2y+z=4$$

**(a)** Find a Cartesian equation of the plane $\Pi_3$ which is perpendicular to $\Pi_1$
and $\Pi_2$ and passes through the origin $(0,0,0)$.
""")

code(r"""
P1 = plane(Eq(3*x + 2*y + z, 6), name='Π1')
P2 = plane(Eq(x - 2*y + z, 4), name='Π2')

q2_1 = ...       # Π3: Eq(...)

verify_plane('2.1', q2_1, plane(vec(0, 0, 0), P1, P2))
""")

md(r"""
### 2.2 — *November 2021 Paper 2 Q11(a), 7 marks*

Three points $A(3,0,0)$, $B(0,-2,0)$ and $C(1,1,-7)$ lie on the plane $\Pi_1$.

**(a)** **(i)** Find the vector $\overrightarrow{AB}$ and the vector $\overrightarrow{AC}$.

**(ii)** Hence find the equation of $\Pi_1$, expressing your answer in the form
$ax+by+cz=d$, where $a,b,c,d\in\mathbb Z$.
""")

code(r"""
A, B, C = vec(3, 0, 0), vec(0, -2, 0), vec(1, 1, -7)

q2_2_AB = ...    # AB
q2_2_AC = ...    # AC
q2_2 = ...       # Π1: Eq(...)

verify_find('2.2(a)(i) AB', q2_2_AB, B - A)
verify_find('2.2(a)(i) AC', q2_2_AC, C - A)
verify_plane('2.2(a)(ii)', q2_2, plane(A, B, C))
""")

md(r"""
### 2.3 — *May 2023 TZ1 Paper 1 Q12(d), 2 marks*

Two lines, $L_1$ and $L_2$, intersect at point $P$. Point $A(2t,8,3)$, where $t>0$, lies
on $L_2$. The direction vector of $L_1$ is $\begin{pmatrix}1\\1\\0\end{pmatrix}$, and
$\overrightarrow{PA}=\begin{pmatrix}2t\\0\\3+t\end{pmatrix}$. It is found in part (b) that $t=3$.

A plane, $\Pi$, contains $L_1$ and $L_2$.

**(d)** Find a normal vector to $\Pi$.

*Parts (a)–(c) and (e) are in C5, A4, C7 and C2. $P$ is not given, and a normal
does not need it: the check puts $P$ at the origin.*
""")

code(r"""
PA = vec(6, 0, 6)                        # (2t, 0, 3 + t) at t = 3
point_P = vec(0, 0, 0)                   # not given; a normal does not depend on it
Pi = plane(line(point_P, vec(1, 1, 0)), line(point_P, PA))

q2_3 = ...       # a normal to Π

verify_normal_vector('2.3', q2_3, Pi)
""")

md(r"""
### 2.4 — *May 2025 TZ1 Paper 1 Q11(b), 4 marks*

The plane $P_1$ has equation $x+2y+z=0$ and the plane $P_2$ has equation $x-y-2z=0$.

A third plane $P_3$ is perpendicular to both $P_1$ and $P_2$.

The unique point of intersection of all three planes is the point $R(5,-5,5)$.

**(b)** Find the Cartesian equation of $P_3$.
""")

code(r"""
P1 = plane(Eq(x + 2*y + z, 0), name='P1')
P2 = plane(Eq(x - y - 2*z, 0), name='P2')

q2_4 = ...       # P3: Eq(...)

verify_plane('2.4', q2_4, plane(vec(5, -5, 5), P1, P2))
""")

md(r"""
### 2.5 — *May 2025 TZ2 Paper 2 Q9(a), 4 marks*

A line $L_1$ has vector equation $\mathbf r=\begin{pmatrix}0\\0\\2\end{pmatrix}+t\begin{pmatrix}1\\0\\1\end{pmatrix}$ where $t\in\mathbb R$.

The plane $P_1$ contains the line $L_1$ and passes through the point $(2,1,5)$.

**(a)** Show that the Cartesian equation of the plane $P_1$ is $x+y-z=-2$.

*Enter the normal you get from the line and the point.*
""")

code(r"""
L1 = line(vec(0, 0, 2) + t*vec(1, 0, 1), t)

q2_5 = ...       # a normal of P1

verify_normal_vector('2.5', q2_5, plane(L1, vec(2, 1, 5)))
""")

md(r"""
### 2.6 — *May 2025 TZ3 Paper 1 Q11(d), 2 marks*

The points $A(1,-4,0)$, $B(-3,-6,2)$, $C(-1,-2,4)$ and $D(3,0,2)$ form a
parallelogram, $ABCD$. It is given that
$\overrightarrow{AB}\times\overrightarrow{AD}=m\begin{pmatrix}-1\\1\\-1\end{pmatrix}$, where $m\in\mathbb Z^+$.

The plane, $P_1$, contains the parallelogram $ABCD$.

**(d)** Find the Cartesian equation of $P_1$.
""")

code(r"""
A, B, C, D = vec(1, -4, 0), vec(-3, -6, 2), vec(-1, -2, 4), vec(3, 0, 2)

q2_6 = ...       # P1: Eq(...)

verify_plane('2.6', q2_6, plane(A, B, D))
""")

md(r"""
### 2.7 — *November 2025 TZ1 Paper 2 Q12(b), 3 marks*

The equations of two lines, $L_1$ and $L_2$, are given by:

$$L_1:\ \mathbf r_1=""" + col(5, 4, 2) + r"+s" + col(1, -1, 1) + r"""\ \text{ where } s\in\mathbb R\qquad L_2:\ \frac{x+1}{2}=y-7=\frac{z+5}{3}$$

The plane $\Pi$ contains the lines $L_1$ and $L_2$.

**(b)** **(i)** Write down the equation of $\Pi$, giving your answer in the form
$\mathbf r=\mathbf a+\lambda\mathbf b+\mu\mathbf c$ where $\lambda,\mu\in\mathbb R$.

**(ii)** Given that $\mathbf b\times\mathbf c=\begin{pmatrix}-4\\-1\\3\end{pmatrix}$, show that the Cartesian
equation of $\Pi$ is $4x+y-3z=18$.

*For (b)(ii) enter $\mathbf a\cdot(\mathbf b\times\mathbf c)$.*
""")

code(r"""
s = symbols('s')
L1 = line(vec(5, 4, 2) + s*vec(1, -1, 1), s)
L2 = cartesian((x + 1)/2, y - 7, (z + 5)/3)
a = vec(5, 4, 2)

q2_7_i = ...     # vec(a) + lam*vec(b) + mu*vec(c)
q2_7_ii = ...    # a · (b × c)

verify_plane('2.7(b)(i)', q2_7_i, plane(L1, L2))
verify_find('2.7(b)(ii)', q2_7_ii, dot(a, vec(-4, -1, 3)))
""")

md(r"""
### 2.8 — *November 2025 TZ3 Paper 1 Q10(f), 4 marks*

The point $P(-1,1,-13)$ lies on the line $L_1$. The point $N$ on the line $L_2$ is the
point of $L_2$ closest to $P$, and it is found in part (e) that
$N\left(\frac13,-\frac{10}3,\frac73\right)$.

**(f)** Point $O$ denotes the origin $(0,0,0)$. Find the equation of the plane containing
points $O$, $P$ and $N$, giving your answer in the form $\alpha x+\beta y+\gamma z=\delta$,
where $\alpha,\beta,\gamma,\delta\in\mathbb Z$.
""")

code(r"""
O, point_P, N = vec(0, 0, 0), vec(-1, 1, -13), vec(Rational(1, 3), Rational(-10, 3), Rational(7, 3))

q2_8 = ...       # the plane OPN: Eq(...)

verify_plane('2.8', q2_8, plane(O, point_P, N))
""")

# ============================================================ § 3
md(r"""
---
# § 3. A line and a plane

**Three questions, 11 marks.** The general point of a line into the equation
of a plane: one value of the parameter, every value, or none.
""")

md(r"""
### 3.1 — *November 2021 Paper 2 Q11(c), 3 marks*

The line $L$ has vector equation $\mathbf r=\begin{pmatrix}0\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\1\\-1\end{pmatrix}$.

**(c)** The plane $\Pi_3$ is given by $2x-2z=3$. The line $L$ and the plane $\Pi_3$
intersect at the point $P$.

**(i)** Show that at the point $P$, $\lambda=\frac34$.

**(ii)** Hence find the coordinates of $P$.

*For (i) enter the value of $\lambda$ that substituting gives.*
""")

code(r"""
L = line(vec(0, -2, 0) + lam*vec(1, 1, -1))
P3 = plane(Eq(2*x - 2*z, 3), name='Π3')
at_P = unknown('lambda')

q3_1_i = ...     # λ where L meets Π3
q3_1_ii = ...    # the point where L meets Π3

verify_find('3.1(c)(i)', q3_1_i, at_P, [on(L.at(at_P), P3)])
verify_intersection('3.1(c)(ii)', q3_1_ii, L, P3)
""")

md(r"""
### 3.2 — *November 2023 TZ1 Paper 2 Q12(b), 3 marks*

Line $L$ is given by the vector equation
$\mathbf r_1=\begin{pmatrix}1\\2\\-3\end{pmatrix}+s\begin{pmatrix}2\\3\\6\end{pmatrix}$ where $s\in\mathbb R$.

Line $M$ is given by the vector equation
$\mathbf r_2=\begin{pmatrix}9\\9\\11\end{pmatrix}+t\begin{pmatrix}4\\1\\2\end{pmatrix}$ where $t\in\mathbb R$.

**(b)** Verify that the lines $L$ and $M$ both lie in the plane $P$ given by
$\mathbf r\cdot\begin{pmatrix}0\\2\\-1\end{pmatrix}=7$.

*Enter $\mathbf r\cdot(0,2,-1)$ at the general point of each line, in terms of its
parameter.*
""")

code(r"""
s = symbols('s')
L = line(vec(1, 2, -3) + s*vec(2, 3, 6), s)
M = line(vec(9, 9, 11) + t*vec(4, 1, 2), t)
n = vec(0, 2, -1)

q3_2_L = ...     # r · (0, 2, −1) along L, in terms of s
q3_2_M = ...     # the same along M, in terms of t

verify_find('3.2(b) L', q3_2_L, dot(L.at(s), n))
verify_find('3.2(b) M', q3_2_M, dot(M.at(t), n))
""")

md(r"""
### 3.3 — *May 2025 TZ3 Paper 1 Q11(f), 5 marks*

The plane $P_1$ has equation $-x+y-z=-5$ and contains the parallelogram $ABCD$,
whose diagonals intersect at $E(0,-3,2)$.

A second plane, $P_2$, has Cartesian equation $5x+y-7z=1$.

The line $L$ passes through $E$ and is perpendicular to $P_1$.

The line $L$ intersects the plane $P_2$ at point $F$.

**(f)** Find the coordinates of $F$.

*Enter the line $L$ too.*
""")

code(r"""
E = vec(0, -3, 2)
P1 = plane(Eq(-x + y - z, -5), name='P1')
P2 = plane(Eq(5*x + y - 7*z, 1), name='P2')
L = line(E, P1.normal)

q3_3_L = ...     # L: vec(...) + lam*vec(...)
q3_3 = ...       # F

verify_line('3.3(f) L', q3_3_L, L)
verify_intersection('3.3(f)', q3_3, L, P2)
""")

# ============================================================ § 4
md(r"""
---
# § 4. Two planes

**Three questions, 10 marks.** The line where two planes meet: a common point
and the direction $\mathbf n_1\times\mathbf n_2$.
""")

md(r"""
### 4.1 — *November 2021 Paper 2 Q11(b), 2 marks*

The plane $\Pi_1$ has equation $2x-3y-z=6$. Plane $\Pi_2$ has equation $3x-y+2z=2$.

**(b)** The line $L$ is the intersection of $\Pi_1$ and $\Pi_2$. Verify that the vector
equation of $L$ can be written as
$\mathbf r=\begin{pmatrix}0\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\1\\-1\end{pmatrix}$.

*Enter $\mathbf n_1\times\mathbf n_2$.*
""")

code(r"""
P1 = plane(Eq(2*x - 3*y - z, 6), name='Π1')
P2 = plane(Eq(3*x - y + 2*z, 2), name='Π2')

q4_1 = ...       # n1 × n2

verify_direction('4.1(b)', q4_1, intersection(P1, P2))
""")

md(r"""
### 4.2 — *May 2022 TZ1 Paper 1 Q11(b), 5 marks*

Consider the planes $\Pi_1:\ 2x-y+z=4$ and $\Pi_2:\ x-2y+3z=5$.

**(b)** **(i)** Verify that the point $P(1,-2,0)$ lies on both $\Pi_1$ and $\Pi_2$.

**(ii)** Find a vector equation of $L$, the line of intersection of $\Pi_1$ and $\Pi_2$.
""")

code(r"""
P1 = plane(Eq(2*x - y + z, 4), name='Π1')
P2 = plane(Eq(x - 2*y + 3*z, 5), name='Π2')

q4_2 = ...       # L: vec(...) + lam*vec(...)

verify_intersection('4.2(b)(ii)', q4_2, P1, P2)
""")

md(r"""
### 4.3 — *May 2023 TZ2 Paper 2 Q6(a), 3 marks*

Consider the two planes $\Pi_1:\ 2x-y+2z=6$ and $\Pi_2:\ 4x+3y-z=2$.

Let $L$ be the line of intersection of $\Pi_1$ and $\Pi_2$.

**(a)** Verify that a vector equation of $L$ is
$\mathbf r=\begin{pmatrix}0\\2\\4\end{pmatrix}+\lambda\begin{pmatrix}1\\-2\\-2\end{pmatrix}$, where $\lambda\in\mathbb R$.

*Enter the point of $L$ with $x=0$ and the direction $\mathbf n_1\times\mathbf n_2$.*
""")

code(r"""
P1 = plane(Eq(2*x - y + 2*z, 6), name='Π1')
P2 = plane(Eq(4*x + 3*y - z, 2), name='Π2')

q4_3_point = ...       # the point of L where x = 0
q4_3_direction = ...   # n1 × n2

verify_intersection('4.3(a) point', q4_3_point, P1, P2, plane(Eq(x, 0)))
verify_direction('4.3(a) direction', q4_3_direction, intersection(P1, P2))
""")

# ============================================================ § 5
md(r"""
---
# § 5. Three planes and systems of equations

**Four questions, 16 marks.** One point, a line of points, or none — and the
letters that decide which.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 2 Q6(b), 2 marks*

Consider the planes

$$\Pi_1:\ 3x+2y+z=6\qquad\Pi_2:\ x-2y+z=4\qquad\Pi_3:\ 2x-y-4z=0$$

**(b)** Find the coordinates of the point where $\Pi_1$, $\Pi_2$ and $\Pi_3$ intersect.
""")

code(r"""
P1 = plane(Eq(3*x + 2*y + z, 6), name='Π1')
P2 = plane(Eq(x - 2*y + z, 4), name='Π2')
P3 = plane(Eq(2*x - y - 4*z, 0), name='Π3')

q5_1 = ...       # the point

verify_intersection('5.1(b)', q5_1, P1, P2, P3)
""")

md(r"""
### 5.2 — *May 2022 TZ1 Paper 1 Q11(a), 4 marks*

Consider the three planes

$$\Pi_1:\ 2x-y+z=4\qquad\Pi_2:\ x-2y+3z=5\qquad\Pi_3:\ -9x+3y-2z=32$$

**(a)** Show that the three planes do not intersect.

*Enter what the three planes share — a point, a line or `'none'` — and the value
of $-9x+3y-2z$ along the line where $\Pi_1$ and $\Pi_2$ meet.*
""")

code(r"""
P1 = plane(Eq(2*x - y + z, 4), name='Π1')
P2 = plane(Eq(x - 2*y + 3*z, 5), name='Π2')
P3 = plane(Eq(-9*x + 3*y - 2*z, 32), name='Π3')

q5_2 = ...           # a point, a line, or 'none'
q5_2_value = ...     # −9x + 3y − 2z along the line where Π1 and Π2 meet

verify_intersection('5.2(a)', q5_2, P1, P2, P3)
verify_find('5.2(a) value', q5_2_value, P3.side(intersection(P1, P2).at(lam)))
""")

md(r"""
### 5.3 — *May 2025 TZ2 Paper 2 Q9(b), 4 marks*

Consider the three planes

$$P_1:\ x+y-z=-2\qquad P_2:\ 2x+by-z=3\qquad P_3:\ x-y+2z=d$$

where $b,d\in\mathbb R^+$.

The three planes intersect in a line.

**(b)** Find the value of $b$ and the value of $d$.
""")

code(r"""
b, d = symbols('b d')
P1 = plane(Eq(x + y - z, -2), name='P1')
P2 = plane(Eq(2*x + b*y - z, 3), name='P2')
P3 = plane(Eq(x - y + 2*z, d), name='P3')

q5_3 = [...]     # [b, d]

verify_find('5.3(b)', q5_3, [b, d], [meet_in_line(P1, P2, P3), b > 0, d > 0])
""")

md(r"""
### 5.4 — *November 2025 TZ3 Paper 2 Q7, 6 marks*

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

*In (a) enter `vec(x, y, z)` in terms of `t`.*
""")

code(r"""
a, k = unknown('a'), unknown('k')
first = plane(Eq(2*x + 6*y - 8*z, 13))
second = plane(Eq(3*x - y + 3*z, 12))
third = plane(Eq(a*x + 12*y - 16*z, k))

q5_4a = ...      # vec(x, y, z) in terms of t
q5_4b = ...      # (x, y, z)
q5_4c_i = ...    # a
q5_4c_ii = ...   # k

verify_intersection('5.4(a)', q5_4a, first, second)
verify_intersection('5.4(b)', q5_4b, first, second, third.subs({a: 3, k: -3}))
verify_find('5.4(c)(i)', q5_4c_i, a, [no_unique_meet(first, second, third)])
verify_find('5.4(c)(ii)', q5_4c_ii, k, [meet_in_line(first, second, third)])
""")

# ============================================================ § 6
md(r"""
---
# § 6. The perpendicular: foot and distance

**Four questions, 29 marks.** From a point along the normal to the plane:
where it lands, and how far that is.
""")

md(r"""
### 6.1 — *May 2022 TZ1 Paper 1 Q11(c), 6 marks*

The line $L$, $\mathbf r=\begin{pmatrix}1\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\5\\3\end{pmatrix}$, is the line of
intersection of $\Pi_1:\ 2x-y+z=4$ and $\Pi_2:\ x-2y+3z=5$.

The plane $\Pi_3$ has equation $-9x+3y-2z=32$.

**(c)** Find the distance between $L$ and $\Pi_3$.

*Paper 1: exact.*
""")

code(r"""
L = line(vec(1, -2, 0) + lam*vec(1, 5, 3))
P3 = plane(Eq(-9*x + 3*y - 2*z, 32), name='Π3')

q6_1 = ...       # the distance, exact

verify_distance('6.1(c)', q6_1, L, P3, exact=True)
""")

md(r"""
### 6.2 — *November 2022 Paper 2 Q12(d), 9 marks*

Consider the points $A(1,2,3)$, $B(k,-2,1)$ and $C(5,0,2)$, where $k\in\mathbb R$.

**(d)** For $k\ne9$, let $\Pi$ be the plane containing $A$, $B$ and $C$.

**(i)** Find the Cartesian equation of the plane $\Pi$.

**(ii)** Find the coordinates of the point on the plane $\Pi$ which is closest to the
origin $(0,0,0)$.
""")

code(r"""
k = symbols('k')
Pi = plane(vec(1, 2, 3), vec(k, -2, 1), vec(5, 0, 2))
closest = unknown('X', 3)

q6_2_i = ...     # Π: Eq(...)
q6_2_ii = ...    # the point closest to the origin

verify_plane('6.2(d)(i)', q6_2_i, Pi)
verify_find('6.2(d)(ii)', q6_2_ii, closest, [on(closest, Pi), perpendicular(closest, Pi)])
""")

md(r"""
### 6.3 — *November 2023 TZ1 Paper 2 Q12(c), 7 marks*

The plane $P$ is given by $\mathbf r\cdot\begin{pmatrix}0\\2\\-1\end{pmatrix}=7$.

Point $B$ has position vector $\begin{pmatrix}-3\\12\\2\end{pmatrix}$. A line through $B$ perpendicular to
$P$ intersects $P$ at point $C$.

**(c)** **(i)** Find the position vector of $C$.

**(ii)** Hence, find $\lvert\overrightarrow{BC}\rvert$.
""")

code(r"""
plane_P = plane(Eq(dot(vec(x, y, z), vec(0, 2, -1)), 7))
B = vec(-3, 12, 2)
C = unknown('C', 3)

q6_3_i = ...     # C
q6_3_ii = ...    # |BC|

verify_find('6.3(c)(i)', q6_3_i, C, [on(C, plane_P), perpendicular(C - B, plane_P)])
verify_distance('6.3(c)(ii)', q6_3_ii, B, plane_P)
""")

md(r"""
### 6.4 — *May 2024 TZ2 Paper 1 Q11(d), 7 marks*

The plane $P_1$ has equation $2x+6y-2z=5$, and the point $A\left(2,\frac12,1\right)$ lies on $P_1$.

The plane $P_2$, parallel to $P_1$, has equation $3x+9y-3z=-\frac{51}2$.

The line through $A$ that is perpendicular to $P_1$ meets $P_2$ at the point $B$.

**(d)** **(i)** Find the coordinates of $B$.

**(ii)** Hence, show that the perpendicular distance between $P_1$ and $P_2$ is $\sqrt{11}$.

*For (ii) enter the distance, exact.*
""")

code(r"""
A = vec(2, Rational(1, 2), 1)
P1 = plane(Eq(2*x + 6*y - 2*z, 5), name='P1')
P2 = plane(Eq(3*x + 9*y - 3*z, Rational(-51, 2)), name='P2')
B = unknown('B', 3)

q6_4_i = ...     # B
q6_4_ii = ...    # the distance between P1 and P2

verify_find('6.4(d)(i)', q6_4_i, B, [on(B, P2), perpendicular(B - A, P1)])
verify_distance('6.4(d)(ii)', q6_4_ii, P1, P2, exact=True)
""")

# ============================================================ § 7
md(r"""
---
# § 7. The reflection

**Three questions, 16 marks.** Twice the step to the foot: a reflected point, a
reflected line, a parallel plane on the other side.
""")

md(r"""
### 7.1 — *November 2021 Paper 2 Q11(d), 9 marks*

The line $L$ has vector equation $\mathbf r=\begin{pmatrix}0\\-2\\0\end{pmatrix}+\lambda\begin{pmatrix}1\\1\\-1\end{pmatrix}$, and the
plane $\Pi_3$ is given by $2x-2z=3$.

**(d)** The point $B(0,-2,0)$ lies on $L$.

**(i)** Find the reflection of the point $B$ in the plane $\Pi_3$.

**(ii)** Hence find the vector equation of the line formed when $L$ is reflected in
the plane $\Pi_3$.
""")

code(r"""
L = line(vec(0, -2, 0) + lam*vec(1, 1, -1))
P3 = plane(Eq(2*x - 2*z, 3), name='Π3')
B = vec(0, -2, 0)
image = unknown('image', 3)

q7_1_i = ...     # the reflection of B
q7_1_ii = ...    # the reflected line: vec(...) + mu*vec(...)

verify_find('7.1(d)(i)', q7_1_i, image, [reflection(image, B, P3)])
verify_line('7.1(d)(ii)', q7_1_ii, mirror(L, P3))
""")

md(r"""
### 7.2 — *November 2023 TZ1 Paper 2 Q12(d), 3 marks*

The plane $P$ is given by $\mathbf r\cdot\begin{pmatrix}0\\2\\-1\end{pmatrix}=7$, and point $B$ has position
vector $\begin{pmatrix}-3\\12\\2\end{pmatrix}$.

**(d)** Find the reflection of the point $B$ in the plane $P$.
""")

code(r"""
plane_P = plane(Eq(dot(vec(x, y, z), vec(0, 2, -1)), 7))
B = vec(-3, 12, 2)
image = unknown('image', 3)

q7_2 = ...       # the reflection of B

verify_find('7.2(d)', q7_2, image, [reflection(image, B, plane_P)])
""")

md(r"""
### 7.3 — *May 2024 TZ2 Paper 1 Q11(e), 4 marks*

The plane $P_1$ has equation $2x+6y-2z=5$, and the point $A\left(2,\frac12,1\right)$ lies on $P_1$.
The plane $P_2:\ 3x+9y-3z=-\frac{51}2$ is parallel to $P_1$ at a perpendicular distance of
$\sqrt{11}$ from it, and the line through $A$ perpendicular to $P_1$ meets $P_2$ at
$B\left(1,-\frac52,2\right)$.

**(e)** Find the equation of a third parallel plane $P_3$ which is also a perpendicular
distance of $\sqrt{11}$ from $P_1$.

*The check builds $P_3$ as the mirror image of $P_2$ in $P_1$.*
""")

code(r"""
P1 = plane(Eq(2*x + 6*y - 2*z, 5), name='P1')
B = vec(1, Rational(-5, 2), 2)

q7_3 = ...       # P3: Eq(...)

verify_plane('7.3(e)', q7_3, plane(mirror(B, P1), P1.normal))
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1

**1.1 (a)** $4+3-2=\boxed{5}$. **(b)** $2(k^2-6)+6(2k+3)+12=2(k+3)^2=0$: $k=-3$; then
$3x-3y-6z=q$ through $A$: $\boxed{k=-3,\ q=-\frac32}$. **(c)** $(3,9,p)=\frac32(2,6,-2)$: $\boxed{p=-3}$.

**1.2 (c)** $\boxed{q=18}$, $\boxed{r=-6}$. **(e)** $\boxed{\mathbf r_3=(1,8,-2)+\gamma(-4,-1,3)}$.

---

## § 2

**2.1** $(3,2,1)\times(1,-2,1)=(4,-2,-8)$: $\boxed{2x-y-4z=0}$.

**2.2 (i)** $\boxed{\overrightarrow{AB}=(-3,-2,0)}$, $\boxed{\overrightarrow{AC}=(-2,1,-7)}$. **(ii)** $(14,-21,-7)$, through $A$:
$\boxed{2x-3y-z=6}$.

**2.3** $(1,1,0)\times(6,0,6)=(6,-6,-6)$: $\boxed{\mathbf n=(1,-1,-1)}$, as a vector, not coordinates.

**2.4** $(1,2,1)\times(1,-1,-2)=(-3,3,-3)$, through $R$: $\boxed{x-y+z=15}$.

**2.5** $(1,0,1)\times(2,1,3)=(-1,-1,1)$: $\boxed{\mathbf n=(1,1,-1)}$, and $(0,0,2)$ gives $x+y-z=-2$.

**2.6** $\overrightarrow{AB}\times\overrightarrow{AD}=(-12,12,-12)$, through $A$: $\boxed{-x+y-z=-5}$.

**2.7 (i)** $\boxed{\mathbf r=(5,4,2)+\lambda(1,-1,1)+\mu(2,1,3)}$. **(ii)** $(5,4,2)\cdot(-4,-1,3)=\boxed{-18}$, so
$4x+y-3z=18$.

**2.8** $(-1,1,-13)\times(1,-10,7)=(-123,-6,9)$, through $O$: $\boxed{-123x-6y+9z=0}$, which is
$41x+2y-3z=0$.

---

## § 3

**3.1** $2\lambda-2(-\lambda)=3$: $\boxed{\lambda=\frac34}$, $\boxed{P\left(\frac34,-\frac54,-\frac34\right)}$.

**3.2** $2(2+3s)-(-3+6s)=\boxed{7}$ and $2(9+t)-(11+2t)=\boxed{7}$ for every $s$ and $t$.

**3.3** $\boxed{L:\ \mathbf r=(0,-3,2)+\lambda(-1,1,-1)}$; $3\lambda-17=1$, $\lambda=6$: $\boxed{F(-6,3,-4)}$.

---

## § 4

**4.1** $\boxed{(-7,-7,7)}=-7(1,1,-1)$, and $(0,-2,0)$ is on both planes.

**4.2** $(2,-1,1)\times(1,-2,3)=(-1,-5,-3)$: $\boxed{\mathbf r=(1,-2,0)+\lambda(-1,-5,-3)}$.

**4.3** $x=0$: $\boxed{(0,2,4)}$. $(2,-1,2)\times(4,3,-1)=\boxed{(-5,10,10)}$.

---

## § 5

**5.1** $\boxed{\left(\frac{41}{21},-\frac{10}{21},\frac{23}{21}\right)}=(1.95,-0.476,1.10)$.

**5.2** $-3x+z=-3$ and $-3x+z=44$: $\boxed{\text{none}}$; along $L$, $-9x+3y-2z=\boxed{-15}$.

**5.3** $(3b-4)y=19-d$: $\boxed{b=\frac43,\ d=19}$.

**5.4 (a)** $\boxed{(x,y,z)=\left(t,\ \frac{27}2-3t,\ \frac{17}2-2t\right)}$. **(b)** $\boxed{(29,-73.5,-49.5)}$.
**(c)** $\boxed{a=4}$, $\boxed{k=26}$.

---

## § 6

**6.1** $L\parallel\Pi_3$; from $(1,-2,0)$ along $(-9,3,-2)$: $t=\frac12$, $\boxed{\frac{\sqrt{94}}2}$.

**6.2 (i)** $(0,k-9,18-2k)=(k-9)(0,1,-2)$: $\boxed{y-2z=-4}$. **(ii)** $t(0,1,-2)$, $5t=-4$:
$\boxed{(0,-0.8,1.6)}$.

**6.3 (i)** $22+5\lambda=7$, $\lambda=-3$: $\boxed{C(-3,6,5)}$. **(ii)** $3\sqrt5=\boxed{6.71}$.

**6.4 (i)** $A+\lambda(2,6,-2)$ into $P_2$: $\frac{15}2+66\lambda=-\frac{51}2$, $\lambda=-\frac12$: $\boxed{B\left(1,-\frac52,2\right)}$.
**(ii)** $\overrightarrow{AB}=(-1,-3,1)$, $\boxed{\sqrt{11}}$.

---

## § 7

**7.1 (i)** $\mu=\frac38$ to the foot, twice: $\boxed{\left(\frac32,-2,-\frac32\right)}$. **(ii)** through $P\left(\frac34,-\frac54,-\frac34\right)$
and $B'$: $\boxed{\mathbf r=\left(\frac32,-2,-\frac32\right)+\mu(1,-1,-1)}$.

**7.2** $\lambda=-6$: $\boxed{(-3,0,8)}$.

**7.3** $C=A+(A-B)=\left(3,\frac72,0\right)$: $\boxed{x+3y-z=\frac{27}2}$.
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
