"""Архив AA HL: где лежат подлинники и какие их страницы чьи.

Это половина предмета, а не ядра. Ядро знает, что у вопроса бывают
страницы подлинника, и умеет их отрисовать и подшить в лист заданий
(drill/paper.py). А вот что подлинник лежит в AA_HL/2022/May/TZ2/Paper 1,
что вопрос начинается со строки «12.» и что в начале схемы оценивания
напечатаны Instructions to Examiners — знает только математика.

Разбор письменной работы опирается на подлинник: страницу билета и страницу
схемы оценивания. Пересказ из корпуса для этого не годится — он получен
извлечением и в одном доказанном случае неверен (см. corpus_issues в
карточке C1). Поэтому страницы рендерятся из самих PDF и уходят в модель
картинками: она смотрит на то же, на что смотрит экзаменатор.

Номера страниц знает корпус, и они лежат в банке рядом с блоком.
"""
from __future__ import annotations

import functools
import os
import re
import time

import pymupdf

from drill import paper

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

QUESTION_PDF = 'question-paper.pdf'
MARKSCHEME_PDF = 'markscheme.pdf'
DPI = paper.DPI
MAX_PAGES = paper.MAX_PAGES


def render(folder, which, spec, extra=0, dpi=DPI):
    """PNG-страницы одного документа.

    extra добавляет следующую страницу: вопрос и его схема оценивания
    regularly переходят через границу листа, и обрыв на середине читается
    хуже, чем лишняя страница.
    """
    path = os.path.join(ROOT, folder,
                        QUESTION_PDF if which == 'question' else MARKSCHEME_PDF)
    if not os.path.isfile(path):
        raise LookupError(f'нет файла: {folder}/{which}')
    numbers = paper.parse_pages(spec)
    if extra and numbers:
        numbers = sorted(set(numbers) | {numbers[-1] + 1})
    images = []
    for number in numbers[:MAX_PAGES]:
        try:
            images.append(paper.render_page(path, number, dpi))
        except LookupError:
            continue          # хвостовая страница может не существовать
    if not images:
        raise LookupError(f'{folder}/{which}: не удалось отрисовать страницы')
    return images


INSTRUCTIONS_HEADING = 'Instructions to Examiners'
INSTRUCTIONS_END = ('Section A', 'Section B')
INSTRUCTIONS_LIMIT = 8


@functools.lru_cache(maxsize=64)
def instructions(folder):
    """«Instructions to Examiners» из начала схемы оценивания, текстом.

    Это официальные правила разметки: что означают M, A, R и AG, когда
    A-балл зависит от предыдущего M, нужно ли повторять напечатанную
    строку в «show that». Они есть в каждой схеме и различаются по
    бумагам только разделом про калькулятор — поэтому берутся из той же
    бумаги, что и вопрос, а не из общего файла.

    Картинками отдавать незачем: это сплошная проза без чертежей, и
    текстом она стоит в пять раз дешевле.
    """
    path = os.path.join(ROOT, folder, MARKSCHEME_PDF)
    if not os.path.isfile(path):
        return ''
    with pymupdf.open(path) as document:
        start = next((n for n in range(min(INSTRUCTIONS_LIMIT,
                                           document.page_count))
                      if INSTRUCTIONS_HEADING in document[n].get_text()), None)
        if start is None:
            return ''
        out = []
        for number in range(start, document.page_count):
            text = document[number].get_text()
            if number > start and any(mark in text
                                      for mark in INSTRUCTIONS_END):
                break
            out.append(text)
    body = '\n'.join(out)
    # В колонтитулах повторяется код бумаги — модели он ни к чему.
    body = re.sub(r'^\s*[–-]\s*\d+\s*[–-]\s*\S+\s*$', '', body,
                  flags=re.M)
    return re.sub(r'\n{3,}', '\n\n', body).strip()


QUESTION_START = re.compile(r'^\s*(\d{1,2})\.\s', re.M)
SEARCH_RADIUS = 2
NEARLY_BLANK = 260


@functools.lru_cache(maxsize=256)
def _page_numbers(path, number):
    """Номера вопросов, начинающихся на странице."""
    with pymupdf.open(path) as document:
        if not 1 <= number <= document.page_count:
            return (), 0
        text = document[number - 1].get_text()
    return (tuple(int(n) for n in QUESTION_START.findall(text)),
            len(re.sub(r'\s+', '', text)))


# Разметка одного вопроса умещается в пару страниц; сам вопрос бывает
# длиннее. Потолок нужен, чтобы длинное исследование Paper 3 не утащило
# в запрос десяток страниц по 2,6 тысячи токенов каждая.
PAGE_LIMIT = {'question': 4, 'markscheme': 2}


def locate(folder, question, hint, which='question', span=1):
    """Страницы билета, на которых действительно стоит этот вопрос.

    Номера страниц в корпусе шумят на единицу — и непостоянно, даже внутри
    одной бумаги, — поэтому подсказка из корпуса берётся как ориентир, а
    страница ищется по самому вопросу: по строке, начинающейся с «N.».

    Следующая страница добавляется только если вопрос на неё продолжается,
    то есть на ней не начинается вопрос с большим номером и она не пуста.
    Раньше она добавлялась всегда, и в 92% случаев это была чужая страница.

    То же самое годится и для схемы оценивания: там подсказка промахивается
    реже, но промахивается — в 35 блоках из 332 нужная страница на единицу
    раньше.
    """
    path = os.path.join(ROOT, folder,
                        QUESTION_PDF if which == 'question' else MARKSCHEME_PDF)
    if not os.path.isfile(path):
        raise LookupError(f'нет файла: {folder}/{which}')
    with pymupdf.open(path) as document:
        total = document.page_count

    hints = _hint_pages(hint, total)
    start = None
    for candidate in _search_order(hints, total):
        numbers, _ = _page_numbers(path, candidate)
        if question in numbers:
            start = candidate
            break
    if start is None:
        # Номер не стоит нигде рядом: длинное исследование Paper 3, где он
        # напечатан лишь на первой странице, или разметка вопроса, начатая
        # на предыдущей странице. Верим корпусу и берём запас.
        limit = PAGE_LIMIT.get(which, 3)
        return [n for n in range(hints[0], hints[-1] + span + 1)
                if 1 <= n <= total][:limit]

    limit = PAGE_LIMIT.get(which, 3)
    pages = [start]
    while len(pages) < limit and pages[-1] + 1 <= total:
        numbers, size = _page_numbers(path, pages[-1] + 1)
        if any(n > question for n in numbers) or size < NEARLY_BLANK:
            break
        pages.append(pages[-1] + 1)
    return pages


LOOSE_PAGE = re.compile(r'\d+')


def _hint_pages(hint, total):
    """Номера страниц из подсказки корпуса, включая написанные прозой.

    У восьми блоков подсказка выглядит как «15/17», «8 of 17» или
    «2023-NOV-TZ1-P2, page 4 of 17»: номер в ней есть, но parse_pages
    его не берёт, и поиск начинался с первой страницы — то есть с
    обложки. Лишние числа не опасны: страницу всё равно подтверждает
    номер вопроса, напечатанный на ней.
    """
    pages = paper.parse_pages(hint)
    if pages:
        return pages
    loose = [int(n) for n in LOOSE_PAGE.findall(str(hint or ''))]
    return [n for n in dict.fromkeys(loose) if 1 <= n <= total] or [1]


def _search_order(hints, total):
    """Подсказки корпуса, затем ближайшие страницы вокруг каждой."""
    order = list(hints)
    for step in range(1, SEARCH_RADIUS + 1):
        for hint in hints:
            order += [hint + step, hint - step]
    return [n for n in dict.fromkeys(order) if 1 <= n <= total]


def block_pages(block, with_markscheme=True):
    """Картинки для одного блока архива: билет и схема оценивания."""
    out = {'question': [page_image(block, 'question', index)
                        for index in range(len(block_page_numbers(
                            block, 'question')))]}
    if with_markscheme:
        try:
            out['markscheme'] = [
                page_image(block, 'markscheme', index)
                for index in range(len(block_page_numbers(block,
                                                          'markscheme')))]
        except LookupError:
            out['markscheme'] = []
    return out


def block_page_numbers(block, which='question'):
    """Какие страницы файла относятся к этому блоку."""
    hint = (block.get('source_pages') if which == 'question'
            else block.get('markscheme_pages'))
    return locate(block['dir'], int(block['question']), hint, which)


def card_pages(block):
    """Страницы вопроса, на которых есть сам вопрос, а не линейка.

    Длинный вопрос переходит на следующий лист, и на том листе часто
    стоит только «(Question 2 continued)» и строчки под ответ. Для
    разбора на бумаге такая страница нужна — на ней пишут; для карточки
    узнавания она пустая, и показывать её нечем.

    Если содержательной не оказалось ни одной, остаётся первая: лучше
    показать лист целиком, чем не показать ничего.
    """
    numbers = block_page_numbers(block, 'question')
    path = os.path.join(ROOT, block['dir'], QUESTION_PDF)
    kept = [number for number in numbers
            if paper.question_clip(path, number) is not None]
    return kept or numbers[:1]


PART_TOKEN = re.compile(r'[a-z]+')
# Пункт случается на листе, который locate не взял: страница с одним
# чертежом считается почти пустой и до неё разбор не доходит.
BAND_LOOKAHEAD = 2


def part_parts(part, question=None):
    """Пункт корпуса — в части: «(g)(ii)» → ('g', 'ii'), «B-I» → ('b', 'i').

    Записан он четырьмя способами: «A», «a», «(a)», «a-i», «(a)(i)»,
    «e(i)», «D-II». У 101 блока пункта нет вовсе — такой вопрос не
    делится, — а иногда поле повторяет номер вопроса: это тоже не пункт.
    Дальше (j) пункты не заходят ни в одной бумаге архива.
    """
    body = str(part or '').strip().lower()
    if not body or (question is not None and body == str(question).lower()):
        return ()
    tokens = PART_TOKEN.findall(body)
    if not tokens or tokens[0] not in 'abcdefghij' or len(tokens[0]) != 1:
        return ()
    out = [tokens[0]]
    for token in tokens[1:]:
        if set(token) - set('ivx'):
            break                      # дальше не пункт, а слово
        out.append(token)
    return tuple(out)


def part_letter(block):
    """Буква пункта блока: «B» → b, «(g)(ii)» → g, «» → None."""
    found = part_parts(block.get('part'), block.get('question'))
    return found[0] if found else None


def part_label(block):
    """Пункт для подписи карточки: «(g)(ii)»."""
    return ''.join(f'({token})'
                   for token in part_parts(block.get('part'),
                                           block.get('question')))


def card_bands(block):
    """Полосы листа, из которых собирается карточка одного пункта.

    None — пункта у блока нет или его не нашли на листе; тогда карточка
    остаётся страницей целиком (см. card_pages).
    """
    letter = part_letter(block)
    if not letter:
        return None
    numbers = block_page_numbers(block, 'question')
    path = os.path.join(ROOT, block['dir'], QUESTION_PDF)
    if not os.path.isfile(path):
        return None
    with pymupdf.open(path) as document:
        total = document.page_count
    tail = [n for n in range(numbers[-1] + 1,
                             numbers[-1] + 1 + BAND_LOOKAHEAD) if n <= total]
    return paper.part_bands(path, tuple(numbers + tail), letter,
                            int(block['question']))


def page_count(block, which='question', crop=False):
    """Сколько страниц у блока. crop считает только содержательные."""
    if crop and which == 'question':
        return 1 if card_bands(block) else len(card_pages(block))
    return len(block_page_numbers(block, which))


def page_image(block, which='question', index=0, crop=False):
    """Одна страница блока картинкой.

    crop вырезает сам вопрос, без поля для письма: на экзаменационном
    листе оно занимает две трети страницы, и в режиме выбора приёма,
    где писать не нужно, оно только заставляет листать. Если у блока
    есть пункт, вырезается ещё и он один: у вопроса Paper 3 пунктов
    бывает десять, и все про разное, а спрашивают про один. Счёт
    страниц при этом идёт по содержательным — тем же, что считает
    page_count.
    """
    if crop and which == 'question':
        bands = card_bands(block)
        if bands:
            if index:
                raise LookupError('такой страницы нет')
            return paper.render_bands(
                os.path.join(ROOT, block['dir'], QUESTION_PDF), bands, DPI)
    numbers = (card_pages(block) if crop and which == 'question'
               else block_page_numbers(block, which))
    if not 0 <= index < len(numbers):
        raise LookupError('такой страницы нет')
    name = QUESTION_PDF if which == 'question' else MARKSCHEME_PDF
    path = os.path.join(ROOT, block['dir'], name)
    clip = paper.question_clip(path, numbers[index]) if crop else None
    return paper.render_page(path, numbers[index], DPI, clip=clip)


def reference(block):
    """Ссылка на источник словами экзамена: «May 2022 TZ2, Paper 1, Q3(b)»."""
    return (f"{block['session']} {block['zone']}, Paper {block['paper']}, "
            f"Q{block['question']}{part_label(block)}")
