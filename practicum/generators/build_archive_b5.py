"""Собирает архивный ноутбук B5: весь корпус темы, по приёмам, подряд.

Третий ноутбук в формате, опробованном на B4 и C3. Практикум B5 учит —
лестница, теория, уровни, тренажёр. Этот ноутбук не учит, он даёт набивать
руку: вопрос, ячейка для ответа с мгновенной проверкой, разбор в конце.

Внутри — показательные и логарифмические модели из архива AA HL, сессии
May 2021 — November 2025: 36 вопросов и 83 балла, разложенные по девяти
приёмам карточки functions-exponential-log-models.yaml.

Почему 36, а не 37. Корпус числит за темой 37 блоков (85 баллов). Один из
них, 2025-NOV-TZ3-P1-Q08-A, помечен темой mathematical_models, но ни
показательной, ни логарифмической функции в нём нет: это «show that
T = 500 sec θ + (2500 − 1000 tan θ)/3» для задачи о времени в пути по пляжу.
Он исключён и записан в corpus_issues карточки. Больше ничего не убрано
и ничего не добавлено — здесь ровно тема, как её видит корпус.

Отличие от C3 в пропорции: там девять хешей из тридцати семи, здесь четыре
из тридцати трёх. Причина в том, что тема почти всюду даёт либо точную
форму (ln 2 / 5730, 10^{-1/2}, 60 + 10 log 2), либо модель, а модель
проверяется подстановкой данных из условия и эталона не требует вовсе.
Хеш остаётся там, где ответ — округление: 2380 лет, 10100 человек,
1041 динар, 5906.23 евро.

Три вопроса кода не имеют вовсе: 5.1 — «show that A₀ = 100» на один балл,
где после подстановки t = 0 проверять нечего, а 8.1 и 8.5 просят назвать
допущение и прокомментировать два предсказания словами.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
по нему practicum/tests/check_archive_b5.py прогоняет весь ноутбук
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

NOTEBOOK = os.path.join(ROOT,
                        'practicum/functions/archive-b5-exponential-log-models.ipynb')


def dn(value, sf=3):
    return digest(sig(value, sf))


# --- хеши для тех четырёх ответов, что являются округлением ---
D_53 = dn(2380)                                   # лет до распада 25%
D_67 = dn(15000 * sp.exp(sp.log(R(89, 100)) / 8 * 27))   # население в 2041
D_72 = dn(1041, 4)                                # динаров через год
D_73 = dn(30000 * R(85, 100)**10, 6)              # евро за машину через 10 лет

ANSWERS = {
    'q1_1': '3*p + q',
    'q1_2': '-Rational(1, 3)',
    'q1_3': 'log(2*n, 2)',

    'q2_1': '3*p/q',
    'q2_2': 'Rational(1, 9)',
    'q2_3': '[Rational(1, 25)]',

    'q3_1': '[14]',

    'q4_1': '1/(1 + v0)',
    'q4_2': 'exp(-k) - 1',
    'q4_3': 'log(3)',

    'q5_2': 'log(2)/5730',
    'q5_3': '2380',

    'q6_1': '310',
    'q6_2a': '60',
    'q6_2b': '0',
    'q6_3': '36',
    'q6_4': '64',
    'q6_5': '81',
    'q6_6': 'Rational(12, 5)**5',
    'q6_7a': '15000*exp(log(Rational(89, 100))/8*t)',
    'q6_7b': '15000*exp(log(Rational(89, 100))/8*27)',

    'q7_1': 'Rational(1, 100)',
    'q7_2': '1041',
    'q7_3': '30000*Rational(85, 100)**10',
    'q7_4': '14',
    'q7_5': '1520',

    'q8_2': '4',
    'q8_3': 'log(Rational(28, 13))/5',
    'q8_4a': '200/(1 + 4*exp(-log(Rational(28, 13))/5*t))',
    'q8_4b': '107',

    'q9_1': '2*Rational(1, 10**6)',
    'q9_2': '60 + 10*log(2, 10)',
    'q9_3': '10**Rational(-1, 2)',
    'q9_4a': '5*(log(x) + 1)*(log(x) + 3)',
    'q9_4b': 'Interval(exp(-5), E)',
    'q9_5': 'Union(Interval.open(-oo, -3), Interval.open(-1, oo))',
    'q9_6': '(S/x)**x',
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
# B5 archive: exponential and logarithmic models

**Every past-paper question on this topic, grouped by technique.** Not a
practicum — a drill. There is no theory here and no ladder to climb: the
theory is in *Practicum B5*, and this notebook is what you open afterwards,
when the only thing left is to do them all until the moves are automatic.

**What is inside.** The whole of `functions.logarithmic_functions`,
`functions.exponential_models`, `functions.mathematical_models` and
`number_algebra.exponential_models`, sessions May 2021 — November 2025:
**36 questions, 83 marks**, in nine sections, one section per technique.

The corpus records 37 blocks and 85 marks. The one difference is a question
filed under `mathematical_models` that has neither an exponential nor a
logarithm in it — *"show that $T=500\sec\theta+\frac{2500-1000\tan\theta}{3}$"*,
about the time to walk across a beach. Nothing else is left out and nothing
is added: this is the topic exactly as the corpus sees it.

**Sixteen questions are Paper 1, eight are Paper 2, twelve are Paper 3.**
The split by paper is also a split by what the answer looks like: Paper 1
wants $\frac{\ln 2}{5730}$ and $3p+q$, Paper 2 and 3 want $2380$ and $107$.
If a Paper 1 answer of yours has a decimal point in it, look again.

**How to work.** Read the question, answer in the cell below it, run the
cell. The check is not a comparison with a stored answer. A model is right
when it reproduces the data it was fitted to — `verify_model` puts each pair
from the question back into whatever you wrote. A root is right when it
satisfies the equation. An expression *in terms of $p$ and $q$* is right when
it uses only those letters and comes out to the right number. So an answer
arrived at by a wrong route still has to be true.

Four checks do compare a hash, and they are the same case each time: the
answer is a rounding — $2380$ years, $10\,100$ people, $1041$ dinar,
€$5906.23$ — and a rounded number satisfies nothing exactly, so there is
nothing to substitute it into.

Three questions have no cell at all. 5.1 is a one-mark *"show that
$A_0=100$"* where substituting $t=0$ leaves nothing to check; 8.1 and 8.5
ask you to state an assumption and to comment on two predictions, in words.

Leave a cell blank and it prints ⬜ and moves on, which means you can run
the whole notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before — and read the markscheme note in it,
because that is where the marks actually are.

**The nine sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The three log laws | 3 | 7 |
| 2 | Change of base | 3 | 10 |
| 3 | An equation with the unknown under a logarithm | 1 | 4 |
| 4 | The laws of exponents, and the relation you were handed | 3 | 5 |
| 5 | Taking logarithms of both sides | 3 | 7 |
| 6 | Reading a model, and fitting one | 7 | 15 |
| 7 | Percentages as a power | 5 | 13 |
| 8 | The logistic model | 5 | 8 |
| 9 | The logarithm as a function | 6 | 14 |

Sections 1–3 move the unknown **up**, out from under a logarithm. Sections
4–8 move it **down**, out of an exponent. Section 9 stops using the
logarithm as a tool and starts asking about it as a function.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/functions to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Interval, Union, solveset, Rational

language('en')                 # this notebook is in English, and so are the checks

a, b, n, p, q, r = symbols('a b n p q r')
S, T, v0 = symbols('S T v0', positive=True)
# S here is the sum from question 6.3, and it shadows sympy's S. Where a check
# wants "all the reals", write Interval(-oo, oo) rather than S.Reals.

print('ready; sympy', sp.__version__)
print('in terms of p and q: ', 3*p + q)
print('an exact log:        ', log(2)/5730)
print('a model in t:        ', 15000*exp(log(Rational(89, 100))/8*t))
print('a set of values:     ', Interval(exp(-5), E))
print('a list of roots:     ', [Rational(1, 25)])
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. The three log laws

$\log_b MN=\log_b M+\log_b N$, $\log_b\frac{M}{N}=\log_b M-\log_b N$,
$\log_b M^r=r\log_b M$ — and there is no law for $\log_b(M+N)$. The loose
number next to a logarithm has to become one: $1=\log_b b$.
""")

md(r"""
### 1.1 — *May 2025 TZ3 Paper 1 Q1(a), 3 marks*

Let $\log_{10}2=p$ and $\log_{10}3=q$. Find an expression for $\log_{10}24$
in terms of $p$ and $q$.
""")

code(r"""
q1_1 = ...       # log_10 24, in terms of p and q

verify_in_terms_of('1.1', q1_1, log(24, 10), {p: log(2, 10), q: log(3, 10)})
""")

md(r"""
### 1.2 — *May 2024 TZ1 Paper 1 Q2(a), 2 marks*

It is given that $\log_{10}a=\dfrac13$, where $a>0$. Find the value of
$\log_{10}\dfrac{1}{a}$.
""")

code(r"""
q1_2 = ...       # log_10 (1/a)

verify_exact('1.2', q1_2, -Rational(1, 3))
""")

md(r"""
### 1.3 — *May 2025 TZ1 Paper 1 Q8(a), 2 marks*

Show that $1+\log_2 n\ge\log_2(n+1)$ for $n\in\mathbb{Z}^{+}$.

The answer is printed in the question, so the cell checks the step that earns
the marks: write $1+\log_2 n$ as a **single logarithm**.
""")

code(r"""
q1_3 = ...       # 1 + log_2 n as one logarithm, e.g. log(<something>, 2)

verify_identity('1.3', q1_3, 1 + log(n, 2), var=n)
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. Change of base

$\log_b a=\dfrac{\log_c a}{\log_c b}$ — the argument on top, the base
underneath. Until two logarithms share a base, no law from section 1 applies
to them. When the bases are powers of one number,
$\log_{b^{m}}a=\frac1m\log_b a$ does it in one line.
""")

md(r"""
### 2.1 — *May 2025 TZ3 Paper 1 Q1(b), 2 marks*

With $\log_{10}2=p$ and $\log_{10}3=q$, find an expression for $\log_3 8$ in
terms of $p$ and $q$.
""")

code(r"""
q2_1 = ...       # log_3 8, in terms of p and q

verify_in_terms_of('2.1', q2_1, log(8, 3), {p: log(2, 10), q: log(3, 10)})
""")

md(r"""
### 2.2 — *May 2024 TZ1 Paper 1 Q2(b), 3 marks*

It is given that $\log_{10}a=\dfrac13$, where $a>0$. Find the value of
$\log_{1000}a$.
""")

code(r"""
q2_2 = ...       # log_1000 a

verify_exact('2.2', q2_2, Rational(1, 9))
""")

md(r"""
### 2.3 — *November 2025 TZ3 Paper 1 Q4, 5 marks*

Solve the equation $3\log_8 10x-\log_4 x=1$ for $x>0$.

Enter a **list** of roots: `[Rational(1, 5)]`, `[4, 9]`.
""")

code(r"""
q2_3 = [...]     # all roots with x > 0

verify_roots('2.3', q2_3, 3*log(10*x, 8) - log(x, 4) - 1, (0.0001, 100))
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. An equation with the unknown under a logarithm

Bases first, then collapse each side to one logarithm, then remove them — and
then check that every argument was positive at the root you found. Removing
logarithms is not reversible, and it invents roots.
""")

md(r"""
### 3.1 — *November 2025 TZ1 Paper 1 Q2(b), 4 marks*

Part (a) of this question established that for $x>7$,
$$\frac{x}{x^2-8x+7}\times\frac{x^2-1}{x+1}\equiv\frac{x}{x-7}.$$

Hence, or otherwise, solve
$$\log_2\bigl[x(x^2-1)\bigr]-1=\log_2\bigl[(x^2-8x+7)(x+1)\bigr].$$
""")

code(r"""
q3_1 = [...]     # all roots

verify_root_set('3.1', q3_1,
                Eq(log(x*(x**2 - 1), 2) - 1, log((x**2 - 8*x + 7)*(x + 1), 2)),
                domain=Interval.open(7, oo))
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. The laws of exponents, and the relation you were handed

$a^{m}a^{n}=a^{m+n}$ and $(a^{m})^{n}=a^{mn}$, used not to tidy an answer but
to make a substitution possible. And $c=e^{\ln c}$ for every $c>0$, which is
the definition of $\ln$ read backwards.
""")

md(r"""
### 4.1 — *May 2021 TZ2 Paper 1 Q11(c), 2 marks*

A particle has velocity $v(t)=(1+v_0)e^{-t}-1$, and the time $T$ at which its
displacement is greatest satisfies $e^{T}=1+v_0$. By using that result, show
that $v(T-k)=e^{k}-1$.

The answer is printed in the question, so the cell checks the substitution the
marks are for: write $e^{-T}$ in terms of $v_0$.
""")

code(r"""
q4_1 = ...       # e^(-T), in terms of v0

verify_identity('4.1', q4_1, 1/(1 + v0), var=v0)
""")

md(r"""
### 4.2 — *May 2021 TZ2 Paper 1 Q11(d), 2 marks*

Similarly, let $v(T+k)$ represent the particle's velocity $k$ seconds after it
reaches its maximum displacement. **Deduce** a similar expression for
$v(T+k)$ in terms of $k$.
""")

code(r"""
q4_2 = ...       # v(T + k), in terms of k

verify_exact('4.2', q4_2, exp(-k) - 1)
""")

md(r"""
### 4.3 — *May 2025 TZ1 Paper 1 Q7(a), 1 mark*

Consider the complex number $z=3^{\,i-1}$. Write the integer $3$ in the form
$e^{a}$, where $a\in\mathbb{R}$.
""")

code(r"""
q4_3 = ...       # a

verify_exact('4.3', q4_3, log(3))
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. Taking logarithms of both sides

Isolate the power first, then take logarithms, then bring the exponent down.
Keep the exact form to the last line: rounding $k$ and then using it moves the
answer by more than the rounding.
""")

md(r"""
### 5.1 — *May 2021 TZ2 Paper 2 Q5(a), 1 mark*

The amount $A$ of carbon-14 present in a plant $t$ years after its death is
modelled by $A=A_0e^{-kt}$, $t\ge 0$, with $A_0,k>0$. At the time of death a
plant is defined to have $100$ units of carbon-14.

Show that $A_0=100$.

*One mark, and once you have put $t=0$ there is nothing left to check — so
this question has no cell. Write the line down anyway; it is a mark.*
""")

md(r"""
### 5.2 — *May 2021 TZ2 Paper 2 Q5(b), 3 marks*

The time taken for half the original amount of carbon-14 to decay is known to
be $5730$ years. Show that $k=\dfrac{\ln 2}{5730}$.

The answer is printed in the question; enter it as an exact expression so the
check can confirm that it is what your working produced.
""")

code(r"""
q5_2 = ...       # k, exactly

verify_exact('5.2', q5_2, log(2)/5730)
""")

md(r"""
### 5.3 — *May 2021 TZ2 Paper 2 Q5(c), 3 marks*

Find, correct to the nearest $10$ years, the time taken after the plant's
death for $25\%$ of the carbon-14 to decay.
""")

code(r"""
q5_3 = ...       # the time, to the nearest 10 years

check_num('5.3', q5_3, 3, 'D_53')
""".replace("'D_53'", repr(D_53)))

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. Reading a model, and fitting one

The first six questions here put numbers into a model somebody else built —
which is what fitting starts with. The last one builds it: two constants, two
conditions, and one decision about what $t=0$ means.
""")

md(r"""
### 6.1 — *May 2023 TZ1 Paper 2 Q3(a), 2 marks*

The total number of children $y$ visiting a park depends on the highest
temperature $T$ in degrees Celsius. A park official predicts it with
$y=-0.6T^2+23T+110$, where $10\le T\le 35$.

Use this model to estimate the number of children in the park on a day when
the highest temperature is $25\,^{\circ}\mathrm{C}$.
""")

code(r"""
q6_1 = ...       # the number of children

verify_exact('6.1', q6_1, 310)
""")

md(r"""
### 6.2 — *November 2025 TZ1 Paper 2 Q10(a), 2 marks*

An airplane lands on a runway $100$ metres in front of a stationary car; at
that instant the car starts to travel in the same direction. For $t\ge 0$
seconds after landing, the velocities in $\mathrm{m\,s^{-1}}$ are
$$v_{\text{air}}=60e^{-0.1t},\qquad v_{\text{car}}=5t .$$

When the airplane lands, write down the speed of **(i)** the airplane;
**(ii)** the car.
""")

code(r"""
q6_2a = ...      # the airplane
q6_2b = ...      # the car

verify_exact('6.2a', q6_2a, 60)
verify_exact('6.2b', q6_2b, 0)
""")

md(r"""
### 6.3 — *May 2023 TZ1 Paper 3 Q2(c), 1 mark*

Let $M_n(S)$ be the maximum product of $n$ positive real numbers whose sum is
$S$. For $n=2$ this product is $M_2(S)=\left(\dfrac{S}{2}\right)^{2}$.

Verify that $M_2(S)=\left(\dfrac{S}{2}\right)^{2}$ is true for $S=12$ — that
is, give the value it produces.
""")

code(r"""
q6_3 = ...       # M_2(12)

verify_exact('6.3', q6_3, 36)
""")

md(r"""
### 6.4–6.6 — *May 2023 TZ1 Paper 3 Q2(e), 1 mark each*

It has been proved that $M_n(S)=\left(\dfrac{S}{n}\right)^{n}$. Hence
determine **(i)** $M_3(12)$; **(ii)** $M_4(12)$; **(iii)** $M_5(12)$.

All three are exact.
""")

code(r"""
q6_4 = ...       # M_3(12)
q6_5 = ...       # M_4(12)
q6_6 = ...       # M_5(12)

verify_exact('6.4', q6_4, 4**3)
verify_exact('6.5', q6_5, 3**4)
verify_exact('6.6', q6_6, Rational(12, 5)**5)
""")

md(r"""
### 6.7 — *November 2022 Paper 2 Q4, 7 marks*

The population of a town $t$ years after 1 January 2014 can be modelled by
$$P(t)=15\,000e^{kt},\qquad k<0,\ t\ge 0 .$$
It is known that between 1 January 2014 and 1 January 2022 the population
decreased by $11\%$.

**(a)** Write down the completed model, with $k$ in place.

**(b)** Use it to estimate the population of this town on 1 January 2041.

The first check puts $t=0$ and $t=8$ back into whatever you wrote and asks
whether $15\,000$ and $13\,350$ come out. It says nothing about 2041.
""")

code(r"""
q6_7a = ...      # the model, an expression in t with no letters left in it
q6_7b = ...      # the population on 1 January 2041

verify_model('6.7a', q6_7a, [(0, 15000), (8, 13350)])
check_num('6.7b', q6_7b, 3, 'D_67')
""".replace("'D_67'", repr(D_67)))

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. Percentages as a power

A percentage change per period is a multiplier per period, and the exponent
counts **periods**, not years. Nominal $4\%$ compounded quarterly is $1\%$
four times. Inflation at $j$ against interest at $i$ leaves
$\frac{1+i}{1+j}$ per period — and the markscheme also accepts the
approximation $1+i-j$.
""")

md(r"""
### 7.1 — *May 2025 TZ1 Paper 1 Q2(a), 1 mark*

Bob invests $1000$ dinar in an account paying a nominal annual interest rate
of $4\%$ compounded **quarterly**. The amount after one complete year can be
written as $1000(1+k)^4$, where $k\in\mathbb{Q}$. Write down the value of $k$.
""")

code(r"""
q7_1 = ...       # k, exactly

verify_exact('7.1', q7_1, Rational(1, 100))
""")

md(r"""
### 7.2 — *May 2025 TZ1 Paper 1 Q2(c), 4 marks*

Hence or otherwise, find the amount of money in the account after one complete
year, giving your answer correct to the nearest dinar.

No calculator: part (b) of that question expanded $(1+x)^4$ for you.
""")

code(r"""
q7_2 = ...       # the amount, to the nearest dinar

check_num('7.2', q7_2, 4, 'D_72')
""".replace("'D_72'", repr(D_72)))

md(r"""
### 7.3 — *May 2025 TZ2 Paper 2 Q4(a), 2 marks*

Alex purchases a car for €$30\,000$. The value of the car depreciates at
$15\%$ per annum. Find the value of the car after ten years, giving your
answer to two decimal places.
""")

code(r"""
q7_3 = ...       # the value after ten years

check_num('7.3', q7_3, 6, 'D_73')
""".replace("'D_73'", repr(D_73)))

md(r"""
### 7.4 — *May 2025 TZ2 Paper 2 Q4(b), 4 marks*

Alex invests €$50\,000$ in a bank account that pays a compound interest rate
of $1.5\%$ per month. Inflation over the same period was $0.8\%$ per month.
Find the number of months required for the **real** value of the investment
to first exceed €$55\,000$.
""")

code(r"""
q7_4 = ...       # the number of months

verify_exact('7.4', q7_4, 14)
""")

md(r"""
### 7.5 — *November 2025 TZ1 Paper 1 Q5(b), 2 marks*

The first four terms of the Maclaurin expansion of $(1-x)^{-4}$ are
$1+4x+10x^2+20x^3$.

A car was purchased four years ago, depreciated in value by $10\%$ each year,
and is worth $\$1000$ today. Using that expansion, estimate the value of the
car four years ago.
""")

code(r"""
q7_5 = ...       # the value four years ago

verify_exact('7.5', q7_5, 1520)
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. The logistic model

$x=\dfrac{L}{1+Ce^{-kt}}$. $L$ is read off the page, $C$ comes from $t=0$
where $e^{0}=1$, and $k$ comes from the second data point by section 5.
""")

md(r"""
### 8.1 — *November 2025 TZ1 Paper 3 Q2(a)(i), 1 mark*

A wolf population had a stable size of $200$. After some years of disruption
it fell to $40$; the area then became protected and the population began to
grow again. Researchers model its size $x$ after $t$ years of protection with
$$x=\frac{L}{1+Ce^{-kt}},\qquad L,C,k\in\mathbb{R}^{+},$$
and decide to let $L=200$.

State the assumption being made in assuming $L=200$.

*A sentence, so this question has no cell. The answer is in the solutions.*
""")

md(r"""
### 8.2 — *November 2025 TZ1 Paper 3 Q2(a)(ii), 2 marks*

At $t=0$ the population of wolves is $40$. Find the value of $C$.
""")

code(r"""
q8_2 = ...       # C

verify_exact('8.2', q8_2, 4)
""")

md(r"""
### 8.3 — *November 2025 TZ1 Paper 3 Q2(a)(iii), 2 marks*

At $t=5$ the population has increased to $70$. Find the value of $k$.

The paper asks for three significant figures; enter the exact form and the
check will accept it.
""")

code(r"""
q8_3 = ...       # k, exactly

verify_exact('8.3', q8_3, log(Rational(28, 13))/5)
""")

md(r"""
### 8.4 — *November 2025 TZ1 Paper 3 Q2(a)(iv), 2 marks*

**(a)** Write down the completed model.

**(b)** Use it to predict the size of the wolf population $10$ years after the
area became protected, correct to the nearest whole number.
""")

code(r"""
q8_4a = ...      # x(t), an expression in t with no letters left in it
q8_4b = ...      # the population at t = 10

verify_model('8.4a', q8_4a, [(0, 40), (5, 70)])
verify_exact('8.4b', q8_4b, 107)
""")

md(r"""
### 8.5 — *November 2025 TZ1 Paper 3 Q2(c), 1 mark*

An alternative model — the Gompertz model, which satisfies
$\frac{dx}{dt}=ax\ln\frac{200}{x}$ — predicts $101$ wolves at $t=10$. After
$10$ years the population is measured and found to be $85$.

Comment on the predictions made by the two models.

*A sentence, so this question has no cell either.*
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. The logarithm as a function

Not a tool now but a function: inside a composition, defining a domain, or
serving as a measuring scale. Solve for $\ln x$ first and remove the logarithm
last — $e^{u}$ is increasing, so it never flips an inequality.
""")

md(r"""
### 9.1 — *May 2024 TZ2 Paper 2 Q3(a), 1 mark*

The loudness $L$ of a sound, in decibels, is related to its intensity $I$
units by $L=10\log_{10}(I\times 10^{12})$. Sound $\mathrm{S}_1$ has intensity
$10^{-6}$ units and loudness $60$ decibels; sound $\mathrm{S}_2$ has twice the
intensity of $\mathrm{S}_1$.

State the intensity of $\mathrm{S}_2$.
""")

code(r"""
q9_1 = ...       # the intensity of S2

verify_exact('9.1', q9_1, 2*Rational(1, 10**6))
""")

md(r"""
### 9.2 — *May 2024 TZ2 Paper 2 Q3(b), 2 marks*

Determine the loudness of $\mathrm{S}_2$.

The markscheme accepts the exact form as a final answer, and so does the
check.
""")

code(r"""
q9_2 = ...       # the loudness of S2

verify_exact('9.2', q9_2, 60 + 10*log(2, 10))
""")

md(r"""
### 9.3 — *May 2024 TZ2 Paper 2 Q3(c), 3 marks*

The maximum loudness of thunder in a thunderstorm was measured to be $115$
decibels. Find the corresponding intensity $I$ of the thunder.
""")

code(r"""
q9_3 = ...       # the intensity of the thunder

verify_exact('9.3', q9_3, 10**Rational(-1, 2))
""")

md(r"""
### 9.4 — *May 2025 TZ1 Paper 1 Q10(d), 3 marks*

The function $f$ is defined by $f(x)=5(x+1)(x+3)$, $x\in\mathbb{R}$; the
function $g$ by $g(x)=\ln x$, $x>0$. An earlier part established that
$f(x)\le 40\iff -5\le x\le 1$.

**(a)** Write down an expression for $(f\circ g)(x)$.

**(b)** Solve $(f\circ g)(x)\le 40$.
""")

code(r"""
q9_4a = ...      # (f o g)(x)
q9_4b = ...      # the solution set

verify_identity('9.4a', q9_4a, 5*(log(x) + 1)*(log(x) + 3))
verify_solution_set('9.4b', q9_4b, 5*(log(x) + 1)*(log(x) + 3) <= 40,
                    domain=Interval.open(0, oo))
""")

md(r"""
### 9.5 — *May 2025 TZ1 Paper 1 Q10(e), 3 marks*

With the same $f$ and $g$, find the domain of $g\circ f$.
""")

code(r"""
q9_5 = ...       # the domain of g o f

verify_solution_set('9.5', q9_5, 5*(x + 1)*(x + 3) > 0)
""")

md(r"""
### 9.6 — *May 2023 TZ1 Paper 3 Q2(i), 2 marks*

The function $g$ is defined by $\ln\bigl(g(x)\bigr)=x\ln\dfrac{S}{x}$, for
$x\in\mathbb{R}^{+}$. Find $g(x)$, and so verify that $g(x)=M_x(S)$ when
$x\in\mathbb{Z}^{+}$.
""")

code(r"""
q9_6 = ...       # g(x), in terms of S and x

verify_identity('9.6', q9_6, exp(x*log(S/x)), var=x)
""")

# --------------------------------------------------------------- Разборы
md(r"""
---
---
# Solutions

Numbered as the questions are. Each names its source and the marks it carries.
""")

md(r"""
## 1. The three log laws

**1.1** — *May 2025 TZ3 P1 Q1(a), 3 marks.* Factorise first, because there is
no law for a sum:
$$24=2^3\times 3\;\Longrightarrow\;
  \log_{10}24=3\log_{10}2+\log_{10}3=3p+q .$$
**(M1)** for using a law, **(A1)** for reaching $3\log_{10}2+\log_{10}3$ with
the arguments actually equal to $2$ and $3$, **A1** for $3p+q$.

**1.2** — *May 2024 TZ1 P1 Q2(a), 2 marks.*
$\log_{10}\frac1a=\log_{10}1-\log_{10}a=-\log_{10}a=-\frac13$. Equally
$\log_{10}a^{-1}=-\log_{10}a$. Note $\log_{10}1=0$, not $1$.

**1.3** — *May 2025 TZ1 P1 Q8(a), 2 marks.* The loose $1$ joins the logarithm:
$$1+\log_2 n=\log_2 2+\log_2 n=\log_2(2n).$$
Then $2n\ge n+1$ for $n\ge 1$, and since **$\log_2$ is increasing**,
$\log_2(2n)\ge\log_2(n+1)$. The second half is the **R1**, and it is for
naming monotonicity out loud — the inequality $2n\ge n+1$ alone does not earn
it. Part (b) of that question then runs induction on this result to prove
$n>\log_2 n$.
""")

md(r"""
## 2. Change of base

**2.1** — *May 2025 TZ3 P1 Q1(b), 2 marks.*
$$\log_3 8=\frac{\log_{10}8}{\log_{10}3}=\frac{3\log_{10}2}{\log_{10}3}
  =\frac{3p}{q}.$$
Argument on top, base underneath. Check the direction once on something known
— $\log_2 8=\frac{\log 8}{\log 2}=3$ — and you will not flip it again.

**2.2** — *May 2024 TZ1 P1 Q2(b), 3 marks.*
$$\log_{1000}a=\frac{\log_{10}a}{\log_{10}1000}=\frac{1/3}{3}=\frac19 .$$
The $3$ underneath is $\log_{10}10^3$. The markscheme prints four routes to
the same place, including $10^{1/3}=1000^{x}=(10^3)^x$ and hence $3x=\frac13$.

**2.3** — *November 2025 TZ3 P1 Q4, 5 marks.* Everything is a power of $2$:
$$3\log_8 10x=3\cdot\frac{\log_2 10x}{3}=\log_2 10x,\qquad
  \log_4 x=\frac{\log_2 x}{2}=\log_2\sqrt{x}.$$
So
$$\log_2\frac{10x}{\sqrt x}=\log_2 2\;\Longrightarrow\;10\sqrt x=2
  \;\Longrightarrow\;\sqrt x=\tfrac15\;\Longrightarrow\;x=\tfrac{1}{25}.$$
The two **M** marks — power/quotient rule and change of base — are
independent and may be awarded in any order, so a wrong order still scores.
The markscheme prints $10\sqrt x=2$ as its own **A1**, which is a warning:
stopping at $\sqrt x=\frac15$ answers a different question.
""")

md(r"""
## 3. An equation with the unknown under a logarithm

**3.1** — *November 2025 TZ1 P1 Q2(b), 4 marks.* The $-1$ is the question.
Either move it across as $1=\log_2 2$, or absorb it as $\log_2\frac12$.
Collapsing both sides,
$$\log_2\frac{x(x^2-1)}{(x^2-8x+7)(x+1)}=\log_2 2 .$$
The fraction inside is exactly what part (a) simplified, so it equals
$\frac{x}{x-7}$, and removing the logarithms gives
$$\frac{x}{x-7}=2\;\Longrightarrow\;x=2x-14\;\Longrightarrow\;x=14 .$$
$14>7$, so every argument is positive and the root stands.

The markscheme's METHOD 2 does it the other way round — use $1=\log_2 2$ on
the left first, get $\log_2\frac{x^3-x}{2}=\log_2\bigl((x^2-8x+7)(x+1)\bigr)$,
and cancel — and lands on $\frac{x}{2}=x-7$. Same answer, same marks.

**Why the domain is not decoration.** Removing logarithms is not reversible:
any root it produced below $7$ would have been manufactured by that step and
not present in the original equation. Here none was, but the habit is what the
check is testing.
""")

md(r"""
## 4. The laws of exponents

**4.1** — *May 2021 TZ2 P1 Q11(c), 2 marks.* $e^{T}=1+v_0$ gives
$e^{-T}=\dfrac{1}{1+v_0}$ — the reciprocal, and this is the line the two marks
rest on. Then split the exponent:
$$v(T-k)=(1+v_0)e^{-(T-k)}-1=(1+v_0)e^{-T}e^{k}-1
        =(1+v_0)\cdot\frac{1}{1+v_0}\cdot e^{k}-1=e^{k}-1 .$$
The markscheme's METHOD 2 is shorter: write $1+v_0$ as $e^{T}$ from the start,
and $e^{T}e^{-(T-k)}=e^{k}$ falls out in one step.

**4.2** — *May 2021 TZ2 P1 Q11(d), 2 marks.* *Deduce* means do not start
again. Replacing $k$ by $-k$ turns "$k$ seconds before" into "$k$ seconds
after": $v(T+k)=e^{-k}-1$. Part (e) then adds the two:
$e^{k}+e^{-k}-2\ge 0$ by AM–GM, so the particle is faster before the turning
point than it is slow after it.

**4.3** — *May 2025 TZ1 P1 Q7(a), 1 mark.* $3=e^{\ln 3}$, so $a=\ln 3$. Not a
trick — the definition of $\ln$ read backwards. The rest of that question uses
it to make sense of $3^{\,i-1}=e^{(i-1)\ln 3}$ and to extract
$\operatorname{Re}(z)=\frac{1}{3}\cos(\ln 3)$.
""")

md(r"""
## 5. Taking logarithms of both sides

**5.1** — *May 2021 TZ2 P2 Q5(a), 1 mark.* $A(0)=A_0e^{0}=A_0$, and the plant
has $100$ units at death, so $A_0=100$. The markscheme wants the line
$100=A_0e^{0}$ written down; the conclusion alone is **A0**.

**5.2** — *May 2021 TZ2 P2 Q5(b), 3 marks.* Half the original amount after
$5730$ years:
$$50=100e^{-5730k}\;\Longrightarrow\;e^{-5730k}=\tfrac12
  \;\Longrightarrow\;e^{5730k}=2\;\Longrightarrow\;5730k=\ln 2
  \;\Longrightarrow\;k=\frac{\ln 2}{5730}.$$
The route through $e^{5730k}=2$ avoids $\ln\frac12=-\ln 2$, which is the most
common sign slip in this topic. The markscheme is unusually generous here —
*"award full marks for at least two correct algebraic steps seen"* — because
several routes exist.

**5.3** — *May 2021 TZ2 P2 Q5(c), 3 marks.* $25\%$ decayed means $75$ units
**remain**:
$$75=100e^{-\frac{\ln 2}{5730}t}
  \;\Longrightarrow\;\ln 0.75=-\frac{\ln 2}{5730}t
  \;\Longrightarrow\;t=\frac{5730\ln\frac43}{\ln 2}=2378.16\ldots$$
To the nearest $10$ years, $t=2380$. This is the one question in the topic
where the markscheme prints both routes and pays the same for either:
**EITHER** solve graphically **OR** manipulate logs. What the graph does not
give you is the exact form — which costs nothing here and costs the whole
mark in part (b).
""")

md(r"""
## 6. Reading a model, and fitting one

**6.1** — *May 2023 TZ1 P2 Q3(a), 2 marks.*
$y=-0.6(25)^2+23(25)+110=-375+575+110=310$ children. Exact, despite being a
calculator paper: the model is a quadratic with terminating coefficients.

**6.2** — *November 2025 TZ1 P2 Q10(a), 2 marks.* At $t=0$:
$v_{\text{air}}=60e^{0}=60\ \mathrm{m\,s^{-1}}$ and
$v_{\text{car}}=5\times 0=0$. One mark each, and the whole content is
$e^{0}=1$. The rest of that question integrates the difference to find when
the car catches the plane.

**6.3** — *May 2023 TZ1 P3 Q2(c), 1 mark.* $M_2(12)=\left(\frac{12}{2}\right)^2
=6^2=36$, which agrees with parts (a) and (b): the two numbers summing to $12$
with the largest product are $6$ and $6$.

**6.4–6.6** — *May 2023 TZ1 P3 Q2(e), 1 mark each.*
$$M_3(12)=4^3=64,\qquad M_4(12)=3^4=81,\qquad
  M_5(12)=\left(\tfrac{12}{5}\right)^5=2.4^5=79.62624 .$$
The sequence is the point: the product rises, peaks between $n=4$ and $n=5$,
and falls. Later parts of that question find the peak exactly — it is at
$x=S/e$, which for $S=12$ is $4.41$, and it is why $n=4$ beats $n=5$.

**6.7** — *November 2022 Paper 2 Q4, 7 marks.* $t=0$ is 1 January 2014, so 1
January 2022 is $t=8$ and 1 January 2041 is $t=27$. A decrease of $11\%$
leaves $89\%$:
$$P(8)=0.89\times 15\,000=13\,350\;\Longrightarrow\;e^{8k}=0.89
  \;\Longrightarrow\;k=\frac{\ln 0.89}{8}=-0.014566\ldots$$
Then $P(27)=15\,000e^{-0.014566\ldots\times 27}=10\,122.3\ldots$, and the
markscheme accepts $10\,100$ (three significant figures) or $10\,122$.

**Where the seven marks are:** recognising $P(0)=15\,000$; computing
$0.89\times 15\,000$; recognising $t=8$; substituting both; finding $k$;
substituting $t=27$; the number. Six of the seven are before the exponential
is ever evaluated, and the two most often lost are the third and the sixth —
the two that are only about what $t$ means. Answering with $t=19$ gives
$11\,400$ and scores five of the seven.
""")

md(r"""
## 7. Percentages as a power

**7.1** — *May 2025 TZ1 P1 Q2(a), 1 mark.* Nominal $4\%$ compounded quarterly
is $\frac{4\%}{4}=1\%$ per quarter, so $k=\frac{4}{400}=\frac{1}{100}$.
Everything downstream depends on this one mark.

**7.2** — *May 2025 TZ1 P1 Q2(c), 4 marks.* No calculator, so expand rather
than evaluate. With $(1+x)^4=1+4x+6x^2+4x^3+x^4$ at $x=\frac{1}{100}$,
$$1000\left(1+\tfrac{1}{100}\right)^4=1000+40+0.6+0.004+\ldots=1040.6\ldots$$
so $1041$ dinar. The first two terms already give $1040$; the third decides
the rounding. The markscheme's METHOD 2 multiplies $1.01$ out by hand
— $(1.0201)(1.030301)$ — and is longer.

**7.3** — *May 2025 TZ2 P2 Q4(a), 2 marks.* Depreciation at $15\%$ is a
multiplier of $0.85$: $30\,000\times 0.85^{10}=5906.2321\ldots\to €5906.23$.
Two decimal places, because it is money and because the question says so.

**7.4** — *May 2025 TZ2 P2 Q4(b), 4 marks.* The exact real multiplier per
month is the quotient
$$\frac{1.015}{1.008}=1.00694\ldots\;\Longrightarrow\;
  n>\frac{\ln 1.1}{\ln 1.00694\ldots}=13.7722\ldots\;\Longrightarrow\;n=14 .$$
The markscheme's own METHOD 1 is the approximation $r=1.5-0.8=0.7\%$, giving
$n>\frac{\ln 1.1}{\ln 1.007}=13.6633\ldots$ and the same answer, for full
marks; with it, $n=13$ gives €$54\,746.09$ and $n=14$ gives €$55\,129.31$.

**The wrong answer the markscheme names.** $164$ months, worth
**(A1)(M1)(A0)(A0)** — the method mark survives, both answer marks are gone.
It comes from reading $0.7\%$ as an *annual* rate and compounding it monthly:
$\frac{\ln 1.1}{\ln(1+0.007/12)}=163.5\ldots$ The period was in the question
all along.

**7.5** — *November 2025 TZ1 P1 Q5(b), 2 marks.* Four years of $10\%$
depreciation multiply by $0.9^4$, so the value four years ago is
$1000\times 0.9^{-4}=1000(1-0.1)^{-4}$. With the given expansion at $x=0.1$,
$$(1-x)^{-4}\approx 1+4(0.1)+10(0.01)+20(0.001)=1.52\;\Longrightarrow\;\$1520 .$$
The exact value is $1000/0.6561=1524.16\ldots$; the series truncated at $x^3$
gives $1520$, which is what the question asks for. Part (a) of that question
is where $a=4$ and $b=10$ come from, by differentiating the Maclaurin series.
""")

md(r"""
## 8. The logistic model

**8.1** — *November 2025 TZ1 P3 Q2(a)(i), 1 mark.* **The assumption is that
the long-term population after the disruption will be the same as it was
before** — that the carrying capacity has not changed. The markscheme condones
*"the maximum value / carrying capacity of the population will be 200"*.

**8.2** — *…(ii), 2 marks.* At $t=0$, $e^{0}=1$:
$$40=\frac{200}{1+C}\;\Longrightarrow\;40+40C=200\;\Longrightarrow\;C=4 .$$
Forgetting $e^{0}=1$ is the only way to lose this.

**8.3** — *…(iii), 2 marks.* At $t=5$:
$$70=\frac{200}{1+4e^{-5k}}\;\Longrightarrow\;1+4e^{-5k}=\frac{20}{7}
  \;\Longrightarrow\;e^{-5k}=\frac{13}{28}
  \;\Longrightarrow\;k=\frac15\ln\frac{28}{13}=0.153451\ldots\to 0.153 .$$
The markscheme prints it as $-\frac15\ln\frac{130}{280}$ — the same number
with the minus still inside.

**8.4** — *…(iv), 2 marks.* $x(t)=\dfrac{200}{1+4e^{-0.153451\ldots t}}$ and
$$x(10)=\frac{200}{1+4e^{-1.53451\ldots}}=107.397\ldots\to 107\ \text{wolves.}$$
Whole animals, so a whole number.

**The ten-second sanity check.** Evaluate at a large $t$: the model must
approach $200$ from below. With the sign of $k$ flipped it collapses towards
zero instead — invisible in the algebra, obvious in the number.

**8.5** — *…(c), 1 mark.* **Both models overestimate, and the Gompertz model
is closer to the true value.** Logistic $107$, Gompertz $101$, measured $85$.
The markscheme accepts either half of that sentence and follows through on
your own two numbers, as long as both are positive and both are compared
with $85$.
""")

md(r"""
## 9. The logarithm as a function

**9.1** — *May 2024 TZ2 P2 Q3(a), 1 mark.* Twice $10^{-6}$ is
$2\times 10^{-6}$, that is $\frac{1}{500\,000}$. A mark for reading.

**9.2** — *…(b), 2 marks.*
$$L=10\log_{10}(2\times 10^{-6}\times 10^{12})=10\log_{10}(2\times 10^{6})
  =10(6+\log_{10}2)=60+10\log_{10}2=63.0102\ldots\to 63.0 .$$
The markscheme accepts $60+10\log_{10}2$ as a final answer. Notice what did
not happen: doubling the intensity did not double the loudness, it added about
$3$ decibels. That is what a logarithmic scale is *for* — it turns
multiplication into addition. The markscheme also names the wrong answer
$L=0$, which comes from using $I=10^{-12}$.

**9.3** — *…(c), 3 marks.*
$$115=10\log_{10}(I\times 10^{12})\;\Longrightarrow\;I\times 10^{12}=10^{11.5}
  \;\Longrightarrow\;I=10^{-0.5}=\frac{1}{\sqrt{10}}=0.316227\ldots$$
Exact forms $10^{-0.5}$ and $\frac{1}{\sqrt{10}}$ are both accepted.

**9.4** — *May 2025 TZ1 P1 Q10(d), 3 marks.*
$(f\circ g)(x)=f(\ln x)=5(\ln x+1)(\ln x+3)$; the markscheme also accepts
$5(\ln x+2)^2-5$ and $5(\ln x)^2+20\ln x+15$. Then, using the earlier result
$f(x)\le 40\iff -5\le x\le 1$ with $x$ replaced by $\ln x$,
$$-5\le\ln x\le 1\;\Longrightarrow\;e^{-5}\le x\le e ,$$
because $e^{u}$ is increasing and so preserves both inequalities. The
**(M1)** is precisely for *"attempt to replace $x$ with $\ln x$ using their
solution to part (c)"* — that is, for **not** solving the quadratic again.
Applying $e$ to $-5$ and writing $-e^{5}$ is the standard error.

**9.5** — *…(e), 3 marks.* $(g\circ f)(x)=\ln\bigl(f(x)\bigr)$ needs
$f(x)>0$:
$$(x+1)(x+3)>0\;\Longrightarrow\;x<-3\ \text{ or }\ x>-1 ,$$
that is $(-\infty,-3)\cup(-1,\infty)$. Two separate marks: one for the
critical values, one for the inequalities pointing the right way. Writing
$-3<x<-1$ — the inside of the parabola, where $f$ is negative — collects the
first and loses the second. Note that the domain of the composition is
*narrower* than the domain of $f$, which is all of $\mathbb{R}$.

**9.6** — *May 2023 TZ1 P3 Q2(i), 2 marks.* Use the power law on the right and
then exponentiate:
$$\ln\bigl(g(x)\bigr)=x\ln\frac{S}{x}=\ln\left(\frac{S}{x}\right)^{x}
  \;\Longrightarrow\;g(x)=\left(\frac{S}{x}\right)^{x},$$
which is $M_x(S)$ whenever $x$ is a positive integer. **M1** for moving the
$x$ up as a power, **A1** for $g$ itself.

**Why anyone would bother.** $M_n(S)$ is defined only for whole $n$ — you
cannot have $4.41$ factors. Writing it as $g$, a function of a real variable
that agrees with $M_n$ at the integers, is what makes it differentiable, and
differentiating is how the question then finds the best $n$. It is the same
move that turns compound interest into $e^{rt}$.
""")

md(r"""
---
## What to do when it goes wrong

**Your model gives the wrong number at a data point.** The constants are not
the problem — the time is. Write down what $t=0$ means and recount.

**Your answer is off by a factor you cannot find.** Check whether a percentage
went in as $0.11$ where $0.89$ was meant, or as $1.04$ where $1.01$ was meant,
or whether the exponent counted years where it should have counted months.

**Your logarithmic equation has a root the check rejects.** Removing
logarithms is not reversible. Put the root back into the *original* equation
and look at every argument.

**Your inequality came out backwards.** You applied $e^{u}$ or $\ln$ to one
side only, or to a negative number. Both are increasing: they never flip an
inequality, and they never accept a negative argument.

**Your exact answer became a decimal.** On Paper 1 that is the whole mark.
Keep $\ln 2$, keep $\frac19$, keep $3p+q$, keep $10^{-1/2}$. The calculator
comes out only when the paper number says it may.

**Nothing is wrong and you are still slow.** Sections 1–3 should take seconds,
not minutes. If they do not, the three laws are not yet automatic, and no
amount of model-fitting practice will fix that.
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
