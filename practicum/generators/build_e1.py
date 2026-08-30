"""Собирает практикум E1 (пределы, неопределённости, правило Лопиталя) в .ipynb.

Пятый практикум серии на английском: ноутбук целиком английский, kit
переключается вызовом language('en') в установочной ячейке. Документация
репозитория (карта, PRACTICUM.md, этот заголовок) остаётся русской.

Тема даёт десятое понятие равенства ответов: ответ здесь — предел, а у
предела нет числа, которое можно взять и сравнить. Он определён тем, к чему
выражение подходит, — и проверка подходит вместе с ним. verify_limit
подставляет в само выражение из условия точки, приближающиеся к искомой, и
требует, чтобы названное число оказалось тем, к чему эти значения сходятся.
Эталона не хранится вовсе.

Второй новой проверкой стала verify_indeterminate. «Show that the limit is
in indeterminate form» стоит в архиве отдельным баллом дважды, и балл этот
за проверку, а не за вычисление: без неё правило Лопиталя неприменимо, а
второе его применение без повторной проверки — стандартная потеря баллов.
Проверка смотрит на числитель и знаменатель порознь и не верит на слово.

Обе живут в kit.py и проверены в tests/test_kit_limit.py.
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

R = sp.Rational
x, t, b, n, m, c, alpha = sp.symbols('x t b n m c alpha')

NOTEBOOK = os.path.join(ROOT, 'practicum/calculus/practicum-e1-limits.ipynb')


def dn(value, sf=6):
    return digest(sig(value, sf))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_e1.py ---
# Хешей в этой теме мало и меньше быть не может: предел проверяется
# приближением к нему, а не сверкой с числом, и почти каждый ответ уходит
# в verify_limit. Хеш остаётся там, где ответ — не сам предел: постоянная,
# подобранная под него, и число, снятое с калькулятора.
D_9C = dn(4, 1)                    # k в sin^2(kx)/x^2 -> 16
D_8C = dn(9, 1)                    # k плотности k t e^{-3t}
D_10C = dn(sp.pi / 4, 6)           # предельный угол между u и v
# Два ряда Маклорена: ответ прячется, потому что вопрос просит именно его.
D_6A = digest(kit._series_canon(1 + x - x**3 / 3 - x**4 / 6, x, 6))
D_7B = digest(kit._series_canon(1 - n * x**2 / 2, x, 6))

TRIGGER = {1: 'substitute', 2: 'infinity', 3: 'context', 4: 'lhopital',
           5: 'again', 6: 'series', 7: 'finite', 8: 'parameter',
           9: 'substitute', 10: 'lhopital', 11: 'infinity', 12: 'symbolic'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

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
# Practicum E1: limits, indeterminate forms, l'Hôpital's rule

**73 marks, 20 blocks, nine techniques.** The whole topic is one
question asked over and over: *what does this expression approach?* You
answer it by substituting. When substituting works, you are finished in
one line. When it gives $\frac00$ or $\frac{\infty}{\infty}$ you have
learned nothing yet — and everything else in this practicum is what to
do next.

**Material.** All of `calculus.limits` from the AA HL archive, sessions
May 2021 — November 2025. Twenty-two blocks in the corpus, of which two
are duplicates: November 2023 Paper 3 is one paper filed under both
zones, and the November 2023 Paper 1 question on $\sin^2(kx)/x^2$ was
set in TZ1 and TZ2 word for word.

**This practicum is in English,** like B2 to B5. The checks speak
whichever language the notebook asks them to, and this one asks for
English in the setup cell.

**The one thing to carry out of here.**

> Substitute **first**, always. If it gives a number, that is the limit
> and you are done. If it gives $\frac00$ or $\frac{\infty}{\infty}$,
> you have a licence to differentiate — and not before.

That order is not pedantry, it is where the marks are. May 2025 TZ2 is
worth five marks for a limit whose value is $0$, and the first of them
is for rewriting $(3x+1)e^{-3x}$ as $\dfrac{3x+1}{e^{3x}}$ — because a
product is not a quotient, and l'Hôpital's rule applies to quotients.
The markscheme says so in as many words: *"This first A1 must be seen."*

**Where the calculator sits, and here it barely matters.** 44% of the
marks carry one, and almost none of them use it. The answers in this
topic are $\frac23$, $-3$, $-\frac14$, $\frac{\pi}{4}$, $-\frac{n}{2}$,
$\frac12 n(n+1)$ — exact things. The two questions that do want a number
want it from an integral, not from the limit.

**How the checks work here.** Two of them are new, and the first one is
the reason this practicum exists.

* `verify_limit` does not know the answer. It takes the expression from
  the question, walks in towards the point along a ladder —
  $10^{-1}, 10^{-2}, \dots, 10^{-8}$, from both sides — and asks whether
  the number you named is what those values are settling on. There is no
  stored constant anywhere: it cannot be wrong in the same way you are,
  because there is nothing for it to be wrong about.

  It also catches the two standard losses. An answer with $x$ still in
  it is rejected on sight — a limit is a number, not an expression. And
  an answer read off after one round of l'Hôpital when the form was
  still $\frac00$ simply does not converge to what you wrote.

* `verify_indeterminate` is for *"show that the limit is in
  indeterminate form"*, which is worth its own mark twice in this
  archive. It looks at the numerator and at the denominator separately
  and tells you which way each one is actually going. Claiming
  $\frac00$ where the truth is $\frac{\infty}{\infty}$ does not pass.

**How to work**

1. Read the map of techniques first. It is arranged by **what
   substituting gave you**.
2. Work **on paper**. Every limit in this topic is a Paper 1 answer even
   when it appears on Paper 2.
3. Exact answers throughout: `Rational(2, 3)`, `-pi/4`, `-n/2`,
   `n*(n+1)/2`. `oo` for an infinite limit.
4. The value of a limit is entered as a plain expression — no `lim`, no
   `x` in it.
5. A form is entered as a string: `'0/0'` or `'oo/oo'`.
6. The last three blocks are a whole Paper 3 part, a recognition
   trainer, and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/calculus to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Rational, oo, pi, limit-free tools

language('en')                 # this notebook is in English, and so are the checks

b, c, m, n = symbols('b c m n')
alpha = symbols('alpha')

print('ready; sympy', sp.__version__)
print('an exact limit:      ', Rational(2, 3))
print('a limit in terms of n:', -n/2)
print('an infinite limit:   ', oo)
print("a form, as a string: ", '0/0')
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | Substitute, and cancel | the point is in the domain, or $\frac00$ from a shared factor | put the number in; factorise if it stops you |
| 2 | Highest power | $x\to\infty$ and no exponentials | divide top and bottom by it |
| 3 | l'Hôpital once | $\frac00$ or $\frac{\infty}{\infty}$, nothing to cancel | differentiate top and bottom **separately** |
| 4 | l'Hôpital again | the denominator is $x^3$, $x^4$, a high power | check the form again before repeating |
| 5 | Maclaurin instead | $e$, $\sin$, $\cos$, $\ln$ around $0$ | replace each factor by its series |
| 6 | Choose the constant | a letter in the question, «a finite limit only exists» | force the numerator to vanish |
| 7 | Limit in a parameter | $n\to\infty$ or $\alpha\to\frac{\pi}{2}$, with $x$ held fixed | ask what survives |
| 8 | The rule with a letter in it | $x^{n+2}$, $S_n(x)$ — a parameter inside the expression | differentiate in $x$, carrying $n$ along |
| 9 | What it means | «state a reason», «explain the significance» | answer about the model, not the algebra |

**The ladder goes by what substituting gave you.**

**Rungs 1–2 — substituting settled it.** Either the point is in the
domain and the limit is the value, or the $\frac00$ came from a factor
you can cancel, or the point is at infinity and only the highest powers
matter. None of these needs calculus. Do not reach for l'Hôpital's rule
here: it would give the right answer, but slower, and on a question
worth one mark that is the whole of the time you had.

**Rungs 3–5 — substituting gave $\frac00$ and there is nothing to
cancel.** This is the middle of the topic and nine of the twenty blocks.
Rung 3 is the rule itself. Rung 4 is the discipline around it: after
differentiating, *look again* — the form is often still $\frac00$, and
the markscheme for May 2024 will not give you the mark unless the second
application is justified. Rung 5 is the alternative the Paper 1
questions are really built for: when the expression is made of $e^x$,
$\sin$, $\cos$ around zero, its Maclaurin series answers in one line
what l'Hôpital answers in three.

**Rungs 6–8 — the limit is not quite the question.** Rung 6 hands you a
letter and tells you the limit is finite; you work backwards to the
letter. Rung 7 takes the limit in something other than $x$ — in $n$, in
$\alpha$ — while $x$ sits there unmoved, and the answer is an expression
in the letters that stayed. Rung 8 keeps the limit in $x$ but leaves a
parameter inside the expression, so the differentiation carries $n$
along and the answer is a formula: $\frac12 n(n+1)$, or simply $1$ for
every $n$ at once.

**Rung 9 — the sentence at the end.** Two marks in the archive are for
saying what the limit means: that a sprinter's speed never reaches
$8.14\ \mathrm{m\,s^{-1}}$ because the race ends first, that a parabola
looks straight from far enough away. They are the easiest marks in the
topic and the ones most often left blank.

**What saves the most time.** Write $\lim_{x\to a}$ on *every* line. It
looks like decoration and it is not: May 2021 caps the question at
**M1A1A0M1A1** — four marks out of five — for a perfect solution with
the symbol missing, and November 2022 refuses the mark for the
indeterminate form outright if $\lim$ is not written.
""")

md(r"""
---
# Part I — when substituting is enough

---
## Theory 1. What the notation asks, and why substituting comes first

$$\lim_{x\to a}f(x)=L$$

says: *as $x$ gets close to $a$, $f(x)$ gets close to $L$* — and it says
nothing whatever about $f(a)$. That gap is the whole subject. $f(a)$ may
be a different number, or may not exist at all, and the limit is fine
either way.

**But when the function is continuous at $a$, the gap closes** and
$\lim_{x\to a}f(x)=f(a)$. Every function you meet in this course —
polynomials, $e^x$, $\sin$, $\cos$, $\ln$ on its domain, and sums,
products and quotients of them where the denominator is not zero — is
continuous. So *substitute first* is not a shortcut. It is the theorem.

**The $\frac00$ you get is not an answer, and not a failure either.** It
is a diagnosis: the numerator and denominator are both dying at $a$, and
the limit is a statement about *which of them dies faster*. Nothing about
$\frac00$ tells you the answer — it can come out to $0$, to $\frac23$,
to $-3$, or to $\infty$. That is exactly why it is called
*indeterminate*.

**The first cure: they are dying because of a shared factor.** In
May 2024 TZ1 the function is
$$f(x)=\frac{P(x)}{(x+1)Q(x)},\qquad
  P(x)=3x^3+5x^2+x-1,\quad Q(x)=(x+1)(2x+1),$$
and substituting $x=-1$ gives $\frac00$. But $P(x)=(x+1)^2(3x-1)$, so
$$f(x)=\frac{(x+1)^2(3x-1)}{(x+1)^2(2x+1)}=\frac{3x-1}{2x+1}
  \qquad\text{for }x\ne-1,$$
and now substituting works. The cancelled factor is exactly the shared
cause of death. Note the phrase *for $x\ne -1$*: the two functions are
not equal at $-1$, and that is precisely why the limit exists where the
value does not.
""")

md(r"""
## Task 1 🟢 — substitute, and cancel what stops you

Consider the polynomials
$$P(x)=3x^3+5x^2+x-1,\qquad Q(x)=(x+1)(2x+1),$$
and the function
$$f(x)=\frac{P(x)}{(x+1)Q(x)},\qquad x\ne-1,\ x\ne-\tfrac12 .$$

**(a)** Express $P(x)$ as a product of three linear factors.

**(b)** Find $\displaystyle\lim_{x\to-1}f(x)$.

The check for (b) has no stored answer. It takes $f$ as the question
defines it, walks in towards $-1$ from both sides, and asks whether your
number is what the values are settling on.

*May 2024 TZ1 Paper 1 Q11(b) and Q11(f)(i) — 3 marks and part of 3.*
""")

code(r"""
FX = (3*x**3 + 5*x**2 + x - 1) / ((x + 1) * (x + 1) * (2*x + 1))   # f as given

q1a = ...        # the cubic as a product of three linear factors
q1b = ...        # the limit as x -> -1

verify_factored('1a', q1a, 3*x**3 + 5*x**2 + x - 1, n=3)
verify_limit('1b', q1b, FX, point=-1)
""")

md(r"""
---
## Theory 2. At infinity: only the highest power is alive

$x\to\infty$ is not a point you can substitute into, so the rule is
different — but it is just as mechanical. **Divide the numerator and the
denominator by the highest power of $x$ that appears**, and then use
$\dfrac{1}{x^k}\to 0$.

$$\frac{3x-1}{2x+1}
  =\frac{3-\frac1x}{2+\frac1x}\;\longrightarrow\;\frac{3-0}{2+0}=\frac32 .$$

Everything except the leading terms has died. That is the whole of the
technique, and it gives the three cases at once:

| top vs bottom | example | limit |
| --- | --- | --- |
| same degree | $\dfrac{3x-1}{2x+1}$ | ratio of leading coefficients, $\frac32$ |
| bottom wins | $\dfrac{2x+5}{x^2}$ | $0$ |
| top wins | $\dfrac{x^2}{2x+5}$ | $\infty$ — no limit |

**Roots count as powers.** May 2025 TZ3 models a sprinter's velocity by
$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}} .$$
Under the root, $t^2+0.2$ behaves like $t^2$, so $\sqrt{t^2+0.2}$
behaves like $t$: top and bottom are both degree one and the limit is
$8.14$. Written out,
$$\frac{8.14\,t}{\sqrt{t^2+0.2}}
 =\frac{8.14}{\sqrt{1+\frac{0.2}{t^2}}}\;\longrightarrow\;8.14 .$$

**Exponentials are not powers, and they beat every power.** $e^{x}$
outgrows $x^{100}$; $e^{-x}$ dies faster than $\frac{1}{x^{100}}$. So
$\dfrac{3x+1}{e^{3x}}\to 0$ and $\dfrac{e^{b}-b-1}{e^{b}}\to 1$ — but
neither of those is settled by dividing by a power, and both are in
Part II.
""")

md(r"""
## Task 2 🟢 — the far end

**(a)** With $f$ as in Task 1, find $\displaystyle\lim_{x\to\infty}f(x)$.

Two athletes run a $200$ m race. Fiona's velocity, in $\mathrm{m\,s^{-1}}$,
is modelled by
$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}},\qquad t\ge 0 .$$

**(b)** Write down the limit of $v(t)$ as $t$ approaches infinity.

*May 2024 TZ1 Paper 1 Q11(f)(ii) — part of 3 marks. May 2025 TZ3
Paper 2 Q10(c)(i) — part of 3 marks.*
""")

code(r"""
VT = Rational(814, 100)*t / sqrt(t**2 + Rational(2, 10))

q2a = ...        # the limit of f as x -> oo
q2b = ...        # the limit of v as t -> oo

verify_limit('2a', q2a, FX, point=oo)
verify_limit('2b', q2b, VT, var=t, point=oo)
""")

md(r"""
---
## Theory 3. The sentence at the end: what a limit means

Two of the archive's marks are not for a number at all. They are for one
sentence about what the number means, and both are worth as much as a
line of algebra.

**A limit the model never reaches.** Fiona's velocity tends to
$8.14\ \mathrm{m\,s^{-1}}$ as $t\to\infty$. The examiner then asks: *why
is this value not valid in the context of the question?* It is a race
over $200$ metres. It is over in about $26$ seconds; $t$ never gets
anywhere near infinity, and Fiona never runs at $8.14$. The limit
describes the formula, and the formula stops describing Fiona when she
crosses the line.

**A limit that says what a shape looks like from far away.** May 2025
TZ1 defines the *curvature* of a graph,
$$k(x)=\frac{|f''(x)|}{\bigl(1+(f'(x))^2\bigr)^{3/2}},$$
and for a quadratic $h(x)=ax^2+bx+c$ works out
$$k(x)=\frac{2|a|}{\bigl(1+(2ax+b)^2\bigr)^{3/2}} .$$
Then: *state $\lim_{x\to\infty}k(x)$ and explain briefly the
significance of this result.* The value is $0$, and the significance is
that far out along a parabola the curving has all but stopped — for
large $x$ a quadratic is nearly straight. One mark for the $0$, one for
the sentence.

**How to write these.** Say what happens to the *thing being modelled*,
not to the algebra. "The denominator grows without bound" earns nothing.
"The race is over long before then" earns the mark.
""")

md(r"""
## Task 3 🟡 — the number and the sentence

Fiona's velocity is $v(t)=\dfrac{8.14\,t}{\sqrt{t^2+0.2}}$, as in
Task 2, in a $200$ m race.

**(a)** State a reason why the value in Task 2(b) is not valid in the
context of this question.

For a quadratic $h(x)=ax^2+bx+c$ with $a\ne 0$, the curvature is
$$k(x)=\frac{2|a|}{\bigl(1+(2ax+b)^2\bigr)^{3/2}} .$$

**(b)** State the value of $\displaystyle\lim_{x\to\infty}k(x)$.

**(c)** Explain briefly the significance of this result.

Parts (a) and (c) are sentences, and no cell can mark a sentence. Write
them in the markdown cell below in one line each, then compare with the
solution — the point is whether you talked about the runner and the
parabola or about the algebra.

*May 2025 TZ3 Paper 2 Q10(c)(ii) — part of 3 marks. May 2025 TZ1
Paper 3 Q2(b)(iii) — 2 marks.*
""")

code(r"""
a = symbols('a')
KX = 2*abs(a) / (1 + (2*a*x + b)**2)**Rational(3, 2)

q3b = ...        # the limit of the curvature as x -> oo

verify_limit('3b', q3b, KX, point=oo, params={a: (2, -3), b: (5, 0)})
""")

md(r"""
**(a)** *your sentence here*

**(c)** *your sentence here*
""")

md(r"""
---
# Part II — when substituting gives $\frac00$

---
## Theory 4. l'Hôpital's rule, and the licence it needs

> If $\displaystyle\lim_{x\to a}\frac{f(x)}{g(x)}$ has the form
> $\dfrac00$ or $\dfrac{\infty}{\infty}$, then
> $$\lim_{x\to a}\frac{f(x)}{g(x)}=\lim_{x\to a}\frac{f'(x)}{g'(x)}$$
> whenever the limit on the right exists.

**Three things about it that cost marks.**

**It is not the quotient rule.** You differentiate the top, you
differentiate the bottom, and you put one over the other. Nothing is
subtracted, nothing is squared.

**The licence has to be shown.** The rule is only true for those two
forms. Substituting first is what earns the right to use it, and the
markschemes are explicit: November 2022 gives a mark purely for writing
$\lim_{x\to1}f_1(x)=\frac{n-(n+1)+1}{0}=\frac00$, and refuses it if the
$\lim$ symbol is not there.

**It applies to quotients only.** May 2025 TZ2 asks for
$\lim_{x\to\infty}(3x+1)e^{-3x}$, which is a *product* of the form
$\infty\cdot 0$. No rule applies to it until it is rewritten:
$$(3x+1)e^{-3x}=\frac{3x+1}{e^{3x}}\qquad\text{— now it is }
\frac{\infty}{\infty},$$
and the markscheme awards its first mark for that rewrite alone.

**A worked one, in full.** May 2021 TZ1:
$$\lim_{x\to0}\frac{\arctan 2x}{\tan 3x}
  \;=\;\frac{\arctan 0}{\tan 0}=\frac00\ \checkmark
  \;=\;\lim_{x\to0}\frac{\dfrac{2}{1+4x^2}}{3\sec^2 3x}
  \;=\;\frac{2/1}{3\cdot 1}=\frac23 .$$
Five marks: one for attempting to differentiate top and bottom, one for
each derivative, one for substituting, one for $\frac23$. Write the
$\lim$ on every line or the maximum drops to four.
""")

md(r"""
## Task 4 🟢 — the rule, once

**(a)** Show that $\displaystyle\lim_{x\to 0}\frac{\arctan 2x}{\tan 3x}$
is in indeterminate form, and name the form.

**(b)** Use l'Hôpital's rule to find
$\displaystyle\lim_{x\to 0}\frac{\arctan 2x}{\tan 3x}$.

For (a) the form is entered as a string, `'0/0'` or `'oo/oo'`. The check
looks at the numerator and the denominator separately and will tell you
which way each one is really going.

*May 2021 TZ1 Paper 1 Q8 — 5 marks.*
""")

code(r"""
q4a = ...        # the form, as a string: '0/0' or 'oo/oo'
q4b = ...        # the limit

verify_indeterminate('4a', q4a, atan(2*x), tan(3*x))
verify_limit('4b', q4b, atan(2*x)/tan(3*x))
""")

md(r"""
---
## Theory 5. Applying it again — and knowing when to stop

After one round you have a new quotient, and the first thing to do with
it is the first thing you did with the old one: **substitute**. Three
outcomes.

* **A number.** That is the limit. Stop.
* **$\frac00$ or $\frac{\infty}{\infty}$ again.** New licence, apply the
  rule again.
* **Something like $\frac{-2}{-2}$ or $\frac{3}{0}$.** Not
  indeterminate. Stop, and read the answer off. Applying the rule here
  is not merely wasteful — it gives the wrong number.

May 2024 TZ2 makes the point explicitly. The question is
$$\lim_{x\to0}\frac{\sec^4x-\cos^2x}{x^4-x^2},$$
which needs two rounds; after the second the denominator is $12x^2-2$,
which at $x=0$ is $-2$. The markscheme's note reads: *M1 for second use
of l'Hôpital's rule provided expression is in indeterminate $\frac00$
form and no third attempt at using the rule.* A third round costs the
mark.

**How many rounds to expect, at a glance.** Look at the denominator. A
denominator of $x^2$ usually takes two rounds, $x^3$ three, $x^4$ four —
each round lowers the power by one, and the limit becomes visible when
the denominator finally survives substitution. So
$$\lim_{x\to0}\frac{e^x\cos x-1-x}{x^3}$$
is a three-round question before you start, and if that sounds like a
lot of trigonometric differentiation — it is, and Theory 6 is the way
round it.
""")

md(r"""
## Task 5 🟡 — twice, and stop

Use l'Hôpital's rule to find
$$\lim_{x\to 0}\frac{\sec^4 x-\cos^2 x}{x^4-x^2}.$$

Six marks, no calculator. Differentiate carefully — $\sec^4x$ needs the
chain rule, and the whole question is lost in that one derivative.

*May 2024 TZ2 Paper 1 Q8 — 6 marks.*
""")

code(r"""
q5 = ...         # the limit

verify_limit('5', q5, (sec(x)**4 - cos(x)**2)/(x**4 - x**2))
""")

md(r"""
## Task 6 🔴 — three rounds, or one line

The function $g$ is defined by $g(x)=e^x\cos x$, $x\in\mathbb{R}$.

**(a)** Find the Maclaurin series for $g(x)$ up to and including the
$x^4$ term.

**(b)** Hence, or otherwise, determine the value of
$$\lim_{x\to 0}\frac{e^x\cos x-1-x}{x^3}.$$

Do (b) both ways if you have time — first with l'Hôpital three times,
then with the series from (a). The second way is four lines and the
first is a page, and knowing that in the exam is worth more than the
answer.

*May 2022 TZ1 Paper 1 Q12(d) and Q12(e) — 5 marks and 3 marks.*
""")

code(r"""
q6a = ...        # the Maclaurin series of e^x cos x up to the x^4 term
q6b = ...        # the limit

check_series('6a', q6a, D_6A)
verify_limit('6b', q6b, (exp(x)*cos(x) - 1 - x)/x**3)
""".replace('D_6A', repr(D_6A)))

md(r"""
---
## Theory 6. Maclaurin instead: read the leading term

Every function in this topic has a series you already know:

$$e^x=1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\dots,\qquad
  \sin x=x-\frac{x^3}{3!}+\dots,\qquad
  \cos x=1-\frac{x^2}{2!}+\frac{x^4}{4!}-\dots$$

Near $0$, a series *is* the function, and a quotient of series is
settled by looking at the lowest power that survives on each side.

**Why it wins.** l'Hôpital differentiates the whole expression, again
and again, and every round doubles the mess. The series is built once
and then you read it. Compare, on the same question:

$$e^x\cos x=1+x+\frac{x^2}{2}\cdot 0 - \frac{x^3}{3}+\dots
  \;\Longrightarrow\;
  \frac{e^x\cos x-1-x}{x^3}=\frac{-\frac{x^3}{3}+\dots}{x^3}
  \longrightarrow -\frac13 .$$

The numerator's first three terms are $1+x+0\cdot x^2$, which is exactly
why the question subtracts $1+x$: it is clearing everything above the
$x^3$ you are dividing by.

**The version that looks impossible and is not.** November 2021 asks for
$$\lim_{x\to0}\frac{\bigl(x^2e^x-x^2\bigr)^3}{x^9}.$$
A ninth power. But $x^9=(x^3)^3$, so the whole thing is a cube:
$$\frac{\bigl(x^2e^x-x^2\bigr)^3}{x^9}
 =\left(\frac{x^2e^x-x^2}{x^3}\right)^{3}
 =\left(\frac{e^x-1}{x}\right)^{3}
 \longrightarrow 1^3=1,$$
because $e^x-1=x+\frac{x^2}{2}+\dots$ and dividing by $x$ leaves
$1+\frac{x}{2}+\dots\to 1$. Pull the power out first, always.

**With a parameter in the exponent.** May 2025 TZ1 has
$f_n(x)=\cos^n x$ and asks for $\lim_{x\to0}\frac{f_n(x)-1}{x^2}$ in
terms of $n$. Raise the series:
$$\cos^n x=\left(1-\frac{x^2}{2}+\dots\right)^{n}
 =1-\frac{nx^2}{2}+\dots
 \;\Longrightarrow\;\frac{f_n(x)-1}{x^2}\longrightarrow-\frac n2 .$$
Only the first two terms of the binomial matter, because everything
after them carries $x^4$.
""")

md(r"""
## Task 7 🟡 — pull the power out, keep the parameter

**(a)** Determine the value of
$\displaystyle\lim_{x\to 0}\frac{\bigl(x^2e^x-x^2\bigr)^3}{x^9}$.

Let $f_n(x)=\cos^n x$, where $x\in\mathbb{R}$ and $n\in\mathbb{N}$.

**(b)** Find the Maclaurin series of $f_n(x)$ up to the term in $x^2$.

**(c)** Hence or otherwise, find
$\displaystyle\lim_{x\to 0}\frac{f_n(x)-1}{x^2}$ in terms of $n$.

The check for (c) takes your answer, puts $n=1,2,5,9$ into it in turn,
and walks in on $\cos^n x$ each time. An answer that happens to work for
one $n$ will not survive the others.

*November 2021 Paper 1 Q11(c) — 4 marks. May 2025 TZ1 Paper 1 Q12(e) —
5 marks.*
""")

code(r"""
q7a = ...        # the limit of (x^2 e^x - x^2)^3 / x^9
q7b = ...        # the Maclaurin series of cos^n x up to x^2, in terms of n
q7c = ...        # the limit of (cos^n x - 1)/x^2, in terms of n

verify_limit('7a', q7a, (x**2*exp(x) - x**2)**3 / x**9)
check_series('7b', q7b, D_7B)
verify_limit('7c', q7c, (cos(x)**n - 1)/x**2, params={n: (1, 2, 5, 9)})
""".replace('D_7B', repr(D_7B)))

md(r"""
---
## Theory 7. $\frac{\infty}{\infty}$, and the forms that must be rearranged

The rule takes $\frac{\infty}{\infty}$ on exactly the same terms as
$\frac00$, and at infinity that is usually the form you meet.

**A worked one.** May 2023 TZ1 Paper 3 arrives at the area
$\dfrac{e^b-b-1}{e^b}$ under $xe^{-x}$ up to $x=b$, and asks for its
limit as $b\to\infty$. Both parts run away to infinity, so:
$$\lim_{b\to\infty}\frac{e^b-b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b}{e^b}=1 .$$
Two rounds, two marks, and the answer says the total area under
$xe^{-x}$ from $0$ to $\infty$ is exactly $1$.

**The rearrangements you must know.** The rule reads quotients. Anything
else is rewritten first, and the rewrite is where the mark is.

| what you have | form | rewrite as |
| --- | --- | --- |
| $(3x+1)e^{-3x}$ | $\infty\cdot 0$ | $\dfrac{3x+1}{e^{3x}}$ |
| $x\ln x$, $x\to0^+$ | $0\cdot(-\infty)$ | $\dfrac{\ln x}{1/x}$ |
| $\dfrac{1}{x}-\dfrac{1}{\sin x}$ | $\infty-\infty$ | one fraction |

Put the factor that dies into the denominator, upside down. That is the
whole of the trick.

**And what the answer is then used for.** In May 2025 TZ2 the limit is
not the point. $f(t)=kte^{-3t}$ is a probability density function, and
$$\int_0^{a}f(t)\,dt=\frac k9\Bigl[1-(3a+1)e^{-3a}\Bigr].$$
Because $(3a+1)e^{-3a}\to 0$, the total probability is $\frac k9$; and a
density integrates to $1$; so $k=9$. The limit was one step inside a
five-mark chain.
""")

md(r"""
## Task 8 🟡 — the other indeterminate form

**(a)** Use l'Hôpital's rule to find
$\displaystyle\lim_{b\to\infty}\frac{e^b-b-1}{e^b}$. You may assume that
the condition for applying the rule has been met.

The time $T$, in minutes, that a spinning top is in motion is modelled
by the probability density function
$$f(t)=\begin{cases}kte^{-3t}, & t\ge 0\\ 0,&\text{otherwise}\end{cases}
  \qquad k\in\mathbb{Z}^{+},$$
and it is given that
$\displaystyle\int_0^{a}f(t)\,dt=\frac k9\Bigl[1-(3a+1)e^{-3a}\Bigr]$.

**(b)** Use l'Hôpital's rule to find
$\displaystyle\lim_{x\to\infty}(3x+1)e^{-3x}$.

**(c)** Hence, by considering
$\displaystyle\lim_{a\to\infty}\int_0^{a}f(t)\,dt$, find the value of
$k$.

*May 2023 TZ1 Paper 3 Q1(c)(i) — 2 marks. May 2025 TZ2 Paper 2 Q11(c) —
5 marks.*
""")

code(r"""
q8a = ...        # the limit as b -> oo
q8b = ...        # the limit as x -> oo
q8c = ...        # the value of k

verify_limit('8a', q8a, (exp(b) - b - 1)/exp(b), var=b, point=oo)
verify_limit('8b', q8b, (3*x + 1)*exp(-3*x), point=oo)
check_num('8c', q8c, 1, D_8C)
""".replace('D_8C', repr(D_8C)))

md(r"""
---
# Part III — when the limit is not the question

---
## Theory 8. Choosing the constant that makes a limit exist

Sometimes the letter is the answer. The question hands you an unknown
constant and tells you the limit is finite; you work backwards.

**The reasoning, in one move.** Consider
$$\lim_{x\to0}\frac{\arctan(\cos x)-k}{x^2},\qquad k\in\mathbb{R}.$$
The denominator goes to $0$. If the numerator went to anything other
than $0$, the quotient would run away to $\pm\infty$ and there would be
no finite limit. So a finite limit **requires** $\frac00$:
$$\lim_{x\to0}\bigl(\arctan(\cos x)-k\bigr)=0
 \;\Longrightarrow\;\arctan 1-k=0
 \;\Longrightarrow\;k=\frac{\pi}{4}.$$
Two marks, and the second one is for $\arctan 1=\frac\pi4$ rather than
for the reasoning. The markscheme's warning is worth reading twice:
*award M1A0 for using $k=\frac\pi4$ to show the limit is $\frac00$* —
that is the argument backwards, and it earns half.

**The same idea from the other end.** November 2023 gives
$f(x)=\dfrac{\sin^2(kx)}{x^2}$ with $k>0$ and tells you
$\lim_{x\to0}f(x)=16$. Here the form is $\frac00$ whatever $k$ is; the
limit itself pins $k$ down:
$$\frac{\sin^2 kx}{x^2}=\left(\frac{\sin kx}{x}\right)^{2}
 \longrightarrow k^2 ,$$
so $k^2=16$ and, since $k>0$, $k=4$. The negative root is there to be
discarded, and discarding it out loud is part of the answer.
""")

md(r"""
## Task 9 🟡 — solve for the constant

Consider $\displaystyle\lim_{x\to0}\frac{\arctan(\cos x)-k}{x^2}$, where
$k\in\mathbb{R}$.

**(a)** Show that a finite limit only exists for $k=\dfrac{\pi}{4}$.

**(b)** Using l'Hôpital's rule, find the value of the limit when
$k=\dfrac\pi4$.

Now consider $f(x)=\dfrac{\sin^2(kx)}{x^2}$, where $x\ne0$ and
$k\in\mathbb{R}^{+}$.

**(c)** Given that $\displaystyle\lim_{x\to0}f(x)=16$, find the value
of $k$.

*May 2022 TZ2 Paper 2 Q7 — 8 marks. November 2023 TZ1 Paper 1 Q9(b) —
6 marks.*
""")

code(r"""
q9a = ...        # the value of k that makes the limit finite
q9b = ...        # the value of the limit at that k
q9c = ...        # the value of k in sin^2(kx)/x^2

verify_exact('9a', q9a, pi/4)
verify_limit('9b', q9b, (atan(cos(x)) - pi/4)/x**2)
check_num('9c', q9c, 1, D_9C)
""".replace('D_9C', repr(D_9C)))

md(r"""
---
## Theory 9. The limit taken somewhere other than $x$

$x$ is not sacred. The archive takes limits in $n$, in $b$, in $\alpha$,
in $m^n$ — and when it does, everything that is not the limiting
variable simply stays where it is.

**A parameter going to infinity.** May 2025 TZ3 Paper 3 has
$$f^n(x)=m^nx+c\,\frac{1-m^n}{1-m},\qquad -1<m<1,$$
and asks for the straight line the family approaches as $n\to\infty$.
The only thing moving is $m^n$, and $|m|<1$ makes it $0$. So $m^nx\to0$
and the bracket $\to 1$, leaving
$$y=\frac{c}{1-m}.$$
Four marks: one for using $m^n\to0$, one for each of the two terms, one
for the line. Note that $x$ never went anywhere — the answer is a
*horizontal* line, which is the point of the question.

**A parameter going to a finite place.** November 2022 Paper 2 takes
$\mathbf{u}=\mathbf{i}+\mathbf{j}$ and
$\mathbf{v}=\cos\frac1n\,\mathbf{i}+\sin\frac1n\,\mathbf{j}$, and asks
for the angle $\theta$ between them as $n\to\infty$. As
$\frac1n\to0$, $\mathbf{v}\to\mathbf{i}$, so $\theta$ tends to the
angle between $\mathbf{i}+\mathbf{j}$ and $\mathbf{i}$, which is
$\frac\pi4$. Or through the cosine:
$$\cos\theta=\frac{\cos\frac1n+\sin\frac1n}{\sqrt2}
 \longrightarrow\frac{1+0}{\sqrt2}=\frac1{\sqrt2} .$$
The markscheme accepts $45°$ and refuses $0.785$: an *exact* value was
asked for.

**A parameter running to a place where a function blows up.**
November 2023 Paper 3 has two families of curves meeting at an angle
$\alpha$, with
$$g(x,y)=\frac{f(x,y)+\tan\alpha}{1-f(x,y)\tan\alpha},$$
and asks what happens as $\alpha\to\frac\pi2$, where $\tan\alpha$ is
unbounded. Divide top and bottom by $\tan\alpha$ — then it is
$\frac1{\tan\alpha}$ that moves, and it moves to $0$:
$$g=\frac{\frac{f}{\tan\alpha}+1}{\frac{1}{\tan\alpha}-f}
  \longrightarrow\frac{0+1}{0-f}=-\frac1f .$$
Perpendicular curves, which is what $\alpha=\frac\pi2$ means, and the
negative reciprocal gradient, which is what perpendicular means.
""")

md(r"""
## Task 10 🟡 — let the parameter go

Consider $f^n(x)=m^nx+c\left(\dfrac{1-m^n}{1-m}\right)$, where
$-1<m<1$.

**(a)** As $n\to\infty$, the family of graphs $y=f^n(x)$ approaches the
graph of a straight line $L$. Determine the equation of $L$, giving your
answer in terms of $c$ and $m$.

Consider the vectors $\mathbf{u}=\mathbf{i}+\mathbf{j}$ and
$\mathbf{v}=\left(\cos\frac1n\right)\mathbf{i}+\left(\sin\frac1n\right)\mathbf{j}$,
where $n\in\mathbb{Z}^{+}$, and let $\theta$ be the angle between them.

**(b)** Find an expression for $\cos\theta$ in terms of $n$.

**(c)** Find the exact value of the limit approached by $\theta$ as
$n\to\infty$.

For (a) the answer is the right-hand side of $y=\dots$ — an expression
in $c$ and $m$, with no $x$ and no $n$ in it.

*May 2025 TZ3 Paper 3 Q1(d) — 4 marks. November 2022 Paper 2 Q7 —
6 marks.*
""")

code(r"""
FN = m**n*x + c*(1 - m**n)/(1 - m)
COSTHETA = (cos(1/n) + sin(1/n))/sqrt(2)

q10a = ...       # the right-hand side of the equation of L
q10b = ...       # cos(theta) in terms of n
q10c = ...       # the exact limit of theta

verify_limit('10a', q10a, FN, var=n, point=oo,
             params={m: (Rational(1, 2), -Rational(3, 4)),
                     c: (5, -2), x: (3, 7)})
verify_identity('10b', q10b, COSTHETA, var=n, samples=(1, 2, 3, 5))
check_num('10c', q10c, 6, D_10C)
""".replace('D_10C', repr(D_10C)))

md(r"""
## Task 11 🔴 — a whole Paper 3 part

Consider $f(x)=1+x+x^2+\dots+x^n$, where $n\in\mathbb{Z}^{+}$, and let
$f_1(x)=x\,f'(x)$. It has been shown that, for $x\ne1$,
$$f_1(x)=\frac{nx^{n+2}-(n+1)x^{n+1}+x}{(x-1)^2}.$$

**(a)** Show that $\displaystyle\lim_{x\to1}f_1(x)$ is in indeterminate
form, and name the form.

**(b)** Hence, by applying l'Hôpital's rule, show that
$$\lim_{x\to1}f_1(x)=\tfrac12 n(n+1).$$

Two rounds of the rule, with $n$ sitting in the exponents the whole
time — differentiate $x^{n+2}$ as $(n+2)x^{n+1}$ and keep going. The
answer is a formula you have met before: $f_1(1)=1+2+\dots+n$, which is
what the whole question was built to produce.

*November 2022 Paper 3 Q1(g) — 6 marks.*
""")

code(r"""
TOP = n*x**(n + 2) - (n + 1)*x**(n + 1) + x
F1 = TOP/(x - 1)**2

q11a = ...       # the form, as a string
q11b = ...       # the limit, in terms of n

verify_indeterminate('11a', q11a, TOP, (x - 1)**2, point=1, params={n: (2, 5, 8)})
verify_limit('11b', q11b, F1, point=1, params={n: (2, 3, 7)})
""")

md(r"""
## Task 12 🔴 — two limits taken in something else

Two families of curves $F$ and $G$ meet at an acute angle $\alpha$. The
gradient of $F$ is $f(x,y)$, the gradient of $G$ is $g(x,y)$, and
$$g(x,y)=\frac{f(x,y)+\tan\alpha}{1-f(x,y)\tan\alpha}.$$

**(a)** By considering $\displaystyle\lim_{\alpha\to\pi/2}\tan\alpha$,
show that for all finite $f(x,y)$,
$$\lim_{\alpha\to\pi/2}g(x,y)=-\frac{1}{f(x,y)}.$$

Let $S_1(x)=\sin x$ and $S_n(x)=\sin\bigl(S_{n-1}(x)\bigr)$ for
$n\ge 2$, so $S_3(x)=\sin(\sin(\sin x))$. It has been proved that
$$S_n'(x)=\cos\bigl(S_{n-1}(x)\bigr)\cos\bigl(S_{n-2}(x)\bigr)\cdots
  \cos\bigl(S_1(x)\bigr)\cos x .$$

**(b)** Use l'Hôpital's rule to show that
$\displaystyle\lim_{x\to0}\frac{S_n(x)}{x}=1$ for $n\in\mathbb{Z}^{+}$.

For (a), enter the limit as an expression in the letter `F` standing for
$f(x,y)$; the check substitutes several values of it. For (b), enter the
value once — the check tries it on $S_3$ and on $S_6$.

*November 2023 Paper 3 Q2(f) — 2 marks. November 2025 TZ3 Paper 3 Q1(g)
— 3 marks.*
""")

code(r"""
F = symbols('F')                       # f(x, y), which does not move
G = (F + tan(alpha))/(1 - F*tan(alpha))

S3 = sin(sin(sin(x)))
S6 = sin(sin(sin(sin(sin(sin(x))))))

q12a = ...       # the limit of g as alpha -> pi/2, in terms of F
q12b = ...       # the limit of S_n(x)/x as x -> 0

verify_limit('12a', q12a, G, var=alpha, point=pi/2,
             params={F: (2, -3, Rational(1, 5))})
verify_limit('12b (n = 3)', q12b, S3/x)
verify_limit('12b (n = 6)', q12b, S6/x)
""")

md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. For each one, name the technique — **do not solve
anything.** On the exam the difference between a solved limit and an
unsolved one is usually the first ten seconds, because every technique
here is short once chosen and hopeless once mis-chosen.

Use these codes:

`substitute` · put the number in, cancelling first if you must  |
`infinity` · $x\to\infty$, highest power  |
`lhopital` · $\frac00$ or $\frac\infty\infty$, differentiate  |
`again` · expect several rounds  |  `series` · Maclaurin instead  |
`finite` · find the constant that makes it exist  |
`parameter` · the limit is in something other than $x$  |
`symbolic` · a parameter sits inside the expression  |
`context` · say what it means

1. $\displaystyle\lim_{x\to3}\frac{x^2-9}{x-3}$
2. $\displaystyle\lim_{x\to\infty}\frac{5x^2-x}{2x^2+7}$
3. A population is modelled by $P(t)=\frac{800}{1+9e^{-0.4t}}$. State
   $\lim_{t\to\infty}P(t)$ and explain what it says about the
   population.
4. $\displaystyle\lim_{x\to0}\frac{e^{2x}-1}{\sin 5x}$
5. $\displaystyle\lim_{x\to0}\frac{\sin x-x\cos x}{x^3}$
6. $\displaystyle\lim_{x\to0}\frac{\ln(1+x)-x+\frac{x^2}{2}}{x^3}$,
   given the series for $\ln(1+x)$
7. $\displaystyle\lim_{x\to0}\frac{\sqrt{4+x}-a}{x}$ is finite. Find $a$.
8. $\displaystyle\lim_{n\to\infty}\bigl(m^{n}a+b\bigr)$, where $|m|<1$
   and $a$, $b$ are fixed
9. $\displaystyle\lim_{x\to\frac\pi4}\frac{\sin x}{1+\cos x}$
10. $\displaystyle\lim_{x\to\infty}x\ln\!\left(1+\frac1x\right)$
11. $\displaystyle\lim_{x\to-\infty}\frac{3x^3+x}{x^3-4x^2}$
12. $\displaystyle\lim_{x\to1}\frac{x^{n}-1}{x-1}$, where
    $n\in\mathbb{Z}^{+}$
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, TRIGGER_KEY)
""".replace("TRIGGER_KEY", repr(TRIGGER_KEY)))

md(r"""
---
## On the timer

**May 2025 TZ3 Paper 1 Q9 — 6 marks. Target: 9 minutes.**

Close everything above. No calculator.

> Determine the value of
> $$\lim_{x\to 0}\left(\frac{x\sin x}{1-\cos x}\right).$$

Six marks for one limit. Substituting gives $\frac00$; the denominator
is second order in $x$, so expect two rounds, and check the form again
after the first. There is a one-line route through the series as well —
if you see it, take it, and then do it the long way afterwards to check
you would have got there anyway.

**Attempt log.** Copy this line and add a date and a time each pass.

```
2026-08-30 — 
```
""")

code(r"""
qt = ...         # the limit

verify_limit('timed', qt, x*sin(x)/(1 - cos(x)))
""")

md(r"""
---
# 🔑 Solutions

Read one only after you have an answer of your own — even a wrong one.
Each solution names its source and the marks it carries.

---
### Task 1 — substitute, and cancel what stops you
*May 2024 TZ1 P1 Q11(b), 3 marks · Q11(f)(i), part of 3 marks*

**(a)** $P(-1)=-3+5-1-1=0$, so $(x+1)$ is a factor. Dividing,
$$P(x)=(x+1)(3x^2+2x-1)=(x+1)(3x-1)(x+1)=(x+1)^2(3x-1).$$

**(b)** Substituting $x=-1$ into $f$ gives $\frac00$, so look for the
shared factor. With $Q(x)=(x+1)(2x+1)$,
$$f(x)=\frac{(x+1)^2(3x-1)}{(x+1)\cdot(x+1)(2x+1)}
      =\frac{3x-1}{2x+1}\quad (x\ne-1),$$
and now
$$\lim_{x\to-1}f(x)=\frac{-3-1}{-2+1}=\frac{-4}{-1}=4 .$$
No calculus needed, and none wanted: the whole question is the
factorisation from (a) being used again.

---
### Task 2 — the far end
*May 2024 TZ1 P1 Q11(f)(ii) · May 2025 TZ3 P2 Q10(c)(i)*

**(a)** Using the cancelled form, divide by $x$:
$$\lim_{x\to\infty}\frac{3x-1}{2x+1}
 =\lim_{x\to\infty}\frac{3-\frac1x}{2+\frac1x}=\frac32 .$$

**(b)** $\sqrt{t^2+0.2}$ behaves like $t$, so
$$v(t)=\frac{8.14\,t}{\sqrt{t^2+0.2}}
 =\frac{8.14}{\sqrt{1+\frac{0.2}{t^2}}}\longrightarrow 8.14 .$$
"Write down" means one mark and no working — but the working above is
what tells you it is $8.14$ and not $0$ or $\infty$.

---
### Task 3 — the number and the sentence
*May 2025 TZ3 P2 Q10(c)(ii) · May 2025 TZ1 P3 Q2(b)(iii), 2 marks*

**(a)** The race is $200$ metres long. Fiona finishes in about
$26$ seconds, so $t$ never approaches infinity and her velocity never
reaches $8.14\ \mathrm{m\,s^{-1}}$ — it is a bound the model tends to,
not a speed anybody runs at.

**(b)** As $x\to\infty$, $(2ax+b)^2\to\infty$, so the denominator grows
without bound while the numerator $2|a|$ is fixed:
$$\lim_{x\to\infty}k(x)=0 .$$

**(c)** The curvature of a quadratic tends to zero far from the vertex:
for large $x$ a parabola is very nearly a straight line. The markscheme
takes *"for large positive values of $x$, a quadratic function behaves
like a linear function"* word for word.

---
### Task 4 — the rule, once
*May 2021 TZ1 P1 Q8, 5 marks*

**(a)** $\arctan(2\cdot0)=0$ and $\tan(3\cdot0)=0$, so
$$\lim_{x\to0}\frac{\arctan2x}{\tan3x}=\frac00 ,$$
which is indeterminate and gives the licence for the rule.

**(b)** Differentiating top and bottom separately,
$$\frac{\mathrm d}{\mathrm dx}\arctan 2x=\frac{2}{1+4x^2},\qquad
  \frac{\mathrm d}{\mathrm dx}\tan 3x=3\sec^2 3x ,$$
so
$$\lim_{x\to0}\frac{\arctan2x}{\tan3x}
 =\lim_{x\to0}\frac{\frac{2}{1+4x^2}}{3\sec^23x}
 =\frac{2}{3}.$$
**M1** for attempting to differentiate both, **A1A1** for the two
derivatives, **(M1)** for substituting $x=0$, **A1** for $\frac23$. The
note is blunt: *do not condone absence of limits* — without $\lim$ on
each line the maximum is **M1A1A0M1A1**.

---
### Task 5 — twice, and stop
*May 2024 TZ2 P1 Q8, 6 marks*

Substituting gives $\frac{1-1}{0-0}=\frac00$, so the rule applies.

**First round.** $\dfrac{\mathrm d}{\mathrm dx}\bigl(\sec^4x-\cos^2x\bigr)
=4\sec^4x\tan x+2\sin x\cos x$ and
$\dfrac{\mathrm d}{\mathrm dx}\bigl(x^4-x^2\bigr)=4x^3-2x$, so
$$\lim_{x\to0}\frac{4\sec^4x\tan x+2\sin x\cos x}{4x^3-2x} .$$
At $x=0$ this is $\frac{0}{0}$ again — a second licence.

**Second round.** Differentiating $4\sec^4x\tan x$ by the product rule
gives $16\sec^4x\tan^2x+4\sec^6x$, and $2\sin x\cos x=\sin 2x$ gives
$2\cos 2x=2\cos^2x-2\sin^2x$:
$$\lim_{x\to0}\frac{16\sec^4x\tan^2x+4\sec^6x-2\sin^2x+2\cos^2x}{12x^2-2}
 =\frac{0+4-0+2}{-2}=\frac{6}{-2}=-3 .$$

At $x=0$ the denominator is $-2$, not $0$: the form is no longer
indeterminate and the work stops here. The markscheme is explicit —
**M1** for the second use of the rule *providing their expression is in
indeterminate form as $x\to0$ and providing there is no third attempt at
using l'Hôpital's rule*.

Its other note is the one that quietly costs marks: *to award full marks
limit notation $\lim_{x\to0}$ must be seen at least once in the working.
If no limit notation is seen but otherwise all correct, do not award the
final A1.*

Where the six go: **M1** for attempting the rule, **A1A1** for the two
first derivatives, **M1** for the second application, **A1A1** for the
second derivatives — and the answer $-3$ falls out of them.

---
### Task 6 — three rounds, or one line
*May 2022 TZ1 P1 Q12(d), 5 marks · Q12(e), 3 marks*

**(a)** With $g(x)=e^x\cos x$: $g(0)=1$, $g'(0)=1$, and the relation
$g''=2(g'-g)$ from part (c) of the original question gives $g''(0)=0$,
$g'''(0)=-2$, $g^{(4)}(0)=-4$. So
$$g(x)=1+x+0\cdot\frac{x^2}{2}-\frac{2x^3}{6}-\frac{4x^4}{24}
      =1+x-\frac{x^3}{3}-\frac{x^4}{6}.$$

**(b)** Now the limit is one subtraction:
$$\frac{e^x\cos x-1-x}{x^3}
 =\frac{-\frac{x^3}{3}-\frac{x^4}{6}+\dots}{x^3}
 =-\frac13-\frac x6+\dots\longrightarrow-\frac13 .$$
Three marks. The l'Hôpital route reaches the same place after three
rounds — the markscheme prints it as METHOD 2 and it runs to half a
page.

---
### Task 7 — pull the power out, keep the parameter
*November 2021 P1 Q11(c), 4 marks · May 2025 TZ1 P1 Q12(e), 5 marks*

**(a)** $x^9=(x^3)^3$, so the whole expression is a cube:
$$\frac{(x^2e^x-x^2)^3}{x^9}
 =\left(\frac{x^2(e^x-1)}{x^3}\right)^3
 =\left(\frac{e^x-1}{x}\right)^3 .$$
And $\frac{e^x-1}{x}=1+\frac x2+\dots\to1$, so the limit is $1^3=1$.

**(b)** From $\cos x=1-\frac{x^2}{2}+\dots$, raising to the $n$th power
and keeping only what survives division by $x^2$:
$$\cos^nx=\left(1-\frac{x^2}{2}+\dots\right)^n=1-\frac{nx^2}{2}+\dots$$
(the binomial's next term carries $x^4$). Equivalently, differentiate
twice: $f_n'(x)=-n\cos^{n-1}x\sin x$ and
$f_n''(x)=-n\cos^nx+n(n-1)\cos^{n-2}x\sin^2x$, so $f_n(0)=1$,
$f_n'(0)=0$, $f_n''(0)=-n$.

**(c)** $$\frac{f_n(x)-1}{x^2}=\frac{-\frac{nx^2}{2}+\dots}{x^2}
 \longrightarrow-\frac n2 .$$
The markscheme's note is worth having: *do not award FT marks for an
expression that does not involve $n$.* An answer without $n$ in it is
not an answer to this question.

---
### Task 8 — the other indeterminate form
*May 2023 TZ1 P3 Q1(c)(i), 2 marks · May 2025 TZ2 P2 Q11(c), 5 marks*

**(a)** Both parts run to infinity, so the form is
$\frac{\infty}{\infty}$:
$$\lim_{b\to\infty}\frac{e^b-b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b-1}{e^b}
 =\lim_{b\to\infty}\frac{e^b}{e^b}=1 .$$
One mark for the correct quotient, one for the $1$.

**(b)** A product of the form $\infty\cdot0$ is not a quotient. Rewrite
first — this is the mark the markscheme insists on seeing:
$$(3x+1)e^{-3x}=\frac{3x+1}{e^{3x}}
 \;\Longrightarrow\;
 \lim_{x\to\infty}\frac{3}{3e^{3x}}
 =\lim_{x\to\infty}\frac{1}{e^{3x}}=0 .$$

**(c)** Take the limit through the given integral:
$$\lim_{a\to\infty}\int_0^a f(t)\,dt
 =\frac k9\Bigl(1-\lim_{a\to\infty}(3a+1)e^{-3a}\Bigr)
 =\frac k9(1-0)=\frac k9 .$$
A probability density function integrates to $1$ over its whole range,
so $\frac k9=1$ and $k=9$.

---
### Task 9 — solve for the constant
*May 2022 TZ2 P2 Q7, 8 marks · November 2023 TZ1 P1 Q9(b), 6 marks*

**(a)** $\lim_{x\to0}x^2=0$. A finite limit therefore requires the
numerator to go to $0$ as well — otherwise the quotient is unbounded.
So
$$\lim_{x\to0}\bigl(\arctan(\cos x)-k\bigr)=0
 \;\Longrightarrow\;\arctan 1-k=0\;\Longrightarrow\;k=\frac\pi4 .$$
Note the direction: you deduce $k$ from the requirement, you do not
substitute $k$ and check. **M1A0** for the second.

**(b)** With $k=\frac\pi4$ the form is $\frac00$. First round:
$$\lim_{x\to0}\frac{\dfrac{-\sin x}{1+\cos^2x}}{2x}
 =\lim_{x\to0}\frac{-\sin x}{2x\,(1+\cos^2 x)} ,$$
still $\frac00$. Second round, or simply $\frac{\sin x}{x}\to1$ and
$1+\cos^2x\to2$:
$$\longrightarrow\frac{-1}{2\cdot 2}=-\frac14 .$$

**(c)** $$\frac{\sin^2kx}{x^2}=\left(\frac{\sin kx}{x}\right)^2
 =k^2\left(\frac{\sin kx}{kx}\right)^2\longrightarrow k^2 .$$
So $k^2=16$, and $k\in\mathbb{R}^+$ leaves $k=4$. Saying why $-4$ is
rejected is part of the answer.

---
### Task 10 — let the parameter go
*May 2025 TZ3 P3 Q1(d), 4 marks · November 2022 P2 Q7, 6 marks*

**(a)** Only $m^n$ moves, and $-1<m<1$ makes $m^n\to0$. Hence
$m^nx\to0$ and $\dfrac{1-m^n}{1-m}\to\dfrac{1}{1-m}$, so
$$L:\;y=\frac{c}{1-m}.$$
**(M1)** for using $m^n\to0$, **(A1)** for the $x$ term vanishing,
**A1** for the constant term, **A1** for the line.

**(b)** $\mathbf u\cdot\mathbf v=\cos\frac1n+\sin\frac1n$,
$|\mathbf u|=\sqrt2$, $|\mathbf v|=1$, so
$$\cos\theta=\frac{\cos\frac1n+\sin\frac1n}{\sqrt2}.$$

**(c)** $\frac1n\to0$, so $\cos\theta\to\frac{1+0}{\sqrt2}
=\frac1{\sqrt2}$ and
$$\theta\longrightarrow\frac\pi4 .$$
$45°$ is accepted; $0.785$ is not, because the question said *exact*.

---
### Task 11 — a whole Paper 3 part
*November 2022 P3 Q1(g), 6 marks*

**(a)** At $x=1$ the numerator is $n\cdot1-(n+1)\cdot1+1=0$ and the
denominator is $0$, so
$$\lim_{x\to1}f_1(x)=\frac{n-(n+1)+1}{0}=\frac00 .$$
One mark, **R1**, and the note says it is refused if $\lim_{x\to1}$ is
not written down.

**(b)** First round:
$$\lim_{x\to1}\frac{n(n+2)x^{n+1}-(n+1)^2x^n+1}{2(x-1)} .$$
At $x=1$ the numerator is $n(n+2)-(n+1)^2+1=n^2+2n-n^2-2n-1+1=0$, so it
is $\frac00$ again. Second round:
$$\lim_{x\to1}\frac{n(n+1)(n+2)x^{n}-n(n+1)^2x^{n-1}}{2}$$
$$=\frac{n(n+1)\bigl[(n+2)-(n+1)\bigr]}{2}=\frac{n(n+1)}{2}.$$
Which is $1+2+\dots+n$ — and it had to be, because
$f_1(1)=1+2\cdot1+\dots+n\cdot1$.

---
### Task 12 — two limits taken in something else
*November 2023 P3 Q2(f), 2 marks · November 2025 TZ3 P3 Q1(g), 3 marks*

**(a)** As $\alpha\to\frac\pi2$, $\tan\alpha$ is unbounded, so divide
top and bottom by it and let $\frac1{\tan\alpha}\to0$:
$$g=\frac{\frac{f}{\tan\alpha}+1}{\frac1{\tan\alpha}-f}
 \longrightarrow\frac{0+1}{0-f}=-\frac1f .$$
Two marks: **M1** for the division, **R1** for
$\frac1{\tan\alpha}\to0$, and the **R1** depends on the **M1**.

**(b)** $S_n(0)=0$ and the denominator is $0$, so the form is
$\frac00$. One round of the rule:
$$\lim_{x\to0}\frac{S_n(x)}{x}=\lim_{x\to0}\frac{S_n'(x)}{1}
 =\lim_{x\to0}\cos\bigl(S_{n-1}(x)\bigr)\cdots\cos\bigl(S_1(x)\bigr)\cos x .$$
Every $S_k(0)=0$, so every factor is $\cos 0=1$, and the product of $n$
ones is $1$. The proof by induction in the previous part is what makes
this one line long.

---
### On the timer
*May 2025 TZ3 P1 Q9, 6 marks*

Substituting gives $\frac{0\cdot0}{1-1}=\frac00$. First round:
$$\lim_{x\to0}\frac{\sin x+x\cos x}{\sin x},$$
still $\frac00$. Second round:
$$\lim_{x\to0}\frac{2\cos x-x\sin x}{\cos x}=\frac{2-0}{1}=2 .$$

The one-line route: $\sin x\approx x$ and
$1-\cos x\approx\frac{x^2}{2}$, so
$$\frac{x\sin x}{1-\cos x}\approx\frac{x\cdot x}{x^2/2}=2 .$$
Or, without any series at all, multiply above and below by
$1+\cos x$:
$$\frac{x\sin x(1+\cos x)}{1-\cos^2x}
 =\frac{x\sin x(1+\cos x)}{\sin^2 x}
 =\frac{x}{\sin x}(1+\cos x)\longrightarrow1\cdot2=2 .$$
Three routes, one answer, and the third is the one to have on a
no-calculator paper.

---
### Key to the recognition drill

| # | code | why |
| --- | --- | --- |
| 1 | `substitute` | $x^2-9=(x-3)(x+3)$; cancel the shared factor and put $3$ in |
| 2 | `infinity` | same degree top and bottom: ratio of leading coefficients, $\frac52$ |
| 3 | `context` | the number is $800$; the mark is for saying it is the ceiling the population never quite reaches |
| 4 | `lhopital` | $\frac00$, nothing to cancel, one round gives $\frac25$ |
| 5 | `again` | denominator $x^3$ and no series offered: expect three rounds, ending at $\frac13$ |
| 6 | `series` | the series is handed to you; use it rather than differentiating three times |
| 7 | `finite` | the denominator dies, so the numerator must: $a=2$ |
| 8 | `parameter` | the limit is in $n$; $m^n\to0$ and $a$, $b$ sit still, so the answer is $b$ |
| 9 | `substitute` | $\frac\pi4$ is in the domain and nothing vanishes; substitute and stop |
| 10 | `lhopital` | $\infty\cdot0$: rewrite as $\dfrac{\ln(1+1/x)}{1/x}$ first, then the rule |
| 11 | `infinity` | degree three over degree three, so $3$ — and $-\infty$ changes nothing |
| 12 | `symbolic` | $\frac00$ with $n$ in the exponent; one round of the rule gives $n$ |

Numbers 5 and 6 are the pair to look at twice. Both have a high power
in the denominator; the difference is that 6 hands you the series and 5
does not. When a series is given, the question is telling you which
technique it wants.

---
### Where the marks went, across the topic

| technique | blocks | marks |
| --- | --- | --- |
| substitute, and cancel | 1 | part of 3 |
| highest power | 2 | part of 6 |
| l'Hôpital, one round | 3 | 8 |
| l'Hôpital, more than one | 3 | 18 |
| Maclaurin instead | 3 | 9 |
| choose the constant | 3 | 10 |
| limit in a parameter | 3 | 9 |
| the rule with a letter in it | 3 | 9 |
| what it means | 2 | part of 5 |

Rows three to five are $35$ of the $73$ marks and they are one
instruction repeated: **substitute, name the form, differentiate,
substitute again.** The topic is small and it is nearly all one habit.
The surprise is row seven — nine marks for limits that have nothing to
do with $x$ — and it is where a student who has only practised
$\frac00$ loses the most.
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
