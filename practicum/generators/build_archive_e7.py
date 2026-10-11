"""Собирает архивный ноутбук E7: вся тема дифференциальных уравнений подряд.

Двадцать пятый ноутбук формата и последний из архивов, которых не хватало
в начале серии. Практикум учит — лестница, теория, три уровня, тренажёр,
таймер. Архив не учит. Он даёт набивать руку: **вся тема подряд, по тем же
семи приёмам, без единой строчки теории**. Тридцать семь вопросов, 64 блока,
255 баллов.

Разметка взята из карточки calculus-differential-equations.yaml: поле blocks
у каждого приёма. Ноябрь 2023 года задвоился: Paper 2 TZ1 и TZ2 — одна
бумага (вопрос 9 совпадает слово в слово), Paper 3 той сессии общий. Четыре
блока прогнаны классификацией дважды, 20 баллов; в архиве они стоят по
одному разу, с пометкой.

Части одного вопроса разнесены по своим приёмам. Логистика мая 2021 TZ1 Q12 —
в § 3; её близнец мая 2022 TZ2 Q12 — тоже в § 3, а начало того же вопроса
уехало в архив E9. Исследование мая 2023 TZ2 Q12 разошлось по §§ 4, 6 и 7;
май 2024 TZ2 Q12 — по §§ 5, 6 и 7; ноябрь 2025 TZ3 Q12 — по §§ 4, 6 и 7;
волки ноября 2025 TZ1 Paper 3 — по §§ 2 и 6. Условие каждого пункта повторено
целиком, насколько оно нужно пункту.

Последний раздел — система двух уравнений (ноябрь 2021, Paper 3, 30 баллов).
Семи приёмов темы в нём нет: он сводит систему к одному уравнению второго
порядка и решает его показательной подстановкой. В программе это тот же
подраздел, и в архиве он стоит отдельным разделом, а не притворяется приёмом.

Шесть ответов — выбор формулировки по хешу: это баллы R1 за обоснование, где
считать нечего, а балл дают за слова. Остальные шестьдесят три проверяются
самой моделью вопроса — уравнением, полем, ломаной.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_e7.py подставляет эталоны
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
    ROOT, 'practicum/calculus/archive-e7-differential-equations.ipynb')

STEADY = 'b'           # 2.5(ii): что значит dx/dt = 0 при x = 200
ASYMPTOTE = 'a'        # 3.3(iii): отчего Эйлер дал 10.7 вместо 27.3
POSITIVE = 'c'         # 5.3(f): отчего наклон положителен
MORE_REAL = 'b'        # 6.7(ii): что сказать о поправленной модели
STEEP = 'a'            # 7.3(ii): отчего приближение плохое
UPPER = 'b'            # 7.4(ii): отчего Эйлер не уходит на нижнюю ветвь

ANSWERS = {
    # § 1. Straight integration
    'q1_1': 'sin(x - pi/4) + 1',
    'q1_2': '6380000',
    # § 2. Separating the variables
    'q2_1': '(1 + v0)*exp(-t) - 1',
    'q2_2': '4 - 2*exp(-x/10)',
    'q2_3': 'Eq(x**2 + y**2, k)',
    'q2_4a': '-4',
    'q2_4b': '-4 - pi',
    'q2_5a': '0',
    'q2_5b': f"'{STEADY}'",
    'q2_5c': '200*exp(-A*exp(-a*t))',
    'q2_5d': 'log(5)',
    'q2_5e': '0.0855',
    'q2_5f': '101',
    # § 3. Partial fractions after separating
    'q3_1a': '1200*k/((k - 1200)*exp(-t/5) + 1200)',
    'q3_1b': '2845',
    'q3_2a': 'Eq(k*t, log(pop*(N - P0)/(P0*(N - pop))))',
    'q3_2b': 'log(3)/5',
    'q3_3a': '(8*x + x**4)/(4 - x**3)',
    'q3_3b': '27.3',
    'q3_3c': f"'{ASYMPTOTE}'",
    'q3_4a': '3*exp(x - 2*atan(x))',
    'q3_4b': '2.58786',
    # § 4. The substitution y = vx
    'q4_1': 'v**2 - v - 2',
    'q4_2a': 'Eq(y**2, 4*x**2*(1 - log(x)))',
    'q4_2b': '[sqrt(2), -sqrt(2)]',
    'q4_3a': 'x*sqrt((9*x**4 - 1)/2)',
    'q4_3b': '2.71',
    'q4_3c': '1/sqrt(3)',
    'q4_4a': '(y - x)/(y + x)',
    'q4_4b': 'Eq(log(1 + (y/x)**2)/2 + atan(y/x) + log(x), D)',
    'q4_5': 'Eq(x**2 - 2*x*y - y**2, 4)',
    'q4_6a': 'Eq(x**2, A*(x + y)/(x - y))',
    'q4_6b': 'x*(x**2 - A)/(x**2 + A)',
    'q4_7': 'Eq(x**6*(2*y - x)**3, 2*(x + 2*y))',
    # § 5. The integrating factor
    'q5_1': 'log(2*x)/x - 1/x + 3/(2*x**2)',
    'q5_2': '3*exp(x) - x - 1',
    'q5_3a': 'sqrt(cot(x))',
    'q5_3b': 'x*sqrt(tan(x))',
    'q5_3c': '2.53',
    'q5_3d': f"'{POSITIVE}'",
    'q5_4': 'x**2 - 2*x - 3 + C*exp(-x)',
    'q5_5': '(pi - x*cot(x) + log(sin(x)))/x**3',
    # § 6. Euler's method
    'q6_1': '10.7',
    'q6_2': '2.58046',
    'q6_3': '2.65',
    'q6_4a': '2.098',
    'q6_4b': '0.000479',
    'q6_5': '1.98',
    'q6_6': '1.26',
    'q6_7a': '89',
    'q6_7b': f"'{MORE_REAL}'",
    'q6_8a': '-1.7',
    'q6_8b': '1.07',
    # § 7. Which side the tangents lie
    'q7_1': "'up'",
    'q7_2': "'up'",
    'q7_3a': f"'{STEEP}'",
    'q7_3b': "'up'",
    'q7_4a': "'over'",
    'q7_4b': f"'{UPPER}'",
    'q7_5': "'up'",
    # § 8. Two equations at once
    'q8_1': 'A*exp(t)',
    'q8_2': '(-A*t + D)*exp(t)',
    'q8_3': '(2, 0)',
    'q8_4': 'B*exp(2*t)',
    'q8_5': 'B*exp(2*t)/2 + C',
    'q8_6': '-B*exp(2*t)/2 + C',
    'q8_7': '(2, 3)',
    'q8_8': '[3, -1]',
    'q8_9': 'F*exp(3*t) + G*exp(-t)',
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
# E7 archive — differential equations, all of them

**Thirty-seven questions, 255 marks.** Every question the archive asks about a
first-order differential equation, from May 2021 to November 2025, in the order
of the seven techniques rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-e7-differential-equations.ipynb`.

| § | technique | parts | marks |
|---|---|---|---|
| 1 | Straight integration | 2 | 10 |
| 2 | Separating the variables | 11 | 35 |
| 3 | Partial fractions after separating | 9 | 39 |
| 4 | The substitution $y=vx$ | 12 | 64 |
| 5 | The integrating factor | 8 | 37 |
| 6 | Euler's method | 11 | 29 |
| 7 | Which side the tangents lie | 7 | 11 |
| 8 | Two equations at once | 9 | 30 |

The checks are the same ones the practicum uses and they store nothing. An
equation is a field of slopes, and the field is all a check is given. Your
solution it substitutes into the equation. An implicit answer it walks along
your own curve: it sets the constant so the curve passes through a sample
point, and the slope there has to be the one the field asks for — so
$x^2+y^2=k$, $y^2=k-x^2$ and $(x^2+y^2)^2=k$ all pass, as they do in the
markscheme. A value of the solution it reaches by going along the field from
the initial condition, which is why the questions whose integral has no closed
form are checked as well. Euler's broken line it builds itself, with the same
step and no rounding on the way — and that is how it knows what the answer
does not show: whether the line stays below the solution or above it. Three
significant figures, unless the question asks otherwise.

**Parts of one question are split by technique.** The investigation of May 2023
TZ2 appears in §§ 4, 6 and 7; May 2024 TZ2 in §§ 5, 6 and 7; November 2025 TZ3
in §§ 4, 6 and 7; the wolves of November 2025 TZ1 Paper 3 in §§ 2 and 6. Each
part repeats what it needs.

**Twins.** November 2023 Paper 2 was set as TZ1 and TZ2 and is one paper — its
question 9 is the same word for word — and its Paper 3 was common to both
zones. Those four questions stand here once.

**The last section is not a technique.** A system of two equations (November
2021, Paper 3, 30 marks) is in the same syllabus subtopic, but it is solved by
collapsing the system into one second-order equation and trying $y=Fe^{\lambda t}$.
It stands apart rather than pretending to be the eighth rung.

Six answers are a choice between phrasings, `'a'` to `'d'`: those are the
reason marks of the topic, where nothing is computed and the mark is for the
words. The check knows only a digest of them.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + verify_ode, verify_family, verify_euler

language('en')                 # this notebook is in English, and so are the checks

# letters the questions use beyond the ones kit already has
a, m, D, F, G, X, Y = symbols('a m D F G X Y')
v0, P0, pop, w = symbols('v0 P0 pop w')

print('ready; sympy', sp.__version__)
""")

# ================================================================ § 1
md(r"""
---
# § 1. Straight integration

**Two parts, 10 marks.** There is no $y$ on the right-hand side, so the
equation is an integral with a constant waiting for the initial condition.
""")

md(r"""
### 1.1 — *November 2021 Paper 1 Q1, 4 marks*

Given that $\dfrac{dy}{dx}=\cos\left(x-\dfrac\pi4\right)$ and $y=2$ when
$x=\dfrac{3\pi}4$, find $y$ in terms of $x$.
""")

code(r"""
q1_1 = ...       # y in terms of x

verify_ode('1.1', q1_1, cos(x - pi/4), ic=(3*pi/4, 2))
""")

md(r"""
### 1.2 — *May 2025 TZ1 Paper 2 Q3, 6 marks*

A population $P$ has a rate of change modelled by
$\dfrac{dP}{dt}=-104000e^{-0.0145t}$, where $t$ is the time measured in years
since the start of 2022. At the start of 2022 the population was
$6.78\times10^6$. Based on this model, find the predicted population at the
start of 2026.
""")

code(r"""
q1_2 = ...       # the population at t = 4

verify_solved('1.2', q1_2, -104000*exp(-0.0145*t), (0, 6.78*10**6), 4,
              var=t, dep=w)
""")

# ================================================================ § 2
md(r"""
---
# § 2. Separating the variables

**Eleven parts, 35 marks.** Everything with $y$ to one side, everything with
$x$ to the other, one constant, and then the initial condition.
""")

md(r"""
### 2.1 — *May 2021 TZ2 Paper 1 Q11(a), 6 marks*

The acceleration, $a$ m s⁻², of a particle moving in a horizontal line at time
$t$ seconds, $t\ge0$, is given by $a=-(1+v)$, where $v$ m s⁻¹ is the particle's
velocity and $v>-1$. At $t=0$ the particle is at a fixed origin $O$ and has
initial velocity $v_0$ m s⁻¹.

By solving an appropriate differential equation, show that the particle's
velocity at time $t$ is given by $v(t)=(1+v_0)e^{-t}-1$.

*Write the velocity; the letter is `v0`.*
""")

code(r"""
q2_1 = ...       # v in terms of t and v0

verify_ode('2.1', q2_1, -(1 + v), ic=(0, v0), var=t, dep=v)
""")

md(r"""
### 2.2 — *November 2023 Paper 2 Q9(b), 5 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{4-y}{10}$, where
$y=2$ when $x=0$. By solving the differential equation, show that
$y=4-2e^{-\frac x{10}}$.

*This paper was set as TZ1 and TZ2 and is one paper; the question appears here
once.*
""")

code(r"""
q2_2 = ...       # y in terms of x

verify_ode('2.2', q2_2, (4 - y)/10, ic=(0, 2))
""")

md(r"""
### 2.3 — *November 2023 Paper 3 Q2(a)(iii), 2 marks*

A family of straight lines $L$ has equation $y=mx$, where $m$ is a parameter.
Each member of $L$ meets every member of a family of curves $C$ at right
angles, so the gradient of $C$ is $\dfrac{dy}{dx}=-\dfrac xy$.

By solving that differential equation, show that the family of curves $C$ has
equation $x^2+y^2=k$, where $k$ is a parameter.

*Write the family as an equation, with `k` for the parameter.*
""")

code(r"""
q2_3 = ...       # Eq(..., ...) — the family of curves

verify_family('2.3', q2_3, -x/y)
""")

md(r"""
### 2.4 — *November 2025 TZ1 Paper 1 Q7, 8 marks*

Consider the differential equation $\dfrac{dy}{dx}=y^2\cos^2x$, $y\ne0$. Its
solutions can be expressed in the form

$$y=\frac a{2x+\sin 2x+b},$$

where $a$ and $b$ are constants such that $a\in\mathbb Z$ and
$b\in\mathbb R$.

**(a)** By solving the differential equation, find the value of $a$. *[6]*

**(b)** Given that $y=1$ when $x=\dfrac\pi2$, find the value of $b$. *[2]*
""")

code(r"""
q2_4a = ...      # a
q2_4b = ...      # b

form = a/(2*x + sin(2*x) + B)          # the form the question gives

verify_ode('2.4(a)', put(form, a=q2_4a), y**2*cos(x)**2)
verify_ode('2.4(b)', put(form, a=q2_4a, B=q2_4b), y**2*cos(x)**2, ic=(pi/2, 1))
""")

md(r"""
### 2.5 — *November 2025 TZ1 Paper 3 Q2(b), 14 marks*

Historically a population of wolves in an area had a stable size of 200. After
some years of disruption the population was reduced to 40 wolves, and the area
then became a protected space. Let $x$ be the size of the wolf population and
$t$ the time in years since the area became protected; at $t=0$ there were 40
wolves, and at $t=5$ there were 70.

The Gompertz model satisfies $\dfrac{dx}{dt}=ax\ln\left(\dfrac{200}x\right)$,
$a\in\mathbb R^+$.

**(i)** Write down the value of $\dfrac{dx}{dt}$ when $x=200$. *[1]*

**(ii)** Interpret your answer to (i) in context. *[1]*

* `'a'` — the population reaches 200 after a finite time
* `'b'` — the population is steady at 200: that is the equilibrium size
* `'c'` — 200 is the largest population the area could ever hold
* `'d'` — the population grows fastest when it reaches 200

**(iii)** It can be shown that $\dfrac{d}{dx}\ln(\ln 200-\ln x)
=\dfrac{-1}{x\ln\left(\frac{200}x\right)}$. Hence, use separation of variables
to show that the general solution can be written as
$\ln x=\ln 200-Ae^{-at}$, where $A$ is an arbitrary positive constant. *[5]*

*Write the same solution as $x=f(t)$, with the letters `A` and `a`. In the
cell the population is `w`: `x` is already the letter of the horizontal axis.*

**(iv)** Use the size of the population at $t=0$ to find the value of $A$.
Give your answer in the form $A=\ln p$. *[2]*

**(v)** Use the size of the population at $t=5$ to show that $a=0.0855$,
correct to three significant figures. *[2]*

**(vi)** Use the Gompertz model to predict the size of the wolf population at
$t=10$. Give your answer correct to the nearest whole number. *[3]*
""")

code(r"""
q2_5a = ...      # dx/dt when x = 200
q2_5b = ...      # 'a', 'b', 'c' or 'd'
q2_5c = ...      # w in terms of t, with A and a
q2_5d = ...      # A
q2_5e = ...      # a, to 3 s.f.
q2_5f = ...      # the population at t = 10, to the nearest whole number

field = a*w*log(200/w)                 # the Gompertz model of the question

verify_field('2.5(i)', q2_5a, field, (0, 200), var=t, dep=w)
check_word('2.5(ii)', q2_5b, """ + repr(digest(STEADY)) + r""")
verify_ode('2.5(iii)', q2_5c, field, var=t, dep=w, letters=2)
verify_ode('2.5(iv)', put(q2_5c, A=q2_5d), field, ic=(0, 40), var=t, dep=w)
verify_letter('2.5(v)', q2_5e, put(q2_5c, A=q2_5d), a, (5, 70), var=t)
verify_solved('2.5(vi)', q2_5f, put(field, a=q2_5e), (0, 40), 10,
              var=t, dep=w, whole=True)
""")

# ================================================================ § 3
md(r"""
---
# § 3. Partial fractions after separating

**Nine parts, 39 marks.** After separating, the left side is a fraction whose
denominator factorises. The logistic model lives here: $P(k-P)$ in the
denominator is the standard source of the two logarithms.
""")

md(r"""
### 3.1 — *May 2021 TZ1 Paper 2 Q12(c)(d), 11 marks*

Consider $P$, the population of a colony of ants, which has an initial value of
1200. The rate of change of the population can be modelled by

$$\frac{dP}{dt}=\frac{P(k-P)}{5k},$$

where $t$ is the time measured in days, $t\ge0$, and $k$ is the upper bound for
the population.

**(c)** By solving the differential equation, show that
$P=\dfrac{1200k}{(k-1200)e^{-\frac t5}+1200}$. *[8]*

**(d)** At $t=10$ the population of the colony has doubled in size from its
initial value. Find the value of $k$, giving your answer correct to four
significant figures. *[3]*

*The population here is `pop`.*
""")

code(r"""
q3_1a = ...      # pop in terms of t and k
q3_1b = ...      # k, to 4 s.f.

verify_ode('3.1(c)', q3_1a, pop*(k - pop)/(5*k), ic=(0, 1200), var=t, dep=pop)
verify_letter('3.1(d)', q3_1b, q3_1a, k, (10, 2400), var=t, digits=4)
""")

md(r"""
### 3.2 — *May 2022 TZ2 Paper 2 Q12(e)(f), 9 marks*

The population $P$ of a species of marsupial is modelled by

$$\frac{dP}{dt}=kP\left(1-\frac PN\right),$$

where $t$ is the time in years, $N$ is the maximum population the island can
sustain and $P_0$ is the population at $t=0$.

**(e)** By solving the differential equation, show that
$kt=\ln\left[\dfrac P{N-P}\cdot\dfrac{N-P_0}{P_0}\right]$. *[7]*

**(f)** After 10 years the population has grown to $3P_0$, and $N=4P_0$. Find
the value of $k$. *[2]*

*Write (e) as an equation; the population is `pop`, and the letters are `k`,
`N` and `P0`.*
""")

code(r"""
q3_2a = ...      # Eq(k*t, ...)
q3_2b = ...      # k, exactly

verify_family('3.2(e)', q3_2a, k*pop*(1 - pop/N), var=t, dep=pop, par=P0,
              params={k: 0.3, N: 1000}, ic=(0, P0),
              points=[(0.5, 150), (2, 400), (3, 700)])
verify_letter('3.2(f)', q3_2b, q3_2a, k, {t: 10, pop: 3*P0, N: 4*P0})
""")

md(r"""
### 3.3 — *May 2022 TZ1 Paper 2 Q12(c), 12 marks*

Consider the differential equation $x^2\dfrac{dy}{dx}=y^2-2x^2$ for $x>0$ and
$y>2x$. It is given that $y=3$ when $x=1$, and — from § 4.1 — that the
substitution $y=vx$ turns the equation into $x\dfrac{dv}{dx}=v^2-v-2$.

**(i)** By solving the differential equation, show that
$y=\dfrac{8x+x^4}{4-x^3}$. *[—]*

**(ii)** Find the actual value of $y$ when $x=1.5$. *[—]*

**(iii)** Using the graph of $y=\dfrac{8x+x^4}{4-x^3}$, suggest a reason why the
approximation given by Euler's method in § 6.1 is not a good estimate of the
actual value of $y$ at $x=1.5$. *[12 marks for (i)–(iii)]*

* `'a'` — the curve has a vertical asymptote at $x=\sqrt[3]4\approx1.59$, and
  the gradient changes rapidly well before it
* `'b'` — a step length of $0.1$ is too small over an interval of length $0.5$
* `'c'` — the curve is concave down there, so the tangents overshoot it
* `'d'` — the starting value $y=3$ is not given accurately enough
""")

code(r"""
q3_3a = ...      # y in terms of x
q3_3b = ...      # y(1.5)
q3_3c = ...      # 'a', 'b', 'c' or 'd'

verify_ode('3.3(i)', q3_3a, (y**2 - 2*x**2)/x**2, ic=(1, 3))
verify_solved('3.3(ii)', q3_3b, (y**2 - 2*x**2)/x**2, (1, 3), 1.5, euler=0.1)
check_word('3.3(iii)', q3_3c, """ + repr(digest(ASYMPTOTE)) + r""")
""")

md(r"""
### 3.4 — *May 2023 TZ1 Paper 2 Q12(d), 7 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{x^2y-y}{x^2+1}$,
where $y>0$ and $y=3$ when $x=0$. It is given that
$\dfrac{x^2-1}{x^2+1}\equiv1-\dfrac2{x^2+1}$.

**(i)** Solve the differential equation. Give your answer in the form
$y=f(x)$. *[—]*

**(ii)** Hence, find the value of $y$ when $x=0.15$. Give your answer correct
to six significant figures. *[7 marks for (i)–(ii)]*
""")

code(r"""
q3_4a = ...      # y in terms of x
q3_4b = ...      # y(0.15), to 6 s.f.

verify_ode('3.4(i)', q3_4a, (x**2*y - y)/(x**2 + 1), ic=(0, 3))
verify_solved('3.4(ii)', q3_4b, (x**2*y - y)/(x**2 + 1), (0, 3), 0.15, digits=6,
              euler=0.03)
""")

# ================================================================ § 4
md(r"""
---
# § 4. The substitution $y=vx$

**Twelve parts, 64 marks.** The biggest rung of the topic. The right-hand side
depends only on the ratio $y/x$: put $y=vx$, remember that
$\dfrac{dy}{dx}=v+x\dfrac{dv}{dx}$, and what is left separates. Five of the
seven questions here are *show that* or ask for an exact form, so the marks are
for the working — the calculator is of no use at all.
""")

md(r"""
### 4.1 — *May 2022 TZ1 Paper 2 Q12(b), 3 marks*

Consider the differential equation $x^2\dfrac{dy}{dx}=y^2-2x^2$ for $x>0$ and
$y>2x$, with $y=3$ when $x=1$.

Use the substitution $y=vx$ to show that $x\dfrac{dv}{dx}=v^2-v-2$.

*Write the right-hand side in terms of `v`.*
""")

code(r"""
q4_1 = ...       # h(v), where x·dv/dx = h(v)

verify_substitution('4.1', q4_1, (y**2 - 2*x**2)/x**2)
""")

md(r"""
### 4.2 — *November 2022 Paper 1 Q9, 10 marks*

Consider the homogeneous differential equation
$\dfrac{dy}{dx}=\dfrac{y^2-2x^2}{xy}$, where $x,y\ne0$. It is given that $y=2$
when $x=1$.

**(a)** By using the substitution $y=vx$, solve the differential equation. Give
your answer in the form $y^2=f(x)$. *[8]*

**(b)** The points of zero gradient on the curve $y^2=f(x)$ lie on two straight
lines of the form $y=mx$, where $m\in\mathbb R$. Find the values of $m$. *[2]*
""")

code(r"""
q4_2a = ...      # Eq(y**2, ...)
q4_2b = [...]    # both values of m

verify_family('4.2(a)', q4_2a, (y**2 - 2*x**2)/(x*y), ic=(1, 2), span=(0, 3))
verify_directions('4.2(b)', q4_2b, (y**2 - 2*x**2)/(x*y), slope=m)
""")

md(r"""
### 4.3 — *May 2023 TZ2 Paper 2 Q12(b)(c)(f), 15 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{x^2+3y^2}{xy}$, where
$x>0$, $y>0$. It is given that $y=2$ when $x=1$.

**(b)** By solving the differential equation, show that
$y=x\sqrt{\dfrac{9x^4-1}2}$. *[8]*

**(c)** Find the value of $y$ when $x=1.1$. *[1]*

**(f)** The graph of $y=x\sqrt{\dfrac{9x^4-1}2}$ for
$\dfrac{\sqrt3}3<x<1$ has a point of inflexion at the point $P$. It can be
shown that $\dfrac{d^2y}{dx^2}=\dfrac{-x^4+x^2y^2+6y^4}{x^2y^3}$ for $x>0$,
$y>0$. Use this expression to show that $P$ lies on the straight line $y=mx$,
where the exact value of $m$ is to be determined. *[6]*
""")

code(r"""
q4_3a = ...      # y in terms of x
q4_3b = ...      # y(1.1)
q4_3c = ...      # m, exactly

verify_ode('4.3(b)', q4_3a, (x**2 + 3*y**2)/(x*y), ic=(1, 2))
verify_solved('4.3(c)', q4_3b, (x**2 + 3*y**2)/(x*y), (1, 2), 1.1, euler=0.1)
verify_inflexion('4.3(f)', q4_3c, (x**2 + 3*y**2)/(x*y), (1, 2), (0.58, 1))
""")

md(r"""
### 4.4 — *November 2023 Paper 3 Q2(e), 11 marks*

Consider two families of curves, $F$ and $G$. The gradient of $F$ is denoted by
$f(x,y)$ and the gradient of $G$ by $g(x,y)$; each member of $F$ intersects
every member of $G$ at an acute angle $\alpha$. It can be shown that

$$g(x,y)=\frac{f(x,y)+\tan\alpha}{1-f(x,y)\tan\alpha}.$$

Consider the case where $f(x,y)=-\dfrac xy$, for $x\ne0$, $y\ne0$, and
$\alpha=\dfrac\pi4$.

**(i)** Show that $g(x,y)=\dfrac{y-x}{y+x}$. *[2]*

**(ii)** Hence, by solving the homogeneous differential equation
$\dfrac{dy}{dx}=\dfrac{y-x}{y+x}$, find a general equation that represents this
family of curves, $G$. Give your answer in the form $h(x,y)=d$, where $d$ is a
parameter. *[9]*

*The parameter is `D`; `d` is taken by sympy.*
""")

code(r"""
q4_4a = ...      # g(x, y), tidied up
q4_4b = ...      # Eq(..., D) — the family G

verify_identity('4.4(i)', q4_4a, (-x/y + tan(pi/4))/(1 - (-x/y)*tan(pi/4)))
verify_family('4.4(ii)', q4_4b, (y - x)/(y + x), span=(0, 4))
""")

md(r"""
### 4.5 — *May 2025 TZ1 Paper 1 Q9, 8 marks*

Consider the homogeneous differential equation
$\dfrac{dy}{dx}=\dfrac{x-y}{x+y}$, where $x>0$ and $y\ne-x$. It is given that
$y=0$ when $x=2$.

By using the substitution $y=vx$, show that the solution of the differential
equation is $x^2-2xy-y^2=4$.
""")

code(r"""
q4_5 = ...       # Eq(..., ...) — the solution

verify_family('4.5', q4_5, (x - y)/(x + y), ic=(2, 0))
""")

md(r"""
### 4.6 — *May 2025 TZ2 Paper 3 Q1(f)(g), 9 marks*

Consider the differential equation $x^2\dfrac{dy}{dx}=x(x+y)-y^2$, where
$x\ne0$ and $y\ne\pm x$. Using the substitution $y=vx$, the equation can be
written as $x\dfrac{dv}{dx}=1-v^2$, and it was shown earlier that

$$\int\frac1{1-v^2}\,dv=\ln\sqrt{\frac{A(1+v)}{1-v}},$$

where $A$ is a positive constant.

**(f)** Hence, show that a solution to the original differential equation may be
expressed in the form $x^2=\dfrac{A(x+y)}{x-y}$. *[5]*

**(g)** Show that a solution to the original differential equation is
$y=\dfrac{x(x^2-A)}{x^2+A}$. *[4]*
""")

code(r"""
q4_6a = ...      # Eq(x**2, ...)
q4_6b = ...      # y in terms of x and A

verify_family('4.6(f)', q4_6a, (x*(x + y) - y**2)/x**2)
verify_ode('4.6(g)', q4_6b, (x*(x + y) - y**2)/x**2, letters=1)
""")

md(r"""
### 4.7 — *November 2025 TZ3 Paper 2 Q12(d), 8 marks*

Consider the homogeneous differential equation
$(x^2+xy)\dfrac{dy}{dx}=x^2+xy-3y^2$, where $x>0$ and $y>\dfrac x2$. It is
given that $y=\dfrac32$ when $x=1$, and that
$\dfrac{1+v}{1-4v^2}=\dfrac A{1-2v}+\dfrac B{1+2v}$ for constants $A$ and $B$
found earlier.

By solving the differential equation, show that $x^6(2y-x)^3=2(x+2y)$.
""")

code(r"""
q4_7 = ...       # Eq(..., ...) — the solution

verify_family('4.7', q4_7, (x**2 + x*y - 3*y**2)/(x**2 + x*y), ic=(1, Rational(3, 2)),
              span=(0.5, 2))
""")

# ================================================================ § 5
md(r"""
---
# § 5. The integrating factor

**Eight parts, 37 marks.** The equation is linear in $y$:
$\dfrac{dy}{dx}+P(x)y=Q(x)$. Separating fails because $Q(x)$ keeps $y$ from
gathering on one side; multiplying by $I=e^{\int P\,dx}$ turns the left side
into $(Iy)'$.
""")

md(r"""
### 5.1 — *November 2021 Paper 1 Q8, 7 marks*

Solve the differential equation
$\dfrac{dy}{dx}=\dfrac{\ln 2x}{x^2}-\dfrac{2y}x$, $x>0$, given that $y=4$ at
$x=\dfrac12$. Give your answer in the form $y=f(x)$.
""")

code(r"""
q5_1 = ...       # y in terms of x

verify_ode('5.1', q5_1, log(2*x)/x**2 - 2*y/x, ic=(Rational(1, 2), 4))
""")

md(r"""
### 5.2 — *May 2024 TZ1 Paper 2 Q7, 7 marks*

Solve the differential equation $\dfrac{dy}{dx}-y=x$, given that $y=2$ when
$x=0$. Give your answer in the form $y=f(x)$.
""")

code(r"""
q5_2 = ...       # y in terms of x

verify_ode('5.2', q5_2, x + y, ic=(0, 2))
""")

md(r"""
### 5.3 — *May 2024 TZ2 Paper 2 Q12(c)(d)(e)(i)(f), 12 marks*

Consider the differential equation
$\dfrac{dy}{dx}=y\,\mathrm{cosec}\,2x+\sqrt{\tan x}$, where
$0<x<\dfrac\pi2$ and $y=\dfrac\pi4$ at $x=\dfrac\pi4$. It was shown earlier
that $\dfrac d{dx}\left[\dfrac12\ln(\cot x)\right]=-\mathrm{cosec}\,2x$.

**(c)** Show that $\sqrt{\cot x}$ is an integrating factor for this
differential equation. *[4]*

**(d)** Hence, by solving the differential equation, show that
$y=x\sqrt{\tan x}$. *[5]*

**(e)(i)** Consider the curve $y=x\sqrt{\tan x}$ for $0<x<\dfrac\pi2$. Find the
$y$-coordinate at $x=\dfrac{5\pi}{12}$. Give your answer correct to three
significant figures. *[1]*

**(f)** By considering
$\dfrac{dy}{dx}=y\,\mathrm{cosec}\,2x+\sqrt{\tan x}$, deduce that the curve
$y=x\sqrt{\tan x}$ has a positive gradient for $0<x<\dfrac\pi2$. *[2]*

* `'a'` — $y$ increases because both $x$ and $\sqrt{\tan x}$ increase
* `'b'` — $\dfrac{dy}{dx}=0$ only at $x=0$, so there is no stationary point inside
* `'c'` — on this interval $y>0$, $\mathrm{cosec}\,2x>0$ and $\sqrt{\tan x}>0$,
  so $\dfrac{dy}{dx}$ is a sum of positive terms
* `'d'` — the second derivative is positive there, so the gradient cannot be negative
""")

code(r"""
q5_3a = ...      # the integrating factor
q5_3b = ...      # y in terms of x
q5_3c = ...      # the y-coordinate at x = 5pi/12
q5_3d = ...      # 'a', 'b', 'c' or 'd'

field = y*cosec(2*x) + sqrt(tan(x))

verify_factor('5.3(c)', q5_3a, field)
verify_ode('5.3(d)', q5_3b, field, ic=(pi/4, pi/4))
verify_solved('5.3(e)', q5_3c, field, (pi/4, pi/4), 5*pi/12, euler=pi/12)
check_word('5.3(f)', q5_3d, """ + repr(digest(POSITIVE)) + r""")
""")

md(r"""
### 5.4 — *May 2025 TZ3 Paper 2 Q12(b), 4 marks*

It was found earlier that $\displaystyle\int(x^2-5)e^x\,dx=(x^2-2x-3)e^x+c$.

Consider the differential equation $\dfrac{dy}{dx}=x^2-y-5$. By solving the
differential equation, show that its solution can be expressed in the form
$y=x^2-2x-3+Ce^{-x}$, where $C$ is a constant.
""")

code(r"""
q5_4 = ...       # y in terms of x, with C

verify_ode('5.4', q5_4, x**2 - y - 5, letters=1)
""")

md(r"""
### 5.5 — *November 2025 TZ3 Paper 1 Q6, 7 marks*

In this question you may assume the result
$\displaystyle\int x\,\mathrm{cosec}^2x\,dx=\ln|\sin x|-x\cot x+c$.

Consider the differential equation
$x\dfrac{dy}{dx}+3y=\dfrac{\mathrm{cosec}^2x}x$ for $0<x<\pi$. Given that
$y=\dfrac8{\pi^2}$ when $x=\dfrac\pi2$, find the particular solution for this
differential equation. Express your answer in the form $y=f(x)$.
""")

code(r"""
q5_5 = ...       # y in terms of x

verify_ode('5.5', q5_5, (cosec(x)**2/x - 3*y)/x, ic=(pi/2, 8/pi**2))
""")

# ================================================================ § 6
md(r"""
---
# § 6. Euler's method

**Eleven parts, 29 marks.** A step length is given and an approximate value is
asked for; the closed form may not exist at all. Every one of these is a
Paper 2 question — the iteration goes into the calculator as a table or a
recursive sequence, and the intermediate values are not rounded.
""")

md(r"""
### 6.1 — *May 2022 TZ1 Paper 2 Q12(a), 4 marks*

Consider the differential equation $x^2\dfrac{dy}{dx}=y^2-2x^2$ for $x>0$ and
$y>2x$. It is given that $y=3$ when $x=1$.

Use Euler's method, with a step length of $0.1$, to find an approximate value of
$y$ when $x=1.5$.
""")

code(r"""
q6_1 = ...       # the approximation at x = 1.5

verify_euler('6.1', q6_1, (y**2 - 2*x**2)/x**2, (1, 3), 0.1, 1.5)
""")

md(r"""
### 6.2 — *May 2023 TZ1 Paper 2 Q12(a), 4 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{x^2y-y}{x^2+1}$,
where $y>0$ and $y=3$ when $x=0$.

Use Euler's method, with a step length of $0.03$, to find an approximate value
for $y$ when $x=0.15$. Give your answer correct to six significant figures.
""")

code(r"""
q6_2 = ...       # the approximation at x = 0.15, to 6 s.f.

verify_euler('6.2', q6_2, (x**2*y - y)/(x**2 + 1), (0, 3), 0.03, 0.15, digits=6)
""")

md(r"""
### 6.3 — *May 2023 TZ2 Paper 2 Q12(a), 2 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{x^2+3y^2}{xy}$, where
$x>0$, $y>0$ and $y=2$ when $x=1$.

Use Euler's method with step length $0.1$ to find an approximate value of $y$
when $x=1.1$.
""")

code(r"""
q6_3 = ...       # the approximation at x = 1.1

verify_euler('6.3', q6_3, (x**2 + 3*y**2)/(x*y), (1, 2), 0.1, 1.1)
""")

md(r"""
### 6.4 — *November 2023 Paper 2 Q9(a)(c), 4 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{4-y}{10}$, where
$y=2$ when $x=0$.

**(a)** Use Euler's method with a step size of $0.1$ to find an approximation
for $y$ when $x=0.5$. Give your answer correct to four significant figures.
*[3]*

**(c)** Find the absolute value of the error in your approximation in part (a).
*[1]*

*The exact solution, $y=4-2e^{-\frac x{10}}$, is § 2.2.*
""")

code(r"""
q6_4a = ...      # the approximation at x = 0.5, to 4 s.f.
q6_4b = ...      # |approximation - exact|

verify_euler('6.4(a)', q6_4a, (4 - y)/10, (0, 2), 0.1, 0.5, digits=4)
verify_euler('6.4(c)', q6_4b, (4 - y)/10, (0, 2), 0.1, 0.5, report='error')
""")

md(r"""
### 6.5 — *May 2024 TZ2 Paper 2 Q12(a), 3 marks*

Consider the differential equation
$\dfrac{dy}{dx}=y\,\mathrm{cosec}\,2x+\sqrt{\tan x}$, where $0<x<\dfrac\pi2$
and $y=\dfrac\pi4$ at $x=\dfrac\pi4$.

Use Euler's method with step length $\dfrac\pi{12}$ to find an approximate
value of $y$ when $x=\dfrac{5\pi}{12}$. Give your answer correct to three
significant figures.
""")

code(r"""
q6_5 = ...       # the approximation at x = 5pi/12

verify_euler('6.5', q6_5, y*cosec(2*x) + sqrt(tan(x)), (pi/4, pi/4), pi/12, 5*pi/12)
""")

md(r"""
### 6.6 — *May 2025 TZ1 Paper 2 Q9(a), 3 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{2x}{x^2+y}$. The
solution curve passes through the point $(1,0)$.

Use Euler's method with a step value of $0.25$ to estimate the value of $y$
when $x=2$.
""")

code(r"""
q6_6 = ...       # the estimate at x = 2

verify_euler('6.6', q6_6, 2*x/(x**2 + y), (1, 0), 0.25, 2)
""")

md(r"""
### 6.7 — *November 2025 TZ1 Paper 3 Q2(d), 5 marks*

About 3 % of the wolf population of § 2.5 emigrates from the protected area
each year, and the adapted model satisfies

$$\frac{dx}{dt}=0.0855\,x\ln\left(\frac{200}x\right)-0.03\,x.$$

**(i)** Use Euler's method, with a step size of $0.5$ years and an initial
value of $x_0=70$ when $t=5$, to find an estimate for the size of the wolf
population when $t=10$. Give your answer correct to the nearest whole number.
*[4]*

**(ii)** Comment on your answer. After 10 years the wolf population was
measured and found to be 85; the logistic model of part (a) predicted 106 and
the Gompertz model of § 2.5 predicted 101. *[1]*

* `'a'` — the two earlier models now agree, so the emigration term was unnecessary
* `'b'` — 89 is the closest of the three to the measured 85, so the adapted
  model is the most realistic
* `'c'` — the estimate is above 85, so this model underestimates the population
* `'d'` — Euler's method is exact here, so 89 is the true size
""")

code(r"""
q6_7a = ...      # the estimate at t = 10, to the nearest whole number
q6_7b = ...      # 'a', 'b', 'c' or 'd'

verify_euler('6.7(i)', q6_7a, 0.0855*w*log(200/w) - 0.03*w, (5, 70), 0.5, 10,
             var=t, dep=w, whole=True)
check_word('6.7(ii)', q6_7b, """ + repr(digest(MORE_REAL)) + r""")
""")

md(r"""
### 6.8 — *November 2025 TZ3 Paper 2 Q12(a)(i)(ii), 4 marks*

Consider the homogeneous differential equation
$(x^2+xy)\dfrac{dy}{dx}=x^2+xy-3y^2$, where $x>0$ and $y>\dfrac x2$. It is
given that $y=\dfrac32$ when $x=1$.

**(i)** Find the value of $\dfrac{dy}{dx}$ when $x=1$. *[1]*

**(ii)** Use Euler's method with two equal steps to estimate the value of $y$
when $x=1.4$. *[3]*
""")

code(r"""
q6_8a = ...      # dy/dx at x = 1
q6_8b = ...      # the estimate at x = 1.4

field = (x**2 + x*y - 3*y**2)/(x**2 + x*y)

verify_field('6.8(i)', q6_8a, field, (1, Rational(3, 2)))
verify_euler('6.8(ii)', q6_8b, field, (1, Rational(3, 2)), 0.2, 1.4)
""")

# ================================================================ § 7
md(r"""
---
# § 7. Which side the tangents lie

**Seven parts, 11 marks.** Euler's method walks along tangents, so the sign of
its error is the concavity of the solution: a curve that bends upwards lies
above its tangents, and the broken line falls short. The mark is for naming the
reason — the second derivative or the concavity — not for the word
*underestimate*.
""")

md(r"""
### 7.1 — *May 2023 TZ1 Paper 2 Q12(e), 2 marks*

For the equation of § 6.2, $\dfrac{dy}{dx}=\dfrac{x^2y-y}{x^2+1}$ with $y=3$ at
$x=0$: for $0\le x<1$, explain why the approximate value for $y$ obtained using
Euler's method will always be less than the actual value for $y$.

*Answer with the concavity of the solution curve there — `'up'` or `'down'`.
The tangents do the rest.*
""")

code(r"""
q7_1 = ...       # 'up' or 'down'

verify_curvature('7.1', q7_1, (x**2*y - y)/(x**2 + 1), (0, 3), (0, 0.99))
""")

md(r"""
### 7.2 — *May 2023 TZ2 Paper 2 Q12(d), 2 marks*

With reference to the concavity of the graph of $y=x\sqrt{\dfrac{9x^4-1}2}$ for
$1\le x\le1.1$, explain why the value of $y$ found in § 4.3(c) is greater than
the approximate value of $y$ found in § 6.3.

*Answer with the concavity.*
""")

code(r"""
q7_2 = ...       # 'up' or 'down'

verify_curvature('7.2', q7_2, (x**2 + 3*y**2)/(x*y), (1, 2), (1, 1.1))
""")

md(r"""
### 7.3 — *May 2024 TZ2 Paper 2 Q12(e)(ii)(iii), 2 marks*

Consider the curve $y=x\sqrt{\tan x}$ of § 5.3 and the Euler approximation of
§ 6.5.

**(ii)** By considering the gradient of the curve, suggest a reason why Euler's
method does not give a good approximation for the $y$-coordinate at
$x=\dfrac{5\pi}{12}$. *[1]*

* `'a'` — the gradient changes substantially over the interval, and two steps
  cannot follow it
* `'b'` — the step length $\dfrac\pi{12}$ is not a whole number of degrees
* `'c'` — the starting point $x=\dfrac\pi4$ is a stationary point
* `'d'` — $\mathrm{cosec}\,2x$ is undefined at $x=\dfrac\pi2$, which is inside
  the interval

**(iii)** State why this approximation is less than the $y$-coordinate at
$x=\dfrac{5\pi}{12}$. *[1]*

*Answer with the concavity.*
""")

code(r"""
q7_3a = ...      # 'a', 'b', 'c' or 'd'
q7_3b = ...      # 'up' or 'down'

check_word('7.3(ii)', q7_3a, """ + repr(digest(STEEP)) + r""")
verify_curvature('7.3(iii)', q7_3b, y*cosec(2*x) + sqrt(tan(x)), (pi/4, pi/4),
                 (pi/4, 5*pi/12))
""")

md(r"""
### 7.4 — *May 2025 TZ1 Paper 2 Q9(b), 3 marks*

Consider the differential equation $\dfrac{dy}{dx}=\dfrac{2x}{x^2+y}$ with the
solution curve through $(1,0)$, and the estimate of § 6.6. Part of the solution
curve lies below the $x$-axis: at $x=2$ the curve has a negative branch as well
as a positive one.

**(i)** Determine whether your answer to § 6.6 is an overestimate or an
underestimate. *[2]*

**(ii)** Justify why the use of Euler's method starting at $(1,0)$ does not lead
to an estimate of the negative value of $y$ when $x=2$. *[1]*

* `'a'` — the method rounds up at every step, so it can never return a negative
  value
* `'b'` — the gradient at $(1,0)$ is positive, so the broken line sets off along
  the upper part of the curve
* `'c'` — the equation has no solution with $y<0$
* `'d'` — a step of $0.25$ is too long to cross the $x$-axis
""")

code(r"""
q7_4a = ...      # 'over' or 'under'
q7_4b = ...      # 'a', 'b', 'c' or 'd'

verify_euler('7.4(i)', q7_4a, 2*x/(x**2 + y), (1, 0), 0.25, 2, report='sense')
check_word('7.4(ii)', q7_4b, """ + repr(digest(UPPER)) + r""")
""")

md(r"""
### 7.5 — *November 2025 TZ3 Paper 2 Q12(a)(iii), 2 marks*

Hence, state the concavity of the solution curve of § 6.8 for
$1\le x\le1.4$. You may assume that the concavity does not change in this
interval. Give a reason for your answer.
""")

code(r"""
q7_5 = ...       # 'up' or 'down'

verify_curvature('7.5', q7_5, (x**2 + x*y - 3*y**2)/(x**2 + x*y),
                 (1, Rational(3, 2)), (1, 1.4))
""")

# ================================================================ § 8
md(r"""
---
# § 8. Two equations at once

**Nine parts, 30 marks — one question.** November 2021, Paper 3: a system of
two linear differential equations. None of the seven techniques solves it.
Instead the system collapses into a single second-order equation, and that one
is solved by trying $y=Fe^{\lambda t}$. The syllabus keeps it in this subtopic,
so the archive keeps it too — as its own section rather than an eighth rung.

Throughout, $\dfrac{dx}{dt}=x-y$ and $\dfrac{dy}{dt}=ax+y$, where
$x,y,t\in\mathbb R^+$ and $a$ is a parameter.
""")

md(r"""
### 8.1 — *November 2021 Paper 3 Q2, 30 marks*

**First consider the case where $a=0$.**

**(a)(i)** By solving the differential equation $\dfrac{dy}{dt}=y$, show that
$y=Ae^t$, where $A$ is a constant. *[3]*

**(a)(ii)** Show that $\dfrac{dx}{dt}-x=-Ae^t$. *[1 — one line of
substitution; the work is in (iii)]*

**(a)(iii)** Solve the differential equation in part (a)(ii) to find $x$ as a
function of $t$. *[4]*
""")

code(r"""
q8_1 = ...       # y as a function of t
q8_2 = ...       # x as a function of t, with A and D

verify_ode('8.1(a)(i)', q8_1, y, var=t, dep=y, letters=1)
verify_ode('8.1(a)(iii)', q8_2, x - A*exp(t), var=t, dep=x, letters=2)
""")

md(r"""
**Now consider the case where $a=-1$**, so that $\dfrac{dx}{dt}=x-y$ and
$\dfrac{dy}{dt}=-x+y$.

**(b)(i)** By differentiating $\dfrac{dy}{dt}=-x+y$ with respect to $t$, show
that $\dfrac{d^2y}{dt^2}=2\dfrac{dy}{dt}$. *[3]*

*Answer with the pair $(p,q)$ in
$\dfrac{d^2y}{dt^2}=p\dfrac{dy}{dt}+qy$.*

**(b)(ii)** By substituting $Y=\dfrac{dy}{dt}$, show that $Y=Be^{2t}$, where
$B$ is a constant. *[3]*

**(b)(iii)** Hence find $y$ as a function of $t$. *[2]*

**(b)(iv)** Hence show that $x=-\dfrac B2e^{2t}+C$, where $C$ is a constant.
*[3]*
""")

code(r"""
q8_3 = ...       # (p, q)
q8_4 = ...       # Y as a function of t
q8_5 = ...       # y as a function of t, with B and C
q8_6 = ...       # x as a function of t, with B and C

verify_eliminated('8.1(b)(i)', q8_3, {x: x - y, y: -x + y}, y)
verify_ode('8.1(b)(ii)', q8_4, 2*Y, var=t, dep=Y, letters=1)
verify_ode('8.1(b)(iii)', q8_5, B*exp(2*t), var=t, dep=y, letters=2)
verify_system('8.1(b)(iv)', (q8_6, q8_5), {x: x - y, y: -x + y})
""")

md(r"""
**Now consider the case where $a=-4$**, so that $\dfrac{dx}{dt}=x-y$ and
$\dfrac{dy}{dt}=-4x+y$.

**(c)(i)** Show that $\dfrac{d^2y}{dt^2}-2\dfrac{dy}{dt}-3y=0$. *[3]*

*Answer with the pair $(p,q)$ in
$\dfrac{d^2y}{dt^2}=p\dfrac{dy}{dt}+qy$.*

From the previous cases, we might conjecture that a solution to this
differential equation is $y=Fe^{\lambda t}$, $\lambda\in\mathbb R$ and $F$ a
constant.

**(c)(ii)** Find the two values for $\lambda$ that satisfy
$\dfrac{d^2y}{dt^2}-2\dfrac{dy}{dt}-3y=0$. *[4]*

**(c)(iii)** Let the two values found in part (c)(ii) be $\lambda_1$ and
$\lambda_2$. Verify that $y=Fe^{\lambda_1t}+Ge^{\lambda_2t}$ is a solution to
the differential equation in (c)(i), where $G$ is a constant. *[4]*
""")

code(r"""
q8_7 = ...       # (p, q)
q8_8 = [...]     # both values of lambda
q8_9 = ...       # the general solution, with F and G

verify_eliminated('8.1(c)(i)', q8_7, {x: x - y, y: -4*x + y}, y)
verify_second_order('8.1(c)(ii)', q8_8, (1, -2, -3))
verify_second_order('8.1(c)(iii)', q8_9, (1, -2, -3), letters=2)
""")

# ================================================================ решения
md(r"""
---
# Solutions

Open these only after you have been stuck twice. Every answer below is the
markscheme's, written out; the checks above accept any equivalent form, so a
different-looking solution of yours may still be right.

---

## § 1

**1.1** $\int\cos\left(x-\frac\pi4\right)dx=\sin\left(x-\frac\pi4\right)+c$; at
$x=\frac{3\pi}4$, $2=\sin\frac\pi2+c$, so $c=1$ and
$\boxed{y=\sin\left(x-\frac\pi4\right)+1}$.

**1.2** $\int_0^4-104000e^{-0.0145t}dt=-404165.8\ldots$ ($t=4$ at the start of
2026), and $6.78\times10^6-404165.8\ldots=6375834.1\ldots\approx
\boxed{6.38\times10^6}$.

---

## § 2

**2.1** $\int\frac{dv}{1+v}=-\int dt$ gives $\ln(1+v)=-t+c$; $v(0)=v_0$ gives
$c=\ln(1+v_0)$, so $1+v=(1+v_0)e^{-t}$ and
$\boxed{v=(1+v_0)e^{-t}-1}$.

**2.2** $\int\frac{dy}{4-y}=\int\frac{dx}{10}$ gives
$-\ln|4-y|=\frac x{10}+c$; $(0,2)$ gives $c=-\ln2$, so $4-y=2e^{-x/10}$ and
$\boxed{y=4-2e^{-x/10}}$.

**2.3** $y\,dy=-x\,dx$ gives $\frac{y^2}2=-\frac{x^2}2+c$, that is
$\boxed{x^2+y^2=k}$.

**2.4** $\int y^{-2}dy=\int\cos^2x\,dx=\int\frac{1+\cos2x}2dx$ gives
$-\frac1y=\frac{2x+\sin2x}4+c$, so $y=\frac{-4}{2x+\sin2x+C}$ and
$\boxed{a=-4}$. At $x=\frac\pi2$: $1=\frac{-4}{\pi+0+b}$, so
$\boxed{b=-4-\pi}$.

**2.5** **(i)** $\ln\frac{200}{200}=0$, so $\boxed{\frac{dx}{dt}=0}$.
**(ii)** $\boxed{\text{b}}$ — the population is steady at 200.
**(iii)** $\int\frac{-dx}{x\ln(200/x)}=\int-a\,dt$ with the given derivative
gives $\ln(\ln200-\ln x)=-at+c$, so $\ln200-\ln x=Ae^{-at}$ and
$\boxed{x=200e^{-Ae^{-at}}}$. **(iv)** $200e^{-A}=40$, so
$\boxed{A=\ln5}$. **(v)** $\ln70=\ln200-\ln5\cdot e^{-5a}$ gives
$a=0.0854528\ldots\approx\boxed{0.0855}$. **(vi)**
$\ln x=\ln200-\ln5\cdot e^{-0.854528\ldots}$ gives $x=100.839\ldots\approx
\boxed{101}$ wolves.

---

## § 3

**3.1** **(c)** $5k\int\frac{dP}{P(k-P)}=\int dt$ with
$\frac k{P(k-P)}=\frac1P+\frac1{k-P}$ gives
$5\big(\ln P-\ln(k-P)\big)=t+c$; $(0,1200)$ gives
$c=5\ln\frac{1200}{k-1200}$, and rearranging isolates
$\boxed{P=\frac{1200k}{(k-1200)e^{-t/5}+1200}}$. **(d)**
$2400=\frac{1200k}{(k-1200)e^{-2}+1200}$ gives $k=2845.34\ldots\approx
\boxed{2845}$.

**3.2** **(e)** $\int\frac{N\,dP}{P(N-P)}=\int k\,dt$ with
$\frac N{P(N-P)}=\frac1P+\frac1{N-P}$ gives $\ln P-\ln(N-P)=kt+C$; at $t=0$,
$P=P_0$, so $C=\ln P_0-\ln(N-P_0)$ and
$\boxed{kt=\ln\left[\frac P{N-P}\cdot\frac{N-P_0}{P_0}\right]}$. **(f)**
$10k=\ln\left(\frac{3P_0}{P_0}\cdot\frac{3P_0}{P_0}\right)=\ln9$, so
$\boxed{k=\frac15\ln3}\approx0.220$.

**3.3** **(i)** $\frac{dv}{(v-2)(v+1)}=\frac{dx}x$ with
$\frac1{(v-2)(v+1)}=\frac13\left(\frac1{v-2}-\frac1{v+1}\right)$ gives
$\frac13\ln\left|\frac{v-2}{v+1}\right|=\ln|x|+c$; $v=3$ at $x=1$ gives
$\frac{v-2}{v+1}=\frac{x^3}4$, and $v=\frac yx$ turns that into
$\boxed{y=\frac{8x+x^4}{4-x^3}}$. **(ii)**
$\frac{12+5.0625}{0.625}=\boxed{27.3}$. **(iii)** $\boxed{\text{a}}$ — the
asymptote stands at $x=\sqrt[3]4=1.5874\ldots$, just past the interval.

**3.4** **(i)** $\int\frac{dy}y=\int\left(1-\frac2{x^2+1}\right)dx$ gives
$\ln y=x-2\arctan x+c$; $y(0)=3$ gives $c=\ln3$, so
$\boxed{y=3e^{x-2\arctan x}}$. **(ii)** $y(0.15)=2.58786288\ldots\approx
\boxed{2.58786}$.

---

## § 4

**4.1** $y=vx$ gives $\frac{dy}{dx}=v+x\frac{dv}{dx}$, and
$v+x\frac{dv}{dx}=v^2-2$, so $x\frac{dv}{dx}=\boxed{v^2-v-2}$.

**4.2** **(a)** $v+x\frac{dv}{dx}=\frac{v^2-2}v$ gives
$x\frac{dv}{dx}=-\frac2v$; $\int v\,dv=-2\int\frac{dx}x$ gives
$\frac{v^2}2=-2\ln|x|+c$, and $(1,2)$ gives $c=2$:
$\boxed{y^2=4x^2(1-\ln x)}$. **(b)** $\frac{dy}{dx}=0$ needs $y^2=2x^2$, so
$y=\pm\sqrt2\,x$ and $\boxed{m=\pm\sqrt2}$.

**4.3** **(b)** $v+x\frac{dv}{dx}=\frac{1+3v^2}v$ gives
$x\frac{dv}{dx}=\frac{1+2v^2}v$; $\int\frac{v\,dv}{1+2v^2}=\int\frac{dx}x$
gives $\frac14\ln(1+2v^2)=\ln x+C$, and $(1,2)$ gives $C=\frac14\ln9$, so
$1+\frac{2y^2}{x^2}=9x^4$ and $\boxed{y=x\sqrt{\frac{9x^4-1}2}}$. **(c)**
$y(1.1)=2.71422\ldots\approx\boxed{2.71}$. **(f)**
$\frac{d^2y}{dx^2}=0$ needs $-x^4+x^2y^2+6y^4=0$; dividing by $y^4$ and
putting $m=\frac yx$ gives $6m^4+m^2-1=0$, that is $(3m^2-1)(2m^2+1)=0$, so
$\boxed{m=\frac1{\sqrt3}}$ ($x>0$, $y>0$).

**4.4** **(i)**
$\frac{-\frac xy+1}{1+\frac xy}=\boxed{\frac{y-x}{y+x}}$. **(ii)** $y=vx$
gives $x\frac{dv}{dx}=\frac{v-1}{v+1}-v=-\frac{1+v^2}{1+v}$;
$\int\frac{1+v}{1+v^2}dv=-\int\frac{dx}x$ gives
$\frac12\ln(1+v^2)+\arctan v=-\ln|x|+d$, so
$\boxed{\frac12\ln\left(1+\frac{y^2}{x^2}\right)+\arctan\frac yx+\ln|x|=d}$.

**4.5** $y=vx$ gives $x\frac{dv}{dx}=\frac{1-v}{1+v}-v=\frac{1-2v-v^2}{1+v}$;
$\int\frac{(1+v)dv}{1-2v-v^2}=\int\frac{dx}x$ gives
$-\frac12\ln|1-2v-v^2|=\ln|x|+c$, and $x=2$, $v=0$ gives $c=-\ln2$:
$x^2\left(1-\frac{2y}x-\frac{y^2}{x^2}\right)=4$, that is
$\boxed{x^2-2xy-y^2=4}$.

**4.6** **(f)** $\int\frac{dv}{1-v^2}=\int\frac{dx}x$ gives
$\ln\sqrt{\frac{A(1+v)}{1-v}}=\ln x$, so $x^2=\frac{A(1+v)}{1-v}$ and with
$v=\frac yx$, $\boxed{x^2=\frac{A(x+y)}{x-y}}$. **(g)** $x^2(x-y)=A(x+y)$
gives $x^3-Ax=y(x^2+A)$, so $\boxed{y=\frac{x(x^2-A)}{x^2+A}}$.

**4.7** $y=vx$ gives $(1+v)x\frac{dv}{dx}=1-4v^2$, and
$\frac{1+v}{1-4v^2}=\frac{3/4}{1-2v}+\frac{1/4}{1+2v}$, so
$\ln x=-\frac38\ln|1-2v|+\frac18\ln|1+2v|+c$; $x=1$, $v=\frac32$ gives
$c=\frac18\ln2$. Then $8\ln x+3\ln(2v-1)=\ln(1+2v)+\ln2$, that is
$\boxed{x^6(2y-x)^3=2(x+2y)}$.

---

## § 5

**5.1** $\frac{dy}{dx}+\frac2xy=\frac{\ln2x}{x^2}$ and $I=x^2$, so
$(x^2y)'=\ln2x$ and $x^2y=x\ln2x-x+c$ by parts. At $x=\frac12$, $y=4$:
$4=0-2+4c$, so $c=\frac32$ and
$\boxed{y=\frac{\ln2x}x-\frac1x+\frac3{2x^2}}$.

**5.2** $I=e^{-x}$, so $(ye^{-x})'=xe^{-x}$ and
$ye^{-x}=-xe^{-x}-e^{-x}+c$ by parts, that is $y=-x-1+ce^x$; $y(0)=2$ gives
$c=3$ and $\boxed{y=3e^x-x-1}$.

**5.3** **(c)** $I=e^{\int-\mathrm{cosec}\,2x\,dx}=e^{\frac12\ln(\cot x)}
=\boxed{\sqrt{\cot x}}$. **(d)**
$\left(y\sqrt{\cot x}\right)'=\sqrt{\tan x}\sqrt{\cot x}=1$, so
$y\sqrt{\cot x}=x+C$; at $x=\frac\pi4$ both sides are $\frac\pi4$, so $C=0$
and $\boxed{y=x\sqrt{\tan x}}$. **(e)(i)**
$\frac{5\pi}{12}\sqrt{\tan\frac{5\pi}{12}}=2.52878\ldots\approx\boxed{2.53}$.
**(f)** $\boxed{\text{c}}$ — $y>0$, $\mathrm{cosec}\,2x>0$ and
$\sqrt{\tan x}>0$ on the interval.

**5.4** $I=e^x$, so $(ye^x)'=(x^2-5)e^x$ and
$ye^x=(x^2-2x-3)e^x+C$ by the given integral:
$\boxed{y=x^2-2x-3+Ce^{-x}}$.

**5.5** $\frac{dy}{dx}+\frac3xy=\frac{\mathrm{cosec}^2x}{x^2}$ and $I=x^3$, so
$(x^3y)'=x\,\mathrm{cosec}^2x$ and $x^3y=\ln|\sin x|-x\cot x+c$ by the given
integral. At $x=\frac\pi2$, $y=\frac8{\pi^2}$: $\pi=0-0+c$, so $c=\pi$ and
$\boxed{y=\frac{\pi-x\cot x+\ln|\sin x|}{x^3}}$.

---

## § 6

**6.1** $3\to3.7\to4.63140\to5.92098\to7.79542\to10.6958\ldots\approx
\boxed{10.7}$.

**6.2** $3\to2.91\to2.82285\to2.73877\to2.65793\to2.58046\ldots$, so
$\boxed{2.58046}$ to six significant figures.

**6.3** $2+0.1\cdot\frac{1^2+3\cdot2^2}{1\cdot2}=\boxed{2.65}$.

**6.4** **(a)** $2\to2.02\to2.0398\to2.05940\to2.07880\to2.09801\ldots\approx
\boxed{2.098}$. **(c)**
$\left|2.0980199\ldots-\left(4-2e^{-0.05}\right)\right|=0.000478749\ldots
\approx\boxed{0.000479}$.

**6.5** $\frac\pi4\to1.25281\to1.97608\ldots\approx\boxed{1.98}$.

**6.6** $0\to0.5\to0.803030\to1.04868\to1.26152\ldots\approx\boxed{1.26}$.

**6.7** **(i)** Ten steps of $0.5$ from 70 reach $89.42803\ldots\approx
\boxed{89}$ wolves. **(ii)** $\boxed{\text{b}}$ — 89 is the closest of the
three predictions to the measured 85.

**6.8** **(i)** $\frac{1+1.5-3(1.5)^2}{1+1.5}=\frac{-4.25}{2.5}=\boxed{-1.7}$.
**(ii)** $1.5\to1.16\to1.07491\ldots\approx\boxed{1.07}$.

---

## § 7

**7.1** $\boxed{\text{up}}$ — $\frac{d^2y}{dx^2}>0$ there, so the tangents
Euler walks along lie below the curve and the approximation falls short.

**7.2** $\boxed{\text{up}}$ — same reason, which is why $2.71$ beats $2.65$.

**7.3** **(ii)** $\boxed{\text{a}}$ — the gradient changes substantially over
$\left[\frac\pi4,\frac{5\pi}{12}\right]$. **(iii)** $\boxed{\text{up}}$.

**7.4** **(i)** $\boxed{\text{over}}$ — the curve is concave down here, and the
solution arrives at $1.118$ while the broken line reaches $1.262$.
**(ii)** $\boxed{\text{b}}$ — the gradient at $(1,0)$ is positive, so the line
sets off upwards.

**7.5** $\boxed{\text{up}}$ — the gradient rises from $-1.7$ at $x=1$ to
$-0.425\ldots$ at $x=1.2$, so the $y$-values fall by less and less.

---

## § 8

**8.1** **(a)(i)** $\int\frac{dy}y=\int dt$ gives $\ln y=t+c$, so
$\boxed{y=Ae^t}$. **(a)(iii)** $I=e^{-t}$ gives $(xe^{-t})'=-A$, so
$xe^{-t}=-At+D$ and $\boxed{x=(-At+D)e^t}$.

**(b)(i)** $\frac{d^2y}{dt^2}=-\frac{dx}{dt}+\frac{dy}{dt}
=-(x-y)+(-x+y)=2(y-x)=2\frac{dy}{dt}$, so
$\boxed{(p,q)=(2,0)}$. **(b)(ii)** $\frac{dY}{dt}=2Y$ gives
$\boxed{Y=Be^{2t}}$. **(b)(iii)** integrating,
$\boxed{y=\frac B2e^{2t}+C}$. **(b)(iv)** $\frac{dy}{dt}=-x+y$ gives
$Be^{2t}=-x+\frac B2e^{2t}+C$, so $\boxed{x=-\frac B2e^{2t}+C}$.

**(c)(i)** $\frac{d^2y}{dt^2}=-4\frac{dx}{dt}+\frac{dy}{dt}=-4(x-y)+(-4x+y)
=-8x+5y=2(-4x+y)+3y$, so $\boxed{(p,q)=(2,3)}$ and
$\frac{d^2y}{dt^2}-2\frac{dy}{dt}-3y=0$. **(c)(ii)** $y=Fe^{\lambda t}$ gives
$\lambda^2-2\lambda-3=0$, so $\boxed{\lambda=3,\,-1}$. **(c)(iii)** with
$y=Fe^{3t}+Ge^{-t}$,
$\left(9Fe^{3t}+Ge^{-t}\right)-2\left(3Fe^{3t}-Ge^{-t}\right)
-3\left(Fe^{3t}+Ge^{-t}\right)=0$, so
$\boxed{y=Fe^{3t}+Ge^{-t}}$ is a solution.
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
