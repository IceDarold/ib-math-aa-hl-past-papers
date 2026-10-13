"""Собирает практикум A5 (комплексные числа: формы и арифметика) в формате .ipynb."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'practicum'))
import sympy as sp
from kit import digest, sig, _complex_canon

I, P = sp.I, sp.pi
sq = sp.sqrt


def dz(value, sf=6):
    return digest(_complex_canon(value, sf))


def dset(values, sf=6):
    return digest('|'.join(sorted(_complex_canon(v, sf) for v in values)))


# --- эталонные ответы; каждый проверен в practicum/tests/verify_a5.py ---
D_Z1 = dz(3 * sq(2) * sp.exp(-I * P / 4))                  # 3 − 3i
D_Z2 = dz(2 * sp.exp(I * P / 3))                           # 1 + i√3
D_MOD3 = digest(sig(2, 6))
D_ARG3 = digest(sp.srepr(sp.simplify(2 * P / 3)))
D_Z4 = dz(sq(3) + I)                                       # 4i/(1 + i√3)
D_MOD5 = digest(sig(2, 6))
D_ARG5 = digest(sp.srepr(sp.simplify(P / 6)))
D_P6 = digest(sig(-19, 6))
D_Q6 = digest(sig(2, 6))
D_SET7 = dset([2, -1 + sq(3) * I, -1 - sq(3) * I])
D_B8 = digest(sp.srepr(sp.simplify(sp.Integer(-1))))
D_K9 = digest(sig(3, 6))
D_ZW9 = dz(-16)
D_A10 = digest(sp.srepr(sp.simplify((2 + sq(3)) / 2)))
D_B10 = digest(sp.srepr(sp.simplify((2 - sq(3)) / 2)))
D_SET11 = dset([-1 - sq(3) * I, -3])
D_SETA = dset([2, -4], sf=6)

TRIGGER = {1: 'form', 2: 'form', 3: 'modarg', 4: 'cart', 5: 'modarg', 6: 'parts',
           7: 'parts', 8: 'prop', 9: 'prop', 10: 'parts', 11: 'roots', 12: 'roots',
           13: 'cart', 14: 'roots', 15: 'prop'}
TRIGGER_KEY = {i: digest(v) for i, v in TRIGGER.items()}

cells = []


def _lines(src):
    parts = src.strip('\n').split('\n')
    return [p + '\n' for p in parts[:-1]] + parts[-1:]


def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": _lines(src)})


def code(src):
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": _lines(src)})


md(r"""
# Practicum A5: complex numbers, forms and arithmetic ℂ

The most «paper» topic of the archive after trigonometric equations: **102 marks out
of 144 are Paper 1**, and the calculator share is 29%. There is nothing to compute;
everything is solved by moving between three ways of writing the same number.

**Material.** 42 blocks and 144 marks from the AA HL archive, sessions May 2021 —
November 2025. Every task below is a real past-paper question, cited.

**What is here and what is in A6.** Complex numbers make a large topic in the
archive, 238 marks, and it splits in two by the substance of the technique rather
than down the middle:

- **A5, this practicum** — the three forms, moving between them, arithmetic,
  the conjugate, modulus and argument, conjugate roots of polynomials;
- **A6** — de Moivre's theorem, $n$-th roots, roots of unity, rotations and the
  geometry of the Argand plane.

The border runs where the arithmetic ends and raising to a power begins. If $z^n$
shows up in the solution, it is A6.

**How to work**

1. Read the map of techniques. The first four are about the forms, the fifth is
   about the properties of a product, the sixth is about polynomials.
2. Work **on paper**. Draw the Argand plane: the quadrant the number lies in
   determines the argument, and by eye that is more reliable than an arctangent.
3. Enter the answer in whichever form suits you. The check compares **the number
   itself**, not the writing: `2*exp(I*pi/3)`, `2*(cos(pi/3) + I*sin(pi/3))` and
   `1 + sqrt(3)*I` all count the same.
4. The last blocks are a recognition trainer and one question on a timer.

Difficulty marks: 🟢 the technique on its own · 🟡 the technique in a wrapper ·
🔴 several techniques, or a whole exam question.
""")

code(r"""
import sys
sys.path.append('..')          # from practicum/number_algebra to practicum/kit/
import sympy as sp             # the escape hatch: anything not in kit is in sp
from kit import *              # checks + I, pi, sqrt, exp, re, im and the other names

language('en')                 # this notebook is in English, and so are the checks

z, w = symbols('z w')
a, b = symbols('a b', real=True)

print('ready; sympy', sp.__version__)
print('the imaginary unit is I:', (1 + I)**2, '   and pi, sqrt as usual:', 2*exp(I*pi/3))
""")

md(r"""
---
## Map of techniques

| # | Technique | Trigger in the question | Gives |
| --- | --- | --- | --- |
| 1 | Arithmetic and the conjugate | a fraction with $i$ in the denominator, «rationalise» | $a + bi$ |
| 2 | Equate the parts | an equality of two complex expressions with unknowns | a system |
| 3 | Modulus and argument | «find $\lvert z\rvert$ and $\arg z$» | $r$, $\theta$ |
| 4 | Change of form | «in the form $re^{i\theta}$», «in Cartesian form» | another writing |
| 5 | Properties of a product | $\lvert z_1z_2\rvert$, $\arg(z_1z_2)$, the condition «$z \in \mathbb{R}$» | a relation |
| 6 | Conjugate roots | a polynomial with real coefficients | the other roots |

Techniques 1–4 are one and the same skill seen from four sides: **moving freely
between the three ways of writing a number.** The fifth and the sixth are built on
top of it.

The three forms, between which everything happens:

$$z = a + bi
\;=\; r(\cos\theta + i\sin\theta)
\;=\; r e^{i\theta}.$$

The rule of choice that saves half the work: **add in Cartesian, multiply in
polar.** Addition and subtraction are trivial in $a+bi$ and meaningless in the polar
form; multiplication, division and powers in the polar form come down to doing
something to $r$ and to $\theta$ separately.
""")

md(r"""
---
## Theory 1. The conjugate, and what it is for

The conjugate $\bar z = a - bi$ reflects the number in the real axis. Two of its
properties do all the work:

$$z\bar z = a^2 + b^2 = |z|^2 \quad(\text{always real}), \qquad
z + \bar z = 2a = 2\operatorname{Re}(z).$$

The first is the reason the conjugate is used at all. A complex number in a
denominator is not an answer; to get rid of it, multiply numerator and denominator by
the conjugate of the denominator, and the denominator becomes real:

$$\frac{1}{2 + 3i} = \frac{1}{2+3i}\cdot\frac{2 - 3i}{2 - 3i}
= \frac{2 - 3i}{4 + 9} = \frac{2}{13} - \frac{3}{13}i.$$

This is exactly the technique used to clear a root out of a denominator, and in the
markscheme it is called rationalising.
""")

md(r"""
## Task 1 🟢 — into exponential form

Express $z_1 = 3 - 3i$ in the form $re^{i\theta}$, where $r > 0$ and
$-\pi < \theta \le \pi$.

The order: the modulus by Pythagoras, then the quadrant from the signs, then the
acute angle from the arctangent of the ratio.

*Source: May 2025 TZ3, Paper 1, Q8(a) (3 marks, no calculator).*
""")

code(r"""
my_z1 = ...              # for example 5*exp(I*pi/3) or 5*(cos(pi/3) + I*sin(pi/3))

check_complex('Task 1', my_z1, '""" + D_Z1 + r"""')
""")

md(r"""
## Task 2 🟢 — one more change of form

Express $w = 1 + i\sqrt{3}$ in the form $re^{i\alpha}$, where $r > 0$ and
$-\pi < \alpha \le \pi$.

*Source: November 2025 TZ3, Paper 1, Q11(a)(i) (2 marks, no calculator).*
""")

code(r"""
my_w = ...

check_complex('Task 2', my_w, '""" + D_Z2 + r"""')
""")

md(r"""
---
## Theory 2. The argument and the quadrant

The modulus raises no questions: $|a + bi| = \sqrt{a^2 + b^2}$. The argument does,
and almost always in the same way.

The formula $\arg z = \arctan\dfrac{b}{a}$ is **only valid in the right half-plane**,
when $a > 0$. The arctangent returns values in $\left(-\frac{\pi}{2},
\frac{\pi}{2}\right)$, while an argument can be anything in $(-\pi, \pi]$. The
numbers $1 + i$ and $-1 - i$ have the same ratio $b/a = 1$ but arguments
$\frac{\pi}{4}$ and $-\frac{3\pi}{4}$.

A reliable order:

1. Mark the number on the plane and name the quadrant.
2. Find the **acute** angle $\alpha = \arctan\left|\dfrac{b}{a}\right|$.
3. Build it up to the right quadrant: I is $\alpha$, II is $\pi - \alpha$,
   III is $\alpha - \pi$, IV is $-\alpha$.

The drawing here is not an illustration, it is the method itself. Checking takes a
second: a number in the second quadrant must have its argument between
$\frac{\pi}{2}$ and $\pi$.
""")

md(r"""
## Task 3 🟢 — modulus, argument, and deducing the form

Given $u = -1 + \sqrt{3}\,i$.

**(a)** Find $|u|$ and $\arg u$.
**(b)** Hence show that $u = 2e^{2\pi i/3}$.

The number lies in the second quadrant — which is exactly where the arctangent
formula gives the wrong answer.

*Source: May 2023 TZ2, Paper 1, Q11(a) (3 marks, no calculator).*
""")

code(r"""
my_mod = ...
my_arg = ...             # the exact value

check_num('Task 3, |u|', my_mod, 6, '""" + D_MOD3 + r"""')
check_expr('Task 3, arg u', my_arg, '""" + D_ARG3 + r"""')
""")

md(r"""
## Task 4 🟢 — clearing the i out of the denominator

Given $w = \dfrac{4i}{1 + i\sqrt{3}}$.

Show that $w = \sqrt{3} + i$.

*Source: November 2025 TZ1, Paper 1, Q11(a) (2 marks, no calculator).*
""")

code(r"""
my_w4 = ...              # the result in the form a + b*I

check_complex('Task 4', my_w4, '""" + D_Z4 + r"""')
""")

md(r"""
## Task 5 🟢 — the modulus and argument of the result

For the same $w = \sqrt{3} + i$, find $|w|$ and $\arg w$.

*Source: November 2025 TZ1, Paper 1, Q11(b) (3 marks, no calculator).*
""")

code(r"""
my_mod5 = ...
my_arg5 = ...            # the exact value

check_num('Task 5, |w|', my_mod5, 6, '""" + D_MOD5 + r"""')
check_expr('Task 5, arg w', my_arg5, '""" + D_ARG5 + r"""')
""")

md(r"""
---
## Theory 3. Equating real and imaginary parts

The technique a third of the topic rests on. It comes from the definition of
equality:

$$a + bi = c + di \quad\Longleftrightarrow\quad a = c \ \text{ and } \ b = d.$$

That is, **one complex equation is equivalent to two real ones**. Hence the recipe:
if the unknowns in the question are real and the equation is complex, split both
sides into parts and get a system.

The order that saves time:

1. Write the unknown as $z = a + bi$ with $a$, $b$ real.
2. Expand everything, remembering that $i^2 = -1$.
3. Collect separately everything without $i$ and everything multiplying $i$.
4. Equate them to the corresponding parts of the right-hand side.
5. Solve the resulting system of two real equations.

Step 3 is where the marks go: a term like $qi \cdot i$ is real, not imaginary, and
it is easy to leave it in the wrong pile.
""")

md(r"""
## Task 6 🟡 — a system out of one equation

Given that $z = 5 + qi$ satisfies the equation

$$z^2 + iz = -p + 25i,$$

where $p, q \in \mathbb{R}$, find the values of $p$ and $q$.

*Source: November 2023 TZ1, Paper 1, Q7 (5 marks, no calculator).*
""")

code(r"""
my_p = ...
my_q = ...

check_num('Task 6, p', my_p, 6, '""" + D_P6 + r"""')
check_num('Task 6, q', my_q, 6, '""" + D_Q6 + r"""')
""")

md(r"""
## Task 7 🟡 — an equation with a conjugate

Solve $z^2 = 2\bar z$ for $z \ne 0$. Find **all** the roots.

The same technique here, but with two surprises. First: after splitting into parts
one of the equations factorises, and two cases appear. Second: there are three roots,
although the equation looks quadratic.

*Source: May 2023 TZ2, Paper 1, Q11(d) (5 marks, no calculator).*
""")

code(r"""
my_roots = [...]         # the list of all roots, order does not matter

check_complex_set('Task 7', my_roots, '""" + D_SET7 + r"""')
""")

md(r"""
---
## Theory 4. Properties of a product and a quotient

In polar form multiplication splits into two independent actions:

$$|z_1 z_2| = |z_1|\,|z_2|, \qquad \arg(z_1 z_2) = \arg z_1 + \arg z_2,$$

$$\left|\frac{z_1}{z_2}\right| = \frac{|z_1|}{|z_2|}, \qquad
\arg\!\left(\frac{z_1}{z_2}\right) = \arg z_1 - \arg z_2.$$

The moduli multiply, the arguments add. This is the only reason the polar form is
needed at all.

**How it is asked.** Almost always through the condition «$z_1z_2$ is real» or «is
purely imaginary». It translates like this:

$$z \in \mathbb{R} \iff \arg z = k\pi, \qquad
z \text{ is purely imaginary} \iff \arg z = \frac{\pi}{2} + k\pi.$$

That gives an equation in integers, and the smallest solution is asked for. Zero is
an allowed value of the argument too — that is the one people forget.
""")

md(r"""
## Task 8 🟡 — the argument of a product

Given $z_1 = 1 + bi$ and $z_2 = (1 - b^2) - 2bi$, where $b \in \mathbb{R}$,
$b \ne 0$.

**(a)** Find an expression for $z_1z_2$ in terms of $b$.
**(b)** Given that $\arg(z_1z_2) = \dfrac{\pi}{4}$, find the value of $b$.

Part (a) is worth taking as far as «a positive number times something»: then in (b)
the positive factor does not affect the argument, and everything comes down to one
arctangent.

*Source: May 2022 TZ1, Paper 1, Q9 (6 marks, no calculator).*
""")

code(r"""
my_b8 = ...              # the exact value

check_expr('Task 8', my_b8, '""" + D_B8 + r"""')
""")

md(r"""
## Task 9 🟡 — the condition for being real

Given complex numbers $z$ and $w$ with
$|z| = 2$, $\arg z = \dfrac{\pi}{5}$, $|w| = 8$, $\arg w = -\dfrac{2k\pi}{5}$,
where $k \in \mathbb{Z}^+$.

Given that $zw \in \mathbb{R}$, find the smallest value of $k$ and the corresponding
value of $zw$.

*Source: May 2021 TZ1, Paper 2, Q8 (7 marks, calculator).*
""")

code(r"""
my_k = ...
my_zw = ...

check_num('Task 9, k', my_k, 6, '""" + D_K9 + r"""')
check_complex('Task 9, zw', my_zw, '""" + D_ZW9 + r"""')
""")

md(r"""
## Task 10 🔴 — a square root through the parts

Given that $w = \sqrt{3} + i$ can be written as $w = (a + bi)^2$, where $a, b > 0$.

Find $a^2$ and $b^2$. The answers are **exact**.

Expand the square, equate the parts and get a system. It is non-linear, but it comes
down to a quadratic in $a^2$. There is a short way too: $a^2 + b^2 = |a+bi|^2 = |w|$,
and together with $a^2 - b^2 = \sqrt3$ that is already a linear system.

*Source: November 2025 TZ1, Paper 1, Q11(d) (8 marks, no calculator).*
""")

code(r"""
my_a2 = ...              # the exact value
my_b2 = ...              # the exact value

check_expr('Task 10, a^2', my_a2, '""" + D_A10 + r"""')
check_expr('Task 10, b^2', my_b2, '""" + D_B10 + r"""')
""")

md(r"""
---
## Theory 5. Conjugate roots of a polynomial

The fact the whole technique grows out of:

> If a polynomial has **real coefficients** and $z_0$ is a root of it, then
> $\bar z_0$ is a root as well.

The condition about real coefficients is essential, and in the question it is always
written out explicitly. Without it the theorem is false.

The consequences that get used:

- complex roots come in **pairs**, so a polynomial of odd degree has at least one
  real root;
- knowing one complex root, you get a second one for free;
- a pair $z_0, \bar z_0$ gives a real quadratic factor
  $z^2 - 2\operatorname{Re}(z_0)z + |z_0|^2$.

After that Vieta comes in. For a polynomial $z^n + c_{n-1}z^{n-1} + \ldots + c_0$:

$$\sum z_i = -c_{n-1}, \qquad \prod z_i = (-1)^n c_0.$$

The sum of a conjugate pair is $2\operatorname{Re}(z_0)$, the product is $|z_0|^2$ —
both real, and the unknowns come out of a single equation.

**On a real question.** A polynomial $z^4 + pz^3 + \ldots + 80$ with real
coefficients has roots $3+i$, $\alpha$, $\alpha^2$ (with $\alpha$ real). The product
of the roots is 80, so $(3+i)(3-i)\alpha\cdot\alpha^2 = 80$, that is
$10\alpha^3 = 80$ and $\alpha = 2$. Then the sum of the roots:
$-p = (3+i) + (3-i) + 2 + 4 = 12$, hence $p = -12$. The imaginary parts cancelled by
themselves — they always do.
""")

md(r"""
## Task 11 🟡 — the other roots of a cubic

Given that $u = -1 + \sqrt{3}\,i$ is a root of the equation

$$z^3 + 5z^2 + 10z + 12 = 0,$$

find the other two roots.

*Source: May 2023 TZ2, Paper 1, Q11(c)(i) (part of 9 marks, no calculator).*
""")

code(r"""
my_rest = [...]          # the two remaining roots

check_complex_set('Task 11', my_rest, '""" + D_SET11 + r"""')
""")

md(r"""
---
## Trainer: name the technique

Nothing is solved here: name the technique with one code.

| Code | Technique |
| --- | --- |
| `cart` | arithmetic, clear the $i$ out of the denominator |
| `parts` | equate real and imaginary parts |
| `modarg` | find the modulus and the argument |
| `form` | change to another form |
| `prop` | properties of the modulus and argument of a product |
| `roots` | conjugate roots of a polynomial, Vieta |

1. «Express $3 - 3i$ in the form $re^{i\theta}$»
2. «Write $2e^{i\pi/3}$ in Cartesian form»
3. «Find $|u|$ and $\arg u$ for $u = -1 + \sqrt3 i$»
4. «Show that $\dfrac{4i}{1 + i\sqrt3} = \sqrt3 + i$»
5. «Find $\arg w$, where $w = \sqrt3 + i$»
6. «$z = 5 + qi$ satisfies $z^2 + iz = -p + 25i$. Find $p$ and $q$»
7. «Solve $z^2 = 2\bar z$»
8. «Find $\arg(z_1z_2)$ in terms of $k$»
9. «Given that $zw$ is real, find the smallest $k$»
10. «$w = (a+bi)^2$, find $a^2$»
11. «$-1+\sqrt3 i$ is a root of a cubic. Find the others»
12. «Two roots of a quartic are $a+bi$ and $b+ai$. Find $a$»
13. «Simplify $\dfrac{1}{2+3i}$»
14. «Find $p$, given that the sum of the roots is 12»
15. «Show that $\lvert z_1z_2\rvert = \lvert z_1\rvert\lvert z_2\rvert$»

The target is 15 out of 15 in under two minutes.
""")

code(r"""
answers = {
    1: '', 2: '', 3: '', 4: '', 5: '', 6: '', 7: '', 8: '',
    9: '', 10: '', 11: '', 12: '', 13: '', 14: '', 15: '',
}

KEY = """ + repr(TRIGGER_KEY) + r"""
trigger_check(answers, KEY)
""")

md(r"""
---
## Task 12 🔴 — ON THE TIMER: 12 minutes

Close everything above. Paper 1 format, no calculator, 8 marks.

The equation $z^4 + 4z^3 + 8z^2 + 80z + 400 = 0$ has real coefficients. Given that
$a + bi$ and $b + ai$ are two of its roots, where $a, b \in \mathbb{R}$, find the
possible values of $a$.

A hint about the structure, not about the solution: the coefficients are real, so you
know not two roots but four. After that you need both of Vieta's formulas — one gives
a linear relation, the other a quadratic one.

*Source: May 2021 TZ1, Paper 1, Q7 (8 marks, no calculator).*
""")

code(r"""
# set a timer for 12 minutes
my_a_values = [...]      # all the possible values of a

check_complex_set('Task 12', my_a_values, '""" + D_SETA + r"""')
""")

md(r"""
### Attempt log

| Question | Answer |
| --- | --- |
| Did you finish inside 12 minutes? | |
| Did you write down all four roots straight away? | |
| Which of Vieta's formulas did you take first? | |
| Where did the time go? | |

If you started expanding $(z - (a+bi))(z - (a-bi))\ldots$ head-on, that works too and
the markscheme accepts it, but it is longer than writing down the sum and the
product.
""")

md(r"""
---
# 🔑 Solutions

Check not only the answer but that no step is missing: the markscheme pays for
method.
""")

md(r"""
## Solution 1 — into exponential form

$z_1 = 3 - 3i$ lies in the **fourth** quadrant: the real part is positive, the
imaginary part negative.

$$r = \sqrt{3^2 + (-3)^2} = \sqrt{18} = 3\sqrt2.$$

The acute angle: $\arctan\left|\frac{-3}{3}\right| = \arctan 1 = \frac{\pi}{4}$.
In the fourth quadrant the argument is negative, so $\theta = -\frac{\pi}{4}$.

$$z_1 = 3\sqrt2\, e^{-i\pi/4}.$$

```python
my_z1 = 3*sqrt(2)*exp(-I*pi/4)
```
""")

md(r"""
## Solution 2 — one more change of form

$w = 1 + i\sqrt3$ is in the **first** quadrant, so the arctangent gives the answer
straight away.

$$r = \sqrt{1 + 3} = 2, \qquad
\alpha = \arctan\frac{\sqrt3}{1} = \frac{\pi}{3}.$$

$$w = 2e^{i\pi/3}.$$

```python
my_w = 2*exp(I*pi/3)
```
""")

md(r"""
## Solution 3 — modulus, argument, and deducing the form

$u = -1 + \sqrt3 i$ is in the **second** quadrant.

$$|u| = \sqrt{(-1)^2 + (\sqrt3)^2} = \sqrt4 = 2.$$

The acute angle is $\arctan\frac{\sqrt3}{1} = \frac{\pi}{3}$, and in the second
quadrant the argument is built up as $\pi - \frac{\pi}{3} = \frac{2\pi}{3}$.

$$u = 2\left(\cos\frac{2\pi}{3} + i\sin\frac{2\pi}{3}\right) = 2e^{2\pi i/3}.$$

```python
my_mod = 2
my_arg = 2*pi/3
```

The answer $-\frac{\pi}{3}$ is the standard mistake: that is exactly what a
calculator gives for $\arctan(-\sqrt3)$, because it does not know which quadrant the
number is in.
""")

md(r"""
## Solution 4 — clearing the i out of the denominator

Multiply by the conjugate of the denominator:

$$w = \frac{4i}{1 + i\sqrt3}\cdot\frac{1 - i\sqrt3}{1 - i\sqrt3}
= \frac{4i(1 - i\sqrt3)}{1 + 3}
= \frac{4i - 4i^2\sqrt3}{4}
= \frac{4\sqrt3 + 4i}{4} = \sqrt3 + i.$$

```python
my_w4 = sqrt(3) + I
```

The key step is $-4i^2\sqrt3 = +4\sqrt3$: minus times minus gives plus, and the
imaginary term becomes real.
""")

md(r"""
## Solution 5 — the modulus and argument of the result

$w = \sqrt3 + i$ is in the first quadrant.

$$|w| = \sqrt{3 + 1} = 2, \qquad
\arg w = \arctan\frac{1}{\sqrt3} = \frac{\pi}{6}.$$

```python
my_mod5 = 2
my_arg5 = pi/6
```
""")

md(r"""
## Solution 6 — a system out of one equation

Substitute $z = 5 + qi$ and expand:

$$z^2 = (5 + qi)^2 = 25 + 10qi + q^2i^2 = (25 - q^2) + 10qi,$$

$$iz = i(5 + qi) = 5i + qi^2 = -q + 5i.$$

Add them and collect the parts:

$$z^2 + iz = \underbrace{(25 - q^2 - q)}_{\text{real}}
+ \underbrace{(10q + 5)}_{\text{imaginary}}\,i = -p + 25i.$$

Imaginary parts: $10q + 5 = 25 \Rightarrow q = 2$.
Real parts: $25 - 4 - 2 = 19 = -p \Rightarrow p = -19$.

```python
my_p = -19
my_q = 2
```

Note the order: the imaginary equation contains only $q$, so that is the one to start
with. Starting with the real one you get an equation in two unknowns.
""")

md(r"""
## Solution 7 — an equation with a conjugate

Let $z = a + bi$. Then

$$z^2 = (a^2 - b^2) + 2abi, \qquad 2\bar z = 2a - 2bi.$$

Equate the parts:

$$a^2 - b^2 = 2a, \qquad 2ab = -2b.$$

**The second equation factorises:** $2b(a + 1) = 0$, so $b = 0$ or $a = -1$. Take
both cases.

*Case $b = 0$.* Then $a^2 = 2a$, that is, $a = 0$ or $a = 2$. Zero is excluded by the
question, so $z = 2$ remains.

*Case $a = -1$.* Then $1 - b^2 = -2$, so $b^2 = 3$ and $b = \pm\sqrt3$. That gives
$z = -1 \pm \sqrt3 i$.

$$z \in \{\,2,\ -1 + \sqrt3 i,\ -1 - \sqrt3 i\,\}.$$

```python
my_roots = [2, -1 + sqrt(3)*I, -1 - sqrt(3)*I]
```

The temptation to divide the second equation by $b$ costs two roots out of three
here: you cannot divide by an expression that may be zero — exactly as in
trigonometric equations.

A pleasant observation: the three numbers found are precisely the cube roots of 8.
And so they should be: multiplying $z^2 = 2\bar z$ by $z$ gives
$z^3 = 2z\bar z = 2|z|^2$, and $|z| = 2$ for all three.
""")

md(r"""
## Solution 8 — the argument of a product

**(a)** Expand:

$$z_1z_2 = (1 + bi)\bigl((1 - b^2) - 2bi\bigr)
= (1 - b^2) - 2bi + bi(1-b^2) - 2b^2i^2.$$

Collect: the real part is $1 - b^2 + 2b^2 = 1 + b^2$, the imaginary part
$-2b + b - b^3 = -b(1 + b^2)$. So

$$z_1z_2 = (1 + b^2)(1 - bi).$$

**(b)** The factor $1 + b^2$ is **strictly positive**, so it does not affect the
argument:

$$\arg(z_1z_2) = \arg(1 - bi) = \frac{\pi}{4}.$$

The number $1 - bi$ has real part 1 and imaginary part $-b$. An argument of
$\frac{\pi}{4}$ means the parts are equal and both positive: $-b = 1$, that is,
$b = -1$.

```python
my_b8 = -1
```

Check: at $b = -1$ we get $z_1z_2 = 2(1 + i) = 2 + 2i$, and
$\arg(2+2i) = \frac{\pi}{4}$.
""")

md(r"""
## Solution 9 — the condition for being real

The modulus: $|zw| = |z||w| = 2 \cdot 8 = 16$.

The argument: $\arg(zw) = \arg z + \arg w = \dfrac{\pi}{5} - \dfrac{2k\pi}{5}
= \dfrac{(1 - 2k)\pi}{5}$.

A number is real exactly when its argument is a multiple of $\pi$:

$$\frac{(1-2k)\pi}{5} = n\pi \;\Longrightarrow\; 1 - 2k = 5n.$$

Go through the $n$: at $n = -1$ we get $1 - 2k = -5$, that is, $k = 3$ — a positive
integer. At $n = 1$ we get $k = -2$, at $n = 0$ a fraction. The smallest value that
works is $k = 3$.

Then $\arg(zw) = \dfrac{(1-6)\pi}{5} = -\pi$, and

$$zw = 16(\cos(-\pi) + i\sin(-\pi)) = -16.$$

```python
my_k = 3
my_zw = -16
```
""")

md(r"""
## Solution 10 — a square root through the parts

$$(a + bi)^2 = a^2 - b^2 + 2abi = \sqrt3 + i.$$

Equate the parts: $a^2 - b^2 = \sqrt3$ and $2ab = 1$.

**The short way.** Take the modulus of both sides of the original equality:
$|a+bi|^2 = |w|$, that is, $a^2 + b^2 = 2$. Together with $a^2 - b^2 = \sqrt3$ this
is a linear system in $a^2$ and $b^2$:

$$a^2 = \frac{2 + \sqrt3}{2}, \qquad b^2 = \frac{2 - \sqrt3}{2}.$$

**The direct way.** From $2ab = 1$ we get $b = \frac{1}{2a}$, and substituting gives
$a^2 - \frac{1}{4a^2} = \sqrt3$, that is, $4a^4 - 4\sqrt3\,a^2 - 1 = 0$. As a
quadratic in $a^2$:

$$a^2 = \frac{4\sqrt3 \pm \sqrt{48 + 16}}{8} = \frac{4\sqrt3 \pm 8}{8}
= \frac{\sqrt3 \pm 2}{2}.$$

The condition $a > 0$ leaves the plus sign, and both ways agree.

```python
my_a2 = (2 + sqrt(3))/2
my_b2 = (2 - sqrt(3))/2
```

Check: $a^2 - b^2 = \sqrt3$ ✓, and $2ab = 2\sqrt{a^2b^2}
= 2\sqrt{\frac{4-3}{4}} = 1$ ✓.
""")

md(r"""
## Solution 11 — the other roots of a cubic

The coefficients are real, so the conjugate $-1 - \sqrt3 i$ is a root as well. That
is the first answer and the first mark.

The third root $c$ is real (in a cubic the complex roots come as a pair). From the
sum of the roots:

$$(-1 + \sqrt3 i) + (-1 - \sqrt3 i) + c = -5 \;\Longrightarrow\; -2 + c = -5
\;\Longrightarrow\; c = -3.$$

Or from the product: $(-1+\sqrt3 i)(-1-\sqrt3 i)\,c = -12$, where the first factor is
$1 + 3 = 4$, so $4c = -12$ and $c = -3$.

$$z \in \{\,-1 + \sqrt3 i,\ -1 - \sqrt3 i,\ -3\,\}.$$

```python
my_rest = [-1 - sqrt(3)*I, -3]
```
""")

md(r"""
## Solution 12 — the task on the timer

The coefficients are real and two roots are given: $a + bi$ and $b + ai$. So there
are two more — their conjugates: $a - bi$ and $b - ai$.

**The sum of the roots** equals minus the coefficient of $z^3$, that is, $-4$:

$$(a+bi) + (a-bi) + (b+ai) + (b-ai) = 2a + 2b = -4
\;\Longrightarrow\; a + b = -2.$$

**The product of the roots** equals the constant term (the degree is even), that is,
400. The conjugate pairs give squared moduli:

$$(a+bi)(a-bi)\,(b+ai)(b-ai) = (a^2+b^2)(b^2+a^2) = (a^2+b^2)^2 = 400,$$

hence $a^2 + b^2 = 20$ (a modulus is non-negative, so only the plus sign).

Solve the system. From the first, $b = -2 - a$; substituting:

$$a^2 + (a+2)^2 = 20 \;\Longrightarrow\; 2a^2 + 4a - 16 = 0
\;\Longrightarrow\; a^2 + 2a - 8 = 0,$$

$$a = 2 \quad\text{or}\quad a = -4.$$

```python
my_a_values = [2, -4]
```

Check: at $a = 2$ we get $b = -4$, and $a^2 + b^2 = 4 + 16 = 20$ ✓. The pair
$(a, b) = (-4, 2)$ gives the same four roots in a different order, so both values of
$a$ really are possible.
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.12"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out = os.path.join(ROOT, 'practicum/number_algebra',
                   'practicum-a5-complex-forms.ipynb')
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, 'w') as fh:
    json.dump(nb, fh, ensure_ascii=False, indent=1)
print(f'cells: {len(cells)} -> {out}')
