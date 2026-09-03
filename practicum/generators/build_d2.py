"""Собирает практикум D2: вероятность — события, условная, независимость, деревья.

Восьмой практикум серии и первый по статистике. Лестница из десяти приёмов
делится по тому, что приходится делать с пространством: приёмы 1–3 читают
готовую диаграмму Венна, 4, 5, 8 и 9 строят пространство сами, 6 и 7
проходят построенное в обратную сторону, 10 ищет в нём букву.

Проверок здесь три новых, и все живут в kit вместе с практикумом.

`verify_event` эталона не хранит. Вопрос о вероятности задаёт пространство,
а пространство определяет ответ: условия билета — «P(A) = 0,65»,
«P(A|B) = 1/4», «A и B независимы» — решаются как уравнения на веса атомов
диаграммы Венна, и то, о чём спрашивают, вычисляется по определению.
Интереснее то, что она делает с неверным ответом: промахи темы именные —
условная вероятность в обратную сторону, объединение без вычитания
пересечения, независимость там, где её не обещали, — и каждый из них
строится из того же пространства.

`verify_probability` — для вопросов, где пространство проще перечислить,
чем вывести: дерево, повторные испытания, вынимание без возвращения,
216 равновозможных троек. Первым делом она проверяет, что веса исходов
дают единицу; неверно переписанное дерево ловится именно здесь.

`verify_independence` — для вопросов «независимы ли». Вердикт сам по себе
монета, и схема оценивания не даёт за него отдельного балла: R-балл
зависит от предыдущего, а тот стоит на двух числах. Их и просят.

ANSWERS хранит эталонный ответ для каждой ячейки. В ноутбук он не попадает —
practicum/tests/verify_d2.py прогоняет по нему весь ноутбук и требует,
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

R = sp.Rational

NOTEBOOK = os.path.join(ROOT, 'practicum/statistics/practicum-d2-probability.ipynb')

TRIGGER = {1: 'venn', 2: 'given', 3: 'bayes', 4: 'indep', 5: 'count',
           6: 'tree', 7: 'letter', 8: 'noreplace', 9: 'total', 10: 'first',
           11: 'given', 12: 'indep'}
TRIGGER_KEY = {i: digest(val) for i, val in TRIGGER.items()}

ANSWERS = {
    'q1a': 'Rational(4, 5)',
    'q1b': 'Rational(1, 5)',
    'q2a': 'Rational(2, 25)',
    'q2b': 'Rational(3, 25)',
    'q3a': 'Rational(1, 12)',
    'q3b': 'Rational(5, 8)',
    'q4a': 'Rational(1, 3)',
    'q4b': 'Rational(9, 16)',
    'q5': 'Rational(1, 5)',
    'q6a': 'Rational(9, 14)',
    'q6b': '[Rational(9, 28), Rational(5, 14)]',
    'q7a': 'Rational(81, 1000)',
    'q7b': '0.468559',
    'q8': '[Rational(1, 3)]',
    'q9a': '0.081',
    'q9b': '0.543209',
    'q10a': '0.134172',
    'q10b': '0.721870',
    'q11a': 'y_*(y_ - 1)*(y_ - 2)/((y_ + 10)*(y_ + 9)*(y_ + 8))',
    'q11b': '4',
    'q12a': 'Rational(5, 216)',
    'q12b': 'Rational(19, 108)',
    'qt_a': 'Rational(6, 25)',
    'qt_b': 'Rational(3, 5)',
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
# D2 — Probability: events, conditioning, independence, trees

**156 marks of the archive, ten techniques, twelve tasks.** The first
practicum in the statistics section, and the first anywhere in the series
whose answer is just a number between zero and one.

That last fact is what makes the topic feel easy and score badly. Nothing
here is hard to compute. What is hard is knowing **which space you are
computing in** — and every lost mark in this topic is a mark lost to the
wrong space, not to the wrong arithmetic.

## The one idea

A probability question does not give you a number to manipulate. It gives
you a **space**, and the space gives you every number you will ever need
from it. Two events cut the space into four cells; a tree cuts it into
paths; three dice cut it into 216 triples. Once the cells are filled in,
the question is arithmetic. Before they are, no formula will save you.

So the work, always, is: *what are the outcomes, and what are their
weights?* Draw the diagram. Draw the tree. Write the 216 down as a rule.
Then read the answer off.

## How the checks work

They do not know the answer. `verify_event` takes the conditions your
question states — $P(A)=0.65$, $P(A\mid B)=\tfrac14$, *A and B are
independent* — treats them as equations on the weights of the four cells,
solves them, and computes what was asked from the definition.
`verify_probability` is handed a space written out as outcomes and weights,
checks that the weights come to one, and adds up the ones you want.

When you are wrong they say **how**. The slips in this topic have names,
and each is rebuilt from your own space:

| what you wrote | what the check says |
|---|---|
| $P(B\mid A)$ instead of $P(A\mid B)$ | the conditional is the wrong way round |
| $P(A\cap B)$ instead of $P(A\mid B)$ | it has not been divided by the condition yet |
| $P(A)+P(B)$ for $P(A\cup B)$ | the intersection is counted twice |
| $P(A)\,P(B)$ for $P(A\cap B)$ | the question never promised independence |
| $1-p$ instead of $p$ | that is the opposite event |
| anything above 1 | a probability is never above one |

## Order of work

| level | what it means | tasks |
|---|---|---|
| 🟢 | the space is drawn for you; read it | 1–3 |
| 🟡 | build the space, then read it | 4–8 |
| 🔴 | build it, then run it backwards | 9–12 |

Every task is a real past-paper question, cited. The full archive of the
topic — all fifty questions — is in the companion notebook
*D2 archive: probability*.

**62% of these marks carry a calculator**, and unusually for this series
that is close to honest: about 30 marks out of 156 genuinely need one,
because normal and binomial probabilities sit on the branches of the trees
in tasks 9 and 10. The other 126 are paper.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/statistics to practicum/kit.py
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + Rational, Eq, events, P(...)

language('en')                 # this notebook is in English, and so are the checks

k_, p_, y_ = symbols('k p y')

print('ready; sympy', sp.__version__)
print('a probability:  ', Rational(9, 14))
print('two numbers:    ', [Rational(9, 28), Rational(5, 14)])
print('events:         ', events('A B'))
""")

md(r"""
---
## Map of the ten techniques

| # | technique | you recognise it by | it reduces to |
|---|---|---|---|
| 1 | the algebra of events | a list of $P(\cdot)$ for combinations of two events | four cells that add to one |
| 2 | conditional probability | the word *given*, or a vertical bar | $P(A\cap B)/P(B)$ |
| 3 | independence | the word *independent*, in the question or the answer | one more equation: $P(A\cap B)=P(A)P(B)$ |
| 4 | trees | the experiment has stages | multiply along, add across |
| 5 | repeated trials | the same trial over and over | $p(1-p)^{n-1}$ for the first success |
| 6 | total probability | the population splits into parts | $\sum P(C_i)P(E\mid C_i)$ |
| 7 | Bayes | the effect is known, the cause is asked | one path over technique 6 |
| 8 | without replacement | nothing goes back | the denominator shrinks — and so does the numerator |
| 9 | counting | equally likely outcomes you can count | how many fit / how many there are |
| 10 | a letter in the space | an unknown $k$, $p$ or $x$ inside a probability | an equation, and a root thrown away |

Techniques 1–3 all live on the same picture and are really one skill seen
three ways. Techniques 6 and 7 are one machine run forwards and backwards.
The genuinely separate ones are 4, 5, 8, 9 — the four ways a space gets
built — and 10, which is the only place where an answer is rejected for
not being a probability.
""")

# ================================================================= теория 1
md(r"""
---
# 🟢 Part 1. Four cells

## Theory: the diagram is the method

Two events $A$ and $B$ cut the sample space into four pieces and no more:

$$A\cap B, \qquad A\cap B', \qquad A'\cap B, \qquad A'\cap B'$$

Their probabilities add to one. **Everything** you can be asked about $A$
and $B$ is a sum of some of them, so filling the four cells in solves the
question before you have used a single formula.

The formulas are just readings of the picture:

$$P(A\cup B)=P(A)+P(B)-P(A\cap B)$$

— because adding $P(A)$ and $P(B)$ counts the middle cell twice.

$$P(A'\cap B')=1-P(A\cup B)$$

— De Morgan: *neither* is the complement of *either*. This is the one that
goes wrong. $1-P(A)-P(B)$ is not it, and the difference is exactly the
middle cell.

### Conditioning is a new diagram

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}$$

The bar throws away everything outside $B$ and asks the question again in
what is left. Two things follow that people get wrong constantly.

**The order matters.** $P(A\mid B)$ and $P(B\mid A)$ have the same
numerator and different denominators. They agree only when
$P(A)=P(B)$, which is an accident.

**The complement is of the event, not of the condition.**
$P(A'\mid B)=1-P(A\mid B)$ is true — the events inside $B$ still add to
one. But $P(A\mid B')$ has nothing to do with $P(A\mid B)$: it is a
different question about a different piece of the space.

> **What the markscheme actually wants.** November 2023 is worth reading
> once: *"For the final mark, 0.2 must be stated as the candidate's answer,
> or labeled as $P(A'\cap B')$ in their Venn diagram. Just seeing an
> unlabeled 0.2 in the correct region earns M1A0."* A number in the right
> place on a picture is not an answer until you say what it is.
""")

md(r"""
### Task 1 🟢 — *November 2023 TZ1 Paper 1 Q2, 4 marks*

Events $A$ and $B$ are such that $P(A)=0.65$, $P(B)=0.75$ and
$P(A\cap B)=0.6$.

**(a)** Find $P(A\cup B)$.
**(b)** Hence, or otherwise, find $P(A'\cap B')$.
""")

code(r"""
A, B = events('A B')
given = [(P(A), 0.65), (P(B), 0.75), (P(A & B), 0.6)]

q1a = ...
q1b = ...

verify_event('1a', q1a, given, P(A | B))
verify_event('1b', q1b, given, P(~A & ~B))
""")

md(r"""
### Task 2 🟢 — *May 2021 TZ2 Paper 2 Q3(a)(b), 4 marks*

At a school, 70% of the students play a sport and 20% of the students are
involved in theatre. 18% of the students do neither activity. A student is
selected at random.

**(a)** Find the probability that the student plays a sport and is
involved in theatre.
**(b)** Find the probability that the student is involved in theatre, but
does not play a sport.

*The 18% is the fourth cell, and it is the only reason this question is
solvable. Percentages in words are probabilities; put them on the diagram
as they arrive.*
""")

code(r"""
S, T = events('S T')
school = [(P(S), Rational(7, 10)), (P(T), Rational(2, 10)),
          (P(~S & ~T), Rational(18, 100))]

q2a = ...
q2b = ...

verify_event('2a', q2a, school, P(S & T))
verify_event('2b', q2b, school, P(T & ~S))
""")

md(r"""
### Task 3 🟢 — *November 2025 TZ3 Paper 1 Q2, 6 marks*

Events $A$ and $B$ are such that $P(A)=\dfrac12$, $P(B)=\dfrac13$ and
$P(A\mid B)=\dfrac14$.

**(a)** Find the probability that both events $A$ and $B$ occur.
**(b)** Find $P(A\mid B')$.

*Part (b) is the trap named above. $1-\tfrac14=\tfrac34$ is not the answer,
and it is not close to the answer.*
""")

code(r"""
A, B = events('A B')
given = [(P(A), Rational(1, 2)), (P(B), Rational(1, 3)),
         (P(A, given=B), Rational(1, 4))]

q3a = ...
q3b = ...

verify_event('3a', q3a, given, P(A & B))
verify_event('3b', q3b, given, P(A, given=~B))
""")

# ================================================================= теория 2
md(r"""
---
# 🟡 Part 2. Building the space

## Theory: four ways a space gets made

Part 1 handed you a filled diagram. From here you have to draw it.

### Independence is an equation, not an adjective

$$A \text{ and } B \text{ independent} \iff P(A\cap B)=P(A)\,P(B)$$

That is a **definition**, and it works in both directions, which is the
whole point.

- The question **asks** whether they are independent → compute both sides
  and compare. The verdict alone earns nothing: the markscheme says *"Both
  conclusion and reasoning are required. Do not split the A2."*
- The question **says** they are independent → you have gained an equation.
  Usually it is the one that makes the problem solvable, and usually it is
  quadratic, which is why those parts are worth four marks and not two.

And when it is quadratic, **one root goes in the bin** — not because it is
extraneous, but because it is bigger than one and probabilities are not.
Say so in writing. May 2022 TZ2 gives $P(B)=0.2$ and $P(B)=\tfrac{17}{15}$,
and the markscheme awards **A1 instead of A2** to anyone who hands in both.

### Trees: along a branch multiply, between branches add

The first level carries the probabilities of the first stage; every node of
the second level carries **conditional** probabilities. Each fan of
branches adds to one — check that, always, because it is free and it
catches everything.

Write the branch complement as $1-p$ and define it. May 2023 is explicit:
*"award A0 for $G'$ branch labelled $q$ unless explicitly defined as
$1-p$."*

### Repeated trials: the first success

$$P(\text{first success on trial } n)=p\,(1-p)^{\,n-1}$$

$n-1$ failures, then a success. The exponent is $n-1$; that off-by-one is
the entire difficulty. And "at least one in $n$" is always
$1-(1-p)^{n}$ — never a sum, because the sum is where a term gets dropped.

### A letter in the space

An unknown $k$, $p$ or $x$ sits inside the probabilities and a probability
computed from it is given. You do not substitute; you write the equation
and solve it. Then you throw a root away and **say why**: May 2024 TZ2
gives a whole R1 mark for the sentence *"$\tfrac83>1$"*.
""")

md(r"""
### Task 4 🟡 — *May 2025 TZ2 Paper 1 Q4, 7 marks*

Events $A$ and $B$ are such that $P(A\cup B)=\dfrac58$ and
$P(A\cap B')=\dfrac{7}{24}$.

**(a)** Find $P(B)$.
**(b)** Given that events $A$ and $B$ are independent, find $P(A'\mid B)$.

*Two numbers do not fill four cells, and they do not have to: $P(B)$ is
determined anyway, because $A\cup B$ splits into $A\cap B'$ and $B$ with
no overlap. Part (b) is where independence earns its keep.*
""")

code(r"""
A, B = events('A B')
given = [(P(A | B), Rational(5, 8)), (P(A & ~B), Rational(7, 24))]

q4a = ...
q4b = ...

verify_event('4a', q4a, given, P(B))
verify_event('4b', q4b, given + [Eq(P(A & B), P(A)*P(B))], P(~A, given=B))
""")

md(r"""
### Task 5 🟡 — *May 2022 TZ2 Paper 2 Q3, 6 marks*

Events $A$ and $B$ are independent and $P(A)=3P(B)$.

Given that $P(A\cup B)=0.68$, find $P(B)$.

*Independence turns the addition rule into a quadratic. Solve it, then look
at both roots and decide out loud which one is a probability.*
""")

code(r"""
A, B = events('A B')
given = [Eq(P(A & B), P(A)*P(B)),
         Eq(sympify(P(A)), 3*sympify(P(B))),
         (P(A | B), Rational(68, 100))]

q5 = ...

verify_event('5', q5, given, P(B))
""")

md(r"""
### Task 6 🟡 — *November 2021 Paper 1 Q4, 5 marks*

Box 1 contains 5 red balls and 2 white balls. Box 2 contains 4 red balls
and 3 white balls.

**(a)** A box is chosen at random and a ball is drawn. Find the probability
that the ball is red.

Let $A$ be the event that "box 1 is chosen" and $R$ be the event that "a
red ball is drawn".

**(b)** Determine whether events $A$ and $R$ are independent.

*For (b) hand over the two numbers the comparison rests on, in the order
$P(A)\,P(R)$ then $P(A\cap R)$ — which is what the markscheme wants to see
under the conclusion.*
""")

code(r"""
boxes = {('1', 'red'):   Rational(1, 2)*Rational(5, 7),
         ('1', 'white'): Rational(1, 2)*Rational(2, 7),
         ('2', 'red'):   Rational(1, 2)*Rational(4, 7),
         ('2', 'white'): Rational(1, 2)*Rational(3, 7)}
A, Rd = events('A R')
tree = [(P(A), Rational(1, 2)), (P(Rd, given=A), Rational(5, 7)),
        (P(Rd, given=~A), Rational(4, 7))]

q6a = ...
q6b = ...          # [P(A)*P(R), P(A and R)]

verify_probability('6a', q6a, boxes, lambda o: o[1] == 'red')
verify_independence('6b', q6b, tree, A, Rd)
""")

md(r"""
### Task 7 🟡 — *May 2024 TZ1 Paper 3 Q1(a), 5 marks*

In a new computer game, each time a player performs an action there is a
random chance that the action will be *boosted*. In the first model the
probability that an action will be boosted is constant. Suppose that
probability is 0.1.

**(a)** Find the probability that the first boost occurs on the third
action.
**(b)** Find the probability that at least one boost occurs in the first
six actions.

*Part (b) through the complement. Six terms added up give the same number
and take six times as long, and the sixth is the one that gets dropped.*
""")

code(r"""
boost = {n: Rational(1, 10)*Rational(9, 10)**(n - 1) for n in range(1, 400)}
boost['never'] = Rational(9, 10)**399

q7a = ...
q7b = ...

verify_probability('7a', q7a, boost, lambda o: o == 3)
verify_probability('7b', q7b, boost, lambda o: o != 'never' and o <= 6)
""")

md(r"""
### Task 8 🟡 — *May 2024 TZ2 Paper 1 Q4(b), 4 marks*

A species of bird nests in Spring with probability $k$ and in Summer with
probability $\dfrac{k}{2}$, in each season independently of the other. It
is known that the probability of not nesting in Spring **and** not nesting
in Summer is $\dfrac59$.

**(i)** Show that $9k^{2}-27k+8=0$.
**(ii)** Both $k=\dfrac13$ and $k=\dfrac83$ satisfy that equation. State
why $k=\dfrac13$ is the only valid solution.

*Hand over $k$; the check puts it back into the sentence the question
states, which is (i) done properly. Part (ii) is one line of prose and one
whole mark — write it before you look at the solution.*
""")

code(r"""
q8 = ...           # [k]

verify_constants('8', q8, [k_], [
    ('not nesting in Spring and not nesting in Summer has probability 5/9',
     Eq((1 - k_)*(1 - k_/2), Rational(5, 9))),
], domain=Interval(0, 1))
""")

# ================================================================= теория 3
md(r"""
---
# 🔴 Part 3. Running it backwards

## Theory: total probability, Bayes, and two ways of counting

### Down the tree: total probability

$$P(E)=\sum_i P(C_i)\,P(E\mid C_i)$$

The population splits into parts — two machines, three clerks, two kinds of
apple — and each part contributes **its share times what happens inside
it**. Check first that the parts cover everything and do not overlap; that
is what makes the sum legitimate.

The standard wrong answer is to add the conditional probabilities without
their weights. For May 2025 TZ3 that gives $0.08+0.06+0.11=0.25$ instead of
$0.081$ — wrong by a factor of three, and it looks perfectly reasonable
until you notice it is not a weighted average of anything.

### Back up the tree: Bayes

$$P(C\mid E)=\frac{P(C)\,P(E\mid C)}{P(E)}$$

The tree runs cause → effect; the question runs effect → cause. The
numerator is **one path**; the denominator is the whole of $P(E)$, which
is the sum you just did. There is nothing else to it: the hard part was
total probability, and Bayes is a division.

The markscheme wants the conditional written **in context** — *"not just
$P(A\mid B)$"*. Letters earn nothing; name the events.

Bayes is also where intuition is worst. Task 9's Amanda enters 55% of the
surveys and makes 54% of the errors — barely a shift, because her error
rate is near average. But in the archive's apple question, 80% of apples
are eating apples and only **one in six** of the heavy ones is: the
conditioning is severe because the rates differ by a factor of twenty.

### Without replacement

$$P(YY)=\frac{y}{r+y}\cdot\frac{y-1}{r+y-1}$$

Both the numerator and the denominator drop by one. Everyone remembers the
denominator; the numerator is the one that gets left alone.

### Counting an equally likely space

When outcomes are equally likely and countable, probability is
$\dfrac{\text{how many fit}}{\text{how many there are}}$, and all the work
is in the counting. Count **by cases**, never by listing, and count
**ordered tuples**: rolling $1,2,3$ is a different outcome from $3,2,1$,
and both are among the 216.
""")

md(r"""
### Task 9 🔴 — *May 2025 TZ3 Paper 2 Q11(c), 6 marks*

Amanda, Bryce and Carmen enter data from surveys into a database. Surveys
entered by Amanda, Bryce and Carmen are inaccurate 8%, 6% and 11% of the
time respectively. From the surveys assigned to the three of them, Amanda
enters 55%, Bryce 25% and Carmen 20%.

Find the probability that a randomly selected survey was

**(i)** entered inaccurately;
**(ii)** entered by Amanda, given that the survey was entered
inaccurately.
""")

code(r"""
clerk = {'Amanda': (Rational(55, 100), Rational(8, 100)),
         'Bryce':  (Rational(25, 100), Rational(6, 100)),
         'Carmen': (Rational(20, 100), Rational(11, 100))}
survey = {(who, ok): share*(bad if ok == 'wrong' else 1 - bad)
          for who, (share, bad) in clerk.items() for ok in ('wrong', 'right')}

q9a = ...
q9b = ...

verify_probability('9a', q9a, survey, lambda o: o[1] == 'wrong')
verify_probability('9b', q9b, survey,
                   lambda o: o[0] == 'Amanda', given=lambda o: o[1] == 'wrong')
""")

md(r"""
### Task 10 🔴 — *November 2025 TZ1 Paper 2 Q7, 7 marks*

Two machines are used in a factory to manufacture semiconductors. Machine A
manufactures defective semiconductors 10% of the time, while machine B
manufactures defective semiconductors 5% of the time. A randomly selected
machine manufactures ten semiconductors. Both machines are equally likely
to be selected.

**(a)** Find the probability that exactly two semiconductors are
defective.
**(b)** Given that exactly two semiconductors are defective, find the
probability that they were manufactured by machine A.

*The branch probabilities are binomial — that is D3's business and the
GDC's. What is D2's business is the tree they sit in and the direction the
question runs.*
""")

code(r"""
chip = {(name, d): Rational(1, 2)*binomial(10, d)*q**d*(1 - q)**(10 - d)
        for name, q in (('A', Rational(1, 10)), ('B', Rational(1, 20)))
        for d in range(11)}

q10a = ...
q10b = ...

verify_probability('10a', q10a, chip, lambda o: o[1] == 2)
verify_probability('10b', q10b, chip,
                   lambda o: o[0] == 'A', given=lambda o: o[1] == 2)
""")

md(r"""
### Task 11 🔴 — *May 2023 TZ2 Paper 2 Q11(d)(e), 8 marks*

A game of chance involves drawing three balls out of a box without
replacement. The box initially contains 10 red balls and $y$ yellow balls.
Let $P(YYY)$ represent the probability of drawing three yellow balls
without replacement.

**(a)** Find an expression for $P(YYY)$ in terms of $y$.

A yellow ball is added, so the box now contains 10 red balls and $(y+1)$
yellow balls. The probability of drawing three yellow balls is now twice
the probability in part (a).

**(b)** Find the initial number of yellow balls in the box.
""")

code(r"""
q11a = ...         # in terms of y_
q11b = ...         # the number of yellow balls the box started with

# the model stage by stage: at draw i there are y - i yellow left of y + 10 - i
stages = [(y_ - i)/(y_ + 10 - i) for i in range(3)]
verify_identity('11a', q11a, Mul(*stages), var=y_, samples=(4, 7, 11, 20))

verify_constants('11b', [q11b], [y_], [
    ('adding one yellow ball doubles the probability of drawing three',
     Eq((y_ + 1)*y_*(y_ - 1)/((y_ + 11)*(y_ + 10)*(y_ + 9)),
        2*y_*(y_ - 1)*(y_ - 2)/((y_ + 10)*(y_ + 9)*(y_ + 8)))),
])
""")

md(r"""
### Task 12 🔴 — *May 2024 TZ2 Paper 3 Q2(c)(f), 12 marks*

Consider quadratic functions $f(x)=ax^{2}+bx+c$ whose coefficients $a$, $b$
and $c$ are randomly generated in turn by rolling an unbiased six-sided die
three times.

**(a)** By considering the discriminant, or otherwise, show that the
probability of the graph having only one $x$-intercept is $\dfrac5{216}$.

**(b)** Let $p$ be the probability of the graph having two **distinct**
$x$-intercepts. Find the value of $p$.

*Twelve marks of counting. Part (b) is done by cases on the value of $ac$,
and two of those cases are where everyone loses it: at $ac=4$ the
discriminant is exactly zero when $b=4$ — that belongs to part (a) — and
at $ac=6$ there are four ordered pairs, not two.*
""")

code(r"""
rolls = {(u, v, w): Rational(1, 216)
         for u in range(1, 7) for v in range(1, 7) for w in range(1, 7)}

q12a = ...
q12b = ...

verify_probability('12a', q12a, rolls, lambda t: t[1]**2 - 4*t[0]*t[2] == 0)
verify_probability('12b', q12b, rolls, lambda t: t[1]**2 - 4*t[0]*t[2] > 0)
""")

# ================================================================ тренажёр
md(r"""
---
## Trainer: name the technique in five seconds

Twelve openings. Do not compute anything — say only **which move you would
make first**. That is the decision this topic turns on, and on the paper
you get about five seconds of it.

| code | technique |
| --- | --- |
| `venn` | four cells: addition rule, complement, De Morgan |
| `given` | conditional probability |
| `indep` | independence, as a test or as an extra equation |
| `tree` | stages: multiply along, add across |
| `first` | repeated trials, the first success |
| `total` | the population splits into parts |
| `bayes` | the effect is known, the cause is asked |
| `noreplace` | nothing goes back in the box |
| `count` | equally likely outcomes, counted |
| `letter` | an unknown inside the probability |

1. $P(A)=0.65$, $P(B)=0.75$, $P(A\cap B)=0.6$. Find $P(A'\cap B')$.
2. $P(A)=\tfrac12$, $P(B)=\tfrac13$, $P(A\mid B)=\tfrac14$. Find $P(A\mid B')$.
3. Given that a randomly selected muffin weighs less than 61 g, find the probability that it is chocolate.
4. $P(A\cap B')=0.16$ and $P(A'\cap B)=0.36$; given $P(A\cap B)=x$, find $x$.
5. Show that the probability of a randomly generated quadratic having only one $x$-intercept is $\tfrac5{216}$.
6. A box is chosen at random and a ball is drawn. Find the probability that the ball is red.
7. It is known that the probability of not nesting in either season is $\tfrac59$. Show that $9k^{2}-27k+8=0$.
8. Find an expression for $P(YYY)$ in terms of $y$, where the box holds 10 red and $y$ yellow.
9. Find the probability that a randomly selected survey was entered inaccurately.
10. Find the probability that the first day that it rains in May is on the 10th day.
11. An employee is selected at random from the group who work more than 40 hours. Find the probability that they work less than 55 hours.
12. Determine whether events $A$ and $R$ are independent.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '',
    7: '', 8: '', 9: '', 10: '', 11: '', 12: '',
}

trigger_check(answers, """ + repr(TRIGGER_KEY) + r""")
""")

md(r"""
---
## On the timer

*May 2022 TZ1 Paper 2 Q5 — 6 marks. Eight minutes.*

Top of the notebook covered, paper and pen, formula booklet allowed.

Let $A$ and $B$ be two independent events such that $P(A\cap B')=0.16$ and
$P(A'\cap B)=0.36$.

**(a)** Given that $P(A\cap B)=x$, find the value of $x$.

**(b)** Find $P(A'\mid B')$.

| date | time | notes |
| --- | --- | --- |
|  |  |  |
""")

code(r"""
A, B = events('A B')
paper = [Eq(P(A & B), P(A)*P(B)),
         (P(A & ~B), Rational(16, 100)), (P(~A & B), Rational(36, 100))]

qt_a = ...
qt_b = ...

verify_event('timer (a)', qt_a, paper, P(A & B))
verify_event('timer (b)', qt_b, paper, P(~A, given=~B))
""")

# ================================================================= решения
md(r"""
---
# 🔑 Solutions

---

**1 (a)** $P(A\cup B)=0.65+0.75-0.6=\boxed{0.8}$. The subtraction is there
because adding $P(A)$ and $P(B)$ counts the middle cell twice.

**1 (b)** De Morgan: $A'\cap B'=(A\cup B)'$, so $1-0.8=\boxed{0.2}$.

Not $1-0.65-0.75$, which is negative. If your answer comes out negative you
have used $1-P(A)-P(B)$; the check will refuse it before you notice.

---

**2 (a)** The four cells add to one:
$$P(S)+P(T)+P(S'\cap T')-P(S\cap T)=1$$
$$0.7+0.2+0.18-P(S\cap T)=1 \Longrightarrow P(S\cap T)=\boxed{0.08}$$

Or: $P(S\cup T)=1-0.18=0.82$, then $0.82=0.7+0.2-P(S\cap T)$.

**2 (b)** $P(T\cap S')=P(T)-P(T\cap S)=0.2-0.08=\boxed{0.12}$.

The markscheme's note on the diagram route is worth reading: *"To obtain
the M1 for the Venn diagram all labels must be correct and in the correct
sections. For example, do not accept 0.7 in the area corresponding to
$S\cap T'$."* $P(S)$ is not the left cell — it is the left cell plus the
middle.

---

**3 (a)** $P(A\cap B)=P(A\mid B)\,P(B)=\tfrac14\cdot\tfrac13
=\boxed{\tfrac1{12}}$.

The conditional multiplies the probability of **its own condition**. That
is the direction to memorise; the other one gives $\tfrac18$ and is wrong.

**3 (b)** $P(B')=\tfrac23$, and
$$P(A\cap B')=P(A)-P(A\cap B)=\tfrac12-\tfrac1{12}=\tfrac5{12}$$
$$P(A\mid B')=\frac{5/12}{2/3}=\boxed{\tfrac58}$$

Not $1-\tfrac14=\tfrac34$. Complementing the **condition** changes which
piece of the space you are standing in; complementing the **event** does
not. Only the second one is a subtraction from 1.

---

**4 (a)** $A\cup B$ is $A\cap B'$ together with $B$, and those do not
overlap:
$$\tfrac58=\tfrac7{24}+P(B) \Longrightarrow P(B)=\tfrac{15-7}{24}
=\boxed{\tfrac13}$$

Two numbers and four cells, and the answer comes out anyway. It is worth
seeing why: $P(A\cap B)$ is genuinely undetermined here, and $P(B)$ does
not depend on it.

**4 (b)** Independence gives $P(A\cap B')=P(A)\,P(B')$, so
$\tfrac7{24}=P(A)\cdot\tfrac23$ and $P(A)=\tfrac7{16}$. Independence again
makes the condition irrelevant:
$$P(A'\mid B)=P(A')=1-\tfrac7{16}=\boxed{\tfrac9{16}}$$

That last step is the point of independence: conditioning on $B$ tells you
nothing about $A$, so the bar can be dropped. If you did it the long way
you got the same number and spent three more minutes.

---

**5** Independence turns the addition rule into a quadratic in $b=P(B)$:
$$0.68=3b+b-3b^{2} \Longrightarrow 3b^{2}-4b+0.68=0$$
$$b=\frac{4\pm\sqrt{16-8.16}}{6}=\frac{4\pm2.8}{6}
\Longrightarrow b=0.2 \text{ or } b=\tfrac{17}{15}$$

$\tfrac{17}{15}=1.133\ldots>1$, and a probability is never above one, so
$P(B)=\boxed{0.2}$.

The markscheme: *"Award A1 if both answers are given as final answers for
$P(B)$."* Two of the six marks are for making the choice and knowing why.

---

**6 (a)** $P(R)=P(R\cap B_1)+P(R\cap B_2)
=\tfrac12\cdot\tfrac57+\tfrac12\cdot\tfrac47=\tfrac{9}{14}
=\boxed{\tfrac9{14}}$.

**6 (b)** $P(A)=\tfrac12$ and $P(A\cap R)=\tfrac12\cdot\tfrac57
=\tfrac5{14}$, so
$$P(A)\,P(R)=\tfrac12\cdot\tfrac9{14}=\tfrac9{28}=\tfrac{9}{28},
\qquad P(A\cap R)=\tfrac5{14}=\tfrac{10}{28}$$
They differ, so $A$ and $R$ are **not** independent.
$\boxed{[\tfrac9{28},\ \tfrac5{14}]}$

The markscheme also accepts the prose version — *"different number of red
balls in each box"* — because that is the same statement: which box you are
in changes the chance of red, and that is exactly what dependence means.

---

**7 (a)** Two misses then a hit: $0.9^{2}\times0.1=\boxed{0.081}$.

**7 (b)** Through the complement: $1-0.9^{6}=1-0.531441=\boxed{0.469}$.

---

**8 (i)** Not nesting in Spring is $1-k$; not nesting in Summer is
$1-\tfrac{k}{2}$, and the seasons are independent, so
$$(1-k)\!\left(1-\frac{k}{2}\right)=\frac59
\Longrightarrow 1-\frac{3k}{2}+\frac{k^{2}}{2}=\frac59$$
Multiply by 18:
$$18-27k+9k^{2}=10 \Longrightarrow \boxed{9k^{2}-27k+8=0}$$

**8 (ii)** $k=\tfrac83>1$, and $k$ is a probability, so it cannot exceed
one. Hence $k=\boxed{\tfrac13}$.

The markscheme accepts *"any valid reasoning indicating that any
probability cannot be greater than 1 and/or probability cannot be less than
0"*. One sentence, one mark, and it is the mark most often missing.

---

**9 (i)** Weighted by the shares:
$$0.55(0.08)+0.25(0.06)+0.20(0.11)=0.044+0.015+0.022=\boxed{0.081}$$

Check the shares add to one before you start; here $0.55+0.25+0.20=1$, so
the three parts really do cover everybody.

**9 (ii)** $$P(\text{Amanda}\mid\text{inaccurate})
=\frac{0.55\times0.08}{0.081}=\frac{0.044}{0.081}=\boxed{0.543}$$

Amanda enters 55% of the surveys and produces 54% of the errors. Almost no
shift — because her error rate, 8%, is close to the overall 8.1%.
Conditioning only moves things when the rates differ.

---

**10 (a)** Each machine gives a binomial: $B(10,0.1)$ and $B(10,0.05)$.
$$P(\text{2 defective})=0.5\times0.193710+0.5\times0.0746347=\boxed{0.134}$$

**10 (b)** $$P(A\mid\text{2 defective})=\frac{0.5\times0.193710}{0.134172}
=\boxed{0.722}$$

Two defective out of ten is more like machine A than machine B, so seeing
it pushes the odds from 50:50 to about 72:28. That is what Bayes is for.

The markscheme's note is worth keeping: *"recognition must be shown in
context, either in words or symbols, not just $P(A\mid B)$."*

---

**11 (a)** Three yellows drawn from $y$ yellow and 10 red, nothing
replaced:
$$P(YYY)=\boxed{\frac{y(y-1)(y-2)}{(y+10)(y+9)(y+8)}}$$

Both parts of every fraction go down by one. Writing $\tfrac{y}{y+10}$
three times is the standard wrong answer and it is the with-replacement
model.

**11 (b)** With one more yellow the box holds $y+1$ yellow and 10 red:
$$\frac{(y+1)y(y-1)}{(y+11)(y+10)(y+9)}
=2\cdot\frac{y(y-1)(y-2)}{(y+10)(y+9)(y+8)}$$
Cancel $y(y-1)$ — legitimate, since $y\ge3$ — and $(y+10)(y+9)$:
$$\frac{y+1}{y+11}=\frac{2(y-2)}{y+8}
\Longrightarrow (y+1)(y+8)=2(y-2)(y+11)$$
$$y^{2}+9y+8=2y^{2}+18y-44 \Longrightarrow y^{2}+9y-52=0
\Longrightarrow (y-4)(y+13)=0$$
$$\boxed{y=4}$$

Check: $\tfrac{4\cdot3\cdot2}{14\cdot13\cdot12}=\tfrac1{91}$ and
$\tfrac{5\cdot4\cdot3}{15\cdot14\cdot13}=\tfrac2{91}$. Twice, as promised.

---

**12 (a)** One $x$-intercept means $b^{2}=4ac$. Since $4ac$ is a multiple
of four, $b$ must be even.

- $b=2$: $ac=1$, so $(a,c)=(1,1)$ — 1 way.
- $b=4$: $ac=4$, so $(1,4),(2,2),(4,1)$ — 3 ways.
- $b=6$: $ac=9$, so $(3,3)$ — 1 way, since $(1,9)$ needs a nine.

Five triples of 216: $\boxed{\tfrac5{216}}$.

**12 (b)** Two distinct intercepts means $b>2\sqrt{ac}$, so only
$ac\le8$ can contribute:

| $ac$ | $2\sqrt{ac}$ | $(a,c)$ pairs | $b$ that work | product |
|---|---|---|---|---|
| 1 | 2 | 1 | 4 | 4 |
| 2 | 2.83 | 2 | 4 | 8 |
| 3 | 3.46 | 2 | 3 | 6 |
| 4 | 4 | 3 | 2 | 6 |
| 5 | 4.47 | 2 | 2 | 4 |
| 6 | 4.90 | 4 | 2 | 8 |
| 8 | 5.66 | 2 | 1 | 2 |

$4+8+6+6+4+8+2=38$, so
$p=\dfrac{38}{216}=\boxed{\dfrac{19}{108}}\approx0.176$.

The two rows that go wrong: at $ac=4$ the bar is exactly 4, and $b=4$ gives
the repeated root that belongs to part (a); at $ac=6$ there are four
ordered pairs, because $6=1\times6=2\times3$ and both orders count.

---

## Timer

**(a)** Write $x=P(A\cap B)$. Then $P(A)=x+0.16$ and $P(B)=x+0.36$, and
independence says
$$x=(x+0.16)(x+0.36) \Longrightarrow x^{2}-0.48x+0.0576=0
\Longrightarrow (x-0.24)^{2}=0$$
so $x=\boxed{0.24}$ — a repeated root, so no choice to make here.

**(b)** $A$ and $B$ independent makes $A'$ and $B'$ independent too, so
$$P(A'\mid B')=P(A')=1-(0.16+0.24)=\boxed{0.6}$$

The long way also works: $P(A'\cap B')=1-0.16-0.24-0.36=0.24$ and
$P(B')=1-0.6=0.4$, giving $0.24/0.4=0.6$.
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
