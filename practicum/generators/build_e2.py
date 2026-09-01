"""Собирает практикум E2: ряды Маклорена.

Шестой практикум серии на английском. Лестница из девяти приёмов делится
ровно по тому, что с рядом делают: приёмы 1–5 его строят, 6–7 получают
из другого ряда или прямо из уравнения, 8–9 им пользуются.

Три проверки здесь новые и живут в kit вместе с практикумом.

`verify_maclaurin` эталона не хранит. Ряд Маклорена — не какой-то многочлен,
который надо угадать, а единственный многочлен своей степени, прилегающий
к функции в нуле теснее прочих; проверка вычитает написанное из функции
и смотрит, с какой степени начинается остаток. Это и есть определение,
и сверять при таком определении не с чем.

`verify_series_solution` — для приёма 7, где функции нет вовсе: она задана
уравнением. Проверка подставляет многочлен в уравнение и требует, чтобы
невязка обнулилась до нужной степени.

`verify_terms` — для приёма 9. Ошибка от n членов знакочередующегося ряда
оценивается членом n + 1, и вся потеря баллов темы здесь одна: границу
примеряют не к тому члену. Проверка примеряет её к обоим соседям и говорит,
в какую сторону промах.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e2.py прогоняет по нему весь ноутбук и требует,
чтобы каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp
from kit import digest, sig

R = sp.Rational
x = sp.Symbol('x')
n, m, a, r = sp.symbols('n m a r')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e2-maclaurin.ipynb')


def dn(value, sf=6):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(sp.sympify(expr))))


# --- хеши; все до одного — приближения, подставлять их некуда ---
D_10B = dn(sp.N(3 - 3*R(15, 100) + R(3, 2)*R(15, 100)**2
                + R(3, 2)*R(15, 100)**3, 12), 6)     # y(0.15)
D_11A = de(R(61, 105))                               # интеграл через ряд
D_12A = dn(3.156, 4)                                 # π к трём знакам
D_12C = dn(3.69e-5, 2)                               # ошибка приближения
D_12D = dn(float(1) / 21870, 3)                      # граница по теореме
D_TA = de(R(500, 279))                               # √3 на таймере

TRIGGER = {1: 'mult', 2: 'sub', 3: 'binom', 4: 'def', 5: 'comp',
           6: 'termwise', 7: 'ode', 8: 'approx', 9: 'error', 10: 'sub',
           11: 'termwise', 12: 'def'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': 'x**2 - x**6/6',
    'q1b': '1 - 2*x**2 + 2*x**4/3',
    'q2': '1 + 4*x + 10*x**2 + 20*x**3',
    'q3': 'x**2 + x**3 + x**4/2',
    'q4': '1 - n*x**2/2',
    'q5': 'x + x**2 + x**3/3',
    'q6a': 'x**4 - x**8/3',
    'q6b': '4*x**3 - 8*x**7/3',
    'q7a': '1 - 2*x**2 + 8*x**4/3',
    'q7b': 'E*(1 - 2*x**2 + 8*x**4/3)',
    'q8': '[Rational(3, 2), -Rational(5, 2)]',
    'q9a': 'a/(1 - r)**2',
    'q9b': 'sqrt(2)/2',
    'q9c': '1/(1 + 2*x**2)',
    'q10a': '3 - 3*x + 3*x**2/2 + 3*x**3/2',
    'q10b': '2.58881',
    'q11a': 'Rational(61, 105)',
    'q11b': '4*pi',
    'q12a': '3.156',
    'q12b': '6',
    'q12c': '3.69e-5',
    'q12d': 'Rational(1, 21870)',
    'qt_a': '1 + a*x/2 + 3*a**2*x**2/8',
    'qt_b': 'Rational(500, 279)',
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
# Practicum E2: Maclaurin series

**99 marks, 26 blocks, nine techniques.** Every question in this topic is
the same trade: you give up a function and get a polynomial back. The
polynomial is wrong everywhere except near zero, and near zero it is wrong
by so little that you can integrate it, divide by $x^3$, or put a number
into it and call the answer $\pi$.

**Material.** All of `calculus.series` from the AA HL archive, sessions
May 2021 — November 2025. The corpus records 27 blocks; one is a duplicate,
the November 2023 question on $\mathrm{e}^{\cos 2x}$ set word for word in
TZ1 and TZ2.

**This practicum is in English,** like B2 to B5 and E1. The checks speak
whichever language the notebook asks them to, and this one asks for English
in the setup cell.

**The one thing to carry out of here.**

> There are five series you have to know cold — $\mathrm{e}^x$, $\sin x$,
> $\cos x$, $\ln(1+x)$, $\arctan x$ — and almost every question begins by
> recognising one of them under a disguise. When none of them fits, you
> fall back on $f^{(n)}(0)/n!$, and that is slower, so look properly first.

The disguises are the topic. $\sin(x^2)$ is the sine series. $\sec x$ is
the binomial series with $\cos x-1$ inside it. $\sum(-2x^2)^r$ is the
geometric series, which is the Maclaurin series of $\frac{1}{1+2x^2}$ read
backwards. $\arctan x$ is that same geometric series integrated.

**Where the calculator sits — and this time it matters.** 43% of the marks
carry one, and unlike the four topics before this one, that is not an
illusion. Paper 1 wants $x+x^2+\frac{x^3}{3}$ and $m=\frac32,-\frac52$:
exact, always. Paper 3 wants $\pi\approx3.1412$ and an error of
$3.7\times10^{-5}$, and there is no exact form to hide behind. The second
half of this practicum is arithmetic on purpose.

**How the checks work here.** Three of them are new.

* `verify_maclaurin` does not know the answer. A Maclaurin polynomial is
  not some polynomial to be guessed: it is the one that hugs the function
  at zero closely enough, and closeness is a property of your answer and
  the function alone. So the check subtracts what you wrote from the
  function in the question and asks where the remainder starts. If it
  starts above the power you were asked for, the answer is right; if it
  starts at $x^2$, it tells you that and nothing more.

  It condones extra correct terms, because the markscheme does — *condone
  presence of any additional terms once the first two correct terms are
  seen.*

* `verify_series_solution` is for the technique where there is no function
  at all, only a differential equation. It puts your polynomial into the
  equation and into the initial condition, and reports the first term that
  does not fit.

* `verify_terms` is for the last technique. The error left by $n$ terms of
  an alternating series is bounded by term number $n+1$, and the whole of
  the loss in these questions is trying the bound on term $n$ instead. The
  check tries it on both neighbours and says which way you went wrong.

**How to work**

1. Read the map of techniques first. It is arranged by **where the series
   is going to come from**.
2. Work **on paper**. Fourteen of the twenty-six blocks are Paper 1.
3. Exact answers in Part I and II: `x + x**2 + x**3/3`, `1 - n*x**2/2`,
   `E*(1 - 2*x**2 + 8*x**4/3)`.
4. Decimals in Part III, and to the number of figures asked for.
5. A series is entered as a plain polynomial — no `+ ...`, no `O(x**4)`.
6. The last three blocks are the November 2025 Paper 3 investigation, a
   recognition trainer, and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, series, Sum

language('en')                 # this notebook is in English, and so are the checks

a, b, c, d, m, n, r = symbols('a b c d m n r')

print('ready; sympy', sp.__version__)
print('a series, written out: ', x + x**2 + x**3/3)
print('a series with a letter:', 1 - n*x**2/2)
print('a series with e in it: ', E*(1 - 2*x**2))
print('an exact number:       ', Rational(500, 279))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | From the definition | no known series fits; the part before found $f^{(n)}$ | $f^{(n)}(0)$, then divide by $n!$ |
| 2 | Substitute into a known series | $\sin(x^2)$, $\cos 2x$, $\mathrm{e}^{-3x}$ | replace $x$ by the whole new argument |
| 3 | The binomial series | a bracket to a fractional or negative power | force it into $(1+u)^p$ |
| 4 | Multiply two series | a product of two functions you both know | expand each with room, multiply, truncate as you go |
| 5 | A series inside a series | $\mathrm{e}^{\cos 2x}$, $\sec x$ | make the inside vanish at $0$ first |
| 6 | Differentiate or integrate | «use integration to show», a geometric series | do it term by term; find the constant |
| 7 | Out of a differential equation | $y$ given by an equation and $y(0)$ | differentiate the equation, implicitly |
| 8 | The series in place of the function | «hence», an integral with no antiderivative | swap it in and do the easy thing |
| 9 | How wrong it is | «error», $0.0001$, $1\times10^{-6}$ | the next term is the bound |

**The ladder goes by where the series comes from.**

**Rungs 1–5 — you are building it.** Forty-five of the ninety-nine marks,
and the choice between the five is most of the work. It is settled by
looking at the function before writing anything: a product goes to rung 4,
a bracket to a strange power goes to rung 3, a familiar function with a new
argument goes to rung 2, a familiar function with a *series* inside goes to
rung 5 — and rung 1 is the fallback when none of them fits, which in this
archive means the part before has already handed you the derivatives.

**Rungs 6–7 — it comes from something else.** From a series you already
have, differentiated or integrated; or from an equation, when no formula
for the function exists at all. These two are the cleverest questions in
the topic and the shortest to write down.

**Rungs 8–9 — you are spending it.** The series stands in for the
function, and then a limit, an integral or a number falls out. Rung 9 is
the only place in the whole AA HL archive where anyone asks how good the
approximation actually is.

**The five you must know.** They are in the formula booklet, and looking
them up costs you the twenty seconds in which you were supposed to
recognise the disguise.

$$\mathrm{e}^x=1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\dots\qquad
 \sin x=x-\frac{x^3}{3!}+\frac{x^5}{5!}-\dots\qquad
 \cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\dots$$
$$\ln(1+x)=x-\frac{x^2}{2}+\frac{x^3}{3}-\dots\qquad
 \arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\dots$$
""")

# ================================================================== Part I
md(r"""
---
# Part I — building the series

## Theory 1. Substitution is the first thing to try

$\sin(x^2)$ is not a new function. It is $\sin u$ with $u=x^2$, and the
series for $\sin u$ is known, so put $x^2$ where $u$ was:

$$\sin(x^2)=x^2-\frac{(x^2)^3}{3!}+\dots=x^2-\frac{x^6}{6}+\dots$$

Two things go wrong here, and both go wrong to nearly everybody.

**The whole argument gets substituted, power and all.** $(x^2)^3$ is $x^6$,
not $x^3$. If you catch yourself writing $-\frac{x^3}{6}$, you substituted
into the exponent instead of into the variable.

**How deep to expand changes.** For $\cos 2x$ up to $x^4$ you need three
terms of the cosine series, because $(2x)^4$ lands on $x^4$. For
$\sin(x^2)$ up to $x^6$ you need two, because $(x^2)^3$ already lands
there. Work out which power of the original series reaches your target
*before* you start writing.

And a phrase worth reading carefully: **"the first two non-zero terms"**
is not "the first two terms". Every one of these functions is even or odd,
so half its coefficients are zero, and counting the zeros is a way to
lose both marks while writing the right series.
""")

md(r"""
## Task 1 🟢 — the same substitution twice

*May 2024 TZ1 Paper 1 Q8(a)(i), 2 marks · November 2023 TZ1 Paper 1
Q11(d)(i), part of 6 marks*

**(a)** Find the first two non-zero terms in the Maclaurin series of
$\sin\!\left(x^2\right)$.

**(b)** Find the Maclaurin series for $\cos 2x$, up to and including the
term in $x^4$.
""")

code(r"""
q1a = ...        # the first two non-zero terms of sin(x^2)
q1b = ...        # cos(2x) up to and including x^4

verify_maclaurin('1a', q1a, sin(x**2), terms=2)
verify_maclaurin('1b', q1b, cos(2*x), order=4)
""")

md(r"""
## Theory 2. The binomial series, when the power is not a whole number

$$(1+u)^p=1+pu+\frac{p(p-1)}{2!}u^2+\frac{p(p-1)(p-2)}{3!}u^3+\dots,
 \qquad |u|<1 .$$

For a whole positive $p$ the coefficients run out and this is the ordinary
binomial theorem of A3. For $p=-4$ or $p=-\frac12$ they never run out, and
the expansion is a Maclaurin series like any other — which is why it lives
here as well as there.

**The bracket must start with $1$.** $(2-x)^{1/2}$ cannot be expanded until
it is $\sqrt2\left(1-\frac x2\right)^{1/2}$. Taking the factor out is the
first mark whenever the question needs it.

**The sign travels with $u$.** For $(1-x)^{-4}$ you have $u=-x$, and the
coefficient of $x^2$ is $\frac{(-4)(-5)}{2}(-x)^2=10x^2$: four minus signs,
all cancelling. Every coefficient of $(1-x)^{-4}$ comes out positive, and
if yours alternate you dropped one of them.

**$|u|<1$ is part of the answer** when the question asks for it. For a
product of two such brackets, both conditions have to hold and the tighter
one wins.
""")

md(r"""
## Task 2 🟢 — a negative index

*November 2025 TZ1 Paper 1 Q5(a), 5 marks*

The first four terms of the Maclaurin series expansion of $(1-x)^{-4}$ are
$$1+ax+bx^2+20x^3,\qquad a,b\in\mathbb{Z}^+ .$$

(i) Show that $a=4$.  (ii) Find the value of $b$.

*Enter the whole series up to $x^3$ — the two parts together.*
""")

code(r"""
q2 = ...         # 1 + a*x + b*x**2 + 20*x**3, with the letters filled in

verify_maclaurin('2', q2, (1 - x)**-4, order=3)
""")

md(r"""
## Theory 3. From the definition — and why it is almost never the fast way

$$f(x)=f(0)+f'(0)\,x+\frac{f''(0)}{2!}x^2+\frac{f'''(0)}{3!}x^3+\dots$$

This always works and is almost always slower than recognising a known
series. It earns its place in two situations, and both are all over this
archive.

**The derivatives have been handed to you.** The part before asked you to
prove $\frac{\mathrm{d}^n}{\mathrm{d}x^n}(x^2\mathrm{e}^x)$ by induction,
or to show that $g''=2(g'-g)$. That is not a separate question — it is the
supply of $f^{(n)}(0)$, and *hence* means use it.

**A relation, not a formula.** When you are given $g''=2(g'-g)$, substitute
$x=0$ **into the relation**. It stops being about functions and becomes
arithmetic on numbers: $g''(0)=2(g'(0)-g(0))$, then $g'''(0)$, then
$g^{(4)}(0)$, each from the two before it.

**The factorial is the whole thing.** $f'''(0)=9$ gives the term
$\frac{9}{3!}x^3=\frac32x^3$, not $9x^3$. In every question of this kind
the marks that go missing are the divisions by $n!$, and there is nothing
subtle about it: it is simply forgotten under time pressure.

A zero coefficient is a coefficient. If $g''(0)=0$, the $x^2$ term is
absent and the series still has an $x^3$ term after it — do not shuffle the
others down into the hole.
""")

md(r"""
## Task 3 🟡 — with the derivatives supplied

*November 2021 Paper 1 Q11(b), 3 marks*

It is given that
$$\frac{\mathrm{d}^n}{\mathrm{d}x^n}\!\left(x^2\mathrm{e}^x\right)
 =\left[x^2+2nx+n(n-1)\right]\mathrm{e}^x,\qquad n\in\mathbb{Z}^+ .$$

Hence or otherwise, determine the Maclaurin series of $f(x)=x^2\mathrm{e}^x$
in ascending powers of $x$, up to and including the term in $x^4$.
""")

code(r"""
q3 = ...

verify_maclaurin('3', q3, x**2 * exp(x), order=4)
""")

md(r"""
## Task 4 🟡 — a letter in the answer

*May 2025 TZ1 Paper 1 Q12(e)(i), 3 marks*

Consider the family of functions $f_n(x)=\cos^n x$, where $x\in\mathbb{R}$
and $n\in\mathbb{N}$.

Find the Maclaurin series of $f_n(x)$ up to the term in $x^2$.

*Two routes: differentiate $\cos^n x$ twice, or expand
$\left(1-\frac{x^2}{2}+\dots\right)^n$ binomially and keep two terms. The
second is three lines shorter. The check runs your answer at $n=2$, $n=3$
and $n=7$, so it has to hold for every $n$, not one.*
""")

code(r"""
q4 = ...         # in terms of n

verify_maclaurin('4', q4, cos(x)**n, order=2, params={n: (2, 3, 7)})
""")

# ================================================================= Part II
md(r"""
---
# Part II — putting series together

## Theory 4. Multiplying, and how deep each factor has to go

The commonest technique in the topic — $21$ of the $99$ marks. Expand both
factors, multiply, keep the powers you were asked for.

**Truncate as you go, not at the end.** Multiplying two four-term
polynomials gives sixteen products, of which you want four. Writing all
sixteen is how the question runs out of time.

**The two factors need different depths.** For $\mathrm{e}^x\sin x$ up to
$x^3$:

$$\mathrm{e}^x=1+x+\frac{x^2}{2}+\frac{x^3}{6},\qquad
 \sin x=x-\frac{x^3}{6}$$

three terms of the exponential and two of the sine, because $\sin x$ starts
at $x^1$ and every one of its terms gets pushed up by whatever it meets.
Symmetric truncation is the standard way to lose the last coefficient.

**Squaring is multiplying.** $\left(x^2-\frac{x^6}{6}\right)^2$ is
$x^4-\frac{x^8}{3}+\dots$, and the middle term $2\cdot x^2\cdot
\frac{x^6}{6}$ is the mark. The markscheme for May 2024 awards **M0** —
not one mark of the three — for squaring term by term.

**The constant term is a check you can do in one second.** It is the
product of the two constant terms, always. If yours is not, stop and look.
""")

md(r"""
## Task 5 🟢 — a product of two standard series

*May 2022 TZ1 Paper 1 Q12(a), 4 marks*

The function $f$ is defined by $f(x)=\mathrm{e}^x\sin x$, where
$x\in\mathbb{R}$.

Find the Maclaurin series for $f(x)$ up to and including the $x^3$ term.
""")

code(r"""
q5 = ...

verify_maclaurin('5', q5, exp(x)*sin(x), order=3)
""")

md(r"""
## Task 6 🟡 — a square, then a shortcut

*May 2024 TZ1 Paper 1 Q8(a)(ii), 3 marks · Q8(b), 2 marks*

**(a)** Find the first two non-zero terms in the Maclaurin series of
$\sin^2\!\left(x^2\right)$.

**(b)** Hence, or otherwise, find the first two non-zero terms in the
Maclaurin series of $4x\sin\!\left(x^2\right)\cos\!\left(x^2\right)$.

*Part (b) is worth two marks and there is a way to do it in one line.
Look at what part (a) is, and at what its derivative is.*
""")

code(r"""
q6a = ...
q6b = ...

verify_maclaurin('6a', q6a, sin(x**2)**2, terms=2)
verify_maclaurin('6b', q6b, 4*x*sin(x**2)*cos(x**2), terms=2)
""")

md(r"""
## Theory 5. A series inside a series

Section 2 substituted a single power into a known series. Now what goes
inside is itself a series, and one condition suddenly matters:

> **The inside has to vanish at zero.**

$\mathrm{e}^u$ is expanded about $u=0$. At $x=0$, $\cos 2x$ equals $1$, not
$0$ — so $\mathrm{e}^{\cos 2x}$ cannot be expanded by substituting
$\cos 2x$ for $u$. The repair is to subtract the $1$ and put it back
outside:

$$\mathrm{e}^{\cos 2x}=\mathrm{e}\cdot\mathrm{e}^{\cos 2x-1},$$

and now the exponent does vanish at zero. November 2023 walks you through
exactly this in three parts, which is the examiner telling you that the
step is the question.

The same trick builds $\sec x$ out of nothing:

$$\sec x=\frac{1}{\cos x}=\frac{1}{1-(1-\cos x)}=(1+t)^{-1},
 \qquad t=\cos x-1 .$$

**Powers of the inside.** $u^2$ and $u^3$ have to be expanded too, but only
as far as they reach. If $u=-2x^2+\frac{2x^4}{3}$, then up to $x^4$ the
square is just $(-2x^2)^2=4x^4$ — the cross term is $x^6$ and out of range.
Taking only the leading term of $u$ inside $u^2$ is right; taking only the
leading term of $u$ *outside* loses a coefficient.

**The factor put outside must come back.** Writing the series for
$\mathrm{e}^{\cos 2x-1}$ and forgetting to multiply by $\mathrm{e}$ is a
whole mark, and it is the last line of the question.
""")

md(r"""
## Task 7 🔴 — three parts of one November question

*November 2023 TZ1 Paper 1 Q11(d)(ii) and (iii), part of 6 marks*

Consider $f(x)=\mathrm{e}^{\cos 2x}$. You found the series for $\cos 2x$
in Task 1(b).

**(a)** Hence, find the Maclaurin series for $\mathrm{e}^{\cos 2x-1}$, up
to and including the term in $x^4$.

**(b)** Hence, write down the Maclaurin series for $f(x)$, up to and
including the term in $x^4$.
""")

code(r"""
q7a = ...        # the series for e^(cos 2x - 1)
q7b = ...        # the series for e^(cos 2x)   -- E is Euler's number in kit

verify_maclaurin('7a', q7a, exp(cos(2*x) - 1), order=4)
verify_maclaurin('7b', q7b, exp(cos(2*x)),     order=4)
""")

md(r"""
## Task 8 🔴 — the coefficient is the equation

*May 2021 TZ1 Paper 1 Q12(c), 8 marks*

Let $f(x)=\sqrt{1+x}$ for $x>-1$, and let $g(x)=\mathrm{e}^{mx}$,
$m\in\mathbb{Q}$. Consider $h(x)=f(x)\times g(x)$ for $x>-1$.

It is given that the $x^2$ term in the Maclaurin series for $h(x)$ has a
coefficient of $\frac74$. Find the possible values of $m$.

*Eight marks, and only three of them are the multiplication. The rest is a
quadratic. Watch the $2!$: the coefficient of $x^2$ is
$\frac{h''(0)}{2!}$, and confusing the two turns $\frac74$ into
$\frac72$.*
""")

code(r"""
H = sqrt(1 + x) * exp(m*x)

q8 = [...]       # all the values of m, as a list

# The check puts each of your values back where the question puts it: into
# the coefficient of x^2, which has to come out as 7/4. Then it scans the
# window for values you missed.
verify_roots('8', q8, series(H, x, 0, 3).removeO().coeff(x, 2) - Rational(7, 4),
             (-10, 10), var=m)
""")

# ================================================================ Part III
md(r"""
---
# Part III — spending the series

## Theory 6. Differentiating and integrating, term by term

A series can be differentiated or integrated one term at a time, and that
is often the only sane way to get the one you want.

The tell is a geometric series in the question. $1+u+u^2+\dots=\frac{1}{1-u}$
is a Maclaurin series — the one everybody uses without noticing — and it
runs in both directions:

$$\frac{1}{1+x^2}=1-x^2+x^4-x^6+\dots
 \;\xrightarrow{\ \int\ }\;
 \arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\dots$$

That is where the series for $\arctan x$ in the formula booklet comes from,
and November 2025 asks you to produce it.

**Integration brings a constant, and the constant is a mark.** Write
$+C$, then put $x=0$: $\arctan 0=0$, so $C=0$. Skipping the line loses the
mark even though the constant is zero.

**Differentiating the closed form needs the chain rule.**
$\frac{\mathrm{d}}{\mathrm{d}r}\frac{a}{1-r}=\frac{a}{(1-r)^2}$: the minus
from differentiating $(1-r)$ cancels the minus from the power, which is
why the answer is positive and squared.

**Backwards counts too.** If a question hands you $\sum_{r=0}^{n}(-2x^2)^r$
and asks for the function, recognise the geometric series and fold it up
into $\frac{1}{1+2x^2}$. Same identity, read right to left — and the radius
of convergence comes with it: $|-2x^2|<1$ means $|x|<\frac{1}{\sqrt2}$.
""")

md(r"""
## Task 9 🟡 — both directions

*May 2024 TZ1 Paper 3 Q1(c)(i), 4 marks · May 2025 TZ1 Paper 2 Q12(c),
5 marks*

**(a)** For an infinite geometric sequence with first term $a$ and common
ratio $r$ $(|r|<1)$,
$$a+ar+ar^2+ar^3+\dots=\frac{a}{1-r}.$$
By differentiating both sides with respect to $r$, find an expression for
$\displaystyle\sum_{n=1}^{\infty} n\,a\,r^{\,n-1}$ in terms of $a$ and $r$.

**(b)** Now the other direction. Consider
$\displaystyle f_n(x)=\sum_{r=0}^{n}\left(-2x^2\right)^r$ and
$f(x)=\lim_{n\to\infty}f_n(x)$, defined on $-k<x<k$ where $k>0$. The
largest possible value of $k$ is $K$.

  (i) Find $K$, in exact form.
  (ii) Express $f(x)$ as a rational function $\frac{1}{a+bx^2}$.
""")

code(r"""
q9a = ...        # the sum, in terms of a and r
q9b = ...        # K, exact
q9c = ...        # f(x) as a rational function

verify_identity('9a', q9a, diff(a/(1 - r), r), var=r)
verify_exact('9b', q9b, 1/sqrt(2))

# For (ii) the check has no closed form to compare against: it sums the
# series from the question far enough that the tail cannot be seen, and
# asks whether your rational function agrees inside the domain.
PARTIAL = Sum((-2*x**2)**r, (r, 0, 200)).doit()
verify_identity('9c', q9c, PARTIAL, var=x,
                samples=(0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4))
""")

md(r"""
## Theory 7. When there is no formula for the function at all

$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{x^2y-y}{x^2+1},\qquad y(0)=3 .$$

There is no $y=\dots$ here, and the question still asks for the Maclaurin
series of $y$. It can, because the series only needs the derivatives at one
point, and the equation produces them one at a time:

* put $x=0$ and $y=3$ into the equation → $y'(0)=-3$;
* differentiate the whole equation → an expression for $y''$ in terms of
  $x$, $y$ and $y'$; put $x=0$ and what you have → $y''(0)$;
* differentiate again → $y'''(0)$; and so on for as many terms as asked.

**The one thing that goes wrong.** The right-hand side contains $y$, and
$y$ is a function of $x$. Differentiating it produces
$\frac{\mathrm{d}y}{\mathrm{d}x}$, by the chain rule. Treating $y$ as a
constant makes the second derivative wrong and everything above it too.

**Do not substitute $x=0$ too early.** Put the numbers in *after*
differentiating, not before: a differentiated equation is still an
equation, but a number is not.

**And divide by $n!$.** $y'''(0)=9$ gives $\frac{9}{3!}x^3=\frac32x^3$.
""")

md(r"""
## Task 10 🟡 — a series out of an equation

*May 2023 TZ1 Paper 2 Q12(c), 3 marks*

Consider the differential equation
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{x^2y-y}{x^2+1},$$
where $y>0$ and $y=3$ when $x=0$. It has been shown that
$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}=3$ when $x=0$.

**(a)** Given that $\frac{\mathrm{d}^3y}{\mathrm{d}x^3}=9$ when $x=0$, find
the first four terms of the Maclaurin series for $y$.

**(b)** Use the Maclaurin series to find an approximate value for $y$ when
$x=0.15$. Give your answer correct to six significant figures.
""")

code(r"""
RHS = (x**2*y - y)/(x**2 + 1)

q10a = ...       # the first four terms
q10b = ...       # y(0.15), six significant figures

# There is no function to compare with. The check puts your polynomial into
# the equation instead, and into the initial condition.
verify_series_solution('10a', q10a, RHS, ic=3, order=3)
check_num('10b', q10b, 6, '""" + D_10B + r"""')
""")

md(r"""
## Theory 8. The series in place of the function

Now the point of all of it. A polynomial can be integrated, cancelled and
evaluated; the function often cannot.

$$\int_0^1\mathrm{e}^{x^2}\sin\!\left(x^2\right)\mathrm{d}x$$

has no antiderivative in closed form. That is not an obstacle to the
question — it *is* the question. Substitute $x^2$ into the series you
already found for $\mathrm{e}^x\sin x$, integrate the polynomial, and the
answer is $\frac{61}{105}$.

**«Hence» names the series you are meant to use.** It almost always points
at the part immediately above. Solving the question again from scratch may
still earn the answer marks and will not earn the method ones.

**A limit falls out the same way.** Replace each function by its series,
cancel the power of $x$ in the denominator, read the constant term. That is
E1's technique arriving from this side, and when the previous part built
the series it is three lines against l'Hôpital's page.

**Say where the approximation is legal.** A series expansion is valid only
inside its radius; an approximation used at $x=\frac12$ when the radius is
$\frac14$ is not an approximation, it is a wrong answer.
""")

md(r"""
## Task 11 🟡 — an integral and a limit

*May 2022 TZ1 Paper 1 Q12(b), 4 marks · May 2021 TZ1 Paper 3 Q2(e)(i),
3 marks*

**(a)** You found in Task 5 that
$\mathrm{e}^x\sin x=x+x^2+\frac{x^3}{3}+\dots$

Hence, find an approximate value for
$\displaystyle\int_0^1\mathrm{e}^{x^2}\sin\!\left(x^2\right)\mathrm{d}x$.
Give the exact fraction.

**(b)** The Maclaurin series for $\tan x$ is
$x+\frac{x^3}{3}+\frac{2x^5}{15}+\dots$

Use it to find
$\displaystyle\lim_{n\to\infty}\left(4n\tan\frac{\pi}{n}\right)$.
""")

code(r"""
q11a = ...       # the exact fraction
q11b = ...       # the limit

check_expr('11a', q11a, '""" + D_11A + r"""')
verify_limit('11b', q11b, 4*n*tan(pi/n), var=n, point=oo)
""")

md(r"""
## Theory 9. The same series in Paper 3: how wrong is it?

Everywhere above, the series was exact enough and nobody asked. November
2025 Paper 3 asks, and it is the only place in the archive that does.

It can ask because the series for $\arctan x$ **alternates** and its terms
shrink:

> **Theorem.** For an alternating series with terms of decreasing
> magnitude, the error from using a finite number of terms is at most the
> absolute value of the next term.

That is the whole of rung 9, and it turns an approximation into a
guarantee. With $x=\frac{1}{\sqrt3}$, where
$\arctan\frac{1}{\sqrt3}=\frac{\pi}{6}$, the series computes $\pi$ and the
theorem says how well.

**This is the Paper 1 / Paper 3 split made visible.** Same series, same
substitution. On Paper 1 you would be asked for the exact form and stop.
Here you are asked for $\pi$ to four decimal places, for the number of
terms that buys an error under $10^{-6}$, and for the actual error against
the bound — three things a calculator has to do, and none of them has an
exact form to hide behind.

**The one mistake.** The error from $n$ terms is bounded by term number
$n+1$. Solving the inequality gives you the index of the first term small
enough to *drop*; the answer is one less than that. The markscheme for this
question lists three different indexings students use and gives full marks
for each, because all three end at the same count — the counting is what is
being marked.
""")

md(r"""
## Task 12 🔴 — the November 2025 investigation

*November 2025 TZ3 Paper 3 Q2(c), 3 marks · (d), 3 marks · (h), 5 marks*

Throughout, $\arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}+\dots$

**(a)** Using $x=\frac{1}{\sqrt3}$ and the first **three** non-zero terms,
find an approximation for $\pi$ to three decimal places.

**(b)** Determine how many non-zero terms of the series would need to be
used, such that the error in approximating
$\arctan\!\left(\frac{1}{\sqrt3}\right)$ is less than $0.0001$.

**(c)** It is given that
$\int_0^{1/\sqrt3}\arctan x\,\mathrm{d}x=\frac{\pi}{6\sqrt3}-\frac12\ln\frac43$,
and that the same integral taken over the first **four** terms of the
series comes to $0.158422$.

Verify that the theorem holds here: state the actual error (to two
significant figures) and the bound the theorem gives (exactly).
""")

code(r"""
# Term number k of the series for arctan(1/sqrt(3)), ignoring its sign.
TERM = (1/sqrt(3))**(2*k - 1) / (2*k - 1)

q12a = ...       # pi, to three decimal places
q12b = ...       # how many non-zero terms
q12c = ...       # the actual error, two significant figures
q12d = ...       # the bound the theorem gives, exactly

check_num('12a', q12a, 4, '""" + D_12A + r"""')
verify_terms('12b', q12b, TERM, 0.0001)
check_num('12c', q12c, 2, '""" + D_12C + r"""')
check_num('12d', q12d, 3, '""" + D_12D + r"""')
""")

# ================================================================ тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **where the series is
going to come from**. That is the decision the whole topic turns on, and on
the paper you get about five seconds of it before you have committed.

| code | technique |
| --- | --- |
| `def` | from the definition, $f^{(n)}(0)/n!$ |
| `sub` | substitute into a known series |
| `binom` | the binomial series |
| `mult` | multiply two series |
| `comp` | a series inside a series |
| `termwise` | differentiate or integrate a series |
| `ode` | out of a differential equation |
| `approx` | use the series in place of the function |
| `error` | bound the error, count the terms |

1. Find the Maclaurin series for $\mathrm{e}^x\sin x$ up to the $x^3$ term.
2. Find the first two non-zero terms in the Maclaurin series of $\sin(x^2)$.
3. The first four terms of the expansion of $(1-x)^{-4}$ are $1+ax+bx^2+20x^3$. Find $b$.
4. Given that $\frac{\mathrm{d}^n}{\mathrm{d}x^n}(x^2\mathrm{e}^x)=[x^2+2nx+n(n-1)]\mathrm{e}^x$, determine the Maclaurin series of $x^2\mathrm{e}^x$ up to $x^4$.
5. Hence, find the Maclaurin series for $\mathrm{e}^{\cos 2x-1}$ up to the term in $x^4$.
6. Hence, use integration to show that $\arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\dots$
7. Given that $\frac{\mathrm{d}^3y}{\mathrm{d}x^3}=9$ when $x=0$, find the first four terms of the Maclaurin series for $y$.
8. Hence, find an approximate value for $\int_0^1\mathrm{e}^{x^2}\sin(x^2)\,\mathrm{d}x$.
9. Determine how many non-zero terms would need to be used, such that the error is less than $0.0001$.
10. Find the Maclaurin series for $\cos 2x$, up to and including the term in $x^4$.
11. By differentiating both sides of $a+ar+ar^2+\dots=\frac{a}{1-r}$ with respect to $r$, find $\sum_{n=1}^{\infty}nar^{\,n-1}$.
12. It has been shown that $g''(x)=2(g'(x)-g(x))$. Using this, find the Maclaurin series for $g(x)=\mathrm{e}^x\cos x$ up to the $x^4$ term.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + r""")
""")

md(r"""
---
## On the timer

*May 2024 TZ2 Paper 1 Q12(b), (c) and (e) — 11 marks. Twelve minutes.*

Top of the notebook covered, paper and pen, no formula booklet except the
five standard series and the binomial series.

Let $f(x)=(1-ax)^{-\frac12}$, where $ax<1$, $a\ne0$.

**(a)** Show that the Maclaurin series for $f(x)$ up to and including the
$x^2$ term is $1+\frac12ax+\frac38a^2x^2$.

**(b)** Hence show that
$(1-2x)^{-\frac12}(1-4x)^{-\frac12}\approx\frac{2+6x+19x^2}{2}$.

**(c)** Use $x=\frac{1}{10}$ to determine an approximate value for
$\sqrt3$, in the form $\frac cd$ with $c,d\in\mathbb{Z}^+$.

Enter the series from (a) and the fraction from (c). Part (b) is on paper —
its answer is printed in the question, and the marks are in the route.

| date | time | notes |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_a = ...       # the series for (1 - a*x)**(-1/2) up to x^2, in terms of a
qt_b = ...       # the approximation for sqrt(3), as a fraction

verify_maclaurin('timer (a)', qt_a, (1 - a*x)**Rational(-1, 2), order=2,
                 params={a: (1, 2, -3)})
check_expr('timer (c)', qt_b, '""" + D_TA + r"""')
""")

# ================================================================= решения
md(r"""
---
# 🔑 Solutions

---
### Task 1 — the same substitution twice

**(a)** $\sin u=u-\frac{u^3}{3!}+\dots$ with $u=x^2$:
$$\sin(x^2)=x^2-\frac{(x^2)^3}{6}+\dots=x^2-\frac{x^6}{6}+\dots$$
**A1** for each term. The whole question is $(x^2)^3=x^6$.

**(b)** $\cos u=1-\frac{u^2}{2!}+\frac{u^4}{4!}-\dots$ with $u=2x$:
$$\cos 2x=1-\frac{4x^2}{2}+\frac{16x^4}{24}-\dots=1-2x^2+\frac{2x^4}{3}-\dots$$
Both the $4$ and the $16$ come out of the substitution, and both carry
marks. Three terms of the cosine series are needed to reach $x^4$ — two
would stop at $x^2$.

Notice the difference in depth between the two parts. In (a) two terms of
the sine series reach $x^6$; in (b) three terms of the cosine series are
needed to reach $x^4$. Same technique, opposite answer to «how far do I
expand», and it is settled by the substitution, not by the target.

---
### Task 2 — a negative index

**(i)** With $p=-4$, $u=-x$: the coefficient of $x$ is $p\cdot(-1)=4$,
so $a=4$. The markscheme is firm: *do not award the mark for $1+4x$ seen
without clear evidence of a substitution.* Writing down the answer to a
**show that** earns nothing.

**(ii)** $$\frac{p(p-1)}{2!}u^2=\frac{(-4)(-5)}{2}(-x)^2=10x^2,$$
so $b=10$, and the series is $1+4x+10x^2+20x^3+\dots$

The given $20x^3$ is a free check:
$\frac{(-4)(-5)(-6)}{6}(-x)^3=20x^3$ — three minus signs from the
coefficients and one from $(-x)^3$, all cancelling. That is why every
coefficient of $(1-x)^{-4}$ is positive.

The next part of the paper values a car depreciating $10\%$ a year: today
it is worth \$1000, so four years ago it was
$1000\times(0.9)^{-4}$, and the series at $x=0.1$ gives $\$1520$. The true
value is $\$1524$ — the series is three terms short, and the question
knows it.

---
### Task 3 — with the derivatives supplied

Put $x=0$ into the given formula:
$$f^{(n)}(0)=\bigl[0+0+n(n-1)\bigr]\mathrm{e}^0=n(n-1),$$
so $f''(0)=2$, $f'''(0)=6$, $f^{(4)}(0)=12$, and $f(0)=f'(0)=0$ (from $f$
itself — the formula only starts at $n=1$). Then
$$f(x)=\frac{2}{2!}x^2+\frac{6}{3!}x^3+\frac{12}{4!}x^4+\dots
 =x^2+x^3+\frac{x^4}{2}+\dots$$

Three marks, and all three are the division by $n!$.

*Otherwise*: multiply $x^2$ by the series for $\mathrm{e}^x$. One line, and
the markscheme allows it — but the question sits directly after an
induction proof of that formula, and *hence* is where the method marks are.

---
### Task 4 — a letter in the answer

**The short route.** $\cos x=1-\frac{x^2}{2}+\dots$, so
$$\cos^n x=\left(1-\frac{x^2}{2}+\dots\right)^n
 =1+n\left(-\frac{x^2}{2}\right)+\dots=1-\frac n2x^2+\dots$$
Every later binomial term carries $\left(\frac{x^2}{2}\right)^2=x^4$ or
higher, so up to $x^2$ two terms are all there is.

**The long route.** $f_n'(x)=-n\cos^{n-1}x\sin x$, which is $0$ at $x=0$;
$f_n''(x)=n(n-1)\cos^{n-2}x\sin^2x-n\cos^nx$, which is $-n$ at $x=0$; so
the $x^2$ coefficient is $-\frac n2$.

Both are marked the same. The first is rung 3 doing rung 1's work, and
that is the general lesson of Part I: the rung you climb is a choice, and
the cheap one is usually the one that recognises a known series.

In the paper the next part asks for
$\lim_{x\to0}\frac{f_n(x)-1}{x^2}$, which is now $-\frac n2$ by inspection.
That part belongs to E1, and it is the reason this one was set.

---
### Task 5 — a product of two standard series

$$\mathrm{e}^x=1+x+\frac{x^2}{2}+\frac{x^3}{6},\qquad \sin x=x-\frac{x^3}{6}$$
$$\mathrm{e}^x\sin x=x+x^2+\left(\frac12-\frac16\right)x^3+\dots
 =x+x^2+\frac{x^3}{3}+\dots$$

Collecting $x^3$: $1\cdot\left(-\frac{x^3}{6}\right)$ from the constant of
$\mathrm{e}^x$ times the cubic of $\sin x$, and $\frac{x^2}{2}\cdot x$ from
the quadratic times the linear. Two contributions, $-\frac16+\frac12
=\frac13$.

**M1** for recognising both series, **M1** for the attempt to multiply up
to $x^3$, **A1A1** for the intermediate expression and the answer.

*Otherwise*: $f'=\mathrm{e}^x(\cos x+\sin x)$, $f''=2\mathrm{e}^x\cos x$,
$f'''=2\mathrm{e}^x(\cos x-\sin x)$ give $0,1,2,2$ at zero. Same series,
four times the work, and one more chance to lose a sign.

---
### Task 6 — a square, then a shortcut

**(a)** Square the answer to Task 1(a):
$$\left(x^2-\frac{x^6}{6}\right)^2
 =x^4-2\cdot x^2\cdot\frac{x^6}{6}+\dots=x^4-\frac{x^8}{3}+\dots$$
The cross term is the mark. The markscheme awards **M0** for
$(x^2)^2-\left(\frac{x^6}{3!}\right)^2$ — squaring term by term — which
means none of the three marks, not a deduction.

*Otherwise*: $\sin^2\theta=\frac{1-\cos2\theta}{2}$ with $\theta=x^2$, then
the cosine series. No cross term to forget.

**(b)** Two ways, and one of them is why (a) and (b) are next to each
other.

*Hence*: $\frac{\mathrm{d}}{\mathrm{d}x}\sin^2(x^2)
=2\sin(x^2)\cdot\cos(x^2)\cdot 2x=4x\sin(x^2)\cos(x^2)$ — the expression in
the question is the derivative of the function in part (a). So
differentiate the answer to (a) term by term:
$$\frac{\mathrm{d}}{\mathrm{d}x}\left(x^4-\frac{x^8}{3}\right)
 =4x^3-\frac{8x^7}{3}.$$
Two marks, one line.

*Otherwise*: $4x\sin(x^2)\cos(x^2)=2x\sin(2x^2)$ by the double-angle
identity, and then the sine series with $u=2x^2$:
$2x\left(2x^2-\frac{8x^6}{6}\right)=4x^3-\frac{8x^7}{3}$.

Both are full marks. The first is rung 6 appearing two rungs early, and it
is worth noticing here because it is the technique the whole of Part III
is built on.

---
### Task 7 — three parts of one November question

**(a)** $u=\cos 2x-1=-2x^2+\frac{2x^4}{3}-\dots$, which vanishes at $x=0$,
so $\mathrm{e}^u=1+u+\frac{u^2}{2}+\dots$ is legitimate:
$$1+\left(-2x^2+\frac{2x^4}{3}\right)+\frac{(-2x^2)^2}{2}+\dots
 =1-2x^2+\frac{2x^4}{3}+2x^4+\dots=1-2x^2+\frac{8x^4}{3}+\dots$$
The $x^4$ coefficient collects $\frac23$ from $u$ and $2$ from
$\frac{u^2}{2}$. Inside $u^2$ only the leading term matters — the cross
term is $x^6$ — but outside it, both do.

**(b)** $\mathrm{e}^{\cos 2x}=\mathrm{e}\cdot\mathrm{e}^{\cos 2x-1}$, so
$$f(x)=\mathrm{e}\left(1-2x^2+\frac{8x^4}{3}\right)+\dots$$
*Write down* — one mark, no working expected, and all of it is not losing
the $\mathrm{e}$.

**Why the question is built in three parts.** $\mathrm{e}^{\cos 2x}$ cannot
be expanded by putting $\cos 2x$ into the series for $\mathrm{e}^u$: at
$x=0$ the exponent is $1$, and the series for $\mathrm{e}^u$ is about
$u=0$. Subtracting the $1$ and restoring the factor outside is the only
honest route, and part (ii) exists to force it.

The paper's last part uses the first two non-zero terms to show
$\int_0^{1/10}\mathrm{e}^{\cos 2x}\mathrm{d}x\approx\frac{149\mathrm{e}}{1500}$,
which is rung 8 — and it is worth doing on paper to see how quickly this
series pays for itself.

---
### Task 8 — the coefficient is the equation

$$f(x)=\sqrt{1+x}=1+\frac x2-\frac{x^2}{8}+\dots,\qquad
 g(x)=\mathrm{e}^{mx}=1+mx+\frac{m^2x^2}{2}+\dots$$
Collecting $x^2$ in the product — three contributions:
$$1\cdot\frac{m^2}{2}\;+\;\frac12\cdot m\;+\;\left(-\frac18\right)\cdot1
 =\frac{m^2}{2}+\frac m2-\frac18 .$$
Set that equal to $\frac74$:
$$\frac{m^2}{2}+\frac m2-\frac18=\frac74
 \;\Longrightarrow\;4m^2+4m-15=0
 \;\Longrightarrow\;(2m+5)(2m-3)=0,$$
so $m=\frac32$ or $m=-\frac52$.

Eight marks: two for the two expansions, one for collecting the
coefficient, one for the equation, two for solving, two for the pair of
answers. Only three of the eight are the series work.

The markscheme's third method goes through
$h''(0)=f(0)g''(0)+2f'(0)g'(0)+f''(0)g(0)=m^2+m-\frac14$ and sets it to
$\frac72$ — the same quadratic, doubled, because $h''(0)=2!\times$ (the
$x^2$ coefficient). Mixing the two conventions is the standard way to lose
this question: $\frac74$ belongs to the coefficient, $\frac72$ to the
second derivative.

Both roots are wanted. «The possible values» is plural, and stopping at
$\frac32$ is one mark short.

---
### Task 9 — both directions

**(a)** Differentiate the sum term by term:
$$\frac{\mathrm{d}}{\mathrm{d}r}\left(a+ar+ar^2+\dots\right)
 =a+2ar+3ar^2+\dots=\sum_{n=1}^{\infty}n\,a\,r^{\,n-1},$$
and the closed form:
$$\frac{\mathrm{d}}{\mathrm{d}r}\left(\frac{a}{1-r}\right)
 =\frac{a}{(1-r)^2}.$$
So the sum is $\frac{a}{(1-r)^2}$.

$a$ is the first term, a constant, and rides along untouched. The square
comes from the power rule, the plus sign from the chain rule cancelling it
against the $-1$ in $(1-r)$.

In the paper this gives $\mathrm{E}(X)=\frac1p$ for the number of attempts
until a first success, with $a=p$ and $r=1-p$ — a geometric distribution's
mean, derived rather than quoted.

**(b)(i)** $f_n$ is geometric with ratio $-2x^2$; the limit exists exactly
when $|-2x^2|<1$, that is $|x|<\frac{1}{\sqrt2}$. So
$K=\frac{1}{\sqrt2}=\frac{\sqrt2}{2}$. *Exact form* is a requirement on the
writing — $0.707$ earns nothing.

**(b)(ii)** Inside that interval,
$$f(x)=\frac{1}{1-(-2x^2)}=\frac{1}{1+2x^2},$$
so $a=1$, $b=2$.

This is (a) read backwards. Everywhere else a geometric series builds a
Maclaurin series; here a Maclaurin series is recognised as geometric and
folded back into the function it came from. One identity,
$\frac{1}{1-u}=1+u+u^2+\dots$, and the topic uses it in both directions.

---
### Task 10 — a series out of an equation

**(a)** At $x=0$, $y=3$, so the equation itself gives
$$\left.\frac{\mathrm{d}y}{\mathrm{d}x}\right|_0=\frac{0-3}{0+1}=-3 .$$
With $y''(0)=3$ and $y'''(0)=9$ given,
$$y=3-3x+\frac{3}{2!}x^2+\frac{9}{3!}x^3+\dots
 =3-3x+\frac32x^2+\frac32x^3+\dots$$
Both $\frac32$'s are factorial divisions, and both are marks:
$\frac{3}{2!}=\frac32$, $\frac{9}{3!}=\frac32$. Writing $3x^2+9x^3$ is the
standard loss.

For the record, the second derivative that was given comes from
differentiating the equation implicitly:
$$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}
 =\frac{(2xy+x^2y'-y')(x^2+1)-(x^2y-y)(2x)}{(x^2+1)^2},$$
which at $x=0$, $y=3$, $y'=-3$ is $\frac{(0+0+3)(1)-0}{1}=3$. The $y'$
inside the numerator is the chain rule doing its work — leave it out and
the answer is $0$.

**(b)** $$y(0.15)\approx3-0.45+\frac32(0.0225)+\frac32(0.003375)
 =2.588\,8125,$$ so $2.58881$ to six significant figures.

Six figures is the point. The same $y(0.15)$ is computed three times in
that paper — by Euler's method with step $0.03$, by this series, and from
the exact solution $y=3\mathrm{e}^{x-2\arctan x}$ in part (d) — and the
three answers first differ in the fourth figure. Rounding early destroys
the comparison the question was built for.

---
### Task 11 — an integral and a limit

**(a)** Put $x^2$ where $x$ was in the series from Task 5:
$$\mathrm{e}^{x^2}\sin\!\left(x^2\right)=x^2+x^4+\frac{x^6}{3}+\dots$$
Integrate term by term:
$$\int_0^1\left(x^2+x^4+\frac{x^6}{3}\right)\mathrm{d}x
 =\left[\frac{x^3}{3}+\frac{x^5}{5}+\frac{x^7}{21}\right]_0^1
 =\frac13+\frac15+\frac1{21}=\frac{61}{105}.$$

$\mathrm{e}^{x^2}\sin(x^2)$ has no antiderivative in closed form; the word
*approximate* in the question is the acknowledgement. The markscheme note:
*condone absence of limits up to this stage* — the limits of integration
only have to appear when you evaluate.

**(b)** With $u=\frac{\pi}{n}\to0$,
$$4n\tan\frac{\pi}{n}=4n\left(\frac{\pi}{n}+\frac{\pi^3}{3n^3}+\dots\right)
 =4\pi+\frac{4\pi^3}{3n^2}+\dots\;\longrightarrow\;4\pi .$$
Every term after the first carries $\frac{1}{n^2}$ or smaller.

In the paper, $4n\tan\frac{\pi}{n}$ is the common value of area and
perimeter for a regular $n$-gon with $A=P$, and the next part asks what
$4\pi$ means: it is the circle, whose area and circumference both equal
$4\pi$ at radius $2$.

---
### Task 12 — the November 2025 investigation

**(a)** $\arctan\frac1{\sqrt3}=\frac\pi6$, so $\pi=6\arctan\frac1{\sqrt3}$.
Three terms:
$$\frac{1}{\sqrt3}-\frac13\left(\frac{1}{\sqrt3}\right)^3
 +\frac15\left(\frac{1}{\sqrt3}\right)^5=0.526\,030\dots$$
and $\pi\approx6\times0.526030=3.156$.

Recognising $\arctan\frac1{\sqrt3}=\frac\pi6$ is the first mark and the
whole idea: the series computes a number that happens to be a known
fraction of $\pi$.

**(b)** Term $m$ has magnitude
$\frac{1}{2m-1}\left(\frac{1}{\sqrt3}\right)^{2m-1}$:
$$m=4:\ 0.003054,\quad m=5:\ 0.000792,\quad
 m=6:\ 0.000216,\quad m=7:\ 0.000061 .$$
The first one below $0.0001$ is $m=7$, so the last term kept is number $6$:
**six non-zero terms**.

Solving $\frac{1}{2m-1}\left(\frac1{\sqrt3}\right)^{2m-1}<0.0001$ on the
GDC gives $m=6.61$, hence $m=7$ for the first term dropped, hence $6$
kept. The calculator gives you the index of the first term small enough to
throw away; the answer is one less. That single step is what the question
is marking.

**(c)** The bound: the four terms kept are $x$, $-\frac{x^3}{3}$,
$\frac{x^5}{5}$, $-\frac{x^7}{7}$, so the first one dropped is
$\frac{x^9}{9}$, and
$$\int_0^{1/\sqrt3}\frac{x^9}{9}\,\mathrm{d}x
 =\left[\frac{x^{10}}{90}\right]_0^{1/\sqrt3}
 =\frac{1}{90\cdot3^5}=\frac{1}{21870}=4.57\times10^{-5}.$$

The actual error: the exact value is
$\frac{\pi}{6\sqrt3}-\frac12\ln\frac43=0.158\,458\,558\dots$, and
$$0.158458558\dots-0.158422=3.69\times10^{-5}.$$

$3.69\times10^{-5}<4.57\times10^{-5}$, so the theorem holds. The **R1** is
that inequality written down; producing both numbers and stopping loses it.

Two significant figures is asked for deliberately. Using the unrounded
value from the previous part instead of $0.158422$ gives
$3.73\times10^{-5}$, and the markscheme accepts both — they agree to two
figures and part company in the third.

---
### On the timer

**(a)** From the proved $n$th derivative, at $x=0$,
$f^{(n)}(0)=\frac{a^n(2n-1)!}{2^{2n-1}(n-1)!}$, so $f'(0)=\frac a2$ and
$f''(0)=\frac{6a^2}{8}=\frac{3a^2}{4}$, giving
$$f(x)=1+\frac a2x+\frac{3a^2}{4}\cdot\frac{x^2}{2!}
 =1+\frac12ax+\frac38a^2x^2 .$$

*Otherwise, and faster*: the binomial series with $p=-\frac12$, $u=-ax$:
$$1+\left(-\tfrac12\right)(-ax)
 +\frac{\left(-\frac12\right)\left(-\frac32\right)}{2}(-ax)^2
 =1+\frac12ax+\frac38a^2x^2 .$$

**(b)** Take $a=2$ and $a=4$:
$$(1-2x)^{-\frac12}\approx1+x+\frac32x^2,\qquad
 (1-4x)^{-\frac12}\approx1+2x+6x^2,$$
and multiplying up to $x^2$,
$$1+3x+\left(6+2+\tfrac32\right)x^2=1+3x+\frac{19}{2}x^2
 =\frac{2+6x+19x^2}{2}.$$
The middle coefficient is three contributions: $6$, the cross term $2$, and
$\frac32$. Dropping the cross term gives $\frac{15}{2}$, and it is the
commonest error in the question.

**(c)** At $x=\frac1{10}$ the approximation is
$\frac{2+0.6+0.19}{2}=\frac{279}{200}$, and the exact left-hand side is
$$\left(\tfrac45\right)^{-\frac12}\left(\tfrac35\right)^{-\frac12}
 =\frac{1}{\sqrt{0.48}}=\frac{10}{\sqrt{48}}=\frac{10}{4\sqrt3},$$
so
$$\frac{10}{4\sqrt3}\approx\frac{279}{200}
 \;\Longrightarrow\;\frac{1}{\sqrt3}\approx\frac{279}{500}
 \;\Longrightarrow\;\sqrt3\approx\frac{500}{279}.$$

**This last step deserves a minute of its own.** Rearranging first and
solving afterwards gives a different answer. Writing $\frac{10}{4\sqrt3}$
as $\frac{5\sqrt3}{6}$ and then solving gives
$$\sqrt3\approx\frac65\cdot\frac{279}{200}=\frac{837}{500}=1.674 ,$$
against $\frac{500}{279}=1.7921$ from the route above. The true value is
$1.7321$: one answer is $3.5\%$ high, the other $3.4\%$ low. They straddle
it, and neither is the better number — they are one error pointing two
ways.

Here is why. The approximation $\frac{279}{200}$ undershoots the exact
$\frac{10}{4\sqrt3}$ by a factor of $0.9665$. Isolate $\sqrt3$ from the
denominator and it picks up $\frac{1}{0.9665}$; move it to the numerator
first and it picks up $0.9665$ instead. An equation survives being
multiplied through by $\sqrt3$. An **approximate** equation carries its
error across with it, and which side the error lands on depends on the
order of your algebra.

Only one of the two is the markscheme's, and the rule that produces it is
short: leave $\sqrt3$ where the exact side puts it, and isolate it on the
last line.

The approximation is crude to start with — $1.395$ against a true
$1.4434$ — because $x=\frac1{10}$ is not small next to the radius
$\frac14$, and only three terms were kept. The next part of the paper asks
for that restriction on $x$, and it is $|x|<\frac14$: the tighter of the
two brackets' conditions.

---
### Key to the recognition drill

1 `mult` — a product of two known series.
2 `sub` — the sine series with $x^2$ inside.
3 `binom` — a bracket to the power $-4$.
4 `def` — the $n$th derivative is handed over; $f^{(n)}(0)/n!$.
5 `comp` — $\cos 2x-1$ is a series, and it goes inside $\mathrm{e}^u$.
6 `termwise` — «use integration», and the integrand is geometric.
7 `ode` — the function is given by an equation and a starting value.
8 `approx` — «hence», and an integral with no antiderivative.
9 `error` — the word «error» and a bound.
10 `sub` — the cosine series with $2x$ inside.
11 `termwise` — «by differentiating both sides».
12 `def` — a relation between derivatives, evaluated at $0$.

Two of these are worth arguing about, and the argument is the point.

**4 and 12 are both `def`** even though neither differentiates anything:
the derivatives arrive from the part before, one as a formula and one as a
relation. What makes them the same technique is what you do next —
substitute $x=0$ and divide by $n!$.

**3 could be `def`** — you can differentiate $(1-x)^{-4}$ four times and it
works. It is `binom` because the binomial series is written down in one
line and the differentiation takes four, and choosing the cheap route is
the skill being drilled.

---
### Where the marks went, across the topic

| technique | marks | share |
| --- | --- | --- |
| Multiply two series | 21 | 21% |
| The series in place of the function | 20 | 20% |
| How wrong it is | 13 | 13% |
| From the definition | 13 | 13% |
| Differentiate or integrate | 12 | 12% |
| A series inside a series | 4 + part of 6 | ~8% |
| The binomial series | 5 | 5% |
| A series out of a differential equation | 3 | 3% |
| Substitute into a known series | 2 + part of 6 | ~5% |

Two things stand out.

**Building the series is worth less than using it.** Rungs 1–5 together
carry $45$ marks and rungs 6–9 carry $54$. The expansion is the part
everyone practises and the part that is worth fewer marks; the arithmetic
afterwards — an integral, a value of $\pi$, an error bound — is worth more
and gets practised less.

**The topic concentrates.** $56$ of the $99$ marks are the last question of
a Paper 1, and $21$ more are one November 2025 Paper 3 investigation. Two
questions, three quarters of the topic. When Maclaurin series appear on a
paper, they appear as a twenty-mark question and not as a five-mark one —
which is worth knowing when you decide what to revise and in what order.
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
