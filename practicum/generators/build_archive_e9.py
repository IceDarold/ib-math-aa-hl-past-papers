"""Собирает архивный ноутбук E9: вся тема оптимизации и связанных скоростей подряд.

Двадцать четвёртый ноутбук формата и последний: после него у каждого
практикума карты есть архив. Практикум учит — лестница, теория, три уровня,
тренажёр, таймер. Архив не учит. Он даёт набивать руку: **вся тема подряд,
по тем же девяти приёмам, без единой строчки теории**. Двадцать девять
вопросов, 42 блока, 147 баллов.

Разметка взята из карточки calculus-optimization-rates.yaml: поле blocks у
каждого приёма. Два пункта ноября 2023 года — Q4(a) и Q8(b) Paper 2 TZ2 —
стоят здесь, а их близнецы из копии TZ1 той же бумаги — в E8 и C7. В архиве
они остаются с пометкой: они часть доли E9.

Части одного вопроса разнесены по своим приёмам. Частица мая 2022 TZ2 Q5 —
в §§ 1 и 3; частица мая 2024 TZ2 Q4 — в §§ 1, 2 и 3; частица мая 2025 TZ2
Q5 — в §§ 2 и 3; логистика мая 2022 TZ2 Q12 — в §§ 1 и 8; коридор мая 2023
TZ1 Q11 — дважды в § 6. Условие каждого пункта повторено целиком, насколько
оно нужно пункту.

Два ответа — выбор формулировки по хешу: смысл dP/dt (май 2022 TZ2 Q12(a))
и почему x_m даёт наибольший объём (май 2025 TZ3 Paper 3 Q2(e)). Их не из
чего вычислить. Остальные сорок четыре проверяются самой моделью вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_e9.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/calculus/archive-e9-optimisation-rates.ipynb')

MEANING = 'b'          # 1.8: смысл dP/dt
ENDS = 'a'             # 6.5: почему x_m — наибольший объём

ANSWERS = {
    # § 1. A rate at a moment
    'q1_1': '-0.651',
    'q1_2': '5.93',
    'q1_3': '[2.26, 2.96]',
    'q1_4': '0.591',
    'q1_5': '0.395',
    'q1_6': '3.14',
    'q1_7': '-0.996',
    'q1_8': f"'{MEANING}'",
    # § 2. Rest and turning
    'q2_1': '6.74',
    'q2_2': '5.74',
    'q2_3a': '1.69',
    'q2_3b': 'Interval(1.69, 6.12)',
    'q2_4': '-4.71',
    'q2_5': '-2.53',
    'q2_6': '0.986',
    # § 3. The largest value in motion
    'q3_1': '-1.84',
    'q3_2': '1.18',
    'q3_3': '2.72',
    'q3_4a': '1.81',
    'q3_4b': '4.19',
    'q3_4c': '-1.47',
    'q3_4d': '1.07',
    # § 4. A chain through one quantity
    'q4_1': '30',
    'q4_2': '0.140',
    'q4_3': '0.0531',
    'q4_4': '0.0261',
    # § 5. A chain through an angle
    'q5_1': '5.2',
    'q5_2': '425',
    'q5_3': '-0.724',
    # § 6. The optimum of a model
    'q6_1': '-3*sqrt(3)/2',
    'q6_2': 'Rational(2, 3)',
    'q6_3a': "'up'",
    'q6_3b': '15*sqrt(5)/4',
    'q6_4': "'no'",
    'q6_5': f"'{ENDS}'",
    # § 7. The shortest distance
    'q7_1': 'exp(Rational(-1, 2))',
    'q7_2': '1.01',
    'q7_3': '6.75',
    # § 8. The fastest change
    'q8_1': '1.58',
    'q8_2a': '1.76',
    'q8_2b': '5.20',
    'q8_3': 'N/2',
    'q8_4': 'k*N/4',
    # § 9. The best whole number
    'q9_1': '(81, 4)',
    'q9_2': '(1550, 7)',
    'q9_3': '9.47*10**15',
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
# E9 archive — optimisation and related rates, all of them

**Twenty-nine questions, 147 marks.** Every question the archive asks about how
fast things change and where they are best, from May 2021 to November 2025, in
the order of the nine techniques rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-e9-optimisation-rates.ipynb`.

| § | technique | parts | marks |
|---|---|---|---|
| 1 | A rate at a moment | 8 | 19 |
| 2 | Rest and turning | 6 | 17 |
| 3 | The largest value in motion | 4 | 14 |
| 4 | A chain through one quantity | 4 | 23 |
| 5 | A chain through an angle | 3 | 20 |
| 6 | The optimum of a model | 5 | 16 |
| 7 | The shortest distance | 3 | 14 |
| 8 | The fastest change | 4 | 16 |
| 9 | The best whole number | 3 | 8 |

The checks are the same ones the practicum uses and they store nothing. A
particle is handed over as the question gives it — `particle(v=...)` or
`particle(s=...)` — and the check **measures** its acceleration by moving time
a little; a related rate is the one that keeps the relation true when the
picture moves; a best value is found by looking at the whole interval, its
ends, and — when the letter counts things — every whole number. Three
significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** The particle of May 2024 TZ2
appears in §§ 1, 2 and 3; the logistic model of May 2022 TZ2 in §§ 1 and 8.
Each part repeats what it needs.

**Two parts are twins.** November 2023 Paper 2 was set as TZ1 and TZ2 and is
one paper. Its Q4(a) and Q8(b) stand here as the TZ2 copy; the TZ1 copies are
in the E8 and C7 archives.

Two answers are a choice between phrasings, `'a'` to `'d'`: there is nothing
to compute in them, and the check knows only a digest.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + particle, rate_of, dt

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ================================================================ § 1
md(r"""
---
# § 1. A rate at a moment

**Eight parts, 19 marks.** Name whose rate it is, then take the derivative at
the moment — or solve for the moment when the rate is given.
""")

md(r"""
### 1.1 — *May 2024 TZ1 Paper 2 Q10(c), 2 marks*

The height of water at Sule Skerry, in metres, is
$H(t)=1.63\sin\big(0.513(t-8.20)\big)+2.13$, where $t$ is the number of hours
after midnight. Find the rate of change of the height of the water when $t=13$,
in metres per hour.
""")

code(r"""
q1_1 = ...       # H'(13)

verify_rate('1.1', q1_1, 1.63*sin(0.513*(t - 8.20)) + 2.13, 13)
""")

md(r"""
### 1.2 — *May 2021 TZ1 Paper 2 Q4(c), 2 marks*

A particle moves in a straight line with velocity $v(t)=t\sin t-3$ m s⁻¹ for
$0\le t\le10$. Find the acceleration of the particle when $t=7$.
""")

code(r"""
q1_2 = ...       # the acceleration at t = 7

path = particle(v=t*sin(t) - 3, span=(0, 10))

verify_motion('1.2', q1_2, path, 'acceleration', 7)
""")

md(r"""
### 1.3 — *May 2022 TZ2 Paper 2 Q5(b), 3 marks*

A particle moves in a straight line with velocity
$v=\dfrac{(t^2+1)\cos t}{4}$ m s⁻¹, $0\le t\le3$. Find the times when the
particle's acceleration is $-1.9$ m s⁻².

*Both times, as a list.*
""")

code(r"""
q1_3 = [...]     # every time when a = -1.9

path = particle(v=(t**2 + 1)*cos(t)/4, span=(0, 3))

verify_when('1.3', q1_3, path, ('acceleration', -1.9), 'all')
""")

md(r"""
### 1.4 — *May 2025 TZ3 Paper 2 Q10(b), 2 marks*

Fiona's velocity during a race is $v(t)=\dfrac{8.14\,t}{\sqrt{t^2+0.2}}$ m s⁻¹,
$t\ge0$. Find the time when Fiona's acceleration is $4$ m s⁻².
""")

code(r"""
q1_4 = ...       # the time when a = 4

path = particle(v=8.14*t/sqrt(t**2 + 0.2), span=(0, oo))

verify_when('1.4', q1_4, path, ('acceleration', 4))
""")

md(r"""
### 1.5 — *May 2023 TZ2 Paper 2 Q5(a), 2 marks*

A particle moves in a straight line with velocity
$v(t)=4e^{-t/3}\cos\left(\dfrac t2-\dfrac\pi4\right)$ m s⁻¹ for $0\le t\le4\pi$.
Let $t_1$ be the first time when the particle's **acceleration** is zero. Find
$t_1$.
""")

code(r"""
q1_5 = ...       # t_1

path = particle(v=4*exp(-t/3)*cos(t/2 - pi/4), span=(0, 4*pi))

verify_when('1.5', q1_5, path, ('acceleration', 0))
""")

md(r"""
### 1.6 — *May 2022 TZ2 Paper 2 Q10(d), 6 marks*

The height of Plant A is $h_A(t)=\sin(2t+6)+9t+27$ cm and of Plant B
$h_B(t)=8t+32$ cm, $t$ in weeks, $0\le t\le9$. Find the total amount of time
when the rate of growth of Plant B was greater than the rate of growth of Plant
A.
""")

code(r"""
q1_6 = ...       # total time, weeks

verify_duration('1.6', q1_6, 8*t + 32, sin(2*t + 6) + 9*t + 27, (0, 9))
""")

md(r"""
### 1.7 — *May 2024 TZ2 Paper 2 Q4(a), 1 mark*

A particle moves in a straight line with velocity
$v(t)=1+e^{-t}-e^{-\sin 2t}$ m s⁻¹ for $0\le t\le2$. Find the velocity of the
particle at $t=2$.
""")

code(r"""
q1_7 = ...       # v(2)

path = particle(v=1 + exp(-t) - exp(-sin(2*t)), span=(0, 2))

verify_motion('1.7', q1_7, path, 'velocity', 2)
""")

md(r"""
### 1.8 — *May 2022 TZ2 Paper 2 Q12(a), 1 mark*

The population $P$ of a species of marsupial is modelled by
$\dfrac{dP}{dt}=kP\left(1-\dfrac PN\right)$, where $t$ is the time in years. In
the context of the model, interpret the meaning of $\dfrac{dP}{dt}$.

* `'a'` — the population of marsupials at time $t$
* `'b'` — the rate of change of the population with respect to time
* `'c'` — the growth in the population per year
* `'d'` — the largest population the island can sustain
""")

code(r"""
q1_8 = ...       # 'a', 'b', 'c' or 'd'

check_word('1.8', q1_8, """ + repr(digest(MEANING)) + r""")
""")

# ================================================================ § 2
md(r"""
---
# § 2. Rest and turning

**Six parts, 17 marks.** At rest: $v=0$. Changes direction: $v$ changes sign.
Displacement increasing: $v>0$. Only the roots inside the interval count, and
only as many as are asked.
""")

md(r"""
### 2.1 — *May 2021 TZ1 Paper 2 Q4(a), 2 marks*

A particle moves in a straight line with velocity $v(t)=t\sin t-3$ m s⁻¹ for
$0\le t\le10$. Find the smallest value of $t$ for which the particle is at rest.
""")

code(r"""
q2_1 = ...       # the first time at rest

path = particle(v=t*sin(t) - 3, span=(0, 10))

verify_when('2.1', q2_1, path, 'rest')
""")

md(r"""
### 2.2 — *November 2023 TZ2 Paper 2 Q4(a), 2 marks*

A particle moves along a straight line. Its displacement from a fixed point O
after $t$ seconds is $s(t)=4.3\sin\left(\sqrt{3t+5}\right)$ m, $0\le t\le10$. The
particle first comes to rest after $q$ seconds. Find $q$.

*The TZ1 copy of this part is in the E8 archive.*
""")

code(r"""
q2_2 = ...       # q

path = particle(s=4.3*sin(sqrt(3*t + 5)), span=(0, 10))

verify_when('2.2', q2_2, path, 'rest')
""")

md(r"""
### 2.3 — *May 2024 TZ1 Paper 2 Q4(a) and (b), 4 marks*

A particle moves in a straight line with velocity $v=2\sin(0.5t)+0.3t-2$ m s⁻¹
for $0\le t\le10$.

**(a)** Find the smallest value of $t$ when the particle changes direction.

**(b)** Find the range of values of $t$ for which the displacement of the
particle is increasing. *As `Interval(a, b)`.*
""")

code(r"""
q2_3a = ...      # the first change of direction
q2_3b = ...      # when the displacement increases

path = particle(v=2*sin(0.5*t) + 0.3*t - 2, span=(0, 10))

verify_when('2.3(a)', q2_3a, path, 'turn')
verify_while('2.3(b)', q2_3b, path, 'forward')
""")

md(r"""
### 2.4 — *May 2022 TZ1 Paper 2 Q4(b), 3 marks*

A particle moves along a straight line with velocity $v(t)=e^{\sin t}+4\sin t$
m s⁻¹ for $0\le t\le6$. Find the acceleration of the particle when it changes
direction.
""")

code(r"""
q2_4 = ...       # the acceleration at the change of direction

path = particle(v=exp(sin(t)) + 4*sin(t), span=(0, 6))

verify_motion('2.4', q2_4, path, 'acceleration', 'turn')
""")

md(r"""
### 2.5 — *May 2024 TZ2 Paper 2 Q4(c), 3 marks*

A particle moves in a straight line with velocity $v(t)=1+e^{-t}-e^{-\sin2t}$
m s⁻¹ for $0\le t\le2$. Find the acceleration of the particle at the instant it
changes direction.
""")

code(r"""
q2_5 = ...       # the acceleration at the change of direction

path = particle(v=1 + exp(-t) - exp(-sin(2*t)), span=(0, 2))

verify_motion('2.5', q2_5, path, 'acceleration', 'turn')
""")

md(r"""
### 2.6 — *May 2025 TZ2 Paper 2 Q5(c), 3 marks*

A particle P moves in a straight line with velocity $v(t)=e^{-\sin t}\cos(2t)$
m s⁻¹ for $0\le t\le5$. Find the acceleration when P changes direction for the
second time.
""")

code(r"""
q2_6 = ...       # the acceleration at the second change

path = particle(v=exp(-sin(t))*cos(2*t), span=(0, 5))

verify_motion('2.6', q2_6, path, 'acceleration', ('turn', 2))
""")

# ================================================================ § 3
md(r"""
---
# § 3. The largest value in motion

**Four questions, 14 marks.** Compare the vertices **and** the ends of the
interval. Speed is $|v|$.
""")

md(r"""
### 3.1 — *May 2022 TZ2 Paper 2 Q5(c), 2 marks*

A particle moves in a straight line with velocity
$v=\dfrac{(t^2+1)\cos t}{4}$ m s⁻¹, $0\le t\le3$. Find the particle's
acceleration when its speed is at its greatest.
""")

code(r"""
q3_1 = ...       # the acceleration when the speed is greatest

path = particle(v=(t**2 + 1)*cos(t)/4, span=(0, 3))

verify_motion('3.1', q3_1, path, 'acceleration', 'fastest')
""")

md(r"""
### 3.2 — *May 2024 TZ2 Paper 2 Q4(b), 2 marks*

A particle moves in a straight line with velocity $v(t)=1+e^{-t}-e^{-\sin2t}$
m s⁻¹ for $0\le t\le2$. Find the maximum velocity of the particle.
""")

code(r"""
q3_2 = ...       # the maximum velocity

path = particle(v=1 + exp(-t) - exp(-sin(2*t)), span=(0, 2))

verify_extreme('3.2', q3_2, path, 'velocity')
""")

md(r"""
### 3.3 — *May 2025 TZ2 Paper 2 Q5(a), 2 marks*

A particle P moves in a straight line with velocity $v(t)=e^{-\sin t}\cos(2t)$
m s⁻¹ for $0\le t\le5$. Find the maximum speed of P.
""")

code(r"""
q3_3 = ...       # the maximum speed

path = particle(v=exp(-sin(t))*cos(2*t), span=(0, 5))

verify_extreme('3.3', q3_3, path, 'speed')
""")

md(r"""
### 3.4 — *November 2025 TZ3 Paper 2 Q10(a) and (b), 8 marks*

A particle P moves in a straight line so that its displacement from a fixed
point O at time $t$ seconds is
$s(t)=2^{\left(1-\frac t5\right)}\sin\left(\dfrac{2\pi t}{3}\right)$ cm, $t\ge0$.

**(a)** Find (i) the maximum displacement of P from O; (ii) the maximum velocity
of P.

**(b)** Find (i) the minimum value of the displacement function $s(t)$;
(ii) the displacement of P from O when $t=3.5$.
""")

code(r"""
q3_4a = ...      # the maximum displacement
q3_4b = ...      # the maximum velocity
q3_4c = ...      # the minimum displacement
q3_4d = ...      # s(3.5)

path = particle(s=2**(1 - t/5)*sin(2*pi*t/3), span=(0, oo))

verify_extreme('3.4(a)(i)', q3_4a, path, 'displacement')
verify_extreme('3.4(a)(ii)', q3_4b, path, 'velocity')
verify_extreme('3.4(b)(i)', q3_4c, path, 'displacement', 'min')
verify_motion('3.4(b)(ii)', q3_4d, path, 'displacement', 3.5)
""")

# ================================================================ § 4
md(r"""
---
# § 4. A chain through one quantity

**Four questions, 23 marks.** The relation first, then the chain, then the state
of the moment, then the numbers.
""")

md(r"""
### 4.1 — *May 2023 TZ1 Paper 1 Q6, 5 marks*

The side lengths, $x$ cm, of an equilateral triangle are increasing at a rate of
$4$ cm s⁻¹. Find the rate at which the area of the triangle, $A$ cm², is
increasing when the side lengths are $5\sqrt3$ cm.

*No calculator: exact.*
""")

code(r"""
q4_1 = ...       # dA/dt

A = Symbol('A')
triangle = measure('triangle', (0, 0, 0), (x, 0, 0), (x/2, sqrt(3)*x/2, 0))

verify_related('4.1', q4_1, Eq(A, triangle), Eq(x, 5*sqrt(3)), {dt(x): 4}, dt(A),
               where={x: (0, 20)}, exact=True)
""")

md(r"""
### 4.2 — *May 2024 TZ2 Paper 2 Q6, 6 marks*

The volume of a spherical bubble increases at a constant rate of $5$ cm³ s⁻¹; its
initial volume can be taken as zero. Find the rate, in cm s⁻¹, at which the radius
of the bubble is increasing when the volume of the bubble is $20$ cm³.
""")

code(r"""
q4_2 = ...       # dr/dt when V = 20

V, r = symbols('V r')

verify_related('4.2', q4_2, Eq(V, 4*pi*r**3/3), Eq(V, 20), {dt(V): 5}, dt(r),
               where={r: (0, 10)})
""")

md(r"""
### 4.3 — *May 2022 TZ1 Paper 2 Q10(e), 6 marks*

A water container is modelled by rotating $y=\sqrt{x^2-1}$, $1\le x\le2$, about
the $y$-axis. When it is filled to a height of $h$ metres, the volume of water is
$V=\pi\left(\dfrac13h^3+h\right)$ m³, and the container is full at $h=\sqrt3$.
Water is added at a constant rate of $0.4$ m³ s⁻¹.

Find the rate of change of the height of the water when the container is filled
to half its maximum volume.
""")

code(r"""
q4_3 = ...       # dh/dt at half the maximum volume

V, h = symbols('V h')
full = pi*(sqrt(3)**3/3 + sqrt(3))

verify_related('4.3', q4_3, Eq(V, pi*(h**3/3 + h)), Eq(V, full/2), {dt(V): 0.4}, dt(h),
               where={h: (0, sqrt(3))})
""")

md(r"""
### 4.4 — *November 2022 Paper 2 Q8, 6 marks*

Liquid is poured into a round-bottomed flask at $2$ cm³ s⁻¹. The volume $V$ cm³
and height $h$ cm of the liquid satisfy $V=5\pi h^2-\dfrac13\pi h^3$, and the
liquid never reaches the neck: $0\le h\le10$. Find the rate of change of the
height of the liquid when the volume is $200$ cm³.
""")

code(r"""
q4_4 = ...       # dh/dt when V = 200

V, h = symbols('V h')

verify_related('4.4', q4_4, Eq(V, 5*pi*h**2 - pi*h**3/3), Eq(V, 200), {dt(V): 2}, dt(h),
               where={h: (0, 10)})
""")

# ================================================================ § 5
md(r"""
---
# § 5. A chain through an angle

**Three questions, 20 marks.** The picture gives the relation; the second
condition gives the state; *speed* has no sign, *how fast is it changing* does.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 2 Q9(b), 6 marks*

Two boats A and B travel due north; initially B is $50$ m due east of A. After
$t$ seconds A has travelled $x$ m and B $y$ m, and $\theta$ is the bearing of B
from A. Part (a) shows $y=x+50\cot\theta$. At time $T$ boat B has travelled $10$
m further than A, B is travelling at double the speed of A, and $\theta$ changes
at $-0.1$ rad s⁻¹. Find the speed of boat A at time $T$.
""")

code(r"""
q5_1 = ...       # the speed of boat A

y, theta = symbols('y theta')

verify_related('5.1', q5_1, Eq(y, x + 50*cot(theta)), Eq(y - x, 10),
               [Eq(dt(y), 2*dt(x)), Eq(dt(theta), -0.1)], dt(x),
               where={theta: (0, pi/2)}, size=True)
""")

md(r"""
### 5.2 — *May 2025 TZ3 Paper 2 Q9(b), 7 marks*

An airplane flies at a constant height of $6$ km towards a runway AB of length
$2$ km. With $GA=x$ km, the viewing angle of the runway is
$\theta=\arctan\left(\frac{x+2}6\right)-\arctan\left(\frac x6\right)$. When the
viewing angle is $0.178$ radians it is changing at $12.5$ radians per hour. Find
the speed of the airplane.
""")

code(r"""
q5_2 = ...       # the speed, km per hour

theta = Symbol('theta')

verify_related('5.2', q5_2, Eq(theta, atan((x + 2)/6) - atan(x/6)), Eq(theta, 0.178),
               {dt(theta): 12.5}, dt(x), where={x: (0, 50)}, size=True)
""")

md(r"""
### 5.3 — *November 2025 TZ1 Paper 2 Q9, 7 marks*

Triangle ABC has $AB=15$ cm, $BC=20$ cm, $AC=x$ cm and $A\hat BC=\theta$,
$0<\theta<\frac\pi2$. Angle $\theta$ is decreasing at $\frac\pi{60}$ radians per
minute. Determine how fast the length of AC is changing when the area of the
triangle is $140$ cm².
""")

code(r"""
q5_3 = ...       # dx/dt, with its sign

S, theta = symbols('S theta')
B_, C_, A_ = (0, 0, 0), (20, 0, 0), (15*cos(theta), 15*sin(theta), 0)

verify_related('5.3', q5_3, [Eq(x, distance(A_, C_)), Eq(S, measure('triangle', A_, B_, C_))],
               Eq(S, 140), {dt(theta): -pi/60}, dt(x), where={theta: (0, pi/2)})
""")

# ================================================================ § 6
md(r"""
---
# § 6. The optimum of a model

**Five parts, 16 marks.** $f'=0$ inside the domain, a reason for the kind, and
then the thing actually asked.
""")

md(r"""
### 6.1 — *May 2023 TZ2 Paper 1 Q10(d), 6 marks*

Triangle PQR is inscribed in $x^2+y^2=9$ with $P(-3,0)$, $Q(x,y)$ in the first
quadrant and $R(x,-y)$ in the fourth. Its area is $A=(x+3)\sqrt{9-x^2}$, and
$\dfrac{dA}{dx}=\dfrac{9-3x-2x^2}{\sqrt{9-x^2}}$. Find the $y$-coordinate of R
such that $A$ is a maximum.

*No calculator: exact.*
""")

code(r"""
q6_1 = ...       # the y-coordinate of R

verify_best('6.1', q6_1, (x + 3)*sqrt(9 - x**2), Interval.open(0, 3), 'max',
            report=-sqrt(9 - x**2), exact=True)
""")

md(r"""
### 6.2 — *November 2025 TZ3 Paper 1 Q8(c), 4 marks*

Astrid's time to reach Bronwyn is
$T=500\sec\theta+\dfrac{2500-1000\tan\theta}{3}$ seconds, $0<\tan\theta<\frac52$,
and she chooses $\theta$ to make $T$ as small as possible. The paper asks to
show that then $PX=400\tan\theta=160\sqrt5$ m.

Enter $\sin\theta$ at the quickest route — the line of working that carries the
marks.

*No calculator: exact.*
""")

code(r"""
q6_2 = ...       # sin(theta) at the minimum of T

theta = Symbol('theta')
T_walk = 500*sec(theta) + (2500 - 1000*tan(theta))/3

verify_best('6.2', q6_2, T_walk, Interval.open(0, atan(Rational(5, 2))), 'min',
            var=theta, report=sin(theta), exact=True)
""")

md(r"""
### 6.3 — *May 2023 TZ1 Paper 1 Q11(d), 3 marks*

A segment AB through the corner C of a passage has length
$L=\frac34\sec\alpha+6\,\mathrm{cosec}\,\alpha$, $0<\alpha<\frac\pi2$, and
$\frac{dL}{d\alpha}=0$ at $\alpha=\arctan2$.

**(i)** Justify that $L$ is a minimum there: which way is the graph of $L$
concave at $\alpha=\arctan2$? Enter `'up'` or `'down'`.

**(ii)** Determine this minimum value of $L$. *Exact.*
""")

code(r"""
q6_3a = ...      # 'up' or 'down'
q6_3b = ...      # the minimum of L

alpha = Symbol('alpha')
L = Rational(3, 4)*sec(alpha) + 6*cosec(alpha)

verify_concavity('6.3(i)', q6_3a, L, atan(2), var=alpha)
verify_best('6.3(ii)', q6_3b, L, Interval.open(0, pi/2), 'min', var=alpha, exact=True)
""")

md(r"""
### 6.4 — *May 2023 TZ1 Paper 1 Q11(e), 2 marks*

Two people need to carry a pole of length $11.25$ m horizontally from the
passageway of 6.3 into the room. Determine whether this is possible. Enter
`'yes'` or `'no'`.
""")

code(r"""
q6_4 = ...       # 'yes' or 'no'

alpha = Symbol('alpha')

verify_fits('6.4', q6_4, Rational(3, 4)*sec(alpha) + 6*cosec(alpha),
            Interval.open(0, pi/2), 11.25, var=alpha)
""")

md(r"""
### 6.5 — *May 2025 TZ3 Paper 3 Q2(e), 1 mark*

An open box is folded from an $a\times b$ sheet of cardboard: $V=x(a-2x)(b-2x)$,
$0\le x\le\frac a2$. Part (a) gives $V=0$ at $x=0$ and at $x=\frac a2$, and part
(d) shows a local maximum of $V$ at $x=x_m$ inside the interval. Explain why
$x_m$ gives the maximum volume of the box.

* `'a'` — $V$ is zero at both ends of the interval and positive at $x_m$, so the local maximum is the largest value
* `'b'` — because $\frac{dV}{dx}=0$ at $x_m$
* `'c'` — because $\frac{d^2V}{dx^2}<0$ at $x_m$
* `'d'` — because $x_m$ is the smaller solution of $\frac{dV}{dx}=0$
""")

code(r"""
q6_5 = ...       # 'a', 'b', 'c' or 'd'

check_word('6.5', q6_5, """ + repr(digest(ENDS)) + r""")
""")

# ================================================================ § 7
md(r"""
---
# § 7. The shortest distance

**Three questions, 14 marks.** Minimise the square; one parameter for two
moving points; the root only at the end.
""")

md(r"""
### 7.1 — *May 2025 TZ2 Paper 1 Q6(b), 6 marks*

$f(x)=\sqrt{x^2\ln x+4-x^2}$, $x>0$. The distance from the origin to a point of
the graph is $l=\sqrt{x^2\ln x+4}$. Find the $x$-coordinate of the point on the
graph of $f$ which is closest to the origin.

*No calculator: exact.*
""")

code(r"""
q7_1 = ...       # x of the closest point

verify_best('7.1', q7_1, sqrt(x**2*log(x) + 4), Interval.open(0, 10), 'min',
            report='place', exact=True)
""")

md(r"""
### 7.2 — *May 2022 TZ2 Paper 2 Q11(e), 5 marks*

Two airplanes have position vectors, in km, after $t$ minutes,
$\mathbf r_A=\begin{pmatrix}19\\-1\\1\end{pmatrix}+t\begin{pmatrix}-6\\2\\4\end{pmatrix}$
and
$\mathbf r_B=\begin{pmatrix}1\\0\\12\end{pmatrix}+t\begin{pmatrix}4\\2\\-2\end{pmatrix}$,
$0\le t\le2.5$. Let $D(t)$ be the distance between them. Find the minimum value
of $D(t)$.
""")

code(r"""
q7_2 = ...       # the minimum of D(t)

r_A = Matrix([19, -1, 1]) + t*Matrix([-6, 2, 4])
r_B = Matrix([1, 0, 12]) + t*Matrix([4, 2, -2])

verify_best('7.2', q7_2, distance(r_A, r_B), (0, 2.5), 'min', var=t)
""")

md(r"""
### 7.3 — *November 2023 TZ2 Paper 2 Q8(b), 3 marks*

For the points $A(0,p,2)$, $B(1,1,1)$, $C(p,0,4)$, $p>0$, part (a) shows

$$\vec{AB}\times\vec{AC}=\begin{pmatrix}2-3p\\-2-p\\p^2-2p\end{pmatrix}$$

Find the smallest possible value of $\left|\vec{AB}\times\vec{AC}\right|^2$.

*The TZ1 copy of this part is in the C7 archive.*
""")

code(r"""
q7_3 = ...       # the smallest |AB x AC|^2

p = Symbol('p')
product = Matrix([2 - 3*p, -2 - p, p**2 - 2*p])

verify_best('7.3', q7_3, product.dot(product), Interval.open(0, 20), 'min', var=p)
""")

# ================================================================ § 8
md(r"""
---
# § 8. The fastest change

**Four parts, 16 marks.** The quantity made largest is itself a rate: its
vertex is where the second derivative vanishes.
""")

md(r"""
### 8.1 — *May 2021 TZ1 Paper 2 Q12(e), 3 marks*

The population of a colony of ants is
$P=\dfrac{1200k}{1200+(k-1200)e^{-t/5}}$, $t\ge0$ in days, and part (d) gives
$k=2845.35$ $(2845.347\ldots)$. Find the value of $t$ when the rate of change of
the population is at its maximum.
""")

code(r"""
q8_1 = ...       # t at the fastest growth

k_ants = 2845.347
ants = 1200*k_ants/(1200 + (k_ants - 1200)*exp(-t/5))

verify_best('8.1', q8_1, rate_of(ants), (0, 40), 'max', var=t, report='place')
""")

md(r"""
### 8.2 — *May 2021 TZ2 Paper 2 Q11(d), 6 marks*

A bowl is formed by rotating $y=f(x)=\dfrac{ke^{x/2}}{1+e^x}$,
$0\le x\le\ln16$, about the $x$-axis, and part (b) gives $k=\sqrt{\frac{680}\pi}$.
$f(x)$ is the cross-sectional radius at distance $x$.

**(i)** By sketching the graph of a suitable derivative of $f$, find where the
cross-sectional radius of the bowl is decreasing most rapidly.

**(ii)** State the cross-sectional radius at this point.
""")

code(r"""
q8_2a = ...      # x where the radius falls fastest
q8_2b = ...      # the radius there

k_bowl = sqrt(680/pi)
radius = k_bowl*exp(x/2)/(1 + exp(x))

verify_best('8.2(i)', q8_2a, rate_of(radius, x), (0, log(16)), 'min', report='place')
verify_best('8.2(ii)', q8_2b, rate_of(radius, x), (0, log(16)), 'min', report=radius)
""")

md(r"""
### 8.3 — *May 2022 TZ2 Paper 2 Q12(c) and (d), 7 marks*

The population $P$ of a species is modelled by
$\dfrac{dP}{dt}=kP\left(1-\dfrac PN\right)$, with $k$, $N$ positive and
$0<P<N$.

**(c)** Find the value of $P$ at which the population increases at its maximum
rate. (The paper says: show that it is $\frac N2$, and justify.)

**(d)** Hence determine the maximum value of $\dfrac{dP}{dt}$ in terms of $k$
and $N$.
""")

code(r"""
q8_3 = ...       # the population at the maximum rate
q8_4 = ...       # the maximum of dP/dt

pop = Symbol('pop')             # the population of the question
growth = k*pop*(1 - pop/N)

verify_best('8.3', q8_3, growth, (0, N), 'max', var=pop, report='place',
            params={k: (0.7, 0.3, 2), N: (100, 7, 50)})
verify_best('8.4', q8_4, growth, (0, N), 'max', var=pop,
            params={k: (0.7, 0.3, 2), N: (100, 7, 50)})
""")

# ================================================================ § 9
md(r"""
---
# § 9. The best whole number

**Three parts, 8 marks.** $M_n(S)=\left(\frac Sn\right)^n$ is the maximum
product of $n$ positive numbers with sum $S$, and $P(S)$ is its largest value
over whole $n$. Compare the whole numbers either side of the vertex.
""")

md(r"""
### 9.1–9.3 — *May 2023 TZ1 Paper 3 Q2(f), (g), (j), 8 marks*

**9.1** Write down the value of $P(12)$ and the value of $n$ at which it occurs.

**9.2** Determine the value of $P(20)$ and the value of $n$ at which it occurs.

**9.3** Find the largest possible product of positive numbers whose sum is
$100$, in the form $a\times10^k$ with $1\le a<10$.

*Pairs as `(P, n)`.*
""")

code(r"""
q9_1 = ...       # (P(12), n)
q9_2 = ...       # (P(20), n)
q9_3 = ...       # the largest product with sum 100

n = Symbol('n')

verify_best('9.1', q9_1, (12/n)**n, (1, 40), 'max', var=n, report=('value', 'place'),
            integer=True)
verify_best('9.2', q9_2, (20/n)**n, (1, 40), 'max', var=n, report=('value', 'place'),
            integer=True)
verify_best('9.3', q9_3, (100/n)**n, (1, 200), 'max', var=n, integer=True)
""")

# ================================================================== решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1

**1.1** $H'(13)=\boxed{-0.651}$ m per hour $(-0.650622\ldots)$.

**1.2** $a=v'(7)=\sin7+7\cos7=\boxed{5.93}$ m s⁻² $(5.93430\ldots)$.

**1.3** $a(t)=v'(t)=-1.9$ on $[0,3]$ at $\boxed{t=2.26,\ 2.96}$ s.

**1.4** Solving $v'(t)=4$: $\boxed{t=0.591}$ s.

**1.5** $v'(t)=0$ first at the local maximum of $v$:
$\boxed{t_1=\arctan\frac5{12}\approx0.395}$ s.

**1.6** $h_B'>h_A'$ means $\cos(2t+6)<-\frac12$: three stretches of length
$\frac\pi3$, total $\boxed{\pi\approx3.14}$ weeks.

**1.7** $v(2)=1+e^{-2}-e^{-\sin4}=\boxed{-0.996}$ m s⁻¹.

**1.8** $\boxed{\text{b}}$ — the rate of change of the population with respect
to time. *"Growth per year"* is explicitly not accepted.

---

## § 2

**2.1** $t\sin t=3$ first at $\boxed{t=6.74}$ s; $9.09$ is the second root and
is not asked.

**2.2** $v=\frac{ds}{dt}=\frac{3\cdot4.3\cos\sqrt{3t+5}}{2\sqrt{3t+5}}=0$ when
$\sqrt{3t+5}=\frac{3\pi}2$ (the first such value above $\sqrt5$), so
$\boxed{q=5.74}$.

**2.3** **(a)** $\boxed{t=1.69}$; **(b)** $v>0$ between the roots:
$\boxed{1.69<t<6.12}$.

**2.4** $v=0$ at $t=3.34692\ldots$; $a=v'(3.346\ldots)=\boxed{-4.71}$ m s⁻².

**2.5** $v=0$ at $t=1.65840\ldots$; $a=\boxed{-2.53}$ m s⁻².

**2.6** $v=0$ at $\frac\pi4,\frac{3\pi}4,\frac{5\pi}4$; at the second,
$a=2e^{-1/\sqrt2}=\boxed{0.986}$ m s⁻².

---

## § 3

**3.1** $|v|$ is greatest at the end $t=3$; $a=v'(3)=\boxed{-1.84}$ m s⁻².

**3.2** $v'(t)=0$ at $t=0.405833\ldots$; $v_{\max}=\boxed{1.18}$ m s⁻¹.

**3.3** The lowest point of $v$ is $(4.712\ldots,\,-e)$: maximum speed
$\boxed{e\approx2.72}$ m s⁻¹.

**3.4** **(a)(i)** $\boxed{1.81}$ cm. **(ii)** The graph of $s$ is steepest at
$t=0$: $v(0)=\frac{4\pi}3=\boxed{4.19}$ cm s⁻¹. **(b)(i)** $\boxed{-1.47}$ cm.
**(ii)** $s(3.5)=\boxed{1.07}$ cm.

---

## § 4

**4.1** $A=\frac{\sqrt3}4x^2$, $\frac{dA}{dt}=\frac{\sqrt3}2x\cdot4=\boxed{30}$
cm² s⁻¹ at $x=5\sqrt3$.

**4.2** $r=\left(\frac{15}\pi\right)^{1/3}=1.68389\ldots$ and
$\frac{dr}{dt}=\frac5{4\pi r^2}=\boxed{0.140}$ cm s⁻¹.

**4.3** $V_{\max}=2\sqrt3\pi$; half is $\sqrt3\pi$, reached at $h=1.1818\ldots$.
$\frac{dV}{dh}=\pi(h^2+1)$, so $\frac{dh}{dt}=\frac{0.4}{\pi(h^2+1)}=\boxed{0.0531}$
m s⁻¹.

**4.4** $h=4.20648\ldots$, $\frac{dh}{dt}=\frac{2}{10\pi h-\pi h^2}=\boxed{0.0261}$
cm s⁻¹.

---

## § 5

**5.1** $\frac{dx}{dt}=-50\,\mathrm{cosec}^2\theta\,\frac{d\theta}{dt}$ with
$\cot\theta=\frac15$: $\frac{dx}{dt}=-50\cdot\frac{26}{25}\cdot(-0.1)=\boxed{5.2}$
m s⁻¹.

**5.2** $x=4.63047\ldots$, $\frac{d\theta}{dx}=-0.0294199\ldots$, so
$\frac{dx}{dt}=-424.88\ldots$ and the speed is $\boxed{425}$ km h⁻¹.

**5.3** $\sin\theta=\frac{14}{15}$, $x^2=625-600\cos\theta$,
$\frac{dx}{dt}=\frac{600\sin\theta}{2x}\cdot\left(-\frac\pi{60}\right)=\boxed{-0.724}$
cm per minute.

---

## § 6

**6.1** $9-3x-2x^2=0$ gives $x=\frac32$ (reject $-3$), and
$y_R=-\sqrt{9-\frac94}=\boxed{-\frac{3\sqrt3}2}$.

**6.2** $\frac{dT}{d\theta}=500\sec\theta\tan\theta-\frac{1000}3\sec^2\theta=0$
gives $\boxed{\sin\theta=\frac23}$, so $\tan\theta=\frac2{\sqrt5}$ and
$PX=160\sqrt5$.

**6.3** **(i)** $\frac{d^2L}{d\alpha^2}=\frac{45}4\sqrt5>0$: concave
$\boxed{\text{up}}$, so with $\frac{dL}{d\alpha}=0$ it is a minimum.
**(ii)** $L_{\min}=\frac34\sqrt5+6\cdot\frac{\sqrt5}2=\boxed{\frac{15\sqrt5}4}$.

**6.4** $11.25=\frac{45}4>\frac{15\sqrt5}4\approx8.39$: $\boxed{\text{no}}$.

**6.5** $\boxed{\text{a}}$ — the largest value on a closed interval is at a
vertex or an end; the ends give $0$ and $V(x_m)>0$.

---

## § 7

**7.1** Minimise $l^2=x^2\ln x+4$: $2x\ln x+x=0$, $x>0$, $\boxed{x=e^{-1/2}}$.

**7.2** $D^2=136t^2-492t+446$, least at $t=\frac{123}{68}$:
$D_{\min}=\frac{\sqrt{1190}}{34}=\boxed{1.01}$ km.

**7.3** $\left|\vec{AB}\times\vec{AC}\right|^2=p^4-4p^3+14p^2-8p+8$, least at
$p=0.3264\ldots$: $\boxed{6.75}$.

---

## § 8

**8.1** Growth is fastest at $P=\frac k2$:
$t=5\ln\frac{k-1200}{1200}=\boxed{1.58}$ days.

**8.2** **(i)** The minimum of $f'$ (or the zero of $f''$):
$e^x=3+2\sqrt2$, $\boxed{x=1.76}$. **(ii)**
$f(1.76\ldots)=\sqrt{\frac{85}\pi}=\boxed{5.20}$ cm.

**8.3** $kP\left(1-\frac PN\right)$ has its vertex at $\boxed{P=\frac N2}$, where
$\frac{d^2P}{dt^2}$ changes from positive to negative.

**8.4** $k\cdot\frac N2\cdot\frac12=\boxed{\frac{kN}4}$.

---

## § 9

**9.1** $12, 36, 64, 81, 79.6, 64$: $\boxed{P(12)=81,\ n=4}$.

**9.2** $(20/7)^7=1554.26$ beats $(20/8)^8=1525.88$: $\boxed{P(20)=1550,\ n=7}$.

**9.3** $(100/37)^{37}=9.474\times10^{15}$ beats $(100/36)^{36}=9.400\times10^{15}$:
$\boxed{9.47\times10^{15}}$.
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
