"""Собирает архивный ноутбук E2: весь корпус темы, по приёмам, подряд.

Пятый ноутбук в формате, опробованном на B4, C3, B5 и E1. Практикум E2
учит — лестница, теория, уровни, тренажёр. Этот не учит, он даёт набивать
руку: вопрос, ячейка для ответа с мгновенной проверкой, разбор в конце.

Внутри — вся тема calculus.series из архива AA HL, сессии May 2021 —
November 2025: 27 вопросов и 99 баллов, разложенные по девяти приёмам
карточки calculus-series.yaml.

Почему 99, а не 105. Корпус числит за темой 27 блоков, и один из них
дублирует другой: вопрос про e^(cos 2x) в ноябре 2023 поставлен в TZ1
и TZ2 слово в слово. Бумаги разные (8823-7106 и 8823-7111), совпадение
в них самих, а не в разметке; ровно та же пара бумаг дала такой же дубль
в E1. В архив вопрос входит один раз.

Вопросов при этом 27, а блоков 26: ноябрьский вопрос разрезан по пунктам —
(d)(i) отвечает подстановкой и стоит в секции 2, (d)(ii) и (d)(iii)
отвечают подстановкой ряда в ряд и стоят в секции 5.

Четыре вопроса ячейки не имеют вовсе: их ответ напечатан в самом условии
(«show that»), проверять нечего, и весь смысл там в выкладке. Такие
вопросы отправляют читать решение — так же, как это делалось в C3 и E1.

Хешей здесь шесть из двадцати трёх — против двух из двадцати трёх в E1,
и причина в самой теме. Хеш нужен там, где ответ нельзя подставить обратно
в условие, а вторая половина E2 состоит из приближений: 61/105, 500/279,
π ≈ 3.1412, ошибка 3.7·10⁻⁵. Приближение — это число, а не соотношение,
и подставлять его некуда. Чем полезнее ответ, тем меньше он проверяем
по существу.

Зато первая половина проверяется без эталона вовсе. verify_maclaurin
вычитает написанное из функции и смотрит, с какой степени начинается
остаток; verify_series_solution подставляет многочлен в дифференциальное
уравнение; verify_terms примеряет границу к члену n + 1 и к члену n;
verify_roots подставляет каждое найденное значение m обратно в
коэффициент при x².

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_e2.py прогоняет весь ноутбук
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
x = sp.Symbol('x')
n, m, a, r = sp.symbols('n m a r')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/archive-e2-maclaurin.ipynb')


def dn(value, sf=3):
    return digest(sig(value, sf))


def de(expr):
    return digest(sp.srepr(sp.simplify(sp.sympify(expr))))


# --- шесть хешей; все шесть — приближения, подставлять их некуда ---
D_72 = dn(sp.N(3 - 3*R(15, 100) + R(3, 2)*R(15, 100)**2
               + R(3, 2)*R(15, 100)**3, 12), 6)          # y(0.15), 6 знач. цифр
D_81 = de(R(61, 105))                                    # интеграл через ряд
D_82 = de(R(500, 279))                                   # √3 в виде c/d
D_83 = dn(3.156, 4)                                      # π к трём знакам
D_84 = dn(3.1412, 5)                                     # π к четырём знакам
# Ошибка: 3.69·10⁻⁵ по округлённому значению из пункта (f), 3.73·10⁻⁵
# по неокруглённому. Схема оценивания принимает оба; до двух значащих
# цифр они совпадают, и проверка спрашивает именно две.
D_92 = dn(3.69e-5, 2)
D_93 = dn(float(1) / 21870, 3)                           # граница по теореме

ANSWERS = {
    'q1_1': 'x**2 + x**3 + x**4/2',
    'q1_2': '1 + x - x**3/3 - x**4/6',
    'q1_3': '1 - n*x**2/2',
    'q2_1': 'x**2 - x**6/6',
    'q2_2': '1 - 2*x**2 + 2*x**4/3',
    'q3_1': '1 + 4*x + 10*x**2 + 20*x**3',
    'q4_1': 'x + x**2 + x**3/3',
    'q4_2': 'x**4 - x**8/3',
    'q4_3': '4*x**3 - 8*x**7/3',
    'q4_4': '[Rational(3, 2), -Rational(5, 2)]',
    'q5_1': '1 - 2*x**2 + 8*x**4/3',
    'q5_2': 'E*(1 - 2*x**2 + 8*x**4/3)',
    'q6_1': 'a/(1 - r)**2',
    'q6_2': 'sqrt(2)/2',
    'q6_3': '1/(1 + 2*x**2)',
    'q7_1': '3 - 3*x + 3*x**2/2 + 3*x**3/2',
    'q7_2': '2.58881',
    'q8_1': 'Rational(61, 105)',
    'q8_2': 'Rational(500, 279)',
    'q8_3': '3.156',
    'q8_4': '3.1412',
    'q8_5': '4*pi',
    'q8_6': '4',
    'q9_1': '6',
    'q9_2': '3.69e-5',
    'q9_3': 'Rational(1, 21870)',
    'q9_4': '7',
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
# E2 archive: Maclaurin series

**Every past-paper question on this topic, grouped by technique.** Not a
practicum — a drill. There is no theory here and no ladder to climb: the
theory is in *Practicum E2*, and this notebook is what you open afterwards,
when the only thing left is to do them all until the moves are automatic.

**What is inside.** The whole of `calculus.series`, sessions May 2021 —
November 2025: **27 questions, 99 marks**, in nine sections, one section
per technique.

The corpus records 27 blocks and 105 marks. One of them is a duplicate: the
November 2023 question on $\mathrm{e}^{\cos 2x}$ was set in TZ1 and in TZ2
word for word — two different papers, 8823-7106 and 8823-7111, one question.
It appears here once. The count of *questions* is nevertheless 27, because
the November 2023 question is split across two sections: part (d)(i) is
answered by substituting into a known series and belongs to section 2, while
(d)(ii) and (d)(iii) put a series inside a series and belong to section 5.

**Fourteen questions are Paper 1, four are Paper 2, eight are Paper 3** —
and unlike the four topics before it, this one really does split that way.
Paper 1 wants $x+x^2+\frac{x^3}{3}$ and $m=\frac32,-\frac52$: exact, every
time. Paper 3 wants $\pi\approx3.1412$ and an error of $3.7\times10^{-5}$.
The second half of this topic is arithmetic, and it is meant to be.

**How to work.** Read the question, answer in the cell below it, run the
cell. Most of the checks here do not know the answer. `verify_maclaurin`
takes the function from the question, subtracts what you wrote, and asks
where the remainder starts: a Maclaurin polynomial is not some polynomial to
be guessed but the one that hugs the function at zero tightly enough, and
that is a property of your answer alone. `verify_series_solution` puts your
polynomial into the differential equation. `verify_terms` tries the error
bound against term $n+1$ and against term $n$, which is the whole of the
off-by-one this topic is famous for.

**Six checks do compare a hash**, and they are all the same case: the answer
is an approximation. $\frac{61}{105}$, $\frac{500}{279}$, $3.1412$,
$3.7\times10^{-5}$ — a number produced by throwing away the tail of a series
has nothing to be substituted back into. E1 needed two hashes in twenty-three
cells; E2 needs six, and the reason is not a weaker design but a topic whose
second half is entirely about approximation.

**Four questions have no cell at all.** In each of them the answer is printed
in the question — «show that the Maclaurin series for $\sec x$ … is
$1+\frac{x^2}{2}+\frac{5x^4}{24}$» — so there is nothing to check and
everything to derive. Read the question, do the work on paper, then read the
solution.

Leave a cell blank and it prints ⬜ and moves on, which means you can run
the whole notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before — and read the markscheme note in it,
because that is where the marks actually are.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | Straight from the definition | 4 | 13 |
| 2 | Substitute into a series you know | 2 | 2 + part of 6 |
| 3 | The binomial series | 1 | 5 |
| 4 | Multiplying two series | 5 | 21 |
| 5 | A series inside a series | 2 | 4 + part of 6 |
| 6 | Differentiating and integrating a series | 3 | 12 |
| 7 | A series out of a differential equation | 1 | 3 |
| 8 | The series in place of the function | 6 | 20 |
| 9 | How wrong the approximation is | 3 | 13 |

Sections 1–5 build a series and carry $45$ of the $99$ marks; the choice
between them is half the work, and it is settled by looking at the function
before writing anything. Sections 6–7 get a series out of another series or
out of an equation. Sections 8–9 use it — and section 9 is the only place
in the whole archive where anyone asks how good an approximation is.

**Five series are worth knowing cold**, because every question here starts
by recognising one of them: $\mathrm{e}^x$, $\sin x$, $\cos x$,
$\ln(1+x)$, $\arctan x$. They are in the formula booklet. The binomial
series is there too, and the questions that need it say so.
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
print('an exact number:       ', Rational(500, 279))
print('a decimal:             ', 3.1412)
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. Straight from the definition

$$f(x)=f(0)+f'(0)\,x+\frac{f''(0)}{2!}x^2+\frac{f'''(0)}{3!}x^3+\dots$$

The way in when nothing else works: differentiate, put $x=0$, divide by
$n!$. In practice the differentiating has usually been done for you in the
part before — an $n$th derivative proved by induction, or a relation like
$g''=2(g'-g)$ — and *hence* means you are meant to use it.
""")

md(r"""
### 1.1 — *November 2021 Paper 1 Q11(b), 3 marks*

It is given that
$$\frac{\mathrm{d}^n}{\mathrm{d}x^n}\!\left(x^2\mathrm{e}^x\right)
 =\left[x^2+2nx+n(n-1)\right]\mathrm{e}^x,\qquad n\in\mathbb{Z}^+ .$$

Hence or otherwise, determine the Maclaurin series of $f(x)=x^2\mathrm{e}^x$
in ascending powers of $x$, up to and including the term in $x^4$.
""")

code(r"""
F = x**2 * exp(x)

q1_1 = ...

verify_maclaurin('1.1', q1_1, F, order=4)
""")

md(r"""
### 1.2 — *May 2022 TZ1 Paper 1 Q12(d), 5 marks*

The function $g$ is defined by $g(x)=\mathrm{e}^x\cos x$. It has been shown
that
$$g''(x)=2\bigl(g'(x)-g(x)\bigr)
 \qquad\text{and}\qquad
 g^{(4)}(x)=2\bigl(g'''(x)-g''(x)\bigr).$$

Using this result, find the Maclaurin series for $g(x)$ up to and including
the $x^4$ term.
""")

code(r"""
G = exp(x) * cos(x)

q1_2 = ...

verify_maclaurin('1.2', q1_2, G, order=4)
""")

md(r"""
### 1.3 — *May 2025 TZ1 Paper 1 Q12(e)(i), 3 marks*

Consider the family of functions $f_n(x)=\cos^n x$, where $x\in\mathbb{R}$
and $n\in\mathbb{N}$.

Find the Maclaurin series of $f_n(x)$ up to the term in $x^2$.
""")

code(r"""
FN = cos(x)**n

q1_3 = ...

verify_maclaurin('1.3', q1_3, FN, order=2, params={n: (2, 3, 7)})
""")

md(r"""
### 1.4 — *May 2024 TZ2 Paper 1 Q12(b), 2 marks*

Let $f(x)=(1-ax)^{-\frac12}$, where $ax<1$, $a\ne0$. It has been proved by
induction that
$$f^{(n)}(x)=\frac{a^n(2n-1)!\,(1-ax)^{-\frac{2n+1}{2}}}{2^{2n-1}(n-1)!},
 \qquad n\in\mathbb{Z}^+ .$$

By using part (a) or otherwise, show that the Maclaurin series for
$f(x)=(1-ax)^{-\frac12}$ up to and including the $x^2$ term is
$$1+\tfrac12 ax+\tfrac38 a^2x^2 .$$

*This question has no cell: the answer is printed in it. The marks are in
the route, and the route is in the solution.*
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. Substitute into a series you know

$\sin(x^2)$, $\cos 2x$, $\mathrm{e}^{-3x}$: the same five series with a
different letter inside. Replace $x$ by the whole new argument, power and
all — and recount how deep the original series has to go, because
$(x^2)^3=x^6$ eats three terms of the answer in one.
""")

md(r"""
### 2.1 — *May 2024 TZ1 Paper 1 Q8(a)(i), 2 marks*

Find the first two non-zero terms in the Maclaurin series of $\sin(x^2)$.
""")

code(r"""
q2_1 = ...

verify_maclaurin('2.1', q2_1, sin(x**2), terms=2)
""")

md(r"""
### 2.2 — *November 2023 TZ1 Paper 1 Q11(d)(i), part of 6 marks*

Consider the function $f(x)=\mathrm{e}^{\cos 2x}$, where
$-\frac{\pi}{4}\le x\le\frac{5\pi}{4}$.

Find the Maclaurin series for $\cos 2x$, up to and including the term
in $x^4$.
""")

code(r"""
q2_2 = ...

verify_maclaurin('2.2', q2_2, cos(2*x), order=4)
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. The binomial series

$$(1+u)^p=1+pu+\frac{p(p-1)}{2!}u^2+\frac{p(p-1)(p-2)}{3!}u^3+\dots,
 \qquad |u|<1 .$$

The bracket has to start with a $1$; if it does not, take the factor out
first. The sign inside travels with $u$, and the expansion is infinite, so
the question always says where to stop.
""")

md(r"""
### 3.1 — *November 2025 TZ1 Paper 1 Q5(a), 5 marks*

The first four terms of the Maclaurin series expansion of $(1-x)^{-4}$ are
$$1+ax+bx^2+20x^3,\qquad a,b\in\mathbb{Z}^+ .$$

(i) Show that $a=4$.  (ii) Find the value of $b$.

*Answer with the whole series up to $x^3$ — that is the two parts together.*
""")

code(r"""
q3_1 = ...

verify_maclaurin('3.1', q3_1, (1 - x)**-4, order=3)
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. Multiplying two series

The commonest technique in the topic: $21$ of the $99$ marks. Expand each
factor with a little room to spare, multiply, and throw away everything
above the power you were asked for **as you go**, not at the end.

One thing to watch before you start: how deep each factor has to go is not
the same for both. $\sin x$ begins at $x$, so in $\mathrm{e}^x\sin x$ up to
$x^3$ the sine needs two terms and the exponential three.
""")

md(r"""
### 4.1 — *May 2022 TZ1 Paper 1 Q12(a), 4 marks*

The function $f$ is defined by $f(x)=\mathrm{e}^x\sin x$, where
$x\in\mathbb{R}$.

Find the Maclaurin series for $f(x)$ up to and including the $x^3$ term.
""")

code(r"""
q4_1 = ...

verify_maclaurin('4.1', q4_1, exp(x)*sin(x), order=3)
""")

md(r"""
### 4.2 — *May 2024 TZ1 Paper 1 Q8(a)(ii), 3 marks*

Find the first two non-zero terms in the Maclaurin series of $\sin^2(x^2)$.
""")

code(r"""
q4_2 = ...

verify_maclaurin('4.2', q4_2, sin(x**2)**2, terms=2)
""")

md(r"""
### 4.3 — *May 2024 TZ1 Paper 1 Q8(b), 2 marks*

Hence, or otherwise, find the first two non-zero terms in the Maclaurin
series of $4x\sin(x^2)\cos(x^2)$.
""")

code(r"""
q4_3 = ...

verify_maclaurin('4.3', q4_3, 4*x*sin(x**2)*cos(x**2), terms=2)
""")

md(r"""
### 4.4 — *May 2021 TZ1 Paper 1 Q12(c), 8 marks*

Let $f(x)=\sqrt{1+x}$ for $x>-1$, and let $g(x)=\mathrm{e}^{mx}$,
$m\in\mathbb{Q}$. Consider the function $h$ defined by
$h(x)=f(x)\times g(x)$ for $x>-1$.

It is given that the $x^2$ term in the Maclaurin series for $h(x)$ has a
coefficient of $\frac74$. Find the possible values of $m$.
""")

code(r"""
H = sqrt(1 + x) * exp(m*x)

q4_4 = [...]

# The check puts each of your values back where the question puts it: into
# the coefficient of x^2, which has to come out as 7/4. Then it scans the
# window for values you missed.
verify_roots('4.4', q4_4, series(H, x, 0, 3).removeO().coeff(x, 2) - Rational(7, 4),
             (-10, 10), var=m)
""")

md(r"""
### 4.5 — *May 2024 TZ2 Paper 1 Q12(c), 4 marks*

It has been shown that the Maclaurin series for $(1-ax)^{-\frac12}$ up to
the $x^2$ term is $1+\frac12ax+\frac38a^2x^2$.

Hence show that
$$(1-2x)^{-\frac12}(1-4x)^{-\frac12}\approx\frac{2+6x+19x^2}{2}.$$

*This question has no cell: the answer is printed in it.*
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. A series inside a series

Section 2 substituted a single power. Here what goes inside is itself a
series, and it has to be raised to powers — so the arithmetic is longer and
one condition matters that did not before: **the inside has to vanish at
zero.** $\mathrm{e}^u$ is expanded about $u=0$, and $\cos 2x$ at $x=0$ is
$1$, not $0$. That is why the November 2023 question walks you through
$\mathrm{e}^{\cos 2x-1}$ first and only then puts the $\mathrm{e}$ back.
""")

md(r"""
### 5.1 — *May 2021 TZ2 Paper 2 Q9(b), 4 marks*

The first three terms of the binomial expansion of $(1+t)^{-1}$ in ascending
powers of $t$ are $1-t+t^2$.

By using the Maclaurin series for $\cos x$ and the result above, show that
the Maclaurin series for $\sec x$ up to and including the term in $x^4$ is
$$1+\frac{x^2}{2}+\frac{5x^4}{24}.$$

*This question has no cell: the answer is printed in it.*
""")

md(r"""
### 5.2 — *November 2023 TZ1 Paper 1 Q11(d)(ii) and (iii), part of 6 marks*

Still with $f(x)=\mathrm{e}^{\cos 2x}$, and using the series for $\cos 2x$
from 2.2:

(ii) Hence, find the Maclaurin series for $\mathrm{e}^{\cos 2x-1}$, up to
and including the term in $x^4$.

(iii) Hence, write down the Maclaurin series for $f(x)$, up to and including
the term in $x^4$.
""")

code(r"""
q5_1 = ...          # (ii)  the series for e^(cos 2x - 1)
q5_2 = ...          # (iii) the series for e^(cos 2x)

verify_maclaurin('5.2(ii)',  q5_1, exp(cos(2*x) - 1), order=4)
verify_maclaurin('5.2(iii)', q5_2, exp(cos(2*x)),     order=4)
""")

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. Differentiating and integrating a series

When the series you want is unknown but the series for its derivative or
its integral is not. The tell is usually a geometric series in the question,
because $1+u+u^2+\dots=\frac{1}{1-u}$ *is* a Maclaurin series — the one
everybody uses without noticing.

Integrating brings a constant with it, and $x=0$ is what fixes it. That is
a mark on its own.
""")

md(r"""
### 6.1 — *November 2025 TZ3 Paper 3 Q2(b), 3 marks*

Given $|x|<1$, the sum to infinity of the geometric series
$1-x^2+x^4-x^6+\dots$ is $\dfrac{1}{1+x^2}$.

Hence, use integration to show that the Maclaurin series of $\arctan x$ may
be expressed as
$$\arctan x=x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}+\dots$$

*This question has no cell: the answer is printed in it. It is also the
foundation of every question in sections 8 and 9, so it is worth doing on
paper properly.*
""")

md(r"""
### 6.2 — *May 2024 TZ1 Paper 3 Q1(c)(i), 4 marks*

Consider the sum of an infinite geometric sequence, with first term $a$ and
common ratio $r$ $(|r|<1)$,
$$a+ar+ar^2+ar^3+\dots=\frac{a}{1-r}.$$

By differentiating both sides of the above equation with respect to $r$,
find an expression for $\displaystyle\sum_{n=1}^{\infty} n\,a\,r^{\,n-1}$ in
terms of $a$ and $r$.
""")

code(r"""
q6_1 = ...

# The check does to the right-hand side exactly what the question tells you
# to do to both sides — and then compares.
verify_identity('6.2', q6_1, diff(a/(1 - r), r), var=r)
""")

md(r"""
### 6.3 — *May 2025 TZ1 Paper 2 Q12(c), 5 marks*

Consider the family of functions $f_n$ defined by
$\displaystyle f_n(x)=\sum_{r=0}^{n}\left(-2x^2\right)^r$, where
$x\in\mathbb{R}$ and $n\in\mathbb{N}$.

Consider the function $f(x)=\lim_{n\to\infty}f_n(x)$, defined over the
domain $-k<x<k$ where $k>0$. The largest possible value of $k$ is $K$.

(i) Find the value of $K$, giving your answer in exact form.

(ii) Express $f(x)$ as a rational function in the form
$\dfrac{1}{a+bx^2}$, where $a$ and $b$ are constants to be determined.
""")

code(r"""
q6_2 = ...          # (i)  K, exact
q6_3 = ...          # (ii) f(x) as a rational function

verify_exact('6.3(i)', q6_2, 1/sqrt(2))

# For (ii) the check has no closed form to compare against — it sums the
# series from the question far enough that the tail cannot be seen, and
# asks whether your rational function agrees inside the domain.
PARTIAL = Sum((-2*x**2)**r, (r, 0, 200)).doit()
verify_identity('6.3(ii)', q6_3, PARTIAL, var=x,
                samples=(0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4))
""")

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. A series out of a differential equation

There is no formula for the function at all — only an equation and a
starting value. That is enough: the equation hands you $y'(0)$, and
differentiating the equation hands you the next derivative, one at a time.

The one thing that goes wrong here goes wrong every time: the right-hand
side contains $y$, and $y$ is a function of $x$, so differentiating it
produces $\frac{\mathrm{d}y}{\mathrm{d}x}$. Miss that and the whole tower
collapses from the second derivative up.
""")

md(r"""
### 7.1 — *May 2023 TZ1 Paper 2 Q12(c), 3 marks*

Consider the differential equation
$$\frac{\mathrm{d}y}{\mathrm{d}x}=\frac{x^2y-y}{x^2+1},$$
where $y>0$ and $y=3$ when $x=0$. It has been shown that
$\frac{\mathrm{d}^2y}{\mathrm{d}x^2}=3$ when $x=0$.

(i) Given that $\frac{\mathrm{d}^3y}{\mathrm{d}x^3}=9$ when $x=0$, find the
first four terms of the Maclaurin series for $y$.

(ii) Use the Maclaurin series to find an approximate value for $y$ when
$x=0.15$. Give your answer correct to six significant figures.
""")

code(r"""
RHS = (x**2*y - y)/(x**2 + 1)

q7_1 = ...          # (i)  the first four terms
q7_2 = ...          # (ii) y(0.15) to six significant figures

# No function to compare with — there is no formula for y. The check puts
# your polynomial into the equation instead, and into the initial condition.
verify_series_solution('7.1(i)', q7_1, RHS, ic=3, order=3)
check_num('7.1(ii)', q7_2, 6, '""" + D_72 + r"""')
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. The series in place of the function

The series is in hand — usually from the part just above, and *hence* says
so. Now the polynomial stands in for the function, and you do to it what you
could not do to her: cancel a power and read off a limit, substitute a
number, integrate.

$\int_0^1\mathrm{e}^{x^2}\sin(x^2)\,\mathrm{d}x$ has no antiderivative in
closed form. That is not an obstacle to the question — it is the question.
""")

md(r"""
### 8.1 — *May 2022 TZ1 Paper 1 Q12(b), 4 marks*

The Maclaurin series for $\mathrm{e}^x\sin x$ up to the $x^3$ term is
$x+x^2+\frac{x^3}{3}$ (question 4.1).

Hence, find an approximate value for
$\displaystyle\int_0^1\mathrm{e}^{x^2}\sin\!\left(x^2\right)\mathrm{d}x$.
""")

code(r"""
q8_1 = ...          # exact fraction

check_expr('8.1', q8_1, '""" + D_81 + r"""')
""")

md(r"""
### 8.2 — *May 2024 TZ2 Paper 1 Q12(e), 5 marks*

It has been shown that
$(1-2x)^{-\frac12}(1-4x)^{-\frac12}\approx\frac{2+6x+19x^2}{2}$, valid for
$|x|<\frac14$.

Use $x=\frac{1}{10}$ to determine an approximate value for $\sqrt3$. Give
your answer in the form $\frac{c}{d}$, where $c,d\in\mathbb{Z}^+$.
""")

code(r"""
q8_2 = ...

check_expr('8.2', q8_2, '""" + D_82 + r"""')
""")

md(r"""
### 8.3 — *November 2025 TZ3 Paper 3 Q2(c), 3 marks*

Using $x=\frac{1}{\sqrt3}$ and the first **three** (non-zero) terms of the
Maclaurin series of $\arctan x$, find an approximation for $\pi$ to three
decimal places.
""")

code(r"""
q8_3 = ...

check_num('8.3', q8_3, 4, '""" + D_83 + r"""')
""")

md(r"""
### 8.4 — *November 2025 TZ3 Paper 3 Q2(g), 2 marks*

It has been shown by parts that
$$\int_0^{\frac{1}{\sqrt3}}\arctan x\,\mathrm{d}x
 =\frac{\pi}{6\sqrt3}-\frac12\ln\frac43 ,$$
and the same integral, taken over the first four terms of the series for
$\arctan x$, comes to $0.158422$ (to six decimal places).

Use these two results to find an approximation for $\pi$. Give your answer
to four decimal places.
""")

code(r"""
q8_4 = ...

check_num('8.4', q8_4, 5, '""" + D_84 + r"""')
""")

md(r"""
### 8.5 — *May 2021 TZ1 Paper 3 Q2(e)(i), 3 marks*

The Maclaurin series for $\tan x$ is
$x+\frac{x^3}{3}+\frac{2x^5}{15}+\dots$

Use it to find $\displaystyle\lim_{n\to\infty}\left(4n\tan\frac{\pi}{n}\right)$.
""")

code(r"""
q8_5 = ...

verify_limit('8.5', q8_5, 4*n*tan(pi/n), var=n, point=oo)
""")

md(r"""
### 8.6 — *May 2021 TZ2 Paper 2 Q9(c), 3 marks*

By using the Maclaurin series for $\arctan x$ and the series for $\sec x$
from 5.1, find
$$\lim_{x\to0}\left(\frac{x\arctan 2x}{\sec x-1}\right).$$
""")

code(r"""
q8_6 = ...

verify_limit('8.6', q8_6, x*arctan(2*x)/(sec(x) - 1))
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. How wrong the approximation is

The only place in the archive where the question is not *what does the
series give* but *how far off is it*. It works because the series for
$\arctan x$ alternates and its terms shrink:

> **Theorem.** For alternating series with terms of decreasing magnitude,
> the error obtained in using a finite number of terms is less than or equal
> to the absolute value of the next term in the sequence.

All three questions below turn on the same sentence, and so does the one
mistake everyone makes: the error from $n$ terms is bounded by term
number $n+1$.
""")

md(r"""
### 9.1 — *November 2025 TZ3 Paper 3 Q2(d), 3 marks*

Determine how many (non-zero) terms of the series would need to be used,
such that the error in approximating $\arctan\!\left(\frac{1}{\sqrt3}\right)$
is less than $0.0001$.
""")

code(r"""
# Term number k of the series for arctan(1/sqrt(3)), ignoring its sign.
TERM = (1/sqrt(3))**(2*k - 1) / (2*k - 1)

q9_1 = ...

verify_terms('9.1', q9_1, TERM, 0.0001)
""")

md(r"""
### 9.2 — *November 2025 TZ3 Paper 3 Q2(h), 5 marks*

$$\int_0^{\frac{1}{\sqrt3}}\!\left(x-\frac{x^3}{3}+\frac{x^5}{5}
 -\frac{x^7}{7}+\dots\right)\mathrm{d}x$$
may be considered as the sum of alternating terms, and
$\int_0^{1/\sqrt3}\arctan x\,\mathrm{d}x$ is approximated using the sum of
the **first four** definite integrals — which comes to $0.158422$.

The exact value of the integral is $\frac{\pi}{6\sqrt3}-\frac12\ln\frac43$.

Verify that the theorem holds in this case: state the actual error, and
state the bound the theorem gives.
""")

code(r"""
q9_2 = ...          # the actual error, to two significant figures
q9_3 = ...          # the bound the theorem gives, exactly

check_num('9.2 the error', q9_2, 2, '""" + D_92 + r"""')
check_num('9.2 the bound', q9_3, 3, '""" + D_93 + r"""')
""")

md(r"""
### 9.3 — *November 2025 TZ3 Paper 3 Q2(i), 5 marks*

Suppose that the maximum error in approximating
$\int_0^{1/\sqrt3}\arctan x\,\mathrm{d}x$ is required to be at most
$1\times10^{-6}$.

Determine the smallest number of (non-zero) terms of the Maclaurin series
for $\arctan x$ that should be used.
""")

code(r"""
# Now the terms being added are integrals, not values: term number k is
# the integral of x^(2k-1)/(2k-1) from 0 to 1/sqrt(3).
INTEGRAL = integrate(x**(2*k - 1)/(2*k - 1), (x, 0, 1/sqrt(3)))

q9_4 = ...

verify_terms('9.3', q9_4, INTEGRAL, 1e-6, strict=False)
""")

# ------------------------------------------------------------------ решения
md(r"""
---
# 🔑 Solutions

Numbered as above. Read one after you have worked the question.

---
### 1.1 — *November 2021 P1 Q11(b), 3 marks*

The given formula hands over every derivative at once. Put $x=0$:
$$f^{(n)}(0)=\bigl[0+0+n(n-1)\bigr]\mathrm{e}^0=n(n-1),$$
so $f(0)=0$, $f'(0)=0$, $f''(0)=2$, $f'''(0)=6$, $f^{(4)}(0)=12$, and
$$f(x)=\frac{2}{2!}x^2+\frac{6}{3!}x^3+\frac{12}{4!}x^4+\dots
 =x^2+x^3+\frac{x^4}{2}+\dots$$

The formula is stated for $n\in\mathbb{Z}^+$, so $f(0)$ has to come from
$f$ itself; it is $0$, which is why the series starts at $x^2$.

*Otherwise*: multiply $x^2$ by the series for $\mathrm{e}^x$ and read off
three terms. That is section 4's technique, it is faster here, and the
markscheme allows it — but the question is placed after an induction proof
for a reason, and «hence» is where the marks are.

---
### 1.2 — *May 2022 TZ1 P1 Q12(d), 5 marks*

Substituting $x=0$ turns the two relations into arithmetic. With
$g(x)=\mathrm{e}^x\cos x$: $g(0)=1$ and $g'(0)=1$ (product rule, or
$g'=\mathrm{e}^x(\cos x-\sin x)$). Then

$$g''(0)=2\bigl(g'(0)-g(0)\bigr)=2(1-1)=0,$$
$$g'''(0)=2\bigl(g''(0)-g'(0)\bigr)=2(0-1)=-2,$$
$$g^{(4)}(0)=2\bigl(g'''(0)-g''(0)\bigr)=2(-2-0)=-4,$$

so
$$g(x)=1+x+\frac{0}{2!}x^2-\frac{2}{3!}x^3-\frac{4}{4!}x^4+\dots
 =1+x-\frac{x^3}{3}-\frac{x^4}{6}+\dots$$

The relation $g'''=2(g''-g')$ used in the middle line is not given — it is
the same differentiation done once more, and it is expected.

Note the missing $x^2$: the coefficient really is zero, and an answer that
quietly renumbers the terms to avoid the gap is wrong.

---
### 1.3 — *May 2025 TZ1 P1 Q12(e)(i), 3 marks*

$f_n(x)=\cos^n x$, so $f_n(0)=1$ and
$f_n'(x)=-n\cos^{n-1}x\,\sin x$, which is $0$ at $x=0$. Then
$$f_n''(x)=n(n-1)\cos^{n-2}x\,\sin^2x-n\cos^n x,\qquad f_n''(0)=-n,$$
and
$$f_n(x)=1-\frac{n}{2}x^2+\dots$$

*Otherwise*, and much faster: $\cos x=1-\frac{x^2}{2}+\dots$, so
$\cos^n x=\left(1-\frac{x^2}{2}+\dots\right)^n$, and the binomial expansion
keeps only $1+n\!\left(-\frac{x^2}{2}\right)$ up to $x^2$. That is section 3
doing section 1's work.

The next part of the paper wants
$\lim_{x\to0}\frac{f_n(x)-1}{x^2}$, which is now $-\frac n2$ by inspection —
that part belongs to E1.

---
### 1.4 — *May 2024 TZ2 P1 Q12(b), 2 marks*

From the proved formula, at $x=0$,
$$f^{(n)}(0)=\frac{a^n(2n-1)!}{2^{2n-1}(n-1)!}.$$
So $f'(0)=\frac{a\cdot1!}{2\cdot0!}=\frac a2$ and
$f''(0)=\frac{a^2\cdot3!}{2^3\cdot1!}=\frac{6a^2}{8}=\frac{3a^2}{4}$, and
$$f(x)=1+\frac{a}{2}x+\frac{3a^2}{4}\cdot\frac{x^2}{2!}
 =1+\frac12ax+\frac38a^2x^2 .\qquad\text{{\bf AG}}$$

$f(0)=1$ comes from $f$, not from the formula — the formula starts at
$n=1$. Two marks, and both of them are the division by $n!$: the numbers
$\frac a2$ and $\frac{3a^2}{4}$ are $f'(0)$ and $f''(0)$, not the
coefficients.

*Otherwise*: the binomial series with $p=-\frac12$ and $u=-ax$ gives the
same three terms in one line. The markscheme allows it, and part (a) is
what makes the long way worth the marks.

---
### 2.1 — *May 2024 TZ1 P1 Q8(a)(i), 2 marks*

$\sin u=u-\frac{u^3}{3!}+\dots$ with $u=x^2$:
$$\sin(x^2)=x^2-\frac{(x^2)^3}{3!}+\dots=x^2-\frac{x^6}{6}+\dots$$

**A1** for each term. The whole of the question is $(x^2)^3=x^6$, and the
standard slip is $-\frac{x^3}{6}$ — cubing the exponent instead of the
argument.

The markscheme note that governs all of question 8: *condone presence of
any additional terms once the first two correct terms are seen.*

---
### 2.2 — *November 2023 TZ1 P1 Q11(d)(i), part of 6 marks*

$\cos u=1-\frac{u^2}{2!}+\frac{u^4}{4!}-\dots$ with $u=2x$:
$$\cos 2x=1-\frac{4x^2}{2}+\frac{16x^4}{24}-\dots
 =1-2x^2+\frac{2x^4}{3}-\dots$$

Both the $4$ and the $16$ come from the substitution, and both are where
the marks go. Three terms of the cosine series are needed to reach $x^4$,
not two.

---
### 3.1 — *November 2025 TZ1 P1 Q5(a), 5 marks*

**(i)** With $p=-4$ and $u=-x$: the coefficient of $x$ is
$p\cdot(-1)=4$, so $a=4$. **AG**

The markscheme is firm about this: *do not award the mark for $1+4x$ seen
without clear evidence of a substitution.* Writing down the answer to an
**AG** earns nothing.

**(ii)** The next coefficient is
$$\frac{p(p-1)}{2!}(-x)^2=\frac{(-4)(-5)}{2}x^2=10x^2,$$
so $b=10$. Check against the given $20x^3$:
$\frac{(-4)(-5)(-6)}{6}(-x)^3=20x^3$ — the three minus signs and the one
from $(-x)^3$ cancel, which is why every coefficient of $(1-x)^{-4}$ is
positive.

*Otherwise*, by differentiation: $f'(x)=4(1-x)^{-5}$ gives $f'(0)=4$;
$f''(x)=20(1-x)^{-6}$ gives $f''(0)=20$, and $b=\frac{20}{2!}=10$.

---
### 4.1 — *May 2022 TZ1 P1 Q12(a), 4 marks*

$$\mathrm{e}^x=1+x+\frac{x^2}{2}+\frac{x^3}{6}+\dots,\qquad
 \sin x=x-\frac{x^3}{6}+\dots$$
Multiply, keeping powers up to $x^3$:
$$\mathrm{e}^x\sin x
 =x+x^2+\left(\frac12-\frac16\right)x^3+\dots
 =x+x^2+\frac{x^3}{3}+\dots$$

**M1** for recognising both series, **M1** for the attempt to multiply up to
$x^3$, **A1A1** for the working and the answer.

Note the asymmetry: the exponential needs three terms and the sine two,
because the sine starts at $x$ and every one of its terms is pushed up a
power by the multiplication.

*Otherwise*, the derivatives: $f'=\mathrm{e}^x(\cos x+\sin x)$,
$f''=2\mathrm{e}^x\cos x$, $f'''=2\mathrm{e}^x(\cos x-\sin x)$, giving
$0,1,2,2$ at zero — the same series in four times the work.

---
### 4.2 — *May 2024 TZ1 P1 Q8(a)(ii), 3 marks*

Square the answer to 2.1:
$$\sin^2(x^2)=\left(x^2-\frac{x^6}{6}+\dots\right)^2
 =x^4-2\cdot x^2\cdot\frac{x^6}{6}+\dots=x^4-\frac{x^8}{3}+\dots$$

The middle term is the whole question, and the markscheme says so with an
unusual **M0**: *award M0 for $(x^2)^2-\left(\frac{x^6}{3!}\right)^2$* —
squaring term by term.

*Otherwise*: $\sin^2\theta=\frac{1-\cos2\theta}{2}$ with $\theta=x^2$,
then the cosine series. Same answer, and no cross term to forget.

---
### 4.3 — *May 2024 TZ1 P1 Q8(b), 2 marks*

$4x\sin(x^2)\cos(x^2)=2x\cdot2\sin(x^2)\cos(x^2)=2x\sin(2x^2)$, and
$$2x\sin(2x^2)=2x\left(2x^2-\frac{(2x^2)^3}{6}+\dots\right)
 =4x^3-\frac{8x^7}{3}+\dots$$

*Otherwise, and this is what «hence» means here*: differentiate 4.2.
$\frac{\mathrm{d}}{\mathrm{d}x}\sin^2(x^2)=4x\sin(x^2)\cos(x^2)$, and
differentiating $x^4-\frac{x^8}{3}$ term by term gives
$4x^3-\frac{8x^7}{3}$ in one line. Two marks, thirty seconds.

That is section 6's technique arriving early, and it is the reason parts
(a)(ii) and (b) are next to each other.

---
### 4.4 — *May 2021 TZ1 P1 Q12(c), 8 marks*

$$f(x)=\sqrt{1+x}=1+\frac x2-\frac{x^2}{8}+\dots,\qquad
 g(x)=\mathrm{e}^{mx}=1+mx+\frac{m^2x^2}{2}+\dots$$
The $x^2$ coefficient of the product is
$$\frac{m^2}{2}+\frac12\cdot m+1\cdot\left(-\frac18\right)
 =\frac{m^2}{2}+\frac m2-\frac18 .$$
Set it equal to $\frac74$:
$$\frac{m^2}{2}+\frac m2-\frac18=\frac74
 \;\Longrightarrow\; 4m^2+4m-15=0
 \;\Longrightarrow\; (2m+5)(2m-3)=0,$$
so $m=\frac32$ or $m=-\frac52$.

Eight marks, and the arithmetic of the product is only three of them. The
markscheme's method 3 goes the long way — $h''(0)=f(0)g''(0)+2f'(0)g'(0)
+f''(0)g(0)$ — and lands on $m^2+m-\frac14=\frac72$, the same quadratic
after doubling. Both routes are worth the same; the series route is
shorter, because $f$'s expansion was already needed in parts (a) and (b).

The trap is the factor $2!$. The $x^2$ *coefficient* is $\frac{h''(0)}{2!}$,
and confusing the two turns $\frac74$ into $\frac72$ and the answer into
nonsense.

---
### 4.5 — *May 2024 TZ2 P1 Q12(c), 4 marks*

Take $a=2$ and $a=4$ in the result of 1.4:
$$(1-2x)^{-\frac12}\approx1+x+\frac32x^2,\qquad
 (1-4x)^{-\frac12}\approx1+2x+6x^2 .$$
Multiply, up to $x^2$:
$$1+3x+\left(6+2+\frac32\right)x^2=1+3x+\frac{19}{2}x^2
 =\frac{2+6x+19x^2}{2}.\qquad\text{{\bf AG}}$$

The middle coefficient is $6+2+\frac32$: the $x^2$ of one, the $x\cdot x$
cross term, and the $x^2$ of the other. Dropping the cross term is the
standard loss, and it gives $\frac{15}{2}$.

The form matters. **AG** means the answer as printed, over $2$; an answer
left as $1+3x+\frac{19}{2}x^2$ is the same number and not the same
statement.

---
### 5.1 — *May 2021 TZ2 P2 Q9(b), 4 marks*

$$\sec x=\frac{1}{\cos x}=\frac{1}{1-\left(1-\cos x\right)}
 =\bigl(1+t\bigr)^{-1},\qquad t=\cos x-1 .$$
From the cosine series, $t=-\frac{x^2}{2}+\frac{x^4}{24}-\dots$, and from
part (a), $(1+t)^{-1}=1-t+t^2-\dots$:
$$\sec x=1-\left(-\frac{x^2}{2}+\frac{x^4}{24}\right)
 +\left(-\frac{x^2}{2}\right)^2+\dots
 =1+\frac{x^2}{2}-\frac{x^4}{24}+\frac{x^4}{4}+\dots
 =1+\frac{x^2}{2}+\frac{5x^4}{24}.\qquad\text{{\bf AG}}$$

The $\frac{x^4}{4}$ comes from $t^2$, and it is the mark. Only the
$-\frac{x^2}{2}$ part of $t$ matters inside $t^2$; the $\frac{x^4}{24}$
squared is $x^8$ and out of range.

Everything rests on writing $\cos x$ as $1+t$ with $t\to0$. The expansion
of $(1+t)^{-1}$ is valid for $|t|<1$, and $t=\cos x-1$ is near zero when
$x$ is — which is exactly why the question hands you $(1+t)^{-1}$ in part
(a) rather than letting you loose on $\frac{1}{\cos x}$.

*Otherwise*: four derivatives of $\sec x$. It works and nobody does it
twice.

---
### 5.2 — *November 2023 TZ1 P1 Q11(d)(ii) and (iii), part of 6 marks*

**(ii)** With $u=\cos 2x-1=-2x^2+\frac{2x^4}{3}-\dots$ (from 2.2), which
does vanish at $x=0$:
$$\mathrm{e}^u=1+u+\frac{u^2}{2}+\dots
 =1+\left(-2x^2+\frac{2x^4}{3}\right)+\frac{(-2x^2)^2}{2}+\dots$$
$$=1-2x^2+\frac{2x^4}{3}+2x^4+\dots=1-2x^2+\frac{8x^4}{3}+\dots$$

**(iii)** $\mathrm{e}^{\cos 2x}=\mathrm{e}\cdot\mathrm{e}^{\cos 2x-1}$, so
$$f(x)=\mathrm{e}\left(1-2x^2+\frac{8x^4}{3}\right)+\dots$$
*Write down* — one mark, no working expected, and the whole of it is not
losing the $\mathrm{e}$.

Why the question is built this way: $\mathrm{e}^{\cos 2x}$ cannot be
expanded by substituting into $\mathrm{e}^u$ directly, because at $x=0$ the
exponent is $1$, not $0$, and the series for $\mathrm{e}^u$ is about
$u=0$. Subtracting the $1$ and putting the factor $\mathrm{e}$ back outside
is the only honest route, and part (ii) is there to force it.

The $x^4$ coefficient collects two contributions, $\frac23$ from $u$ and
$2$ from $\frac{u^2}{2}$. Taking only the first term of $u$ inside $u^2$
is fine here — $\left(-2x^2\right)^2=4x^4$ and the cross term is $x^6$ —
but taking only the first term of $u$ *outside* loses $\frac23$.

---
### 6.1 — *November 2025 TZ3 P3 Q2(b), 3 marks*

$\frac{1}{1+x^2}$ is the sum of the geometric series, and it is also
$\frac{\mathrm{d}}{\mathrm{d}x}\arctan x$. So integrate both sides term by
term:
$$\arctan x=\int\left(1-x^2+x^4-x^6+\dots\right)\mathrm{d}x
 =x-\frac{x^3}{3}+\frac{x^5}{5}-\frac{x^7}{7}+\dots+C .$$
Putting $x=0$: $\arctan 0=0=C$, so $C=0$. **AG**

Three marks: the recognition that the sum is $\arctan'$, the term-by-term
integration, and the constant. The constant is a separate mark and it is
the one people skip — «$+C$, and $C=0$ since $\arctan0=0$» is a full line
of the markscheme.

Everything in sections 8 and 9 is this series, so it is worth being able to
produce it rather than recall it.

---
### 6.2 — *May 2024 TZ1 P3 Q1(c)(i), 4 marks*

$$\frac{\mathrm{d}}{\mathrm{d}r}\left(a+ar+ar^2+ar^3+\dots\right)
 =a+2ar+3ar^2+\dots=\sum_{n=1}^{\infty}n\,a\,r^{\,n-1},$$
$$\frac{\mathrm{d}}{\mathrm{d}r}\left(\frac{a}{1-r}\right)
 =\frac{a}{(1-r)^2},$$
so $\displaystyle\sum_{n=1}^{\infty}n\,a\,r^{\,n-1}=\frac{a}{(1-r)^2}$.

The right-hand side is $a(1-r)^{-1}$, and the chain rule contributes the
$-1$ from differentiating $(1-r)$, which cancels the $-1$ from the power.
The square, and the plus sign, both come from there.

$a$ is a constant here — it is the first term, not a function of $r$ — so
it rides along untouched. The next part of the question sets $a=p$ and
$r=1-p$ and gets $\mathrm{E}(X)=\frac1p$; that part is statistics.

---
### 6.3 — *May 2025 TZ1 P2 Q12(c), 5 marks*

**(i)** $f_n(x)=\sum_{r=0}^{n}\left(-2x^2\right)^r$ is geometric with ratio
$-2x^2$. The limit as $n\to\infty$ exists exactly when $|-2x^2|<1$, that is
$x^2<\frac12$, that is $|x|<\frac{1}{\sqrt2}$. So
$$K=\frac{1}{\sqrt2}=\frac{\sqrt2}{2}.$$
*Exact form* is a requirement on the writing: $0.707$ earns nothing.

**(ii)** Inside that domain the sum to infinity is
$$f(x)=\frac{1}{1-(-2x^2)}=\frac{1}{1+2x^2},$$
so $a=1$ and $b=2$.

This is section 6 in reverse. Everywhere else a geometric series is used to
*build* a Maclaurin series; here a Maclaurin series is recognised as
geometric and folded back into the function it came from. Both directions
are the single identity $\frac{1}{1-u}=1+u+u^2+\dots$, and knowing it in
both directions is what the question is testing.

---
### 7.1 — *May 2023 TZ1 P2 Q12(c), 3 marks*

**(i)** From the given values: $y(0)=3$; the equation at $x=0$ gives
$$\left.\frac{\mathrm{d}y}{\mathrm{d}x}\right|_{0}
 =\frac{0-3}{0+1}=-3;$$
and $y''(0)=3$, $y'''(0)=9$ are given. So
$$y=3-3x+\frac{3}{2!}x^2+\frac{9}{3!}x^3+\dots
 =3-3x+\frac32x^2+\frac32x^3+\dots$$

Both $\frac32$'s are the division by a factorial, and both are marks:
$\frac{3}{2!}=\frac32$ and $\frac{9}{3!}=\frac32$. Writing $3x^2+9x^3$ is
the standard loss.

**(ii)** At $x=0.15$:
$$y\approx3-0.45+\frac32(0.0225)+\frac32(0.003375)=2.588\,8125,$$
so $2.58881$ to six significant figures.

Six significant figures is the point of the question. The same $y(0.15)$
is asked three times in this paper — by Euler's method in (a), by this
series, and from the exact solution in (d) — and the three answers differ
in the fourth figure. Rounding early destroys the comparison the question
was built for.

---
### 8.1 — *May 2022 TZ1 P1 Q12(b), 4 marks*

Substituting $x^2$ for $x$ in the series of 4.1:
$$\mathrm{e}^{x^2}\sin\!\left(x^2\right)
 =x^2+x^4+\frac{x^6}{3}+\dots$$
Integrate term by term:
$$\int_0^1\left(x^2+x^4+\frac{x^6}{3}\right)\mathrm{d}x
 =\left[\frac{x^3}{3}+\frac{x^5}{5}+\frac{x^7}{21}\right]_0^1
 =\frac13+\frac15+\frac1{21}=\frac{61}{105}.$$

$\mathrm{e}^{x^2}\sin(x^2)$ has no antiderivative in closed form. That is
not a difficulty in the question — it is the reason for the question, and
the reason the word is *approximate*.

**A1** for the substituted series, **M1** for substituting and integrating,
**A1** for the integrated form, **A1** for $\frac{61}{105}$. The markscheme
note: *condone absence of limits up to this stage* — the limits only have
to appear when you evaluate.

---
### 8.2 — *May 2024 TZ2 P1 Q12(e), 5 marks*

At $x=\frac1{10}$ the approximation gives
$$\frac{2+0.6+0.19}{2}=\frac{2.79}{2}=\frac{279}{200},$$
and the exact left-hand side is
$$\left(\tfrac45\right)^{-\frac12}\left(\tfrac35\right)^{-\frac12}
 =\frac{1}{\sqrt{0.48}}=\frac{10}{\sqrt{48}}=\frac{10}{4\sqrt3}.$$
So
$$\frac{10}{4\sqrt3}\approx\frac{279}{200}
 \;\Longrightarrow\;\frac{1}{\sqrt3}\approx\frac{279}{500}
 \;\Longrightarrow\;\sqrt3\approx\frac{500}{279}.$$

**Worth stopping on.** The same statement rearranged differently gives a
different answer. Writing $\frac{10}{4\sqrt3}$ as $\frac{5\sqrt3}{6}$ first
and *then* solving gives
$$\sqrt3\approx\frac65\cdot\frac{279}{200}=\frac{837}{500}=1.674,$$
against $\frac{500}{279}=1.7921$ from the route above. The true value is
$1.7321$, so the two answers straddle it: one is $3.5\%$ high, the other
$3.4\%$ low. Neither is nonsense and neither is better — they are the same
error pointing in opposite directions.

That is exactly what an approximate equality does when you rearrange it.
The approximation $\frac{279}{200}$ undershoots the exact
$\frac{10}{4\sqrt3}$ by a factor of $0.9665$. If $\sqrt3$ sits in the
denominator when you isolate it, it inherits $\frac{1}{0.9665}$; if you
have moved it to the numerator first, it inherits $0.9665$. An equation
survives being multiplied through by $\sqrt3$; an *approximate* equation
carries its error across with it.

Only one of the two is the markscheme's, and the rule that produces it is
worth keeping: leave $\sqrt3$ where the exact side puts it, and isolate it
on the last line.

The approximation is crude to begin with — $1.395$ against a true
$1.4434$ — because $x=\frac1{10}$ is not that small next to the radius
$\frac14$, and only three terms were kept. A $3.4\%$ error in the product
is a $3.4\%$ error in $\sqrt3$, whichever way round you write it.

---
### 8.3 — *November 2025 TZ3 P3 Q2(c), 3 marks*

$\arctan\frac{1}{\sqrt3}=\frac{\pi}{6}$, so $\pi=6\arctan\frac{1}{\sqrt3}$.
With three terms,
$$\arctan\frac{1}{\sqrt3}\approx\frac{1}{\sqrt3}
 -\frac{1}{3}\left(\frac{1}{\sqrt3}\right)^{3}
 +\frac{1}{5}\left(\frac{1}{\sqrt3}\right)^{5}
 =0.526\,030\dots$$
and $\pi\approx6\times0.526030=3.156$ to three decimal places.

The recognition that $\arctan\frac1{\sqrt3}=\frac\pi6$ is the first mark
and the whole idea: the series computes a number that happens to be a known
fraction of $\pi$, and that is how $\pi$ gets approximated at all.

Three terms is not many — $3.156$ against $3.14159$ — which is what makes
parts (d) to (i) worth asking.

---
### 8.4 — *November 2025 TZ3 P3 Q2(g), 2 marks*

Set the exact value equal to the approximation:
$$\frac{\pi}{6\sqrt3}-\frac12\ln\frac43\approx0.158422 .$$
$\frac12\ln\frac43=0.143841\dots$, so
$$\frac{\pi}{6\sqrt3}\approx0.302263\dots,\qquad
 \pi\approx6\sqrt3\times0.302263=3.1412 .$$

Better than 8.3 by two decimal places, from the same series — because
integrating a series smooths it: each term is divided by one more power,
and the tail shrinks faster.

Four decimal places is asked for, so carry six through the arithmetic. The
approximation $0.158422$ is itself given to six.

---
### 8.5 — *May 2021 TZ1 P3 Q2(e)(i), 3 marks*

Put $u=\frac{\pi}{n}$, which $\to0$ as $n\to\infty$. With
$\tan u=u+\frac{u^3}{3}+\dots$,
$$4n\tan\frac{\pi}{n}
 =4n\left(\frac{\pi}{n}+\frac{\pi^3}{3n^3}+\dots\right)
 =4\pi+\frac{4\pi^3}{3n^2}+\dots\;\longrightarrow\;4\pi .$$

Every term after the first carries $\frac{1}{n^2}$ or smaller, so they all
vanish and the limit is the first term alone.

In the question $4n\tan\frac{\pi}{n}$ is the common value of the area and
the perimeter of a regular $n$-gon with $A=P$; part (e)(ii) asks what
$4\pi$ means, and the answer is the circle — area and circumference of a
circle of radius $2$ are both $4\pi$.

---
### 8.6 — *May 2021 TZ2 P2 Q9(c), 3 marks*

$\arctan 2x=2x-\frac{(2x)^3}{3}+\dots$ and, from 5.1,
$\sec x-1=\frac{x^2}{2}+\frac{5x^4}{24}+\dots$, so
$$\frac{x\arctan 2x}{\sec x-1}
 =\frac{2x^2-\frac{8x^4}{3}+\dots}{\frac{x^2}{2}+\frac{5x^4}{24}+\dots}
 =\frac{2-\frac{8x^2}{3}+\dots}{\frac12+\frac{5x^2}{24}+\dots}
 \;\longrightarrow\;\frac{2}{\frac12}=4 .$$

Cancel $x^2$ from top and bottom and the indeterminacy is gone; what is
left is a ratio of constant terms.

This is a $\frac00$ limit that l'Hôpital would also settle — twice over,
with a second derivative of $\sec x$ on the way. The series route is three
lines because both series were already built in parts (a) and (b), and
*«by using…»* says to use them.

---
### 9.1 — *November 2025 TZ3 P3 Q2(d), 3 marks*

Using $n$ terms leaves out term $n+1$ first, and by the theorem the error is
at most that term. With $x=\frac1{\sqrt3}$, term number $m$ has magnitude
$$\frac{1}{2m-1}\left(\frac{1}{\sqrt3}\right)^{2m-1}.$$
Evaluate:
$$m=4:\ 0.003054,\quad m=5:\ 0.000792,\quad
 m=6:\ 0.000216,\quad m=7:\ 0.000061 .$$
The first one below $0.0001$ is $m=7$, so the last term **kept** is number
$6$: **6 non-zero terms**.

The markscheme allows solving $\frac{1}{2m-1}\left(\frac1{\sqrt3}
\right)^{2m-1}<0.0001$ on the GDC, which gives $m=6.60\dots$, hence
$m=7$ for the first omitted term, hence $6$ terms kept.

Everything in this question is that last step. The number the calculator
prints is the index of the *first term small enough to drop*, and the
answer is one less. The markscheme even lists the two other indexings
students use — $2m+1$ instead of $2m-1$, or $n$ as the exponent — and
gives full marks for each, because they all end at $6$.

---
### 9.2 — *November 2025 TZ3 P3 Q2(h), 5 marks*

**The bound.** The four integrals kept are of $x$, $-\frac{x^3}{3}$,
$\frac{x^5}{5}$, $-\frac{x^7}{7}$; the first one dropped is of
$\frac{x^9}{9}$:
$$\int_0^{\frac{1}{\sqrt3}}\frac{x^9}{9}\,\mathrm{d}x
 =\left[\frac{x^{10}}{90}\right]_0^{\frac{1}{\sqrt3}}
 =\frac{1}{90\cdot3^{5}}=\frac{1}{21870}=4.57\times10^{-5}.$$

**The actual error.** The exact value is
$\frac{\pi}{6\sqrt3}-\frac12\ln\frac43=0.158458558\dots$, and the
approximation is $0.158422$, so
$$\text{error}=0.158458558\dots-0.158422=3.69\times10^{-5}.$$

**The comparison.** $3.69\times10^{-5}<4.57\times10^{-5}$, so the theorem
holds. **AG**

Two significant figures is what the cell asks for, and deliberately: using
the *unrounded* value from part (f) instead of $0.158422$ gives
$3.73\times10^{-5}$, and the markscheme accepts both. They differ in the
third figure and agree in the first two.

The **R1** is the comparison itself. Producing both numbers and not writing
the inequality loses it.

---
### 9.3 — *November 2025 TZ3 P3 Q2(i), 5 marks*

Now the alternating terms are integrals. Term number $m$ is
$$\int_0^{\frac{1}{\sqrt3}}\frac{x^{2m-1}}{2m-1}\,\mathrm{d}x
 =\frac{1}{2m(2m-1)}\left(\frac{1}{\sqrt3}\right)^{2m}
 =\frac{1}{2m(2m-1)\,3^{m}} .$$
Require this to be at most $1\times10^{-6}$:
$$m=6:\ 1.04\times10^{-5},\qquad
 m=7:\ 2.51\times10^{-6},\qquad
 m=8:\ 6.35\times10^{-7}.$$
The first term small enough to drop is $m=8$, so **7 non-zero terms** are
needed.

The markscheme's route is the same with a continuous variable: solving
$\frac{(1/\sqrt3)^{n+1}}{n(n+1)}<10^{-6}$ gives $n=14.33\dots$, so
$n=15$ — that is the *power*, $x^{15}$, which is the $8$th non-zero term,
so seven terms are kept.

Two conversions in a row, and both are off-by-one: power $\to$ term number
$\to$ terms kept. It is a five-mark question and four of the marks are
arithmetic; the fifth is arriving at $7$ rather than $8$ or $15$.

Compare with 9.1: there the terms were $\frac{x^{2m-1}}{2m-1}$ and six were
needed for $10^{-4}$; here the integration divides each term by one more
power of $\sqrt3$ and by $2m$, and seven terms buy a bound a hundred times
tighter. That is the same effect that made 8.4 beat 8.3.
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
