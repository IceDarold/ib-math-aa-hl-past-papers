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


def block_pages(block, with_markscheme=True):
    """Картинки для одного блока архива: билет и схема оценивания."""
    out = {'question': render(block['dir'], 'question',
                              block.get('source_pages'), extra=1)}
    if with_markscheme:
        try:
            out['markscheme'] = render(block['dir'], 'markscheme',
                                       block.get('markscheme_pages'), extra=1)
        except LookupError:
            out['markscheme'] = []
    return out


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
