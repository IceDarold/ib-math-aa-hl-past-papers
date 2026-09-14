"""Собирает архивный ноутбук A2: вся тема геометрических прогрессий подряд.

Четырнадцатый ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5 и E6. Практикум учит: лестница из приёмов, теория перед каждым, три
уровня сложности, тренажёр распознавания, задание на время. Он берёт
из корпуса не всё, а то, на чём приём виден лучше всего.

Этот не учит. Он даёт набивать руку: **вся тема подряд, по тем же семи
приёмам, без единой строчки теории**. Двадцать семь вопросов, 77 баллов —
ровно то, что архив спрашивает про геометрические прогрессии с ноября
2021 по ноябрь 2025.

Разметка взята из карточки number-algebra-geometric-sequences.yaml: поле
blocks у каждого приёма. Никакой отдельной разметки формат не заводит.

Два места, где тема заставила формат подвинуться.

**Вопрос, разрезанный между практикумами.** Майский 2023 TZ1 вопрос 10
и майский 2025 TZ3 вопрос 10 начинаются арифметической
последовательностью и кончаются геометрической. Здесь они начинаются
с середины, и в самом ноутбуке об этом сказано прямым текстом:
предыдущие пункты разобраны в A1.

**Два вопроса проверить нельзя.** «State a reason why the sum does not
exist» и «show that k² − 10k − 24 = 0» — у них нет ячейки, а в разборе
выписано то, что принимает схема оценивания.

Хешей в этом ноутбуке нет ни одного: всякий ответ темы — член, сумма,
знаменатель или номер, и всякий получается ходом по прогрессии.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_a2.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(
    ROOT, 'practicum/number_algebra/archive-a2-geometric-sequences.ipynb')

ANSWERS = {
    # § 1. The ratio and a term
    'q1_1r': '0.21',
    'q1_1': '16.8',
    'q1_2t': '[7, -21, 63]',
    'q1_2r': '-3',
    'q1_3': 'Rational(65, 2)',
    'q1_4': '29750',
    'q1_5': '10423',
    # § 2. Add the first n
    'q2_1': '(10**n - 1)/9',
    'q2_2': '10*(10**n - 1)/9',
    'q2_3p': 'Rational(8, 5)',
    'q2_3a': '10',
    # § 3. The infinite sum
    'q3_1': 'Rational(14, 3)',
    'q3_3r': '0.812',
    'q3_3d': '19.2',
    'q3_4p': '[-sqrt(3)/3, sqrt(3)/3]',
    'q3_4x': 'exp(2)',
    # § 4. A series written as a sigma
    'q4_1': 'Rational(7, 12)',
    'q4_2': 'Rational(53, 990)',
    'q4_3': 'Rational(251, 990)',
    # § 5. Three quantities in a geometric sequence
    'q5_1': 's**2/a',
    'q5_2': '[-sqrt(3), sqrt(3)]',
    'q5_3n': '-sqrt(3)',
    'q5_3': '-15*sqrt(3)',
    'q5_5k': '-2',
    'q5_5t': '[-7, 7, -7]',
    'q5_5r': '-1',
    'q5_6': '0',
    # § 6. The smallest n
    'q6_1r': '1.2',
    'q6_1': '27',
    'q6_2': '64',
    'q6_3': '20',
    # § 7. The ratio is an expression
    'q7_1n': 'n + 1',
    'q7_1': '(x**(n + 1) - 1)/(x - 1)',
    'q7_2': '1/(1 + x**2)',
    'q7_3': '1 - 2*x**2 + 4*x**4 - 8*x**6 + 16*x**8',
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
# A2 archive — geometric sequences and infinite sums, all of it

**Twenty-seven questions, 77 marks.** Every question the archive asks
about geometric sequences, from November 2021 to November 2025, in the
order of the seven techniques rather than the order of the papers.

No theory. No worked examples. Open it, answer twenty-seven questions,
close it. The theory is in the practicum,
`practicum-a2-geometric-sequences.ipynb`.

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The ratio and a term | 5 | 13 |
| 2 | Add the first $n$ | 3 | 10 |
| 3 | The infinite sum | 4 | 15 |
| 4 | A series written as a $\Sigma$ | 3 | 7 |
| 5 | Three quantities in a geometric sequence | 6 | 14 |
| 6 | The smallest $n$ | 3 | 12 |
| 7 | The ratio is an expression | 3 | 6 |

Answers go on one line each. The checks are the same ones the practicum
uses and they store nothing: a sequence is handed over as a rule — a
first term and a ratio — and the check multiplies its way along it.
The infinite sum is reached by adding until the tail stops mattering,
which is why a series that does not shrink cannot be summed at all.

**Two questions have no cell.** *State a reason why the sum does not
exist* and *show that $k^2-10k-24=0$* cannot be checked by anything;
what the markscheme accepts for them is written out in the solutions at
the end.

**Two questions start in the middle.** May 2023 TZ1 Q10 and May 2025 TZ3
Q10 begin arithmetic and finish geometric. Their earlier parts are in
the A1 archive, and it is said again where it happens.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + geometric, term, total, infinite, ...

language('en')                 # this notebook is in English, and so are the checks

n = symbols('n')               # the index: every one of these papers calls it n
m = symbols('m')               # a second index, in § 5
p = symbols('p')               # the ratio when the paper calls it p
r = symbols('r')               # the ratio when it is the unknown
a, s, t = symbols('a s t')     # letters that stay letters
x = symbols('x')               # the ratio is allowed to be an expression in x
                               # k already comes from kit


# Every sequence below may be built from an answer you have not written
# yet. geometric() returns an empty rule in that case, so the notebook
# runs top to bottom while it is still blank.

def ratios(rule):
    # the geometric sequence whose nth term is rule(n)
    try:
        first, second = rule(1), rule(2)
    except TypeError:
        return geometric(..., ...)
    if blank(first, second) or first == 0:
        return geometric(..., ...)
    return geometric(first, second / first)


print('ready; sympy', sp.__version__)
print('a geometric sequence:', geometric(3, 2), '→ term 5 is',
      term(geometric(3, 2), 5))
""")

# ============================================================ § 1
md(r"""
---
# § 1. The ratio and a term

**Five questions, 13 marks.** $u_n=u_1r^{\,n-1}$, read forwards and
backwards, with percentages counting as ratios.
""")

md(r"""
### 1.1 — *May 2025 TZ2 Paper 2 Q7(a), 3 marks*

A geometric sequence has first term $80$ and fourth term $0.74088$.
Find the second term.
""")

code(r"""
q1_1r = ...      # the common ratio
q1_1 = ...       # the second term

mine = geometric(80, q1_1r)

verify_term('1.1 (r)', 0.74088, mine, 4)
verify_term('1.1', q1_1, mine, 2)
""")

md(r"""
### 1.2 — *May 2025 TZ3 Paper 1 Q10(b)(i), 3 marks*

The sequence $\{u_n\}$ has first three terms $u_1=k-5$, $u_2=3-2k$ and
$u_3=5k+3$, where $k\in\mathbb R$. *(Part (a), where the sequence is
arithmetic, is in the A1 archive.)*

Consider the case where $k=12$. Show that the first three terms of
$\{u_n\}$ form a geometric sequence.
""")

code(r"""
q1_2t = [...]    # the first three terms when k = 12
q1_2r = ...      # the common ratio

printed = [k - 5, 3 - 2 * k, 5 * k + 3]

verify_start('1.2', q1_2t, ratios(lambda i: printed[i - 1].subs(k, 12)))
verify_geometric('1.2 geometric', q1_2t)
verify_ratio('1.2 (r)', q1_2r, q1_2t)
""")

md(r"""
### 1.3 — *May 2025 TZ1 Paper 1 Q5(b), 3 marks*

Ten rectangular picture frames have areas $20\left(\tfrac94\right)^{n-1}$
cm² for $n=1,\dots,10$. Find the median area of the ten frames, giving
your answer in the form $q\left(\tfrac94\right)^{4}$ cm², where
$q\in\mathbb Q^+$.
""")

code(r"""
q1_3 = ...       # q

areas = geometric(20, Rational(9, 4))
from_median = (... if blank(q1_3)
               else total(areas, 4) + 2 * q1_3 * Rational(9, 4) ** 4)

verify_total('1.3', from_median, areas, 6)
""")

md(r"""
### 1.4 — *May 2024 TZ1 Paper 2 Q1(a), 2 marks*

Darren buys a car for $\$35\,000$. The value of the car decreases by
$15\%$ in the first year. Find the value of the car at the end of the
first year.

### 1.5 — *May 2024 TZ1 Paper 2 Q1(b), 2 marks*

After the first year, the value of the car decreases by $11\%$ in each
subsequent year. Find the value of Darren's car $10$ years after he
buys it, giving your answer to the nearest dollar.
""")

code(r"""
q1_4 = ...       # the value after one year
q1_5 = ...       # the value after ten years, to the nearest dollar

car = geometric(q1_4, 0.89)

verify_term('1.4', 35000 * 0.85, car, 1)
verify_term('1.5', q1_5, car, 10)
""")

# ============================================================ § 2
md(r"""
---
# § 2. Add the first $n$

**Three questions, 10 marks.** $S_n=\dfrac{u_1(r^{\,n}-1)}{r-1}$, and
counting the terms before using it.
""")

md(r"""
### 2.1 — *May 2024 TZ1 Paper 1 Q5(a), 1 mark*

Consider a geometric sequence with first term $1$ and common ratio $10$.
$S_n$ is the sum of the first $n$ terms. Find an expression for $S_n$ in
the form $\dfrac{a^{\,n}-1}{b}$, where $a,b\in\mathbb Z^+$.

### 2.2 — *May 2024 TZ1 Paper 1 Q5(b), 4 marks*

Hence show that
$S_1+S_2+\dots+S_n=\dfrac{10\left(10^{\,n}-1\right)-9n}{81}$.

*Nothing to hand over at the end of a "show that" — so write down the
geometric half of the working instead: the value of
$10+100+\dots+10^{\,n}$, in terms of $n$.*
""")

code(r"""
q2_1 = ...       # S_n, in terms of n
q2_2 = ...       # 10 + 100 + ... + 10**n, in terms of n

verify_total('2.1', q2_1, geometric(1, 10), n)
verify_total('2.2', q2_2, geometric(10, 10), n)
""")

md(r"""
### 2.3 — *May 2025 TZ1 Paper 1 Q5(a), 5 marks*

Frame $F_1$ has width $4$ cm and height $5$ cm; the width and height of
$F_n$ are each increased by $50\%$ to give those of $F_{n+1}$, for
$1\le n\le9$.

**(i)** Show that the area of frame $F_n$ is
$20\left(\tfrac94\right)^{\,n-1}$ cm².
**(ii)** Hence find the mean area of the ten frames, in the form
$p\left(\left(\tfrac94\right)^{a}-1\right)$ cm², where
$p\in\mathbb Q^+$, $a\in\mathbb Z^+$.
""")

code(r"""
q2_3p = ...      # p
q2_3a = ...      # a

areas = geometric(20, Rational(9, 4))
from_mean = (... if blank(q2_3p, q2_3a)
             else 10 * q2_3p * (Rational(9, 4) ** q2_3a - 1))

verify_total('2.3', from_mean, areas, 10)
""")

# ============================================================ § 3
md(r"""
---
# § 3. The infinite sum

**Four questions, 15 marks.** $S_\infty=\dfrac{u_1}{1-r}$, and the
condition $|r|<1$ that makes it exist.
""")

md(r"""
### 3.1 — *November 2021 Paper 2 Q5(b), 3 marks*

The sum of the first $n$ terms of a geometric sequence is
$S_n=\displaystyle\sum_{i=1}^{n}\frac23\left(\frac78\right)^{i}$.
Find $S_\infty$.
""")

code(r"""
q3_1 = ...       # the sum to infinity

verify_infinite('3.1', q3_1, geometric(Rational(2, 3) * Rational(7, 8),
                                       Rational(7, 8)), exact=True)
""")

md(r"""
### 3.2 — *May 2025 TZ3 Paper 1 Q10(b)(ii), 1 mark* — no cell

The first three terms of $\{u_n\}$ with $k=12$ are $7$, $-21$, $63$ and
the sequence is geometric. State a reason why the sum of an infinite
number of terms of this sequence does not exist.

*One sentence, and no cell can check a sentence. The markscheme's
wording is in the solutions.*

### 3.3 — *November 2025 TZ3 Paper 2 Q10(e), 5 marks*

A particle $P$ moves so that its displacement from O at time $t$ is
$s(t)=2^{\left(1-\frac t5\right)}\sin\!\left(\frac{2\pi t}3\right)$,
$t\ge0$; it passes through O every $T$ seconds. The sequence
$u_1,u_2,u_3\dots$ of largest **distances** from O in the successive
intervals $0<t<T$, $T<t<2T$, $2T<t<3T\dots$ is geometric, and earlier
parts give $u_1=1.80645$, $u_2=1.46729$, $u_3=1.19181$.

**(i)** Determine the value of the common ratio $r$.
**(ii)** Calculate the total distance travelled by $P$ if it were to
continue to move in this way indefinitely.
""")

code(r"""
q3_3r = ...      # the common ratio, to three significant figures
q3_3d = ...      # the total distance

out_and_back = geometric(2 * 1.80645, 1.46729 / 1.80645)   # out and back each time

verify_ratio('3.3(i)', q3_3r, [1.80645, 1.46729, 1.19181])
verify_infinite('3.3(ii)', q3_3d, out_and_back)
""")

md(r"""
### 3.4 — *May 2022 TZ1 Paper 1 Q10(a), 6 marks*

Consider the series $\ln x+p\ln x+\tfrac13\ln x+\dots$, where
$x\in\mathbb R$, $x>1$ and $p\in\mathbb R$, $p\ne0$. Consider the case
where the series is geometric.

**(i)** Show that $p=\pm\tfrac1{\sqrt3}$.
**(ii)** Hence or otherwise, show that the series is convergent.
**(iii)** Given that $p>0$ and $S_\infty=3+\sqrt3$, find the value of
$x$.

*Divide every term by $\ln x$ and the series becomes $1,p,\tfrac13$ —
which is what the check is handed. For (iii) the answer goes inside the
sequence, and the $3+\sqrt3$ comes from the question.*
""")

code(r"""
q3_4p = [...]    # both values of p
q3_4x = ...      # the value of x

# 1, p, 1/3 is the series with ln x divided out
verify_root_set('3.4(i)', q3_4p, Eq(term(geometric(1, p), 3), Rational(1, 3)),
                var=p)
verify_infinite('3.4(iii)', 3 + sqrt(3),
                geometric(... if blank(q3_4x) else ln(q3_4x), 1 / sqrt(3)))
""")

# ============================================================ § 4
md(r"""
---
# § 4. A series written as a $\Sigma$

**Three questions, 7 marks.** The first term is the summand at the lower
limit, and the constant in front of the bracket is not it.
""")

md(r"""
### 4.1 — *November 2021 Paper 2 Q5(a), 2 marks*

The sum of the first $n$ terms of a geometric sequence is
$S_n=\displaystyle\sum_{i=1}^{n}\frac23\left(\frac78\right)^{i}$.
Find the first term of the sequence, $u_1$.
""")

code(r"""
q4_1 = ...       # the first term

mine = geometric(q4_1, Rational(7, 8))

verify_term('4.1', Rational(2, 3) * Rational(7, 8) ** 2, mine, 2)
""")

md(r"""
### 4.2 — *November 2025 TZ1 Paper 2 Q6(a), 3 marks*

Consider the infinite series
$\displaystyle\sum_{k=0}^{\infty}\left(\frac{53}{1000}\right)
\left(\frac1{100}\right)^{k}$. Find the exact value of $S_\infty$.

### 4.3 — *November 2025 TZ1 Paper 2 Q6(b), 2 marks*

Let $0.2\overline{53}$ represent the repeating decimal
$0.2535353\ldots$ Use your answer from part (a) to express
$0.2\overline{53}$ as a fraction whose numerator and denominator have no
common factors.
""")

code(r"""
q4_2 = ...       # the exact sum to infinity
q4_3 = ...       # the repeating decimal as a fraction

series = geometric(Rational(53, 1000), Rational(1, 100))

verify_infinite('4.2', q4_2, series, exact=True)
verify_infinite('4.3', ... if blank(q4_3) else q4_3 - Rational(1, 5),
                series, exact=True)
""")

# ============================================================ § 5
md(r"""
---
# § 5. Three quantities in a geometric sequence

**Six questions, 14 marks.** $s^2=at$, and the quadratic it turns into
when a letter sits inside the terms.
""")

md(r"""
### 5.1 — *May 2024 TZ2 Paper 1 Q10(b), 2 marks*

Consider the geometric sequence $a,\ s,\ t\dots$, where $a,s,t\ne0$.
Show that $s^2=at$.

*Nothing to hand over — so write the third term in terms of the first
two.*
""")

code(r"""
q5_1 = ...       # t, in terms of a and s

verify_geometric('5.1', [a, s, q5_1])
""")

md(r"""
### 5.2 — *May 2023 TZ1 Paper 1 Q10(d), 3 marks*

An arithmetic sequence $u_n$ has $u_1=5$ and $u_6=15$. *(Parts (a)–(c),
which establish that, are in the A1 archive.)* Consider a geometric
sequence $v_n$, where $v_2=u_1$ and $v_4=u_6$. Find the possible values
of the common ratio, $r$.

### 5.3 — *May 2023 TZ1 Paper 1 Q10(e), 2 marks*

Given that $v_{99}<0$, find $v_5$.
""")

code(r"""
q5_2 = [...]     # both possible values of r
q5_3n = ...      # the one that makes v99 negative
q5_3 = ...       # v5

# the sequence starts at v2, so its 3rd term is v4
verify_root_set('5.2', q5_2, Eq(term(geometric(5, r), 3), 15), var=r)
verify_term('5.3', q5_3, geometric(5, q5_3n), 4)
""")

md(r"""
### 5.4 — *May 2025 TZ3 Paper 1 Q10(c)(i), 2 marks* — no cell

The sequence $\{u_n\}$ has $u_1=k-5$, $u_2=3-2k$, $u_3=5k+3$, and is
geometric for a second value of $k$ besides $12$. Show that
$k^2-10k-24=0$.

*A "show that" whose whole content is the algebra between the two
printed lines. The expansion is in the solutions.*

### 5.5 — *May 2025 TZ3 Paper 1 Q10(c)(ii), 4 marks*

Find the first three terms of $\{u_n\}$ for this second value of $k$.

### 5.6 — *May 2025 TZ3 Paper 1 Q10(c)(iii), 1 mark*

Hence write down the value of $S_{2m}$, the sum of the first $2m$ terms,
for this second value of $k$.
""")

code(r"""
q5_5k = ...      # the second value of k
q5_5t = [...]    # the first three terms
q5_5r = ...      # the common ratio they have
q5_6 = ...       # S_2m

printed = [k - 5, 3 - 2 * k, 5 * k + 3]

verify_root_set('5.5 (k)', [12, q5_5k], Eq(k ** 2 - 10 * k - 24, 0), var=k)
verify_start('5.5', q5_5t,
             ratios(lambda i: printed[i - 1].subs(k, q5_5k)
                    if not blank(q5_5k) else ...))
verify_ratio('5.5 (r)', q5_5r, q5_5t)
verify_total('5.6', q5_6, geometric(q5_5t[0], q5_5r), 2 * m)
""")

# ============================================================ § 6
md(r"""
---
# § 6. The smallest $n$

**Three questions, 12 marks.** A table of values, a sketch or logarithms
— the markscheme lists all three as equals — and then rounding the right
way.
""")

md(r"""
### 6.1 — *November 2022 Paper 2 Q3, 5 marks*

A geometric sequence has a first term of $50$ and a fourth term of
$86.4$. The sum of the first $n$ terms is $S_n$. Find the smallest value
of $n$ such that $S_n>33\,500$.
""")

code(r"""
q6_1r = ...      # the common ratio
q6_1 = ...       # the smallest n

mine = geometric(50, q6_1r)

verify_term('6.1 (r)', 86.4, mine, 4)
verify_least('6.1', q6_1, mine, lambda partial: partial > 33500)
""")

md(r"""
### 6.2 — *November 2021 Paper 2 Q5(c), 4 marks*

For the series $S_n=\displaystyle\sum_{i=1}^{n}\frac23
\left(\frac78\right)^{i}$, find the least value of $n$ such that
$S_\infty-S_n<0.001$.

*Your own $S_\infty$ from 3.1 is what the condition is built out of, so
a wrong answer there costs you that answer only.*
""")

code(r"""
q6_2 = ...       # the least n

mine = geometric(Rational(2, 3) * Rational(7, 8), Rational(7, 8))

verify_least('6.2', q6_2, mine,
             lambda partial: q3_1 - partial < Rational(1, 1000))
""")

md(r"""
### 6.3 — *May 2024 TZ1 Paper 2 Q1(c), 3 marks*

Darren's car is worth $\$29\,750$ after one year and loses $11\%$ of its
value each year after that. When he has owned it for $n$ complete years
its value is less than $10\%$ of the original $\$35\,000$. Find the
least value of $n$.
""")

code(r"""
q6_3 = ...       # the least number of complete years

car = geometric(29750, 0.89)

verify_least('6.3', q6_3, car, lambda value: value < 3500, what='term')
""")

# ============================================================ § 7
md(r"""
---
# § 7. The ratio is an expression

**Three questions, 6 marks.** The same three formulas with $r$ that is
not a number, and the convergence condition written as a set of $x$.
""")

md(r"""
### 7.1 — *November 2022 Paper 3 Q1(e), 2 marks*

By considering $f(x)=1+x+x^2+\dots+x^{\,n}$ as a geometric series, for
$x\ne1$, show that $f(x)=\dfrac{x^{\,n+1}-1}{x-1}$.

*One of the two marks is **R1 for a clear indication of how many terms
there are**, so write that down as well.*
""")

code(r"""
q7_1n = ...      # how many terms, in terms of n
q7_1 = ...       # the sum of that many terms

verify_total('7.1', q7_1, geometric(1, x), q7_1n,
             var=x, values=(2, 3, Rational(1, 2)))
""")

md(r"""
### 7.2 — *November 2025 TZ3 Paper 3 Q2(a), 2 marks*

Given $|x|<1$, find the sum to infinity of the geometric series
$1-x^2+x^4-x^6+\dots$

### 7.3 — *May 2025 TZ1 Paper 2 Q12(b), 2 marks*

Consider $f_n(x)=\displaystyle\sum_{r=0}^{n}\left(-2x^2\right)^{r}$.
Given that $f_3(x)=1-2x^2+4x^4-8x^6$, write down a similar expression
for $f_4(x)$ in ascending powers of $x$.
""")

code(r"""
q7_2 = ...       # the sum to infinity of 1 - x^2 + x^4 - ...
q7_3 = ...       # f4(x)

verify_infinite('7.2', q7_2, geometric(1, -x ** 2),
                var=x, values=(Rational(1, 2), Rational(1, 3)))
verify_total('7.3', q7_3, geometric(1, -2 * x ** 2), 5,
             var=x, values=(2, Rational(1, 3)))
""")

# ============================================================ решения
md(r"""
---
---

# 🔑 Solutions

---

**1.1** $80r^3=0.74088$, so $r^3=0.0092610$ and $\boxed{r=0.21}$ —
exact, since $0.21^3=0.009261$. Then $u_2=80(0.21)=\boxed{16.8}$.

**1.2** With $k=12$ the terms are $7$, $-21$, $63$, and

$$\frac{-21}{7}=-3=\frac{63}{-21}$$

Equal ratios, so geometric, with $\boxed{r=-3}$. Showing only one of the
two divisions is not showing it.

**1.3** The median of ten values is the mean of the 5th and 6th:

$$\frac{20\left(\tfrac94\right)^4+20\left(\tfrac94\right)^5}{2}
=\frac{20\left(\tfrac94\right)^4\left(1+\tfrac94\right)}2
=\boxed{\tfrac{65}2\left(\tfrac94\right)^4}$$

**1.4** $0.85\times35\,000=\boxed{\$29\,750}$.

**1.5** $29\,750$ is the value after **one** year, so ten years is nine
more steps: $29\,750\times0.89^{\,9}=\boxed{\$10\,423}$. Using
$0.89^{10}$ gives $\$9276$ and counts the first year twice.

---

**2.1** $S_n=\dfrac{1\left(10^{\,n}-1\right)}{10-1}
=\boxed{\dfrac{10^{\,n}-1}9}$.

**2.2** $\displaystyle\sum_{i=1}^{n}S_i
=\frac19\left(\sum 10^{\,i}-\sum1\right)$, and the first of those is
geometric with $u_1=10$, $r=10$:

$$\sum_{i=1}^{n}10^{\,i}=\boxed{\frac{10\left(10^{\,n}-1\right)}9}$$

so the whole thing is
$\frac19\left(\frac{10(10^n-1)}9-n\right)
=\frac{10(10^n-1)-9n}{81}$. The $81$ is two nines, one from each sum.

**2.3 (i)** Both sides have ratio $\tfrac32$, so the area has ratio
$\left(\tfrac32\right)^2=\tfrac94$, and
$4\cdot5=20$ is the first area.

**(ii)** $S_{10}=\dfrac{20\left(\left(\tfrac94\right)^{10}-1\right)}
{\tfrac94-1}=16\left(\left(\tfrac94\right)^{10}-1\right)$, and the mean
is a tenth of it: $\boxed{p=\tfrac85,\ a=10}$.

---

**3.1** $u_1=\tfrac23\cdot\tfrac78=\tfrac7{12}$ and $r=\tfrac78$, so

$$S_\infty=\frac{7/12}{1-7/8}=\boxed{\frac{14}3}$$

**3.2** $|r|=3\ge1$: the terms do not decrease in size, so the series
diverges. *"$r<1$"* is not a reason — $-3$ **is** less than $1$. The
markscheme wants $|r|\ge1$, and accepts $|r|>1$ or $r<-1$.

**3.3 (i)** $r=\dfrac{1.46729}{1.80645}=0.812252\ldots=\boxed{0.812}$,
and $\dfrac{1.19181}{1.46729}$ gives the same.

**(ii)** Each interval is travelled out and back, so the distance in it
is $2u_i$:

$$2\times\frac{1.80645}{1-0.812252}=2(9.62167)=\boxed{19.2\text{ cm}}$$

**3.4 (i)** Dividing through by $\ln x$ (legal because $x>1$, so
$\ln x\ne0$) leaves $1,\ p,\ \tfrac13$:

$$p^2=\tfrac13\Longrightarrow\boxed{p=\pm\tfrac1{\sqrt3}}$$

**(ii)** $|p|=\tfrac1{\sqrt3}<1$, so the series converges. Both signs
have to be mentioned; considering only one is **R0**.

**(iii)** With $p=\tfrac1{\sqrt3}$,

$$\frac{\ln x}{1-\tfrac1{\sqrt3}}=3+\sqrt3
\Longrightarrow \ln x=\left(3+\sqrt3\right)\left(1-\tfrac1{\sqrt3}\right)
=3+\sqrt3-\sqrt3-1=2$$

$$\boxed{x=\mathrm e^2}$$

---

**4.1** The summand at $i=1$, not the constant in front:

$$u_1=\frac23\cdot\frac78=\boxed{\frac7{12}}$$

**4.2** This $\Sigma$ starts at $k=0$, so here the constant **is** the
first term:

$$S_\infty=\frac{53/1000}{1-1/100}=\boxed{\frac{53}{990}}$$

**4.3** $0.2535353\ldots=0.2+0.0535353\ldots$:

$$\frac15+\frac{53}{990}=\frac{198+53}{990}=\boxed{\frac{251}{990}}$$

$251$ is prime, so nothing cancels.

---

**5.1** $\dfrac sa=\dfrac ts$ gives $s^2=at$, that is
$\boxed{t=\dfrac{s^2}a}$.

**5.2** $v_2$ and $v_4$ are two steps apart:

$$5r^2=15\Longrightarrow r^2=3\Longrightarrow\boxed{r=\pm\sqrt3}$$

$\sqrt3$ alone, with no working, scores **M1A1A0**.

**5.3** $v_{99}=v_2r^{97}$ and $97$ is odd, so $v_{99}<0$ forces
$r=-\sqrt3$:

$$v_5=5\left(-\sqrt3\right)^3=\boxed{-15\sqrt3}$$

**5.4** Equal ratios:

$$\frac{3-2k}{k-5}=\frac{5k+3}{3-2k}\Longrightarrow(3-2k)^2=(k-5)(5k+3)$$

$$9-12k+4k^2=5k^2-22k-15\Longrightarrow k^2-10k-24=0$$

**5.5** $(k-12)(k+2)=0$, and $k=12$ was 1.2, so $\boxed{k=-2}$ and the
terms are

$$-7,\qquad 7,\qquad -7$$

with $r=-1$. Substituting into the wrong expression is the standard
slip: $u_3$ is $5k+3$.

**5.6** With $r=-1$ the terms cancel in pairs, and $2m$ terms make $m$
pairs, so $\boxed{S_{2m}=0}$. No formula needed.

---

**6.1** $50r^3=86.4$ gives $r=1.2$, and

$$250\left(1.2^{\,n}-1\right)>33\,500\Longrightarrow1.2^{\,n}>135
\Longrightarrow n>26.9045\ldots\Longrightarrow\boxed{n=27}$$

$S_{26}=28\,368.8$ and $S_{27}=34\,092.6$ — check both.

**6.2** The critical value is $63.2675\ldots$, so $\boxed{n=64}$;
$S_\infty-S_{63}=0.001036$ is still too big and
$S_\infty-S_{64}=0.000906$ is small enough. Solving
$S_\infty-u_n<0.001$ instead scores **M0**.

**6.3** $10\%$ of $\$35\,000$ is $\$3500$:

$$29\,750\times0.89^{\,n-1}<3500\Longrightarrow n>19.364\ldots
\Longrightarrow\boxed{n=20}$$

At $19$ years the car is worth $\$3651.80$, at $20$ it is $\$3250.10$.

---

**7.1** The powers run $x^0$ to $x^{\,n}$, so there are $\boxed{n+1}$
terms, and

$$f(x)=\frac{1\left(x^{\,n+1}-1\right)}{x-1}
=\boxed{\frac{x^{\,n+1}-1}{x-1}}$$

The **R1** is for the count; using $n$ terms gives
$\tfrac{x^{\,n}-1}{x-1}$, which is the mistake the mark exists to catch.

**7.2** $u_1=1$, $r=-x^2$, and $|x|<1$ makes $|r|<1$:

$$S_\infty=\frac1{1-(-x^2)}=\boxed{\frac1{1+x^2}}$$

Reading the ratio as $x^2$ gives $\tfrac1{1-x^2}$ — a different series.

**7.3** One more term than $f_3$, and $\left(-2x^2\right)^4=16x^8$:

$$f_4(x)=\boxed{1-2x^2+4x^4-8x^6+16x^8}$$

Five terms, because $r$ runs from $0$ to $4$.
""")


def build():
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.12"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    os.makedirs(os.path.dirname(NOTEBOOK), exist_ok=True)
    with open(NOTEBOOK, 'w') as fh:
        json.dump(nb, fh, ensure_ascii=False, indent=1)
    n_code = sum(1 for c in cells if c['cell_type'] == 'code')
    print(f"{NOTEBOOK}: {len(cells)} ячеек, из них {n_code} с кодом, "
          f"эталонов {len(ANSWERS)}")


if __name__ == '__main__':
    build()
