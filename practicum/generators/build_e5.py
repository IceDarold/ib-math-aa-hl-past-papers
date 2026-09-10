"""Собирает практикум E5: техника интегрирования.

Двенадцатый практикум серии и первая половина темы
calculus.integration_applications. Лестница из восьми приёмов идёт по тому,
что мешает взять первообразную: 1–2 — ничего не мешает, таблица подходит
сразу или после замены; 3–5 — подынтегральное выражение надо сначала
разобрать; 6–7 — первообразной в конечном виде нет; 8 — первообразная уже
не вопрос.

Восемнадцатое понятие равенства ответов: первообразная узнаётся по своей
производной. У производной ответ один, у первообразной ответа нет вовсе —
есть семейство, отличающееся постоянной, и сверять не с чем. Раздел kit
написан так, что вычислить ответ он не может в принципе: внутри нет ни
одного интегрирования, ни sympy, ни своего. Проверка умеет ровно одно —
продифференцировать написанное и посмотреть, вышла ли подынтегральная
функция; постоянная исчезает сама, как бы она ни была одета.

Шесть новых проверок. `verify_antiderivative` — производная написанного
равна подынтегральной функции, а с through ещё и график проходит через
точку. `verify_integral` — число, взятое адаптивным Симпсоном по самому
выражению, с лестницей к бесконечному пределу. `verify_accumulated` —
основная теорема: G′(s) = f(s) и G(a) = 0. `verify_transformed` — замена
законна, когда g(u(x))·u′(x) = f(x). `verify_reduction` — формула понижения
как численное тождество между интегралами. `verify_termwise` — производная
ответа совпадает с рядом подынтегральной функции до заказанной степени.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_e5.py прогоняет по нему весь ноутбук и требует,
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

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e5-integration.ipynb')

TRIGGER = {1: 'parts', 2: 'apart', 3: 'table', 4: 'series', 5: 'usub',
           6: 'logint', 7: 'reduce', 8: 'condition', 9: 'parts', 10: 'usub',
           11: 'condition', 12: 'apart'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '3*x - 10*sqrt(x)',
    'q1': '4',
    'q2': 'x**3 + 5*exp(x) - 1',
    'q3': 'x**3 + 6*x**2 - 15*x - 10',
    'q4a': '1/k',
    'q4b': '1/k',
    'q4': 'log(x/(k - x))/k',
    'q5': '3*log(1 + x**2) + 5 - 3*log(2)',
    'q6u': 'u**(n - 1)',
    'q6': '(2**n - 1)/n',
    'q7u': '2*t*cos(t)',
    'q7': '2*sin(sqrt(x)) - 2*sqrt(x)*cos(sqrt(x))',
    'q8': 'x**2*log(x)**2/2 - x**2*log(x)/2 + x**2/4',
    'q8e': '(E**2 - 1)/4',
    'q9': '(x**2 - 2*x - 3)*exp(x)',
    'q10': 'x*acos(x) - sqrt(1 - x**2)',
    'q11a': '-(x + 1)*exp(-x)',
    'q11one': '1',
    'q11four': '24',
    'q11five': '120',
    'q11n': 'factorial(n)',
    'q12': '3/(x + 3) - 1/(x - 4)',
    'q12v': '5*log(2)',
    'q13u': 'u/(u**2 - u - 2)',
    'q13p': 'Rational(1, 3)/(u + 1) + Rational(2, 3)/(u - 2)',
    'q13': 'log(Abs(sin(x) + 1))/3 + 2*log(Abs(sin(x) - 2))/3',
    'q14': 'log(Abs((1 + v)/(1 - v)))/2 + log(A)/2',
    'q15d': 'exp(x + x**2/2)',
    'q15e': 'exp(x/2)*sqrt(sin(x))',
    'q16': '-sin(x)**(n - 1)*cos(x)/n + (n - 1)*J(n - 2)/n',
    'q16c': 'cos(x)**3*sin(x)/4 + 3*cos(x)*sin(x)/8 + 3*x/8',
    'q17a': 'x - x**3/3 + x**5/5 - x**7/7 + C',
    'q17b': 'x + x**3/6 + 3*x**5/40 + C',
    'q17k': '3',
    'q18s': 'E - 2*E*x**2',
    'q18': '73*E/375',
    'q19': '4',
    'q20k': '0.713250',
    'q21a': '-1.6',
    'q21b': '3.2',
    'qt': '(E**2 - 1)/4',
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
# Practicum E5: techniques of integration

**157 marks, 39 blocks, eight techniques.** One question runs through all of
them: *what is the antiderivative?* Every technique in this practicum is a way
of making an integrand look like something the table already knows.

**Material.** The half of `calculus.integration_applications` in the AA HL
archive where the answer is an antiderivative or the number an antiderivative
gives, sessions May 2021 — November 2025. The whole topic is 354 marks — twice
what a practicum may hold — so it is cut in two by what the question asks for:
*find $\int x(\ln x)^2\,\mathrm{d}x$* is here, *find the area* is E6.

**This practicum is in English,** like B2 to B5 and E1 to E4. The checks speak
whichever language the notebook asks them to, and this one asks for English in
the setup cell.

**The one thing to carry out of here.**

> An antiderivative is not an answer, it is a **family**. $F$ and $F+7$ are
> equally right, and so are $F+\ln A$ and $F+\tfrac12\ln A$. The only question
> that has a definite answer is *does the derivative come back?* — and that is
> the question you should be asking yourself at the end of every one of these,
> because it costs ten seconds and it is the whole mark scheme.

And the thing that follows from it: **you can always check your own work
here, completely, without the answer.** Differentiate what you wrote. This is
not true of most topics, and it is true of every single mark in this one.

**Where the calculator sits.** 45% of the marks formally carry one, and this
is the least calculator-flavoured topic in the whole series: **86 of the 157
marks are Paper 1**, against 27% in E3 and 23% in E4. Substitution,
integration by parts and partial fractions are exactly the things a GDC does
not do. The two places a calculator genuinely earns its keep are
$A_4=\int_0^{\infty}x^4\mathrm{e}^{-x}\,\mathrm{d}x=24$, where the upper limit
has to be faked, and $k=0.713250$ to six significant figures.

**How the checks work here.** Six are new, and all six rest on one thing:
**the checks never integrate.** There is not one call to `integrate` inside
this part of `kit.py`, by sympy or by hand — a test proves it by reading the
source. The checks can *recognise* an antiderivative; they cannot produce one.

| check | what it does to your answer |
| --- | --- |
| `verify_antiderivative` | differentiates it, and wants the integrand back |
| `verify_antiderivative(..., through=)` | the same, and the graph must pass through the given point |
| `verify_integral` | adds the integrand up by adaptive Simpson and compares numbers |
| `verify_accumulated` | $G'(s)=f(s)$ **and** $G(a)=0$ — the fundamental theorem, both halves |
| `verify_transformed` | pushes your substitution forward: $g(u(x))\,u'(x)$ must be $f(x)$ |
| `verify_reduction` | evaluates both sides of your recursion for several $n$ |
| `verify_termwise` | differentiates it and matches the integrand's series to the ordered degree |

Three consequences worth knowing before you start.

**The constant is free, in any costume.** `+ C`, `- 1`, `+ log(A)/2`,
`+ 5 - 3*log(2)` — all of them differentiate to zero, so all of them pass.
When the constant is *not* free, the question gives you a point, and the check
is told about it.

**`ln|x|` and `ln x` are the same answer.** The check strips the modulus
before differentiating, because $\ln|g|$ and $\ln g$ have the same derivative
wherever both exist.

**A wrong constant factor is named, not just refused.** Writing
$\sin 3x$ for $\int\cos 3x\,\mathrm{d}x$ gets you told that your derivative is
exactly three times the integrand — which is the single commonest slip in this
topic and the one your own differentiation would have caught.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, sqrt, pi, E, log, Eq

language('en')                 # this notebook is in English, and so are the checks

a, b, c, g, n, p, q, r, s = symbols('a b c g n p q r s')   # letters that stay letters
J = Function('J')              # J(m) means "the integral of f_m", used in task 14
                               # x, y, t, u, v, A, C, k already come from kit

print('ready; sympy', sp.__version__)
print('an integrand:      ', x*log(x)**2)
print('an antiderivative: ', x**2*log(x)**2/2 - x**2*log(x)/2 + x**2/4)
print('the same family:   ', x**2*log(x)**2/2 - x**2*log(x)/2 + x**2/4 + C)
print('a definite value:  ', (E**2 - 1)/4)
""")

md(r"""
---
## Map of techniques

| # | Technique | What the integrand looks like | First move |
| --- | --- | --- | --- |
| 1 | Table, plus a constant from a point | a sum of powers, exponentials and plain trigonometric terms | rewrite every term as a power |
| 2 | Substitution | a function sitting beside its own derivative | name $u$, and say what $\mathrm{d}x$ becomes |
| 3 | Integration by parts | a product of two unlike things, or a lone $\ln$ or inverse trigonometric function | pick the factor that simplifies when differentiated |
| 4 | Partial fractions | one fraction whose denominator factorises | split it before integrating anything |
| 5 | The quotient is $f'/f$ | a fraction whose top is the bottom differentiated | check that guess before doing anything else |
| 6 | Reduction formula | a power $n$ that is left as a letter | split off one factor and integrate by parts |
| 7 | Integrate the series | a function with no elementary antiderivative | expand first, integrate term by term |
| 8 | The integral is a condition | the value of the integral is *given* | write the equation, then solve it |

**The ladder goes by what is standing between you and the table.**

**Rungs 1–2 — nothing much.** Thirty-five marks. Either the integrand is
already in the table, or one change of variable puts it there. All seventeen
marks of rung 2 are Paper 1.

**Rungs 3–5 — the integrand has to be taken apart first.** Eighty-three marks,
over half the topic. A product is separated by parts, a fraction is split into
simple ones, a quotient turns out to be $f'/f$ in disguise. This is where the
topic actually lives.

**Rungs 6–7 — there is no antiderivative in closed form.** Twenty-five marks.
Either you recurse on the exponent, or you give up on the function and
integrate its series instead.

**Rung 8 — the antiderivative is not the question.** Fourteen marks. The value
of the integral is handed to you and a limit, or a constant, is what comes out.

**The three facts the whole topic runs on.**

$$\int u\,\mathrm{d}v = uv-\int v\,\mathrm{d}u$$

$$\int f(g(x))\,g'(x)\,\mathrm{d}x=\int f(u)\,\mathrm{d}u
\qquad\text{with}\quad u=g(x)$$

$$\int\frac{f'(x)}{f(x)}\,\mathrm{d}x=\ln|f(x)|+c$$

Everything else in these 157 marks is deciding which of the three you are
looking at.
""")

# ================================================================== Part I
md(r"""
---
# Part I — the antiderivative is visible

## Theory 1. Two different things are called "the integral"

$\int f(x)\,\mathrm{d}x$ is a **family of functions**. $\int_a^b f(x)\,\mathrm{d}x$
is a **number**. They are related by one line, and the line is worth reading
slowly:

$$\int_a^b f(x)\,\mathrm{d}x = F(b)-F(a)\quad\text{for any }F\text{ in the family.}$$

*Any* $F$ — because the constant cancels in the subtraction. That is why the
constant matters in one of these and not in the other, and it is why *both*
of the following are whole marks in this archive:

**Losing $+c$.** The mark scheme says "condone absence of $+c$" in some years
and does not in others. When a point on the graph is given, absence of $+c$ is
never condoned, because there is then nothing to substitute into.

**Substituting only the top limit.** $F(b)-F(a)$, not $F(b)$. Every year.

**The one rewrite that unlocks rung 1.** Everything that is not obviously a
power has to be made into one before the table applies:

$$\sqrt[3]{x^2}=x^{2/3}\ \longrightarrow\ \int x^{2/3}\,\mathrm{d}x
=\frac{x^{5/3}}{5/3}=\frac{3}{5}x^{5/3}$$

Raise the index by one **and divide by the new index**. The second half is
where the marks go.
""")

md(r"""
## Task 1 🟢 — a definite integral, and the antiderivative behind it

*May 2022 TZ1 Paper 1 Q1, 5 marks · no calculator*

Find the value of $\displaystyle\int_1^9\left(3-\frac{5}{\sqrt x}\right)\mathrm{d}x$.
""")

code(r"""
q1a = ...        # an antiderivative of 3 - 5/sqrt(x), with or without + c
q1 = ...          # the value of the definite integral

verify_antiderivative('1a', q1a, 3 - 5/sqrt(x), domain=(0.5, 9))
verify_integral('1', q1, 3 - 5/sqrt(x), 1, 9)
""")

md(r"""
## Task 2 🟢 — $f'$ and one point, twice

*May 2022 TZ2 Paper 2 Q2, 5 marks · calculator ·
and November 2025 TZ1 Paper 1 Q9(e), 4 marks · no calculator*

**(a)** The derivative of a function $g$ is $g'(x)=3x^2+5\mathrm{e}^x$, and the
graph of $g$ passes through $(0,4)$. Find $g(x)$.

**(b)** The function $f$ has derivative $f'(x)=3x^2+12x-15$. Given that
$f(-2)=36$, find $f(x)$.

**(c)** *November 2022 Paper 1 Q4, 5 marks.* The derivative of $f$ is
$f'(x)=\dfrac{6x}{1+x^2}$, and the graph of $y=f(x)$ passes through $(1,5)$.
Find an expression for $f(x)$.

All three are the same three lines. Integrate, add $c$, use the point. The
check is told about the point, so leaving $c$ as a letter will not pass. The
third one is here to show that the shape of the question does not change when
the integration itself needs a substitution — which is the next rung.
""")

code(r"""
q2 = ...         # g(x)
q3 = ...         # f(x)
q5 = ...         # f(x) for part (c)

verify_antiderivative('2a', q2, 3*x**2 + 5*exp(x), through=(0, 4))
verify_antiderivative('2b', q3, 3*x**2 + 12*x - 15, through=(-2, 36))
verify_antiderivative('2c', q5, 6*x/(1 + x**2), through=(1, 5))
""")

md(r"""
## Task 3 🟡 — the same, with a letter in it

*May 2021 TZ1 Paper 2 Q12(a)(b), 6 marks · calculator*

The function $f$ has derivative
$$f'(x)=\frac{1}{x(k-x)},\qquad x\ne 0,\ x\ne k,$$
where $k$ is a positive constant.

**(a)** $f'(x)$ can be written as $\dfrac{a}{x}+\dfrac{b}{k-x}$. Find $a$ and
$b$ in terms of $k$.

**(b)** Hence find an expression for $f(x)$.

Nothing changes because $k$ is a letter — except that the check now runs your
answer at several values of $k$ and wants it right at every one.
""")

code(r"""
q4a = ...        # a, in terms of k
q4b = ...        # b, in terms of k
q4 = ...          # f(x); the constant is free here, no point was given

verify_identity('3a', ... if blank(q4a, q4b) else q4a/x + q4b/(k - x),
                1/(x*(k - x)))
verify_antiderivative('3b', q4, 1/(x*(k - x)), domain=(0.1, 0.9),
                      params={k: (1, 3, 8)})
""")

md(r"""
## Theory 2. Substitution is a statement about $\mathrm{d}x$

The rule is usually written

$$\int f(g(x))\,g'(x)\,\mathrm{d}x=\int f(u)\,\mathrm{d}u,$$

and read as "replace $g(x)$ by $u$". That reading loses marks, because it
quietly skips the part that actually does the work:

$$u=g(x)\ \Longrightarrow\ \mathrm{d}u=g'(x)\,\mathrm{d}x
\ \Longrightarrow\ \mathrm{d}x=\frac{\mathrm{d}u}{g'(x)}.$$

**The substitution divides by the derivative.** If you forget that, your answer
comes out wrong by exactly a constant factor — and that is the slip the check
names by name, because it is the commonest one in the topic.

**Definite integrals: change the limits or change back, never neither.**
$\int_0^{\pi/3}$ becomes $\int_1^{2}$ when $u=\sec x$, because
$\sec 0=1$ and $\sec\tfrac{\pi}{3}=2$. Substituting $x=\pi/3$ into an
expression in $u$ is a wrong answer that looks like a right one.

**How to spot the substitution.** Look for a function sitting next to its own
derivative, possibly times a constant:

$$\underbrace{\mathrm{e}^{x^3}}_{f(u)}\cdot\underbrace{x^2}_{u'\text{, times }\tfrac13},
\qquad
\underbrace{\frac{1}{\ln x}}_{f(u)}\cdot\underbrace{\frac1x}_{u'},
\qquad
x\sqrt{x-1}\ \text{with}\ u=x-1 .$$

The third one is the interesting case: there is no derivative anywhere in
sight. The substitution has to *make* the integrand fit, and the stray $x$
becomes $u+1$ — so $x\sqrt{x-1}\,\mathrm{d}x$ turns into
$(u+1)\sqrt u\,\mathrm{d}u$, which is two powers and nothing else. When a
substitution leaves an $x$ behind, that $x$ has to be rewritten, not ignored.
""")

md(r"""
## Task 4 🟡 — the substitution is named for you

*May 2022 TZ2 Paper 1 Q7, 6 marks · no calculator*

By using the substitution $u=\sec x$ or otherwise, find an expression for
$$\int_0^{\pi/3}\sec^n x\,\tan x\,\mathrm{d}x$$
in terms of $n$, where $n$ is a non-zero real number.

**(a)** Write the integrand after the substitution, as an expression in $u$.
This is the thing the mark scheme gives A1 for.

**(b)** Give the value of the integral in terms of $n$.
""")

code(r"""
q6u = ...        # the integrand in terms of u, once du has absorbed the dx
q6 = ...          # the value of the definite integral, in terms of n

# The check pushes your substitution back: it replaces u by sec(x), multiplies
# by the derivative of sec(x), and wants the original integrand to reappear.
verify_transformed('4a', q6u, sec(x)**n*tan(x), sec(x), domain=(0.1, 1.0))
verify_integral('4b', q6, sec(x)**n*tan(x), 0, pi/3, params={n: (2, 3, 5, -1)})
""")

md(r"""
## Task 5 🟡 — the substitution that creates a derivative

*May 2023 TZ2 Paper 1 Q12(a), 6 marks · no calculator*

By using an appropriate substitution, the paper asks you to show that
$$\int\cos\sqrt x\,\mathrm{d}x = 2\sqrt x\sin\sqrt x+2\cos\sqrt x+C.$$

That answer is printed in the question, so there is nothing to hand in — the
mark scheme is buying the *route*. So hand in the route, and then do the one
the paper did not ask.

**(a)** With $t=\sqrt x$, write the integrand in terms of $t$, including what
$\mathrm{d}x$ becomes.

**(b)** Now find $\displaystyle\int\sin\sqrt x\,\mathrm{d}x$, by the same route.
""")

code(r"""
q7u = ...        # the integrand of the cosine one, in terms of t
q7 = ...          # an antiderivative of sin(sqrt(x))

verify_transformed('5a', q7u, cos(sqrt(x)), sqrt(x), new=t, domain=(0.2, 4.0))
verify_antiderivative('5b', q7, sin(sqrt(x)), domain=(0.2, 4.0))
""")

# ================================================================= Part II
md(r"""
---
# Part II — the integrand has to be taken apart

## Theory 3. Integration by parts: what "simplifies" means

$$\int u\,\mathrm{d}v=uv-\int v\,\mathrm{d}u$$

The whole skill is choosing $u$. The rule of thumb people repeat — LIATE —
is a memory aid for one real criterion:

> **$u$ is the factor that gets *simpler* when differentiated, and $\mathrm{d}v$
> is the factor you can integrate without regret.**

$(\ln x)^2\to\ 2\ln x/x$: simpler. $x^2\to 2x\to 2$: simpler, and it dies in
two steps. $\mathrm{e}^x\to\mathrm{e}^x$: no progress, so $\mathrm{e}^x$ is
never $u$ when something else is available.

**Three shapes appear in this archive, and they behave differently.**

**A polynomial times an exponential.** $\int(x^2+3x)\mathrm{e}^{2x}\,\mathrm{d}x$.
Two applications, and the polynomial is gone. This one always terminates,
and the number of applications is the degree of the polynomial.

**A power times a logarithm.** $\int x(\ln x)^2\,\mathrm{d}x$. Two
applications, and the logarithms are gone — but the second application is on
$\int x\ln x\,\mathrm{d}x$, not on the original, which is where the sign
errors live.

**A lone function with no product in it.** $\int\ln x\,\mathrm{d}x$. There is
no product at all until you write one: $\mathrm{d}v=1\cdot\mathrm{d}x$,
$u=\ln x$. Then $v=x$ and

$$\int\ln x\,\mathrm{d}x=x\ln x-\int x\cdot\frac1x\,\mathrm{d}x=x\ln x-x+c,$$

where the remaining integral collapsed to $\int1\,\mathrm{d}x$. Notice that
parts turned a function with no obvious antiderivative into one that has a
very obvious one. That is what parts is *for*, and it is the move to try on
any lone $\ln$ or lone inverse trigonometric function.
""")

md(r"""
## Task 6 🟡 — twice by parts, and a definite value

*November 2023 TZ1 Paper 1 Q8, 9 marks · no calculator*

**(a)** Find $\displaystyle\int x(\ln x)^2\,\mathrm{d}x$.

The paper's part (b) then asks you to show that $\int_1^4$ of the same thing
is $32(\ln 2)^2-16\ln 2+\tfrac{15}{4}$ — printed, so nothing to hand in.

**(b)** Evaluate $\displaystyle\int_1^{\mathrm{e}}x(\ln x)^2\,\mathrm{d}x$
instead. The limits are kinder and the answer is short.
""")

code(r"""
q8 = ...          # an antiderivative of x*(ln x)^2
q8e = ...        # the value between 1 and e, exactly

verify_antiderivative('6a', q8, x*log(x)**2, domain=(0.4, 3.0))
verify_integral('6b', q8e, x*log(x)**2, 1, E)
""")

md(r"""
## Task 7 🟡 — a polynomial that dies in two steps

*May 2025 TZ3 Paper 2 Q12(a), 6 marks · calculator*

Find $\displaystyle\int(x^2-5)\mathrm{e}^x\,\mathrm{d}x$.

The mark scheme's answer is $(x^2-2x-3)\mathrm{e}^x+c$. Get it wrong by one
sign and the check will tell you nothing more than that it is wrong — so
differentiate your own answer first. It takes ten seconds and it is the
product rule.
""")

code(r"""
q9 = ...         # an antiderivative of (x^2 - 5)e^x

verify_antiderivative('7', q9, (x**2 - 5)*exp(x))
""")

md(r"""
## Task 8 🟡 — parts with nothing to pair

*November 2025 TZ1 Paper 2 Q11(a), 4 marks · calculator*

Use integration by parts to find $\displaystyle\int\arccos x\,\mathrm{d}x$.

There is no second factor. Write one.
""")

code(r"""
q10 = ...        # an antiderivative of arccos(x)

verify_antiderivative('8', q10, acos(x), domain=(-0.9, 0.9))
""")

md(r"""
## Task 9 🔴 — parts, an improper integral, and a pattern

*May 2023 TZ1 Paper 3 Q1(b)(c)(d)(e), 10 marks · calculator*

This question investigates the family $f_n(x)=x^n\mathrm{e}^{-x}$ for $x\ge0$.

The paper's part (b) shows that the area under $f_1$ up to $x=b$ is
$\dfrac{\mathrm{e}^b-b-1}{\mathrm{e}^b}$ — printed, so hand in the step
before it instead.

**(a)** Find an antiderivative of $x\mathrm{e}^{-x}$.

The total area is written $A_n=\displaystyle\int_0^{\infty}f_n(x)\,\mathrm{d}x$.

**(b)** Write down $A_1$.

**(c)** Use your calculator, with a sensible upper limit in place of $\infty$,
to find $A_4$ and $A_5$.

**(d)** You are given $A_2=2$ and $A_3=6$. Suggest an expression for $A_n$.

For (c) and (d), `verify_integral` also faces an infinite limit, and it does
what you do: pushes the upper limit out — 10, 20, 40, ... — until two
successive values agree.
""")

code(r"""
q11a = ...        # an antiderivative of x*e^(-x)
q11one = ...      # A_1
q11four = ...    # A_4
q11five = ...    # A_5
q11n = ...        # A_n, as an expression in n

verify_antiderivative('9a', q11a, x*exp(-x))
verify_integral('9b', q11one, x*exp(-x), 0, oo)
verify_integral('9c', q11four, x**4*exp(-x), 0, oo)
verify_integral('9d', q11five, x**5*exp(-x), 0, oo)
verify_integral('9e', q11n, x**n*exp(-x), 0, oo, params={n: (2, 3, 4, 5, 6)})
""")

md(r"""
## Theory 4. Partial fractions, and the two traps in them

A proper rational function splits into pieces the table knows:

$$\frac{5x-4}{(x-1)(x+2)}=\frac{A}{x-1}+\frac{B}{x+2},\qquad
\frac{1}{(x-3)^2(x+4)}=\frac{A}{x-3}+\frac{B}{(x-3)^2}+\frac{D}{x+4}.$$

**Trap one: a repeated factor needs two fractions, not one.** $(x+1)^2$ gets
both $\dfrac{A}{x+1}$ and $\dfrac{B}{(x+1)^2}$, and they integrate to
completely different things —

$$\int\frac{\mathrm{d}x}{x-3}=\ln|x-3|,\qquad
\int\frac{\mathrm{d}x}{(x-3)^2}=-\frac{1}{x-3}.$$

A logarithm where a reciprocal belongs is the most expensive single error in
rung 4.

**Trap two: the inside function still brings a factor.**

$$\int\frac{\mathrm{d}x}{3x-2}=\frac{1}{3}\ln|3x-2|+c.$$

That $\tfrac12$ is the substitution rule again, and it is dropped constantly.

**Where the constant hides.** Mark schemes in this topic often print the
constant already dressed for the next step. A split like

$$\int\frac{\mathrm{d}y}{y^2-9}=\frac16\ln\left|\frac{y-3}{y+3}\right|+\frac16\ln A$$

looks as though something extra has appeared, but $\tfrac16\ln A$ *is* the
constant of integration — written that way so that exponentiating both sides
comes out clean, with $A$ multiplying instead of $c$ adding. Expect it, and do
not try to reconcile it with your own $+c$: the check differentiates, and
anything constant vanishes whatever costume it wears.
""")

md(r"""
## Task 10 🟡 — split it, then integrate it

*November 2021 Paper 2 Q10(e), 7 marks · calculator*

Consider $f(x)=\dfrac{x^2-x-12}{2x-15}$, so that
$\dfrac{1}{f(x)}=\dfrac{2x-15}{(x+3)(x-4)}$.

**(a)** Express $\dfrac{1}{f(x)}$ in partial fractions.

**(b)** Hence find the exact value of $\displaystyle\int_0^3\frac{1}{f(x)}\,\mathrm{d}x$,
as a single logarithm.
""")

code(r"""
q12 = ...         # the partial fractions, as a sum
q12v = ...       # the exact value between 0 and 3

# check_apart wants each term to be a genuine partial fraction: no x upstairs,
# and a denominator that does not factorise further. Equality alone is not
# enough, because the original fraction equals itself.
check_apart('10a', q12, (2*x - 15)/((x + 3)*(x - 4)))
verify_integral('10b', q12v, (2*x - 15)/((x + 3)*(x - 4)), 0, 3)
""")

md(r"""
## Task 11 🔴 — substitution first, then partial fractions

*May 2021 TZ2 Paper 1 Q9, 7 marks · no calculator*

By using the substitution $u=\sin x$, find
$$\int\frac{\sin x\cos x}{\sin^2 x-\sin x-2}\,\mathrm{d}x.$$

Three moves, and each one is a mark: change the variable, split the fraction,
integrate the pieces.
""")

code(r"""
q13u = ...       # the integrand in terms of u
q13p = ...       # that integrand split into partial fractions
q13 = ...         # the antiderivative, back in terms of x

verify_transformed('11a', q13u, sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2), sin(x))
check_apart('11b', q13p, u/(u**2 - u - 2), var=u)
verify_antiderivative('11c', q13, sin(x)*cos(x)/(sin(x)**2 - sin(x) - 2),
                      domain=(0.2, 1.2))
""")

md(r"""
## Task 12 🟢 — the constant in costume

*May 2025 TZ2 Paper 3 Q1(e), 5 marks · calculator*

Using partial fractions, show that
$$\int\frac{\mathrm{d}v}{1-v^2}=\frac12\ln\left|\frac{1+v}{1-v}\right|+\frac12\ln A,$$
where $A$ is a positive constant.

Printed again — so write it out yourself and let the check confirm that the
$\tfrac12\ln A$ really is free. Then try replacing it by `+ C` and by `- 4`:
all three are the same answer.
""")

code(r"""
q14 = ...        # the antiderivative, with the constant dressed however you like

verify_antiderivative('12', q14, 1/(1 - v**2), var=v, domain=(0.05, 0.9))
""")

md(r"""
## Theory 5. When the quotient is $f'/f$

$$\int\frac{f'(x)}{f(x)}\,\mathrm{d}x=\ln|f(x)|+c .$$

This is substitution with $u=f(x)$, but it is worth its own rung because the
recognition is the whole difficulty: the numerator is rarely handed to you as
a derivative, and getting it there is algebra, not calculus.

**The May 2024 Paper 3 investigation** is the case in the archive. It arrives
at
$$\frac{f'(x)}{f(x)}=\frac{g'(x)}{g'(x)-g(x)}$$
and then asks you to integrate both sides. Two things happen at once:

**The left side becomes $\ln|f(x)|$**, by the rule above.

**The constant changes shape.** Exponentiating $\ln|f|=\text{(something)}+c$
gives $f=\mathrm{e}^{c}\,\mathrm{e}^{\text{(something)}}$, and $\mathrm{e}^c$
is renamed $A$. A constant that was *added* is now *multiplying*. Writing
"$+c$" after exponentiating is a real, marked error.

Then the right side has to be simplified before it can be integrated at all:

$$g=x^2:\quad \frac{g'}{g'-g}=\frac{2x}{2x-x^2}=\frac{2}{2-x},$$

$$g=\mathrm{e}^{3x}:\quad \frac{g'}{g'-g}=\frac{3\mathrm{e}^{3x}}{3\mathrm{e}^{3x}-\mathrm{e}^{3x}}
=\frac32 .$$

Both are then easy — the second is a constant, and its integral is a straight
line. Getting to that point is the work; integrating what is left is not.
""")

md(r"""
## Task 13 🔴 — two functions out of one formula

*May 2024 TZ2 Paper 3 Q1(d)(e), 12 marks · calculator*

Part (c) of that paper establishes
$$f(x)=A\exp\left(\int\frac{g'(x)}{g'(x)-g(x)}\,\mathrm{d}x\right).$$
Take $A=1$ throughout.

**(a)** With $g(x)=x\mathrm{e}^x$, find $f(x)$.

**(b)** With $g(x)=\sin x+\cos x$ on $0<x<\pi$, find $f(x)$, giving your
answer in the form $f(x)=\dfrac{\mathrm{e}^x}{h(x)}$. Hand in $h(x)$.

Both are checked the same way, and it is worth seeing why: if
$f=\exp(\int\!\ldots)$ then $\ln f$ is an antiderivative of the integrand. So
the check takes the logarithm of your $f$ and differentiates *that*. With
$A=1$ the constant is pinned too, so `through` is used in (a).
""")

code(r"""
q15d = ...       # f(x) for g(x) = x*e^x
q15e = ...       # h(x), where f(x) = e^x / h(x), for g(x) = sin x + cos x

# (a) g' = (x+1)e^x and g' - g = e^x, so the integrand is x + 1.
verify_antiderivative('13a', log(q15d) if not blank(q15d) else ...,
                      x + 1, through=(0, 0))
# (b) f = e^x/h, so log f = x - log h, and the integrand is 1/2 - cot(x)/2.
verify_antiderivative('13b', x - log(q15e) if not blank(q15e) else ...,
                      Rational(1, 2) - cot(x)/2, domain=(0.2, 2.9))
""")

# ================================================================ Part III
md(r"""
---
# Part III — there is no antiderivative in closed form

## Theory 6. A reduction formula is a recursion, not an answer

$\int\cos^n x\,\mathrm{d}x$ has no single closed form covering every $n$.
What it has is a way down. Write $\cos^n x=\cos^{n-1}x\cdot\cos x$ and
integrate by parts with $u=\cos^{n-1}x$, $\mathrm{d}v=\cos x\,\mathrm{d}x$:

$$\int\cos^n x\,\mathrm{d}x=\cos^{n-1}x\sin x+(n-1)\int\cos^{n-2}x\,\mathrm{d}x
-(n-1)\int\cos^n x\,\mathrm{d}x .$$

The last term is the integral you started with. **Collect it**, and the formula
becomes usable:

$$\int\cos^n x\,\mathrm{d}x=\frac{1}{n}\cos^{n-1}x\sin x
+\frac{n-1}{n}\int\cos^{n-2}x\,\mathrm{d}x .$$

Two remarks that are worth a mark each.

**The $(n-1)$ comes from the chain rule**, differentiating $\cos^{n-1}x$, and
it is dropped often enough that the mark scheme awards it separately.

**The recursion has to bottom out.** $n=4\to n=2\to n=0$, and
$\int\cos^0x\,\mathrm{d}x=x$. Stopping at $n=2$ and guessing is where the
last mark goes.

**How the check works.** A reduction formula is an identity between integrals,
so `verify_reduction` treats it as one: for each of several $n$ it evaluates
$\int_a^b$ of both sides numerically — the terms containing $J(m)$ by
quadrature, the free term by substituting the limits — and compares. It never
finds an antiderivative, which is the point: a formula it could derive would
be a formula it could hand you.
""")

md(r"""
## Task 14 🔴 — build the same formula for sine

*May 2025 TZ1 Paper 1 Q12(a)(b)(c), 10 marks · no calculator*

The paper builds and uses the cosine formula above. Both of its first two
parts are printed, so build the sine one instead, then use the printed cosine
one for the part that is actually asked.

**(a)** Show that, for $n>1$,
$$\int\sin^n x\,\mathrm{d}x=\square+\square\int\sin^{n-2}x\,\mathrm{d}x .$$
Write the right-hand side, using `J(n-2)` to stand for
$\int\sin^{n-2}x\,\mathrm{d}x$.

**(b)** Find an expression for $\displaystyle\int\cos^4x\,\mathrm{d}x$ in the
form $p\cos^3x\sin x+q\cos x\sin x+rx+c$ with $p,q,r\in\mathbb{Q}^+$.
""")

code(r"""
q16 = ...         # the right-hand side for sin^n, written with J(n-2)
q16c = ...       # an antiderivative of cos^4(x)

verify_reduction('14a', q16, sin(x)**n, n, J)
verify_antiderivative('14b', q16c, cos(x)**4)
""")

md(r"""
## Theory 7. Integrating a series

Some integrands have no elementary antiderivative at all
($\mathrm{e}^{\cos 2x}$), and some have one you are not allowed to write down
yet ($\arctan x$, in the question that is *deriving* it). In both cases the
move is the same: replace the function by the first few terms of its Maclaurin
series and integrate those.

$$\frac{1}{1-x}=1+x+x^2+x^3+\ldots
\ \longrightarrow\ \int\frac{\mathrm{d}x}{1-x}
= x+\frac{x^2}{2}+\frac{x^3}{3}+\frac{x^4}{4}+c$$

Three things to be careful about, and all three are marked.

**Integrate the series, do not hand in the series.** $1+x+x^2+x^3$ is the
*integrand*. A surprising number of scripts stop there.

**Divide by the new index.** $x^3\to x^4/4$, not $x^4$.

**Stop where you were told to stop.** "Up to and including the term in $x^7$"
means $x^9$ is wrong, not extra credit. The check enforces this.

And the reason any of it is useful: the left-hand side is often a function you
know. Here $\int\frac{\mathrm{d}x}{1-x}=-\ln(1-x)$, so the series just
integrated *is* a series for $-\ln(1-x)$, and putting $x=\tfrac12$ into it
gives a numerical approximation of $\ln 2$. That is the shape of every
question on this rung: integrate a series, recognise what it converges to,
substitute a number, get a decimal for a constant you could not otherwise
reach by hand.
""")

md(r"""
## Task 15 🟡 — two series, and $\pi$ at the end of them

*November 2025 TZ1 Paper 1 Q10(a)(ii)(b)(ii)(c), 7 marks · no calculator*

**(a)** Given that $\dfrac{1}{1+x^2}=1-x^2+x^4-x^6+\ldots$ for $|x|<1$, find
an approximation for $\displaystyle\int\frac{\mathrm{d}x}{1+x^2}$ up to and
including the term in $x^7$.

**(b)** Given that $\dfrac{1}{\sqrt{1-x^2}}=1+\tfrac12x^2+\tfrac38x^4+\ldots$,
find a polynomial expression for $\displaystyle\int\frac{\mathrm{d}x}{\sqrt{1-x^2}}$
up to and including the term in $x^5$.

**(c)** The expression $\dfrac{25}{48}+\dfrac{k}{1280}$, with
$k\in\mathbb{Z}^+$, approximates $\arcsin\tfrac12$. Use (b) to find $k$.
""")

code(r"""
q17a = ...       # the integral of 1/(1+x^2), up to x^7
q17b = ...       # the integral of 1/sqrt(1-x^2), up to x^5
q17k = ...       # k

verify_termwise('15a', q17a, 1/(1 + x**2), 8)
verify_termwise('15b', q17b, 1/sqrt(1 - x**2), 6)
# (c) is checked against your own (b): the approximation is that polynomial
# evaluated between 0 and 1/2, so the constant drops out on its own.
q17c = ... if blank(q17b, q17k) else Rational(25, 48) + q17k/S(1280)
q17w = 0 if blank(q17b) else q17b.subs(x, Rational(1, 2)) - q17b.subs(x, 0)
verify_exact('15c', q17c, q17w)
""")

md(r"""
## Task 16 🟡 — two terms are enough

*November 2023 TZ1 Paper 1 Q11(d)(iii)(e), 3 marks · no calculator*

For $f(x)=\mathrm{e}^{\cos 2x}$, the paper's part (d) builds the Maclaurin
series and part (e) uses its first two non-zero terms to show that
$\int_0^{1/10}f(x)\,\mathrm{d}x\approx\frac{149\mathrm{e}}{1500}$ — printed,
as usual.

**(a)** Write the Maclaurin series of $\mathrm{e}^{\cos 2x}$ up to and
including the term in $x^2$.

**(b)** Use those two terms to approximate $\displaystyle\int_0^{1/5}
\mathrm{e}^{\cos 2x}\,\mathrm{d}x$. Give an exact answer.

Part (b) is checked against the integral of the **approximation**, not of the
real function — because that is what was asked. The true value is 0.1963; the
approximation is 0.1985, and the gap is what the next term is for.
""")

code(r"""
q18s = ...       # the Maclaurin series of e^(cos 2x) up to x^2
q18 = ...         # the approximation to the integral from 0 to 1/5

verify_maclaurin('16a', q18s, exp(cos(2*x)), terms=2)
verify_integral('16b', q18, q18s, 0, Rational(1, 5))
""")

# ================================================================= Part IV
md(r"""
---
# Part IV — the antiderivative is not the question

## Theory 8. Reading the equation backwards

Sometimes the value of an integral is what you are *given*. Then the
antiderivative is a step, and the unknown is somewhere else — a limit, a
constant inside the integrand, a probability that has to come to 1.

$$\int_0^c\mathrm{e}^{2x}\,\mathrm{d}x=4
\quad\Longrightarrow\quad
\frac{\mathrm{e}^{2c}-1}{2}=4
\quad\Longrightarrow\quad
\mathrm{e}^{2c}=9
\quad\Longrightarrow\quad c=\ln 3 .$$

Note how little of that was integration: one line, and then three lines of
ordinary algebra. That ratio is typical of the whole rung.

Two habits earn marks here.

**Finish the algebra.** $\mathrm{e}^{2c}=9$ is not an answer to "find $c$",
and neither is $2c=\ln 9$. Nor is a $\pm$ pair when the diagram shows which
sign is wanted.

**Watch the accuracy the question asks for.** *Correct to six significant
figures* means six of them: an answer rounded to three scores nothing, however
right it is. This is the one place in the topic where the calculator does real
work — the equation you end up with usually has no closed-form root, so the
GDC solves it and the only question left is how many digits you copy down.

**And sometimes there is no antiderivative to find at all.** If $f$ is odd,
$\int_{-a}^{a}f=0$ and $\int_{-a}^{0}f=-\int_0^{a}f$, whatever $f$ is — even
when all you have is a picture of it.
""")

md(r"""
## Task 17 🟡 — three integrals read backwards

*May 2023 TZ2 Paper 1 Q4, 6 marks · no calculator ·
November 2025 TZ1 Paper 2 Q11(b), 6 marks · calculator ·
May 2024 TZ1 Paper 1 Q9(c), 2 marks · no calculator*

**(a)** The region bounded by $y=\dfrac{x}{x^2+2}$, the $x$-axis and the line
$x=c$ (with $c>0$) has area $\ln 3$. Find $c$.

**(b)** The random variable $X$ has probability density function
$f(x)=3x\arccos(x^2)$ for $0\le x\le k$, and zero elsewhere. Find $k$, correct
to six significant figures.

**(c)** $f$ is an odd function and $\displaystyle\int_0^4 f(|x|)\,\mathrm{d}x=1.6$.
Write down the value of
(i) $\displaystyle\int_{-4}^{0}f(x)\,\mathrm{d}x$;
(ii) $\displaystyle\int_{-4}^{4}\bigl(f(|x|)+f(x)\bigr)\mathrm{d}x$.

In (a) and (b) your answer goes in as a **limit of integration**, and the
check integrates up to it. In (c) there is no integrand to hand the check —
the function only exists as a graph — so those two are compared as numbers.
""")

code(r"""
q19 = ...         # c
q20k = ...       # k, to six significant figures
q21a = ...       # (c)(i)
q21b = ...       # (c)(ii)

verify_integral('17a', log(3), x/(x**2 + 2), 0, q19)
verify_integral('17b', 1, 3*x*acos(x**2), 0, q20k, tol=1e-6)
check_num('17c', q21a, 2, 'c144de0e3592')
check_num('17d', q21b, 2, '3135d2d71bff')
""")

# ============================================================ распознавание
md(r"""
---
## Trainer: name the technique in five seconds

Twelve integrals from the archive, none of them worked out. Say which
technique each one is, in one word, **before** doing any of them. Choosing the
technique is most of this topic; the rest is bookkeeping.

| code | technique |
| --- | --- |
| `table` | already a sum of standard forms, or $f'$ plus a point |
| `usub` | a function sits beside its own derivative |
| `parts` | a product, and one factor simplifies when differentiated |
| `apart` | a proper rational function with a factorisable denominator |
| `logint` | the numerator is the denominator differentiated |
| `reduce` | the exponent is a letter |
| `series` | replace the function by its first few terms |
| `condition` | the value of the integral is given; something else is asked |

1. $\displaystyle\int t\,\mathrm{e}^{-3t}\,\mathrm{d}t$
2. $\displaystyle\int\frac{\mathrm{d}x}{(x+1)^2(2x+1)}$
3. $g'(x)=3x^2+5\mathrm{e}^x$ and $g(0)=4$; find $g$.
4. $\displaystyle\int_0^{1/\sqrt3}\left(x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}\right)\mathrm{d}x$
   to six decimal places
5. $\displaystyle\int\frac{6x}{1+x^2}\,\mathrm{d}x$, given the graph passes through $(1,5)$
6. Integrate both sides of $\dfrac{f'}{f}=\dfrac{g'}{g'-g}$.
7. Show that $\displaystyle\int\cos^n x\,\mathrm{d}x=\frac{1}{n}\cos^{n-1}x\sin x
   +\frac{n-1}{n}\int\cos^{n-2}x\,\mathrm{d}x$.
8. The area under $y=\dfrac{x}{x^2+2}$ from $0$ to $c$ is $\ln 3$. Find $c$.
9. $\displaystyle\int\arccos x\,\mathrm{d}x$
10. $\displaystyle\int_0^{\pi/3}\sec^n x\tan x\,\mathrm{d}x$
11. $\displaystyle\int_{-4}^{4}f(x)\,\mathrm{d}x$, where $f$ is odd
12. $\displaystyle\int_0^3\frac{2x-15}{(x+3)(x-4)}\,\mathrm{d}x$
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
# On the timer — 6 minutes

*November 2023 TZ1 Paper 1 Q8, adapted · no calculator*

Find the exact value of $\displaystyle\int_1^{\mathrm{e}}x(\ln x)^2\,\mathrm{d}x$.

Six minutes is what nine marks are worth at AA HL pace. Two applications of
parts, then substitute two limits. Write the antiderivative down before you
touch the limits — the commonest way to lose this is to start substituting
into something half-finished.
""")

code(r"""
qt = ...         # the exact value

verify_integral('timer', qt, x*log(x)**2, 1, E)
""")

md(r"""
---
## What to take away

**Differentiate your answer.** Every mark in this practicum can be checked by
you, alone, in ten seconds, with no answer key. There is no other topic in AA
HL where that is true, and there is no excuse for handing in an integral you
have not differentiated.

**The choice of technique is the exam.** By the time you have decided between
parts and substitution, the question is over; the rest is algebra you have
done a hundred times. That is why the trainer above is here and why it is
worth redoing until it takes five seconds a line.

**The constant is not decoration.** It is free when the question gives you no
point and pinned when it does, and it changes shape when you exponentiate.
Three separate marks in this archive turn on it.

---
### Where the marks went, across the topic

| technique | marks | share |
| --- | --- | --- |
| Integration by parts | 46 | 29% |
| Partial fractions | 23 | 15% |
| Table, plus a constant | 18 | 11% |
| Substitution | 17 | 11% |
| Integrate the series | 15 | 10% |
| The quotient is $f'/f$ | 14 | 9% |
| The integral is a condition | 14 | 9% |
| Reduction formula | 10 | 6% |

Three things stand out.

**Parts is nearly a third of the topic on its own**, and it is the only
technique spread evenly across all three papers: 18 marks on Paper 1, 14 on
Paper 2, 14 on Paper 3. If you drill one thing, drill parts.

**86 of the 157 marks are Paper 1.** After E3 (27% Paper 1) and E4 (23%), this
is a change of climate. The techniques of integration are the part of calculus
IB still tests by hand, and the 45% "calculator" figure is the most misleading
one in the series so far.

**Thirty-five marks are Paper 3**, and all of them are inside investigations
about something else — the family $x^n\mathrm{e}^{-x}$, functions satisfying
$(fg)'=f'g'$, the Maclaurin series of $\arctan$. Integration is never the
subject of a Paper 3; it is the step in the middle that stops you if you
cannot do it.
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
