"""Собирает практикум C1 (треугольник) в формате .ipynb."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig

sq = sp.sqrt
R = sp.Rational
x, y, t, u = sp.symbols('x y t u')
a, b, c, d, h, p, q, s = sp.symbols('a b c d h p q s')
alpha, beta, theta = sp.symbols('alpha beta theta')


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_c1.py ---
D_R1 = dn(18.2 / math.tan(math.radians(58)) - 5, 3)
D_V1 = dn(math.pi * (18.2 / math.tan(math.radians(58)) - 5)**2 * 20 / 3, 3)
D_ANG2 = dn(math.degrees(math.atan(math.sqrt(29) / (5 * math.sqrt(2) / 2))), 3)
D_JDL3 = dn(99, 3)
D_H6 = dn(150 * math.sin(math.radians((180 - math.degrees(
    math.acos((150**2 + 90**2 - 154**2) / (2 * 150 * 90)))) / 2)), 3)
D_P10 = dn(7 + 12 + 6.050684854040104, 3)
D_P15, D_Q15 = dn(25), dn(7)
D_MAX17 = dn(19.5959, 3)

TRIGGER = {1: 'cos', 2: 'area', 3: 'right', 4: 'ambig', 5: 'sin',
           6: 'exact', 7: 'view', 8: 'model', 9: 'cos', 10: 'area',
           11: 'right', 12: 'sin', 13: 'exact', 14: 'ambig', 15: 'model'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

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
# Practicum C1: the triangle

**116 marks, 39 blocks, eight techniques.** The oldest topic on the syllabus and the
only one where almost everything is done with two formulas — but the choice between
them has to be made in every question.

**Material.** 39 blocks and 116 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**The main idea of the topic.** A side length or an angle means nothing on its own:
the answer here is a **triangle**, and the number found is only one part of it.
Hence the two consequences the practicum is built around.

First: the formula is chosen by **what is given**, not by what is wanted. Three
sides, or two sides and the angle between them — the cosine rule. A side opposite a
known angle — the sine rule. Two sides and the angle between them — the area.

Second: sometimes the data are not enough for one triangle. Two sides and the angle
opposite the smaller of them define **two** different triangles, and both are real.
Which one is meant is decided by the question, not by the algebra.

**How to work**

1. Read the map of techniques and keep it beside you: half the mistakes in the topic
   are correct arithmetic with the wrong formula.
2. **Draw.** In the archive nearly every question comes with a diagram, and the ones
   that do not require a diagram to be built. That is the first move, and the one
   most often skipped.
3. Enter angles **in degrees** unless the question says otherwise; in the checks
   `deg=False` switches to radians.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + solve_triangle, sqrt, pi

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d = symbols('a b c d')
alpha, beta, theta = symbols('alpha beta theta')
h, p, q, s = symbols('h p q s')

print('ready; sympy', sp.__version__)
# The sides a, b, c are opposite the angles A, B, C — as in every IB formula.
for tri in solve_triangle(b=12, c=7, A=116):
    print('from two sides and the angle between them:',
          {k: round(v, 3) for k, v in sorted(tri.items())})
print('how many triangles a = 7, b = 12, A = 25 degrees gives:',
      len(solve_triangle(a=7, b=12, A=25)))
""")

md(r"""
---
## Map of techniques

| # | Technique | What is given | First move |
| --- | --- | --- | --- |
| 1 | A right-angled triangle | a right angle in the diagram | $\sin,\cos,\tan$ and their inverses |
| 2 | From a description to a diagram | directions, angles of elevation, «bearing» | draw it and label every known part |
| 3 | The cosine rule | three sides, or two sides and the angle **between** them | $a^2 = b^2+c^2-2bc\cos A$ |
| 4 | The sine rule | a side opposite a known angle | $\dfrac{a}{\sin A} = \dfrac{b}{\sin B}$ |
| 5 | The ambiguous case | two sides and the angle opposite the **smaller** one | find both angles: $\theta$ and $180^\circ-\theta$ |
| 6 | Area | two sides and the angle between them | $S = \tfrac12 ab\sin C$ |
| 7 | Exact values | Paper 1, «exact value», «in the form $p\sqrt q$» | $\sin^2+\cos^2=1$, do not evaluate the radicals |
| 8 | A triangle with a letter | «show that …», the area as a function | express the sides through the letter and substitute |

The ladder goes by **what is given**. Techniques 1–2 are about getting a triangle at
all: out of a right angle in the diagram or out of a description in words.
Techniques 3–5 are the two main formulas and the case where their data are not
enough for one answer. Techniques 6–8 work with a triangle that is already there:
the area, the exact form, a letter instead of a number.

**How to choose between the cosine and the sine rule.** There is one rule, and it is
about the data, not about the question:

* you see **three sides** or **two sides and the angle between them** — the cosine
  rule;
* you see **a side and the angle opposite it** — the sine rule;
* you see neither — look for a second triangle in the diagram.

**What saves the most time.** Labelling everything known on the diagram before
choosing a formula. The rule above is read straight off the diagram in a couple of
seconds, and without a diagram it cannot be read at all.
""")

md(r"""
---
## Theory 1. The right-angled triangle

Three ratios and their three inverses — that is the whole technique:

$$\sin\theta = \frac{\text{opposite}}{\text{hypotenuse}},\quad
\cos\theta = \frac{\text{adjacent}}{\text{hypotenuse}},\quad
\tan\theta = \frac{\text{opposite}}{\text{adjacent}}.$$

Plus Pythagoras. In the archive this technique is almost never a whole question: it
turns up **inside** problems about solids and models, and the work consists of
finding the right-angled triangle in the diagram.

**Where it hides in three dimensions.** Three places worth knowing by heart:

| What is wanted | Which triangle |
| --- | --- |
| the diagonal of a square base of side $s$ | right-angled with legs $s$ and $s$: the diagonal is $s\sqrt2$ |
| the angle between a lateral edge and the base | the height of the pyramid and **half** the diagonal |
| the height of an equilateral triangle of side $s$ | legs $\frac s2$ and $h$: $h = \frac{s\sqrt3}{2}$ |

**Careful with the half.** The most frequent mistake in pyramid questions is taking
the whole diagonal of the base instead of half of it. The angle then comes out
smaller than the real one, and you can check yourself with an estimate: if the
height is comparable with half the diagonal, the angle should be around
$45^\circ$.
""")

md(r"""
## Task 1 🟢 — an angle of elevation and a cone

A monument is in the shape of a right cone of height 20 m. Oliver stands 5 m from
the base of the monument, his eyes are 1.8 m above the ground, and the angle of
elevation from eye level to the vertex of the cone is $58^\circ$.

**(a)** Find the radius of the base of the cone.

**(b)** Find the volume of the monument.

The answers to three significant figures.

*Source: May 2024 TZ1, Paper 2, Q2 (3 + 2 marks, calculator).*
""")

code(r"""
my1_r = ...              # the radius of the base, m
my1_v = ...              # the volume of the monument, m^3

check_num('Task 1(a)', my1_r, 3, '""" + D_R1 + r"""')
check_num('Task 1(b)', my1_v, 3, '""" + D_V1 + r"""')
""")

md(r"""
## Task 2 🟢 — a triangle inside a pyramid

A right pyramid with square base $ABCD$ has apex $V(1,\ 7,\ 0)$; the point
$X(-3,\ 4,\ 2)$ is the centre of the base. The side of the base is 5 cm.

**(a)** Find $VX$ — as an exact value.

**(b)** Find $AC$ — as an exact value.

**(c)** Find the angle between the edge $[VC]$ and the plane of the base (three
significant figures).

*Source: May 2025 TZ2, Paper 2, Q2 (2 + 2 + 2 marks, calculator).*
""")

code(r"""
my2_vx = ...             # VX, exactly
my2_ac = ...             # AC, exactly
my2_angle = ...          # the angle between [VC] and the base, degrees

verify_exact('Task 2(a)', my2_vx, sqrt(29))
verify_exact('Task 2(b)', my2_ac, 5*sqrt(2))
check_num('Task 2(c)', my2_angle, 3, '""" + D_ANG2 + r"""')
""")

md(r"""
---
## Theory 2. From a description to a diagram

Half the questions in the topic arrive as text rather than a picture: «bearing
$127^\circ$», «angle of elevation», «40 km to the west». The technique consists of
turning the description into a triangle with its parts labelled.

**Bearings.** Measured always **from north, clockwise**, with three digits:
$127^\circ$, $270^\circ$. Hence the conversion rules:

* east is $090^\circ$, north is $000^\circ$;
* the angle between a bearing $\theta$ and the direction due east is
  $90^\circ - \theta$;
* the reverse bearing differs by $180^\circ$.

**Angles of elevation and depression.** An angle of elevation is measured from the
**horizontal upwards**, an angle of depression from the horizontal downwards. Both
always sit in a right-angled triangle one of whose legs is vertical. The observer's
eye level is subtracted from the height of the object: you do not look from the
ground.

**What must be drawn.** North as an arrow, every known length, every known angle,
and a question mark where the answer is. After that the angle sum of the triangle
usually gives the missing angle in one line.
""")

md(r"""
## Task 3 🟡 — bearings and the sine rule

The cities of Lucknow ($L$), Jaipur ($J$) and Delhi ($D$). Lucknow is 500 km due
east of Jaipur, the bearing of Delhi from Jaipur is $034^\circ$, and the angle
$J\hat{L}D$ is $25^\circ$.

**(a)** Find the angle $J\hat{D}L$.

**(b)** Find the distance $DL$ (three significant figures).

The check for part (b) builds the triangle from **your** angle from (a) — exactly
like follow through in the marking: a mistake in (a) is not punished twice, but it
is not fixed either.

*Source: May 2023 TZ1, Paper 2, Q1 (2 + 3 marks, calculator).*
""")

code(r"""
my3_angle = ...          # the angle JDL, degrees
my3_dl = ...             # the distance DL, km

check_num('Task 3(a)', my3_angle, 3, '""" + D_JDL3 + r"""')
verify_triangle('Task 3(b)', {'a': my3_dl}, B=25, C=my3_angle, c=500)
""")

md(r"""
---
## Theory 3. The cosine rule

$$a^2 = b^2 + c^2 - 2bc\cos A, \qquad
\cos A = \frac{b^2+c^2-a^2}{2bc}.$$

The sides $a$, $b$, $c$ are opposite the angles $A$, $B$, $C$ — that convention
holds in every IB formula, and confusing it costs more than any arithmetic
slip.

**Two cases, and both are about what is given.**

| Given | What is found | How |
| --- | --- | --- |
| two sides and the angle **between** them (SAS) | the third side | the first formula |
| three sides (SSS) | any angle | the second formula |

**The key word is «between».** If the known angle does **not** lie between the known
sides, the cosine rule still works but turns into a quadratic in the unknown side —
and that can have two positive roots. That is the ambiguous case, technique 5.

**An obtuse angle shows in the sign.** If $\cos A$ comes out negative, the angle is
obtuse, and that is not an error: `arccos` returns a value above $90^\circ$ by
itself. But if **two** angles of the triangle come out obtuse, there is certainly a
mistake.

**A five-second check.** The larger angle is opposite the larger side. Look at the
diagram: if the longest side has come out opposite the smallest angle, there is no
point computing further.
""")

md(r"""
## Task 4 🟢 — the third side

In triangle $ABC$: $AB = 7$, $AC = 12$, $B\hat{A}C = 116^\circ$. Find $BC$.

*Source: May 2025 TZ3, Paper 2, Q1(a) (3 marks, calculator).*
""")

code(r"""
my4 = ...                # BC

verify_triangle('Task 4', {'a': my4}, b=12, c=7, A=116)
""")

md(r"""
## Task 5 🟢 — an angle from three sides

The same triangle: $AB = 7$, $AC = 12$, $B\hat{A}C = 116^\circ$. Find the angle
$A\hat{C}B$ (three significant figures).

*Source: May 2025 TZ3, Paper 2, Q1(b) (3 marks, calculator).*
""")

code(r"""
my5 = ...                # the angle ACB, degrees

verify_triangle('Task 5', {'C': my5}, b=12, c=7, A=116)
""")

md(r"""
## Task 6 🟡 — two buildings

Two buildings stand on horizontal ground. From a point $P$ on the ground between
them the angle of elevation to the top of each building is the same and equals
$\theta$. The distance from $P$ to the top $A$ of the tall building is 150 m, to the
top $B$ of the short one 90 m, and the distance $AB$ is 154 m.

**(a)** Find the angle $A\hat{P}B$ (three significant figures).

**(b)** Find the height $h$ of the tall building (three significant figures).

The second part is shorter than the first if you notice what the three angles at the
point $P$ on a straight line add up to.

*Source: May 2023 TZ2, Paper 2, Q2 (6 marks, calculator).*
""")

code(r"""
my6_apb = ...            # the angle APB, degrees
my6_h = ...              # the height h, m

verify_triangle('Task 6(a)', {'A': my6_apb}, a=154, b=90, c=150)
check_num('Task 6(b)', my6_h, 3, '""" + D_H6 + r"""')
""")

md(r"""
## Task 7 🔴 — one diagonal, two triangles

A quadrilateral $ABCD$ has $AB = 2$, $BC = 4$, $CD = 6$, $DA = 8$. Write
$\alpha = A\hat{B}C$ and $\beta = A\hat{D}C$.

The diagonal $AC$ belongs to both triangles, $ABC$ and $ADC$. Express its length
through $\alpha$, then through $\beta$, and show that

$$\alpha = \arccos(6\cos\beta - 5).$$

Enter what $\cos\alpha$ equals — an expression in $\beta$.

*Source: November 2022, Paper 2, Q9(a) (4 marks, calculator).*
""")

code(r"""
my7 = ...                # cos alpha in terms of beta

verify_identity('Task 7', my7, 6*cos(beta) - 5, var=beta,
                samples=(0.2, 0.4, 0.6, 0.8))
""")

md(r"""
---
## Theory 4. The sine rule

$$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R.$$

It works when **a side together with the angle opposite it** is known — that pair is
the key to everything else.

**What applying it looks like.** Exactly two of the fractions are taken out of the
proportion, not all three: one with a known numerator and denominator, the other
with a single unknown. From there it is a linear equation.

**The angle sum is part of the technique.** Often two angles and one side are known;
the third angle comes from subtracting from $180^\circ$, and only then does the
proportion work. There is no separate mark for that step in the exam, but without it
nothing comes out.

**Careful: `arcsin` returns an acute angle.** If the sine rule is used to find an
**angle** rather than a side, the equation $\sin B = k$ has two solutions in the
range of a triangle: $B$ and $180^\circ - B$. The calculator shows only the first.
When the second one works too — that is technique 5.

**When hunting an angle is safe.** If it is opposite the smaller of two known sides,
it cannot be obtuse, and `arcsin` gives the only answer. Opposite the larger side —
you have to think.
""")

md(r"""
## Task 8 🔴 — an exact answer through the sine rule

In triangle $PQR$: $PR = 5$ cm, $Q\hat{P}R = 45^\circ$, $P\hat{R}Q = 60^\circ$.

Find $QR$, giving the answer in the form $p(\sqrt q - 1)$ cm, where
$p, q \in \mathbb{Q}$.

You will need the exact value $\sin 75^\circ = \dfrac{\sqrt6+\sqrt2}{4}$ and the
clearing of the surd from the denominator.

*Source: May 2025 TZ1, Paper 1, Q11(c)(ii) (part of a 7-mark question, no
calculator).*
""")

code(r"""
my8 = ...                # QR, as an exact value

verify_exact('Task 8', my8, 5*sqrt(3) - 5)
""")

md(r"""
## Task 9 🟡 — the sine rule in a model

A sprinkler stands at a point $S$ and waters a circle of radius 20 m. The point $S$
is 14 m from the edge of a path running north to south; the edge of the path meets
the circle at the points $A$ and $B$.

The sprinkler makes one turn in 16 seconds, that is, it rotates $\frac\pi8$ radians
per second. At time $t$ the water crosses the edge of the path at a point $D$ which
is $d$ metres south of $A$. Write $\alpha = A\hat{S}D = \frac{\pi t}{8}$ and
$\beta = S\hat{A}B = 0.7754$ radians.

Using the sine rule in the triangle $ASD$, show that

$$d(t) = \frac{20\sin\frac{\pi t}{8}}{\sin\left(2.37 - \frac{\pi t}{8}\right)}.$$

Enter an expression for the third angle of the triangle, $A\hat{D}S$, in radians —
the denominator comes out of it.

*Source: May 2024 TZ2, Paper 2, Q11(e) (3 marks, calculator).*
""")

code(r"""
my9 = ...                # the angle ADS in radians, in terms of t

verify_identity('Task 9', my9, pi - 0.7754 - pi*t/8, var=t,
                samples=(0.5, 1.5, 2.5, 3.5))
""")

md(r"""
---
## Theory 5. The ambiguous case

The only place in the topic where the answer is **not one** triangle.

Two sides and the angle opposite one of them are given (the SSA case). The sine rule
gives $\sin B = \dfrac{b\sin A}{a}$, and that equation has two solutions in
$(0^\circ, 180^\circ)$:

$$B_1 = \arcsin\frac{b\sin A}{a}, \qquad B_2 = 180^\circ - B_1.$$

Both are valid if $A + B < 180^\circ$. Then there are two triangles, and they are
different: in one $B$ is acute, in the other obtuse.

**When there are not two options.**

| Condition | How many triangles |
| --- | --- |
| $\dfrac{b\sin A}{a} > 1$ | none |
| $a \ge b$ (the angle is opposite the larger side) | one |
| $A \ge 90^\circ$ | one |
| otherwise | **two** |

**How it sounds in a question.** The words «smallest possible», «the largest
possible», «find all possible values» are a direct signal: there are several options
and the question is about the choice. If there are no such words and the data still
give two triangles, the diagram in the question usually shows the one meant.

**What the check does with this.** `solve_triangle` returns a **list**; if it has
two elements, `verify_triangle` says so directly and will not decide for you which
one was meant.
""")

md(r"""
## Task 10 🔴 — the smallest perimeter

In triangle $ABC$: $AC = 12$, $CB = 7$, $B\hat{A}C = 25^\circ$.

**(a)** Find both possible lengths of the side $AB$ (three significant figures).

**(b)** Find the smallest possible perimeter of the triangle $ABC$ (three
significant figures).

*Source: November 2021, Paper 2, Q2 (5 marks, calculator).*
""")

code(r"""
my10_ab = [..., ...]     # both possible lengths of AB
my10_p = ...             # the smallest perimeter

verify_triangle('Task 10, the first', {'c': my10_ab[0]}, a=7, b=12, A=25)
verify_triangle('Task 10, the second', {'c': my10_ab[1]}, a=7, b=12, A=25)
check_num('Task 10(b)', my10_p, 3, '""" + D_P10 + r"""')
""")

md(r"""
---
## Theory 6. Area

$$S = \frac12 ab\sin C.$$

The angle is taken **between** the sides $a$ and $b$ — as in the cosine rule, and
for the same reason: the formula comes from $\frac12 \cdot$ base $\cdot$ height,
where the height is $a\sin C$.

**When the formula is not needed.** If the triangle is right-angled, the area is
easier as half the product of the legs, and on the coordinate plane as half the
product of a base and a height read straight off the axes. Both ways turn up in the
archive more often than the formula itself.

**A triangle on an Argand diagram is the same triangle.** The vertices $2+i$, $-1$,
$2-i$ are the points $(2,1)$, $(-1,0)$, $(2,-1)$: the base is vertical and equals
$2$, the height is horizontal and equals $3$, and the area is computed in your head.
Convert the complex numbers into coordinates **before** reaching for formulas: half
of such questions, once converted, are solved with no trigonometric function at
all.

**The reverse question.** The area is given and a side is wanted — the equation
$\frac12 ab\sin C = S$ is linear in either of the sides, and that is the most
frequent way of asking about area on Paper 1.
""")

md(r"""
## Task 11 🟢 — the area from two sides and a cosine

In triangle $ABC$: $AB = 6$ cm, $AC = 10$ cm, $\cos B\hat{A}C = \frac15$.

Find the area of triangle $ABC$ — as an exact value.

*Source: November 2023 TZ1, Paper 1, Q4 (6 marks, no calculator; the same question
appears in TZ2).*
""")

code(r"""
my11 = ...               # the area of ABC, exactly

verify_exact('Task 11', my11, 12*sqrt(6))
""")

md(r"""
## Task 12 🟡 — a triangle on an Argand diagram

The points $u = 1+\sqrt3 i$, $v = -2$, $w = 1-\sqrt3 i$ are marked on an Argand
diagram. Find the area of the triangle $UVW$ — as an exact value.

*Source: May 2024 TZ1, Paper 1, Q12(d) (3 marks, no calculator).*
""")

code(r"""
my12 = ...               # the area of UVW, exactly

verify_exact('Task 12', my12, 3*sqrt(3))
""")

md(r"""
## Task 13 🟡 — an area with a letter

Let $a > 1$.

**(a)** Show that
$a^2 + \left(\dfrac{a^2-1}{2}\right)^2 = \left(\dfrac{a^2+1}{2}\right)^2$. Enter the
left-hand side — that is the whole work of the part.

**(b)** A right-angled triangle has sides $a$, $\dfrac{a^2-1}{2}$ and
$\dfrac{a^2+1}{2}$. Find its area as an expression in $a$.

Part (a) shows at once which of the three sides is the hypotenuse.

*Source: November 2022, Paper 1, Q3 (3 + 2 marks, no calculator).*
""")

code(r"""
my13_sq = ...            # the left-hand side of the identity from (a)
my13_area = ...          # the area in terms of a

verify_identity('Task 13(a)', my13_sq, ((a**2 + 1)/2)**2, var=a,
                samples=(1.5, 2, 3, 5))
verify_identity('Task 13(b)', my13_area, a*(a**2 - 1)/4, var=a,
                samples=(1.5, 2, 3, 5))
""")

md(r"""
## Task 14 🟡 — a quadrilateral on the coordinate plane

A quadrilateral $OABC$ is symmetric about the diagonal $[OB]$, with $A(6, 0)$ and
$C(3, 3\sqrt3)$.

**(a)** Find the equation of the line $OB$ — an expression for $y$ in terms of $x$.

**(b)** Given that $[OA]$ is perpendicular to $[AB]$, find the area of the
quadrilateral $OABC$ — as an exact value.

The symmetry works twice here: it gives the direction of $OB$ and it splits the
quadrilateral into two equal triangles.

*Source: May 2024 TZ2, Paper 1, Q3 (4 + 3 marks, no calculator).*
""")

code(r"""
my14_line = ...          # y in terms of x for the line OB
my14_area = ...          # the area of OABC, exactly

verify_identity('Task 14(a)', my14_line, x/sqrt(3), var=x)
verify_exact('Task 14(b)', my14_area, 12*sqrt(3))
""")

md(r"""
---
## Theory 7. Exact values

On Paper 1 there is no calculator and the answer is asked for exactly: «find the
exact value», «give your answer in the form $\frac{p\sqrt q}{2}$». That is a
requirement on the **writing**: 29.4 instead of $12\sqrt6$ earns no mark.

**The sine from the cosine.** The main tool of the topic:

$$\sin^2\theta + \cos^2\theta = 1 \ \Longrightarrow\
\sin\theta = \pm\sqrt{1-\cos^2\theta}.$$

In a triangle the sign takes care of itself: any angle of a triangle lies between
$0^\circ$ and $180^\circ$, and there the sine is **positive**. This is the rare case
where a $\pm$ does not turn into a case analysis.

**What to do with surds.**

* $\sqrt{a}\cdot\sqrt{b} = \sqrt{ab}$ — multiply under the root rather than
  evaluate;
* $\dfrac{1}{\sqrt3} = \dfrac{\sqrt3}{3}$ — clear the surd from the denominator;
* $\dfrac{1}{\sqrt5+\sqrt3}$ — multiply by the conjugate $\sqrt5-\sqrt3$; the
  denominator becomes a difference of squares and turns into $2$.

**The form of the answer is part of the task.** «In the form $p\sqrt q$, where
$p, q \in \mathbb{Z}^+$» means that $q$ has to be reduced to its square-free form:
$5\sqrt{175}$ formally equals $25\sqrt7$, but it is written wrongly.
""")

md(r"""
## Task 15 🔴 — the area in a given form

In triangle $ABC$: $AB = 10$, $BC = x$, $AC = 2x$ and $\cos \hat{C} = \frac34$.

Find the area of the triangle in the form $\dfrac{p\sqrt q}{2}$, where
$p, q \in \mathbb{Z}^+$.

The first move is the cosine rule in $x$: the angle $C$ lies between the sides $BC$
and $AC$, and opposite it lies the known side $AB$.

*Source: May 2021 TZ2, Paper 1, Q6 (7 marks, no calculator).*
""")

code(r"""
my15_p = ...             # p
my15_q = ...             # q

check_num('Task 15, p', my15_p, 6, '""" + D_P15 + r"""')
check_num('Task 15, q', my15_q, 6, '""" + D_Q15 + r"""')
""")

md(r"""
---
## Theory 8. A triangle with a letter

The last technique of the topic: there are no longer sides and angles as numbers,
there are expressions. Three formats, and all three appear in the archive.

**«Show that».** The triangle is expressed through a parameter and brought to the
printed form. The work is the same as in B1: the marks are for the road, not for the
answer. It is worth remembering that such parts almost always involve the angle sum
— it gives the third angle through the first two.

**The area as a function.** Build an expression for the area in terms of one
parameter and find the maximum. On Paper 2 the maximum is found on the GDC, and that
is the only place in the topic where a calculator is genuinely needed.

**A difference of arctangents.** The classic «angle of view» construction: two rays
are drawn from the point of observation — to the far end of a strip and to the near
one — each lying in its own right-angled triangle with a common vertical leg, and
the angle wanted is the **difference** of two arctangents. All the work is in naming
the two legs correctly: the common leg is the same in both triangles, while the
other legs differ by the length of the strip.

**The general rule.** Before building an expression, give exactly one quantity a
letter. If two letters end up in the expression, a relation between them has been
lost somewhere — most often the angle sum or the cosine rule for the common side.
""")

md(r"""
## Task 16 🟡 — an angle of view

An aeroplane $P$ flies at a constant height of 6 km above horizontal ground and
approaches a runway $[AB]$ of length 2 km. The point $G$ is the projection of the
aeroplane onto the ground; when $GA = x$ km, the angle of view of the runway
$A\hat{P}B$ equals $\theta$.

Show that

$$\theta = \arctan\left(\frac{x+2}{6}\right) - \arctan\left(\frac x6\right).$$

Enter an expression for $\theta$.

*Source: May 2025 TZ3, Paper 2, Q9(a) (2 marks, calculator).*
""")

code(r"""
my16 = ...               # theta in terms of x

verify_identity('Task 16', my16,
                atan((x + 2)/6) - atan(x/6), var=x,
                samples=(0.5, 1, 2, 4))
""")

md(r"""
## Task 17 🔴 — the largest area of a quadrilateral

A continuation of task 7: the quadrilateral $ABCD$ with sides $AB = 2$, $BC = 4$,
$CD = 6$, $DA = 8$, where $\alpha = A\hat{B}C$, $\beta = A\hat{D}C$ and
$\cos\alpha = 6\cos\beta - 5$.

**(a)** Find the largest possible area of the quadrilateral $ABCD$ (three
significant figures).

**(b)** The same maximum can be written exactly. Enter its exact value.

A hint for the second part: look at what $\alpha+\beta$ equals at the maximum.

*Source: November 2022, Paper 2, Q9(b) (4 marks, calculator).*
""")

code(r"""
my17_max = ...           # the largest area, three significant figures
my17_exact = ...         # the same thing, exactly

check_num('Task 17(a)', my17_max, 3, '""" + D_MAX17 + r"""')
verify_exact('Task 17(b)', my17_exact, 8*sqrt(6))
""")

md(r"""
## Task 18 🟡 — a «show that» from a diagram

A narrow corridor of width $\frac34$ m meets a room of width 6 m at right angles; at
the point $C$ is the inner corner. The points $A$ and $B$ lie at the feet of the
walls so that $A$, $C$ and $B$ are collinear. Let $L = AB$, and let $\alpha$ be the
angle $[AB]$ makes with the wall of the room, where $0 < \alpha < \frac\pi2$.

Show that

$$L = \frac34\sec\alpha + 6\operatorname{cosec}\alpha.$$

The segment $[AB]$ is split by $C$ into two pieces, and each lies in its own
right-angled triangle: in one the adjacent leg is $\frac34$, in the other the
opposite leg is 6.

Enter an expression for $L$ using only $\sin$ and $\cos$.

*Source: May 2023 TZ1, Paper 1, Q11(a) (2 marks, no calculator).*
""")

code(r"""
my18 = ...               # L in terms of sin and cos

verify_identity('Task 18', my18,
                Rational(3, 4)/cos(alpha) + 6/sin(alpha), var=alpha,
                samples=(0.4, 0.8, 1.2, 1.5))
""")

md(r"""
---
## Trainer: name the technique in five seconds

Below are fifteen statements with no solutions. For each one write the code of the
technique — and nothing else. Nothing has to be computed; the aim is for the first
move to be found before the computing starts.

The codes: `right` (a right-angled triangle) · `view` (from a description to a
diagram) · `cos` (the cosine rule) · `sin` (the sine rule) · `ambig` (the ambiguous
case) · `area` (area) · `exact` (exact values) · `model` (a triangle with a letter)

1. In a triangle $a = 5$, $b = 7$, $C = 40^\circ$. Find $c$.
2. Find the area of a triangle with sides 6 and 9 and the angle $50^\circ$ between them.
3. A ladder 4 m long leans at $70^\circ$ to the ground. How high is its top?
4. In a triangle $a = 8$, $b = 11$, $A = 32^\circ$. Find all the possible $B$.
5. In a triangle $A = 40^\circ$, $B = 65^\circ$, $a = 12$. Find $b$.
6. Given $\cos\theta = \frac13$, find the exact value of $\sin\theta$, where $\theta$ is an angle of a triangle.
7. A ship sails on a bearing of $120^\circ$ for 30 km, then on $210^\circ$ for another 40 km. How far is it from the start?
8. The area of a triangle with sides $x$ and $x+2$ and the angle $30^\circ$ between them is 6. Find $x$.
9. In a triangle $a = 4$, $b = 6$, $c = 9$. Find the largest angle.
10. The diagonals of a rhombus are 10 and 24. Find its area.
11. The angle between the diagonal of a cube of edge 1 and its base.
12. In a triangle $B = 50^\circ$, $C = 70^\circ$, $c = 15$. Find $a$.
13. Find the exact value of the area of a triangle with sides 4, 4 and the angle $60^\circ$.
14. In a triangle $a = 9$, $b = 12$, $A = 35^\circ$. How many such triangles are there?
15. The area of a triangle with $AB = x$, $AC = 10 - x$ and the angle $60^\circ$ between them — for which $x$ is it largest?
""")

code(r"""
answers = {
    1: '',   2: '',   3: '',   4: '',   5: '',
    6: '',   7: '',   8: '',   9: '',  10: '',
   11: '',  12: '',  13: '',  14: '',  15: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + r""")
""")

md(r"""
---
## Task 19 🔴 — on the timer, 10 minutes

A whole Paper 1 question with no calculator. Seven marks, target time about 10
minutes.

In triangle $ABC$: $AB = 5$, $BC = 6\sqrt2$, $A\hat{C}B = \theta$ and
$B\hat{A}C = 2\theta$, where $0 < \theta < \frac\pi2$.

**(a)** Using the sine rule, show that $\cos\theta = \dfrac{3\sqrt2}{5}$. Enter an
expression for $BC$ in terms of $\cos\theta$ from which that follows. [3]

**(b)** Find $\sin\theta$ — as an exact value. [2]

**(c)** The point $D$ lies on $[AC]$ so that the area of triangle $BCD$ is
$2\sqrt{14}$. Find $DC$ — as an exact value. [2]

*Source: May 2025 TZ2, Paper 1, Q3 (3 + 2 + 2 marks, no calculator).*
""")

code(r"""
my19_bc = ...            # BC in terms of cos theta
my19_sin = ...           # sin theta, exactly
my19_dc = ...            # DC, exactly

verify_identity('Task 19(a)', my19_bc, 10*cos(theta), var=theta,
                samples=(0.3, 0.5, 0.7, 0.9))
verify_exact('Task 19(b)', my19_sin, sqrt(7)/5)
verify_exact('Task 19(c)', my19_dc, Rational(10, 3))
""")

md(r"""
---
# Solutions

Below is a full working of every task with the markscheme's marking. Open them after
you have solved on your own: the working explains not only the answer but what
exactly the marks are given for.
""")

md(r"""
## Solution 1 — an angle of elevation and a cone

Oliver's eyes are at a height of 1.8 m and the vertex of the cone at 20 m, so the
vertical leg equals $20 - 1.8 = 18.2$. The horizontal leg is the distance from his
eyes to the **axis** of the cone, that is, $5 + r$:

$$\tan 58^\circ = \frac{18.2}{5+r} \iff 5+r = \frac{18.2}{\tan58^\circ}
= 11.37\ldots$$

Hence $r = 6.372\ldots \approx 6.37$ m.

**(b)** The volume of a cone:

$$V = \frac13\pi r^2 h = \frac13\pi (6.3726)^2 \cdot 20
= 850.5\ldots \approx 851\ \text{m}^3.$$

```python
my1_r = 6.3726
my1_v = 850.54
```

**The marking.** (a): M1 for the right trigonometric equation, A1 for $11.4$ (or
equivalent), A1 for $6.37$. (b): M1 for substituting into the volume formula, A1 for
851.

**Two traps, both about the diagram.** The first: taking the vertical leg to be 20
and forgetting the observer's height. The second: taking the horizontal leg to be 5
— but 5 metres is to the **base** of the cone, while the angle of elevation looks at
the vertex, which stands above the centre.

**About rounding.** In (b) the unrounded radius has to be substituted: with
$r = 6.37$ you get $850.0$, and that is already a different third significant
figure. The same storyline as in B1 with the tortoise question.
""")

md(r"""
## Solution 2 — a triangle inside a pyramid

**(a)** $VX$ is the distance between two points:

$$VX = \sqrt{(1+3)^2 + (7-4)^2 + (0-2)^2} = \sqrt{16+9+4} = \sqrt{29}.$$

**(b)** The diagonal of a square of side 5:

$$AC = 5\sqrt2.$$

**(c)** The angle between the edge $[VC]$ and the base is the angle $V\hat{C}X$ in
the right-angled triangle $VXC$, where $VX$ is vertical and
$XC = \frac{AC}{2} = \frac{5\sqrt2}{2}$:

$$\tan(V\hat{C}X) = \frac{VX}{XC} = \frac{\sqrt{29}}{\frac{5\sqrt2}{2}}
= 1.523\ldots \ \Longrightarrow\ V\hat{C}X = 56.7^\circ.$$

```python
my2_vx = sqrt(29)
my2_ac = 5*sqrt(2)
my2_angle = 56.714
```

**The marking.** (a): M1 for the distance formula, A1 for $\sqrt{29}$. (b): M1 for
Pythagoras or for $5\sqrt2$, A1. (c): M1 for the right triangle, A1 for
$56.7^\circ$.

**Half the diagonal.** The most frequent mistake of the topic in three dimensions:
taking the whole of $AC$. That gives $46.9^\circ$ — an answer that looks plausible,
and the mistake can only be spotted on the diagram: $X$ is the **centre** of the
base, not a vertex of the square.

**Why an exact value.** In (a) and (b) the question does not ask for rounding, and
$\sqrt{29}$ is a finished answer. The check takes that requirement literally:
`verify_exact` will not accept 5.39.
""")

md(r"""
## Solution 3 — bearings and the sine rule

**(a)** The bearing $034^\circ$ is measured from north clockwise, and Lucknow lies
due east, that is, on the bearing $090^\circ$. So

$$D\hat{J}L = 90^\circ - 34^\circ = 56^\circ,$$

and by the angle sum of the triangle

$$J\hat{D}L = 180^\circ - 56^\circ - 25^\circ = 99^\circ.$$

**(b)** The sine rule: the side $DL$ is opposite the angle $J$, the side
$JL = 500$ is opposite the angle $D$:

$$\frac{DL}{\sin 56^\circ} = \frac{500}{\sin 99^\circ}
\ \Longrightarrow\ DL = \frac{500\sin56^\circ}{\sin99^\circ}
= 419.7 \approx 420\ \text{km}.$$

```python
my3_angle = 99
my3_dl = 419.69
```

**The marking.** (a): M1 for $56^\circ$ (or for using the bearing correctly), A1 for
$99^\circ$. (b): M1 for the sine rule, A1 for the substitution, A1 for 420.

**Where the mark goes in (a).** Taking $34^\circ$ as an angle of the triangle. A
bearing is measured from **north**, while the side $JL$ runs east — there is a right
angle between them, and the subtraction is compulsory.

**A plausibility check.** Opposite the largest angle ($99^\circ$) lies the longest
side, which is $JL = 500$. Our answer $DL = 420$ is less than 500, which agrees.
""")

md(r"""
## Solution 4 — the third side

The angle $A$ lies between the sides $AB$ and $AC$, so the cosine rule works:

$$BC^2 = AB^2 + AC^2 - 2\cdot AB\cdot AC\cos A
= 49 + 144 - 168\cos116^\circ.$$

The cosine of an obtuse angle is negative, so the third term is **added**:

$$BC^2 = 193 + 168\cdot0.4384 = 266.6\ldots
\ \Longrightarrow\ BC = 16.3.$$

```python
my4 = 16.329
```

**The marking.** M1 for the cosine rule, A1 for the right substitution, A1 for
16.3.

**The minus is in the formula, not in the answer.** The formula is always written
with a minus: $-2bc\cos A$. When $A$ is obtuse the cosine is itself negative, and
minus times minus gives plus. Trying to «fix the sign» by hand is a reliable way of
getting $BC = 8.5$ instead of 16.3.

**An estimate.** The obtuse angle is opposite the longest side, and the sides 7 and
12 are shorter than 16.3 — it agrees.
""")

md(r"""
## Solution 5 — an angle from the data of the same triangle

The sine rule is easiest: the angle $C$ is opposite the side $AB = 7$ and the angle
$A = 116^\circ$ is opposite $BC = 16.33$:

$$\frac{\sin C}{7} = \frac{\sin 116^\circ}{16.33}
\ \Longrightarrow\ \sin C = 0.3855\ldots
\ \Longrightarrow\ C = 22.7^\circ.$$

```python
my5 = 22.662
```

**The marking.** M1 for the sine rule (or the cosine rule), A1 for the right
substitution, A1 for $22.7^\circ$.

**Here `arcsin` is safe.** The angle $C$ is opposite the side 7 — not the longest
one, so it cannot be obtuse, and the second root
$180^\circ - 22.7^\circ = 157.3^\circ$ falls away by itself: with the known
$116^\circ$ the sum would exceed $180^\circ$.

**The second route.** The cosine rule on three sides gives the same answer and does
not need the value found in (a). In the exam that is useful: a mistake in (a) would
not drag (b) down with it. But the rounded $BC$ has to be substituted, so the sine
route is more accurate.
""")

md(r"""
## Solution 6 — two buildings

**(a)** In the triangle $APB$ all three sides are known: $PA = 150$, $PB = 90$,
$AB = 154$. By the cosine rule

$$\cos(A\hat{P}B) = \frac{150^2+90^2-154^2}{2\cdot150\cdot90}
= \frac{6884}{27000} = 0.2549\ldots
\ \Longrightarrow\ A\hat{P}B = 75.2^\circ.$$

**(b)** The point $P$ lies on a straight line between the buildings, and the three
angles there make a straight angle:

$$\theta + A\hat{P}B + \theta = 180^\circ
\ \Longrightarrow\ \theta = \frac{180^\circ - 75.23^\circ}{2}
= 52.39^\circ.$$

Then the tall building gives a right-angled triangle with hypotenuse $PA = 150$:

$$h = 150\sin\theta = 118.8 \approx 119\ \text{m}.$$

```python
my6_apb = 75.229
my6_h = 118.82
```

**The marking.** M1 for the cosine rule, A1 for $75.2^\circ$, M1 for finding
$\theta$, A1 for $52.4^\circ$, M1 for $h = 150\sin\theta$, A1 for 119.

**The key to the whole question is one line.** The angles of elevation to both
buildings are equal, and both are measured from the same horizontal at the same
point. So together with $A\hat{P}B$ they make $180^\circ$. Without that observation
the question cannot be solved at all; with it the rest takes two lines.

**What to check at the end.** $h = 119$ with a hypotenuse of 150 is plausible
($\sin52^\circ \approx 0.79$). The short building would come out as
$90\sin\theta = 71.3$ m, and it really is lower.
""")

md(r"""
## Solution 7 — one diagonal, two triangles

The diagonal $AC$ belongs to both triangles, so its square can be written twice. In
the triangle $ABC$ the angle $\alpha$ lies between the sides 2 and 4:

$$AC^2 = 2^2+4^2-2\cdot2\cdot4\cos\alpha = 20-16\cos\alpha.$$

In the triangle $ADC$ the angle $\beta$ lies between the sides 6 and 8:

$$AC^2 = 6^2+8^2-2\cdot6\cdot8\cos\beta = 100-96\cos\beta.$$

Equate them:

$$20-16\cos\alpha = 100-96\cos\beta
\iff 16\cos\alpha = 96\cos\beta - 80
\iff \cos\alpha = 6\cos\beta - 5,$$

that is, $\alpha = \arccos(6\cos\beta-5)$. $\blacksquare$

```python
my7 = 6*cos(beta) - 5
```

**The marking.** A1 for the first expression, A1 for the second, M1 for equating
them, A1 for the required relation.

**A technique worth remembering.** A side shared by two triangles is an equation. In
exactly the same way B1 found the intersections of two curves: one quantity written
two ways gives a relation between the parameters.

**A side consequence.** From $\cos\alpha = 6\cos\beta-5$ it is clear that
$\cos\beta \ge \frac23$: otherwise the left-hand side would leave $[-1,1]$. That is,
$\beta \le 48.2^\circ$, and that restriction will be needed in task 17.
""")

md(r"""
## Solution 8 — an exact answer through the sine rule

The third angle: $P\hat{Q}R = 180^\circ - 45^\circ - 60^\circ = 75^\circ$. The side
$QR$ is opposite the angle $P = 45^\circ$, the side $PR = 5$ is opposite the angle
$Q = 75^\circ$:

$$\frac{QR}{\sin45^\circ} = \frac{5}{\sin75^\circ}
\ \Longrightarrow\ QR = \frac{5\sin45^\circ}{\sin75^\circ}
= \frac{5\cdot\frac{\sqrt2}{2}}{\frac{\sqrt6+\sqrt2}{4}}
= \frac{10\sqrt2}{\sqrt6+\sqrt2}.$$

Multiply by the conjugate:

$$QR = \frac{10\sqrt2(\sqrt6-\sqrt2)}{(\sqrt6+\sqrt2)(\sqrt6-\sqrt2)}
= \frac{10\sqrt{12}-20}{4} = \frac{20\sqrt3-20}{4} = 5(\sqrt3-1).$$

```python
my8 = 5*(sqrt(3) - 1)
```

**The marking.** M1 for the sine rule, A1 for substituting the exact
$\sin75^\circ$, M1 for multiplying by the conjugate, A1 for the answer in the
required form.

**Where the solution breaks.** At $\frac{10\sqrt2}{\sqrt6+\sqrt2}$. What is needed
next is one technique — the conjugate — and without it the answer stays in a form
the markscheme does not accept: the demand «in the form $p(\sqrt q-1)$» is a demand
on the writing.

**A check by size.** $5(\sqrt3-1) = 3.66$, while $PR = 5$. Opposite the smaller
angle ($45^\circ$ against $60^\circ$) lies the smaller side — it agrees.
""")

md(r"""
## Solution 9 — the sine rule in a model

In the triangle $ASD$ two angles are known:
$\alpha = A\hat{S}D = \frac{\pi t}{8}$ and $\beta = S\hat{A}D = 0.7754$. The third
comes from the angle sum:

$$A\hat{D}S = \pi - 0.7754 - \frac{\pi t}{8}
= 2.3662 - \frac{\pi t}{8} \approx 2.37 - \frac{\pi t}{8}.$$

The side $AD = d$ is opposite the angle $\alpha$, the side $SA = 20$ is opposite the
angle $A\hat{D}S$:

$$\frac{d}{\sin\frac{\pi t}{8}} = \frac{20}{\sin\left(2.37-\frac{\pi t}{8}\right)}
\ \Longrightarrow\
d(t) = \frac{20\sin\frac{\pi t}{8}}{\sin\left(2.37-\frac{\pi t}{8}\right)}.
\qquad \blacksquare$$

```python
my9 = pi - 0.7754 - pi*t/8
```

**The marking.** M1 for the third angle, M1 for the sine rule, A1 for the required
form.

**A familiar model.** This is the very $d(t)$ that B1 (task 13) solved numerically,
hunting for the moment the water meets the tortoise. It also emerged there that
around $t = 6.04$ it has a discontinuity: the denominator vanishes. Now it is clear
where that comes from — the angle $A\hat{D}S$ becomes zero there, and there is no
triangle any more.

**About the rounded constant.** $\pi - 0.7754 = 2.3662$, while the question has
$2.37$. The model in the exam is rounded, and that is normal; but it is exactly why
the position of the discontinuity in B1 was computed approximately.
""")

md(r"""
## Solution 10 — the smallest perimeter

We are given $a = CB = 7$, $b = AC = 12$ and the angle $A = 25^\circ$, which is
opposite the side $a$. The smaller side opposite the known angle — the ambiguous
case.

By the sine rule:

$$\sin B = \frac{b\sin A}{a} = \frac{12\sin25^\circ}{7} = 0.7243\ldots$$

Hence **two** values:

$$B_1 = 46.43^\circ, \qquad B_2 = 180^\circ - 46.43^\circ = 133.57^\circ.$$

Both work: $25^\circ + B < 180^\circ$ in either case. The third angle and the third
side:

$$C_1 = 108.57^\circ,\ AB_1 = \frac{7\sin C_1}{\sin25^\circ} = 15.70;
\qquad
C_2 = 21.43^\circ,\ AB_2 = 6.051.$$

The perimeters: $7+12+15.70 = 34.70$ and $7+12+6.051 = 25.05$. So

$$P_{\min} = 25.1.$$

```python
my10_ab = [15.701, 6.0507]
my10_p = 25.051
```

**The marking.** M1 for the sine or cosine rule, A1 for the first value, M1 for
realising that there are two solutions, A1 for the second value, A1 for the smallest
perimeter.

**The second route — a quadratic.** The cosine rule in $AB$:
$7^2 = 12^2 + AB^2 - 24\,AB\cos25^\circ$. That is a quadratic with two positive
roots, 15.70 and 6.051 — the same two triangles obtained with no `arcsin` at all.
Many people discover the ambiguity exactly that way, by seeing two roots.

**Why the smaller perimeter goes with the obtuse $B$.** The angle $B$ is opposite
$AC = 12$, and that side is fixed. An obtuse $B$ «presses» the third vertex in, and
the side $AB$ comes out shorter — 6.05 against 15.70.

**The words to watch for.** «Smallest possible», «all possible values», «find the
two possible» are a direct indication that there are two triangles. If there are no
such words and the ambiguity is there anyway, the diagram suggests the choice.
""")

md(r"""
## Solution 11 — the area from two sides and a cosine

The sine of an angle of a triangle is always positive, so the sign is settled with
no case analysis:

$$\sin A = \sqrt{1-\cos^2 A} = \sqrt{1-\tfrac{1}{25}}
= \sqrt{\tfrac{24}{25}} = \frac{2\sqrt6}{5}.$$

Then the area formula:

$$S = \frac12\cdot 6\cdot 10\cdot\frac{2\sqrt6}{5} = 12\sqrt6.$$

```python
my11 = 12*sqrt(6)
```

**The marking.** M1 for using $\sin^2+\cos^2=1$, A1 for $\frac{2\sqrt6}{5}$, M1 for
the area formula, A1 for the substitution, A1A1 for simplifying to $12\sqrt6$.

**Why no $\pm$.** An angle of a triangle lies in $(0^\circ,180^\circ)$, and there
the sine is positive. This is the only place in the syllabus where $\sin^2 = k$
implies a single answer with no reservations — and it is worth knowing, because in
trigonometric equations (C3) it is the other way round.

**The second route.** Drop the height from $B$ onto $AC$: $\cos A = \frac15$ gives
$AH = 6\cdot\frac15 = 1.2$, then $BH = \sqrt{36-1.44}$, and the area is
$\frac12\cdot10\cdot BH$. The same answer, but the surds are uglier — the markscheme
accepts it and it takes longer.

**About exactness.** $12\sqrt6 = 29.39$, and on Paper 1 such an answer is not
accepted: the question asks for the exact value. The check behaves the same way.
""")

md(r"""
## Solution 12 — a triangle on an Argand diagram

The points: $U(1,\sqrt3)$, $V(-2,0)$, $W(1,-\sqrt3)$. The side $UW$ is vertical
(both have abscissa 1), and its length is

$$UW = \sqrt3 - (-\sqrt3) = 2\sqrt3.$$

The height from $V$ to the line $x=1$ is horizontal and equals $1-(-2) = 3$. So

$$S = \frac12\cdot 2\sqrt3\cdot 3 = 3\sqrt3.$$

```python
my12 = 3*sqrt(3)
```

**The marking.** M1 for finding the base or the height, A1 for the other one, A1 for
$3\sqrt3$.

**The formula $\frac12 ab\sin C$ is surplus here.** It would work — the angle at $V$
is $60^\circ$ and $UV = VW = 2\sqrt3$ — but there would be more to compute. The sign
that it is not the one needed: two vertices have the same abscissa, that is, the base
is already parallel to an axis.

**The complex numbers here are only decoration.** An Argand diagram is an ordinary
coordinate plane, and a triangle on it is an ordinary triangle. Worth noticing: a
question from the complex-numbers section is solved with a technique from the
triangle section.
""")

md(r"""
## Solution 13 — an area with a letter

**(a)** Expand the left-hand side:

$$a^2 + \left(\frac{a^2-1}{2}\right)^2
= a^2 + \frac{a^4-2a^2+1}{4}
= \frac{4a^2 + a^4 - 2a^2 + 1}{4}
= \frac{a^4+2a^2+1}{4} = \left(\frac{a^2+1}{2}\right)^2.
\qquad \blacksquare$$

**(b)** The identity from (a) is Pythagoras for the set
$\left(a,\ \frac{a^2-1}{2},\ \frac{a^2+1}{2}\right)$: on the left the sum of the
squares of two sides, on the right the square of the third. So the hypotenuse is
$\frac{a^2+1}{2}$ and the legs are $a$ and $\frac{a^2-1}{2}$. The area of a
right-angled triangle is half the product of the legs:

$$S = \frac12\cdot a\cdot\frac{a^2-1}{2} = \frac{a(a^2-1)}{4}.$$

```python
my13_sq = a**2 + ((a**2 - 1)/2)**2
my13_area = a*(a**2 - 1)/4
```

**The marking.** (a): M1 for attempting to expand, A1 for the right expansion, A1 —
AG. (b): M1 for the right legs, A1 for the expression.

**Part (a) is itself the hint for (b).** It is not saying «check the algebra» but
«here are the two sides that are the legs». Noticing that is worth two marks:
without part (a) you would have to compare three expressions with one another.

**What this triple is.** At $a = 3$ the sides are $3$, $4$, $5$; at $a = 5$ — $5$,
$12$, $13$. That is the general form of the Pythagorean triples with an odd leg, and
both triples have already appeared in practicum B1 in the question about a triangle
whose area equals its perimeter.

**About the writing.** The answer $\frac{a^3-a}{4}$ is the same thing, and the check
accepts both forms: there is no requirement on the writing here, only on the value.
""")

md(r"""
## Solution 14 — a quadrilateral on the coordinate plane

**(a)** Symmetry about $[OB]$ means that $[OB]$ is the perpendicular bisector of
$[AC]$; in particular, $OB$ passes through the midpoint of $[AC]$:

$$M = \left(\frac{6+3}{2},\ \frac{0+3\sqrt3}{2}\right)
= \left(\frac92,\ \frac{3\sqrt3}{2}\right).$$

The line through the origin and $M$:

$$k = \frac{3\sqrt3/2}{9/2} = \frac{\sqrt3}{3} = \frac{1}{\sqrt3},
\qquad y = \frac{x}{\sqrt3}.$$

**(b)** $[OA]$ lies on the $x$-axis and $[AB]$ is perpendicular to it — so $AB$ is
vertical, and the point $B$ has abscissa 6. Then
$B\left(6,\ 6\cdot\frac{1}{\sqrt3}\right) = B(6,\ 2\sqrt3)$.

The diagonal $[OB]$ splits the quadrilateral into two equal triangles (the
symmetry), so

$$S = 2\cdot S_{OAB} = 2\cdot\frac12\cdot 6\cdot 2\sqrt3 = 12\sqrt3.$$

```python
my14_line = x/sqrt(3)
my14_area = 12*sqrt(3)
```

**The marking.** (a): A1 for the midpoint, M1 for the gradient, A1A1 for the
equation. (b): M1 for finding $B$, M1 for using the symmetry, A1 for $12\sqrt3$.

**The symmetry works twice.** First it gives the direction of $OB$ (through the
midpoint of $[AC]$), then it halves the quadrilateral. Both times it saves
computation, and both times there is an M1 for it.

**A check through an angle.** The gradient $\frac{1}{\sqrt3}$ is $30^\circ$, and the
point $C(3,3\sqrt3)$ lies at $60^\circ$. The bisector of the angle $AOC$ does run at
$30^\circ$ — the symmetry agrees.
""")

md(r"""
## Solution 15 — the area in a given form

The angle $C$ lies between the sides $BC = x$ and $AC = 2x$, and opposite it is the
side $AB = 10$. The cosine rule:

$$100 = x^2 + (2x)^2 - 2\cdot x\cdot 2x\cdot\frac34
= x^2 + 4x^2 - 3x^2 = 2x^2.$$

Hence $x^2 = 50$, that is, $x = 5\sqrt2$.

The sine of the angle $C$ is positive:

$$\sin C = \sqrt{1-\tfrac{9}{16}} = \frac{\sqrt7}{4}.$$

The area:

$$S = \frac12\cdot x\cdot 2x\cdot\sin C = x^2\cdot\frac{\sqrt7}{4}
= 50\cdot\frac{\sqrt7}{4} = \frac{25\sqrt7}{2}.$$

So $p = 25$, $q = 7$.

```python
my15_p = 25
my15_q = 7
```

**The marking.** M1 for the cosine rule, A1 for $2x^2 = 100$, A1 for
$x = 5\sqrt2$, M1 for $\sin C$, A1 for $\frac{\sqrt7}{4}$, M1 for the area formula,
A1 for $\frac{25\sqrt7}{2}$.

**The beauty is in the cancellation.** $x^2+4x^2-3x^2 = 2x^2$ — three terms collapse
into one, and the root comes out «nice». That is a sign that the question was built
for an exact answer: if something bulky is left after the substitution, the angle has
most likely been confused.

**$x$ itself does not go into the answer.** The area depends on $x^2$, and we know
that straight away — 50. Taking the root was not necessary; in the exam that saves a
line and protects against a sign error.

**About the form $\frac{p\sqrt q}{2}$.** The writing $\frac{5\sqrt{175}}{2}$ equals
the same number, but $q$ has to be square-free: $175 = 25\cdot7$. The requirement
«$p,q\in\mathbb{Z}^+$» implies the reduced form.
""")

md(r"""
## Solution 16 — an angle of view

The point $G$ lies below the aeroplane, and $PG = 6$ is the common leg of two
right-angled triangles. The far end of the runway is $x + 2$ from $G$, the near one
$x$:

$$\tan(G\hat{P}B) = \frac{x+2}{6}, \qquad
\tan(G\hat{P}A) = \frac{x}{6}.$$

The angle of view is the difference:

$$\theta = A\hat{P}B = G\hat{P}B - G\hat{P}A
= \arctan\left(\frac{x+2}{6}\right) - \arctan\left(\frac x6\right).
\qquad \blacksquare$$

```python
my16 = atan((x + 2)/6) - atan(x/6)
```

**The marking.** M1 for both arctangents (or for one with an indication that the
other is the same), A1 for the difference.

**Why a difference and not a sum.** Both triangles lie on the same side of the
vertical $PG$, and the smaller angle is «subtracted» from the larger. If the runway
lay on both sides of the point $G$, it would be a sum — and that is the first thing
to check on the diagram.

**Where this leads.** In the original the question goes on to the derivative
$\frac{d\theta}{dt}$ and the speed of the aeroplane: the «angle of view»
construction is a standard entry into related-rates problems (E9).
""")

md(r"""
## Solution 17 — the largest area of a quadrilateral

The area is the sum of the areas of two triangles:

$$S = \frac12\cdot2\cdot4\sin\alpha + \frac12\cdot6\cdot8\sin\beta
= 4\sin\alpha + 24\sin\beta.$$

From task 7 we know $\cos\alpha = 6\cos\beta - 5$, that is,
$\alpha = \arccos(6\cos\beta-5)$. Substituting gives a function of one variable:

$$S(\beta) = 4\sin\big(\arccos(6\cos\beta-5)\big) + 24\sin\beta,$$

where $\cos\beta \ge \frac23$, that is, $0 < \beta \le 48.2^\circ$. The maximum on
the GDC:

$$S_{\max} = 19.5959\ldots \approx 19.6
\quad\text{at}\quad \beta = 44.4^\circ,\ \alpha = 135.6^\circ.$$

**(b)** Notice: $\alpha + \beta = 180^\circ$ to every figure. The quadrilateral with
the largest area for given sides is the **cyclic** one, and for it Brahmagupta's
formula works:

$$S = \sqrt{(s-a)(s-b)(s-c)(s-d)}, \qquad
s = \frac{2+4+6+8}{2} = 10,$$
$$S = \sqrt{8\cdot6\cdot4\cdot2} = \sqrt{384} = 8\sqrt6.$$

And $8\sqrt6 = 19.5959\ldots$ — the same number.

```python
my17_max = 19.5959
my17_exact = 8*sqrt(6)
```

**The marking.** M1 for expressing the area through the two triangles, M1 for
substituting the relation from (a), A1 for the function of one variable, A1 for
19.6.

**The exam asks only for 19.6.** Brahmagupta's formula is not on the AA HL
syllabus, and part (b) has been added here by the practicum. The point is that the
numerical answer can then be checked independently: the agreement of $19.5959$ and
$\sqrt{384}$ to five figures is no coincidence.

**Why the maximum is where $\alpha+\beta = 180^\circ$.** That is exactly the
condition for being cyclic: the opposite angles of a cyclic quadrilateral add to a
straight angle. The problem «maximise the area for given sides» always has the answer
«the cyclic one» — a good illustration of the fact that a GDC finds a number, not a
reason.
""")

md(r"""
## Solution 18 — a «show that» from a diagram

The point $C$ splits $[AB]$ into two pieces. The piece in the room of width 6 m: the
angle between the segment and the wall of the room is $\alpha$, and the width 6 lies
**opposite** that angle, so

$$CB = \frac{6}{\sin\alpha} = 6\operatorname{cosec}\alpha.$$

The piece in the corridor of width $\frac34$: there the same angle turns out to be
adjacent, and

$$AC = \frac{3/4}{\cos\alpha} = \frac34\sec\alpha.$$

Add them:

$$L = AC + CB = \frac34\sec\alpha + 6\operatorname{cosec}\alpha.
\qquad \blacksquare$$

```python
my18 = Rational(3, 4)/cos(alpha) + 6/sin(alpha)
```

**The marking.** A1 for one piece, A1 for the other; the sum is AG.

**Why one angle works in two triangles.** The walls are perpendicular, and the angle
$\alpha$ carries into the second triangle as the complement of
$90^\circ - \alpha$. Hence the swap of $\sin$ for $\cos$: what was opposite has
become adjacent.

**Where this leads.** In the original the minimum of $L$ is then hunted — the
classic «carry a ladder round a corner» problem, with the answer
$\alpha = \arctan\sqrt[3]{8} = \arctan 2$. The triangle here is only the entrance;
the problem itself is about the derivative (E9).
""")

md(r"""
## Solution 19 — the task on the timer

**(a)** The side $BC$ is opposite the angle $A = 2\theta$, the side $AB = 5$ is
opposite the angle $C = \theta$. The sine rule:

$$\frac{BC}{\sin2\theta} = \frac{5}{\sin\theta}
\ \Longrightarrow\ BC = \frac{5\sin2\theta}{\sin\theta}
= \frac{5\cdot2\sin\theta\cos\theta}{\sin\theta} = 10\cos\theta.$$

By the question $BC = 6\sqrt2$, so

$$10\cos\theta = 6\sqrt2 \iff \cos\theta = \frac{6\sqrt2}{10}
= \frac{3\sqrt2}{5}. \qquad \blacksquare$$

**(b)** An angle of a triangle, so the sine is positive:

$$\sin\theta = \sqrt{1-\frac{18}{25}} = \sqrt{\frac{7}{25}}
= \frac{\sqrt7}{5}.$$

**(c)** In the triangle $BCD$ the angle at the vertex $C$ is the same $\theta$, and
the sides at it are $BC = 6\sqrt2$ and $DC$:

$$\frac12\cdot 6\sqrt2\cdot DC\cdot\frac{\sqrt7}{5} = 2\sqrt{14}
\iff \frac{3\sqrt{14}}{5}\,DC = 2\sqrt{14}
\iff DC = \frac{10}{3}.$$

```python
my19_bc = 10*cos(theta)
my19_sin = sqrt(7)/5
my19_dc = Rational(10, 3)
```

**The marking.** (a): M1 for the sine rule, M1 for the double angle formula, A1 —
AG. (b): M1 for $\sin^2+\cos^2=1$, A1 for $\frac{\sqrt7}{5}$. (c): M1 for the area
formula with the sine found, A1 for $\frac{10}{3}$.

**The key to the whole question is the cancellation of $\sin\theta$.** The double
angle formula turns $\frac{\sin2\theta}{\sin\theta}$ into $2\cos\theta$, and the
equation becomes linear. Without it a trigonometric equation in $\theta$ is left,
which cannot be solved on Paper 1.

**How it looks in time.** Seven marks in ten minutes, and the first three are the
dearest: part (a) carries the other two. If the double angle formula has not come to
mind within a minute, there is no point going on.

**A check at the end.** The $\sqrt{14}$ in the answer to (c) cancels completely, and
$DC = \frac{10}{3} = 3.33$. The side $AC$ meanwhile equals
$AB\cos\theta + \ldots$ — in any case $DC$ has to be smaller than $AC$, and $3.33$
does not contradict that.
""")

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

OUT = os.path.join(ROOT, 'practicum/geometry', 'practicum-c1-triangle.ipynb')
with open(OUT, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
    fh.write('\n')
print(f'записано {OUT}: {len(cells)} ячеек')
