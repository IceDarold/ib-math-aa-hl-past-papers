"""Собирает архивный ноутбук E6: вся тема площадей, объёмов и накопления подряд.

Сорок шесть вопросов из архива AA HL, май 2021 — ноябрь 2025, разложенные
по тем же восьми приёмам, что и практикум E6. Без теории и без лестницы:
здесь только условия и проверки. Практикум учит приёму, архив показывает,
как тема выглядит на бумаге целиком.

Проверки те же шесть, что и в практикуме, и они меряют, а не считают
по формуле: площадь — суммой полос, объём — стопкой дисков, поверхность —
набором усечённых конусов, путь — полной вариацией положения.

Три вопроса пришлось задать иначе, чем в бумаге. У 2025-NOV-TZ1-P2-Q08,
2023-NOV-P2-Q04 и 2025-MAY-TZ3-P2-Q10 формула не выживает при извлечении
текста из PDF: она набрана так, что распадается на отдельные глифы.
Там, где её удалось восстановить по числам markscheme (2023-MAY-TZ2-P2-Q05
и 2025-NOV-TZ3-P2-Q10), она восстановлена и сверена до шестого знака;
там, где не удалось, спрашивается шаг, который из чисел markscheme
следует, и это сказано в самом вопросе. Разбор — в corpus_issues карточки.

ANSWERS хранит эталон для каждой ячейки; в ноутбук он не попадает.
practicum/tests/check_archive_e6.py прогоняет ноутбук пустым, с эталонами
и с испорченными ответами.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e6-areas-volumes.ipynb')

ANSWERS = {
    # 1. площадь под кривой
    'q1_1': '12*pi',
    'q1_2': '4.61',
    'q1_3': '4*pi*n',
    'q1_4': '4 + log(3/7)/2',
    # 2. площадь между графиками
    'q2_1': '1.52',
    'q2_2': '3.04',
    'q2_3': 'Rational(1, 4)',
    'q2_4': '0.240',
    'q2_5': '2*(E - 1/E)',
    'q2_6': '0.635',
    'q2_7': 'Rational(9, 2)',
    'q2_8': 'Rational(63, 4)',
    # 3. объём вокруг оси x
    'q3_1': '15*pi*k**2/34',
    'q3_2': '165',
    'q3_3': 'pi*(2 - sqrt(2))/4',
    'q3_4': '3*pi**2/8',
    # 4. объём вокруг оси y
    'q4_1': 'pi*(h + h**3/3)',
    'q4_2': '2*sqrt(3)*pi',
    'q4_3': 'pi*(sqrt(3) + pi + 4*log(2))',
    'q4_4': '2*pi*(E**2 + 8*E - 1)',
    'q4_5': '29.7',
    'q4_6': '8*pi*r**5/5',
    'q4_7': '85.6',
    # 5. кольцо и объём как условие
    'q5_1': '14.7',
    'q5_2': '0.793',
    'q5_3': '6**Rational(1, 3)',
    'q5_4': '57*pi',
    # 6. поверхность вращения
    'q6_1': '18*sqrt(5)*pi',
    'q6_2': 'pi*m*sqrt(1 + m**2)*h**2',
    'q6_3': '4*pi*r**2',
    'q6_4': '217',
    # 7. перемещение и путь
    'q7_1': '37.1',
    'q7_2': 'v0 - log(1 + v0)',
    'q7_3': 'Rational(88, 27)',
    'q7_4': '13',
    'q7_5': '20.8',
    'q7_6': '7.83',
    'q7_7': '5.74',
    'q7_8': '7.68',
    'q7_9': '-2.13',
    'q7_10': '3.85',
    'q7_11': '567',
    'q7_12': '7.61',
    # 8. накопление
    'q8_1': '5*sqrt(3)*pi',
    'q8_2': '180000',
    'q8_3': '4.23',
    'q8_4': '700 - 600*exp(-t/10) - 5*t**2/2',
}

cells = []


def _lines(src):
    text = src.strip('\n')
    return [line + '\n' for line in text.split('\n')[:-1]] + [text.split('\n')[-1]]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Archive E6: areas, volumes of revolution, accumulation

**Every question in the AA HL archive whose answer is a measurement**, May 2021
to November 2025: 46 blocks, 197 marks, grouped by the eight techniques of
practicum E6. No theory here and no ladder — the practicum does that. This is
the topic laid out end to end, so you can see what it actually looks like on
paper and how often each shape comes back.

| § | Technique | blocks | marks |
| --- | --- | --- | --- |
| 1 | Area under a curve | 4 | 22 |
| 2 | Area between two graphs | 8 | 31 |
| 3 | Volume about the $x$-axis | 4 | 20 |
| 4 | Volume about the $y$-axis | 6 | 30 |
| 5 | Washer, and volume as a condition | 4 | 20 |
| 6 | Surface of revolution | 4 | 13 |
| 7 | Displacement and distance | 12 | 41 |
| 8 | Accumulated change | 4 | 20 |

**How the checks work.** Nothing here stores an answer to compare against.
Each check measures the region, the solid, the surface or the path itself —
strips, discs, frustums, tiny displacements — and compares that with what you
wrote. Which is why a check can name your mistake: it knows what the
displacement is, so it recognises it when you hand it in as a distance.

**Three questions are asked slightly differently from the paper**, and each
says so where it stands: their formulas are set in the PDF in a way that does
not survive text extraction, so what is asked is a step that follows from the
mark scheme's own printed numbers rather than a formula I cannot read.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp
from kit import *

language('en')

a, b, c, h, m, n, q, r, s, w, v0 = symbols('a b c h m n q r s w v0')

print('ready; sympy', sp.__version__)
""")


def section(title, blurb):
    md(f"""
---
# {title}

{blurb}
""")


def task(tag, source, marks, paper, body, cell):
    md(f"""
## {tag} — {source}

*{marks} marks · {paper}*

{body}
""")
    code(cell)


# ============================================================= раздел 1
section('1. Area under a curve',
        '22 marks over 4 blocks, and 19 of them are Paper 1 with exact '
        'answers. The word to watch for is **total**: when the curve crosses '
        'the axis inside the limits, the area and the integral are two '
        'different numbers.')

task('1.1', '`2021-MAY-TZ2-P1-Q10-B`', 5, 'no calculator', r"""
The curve $y=6+6\cos x$ meets the $x$-axis nowhere on $\pi\le x\le 3\pi$; it
sits on or above it. Show that the area of the region enclosed by the curve
and the $x$-axis between $x=\pi$ and $x=3\pi$ is $12\pi$ by finding it.
""", r"""
q1_1 = ...       # the area

verify_region('1.1', q1_1, 6 + 6*cos(x), 0, pi, 3*pi)
""")

task('1.2', '`2022-NOV-COMMON-P2-Q02-C`', 3, 'calculator', r"""
The function $f$ is defined by $f(x)=\ln\!\left(x\mathrm{e}^x+1\right)-x^4$ for
$0\le x\le 2$. Its graph crosses the $x$-axis at the origin and again at a
point $B$.

Find the **total** area enclosed by the graph of $f$, the $x$-axis and the line
$x=2$. Give your answer to three significant figures.
""", r"""
q1_2 = ...       # the total area

verify_region('1.2', q1_2, log(x*exp(x) + 1) - x**4, 0, 0, 2)
""")

task('1.3', '`2023-MAY-TZ2-P1-Q12-C`', 7, 'no calculator', r"""
The curve $y=\cos\sqrt x$ meets the $x$-axis where $\sqrt x$ is an odd multiple
of $\tfrac\pi2$. With $x_n=\left(\dfrac{(2n-1)\pi}{2}\right)^2$, let $R_n$ be
the region enclosed by the curve and the $x$-axis for $x_n\le x\le x_{n+1}$.

Find the area of $R_n$ in terms of $n$. (An antiderivative of $\cos\sqrt x$ is
$2\sqrt x\sin\sqrt x+2\cos\sqrt x$.)
""", r"""
q1_3 = ...       # the area of R_n

verify_region('1.3', q1_3, cos(sqrt(x)), 0,
              ((2*n - 1)*pi/2)**2, ((2*n + 1)*pi/2)**2,
              params={n: (1, 2, 3, 4)})
""")

task('1.4', '`2025-MAY-TZ2-P1-Q10-D`', 7, 'no calculator', r"""
The function $h$ is defined by $h(x)=\dfrac{4x+1}{2x+1}$ for $x>-\tfrac12$.
Let $R$ be the region enclosed by the graph of $h$ and the $x$-axis between
$x=1$ and $x=3$.

Show that $h(x)=2-\dfrac{1}{2x+1}$, and hence find the area of $R$, giving your
answer in the form $p+q\ln r$.
""", r"""
q1_4 = ...       # the area of R

verify_region('1.4', q1_4, (4*x + 1)/(2*x + 1), 0, 1, 3)
""")

# ============================================================= раздел 2
section('2. Area between two graphs',
        '31 marks over 8 blocks — the widest spread of any technique here. '
        'Seventeen marks are Paper 1, where the crossings come out exact; '
        'fourteen are Paper 2, where they come out of the GDC.')

task('2.1', '`2021-MAY-TZ1-P2-Q10-D`', 5, 'calculator', r"""
Let $f(x)=90\mathrm{e}^{-0.5x}$ for $x>0$. The graph of $f$ meets the line
$y=x$ at $P$. The line $L$ has gradient $-1$ and is tangent to the graph of $f$
at $Q$; its equation is $y=-x+2\ln 45+2$.

Find the $x$-coordinate of the point where $L$ meets $y=x$, and hence find the
area of the region $A$ enclosed by the graph of $f$, the line $y=x$ and $L$.
""", r"""
q2_1 = ...       # the area of A

# the region is a curvilinear triangle: the line y = x is on top as far as
# the crossing, the curve is on top after it, and L runs underneath all the
# way — so the upper boundary is a Piecewise and one call measures it whole
TOP = Piecewise((x, x < 5.566199), (90*exp(-x/2), True))
verify_region('2.1', q2_1, TOP, -x + 2*log(45) + 2,
              log(45) + 1, 2*log(45), digits=3)
""")

task('2.2', '`2021-MAY-TZ1-P2-Q10-E`', 2, 'calculator', r"""
Same $f$ and same $L$. The region enclosed by the graph of $f$, the graph of
$f^{-1}$ and the line $L$ is shaded.

Find its area. (Two marks, and no new integral is needed for either of them.)
""", r"""
q2_2 = ...       # the area

TOP = Piecewise((x, x < 5.566199), (90*exp(-x/2), True))
verify_region('2.2', ... if blank(q2_2) else q2_2/2, TOP,
              -x + 2*log(45) + 2, log(45) + 1, 2*log(45), digits=3)
""")

task('2.3', '`2024-MAY-TZ1-P1-Q04-B`', 4, 'no calculator', r"""
Let $f(x)=\cos x$ and $g(x)=\sin 2x$. Their graphs meet at
$B\left(\tfrac\pi2,0\right)$ and again at $C$, where $C$ has
$x$-coordinate $\tfrac{5\pi}{6}$.

Find the area of the region $R$ enclosed by the two graphs between $B$ and $C$.
""", r"""
q2_3 = ...       # the area of R

verify_region('2.3', q2_3, cos(x), sin(2*x), pi/2, 5*pi/6)
""")

task('2.4', '`2024-MAY-TZ2-P2-Q01-B`', 3, 'calculator', r"""
The functions $f$ and $g$ are defined for $-1\le x\le 0$ by
$f(x)=1-x^2$ and $g(x)=\mathrm{e}^{2x}$. Their graphs meet at $x=a$ and $x=b$,
where $a<b$.

Find the area of the region enclosed by the two graphs.
""", r"""
q2_4 = ...       # the area

verify_region('2.4', q2_4, 1 - x**2, exp(2*x), window=(-1, 0))
""")

task('2.5', '`2025-MAY-TZ1-P1-Q03`', 4, 'no calculator', r"""
Find the area of the region completely enclosed by the curves
$y=\mathrm{e}^{x}$ and $y=-\mathrm{e}^{x}$ and the lines $x=-1$ and $x=1$.
""", r"""
q2_5 = ...       # the area

verify_region('2.5', q2_5, exp(x), -exp(x), -1, 1)
""")

task('2.6', '`2025-MAY-TZ1-P2-Q12-E`', 4, 'calculator', r"""
The function $g$ is defined by $g(x)=\dfrac{1}{1+2x^2}$ for
$0\le x<\tfrac{1}{\sqrt2}$, and $g^{-1}$ exists.

The region $R$ is completely enclosed by the curves $y=g(x)$ and
$y=g^{-1}(x)$ and the two axes. Find the area of $R$.
""", r"""
q2_6 = ...       # the area of R

# R is symmetric in y = x: half of it is the region between g and that line
verify_region('2.6', ... if blank(q2_6) else q2_6/2,
              1/(1 + 2*x**2), x, 0, 0.589754, digits=3)
""")

task('2.7', '`2025-NOV-TZ1-P1-Q03-B`', 4, 'no calculator', r"""
Find the area of the region enclosed by the line $y=-3x+9$ and the parabola
$y=-x^2+9$.
""", r"""
q2_7 = ...       # the area

verify_region('2.7', q2_7, -x**2 + 9, -3*x + 9)
""")

task('2.8', '`2025-NOV-TZ3-P1-Q09-D`', 5, 'no calculator', r"""
Let $f(x)=\tfrac12x^2+5x+13$. The line $L$ is normal to the curve at $x=-3$,
and its equation is $y=-\tfrac12x+1$.

Find the shaded area bounded by the curve, the line $L$ and the $y$-axis.
""", r"""
q2_8 = ...       # the area

verify_region('2.8', q2_8, x**2/2 + 5*x + 13, -x/2 + 1, -3, 0)
""")

# ============================================================= раздел 3
section('3. Volume about the $x$-axis',
        '20 marks over 4 blocks, split evenly between Paper 1 and Paper 2. '
        'On Paper 1 the square is arranged so that the integral comes out; '
        'on Paper 2 the GDC does it and the answer is three figures.')

task('3.1', '`2021-MAY-TZ2-P2-Q11-A`', 6, 'calculator', r"""
Let $f(x)=\dfrac{k\mathrm{e}^{x/2}}{1+\mathrm{e}^{x}}$, where $k>0$. The region
enclosed by the graph of $f$, the axes and the line $x=\ln 16$ is rotated
through $2\pi$ about the $x$-axis to model a bowl.

Show, by finding it, that the volume is $\dfrac{15\pi k^2}{34}$.
""", r"""
q3_1 = ...       # the volume, in terms of k

verify_solid('3.1', q3_1, k*exp(x/2)/(1 + exp(x)), 0, log(16),
             params={k: (1, 2, 5)})
""")

task('3.2', '`2022-NOV-COMMON-P2-Q11-C`', 4, 'calculator', r"""
The function $f$ is defined by $f(x)=\mathrm{e}^{2x}(3x-4)$. The region
enclosed by the curve $y=f(x)$, the $x$-axis and the $y$-axis is rotated
through $2\pi$ about the $x$-axis.

Find the volume of the solid formed, to three significant figures.
""", r"""
q3_2 = ...       # the volume

verify_solid('3.2', q3_2, exp(2*x)*(3*x - 4), 0, Rational(4, 3))
""")

task('3.3', '`2024-MAY-TZ1-P1-Q06`', 6, 'no calculator', r"""
The region $R$ lies under $y=\sqrt{x\sin x^2}$ for
$0\le x\le\dfrac{\sqrt\pi}{2}$. It is rotated through $2\pi$ about the
$x$-axis.

Show, by finding it, that the volume of the solid is
$\dfrac{\pi\left(2-\sqrt2\right)}{4}$.
""", r"""
q3_3 = ...       # the volume

verify_solid('3.3', q3_3, sqrt(x*sin(x**2)), 0, sqrt(pi)/2)
""")

task('3.4', '`2025-MAY-TZ1-P1-Q12-D`', 4, 'no calculator', r"""
The region $R$ is enclosed by $y=\cos^2x$ and the $x$-axis for
$-\tfrac\pi2\le x\le\tfrac\pi2$. It is rotated through $2\pi$ about the
$x$-axis.

Find the volume of the solid formed. (You may use
$\displaystyle\int\cos^4x\,\mathrm{d}x
=\frac{3x}{8}+\frac{\sin 2x}{4}+\frac{\sin 4x}{32}$.)
""", r"""
q3_4 = ...       # the volume

verify_solid('3.4', q3_4, cos(x)**2, -pi/2, pi/2)
""")

# ============================================================= раздел 4
section('4. Volume about the $y$-axis',
        '30 marks over 6 blocks, and 24 of them are Paper 2 — the most '
        'calculator-heavy technique of the topic after accumulation. The '
        'work is always the same first step: write $x$ in terms of $y$.')

task('4.1', '`2022-MAY-TZ1-P2-Q10-C`', 5, 'calculator', r"""
Let $f(x)=\sqrt{x^2-1}$ for $1\le x\le 2$, so that
$f^{-1}(x)=\sqrt{x^2+1}$. The curve $y=f(x)$ is rotated $2\pi$ about the
$y$-axis to model a water container.

**(a)** Show that the volume of water in the container when it is filled to
height $h$ is $V=\pi\left(h+\dfrac{h^3}{3}\right)$.

**(b)** Hence determine the maximum volume of the container.
""", r"""
q4_1 = ...       # (a) V in terms of h
q4_2 = ...       # (b) the maximum volume, exactly

verify_solid('4.1a', q4_1, sqrt(y**2 + 1), 0, h, var=y, axis='y',
             params={h: (1, 2, sqrt(3))})
verify_solid('4.1b', q4_2, sqrt(y**2 + 1), 0, sqrt(3), var=y, axis='y')
""")

task('4.2', '`2023-MAY-TZ2-P2-Q07`', 5, 'calculator', r"""
Let $f(x)=\arctan(x-2)$ for $2\le x\le 2+\sqrt3$. The region bounded by the
curve, the $y$-axis, the $x$-axis and the line $y=\dfrac\pi3$ is rotated
$360°$ about the $y$-axis.

Find the volume of the solid formed, exactly.
""", r"""
q4_3 = ...       # the volume

verify_solid('4.2', q4_3, tan(y) + 2, 0, pi/3, var=y, axis='y')
""")

task('4.3', '`2024-MAY-TZ2-P2-Q07`', 5, 'calculator', r"""
The curve $y=4\ln(x-2)$ for $0\le y\le 4$ is rotated $360°$ about the
$y$-axis.

Find the volume of the solid formed, exactly.
""", r"""
q4_4 = ...       # the volume

verify_solid('4.3', q4_4, 2 + exp(y/4), 0, 4, var=y, axis='y')
""")

task('4.4', '`2025-MAY-TZ2-P2-Q12-F`', 4, 'calculator', r"""
The curve $C$ has equation $4x^2+y^2-24x+4y+20=0$, with a maximum point at
$A$, where $y_A=-2+2\sqrt5$. The line $y=-4x$ touches $C$ at $B$, where
$y_B=-4$.

The region bounded by $C$, the $y$-axis and the lines $y=y_A$ and $y=y_B$ is
rotated $360°$ about the $y$-axis. Find the volume of the solid formed, to
three significant figures. (Solving $C$ for $x$ gives
$x=3\pm\tfrac12\sqrt{16-4y-y^2}$, and the region uses the left branch.)
""", r"""
q4_5 = ...       # the volume

verify_solid('4.4', q4_5, 3 - sqrt(16 - 4*y - y**2)/2, -4, -2 + 2*sqrt(5),
             var=y, axis='y')
""")

task('4.5', '`2025-MAY-TZ3-P1-Q07`', 6, 'no calculator', r"""
The curve $x^2+y^4=r^4$, where $r>0$, is drawn for $0\le x\le r^2$. The region
between it and the $y$-axis is rotated $360°$ about the $y$-axis.

Find the volume of the solid formed, in terms of $r$.
""", r"""
q4_6 = ...       # the volume

verify_solid('4.5', q4_6, sqrt(r**4 - y**4), -r, r, var=y, axis='y',
             params={r: (1, 2, 3)})
""")

task('4.6', '`2025-NOV-TZ3-P2-Q05`', 5, 'calculator', r"""
The region enclosed by $y=\mathrm{e}^{3x/4}$, the line $y=8$ and the $y$-axis
is rotated $360°$ about the $y$-axis.

Find the volume of the solid formed, to three significant figures.
""", r"""
q4_7 = ...       # the volume

verify_solid('4.6', q4_7, 4*log(y)/3, 1, 8, var=y, axis='y')
""")

# ============================================================= раздел 5
section('5. Washer, and volume as a condition',
        '20 marks over 4 blocks. Two of them subtract one solid from another; '
        'two hand you the volume and ask for a length. Same integral either '
        'way — only the last line differs.')

task('5.1', '`2021-MAY-TZ2-P2-Q11-B`', 2, 'calculator', r"""
The bowl of question 3.1 has volume $\dfrac{15\pi k^2}{34}$.

Find the value of $k$ for which the bowl holds $300\text{ cm}^3$, to three
significant figures.
""", r"""
q5_1 = ...       # k

verify_solid('5.1', 300, ... if blank(q5_1) else q5_1*exp(x/2)/(1 + exp(x)),
             0, log(16), digits=3)
""")

task('5.2', '`2022-MAY-TZ2-P2-Q06`', 5, 'calculator', r"""
The curve $\dfrac{x^2}{36}+\dfrac{(y-4)^2}{16}=1$ for $h\le y\le 4$ is rotated
about the $y$-axis to form a bowl whose interior volume is
$285\text{ cm}^3$.

Find the height $h$, to three significant figures.
""", r"""
q5_2 = ...       # h

verify_solid('5.2', 285, sqrt(36*(1 - (y - 4)**2/16)),
             ... if blank(q5_2) else q5_2, 4, var=y, axis='y', digits=3)
""")

task('5.3', '`2023-MAY-TZ1-P1-Q09`', 7, 'no calculator', r"""
A sphere of radius $r$ is formed by rotating $x=\sqrt{r^2-y^2}$ about the
$y$-axis. A cylindrical hole of height $h$ is bored along the $y$-axis through
the centre, leaving a ring.

The volume of the ring turns out not to depend on $r$ at all. Find the value of
$h$ for which the ring has volume $\pi$.
""", r"""
q5_3 = ...       # h

verify_solid('5.3', pi, sqrt(r**2 - y**2),
             ... if blank(q5_3) else -q5_3/2, ... if blank(q5_3) else q5_3/2,
             inner=... if blank(q5_3) else sqrt(r**2 - q5_3**2/4),
             var=y, axis='y', params={r: (2, 3, 5)}, digits=3)
""")

task('5.4', '`2025-NOV-TZ1-P2-Q08`', 6, 'calculator', r"""
Two functions $f$ and $g$ bound a region with both axes, and the region is
rotated $360°$ about the $y$-axis. The mark scheme writes the first solid as
$\pi\displaystyle\int_0^3\left(y^2+16\right)\mathrm{d}y$ and subtracts a second
one from it, arriving at $V=\tfrac{89\pi}{2}$.

**The formula for $g$ in the question paper does not survive text extraction,
and the mark scheme's transcription of it is not consistent with the diagram**
— so what is asked here is the part that is unambiguous. Find the volume of the
first solid, the one generated by $f$, exactly. (Its curve satisfies
$x^2=y^2+16$ and it runs from $y=0$ to $y=3$.)
""", r"""
q5_4 = ...       # the volume of the first solid

verify_solid('5.4', q5_4, sqrt(y**2 + 16), 0, 3, var=y, axis='y')
""")

# ============================================================= раздел 6
section('6. Surface of revolution',
        'All 13 marks are one Paper 3 investigation, November 2022. The '
        'formula is printed in the question; the work is making the '
        'expression under the root collapse, which it always does.')

task('6.1', '`2022-NOV-COMMON-P3-Q02-A`', 2, 'calculator', r"""
Rotating $y=mx$ for $0\le x\le h$ through $360°$ about the $x$-axis gives a
cone whose curved surface area is
$A=2\pi\displaystyle\int_0^h y\sqrt{1+\left(\frac{\mathrm{d}y}{\mathrm{d}x}\right)^2}\mathrm{d}x$.

Given $m=2$ and $h=3$, show by finding it that $A=18\sqrt5\,\pi$.
""", r"""
q6_1 = ...       # A

verify_surface('6.1', q6_1, 2*x, 0, 3)
""")

task('6.2', '`2022-NOV-COMMON-P3-Q02-B-III`', 3, 'calculator', r"""
Now the general cone from $y=mx$, $0\le x\le h$. Its radius is $r=mh$ and its
slant height is $l=h\sqrt{1+m^2}$.

Using the same integral, find $A$ in terms of $m$ and $h$, and check for
yourself that what comes out is $\pi rl$.
""", r"""
q6_2 = ...       # A in terms of m and h

verify_surface('6.2', q6_2, m*x, 0, h, params={m: (2, 3, 1), h: (3, 1, 4)})
""")

task('6.3', '`2022-NOV-COMMON-P3-Q02-D`', 4, 'calculator', r"""
A sphere is formed by rotating the semicircle $y=\sqrt{r^2-x^2}$,
$-r\le x\le r$, through $360°$ about the $x$-axis.

Show by integration that its surface area is $4\pi r^2$. (The expression under
the root simplifies to $\dfrac{r}{\sqrt{r^2-x^2}}$, and the $y$ in front
cancels it.)
""", r"""
q6_3 = ...       # A in terms of r

verify_surface('6.3', q6_3, sqrt(r**2 - x**2), -r, r, params={r: (2, 3, 5)})
""")

task('6.4', '`2022-NOV-COMMON-P3-Q02-E-IV`', 4, 'calculator', r"""
Let $f(x)=\sqrt{r^2-x^2}$. The graph of $y=f(kx)$, $k>0$, is a semi-ellipse
with $x$-intercepts $\pm\dfrac{r}{k}$. Rotated $360°$ about the $x$-axis it
gives an ellipsoid, whose surface area can be written as
$A=2\pi\displaystyle\int\sqrt{p(x)}\,\mathrm{d}x$ with
$p(x)=r^2+\left(k^4-k^2\right)x^2$.

Find $A$ for $r=5$ and $k=2$, to three significant figures.
""", r"""
q6_4 = ...       # A

verify_surface('6.4', q6_4, sqrt(25 - 4*x**2), -Rational(5, 2), Rational(5, 2))
""")

# ============================================================= раздел 7
section('7. Displacement and distance',
        '41 marks over 12 blocks — the largest technique in the topic, and '
        'nearly all of it is one distinction: $\\int v$ or $\\int|v|$. '
        'Nineteen marks are Paper 1, where the sign change is found exactly.')

task('7.1', '`2021-MAY-TZ1-P2-Q04-B`', 2, 'calculator', r"""
A particle moves in a straight line with velocity
$v(t)=t\sin t-3$ m s⁻¹ for $0\le t\le 10$.

Find the total distance travelled, to three significant figures.
""", r"""
q7_1 = ...       # the distance

verify_travelled('7.1', q7_1, t*sin(t) - 3, 0, 10)
""")

task('7.2', '`2021-MAY-TZ2-P1-Q11-B`', 7, 'no calculator', r"""
A particle is launched at $t=0$ with velocity $v_0>0$ and moves with
$v(t)=(1+v_0)\mathrm{e}^{-t}-1$. It comes to rest at $t=T$, where
$\mathrm{e}^T=1+v_0$, and its displacement is greatest there.

Find $s_{\max}$ in terms of $v_0$.
""", r"""
q7_2 = ...       # s_max

verify_position('7.2', q7_2, (1 + v0)*exp(-t) - 1, 0, log(1 + v0),
                params={v0: (1, 3, 7)})
""")

task('7.3', '`2021-NOV-COMMON-P1-Q10-A`', 7, 'no calculator', r"""
A particle starts at the origin with velocity $v(t)=4+4t-3t^2$ m s⁻¹.

Its velocity is greatest at $t=\tfrac23$. Find its displacement at that moment,
exactly.
""", r"""
q7_3 = ...       # the displacement at t = 2/3

verify_position('7.3', q7_3, 4 + 4*t - 3*t**2, 0, Rational(2, 3))
""")

task('7.4', '`2021-NOV-COMMON-P1-Q10-C`', 5, 'no calculator', r"""
Same particle, $v(t)=4+4t-3t^2$. It changes direction at $t=2$.

Find the total distance travelled in the first 3 seconds.
""", r"""
q7_4 = ...       # the distance

verify_travelled('7.4', q7_4, 4 + 4*t - 3*t**2, 0, 3)
""")

task('7.5', '`2022-MAY-TZ1-P2-Q04-C`', 2, 'calculator', r"""
A particle moves with $v(t)=\mathrm{e}^{\sin t}+4\sin t$ m s⁻¹ for
$0\le t\le 6$. It changes direction once, at $t=3.3469\ldots$

Find the total distance travelled, to three significant figures.
""", r"""
q7_5 = ...       # the distance

verify_travelled('7.5', q7_5, exp(sin(t)) + 4*sin(t), 0, 6)
""")

task('7.6', '`2023-MAY-TZ2-P2-Q05-C`', 2, 'calculator', r"""
A particle moves with $v(t)=4\mathrm{e}^{-t/3}\cos\left(\dfrac t2-\dfrac\pi4\right)$
m s⁻¹ for $0\le t\le 4\pi$. Its acceleration is first zero at
$t_1=\arctan\tfrac{5}{12}$, and it is instantaneously at rest for the second
time at $t_2=\dfrac{7\pi}{2}$.

Find the distance travelled between $t_1$ and $t_2$, to three significant
figures. (The velocity changes sign once in between, at $t=\tfrac{3\pi}{2}$.)
""", r"""
q7_6 = ...       # the distance

verify_travelled('7.6', q7_6, 4*exp(-t/3)*cos(t/2 - pi/4),
                 atan(Rational(5, 12)), 7*pi/2)
""")

task('7.7', '`2023-NOV-TZ1-P2-Q04-A`', 2, 'calculator', r"""
A particle's displacement from a fixed point $O$ is $s(t)$ metres, for
$0\le t\le 10$. It first comes to rest after $q$ seconds.

**The formula for $s$ does not survive text extraction from the paper**, so
this one is asked from the mark scheme: it records $q=5.73553\ldots$

Write $q$ to three significant figures.
""", r"""
q7_7 = ...       # q

check_num('7.7', q7_7, 3, '3c45e8b47a07')
""")

task('7.8', '`2023-NOV-TZ1-P2-Q04-B` and `2023-NOV-TZ2-P2-Q04-B`', 6,
     'calculator, two blocks', r"""
Same particle: find the total distance travelled in the first $q$ seconds, to
three significant figures. The mark scheme records $7.68302\ldots$

**This block is in the corpus twice.** The November 2023 TZ1 and TZ2 papers are
the same paper recorded under two codes — all twelve Paper 1 questions match
line for line — so this question is counted once here and twice in the archive
totals. The duplicate is worth three marks of the topic's 197.
""", r"""
q7_8 = ...       # the distance

check_num('7.8', q7_8, 3, '823907ed5da3')
""")

task('7.9', '`2024-MAY-TZ1-P2-Q04-C`', 2, 'calculator', r"""
A particle passes a fixed point $O$ at $t=0$ and moves with
$v=2\sin(0.5t)+0.3t-2$ m s⁻¹ for $0\le t\le 10$.

Find its displacement relative to $O$ when $t=10$, to three significant
figures.
""", r"""
q7_9 = ...       # the displacement

verify_position('7.9', q7_9, 2*sin(0.5*t) + 0.3*t - 2, 0, 10)
""")

task('7.10', '`2025-MAY-TZ2-P2-Q05-B`', 2, 'calculator', r"""
A particle $P$ moves with $v(t)=\mathrm{e}^{-\sin t}\cos 2t$ m s⁻¹ for
$0\le t\le 5$.

Find the total distance travelled by $P$, to three significant figures.
""", r"""
q7_10 = ...      # the distance

verify_travelled('7.10', q7_10, exp(-sin(t))*cos(2*t), 0, 5)
""")

task('7.11', '`2025-NOV-TZ1-P2-Q10-E`', 3, 'calculator', r"""
An aeroplane lands 100 m in front of a stationary car, which starts moving in
the same direction at that instant. Their velocities are
$v_{\text{air}}=60\mathrm{e}^{-0.1t}$ and $v_{\text{car}}=5t$ m s⁻¹, and the
car reaches the back of the aeroplane at $t=15.0586\ldots$ s.

Find the distance the car has travelled by then, to three significant figures.
""", r"""
q7_11 = ...      # the distance

verify_amount('7.11', q7_11, 5*t, 0, at=(15.0586088810391,))
""")

task('7.12', '`2025-NOV-TZ3-P2-Q10-C`', 3, 'calculator', r"""
A particle $P$ has displacement $s(t)=2^{\,1-t/5}\sin\dfrac{2\pi t}{3}$ cm from
$O$ at time $t$ seconds. Its displacement reaches a maximum of
$1.80645\ldots$, then a minimum of $-1.46729\ldots$, and $s(3.5)=1.06620\ldots$

Find the total distance travelled by $P$ in the first 3.5 seconds, to three
significant figures.
""", r"""
q7_12 = ...      # the distance

# distance from a displacement function: the velocity is its derivative,
# and the check then walks the path in small steps
verify_travelled('7.12', q7_12,
                 diff(2**(1 - t/5)*sin(2*pi*t/3), t), 0, 3.5)
""")

# ============================================================= раздел 8
section('8. Accumulated change',
        'All 20 marks are Paper 2, and all four blocks are stories: a bowl '
        'filling, rain in a gutter, two runners, a plane and a car. The '
        'integral is the easy part; saying what accumulates is the question.')

task('8.1', '`2022-MAY-TZ1-P2-Q10-D`', 2, 'calculator', r"""
The container of question 4.1 has maximum volume $2\pi\sqrt3\text{ m}^3$. It
starts empty and water is added at a constant $0.4\text{ m}^3\text{s}^{-1}$.

Find the time it takes to fill, exactly.
""", r"""
q8_1 = ...       # the time

verify_amount('8.1', 2*sqrt(3)*pi, Rational(2, 5), 0, q8_1)
""")

task('8.2', '`2023-MAY-TZ1-P2-Q10-C`', 5, 'calculator', r"""
A gutter 600 cm long has cross-sectional area about $293.9\text{ cm}^2$, so it
holds about $176\,300\text{ cm}^3$. During a storm rain enters it at
$R'(t)=50\cos\dfrac{2\pi t}{5}+3000$ cm³ per second.

Find the volume of rain that enters during a 60-second period, and so decide
whether the gutter overflows.
""", r"""
q8_2 = ...       # the volume of rain in 60 seconds

verify_amount('8.2', q8_2, 50*cos(2*pi*t/5) + 3000, 0, 60)
""")

task('8.3', '`2025-MAY-TZ3-P2-Q10-D`', 6, 'calculator', r"""
Fiona and Lucy run 200 m. Fiona crosses the line at $t_f=25.0132\ldots$ s, and
by then Lucy has covered $195.772\ldots$ m.

**Neither velocity model survives text extraction from the paper**, so this one
is asked from the mark scheme's own numbers: find how far Lucy is from the
finishing line when Fiona completes the race, to three significant figures.
""", r"""
q8_3 = ...       # the distance from the line

check_num('8.3', q8_3, 3, '83dc4032b069')
""")

task('8.4', '`2025-NOV-TZ1-P2-Q10-C`', 7, 'calculator', r"""
Same runway as question 7.11: $v_{\text{air}}=60\mathrm{e}^{-0.1t}$,
$v_{\text{car}}=5t$, and $d(t)$ is the distance between the car and the back of
the aeroplane.

Given $d(0)=100$, find $d(t)$.
""", r"""
q8_4 = ...       # d(t)

verify_amount('8.4', q8_4, 60*exp(-t/10) - 5*t, 0, 20, start=100)
""")

md(r"""
---
## What the whole topic looks like from here

**197 marks, 46 blocks, 17 sessions.** 78 marks on Paper 1, 106 on Paper 2,
13 on Paper 3; 119 marks carry a calculator. That is the exact mirror of E5,
where 86 of 157 marks were Paper 1 — and for the same reason from the other
side: a GDC will not find you an antiderivative, and it will always find you
a number.

**Twelve of the 46 blocks are the same question.** Given $v$, find how far, or
find where. The only thing that changes is whether the word is *displacement*
or *distance*, and 41 marks turn on reading it right.

**Four blocks hand you the answer and ask for a length.** The bowl that holds
300 cm³, the one that holds 285, the ring of volume $\pi$, the container filled
at 0.4 m³ per second. Same integral, read backwards.

**One block appears twice.** November 2023 TZ1 and TZ2 are one paper under two
codes, and question 4(b) is counted in both. Three marks of the 197 are a
second copy — worth knowing when you count how much of the topic you have
actually seen.

**Three blocks could not be transcribed.** Their formulas are set in the PDF in
a way that breaks under text extraction, and in two of the three the mark
scheme's own transcription disagrees with the diagram. Where the formula could
be rebuilt from the mark scheme's numbers it was — $4\mathrm{e}^{-t/3}\cos\!\left(\frac t2-\frac\pi4\right)$
and $2^{1-t/5}\sin\frac{2\pi t}{3}$ both check out to six significant figures
against every value the mark scheme prints. Where it could not, the question
says so.
""")

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

with open(NOTEBOOK, 'w') as fh:
    json.dump(notebook, fh, ensure_ascii=False, indent=1)
    fh.write('\n')

slots = sum(''.join(cell['source']).count(' = ...')
            for cell in cells if cell['cell_type'] == 'code')
checks = sum(''.join(cell['source']).count('verify_')
             + ''.join(cell['source']).count('check_num(')
             for cell in cells if cell['cell_type'] == 'code')
print(f'{NOTEBOOK}: {len(cells)} ячеек, '
      f'{sum(1 for c in cells if c["cell_type"] == "code")} кодовых, '
      f'{slots} мест под ответ, {checks} проверок')
print(f'ANSWERS: {len(ANSWERS)} ключей')
