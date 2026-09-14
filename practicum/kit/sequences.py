"""Последовательности (A1, A2): член и сумма порождаются шагом, а не формулой.

`blank` отсюда же — пустое место в ответе; им пользуется и статистика.
"""

import sympy as sp

from .core import *  # noqa: F401,F403 — имена ноутбука общие для всего kit
from .core import _blank, _t
from .geometry import _near


# ===================================================== последовательность
# Шестнадцатое понятие равенства ответов: последовательность порождается.
#
# Эталона снова нет. Проверка получает не ответ и не формулу, а правило:
# первый член и шаг. Член находится сложением шага n−1 раз, сумма —
# сложением первых n членов. Ни u₁+(n−1)d, ни n/2(2u₁+(n−1)d) внутри
# проверки не написано ни разу, и потому 2n+3, 5+2(n−1) и n+(n+3)
# проходят одинаково.
#
# Работает в обе стороны, и в этой теме обратный ход — половина заданий.
# Прямой: прогрессия известна, ответ — её член или сумма. Обратный: член
# известен из условия, а прогрессию строят из ответа, и она обязана этому
# члену отвечать. Так проверяется «найдите первый член и разность» —
# самый частый вопрос темы, у которого ответов два и оба в одной строке.

_SEQ_TOL = 5e-4          # три значащие цифры — столько же принимает экзамен
_SEQ_WALK = 4000         # дальше по прогрессии проверка не идёт
_SEQ_SAMPLES = (1, 2, 3, 5, 8)   # значения n, на которых сверяется формула
_SEQ_TAIL = 1e-9         # хвост, ниже которого бесконечное сложение останавливается
_SEQ_EXACT = 1e-8        # допуск там, где вопрос просит точное значение


def progression(first, step):
    """Арифметическая прогрессия как правило, а не как формула.

    first — первый член, step — общая разность. Проверка не хранит из
    этого ничего, кроме пары чисел: члены она получает сложением.

    Оба аргумента разрешено брать из ещё не заполненного ответа, и тогда
    прогрессии просто нет: ноутбук обязан проходиться сверху вниз
    и пустым.
    """
    if any(v is Ellipsis for v in (first, step)):
        return ('ap', Ellipsis, Ellipsis)
    return ('ap', sp.sympify(first), sp.sympify(step))


def geometric(first, ratio):
    """Геометрическая прогрессия как правило, а не как формула.

    first — первый член, ratio — знаменатель. Проверка не хранит из
    этого ничего, кроме пары значений: члены она получает умножением.
    Ни u₁r^(n−1), ни u₁(rⁿ−1)/(r−1) внутри неё не написано ни разу.

    Знаменателю разрешено быть выражением: у ряда 1 + x + x² + … он
    равен x, и тогда проверке передают, при каких значениях буквы
    сверяться.
    """
    if any(v is Ellipsis for v in (first, ratio)):
        return ('gp', Ellipsis, Ellipsis)
    return ('gp', sp.sympify(first), sp.sympify(ratio))


def _kind(seq):
    """'ap' или 'gp' — какого рода прогрессия передана."""
    if not isinstance(seq, (list, tuple)) or len(seq) != 3 \
            or seq[0] not in ('ap', 'gp'):
        raise ValueError(_t(
            'последовательность задаётся progression(...) или geometric(...)',
            'a sequence is given by progression(...) or geometric(...)'))
    return seq[0]


def _run(seq, count):
    """Первые count членов прогрессии: арифметическая складывает, геометрическая умножает."""
    kind = _kind(seq)
    value, out = seq[1], []
    for _ in range(count):
        out.append(value)
        value = value + seq[2] if kind == 'ap' else value * seq[2]
    return out


def _fixed(seq, run):
    """Та же прогрессия со подставленными значениями буквы."""
    if blank(seq[1], seq[2]):
        return seq
    return (seq[0], sp.sympify(seq[1]).subs(run), sp.sympify(seq[2]).subs(run))


def blank(*values):
    """Остался ли хоть в одном ответе placeholder `...`.

    Правило прогрессии в ноутбуке постоянно собирают из ответа, и
    собирать бывает ещё не из чего. Явная проверка нужна там, где
    выражение считается до вызова verify_*: `q*n**2` с Ellipsis
    внутри падает раньше, чем проверка успеет напечатать белый квадрат.
    """
    return any(value is Ellipsis for value in values)


def term(seq, n):
    """n-й член прогрессии, полученный сложением.

    Нужен там, где условие говорит не про один член: «шестой и
    двенадцатый в сумме дают двадцать четыре» — это term(mine, 6)
    и term(mine, 12), сложенные в самой ячейке.
    """
    if blank(seq[1], seq[2]):
        return Ellipsis
    return _run(seq, int(n))[-1]


def total(seq, n):
    """Сумма первых n членов прогрессии, полученная сложением."""
    if blank(seq[1], seq[2]):
        return Ellipsis
    return sp.Add(*_run(seq, int(n)))


def _converges(seq):
    """Убывает ли геометрическая прогрессия так, что её можно сложить всю.

    Условие |r| < 1 здесь не напоминание из учебника, а то, без чего
    сложению негде остановиться: проверка складывает члены, пока хвост
    не станет меньше допуска, и у расходящегося ряда такого места нет.
    """
    if _kind(seq) != 'gp':
        return False
    ratio = sp.sympify(seq[2])
    if not ratio.is_number:
        return False
    return abs(float(sp.N(ratio))) < 1


def infinite(seq):
    """Сумма всей геометрической прогрессии, полученная сложением.

    Складывает член за членом, пока и очередной член, и оценка всего
    оставшегося хвоста не станут меньше _SEQ_TAIL. Формулы u₁/(1−r)
    внутри нет: она получается, а не берётся.

    Возвращает None, если складывать нечего — прогрессия не убывает.
    """
    if blank(seq[1], seq[2]):
        return Ellipsis
    if not _converges(seq):
        return None
    ratio = float(sp.N(sp.sympify(seq[2])))
    running, value = sp.Integer(0), sp.sympify(seq[1])
    for _ in range(_SEQ_WALK):
        running = running + value
        value = value * seq[2]
        rest = abs(float(sp.N(value))) / (1 - abs(ratio))
        if rest < _SEQ_TAIL:
            break
    return running


def _index(label, n):
    """Номер члена: целое и положительное, иначе это не номер.

    Схема оценивания ноября 2025 года прощает ответ «n = 0, 13»
    отдельной оговоркой — значит, соблазн назвать номером ноль
    достаточно частый, чтобы его назвать вслух.
    """
    try:
        value = sp.sympify(n)
    except (sp.SympifyError, TypeError, AttributeError):
        value = None
    if value is None or getattr(value, 'free_symbols', set()) \
            or not value.is_number:
        print(f"{NO} {label}: " + _t("номер члена это число",
                                     "the index of a term is a number"))
        return None
    if not _near(value, sp.Integer(round(float(value))), _SEQ_TOL) \
            or float(value) < 1:
        print(f"{NO} {label}: " + _t(
            "номер считает члены: он обязан быть целым и положительным",
            "an index counts terms: it has to be a whole number, and at "
            "least one"))
        return None
    if float(value) > _SEQ_WALK:
        print(f"{NO} {label}: " + _t(
            f"дальше {_SEQ_WALK}-го члена проверка не идёт",
            f"the check does not walk past term {_SEQ_WALK}"))
        return None
    return int(round(float(value)))


def _as_value(label, got, want, what):
    """Ответ, приведённый к выражению, или None.

    Буква в ответе допустима ровно тогда, когда она есть и в самой
    прогрессии: у последовательности ln x, ⅔ln x, ⅓ln x суммы числами
    не бывают. А там, где прогрессия числовая, выражение с буквой —
    не ответ, и об этом стоит сказать прямо.
    """
    try:
        value = sp.sympify(got)
    except (sp.SympifyError, TypeError, AttributeError):
        print(f"{NO} {label}: {what}")
        return None
    free = getattr(sp.sympify(want), 'free_symbols', set())
    if getattr(value, 'free_symbols', set()) and not free:
        print(f"{NO} {label}: {what}")
        return None
    return value


def _agree(got, want, tol=_SEQ_TOL):
    """Сходится ли ответ с тем, что дала прогрессия.

    Сначала алгебраически: у логарифмических членов числа нет вовсе,
    и −90 − 25 ln 3 сравнивать с суммой можно только упрощением.
    Потом численно, с тем же допуском, что принимает экзамен.
    """
    try:
        if sp.simplify(sp.sympify(got) - sp.sympify(want)) == 0:
            return True
    except (sp.SympifyError, TypeError, AttributeError):
        return False
    if _near(got, want, tol):
        return True
    if tol < _SEQ_TOL:
        return False          # допуск затянут вопросом: округление не в счёт
    # Экзамен принимает три значащие цифры, и 4.67 вместо 14/3 — верный
    # ответ. Относительный допуск такое округление отвергает, когда первая
    # значащая цифра мала: у 4.67 ошибка округления вчетверо больше, чем
    # у 9.67. Поэтому запись сверяется ещё и по самим цифрам.
    try:
        return sig(got, 3) == sig(want, 3)
    except (TypeError, ValueError):
        return False


def _seq_report(label, got, want, slips, tol=_SEQ_TOL):
    """Общий разбор: сходится, известный промах или мимо."""
    if _agree(got, want, tol):
        print(f"{OK} {label}")
        return True
    for what, value in slips.items():
        if value is not None and _agree(got, value, tol):
            print(f"{NO} {label}: {what}")
            return False
    print(f"{NO} {label}: " + _t("у этой последовательности выходит другое",
                                 "this sequence gives something else"))
    return False


def _where(var, run):
    """Хвост сообщения: при каком значении буквы проверка не сошлась."""
    if not run or var is None or var not in run:
        return ''
    return ' (' + _t(f'при {var} = {run[var]}',
                     f'at {var} = {run[var]}') + ')'


def _walkpoints(n, var, values):
    """Пары «подстановка, номер», на которых сверяется ответ.

    Буква в самой прогрессии — это values: условие обязано выполняться
    при каждом её значении, а не при одном удачном. Буква вместо номера
    — это ответ-формула, и она сверяется на нескольких n сразу. Номером
    бывает и выражение: у ряда 1 + x + … + xⁿ слагаемых n + 1, и
    подставляется тогда буква, а номер считается из неё.
    """
    runs = [{}] if var is None else [{var: value} for value in values]
    try:
        free = [s for s in sorted(sp.sympify(n).free_symbols, key=str)
                if s != var]
    except (sp.SympifyError, TypeError, AttributeError):
        free = []
    if free:
        index = free[0]
        return [({**run, index: i}, sp.sympify(n).subs({**run, index: i}))
                for run in runs for i in _SEQ_SAMPLES]
    return [(run, n) for run in runs]


def _sampled(label, got, rule, var, values):
    """Сверка ответа-выражения: обе стороны считаются при нескольких n.

    Ответ вида u_n = 2n + 3 нельзя сверить сложением при одном номере:
    формула должна совпадать с прогрессией на всех n, а не на счастливом.
    Поэтому берётся несколько значений, и каждое проверяется отдельно.
    """
    for value in values:
        want = rule(value)
        if want is None:
            return False
        mine = sp.sympify(got).subs(var, value)
        if not _agree(mine, want):
            print(f"{NO} {label}: " + _t(
                f"при {var} = {value} последовательность даёт другое",
                f"at {var} = {value} the sequence gives something else"))
            return False
    print(f"{OK} {label}")
    return True


def verify_term(label, got, seq, n, var=None, values=()):
    """Ответ — член последовательности, и он получается ходом по ней.

    seq строится progression(...) или geometric(...); n — номер члена.
    Арифметическая доходит до него сложением, геометрическая умножением;
    формулы n-го члена у проверки нет ни той, ни другой.

    Обратный ход — тот же вызов, прочитанный наоборот:

        verify_term('1', 6, progression(q_u1, q_d), 7)

    это «седьмой член вашей прогрессии равен шести?», и так проверяется
    «найдите первый член и общую разность» без единого хранимого ответа.

    Если ответ содержит букву, n обязано быть этой буквой: тогда
    сравнение идёт при нескольких её значениях сразу, и «выразите u_n
    через n» проверяется тем же вызовом. Буква внутри самой прогрессии
    задаётся var и values.
    """
    if _blank(label, got, seq, n):
        return False
    kind = _kind(seq)
    what = _t("член этой последовательности это число",
              "a term of this sequence is a number")
    for run, place in _walkpoints(n, var, values):
        here = _fixed(seq, run)
        index = _index(label, place)
        if index is None:
            return False
        terms = _run(here, index + 1)
        want = terms[index - 1]
        answer = _as_value(label, sp.sympify(got).subs(run), want, what)
        if answer is None:
            return False
        if _agree(answer, want):
            continue
        slips = {_t("это следующий член: номер сдвинут на единицу",
                    "that is the next term: the index is out by one"):
                 terms[index],
                 _t("это предыдущий член: номер сдвинут на единицу",
                    "that is the previous term: the index is out by one"):
                 terms[index - 2] if index > 1 else None,
                 _t("это сумма первых членов, а не сам член",
                    "that is the sum of the terms, not the term itself"):
                 sp.Add(*terms[:index])}
        if kind == 'ap':
            slips[_t("шаг сделан n раз вместо n−1: первый член тоже член",
                     "the step is taken n times instead of n−1: the first "
                     "term is a term too")] = want + here[2]
        else:
            slips[_t("знаменатель перевёрнут: он считается как следующий "
                     "член, делённый на предыдущий",
                     "the ratio is upside down: it is the next term divided "
                     "by the one before")] = (
                _run((kind, here[1], 1 / here[2]), index)[-1]
                if here[2] != 0 else None)
        return _seq_report(label + _where(var, run), answer, want, slips)
    print(f"{OK} {label}")
    return True


def verify_total(label, got, seq, n, var=None, values=()):
    """Ответ — сумма первых n членов, и она получается сложением.

    Ни n/2(2u₁+(n−1)d), ни u₁(rⁿ−1)/(r−1) проверке не нужны: она честно
    складывает первые n членов прогрессии.

    Обратный ход тот же: `verify_total('1b', 0, mine, q_n)` — «сумма
    первых ваших n членов равна нулю?», и так проверяется «найдите n».
    Номер при этом обязан быть целым и положительным, и проверка это
    говорит отдельной строкой: ноль членов тоже даёт нулевую сумму,
    и схема оценивания такой ответ отдельно оговаривает.

    Ответ-формула сверяется при нескольких n, как и в verify_term;
    буква внутри самой прогрессии задаётся var и values.
    """
    if _blank(label, got, seq, n):
        return False
    kind = _kind(seq)
    what = _t("сумма этой последовательности это число",
              "a sum of this sequence is a number")
    for run, place in _walkpoints(n, var, values):
        here = _fixed(seq, run)
        index = _index(label, place)
        if index is None:
            return False
        terms = _run(here, index + 1)
        want = sp.Add(*terms[:index])
        answer = _as_value(label, sp.sympify(got).subs(run), want, what)
        if answer is None:
            return False
        if _agree(answer, want):
            continue
        slips = {_t("это n-й член, а не сумма первых n",
                    "that is the nth term, not the sum of the first n"):
                 terms[index - 1],
                 _t("сложено на один член больше",
                    "one term too many has been added"): sp.Add(*terms),
                 _t("сложено на один член меньше",
                    "one term too few has been added"):
                 sp.Add(*terms[:index - 1]) if index > 1 else None}
        if kind == 'ap':
            slips[_t("сумма удвоена: n/2 превратилось в n",
                     "the sum is doubled: the n/2 has become n")] = 2 * want
            slips[_t("взята половина суммы",
                     "that is half of the sum")] = want / 2
        else:
            slips[_t("это сумма всей прогрессии, а не первых n",
                     "that is the sum of the whole sequence, not of the "
                     "first n")] = infinite(here)
        return _seq_report(label + _where(var, run), answer, want, slips)
    print(f"{OK} {label}")
    return True


def verify_start(label, got, seq):
    """Ответ — несколько первых членов подряд.

    «Write down the first four terms» — вопрос на четыре балла, где
    считать нечего, а промахнуться можно в каждом. Список сверяется
    почленно, и сообщение называет номер первого расхождения, не
    называя, что там должно стоять.
    """
    if _blank(label, got, seq):
        return False
    if not isinstance(got, (list, tuple)) or not got:
        print(f"{NO} {label}: " + _t("ответ это список членов подряд",
                                     "the answer is a list of consecutive "
                                     "terms"))
        return False
    terms = _run(seq, len(got))
    for i, (mine, want) in enumerate(zip(got, terms), start=1):
        value = _as_value(label, mine, want,
                          _t("член этой последовательности это число",
                             "a term of this sequence is a number"))
        if value is None:
            return False
        if not _agree(value, want):
            print(f"{NO} {label}: " + _t(
                f"член номер {i} не такой", f"term number {i} is not that"))
            return False
    print(f"{OK} {label}")
    return True


def _differences(label, items, var, values):
    """Разности соседних членов. None, если список не годится."""
    if len(items) < 3:
        print(f"{NO} {label}: " + _t(
            "арифметическая последовательность начинается с трёх членов",
            "an arithmetic sequence starts at three terms"))
        return None
    runs = [{}] if var is None else [{var: value} for value in values]
    out = []
    for run in runs:
        row = []
        for before, after in zip(items, items[1:]):
            try:
                row.append(sp.simplify(sp.sympify(after).subs(run)
                                       - sp.sympify(before).subs(run)))
            except (sp.SympifyError, TypeError, AttributeError):
                print(f"{NO} {label}: " + _t("члены это выражения",
                                             "the terms are expressions"))
                return None
        out.append(row)
    return out


def verify_arithmetic(label, items, var=None, values=()):
    """Эти члены, в этом порядке, образуют арифметическую последовательность?

    Ответа-числа здесь нет вовсе: ответ сидит внутри самих членов.
    Экзамен спрашивает «покажите, что m, r и c образуют арифметическую
    последовательность», и ваш найденный c приходит сюда третьим членом.

    var и values — когда члены содержат букву: условие обязано
    выполняться при всех её значениях, а не при одном удачном, поэтому
    берётся несколько.
    """
    if _blank(label, *items):
        return False
    rows = _differences(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, step in enumerate(row[1:], start=2):
            if not _agree(step, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"разность между членами {i} и {i + 1} не такая, как "
                    f"между первыми двумя",
                    f"the difference between terms {i} and {i + 1} is not "
                    f"the one between the first two"))
                return False
    print(f"{OK} {label}")
    return True


def verify_step(label, got, items, var=None, values=()):
    """Ответ — общая разность, и она берётся вычитанием соседних членов.

    Сначала проверяется, что разность вообще постоянна: «найдите общую
    разность» у неарифметической последовательности ответа не имеет.
    Потом — что она равна вашей.

    items разрешено собирать из правила: [rule(1), rule(2), rule(3)] —
    так проверяется «покажите, что площади образуют арифметическую
    последовательность, и найдите разность».
    """
    if _blank(label, got, *items):
        return False
    rows = _differences(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, step in enumerate(row[1:], start=2):
            if not _agree(step, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"разность непостоянна: между членами {i} и {i + 1} она "
                    f"другая",
                    f"the difference is not constant: between terms {i} and "
                    f"{i + 1} it is different"))
                return False
    want = rows[0][0]
    if var is not None:
        for run, row in zip([{var: value} for value in values], rows):
            if not _agree(sp.sympify(got).subs(run), row[0]):
                print(f"{NO} {label}: " + _t(
                    "разность этой последовательности другая",
                    "this sequence has a different common difference"))
                return False
        print(f"{OK} {label}")
        return True
    answer = _as_value(label, got, want,
                       _t("общая разность этой последовательности это число",
                          "the common difference of this sequence is "
                          "a number"))
    if answer is None:
        return False
    slips = {_t("знак разности противоположный: она считается как "
                "следующий минус предыдущий",
                "the sign is the other way round: the difference is the "
                "next term minus the one before"): -want,
             _t("это разность через один член, а не между соседними",
                "that is the difference two terms apart, not between "
                "neighbours"): 2 * want}
    return _seq_report(label, answer, want, slips)


def _ratios(label, items, var, values):
    """Отношения соседних членов. None, если список не годится."""
    if len(items) < 3:
        print(f"{NO} {label}: " + _t(
            "геометрическая последовательность начинается с трёх членов",
            "a geometric sequence starts at three terms"))
        return None
    runs = [{}] if var is None else [{var: value} for value in values]
    out = []
    for run in runs:
        row = []
        for before, after in zip(items, items[1:]):
            try:
                bottom = sp.simplify(sp.sympify(before).subs(run))
                top = sp.simplify(sp.sympify(after).subs(run))
            except (sp.SympifyError, TypeError, AttributeError):
                print(f"{NO} {label}: " + _t("члены это выражения",
                                             "the terms are expressions"))
                return None
            if bottom == 0:
                print(f"{NO} {label}: " + _t(
                    "у геометрической последовательности членов-нулей не бывает: "
                    "делить не на что",
                    "a geometric sequence has no zero term: there is nothing "
                    "to divide by"))
                return None
            row.append(sp.simplify(top / bottom))
        out.append(row)
    return out


def verify_geometric(label, items, var=None, values=()):
    """Эти члены, в этом порядке, образуют геометрическую последовательность?

    Ответа-числа здесь нет вовсе: ответ сидит внутри самих членов.
    Экзамен спрашивает «покажите, что первые три члена образуют
    геометрическую последовательность», и ваш найденный член приходит
    сюда третьим.

    var и values — когда члены содержат букву: условие обязано
    выполняться при всех её значениях, а не при одном удачном.
    """
    if _blank(label, *items):
        return False
    rows = _ratios(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, ratio in enumerate(row[1:], start=2):
            if not _agree(ratio, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"отношение членов {i} и {i + 1} не такое, как у первых "
                    f"двух",
                    f"the ratio of terms {i} and {i + 1} is not the one of "
                    f"the first two"))
                return False
    print(f"{OK} {label}")
    return True


def verify_ratio(label, got, items, var=None, values=()):
    """Ответ — знаменатель, и он берётся делением соседних членов.

    Сначала проверяется, что отношение вообще постоянно: «найдите
    знаменатель» у негеометрической последовательности ответа не имеет.
    Потом — что оно равно вашему.

    items разрешено собирать из правила: [rule(1), rule(2), rule(3)] —
    так проверяется «покажите, что площади образуют геометрическую
    последовательность, и найдите знаменатель».
    """
    if _blank(label, got, *items):
        return False
    rows = _ratios(label, list(items), var, values)
    if rows is None:
        return False
    for row in rows:
        for i, ratio in enumerate(row[1:], start=2):
            if not _agree(ratio, row[0]):
                print(f"{NO} {label}: " + _t(
                    f"отношение непостоянно: у членов {i} и {i + 1} оно "
                    f"другое",
                    f"the ratio is not constant: for terms {i} and {i + 1} "
                    f"it is different"))
                return False
    want = rows[0][0]
    if var is not None:
        for run, row in zip([{var: value} for value in values], rows):
            if not _agree(sp.sympify(got).subs(run), row[0]):
                print(f"{NO} {label}: " + _t(
                    "у этой последовательности знаменатель другой",
                    "this sequence has a different common ratio"))
                return False
        print(f"{OK} {label}")
        return True
    answer = _as_value(label, got, want,
                       _t("знаменатель этой последовательности это число",
                          "the common ratio of this sequence is a number"))
    if answer is None:
        return False
    slips = {_t("знаменатель перевёрнут: он считается как следующий член, "
                "делённый на предыдущий",
                "the ratio is upside down: it is the next term divided by "
                "the one before"): 1 / want if want != 0 else None,
             _t("это отношение через один член, а не между соседними",
                "that is the ratio two terms apart, not between neighbours"):
             want ** 2,
             _t("знак потерян: у чередующейся последовательности "
                "знаменатель отрицательный",
                "the sign is gone: an alternating sequence has a negative "
                "ratio"): -want,
             _t("это разность соседних членов, а не их отношение",
                "that is the difference of neighbouring terms, not their "
                "ratio"): sp.simplify(sp.sympify(items[1]) - sp.sympify(items[0]))}
    return _seq_report(label, answer, want, slips)


def verify_infinite(label, got, seq, var=None, values=(), exact=False):
    """Ответ — сумма всей геометрической прогрессии.

    Проверка складывает члены, пока хвост не станет меньше допуска, и
    формулы u₁/(1−r) внутри неё нет. Отсюда и главное: у расходящейся
    прогрессии складывать негде, и такой вызов честно отвечает, что
    бесконечной суммы не существует, — то самое условие |r| < 1,
    за которое на экзамене стоит отдельный балл.

    Знаменателю разрешено быть выражением: тогда var и values говорят,
    при каких значениях буквы сверяться, и ответ 1/(1+x²) проверяется
    сложением при каждом из них.

    exact=True добавляет требование к записи: «find the exact value»
    десятичной дроби не принимает.
    """
    if _blank(label, got, seq):
        return False
    if _kind(seq) != 'gp':
        print(f"{NO} {label}: " + _t(
            "бесконечная сумма бывает у геометрической прогрессии",
            "a sum to infinity belongs to a geometric sequence"))
        return False
    if exact and sp.sympify(got).atoms(sp.Float):
        print(f"{NO} {label}: " + _t(
            "вопрос просит точное значение: оставьте дробь или корень",
            "the question asks for the exact value: keep the fraction or "
            "the surd"))
        return False
    runs = [{}] if var is None else [{var: value} for value in values]
    for run in runs:
        here = _fixed(seq, run)
        if not _converges(here):
            print(f"{NO} {label}{_where(var, run)}: " + _t(
                "эта прогрессия не убывает: бесконечной суммы у неё нет",
                "this sequence does not shrink: it has no sum to infinity"))
            return False
        want = infinite(here)
        answer = _as_value(label, sp.sympify(got).subs(run), want,
                           _t("бесконечная сумма это число",
                              "a sum to infinity is a number"))
        if answer is None:
            return False
        # «Точное значение» — требование не только к записи, но и к самому
        # числу: 53/999 сходится с 53/990 в трёх значащих цифрах, а дробью
        # является другой. Поэтому при exact допуск сжимается до точности
        # самого сложения.
        tol = _SEQ_EXACT if exact else _SEQ_TOL
        if _agree(answer, want, tol):
            continue
        slips = {_t("это первый член, а не сумма",
                    "that is the first term, not the sum"): here[1],
                 _t("в знаменателе 1 + r вместо 1 − r",
                    "the denominator is 1 + r instead of 1 − r"):
                 here[1] / (1 + here[2]) if here[2] != -1 else None,
                 _t("делено на r вместо 1 − r",
                    "divided by r instead of by 1 − r"):
                 here[1] / here[2] if here[2] != 0 else None}
        return _seq_report(label + _where(var, run), answer, want, slips,
                           tol)
    print(f"{OK} {label}")
    return True


def verify_least(label, got, seq, holds, what='total', limit=None):
    """Ответ — наименьшее n, при котором условие выполняется.

    Проверка идёт по прогрессии от первого члена, считает то, о чём
    условие говорит, — сумму первых n (`what='total'`) или сам n-й член
    (`what='term'`), — и останавливается на первом n, где holds сказал
    «да». Ни логарифма, ни решения неравенства внутри нет: наименьшее
    находится перебором, ровно как таблицей на калькуляторе.

    holds — то, что спрашивает условие, записанное как функция от этого
    значения: `lambda s: s > 33500`.

    Заодно проверяется, что предыдущий номер условию не отвечает: иначе
    ответ не наименьший, а просто подходящий.
    """
    if _blank(label, got, seq):
        return False
    span = limit or _SEQ_WALK
    running, least, before = sp.Integer(0), None, None
    value = None
    for i, item in enumerate(_run(seq, span), start=1):
        running = running + item
        value = running if what == 'total' else item
        try:
            if holds(value):
                least, at = i, value
                break
        except TypeError:
            print(f"{NO} {label}: " + _t(
                "условие не сравнивается: в нём остался незаполненный ответ",
                "the condition cannot be compared: an answer in it is still "
                "blank"))
            return False
        before = value
    if least is None:
        print(f"{NO} {label}: " + _t(
            f"за первые {span} членов условие так и не выполнилось",
            f"the condition never holds within the first {span} terms"))
        return False
    index = _index(label, got)
    if index is None:
        return False
    slips = {_t("на единицу меньше: при этом номере условие ещё не "
                "выполняется",
                "one less: at that index the condition does not hold yet"):
             least - 1,
             _t("условие выполняется и раньше: наименьшее не это",
                "the condition holds earlier than that: this is not the "
                "least one"): least + 1,
             _t("это значение, а не номер, при котором оно достигнуто",
                "that is the value, not the index at which it is reached"):
             at}
    if before is not None and holds(before):
        print(f"{NO} {label}: " + _t(
            "условие выполняется и раньше: наименьшее n не такое",
            "the condition already holds earlier: this is not the least n"))
        return False
    return _seq_report(label, sp.Integer(index), sp.Integer(least), slips)


def verify_peak(label, got, seq, at=None, limit=None):
    """Ответ — наибольшая из сумм S₁, S₂, S₃, … , и её ищут перебором.

    Проверка складывает член за членом и запоминает наибольшую сумму.
    Знать, что S_n — квадратичная по n и что максимум приходится на
    перемену знака членов, ей для этого не нужно.

    at — номер, на котором максимум достигается, если вопрос просит и
    его. Максимум бывает достигнут дважды подряд: когда очередной член
    ровно нуль, S_{n−1} = S_n, и оба номера верны. Проверка принимает
    любой из них.
    """
    if _blank(label, got, seq):
        return False
    if at is not None and _blank(label, at):
        return False
    if _kind(seq) != 'ap':
        print(f"{NO} {label}: " + _t(
            "наибольшая сумма ищется у арифметической прогрессии",
            "the greatest sum is looked for in an arithmetic sequence"))
        return False
    step = seq[2]
    if not sp.sympify(step).is_number or float(step) >= 0:
        print(f"{NO} {label}: " + _t(
            "у растущей последовательности наибольшей суммы нет",
            "a sequence that grows has no greatest sum"))
        return False
    # Шагов ровно столько, сколько нужно, чтобы члены сменили знак:
    # после этого суммы только убывают.
    span = limit or min(_SEQ_WALK,
                        int(abs(float(seq[1]) / float(step))) + 5)
    terms = _run(seq, max(span, 2))
    best, running, where = None, 0, []
    for i, value in enumerate(terms, start=1):
        running = running + value
        if best is None or float(running - best) > _SEQ_TOL:
            best, where = running, [i]
        elif _near(running, best, _SEQ_TOL):
            where.append(i)
    answer = _as_value(label, got, best, _t("сумма это число",
                                           "a sum is a number"))
    if answer is None:
        return False
    slips = {_t("это наибольший член, а не наибольшая сумма",
                "that is the largest term, not the largest sum"): terms[0],
             _t("сумма оборвана на один член раньше, чем нужно",
                "the sum stops one term short"):
             best - terms[where[0] - 1] if where[0] > 1 else None}
    if not _seq_report(label, answer, best, slips):
        return False
    if at is not None:
        index = _index(f'{label} (n)', at)
        if index is None:
            return False
        if index not in where:
            print(f"{NO} {label} (n): " + _t(
                "на этом номере сумма не наибольшая",
                "the sum is not greatest at that index"))
            return False
        print(f"{OK} {label} (n)")
    return True
