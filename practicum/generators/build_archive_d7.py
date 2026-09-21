"""Собирает архивный ноутбук D7: вся тема данных подряд.

Двадцать третий ноутбук формата, после B4, C3, B5, E1, E2, E3, D2, D1, C2,
A1, E4, E5, E6, A2, D3, D4, D5, D6, C5, C6, C7 и E8. Практикум учит:
лестница из приёмов, теория перед каждым, три уровня сложности, тренажёр
распознавания, задание на время. Архив не учит. Он даёт набивать руку:
**вся тема подряд, по тем же восьми приёмам, без единой строчки теории**.
Семнадцать вопросов бумаг, разнесённых на тридцать четыре пункта, 91 балл.

Разметка взята из карточки statistics-regression.yaml: поле blocks у
каждого приёма. Дубля в теме нет, и вычитать нечего: 44 блока, 91 балл.

Части одного вопроса разнесены по своим приёмам: ноябрь 2021 Q1 — в §§ 3,
4, 5 и 8; май 2021 TZ1 Q1 — в §§ 4, 5 и 7; май 2022 TZ1 Paper 1 Q2 — в §§ 2
и 7; май 2022 TZ2 Q4 — в §§ 2 и 8. Условие каждого пункта повторено
целиком, насколько оно нужно пункту.

Хешей четыре — ответы-слова, которые не из чего вычислить: почему медиана
осталась 10.5, прямое ли влияние у практики на экзамен, есть ли у ящиков
сна повод говорить о причине, и как называется способ отбора. Всё прочее
проверяется самими данными вопроса.

ANSWERS хранит эталонный ответ для каждого placeholder. В ноутбук он
не попадает — practicum/tests/check_archive_d7.py подставляет эталоны
построчно и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

from kit import digest

NOTEBOOK = os.path.join(
    ROOT, 'practicum/statistics/archive-d7-regression.ipynb')

D_1_1A = digest('a')            # один ниже медианы, другой выше
D_8_1 = digest('b')             # данные показывают связь, не причину
D_8_3 = digest('a')             # медиана после плохого сна = Q3 после хорошего
D_8_4 = digest('convenience')

ANSWERS = {
    # § 1. The summary number
    'q1_1a': "'a'",
    'q1_1b': '(5, 19)',
    'q1_2a': '7',
    'q1_2b': '1.58',
    'q1_3': '(17, 20)',
    'q1_4a': '6.45',
    'q1_4b_i': '14.0',
    'q1_4b_ii': '18.5',
    # § 2. The box and its fences
    'q2_1a': '45',
    'q2_1b': '25',
    'q2_2': '16',
    'q2_3a': '0.28',
    'q2_3b_fence': '0.47',
    'q2_3b': "'no'",
    'q2_3c': "'positive'",
    # § 3. The correlation coefficient
    'q3_1': '0.978',
    'q3_2': '0.884',
    'q3_3': '0.981',
    'q3_4': '0.901',
    'q3_5': '0.954',
    # § 4. The line from the data
    'q4_1a': '(0.433, 4.50)',
    'q4_1d': '(15, 11)',
    'q4_2': '(1.37, 64.5)',
    'q4_3': '(1.01, 2.45)',
    'q4_4': '(1.93, 7.22)',
    'q4_5': '(1.98, 40.2)',
    # § 5. The prediction
    'q5_1': '12.3',
    'q5_2b': '0.805',
    'q5_2c': '8.52',
    'q5_3': '6.83',
    'q5_4': '81',
    'q5_5': '45.9',
    'q5_6': '157',
    'q5_7': '79.8',
    # § 6. Which line, and where not
    'q6_1b': 'Eq(x, 0.0935*y + 7.43)',
    'q6_1c': '36',
    'q6_2b': "'extrapolation'",
    'q6_2c_i': "'wrong line'",
    'q6_2c_ii': '86',
    # § 7. The mean point
    'q7_1': '(15, 11)',
    'q7_2': '16',
    'q7_3': '(160, 20.9)',
    'q7_4_i': '12',
    'q7_4_ii': '34',
    # § 8. What the data do not say
    'q8_1': "'b'",
    'q8_2': "'no effect'",
    'q8_3': "'a'",
    'q8_4': "'convenience'",
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
# D7 archive — describing data, all of it

**Seventeen questions, 91 marks.** Every question the archive asks about a set
of data, from May 2021 to November 2025 — summary numbers, box and whisker
diagrams, correlation and regression — in the order of the eight techniques
rather than the order of the papers.

No theory. No worked examples. The theory is in the practicum,
`practicum-d7-regression.ipynb`.

| § | technique | parts | marks |
|---|---|---|---|
| 1 | The summary number | 4 | 20 |
| 2 | The box and its fences | 3 | 13 |
| 3 | The correlation coefficient | 5 | 9 |
| 4 | The line from the data | 5 | 11 |
| 5 | The prediction | 7 | 15 |
| 6 | Which line, and where not | 2 | 10 |
| 7 | The mean point | 4 | 9 |
| 8 | What the data do not say | 4 | 4 |

The checks are the same ones the practicum uses and they store nothing. Each is
handed the data exactly as the question gives them: `verify_fit` searches for
the line with the least sum of squared misses, `verify_strength` takes $r$ from
the same search, `verify_missing` puts your values into the data and recounts,
`verify_bound` solves the no-outlier inequality itself. Three significant
figures, unless the question asks otherwise.

**Parts of one question are split by technique.** November 2021 Q1 appears in
§§ 3, 4, 5 and 8; May 2021 TZ1 Q1 in §§ 4, 5 and 7. Each part repeats what it
needs.

Four answers are words that nothing can compute — a reason, a claim, the name
of a sampling method. Those are chosen from a list and checked by a hash.

Solutions are at the very bottom, deliberately far away.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Sample, Box, Pairs, fit, strength

language('en')                 # this notebook is in English, and so are the checks

print('ready; sympy', sp.__version__)
""")

# ================================================================ § 1
md(r"""
---
# § 1. The summary number

**Four questions, 20 marks.** $\text{sum}=n\cdot\text{mean}$; the median is a
place; $\sigma$ divides by $n$.
""")

md(r"""
### 1.1 — *November 2025 TZ3 Paper 2 Q2, 6 marks*

A teacher sets her class of 30 pupils a quiz. Aiden and Brett were absent. The
box and whisker diagram of the 28 pupils who took the quiz has median $10.5$,
lowest score $6$ and highest score $17$. On their return Aiden scores less than
$6$ and Brett scores more than $17$.

**(a)** Explain, briefly, why the median score for all 30 pupils would still be
$10.5$. Choose:

* `'a'` — Aiden's score is below $10.5$ and Brett's is above, so the middle
  value stays in the same place;
* `'b'` — the mean only rises from $10.5$ to $10.6$;
* `'c'` — the range of the 30 scores is $14$;
* `'d'` — adding two scores never changes a median.

The mean score of the 28 pupils was $10.5$. The mean score for all 30 pupils is
now $10.6$. The range of scores for all 30 pupils is $14$.

**(b)** Determine Aiden's score and Brett's score.
""")

code(r"""
a, b = symbols('a b')

q1_1a = ...      # 'a', 'b', 'c' or 'd'
q1_1b = ...      # (Aiden, Brett)

scores = Sample([Bunch(28, average=10.5, lowest=6, highest=17), a, b])

check_word('1.1(a)', q1_1a, '""" + D_1_1A + r"""')
verify_missing('1.1(b)', q1_1b, scores, holds=[a < 6, b > 17], mean=10.6, range=14)
""")

md(r"""
### 1.2 — *May 2022 TZ1 Paper 2 Q1, 4 marks*

| exercising time (hours) | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|
| number of students | 5 | 1 | 4 | 3 | $x$ |

The median is $4.5$ hours.

**(a)** Find the value of $x$.

**(b)** Find the standard deviation.
""")

code(r"""
q1_2a = ...      # x
q1_2b = ...      # the standard deviation

hours = Sample({2: 5, 3: 1, 4: 4, 5: 3, 6: x})

verify_missing('1.2(a)', q1_2a, hours, median=4.5)
verify_summary('1.2(b)', q1_2b, hours.put({x: 7}), 'deviation')
""")

md(r"""
### 1.3 — *May 2024 TZ2 Paper 2 Q2(b), 4 marks*

Consider the bivariate data set, where $p,q\in\mathbb Z^+$.

| $x$ | 5 | 6 | 6 | 8 | 10 |
|---|---|---|---|---|---|
| $y$ | 9 | 13 | $p$ | $q$ | 21 |

It is known that $\bar y=16$. Given that $q-p=3$, find the value of $p$ and the
value of $q$.
""")

code(r"""
p, q = symbols('p q', positive=True)

q1_3 = ...       # (p, q)

verify_missing('1.3', q1_3, Sample([9, 13, p, q, 21], 'y'), holds=[Eq(q - p, 3)], mean=16)
""")

md(r"""
### 1.4 — *November 2025 TZ1 Paper 2 Q3(a),(b), 6 marks*

Data was collected on two variables, $x$ and $y$, from eight members of a
population.

| $x$ | 3.8 | 6.3 | 2.5 | 2.4 | 8.9 | 10.7 | 6.7 | 10.3 |
|---|---|---|---|---|---|---|---|---|
| $y$ | 11.8 | 9.7 | 6.1 | 4.1 | $p$ | 23.3 | 13.7 | 24.5 |

**(a)** Find $\bar x$.

The regression line of $y$ on $x$ for this data is $y=0.014375+2.1625x$.

**(b)** Find (i) $\bar y$; (ii) the value of $p$.
""")

code(r"""
p = symbols('p')

q1_4a = ...      # x-bar
q1_4b_i = ...    # y-bar
q1_4b_ii = ...   # p

xs = Sample([3.8, 6.3, 2.5, 2.4, 8.9, 10.7, 6.7, 10.3])
ys = Sample([11.8, 9.7, 6.1, 4.1, p, 23.3, 13.7, 24.5], 'y')
line = Eq(y, 0.014375 + 2.1625*x)

verify_summary('1.4(a)', q1_4a, xs, 'mean')
verify_estimate('1.4(b)(i)', q1_4b_i, line, mean(xs))
verify_missing('1.4(b)(ii)', q1_4b_ii, ys, mean=0.014375 + 2.1625*mean(xs))
""")

# ================================================================ § 2
md(r"""
---
# § 2. The box and its fences

**Three questions, 13 marks.** $Q_3+1.5\cdot\text{IQR}$ and
$Q_1-1.5\cdot\text{IQR}$; *no outliers* is an inequality.
""")

md(r"""
### 2.1 — *May 2021 TZ1 Paper 1 Q3, 5 marks*

A box and whisker diagram of the weights of lizard eggs, in grams, has lowest
value $10$, lower quartile $L$, median $40$, upper quartile $U$ and highest
value $75$. The interquartile range is $20$ grams and there are no outliers.

**(a)** Find the minimum possible value of $U$.

**(b)** Hence, find the minimum possible value of $L$.
""")

code(r"""
L, U = symbols('L U')

q2_1a = ...      # the minimum U
q2_1b = ...      # the minimum L

eggs = Box(10, L, 40, U, 75)
rules = [Eq(iqr(eggs), 20), clean(eggs)]

verify_bound('2.1(a)', q2_1a, eggs, U, 'least', holds=rules)
verify_bound('2.1(b)', q2_1b, eggs, L, 'least', holds=rules)
""")

md(r"""
### 2.2 — *May 2022 TZ1 Paper 1 Q2(a), 3 marks*

The ages of the eldest children of the adults at a swimming pool are summarised
in a box and whisker diagram with lowest value $2$, $Q_1=6$, median $7$,
$Q_3=10$ and highest value $18$.

Find the largest value of $c$ that would not be considered an outlier.
""")

code(r"""
q2_2 = ...       # the largest c that is not an outlier

verify_fence('2.2', q2_2, Box(2, 6, 7, 10, 18), 'upper')
""")

md(r"""
### 2.3 — *May 2022 TZ2 Paper 2 Q4(a)–(c), 5 marks*

Nine adults had their reaction times measured after sleeping well. The box and
whisker diagram reads: lowest $0.24$, $Q_1=0.27$, median $0.28$, $Q_3=0.35$,
highest $0.46$ (seconds).

**(a)** State the median reaction time after sleeping well.

**(b)** Verify that the measurement of $0.46$ seconds is not an outlier.

**(c)** State why it appears that the mean reaction time is greater than the
median reaction time.

*(b): the upper fence, and `'yes'` or `'no'`. (c): `'positive'`, `'negative'`
or `'none'`.*
""")

code(r"""
q2_3a = ...          # the median
q2_3b_fence = ...    # the upper fence
q2_3b = ...          # is 0.46 an outlier?
q2_3c = ...          # the skew

slept = Box(0.24, 0.27, 0.28, 0.35, 0.46)

verify_summary('2.3(a)', q2_3a, slept, 'median')
verify_fence('2.3(b) fence', q2_3b_fence, slept, 'upper')
verify_outlier('2.3(b)', q2_3b, slept, 0.46)
verify_skew('2.3(c)', q2_3c, slept)
""")

# ================================================================ § 3
md(r"""
---
# § 3. The correlation coefficient

**Five questions, 9 marks.** Three significant figures, and $r$, not $r^2$.
""")

md(r"""
### 3.1 — *May 2021 TZ2 Paper 2 Q1(a)(ii), 3 marks with (a)(i)*

| number of customers ($x$) | 3 | 9 | 11 | 10 | 5 |
|---|---|---|---|---|---|
| waiting time ($y$ minutes) | 6 | 10 | 12 | 11 | 6 |

Write down the value of Pearson's product-moment correlation coefficient, $r$.
(Part (a)(i), the line, is 5.2 below.)
""")

code(r"""
q3_1 = ...       # r

verify_strength('3.1', q3_1, Pairs([3, 9, 11, 10, 5], [6, 10, 12, 11, 6]))
""")

md(r"""
### 3.2 — *November 2021 Paper 2 Q1(a), 2 marks*

| weekly practice ($h$ hours) | 28 | 13 | 45 | 33 | 17 | 29 | 39 | 36 |
|---|---|---|---|---|---|---|---|---|
| diploma score ($D$) | 115 | 82 | 120 | 116 | 79 | 101 | 110 | 121 |

Find Pearson's product-moment correlation coefficient, $r$, for these data.
""")

code(r"""
q3_2 = ...       # r

piano = Pairs([28, 13, 45, 33, 17, 29, 39, 36],
              [115, 82, 120, 116, 79, 101, 110, 121], names=('h', 'D'))

verify_strength('3.2', q3_2, piano)
""")

md(r"""
### 3.3 — *November 2022 Paper 2 Q1(b), 1 mark*

| Mathematics ($x$) | 64 | 68 | 72 | 75 | 80 | 82 | 85 | 86 |
|---|---|---|---|---|---|---|---|---|
| Science ($y$) | 67 | 72 | 77 | 76 | 84 | 83 | 89 | 91 |

Write down the value of the Pearson's product-moment correlation coefficient,
$r$.
""")

code(r"""
q3_3 = ...       # r

maths = Pairs([64, 68, 72, 75, 80, 82, 85, 86], [67, 72, 77, 76, 84, 83, 89, 91])

verify_strength('3.3', q3_3, maths)
""")

md(r"""
### 3.4 — *May 2024 TZ1 Paper 2 Q5(a), 2 marks*

| A, $x$ | 52 | 71 | 100 | 93 | 81 | 80 | 88 | 100 | 70 | 61 |
|---|---|---|---|---|---|---|---|---|---|---|
| B, $y$ | 58 | 80 | 92 | 98 | 90 | 82 | 100 | 100 | 65 | 74 |

Find the value of Pearson's product-moment correlation coefficient, $r$.
""")

code(r"""
q3_4 = ...       # r

tests = Pairs([52, 71, 100, 93, 81, 80, 88, 100, 70, 61],
              [58, 80, 92, 98, 90, 82, 100, 100, 65, 74])

verify_strength('3.4', q3_4, tests)
""")

md(r"""
### 3.5 — *November 2025 TZ1 Paper 2 Q3(c), 1 mark*

For the data of 1.4, with the value of $p$ found there, find Pearson's
product-moment correlation coefficient, $r$.
""")

code(r"""
q3_5 = ...       # r

data = Pairs([3.8, 6.3, 2.5, 2.4, 8.9, 10.7, 6.7, 10.3],
             [11.8, 9.7, 6.1, 4.1, 18.5, 23.3, 13.7, 24.5])

verify_strength('3.5', q3_5, data)
""")

# ================================================================ § 4
md(r"""
---
# § 4. The line from the data

**Five questions, 11 marks.** The pair $(a,b)$ of $y=ax+b$, three significant
figures.
""")

md(r"""
### 4.1 — *May 2021 TZ1 Paper 2 Q1(a),(d), 4 marks*

| $x$ | 3.3 | 6.9 | 11.9 | 13.4 | 17.8 | 19.6 | 21.8 | 25.3 |
|---|---|---|---|---|---|---|---|---|
| $y$ | 6.3 | 8.1 | 8.4 | 11.6 | 10.3 | 12.9 | 13.1 | 17.3 |

The relationship between $x$ and $y$ can be modelled by the regression line of
$y$ on $x$ with equation $y=ax+b$.

**(a)** Write down the value of $a$ and the value of $b$.

**(d)** Draw the line of best fit on the scatter diagram.

*For (d) enter the point, other than the $y$-intercept, that the line has to go
through to earn the mark.*
""")

code(r"""
q4_1a = ...      # (a, b)
q4_1d = ...      # the point the line must pass through

experiment = Pairs([3.3, 6.9, 11.9, 13.4, 17.8, 19.6, 21.8, 25.3],
                   [6.3, 8.1, 8.4, 11.6, 10.3, 12.9, 13.1, 17.3])

verify_fit('4.1(a)', q4_1a, experiment)
verify_centre('4.1(d)', q4_1d, experiment)
""")

md(r"""
### 4.2 — *November 2021 Paper 2 Q1(b), 1 mark*

For the practice data of 3.2, the relationship can be modelled by the regression
equation $D=ah+b$. Write down the value of $a$ and the value of $b$.
""")

code(r"""
q4_2 = ...       # (a, b)

verify_fit('4.2', q4_2, piano)
""")

md(r"""
### 4.3 — *November 2022 Paper 2 Q1(a), 2 marks*

For the Mathematics and Science scores of 3.3, the regression line of $y$ on $x$
can be written in the form $y=ax+b$. Find the value of $a$ and the value of $b$.
""")

code(r"""
q4_3 = ...       # (a, b)

verify_fit('4.3', q4_3, maths)
""")

md(r"""
### 4.4 — *May 2023 TZ2 Paper 2 Q1(a), 2 marks*

A botanist measures the average height, $h$ cm, of plants after $d$ days.

| days ($d$) | 2 | 5 | 13 | 24 | 33 | 37 | 42 |
|---|---|---|---|---|---|---|---|
| height ($h$) | 10 | 16 | 30 | 59 | 76 | 79 | 82 |

The regression line of $h$ on $d$ can be written $h=ad+b$. Find the value of
$a$ and the value of $b$.
""")

code(r"""
q4_4 = ...       # (a, b)

plants = Pairs([2, 5, 13, 24, 33, 37, 42], [10, 16, 30, 59, 76, 79, 82], names=('d', 'h'))

verify_fit('4.4', q4_4, plants)
""")

md(r"""
### 4.5 — *May 2025 TZ2 Paper 2 Q1(a), 2 marks*

| play time ($x$ hours) | 11 | 13 | 14 | 17 | 22 | 24 |
|---|---|---|---|---|---|---|
| sleep time ($y$ hours) | 62 | 65 | 68 | 75 | 84 | 87 |

The regression line of $y$ on $x$ can be written $y=ax+b$. Find the value of
$a$ and the value of $b$.
""")

code(r"""
q4_5 = ...       # (a, b)

sleep = Pairs([11, 13, 14, 17, 22, 24], [62, 65, 68, 75, 84, 87])

verify_fit('4.5', q4_5, sleep)
""")

# ================================================================ § 5
md(r"""
---
# § 5. The prediction

**Seven questions, 15 marks.** Substitute into the line; $a$ is the change per
unit.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 2 Q1(b), 2 marks*

Use the model of 4.1 to predict the value of $y$ when $x=18$.
""")

code(r"""
q5_1 = ...       # y at x = 18

verify_estimate('5.1', q5_1, experiment, 18)
""")

md(r"""
### 5.2 — *May 2021 TZ2 Paper 2 Q1(a)(i),(b),(c), 3 marks*

For the café data of 3.1, with the regression line $y=ax+b$ of waiting time on
number of customers:

**(b)** Interpret, in context, the value of $a$.

**(c)** Seven customers are already waiting. Estimate Sarah's waiting time.

*(b): the number of minutes the waiting time changes for one more customer.*
""")

code(r"""
q5_2b = ...      # minutes per one more customer
q5_2c = ...      # the waiting time with 7 customers ahead

cafe = Pairs([3, 9, 11, 10, 5], [6, 10, 12, 11, 6])

verify_change('5.2(b)', q5_2b, cafe, 1)
verify_estimate('5.2(c)', q5_2c, cafe, 7)
""")

md(r"""
### 5.3 — *November 2021 Paper 2 Q1(c), 2 marks*

One of the students of 3.2 wished she had practised more. Based on the given
data, determine how her score could have been expected to alter had she
practised an extra five hours per week.
""")

code(r"""
q5_3 = ...       # the change in the score

verify_change('5.3', q5_3, piano, 5)
""")

md(r"""
### 5.4 — *November 2022 Paper 2 Q1(c), 2 marks*

Use the regression line of 4.3 to predict the Science test score for a student
who has a score of $78$ on the Mathematics test, to the nearest integer.
""")

code(r"""
q5_4 = ...       # the Science score

verify_estimate('5.4', q5_4, maths, 78, whole=True)
""")

md(r"""
### 5.5 — *May 2023 TZ2 Paper 2 Q1(b), 2 marks*

Use the regression line of 4.4 to estimate the average height of the plants
when the experiment has been running for $20$ days.
""")

code(r"""
q5_5 = ...       # h at d = 20

verify_estimate('5.5', q5_5, plants, 20)
""")

md(r"""
### 5.6 — *May 2025 TZ1 Paper 2 Q4(a), 2 marks*

For a large group of adults the regression line of foot length on arm span is
$F=0.335A-32.6$, and of arm span on foot length $A=2.89F+99.3$. By using an
appropriate regression line, find an estimate of the arm span for an adult with
a foot length of $19.8$ cm.
""")

code(r"""
q5_6 = ...       # the arm span

A, F = symbols('A F')
f_on_a = Eq(F, 0.335*A - 32.6)
a_on_f = Eq(A, 2.89*F + 99.3)

verify_estimate('5.6', q5_6, [f_on_a, a_on_f], 19.8, of=A)
""")

md(r"""
### 5.7 — *May 2025 TZ2 Paper 2 Q1(b), 2 marks*

Use the regression line of 4.5 to estimate the sleep time of a child whose
weekly play time is $20$ hours.
""")

code(r"""
q5_7 = ...       # the sleep time

verify_estimate('5.7', q5_7, sleep, 20)
""")

# ================================================================ § 6
md(r"""
---
# § 6. Which line, and where not

**Two questions, 10 marks.** Predict $x$ with the line of $x$ on $y$; outside
the data, predict nothing.
""")

md(r"""
### 6.1 — *May 2023 TZ1 Paper 2 Q3(b),(c), 5 marks*

The number of children in a park is modelled by $y=-0.6T^2+23T+110$, where $T$
°C is the highest temperature. An ice cream vendor records, on five days:

| children ($y$) | 81 | 175 | 202 | 346 | 360 |
|---|---|---|---|---|---|
| ice creams sold ($x$) | 15 | 27 | 23 | 35 | 46 |

**(b)** Find an appropriate regression equation that will allow the vendor to
predict the number of ice creams sold on a day when there are $y$ children.

**(c)** Hence predict the number of ice creams sold on a day when the highest
temperature is $25$ °C.
""")

code(r"""
q6_1b = ...      # the regression equation
q6_1c = ...      # ice creams, a whole number

park = Pairs([81, 175, 202, 346, 360], [15, 27, 23, 35, 46], names=('y', 'x'))

verify_fit('6.1(b)', q6_1b, park, of='x')
verify_estimate('6.1(c)', q6_1c, park, -0.6*25**2 + 23*25 + 110, of='x', whole=True)
""")

md(r"""
### 6.2 — *May 2024 TZ1 Paper 2 Q5(b),(c), 5 marks*

For the tests of 3.4 the regression line of $y$ on $x$ is $y=0.822x+18.4$.
Paulo scored $10$ on Test A and was absent for Test B; the teacher estimated his
Test B score from this line. Giovanni scored $90$ on Test B and was absent for
Test A; the teacher solved $90=0.822x+18.4$ for his Test A score.

**(b)** Give a reason why this method is not appropriate for Paulo.

**(c)** (i) Give a reason why this method is not appropriate for Giovanni.
(ii) Use an appropriate method to estimate Giovanni's Test A score to the
nearest integer.

*Reasons: `'extrapolation'` or `'wrong line'`.*
""")

code(r"""
q6_2b = ...      # the reason for Paulo
q6_2c_i = ...    # the reason for Giovanni
q6_2c_ii = ...   # Giovanni's Test A score

verify_reason('6.2(b)', q6_2b, tests, 10, given='x', predict='y')
verify_reason('6.2(c)(i)', q6_2c_i, tests, 90, given='y', predict='x')
verify_estimate('6.2(c)(ii)', q6_2c_ii, tests, 90, of='x', whole=True)
""")

# ================================================================ § 7
md(r"""
---
# § 7. The mean point

**Four questions, 9 marks.** Every regression line passes through
$(\bar x,\bar y)$; two lines meet there.
""")

md(r"""
### 7.1 — *May 2021 TZ1 Paper 2 Q1(c), 1 mark*

For the data of 4.1, write down the value of $\bar x$ and the value of $\bar y$.
""")

code(r"""
q7_1 = ...       # (x-bar, y-bar)

verify_centre('7.1', q7_1, experiment)
""")

md(r"""
### 7.2 — *May 2024 TZ2 Paper 2 Q2(a), 1 mark*

The regression line of $y$ on $x$ for the data of 1.3 is $y=2.1875x+0.6875$,
and it passes through the mean point. Given that $\bar x=7$, verify that
$\bar y=16$: enter the value the line gives.
""")

code(r"""
q7_2 = ...       # y-bar

verify_estimate('7.2', q7_2, Eq(y, 2.1875*x + 0.6875), 7)
""")

md(r"""
### 7.3 — *May 2025 TZ1 Paper 2 Q4(b), 3 marks*

For the adults of 5.6, find the mean arm span and the mean foot length.

*The pair (mean arm span, mean foot length).*
""")

code(r"""
q7_3 = ...       # (mean A, mean F)

verify_centre('7.3', q7_3, [f_on_a, a_on_f], order=(A, F))
""")

md(r"""
### 7.4 — *May 2022 TZ1 Paper 1 Q2(b), 4 marks*

At the swimming pool of 2.2 the age of an adult is $a$ years and of their eldest
child $c$ years. The regression line of $a$ on $c$ is $a=\frac74c+20$; the
regression line of $c$ on $a$ is $c=\frac12a-9$.

**(i)** One of the adults surveyed is $42$ years old. Estimate the age of their
eldest child.

**(ii)** Find the mean age of all the adults surveyed.
""")

code(r"""
q7_4_i = ...     # the child's age
q7_4_ii = ...    # the mean age of the adults

a, c = symbols('a c')
a_on_c = Eq(a, Rational(7, 4)*c + 20)
c_on_a = Eq(c, a/2 - 9)

verify_estimate('7.4(i)', q7_4_i, [a_on_c, c_on_a], 42, of=c)
verify_centre('7.4(ii)', q7_4_ii, [a_on_c, c_on_a], of=a)
""")

# ================================================================ § 8
md(r"""
---
# § 8. What the data do not say

**Four questions, 4 marks.** Correlation is not cause; $r$ ignores shifts.
""")

md(r"""
### 8.1 — *November 2021 Paper 2 Q1(d), 1 mark*

Lucy asserts that the number of hours a student practises (3.2) has a direct
effect on their final diploma result. Comment on the validity of her assertion:

* `'a'` — valid: $r$ is close to $1$;
* `'b'` — not valid: the data can only show a correlation, not a cause;
* `'c'` — valid: the gradient of the line is positive;
* `'d'` — not valid: eight students are too few for any regression.
""")

code(r"""
q8_1 = ...       # 'a', 'b', 'c' or 'd'

check_word('8.1', q8_1, '""" + D_8_1 + r"""')
""")

md(r"""
### 8.2 — *November 2021 Paper 2 Q1(e), 1 mark*

Lucy deducts a fixed number of hours per week from each student's recorded
hours. State how, if at all, the value of $r$ would be affected:
`'no effect'`, `'increases'` or `'decreases'`.
""")

code(r"""
q8_2 = ...       # the effect on r

verify_effect('8.2', q8_2, piano, lambda hours: hours - 3, which='h')
""")

md(r"""
### 8.3 — *May 2022 TZ2 Paper 2 Q4(d), 1 mark*

After **not** sleeping well, the nine adults of 2.3 have the box and whisker
diagram $0.27,\ 0.29,\ 0.35,\ 0.39,\ 0.48$. Comment on whether the two diagrams
provide any evidence that might suggest that not sleeping well causes an
increase in reaction time:

* `'a'` — yes: the median after not sleeping well equals the upper quartile
  after sleeping well;
* `'b'` — no: correlation does not imply causation;
* `'c'` — yes: the mean reaction time is higher after not sleeping well;
* `'d'` — no: the two diagrams overlap.
""")

code(r"""
q8_3 = ...       # 'a', 'b', 'c' or 'd'

check_word('8.3', q8_3, '""" + D_8_3 + r"""')
""")

md(r"""
### 8.4 — *May 2025 TZ3 Paper 2 Q3(c), 1 mark*

A supermarket manager surveys the first 50 customers to arrive on a particular
day. Which one best describes the sampling method: simple random, systematic,
convenience, quota or stratified?
""")

code(r"""
q8_4 = ...       # the sampling method

check_word('8.4', q8_4, '""" + D_8_4 + r"""')
""")

# ================================================================== решения
md(r"""
---
---

# 🔑 Solutions

---

## § 1

**1.1 (a)** $\boxed{\text{a}}$: the median is the middle value, and as Aiden's
score is below $10.5$ and Brett's is above, the middle stays in the same place.

**1.1 (b)** $30\cdot10.6-28\cdot10.5=318-294=24$ for the two together; the new
range is Brett's minus Aiden's, $14$. So Aiden $\boxed{5}$, Brett
$\boxed{19}$.

**1.2 (a)** Ten values up to $4$, so $\Sigma f=20$: $x=\boxed{7}$.
**(b)** $\sigma=\boxed{1.58}$ $(1.58429\ldots)$.

**1.3** $\frac{9+13+p+q+21}{5}=16$ gives $p+q=37$; with $q-p=3$:
$p=\boxed{17}$, $q=\boxed{20}$.

**1.4 (a)** $\bar x=\frac{51.6}{8}=\boxed{6.45}$.
**(b)(i)** $\bar y=0.014375+2.1625\cdot6.45=13.9625\approx\boxed{14.0}$.
**(ii)** $8\cdot13.9625=111.7=93.2+p$, so $p=\boxed{18.5}$.

---

## § 2

**2.1 (a)** $75\le U+30$ gives $U\ge45$ (and the lower fence, $10\ge U-50$,
allows up to $60$): $U=\boxed{45}$. **(b)** $L=U-20=\boxed{25}$.

**2.2** $10+1.5\cdot(10-6)=\boxed{16}$.

**2.3 (a)** $\boxed{0.28}$ s. **(b)** $0.35+1.5\cdot0.08=\boxed{0.47}$ and
$0.46<0.47$: $\boxed{\text{not an outlier}}$. **(c)** The median is closer to
$Q_1$: $\boxed{\text{positively skewed}}$, so the mean is pulled above the
median.

---

## § 3

**3.1** $r=\boxed{0.978}$. **3.2** $r=\boxed{0.884}$. **3.3** $r=\boxed{0.981}$.
**3.4** $r=\boxed{0.901}$. **3.5** $r=\boxed{0.954}$ $(0.953958\ldots)$.

---

## § 4

**4.1 (a)** $a=\boxed{0.433}$, $b=\boxed{4.50}$. **(d)** Through
$\boxed{(15,\ 11)}$, the mean point, and meeting the $y$-axis near $4.50$.

**4.2** $a=\boxed{1.37}$, $b=\boxed{64.5}$. **4.3** $a=\boxed{1.01}$,
$b=\boxed{2.45}$. **4.4** $a=\boxed{1.93}$, $b=\boxed{7.22}$
$(1.93258\ldots,\ 7.21662\ldots)$. **4.5** $a=\boxed{1.98}$, $b=\boxed{40.2}$
$(1.97651\ldots,\ 40.2286\ldots)$.

---

## § 5

**5.1** $\boxed{12.3}$. **5.2 (b)** An increase of $\boxed{0.805}$ minutes of
waiting time per additional customer ahead. **(c)** $\boxed{8.52}$ minutes.

**5.3** $5\cdot1.36609\ldots=\boxed{6.83}$: about seven marks more.

**5.4** $81.39\ldots\approx\boxed{81}$. **5.5** $\boxed{45.9}$ cm
$(45.8683\ldots)$.

**5.6** Use $A$ on $F$: $2.89\cdot19.8+99.3=156.522\approx\boxed{157}$ cm.

**5.7** $\boxed{79.8}$ hours $(79.7589\ldots)$.

---

## § 6

**6.1 (b)** Predicting $x$ from $y$: the line of $x$ on $y$,
$\boxed{x=0.0935y+7.43}$. **(c)** $y(25)=310$ and
$0.0935114\ldots\cdot310+7.43053\ldots=36.4\ldots\approx\boxed{36}$.

**6.2 (b)** $10$ is outside the Test A data: $\boxed{\text{extrapolation}}$.
**(c)(i)** Predicting $x$ with the line of $y$ on $x$:
$\boxed{\text{the wrong line}}$. **(ii)** The line of $x$ on $y$ at $y=90$ gives
$85.62\ldots\approx\boxed{86}$.

---

## § 7

**7.1** $\boxed{(15,\ 11)}$. **7.2** $2.1875\cdot7+0.6875=\boxed{16}$.

**7.3** The lines meet at the mean point: $\bar A=\boxed{160}$ cm,
$\bar F=\boxed{20.9}$ cm.

**7.4 (i)** $c=\frac12\cdot42-9=\boxed{12}$. **(ii)** $a=\frac78a+\frac{17}4$,
so $\bar a=\boxed{34}$.

---

## § 8

**8.1** $\boxed{\text{b}}$. **8.2** $\boxed{\text{no effect}}$.
**8.3** $\boxed{\text{a}}$ — R0 for *correlation does not imply causation*, and a
comparison of means is not accepted. **8.4** $\boxed{\text{convenience}}$.
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
