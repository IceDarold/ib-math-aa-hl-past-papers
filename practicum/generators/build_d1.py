"""Собирает практикум D1: комбинаторика — размещения, блоки, дополнение.

Девятый практикум серии на английском и второй по статистике. Лестница из семи
приёмов делится на три части: приёмы 1–3 — вся арифметика темы, и каждый
следующий получается из предыдущего делением на порядок; приёмы 4 и 5 —
два способа обойтись с ограничением, положительным и отрицательным;
приёмы 6 и 7 надстраиваются над первыми пятью.

Проверок здесь две новых, и обе живут в kit вместе с практикумом.

`verify_count` эталона не хранит и не может: ответ — целое число, и она
получает не его, а описание того, что считают, — как выглядит объект и
что значит «подходит». Дальше она перебирает и складывает единицы.
Описание это условие вопроса, переписанное на Python, а не метод его
решения: «все способы разложить пятерых овец по шести загонам, где Амбер
и Брауни в разных» — это условие; 6·5·6³ — это метод, и его в вызове нет.

Там, где перебор физически не влезает — 15! это 1,3·10¹², — перечисляются
не все объекты, а те, кого касается ограничение, и каждый отвечает за
`each` штук. У десятерых детей за десятью партами ограничение касается
четверых: перебираются 5040 способов посадить их, остальные шестеро дают
множитель 6!.

`verify_count_law` — для ответа-выражения от n: «write down an expression
for the number of ways». Сверять такое с записанным ⁿC₃ значило бы сверять
запись, поэтому проверка берёт маленькие n, пересчитывает объекты
перебором и смотрит, то же ли число даёт выражение.

Ответ «найдите n» проверяется тем, что уже есть: verify_param_set берёт
множество и спрашивает у самого условия, выполняется ли оно ровно там.
Ответ поэтому пишется множеством — {9}, а не 9, — и это не формальность:
схема оценивания мая 2024 TZ2 не даёт последний балл, если рядом с
девяткой написана и четвёрка.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_d1.py прогоняет по нему весь ноутбук и требует,
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

NOTEBOOK = os.path.join(ROOT, 'practicum/statistics/practicum-d1-combinatorics.ipynb')

TRIGGER = {1: 'product', 2: 'perm', 3: 'comb', 4: 'block', 5: 'minus',
           6: 'cases', 7: 'letter', 8: 'block', 9: 'minus', 10: 'comb',
           11: 'cases', 12: 'perm'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': '125',
    'q1b': '60',
    'q2a': '136080',
    'q2b': '84',
    'q3': '25200',
    'q4a': 'factorial(15)',
    'q4b': '12441600',
    'q4c': '21',
    'q5a': '5040',
    'q5b': '20160',
    'q6a': '720',
    'q6b': '10080',
    'q7a': '6480',
    'q7b': '384',
    'q8a': '362880',
    'q8b': '30240',
    'q8c': '75',
    'q9a': '645120',
    'q9b': '518400',
    'q10': '1360',
    'q11': '126126',
    'q12a': 'binomial(n_, 3)',
    'q12b': '{9}',
    'qt': '{24}',
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
# D1 — Combinatorics: arrangements, blocks, complements

**83 marks of the archive, seven techniques, twelve tasks.** The smallest
topic in the statistics section and the second smallest anywhere in the
archive. Fifteen questions in five years, none longer than seven marks,
and not one session without one.

## The one idea

Every question in this topic asks the same thing: **how many objects of a
certain kind are there?** All the machinery — $n!$, $^nP_r$, $^nC_r$ — is
three answers to one prior question, and the prior question is the whole
topic:

> *If I build one of these objects, what choices do I make, and does the
> order of those choices produce a different object?*

Answer that and the formula follows. Skip it and no formula helps, because
$^{10}P_3$ and $^{10}C_3$ are both perfectly good numbers and only one of
them counts what the question is asking about.

That is why the ladder below is not a list of formulas. It is a list of
**decisions**, and each rung is the previous one with one more decision
made.

## How the checks work

They do not know the answers. `verify_count` is handed a description of
the objects — how one is built, and what makes it count — and it
enumerates them and adds up. The description is the *question* rewritten
in Python, not the *method*:

```python
verify_count('7a', q7a, product(PENS, repeat=5),
             keep=lambda pen: pen[AMBER] != pen[BROWNIE])
```

is *"all the ways of putting five sheep in six pens, keeping the ones
where Amber and Brownie are apart"*. It is the sentence from the paper.
The method — $6\times5\times6^3$, or $6^5-6^4$ — appears nowhere in it,
and that is the part you are here to supply.

When you are wrong the check says **how**, and every diagnosis is built
out of the same enumeration:

| what you wrote | what the check says |
|---|---|
| the unrestricted count | the restriction is missing |
| the count of the bad cases | that is what the question forbids |
| the answer $\div\,r!$ | an order inside $r$ objects has been dropped |
| the answer $\times\,r!$ | an order the question does not ask for has been counted |
| half or twice the answer | the order inside the pair |
| a fraction | a number of things is a whole number |

Two questions have answers that are not counts. *Write down an expression
for the number of ways* is checked by `verify_count_law`, which
re-enumerates at small $n$ and compares — so $^nC_3$, $\frac{n!}{3!(n-3)!}$
and $\frac{n(n-1)(n-2)}{6}$ all pass. *Determine the value of $n$* is
answered as a **set**, `{9}`, and checked by putting it back into the
condition. Writing it as a set is not pedantry: the markscheme refuses the
last mark if a second value of $n$ is written down beside the right one.

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | count the choices; decide whether order matters | 1–3 |
| 🟡 | there is a restriction: glue it, or subtract it | 4–7 |
| 🔴 | one count is not enough | 8–12 |

Every task is a real past-paper question, cited. The full archive of the
topic — all twenty-eight questions — is in the companion notebook
*D1 archive: combinatorics*.

**77% of these marks carry a calculator, and the button really does the
arithmetic:** $^nP_r$, $^nC_r$ and $n!$ are keys, and 126 126 does not
come out in your head. But they are the *last* thing you press. About 28
of the 83 marks are the final A1 of a question; the other 55 are for
deciding what to count, and no calculator has an opinion about that.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + factorial, binomial, permutations, ...

language('en')                 # this notebook is in English, and so are the checks

n_ = symbols('n')

print('ready; sympy', sp.__version__)
print('a count:       ', factorial(15))
print('a binomial:    ', binomial(9, 6))
print('a set:         ', {9})
print('an enumeration:', len(list(permutations(range(5), 3))))
""")

md(r"""
---
## Map of the seven techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the product rule | the object is built in steps, and nothing runs out | multiply the choices |
| 2 | arrangements | things are placed, each used once | $n!$ or $^nP_r$ |
| 3 | selections | a group is picked and its inside order is nothing | $^nP_r$ divided by $r!$ |
| 4 | the block | *next to each other*, *grouped together* | glue, arrange, multiply by the inside |
| 5 | the complement | *not next to each other*, *at least* | all of them, minus technique 4 |
| 6 | cases | the answer depends on *where* | techniques 1–5, added |
| 7 | a letter in the count | $n$ is asked for, not given | techniques 1–6, then an equation |

The first three are one decision made twice. Start with the product rule:
$6\times6\times6$. Now say the objects cannot repeat, and it becomes
$6\times5\times4$ — an arrangement. Now say their order does not matter
either, and divide by $3!$ — a selection. Nothing new has been introduced;
each rung has taken one more thing away.

Techniques 4 and 5 are the same restriction seen from the two sides.
*Together* is a gluing; *apart* is everything minus the gluing. That is why
5 needs 4 and not the other way round.

Techniques 6 and 7 build on all of the above: 6 adds counts that do not
overlap, 7 sets one equal to a number and solves for $n$.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Three counts

## Theory: one decision, made twice

Build one object. You make a sequence of choices. If the choices are
independent, the counts multiply — that is the whole of the **product
rule**, and it is the only genuinely primitive idea in the topic:

$$\text{a three-digit code from five symbols} = 5\times5\times5=125$$

Now add a condition: **no symbol is used twice**. The second choice has
lost one option and the third has lost two:

$$5\times4\times3=60=\frac{5!}{2!}={}^5P_3$$

That is an **arrangement**. $^nP_r$ is not a new idea; it is the product
rule with the supply running down.

Now add a second condition: **the order of the chosen symbols does not
matter**. Every group of three has been counted once for each of its $3!$
orderings, so:

$$^5C_3=\frac{^5P_3}{3!}=\frac{60}{6}=10$$

A **selection**. Again nothing new — a division by an over-count.

> Three formulas, one idea, two decisions:
> *can things repeat?* and *does their order make a different object?*
> Answer those two and you have already chosen the formula.

### The decision is not always announced

Sometimes the paper says *order is not important*. More often it does not,
and the giveaway is subtler. May 2022 TZ2 asks for six-digit numbers whose
digits are **in increasing order**. Order matters enormously to the number
— 134679 and 971643 are different numbers — but you do not get to choose
it: each set of six digits produces exactly **one** increasing number. So
the count is a selection, $^9C_6$, and the markscheme gives a whole mark
for saying why:

> *"every unordered subset of 6 digits from the set of 9 non-zero digits
> can be arranged in exactly one way into a 6-digit number with the digits
> in increasing order."*

### Restricted positions go first

If one position is special, fill it first. A six-digit number cannot start
with 0, so:

$$\underbrace{9}_{\text{not }0}\times\underbrace{^9P_5}_{\text{the rest, from the nine left}}=9\times15120=136080$$

The markscheme for that question names two wrong answers explicitly, and
both come from filling the special position last:

> *"Award M1A0 for $10\times9\times8\times7\times6\times5={}^{10}P_6=151200$"*
> and *"Award M1A0 for $^9P_6=60480$."*

The first forgot the restriction; the second applied it to the wrong pool.
""")

md(r"""
### Task 1 🟢 — *November 2022 Paper 1 Q11(a), 4 marks*

Consider a three-digit code $abc$, where each of $a$, $b$ and $c$ is
assigned one of the values $1$, $2$, $3$, $4$ or $5$.

Find the total number of possible codes

**(a)** assuming that each value can be repeated (for example, $121$ or $444$);
**(b)** assuming that no value is repeated.
""")

code(r"""
VALUES = (1, 2, 3, 4, 5)

q1a = ...
q1b = ...

verify_count('1a', q1a, product(VALUES, repeat=3))
verify_count('1b', q1b, permutations(VALUES, 3))
""")

md(r"""
### Task 2 🟢 — *May 2022 TZ2 Paper 2 Q9, 4 marks*

Consider the set of six-digit positive integers that can be formed from
the digits $0,1,2,3,4,5,6,7,8$ and $9$.

Find the total number of six-digit positive integers that can be formed
such that

**(a)** the digits are distinct;
**(b)** the digits are distinct and are in increasing order.

*Both parts count the same objects. Only the second sentence differs, and
it is worth thinking about what it actually removes.*
""")

code(r"""
# a six-digit number with distinct digits is six different digits in places
q2a = ...
q2b = ...

verify_count('2a', q2a, permutations(range(10), 6),
             keep=lambda digits: digits[0] != 0)
verify_count('2b', q2b, permutations(range(10), 6),
             keep=lambda digits: digits[0] != 0 and list(digits) == sorted(digits))
""")

md(r"""
### Task 3 🟢 — *November 2025 TZ1 Paper 2 Q2, 4 marks*

A particular service group at a school has ten members.

The group intends to select a committee of seven by first choosing a
chairperson, a vice-chairperson and a treasurer, then selecting four
additional members to complete the committee.

Determine the number of ways in which this committee can be chosen.

*One question, both decisions, in that order. The three officers are
distinguishable from one another; the four extra members are not.*
""")

code(r"""
MEMBERS = range(10)

# a committee: three named posts, then four ordinary members
def committees():
    for officers in permutations(MEMBERS, 3):
        rest = [m for m in MEMBERS if m not in officers]
        for others in combinations(rest, 4):
            yield officers, others

q3 = ...

verify_count('3', q3, committees())
""")

# ================================================================= теория 2
md(r"""
---
# 🟡 Part 2. One restriction

## Theory: glue it, or subtract it

Almost every restriction in this topic is one of two sentences:

- **together** — *next to each other*, *immediately after*, *grouped*;
- **apart** — *not next to each other*, *must not share*, *at least one
  seat away*.

They are not two techniques. They are one technique and its complement.

### Together: glue and count the inside

Treat the things that must stand together as **one object**, arrange what
you now have, and multiply by the orders **inside** the glued object.

Nine people in a line with three of them together:

$$\underbrace{7!}_{\text{six others }+\text{ the block}}\times\underbrace{3!}_{\text{inside the block}}=5040\times6=30240$$

The $3!$ is the mark people lose. The markscheme for November 2023 awards
M1 for *"an attempt to consider girls as a single object"* and A1 for
$7!\times3!$ — the second mark is entirely the inside.

**Two glued objects means two insides and one outside.** Fifteen books,
grouped by three continents:

$$\underbrace{6!\times5!\times4!}_{\text{inside each continent}}\times\underbrace{3!}_{\text{the order of the continents}}=12\,441\,600$$

and the markscheme gives that last $3!$ its own M1: *"recognise that the
three groups can be placed in any order."*

**When the block does not fill the row, count its positions.** Five people
sitting together somewhere in a row of ten seats: the block can start at
seat 1 through seat 6, so

$$6\times5!=720$$

Six positions, not $6!$ objects — although here, by coincidence,
$6\times5!$ *is* $6!$, and the markscheme resignedly writes *"accept 6!"*.
A right answer can arrive for the wrong reason; on a different row length
it would not.

### Apart: count everything, then remove the together

The direct count of *apart* splits into cases and takes ten minutes. The
complement takes two lines:

$$\text{apart}=\text{all}-\text{together}$$

and you already know how to count *together*. Amber and Brownie in a
$3\times2$ grid of pens, one sheep each, not sharing a boundary:

$$6!-\underbrace{2\times7\times4!}_{\text{7 adjacent pairs, 2 orders, 4! for the rest}}=720-336=384$$

The 7 is worth pausing on. In a grid of three rows and two columns there
are three horizontal adjacent pairs and four vertical ones. Not eight, not
six — you have to look at the picture.

> **Which whole are you subtracting from?** May 2024 TZ1 asks for
> arrangements with Alvin and Bobby adjacent, then asks again with
> Catalina and Daniela *also* forbidden from being adjacent. The second
> answer is not $10!$ minus something. Alvin and Bobby are still glued, so
> the whole is the answer to part (a).

### Symmetry is the complement in disguise

*Jack finishes somewhere after Andrea.* Every finishing order has a mirror
image in which they are swapped, and exactly one of the two has Jack
later. So the answer is half of everything:

$$\frac{8!}{2}=20160$$

No cases, no gluing. It works whenever the condition and its negation are
in bijection — and it is worth spotting, because the case-by-case route is
$(7+6+5+4+3+2+1)\times6!$ and takes seven times as long.
""")

md(r"""
### Task 4 🟡 — *November 2025 TZ3 Paper 2 Q8, 7 marks*

Malik owns $15$ recipe books which he bought while travelling.

**(a)** Find the number of different ways of arranging the books in a line
on a shelf.

Malik's books were bought in three continents. Six books are from Asia,
five from Europe and four from Africa. Malik decides to arrange the books
on the shelf so that the books from each of the continents are grouped
together.

**(b)** Determine the number of different ways that Malik can do this.

Malik chooses four books, all from the same continent.

**(c)** Determine the number of different choices Malik could make.
""")

code(r"""
BOOKS = tuple('A' * 6 + 'E' * 5 + 'F' * 4)      # each book carries its continent

# the books of each continent stand on the shelf in one run
def in_one_run(shelf):
    line = ''.join(shelf)
    return all(c * line.count(c) in line for c in 'AEF')

q4a = ...
q4b = ...
q4c = ...

# 15! arrangements will not fit; the first four places are enumerated and
# the remaining eleven books contribute a factor of 11!
verify_count('4a', q4a, permutations(range(15), 4), each=factorial(11))
# here the shelf pattern is enumerated — which continent stands where —
# and each pattern stands for 6!*5!*4! arrangements of the books themselves
verify_count('4b', q4b, multiset_permutations(list(BOOKS)), keep=in_one_run,
             each=factorial(6) * factorial(5) * factorial(4))
verify_count('4c', q4c, combinations(BOOKS, 4),
             keep=lambda four: len(set(four)) == 1)
""")

md(r"""
### Task 5 🟡 — *May 2021 TZ2 Paper 2 Q7, 5 marks*

Eight runners compete in a race where there are no tied finishes. Andrea
and Jack are two of the eight competitors in this race.

Find the total number of possible ways in which the eight runners can
finish if Jack finishes

**(a)** in the position immediately after Andrea;
**(b)** in any position after Andrea.

*Part (a) is a block with one inside order, not two. Part (b) is not a
block at all.*
""")

code(r"""
ANDREA, JACK = 0, 1
RUNNERS = range(8)

q5a = ...
q5b = ...

verify_count('5a', q5a, permutations(RUNNERS),
             keep=lambda order: order.index(JACK) == order.index(ANDREA) + 1)
verify_count('5b', q5b, permutations(RUNNERS),
             keep=lambda order: order.index(JACK) > order.index(ANDREA))
""")

md(r"""
### Task 6 🟡 — *May 2022 TZ1 Paper 2 Q9, 7 marks*

Mary, three female friends, and her brother, Peter, attend the theatre. In
the theatre there is a row of 10 empty seats. For the first half of the
show, they decide to sit next to each other in this row.

**(a)** Find the number of ways these five people can be seated in this row.

For the second half of the show, they return to the same row of 10 empty
seats. The four girls decide to sit at least one seat apart from Peter.
The four girls do not have to sit next to each other.

**(b)** Find the number of ways these five people can now be seated in
this row.
""")

code(r"""
PETER, GIRLS = 0, (1, 2, 3, 4)
SEATS = range(10)

q6a = ...
q6b = ...

# seat[i] is the seat that person i takes
verify_count('6a', q6a, permutations(SEATS, 5),
             keep=lambda seat: max(seat) - min(seat) == 4)
verify_count('6b', q6b, permutations(SEATS, 5),
             keep=lambda seat: all(abs(seat[g] - seat[PETER]) > 1 for g in GIRLS))
""")

md(r"""
### Task 7 🟡 — *May 2021 TZ1 Paper 1 Q9, 8 marks*

A farmer has six sheep pens, arranged in a grid with **three rows and two
columns**. Five sheep called Amber, Brownie, Curly, Daisy and Eden are to
be placed in the pens. Amber and Brownie are known to fight.

Find the number of ways of placing the sheep in the pens in each of the
following cases:

**(a)** Each pen is large enough to contain five sheep. Amber and Brownie
must not be placed in the same pen.
**(b)** Each pen may only contain one sheep. Amber and Brownie must not be
placed in pens which share a boundary.

*Paper 1, so no calculator, and none is needed. Part (a) is the product
rule with one thing forbidden; part (b) is the complement, and its whole
difficulty is counting the boundaries.*
""")

code(r"""
AMBER, BROWNIE = 0, 1
PENS = range(6)                 # pen p sits in row p // 2, column p % 2

# pens sharing a side in the three-by-two grid
def share_a_boundary(one, other):
    return abs(one // 2 - other // 2) + abs(one % 2 - other % 2) == 1

q7a = ...
q7b = ...

# (a) a pen holds every sheep: each sheep picks a pen, and pens do not fill up
verify_count('7a', q7a, product(PENS, repeat=5),
             keep=lambda pen: pen[AMBER] != pen[BROWNIE])
# (b) one sheep to a pen
verify_count('7b', q7b, permutations(PENS, 5),
             keep=lambda pen: not share_a_boundary(pen[AMBER], pen[BROWNIE]))
""")

# ================================================================= теория 3
md(r"""
---
# 🔴 Part 3. When one count is not enough

## Theory: split, add, and solve

### Cases

Sometimes no single expression covers the question, because the number of
options for one object depends on **where another object went**. May 2022
TZ1 is the cleanest example: Peter must have an empty seat on each side of
him, so

- Peter at either end (2 seats): one neighbour to protect, four girls from
  the eight remaining seats, $2\times{}^8P_4=3360$;
- Peter not at an end (8 seats): two neighbours, $8\times{}^7P_4=6720$.

$$3360+6720=10080$$

Two rules govern every case split, and both are worth checking out loud:

**They must not overlap.** Ask: can one object land in two cases at once?
If it can, you have counted it twice.

**They must cover everything.** Four books from one continent is
$^6C_4+{}^5C_4+{}^4C_4=15+5+1=21$ — and the last term is easy to drop,
because there is only one way to take all four African books and it does
not feel like a case. The markscheme gives a separate M1 just for
*"recognition that the sum of 3 different cases is required."*

The split does not have to be by position. May 2023 TZ2 asks for triples
from $\{1,\dots,30\}$ whose sum is divisible by 3. Sort the thirty numbers
by remainder — ten leave 0, ten leave 1, ten leave 2 — and a triple works
exactly when the three remainders are all equal or all different:

$$3\times{}^{10}C_3+\left({}^{10}C_1\right)^3=360+1000=1360$$

### Identical groups: divide by their order

Fifteen students into three teams of five. Choosing team A, then team B,
then team C gives

$$^{15}C_5\times{}^{10}C_5\times{}^{5}C_5=3003\times252\times1=756\,756$$

but the teams have no names. Each actual split has been counted once for
every order in which its three teams could have been picked — $3!$ of them:

$$\frac{756756}{3!}=126\,126$$

There is a way to avoid the division entirely, and the markscheme accepts
it: put a fixed student in a team, choose their four teammates
($^{14}C_4$), take whoever is now lowest-numbered and choose theirs
($^9C_4$), and the last four are forced:

$$^{14}C_4\times{}^9C_4\times{}^4C_4=1001\times126\times1=126\,126$$

No over-count happens, so no division is needed. The two methods disagree
about nothing except how much you have to remember.

### A letter in the count

The last rung is every rung before it, with $n$ where a number used to be.
Three things go wrong here and all three are worth naming.

**Cancel, do not expand.** $\tfrac12{}^nC_3={}^2C_1\times{}^{n-2}C_2$
becomes $n(n-1)=12(n-3)$ after the factorials cancel, and
$n^2-13n+36=0$ after that. Expanding $n!$ gets you nowhere. The markscheme
awards M1 for *"a valid attempt to eliminate all factorials."*

**Throw away the root the question forbids.** $n^2-13n+36=0$ has roots
9 and 4. At $n=4$ the second group holds one student, and the question
says it must hold at least three. The markscheme is blunt: *"Do not award
the final A1 if additional values of $n$ are given."* The rejection is a
mark, not a tidy-up — which is why the answer here is written as the set
$\{9\}$.

**Round an inequality towards the condition, not towards the arithmetic.**
$\frac{6}{n(n-1)}>0.05$ gives $n<11.47$, so the greatest integer is 11.
The markscheme also accepts the table: $n=11$ gives $0.0545\ldots$ and
$n=12$ gives $0.0454\ldots$ — checking both sides of the boundary *is* the
solution, and it earns the same marks.
""")

md(r"""
### Task 8 🔴 — *November 2023 TZ1 Paper 2 Q7, 6 marks*

A junior baseball team consists of six boys and three girls. The team
members are to be placed in a line to have their photograph taken.

**(a)** In how many ways can the team members be placed if
&nbsp;&nbsp;**(i)** there are no restrictions;
&nbsp;&nbsp;**(ii)** the girls must be placed next to each other?

**(b)** Five members of the team are selected to attend a baseball summer
camp. Find the number of possible selections that contain at least two
girls.

*Part (b) has two honest routes and one dishonest one. Add the two cases
that qualify, or subtract the two that do not, from everything. Mixing the
halves of the two routes gives a number that is not 75.*
""")

code(r"""
TEAM = range(9)
GIRLS = {0, 1, 2}               # the six boys are 3..8

def girls_in(line):
    return [i for i, member in enumerate(line) if member in GIRLS]

q8a = ...
q8b = ...
q8c = ...

verify_count('8a', q8a, permutations(TEAM))
verify_count('8b', q8b, permutations(TEAM),
             keep=lambda line: max(girls_in(line)) - min(girls_in(line)) == 2)
verify_count('8c', q8c, combinations(TEAM, 5),
             keep=lambda five: len(GIRLS & set(five)) >= 2)
""")

md(r"""
### Task 9 🔴 — *May 2024 TZ1 Paper 2 Q9, 7 marks*

A group of 10 children includes one pair of brothers, Alvin and Bobby, and
one pair of sisters, Catalina and Daniela. The children are to be seated
at 10 desks arranged in **two rows of five**.

Alvin and Bobby must be seated next to each other **in the same row**.

**(a)** Find the total number of ways the children can be seated.

After an argument, Catalina and Daniela must not be seated next to each
other. Alvin and Bobby must still be seated next to each other.

**(b)** Find the total number of ways the children can be seated.

*"In the same row" is the whole question. Desks 5 and 6 are next to each
other on the page and not next to each other in the problem.*
""")

code(r"""
ALVIN, BOBBY, CATALINA, DANIELA = 0, 1, 2, 3
DESKS = range(10)               # 0-4 front row, 5-9 back row, left to right

# neighbouring desks in the same row
def side_by_side(one, other):
    return one // 5 == other // 5 and abs(one - other) == 1

q9a = ...
q9b = ...

# the restriction touches only the named children; the rest give a factor
verify_count('9a', q9a, permutations(DESKS, 2),
             keep=lambda desk: side_by_side(desk[ALVIN], desk[BOBBY]),
             each=factorial(8))
verify_count('9b', q9b, permutations(DESKS, 4),
             keep=lambda desk: side_by_side(desk[ALVIN], desk[BOBBY])
                               and not side_by_side(desk[CATALINA], desk[DANIELA]),
             each=factorial(6))
""")

md(r"""
### Task 10 🔴 — *May 2023 TZ2 Paper 2 Q9, 5 marks*

Let $S$ be the set of 30 positive integers $\{1,2,3,\dots,28,29,30\}$.

Raghu randomly selects three positive integers from $S$ without
replacement. He then adds them together and determines whether the sum is
divisible by 3.

Determine the total number of selections Raghu can make to obtain a sum
that is divisible by 3.

You may assume that order is not important, for example,
$\{1,2,3\},\{1,3,2\},\{2,3,1\},\{2,1,3\},\{3,1,2\},\{3,2,1\}$ are all
considered to be the same selection.

*Thirty numbers, but only three kinds of number. Sorting them by remainder
turns this into a small question.*
""")

code(r"""
q10 = ...

verify_count('10', q10, combinations(range(1, 31), 3),
             keep=lambda three: sum(three) % 3 == 0)
""")

md(r"""
### Task 11 🔴 — *May 2025 TZ2 Paper 2 Q11(a), 3 marks*

A mathematics class of 15 students plays a game which requires three equal
size teams.

Find the total number of ways that the three teams can be chosen.

*The teams have no names. Whatever you compute first, ask whether the same
three teams could have been produced twice.*
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

q11 = ...

verify_count('11', q11, team_splits())          # the enumeration takes a second or two
""")

md(r"""
### Task 12 🔴 — *May 2024 TZ2 Paper 1 Q9, 7 marks*

A teacher takes $n$ students on a field trip. The students are assigned
randomly into two groups. For safety reasons there must be exactly three
students in the first group and at least three students in the second
group. The teacher will randomly assign three students to the first group
and the other students to the second group.

**(a)** Write down an expression for the number of ways that the students
could be assigned.

Two of the students ask the teacher not to work in the same group. The
teacher agrees and now finds that the number of ways to assign the
students is halved.

**(b)** Determine the value of $n$.

*Part (b) is answered as a set, `{9}`. Both roots of the quadratic satisfy
the equation; only one of them satisfies the question.*
""")

code(r"""
# how many ways to pick three out of size — and, if apart, so that the two
# named students land in different groups
def assignments(size, apart=False):
    groups = combinations(range(size), 3)
    if apart:
        groups = (g for g in groups if len({0, 1} & set(g)) == 1)
    return sum(1 for _ in groups)

# the condition of part (b), read literally
def halved(size):
    if not sympify(size).is_integer or size < 4:
        return None                          # a number of students is a whole number
    size = int(size)
    return size - 3 >= 3 and 2 * assignments(size, apart=True) == assignments(size)

q12a = ...
q12b = {...}

verify_count_law('12a', q12a, n_, assignments, sizes=(5, 6, 7, 8, 9))
verify_param_set('12b', q12b, halved, var=n_, window=(4, 30))
""")

# ================================================================= тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would
make first**. On the paper that decision takes about five seconds, and
everything else follows from it.

| code | technique |
| --- | --- |
| `product` | steps multiply; nothing runs out |
| `perm` | things are placed, each used once |
| `comb` | a group is chosen and its inside order is nothing |
| `block` | something must stay together: glue it |
| `minus` | something must stay apart: count all, subtract the together |
| `cases` | it depends on where; split and add |
| `letter` | $n$ is what is asked for |

1. A three-digit code is made from the values 1 to 5, each of which may be repeated. How many codes are there?
2. Six-digit numbers are made from distinct digits and cannot start with 0. How many are there?
3. Three integers are chosen from thirty; order is not important. How many selections are there altogether?
4. Fifteen books are shelved so that the books from each continent stand together. How many arrangements?
5. Alvin and Bobby sit next to each other; Catalina and Daniela must not. How many seatings?
6. Three integers are chosen from thirty. How many of those selections have a sum divisible by 3?
7. The number of ways is halved when two students are separated. Find the number of students.
8. Jack finishes in the position immediately after Andrea. How many finishing orders?
9. Amber and Brownie must not be placed in pens which share a boundary. How many placements?
10. Fifteen students form three equal teams with no names. How many ways?
11. Four books are chosen, all from the same continent. How many choices?
12. A chairperson, a vice-chairperson and a treasurer are chosen from ten members. How many ways?
""")

code("""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + """)
""")

# ================================================================= таймер
md(r"""
---
## On the clock — *May 2025 TZ3 Paper 2 Q8, 5 marks*

**Five marks, seven minutes.** No hints this time.

A class of students plays a tic-tac-toe competition among themselves. Each
individual game in the competition involves only two students.

Every student in the class is to play every other student **twice**.
However, Stephen left the class after he had played only seven games. All
other games, not involving Stephen, were played.

By the end of the competition a total of $513$ games had been played.

Determine the number of students that were originally in the class.

*Answer as a set, as in task 12.*
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

qt = {...}

verify_param_set('timer', qt, games, var=n_, window=(3, 40))
""")

# ================================================================= решения
md(r"""
---
# 🔑 Solutions

---

**1 (a)** Three independent choices out of five: $5\times5\times5
=\boxed{125}$.

**1 (b)** The supply runs down: $5\times4\times3={}^5P_3=\boxed{60}$.

The two parts are printed side by side in the paper for a reason. The only
difference between them is one sentence, and it changes $5^3$ into
$\frac{5!}{2!}$.

---

**2 (a)** Fill the restricted position first. The leading digit has 9
choices (anything but 0); the other five positions take five of the nine
digits that are left, in order:

$$9\times{}^9P_5=9\times15120=\boxed{136080}$$

$^{10}P_6=151200$ ignores the restriction; $^9P_6=60480$ applies it and
then forgets that 0 is available for the later positions. Both are named
in the markscheme, and both score M1A0.

**2 (b)** An increasing six-digit number cannot contain 0 — it would have
to come first, and it cannot. So choose six digits from $\{1,\dots,9\}$;
each choice can be written in increasing order in exactly one way:

$$^9C_6\times1=\boxed{84}$$

Equivalently $^9C_3$: choosing which three digits to leave out.

---

**3** The three officers are distinguishable, so their selection is an
arrangement; the four extra members are not, so theirs is a selection:

$$^{10}P_3\times{}^7C_4=720\times35=\boxed{25200}$$

$^{10}C_3\times3!$ is the same number written the other way round, and the
markscheme accepts it. What it does not accept is $^{10}C_3\times{}^7C_4$
— that is 4200, and it has thrown away the fact that a chairperson is not
a treasurer.

---

**4 (a)** Fifteen distinct books in a line: $\boxed{15!}=1.31\times10^{12}$.

The markscheme accepts either form. There is no reason to evaluate it.

**4 (b)** Three blocks. Arrange inside each, then arrange the blocks:

$$6!\times5!\times4!\times3!=720\times120\times24\times6=\boxed{12441600}$$

The final $3!$ is the mark most often lost. Asia, Europe, Africa is one
shelf; Africa, Asia, Europe is another.

**4 (c)** Three cases, one per continent, and they cannot overlap:

$$^6C_4+{}^5C_4+{}^4C_4=15+5+1=\boxed{21}$$

The $^4C_4=1$ is the term that disappears. There *is* one way to take all
four African books, and it is worth a mark.

---

**5 (a)** *Immediately after* glues Andrea and Jack into one object with
**one** possible inside order — Andrea first. So there are seven objects:

$$7!=\boxed{5040}$$

Multiplying by $2!$ here is the standard slip, and it doubles the answer.
The block technique multiplies by the number of orders *the question
allows*, which is not always the number of orders that exist.

**5 (b)** For every finishing order, swapping Andrea and Jack gives another
one, and exactly one of the pair has Jack later. So it is half of
everything:

$$\frac{8!}{2}=\frac{40320}{2}=\boxed{20160}$$

The markscheme's second method counts positions:
$(7+6+5+4+3+2+1)\times6!=28\times720=20160$. Same answer, seven times the
work.

---

**6 (a)** The five sit as a block somewhere in a row of ten. The block
occupies five consecutive seats, so it can start at seat 1, 2, 3, 4, 5 or
6 — six positions — and the five people can be arranged inside it in $5!$
ways:

$$6\times5!=6\times120=\boxed{720}$$

The markscheme adds *"accept $6!$"*, because $6\times5!$ happens to equal
$6!$. It does not mean the block is a sixth object; try the same question
in a row of eleven seats and the two numbers separate.

**6 (b)** Peter's neighbours must be empty, and how many neighbours he has
depends on where he sits:

- Peter at either end — 2 choices. One seat next to him is barred, leaving
  8 seats for the four girls, in order: $2\times{}^8P_4=2\times1680=3360$.
- Peter not at an end — 8 choices. Two seats are barred, leaving 7:
  $8\times{}^7P_4=8\times840=6720$.

$$3360+6720=\boxed{10080}$$

The cases do not overlap (Peter is either at an end or not) and they cover
everything (there is no third possibility). Both facts are worth stating
before you add.

---

**7 (a)** Every pen holds all five sheep, so each sheep chooses a pen
freely — except that Brownie cannot repeat Amber's:

$$\underbrace{6}_{\text{Amber}}\times\underbrace{5}_{\text{Brownie}}
\times\underbrace{6^3}_{\text{Curly, Daisy, Eden}}=5\times6^4=\boxed{6480}$$

Or through the complement: $6^5-6^4=7776-1296=6480$. Both are in the
markscheme, and the second is a preview of part (b).

**7 (b)** One sheep per pen, so this is $^6P_5=6!=720$ placements in all.
Now count the forbidden ones. In a grid of three rows and two columns the
pens that share a boundary are:

$$\underbrace{3}_{\text{horizontal pairs}}+\underbrace{4}_{\text{vertical pairs}}=7$$

For each of the 7 pairs, Amber and Brownie can go two ways round, and the
other three sheep fill three of the four remaining pens in $4!$ ordered
ways:

$$720-2\times7\times4!=720-336=\boxed{384}$$

The markscheme's second method is the case split: Amber in a corner pen
(4 of them, 3 pens then free for Brownie) or in a middle pen (2 of them,
2 free), giving $4\times3\times4!+2\times2\times4!=(12+4)\times24=384$.
Corner pens have two neighbours, middle pens have three — which is the same
observation as the 7, seen from the other side.

---

**8 (a)(i)** Nine people, no restrictions: $9!=\boxed{362880}$.

**8 (a)(ii)** The three girls become one object, so seven objects are
arranged, and the girls have $3!$ orders inside:

$$7!\times3!=5040\times6=\boxed{30240}$$

**8 (b)** *At least two girls* out of three, in a selection of five from
nine. Two routes:

$$\underbrace{^6C_3\times{}^3C_2}_{\text{exactly 2 girls}}
+\underbrace{^6C_2\times{}^3C_3}_{\text{exactly 3 girls}}=60+15=\boxed{75}$$

or, from the other end,

$$\underbrace{^9C_5}_{\text{all}}-\underbrace{^3C_1\times{}^6C_4}_{\text{one girl}}
-\underbrace{^6C_5}_{\text{no girls}}=126-45-6=75$$

Both are in the markscheme. The number of girls is at most three, so
"at least two" is only two cases — which is why adding is as short as
subtracting here. With six girls it would not be.

---

**9 (a)** *Next to each other in the same row.* Each row of five desks has
four adjacent pairs, so there are $2\times4=8$ pairs of desks, and Alvin
and Bobby can sit in either order:

$$\underbrace{8\times2}_{=16}\times\underbrace{8!}_{\text{the other eight children}}
=16\times40320=\boxed{645120}$$

The markscheme's second method is worth seeing: treat the ten desks as one
line of ten, which has nine adjacent pairs, then remove the pair that
straddles the two rows — $2\times9!-2\times8!=725760-80640=645120$.

**9 (b)** Alvin and Bobby stay glued, so the whole to subtract from is
part (a), not $10!$. Count the arrangements where Catalina and Daniela are
*also* adjacent, splitting on where Alvin and Bobby sit:

- Alvin and Bobby at the end of a row — 8 ways ($2$ rows $\times2$ ends
  $\times2$ orders). Three desks are left in that row, giving 2 adjacent
  pairs, plus 4 in the other row: 6 pairs, 2 orders, so
  $8\times12\times6!=69120$.
- Alvin and Bobby not at an end — also 8 ways. Now the leftover desks in
  their row give only 1 adjacent pair, plus 4: 5 pairs, 2 orders, so
  $8\times10\times6!=57600$.

$$645120-(69120+57600)=\boxed{518400}$$

---

**10** Every integer leaves remainder 0, 1 or 2 on division by 3, and
$\{1,\dots,30\}$ splits into three groups of exactly ten. The sum of three
numbers is divisible by 3 exactly when their remainders are all the same
or all different:

$$\underbrace{3\times{}^{10}C_3}_{\text{all from one class}}
+\underbrace{10\times10\times10}_{\text{one from each}}=360+1000=\boxed{1360}$$

The complement works too and the markscheme gives it: $^{30}C_3=4060$
in all, and the selections whose sum is *not* divisible by 3 come to 2700.

---

**11** Choosing the teams one after another counts each split $3!$ times:

$$\frac{^{15}C_5\times{}^{10}C_5\times{}^5C_5}{3!}
=\frac{3003\times252\times1}{6}=\frac{756756}{6}=\boxed{126126}$$

Equivalently $\dfrac{15!}{5!\,5!\,5!\,3!}$.

The markscheme's second method avoids the division: fix one student, choose
their four teammates from the other fourteen, then fix any student not yet
placed and choose theirs from the nine left:

$$^{14}C_4\times{}^9C_4\times{}^4C_4=1001\times126\times1=126126$$

Nobody is over-counted, so nobody has to be divided out. Both are three
marks; the second is harder to get wrong.

---

**12 (a)** Three students out of $n$, order irrelevant, and the rest are
the second group: $\boxed{^nC_3}$.

**12 (b)** With the two students separated: choose which of them goes into
the first group ($^2C_1=2$), then two more from the other $n-2$:

$$^2C_1\times{}^{n-2}C_2=2\times\frac{(n-2)(n-3)}{2}=(n-2)(n-3)$$

This is half of part (a):

$$\frac12\cdot\frac{n(n-1)(n-2)}{6}=(n-2)(n-3)$$

Cancel $(n-2)$ — legitimate, since $n\ge6$ — and multiply by 12:

$$n(n-1)=12(n-3) \Longrightarrow n^2-13n+36=0
\Longrightarrow (n-9)(n-4)=0$$

$n=4$ satisfies the equation. It does not satisfy the question: with four
students the second group would hold one, and the trip requires at least
three. So $n=\boxed{\{9\}}$.

The markscheme does not spell the rejection out; it just writes *"Do not
award the final A1 if additional values of $n$ are given."* One of the six
marks is for noticing that the algebra offered you something the situation
cannot use.

---

## Timer

Everyone plays everyone twice, so a class of $n$ plays
$2\times{}^nC_2=n(n-1)$ games. Stephen should have played $2(n-1)$ and
played 7, so $2(n-1)-7$ games are missing:

$$n(n-1)-\bigl(2(n-1)-7\bigr)=513$$
$$n^2-n-2n+2+7=513 \Longrightarrow n^2-3n-504=0
\Longrightarrow (n-24)(n+21)=0$$

$n=-21$ is not a number of students, so $n=\boxed{\{24\}}$.

Check: $24\times23=552$ games if nobody had left, and $2\times23-7=39$ of
them were not played. $552-39=513$.

The markscheme's other route counts the $N=n-1$ students who are not
Stephen: they play $N(N-1)$ games among themselves, plus Stephen's 7,
giving $N(N-1)+7=513$, $N=23$, and one more for Stephen.
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
