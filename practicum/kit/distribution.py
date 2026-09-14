"""Распределение, заданное моделью: B(n, p), E и Var, выборка (D3).

Статистика — единственное место пакета, где темы ссылаются друг на друга в
обе стороны: вероятность события здесь считает и таблица, и нормальная
кривая, и плотность, а они в свою очередь дописывают сюда свои случаи.
Такие ссылки вперёд собраны в конце модуля отдельным импортом. Он стоит
последним, потому что при импорте нужны только уже определённые имена, а
имена из следующих модулей зовутся лишь изнутри функций.
"""

import itertools
import math

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .sequences import blank
from .probability import P, _Prob, _PROB_TOL


# ========================================================== распределение
# Двадцатое понятие равенства ответов: распределение складывается по значениям.
#
# Ответ опять вероятность, как в D2, но восстанавливать пространство из
# условий больше не нужно: вопрос называет его сам. X ~ B(n, p) — это
# n + 1 значение и вероятность каждого, и проверка знает только это.
# «Не больше шести» она складывает по значениям от нуля до шести, среднее —
# суммой k·P(X = k), дисперсию — суммой квадратов отклонений от него.
# Ни np, ни np(1 − p), ни 1 − (1 − p)ⁿ внутри не написано: все они
# получаются сложением, а не берутся.
#
# Главный промах темы — граница. «More than 6» начинается с семи, «fewer
# than 49» кончается на сорока восьми, «at least 10» включает десять,
# а калькулятор умеет только P(X ≤ k). Событие помнит, из каких сравнений
# собрано, и проверка сдвигает каждую границу по очереди: совпал ответ со
# сдвинутой — она говорит, какая граница и в какую сторону.

_DRAW_LIMIT = 2000       # дальше по числу испытаний проверка не идёт
_DRAW_SAY = {'==': '=', '<': '<', '<=': '≤', '>': '>', '>=': '≥'}
_DRAW_TOGGLE = {'<': '<=', '<=': '<', '>': '>=', '>=': '>', '==': '<='}


def _draw_agree(got, want):
    """Сходятся ли две вероятности — относительно, а не абсолютно.

    Общий допуск секций выше абсолютный для чисел меньше единицы, и для
    вероятности 0,00394 он принял бы 0,0036. Здесь малые вероятности —
    обычное дело (ровно 34 растения из ста — 0,0133), поэтому сверка
    относительная: 5·10⁻⁴ от самого числа или те же три значащие цифры.
    """
    try:
        one, two = sp.sympify(got), sp.sympify(want)
        if sp.simplify(one - two) == 0:
            return True
        left, right = float(one), float(two)
    except (sp.SympifyError, TypeError, ValueError, AttributeError):
        return False
    if right == 0:
        return abs(left) < 1e-12
    if abs(left - right) <= 5e-4 * abs(right):
        return True
    # ровно пополам в четвёртой цифре: 0,3375 честно округляется и в 0,337,
    # и в 0,338, а двоичная запись решает за человека
    if not (math.isfinite(left) and math.isfinite(right)):
        return False
    unit = 10 ** (math.floor(math.log10(abs(right))) - 2)
    scaled = abs(right) / unit
    if abs(scaled - math.floor(scaled) - 0.5) < 1e-9 and abs(left - right) <= unit / 2 * (1 + 1e-9):
        return True
    return sig(left, 3) == sig(right, 3)


class _Variable:
    """Случайная величина: набор значений и вероятность каждого.

    Общее у биномиальной модели D3 и таблицы D4. Сравнения возвращают
    события: `X >= 1`, `X == 5`, `X < Y`. Это не булевы значения, а
    множества значений, и `P(...)` их складывает. Арифметика с числом даёт
    aX + b, от которого берут среднее и дисперсию; сумма двух величин —
    новая величина, сложенная по парам значений.

    Осторожно: `==` здесь событие, а не сравнение объектов, поэтому
    величины сравнивают только через `is`.
    """

    name = 'X'
    inner = None
    p = None

    __hash__ = object.__hash__

    def _compare(self, rel, k):
        if not (k is Ellipsis or isinstance(k, _Variable)):
            k = sp.sympify(k)
        return _Draw(('leaf', self, rel, k))

    def __eq__(self, k):
        return self._compare('==', k)

    def __ne__(self, k):
        return ~self._compare('==', k)

    def __lt__(self, k):
        return self._compare('<', k)

    def __le__(self, k):
        return self._compare('<=', k)

    def __gt__(self, k):
        return self._compare('>', k)

    def __ge__(self, k):
        return self._compare('>=', k)

    def __mul__(self, a):
        return _Linear(self, a, 0)

    __rmul__ = __mul__

    def __truediv__(self, a):
        return _Linear(self, 1 / sp.sympify(a), 0)

    def __add__(self, b):
        if isinstance(b, _Variable):
            return _sum_of(self, b)
        return _Linear(self, 1, b)

    __radd__ = __add__

    def __sub__(self, b):
        return _Linear(self, 1, -sp.sympify(b))

    def __rsub__(self, b):
        return _Linear(self, -1, b)

    def __neg__(self):
        return _Linear(self, -1, 0)

    def rules(self):
        """Что обязано выполняться, чтобы величина была величиной."""
        return []


class _Trials(_Variable):
    """X ~ B(n, p): n независимых испытаний с вероятностью успеха p.

    Хранит только n, p и имя. Вероятность одного значения — `chance` —
    единственное место секции, где p возводится в степень: это само
    определение распределения, а не формула для ответа.
    """

    def __init__(self, n, p, name='X'):
        self.name = name
        self.inner = None
        if n is Ellipsis or p is Ellipsis:
            self.n, self.p = n, p
            return
        if isinstance(p, _Prob) and p.args and isinstance(p.args[0], _Draw):
            # успех здесь — событие над другой моделью: коробка, в которой
            # не меньше тридцати яблок. Помним её ради разбора промаха
            self.inner = _draw_vars(p.args[0].node)[0]
        self.n = sp.sympify(n)
        self.p = sp.sympify(p)
        if not (self.n.is_integer and self.n >= 0):
            raise ValueError(_t(f'число испытаний — целое неотрицательное, а не {n}',
                                f'the number of trials is a whole number, not {n}'))
        if self.p.is_number and not -1e-12 <= float(self.p) <= 1 + 1e-12:
            raise ValueError(_t(f'вероятность успеха лежит в [0, 1], а не {p}',
                                f'the probability of success lies in [0, 1], not {p}'))

    __hash__ = object.__hash__

    def blank(self):
        return self.n is Ellipsis or self.p is Ellipsis

    def values(self):
        return range(int(self.n) + 1)

    def chance(self, k, p=None):
        """P(X = k) по определению: сколькими способами, и вероятность каждого."""
        p = self.p if p is None else p
        return binomial(self.n, k) * p ** k * (1 - p) ** (self.n - k)

    def rules(self):
        return [(_t('вероятность успеха', 'the probability of success'), self.p, 'prob')]

    def __repr__(self):
        shown = f"{float(self.p):.10g}" if getattr(self.p, 'is_Float', False) else self.p
        return f"{self.name} ~ B({self.n}, {shown})"


def Bin(n, p, name='X'):
    """Биномиальная величина: `X = Bin(30, 0.05)` — это X ~ B(30, 0.05).

    Вероятность успеха можно брать из другого ответа: коробка с не менее
    чем тридцатью яблоками — это `Bin(10, P(box >= 30))`. Буква вместо p
    тоже разрешена — так ставят вопрос «найдите p, если Var(X) = 5,75».
    """
    return _Trials(n, p, name)


class _Linear:
    """aX + b — то, от чего берут среднее и дисперсию: Var(1 − 2X)."""

    def __init__(self, var, a, b):
        self.var, self.a, self.b = var, sp.sympify(a), sp.sympify(b)

    def __mul__(self, c):
        return _Linear(self.var, self.a * sp.sympify(c), self.b * sp.sympify(c))

    __rmul__ = __mul__

    def __truediv__(self, c):
        return self * (1 / sp.sympify(c))

    def __add__(self, c):
        if isinstance(c, (_Variable, _Linear)):
            raise TypeError(_t('aX + bY складывается из двух величин: сначала X + Y, '
                               'потом множитель',
                               'aX + bY is built from two variables: form X + Y first'))
        return _Linear(self.var, self.a, self.b + sp.sympify(c))

    __radd__ = __add__

    def __sub__(self, c):
        return _Linear(self.var, self.a, self.b - sp.sympify(c))

    def __rsub__(self, c):
        return _Linear(self.var, -self.a, sp.sympify(c) - self.b)

    def __neg__(self):
        return _Linear(self.var, -self.a, -self.b)

    def __repr__(self):
        name = self.var.name
        if not (self.a.is_number and self.b.is_number):
            return f"{self.b} + ({self.a})*{name}" if self.b != 0 else f"({self.a})*{name}"
        size = abs(self.a)
        head = name if size == 1 else f"{size}{name}"
        if self.b == 0:
            return head if self.a > 0 else f"-{head}"
        return f"{self.b} {'+' if self.a > 0 else '-'} {head}"


def _as_linear(item):
    if isinstance(item, _Variable):
        return _Linear(item, 1, 0)
    return item


class _Draw:
    """Событие над биномиальными величинами — дерево сравнений.

    Листья — сравнения вида X ≥ 1, узлы — «и», «или», «ровно одно из»,
    «не». Дерево хранится, а не сворачивается в множество значений, ради
    разбора неверного ответа: сдвинуть можно только ту границу, про
    которую известно, где она стоит.
    """

    def __init__(self, node):
        self.node = node

    @property
    def space(self):
        return _DRAWS

    def __and__(self, other):
        return _Draw(('and', self.node, other.node))

    def __or__(self, other):
        return _Draw(('or', self.node, other.node))

    def __xor__(self, other):
        return _Draw(('xor', self.node, other.node))

    def __invert__(self):
        return _Draw(('not', self.node))

    def __repr__(self):
        return _draw_say(self.node)


def _draw_say(node):
    kind = node[0]
    if kind == 'leaf':
        other = node[3].name if isinstance(node[3], _Variable) else node[3]
        if node[2] == 'from':
            return _t(f"{node[1].name} из {other}", f"{node[1].name} from {other}")
        return f"{node[1].name} {_DRAW_SAY[node[2]]} {other}"
    if kind in ('yes', 'no'):
        return kind
    if kind == 'not':
        return _t(f"не ({_draw_say(node[1])})", f"not ({_draw_say(node[1])})")
    word = {'and': _t('и', 'and'), 'or': _t('или', 'or'),
            'xor': _t('ровно одно из', 'exactly one of')}[kind]
    if kind == 'xor':
        return f"{word} ({_draw_say(node[1])}, {_draw_say(node[2])})"
    return f"{_draw_say(node[1])} {word} {_draw_say(node[2])}"


def _draw_vars(node, out=None):
    """Величины события в порядке появления, каждая один раз."""
    out = [] if out is None else out
    if node[0] == 'leaf':
        for var in (node[1], node[3]):
            if isinstance(var, _Variable) and not any(var is seen for seen in out):
                out.append(var)
    else:
        for child in node[1:]:
            _draw_vars(child, out)
    return out


def _draw_holds(node, values):
    """Выполняется ли событие при данных значениях величин."""
    kind = node[0]
    if kind == 'leaf':
        _, var, rel, k = node
        here = values[id(var)]
        if isinstance(k, _Variable):
            k = values[id(k)]
        return {'==': here == k, '<': here < k, '<=': here <= k,
                '>': here > k, '>=': here >= k}[rel]
    if kind == 'not':
        return not _draw_holds(node[1], values)
    left, right = _draw_holds(node[1], values), _draw_holds(node[2], values)
    return {'and': left and right, 'or': left or right,
            'xor': left != right}[kind]


def _draw_blank(node):
    return any(var.blank() for var in _draw_vars(node)) or any(
        leaf[3] is Ellipsis for _, leaf in _draw_leaves(node))


def _draw_chance(var, p_mode):
    """Вероятность успеха, какой её взяли: как есть, перепутанной или округлённой.

    У таблицы вероятности успеха нет — у неё своя вероятность каждого
    значения, и промахи с p к ней неприменимы.
    """
    if not isinstance(var, _Trials):
        return None
    if p_mode == 'swap':
        return 1 - var.p
    if p_mode == 'round' and var.p.is_number:
        return sp.Float(sig(var.p, 3))
    if p_mode == 'inner' and var.inner is not None:
        return var.inner.p
    return var.p


def _draw_mass(node, p_mode=None):
    """Вероятность события: сумма по всем значениям, при которых оно выполняется.

    Величины независимы — так поставлен каждый вопрос темы, — и вероятность
    набора значений есть произведение вероятностей каждого. Ничего, кроме
    P(X = k), здесь не используется.
    """
    variables = _draw_vars(node)
    running = sp.Integer(0)
    for combo in itertools.product(*[var.values() for var in variables]):
        values = {id(var): k for var, k in zip(variables, combo)}
        if not _draw_holds(node, values):
            continue
        weight = sp.Integer(1)
        for var, k in zip(variables, combo):
            weight = weight * var.chance(k, _draw_chance(var, p_mode))
        running = running + weight
    return running


class _DrawSpace:
    """То, что P(...) спрашивает у события: его вероятность."""

    def mass(self, event):
        return _draw_mass(event.node)


_DRAWS = _DrawSpace()


def _draw_prob(event, given=None):
    """P(...) для событий над биномиальными величинами."""
    nodes = [event.node] + ([] if given is None else [given.node])
    if any(_draw_blank(node) for node in nodes):
        return Ellipsis
    if any(_is_curve(node) for node in nodes):
        return _curve_prob(event, given)      # нормальная величина, D5
    for node in nodes:
        for var in _draw_vars(node):
            if getattr(var, 'stand_in', None) is not None:
                raise ValueError(_t(
                    f"о {var.name} известны только E и Var — вероятностей событий по ним не посчитать",
                    f"only E and Var of {var.name} are known — they do not give probabilities of events"))
    if given is None:
        return _Prob(_draw_mass(event.node), 'plain', (event,), f"P({event})")
    base = _draw_mass(given.node)
    if base == 0:
        raise ValueError(_t(f"условие {given} невозможно",
                            f"the condition {given} cannot happen"))
    joint = _draw_mass(('and', event.node, given.node))
    return _Prob(joint / base, 'given', (event, given), f"P({event} | {given})")


def _draw_leaves(node, path=()):
    """Все сравнения события вместе с тем, где они в дереве стоят."""
    if node[0] == 'leaf':
        return [(path, node)]
    found = []
    for i, child in enumerate(node[1:], start=1):
        found += _draw_leaves(child, path + (i,))
    return found


def _draw_swap(node, path, leaf):
    """То же дерево, где сравнение по адресу path заменено на leaf."""
    if not path:
        return leaf
    head, rest = path[0], path[1:]
    return node[:head] + (_draw_swap(node[head], rest, leaf),) + node[head + 1:]


def _draw_value(kind, target, condition=None, p_mode=None):
    """Вероятность, пересчитанная по дереву: безусловная или условная."""
    if kind == 'plain':
        return _draw_mass(target, p_mode)
    base = _draw_mass(condition, p_mode)
    if base == 0:
        return None
    return _draw_mass(('and', target, condition), p_mode) / base


def _boundary_words(leaf, moved):
    """Как назвать сдвинутую границу: какое сравнение и что с ним стало."""
    _, var, rel, k = leaf
    was, now = _draw_say(leaf), _draw_say(moved)
    if isinstance(k, _Variable):
        return _t(f"«{was}» и «{now}» различаются ничьими: равные значения "
                  f"посчитаны не с той стороны",
                  f"«{was}» and «{now}» differ by the ties: equal values "
                  f"are on the wrong side")
    if rel == '==':
        return _t(f"это P({now}): накопленная вероятность вместо вероятности "
                  f"одного значения — cdf там, где нужен pdf",
                  f"that is P({now}): a cumulative probability where a single "
                  f"value was asked — cdf where pdf was wanted")
    if rel in ('>', '<'):
        edge = k + 1 if rel == '>' else k - 1
        return _t(f"граница взята не так: «{was}» {'начинается' if rel == '>' else 'кончается'} "
                  f"на {edge}, а посчитано и значение {k}",
                  f"the boundary is off: «{was}» {'starts' if rel == '>' else 'stops'} "
                  f"at {edge}, and this counts {k} as well")
    return _t(f"граница взята не так: «{was}» включает само {k}, а здесь "
              f"посчитано «{now}»",
              f"the boundary is off: «{was}» includes {k} itself, and this "
              f"is «{now}»")


def _draw_slips(find):
    """Типовые промахи, собранные из самого события, а не из списка."""
    slips = {}
    kind = find.kind
    target = find.args[0].node
    condition = find.args[1].node if kind == 'given' else None
    want = _draw_value(kind, target, condition)

    if kind == 'given':
        slips[_t("условная вероятность взята в обратную сторону: посчитано "
                 "P(условие | событие)",
                 "the conditional is the wrong way round: that is "
                 "P(condition | event)")] = _draw_value('given', condition, target)
        slips[_t("это вероятность пересечения — делить на вероятность условия "
                 "ещё не стали",
                 "that is the intersection: it has not been divided by the "
                 "probability of the condition")] = \
            _draw_mass(('and', target, condition))
        alone = _draw_mass(target) / _draw_mass(condition)
        slips[_t("в числителе всё событие, а нужна только та его часть, что "
                 "лежит внутри условия",
                 "the numerator is the whole event, but only the part of it "
                 "inside the condition belongs there")] = alone
        for where, tree in (('condition', condition), ('target', target)):
            for path, leaf in _draw_leaves(tree):
                moved = ('leaf', leaf[1], _DRAW_TOGGLE[leaf[2]], leaf[3])
                changed = _draw_swap(tree, path, moved)
                value = (_draw_value('given', target, changed) if where == 'condition'
                         else _draw_value('given', changed, condition))
                inside = _t(" (в условии)", " (in the condition)") \
                    if where == 'condition' else ''
                slips[_boundary_words(leaf, moved) + inside] = value
    else:
        if target[0] == 'xor':
            left, right = target[1], target[2]
            slips[_t("это «хотя бы одно из двух»: случай, когда выполнены оба, "
                     "сюда не входит",
                     "that is «at least one of the two»: the case where both "
                     "happen does not belong here")] = _draw_mass(('or', left, right))
            slips[_t("сумма двух вероятностей считает случай «оба» дважды, "
                     "а его не надо считать вовсе",
                     "adding the two probabilities counts «both» twice, and it "
                     "should not be counted at all")] = \
                _draw_mass(left) + _draw_mass(right)
        for path, leaf in _draw_leaves(target):
            moved = ('leaf', leaf[1], _DRAW_TOGGLE[leaf[2]], leaf[3])
            slips[_boundary_words(leaf, moved)] = \
                _draw_mass(_draw_swap(target, path, moved))
        slips[_t("это вероятность противоположного события",
                 "that is the probability of the opposite event")] = 1 - want
        variables = _draw_vars(target)
        if len(variables) == 1 and isinstance(variables[0], _Trials):
            slips[_t("это вероятность одного испытания, а не события над всеми n",
                     "that is the probability for a single trial, not for the "
                     "event about all n of them")] = variables[0].p

    if any(var.inner is not None for var in _draw_vars(target)):
        slips[_t("во внешнюю модель подставлена вероятность внутреннего "
                 "испытания: одно испытание здесь — целая группа, и её успех "
                 "сам посчитан из внутренней модели",
                 "the outer model uses the inner trial's probability: one trial "
                 "here is a whole group, and its success was itself computed "
                 "from the inner model")] = \
            _draw_value(kind, target, condition, 'inner')

    if any(isinstance(var, _Trials) for var in _draw_vars(target)):
        slips[_t("успех и неудача перепутаны: посчитано с 1 − p вместо p",
                 "success and failure are swapped: this uses 1 − p instead of p")] = \
            _draw_value(kind, target, condition, 'swap')
    return {what: value for what, value in slips.items()
            if value is not None and not _draw_agree(value, want)}


def _chance_answer(label, got):
    """Ответ-вероятность как число, или None с объяснением."""
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        value = None
    if value is None or getattr(value, 'free_symbols', set()) \
            or not value.is_number or value.is_real is False:
        print(f"{NO} {label}: " + _t("вероятность это число",
                                     "a probability is a number"))
        return None
    if not -_PROB_TOL <= float(value) <= 1 + _PROB_TOL:
        print(f"{NO} {label}: " + _t(
            "вероятность не бывает меньше нуля или больше единицы",
            "a probability is never below zero or above one"))
        return None
    return value


def verify_binomial(label, got, find):
    """Ответ — вероятность события над биномиальными величинами.

    `find` пишут так, как печатает билет: `P(X > 6)`, `P(X == 34, given=X < 49)`,
    `P((R >= 1) ^ (S >= 1))` — «ровно один из двоих». Проверка складывает
    вероятности подходящих значений; эталона она не хранит.

    Ответ, посчитанный от промежуточной вероятности, округлённой до трёх
    значащих цифр, принимается с замечанием: схема оценивания так и делает
    («use of 0.239 results in…»), но привычку держать полное значение стоит
    назвать.

    Неверный ответ разбирается: сдвинутая граница — с указанием какая,
    накопленная вероятность вместо точечной, условная в обратную сторону,
    успех и неудача местами.
    """
    if _blank(label, got, find):
        return False
    if not isinstance(find, _Prob) or not isinstance(find.args[0], _Draw):
        print(f"{NO} {label}: " + _t(
            "нечего искать: событие строится из величин — Bin(...), Dist(...)",
            "nothing to find: the event is built from variables — Bin(...), Dist(...)"))
        return False
    value = _chance_answer(label, got)
    if value is None:
        return False
    want = sp.sympify(find)
    if _draw_agree(value, want):
        print(f"{OK} {label}")
        return True
    target = find.args[0].node
    condition = find.args[1].node if find.kind == 'given' else None
    rounded = _draw_value(find.kind, target, condition, 'round')
    if rounded is not None and not _draw_agree(rounded, want) and _draw_agree(value, rounded):
        print(f"{OK} {label}: " + _t(
            "сходится с вероятностью, округлённой по дороге до трёх цифр. "
            "Схема оценивания такое принимает, но промежуточное значение "
            "лучше держать полностью",
            "this matches a probability rounded to three figures on the way. "
            "The markscheme accepts it, but carry the full value next time"))
        return True
    for what, slip in _draw_slips(find).items():
        if _draw_agree(value, slip):
            print(f"{NO} {label}: {what}")
            return False
    if sig(value, 2) == sig(want, 2) and float(sig(value, 2)) == float(value):
        print(f"{NO} {label}: " + _t(
            "две значащие цифры. Схема оценивания без записи решения даёт за "
            "такое (M1)A0: нужны три",
            "two significant figures. Without working the markscheme gives "
            "(M1)A0 for that: three are needed"))
        return False
    print(f"{NO} {label}: " + _t("у этого распределения выходит другое",
                                 "this distribution gives something else"))
    return False


def _moment(kind, linear, p_mode=None):
    """Среднее или дисперсия aX + b — сложением по значениям X."""
    var, a, b = linear.var, linear.a, linear.b
    if isinstance(var, _Series):
        return var.moment(kind, a, b)          # значений бесконечно много, D4
    if isinstance(var, _Density) or (isinstance(var, _Mapped) and isinstance(var.base, _Density)):
        return _density_moment(kind, var, a, b)   # интеграл, а не сумма, D6
    p = _draw_chance(var, p_mode)
    if kind == 'square':                       # E((aX + b)²), для разбора промаха
        return sp.expand(sp.Add(*[(a * k + b) ** 2 * var.chance(k, p)
                                  for k in var.values()]))
    mean = sp.expand(sp.Add(*[(a * k + b) * var.chance(k, p) for k in var.values()]))
    if kind == 'mean':
        return mean
    spread = sp.Add(*[(a * k + b - mean) ** 2 * var.chance(k, p)
                      for k in var.values()])
    return sp.expand(spread)


def Expect(item):
    """E(aX + b), полученное сложением k·P(X = k). Буквой E занята e = 2,718…"""
    linear = _as_linear(item)
    if linear.var.blank():
        return Ellipsis
    return _Prob(_moment('mean', linear), 'mean', (linear,), f"E({linear})")


def Var(item):
    """Var(aX + b), полученная сложением квадратов отклонений от среднего."""
    linear = _as_linear(item)
    if linear.var.blank():
        return Ellipsis
    return _Prob(_moment('var', linear), 'var', (linear,), f"Var({linear})")


def SD(item):
    """Стандартное отклонение aX + b — корень из дисперсии, сложенной по значениям."""
    linear = _as_linear(item)
    if linear.var.blank():
        return Ellipsis
    return _Prob(sp.sqrt(_moment('var', linear)), 'sd', (linear,), f"SD({linear})")


def binompdf(n, p, k):
    """P(X = k) для X ~ B(n, p) — кнопка калькулятора, десятичной дробью."""
    if blank(n, p, k):
        return Ellipsis
    return sp.N(sp.sympify(P(Bin(n, p) == k)), 12)


def binomcdf(n, p, *bounds):
    """Накопленная вероятность, как на калькуляторе.

    `binomcdf(n, p, k)` — P(X ≤ k), как у TI. `binomcdf(n, p, a, b)` —
    P(a ≤ X ≤ b), как у Casio. Всё прочее — «больше», «хотя бы», «меньше» —
    калькулятор не умеет, и перевести в эти две формы надо самому.
    """
    if blank(n, p, *bounds):
        return Ellipsis
    X = Bin(n, p)
    if len(bounds) == 1:
        return sp.N(sp.sympify(P(X <= bounds[0])), 12)
    if len(bounds) == 2:
        return sp.N(sp.sympify(P((X >= bounds[0]) & (X <= bounds[1]))), 12)
    raise TypeError(_t('binomcdf(n, p, k) или binomcdf(n, p, a, b)',
                       'binomcdf(n, p, k) or binomcdf(n, p, a, b)'))


def _draw_roots(condition, var):
    """Корни условия на букву-вероятность, лежащие в [0, 1]."""
    expr = sp.sympify(condition)
    expr = expr.lhs - expr.rhs if isinstance(expr, sp.Equality) else expr
    expr = sp.expand(expr)
    try:
        found = sp.Poly(expr, var).nroots(n=30)
    except (sp.PolynomialError, sp.polys.polyerrors.PolificationFailed):
        found = sp.solve(expr, var)
    roots = []
    for root in found:
        number = complex(sp.N(root, 30))
        if abs(number.imag) < 1e-12 and -1e-12 <= number.real <= 1 + 1e-12:
            roots.append(sp.Float(number.real, 30))
    return sorted(roots)


def verify_parameter(label, got, condition, var):
    """Ответ — все значения вероятности успеха, при которых условие верно.

    `condition` пишут как в билете: `Eq(Var(Bin(25, p)), 5.75)`. Дисперсия
    складывается по значениям X с буквой p внутри и даёт многочлен от p;
    проверка ищет его корни сама, оставляет лежащие в [0, 1] и сверяет
    с ответом оба направления: лишних нет, потерянных нет.
    """
    if _blank(label, got, condition):
        return False
    given = list(got) if isinstance(got, (list, tuple, set)) else [got]
    roots = _draw_roots(condition, var)
    numbers = []
    for item in given:
        value = _chance_answer(label, item)
        if value is None:
            return False
        numbers.append(value)
    for value in numbers:
        if not any(_draw_agree(value, root) for root in roots):
            print(f"{NO} {label}: " + _t(
                f"при {var} = {sig(value, 6)} условие не выполняется",
                f"at {var} = {sig(value, 6)} the condition does not hold"))
            return False
    missing = [root for root in roots
               if not any(_draw_agree(value, root) for value in numbers)]
    if missing:
        paired = any(_draw_agree(1 - root, value) for root in missing for value in numbers)
        tail = _t(" Здесь p и 1 − p дают одно и то же: успех и неудачу можно "
                  "поменять местами, и разброс не изменится.",
                  " Here p and 1 − p give the same thing: swap success and "
                  "failure and the spread does not change.") if paired else ''
        print(f"{NO} {label}: " + _t(
            f"значения верны, но найдено не всё: условию отвечают {len(roots)}.",
            f"the values are right, but not all of them: {len(roots)} satisfy "
            f"the condition.") + tail)
        return False
    print(f"{OK} {label}")
    return True


def verify_moment(label, got, what, given=None, var=None, tables=(), count=False,
                  exact=False, places=None):
    """Ответ — E(aX + b), Var(aX + b) или SD(aX + b).

    Среднее проверка получает сложением k·P(X = k), дисперсию — сложением
    квадратов отклонений; ни np, ни np(1 − p), ни a²Var(X) внутри нет.

    `given` и `var` — когда буква в вопросе не дана, а задана условием:
    тогда проверка сама находит все допустимые значения и требует, чтобы
    ответ годился при каждом. Так Var(1 − 2X) проверяется, даже если p
    найдено неверно. У таблицы с буквами условие «вероятности складываются
    в единицу» добавляется само, и `given` бывает пустым списком.

    Ответ, посчитанный от буквы, округлённой по дороге до трёх значащих
    цифр или до целого, принимается с замечанием: схемы оценивания так и
    делают («accept 3.80 from their 3sf answer», «accept 362 to 370»).

    `tables` — другие таблицы, чьи буквы входят в условие: у P(X < Y) = 1/2
    складываться в единицу обязаны обе.

    Если в `what` осталась буква, которую никто не задавал, ответ — не
    число, а выражение от неё: «write down E(X) in terms of p». Тогда оно
    сверяется в нескольких значениях буквы.

    `count=True` — спрашивают оценку числа предметов («estimate the number
    of bags»): схема оценивания принимает и 7,66, и 8, и целое тогда не
    промах, а допустимая запись.

    У величины с плотностью (D6) среднее и дисперсия — интегралы, а буквы
    плотности находятся из того, что площадь под ней — единица: `given=[]`,
    `var=k`. `exact=True` — вопрос просит точное значение; `places=2` —
    ответ до цента, два знака после запятой.
    """
    if _blank(label, got, what):
        return False
    kind, linear = what.kind, what.args[0]
    unknowns = _as_unknowns(var)
    loose = sp.sympify(what).free_symbols - set(unknowns)
    if given is None and loose:
        return _moment_expression(label, got, what, sorted(loose, key=str))
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        value = None
    if value is None or getattr(value, 'free_symbols', set()) or not value.is_number:
        print(f"{NO} {label}: " + _t("ответ это число", "the answer is a number"))
        return False
    if kind in ('var', 'sd') and float(value) < 0:
        print(f"{NO} {label}: " + (_t("дисперсия не бывает отрицательной",
                                      "a variance is never negative") if kind == 'var' else
                                   _t("стандартное отклонение не бывает отрицательным",
                                      "a standard deviation is never negative")))
        return False
    if given is None:
        runs = [{}]
    else:
        runs, _ = _letter_runs(_as_conditions(given), unknowns,
                               [linear.var] + list(tables))
        runs = runs or []
    if not runs:
        names = ', '.join(str(u) for u in unknowns)
        print(f"{NO} {label}: " + _t(f"условию не отвечает ни одно {names}",
                                     f"no {names} satisfies the condition"))
        return False
    trials = isinstance(linear.var, _Trials)
    for run in runs:
        want = sp.sympify(what).subs(run)
        if _draw_agree(value, want):
            if exact and value.has(sp.Float):
                print(f"{NO} {label}: " + _t(
                    "вопрос просит точное значение, а это десятичная дробь",
                    "the question asks for the exact value, and this is a decimal"))
                return False
            if exact and abs(float(value) - float(want)) > 1e-9 * max(1.0, abs(float(want))):
                print(f"{NO} {label}: " + _t("это близко, но не точное значение",
                                             "that is close, but it is not the exact value"))
                return False
            if places is not None and (round(float(value), places) != round(float(want), places)
                                       or abs(float(value) - round(float(value), places)) > 1e-9):
                print(f"{NO} {label}: " + _t(
                    f"вопрос просит ответ с {places} знаками после запятой",
                    f"the question asks for {places} decimal places"))
                return False
            continue
        for rounded, how in _rounded_runs(run):
            near = sp.sympify(what).subs(rounded)
            if not _draw_agree(near, want) and _draw_agree(value, near):
                print(f"{OK} {label}: " + _t(
                    f"сходится с {how}, округлённым по дороге. Схема оценивания "
                    f"такое принимает, но промежуточное значение лучше держать "
                    f"полностью",
                    f"this matches {how} rounded on the way. The markscheme "
                    f"accepts it, but carry the full value next time"))
                return True
        plain = _Linear(linear.var, 1, 0)
        mean_x = _moment('mean', plain).subs(run)
        spread_x = _moment('var', plain).subs(run)
        slips = {}
        if kind == 'mean':
            if trials:
                slips[_t("это ожидаемое число неудач: успех и неудача перепутаны",
                         "that is the expected number of failures: success and "
                         "failure are swapped")] = \
                    _moment('mean', linear, 'swap').subs(run)
                slips[_t("это вероятность одного испытания, а не ожидаемое число",
                         "that is the probability for one trial, not the expected "
                         "number")] = linear.var.p.subs(run)
            slips[_t("постоянная потеряна", "the constant is lost")] = \
                linear.a * mean_x
            if isinstance(linear.var, _Density):
                shape = linear.var.shape(run)
                lo, hi = linear.var.support(shape)
                slips[_t("это ∫ x dx без плотности: каждое x умножают на f(x)",
                         "that is ∫ x dx with no density: each x is multiplied by "
                         "f(x)")] = math.fsum(
                    _quad(lambda p: float(linear.a.subs(run)) * p + float(linear.b.subs(run)), a, b)
                    for a, b, _ in shape if b > a)
                if not (math.isinf(lo) or math.isinf(hi)):
                    slips[_t("это середина промежутка: так бывает только у симметричной "
                             "плотности",
                             "that is the middle of the interval: that only works for a "
                             "symmetric density")] = linear.a * (lo + hi) / 2 + linear.b
            if isinstance(linear.var, _Table):
                listed = list(linear.var.values())
                slips[_t("это среднее значений без весов: каждое значение "
                         "умножают на его вероятность",
                         "that is the average of the values with no weights: each "
                         "value is multiplied by its own probability")] = \
                    sp.Add(*[linear.a * v + linear.b for v in listed]).subs(run) / len(listed)
            if linear.a != 1 or linear.b != 0:
                slips[_t(f"это E({linear.var.name}), а спрашивали E({linear})",
                         f"that is E({linear.var.name}), and the question asks for "
                         f"E({linear})")] = mean_x
        elif kind == 'sd':
            spread_y = _moment('var', linear).subs(run)
            slips[_t("это дисперсия: стандартное отклонение — корень из неё",
                     "that is the variance: the standard deviation is its square "
                     "root")] = spread_y
            slips[_t("это среднее, а не стандартное отклонение",
                     "that is the mean, not the standard deviation")] = \
                _moment('mean', linear).subs(run)
            if isinstance(linear.var, _Table) and linear.var.counts:
                size = sp.sympify(linear.var.size).subs(run)
                slips[_t("поделено на n − 1: это оценка по выборке, а стандартное "
                         "отклонение данных в IB делится на n",
                         "divided by n − 1: that is the sample estimate, and IB's "
                         "standard deviation of data divides by n")] = \
                    sp.sqrt(spread_y * size / (size - 1))
        else:
            slips[_t("это среднее, а не дисперсия",
                     "that is the mean, not the variance")] = \
                _moment('mean', linear).subs(run)
            slips[_t("это стандартное отклонение: дисперсия — его квадрат",
                     "that is the standard deviation: the variance is its "
                     "square")] = sp.sqrt(want)
            slips[_t("множитель при X не возведён в квадрат",
                     "the multiplier of X has not been squared")] = \
                abs(linear.a) * spread_x
            slips[_t("постоянная в дисперсию не входит: сдвиг не меняет разброса",
                     "a constant does not enter a variance: shifting does not "
                     "change the spread")] = linear.a * linear.a * spread_x + linear.b
            if not isinstance(linear.var, _Trials):
                square = _moment('square', linear).subs(run)
                slips[_t(f"это E({linear.var.name}²): квадрат среднего ещё не вычтен",
                         f"that is E({linear.var.name}²): the square of the mean has "
                         f"not been subtracted yet")] = _moment('square', plain).subs(run)
                mean_y = _moment('mean', linear).subs(run)
                slips[_t(f"это E(({linear})²): квадрат среднего ещё не вычтен",
                         f"that is E(({linear})²): the square of the mean has not "
                         f"been subtracted yet")] = square
                slips[_t("вычтено среднее, а не его квадрат",
                         "the mean was subtracted, not its square")] = square - mean_y
        for what_word, slip in slips.items():
            slip = sp.sympify(slip).subs(run)
            if not _draw_agree(slip, want) and _draw_agree(value, slip):
                print(f"{NO} {label}: {what_word}")
                return False
        if kind == 'mean' and value.is_integer and value == round(float(want)) and count:
            print(f"{OK} {label}: " + _t(
                f"оценка числа предметов: схема оценивания принимает и целое, и "
                f"{sig(want, 3)}",
                f"an estimate of a number of items: the markscheme accepts both the "
                f"whole number and {sig(want, 3)}"))
            return True
        if kind == 'mean' and value.is_integer and value == round(float(want)):
            print(f"{NO} {label}: " + _t(
                "ожидаемое число округлено до целого, а оно не обязано быть "
                "целым: это среднее, а не число, которое случится",
                "the expected number has been rounded to a whole number, and it "
                "does not have to be one: it is a mean, not a count that will "
                "happen"))
            return False
        print(f"{NO} {label}: " + _t("у этого распределения выходит другое",
                                     "this distribution gives something else"))
        return False
    print(f"{OK} {label}")
    return True


def verify_trials(label, got, family, holds=None, near=None, limit=_DRAW_LIMIT):
    """Ответ — число испытаний n.

    `family(n)` строит вероятность при данном n: `lambda n: P(Bin(n, 0.25) >= 1)`.
    Вопрос бывает двух видов:

      * `holds` — «наименьшее n, при котором…»: проверка перебирает n
        по порядку и останавливается на первом, где условие выполнено.
        Ни логарифма, ни 1 − (1 − p)ⁿ внутри нет — ровно таблица на
        калькуляторе, которую схема оценивания принимает наравне;
      * `near` — «вероятность приблизительно равна 0,367»: проверка ищет
        n, при котором вероятность округляется до того же числа.
    """
    if _blank(label, got):
        return False
    try:
        number = sp.sympify(got)
        whole = number.is_number and abs(float(number) - round(float(number))) < 1e-9
    except (sp.SympifyError, TypeError, AttributeError, ValueError):
        whole = False
    if not whole or float(number) < 1:
        print(f"{NO} {label}: " + _t(
            "n считает испытания: оно целое и положительное. Граница из "
            "логарифма ещё не ответ — ответ целое число по нужную сторону от неё",
            "n counts trials: it is a whole positive number. A boundary out of "
            "a logarithm is not the answer yet — the answer is the whole number "
            "on the right side of it"))
        return False
    got_n = int(round(float(number)))
    first = family(1)
    if first is Ellipsis:
        _blank(label, first)
        return False

    def at(i):
        return sp.N(sp.sympify(family(i)), 20)

    want, seen = None, {}
    for i in range(1, limit + 1):
        seen[i] = at(i)
        if holds is not None and holds(seen[i]):
            want = i
            break
        if near is not None and sig(seen[i], 3) == sig(near, 3):
            want = i
            break
    if want is None:
        print(f"{NO} {label}: " + _t(
            f"до n = {limit} такого числа испытаний нет",
            f"no number of trials up to {limit} does this"))
        return False
    if got_n == want:
        print(f"{OK} {label}")
        return True
    here = seen[got_n] if got_n in seen else at(got_n)
    if holds is not None and got_n < want:
        print(f"{NO} {label}: " + _t(
            f"при n = {got_n} условие ещё не выполнено: вероятность {sig(here, 6)}",
            f"at n = {got_n} the condition does not hold yet: the probability "
            f"is {sig(here, 6)}"))
    elif holds is not None:
        print(f"{NO} {label}: " + _t(
            "условие выполнено, но это n не наименьшее: при меньшем оно "
            "выполняется тоже",
            "the condition holds, but this n is not the least: it holds for a "
            "smaller one too"))
    else:
        print(f"{NO} {label}: " + _t(
            f"при n = {got_n} вероятность {sig(here, 3)}, а не {near}",
            f"at n = {got_n} the probability is {sig(here, 3)}, not {near}"))
    return False


# Ссылки вперёд: эти имена зовутся только изнутри функций, а модули,
# где они живут, сами импортируют этот. Поэтому импорт стоит в конце.
from .table import (  # noqa: E402
    _as_conditions, _as_unknowns, _letter_runs, _moment_expression,
    _rounded_runs, _Series, _sum_of, _Table,
)
from .normal import _curve_prob, _is_curve, _Mapped  # noqa: E402
from .density import _Density, _density_moment, _quad  # noqa: E402
