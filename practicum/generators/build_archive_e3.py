"""Собирает архивный ноутбук E3: техника дифференцирования, вся тема подряд.

Шестой ноутбук в формате, опробованном на B4, C3, B5, E1 и E2. Практикум E3
учит — лестница, теория, уровни, тренажёр. Этот не учит, он даёт набивать
руку: вопрос, ячейка для ответа с мгновенной проверкой, разбор в конце.

Внутри — та часть calculus.differentiation, где спрашивают саму производную:
55 вопросов и 188 баллов, разложенные по девяти приёмам карточки
calculus-differentiation.yaml. Оставшиеся 43 блока темы ушли в E4 (производная
как наклон) и в E9 (производная как скорость); разрез поимённый, списки
лежат в blocks карточек.

Почему проверок здесь получается больше, чем вопросов. Тема устроена так,
что половина вопросов — «show that f′(x) = …» с напечатанным ответом.
В E2 такие вопросы оставались без ячейки: ряд там надо было угадать, и
напечатанный ответ отвечать было нечем. Здесь иначе. Написать производную
и есть вся работа; ячейка не сторожит, а сообщает, сошлась ли алгебра,
и потому стоит даже там, где ответ виден в условии. Без ячейки остаются
четыре вопроса, у которых сдавать нечего: два «покажите, что сумма равна
такой-то сумме», одна перестановка равенства и одно неравенство.

Эталон хранится в трёх местах из пятидесяти пяти: набор корней в 9.1
(хеш), 2|a| в 8.3 и 1/r в 7.6. Всё остальное проверка получает из условия —
verify_derivative дифференцирует функцию сама, verify_stationary сканирует
производную по отрезку, verify_constants подставляет числа в условия
вопроса, verify_param_set опрашивает неравенство в пробных точках.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_e3.py прогоняет весь ноутбук
с заполненными ответами и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest

R = sp.Rational
x = sp.Symbol('x')
a, b, c, m, n, r = sp.symbols('a b c m n r')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e3-differentiation.ipynb')

# Единственный хеш: набор из трёх корней с буквой внутри. Подставить его
# некуда — уравнение f′ = 0 здесь записано через n, и численно опросить
# его нельзя, — а срепр набора канонизируется так же, как в check_set.
D_91 = digest('|'.join(sorted(sp.srepr(sp.simplify(v))
                              for v in (sp.Integer(0), a / 2, a))))

ANSWERS = {
    'q1_1': '-2*(x - h)',
    'q1_2': '3*x**2 - 3*c',
    'q1_3': 'Rational(1, 16) + Rational(3, 8)*t + Rational(15, 16)*t**2 + Rational(7, 4)*t**3',
    'q2_1': '500*sec(theta)*tan(theta) - 1000*sec(theta)**2/3',
    'q2_2': '3*sec(alpha)*tan(alpha)/4 - 6*cosec(alpha)*cot(alpha)',
    'q2_3': '(exp(t) + exp(-t))/2',
    'q3_1': '-2*E**2',
    'q3_2': '2/(2 - x)**3',
    'q3_3': '-x/sqrt(r**2 - x**2)',
    'q3_4': '-cosec(2*x)',
    'q3_5': '-1/(x*log(200/x))',
    'q3_6': 'cos(sin(sin(x)))*cos(sin(x))*cos(x)',
    'q3_7': '2*E**2',
    'q4_1': '(6*x - 5)*exp(2*x)',
    'q4_2': 'n*x**(n - 1)*(a - 2*x)*(a - x)**(n - 1)',
    'q4_3': '2*(x - r)*(x - a) + x**2 - 2*a*x + a**2 + b**2',
    'q4_4': '(9 - 3*x - 2*x**2)/sqrt(9 - x**2)',
    'q5_1': '(-12*x**2 - 16*x - 3)/(4*x**2 - 1)**2',
    'q5_2': '2*(x - a + 15)*(2*x + a)**2/(x + 5)**3',
    'q5_3': '1',
    'q5_4': '2*x/(sqrt(x**2)*(1 + x**2))',
    'q5_5': '(n*x**(n + 1) - (n + 1)*x**n + 1)/(x - 1)**2',
    'q6_1': '4*x/(2 - x)**3',
    'q6_2': '4*x/(2 - x)**3',
    'q6_4': '0',
    'q7_1': '-1/(4*(1 + x)**Rational(3, 2))',
    'q7_2': '-2*exp(x)*sin(x)',
    'q7_3a': ('3*(sec(alpha)*tan(alpha)**2 + sec(alpha)**3)/4'
              ' + 6*(cosec(alpha)*cot(alpha)**2 + cosec(alpha)**3)'),
    'q7_3b': '45*sqrt(5)/4',
    'q7_4': '12*x**2 - 18*x',
    'q7_5': '-r**2/(r**2 - x**2)**Rational(3, 2)',
    'q7_6': '1/r',
    'q8_1': '-k**2*x/sqrt(r**2 - k**2*x**2)',
    'q8_2': '-b/(2*a)',
    'q8_3': '2*Abs(a)',
    'q8_4': '4',
    'q8_5': 'sqrt(2)/2',
    'q8_6': '2*sqrt(3)/9',
    'q8_7a': '-log(2)/2',
    'q8_7b': '2*sqrt(3)/9',
    'q8_8': '12*x**2 - 4*(a + b)*x + a*b',
    'q8_9': 'm/2',
    'q9_1': '[0, a/2, a]',
    'q9_3a': '-4*sin(2*x)',
    'q9_3b': '[(0, 1), (pi/2, -3), (pi, 1)]',
    'q9_4': '[(0, E), (pi/2, exp(-1)), (pi, E)]',
    'q9_5': '[(1, 1)]',
    'q9_6': 'Union(Interval.open(-oo, -1.74), Interval.open(0.518, oo))',
    'q9_7': 'Interval.open(-oo, log(Rational(2, 3)))',
    'q9_8': '[-5, 1]',
    'q9_9': '[-2]',
    'q9_10': '[(0, 0), (Rational(3, 2), Rational(-9, 16))]',
    'q9_11': '[3, -11, 8]',
    'q9_12': '[(pi/2, sin(1)), (3*pi/2, -sin(1))]',
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
# E3 archive: differentiating

**Every past-paper question in which the answer is a derivative, grouped by
technique.** Not a practicum — a drill. There is no theory here and no ladder
to climb: the theory is in *Practicum E3*, and this notebook is what you open
afterwards, when the only thing left is to do them all until the moves are
automatic.

**What is inside.** The part of `calculus.differentiation` that asks for the
derivative itself, sessions May 2021 — November 2025: **55 questions, 188
marks**, in nine sections, one section per technique.

The whole topic is 98 blocks and 350 marks — twice the size a practicum is
allowed to be. It is cut in three by what the question asks for, not by what
the function looks like. *Find $f'(x)$* is here. *Find the tangent* is E4,
together with everything that turns the derivative into a gradient and
everything given by an equation rather than a formula. *Find the acceleration*
is E9. One archive question is therefore sometimes split: in May 2022 Paper 3,
part (d)(i) asks you to show what $g'(x)$ is and lives here, while (d)(ii)
builds the tangent from it and lives in E4.

**Thirty-four of the fifty-five are Paper 3.** This topic lives inside the
long investigations, and that is not an accident: there the derivative is
taken not for its own sake but for the next part. Twenty-nine of the 188
marks are one May 2025 investigation about curvature, and ten more are a
November 2022 one about surfaces of revolution.

**73% of the marks carry a calculator, and almost none of them need one.**
Genuine GDC work in this topic comes to about 15 marks out of 188: two roots
of an inequality in May 2025 TZ2, two values of $a$ in May 2025 TZ3, and a
system of three linear equations in May 2024 TZ2. Everything else is done on
paper with the calculator sitting there switched on.

**How to work.** Read the question, answer in the cell below it, run the cell.
Almost none of the checks here know the answer. `verify_derivative` takes the
function out of the question and differentiates it — a derivative is not
something to be guessed, it is computed, and any equivalent way of writing it
is accepted. When your answer is wrong it does more than say so: it rebuilds
the standard slips out of that same function — the chain factor left off, the
product done as $u'v'$, the quotient sign the wrong way round, the power not
dropped — and if what you wrote is one of them, it says which.
`verify_stationary` scans the derivative across the interval from the question
and catches both the missing second coordinate and the missing point.
`verify_constants` puts your numbers back into the conditions the question
states. `verify_param_set` asks the inequality itself, at points inside your
set and outside it.

**Three answers out of fifty-five are stored**: the three roots in 9.1 (a
hash), $2|a|$ in 8.3 and $1/r$ in 7.6. The other fifty-two are worked out
from the question every time you run the cell.

**Half the questions here print their own answer** — *show that
$f'(x)=\dots$* — and they still have a cell. That is a change from the E2
archive, where a printed answer meant no cell at all. The reason is that here
the printed thing **is** the work: writing the derivative down is the entire
question, and typing it tells you at once whether your algebra landed on it.
The cell is not guarding anything; it is answering you.

**Four questions have no cell**, because there is nothing to hand over: two
*show that this sum equals that sum*, one rearrangement of an identity, and
one inequality. Read them, do them on paper, read the solution.

Leave a cell blank and it prints ⬜ and moves on, so you can run the whole
notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The power rule, term by term | 5 | 7 |
| 2 | The ones you have to know | 3 | 10 |
| 3 | The chain rule | 7 | 18 |
| 4 | The product rule | 4 | 14 |
| 5 | The quotient rule | 5 | 22 |
| 6 | Getting to the printed line | 4 | 10 |
| 7 | Second and higher derivatives | 6 | 29 |
| 8 | A letter in the function | 9 | 27 |
| 9 | Reading the derivative | 12 | 51 |

Sections 1–5 pick the rule, and picking it is done by looking at the shape of
the function before you write anything. Section 6 is the algebra that gets you
from your line to the printed one, which is where most of the lost marks in
this topic actually are. Sections 7–8 iterate and generalise. Section 9 is
worth 51 of the 188 marks on its own: the derivative is already there and the
question is what it *says*.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, diff, Abs

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d, h, m, n, p, q, r = symbols('a b c d h m n p q r')
alpha, theta = symbols('alpha theta')

print('ready; sympy', sp.__version__)
print('a derivative:        ', 2/(2 - x)**3)
print('with a letter in it: ', -k**2*x/sqrt(r**2 - k**2*x**2))
print('an exact value:      ', 45*sqrt(5)/4)
print('a pair of points:    ', [(0, E), (pi/2, exp(-1))])
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. The power rule, term by term

$$\frac{\mathrm{d}}{\mathrm{d}x}\,x^{n}=n\,x^{n-1}$$

A sum is differentiated one term at a time, and a constant term disappears
altogether. Everything else in this notebook is built on top of this, so the
five questions here are the cheapest marks in the topic — and the place where
a lost constant costs a whole answer.
""")

md(r"""
### 1.1 — *May 2021 TZ1 Paper 1 Q4(a), 1 mark*

Consider the functions $f(x)=-(x-h)^{2}+2k$ and $g(x)=\mathrm{e}^{x-2}+k$,
where $h,k\in\mathbb{R}$.

Find $f'(x)$.
""")

code(r"""
q1_1 = ...

verify_derivative('1.1', q1_1, -(x - h)**2 + 2*k)
""")

md(r"""
### 1.2 — *May 2021 TZ1 Paper 3 Q1(b), 1 mark*

Consider the function $f(x)=x^{3}-3cx+2$ for $x\in\mathbb{R}$, where $c$ is
a parameter, $c\in\mathbb{R}$.

Write down an expression for $f'(x)$.
""")

code(r"""
q1_2 = ...

verify_derivative('1.2', q1_2, x**3 - 3*c*x + 2)
""")

md(r"""
### 1.3 — *May 2025 TZ1 Paper 3 Q1(c)(i), 2 marks*

$$G(t)=\frac{1}{16}t+\frac{3}{16}t^{2}+\frac{5}{16}t^{3}+\frac{7}{16}t^{4}$$

Find $G'(t)$.
""")

code(r"""
q1_3 = ...

verify_derivative('1.3', q1_3,
                  t/16 + 3*t**2/16 + 5*t**3/16 + 7*t**4/16, var=t)
""")

md(r"""
### 1.4 — *November 2022 Paper 3 Q1(c), 1 mark* · no cell

Consider the function $f(x)=1+x+x^{2}+\dots+x^{n}$, $n\in\mathbb{Z}^{+}$.

Show that $x\,f'(x)=x+2x^{2}+3x^{3}+\dots+nx^{n}$.

*The answer is the sum printed in the question, so there is nothing to type.
Do it on paper and read the solution.*
""")

md(r"""
### 1.5 — *November 2022 Paper 3 Q1(d)(i), 2 marks* · no cell

With $f_{1}(x)=x\,f'(x)$ and $f_{2}(x)=x\,f_{1}'(x)$, show that
$$f_{2}(x)=\sum_{i=1}^{n}i^{2}x^{i}.$$

*Again the answer is printed. The work is one differentiation and one
multiplication by $x$; the solution shows both.*
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. The ones you have to know

$$\frac{\mathrm{d}}{\mathrm{d}\theta}\sec\theta=\sec\theta\tan\theta\qquad
\frac{\mathrm{d}}{\mathrm{d}\theta}\csc\theta=-\csc\theta\cot\theta\qquad
\frac{\mathrm{d}}{\mathrm{d}\theta}\cot\theta=-\csc^{2}\theta$$

Three lines of the formula booklet, and two of the three carry a minus sign
that goes missing more often than anything else in this topic.
""")

md(r"""
### 2.1 — *November 2025 TZ3 Paper 1 Q8(b), 3 marks*

Astrid walks across a beach and then along a promenade; the time she takes is

$$T=500\sec\theta+\frac{2500-1000\tan\theta}{3}.$$

Find $\dfrac{\mathrm{d}T}{\mathrm{d}\theta}$.
""")

code(r"""
q2_1 = ...

verify_derivative('2.1', q2_1, 500*sec(theta) + (2500 - 1000*tan(theta))/3,
                  var=theta)
""")

md(r"""
### 2.2 — *May 2023 TZ1 Paper 1 Q11(b)(i), part of 5 marks*

A pole of length $L$ is carried round a corner between a passageway of width
$\frac34$ m and a room of width $6$ m, at an angle $\alpha$ to the wall, where
$0<\alpha<\frac{\pi}{2}$:

$$L=\frac{3}{4}\sec\alpha+6\csc\alpha .$$

Find $\dfrac{\mathrm{d}L}{\mathrm{d}\alpha}$.

*Part (ii) then shows that $\frac{\mathrm{d}L}{\mathrm{d}\alpha}=0$ gives
$\alpha=\arctan 2$; that half is in the solution.*
""")

code(r"""
q2_2 = ...

verify_derivative('2.2', q2_2, 3*sec(alpha)/4 + 6*cosec(alpha), var=alpha)
""")

md(r"""
### 2.3 — *November 2021 Paper 3 Q1(a), 2 marks*

$$f(z)=\frac{\mathrm{e}^{z}+\mathrm{e}^{-z}}{2}$$

Verify that $u=f(t)$ satisfies the differential equation
$\dfrac{\mathrm{d}^{2}u}{\mathrm{d}t^{2}}=u$.

*Enter $f''(t)$ — that is the whole of the verification, since the point is
that it comes back to $f(t)$ itself.*
""")

code(r"""
q2_3 = ...

verify_derivative('2.3', q2_3, (exp(t) + exp(-t))/2, var=t, order=2)
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. The chain rule

$$\frac{\mathrm{d}}{\mathrm{d}x}\,F\bigl(u(x)\bigr)=F'\bigl(u(x)\bigr)\cdot u'(x)$$

The tell is not the shape of the formula, it is what you would have to do to
evaluate it: if working out $f(2)$ makes you compute something *inside* first,
that inside has to come back out as a factor.
""")

md(r"""
### 3.1 — *November 2022 Paper 1 Q1, 4 marks*

The function $g$ is defined by $g(x)=\mathrm{e}^{x^{2}+1}$, where
$x\in\mathbb{R}$.

Find $g'(-1)$.
""")

code(r"""
G = exp(x**2 + 1)
q3_1 = ...

verify_exact('3.1', q3_1, diff(G, x).subs(x, -1))
""")

md(r"""
### 3.2 — *May 2024 TZ2 Paper 3 Q1(a)(i), 2 marks*

$$f(x)=\frac{1}{(2-x)^{2}},\qquad x\in\mathbb{R},\ x\ne2$$

Find an expression for $f'(x)$.
""")

code(r"""
q3_2 = ...

verify_derivative('3.2', q3_2, 1/(2 - x)**2)
""")

md(r"""
### 3.3 — *November 2022 Paper 3 Q2(c), 2 marks*

Consider the semi-circle of radius $r$ defined by $y=\sqrt{r^{2}-x^{2}}$,
where $-r\le x\le r$.

Find an expression for $\dfrac{\mathrm{d}y}{\mathrm{d}x}$.
""")

code(r"""
q3_3 = ...

verify_derivative('3.3', q3_3, sqrt(r**2 - x**2), params={r: (2, 3, 5)})
""")

md(r"""
### 3.4 — *May 2024 TZ2 Paper 2 Q12(b), 4 marks*

Show that
$$\frac{\mathrm{d}}{\mathrm{d}x}\!\left(\frac{1}{2}\ln\left(\cot
x\right)\right)=-\csc 2x .$$

*The answer is printed; type it anyway. The four marks are the chain rule,
the derivative of $\cot$, and the double-angle identity that turns
$-\frac{\csc^{2}x}{2\cot x}$ into $-\csc 2x$ — and if your algebra stopped
one step early, the cell will still say ✅, which is itself worth knowing.*
""")

code(r"""
q3_4 = ...

verify_derivative('3.4', q3_4, log(cot(x))/2)
""")

md(r"""
### 3.5 — *November 2025 TZ1 Paper 3 Q2(b)(iii), 2 marks*

Consider the function $f(x)=\ln\left(\ln 200-\ln x\right)$, where $0<x<200$.

Show that
$$f'(x)=\frac{-1}{x\ln\!\left(\frac{200}{x}\right)}.$$
""")

code(r"""
q3_5 = ...

verify_derivative('3.5', q3_5, log(log(200) - log(x)))
""")

md(r"""
### 3.6 — *November 2025 TZ3 Paper 3 Q1(e), 1 mark*

$S_{n}(x)$ is $\sin x$ composed inside itself $n-1$ times, so
$S_{3}(x)=\sin\bigl(\sin(\sin x)\bigr)$. It is given that
$$S_{n}'(x)=\cos\bigl(S_{n-1}(x)\bigr)\cos\bigl(S_{n-2}(x)\bigr)\dots
\cos\bigl(S_{1}(x)\bigr)\cos x .$$

Hence show that
$S_{3}'(x)=\cos\bigl(\sin(\sin x)\bigr)\cos(\sin x)\cos x$.
""")

code(r"""
q3_6 = ...

verify_derivative('3.6', q3_6, sin(sin(sin(x))))
""")

md(r"""
### 3.7 — *November 2022 Paper 2 Q11(d)(ii), 3 marks*

The function $f$ is defined by $f(x)=\mathrm{e}^{2x}(3x-4)$. Consider a
function $g$ such that $g(0)=1$ and $g'(0)=2$.

Find the value of $(f\circ g)'(0)$.
""")

code(r"""
F = exp(2*x)*(3*x - 4)
q3_7 = ...

verify_exact('3.7', q3_7, 2*diff(F, x).subs(x, 1))
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. The product rule

$$(uv)'=u'v+uv'$$

Two terms, and the mark scheme gives the method mark for seeing two terms.
Writing $u'v'$ loses it before any arithmetic happens.
""")

md(r"""
### 4.1 — *November 2022 Paper 2 Q11(a), 3 marks*

The function $f$ is defined by $f(x)=\mathrm{e}^{2x}(3x-4)$, where
$x\in\mathbb{R}$.

Find $f'(x)$.
""")

code(r"""
q4_1 = ...

verify_derivative('4.1', q4_1, exp(2*x)*(3*x - 4))
""")

md(r"""
### 4.2 — *May 2021 TZ2 Paper 3 Q1(c), 5 marks*

Consider $f_{n}(x)=x^{n}(a-x)^{n}$, where $a\in\mathbb{R}^{+}$ and
$n\in\mathbb{Z}^{+}$, $n>1$.

Show that $f_{n}'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}$.
""")

code(r"""
q4_2 = ...

verify_derivative('4.2', q4_2, x**n*(a - x)**n, params={n: (2, 3, 5)})
""")

md(r"""
### 4.3 — *May 2022 TZ1 Paper 3 Q2(d)(i), 2 marks*

Consider the function $g(x)=(x-r)(x^{2}-2ax+a^{2}+b^{2})$ for
$x\in\mathbb{R}$, where $r,a\in\mathbb{R}$ and $b\in\mathbb{R}$, $b>0$.

Show that $g'(x)=2(x-r)(x-a)+x^{2}-2ax+a^{2}+b^{2}$.
""")

code(r"""
q4_3 = ...

verify_derivative('4.3', q4_3, (x - r)*(x**2 - 2*a*x + a**2 + b**2))
""")

md(r"""
### 4.4 — *May 2023 TZ2 Paper 1 Q10(c), 4 marks*

A triangle PQR is inscribed in the circle $x^{2}+y^{2}=9$ with
$\mathrm{P}(-3,0)$, $\mathrm{Q}(x,y)$ and $\mathrm{R}(x,-y)$, and its area is
$A=(x+3)\sqrt{9-x^{2}}$.

Show that
$$\frac{\mathrm{d}A}{\mathrm{d}x}=\frac{9-3x-2x^{2}}{\sqrt{9-x^{2}}}.$$
""")

code(r"""
q4_4 = ...

verify_derivative('4.4', q4_4, (x + 3)*sqrt(9 - x**2))
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. The quotient rule

$$\left(\frac{u}{v}\right)'=\frac{u'v-uv'}{v^{2}}$$

The numerator does not commute. Swapping its two terms gives you exactly
minus the right answer, which is the single most expensive slip in this
section — and one the check names when it sees it.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 2 Q11(b), 3 marks*

The function $f$ is defined by
$$f(x)=\frac{3x+2}{4x^{2}-1},\qquad x\in\mathbb{R},\ x\ne p,\ x\ne q .$$

Find an expression for $f'(x)$.
""")

code(r"""
q5_1 = ...

verify_derivative('5.1', q5_1, (3*x + 2)/(4*x**2 - 1))
""")

md(r"""
### 5.2 — *May 2025 TZ3 Paper 2 Q5(a), 3 marks*

Consider the function
$$f(x)=\frac{(2x+a)^{3}}{(x+5)^{2}},\qquad x\ne-5,\ a\in\mathbb{R}^{+}.$$

Find an expression for $f'(x)$, in terms of $a$.
""")

code(r"""
q5_2 = ...

verify_derivative('5.2', q5_2, (2*x + a)**3/(x + 5)**2, params={a: (1, 3, 7)})
""")

md(r"""
### 5.3 — *May 2025 TZ2 Paper 3 Q1(c), 4 marks*

Given
$$f(x)=\frac{x\left(x^{2}-A\right)}{x^{2}+A},$$
where $A$ is a positive constant, prove that $f'\!\left(\sqrt{A}\right)$ is
independent of $A$.

*Enter the value of $f'\!\left(\sqrt{A}\right)$.*
""")

code(r"""
A = symbols('A', positive=True)      # the question says A is positive
F = x*(x**2 - A)/(x**2 + A)
q5_3 = ...

verify_exact('5.3', q5_3, simplify(diff(F, x).subs(x, sqrt(A))))
""")

md(r"""
### 5.4 — *May 2021 TZ2 Paper 2 Q12(c)(i), part of 9 marks*

A function $f$ is defined by
$$f(x)=\arcsin\left(\frac{x^{2}-1}{x^{2}+1}\right),\qquad x\in\mathbb{R}.$$

Show that
$$f'(x)=\frac{2x}{\sqrt{x^{2}}\left(x^{2}+1\right)}\qquad
\text{for }x\in\mathbb{R},\ x\ne0 .$$

*Part (ii) then uses $\sqrt{x^{2}}=|x|$ to show $f$ is decreasing for $x<0$;
that half is in the solution, and it is where the other marks are.*
""")

code(r"""
q5_4 = ...

verify_derivative('5.4', q5_4, arcsin((x**2 - 1)/(x**2 + 1)))
""")

md(r"""
### 5.5 — *November 2022 Paper 3 Q1(f), 3 marks*

For $x\ne1$, the function $f(x)=1+x+x^{2}+\dots+x^{n}$ can be written as a
geometric sum, $f(x)=\dfrac{x^{n+1}-1}{x-1}$.

Show that
$$f_{1}(x)=x\,f'(x)=\frac{nx^{n+2}-(n+1)x^{n+1}+x}{(x-1)^{2}} .$$

*Enter $f'(x)$ — multiplying by $x$ at the end is the easy half.*
""")

code(r"""
q5_5 = ...

verify_derivative('5.5', q5_5, (x**(n + 1) - 1)/(x - 1), params={n: (2, 3, 5)})
""")

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. Getting to the printed line

A *show that* question hands you the destination. What it is really asking is
the algebra between your line and that one: a common denominator, a factor
taken out, a sign moved. The differentiation in these four is trivial; the
marks are entirely in what happens afterwards.

One rule from the mark schemes: **work in one direction.** Starting from both
ends and meeting in the middle is not accepted, and neither is stopping one
step short of the printed form.
""")

md(r"""
### 6.1 — *May 2024 TZ2 Paper 3 Q1(a)(ii), 2 marks*

With $f(x)=\dfrac{1}{(2-x)^{2}}$ and $g(x)=x^{2}$, show that

$$f'(x)\,g'(x)=\frac{4x}{(2-x)^{3}} .$$
""")

code(r"""
F, G = 1/(2 - x)**2, x**2
q6_1 = ...

verify_identity('6.1', q6_1, diff(F, x)*diff(G, x))
""")

md(r"""
### 6.2 — *May 2024 TZ2 Paper 3 Q1(a)(iii), 4 marks*

With the same $f$ and $g$, show that

$$f(x)\,g'(x)+g(x)\,f'(x)=\frac{4x}{(2-x)^{3}} .$$

*Same destination as 6.1, four marks instead of two, and the difference is
one common denominator: $\frac{2x}{(2-x)^{2}}+\frac{2x^{2}}{(2-x)^{3}}$ has
to become a single fraction over $(2-x)^{3}$, not over $(2-x)^{5}$.*
""")

code(r"""
F, G = 1/(2 - x)**2, x**2
q6_2 = ...

verify_identity('6.2', q6_2, F*diff(G, x) + G*diff(F, x))
""")

md(r"""
### 6.3 — *May 2024 TZ2 Paper 3 Q1(b), 2 marks* · no cell

Consider two non-constant functions $f$ and $g$ with $f(x)>0$ and
$g(x)\ne g'(x)$.

By rearranging the equation $f(x)g'(x)+g(x)f'(x)=f'(x)g'(x)$, show that

$$\frac{f'(x)}{f(x)}=\frac{g'(x)}{g'(x)-g(x)} .$$

*Nothing is differentiated here at all — it is two lines of algebra on an
identity, and there is no expression to hand over. The solution has both
lines.*
""")

md(r"""
### 6.4 — *May 2025 TZ1 Paper 3 Q2(a), 2 marks*

The curvature $k$ of a twice-differentiable function $f$ is defined by

$$k(x)=\frac{\left|f''(x)\right|}{\left(1+\left(f'(x)\right)^{2}\right)^{\frac32}} .$$

Show that $k(x)=0$ for the family of linear functions $g(x)=mx+c$.

*Enter the value of $k(x)$ for such a $g$.*
""")

code(r"""
g = m*x + c
q6_4 = ...

verify_exact('6.4', q6_4,
             simplify(Abs(diff(g, x, 2))/(1 + diff(g, x)**2)**Rational(3, 2)))
""")

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. Second and higher derivatives

Differentiate, then differentiate that. Two things make it harder than it
sounds: the form you leave the first derivative in decides how long the second
takes, and the answer is often meant to be simplified using something you
already know about the function itself.
""")

md(r"""
### 7.1 — *May 2021 TZ1 Paper 1 Q12(a), 3 marks*

Let $f(x)=\sqrt{1+x}$ for $x>-1$. Show that

$$f''(x)=-\frac{1}{4\sqrt{(1+x)^{3}}} .$$
""")

code(r"""
q7_1 = ...

verify_derivative('7.1', q7_1, sqrt(1 + x), order=2)
""")

md(r"""
### 7.2 — *May 2022 TZ1 Paper 1 Q12(c), 5 marks*

The function $g$ is defined by $g(x)=\mathrm{e}^{x}\cos x$.

(i) Show that $g''(x)=2\bigl(g'(x)-g(x)\bigr)$.

(ii) Hence deduce that $g^{(4)}(x)=2\bigl(g'''(x)-g''(x)\bigr)$.

*Enter $g''(x)$. Part (ii) is one differentiation of the identity in (i),
and it is in the solution.*
""")

code(r"""
q7_2 = ...

verify_derivative('7.2', q7_2, exp(x)*cos(x), order=2)
""")

md(r"""
### 7.3 — *May 2023 TZ1 Paper 1 Q11(c), 7 marks*

With $L=\frac{3}{4}\sec\alpha+6\csc\alpha$ as in 2.2:

(i) Find $\dfrac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}$.

(ii) When $\alpha=\arctan 2$, show that
$\dfrac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}=\dfrac{45\sqrt{5}}{4}$.
""")

code(r"""
L = 3*sec(alpha)/4 + 6*cosec(alpha)
q7_3a = ...     # the second derivative
q7_3b = ...     # its exact value at alpha = arctan 2

verify_derivative('7.3 (i)', q7_3a, L, var=alpha, order=2)
verify_exact('7.3 (ii)', q7_3b, simplify(diff(L, alpha, 2).subs(alpha, arctan(2))))
""")

md(r"""
### 7.4 — *May 2024 TZ1 Paper 3 Q2(a), 3 marks*

The curve $y=x^{4}-3x^{3}+3x$ has points of inflexion at B and C.

Find $\dfrac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}$.
""")

code(r"""
q7_4 = ...

verify_derivative('7.4', q7_4, x**4 - 3*x**3 + 3*x, order=2)
""")

md(r"""
### 7.5 — *May 2025 TZ1 Paper 3 Q2(e)(i), 6 marks*

Consider the family of curves $y=\sqrt{r^{2}-x^{2}}$, where $-r<x<r$, $y>0$
and $r$ is a positive constant.

Show that
$$\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=-\frac{r^{2}}{y^{3}} .$$

*Enter it in terms of $x$ and $r$. Turning that into $-r^{2}/y^{3}$ is the
substitution the question is really about, and it is the last mark.*
""")

code(r"""
q7_5 = ...

verify_derivative('7.5', q7_5, sqrt(r**2 - x**2), order=2, params={r: (2, 3, 5)})
""")

md(r"""
### 7.6 — *May 2025 TZ1 Paper 3 Q2(e)(ii), 5 marks*

Hence show that the curvature $k$ is constant for this family of curves.

*Enter that constant, in terms of $r$.*
""")

code(r"""
q7_6 = ...

verify_exact('7.6', q7_6, 1/r)
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. A letter in the function

The rules do not change when a letter appears. What changes is the ending:
there is no number to arrive at, so you have to decide when the expression is
simplified enough — and the mark scheme has an opinion about that.

Nine of these come from two Paper 3 investigations, and eight of the nine are
the May 2025 one on curvature. It is worth doing them in order.
""")

md(r"""
### 8.1 — *November 2022 Paper 3 Q2(e)(iii), 2 marks*

Find $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ for
$y=f(kx)=\sqrt{r^{2}-k^{2}x^{2}}$, in terms of $x$, $r$ and $k$.
""")

code(r"""
q8_1 = ...

verify_derivative('8.1', q8_1, sqrt(r**2 - k**2*x**2),
                  params={k: (1, 2, 3), r: (7, 8, 9)})
""")

md(r"""
### 8.2 — *May 2025 TZ1 Paper 3 Q2(b)(i), 1 mark*

For the family of quadratics $h(x)=ax^{2}+bx+c$ it is given that

$$k(x)=\frac{2|a|}{\left(1+(2ax+b)^{2}\right)^{\frac32}},\qquad
k'(x)=-\frac{12a|a|(2ax+b)}{\left(1+(2ax+b)^{2}\right)^{\frac52}} .$$

By solving $k'(x)=0$, find the value of $x$ where $k_{\max}$ occurs.
""")

code(r"""
q8_2 = ...

verify_constants('8.2', [q8_2], [x],
                 [('the numerator of k′(x) vanishes there', 2*a*x + b)])
""")

md(r"""
### 8.3 — *May 2025 TZ1 Paper 3 Q2(b)(ii), 2 marks*

Determine an expression for $k_{\max}$, in terms of $a$ only.
""")

code(r"""
q8_3 = ...

verify_exact('8.3', q8_3, 2*Abs(a))
""")

md(r"""
### 8.4 — *May 2025 TZ1 Paper 3 Q2(b)(iv), 2 marks*

Consider $p(x)=-2x^{2}+2x-10$ and $q(x)=2x^{2}+5x+25$. State which one of
the following is true and justify your answer.

**A.** $k_{\max}$ of $p>k_{\max}$ of $q$ **B.** $k_{\max}$ of $p<k_{\max}$
of $q$ **C.** $k_{\max}$ of $p=k_{\max}$ of $q$

*Enter the common value of $k_{\max}$; which letter is true follows, and the
justification is in the solution.*
""")

code(r"""
pf = -2*x**2 + 2*x - 10
q8_4 = ...

verify_exact('8.4', q8_4,
             maximum(Abs(diff(pf, x, 2))/(1 + diff(pf, x)**2)**Rational(3, 2), x))
""")

md(r"""
### 8.5 — *May 2025 TZ1 Paper 3 Q2(c)(i), 2 marks*

For $v(x)=\ln x$, $x>0$, it is given that

$$k(x)=\frac{x}{\left(1+x^{2}\right)^{\frac32}},\qquad
k'(x)=\frac{1-2x^{2}}{\left(1+x^{2}\right)^{\frac52}} .$$

Determine the exact value of $x$ where $k_{\max}$ occurs.
""")

code(r"""
q8_5 = ...

verify_roots('8.5', [q8_5], 1 - 2*x**2, domain=(0, 10))
""")

md(r"""
### 8.6 — *May 2025 TZ1 Paper 3 Q2(c)(ii), 4 marks*

Show that $k_{\max}=\dfrac{2\sqrt{3}}{9}$ for $v(x)=\ln x$.
""")

code(r"""
kv = x/(1 + x**2)**Rational(3, 2)
q8_6 = ...

verify_exact('8.6', q8_6, maximum(kv, x, Interval(0, oo)))
""")

md(r"""
### 8.7 — *May 2025 TZ1 Paper 3 Q2(d)(i), 5 marks*

For $w(x)=\mathrm{e}^{x}$ it is given that

$$k(x)=\frac{\mathrm{e}^{x}}{\left(1+\mathrm{e}^{2x}\right)^{\frac32}},\qquad
k'(x)=\frac{\mathrm{e}^{x}\left(1-2\mathrm{e}^{2x}\right)}
{\left(1+\mathrm{e}^{2x}\right)^{\frac52}} .$$

Show that $k_{\max}=\dfrac{2\sqrt{3}}{9}$.
""")

code(r"""
kw = exp(x)/(1 + exp(2*x))**Rational(3, 2)
q8_7a = ...     # the exact x where k'(x) = 0
q8_7b = ...     # the value of k there

verify_roots('8.7 (x)', [q8_7a], 1 - 2*exp(2*x), domain=(-5, 5))
verify_exact('8.7 (k)', q8_7b, maximum(kw, x))
""")

md(r"""
### 8.8 — *May 2025 TZ3 Paper 3 Q2(c), 6 marks*

An open-topped box is made by cutting squares of side $x$ from an $a\times b$
sheet, and its volume is $V=4x^{3}-2(a+b)x^{2}+abx$.

Show that the only solutions of $\dfrac{\mathrm{d}V}{\mathrm{d}x}=0$ are
$$x=\frac{(a+b)\pm\sqrt{a^{2}-ab+b^{2}}}{6} .$$

*Enter $\dfrac{\mathrm{d}V}{\mathrm{d}x}$; the quadratic formula on it is the
other half, and it is in the solution.*
""")

code(r"""
q8_8 = ...

verify_derivative('8.8', q8_8, 4*x**3 - 2*(a + b)*x**2 + a*b*x,
                  params={a: (1, 2, 3), b: (4, 5, 7)})
""")

md(r"""
### 8.9 — *May 2024 TZ1 Paper 3 Q2(e), 3 marks*

Consider the general curve $y=x^{4}-mx^{3}+nx$, where $m,n\in\mathbb{R}$ and
$m>0$.

Find the $x$-coordinates of the two points of inflexion in terms of $m$.

*One of the two is the origin. Enter the other one — the one that moves
with $m$.*
""")

code(r"""
Y = x**4 - m*x**3 + n*x
q8_9 = ...

verify_constants('8.9', [q8_9], [x],
                 [('the second derivative vanishes there', diff(Y, x, 2)),
                  ('and it is not x = 0, which is the other one',
                   diff(Y, x, 2)/x)])
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. Reading the derivative

Fifty-one of the 188 marks, and the derivative is usually already there —
found in the part before, or printed in the question. What is being asked is
what it *says*: where it is zero, what sign it has, what the second one adds.

Two habits pay for themselves here. **Coordinates means both numbers**: the
$x$ that makes $f'=0$ is half the answer, and substituting it back into $f$
is the other half. **The interval in the question is the interval**: a
trigonometric answer over $-\frac{\pi}{4}\le x\le\frac{5\pi}{4}$ has one more
point in it than the same answer over one turn.
""")

md(r"""
### 9.1 — *May 2021 TZ2 Paper 3 Q1(d), 2 marks*

With $f_{n}'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}$ from 4.2, state the three
solutions to the equation $f_{n}'(x)=0$.
""")

code(r"""
q9_1 = [...]

check_set('9.1', q9_1, '""" + D_91 + r"""')
""")

md(r"""
### 9.2 — *May 2021 TZ2 Paper 3 Q1(f), 2 marks* · no cell

Hence, or otherwise, show that $f_{n}'\!\left(\frac{a}{4}\right)>0$ for
$n\in\mathbb{Z}^{+}$.

*The answer is an inequality argument — every factor positive — and there is
no expression to hand over. The solution lists the factors.*
""")

md(r"""
### 9.3 — *November 2022 Paper 1 Q10(b), 7 marks*

The function $f$ is defined by $f(x)=\cos^{2}x-3\sin^{2}x$, $0\le x\le\pi$.

(i) Find $f'(x)$.

(ii) Hence find the coordinates of the points on the graph of $y=f(x)$
where $f'(x)=0$.
""")

code(r"""
q9_3a = ...          # f'(x)
q9_3b = [...]        # the points, each written as (x, y)

verify_derivative('9.3 (i)', q9_3a, cos(x)**2 - 3*sin(x)**2)
verify_stationary('9.3 (ii)', q9_3b, cos(x)**2 - 3*sin(x)**2, domain=(0, pi))
""")

md(r"""
### 9.4 — *November 2023 TZ1 Paper 1 Q11(a), 5 marks*

Consider the function $f(x)=\mathrm{e}^{\cos 2x}$, where
$-\dfrac{\pi}{4}\le x\le\dfrac{5\pi}{4}$.

Find the coordinates of the points on the curve $y=f(x)$ where the gradient
is zero.
""")

code(r"""
q9_4 = [...]

verify_stationary('9.4', q9_4, exp(cos(2*x)), domain=(-pi/4, 5*pi/4))
""")

md(r"""
### 9.5 — *May 2023 TZ2 Paper 3 Q1(b), 5 marks*

Use calculus to find the minimum value of the expression $x-\ln x$,
justifying that this value is a minimum.

*Enter the minimum as a point: where it happens and what it is.*
""")

code(r"""
q9_5 = [...]

verify_stationary('9.5', q9_5, x - log(x), domain=(0.1, 10))
""")

md(r"""
### 9.6 — *May 2025 TZ2 Paper 2 Q3(a), 3 marks*

The derivative of a function $f$ is given by $f'(x)=4+2x-3\mathrm{e}^{x}$,
where $x\in\mathbb{R}$.

Find the values of $x$ for which $f$ is decreasing.
""")

code(r"""
q9_6 = ...

verify_param_set('9.6', q9_6,
                 lambda val: bool((4 + 2*x - 3*exp(x)).subs(x, val).evalf() < 0),
                 var=x, window=(-8, 4), tol=Rational(1, 100))
""")

md(r"""
### 9.7 — *May 2025 TZ2 Paper 2 Q3(b), 3 marks*

Find the values of $x$ for which the graph of $f$ is concave-up.
""")

code(r"""
q9_7 = ...

verify_param_set('9.7', q9_7,
                 lambda val: bool((2 - 3*exp(x)).subs(x, val).evalf() > 0),
                 var=x, window=(-8, 4), tol=Rational(1, 100))
""")

md(r"""
### 9.8 — *November 2025 TZ1 Paper 1 Q9(a), 3 marks*

The function $f$ has a derivative given by $f'(x)=3x^{2}+12x-15$. The graph
of $y=f(x)$ has horizontal tangents at the points where $x=a$ and $x=b$,
$a<b$.

Find the value of $a$ and the value of $b$.
""")

code(r"""
q9_8 = [...]

verify_roots('9.8', q9_8, 3*x**2 + 12*x - 15, domain=(-20, 20))
""")

md(r"""
### 9.9 — *November 2025 TZ1 Paper 1 Q9(c), 3 marks*

The second derivative $f''(x)$ is zero at $x=c$. Find the value of $c$.
""")

code(r"""
q9_9 = [...]

verify_roots('9.9', q9_9, diff(3*x**2 + 12*x - 15, x), domain=(-20, 20))
""")

md(r"""
### 9.10 — *May 2024 TZ1 Paper 3 Q2(b), 4 marks*

The curve $y=x^{4}-3x^{3}+3x$ has points of inflexion at B and C.

Find the coordinates of B and C.
""")

code(r"""
q9_10 = [...]

verify_stationary('9.10', q9_10, x**4 - 3*x**3 + 3*x, domain=(-2, 3), order=2)
""")

md(r"""
### 9.11 — *May 2024 TZ2 Paper 2 Q9, 8 marks*

Consider the curve
$$y=\frac{x-4}{ax^{2}+bx+c},$$
where $a$, $b$ and $c$ are non-zero constants. The curve has a local minimum
point at $(2,1)$ and a vertical asymptote with equation $x=1$.

Find the values of $a$, $b$ and $c$.
""")

code(r"""
a_, b_, c_ = symbols('a_ b_ c_')
Y = (x - 4)/(a_*x**2 + b_*x + c_)
q9_11 = [...]        # a, b, c in that order

verify_constants('9.11', q9_11, [a_, b_, c_], [
    ('the denominator is zero at the asymptote x = 1',
     (a_*x**2 + b_*x + c_).subs(x, 1)),
    ('the curve passes through (2, 1)', Eq(Y.subs(x, 2), 1)),
    ('and the gradient there is zero, because it is a minimum',
     diff(Y, x).subs(x, 2)),
])
""")

md(r"""
### 9.12 — *November 2025 TZ3 Paper 3 Q1(d), 6 marks*

Consider the graph of $y=S_{2}(x)=\sin(\sin x)$ for $0\le x\le 2\pi$.

By considering the equation $\dfrac{\mathrm{d}y}{\mathrm{d}x}=0$, show that
there are exactly two points of zero gradient, one at $x=\frac{\pi}{2}$ and
one at $x=\frac{3\pi}{2}$.

*Enter both points with their $y$-coordinates. The "exactly" is the other
half: $\cos(\sin x)=0$ would need $\sin x=\frac{\pi}{2}$, which never
happens — that argument is in the solution.*
""")

code(r"""
q9_12 = [...]

verify_stationary('9.12', q9_12, sin(sin(x)), domain=(0, 2*pi))
""")

# ================================================================= решения
md(r"""
---
# 🔑 Solutions

---
### 1.1
$f(x)=-(x-h)^{2}+2k$. The $2k$ is a constant and goes. The chain rule on
$(x-h)^{2}$ gives $2(x-h)\cdot1$, so
$$f'(x)=-2(x-h)\;\bigl(=2h-2x\bigr).$$
**A1.** Both forms are accepted.

---
### 1.2
$f'(x)=3x^{2}-3c$. The word is *write down*: one mark, no working expected.
$c$ is a parameter, so it behaves like a number and $-3cx$ differentiates to
$-3c$.

---
### 1.3
Term by term:
$$G'(t)=\frac{1}{16}+\frac{6}{16}t+\frac{15}{16}t^{2}+\frac{28}{16}t^{3}
=\frac{1}{16}+\frac{3}{8}t+\frac{15}{16}t^{2}+\frac{7}{4}t^{3}.$$
**A1A1** — one for the first two terms, one for the rest. Unsimplified
sixteenths are accepted.

The point of the question is next door: $G'(1)=\frac{1+6+15+28}{16}
=\frac{50}{16}=\mathrm{E}(M)$. A polynomial whose coefficients are a
probability distribution has its mean sitting in $G'(1)$.

---
### 1.4
$f(x)=1+x+x^{2}+\dots+x^{n}$, so term by term
$$f'(x)=1+2x+3x^{2}+\dots+nx^{n-1},$$
and multiplying every term by $x$,
$$x\,f'(x)=x+2x^{2}+3x^{3}+\dots+nx^{n}. \qquad\textbf{AG}$$
One mark, and it is for showing both lines: the mark scheme wants to see the
differentiation *and* the multiplication.

---
### 1.5
$f_{1}(x)=x\,f'(x)=\sum_{i=1}^{n}i\,x^{i}$ by 1.4. Differentiate that term
by term:
$$f_{1}'(x)=\sum_{i=1}^{n}i^{2}x^{i-1},$$
because $\frac{\mathrm{d}}{\mathrm{d}x}\bigl(i\,x^{i}\bigr)=i\cdot i\,x^{i-1}$.
Multiply by $x$:
$$f_{2}(x)=x\,f_{1}'(x)=\sum_{i=1}^{n}i^{2}x^{i}. \qquad\textbf{AG}$$
**M1A1.** The $i\cdot i$ is the whole question — each term already carries a
factor $i$, and differentiating brings down another.

---
### 2.1
$$\frac{\mathrm{d}T}{\mathrm{d}\theta}
=500\sec\theta\tan\theta-\frac{1000}{3}\sec^{2}\theta .$$
**A1A1A1** — one for each of $\sec\theta\tan\theta$, $\sec^{2}\theta$ and the
$\frac{1000}{3}$. The constant $\frac{2500}{3}$ vanishes; the $\frac13$ has to
survive on the tangent term, and that is where the third mark goes missing.

---
### 2.2
$$\frac{\mathrm{d}L}{\mathrm{d}\alpha}
=\frac{3}{4}\sec\alpha\tan\alpha-6\csc\alpha\cot\alpha .$$
**A1A1.** Note the minus: $\csc$ differentiates to $-\csc\cot$, and it is the
minus that makes the equation $\frac{\mathrm{d}L}{\mathrm{d}\alpha}=0$ have a
solution at all.

Part (ii), for the record: rewrite in sines and cosines,
$$\frac{3\sin\alpha}{4\cos^{2}\alpha}=\frac{6\cos\alpha}{\sin^{2}\alpha}
\;\Longrightarrow\;\sin^{3}\alpha=8\cos^{3}\alpha
\;\Longrightarrow\;\tan^{3}\alpha=8
\;\Longrightarrow\;\tan\alpha=2 .$$
Cube-rooting a *cubed* tangent is the step people skip; $\tan^{3}\alpha=8$
does not give $\tan\alpha=\pm2$, because the cube root of a real number is
unique.

---
### 2.3
$f(t)=\frac{\mathrm{e}^{t}+\mathrm{e}^{-t}}{2}$, so
$$f'(t)=\frac{\mathrm{e}^{t}-\mathrm{e}^{-t}}{2},\qquad
f''(t)=\frac{\mathrm{e}^{t}+\mathrm{e}^{-t}}{2}=f(t).$$
**A1A1.** The first derivative flips the sign of the second exponential and
the second flips it back — which is the entire content of
$\frac{\mathrm{d}^{2}u}{\mathrm{d}t^{2}}=u$, and the reason $\cosh$ and
$\sinh$ behave like $\cos$ and $\sin$ with the minus signs taken out.

---
### 3.1
$g(x)=\mathrm{e}^{x^{2}+1}$. Chain rule with $u=x^{2}+1$:
$$g'(x)=2x\,\mathrm{e}^{x^{2}+1},\qquad
g'(-1)=-2\,\mathrm{e}^{2}.$$
**A1A1A1A1** — two for the derivative, two for the substitution. Note
$(-1)^{2}+1=2$, not $0$: the exponent is $x^{2}+1$ and the square kills the
sign.

---
### 3.2
Rewrite as $f(x)=(2-x)^{-2}$, then chain rule with $u=2-x$, $u'=-1$:
$$f'(x)=-2(2-x)^{-3}\cdot(-1)=\frac{2}{(2-x)^{3}} .$$
**M1A1.** Two minus signs, and they cancel. Dropping the inner $-1$ gives you
the answer with the wrong sign, which is the single commonest error in the
whole of section 3.

---
### 3.3
$y=(r^{2}-x^{2})^{\frac12}$, chain rule with $u=r^{2}-x^{2}$, $u'=-2x$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac12(r^{2}-x^{2})^{-\frac12}\cdot(-2x)
=-\frac{x}{\sqrt{r^{2}-x^{2}}} .$$
**M1A1.** $r$ is a constant here, so $r^{2}$ contributes nothing to $u'$.

---
### 3.4
Chain rule on $\ln(\cot x)$, then the derivative of $\cot$:
$$\frac{\mathrm{d}}{\mathrm{d}x}\left(\tfrac12\ln(\cot x)\right)
=\frac12\cdot\frac{1}{\cot x}\cdot(-\csc^{2}x)
=-\frac{\csc^{2}x}{2\cot x}
=-\frac{1}{2\sin x\cos x}
=-\frac{1}{\sin 2x}=-\csc 2x .$$
**M1A1A1A1.** Four marks and only the first is differentiation. The rest is
$\frac{\csc^{2}x}{\cot x}=\frac{1}{\sin x\cos x}$ and then the double angle
$2\sin x\cos x=\sin 2x$.

---
### 3.5
$f(x)=\ln(\ln 200-\ln x)$. Chain rule with $u=\ln 200-\ln x$,
$u'=-\frac1x$:
$$f'(x)=\frac{1}{\ln 200-\ln x}\cdot\left(-\frac1x\right)
=\frac{-1}{x\ln\!\left(\frac{200}{x}\right)} .$$
**M1A1.** The minus comes from the inside, and $\ln 200-\ln x=\ln\frac{200}{x}$
is the tidy-up the printed answer is written in. Since $0<x<200$ the logarithm
is positive, so $f'<0$ throughout — the population model this belongs to is
decreasing, which is the check worth doing.

---
### 3.6
The formula gives $S_{3}'(x)=\cos\bigl(S_{2}(x)\bigr)\cos\bigl(S_{1}(x)\bigr)
\cos x$, and $S_{2}(x)=\sin(\sin x)$, $S_{1}(x)=\sin x$, so
$$S_{3}'(x)=\cos\bigl(\sin(\sin x)\bigr)\cos(\sin x)\cos x .$$
**A1.** One mark for substituting $n=3$ — but the chain rule is what the
formula encodes: three nested sines give three cosine factors, one per layer.

---
### 3.7
$(f\circ g)'(0)=f'\bigl(g(0)\bigr)\cdot g'(0)=f'(1)\cdot2$. From 4.1,
$f'(x)=\mathrm{e}^{2x}(6x-5)$, so $f'(1)=\mathrm{e}^{2}$ and
$$(f\circ g)'(0)=2\mathrm{e}^{2}.$$
**M1A1A1.** No formula for $g$ exists and none is needed: the chain rule works
on the two numbers you were given.

---
### 4.1
$u=\mathrm{e}^{2x}$, $v=3x-4$:
$$f'(x)=2\mathrm{e}^{2x}(3x-4)+3\mathrm{e}^{2x}=\mathrm{e}^{2x}(6x-5).$$
**M1A1A1.** The $2$ in $2\mathrm{e}^{2x}$ is the chain rule inside the product
rule, and the factorised form is what the next part needs.

---
### 4.2
$u=x^{n}$, $v=(a-x)^{n}$:
$$f_{n}'(x)=nx^{n-1}(a-x)^{n}+x^{n}\cdot n(a-x)^{n-1}\cdot(-1).$$
Take out $nx^{n-1}(a-x)^{n-1}$:
$$=nx^{n-1}(a-x)^{n-1}\bigl[(a-x)-x\bigr]=nx^{n-1}(a-2x)(a-x)^{n-1}.
\qquad\textbf{AG}$$
**M1A1A1M1A1.** Five marks, and three of them are the factorisation. The
$(-1)$ from the chain rule on $(a-x)^{n}$ is what makes the bracket
$(a-x)-x$ rather than $(a-x)+x$.

---
### 4.3
$u=x-r$, $v=x^{2}-2ax+a^{2}+b^{2}$:
$$g'(x)=1\cdot(x^{2}-2ax+a^{2}+b^{2})+(x-r)(2x-2a)
=2(x-r)(x-a)+x^{2}-2ax+a^{2}+b^{2}. \qquad\textbf{AG}$$
**A1A1.** Expanding everything is also accepted, but the printed form is the
one the next part uses: at $x=a$ the first term dies and $g'(a)=b^{2}$.

---
### 4.4
$A=(x+3)\sqrt{9-x^{2}}$, so with $u=x+3$, $v=(9-x^{2})^{\frac12}$:
$$\frac{\mathrm{d}A}{\mathrm{d}x}=\sqrt{9-x^{2}}
+(x+3)\cdot\frac{-x}{\sqrt{9-x^{2}}}
=\frac{(9-x^{2})-x(x+3)}{\sqrt{9-x^{2}}}
=\frac{9-3x-2x^{2}}{\sqrt{9-x^{2}}} . \qquad\textbf{AG}$$
**M1A1M1A1.** Both the product rule and, inside it, the chain rule; then a
common denominator. $(9-x^{2})-x^{2}-3x$ is where the $-2x^{2}$ comes from,
and losing one of the two $x^{2}$ terms is the usual way to miss the printed
line.

---
### 5.1
$u=3x+2$, $v=4x^{2}-1$:
$$f'(x)=\frac{3(4x^{2}-1)-(3x+2)(8x)}{(4x^{2}-1)^{2}}
=\frac{12x^{2}-3-24x^{2}-16x}{(4x^{2}-1)^{2}}
=\frac{-12x^{2}-16x-3}{(4x^{2}-1)^{2}} .$$
**M1A1A1.** The numerator does not factorise over the integers, so this is the
final form. Any equivalent arrangement is accepted.

---
### 5.2
$u=(2x+a)^{3}$, $v=(x+5)^{2}$, and both need the chain rule:
$$f'(x)=\frac{6(2x+a)^{2}(x+5)^{2}-2(2x+a)^{3}(x+5)}{(x+5)^{4}}
=\frac{2(x-a+15)(2x+a)^{2}}{(x+5)^{3}} .$$
**M1A1A1.** The mark scheme accepts the unsimplified version — but part (b)
needs $f'(1)=\tan70^{\circ}$, and doing that on the tidy form is three times
faster. The two values that come out are $a=2.73$ and $a=15.0$.

---
### 5.3
$$f'(x)=\frac{(3x^{2}-A)(x^{2}+A)-x(x^{2}-A)(2x)}{(x^{2}+A)^{2}} .$$
At $x=\sqrt{A}$ the second term vanishes because $x^{2}-A=0$, and the first
becomes $(3A-A)(2A)=4A^{2}$ over $(2A)^{2}=4A^{2}$:
$$f'\!\left(\sqrt{A}\right)=1 .$$
**M1A1A1A1.** Independent of $A$ — which is what was to be proved, and the
last mark is for saying so.

*The corpus records this function without its leading $x$. With that version
$f'(\sqrt{A})=\frac{1}{\sqrt{A}}$ and the question would be false; the form
above is the one printed on the paper.*

---
### 5.4
$u=\frac{x^{2}-1}{x^{2}+1}$, and $\frac{\mathrm{d}u}{\mathrm{d}x}
=\frac{2x(x^{2}+1)-(x^{2}-1)2x}{(x^{2}+1)^{2}}=\frac{4x}{(x^{2}+1)^{2}}$.
Then
$$f'(x)=\frac{1}{\sqrt{1-u^{2}}}\cdot\frac{4x}{(x^{2}+1)^{2}},\qquad
1-u^{2}=\frac{(x^{2}+1)^{2}-(x^{2}-1)^{2}}{(x^{2}+1)^{2}}
=\frac{4x^{2}}{(x^{2}+1)^{2}},$$
so $\sqrt{1-u^{2}}=\dfrac{2\sqrt{x^{2}}}{x^{2}+1}$ and
$$f'(x)=\frac{2x}{\sqrt{x^{2}}\,(x^{2}+1)} . \qquad\textbf{AG}$$
**M1A1M1A1A1** for part (i). Part (ii): for $x<0$, $\sqrt{x^{2}}=|x|=-x$, so
$f'(x)=\frac{2x}{-x(x^{2}+1)}=-\frac{2}{x^{2}+1}<0$, and $f$ is decreasing.
Writing $\sqrt{x^{2}}=x$ instead of $|x|$ turns the answer into a constant
$\frac{2}{x^{2}+1}$ and loses the whole of (ii) — the question spells the
identity out for exactly that reason.

---
### 5.5
$f(x)=\dfrac{x^{n+1}-1}{x-1}$, so
$$f'(x)=\frac{(n+1)x^{n}(x-1)-(x^{n+1}-1)}{(x-1)^{2}}
=\frac{nx^{n+1}-(n+1)x^{n}+1}{(x-1)^{2}},$$
and multiplying by $x$,
$$f_{1}(x)=\frac{nx^{n+2}-(n+1)x^{n+1}+x}{(x-1)^{2}} . \qquad\textbf{AG}$$
**M1A1A1.** The expansion is $(n+1)x^{n+1}-(n+1)x^{n}-x^{n+1}+1$, and the two
$x^{n+1}$ terms combine to $nx^{n+1}$. That is the whole question.

---
### 6.1
$f'(x)=\dfrac{2}{(2-x)^{3}}$ from 3.2 and $g'(x)=2x$, so
$$f'(x)g'(x)=\frac{4x}{(2-x)^{3}} . \qquad\textbf{AG}$$
**A1A1.** Two marks for a multiplication, because the paper needs this exact
expression twice and is establishing it once.

---
### 6.2
$$f(x)g'(x)+g(x)f'(x)
=\frac{2x}{(2-x)^{2}}+\frac{2x^{2}}{(2-x)^{3}} .$$
Common denominator $(2-x)^{3}$ — not $(2-x)^{5}$, because the first
denominator divides the second:
$$=\frac{2x(2-x)+2x^{2}}{(2-x)^{3}}=\frac{4x-2x^{2}+2x^{2}}{(2-x)^{3}}
=\frac{4x}{(2-x)^{3}} . \qquad\textbf{AG}$$
**M1A1A1A1.** The $-2x^{2}$ and the $+2x^{2}$ cancel exactly, which is why
this pair of functions was chosen: $f g'+g f'=f'g'$, and the whole question
is built on that coincidence.

---
### 6.3
Start from $f g'+g f'=f'g'$ and collect the terms that carry $f'$ on one
side. They are $g f'$ and $f'g'$, so the term left alone is $f g'$:
$$f g'=f'g'-g f'=f'\left(g'-g\right).$$
Now divide by $f\left(g'-g\right)$, which is allowed because the question
says $f(x)>0$ and $g(x)\ne g'(x)$:
$$\frac{f'}{f}=\frac{g'}{g'-g} . \qquad\textbf{AG}$$
**M1A1.** Two marks, and the only wrong turn is collecting the wrong pair:
$f g'$ is the one term with no $f'$ in it, so it is the one that has to end
up by itself.

---
### 6.4
$g(x)=mx+c$ gives $g'(x)=m$ and $g''(x)=0$, so
$$k(x)=\frac{|0|}{\left(1+m^{2}\right)^{\frac32}}=0 .$$
**A1A1.** A straight line does not curve — the definition is being sanity
checked before it is used on anything interesting.

---
### 7.1
$f(x)=(1+x)^{\frac12}$, so $f'(x)=\frac12(1+x)^{-\frac12}$ and
$$f''(x)=-\frac14(1+x)^{-\frac32}=-\frac{1}{4\sqrt{(1+x)^{3}}} .
\qquad\textbf{AG}$$
**A1A1A1.** Leaving the first derivative as $\frac{1}{2\sqrt{1+x}}$ and
attacking it with the quotient rule works too and takes three times as long.

---
### 7.2
$g(x)=\mathrm{e}^{x}\cos x$:
$$g'(x)=\mathrm{e}^{x}\cos x-\mathrm{e}^{x}\sin x,\qquad
g''(x)=-2\mathrm{e}^{x}\sin x .$$
And $2\bigl(g'(x)-g(x)\bigr)=2(-\mathrm{e}^{x}\sin x)=-2\mathrm{e}^{x}\sin x
=g''(x)$. $\textbf{AG}$

**M1A1A1** for (i). For (ii), differentiate the identity itself:
$$g'''(x)=2\bigl(g''(x)-g'(x)\bigr),\qquad
g^{(4)}(x)=2\bigl(g'''(x)-g''(x)\bigr). \qquad\textbf{A1A1}$$
Nothing is differentiated twice more — an identity between functions can be
differentiated as it stands, and that is the whole of (ii).

---
### 7.3
Differentiating $\frac{3}{4}\sec\alpha\tan\alpha-6\csc\alpha\cot\alpha$ by the
product rule on each term:
$$\frac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}
=\frac{3}{4}\left(\sec\alpha\tan^{2}\alpha+\sec^{3}\alpha\right)
+6\left(\csc\alpha\cot^{2}\alpha+\csc^{3}\alpha\right).$$
At $\tan\alpha=2$ a right triangle with legs $2$ and $1$ gives
$\sec\alpha=\sqrt5$, $\csc\alpha=\frac{\sqrt5}{2}$, $\cot\alpha=\frac12$:
$$\frac{3}{4}\left(4\sqrt5+5\sqrt5\right)
+6\left(\frac{\sqrt5}{8}+\frac{5\sqrt5}{8}\right)
=\frac{27\sqrt5}{4}+\frac{18\sqrt5}{4}=\frac{45\sqrt5}{4} . \qquad\textbf{AG}$$
**A1A1A1A1M1A1A1.** Seven marks, four for the differentiation and three for
the triangle. Both signs come out positive, which is what makes it a minimum
in part (d).

---
### 7.4
$y=x^{4}-3x^{3}+3x$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=4x^{3}-9x^{2}+3,\qquad
\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=12x^{2}-18x .$$
**A1A1A1.** The $+3x$ leaves a constant in the first derivative and nothing in
the second.

---
### 7.5
$y=(r^{2}-x^{2})^{\frac12}$ gives $\frac{\mathrm{d}y}{\mathrm{d}x}
=-\frac{x}{y}$ (using $y$ for the root). Quotient rule:
$$\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}
=-\frac{y-x\frac{\mathrm{d}y}{\mathrm{d}x}}{y^{2}}
=-\frac{y+\frac{x^{2}}{y}}{y^{2}}
=-\frac{y^{2}+x^{2}}{y^{3}}=-\frac{r^{2}}{y^{3}} ,$$
because $x^{2}+y^{2}=r^{2}$. In $x$ and $r$ that is
$-\dfrac{r^{2}}{(r^{2}-x^{2})^{\frac32}}$. $\textbf{AG}$

**M1A1M1A1A1A1.** The last substitution is the point of the question: the
relation between $x$ and $y$ turns a messy expression into a clean one, and
six marks say so.

---
### 7.6
Substituting into the definition, with
$\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{x}{y}$ and
$\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=-\frac{r^{2}}{y^{3}}$:
$$k=\frac{\frac{r^{2}}{y^{3}}}{\left(1+\frac{x^{2}}{y^{2}}\right)^{\frac32}}
=\frac{\frac{r^{2}}{y^{3}}}{\left(\frac{r^{2}}{y^{2}}\right)^{\frac32}}
=\frac{r^{2}/y^{3}}{r^{3}/y^{3}}=\frac{1}{r} .$$
**M1A1A1A1A1.** Constant, and equal to the reciprocal of the radius — the
one curve whose curvature is the same everywhere is the circle, and this is
the calculation that says so.

---
### 8.1
$y=\left(r^{2}-k^{2}x^{2}\right)^{\frac12}$, chain rule with
$u'=-2k^{2}x$:
$$\frac{\mathrm{d}y}{\mathrm{d}x}=-\frac{k^{2}x}{\sqrt{r^{2}-k^{2}x^{2}}} .$$
**A1A1.** The $k^{2}$ on top comes from differentiating $k^{2}x^{2}$; $k$ is a
constant and is never itself differentiated.

---
### 8.2
$k'(x)=0$ needs the numerator to vanish, and $12a|a|\ne0$, so $2ax+b=0$:
$$x=-\frac{b}{2a} .$$
**A1.** The vertex of the parabola — a quadratic is at its most curved exactly
where it turns.

---
### 8.3
At $x=-\frac{b}{2a}$ the bracket $2ax+b$ is zero, so the denominator of
$k$ is $1$:
$$k_{\max}=2|a| .$$
**M1A1.** The modulus survives: $a=-2$ and $a=2$ give the same curvature,
because a parabola opening downwards curves exactly as hard as the one
opening upwards. Writing $2a$ instead of $2|a|$ costs the mark and makes
part (iv) come out wrong.

---
### 8.4
$p$ has $a=-2$ and $q$ has $a=2$, so both have $|a|=2$ and
$$k_{\max}=2|a|=4$$
for each. Statement **C** is true.

**A1A1** — one for the statement, one for the justification, and the
justification has to name $|a|$.

---
### 8.5
$k'(x)=0$ needs $1-2x^{2}=0$, so $x=\pm\frac{1}{\sqrt2}$; the domain of
$\ln x$ is $x>0$, so
$$x=\frac{1}{\sqrt2}=\frac{\sqrt2}{2} .$$
**M1A1.** The negative root is not rejected for being negative — it is
rejected for being outside the domain of the function whose curvature this is.

---
### 8.6
$$k_{\max}=\frac{\frac{1}{\sqrt2}}{\left(1+\frac12\right)^{\frac32}}
=\frac{\frac{1}{\sqrt2}}{\left(\frac32\right)^{\frac32}}
=\frac{1}{\sqrt2}\cdot\frac{2\sqrt2}{3\sqrt3}=\frac{2}{3\sqrt3}
=\frac{2\sqrt3}{9} . \qquad\textbf{AG}$$
**M1A1A1A1.** $\left(\frac32\right)^{\frac32}=\frac{3\sqrt3}{2\sqrt2}$, and
rationalising at the end is the last mark.

---
### 8.7
$k'(x)=0$ needs $1-2\mathrm{e}^{2x}=0$, so
$\mathrm{e}^{2x}=\frac12$ and $\mathrm{e}^{x}=\frac{1}{\sqrt2}$, that is
$x=-\frac{\ln 2}{2}$. Then
$$k=\frac{\frac{1}{\sqrt2}}{\left(1+\frac12\right)^{\frac32}}
=\frac{2\sqrt3}{9},$$
the same arithmetic as 8.6. $\textbf{AG}$

**M1A1M1A1A1.** And part (ii): $\ln x$ and $\mathrm{e}^{x}$ are reflections of
each other in $y=x$, and reflecting a curve does not change how sharply it
bends. One mark, no calculation.

---
### 8.8
$$\frac{\mathrm{d}V}{\mathrm{d}x}=12x^{2}-4(a+b)x+ab .$$
Setting it to zero and using the quadratic formula:
$$x=\frac{4(a+b)\pm\sqrt{16(a+b)^{2}-48ab}}{24}
=\frac{(a+b)\pm\sqrt{(a+b)^{2}-3ab}}{6}
=\frac{(a+b)\pm\sqrt{a^{2}-ab+b^{2}}}{6} . \qquad\textbf{AG}$$
**A1M1A1A1A1A1.** The discriminant simplifies because
$(a+b)^{2}-3ab=a^{2}-ab+b^{2}$, and pulling $16$ out from under the root is
what turns $24$ into $6$.

---
### 8.9
$y=x^{4}-mx^{3}+nx$ gives
$$\frac{\mathrm{d}y}{\mathrm{d}x}=4x^{3}-3mx^{2}+n,\qquad
\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=12x^{2}-6mx=6x(2x-m),$$
so the two points of inflexion are at $x=0$ and
$$x=\frac{m}{2} .$$
**A1A1A1.** The $n$ disappears in the second derivative, which is why the
answer is in terms of $m$ alone — and why the line through the two points of
inflexion has a slope that depends on both.

---
### 9.1
$f_{n}'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}=0$ when any factor is zero:
$$x=0,\qquad x=\frac{a}{2},\qquad x=a .$$
**A1A1.** Three factors, three solutions; the powers $n-1$ do not add any.

---
### 9.2
At $x=\frac{a}{4}$, with $a>0$ and $n\in\mathbb{Z}^{+}$:

* $n>0$;
* $x^{n-1}=\left(\frac{a}{4}\right)^{n-1}>0$;
* $a-2x=a-\frac{a}{2}=\frac{a}{2}>0$;
* $(a-x)^{n-1}=\left(\frac{3a}{4}\right)^{n-1}>0$.

A product of positive factors is positive, so
$f_{n}'\!\left(\frac{a}{4}\right)>0$. $\textbf{AG}$

**M1A1.** The mark scheme wants every factor named. $\frac{a}{4}$ sits between
$0$ and $\frac{a}{2}$, so this is the statement that the curve is rising on
that first stretch.

---
### 9.3
$f(x)=\cos^{2}x-3\sin^{2}x$. Using $\cos^{2}x=\frac{1+\cos2x}{2}$ and
$\sin^{2}x=\frac{1-\cos2x}{2}$, or the chain rule twice:
$$f'(x)=-2\cos x\sin x-6\sin x\cos x=-8\sin x\cos x=-4\sin 2x .$$
Then $f'(x)=0$ on $0\le x\le\pi$ at $x=0,\frac{\pi}{2},\pi$, and
$$(0,1),\qquad\left(\tfrac{\pi}{2},-3\right),\qquad(\pi,1).$$
**A1A1M1A1A1A1A1.** Seven marks, and four of them are the coordinates: the
question says *coordinates*, so each $x$ has to go back into $f$. The
endpoints count — $x=0$ and $x=\pi$ are inside the closed interval.

---
### 9.4
$f(x)=\mathrm{e}^{\cos 2x}$, so
$f'(x)=-2\sin 2x\,\mathrm{e}^{\cos 2x}$, which is zero when
$\sin 2x=0$. On $-\frac{\pi}{4}\le x\le\frac{5\pi}{4}$ that gives
$2x=0,\pi,2\pi$, so $x=0,\frac{\pi}{2},\pi$:
$$(0,\mathrm{e}),\qquad\left(\tfrac{\pi}{2},\tfrac{1}{\mathrm{e}}\right),
\qquad(\pi,\mathrm{e}).$$
**M1A1A1A1A1.** The exponential is never zero, so only the sine matters. The
interval runs past $\pi$ to $\frac{5\pi}{4}$, but the next solution is at
$\frac{3\pi}{2}$ and does not fit — worth checking rather than assuming.

*The corpus records this domain as $-\frac{\pi}{4}\le x\le\pi$. The answer is
the same either way, which is exactly why the error survived.*

---
### 9.5
$\frac{\mathrm{d}}{\mathrm{d}x}(x-\ln x)=1-\frac1x=0$ at $x=1$, and
$$\frac{\mathrm{d}^{2}}{\mathrm{d}x^{2}}(x-\ln x)=\frac{1}{x^{2}}>0
\quad\text{for all }x>0,$$
so it is a minimum, and its value is $1-\ln 1=1$.

**A1A1A1A1A1.** The justification is a mark on its own: *find the minimum,
justifying that it is a minimum*. The consequence, in part (c), is
$x>\ln x$ for every positive $x$ — a one-line proof of an inequality that
looks like it should need work.

---
### 9.6
$f$ decreases where $f'(x)<0$, that is $4+2x-3\mathrm{e}^{x}<0$. The
critical values, from the GDC, are $x=-1.73554\ldots$ and $x=0.517999\ldots$,
and between them $f'>0$ (at $x=0$, $f'=1$). So
$$x\le-1.74\quad\text{or}\quad x\ge0.518 .$$
**A1M1A1.** The mark scheme accepts strict and non-strict inequalities alike
here, and it writes the two conditions joined by *and*, meaning both
stretches. Giving only one of the two is the way this mark goes.

---
### 9.7
$f''(x)=2-3\mathrm{e}^{x}$, and concave-up means $f''>0$:
$$2-3\mathrm{e}^{x}>0\;\Longrightarrow\;\mathrm{e}^{x}<\tfrac23
\;\Longrightarrow\;x<\ln\tfrac23\;(=-0.405).$$
**A1M1A1.** One stretch this time, because $f''$ is decreasing throughout.
Differentiating a derivative you were *given* is the step that gets skipped:
$f'$ is the starting point, not $f$.

---
### 9.8
$3x^{2}+12x-15=0$, so $x^{2}+4x-5=0$ and $(x+5)(x-1)=0$:
$$a=-5,\qquad b=1 .$$
**M1A1A1.** $a<b$ is given, so the order is fixed and the two values are not
interchangeable.

---
### 9.9
$f''(x)=6x+12$, zero at
$$c=-2 .$$
**A1M1A1.** And $-2$ is the midpoint of $-5$ and $1$: for a cubic the point
of inflexion always sits halfway between the two turning points.

---
### 9.10
From 7.4, $\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=12x^{2}-18x=6x(2x-3)$,
which is zero at $x=0$ and $x=\frac32$. Substituting into
$y=x^{4}-3x^{3}+3x$:
$$\mathrm{B}(0,0),\qquad \mathrm{C}\!\left(\tfrac32,-\tfrac{9}{16}\right).$$
**M1A1A1A1.** $\left(\frac32\right)^{4}-3\left(\frac32\right)^{3}
+3\cdot\frac32=\frac{81}{16}-\frac{81}{8}+\frac92=-\frac{9}{16}$. The line
through B and C then has slope $-\frac{9}{16}\div\frac32=-0.375$, which is
the next part.

---
### 9.11
Three conditions, three equations:

* vertical asymptote at $x=1$: the denominator vanishes there, $a+b+c=0$;
* the curve passes through $(2,1)$: $\frac{2-4}{4a+2b+c}=1$, so
  $4a+2b+c=-2$;
* a minimum at $x=2$: the numerator of $\frac{\mathrm{d}y}{\mathrm{d}x}$
  vanishes there, $(4a+2b+c)-(2-4)(4a+b)=0$, so $12a+4b+c=0$.

Solving: $a=3$, $b=-11$, $c=8$.

**M1A1A1M1(M1)A1M1A1.** Eight marks, and only two of them are calculus. The
mark scheme adds a warning worth reading: *an incorrect numerator may lead to
a correct equation* — and in that case the mark is not given, because the
right answer arrived by the wrong route.

---
### 9.12
$y=\sin(\sin x)$, so
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\cos(\sin x)\cos x=0 .$$
A product is zero when a factor is. $\cos x=0$ gives
$x=\frac{\pi}{2},\frac{3\pi}{2}$ on $0\le x\le2\pi$. The other factor
$\cos(\sin x)=0$ would need $\sin x=\frac{\pi}{2}\approx1.571$, and
$|\sin x|\le1$, so it never happens. Exactly two points:
$$\left(\tfrac{\pi}{2},\sin 1\right),\qquad
\left(\tfrac{3\pi}{2},-\sin 1\right).$$
**M1A1A1A1M1A1.** Six marks, and two of them are for ruling the second factor
out. *Exactly two* is a claim about what is **not** there, and it has to be
argued.

---
### Where the marks went, across the topic

| technique | marks | share |
| --- | --- | --- |
| Reading the derivative | 51 | 27% |
| Second and higher derivatives | 29 | 15% |
| A letter in the function | 27 | 14% |
| The quotient rule | 22 | 12% |
| The chain rule | 18 | 10% |
| The product rule | 14 | 7% |
| Getting to the printed line | 10 | 5% |
| The ones you have to know | 10 | 5% |
| The power rule, term by term | 7 | 4% |

Three things stand out.

**The rules are worth a quarter of the topic.** Sections 1–5 together carry
$71$ marks and sections 6–9 carry $117$. Choosing and applying the right rule
is the part everyone drills; what the archive actually pays for is the algebra
after it and the reading of the result.

**Reading the derivative is the biggest single block, at $51$ marks.** And it
is the one that needs no new technique at all: solve $f'=0$, put the answers
back into $f$, look at signs. The failures there are not failures of calculus
— a missing second coordinate, an interval read as one turn instead of one
and a quarter, a *decreasing* solved as an equation.

**Two Paper 3 investigations carry $39$ of the $188$ marks** — the May 2025 one
on curvature and the November 2022 one on surfaces of revolution. That is the
shape of this topic: not five-mark questions scattered about, but a long
question in which the derivative is a step, taken over and over.
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
