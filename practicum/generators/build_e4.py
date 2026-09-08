"""Собирает практикум E4: неявное дифференцирование, касательная и нормаль.

Одиннадцатый практикум серии и вторая треть темы calculus.differentiation.
Лестница из восьми приёмов делится по тому, чем в вопросе служит прямая:
1–3 — она ответ, 4–6 — кривая перестала быть функцией, 7–8 — прямая стала
условием, из которого достают постоянную.

Проверок здесь восемь новых, и все они устроены вокруг одного понятия.

Семнадцатое понятие равенства ответов: касательная держится кривой.
Кривая задаётся условием на пару чисел F(x, y) = 0, и «y = f(x)» — частный
случай этого, а не другой случай. Проверка не решает условие относительно y
и не дифференцирует его: она идёт по кривой. Слева и справа от точки
берётся x на шаг в сторону, для каждого решается F(x, ·) = 0 у самой точки,
и наклон получается секущей через две найденные точки. Ни dy/dx = −F_x/F_y,
ни правил дифференцирования внутри проверки не написано ни разу.

Отсюда всё остальное. `verify_tangent` — прямая проходит через точку кривой
и идёт с тем же наклоном. `verify_normal` — то же, но произведение наклонов
равно −1. `verify_slope` — ответ через x и y сверяется в нескольких точках
самой кривой, потому что «в терминах x и y» именно это и значит.
`verify_where` — обратный ход: точка ищется просмотром кривой, и полнота
набора берётся оттуда же. `verify_second` — три шага по кривой вместо
второго дифференцирования. `verify_right_angle` — два наклона в общей
точке. `verify_constant` — буква сидит внутри кривой, поэтому кривая
строится из ответа.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e4.py прогоняет по нему весь ноутбук и требует,
чтобы каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e4-tangents.ipynb')

TRIGGER = {1: 'implicit', 2: 'condition', 3: 'point', 4: 'normal',
           5: 'tangent', 6: 'second', 7: 'right', 8: 'itangent',
           9: 'point', 10: 'condition', 11: 'tangent', 12: 'implicit'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '6',
    'q1b': '23',
    'q1c': '30*x - 97',
    'q2': 'b**2*(x - r)',
    'q2r': 'r',
    'q3': '1 - x/2',
    'q4': 't**2',
    'q5': '8',
    'q6': '(2*log(45), 2)',
    'q7': '[2.73, 15.0]',
    'q8': '4*(3 - x)/(y + 2)',
    'q9a': '(1 - y*(1 + log(x*y)))/(1 + x*(1 + log(x*y)))',
    'q9b': '1',
    'q10a': '(2*x - exp(x + y))/(exp(x + y) - 2*y)',
    'q10b': '[(0.331, -0.743), (1.84, -0.538)]',
    'q10d': '(-0.451, -0.451)',
    'q11a': 'Rational(-17, 10)',
    'q11b': 'Rational(1008, 125)',
    'q12f': '-sin(k)',
    'q12g': 'sec(k)**2',
    'q13a': 'y/x',
    'q13f': '-a/sqrt(a*b)',
    'q13g': 'b/sqrt(a*b)',
    'q14h': '(E + 6)/2',
    'q14k': 'E + E**2/4',
    'q15x': 'E',
    'q15y': 'E',
    'q15a': 'E**(1/E)',
    'qt_a': 'exp(2*x)*(6*x - 5)',
    'qt_b': '(0.863, -7.93)',
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
# Practicum E4: implicit differentiation, tangents and normals

**131 marks, 33 blocks, eight techniques.** Everything in this topic is one
idea used from both ends: the gradient of a curve at a point is the gradient
of the straight line that touches it there. Sometimes the line is what you
hand in. Sometimes the line is given and the point is what you hand in.
Sometimes neither is the answer and the touching itself is the equation.

**Material.** The part of `calculus.differentiation` in the AA HL archive
where the derivative works as a *gradient*, sessions May 2021 — November 2025.
The whole topic is 350 marks — twice what a practicum may hold — so it is cut
in three by what the question asks for: *find $f'(x)$* is E3, *find the
tangent* is here, *find the acceleration* is E9.

**This practicum is in English,** like B2 to B5 and E1 to E3. The checks speak
whichever language the notebook asks them to, and this one asks for English
in the setup cell.

**The one thing to carry out of here.**

> A curve is a **condition on a pair of numbers**, not a formula for $y$.
> $y=f(x)$ is one shape that condition can take, and it is not the interesting
> one. Everything you know about tangents — the gradient, the normal, the
> point where the gradient is $-1$ — survives when $y$ cannot be got out of
> the equation, and it survives without any change of method.

And the thing that follows from it: **the hard half of this topic is never
the differentiation.** It is knowing which of the two coordinates you are
short of, and going to the *curve* for it rather than to the tangent.

**Where the calculator sits.** 77% of the marks formally carry one, and about
16 of the 131 actually need one — two roots of $2x^2+(\ln 2x)^2-2x\ln 2x-2x=0$,
one root of $\mathrm{e}^{2x}=2x^2$, one root of $\mathrm{e}^{2x}(6x-5)=1$, and
two values of $a$ from a cubic. This is the seventh topic in a row where that
number is an illusion. Thirty of the marks are Paper 1, and that is the most
honest slice this topic has ever had: a tangent to a written function is
asked without a calculator, and a curve given by an equation almost always
with one.

**How the checks work here.** All eight are new, and all eight rest on one
thing: **the checks walk along the curve.**

Given a point on the curve, a check takes one step to the left and one step
to the right — and for each, it solves the curve's own equation for the other
coordinate. The gradient is then the gradient of the line through the two
points it found. There is no $\frac{\mathrm{d}y}{\mathrm{d}x}=-F_x/F_y$ in
there, no chain rule, no stored answer. It is the definition, walked.

| check | what it holds your answer against |
| --- | --- |
| `verify_slope` | the gradient of the curve at points *of the curve* |
| `verify_tangent` | your line passes through the point and leans with it |
| `verify_normal` | the same, with the two gradients multiplying to $-1$ |
| `verify_where` | the point is on the curve, leans right, and there are no others |
| `verify_second` | three steps along the curve instead of a second derivative |
| `verify_right_angle` | two gradients at one shared point, product $-1$ |
| `verify_constant` | the curve is rebuilt from your letter and then walked |
| `verify_on` | the point $(a, \text{your answer})$ is on the curve |

Two consequences worth knowing before you start.

**Any arrangement of a line passes.** `30*x - 97`, `Eq(y, 30*x - 97)` and
`30*(x - 4) + 23` are one line, and the check compares lines.

**Rounded answers pass, and are checked as rounded.** When you write
$(1.84, -0.538)$, the check does not test whether that pair is on the curve —
it is not, and neither is any 3 s.f. answer. It looks for the real solution
next door and asks whether your digits round to it. Get the third figure
wrong and it will say so.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, log, Eq

language('en')                 # this notebook is in English, and so are the checks

a, b, c, h, m, r = symbols('a b c h m r')   # letters that stay letters
                                            # x, y, t, k already come from kit


def shape(build, *answers):
    # A curve built out of your own answers. While they are blank there is no
    # curve to walk, and the check prints an empty box instead of crashing.
    return curve(...) if blank(*answers) else curve(build())


print('ready; sympy', sp.__version__)
print('a curve given by an equation: ', Eq(exp(x + y), x**2 + y**2))
print('a curve that is a function:   ', Eq(y, 90*exp(-x/2)))
print('a line:                       ', 30*x - 97)
print('a point:                      ', (2*log(45), 2))
""")

md(r"""
---
## Map of techniques

| # | Technique | What the question says | First move |
| --- | --- | --- | --- |
| 1 | Tangent at a known point | *find the equation of the tangent at $x=4$* | get $y_0$ from the curve, $m$ from $f'$ |
| 2 | Normal | *normal*, *perpendicular to the curve* | $-1/m$, not $-m$ |
| 3 | Gradient given, find the point | *gradient is $\tfrac13$*, *parallel to $y=x$*, *at $70^\circ$* | set $f'=m$ and solve |
| 4 | The curve is an equation | $\mathrm{e}^{x+y}=x^2+y^2$ | differentiate both sides, keep $\frac{\mathrm{d}y}{\mathrm{d}x}$ |
| 5 | Tangent to such a curve | *the tangent at $x=1$*, *where the tangent is horizontal* | you need **both** coordinates first |
| 6 | Differentiate the relation again | $\frac{\mathrm{d}^2y}{\mathrm{d}x^2}$ with no $y=f(x)$ | differentiate the equation you already have |
| 7 | Right angle as a condition | *intersect at right angles* | two gradients, one point, product $-1$ |
| 8 | Touching as a condition | *common tangent*, *is a tangent to*, *parallel to* | two equations, not one |

**The ladder goes by what the straight line is doing in the question.**

**Rungs 1–3 — the line is the answer.** Thirty-eight marks. The curve is a
function, the work is bookkeeping, and the marks are lost on the second
coordinate and on extra roots, never on the calculus.

**Rungs 4–6 — the curve stopped being a function.** Fifty-six marks, more
than either other block. Nothing about tangents changes; what changes is that
you can no longer get $y$ by substituting $x$, so every gradient needs a pair.

**Rungs 7–8 — the line is the condition.** Thirty-seven marks. Perpendicular
and tangent stop being things you find and become things you *impose*, and
what comes out is a constant.

**The two facts the whole topic runs on.**

$$\text{tangent at }(x_0,y_0):\quad y-y_0=m(x-x_0),\qquad
m=\left.\frac{\mathrm{d}y}{\mathrm{d}x}\right|_{(x_0,y_0)}$$

$$\text{perpendicular}\iff m_1m_2=-1\qquad\text{(so the normal has }-1/m)$$

Everything else in these 131 marks is getting $m$, and getting $y_0$.
""")

# ================================================================== Part I
md(r"""
---
# Part I — the line is the answer

## Theory 1. Two numbers, and they come from different places

A tangent needs a point and a gradient. The mistake that costs whole
questions is taking both from the same line of working.

$$\underbrace{y_0=f(x_0)}_{\text{from the curve}}\qquad
\underbrace{m=f'(x_0)}_{\text{from the derivative}}$$

Three things follow, and each is worth a mark somewhere in this archive.

**If a tangent is *given*, it hands you both numbers.** *The line $y=6x-1$ is
the tangent to $y=f(x)$ at $x=4$* tells you $f'(4)=6$ **and** $f(4)=23$ — the
second because the point of contact lies on both, so you may read $f(4)$ off
the line. That is a whole mark on its own, and it is the only place in this
topic where you get a value of $f$ without knowing $f$.

**Through a composition, the chain rule survives into the gradient.** If
$h=f\circ g$ then $h'(4)=f'(g(4))\cdot g'(4)$, and $g'(4)$ is a factor people
drop while concentrating on $f'$.

**A tangent with letters in it is still just $y-y_0=m(x-x_0)$.** Paper 3 will
hand you $g(x)=(x-r)(x^2-2ax+a^2+b^2)$ and ask where its tangent crosses the
$x$-axis; the algebra is unpleasant and the method is the same three lines.
""")

md(r"""
## Task 1 🟢 — a tangent you are given, and a tangent you build

*November 2021 Paper 1 Q5(a)(b)(d), 5 marks · no calculator*

The function $f$ is defined for all $x\in\mathbb{R}$. The line $y=6x-1$ is the
tangent to the graph of $f$ at $x=4$.

**(a)** Write down the value of $f'(4)$.

**(b)** Find $f(4)$.

The function $g$ is defined for all $x\in\mathbb{R}$, where $g(x)=x^2-3x$, and
$h(x)=f\bigl(g(x)\bigr)$.

**(c)** Hence find the equation of the tangent to the graph of $h$ at $x=4$.
""")

code(r"""
q1a = ...        # f'(4)
q1b = ...        # f(4)
q1c = ...        # the tangent to h at x = 4, as an expression in x

given = curve(Eq(y, 6*x - 1))            # the tangent you were handed
verify_slope('1a', q1a, given, at=4)
verify_on('1b', q1b, given, 4)

# f itself is unknown, and the answer must not depend on which f you imagine.
# So the check tries four different functions that all satisfy f(4) = 23 and
# f'(4) = 6, composes each with g, and demands the same tangent every time.
inner = x**2 - 3*x
family = curve(Eq(y, 6*inner - 1 + c*(inner - 4)**2))
verify_tangent('1c', q1c, family, 4, params={c: (0, 2, -3, 5)})
""")

md(r"""
## Task 2 🔴 — the same three lines, with letters

*May 2022 TZ1 Paper 3 Q2(d)(ii), 6 marks · Paper 3*

Consider $g(x)=(x-r)(x^2-2ax+a^2+b^2)$ for $x\in\mathbb{R}$, where
$r,a\in\mathbb{R}$ and $b>0$. You may use
$$g'(x)=2(x-r)(x-a)+x^2-2ax+a^2+b^2 .$$

**(a)** Find the equation of the tangent to the curve $y=g(x)$ at the point
$\mathrm{A}\bigl(a,g(a)\bigr)$, as an expression in $x$.

**(b)** Hence give the $x$-coordinate of the point $\mathrm{R}$ where that
tangent meets the $x$-axis.

*The exam asks you to prove that $\mathrm{R}$ is $(r,0)$. Here you find it —
which is the same work, and something a check can hold.*
""")

code(r"""
q2 = ...         # the tangent at A, in terms of x, a, b and r
q2r = ...        # the x-coordinate of R

letters = {a: (1, 2, -1, 3), b: (2, 1, 3, 1), r: (-2, 0, 4, 1)}
cubic = curve(Eq(y, (x - r)*(x**2 - 2*a*x + a**2 + b**2)))
verify_tangent('2a', q2, cubic, a, params=letters)

# The second answer goes back into the first: R is the point of your own
# tangent whose height is zero.
verify_on('2b', 0, shape(lambda: Eq(y, q2), q2), q2r, params=letters)
""")

md(r"""
## Theory 2. The normal, and the one step where it differs

A normal is perpendicular to the tangent at the same point, so

$$m_{\text{normal}}=-\frac{1}{m_{\text{tangent}}}.$$

Not $-m$. The archive contains that slip in both directions, and it is
invisible in your own working because $-2$ and $-\tfrac12$ look equally
plausible sitting next to a gradient of $2$.

Two corners worth naming.

**Where the tangent is horizontal the normal is vertical,** and a vertical
line has no gradient at all — its equation is $x=c$, and $y=mx+c$ cannot
express it.

**A normal with a letter in it is where this topic starts being interesting.**
For $y=\tfrac1x$ the tangent at $x=t$ has gradient $-\tfrac1{t^2}$, so the
normal has gradient $t^2$ — and now the *whole family* of normals is
parametrised by $t$, which is what November 2025 Paper 3 spends 26 marks on.
""")

md(r"""
## Task 3 🟢 — a normal, printed in the question

*November 2025 TZ3 Paper 1 Q9(c), 5 marks · no calculator*

Consider $f(x)=\tfrac12x^2+kx+13$ with $k=5$. The line $L$ is normal to the
curve $y=f(x)$ at $x=-3$.

Show that the equation of $L$ is $y=-\tfrac12x+1$ by writing it down as an
expression in $x$.
""")

code(r"""
q3 = ...         # the normal at x = -3, as an expression in x

verify_normal('3', q3, curve(Eq(y, x**2/2 + 5*x + 13)), -3)
""")

md(r"""
## Task 4 🟡 — a normal with a letter for the point

*November 2025 TZ1 Paper 3 Q1(a)(i), 2 marks · Paper 3*

The curve $H$ has equation $y=\tfrac1x$, where $x\in\mathbb{R}$, $x\ne0$.
A line $N$ is normal to $H$ at $x=t$.

Show that the gradient of $N$ is $t^2$ by writing that gradient down.
""")

code(r"""
q4 = ...         # the gradient of N, in terms of t

# You hand in a gradient; the check builds the normal through the point of H
# out of it and holds that line against the curve.
line = ... if blank(q4) else q4*(x - t) + 1/t
verify_normal('4', line, curve(Eq(y, 1/x)), t, params={t: (0.5, 1, 2, 3)})
""")

md(r"""
## Theory 3. Backwards: the gradient is given, the point is not

Three phrasings, one meaning. Convert first, solve second.

| the question says | the gradient is |
| --- | --- |
| *the gradient of $L$ is $\tfrac13$* | $\tfrac13$ |
| *the tangent is parallel to $y=x$* | $1$ |
| *the tangent makes an angle of $70^\circ$ with the horizontal* | $\tan 70^\circ$ |

Then solve $f'(x)=m$, and after that three habits:

**Throw out the roots the domain forbids.** $f(x)=\ln(x^2-16)$ is given for
$x>4$; $f'(x)=\tfrac13$ has roots $8$ and $-2$, and the mark scheme says in
so many words that including $-2$ loses the mark. Extra answers are not free.

**If the question says *coordinates*, give two numbers.** Substituting back
into $f$ is a separate mark, every time.

**If the question says *exact*, do not touch the calculator at the end.**
$2\ln 45$ is exact; $7.61$ is not, and it scores zero on a question that asked
for exact coordinates even though it is the same number.
""")

md(r"""
## Task 5 🟡 — one root wanted, two available

*May 2021 TZ2 Paper 1 Q4(b), 6 marks · no calculator*

Consider $f(x)=\ln(x^2-16)$ for $x>4$. The line $L$ is the tangent to the
graph of $f$ at the point $\mathrm{B}$, and the gradient of $L$ is $\tfrac13$.

Find the $x$-coordinate of $\mathrm{B}$.
""")

code(r"""
q5 = ...         # the x-coordinate of B — a list, if you think there is more than one

# coordinates=False: this question asked for x alone, so y is not held against
# you. The domain from the question is passed in, and any answer outside it
# comes back as an extra root, which is exactly what the mark scheme does.
verify_where('5', q5, curve(Eq(y, log(x**2 - 16))), Rational(1, 3), (4.01, 30),
             coordinates=False)
""")

md(r"""
## Task 6 🟡 — exact coordinates

*May 2021 TZ1 Paper 2 Q10(b), 4 marks · calculator allowed*

Consider $f(x)=90\mathrm{e}^{-0.5x}$ for $x\in\mathbb{R}^{+}$. The line $L$ has
gradient $-1$ and is tangent to the graph of $f$ at the point $\mathrm{Q}$.

Find the **exact** coordinates of $\mathrm{Q}$.
""")

code(r"""
q6 = ...         # (x, y) — exact, both of them

verify_where('6', q6, curve(Eq(y, 90*exp(-x/2))), -1, (0.01, 20))
""")

md(r"""
## Task 7 🔴 — the gradient arrives as an angle

*May 2025 TZ3 Paper 2 Q5(b), 4 marks · calculator*

Consider $f(x)=\dfrac{(2x+a)^3}{(x+5)^2}$, where $x\ne-5$ and $a\in\mathbb{R}^{+}$.
When $x=1$, the tangent to the graph of $f$ makes an angle of $70^\circ$ with
the horizontal.

Find the two possible values of $a$, to 3 significant figures.
""")

code(r"""
q7 = ...         # a list of both values

# The letter sits inside the curve, so there is nothing to substitute the
# answer into. The check builds the curve out of each value you give and then
# walks it — and sweeps the window for values you missed.
verify_constant('7', q7, lambda v: curve(Eq(y, (2*x + v)**3/(x + 5)**2)),
                1, tan(70*pi/180), (0.1, 25))
""")

# ================================================================= Part II
md(r"""
---
# Part II — the curve is an equation

## Theory 4. $y$ is a function of $x$ even when nobody wrote it that way

$\mathrm{e}^{x+y}=x^2+y^2$ cannot be solved for $y$. It still describes a
curve, and that curve still has a gradient at each of its points. The only
new rule is the chain rule, applied to $y$:

$$\frac{\mathrm{d}}{\mathrm{d}x}\bigl(y^2\bigr)=2y\frac{\mathrm{d}y}{\mathrm{d}x},
\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\bigl(xy\bigr)=y+x\frac{\mathrm{d}y}{\mathrm{d}x},
\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\bigl(\mathrm{e}^{x+y}\bigr)
=\mathrm{e}^{x+y}\Bigl(1+\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)$$

Then the same four moves every time: differentiate both sides, collect the
$\frac{\mathrm{d}y}{\mathrm{d}x}$ terms on one side, factor, divide.

**The answer has both letters in it, and that is not a failure.** $\frac{4(3-x)}{y+2}$
is a complete answer; there is nothing further to do with it. It also means
that to get a *number* you need a *point*, both coordinates — which is the
whole difficulty of the next rung.

**When $x$ is in the base and the exponent at once, take logs first.**
$g(x)=(S/x)^x$ has no rule that applies. Writing $\ln g=x\ln(S/x)$ and
differentiating both sides gives $\frac{g'}{g}=\ln S-\ln x-1$, and since
$g\neq0$, setting $g'=0$ is setting that bracket to zero. This is implicit
differentiation used on a function that *was* explicit — the technique is
about what is convenient, not about what is possible.
""")

md(r"""
## Task 8 🟢 — an ellipse, and the printed line

*May 2025 TZ2 Paper 2 Q12(a), 4 marks · calculator*

The curve $C$ has equation $4x^2+y^2-24x+4y+20=0$.

Use implicit differentiation to show that
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\dfrac{4(3-x)}{y+2}$, by writing the
gradient down as an expression in $x$ and $y$.
""")

code(r"""
q8 = ...         # dy/dx, in terms of x and y

# No point is named, so the check picks several points of the curve itself and
# demands that one written expression give the right gradient at all of them.
verify_slope('8', q8, curve(4*x**2 + y**2 - 24*x + 4*y + 20), domain=(1.5, 4.5))
""")

md(r"""
## Task 9 🔴 — a logarithm of a product, then a tangent

*November 2021 Paper 2 Q8, 8 marks · calculator*

Consider the curve $C$ given by $y=x-xy\ln(xy)$, where $x>0$, $y>0$.

**(a)** The exam asks you to show that
$$\frac{\mathrm{d}y}{\mathrm{d}x}+\Bigl(x\frac{\mathrm{d}y}{\mathrm{d}x}+y\Bigr)
\bigl(1+\ln(xy)\bigr)=1 .$$
Do that, and then finish the job: write
$\dfrac{\mathrm{d}y}{\mathrm{d}x}$ as an expression in $x$ and $y$.

**(b)** Hence find the equation of the tangent to $C$ at the point where
$x=1$, as an expression in $x$.
""")

code(r"""
q9a = ...        # dy/dx, in terms of x and y
q9b = ...        # the tangent to C at x = 1, as an expression in x

spiral = curve(Eq(y, x - x*y*log(x*y)))
verify_slope('9a', q9a, spiral, domain=(0.4, 1.6))
verify_tangent('9b', q9b, spiral, (1, 1))
""")

md(r"""
## Theory 5. To get a number out of $\frac{\mathrm{d}y}{\mathrm{d}x}$ you need a pair

This is the whole of rung 5, and it cuts both ways.

**Forwards.** *The tangent at the point where $x=1$.* You have one coordinate;
the other comes from the **curve's own equation** with $x=1$ substituted —
here $y=1-y\ln y$, which has the single solution $y=1$. Only then does
$\frac{\mathrm{d}y}{\mathrm{d}x}$ become a number.

**Backwards.** *Where is the tangent horizontal?* Setting a fraction to zero
means setting its **numerator** to zero, and that is one equation in two
unknowns. The second equation is the curve. Solve the pair.

$$2x-\mathrm{e}^{x+y}=0\quad\text{and}\quad\mathrm{e}^{x+y}=x^2+y^2$$
$$\Longrightarrow\quad y=\ln(2x)-x$$
$$\Longrightarrow\quad 2x^2+\bigl(\ln 2x\bigr)^2-2x\ln 2x-2x=0,$$

and *that* is what the calculator is for. Two roots, so two points — and
stopping at one is the commonest lost mark of the rung.

**A gradient of $-1$ on a curve symmetric in $y=x$ is a special case worth
seeing.** $\frac{\mathrm{d}y}{\mathrm{d}x}=-1$ forces $y=x$ here, and
substituting that into the curve leaves one equation in one unknown.
""")

md(r"""
## Task 10 🔴 — the same curve, three ways

*May 2024 TZ1 Paper 2 Q11(a)(b)(d), 18 marks · calculator*

The curve $C$ is defined by $\mathrm{e}^{x+y}=x^2+y^2$ and has a line of
symmetry $y=x$. There are two points on $C$ where the tangent is horizontal,
labelled $\mathrm{P}$ and $\mathrm{Q}$.

**(a)** Show that
$\dfrac{\mathrm{d}y}{\mathrm{d}x}=\dfrac{2x-\mathrm{e}^{x+y}}{\mathrm{e}^{x+y}-2y}$
by writing it down.

**(b)** Find the coordinates of $\mathrm{P}$ and of $\mathrm{Q}$, to 3
significant figures.

**(c)** Find the coordinates of the point on $C$ where the tangent has
gradient $-1$, to 3 significant figures.
""")

code(r"""
q10a = ...       # dy/dx, in terms of x and y
q10b = ...       # [(x, y), (x, y)] — both points, 3 s.f.
q10d = ...       # (x, y) — the point where the gradient is -1, 3 s.f.

loop = curve(Eq(exp(x + y), x**2 + y**2))
verify_slope('10a', q10a, loop, domain=(0.2, 2))
verify_where('10b', q10b, loop, 0, (0.05, 3))
verify_where('10c', q10d, loop, -1, (-1, 0.5))
""")

md(r"""
## Theory 6. Differentiating the relation a second time

When there is no $y=f(x)$, there is nothing to differentiate twice — except
the equation you already have. Differentiate it again, treating both $y$ and
$\frac{\mathrm{d}y}{\mathrm{d}x}$ as functions of $x$:

$$\frac{\mathrm{d}}{\mathrm{d}x}\Bigl(x\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)
=\frac{\mathrm{d}y}{\mathrm{d}x}+x\frac{\mathrm{d}^2y}{\mathrm{d}x^2},
\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\Bigl(y\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)
=\Bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)^{2}+y\frac{\mathrm{d}^2y}{\mathrm{d}x^2}$$

The second of these is where $\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$
comes from, and it is the term people lose.

**Substitute numbers last.** Differentiate the whole relation, *then* put in
$x=1$, $y=\tfrac32$, $\frac{\mathrm{d}y}{\mathrm{d}x}=-1.7$. Substituting
first destroys the variable you were about to differentiate.

**The same move solves a differential equation you have never solved.**
$\frac{\mathrm{d}P}{\mathrm{d}t}=kP(1-P/N)$ gives
$\frac{\mathrm{d}^2P}{\mathrm{d}t^2}$ by the product rule plus one
substitution of the first equation back into itself — and that second
derivative is what tells you the population grows fastest at $P=N/2$.
""")

md(r"""
## Task 11 🔴 — a second derivative with no formula for $y$

*November 2025 TZ3 Paper 2 Q12(a)(i)(b)(ii), 6 marks · calculator*

Consider the homogeneous differential equation
$$\bigl(x^2+xy\bigr)\frac{\mathrm{d}y}{\mathrm{d}x}=x^2+xy-3y^2,
\qquad x>0,\ y>\tfrac{x}{2},$$
with $y=\tfrac32$ when $x=1$.

**(a)** Find the value of $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ when $x=1$.

**(b)** Differentiating the relation again gives
$$\bigl(x^2+xy\bigr)\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2x+y-x\Bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)^{2}
-(x+7y)\frac{\mathrm{d}y}{\mathrm{d}x}.$$
Find the value of $\dfrac{\mathrm{d}^2y}{\mathrm{d}x^2}$ when $x=1$, exactly.

*Part (d) of that question solves the equation and gets
$x^{6}(2y-x)^{3}=2(x+2y)$. The checks below walk **that** curve — the one
your solution is a point of — so nothing they do repeats the work you are
being asked to do.*
""")

code(r"""
q11a = ...       # dy/dx at x = 1
q11b = ...       # the second derivative at x = 1, exactly

solved = curve(Eq(x**6*(2*y - x)**3, 2*(x + 2*y)))
verify_slope('11a', q11a, solved, at=(1, Rational(3, 2)))
verify_second('11b', q11b, solved, (1, Rational(3, 2)))
""")

# ================================================================ Part III
md(r"""
---
# Part III — the line is the condition

## Theory 7. A right angle is an equation

*Show that the curves intersect at right angles* is not a request for a line.
It is three separate claims, and the mark scheme pays for all three:

1. the point lies on **both** curves;
2. each gradient is the gradient of **its own** curve there;
3. the two multiply to $-1$.

The failure is almost never the differentiation. It is substituting the point
into one curve's gradient and a different point into the other's, or stopping
after showing the two gradients are different.

**Families are where this gets used.** *Each member of the family $y=mx$ meets
each member of family $C$ at right angles.* The gradient of $y=mx$ at the
point $(x,y)$ on it is $m=\frac{y}{x}$ — written in $x$ and $y$, not in $m$,
which is a mark on its own and the reason the whole thing works. Then
perpendicularity says the other family has $\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{x}{y}$,
and solving *that* differential equation gives $x^2+y^2=k$: circles, cutting
every line through the origin square.
""")

md(r"""
## Task 12 🟡 — two curves, one point, one right angle

*May 2023 TZ2 Paper 1 Q8(a)(b), 4 marks · no calculator*

The functions $f$ and $g$ are defined by $f(x)=\cos x$ for
$0\le x\le\tfrac{\pi}{2}$ and $g(x)=\tan x$ for $0\le x<\tfrac{\pi}{2}$. The
curves meet at a point $\mathrm{P}$ whose $x$-coordinate is $k$.

Given that $\cos^2k=\sin k$, show that the tangent to $y=f(x)$ at $\mathrm{P}$
and the tangent to $y=g(x)$ at $\mathrm{P}$ meet at right angles — by writing
down the two gradients in terms of $k$.
""")

code(r"""
q12f = ...       # f'(k)
q12g = ...       # g'(k)

meet = nsolve(cos(x) - tan(x), x, 0.6)   # where the two curves cross
verify_right_angle('12', (q12f, q12g), curve(Eq(y, cos(x))), curve(Eq(y, tan(x))),
                   (k, cos(k)), params={k: (meet,)})
""")

md(r"""
## Task 13 🔴 — two families, cutting square everywhere

*November 2023 Paper 3 Q2(a)(i)(d), 6 marks · Paper 3*

**(a)** Consider the family of straight lines $L$ with equation $y=mx$, where
$m$ is a parameter. Write down an expression for the gradient of $L$ in terms
of $x$ and $y$.

A family of curves has equation $y^2=4a^2-4ax$, where $a>0$; a second family
has $y^2=4b^2+4bx$, where $b>0$. They meet at
$\mathrm{M}\bigl(a-b,\,2\sqrt{ab}\bigr)$.

**(b)** Show that at $\mathrm{M}$ the two curves intersect at right angles, by
writing down the two gradients in terms of $a$ and $b$.
""")

code(r"""
q13a = ...       # the gradient of L, in terms of x and y
q13f = ...       # dy/dx of the first family at M
q13g = ...       # dy/dx of the second family at M

verify_slope('13a', q13a, curve(Eq(y, m*x)), domain=(0.5, 3), params={m: (2, -1, 0.5)})

first = curve(Eq(y**2, 4*a**2 - 4*a*x))
second = curve(Eq(y**2, 4*b**2 + 4*b*x))
verify_right_angle('13b', (q13f, q13g), first, second, (a - b, 2*sqrt(a*b)),
                   params={a: (2, 3, 5), b: (1, 2, 4)})
""")

md(r"""
## Theory 8. Touching is two equations, not one

*The graphs of $f$ and $g$ have a common tangent at $x=3$.* That sentence is
worth two equations:

$$f'(3)=g'(3)\qquad\text{and}\qquad f(3)=g(3).$$

The gradients alone give parallel, not touching. The values alone give
crossing, not touching. Both together give touching, and questions of this
kind hand you exactly as many unknowns as you have equations.

Two other faces of the same idea:

**Parallel to a given line** is only the first equation, and that is enough
when the question only wants one constant: *the tangent to $y=(2x-1)\mathrm{e}^{kx}$
at $x=1$ is parallel to $y=5\mathrm{e}^{k}x$* gives
$\mathrm{e}^{k}(k+2)=5\mathrm{e}^{k}$, and since $\mathrm{e}^{k}\neq0$ — say
so — $k=3$.

**A double root is touching.** If $f(x)-\ell(x)$ factors as $(x-4)^2(x-1)$
then the line $\ell$ meets the curve twice at $x=4$, which is what tangency
means. It is an alternative proof, it is on the mark scheme, and on a cubic
it is faster than differentiating.

**And *exact* still means exact.** $a=\mathrm{e}^{1/\mathrm{e}}$ is the answer;
$1.44$ is the check that you have not blundered.
""")

md(r"""
## Task 14 🟡 — a common tangent fixes two constants

*May 2021 TZ1 Paper 1 Q4(b)(c), 6 marks · no calculator*

Consider $f(x)=-(x-h)^2+2k$ and $g(x)=\mathrm{e}^{x-2}+k$, where
$h,k\in\mathbb{R}$. The graphs of $f$ and $g$ have a common tangent at $x=3$.

**(a)** Show that $h=\dfrac{\mathrm{e}+6}{2}$, by writing $h$ down.

**(b)** Hence show that $k=\mathrm{e}+\dfrac{\mathrm{e}^2}{4}$, by writing $k$
down.

*Note. The corpus this practicum is built from prints
$k=\frac{2\mathrm{e}+\mathrm{e}^2}{4}\approx3.21$ here. The paper prints
$\mathrm{e}+\frac{\mathrm{e}^2}{4}\approx4.57$, and the paper is right.*
""")

code(r"""
q14h = ...       # h
q14k = ...       # k

# (a) is the first of the two conditions: the gradient of f at x = 3 equals
# g'(3) = e. The check rebuilds f from your h and walks it.
verify_constant('14a', q14h, lambda v: curve(Eq(y, -(x - v)**2)), 3, E, (0, 8))

# (b) is the second condition, and both answers go into it: the point that g
# passes through at x = 3 has to lie on f as well.
verify_on('14b', ... if blank(q14k) else E + q14k,
          shape(lambda: Eq(y, -(x - q14h)**2 + 2*q14k), q14h, q14k), 3)
""")

md(r"""
## Task 15 🔴 — the line is given, the curve is the unknown

*May 2023 TZ2 Paper 3 Q1(e), 8 marks · Paper 3*

For $1.4\le a\le1.5$ there is a value of $a$ for which the line $y=x$ is a
tangent to the graph of $y=\log_a x$ at a point $\mathrm{P}$.

Find the **exact** coordinates of $\mathrm{P}$ and the **exact** value of $a$.
""")

code(r"""
q15x = ...       # the x-coordinate of the tangency point, exactly
q15y = ...       # the y-coordinate of the tangency point, exactly
q15a = ...       # a, exactly

# Everything the question gave is what comes back out: the check builds the
# curve from your a, takes your own point of contact, and asks whether the
# line y = x — the one line you were given — is tangent to it there.
verify_tangent('15', x, shape(lambda: Eq(y, log(x)/log(q15a)), q15a),
               (q15x, q15y))
""")

# ============================================================ распознавание
md(r"""
---
## Trainer: name the technique in five seconds

Twelve questions from the archive, none of them solved. Say which technique
each one is, in one word, **before** doing any of them.

| code | technique |
| --- | --- |
| `tangent` | a tangent at a point the question names |
| `normal` | the word *normal*, or perpendicular to the curve |
| `point` | the gradient is given; the point is the answer |
| `implicit` | the curve is an equation; the answer keeps both letters |
| `itangent` | a tangent or a point on such a curve |
| `second` | differentiate the relation a second time |
| `right` | two curves, one point, product $-1$ |
| `condition` | touching is the claim, and a constant comes out |

1. Show that $\dfrac{\mathrm{d}y}{\mathrm{d}x}=\pm\dfrac{3x^2+1}{2\sqrt{x^3+x}}$
   for $x>0$ on $y^2=x^3+x$.
2. The tangent to $y=(2x-1)\mathrm{e}^{kx}$ at $x=1$ is parallel to
   $y=5\mathrm{e}^{k}x$. Find $k$.
3. Find the coordinates of the point on $y=\mathrm{e}^{2x}(3x-4)$ where the
   tangent is parallel to $y=x$.
4. Show that the gradient of the line normal to $y=\tfrac1x$ at $x=t$ is $t^2$.
5. Find the gradient of the tangent $T_k$ to $y=15\cos\bigl(\tfrac{\pi x}{50}\bigr)+15$
   at $\bigl(k,h(k)\bigr)$, in terms of $k$.
6. Show that $\dfrac{\mathrm{d}^2P}{\mathrm{d}t^2}=k^2P\bigl(1-\tfrac{P}{N}\bigr)
   \bigl(1-\tfrac{2P}{N}\bigr)$, given $\dfrac{\mathrm{d}P}{\mathrm{d}t}=kP\bigl(1-\tfrac{P}{N}\bigr)$.
7. At $\mathrm{M}$, show that $y^2=4a^2-4ax$ and $y^2=4b^2+4bx$ intersect at
   right angles.
8. Find the equation of the tangent to $y^2=x^3+2$ at the rational point
   $\mathrm{P}(-1,-1)$.
9. Given that the tangent to $y=\ln(x^2-16)$ at $\mathrm{B}$ has gradient
   $\tfrac13$, find the $x$-coordinate of $\mathrm{B}$.
10. Show that the line $y=x-1$ is tangent to $y=(x-1)(x^2-8x+17)$ at
    $\mathrm{A}(4,3)$.
11. The line $y=6x-1$ is the tangent to $y=f(x)$ at $x=4$, and
    $h(x)=f(x^2-3x)$. Find the tangent to $h$ at $x=4$.
12. Find, in terms of $S$, the $x$-coordinate of the maximum of $g$, where
    $\ln\bigl(g(x)\bigr)=x\ln\bigl(\tfrac{S}{x}\bigr)$.
""")

code(r"""
answers = {
    1: '',   2: '',   3: '',   4: '',
    5: '',   6: '',   7: '',   8: '',
    9: '',  10: '',  11: '',  12: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

# ================================================================== таймер
md(r"""
---
# On the timer — 8 minutes

*November 2022 Paper 2 Q11(a)(b), 6 marks · calculator*

The function $f$ is defined by $f(x)=\mathrm{e}^{2x}(3x-4)$, where
$x\in\mathbb{R}$.

**(a)** Find $f'(x)$.

**(b)** Hence, or otherwise, find the coordinates of the point on the graph of
$y=f(x)$ where the tangent is parallel to the line $y=x$. Give your answer to
3 significant figures.

Eight minutes. Part (a) is E3 and should take one; the six marks are mostly in
knowing what *parallel to $y=x$* is worth.
""")

code(r"""
qt_a = ...       # f'(x)
qt_b = ...       # (x, y), 3 s.f.

verify_derivative('timer (a)', qt_a, exp(2*x)*(3*x - 4))
verify_where('timer (b)', qt_b, curve(Eq(y, exp(2*x)*(3*x - 4))), 1, (-2, 3))
""")

md(r"""
---
# Solutions

Read these after you have written something down, not before.

## Task 1

**(a)** The tangent's gradient *is* the derivative at the point of contact:
$f'(4)=6$. **A1**

**(b)** The point of contact lies on the tangent as well as on the curve, so
$f(4)=6\cdot4-1=23$. **A1** This is the whole of the mark: nothing about $f$
is known except through the line.

**(c)** Chain rule: $h'(x)=f'\bigl(g(x)\bigr)g'(x)$. Now $g(4)=16-12=4$, which
is the point where we know things about $f$, and $g'(x)=2x-3$ so $g'(4)=5$:
$$h'(4)=f'(4)\cdot 5=6\cdot5=30 .$$
Also $h(4)=f\bigl(g(4)\bigr)=f(4)=23$. So
$$y-23=30(x-4),\qquad y=30x-97 .$$
**M1A1A1**

The coincidence that makes this question work is $g(4)=4$: without it $f'(g(4))$
would be a number nobody has. Notice it early and the question is three lines.

## Task 2

$$g(a)=(a-r)\bigl(a^2-2a^2+a^2+b^2\bigr)=b^2(a-r),\qquad
g'(a)=0+a^2-2a^2+a^2+b^2=b^2 .$$

The first factor of $g'$ vanishes at $x=a$, which is why $g'(a)$ is so clean.
Then
$$y-b^2(a-r)=b^2(x-a)\;\Longrightarrow\;y=b^2x-b^2r=b^2(x-r).$$
Setting $y=0$ and using $b>0$, so $b^2\neq0$, gives $x=r$. **A1A1M1A1M1R1**

The $b>0$ is not decoration: dividing by $b^2$ is the step, and it is legal
only because the question said so.

## Task 3

At $x=-3$: $f(-3)=\tfrac92-15+13=\tfrac52$, and $f'(x)=x+5$ so $f'(-3)=2$.
The normal has gradient $-\tfrac12$:
$$y-\tfrac52=-\tfrac12(x+3)\;\Longrightarrow\;y=-\tfrac12x-\tfrac32+\tfrac52
=-\tfrac12x+1 .$$
**A1A1A1M1A1**

Five marks for five lines, and four of them are arithmetic. This is what a
normal question looks like on Paper 1.

## Task 4

$y=x^{-1}$ gives $\frac{\mathrm{d}y}{\mathrm{d}x}=-x^{-2}$, so at $x=t$ the
tangent has gradient $-\tfrac{1}{t^2}$ and the normal has
$$m_N=\frac{-1}{-1/t^2}=t^2 . \qquad\textbf{M1A1}$$

Two marks, and the whole of the rest of that Paper 3 — 24 more marks about
how many normals of a given gradient a hyperbola has — rests on this line.

## Task 5

$$f'(x)=\frac{2x}{x^2-16}=\frac13\;\Longrightarrow\;6x=x^2-16
\;\Longrightarrow\;x^2-6x-16=0\;\Longrightarrow\;(x-8)(x+2)=0 .$$
The domain is $x>4$, so $x=8$. **M1A1M1A1M1A1**

The mark scheme says: *award A0 if the final answer includes additional
solutions.* Writing "$x=8$ or $x=-2$" is not a partially right answer here;
it is a wrong one, because $-2$ is not in the domain of $f$ at all.

## Task 6

$f'(x)=-45\mathrm{e}^{-0.5x}$, and setting that to $-1$:
$$\mathrm{e}^{-0.5x}=\tfrac1{45}\;\Longrightarrow\;-\tfrac12x=-\ln 45
\;\Longrightarrow\;x=2\ln 45 .$$
Then
$$y=90\mathrm{e}^{-\ln 45}=\frac{90}{45}=2 .$$
So $\mathrm{Q}=(2\ln 45,\,2)$. **A1M1A1A1**

The $y$-coordinate coming out as a clean $2$ is the sign you have not slipped;
if it is $1.9998$ you have rounded $x$ somewhere you should not have. And
$2\ln45=\ln 2025$ is the same answer, which is why the check compares numbers
and not strings.

## Task 7

Quotient rule, with a common factor pulled out:
$$f'(x)=\frac{3(2x+a)^2\cdot2\,(x+5)^2-(2x+a)^3\cdot2(x+5)}{(x+5)^4}
=\frac{2(2x+a)^2(x+15-a)}{(x+5)^3}.$$
At $x=1$ that is $\dfrac{(2+a)^2(16-a)}{108}$, and the angle gives
$$(2+a)^2(16-a)=108\tan 70^\circ\approx296.7 .$$
Solving the cubic: $a=2.73$ and $a=14.97\approx15.0$ (the third root is
negative and $a>0$). **M1A1A1A1**

The angle is the whole trick, and it is worth saying out loud: a line at
$70^\circ$ to the horizontal has gradient $\tan 70^\circ\approx2.75$, not
$70$ and not $\tfrac{70}{90}$.

## Task 8

$$8x+2y\frac{\mathrm{d}y}{\mathrm{d}x}-24+4\frac{\mathrm{d}y}{\mathrm{d}x}=0
\;\Longrightarrow\;(2y+4)\frac{\mathrm{d}y}{\mathrm{d}x}=24-8x
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{24-8x}{2y+4}
=\frac{4(3-x)}{y+2}.$$
**M1A1A1A1**

Two places to lose it: the $4y$ term differentiates to
$4\frac{\mathrm{d}y}{\mathrm{d}x}$ and not to $4$, and the final cancelling is
a factor of $2$ top and bottom — the printed form has $4$ in the numerator,
not $8$.

## Task 9

**(a)** Write $w=xy$, so $w'=y+x\frac{\mathrm{d}y}{\mathrm{d}x}$ and
$\frac{\mathrm{d}}{\mathrm{d}x}\bigl(w\ln w\bigr)=w'\bigl(\ln w+1\bigr)$.
Differentiating $y=x-xy\ln(xy)$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=1-\Bigl(y+x\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)
\bigl(1+\ln(xy)\bigr),$$
which rearranges to the printed line. **M1A1A1** Solving for the derivative,
$$\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{1-y\bigl(1+\ln(xy)\bigr)}{1+x\bigl(1+\ln(xy)\bigr)} .$$

**(b)** At $x=1$ the curve says $y=1-y\ln y$, and $y=1$ satisfies it — it is
the only positive solution. Substituting $x=y=1$: $\ln(xy)=0$, so
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{1-1\cdot1}{1+1\cdot1}=0,$$
and the tangent is the horizontal line $y=1$. **M1A1M1A1A1**

The point is worth dwelling on: the *only* way to get that $y=1$ is from the
curve's own equation. There is no formula for $y$ to substitute into.

## Task 10

**(a)** Differentiating $\mathrm{e}^{x+y}=x^2+y^2$:
$$\mathrm{e}^{x+y}\Bigl(1+\frac{\mathrm{d}y}{\mathrm{d}x}\Bigr)
=2x+2y\frac{\mathrm{d}y}{\mathrm{d}x}
\;\Longrightarrow\;
\frac{\mathrm{d}y}{\mathrm{d}x}
=\frac{2x-\mathrm{e}^{x+y}}{\mathrm{e}^{x+y}-2y}.$$

**(b)** Horizontal means the numerator vanishes: $\mathrm{e}^{x+y}=2x$, so
$x+y=\ln(2x)$ and $y=\ln(2x)-x$. Substituting into the curve,
$$2x=x^2+\bigl(\ln(2x)-x\bigr)^2
\;\Longrightarrow\;2x^2+\bigl(\ln 2x\bigr)^2-2x\ln 2x-2x=0 .$$
The calculator gives $x=0.331$ and $x=1.842$, and then
$y=\ln(2x)-x$ gives
$$\mathrm{P}=(0.331,\,-0.743),\qquad \mathrm{Q}=(1.84,\,-0.538).$$

**(c)** Gradient $-1$ means $2x-\mathrm{e}^{x+y}=-\bigl(\mathrm{e}^{x+y}-2y\bigr)$,
that is $x=y$ — the line of symmetry, which the diagram told you. Then
$\mathrm{e}^{2x}=2x^2$ gives $x=-0.451$, and the point is
$(-0.451,\,-0.451)$.

Two things to take away. **The horizontal-tangent condition is about the
numerator alone**, and it is one equation in two unknowns until you bring the
curve back in. And **there are two points, not one** — the check counts them,
and so does the mark scheme.

## Task 11

**(a)** Substitute straight into the relation: with $x=1$ and $y=\tfrac32$,
$$\bigl(1+\tfrac32\bigr)\frac{\mathrm{d}y}{\mathrm{d}x}=1+\tfrac32-3\cdot\tfrac94
=-\tfrac{17}{4}\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=-\tfrac{17}{10}
=-1.7 .$$

**(b)** Now put $x=1$, $y=\tfrac32$, $\frac{\mathrm{d}y}{\mathrm{d}x}=-1.7$
into the second relation:
$$\tfrac52\cdot\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2+\tfrac32-1\cdot(-1.7)^2-\bigl(1+\tfrac{21}{2}\bigr)(-1.7)
=3.5-2.89+19.55=20.16,$$
$$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}=\frac{20.16}{2.5}=8.064=\frac{1008}{125}.$$
**M1A1**

Where does the second relation come from? Differentiate the first one:
$$\bigl(2x+y+x\tfrac{\mathrm{d}y}{\mathrm{d}x}\bigr)\frac{\mathrm{d}y}{\mathrm{d}x}
+\bigl(x^2+xy\bigr)\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
=2x+y+x\frac{\mathrm{d}y}{\mathrm{d}x}-6y\frac{\mathrm{d}y}{\mathrm{d}x},$$
and collecting the $\frac{\mathrm{d}y}{\mathrm{d}x}$ terms on the right gives
the printed line, with the $-x\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$
coming from the product rule on $x\frac{\mathrm{d}y}{\mathrm{d}x}$ inside the
bracket.

*A footnote on the corpus this practicum was built from: it prints that
relation with $+2x\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$ instead of
$-x\bigl(\frac{\mathrm{d}y}{\mathrm{d}x}\bigr)^2$, which gives the wrong
number here. The paper is right; substituting and getting $8.064$ is how you
tell.*

## Task 12

$f'(x)=-\sin x$, so $f'(k)=-\sin k$. And $g'(x)=\sec^2x$, so
$$g'(k)=\sec^2 k=\frac{1}{\cos^2 k}=\frac{1}{\sin k}$$
using the given $\cos^2k=\sin k$. Therefore
$$f'(k)\,g'(k)=-\sin k\cdot\frac{1}{\sin k}=-1,$$
so the tangents are perpendicular. **A1A1R1**

That substitution is the entire question. Without $\cos^2k=\sin k$ the product
is $-\sin k\sec^2k$ and stays a function of $k$; with it, everything cancels.

For the record, part (c): $\cos^2k=\sin k$ becomes $1-\sin^2k=\sin k$, so
$\sin^2k+\sin k-1=0$ and $\sin k=\frac{-1+\sqrt5}{2}$, the positive root.

## Task 13

**(a)** A point $(x,y)$ on $y=mx$ has $m=\dfrac{y}{x}$, and since the gradient
of the line *is* $m$, the gradient of $L$ is $\dfrac{y}{x}$. **A1**

One mark, and it is the hinge of the whole 31-mark investigation: written in
$x$ and $y$, the gradient of the family can be fed straight into
perpendicularity, and $\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{x}{y}$ solves to
$x^2+y^2=k$.

**(b)** Differentiating each family implicitly,
$$y^2=4a^2-4ax\;\Longrightarrow\;2y\frac{\mathrm{d}y}{\mathrm{d}x}=-4a
\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{2a}{y},$$
$$y^2=4b^2+4bx\;\Longrightarrow\;\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{2b}{y}.$$
At $\mathrm{M}$, where $y=2\sqrt{ab}$, these are $-\dfrac{a}{\sqrt{ab}}$ and
$\dfrac{b}{\sqrt{ab}}$, and
$$-\frac{a}{\sqrt{ab}}\cdot\frac{b}{\sqrt{ab}}=-\frac{ab}{ab}=-1 .$$
**M1A1M1A1A1**

Both parabolas are drawn as $y^2=\dots$, so implicit differentiation is not a
choice made for elegance — solving for $y$ would put a square root in
everything and a $\pm$ in front of it.

## Task 14

**(a)** $f'(x)=-2(x-h)$ and $g'(x)=\mathrm{e}^{x-2}$, so $g'(3)=\mathrm{e}$.
A common tangent at $x=3$ means the gradients agree there:
$$-2(3-h)=\mathrm{e}\;\Longrightarrow\;3-h=-\tfrac{\mathrm{e}}{2}
\;\Longrightarrow\;h=3+\tfrac{\mathrm{e}}{2}=\frac{\mathrm{e}+6}{2}.$$
**A1M1A1**

**(b)** And the values agree there too — that is the second half of *common
tangent*:
$$-(3-h)^2+2k=\mathrm{e}+k .$$
With $3-h=-\tfrac{\mathrm{e}}{2}$ the left side is $-\tfrac{\mathrm{e}^2}{4}+2k$,
so
$$k=\mathrm{e}+\frac{\mathrm{e}^2}{4}\approx4.57 .$$
**M1A1A1**

Everything about this question is in the phrase *common tangent*: two
conditions, two unknowns, one at a time.

## Task 15

Let $y=\log_a x=\dfrac{\ln x}{\ln a}$. Tangency to $y=x$ needs the gradient to
be $1$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{1}{x\ln a}=1
\;\Longrightarrow\;x=\frac{1}{\ln a},$$
and needs the point to be on both lines, so $\log_a x=x$:
$$\frac{\ln x}{\ln a}=x .$$
Substituting $x=\frac1{\ln a}$ into that gives
$\ln\bigl(\tfrac1{\ln a}\bigr)=1$, hence $\tfrac1{\ln a}=\mathrm{e}$ and so
$$x=\mathrm{e},\qquad \mathrm{P}=(\mathrm{e},\mathrm{e}),\qquad
\ln a=\frac1{\mathrm{e}},\qquad a=\mathrm{e}^{1/\mathrm{e}}\approx1.4447 .$$
**A1M1A1M1A1A1M1A1**

The $1.4\le a\le1.5$ in the question is a check, not a method: it tells you
which of the plausible answers you are heading for. And $\mathrm{P}=(\mathrm{e},\mathrm{e})$
is on $y=x$ by construction, so finding $x$ finds both coordinates.

---
### On the timer

**(a)** Product rule:
$$f'(x)=2\mathrm{e}^{2x}(3x-4)+3\mathrm{e}^{2x}=\mathrm{e}^{2x}(6x-5).$$
**M1A1A1**

**(b)** *Parallel to $y=x$* means gradient $1$:
$$\mathrm{e}^{2x}(6x-5)=1 .$$
Nothing algebraic will solve that; the calculator gives $x=0.863$, and
$$y=\mathrm{e}^{2(0.863)}\bigl(6(0.863)-4\bigr)=-7.93 .$$
So the point is $(0.863,\,-7.93)$. **M1A1A1**

Substitute into $f$, not into $f'$. It is the single most common way to lose
the last mark on a question of this shape, and it is entirely mechanical to
avoid.

---
### Key to the recognition drill

1 `implicit` — $y^2=x^3+x$ cannot be split, and the answer keeps both letters.
2 `condition` — the tangent is not asked for; *parallel* is an equation on $k$.
3 `point` — the gradient is given as $1$, and the point is the answer.
4 `normal` — the word is in the question, and $-1/m$ is the whole of it.
5 `tangent` — a gradient at a named point of a written function.
6 `second` — differentiate the relation again, then substitute it into itself.
7 `right` — two curves, one point, product $-1$.
8 `itangent` — a tangent, but to a curve given by an equation.
9 `point` — gradient $\tfrac13$ given, $x$-coordinate wanted.
10 `condition` — *show that the line is tangent*: touching is the claim.
11 `tangent` — a tangent at a named point, with a chain rule inside.
12 `implicit` — take logs of both sides and differentiate; $x$ is in the base
   and the exponent at once.

Four of these are worth arguing about, and the argument is the point.

**1 could be `itangent`.** It is not: nothing is asked about a line. The
question stops at $\frac{\mathrm{d}y}{\mathrm{d}x}$, and that is rung 4.
Part (f) of the same paper *is* `itangent`, and that is question 8 here.

**3 and 9 look different and are the same.** One says *parallel to $y=x$* and
one says *gradient $\tfrac13$*; both are a number, and both want a point back.
The phrasing is the only thing that changes.

**10 could be `tangent`.** The word is there, and the technique is not:
nothing is being found. What is being *established* is that touching happens,
which needs two conditions or a double root — rung 8.

**12 could be `point`,** because a maximum is where the gradient is zero. But
the gradient of $(S/x)^x$ does not exist until you take logarithms, and the
taking of logarithms is the question. The zero is the last line, not the first.

---
### Where the marks went, across the topic

| technique | marks | share |
| --- | --- | --- |
| Touching as a condition | 23 | 18% |
| The curve is an equation | 21 | 16% |
| Tangent to such a curve | 20 | 15% |
| Gradient given, find the point | 17 | 13% |
| Differentiate the relation again | 15 | 11% |
| Tangent at a known point | 14 | 11% |
| Right angle as a condition | 14 | 11% |
| Normal | 7 | 5% |

Three things stand out.

**The two ends of the ladder are worth more than the middle.** Rungs 1–3, the
ones every course drills, carry 38 marks. Rungs 7–8, where the line stops
being the answer, carry 37 — and almost nobody practises them, because they do
not look like tangent questions at all until you notice the word *common*.

**Rungs 4–6 are the biggest single block at 56 marks,** and the calculus in
them is one rule: $y$ is a function of $x$, so it brings a
$\frac{\mathrm{d}y}{\mathrm{d}x}$ with it. Everything else is bookkeeping —
and the bookkeeping is where the marks go.

**Forty-two of the 131 marks are Paper 3.** The same shape E3 had: this
material does not appear as a five-mark question at the end of a paper, it
appears as one step of a twenty-eight mark investigation, over and over. The
November 2023 investigation on orthogonal families and the November 2025 one
on normals to hyperbolas are 57 marks between them, of which this topic
claims 8 — the other 49 belong to E7, B4 and A5, and that is the honest
picture of how Paper 3 is built.
""")


def build():
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python", "name": "python3"},
                       "language_info": {"name": "python"}},
          "nbformat": 4, "nbformat_minor": 5}
    os.makedirs(os.path.dirname(NOTEBOOK), exist_ok=True)
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    codes = sum(1 for cc in cells if cc['cell_type'] == 'code')
    print(f'{NOTEBOOK}: {len(cells)} ячеек, из них {codes} с кодом')


if __name__ == '__main__':
    build()
