"""Страницы архива как картинки.

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

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

QUESTION_PDF = 'question-paper.pdf'
MARKSCHEME_PDF = 'markscheme.pdf'
DPI = 150
MAX_PAGES = 4


def parse_pages(spec):
    """«3», «3-4», «3, 5» → [3], [3, 4], [3, 5]."""
    pages = []
    for chunk in re.split(r'[;,]', str(spec or '')):
        chunk = chunk.strip()
        if not chunk:
            continue
        span = re.match(r'^(\d+)\s*[-–]\s*(\d+)$', chunk)
        if span:
            start, end = int(span.group(1)), int(span.group(2))
            pages += list(range(start, end + 1))
        elif chunk.isdigit():
            pages.append(int(chunk))
    return sorted(dict.fromkeys(pages))


@functools.lru_cache(maxsize=64)
def _render(path, number, dpi):
    with pymupdf.open(path) as document:
        if not 1 <= number <= document.page_count:
            raise LookupError(f'{path}: страницы {number} нет')
        return document[number - 1].get_pixmap(dpi=dpi).tobytes('png')


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
    numbers = parse_pages(spec)
    if extra and numbers:
        numbers = sorted(set(numbers) | {numbers[-1] + 1})
    images = []
    for number in numbers[:MAX_PAGES]:
        try:
            images.append(_render(path, number, dpi))
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

    hints = parse_pages(hint) or [1]
    start = None
    for candidate in _search_order(hints[0], total):
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


def _search_order(hint, total):
    """Подсказка корпуса, затем ближайшие страницы вокруг неё."""
    order = [hint]
    for step in range(1, SEARCH_RADIUS + 1):
        order += [hint + step, hint - step]
    return [n for n in order if 1 <= n <= total]


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


def page_image(block, which='question', index=0):
    """Одна страница блока картинкой."""
    numbers = block_page_numbers(block, which)
    if not 0 <= index < len(numbers):
        raise LookupError('такой страницы нет')
    name = QUESTION_PDF if which == 'question' else MARKSCHEME_PDF
    return _render(os.path.join(ROOT, block['dir'], name), numbers[index], DPI)


def reference(block):
    """Ссылка на источник словами экзамена: «May 2022 TZ2, Paper 1, Q3(b)»."""
    part = (block.get('part') or '').lower()
    # В корпусе поле part иногда повторяет номер вопроса — такую «часть»
    # печатать незачем, она не существует в бумаге.
    if not re.fullmatch(r'[a-z]+(?:-[ivx]+)*', part) or part == str(
            block.get('question', '')).lower():
        part = ''
    tail = f"({part.replace('-', ')(')})" if part else ''
    return (f"{block['session']} {block['zone']}, Paper {block['paper']}, "
            f"Q{block['question']}{tail}")
