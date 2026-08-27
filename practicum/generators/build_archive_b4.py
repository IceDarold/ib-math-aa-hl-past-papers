"""Собирает архивный ноутбук B4: весь корпус темы, по приёмам, подряд.

Пробный формат для веба. Практикум B4 учит: лестница, теория, три уровня
сложности, тренажёр, задание на время. Этот ноутбук не учит — он даёт
набивать руку. Внутри вся тема из архива, 54 вопроса и 127 баллов,
разложенные по девяти приёмам карточки functions-curve-sketching.yaml, и
ничего кроме них: вопрос, ячейка для ответа с мгновенной проверкой, и
разбор в конце.

Почему 54, а не 62. Ноябрь 2023 лежит в корпусе двумя зональными копиями
одной бумаги (это установлено в B2 и измерено в B4: 20 баллов из 147).
Здесь дубли сведены, и остаётся ровно то, что на самом деле спрашивали:
127 баллов.

Ответы не хранятся: почти каждая проверка спрашивает у самой функции —
verify_asymptotes считает предел, verify_sketch пересчитывает особенности,
verify_range проверяет достижимость, verify_param_set опрашивает семейство.
Хеш нужен только там, где ответ — число из markscheme, которое неоткуда
вывести проверкой (вторая производная в приёме 7, наклон ветви в приёме 8).

ANSWERS хранит эталонный ответ для каждой ячейки. Он не попадает в
ноутбук — по нему practicum/tests/check_archive_b4.py прогоняет весь
ноутбук с заполненными ответами и требует, чтобы каждая проверка сказала
✅. Это и есть проверка того, что разбор в конце и код в ячейках согласны.
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
x, y = sp.symbols('x y')


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(expr)))


def dset(values):
    return digest('|'.join(sorted(sp.srepr(sp.simplify(val)) for val in values)))


# --- хеши для тех немногих ответов, что не выводятся из самой функции ---
D_54 = de(sp.Eq(x, -5))                 # ось симметрии x^2/2 + 5x + 13
D_71A = de(-4 * sp.E)                   # f''(0) у e^(cos 2x)
D_71B = de(4 / sp.E)                    # f''(pi/2)
D_71C = de(sp.E**2)                     # во сколько раз максимум острее минимума
D_81 = dn(0)                            # наклон верхней ветви y^2 = x^3 в нуле
D_83 = de(sp.oo)                        # и у y^2 = x^3 + 1 в её x-пересечении
D_82 = dset([-1, 1])                    # y-пересечения y^2 = x^3 + 1

# --- эталонные ответы; в ноутбук не попадают, см. check_archive_b4.py ---
ANSWERS = {
    'q1_1': '[Eq(x, 3), Eq(y, -2)]',
    'q1_2': 'Eq(x, Rational(15, 2))',
    'q1_3': '[Eq(x, -1), Eq(y, 2)]',
    'q1_4': '[Eq(x, 2), Eq(y, Rational(7, 2))]',
    'q1_5': '[Eq(x, 2), Eq(y, 1)]',
    'q1_6': 'Eq(x, -3)',
    'q1_7': 'Eq(y, Rational(2, 3))',
    'q1_8': 'Eq(y, Rational(3, 2))',

    'q2_1': 'Eq(y, pi/2)',
    'q2_2': 'Eq(x, 0)',

    'q3_1': '[Eq(x, Rational(-2, 3)), Eq(y, 4*x/3 - Rational(8, 9))]',
    'q3_2': 'Eq(y, x/2 + Rational(13, 4))',
    'q3_3': 'Eq(y, x/2 - Rational(17, 2))',
    'q3_4': 'Eq(y, x)',

    'q4_1': ("{'vertical_asymptotes': [Rational(-1, 2), Rational(1, 2)],"
             " 'horizontal_asymptotes': [0], 'x_intercepts': [Rational(-2, 3)],"
             " 'y_intercept': -2, 'maxima': [(-0.226, -1.66)],"
             " 'minima': [(-1.11, -0.339)]}"),
    'q4_2': ("{'vertical_asymptotes': [3], 'horizontal_asymptotes': [-2],"
             " 'x_intercepts': [-2], 'y_intercept': Rational(4, 3)}"),
    'q4_3': ("{'vertical_asymptotes': [Rational(15, 2)],"
             " 'oblique_asymptotes': [x/2 + Rational(13, 4)],"
             " 'x_intercepts': [-3, 4], 'y_intercept': Rational(4, 5)}"),
    'q4_4': ("{'vertical_asymptotes': [-1], 'horizontal_asymptotes': [2],"
             " 'x_intercepts': [Rational(1, 2)], 'y_intercept': -1}"),
    'q4_5': ("{'vertical_asymptotes': [-1, 3], 'horizontal_asymptotes': [0],"
             " 'x_intercepts': [], 'y_intercept': Rational(-1, 3),"
             " 'maxima': [(1, Rational(-1, 4))]}"),
    'q4_6': ("{'vertical_asymptotes': [2], 'horizontal_asymptotes': [1],"
             " 'x_intercepts': [3], 'y_intercept': Rational(3, 2)}"),
    'q4_7': ("{'vertical_asymptotes': [-3],"
             " 'oblique_asymptotes': [x/2 - Rational(17, 2)],"
             " 'x_intercepts': [2, 12], 'y_intercept': 4}"),
    'q4_8': ("{'x_intercepts': [-4, 0, 4], 'y_intercept': 0,"
             " 'maxima': [(-1.94, 1.20)], 'minima': [(1.94, -1.20)]}"),
    'q4_9': '[-4, 0, 4]',
    'q4_10': "{'vertical_asymptotes': [0], 'horizontal_asymptotes': [0]}",

    'q5_1': 'Interval(-5, oo)',
    'q5_2': ('Union(Interval(-oo, (5 - sqrt(13))/6),'
             ' Interval((5 + sqrt(13))/6, oo))'),
    'q5_3': ('Union(Interval(-oo, -10 - 5*sqrt(3)),'
             ' Interval(-10 + 5*sqrt(3), oo))'),
    'q5_4a': 'Eq(x, -5)',
    'q5_4b': "{'minima': [(-5, Rational(1, 2))]}",

    'q6_1': "{'y_intercept': 2, 'maxima': [(-1, 4)], 'minima': [(1, 0)]}",
    'q6_2': ("{'y_intercept': 2, 'maxima': [(-sqrt(2), 2 + 4*sqrt(2))],"
             " 'minima': [(sqrt(2), 2 - 4*sqrt(2))]}"),
    'q6_3': "{'endpoints': [(1, 0), (2, sqrt(3))]}",
    'q6_4': "{'x_intercepts': [1]}",
    'q6_4b': "{'x_intercepts': [1]}",
    'q6_5': "{'x_intercepts': [1], 'maxima': [], 'minima': []}",
    'q6_6': ("{'x_intercepts': [-2, -1], 'y_intercept': 2,"
             " 'maxima': [(Rational(-5, 3), Rational(4, 27))],"
             " 'minima': [(-1, 0)]}"),
    'q6_7': "{'x_intercepts': [0], 'maxima': [(1, exp(-1))]}",
    'q6_8': ("{'x_intercepts': [-1.24, 2.42], 'y_intercept': -3,"
             " 'minima': [(1.10, -4.30)],"
             " 'endpoints': [(-4, 8.02), (3, 7.09)]}"),
    'q6_9': "{'x_intercepts': [-3, -1], 'y_intercept': 15, 'minima': [(-2, -5)]}",
    'q6_10': "{'maxima': [(-2.70, 2.28)], 'minima': [(0.899, -4.19)]}",
    'q6_11': '[-2, 2]',

    'q7_1a': '-4*E',
    'q7_1b': '4/E',
    'q7_1c': 'E**2',

    'q8_1': "{'x_intercepts': [0], 'y_intercept': 0}",
    'q8_1b': '0',
    'q8_2': "{'x_intercepts': [-1]}",
    'q8_2b': '[-1, 1]',
    'q8_3': 'oo',
    'q8_5a': "{'x_intercepts': [2]}",
    'q8_5b': "{'x_intercepts': [-1]}",

    'q9_1': 'FiniteSet(-4, 0)',
    'q9_2': 'Union(Interval.open(-oo, -4), Interval.open(0, oo))',
    'q9_3': 'Interval.open(-4, 0)',
    'q9_4': 'FiniteSet(0, 4)',
    'q9_5': 'Union(Interval.open(-oo, 0), Interval.open(4, oo))',
    'q9_6': 'Interval.open(0, 4)',
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
# B4 archive: curve sketching and asymptotes

**Every past-paper question on this topic, grouped by technique.** Not a
practicum — a drill. There is no theory here and no ladder to climb: the
theory is in *Practicum B4*, and this notebook is what you open afterwards,
when the only thing left is to do them all until the moves are automatic.

**What is inside.** The whole of `functions.curve_sketching` and the whole
of `functions.asymptotes` from the AA HL archive, sessions May 2021 —
November 2025: **54 questions, 127 marks**, in nine sections, one section
per technique.

The corpus records 62 blocks and 147 marks. The difference is the November
2023 session, which sits in the archive as two zonal copies of one paper;
the duplicates are merged here, and what is left is what was actually
asked. Where a question appears in both copies the source line says so.

**How to work.** Read the question, answer in the cell below it, run the
cell. The check is not a comparison with a stored answer — it goes back to
the function and asks it. An asymptote is right when the curve actually
approaches it, a range is right when every value in it is attained and
none outside it is, a sketch is right when the features you listed are the
features the function has. So an answer arrived at by a wrong route still
has to be true.

Leave a cell blank and it prints ⬜ and moves on, which means you can run
the whole notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before — and read the markscheme note in it,
because that is where the marks actually are.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Read the vertical and horizontal asymptotes off a rational function | 8 | 12 |
| 2 | Find an asymptote that cannot be read off | 2 | 3 |
| 3 | Find the oblique asymptote | 4 | 13 |
| 4 | Sketch a rational curve | 10 | 26 |
| 5 | Find the range | 4 | 13 |
| 6 | Sketch a curve from its formula, labelling what was asked for | 11 | 33 |
| 7 | Sketch using the second derivative | 1 | 3 |
| 8 | Sketch a curve that is not a function | 5 | 10 |
| 9 | Count the roots of a family | 9 | 14 |

One sentence to carry into the exam: **the marks are for the list, not for
the curve.** Intercepts, turning points, asymptotes — write that list down
before drawing anything.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Union, FiniteSet, Eq, solveset

import matplotlib.pyplot as plt
import numpy as np

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d, m, t = symbols('a b c d m t')
A = Symbol('A', positive=True)


# Draw the true curve so you can compare your sketch with it. Pass
# expressions, or (expression, label) pairs; `lines` takes asymptotes as
# ('v', 3) or ('h', -2) or ('o', x/2 - 1); `marks` takes points to dot.
def show(*curves, span=(-6, 6), ylim=None, size=(6, 3.4), marks=(), lines=()):
    grid = np.linspace(float(span[0]), float(span[1]), 2000)
    fig, ax = plt.subplots(figsize=size)
    for item in curves:
        expr, name = item if isinstance(item, tuple) else (item, None)
        g = lambdify(x, expr, 'math')
        vals = []
        for u in grid:
            try:
                v = float(g(float(u)))
            except (ValueError, TypeError, ZeroDivisionError, OverflowError):
                v = float('nan')
            vals.append(v if abs(v) < 1e6 else float('nan'))
        ax.plot(grid, vals, lw=1.7, label=name or f'y = {expr}')
    for kind, where in lines:
        if kind == 'v':
            ax.axvline(float(where), color='0.55', ls='--', lw=1)
        elif kind == 'h':
            ax.axhline(float(where), color='0.55', ls='--', lw=1)
        else:
            g = lambdify(x, where, 'math')
            ax.plot(grid, [g(float(u)) for u in grid], color='0.55', ls='--', lw=1)
    for point in marks:
        ax.plot(float(point[0]), float(point[1]), 'o', ms=5, color='0.2')
    ax.axhline(0, color='0.6', lw=.8)
    ax.axvline(0, color='0.6', lw=.8)
    ax.grid(alpha=.3)
    if ylim:
        ax.set_ylim(float(ylim[0]), float(ylim[1]))
    ax.legend(fontsize=8)
    plt.tight_layout()
    plt.show()


print('ready; sympy', sp.__version__)
print('an asymptote:        ', Eq(y, x/2 - Rational(17, 2)))
print('a range:             ', Union(Interval(-oo, -1), Interval(2, oo)))
print('a sketch as features:', {'x_intercepts': [2, 12], 'minima': [(5.66, -1.34)]})
print('sketch keys:', 'x_intercepts, y_intercept, maxima, minima, cusps,',
      'endpoints, vertical_asymptotes, horizontal_asymptotes, oblique_asymptotes')
""")

md(r"""
---
## 1 · Read the vertical and horizontal asymptotes off a rational function

*"Write down the equation of the vertical asymptote."* Set the denominator
to zero; compare the degrees for the horizontal one. **8 questions, 12
marks, and eight of them are Paper 1.**

Every answer here is an equation. A number scores zero — the markscheme
says *"must be written as an equation"* in as many words.
""")

md(r"""
### 1.1 · November 2021, Paper 1, Q2(a) · 2 marks · no calculator

The function $f$ is defined by $f(x)=\dfrac{2x+4}{3-x}$, where
$x\in\mathbb{R}$, $x\ne 3$.

Write down the equation of

**(i)** the vertical asymptote of the graph of $f$;

**(ii)** the horizontal asymptote of the graph of $f$.
""")

code(r"""
q1_1 = [...]                   # both asymptotes, as equations

verify_asymptotes('1.1', q1_1, (2*x + 4)/(3 - x))
""")

md(r"""
### 1.2 · November 2021, Paper 2, Q10(b) · 1 mark · calculator

Consider the function $f(x)=\dfrac{x^{2}-x-12}{2x-15}$, where
$x\in\mathbb{R}$, $x\ne\tfrac{15}{2}$.

Write down the equation of the vertical asymptote of the graph of $f$.
""")

code(r"""
q1_2 = ...                     # the vertical asymptote, as an equation

verify_asymptotes('1.2', q1_2, (x**2 - x - 12)/(2*x - 15), kinds=('vertical',))
""")

md(r"""
### 1.3 · May 2022 TZ2, Paper 1, Q3(a) · 2 marks · no calculator

A function $f$ is defined by $f(x)=\dfrac{2x-1}{x+1}$, where
$x\in\mathbb{R}$, $x\ne-1$.

The graph of $y=f(x)$ has a vertical asymptote and a horizontal asymptote.
Write down the equation of

**(i)** the vertical asymptote; **(ii)** the horizontal asymptote.
""")

code(r"""
q1_3 = [...]

verify_asymptotes('1.3', q1_3, (2*x - 1)/(x + 1))
""")

md(r"""
### 1.4 · May 2023 TZ1, Paper 1, Q1(b) · 2 marks · no calculator

The function $f$ is defined by $f(x)=\dfrac{7x+7}{2x-4}$ for
$x\in\mathbb{R}$, $x\ne 2$.

For the graph of $y=f(x)$, write down the equation of

**(i)** the vertical asymptote; **(ii)** the horizontal asymptote.
""")

code(r"""
q1_4 = [...]

verify_asymptotes('1.4', q1_4, (7*x + 7)/(2*x - 4))
""")

md(r"""
### 1.5 · May 2023 TZ2, Paper 1, Q2(a) · 2 marks · no calculator

A function $f$ is defined by $f(x)=1-\dfrac{1}{x-2}$, where
$x\in\mathbb{R}$, $x\ne 2$.

The graph of $y=f(x)$ has a vertical asymptote and a horizontal asymptote.
Write down the equation of

**(i)** the vertical asymptote; **(ii)** the horizontal asymptote.
""")

code(r"""
q1_5 = [...]

verify_asymptotes('1.5', q1_5, 1 - 1/(x - 2))
""")

md(r"""
### 1.6 · November 2023, Paper 2, Q11(a) · 1 mark · calculator

*Recorded twice in the corpus, once under TZ1 and once under TZ2. It is
one paper.*

Consider the function defined by $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, where
$x\in\mathbb{R}$, $x\ne-3$.

State the equation of the vertical asymptote on the graph of $f$.
""")

code(r"""
q1_6 = ...

verify_asymptotes('1.6', q1_6, (x**2 - 14*x + 24)/(2*x + 6), kinds=('vertical',))
""")

md(r"""
### 1.7 · May 2024 TZ2, Paper 1, Q5(a) · 1 mark · no calculator

A function $f$ is defined by $f(x)=\dfrac{2(x+3)}{3(x+2)}$, where
$x\in\mathbb{R}$, $x\ne-2$. The graph of $y=f(x)$ is given in the paper.

Write down the equation of the horizontal asymptote.
""")

code(r"""
q1_7 = ...

verify_asymptotes('1.7', q1_7, 2*(x + 3)/(3*(x + 2)), kinds=('horizontal',))
""")

md(r"""
### 1.8 · May 2025 TZ2, Paper 1, Q1(b) · 1 mark · no calculator

The function $f$ is defined by $f(x)=\dfrac{3x-2}{2x+1}$ for
$x\in\mathbb{R}$, $x\ne-\tfrac12$.

Write down the equation of the horizontal asymptote.
""")

code(r"""
q1_8 = ...

verify_asymptotes('1.8', q1_8, (3*x - 2)/(2*x + 1), kinds=('horizontal',))
""")


md(r"""
---
## 2 · Find an asymptote that cannot be read off

No denominator to set to zero, no degrees to compare — the answer is a
limit and nothing else. **2 questions, 3 marks.**
""")

md(r"""
### 2.1 · May 2021 TZ2, Paper 2, Q12(b) · 2 marks · calculator

A function $f$ is defined by
$f(x)=\arcsin\!\left(\dfrac{x^{2}-1}{x^{2}+1}\right)$, $x\in\mathbb{R}$.

By considering limits, show that the graph of $y=f(x)$ has a horizontal
asymptote and state its equation.
""")

code(r"""
q2_1 = ...                     # the horizontal asymptote, as an equation

verify_asymptotes('2.1', q2_1, asin((x**2 - 1)/(x**2 + 1)), kinds=('horizontal',))
""")

md(r"""
### 2.2 · November 2023, Paper 1, Q10(a) · 1 mark · no calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

The functions $f$ and $g$ are defined by

$$f(x)=\ln(2x-9),\ \ x>\tfrac92\qquad
g(x)=2\ln x-\ln d,\ \ x>0,\ d\in\mathbb{R}^{+}.$$

State the equation of the vertical asymptote to the graph of $y=g(x)$.
""")

code(r"""
q2_2 = ...

dpos = Symbol('d', positive=True)
verify_asymptotes('2.2', q2_2, 2*log(x) - log(dpos), kinds=('vertical',))
""")

md(r"""
---
## 3 · Find the oblique asymptote

The numerator's degree is exactly one more than the denominator's. Divide:
the quotient is the line, the remainder is what vanishes. **4 questions, 13
marks — and all of them are on calculator papers, where the calculator can
do nothing at all.**
""")

md(r"""
### 3.1 · May 2021 TZ1, Paper 2, Q11(e) · 4 marks · calculator

The function $g$ is defined by $g(x)=\dfrac{4x^{2}-1}{3x+2}$, for
$x\in\mathbb{R}$, $x\ne-\tfrac23$.

Find the equations of **all** the asymptotes on the graph of $y=g(x)$.
""")

code(r"""
q3_1 = [...]                   # all of them — and there may be fewer kinds than you expect

verify_asymptotes('3.1', q3_1, (4*x**2 - 1)/(3*x + 2))
""")

md(r"""
### 3.2 · November 2021, Paper 2, Q10(c) · 4 marks · calculator

Consider $f(x)=\dfrac{x^{2}-x-12}{2x-15}$, $x\ne\tfrac{15}{2}$.

The oblique asymptote of the graph of $f$ can be written as $y=ax+b$ where
$a,b\in\mathbb{Q}$. Find the value of $a$ and the value of $b$.
""")

code(r"""
q3_2 = ...                     # the whole line, as an equation

verify_asymptotes('3.2', q3_2, (x**2 - x - 12)/(2*x - 15), kinds=('oblique',))
""")

md(r"""
### 3.3 · November 2023, Paper 2, Q11(c) · 4 marks · calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

Consider $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$, $x\ne-3$.

The graph of $f$ has an oblique asymptote of the form $y=ax+b$, where
$a,b\in\mathbb{Q}$. Find the value of $a$ and the value of $b$.
""")

code(r"""
q3_3 = ...

verify_asymptotes('3.3', q3_3, (x**2 - 14*x + 24)/(2*x + 6), kinds=('oblique',))
""")

md(r"""
### 3.4 · May 2025 TZ2, Paper 3, Q1(d)(ii) · 1 mark · calculator

Consider the curve $y=\dfrac{x\left(x^{2}-A\right)}{x^{2}+A}$, where $A$ is
a positive constant and $x\in\mathbb{R}$.

Part (d)(i) has just established the identity
$\;x-\dfrac{2Ax}{x^{2}+A}\equiv\dfrac{x\left(x^{2}-A\right)}{x^{2}+A}$.

Hence, determine the equation of the oblique asymptote to the curve.
""")

code(r"""
q3_4 = ...                     # one answer for every A at once

verify_asymptotes('3.4', q3_4, x*(x**2 - A)/(x**2 + A), kinds=('oblique',))
""")

md(r"""
---
## 4 · Sketch a rational curve

Asymptotes first, dashed and labelled; then the intercepts; then the
turning points; then join the branches, one region at a time. That order
is not advice — it is the order the markscheme pays in. **10 questions, 26
marks.**

The check reads your sketch as the list of features you claim, and it
catches both kinds of error separately: a feature named that is not there,
and a feature there that you did not name. What it cannot see is the shape
*between* the features, so every task here prints the true curve
underneath. Compare.
""")

md(r"""
### 4.1 · May 2021 TZ1, Paper 2, Q11(d) · 5 marks · calculator

The function $f$ is defined by $f(x)=\dfrac{3x+2}{4x^{2}-1}$, for
$x\in\mathbb{R}$, $x\ne p$, $x\ne q$.

Sketch the graph of $y=f(x)$ for $-3\le x\le 3$, showing the values of any
axes intercepts, the coordinates of any local maxima and local minima, and
giving the equations of any asymptotes.
""")

code(r"""
q4_1 = {...}     # keys: vertical_asymptotes, horizontal_asymptotes, x_intercepts,
                 # y_intercept, maxima, minima

f41 = (3*x + 2)/(4*x**2 - 1)
verify_sketch('4.1', q4_1, f41)

show(f41, span=(-3, 3), ylim=(-6, 6), size=(6, 3.6),
     lines=[('v', Rational(-1, 2)), ('v', Rational(1, 2)), ('h', 0)])
""")

md(r"""
### 4.2 · November 2021, Paper 1, Q2(c) · 1 mark · no calculator

Sketch the graph of $f(x)=\dfrac{2x+4}{3-x}$ on the axes provided (both
axes run from $-15$ to $15$).

*The question asks only for the shape; list the features you would put on
the sketch and let the check confirm them.*
""")

code(r"""
q4_2 = {...}     # keys: vertical_asymptotes, horizontal_asymptotes,
                 # x_intercepts, y_intercept

f42 = (2*x + 4)/(3 - x)
verify_sketch('4.2', q4_2, f42)

show(f42, span=(-15, 15), ylim=(-15, 15), lines=[('v', 3), ('h', -2)])
""")

md(r"""
### 4.3 · November 2021, Paper 2, Q10(d) · 3 marks · calculator

Sketch the graph of $f(x)=\dfrac{x^{2}-x-12}{2x-15}$ for $-30\le x\le 30$,
clearly indicating the points of intersection with each axis and any
asymptotes.
""")

code(r"""
q4_3 = {...}     # keys: vertical_asymptotes, oblique_asymptotes,
                 # x_intercepts, y_intercept

f43 = (x**2 - x - 12)/(2*x - 15)
verify_sketch('4.3', q4_3, f43)

show(f43, span=(-30, 30), ylim=(-30, 30),
     lines=[('v', Rational(15, 2)), ('o', x/2 + Rational(13, 4))])
""")

md(r"""
### 4.4 · May 2022 TZ2, Paper 1, Q3(b) · 3 marks · no calculator

On the set of axes provided ($-6$ to $6$ both ways), sketch the graph of
$y=f(x)$ where $f(x)=\dfrac{2x-1}{x+1}$.

On your sketch, clearly indicate the asymptotes and the position of any
points of intersection with the axes.
""")

code(r"""
q4_4 = {...}     # keys: vertical_asymptotes, horizontal_asymptotes,
                 # x_intercepts, y_intercept

f44 = (2*x - 1)/(x + 1)
verify_sketch('4.4', q4_4, f44)

show(f44, span=(-6, 6), ylim=(-6, 6), lines=[('v', -1), ('h', 2)])
""")

md(r"""
### 4.5 · May 2022 TZ2, Paper 1, Q11(a) · 6 marks · no calculator

A function $f$ is defined by $f(x)=\dfrac{1}{x^{2}-2x-3}$, where
$x\in\mathbb{R}$, $x\ne-1$, $x\ne 3$.

Sketch the curve $y=f(x)$, clearly indicating any asymptotes with their
equations. State the coordinates of any local maximum or minimum points and
any points of intersection with the coordinate axes.
""")

code(r"""
q4_5 = {...}     # keys: vertical_asymptotes, horizontal_asymptotes,
                 # x_intercepts, y_intercept, maxima

f45 = 1/(x**2 - 2*x - 3)
verify_sketch('4.5', q4_5, f45)

show(f45, span=(-4, 6), ylim=(-3, 2), lines=[('v', -1), ('v', 3), ('h', 0)])
""")

md(r"""
### 4.6 · May 2023 TZ2, Paper 1, Q2(c) · 1 mark · no calculator

On the set of axes provided, sketch the graph of $y=f(x)$ where
$f(x)=1-\dfrac{1}{x-2}$, showing all the features found in parts (a) and
(b) — the two asymptotes and the two intercepts.
""")

code(r"""
q4_6 = {...}     # keys: vertical_asymptotes, horizontal_asymptotes,
                 # x_intercepts, y_intercept

f46 = 1 - 1/(x - 2)
verify_sketch('4.6', q4_6, f46)

show(f46, span=(-5, 9), ylim=(-5, 6), lines=[('v', 2), ('h', 1)])
""")

md(r"""
### 4.7 · November 2023, Paper 2, Q11(d) · 4 marks · calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

Sketch the graph of $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$ for $-50\le x\le 50$,
showing clearly the asymptotes and any intersections with the axes.
""")

code(r"""
q4_7 = {...}     # keys: vertical_asymptotes, oblique_asymptotes,
                 # x_intercepts, y_intercept

f47 = (x**2 - 14*x + 24)/(2*x + 6)
verify_sketch('4.7', q4_7, f47)

show(f47, span=(-50, 50), ylim=(-60, 40),
     lines=[('v', -3), ('o', x/2 - Rational(17, 2))])
""")

md(r"""
### 4.8 · May 2025 TZ2, Paper 3, Q1(a)(i)(iii) · 1 + 2 marks · calculator

Consider the curve given by $y=\dfrac{x\left(x^{2}-16\right)}{x^{2}+16}$.

**(i)** Sketch the curve of $y$ for $-10\le x\le 10$.

**(iii)** State the coordinates of the local maximum point and the
coordinates of the local minimum point.
""")

code(r"""
q4_8 = {...}     # keys: x_intercepts, y_intercept, maxima, minima

f48 = x*(x**2 - 16)/(x**2 + 16)
verify_sketch('4.8', q4_8, f48)

show(f48, span=(-10, 10), ylim=(-10, 10), lines=[('o', x)])
""")

md(r"""
### 4.9 · May 2025 TZ2, Paper 3, Q1(a)(ii) · 1 mark · calculator

State the coordinates of the points where the same curve
$y=\dfrac{x\left(x^{2}-16\right)}{x^{2}+16}$ crosses the $x$-axis.
""")

code(r"""
q4_9 = [...]                   # the x-coordinates

verify_sketch('4.9', {'x_intercepts': q4_9}, x*(x**2 - 16)/(x**2 + 16))
""")

md(r"""
### 4.10 · November 2025 TZ1, Paper 3, Q1(d)(i) · 1 mark · calculator

The curve $H$ has equation $y=\dfrac{1}{x}$, where $x\in\mathbb{R}$,
$x\ne 0$.

Sketch the curve $H$.
""")

code(r"""
q4_10 = {...}    # keys: vertical_asymptotes, horizontal_asymptotes

verify_sketch('4.10', q4_10, 1/x)

show(1/x, span=(-6, 6), ylim=(-6, 6), lines=[('v', 0), ('h', 0)])
""")


md(r"""
---
## 5 · Find the range

The same picture read sideways: off the vertical axis instead of the
horizontal one. **4 questions, 13 marks — and the mark is usually one
symbol.** A turning point is attained and takes $\le$; a horizontal
asymptote is not and takes $<$.

The check tests every endpoint of your set three times over — the endpoint
itself and a step to either side of it — because that is the only place
this topic is ever wrong.
""")

md(r"""
### 5.1 · May 2021 TZ2, Paper 2, Q4(a) · 2 marks · calculator

The functions $f$ and $g$ are defined for $x\in\mathbb{R}$ by
$f(x)=6x^{2}-12x+1$ and $g(x)=-x+c$, where $c\in\mathbb{R}$.

Find the range of $f$.
""")

code(r"""
q5_1 = ...                     # a set or an inequality: Interval(...), (y >= ...)

verify_range('5.1', q5_1, 6*x**2 - 12*x + 1)
""")

md(r"""
### 5.2 · May 2023 TZ2, Paper 2, Q8(a) · 4 marks · calculator

A function $g$ is defined by $g(x)=\dfrac{2x-5}{x^{2}-3}$, where
$x\in\mathbb{R}$, $x\ne\pm\sqrt3$.

Determine the range of $g$.
""")

code(r"""
q5_2 = ...                     # exact form; the calculator gives 3 s.f., the algebra gives surds

verify_range('5.2', q5_2, (2*x - 5)/(x**2 - 3))
""")

md(r"""
### 5.3 · November 2023, Paper 2, Q11(e) · 4 marks · calculator

*The corpus records this part only under TZ2, but it is printed in both
copies of the paper.*

Find the range of $f$, where $f(x)=\dfrac{x^{2}-14x+24}{2x+6}$,
$x\ne-3$.
""")

code(r"""
q5_3 = ...

verify_range('5.3', q5_3, (x**2 - 14*x + 24)/(2*x + 6))
""")

md(r"""
### 5.4 · November 2025 TZ3, Paper 1, Q9(b) · 3 marks · no calculator

Consider the function defined by $f(x)=\tfrac12x^{2}+kx+13$, where
$x\in\mathbb{R}$ and $k\in\mathbb{Z}^{+}$. Part (a) has shown that if
$f(x)=0$ has no real roots then the greatest possible value of $k$ is $5$.
Take $k=5$.

**(i)** Write down the equation of the axis of symmetry of the graph of $f$.

**(ii)** Hence, or otherwise, determine the coordinates of the minimum
point on the graph of $f$.
""")

code(r"""
q5_4a = ...                    # the axis of symmetry, as an equation
q5_4b = {...}                  # key: minima

check_expr('5.4(i)', q5_4a, '""" + D_54 + r"""')
verify_sketch('5.4(ii)', q5_4b, x**2/2 + 5*x + 13)
""")

md(r"""
---
## 6 · Sketch a curve from its formula, labelling what was asked for

The largest section: **11 questions, 33 marks.** Nine of them are on
calculator papers, and here the calculator earns its place — nobody finds
the roots of $e^{x}-3x-4$ by hand for a sketch.

Read the instruction first and write down the list of things it names. The
marks are for the labels.
""")

md(r"""
### 6.1 · May 2021 TZ1, Paper 3, Q1(a)(i) · 3 marks · calculator

*This question asks you to explore the behaviour and key features of cubic
polynomials of the form $x^{3}-3cx+d$.*

Consider $f(x)=x^{3}-3cx+2$ for $x\in\mathbb{R}$, where $c$ is a parameter.

Sketch the graph of $y=f(x)$ showing the value of the $y$-intercept and the
coordinates of any points with zero gradient, for $c=1$.
""")

code(r"""
q6_1 = {...}     # keys: y_intercept, maxima, minima

f61 = x**3 - 3*x + 2
verify_sketch('6.1', q6_1, f61)

show(f61, span=(-3, 3), ylim=(-6, 10))
""")

md(r"""
### 6.2 · May 2021 TZ1, Paper 3, Q1(a)(ii) · 3 marks · calculator

The same, for $c=2$: sketch $y=x^{3}-6x+2$, showing the value of the
$y$-intercept and the coordinates of any points with zero gradient.

*The markscheme accepts the exact coordinates as well as the 3 s.f. ones.*
""")

code(r"""
q6_2 = {...}     # keys: y_intercept, maxima, minima

f62 = x**3 - 6*x + 2
verify_sketch('6.2', q6_2, f62)

show(f62, span=(-3, 3), ylim=(-8, 12))
""")

md(r"""
### 6.3 · May 2022 TZ1, Paper 2, Q10(a) · 2 marks · calculator

Consider the function $f(x)=\sqrt{x^{2}-1}$, where $1\le x\le 2$.

Sketch the curve $y=f(x)$, clearly indicating the coordinates of the
endpoints.
""")

code(r"""
q6_3 = {...}     # key: endpoints

f63 = sqrt(x**2 - 1)
verify_sketch('6.3', q6_3, f63, domain=(1, 2))

show(f63, span=(1, 2), size=(5, 3))
""")

md(r"""
### 6.4 · May 2022 TZ1, Paper 3, Q2(c) · 2 marks · calculator

Consider $f(x)=(x-1)(x^{2}-8x+17)$ for $x\in\mathbb{R}$. Part (b) has shown
that the line $y=x-1$ is tangent to the curve $y=f(x)$ at the point
$\mathrm{A}(4,3)$.

Sketch the curve $y=f(x)$ and the tangent to the curve at point
$\mathrm{A}$, clearly showing where the tangent crosses the $x$-axis.
""")

code(r"""
q6_4 = {...}     # key: x_intercepts — for the curve
q6_4b = {...}    # key: x_intercepts — for the tangent line

f64 = (x - 1)*(x**2 - 8*x + 17)
verify_sketch('6.4 curve', q6_4, f64)
verify_sketch('6.4 tangent', q6_4b, x - 1)

show(f64, (x - 1, 'tangent at A'), span=(-1, 6), ylim=(-10, 25),
     marks=[(4, 3)])
""")

md(r"""
### 6.5 · May 2022 TZ1, Paper 3, Q2(h)(i) · 2 marks · calculator

Consider the curve $y=(x-r)(x^{2}-2ax+a^{2}+b^{2})$ in the special case
$a=r=1$ and $b=2$.

Sketch the curve.

*The markscheme wants a positive cubic with **no** stationary points and a
non-stationary point of inflexion at $x=1$. State the intercepts and the
turning points you find — and there is a right answer for a list that turns
out to be empty.*
""")

code(r"""
q6_5 = {...}     # keys: x_intercepts, maxima, minima

f65 = (x - 1)*(x**2 - 2*x + 5)
verify_sketch('6.5', q6_5, f65)

show(f65, span=(-2, 4), ylim=(-20, 20))
""")

md(r"""
### 6.6 · November 2022, Paper 1, Q11(b)(iv) · 3 marks · no calculator

Let $P(x)=x^{3}+ax^{2}+bx+c$, where each of $a$, $b$, $c$ is one of
$1,2,3,4,5$ and no value is repeated. Earlier parts give $a=4$, $b=5$,
$c=2$, so $P(x)=(x+1)^{2}(x+2)$.

Hence or otherwise, sketch the graph of $y=P(x)$, clearly showing the
coordinates of any intercepts with the axes.
""")

code(r"""
q6_6 = {...}     # keys: x_intercepts, y_intercept, maxima, minima

f66 = x**3 + 4*x**2 + 5*x + 2
verify_sketch('6.6', q6_6, f66)

show(f66, span=(-3, 1), ylim=(-3, 6))
""")

md(r"""
### 6.7 · May 2023 TZ1, Paper 3, Q1(a) · 4 marks · calculator

*In this question you will be investigating the family of functions of the
form $f(x)=x^{n}e^{-x}$.*

When $n=1$, the function is $f_{1}(x)=xe^{-x}$, where $x\ge 0$.

Sketch the graph of $y=f_{1}(x)$, stating the coordinates of the local
maximum point.
""")

code(r"""
q6_7 = {...}     # keys: x_intercepts, maxima

f67 = x*exp(-x)
verify_sketch('6.7', q6_7, f67, domain=(0, oo))

show(f67, span=(0, 8), size=(5.5, 3))
""")

md(r"""
### 6.8 · November 2023, Paper 2, Q2(a) · 3 marks · calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

Consider the function $f(x)=e^{x}-3x-4$.

On the axes provided, sketch the graph of $f$ for $-4\le x\le 3$.

*The markscheme pays for the roots, for the $y$-intercept together with the
local minimum, and for the two endpoints.*
""")

code(r"""
q6_8 = {...}     # keys: x_intercepts, y_intercept, minima, endpoints

f68 = exp(x) - 3*x - 4
verify_sketch('6.8', q6_8, f68, domain=(-4, 3))

show(f68, span=(-4, 3), ylim=(-6, 10))
""")

md(r"""
### 6.9 · May 2025 TZ1, Paper 1, Q10(b) · 4 marks · no calculator

The function $f$ is defined by $f(x)=5(x+1)(x+3)$, where $x\in\mathbb{R}$.

Sketch the graph of $y=f(x)$, showing the values of any intercepts with the
axes and the coordinates of the vertex.
""")

code(r"""
q6_9 = {...}     # keys: x_intercepts, y_intercept, minima

f69 = 5*(x + 1)*(x + 3)
verify_sketch('6.9', q6_9, f69)

show(f69, span=(-5, 1), ylim=(-8, 20))
""")

md(r"""
### 6.10 · May 2025 TZ3, Paper 2, Q12(c) · 5 marks · calculator

Part (b) has solved $\dfrac{dy}{dx}=x^{2}-y-5$ and given the general
solution $y=x^{2}-2x-3+Ce^{-x}$.

Sketch the curve of the particular solution which passes through the point
$(-3,2)$, for $-4\le x\le 4$, clearly labelling the coordinates of any
local maximum and minimum points.
""")

code(r"""
q6_10 = {...}    # keys: maxima, minima

f610 = x**2 - 2*x - 3 - 10*exp(-x - 3)
verify_sketch('6.10', q6_10, f610)

show(f610, span=(-4, 4), ylim=(-6, 6))
""")

md(r"""
### 6.11 · November 2025 TZ1, Paper 3, Q1(d)(ii) · 2 marks · calculator

*This question asks you to investigate lines normal to curves of the form
$y=\dfrac{k^{2}}{x}$.* The curve $H$ is $y=\dfrac1x$. Earlier parts have
shown that a line normal to $H$ at $x=t$ has gradient $t^{2}$, and that
there are exactly two normals of gradient $m$ whenever $m>0$, $m\ne 1$.

For an appropriate value of $m$, sketch two lines that are normal to $H$,
clearly indicating the point at which each line is normal to $H$.

*Take $m=4$ and give the two values of $x$ at which a line of gradient $4$
is normal to $H$.*
""")

code(r"""
q6_11 = [...]                  # the two values of x

# the normal's gradient is -1 over the curve's gradient
verify_roots('6.11', q6_11, -1/diff(1/x, x) - 4, (-10, 10))

show(1/x, (4*x + 1/2 - 8, 'normal at x = 2'), (4*x - 1/2 + 8, 'normal at x = -2'),
     span=(-4, 4), ylim=(-6, 6), marks=[(2, Rational(1, 2)), (-2, Rational(-1, 2))])
""")


md(r"""
---
## 7 · Sketch using the second derivative

**1 question, 3 marks** — and it is the only place in the topic where the
mark is for the shape *between* the features, which no check can see. So
this one is answered through the second derivative instead: the numbers
that decide how sharply the curve turns.
""")

md(r"""
### 7.1 · November 2023, Paper 1, Q11(c) · 3 marks · no calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

Consider $f(x)=e^{\cos 2x}$, where $-\tfrac{\pi}{4}\le x\le\tfrac{5\pi}{4}$.
Part (a) found the points of zero gradient and part (b) used the second
derivative to classify them.

Sketch the curve of $y=f(x)$ for $0\le x\le\pi$, taking into consideration
the relative values of the second derivative found in part (b).

**(i)** $f''(0)$. **(ii)** $f''\!\left(\tfrac{\pi}{2}\right)$.
**(iii)** By what factor is the curve's bend sharper at the maximum than at
the minimum, that is $\left|f''(0)\right|\div\left|f''(\pi/2)\right|$?
""")

code(r"""
q7_1a = ...                    # f''(0), exactly
q7_1b = ...                    # f''(pi/2), exactly
q7_1c = ...                    # the ratio of the magnitudes

check_expr('7.1(i)', q7_1a, '""" + D_71A + r"""')
check_expr('7.1(ii)', q7_1b, '""" + D_71B + r"""')
check_expr('7.1(iii)', q7_1c, '""" + D_71C + r"""')

show(exp(cos(2*x)), span=(0, float(pi)), size=(5.5, 3),
     marks=[(0, float(E)), (float(pi/2), float(1/E)), (float(pi), float(E))])
""")

md(r"""
---
## 8 · Sketch a curve that is not a function

$y^{2}=f(x)$: two branches, mirror images in the $x$-axis, and at an
$x$-intercept the curve is vertical — unless the two branches meet there in
a cusp. **5 questions, 10 marks, all of them Paper 3.**
""")

md(r"""
### 8.1 · May 2022 TZ2, Paper 3, Q1(a)(i) · 2 marks · calculator

*This question asks you to explore properties of a family of curves of the
type $y^{2}=x^{3}+ax+b$.*

On the same set of axes, sketch $y^{2}=x^{3}$ for $x\ge 0$, on
$-2\le x\le 2$ and $-2\le y\le 2$, clearly indicating any points of
intersection with the coordinate axes.

*The upper branch is $y=x^{3/2}$. Give its intercepts, and its gradient at
the origin — that number is what makes the markscheme's cusp a cusp.*
""")

code(r"""
q8_1 = {...}     # keys: x_intercepts, y_intercept — for the upper branch
q8_1b = ...      # the gradient of the upper branch at the origin

verify_sketch('8.1', q8_1, x**Rational(3, 2), domain=(0, 2))
check_num('8.1 gradient', q8_1b, 6, '""" + D_81 + r"""')

show(x**Rational(3, 2), -x**Rational(3, 2), span=(0, 2), ylim=(-2, 2), size=(5, 3.2))
""")

md(r"""
### 8.2 · May 2022 TZ2, Paper 3, Q1(a)(ii) · 2 marks · calculator

On the same axes, sketch $y^{2}=x^{3}+1$ for $x\ge-1$, clearly indicating
any points of intersection with the coordinate axes.
""")

code(r"""
q8_2 = {...}     # key: x_intercepts — for the upper branch
q8_2b = [...]    # both y-intercepts of the curve

verify_sketch('8.2', q8_2, sqrt(x**3 + 1), domain=(-1, 2))
check_set('8.2 y-intercepts', q8_2b, '""" + D_82 + r"""')

show(sqrt(x**3 + 1), -sqrt(x**3 + 1), span=(-1, 2), ylim=(-3, 3), size=(5, 3.2))
""")

md(r"""
### 8.3 · May 2022 TZ2, Paper 3, Q1(b)(ii) · 1 mark · calculator

By considering each curve from part (a), identify **two** key features that
would distinguish one curve from the other.

*The exam wants words, and the solution lists every accepted answer. One of
them is a number, so answer that one here: the gradient of the upper branch
of $y^{2}=x^{3}+1$ at its $x$-intercept.*
""")

code(r"""
q8_3 = ...                     # a number, or oo

check_expr('8.3', q8_3, '""" + D_83 + r"""')
""")

md(r"""
### 8.4 · May 2022 TZ2, Paper 3, Q1(c) · 2 marks · calculator

Now consider curves of the form $y^{2}=x^{3}+b$, for
$x\ge-\sqrt[3]{b}$, where $b\in\mathbb{Z}^{+}$.

By varying the value of $b$, suggest **two** key features common to these
curves.

*Words again, and no check: this one is scored by the solution below. Write
your two down first, then compare — the markscheme prints eleven acceptable
answers and refuses one that looks acceptable.*
""")

md(r"""
### 8.5 · November 2023, Paper 3, Q2(b) · 3 marks · calculator

*Recorded twice in the corpus, TZ1 and TZ2. One paper.*

A family of curves has equation $y^{2}=4a^{2}-4ax$, and a second family has
equation $y^{2}=4b^{2}+4bx$, where $a$ and $b$ are positive real
parameters.

Consider the case $a=2$ and $b=1$. On the same set of axes, sketch the
curves $y^{2}=16-8x$ and $y^{2}=4+4x$. On your sketch, clearly label each
curve and any $x$-intercepts.
""")

code(r"""
q8_5a = {...}    # key: x_intercepts — for y^2 = 16 - 8x
q8_5b = {...}    # key: x_intercepts — for y^2 = 4 + 4x

verify_sketch('8.5 first', q8_5a, sqrt(16 - 8*x), domain=(-5, 2))
verify_sketch('8.5 second', q8_5b, sqrt(4 + 4*x), domain=(-1, 5))

show((sqrt(16 - 8*x), 'y^2 = 16 - 8x'), (-sqrt(16 - 8*x), None),
     (sqrt(4 + 4*x), 'y^2 = 4 + 4x'), (-sqrt(4 + 4*x), None),
     span=(-2, 3), ylim=(-6, 6))
""")

md(r"""
---
## 9 · Count the roots of a family

A letter in the formula and a question that asks for a count. The count
changes exactly when a turning point crosses the axis — which is why this
is the last section: it needs the whole list and one idea more.

**9 questions, 14 marks, and all of them are one Paper 3 investigation:**
November 2023, the family $y=x^{3}+ax^{2}+b$.

The check here holds no answer at all. It is handed a function that counts
the distinct real roots of the cubic, and it asks that function about your
set — inside, outside, and on both sides of every endpoint.
""")

code(r"""
# The whole of section 9 is checked against this. It is not an answer: it
# is the question, written so a machine can be asked it one b at a time.
def crossings(a_value, count):
    def holds(b_value):
        roots = Poly(x**3 + a_value*x**2 + b_value, x).real_roots()
        return len(set(roots)) == count
    return holds


print('ready')
""")

md(r"""
### 9.1 · November 2023, Paper 3, Q1(a) · 2 marks · calculator

*This question asks you to explore some properties of the family of curves
$y=x^{3}+ax^{2}+b$, where $a,b$ are real parameters.*

First consider the case $a=3$.

By systematically varying the value of $b$, or otherwise, find the two
values of $b$ such that the curve $y=x^{3}+3x^{2}+b$ has exactly two
$x$-axis intercepts.
""")

code(r"""
q9_1 = ...                     # a set: FiniteSet(...)

verify_param_set('9.1', q9_1, crossings(3, 2), var=b)
""")

md(r"""
### 9.2 · November 2023, Paper 3, Q1(b)(i) · 1 mark · calculator

Write down the set of values of $b$ such that $y=x^{3}+3x^{2}+b$ has
exactly **one** $x$-axis intercept.
""")

code(r"""
q9_2 = ...                     # Interval.open(...), Union(...), ...

verify_param_set('9.2', q9_2, crossings(3, 1), var=b)
""")

md(r"""
### 9.3 · November 2023, Paper 3, Q1(b)(ii) · 1 mark · calculator

Write down the set of values of $b$ such that $y=x^{3}+3x^{2}+b$ has
exactly **three** $x$-axis intercepts.
""")

code(r"""
q9_3 = ...

verify_param_set('9.3', q9_3, crossings(3, 3), var=b)
""")

md(r"""
### 9.4 · November 2023, Paper 3, Q1(c)(i) · 1 mark · calculator

Now consider the case $a=-3$. Write down the set of values of $b$ such that
$y=x^{3}-3x^{2}+b$ has exactly **two** $x$-axis intercepts.
""")

code(r"""
q9_4 = ...

verify_param_set('9.4', q9_4, crossings(-3, 2), var=b)
""")

md(r"""
### 9.5 · November 2023, Paper 3, Q1(c)(ii) · 1 mark · calculator

Write down the set of values of $b$ such that $y=x^{3}-3x^{2}+b$ has
exactly **one** $x$-axis intercept.
""")

code(r"""
q9_5 = ...

verify_param_set('9.5', q9_5, crossings(-3, 1), var=b)
""")

md(r"""
### 9.6 · November 2023, Paper 3, Q1(c)(iii) · 1 mark · calculator

Write down the set of values of $b$ such that $y=x^{3}-3x^{2}+b$ has
exactly **three** $x$-axis intercepts.
""")

code(r"""
q9_6 = ...

verify_param_set('9.6', q9_6, crossings(-3, 3), var=b)
""")

md(r"""
### 9.7 · November 2023, Paper 3, Q1(d) · 1 mark · calculator

Consider the curve $y=x^{3}+ax^{2}+b$ for $a\ne 0$, in the case where it
has exactly three $x$-axis intercepts.

State whether each point of zero gradient is located above or below the
$x$-axis.

*One line of words, and no check — this is the sentence part (h) is built
on. Write it down before opening the solution.*
""")

md(r"""
### 9.8 · November 2023, Paper 3, Q1(f)(ii) · 1 mark · calculator

Consider the points $\mathrm{P}(0,b)$ and
$\mathrm{Q}\!\left(-\tfrac23a,\tfrac{4}{27}a^{3}+b\right)$ of zero gradient
for $a>0$ and $b>0$.

Determine whether each point is located above or below the $x$-axis.

*Words again, no check.*
""")

md(r"""
### 9.9 · November 2023, Paper 3, Q1(h) · 5 marks · calculator

Prove that if $4a^{3}b+27b^{2}<0$ then the curve $y=x^{3}+ax^{2}+b$ has
exactly three $x$-axis intercepts.

*The last five marks of the investigation, and a proof — nothing to check.
Write it out, then read the solution: the whole argument is 9.7 said in
algebra.*
""")


md(r"""
---
# Solutions

Numbered exactly as the questions. Each one gives the answer, the shortest
route to it, and the markscheme detail — which is usually where the mark
was actually lost.
""")

md(r"""
## 1 · Reading them off

**1.1** $\;x=3$ and $y=-2$. The denominator $3-x$ vanishes at $x=3$; the
degrees are equal so the horizontal asymptote is the ratio of the leading
coefficients, $\dfrac{2}{-1}=-2$.

That minus sign is the whole difficulty. Written as $\dfrac{2x+4}{3-x}$ the
denominator's leading coefficient is $-1$, and reading the ratio as $2$ is
the standard slip; rewriting as $\dfrac{-2x-4}{x-3}$ first makes it visible.

**1.2** $\;x=\tfrac{15}{2}$. The markscheme prints *"Award A0 for
$x\ne\tfrac{15}{2}$"* — copying the exclusion from the stem is not an
answer. It also allows the mark to be earned in part (d) if the line
appears on the sketch there.

**1.3** $\;x=-1$, $\;y=2$.

**1.4** $\;x=2$, $\;y=\tfrac72$. The markscheme writes *"must be an
equation with $x$"* and *"must be an equation with $y$"* against the two
A1s.

**1.5** $\;x=2$, $\;y=1$. Here the function is already in the shifted form
$1-\dfrac{1}{x-2}$, so both asymptotes can be read straight off: the
subtracted fraction blows up at $x=2$ and dies at infinity, leaving $y=1$.

**1.6** $\;x=-3$. Accept $2x+6=0$.

**1.7** $\;y=\tfrac23$. Cancelling the constants first —
$\dfrac{2(x+3)}{3(x+2)}$ — hides nothing: the leading coefficients are $2$
and $3$.

**1.8** $\;y=\tfrac32$. *"Must be an equation. Do not accept the $\ne$
sign."*
""")

md(r"""
## 2 · The ones you cannot read off

**2.1** $\;y=\dfrac{\pi}{2}$. As $x\to\pm\infty$ the inside tends to $1$,
so $f(x)\to\arcsin 1=\dfrac{\pi}{2}$. Two marks: one for the limit
argument, one for the equation.

The trap is stopping at the inside. $\dfrac{x^{2}-1}{x^{2}+1}\to 1$ is
true and worth nothing on its own — the asymptote is $\arcsin$ of that, not
that.

**2.2** $\;x=0$. Nothing is a denominator here. The graph of
$g(x)=2\ln x-\ln d$ stops where its domain stops, and $\ln x\to-\infty$ as
$x\to 0^{+}$ whatever $d$ is. The value of $d$ never enters — which is
exactly what the single mark is testing.
""")

md(r"""
## 3 · The oblique one

**3.1** $\;x=-\tfrac23$ and $\;y=\dfrac43x-\dfrac89$, and **there is no
horizontal asymptote.** The numerator's degree is one higher than the
denominator's, so the ratio of the leading coefficients, $\tfrac43$, is the
*gradient* of a slanted line, not a horizontal one. Quoting $y=\tfrac43$
here is the single most common way to lose the part.

The markscheme splits its four marks A1 (the vertical), A1 (the gradient
$\tfrac43$), M1 (a method for the whole line), A1 (the equation) — and then
notes *"Do not award the final A1 if the answer is not given as an
equation."* Long division:

$$\frac{4x^{2}-1}{3x+2}=\frac43x-\frac89+\frac{7/9}{3x+2}.$$

**3.2** $\;y=\dfrac{x}{2}+\dfrac{13}{4}$, so $a=\tfrac12$, $b=\tfrac{13}{4}$.
Three routes, all in the markscheme: divide; or write
$\dfrac{x^{2}-x-12}{2x-15}\equiv\dfrac{x}{2}+b+\dfrac{c}{2x-15}$ and equate
coefficients of $x$, giving $-1=-\tfrac{15}{2}+2b$; or take
$a=\lim\dfrac{f(x)}{x}$ and $b=\lim\left(f(x)-ax\right)$.

The sign in $-1=-\tfrac{15}{2}+2b$ is where the part is lost: dropping the
minus gives $b=-\tfrac{13}{4}$.

**3.3** $\;y=\dfrac{x}{2}-\dfrac{17}{2}$, so $a=\tfrac12$,
$b=-\tfrac{17}{2}$. Same three routes; equating coefficients of $x$ gives
$-14=3+2b$.

**3.4** $\;y=x$, for **every** positive $A$. Part (d)(i) has already done
the division for you: $\dfrac{x(x^{2}-A)}{x^{2}+A}=x-\dfrac{2Ax}{x^{2}+A}$,
and the subtracted term tends to $0$ as $x\to\pm\infty$ because its
denominator has the higher degree. *"Award A0 if not given as an
equation."*
""")

md(r"""
## 4 · Rational sketches

**4.1** Vertical asymptotes $x=\pm\tfrac12$, horizontal asymptote $y=0$,
$x$-intercept $-\tfrac23$, $y$-intercept $-2$, local minimum
$(-1.11,-0.339)$ on the left branch and local maximum $(-0.226,-1.66)$ on
the middle one. Three branches, not two.

The markscheme is worth reading in full: *A1* for both vertical asymptotes
with their equations, *A1* for the horizontal asymptote with its equation,
*A1* for each correct branch including asymptotic behaviour, the
coordinates of the minimum and maximum, and the values of the axes
intercepts — and then *"If vertical asymptotes are absent (or not vertical)
and the branches overlap as a consequence, award maximum A0A1A0A1A1."*
Overlapping branches are the failure this question is built to catch.

**4.2** $x=3$, $y=-2$, $(-2,0)$, $\left(0,\tfrac43\right)$. One mark, for
*"completely correct shape: two branches in correct quadrants with
asymptotic behaviour"*.

**4.3** $x=\tfrac{15}{2}$, $y=\tfrac{x}{2}+\tfrac{13}{4}$, $(-3,0)$,
$(4,0)$, $\left(0,\tfrac45\right)$. Three marks: shape, both asymptotes
with correct asymptotic behaviour, intercepts — and the markscheme adds
*"Points of intersection with the axes and the equations of asymptotes are
not required to be labelled."* Here the drawing itself is the answer.

**4.4** $x=-1$, $y=2$, $\left(\tfrac12,0\right)$, $(0,-1)$. Three marks:
one for the shape with both asymptotes, one for each intercept.

**4.5** Vertical asymptotes $x=-1$ and $x=3$, horizontal asymptote $y=0$,
**no $x$-intercept at all**, $y$-intercept $-\tfrac13$, local maximum
$\left(1,-\tfrac14\right)$.

Two vertical asymptotes cut the line into three pieces, so the curve has
three branches, and the middle one is the only one carrying a turning
point. The maximum sits at $x=1$ because that is the axis of symmetry of
$x^{2}-2x-3$ — which is a legitimate method here and a wrong habit
generally; the markscheme allows *"uses the axis of symmetry or attempts to
solve $f'(x)=0$"*. It then awards *(M1)A0* if the maximum is placed at
$x=1$ without its coordinates.

**4.6** $x=2$, $y=1$, $(3,0)$, $\left(0,\tfrac32\right)$.

**4.7** $x=-3$, $y=\tfrac{x}{2}-\tfrac{17}{2}$, $(2,0)$, $(12,0)$,
$(0,4)$. Four marks, and the first has a condition attached: *"two branches
with approximately correct shape — for this A1 the graph must be a
function."* A curve drawn as a loop earns nothing for shape.

**4.8** Crossings at $(-4,0)$, $(0,0)$, $(4,0)$; local maximum
$(-1.94,1.20)$, local minimum $(1.94,-1.20)$. The curve is odd, which is
why the two turning points are reflections of each other through the
origin.

**4.9** $(-4,0)$, $(0,0)$, $(4,0)$ — and the markscheme adds *"Award A0 if
additional points are given."* The factor $x$ in front is easy to drop, and
dropping it loses the intercept at the origin.

**4.10** $x=0$ and $y=0$; two branches, in the first and third quadrants.
One mark, and it is the setup for the two normals in 6.11.
""")

md(r"""
## 5 · Ranges

**5.1** $\;y\ge-5$. Complete the square: $f(x)=6(x-1)^{2}-5$, so the vertex
is $(1,-5)$ and the parabola opens upwards. The vertex is *attained*, so
the inequality is not strict.

**5.2** $\;g(x)\le\dfrac{5-\sqrt{13}}{6}$ or
$\;g(x)\ge\dfrac{5+\sqrt{13}}{6}$, that is $g(x)\le 0.232$ or
$g(x)\ge 1.43$.

Set $y=\dfrac{2x-5}{x^{2}-3}$ and clear the fraction:
$yx^{2}-2x+(5-3y)=0$. For a real $x$ to exist the discriminant must be
non-negative: $4-4y(5-3y)=12y^{2}-20y+4\ge 0$, whose roots are
$\dfrac{5\pm\sqrt{13}}{6}$. Both ends are attained — they are the turning
points of the curve — so both inequalities are weak, and there is a gap
between them because the two branches never meet.

The calculator route (find the local maximum and minimum) gets the same
answer to 3 s.f. and cannot produce the surd. Both are accepted.

**5.3** $\;y\le-10-5\sqrt3$ or $\;y\ge-10+5\sqrt3$, that is
$y\le-18.7$ or $y\ge-1.34$.

The markscheme: *A1* for each inequality, and then *"Award A1A0 for strict
inequalities in both."* Both ends are turning points of the curve, both are
reached, and writing $<$ costs a mark even though the two numbers are
right. This is the whole reason `verify_range` tests each endpoint
separately.

**5.4** Axis of symmetry $\;x=-5$; minimum point
$\left(-5,\tfrac12\right)$.

With $k=5$ the function is $\tfrac12x^{2}+5x+13$, so the axis is
$x=-\dfrac{b}{2a}=-\dfrac{5}{2\cdot\frac12}=-5$; substituting back gives
$\tfrac12(25)-25+13=\tfrac12$. Completing the square does both at once:
$\tfrac12(x+5)^{2}+\tfrac12$. *"Must be an equation"* against the axis.
""")


md(r"""
## 6 · Labelled sketches

**6.1** $y$-intercept $2$; local maximum $(-1,4)$; local minimum $(1,0)$.
$f'(x)=3x^{2}-3c$ with $c=1$ gives $x=\pm1$, and $f(1)=0$ means the curve
*touches* the axis there rather than crossing it: $x^{3}-3x+2=(x-1)^{2}(x+2)$.

**6.2** $y$-intercept $2$; local maximum
$\left(-\sqrt2,\,2+4\sqrt2\right)=(-1.41,7.66)$; local minimum
$\left(\sqrt2,\,2-4\sqrt2\right)=(1.41,-3.66)$. The markscheme prints the
exact coordinates as an accepted alternative — worth knowing, because the
calculator will not offer them.

**6.3** Endpoints $(1,0)$ and $\left(2,\sqrt3\right)=(2,1.73)$, and the
shape is concave down. Two marks: one for the shape on the given domain,
one for both endpoints. *"The coordinates of endpoints may be seen on the
graph or marked on the axes."*

The domain is given as $1\le x\le 2$ and the curve simply stops there.
Drawing the whole of $\sqrt{x^{2}-1}$ loses the shape mark.

**6.4** The curve crosses the $x$-axis at $x=1$ only — its quadratic factor
$x^{2}-8x+17=(x-4)^{2}+1$ has no real roots — and so does the tangent
$y=x-1$. That coincidence is what the question is about: *"clearly showing
where the tangent crosses the $x$-axis"*, and the markscheme adds *"Award
A1A0 if both graphs cross the $x$-axis at distinctly different points."*

The other mark is for a positive cubic with a local maximum and local
minimum in the first quadrant, both to the left of $\mathrm{A}(4,3)$. The
minimum is at $x=\tfrac{10+\sqrt7}{3}\approx 4.2$ — so close to
$\mathrm{A}$ that the markscheme condones sketches where they appear to
coincide.

**6.5** $x$-intercept $1$, and **no stationary points at all**: the
derivative $3x^{2}-6x+7$ has discriminant $36-84<0$. The curve rises
through a non-stationary point of inflexion at $x=1$.

Drawing a cubic with two turning points because cubics have two is the
trap. The markscheme: *"a positive cubic with no stationary points and a
non-stationary point of inflexion at $x=1$"*, with the note *"graphs may
appear approximately linear; award this A1 if a change of concavity either
side of $x=1$ is apparent."*

**6.6** $x$-intercepts $-2$ and $-1$, $y$-intercept $2$, local maximum
$\left(-\tfrac53,\tfrac{4}{27}\right)$, local minimum $(-1,0)$.

$P(x)=(x+1)^{2}(x+2)$, so $x=-1$ is a double root: the curve *touches* the
axis there, and that touch is the local minimum. The markscheme asks for
the local maximum only to be *"anywhere between $x=-2$ and $x=-1$"* but
insists on the local minimum being at $(-1,0)$.

**6.7** Passes through the origin; local maximum
$\left(1,\tfrac1e\right)=(1,0.368)$; domain $x\ge 0$; single maximum with
$y\to 0$ as $x\to\infty$.

Four separate A1s, and one of them is *for the correct domain* — the family
is defined for $x\ge 0$ and drawing the left half throws a mark away. The
asymptote does not have to be named.

**6.8** Roots $-1.24$ and $2.42$; $y$-intercept $-3$; local minimum
$(\ln 3,\,-3\ln3-1)=(1.10,-4.30)$; endpoints $(-4,8.02)$ and $(3,7.09)$.

Three marks, and the third is *for the endpoints* — with the intervals
spelled out: the left end in $-4.5<x<-3.5$, $7.5<y<8.5$ and the right end
in $2.5<x<3.5$, $6.5<y<7.5$. A sketch that runs off the given window is a
different sketch.

**6.9** $x$-intercepts $-3$ and $-1$, $y$-intercept $15$, vertex
$(-2,-5)$. Part (a) has already written $f$ as $5(x+2)^{2}-5$, which hands
you the vertex; the intercepts are the factors and $f(0)=15$. Four marks:
shape, roots, $y$-intercept, vertex.

**6.10** Local maximum $(-2.70,2.28)$, local minimum $(0.899,-4.19)$, three
$x$-intercepts — two negative and one positive — and the curve is drawn only
on $-4\le x\le 4$.

The particular solution comes first: $2=9+6-3+Ce^{3}$ gives
$C=-10e^{-3}=-0.498$, so $y=x^{2}-2x-3-10e^{-x-3}$. Five marks, of which
one is *for the domain* and one is for the two labelled turning points
together.

**6.11** $x=2$ and $x=-2$: the normal at $x=t$ has gradient $t^{2}$, so
gradient $4$ means $t^{2}=4$. The two normals are $y=4x-\tfrac{15}{2}$ and
$y=4x+\tfrac{15}{2}$, touching $H$ at $\left(2,\tfrac12\right)$ and
$\left(-2,-\tfrac12\right)$.

The markscheme wants two *parallel* lines, each normal to $H$, each with
$c\ne 0$, and it adds: *"for normal lines that cross the $y$-axis, award
A1A0 if the $y$-intercepts are not approximately equidistant from
$\mathrm{O}$"*, and *"maximum A1A0 for a normal line sketched for
$0<m<1$ and a normal line sketched for $m>1$"* — that is, the two lines
must share one $m$, which is the entire point of part (c)(ii).
""")

md(r"""
## 7 · Shape from the second derivative

**7.1** $f''(0)=-4e\approx-10.9$, $f''\!\left(\tfrac{\pi}{2}\right)=\dfrac4e
\approx 1.47$, and the ratio of the magnitudes is $e^{2}\approx 7.39$.

Differentiate twice: $f'(x)=-2\sin(2x)\,e^{\cos 2x}$ and

$$f''(x)=\left(4\sin^{2}(2x)-4\cos 2x\right)e^{\cos 2x}.$$

At $x=0$ the sine vanishes and $\cos 0=1$, leaving $-4e$; at
$x=\tfrac{\pi}{2}$ the sine vanishes again and $\cos\pi=-1$, leaving
$4e^{-1}$.

The sketch: maxima at $(0,e)$ and $(\pi,e)$, minimum at
$\left(\tfrac{\pi}{2},\tfrac1e\right)$ — and the third mark is *"for
showing a higher rate of change of gradient at the maxima and a lower rate
of change of gradient at the minimum point."* Seven times sharper is what
those two numbers mean: two narrow peaks and a long flat trough. The word
*relative* in the question is the whole question.
""")

md(r"""
## 8 · Curves that are not functions

**8.1** The curve passes through the origin and meets the axes nowhere
else; the gradient of the upper branch $y=x^{3/2}$ at the origin is $0$,
and the lower branch arrives with gradient $0$ too, from below. Two zero
gradients meeting head-on is a **cusp** — and the markscheme's two marks
are exactly *"approximately symmetric about the $x$-axis graph of
$y^{2}=x^{3}$"* and *"including cusp/sharp point at $(0,0)$."*

**8.2** $x$-intercept $-1$, $y$-intercepts $1$ and $-1$. Marks for the
symmetric shape *"with approximately correct gradient at axes intercepts"*
and for the positions $x=-1$, $y=\pm 1$.

The two "gradients at the intercepts" are the whole distinction from 8.1,
which is what the next part asks for.

**8.3** $\infty$ — the branch is vertical there. Differentiating
$y^{2}=x^{3}+1$ implicitly, $2y\,y'=3x^{2}$, and at $(-1,0)$ the left side
vanishes while the right does not, so $y'$ is undefined and the tangent is
vertical.

The question wants words, and the markscheme accepts any **two** of:
$y^{2}=x^{3}$ has a cusp and the other does not; the graphs have different
domains; $y^{2}=x^{3}+1$ has points of inflexion and the other does not;
different $x$-intercepts (one goes through the origin, the other does not);
different $y$-intercepts.

**8.4** Any **two** of the eleven the markscheme lists: as $x\to\infty$,
$y\to\pm\infty$; for large $x$ the curve is approximated by $y^{2}=x^{3}$;
one $x$-intercept, at $x=-\sqrt[3]{b}$; two $y$-intercepts, at
$y=\pm\sqrt{b}$; they all have the same range; $y=0$ is a line of symmetry;
one $x$-intercept; two $y$-intercepts; two points of inflexion; vertical
gradient at the $x$-intercept; no cusp at the $x$-intercept.

And the refusal: *"Do not credit an answer of 'they are all symmetrical'
without some reference to the line of symmetry"*, and *"do not allow
same/similar shape"*. A key feature has to be a feature, not an impression.

**8.5** $y^{2}=16-8x$ opens to the **left** from its $x$-intercept $2$;
$y^{2}=4+4x$ opens to the **right** from $-1$. They cross twice, once in
the first quadrant and once in the fourth. Three marks: one for each curve
having approximately the right shape and position, one for the two
$x$-intercepts.

The general result waiting two parts later is that these two families cross
at right angles — which is why the sketch is asked for first.
""")

md(r"""
## 9 · Counting the roots of $y=x^{3}+ax^{2}+b$

The one idea behind all nine parts: the cubic has zero gradient at
$\mathrm{P}(0,b)$ and at
$\mathrm{Q}\!\left(-\tfrac23a,\;\tfrac{4}{27}a^{3}+b\right)$, and it has

* **three** $x$-intercepts when $\mathrm{P}$ and $\mathrm{Q}$ are on
  opposite sides of the axis,
* **two** when one of them is *on* the axis,
* **one** when both are on the same side.

Everything below is that sentence with numbers in it.

**9.1** $b=-4$ and $b=0$. With $a=3$ the two zero-gradient points are
$(0,b)$ and $(-2,4+b)$; they lie on the axis when $b=0$ and when $b=-4$.
Two marks, one of them (M1) for *"varies the value of $b$ with $a=3$"* or
for evidence that the case $b=0$ was considered at all.

**9.2** $b<-4$ or $b>0$. **9.3** $-4<b<0$.

**9.4** $b=0$ and $b=4$. With $a=-3$ the points are $(0,b)$ and $(2,b-4)$.

**9.5** $b<0$ or $b>4$. **9.6** $0<b<4$.

The pair $(9.2,9.3)$ and the pair $(9.5,9.6)$ are the same two answers with
the interval reflected, because changing the sign of $a$ reflects the
family in the $y$-axis.

**9.7** One point of zero gradient is above the $x$-axis and the other is
below it — one on either side. That is the whole mark.

**9.8** Both above. With $a>0$ and $b>0$: $\mathrm{P}=(0,b)$ has $b>0$, and
$\mathrm{Q}$ has height $\tfrac{4}{27}a^{3}+b$, a sum of two positive
numbers. (Part (f)(i) has just shown $\dfrac{d^{2}y}{dx^{2}}=6x+2a$, so
$\mathrm{P}$ is the local minimum and $\mathrm{Q}$ the local maximum — and
if even the minimum is above the axis, the curve crosses once.)

**9.9** Factorise the given quantity:

$$4a^{3}b+27b^{2}=27b\left(\frac{4}{27}a^{3}+b\right)<0 .$$

The two factors are exactly the heights of $\mathrm{P}$ and $\mathrm{Q}$ —
$b$ and $\tfrac{4}{27}a^{3}+b$ — up to the positive constant $27$. Their
product is negative precisely when exactly one of the two heights is
negative, that is when $\mathrm{P}$ and $\mathrm{Q}$ lie on opposite sides
of the $x$-axis; and by 9.7 that happens if and only if the curve has
exactly three $x$-axis intercepts.

Five marks: M1 for attempting the factorisation, A1 for it, A1 for stating
*both* cases ($b>0$ with $\tfrac{4}{27}a^{3}+b<0$, or $b<0$ with
$\tfrac{4}{27}a^{3}+b>0$ — *"only award this A1 if both cases are
stated"*), R1 for opposite signs meaning opposite sides, R1 for opposite
sides meaning three intercepts. Proving the converse instead earns at most
three of the five.
""")

md(r"""
---

**Done.** Fifty-four questions, 127 marks, the whole of the topic as the
archive has it.

What the checks could not see, and you should: the shape of every curve
*between* the features you listed, which is where the sketching marks
divide; the two verbal parts, 8.4 and 9.7; and the proof in 9.9. For those
the solution above is the marker.

If a section came out slow, that section's rung in *Practicum B4* has the
theory, the traps, and the drill items behind it.
""")


NOTEBOOK = os.path.join(ROOT, 'practicum', 'functions',
                        'archive-b4-curve-sketching.ipynb')

DOC = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python",
                       "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}


if __name__ == '__main__':
    with open(NOTEBOOK, 'w') as fh:
        json.dump(DOC, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(f'{NOTEBOOK}: {len(cells)} cells')
