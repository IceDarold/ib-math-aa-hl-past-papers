"""Собирает практикум E3: техника дифференцирования.

Седьмой практикум серии на английском. Лестница из девяти приёмов делится
по тому, что спрашивают: приёмы 1–5 выбирают правило по форме записи,
6–8 доводят результат до нужного вида и повторяют, 9 читает готовую
производную.

Проверок здесь три новых, и все живут в kit вместе с практикумом.

`verify_derivative` эталона не хранит: производная у функции одна, и
проверка получает её из условия. Интереснее то, что она делает с неверным
ответом. Промахи в этой теме именные — потерянный множитель цепного
правила, произведение как u′v′, перевёрнутый знак в частном, непонижённый
показатель, — и проверка строит каждый из них из той же самой функции.
Списка неверных ответов при этом тоже нет: они выводятся, а не хранятся.

`verify_stationary` — для приёма 9. Точка нулевого наклона это пара чисел,
и половина потерянных баллов темы там, где найдена только первая. Проверка
требует обе координаты и сканирует производную по отрезку из условия,
чтобы поймать вторую потерю — найдены не все точки.

`verify_constants` — для вопросов, где буквы стоят внутри функции и
подставлять ответ некуда. Подставляется он в условия самого вопроса:
асимптота там-то, кривая проходит через такую-то точку, производная в ней
равна нулю. Проверка называет то условие, которое не выполнилось.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e3.py прогоняет по нему весь ноутбук и требует,
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

R = sp.Rational
x = sp.Symbol('x')
a, b, n = sp.symbols('a b n')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e3-differentiation.ipynb')

TRIGGER = {1: 'quotient', 2: 'chain', 3: 'product', 4: 'read', 5: 'higher',
           6: 'table', 7: 'power', 8: 'form', 9: 'letter', 10: 'read',
           11: 'chain', 12: 'quotient'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '-2*(x - h)',
    'q1b': 'Rational(1, 16) + Rational(3, 8)*t + Rational(15, 16)*t**2 + Rational(7, 4)*t**3',
    'q2': '500*sec(theta)*tan(theta) - 1000*sec(theta)**2/3',
    'q3a': '-2*E**2',
    'q3b': '2/(2 - x)**3',
    'q4': 'n*x**(n - 1)*(a - 2*x)*(a - x)**(n - 1)',
    'q5a': '(-12*x**2 - 16*x - 3)/(4*x**2 - 1)**2',
    'q5b': '2*(x - a + 15)*(2*x + a)**2/(x + 5)**3',
    'q6a': '4*x/(2 - x)**3',
    'q6b': '4*x/(2 - x)**3',
    'q7': '-2*exp(x)*sin(x)',
    'q8a': '3*sec(alpha)*tan(alpha)/4 - 6*cosec(alpha)*cot(alpha)',
    'q8b': ('3*(sec(alpha)*tan(alpha)**2 + sec(alpha)**3)/4'
            ' + 6*(cosec(alpha)*cot(alpha)**2 + cosec(alpha)**3)'),
    'q8c': '45*sqrt(5)/4',
    'q9a': '-b/(2*a)',
    'q9b': '2*Abs(a)',
    'q10a': '-4*sin(2*x)',
    'q10b': '[(0, 1), (pi/2, -3), (pi, 1)]',
    'q11a': 'Union(Interval.open(-oo, -1.74), Interval.open(0.518, oo))',
    'q11b': 'Interval.open(-oo, log(Rational(2, 3)))',
    'q12': '[3, -11, 8]',
    'qt_a': '(x + 3)*sqrt(9 - x**2)',
    'qt_b': '(9 - 3*x - 2*x**2)/sqrt(9 - x**2)',
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
# Practicum E3: differentiating

**188 marks, 55 blocks, nine techniques.** Every question in this topic is
the same trade in reverse of E2: you are handed a function and you give back
another function. Which rule you reach for is settled by the *shape* of what
you were handed, and that decision takes two seconds and costs the whole
question if you get it wrong.

**Material.** The part of `calculus.differentiation` in the AA HL archive
where the answer is the derivative itself, sessions May 2021 — November 2025.
The whole topic is 350 marks — twice what a practicum may hold — so it is cut
in three by what the question asks for: *find $f'(x)$* here, *find the
tangent* in E4, *find the acceleration* in E9.

**This practicum is in English,** like B2 to B5, E1 and E2. The checks speak
whichever language the notebook asks them to, and this one asks for English
in the setup cell.

**The one thing to carry out of here.**

> Reach for the rule by looking at the **written shape**, not at what the
> function is called. A bracket with something inside it that is not $x$ —
> chain. Two things multiplied, both moving — product. Something on top and
> something on the bottom, both moving — quotient. Everything else is the
> power rule and the table.

And the thing that follows from it: **most of the marks in this topic are not
the differentiation.** Sections 1–5 of the archive carry 71 marks between
them; sections 6–9 carry 117. What the archive pays for is the algebra that
gets you from your line to the printed one, and the reading of a derivative
you already have.

**Where the calculator sits.** 73% of the marks formally carry one, and about
15 of the 188 actually need one. This is the sixth topic in a row where that
number is an illusion, and the widest gap of the six. Paper 3 in particular
looks like calculator territory and is nothing of the sort: $\frac{45\sqrt5}{4}$,
$-\frac{r^{2}}{y^{3}}$, $\frac{2\sqrt3}{9}$, $2|a|$.

**How the checks work here.** Three of them are new.

`verify_derivative(label, got, f)` differentiates the function from the
question and compares — as functions, not as strings, so any equivalent
arrangement passes. When your answer is wrong it does more than say so. It
rebuilds the standard slips out of that same function — the chain factor
dropped, the product done as $u'v'$, the quotient numerator the wrong way
round, the power not lowered — and if what you wrote matches one of them, it
tells you which one. Neither the right answer nor the wrong ones are stored
anywhere: both are worked out from $f$.

`verify_stationary(label, got, f, domain)` takes a list of points, checks
that the derivative really is zero at each one **and** that the second
coordinate is the value of $f$ there, then scans the interval for points you
missed.

`verify_constants(label, got, unknowns, conditions)` is for the questions
where letters sit inside the function. There is nowhere to substitute the
answer, so it substitutes into the *conditions the question states* — the
asymptote, the point on the curve, the zero gradient — and names the one that
fails.
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
print('with a letter in it: ', n*x**(n - 1))
print('an exact value:      ', 45*sqrt(5)/4)
print('a pair of points:    ', [(0, 1), (pi/2, -3)])
""")

md(r"""
---
## Map of techniques

| # | Technique | What the function looks like | First move |
| --- | --- | --- | --- |
| 1 | Power rule, term by term | a sum of powers of $x$ | drop each power by one |
| 2 | The table | $\sec$, $\csc$, $\cot$, $\ln$, $\mathrm{e}^{x}$ | look it up, keep the minus |
| 3 | Chain rule | something inside a bracket | outside first, then times the inside |
| 4 | Product rule | two moving factors multiplied | write $u'v+uv'$ before computing |
| 5 | Quotient rule | moving top over moving bottom | $\dfrac{u'v-uv'}{v^{2}}$, in that order |
| 6 | To the printed line | *show that* $f'(x)=\dots$ | common denominator, then factor |
| 7 | Second and higher | $f''$, $\mathrm{d}^{2}y/\mathrm{d}x^{2}$ | tidy the first one *for* the second |
| 8 | A letter in it | $a$, $k$, $m$, $n$, $r$ in the answer | treat it as a number, keep the modulus |
| 9 | Read the derivative | *where is the gradient zero* | solve $f'=0$, then substitute back |

**The ladder goes by what the question asks for.**

**Rungs 1–5 — you are choosing the rule.** Seventy-one of the 188 marks, and
the choice is made by looking, not by computing. It is the part everyone
drills, and it is worth the least.

**Rungs 6–8 — you are finishing.** The algebra to the printed line, the second
derivative, the letter that will not go away. Fifty-one marks, and the
differentiation in them is usually the easy half.

**Rungs 9 — you are reading.** Fifty-one marks on its own, all of it after the
derivative already exists. Solve $f'=0$; put the roots back into $f$; look at
signs. The lost marks here are not calculus at all — a coordinate given as one
number, an interval read short, *decreasing* solved as an equation.

**The table you must know cold.** It is in the formula booklet, and looking it
up costs the seconds in which you were meant to recognise the shape.

$$\frac{\mathrm{d}}{\mathrm{d}x}\sec x=\sec x\tan x\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\csc x=-\csc x\cot x\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\cot x=-\csc^{2}x$$
$$\frac{\mathrm{d}}{\mathrm{d}x}\tan x=\sec^{2}x\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\ln x=\frac1x\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\arctan x=\frac{1}{1+x^{2}}$$
""")

# ================================================================== Part I
md(r"""
---
# Part I — choosing the rule

## Theory 1. The shape decides, and you decide before you write

Four rules cover everything in this topic, and which one applies is a
property of how the function is **written**, not of what it is.

$$\underbrace{x^{4}-3x^{3}+3x}_{\text{a sum: term by term}}\qquad
\underbrace{\mathrm{e}^{x^{2}+1}}_{\text{something inside: chain}}\qquad
\underbrace{\mathrm{e}^{2x}(3x-4)}_{\text{two moving factors: product}}\qquad
\underbrace{\frac{3x+2}{4x^{2}-1}}_{\text{moving over moving: quotient}}$$

Three things are worth saying before any of the rules.

**A constant is a constant even when it is a letter.** In $x^{3}-3cx+2$ the
$c$ is a parameter: $-3cx$ differentiates to $-3c$, and the $2$ disappears.
People who differentiate $c$ lose the question, not the mark.

**A bottom without $x$ in it is not a quotient.** $\frac{2500-1000\tan\theta}{3}$
is $\frac13$ times something — the quotient rule on it is legal and three
times the work.

**Expand first when expanding is cheap.** $x(2-x)$ is a product, but writing
$2x-x^{2}$ takes one second and removes the rule entirely. $x^{n}(a-x)^{n}$
is also a product and expanding it is out of the question — the difference is
whether the expansion is finite and short.
""")

md(r"""
## Task 1 🟢 — term by term, twice

*May 2021 TZ1 Paper 1 Q4(a), 1 mark · May 2025 TZ1 Paper 3 Q1(c)(i), 2 marks*

**(a)** Consider $f(x)=-(x-h)^{2}+2k$, where $h,k\in\mathbb{R}$. Find
$f'(x)$.

**(b)** Find $G'(t)$ for
$$G(t)=\frac{1}{16}t+\frac{3}{16}t^{2}+\frac{5}{16}t^{3}+\frac{7}{16}t^{4}.$$
""")

code(r"""
q1a = ...        # f'(x)
q1b = ...        # G'(t)

verify_derivative('1a', q1a, -(x - h)**2 + 2*k)
verify_derivative('1b', q1b, t/16 + 3*t**2/16 + 5*t**3/16 + 7*t**4/16, var=t)
""")

md(r"""
## Theory 2. The table, and the two minus signs in it

$$\frac{\mathrm{d}}{\mathrm{d}\theta}\sec\theta=\sec\theta\tan\theta\qquad
\frac{\mathrm{d}}{\mathrm{d}\theta}\csc\theta=-\csc\theta\cot\theta\qquad
\frac{\mathrm{d}}{\mathrm{d}\theta}\cot\theta=-\csc^{2}\theta$$

$\sec$ is the odd one out: it is the only one of the three without a minus.
$\csc$ and $\cot$ both carry one, and in this archive the missing minus on
$\csc$ is the single most common lost mark of the whole section — because it
is the minus that lets $\frac{\mathrm{d}L}{\mathrm{d}\alpha}=0$ have a
solution at all. If your equation has no solution, look there first.

A second habit worth having: **check the sign against the picture.** A cost
that must have a minimum has a derivative that changes sign; a population
model that is decreasing has $f'<0$ everywhere. Thirty seconds of that catches
more errors than re-differentiating does.
""")

md(r"""
## Task 2 🟢 — sec and tan in one line

*November 2025 TZ3 Paper 1 Q8(b), 3 marks*

Astrid walks across a beach at $0.8\ \mathrm{m\,s^{-1}}$ and then jogs along
the promenade at $1.2\ \mathrm{m\,s^{-1}}$; the time she takes, in seconds, is

$$T=500\sec\theta+\frac{2500-1000\tan\theta}{3},\qquad
0<\tan\theta\le\frac{5}{2}.$$

Find $\dfrac{\mathrm{d}T}{\mathrm{d}\theta}$.
""")

code(r"""
q2 = ...

verify_derivative('2', q2, 500*sec(theta) + (2500 - 1000*tan(theta))/3,
                  var=theta)
""")

md(r"""
## Theory 3. The chain rule, and the factor that goes missing

$$\frac{\mathrm{d}}{\mathrm{d}x}F\bigl(u(x)\bigr)=F'\bigl(u(x)\bigr)\cdot u'(x)$$

The reliable tell is not the shape of the formula but what evaluating it
would make you do: if computing $f(2)$ forces you to work out something
*inside* first, that inside comes back out as a multiplier.

$$\mathrm{e}^{x^{2}+1}\ \to\ 2x\,\mathrm{e}^{x^{2}+1}\qquad
\sqrt{r^{2}-x^{2}}\ \to\ \frac{-x}{\sqrt{r^{2}-x^{2}}}\qquad
\ln(\cot x)\ \to\ \frac{-\csc^{2}x}{\cot x}$$

**The whole inside gets differentiated, constants included.** For
$\sqrt{r^{2}-k^{2}x^{2}}$ the inside derivative is $-2k^{2}x$, and the $k^{2}$
stays. It is not being differentiated; it is coming along.

**Rewriting first is usually cheaper than the quotient rule.**
$\frac{1}{(2-x)^{2}}$ is $(2-x)^{-2}$, and one chain rule beats one quotient
rule every time. Watch the two minus signs though: $-2(2-x)^{-3}\cdot(-1)$
comes out **positive**.

**A chain of three is still one rule, applied three times.**
$\sin(\sin(\sin x))$ differentiates to
$\cos(\sin(\sin x))\cos(\sin x)\cos x$: one cosine per layer, and the layers
peel from the outside in.
""")

md(r"""
## Task 3 🟢 — inside, then out

*November 2022 Paper 1 Q1, 4 marks · May 2024 TZ2 Paper 3 Q1(a)(i), 2 marks*

**(a)** The function $g$ is defined by $g(x)=\mathrm{e}^{x^{2}+1}$, where
$x\in\mathbb{R}$. Find $g'(-1)$.

**(b)** Find an expression for $f'(x)$, where
$f(x)=\dfrac{1}{(2-x)^{2}}$, $x\ne2$.
""")

code(r"""
G = exp(x**2 + 1)
q3a = ...        # g'(-1), exact
q3b = ...        # f'(x)

verify_exact('3a', q3a, diff(G, x).subs(x, -1))
verify_derivative('3b', q3b, 1/(2 - x)**2)
""")

md(r"""
## Theory 4. Product and quotient, and the two ways to lose them

$$(uv)'=u'v+uv'\qquad\qquad
\left(\frac{u}{v}\right)'=\frac{u'v-uv'}{v^{2}}$$

**The product has two terms, and the method mark is for having two.** Writing
$u'v'$ is not a slip in the arithmetic, it is a different (wrong) rule, and
mark schemes give it nothing.

**The quotient numerator does not commute.** $\frac{uv'-u'v}{v^{2}}$ is
exactly minus the right answer, which is worse than a random error: it looks
plausible, it has the right size, and it takes the rest of the question with
it.

**Factorise before you go on.** Almost every product-rule answer in this
archive is wanted in a factorised form, because the *next* part of the
question sets it to zero:

$$nx^{n-1}(a-x)^{n}+x^{n}\cdot n(a-x)^{n-1}(-1)
=nx^{n-1}(a-x)^{n-1}\bigl[(a-x)-x\bigr]=nx^{n-1}(a-2x)(a-x)^{n-1}.$$

The bracket is $(a-x)-x$ and not $(a-x)+x$ because of the $-1$ from the chain
rule inside the product rule. That $-1$ is three of the five marks.
""")

md(r"""
## Task 4 🟡 — a product with a letter in the exponent

*May 2021 TZ2 Paper 3 Q1(c), 5 marks*

Consider $f_{n}(x)=x^{n}(a-x)^{n}$, where $a\in\mathbb{R}^{+}$ and
$n\in\mathbb{Z}^{+}$, $n>1$.

Show that $f_{n}'(x)=n\,x^{n-1}(a-2x)(a-x)^{n-1}$.
""")

code(r"""
q4 = ...

verify_derivative('4', q4, x**n*(a - x)**n, params={n: (2, 3, 5)})
""")

md(r"""
## Task 5 🟡 — two quotients, one with a letter

*May 2021 TZ1 Paper 2 Q11(b), 3 marks · May 2025 TZ3 Paper 2 Q5(a), 3 marks*

**(a)** Find an expression for $f'(x)$, where
$f(x)=\dfrac{3x+2}{4x^{2}-1}$.

**(b)** Find an expression for $f'(x)$ in terms of $a$, where
$f(x)=\dfrac{(2x+a)^{3}}{(x+5)^{2}}$, $x\ne-5$, $a\in\mathbb{R}^{+}$.
""")

code(r"""
q5a = ...        # for (3x + 2)/(4x^2 - 1)
q5b = ...        # for (2x + a)^3/(x + 5)^2, in terms of a

verify_derivative('5a', q5a, (3*x + 2)/(4*x**2 - 1))
verify_derivative('5b', q5b, (2*x + a)**3/(x + 5)**2, params={a: (1, 3, 7)})
""")

# ================================================================= Part II
md(r"""
---
# Part II — finishing

## Theory 5. The printed line is the question

Half the marks in this topic sit after the differentiation is done. A
*show that* question hands you the destination, and what it is testing is the
route: a common denominator, a factor taken out, a sign moved.

Two rules from the mark schemes, both worth money.

**Work in one direction.** Starting from your expression and from the printed
one and meeting in the middle is not accepted. Start at yours and arrive.

**Arrive all the way.** $\frac{2x}{(2-x)^{2}}+\frac{2x^{2}}{(2-x)^{3}}$ is
correct and is not the answer. The common denominator is $(2-x)^{3}$ — not
$(2-x)^{5}$, because the first denominator divides the second — and then

$$\frac{2x(2-x)+2x^{2}}{(2-x)^{3}}=\frac{4x-2x^{2}+2x^{2}}{(2-x)^{3}}
=\frac{4x}{(2-x)^{3}} .$$

The $-2x^{2}$ and the $+2x^{2}$ cancelling is the entire point of that
question, and it is four marks.
""")

md(r"""
## Task 6 🟡 — the same destination, twice

*May 2024 TZ2 Paper 3 Q1(a)(ii) and (iii), 2 + 4 marks*

Let $f(x)=\dfrac{1}{(2-x)^{2}}$ and $g(x)=x^{2}$.

**(a)** Show that $f'(x)\,g'(x)=\dfrac{4x}{(2-x)^{3}}$.

**(b)** Show that $f(x)\,g'(x)+g(x)\,f'(x)=\dfrac{4x}{(2-x)^{3}}$.

*Same answer, twice the marks for (b). The difference is one common
denominator — and the coincidence that makes it work is what the rest of that
Paper 3 is about.*
""")

code(r"""
F, G = 1/(2 - x)**2, x**2
q6a = ...        # f'(x) g'(x)
q6b = ...        # f(x) g'(x) + g(x) f'(x)

verify_identity('6a', q6a, diff(F, x)*diff(G, x))
verify_identity('6b', q6b, F*diff(G, x) + G*diff(F, x))
""")

md(r"""
## Theory 6. The second derivative, and the form you leave the first in

Differentiate, then differentiate that. Two things make it harder than it
sounds.

**The form of $f'$ decides how long $f''$ takes.** For $f(x)=\sqrt{1+x}$,
leaving $f'(x)=\frac12(1+x)^{-1/2}$ gives $f''$ in one line. Leaving it as
$\frac{1}{2\sqrt{1+x}}$ invites the quotient rule and three times the work,
for the same answer.

**An identity between derivatives can be differentiated as it stands.** Once
you have shown $g''=2(g'-g)$, you get $g'''=2(g''-g')$ and
$g^{(4)}=2(g'''-g'')$ for nothing — no further differentiation of $g$ at all.
That is what *hence deduce* means, and it is two of the five marks.

**Substitute back what you know about the curve.** For $y=\sqrt{r^{2}-x^{2}}$,
$$\frac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}=-\frac{y^{2}+x^{2}}{y^{3}}
=-\frac{r^{2}}{y^{3}},$$
because $x^{2}+y^{2}=r^{2}$. The tidy form is not cosmetic — the next part
divides by it.
""")

md(r"""
## Task 7 🟡 — a relation between derivatives

*May 2022 TZ1 Paper 1 Q12(c), 5 marks*

The function $g$ is defined by $g(x)=\mathrm{e}^{x}\cos x$, where
$x\in\mathbb{R}$.

**(i)** Show that $g''(x)=2\bigl(g'(x)-g(x)\bigr)$.

**(ii)** Hence, deduce that $g^{(4)}(x)=2\bigl(g'''(x)-g''(x)\bigr)$.

*Enter $g''(x)$. Part (ii) needs no differentiation of $g$ at all — see the
solution.*
""")

code(r"""
q7 = ...

verify_derivative('7', q7, exp(x)*cos(x), order=2)
""")

md(r"""
## Task 8 🔴 — a pole round a corner, all the way to a number

*May 2023 TZ1 Paper 1 Q11(b)(i) and (c), 5 + 7 marks*

A pole of length $L$ is carried round a corner between a passageway of width
$\frac34$ m and a room of width $6$ m, at an angle $\alpha$ to the wall,
$0<\alpha<\frac{\pi}{2}$:

$$L=\frac{3}{4}\sec\alpha+6\csc\alpha .$$

**(a)** Find $\dfrac{\mathrm{d}L}{\mathrm{d}\alpha}$.

**(b)** Find $\dfrac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}$.

**(c)** When $\alpha=\arctan 2$, show that
$\dfrac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}=\dfrac{45\sqrt5}{4}$.
""")

code(r"""
L = 3*sec(alpha)/4 + 6*cosec(alpha)
q8a = ...        # dL/d(alpha)
q8b = ...        # d^2L/d(alpha)^2
q8c = ...        # its exact value at alpha = arctan 2

verify_derivative('8a', q8a, L, var=alpha)
verify_derivative('8b', q8b, L, var=alpha, order=2)
verify_exact('8c', q8c, simplify(diff(L, alpha, 2).subs(alpha, arctan(2))))
""")

md(r"""
## Theory 7. A letter in the function

The rules do not change. What changes is the ending: there is no number to
arrive at, so you have to decide when the expression is simplified enough —
and two habits decide it for you.

**Check on a value.** If the answer is supposed to be in terms of $m$, put
$m=2$ into both the original and your answer and differentiate numerically.
Ten seconds, and it catches a dropped factor every time.

**Keep the modulus.** $k_{\max}=2|a|$, not $2a$. A parabola opening downwards
curves exactly as hard as the one opening upwards, and the question that comes
next — *which of $p$ and $q$ is more curved* — is answerable only if the
modulus survived. Writing $2a$ gets one wrong answer and then a second one.
""")

md(r"""
## Task 9 🔴 — the curvature of a parabola

*May 2025 TZ1 Paper 3 Q2(b)(i) and (ii), 1 + 2 marks*

The curvature $k$ of a twice-differentiable function $f$ is

$$k(x)=\frac{\left|f''(x)\right|}
{\left(1+\left(f'(x)\right)^{2}\right)^{\frac32}} .$$

For the family $h(x)=ax^{2}+bx+c$, $a\ne0$, it is given that

$$k(x)=\frac{2|a|}{\left(1+(2ax+b)^{2}\right)^{\frac32}},\qquad
k'(x)=-\frac{12a|a|(2ax+b)}{\left(1+(2ax+b)^{2}\right)^{\frac52}} .$$

**(a)** By solving $k'(x)=0$, find the value of $x$ where $k_{\max}$ occurs.

**(b)** Determine an expression for $k_{\max}$, in terms of $a$ only.
""")

code(r"""
q9a = ...        # the x where k_max happens
q9b = ...        # k_max, in terms of a

verify_constants('9a', [q9a], [x],
                 [('the numerator of k′(x) vanishes there', 2*a*x + b)])
verify_exact('9b', q9b, 2*Abs(a))
""")

# ================================================================ Part III
md(r"""
---
# Part III — reading the derivative

## Theory 8. Fifty-one marks after the calculus is over

Rung 9 is the largest single block in the topic, and it needs no technique
that is not already above. The derivative exists — you found it in the part
before, or the question printed it — and what is being asked is what it says.

$$f'(x)=0\ \to\ \text{where the tangent is flat}\qquad
f'(x)<0\ \to\ \text{decreasing}\qquad
f''(x)>0\ \to\ \text{concave-up}$$

Four ways the marks actually go, all of them non-mathematical.

**"Coordinates" means two numbers.** Solving $f'(x)=0$ gives you the $x$'s;
each one has to go back into $f$. In the November 2022 question that is four
of the seven marks.

**The interval in the question is the interval.** $\mathrm{e}^{\cos 2x}$ on
$-\frac{\pi}{4}\le x\le\frac{5\pi}{4}$ has three flat points, not two. Read
the upper limit, then check whether the next solution fits — do not assume
either way.

**"Decreasing" is an inequality, not an equation.** Finding the critical
values is the method mark; writing the intervals between them is the answer
mark. And when there are two intervals, giving one of them scores the same as
giving none.

**A given derivative is the starting point.** When the question says
*the derivative of $f$ is given by $f'(x)=\dots$*, concave-up needs $f''$,
which means differentiating what you were handed — not $f$, which you do not
have.
""")

md(r"""
## Task 10 🟡 — find it, then read it

*November 2022 Paper 1 Q10(b), 7 marks*

The function $f$ is defined by $f(x)=\cos^{2}x-3\sin^{2}x$, $0\le x\le\pi$.

**(i)** Find $f'(x)$.

**(ii)** Hence find the coordinates of the points on the graph of $y=f(x)$
where $f'(x)=0$.
""")

code(r"""
q10a = ...       # f'(x)
q10b = [...]     # the points, each written as (x, y)

verify_derivative('10a', q10a, cos(x)**2 - 3*sin(x)**2)
verify_stationary('10b', q10b, cos(x)**2 - 3*sin(x)**2, domain=(0, pi))
""")

md(r"""
## Task 11 🟡 — two inequalities from one given derivative

*May 2025 TZ2 Paper 2 Q3, 3 + 3 marks*

The derivative of a function $f$ is given by $f'(x)=4+2x-3\mathrm{e}^{x}$,
where $x\in\mathbb{R}$.

**(a)** Find the values of $x$ for which $f$ is decreasing.

**(b)** Find the values of $x$ for which the graph of $f$ is concave-up.

*This is the one question in the practicum where the calculator earns its
place: the two critical values in (a) are $-1.73554\dots$ and
$0.517999\dots$, and nothing is going to give them to you exactly.*
""")

code(r"""
q11a = ...       # where f is decreasing
q11b = ...       # where the graph is concave-up

verify_param_set('11a', q11a,
                 lambda val: bool((4 + 2*x - 3*exp(x)).subs(x, val).evalf() < 0),
                 var=x, window=(-8, 4), tol=Rational(1, 100))
verify_param_set('11b', q11b,
                 lambda val: bool((2 - 3*exp(x)).subs(x, val).evalf() > 0),
                 var=x, window=(-8, 4), tol=Rational(1, 100))
""")

md(r"""
## Theory 9. When the letters are inside the function

Sometimes the unknowns are not the answer to a derivative but constants
buried in the function, and the question pins them with facts about the
curve. There is nothing to differentiate your way to; there is a system to
build.

Each sentence of the question is one equation, and the trick is knowing which
kind:

* **a vertical asymptote at $x=1$** → the denominator is zero there;
* **the curve passes through $(2,1)$** → substitute the point;
* **a local minimum at $(2,1)$** → the derivative is zero there, which for a
  quotient means the **numerator** of $\frac{\mathrm{d}y}{\mathrm{d}x}$ is
  zero there.

The mark scheme for the question below adds a warning worth carrying around:
*an incorrect numerator may lead to a correct equation* — and in that case
the mark is not given. Arriving at the right answer by the wrong route is
specifically not credited here.
""")

md(r"""
## Task 12 🔴 — three sentences, three equations

*May 2024 TZ2 Paper 2 Q9, 8 marks*

Consider the curve
$$y=\frac{x-4}{ax^{2}+bx+c},$$
where $a$, $b$ and $c$ are non-zero constants. The curve has a local minimum
point at $(2,1)$ and a vertical asymptote with equation $x=1$.

Find the values of $a$, $b$ and $c$.
""")

code(r"""
a_, b_, c_ = symbols('a_ b_ c_')
Y = (x - 4)/(a_*x**2 + b_*x + c_)
q12 = [...]      # a, b, c in that order

verify_constants('12', q12, [a_, b_, c_], [
    ('the denominator is zero at the asymptote x = 1',
     (a_*x**2 + b_*x + c_).subs(x, 1)),
    ('the curve passes through (2, 1)', Eq(Y.subs(x, 2), 1)),
    ('and the gradient there is zero, because it is a minimum',
     diff(Y, x).subs(x, 2)),
])
""")

# ================================================================ тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which rule you would
reach for first**. That is the decision the whole topic turns on, and on the
paper you get about five seconds of it.

| code | technique |
| --- | --- |
| `power` | power rule, term by term |
| `table` | a standard derivative: sec, cosec, cot, ln |
| `chain` | something inside a bracket |
| `product` | two moving factors multiplied |
| `quotient` | moving over moving |
| `form` | the answer is printed; the work is algebra |
| `higher` | a second or higher derivative |
| `letter` | the answer has to be in terms of a letter |
| `read` | the derivative exists; say what it means |

1. Find an expression for $f'(x)$ where $f(x)=\dfrac{3x+2}{4x^{2}-1}$.
2. Find $\dfrac{\mathrm{d}y}{\mathrm{d}x}$ for $y=\sqrt{r^{2}-x^{2}}$.
3. Find $f'(x)$ for $f(x)=\mathrm{e}^{2x}(3x-4)$.
4. Find the values of $x$ for which the graph of $f$ is concave-up, given $f'(x)=4+2x-3\mathrm{e}^{x}$.
5. Find $\dfrac{\mathrm{d}^{2}y}{\mathrm{d}x^{2}}$ for $y=x^{4}-3x^{3}+3x$.
6. Find $\dfrac{\mathrm{d}T}{\mathrm{d}\theta}$ for $T=500\sec\theta+\frac{2500-1000\tan\theta}{3}$.
7. Write down an expression for $f'(x)$ where $f(x)=x^{3}-3cx+2$.
8. Show that $f(x)g'(x)+g(x)f'(x)=\dfrac{4x}{(2-x)^{3}}$.
9. Determine an expression for $k_{\max}$ in terms of $a$ only.
10. Find the coordinates of the points on $y=\mathrm{e}^{\cos 2x}$ where the gradient is zero.
11. Show that $S_{3}'(x)=\cos\bigl(\sin(\sin x)\bigr)\cos(\sin x)\cos x$.
12. Prove that $f'\!\left(\sqrt{A}\right)$ is independent of $A$, where $f(x)=\dfrac{x\left(x^{2}-A\right)}{x^{2}+A}$.
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

*May 2023 TZ2 Paper 1 Q10(a), (b) and (c) — 8 marks. Ten minutes.*

Top of the notebook covered, paper and pen, formula booklet allowed.

A circle with equation $x^{2}+y^{2}=9$ has centre $(0,0)$ and radius $3$. A
triangle PQR is inscribed in the circle with vertices at $\mathrm{P}(-3,0)$,
$\mathrm{Q}(x,y)$ and $\mathrm{R}(x,-y)$, where Q and R are variable points
in the first and fourth quadrants respectively.

**(a)** For point Q, show that $y=\sqrt{9-x^{2}}$.

**(b)** Hence, find an expression for $A$, the area of triangle PQR, in
terms of $x$.

**(c)** Show that
$\dfrac{\mathrm{d}A}{\mathrm{d}x}=\dfrac{9-3x-2x^{2}}{\sqrt{9-x^{2}}}$.

Enter the answers to (b) and (c). Part (a) is one line on paper.

| date | time | notes |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_a = ...       # A, the area, in terms of x
qt_b = ...       # dA/dx

verify_identity('timer (b)', qt_a, (x + 3)*sqrt(9 - x**2))
verify_derivative('timer (c)', qt_b, (x + 3)*sqrt(9 - x**2))
""")

# ================================================================= решения
md(r"""
---
# 🔑 Solutions

---
### Task 1 — term by term, twice

**(a)** The $2k$ is a constant and goes; the chain rule on $(x-h)^{2}$ gives
$2(x-h)$:
$$f'(x)=-2(x-h)=2h-2x .$$
**A1.** One mark, both forms accepted.

**(b)**
$$G'(t)=\frac{1}{16}+\frac{6}{16}t+\frac{15}{16}t^{2}+\frac{28}{16}t^{3}
=\frac{1}{16}+\frac{3}{8}t+\frac{15}{16}t^{2}+\frac{7}{4}t^{3}.$$
**A1A1.** Unsimplified sixteenths are accepted.

The reason that question exists: $G$ is a probability generating function,
and $G'(1)=\frac{1+6+15+28}{16}=\frac{50}{16}$, which is $\mathrm{E}(M)$.
Differentiating a list of probabilities produces its mean.

---
### Task 2 — sec and tan in one line

$$\frac{\mathrm{d}T}{\mathrm{d}\theta}
=500\sec\theta\tan\theta-\frac{1000}{3}\sec^{2}\theta .$$
**A1A1A1** — one for $\sec\theta\tan\theta$, one for $\sec^{2}\theta$, one
for keeping the $\frac13$.

Two things to notice. The constant $\frac{2500}{3}$ vanishes entirely. And
the $\frac13$ has to survive onto the tangent term: the denominator belongs
to the whole second fraction, not to the $2500$ alone. That is the third mark
and the one most often dropped.

---
### Task 3 — inside, then out

**(a)** Chain rule with $u=x^{2}+1$:
$$g'(x)=2x\,\mathrm{e}^{x^{2}+1},\qquad g'(-1)=-2\mathrm{e}^{2}.$$
**A1A1A1A1.** $(-1)^{2}+1=2$, not $0$ — the square eats the sign, and the
exponent is $2$.

**(b)** Rewrite as $(2-x)^{-2}$:
$$f'(x)=-2(2-x)^{-3}\cdot(-1)=\frac{2}{(2-x)^{3}} .$$
**M1A1.** Two minus signs, both real, and they cancel. Forgetting the inner
$-1$ gives $-\frac{2}{(2-x)^{3}}$ — the right size and the wrong sign, which
is the worst kind of error because nothing downstream looks odd.

The quotient rule also works here and takes twice as long. Rewriting a
reciprocal as a negative power is the single cheapest habit in this topic.

---
### Task 4 — a product with a letter in the exponent

$u=x^{n}$, $v=(a-x)^{n}$, and $v$ needs the chain rule:
$$f_{n}'(x)=nx^{n-1}(a-x)^{n}+x^{n}\cdot n(a-x)^{n-1}\cdot(-1).$$
Take out $nx^{n-1}(a-x)^{n-1}$ — the lowest power of each:
$$=nx^{n-1}(a-x)^{n-1}\bigl[(a-x)-x\bigr]=nx^{n-1}(a-2x)(a-x)^{n-1}.
\qquad\textbf{AG}$$
**M1A1A1M1A1.** Five marks and three of them are the factorisation. The
bracket is $(a-x)-x$ because of the chain-rule $-1$; with $+x$ it would
collapse to $a$ and the whole of parts (d) to (h) would come out wrong.

Notice what the factorised form buys: $f_{n}'(x)=0$ now reads off as
$x=0,\frac{a}{2},a$ with no work at all. That is the next two marks.

---
### Task 5 — two quotients, one with a letter

**(a)** $u=3x+2$, $v=4x^{2}-1$:
$$f'(x)=\frac{3(4x^{2}-1)-(3x+2)(8x)}{(4x^{2}-1)^{2}}
=\frac{12x^{2}-3-24x^{2}-16x}{(4x^{2}-1)^{2}}
=\frac{-12x^{2}-16x-3}{(4x^{2}-1)^{2}} .$$
**M1A1A1.** The numerator does not factorise over the integers; this is the
final form.

**(b)** $u=(2x+a)^{3}$, $v=(x+5)^{2}$, and both need the chain rule:
$$f'(x)=\frac{6(2x+a)^{2}(x+5)^{2}-2(2x+a)^{3}(x+5)}{(x+5)^{4}} .$$
Cancel one $(x+5)$ and take out $2(2x+a)^{2}$:
$$=\frac{2(2x+a)^{2}\bigl[3(x+5)-(2x+a)\bigr]}{(x+5)^{3}}
=\frac{2(2x+a)^{2}(x-a+15)}{(x+5)^{3}} .$$
**M1A1A1.** The mark scheme accepts the unsimplified version — and the next
part of that question needs $f'(1)=\tan70^{\circ}$, which on the tidy form is
one substitution and on the untidy one is a page. The two values that come
out are $a=2.73$ and $a=15.0$.

---
### Task 6 — the same destination, twice

**(a)** $f'(x)=\frac{2}{(2-x)^{3}}$ and $g'(x)=2x$, so the product is
$\frac{4x}{(2-x)^{3}}$. **A1A1** — two marks for a multiplication, because
the paper is establishing this expression once and using it twice.

**(b)**
$$f g'+g f'=\frac{2x}{(2-x)^{2}}+\frac{2x^{2}}{(2-x)^{3}}
=\frac{2x(2-x)+2x^{2}}{(2-x)^{3}}
=\frac{4x-2x^{2}+2x^{2}}{(2-x)^{3}}=\frac{4x}{(2-x)^{3}} .\qquad\textbf{AG}$$
**M1A1A1A1.**

The common denominator is $(2-x)^{3}$ because $(2-x)^{2}$ divides it. Using
$(2-x)^{5}$ is not wrong, it is just three lines longer and one of those lines
usually goes astray.

What this pair of functions is for: $f g'+g f'=f'g'$, that is, the product
rule and the wrong "rule" happen to agree. Part (b) of that Paper 3 then
rearranges the coincidence into $\frac{f'}{f}=\frac{g'}{g'-g}$, which is a
differential equation in disguise.

---
### Task 7 — a relation between derivatives

$$g'(x)=\mathrm{e}^{x}\cos x-\mathrm{e}^{x}\sin x,\qquad
g''(x)=-2\mathrm{e}^{x}\sin x .$$
And $2\bigl(g'-g\bigr)=2\bigl(-\mathrm{e}^{x}\sin x\bigr)=-2\mathrm{e}^{x}
\sin x=g''$. $\textbf{AG}$ **M1A1A1**

For (ii), do **not** differentiate $g$ two more times. Differentiate the
identity:
$$g'''=2\bigl(g''-g'\bigr),\qquad g^{(4)}=2\bigl(g'''-g''\bigr).
\qquad\textbf{A1A1}$$
An equality between functions stays an equality when both sides are
differentiated, and *hence deduce* is telling you so. Two marks, no work.

That identity is also how E2 builds the Maclaurin series for
$\mathrm{e}^{x}\cos x$: put $x=0$ into it and the derivatives at zero become
a numerical recursion.

---
### Task 8 — a pole round a corner

**(a)**
$$\frac{\mathrm{d}L}{\mathrm{d}\alpha}
=\frac{3}{4}\sec\alpha\tan\alpha-6\csc\alpha\cot\alpha .$$
**A1A1.** The minus on the $\csc$ term is what makes
$\frac{\mathrm{d}L}{\mathrm{d}\alpha}=0$ solvable; without it the two terms
have the same sign and there is no stationary point at all.

Setting it to zero, in sines and cosines:
$$\frac{3\sin\alpha}{4\cos^{2}\alpha}=\frac{6\cos\alpha}{\sin^{2}\alpha}
\;\Longrightarrow\;\sin^{3}\alpha=8\cos^{3}\alpha
\;\Longrightarrow\;\tan^{3}\alpha=8\;\Longrightarrow\;\tan\alpha=2 .$$
The cube root of a real number is unique, so $\tan\alpha=2$ and no $\pm$.

**(b)** Product rule on each term:
$$\frac{\mathrm{d}^{2}L}{\mathrm{d}\alpha^{2}}
=\frac{3}{4}\left(\sec\alpha\tan^{2}\alpha+\sec^{3}\alpha\right)
+6\left(\csc\alpha\cot^{2}\alpha+\csc^{3}\alpha\right).$$
**A1A1A1A1.**

**(c)** $\tan\alpha=2$ means a right triangle with legs $2$ and $1$ and
hypotenuse $\sqrt5$, so $\sec\alpha=\sqrt5$, $\csc\alpha=\frac{\sqrt5}{2}$,
$\cot\alpha=\frac12$:
$$\frac{3}{4}\left(4\sqrt5+5\sqrt5\right)
+6\left(\frac{\sqrt5}{8}+\frac{5\sqrt5}{8}\right)
=\frac{27\sqrt5}{4}+\frac{18\sqrt5}{4}=\frac{45\sqrt5}{4} .\qquad\textbf{AG}$$
**M1A1A1.**

Draw the triangle. Going through $\alpha=\arctan2$ on a calculator and back
gives a decimal that will not turn into $\frac{45\sqrt5}{4}$, and this is a
Paper 1.

Both terms come out positive, which is the point: $\frac{\mathrm{d}^{2}L}
{\mathrm{d}\alpha^{2}}>0$ makes $\alpha=\arctan2$ a minimum of $L$. And the
minimum of $L$ is the longest pole that fits round the corner:
$$L_{\min}=\frac{3\sqrt5}{4}+3\sqrt5=\frac{15\sqrt5}{4}\approx8.39\ \text{m},$$
which is well short of $11.25$ m — so the pole does **not** go round. The
whole twenty-mark question exists for that one comparison, and it turns on
$L$ being *minimised*: the tightest position is the one that decides.

---
### Task 9 — the curvature of a parabola

**(a)** $k'(x)=0$ needs the numerator to vanish, and $12a|a|\ne0$, so
$2ax+b=0$:
$$x=-\frac{b}{2a} .$$
**A1.** The vertex — a parabola curves hardest exactly where it turns, which
is worth a second's thought before you believe it.

**(b)** At that $x$ the bracket $(2ax+b)$ is zero, so the denominator of $k$
is $1$:
$$k_{\max}=2|a| .$$
**M1A1.**

The modulus is the mark. $p(x)=-2x^{2}+2x-10$ and $q(x)=2x^{2}+5x+25$ both
have $|a|=2$, so both have $k_{\max}=4$ and part (iv)'s answer is **C**. With
$2a$ instead you would get $-4$ and $4$, conclude that $q$ curves more, and
lose two questions from one dropped pair of bars.

---
### Task 10 — find it, then read it

**(i)** $f(x)=\cos^{2}x-3\sin^{2}x$, so by the chain rule on each square
$$f'(x)=-2\cos x\sin x-6\sin x\cos x=-8\sin x\cos x=-4\sin 2x .$$
**A1A1.** Rewriting with the double angle first —
$f=\frac{1+\cos2x}{2}-3\cdot\frac{1-\cos2x}{2}=2\cos2x-1$ — gives the same
answer in one line, and makes (ii) instant.

**(ii)** $\sin 2x=0$ on $0\le x\le\pi$ at $x=0,\frac{\pi}{2},\pi$, and back
into $f$:
$$(0,1),\qquad\left(\tfrac{\pi}{2},-3\right),\qquad(\pi,1).$$
**M1A1A1A1A1.** Five of the seven marks are here and four of them are the
$y$-coordinates. The endpoints count — the interval is closed.

---
### Task 11 — two inequalities from one given derivative

**(a)** Decreasing means $f'(x)<0$, that is $4+2x-3\mathrm{e}^{x}<0$. On the
GDC the two critical values are $-1.73554\dots$ and $0.517999\dots$, and
between them $f'>0$ (at $x=0$ it is $1$). So
$$x\le-1.74\quad\text{or}\quad x\ge0.518 .$$
**A1M1A1.** The mark scheme accepts strict and non-strict alike, so the
endpoints are not where the mark is. Giving only one of the two stretches is.

**(b)** Concave-up means $f''(x)>0$, and $f''(x)=2-3\mathrm{e}^{x}$:
$$2-3\mathrm{e}^{x}>0\;\Longrightarrow\;\mathrm{e}^{x}<\tfrac23
\;\Longrightarrow\;x<\ln\tfrac23\ (=-0.405).$$
**A1M1A1.** One stretch this time, because $f''$ is decreasing everywhere.

The trap in (b) is differentiating $f$. You do not have $f$ — the question
gave you $f'$, and $f''$ is one differentiation of *that*.

---
### Task 12 — three sentences, three equations

**Vertical asymptote at $x=1$.** The denominator vanishes there:
$$a+b+c=0 .$$

**The curve passes through $(2,1)$.**
$$\frac{2-4}{4a+2b+c}=1\;\Longrightarrow\;4a+2b+c=-2 .$$

**A local minimum at $x=2$.** The gradient is zero there, and for a quotient
that means the numerator of $\frac{\mathrm{d}y}{\mathrm{d}x}$ is zero:
$$\bigl(ax^{2}+bx+c\bigr)-(x-4)(2ax+b)=0\ \text{at }x=2,$$
$$(4a+2b+c)-(-2)(4a+b)=0\;\Longrightarrow\;12a+4b+c=0 .$$

Solving the three:
$$a=3,\qquad b=-11,\qquad c=8 .$$
**M1A1A1M1(M1)A1M1A1.** Eight marks, two of them calculus.

The mark scheme's warning is the thing to remember: *an incorrect numerator
may lead to a correct equation* — and then the mark is withheld. A right
answer reached by a wrong route is specifically not credited on this
question, which is unusual enough to be worth knowing exists.

---
### On the timer

**(a)** Q is on the circle in the first quadrant, so $x^{2}+y^{2}=9$ with
$y>0$ gives $y=\sqrt{9-x^{2}}$. **A1**

**(b)** QR is vertical with length $2y=2\sqrt{9-x^{2}}$, and the horizontal
distance from P to that line is $x-(-3)=x+3$:
$$A=\tfrac12\cdot2\sqrt{9-x^{2}}\cdot(x+3)=(x+3)\sqrt{9-x^{2}} .$$
**M1A1A1**

**(c)** Product rule, with the chain rule inside:
$$\frac{\mathrm{d}A}{\mathrm{d}x}=\sqrt{9-x^{2}}
+(x+3)\cdot\frac{-x}{\sqrt{9-x^{2}}}
=\frac{(9-x^{2})-x(x+3)}{\sqrt{9-x^{2}}}
=\frac{9-3x-2x^{2}}{\sqrt{9-x^{2}}} .\qquad\textbf{AG}$$
**M1A1M1A1**

The $-2x^{2}$ needs both $x^{2}$ terms: one from $9-x^{2}$ and one from
$-x(x+3)$. Losing either gives $9-3x-x^{2}$, which looks entirely reasonable
and is not the printed line.

Part (d), for the record: $9-3x-2x^{2}=0$ gives $x=\frac{3}{2}$, and the
$y$-coordinate of R is $-\sqrt{9-\frac94}=-\frac{3\sqrt3}{2}$.

---
### Key to the recognition drill

1 `quotient` — moving top over moving bottom.
2 `chain` — a bracket with $x$ inside a square root.
3 `product` — two moving factors multiplied.
4 `read` — the derivative is given; concave-up is a statement about $f''$.
5 `higher` — a second derivative, asked for directly.
6 `table` — $\sec$ and $\tan$, straight from the booklet.
7 `power` — a sum of powers, and $c$ is a constant.
8 `form` — the answer is printed; the work is a common denominator.
9 `letter` — *in terms of $a$ only*.
10 `read` — solve $f'=0$, then substitute back for the coordinates.
11 `chain` — three nested sines, three cosine factors.
12 `quotient` — and then a substitution, but the rule is the quotient rule.

Three of these are worth arguing about, and the argument is the point.

**2 could be `power`.** $\sqrt{r^{2}-x^{2}}$ is $(r^{2}-x^{2})^{1/2}$, so the
power rule is involved — but the base is not $x$, and that is exactly what
makes it `chain`. The power rule alone applies to $x^{n}$; anything else
inside needs its own derivative brought out.

**5 could be `power`.** It is: $\frac{\mathrm{d}^{2}}{\mathrm{d}x^{2}}
(x^{4}-3x^{3}+3x)$ is two applications of the power rule and nothing else.
It is `higher` because the thing being drilled is doing it twice without
losing the constant on the way.

**12 could be `letter`.** The answer does have $A$ in it — right up until it
does not, which is the whole question. The rule you reach for is still the
quotient rule; the letter is the punchline, not the technique.

---
### Where the marks went, across the topic

| technique | marks | share |
| --- | --- | --- |
| Read the derivative | 51 | 27% |
| Second and higher | 29 | 15% |
| A letter in it | 27 | 14% |
| Quotient rule | 22 | 12% |
| Chain rule | 18 | 10% |
| Product rule | 14 | 7% |
| To the printed line | 10 | 5% |
| The table | 10 | 5% |
| Power rule, term by term | 7 | 4% |

Three things stand out.

**Choosing the rule is worth a quarter of the topic.** Rungs 1–5 carry $71$
marks between them and rungs 6–9 carry $117$. The differentiation is the part
everyone practises and the part that is worth least; the algebra afterwards
and the reading of the result are worth more and get practised less. That is
the same shape E2 had — building the series was worth less than spending it —
and it is starting to look like a property of the whole calculus section
rather than of either topic.

**Reading the derivative is the largest block and needs no new technique.**
Fifty-one marks, all of them after the calculus is over. The failures there
are a coordinate given as one number, an interval read short, and
*decreasing* solved as an equation — none of which is a failure of calculus.

**Thirty-four of the fifty-five blocks are Paper 3.** This topic does not
appear as a five-mark question; it appears as a step inside a twenty-eight
mark investigation, taken over and over. Two of them — May 2025 on curvature
and November 2022 on surfaces of revolution — carry $39$ marks between them.
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
