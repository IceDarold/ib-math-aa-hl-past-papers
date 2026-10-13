"""Собирает практикум A6 (Муавр, корни из единицы, геометрия) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig, _complex_canon

I, P = sp.I, sp.pi
sq = sp.sqrt


def dz(v, sf=6):
    return digest(_complex_canon(v, sf))


def dset(vs, sf=6):
    return digest('|'.join(sorted(_complex_canon(v, sf) for v in vs)))


D_1 = digest(sig(-256, 6))
D_2N = digest(sig(3, 6))
D_2V = dz(8)
D_3 = digest(sig(9, 6))
D_4 = digest(sp.srepr(sp.simplify(P / 9)))
D_5 = dset([sq(2) * sp.exp(I * P / 12), sq(2) * sp.exp(-I * 11 * P / 12)])
D_6 = dset([sq(2) * sp.exp(-I * P / 3), sq(2) * sp.exp(I * 2 * P / 3)])
_q = sq(6) / 3
D_7 = dset([_q**sp.Rational(1, 3) * sp.exp(I * a) for a in
            (-11 * P / 36, 13 * P / 36, -35 * P / 36)])
D_8 = dset([-2, 1 - sq(3) * I])
D_9 = dset([2 * sp.exp(I * (P / 3 + P / 4)), 2 * sp.exp(I * (P + P / 4)),
            2 * sp.exp(I * (-P / 3 + P / 4))])
D_10 = digest(sig(24, 6))
D_11 = digest(sp.srepr(sp.simplify(2 - sq(3))))
D_SUM = dz(0)

TRIGGER = {1: 'power', 2: 'period', 3: 'period', 4: 'rot', 5: 'root', 6: 'root',
           7: 'root', 8: 'unity', 9: 'rot', 10: 'unity', 11: 'ident', 12: 'geom',
           13: 'ident', 14: 'unity', 15: 'power'}
TRIGGER_KEY = {i: digest(v) for i, v in TRIGGER.items()}

cells = []


def _lines(src):
    parts = src.strip('\n').split('\n')
    return [p + '\n' for p in parts[:-1]] + parts[-1:]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Practicum A6: de Moivre, roots of unity, geometry ⚙️

A continuation of A5. There the forms and the arithmetic were dealt with; here
begins what the polar form is for: **raising to a power and taking roots**.
112 marks, 70% of them with no calculator.

**Material.** 31 blocks from the AA HL archive: 27 blocks of the complex numbers
topic (94 marks) plus 4 blocks tagged as trigonometric identities (18 marks) — the
ones where the identity is obtained by raising to a power with de Moivre. The
technique there is complex numbers and the identity is only the result, so the
material lives here rather than in practicum C3.

**The border with A5.** If $z^n$ shows up in the solution, it belongs here. Modulus,
argument, conjugate, equating parts — those are A5.

**One formula, and everything follows from it.**

$$\bigl(r e^{i\theta}\bigr)^n = r^n e^{in\theta}.$$

Raising to a power means raising the modulus to that power and **multiplying** the
argument. Out of that come powers, roots, rotations and trigonometric identities:
four storylines that look different turn out to be one formula read in different
directions.

**How to work**

1. Read the map of techniques: six techniques, all of them readings of de Moivre's
   formula.
2. Draw the Argand plane. The $n$-th roots sit at the vertices of a regular
   $n$-gon, and the drawing often replaces the computation.
3. Enter the answer in any form: the check compares the number itself.
4. **One thing the check does not watch.** When the argument is asked for in the
   interval $(-\pi, \pi]$, bringing it into that interval is worth a mark of its own.
   But $e^{13i\pi/12}$ and $e^{-11i\pi/12}$ are the same number, and the check
   cannot tell them apart. Watch the range yourself: in the exam it is a mark.
5. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')
import sympy as sp
from kit import *

language('en')                 # this notebook is in English, and so are the checks

import matplotlib.pyplot as plt
import numpy as np

z, w = symbols('z w')
theta = Symbol('theta', real=True)

print('ready; sympy', sp.__version__)
print('de Moivre in one line:', expand((2*exp(I*pi/3))**3))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | The formula is read |
| --- | --- | --- | --- |
| 1 | Raising to a power | $z^n$ with a large $n$, «show that $z^n = \ldots$» | left to right |
| 2 | $n$-th roots | «find the square roots», «$z^3 = \ldots$» | right to left |
| 3 | Roots of unity | $z^n = 1$, a regular polygon, $\omega$ | as a symmetry |
| 4 | The periodicity condition | «the smallest $n$ for which $z^n$ is real» | through the argument |
| 5 | Rotation and geometry | «describe the transformation», an equilateral triangle | as a multiplication |
| 6 | Identities via de Moivre | «show that $\sin 5\theta \equiv \ldots$» | part by part |

All six are one formula. Technique 1 applies it directly. Technique 2 inverts it.
Technique 3 is the special case $z^n = 1$ of technique 2, but with such a strong
symmetry that it deserves a conversation of its own. Technique 4 looks only at the
argument and ignores the modulus. Technique 5 reads multiplication as a motion of
the plane. Technique 6 expands the power twice — by the binomial theorem and by de
Moivre — and equates the results.
""")

md(r"""
---
## Theory 1. Raising to a power

$$z = re^{i\theta} \;\Longrightarrow\; z^n = r^n e^{in\theta}
= r^n(\cos n\theta + i\sin n\theta).$$

What it means in practice: **never expand the brackets.** Computing $(1 - i)^{10}$
by the binomial theorem is eleven terms and an all but guaranteed mistake. With de
Moivre it is two lines: the modulus is $\sqrt2$ and the argument $-\frac{\pi}{4}$, so
$(\sqrt2)^{10} = 32$ and $10\cdot\left(-\frac{\pi}{4}\right) = -\frac{5\pi}{2}$.

The argument is then brought into $(-\pi, \pi]$ by adding $2\pi$:
$-\frac{5\pi}{2} + 2\pi = -\frac{\pi}{2}$. The answer is $32e^{-i\pi/2}$, that is,
$-32i$.

**A pleasant feature of conjugates.** If a question adds $z^n$ and $\bar z^n$, the
answer is always real: the imaginary parts are opposite and cancel. So

$$z^n + \bar z^n = 2r^n\cos n\theta,$$

and only the cosine has to be computed.
""")

md(r"""
## Task 1 🟢 — a large power without the binomial theorem

Show that

$$(1 + i\sqrt3)^8 + (1 - i\sqrt3)^8 = -256.$$

The numbers are conjugates, so it is enough to compute one and double the real part.

*Source: November 2025 TZ3, Paper 1, Q11(a)(ii) (4 marks, no calculator).*
""")

code(r"""
my_value = ...

check_num('Task 1', my_value, 6, '""" + D_1 + r"""')
""")

md(r"""
---
## Theory 2. The periodicity condition

The question «for what smallest $n$ is $z^n$ real» is solved **through the argument
alone**: the modulus affects nothing.

Translate the condition into an equality of arguments:

$$z^n \in \mathbb{R} \iff n\theta = k\pi, \qquad
z^n \text{ is purely imaginary} \iff n\theta = \frac{\pi}{2} + k\pi,$$

$$z^n = -i \iff n\theta = -\frac{\pi}{2} + 2k\pi.$$

That gives an equation in integers, and the smallest positive solution is wanted.
The mistake people make: taking the first $k$ rather than the one for which $n$ comes
out **a positive integer** — usually several values have to be tried.

The difference between «is real» and «$= -i$» matters. In the first case any multiple
of $\pi$ will do, in the second only one value modulo $2\pi$, which is why $n$ comes
out larger.
""")

md(r"""
## Task 2 🟢 — when the power becomes real

Given $u = -1 + \sqrt3\,i$ (the same number as in A5).

**(a)** Find the smallest positive integer $n$ for which $u^n$ is real.
**(b)** Evaluate $u^n$ for that $n$.

*Source: May 2023 TZ2, Paper 1, Q11(b) (5 marks, no calculator).*
""")

code(r"""
my_n = ...
my_un = ...

check_num('Task 2, n', my_n, 6, '""" + D_2N + r"""')
check_complex('Task 2, u^n', my_un, '""" + D_2V + r"""')
""")

md(r"""
## Task 3 🟡 — and now exactly −i

Given $z = \cos\dfrac{11\pi}{18} + i\sin\dfrac{11\pi}{18}$.

Find the smallest positive integer $n$ for which $z^n = -i$.

Here several values of $k$ have to be tried: it is not the first one that works.

*Source: May 2023 TZ1, Paper 2, Q6(a) (4 marks, calculator).*
""")

code(r"""
my_n3 = ...

check_num('Task 3', my_n3, 6, '""" + D_3 + r"""')
""")

md(r"""
## Task 4 🟡 — a power as a transformation of the plane

For the same $z$: describe, as a single geometric transformation, what happens to a
point of the Argand plane when $z$ becomes $z^{10}$.

Enter the **angle of rotation** anticlockwise, brought into the interval
$(-\pi, \pi]$, as an exact value.

The modulus here is one, so there is no stretch — only a rotation.

*Source: May 2023 TZ1, Paper 2, Q6(b) (3 marks, calculator).*
""")

code(r"""
my_rotation = ...        # the exact value of the angle

check_expr('Task 4', my_rotation, '""" + D_4 + r"""')
""")

md(r"""
---
## Theory 3. The n-th roots

The same formula read right to left. To solve $z^n = c$, write $c = Re^{i\varphi}$
and take

$$z_k = R^{1/n}\,e^{i(\varphi + 2\pi k)/n}, \qquad k = 0, 1, \ldots, n-1.$$

Three things to hold on to.

**There are exactly $n$ roots.** Not one. The equation $z^4 = 81$ has four
solutions, and the answer «$z = 3$» is worth one mark out of three: the two real
roots are visible at once, but there are two purely imaginary ones as well.

**Where the others come from.** The argument of a number is defined up to $2\pi$,
and on dividing by $n$ that $2\pi$ becomes $\frac{2\pi}{n}$ — the step between
neighbouring roots. After $k = n-1$ the roots start repeating.

**The geometry.** All the roots lie on a circle of radius $R^{1/n}$ and divide it
into $n$ equal parts, that is, they form a **regular $n$-gon**. Hence a fast way to
check an answer: if the roots are not placed symmetrically, something is wrong.
""")

code(r"""
# what the roots look like: a regular n-gon on a circle
fig, ax = plt.subplots(1, 3, figsize=(11, 3.6))
for axis, (n, c, name) in zip(ax, [(3, -8, 'z³ = −8'), (2, np.sqrt(3)+1j, 'z² = √3 + i'),
                                   (6, 1, 'z⁶ = 1')]):
    R, phi = abs(c), np.angle(c)
    pts = [R**(1/n) * np.exp(1j*(phi + 2*np.pi*k)/n) for k in range(n)]
    circle = np.exp(1j*np.linspace(0, 2*np.pi, 300)) * R**(1/n)
    axis.plot(circle.real, circle.imag, color='0.8', lw=1)
    axis.plot([p.real for p in pts] + [pts[0].real],
              [p.imag for p in pts] + [pts[0].imag], 'o-', lw=1.2, ms=6)
    axis.set_title(name, fontsize=10); axis.set_aspect('equal'); axis.grid(alpha=.3)
    axis.axhline(0, color='0.6', lw=.8); axis.axvline(0, color='0.6', lw=.8)
plt.tight_layout(); plt.show()
""")

md(r"""
## Task 5 🟡 — the square roots

Given $w = \sqrt3 + i$ (the same as in A5, task 4).

Using de Moivre's theorem, find **both** square roots of $w$ in the form
$re^{i\theta}$, where $-\pi < \theta \le \pi$.

*Source: November 2025 TZ1, Paper 1, Q11(c) (4 marks, no calculator).*
""")

code(r"""
my_sqrt_w = [...]        # both roots, order does not matter

check_complex_set('Task 5', my_sqrt_w, '""" + D_5 + r"""')
""")

md(r"""
## Task 6 🟡 — roots in polar form

Solve $z^2 = -1 - \sqrt3\,i$, giving the answers in the form
$r(\cos\theta + i\sin\theta)$.

The number under the root lies in the third quadrant — be careful with the argument.

*Source: May 2025 TZ2, Paper 1, Q12(a) (4 marks, no calculator).*
""")

code(r"""
my_roots6 = [...]

check_complex_set('Task 6', my_roots6, '""" + D_6 + r"""')
""")

md(r"""
## Task 7 🔴 — the quotient first, the root second

Given $z_1 = 3 - 3i$ and $z_2 = 2\sqrt3\,e^{5\pi i/6}$.

Find the three cube roots of $\dfrac{z_2}{z_1}$.

The order of work: put $z_1$ into exponential form (that is task 1 of A5), divide
using the properties of the modulus and the argument, bring the argument into
$(-\pi, \pi]$ and only then take the root.

*Source: May 2025 TZ3, Paper 1, Q8(b) (5 marks, no calculator).*
""")

code(r"""
my_cube_roots = [...]    # the three roots

check_complex_set('Task 7', my_cube_roots, '""" + D_7 + r"""')
""")

md(r"""
---
## Theory 4. The roots of unity

The special case $z^n = 1$, but with a symmetry that half of the Paper 3 questions
grow out of.

The roots: $\omega_k = e^{2\pi i k/n}$, the vertices of a regular $n$-gon inscribed
in the unit circle, starting at the point 1.

Two properties that get used all the time.

**The sum of all the roots is zero.** That can be seen geometrically: the vertices
of a regular polygon are symmetric about the centre, and the vectors out of the
centre cancel. For $n = 4$ it is completely direct: $1 + i + (-1) + (-i) = 0$.

Algebraically the same follows from the factorisation
$z^n - 1 = (z-1)(z^{n-1} + \ldots + z + 1)$: at $z = \omega \ne 1$ the first factor
is not zero, so the second one is — that is, the sum of all the roots other than 1
equals $-1$, and together with 1 it is zero. This identity turns up in questions
constantly, and for small $n$ it is quicker to derive it again than to remember it.

**All the powers close up.** $\omega^n = 1$, so $\omega^{n+1} = \omega$ and in
general exponents are counted modulo $n$. Large powers collapse instantly.

**What it is for in the exam.** The classic Paper 3 storyline: the points $P_0,
\ldots, P_{n-1}$ are the vertices of a regular $n$-gon, prove that the product of the
distances from $P_0$ to all the others equals $n$. It is solved through
$|1 - \omega^k|$ and the factorisation above.
""")

md(r"""
## Task 8 🟢 — the other roots of a cube

Given that $u = 1 + \sqrt3\,i$ is one of the roots of the equation $z^3 = -8$,
write down the other two roots in Cartesian form.

There is almost nothing to compute: the roots divide the circle into three equal
parts, and one of them has to be real.

*Source: May 2024 TZ1, Paper 1, Q12(c) (2 marks, no calculator).*
""")

code(r"""
my_others = [...]

check_complex_set('Task 8', my_others, '""" + D_8 + r"""')
""")

md(r"""
## Task 9 🟡 — rotating the whole picture

The points $U$, $V$, $W$ represent the roots from task 8, that is,
$1 + \sqrt3 i$, $-2$ and $1 - \sqrt3 i$.

Each point is rotated about the origin through $\dfrac{\pi}{4}$ anticlockwise. Find
the resulting $u'$, $v'$, $w'$ in the form $re^{i\theta}$, where
$-\pi < \theta \le \pi$.

A rotation through $\alpha$ is multiplication by $e^{i\alpha}$. The modulus does not
change, the arguments shift by $\alpha$.

*Source: May 2024 TZ1, Paper 1, Q12(e) (4 marks, no calculator).*
""")

code(r"""
my_rotated = [...]       # the three numbers

check_complex_set('Task 9', my_rotated, '""" + D_9 + r"""')
""")

md(r"""
## Task 10 🔴 — one equation for six points

All six numbers — $u, v, w$ from task 8 and $u', v', w'$ from task 9 — are solutions
of one equation of the form $z^n = a$.

Find the smallest positive integer $n$.

All six lie on the same circle, so any $n$ suits the modulus. The question is only
about the arguments: they have to fit the grid of solutions of $z^n = a$, and that
grid has step $\frac{2\pi}{n}$.

*Source: May 2024 TZ1, Paper 1, Q12(g) (3 marks, no calculator).*
""")

code(r"""
my_n10 = ...

check_num('Task 10', my_n10, 6, '""" + D_10 + r"""')
""")

md(r"""
---
## Theory 5. Trigonometric identities via de Moivre

The technique for whose sake 18 marks of identities live in this practicum and not in
C3. The idea is that $z^n$ expands in **two ways**.

Take $z = \cos\theta + i\sin\theta$, whose modulus is 1.

*By de Moivre:* $z^n = \cos n\theta + i\sin n\theta$.

*By the binomial theorem:* $z^n = (\cos\theta + i\sin\theta)^n$ expands into a sum
in which the powers of $i$ give alternating signs.

The two expressions are equal, so their real parts are equal and their imaginary
parts are equal. The real parts give a formula for $\cos n\theta$, the imaginary ones
a formula for $\sin n\theta$, both in powers of $\cos\theta$ and $\sin\theta$.

The order that saves time:

1. Expand $(\cos\theta + i\sin\theta)^n$ by the binomial theorem.
2. Replace $i^2 = -1$, $i^3 = -i$, $i^4 = 1$ and split into parts.
3. Equate the imaginary part to $\sin n\theta$ (or the real part to
   $\cos n\theta$).
4. Remove the surplus function with the Pythagorean identity, so that one is left.

Step 4 is compulsory: without it the answer contains both sines and cosines, while
what is wanted is usually in terms of one function.
""")

md(r"""
## Task 11 🔴 — the identity for sin 5θ

Using de Moivre's theorem, show that

$$\sin 5\theta \equiv 16\sin^5\theta - 20\sin^3\theta + 5\sin\theta.$$

Enter below the **imaginary part** of the binomial expansion of
$(\cos\theta + i\sin\theta)^5$ — that is, the expression in $\sin\theta$ and
$\cos\theta$ before the Pythagorean identity is used. The check will confirm that the
step is right.

*Source: November 2023 TZ2, Paper 1, Q12(b) (6 marks, no calculator).*
""")

code(r"""
# the imaginary part of (cos θ + i sin θ)^5, in terms of sin and cos
my_imag = ...

verify_identity('Task 11, the step', my_imag,
                im(expand((cos(theta) + I*sin(theta))**5)), var=theta)
verify_identity('Task 11, the identity', my_imag,
                16*sin(theta)**5 - 20*sin(theta)**3 + 5*sin(theta), var=theta)
""")

md(r"""
## Task 12 🟡 — an exact tangent through an argument

Express $\tan\dfrac{\pi}{12}$ in the form $p + q\sqrt3$, where $p, q \in \mathbb{Z}$.

The way through complex numbers: take a number whose argument is $\frac{\pi}{12}$ —
for example the quotient of two numbers with known arguments — put it into Cartesian
form and take the ratio of the imaginary part to the real part.

Enter the value of $\tan\frac{\pi}{12}$ itself, as an exact expression.

*Source: November 2025 TZ1, Paper 1, Q11(e) (5 marks, no calculator).*
""")

code(r"""
my_tan = ...             # the exact value

check_expr('Task 12', my_tan, '""" + D_11 + r"""')
""")

md(r"""
---
## Theory 6. Multiplication as a motion of the plane

The last reading of the formula. Multiplication by $re^{i\alpha}$ is a **rotation
through $\alpha$ and a stretch by a factor of $r$** about the origin. The special
cases are worth remembering:

| Multiplying by | What it does |
| --- | --- |
| $i$ | a rotation through $\frac{\pi}{2}$ anticlockwise |
| $-1$ | a rotation through $\pi$, that is, a point reflection in the origin |
| $e^{i\alpha}$ | a pure rotation through $\alpha$, the size is kept |
| $r > 0$ | a pure stretch, the direction is kept |

From this come the geometric questions that would otherwise need coordinate
drudgery.

**The canonical storyline.** The points $O$, $Z_1$, $Z_2$ form a **right-angled
isosceles** triangle with the right angle at the origin. What does that mean in the
language of complex numbers? The legs $OZ_1$ and $OZ_2$ are equal, so
$|z_1| = |z_2|$; the angle between them is right, so the arguments differ by
$\frac{\pi}{2}$. Together:

$$z_1 = i\,z_2 .$$

One equality instead of all the geometry — and everything else follows by algebra.
That is how **any** condition about the shape of a triangle translates: equal sides
give equal moduli, the angle between them gives the difference of the arguments, and
the two together give the factor $re^{i\alpha}$ that takes one vertex to the other.
Which factor exactly is decided by the angle in the question.
""")

md(r"""
---
## Trainer: name the technique

| Code | Technique |
| --- | --- |
| `power` | raise to a power with de Moivre |
| `root` | take an $n$-th root |
| `unity` | roots of unity, a regular polygon |
| `period` | the smallest $n$ from a condition on the argument |
| `rot` | a rotation, a geometric transformation |
| `ident` | a trigonometric identity via de Moivre |
| `geom` | the geometry of a figure on the Argand plane |

1. «Show that $(1+i\sqrt3)^8 + (1-i\sqrt3)^8 = -256$»
2. «The smallest $n$ for which $u^n$ is real»
3. «The smallest $n$ for which $z^n = -i$»
4. «Describe the transformation taking $z$ to $z^{10}$»
5. «Find both square roots of $\sqrt3 + i$»
6. «Solve $z^2 = -1 - \sqrt3 i$»
7. «Find the three cube roots of $z_2/z_1$»
8. «Write down the other two roots of $z^3 = -8$»
9. «Rotate $U$, $V$, $W$ through $\pi/4$»
10. «Find the smallest $n$ for which all six points solve $z^n = a$»
11. «Show that $\sin 5\theta \equiv 16\sin^5\theta - \ldots$»
12. «$OZ_1Z_2$ is equilateral. Express $z_1$ in terms of $z_2$»
13. «Show that $(1 + i\tan\theta)^4 + (1 - i\tan\theta)^4 = \dfrac{2\cos 4\theta}{\cos^4\theta}$»
14. «Prove that $1 + \omega + \omega^2 = 0$»
15. «Evaluate $\left(2e^{i\pi/6}\right)^{12}$»

The target is 15 out of 15 in under two minutes.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '',
    9: '', 10: '', 11: '', 12: '', 13: '', 14: '', 15: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## Task 13 🔴 — ON THE TIMER: 10 minutes

Close everything above. Paper 1 format, no calculator, 6 marks.

Given $z_1 = r_1e^{i\alpha}$ and $z_2 = r_2e^{i\theta}$. The points $Z_1$, $O$,
$Z_2$ form an equilateral triangle, with $0 < \alpha - \theta < \pi$.

**(i)** Express $z_1$ in terms of $z_2$.
**(ii)** Hence show that $z_1^2 + z_2^2 = z_1z_2$.

The check below takes the key identity of part (ii): enter the value of
$e^{2i\pi/3} + 1$ in its simplest form. If that is right, the whole derivation goes
through.

*Source: May 2022 TZ2, Paper 1, Q12(c) (6 marks, no calculator).*
""")

code(r"""
# set a timer for 10 minutes
# the key step: what does exp(2*I*pi/3) + 1 equal?
my_key = ...

check_complex('Task 13, the key step', my_key, '""" + dz(sp.exp(2 * I * P / 3) + 1) + r"""')

# and the check of the sum of the roots of unity, on which it all rests
my_omega_sum = ...       # 1 + omega + omega^2 for omega = exp(2*I*pi/3)

check_complex('Task 13, the sum of the roots', my_omega_sum, '""" + D_SUM + r"""')
""")

md(r"""
### Attempt log

| Question | Answer |
| --- | --- |
| Did you finish inside 10 minutes? | |
| How did you write down «equilateral»? | |
| Did you notice that $e^{2i\pi/3} + 1 = e^{i\pi/3}$? | |
| Where did the time go? | |

The condition $0 < \alpha - \theta < \pi$ is not there for nothing: without it the
rotation could go the other way, and instead of $e^{i\pi/3}$ you would get
$e^{-i\pi/3}$. The triangle would be the same, but the sign in the working
different.
""")

md(r"""
---
# 🔑 Solutions
""")

md(r"""
## Solution 1 — a large power without the binomial theorem

$1 + i\sqrt3$: modulus $\sqrt{1+3} = 2$, argument $\frac{\pi}{3}$ (first quadrant).
By de Moivre:

$$(1 + i\sqrt3)^8 = 2^8 e^{8i\pi/3} = 256\,e^{8i\pi/3}.$$

Bring the argument in: $\frac{8\pi}{3} - 2\pi = \frac{2\pi}{3}$.

The second term is the conjugate of the first, so the sum equals twice the real
part:

$$2 \cdot 256\cos\frac{2\pi}{3} = 512 \cdot \left(-\frac12\right) = -256.$$

```python
my_value = 2 * 256 * cos(2*pi/3)
```
""")

md(r"""
## Solution 2 — when the power becomes real

$u = -1 + \sqrt3 i = 2e^{2\pi i/3}$ (see A5, task 3).

$$u^n = 2^n e^{2n\pi i/3}.$$

It is real when $\frac{2n\pi}{3} = k\pi$, that is, when $\frac{2n}{3}$ is an
integer, that is, when $n$ is a multiple of 3. The smallest positive integer is
$n = 3$.

$$u^3 = 2^3 e^{2\pi i} = 8.$$

```python
my_n = 3
my_un = 8
```

A check without de Moivre: $(-1+\sqrt3 i)^3$ should give 8, and that also explains
the find from A5 — the numbers $2, -1\pm\sqrt3 i$ are the cube roots of 8.
""")

md(r"""
## Solution 3 — and now exactly −i

$\arg z = \frac{11\pi}{18}$, modulus 1. The condition $z^n = -i$ means

$$\frac{11\pi n}{18} = -\frac{\pi}{2} + 2\pi k
\;\Longrightarrow\; \frac{11n}{18} = -\frac12 + 2k
\;\Longrightarrow\; 11n = -9 + 36k.$$

Go through the $k$: at $k=1$ we get $11n = 27$, not divisible; at $k=2$,
$11n = 63$, no; at $k=3$, $11n = 99$, so $n = 9$.

```python
my_n3 = 9
```

Check: $\frac{11\pi \cdot 9}{18} = \frac{11\pi}{2}$, subtract $4\pi$ to get
$\frac{3\pi}{2}$, and $\cos\frac{3\pi}{2} + i\sin\frac{3\pi}{2} = -i$ ✓.

Here the difference from task 2 shows: there any multiple of $\pi$ would do and the
answer came out at once; here there is only one value, and it had to be searched
for.
""")

md(r"""
## Solution 4 — a power as a transformation

$$\arg(z^{10}) = 10 \cdot \frac{11\pi}{18} = \frac{110\pi}{18} = \frac{55\pi}{9}.$$

Bring it into $(-\pi, \pi]$ by subtracting $2\pi = \frac{18\pi}{9}$ three times:

$$\frac{55\pi}{9} - \frac{54\pi}{9} = \frac{\pi}{9}.$$

The modulus is $1^{10} = 1$, that is, unchanged. So the transformation is a
**rotation about the origin through $\frac{\pi}{9}$ anticlockwise.**

```python
my_rotation = pi/9
```
""")

md(r"""
## Solution 5 — the square roots

$w = \sqrt3 + i = 2e^{i\pi/6}$ (see A5, task 5).

$$z_k = 2^{1/2}\,e^{i(\pi/6 + 2\pi k)/2}, \qquad k = 0, 1.$$

At $k = 0$: $\sqrt2\,e^{i\pi/12}$.
At $k = 1$: $\sqrt2\,e^{i(\pi/6 + 2\pi)/2} = \sqrt2\,e^{13i\pi/12}$, and bringing it
into the interval: $\frac{13\pi}{12} - 2\pi = -\frac{11\pi}{12}$.

$$z \in \left\{\sqrt2\,e^{i\pi/12},\ \sqrt2\,e^{-11i\pi/12}\right\}.$$

```python
my_sqrt_w = [sqrt(2)*exp(I*pi/12), sqrt(2)*exp(-11*I*pi/12)]
```

Two square roots are always opposite: their arguments differ by exactly $\pi$, and
on the picture that is a diameter.
""")

md(r"""
## Solution 6 — roots in polar form

$-1 - \sqrt3 i$ is in the **third** quadrant: modulus 2, acute angle
$\arctan\sqrt3 = \frac{\pi}{3}$, argument $\frac{\pi}{3} - \pi = -\frac{2\pi}{3}$.

$$z_k = \sqrt2\,e^{i(-2\pi/3 + 2\pi k)/2}.$$

At $k = 0$: $\sqrt2\,e^{-i\pi/3}$.
At $k = 1$: $\sqrt2\,e^{i(-2\pi/3 + 2\pi)/2} = \sqrt2\,e^{2i\pi/3}$.

$$z = \sqrt2\left(\cos\frac{-\pi}{3} + i\sin\frac{-\pi}{3}\right)
\quad\text{and}\quad
\sqrt2\left(\cos\frac{2\pi}{3} + i\sin\frac{2\pi}{3}\right).$$

```python
my_roots6 = [sqrt(2)*exp(-I*pi/3), sqrt(2)*exp(2*I*pi/3)]
```
""")

md(r"""
## Solution 7 — the quotient first, the root second

$z_1 = 3 - 3i = 3\sqrt2\,e^{-i\pi/4}$, $z_2 = 2\sqrt3\,e^{5i\pi/6}$.

Divide — the moduli divide, the arguments subtract:

$$\frac{z_2}{z_1} = \frac{2\sqrt3}{3\sqrt2}\,
e^{i\left(\frac{5\pi}{6} + \frac{\pi}{4}\right)}
= \frac{\sqrt6}{3}\,e^{13i\pi/12}.$$

Bring the argument in: $\frac{13\pi}{12} - 2\pi = -\frac{11\pi}{12}$.

Take the cube root:

$$z_k = \left(\frac{\sqrt6}{3}\right)^{1/3}
e^{i\left(-\frac{11\pi}{12} + 2\pi k\right)/3}, \qquad k = 0, 1, 2,$$

that is, the arguments $-\frac{11\pi}{36}$, $\frac{13\pi}{36}$ and
$-\frac{35\pi}{36}$ (the last one after bringing it in).

```python
r = (sqrt(6)/3)**Rational(1, 3)
my_cube_roots = [r*exp(-11*I*pi/36), r*exp(13*I*pi/36), r*exp(-35*I*pi/36)]
```

Check: neighbouring arguments differ by $\frac{2\pi}{3} = \frac{24\pi}{36}$ ✓.
""")

md(r"""
## Solution 8 — the other roots of a cube

The roots divide the circle into three equal parts, with step $\frac{2\pi}{3}$. The
modulus of each is $|{-8}|^{1/3} = 2$.

The given $u = 1 + \sqrt3 i$ has argument $\frac{\pi}{3}$. Add the step:

$$\frac{\pi}{3} + \frac{2\pi}{3} = \pi \;\Longrightarrow\; 2e^{i\pi} = -2,$$

$$\pi + \frac{2\pi}{3} = \frac{5\pi}{3} \equiv -\frac{\pi}{3}
\;\Longrightarrow\; 2e^{-i\pi/3} = 1 - \sqrt3 i.$$

```python
my_others = [-2, 1 - sqrt(3)*I]
```

The short way: the coefficients are real, so the conjugate of $u$ is a root too,
which gives $1 - \sqrt3 i$ straight away; and the third one has to be real, and from
the product of the roots it is $-2$.
""")

md(r"""
## Solution 9 — rotating the whole picture

A rotation through $\frac{\pi}{4}$ is multiplication by $e^{i\pi/4}$. The moduli do
not change (all equal 2), the arguments shift:

$$\frac{\pi}{3} \to \frac{\pi}{3} + \frac{\pi}{4} = \frac{7\pi}{12}, \qquad
\pi \to \pi + \frac{\pi}{4} = \frac{5\pi}{4} \equiv -\frac{3\pi}{4}, \qquad
-\frac{\pi}{3} \to -\frac{\pi}{12}.$$

$$u' = 2e^{7i\pi/12}, \quad v' = 2e^{-3i\pi/4}, \quad w' = 2e^{-i\pi/12}.$$

```python
my_rotated = [2*exp(7*I*pi/12), 2*exp(-3*I*pi/4), 2*exp(-I*pi/12)]
```

Note the second one: $\frac{5\pi}{4}$ falls outside $(-\pi, \pi]$, and it must be
brought in by subtracting $2\pi$. The answer being in the required interval is worth
a mark of its own.
""")

md(r"""
## Solution 10 — one equation for six points

All six numbers have modulus 2, so an equation $z^n = a$ with $|a| = 2^n$ suits any
$n$ as far as the modulus goes. Only the argument does any work.

Write all six arguments in twelfths of $\pi$:

$$\frac{4\pi}{12},\quad \frac{12\pi}{12},\quad -\frac{4\pi}{12},
\qquad \frac{7\pi}{12},\quad -\frac{9\pi}{12},\quad -\frac{\pi}{12}.$$

The numerators are $4,\ 12,\ -4,\ 7,\ -9,\ -1$ — every argument is a multiple of
$\frac{\pi}{12}$.

The solutions of $z^n = a$ form a regular $n$-gon with step $\frac{2\pi}{n}$, so the
step has to divide **all the pairwise differences** of the arguments. The differences
of these six numbers give, for example, $12 - 7 = 5$ and $7 - 4 = 3$; the greatest
common divisor of all the differences is 1, so the step is $\frac{\pi}{12}$ and
nothing smaller will do.

$$\frac{2\pi}{n} = \frac{\pi}{12} \;\Longrightarrow\; n = 24.$$

```python
my_n10 = 24
```
""")

md(r"""
## Solution 11 — the identity for sin 5θ

Expand $(\cos\theta + i\sin\theta)^5$ by the binomial theorem, writing
$c = \cos\theta$, $s = \sin\theta$:

$$c^5 + 5c^4(is) + 10c^3(is)^2 + 10c^2(is)^3 + 5c(is)^4 + (is)^5.$$

The powers of the imaginary unit: $i^2 = -1$, $i^3 = -i$, $i^4 = 1$, $i^5 = i$. The
imaginary part is collected from the odd terms:

$$\operatorname{Im} = 5c^4s - 10c^2s^3 + s^5.$$

By de Moivre this same imaginary part equals $\sin 5\theta$. What is left is to
remove the cosines with the Pythagorean identity $c^2 = 1 - s^2$:

$$5(1-s^2)^2 s - 10(1-s^2)s^3 + s^5
= 5s(1 - 2s^2 + s^4) - 10s^3 + 10s^5 + s^5,$$

$$= 5s - 10s^3 + 5s^5 - 10s^3 + 10s^5 + s^5
= 16s^5 - 20s^3 + 5s.$$

```python
my_imag = 5*cos(theta)**4*sin(theta) - 10*cos(theta)**2*sin(theta)**3 + sin(theta)**5
```

Step 4 is compulsory: without the substitution $c^2 = 1 - s^2$ the answer contains
both functions, while what is wanted is in terms of the sine.
""")

md(r"""
## Solution 12 — an exact tangent through an argument

The angle needed is $\frac{\pi}{12} = \frac{\pi}{3} - \frac{\pi}{4}$. Take the
quotient of two numbers with those arguments, for example

$$\frac{1 + i\sqrt3}{1 + i}, \qquad
\arg = \frac{\pi}{3} - \frac{\pi}{4} = \frac{\pi}{12}.$$

Put it into Cartesian form by multiplying by the conjugate of the denominator:

$$\frac{(1 + i\sqrt3)(1 - i)}{2}
= \frac{1 - i + i\sqrt3 + \sqrt3}{2}
= \frac{(1 + \sqrt3) + i(\sqrt3 - 1)}{2}.$$

The tangent of the argument is the ratio of the imaginary part to the real part:

$$\tan\frac{\pi}{12} = \frac{\sqrt3 - 1}{\sqrt3 + 1}
= \frac{(\sqrt3-1)^2}{(\sqrt3+1)(\sqrt3-1)}
= \frac{4 - 2\sqrt3}{2} = 2 - \sqrt3.$$

```python
my_tan = 2 - sqrt(3)
```

So $p = 2$, $q = -1$. Check: $2 - \sqrt3 \approx 0.268$, and
$\tan 15^\circ \approx 0.268$ ✓.
""")

md(r"""
## Solution 13 — the task on the timer

**(i)** The triangle $Z_1OZ_2$ is equilateral, so the sides out of $O$ are equal:
$r_1 = r_2$. The angle between them is $\frac{\pi}{3}$, and the condition
$0 < \alpha - \theta < \pi$ says that $Z_1$ is rotated anticlockwise relative to
$Z_2$. So

$$\frac{z_1}{z_2} = e^{i\pi/3} \;\Longrightarrow\; z_1 = z_2 e^{i\pi/3}.$$

**(ii)** Substitute:

$$z_1^2 + z_2^2 = z_2^2 e^{2i\pi/3} + z_2^2 = z_2^2\left(e^{2i\pi/3} + 1\right).$$

The key step is noticing that

$$e^{2i\pi/3} + 1 = \left(-\frac12 + \frac{\sqrt3}{2}i\right) + 1
= \frac12 + \frac{\sqrt3}{2}i = e^{i\pi/3}.$$

Then

$$z_1^2 + z_2^2 = z_2^2 e^{i\pi/3} = z_2 \cdot \left(z_2 e^{i\pi/3}\right)
= z_2 z_1.$$

```python
my_key = exp(I*pi/3)          # the same as exp(2*I*pi/3) + 1
my_omega_sum = 0              # 1 + omega + omega^2
```

Where that equality comes from: the numbers $1$, $e^{2i\pi/3}$, $e^{-2i\pi/3}$ are
the roots of unity and their sum is zero. So
$1 + e^{2i\pi/3} = -e^{-2i\pi/3} = e^{i\pi/3}$, because changing the sign is a
rotation through $\pi$. The same fact as in the theory about the roots of unity.
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = os.path.join(ROOT, 'practicum/number_algebra',
                   'practicum-a6-de-moivre.ipynb')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
print(f'cells: {len(cells)} -> {out}')
