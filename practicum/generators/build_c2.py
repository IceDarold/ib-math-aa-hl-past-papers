"""Собирает практикум C2: радианная мера, сектор, объёмные тела.

Десятый практикум серии на английском и второй в секции C. Лестница из
девяти приёмов идёт по тому, из чего складывают фигуру: сначала дуга
и сектор, потом хорда и сегмент, потом составная область, потом обратная
задача — мера дана, найти фигуру, — и напоследок круг выходит из
плоскости и становится конусом.

Проверка здесь одна новая, и она же пятнадцатое понятие равенства
ответов в серии: **фигуру измеряют**.

Эталона нет. Ноутбук передаёт проверке не ответ и не метод, а границу
фигуры: где идут дуги и где отрезки. `verify_area` берёт площадь формулой
Грина по этому контуру, `verify_perimeter` и `verify_length` складывают
длины кусков, `verify_volume` вращает сечение и применяет теорему Паппа.
Формул темы — ½r²θ, ½r²(θ − sin θ), ⅓πr²h — у проверки нет ни одной,
и потому 3549π/16, 696.844 и 697 проходят одинаково.

Проверка работает в обе стороны, и в этой теме это важнее, чем в
предыдущих. Прямой ход: фигура известна, ответ — её мера. Обратный:
мера известна, а фигуру строят из ответа, и она обязана этой мере
отвечать. Так проверяется «найдите угол» — ваш угол натягивает дугу
в 10 см или не натягивает, — и так же «найдите радиус».

Отсюда же follow through. Ширина жёлоба в задании 11 считается из
найденного вами угла, высота конуса в задании 12 — из найденной вами
образующей. Неверный первый пункт роняет только себя, ровно как
в схеме оценивания.

`verify_law` — для ответа-выражения: «find the area of one of the shaded
segments in terms of θ». Сверять такое с записанным ½r²(θ − sin θ)
значило бы сверять запись, поэтому проверка берёт несколько значений θ,
строит фигуру при каждом и меряет.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не
попадает — practicum/tests/verify_c2.py прогоняет по нему весь ноутбук
и требует, чтобы каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(ROOT,
                        'practicum/geometry/practicum-c2-circular-measure.ipynb')

TRIGGER = {1: 'arc', 2: 'perimeter', 3: 'sector', 4: 'chord', 5: 'segment',
           6: 'region', 7: 'rate', 8: 'cone', 9: 'unknown', 10: 'sector',
           11: 'cone', 12: 'arc'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '18',
    'q1b': 'Rational(5, 2)',
    'q1c': '20',
    'q2th': '2*pi/5',
    'q2r': '30/pi',
    'q2b': '69.6640',
    'q3a': '3549*pi/16',
    'q3b': 'Rational(91, 8)',
    'q4a': '8.13416',
    'q4b': '54.7898',
    'q5r': '9.38463',
    'q5b': '35.4099',
    'q6a': '2*th - 2*sin(th)',
    'q6b': '2.35673',
    'q7': '[1.90]',
    'q8r': 'Rational(5, 2)',
    'q8th': '2',
    'q9r': '8.68243',
    'q9p': '99.7838',
    'q10': '0.411273',
    'q11a': '2.08',
    'q11b': '294',
    'q12a': '4',
    'q12b': '8*sqrt(3)*pi/3',
    'q12c': '851',
    'q13c': '4.05093',
    'qt_th': '1.59935',
    'qt_r': '6.53330',
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
# C2 — Radian measure, sectors, solids

**105 marks of the archive, nine techniques, thirteen tasks.** Two topics
that are really one: everything the archive asks about circular measure,
and everything it asks about solids — which turns out to be cones, and
cones come from sectors.

## The one idea

A radian is not another scale for angle. It is a **definition of angle as
a length**:

$$\theta=\frac{\text{arc}}{\text{radius}}$$

Read that once more, because the whole topic is inside it. The angle *is*
the number of radii that fit along the arc. Multiply both sides by $r$ and
you have $s=r\theta$ — not a formula to remember, but the same sentence
written with a multiplication sign.

Everything else follows in one step. A full turn is $2\pi r/r=2\pi$. A
sector is the fraction $\theta/2\pi$ of the disc, so its area is
$\frac{\theta}{2\pi}\cdot\pi r^2=\tfrac12r^2\theta$.

And this is exactly why **degrees may not be substituted**. What goes into
these formulas is not an angle, it is a ratio of two lengths. A degree has
no such ratio; it is $\tfrac1{360}$ of a convention.

## The other idea

After that, the topic stops being about circles at all. Every remaining
question is one move:

> **Cut the shaded shape into pieces whose measure you already know.**

A segment is a sector minus a triangle. A logo is a rectangle minus two
segments. A gutter is a segment plus a rectangle. The letter C is a sector
minus a sector. That work happens on the diagram, before any button is
pressed, and the ladder below is a list of pieces, not of formulas.

## How the checks work

They do not know the answers, and they do not know the formulas. Each
check is handed the **boundary of the figure** — where the arcs run and
where the straight edges run — and it measures:

```python
verify_area('1c', q1c, *sector(4, 0, q1b))
```

is *"the shaded sector of the paper — the one with radius 4 and your
angle — how big is it?"* The area comes out of a contour integral;
$\tfrac12r^2\theta$ appears nowhere, so any correct form of the answer
passes: $\tfrac{3549\pi}{16}$, $696.844$ and $697$ are the same answer.

**The checks run in both directions, and you will use both.**

| direction | what is known | what carries your answer |
|---|---|---|
| forward | the figure | the measurement |
| backward | the measurement | the figure |

Backward looks like this:

```python
verify_length('1b', 10, arc((0, 0), 4, 0, q1b))
```

— *"the arc of radius 4 through your angle: is it 10 cm long?"* That is
how *find the angle* and *find the radius* get checked without any answer
being stored.

One thing measuring cannot do: reject a root that the *situation*
forbids. In task 10 both solutions of the quadratic make a genuine sector
of the right area, and only the question knows that the angle was said to
be acute. That mark is yours; the check will not withhold it. The same
gap is flagged where it occurs.

A consequence worth having: **figures may be built from your own earlier
answers.** In task 11 the width of the gutter comes from the angle you
found; in task 12 the height of the cone comes from the slant height you
found. A wrong first part therefore costs you the first part only — which
is what a markscheme calls follow through.

When you are wrong the check says **how**, and every diagnosis is built
from the same contour:

| what you wrote | what the check says |
|---|---|
| the polygon through the arc's ends | the arc has been read as a chord |
| the whole sector | a segment is the sector minus the triangle |
| the triangle | that is the triangle on the same chord |
| the arc alone | the boundary has straight pieces too |
| the other way round the circle | minor instead of major |
| one of several equal pieces | the figure has $n$ of them |
| $180/\pi$ times the answer | the angle went in as degrees |
| the area of the cross-section | that is the section, not the solid |
| three times the answer | the factor of $\tfrac13$ is missing |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | one measurement, one formula | 1–3 |
| 🟡 | the shape has to be cut up first | 4–8, 12–13 |
| 🔴 | the measurement is given and the shape is not | 9–11 |

Every task is a real past-paper question, cited.

**77% of these marks are on a calculator paper, and the number flatters
it.** Twelve of the thirteen tasks need nothing from the machine but
arithmetic: there is no button for *the shaded part is a rectangle minus
two segments*. The exception is task 6, where the equation
$\theta-\sin\theta=c$ comes out and no algebra will solve it — and that
equation, with the one like it in the timer, is 9 marks out of 105.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + sin, cos, pi, sqrt, arc, seg, cone, ...

language('en')                 # this notebook is in English, and so are the checks

th = symbols('theta')          # the letter every one of these papers uses
DEGREE = pi / 180              # so that 210*DEGREE reads as '210 degrees'


# Every figure below may be drawn from an answer you have not written yet.
# undrawn(...) returns an empty boundary in that case, so the notebook runs
# top to bottom while it is still blank and the checks print a white square.

def point(radius, angle, centre=(0, 0)):
    # the point of the circle at that angle
    if undrawn(radius, angle):
        return (Ellipsis, Ellipsis)
    return (centre[0] + radius * cos(angle), centre[1] + radius * sin(angle))


def sector(radius, start, end, centre=(0, 0)):
    # the boundary of a sector: out along one radius, round, back along the other
    return undrawn(radius, start, end) or (
        seg(centre, point(radius, start, centre)),
        arc(centre, radius, start, end),
        seg(point(radius, end, centre), centre))


def segment(radius, start, end, centre=(0, 0)):
    # the boundary of a segment: round the arc, back along the chord
    return undrawn(radius, start, end) or (
        arc(centre, radius, start, end),
        seg(point(radius, end, centre), point(radius, start, centre)))


def fan(radius, angle, count):
    # count copies of the same sector, laid round the centre one after another
    if undrawn(radius, angle):
        return undrawn(radius, angle)
    return [i for k in range(count) for i in segment(radius, k * angle, (k + 1) * angle)]


print('ready; sympy', sp.__version__)
print('exact:      ', 3549 * pi / 16)
print('to 3 s.f.:  ', sig(3549 * pi / 16, 3))
print('a figure:   ', len(sector(4, 0, Rational(5, 2))), 'pieces')
""")

md(r"""
---
## Map of the nine techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | radians and arc length | two of $s$, $r$, $\theta$ are given | $s=r\theta$ |
| 2 | angle against time | *one revolution every 16 seconds* | $\omega=2\pi/T$, then technique 1 |
| 3 | perimeter of a sector | the word *perimeter* beside an arc | walk the boundary and add |
| 4 | area of a sector | a shaded slice of pie | $\tfrac12r^2\theta$ |
| 5 | chord and half-angle | a chord, or a distance from the centre | drop a perpendicular; a right triangle |
| 6 | area of a segment | one straight side, not two | sector minus triangle |
| 7 | a composite region | the shape has no name | cut into 4, 5, 6 and add |
| 8 | two conditions, no numbers | neither $r$ nor $\theta$ is given | eliminate, solve, reject a root |
| 9 | the circle leaves the plane | a cone | arc becomes circumference; Pythagoras |

Techniques 1–4 are one idea applied four times. Technique 5 is C1 walking
in: the perpendicular from the centre to a chord makes a right triangle,
and everything about chords comes out of it. Technique 6 is the first
subtraction and technique 7 is all the others. Technique 8 turns the topic
round — you are given the measurement and asked for the shape — and
technique 9 leaves the page.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. The arc *is* the angle

## Theory: one definition, four consequences

Put an arc of length $s$ on a circle of radius $r$. The angle it subtends
at the centre, **measured in radians**, is defined as

$$\theta=\frac{s}{r}\qquad\Longleftrightarrow\qquad s=r\theta$$

Four things come straight out of it, and they are the whole of Part 1.

**A full turn is $2\pi$.** The whole circumference is $2\pi r$, so
$\theta=2\pi r/r=2\pi$. Hence $180^\circ=\pi$, and hence degrees convert
by $\times\pi/180$.

**A sector is a fraction of the disc.** The slice at angle $\theta$ is
$\theta/2\pi$ of the whole, so

$$A=\frac{\theta}{2\pi}\cdot\pi r^2=\tfrac12r^2\theta$$

**The perimeter of a sector is not the arc.** Walk round the shaded slice
with your finger: out along a radius, round the arc, back along the other
radius. Three pieces:

$$P=r\theta+2r$$

The paper asks for this and marks it separately. May 2023 TZ2 gives it a
whole mark of its own: *"arc + 2 × radius"*.

**The larger sector uses $2\pi-\theta$.** If the shaded piece is the big
one, the angle in the formula is the reflex angle, and reading it off the
diagram is the only step that can go wrong.

### The degrees trap is not a rounding error

Substituting degrees into $\tfrac12r^2\theta$ does not give a slightly
wrong answer; it gives one that is $180/\pi\approx57$ times too big. The
markscheme of November 2021 Paper 2 is explicit about the price:

> *"Award a maximum of M1A1A0A0A0 if a candidate uses degrees, even if
> later work is correct."*

Two marks out of five for a completely correct method.
""")

md(r"""
### Task 1 🟢 — *May 2023 TZ2 Paper 1 Q1, 6 marks*

The following diagram shows a circle with centre $O$ and radius $4$ cm.
The points $P$, $Q$ and $R$ lie on the circumference and
$P\hat{O}R=\theta$, measured in radians. The shaded sector is $POR$, and
**the length of arc $PQR$ is $10$ cm**.

**(a)** Find the perimeter of the shaded sector.
**(b)** Find $\theta$.
**(c)** Find the area of the shaded sector.

*Paper 1: no calculator, and none is needed. Notice that (a) can be
answered before (b) — the arc is already given to you.*
""")

code(r"""
q1a = ...        # the perimeter, in cm
q1b = ...        # the angle, in radians
q1c = ...        # the area, in cm^2

shaded = sector(4, 0, q1b)                 # your angle, drawn

verify_length('1b', 10, arc((0, 0), 4, 0, q1b))    # is your arc 10 cm long?
verify_perimeter('1a', q1a, *shaded)
verify_area('1c', q1c, *shaded)
""")

md(r"""
### Task 2 🟢 — *November 2025 TZ1 Paper 2 Q1, 6 marks*

A regular pentagon is inscribed in a circle with centre $O$ and radius
$r$ cm. The angle $A\hat{O}B$ is $\theta$, and **arc $AB$ is $12$ cm**.

**(a)** Find **(i)** $\theta$; **(ii)** $r$.
**(b)** Find the area of the shaded region — the five pieces of the disc
left outside the pentagon.

*The first check draws five arcs like yours, one after another. If your
angle is right they close the circle; if it is not, they do not, and the
check says so in those words.*
""")

code(r"""
q2th = ...       # the angle at the centre, in radians
q2r  = ...       # the radius, in cm
q2b  = ...       # the shaded area, in cm^2

def rim(radius, angle):
    # five arcs like yours, laid one after another round the centre
    return undrawn(radius, angle) or [
        arc((0, 0), radius, k * angle, (k + 1) * angle) for k in range(5)]


verify_perimeter('2a', 5 * 12, *rim(q2r, q2th))   # five arcs of 12 cm, right round
verify_area('2b', q2b, *fan(q2r, q2th, 5))
""")

md(r"""
### Task 3 🟢 — *May 2025 TZ1 Paper 2 Q1, 6 marks*

The points $A$ and $B$ lie on a circle with centre $O$ and radius
$19.5$ cm, such that $B\hat{O}A=210^\circ$. A piece of paper is cut into
the shape of the sector $BOA$. A hollow cone with no base is then made
from that sector by joining $A$ to $B$; the sector becomes the curved
surface of the cone.

**(a)** Find the area of the sector $BOA$.
**(b)** Find the radius of the cone.

*Two different things happen to the same number here. In (a) the $210^\circ$
becomes an angle in radians; in (b) the arc it cuts becomes a circle of a
different radius. Nothing about the paper changes when you roll it: the
cut edge keeps its length.*
""")

code(r"""
q3a = ...        # the area of the sector, in cm^2
q3b = ...        # the radius of the cone's base, in cm

CUT = 19.5 * 210 * DEGREE        # the curved edge of the paper sector

verify_area('3a', q3a, *sector(19.5, 0, 210 * DEGREE))
verify_length('3b', CUT, arc((0, 0), q3b, 0, 2 * pi))   # the same edge, joined up
""")

# ================================================================= теория 2
md(r"""
---
# 🟡 Part 2. Chords and segments

## Theory: the perpendicular from the centre

Draw a chord $[AB]$ in a circle of radius $r$, with $A\hat{O}B=\theta$.
Drop a perpendicular from $O$ to the chord, meeting it at $M$. That single
line does three things at once:

- it **bisects the chord**: $AM=MB$;
- it **bisects the angle**: $A\hat{O}M=\theta/2$;
- it makes a **right-angled triangle** $OMA$ with hypotenuse $r$.

From that triangle, everything about chords:

$$AB=2r\sin\frac{\theta}{2},\qquad OM=r\cos\frac{\theta}{2},\qquad
\theta=2\arccos\frac{OM}{r}$$

The cosine rule gives the first of these too — $AB^2=r^2+r^2-2r^2\cos\theta$
— and the markscheme accepts either. The right triangle is usually shorter,
and it is the only route when what you are given is the distance $OM$.

> The mark that gets dropped here is the **doubling**. You find $AM$, or
> you find $\theta/2$, and then you write it down. May 2024 TZ2 gives
> *"recognizes that $AB=2AM$"* its own mark.

## Theory: a segment is a sector minus a triangle

The region between a chord and its arc has no formula of its own. It is a
subtraction, and both parts you already have:

$$\underbrace{\tfrac12r^2\theta}_{\text{sector }OAB}
-\underbrace{\tfrac12r^2\sin\theta}_{\text{triangle }OAB}
=\tfrac12r^2(\theta-\sin\theta)$$

The triangle's area is $\tfrac12ab\sin C$ from C1, with both sides equal
to $r$.

Three numbers live in that one line — sector, triangle, difference — and
the markscheme distinguishes them. So does the check: give it the sector
and it will tell you that a segment is the sector minus the triangle; give
it the triangle and it will say so.

> **The mixed-mode error.** In $\tfrac12r^2(\theta-\sin\theta)$ the letter
> $\theta$ appears twice: once as a number, once inside a sine. If your
> calculator is in degrees, the first is right and the second is wrong,
> and the answer is neither one thing nor the other. This is the quietest
> mistake in the topic.
""")

md(r"""
### Task 4 🟡 — *May 2022 TZ2 Paper 2 Q1, 6 marks*

The following diagram shows a circle with centre $O$ and radius $5$ metres.
Points $A$ and $B$ lie on the circle and $A\hat{O}B=1.9$ radians. **The
shaded sector is the larger one.**

**(a)** Find the length of the chord $[AB]$.
**(b)** Find the area of the shaded sector.
""")

code(r"""
q4a = ...        # the chord, in m
q4b = ...        # the shaded area, in m^2

A4, B4 = point(5, 0), point(5, 1.9)

verify_length('4a', q4a, seg(A4, B4))
verify_area('4b', q4b, *sector(5, 1.9, 2 * pi))    # from B all the way round to A
""")

md(r"""
### Task 5 🟡 — *May 2025 TZ3 Paper 2 Q4, 5 marks*

Points $A$, $B$ and $C$ lie on a circle with centre $O$. The area of
triangle $AOB$ is $26$ cm$^2$ and $A\hat{O}B=2.51$ radians. $C$ lies on
the major arc.

Find the radius of the circle, and hence the length of arc $ACB$.

*The paper asks only for the arc; the markscheme scores the radius on the
way. Both are asked here, because a wrong radius and a wrong arc are two
different mistakes and it is worth knowing which one you made.*
""")

code(r"""
q5r = ...        # the radius, in cm
q5b = ...        # the length of the major arc ACB, in cm

def triangle(radius, angle):
    # the triangle AOB: two radii and the chord between their ends
    return undrawn(radius, angle) or (
        seg((0, 0), point(radius, 0)),
        seg(point(radius, 0), point(radius, angle)),
        seg(point(radius, angle), (0, 0)))


verify_area('5 (radius)', 26, *triangle(q5r, 2.51))            # triangle AOB
verify_length('5 (arc)', q5b, arc((0, 0), q5r, 2.51, 2 * pi))
""")

md(r"""
### Task 6 🟡 — *May 2022 TZ1 Paper 2 Q2, 6 marks*

A logo is created by removing two equal segments from a rectangle
measuring $5$ cm by $4$ cm. The points $A$ and $B$ lie on a circle with
centre $O$ and radius $2$ cm, such that $A\hat{O}B=\theta$, where
$0<\theta<\pi$. One segment is removed from each of the two long sides.

**(a)** Find the area of one of the shaded segments **in terms of
$\theta$**.
**(b)** Given that the area of the logo is $13.4$ cm$^2$, find the value
of $\theta$.

*Part (a) is checked by measuring the segment at three different angles,
so any correct form passes. Part (b) is the one place in this notebook
where the equation cannot be solved by hand — use a graph.*
""")

code(r"""
def one_segment(angle):
    # the segment cut off a circle of radius 2 by a chord at that angle
    return segment(2, 0, angle)


def logo(angle):
    # the rectangle, 4 wide and 5 tall, with a segment bitten out of each side
    if undrawn(angle):
        return undrawn(angle)
    half = angle / 2
    away, high = 2 * cos(half), 2 * sin(half)      # centre to chord, half-chord
    left, right = (-away, Rational(5, 2)), (4 + away, Rational(5, 2))
    low_l, top_l = (0, Rational(5, 2) - high), (0, Rational(5, 2) + high)
    low_r, top_r = (4, Rational(5, 2) - high), (4, Rational(5, 2) + high)
    return (seg((0, 0), (4, 0)), seg((4, 0), low_r),
            arc(right, 2, pi + half, pi - half),
            seg(top_r, (4, 5)), seg((4, 5), (0, 5)), seg((0, 5), top_l),
            arc(left, 2, half, -half),
            seg(low_l, (0, 0)))


q6a = ...        # the area of one segment, in terms of th
q6b = ...        # the angle, in radians

verify_law('6a', q6a, th, one_segment, (0.7, 1.9, 2.8))
verify_area('6b', 13.4, *logo(q6b))       # does your angle leave 13.4 cm^2?
""")

md(r"""
### Task 7 🟡 — *November 2021 Paper 2 Q4, 6 marks*

The following diagram shows a semicircle with centre $O$ and radius $r$.
Points $P$, $Q$ and $R$ lie on the circumference, such that $PQ=2r$ and
$R\hat{O}Q=\theta$, where $0<\theta<\pi$. Two regions are shaded: the
triangle $POR$, and the segment between the chord $[RQ]$ and its arc.

**(a)** Given that the areas of the two shaded regions are equal, show
that $\theta=2\sin\theta$.
**(b)** Hence determine the value of $\theta$.

*Part (a) is a show that — do it on paper, and the derivation is in the
solutions. Part (b) starts from the equation (a) gives you, and the check
scans the whole interval: a root is not enough, it has to be all of them.*
""")

code(r"""
q7 = [...]       # every value of theta in (0, pi), as a list

# Three significant figures is what the paper asks for, and a number
# rounded that far does not satisfy the equation exactly. The tolerance
# is what the exam accepts, not what sympy would.
verify_roots('7', q7, th - 2 * sin(th), (0.1, pi), var=th, tol=1e-2)
""")

md(r"""
### Task 8 🟡 — *May 2024 TZ1 Paper 1 Q3, 8 marks*

Points $A$ and $B$ lie on the circumference of a circle of radius $r$ cm
with centre $O$. The angle $A\hat{O}B$ is $\theta$, measured in radians.
**The perimeter of the sector is $10$ cm and its area is $6.25$ cm$^2$.**

**(a)** Show that $4r^2-20r+25=0$.
**(b)** Hence, or otherwise, find the value of $r$ and the value of
$\theta$.

*Paper 1, and the last 🟡 before the shapes stop having names. Part (a) is
a show that; part (b) is checked by drawing your sector and measuring it
twice — its perimeter and its area are both given in the question.*
""")

code(r"""
q8r  = ...       # the radius, in cm
q8th = ...       # the angle, in radians

mine = sector(q8r, 0, q8th)

verify_perimeter('8 (perimeter)', 10, *mine)
verify_area('8 (area)', 6.25, *mine)
""")

# ================================================================= теория 3
md(r"""
---
# 🔴 Part 3. The measurement is given; find the shape

## Theory: cut the shape into pieces that have names

None of the shapes below is a sector, a segment or a triangle. All of them
are sums and differences of those:

| the shape | what it is made of |
|---|---|
| a logo: rectangle with two bites | rectangle $-$ 2 segments |
| the letter C between two circles | sector of radius $R$ $-$ sector of radius $r$ |
| a gutter's cross-section | segment $+$ rectangle |
| a disc outside an inscribed pentagon | 5 segments |

Two rules make the cutting reliable.

**Write each piece on its own line, with its own sign.** The arithmetic is
never the difficulty; keeping track of what has been added and what
subtracted is.

**Count the repeats before you finish.** Five segments, two bites, two
vertical sides. The markscheme of November 2025 TZ1 gives a separate mark
for the $\times5$.

The markscheme of the gutter question is unusually frank about all this:

> *"There are many different ways to dissect the cross-section to
> determine its area."*

They all give the same number, and choosing one is drawing, not
calculating.

## Theory: two conditions instead of two numbers

The hardest questions in the topic give you no $r$ and no $\theta$. They
give you two *measurements* — a perimeter and an area, an area and a
ratio — and both of those are expressions in $r$ and $\theta$. Two
equations, two unknowns:

$$2r+r\theta=10\qquad\text{and}\qquad\tfrac12r^2\theta=6.25$$

The first one gives $r\theta=10-2r$. Put that into the second, written as
$\tfrac12r\cdot(r\theta)$:

$$\tfrac12r(10-2r)=6.25\ \Longrightarrow\ 4r^2-20r+25=0$$

Eliminate the one you are not asked for; solve what is left; and then do
the step that carries its own mark:

> **Reject the root the question forbids.** *"Award (A1)(M1)A0 if
> additional answers are given"* — November 2025 TZ3. The circle does not
> care that $\theta=9.73$ solves the quadratic; the question said the
> angle was acute.

Sometimes what is left is not a quadratic at all. $20-4\theta+4\sin\theta
=13.4$ has no algebraic solution, and none is expected: this is where the
calculator finally does something a pencil cannot.
""")

md(r"""
### Task 9 🔴 — *November 2023 Paper 2 Q3, 7 marks*

A logo is a letter “C” formed between two circles with centre $O$. The
point $A$ lies on the inner circle, radius $r$ cm, where $r<10$; the point
$B$ lies on the outer circle, radius $10$ cm. **The reflex angle
$A\hat{O}B$ is $5.2$ radians**, and the C is the shaded region between the
two arcs.

**(a)** Show that the area of the C is $260-2.6r^2$.
**(b)** Given that the area of the C is $64$ cm$^2$, find **(i)** the
value of $r$; **(ii)** the perimeter of the C.

*Part (a) is a show that. In (b) the figure is built from your own $r$,
so if (i) is wrong then (ii) is judged against the C you actually drew.*
""")

code(r"""
def letter_c(inner):
    # the region between two arcs of 5.2 radians, plus the two straight ends
    return undrawn(inner) or (
            seg((inner, 0), (10, 0)),
            arc((0, 0), 10, 0, 5.2),
            seg(point(10, 5.2), point(inner, 5.2)),
            arc((0, 0), inner, 5.2, 0))


q9r = ...        # the inner radius, in cm
q9p = ...        # the perimeter of the C, in cm

verify_area('9 (radius)', 64, *letter_c(q9r))
verify_perimeter('9 (perimeter)', q9p, *letter_c(q9r))
""")

md(r"""
### Task 10 🔴 — *November 2025 TZ3 Paper 2 Q3, 6 marks*

Consider a circle of radius $8$ mm and a sector of radius $r$ mm whose
acute angle at the centre is $\theta$ radians. **The perimeter of the
sector is $1.5$ times the circumference of the circle.**

**(a)** Show that $r=\dfrac{24\pi}{\theta+2}$.
**(b)** It is given that the area of the circle is the same as the area of
the sector. Determine the value of $\theta$.

*The quadratic in (b) has two roots and only one of them is acute. Write
down the acute one, and only that one.*

> **Where the check is softer than the exam.** Both roots build a real
> sector, and both sectors have exactly the area asked for — they are
> simply different sectors. Measuring cannot tell them apart, so the check
> will accept $9.73$. The markscheme will not: *"Award (A1)(M1)A0 if
> additional answers are given."* That mark is yours to earn on your own.
""")

code(r"""
def from_part_a(angle):
    # part (a) gives the radius, so your angle draws the whole sector
    return undrawn(angle) or sector(24 * pi / (angle + 2), 0, angle)


q10 = ...        # the angle, in radians

verify_area('10', pi * 8 ** 2, *from_part_a(q10))   # equal to the circle
""")

md(r"""
### Task 11 🔴 — *May 2023 TZ1 Paper 2 Q10(a)(b), 10 marks*

A gutter is made by folding a sheet of metal $45$ cm wide. Its
cross-section is shaded in the diagram: arc $AB$ lies on a circle with
centre $O$ and radius $12$ cm, the two vertical sides above $A$ and $B$
are $10$ cm high, and the width of the gutter is $w$ cm. Let
$A\hat{O}B=\theta$, where $0<\theta<\pi$.

**(a)** Show that $\theta=2.08$, correct to three significant figures.
**(b)** Find the area of the cross-section of the gutter.

*The whole $45$ cm of metal is the boundary of the cross-section except
the open top: up one side, round the arc, up the other. That is what the
first check walks along. The second measures the shape your angle makes.*
""")

code(r"""
def corners(angle):
    # A and B at the ends of the arc, C and D ten centimetres above them
    low, high = -pi / 2 - angle / 2, -pi / 2 + angle / 2
    A11, B11 = point(12, low), point(12, high)
    return A11, B11, (B11[0], B11[1] + 10), (A11[0], A11[1] + 10)


def gutter(angle):
    # the cross-section: the arc below AB, and the rectangle above it
    if undrawn(angle):
        return undrawn(angle)
    A11, B11, C11, D11 = corners(angle)
    return (arc((0, 0), 12, -pi / 2 - angle / 2, -pi / 2 + angle / 2),
            seg(B11, C11), seg(C11, D11), seg(D11, A11))


def metal(angle):
    # the sheet: down one side, round the arc, up the other. The top is open.
    if undrawn(angle):
        return undrawn(angle)
    A11, B11, C11, D11 = corners(angle)
    return (seg(D11, A11), gutter(angle)[0], seg(B11, C11))


q11a = ...       # the angle, in radians
q11b = ...       # the area of the cross-section, in cm^2

verify_length('11a', 45, *metal(q11a))
verify_area('11b', q11b, *gutter(q11a))
""")

# ================================================================= теория 4
md(r"""
---
# 🟡 Part 4. The circle leaves the plane

## Theory: a cone is a rolled-up sector

Cut a sector of radius $l$ out of paper and join its two straight edges.
The result is a cone with no base, and **nothing about the paper has
changed**: the radius of the sector is now the slant height, and the arc
is now the circle round the bottom.

$$\underbrace{l\theta}_{\text{the arc}}=\underbrace{2\pi R}_{\text{the base circle}}$$

That single equation is the whole of the conversion, and it is why the
curved surface area of a cone is $\pi Rl$ and not something you have to
remember: the sector's area is $\tfrac12l^2\theta=\tfrac12l\cdot l\theta
=\tfrac12l\cdot2\pi R=\pi Rl$.

The rest is Pythagoras and one formula from the booklet:

$$l^2=R^2+h^2,\qquad V=\tfrac13\pi R^2h,\qquad
S_{\text{total}}=\underbrace{\pi R^2}_{\text{base}}+\underbrace{\pi Rl}_{\text{curved}}$$

> **Two traps, and both are about what is included.** *Total* surface area
> has the base in it; *curved* surface area does not. And the $\tfrac13$
> in the volume is the difference between a cone and the cylinder around
> it — the check will tell you if you have dropped it, in exactly those
> words.

## The same solid on the two papers

The archive gives this technique on both papers, and the difference is
only in the shape of the answer.

| | May 2021 TZ2 Paper 1 | May 2024 TZ1 Paper 2 |
|---|---|---|
| given | $R=2$, total surface $12\pi$ | $h=20$, $R$ from part (a) |
| work | $4\pi+2\pi l=12\pi$; $h=\sqrt{16-4}$ | substitute |
| answer | $\dfrac{8\sqrt3\,\pi}{3}$ | $851$ m$^3$ |

Same formulas, same two lines of work. On Paper 1 a decimal earns nothing;
on Paper 2 three significant figures are expected. The mathematics does
not notice which paper it is on — but the markscheme does.
""")

md(r"""
### Task 12 🟡 — *May 2021 TZ2 Paper 1 Q10(c)(d) and May 2024 TZ1 Paper 2 Q2(b), 9 marks*

**A right cone has a total surface area of $12\pi$, base radius $2$,
height $h$ and slant height $l$.**

**(a)** Find the value of $l$.
**(b)** Hence find the volume of the cone. *Give an exact answer.*

**A monument is a right cone of vertical height $20$ m. Part (a) of that
question gives the base radius as $6.37$ m.**

**(c)** Find the volume of the monument.

*The check in (a) unrolls the cone: a disc for the base, and the sector
that the curved surface came from. In (b) and (c) the solid is spun out of
its own cross-section, so no volume formula is stored anywhere.*
""")

code(r"""
q12a = ...       # the slant height l
q12b = ...       # the volume of the cone, exactly
q12c = ...       # the volume of the monument, in m^3

def unrolled(slant):
    # the cone opened out flat: the base disc, and the sector it came from
    return undrawn(slant) or (
        (arc((0, 0), 2, 0, 2 * pi),) + sector(slant, 0, 2 * pi * 2 / slant))


verify_area('12a', 12 * pi, *unrolled(q12a))

verify_volume('12b', q12b, *cone(radius=2, slant=q12a), exact=True)
verify_volume('12c', q12c, *cone(radius=6.37262, height=20))
""")

md(r"""
### Task 13 🟡 — *May 2024 TZ2 Paper 2 Q11(a)–(d), 9 marks*

A rotating sprinkler at a fixed point $S$ waters every point inside a
circle of radius $20$ m. $S$ is $14$ m from the edge of a straight path,
and that edge meets the circle at $A$ and $B$.

**(a)** Show that $AB=28.57$, correct to four significant figures.
**(b)** The sprinkler makes one revolution every $16$ seconds. Show that
it turns through $\dfrac{\pi}{8}$ radians in one second.
**(c)** Let $T$ seconds be the time for which $[AB]$ is watered in each
revolution. Find the value of $T$.
**(d)** At $t=0$ the water crosses the path at $A$; at time $t$ it crosses
at $D$. Write down an expression for $\alpha=A\hat{S}D$ in terms of $t$.

*(a), (b) and (d) print their own answers, so only (c) is checked — and it
is checked with the two numbers (a) and (b) hand you. Your $T$ seconds
turn the jet through some angle; the chord it cuts must be the $28.57$ m
of part (a).*
""")

code(r"""
def jet(seconds):
    # the chord between where the jet crosses the path and where it leaves
    if undrawn(seconds):
        return undrawn(seconds)
    swept = seconds * pi / 8                # the angle your T seconds turns through
    return (seg(point(20, -swept / 2), point(20, swept / 2)),)


q13c = ...       # the time, in seconds

verify_length('13c', 28.5657, *jet(q13c))
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would
make first**.

| code | technique |
| --- | --- |
| `arc` | two of $s$, $r$, $\theta$ are known; use $s=r\theta$ |
| `rate` | something turns; find $\omega=2\pi/T$ first |
| `perimeter` | walk the boundary: arc plus the straight pieces |
| `sector` | $\tfrac12r^2\theta$, with the right $\theta$ |
| `chord` | drop the perpendicular; a right triangle |
| `segment` | sector minus triangle |
| `region` | cut the shape into named pieces and add |
| `unknown` | two conditions, eliminate, solve, reject a root |
| `cone` | the arc becomes a circumference; Pythagoras |

1. A sector of a circle of radius $4$ cm has an arc of length $10$ cm. Find the angle at the centre.
2. Find the perimeter of a sector of radius $4$ cm whose arc is $10$ cm long.
3. A circle has radius $5$ m and $A\hat{O}B=1.9$. Find the area of the larger of the two sectors.
4. A circle has radius $5$ m and $A\hat{O}B=1.9$. Find the length of the chord $[AB]$.
5. Find the area of the region between a chord $[AB]$ and its arc, given $r=2$ and $A\hat{O}B=\theta$.
6. Find the area of a logo made by removing two equal segments from a $5$ cm by $4$ cm rectangle.
7. A sprinkler makes one revolution every $16$ seconds. Find the angle it turns through in one second.
8. A paper sector of radius $19.5$ cm is rolled up until its straight edges meet. Find the radius of the base.
9. The perimeter of a sector is $10$ cm and its area is $6.25$ cm$^2$. Find $r$ and $\theta$.
10. Convert $210^\circ$ into radians and find the area of the sector of radius $19.5$ cm.
11. Find the volume of a right cone with base radius $2$ and slant height $4$.
12. The Earth is a sphere of radius $6000$ km, and the shortest distance from $M$ to $N$ across its surface is $6000$ km. Find the angle $M\hat{O}N$.
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
## On the clock — *May 2025 TZ2 Paper 2 Q6, 6 marks*

**Six marks, nine minutes.** No hints this time.

The following diagram shows a circle with centre $O$ and radius $r$ cm.
Points $A$ and $B$ lie on the circle and $A\hat{O}B=\theta$ radians. The
sector $OAB$ is divided into two regions: a shaded segment $P$ and a
triangle $Q$.

The area of the shaded segment $P$ is $12.8$ cm$^2$, and the areas of $P$
and $Q$ are in the ratio $3:5$.

Find the value of $\theta$ and the value of $r$.

*The paper asks only for $r$; the markscheme finds $\theta$ first and
scores it. Both are asked here.*

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_th = ...      # the angle, in radians
qt_r  = ...      # the radius, in cm

# the shaded segment is 12.8; segment and triangle together fill the
# sector, so the segment is three eighths of it
verify_area('timer, segment', 12.8, *segment(qt_r, 0, qt_th))
verify_area('timer, sector', 12.8 * Rational(8, 3), *sector(qt_r, 0, qt_th))
""")


# ================================================================= решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** Walk the boundary: out along a radius, round the arc, back along
the other radius. The arc is given as $10$ cm:

$$P=10+4+4=\boxed{18\text{ cm}}$$

The markscheme gives a mark for the phrase *"arc + 2 × radius"* alone. You
never need $\theta$ for this part.

**1 (b)** $s=r\theta$ with $s=10$ and $r=4$:

$$10=4\theta\Longrightarrow\theta=\boxed{\tfrac52}$$

**1 (c)** $A=\tfrac12r^2\theta=\tfrac12\cdot16\cdot\tfrac52=\boxed{20\text{ cm}^2}$.

Or, without $\theta$ at all: $A=\tfrac12rs=\tfrac12\cdot4\cdot10=20$. The
two are the same identity read in two directions.

---

**2 (a)** A regular pentagon splits the full turn into five equal parts:

$$\theta=\frac{2\pi}{5}\approx1.2566$$

and then $s=r\theta$ with $s=12$:

$$12=r\cdot\frac{2\pi}{5}\Longrightarrow r=\frac{60}{2\pi}=\boxed{\frac{30}{\pi}}\approx9.5493\text{ cm}$$

**2 (b)** The shaded region is the five pieces of the disc left outside the
pentagon, and each is a **segment** on a side of the pentagon:

$$5\times\tfrac12r^2(\theta-\sin\theta)
=\tfrac52\left(\frac{30}{\pi}\right)^2\left(\frac{2\pi}{5}-\sin\frac{2\pi}{5}\right)
=\boxed{69.7\text{ cm}^2}$$

The markscheme's other route subtracts the whole pentagon from the whole
disc, $\pi r^2-5\cdot\tfrac12r^2\sin\theta$, which is the same five
segments collected differently. Either way, the mark that goes missing is
the $\times5$.

---

**3 (a)** $210^\circ$ in radians is $210\cdot\dfrac{\pi}{180}=\dfrac{7\pi}{6}$, so

$$A=\tfrac12(19.5)^2\cdot\frac{7\pi}{6}=\boxed{\frac{3549\pi}{16}}\approx697\text{ cm}^2$$

The degree form $\dfrac{210}{360}\pi r^2$ gives the same number and the
same marks.

**3 (b)** Rolling the paper changes nothing about its edges. The cut edge
was an arc of length

$$s=19.5\cdot\frac{7\pi}{6}=\frac{91\pi}{4}\approx71.47\text{ cm}$$

and after rolling it is the circle round the bottom of the cone:

$$2\pi R=\frac{91\pi}{4}\Longrightarrow R=\boxed{\frac{91}{8}}=11.375\text{ cm}$$

The sector's own radius, $19.5$, has become the **slant height**. Confusing
it with $R$ is the standard mistake here.

---

**4 (a)** Either the cosine rule,

$$AB^2=5^2+5^2-2\cdot5\cdot5\cos1.9\Longrightarrow AB=\sqrt{50-50\cos1.9}$$

or the perpendicular from $O$, which halves both chord and angle:

$$AB=2\cdot5\sin\frac{1.9}{2}=10\sin0.95=\boxed{8.13\text{ m}}$$

Both are in the markscheme. The second is shorter and generalises.

**4 (b)** The shaded sector is the **larger** one, so its angle is the
reflex angle:

$$A=\tfrac12(5)^2(2\pi-1.9)=\tfrac12\cdot25\cdot4.3832=\boxed{54.8\text{ m}^2}$$

Or take the whole disc and remove the small sector:
$\pi(5)^2-\tfrac12(25)(1.9)=78.54-23.75=54.79$. Reading $1.9$ off the
diagram and using it directly gives $23.8$ — a complete method, no marks.

---

**5** The triangle $AOB$ has two sides equal to $r$ and the angle
$2.51$ between them:

$$\tfrac12r^2\sin2.51=26\Longrightarrow r^2=\frac{52}{\sin2.51}
\Longrightarrow r=\boxed{9.38\text{ cm}}$$

$C$ is on the major arc, so arc $ACB$ uses the reflex angle:

$$s=r(2\pi-2.51)=9.3846\times3.7732=\boxed{35.4\text{ cm}}$$

Using $2.51$ instead gives $23.6$, which is the arc on the other side of
the chord — the check names that mistake in those words.

---

**6 (a)** Sector minus triangle, with $r=2$:

$$\tfrac12(2)^2\theta-\tfrac12(2)^2\sin\theta=\boxed{2\theta-2\sin\theta}$$

**6 (b)** The rectangle is $5\times4=20$, and two of those segments are
removed:

$$20-2(2\theta-2\sin\theta)=13.4$$
$$20-4\theta+4\sin\theta=13.4$$

There is no algebraic route from here — $\theta$ appears both inside and
outside a sine — so graph $y=20-4\theta+4\sin\theta$ against $y=13.4$ on
$0<\theta<\pi$:

$$\theta=\boxed{2.36}$$

The markscheme's other opening is to note that one segment must be
$(20-13.4)/2=3.3$ and solve $2\theta-2\sin\theta=3.3$. Same equation.

> *"do not accept an answer in degrees"*, says the markscheme, and then
> names the number it will not accept: $135.030\ldots$

---

**7 (a)** $PQ=2r$ makes $[PQ]$ a diameter, so $P$, $O$ and $Q$ are
collinear and $P\hat{O}R=\pi-\theta$.

The segment between chord $[RQ]$ and its arc:

$$\tfrac12r^2\theta-\tfrac12r^2\sin\theta$$

The triangle $POR$ has sides $OP=OR=r$ and the angle $\pi-\theta$ between
them:

$$\tfrac12r^2\sin(\pi-\theta)$$

Set them equal, cancel $\tfrac12r^2$, and use $\sin(\pi-\theta)=\sin\theta$:

$$\theta-\sin\theta=\sin\theta\Longrightarrow\theta=2\sin\theta$$

**7 (b)** On $0<\theta<\pi$ the equation $\theta=2\sin\theta$ has exactly
one solution:

$$\theta=\boxed{1.90}$$

($\theta=0$ solves it too, and is excluded by the question — a segment of
zero angle is not a region.) The markscheme adds *"Award A0 if there is
more than one solution"*, which is why the check scans the whole interval
rather than testing the one number you wrote.

---

**8 (a)** Two conditions, both in $r$ and $\theta$:

$$2r+r\theta=10,\qquad \tfrac12r^2\theta=6.25$$

From the first, $r\theta=10-2r$. Substitute into the second, written as
$\tfrac12r(r\theta)$:

$$\tfrac12r(10-2r)=6.25\Longrightarrow 10r-2r^2=12.5
\Longrightarrow 4r^2-20r+25=0$$

**8 (b)** That quadratic is a perfect square:

$$(2r-5)^2=0\Longrightarrow r=\boxed{\tfrac52}$$

A repeated root, so there is nothing to reject here. Back-substituting into
the perimeter:

$$2\cdot\tfrac52+\tfrac52\theta=10\Longrightarrow\tfrac52\theta=5
\Longrightarrow\theta=\boxed{2}$$

---

**9 (a)** Both arcs subtend the same reflex angle $5.2$, so the C is one
sector minus another:

$$\tfrac12(10)^2(5.2)-\tfrac12r^2(5.2)=260-2.6r^2$$

**9 (b)(i)** $260-2.6r^2=64$, so

$$r^2=\frac{196}{2.6}=\frac{980}{13}\Longrightarrow r=\frac{14\sqrt{65}}{13}=\boxed{8.68\text{ cm}}$$

The negative root is not a radius, and $r<10$ was given.

**9 (b)(ii)** Walk the boundary of the C: the outer arc, the inner arc,
and the **two straight ends** where the two circles are joined:

$$\underbrace{10(5.2)}_{52}+\underbrace{r(5.2)}_{45.15}
+\underbrace{2(10-r)}_{2.635}=\boxed{99.8\text{ cm}}$$

Leaving out the straight ends gives $97.1$, and the check says so by name.

---

**10 (a)** The circle has circumference $2\pi(8)=16\pi$, so the perimeter
of the sector is $1.5\times16\pi=24\pi$. A sector's perimeter is
$r\theta+2r$:

$$r\theta+2r=24\pi\Longrightarrow r(\theta+2)=24\pi
\Longrightarrow r=\frac{24\pi}{\theta+2}$$

**10 (b)** Equal areas:

$$\pi(8)^2=\tfrac12r^2\theta=\tfrac12\left(\frac{24\pi}{\theta+2}\right)^2\theta$$
$$64\pi(\theta+2)^2=288\pi^2\theta\Longrightarrow(\theta+2)^2=4.5\pi\theta$$
$$\theta^2+(4-4.5\pi)\theta+4=0\Longrightarrow\theta=0.411\ \text{or}\ 9.73$$

The angle was said to be **acute**, so

$$\theta=\boxed{0.411}$$

Writing both down costs the last mark: *"Award (A1)(M1)A0 if additional
answers are given."*

---

**11 (a)** The metal is $45$ cm wide and becomes two vertical sides and the
arc:

$$45=10+s+10\Longrightarrow s=25$$

and $s=r\theta$ with $r=12$:

$$\theta=\frac{25}{12}=2.0833\ldots=\boxed{2.08}\ \text{(3 s.f.)}$$

**11 (b)** Cut the cross-section into the segment below $[AB]$ and the
rectangle above it. First the width, from the half-angle:

$$w=2\cdot12\sin\frac{2.08}{2}=20.70\text{ cm}$$

Then the segment:

$$\tfrac12(12)^2(2.08-\sin2.08)=149.76-62.87=86.89\text{ cm}^2$$

and the rectangle $10w=206.98$ cm$^2$:

$$86.89+206.98=293.9\approx\boxed{294\text{ cm}^2}$$

Keeping $\theta=25/12$ throughout gives $294.4$ — the same to three
significant figures, and the markscheme accepts both. The markscheme also
says outright that *"there are many different ways to dissect the
cross-section"*: two trapezia plus a sector is one of them, and it lands
on the same number.

---

**12 (a)** Total surface area is the base plus the curved part:

$$\pi r^2+\pi rl=12\pi\Longrightarrow 4\pi+2\pi l=12\pi
\Longrightarrow 2\pi l=8\pi\Longrightarrow l=\boxed{4}$$

Forgetting the base gives $\pi\cdot2\cdot l=12\pi$ and $l=6$.

**12 (b)** Pythagoras first, then the volume:

$$h=\sqrt{l^2-r^2}=\sqrt{16-4}=2\sqrt3$$
$$V=\tfrac13\pi r^2h=\tfrac13\pi(4)(2\sqrt3)=\boxed{\frac{8\sqrt3\,\pi}{3}}$$

Paper 1: $14.5$ earns nothing.

**12 (c)** Nothing new — the same formula with $h$ given:

$$V=\tfrac13\pi(6.3726)^2(20)=850.54\approx\boxed{851\text{ m}^3}$$

Paper 2: $\dfrac{8\sqrt3\pi}{3}$ would be fine too, but three significant
figures are what is asked for. The markscheme also accepts $850$, from the
rounded $r=6.37$.

---

**13 (a)** Let $M$ be the midpoint of $[AB]$. Then $SM\perp AB$, $SM=14$
and $SA=20$:

$$AM=\sqrt{20^2-14^2}=\sqrt{204}\Longrightarrow AB=2\sqrt{204}=28.5657\ldots=\boxed{28.57}$$

**13 (b)** One revolution is $2\pi$ and takes $16$ seconds:

$$\omega=\frac{2\pi}{16}=\boxed{\frac{\pi}{8}}\ \text{rad s}^{-1}$$

**13 (c)** The half-angle at the centre comes from the same right triangle:

$$\cos\frac{A\hat SB}{2}=\frac{14}{20}\Longrightarrow A\hat SB=2\arccos(0.7)=1.5908$$

and time is angle divided by rate:

$$T=\frac{1.5908}{\pi/8}=\frac{16\arccos0.7}{\pi}=\boxed{4.05\text{ s}}$$

**13 (d)** The angle grows at a constant $\pi/8$ per second:

$$\alpha=\boxed{\frac{\pi}{8}t}$$

---

## Timer

$P$ is the segment and $Q$ the triangle, and together they are the sector.
From $P:Q=3:5$ with $P=12.8$:

$$Q=\frac53(12.8)=\frac{64}{3},\qquad P+Q=\frac{102.4}{3}=34.133$$

Now write both areas in $r$ and $\theta$:

$$\tfrac12r^2\theta=34.133,\qquad \tfrac12r^2\sin\theta=\frac{64}{3}$$

Divide one by the other and $r$ disappears:

$$\frac{\theta}{\sin\theta}=\frac{102.4/3}{64/3}=1.6
\Longrightarrow\theta=1.6\sin\theta$$

which is the same shape of equation as task 7, and is solved the same way:

$$\theta=\boxed{1.599}$$

Then back into the segment:

$$\tfrac12r^2(\theta-\sin\theta)=12.8\Longrightarrow r=\boxed{6.53\text{ cm}}$$

The ratio is the whole difficulty. Everything after it is two formulas you
have used a dozen times, and the division that kills $r$ is the move worth
remembering: **when two areas of the same circle are given in a ratio, the
radius cancels.**
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
