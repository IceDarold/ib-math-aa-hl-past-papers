"""Собирает практикум E9: оптимизация и связанные скорости.

Тридцать пятый практикум серии и последний в карте. Темы calculus.optimization
и calculus.rates_of_change целиком и десять блоков calculus.differentiation
(движение частицы: v = ds/dt, a = dv/dt): 42 блока и 147 баллов.

Лестница из девяти приёмов идёт в три этажа. Движение по прямой: скорость в
момент, покой и разворот, наибольшее значение на отрезке. Связанные скорости:
через одну величину и через угол. Наилучшее: оптимум модели, наименьшее
расстояние, наибольшая скорость изменения и наилучшее целое.

Двадцать девятое понятие равенства ответов: **скорость меряют движением, а
наилучшее выбирают из всего разрешённого**. Проверка не дифференцирует:
время сдвигают на 10⁻¹² и делят разность; связанные скорости — те, при
которых связь не ломается, когда картинку подталкивают; наибольшее ищется
просмотром промежутка вместе с концами, а у целой буквы — перебором целых.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e9.py прогоняет по нему весь ноутбук и требует, чтобы
каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/calculus/practicum-e9-optimisation-rates.ipynb')

TRIGGER = {1: 'rate', 2: 'rest', 3: 'peak', 4: 'chain', 5: 'angle', 6: 'optimum',
           7: 'distance', 8: 'fastest', 9: 'whole', 10: 'rest', 11: 'chain',
           12: 'peak'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '-0.651',
    'q1b': '0.591',
    'q2': '3.14',
    'q3a': '1.69',
    'q3b': 'Interval(1.69, 6.12)',
    'q4a': '-4.71',
    'q4b': '0.986',
    'q5a': '2.72',
    'q5b': '-1.84',
    'q6a': '1.81',
    'q6b': '4.19',
    'q6c': '-1.47',
    'q7': '30',
    'q8': '0.0261',
    'q9': '-0.724',
    'q10': '5.2',
    'q11a': '-3*sqrt(3)/2',
    'q11b': 'Rational(2, 3)',
    'q11c': '15*sqrt(5)/4',
    'q11d': "'no'",
    'q12a': 'exp(Rational(-1, 2))',
    'q12b': '1.01',
    'q13c': 'N/2',
    'q13d': 'k*N/4',
    'q14f': '(81, 4)',
    'q14g': '(1550, 7)',
    'q14j': '9.47*10**15',
    'qt': '425',
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
# E9 — Optimisation and related rates

**147 marks of the archive, nine techniques, fourteen tasks.** Everything the
archive asks about how fast things change and where they are best, from May
2021 to November 2025: a particle moving along a line, two quantities tied
together and changing in time, and a model whose largest or smallest value is
the answer.

## The one idea

A derivative is a **rate**. Every question in this topic is one of three:

1. **How fast, right now?** — the derivative at a moment. Acceleration is the
   rate of the velocity; the rate of change of the height is $H'(t)$.
2. **How fast is the other one?** — two quantities tied by a relation, one
   rate given, the other asked. The relation is differentiated **before** the
   numbers of the moment go in.
3. **Where is it best?** — the largest or smallest value of a model on the
   interval the question allows. The ends count. Whole numbers count only as
   whole numbers.

## How the checks work

They do not know the answers, and they never differentiate. A rate is
**measured**: the check moves time by $10^{-12}$, sees how far the quantity
moved, and divides. A related rate is the one that keeps the relation true
when the picture moves. A best value is found by **looking at everything the
question allows** — the whole interval, its ends, every whole number.

```python
path = particle(v=t*sin(t) - 3, span=(0, 10))
verify_motion('a', my_a, path, 'acceleration', 'turn')
verify_related('b', my_rate, Eq(V, pi*h**2), Eq(V, 50), {dt(V): 3}, dt(h))
verify_best('c', my_x, x*(12 - 2*x)**2, (0, 6), 'max', report='place')
```

When you are wrong the check says **how**:

| what you wrote | what the check says |
|---|---|
| the velocity where the acceleration was asked | that is the velocity at that moment |
| $dh/dV$ where $dh/dt$ was asked | multiply by $dV/dt$ |
| $-425$ for a speed | a speed is a size, without the sign |
| $n=7.36$ | $n$ counts things, so it is a whole number |
| $D^2$ where $D$ was asked | that is the square: the root is missing |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | a particle on a line: rates, rest, the largest value | 1–6 |
| 🟡 | related rates, through a length and through an angle | 7–10 |
| 🔴 | the best value of a model, a distance, a rate, a whole number | 11–14 |

Every task is a real past-paper question, cited.

**121 of the 147 marks are on a calculator paper, and this time the number is
nearly honest.** The motion questions are button work almost entirely; in
related rates the calculator finds the state of the moment, and the chain is
written by hand. About 75 of the 121 marks belong to the calculator.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + particle, rate_of, dt

language('en')                 # this notebook is in English, and so are the checks

# particle(v=..., span=(0, 10)) — a particle given by its velocity (or s=...).
# rate_of(f) — the rate of change of f, measured by moving time a little.
# dt(h) — the rate of h in a related-rates question: dh/dt.

print('ready; sympy', sp.__version__)
sample = 20 + 60*exp(-t/10)
print('rate of the sample at t = 5:', round(float(rate_of(sample)(5)), 4))
""")

md(r"""
---
## Map of the nine techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | a rate at a moment | *find the rate of change … when $t=13$*, *find the acceleration* | the derivative at that moment |
| 2 | rest and turning | *at rest*, *changes direction*, *displacement is increasing* | $v=0$, $v$ changes sign, $v>0$ |
| 3 | the largest value in motion | *maximum speed*, *maximum displacement* | turning points **and** the ends |
| 4 | a chain through one quantity | *poured in at 2 cm³ s⁻¹ … the rate of change of the height* | $\frac{dh}{dt}=\frac{dV/dt}{dV/dh}$ |
| 5 | a chain through an angle | *the angle is decreasing at … how fast is AC changing* | differentiate the geometry in $t$ |
| 6 | the optimum of a model | *such that the area is a maximum*, *justify that it is a minimum* | $f'=0$ inside the domain, then answer what is asked |
| 7 | the shortest distance | *closest to the origin*, *minimum value of $D(t)$* | minimise $D^2$, then take the root |
| 8 | the fastest change | *rate of change is at its maximum*, *decreasing most rapidly* | the vertex of the rate: $f''=0$ |
| 9 | the best whole number | *the value of $n$ at which it occurs* | compare the whole numbers either side of the vertex |

Techniques 1–3 are one particle read three ways. Techniques 4–5 are one chain
rule, with a length or an angle in the middle. Techniques 6–9 are all "where is
it best", and they differ only in **what** is made best and **what** is
reported.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. A particle on a line

## Theory: a rate is a derivative with a clock

A cup of coffee cools as $T(t)=20+60e^{-t/10}$ degrees after $t$ minutes. How
fast is it cooling at $t=5$?

$$T'(t)=-6e^{-t/10},\qquad T'(5)=-6e^{-1/2}\approx-3.64\ \text{°C per minute}$$

The minus sign **is** the answer that it is cooling; do not drop it. And the
temperature itself, $T(5)\approx56.4$, is not a rate at all — the most common
lost mark here is answering the question that was not asked.

For motion the names are fixed:

$$v=\frac{ds}{dt},\qquad a=\frac{dv}{dt}$$

So *"find the acceleration"* means differentiate the velocity, and *"when is the
acceleration 3"* means solve $v'(t)=3$ on the interval in the question. With
$v(t)=t^2-4t$: $a=2t-4$, and $a=3$ at $t=3.5$.

> **Radians.** On a calculator paper everything with $\sin t$ is in radians.
> One markscheme in this topic awards A0 for the answer that came out of a
> calculator left in degrees.

**Comparing rates is not comparing sizes.** *"When does B grow faster than
A"* is an inequality between the derivatives. Where B is taller is a different
question with a different answer.
""")

md(r"""
### Task 1 🟢 — *May 2024 TZ1 Paper 2 Q10(c) and May 2025 TZ3 Paper 2 Q10(b), 4 marks*

**(a)** The height of water in metres at Sule Skerry is modelled by

$$H(t)=1.63\sin\big(0.513(t-8.20)\big)+2.13$$

where $t$ is the number of hours after midnight. Find the rate of change of the
height of the water when $t=13$, giving your answer in metres per hour.

**(b)** Fiona's velocity, in m s⁻¹, during a race is modelled by

$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}},\qquad t\ge0$$

Find the time when Fiona's acceleration is $4$ m s⁻².

*Three significant figures.*
""")

code(r"""
q1a = ...        # the rate of change of H at t = 13
q1b = ...        # the time when the acceleration is 4

H = 1.63*sin(0.513*(t - 8.20)) + 2.13
fiona = particle(v=8.14*t/sqrt(t**2 + 0.2), span=(0, oo))

verify_rate('1(a)', q1a, H, 13)
verify_when('1(b)', q1b, fiona, ('acceleration', 4))
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ2 Paper 2 Q10(d), 6 marks*

The height of Plant A, $h_A$ cm, at time $t$ weeks is modelled by
$h_A(t)=\sin(2t+6)+9t+27$, and the height of Plant B by $h_B(t)=8t+32$, both
for $0\le t\le9$.

For $0\le t\le9$, find the total amount of time when the rate of growth of
Plant B was greater than the rate of growth of Plant A.

*Three significant figures, in weeks.*
""")

code(r"""
q2 = ...         # total time, in weeks

h_A = sin(2*t + 6) + 9*t + 27
h_B = 8*t + 32

verify_duration('2', q2, h_B, h_A, (0, 9))
""")

# ================================================================= теория 2
md(r"""
## Theory: at rest, and turning back

Take $v(t)=t^2-5t+4=(t-1)(t-4)$ on $0\le t\le6$.

* **At rest** means $v=0$: at $t=1$ and at $t=4$.
* **Changes direction** means $v$ **changes sign**. Here it does at both:
  $+$ before $1$, $-$ between $1$ and $4$, $+$ after $4$.
* **The displacement is increasing** exactly where $v>0$: for $0\le t<1$ and
  for $4<t\le6$.

The two words are not the same. With $w(t)=(t-2)^2$ the particle stops at
$t=2$ and carries on **the same way**: $w$ touches zero and stays positive. At
rest, yes; changes direction, no.

> **One value, not three.** *"Find the smallest value of $t$ …"* is worth two
> marks, and markschemes say *do not award A1 if additional values are given*.
> A calculator that returns three roots of $v=0$ has done its job; choosing is
> yours — and only roots inside the interval of the question count.

**Acceleration at the moment it turns** is two steps: find the moment from
$v$, then put it into $v'$. In the example $v'(t)=2t-5$, so at the second turn
$a=v'(4)=3$.
""")

md(r"""
### Task 3 🟢 — *May 2024 TZ1 Paper 2 Q4(a) and (b), 4 marks*

A particle moves in a straight line. For $0\le t\le10$ its velocity, in metres
per second, is

$$v=2\sin(0.5t)+0.3t-2$$

**(a)** Find the smallest value of $t$ when the particle changes direction.

**(b)** Find the range of values of $t$ for which the displacement of the
particle is increasing.

*Three significant figures. In (b) write the answer as `Interval(a, b)`.*
""")

code(r"""
q3a = ...        # the first change of direction
q3b = ...        # when the displacement increases

path = particle(v=2*sin(0.5*t) + 0.3*t - 2, span=(0, 10))

verify_when('3(a)', q3a, path, 'turn')
verify_while('3(b)', q3b, path, 'forward')
""")

md(r"""
### Task 4 🟢 — *May 2022 TZ1 Paper 2 Q4(b) and May 2025 TZ2 Paper 2 Q5(c), 6 marks*

**(a)** A particle moves along a straight line so that its velocity after $t$
seconds is $v(t)=e^{\sin t}+4\sin t$ for $0\le t\le6$. Find the acceleration
of the particle when it changes direction.

**(b)** A particle P moves in a straight line with velocity
$v(t)=e^{-\sin t}\cos(2t)$ for $0\le t\le5$. Find the acceleration when P
changes direction for the **second** time.

*Three significant figures.*
""")

code(r"""
q4a = ...        # the acceleration at the change of direction
q4b = ...        # the acceleration at the second change of direction

first = particle(v=exp(sin(t)) + 4*sin(t), span=(0, 6))
second = particle(v=exp(-sin(t))*cos(2*t), span=(0, 5))

verify_motion('4(a)', q4a, first, 'acceleration', 'turn')
verify_motion('4(b)', q4b, second, 'acceleration', ('turn', 2))
""")

# ================================================================= теория 3
md(r"""
## Theory: the largest value lives at a vertex **or at an end**

Take $v(t)=3-t^2$ on $0\le t\le3$. Its graph has a vertex at $t=0$, where
$v=3$. Is that the greatest speed? No:

$$v(3)=3-9=-6,\qquad |v(3)|=6>3$$

**Speed is $|v|$.** The particle is fastest where the velocity is most
negative, and here that is the end of the interval, where the graph has no
vertex at all. Setting $v'=0$ finds only vertices; the ends must be checked by
hand.

The same for displacement: a particle given by $s(t)$ may be fastest at
$t=0$, where the graph of $s$ is steepest — again an end, not a vertex of $v$.

> **The word decides the sign.** *Maximum velocity* keeps the sign; *maximum
> speed* does not. An answer of $-6$ for a speed loses the mark.

| asked for | compare |
|---|---|
| maximum velocity | the largest $v$: vertices of $v$ and the ends |
| maximum speed | the largest $|v|$: both the highest and the lowest $v$ |
| maximum displacement | the largest $s$: vertices of $s$ and the ends |
""")

md(r"""
### Task 5 🟢 — *May 2025 TZ2 Paper 2 Q5(a) and May 2022 TZ2 Paper 2 Q5(c), 4 marks*

**(a)** A particle P moves in a straight line with velocity
$v(t)=e^{-\sin t}\cos(2t)$ for $0\le t\le5$. Find the maximum speed of P.

**(b)** A particle moves in a straight line with velocity

$$v=\frac{(t^2+1)\cos t}{4},\qquad 0\le t\le3$$

Find the particle's acceleration when its speed is at its greatest.

*Three significant figures.*
""")

code(r"""
q5a = ...        # the maximum speed
q5b = ...        # the acceleration when the speed is greatest

path = particle(v=exp(-sin(t))*cos(2*t), span=(0, 5))
other = particle(v=(t**2 + 1)*cos(t)/4, span=(0, 3))

verify_extreme('5(a)', q5a, path, 'speed')
verify_motion('5(b)', q5b, other, 'acceleration', 'fastest')
""")

md(r"""
### Task 6 🟢 — *November 2025 TZ3 Paper 2 Q10(a) and (b)(i), 7 marks*

A particle P moves in a straight line so that its displacement, $s$ cm, from a
fixed point O at time $t$ seconds is

$$s(t)=2^{\left(1-\frac t5\right)}\sin\left(\frac{2\pi t}{3}\right),\qquad t\ge0$$

**(a)** Find (i) the maximum displacement of P from O; (ii) the maximum
velocity of P.

**(b)** Find the minimum value of the displacement function $s(t)$.

*Three significant figures.*
""")

code(r"""
q6a = ...        # the maximum displacement
q6b = ...        # the maximum velocity
q6c = ...        # the minimum displacement

path = particle(s=2**(1 - t/5)*sin(2*pi*t/3), span=(0, oo))

verify_extreme('6(a)(i)', q6a, path, 'displacement')
verify_extreme('6(a)(ii)', q6b, path, 'velocity')
verify_extreme('6(b)(i)', q6c, path, 'displacement', 'min')
""")

# ================================================================= теория 4
md(r"""
---
# 🟡 Part 2. Related rates

## Theory: one chain, two rates

A cube is growing: its side $s$ increases at $0.5$ cm s⁻¹. How fast is its
volume growing when the side is $4$ cm?

The relation comes first, with **no numbers of the moment in it**:

$$V=s^3\quad\Longrightarrow\quad\frac{dV}{dt}=3s^2\,\frac{ds}{dt}$$

and only now the moment: $\frac{dV}{dt}=3\cdot16\cdot0.5=24$ cm³ s⁻¹.

The chain can run the other way. If instead the **volume** grows at $6$ cm³ s⁻¹
and the question asks for the side when $V=27$:

$$\frac{ds}{dt}=\frac{dV/dt}{dV/ds}=\frac{6}{3s^2},\qquad V=27\Rightarrow s=3,\qquad \frac{ds}{dt}=\frac{2}{9}$$

Three steps, and each is a mark: **the relation**, **the chain**, **the state
of the moment** (here $s$ from $V$).

> **Three ways to lose it.** Stopping at $\frac{ds}{dV}$ — a rate per unit of
> volume, not per second. Turning the chain upside down,
> $\frac{dV}{dt}\cdot\frac{dV}{ds}$. And putting $s=3$ in before
> differentiating — then $V=27$ is a constant and its derivative is zero.

**The state may have several roots.** A cubic in $h$ can have three, and only
one is inside the container. The question's picture tells you which.
""")

md(r"""
### Task 7 🟡 — *May 2023 TZ1 Paper 1 Q6, 5 marks*

The side lengths, $x$ cm, of an equilateral triangle are increasing at a rate of
$4$ cm s⁻¹.

Find the rate at which the area of the triangle, $A$ cm², is increasing when the
side lengths are $5\sqrt3$ cm.

*No calculator: give the exact value. The cell draws the triangle by its
vertices, so the area comes from the picture.*
""")

code(r"""
q7 = ...         # dA/dt, exact

A = Symbol('A')
triangle = measure('triangle', (0, 0, 0), (x, 0, 0), (x/2, sqrt(3)*x/2, 0))

verify_related('7', q7, Eq(A, triangle), Eq(x, 5*sqrt(3)), {dt(x): 4}, dt(A),
               where={x: (0, 20)}, exact=True)
""")

md(r"""
### Task 8 🟡 — *November 2022 Paper 2 Q8, 6 marks*

Liquid is poured into a round-bottomed flask at a rate of $2$ cm³ s⁻¹. The
volume $V$ cm³ and the height $h$ cm of the liquid satisfy

$$V=5\pi h^2-\frac13\pi h^3$$

and the liquid never reaches the neck of the flask, whose sphere has diameter
$10$ cm. Find the rate of change of the height of the liquid at the instant when
the volume of the liquid is $200$ cm³.

*Three significant figures.*
""")

code(r"""
q8 = ...         # dh/dt when V = 200

V, h = symbols('V h')

verify_related('8', q8, Eq(V, 5*pi*h**2 - pi*h**3/3), Eq(V, 200), {dt(V): 2}, dt(h),
               where={h: (0, 10)})
""")

# ================================================================= теория 5
md(r"""
## Theory: when the middle of the chain is an angle

A ladder $5$ m long leans on a wall, and its foot slides so that the angle
$\theta$ with the ground **decreases** at $0.2$ rad s⁻¹. How fast is the foot
moving away from the wall when $\theta=\frac\pi3$?

The picture gives the relation, $x=5\cos\theta$, and every letter in it depends
on time:

$$\frac{dx}{dt}=-5\sin\theta\,\frac{d\theta}{dt}=-5\cdot\frac{\sqrt3}{2}\cdot(-0.2)=\frac{\sqrt3}{2}\approx0.866\ \text{m s}^{-1}$$

The angle rate is **negative** because the angle decreases; the sign travels
through the chain, and the answer comes out positive because the foot moves
away.

**The state of the moment** is often given indirectly. *"When the triangle's
area is $30$"* fixes $\sin\theta$ through $\frac12ab\sin\theta$; *"when the
shadow is twice as long as the pole"* fixes $\tan\theta$. Find it, and then —
only then — substitute.

> **Speed or rate?** *"Find the speed"* wants a size: no sign. *"Determine how
> fast AC is changing"* wants the sign: a markscheme awards A0 for the positive
> number when the length is decreasing.
""")

md(r"""
### Task 9 🟡 — *November 2025 TZ1 Paper 2 Q9, 7 marks*

Consider triangle ABC with $AB=15$ cm, $BC=20$ cm, $AC=x$ cm and
$A\hat BC=\theta$, where $0<\theta<\frac\pi2$.

Angle $\theta$ is decreasing at the constant rate of $\frac{\pi}{60}$ radians per
minute.

Determine how fast the length of AC is changing when the area of the triangle
is $140$ cm².

*Three significant figures. The cell draws the triangle: B at the origin, C on
the axis, A turning with $\theta$.*
""")

code(r"""
q9 = ...         # dx/dt, with its sign

S, theta = symbols('S theta')
B_, C_, A_ = (0, 0, 0), (20, 0, 0), (15*cos(theta), 15*sin(theta), 0)

verify_related('9', q9, [Eq(x, distance(A_, C_)), Eq(S, measure('triangle', A_, B_, C_))],
               Eq(S, 140), {dt(theta): -pi/60}, dt(x), where={theta: (0, pi/2)})
""")

md(r"""
### Task 10 🔴 — *May 2021 TZ1 Paper 2 Q9(b), 6 marks*

Two boats A and B travel due north. Initially boat B is $50$ m due east of boat
A. After $t$ seconds boat A has travelled $x$ m and boat B $y$ m, and $\theta$ is
the bearing of B from A, in radians. Part (a) shows that

$$y=x+50\cot\theta$$

At time $T$: boat B has travelled $10$ m further than boat A; boat B is
travelling at double the speed of boat A; and $\theta$ changes at
$-0.1$ radians per second.

Find the speed of boat A at time $T$.

*Three significant figures. Where exactly the boats are is not given, and the
check tries several places to make sure the answer does not depend on it.*
""")

code(r"""
q10 = ...        # the speed of boat A

y, theta = symbols('y theta')

verify_related('10', q10, Eq(y, x + 50*cot(theta)), Eq(y - x, 10),
               [Eq(dt(y), 2*dt(x)), Eq(dt(theta), -0.1)], dt(x),
               where={theta: (0, pi/2)}, size=True)
""")

# ================================================================= теория 6
md(r"""
---
# 🔴 Part 3. Where is it best

## Theory: the model, the domain, and what is actually asked

A rectangle stands on the $x$-axis under $y=12-x^2$, with its top corners on
the curve at $(\pm x,\,12-x^2)$. Its area is

$$A(x)=2x\left(12-x^2\right)=24x-2x^3,\qquad 0<x<2\sqrt3$$

$A'(x)=24-6x^2=0$ gives $x=\pm2$, and the domain throws out $x=-2$. Then

$$A''(x)=-12x,\qquad A''(2)=-24<0$$

so $x=2$ gives a **maximum** — and that sentence, with the value of $A''$, is
the R mark. *"$A'=0$ there"* alone is not a reason.

**Now read the question again.** If it asks for the *height* of the largest
rectangle, the answer is $12-2^2=8$, not $x=2$. In this topic the variable of
the model and the thing asked for are different more often than not: the
$y$-coordinate of a vertex, a distance $PX$, the value $\sin\theta$.

> **Comparing with the optimum.** *"Can a pole of length 11 m be carried round
> the corner?"* is answered by the **smallest** length of the segment through
> the corner: the pole passes only if it is no longer than that.
""")

md(r"""
### Task 11 🔴 — *May 2023 TZ2 P1 Q10(d), November 2025 TZ3 P1 Q8(c), May 2023 TZ1 P1 Q11(d)(ii), (e); 15 marks*

**(a)** A triangle PQR is inscribed in the circle $x^2+y^2=9$, with $P(-3,0)$,
$Q(x,y)$ in the first quadrant and $R(x,-y)$ in the fourth. Its area is
$A=(x+3)\sqrt{9-x^2}$. Find the $y$-coordinate of R such that $A$ is a maximum.

**(b)** Astrid walks from R to X across the sand and then jogs along the
promenade to Q. The time taken is

$$T=500\sec\theta+\frac{2500-1000\tan\theta}{3},\qquad 0<\tan\theta<\frac52$$

She chooses $\theta$ so that $T$ is as small as possible. Find $\sin\theta$ for
that choice. (The paper then shows $PX=400\tan\theta=160\sqrt5$.)

**(c)** A straight segment AB touches the corner C of a passage of width
$\frac34$ m joining a room of width $6$ m. Its length is

$$L=\frac34\sec\alpha+6\,\mathrm{cosec}\,\alpha,\qquad 0<\alpha<\frac\pi2$$

Determine the minimum value of $L$.

**(d)** Two people need to carry a pole of length $11.25$ m horizontally from
the passage into the room. Is this possible? Enter `'yes'` or `'no'`.

*No calculator in (a)–(c): exact values.*
""")

code(r"""
q11a = ...       # the y-coordinate of R
q11b = ...       # sin(theta) at the quickest route
q11c = ...       # the minimum of L
q11d = ...       # 'yes' or 'no'

theta, alpha = symbols('theta alpha')
area = (x + 3)*sqrt(9 - x**2)
time_taken = 500*sec(theta) + (2500 - 1000*tan(theta))/3
L = Rational(3, 4)*sec(alpha) + 6*cosec(alpha)

verify_best('11(a)', q11a, area, Interval.open(0, 3), 'max', report=-sqrt(9 - x**2), exact=True)
verify_best('11(b)', q11b, time_taken, Interval.open(0, atan(Rational(5, 2))), 'min',
            var=theta, report=sin(theta), exact=True)
verify_best('11(c)', q11c, L, Interval.open(0, pi/2), 'min', var=alpha, exact=True)
verify_fits('11(d)', q11d, L, Interval.open(0, pi/2), 11.25, var=alpha)
""")

# ================================================================= теория 7
md(r"""
## Theory: minimise the square

Which point of $y=\sqrt x$ is closest to $(3,0)$? The distance is

$$D=\sqrt{(x-3)^2+\left(\sqrt x\right)^2}=\sqrt{x^2-5x+9}$$

and a square root is an increasing function, so $D$ is smallest exactly where
$D^2$ is. Minimise the square — no chain rule, no root in the denominator:

$$\frac{d}{dx}\left(x^2-5x+9\right)=2x-5=0\quad\Longrightarrow\quad x=\frac52$$

and **only then** take the root, if the distance itself is asked:
$D=\sqrt{\frac{25}4-\frac{25}2+9}=\frac{\sqrt{11}}{2}$.

Two points moving in time are the same question with $t$ as the letter —
**one** $t$ for both. Giving them two different parameters measures the
distance between their paths, not between them, and earns nothing.

> **The domain again.** If the curve lives on $x>0$, then $x=0$ is not an
> answer even when it solves the equation.
""")

md(r"""
### Task 12 🔴 — *May 2025 TZ2 Paper 1 Q6(b) and May 2022 TZ2 Paper 2 Q11(e), 11 marks*

**(a)** Let $f(x)=\sqrt{x^2\ln x+4-x^2}$, $x>0$. Part (a) shows that the distance
from the origin to a point of the graph is $l=\sqrt{x^2\ln x+4}$. Find the
$x$-coordinate of the point on the graph of $f$ which is closest to the origin.

**(b)** Two airplanes have position vectors, in km, after $t$ minutes

$$\mathbf r_A=\begin{pmatrix}19\\-1\\1\end{pmatrix}+t\begin{pmatrix}-6\\2\\4\end{pmatrix},\qquad
\mathbf r_B=\begin{pmatrix}1\\0\\12\end{pmatrix}+t\begin{pmatrix}4\\2\\-2\end{pmatrix},\qquad 0\le t\le2.5$$

Let $D(t)$ be the distance between them. Find the minimum value of $D(t)$.

*(a) exact, no calculator; (b) three significant figures.*
""")

code(r"""
q12a = ...       # x of the closest point
q12b = ...       # the minimum of D(t)

l = sqrt(x**2*log(x) + 4)
r_A = Matrix([19, -1, 1]) + t*Matrix([-6, 2, 4])
r_B = Matrix([1, 0, 12]) + t*Matrix([4, 2, -2])

verify_best('12(a)', q12a, l, Interval.open(0, 10), 'min', report='place', exact=True)
verify_best('12(b)', q12b, distance(r_A, r_B), (0, 2.5), 'min', var=t)
""")

# ================================================================= теория 8
md(r"""
## Theory: the fastest change is the vertex of the rate

The height of a hill is $r(x)=\dfrac1{1+x^2}$ for $x\ge0$. Where is it
**falling most steeply**?

The quantity made smallest here is not $r$ but its **rate**:

$$r'(x)=-\frac{2x}{(1+x^2)^2}$$

The steepest fall is the lowest point of the graph of $r'$ — the vertex of the
rate, which is where $r''=0$:

$$r''(x)=\frac{6x^2-2}{(1+x^2)^3}=0\quad\Longrightarrow\quad x=\frac1{\sqrt3}$$

and $r''$ changes from negative to positive there, so $r'$ has a minimum. In
the language of E8: the fastest change of $r$ sits at a **point of inflexion**
of $r$.

> **Three readings to keep apart.** *Decreasing most rapidly* — the smallest
> (most negative) $r'$. *Smallest $r$* — a different place, often an end.
> *$r'=0$* — where $r$ stops changing, the opposite of the fastest change.

When the rate is given as a function of the quantity itself —
$\frac{dP}{dt}=g(P)$ — its largest value is found in $P$, with no time at all:
the vertex of $g$.
""")

md(r"""
### Task 13 🔴 — *May 2022 TZ2 Paper 2 Q12(c) and (d), 7 marks*

The population $P$ of a species of marsupial is modelled by

$$\frac{dP}{dt}=kP\left(1-\frac PN\right)$$

where $k$ and $N$ are positive constants and $0<P<N$.

**(c)** Find the value of $P$ at which the population increases at its maximum
rate. (The paper says *show that it is $\frac N2$ — justify your answer*.)

**(d)** Hence determine the maximum value of $\frac{dP}{dt}$ in terms of $k$ and
$N$.

*The answers carry the letters. The check tries three sets of values of $k$ and
$N$.*
""")

code(r"""
q13c = ...       # the population at the maximum rate
q13d = ...       # the maximum of dP/dt

pop = Symbol('pop')             # the population of the question
growth = k*pop*(1 - pop/N)

verify_best('13(c)', q13c, growth, (0, N), 'max', var=pop, report='place',
            params={k: (0.7, 0.3, 2), N: (100, 7, 50)})
verify_best('13(d)', q13d, growth, (0, N), 'max', var=pop,
            params={k: (0.7, 0.3, 2), N: (100, 7, 50)})
""")

# ================================================================= теория 9
md(r"""
## Theory: whole numbers are compared, not rounded

How many years $n$ make $f(n)=n\cdot0.85^n$ largest? As a smooth function its
vertex is at

$$f'(n)=0.85^n\left(1+n\ln0.85\right)=0\quad\Longrightarrow\quad n=-\frac1{\ln0.85}\approx6.15$$

But years are whole. Compare the neighbours:

$$f(6)=6\cdot0.85^6\approx2.263,\qquad f(7)=7\cdot0.85^7\approx2.244$$

so $n=6$. Here rounding would have worked; it does not always. The vertex tells
you **where to look**, and the comparison decides.

> **Two numbers asked, two numbers given.** *"Write down the value of $P$ and the
> value of $n$ at which it occurs"* is a pair; one without the other loses a
> mark. And the value at the vertex, $f(6.15)$, is not a value the function
> ever takes on whole numbers — a markscheme gives A0 for it.
""")

md(r"""
### Task 14 🔴 — *May 2023 TZ1 Paper 3 Q2(f), (g), (j), 8 marks*

$M_n(S)$ is the maximum product of $n$ positive real numbers with sum $S$, and
earlier parts show $M_n(S)=\left(\frac Sn\right)^n$. For $n\in\mathbb Z^+$, $P(S)$
is the largest value of $M_n(S)$ over all $n$.

**(f)** Write down the value of $P(12)$ and the value of $n$ at which it occurs.

**(g)** Determine the value of $P(20)$ and the value of $n$ at which it occurs.

**(j)** Find the largest possible product of positive numbers whose sum is
$100$. Give your answer in the form $a\times10^k$, $1\le a<10$.

*Pairs as `(P, n)`. Three significant figures where the value is not whole.*
""")

code(r"""
q14f = ...       # (P(12), n)
q14g = ...       # (P(20), n)
q14j = ...       # the largest product with sum 100

n = Symbol('n')

verify_best('14(f)', q14f, (12/n)**n, (1, 40), 'max', var=n, report=('value', 'place'),
            integer=True)
verify_best('14(g)', q14g, (20/n)**n, (1, 40), 'max', var=n, report=('value', 'place'),
            integer=True)
verify_best('14(j)', q14j, (100/n)**n, (1, 200), 'max', var=n, integer=True)
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would make
first**.

| code | technique |
| --- | --- |
| `rate` | a derivative at a moment, or the meaning of one |
| `rest` | at rest, changes direction, displacement increasing |
| `peak` | the largest value in motion, ends included |
| `chain` | a related rate through one quantity |
| `angle` | a related rate through an angle |
| `optimum` | the best value of a model, and what is asked there |
| `distance` | the shortest distance, through its square |
| `fastest` | where a rate is largest or smallest |
| `whole` | the best whole number |

1. Find the rate of change of the temperature $T(t)=15+40e^{-0.2t}$ at $t=3$.
2. $v(t)=\cos t-0.2t$; find the first time the particle turns back.
3. $v(t)=4-t^2$ on $0\le t\le3$; find the maximum speed.
4. Sand forms a cone with $V=\frac{\pi}{3}h^3$, poured at $2$ m³ min⁻¹; find $\frac{dh}{dt}$ when $h=1.5$.
5. A kite at height $30$ m moves horizontally; the angle of the string changes at $0.02$ rad s⁻¹. Find the speed of the kite.
6. A box with a square base and volume $32$ has the least surface area. Find its height.
7. Find the point of $y=x^2$ nearest to $(0,2)$.
8. $N(t)=\dfrac{500}{1+4e^{-t}}$; when is the number growing fastest?
9. How many identical parcels $n$ make $n(20-n)^2$ largest?
10. $s(t)=t^3-6t^2+9t$; for which $t$ is the displacement decreasing?
11. A spherical balloon loses air at $3$ cm³ s⁻¹; how fast is the radius shrinking when $r=5$?
12. $s(t)=e^{-t}\sin 2t$, $t\ge0$; find the maximum velocity.
""")

code("""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + """)
""")

# =================================================================== таймер
md(r"""
---
## On the clock — *May 2025 TZ3 Paper 2 Q9(b), 7 marks*

**Seven marks, ten minutes.** Calculator allowed, no hints.

An airplane P flies at a constant height of $6$ km over horizontal ground,
approaching a runway AB of length $2$ km. G is the point on the ground directly
below the airplane, $GA=x$ km, and the pilot's viewing angle of the runway,
$A\hat PB$, is $\theta$. Part (a) shows that

$$\theta=\arctan\left(\frac{x+2}{6}\right)-\arctan\left(\frac x6\right)$$

When the viewing angle is $0.178$ radians, it is changing at a rate of
$12.5$ radians per hour. Find the speed of the airplane.

*Three significant figures, in km per hour.*

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt = ...         # the speed of the airplane

theta = Symbol('theta')

verify_related('timer', qt, Eq(theta, atan((x + 2)/6) - atan(x/6)), Eq(theta, 0.178),
               {dt(theta): 12.5}, dt(x), where={x: (0, 50)}, size=True)
""")

# ================================================================== решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1 (a)** The rate of change of $H$ is $H'(t)$; the calculator's $\frac{d}{dx}$
at $t=13$ gives $\boxed{-0.651}$ m per hour $(-0.650622\ldots)$. The water is
falling.

**1 (b)** Acceleration is $v'(t)$. Graphing $v'(t)$ and $y=4$, or solving
$v'(t)=4$, gives $\boxed{t=0.591}$ s $(0.590930\ldots)$.

---

**2** $h_A'(t)=2\cos(2t+6)+9$ and $h_B'(t)=8$. B grows faster when
$8>2\cos(2t+6)+9$, that is $\cos(2t+6)<-\frac12$. On $0\le t\le9$ this holds on
three stretches, each of length $\frac\pi3$:

$$\left(\tfrac{4\pi}3-3,\ \tfrac{5\pi}3-3\right),\quad\left(\tfrac{7\pi}3-3,\ \tfrac{8\pi}3-3\right),\quad\left(\tfrac{10\pi}3-3,\ \tfrac{11\pi}3-3\right)$$

so the total is $3\cdot\frac\pi3=\boxed{\pi\approx3.14}$ weeks.

---

**3 (a)** The particle changes direction where $v=0$ and changes sign. The
smallest root is $\boxed{t=1.69}$ $(1.68694\ldots)$.

**3 (b)** The displacement increases where $v>0$, between the two roots:
$\boxed{1.69<t<6.12}$.

---

**4 (a)** $v=0$ on $[0,6]$ only at $t=3.34692\ldots$, and $v$ changes sign
there. Then $a=v'(3.34692\ldots)=\boxed{-4.71}$ m s⁻².

**4 (b)** $v=0$ where $\cos2t=0$: $t=\frac\pi4,\frac{3\pi}4,\frac{5\pi}4$. The
second is $\frac{3\pi}4$. There $\cos2t=0$ and $\sin2t=-1$, so only one term
of $v'(t)=-\cos t\,e^{-\sin t}\cos2t-2e^{-\sin t}\sin2t$ survives:
$a=2e^{-\sin(3\pi/4)}=2e^{-1/\sqrt2}\approx\boxed{0.986}$ m s⁻².

---

**5 (a)** Speed is $|v|$. The lowest point of $v$ on $[0,5]$ is
$(4.71238\ldots,\ -2.71828\ldots)$, so the maximum speed is
$\boxed{e\approx2.72}$ m s⁻¹. The highest point of $v$ is only $1.13$.

**5 (b)** $|v|$ is greatest at the end, $t=3$: $|v(3)|=2.47$, larger than at
any vertex inside. Then $a=v'(3)=\boxed{-1.84}$ m s⁻².

---

**6 (a)(i)** The first maximum of $s$ is at $t=0.718\ldots$, height
$\boxed{1.81}$ cm; later ones are lower.

**6 (a)(ii)** $v=s'(t)$, and the graph of $s$ is steepest at the start:
$v(0)=\frac{4\pi}3\approx\boxed{4.19}$ cm s⁻¹. The vertices of $v$ inside are
lower.

**6 (b)(i)** The first minimum: $\boxed{-1.47}$ cm at $t=2.218\ldots$.

---

**7** $A=\frac12x^2\sin\frac\pi3=\frac{\sqrt3}4x^2$, so
$\frac{dA}{dt}=\frac{\sqrt3}{2}x\,\frac{dx}{dt}$ and

$$\frac{dA}{dt}=\frac{\sqrt3}2\cdot5\sqrt3\cdot4=\boxed{30}\ \text{cm}^2\,\text{s}^{-1}$$

---

**8** $\frac{dV}{dh}=10\pi h-\pi h^2$, so
$\frac{dh}{dt}=\frac{2}{10\pi h-\pi h^2}$. Solving $5\pi h^2-\frac13\pi h^3=200$
gives $h=4.20648\ldots$ (the other roots, $-3.24$ and $14.0$, are outside the
flask). Then $\frac{dh}{dt}=\boxed{0.0261}$ cm s⁻¹.

---

**9** $x^2=625-600\cos\theta$, so $2x\frac{dx}{dt}=600\sin\theta\frac{d\theta}{dt}$.
The area gives $\frac12\cdot15\cdot20\sin\theta=140$, so $\sin\theta=\frac{14}{15}$,
$\cos\theta=\frac{\sqrt{29}}{15}$ and $x=\sqrt{625-40\sqrt{29}}$. Then

$$\frac{dx}{dt}=\frac{600\cdot\frac{14}{15}\cdot\left(-\frac\pi{60}\right)}{2x}\approx\boxed{-0.724}\ \text{cm per minute}$$

negative, because AC is getting shorter.

---

**10** Differentiate: $\frac{dy}{dt}=\frac{dx}{dt}-50\,\mathrm{cosec}^2\theta\frac{d\theta}{dt}$.
With $\frac{dy}{dt}=2\frac{dx}{dt}$ this gives
$\frac{dx}{dt}=-50\,\mathrm{cosec}^2\theta\frac{d\theta}{dt}$. From $y-x=10$,
$\cot\theta=\frac15$ and $\mathrm{cosec}^2\theta=1+\frac1{25}=\frac{26}{25}$, so

$$\frac{dx}{dt}=-50\cdot\frac{26}{25}\cdot(-0.1)=\boxed{5.2}\ \text{m s}^{-1}$$

---

**11 (a)** Part (c) of the paper gives $\frac{dA}{dx}=\frac{9-3x-2x^2}{\sqrt{9-x^2}}$.
Zero when $2x^2+3x-9=(2x-3)(x+3)=0$, and Q in the first quadrant rejects
$x=-3$. So $x=\frac32$ and R, below the axis, has

$$y=-\sqrt{9-\tfrac94}=\boxed{-\frac{3\sqrt3}{2}}$$

**11 (b)** $\frac{dT}{d\theta}=500\sec\theta\tan\theta-\frac{1000}3\sec^2\theta=0$
gives $500\sin\theta=\frac{1000}3$, so $\boxed{\sin\theta=\frac23}$; then
$\tan\theta=\frac2{\sqrt5}$ and $PX=400\tan\theta=160\sqrt5$.

**11 (c)** At $\alpha=\arctan2$: $\sec\alpha=\sqrt5$, $\mathrm{cosec}\,\alpha=\frac{\sqrt5}2$,

$$L_{\min}=\frac34\sqrt5+6\cdot\frac{\sqrt5}2=\boxed{\frac{15\sqrt5}{4}}\approx8.39$$

($\frac{d^2L}{d\alpha^2}>0$ there, which part (d)(i) asks you to say.)

**11 (d)** $11.25=\frac{45}4>\frac{15\sqrt5}4$: the pole is longer than the
shortest segment through the corner, so $\boxed{\text{no}}$.

---

**12 (a)** Minimise $l^2=x^2\ln x+4$: $\frac{d}{dx}(l^2)=2x\ln x+x=x(2\ln x+1)=0$.
$x>0$, so $\ln x=-\frac12$ and $\boxed{x=e^{-1/2}}$.

**12 (b)** With one $t$: $\mathbf r_B-\mathbf r_A=(-18+10t,\ 1,\ 11-6t)$ and
$D^2=136t^2-492t+446$, smallest at $t=\frac{123}{68}$:

$$D_{\min}=\frac{\sqrt{1190}}{34}\approx\boxed{1.01}\ \text{km}$$

---

**13 (c)** $g(P)=kP-\frac kNP^2$ is a parabola in $P$ opening downwards, with
vertex at $\boxed{P=\frac N2}$. In the paper's language: $\frac{d^2P}{dt^2}=0$ at
$P=0,\frac N2,N$, and $\frac{d^2P}{dt^2}$ changes from positive to negative at
$\frac N2$, so $\frac{dP}{dt}$ has a maximum there.

**13 (d)** $\frac{dP}{dt}=k\cdot\frac N2\left(1-\frac12\right)=\boxed{\frac{kN}{4}}$.

---

**14 (f)** $(12/n)^n$: $12, 36, 64, 81, 79.6, 64$ for $n=1,\dots,6$, so
$\boxed{P(12)=81 \text{ at } n=4}$.

**14 (g)** The vertex is at $\frac{20}e\approx7.36$; compare
$(20/7)^7=1554.26$ and $(20/8)^8=1525.88$: $\boxed{P(20)\approx1550 \text{ at } n=7}$.

**14 (j)** The vertex is at $\frac{100}e\approx36.8$; compare
$(100/36)^{36}=9.3996\times10^{15}$ and $(100/37)^{37}=9.47406\times10^{15}$:
$\boxed{9.47\times10^{15}}$. The vertex value $e^{100/e}\approx9.48\times10^{15}$
is not a product of whole-number many parts.

---

## Timer

Solve $\arctan\frac{x+2}6-\arctan\frac x6=0.178$: $x=4.63047\ldots$ (the root
$-6.63$ is behind the runway's start, where the question's picture is not).
Differentiate in $t$:

$$\frac{d\theta}{dt}=\left(\frac{6}{(x+2)^2+36}-\frac{6}{x^2+36}\right)\frac{dx}{dt}=-0.0294199\ldots\cdot\frac{dx}{dt}$$

so $\frac{dx}{dt}=\frac{12.5}{-0.0294199\ldots}=-424.88\ldots$, and the speed is
$\boxed{425}$ km per hour — $x$ shrinks because the airplane approaches.
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
