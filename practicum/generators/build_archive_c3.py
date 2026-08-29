"""Собирает архивный ноутбук C3: весь корпус темы, по приёмам, подряд.

Второй ноутбук в формате, опробованном на B4. Практикум C3 учит — лестница,
теория, уровни, тренажёр. Этот ноутбук не учит, он даёт набивать руку: вопрос,
ячейка для ответа с мгновенной проверкой, разбор в конце. Ничего больше.

Внутри — тригонометрические уравнения и тождества из архива AA HL, сессии
May 2021 — November 2025: 35 вопросов и 129 баллов, разложенные по девяти
приёмам карточки geometry-trigonometric-equations.yaml.

Почему 35, а не 45. Корпус числит за темой 45 блоков (176 баллов), но:

  * семь блоков (28 баллов) темой не являются — четыре про комплексные числа
    (аргумент, геометрическое место), три вообще без тригонометрии. Это
    ровно те блоки, что перечислены в corpus_issues карточки;
  * ноябрь 2023 лежит в корпусе двумя зональными копиями одной бумаги —
    Q12(c) посчитан дважды (7 баллов);
  * три блока (14 баллов) получают тождество возведением в степень
    по Муавру: sin 5θ, (1 ± i tan θ)^4, tan(π/12) через аргумент. Их приём
    комплексный, и они уходят в A6.

Обратно добавлены два: sin 75° через формулу сложения (2025-MAY-TZ1-P1-Q11-C-I,
в корпусе тема блока — geometry.trigonometry) и sin 3θ (2025-NOV-TZ1-P1-Q08-A).
Второй — единственное пересечение с A6: карточка A6 числит его за собой как
тождество по Муавру, но в бумаге стоит просто «show that», и METHOD 1
markscheme — формула сложения углов. Здесь он поэтому есть; доли тем в карте
при этом не тронуты, см. заметку к C3 в map.yaml.

Ответы не хранятся почти нигде: verify_roots подставляет каждый корень в само
уравнение и сканирует отрезок на полноту набора, verify_identity проверяет
переход, verify_param_set опрашивает условие, verify_solution_set решает
неравенство сам. Хеш нужен девять раз из тридцати семи: восемь раз это
калькуляторное число с тремя значащими цифрами (такое число уравнению точно
не удовлетворяет, и подставлять его некуда), а в 5.7 — промежуточная величина,
которую проверке неоткуда вывести, не выдав всю выкладку.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_c3.py прогоняет весь ноутбук
с заполненными ответами и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
import kit
from kit import digest, sig

sq = sp.sqrt
R = sp.Rational
x = sp.Symbol('x')

NOTEBOOK = os.path.join(ROOT,
                        'practicum/geometry/archive-c3-trigonometric-equations.ipynb')


def dn(value, sf=3):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dser(expr, var):
    # то же, чем сверяет check_series: значения в нескольких точках,
    # поэтому 2/cos(pi/n) и 2*sec(pi/n) дают один хеш
    return digest(kit._series_canon(expr, var))


# --- хеши для тех девяти ответов, что подстановкой не проверяются ---
D_44 = de((-1 + sq(5)) / 2)      # sin k = (−1 + √5)/2, «в форме (a + √b)/c»
D_45 = dn(4.32)                  # f(α) при sec α = 1.5
D_54A = dn(19.5)                 # 3cos2x + 11sinx − 6 = 0 на [0°, 180°]
D_54B = dn(161)
D_91 = dn(1.90)                  # θ = 2 sin θ
D_94 = dn(0.234)                 # первый раз, когда груз на высоте 1.5 м
D_95A = dn(7.24)                 # угол наклона касательной π/8
D_95B = dn(42.8)
D_57 = dser(2 / sp.cos(sp.pi / sp.Symbol('n')), sp.Symbol('n'))  # сторона a

# --- эталонные ответы; в ноутбук не попадают, см. check_archive_c3.py ---
ANSWERS = {
    'q1_1': '[pi, 3*pi]',
    'q1_2': 'sin(-k*x)**2/(-x)**2',

    'q2_1': '[25, 115]',
    'q2_2': '[17*pi/6]',

    'q3_1': '(p + q)/(1 - p*q)',
    'q3_2': 'atan((x/(x + 1) + 1)/(1 - x/(x + 1)))',
    'q3_3': 'sin(pi/4)*cos(pi/6) + cos(pi/4)*sin(pi/6)',
    'q3_4': '2*sin(t)*cos(t)*cos(t) + (1 - 2*sin(t)**2)*sin(t)',
    'q3_5': '(-x/y + 1)/(1 + x/y)',

    'q4_1': '[pi/6, 5*pi/6]',
    'q4_2': '-sqrt(5)/2',
    'q4_4': '(-1 + sqrt(5))/2',
    'q4_5': '4.32',

    'q5_1': '[-pi/2, pi/6, 5*pi/6]',
    'q5_2': '[3*pi/2]',
    'q5_3': '3*(1 - 2*sin(x)**2) + 11*sin(x)',
    'q5_4a': '19.5',
    'q5_4b': '161',
    'q5_5': '2*sin(x)*cos(x) + (1 - 2*sin(x)**2) - 1',
    'q5_6': '2*a**2*(1 - cos(2*pi/n))',
    'q5_7': '2/cos(pi/n)',

    'q6_1': '[pi/4, 5*pi/4, 7*pi/6, 11*pi/6]',
    'q6_2': '[pi/6, pi/2, 5*pi/6]',
    'q6_3a': 'sin(t)*(16*sin(t)**4 - 20*sin(t)**2 + 5)',
    'q6_3b': '[(5 - sqrt(5))/8, (5 + sqrt(5))/8]',

    'q7_1': '[pi/12, 7*pi/12]',
    'q7_2': '[pi/6, 5*pi/6]',

    'q8_1': '[7*pi/12, 11*pi/12]',
    'q8_2': 'Interval.open(pi/4, 3*pi/4)',
    'q8_3': '[-Rational(1, 2)]',
    'q8_4': 'Interval(pi/3, 2*pi/3) - FiniteSet(pi/2)',

    'q9_1': '1.90',
    'q9_2': '[pi/2]',
    'q9_3': '[3*pi/2, 7*pi/2]',
    'q9_4': '0.234',
    'q9_5a': '7.24',
    'q9_5b': '42.8',
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
# C3 archive: trigonometric equations and identities

**Every past-paper question on this topic, grouped by technique.** Not a
practicum — a drill. There is no theory here and no ladder to climb: the
theory is in *Practicum C3*, and this notebook is what you open afterwards,
when the only thing left is to do them all until the moves are automatic.

**What is inside.** The whole of `geometry.trigonometric_equations` and the
identities that belong with it, sessions May 2021 — November 2025:
**35 questions, 129 marks**, in nine sections, one section per technique.

The corpus records 45 blocks and 176 marks for the topic. The difference is
material that is not this topic: four blocks are complex numbers wearing a
trigonometric hat, three have no trigonometry in them at all, one November
2023 question is counted twice because that session sits in the archive as
two zonal copies of one paper, and three identities are obtained by raising
a complex number to a power — those live in *Practicum A6*.

**This is the least calculator-dependent topic in the archive.** Twenty-six
of the thirty-five questions are Paper 1, and section 9 — the whole of the
GDC work — is ten marks. If a question here has an ugly answer, you have
almost certainly gone wrong.

**How to work.** Read the question, answer in the cell below it, run the
cell. The check is not a comparison with a stored answer — it goes back to
the equation and asks it. A root is right when it satisfies the equation,
a set of roots is right when the interval holds no others, an identity is
right when the two sides agree everywhere. So an answer arrived at by a
wrong route still has to be true.

Nine of the checks do compare a hash. Eight of them are the same case — a
calculator answer given to three significant figures, which does not satisfy
the equation exactly, so there is nothing to substitute it into. The ninth is
5.7, where the answer is a step on the way and a check that could derive it
would have to give the whole derivation away.

Leave a cell blank and it prints ⬜ and moves on, which means you can run
the whole notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before — and read the markscheme note in it,
because that is where the marks actually are.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The unit circle: a reference angle, then every root in the interval | 2 | 5 |
| 2 | A compound argument: what sits under the function is not $x$ | 2 | 9 |
| 3 | The compound angle formulas | 5 | 15 |
| 4 | The Pythagorean identity, and the quadratic it makes | 5 | 18 |
| 5 | The double angle, and the quadratic it makes | 7 | 27 |
| 6 | Factorise — never divide | 3 | 16 |
| 7 | Reduce it to a tangent | 2 | 10 |
| 8 | Choosing which roots survive | 4 | 19 |
| 9 | Solving numerically | 5 | 10 |

One sentence to carry into the exam: **finding a root is half the question.**
The other half is every other root in the interval, and the markscheme pays
for both.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/geometry to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, FiniteSet, Rational, solveset

import matplotlib.pyplot as plt
import numpy as np

language('en')                 # this notebook is in English, and so are the checks

a, n, p, q = symbols('a n p q')


# Draw the curve so you can count the roots before you name them. `zeros=True`
# marks where it crosses. Angles are in radians; pass degrees=True for degrees.
def show(*curves, span=(0, 2*pi), size=(6.5, 3.2), degrees=False, zeros=True):
    lo, hi = float(span[0]), float(span[1])
    grid = np.linspace(lo, hi, 2000)
    fig, ax = plt.subplots(figsize=size)
    for item in curves:
        expr, name = item if isinstance(item, tuple) else (item, None)
        g = lambdify(x, expr, 'math')
        vals = []
        for u in grid:
            try:
                v = float(g(float(u) * (np.pi/180 if degrees else 1)))
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                v = float('nan')
            vals.append(v if abs(v) < 1e3 else float('nan'))
        ax.plot(grid, vals, lw=1.7, label=name or f'y = {expr}')
    ax.axhline(0, color='0.6', lw=.8)
    ax.grid(alpha=.3)
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


print('ready; sympy', sp.__version__)
print('a set of roots:  ', [pi/6, 5*pi/6])
print('an exact value:  ', -sqrt(5)/2)
print('an interval:     ', Interval(pi/3, 2*pi/3) - FiniteSet(pi/2))
print('degrees stay numbers: the interval 0 to 180 is written (0, 180)')
""")

# ----------------------------------------------------------------- section 1
md(r"""
---
## 1 · The unit circle: a reference angle, then every root in the interval

*One trigonometric function, and its argument is $x$ itself.* Take the
inverse to get the reference angle, then rebuild the rest by the symmetry of
the quarters, then keep the ones inside the interval. **2 questions, 5
marks.**

The thinnest section in the archive, and that is the point: this technique is
almost never the whole question. It is the last two lines of nearly every
other question in this notebook.
""")

md(r"""
### 1.1 · May 2021 TZ2, Paper 1, Q10(a) · 3 marks · no calculator

Consider the function $f$ defined by $f(x)=6+6\cos x$, for
$0\le x\le 4\pi$.

The graph of $f$ touches the $x$-axis at the points A and B.

Find the $x$-coordinates of A and B.
""")

code(r"""
q1_1 = [...]                   # both x-coordinates

verify_roots('1.1', q1_1, 6 + 6*cos(x), (0, 4*pi))
""")

md(r"""
### 1.2 · November 2023, Paper 1, Q9(a) · 2 marks · no calculator

Consider the function $f(x)=\dfrac{\sin^{2}(kx)}{x^{2}}$, where $x\ne 0$
and $k\in\mathbb{R}^{+}$.

Show that $f$ is an even function.
""")

code(r"""
q1_2 = ...                     # f(-x), written out before you simplify it

verify_identity('1.2', q1_2, sin(k*x)**2/x**2)
""")

# ----------------------------------------------------------------- section 2
md(r"""
---
## 2 · A compound argument: what sits under the function is not $x$

*The function is applied to $ax+b$ — to $2x-5^\circ$, to $\tfrac{x}{2}+\tfrac{\pi}{3}$.*
Name that whole thing as the new variable, **convert the interval to match
it**, solve there, and only then come back to $x$. **2 questions, 9 marks,
both Paper 1.**

The interval is where the marks go. Under $2x$ on $[0,\pi]$ the argument runs
over $[0,2\pi]$, so there are twice as many roots as you would guess.
""")

md(r"""
### 2.1 · May 2024 TZ2, Paper 1, Q1 · 4 marks · no calculator

Solve $\tan(2x-5^\circ)=1$ for $0^\circ\le x\le 180^\circ$.
""")

code(r"""
q2_1 = [...]                   # in degrees, as plain numbers

verify_roots('2.1', q2_1, tan((2*x - 5)*pi/180) - 1, (0, 180))
""")

md(r"""
### 2.2 · May 2022 TZ2, Paper 1, Q4 · 5 marks · no calculator

Find the least positive value of $x$ for which
$\cos\!\left(\dfrac{x}{2}+\dfrac{\pi}{3}\right)=\dfrac{1}{\sqrt{2}}$.
""")

code(r"""
q2_2 = [...]                   # a list holding the one value you want

# there is exactly one solution below 3*pi, so checking the interval (0, 3*pi)
# also checks that yours is the least positive one
verify_roots('2.2', q2_2, cos(x/2 + pi/3) - 1/sqrt(2), (0, 3*pi))
""")

# ----------------------------------------------------------------- section 3
md(r"""
---
## 3 · The compound angle formulas

*The angle is a sum or a difference of two angles that are each interesting
on their own.* In practice: an exact value is wanted for an angle that is not
on the unit circle ($75^\circ$, $\pi/12$), or two arctangents have to be added.
**5 questions, 15 marks.**

$$\sin(A\pm B)=\sin A\cos B\pm\cos A\sin B$$
$$\cos(A\pm B)=\cos A\cos B\mp\sin A\sin B$$
$$\tan(A\pm B)=\frac{\tan A\pm\tan B}{1\mp\tan A\tan B}$$

The sign in the cosine and the tangent is the opposite of the sign on the
left. That is the single most common slip in the topic.
""")

md(r"""
### 3.1 · May 2021 TZ2, Paper 1, Q12(b) · 4 marks · no calculator

Show that $\arctan p+\arctan q\equiv\arctan\!\left(\dfrac{p+q}{1-pq}\right)$
where $p,q>0$ and $pq<1$.
""")

code(r"""
# put A = arctan p and B = arctan q, so tan A = p and tan B = q
q3_1 = ...                     # tan(A + B), in terms of p and q

verify_identity('3.1', q3_1, tan(atan(p) + atan(q)), var=p)
""")

md(r"""
### 3.2 · May 2021 TZ2, Paper 1, Q12(c) · 3 marks · no calculator

Verify that $\arctan(2x+1)=\arctan\!\left(\dfrac{x}{x+1}\right)+\dfrac{\pi}{4}$
for $x\in\mathbb{R}$, $x>0$.
""")

code(r"""
# pi/4 is arctan 1, so the right-hand side is a sum of two arctangents:
# apply 3.1 to it and write the single arctangent it collapses to
q3_2 = ...

verify_identity('3.2', q3_2, atan(2*x + 1))
""")

md(r"""
### 3.3 · May 2025 TZ1, Paper 1, Q11(c)(i) · part of 7 marks · no calculator

Using an appropriate compound angle identity, show that
$\sin 75^\circ=\dfrac{\sqrt{2}+\sqrt{6}}{4}$.
""")

code(r"""
q3_3 = ...                     # sin 75 as an expanded sum of exact values

verify_exact('3.3', q3_3, (sqrt(2) + sqrt(6))/4)
""")

md(r"""
### 3.4 · November 2025 TZ1, Paper 1, Q8(a) · 4 marks · no calculator

Show that $\sin 3\theta\equiv 3\sin\theta-4\sin^{3}\theta$.

*The markscheme allows De Moivre here, and Practicum A6 drills it that way.
The angle sum is shorter, and it is the method this section is about.*
""")

code(r"""
# 3*t is 2*t + t; expand, then clear the double angles
q3_4 = ...                     # your expression, in sin(t) and cos(t)

verify_identity('3.4', q3_4, 3*sin(t) - 4*sin(t)**3, var=t)
""")

md(r"""
### 3.5 · November 2023, Paper 3, Q2(e)(i) · 2 marks · calculator

Two families of curves $F$ and $G$ meet at an acute angle $\alpha$. Writing
$f(x,y)$ for the gradient of $F$ and $g(x,y)$ for the gradient of $G$, it can
be shown that

$$g(x,y)=\frac{f(x,y)+\tan\alpha}{1-f(x,y)\tan\alpha}.$$

Consider the case where $f(x,y)=-\dfrac{x}{y}$, for $x\ne 0$, $y\ne 0$, and
$\alpha=\dfrac{\pi}{4}$.

Show that $g(x,y)=\dfrac{y-x}{y+x}$.
""")

code(r"""
q3_5 = ...                     # the formula with f and tan(pi/4) substituted

verify_identity('3.5', q3_5, (y - x)/(y + x))
""")

# ----------------------------------------------------------------- section 4
md(r"""
---
## 4 · The Pythagorean identity, and the quadratic it makes

*One function appears squared and another appears to the first power.*
Replace $\cos^{2}x$ by $1-\sin^{2}x$ (or the other way round) so that only one
function is left, and solve the quadratic. **5 questions, 18 marks.**

Then throw away the root outside $[-1,1]$ — $\sin x=2$ is not a case to
investigate — and solve what remains.

Three of these five run the identity **backwards**: you are given one function
and asked for another, exactly. The technique is the same; the mark that gets
lost is the sign, and only the quadrant decides it.
""")

md(r"""
### 4.1 · May 2021 TZ2, Paper 1, Q2 · 7 marks · no calculator

Solve the equation $2\cos^{2}x+5\sin x=4$, $0\le x\le 2\pi$.
""")

code(r"""
q4_1 = [...]

verify_roots('4.1', q4_1, 2*cos(x)**2 + 5*sin(x) - 4, (0, 2*pi))
""")

md(r"""
### 4.2 · May 2021 TZ1, Paper 1, Q6 · 4 marks · no calculator

It is given that $\operatorname{cosec}\theta=\dfrac{3}{2}$, where
$\dfrac{\pi}{2}<\theta<\dfrac{3\pi}{2}$.

Find the exact value of $\cot\theta$.
""")

code(r"""
q4_2 = ...                     # exact: a surd, not a decimal

# the check rebuilds theta from what you were given and asks the angle itself
verify_exact('4.2', q4_2, cot(pi - asin(Rational(2, 3))))
""")

md(r"""
### 4.3 · May 2023 TZ2, Paper 1, Q8(a) · 1 mark · no calculator

The functions $f$ and $g$ are defined by

$$f(x)=\cos x,\ 0\le x\le\tfrac{\pi}{2}\qquad
g(x)=\tan x,\ 0\le x<\tfrac{\pi}{2}.$$

The curves $y=f(x)$ and $y=g(x)$ intersect at a point P whose $x$-coordinate
is $k$, where $0<k<\tfrac{\pi}{2}$.

Show that $\cos^{2}k=\sin k$.

*One line, and there is nothing for a check to hold on to — the solution is
at the end.*
""")

md(r"""
### 4.4 · May 2023 TZ2, Paper 1, Q8(c) · 3 marks · no calculator

Find the value of $\sin k$. Give your answer in the form
$\dfrac{a+\sqrt{b}}{c}$, where $a,c\in\mathbb{Z}$ and $b\in\mathbb{Z}^{+}$.
""")

code(r"""
q4_4 = ...                     # exact

check_expr('4.4', q4_4, 'D_44')
""".replace("'D_44'", repr(D_44)))

md(r"""
### 4.5 · May 2025 TZ1, Paper 2, Q6(c) · 3 marks · calculator

Consider the function $f(x)=4\cot x+\sin x$, where $0<x<\pi$.

It is given that $\sec\alpha=1.5$, where $0<\alpha<\pi$.

Find the value of $f(\alpha)$.
""")

code(r"""
q4_5 = ...                     # three significant figures

check_num('4.5', q4_5, 3, 'D_45')
""".replace("'D_45'", repr(D_45)))

# ----------------------------------------------------------------- section 5
md(r"""
---
## 5 · The double angle, and the quadratic it makes

*The same equation holds both $2x$ and $x$.* Choose the form of the double
angle that leaves you with the function already there — and there is a right
choice:

$$\cos 2x=1-2\sin^{2}x\quad\text{if $\sin x$ is next to it},\qquad
\cos 2x=2\cos^{2}x-1\quad\text{if $\cos x$ is},$$
$$\sin 2x=2\sin x\cos x\quad\text{if a factorisation is coming}.$$

**7 questions, 27 marks — the largest section here.** Choose the other form
and you are not wrong, only slower: it introduces the second function and you
have to remove it again.
""")

md(r"""
### 5.1 · May 2023 TZ1, Paper 1, Q3 · 6 marks · no calculator

Solve $\cos 2x=\sin x$, where $-\pi\le x\le\pi$.
""")

code(r"""
q5_1 = [...]

verify_roots('5.1', q5_1, cos(2*x) - sin(x), (-pi, pi))
""")

md(r"""
### 5.2 · May 2025 TZ3, Paper 1, Q3 · 5 marks · no calculator

Solve the equation $2\cos 2\theta-5\cos\theta+2=0$, where
$\pi\le\theta\le 2\pi$.
""")

code(r"""
q5_2 = [...]                   # theta is x here

verify_roots('5.2', q5_2, 2*cos(2*x) - 5*cos(x) + 2, (pi, 2*pi))
""")

md(r"""
### 5.3 · November 2025 TZ3, Paper 2, Q1(a) · 2 marks · calculator

Show that $3\cos 2x+11\sin x=3+11\sin x-6\sin^{2}x$.
""")

code(r"""
q5_3 = ...                     # the left-hand side with cos(2x) replaced

verify_identity('5.3', q5_3, 3*cos(2*x) + 11*sin(x))
""")

md(r"""
### 5.4 · November 2025 TZ3, Paper 2, Q1(b) · 3 marks · calculator

Hence, or otherwise, solve the equation $3\cos 2x+11\sin x-6=0$ for
$0^\circ\le x\le 180^\circ$.
""")

code(r"""
q5_4a = ...                    # the smaller root, in degrees, 3 s.f.
q5_4b = ...                    # the larger

check_num('5.4a', q5_4a, 3, 'D_54A')
check_num('5.4b', q5_4b, 3, 'D_54B')
""".replace("'D_54A'", repr(D_54A)).replace("'D_54B'", repr(D_54B)))

md(r"""
### 5.5 · May 2021 TZ1, Paper 1, Q5(a) · 2 marks · no calculator

Show that $\sin 2x+\cos 2x-1=2\sin x(\cos x-\sin x)$.
""")

code(r"""
q5_5 = ...                     # the left-hand side with both double angles opened

verify_identity('5.5', q5_5, sin(2*x) + cos(2*x) - 1)
""")

md(r"""
### 5.6 · May 2021 TZ1, Paper 3, Q2(c) · 2 marks · calculator

An $n$-sided regular polygon can be divided into $n$ congruent isosceles
triangles. Let $a$ be the length of each of the two equal sides of one such
triangle and let $y$ be the length of the third side. The included angle
between the two equal sides has magnitude $\dfrac{2\pi}{n}$.

Show that $y=2a\sin\dfrac{\pi}{n}$.

*(The paper calls the equal side $x$; here it is $a$, because $x$ is taken.)*
""")

code(r"""
q5_6 = ...                     # y**2 from the cosine rule, before you simplify

verify_identity('5.6', q5_6, (2*a*sin(pi/n))**2, var=n)
""")

md(r"""
### 5.7 · May 2021 TZ1, Paper 3, Q2(d) · 7 marks · calculator

The area of one of those isosceles triangles is
$A_T=\dfrac{1}{2}a^{2}\sin\dfrac{2\pi}{n}$.

Consider an $n$-sided regular polygon whose area and perimeter have the same
numerical value. Use the results above to show that this common value is
$4n\tan\dfrac{\pi}{n}$.
""")

code(r"""
# area = perimeter means n*A_T = n*y, which fixes the side length
q5_7 = ...                     # a, in terms of n

check_series('5.7', q5_7, 'D_57', var=n)
""".replace("'D_57'", repr(D_57)))

# ----------------------------------------------------------------- section 6
md(r"""
---
## 6 · Factorise — never divide

*Both sides share a factor, or the equation can be pushed into $A\cdot B=0$.*
Move everything to one side, take the common factor out **without cancelling
it**, and then solve both brackets. **3 questions, 16 marks.**

Divide by $\cos x$ instead and you lose every root where $\cos x=0$ — a whole
series of solutions, and the most expensive mistake in the topic. In 6.2 the
paper hands you the lost root as a labelled point, which is exactly how
examiners hint that you were about to drop it.
""")

md(r"""
### 6.1 · May 2021 TZ1, Paper 1, Q5(b) · 6 marks · no calculator

Hence or otherwise, solve
$\sin 2x+\cos 2x-1+\cos x-\sin x=0$ for $0<x<2\pi$.

*(Part (a) is 5.5: $\sin 2x+\cos 2x-1=2\sin x(\cos x-\sin x)$.)*
""")

code(r"""
q6_1 = [...]

verify_roots('6.1', q6_1, sin(2*x) + cos(2*x) - 1 + cos(x) - sin(x), (0, 2*pi))
""")

md(r"""
### 6.2 · May 2024 TZ1, Paper 1, Q4(a) · 3 marks · no calculator

Consider the functions $f(x)=\cos x$ and $g(x)=\sin 2x$, where
$0\le x\le\pi$.

The graph of $f$ intersects the graph of $g$ at the point A, at the point
$\text{B}\left(\dfrac{\pi}{2},0\right)$ and at the point C.

Find the $x$-coordinate of A and the $x$-coordinate of C.
""")

code(r"""
q6_2 = [...]                   # all three, B included — see how it survives

verify_roots('6.2', q6_2, cos(x) - sin(2*x), (0, pi))
""")

md(r"""
### 6.3 · November 2023, Paper 1, Q12(c) · 7 marks · no calculator

It has been shown that
$\sin 5\theta\equiv 16\sin^{5}\theta-20\sin^{3}\theta+5\sin\theta$.

**(i)** Hence, show that $\theta=\dfrac{\pi}{5}$ and $\theta=\dfrac{3\pi}{5}$
are solutions of the equation $16\sin^{4}\theta-20\sin^{2}\theta+5=0$.

**(ii)** Hence, show that
$\sin\dfrac{\pi}{5}\sin\dfrac{3\pi}{5}=\dfrac{\sqrt{5}}{4}$.
""")

code(r"""
q6_3a = ...                    # sin(5t) with the common factor taken out
q6_3b = [...]                  # the two values of sin(t)**2 that the bracket gives

verify_identity('6.3a', q6_3a, sin(5*t), var=t)
verify_roots('6.3b', q6_3b, 16*x**2 - 20*x + 5, (0, 1))
""")

# ----------------------------------------------------------------- section 7
md(r"""
---
## 7 · Reduce it to a tangent

*$\sin$ and $\cos$ enter to the same degree — the equation is homogeneous in
them.* Divide through by $\cos x$ to that degree, check separately whether
$\cos x=0$ is a solution, and solve for $\tan x$. **2 questions, 10 marks.**

Two things to hold on to. The tangent gives **one** root per period $\pi$,
not two. And $\tan^{2}x=k$ has two square roots, so taking only the positive
one loses a whole series.
""")

md(r"""
### 7.1 · May 2022 TZ1, Paper 1, Q3(b) · 5 marks · no calculator

Consider the functions $f(x)=\sqrt{3}\sin x+\cos x$, where $0\le x\le\pi$,
and $g(x)=2x$, where $x\in\mathbb{R}$.

Solve the equation $(f\circ g)(x)=2\cos 2x$, where $0\le x\le\pi$.
""")

code(r"""
q7_1 = [...]

verify_roots('7.1', q7_1, sqrt(3)*sin(2*x) + cos(2*x) - 2*cos(2*x), (0, pi))
""")

md(r"""
### 7.2 · November 2022, Paper 1, Q10(a) · 5 marks · no calculator

The function $f$ is defined by $f(x)=\cos^{2}x-3\sin^{2}x$, $0\le x\le\pi$.

Find the roots of the equation $f(x)=0$.
""")

code(r"""
q7_2 = [...]

verify_roots('7.2', q7_2, cos(x)**2 - 3*sin(x)**2, (0, pi))
""")

# ----------------------------------------------------------------- section 8
md(r"""
---
## 8 · Choosing which roots survive

*There is a clause: $\theta\ne\pi/4$, a denominator, a square root, an inverse
function, or the words "the least positive".* The sign of this technique is
that solving the equation is not the end of the work. **4 questions, 19
marks.**

Write every restriction down before you start. A fraction is zero where its
numerator is zero **and its denominator is not**. Squaring manufactures roots
that were never there, so substitute back. And $\arcsin$ and $\arccos$ only
accept arguments in $[-1,1]$, which quietly narrows what $x$ may be.
""")

md(r"""
### 8.1 · November 2021, Paper 1, Q6(b) · 5 marks · no calculator

It has been shown that
$2x-3-\dfrac{6}{x-1}=\dfrac{2x^{2}-5x-3}{x-1}$, $x\in\mathbb{R}$, $x\ne 1$.

Hence or otherwise, solve the equation

$$2\sin 2\theta-3-\frac{6}{\sin 2\theta-1}=0
\quad\text{for } 0\le\theta\le\pi,\ \theta\ne\frac{\pi}{4}.$$
""")

code(r"""
q8_1 = [...]                   # theta is x here

verify_roots('8.1', q8_1, 2*sin(2*x) - 3 - 6/(sin(2*x) - 1), (0, pi))
""")

md(r"""
### 8.2 · November 2022, Paper 1, Q10(d) · 4 marks · no calculator

With $f(x)=\cos^{2}x-3\sin^{2}x$ on $0\le x\le\pi$ as in 7.2, solve the
inequality $|f(x)|>1$.
""")

code(r"""
q8_2 = ...                     # an interval, or an inequality in x

# |f| > 1 is the same as f**2 > 1, which is a form sympy can solve itself
verify_solution_set('8.2', q8_2, (cos(x)**2 - 3*sin(x)**2)**2 > 1,
                    domain=Interval(0, pi))
""")

md(r"""
### 8.3 · May 2025 TZ2, Paper 1, Q8(b) · 6 marks · no calculator

Solve $\arccos(x)+\arccos\!\left(x\sqrt{3}\right)=\dfrac{3\pi}{2}$, for
$-\dfrac{1}{\sqrt{3}}\le x\le\dfrac{1}{\sqrt{3}}$.
""")

code(r"""
q8_3 = [...]                   # every x that survives, and only those

verify_roots('8.3', q8_3, acos(x) + acos(x*sqrt(3)) - 3*pi/2,
             (-1/sqrt(3), 1/sqrt(3)))
""")

md(r"""
### 8.4 · May 2023 TZ2, Paper 1, Q9(c) · 4 marks · no calculator

OABC is a parallelogram with $\overrightarrow{\text{OA}}=\boldsymbol{a}$,
$\overrightarrow{\text{OC}}=\boldsymbol{c}$ and
$|\boldsymbol{c}|=2|\boldsymbol{a}|$, where $|\boldsymbol{a}|\ne 0$. The
angle between $\overrightarrow{\text{OA}}$ and $\overrightarrow{\text{OC}}$
is $\theta$, where $0<\theta<\pi$.

M lies on [AB] with $\overrightarrow{\text{AM}}=k\,\overrightarrow{\text{AB}}$,
where $0\le k\le 1$, and it has been shown that

$$|\boldsymbol{a}|^{2}(1-2k)\bigl(2\cos\theta-(1-2k)\bigr)=0.$$

Find the range of values for $\theta$ such that there are two possible
positions for M.
""")

code(r"""
# how many k in [0, 1] satisfy (1 - 2k)(2cos(theta) - (1 - 2k)) = 0
def positions(theta):
    roots = {round(float(v), 9) for v in (Rational(1, 2),
                                          Rational(1, 2) - cos(theta))}
    return len([r for r in roots if 0 <= r <= 1])


q8_4 = ...                     # theta is t here; an interval, or an inequality

verify_param_set('8.4', q8_4, lambda v: positions(v) == 2, var=t, window=(0, pi))
""")

# ----------------------------------------------------------------- section 9
md(r"""
---
## 9 · Solving numerically

*The numbers do not land on the unit circle, the paper allows a calculator,
and the answer is wanted to three significant figures.* **5 questions, 10
marks — the entire GDC content of the topic.**

The technique is the calculator, so the marks are elsewhere: in the interval
(how many roots are on it, and is the one you found the one that was asked
for), in the mode (radians, not degrees), and in rounding only at the end.
""")

md(r"""
### 9.1 · November 2021, Paper 2, Q4(b) · 1 mark · calculator

A semicircle has centre O and radius $r$; P, Q and R lie on the circle with
$\text{PQ}=2r$ and $\text{R}\hat{\text{O}}\text{Q}=\theta$, where
$0<\theta<\pi$. The two shaded regions have equal areas, which gives
$\theta=2\sin\theta$.

Hence determine the value of $\theta$.
""")

code(r"""
q9_1 = ...                     # three significant figures, radians

check_num('9.1', q9_1, 3, 'D_91')
""".replace("'D_91'", repr(D_91)))

md(r"""
### 9.2 · May 2022 TZ2, Paper 2, Q5(a) · 2 marks · calculator

A particle moves in a straight line such that its velocity, $v\ \text{m s}^{-1}$,
at time $t$ seconds is given by
$v=\dfrac{(t^{2}+1)\cos t}{4}$, $0\le t\le 3$.

Determine when the particle changes its direction of motion.
""")

code(r"""
q9_2 = [...]                   # every such time in the interval

verify_roots('9.2', q9_2, (t**2 + 1)*cos(t)/4, (0, 3), var=t)
""")

md(r"""
### 9.3 · May 2023 TZ2, Paper 2, Q5(b) · 2 marks · calculator

A particle moves in a straight line with velocity
$v(t)=4\mathrm{e}^{-t/3}\cos\!\left(\dfrac{t}{2}-\dfrac{\pi}{4}\right)$,
for $0\le t\le 4\pi$.

Let $t_2$ be the **second** time when the particle is instantaneously at
rest. Find the value of $t_2$.
""")

code(r"""
q9_3 = [...]                   # both times it is at rest; the second one is t2

verify_roots('9.3', q9_3, 4*exp(-t/3)*cos(t/2 - pi/4), (0, 4*pi), var=t)
""")

md(r"""
### 9.4 · May 2023 TZ2, Paper 2, Q10(d) · 2 marks · calculator

A weight on a spring moves up and down. The height, $H$ metres, of its base
above the ground is modelled by $H(t)=a\cos(7.8t)+b$, for $0\le t\le 10$.
Its minimum height is 1 metre and its maximum height is 1.8 metres, so
$a=-0.4$ and $b=1.4$.

Find the first time that the base of the weight reaches a height of 1.5
metres.
""")

code(r"""
q9_4 = ...                     # seconds, three significant figures

check_num('9.4', q9_4, 3, 'D_94')
""".replace("'D_94'", repr(D_94)))

md(r"""
### 9.5 · May 2025 TZ1, Paper 2, Q5(b) · 3 marks · calculator

Consider the function $h(x)=15\cos\!\left(\dfrac{\pi x}{50}\right)+15$, where
$0\le x\le 50$. The tangent $T_k$ to the curve $y=h(x)$ at the point
$(k,h(k))$ has gradient
$h'(k)=-\dfrac{15\pi}{50}\sin\!\left(\dfrac{\pi k}{50}\right)$.

The angle between $T_k$ and the $x$-axis is $\dfrac{\pi}{8}$ radians. Find
the possible values of $k$.
""")

code(r"""
q9_5a = ...                    # the smaller value, 3 s.f.
q9_5b = ...                    # the larger

check_num('9.5a', q9_5a, 3, 'D_95A')
check_num('9.5b', q9_5b, 3, 'D_95B')
""".replace("'D_95A'", repr(D_95A)).replace("'D_95B'", repr(D_95B)))

# ------------------------------------------------------------------ solutions
md(r"""
---
---
# Solutions

Numbered as above. The **route** is the shortest way through; the
**markscheme note** is where the marks actually moved.
""")

md(r"""
## 1 · The unit circle

**1.1** $x=\pi$ and $x=3\pi$.

Route: touching the axis means $6+6\cos x=0$, so $\cos x=-1$. On one turn that
is $x=\pi$; the interval runs to $4\pi$, which is two turns, so the next one is
$x=\pi+2\pi=3\pi$.

Markscheme note: `(M1)` for setting $f(x)=0$ (or $f'(x)=0$), then `A1A1` — one
mark for each root. Stopping at $x=\pi$ collects two marks out of three.

**1.2** $f(-x)=\dfrac{\sin^{2}(-kx)}{(-x)^{2}}
=\dfrac{(-\sin kx)^{2}}{x^{2}}=\dfrac{\sin^{2}(kx)}{x^{2}}=f(x)$.

Route: the whole question is $\sin(-\theta)=-\sin\theta$ followed by the square
killing the sign, and $(-x)^{2}=x^{2}$.

Markscheme note: both marks are for **showing** the two sign changes and
concluding $f(-x)=f(x)$. Writing "the square makes it even" without the
substitution is not a proof.
""")

md(r"""
## 2 · A compound argument

**2.1** $x=25^\circ$ and $x=115^\circ$.

Route: $\arctan 1=45^\circ$. The argument $2x-5^\circ$ runs over
$[-5^\circ,355^\circ]$ as $x$ runs over $[0^\circ,180^\circ]$, so it takes the
value $45^\circ$ and also $45^\circ+180^\circ=225^\circ$. Then
$2x=50^\circ,230^\circ$.

Markscheme note: **"do not accept $2x-5^\circ=1$"** — the reference angle has to
appear. And the final `A1` is lost if any extra solution is listed, so the
$405^\circ$ branch has to be discarded before you write the answer down.

**2.2** $x=\dfrac{17\pi}{6}$.

Route: reference angle $\pi/4$. Setting $\tfrac{x}{2}+\tfrac{\pi}{3}=\tfrac{\pi}{4}$
gives a negative $x$, so it is rejected; the next one is
$\tfrac{x}{2}+\tfrac{\pi}{3}=2\pi-\tfrac{\pi}{4}=\tfrac{7\pi}{4}$, so
$\tfrac{x}{2}=\tfrac{17\pi}{12}$.

Markscheme note: there is an explicit `R1` for saying that the first candidate
is rejected **because it is negative**. Silently skipping to the second branch
loses it. And the answer must be in radians.
""")

md(r"""
## 3 · The compound angle formulas

**3.1** Put $A=\arctan p$, $B=\arctan q$, so $\tan A=p$ and $\tan B=q$. Then

$$\tan(A+B)=\frac{\tan A+\tan B}{1-\tan A\tan B}=\frac{p+q}{1-pq},$$

so $A+B=\arctan\!\left(\dfrac{p+q}{1-pq}\right)$, which is the statement.

Markscheme note: `M1` for naming the two angles, `A1` for the formula, `A1` for
taking $\arctan$ back. The condition $pq<1$ is what keeps $A+B$ inside
$(-\tfrac{\pi}{2},\tfrac{\pi}{2})$ so that the last step is legal — that is why
it is in the question.

**3.2** By 3.1 with $p=\dfrac{x}{x+1}$ and $q=1$ (because $\tfrac{\pi}{4}=\arctan 1$):

$$\arctan\frac{x}{x+1}+\arctan 1
=\arctan\frac{\frac{x}{x+1}+1}{1-\frac{x}{x+1}}
=\arctan\frac{2x+1}{1}=\arctan(2x+1).$$

Markscheme note: the first `A1` is for writing $\tfrac{\pi}{4}$ as $\arctan 1$ —
the whole question turns on it.

**3.3** $\sin 75^\circ=\sin(45^\circ+30^\circ)
=\sin 45^\circ\cos 30^\circ+\cos 45^\circ\sin 30^\circ
=\dfrac{\sqrt2}{2}\cdot\dfrac{\sqrt3}{2}+\dfrac{\sqrt2}{2}\cdot\dfrac{1}{2}
=\dfrac{\sqrt6+\sqrt2}{4}$.

Markscheme note: $75^\circ$ has to be split into two angles that are **on the
unit circle**. $75=90-15$ leads nowhere.

**3.4** $\sin 3\theta=\sin(2\theta+\theta)=\sin 2\theta\cos\theta+\cos 2\theta\sin\theta
=2\sin\theta\cos^{2}\theta+(1-2\sin^{2}\theta)\sin\theta$, and
$\cos^{2}\theta=1-\sin^{2}\theta$ turns that into
$2\sin\theta-2\sin^{3}\theta+\sin\theta-2\sin^{3}\theta=3\sin\theta-4\sin^{3}\theta$.

Markscheme note: `M1` angle sum, `M1` a double angle **or** the Pythagorean
identity, and two `A1`s along the way. De Moivre gets the same four marks —
but this is not a complex numbers question, and the angle sum is shorter.

**3.5** With $\tan\dfrac{\pi}{4}=1$ and $f=-\dfrac{x}{y}$:

$$g=\frac{-\frac{x}{y}+1}{1-\left(-\frac{x}{y}\right)}
=\frac{\frac{y-x}{y}}{\frac{y+x}{y}}=\frac{y-x}{y+x}.$$

Markscheme note: `A1` for the substitution and `A1` for clearing the compound
fraction. Two marks for two lines of algebra — this is the cheapest identity
in the archive.
""")

md(r"""
## 4 · The Pythagorean identity

**4.1** $x=\dfrac{\pi}{6},\ \dfrac{5\pi}{6}$.

Route: $\cos^{2}x=1-\sin^{2}x$ turns it into $2\sin^{2}x-5\sin x+2=0$, i.e.
$(2\sin x-1)(\sin x-2)=0$. Reject $\sin x=2$, keep $\sin x=\tfrac12$.

Markscheme note: seven marks for two lines of algebra and two roots, which
tells you where they are: `M1` for the substitution, `A1` for the quadratic,
`M1A1` for solving it, `(A1)` for $\sin x=\tfrac12$, `A1A1` for the two angles.
Every step is paid for separately, so write them all down.

**4.2** $\cot\theta=-\dfrac{\sqrt5}{2}$.

Route: $1+\cot^{2}\theta=\operatorname{cosec}^{2}\theta=\tfrac94$, so
$\cot^{2}\theta=\tfrac54$ and $\cot\theta=\pm\tfrac{\sqrt5}{2}$. Now the
quadrant: $\operatorname{cosec}\theta>0$ means $\sin\theta>0$, and with
$\tfrac{\pi}{2}<\theta<\tfrac{3\pi}{2}$ that puts $\theta$ in the second
quadrant, where the cotangent is negative.

Markscheme note: there is a standalone `R1` for that sentence. Writing
$+\tfrac{\sqrt5}{2}$ as the final answer scores `M1A1R0A0` — half the question
is the sign.

**4.3** The curves meet where $\cos k=\tan k=\dfrac{\sin k}{\cos k}$.
Multiplying by $\cos k$ (which is not zero, since $0<k<\tfrac{\pi}{2}$) gives
$\cos^{2}k=\sin k$.

Markscheme note: one mark, one line — but the line has to be there.

**4.4** $\sin k=\dfrac{-1+\sqrt5}{2}$.

Route: put $\cos^{2}k=1-\sin^{2}k$ into part (a): $1-\sin^{2}k=\sin k$, so
$\sin^{2}k+\sin k-1=0$ and $\sin k=\dfrac{-1\pm\sqrt5}{2}$. On
$0<k<\tfrac{\pi}{2}$ the sine is positive, so only the $+$ root survives.

Markscheme note: **`A0` if both roots are given.** Choosing between them is the
mark; $\tfrac{-1-\sqrt5}{2}\approx-1.62$ is not even a possible sine.

**4.5** $f(\alpha)=\dfrac{29\sqrt5}{15}=4.32$.

Route: $\sec\alpha=1.5$ means $\cos\alpha=\tfrac23$, so
$\alpha=\arccos\tfrac23=0.841\ldots$ (the positive cosine puts it in the first
quadrant, which $0<\alpha<\pi$ allows). Then evaluate
$f(\alpha)=4\cot\alpha+\sin\alpha$.

Markscheme note: `M1` is for recognising $\sec x=\tfrac{1}{\cos x}$ — everything
else is the calculator. Exact or three significant figures both score.
""")

md(r"""
## 5 · The double angle

**5.1** $x=-\dfrac{\pi}{2},\ \dfrac{\pi}{6},\ \dfrac{5\pi}{6}$.

Route: $\sin x$ is present, so use $\cos 2x=1-2\sin^{2}x$:
$2\sin^{2}x+\sin x-1=0$, i.e. $(2\sin x-1)(\sin x+1)=0$. Then $\sin x=\tfrac12$
gives $\tfrac{\pi}{6},\tfrac{5\pi}{6}$ and $\sin x=-1$ gives $-\tfrac{\pi}{2}$.

Markscheme note: `A0` if extra values are given, and **no marks at all for a
final value with no working** — this is a Paper 1 question, and three roots
written down bare are worth nothing.

**5.2** $\theta=\dfrac{3\pi}{2}$.

Route: $\cos\theta$ is present, so $\cos 2\theta=2\cos^{2}\theta-1$:
$4\cos^{2}\theta-5\cos\theta=0$, i.e. $\cos\theta(4\cos\theta-5)=0$. The second
bracket gives $\cos\theta=\tfrac54$, impossible. So $\cos\theta=0$, and on
$[\pi,2\pi]$ that is $\tfrac{3\pi}{2}$ alone.

Markscheme note: `A0` if any extra solution is given. $\tfrac{\pi}{2}$ is
outside the interval, and adding it costs the last mark.

**5.3** $3\cos 2x+11\sin x=3(1-2\sin^{2}x)+11\sin x=3-6\sin^{2}x+11\sin x$.

Markscheme note: the `M1` is awarded only if the double angle formula is
**used**, not merely quoted. And of the three forms of $\cos 2x$, only
$1-2\sin^{2}x$ leaves an expression in $\sin x$ alone.

**5.4** $x=19.5^\circ$ and $x=161^\circ$.

Route: from 5.3 the equation is $-6\sin^{2}x+11\sin x-3=0$, so
$\sin x=\tfrac13$ (the other root, $\tfrac32$, is impossible). On
$[0^\circ,180^\circ]$: $x=19.47\ldots$ and $180-19.47=160.5\ldots$

Markscheme note: a graph on the GDC scores the same `M1A1A1`. Rounding
$160.528$ to $161$, not $160$, is worth a mark on its own.

**5.5** $\sin 2x+\cos 2x-1=2\sin x\cos x+(1-2\sin^{2}x)-1
=2\sin x\cos x-2\sin^{2}x=2\sin x(\cos x-\sin x)$.

Markscheme note: the markscheme prints a warning — **do not award the final
`A1` for proofs that work from both sides to any common expression other than
$2\sin x\cos x-2\sin^{2}x$.** Meeting in the middle at a different point is not
accepted.

**5.6** By the cosine rule in the isosceles triangle,

$$y^{2}=a^{2}+a^{2}-2a^{2}\cos\frac{2\pi}{n}=2a^{2}\left(1-\cos\frac{2\pi}{n}\right)
=2a^{2}\cdot 2\sin^{2}\frac{\pi}{n}=4a^{2}\sin^{2}\frac{\pi}{n},$$

so $y=2a\sin\dfrac{\pi}{n}$.

Route: the double angle read backwards — $1-\cos 2A=2\sin^{2}A$. Dropping the
perpendicular from the apex works too, and is one line shorter.

**5.7** $A=P=4n\tan\dfrac{\pi}{n}$.

Route: $A=n\cdot\tfrac12a^{2}\sin\tfrac{2\pi}{n}$ and $P=n\cdot 2a\sin\tfrac{\pi}{n}$.
Setting them equal and using $\sin\tfrac{2\pi}{n}=2\sin\tfrac{\pi}{n}\cos\tfrac{\pi}{n}$:

$$a^{2}\sin\frac{\pi}{n}\cos\frac{\pi}{n}=2a\sin\frac{\pi}{n}
\ \Longrightarrow\ a\cos\frac{\pi}{n}=2\ \Longrightarrow\ a=\frac{2}{\cos\frac{\pi}{n}}.$$

Then $P=2na\sin\tfrac{\pi}{n}=4n\tan\tfrac{\pi}{n}$.

Markscheme note: seven marks, and most of them are for the cancellation — the
$\sin\tfrac{\pi}{n}$ and one $a$ come off both sides, which is legal because
neither is zero for $n\ge 3$.
""")

md(r"""
## 6 · Factorise — never divide

**6.1** $x=\dfrac{\pi}{4},\ \dfrac{7\pi}{6},\ \dfrac{5\pi}{4},\ \dfrac{11\pi}{6}$.

Route: by 5.5 the equation is
$2\sin x(\cos x-\sin x)+(\cos x-\sin x)=0$, so
$(\cos x-\sin x)(2\sin x+1)=0$. The first bracket gives $\tan x=1$, hence
$\tfrac{\pi}{4},\tfrac{5\pi}{4}$; the second gives $\sin x=-\tfrac12$, hence
$\tfrac{7\pi}{6},\tfrac{11\pi}{6}$.

Markscheme note: `A2` for all four roots, `A1` for any two of them, `A1A0` if
extra values appear alongside the four, and `A1A0` for the four correct
answers **in degrees**. The interval is in radians, so the answer is too.

**6.2** A is at $x=\dfrac{\pi}{6}$ and C is at $x=\dfrac{5\pi}{6}$; the third
intersection is B at $x=\dfrac{\pi}{2}$.

Route: $\cos x=2\sin x\cos x$. Move everything over:
$\cos x(1-2\sin x)=0$. The factor $\cos x=0$ is B — the point the question
hands you. The other bracket gives $\sin x=\tfrac12$.

Markscheme note: the markscheme divides by $\cos x$ and writes
"$(\cos x\ne 0)$" as it does so, which it can only do because B has been
excluded in the question. In any other question that division loses a root.

**6.3** **(i)** $\sin 5\theta=\sin\theta\,(16\sin^{4}\theta-20\sin^{2}\theta+5)$.
At $\theta=\tfrac{\pi}{5}$ and $\theta=\tfrac{3\pi}{5}$ the left side is
$\sin\pi=0$ and $\sin 3\pi=0$, while $\sin\theta\ne 0$ at both. So the bracket
is zero at both, which is the statement.

**(ii)** From the bracket, $\sin^{2}\theta=\dfrac{20\pm\sqrt{80}}{32}
=\dfrac{5\pm\sqrt5}{8}$, and those two values belong to the two angles. Hence

$$\sin\frac{\pi}{5}\sin\frac{3\pi}{5}
=\sqrt{\frac{5+\sqrt5}{8}\cdot\frac{5-\sqrt5}{8}}
=\sqrt{\frac{20}{64}}=\frac{\sqrt5}{4}.$$

Markscheme note: the final `R1` in (i) is dependent on both earlier marks and
is awarded only for saying that $\sin\tfrac{\pi}{5}$ and $\sin\tfrac{3\pi}{5}$
are **not** zero. Without that sentence the factorisation proves nothing.
""")

md(r"""
## 7 · Reduce it to a tangent

**7.1** $x=\dfrac{\pi}{12},\ \dfrac{7\pi}{12}$.

Route: $(f\circ g)(x)=\sqrt3\sin 2x+\cos 2x$, so the equation is
$\sqrt3\sin 2x=\cos 2x$, i.e. $\tan 2x=\dfrac{1}{\sqrt3}$. The argument $2x$
runs over $[0,2\pi]$, so $2x=\tfrac{\pi}{6}$ and $2x=\tfrac{7\pi}{6}$.

Markscheme note: `M1` is for recognising that a tangent (or a cotangent) is
what to form. Degrees cost one mark; degrees plus extra values cost both.

**7.2** $x=\dfrac{\pi}{6},\ \dfrac{5\pi}{6}$.

Route: $\cos^{2}x=3\sin^{2}x$ is homogeneous of degree two, so divide by
$\cos^{2}x$: $\tan^{2}x=\tfrac13$, hence $\tan x=\pm\dfrac{1}{\sqrt3}$. The
minus sign is the second root, in the second quadrant.

Markscheme note: **omitting the $\pm$ and giving only $\tfrac{\pi}{6}$ scores
`M1A1A0A1A0` — two marks lost.** Both signs, or the equivalent
$\cos 2x=\tfrac12$ route with $2x=\tfrac{\pi}{3},\tfrac{5\pi}{3}$.
""")

md(r"""
## 8 · Choosing which roots survive

**8.1** $\theta=\dfrac{7\pi}{12},\ \dfrac{11\pi}{12}$.

Route: by part (a) with $x=\sin 2\theta$, the equation is
$\dfrac{2\sin^{2}2\theta-5\sin 2\theta-3}{\sin 2\theta-1}=0$, so the numerator
must vanish: $(2\sin 2\theta+1)(\sin 2\theta-3)=0$. Reject $\sin 2\theta=3$.
From $\sin 2\theta=-\tfrac12$ with $2\theta\in[0,2\pi]$:
$2\theta=\tfrac{7\pi}{6},\tfrac{11\pi}{6}$.

Markscheme note: `A1` is for $\sin 2\theta=-\tfrac12$ **only** — the rejected
root earns nothing. The excluded $\theta\ne\tfrac{\pi}{4}$ is where the
denominator vanishes, and it is in the question because the numerator does
not vanish there.

**8.2** $\dfrac{\pi}{4}<x<\dfrac{3\pi}{4}$.

Route: $f(x)=\cos^{2}x-3\sin^{2}x=1-4\sin^{2}x$, which starts at $1$, falls to
$-3$ at $x=\tfrac{\pi}{2}$ and comes back to $1$. So $|f|>1$ needs $f<-1$:
$1-4\sin^{2}x<-1$, i.e. $\sin^{2}x>\tfrac12$.

Markscheme note: the markscheme finds the boundary by solving $|f(x)|=1$,
which gives $\tan^{2}x=1$ and $x=\tfrac{\pi}{4},\tfrac{3\pi}{4}$, and then
reads the direction off the graph from part (c). The endpoints are excluded
because the inequality is strict.

**8.3** $x=-\dfrac{1}{2}$.

Route: take the sine of both sides. With $A=\arccos x$, $B=\arccos(x\sqrt3)$
and $\sin\tfrac{3\pi}{2}=-1$:

$$\sqrt{1-x^{2}}\cdot x\sqrt3+x\cdot\sqrt{1-3x^{2}}=-1.$$

Squaring to clear the roots gives $16x^{4}-8x^{2}+1=0$, i.e. $(4x^{2}-1)^{2}=0$,
so $x=\pm\tfrac12$. Substituting back: at $x=\tfrac12$ the two arccosines add
to less than $\pi$, so it is extraneous. Only $x=-\tfrac12$ survives.

Markscheme note: squaring is what creates the false root, and rejecting it is
the last `A1`. Check both candidates in the original equation — the graph in
part (a) is enough to see which one fails.

**8.4** $\dfrac{\pi}{3}\le\theta\le\dfrac{2\pi}{3}$, $\theta\ne\dfrac{\pi}{2}$.

Route: the product is zero when $k=\tfrac12$ or $1-2k=2\cos\theta$, i.e.
$k=\tfrac12-\cos\theta$. Two positions for M means two different $k$ in
$[0,1]$, so $0\le\tfrac12-\cos\theta\le 1$, which is
$-\tfrac12\le\cos\theta\le\tfrac12$, and the two values must differ, so
$\cos\theta\ne 0$.

Markscheme note: `A1` for the cosine inequality, `A1A1` for converting it to
$\theta$ **and** for the exclusion. The excluded point is worth as much as the
interval: at $\theta=\tfrac{\pi}{2}$ the two values of $k$ collide at $\tfrac12$
and M has only one position.
""")

md(r"""
## 9 · Solving numerically

**9.1** $\theta=1.90$.

Route: solve $\theta-2\sin\theta=0$ on $0<\theta<\pi$. The calculator gives
$1.89549\ldots$

Markscheme note: **`A0` if more than one solution is given** — $\theta=0$ is a
root of the equation but is excluded by $0<\theta<\pi$, and it is exactly what
an unguarded solver returns first. `A0` for degrees.

**9.2** $t=1.57$ $\left(=\dfrac{\pi}{2}\right)$ seconds.

Route: the direction changes where $v=0$. Since $t^{2}+1>0$, that is
$\cos t=0$, and the only such $t$ in $[0,3]$ is $\tfrac{\pi}{2}$.

Markscheme note: `M1` is for recognising that $v=0$ is the condition — half
the marks are for reading the word "direction" correctly.

**9.3** $t_2=11.0$ $\left(=\dfrac{7\pi}{2}\right)$ seconds.

Route: $v=0$ where $\cos\!\left(\tfrac{t}{2}-\tfrac{\pi}{4}\right)=0$, so
$\tfrac{t}{2}-\tfrac{\pi}{4}=\tfrac{\pi}{2}+m\pi$ and $t=\tfrac{3\pi}{2}+2m\pi$.
On $[0,4\pi]$ that is $4.712\ldots$ and $10.995\ldots$; the second one is
$t_2$.

Markscheme note: the exponential never vanishes, so it plays no part. The mark
is for taking the **second** root and not the first — sketch the graph, which
the markscheme explicitly accepts as the working.

**9.4** $t=0.234$ seconds.

Route: solve $-0.4\cos(7.8t)+1.4=1.5$, i.e. $\cos(7.8t)=-0.25$. The first
positive solution is $t=\dfrac{\arccos(-0.25)}{7.8}=0.2337\ldots$

Markscheme note: "first time" is the whole question — the period is
$\tfrac{2\pi}{7.8}\approx0.8$ s, so there are a dozen later answers on
$0\le t\le 10$ and only the smallest one scores.

**9.5** $k=7.24$ and $k=42.8$.

Route: an angle of $\tfrac{\pi}{8}$ with the $x$-axis means the gradient is
$\pm\tan\tfrac{\pi}{8}$, and here the curve is falling, so
$h'(k)=-\tan\tfrac{\pi}{8}=-0.4142\ldots$ Solving
$-\tfrac{15\pi}{50}\sin\!\left(\tfrac{\pi k}{50}\right)=-0.4142$ on $[0,50]$
gives two values, one on each side of the steepest point.

Markscheme note: `M1` for the $-\tan\tfrac{\pi}{8}$ (or, equivalently,
$\tan\tfrac{7\pi}{8}$), and the single `A1` needs **both** values. The sine is
symmetric about $x=25$, which is why there are exactly two.
""")

md(r"""
---

## What to do when it goes wrong

* **A root satisfies the equation but the check says the set is incomplete.**
  You solved for the argument and forgot that it runs over a wider interval
  than $x$ does, or you took only one square root, or you divided by a factor
  that could be zero.
* **Extra roots.** Look for a squaring step, a denominator, or an interval
  boundary. Every extra value costs a mark even when the rest are right.
* **"this is a decimal, and the question asks for the exact value."** Paper 1
  answers are surds and fractions of $\pi$; the calculator is for checking the
  size of what you already have.
* **Everything right, one mark gone.** It is usually degrees where radians
  were asked, or a rejected root that was never said out loud to be rejected.
""")

if __name__ == '__main__':
    out = NOTEBOOK
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    with open(out, 'w') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)
        f.write('\n')
    codes = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f'{out}: {len(cells)} ячеек, из них с кодом {codes}')
