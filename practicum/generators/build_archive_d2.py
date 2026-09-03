"""Собирает архивный ноутбук D2: вся вероятность подряд.

Пятьдесят вопросов архива, 156 баллов, десять разделов по приёмам
карточки statistics-probability.yaml. Теории здесь нет: она в практикуме,
а это то, что открывают после него.

Проверки эталона не хранят. `verify_event` восстанавливает вероятностное
пространство из условий самого вопроса — «P(A) = 0,65», «P(A|B) = 1/4»,
«A и B независимы» — решая их как уравнения на веса атомов диаграммы
Венна, и вычисляет то, о чём спрашивают, по определению. `verify_probability`
получает пространство выписанным (дерево, вынимание без возвращения,
216 равновозможных троек) и складывает веса нужных исходов, а первым
делом проверяет, что все веса вместе дают единицу: неверно переписанное
дерево ловится именно здесь.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/check_archive_d2.py подставляет его в собранный .ipynb
и требует, чтобы каждая проверка сказала ✅.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))

import sympy as sp

R = sp.Rational

NOTEBOOK = os.path.join(ROOT, 'practicum/statistics/archive-d2-probability.ipynb')

ANSWERS = {
    # § 1 алгебра событий
    'q1_1': 'Rational(4, 5)',
    'q1_2': 'Rational(1, 5)',
    'q1_3': 'Rational(2, 25)',
    'q1_4': 'Rational(3, 25)',
    'q1_5': 'Rational(1, 3)',
    'q1_6': 'Rational(6, 25)',
    'q1_7': 'Rational(1, 10)',
    'q1_8': 'Rational(3, 10)',
    # § 2 условная вероятность
    'q2_1': 'Rational(1, 12)',
    'q2_2': 'Rational(5, 8)',
    'q2_3': 'Rational(1, 6)',
    'q2_4': 'Rational(1, 5)',
    'q2_5': 'Rational(3, 5)',
    'q2_6': 'Rational(9, 16)',
    'q2_7': 'Rational(3, 25)',
    # § 3 независимость
    'q3_1': '[Rational(1, 6), Rational(1, 6)]',
    'q3_2': '[Rational(12, 125), Rational(3, 25)]',
    'q3_3': '[Rational(9, 28), Rational(5, 14)]',
    'q3_4': 'Rational(6, 25)',
    'q3_5': 'Rational(1, 5)',
    # § 4 дерево
    'q4_1': ('[95*p_/100, 5*p_/100, 2*(1 - p_)/100, 98*(1 - p_)/100]'),
    'q4_2': 'Rational(9, 14)',
    'q4_3': '0.0443430',
    'q4_4': '[k_**2/2, k_*(1 - k_/2), (1 - k_)*k_/2, (1 - k_)*(1 - k_/2)]',
    # § 5 повторные испытания
    'q5_1': '0.0268435',
    'q5_2': 'Rational(81, 1000)',
    'q5_3': '0.468559',
    'q5_4': '0.288',
    'q5_6': '[0.32, 0.1536]',
    'q5_7': 'Rational(3, 20)',
    # § 6 полная вероятность
    'q6_1': '0.226969',
    'q6_2': '0.081',
    'q6_3': '0.134172',
    # § 7 Байес
    'q7_1': '0.965183',
    'q7_2': 'Rational(1, 6)',
    'q7_3': '0.543209',
    'q7_4': '0.721870',
    'q7_5': '0.804590',
    # § 8 без возвращения
    'q8_1': 'Eq(3*y_*(y_ - 1), (r_ + y_)*(r_ + y_ - 1))',
    'q8_2': 'y_*(y_ - 1)*(y_ - 2)/((y_ + 10)*(y_ + 9)*(y_ + 8))',
    'q8_3': '4',
    # § 9 перебор равновозможных
    'q9_1': 'Rational(5, 216)',
    'q9_2': 'Rational(19, 108)',
    'q9_3': 'Rational(3, 10)',
    'q9_4': '5',
    'q9_5': '[3, 5]',
    # § 10 буква внутри вероятности
    'q10_1': '[Rational(1, 3)]',
    'q10_2': '[0.133739]',
    'q10_3': '[Rational(59, 8)]',
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
# D2 archive: probability

**Every past-paper question in which the answer comes out of the structure
of a probability space, grouped by technique.** Not a practicum — a drill.
There is no theory here and no ladder to climb: the theory is in
*Practicum D2*, and this notebook is what you open afterwards, when the only
thing left is to do them all until the moves are automatic.

**What is inside.** The part of `statistics.probability` that is about
events, conditioning, independence and trees, sessions May 2021 —
November 2025: **50 questions, 156 marks**, in ten sections, one section
per technique.

The whole topic is 77 blocks and 237 marks. The 81 marks left over are
mostly not this topic at all: 36 are the binomial distribution (D3), 11 a
probability generating function (D4), 7 the normal distribution (D5), 11 a
density (D6), and 4 are the November 2023 zonal duplicate counted twice.
The last 12 are descriptive statistics — a box plot, a mean, a sampling
method — and they belong to no practicum in the map at all.

**How to work.** Read the question, answer in the cell below it, run the
cell. None of the checks here knows the answer. A question about
probability fixes a **space**, and the space fixes the answer:
`verify_event` takes the conditions the question states — $P(A)=0.65$,
$P(A\mid B)=\tfrac14$, *A and B are independent* — solves them as equations
on the weights of the four cells of the Venn diagram, and computes what
was asked from the definition. `verify_probability` is handed the space
written out — a tree, a sequence of draws without replacement, 216 equally
likely triples — and adds the weights of the outcomes you want; before
anything else it checks that the weights sum to one, which is where a
mis-copied tree gets caught.

When your answer is wrong they do more than say so. The slips in this
topic have names, and each one is rebuilt from the same space: the
conditional taken the wrong way round, the union added without subtracting
the intersection, independence assumed where the question never promised
it, the intersection handed in before it was divided by anything.

**Nothing is stored.** Not one of the fifty answers is written down in this
notebook, as a number or as a hash. Every one of them is worked out from
the question every time you run the cell.

**One question has no cell** — *explain why $Y \le 5$* — because there is
nothing to hand over. Read it, do it on paper, read the solution.

Leave a cell blank and it prints ⬜ and moves on, so you can run the whole
notebook top to bottom on the first open and nothing breaks.

**The solutions are at the end**, numbered the same way. Open one after you
have worked the question, not before.

**The ten sections.**

| § | technique | questions | marks |
|---|---|---|---|
| 1 | The algebra of events | 8 | 17 |
| 2 | Conditional probability | 7 | 22 |
| 3 | Independence as an equation | 5 | 17 |
| 4 | Trees | 4 | 10 |
| 5 | Repeated trials and the first success | 7 | 17 |
| 6 | The law of total probability | 3 | 11 |
| 7 | Bayes: back up the tree | 5 | 20 |
| 8 | Without replacement | 3 | 12 |
| 9 | Counting an equally likely space | 5 | 18 |
| 10 | A letter inside the probability | 3 | 12 |

Sections 1–3 live on a Venn diagram: two events, four cells, and every
question is arithmetic once the cells are filled. Sections 4, 5, 8 and 9
build the space first — that is where the real work of this topic is.
Sections 6 and 7 are one machine run in two directions: down the tree and
back up it. Section 10 puts a letter in the space and asks you to find it,
and it is the only place in the topic where an answer is thrown away for
being bigger than one.

**62% of the marks carry a calculator, and here that is nearly honest.**
Genuine GDC work comes to about 30 marks out of 156 — the normal and
binomial probabilities that sit on the branches of the trees in §6 and §7.
The other 126 are done on paper.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, Eq, events, P(...)

language('en')                 # this notebook is in English, and so are the checks

a_, b_, k_, p_, r_, y_, z_ = symbols('a b k p r y z')

print('ready; sympy', sp.__version__)
print('a probability: ', Rational(9, 14))
print('two numbers:   ', [Rational(1, 6), Rational(1, 6)])
print('an event:      ', events('A B'))
""")

# ------------------------------------------------------------------ § 1
md(r"""
---
## 1. The algebra of events

$$P(A\cup B)=P(A)+P(B)-P(A\cap B), \qquad
P(A'\cap B')=1-P(A\cup B)$$

Two events cut the sample space into four cells: $A\cap B$, $A\cap B'$,
$A'\cap B$, $A'\cap B'$. Their probabilities add to one, and every question
in this section is arithmetic once you know all four. Draw the diagram
before you write anything — it is faster than the formula and it does not
let you forget the fourth cell.
""")

md(r"""
### 1.1 — *November 2023 TZ1 Paper 1 Q2(a), 2 marks*

Events $A$ and $B$ are such that $P(A)=0.65$, $P(B)=0.75$ and
$P(A\cap B)=0.6$.

Find $P(A\cup B)$.
""")

code(r"""
A, B = events('A B')
here = [(P(A), 0.65), (P(B), 0.75), (P(A & B), 0.6)]

q1_1 = ...

verify_event('1.1', q1_1, here, P(A | B))
""")

md(r"""
### 1.2 — *November 2023 TZ1 Paper 1 Q2(b), 2 marks*

Hence, or otherwise, find $P(A'\cap B')$.
""")

code(r"""
q1_2 = ...

verify_event('1.2', q1_2, here, P(~A & ~B))
""")

md(r"""
### 1.3 — *May 2021 TZ2 Paper 2 Q3(a), 2 marks*

At a school, 70% of the students play a sport and 20% of the students are
involved in theatre. 18% of the students do neither activity.

A student is selected at random. Find the probability that the student
plays a sport and is involved in theatre.
""")

code(r"""
S, T = events('S T')
school = [(P(S), Rational(7, 10)), (P(T), Rational(2, 10)),
          (P(~S & ~T), Rational(18, 100))]

q1_3 = ...

verify_event('1.3', q1_3, school, P(S & T))
""")

md(r"""
### 1.4 — *May 2021 TZ2 Paper 2 Q3(b), 2 marks*

Find the probability that the student is involved in theatre, but does not
play a sport.
""")

code(r"""
q1_4 = ...

verify_event('1.4', q1_4, school, P(T & ~S))
""")

md(r"""
### 1.5 — *May 2025 TZ2 Paper 1 Q4(a), 3 marks*

Events $A$ and $B$ are such that $P(A\cup B)=\dfrac58$ and
$P(A\cap B')=\dfrac{7}{24}$.

Find $P(B)$.
""")

code(r"""
A, B = events('A B')
pair = [(P(A | B), Rational(5, 8)), (P(A & ~B), Rational(7, 24))]

q1_5 = ...

verify_event('1.5', q1_5, pair, P(B))
""")

md(r"""
### 1.6 — *November 2022 Paper 1 Q6(a), 1 mark*

Events $A$ and $B$ are such that $P(A)=0.3$ and $P(B)=0.8$.

Determine the value of $P(A\cap B)$ in the case where the events $A$ and
$B$ are independent.
""")

code(r"""
A, B = events('A B')
loose = [(P(A), Rational(3, 10)), (P(B), Rational(8, 10))]

q1_6 = ...

verify_event('1.6', q1_6, loose + [Eq(P(A & B), P(A)*P(B))], P(A & B))
""")

md(r"""
### 1.7 — *November 2022 Paper 1 Q6(b), 3 marks*

Determine the minimum possible value of $P(A\cap B)$.

*Two probabilities do not fix a space. The question is asking how small
the overlap can be made while everything stays a probability, and the
check answers it the same way: it looks for the smallest value $P(A\cap B)$
takes over every space the two conditions allow.*
""")

code(r"""
q1_7 = ...

verify_event('1.7', q1_7, loose, P(A & B), extreme='min')
""")

md(r"""
### 1.8 — *November 2022 Paper 1 Q6(c), 2 marks*

Determine the maximum possible value of $P(A\cap B)$, justifying your
answer.

*The number is checkable; the justification is not, and the markscheme is
strict about it — «Do not award R0A1». The solution says what has to be
written.*
""")

code(r"""
q1_8 = ...

verify_event('1.8', q1_8, loose, P(A & B), extreme='max')
""")

# ------------------------------------------------------------------ § 2
md(r"""
---
## 2. Conditional probability

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}$$

The bar cuts the space down to $B$ and asks the question again inside it.
Two things go wrong here and they go wrong constantly: the two events swap
places, and the division never happens. Both are named by the check, so
when you get one of them you will be told which.
""")

md(r"""
### 2.1 — *November 2025 TZ3 Paper 1 Q2(a), 2 marks*

Events $A$ and $B$ are such that $P(A)=\dfrac12$, $P(B)=\dfrac13$ and
$P(A\mid B)=\dfrac14$.

Find the probability that both events $A$ and $B$ occur.
""")

code(r"""
A, B = events('A B')
given = [(P(A), Rational(1, 2)), (P(B), Rational(1, 3)),
         (P(A, given=B), Rational(1, 4))]

q2_1 = ...

verify_event('2.1', q2_1, given, P(A & B))
""")

md(r"""
### 2.2 — *November 2025 TZ3 Paper 1 Q2(b), 4 marks*

Find $P(A\mid B')$.
""")

code(r"""
q2_2 = ...

verify_event('2.2', q2_2, given, P(A, given=~B))
""")

md(r"""
### 2.3 — *May 2025 TZ1 Paper 1 Q4(a), 3 marks*

Consider events $A$ and $B$ such that
$P(A')=P(A\cup B)=\dfrac34$ and $P(B\mid A)=\dfrac23$.

Find $P(A\cap B)$.
""")

code(r"""
A, B = events('A B')
may25 = [(P(~A), Rational(3, 4)), (P(A | B), Rational(3, 4)),
         (P(B, given=A), Rational(2, 3))]

q2_3 = ...

verify_event('2.3', q2_3, may25, P(A & B))
""")

md(r"""
### 2.4 — *May 2023 TZ2 Paper 1 Q3, 5 marks*

Events $A$ and $B$ are such that $P(A)=0.4$, $P(A\mid B)=0.25$ and
$P(A\cup B)=0.55$.

Find $P(B)$.
""")

code(r"""
A, B = events('A B')
two = [(P(A), Rational(4, 10)), (P(A, given=B), Rational(25, 100)),
       (P(A | B), Rational(55, 100))]

q2_4 = ...

verify_event('2.4', q2_4, two, P(B))
""")

md(r"""
### 2.5 — *May 2022 TZ1 Paper 2 Q5(b), 2 marks*

Let $A$ and $B$ be two independent events such that
$P(A\cap B')=0.16$ and $P(A'\cap B)=0.36$.

Find $P(A'\mid B')$.
""")

code(r"""
A, B = events('A B')
indep = [Eq(P(A & B), P(A)*P(B)),
         (P(A & ~B), Rational(16, 100)), (P(~A & B), Rational(36, 100))]

q2_5 = ...

verify_event('2.5', q2_5, indep, P(~A, given=~B))
""")

md(r"""
### 2.6 — *May 2025 TZ2 Paper 1 Q4(b), 4 marks*

Events $A$ and $B$ are such that $P(A\cup B)=\dfrac58$ and
$P(A\cap B')=\dfrac{7}{24}$.

Given that events $A$ and $B$ are independent, find $P(A'\mid B)$.
""")

code(r"""
A, B = events('A B')
same = [(P(A | B), Rational(5, 8)), (P(A & ~B), Rational(7, 24)),
        Eq(P(A & B), P(A)*P(B))]

q2_6 = ...

verify_event('2.6', q2_6, same, P(~A, given=B))
""")

md(r"""
### 2.7 — *May 2021 TZ2 Paper 2 Q3(c), 2 marks*

At the school 48% of the students are girls, and 25% of the girls are
involved in theatre.

A student is selected at random. Let $G$ be the event "the student is a
girl" and let $T$ be the event "the student is involved in theatre".

Find $P(G\cap T)$.
""")

code(r"""
G, T = events('G T')
girls = [(P(G), Rational(48, 100)), (P(T), Rational(2, 10)),
         (P(T, given=G), Rational(25, 100))]

q2_7 = ...

verify_event('2.7', q2_7, girls, P(G & T))
""")

# ------------------------------------------------------------------ § 3
md(r"""
---
## 3. Independence as an equation

$$A \text{ and } B \text{ are independent} \iff P(A\cap B)=P(A)\,P(B)$$

That is a definition, not a property, and it works in both directions. When
the question asks whether two events are independent, you compute both
sides and compare. When the question *tells* you they are independent, you
have gained an equation you did not have before — usually the one that
makes the question solvable at all.

The first three questions here ask for the verdict. You hand over the two
numbers the comparison rests on, in the order $P(A)\,P(B)$ then
$P(A\cap B)$ — which is exactly what the markscheme wants to see, and it
will not give the mark for a conclusion with no numbers under it.
""")

md(r"""
### 3.1 — *May 2025 TZ1 Paper 1 Q4(b), 3 marks*

Consider events $A$ and $B$ such that $P(A')=P(A\cup B)=\dfrac34$ and
$P(B\mid A)=\dfrac23$.

Show that events $A$ and $B$ are independent.
""")

code(r"""
A, B = events('A B')
may25 = [(P(~A), Rational(3, 4)), (P(A | B), Rational(3, 4)),
         (P(B, given=A), Rational(2, 3))]

q3_1 = ...          # [P(A)*P(B), P(A and B)]

verify_independence('3.1', q3_1, may25, A, B)
""")

md(r"""
### 3.2 — *May 2021 TZ2 Paper 2 Q3(d), 2 marks*

At the school 20% of the students are involved in theatre, 48% are girls,
and 25% of the girls are involved in theatre.

Determine if the events $G$ and $T$ are independent. Justify your answer.
""")

code(r"""
G, T = events('G T')
girls = [(P(G), Rational(48, 100)), (P(T), Rational(2, 10)),
         (P(T, given=G), Rational(25, 100))]

q3_2 = ...          # [P(G)*P(T), P(G and T)]

verify_independence('3.2', q3_2, girls, G, T)
""")

md(r"""
### 3.3 — *November 2021 Paper 1 Q4(b), 2 marks*

Box 1 contains 5 red balls and 2 white balls. Box 2 contains 4 red balls
and 3 white balls. A box is chosen at random and a ball is drawn.

Let $A$ be the event that "box 1 is chosen" and let $R$ be the event that
"a red ball is drawn".

Determine whether events $A$ and $R$ are independent.
""")

code(r"""
A, Rd = events('A R')
boxes = [(P(A), Rational(1, 2)),
         (P(Rd, given=A), Rational(5, 7)),
         (P(Rd, given=~A), Rational(4, 7))]

q3_3 = ...          # [P(A)*P(R), P(A and R)]

verify_independence('3.3', q3_3, boxes, A, Rd)
""")

md(r"""
### 3.4 — *May 2022 TZ1 Paper 2 Q5(a), 4 marks*

Let $A$ and $B$ be two independent events such that $P(A\cap B')=0.16$ and
$P(A'\cap B)=0.36$.

Given that $P(A\cap B)=x$, find the value of $x$.

*Here independence is the third equation. Without it the two numbers given
leave the space undetermined; with it they pin it exactly — and the
equation it adds is quadratic, which is why this part is worth four marks
and the next one two.*
""")

code(r"""
A, B = events('A B')
indep = [Eq(P(A & B), P(A)*P(B)),
         (P(A & ~B), Rational(16, 100)), (P(~A & B), Rational(36, 100))]

q3_4 = ...

verify_event('3.4', q3_4, indep, P(A & B))
""")

md(r"""
### 3.5 — *May 2022 TZ2 Paper 2 Q3, 6 marks*

Events $A$ and $B$ are independent and $P(A)=3P(B)$.

Given that $P(A\cup B)=0.68$, find $P(B)$.

*The quadratic has two roots and the markscheme takes only one: «Award A1
if both answers are given as final answers for $P(B)$». The other root is
$\tfrac{17}{15}$, and what is wrong with it is not that it is extraneous —
it is that it is not a probability.*
""")

code(r"""
A, B = events('A B')
triple = [Eq(P(A & B), P(A)*P(B)),
          Eq(sympify(P(A)), 3*sympify(P(B))),
          (P(A | B), Rational(68, 100))]

q3_5 = ...

verify_event('3.5', q3_5, triple, P(B))
""")

# ------------------------------------------------------------------ § 4
md(r"""
---
## 4. Trees

**Along a branch you multiply; between branches you add.**

A tree is the right picture whenever the experiment has stages. The first
level carries the probabilities of the first stage and adds to one; every
node of the second level carries *conditional* probabilities and adds to
one on its own. From here on the space is written out as a dictionary of
outcomes and weights, and the check adds up the ones you want — after
first making sure your weights come to one, which is where a mis-copied
tree is caught.
""")

md(r"""
### 4.1 — *May 2023 TZ1 Paper 2 Q7(a), 2 marks*

A new test has been developed to identify whether a particular gene, $G$,
is present in a population of parrots. The test returns a correct positive
result 95% of the time for parrots with the gene, and a false positive
result 2% of the time for parrots without the gene. The proportion of the
population with the gene is $p$.

Complete the tree diagram: the branch from the root to $G'$, and the two
branches out of $G$.

*Three boxes, and the check asks for the whole tree at once: write the
weight of each of the four paths and it will tell you whether they come to
one and whether the branch out of $G$ is right. The markscheme is strict
about the first box — «award A0 for $G'$ branch labelled $q$ unless
explicitly defined as $1-p$».*
""")

code(r"""
q4_1 = ...          # the four path weights, in order (G,+), (G,-), (G',+), (G',-)

verify_constants('4.1', q4_1, symbols('u1:5'), [
    ('the four paths together are certain', Eq(sum(symbols('u1:5')), 1)),
    ('a proportion p of the parrots carry the gene',
     Eq(symbols('u1') + symbols('u2'), p_)),
    ('the test is right 95% of the time on parrots that carry it',
     Eq(symbols('u1'), Rational(95, 100)*p_)),
    ('and gives a false positive 2% of the time on parrots that do not',
     Eq(symbols('u3'), Rational(2, 100)*(1 - p_))),
])
""")

md(r"""
### 4.2 — *November 2021 Paper 1 Q4(a), 3 marks*

Box 1 contains 5 red balls and 2 white balls. Box 2 contains 4 red balls
and 3 white balls.

A box is chosen at random and a ball is drawn. Find the probability that
the ball is red.
""")

code(r"""
boxes = {('1', 'red'):   Rational(1, 2)*Rational(5, 7),
         ('1', 'white'): Rational(1, 2)*Rational(2, 7),
         ('2', 'red'):   Rational(1, 2)*Rational(4, 7),
         ('2', 'white'): Rational(1, 2)*Rational(3, 7)}

q4_2 = ...

verify_probability('4.2', q4_2, boxes, lambda o: o[1] == 'red')
""")

md(r"""
### 4.3 — *November 2022 Paper 2 Q10(b), 3 marks*

The time worked, $T$, in hours per week by employees of a large company is
normally distributed with a mean of 42 and standard deviation 10.7.

A group of four employees is selected at random. Each employee is asked in
turn whether they work more than 40 hours per week. Find the probability
that the fourth employee is the only one in the group who works more than
40 hours per week.

*The branch probability comes from the normal distribution — that is the
GDC's work and it belongs to D5. What belongs here is the tree it sits in:
three "no" and then one "yes", in that order and no other.*
""")

code(r"""
over = nsimplify(0.5741362)          # P(T > 40), from the normal distribution
four = {(i, j, m, n): (over if i else 1 - over)*(over if j else 1 - over)
                      *(over if m else 1 - over)*(over if n else 1 - over)
        for i in (0, 1) for j in (0, 1) for m in (0, 1) for n in (0, 1)}

q4_3 = ...

verify_probability('4.3', q4_3, four, lambda o: o == (0, 0, 0, 1))
""")

md(r"""
### 4.4 — *May 2024 TZ2 Paper 1 Q4(a), 2 marks*

A species of bird can nest in two seasons: Spring and Summer. The
probability of nesting in Spring is $k$; the probability of nesting in
Summer is $\dfrac{k}{2}$.

Complete the tree diagram to show the probabilities of not nesting in each
season. Write your answers in terms of $k$.

*Three boxes and two of them are the same. Write the Summer one.*
""")

code(r"""
q4_4 = ...          # the four path weights: nest-nest, nest-not, not-nest, not-not

verify_constants('4.4', q4_4, symbols('v1:5'), [
    ('the four paths together are certain', Eq(sum(symbols('v1:5')), 1)),
    ('the bird nests in Spring with probability k',
     Eq(symbols('v1') + symbols('v2'), k_)),
    ('and in Summer with probability k/2 after nesting in Spring',
     Eq(symbols('v1'), k_*k_/2)),
    ('with the same k/2 in Summer after not nesting in Spring',
     Eq(symbols('v3'), (1 - k_)*k_/2)),
])
""")

# ------------------------------------------------------------------ § 5
md(r"""
---
## 5. Repeated trials and the first success

The same trial, over and over, independently. Two questions get asked:
**how many successes** (that is D3) and **when the first one comes** (that
is here).

$$P(\text{first success on the } n\text{th trial}) = p\,(1-p)^{\,n-1}$$

$n-1$ failures, then a success. The exponent is $n-1$ and not $n$, and that
off-by-one is the whole difficulty of the section.
""")

md(r"""
### 5.1 — *May 2024 TZ1 Paper 2 Q6(c), 2 marks*

In Happyland, the weather on any given day is independent of the weather
on any other day. On any day in May, the probability of rain is 0.2. May
has 31 days.

Find the probability that the first day that it rains in May is on the
10th day.
""")

code(r"""
may = {n: Rational(2, 10)*Rational(8, 10)**(n - 1) for n in range(1, 32)}
may['no rain at all'] = Rational(8, 10)**31

q5_1 = ...

verify_probability('5.1', q5_1, may, lambda o: o == 10)
""")

md(r"""
### 5.2 — *May 2024 TZ1 Paper 3 Q1(a)(i), 2 marks*

In a new computer game, each time a player performs an action, there is a
random chance that the action will be *boosted*. In the first model, the
probability that an action will be boosted is constant.

Suppose the probability that an action will be boosted is 0.1. Find the
probability that the first boost occurs on the third action.
""")

code(r"""
boost = {n: Rational(1, 10)*Rational(9, 10)**(n - 1) for n in range(1, 400)}
boost['never'] = Rational(9, 10)**399

q5_2 = ...

verify_probability('5.2', q5_2, boost, lambda o: o == 3)
""")

md(r"""
### 5.3 — *May 2024 TZ1 Paper 3 Q1(a)(ii), 3 marks*

Find the probability that at least one boost occurs in the first six
actions.
""")

code(r"""
q5_3 = ...

verify_probability('5.3', q5_3, boost, lambda o: o != 'never' and o <= 6)
""")

md(r"""
### 5.4 — *May 2024 TZ1 Paper 3 Q1(e), 2 marks*

In the designer's second model, the initial probability that an action is
boosted is 0.2, and each time an action occurs that is not boosted, the
probability that the next action is boosted increases by 0.2. After an
action has been boosted, the probability resets to 0.2 for the next action.

Show that the probability that the first boost occurs on the third action
is 0.288.

*The printed answer is the work: writing the space down is the question,
and the check tells you at once whether your space is the right one — it
will not let the weights past unless they come to one.*
""")

code(r"""
rising = [Rational(2, 10), Rational(4, 10), Rational(6, 10),
          Rational(8, 10), Rational(10, 10)]
second = {n: rising[n - 1]*Mul(*[1 - q for q in rising[:n - 1]])
          for n in range(1, 6)}

q5_4 = ...

verify_probability('5.4', q5_4, second, lambda o: o == 3)
""")

md(r"""
### 5.5 — *May 2024 TZ1 Paper 3 Q1(f), 1 mark* · no cell

Let $Y$ be the number of actions until the first boost occurs. Explain why
$Y \le 5$.

*Nothing to hand over. Do it on paper and read the solution.*
""")

md(r"""
### 5.6 — *May 2024 TZ1 Paper 3 Q1(g)(i), 2 marks*

The following table shows the probability distribution of $Y$.

| $y$ | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| $P(Y=y)$ | 0.2 | $m$ | 0.288 | $n$ | 0.0384 |

Find the value of $m$ and the value of $n$.
""")

code(r"""
q5_6 = ...          # [m, n]

verify_constants('5.6', q5_6, symbols('m n'), [
    ('the second action is boosted only if the first was not',
     Eq(symbols('m'), Rational(8, 10)*Rational(4, 10))),
    ('and the fourth only if none of the first three was',
     Eq(symbols('n'), Rational(8, 10)*Rational(6, 10)*Rational(4, 10)
        *Rational(8, 10))),
])
""")

md(r"""
### 5.7 — *May 2022 TZ2 Paper 1 Q10(c), 5 marks*

A biased four-sided die with faces 1, 2, 3, 4 has $P(X=x)$ equal to 0.4,
0.3, 0.2, 0.1 respectively. Nicky plays a game with this die: she is
allowed a maximum of five rolls, her score is the sum of the results, and
she wins if her score is at least ten.

After three rolls of the die, Nicky has a score of four. Assuming that
rolls of the die are independent, find the probability that Nicky wins the
game.

*Two rolls left and six more needed. The markscheme awards M0 to anyone who
also considers a score of 5 — the sum of the last two rolls has to reach
6, and 5 is not enough.*
""")

code(r"""
face = {1: Rational(4, 10), 2: Rational(3, 10),
        3: Rational(2, 10), 4: Rational(1, 10)}
last_two = {(u, v): face[u]*face[v] for u in face for v in face}

q5_7 = ...

verify_probability('5.7', q5_7, last_two, lambda o: o[0] + o[1] >= 6)
""")

# ------------------------------------------------------------------ § 6
md(r"""
---
## 6. The law of total probability

$$P(E)=\sum_i P(C_i)\,P(E\mid C_i)$$

The population splits into parts — two machines, three clerks, two kinds
of apple — and you want a probability across the whole of it. Each part
contributes its share times what happens inside it. The parts must cover
everything and must not overlap; check that before anything else.

This is the section where the calculator is finally doing real work: the
conditional probabilities inside the parts are normal or binomial, and
they are not available on paper.
""")

md(r"""
### 6.1 — *May 2022 TZ1 Paper 2 Q11(c)(i), 4 marks*

A bakery makes chocolate muffins, whose weights $C$ are normally
distributed with mean 62 g and standard deviation 2.9 g, and banana
muffins, whose weights $B$ are normally distributed with mean 68 g and
standard deviation 3.4 g. Each day 60% of the muffins made are chocolate.

On a particular day, a muffin is randomly selected from all those made at
the bakery. Find the probability that the randomly selected muffin weighs
less than 61 g.
""")

code(r"""
light = {'chocolate': nsimplify(0.3651120), 'banana': nsimplify(0.0197555)}
muffin = {(kind, w): (Rational(6, 10) if kind == 'chocolate' else Rational(4, 10))
                     * (light[kind] if w == '<61' else 1 - light[kind])
          for kind in light for w in ('<61', '>61')}

q6_1 = ...

verify_probability('6.1', q6_1, muffin, lambda o: o[1] == '<61')
""")

md(r"""
### 6.2 — *May 2025 TZ3 Paper 2 Q11(c)(i), 3 marks*

Amanda, Bryce and Carmen enter data from surveys into a database. Surveys
entered by Amanda, Bryce and Carmen are inaccurate 8%, 6% and 11% of the
time respectively. From the surveys assigned to the three of them, Amanda
enters 55%, Bryce 25% and Carmen 20%.

Find the probability that a randomly selected survey was entered
inaccurately.
""")

code(r"""
clerk = {'Amanda': (Rational(55, 100), Rational(8, 100)),
         'Bryce':  (Rational(25, 100), Rational(6, 100)),
         'Carmen': (Rational(20, 100), Rational(11, 100))}
survey = {(who, ok): share*(bad if ok == 'wrong' else 1 - bad)
          for who, (share, bad) in clerk.items() for ok in ('wrong', 'right')}

q6_2 = ...

verify_probability('6.2', q6_2, survey, lambda o: o[1] == 'wrong')
""")

md(r"""
### 6.3 — *November 2025 TZ1 Paper 2 Q7(a), 4 marks*

Two machines are used in a factory to manufacture semiconductors. Machine A
manufactures defective semiconductors 10% of the time, while machine B
manufactures defective semiconductors 5% of the time. A randomly selected
machine manufactures ten semiconductors. Both machines are equally likely
to be selected.

Find the probability that exactly two semiconductors are defective.
""")

code(r"""
chip = {(name, d): Rational(1, 2)*binomial(10, d)*q**d*(1 - q)**(10 - d)
        for name, q in (('A', Rational(1, 10)), ('B', Rational(1, 20)))
        for d in range(11)}

q6_3 = ...

verify_probability('6.3', q6_3, chip, lambda o: o[1] == 2)
""")

# ------------------------------------------------------------------ § 7
md(r"""
---
## 7. Bayes: back up the tree

$$P(C\mid E)=\frac{P(C)\,P(E\mid C)}{P(E)}$$

The tree runs from cause to effect; the question runs the other way. The
numerator is one path — the share of the cause times what it does — and the
denominator is §6, the whole of $P(E)$. That is the entire method: the hard
part was §6 and you have already done it.

The markscheme wants to see the conditional stated *in context*: «not just
$P(A\mid B)$». Writing the formula with letters earns nothing.
""")

md(r"""
### 7.1 — *May 2022 TZ1 Paper 2 Q11(c)(ii), 3 marks*

Given that a randomly selected muffin weighs less than 61 g, find the
probability that it is chocolate.
""")

code(r"""
q7_1 = ...

verify_probability('7.1', q7_1, muffin,
                   lambda o: o[0] == 'chocolate', given=lambda o: o[1] == '<61')
""")

md(r"""
### 7.2 — *May 2024 TZ2 Paper 1 Q6(b), 4 marks*

A farmer grows cooking apples and eating apples. The weights are normal:
eating apples $\mu=100$, $\sigma=20$; cooking apples $\mu=140$,
$\sigma=40$. For each type, 95% of the weights are within two standard
deviations of the mean. 80% of the apples the farmer grows are eating
apples. Both types are mixed together, and the machine separates out those
weighing more than 140 g into a container.

An apple is randomly selected from this container. Find the probability
that it is an eating apple. Give your answer in the form
$\dfrac{c}{d}$, where $c, d\in\mathbb{Z}^{+}$.

*140 g is two standard deviations above the eating-apple mean and exactly
the cooking-apple mean, so both branch probabilities are readable off the
95% rule without a calculator: 2.5% and 50%.*
""")

code(r"""
apple = {('eating', 'heavy'):  Rational(8, 10)*Rational(25, 1000),
         ('eating', 'light'):  Rational(8, 10)*(1 - Rational(25, 1000)),
         ('cooking', 'heavy'): Rational(2, 10)*Rational(1, 2),
         ('cooking', 'light'): Rational(2, 10)*Rational(1, 2)}

q7_2 = ...

verify_probability('7.2', q7_2, apple,
                   lambda o: o[0] == 'eating', given=lambda o: o[1] == 'heavy')
""")

md(r"""
### 7.3 — *May 2025 TZ3 Paper 2 Q11(c)(ii), 3 marks*

Find the probability that a randomly selected survey was entered by
Amanda, given that the survey was entered inaccurately.
""")

code(r"""
q7_3 = ...

verify_probability('7.3', q7_3, survey,
                   lambda o: o[0] == 'Amanda', given=lambda o: o[1] == 'wrong')
""")

md(r"""
### 7.4 — *November 2025 TZ1 Paper 2 Q7(b), 3 marks*

Given that exactly two semiconductors are defective, find the probability
that they were manufactured by machine A.
""")

code(r"""
q7_4 = ...

verify_probability('7.4', q7_4, chip,
                   lambda o: o[0] == 'A', given=lambda o: o[1] == 2)
""")

md(r"""
### 7.5 — *November 2022 Paper 2 Q10(c)(i), 3 marks*

The time worked, $T$, in hours per week is normally distributed with mean
42 and standard deviation 10.7. A large group of employees work more than
40 hours per week. An employee is selected at random from this large
group. Find the probability that this employee works less than 55 hours
per week.

*The conditioning event is not one branch of a tree here — it is a piece of
the real line. The machine is the same: the numerator is the overlap, the
denominator is the condition.*
""")

code(r"""
hours = {'under 40': nsimplify(0.4258633),      # from the normal distribution
         '40 to 55': nsimplify(0.4619448),
         'over 55':  nsimplify(0.1121919)}

q7_5 = ...

verify_probability('7.5', q7_5, hours,
                   lambda o: o != 'over 55', given=lambda o: o != 'under 40')
""")

# ------------------------------------------------------------------ § 8
md(r"""
---
## 8. Without replacement

Nothing goes back in the box, so the denominator shrinks by one at every
draw — and so does the numerator, if what you drew was what you wanted.

$$P(YY)=\frac{y}{r+y}\cdot\frac{y-1}{r+y-1}$$

Both shrink. Forgetting the numerator is the commoner slip of the two,
because the denominator is the one everybody has been told about.
""")

md(r"""
### 8.1 — *May 2023 TZ2 Paper 2 Q11(a), 4 marks*

A game of chance involves drawing **two** balls at random out of a box
without replacement. The box initially contains $r$ red balls and $y$
yellow balls. Let $P(YY)$ represent the probability of drawing two yellow
balls from the box without replacement.

Consider a version of this game where it is known that
$P(YY)=\dfrac13$.

Show that $2y^{2}-2(r+1)y+r-r^{2}=0$.

*Write the equation your own algebra produced, before it was tidied into
the printed form. The check accepts any equation that says the same thing
up to a numerical factor and a rearrangement, which is what the markscheme
accepts too — so this tells you whether your algebra landed, not whether
you copied the line above.*
""")

code(r"""
q8_1 = ...          # your equation, in r_ and y_

verify_equation('8.1', q8_1,
                Eq(2*y_**2 - 2*(r_ + 1)*y_ + r_ - r_**2, 0), var=y_)
""")

md(r"""
### 8.2 — *May 2023 TZ2 Paper 2 Q11(d), 3 marks*

Now consider a similar game that involves drawing **three** balls out of a
box without replacement. The box initially contains 10 red balls and $y$
yellow balls.

Find an expression for $P(YYY)$ in terms of $y$.
""")

code(r"""
q8_2 = ...          # in terms of y_

# the model, stage by stage: at draw i there are y - i yellow balls left
# out of y + 10 - i, and the answer is the product of the three
stages = [(y_ - i)/(y_ + 10 - i) for i in range(3)]

verify_identity('8.2', q8_2, Mul(*stages), var=y_, samples=(4, 7, 11, 20))
""")

md(r"""
### 8.3 — *May 2023 TZ2 Paper 2 Q11(e), 5 marks*

A yellow ball is added so that the box now contains 10 red balls and
$(y+1)$ yellow balls. The probability of drawing three yellow balls from
the box without replacement is now twice the probability expressed in part
(d).

Find the initial number of yellow balls in the box.
""")

code(r"""
q8_3 = ...          # the number of yellow balls the box started with

verify_constants('8.3', [q8_3], [y_], [
    ('adding one yellow ball doubles the probability of drawing three',
     Eq((y_ + 1)*y_*(y_ - 1)/((y_ + 11)*(y_ + 10)*(y_ + 9)),
        2*y_*(y_ - 1)*(y_ - 2)/((y_ + 10)*(y_ + 9)*(y_ + 8)))),
])
""")

# ------------------------------------------------------------------ § 9
md(r"""
---
## 9. Counting an equally likely space

When the outcomes are equally likely and countable, probability is a
fraction: how many fit over how many there are. The work is entirely in the
counting, and the counting is done by cases — never by listing.

Two things go wrong. The space is counted as *sets* when it is really
*ordered tuples*: rolling 1, 2, 3 in that order is a different outcome from
3, 2, 1, and both are among the 216. And a case gets missed, which no
amount of care with the arithmetic will fix.
""")

md(r"""
### 9.1 — *May 2024 TZ2 Paper 3 Q2(c), 6 marks*

Consider quadratic functions $f(x)=ax^{2}+bx+c$, whose coefficients $a$,
$b$ and $c$ are randomly generated in turn by rolling an unbiased
six-sided die three times and reading off the value shown on the uppermost
face.

By considering the discriminant, or otherwise, show that the probability of
the graph of such a randomly generated quadratic function having only one
$x$-intercept is $\dfrac{5}{216}$.
""")

code(r"""
rolls = {(u, v, w): Rational(1, 216)
         for u in range(1, 7) for v in range(1, 7) for w in range(1, 7)}

q9_1 = ...

verify_probability('9.1', q9_1, rolls,
                   lambda t: t[1]**2 - 4*t[0]*t[2] == 0)
""")

md(r"""
### 9.2 — *May 2024 TZ2 Paper 3 Q2(f), 6 marks*

Now consider randomly generated quadratic functions whose corresponding
graphs have two **distinct** $x$-intercepts. Let $p$ be the probability of
the graph of such a randomly generated quadratic function having two
distinct $x$-intercepts.

Using the approach started in part (e) — where $ac=1$ gives four such
functions and $ac=2$ gives eight — or otherwise, find the value of $p$.
""")

code(r"""
q9_2 = ...

verify_probability('9.2', q9_2, rolls,
                   lambda t: t[1]**2 - 4*t[0]*t[2] > 0)
""")

md(r"""
### 9.3 — *May 2022 TZ2 Paper 1 Q10(b), 2 marks*

A biased four-sided die with faces labelled 1, 2, 3 and 4 is rolled. The
probability distribution for $X$ is $p$, 0.3, $q$, 0.1, and it is known
that $E(X)=2$; part (a) gives $p=0.4$ and $q=0.2$.

Find $P(X>2)$.
""")

code(r"""
biased = {1: Rational(4, 10), 2: Rational(3, 10),
          3: Rational(2, 10), 4: Rational(1, 10)}

q9_3 = ...

verify_probability('9.3', q9_3, biased, lambda o: o > 2)
""")

md(r"""
### 9.4 — *May 2022 TZ2 Paper 1 Q10(d), 2 marks*

David has two pairs of unbiased four-sided dice, a yellow pair and a red
pair. Both yellow dice have faces labelled 1, 2, 3 and 4; let $S$ be the
sum obtained by rolling them, so that $P(S=s)$ is
$\tfrac1{16},\tfrac2{16},\tfrac3{16},\tfrac4{16},\tfrac3{16},
\tfrac2{16},\tfrac1{16}$ for $s=2,\dots,8$.

The first red die has faces labelled 1, 2, 2 and 3. The second red die has
faces labelled 1, $a$, $a$ and $b$, where $a<b$ and $a,b\in\mathbb{Z}^{+}$.
The probability distribution for the sum obtained by rolling the red pair
is the same as the distribution for the yellow pair.

Determine the value of $b$.
""")

code(r"""
q9_4 = ...

verify_constants('9.4', [q9_4], [b_], [
    ('the largest sum the red pair can make is the largest the yellow '
     'pair can make', Eq(3 + b_, 8)),
])
""")

md(r"""
### 9.5 — *May 2022 TZ2 Paper 1 Q10(e), 2 marks*

Find the value of $a$, providing evidence for your answer.

*One equation says everything here. The distribution of a sum is the
product of the two dice's generating polynomials — a face $f$ contributes
$z^{f}$ — so two pairs of dice give the same sums exactly when the two
products agree as polynomials. Hand over both faces and the identity
settles them together.*
""")

code(r"""
q9_5 = ...          # [a, b]

verify_constants('9.5', q9_5, [a_, b_], [
    ('the red pair and the yellow pair have the same generating polynomial',
     Eq(expand((z_ + 2*z_**2 + z_**3)*(z_ + 2*z_**a_ + z_**b_)),
        expand((z_ + z_**2 + z_**3 + z_**4)**2))),
])
""")

# ------------------------------------------------------------------ § 10
md(r"""
---
## 10. A letter inside the probability

The space itself has an unknown in it — a proportion $k$, a probability
$p$, a percentage $x$ — and a probability computed from it is given. You
do not substitute; you solve.

And then you throw a root away. Not because it is extraneous in the usual
algebraic sense, but because it is not a probability: it is bigger than one
or less than zero. **Say so out loud** — the markscheme gives a whole mark
for the sentence, and gives nothing for the right answer arrived at
silently.
""")

md(r"""
### 10.1 — *May 2024 TZ2 Paper 1 Q4(b), 4 marks*

A species of bird nests in Spring with probability $k$ and in Summer with
probability $\dfrac{k}{2}$, independently. It is known that the probability
of not nesting in Spring and not nesting in Summer is $\dfrac59$.

(i) Show that $9k^{2}-27k+8=0$.
(ii) Both $k=\dfrac13$ and $k=\dfrac83$ satisfy $9k^{2}-27k+8=0$. State why
$k=\dfrac13$ is the only valid solution.

*Hand over the value of $k$; the check puts it back into the sentence the
question actually states, which is (i) done properly. What (ii) wants is
one line of prose, and the solution gives it.*
""")

code(r"""
q10_1 = ...         # [k]

verify_constants('10.1', q10_1, [k_], [
    ('not nesting in Spring and not nesting in Summer has probability 5/9',
     Eq((1 - k_)*(1 - k_/2), Rational(5, 9))),
], domain=Interval(0, 1))
""")

md(r"""
### 10.2 — *May 2023 TZ1 Paper 2 Q7(b), 4 marks*

A test returns a correct positive result 95% of the time for parrots with
the gene $G$, and a false positive result 2% of the time for parrots
without it. The proportion of the population with the gene is $p$.

A random sample of the population was tested. It was found that 150 tests
returned a positive result. Out of the 150 parrots with a positive test
result, 18 did not actually have the gene. Find an estimate for $p$.

*The 18 out of 150 is a conditional probability, and the conditioning is on
the test being positive — not on the parrot. That is the whole question.*
""")

code(r"""
q10_2 = ...         # [p], to three significant figures

verify_constants('10.2', q10_2, [p_], [
    ('18 of the 150 positive tests were on parrots without the gene',
     Eq(Rational(2, 100)*(1 - p_)
        / (Rational(95, 100)*p_ + Rational(2, 100)*(1 - p_)),
        Rational(18, 150))),
], tol=5e-6)
""")

md(r"""
### 10.3 — *May 2025 TZ3 Paper 2 Q11(d), 4 marks*

The following year, the accuracy of Amanda's and Bryce's work remained the
same (8% and 6% inaccurate), as did the percentage of surveys entered by
each of the three employees (55%, 25%, 20%). However, Carmen's accuracy had
improved and the probability that she entered a survey inaccurately was
now $x\%$.

The probability that a randomly selected survey had been entered
inaccurately was now the same as the probability that Carmen made an error
when entering a survey.

Find the value of $x$.
""")

code(r"""
q10_3 = ...         # [x], as a percentage

verify_constants('10.3', q10_3, [a_], [
    ('the overall inaccuracy equals Carmen`s own',
     Eq(Rational(55, 100)*Rational(8, 100) + Rational(25, 100)*Rational(6, 100)
        + Rational(20, 100)*a_/100, a_/100)),
])
""")

# --------------------------------------------------------------- Solutions
md(r"""
---
---

# 🔑 Solutions

Numbered as above. Open one after you have worked the question.

---

## 1. The algebra of events

**1.1** $P(A\cup B)=0.65+0.75-0.6=\boxed{0.8}$. Or read it off the diagram:
the three cells $0.05+0.6+0.15$.

**1.2** By De Morgan, $A'\cap B'=(A\cup B)'$, so
$P=1-0.8=\boxed{0.2}$. The markscheme note is worth reading: *"0.2 must be
stated as the candidate's answer, or labeled as $P(A'\cap B')$ in their
Venn diagram. Just seeing an unlabeled 0.2 in the correct region earns
M1A0."* A number in the right place is not an answer.

**1.3** $P(S)+P(T)+P(S'\cap T')-P(S\cap T)=1$, so
$0.7+0.2+0.18-P(S\cap T)=1$ and $P(S\cap T)=\boxed{0.08}$.
Equivalently $P(S\cup T)=1-0.18=0.82$ and then the addition rule.

**1.4** $P(T\cap S')=P(T)-P(T\cap S)=0.2-0.08=\boxed{0.12}$.

**1.5** $A\cup B$ splits into $A\cap B'$ and $B$, which do not overlap:
$\tfrac58=\tfrac7{24}+P(B)$, so $P(B)=\tfrac{15-7}{24}=\boxed{\tfrac13}$.

**1.6** Independent means $P(A\cap B)=P(A)P(B)=0.3\times0.8=\boxed{0.24}$.

**1.7** $P(A\cup B)=P(A)+P(B)-P(A\cap B)=1.1-P(A\cap B)$, and a probability
is at most 1, so $P(A\cap B)\ge0.1$. The value 0.1 is attained when
$A\cup B$ is everything. $\boxed{0.1}$

**1.8** $P(A\cap B)\le P(A)=0.3$, attained when $A\subseteq B$ — which is
possible here because $P(A)<P(B)$. $\boxed{0.3}$

The reasoning is the mark. The markscheme wants *"$A$ is a subset of $B$
(so $P(A\cap B)=P(A)$)"*, or a clearly labelled diagram with $A$ entirely
inside $B$, and it says explicitly **"Do not award R0A1"** — the number
alone scores nothing.

---

## 2. Conditional probability

**2.1** $P(A\cap B)=P(A\mid B)\,P(B)=\tfrac14\cdot\tfrac13=\boxed{\tfrac1{12}}$.
Note which way the multiplication goes: the conditional multiplies the
probability of *its own condition*.

**2.2** $P(B')=\tfrac23$ and
$P(A\cap B')=P(A)-P(A\cap B)=\tfrac12-\tfrac1{12}=\tfrac5{12}$. Then
$P(A\mid B')=\dfrac{5/12}{2/3}=\boxed{\tfrac58}$.

Not $1-P(A\mid B)=\tfrac34$. The complement is taken of the *event*, and
here the complement is taken of the *condition* — a different operation
entirely, and the two agree only by accident.

**2.3** $P(A)=1-\tfrac34=\tfrac14$, and
$P(A\cap B)=P(B\mid A)\,P(A)=\tfrac23\cdot\tfrac14=\boxed{\tfrac16}$.

**2.4** Two equations in $P(B)$ and $P(A\cap B)$:
$$0.55=0.4+P(B)-P(A\cap B), \qquad 0.25=\frac{P(A\cap B)}{P(B)}.$$
Substituting the second into the first: $0.55=0.4+P(B)-0.25P(B)$, so
$0.75P(B)=0.15$ and $P(B)=\boxed{0.2}$.

**2.5** Because $A$ and $B$ are independent, so are $A'$ and $B'$, and
therefore $P(A'\mid B')=P(A')$. From part (a), $P(A\cap B)=0.24$, so
$P(A)=0.16+0.24=0.4$ and $P(A')=\boxed{0.6}$.

The long way works too: $P(B')=1-0.6=0.4$, $P(A'\cap B')=1-0.16-0.24-0.36
=0.24$, and $0.24/0.4=0.6$.

**2.6** From 1.5, $P(B)=\tfrac13$. Independence gives
$P(A\cap B')=P(A)P(B')$, so $\tfrac7{24}=P(A)\cdot\tfrac23$ and
$P(A)=\tfrac7{16}$. Then $P(A'\mid B')$ — no: the question asks
$P(A'\mid B)$, and independence again makes the condition irrelevant:
$P(A'\mid B)=P(A')=1-\tfrac7{16}=\boxed{\tfrac9{16}}$.

**2.7** $P(G\cap T)=P(T\mid G)\,P(G)=0.25\times0.48=\boxed{0.12}$.

Notice that this equals $P(T\cap S')$ from 1.4 — a coincidence of this
paper, and a good reminder that equal numbers are not the same event.

---

## 3. Independence as an equation

**3.1** From 2.3, $P(A)=\tfrac14$ and $P(A\cap B)=\tfrac16$. The addition
rule gives $\tfrac34=\tfrac14+P(B)-\tfrac16$, so $P(B)=\tfrac23$. Then
$$P(A)\,P(B)=\tfrac14\cdot\tfrac23=\tfrac16=P(A\cap B),$$
so $A$ and $B$ are independent. $\boxed{[\tfrac16,\ \tfrac16]}$

The markscheme note: *"The R1 is dependent on all previous marks."* The
conclusion is only worth something standing on the numbers.

**3.2** $P(G)\,P(T)=0.48\times0.2=0.096$, while
$P(G\cap T)=0.12$ from 2.7. They differ, so $G$ and $T$ are **not**
independent. $\boxed{[0.096,\ 0.12]}$

Or, equivalently, $P(T\mid G)=0.25\ne0.2=P(T)$: knowing the student is a
girl changes the probability of theatre, and that is what dependence means.

**3.3** $P(A)=\tfrac12$; $P(R)=\tfrac9{14}$ from 4.2;
$P(A\cap R)=\tfrac12\cdot\tfrac57=\tfrac5{14}$. Then
$$P(A)\,P(R)=\tfrac12\cdot\tfrac9{14}=\tfrac9{28}\ne\tfrac5{14}=\tfrac{10}{28},$$
so **not** independent. $\boxed{[\tfrac9{28},\ \tfrac5{14}]}$

The markscheme also accepts prose — *"different number of red balls in each
box"* — but insists: *"Both conclusion and reasoning are required. Do not
split the A2."*

**3.4** Let $P(A\cap B)=x$. Then $P(A)=x+0.16$ and $P(B)=x+0.36$, and
independence says
$$x=(x+0.16)(x+0.36) \Longrightarrow x^{2}-0.48x+0.0576=0
\Longrightarrow (x-0.24)^{2}=0,$$
so $x=\boxed{0.24}$. A repeated root — the two events are forced.

**3.5** Write $P(B)=b$, so $P(A)=3b$. Independence turns the addition rule
into
$$0.68=3b+b-3b^{2} \Longrightarrow 3b^{2}-4b+0.68=0
\Longrightarrow b=0.2 \text{ or } b=\tfrac{17}{15}.$$
The second is $1.133\ldots>1$, and a probability cannot exceed one, so
$P(B)=\boxed{0.2}$.

The markscheme awards A2 for 0.2 alone and only **A1** if both are offered
as final answers. Rejecting the root is half the mark.

---

## 4. Trees

**4.1** The four paths:
$$0.95p,\quad 0.05p,\quad 0.02(1-p),\quad 0.98(1-p).$$
The missing labels are $1-p$ on the lower first branch and $0.95$, $0.05$
on the two branches out of $G$. The markscheme insists the first be written
as $1-p$: *"award A0 for $G'$ branch labelled $q$ unless explicitly defined
as $1-p$"*. A letter is not a probability until it is defined.

**4.2** $P(R)=P(R\cap B_1)+P(R\cap B_2)
=\tfrac12\cdot\tfrac57+\tfrac12\cdot\tfrac47=\tfrac5{14}+\tfrac4{14}
=\boxed{\tfrac9{14}}$.

**4.3** $P(T>40)=0.574136\ldots$ from the normal distribution. "Only the
fourth" is one specific order — no, three orders are not wanted here: the
question names *the fourth* employee, so it is one path:
$$(1-0.574136)^{3}\times0.574136=\boxed{0.0443}.$$
Compare with 5.7, where the order is free and the paths must be counted.

**4.4** Not nesting in Spring is $1-k$; not nesting in Summer is
$1-\dfrac{k}{2}$, and it is the same on both branches because the seasons
are independent. The four paths:
$$\frac{k^{2}}{2},\quad k\!\left(1-\frac{k}{2}\right),\quad
\frac{(1-k)k}{2},\quad (1-k)\!\left(1-\frac{k}{2}\right).$$

---

## 5. Repeated trials and the first success

**5.1** Nine dry days and then rain:
$0.8^{9}\times0.2=\boxed{0.0268}$.

Not $0.8^{10}\times0.2$ (that is the first rain on the eleventh day) and
not $0.2$ (that is rain on the tenth day regardless of what came before).

**5.2** $0.9^{2}\times0.1=\boxed{0.081}$.

**5.3** Through the complement: $1-0.9^{6}=1-0.531441=\boxed{0.469}$.

Adding six terms gives the same number and takes six times as long; and
the sixth term is the one people drop.

**5.4** In the second model the probability of a boost is 0.2, then 0.4,
then 0.6, … until it happens. The first boost on the third action needs
two misses and then a hit:
$$0.8\times0.6\times0.6=\boxed{0.288}.$$
The third factor is 0.6 and not 0.4: after two misses the probability has
risen twice.

**5.5** After four consecutive misses the probability of a boost has
risen to $0.2+4(0.2)=1$, so the fifth action is boosted with certainty.
Hence $Y\le5$. (One mark, one sentence.)

**5.6** $m=P(Y=2)=0.8\times0.4=\boxed{0.32}$ and
$n=P(Y=4)=0.8\times0.6\times0.4\times0.8=\boxed{0.1536}$.

Check: $0.2+0.32+0.288+0.1536+0.0384=1$. That is worth doing — it catches
a dropped factor instantly.

**5.7** Nicky has 4 after three rolls and two rolls left, so she needs at
least 6 from two rolls. The markscheme is explicit: *"Award M0 if candidate
also considers scores other than 6, 7, or 8 (such as 5)."*

$$P(6)=2(0.3)(0.1)+(0.2)^{2}=0.1,\quad P(7)=2(0.2)(0.1)=0.04,\quad
P(8)=(0.1)^{2}=0.01$$
$$P(\text{wins})=0.1+0.04+0.01=\boxed{0.15}$$

The factors of 2 are the orders: $(2,4)$ and $(4,2)$ are different rolls.

---

## 6. The law of total probability

**6.1** $P(C<61)=0.365112$ and $P(B<61)=0.0197555$ from the normal
distributions. Weighting by the shares:
$$0.6\times0.365112+0.4\times0.0197555=\boxed{0.227}.$$

**6.2** $0.55(0.08)+0.25(0.06)+0.20(0.11)=0.044+0.015+0.022=\boxed{0.081}$.

The shares add to one — check that before anything else. Adding the three
error rates instead (0.25) is the standard wrong answer, and it is wrong by
a factor of three.

**6.3** Each machine gives a binomial: $B(10,0.1)$ and $B(10,0.05)$.
$$0.5\times0.193710+0.5\times0.0746347=\boxed{0.134}.$$

---

## 7. Bayes: back up the tree

**7.1** $$P(\text{choc}\mid{<}61)=\frac{0.6\times0.365112}{0.226969}
=\boxed{0.965}.$$

Almost all light muffins are chocolate, which makes sense: the banana ones
are heavier and there are fewer of them.

**7.2** $P(\text{weight}>140\mid\text{eating})=0.025$, because 140 g is two
standard deviations above 100 and 95% lie within two, leaving 2.5% above.
$P(\text{weight}>140\mid\text{cooking})=0.5$, because 140 is the cooking
mean. So
$$\frac{0.8\times0.025}{0.8\times0.025+0.2\times0.5}
=\frac{0.02}{0.12}=\boxed{\tfrac16}.$$

Four fifths of the apples are eating apples and still only one apple in six
in the container is one — that is what conditioning does.

**7.3** $$\frac{0.55\times0.08}{0.081}=\frac{0.044}{0.081}=\boxed{0.543}.$$

Amanda enters 55% of the surveys and makes 54% of the errors: her rate is
close to the average, so conditioning barely moves the share.

**7.4** $$\frac{0.5\times0.193710}{0.134172}=\boxed{0.722}.$$

The markscheme accepts 0.723 or 0.724 from three-significant-figure values
carried through — but only because it says so; do not count on that.

**7.5** $$P(T<55\mid T>40)=\frac{P(40<T<55)}{P(T>40)}
=\frac{0.461944}{0.574136}=\boxed{0.805}.$$

The markscheme note here is a small mercy worth knowing: *"Do not penalize
for inclusion or non-inclusion of endpoints for probabilities using a
normal distribution."* For a continuous variable the endpoint has
probability zero, so $\le$ and $<$ genuinely agree.

---

## 8. Without replacement

**8.1** $$P(YY)=\frac{y}{r+y}\cdot\frac{y-1}{r+y-1}=\frac13$$
$$3y(y-1)=(r+y)(r+y-1)$$
$$3y^{2}-3y=r^{2}+2ry+y^{2}-r-y$$
$$2y^{2}-2ry-2y+r-r^{2}=0
\Longrightarrow \boxed{2y^{2}-2(r+1)y+r-r^{2}=0}$$

**8.2** Three yellows out of $y$ yellow and 10 red:
$$P(YYY)=\boxed{\frac{y(y-1)(y-2)}{(y+10)(y+9)(y+8)}}$$

**8.3** With one more yellow ball the box holds $y+1$ yellow and 10 red:
$$\frac{(y+1)y(y-1)}{(y+11)(y+10)(y+9)}
=2\cdot\frac{y(y-1)(y-2)}{(y+10)(y+9)(y+8)}$$
Cancel $y(y-1)$ from both sides — legitimate, since $y\ge3$ for the
original probability to be non-zero — and then $(y+10)(y+9)$. The
markscheme awards a method mark for reaching exactly this line:
$$\frac{y+1}{y+11}=\frac{2(y-2)}{y+8}$$
$$(y+1)(y+8)=2(y-2)(y+11) \Longrightarrow y^{2}+9y+8=2y^{2}+18y-44$$
$$y^{2}+9y-52=0 \Longrightarrow (y-4)(y+13)=0 \Longrightarrow \boxed{y=4}$$

The negative root goes for the usual reason — a box cannot hold $-13$
balls. Worth one line of checking: with four yellow,
$P(YYY)=\frac{4\cdot3\cdot2}{14\cdot13\cdot12}=\frac1{91}$; with five,
$\frac{5\cdot4\cdot3}{15\cdot14\cdot13}=\frac2{91}$. Twice, as promised.

---

## 9. Counting an equally likely space

**9.1** One $x$-intercept means the discriminant is zero: $b^{2}=4ac$.
With $b\in\{1,\dots,6\}$, $b^{2}\in\{1,4,9,16,25,36\}$ and $4ac$ is a
multiple of 4, so $b$ must be even: $b=2$ gives $ac=1$, $b=4$ gives
$ac=4$, $b=6$ gives $ac=9$.

- $ac=1$: $(1,1)$ — one way.
- $ac=4$: $(1,4),(2,2),(4,1)$ — three ways.
- $ac=9$: $(3,3)$ — one way. ($(1,9)$ and $(9,1)$ need a 9.)

Five triples out of 216: $\boxed{\tfrac5{216}}$.

**9.2** Two distinct intercepts means $b^{2}>4ac$, that is
$b>2\sqrt{ac}$. Since $b\le6$, only $ac\le8$ can contribute. Count by the
value of $ac$: how many ordered pairs $(a,c)$ give it, and how many $b$
clear the bar.

| $ac$ | $2\sqrt{ac}$ | $(a,c)$ pairs | $b$ that work | product |
|---|---|---|---|---|
| 1 | 2 | $(1,1)$ — 1 | 3,4,5,6 — 4 | 4 |
| 2 | 2.83 | $(1,2),(2,1)$ — 2 | 3,4,5,6 — 4 | 8 |
| 3 | 3.46 | $(1,3),(3,1)$ — 2 | 4,5,6 — 3 | 6 |
| 4 | 4 | $(1,4),(2,2),(4,1)$ — 3 | 5,6 — 2 | 6 |
| 5 | 4.47 | $(1,5),(5,1)$ — 2 | 5,6 — 2 | 4 |
| 6 | 4.90 | $(1,6),(2,3),(3,2),(6,1)$ — 4 | 5,6 — 2 | 8 |
| 8 | 5.66 | $(2,4),(4,2)$ — 2 | 6 — 1 | 2 |

$4+8+6+6+4+8+2=38$, so $p=\dfrac{38}{216}=\boxed{\dfrac{19}{108}}\approx0.176$.

Two rows are easy to get wrong. At $ac=4$ the bar is exactly 4, and $b=4$
gives a repeated root, not two distinct ones — that case belongs to 9.1.
At $ac=6$ there are four pairs, not two: 6 factorises as $1\times6$ and
$2\times3$, and both orders count. This is why the check counts the 216
triples itself instead of trusting a table.

**9.3** $P(X>2)=q+0.1=0.2+0.1=\boxed{0.3}$.

**9.4** The largest sum the yellow pair can make is 8. The red pair's
largest is $3+b$, so $3+b=8$ and $b=\boxed{5}$.

**9.5** The distribution of a sum is the product of generating
polynomials: a die with faces $f_i$ contributes $\sum z^{f_i}$.

$$\text{yellow: } (z+z^{2}+z^{3}+z^{4})^{2}
= z^{2}(1+z+z^{2}+z^{3})^{2} = z^{2}(1+z)^{2}(1+z^{2})^{2}$$
$$\text{red: } (z+2z^{2}+z^{3})(z+2z^{a}+z^{b}) = z(1+z)^{2}(z+2z^{a}+z^{b})$$

Setting them equal: $z+2z^{a}+z^{b}=z(1+z^{2})^{2}=z+2z^{3}+z^{5}$, so
$a=\boxed{3}$ and $b=5$, confirming 9.4.

Without the polynomial the evidence is a table of the sixteen sums with
$a=3$: they come out $1,2,3,4,3,2,1$ over $s=2,\dots,8$, matching the
yellow row exactly. Either is accepted; the polynomial is shorter and
proves there is no other answer.

---

## 10. A letter inside the probability

**10.1** (i) Not nesting in either season:
$$(1-k)\!\left(1-\frac{k}{2}\right)=\frac59
\Longrightarrow 1-k-\frac{k}{2}+\frac{k^{2}}{2}=\frac59$$
$$\Longrightarrow 18-18k-9k+9k^{2}=10
\Longrightarrow \boxed{9k^{2}-27k+8=0}$$

(ii) $k=\tfrac83>1$, and $k$ is a probability, so it cannot exceed one.
Hence $k=\boxed{\tfrac13}$.

That sentence is the R1. The markscheme accepts *"any valid reasoning
indicating that any probability cannot be greater than 1 and/or
probability cannot be less than 0"* — and nothing else.

**10.2** Of the parrots that test positive, the fraction without the gene
is
$$P(G'\mid+)=\frac{0.02(1-p)}{0.95p+0.02(1-p)}=\frac{18}{150}=0.12.$$
Solving: $0.02-0.02p=0.12(0.93p+0.02)$, so
$0.02-0.02p=0.1116p+0.0024$, giving $0.1316p=0.0176$ and
$p=\boxed{0.134}$.

The other route: $0.95p\,S=132$ and $0.02(1-p)S=18$ for the sample size
$S$; dividing removes $S$ and gives the same equation. $S\approx1039$.

**10.3** With Carmen's rate $x\%$,
$$P(I)=0.55(0.08)+0.25(0.06)+0.20\!\left(\frac{x}{100}\right)
=\frac{x}{100}$$
$$0.059+0.002x=0.01x \Longrightarrow 0.008x=0.059
\Longrightarrow x=\boxed{7.38}$$

Read the condition twice before writing it: it says the *overall*
inaccuracy equals *Carmen's own*, which is why $x/100$ appears on both
sides. It does not say her rate is the average of the three.
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
