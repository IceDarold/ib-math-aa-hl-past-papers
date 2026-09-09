"""Собирает архивный ноутбук E5: техника интегрирования, вся тема подряд.

Двенадцатый ноутбук в формате, опробованном на B4, C3, B5, E1, E2, E3, D2,
D1, C2, A1 и E4. Практикум E5 учит — лестница, теория, уровни, тренажёр.
Этот не учит, он даёт набивать руку: вопрос, ячейка для ответа с мгновенной
проверкой, разбор в конце.

Внутри — та половина calculus.integration_applications, где вопрос звучит
«чему равна первообразная»: 36 вопросов и 145 баллов, разложенные по восьми
приёмам карточки calculus-integration.yaml. Ещё три блока корпуса — зональные
дубли ноябрьской 2023: TZ1 и TZ2 в тот год были одной и той же бумагой,
и вопрос стоит здесь один раз, с оговоркой на месте.

Проверки те же, что в практикуме, и ни одна из них не интегрирует: ответ
берут и дифференцируют, а определённый интеграл считают сложением. Поэтому
подсказать ответ проверка не может — только узнать его.

Хешей два из сорока шести: оба в 8.3, где функция задана картинкой и
подынтегрального выражения нет вовсе. Всё остальное проверка получает
из условия.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_e5.py прогоняет весь ноутбук
с заполненными ответами и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest, sig

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e5-integration.ipynb')

# Два хеша темы. У майской 2024 TZ1 Paper 1 Q9 функция задана только графиком:
# подынтегрального выражения нет, и передать проверке нечего.
D_83A = digest(sig(-1.6, 2))
D_83B = digest(sig(3.2, 2))

ANSWERS = {
    # 1. Первообразная по таблице и постоянная по точке
    'q1_1a': '3*x - 10*sqrt(x)',
    'q1_1b': '4',
    'q1_2': 'Rational(3, 7)',
    'q1_3': 'x**3 + 5*exp(x) - 1',
    'q1_4': 'x**3 + 6*x**2 - 15*x - 10',
    'q1_5': 'log(x/(k - x))/k',
    # 2. Замена переменной
    'q2_1a': 'u**(n - 1)',
    'q2_1b': '(2**n - 1)/n',
    'q2_2': '3*log(1 + x**2) + 5 - 3*log(2)',
    'q2_3a': '2*t*cos(t)',
    'q2_3b': '2*t*sin(t) + 2*cos(t)',
    # 3. Интегрирование по частям
    'q3_1': 'x**2*log(x)**2/2 - x**2*log(x)/2 + x**2/4',
    'q3_2': '2*log(2)**2 - 2*log(2) + Rational(3, 4)',
    'q3_3': '(x**2 - 2*x - 3)*exp(x)',
    'q3_4': 'x*acos(x) - sqrt(1 - x**2)',
    'q3_5': 'x*atan(x) - log(1 + x**2)/2',
    'q3_6a': '-t*exp(-3*t)/3 - exp(-3*t)/9',
    'q3_6b': '9',
    'q3_7': '-(x + 1)*exp(-x)',
    'q3_8': '1',
    'q3_9': '24',
    'q3_10': '120',
    # 4. Разложение на простейшие дроби
    'q4_1a': 'u/(u**2 - u - 2)',
    'q4_1b': 'Rational(1, 3)/(u + 1) + Rational(2, 3)/(u - 2)',
    'q4_1c': 'log(Abs(sin(x) + 1))/3 + 2*log(Abs(sin(x) - 2))/3',
    'q4_2a': '3/(x + 3) - 1/(x - 4)',
    'q4_2b': '5*log(2)',
    'q4_3a': '4/(2*x + 1) - 2/(x + 1) - 1/(x + 1)**2',
    'q4_3b': '2*log(Abs(2*x + 1)) - 2*log(Abs(x + 1)) + 1/(x + 1)',
    'q4_4': 'log(Abs((1 + v)/(1 - v)))/2 + log(A)/2',
    # 5. Частное, узнанное как f'/f
    'q5_1': '-2*log(Abs(x - 2))',
    'q5_2': 'exp(x + x**2/2)',
    'q5_3': 'exp(x/2)*sqrt(sin(x))',
    # 6. Формула понижения
    'q6_1': 'cos(x)**(n - 1)*sin(x) + (n - 1)*J(n - 2) - (n - 1)*J(n)',
    'q6_2': 'cos(x)**(n - 1)*sin(x)/n + (n - 1)*J(n - 2)/n',
    'q6_3': 'cos(x)**3*sin(x)/4 + 3*cos(x)*sin(x)/8 + 3*x/8',
    # 7. Интегрирование ряда почленно
    'q7_1a': 'E - 2*E*x**2',
    'q7_1b': '5*E/12',
    'q7_2': 'x - x**3/3 + x**5/5 - x**7/7 + C',
    'q7_3': 'x + x**3/6 + 3*x**5/40 + C',
    'q7_4': '3',
    'q7_5': '0.158422',
    # 8. Интеграл как условие
    'q8_1': '4',
    'q8_2': '0.713250',
    'q8_3a': '-1.6',
    'q8_3b': '3.2',
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
# Archive E5 — techniques of integration

**Every question in the topic, one after another.** No theory, no ladder, no
levels: the practicum has all of that. This is for sitting down and working
through the material until the moves stop needing thought.

**36 questions, 145 marks, May 2021 — November 2025.** The half of
`calculus.integration_applications` where the answer is an antiderivative, or
the number an antiderivative gives — substitution, parts, partial fractions,
reduction formulae, series. What an integral *measures* is E6.

Grouped by the eight techniques of
[`calculus-integration.yaml`](../skills/calculus-integration.yaml), in the
order of the practicum's ladder. Within a group the questions run from short
to long.

**How to use this.** Read the question, write the answer in the cell, run it.
The check answers at once. Solutions are at the bottom — all of them, in
order; use them when you are stuck or when you are done, not in between.

**What the checks do.** They differentiate. Not one of them integrates —
there is no call to `integrate` anywhere in this part of `kit.py`, and a test
proves it by reading the source. A check can *recognise* your antiderivative;
it cannot produce one. Definite values are added up by adaptive Simpson
straight from the integrand.

Two consequences to know before you start.

**The constant is free, in any costume.** `+ C`, `- 1`, `+ log(A)/2` all
differentiate to zero, so all of them pass. Where a point is given and the
constant is pinned, the check is told about the point.

**Where the paper prints the answer, this notebook asks for the step.**
"Show that $\int_1^4 x(\ln x)^2\,\mathrm{d}x = 32(\ln 2)^2-16\ln 2+\tfrac{15}{4}$"
has nothing to hand in, so the question here is the antiderivative, or the
same integral between different limits. Those places are marked.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, log, Eq

language('en')                 # this notebook is in English, and so are the checks

a, b, c, g, n, p, q, r, s = symbols('a b c g n p q r s')   # letters that stay letters
J = Function('J')              # J(m) means "the integral of f_m", used in section 6
                               # x, y, t, u, v, A, C, k already come from kit

print('ready; sympy', sp.__version__)
""")

# ------------------------------------------------------------------ 1
md(r"""
---
# 1. The antiderivative is in the table

*Five questions, 18 marks.* Rewrite each term as something the table knows,
integrate it, and — if a point on the graph was given — find the constant
instead of leaving it as a letter.
""")

md(r"""
## 1.1 · May 2022 TZ1 Paper 1 Q1 · 5 marks · no calculator

Find the value of $\displaystyle\int_1^9\left(3-\frac{5}{\sqrt x}\right)\mathrm{d}x$.
*[5]*

Hand in the antiderivative as well as the number — the mark scheme buys them
separately.
""")

code(r"""
q1_1a = ...      # an antiderivative of 3 - 5/sqrt(x)
q1_1b = ...      # the value of the definite integral

verify_antiderivative('1.1a', q1_1a, 3 - 5/sqrt(x), domain=(0.5, 9))
verify_integral('1.1b', q1_1b, 3 - 5/sqrt(x), 1, 9)
""")

md(r"""
## 1.2 · May 2025 TZ1 Paper 2 Q11(a)(i) · 1 mark · calculator

In a marathon, the time $T$ in hours has probability density function

$$f(t)=\begin{cases}
\dfrac{4}{21}\Bigl(1-\cos\bigl(\tfrac{4\pi}{9}(t-2.25)\bigr)\Bigr), & 2.25\le t<4.5;\\[2ex]
\dfrac{4}{21}\Bigl(1+\cos\bigl(\tfrac{\pi}{3}(t-4.5)\bigr)\Bigr), & 4.5\le t\le 7.5;\\[1ex]
0,&\text{otherwise.}
\end{cases}$$

Find the value of $\displaystyle\int_{2.25}^{4.5}f(t)\,\mathrm{d}t$. *[1]*

The answer is exact, which is the point of the question: the cosine
contributes nothing over a whole half-period.
""")

code(r"""
q1_2 = ...       # the value of the integral

left_piece = Rational(4, 21)*(1 - cos(4*pi*(t - Rational(9, 4))/9))
verify_integral('1.2', q1_2, left_piece, Rational(9, 4), Rational(9, 2), var=t)
""")

md(r"""
## 1.3 · May 2022 TZ2 Paper 2 Q2 · 5 marks · calculator

The derivative of a function $g$ is $g'(x)=3x^2+5\mathrm{e}^x$, where
$x\in\mathbb{R}$. The graph of $g$ passes through $(0,4)$. Find $g(x)$. *[5]*
""")

code(r"""
q1_3 = ...       # g(x)

verify_antiderivative('1.3', q1_3, 3*x**2 + 5*exp(x), through=(0, 4))
""")

md(r"""
## 1.4 · November 2025 TZ1 Paper 1 Q9(e) · 4 marks · no calculator

The function $f$ has derivative $f'(x)=3x^2+12x-15$. Given that $f(-2)=36$,
find $f(x)$. *[4]*
""")

code(r"""
q1_4 = ...       # f(x)

verify_antiderivative('1.4', q1_4, 3*x**2 + 12*x - 15, through=(-2, 36))
""")

md(r"""
## 1.5 · May 2021 TZ1 Paper 2 Q12(b) · 3 marks · calculator

The function $f$ has derivative $f'(x)=\dfrac{1}{x(k-x)}$, where $k$ is a
positive constant, $x\ne 0$ and $x\ne k$. Part (a) has already written this as
$\dfrac{a}{x}+\dfrac{b}{k-x}$ with $a=b=\tfrac1k$.

Hence find an expression for $f(x)$. *[3]*

No point is given, so the constant stays free. The check runs your answer at
three values of $k$.
""")

code(r"""
q1_5 = ...       # f(x), in terms of k

verify_antiderivative('1.5', q1_5, 1/(x*(k - x)), domain=(0.1, 0.9),
                      params={k: (1, 3, 8)})
""")

# ------------------------------------------------------------------ 2
md(r"""
---
# 2. Substitution

*Three questions, 17 marks — all of them Paper 1.* A function is sitting
beside its own derivative, or can be made to. The step the mark scheme pays
for is writing the integrand in the new variable, $\mathrm{d}x$ included.
""")

md(r"""
## 2.1 · May 2022 TZ2 Paper 1 Q7 · 6 marks · no calculator

By using the substitution $u=\sec x$ or otherwise, find an expression for
$$\int_0^{\pi/3}\sec^n x\,\tan x\,\mathrm{d}x$$
in terms of $n$, where $n$ is a non-zero real number. *[6]*

**2.1a** The integrand in terms of $u$. *[2]*

**2.1b** The value of the integral. *[4]*
""")

code(r"""
q2_1a = ...      # the integrand in u, after du has absorbed dx
q2_1b = ...      # the value of the definite integral, in terms of n

verify_transformed('2.1a', q2_1a, sec(x)**n*tan(x), sec(x), domain=(0.1, 1.0))
verify_integral('2.1b', q2_1b, sec(x)**n*tan(x), 0, pi/3, params={n: (2, 3, 5, -1)})
""")

md(r"""
## 2.2 · November 2022 Paper 1 Q4 · 5 marks · no calculator

The derivative of the function $f$ is $f'(x)=\dfrac{6x}{1+x^2}$. The graph of
$y=f(x)$ passes through the point $(1,5)$. Find an expression for $f(x)$. *[5]*
""")

code(r"""
q2_2 = ...       # f(x)

verify_antiderivative('2.2', q2_2, 6*x/(1 + x**2), through=(1, 5))
""")

md(r"""
## 2.3 · May 2023 TZ2 Paper 1 Q12(a) · 6 marks · no calculator

By using an appropriate substitution, show that
$$\int\cos\sqrt x\,\mathrm{d}x=2\sqrt x\sin\sqrt x+2\cos\sqrt x+C .$$
*[6]*

**Printed, so hand in the route.** With $t=\sqrt x$:

**2.3a** the integrand in terms of $t$, including what $\mathrm{d}x$ becomes;

**2.3b** an antiderivative of *that*, still in terms of $t$.

Substituting $t=\sqrt x$ back into 2.3b gives the printed line.
""")

code(r"""
q2_3a = ...      # the integrand in t
q2_3b = ...      # an antiderivative of it, in t

verify_transformed('2.3a', q2_3a, cos(sqrt(x)), sqrt(x), new=t, domain=(0.2, 4.0))
verify_antiderivative('2.3b', q2_3b, 2*t*cos(t), var=t)
""")

# ------------------------------------------------------------------ 3
md(r"""
---
# 3. Integration by parts

*Ten questions, 37 marks.* The largest technique in the topic, and the only
one spread evenly over all three papers. Choose $u$ to be the factor that
simplifies when differentiated; everything else follows.
""")

md(r"""
## 3.1 · November 2023 TZ1 Paper 1 Q8(a) · 6 marks · no calculator

Find $\displaystyle\int x(\ln x)^2\,\mathrm{d}x$. *[6]*

*The same question is printed in the November 2023 TZ2 paper, word for word.
Those two papers are one paper — see the note at the end.*
""")

code(r"""
q3_1 = ...       # an antiderivative of x*(ln x)^2

verify_antiderivative('3.1', q3_1, x*log(x)**2, domain=(0.4, 3.0))
""")

md(r"""
## 3.2 · November 2023 TZ1 Paper 1 Q8(b) · 3 marks · no calculator

Hence show that
$\displaystyle\int_1^4 x(\ln x)^2\,\mathrm{d}x=32(\ln 2)^2-16\ln 2+\tfrac{15}{4}$.
*[3]*

**Printed.** Do the same thing between different limits instead: find the
exact value of $\displaystyle\int_1^2 x(\ln x)^2\,\mathrm{d}x$.
""")

code(r"""
q3_2 = ...       # the exact value between 1 and 2

verify_integral('3.2', q3_2, x*log(x)**2, 1, 2)
""")

md(r"""
## 3.3 · May 2025 TZ3 Paper 2 Q12(a) · 6 marks · calculator

Find $\displaystyle\int(x^2-5)\mathrm{e}^x\,\mathrm{d}x$. *[6]*
""")

code(r"""
q3_3 = ...       # an antiderivative

verify_antiderivative('3.3', q3_3, (x**2 - 5)*exp(x))
""")

md(r"""
## 3.4 · November 2025 TZ1 Paper 2 Q11(a) · 4 marks · calculator

Use integration by parts to find $\displaystyle\int\arccos x\,\mathrm{d}x$. *[4]*
""")

code(r"""
q3_4 = ...       # an antiderivative of arccos(x)

verify_antiderivative('3.4', q3_4, acos(x), domain=(-0.9, 0.9))
""")

md(r"""
## 3.5 · November 2025 TZ3 Paper 3 Q2(e) · 4 marks · calculator

By using integration by parts, show that
$$\int_0^{1/\sqrt3}\arctan x\,\mathrm{d}x=\frac{\pi}{6\sqrt3}-\frac12\ln\frac43 .$$
*[4]*

**Printed.** Hand in the antiderivative of $\arctan x$ instead — that is the
whole of the working, and the substitution of limits is arithmetic.
""")

code(r"""
q3_5 = ...       # an antiderivative of arctan(x)

verify_antiderivative('3.5', q3_5, atan(x))
""")

md(r"""
## 3.6 · May 2025 TZ2 Paper 2 Q11(b), and (c)(ii) · 4 marks · calculator

The time $T$ in minutes that a spinning top stays in motion has probability
density function
$$f(t)=\begin{cases}kt\mathrm{e}^{-3t},&t\ge0;\\0,&\text{otherwise,}\end{cases}
\qquad k\in\mathbb{Z}^+ .$$

The paper shows that
$\displaystyle\int_0^a f(t)\,\mathrm{d}t=\frac{k}{9}\bigl[1-(3a+1)\mathrm{e}^{-3a}\bigr]$ —
printed, so:

**3.6a** find an antiderivative of $t\mathrm{e}^{-3t}$;

**3.6b** hence find $k$, using that the total probability is 1.
""")

code(r"""
q3_6a = ...      # an antiderivative of t*e^(-3t)
q3_6b = ...      # k

verify_antiderivative('3.6a', q3_6a, t*exp(-3*t), var=t)
# The whole area under a density is 1. Your k goes into the integrand, and the
# check adds it up all the way to infinity by pushing the limit out.
verify_integral('3.6b', 1, ... if blank(q3_6b) else q3_6b*t*exp(-3*t), 0, oo, var=t)
""")

md(r"""
## 3.7 — 3.10 · May 2023 TZ1 Paper 3 Q1(b)(c)(ii)(d) · 10 marks · calculator

This investigation is about the family $f_n(x)=x^n\mathrm{e}^{-x}$, $x\ge0$.

Part (b) shows that the area under $f_1$ between $0$ and $b$ is
$\dfrac{\mathrm{e}^b-b-1}{\mathrm{e}^b}$ — printed, so:

**3.7** find an antiderivative of $x\mathrm{e}^{-x}$. *[6]*

The total area is $A_n=\displaystyle\int_0^{\infty}f_n(x)\,\mathrm{d}x$, which
part (c)(i) shows is the limit of the expression above.

**3.8** Write down the value of $A_1$. *[1]*

**3.9** Use a GDC, with a suitable upper limit in place of $\infty$, to find
$A_4$. *[2]*

**3.10** And $A_5$. *[1]*
""")

code(r"""
q3_7 = ...        # an antiderivative of x*e^(-x)
q3_8 = ...        # A_1
q3_9 = ...        # A_4
q3_10 = ...      # A_5

verify_antiderivative('3.7', q3_7, x*exp(-x))
verify_integral('3.8', q3_8, x*exp(-x), 0, oo)
verify_integral('3.9', q3_9, x**4*exp(-x), 0, oo)
verify_integral('3.10', q3_10, x**5*exp(-x), 0, oo)
""")

# ------------------------------------------------------------------ 4
md(r"""
---
# 4. Partial fractions

*Four questions, 23 marks.* Factorise the denominator, split, integrate the
pieces. A repeated factor needs two fractions and they integrate to different
kinds of thing.
""")

md(r"""
## 4.1 · May 2021 TZ2 Paper 1 Q9 · 7 marks · no calculator

By using the substitution $u=\sin x$, find
$$\int\frac{\sin x\cos x}{\sin^2 x-\sin x-2}\,\mathrm{d}x .$$
*[7]*

**4.1a** the integrand in terms of $u$;
**4.1b** that integrand in partial fractions;
**4.1c** the antiderivative, back in terms of $x$.
""")

code(r"""
q4_1a = ...      # the integrand in u
q4_1b = ...      # split into partial fractions
q4_1c = ...      # the antiderivative in x

raw = sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2)
verify_transformed('4.1a', q4_1a, raw, sin(x))
check_apart('4.1b', q4_1b, u/(u**2 - u - 2), var=u)
verify_antiderivative('4.1c', q4_1c, raw, domain=(0.2, 1.2))
""")

md(r"""
## 4.2 · November 2021 Paper 2 Q10(e) · 7 marks · calculator

Consider $f(x)=\dfrac{x^2-x-12}{2x-15}$, so that
$\dfrac{1}{f(x)}=\dfrac{2x-15}{(x+3)(x-4)}$.

**4.2a** Express $\dfrac{1}{f(x)}$ in partial fractions. *[3]*

**4.2b** Hence find the exact value of
$\displaystyle\int_0^3\frac{1}{f(x)}\,\mathrm{d}x$, as a single logarithm. *[4]*
""")

code(r"""
q4_2a = ...      # the partial fractions
q4_2b = ...      # the exact value

check_apart('4.2a', q4_2a, (2*x - 15)/((x + 3)*(x - 4)))
verify_integral('4.2b', q4_2b, (2*x - 15)/((x + 3)*(x - 4)), 0, 3)
""")

md(r"""
## 4.3 · May 2024 TZ1 Paper 1 Q11(d)(e) · 4 marks · no calculator

With $Q(x)=(x+1)(2x+1)$:

**4.3a** Show that $\dfrac{1}{(x+1)Q(x)}$ splits into partial fractions. *[2]*

**4.3b** Hence find $\displaystyle\int\frac{\mathrm{d}x}{(x+1)^2(2x+1)}$. *[4]*

The repeated factor is the whole question: one of the three pieces integrates
to a reciprocal, not a logarithm.
""")

code(r"""
q4_3a = ...      # the partial fractions of 1/((x+1)^2 (2x+1))
q4_3b = ...      # the antiderivative

check_apart('4.3a', q4_3a, 1/((x + 1)**2*(2*x + 1)))
verify_antiderivative('4.3b', q4_3b, 1/((x + 1)**2*(2*x + 1)), domain=(0.2, 3.0))
""")

md(r"""
## 4.4 · May 2025 TZ2 Paper 3 Q1(e) · 5 marks · calculator

Using partial fractions, show that
$$\int\frac{\mathrm{d}v}{1-v^2}=\frac12\ln\left|\frac{1+v}{1-v}\right|+\frac12\ln A,$$
where $A$ is a positive constant. *[5]*

**Printed**, but worth writing out: $\tfrac12\ln A$ *is* the constant of
integration, dressed so that exponentiating both sides comes out clean. The
check differentiates, so it does not care what the constant is wearing — try
`+ C` and `- 4` in its place and watch all three pass.
""")

code(r"""
q4_4 = ...       # the antiderivative, constant dressed however you like

verify_antiderivative('4.4', q4_4, 1/(1 - v**2), var=v, domain=(0.05, 0.9))
""")

# ------------------------------------------------------------------ 5
md(r"""
---
# 5. The quotient is $f'/f$

*Three questions, 14 marks — one Paper 3 investigation.* The rule is
$\int\frac{f'}{f}=\ln|f|+c$, and the difficulty is never the rule: it is
getting the quotient into that shape, and then handling a constant that
turns from a summand into a factor.
""")

md(r"""
## 5.1 · May 2024 TZ2 Paper 3 Q1(c) · 2 marks · calculator

The investigation reaches
$\dfrac{f'(x)}{f(x)}=\dfrac{g'(x)}{g'(x)-g(x)}$ and asks you to integrate both
sides, showing that
$f(x)=A\exp\left(\int\frac{g'(x)}{g'(x)-g(x)}\,\mathrm{d}x\right)$. *[2]*

**Printed.** Do the left-hand side on the paper's own example instead: part (a)
uses $f(x)=\dfrac{1}{(x-2)^2}$. Find $\displaystyle\int\frac{f'(x)}{f(x)}\,\mathrm{d}x$
for that $f$.
""")

code(r"""
q5_1 = ...       # the antiderivative of f'/f for f(x) = 1/(x-2)^2

verify_antiderivative('5.1', q5_1, -2/(x - 2), domain=(2.4, 6.0))
""")

md(r"""
## 5.2 · May 2024 TZ2 Paper 3 Q1(d) · 5 marks · calculator

Using the result of part (c) with $A=1$: consider $g(x)=x\mathrm{e}^x$. Find
$f(x)$ such that $f$ and $g$ satisfy both
$(fg)'=fg'+gf'$ and $(fg)'=f'g'$. *[5]*
""")

code(r"""
q5_2 = ...       # f(x)

# If f = exp(∫ ...), then log f is an antiderivative of the integrand — and
# with A = 1 the constant is pinned too, so the point goes in as well.
verify_antiderivative('5.2', ... if blank(q5_2) else log(q5_2), x + 1,
                      through=(0, 0))
""")

md(r"""
## 5.3 · May 2024 TZ2 Paper 3 Q1(e) · 7 marks · calculator

The same, with $g(x)=\sin x+\cos x$ on $0<x<\pi$ and $A=1$. Give your answer
in the form $f(x)=\dfrac{\mathrm{e}^x}{h(x)}$, and hand in $h(x)$. *[7]*
""")

code(r"""
q5_3 = ...       # h(x)

verify_antiderivative('5.3', ... if blank(q5_3) else x - log(q5_3),
                      Rational(1, 2) - cot(x)/2, domain=(0.2, 2.9))
""")

# ------------------------------------------------------------------ 6
md(r"""
---
# 6. Reduction formula

*Three questions, 10 marks — one Paper 1 question.* The exponent is a letter,
so there is no single antiderivative. What there is, is a way down.

Write your formulae with `J(m)` standing for $\int\cos^m x\,\mathrm{d}x$. The
check evaluates both sides over a fixed interval for several $n$; it never
finds an antiderivative, so it cannot hand you the formula, only confirm it.
""")

md(r"""
## 6.1 · May 2025 TZ1 Paper 1 Q12(a) · 4 marks · no calculator

Consider $f_n(x)=\cos^n x$. By writing $\cos^n x$ as $\cos^{n-1}x\cos x$, show
that for $n>1$
$$\int\cos^n x\,\mathrm{d}x=\cos^{n-1}x\sin x+(n-1)\int\cos^{n-2}x\,\mathrm{d}x
-(n-1)\int\cos^n x\,\mathrm{d}x .$$
*[4]*

Write the right-hand side. The check will confirm the identity is true — get
one sign or one factor of $(n-1)$ wrong and it will not.
""")

code(r"""
q6_1 = ...       # the right-hand side, using J(n) and J(n-2)

verify_reduction('6.1', q6_1, cos(x)**n, n, J)
""")

md(r"""
## 6.2 · May 2025 TZ1 Paper 1 Q12(b) · 2 marks · no calculator

Hence show that for $n>1$
$$\int f_n(x)\,\mathrm{d}x=\frac1n\cos^{n-1}x\sin x
+\frac{n-1}{n}\int f_{n-2}(x)\,\mathrm{d}x .$$
*[2]*

Two marks for collecting the like integrals onto one side and dividing. The
version in 6.1 is unusable as it stands; this one is not.
""")

code(r"""
q6_2 = ...       # the collected right-hand side

verify_reduction('6.2', q6_2, cos(x)**n, n, J)
""")

md(r"""
## 6.3 · May 2025 TZ1 Paper 1 Q12(c) · 4 marks · no calculator

Hence find an expression for $\displaystyle\int\cos^4x\,\mathrm{d}x$, giving
your answer in the form $p\cos^3x\sin x+q\cos x\sin x+rx+c$ with
$p,q,r\in\mathbb{Q}^+$. *[4]*

Two steps down: $n=4$, then $n=2$, then $\int\cos^0x\,\mathrm{d}x=x$.
""")

code(r"""
q6_3 = ...       # an antiderivative of cos^4(x)

verify_antiderivative('6.3', q6_3, cos(x)**4)
""")

# ------------------------------------------------------------------ 7
md(r"""
---
# 7. Integrate the series

*Five questions, 12 marks.* The function has no elementary antiderivative, or
has one you are not allowed to write down yet. Expand, integrate term by term,
and stop exactly where you were told to.
""")

md(r"""
## 7.1 · November 2023 TZ1 Paper 1 Q11(d)(iii)(e) · 3 marks · no calculator

Consider $f(x)=\mathrm{e}^{\cos 2x}$.

**7.1a** Write down the Maclaurin series of $f$ up to and including the term
in $x^2$. *[1]*

Part (e) uses those two terms to show that
$\int_0^{1/10}f(x)\,\mathrm{d}x\approx\frac{149\mathrm{e}}{1500}$ — printed, so:

**7.1b** use the same two terms to approximate
$\displaystyle\int_0^{1/2}\mathrm{e}^{\cos 2x}\,\mathrm{d}x$. Exact answer. *[2]*

*The same question is printed in the November 2023 TZ2 paper, word for word.*
""")

code(r"""
q7_1a = ...      # the series up to x^2
q7_1b = ...      # the approximation to the integral from 0 to 1/2

verify_maclaurin('7.1a', q7_1a, exp(cos(2*x)), terms=2)
verify_integral('7.1b', q7_1b, q7_1a, 0, Rational(1, 2))
""")

md(r"""
## 7.2 · November 2025 TZ1 Paper 1 Q10(a)(ii) · 2 marks · no calculator

Given that the first four terms of the binomial expansion of
$\dfrac{1}{1+x^2}$ are $1-x^2+x^4-x^6$, find an approximation for
$\displaystyle\int\frac{\mathrm{d}x}{1+x^2}$ up to and including the term in
$x^7$. *[2]*
""")

code(r"""
q7_2 = ...       # the approximation, with its constant

verify_termwise('7.2', q7_2, 1/(1 + x**2), 8)
""")

md(r"""
## 7.3 · November 2025 TZ1 Paper 1 Q10(b)(ii) · 1 mark · no calculator

Given that $\dfrac{1}{\sqrt{1-x^2}}=1+\tfrac12x^2+\tfrac38x^4+\ldots$, find a
polynomial expression for $\displaystyle\int\frac{\mathrm{d}x}{\sqrt{1-x^2}}$
up to and including the term in $x^5$. *[1]*
""")

code(r"""
q7_3 = ...       # the polynomial, with its constant

verify_termwise('7.3', q7_3, 1/sqrt(1 - x**2), 6)
""")

md(r"""
## 7.4 · November 2025 TZ1 Paper 1 Q10(c) · 4 marks · no calculator

The expression $\dfrac{25}{48}+\dfrac{k}{1280}$, with $k\in\mathbb{Z}^+$, can
be used to approximate $\arcsin\tfrac12$. Use the result of 7.3 to find $k$.
*[4]*

The mark that most scripts lose here is the first one: recognising that the
integral in 7.3 *is* $\arcsin x$.
""")

code(r"""
q7_4 = ...       # k

# Checked against your own 7.3, evaluated between 0 and 1/2 — so the constant
# drops out and nothing about the answer is given away.
left  = ... if blank(q7_3, q7_4) else Rational(25, 48) + q7_4/S(1280)
right = 0 if blank(q7_3) else q7_3.subs(x, Rational(1, 2)) - q7_3.subs(x, 0)
verify_exact('7.4', left, right)
""")

md(r"""
## 7.5 · November 2025 TZ3 Paper 3 Q2(f) · 2 marks · calculator

Determine the value of
$$\int_0^{1/\sqrt3}\left(x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}\right)\mathrm{d}x,$$
giving your answer to six decimal places. *[2]*

Six decimal places, so the check is told to be strict about them.
""")

code(r"""
q7_5 = ...       # the value, to six decimal places

verify_integral('7.5', q7_5, x - x**3/3 + x**5/5 - x**7/7, 0, 1/sqrt(3),
                tol=1e-6)
""")

# ------------------------------------------------------------------ 8
md(r"""
---
# 8. The integral is a condition

*Three questions, 14 marks.* The value of the integral is what you are given.
The antiderivative is a step, and the unknown is a limit, a constant, or
nothing at all — sometimes symmetry answers the question outright.
""")

md(r"""
## 8.1 · May 2023 TZ2 Paper 1 Q4 · 6 marks · no calculator

The region $R$ is bounded by the curve $y=\dfrac{x}{x^2+2}$ (for $x\ge0$), the
$x$-axis and the line $x=c$. The area of $R$ is $\ln 3$. Find the value of $c$.
*[6]*

Your answer goes in as the upper limit, and the check integrates up to it.
""")

code(r"""
q8_1 = ...       # c

verify_integral('8.1', log(3), x/(x**2 + 2), 0, q8_1)
""")

md(r"""
## 8.2 · November 2025 TZ1 Paper 2 Q11(b) · 6 marks · calculator

The random variable $X$ has probability density function
$$f(x)=\begin{cases}3x\arccos(x^2),&0\le x\le k;\\0,&\text{otherwise.}\end{cases}$$

Part (i) shows that $k^2\arccos(k^2)-\sqrt{1-k^4}+\tfrac13=0$ — printed.

**8.2** Hence find the value of $k$, correct to six significant figures. *[6]*

This is the one place in the topic where a calculator earns its keep: that
equation has no closed-form root. Six significant figures means $0.713$ is not
an answer, and the check is set to notice.
""")

code(r"""
q8_2 = ...       # k, to six significant figures

verify_integral('8.2', 1, 3*x*acos(x**2), 0, q8_2, tol=1e-6)
""")

md(r"""
## 8.3 · May 2024 TZ1 Paper 1 Q9(c) · 2 marks · no calculator

$f$ is an odd function, and it is given that
$\displaystyle\int_0^4 f(|x|)\,\mathrm{d}x=1.6$.

Write down the value of

**8.3a** $\displaystyle\int_{-4}^{0}f(x)\,\mathrm{d}x$; *[1]*

**8.3b** $\displaystyle\int_{-4}^{4}\bigl(f(|x|)+f(x)\bigr)\mathrm{d}x$. *[1]*

$f$ exists only as a graph here, so there is no integrand to hand the check —
these two are compared as numbers. It is the only place in the notebook where
that happens.
""")

code(r"""
q8_3a = ...      # (a)
q8_3b = ...      # (b)

check_num('8.3a', q8_3a, 2, '""" + D_83A + r"""')
check_num('8.3b', q8_3b, 2, '""" + D_83B + r"""')
""")

# ------------------------------------------------------------- решения
md(r"""
---
# Solutions

## 1.1 · May 2022 TZ1 Paper 1 Q1

Rewrite before integrating: $\dfrac{5}{\sqrt x}=5x^{-1/2}$, so

$$\int\Bigl(3-5x^{-1/2}\Bigr)\mathrm{d}x=3x-\frac{5x^{1/2}}{1/2}=3x-10\sqrt x .$$

Then $\bigl[3x-10\sqrt x\bigr]_1^9=(27-30)-(3-10)=-3+7=4$. **A1A1A1M1A1**

The mark scheme gives one A1 for the rewrite alone. Both the raising of the
index and the dividing by the new index are separately marked.

## 1.2 · May 2025 TZ1 Paper 2 Q11(a)(i)

Over $2.25\le t\le4.5$ the cosine runs through exactly one half-period — from
$\cos(0)$ down to $\cos\pi$ — so its integral is zero and only the constant
survives:

$$\int_{2.25}^{4.5}\frac{4}{21}\Bigl(1-\cos\bigl(\tfrac{4\pi}{9}(t-2.25)\bigr)\Bigr)\mathrm{d}t
=\frac{4}{21}\cdot 2.25=\frac{9}{21}=\frac37 .$$
**A1**

Which is the point of the question: the first half of the race accounts for
$\tfrac37$ of the runners, exactly, and you can see it without a calculator.

## 1.3 · May 2022 TZ2 Paper 2 Q2

$g(x)=x^3+5\mathrm{e}^x+c$, and $g(0)=4$ gives $0+5+c=4$, so $c=-1$:
$$g(x)=x^3+5\mathrm{e}^x-1 .\qquad\textbf{M1A1A1M1A1}$$

The mark scheme insists the substitution be into an expression that *contains*
$+c$ — substituting into $x^3+5\mathrm{e}^x$ scores M0.

## 1.4 · November 2025 TZ1 Paper 1 Q9(e)

$f(x)=x^3+6x^2-15x+c$, and $f(-2)=-8+24+30+c=46+c=36$, so $c=-10$:
$$f(x)=x^3+6x^2-15x-10 .\qquad\textbf{M1A1M1A1}$$

## 1.5 · May 2021 TZ1 Paper 2 Q12(b)

With $f'(x)=\dfrac{1}{kx}+\dfrac{1}{k(k-x)}$, the second term integrates with
a sign change from the inside function:

$$f(x)=\frac1k\ln|x|-\frac1k\ln|k-x|+c=\frac1k\ln\left|\frac{x}{k-x}\right|+c .$$
**M1A1A1**

The $-\tfrac1k\ln|k-x|$ is where the marks go: $\dfrac{\mathrm{d}}{\mathrm{d}x}(k-x)=-1$,
and forgetting it flips the fraction inside the logarithm.

## 2.1 · May 2022 TZ2 Paper 1 Q7

$u=\sec x$ gives $\mathrm{d}u=\sec x\tan x\,\mathrm{d}x$, and the integrand
already contains that factor:

$$\sec^n x\tan x\,\mathrm{d}x=\sec^{n-1}x\cdot\underbrace{\sec x\tan x\,\mathrm{d}x}_{\mathrm{d}u}
=u^{n-1}\,\mathrm{d}u .$$

New limits: $x=0\to u=1$, $x=\tfrac\pi3\to u=2$. So

$$\int_1^2 u^{n-1}\,\mathrm{d}u=\left[\frac{u^n}{n}\right]_1^2=\frac{2^n-1}{n}.$$
**A1M1A1A1M1A1**

Method 2 in the mark scheme skips the substitution entirely and integrates by
inspection: the derivative of $\sec^n x$ is $n\sec^{n-1}x\cdot\sec x\tan x$,
so the antiderivative is $\tfrac1n\sec^n x$ — same marks, half the writing.

## 2.2 · November 2022 Paper 1 Q4

$u=1+x^2$, $\mathrm{d}u=2x\,\mathrm{d}x$, so
$\int\frac{6x}{1+x^2}\mathrm{d}x=3\int\frac{\mathrm{d}u}{u}=3\ln(1+x^2)+c$.
Then $f(1)=5$ gives $3\ln 2+c=5$, so

$$f(x)=3\ln(1+x^2)+5-3\ln 2 .\qquad\textbf{M1A1A1M1A1}$$

No modulus is needed: $1+x^2>0$ always.

## 2.3 · May 2023 TZ2 Paper 1 Q12(a)

$t=\sqrt x$ gives $x=t^2$ and $\mathrm{d}x=2t\,\mathrm{d}t$, so
$\int\cos\sqrt x\,\mathrm{d}x=\int 2t\cos t\,\mathrm{d}t$. Note that the
substitution *created* the factor $2t$ that makes the next step possible.

By parts with $u=2t$, $\mathrm{d}v=\cos t\,\mathrm{d}t$:
$$\int 2t\cos t\,\mathrm{d}t=2t\sin t-\int 2\sin t\,\mathrm{d}t=2t\sin t+2\cos t+C,$$
and $t=\sqrt x$ gives the printed answer. **M1A1A1M1A1A1**

## 3.1 · November 2023 TZ1 Paper 1 Q8(a)

$u=(\ln x)^2$, $\mathrm{d}v=x\,\mathrm{d}x$:
$$\int x(\ln x)^2\mathrm{d}x=\frac{x^2}{2}(\ln x)^2-\int x\ln x\,\mathrm{d}x .$$
The remaining integral is parts again, $u=\ln x$, $\mathrm{d}v=x\,\mathrm{d}x$:
$\int x\ln x\,\mathrm{d}x=\frac{x^2}{2}\ln x-\frac{x^2}{4}$. Hence

$$\int x(\ln x)^2\mathrm{d}x=\frac{x^2}{2}(\ln x)^2-\frac{x^2}{2}\ln x+\frac{x^2}{4}+c .$$
**M1M1A1M1A1A1**

## 3.2 · November 2023 TZ1 Paper 1 Q8(b)

With $F$ as above, $F(1)=\tfrac14$ and
$F(2)=2(\ln2)^2-2\ln2+1$, so

$$\int_1^2 x(\ln x)^2\,\mathrm{d}x=2(\ln 2)^2-2\ln 2+\frac34 \approx 0.1743 .$$

The paper's own limits, $1$ to $4$, work the same way once you replace
$\ln 4$ by $2\ln 2$ — which is what the second M1 is for.

## 3.3 · May 2025 TZ3 Paper 2 Q12(a)

$u=x^2-5$, $\mathrm{d}v=\mathrm{e}^x\mathrm{d}x$:
$$\int(x^2-5)\mathrm{e}^x\mathrm{d}x=(x^2-5)\mathrm{e}^x-\int 2x\mathrm{e}^x\mathrm{d}x
=(x^2-5)\mathrm{e}^x-\bigl(2x\mathrm{e}^x-2\mathrm{e}^x\bigr),$$
that is $(x^2-2x-3)\mathrm{e}^x+c$. **M1A1M1A1A1A1**

The polynomial dies in two steps because differentiating it twice reaches a
constant. That is the whole reason this shape always terminates.

## 3.4 · November 2025 TZ1 Paper 2 Q11(a)

There is no product until you write one: $u=\arccos x$, $\mathrm{d}v=\mathrm{d}x$,
so $v=x$ and $\mathrm{d}u=-\dfrac{\mathrm{d}x}{\sqrt{1-x^2}}$:

$$\int\arccos x\,\mathrm{d}x=x\arccos x+\int\frac{x}{\sqrt{1-x^2}}\mathrm{d}x
=x\arccos x-\sqrt{1-x^2}+c,$$

the last integral by $u=1-x^2$. **M1A1M1A1**

Method 2 substitutes $x=\cos\theta$ first and integrates by parts afterwards —
same four marks.

## 3.5 · November 2025 TZ3 Paper 3 Q2(e)

$u=\arctan x$, $\mathrm{d}v=\mathrm{d}x$:
$$\int\arctan x\,\mathrm{d}x=x\arctan x-\int\frac{x}{1+x^2}\mathrm{d}x
=x\arctan x-\frac12\ln(1+x^2)+c .$$

Between $0$ and $\tfrac1{\sqrt3}$:
$\tfrac{1}{\sqrt3}\cdot\tfrac\pi6-\tfrac12\ln\tfrac43=\dfrac{\pi}{6\sqrt3}-\dfrac12\ln\dfrac43$.
**A1A1A1A1**

## 3.6 · May 2025 TZ2 Paper 2 Q11(b), (c)(ii)

$u=t$, $\mathrm{d}v=\mathrm{e}^{-3t}\mathrm{d}t$, so $v=-\tfrac13\mathrm{e}^{-3t}$:
$$\int t\mathrm{e}^{-3t}\mathrm{d}t=-\frac{t}{3}\mathrm{e}^{-3t}
+\frac13\int\mathrm{e}^{-3t}\mathrm{d}t=-\frac{t}{3}\mathrm{e}^{-3t}-\frac19\mathrm{e}^{-3t}+c .$$

Between $0$ and $a$ that is $\tfrac19\bigl[1-(3a+1)\mathrm{e}^{-3a}\bigr]$, and
multiplying by $k$ gives the printed line. **M1A1A1A1**

For $k$: as $a\to\infty$ the bracket tends to $1$, so the total probability is
$\tfrac{k}{9}=1$ and $k=9$.

## 3.7 — 3.10 · May 2023 TZ1 Paper 3 Q1

$u=x$, $\mathrm{d}v=\mathrm{e}^{-x}\mathrm{d}x$, $v=-\mathrm{e}^{-x}$:
$$\int x\mathrm{e}^{-x}\mathrm{d}x=-x\mathrm{e}^{-x}+\int\mathrm{e}^{-x}\mathrm{d}x
=-(x+1)\mathrm{e}^{-x}+c .$$
Between $0$ and $b$: $-(b+1)\mathrm{e}^{-b}+1=\dfrac{\mathrm{e}^b-b-1}{\mathrm{e}^b}$,
the printed answer. **A1M1A1A1M1A1**

$A_1$ is the limit of that as $b\to\infty$, which part (c)(i) finds by
l'Hôpital: $A_1=1$. **A1**

$A_4=24$ and $A_5=120$ from a GDC with an upper limit around $20$ — the
integrand at $x=20$ is $20^5\mathrm{e}^{-20}\approx 0.0066$, small enough.
**M1A1A1**

And then $A_n=n!$, which part (f) proves by induction. The whole 25-mark
investigation is a derivation of the gamma function without naming it.

## 4.1 · May 2021 TZ2 Paper 1 Q9

$u=\sin x$, $\mathrm{d}u=\cos x\,\mathrm{d}x$, so the integrand becomes
$\dfrac{u}{u^2-u-2}\,\mathrm{d}u=\dfrac{u}{(u+1)(u-2)}\mathrm{d}u$.

Partial fractions: $\dfrac{u}{(u+1)(u-2)}=\dfrac{A}{u+1}+\dfrac{B}{u-2}$ gives
$A(u-2)+B(u+1)=u$; $u=-1$ gives $A=\tfrac13$, $u=2$ gives $B=\tfrac23$.

$$\int=\frac13\ln|u+1|+\frac23\ln|u-2|+C
=\frac13\ln|\sin x+1|+\frac23\ln|\sin x-2|+C .$$
**A1A1M1M1A1A1A1**

Note $\sin x-2<0$ always, which is exactly why the modulus is not optional.

## 4.2 · November 2021 Paper 2 Q10(e)

$\dfrac{2x-15}{(x+3)(x-4)}=\dfrac{A}{x+3}+\dfrac{B}{x-4}$: $x=-3$ gives
$-21=-7A$, so $A=3$; $x=4$ gives $-7=7B$, so $B=-1$.

$$\int_0^3\left(\frac{3}{x+3}-\frac{1}{x-4}\right)\mathrm{d}x
=\bigl[3\ln|x+3|-\ln|x-4|\bigr]_0^3
=(3\ln6-\ln1)-(3\ln3-\ln4).$$

$3\ln 6-3\ln 3=3\ln 2$, and $+\ln 4=2\ln 2$, so the total is
$5\ln 2=\ln 32$. **M1A1A1M1A1A1A1**

## 4.3 · May 2024 TZ1 Paper 1 Q11(d)(e)

$\dfrac{1}{(x+1)^2(2x+1)}=\dfrac{A}{x+1}+\dfrac{B}{(x+1)^2}+\dfrac{D}{2x+1}$
gives $A=-2$, $B=-1$, $D=4$, so the split is
$\dfrac{4}{2x+1}-\dfrac{2}{x+1}-\dfrac{1}{(x+1)^2}$.

Integrating each piece — and the third one is *not* a logarithm:

$$2\ln|2x+1|-2\ln|x+1|+\frac{1}{x+1}+C .$$
**A1A1M1A1**

The $\tfrac12$ from the inside function of $2x+1$ cancels against the $4$,
which is why the first coefficient comes out as $2$ and not $4$.

## 4.4 · May 2025 TZ2 Paper 3 Q1(e)

$\dfrac{1}{1-v^2}=\dfrac{1}{(1-v)(1+v)}=\dfrac{1/2}{1-v}+\dfrac{1/2}{1+v}$, so

$$\int\frac{\mathrm{d}v}{1-v^2}=-\frac12\ln|1-v|+\frac12\ln|1+v|+c
=\frac12\ln\left|\frac{1+v}{1-v}\right|+c .$$

Writing $c=\tfrac12\ln A$ is legal because $A$ ranges over all positive
numbers as $c$ ranges over $\mathbb{R}$, and it makes part (f) — where both
sides get exponentiated — come out without a stray $\mathrm{e}^{2c}$.
**M1A1M1A1A1**

## 5.1 · May 2024 TZ2 Paper 3 Q1(c)

For $f(x)=(x-2)^{-2}$: $f'(x)=-2(x-2)^{-3}$, so
$\dfrac{f'}{f}=\dfrac{-2}{x-2}$ and

$$\int\frac{f'(x)}{f(x)}\mathrm{d}x=-2\ln|x-2|+c
\ \left(=\ln\bigl|f(x)\bigr|+c\right).$$

Which is the general fact the printed part uses: integrating $f'/f$ gives
$\ln|f|$, and exponentiating turns the additive constant into the multiplier
$A=\mathrm{e}^c$. **A1A1**

## 5.2 · May 2024 TZ2 Paper 3 Q1(d)

$g=x\mathrm{e}^x$ gives $g'=(x+1)\mathrm{e}^x$ and
$g'-g=(x+1)\mathrm{e}^x-x\mathrm{e}^x=\mathrm{e}^x$, so

$$\frac{g'}{g'-g}=\frac{(x+1)\mathrm{e}^x}{\mathrm{e}^x}=x+1 .$$

Then $\int(x+1)\mathrm{d}x=\tfrac{x^2}{2}+x$ and, with $A=1$,
$f(x)=\mathrm{e}^{x+x^2/2}$. **A1M1A1M1A1**

The mark scheme awards A0 if $+c$ survives into the final answer: $A=1$ was
given, and the constant has already been used.

## 5.3 · May 2024 TZ2 Paper 3 Q1(e)

$g=\sin x+\cos x$ gives $g'=\cos x-\sin x$ and
$g'-g=-2\sin x$, so

$$\frac{g'}{g'-g}=\frac{\cos x-\sin x}{-2\sin x}=\frac12-\frac12\cot x .$$

Integrating: $\dfrac{x}{2}-\dfrac12\ln(\sin x)$ — no modulus needed, since
$0<x<\pi$ was given precisely so that $\sin x>0$. With $A=1$,

$$f(x)=\frac{\mathrm{e}^{x/2}}{\sqrt{\sin x}}
=\frac{\mathrm{e}^{x}}{\mathrm{e}^{x/2}\sqrt{\sin x}},
\qquad h(x)=\mathrm{e}^{x/2}\sqrt{\sin x}.$$
**A1M1A1M1A1A1A1**

The last two marks are for the rearrangement into the requested form. Stopping
at $\mathrm{e}^{x/2}/\sqrt{\sin x}$ is a correct function and an incomplete
answer.

## 6.1 — 6.2 · May 2025 TZ1 Paper 1 Q12(a)(b)

Split off one factor and integrate by parts with $u=\cos^{n-1}x$,
$\mathrm{d}v=\cos x\,\mathrm{d}x$:

$$\int\cos^n x\,\mathrm{d}x=\cos^{n-1}x\sin x
+(n-1)\int\cos^{n-2}x\sin^2 x\,\mathrm{d}x .$$

Now $\sin^2x=1-\cos^2x$ splits the last integral in two:

$$=\cos^{n-1}x\sin x+(n-1)\int\cos^{n-2}x\,\mathrm{d}x-(n-1)\int\cos^n x\,\mathrm{d}x .$$
**M1A1A1A1**

The formula is useless in that form — the thing you want is on both sides.
Collect it: $n\int\cos^n x\,\mathrm{d}x=\cos^{n-1}x\sin x+(n-1)\int\cos^{n-2}x\,\mathrm{d}x$,
hence

$$\int\cos^n x\,\mathrm{d}x=\frac1n\cos^{n-1}x\sin x+\frac{n-1}{n}\int\cos^{n-2}x\,\mathrm{d}x .$$
**M1A1**

## 6.3 · May 2025 TZ1 Paper 1 Q12(c)

$n=4$: $\int\cos^4=\tfrac14\cos^3x\sin x+\tfrac34\int\cos^2x\,\mathrm{d}x$.

$n=2$: $\int\cos^2=\tfrac12\cos x\sin x+\tfrac12\int\mathrm{d}x
=\tfrac12\cos x\sin x+\tfrac{x}{2}$.

Substituting back,

$$\int\cos^4x\,\mathrm{d}x=\frac14\cos^3x\sin x+\frac38\cos x\sin x+\frac38x+c,$$
so $p=\tfrac14$, $q=r=\tfrac38$. **M1M1A1A1**

The alternative route uses the double-angle formula for $\cos^2x$ instead of a
second application — same marks, and safer if you distrust your own recursion.

## 7.1 · November 2023 TZ1 Paper 1 Q11(d)(iii)(e)

$\cos 2x=1-2x^2+\tfrac23x^4-\ldots$, so
$\mathrm{e}^{\cos 2x}=\mathrm{e}\cdot\mathrm{e}^{\cos 2x-1}
=\mathrm{e}\bigl(1-2x^2+\ldots\bigr)$, and the first two non-zero terms are
$\mathrm{e}-2\mathrm{e}x^2$.

$$\int_0^{1/2}\mathrm{e}(1-2x^2)\mathrm{d}x
=\mathrm{e}\left[x-\frac{2x^3}{3}\right]_0^{1/2}
=\mathrm{e}\left(\frac12-\frac{1}{12}\right)=\frac{5\mathrm{e}}{12}\approx 1.133 .$$
**M1A1A1**

The paper's own limits stop at $\tfrac1{10}$, where the approximation is good
to four decimal places. At $\tfrac12$ the true value is $1.108$, so the error
has grown from $10^{-5}$ to $0.02$ — which is what the $x^4$ term is for.

## 7.2 · November 2025 TZ1 Paper 1 Q10(a)(ii)

Integrate the four terms one at a time, raising each index and dividing:

$$\int(1-x^2+x^4-x^6)\,\mathrm{d}x=x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}+C .$$
**A2**

That is the Maclaurin series of $\arctan x$, and the question is one of the
standard ways of deriving it.

## 7.3 · November 2025 TZ1 Paper 1 Q10(b)(ii)

$$\int\left(1+\frac{x^2}{2}+\frac{3x^4}{8}\right)\mathrm{d}x
=x+\frac{x^3}{6}+\frac{3x^5}{40}+C .\qquad\textbf{A1}$$

## 7.4 · November 2025 TZ1 Paper 1 Q10(c)

The integral in 7.3 is $\arcsin x$, so

$$\arcsin\frac12\approx\frac12+\frac16\cdot\frac18+\frac{3}{40}\cdot\frac1{32}
=\frac12+\frac1{48}+\frac{3}{1280}=\frac{25}{48}+\frac{3}{1280},$$

giving $k=3$. **A1M1A1A1**

The value is $0.523177$ against $\pi/6=0.523599$ — good to three decimal
places from three terms.

## 7.5 · November 2025 TZ3 Paper 3 Q2(f)

$$\left[\frac{x^2}{2}-\frac{x^4}{12}+\frac{x^6}{30}-\frac{x^8}{56}\right]_0^{1/\sqrt3}
=0.158422 .\qquad\textbf{A2}$$

Compare with part (e): $\int_0^{1/\sqrt3}\arctan x\,\mathrm{d}x=0.158459$.
The four terms of the series get five significant figures, and the whole
investigation is about how much better each further term makes it.

## 8.1 · May 2023 TZ2 Paper 1 Q4

$\displaystyle\int_0^c\frac{x}{x^2+2}\mathrm{d}x
=\left[\frac12\ln(x^2+2)\right]_0^c=\frac12\ln\frac{c^2+2}{2}$,
by inspection or $u=x^2+2$.

Set that equal to $\ln 3$: $\ln\dfrac{c^2+2}{2}=2\ln 3=\ln 9$, so
$c^2+2=18$, $c^2=16$, and $c=4$ since $c>0$. **M1A1M1M1A1A1**

Two of the six marks are for the log laws, and one for finishing: $c^2=16$ is
not an answer to "find the value of $c$".

## 8.2 · November 2025 TZ1 Paper 2 Q11(b)

$u=x^2$ turns $\int_0^k 3x\arccos(x^2)\mathrm{d}x$ into
$\tfrac32\int_0^{k^2}\arccos u\,\mathrm{d}u$, and part (a) has already found
that antiderivative:

$$\frac32\Bigl[u\arccos u-\sqrt{1-u^2}\Bigr]_0^{k^2}
=\frac32\Bigl(k^2\arccos(k^2)-\sqrt{1-k^4}+1\Bigr).$$

Setting that to $1$ and dividing by $\tfrac32$ gives the printed equation.
Solving it on a GDC: $k=0.713250$. **M1M1A1A2**

## 8.3 · May 2024 TZ1 Paper 1 Q9(c)

$f$ is odd, so $f(-x)=-f(x)$ and the graph on $[-4,0]$ is the graph on $[0,4]$
turned upside down. For $x\ge0$, $f(|x|)=f(x)$, so
$\int_0^4 f(x)\,\mathrm{d}x=1.6$ and

$$\int_{-4}^{0}f(x)\,\mathrm{d}x=-\int_0^4 f(x)\,\mathrm{d}x=-1.6 .$$

For the second: $f(|x|)$ is *even*, so $\int_{-4}^{4}f(|x|)\mathrm{d}x=2\cdot1.6=3.2$;
and $f$ is odd, so $\int_{-4}^{4}f(x)\mathrm{d}x=0$. The total is $3.2$.
**A1A1**

Two marks, no antiderivative, and no formula for $f$ — the whole question is
the two symmetry facts.

---
### What the topic looks like from above

| technique | questions | marks |
| --- | --- | --- |
| Integration by parts | 10 | 37 |
| Partial fractions | 4 | 23 |
| The antiderivative is in the table | 5 | 18 |
| Substitution | 3 | 17 |
| The quotient is $f'/f$ | 3 | 14 |
| The integral is a condition | 3 | 14 |
| Integrate the series | 5 | 12 |
| Reduction formula | 3 | 10 |

Three things worth noticing once you have worked through them all.

**Parts is a quarter of the topic and the only technique on every paper.**
Eighteen marks on Paper 1, fourteen on Paper 2, fourteen on Paper 3.

**Eighty-six of the 145 marks are Paper 1.** This is the least
calculator-flavoured topic in the archive, and the 45% of marks that formally
allow one is the most misleading figure in the whole series. The calculator
does real work exactly twice: $A_4$ and $A_5$ in 3.9–3.10, and $k=0.713250$
in 8.2.

**Nine questions of the 36 print their own answer.** *Show that*, *hence
show*, *by using integration by parts, show*. In every one of those this
notebook asks for the step instead — the antiderivative, the substituted
integrand, or the same integral between other limits — because a printed
answer teaches nothing and checks nothing.

**A note on November 2023.** The corpus holds that session as two zones, TZ1
and TZ2, and counts its questions twice. They are the same paper: all twelve
questions of Paper 1 and nine of the twelve on Paper 2 are identical word for
word, and the only line that differs is the paper's own code, 8823–7106
against 8823–7111. Three blocks of this topic — 3.1, 3.2 and 7.1 — are
therefore in the corpus twice and here once. That double count is worth 12 of
the 157 marks the corpus reports for E5, which is why this notebook says 145.
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
