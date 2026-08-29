"""Собирает практикум B5 (показательные и логарифмические модели) в .ipynb.

Четвёртый практикум серии на английском: ноутбук целиком английский, kit
переключается вызовом language('en') в установочной ячейке. Документация
репозитория (карта, PRACTICUM.md, этот заголовок) остаётся русской.

Тема даёт девятое понятие равенства ответов: ответ здесь — сама модель,
и верна она не тогда, когда её постоянные совпали с эталонными, а тогда,
когда она воспроизводит данные, из которых её строили. Отсюда verify_model:
он подставляет в ответ каждую пару из условия и ничего не хранит. Заодно
он ловит главную потерю баллов темы — сдвинутый отсчёт времени: постоянные
верны, а t = 19 вместо t = 27.

Второй новой проверкой стала verify_in_terms_of. Вопрос «выразите log 24
через p и q» имеет ответом не число, а выражение через данные буквы,
поэтому проверка требует двух вещей сразу: чужих букв в ответе нет,
а после подстановки истинных значений получается то самое число. Без
первого условия ответ log 24, переписанный сам через себя, проходил бы.

Обе живут в kit.py и проверены в tests/test_kit_model.py.
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
x, t, k = sp.symbols('x t k')

NOTEBOOK = os.path.join(ROOT, 'practicum/functions/practicum-b5-exponential-log-models.ipynb')


def dn(value, sf=6):
    return digest(sig(value, sf))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_b5.py ---
D_62 = dn(2380, 3)                       # 25% углерода-14 распалось, лет
D_71 = dn(30000 * R(85, 100)**10, 6)     # стоимость машины через десять лет
D_72 = dn(14, 2)                         # месяцев до 55000 реальных
D_82 = dn(1041, 4)                       # динаров через год
D_83 = dn(1520, 3)                       # стоимость машины четыре года назад
D_93 = dn(sp.log(R(28, 13)) / 5, 3)      # k логистической модели
D_94 = dn(107, 3)                        # волков через десять лет
D_112 = dn(60 + 10 * sp.log(2, 10), 3)   # громкость S2, децибелы
D_113 = dn(10**sp.Rational(-1, 2), 3)    # интенсивность грома
D_T1 = dn(15000 * sp.exp(sp.log(R(89, 100)) / 8 * 27), 3)  # население в 2041

TRIGGER = {1: 'laws', 2: 'base', 3: 'logeq', 4: 'powers', 5: 'takelogs',
           6: 'fit', 7: 'percent', 8: 'logistic', 9: 'function',
           10: 'takelogs', 11: 'base', 12: 'fit'}
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
# Practicum B5: exponential and logarithmic models

**85 marks, 37 blocks, nine techniques.** Every question in this topic
is one of two sentences. *The unknown is in the exponent* — and the only
way down is a logarithm. *The unknown is under a logarithm* — and the
only way up is a power. Everything else is arithmetic.

**Material.** The whole of `functions.logarithmic_functions`,
`functions.exponential_models`, `functions.mathematical_models` and
`number_algebra.exponential_models` from the AA HL archive, sessions May
2021 — November 2025. Four topics, because no one of them reaches the
lower bound of 60 marks on its own — the largest is 35 — and because the
archive does not separate them either: November 2025 Paper 3 fits a
logistic curve, takes logarithms of it, and then solves the differential
equation behind it, in one question.

**This practicum is in English,** like B2, B3 and B4. The checks speak
whichever language the notebook asks them to, and this one asks for
English in the setup cell.

**The two sentences.**

> $50 = 100e^{-5730k}$ — *the unknown is in the exponent.* Take
> logarithms of both sides and it walks down: $k=\dfrac{\ln 2}{5730}$.
>
> $3\log_8 10x-\log_4 x=1$ — *the unknown is under a logarithm.* Make
> the bases agree, collapse each side to one logarithm, and then remove
> them: $x=\dfrac{1}{25}$.

Everything in the topic is one of these with more furniture around it. A
population model is the first sentence with two data points instead of
one. Compound interest is the first sentence with the base written as
$1+r$. Decibels are the second sentence with a factor of 10 in front.

**Where the calculator sits, and here it is not an illusion.** 54% of
the marks carry one, and unlike B2 and B3 the split is real: Paper 1
asks for the laws and the exact form, Paper 2 and Paper 3 ask you to fit
a model to data and predict. The same technique — take logs of both
sides — ends at $\dfrac{\ln 2}{5730}$ on one paper and at $2380$ on the
other.

**How the checks work here.** Two of them are new.

* `verify_model` takes the model you fitted and puts the data back into
  it. No stored constants: your $A$ and $k$ are right when
  $A(0)$ and $A(8)$ come out to what the question said they were. This
  is where the marks in the topic actually go — *"recognizing that
  $t=8$ on 1 January 2022"* is one of the seven marks in November 2022,
  and getting $t$ wrong is the standard way to lose the question with
  perfect algebra.
* `verify_in_terms_of` is for *"find an expression for $\log_{10}24$ in
  terms of $p$ and $q$"*. It checks two things at once: that nothing but
  the given letters appears in your answer, and that substituting their
  true values gives the right number. Without the first check,
  $\log_{10}24$ rewritten as itself would pass.

**How to work**

1. Read the map of techniques first. It is arranged by **which way the
   unknown has to move**.
2. Work **on paper** before typing anything. On Paper 1 questions there
   is no calculator at all.
3. Exact answers where the paper is Paper 1: `Rational(1, 9)`,
   `log(2)/5730`, `3*p + q`. Three significant figures where the paper
   is Paper 2 or 3.
4. A model is entered as an expression in `t`: `15000*exp(-0.0146*t)`,
   `200/(1 + 4*exp(-0.153*t))`.
5. A set of values is entered as a set or an inequality:
   `Interval(exp(-5), E)`, `(x > -1)`, `Union(...)`.
6. The last three blocks are a Paper 1 / Paper 2 comparison, a
   recognition trainer, and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a
wrapper · 🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Union, solveset, Rational

language('en')                 # this notebook is in English, and so are the checks

a, b, n, p, q, r = symbols('a b n p q r')
S, T, v0 = symbols('S T v0', positive=True)
# S here is the sum from Task 12, and it shadows sympy's S. Where a check
# wants "all the reals", write Interval(-oo, oo) rather than S.Reals.

print('ready; sympy', sp.__version__)
print('in terms of p and q: ', 3*p + q)
print('an exact log:        ', log(2)/5730)
print('a model in t:        ', 15000*exp(log(Rational(89, 100))/8*t))
print('a set of values:     ', Interval(exp(-5), E))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | First move |
| --- | --- | --- | --- |
| 1 | The three log laws | several logs of one base; «in terms of $p$ and $q$» | factorise the argument |
| 2 | Change of base | two different bases in one line | rewrite everything in the smallest base |
| 3 | Log equation | $x$ under a logarithm | collapse each side to one log |
| 4 | Laws of exponents | powers of one base; a given relation like $e^{T}=1+v_0$ | split the exponent |
| 5 | Take logs of both sides | the unknown is in the exponent | isolate the power first |
| 6 | Fit the model | a form with letters and two data points | decide what $t=0$ means |
| 7 | Percentages as a power | «per annum», «compounded», «inflation» | turn the percentage into a multiplier |
| 8 | The logistic model | a stated long-run limit $L$ | put $t=0$ and use $e^{0}=1$ |
| 9 | The logarithm as a function | $\ln$ inside another function; a log scale | solve for $\ln x$, remove it last |

**The ladder goes by which way the unknown has to move.**

**Rungs 1–3 — upwards, out from under the logarithm.** First the three
laws, which are the whole of Paper 1 in this topic. Then change of base,
which exists for one reason: until the bases agree, no law applies.
Then the equation, which is the two of them plus one step — remove the
logarithms — and one habit: check the arguments were positive.

**Rungs 4–6 — downwards, out of the exponent.** The laws of exponents
first, because they are what makes the descent possible and because two
questions in the archive are nothing else. Then the descent itself. Then
the descent done twice, which is what fitting a model is: one data point
gives the multiplier, the second gives $k$.

**Rungs 7–8 — the two models the archive actually asks about.**
Percentage growth is $A(1+r)^{t}$, and the whole difficulty is
translating English into $r$: *nominal* $4\%$ *compounded quarterly*
means $r=0.01$ per quarter, and *inflation* means you divide by
$1+j$ rather than subtracting $j$. The logistic model is
$L/(1+Ce^{-kt})$, and it is the same fit with a ceiling read straight
off the page.

**Rung 9 — the logarithm as a function, not as a tool.** $\ln$ inside a
composition, $\ln$ defining a domain, $\ln$ as a measuring scale. This
comes last not because it is hard but because it uses rung 1 in a place
where you were not looking for it.

**What saves the most time.** Before touching anything, write down what
$t=0$ means and what one unit of $t$ is. Half the lost marks in this
topic are there, and they are lost before any mathematics happens.
""")

md(r"""
---
# Part I — upwards: out from under the logarithm

---
## Theory 1. Three laws, and the one that does not exist

$\log_b a$ is the answer to one question: *to what power must $b$ be
raised to give $a$?* Everything follows from that, including the three
laws:

$$\log_b(MN)=\log_b M+\log_b N, \qquad
  \log_b\!\frac{M}{N}=\log_b M-\log_b N, \qquad
  \log_b M^{\,r}=r\log_b M .$$

**The law that does not exist** is $\log(M+N)$. There is no rule for it,
and the examiner knows exactly how tempting it looks. Every appearance
of a sum inside a logarithm in this archive is there to be
*factorised* first: $\log_{10}24=\log_{10}(2^3\cdot 3)$, not
$\log_{10}(20+4)$.

**The fourth fact, which is not a law but is worth as many marks.** A
number standing next to a logarithm has to become one before it can join
in:

$$1=\log_b b, \qquad 3=\log_2 8, \qquad -1=\log_{10}\tfrac{1}{10}.$$

Both log-equation questions in the archive hinge on this. November 2025
TZ1 has $\log_2[\dots]-1=\log_2[\dots]$, and the $-1$ is the question.

**"In terms of $p$ and $q$" is an instruction about the form of the
answer.** May 2025 TZ3 gives $p=\log_{10}2$, $q=\log_{10}3$ and asks for
$\log_{10}24$. The answer is $3p+q$. A decimal, however accurate, is not
an answer — and neither is $\log_{10}24$ rewritten as
$\frac{\ln 24}{\ln 10}$.

**Monotonicity is a licence, and it costs a mark to skip.** To go from
$2n\ge n+1$ to $\log_2 2n\ge\log_2(n+1)$ you need the fact that
$\log_2$ is increasing. The markscheme for May 2025 TZ1 Q8(a) awards
**R1** for exactly that sentence.
""")

md(r"""
## Task 1 🟢 — the laws in both directions

**(a)** Let $\log_{10}2=p$ and $\log_{10}3=q$. Find an expression for
$\log_{10}24$ in terms of $p$ and $q$.

**(b)** Show that $1+\log_2 n\ge\log_2(n+1)$ for $n\in\mathbb{Z}^{+}$.

For (b) the answer is printed in the question, so there is nothing to
hide. What the cell checks is the step that earns the marks: write
$1+\log_2 n$ **as a single logarithm**.

*May 2025 TZ3 Paper 1 Q1(a) — 3 marks. May 2025 TZ1 Paper 1 Q8(a) —
2 marks.*
""")

code(r"""
q1a = ...        # log_10 24 in terms of p and q
q1b = ...        # 1 + log_2 n written as one logarithm, e.g. log(<something>, 2)

verify_in_terms_of('1a', q1a, log(24, 10), {p: log(2, 10), q: log(3, 10)})
verify_identity('1b', q1b, 1 + log(n, 2), var=n)
""")

md(r"""
---
## Theory 2. Change of base, and why it is always available

$$\log_b a=\frac{\log_c a}{\log_c b}\qquad\text{for any base }c>0,\ c\ne 1 .$$

Two logarithms of different bases cannot be added, subtracted or
compared. Nothing from Theory 1 applies until they agree. So the first
move in any question with two bases is to pick one and convert.

**Which base to pick.** Almost always the smallest one that the others
are powers of. The archive is unsubtle about this:

| question | bases seen | base to use |
| --- | --- | --- |
| May 2024 TZ1 | $10$ and $1000$ | $10$, since $1000=10^3$ |
| May 2025 TZ3 | $10$ and $3$ | $10$, since $q=\log_{10}3$ is given |
| Nov 2025 TZ3 | $8$ and $4$ | $2$, since $8=2^3$ and $4=2^2$ |

**The shortcut worth memorising.** When the bases are powers of one
number, the conversion is just a fraction:

$$\log_{b^{m}} a=\frac{1}{m}\log_b a .$$

That is why $\log_{1000}a=\tfrac{1}{3}\log_{10}a=\tfrac{1}{3}\cdot
\tfrac{1}{3}=\tfrac{1}{9}$ in one line, and why
$3\log_8 10x=\log_2 10x$ — the $3$ in front and the $3$ in $8=2^3$
cancel exactly.

**The direction people get wrong.** $\log_b a=\frac{\log a}{\log b}$:
the *argument* goes on top, the *base* goes underneath. Check it once on
something you know — $\log_2 8=\frac{\log 8}{\log 2}=\frac{3\log 2}{\log
2}=3$ — and you will not flip it again.

**Why your calculator needs this too.** A GDC computes only $\ln$ and
$\log_{10}$. Every other base it reaches by exactly this formula. It is
not a trick for exams; it is the definition being used sideways.
""")

md(r"""
## Task 2 🟢 — one base at a time

**(a)** Let $\log_{10}2=p$ and $\log_{10}3=q$. Find an expression for
$\log_3 8$ in terms of $p$ and $q$.

It is given that $\log_{10}a=\tfrac{1}{3}$, where $a>0$. Find the value
of

**(b)** $\log_{10}\dfrac{1}{a}$;  **(c)** $\log_{1000}a$.

*May 2025 TZ3 Paper 1 Q1(b) — 2 marks. May 2024 TZ1 Paper 1 Q2 —
5 marks. All Paper 1: the answers are exact.*
""")

code(r"""
q2a = ...        # log_3 8 in terms of p and q
q2b = ...        # log_10 (1/a)
q2c = ...        # log_1000 a

verify_in_terms_of('2a', q2a, log(8, 3), {p: log(2, 10), q: log(3, 10)})
verify_exact('2b', q2b, -Rational(1, 3))
verify_exact('2c', q2c, Rational(1, 9))
""")

md(r"""
---
## Theory 3. Solving when the unknown is under the logarithm

The recipe is fixed, and every step of it is a separate mark.

1. **Make the bases agree** (Theory 2).
2. **Collapse each side to a single logarithm** (Theory 1), turning any
   loose number into $\log_b b^{\,\text{that number}}$.
3. **Remove the logarithms.** From $\log_b A=\log_b B$ conclude $A=B$;
   from $\log_b A=c$ conclude $A=b^{\,c}$. This is legitimate because
   $\log_b$ is one-to-one — the same monotonicity that licensed the
   inequality in Task 1.
4. **Solve the algebraic equation** that is left.
5. **Check the arguments.** Every expression that stood inside a
   logarithm must be strictly positive at your root. This is not
   tidiness: taking logarithms is not reversible, and step 3 invents
   roots that the original equation never had.

**Where the archive puts the difficulty.** Not in step 4. November 2025
TZ3 collapses to $10\sqrt{x}=2$, which is trivial; the five marks are
for steps 1–3. November 2025 TZ1 collapses to $\frac{x}{2}=x-7$, which
is trivial; the four marks are for spotting that the loose $-1$ is
$\log_2\frac12$ and that the fractions cancel.

**The trap with a name.** From $\log A-\log B=\log C$ people conclude
$A-B=C$. The subtraction is *outside* the logarithms and the division is
*inside*: $\frac{A}{B}=C$. Write the quotient down explicitly before
removing anything.
""")

md(r"""
## Task 3 🟡 — two bases, one unknown

Solve the equation $3\log_8 10x-\log_4 x=1$ for $x>0$.

Enter the answer as a **list** of roots: `[Rational(1, 5)]`, `[4, 9]`.
The check substitutes each of them into the equation itself and then
scans the interval for the ones you did not write down.

*November 2025 TZ3 Paper 1 Q4 — 5 marks, no calculator.*
""")

code(r"""
q3 = [...]       # all roots with x > 0

verify_roots('3', q3, 3*log(10*x, 8) - log(x, 4) - 1, (0.0001, 100))
""")

md(r"""
## Task 4 🔴 — the loose $-1$, and the domain that removes a root

**(a)** Given that $x>7$, show that
$$\dfrac{x}{x^2-8x+7}\times\dfrac{x^2-1}{x+1}\equiv\dfrac{x}{x-7}.$$

**(b)** Hence, or otherwise, solve
$$\log_2\bigl[x(x^2-1)\bigr]-1=\log_2\bigl[(x^2-8x+7)(x+1)\bigr].$$

Part (a) is a factorising exercise, and the cell asks for the factor
that does the work: write $x^2-8x+7$ as a product of two linear factors.
Part (b) is the equation; note that the condition $x>7$ from part (a) is
exactly what makes every argument positive, so it is the domain, not
decoration.

*November 2025 TZ1 Paper 1 Q2 — 6 marks, no calculator.*
""")

code(r"""
q4a = ...        # x^2 - 8x + 7 as a product of two linear factors
q4b = [...]      # all roots of the equation in (b)

verify_factored('4a', q4a, x**2 - 8*x + 7, n=2)
verify_root_set('4b', q4b,
                Eq(log(x*(x**2 - 1), 2) - 1, log((x**2 - 8*x + 7)*(x + 1), 2)),
                domain=Interval.open(7, oo))
""")

md(r"""
---
# Part II — downwards: out of the exponent

---
## Theory 4. The laws of exponents, and the relation you were handed

$$a^{m}a^{n}=a^{m+n},\qquad \frac{a^{m}}{a^{n}}=a^{m-n},\qquad
  (a^{m})^{n}=a^{mn},\qquad a^{0}=1 .$$

Nothing here is new. What is new is *where* the archive uses them: not
to simplify an answer, but to make a substitution possible.

**May 2021 TZ2 Paper 1 Q11** hands you $v(t)=(1+v_0)e^{-t}-1$ and, from
an earlier part, the relation $e^{T}=1+v_0$. Then it asks for
$v(T-k)$. The whole of the two marks is one splitting:

$$v(T-k)=(1+v_0)e^{-(T-k)}-1
        =(1+v_0)\,\underbrace{e^{-T}}_{\;=\,1/(1+v_0)}\,e^{k}-1
        = e^{k}-1 .$$

Two things go wrong here and both are visible in the line above. The
minus in front of the bracket has to reach *both* terms, so the $e^{k}$
comes out with a plus. And $e^{T}=1+v_0$ gives
$e^{-T}=\dfrac{1}{1+v_0}$, not $1+v_0$.

**"Deduce a similar expression" means do not start again.** Part (d)
asks for $v(T+k)$. Replacing $k$ by $-k$ in the result of (c) is the
whole of it: $e^{-k}-1$. Two marks, ten seconds, and the word *deduce*
is the instruction.

**Any positive number is a power of $e$.** $3=e^{\ln 3}$ — not a trick,
just the definition of $\ln$ read backwards. May 2025 TZ1 Q7 opens with
that one-mark part and then uses it to make sense of $3^{\,i-1}$.
""")

md(r"""
## Task 5 🟢 — the substitution that does the work

The velocity of a particle is $v(t)=(1+v_0)e^{-t}-1$, and the time $T$
at which its displacement is greatest satisfies $e^{T}=1+v_0$.

**(a)** Write down $e^{-T}$ in terms of $v_0$.

**(b)** Hence show that $v(T-k)=e^{k}-1$, and **deduce** an expression
for $v(T+k)$ in terms of $k$.

Part (a) is the step the markscheme pays for; the cell checks it, and
then checks the deduction in (b).

*May 2021 TZ2 Paper 1 Q11(c) and (d) — 4 marks, no calculator.*
""")

code(r"""
q5a = ...        # e^(-T) in terms of v0
q5b = ...        # v(T + k), in terms of k

verify_identity('5a', q5a, 1/(1 + v0), var=v0)
verify_exact('5b', q5b, exp(-k) - 1)
""")

md(r"""
---
## Theory 5. Taking logarithms of both sides

When the unknown is in the exponent, no amount of algebra will get it
out. One operation will, and it is the only one:

$$a^{\,u}=b \quad\Longrightarrow\quad u\ln a=\ln b
  \quad\Longrightarrow\quad u=\frac{\ln b}{\ln a} .$$

**Isolate the power first.** From $50=100e^{-5730k}$, divide by $100$
*before* taking logarithms. $\ln(100e^{-5730k})$ is $\ln 100-5730k$, not
$100\times(-5730k)$, and half the lost marks in this technique are that
line.

**Two ways to say the same half-life, and the markscheme prints both.**

$$e^{-5730k}=\tfrac12 \;\Rightarrow\; -5730k=\ln\tfrac12=-\ln 2
  \qquad\text{or}\qquad
  e^{5730k}=2 \;\Rightarrow\; 5730k=\ln 2 .$$

The second avoids the minus sign entirely, which is why it is worth
preferring: $\ln\frac12=-\ln 2$ is the single most common sign slip in
the topic.

**Round at the end, never in the middle.** May 2021 asks for the time to
the nearest 10 years. Carrying $k=1.21\times 10^{-4}$ instead of
$\frac{\ln 2}{5730}$ moves the answer by years. Keep the exact form all
the way to the last line — that is what "exact form" is *for*, even on a
calculator paper.

**"First exceeds" is a ceiling, not a rounding.** May 2025 TZ2 gets
$n=13.77$ and answers $14$ months. Rounding to the nearest would give
$14$ here too, by luck; $n=13.2$ would still answer $14$.
""")

md(r"""
## Task 6 🟡 — a half-life, exactly and then numerically

The amount $A$ of carbon-14 in a plant $t$ years after its death is
modelled by $A=A_0e^{-kt}$, with $A_0,k>0$. At the time of death a plant
is defined to have $100$ units. The half-life is $5730$ years.

**(a)** Show that $k=\dfrac{\ln 2}{5730}$.

**(b)** Find, correct to the nearest $10$ years, the time after death
for $25\%$ of the carbon-14 to decay.

**(c)** Write down the completed model $A(t)$, with both constants in
place.

Part (c) is the first appearance of `verify_model`. It stores nothing:
it puts $t=0$, $t=5730$ and $t=11460$ back into whatever you wrote and
asks whether $100$, $50$ and $25$ come out. Only the numbers the question
states go in — a prediction is checked by the question that asks for it,
not by the model's own definition.

*May 2021 TZ2 Paper 2 Q5 — 7 marks, calculator allowed.*
""")

code(r"""
q6a = ...        # k, exactly
q6b = ...        # the time, to the nearest 10 years
q6c = ...        # A(t), an expression in t with no letters left in it

verify_exact('6a', q6a, log(2)/5730)
check_num('6b', q6b, 3, 'D_62')
verify_model('6c', q6c, [(0, 100), (5730, 50), (11460, 25)])
""".replace("'D_62'", repr(D_62)))

md(r"""
---
## Theory 6. Fitting a model: two constants, two conditions

$A(t)=A_0e^{kt}$ has two unknowns, so it takes exactly two facts to pin
down. The archive supplies them in the same shape every time.

1. **Decide what $t=0$ is and write it down.** Not later — now. In
   November 2022 the model starts on 1 January 2014, the second fact is
   about 1 January 2022, and the question asks about 1 January 2041. So
   $t=8$ and $t=27$. Answering with $t=19$ is answering a different
   question perfectly.
2. **The first condition gives the multiplier.** Almost always it is
   $A(0)$, and $e^{0}=1$ makes it immediate: $A_0=15000$.
3. **The second gives $k$,** by Theory 5. Here the phrasing does the
   damage: *"the population decreased by 11%"* means
   $A(8)=0.89\times 15000$, not $0.11\times 15000$.
4. **Substitute the target $t$.** Keep $k$ exact until this line.

**What the markscheme actually pays for.** November 2022 splits seven
marks as: recognising $A_0$, computing the $11\%$ drop, recognising
$t=8$, substituting, finding $k$, substituting $t=27$, and the number.
Five of the seven are set-up. The exponential is one line in the middle.

**How to check a fitted model in ten seconds.** Put the data back in. If
$A(8)$ does not come out to $13350$, the model is wrong regardless of
how the algebra looked. That is exactly what `verify_model` does below,
and it is a habit worth having on paper too.
""")

md(r"""
## Theory 7. Percentages, which are the same thing in English

A percentage change per period is a multiplier per period:

| the question says | the multiplier is |
| --- | --- |
| grows by $15\%$ a year | $1.15$ per year |
| depreciates at $15\%$ per annum | $0.85$ per year |
| decreased by $11\%$ over the period | $0.89$ over the period |
| nominal $4\%$ per year, compounded **quarterly** | $1+\frac{0.04}{4}=1.01$ per **quarter** |
| interest $1.5\%$ a month against inflation $0.8\%$ a month | $\dfrac{1.015}{1.008}$, or $1.007$ — see below |

**Nominal rate ÷ number of periods.** $4\%$ compounded quarterly is
$1\%$ four times, not $4\%$ once. The May 2025 TZ1 question makes this
its one-mark part (a) precisely because everything after it depends on
it.

**The exponent counts periods, not years.** After ten years of monthly
compounding the exponent is $120$, and this is where the archive puts
its named wrong answer: see the solution to Task 7.

**Inflation: the exam accepts both the exact version and the
approximation.** The *real* multiplier for an investment growing at $i$
while prices grow at $j$ is $\frac{1+i}{1+j}$. The markscheme for May
2025 TZ2 prints $r=c-i=1.5-0.8=0.7\%$ as **METHOD 1** and the quotient
$\frac{1.015}{1.008}=1.00694\ldots$ as **METHOD 2**, and pays the same
for either — the two differ in the fifth decimal place and land on the
same month. Worth knowing which is which anyway: subtraction is a first-
order approximation to the quotient, and it stops being close when the
rates get large.

**On Paper 1 the power gets expanded, not evaluated.** $1000(1.01)^4$ is
$1000\bigl(1+4(0.01)+6(0.01)^2+\dots\bigr)=1000+40+0.6+\dots=1041$ to the
nearest dinar, and $1000\times 0.9^{-4}$ is the Maclaurin series of
$(1-x)^{-4}$ at $x=0.1$. That is the binomial theorem from A7 doing
service here, and it is the reason both of these are Paper 1 questions
at all.
""")

md(r"""
## Task 7 🔴 — a whole Paper 2 model question

Alex purchases a car for €$30\,000$. The value of the car depreciates at
$15\%$ per annum.

**(a)** Find the value of the car after ten years, correct to two
decimal places.

Alex invests €$50\,000$ in a bank account paying compound interest of
$1.5\%$ per month. Inflation over the same period was $0.8\%$ per month.

**(b)** Find the number of months required for the **real** value of the
investment to first exceed €$55\,000$.

*May 2025 TZ2 Paper 2 Q4 — 6 marks, calculator allowed.*
""")

code(r"""
q7a = ...        # the value of the car after ten years
q7b = ...        # the number of months

check_num('7a', q7a, 6, 'D_71')
check_num('7b', q7b, 2, 'D_72')
""".replace("'D_71'", repr(D_71)).replace("'D_72'", repr(D_72)))

md(r"""
## Task 8 🟡 — the same percentages with no calculator

Bob invests $1000$ dinar in an account paying a nominal annual interest
rate of $4\%$ compounded **quarterly**. The amount after one complete
year can be written as $1000(1+k)^4$, $k\in\mathbb{Q}$.

**(a)** Write down the value of $k$.

**(b)** Hence or otherwise find the amount in the account after one
complete year, to the nearest dinar.

A car depreciated in value by $10\%$ each year and is worth $\$1000$
today. The first four terms of the Maclaurin expansion of $(1-x)^{-4}$
are $1+4x+10x^2+20x^3$.

**(c)** Estimate the value of the car four years ago.

*May 2025 TZ1 Paper 1 Q2 — 5 of its 7 marks. November 2025 TZ1 Paper 1
Q5(b) — 2 marks. Both Paper 1.*
""")

code(r"""
q8a = ...        # k, exactly
q8b = ...        # the amount after one year, to the nearest dinar
q8c = ...        # the value of the car four years ago

verify_exact('8a', q8a, Rational(1, 100))
check_num('8b', q8b, 4, 'D_82')
check_num('8c', q8c, 3, 'D_83')
""".replace("'D_82'", repr(D_82)).replace("'D_83'", repr(D_83)))

md(r"""
---
## Theory 8. The logistic model

$$x(t)=\frac{L}{1+Ce^{-kt}},\qquad L,C,k>0 .$$

Three constants, and the archive gives you them in a fixed order.

**$L$ is read off the page.** It is the value the population settles at
as $t\to\infty$, because $e^{-kt}\to 0$. When November 2025 says a wolf
population *"had a stable size of 200"* and the researchers *"decide to
let $L=200$"*, the assumption being made is that the long-run size after
the disruption will be the same as it was before. That sentence is a
mark.

**$C$ comes from $t=0$,** and it is easy because $e^{0}=1$:

$$40=\frac{200}{1+C}\;\Longrightarrow\;40+40C=200\;\Longrightarrow\;C=4 .$$

**$k$ comes from the second data point,** by Theory 5 again:
$70=\dfrac{200}{1+4e^{-5k}}$ unwinds to
$k=\tfrac15\ln\tfrac{28}{13}=0.153$.

**Then predict, and round to a whole animal.**
$x(10)=107.397\ldots\to 107$ wolves.

**The ten-second sanity check.** Evaluate your model at a large $t$. It
must approach $L$ from below. If it runs away or falls, the sign of $k$
is wrong — and a wrong sign there is invisible in the algebra and
obvious in the number.
""")

md(r"""
## Task 9 🔴 — a whole Paper 3 fit

A wolf population had a stable size of $200$. After a disruption it fell
to $40$, the area became protected, and the population began to grow
again. Let $x$ be the size of the population $t$ years after protection
began, modelled by $x=\dfrac{L}{1+Ce^{-kt}}$ with $L=200$.

At $t=0$ there are $40$ wolves; at $t=5$ there are $70$.

**(a)** Find $C$.  **(b)** Find $k$, to three significant figures.

**(c)** Write down the completed model.

**(d)** Predict the population at $t=10$, to the nearest whole number.

*November 2025 TZ1 Paper 3 Q2(a) — 7 of the question's 29 marks,
calculator allowed.*
""")

code(r"""
q9a = ...        # C
q9b = ...        # k
q9c = ...        # x(t), an expression in t with no letters left in it
q9d = ...        # the population at t = 10

verify_exact('9a', q9a, 4)
check_num('9b', q9b, 3, 'D_93')
verify_model('9c', q9c, [(0, 40), (5, 70)])
check_num('9d', q9d, 3, 'D_94')
""".replace("'D_93'", repr(D_93)).replace("'D_94'", repr(D_94)))

md(r"""
---
# Part III — the logarithm as a function

---
## Theory 9. Composition, domain, and scale

The first eight techniques treat $\ln$ as a tool. This one treats it as
a function with a graph, a domain and a range, and the archive asks
about all three.

**Composition.** $(f\circ g)(x)=f(g(x))$: put $g$ *inside* $f$. With
$f(x)=5(x+1)(x+3)$ and $g(x)=\ln x$,

$$(f\circ g)(x)=5(\ln x+1)(\ln x+3).$$

Solving $(f\circ g)(x)\le 40$ is then a two-stage job, and doing it in
one stage is how the mark is lost. **Solve for $\ln x$ first** — the
previous part of that same question gave $-5\le x\le 1$ for $f(x)\le
40$, so here $-5\le\ln x\le 1$ — and only then exponentiate, which is
allowed because $e^{u}$ is increasing and so preserves the inequality:

$$e^{-5}\le x\le e .$$

Applying $e$ to $-5$ and getting $-e^{5}$ is the standard error, and it
is the same error as writing $\ln\frac12=-\ln 2$ backwards.

**Domain of a composition.** $\operatorname{dom}(g\circ f)$ is the set
of $x$ in the domain of $f$ whose image $f(x)$ lies in the domain of
$g$. With $g=\ln$ that means $f(x)>0$:

$$5(x+1)(x+3)>0 \;\Longleftrightarrow\; x<-3 \ \text{ or }\ x>-1 .$$

Note what it is *not*: the domain of $f$, which is all of $\mathbb{R}$.
The composition is narrower than either function alone, and the marks
are split between finding the critical values and getting the two
inequalities the right way round.

**A logarithmic scale.** Loudness in decibels is
$L=10\log_{10}(I\times 10^{12})$. Two facts follow immediately from
Theory 1 and neither needs a calculator:

* doubling the intensity adds $10\log_{10}2\approx 3.01$ decibels —
  not double the loudness;
* going up $10$ decibels multiplies the intensity by $10$.

That is what a log scale is *for*: it turns multiplication into
addition. Every question about one is Theory 1 wearing a lab coat.

**And an equation given as $\ln(g(x))=\dots$** is not an equation for
$x$ — it is a definition of $g$, one exponential away:

$$\ln\bigl(g(x)\bigr)=x\ln\frac{S}{x}
  =\ln\left(\frac{S}{x}\right)^{x}
  \;\Longrightarrow\; g(x)=\left(\frac{S}{x}\right)^{x}.$$

The power law does the work; exponentiating is the last step, not the
first.
""")

md(r"""
## Task 10 🟡 — composition, both ways

The function $f$ is defined by $f(x)=5(x+1)(x+3)$, $x\in\mathbb{R}$; the
function $g$ by $g(x)=\ln x$, $x>0$. You may use that
$f(x)\le 40 \iff -5\le x\le 1$.

**(a)** Write down an expression for $(f\circ g)(x)$.

**(b)** Solve $(f\circ g)(x)\le 40$.

**(c)** Find the domain of $g\circ f$.

*May 2025 TZ1 Paper 1 Q10(d) and (e) — 6 marks, no calculator.*
""")

code(r"""
q10a = ...       # (f o g)(x)
q10b = ...       # the solution set of (f o g)(x) <= 40
q10c = ...       # the domain of g o f

verify_identity('10a', q10a, 5*(log(x) + 1)*(log(x) + 3))
verify_solution_set('10b', q10b, 5*(log(x) + 1)*(log(x) + 3) <= 40,
                    domain=Interval.open(0, oo))
verify_solution_set('10c', q10c, 5*(x + 1)*(x + 3) > 0)
""")

md(r"""
## Task 11 🟡 — a scale where multiplying is adding

The loudness $L$ of a sound, in decibels, is related to its intensity
$I$ units by $L=10\log_{10}(I\times 10^{12})$. Sound $\mathrm{S}_1$ has
intensity $10^{-6}$ units and loudness $60$ decibels. Sound
$\mathrm{S}_2$ has twice the intensity of $\mathrm{S}_1$.

**(a)** State the intensity of $\mathrm{S}_2$.

**(b)** Determine the loudness of $\mathrm{S}_2$.

**(c)** The maximum loudness of thunder was measured at $115$ decibels.
Find the corresponding intensity.

*May 2024 TZ2 Paper 2 Q3 — 6 marks, calculator allowed. Part (a) is
exact; (b) and (c) to three significant figures.*
""")

code(r"""
q11a = ...       # the intensity of S2, exactly
q11b = ...       # the loudness of S2
q11c = ...       # the intensity of the thunder

verify_exact('11a', q11a, 2*Rational(1, 10**6))
check_num('11b', q11b, 3, 'D_112')
check_num('11c', q11c, 3, 'D_113')
""".replace("'D_112'", repr(D_112)).replace("'D_113'", repr(D_113)))

md(r"""
## Task 12 🔴 — an exponential hiding behind a logarithm

Let $M_n(S)$ be the largest possible product of $n$ positive reals with
sum $S$. It has been proved that $M_n(S)=\left(\dfrac{S}{n}\right)^{n}$.

**(a)** Write down $M_3(12)$, $M_4(12)$ and $M_5(12)$, exactly.

The function $g$ is defined by $\ln\bigl(g(x)\bigr)=x\ln\dfrac{S}{x}$,
for $x\in\mathbb{R}^{+}$.

**(b)** Find $g(x)$, and so verify that $g(x)=M_x(S)$ for
$x\in\mathbb{Z}^{+}$.

The point of (b) is that the formula for a *whole number* of factors
extends to a real $x$ — which is what makes it differentiable, and is
why the rest of that Paper 3 question can maximise it.

*May 2023 TZ1 Paper 3 Q2(e) and (i) — 5 marks, calculator allowed, but
every answer here is exact.*
""")

code(r"""
q12a3 = ...      # M_3(12), exactly
q12a4 = ...      # M_4(12), exactly
q12a5 = ...      # M_5(12), exactly
q12b = ...       # g(x), in terms of S and x

verify_exact('12a-3', q12a3, 4**3)
verify_exact('12a-4', q12a4, 3**4)
verify_exact('12a-5', q12a5, Rational(12, 5)**5)
verify_identity('12b', q12b, exp(x*log(S/x)), var=x)
""")

md(r"""
---
## The same question on Paper 2

**May 2021 TZ2 Paper 2 Q5(c)** — *find, correct to the nearest 10 years,
the time for 25% of the carbon-14 to decay* — is the one place in this
topic where the markscheme prints both routes side by side and pays the
same for either:

> **EITHER** using an appropriate graph to attempt to solve for $t$
> **(M1)**
> **OR** manipulating logs to attempt to solve for $t$ **(M1)**
> $\ln 0.75=-\dfrac{\ln 2}{5730}t$

So the calculator is not a shortcut past the mathematics; it is one of
two accepted methods, and the marks for setting up $75=100e^{-kt}$ come
first either way. The cell below does both and prints them together.

The interesting part is what the calculator does **not** give you: the
exact form. Notice that the graph route lands on $2378.16\ldots$ and
stops, while the algebra route lands on
$t=\dfrac{5730\ln\frac43}{\ln 2}$, which you can then round to anything
the question asks for. On Paper 2 that difference costs nothing. In part
(b) of the same question, where the answer *is* $\frac{\ln 2}{5730}$, it
costs the whole mark.
""")

code(r"""
kc = log(2)/5730
model = 100*exp(-kc*t)

exact = list(solveset(Eq(model, 75), t, Interval(0, oo)))[0]
print('exact time for 25% to decay:', exact, '   ( = 5730*ln(4/3)/ln 2 )')
print('as a decimal:               ', nsolve(Eq(model, 75), t, 2000))
print('to the nearest 10 years:    ', 10*round(float(nsolve(Eq(model, 75), t, 2000))/10))
print()
print('and the check that the model is the right one:')
verify_model('by graph', model, [(0, 100), (5730, 50)])
""")

md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. For each one, name the technique — **do not solve
anything.** This is the cheapest half-hour in the whole practicum: on
the exam the difference between a solved question and an unsolved one is
usually the first thirty seconds.

Use these codes:

`laws` · the three log laws  |  `base` · change of base  |
`logeq` · log equation  |  `powers` · laws of exponents  |
`takelogs` · take logs of both sides  |  `fit` · fit a model to data  |
`percent` · percentages as a power  |  `logistic` · the logistic model  |
`function` · the logarithm as a function

1. Let $\log_{10}2=p$. Find $\log_{10}50$ in terms of $p$.
2. Solve $\log_9 x+\log_3 x=6$.
3. Solve $\log_5(x+3)+\log_5(x-1)=1$.
4. Given $e^{2a}=7$, write $e^{-6a}$ as a fraction.
5. Solve $3^{\,x+1}=200$, giving your answer to three significant
   figures.
6. A culture has $500$ bacteria at noon and $1200$ at 3 pm and grows as
   $N=N_0e^{kt}$. Estimate the count at 6 pm.
7. A machine bought for $\$8000$ loses $12\%$ of its value each year.
   Find its value after seven years.
8. A fish population cannot exceed $5000$; it was $400$ when counting
   began and $900$ after two years. Predict year five.
9. Find the domain of $h(x)=\ln(x^2-4)$.
10. The half-life of a substance is $12$ hours. Find the time for $90\%$
    of it to decay.
11. Solve $\log_4 x=\log_{16}(x+6)$.
12. A town of $20\,000$ shrinks by $3\%$ per year for eight years, then
    is modelled as $Pe^{kt}$ from that point. Find $k$.
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

**November 2022 Paper 2 Q4 — 7 marks. Target: 11 minutes.**

Close everything above. Calculator allowed.

> The population of a town $t$ years after 1 January 2014 can be
> modelled by
> $$P(t)=15\,000e^{kt},\qquad k<0,\ t\ge 0 .$$
> It is known that between 1 January 2014 and 1 January 2022 the
> population decreased by $11\%$.
>
> Use this model to estimate the population of this town on 1 January
> 2041.

Seven marks for one sentence, and five of them are set-up. Before
touching the calculator, write down three things: what $t=0$ is, what
$t$ is on 1 January 2022, and what $t$ is on 1 January 2041.

**Attempt log.** Copy this line and add a date and a time each pass.

```
2026-09-01 — 
```
""")

code(r"""
qt_model = ...   # the population model, with k in place
qt = ...         # the population on 1 January 2041

verify_model('timed model', qt_model, [(0, 15000), (8, 13350)])
check_num('timed answer', qt, 3, 'D_T1')
""".replace("'D_T1'", repr(D_T1)))

md(r"""
---
# 🔑 Solutions

Read one only after you have an answer of your own — even a wrong one.
Each solution names its source and the marks it carries.

---
### Task 1 — the laws in both directions
*May 2025 TZ3 P1 Q1(a), 3 marks · May 2025 TZ1 P1 Q8(a), 2 marks*

**(a)** Factorise first, because there is no law for a sum:
$$24=2^3\times 3
  \;\Longrightarrow\;
  \log_{10}24=\log_{10}2^3+\log_{10}3=3\log_{10}2+\log_{10}3=3p+q .$$
The markscheme awards **(M1)** for using $\log ab=\log a+\log b$ or
$\log a^m=m\log a$, **(A1)** for reaching $3\log_{10}2+\log_{10}3$ with
the arguments actually being $2$ and $3$, and **A1** for $3p+q$.

**(b)** The loose $1$ has to join the logarithm:
$$1+\log_2 n=\log_2 2+\log_2 n=\log_2(2n).$$
Then, since $n\ge 1$ gives $2n\ge n+1$, and since $\log_2$ is
**increasing**,
$$\log_2(2n)\ge\log_2(n+1),$$
which is the statement. The second half is an **R1** and it is for
naming monotonicity out loud; the inequality $2n\ge n+1$ alone does not
earn it.

---
### Task 2 — one base at a time
*May 2025 TZ3 P1 Q1(b), 2 marks · May 2024 TZ1 P1 Q2, 5 marks*

**(a)** $\log_3 8=\dfrac{\log_{10}8}{\log_{10}3}
        =\dfrac{3\log_{10}2}{\log_{10}3}=\dfrac{3p}{q}$.
Argument on top, base underneath.

**(b)** $\log_{10}\dfrac1a=\log_{10}1-\log_{10}a=-\log_{10}a=-\dfrac13$.
Equivalently $\log_{10}a^{-1}=-\log_{10}a$.

**(c)** $\log_{1000}a=\dfrac{\log_{10}a}{\log_{10}1000}
        =\dfrac{1/3}{3}=\dfrac19$.
The three in the denominator is $\log_{10}10^3$ — the same shortcut as
$\log_{b^m}a=\frac1m\log_b a$.

---
### Task 3 — two bases, one unknown
*November 2025 TZ3 P1 Q4, 5 marks*

Everything is a power of $2$: $8=2^3$ and $4=2^2$. So
$$3\log_8 10x=3\cdot\frac{\log_2 10x}{3}=\log_2 10x,
  \qquad
  \log_4 x=\frac{\log_2 x}{2}=\log_2 x^{1/2}=\log_2\sqrt{x}.$$
The equation becomes
$$\log_2 10x-\log_2\sqrt{x}=1
  \;\Longrightarrow\;
  \log_2\frac{10x}{\sqrt x}=\log_2 2
  \;\Longrightarrow\;
  10\sqrt{x}=2 ,$$
so $\sqrt{x}=\frac15$ and $x=\dfrac{1}{25}$.

Both **M** marks are for method seen anywhere — power/quotient rule and
change of base — and they are independent, so partial credit survives a
wrong order. The last three marks are the correct equation in one base,
the correct equation without logarithms, and the answer. Note the trap
that the mark scheme implies by printing $10\sqrt x=2$ separately:
stopping at $\sqrt x=\frac15$ answers a different question.

---
### Task 4 — the loose $-1$, and the domain
*November 2025 TZ1 P1 Q2, 6 marks*

**(a)** $x^2-8x+7=(x-7)(x-1)$ and $x^2-1=(x-1)(x+1)$, so
$$\frac{x}{(x-7)(x-1)}\times\frac{(x-1)(x+1)}{x+1}=\frac{x}{x-7}.$$

**(b)** The $-1$ is $\log_2\frac12$, or equivalently move it across as
$1=\log_2 2$. Collapsing both sides,
$$\log_2\frac{x(x^2-1)}{(x^2-8x+7)(x+1)}=\log_2 2 .$$
The fraction inside is exactly what part (a) simplified, so it is
$\dfrac{x}{x-7}$, and removing the logarithms gives
$$\frac{x}{x-7}=2\;\Longrightarrow\;x=2x-14\;\Longrightarrow\;x=14 .$$
$14>7$, so every argument is positive and the root stands.

**Why the domain matters even though nothing was discarded here.** The
condition $x>7$ came from part (a) and is what makes $x^2-8x+7>0$. Had
the algebra produced a second root below $7$, it would have been
manufactured by the removal step, not present in the original equation —
and `verify_root_set` says so in exactly those words.

---
### Task 5 — the substitution that does the work
*May 2021 TZ2 P1 Q11(c) and (d), 4 marks*

**(a)** $e^{T}=1+v_0$, so $e^{-T}=\dfrac{1}{1+v_0}$. Reciprocal, not the
same thing — this is the one line the two marks of (c) are built on.

**(b)** Split the exponent, then substitute:
$$v(T-k)=(1+v_0)e^{-(T-k)}-1
        =(1+v_0)e^{-T}e^{k}-1
        =(1+v_0)\cdot\frac{1}{1+v_0}\cdot e^{k}-1
        = e^{k}-1 .$$
The markscheme's METHOD 2 is shorter still: write $1+v_0$ as $e^{T}$ from
the start, and $e^{T}e^{-(T-k)}=e^{k}$ falls out in one step.

For (d), *deduce*: replacing $k$ by $-k$ turns "$k$ seconds before" into
"$k$ seconds after", so $v(T+k)=e^{-k}-1$. Two marks for one
substitution.

**And the part (e) that follows,** though it is outside this practicum:
$v(T-k)+v(T+k)=e^{k}+e^{-k}-2\ge 0$ because $e^{k}+e^{-k}\ge 2$ by AM–GM.
The particle is faster before the turning point than it is slow after
it.

---
### Task 6 — a half-life, exactly and then numerically
*May 2021 TZ2 P2 Q5, 7 marks*

**(a)** Half the original amount after $5730$ years:
$$50=100e^{-5730k}
  \;\Longrightarrow\;
  e^{-5730k}=\tfrac12
  \;\Longrightarrow\;
  e^{5730k}=2
  \;\Longrightarrow\;
  5730k=\ln 2
  \;\Longrightarrow\;
  k=\frac{\ln 2}{5730}.$$
The markscheme's note is unusually generous — *"award full marks for at
least two correct algebraic steps seen"* — and the reason is that there
are several routes. The route above avoids $\ln\frac12$ entirely.

**(b)** $25\%$ has decayed means $75$ units **remain**, not $25$:
$$75=100e^{-\frac{\ln 2}{5730}t}
  \;\Longrightarrow\;
  \ln 0.75=-\frac{\ln 2}{5730}t
  \;\Longrightarrow\;
  t=\frac{5730\ln\frac43}{\ln 2}=2378.16\ldots$$
To the nearest $10$ years, $t=2380$.

**(c)** $A(t)=100e^{-\frac{\ln 2}{5730}t}$, equivalently
$100\cdot 2^{-t/5730}$. Both pass the check, because the check puts
$t=0$, $t=5730$ and $t=11460$ back in and asks for $100$, $50$ and $25$.

---
### Task 7 — a whole Paper 2 model question
*May 2025 TZ2 P2 Q4, 6 marks*

**(a)** Depreciation at $15\%$ is a multiplier of $0.85$:
$$30\,000\times 0.85^{10}=5906.2321\ldots\to €5906.23 .$$
Two decimal places, because the question says so and because it is
money.

**(b)** The real multiplier per month, exactly, is a **quotient**:
$$\frac{1+0.015}{1+0.008}=\frac{1.015}{1.008}=1.00694\ldots$$
Then
$$50\,000(1.00694\ldots)^{n}>55\,000
  \;\Longrightarrow\;
  n>\frac{\ln 1.1}{\ln 1.00694\ldots}=13.7722\ldots$$
so the first month is $n=14$.

The markscheme's own **METHOD 1** is the approximation
$r=1.5-0.8=0.7\%$, which gives $n>\frac{\ln 1.1}{\ln 1.007}=13.6633\ldots$
and the same answer, and it earns full marks. Either is fine. It also
awards a mark for one correct crossover value: with $0.7\%$, $n=13$
gives €$54\,746.09$ and $n=14$ gives €$55\,129.31$.

**The wrong answer the markscheme names.** $164$ months, worth
**(A1)(M1)(A0)(A0)** — the method is right and both answer marks are
gone. It comes from reading $0.7\%$ as an *annual* rate and compounding
it monthly: $\frac{\ln 1.1}{\ln(1+0.007/12)}=163.5\ldots$ The period
was in the question all along; the arithmetic never noticed.

---
### Task 8 — the same percentages with no calculator
*May 2025 TZ1 P1 Q2, 5 of 7 marks · November 2025 TZ1 P1 Q5(b), 2 marks*

**(a)** *Nominal* $4\%$ *compounded quarterly* means the rate per quarter
is $\dfrac{4\%}{4}=1\%$, so $k=\dfrac{4}{400}=\dfrac{1}{100}=0.01$. One
mark, and everything downstream fails without it.

**(b)** No calculator, so expand rather than evaluate. With
$(1+x)^4=1+4x+6x^2+4x^3+x^4$ at $x=\frac{1}{100}$,
$$1000\left(1+\tfrac1{100}\right)^4
  =1000+40+0.6+0.004+\ldots=1040.6\ldots\to 1041\ \text{dinar}.$$
The first two terms already give $1040$; the third decides the rounding.

**(c)** Four years of $10\%$ depreciation multiply by $0.9^4$, so the
value four years ago is $1000\times 0.9^{-4}=1000(1-0.1)^{-4}$. With the
given expansion at $x=0.1$,
$$(1-x)^{-4}\approx 1+4(0.1)+10(0.01)+20(0.001)=1.52
  \;\Longrightarrow\; \$1520 .$$
(The exact value is $1000/0.6561=1524.16\ldots$; the series truncated at
$x^3$ gives $1520$, which is what the question asks for.)

---
### Task 9 — a whole Paper 3 fit
*November 2025 TZ1 P3 Q2(a), 7 marks*

**(a)** At $t=0$, $e^{0}=1$:
$$40=\frac{200}{1+C}\;\Longrightarrow\;40+40C=200\;\Longrightarrow\;C=4 .$$

**(b)** At $t=5$:
$$70=\frac{200}{1+4e^{-5k}}
  \;\Longrightarrow\;
  1+4e^{-5k}=\frac{20}{7}
  \;\Longrightarrow\;
  e^{-5k}=\frac{13}{28}
  \;\Longrightarrow\;
  k=\frac15\ln\frac{28}{13}=0.153451\ldots\to 0.153 .$$
The markscheme prints it as $-\frac15\ln\frac{130}{280}$, which is the
same number written with the minus still inside.

**(c)** $x(t)=\dfrac{200}{1+4e^{-0.153451\ldots t}}$.

**(d)** $x(10)=\dfrac{200}{1+4e^{-1.53451\ldots}}=107.397\ldots\to 107$
wolves. Whole animals, so a whole number.

**What the rest of that question does with this,** for context: it
compares the logistic prediction against a Gompertz model, which
satisfies $\frac{dx}{dt}=ax\ln\frac{200}{x}$ and integrates — by
separation of variables, technique 2 of E7 — to $\ln x=\ln 200-Ae^{-at}$.
That model predicts $101$. The measured population turned out to be
$85$, so **both models overestimate and the Gompertz one is closer**,
which is the one-mark part (c).

---
### Task 10 — composition, both ways
*May 2025 TZ1 P1 Q10(d) and (e), 6 marks*

**(a)** $(f\circ g)(x)=f(\ln x)=5(\ln x+1)(\ln x+3)$. The markscheme
also accepts $5(\ln x+2)^2-5$ and $5(\ln x)^2+20\ln x+15$.

**(b)** Part (c) of the same question established
$f(x)\le 40\iff -5\le x\le 1$. Replacing $x$ by $\ln x$,
$$-5\le\ln x\le 1
  \;\Longrightarrow\;
  e^{-5}\le x\le e .$$
Exponentiating preserves the inequalities because $e^{u}$ is increasing.
The **(M1)** is precisely for *"attempt to replace $x$ with $\ln x$
using their solution to part (c)"* — that is, for not solving the
quadratic again.

**(c)** $(g\circ f)(x)=\ln\bigl(f(x)\bigr)$ needs $f(x)>0$:
$$(x+1)(x+3)>0\;\Longrightarrow\;x<-3\ \text{ or }\ x>-1 ,$$
that is $(-\infty,-3)\cup(-1,\infty)$. Two separate marks: one for the
critical values $-3$ and $-1$, one for the inequalities pointing the
right way. Writing $-3<x<-1$ — the *inside* of the parabola, where $f$
is negative — collects the first and loses the second.

---
### Task 11 — a scale where multiplying is adding
*May 2024 TZ2 P2 Q3, 6 marks*

**(a)** Twice $10^{-6}$ is $2\times 10^{-6}$. One mark, and it is a mark
for reading.

**(b)** $$L=10\log_{10}(2\times 10^{-6}\times 10^{12})
        =10\log_{10}(2\times 10^{6})
        =10\left(6+\log_{10}2\right)
        =60+10\log_{10}2=63.0102\ldots\to 63.0 .$$
The markscheme accepts $60+10\log_{10}2$ as a final answer. Note what
did **not** happen: doubling the intensity did not double the loudness,
it added about $3$ decibels. That is the whole idea of a log scale.

**(c)** $$115=10\log_{10}(I\times 10^{12})
  \;\Longrightarrow\;
  I\times 10^{12}=10^{11.5}
  \;\Longrightarrow\;
  I=10^{-0.5}=\frac{1}{\sqrt{10}}=0.316227\ldots\to 0.316 .$$
Exact forms $10^{-0.5}$ and $\frac{1}{\sqrt{10}}$ are accepted too.

---
### Task 12 — an exponential hiding behind a logarithm
*May 2023 TZ1 P3 Q2(e) and (i), 5 marks*

**(a)** Straight into $\left(\frac{S}{n}\right)^{n}$ with $S=12$:
$$M_3(12)=4^3=64,\qquad
  M_4(12)=3^4=81,\qquad
  M_5(12)=2.4^5=79.62624 .$$
Three separate one-mark parts, and the sequence is the point: the
product rises, peaks somewhere between $n=4$ and $n=5$, and falls. The
next parts of that question find the peak — it is at $x=S/e$, which for
$S=12$ is $4.41$.

**(b)** Use the power law on the right-hand side and then exponentiate:
$$\ln\bigl(g(x)\bigr)=x\ln\frac{S}{x}=\ln\left(\frac{S}{x}\right)^{x}
  \;\Longrightarrow\;
  g(x)=\left(\frac{S}{x}\right)^{x},$$
which is $M_x(S)$ whenever $x$ is a positive integer. **M1** for moving
the $x$ up as a power, **A1** for $g$ itself.

**Why anyone would bother.** $M_n(S)$ is defined only for whole $n$ —
you cannot have $4.41$ factors. Writing it as $g$, a function of a real
variable that agrees with $M_n$ at the integers, is what makes it
differentiable, and differentiating is how the question then finds the
best $n$. Extending a discrete formula to a continuous one by way of
logarithms is a move worth recognising; it is the same move that turns
compound interest into $e^{rt}$.

---
### On the timer
*November 2022 Paper 2 Q4, 7 marks*

$t=0$ is 1 January 2014, so 1 January 2022 is $t=8$ and 1 January 2041
is $t=27$.

A decrease of $11\%$ leaves $89\%$:
$$P(8)=0.89\times 15\,000=13\,350
  \;\Longrightarrow\;
  15\,000e^{8k}=13\,350
  \;\Longrightarrow\;
  e^{8k}=0.89
  \;\Longrightarrow\;
  k=\frac{\ln 0.89}{8}=-0.014566\ldots$$
Then
$$P(27)=15\,000e^{-0.014566\ldots\times 27}=10\,122.3\ldots$$
The markscheme accepts $10\,100$ (three significant figures) or
$10\,122$.

**Where the seven marks are.** Recognising $P(0)=15\,000$; computing
$0.89\times 15\,000$; recognising $t=8$; substituting both into the
model; $k=\frac{\ln 0.89}{8}$; substituting $t=27$; the number. Six of
the seven are before the exponential is ever evaluated, and the two most
commonly lost are the third and the sixth — the two that are only about
what $t$ means.

---
### What to do when it goes wrong

**Your model gives the wrong number at a data point.** The constants are
not the problem — the time is. Write down what $t=0$ is and recount.

**Your answer is off by a factor you cannot find.** Check whether a
percentage went in as $0.11$ where $0.89$ was meant, or as $1.04$ where
$1.01$ was meant.

**Your logarithmic equation has a root the check rejects.** Removing
logarithms is not reversible. Put the root back into the *original*
equation and look at every argument.

**Your inequality came out backwards.** You applied $e^{u}$ or $\ln$ to
one side only, or to a negative number. Both are increasing functions:
they never flip an inequality, and they never accept a negative
argument.

**Your exact answer became a decimal.** On Paper 1 that is the whole
mark. Keep $\ln 2$, keep $\frac{1}{9}$, keep $3p+q$; the calculator
comes out only when the paper number says it may.
""")


def build():
    nb = {"cells": cells,
          "metadata": {"kernelspec": {"display_name": "Python 3",
                                      "language": "python", "name": "python3"},
                       "language_info": {"name": "python", "version": "3.12"}},
          "nbformat": 4, "nbformat_minor": 5}
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    codes = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f'{NOTEBOOK}: ячеек {len(cells)}, из них с кодом {codes}')


if __name__ == '__main__':
    build()
