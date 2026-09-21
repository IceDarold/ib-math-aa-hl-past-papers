"""Собирает практикум D7: описательная статистика, регрессия и корреляция.

Тридцать пятый практикум серии. statistics.regression целиком (33 блока,
69 баллов) и 22 балла описательной статистики, приписанные к D7 картой:
44 блока и 91 балл. Revisit прежней карты закрыт в пользу приёма —
описательная статистика стала первыми двумя ступенями, а практикум
переименован.

Лестница из восьми приёмов идёт от одной величины к двум: сводное число и
обратный ход к нему, ящик с усами, r, прямая, подстановка, выбор прямой,
точка средних и то, чего данные не говорят.

Двадцать восьмое понятие равенства ответов: **прямая — это наименьшая
сумма квадратов**. Проверка ищет прямую поиском по дну суммы квадратов
промахов, а r берёт как долю объяснённого разброса; формул Sxy/Sxx
внутри нет.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_d7.py прогоняет по нему весь ноутбук и требует, чтобы
каждая проверка сказала ✅, а типовые ошибки — ❌.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/practicum-d7-regression.ipynb')

TRIGGER = {1: 'summary', 2: 'outlier', 3: 'strength', 4: 'fit', 5: 'predict',
           6: 'direction', 7: 'centre', 8: 'cause', 9: 'summary', 10: 'direction',
           11: 'centre', 12: 'outlier'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

# Три ответа-слова не из чего вычислить: их проверяет хеш.
D_13A = digest('b')            # «прямого влияния данные не показывают»
D_13C = digest('a')            # медиана после плохого сна = Q3 после хорошего
D_13D = digest('convenience')  # первые пятьдесят покупателей

ANSWERS = {
    'q1': '(5, 19)',
    'q2a': '7',
    'q2b': '1.58',
    'q3a': '45',
    'q3b': '25',
    'q4a': '0.28',
    'q4b_fence': '0.47',
    'q4b': "'no'",
    'q4c': "'positive'",
    'q5a': '(1.01, 2.45)',
    'q5b': '0.981',
    'q5c': '81',
    'q6a': '(0.805, 2.88)',
    'q6a_r': '0.978',
    'q6b': '0.805',
    'q6c': '8.52',
    'q7a': '(0.433, 4.50)',
    'q7b': '12.3',
    'q7c': '(15, 11)',
    'q8a': '0.884',
    'q8b': '(1.37, 64.5)',
    'q8c': '6.83',
    'q9b': 'Eq(x, 0.0935*y + 7.43)',
    'q9c': '36',
    'q10a': '0.901',
    'q10b': "'extrapolation'",
    'q10c_i': "'wrong line'",
    'q10c_ii': '86',
    'q11a': '16',
    'q11b': '(17, 20)',
    'q12a': '16',
    'q12b_i': '12',
    'q12b_ii': '34',
    'q13a': "'b'",
    'q13b': "'no effect'",
    'q13c': "'a'",
    'q13d': "'convenience'",
    'qt_a': '157',
    'qt_b': '(160, 20.9)',
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
# D7 — Describing data: summary statistics, regression and correlation

**91 marks of the archive, eight techniques, thirteen tasks.** Everything the
archive asks about a set of data from May 2021 to November 2025: the numbers
that summarise one variable, the box and whisker diagram and its outliers,
and the line and the coefficient that describe two variables together.

## The one idea

A summary number is **a property of the data set**, and the data set can be
recovered from it one step back:

$$\text{sum}=n\cdot\bar x$$

Half of the one-variable questions in the archive are not *find the mean*
but *the mean is known — find the missing value*. The same move comes back
with two variables: the regression line passes through $(\bar x,\bar y)$,
and a missing value hides in $\bar y$.

## What the calculator gives, and what it does not

For two variables the GDC gives everything at once: $a$, $b$ and $r$ from one
screen. What it does not give is **which line** to use, **whether** to use it,
and **what it means**. Those are the marks that are lost.

| the question says | what it wants |
|---|---|
| *the regression line of $y$ on $x$* | the line that predicts $y$ |
| *predict $x$ when $y=\dots$* | the line of $x$ on $y$ — a different line |
| *a value outside the data* | extrapolation: the line should not be used |
| *the two regression lines* | they meet at $(\bar x,\bar y)$ |
| *does $x$ cause $y$?* | correlation does not show that |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | one variable: the summary numbers, the box and its fences | 1–4 |
| 🟡 | two variables: $r$, the line, the prediction, the mean point | 5–8 |
| 🔴 | which line, the reverse step through the mean point, what the data do not say | 9–13 |

Every task is a real past-paper question, cited.

**79 of these 91 marks are on a calculator paper, and the number flatters
more than anywhere else in the series.** The button really works for about
25 of them: $a$, $b$ and $r$ from raw data and one standard deviation. The
other 54 are a substitution, two linear equations or one sentence.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Sample, Box, Pairs, fit, strength

language('en')                 # this notebook is in English, and so are the checks

# Sample([...]) is a list of observations; Sample({value: frequency}) a table.
#     mean(S), median(S), quartiles(S), iqr(S), deviation(S), spread(S)
# Box(lowest, Q1, median, Q3, highest) is what a box and whisker diagram shows.
#     fence(B) — the two outlier fences, clean(B) — "no outliers"
# Pairs(xs, ys) is two-variable data.
#     fit(D) — (a, b) of the line of y on x; fit(D, of='x') — x on y
#     strength(D) — r, centre(D) — the mean point
# Letters are allowed in a Sample or a Box: the checks put your answer in.

print('ready; sympy', sp.__version__)
demo = Pairs([1, 2, 3, 4, 5], [2, 4, 5, 4, 5])
print('the line of y on x:', fit(demo))
print('r:                 ', strength(demo))
print('the mean point:    ', centre(demo))
""")

md(r"""
---
## Map of the eight techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the summary number | *find the standard deviation*, *the median is 4.5 — find $x$*, *determine the two scores* | $\text{sum}=n\bar x$; the median is a place |
| 2 | the box and its fences | *the largest value not an outlier*, *verify that 0.46 is not an outlier* | $Q_3+1.5\cdot\text{IQR}$ |
| 3 | the correlation coefficient | *find Pearson's product-moment correlation coefficient $r$* | the GDC's linear regression screen |
| 4 | the line from the data | *the regression line of $y$ on $x$ … find $a$ and $b$* | the same screen |
| 5 | the prediction | *use this model to predict*, *interpret $a$ in context* | substitution; $a$ is the change per unit |
| 6 | which line, and where not | *an appropriate regression equation*, *why is this method not appropriate* | predict $x$ — the line of $x$ on $y$; outside the data — no line |
| 7 | the mean point | *find the mean arm span*, *verify that $\bar y=16$* | both lines pass through $(\bar x,\bar y)$ |
| 8 | what the data do not say | *comment on the validity of the assertion*, *how would $r$ be affected* | correlation is not cause; $r$ ignores shifts |

Techniques 1–2 are one variable. Techniques 3–5 are the calculator's one
screen, read three ways. Techniques 6–8 are the questions the screen does not
answer.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. One variable

## Theory: the summary number, and the step back

Five marks: $12,\ 15,\ p,\ 18,\ 20$, with mean $16$. The mean is not a
formula to evaluate here — it is an equation for $p$:

$$\frac{12+15+p+18+20}{5}=16\ \Rightarrow\ 65+p=80\ \Rightarrow\ p=15$$

That is the whole technique: **$\text{sum}=n\cdot\text{mean}$**, written down
before anything else.

**Two unknowns need two equations.** The mean gives one — the sum of the
unknowns. The second comes from somewhere else in the question: a
difference, a range, a condition such as *one of them scored more than 17*.
The range is $\max-\min$, and when a new value lies outside the old set, it
**becomes** the new maximum or minimum.

**The median is a place, not a value.** Of $n$ ordered observations it stands
at place $\frac{n+1}{2}$: the 5th of 9, halfway between the 5th and 6th of 10.
In a frequency table count along the frequencies. For

| value | 1 | 2 | 3 |
|---|---|---|---|
| frequency | 3 | 5 | 2 |

the 5th and 6th observations are both $2$, so the median is $2$ — not the
middle of the column of values.

**The standard deviation in IB divides by $n$.** The calculator shows two:
$\sigma_x$ (divide by $n$) and $s_x$ (divide by $n-1$). The paper wants
$\sigma_x$. For the table above $\bar x=1.9$ and $\sigma=0.7$.

> **In the notebook** `Sample({1: 3, 2: 5, 3: 2})` is that table; `median(S)`
> and `deviation(S)` count it. A letter in the list — `Sample([12, 15, p, 18, 20])`
> — is a missing value, and `mean(S)` comes back as an expression in it.
""")

md(r"""
### Task 1 🟢 — *November 2025 TZ3 Paper 2 Q2(b), 5 marks*

A teacher sets her class of 30 pupils a quiz. Aiden and Brett were absent on
the day; the box and whisker diagram of the 28 pupils who took the quiz runs
from a lowest score of $6$ to a highest of $17$.

Aiden and Brett take the quiz when they return. Aiden scores less than $6$.
Brett scores more than $17$.

The mean score of the 28 pupils was $10.5$. The mean score for all 30 pupils is
now $10.6$. The range of scores for all 30 pupils is $14$.

Determine Aiden's score and Brett's score.

*Enter the pair (Aiden, Brett). The check puts both scores into the class and
recounts the mean and the range.*
""")

code(r"""
a, b = symbols('a b')    # Aiden's and Brett's scores

q1 = ...         # (Aiden, Brett)

others = Bunch(28, average=10.5, lowest=6, highest=17)
scores = Sample([others, a, b])

verify_missing('1', q1, scores, holds=[a < 6, b > 17], mean=10.6, range=14)
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ1 Paper 2 Q1, 4 marks*

The number of hours spent exercising each week by a group of students is shown
in the following table.

| exercising time (hours) | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| number of students | 5 | 1 | 4 | 3 | $x$ |

The median is $4.5$ hours.

**(a)** Find the value of $x$.

**(b)** Find the standard deviation.

*(b) to three significant figures.*
""")

code(r"""
q2a = ...        # x
q2b = ...        # the standard deviation

hours = Sample({2: 5, 3: 1, 4: 4, 5: 3, 6: x})

verify_missing('2(a)', q2a, hours, median=4.5)
verify_summary('2(b)', q2b, hours.put({x: 7}), 'deviation')
""")

# ================================================================= теория 2
md(r"""
## Theory: five numbers, and the rule for an outlier

A box and whisker diagram shows five numbers and nothing else: the lowest
value, $Q_1$, the median, $Q_3$ and the highest value. There is **no mean on
it**, and a question that asks you to compare means from two diagrams is
asking for something that is not there.

**An outlier is a rule, not an opinion.** A value is an outlier when it lies
more than $1.5\cdot\text{IQR}$ beyond the box:

$$x<Q_1-1.5\cdot\text{IQR}\qquad\text{or}\qquad x>Q_3+1.5\cdot\text{IQR}$$

For the box $3,\ 8,\ 11,\ 14,\ 25$: $\text{IQR}=6$, the upper fence is
$14+9=23$, and $25$ **is** an outlier. The largest value that would not be one
is the fence itself, $23$.

**"There are no outliers" is an inequality.** Take the box
$5,\ L,\ 20,\ U,\ 44$ with $\text{IQR}=12$ and no outliers. Then
$44\le U+18$, so $U\ge 26$; and $5\ge L-18=U-30$, so $U\le 35$. One more
condition is not written anywhere and still holds: a quartile cannot pass the
median, so $L=U-12\le 20$ and $U\le 32$. The upper quartile can be anything
from $26$ to $32$ — and *the minimum possible value of $U$* is the left end,
$26$. Solve the inequality, do not guess the equation.

**The box shows the skew.** When the median sits closer to $Q_1$ than to $Q_3$,
the upper half of the data is more spread out: the tail is on the right
(*positively skewed*), and the few large values pull the mean **above** the
median.

> **In the notebook** `Box(3, 8, 11, 14, 25)` is that diagram, `fence(B)` gives
> both fences and `clean(B)` is the condition *no outliers*.
""")

md(r"""
### Task 3 🟢 — *May 2021 TZ1 Paper 1 Q3, 5 marks*

A research student weighed lizard eggs in grams. The box and whisker diagram of
the results has lowest value $10$, lower quartile $L$, median $40$, upper
quartile $U$ and highest value $75$.

The interquartile range is $20$ grams and there are no outliers in the results.

**(a)** Find the minimum possible value of $U$.

**(b)** Hence, find the minimum possible value of $L$.

*No calculator.*
""")

code(r"""
L, U = symbols('L U')

q3a = ...        # the minimum possible U
q3b = ...        # the minimum possible L

eggs = Box(10, L, 40, U, 75)
rules = [Eq(iqr(eggs), 20), clean(eggs)]

verify_bound('3(a)', q3a, eggs, U, 'least', holds=rules)
verify_bound('3(b)', q3b, eggs, L, 'least', holds=rules)
""")

md(r"""
### Task 4 🟡 — *May 2022 TZ2 Paper 2 Q4(a)–(c), 5 marks*

A random sample of nine adults were selected to see whether sleeping well
affected their reaction times to a visual stimulus. The box and whisker
diagram of the reaction times, in seconds, measured after sleeping well reads

| lowest | $Q_1$ | median | $Q_3$ | highest |
|---|---|---|---|---|
| 0.24 | 0.27 | 0.28 | 0.35 | 0.46 |

**(a)** State the median reaction time after sleeping well.

**(b)** Verify that the measurement of $0.46$ seconds is not an outlier.

**(c)** State why it appears that the mean reaction time is greater than the
median reaction time.

*In (b) give the upper fence and say `'yes'` or `'no'`: is 0.46 an outlier?
In (c) name the skew: `'positive'`, `'negative'` or `'none'`.*
""")

code(r"""
q4a = ...          # the median
q4b_fence = ...    # the upper fence
q4b = ...          # 'yes' or 'no': is 0.46 an outlier?
q4c = ...          # the skew of the data

slept = Box(0.24, 0.27, 0.28, 0.35, 0.46)

verify_summary('4(a)', q4a, slept, 'median')
verify_fence('4(b) fence', q4b_fence, slept, 'upper')
verify_outlier('4(b)', q4b, slept, 0.46)
verify_skew('4(c)', q4c, slept)
""")

# ================================================================= теория 3
md(r"""
---
# 🟡 Part 2. Two variables

## Theory: one screen, two answers

Take the data

| $x$ | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| $y$ | 2 | 4 | 5 | 4 | 5 |

Linear regression on the GDC gives, from one screen,

$$y=0.6x+2.2,\qquad r=0.775$$

**What the line is.** Of all straight lines, it is the one for which the sum of
the squared vertical misses $\sum\left(y_i-(ax_i+b)\right)^2$ is the smallest
— the *least squares* line. That is also how this notebook's checks find it:
not from a formula, but by searching for the bottom of that sum.

**What $r$ is.** A number from $-1$ to $1$: how closely the points hug the
line. Its sign is the sign of the gradient, always. Its square is the share of
the spread of $y$ that the line explains — here $0.775^2=0.6$, sixty per cent.

**Four ways to lose the marks from this screen.**

* writing $r^2$ instead of $r$ — the calculator shows both, one line apart;
* $a$ and $b$ the other way round — some calculator models write $y=a+bx$;
* two significant figures: $0.78$ is not $0.775$;
* the quadratic or exponential regression, one line away in the menu.

> **Keep the unrounded values.** The next part almost always substitutes into
> this line. Use the stored $a$ and $b$, not the rounded ones.
""")

md(r"""
### Task 5 🟢 — *November 2022 Paper 2 Q1, 5 marks*

The following table shows the Mathematics test scores ($x$) and the Science
test scores ($y$) for a group of eight students.

| Mathematics ($x$) | 64 | 68 | 72 | 75 | 80 | 82 | 85 | 86 |
|---|---|---|---|---|---|---|---|---|
| Science ($y$) | 67 | 72 | 77 | 76 | 84 | 83 | 89 | 91 |

The regression line of $y$ on $x$ for this data can be written in the form
$y=ax+b$.

**(a)** Find the value of $a$ and the value of $b$.

**(b)** Write down the value of the Pearson's product-moment correlation
coefficient, $r$.

**(c)** Use the equation of your regression line to predict the Science test
score for a student who has a score of $78$ on the Mathematics test. Express
your answer to the nearest integer.
""")

code(r"""
q5a = ...        # (a, b)
q5b = ...        # r
q5c = ...        # the Science score, to the nearest integer

scores = Pairs([64, 68, 72, 75, 80, 82, 85, 86],
               [67, 72, 77, 76, 84, 83, 89, 91])

verify_fit('5(a)', q5a, scores)
verify_strength('5(b)', q5b, scores)
verify_estimate('5(c)', q5c, scores, 78, whole=True)
""")

md(r"""
### Task 6 🟢 — *May 2021 TZ2 Paper 2 Q1, 6 marks*

At a café, the waiting time between ordering and receiving a cup of coffee
depends on the number of customers who have already ordered and are waiting.
Sarah visited the café on five consecutive days.

| number of customers ($x$) | 3 | 9 | 11 | 10 | 5 |
|---|---|---|---|---|---|
| Sarah's waiting time ($y$ minutes) | 6 | 10 | 12 | 11 | 6 |

The relationship between $x$ and $y$ can be modelled by the regression line of
$y$ on $x$ with equation $y=ax+b$.

**(a)** (i) Find the value of $a$ and the value of $b$. (ii) Write down the
value of Pearson's product-moment correlation coefficient, $r$.

**(b)** Interpret, in context, the value of $a$ found in part (a)(i).

**(c)** Seven customers are already waiting. Use the result from part (a)(i)
to estimate Sarah's waiting time.

*In (b) give the number the interpretation is about: by how many minutes does
the waiting time change for **one** more customer? On paper, the sentence.*
""")

code(r"""
q6a = ...        # (a, b)
q6a_r = ...      # r
q6b = ...        # minutes per one more customer
q6c = ...        # the estimated waiting time

cafe = Pairs([3, 9, 11, 10, 5], [6, 10, 12, 11, 6])

verify_fit('6(a)(i)', q6a, cafe)
verify_strength('6(a)(ii)', q6a_r, cafe)
verify_change('6(b)', q6b, cafe, 1)
verify_estimate('6(c)', q6c, cafe, 7)
""")

# ================================================================= теория 4
md(r"""
## Theory: the point every regression line goes through

The least squares line **always** passes through the mean point
$(\bar x,\bar y)$. For the data of the previous theory $\bar x=3$,
$\bar y=4$, and indeed $0.6\cdot3+2.2=4$.

That gives two things for free.

* **Drawing the line.** Two points fix it: $(\bar x,\bar y)$ and the
  $y$-intercept $(0,b)$. The mark scheme checks exactly that the line goes
  through $(\bar x,\bar y)$.
* **Writing down $\bar x$ and $\bar y$.** The calculator prints them on the
  same statistics screen; the question says *write down*, one mark.

**The gradient is a rate.** $a$ is how much $y$ changes when $x$ goes up by
one. So *what change in $y$ would three more units of $x$ bring?* is $3a$ —
not a substitution at all, and the intercept $b$ plays no part in it. In the
example that is $3\cdot0.6=1.8$.
""")

md(r"""
### Task 7 🟡 — *May 2021 TZ1 Paper 2 Q1(a)–(c), 5 marks*

The following table shows the data collected from an experiment.

| $x$ | 3.3 | 6.9 | 11.9 | 13.4 | 17.8 | 19.6 | 21.8 | 25.3 |
|---|---|---|---|---|---|---|---|---|
| $y$ | 6.3 | 8.1 | 8.4 | 11.6 | 10.3 | 12.9 | 13.1 | 17.3 |

The relationship between $x$ and $y$ can be modelled by the regression line of
$y$ on $x$ with equation $y=ax+b$.

**(a)** Write down the value of $a$ and the value of $b$.

**(b)** Use this model to predict the value of $y$ when $x=18$.

**(c)** Write down the value of $\bar x$ and the value of $\bar y$.
""")

code(r"""
q7a = ...        # (a, b)
q7b = ...        # y when x = 18
q7c = ...        # (x-bar, y-bar)

experiment = Pairs([3.3, 6.9, 11.9, 13.4, 17.8, 19.6, 21.8, 25.3],
                   [6.3, 8.1, 8.4, 11.6, 10.3, 12.9, 13.1, 17.3])

verify_fit('7(a)', q7a, experiment)
verify_estimate('7(b)', q7b, experiment, 18)
verify_centre('7(c)', q7c, experiment)
""")

md(r"""
### Task 8 🟡 — *November 2021 Paper 2 Q1(a)–(c), 5 marks*

In Lucy's music academy, eight students took their piano diploma examination.
Lucy recorded the average number of hours per week each student practised.

| average weekly practice ($h$ hours) | 28 | 13 | 45 | 33 | 17 | 29 | 39 | 36 |
|---|---|---|---|---|---|---|---|---|
| diploma score ($D$) | 115 | 82 | 120 | 116 | 79 | 101 | 110 | 121 |

**(a)** Find Pearson's product-moment correlation coefficient, $r$, for these
data.

**(b)** The relationship between the variables can be modelled by the
regression equation $D=ah+b$. Write down the value of $a$ and the value of $b$.

**(c)** One of these eight students wished she had practised more. Based on the
given data, determine how her score could have been expected to alter had she
practised an extra five hours per week.
""")

code(r"""
q8a = ...        # r
q8b = ...        # (a, b)
q8c = ...        # the change in the score

piano = Pairs([28, 13, 45, 33, 17, 29, 39, 36],
              [115, 82, 120, 116, 79, 101, 110, 121], names=('h', 'D'))

verify_strength('8(a)', q8a, piano)
verify_fit('8(b)', q8b, piano)
verify_change('8(c)', q8c, piano, 5)
""")

# ================================================================= теория 5
md(r"""
---
# 🔴 Part 3. What the screen does not decide

## Theory: two lines, not one

For the same data of the earlier theory there are **two** regression lines:

$$y\text{ on }x:\quad y=0.6x+2.2\qquad\qquad x\text{ on }y:\quad x=y-1$$

The first minimises the vertical misses, the second the horizontal ones. They
are different lines. To predict $x$ when $y=5$:

* the line of $x$ on $y$ gives $x=5-1=4$ — **right**;
* the line of $y$ on $x$ solved for $x$ gives $x=\frac{5-2.2}{0.6}=4.67$ —
  **wrong**, and it earns nothing.

The rule: **the variable you predict stands on the left**. On the GDC, enter
the lists the other way round.

**Extrapolation.** A line fitted to $x$ from $1$ to $5$ says nothing about
$x=40$. A value outside the range of the data is a reason — worth a mark on
its own — not to use the line at all.

*Why is this method not appropriate?* has two standard answers, and the
question decides which:

| the value given | the variable predicted | the reason |
|---|---|---|
| outside the data | either | `'extrapolation'` |
| inside the data | $x$, with the line of $y$ on $x$ | `'wrong line'` |
""")

md(r"""
### Task 9 🟡 — *May 2023 TZ1 Paper 2 Q3(b),(c), 5 marks*

The total number of children, $y$, visiting a park depends on the highest
temperature, $T$ °C. A park official predicts it with the model
$y=-0.6T^2+23T+110$, $10\le T\le35$.

An ice cream vendor investigates the relationship between the number of
children visiting the park and the number of ice creams sold, $x$, on five
different days.

| total number of children ($y$) | 81 | 175 | 202 | 346 | 360 |
|---|---|---|---|---|---|
| ice creams sold ($x$) | 15 | 27 | 23 | 35 | 46 |

**(b)** Find an appropriate regression equation that will allow the vendor to
predict the number of ice creams sold on a day when there are $y$ children in
the park.

**(c)** Hence, use your regression equation to predict the number of ice
creams that the vendor sells on a day when the highest temperature is $25$ °C.

*Enter (b) as an equation with three significant figures; (c) as a whole
number of ice creams.*
""")

code(r"""
q9b = ...        # the regression equation, Eq(... , ...)
q9c = ...        # ice creams sold at 25 °C

park = Pairs([81, 175, 202, 346, 360], [15, 27, 23, 35, 46], names=('y', 'x'))
children = -0.6*25**2 + 23*25 + 110          # the park model at T = 25

verify_fit('9(b)', q9b, park, of='x')
verify_estimate('9(c)', q9c, park, children, of='x', whole=True)
""")

md(r"""
### Task 10 🔴 — *May 2024 TZ1 Paper 2 Q5, 7 marks*

A class is given two tests, each scored out of 100.

| A, $x$ | 52 | 71 | 100 | 93 | 81 | 80 | 88 | 100 | 70 | 61 |
|---|---|---|---|---|---|---|---|---|---|---|
| B, $y$ | 58 | 80 | 92 | 98 | 90 | 82 | 100 | 100 | 65 | 74 |

The regression line of $y$ on $x$ is $y=0.822x+18.4$.

**(a)** Find the value of Pearson's product-moment correlation coefficient, $r$.

Paulo was absent for Test B and scored $10$ on Test A. The teacher estimated
his Test B score as $0.822(10)+18.4\approx27$.

**(b)** Give a reason why this method is not appropriate for Paulo.

Giovanni was absent for Test A and scored $90$ on Test B. The teacher solved
$90=0.822x+18.4$ and estimated his Test A score as $87$.

**(c)** (i) Give a reason why this method is not appropriate for Giovanni.
(ii) Use an appropriate method to show that the estimated Test A score for
Giovanni is $86$ to the nearest integer.

*Reasons are `'extrapolation'` or `'wrong line'`.*
""")

code(r"""
q10a = ...       # r
q10b = ...       # the reason for Paulo
q10c_i = ...     # the reason for Giovanni
q10c_ii = ...    # Giovanni's Test A estimate, to the nearest integer

tests = Pairs([52, 71, 100, 93, 81, 80, 88, 100, 70, 61],
              [58, 80, 92, 98, 90, 82, 100, 100, 65, 74])

verify_strength('10(a)', q10a, tests)
verify_reason('10(b)', q10b, tests, 10, given='x', predict='y')
verify_reason('10(c)(i)', q10c_i, tests, 90, given='y', predict='x')
verify_estimate('10(c)(ii)', q10c_ii, tests, 90, of='x', whole=True)
""")

# ================================================================= теория 6
md(r"""
## Theory: where the two lines meet

Both regression lines pass through $(\bar x,\bar y)$, and two different lines
share exactly one point — so **the means are the solution of a system**. For
the lines

$$y=0.5x+3\qquad\text{and}\qquad x=1.2y-1$$

substitute the first into the second: $x=1.2(0.5x+3)-1=0.6x+2.6$, so
$x=6.5$ and $y=0.5\cdot6.5+3=6.25$. The mean point is $(6.5,\ 6.25)$ — with
no data in sight.

**With data and one line.** Now $\bar x$ comes from the data, $\bar y$ from
the line, and a missing $y$-value from $\bar y$ one step back:
$\text{sum of }y=n\bar y$. This is Technique 1 again, carried over to two
variables.

> **Order the answer as asked.** *The mean arm span and the mean foot length*
> is a pair in that order, whatever order the lines were given in.
""")

md(r"""
### Task 11 🟡 — *May 2024 TZ2 Paper 2 Q2, 5 marks*

Consider the following bivariate data set where $p,q\in\mathbb Z^+$.

| $x$ | 5 | 6 | 6 | 8 | 10 |
|---|---|---|---|---|---|
| $y$ | 9 | 13 | $p$ | $q$ | 21 |

The regression line of $y$ on $x$ has equation $y=2.1875x+0.6875$. The
regression line passes through the mean point $(\bar x,\bar y)$.

**(a)** Given that $\bar x=7$, verify that $\bar y=16$.

**(b)** Given that $q-p=3$, find the value of $p$ and the value of $q$.

*In (a) enter the value of $\bar y$ the line gives.*
""")

code(r"""
p, q = symbols('p q', positive=True)

q11a = ...       # y-bar from the line
q11b = ...       # (p, q)

line = Eq(y, 2.1875*x + 0.6875)
ys = Sample([9, 13, p, q, 21], 'y')

verify_estimate('11(a)', q11a, line, 7)
verify_missing('11(b)', q11b, ys, holds=[Eq(q - p, 3)], mean=16)
""")

md(r"""
### Task 12 🔴 — *May 2022 TZ1 Paper 1 Q2, 7 marks*

A survey at a swimming pool is given to one adult in each family. The age of
the adult, $a$ years, and of their eldest child, $c$ years, are recorded. The
ages of the eldest child are summarised in a box and whisker diagram with
lowest value $2$, $Q_1=6$, median $7$, $Q_3=10$ and highest value $18$.

**(a)** Find the largest value of $c$ that would not be considered an outlier.

The regression line of $a$ on $c$ is $a=\frac74c+20$. The regression line of
$c$ on $a$ is $c=\frac12a-9$.

**(b)** (i) One of the adults surveyed is $42$ years old. Estimate the age of
their eldest child. (ii) Find the mean age of all the adults surveyed.

*No calculator.*
""")

code(r"""
q12a = ...       # the largest c that is not an outlier
q12b_i = ...     # the eldest child's age
q12b_ii = ...    # the mean age of the adults

a, c = symbols('a c')
children = Box(2, 6, 7, 10, 18)
a_on_c = Eq(a, Rational(7, 4)*c + 20)
c_on_a = Eq(c, a/2 - 9)

verify_fence('12(a)', q12a, children, 'upper')
verify_estimate('12(b)(i)', q12b_i, [a_on_c, c_on_a], 42, of=c)
verify_centre('12(b)(ii)', q12b_ii, [a_on_c, c_on_a], of=a)
""")

# ================================================================= теория 7
md(r"""
## Theory: what the numbers do not say

**Correlation is not cause.** A strong $r$ says that two quantities move
together. It does not say that one moves the other: ice cream sales and
sunburn are strongly correlated, and neither causes the other — the weather
causes both. *Comment on the assertion that $x$ has a direct effect on $y$* has
one answer: the data can show a correlation, never a cause.

And the reverse trap: when the question has **no** correlation in it — two box
plots, say — "correlation does not imply causation" earns **R0**. Compare what
is there: medians and quartiles.

**$r$ ignores shifts and stretches.** Adding the same number to every $x$, or
multiplying every $x$ by the same positive number, moves and stretches the
cloud of points without changing its shape. $r$ does not change. (Multiplying
by a **negative** number flips the sign of $r$.)

**Sampling methods**, named by how the sample was chosen:

| how | name |
|---|---|
| every member equally likely, chosen at random | simple random |
| every $k$-th from a list | systematic |
| whoever is easiest to reach | convenience |
| a fixed number from each group, not random | quota |
| random within each group, in proportion | stratified |
""")

md(r"""
### Task 13 🟡 — *four questions, 4 marks*

**(a)** *November 2021 Paper 2 Q1(d).* Lucy (Task 8) asserts that the number of
hours a student practises has a direct effect on their final diploma result.
Comment on the validity of Lucy's assertion. Choose the statement that earns
the mark:

* `'a'` — valid: $r=0.884$ is close to $1$;
* `'b'` — not valid: the data can only show a correlation, not a cause;
* `'c'` — valid: the gradient $a$ is positive;
* `'d'` — not valid: eight students are too few for any regression.

**(b)** *November 2021 Paper 2 Q1(e).* Lucy suspected that each student had not
been practising as much as they reported, and deducted a fixed number of hours
per week from each student's recorded hours. State how, if at all, the value of
$r$ would be affected: `'no effect'`, `'increases'` or `'decreases'`.

**(c)** *May 2022 TZ2 Paper 2 Q4(d).* The second box and whisker diagram of
Task 4, after **not** sleeping well, reads $0.27,\ 0.29,\ 0.35,\ 0.39,\ 0.48$.
Comment on whether the two diagrams provide any evidence that might suggest
that not sleeping well causes an increase in reaction time:

* `'a'` — yes: the median after not sleeping well equals the upper quartile
  after sleeping well;
* `'b'` — no: correlation does not imply causation;
* `'c'` — yes: the mean reaction time is higher after not sleeping well;
* `'d'` — no: the two diagrams overlap.

**(d)** *May 2025 TZ3 Paper 2 Q3(c).* A manager surveys the first 50 customers
to arrive at the supermarket on a particular day. Which best describes the
sampling method: simple random, systematic, convenience, quota or stratified?
""")

code(r"""
q13a = ...       # 'a', 'b', 'c' or 'd'
q13b = ...       # 'no effect', 'increases' or 'decreases'
q13c = ...       # 'a', 'b', 'c' or 'd'
q13d = ...       # the name of the sampling method

piano = Pairs([28, 13, 45, 33, 17, 29, 39, 36],
              [115, 82, 120, 116, 79, 101, 110, 121], names=('h', 'D'))
fewer = 3                                    # any fixed number of hours will do

check_word('13(a)', q13a, '""" + D_13A + r"""')
verify_effect('13(b)', q13b, piano, lambda hours: hours - fewer, which='h')
check_word('13(c)', q13c, '""" + D_13C + r"""')
check_word('13(d)', q13d, '""" + D_13D + r"""')
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would
make first**.

| code | technique |
| --- | --- |
| `summary` | a summary number, or a missing value found from one |
| `outlier` | the box and its fences |
| `strength` | the correlation coefficient $r$ |
| `fit` | the regression line from the data |
| `predict` | substitute into the line, or read its gradient |
| `direction` | which of the two lines, and whether to use one at all |
| `centre` | the mean point $(\bar x,\bar y)$ |
| `cause` | what the data do not show |

1. The mean of $4,\ 7,\ k,\ 9$ is $7$. Find $k$.
2. Is $31$ an outlier for the box $5,\ 12,\ 15,\ 19,\ 31$?
3. Find Pearson's product-moment correlation coefficient for the data in the table.
4. The relationship is modelled by the regression line of $y$ on $x$, $y=ax+b$. Find $a$ and $b$.
5. Use the regression line $y=1.2x+7$ to estimate $y$ when $x=15$.
6. Find a regression equation that predicts the price from the age of the car, given the line of age on price.
7. The regression lines of $y$ on $x$ and of $x$ on $y$ are given. Find $\bar x$.
8. Does a correlation of $0.95$ show that revision time improves exam scores?
9. Find the standard deviation of the frequency table.
10. The line was fitted for $2\le x\le 9$. Why should it not be used at $x=30$?
11. Given that $\bar x=4$, verify that $\bar y=11$ using the regression line.
12. State why the mean appears to be greater than the median, using the box plot.
""")

code("""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + """)
""")

# =================================================================== таймер
md(r"""
---
## On the clock — *May 2025 TZ1 Paper 2 Q4(a),(b), 5 marks*

**Five marks, seven minutes.** No hints.

In a study, measurements for arm span, $A$ cm, and foot length, $F$ cm, are
taken from a large group of adults. For this group, the regression line of $F$
on $A$ is $F=0.335A-32.6$, and the regression line of $A$ on $F$ is
$A=2.89F+99.3$. Each regression line passes through the mean point.

**(a)** By using an appropriate regression line, find an estimate of the arm
span for an adult with a foot length of $19.8$ cm.

**(b)** For this group of adults, find the mean arm span and the mean foot
length.

*Three significant figures. (b) as the pair (mean arm span, mean foot length).*

### Attempt log

| date | time | result |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
qt_a = ...       # the arm span estimate
qt_b = ...       # (mean arm span, mean foot length)

A, F = symbols('A F')
f_on_a = Eq(F, 0.335*A - 32.6)
a_on_f = Eq(A, 2.89*F + 99.3)

verify_estimate('timer (a)', qt_a, [f_on_a, a_on_f], 19.8, of=A)
verify_centre('timer (b)', qt_b, [f_on_a, a_on_f], order=(A, F))
""")

# ================================================================== решения
md(r"""
---
---

# 🔑 Solutions

Work these only after you have your own answer, or you are reading, not
practising.

---

**1** The 28 pupils scored $28\cdot10.5=294$ in total, the 30 pupils
$30\cdot10.6=318$. So Aiden and Brett together scored $318-294=24$.

Aiden is below $6$ and Brett above $17$, so they are the new lowest and highest
scores, and the range is Brett's score minus Aiden's: $B-A=14$. With $A+B=24$,

$$A=\boxed{5},\qquad B=\boxed{19}$$

(Part (a), 1 mark: the median of 30 is the middle of the 15th and 16th scores;
one score was added below the old median and one above, so the middle stays
where it was, at $10.5$.)

---

**2 (a)** The median $4.5$ lies between $4$ and $5$, so the middle of the
ordered data falls exactly between the last $4$ and the first $5$. There are
$5+1+4=10$ values up to $4$, so half the data is $10$ values: $\Sigma f=20$
and $13+x=20$, $x=\boxed{7}$.

**2 (b)** $\bar x=\dfrac{2\cdot5+3+4\cdot4+5\cdot3+6\cdot7}{20}=4.3$ and
$\sigma=\boxed{1.58}$ $(1.58429\ldots)$ — $\sigma_x$ from the calculator, the
one that divides by $n$.

---

**3 (a)** No outlier on the right: $75\le U+1.5\cdot20=U+30$, so $U\ge45$. On
the left, with $L=U-20$: $10\ge L-30=U-50$, so $U\le60$. The minimum possible
value is $U=\boxed{45}$.

**3 (b)** $L=U-20$, so the minimum is $L=45-20=\boxed{25}$.

---

**4 (a)** The median line of the slept-well box: $\boxed{0.28}$ s.

**4 (b)** $\text{IQR}=0.35-0.27=0.08$ and the upper fence is
$0.35+1.5\cdot0.08=\boxed{0.47}$. Since $0.46<0.47$, the measurement is
$\boxed{\text{not an outlier}}$.

**4 (c)** The median ($0.28$) is much closer to $Q_1$ ($0.27$) than to $Q_3$
($0.35$): the data are $\boxed{\text{positively skewed}}$, and the long upper
tail pulls the mean above the median.

---

**5 (a)** $a=\boxed{1.01}$, $b=\boxed{2.45}$ $(1.01206\ldots,\ 2.45230\ldots)$.

**5 (b)** $r=\boxed{0.981}$ $(0.981464\ldots)$.

**5 (c)** $1.01206\ldots\cdot78+2.45230\ldots=81.39\ldots\approx\boxed{81}$.

---

**6 (a)** $a=\boxed{0.805}$, $b=\boxed{2.88}$ $(0.805084\ldots,\ 2.88135\ldots)$
and $r=\boxed{0.978}$ $(0.977772\ldots)$.

**6 (b)** $a$ is the (average) increase in waiting time, $\boxed{0.805}$
minutes, for each additional customer waiting ahead of Sarah.

**6 (c)** $0.805084\ldots\cdot7+2.88135\ldots=8.51694\ldots\approx\boxed{8.52}$
minutes.

---

**7 (a)** $a=\boxed{0.433}$, $b=\boxed{4.50}$ $(0.433156\ldots,\ 4.50265\ldots)$.

**7 (b)** $0.433156\ldots\cdot18+4.50265\ldots=12.2994\ldots\approx\boxed{12.3}$.

**7 (c)** $\bar x=\dfrac{120}{8}=\boxed{15}$ and $\bar y=\dfrac{88}{8}=\boxed{11}$.

(Part (d), 2 marks: a straight line through $(15,11)$ that meets the $y$-axis
near $4.50$.)

---

**8 (a)** $r=\boxed{0.884}$ $(0.883529\ldots)$.

**8 (b)** $a=\boxed{1.37}$, $b=\boxed{64.5}$ $(1.36609\ldots,\ 64.5171\ldots)$.

**8 (c)** Five more hours change the score by
$5a=5\cdot1.36609\ldots=\boxed{6.83}$: about seven marks more. The intercept
plays no part.

---

**9 (b)** The vendor predicts $x$ from $y$, so the line wanted is $x$ on $y$:

$$\boxed{x=0.0935y+7.43}\qquad(0.0935114\ldots,\ 7.43053\ldots)$$

**9 (c)** At $25$ °C the model gives $y=-0.6\cdot625+575+110=310$ children, and
$x=0.0935114\ldots\cdot310+7.43053\ldots=36.419\ldots\approx\boxed{36}$ ice
creams.

---

**10 (a)** $r=\boxed{0.901}$ $(0.901017\ldots)$.

**10 (b)** Paulo's Test A score, $10$, is far outside the data ($52$ to $100$):
$\boxed{\text{extrapolation}}$.

**10 (c)(i)** The teacher predicts $x$ from $y$ with the line of $y$ on $x$:
$\boxed{\text{the wrong line}}$ — it should be the line of $x$ on $y$.

**10 (c)(ii)** The line of $x$ on $y$ is $x=0.987124\ldots y-3.21971\ldots$, and
at $y=90$ it gives $x=85.6214\ldots\approx\boxed{86}$.

---

**11 (a)** $\bar y=2.1875\cdot7+0.6875=15.3125+0.6875=\boxed{16}$.

**11 (b)** $\dfrac{9+13+p+q+21}{5}=16$ gives $p+q=37$; with $q-p=3$,

$$p=\boxed{17},\qquad q=\boxed{20}$$

---

**12 (a)** $\text{IQR}=10-6=4$ and $10+1.5\cdot4=\boxed{16}$.

**12 (b)(i)** To estimate $c$ from $a$ use the line of $c$ on $a$:
$c=\frac12\cdot42-9=\boxed{12}$ years.

**12 (b)(ii)** Both lines pass through $(\bar c,\bar a)$. Substituting
$c=\frac12a-9$ into $a=\frac74c+20$:

$$a=\frac78a-\frac{63}4+20\ \Rightarrow\ \frac18a=\frac{17}4\ \Rightarrow\ a=\boxed{34}$$

---

**13 (a)** $\boxed{\text{b}}$. The mark scheme: *Lucy is incorrect in suggesting
there is a causal relationship. This might be true, but the data can only
indicate a correlation.*

**13 (b)** $\boxed{\text{no effect}}$: subtracting the same number from every
$h$ shifts the cloud of points, and $r$ measures its shape.

**13 (c)** $\boxed{\text{a}}$. The mark scheme accepts a comparison of medians
and quartiles (or *the sample of 9 is too small to draw any conclusions*); it
does not accept a comparison of means, and it gives R0 to *correlation does
not imply causation*.

**13 (d)** The first 50 to arrive are simply the easiest to reach:
$\boxed{\text{convenience}}$ sampling.

---

## Timer

**(a)** Predict $A$ from $F$ with the line of $A$ on $F$:
$A=2.89\cdot19.8+99.3=156.522\approx\boxed{157}$ cm.

**(b)** The lines meet at the mean point. Substitute $F=0.335A-32.6$ into
$A=2.89F+99.3$:

$$A=0.96815A-94.214+99.3\ \Rightarrow\ 0.03185A=5.086\ \Rightarrow\ A=159.69\ldots$$

so the mean arm span is $\boxed{160}$ cm and the mean foot length is
$F=0.335\cdot159.69\ldots-32.6=\boxed{20.9}$ cm.
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
