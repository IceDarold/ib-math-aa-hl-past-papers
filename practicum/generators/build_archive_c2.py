"""Собирает архивный ноутбук C2: вся радианная мера и все тела подряд.

Тридцать четыре вопроса архива, 105 баллов, девять разделов по приёмам
карточки geometry-circular-measure.yaml. Теории здесь нет: она в
практикуме, а это то, что открывают после него.

Проверки эталона не хранят. Им передают не ответ и не метод, а границу
фигуры: где идут дуги и где отрезки. `verify_area` берёт площадь формулой
Грина по этому контуру, `verify_perimeter` и `verify_length` складывают
длины кусков, `verify_volume` вращает сечение и применяет теорему Паппа.
Формул темы — ½r²θ, ½r²(θ − sin θ), ⅓πr²h — у проверок нет ни одной.

Половина вопросов темы обратные: не «найдите меру», а «найдите фигуру».
Тогда проверка идёт наоборот — фигуру строят из ответа, а известная мера
становится тем, с чем её сверяют. `verify_law` — для ответа-выражения:
и для «area in terms of θ», и для «show that r = 24π/(θ + 2)», где
выражением задаётся уже сама фигура.

Раскладка по разделам взята из карточки одним правилом: **блок стоит
в разделе своего верхнего приёма**. Девять блоков карточка числит за
двумя приёмами сразу — «найдите r, потом периметр C» это и составная
область, и обратная задача, — и каждый уходит на ту ступень лестницы,
до которой в нём доходит работа.

Девятый архивный ноутбук серии и первый, где ни один вопрос не сверяется
с числом: измеряют фигуру, и 3549π/16, 696.844 и 697 проходят одинаково.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/check_archive_c2.py подставляет его в собранный
.ipynb и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(ROOT,
                        'practicum/geometry/archive-c2-circular-measure.ipynb')

ANSWERS = {
    # § 1 радианы и длина дуги
    'q1_1': 'Rational(5, 2)',
    'q1_2th': '2*pi/5',
    'q1_2r': '30/pi',
    'q1_3': '3000*pi',
    'q1_4': '57.2958',
    'q1_5': '35.4099',
    'q1_6': '2.08',
    # § 2 угол во времени
    'q2_1': 'pi/8',
    'q2_2': '4.05093',
    'q2_3': 'pi*t/8',
    # § 3 периметр сектора
    'q3_1': '18',
    # § 4 площадь сектора
    'q4_1': '54.7898',
    'q4_2': '20',
    'q4_3': '3549*pi/16',
    # § 5 хорда и половинный угол
    'q5_1': '8.13416',
    'q5_2': '28.5657',
    # § 6 площадь сегмента
    'q6_1t': 'sin(th)/2',
    'q6_1s': '(th - sin(th))/2',
    'q6_2': '2*th - 2*sin(th)',
    # § 7 составная область
    'q7_1': '294',
    'q7_2': '260 - 2.6*r**2',
    'q7_3': '69.6640',
    # § 8 две связи вместо двух чисел
    'q8_1': '2.35673',
    'q8_2r': '8.68243',
    'q8_2p': '99.7838',
    'q8_3': '(10 - 2*r)/r',
    'q8_4r': 'Rational(5, 2)',
    'q8_4th': '2',
    'q8_5th': '1.59935',
    'q8_5r': '6.53330',
    'q8_6': '24*pi/(th + 2)',
    'q8_7': '0.411273',
    # § 9 круг выходит из плоскости
    'q9_1': '4',
    'q9_2': '8*sqrt(3)*pi/3',
    'q9_3': '6*sqrt(5)*pi',
    'q9_4': 'm*h',
    'q9_5': 'h*sqrt(1 + m**2)',
    'q9_6': '851',
    'q9_7': 'Rational(91, 8)',
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
# C2 archive: radian measure, sectors, solids

**Every past-paper question in which the answer is the measurement of a
figure, grouped by technique.** Not a practicum — a drill. There is no
theory here and no ladder to climb: the theory is in *Practicum C2*, and
this notebook is what you open afterwards, when the only thing left is to
do them all until the cutting-up is automatic.

**What is inside.** The whole of `geometry.circular_measure` and the whole
of `geometry.solid_geometry`, sessions May 2021 — November 2025:
**34 questions, 105 marks**, in nine sections, one section per technique.

The two topics are here together because in the archive they are one. The
solids topic has eight blocks; three of them are elsewhere (a vector cone,
a surface-area integral), and the five that remain are all cones — no
sphere, no cylinder, no pyramid gets a question of its own. And a cone,
every time, arrives as a rolled-up sector.

The corpus counts 40 blocks and 127 marks. Six blocks are not here:

| left out | marks | why |
|---|---|---|
| November 2023, second zonal copy | 7 | one paper filed twice, as TZ1 and TZ2 |
| May 2025 TZ3 P1 Q12(a) | 3 | $\lvert z-(2+i)\rvert=3$ — complex numbers |
| November 2022 P3 Q2(e)(v) | 4 | surface of an ellipsoid, by integration |
| May 2023 TZ1 P1 Q12(e) | 7 | the cone is built out of vectors |
| May 2021 TZ1 P3 Q2(e)(ii) | 1 | one sentence inside a Maclaurin investigation |

**How to work.** Read the question, answer in the cell below it, run the
cell. **None of the checks knows the answer.** What each one is handed is
the boundary of a figure — where the arcs run and where the straight
pieces do — and it measures it:

```python
verify_area('4.1', q4_1, *sector(5, 1.9, 2 * pi))
```

That is the diagram from the paper, in Python: a sector of radius 5 going
from $1.9$ all the way round to $2\pi$. The area comes from Green's
theorem on that contour, so $\tfrac12r^2\theta$ is not in the check and
neither is any other formula of the topic. Every correct form of the
answer passes — $\frac{3549\pi}{16}$, $696.844$ and $697$ alike.

**Half of these questions run the other way**, and so does the check. The
paper gives you the measurement and asks for the shape:

```python
verify_length('1.1', 10, arc((0, 0), 4, 0, q1_1))
```

The $10$ cm is the question's; your angle is inside the figure. Draw the
arc your answer says and it is $10$ cm long, or it is not.

That is also where **follow through** comes from. A figure may be built
out of an earlier answer of yours: the five segments of §7.3 stand on the
radius you found in §1.2, and the volume in §9.2 is spun from the slant
height you found in §9.1. A wrong part costs only itself, exactly as in
the markscheme.

**When you are wrong the check says how**, and every diagnosis is read off
the same contour: the arc was taken as a chord, the sector was given
instead of the segment, the arc was taken the other way round the circle,
the angle went in as degrees, one of five equal pieces was counted, the
$\tfrac13$ of a cone was dropped.

**Nothing is stored.** Not one of the thirty-nine answers is written down
in this notebook, as a number or as a hash. That is the third archive
notebook in a row — the two before it were about counting, where an answer
can always be counted again — and the reason here is the same one seen
from the other side: a figure can always be measured, and measuring does
not need to know the answer or even the formula it came from.

**Every question has a cell.** All thirty-four of them, which is the
second notebook running for which that is true. A measurement is always a
number, or an expression that turns into one, and there is always
something to hand over.

**Two places where the check is softer than the exam**, both said again
where they arise. In §8.7 the quadratic has two roots, and both build a
real sector of exactly the right area — measuring cannot tell them apart,
and the markscheme's mark for rejecting one is yours to earn alone. In
§1.4 the markscheme demands a fourth significant figure before the printed
$57.3^\circ$; the check accepts $57.3$.

**Nine of the thirty-four print their own answer** — *show that*
$\theta=2.08$, *show that* $AB=28.57$, *show that the area is*
$260-2.6r^2$. All nine keep their cell, because in all nine the work is to
arrive at the printed thing and the cell says whether you did. Two of
them, §6.1 and §8.3, are asked slightly differently so that there is
something to hand over at all, and both say so on the spot.

Leave a cell blank and it prints ⬜ and moves on, so you can run the whole
notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after
you have worked the question, not before.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Radians and arc length | 6 | 17 |
| 2 | The angle grows with the clock | 3 | 6 |
| 3 | The perimeter of a sector | 1 | 2 |
| 4 | The area of a sector | 3 | 8 |
| 5 | The chord and the half-angle | 2 | 6 |
| 6 | The area of a segment | 2 | 8 |
| 7 | A region with no name | 3 | 12 |
| 8 | Two conditions instead of two numbers | 7 | 28 |
| 9 | The circle leaves the plane | 7 | 18 |

Section 3 holds one question and two marks. That is not a gap in the
notebook; it is what the archive contains. The perimeter of a sector is
asked once on its own in five years, and the rest of the time it is the
first line of something longer — §1.6, §8.3, §8.6 all walk a boundary
before they do anything else.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + sin, cos, pi, sqrt, arc, seg, cone, ...

language('en')                 # this notebook is in English, and so are the checks

th = symbols('theta')          # the angle every one of these papers calls theta
r, h, m = symbols('r h m')     # letters that stay letters
DEGREE = pi / 180              # so that 210*DEGREE reads as '210 degrees'
                               # t, for time, already comes from kit


# Figures here are often drawn out of an answer you have not written yet.
# undrawn(...) hands back an empty boundary in that case, so the notebook
# runs top to bottom while it is still blank and the check prints ⬜.

def point(radius, angle, centre=(0, 0)):
    # the point of the circle at that angle
    if undrawn(radius, angle):
        return (Ellipsis, Ellipsis)
    return (centre[0] + radius * cos(angle), centre[1] + radius * sin(angle))


def sector(radius, start, end, centre=(0, 0)):
    # out along one radius, round the arc, back along the other
    return undrawn(radius, start, end) or (
        seg(centre, point(radius, start, centre)),
        arc(centre, radius, start, end),
        seg(point(radius, end, centre), centre))


def segment(radius, start, end, centre=(0, 0)):
    # round the arc, back along the chord
    return undrawn(radius, start, end) or (
        arc(centre, radius, start, end),
        seg(point(radius, end, centre), point(radius, start, centre)))


def triangle(radius, angle, centre=(0, 0)):
    # two radii and the chord joining their ends
    return undrawn(radius, angle) or (
        seg(centre, point(radius, 0, centre)),
        seg(point(radius, 0, centre), point(radius, angle, centre)),
        seg(point(radius, angle, centre), centre))


print('ready; sympy', sp.__version__)
print('exact:      ', 3549 * pi / 16)
print('to 3 s.f.:  ', sig(3549 * pi / 16, 3))
print('a figure:   ', len(sector(4, 0, Rational(5, 2))), 'pieces')
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. Radians and arc length

$$\theta=\frac{s}{r}\qquad\Longleftrightarrow\qquad s=r\theta$$

The angle *is* the arc, measured in radii. Two of $s$, $r$, $\theta$ are
given and the third is wanted; which one is wanted changes nothing about
the equation and everything about which way you read it.

Degrees have no such ratio behind them, so they never go into this
formula. When a paper hands you $210^\circ$ or asks for an answer in
degrees, the conversion is a step of its own.
""")

md(r"""
### 1.1 — *May 2023 TZ2 Paper 1 Q1(b), 2 marks*

The following diagram shows a circle with centre $O$ and radius $4$ cm.
The points $P$, $Q$ and $R$ lie on the circumference and
$P\hat{O}R=\theta$, measured in radians. The shaded sector is $POR$, and
the length of arc $PQR$ is $10$ cm.

Find $\theta$.
""")

code(r"""
q1_1 = ...       # the angle, in radians

verify_length('1.1', 10, arc((0, 0), 4, 0, q1_1))     # is your arc 10 cm long?
""")

md(r"""
### 1.2 — *November 2025 TZ1 Paper 2 Q1(a), 3 marks*

A regular pentagon is inscribed in a circle with centre $O$ and radius
$r$ cm. $A$ and $B$ are adjacent vertices, the angle $A\hat{O}B$ is
$\theta$, and arc $AB$ is $12$ cm.

Find **(i)** $\theta$; **(ii)** $r$.

*One check for both: five arcs like yours are laid round the centre one
after another. If your angle is right they close the circle, and if your
radius is right they come to $60$ cm.*
""")

code(r"""
q1_2th = ...     # the angle at the centre, in radians
q1_2r  = ...     # the radius, in cm

def rim(radius, angle):
    # five arcs like yours, laid one after another round the centre
    return undrawn(radius, angle) or [
        arc((0, 0), radius, n * angle, (n + 1) * angle) for n in range(5)]


verify_perimeter('1.2', 5 * 12, *rim(q1_2r, q1_2th))
""")

md(r"""
### 1.3 — *May 2025 TZ2 Paper 3 Q2(b)(ii), 2 marks*

The Earth is modelled as a sphere of radius $6000$ km with centre $O$. The
North Pole $P$ lies on the $z$-axis and Nairobi $N$ lies on the equator,
on the $y$-axis; part (b)(i) has just found the angle between
$\overrightarrow{OP}$ and $\overrightarrow{ON}$ to be $90^\circ$.

Show that the distance between $P$ and $N$ along the arc from $P$ to $N$
is $3000\pi$ km.
""")

code(r"""
q1_3 = ...       # the arc PN, in km, exactly

verify_length('1.3', q1_3, arc((0, 0), 6000, 0, pi / 2), exact=True)
""")

md(r"""
### 1.4 — *May 2025 TZ2 Paper 3 Q2(d), 2 marks*

On the same sphere, Moscow $M$ has position vector
$\overrightarrow{OM}=(0,\ 6\cos\theta,\ 6\sin\theta)$ in thousands of
kilometres, so that $\theta$ is the angle $N\hat{O}M$. The shortest
distance between two points on the sphere lies along an arc of a circle
with centre $O$; in this model the shortest distance from Moscow to
Nairobi is $6000$ km.

Show that $\theta=57.3^\circ$, correct to three significant figures.

> **Softer than the exam here.** The markscheme demands that a fourth
> significant figure be seen before the printed answer — $57.2957\ldots$
> — and refuses the mark without it. The check measures your arc, and
> $57.3$ measures close enough. Write the fourth figure anyway.
""")

code(r"""
q1_4 = ...       # the angle, in degrees

def to_moscow(degrees):
    # your angle, drawn as an arc on the 6000 km sphere
    return undrawn(degrees) or (arc((0, 0), 6000, 0, degrees * DEGREE),)


verify_length('1.4', 6000, *to_moscow(q1_4))
""")

md(r"""
### 1.5 — *May 2025 TZ3 Paper 2 Q4, 5 marks*

Points $A$, $B$ and $C$ lie on a circle with centre $O$. The area of
triangle $AOB$ is $26$ cm$^2$ and $A\hat{O}B=2.51$ radians. $C$ lies on
the major arc $AB$.

Find the length of the major arc $ACB$.

*Backwards: your arc gives the circle back its radius, and the triangle
$AOB$ inside that circle has to come to $26$ cm$^2$.*
""")

code(r"""
q1_5 = ...       # the length of the major arc ACB, in cm

def from_arc(major):
    # the major arc subtends 2*pi - 2.51 at the centre, so your answer
    # says what the radius is, and the triangle AOB follows from it
    return undrawn(major) or triangle(major / (2 * pi - 2.51), 2.51)


verify_area('1.5', 26, *from_arc(q1_5))
""")

md(r"""
### 1.6 — *May 2023 TZ1 Paper 2 Q10(a), 3 marks*

An engineer is designing a gutter, open at the top, made by folding a
piece of sheet metal $45$ cm wide. In cross-section, arc $AB$ lies on a
circle with centre $O$ and radius $12$ cm; the two vertical sides, above
$A$ and above $B$, are each $10$ cm high. Let $A\hat{O}B=\theta$, where
$0<\theta<\pi$.

Show that $\theta=2.08$, correct to three significant figures.

*The whole $45$ cm is the boundary of the cross-section except the open
top: down one side, round the arc, up the other. That is the line the
check walks.*
""")

code(r"""
q1_6 = ...       # the angle, in radians

def corners(angle):
    # A and B at the ends of the arc, and the tops of the two sides
    low, high = -pi / 2 - angle / 2, -pi / 2 + angle / 2
    foot_l, foot_r = point(12, low), point(12, high)
    return (foot_l, foot_r,
            (foot_r[0], foot_r[1] + 10), (foot_l[0], foot_l[1] + 10))


def metal(angle):
    # the sheet: down one side, round the arc, up the other. The top is open.
    if undrawn(angle):
        return undrawn(angle)
    foot_l, foot_r, top_r, top_l = corners(angle)
    return (seg(top_l, foot_l),
            arc((0, 0), 12, -pi / 2 - angle / 2, -pi / 2 + angle / 2),
            seg(foot_r, top_r))


verify_length('1.6', 45, *metal(q1_6))
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. The angle grows with the clock

$$\omega=\frac{2\pi}{T}\qquad\text{and then}\qquad\theta=\omega t$$

One revolution every $T$ seconds. Find how much angle that is per second
and the question turns back into section 1. Everything in the archive that
rotates does it at a constant rate, so there is never more to it than a
division — but the division has to happen before anything else.

All three of these are one question: a sprinkler, May 2024 TZ2.
""")

md(r"""
### 2.1 — *May 2024 TZ2 Paper 2 Q11(b), 1 mark*

A rotating sprinkler at a fixed point $S$ waters all points inside and on
a circle of radius $20$ metres. It rotates at a constant rate of one
revolution every $16$ seconds.

Show that the sprinkler rotates through an angle of $\dfrac{\pi}{8}$
radians in one second.
""")

code(r"""
q2_1 = ...       # the angle turned in one second, in radians

# one second is a sixteenth of a revolution, so the tip of the jet
# travels a sixteenth of the way round the 20 m circle
verify_length('2.1', 2 * pi * 20 / 16, arc((0, 0), 20, 0, q2_1))
""")

md(r"""
### 2.2 — *May 2024 TZ2 Paper 2 Q11(c), 4 marks*

$S$ is $14$ metres from the edge of a straight path, and that edge cuts
the circle at $A$ and $B$. Let $T$ seconds be the time for which $[AB]$ is
watered in each revolution.

Find the value of $T$.

*Your $T$ seconds sweep the jet through some angle. The perpendicular from
$S$ to the chord that angle cuts must be the $14$ m of the question.*
""")

code(r"""
q2_2 = ...       # the time, in seconds

def to_path(seconds):
    # from S straight out to the edge of the path: the perpendicular to
    # the chord the jet cuts while it sweeps for that many seconds
    if undrawn(seconds):
        return undrawn(seconds)
    swept = seconds * pi / 8
    return (seg((0, 0), (point(20, swept / 2)[0], 0)),)


verify_length('2.2', 14, *to_path(q2_2))
""")

md(r"""
### 2.3 — *May 2024 TZ2 Paper 2 Q11(d), 1 mark*

Consider one clockwise revolution of the sprinkler. At $t=0$ the water
crosses the edge of the path at $A$; at time $t$ seconds it crosses at a
movable point $D$. Let $\alpha=A\hat{S}D$, in radians.

Write down an expression for $\alpha$ in terms of $t$.

*Checked on a circle of radius $1$, where the arc and the angle are the
same number. That is not a trick — it is what a radian is.*
""")

code(r"""
q2_3 = ...       # alpha, in terms of t

def unit_arc(seconds):
    # in that many seconds the sprinkler turns that fraction of a
    # revolution; on a circle of radius 1 the arc is the angle
    return (arc((0, 0), 1, 0, 2 * pi * seconds / 16),)


verify_law('2.3', q2_3, t, unit_arc, (1, 3, 7), measure='length')
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. The perimeter of a sector

$$P=r\theta+2r$$

Walk round the shaded slice with your finger: out along a radius, round
the arc, back along the other radius. Three pieces, and the two straight
ones are the whole difficulty — the arc is the piece everybody remembers.
""")

md(r"""
### 3.1 — *May 2023 TZ2 Paper 1 Q1(a), 2 marks*

The same circle as §1.1: centre $O$, radius $4$ cm, arc $PQR$ of length
$10$ cm, shaded sector $POR$.

Find the perimeter of the shaded sector.

*This is part (a) of the paper and §1.1 is part (b), and the order is not
an accident: the perimeter needs nothing from the angle, because the arc
is handed to you. The check still has to draw a sector, and it draws yours
from §1.1 — so that one has to be filled in first even though the
mathematics does not require it.*
""")

code(r"""
q3_1 = ...       # the perimeter, in cm

verify_perimeter('3.1', q3_1, *sector(4, 0, q1_1))     # your angle from §1.1
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. The area of a sector

$$A=\frac{\theta}{2\pi}\cdot\pi r^2=\tfrac12r^2\theta$$

A slice of the disc, in the same proportion as its angle. The one thing
that goes wrong is reading the wrong angle off the diagram: when the
shaded piece is the larger one, the number in the formula is $2\pi-\theta$
and not $\theta$.
""")

md(r"""
### 4.1 — *May 2022 TZ2 Paper 2 Q1(b), 3 marks*

The following diagram shows a circle with centre $O$ and radius $5$
metres. Points $A$ and $B$ lie on the circle and $A\hat{O}B=1.9$ radians.
**The shaded sector is the larger one.**

Find the area of the shaded sector.
""")

code(r"""
q4_1 = ...       # the shaded area, in m^2

verify_area('4.1', q4_1, *sector(5, 1.9, 2 * pi))   # from B the long way to A
""")

md(r"""
### 4.2 — *May 2023 TZ2 Paper 1 Q1(c), 2 marks*

The same circle again: radius $4$ cm, arc $PQR$ of length $10$ cm.

Find the area of the shaded sector.
""")

code(r"""
q4_2 = ...       # the area, in cm^2

verify_area('4.2', q4_2, *sector(4, 0, q1_1))          # your angle from §1.1
""")

md(r"""
### 4.3 — *May 2025 TZ1 Paper 2 Q1(a), 3 marks*

The points $A$ and $B$ lie on a circle with centre $O$ and radius
$19.5$ cm, such that $B\hat{O}A=210^\circ$.

Find the area of the sector $BOA$.
""")

code(r"""
q4_3 = ...       # the area of the sector, in cm^2

verify_area('4.3', q4_3, *sector(19.5, 0, 210 * DEGREE))
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. The chord and the half-angle

$$AB=2r\sin\frac{\theta}{2},\qquad OM=r\cos\frac{\theta}{2}$$

Drop the perpendicular from the centre to the chord. It bisects the chord,
it bisects the angle, and it leaves a right-angled triangle with the
radius as hypotenuse — all three at once, and every fact about chords
comes out of that triangle.

The cosine rule gives the same chord and the markscheme takes it. The
right triangle is shorter, and it is the only route when what you are
given is the distance from the centre.

> The mark that goes missing here is the **doubling**. You find half the
> chord, or half the angle, and then you write it down.
""")

md(r"""
### 5.1 — *May 2022 TZ2 Paper 2 Q1(a), 3 marks*

The circle of §4.1: centre $O$, radius $5$ metres, $A\hat{O}B=1.9$
radians.

Find the length of the chord $[AB]$.
""")

code(r"""
q5_1 = ...       # the chord, in m

verify_length('5.1', q5_1, seg(point(5, 0), point(5, 1.9)))
""")

md(r"""
### 5.2 — *May 2024 TZ2 Paper 2 Q11(a), 3 marks*

The sprinkler of §2: it waters a circle of radius $20$ m about $S$, and
$S$ is $14$ m from the straight edge of a path which cuts that circle at
$A$ and $B$.

Show that $AB=28.57$, correct to four significant figures.

*Backwards again: $A$ sits $14$ m across and half your chord along, and it
is on the circle, so $SA$ has to be $20$ m.*
""")

code(r"""
q5_2 = ...       # the chord AB, in m

def to_A(chord):
    # from S to A: 14 m across to the path, then half your chord along it
    return undrawn(chord) or (seg((0, 0), (14, chord / 2)),)


verify_length('5.2', 20, *to_A(q5_2))                  # SA is a radius
""")

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. The area of a segment

$$\underbrace{\tfrac12r^2\theta}_{\text{sector}}
-\underbrace{\tfrac12r^2\sin\theta}_{\text{triangle}}
=\tfrac12r^2(\theta-\sin\theta)$$

The region between a chord and its arc has no formula of its own; it is a
subtraction of two things you already have. Three numbers live in that one
line, and the markscheme distinguishes them — so does the check: hand it
the sector and it will say that a segment is the sector minus the
triangle.

> **The mixed-mode error.** In $\tfrac12r^2(\theta-\sin\theta)$ the letter
> $\theta$ appears twice, once as a number and once inside a sine. In
> degree mode the first is right and the second is wrong, and the answer
> is neither one thing nor the other. It is the quietest mistake in the
> topic.
""")

md(r"""
### 6.1 — *November 2021 Paper 2 Q4(a), 5 marks*

The following diagram shows a semicircle with centre $O$ and radius $r$.
Points $P$, $Q$ and $R$ lie on the circumference, such that $PQ=2r$ and
$R\hat{O}Q=\theta$, where $0<\theta<\pi$. Two regions are shaded: the
triangle $POR$, and the segment between the chord $[RQ]$ and its arc.

Given that the areas of the two shaded regions are equal, show that
$\theta=2\sin\theta$.

*Rewritten so that there is something to hand over, and the rewrite is the
reason the printed answer carries no $r$: both areas have a factor $r^2$
and it cancels. Take $r=1$ and give the two areas separately, in terms of
$\theta$. Setting them equal is the last line, and it is yours.*
""")

code(r"""
q6_1t = ...      # the area of triangle POR, with r = 1, in terms of th
q6_1s = ...      # the area of the segment on [RQ], with r = 1, in terms of th

def por(angle):
    # the triangle: half the diameter, out to R on the circle, and back
    return (seg((-1, 0), (0, 0)), seg((0, 0), point(1, angle)),
            seg(point(1, angle), (-1, 0)))


verify_law('6.1 (triangle)', q6_1t, th, por, (0.7, 1.9, 2.8))
verify_law('6.1 (segment)', q6_1s, th,
           lambda angle: segment(1, 0, angle), (0.7, 1.9, 2.8))
""")

md(r"""
### 6.2 — *May 2022 TZ1 Paper 2 Q2(a), 3 marks*

A logo is created by removing two equal segments from a rectangle
measuring $5$ cm by $4$ cm, one from each of the two long sides. The
points $A$ and $B$ lie on a circle with centre $O$ and radius $2$ cm,
such that $A\hat{O}B=\theta$, where $0<\theta<\pi$.

Find the area of one of the shaded segments in terms of $\theta$.

*Measured at three angles, so any correct form passes:
$2\theta-2\sin\theta$ and $2(\theta-\sin\theta)$ are the same answer.*
""")

code(r"""
q6_2 = ...       # the area of one segment, in terms of th

verify_law('6.2', q6_2, th, lambda angle: segment(2, 0, angle), (0.7, 1.9, 2.8))
""")

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. A region with no name

$$\text{shaded}=\sum(\text{pieces that do have names})$$

None of the shapes here is a sector, a segment or a triangle. All of them
are sums and differences of those, and the work is done on the drawing
before any number is written.

Two rules make the cutting reliable. **Write each piece on its own line,
with its own sign** — the arithmetic is never the difficulty, keeping
track of what has been added and what subtracted is. And **count the
repeats before you finish**: five segments, two bites, two vertical sides.

The markscheme of the gutter question is unusually frank about it:

> *"There are many different ways to dissect the cross-section to
> determine its area."*

They all give the same number, and choosing one is drawing, not
calculating.
""")

md(r"""
### 7.1 — *May 2023 TZ1 Paper 2 Q10(b), 7 marks*

The gutter of §1.6, with $\theta=2.08$ now established: arc $AB$ on a
circle of centre $O$ and radius $12$ cm, two vertical sides of $10$ cm,
and the width of the gutter $w$ cm across the top.

Find the area of the cross-section of the gutter.

*Built from your own answer to §1.6, so a wrong angle there costs only
itself.*
""")

code(r"""
q7_1 = ...       # the area of the cross-section, in cm^2

def gutter(angle):
    # the cross-section: the arc below AB, and the rectangle above it
    if undrawn(angle):
        return undrawn(angle)
    foot_l, foot_r, top_r, top_l = corners(angle)
    return (arc((0, 0), 12, -pi / 2 - angle / 2, -pi / 2 + angle / 2),
            seg(foot_r, top_r), seg(top_r, top_l), seg(top_l, foot_l))


verify_area('7.1', q7_1, *gutter(q1_6))                # your angle from §1.6
""")

md(r"""
### 7.2 — *November 2023 Paper 2 Q3(a), 2 marks*

A logo is a letter “C” formed between two circles with centre $O$. The
point $A$ lies on the inner circle, of radius $r$ cm where $r<10$; the
point $B$ lies on the outer circle, of radius $10$ cm. The reflex angle
$A\hat{O}B$ is $5.2$ radians, and the “C” is the region between the two
arcs.

Show that the area of the “C” is given by $260-2.6r^2$.
""")

code(r"""
q7_2 = ...       # the area of the C, in terms of r

def letter_c(inner):
    # between two arcs of 5.2 radians, closed by the two straight ends
    return undrawn(inner) or (
        seg((inner, 0), (10, 0)),
        arc((0, 0), 10, 0, 5.2),
        seg(point(10, 5.2), point(inner, 5.2)),
        arc((0, 0), inner, 5.2, 0))


verify_law('7.2', q7_2, r, letter_c, (3, 5, 8))
""")

md(r"""
### 7.3 — *November 2025 TZ1 Paper 2 Q1(b), 3 marks*

The regular pentagon of §1.2, inscribed in the circle of radius $r$ cm.
The shaded region is what is left of the disc outside the pentagon — five
equal pieces.

Find the area of the shaded region.

*Drawn from your own $\theta$ and $r$ of §1.2. If you give the check one
piece instead of five it will say so, and name the five.*
""")

code(r"""
q7_3 = ...       # the shaded area, in cm^2

def fan(radius, angle, count):
    # that many segments like yours, laid round the centre in turn
    return undrawn(radius, angle) or [
        piece for n in range(count)
        for piece in segment(radius, n * angle, (n + 1) * angle)]


verify_area('7.3', q7_3, *fan(q1_2r, q1_2th, 5))       # your answers from §1.2
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. Two conditions instead of two numbers

$$2r+r\theta=10\quad\text{and}\quad\tfrac12r^2\theta=6.25
\ \Longrightarrow\ 4r^2-20r+25=0$$

The hardest questions in the topic give you no $r$ and no $\theta$. They
give two *measurements* — a perimeter and an area, an area and a ratio —
and both of those are expressions in $r$ and $\theta$. Two equations, two
unknowns: eliminate the one you were not asked for, solve what is left,
and then do the step that carries its own mark.

> **Reject the root the question forbids.** *"Award (A1)(M1)A0 if
> additional answers are given"* — November 2025 TZ3. The circle does not
> care that $\theta=9.73$ solves the quadratic; the question said the
> angle was acute.

Sometimes what is left is not a quadratic at all.
$20-4\theta+4\sin\theta=13.4$ has no algebraic solution and none is
expected: this is where the calculator finally does something a pencil
cannot.
""")

md(r"""
### 8.1 — *May 2022 TZ1 Paper 2 Q2(b), 3 marks*

The logo of §6.2: a $5$ cm by $4$ cm rectangle with an equal segment
removed from each long side, the segments cut by a circle of radius $2$ cm
at angle $\theta$.

Given that the area of the logo is $13.4$ cm$^2$, find the value of
$\theta$.
""")

code(r"""
q8_1 = ...       # the angle, in radians

def logo(angle):
    # the rectangle, 4 wide and 5 tall, with a segment bitten out of each side
    if undrawn(angle):
        return undrawn(angle)
    half = angle / 2
    away, high = 2 * cos(half), 2 * sin(half)     # centre to chord, half-chord
    left, right = (-away, Rational(5, 2)), (4 + away, Rational(5, 2))
    low_l, top_l = (0, Rational(5, 2) - high), (0, Rational(5, 2) + high)
    low_r, top_r = (4, Rational(5, 2) - high), (4, Rational(5, 2) + high)
    return (seg((0, 0), (4, 0)), seg((4, 0), low_r),
            arc(right, 2, pi + half, pi - half),
            seg(top_r, (4, 5)), seg((4, 5), (0, 5)), seg((0, 5), top_l),
            arc(left, 2, half, -half),
            seg(low_l, (0, 0)))


verify_area('8.1', 13.4, *logo(q8_1))       # does your angle leave 13.4 cm^2?
""")

md(r"""
### 8.2 — *November 2023 Paper 2 Q3(b), 5 marks*

The “C” of §7.2, between circles of radius $r$ and $10$ cm at a reflex
angle of $5.2$ radians. The area of the “C” is $64$ cm$^2$.

**(i)** Find the value of $r$. **(ii)** Find the perimeter of the “C”.

*The figure in (ii) is built from your own $r$, so a wrong (i) costs only
(i).*
""")

code(r"""
q8_2r = ...      # the inner radius, in cm
q8_2p = ...      # the perimeter of the C, in cm

verify_area('8.2 (radius)', 64, *letter_c(q8_2r))
verify_perimeter('8.2 (perimeter)', q8_2p, *letter_c(q8_2r))
""")

md(r"""
### 8.3 — *May 2024 TZ1 Paper 1 Q3(a), 4 marks*

Points $A$ and $B$ lie on the circumference of a circle of radius $r$ cm
with centre $O$. The angle $A\hat{O}B$ is $\theta$, measured in radians.
The perimeter of the sector is $10$ cm and its area is $6.25$ cm$^2$.

Show that $4r^2-20r+25=0$.

*The quadratic is printed, so the cell asks for the step that produces it:
**eliminate $\theta$**. Write $\theta$ in terms of $r$, and the check
draws that sector at three different radii and walks round each one — the
perimeter has to come out $10$ every time.*
""")

code(r"""
q8_3 = ...       # theta in terms of r

def with_angle(radius):
    # your theta(r), drawn as a sector of that radius
    return undrawn(q8_3) or sector(radius, 0, q8_3.subs(r, radius))


verify_law('8.3', 10, r, with_angle, (1.5, 2, 3), measure='perimeter')
""")

md(r"""
### 8.4 — *May 2024 TZ1 Paper 1 Q3(b), 4 marks*

Hence, or otherwise, find the value of $r$ and the value of $\theta$.

*Your sector is measured twice, because the question gave two numbers.*
""")

code(r"""
q8_4r  = ...     # the radius, in cm
q8_4th = ...     # the angle, in radians

mine = sector(q8_4r, 0, q8_4th)

verify_perimeter('8.4 (perimeter)', 10, *mine)
verify_area('8.4 (area)', 6.25, *mine)
""")

md(r"""
### 8.5 — *May 2025 TZ2 Paper 2 Q6, 6 marks*

The following diagram shows a circle with centre $O$ and radius $r$ cm.
Points $A$ and $B$ lie on the circle and $A\hat{O}B=\theta$ radians. The
sector $OAB$ is divided into two regions: a shaded segment $P$ and a
triangle $Q$. The area of $P$ is $12.8$ cm$^2$, and the areas of $P$ and
$Q$ are in the ratio $3:5$.

Find the value of $\theta$ and the value of $r$.

*The paper asks only for $r$; the markscheme finds $\theta$ first and
scores it, so both are asked here.*
""")

code(r"""
q8_5th = ...     # the angle, in radians
q8_5r  = ...     # the radius, in cm

# segment and triangle together fill the sector, so the segment is 3/8
verify_area('8.5 (segment)', 12.8, *segment(q8_5r, 0, q8_5th))
verify_area('8.5 (sector)', 12.8 * Rational(8, 3), *sector(q8_5r, 0, q8_5th))
""")

md(r"""
### 8.6 — *November 2025 TZ3 Paper 2 Q3(a), 3 marks*

Consider a circle of radius $8$ mm and a sector of radius $r$ mm whose
acute angle at the centre is $\theta$ radians. The perimeter of the sector
is $1.5$ times the circumference of the circle.

Show that $r=\dfrac{24\pi}{\theta+2}$.

*Same shape as §8.3, the other way up: write $r$ in terms of $\theta$, and
the check draws that sector at three different angles and walks round each
one — the perimeter has to come out $24\pi$ every time.*
""")

code(r"""
q8_6 = ...       # r in terms of th

def with_radius(angle):
    # your r(theta), drawn as a sector at that angle
    return undrawn(q8_6) or sector(q8_6.subs(th, angle), 0, angle)


verify_law('8.6', 1.5 * 2 * pi * 8, th, with_radius, (0.5, 1, 2.5),
           measure='perimeter')
""")

md(r"""
### 8.7 — *November 2025 TZ3 Paper 2 Q3(b), 3 marks*

It is given that the area of the circle is the same as the area of the
sector.

Determine the value of $\theta$.

> **Softer than the exam here.** The quadratic has two roots, and both of
> them build a real sector of exactly the right area — they are simply two
> different sectors. Measuring cannot tell them apart, so the check will
> accept $9.73$. The markscheme will not: *"Award (A1)(M1)A0 if additional
> answers are given."* Only one of the two is acute, and picking it is
> yours to earn.
""")

code(r"""
q8_7 = ...       # the angle, in radians

def from_part_a(angle):
    # part (a) gives the radius, so your angle draws the whole sector
    return undrawn(angle) or sector(24 * pi / (angle + 2), 0, angle)


verify_area('8.7', pi * 8 ** 2, *from_part_a(q8_7))    # equal to the circle
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. The circle leaves the plane

$$\underbrace{l\theta}_{\text{the arc}}
=\underbrace{2\pi R}_{\text{the base circle}}$$

Cut a sector of radius $l$ out of paper and join its two straight edges.
The result is a cone with no base, and nothing about the paper has
changed: the radius of the sector is now the slant height, and the arc is
now the circle round the bottom.

That one equation is the whole conversion, and it is why the curved
surface of a cone is $\pi Rl$ rather than something to remember: the
sector's area is $\tfrac12l^2\theta=\tfrac12l\cdot l\theta
=\tfrac12l\cdot2\pi R=\pi Rl$.

The rest is Pythagoras and one line from the booklet:

$$l^2=R^2+h^2,\qquad V=\tfrac13\pi R^2h,\qquad
S_{\text{total}}=\pi R^2+\pi Rl$$

> **Two traps, and both are about what is included.** *Total* surface area
> has the base in it; *curved* does not. And the $\tfrac13$ is the whole
> difference between a cone and the cylinder around it — the check names
> that one in those words.

`cone(radius=..., height=...)` — or `slant=` instead — hands the check the
axial cross-section, the triangle that gets spun. The volume then comes
from Pappus' theorem on that contour, so no volume formula is stored
anywhere either.
""")

md(r"""
### 9.1 — *May 2021 TZ2 Paper 1 Q10(c), 3 marks*

A right cone has a total surface area of $12\pi$, base radius $2$, height
$h$ and slant height $l$.

Find the value of $l$.

*The check unrolls it: a disc for the base, and the sector the curved
surface came from.*
""")

code(r"""
q9_1 = ...       # the slant height

def unrolled(slant_height):
    # the cone opened out flat: the base disc, and the sector it came from
    return undrawn(slant_height) or (
        (arc((0, 0), 2, 0, 2 * pi),)
        + sector(slant_height, 0, 2 * pi * 2 / slant_height))


verify_area('9.1', 12 * pi, *unrolled(q9_1))
""")

md(r"""
### 9.2 — *May 2021 TZ2 Paper 1 Q10(d), 4 marks*

Hence, find the volume of the cone.

*Paper 1: a decimal earns nothing here. Built from your own $l$ of §9.1.*
""")

code(r"""
q9_2 = ...       # the volume, exactly

verify_volume('9.2', q9_2, *cone(radius=2, slant=q9_1), exact=True)
""")

md(r"""
### 9.3 — *November 2022 Paper 1 Q2(b), 3 marks*

Consider a circle with diameter $AB$, where $A$ has coordinates
$(1,4,0)$ and $B$ has coordinates $(-3,2,-4)$. Part (a) has found its
centre to be $(-1,3,-2)$ and its radius to be $3$. The circle forms the
base of a right cone whose vertex $V$ has coordinates $(-1,-1,0)$.

Find the exact volume of the cone.

*The cell is given the radius, which is part (a), and the length $VA$,
which is a slant edge and reads straight off the two points. The height —
which is where the marks are — is yours.*
""")

code(r"""
q9_3 = ...       # the volume, exactly

VA = sqrt((1 - (-1)) ** 2 + (4 - (-1)) ** 2 + (0 - 0) ** 2)   # from V to A

verify_volume('9.3', q9_3, *cone(radius=3, slant=VA), exact=True)
""")

md(r"""
### 9.4 — *November 2022 Paper 3 Q2(b)(i), 1 mark*

Consider the straight line from the origin, $y=mx$, where $0\le x\le h$
and $m$, $h$ are positive constants. Rotating it through $360^\circ$ about
the $x$-axis forms a cone.

Deduce an expression for the radius $r$ of this cone in terms of $h$
and $m$.

*Two letters, and the check can only vary one at a time, so it runs twice:
once along $h$ with $m$ pinned at $2$, once along $m$ with $h$ pinned
at $3$. Between them nothing but $mh$ survives.*
""")

code(r"""
q9_4 = ...       # the radius r, in terms of h and m

def base(height, gradient):
    # the base radius: from the axis straight up to the line y = mx
    return (seg((height, 0), (height, gradient * height)),)


verify_law('9.4 (m = 2)', q9_4, h, lambda v: base(v, 2), (1, 3, 7),
           measure='length', at={m: 2})
verify_law('9.4 (h = 3)', q9_4, m, lambda v: base(3, v), (1, 2, 5),
           measure='length', at={h: 3})
""")

md(r"""
### 9.5 — *November 2022 Paper 3 Q2(b)(ii), 2 marks*

Deduce an expression for the slant height $l$ in terms of $h$ and $m$.
""")

code(r"""
q9_5 = ...       # the slant height l, in terms of h and m

def edge(height, gradient):
    # the slant: the piece of the line itself, from the vertex to the rim
    return (seg((0, 0), (height, gradient * height)),)


verify_law('9.5 (m = 2)', q9_5, h, lambda v: edge(v, 2), (1, 3, 7),
           measure='length', at={m: 2})
verify_law('9.5 (h = 3)', q9_5, m, lambda v: edge(3, v), (1, 2, 5),
           measure='length', at={h: 3})
""")

md(r"""
### 9.6 — *May 2024 TZ1 Paper 2 Q2(b), 2 marks*

A monument is in the shape of a right cone with a vertical height of
$20$ metres. Part (a) has found the radius of its base to be
$6.37262\ldots$ m.

Find the volume of the monument.

*Paper 2: three significant figures. The same two lines as §9.2, and the
mathematics does not notice which paper it is on — the markscheme does.*
""")

code(r"""
q9_6 = ...       # the volume, in m^3

verify_volume('9.6', q9_6, *cone(radius=6.37262, height=20))
""")

md(r"""
### 9.7 — *May 2025 TZ1 Paper 2 Q1(b), 3 marks*

The sector $BOA$ of §4.3 — radius $19.5$ cm, $B\hat{O}A=210^\circ$ — is
cut out of a piece of paper. A hollow cone with no base is then made from
it by joining $A$ to $B$; the sector becomes the curved surface of the
cone.

Find the radius of the cone.

*Nothing about the paper changes when you roll it: the cut edge keeps its
length, and the check asks your circle to have exactly that circumference.*
""")

code(r"""
q9_7 = ...       # the radius of the cone's base, in cm

CUT = 19.5 * 210 * DEGREE           # the curved edge of the paper sector

verify_length('9.7', CUT, arc((0, 0), q9_7, 0, 2 * pi))   # the same edge, joined
""")

# ------------------------------------------------------------------ решения
md(r"""
---
# Solutions

Every number below is worked from the question. Where the markscheme gives
a second route, it is here too — not as decoration, but because knowing
that two dissections give the same number is most of what this topic
teaches.

---

## 1. Radians and arc length

**1.1** $s=r\theta$ with $s=10$ and $r=4$:

$$\theta=\frac{10}{4}=\boxed{\tfrac52}=2.5$$

Paper 1, so the fraction is the answer and there is nothing to evaluate.

**1.2 (i)** Five equal arcs fill the circle, so each subtends a fifth of a
full turn:

$$\theta=\frac{2\pi}{5}=\boxed{\tfrac{2\pi}{5}}=1.26\text{ rad}$$

**(ii)** That arc is $12$ cm long, so from $s=r\theta$,

$$r=\frac{12}{2\pi/5}=\frac{60}{2\pi}=\boxed{\tfrac{30}{\pi}}=9.55\text{ cm}$$

The whole circumference is $5\times12=60$ cm, which gives the radius in
one step and is the check's route.

**1.3** Part (b)(i) has $\boldsymbol{p}\cdot\boldsymbol{n}=0$, so the
angle at $O$ is $\tfrac{\pi}{2}$, and

$$s=r\theta=6000\cdot\frac{\pi}{2}=\boxed{3000\pi}\text{ km}$$

The markscheme also takes it as a quarter of the circumference,
$\tfrac14\cdot2\pi\cdot6000$. In the units of the diagram — thousands of
kilometres — the same line reads $6\cdot\tfrac{\pi}{2}=3\pi$.

**1.4** The shortest distance is an arc of the great circle, radius
$6000$ km, and it is $6000$ km long. So $s=r\theta$ gives

$$6000=6000\,\theta\ \Longrightarrow\ \theta=1\text{ radian}$$

and one radian is

$$\frac{180}{\pi}=\boxed{57.2957\ldots^\circ}=57.3^\circ\ (3\text{ s.f.})$$

The whole question is the definition of a radian read out loud: the angle
whose arc equals the radius. **Write the $57.2957$ down** — the markscheme
refuses the A1 unless a fourth significant figure appears somewhere.

**1.5** The triangle first, because it is what carries the $26$:

$$\tfrac12r^2\sin2.51=26\ \Longrightarrow\ r^2=\frac{52}{\sin2.51}
=88.07\ldots\ \Longrightarrow\ r=9.3846\ldots$$

The major arc turns through what is left of the circle:

$$s=r(2\pi-2.51)=9.3846\ldots\times3.7731\ldots=\boxed{35.4}\text{ cm}$$

Taking $2.51$ instead of $2\pi-2.51$ gives $23.6$ — that is the minor arc
$AB$, and $C$ was told to be on the major one.

**1.6** The $45$ cm of metal becomes the two sides and the arc:

$$45=10+12\theta+10\ \Longrightarrow\ 12\theta=25
\ \Longrightarrow\ \theta=\frac{25}{12}=2.0833\ldots=\boxed{2.08}$$

Nothing here is about circles except $s=r\theta$; the difficulty is
reading which parts of the sheet are which, and that $\theta$ is the
angle *at $O$*, not the angle the metal turns through.

---

## 2. The angle grows with the clock

**2.1** One revolution is $2\pi$ and it takes $16$ seconds:

$$\frac{2\pi}{16}=\boxed{\frac{\pi}{8}}$$

One mark, and it is the mark for dividing before doing anything else.

**2.2** $[AB]$ is watered while the jet lies between $SA$ and $SB$, so the
angle swept is $A\hat{S}B$. The perpendicular from $S$ to the path is
$14$ m and the radius is $20$ m, so

$$\cos\frac{A\hat{S}B}{2}=\frac{14}{20}
\ \Longrightarrow\ A\hat{S}B=2\arccos0.7=1.5907\ldots$$

At $\tfrac{\pi}{8}$ radians per second,

$$T=\frac{1.5907\ldots}{\pi/8}=\boxed{4.05}\text{ seconds}$$

Forgetting to double the half-angle gives $2.03$, which is exactly half
the answer, and the check says so in those words.

**2.3** The rate is constant, so the angle is the rate times the time:

$$\alpha=\boxed{\frac{\pi t}{8}}$$

$\tfrac{2\pi t}{16}$ is the same expression and the markscheme takes it.

---

## 3. The perimeter of a sector

**3.1** Out along a radius, round the arc, back along the other radius:

$$P=10+4+4=\boxed{18}\text{ cm}$$

The markscheme spells out what the mark is for — *"arc + 2 × radius"* —
and the answer that loses it is $10$, the arc alone. Note that this is
part (a) of the paper: the angle of §1.1 is not needed, because the arc is
handed to you.

---

## 4. The area of a sector

**4.1** The shaded sector is the **larger** one, so the angle is the
reflex one:

$$A=\tfrac12r^2(2\pi-\theta)=\tfrac12\cdot25\cdot(2\pi-1.9)
=12.5\times4.3831\ldots=\boxed{54.8}\text{ m}^2$$

Using $1.9$ gives $23.75$, the minor sector, and the two together are
$\pi\cdot25=78.5$ — a check worth doing in one line.

**4.2** With $\theta=\tfrac52$ from §1.1,

$$A=\tfrac12\cdot4^2\cdot\tfrac52=\tfrac12\cdot16\cdot2.5=\boxed{20}
\text{ cm}^2$$

The markscheme also accepts $\tfrac12\cdot4\cdot10$ — half the radius
times the arc — which is the same formula with $r\theta$ left standing.

**4.3** $210^\circ$ in radians is $\tfrac{210\pi}{180}=\tfrac{7\pi}{6}$:

$$A=\tfrac12(19.5)^2\cdot\frac{7\pi}{6}=\frac{3549\pi}{16}
=\boxed{697}\text{ cm}^2\quad(696.844\ldots)$$

Substituting $210$ itself gives $38\,036$, which is $\tfrac{180}{\pi}$
times too big. The markscheme of November 2021 prices that mistake
exactly: *"Award a maximum of M1A1A0A0A0 if a candidate uses degrees, even
if later work is correct."*

---

## 5. The chord and the half-angle

**5.1** Drop the perpendicular from $O$ to $[AB]$; it bisects both:

$$AB=2\cdot5\cdot\sin\frac{1.9}{2}=10\sin0.95=\boxed{8.13}\text{ m}$$

The cosine rule gives it too:
$AB^2=25+25-2\cdot25\cos1.9=66.16\ldots$, and $\sqrt{66.16\ldots}=8.13$.

**5.2** Now the perpendicular is the thing you are given. In the right
triangle $SMA$, with $M$ the midpoint of $[AB]$:

$$AM=\sqrt{20^2-14^2}=\sqrt{204}=14.2828\ldots$$
$$AB=2AM=\sqrt{816}=\boxed{28.57}\ (28.5657\ldots)$$

May 2024 gives *"recognizes that $AB=2AM$"* a mark of its own, which tells
you how often the $14.28$ gets written down as the answer.

---

## 6. The area of a segment

**6.1** Since $PQ=2r$, $[PQ]$ is a diameter, so $P$, $O$, $Q$ are
collinear and $P\hat{O}R=\pi-\theta$.

Triangle $POR$ has two sides $OP=OR=r$ with that angle between them:

$$[POR]=\tfrac12r^2\sin(\pi-\theta)=\boxed{\tfrac12r^2\sin\theta}$$

$\sin(\pi-\theta)=\sin\theta$ is the whole of the first shaded region, and
it is why the $\pi-\theta$ disappears.

The segment on $[RQ]$ is the sector $ROQ$ less the triangle $ROQ$:

$$\tfrac12r^2\theta-\tfrac12r^2\sin\theta
=\boxed{\tfrac12r^2(\theta-\sin\theta)}$$

Setting them equal, and cancelling $\tfrac12r^2$ — legitimate, $r>0$:

$$\sin\theta=\theta-\sin\theta\ \Longrightarrow\ \theta=2\sin\theta$$

Part (b) of the same question solves it, $\theta=1.90$, and the corpus
files that one mark under trigonometric equations, not here.

**6.2** Sector minus triangle, with $r=2$:

$$\tfrac12\cdot2^2\cdot\theta-\tfrac12\cdot2^2\sin\theta
=\boxed{2\theta-2\sin\theta}$$

$2(\theta-\sin\theta)$ is the same answer written better, and the check
takes either: it measures the figure at three angles and never looks at
the form.

---

## 7. A region with no name

**7.1** Cut it in two: the segment below $[AB]$, and the rectangle above.

The chord is the width of the gutter:

$$w=2\cdot12\sin\frac{2.08}{2}=24\sin1.04=20.6977\ldots$$

The segment:

$$\tfrac12\cdot12^2(2.08-\sin2.08)=72(2.08-0.873133\ldots)
=86.8944\ldots$$

The rectangle is $w\times10=206.977\ldots$, so

$$86.89+206.98=293.87\approx\boxed{294}\text{ cm}^2$$

Carrying $\theta=\tfrac{25}{12}$ instead of the rounded $2.08$ gives
$294.4$; both round to $294$, and the markscheme says as much. The other
dissection in the markscheme is *sector $+$ rectangle $-$ triangle*, and
it is the same three numbers rearranged.

**7.2** Both arcs turn through the same $5.2$ radians, so the “C” is one
sector minus another:

$$\tfrac12\cdot10^2\cdot5.2-\tfrac12r^2\cdot5.2
=260-2.6r^2\qquad\blacksquare$$

Two marks, and one of them is for seeing that the reflex angle is used
twice — the same $5.2$ in both terms.

**7.3** The disc outside the pentagon is five segments, one on each side.
With $r=\tfrac{30}{\pi}$ and $\theta=\tfrac{2\pi}{5}$:

$$5\cdot\tfrac12r^2(\theta-\sin\theta)
=2.5\times91.189\ldots\times(1.2566\ldots-0.95106\ldots)
=\boxed{69.7}\text{ cm}^2$$

The $\times5$ carries a mark of its own. The other route is the disc minus
the pentagon: $\pi r^2-5\cdot\tfrac12r^2\sin\theta
=286.5-216.8=69.7$, and it is worth doing once to see the two agree.

---

## 8. Two conditions instead of two numbers

**8.1** The logo is the rectangle less two segments, and §6.2 has the
segment:

$$5\times4-2\bigl(2\theta-2\sin\theta\bigr)=13.4$$
$$20-4\theta+4\sin\theta=13.4\ \Longrightarrow\ \theta-\sin\theta=1.65$$

No algebra will finish this. Graph $y=\theta-\sin\theta$ against
$y=1.65$, or solve numerically:

$$\theta=\boxed{2.36}\ (2.35673\ldots)$$

This is one of only two places in the whole topic where the calculator is
doing something a pencil could not.

**8.2 (i)** From §7.2 with the area given:

$$260-2.6r^2=64\ \Longrightarrow\ r^2=\frac{196}{2.6}=75.384\ldots
\ \Longrightarrow\ r=\boxed{8.68}\text{ cm}$$

The negative root is a radius, so it goes.

**(ii)** Walk round the “C”: the outer arc, the inner arc, and the two
straight ends that join them.

$$P=10(5.2)+r(5.2)+2(10-r)=52+45.148\ldots+2.6351\ldots
=\boxed{99.8}\text{ cm}$$

The two straight ends are the piece that gets forgotten, and the check
says *"only the arcs are counted"* when they are.

**8.3** Write both given measurements out:

$$2r+r\theta=10\qquad\text{and}\qquad\tfrac12r^2\theta=6.25$$

The first one gives what the cell asks for:

$$r\theta=10-2r\ \Longrightarrow\ \boxed{\theta=\frac{10-2r}{r}}$$

Put that into the second, written as $\tfrac12r\cdot(r\theta)$:

$$\tfrac12r(10-2r)=6.25\ \Longrightarrow\ 5r-r^2=6.25
\ \Longrightarrow\ 4r^2-20r+25=0\qquad\blacksquare$$

Eliminating $r$ instead of $\theta$ also works and is messier; the
markscheme allows it.

**8.4** The quadratic is a perfect square:

$$4r^2-20r+25=(2r-5)^2=0\ \Longrightarrow\ r=\boxed{\tfrac52}$$

There is only one root, so there is nothing to reject here — the one time
in this section that is true. Then

$$\theta=\frac{10-2(2.5)}{2.5}=\frac{5}{2.5}=\boxed{2}$$

Check both conditions: perimeter $=5+2.5\cdot2=10$ ✓, area
$=\tfrac12(2.5)^2\cdot2=6.25$ ✓.

**8.5** $P$ is a segment and $Q$ is the triangle on the same chord, and
together they are the sector. With $P:Q=3:5$,

$$\frac{\tfrac12r^2(\theta-\sin\theta)}{\tfrac12r^2\sin\theta}=\frac35
\ \Longrightarrow\ 5(\theta-\sin\theta)=3\sin\theta
\ \Longrightarrow\ 5\theta=8\sin\theta$$

The $r$ cancels, which is the point of giving a ratio. Solving
numerically on $(0,\pi)$:

$$\theta=\boxed{1.60}\ (1.59935\ldots)$$

Now the size comes from the $12.8$:

$$\tfrac12r^2(\theta-\sin\theta)=12.8
\ \Longrightarrow\ r^2=\frac{25.6}{0.599758\ldots}=42.684\ldots
\ \Longrightarrow\ r=\boxed{6.53}\text{ cm}$$

A useful check: the sector is $\tfrac83$ of the segment, $34.13$, and the
triangle is the other $\tfrac58$ of it, $21.33$ — and
$12.8:21.33=3:5$ ✓.

**8.6** The circumference of the circle is $2\pi(8)=16\pi$, so the
perimeter of the sector is $1.5\times16\pi=24\pi$:

$$2r+r\theta=24\pi\ \Longrightarrow\ r(\theta+2)=24\pi
\ \Longrightarrow\ \boxed{r=\frac{24\pi}{\theta+2}}\qquad\blacksquare$$

**8.7** Equal areas, with $r$ from part (a):

$$\tfrac12r^2\theta=\pi(8)^2\ \Longrightarrow\
\tfrac12\left(\frac{24\pi}{\theta+2}\right)^2\theta=64\pi$$
$$288\pi^2\theta=64\pi(\theta+2)^2
\ \Longrightarrow\ 4.5\pi\theta=(\theta+2)^2$$
$$\theta^2+(4-4.5\pi)\theta+4=0$$

The two roots are $0.411$ and $9.73$. The question said the angle at the
centre was **acute**, and $9.73$ is more than a full turn, so

$$\theta=\boxed{0.411}$$

Writing both down loses the last mark — *"Award (A1)(M1)A0 if additional
answers are given"* — and this is the one place in the notebook where the
check cannot help you: both roots really do build a sector of area
$64\pi$.

---

## 9. The circle leaves the plane

**9.1** Total surface is base plus curved:

$$\pi(2)^2+\pi(2)l=12\pi\ \Longrightarrow\ 4\pi+2\pi l=12\pi
\ \Longrightarrow\ l=\boxed{4}$$

Using $\pi Rl$ alone — the curved part only — gives $l=6$, and *total* was
the word in the question.

**9.2** Pythagoras first: $h=\sqrt{l^2-R^2}=\sqrt{16-4}=\sqrt{12}=2\sqrt3$.

$$V=\tfrac13\pi R^2h=\tfrac13\pi\cdot4\cdot2\sqrt3
=\boxed{\frac{8\sqrt3\,\pi}{3}}$$

Paper 1, so $14.5$ earns nothing. Dropping the $\tfrac13$ gives
$8\sqrt3\pi$, which is the cylinder of the same height, and the check
names it as that.

**9.3** The radius is $3$ from part (a). The height is the distance from
$V(-1,-1,0)$ to the centre $(-1,3,-2)$:

$$h=\sqrt{0^2+4^2+2^2}=\sqrt{20}=2\sqrt5$$

$$V=\tfrac13\pi(3)^2\sqrt{20}=3\pi\sqrt{20}=\boxed{6\sqrt5\,\pi}$$

The same $h$ comes out of the slant $VA=\sqrt{2^2+5^2}=\sqrt{29}$ with
$h=\sqrt{29-9}=\sqrt{20}$, which is the route the cell's figure takes.
"Exact" is not a suggestion on Paper 1: $42.1$ is not the answer.

**9.4** The line is $y=mx$ and the base of the cone is the circle it
sweeps at $x=h$, so the radius is the height of the line there:

$$r=\boxed{mh}$$

**9.5** The slant is the line itself, from $(0,0)$ to $(h,mh)$:

$$l=\sqrt{h^2+r^2}=\sqrt{h^2+m^2h^2}=\boxed{h\sqrt{1+m^2}}$$

Part (iii), which is not in this topic, then puts both into the integral
and gets $A=\pi rl$ — the formula from the booklet, derived.

**9.6** With $R=6.37262\ldots$ from part (a) and $h=20$:

$$V=\tfrac13\pi(6.37262\ldots)^2(20)=850.54\ldots=\boxed{851}\text{ m}^3$$

The markscheme also accepts $850$, from the rounded $R=6.37$ — worth
noticing, because it is the same question as §9.2 on the other paper and
there a decimal was worth nothing at all.

**9.7** Rolling changes nothing about the paper. The sector's arc becomes
the circle round the bottom of the cone:

$$\underbrace{19.5\cdot\frac{7\pi}{6}}_{\text{the arc}}
=\underbrace{2\pi R}_{\text{the base}}
\ \Longrightarrow\ R=\frac{22.75\pi}{2\pi}=\boxed{\tfrac{91}{8}}
=11.375\text{ cm}$$

The $\pi$ cancels, which is a sign the conversion has been done right: the
answer is a rational number even though the angle was not.
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
