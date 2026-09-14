"""Вероятность пространством исходов (D2) и счёт перебором (D1).
"""

import itertools

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t


# --------------------------------------------------------------- вероятность
#
# Тринадцатое понятие равенства ответов, и первое, где ответ — просто число
# от нуля до единицы. Сверять такое с записанным эталоном было бы ровно тем,
# чего практикумы избегают, и проверять здесь надо не число, а то, откуда оно
# берётся: вопрос о вероятности задаёт **пространство**, а пространство
# определяет ответ однозначно.
#
# Условия вопроса — «P(A) = 0,65», «P(A|B) = 1/4», «A и B независимы» — это
# уравнения на веса исходов. Проверка решает их и вычисляет то, о чём
# спрашивают, по определению. Ни верного ответа, ни неверных она не хранит:
# и те, и другие выводятся из условия.


class _Event:
    """Событие — множество атомов пространства.

    Атом это одна клетка диаграммы Венна: у двух событий их четыре
    (A∩B, A∩B′, A′∩B, A′∩B′), у трёх восемь. Любое событие, какое можно
    записать через A и B, есть объединение атомов, поэтому пересечение,
    объединение и дополнение — операции над множествами индексов, и
    алгебру событий писать не приходится.

    Кроме самих атомов событие помнит, как оно составлено (`op`, `parts`).
    Это нужно не для вычисления, а для разбора неверного ответа: «в объединении
    пересечение посчитано дважды» — промах с именем, и назвать его можно
    только зная, что спрашивали именно про объединение.
    """

    def __init__(self, space, atoms, name, op='atom', parts=()):
        self.space = space
        self.atoms = frozenset(atoms)
        self.name = name
        self.op = op
        self.parts = tuple(parts)

    def __and__(self, other):
        return _Event(self.space, self.atoms & other.atoms,
                      f"{self.name} ∩ {other.name}", 'and', (self, other))

    def __or__(self, other):
        return _Event(self.space, self.atoms | other.atoms,
                      f"{self.name} ∪ {other.name}", 'or', (self, other))

    def __invert__(self):
        return _Event(self.space, self.space.all - self.atoms,
                      f"{self.name}′", 'not', (self,))

    def __repr__(self):
        return self.name


class _Space:
    """Пространство из n событий: 2**n атомов с неизвестными весами."""

    def __init__(self, names):
        self.names = list(names)
        self.size = 2 ** len(self.names)
        self.all = frozenset(range(self.size))
        self.weights = list(sp.symbols(f'w0:{self.size}'))

    def atom_of(self, index, name):
        """Событие номер index: атомы, в двоичном номере которых стоит его бит."""
        inside = [j for j in range(self.size) if (j >> index) & 1]
        return _Event(self, inside, name)

    def mass(self, event):
        return sp.Add(*[self.weights[j] for j in sorted(event.atoms)])


def events(names):
    """События пространства: `A, B = events('A B')`.

    Дальше их пишут так, как пишет экзамен: `A & B` — пересечение,
    `A | B` — объединение, `~A` — дополнение, `P(A, given=B)` — условная
    вероятность. Чему равны эти вероятности, проверка не знает; она узнаёт
    это из условий самого вопроса.
    """
    space = _Space(names.split())
    made = [space.atom_of(i, nm) for i, nm in enumerate(space.names)]
    return made[0] if len(made) == 1 else made


class _Prob:
    """P(...) — выражение через веса атомов, помнящее, о чём спросили.

    Помнить нужно ради разбора неверного ответа. Перепутанный порядок
    в P(A|B) — промах с именем, и назвать его можно, только зная, что
    спрашивали условную вероятность, а не какое-то число вообще.

    Арифметика возвращает обычные выражения sympy, поэтому условия вида
    `P(A) = 3*P(B)` пишутся так, как они напечатаны в билете.
    """

    def __init__(self, expr, kind, args, label):
        self.expr, self.kind, self.args, self.label = expr, kind, args, label

    def _sympy_(self):
        return self.expr

    def __add__(self, other):
        return self.expr + sp.sympify(other)

    __radd__ = __add__

    def __sub__(self, other):
        return self.expr - sp.sympify(other)

    def __rsub__(self, other):
        return sp.sympify(other) - self.expr

    def __mul__(self, other):
        return self.expr * sp.sympify(other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return self.expr / sp.sympify(other)

    def __rtruediv__(self, other):
        return sp.sympify(other) / self.expr

    def __neg__(self):
        return -self.expr

    def __repr__(self):
        return self.label


def P(event, given=None):
    """Вероятность события; `given=` делает её условной.

    `P(A & B)` — вероятность пересечения, `P(A | B)` — объединения,
    `P(A, given=B)` — то, что экзамен пишет как P(A|B). Разделение
    намеренное: вертикальная черта в Python значит объединение, и
    занимать её под условную вероятность значило бы завести запись,
    которую нельзя прочесть вслух так, как она напечатана.
    """
    if isinstance(event, _Draw) or isinstance(given, _Draw):
        return _draw_prob(event, given)      # биномиальные величины, D3
    space = event.space
    if given is None:
        return _Prob(space.mass(event), 'plain', (event,), f"P({event})")
    joint = space.mass(event & given)
    return _Prob(joint / space.mass(given), 'given', (event, given),
                 f"P({event} | {given})")


def _as_equation(item):
    """Условие вопроса → уравнение. Пара (что, чему равно) или готовое Eq."""
    if isinstance(item, (tuple, list)):
        left, right = item
        return sp.Eq(sp.sympify(left), sp.sympify(right))
    if isinstance(item, sp.Equality):
        return item
    return sp.Eq(sp.sympify(item), 0)


_PROB_TOL = 1e-9


def _feasible(run):
    """Веса атомов годятся: все действительны и лежат в [0, 1]."""
    for value in run.values():
        try:
            number = complex(sp.N(value, 30))
        except (TypeError, ValueError):
            return False
        if abs(number.imag) > _PROB_TOL:
            return False
        if number.real < -_PROB_TOL or number.real > 1 + _PROB_TOL:
            return False
    return True


def _solve_space(space, given):
    """Веса атомов из условий вопроса. Возвращает все допустимые решения.

    Условий бывает меньше, чем атомов, и часть весов остаётся буквой.
    Это не значит, что вопрос плох: у мая 2025 TZ2 даны P(A∪B) и P(A∩B′),
    и четвёртая клетка диаграммы действительно не определена — а P(B),
    о котором спрашивают, определено, потому что от неё не зависит.
    Поэтому решение возвращается как есть, а определённость проверяется
    у самого ответа, а не у пространства.
    """
    equations = [sp.Eq(sp.Add(*space.weights), 1)]
    equations += [_as_equation(item) for item in given]
    try:
        found = sp.solve(equations, space.weights, dict=True)
    except (NotImplementedError, TypeError):
        found = []
    runs = []
    for solution in found:
        run = {w: sp.simplify(solution.get(w, w)) for w in space.weights}
        fixed = {w: v for w, v in run.items()
                 if not (v.free_symbols & set(space.weights))}
        if _feasible(fixed):
            runs.append(run)
    return runs


def _value(expr, run):
    return sp.simplify(sp.sympify(expr).subs(run))


def _same_number(one, two, tol=5e-4):
    """Числа сходятся. Допуск — три значащие цифры, как их принимает экзамен."""
    try:
        left, right = complex(sp.N(one, 30)), complex(sp.N(two, 30))
    except (TypeError, ValueError):
        return False
    if abs(left.imag) > _PROB_TOL or abs(right.imag) > _PROB_TOL:
        return False
    scale = max(1.0, abs(right.real))
    return abs(left.real - right.real) <= tol * scale


def _prob_slips(find, run):
    """Типовые промахи, собранные из самого вопроса, а не из списка.

    Каждый строится тем же определением, применённым не так, как оно
    устроено: условная вероятность в обратную сторону, объединение без
    вычитания пересечения, пересечение как произведение там, где
    независимости никто не обещал.
    """
    slips = {}
    if not isinstance(find, _Prob):
        return slips

    if find.kind == 'given':
        target, condition = find.args
        slips[_t("условная вероятность взята в обратную сторону: "
                 "посчитано P(условие | событие)",
                 "the conditional is the wrong way round: "
                 "that is P(condition | event)")] = \
            _value(P(condition, given=target), run)
        slips[_t("это вероятность пересечения — делить на вероятность "
                 "условия ещё не стали",
                 "that is the intersection: it has not been divided by "
                 "the probability of the condition")] = \
            _value(P(target & condition), run)
    else:
        event, = find.args
        if event.op == 'and':
            left, right = event.parts
            slips[_t("вероятности перемножены, а независимость в условии "
                     "не обещана",
                     "the probabilities are multiplied, but the question "
                     "never promised independence")] = \
                _value(sp.sympify(P(left)) * sp.sympify(P(right)), run)
        if event.op == 'or':
            left, right = event.parts
            slips[_t("пересечение посчитано дважды: из суммы его надо вычесть",
                     "the intersection is counted twice: the sum has to "
                     "lose it once")] = \
                _value(sp.sympify(P(left)) + sp.sympify(P(right)), run)

    slips[_t("это вероятность противоположного события",
             "that is the probability of the opposite event")] = \
        _value(1 - sp.sympify(find), run)
    # промах, который сам остался с неизвестным весом, назвать нельзя
    return {what: value for what, value in slips.items()
            if not value.free_symbols}


def _report_probability(label, got, want, slips):
    """Общий разбор ответа-вероятности: сошлось, или как именно не сошлось."""
    try:
        answer = sp.sympify(got)
    except (sp.SympifyError, TypeError):
        print(f"{NO} {label}: " + _t("ответ не разобран как число",
                                     "the answer is not a number"))
        return False
    number = complex(sp.N(answer, 30))
    if abs(number.imag) > _PROB_TOL or not -_PROB_TOL <= number.real <= 1 + _PROB_TOL:
        print(f"{NO} {label}: " + _t(
            "вероятность не бывает меньше нуля или больше единицы",
            "a probability is never below zero or above one"))
        return False
    if _same_number(answer, want):
        print(f"{OK} {label}")
        return True
    for what, value in slips.items():
        if value is not None and _same_number(answer, value):
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t(
        "не совпадает с тем, что даёт пространство из условия",
        "that is not what the space in the question gives"))
    return False


def _polytope_extreme(space, given, target, which):
    """Крайнее значение линейной величины на множестве допустимых весов.

    Условий здесь меньше, чем весов, и пространство определено не
    однозначно — вопрос ставится именно так: «наименьшее возможное
    значение P(A∩B)». Множество допустимых весов это выпуклый многогранник
    (сумма единица, равенства вопроса, каждый вес неотрицателен), а
    крайние значения линейной величины на многограннике достигаются
    в вершинах. Вершины перебираются честно: занулить подходящее число
    весов и решить оставшуюся линейную систему.
    """
    weights = space.weights
    base = [sp.Eq(sp.Add(*weights), 1)] + [_as_equation(item) for item in given]
    best = None
    free = len(weights) - len(base)
    free = max(free, 0)
    for zeros in itertools.combinations(range(len(weights)), free):
        system = base + [sp.Eq(weights[j], 0) for j in zeros]
        try:
            solution = sp.solve(system, weights, dict=True)
        except (NotImplementedError, TypeError):
            continue
        for one in solution:
            run = {w: sp.simplify(one.get(w, w)) for w in weights}
            if any(run[w].free_symbols & set(weights) for w in weights):
                continue
            if not _feasible(run):
                continue
            here = _value(target, run)
            if best is None:
                best = here
            elif which == 'min' and sp.N(here) < sp.N(best):
                best = here
            elif which == 'max' and sp.N(here) > sp.N(best):
                best = here
    return best


def verify_event(label, got, given, find, extreme=None):
    """Ответ — вероятность, а пространство задано условиями вопроса.

    `given` перечисляет то, что сказано в билете: пары (что, чему равно)
    или готовые равенства вроде `Eq(P(A & B), P(A)*P(B))` для независимости.
    Проверка решает эти условия как уравнения на веса атомов и вычисляет
    `find` по определению — эталона она не хранит.

    Когда ответ неверен, проверка не ограничивается словом «неверно». Она
    строит из того же пространства именные промахи темы — условная
    вероятность в обратную сторону, объединение без вычитания пересечения,
    независимость там, где её не обещали, — и, если написанное совпало
    с одним из них, называет его.

    `extreme='min'` или `'max'` — для вопросов, где условий заведомо мало
    и спрашивают крайнее возможное значение.
    """
    if _blank(label, got):
        return False
    space = find.args[0].space if isinstance(find, _Prob) else None
    if space is None:
        print(f"{NO} {label}: " + _t("нечего искать", "nothing to find"))
        return False

    if extreme is not None:
        want = _polytope_extreme(space, given, sp.sympify(find), extreme)
        if want is None:
            print(f"{NO} {label}: " + _t(
                "условия вопроса не дают ни одного допустимого пространства",
                "the conditions allow no valid space at all"))
            return False
        return _report_probability(label, got, want, {})

    runs = _solve_space(space, given)
    if not runs:
        print(f"{NO} {label}: " + _t(
            "условия вопроса не дают ни одного допустимого пространства",
            "the conditions allow no valid space at all"))
        return False
    wants = [_value(find, run) for run in runs]
    loose = [w for w in wants if w.free_symbols & set(space.weights)]
    if loose or (len(wants) > 1
                 and not all(_same_number(w, wants[0]) for w in wants[1:])):
        print(f"{NO} {label}: " + _t(
            "условий не хватает: они допускают разные ответы",
            "the conditions are not enough: they allow different answers"))
        return False
    return _report_probability(label, got, wants[0], _prob_slips(find, runs[0]))


def verify_independence(label, got, given, a, b):
    """Ответ — два числа, которые сравнивают, решая вопрос о независимости.

    Вердикт «зависимы» или «независимы» сам по себе — монета: угадать его
    можно и не считая. Схема оценивания и не даёт за него балла отдельно:
    R-балл зависит от предыдущего, а предыдущий стоит на вычислении
    P(A)·P(B) и P(A∩B). Поэтому в ячейке пишут именно эти два числа,
    в этом порядке, а вывод из них следует сам.
    """
    if _blank(label, got):
        return False
    if not isinstance(got, (list, tuple)) or len(got) != 2:
        print(f"{NO} {label}: " + _t(
            "нужны два числа: произведение P(A)·P(B) и вероятность P(A∩B)",
            "two numbers are wanted: the product P(A)·P(B) and P(A∩B)"))
        return False
    space = a.space
    runs = _solve_space(space, given)
    if not runs:
        print(f"{NO} {label}: " + _t(
            "условия вопроса не дают ни одного допустимого пространства",
            "the conditions allow no valid space at all"))
        return False
    run = runs[0]
    product = _value(sp.sympify(P(a)) * sp.sympify(P(b)), run)
    joint = _value(P(a & b), run)
    if not _same_number(got[0], product):
        print(f"{NO} {label}: " + _t(
            "первое число — не произведение P(A)·P(B)",
            "the first number is not the product P(A)·P(B)"))
        return False
    if not _same_number(got[1], joint):
        print(f"{NO} {label}: " + _t(
            "второе число — не вероятность пересечения P(A∩B)",
            "the second number is not the intersection P(A∩B)"))
        return False
    verdict = _t("независимы", "independent") if _same_number(product, joint) \
        else _t("зависимы", "not independent")
    print(f"{OK} {label}: " + _t(f"числа верны, и они говорят: {verdict}",
                                 f"both numbers are right, and they say: {verdict}"))
    return True


def verify_probability(label, got, space, find, given=None, total=1):
    """Ответ — вероятность, а пространство выписано исходами и весами.

    Там, где событий два или три, пространство восстанавливается из условий
    (`verify_event`). Там, где вопрос про дерево, про последовательные
    вынимания без возвращения или про равновозможные наборы, исходы проще
    перечислить: `space` — это словарь «исход → вес». Проверка складывает
    веса нужных исходов, а не сверяет число с эталоном, и первым делом
    проверяет, что все веса вместе дают единицу: неверно переписанное
    дерево ловится именно здесь.

    `find` и `given` — либо предикат на исходе, либо набор исходов.
    """
    if _blank(label, got):
        return False
    weights = {key: sp.sympify(w) for key, w in space.items()}
    whole = sp.simplify(sp.Add(*weights.values()))
    if sp.simplify(whole - total) != 0:
        print(f"{NO} {label}: " + _t(
            f"веса исходов дают {whole}, а не {total} — пространство выписано неверно",
            f"the outcomes weigh {whole}, not {total} — the space is wrong"))
        return False

    def pick(rule):
        if rule is None:
            return set(weights)
        if callable(rule):
            return {key for key in weights if rule(key)}
        return {key for key in weights if key in set(rule)}

    inside, condition = pick(find), pick(given)
    hit = sp.simplify(sp.Add(*[weights[k] for k in inside & condition]) or 0)
    base = sp.simplify(sp.Add(*[weights[k] for k in condition]) or 0)
    if base == 0:
        print(f"{NO} {label}: " + _t("условие невозможно",
                                     "the condition cannot happen"))
        return False
    want = sp.simplify(hit / base)

    slips = {}
    if given is not None:
        back = sp.Add(*[weights[k] for k in inside]) or 0
        slips[_t("условная вероятность взята в обратную сторону",
                 "the conditional is the wrong way round")] = \
            sp.simplify(hit / back) if back != 0 else None
        slips[_t("это вероятность пересечения — делить на вероятность "
                 "условия ещё не стали",
                 "that is the intersection: it has not been divided by "
                 "the probability of the condition")] = hit
    slips[_t("это вероятность противоположного события",
             "that is the probability of the opposite event")] = 1 - want
    return _report_probability(label, got, want, slips)


# ------------------------------------------------------------------- счёт
#
# Четырнадцатое понятие равенства ответов, и второе подряд, где ответ —
# просто число. У вероятности это было число между нулём и единицей, и
# проверялось оно устройством пространства. У счёта это целое число, и
# проверяется оно тем же самым, доведённым до конца: **объекты
# пересчитываются**.
#
# Эталона снова нет. Ноутбук передаёт проверке не ответ, а описание того,
# что считают: как выглядит объект и что значит «подходит». Проверка
# перебирает и считает сама. Совпало — значит, одно и то же число получено
# двумя разными путями: формулой у студента и перебором у проверки, а
# формулу перебор не знает.
#
# Перебор влезает не всегда: 15! — это 1,3·10¹², и столько объектов не
# переберёт никакой ноутбук. Тогда перечисляются не все объекты, а те, о
# ком идёт речь: в вопросе про десятерых детей за десятью партами
# ограничение касается четверых, и перебираются 5040 способов посадить
# этих четверых, а остальные шестеро дают множитель 6!. Ход тот же, каким
# считает экзаменуемый, но стоит он в проверке, а не в ответе, и на ответ
# не намекает — `each` в подписи не виден.

# Множитель 2! разобран отдельной парой сообщений ниже — про порядок
# внутри пары, — поэтому здесь двойка лишняя: до неё бы не дошло.
_COUNT_FACTORS = tuple(range(3, 11))


def _as_count(value):
    """Ответ-счёт как целое число, или None, если это не целое число."""
    try:
        number = sp.nsimplify(sp.sympify(value))
    except (sp.SympifyError, TypeError, AttributeError):
        return None
    if getattr(number, 'free_symbols', set()):
        return None
    if not number.is_number or not number.is_real:
        return None
    return int(number) if sp.Integer(int(number)) == number else None


def _count_slips(total, matched, each):
    """Типовые промахи, собранные из самого перебора, а не из списка.

    Каждый — то же множество, посчитанное не так, как просили: без
    ограничения, ровно наоборот, без множителя за неупомянутых.
    """
    want = matched * each
    slips = {}
    if matched != total:
        slips[_t("ограничение из условия не учтено: это все объекты подряд",
                 "the restriction is missing: that is every object there is")] \
            = total * each
        slips[_t("посчитано ровно то, что условие запрещает",
                 "that is the count of exactly what the question forbids")] \
            = (total - matched) * each
    if each != 1:
        slips[_t("остальные ещё не расставлены: не хватает множителя",
                 "the others have not been arranged yet: a factor is missing")] \
            = matched
    slips[_t("каждый набор посчитан дважды: порядок внутри пары "
             "здесь не различают",
             "every selection is counted twice: the order inside the pair "
             "does not count here")] = want * 2
    if want % 2 == 0:
        slips[_t("порядок внутри пары не посчитан: её можно поставить "
                 "двумя способами",
                 "the order inside the pair is missing: it can go two ways")] \
            = want // 2
    for size in _COUNT_FACTORS:
        step = sp.factorial(size)
        if want % step == 0:
            slips[_t(f"ответ меньше верного в {size}! раз: где-то потерян "
                     f"порядок внутри {size} объектов",
                     f"the answer is {size}! times too small: the order "
                     f"inside {size} objects has been dropped")] \
                = want // step
        slips[_t(f"ответ больше верного в {size}! раз: где-то посчитан "
                 f"порядок, которого в вопросе нет",
                 f"the answer is {size}! times too large: an order the "
                 f"question does not ask for has been counted")] \
            = want * step
    return slips


def verify_count(label, got, objects, keep=None, each=1):
    """Ответ — сколько объектов, и он проверяется их пересчётом.

    `objects` — то, что перебирают: любой итератор объектов или просто
    их число, когда перебирать нечего. `keep` — что значит «подходит»:
    предикат на объекте. `each` — сколько штук стоит за одним
    перечисленным объектом; он нужен там, где перебирать всё физически
    нельзя, и перечисляют только то, чего касается ограничение.

    Эталон здесь не хранится и не может: проверка складывает единицы,
    а не сверяет число с записанным.
    """
    if _blank(label, got):
        return False
    answer = _as_count(got)
    if answer is None:
        print(f"{NO} {label}: " + _t(
            "сколько-нибудь штук — это целое число",
            "a number of things is a whole number"))
        return False
    if answer < 0:
        print(f"{NO} {label}: " + _t("объектов не бывает меньше нуля",
                                     "there is no negative number of things"))
        return False

    if isinstance(objects, (int, sp.Integer)):
        if keep is not None:
            raise ValueError(_t(
                'verify_count: фильтру нужен перебор, а не готовое число',
                'verify_count: keep needs objects to enumerate, not a number'))
        total = matched = int(objects)
    else:
        total = matched = 0
        for item in objects:
            total += 1
            if keep is None or keep(item):
                matched += 1
    if total == 0:
        print(f"{NO} {label}: " + _t("перебирать нечего: объектов ноль",
                                     "nothing to enumerate: no objects at all"))
        return False

    want = matched * each
    if answer == want:
        print(f"{OK} {label}")
        return True
    for what, value in _count_slips(total, matched, each).items():
        if value == answer:
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t(
        "столько объектов не насчитывается: перебор даёт другое число",
        "the enumeration does not come to that many"))
    return False


def verify_count_law(label, got, var, count, sizes):
    """Ответ — выражение от n, и оно проверяется пересчётом при малых n.

    Экзамен просит «write down an expression for the number of ways», и
    сверять такое с записанным ⁿC₃ значило бы сверять запись. Проверка
    вместо этого берёт маленькие n, пересчитывает объекты перебором и
    смотрит, то же ли число даёт выражение. Любая верная форма проходит:
    ⁿC₃, n!/(3!(n−3)!) и n(n−1)(n−2)/6 — одно и то же выражение.

    Сообщение называет то n, на котором разошлось, и сколько объектов
    там на самом деле. Это подсказка, но подсказка про n = 5, а спросили
    про общее n — как и в verify_roots, где сообщение говорит, около
    какой точки пропажа, но не называет самого корня.
    """
    if _blank(label, got):
        return False
    try:
        expr = sp.sympify(got)
    except (sp.SympifyError, TypeError):
        print(f"{NO} {label}: " + _t("ответ не разобран как выражение",
                                     "the answer is not an expression"))
        return False
    extra = expr.free_symbols - {var}
    if extra:
        names = ', '.join(sorted(str(s) for s in extra))
        print(f"{NO} {label}: " + _t(
            f"в ответе осталась лишняя буква: {names}",
            f"the answer still carries an extra letter: {names}"))
        return False
    for size in sizes:
        real = int(count(size))
        mine = sp.simplify(expr.subs(var, size))
        if not mine.is_number or sp.simplify(mine - real) != 0:
            print(f"{NO} {label}: " + _t(
                f"при {var} = {size} объектов {real}, "
                f"а выражение даёт {mine}",
                f"at {var} = {size} there are {real} objects, "
                f"but the expression gives {mine}"))
            return False
    print(f"{OK} {label}")
    return True


# Ссылки вперёд: эти имена зовутся только изнутри функций, а модули,
# где они живут, сами импортируют этот. Поэтому импорт стоит в конце.
from .distribution import _Draw, _draw_prob  # noqa: E402
