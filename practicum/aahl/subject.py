"""Математика AA HL как предмет для ядра тренажёра (drill-core).

Ядро — расписание повторений, журнал, вечерний набор, все ручки — про
математику не знает. Здесь собрано всё, что знает: банк приёмов, генераторы
задач, проверка ответа настоящими проверками из kit, доступ к подлинникам
и рубрика оформления.

    DRILL_SUBJECTS=math:/путь/practicum/subject.py

Проверка ответа не сравнивает строки. Ученик пишет `2sqrt(6)` или `x=1, x=4`,
а работает ровно тот же код, что и в практикумах-ноутбуках, — значит «верно»
в тренажёре и «верно» в ноутбуке означают одно и то же.

Письменный режим у математики есть: подлинник лежит разворотами PDF, и
модель смотрит на то же, на что смотрит экзаменатор.
"""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))

ID = 'math'
TITLE = 'IB Math AA HL'
BANK = os.path.join(HERE, 'bank.json')
RUBRIC = os.path.join(HERE, 'presentation.yaml')

# Чем предмет правит разбор письменной работы. Правила разметки IB общие на
# любой бумаге; своё здесь — кем представиться модели и как записывать
# формулы. Латех тут обязателен: страница разбора его и рисует, а k(k+1)/2
# в тексте читается плохо.
EXAMINER = ('an experienced IB Mathematics: Analysis and Approaches HL '
            'examiner')
SUBSTANCE = 'MATHEMATICS'
NOTATION = (r'- Write every mathematical expression in LaTeX between dollar '
            r'signs, in "model_write_up", in "one_thing", in the "fix" fields '
            r'and in the lines you quote: $n = k + 1$, $\frac{k(k+1)}{2}$, '
            r'$\sum_{r=1}^{n} r$. A whole displayed line may use $$...$$. '
            r'Keep one step per line and keep the line breaks — the page '
            r'renders this, and plain ASCII like k(k+1)/2 renders badly.')


# Разделы силлабуса: по ним группируются темы на экране набора. Раньше
# этот список был вшит в саму страницу; с появлением физики он поехал —
# над физическими темами стояло «Числа и алгебра».
# Как выглядит ответ: раньше эта строка была вшита в саму страницу и над
# физической задачей предлагала написать 2sqrt(6).
PLACEHOLDER = 'например 2sqrt(6) или 1, 4'

SECTIONS = {
    'A': 'Числа и алгебра',
    'B': 'Функции',
    'C': 'Геометрия и тригонометрия',
    'D': 'Статистика и вероятность',
    'E': 'Математический анализ',
}


def load_bank(path=BANK):
    from drill import engine
    with open(path) as fh:
        return engine.prepare_bank(json.load(fh))


def _lazy():
    """Проверка и генераторы тянут sympy и kit — а это секунды на импорте.

    Предмет загружается на старте службы, но банк и sympy нужны не всем
    ручкам сразу, поэтому тяжёлое подтягивается при первом обращении.
    """
    import sys
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    from aahl import check
    from aahl.items import GENERATORS
    return check, GENERATORS


class _Generators(dict):
    """Реестр генераторов, наполняемый при первом обращении."""

    def _fill(self):
        if not dict.__len__(self):
            self.update(_lazy()[1])
        return self

    def __getitem__(self, key):
        return dict.__getitem__(self._fill(), key)

    def __contains__(self, key):
        return dict.__contains__(self._fill(), key)

    def __iter__(self):
        return dict.__iter__(self._fill())

    def __len__(self):
        return dict.__len__(self._fill())


generators = _Generators()


def evaluate(spec, raw):
    return _lazy()[0].evaluate(spec, raw)


def show_answer(answer, spec=None):
    return _lazy()[0].show_answer(answer, var=(spec or {}).get('var', 'x'))


def rubric(practicum=None):
    from drill import grader
    return grader.rubric(RUBRIC, practicum)


# --- подлинник -------------------------------------------------------------
#
# Разбор письменной работы опирается на сами бумаги: страницу билета и
# страницу схемы оценивания. Пересказ из корпуса для этого не годится — он
# получен извлечением и в одном доказанном случае неверен.

def reference(block):
    from aahl import archive
    return archive.reference(block)


def page_count(block, which='question'):
    from aahl import archive
    return len(archive.block_page_numbers(block, which))


def page_image(block, which='question', index=0):
    from aahl import archive
    return archive.page_image(block, which, index)


def block_pages(block, with_markscheme=True):
    from aahl import archive
    return archive.block_pages(block, with_markscheme)


def instructions(block):
    from aahl import archive
    return archive.instructions(block['dir'])


def question_pdf(block):
    """Файл билета и номера страниц этого вопроса — для листа заданий."""
    from aahl import archive
    path = os.path.join(archive.ROOT, block['dir'], archive.QUESTION_PDF)
    if not os.path.isfile(path):
        raise LookupError(f"нет билета для {block.get('id') or block['dir']}")
    return path, archive.block_page_numbers(block, 'question')


def source_url(block, which='question'):
    """Прямая ссылка на подлинник: страницы отдаёт тот же сайт."""
    from aahl import archive
    name = ('question-paper.pdf' if which == 'question'
            else 'markscheme.pdf')
    hint = (block.get('source_pages') if which == 'question'
            else block.get('markscheme_pages'))
    pages = archive.paper.parse_pages(hint)
    return f"/{block['dir']}/{name}#page={pages[0] if pages else 1}"
