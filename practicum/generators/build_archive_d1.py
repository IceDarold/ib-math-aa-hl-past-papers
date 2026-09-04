"""Собирает архивный ноутбук D1: вся комбинаторика подряд.

Двадцать восемь вопросов архива, 83 балла, семь разделов по приёмам
карточки statistics-combinatorics.yaml. Теории здесь нет: она в
практикуме, а это то, что открывают после него.

Проверки эталона не хранят. `verify_count` получает описание объектов —
как выглядит один и что значит «подходит» — и пересчитывает их перебором.
Описание это условие вопроса, переписанное на Python, а не метод его
решения. Там, где перебрать всё нельзя (15! — это 1,3·10¹²), перечисляются
только объекты, которых касается ограничение, и каждый отвечает за `each`
штук. `verify_count_law` — для ответа-выражения от n: оно проверяется
пересчётом при малых n. Ответ «найдите n» пишется множеством и уходит в
`verify_param_set`, который подставляет его обратно в условие.

Восьмой архивный ноутбук серии и первый, в котором нет ни одного вопроса
без ячейки: в комбинаторике ответ всегда число, и передать его всегда
есть чем.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/check_archive_d1.py подставляет его в собранный .ipynb
и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

NOTEBOOK = os.path.join(ROOT, 'practicum/statistics/archive-d1-combinatorics.ipynb')

ANSWERS = {
    # § 1 правило произведения
    'q1_1': '125',
    'q1_2': '216',
    'q1_3': '6480',
    # § 2 размещения
    'q2_1': '60',
    'q2_2': 'factorial(15)',
    'q2_3': '136080',
    'q2_4': '25200',
    # § 3 сочетания
    'q3_1': '84',
    'q3_2': 'binomial(n_, 3)',
    'q3_3': '126126',
    # § 4 блок
    'q4_1': '5040',
    'q4_2': '720',
    'q4_3': '362880',
    'q4_4': '30240',
    'q4_5': '645120',
    'q4_6': '12441600',
    'q4_7': '8',
    # § 5 дополнение
    'q5_1': '384',
    'q5_2': '20160',
    'q5_3': '518400',
    'q5_4': '75',
    # § 6 случаи
    'q6_1': '10080',
    'q6_2': '1360',
    'q6_3': '21',
    'q6_4': '4',
    'q6_5': '8',
    # § 7 буква внутри счёта
    'q7_1': '{9}',
    'q7_2': 'n_ - 2',
    'q7_3': '{11}',
    'q7_4': '{24}',
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
# D1 archive: combinatorics

**Every past-paper question in which the answer is a count, grouped by
technique.** Not a practicum — a drill. There is no theory here and no
ladder to climb: the theory is in *Practicum D1*, and this notebook is
what you open afterwards, when the only thing left is to do them all until
the decisions are automatic.

**What is inside.** The whole of `statistics.combinatorics`, sessions
May 2021 — November 2025: **28 questions, 83 marks**, in seven sections,
one section per technique.

The corpus counts the topic as 30 blocks and 89 marks. The difference is
the November 2023 zonal duplicate: one paper filed twice, as TZ1 and TZ2,
with the six boys and three girls counted both times. It appears here
once.

**How to work.** Read the question, answer in the cell below it, run the
cell. None of the checks knows the answer. `verify_count` is handed a
description of the objects — how one is built, and what makes it count —
and it enumerates them and adds up:

```python
verify_count('5.1', q5_1, permutations(PENS, 5),
             keep=lambda pen: not share_a_boundary(pen[AMBER], pen[BROWNIE]))
```

That is the sentence from the paper, in Python. The method — $6!-2\cdot7
\cdot4!$ — is nowhere in it, and it is the only thing you have to supply.

Where enumeration will not fit — $15!$ is $1.3\times10^{12}$ — only the
objects the restriction touches are listed, and each stands for a fixed
number of the rest. The multiplier is in the check, not in your answer.

**When you are wrong the check says how**, and every diagnosis is rebuilt
from the same enumeration: the restriction was ignored, the forbidden
cases were counted instead, an order inside $r$ objects was dropped or
counted twice.

Two answers are not counts. *Write down an expression* is checked by
re-enumerating at small $n$, so any correct form passes. *Determine the
value of $n$* is written as a set — `{9}` — and put back into the
condition; that is not pedantry, since the markscheme refuses the last
mark when a second value of $n$ is offered beside the right one.

**Nothing is stored.** Not one of the thirty answers is written down in
this notebook, as a number or as a hash. Every one is worked out from the
question each time you run the cell.

**Every question has a cell.** In seven earlier archive notebooks there
were questions with nothing to hand over — *state two key features*,
*explain why*. Here there are none: the answer to a counting question is
always a number. Three questions do print their answer in the paper
(*explain why there are 216*, *show that there are four*, *show that there
are eight*), and they keep their cells anyway, because in all three the
work is to arrive at the printed number and the cell says whether you did.

Leave a cell blank and it prints ⬜ and moves on, so you can run the whole
notebook top to bottom on the first open and nothing breaks. Two sections
enumerate several hundred thousand objects and take a second or two.

**The solutions are at the end**, numbered the same way. Open one after
you have worked the question, not before.

**The seven sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The product rule | 3 | 7 |
| 2 | Arrangements | 4 | 9 |
| 3 | Selections | 3 | 6 |
| 4 | The block: things that stay together | 6 | 15 |
| 5 | The complement: things that stay apart | 4 | 14 |
| 6 | Cases and the addition rule | 5 | 15 |
| 7 | A letter inside the count | 3 | 17 |
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + factorial, binomial, permutations, ...

language('en')                 # this notebook is in English, and so are the checks

n_ = symbols('n')

print('ready; sympy', sp.__version__)
print('a count:    ', factorial(15))
print('a binomial: ', binomial(9, 6))
print('a set:      ', {9})
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. The product rule

$$\text{choices}_1\times\text{choices}_2\times\cdots\times\text{choices}_k$$

The object is built in steps, the steps do not interfere, and the counts
multiply. Everything else in this notebook is this rule with something
taken away.
""")

md(r"""
### 1.1 — *November 2022 Paper 1 Q11(a)(i), 2 marks*

Consider a three-digit code $abc$, where each of $a$, $b$ and $c$ is
assigned one of the values $1$, $2$, $3$, $4$ or $5$.

Find the total number of possible codes assuming that each value can be
repeated (for example, $121$ or $444$).
""")

code(r"""
VALUES = (1, 2, 3, 4, 5)

q1_1 = ...

verify_count('1.1', q1_1, product(VALUES, repeat=3))
""")

md(r"""
### 1.2 — *May 2024 TZ2 Paper 3 Q2(a), 1 mark*

Quadratic functions $f(x)=ax^2+bx+c$ have their coefficients $a$, $b$ and
$c$ generated in turn by rolling an unbiased six-sided die three times and
reading off the value shown on the uppermost face.

Explain why there are $216$ possible quadratic functions that can be
generated using this method.

*The answer is printed, and the mark is for the sentence $6\times6\times6$,
not for the number. The cell only confirms you know which space you are in.*
""")

code(r"""
FACES = (1, 2, 3, 4, 5, 6)

q1_2 = ...

verify_count('1.2', q1_2, product(FACES, repeat=3))
""")

md(r"""
### 1.3 — *May 2021 TZ1 Paper 1 Q9(a), 4 marks*

A farmer has six sheep pens, arranged in a grid with three rows and two
columns. Five sheep called Amber, Brownie, Curly, Daisy and Eden are to be
placed in the pens. Amber and Brownie are known to fight.

Find the number of ways of placing the sheep in the pens if each pen is
large enough to contain five sheep, and Amber and Brownie must not be
placed in the same pen.
""")

code(r"""
AMBER, BROWNIE = 0, 1
PENS = range(6)                 # pen p sits in row p // 2, column p % 2

q1_3 = ...

verify_count('1.3', q1_3, product(PENS, repeat=5),
             keep=lambda pen: pen[AMBER] != pen[BROWNIE])
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. Arrangements

$$n!\qquad\text{and}\qquad {}^nP_r=\frac{n!}{(n-r)!}$$

Things are placed, each used once, and the order of the placing makes a
different object. The supply runs down as you go, and that is the whole
difference from section 1.

**Fill the restricted position first.** If one place cannot take one of
the objects, deal with it before anything else; leaving it until last is
the single most reliable way to lose the mark.
""")

md(r"""
### 2.1 — *November 2022 Paper 1 Q11(a)(ii), 2 marks*

For the same three-digit code $abc$ built from $1,2,3,4,5$: find the total
number of possible codes assuming that no value is repeated.
""")

code(r"""
q2_1 = ...

verify_count('2.1', q2_1, permutations(VALUES, 3))
""")

md(r"""
### 2.2 — *November 2025 TZ3 Paper 2 Q8(a), 1 mark*

Malik owns $15$ recipe books which he bought while travelling.

Find the number of different ways of arranging the books in a line on a
shelf.

*The markscheme accepts $15!$ as it stands. There is no reason to
evaluate it.*
""")

code(r"""
q2_2 = ...

# 15! arrangements will not fit; the first four places are enumerated and
# the remaining eleven books contribute a factor of 11!
verify_count('2.2', q2_2, permutations(range(15), 4), each=factorial(11))
""")

md(r"""
### 2.3 — *May 2022 TZ2 Paper 2 Q9(a), 2 marks*

Consider the set of six-digit positive integers that can be formed from
the digits $0,1,2,3,4,5,6,7,8$ and $9$.

Find the total number of six-digit positive integers that can be formed
such that the digits are distinct.
""")

code(r"""
q2_3 = ...

verify_count('2.3', q2_3, permutations(range(10), 6),
             keep=lambda digits: digits[0] != 0)
""")

md(r"""
### 2.4 — *November 2025 TZ1 Paper 2 Q2, 4 marks*

A particular service group at a school has ten members. The group intends
to select a committee of seven by first choosing a chairperson, a
vice-chairperson and a treasurer, then selecting four additional members
to complete the committee.

Determine the number of ways in which this committee can be chosen.
""")

code(r"""
MEMBERS = range(10)

# a committee: three named posts, then four ordinary members
def committees():
    for officers in permutations(MEMBERS, 3):
        rest = [m for m in MEMBERS if m not in officers]
        for others in combinations(rest, 4):
            yield officers, others

q2_4 = ...

verify_count('2.4', q2_4, committees())
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. Selections

$$^nC_r=\frac{^nP_r}{r!}$$

A group is chosen and its internal order produces nothing new, so the
arrangement count has over-counted by exactly $r!$. Divide it out.

The same division appears twice more: when the order inside a group is
**fixed by the question** (digits in increasing order), and when several
groups are **indistinguishable from one another** (three unnamed teams).
""")

md(r"""
### 3.1 — *May 2022 TZ2 Paper 2 Q9(b), 2 marks*

Find the total number of six-digit positive integers that can be formed
from $0,1,\dots,9$ such that the digits are distinct **and are in
increasing order**.
""")

code(r"""
q3_1 = ...

verify_count('3.1', q3_1, permutations(range(10), 6),
             keep=lambda digits: digits[0] != 0 and list(digits) == sorted(digits))
""")

md(r"""
### 3.2 — *May 2024 TZ2 Paper 1 Q9(a), 1 mark*

A teacher takes $n$ students on a field trip. The students are assigned
randomly into two groups: exactly three students in the first group and at
least three students in the second group. The teacher will randomly assign
three students to the first group and the other students to the second.

Write down an expression for the number of ways that the students could be
assigned.
""")

code(r"""
# how many ways to pick three out of size — and, if apart, so that the two
# named students land in different groups
def assignments(size, apart=False):
    groups = combinations(range(size), 3)
    if apart:
        groups = (g for g in groups if len({0, 1} & set(g)) == 1)
    return sum(1 for _ in groups)

q3_2 = ...

verify_count_law('3.2', q3_2, n_, assignments, sizes=(5, 6, 7, 8, 9))
""")

md(r"""
### 3.3 — *May 2025 TZ2 Paper 2 Q11(a), 3 marks*

A mathematics class of 15 students plays a game which requires three equal
size teams.

Find the total number of ways that the three teams can be chosen.
""")

code(r"""
CLASS = range(15)

# splits of the class into three fives; the teams have no names, so the
# same three fives written in another order are the same split
def team_splits():
    seen = set()
    for first in combinations(CLASS, 5):
        rest = [s for s in CLASS if s not in first]
        for second in combinations(rest, 5):
            third = tuple(s for s in rest if s not in second)
            split = frozenset((first, second, third))
            if split not in seen:
                seen.add(split)
                yield split

q3_3 = ...

verify_count('3.3', q3_3, team_splits())          # the enumeration takes a second or two
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. The block: things that stay together

Glue what must stand together into one object, arrange what is left, then
multiply by the orders **inside** the glue — and, if there is more than one
block, by the order of the blocks themselves.

$$\underbrace{(n-k+1)!}_{\text{the outside}}\times\underbrace{k!}_{\text{the inside}}$$

Two things get dropped here, every time: the inside order, and — when the
block does not fill the row — the number of positions the block can take.
""")

md(r"""
### 4.1 — *May 2021 TZ2 Paper 2 Q7(a), 2 marks*

Eight runners compete in a race where there are no tied finishes. Andrea
and Jack are two of the eight competitors.

Find the total number of possible ways in which the eight runners can
finish if Jack finishes in the position immediately after Andrea.
""")

code(r"""
ANDREA, JACK = 0, 1
RUNNERS = range(8)

q4_1 = ...

verify_count('4.1', q4_1, permutations(RUNNERS),
             keep=lambda order: order.index(JACK) == order.index(ANDREA) + 1)
""")

md(r"""
### 4.2 — *May 2022 TZ1 Paper 2 Q9(a), 3 marks*

Mary, three female friends, and her brother, Peter, attend the theatre. In
the theatre there is a row of 10 empty seats. For the first half of the
show, they decide to sit next to each other in this row.

Find the number of ways these five people can be seated in this row.
""")

code(r"""
PETER, GIRLS = 0, (1, 2, 3, 4)
SEATS = range(10)

q4_2 = ...

# seat[i] is the seat that person i takes
verify_count('4.2', q4_2, permutations(SEATS, 5),
             keep=lambda seat: max(seat) - min(seat) == 4)
""")

md(r"""
### 4.3 — *November 2023 TZ1 Paper 2 Q7(a), 3 marks*

A junior baseball team consists of six boys and three girls. The team
members are to be placed in a line to have their photograph taken.

In how many ways can the team members be placed if
**(i)** there are no restrictions;
**(ii)** the girls must be placed next to each other?
""")

code(r"""
TEAM = range(9)
GIRLS_IN_TEAM = {0, 1, 2}       # the six boys are 3..8

def girls_at(line):
    return [i for i, member in enumerate(line) if member in GIRLS_IN_TEAM]

q4_3 = ...
q4_4 = ...

verify_count('4.3 (i)', q4_3, permutations(TEAM))
verify_count('4.3 (ii)', q4_4, permutations(TEAM),
             keep=lambda line: max(girls_at(line)) - min(girls_at(line)) == 2)
""")

md(r"""
### 4.4 — *May 2024 TZ1 Paper 2 Q9(a), 3 marks*

A group of 10 children includes one pair of brothers, Alvin and Bobby, and
one pair of sisters, Catalina and Daniela. The children are to be seated at
10 desks arranged in two rows of five. Alvin and Bobby must be seated next
to each other **in the same row**.

Find the total number of ways the children can be seated.
""")

code(r"""
ALVIN, BOBBY, CATALINA, DANIELA = 0, 1, 2, 3
DESKS = range(10)               # 0-4 front row, 5-9 back row, left to right

# neighbouring desks in the same row
def side_by_side(one, other):
    return one // 5 == other // 5 and abs(one - other) == 1

q4_5 = ...

# the restriction touches only two of them; the other eight give a factor of 8!
verify_count('4.4', q4_5, permutations(DESKS, 2),
             keep=lambda desk: side_by_side(desk[ALVIN], desk[BOBBY]),
             each=factorial(8))
""")

md(r"""
### 4.5 — *November 2025 TZ3 Paper 2 Q8(b), 3 marks*

Malik's 15 books were bought in three continents: six from Asia, five from
Europe and four from Africa. Malik decides to arrange the books on the
shelf so that the books from each of the continents are grouped together.

Determine the number of different ways that Malik can do this.
""")

code(r"""
BOOKS = tuple('A' * 6 + 'E' * 5 + 'F' * 4)      # each book carries its continent

# the books of each continent stand on the shelf in one run
def in_one_run(shelf):
    line = ''.join(shelf)
    return all(c * line.count(c) in line for c in 'AEF')

q4_6 = ...

# the shelf pattern is enumerated — which continent stands where — and each
# pattern stands for 6!*5!*4! arrangements of the books themselves
verify_count('4.5', q4_6, multiset_permutations(list(BOOKS)), keep=in_one_run,
             each=factorial(6) * factorial(5) * factorial(4))
""")

md(r"""
### 4.6 — *May 2023 TZ1 Paper 2 Q11(e), 1 mark*

Ten independent laboratory trials were conducted, and exactly three of
them were successful.

Write down the number of ways these three successful trials could have
occurred consecutively.
""")

code(r"""
q4_7 = ...

verify_count('4.6', q4_7, combinations(range(10), 3),
             keep=lambda three: three[2] - three[0] == 2)
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. The complement: things that stay apart

$$\text{apart}=\text{everything}-\text{together}$$

*Apart* counted directly splits into cases and takes ten minutes; counted
as everything minus section 4 it takes two lines. The only two ways to go
wrong are subtracting from the wrong whole, and mis-counting which pairs
are actually adjacent.

Symmetry belongs here too: if the condition and its negation are in
bijection, the answer is exactly half of everything.
""")

md(r"""
### 5.1 — *May 2021 TZ1 Paper 1 Q9(b), 4 marks*

The six sheep pens are arranged in a grid with **three rows and two
columns**, and each pen may now only contain one sheep.

Find the number of ways of placing the five sheep in the pens such that
Amber and Brownie are not placed in pens which share a boundary.
""")

code(r"""
# pens sharing a side in the three-by-two grid
def share_a_boundary(one, other):
    return abs(one // 2 - other // 2) + abs(one % 2 - other % 2) == 1

q5_1 = ...

verify_count('5.1', q5_1, permutations(PENS, 5),
             keep=lambda pen: not share_a_boundary(pen[AMBER], pen[BROWNIE]))
""")

md(r"""
### 5.2 — *May 2021 TZ2 Paper 2 Q7(b), 3 marks*

Find the total number of possible ways in which the eight runners can
finish if Jack finishes in **any** position after Andrea.
""")

code(r"""
q5_2 = ...

verify_count('5.2', q5_2, permutations(RUNNERS),
             keep=lambda order: order.index(JACK) > order.index(ANDREA))
""")

md(r"""
### 5.3 — *May 2024 TZ1 Paper 2 Q9(b), 4 marks*

After an argument, Catalina and Daniela must not be seated next to each
other. Alvin and Bobby must still be seated next to each other.

Find the total number of ways the ten children can be seated.

*The whole you are subtracting from is the answer to 4.4, not $10!$.*
""")

code(r"""
q5_3 = ...

# the restriction touches four of them; the other six give a factor of 6!
verify_count('5.3', q5_3, permutations(DESKS, 4),
             keep=lambda desk: side_by_side(desk[ALVIN], desk[BOBBY])
                               and not side_by_side(desk[CATALINA], desk[DANIELA]),
             each=factorial(6))
""")

md(r"""
### 5.4 — *November 2023 TZ1 Paper 2 Q7(b), 3 marks*

Five members of the baseball team (six boys, three girls) are selected to
attend a summer camp.

Find the number of possible selections that contain at least two girls.
""")

code(r"""
q5_4 = ...

verify_count('5.4', q5_4, combinations(TEAM, 5),
             keep=lambda five: len(GIRLS_IN_TEAM & set(five)) >= 2)
""")

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. Cases and the addition rule

When the number of options for one object depends on where another object
went, no single expression covers the question. Split, count each part with
sections 1–5, and add.

Two checks, both worth saying out loud before you add: **the cases must not
overlap**, and **the cases must cover everything**. The term that gets
dropped is almost always the one that does not feel like a case.
""")

md(r"""
### 6.1 — *May 2022 TZ1 Paper 2 Q9(b), 4 marks*

For the second half of the show, the five return to the same row of 10
empty seats. The four girls decide to sit at least one seat apart from
Peter. The four girls do not have to sit next to each other.

Find the number of ways these five people can now be seated in this row.
""")

code(r"""
q6_1 = ...

verify_count('6.1', q6_1, permutations(SEATS, 5),
             keep=lambda seat: all(abs(seat[g] - seat[PETER]) > 1 for g in GIRLS))
""")

md(r"""
### 6.2 — *May 2023 TZ2 Paper 2 Q9, 5 marks*

Let $S$ be the set of 30 positive integers $\{1,2,3,\dots,28,29,30\}$.
Raghu randomly selects three positive integers from $S$ without
replacement, adds them together and determines whether the sum is divisible
by 3.

Determine the total number of selections Raghu can make to obtain a sum
that is divisible by 3. You may assume that order is not important.
""")

code(r"""
q6_2 = ...

verify_count('6.2', q6_2, combinations(range(1, 31), 3),
             keep=lambda three: sum(three) % 3 == 0)
""")

md(r"""
### 6.3 — *November 2025 TZ3 Paper 2 Q8(c), 3 marks*

Malik chooses four books, all from the same continent (six from Asia, five
from Europe, four from Africa).

Determine the number of different choices Malik could make.
""")

code(r"""
q6_3 = ...

verify_count('6.3', q6_3, combinations(BOOKS, 4),
             keep=lambda four: len(set(four)) == 1)
""")

md(r"""
### 6.4 — *May 2024 TZ2 Paper 3 Q2(e)(i), 1 mark*

The coefficients $a$, $b$, $c$ of $f(x)=ax^2+bx+c$ come from three rolls of
a die. For the case where $ac=1$, show that there are four quadratic
functions whose corresponding graphs have two distinct $x$-intercepts.
""")

code(r"""
q6_4 = ...

verify_count('6.4', q6_4, product(FACES, repeat=3),
             keep=lambda f: f[0] * f[2] == 1 and f[1] ** 2 > 4 * f[0] * f[2])
""")

md(r"""
### 6.5 — *May 2024 TZ2 Paper 3 Q2(e)(ii), 2 marks*

For the case where $ac=2$, show that there are eight quadratic functions
whose corresponding graphs have two distinct $x$-intercepts.
""")

code(r"""
q6_5 = ...

verify_count('6.5', q6_5, product(FACES, repeat=3),
             keep=lambda f: f[0] * f[2] == 2 and f[1] ** 2 > 4 * f[0] * f[2])
""")

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. A letter inside the count

Every technique above, with $n$ where a number used to be. Write the count
as an expression, set it equal to what the question gives, cancel the
factorials rather than expanding them, solve — and then throw away the
roots the **situation** forbids, not just the ones the algebra forbids.

Answers to *find $n$* are written as sets. The markscheme is explicit about
why: *"Do not award the final A1 if additional values of $n$ are given."*
""")

md(r"""
### 7.1 — *May 2024 TZ2 Paper 1 Q9(b), 6 marks*

Two of the $n$ students ask the teacher not to work in the same group. The
teacher agrees and now finds that the number of ways to assign the students
is halved.

Determine the value of $n$.
""")

code(r"""
# the condition of the part, read literally
def halved(size):
    if not sympify(size).is_integer or size < 4:
        return None                          # a number of students is a whole number
    size = int(size)
    return size - 3 >= 3 and 2 * assignments(size, apart=True) == assignments(size)

q7_1 = {...}

verify_param_set('7.1', q7_1, halved, var=n_, window=(4, 30))
""")

md(r"""
### 7.2 — *May 2023 TZ1 Paper 2 Q11(f), 6 marks*

Consider $n$ independent trials where it is given that exactly three
successes have occurred.

**(i)** Write down an expression for the number of ways these three
successful trials could have occurred consecutively.

**(ii)** Find the greatest value of $n$ such that the probability of three
consecutive successful trials is more than $0.05$.
""")

code(r"""
# how many triples of successes run consecutively among size trials
def in_a_row(size):
    return sum(1 for three in combinations(range(size), 3)
               if three[2] - three[0] == 2)

# the greatest n: the share still exceeds 0.05 at n and no longer does at n + 1
def greatest(size):
    if not sympify(size).is_integer or size < 3:
        return None
    over = lambda m: Rational(in_a_row(m), len(list(combinations(range(m), 3)))) \
                     > Rational(5, 100)
    return over(int(size)) and not over(int(size) + 1)

q7_2 = ...
q7_3 = {...}

verify_count_law('7.2 (i)', q7_2, n_, in_a_row, sizes=(4, 5, 6, 7, 8, 9))
verify_param_set('7.2 (ii)', q7_3, greatest, var=n_, window=(3, 40))
""")

md(r"""
### 7.3 — *May 2025 TZ3 Paper 2 Q8, 5 marks*

A class of students plays a tic-tac-toe competition among themselves. Each
individual game involves only two students. Every student in the class is to
play every other student **twice**. However, Stephen left the class after he
had played only seven games. All other games, not involving Stephen, were
played. By the end of the competition a total of $513$ games had been played.

Determine the number of students that were originally in the class.
""")

code(r"""
# whether a class of size students played exactly 513 games
def games(size):
    if not sympify(size).is_integer or size < 3:
        return None
    size = int(size)
    everyone = sum(2 for _ in combinations(range(size), 2))   # everyone plays everyone twice
    missed = 2 * (size - 1) - 7                               # Stephen's games that were not played
    return everyone - missed == 513

q7_4 = {...}

verify_param_set('7.3', q7_4, games, var=n_, window=(3, 40))
""")

# ------------------------------------------------------------------ решения
md(r"""
---
# 🔑 Solutions

---

## 1. The product rule

**1.1** Three independent choices from five values:
$5\times5\times5=\boxed{125}$.

**1.2** The three rolls are independent and each shows one of six faces:
$6\times6\times6=\boxed{216}$. The answer is given in the question, so the
mark is entirely for writing the product — the markscheme labels it AG.

**1.3** Each pen holds all five sheep, so every sheep chooses freely,
except that Brownie must avoid Amber's pen:

$$\underbrace{6}_{\text{Amber}}\times\underbrace{5}_{\text{Brownie}}
\times\underbrace{6^3}_{\text{Curly, Daisy, Eden}}=5\times6^4=\boxed{6480}$$

Or, by the complement, $6^5-6^4=7776-1296=6480$: everything, minus the
placements in which the two are together.

---

## 2. Arrangements

**2.1** The supply runs down: $5\times4\times3={}^5P_3=\boxed{60}$. The only
difference from 1.1 is one sentence in the question.

**2.2** Fifteen distinct books in a line: $\boxed{15!}=1.31\times10^{12}$.

**2.3** The leading digit cannot be 0, so fill it first — 9 choices — and
then arrange five of the nine remaining digits (0 is available again) in
the other five places:

$$9\times{}^9P_5=9\times15120=\boxed{136080}$$

The markscheme names both standard wrong answers: $^{10}P_6=151200$
ignores the restriction, and $^9P_6=60480$ applies it to the whole number
instead of to the first digit. Both score M1A0.

**2.4** Three named posts are an arrangement; four ordinary members are a
selection:

$$^{10}P_3\times{}^7C_4=720\times35=\boxed{25200}$$

$^{10}C_3\times3!\times{}^7C_4$ is the same thing. $^{10}C_3\times{}^7C_4
=4200$ is not: it has forgotten that a chairperson is not a treasurer.

---

## 3. Selections

**3.1** An increasing six-digit number cannot contain 0 — it would have to
come first, and it cannot. Choose six digits from $\{1,\dots,9\}$; each
choice can be written in increasing order in exactly one way:

$$^9C_6\times1=\boxed{84}$$

The markscheme pays a whole mark for that *"exactly one way"*. It is also
$^9C_3$ — choosing the three digits to leave out.

**3.2** Three students out of $n$, order irrelevant; the rest are the second
group: $\boxed{^nC_3}$.

**3.3** Picking team A, then team B, then team C counts every actual split
$3!$ times, once per order in which its teams could have appeared:

$$\frac{^{15}C_5\times{}^{10}C_5\times{}^5C_5}{3!}
=\frac{3003\times252\times1}{6}=\boxed{126126}$$

The markscheme's second method never over-counts, so it never divides: fix
a student, choose their four teammates from the other fourteen; take
whoever is now lowest and choose theirs from the nine left; the last four
are forced. $^{14}C_4\times{}^9C_4\times{}^4C_4=1001\times126\times1
=126126$.

---

## 4. The block

**4.1** *Immediately after* glues Andrea and Jack into one object with
**one** allowed inside order. Seven objects remain:

$$7!=\boxed{5040}$$

Multiplying by $2!$ is the standard slip. The block is multiplied by the
orders the question permits, not by the orders that exist.

**4.2** The five sit as a block somewhere in a row of ten seats. The block
covers five consecutive seats, so it can start at seat 1 through seat 6 —
six positions — and the five people arrange inside it in $5!$ ways:

$$6\times5!=\boxed{720}$$

Here $6\times5!$ happens to equal $6!$, and the markscheme resignedly adds
*"accept 6!"*. It is a coincidence of this row length; in a row of eleven
seats the two numbers separate.

**4.3 (i)** $9!=\boxed{362880}$.

**4.3 (ii)** The three girls become one object, so seven objects are
arranged, and the girls have $3!$ orders inside:

$$7!\times3!=5040\times6=\boxed{30240}$$

The markscheme gives M1 for *"an attempt to consider girls as a single
object"* and A1 for the product. The $3!$ is the half people lose.

**4.4** *Next to each other in the same row.* Each row of five desks has
four adjacent pairs, so eight pairs of desks in all, and Alvin and Bobby
can sit in either order:

$$16\times8!=16\times40320=\boxed{645120}$$

The markscheme's second route: treat the ten desks as a single line, which
has nine adjacent pairs, then remove the one that straddles the rows —
$2\times9!-2\times8!=725760-80640=645120$.

**4.5** Three blocks, each with its own inside order, and the blocks
themselves in any order:

$$6!\times5!\times4!\times3!=720\times120\times24\times6=\boxed{12441600}$$

The last $3!$ has its own M1 in the markscheme: *"recognise that the three
groups can be placed in any order."* Asia–Europe–Africa is one shelf;
Africa–Asia–Europe is another.

**4.6** A run of three consecutive trials out of ten can start at trial 1
through trial 8: $\boxed{8}$.

---

## 5. The complement

**5.1** One sheep per pen gives $^6P_5=6!=720$ placements in all. In a grid
of three rows and two columns the pens sharing a boundary are three
horizontal pairs and four vertical ones — **seven**, and you have to look
at the picture to see it. For each pair, Amber and Brownie go two ways
round and the other three sheep fill three of the four remaining pens:

$$720-2\times7\times4!=720-336=\boxed{384}$$

The markscheme's second route splits by where Amber goes: a corner pen has
two neighbours (4 corners, 3 pens free for Brownie), a middle pen has three
(2 middles, 2 free), giving $(4\times3+2\times2)\times4!=16\times24=384$.

**5.2** Every finishing order has a mirror image with Andrea and Jack
swapped, and exactly one of the two has Jack later:

$$\frac{8!}{2}=\boxed{20160}$$

Counting positions instead — $(7+6+5+4+3+2+1)\times6!=28\times720$ — gives
the same number and takes seven times as long.

**5.3** Alvin and Bobby are still glued, so the whole is 4.4, not $10!$.
Count the seatings in which Catalina and Daniela are **also** adjacent,
split by where Alvin and Bobby sit:

- at the end of a row — 8 ways; three desks are left in that row giving 2
  adjacent pairs, plus 4 in the other row, so $8\times(6\times2)\times6!
  =69120$;
- not at the end — also 8 ways; now only 1 adjacent pair is left in their
  row, plus 4, so $8\times(5\times2)\times6!=57600$.

$$645120-(69120+57600)=\boxed{518400}$$

**5.4** At least two girls out of three, in a selection of five from nine:

$$^6C_3\times{}^3C_2+{}^6C_2\times{}^3C_3=60+15=\boxed{75}$$

or from the other end,
$^9C_5-{}^3C_1\times{}^6C_4-{}^6C_5=126-45-6=75$. Both are in the
markscheme. What is not accepted is half of one route plus half of the
other.

---

## 6. Cases

**6.1** Peter's neighbours must be empty, and how many neighbours he has
depends on where he sits:

- at either end — 2 seats. One neighbouring seat is barred, so the four
  girls take four of the remaining 8 seats in order: $2\times{}^8P_4=3360$.
- not at an end — 8 seats. Two are barred, leaving 7: $8\times{}^7P_4=6720$.

$$3360+6720=\boxed{10080}$$

The two cases do not overlap and together cover all ten seats.

**6.2** Every integer leaves remainder 0, 1 or 2 on division by 3, and
$\{1,\dots,30\}$ splits into three classes of exactly ten. Three numbers
have a sum divisible by 3 exactly when their remainders are all equal or
all different:

$$3\times{}^{10}C_3+10^3=360+1000=\boxed{1360}$$

The complement is also in the markscheme: $^{30}C_3=4060$ selections in
all, of which $^{10}C_2\times{}^{10}C_1\times3!=2700$ have a sum that is
not divisible by 3.

**6.3** Three cases, one per continent, and they cannot overlap:

$$^6C_4+{}^5C_4+{}^4C_4=15+5+1=\boxed{21}$$

The $^4C_4=1$ is the term that vanishes. There *is* exactly one way to take
all four African books, and the markscheme gives M1 for knowing there are
three cases.

**6.4** Two distinct intercepts means $b^2>4ac$. With $ac=1$ the only pair
is $(a,c)=(1,1)$, and $b^2>4$ leaves $b\in\{3,4,5,6\}$:

$$1\times4=\boxed{4}$$

**6.5** With $ac=2$ the pairs are $(1,2)$ and $(2,1)$, and $b^2>8$ again
leaves $b\in\{3,4,5,6\}$:

$$2\times4=\boxed{8}$$

The markscheme accepts the eight triples written out as a list. There is
nothing here for a calculator to do.

---

## 7. A letter inside the count

**7.1** With the two students separated, choose which of them joins the
first group ($^2C_1=2$) and then two more from the other $n-2$:

$$^2C_1\times{}^{n-2}C_2=(n-2)(n-3)$$

This is half of $^nC_3$:

$$\frac12\cdot\frac{n(n-1)(n-2)}{6}=(n-2)(n-3)$$

Cancel $(n-2)$ — legitimate, since $n\ge6$ — and clear the fraction:

$$n(n-1)=12(n-3)\Longrightarrow n^2-13n+36=0\Longrightarrow (n-9)(n-4)=0$$

$n=4$ satisfies the equation and not the question: it leaves one student in
the second group, and the trip needs at least three. So $n=\boxed{\{9\}}$.

**7.2 (i)** Three consecutive trials among $n$ can start at trial 1 through
trial $n-2$: $\boxed{n-2}$.

**7.2 (ii)** Given exactly three successes, all $^nC_3$ patterns are equally
likely, so

$$\frac{n-2}{^nC_3}=\frac{6(n-2)}{n(n-1)(n-2)}=\frac{6}{n(n-1)}>0.05$$
$$n(n-1)<120\Longrightarrow n\le11$$

$n=11$ gives $\tfrac{6}{110}=0.0545\ldots$ and $n=12$ gives
$\tfrac{6}{132}=0.0454\ldots$, so $n=\boxed{\{11\}}$. The markscheme accepts
that table of two values as the whole solution: checking both sides of the
boundary *is* solving the inequality.

**7.3** Everyone plays everyone twice, so a class of $n$ plays
$2\times{}^nC_2=n(n-1)$ games. Stephen should have played $2(n-1)$ and
played 7, so $2(n-1)-7$ games are missing:

$$n(n-1)-\bigl(2(n-1)-7\bigr)=513\Longrightarrow n^2-3n-504=0
\Longrightarrow (n-24)(n+21)=0$$

$-21$ is not a number of students, so $n=\boxed{\{24\}}$. Check:
$24\times23=552$ and $2\times23-7=39$, and $552-39=513$.

The markscheme's other route counts the $N$ students who are not Stephen:
they play $N(N-1)$ games among themselves, so $N(N-1)+7=513$, $N=23$, and
the class held 24.
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
