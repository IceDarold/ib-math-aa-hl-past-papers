"""Собирает архивный ноутбук E1: весь корпус темы, по приёмам, подряд.

Четвёртый ноутбук в формате, опробованном на B4, C3 и B5. Практикум E1
учит — лестница, теория, уровни, тренажёр. Этот не учит, он даёт набивать
руку: вопрос, ячейка для ответа с мгновенной проверкой, разбор в конце.

Внутри — вся тема calculus.limits из архива AA HL, сессии May 2021 —
November 2025: 24 вопроса и 73 балла, разложенные по девяти приёмам
карточки calculus-limits.yaml.

Почему 73, а не 81. Корпус числит за темой 22 блока (81 балл), и два из них
дублируют другие. Ноябрьский Paper 3 2023 года — одна бумага, лежащая в
Common, но корпус держит её двумя зональными копиями, и обе страницы
совпадают побайтово. А вопрос про sin^2(kx)/x^2 в ноябре 2023 поставлен в
TZ1 и TZ2 слово в слово: бумаги разные, вопрос один. Каждый входит в архив
по разу; оба записаны в corpus_issues карточки.

Пропорция хешей здесь самая низкая в серии: два из двадцати трёх. Причина
в самой теме. Предел проверяется приближением к нему — verify_limit берёт
выражение из условия, подходит к точке лестницей и смотрит, туда ли садятся
значения, — и эталона при этом не хранит вовсе. Хеш остаётся только там, где
ответ не предел, а постоянная, подобранная под него: k = 4 и k = 9.

Один вопрос кода не имеет вовсе: 9.1 просит назвать словами, почему предел
скорости не имеет смысла для бегуньи на дистанции в 200 метров.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_e1.py прогоняет весь ноутбук
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

R = sp.Rational
x, t = sp.symbols('x t')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e1-limits.ipynb')


def dn(value, sf=3):
    return digest(sig(value, sf))


# --- два хеша: оба на постоянную, подобранную под предел ---
D_62 = dn(4, 1)          # k в sin^2(kx)/x^2 -> 16
D_63 = dn(9, 1)          # k плотности k t e^{-3t}
# Два ряда Маклорена прячутся: вопрос просит именно их, и показывать ответ
# в тексте проверки было бы то же самое, что напечатать его в условии.
import kit
n = sp.Symbol('n')
D_52A = digest(kit._series_canon(1 + x - x**3 / 3 - x**4 / 6, x, 6))
D_53A = digest(kit._series_canon(1 - n * x**2 / 2, x, 6))

ANSWERS = {
    'q1_1': '4',

    'q2_1': 'Rational(3, 2)',
    'q2_2': 'Rational(814, 100)',

    'q3_1': 'Rational(2, 3)',
    'q3_2': '1',
    'q3_3': '0',

    'q4_1': '-3',
    'q4_2': '2',
    'q4_3': '-Rational(1, 4)',

    'q5_1': '1',
    'q5_2a': '1 + x - x**3/3 - x**4/6',
    'q5_2b': '-Rational(1, 3)',
    'q5_3a': '1 - n*x**2/2',
    'q5_3b': '-n/2',

    'q6_1': 'pi/4',
    'q6_2': '4',
    'q6_3': '9',

    'q7_1': 'c/(1 - m)',
    'q7_2a': '(cos(1/n) + sin(1/n))/sqrt(2)',
    'q7_2b': 'pi/4',
    'q7_3': '-1/F',

    'q8_1': "'0/0'",
    'q8_2': 'n*(n + 1)/2',
    'q8_3': '1',

    'q9_2': '0',
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
# E1 archive: limits, indeterminate forms, l'Hôpital's rule

**Every past-paper question on this topic, grouped by technique.** Not a
practicum — a drill. There is no theory here and no ladder to climb: the
theory is in *Practicum E1*, and this notebook is what you open afterwards,
when the only thing left is to do them all until the moves are automatic.

**What is inside.** The whole of `calculus.limits`, sessions May 2021 —
November 2025: **24 questions, 73 marks**, in nine sections, one section
per technique.

The corpus records 22 blocks and 81 marks. Two of them are duplicates. The
November 2023 Paper 3 is a single paper filed under Common, but the corpus
keeps a zonal copy for each of TZ1 and TZ2 and the two pages are identical
byte for byte. And the November 2023 question on $\sin^2(kx)/x^2$ was set
in TZ1 and in TZ2 word for word — two papers, one question. Each appears
here once. Nothing else is left out and nothing is added.

**Eleven questions are Paper 1, five are Paper 2, eight are Paper 3.** But
the usual split by paper does not apply to this topic: the answers are
$\frac23$, $-3$, $-\frac14$, $\frac\pi4$, $-\frac n2$, $\frac12 n(n+1)$
almost everywhere, calculator or not. Only two answers in the whole topic
are numbers you would want a calculator for, and both are values of a
constant rather than limits.

**How to work.** Read the question, answer in the cell below it, run the
cell. Most of these checks do not know the answer. `verify_limit` takes
the expression from the question, walks in towards the point along
$10^{-1},10^{-2},\dots,10^{-8}$ from both sides, and asks whether the
number you named is where the values are settling. There is no stored
constant for it to be wrong about — so an answer reached by a wrong route
still has to be true, and an answer with $x$ still in it is refused on
sight.

Two checks do compare a hash, and they are the same case twice: the answer
is not a limit but a constant chosen to make one come out right — $k=4$ so
that $\lim\frac{\sin^2 kx}{x^2}=16$, and $k=9$ so that a density integrates
to $1$.

One question has no cell at all: 9.1 asks, in words, why a limiting speed
is meaningless for a runner in a $200$ m race.

Leave a cell blank and it prints ⬜ and moves on, which means you can run
the whole notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before — and read the markscheme note in it,
because that is where the marks actually are.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Substitute, and cancel what stops you | 1 | part of 3 |
| 2 | The highest power at infinity | 2 | part of 6 |
| 3 | l'Hôpital's rule, one round | 3 | 8 |
| 4 | l'Hôpital's rule, more than one | 3 | 18 |
| 5 | Maclaurin instead | 3 | 9 |
| 6 | The constant that makes a limit exist | 3 | 10 |
| 7 | The limit taken in a parameter | 3 | 9 |
| 8 | The rule with a letter inside the expression | 3 | 9 |
| 9 | What the limit means | 2 | part of 5 |

Sections 1–2 need no calculus at all. Sections 3–5 are the rule and the
alternative to it, and they carry $35$ of the $73$ marks. Section 6 works
backwards from a limit to a constant; sections 7 and 8 leave a letter in
the answer. Section 9 is four marks for two sentences.

**One habit runs through all of it.** Write $\lim_{x\to a}$ on every line.
May 2021 caps a perfect solution at four marks out of five without it;
May 2024 withholds the final **A1**; November 2022 refuses the mark for the
indeterminate form outright.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Rational, oo, pi

language('en')                 # this notebook is in English, and so are the checks

a, b, c, m, n = symbols('a b c m n')
alpha, F = symbols('alpha F')
# F stands for f(x, y) in section 7: a gradient that does not move while
# alpha does. Naming it as a letter is what lets a check substitute values.

print('ready; sympy', sp.__version__)
print('an exact limit:      ', Rational(2, 3))
print('a limit in terms of n:', -n/2)
print('an infinite limit:   ', oo)
print("a form, as a string: ", '0/0')
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. Substitute, and cancel what stops you

Substituting is the first move, always. When it gives a number, that is the
limit. When it gives $\frac00$ because the top and the bottom share a
factor, cancel the factor and substitute again.
""")

md(r"""
### 1.1 — *May 2024 TZ1 Paper 1 Q11(f)(i), part of 3 marks*

Consider the polynomials $P(x)=3x^3+5x^2+x-1$ and $Q(x)=(x+1)(2x+1)$, and
the function
$$f(x)=\frac{P(x)}{(x+1)Q(x)},\qquad x\ne-1,\ x\ne-\tfrac12 .$$

Find $\displaystyle\lim_{x\to-1}f(x)$.
""")

code(r"""
FX = (3*x**3 + 5*x**2 + x - 1) / ((x + 1) * (x + 1) * (2*x + 1))

q1_1 = ...

verify_limit('1.1', q1_1, FX, point=-1)
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. The highest power at infinity

Divide the top and the bottom by the highest power of the variable that
appears, then use $\frac{1}{x^k}\to 0$. A root counts as a power:
$\sqrt{t^2+0.2}$ behaves like $t$.
""")

md(r"""
### 2.1 — *May 2024 TZ1 Paper 1 Q11(f)(ii), part of 3 marks*

With $f$ as in 1.1, find $\displaystyle\lim_{x\to\infty}f(x)$.
""")

code(r"""
q2_1 = ...

verify_limit('2.1', q2_1, FX, point=oo)
""")

md(r"""
### 2.2 — *May 2025 TZ3 Paper 2 Q10(c)(i), part of 3 marks*

Two athletes compete in a $200$ metres race along a straight track.
Fiona's velocity, in $\mathrm{m\,s^{-1}}$, during the race can be modelled
by
$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}},\qquad t\ge 0 ,$$
where $t$ is measured in seconds from when the race starts.

Write down the limit of $v(t)$ as $t$ approaches infinity.
""")

code(r"""
VT = Rational(814, 100)*t / sqrt(t**2 + Rational(2, 10))

q2_2 = ...

verify_limit('2.2', q2_2, VT, var=t, point=oo)
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. l'Hôpital's rule, one round

If substituting gives $\frac00$ or $\frac{\infty}{\infty}$, differentiate
the numerator and the denominator **separately** and substitute again. The
rule reads quotients only: a product $\infty\cdot 0$ has to be turned into
one first.
""")

md(r"""
### 3.1 — *May 2021 TZ1 Paper 1 Q8, 5 marks*

Use l'Hôpital's rule to find
$\displaystyle\lim_{x\to 0}\left(\frac{\arctan 2x}{\tan 3x}\right)$.
""")

code(r"""
q3_1 = ...

verify_limit('3.1', q3_1, atan(2*x)/tan(3*x))
""")

md(r"""
### 3.2 — *May 2023 TZ1 Paper 3 Q1(c)(i), 2 marks*

The area of the region bounded by $y=xe^{-x}$, the $x$-axis and the line
$x=b$, where $b>0$, is $\dfrac{e^b-b-1}{e^b}$.

Use l'Hôpital's rule to find $\displaystyle\lim_{b\to\infty}\frac{e^b-b-1}{e^b}$.
You may assume that the condition for applying l'Hôpital's rule has been met.
""")

code(r"""
AREA = (exp(b) - b - 1)/exp(b)

q3_2 = ...

verify_limit('3.2', q3_2, AREA, var=b, point=oo)
""")

md(r"""
### 3.3 — *May 2025 TZ2 Paper 2 Q11(c)(i), part of 5 marks*

Use l'Hôpital's rule to find $\displaystyle\lim_{x\to\infty}(3x+1)e^{-3x}$.
""")

code(r"""
q3_3 = ...

verify_limit('3.3', q3_3, (3*x + 1)*exp(-3*x), point=oo)
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. l'Hôpital's rule, more than one round

After differentiating, substitute again. Still $\frac00$ — apply the rule
again. Not indeterminate any more — stop, and read the answer. A round too
many gives the wrong number and costs the mark.
""")

md(r"""
### 4.1 — *May 2024 TZ2 Paper 1 Q8, 6 marks*

Use l'Hôpital's rule to find
$\displaystyle\lim_{x\to 0}\frac{\sec^4x-\cos^2x}{x^4-x^2}$.
""")

code(r"""
q4_1 = ...

verify_limit('4.1', q4_1, (sec(x)**4 - cos(x)**2)/(x**4 - x**2))
""")

md(r"""
### 4.2 — *May 2025 TZ3 Paper 1 Q9, 6 marks*

Determine the value of
$\displaystyle\lim_{x\to 0}\left(\frac{x\sin x}{1-\cos x}\right)$.
""")

code(r"""
q4_2 = ...

verify_limit('4.2', q4_2, x*sin(x)/(1 - cos(x)))
""")

md(r"""
### 4.3 — *May 2022 TZ2 Paper 2 Q7(b), 6 marks*

Consider $\displaystyle\lim_{x\to 0}\frac{\arctan(\cos x)-k}{x^2}$, where
$k\in\mathbb{R}$, and take $k=\dfrac{\pi}{4}$.

Using l'Hôpital's rule, show algebraically that the value of the limit is
$-\dfrac14$.
""")

code(r"""
q4_3 = ...

verify_limit('4.3', q4_3, (atan(cos(x)) - pi/4)/x**2)
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. Maclaurin instead

Near zero a series *is* the function. Replace each factor by its expansion
and read off the lowest power that survives. Where the denominator is $x^3$
or $x^4$ this is one line against three rounds of differentiation.
""")

md(r"""
### 5.1 — *November 2021 Paper 1 Q11(c), 4 marks*

Let $f(x)=x^2e^x$. Determine the value of
$$\lim_{x\to 0}\left[\frac{\bigl(x^2e^x-x^2\bigr)^3}{x^9}\right].$$
""")

code(r"""
q5_1 = ...

verify_limit('5.1', q5_1, (x**2*exp(x) - x**2)**3 / x**9)
""")

md(r"""
### 5.2 — *May 2022 TZ1 Paper 1 Q12(d) and Q12(e), 5 and 3 marks*

The function $g$ is defined by $g(x)=e^x\cos x$, where $x\in\mathbb{R}$.

**(a)** Find the Maclaurin series for $g(x)$ up to and including the $x^4$
term.

**(b)** Hence, or otherwise, determine the value of
$\displaystyle\lim_{x\to 0}\frac{e^x\cos x-1-x}{x^3}$.
""")

code(r"""
q5_2a = ...
q5_2b = ...

check_series('5.2a', q5_2a, D_52A)
verify_limit('5.2b', q5_2b, (exp(x)*cos(x) - 1 - x)/x**3)
""".replace('D_52A', repr(D_52A)))

md(r"""
### 5.3 — *May 2025 TZ1 Paper 1 Q12(e), 5 marks*

Consider the family of functions $f_n(x)=\cos^n x$, where $x\in\mathbb{R}$
and $n\in\mathbb{N}$.

**(a)** Find the Maclaurin series of $f_n(x)$ up to the term in $x^2$.

**(b)** Hence or otherwise, find
$\displaystyle\lim_{x\to 0}\frac{f_n(x)-1}{x^2}$ in terms of $n$.
""")

code(r"""
q5_3a = ...
q5_3b = ...

check_series('5.3a', q5_3a, D_53A)
verify_limit('5.3b', q5_3b, (cos(x)**n - 1)/x**2, params={n: (1, 2, 5, 9)})
""".replace('D_53A', repr(D_53A)))

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. The constant that makes a limit exist

The letter is the answer. If the denominator goes to zero and the limit is
finite, the numerator must go to zero too — and that equation gives the
letter. Or the limit is stated and the letter is read out of it.
""")

md(r"""
### 6.1 — *May 2022 TZ2 Paper 2 Q7(a), 2 marks*

Consider $\displaystyle\lim_{x\to 0}\frac{\arctan(\cos x)-k}{x^2}$, where
$k\in\mathbb{R}$.

Show that a finite limit only exists for $k=\dfrac{\pi}{4}$, and state the
value of $k$.
""")

code(r"""
q6_1 = ...

verify_exact('6.1', q6_1, pi/4)
""")

md(r"""
### 6.2 — *November 2023 TZ1 Paper 1 Q9(b), 6 marks*

Consider the function $f(x)=\dfrac{\sin^2(kx)}{x^2}$, where $x\ne0$ and
$k\in\mathbb{R}^{+}$.

Given that $\displaystyle\lim_{x\to 0}f(x)=16$, find the value of $k$.
""")

code(r"""
q6_2 = ...

check_num('6.2', q6_2, 1, D_62)
""".replace('D_62', repr(D_62)))

md(r"""
### 6.3 — *May 2025 TZ2 Paper 2 Q11(c)(ii), part of 5 marks*

The time $T$, in minutes, that a spinning top is in motion can be modelled
by the probability density function
$$f(t)=\begin{cases}kte^{-3t}, & t\ge 0\\ 0,&\text{otherwise,}\end{cases}
  \qquad k\in\mathbb{Z}^{+},$$
and $\displaystyle\int_0^{a}f(t)\,\mathrm dt=\frac k9\Bigl[1-(3a+1)e^{-3a}\Bigr]$
for $a\in\mathbb{R}^{+}$.

Hence, by considering $\displaystyle\lim_{a\to\infty}\int_0^{a}f(t)\,\mathrm dt$,
find the value of $k$.
""")

code(r"""
q6_3 = ...

check_num('6.3', q6_3, 1, D_63)
""".replace('D_63', repr(D_63)))

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. The limit taken in a parameter

$x$ is not sacred. When the arrow sits under $n$ or under $\alpha$,
everything that is not the limiting variable stays exactly where it is,
and the answer is an expression in the letters that stayed.
""")

md(r"""
### 7.1 — *May 2025 TZ3 Paper 3 Q1(d), 4 marks*

Consider $f^{\,n}(x)=m^nx+c\left(\dfrac{1-m^n}{1-m}\right)$, where
$-1<m<1$.

As $n\to\infty$, the family of graphs $y=f^{\,n}(x)$ approaches the graph of
a straight line $L$. Determine the equation of $L$, giving your answer in
terms of $c$ and $m$. Enter the right-hand side only.
""")

code(r"""
FN = m**n*x + c*(1 - m**n)/(1 - m)

q7_1 = ...

verify_limit('7.1', q7_1, FN, var=n, point=oo,
             params={m: (Rational(1, 2), -Rational(3, 4)),
                     c: (5, -2), x: (3, 7)})
""")

md(r"""
### 7.2 — *November 2022 Paper 2 Q7, 6 marks*

Consider the vectors $\mathbf u=\mathbf i+\mathbf j$ and
$\mathbf v=\left(\cos\frac1n\right)\mathbf i+\left(\sin\frac1n\right)\mathbf j$,
where $n\in\mathbb{Z}^{+}$. Let $\theta$ be the angle between
$\mathbf u$ and $\mathbf v$.

**(a)** Find an expression for $\cos\theta$ in terms of $n$.

**(b)** Find the exact value of the limit approached by $\theta$ as
$n\to\infty$.
""")

code(r"""
q7_2a = ...
q7_2b = ...

verify_identity('7.2a', q7_2a, (cos(1/n) + sin(1/n))/sqrt(2), var=n,
                samples=(1, 2, 3, 5))
check_num('7.2b', q7_2b, 6, D_72B)
""".replace('D_72B', repr(dn(sp.pi / 4, 6))))

md(r"""
### 7.3 — *November 2023 Paper 3 Q2(f), 2 marks*

Two families of curves $F$ and $G$ intersect at an acute angle $\alpha$.
The gradient of $F$ is $f(x,y)$, the gradient of $G$ is $g(x,y)$, and
$$g(x,y)=\frac{f(x,y)+\tan\alpha}{1-f(x,y)\tan\alpha}.$$

By considering $\displaystyle\lim_{\alpha\to\pi/2}\tan\alpha$, show that for
all finite $f(x,y)$,
$$\lim_{\alpha\to\pi/2}g(x,y)=-\frac{1}{f(x,y)} .$$

Enter the limit as an expression in the letter `F`, standing for $f(x,y)$.
""")

code(r"""
G = (F + tan(alpha))/(1 - F*tan(alpha))

q7_3 = ...

verify_limit('7.3', q7_3, G, var=alpha, point=pi/2,
             params={F: (2, -3, Rational(1, 5))})
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. The rule with a letter inside the expression

The limit is still in $x$, but a parameter sits inside: $x^{n+2}$,
$S_n(x)$. Differentiate in $x$ and carry the letter along; the answer
comes out as a formula, or as one value that holds for every $n$ at once.
Before the rule comes the check, and here that check is worth its own
mark.
""")

md(r"""
### 8.1 — *November 2022 Paper 3 Q1(g)(i), 1 mark*

Let $f(x)=1+x+x^2+\dots+x^n$, $n\in\mathbb{Z}^{+}$, and $f_1(x)=x f'(x)$.
For $x\ne1$ it has been shown that
$$f_1(x)=\frac{nx^{n+2}-(n+1)x^{n+1}+x}{(x-1)^2}.$$

Show that $\displaystyle\lim_{x\to1}f_1(x)$ is in indeterminate form, and
name the form as a string: `'0/0'` or `'oo/oo'`.
""")

code(r"""
TOP = n*x**(n + 2) - (n + 1)*x**(n + 1) + x
F1 = TOP/(x - 1)**2

q8_1 = ...

verify_indeterminate('8.1', q8_1, TOP, (x - 1)**2, point=1,
                     params={n: (2, 5, 8)})
""")

md(r"""
### 8.2 — *November 2022 Paper 3 Q1(g)(ii), 5 marks*

Hence, by applying l'Hôpital's rule, show that
$\displaystyle\lim_{x\to1}f_1(x)=\tfrac12 n(n+1)$.
""")

code(r"""
q8_2 = ...

verify_limit('8.2', q8_2, F1, point=1, params={n: (2, 3, 7)})
""")

md(r"""
### 8.3 — *November 2025 TZ3 Paper 3 Q1(g), 3 marks*

Let $S_1(x)=\sin x$ and $S_n(x)=\sin\bigl(S_{n-1}(x)\bigr)$ for $n\ge2$. It
has been proved that
$$S_n'(x)=\cos\bigl(S_{n-1}(x)\bigr)\cos\bigl(S_{n-2}(x)\bigr)\cdots
  \cos\bigl(S_1(x)\bigr)\cos x .$$

Use l'Hôpital's rule to show that
$\displaystyle\lim_{x\to0}\frac{S_n(x)}{x}=1$ for $n\in\mathbb{Z}^{+}$.
""")

code(r"""
S3 = sin(sin(sin(x)))
S6 = sin(sin(sin(sin(sin(sin(x))))))

q8_3 = ...

verify_limit('8.3 (n = 3)', q8_3, S3/x)
verify_limit('8.3 (n = 6)', q8_3, S6/x)
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. What the limit means

Two marks in the topic are for a sentence about the thing being modelled.
Talk about the runner and the parabola, not about the denominator.
""")

md(r"""
### 9.1 — *May 2025 TZ3 Paper 2 Q10(c)(ii), part of 3 marks*

With $v(t)=\dfrac{8.14\,t}{\sqrt{t^2+0.2}}$ as in 2.2, state a reason why
the value in 2.2 is not valid in the context of this question.

**This question has no cell:** the answer is a sentence. Write it below and
compare with the solution.
""")

md(r"""
*your sentence here*
""")

md(r"""
### 9.2 — *May 2025 TZ1 Paper 3 Q2(b)(iii), 2 marks*

The curvature of a function $f$ is
$k(x)=\dfrac{|f''(x)|}{\bigl(1+(f'(x))^2\bigr)^{3/2}}$, and for a quadratic
$h(x)=ax^2+bx+c$ with $a\ne 0$ it is given that
$$k(x)=\frac{2|a|}{\bigl(1+(2ax+b)^2\bigr)^{3/2}} .$$

State the value of $\displaystyle\lim_{x\to\infty}k(x)$ and explain briefly
the significance of this result. The cell checks the value; write the
explanation in the markdown cell below it.
""")

code(r"""
KX = 2*abs(a) / (1 + (2*a*x + b)**2)**Rational(3, 2)

q9_2 = ...

verify_limit('9.2', q9_2, KX, point=oo, params={a: (2, -3), b: (5, 0)})
""")

md(r"""
*your explanation here*
""")

# ------------------------------------------------------------------ решения
md(r"""
---
# 🔑 Solutions

Numbered as above. Read one after you have worked the question.

---
### 1.1 — *May 2024 TZ1 P1 Q11(f)(i)*

$P(-1)=-3+5-1-1=0$, so $(x+1)$ divides $P$, and
$P(x)=(x+1)(3x^2+2x-1)=(x+1)^2(3x-1)$. With $Q(x)=(x+1)(2x+1)$,
$$f(x)=\frac{(x+1)^2(3x-1)}{(x+1)^2(2x+1)}=\frac{3x-1}{2x+1}\quad(x\ne-1),$$
so $\displaystyle\lim_{x\to-1}f(x)=\frac{-4}{-1}=4$.

No calculus is needed. The cancelled $(x+1)^2$ is the shared reason both
parts vanish; once it is gone the function is continuous at $-1$ and
substitution finishes the job. Note that $f(-1)$ itself does not exist —
which is the whole reason the question asks for a limit.

---
### 2.1 — *May 2024 TZ1 P1 Q11(f)(ii)*

Using the cancelled form and dividing by $x$,
$$\lim_{x\to\infty}\frac{3x-1}{2x+1}
 =\lim_{x\to\infty}\frac{3-\frac1x}{2+\frac1x}=\frac32 .$$
Top and bottom have the same degree, so the limit is the ratio of the
leading coefficients.

---
### 2.2 — *May 2025 TZ3 P2 Q10(c)(i)*

$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}}
 =\frac{8.14}{\sqrt{1+\frac{0.2}{t^2}}}\;\longrightarrow\;8.14 .$$
*Write down* means one mark and no working expected — but this is the
working that tells you the answer is $8.14$ and not $0$ or $\infty$.

---
### 3.1 — *May 2021 TZ1 P1 Q8, 5 marks*

Substituting gives $\frac{\arctan 0}{\tan 0}=\frac00$, so the rule applies:
$$\lim_{x\to0}\frac{\arctan2x}{\tan3x}
 =\lim_{x\to0}\frac{\frac{2}{1+4x^2}}{3\sec^2 3x}
 =\frac{2}{3}.$$
**M1** for attempting to differentiate numerator and denominator, **A1A1**
for the two derivatives, **(M1)** for substituting $x=0$, **A1** for
$\frac23$. The markscheme note: *do not condone absence of limits* — award
a maximum of **M1A1A0M1A1** if $\lim$ is missing.

---
### 3.2 — *May 2023 TZ1 P3 Q1(c)(i), 2 marks*

The form is $\frac{\infty}{\infty}$:
$$\lim_{b\to\infty}\frac{e^b-b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b}{e^b}=1 .$$
**A1** for the correct quotient — *condone absence of limit* here — and
**A1** for the $1$. In the question this is $A_1$, the whole area under
$xe^{-x}$ from $0$ to infinity, and it is exactly $1$.

---
### 3.3 — *May 2025 TZ2 P2 Q11(c)(i)*

$(3x+1)e^{-3x}$ is a product of the form $\infty\cdot0$, and the rule does
not apply to products. Rewrite first:
$$\lim_{x\to\infty}(3x+1)e^{-3x}
 =\lim_{x\to\infty}\frac{3x+1}{e^{3x}}
 =\lim_{x\to\infty}\frac{3}{3e^{3x}}
 =\lim_{x\to\infty}\frac{1}{e^{3x}}=0 .$$
The markscheme's note on the first line is unusually firm: *this first
**A1** must be seen.* The rewrite is the mark.

---
### 4.1 — *May 2024 TZ2 P1 Q8, 6 marks*

$\frac00$ at the start. First round:
$$\lim_{x\to0}\frac{4\sec^4x\tan x+2\sin x\cos x}{4x^3-2x},$$
still $\frac00$. Second round:
$$\lim_{x\to0}\frac{16\sec^4x\tan^2x+4\sec^6x-2\sin^2x+2\cos^2x}{12x^2-2}
 =\frac{0+4-0+2}{-2}=-3 .$$
The denominator is now $-2$, so the form is no longer indeterminate and the
work stops. **M1** for the second application *providing their expression is
in indeterminate form as $x\to0$ and providing there is no third attempt at
using l'Hôpital's rule*, and: *to award full marks limit notation
$\lim_{x\to0}$ must be seen at least once; if no limit notation is seen but
otherwise all correct, do not award the final **A1***.

---
### 4.2 — *May 2025 TZ3 P1 Q9, 6 marks*

$\frac{0\cdot0}{1-1}=\frac00$. First round:
$\displaystyle\lim_{x\to0}\frac{\sin x+x\cos x}{\sin x}$, still $\frac00$.
Second round:
$$\lim_{x\to0}\frac{2\cos x-x\sin x}{\cos x}=\frac{2-0}{1}=2 .$$
Without any calculus: multiply above and below by $1+\cos x$,
$$\frac{x\sin x(1+\cos x)}{1-\cos^2x}=\frac{x}{\sin x}(1+\cos x)
 \longrightarrow 1\cdot 2=2 .$$

---
### 4.3 — *May 2022 TZ2 P2 Q7(b), 6 marks*

With $k=\frac\pi4$ the form is $\frac00$. Differentiating,
$$\frac{\mathrm d}{\mathrm dx}\arctan(\cos x)=\frac{-\sin x}{1+\cos^2x},$$
so
$$\lim_{x\to0}\frac{-\sin x}{2x\,(1+\cos^2x)}
 =-\frac12\cdot\lim_{x\to0}\frac{\sin x}{x}\cdot
   \lim_{x\to0}\frac{1}{1+\cos^2x}
 =-\frac12\cdot1\cdot\frac12=-\frac14 .$$
Or apply the rule a second time to the same effect. Since the answer is
printed in the question, every mark is for the working.

---
### 5.1 — *November 2021 P1 Q11(c), 4 marks*

$x^9=(x^3)^3$, so pull the cube out first:
$$\frac{(x^2e^x-x^2)^3}{x^9}
 =\left(\frac{x^2(e^x-1)}{x^3}\right)^3
 =\left(\frac{e^x-1}{x}\right)^3 .$$
And $e^x-1=x+\frac{x^2}{2}+\dots$, so $\frac{e^x-1}{x}\to1$ and the limit
is $1^3=1$. The markscheme prints this as METHOD 2 and applies l'Hôpital's
rule to the inner quotient; METHOD 1 uses the Maclaurin series from the
previous part.

---
### 5.2 — *May 2022 TZ1 P1 Q12(d) and Q12(e)*

**(a)** With $g(x)=e^x\cos x$: $g(0)=1$, $g'(0)=1$, $g''(0)=0$,
$g'''(0)=-2$, $g^{(4)}(0)=-4$, so
$$g(x)=1+x-\frac{x^3}{3}-\frac{x^4}{6}+\dots$$
The vanishing $x^2$ term is what makes the next part work.

**(b)** $$\frac{e^x\cos x-1-x}{x^3}
 =\frac{-\frac{x^3}{3}-\frac{x^4}{6}+\dots}{x^3}
 \longrightarrow-\frac13 .$$
The l'Hôpital route needs three rounds and runs to half a page; the
markscheme prints both.

---
### 5.3 — *May 2025 TZ1 P1 Q12(e), 5 marks*

**(a)** $\cos x=1-\frac{x^2}{2}+\dots$, so
$$\cos^nx=\left(1-\frac{x^2}{2}+\dots\right)^n=1-\frac{nx^2}{2}+\dots$$
— only the first two binomial terms matter, because the rest carry $x^4$.
Equivalently $f_n(0)=1$, $f_n'(0)=0$, $f_n''(0)=-n$.

**(b)** $$\frac{f_n(x)-1}{x^2}=\frac{-\frac{nx^2}{2}+\dots}{x^2}
 \longrightarrow-\frac n2 .$$
Markscheme note: *do not award FT marks for an expression that does not
involve $n$.* An answer without $n$ in it is not an answer.

---
### 6.1 — *May 2022 TZ2 P2 Q7(a), 2 marks*

$\lim_{x\to0}x^2=0$, so the indeterminate form $\frac00$ is *required* for
the limit to be finite — otherwise the quotient is unbounded. Hence
$$\lim_{x\to0}\bigl(\arctan(\cos x)-k\bigr)=0
 \;\Longrightarrow\;\arctan 1-k=0\;\Longrightarrow\;k=\frac\pi4 .$$
**M1** for setting the numerator's limit to zero, **A1** for
$k=\arctan 1$, **AG** for $\frac\pi4$. The note: *award **M1A0** for using
$k=\frac\pi4$ to show the limit is $\frac00$* — that is the argument
backwards.

---
### 6.2 — *November 2023 TZ1 P1 Q9(b), 6 marks*

$$\frac{\sin^2kx}{x^2}=\left(\frac{\sin kx}{x}\right)^2
 =k^2\left(\frac{\sin kx}{kx}\right)^2\longrightarrow k^2 ,$$
or apply l'Hôpital's rule twice to the same end. So $k^2=16$, and
$k\in\mathbb{R}^{+}$ leaves $k=4$. Rejecting $-4$ out loud is part of the
answer.

---
### 6.3 — *May 2025 TZ2 P2 Q11(c)(ii)*

Take the limit through the given integral, using 3.3:
$$\lim_{a\to\infty}\int_0^a f(t)\,\mathrm dt
 =\frac k9\Bigl(1-\lim_{a\to\infty}(3a+1)e^{-3a}\Bigr)=\frac k9 .$$
A probability density function integrates to $1$ over its whole range —
**M1**, *recognising area of probability density function $=1$, seen
anywhere* — so $\frac k9=1$ and $k=9$.

---
### 7.1 — *May 2025 TZ3 P3 Q1(d), 4 marks*

Only $m^n$ moves, and $-1<m<1$ gives $m^n\to0$. So $m^nx\to0$ and
$c\dfrac{1-m^n}{1-m}\to\dfrac{c}{1-m}$, leaving
$$L:\;y=\frac{c}{1-m} .$$
**(M1)** for applying $m^n\to0$ to at least one term, **(A1)** for the term
in $x$ vanishing, **A1** for the constant term, **A1** for the line. Note
that $x$ never moved: $L$ is horizontal, which is the point of the
question.

---
### 7.2 — *November 2022 P2 Q7, 6 marks*

**(a)** $\mathbf u\cdot\mathbf v=\cos\frac1n+\sin\frac1n$,
$|\mathbf u|=\sqrt2$ and $|\mathbf v|=1$, so
$$\cos\theta=\frac{\cos\frac1n+\sin\frac1n}{\sqrt2}.$$

**(b)** As $n\to\infty$, $\frac1n\to0$, so
$\cos\theta\to\frac{1+0}{\sqrt2}=\frac1{\sqrt2}$ and
$\theta\to\frac\pi4$. Equivalently $\mathbf v\to\mathbf i$, and the angle
between $\mathbf i+\mathbf j$ and $\mathbf i$ is $\frac\pi4$.
The note: *accept $45°$; do not accept rounded values such as $0.785$.*

---
### 7.3 — *November 2023 P3 Q2(f), 2 marks*

As $\alpha\to\frac\pi2$, $\tan\alpha\to\infty$, so
$\frac{1}{\tan\alpha}\to0$. Divide the top and bottom of $g$ by
$\tan\alpha$:
$$g=\frac{\frac{f}{\tan\alpha}+1}{\frac{1}{\tan\alpha}-f}
 \longrightarrow\frac{0+1}{0-f}=-\frac1f .$$
**M1** for the division, **R1** for $\frac1{\tan\alpha}\to0$, and the
**R1** is dependent on the **M1**. Geometrically: $\alpha=\frac\pi2$ means
the families are perpendicular, and perpendicular gradients are negative
reciprocals.

---
### 8.1 — *November 2022 P3 Q1(g)(i), 1 mark*

At $x=1$ the numerator is $n\cdot1-(n+1)\cdot1+1=0$ and the denominator is
$(1-1)^2=0$, so
$$\lim_{x\to1}f_1(x)=\frac{n-(n+1)+1}{0}=\frac00 .$$
**R1**, and the note is strict: *only award **R1** for sufficient
simplification of the numerator, as shown above. Do not award **R1** if
$\lim_{x\to1}$ is not referred to or stated.*

---
### 8.2 — *November 2022 P3 Q1(g)(ii), 5 marks*

First round:
$$\lim_{x\to1}\frac{n(n+2)x^{n+1}-(n+1)^2x^{n}+1}{2(x-1)} .$$
At $x=1$ the numerator is $n(n+2)-(n+1)^2+1=0$, so it is $\frac00$ again.
Second round:
$$\lim_{x\to1}\frac{n(n+1)(n+2)x^{n}-n(n+1)^2x^{n-1}}{2}$$
$$=\frac{n(n+1)\bigl[(n+2)-(n+1)\bigr]}{2}=\frac{n(n+1)}{2}.$$
Which is $1+2+\dots+n$ — as it had to be, since
$f_1(1)=1+2+\dots+n$ directly from the definition.

### 8.3 — *November 2025 TZ3 P3 Q1(g), 3 marks*

$S_n(0)=0$ and the denominator is $0$, so the form is $\frac00$. One round
of the rule:
$$\lim_{x\to0}\frac{S_n(x)}{x}=\lim_{x\to0}\frac{S_n'(x)}{1}
 =\lim_{x\to0}\cos\bigl(S_{n-1}(x)\bigr)\cdots\cos\bigl(S_1(x)\bigr)\cos x .$$
Every $S_k(0)=0$, so every factor tends to $\cos 0=1$, and a product of $n$
ones is $1$. The induction in the previous part is what makes this three
lines rather than $n$ of them.

---
### 9.1 — *May 2025 TZ3 P2 Q10(c)(ii)*

The race is only $200$ metres long. Fiona finishes it in about $26$
seconds, so $t$ never approaches infinity and her velocity never reaches
$8.14\ \mathrm{m\,s^{-1}}$: the limit describes the formula after the race
has stopped describing the runner.

Answers about the algebra — "the denominator grows without bound" — earn
nothing here. The mark is for talking about the race.

---
### 9.2 — *May 2025 TZ1 P3 Q2(b)(iii), 2 marks*

As $x\to\infty$ the term $(2ax+b)^2$ grows without bound while the
numerator $2|a|$ is fixed, so
$$\lim_{x\to\infty}k(x)=0 .$$
**A1**. And the significance, **R1**: the curvature of a quadratic tends to
zero far from the vertex — *for large positive values of $x$, quadratic
functions are close to being straight*, or, as the note allows, *a
quadratic function behaves like a linear function*.

---
---
### Where the marks are

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Substitute and cancel | 1 | part of 3 |
| 2 | Highest power at infinity | 2 | part of 6 |
| 3 | l'Hôpital, one round | 3 | 8 |
| 4 | l'Hôpital, more than one | 3 | 18 |
| 5 | Maclaurin instead | 3 | 9 |
| 6 | The constant that makes it exist | 3 | 10 |
| 7 | The limit in a parameter | 3 | 9 |
| 8 | The rule with a letter inside | 3 | 9 |
| 9 | What the limit means | 2 | part of 5 |

Sections 3 and 4 together are $26$ of the $73$ marks and they are one
instruction repeated: substitute, name the form, differentiate, substitute
again. Sections 7 and 8 are the surprise of the topic — eighteen marks
where the answer is a formula in a letter rather than a number — and that
is where a student who has only practised $\frac00$ loses the most.
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
