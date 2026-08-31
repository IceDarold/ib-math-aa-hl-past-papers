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
import time

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


def render_upload(data, limit=6, dpi=DPI):
    """Присланный PDF — в картинки по страницам.

    Тетрадный лист приходит и снимком, и сканом: телефоны складывают
    несколько страниц в один PDF. Разбирать его на стороне страницы значило
    бы тащить в браузер pdf.js, тогда как PyMuPDF здесь уже есть и уже
    рендерит страницы архива.
    """
    with pymupdf.open(stream=data, filetype='pdf') as document:
        if not document.page_count:
            raise LookupError('в PDF нет страниц')
        return [document[number].get_pixmap(dpi=dpi).tobytes('png')
                for number in range(min(limit, document.page_count))]


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


SHEET_FONTS = ('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
               '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
               '/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf')

WORDS = {
    'ru': {
        'title': 'Вечер',
        'minutes': 'минут',
        'marks': 'баллов',
        'rule': 'В правом верхнем углу каждой страницы работы напиши номер '
                'задания — по нему страницы разложатся сами.',
        'head': ('№', 'вопрос', 'баллы', 'бумага', 'калькулятор'),
        'calc': {'yes': 'можно', 'no': 'нельзя'},
        'set': 'набор',
    },
    'en': {
        'title': 'Evening',
        'minutes': 'minutes',
        'marks': 'marks',
        'rule': 'Write the question number in the top-right corner of every '
                'page of your work, and the pages will sort themselves.',
        'head': ('#', 'question', 'marks', 'paper', 'calculator'),
        'calc': {'yes': 'allowed', 'no': 'not allowed'},
        'set': 'set',
    },
}


def _sheet_font():
    """Файл шрифта с кириллицей, если он в системе есть.

    Базовые четырнадцать шрифтов PDF кириллицы не знают, поэтому без файла
    лист собирается по-английски: лучше читаемая латиница, чем каша.
    """
    for path in SHEET_FONTS:
        if os.path.isfile(path):
            with open(path, 'rb') as handle:
                head = handle.read(4)
            if head[:4] in (b'\x00\x01\x00\x00', b'true', b'ttcf', b'OTTO'):
                return path
    return None


def build_sheet(questions, bank, minutes=None, set_id=None, when=None):
    """Лист заданий одним PDF: обложка со списком и страницы билетов.

    Страницы берутся из самих бумаг архива, а не рендерятся в картинки:
    так лист остаётся текстовым, печатается в исходном качестве и весит
    килобайты вместо мегабайт.
    """
    font = _sheet_font()
    words = WORDS['ru' if font else 'en']
    sheet = pymupdf.open()
    page = sheet.new_page(width=595, height=842)
    name = 'sheet'
    if font:
        page.insert_font(fontname=name, fontfile=font)
    else:
        name = 'helv'

    total = sum(q.get('marks') or 0 for q in questions)
    head = f"{words['title']}"
    if minutes:
        head += f" · {minutes} {words['minutes']}"
    head += f" · {total} {words['marks']}"

    y = 92
    page.insert_text((56, y), head, fontname=name, fontsize=19)
    y += 22
    tail = when or time.strftime('%Y-%m-%d')
    if set_id:
        tail += f" · {words['set']} {set_id}"
    page.insert_text((56, y), tail, fontname=name, fontsize=9.5)

    y += 40
    for text, x in zip(words['head'], (56, 86, 330, 396, 462)):
        page.insert_text((x, y), text, fontname=name, fontsize=9)
    y += 6
    page.draw_line(pymupdf.Point(56, y), pymupdf.Point(539, y),
                   width=0.6, color=(0.72, 0.72, 0.72))

    y += 18
    for question in questions:
        calculator = words['calc'].get(question.get('calculator'), '—')
        cells = ((str(question['n']), 56),
                 (question.get('reference') or question['block'], 86),
                 (str(question.get('marks') or ''), 330),
                 (f"P{question.get('paper')}" if question.get('paper')
                  else '—', 396),
                 (calculator, 462))
        for text, x in cells:
            page.insert_text((x, y), text, fontname=name, fontsize=10)
        y += 19

    y += 16
    page.draw_line(pymupdf.Point(56, y), pymupdf.Point(539, y),
                   width=0.6, color=(0.72, 0.72, 0.72))
    y += 22
    for line in _wrap(words['rule'], 74):
        page.insert_text((56, y), line, fontname=name, fontsize=10.5)
        y += 15

    for question in questions:
        block = bank['archive'][question['block']]
        _append_question(sheet, block, question['n'],
                         part=_asked_part(question.get('reference')),
                         marks=question.get('marks'))
    out = sheet.tobytes(deflate=True, garbage=3)
    sheet.close()
    return out


def _asked_part(reference):
    """«May 2022 TZ2, Paper 1, Q12(c)» → «Q12(c)»."""
    tail = (reference or '').rsplit(',', 1)[-1].strip()
    return tail if tail.startswith('Q') else ''


def _wrap(text, width):
    lines, line = [], ''
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            lines.append(line)
            line = word
        else:
            line = f'{line} {word}'.strip()
    if line:
        lines.append(line)
    return lines


def _append_question(sheet, block, number, part=None, marks=None):
    """Подшивает страницы одного вопроса и метит их номером.

    Номер стоит на самой странице билета: с него и списывают в угол
    рабочего листа, и ошибиться труднее. Рядом — какая часть вопроса
    нужна: на странице их обычно несколько, а спрашивается одна.
    """
    path = os.path.join(ROOT, block['dir'], QUESTION_PDF)
    numbers = block_page_numbers(block, 'question')
    if not os.path.isfile(path) or not numbers:
        raise LookupError(f"нет страниц для {block.get('id') or block['dir']}")
    with pymupdf.open(path) as source:
        for page_number in numbers[:MAX_PAGES]:
            if not 1 <= page_number <= source.page_count:
                continue
            at = sheet.page_count
            sheet.insert_pdf(source, from_page=page_number - 1,
                             to_page=page_number - 1)
            stamped = sheet[at]
            box = stamped.rect
            # Ниже колонтитула: наверху страницы стоят номер листа и код
            # бумаги, и метка на них налезала.
            centre = pymupdf.Point(box.x1 - 42, box.y0 + 86)
            stamped.draw_circle(centre, 17, color=(0.8, 0.1, 0.1), width=1.2)
            stamped.insert_text(
                pymupdf.Point(centre.x - 5 * len(str(number)), centre.y + 6),
                str(number), fontname='helv', fontsize=17,
                color=(0.8, 0.1, 0.1))
            label = ' '.join(str(bit) for bit in (part, f'[{marks}]'
                                                  if marks else None) if bit)
            if label:
                stamped.insert_text(
                    pymupdf.Point(centre.x - 4 * len(label), centre.y + 30),
                    label, fontname='helv', fontsize=8,
                    color=(0.8, 0.1, 0.1))


def shrink(png, max_side=1100):
    """Уменьшенная копия страницы для дешёвого прохода.

    Раскладке страниц по заданиям нужна цифра в углу, а не математика.
    Гнать туда полный разворот в 150 dpi — платить за то, что не читают.
    """
    try:
        pix = pymupdf.Pixmap(png)
        while max(pix.width, pix.height) > max_side:
            pix.shrink(1)          # каждый шаг делит сторону пополам
        return pix.tobytes('png')
    except Exception:  # noqa: BLE001
        return png                 # уменьшить не вышло — шлём как есть
