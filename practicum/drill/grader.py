"""Разбор письменной работы: математика отдельно, оформление отдельно.

Тренажёр проверяет ответ, а экзамен платит за запись. Здесь проверяется
именно запись: виден ли ход, названо ли предположение индукции, написан ли
вывод словами, стоит ли ответ в напечатанной форме. Рубрики лежат в
presentation.yaml и задаются явно — на вкус модели это не оставляется.

Опора — подлинник: страница билета и страница схемы оценивания уходят
картинками вместе с работой. Разбор идёт по-английски: язык экзамена
и есть то, чему учимся.

Модель ничего не решает про ответ там, где есть машинная проверка: она
говорит про метод и оформление, и её вердикт помечается отдельно.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))

API_URL = os.environ.get('DRILL_GRADER_URL',
                         'https://api.openai.com/v1/chat/completions')
MODEL = os.environ.get('DRILL_GRADER_MODEL', 'gpt-5.6-sol')
KEY_FILE = os.environ.get('DRILL_GRADER_KEY_FILE', '/etc/drill/openai.env')
TIMEOUT = 240
MAX_PHOTOS = 6


class GraderError(RuntimeError):
    """Разбор не состоялся: нет ключа, сеть, или модель ответила не тем."""


def api_key():
    """Ключ из окружения, иначе из файла службы. В репозитории его нет."""
    key = os.environ.get('OPENAI_API_KEY')
    if key:
        return key
    if os.path.isfile(KEY_FILE):
        for line in open(KEY_FILE):
            name, _, value = line.strip().partition('=')
            if name == 'OPENAI_API_KEY' and value:
                return value
    raise GraderError('ключ проверяющей модели не найден')


def rubric(practicum=None):
    """Пункты оформления: общие, по типу вопроса и по практикуму."""
    with open(os.path.join(HERE, 'presentation.yaml')) as fh:
        data = yaml.safe_load(fh)
    items = list(data['common'])
    for name, group in data.get('by_question_type', {}).items():
        for item in group['items']:
            items.append(dict(item, applies_when=group['when']))
    if practicum:
        items += data.get('by_practicum', {}).get(practicum, [])
    return items


SYSTEM = """You are an experienced IB Mathematics: Analysis and Approaches HL examiner.
You mark a photographed handwritten solution the way a real examiner does, against the markscheme.

Judge two things separately and never merge them:
  1. MATHEMATICS — is the reasoning correct, and is the answer right?
  2. PRESENTATION — is it written the way the markscheme requires?
A candidate can be mathematically perfect and still lose marks on presentation. Say so plainly when that happens.

Rules you must follow:
- Transcribe the work first, before judging anything. If the handwriting is unclear, say so in the transcription rather than guessing and then criticising.
- A correct answer reached by an invalid method is not correct. Name the invalid step.
- Judge presentation only against the rubric you are given. Do not invent additional style requirements, and do not penalise ordinary abbreviations or untidy handwriting.
- Work the candidate has crossed out is not marked at all, and where two different answers are offered only the first one counts. Follow that: do not rescue a candidate by marking crossed-out work or a better second attempt.
- The official Instructions to Examiners come from the front of this markscheme and are authoritative. Where the rubric asks for more than they require, follow them and mark the rubric item as met.
- Mark codes: M1 method, A1 accuracy, R1 reasoning, AG answer given in the question.
- Write every word of your feedback in English. The candidate is practising exam register, so your phrasing is part of the teaching.
- In "fix" fields give the exact sentence the candidate should have written, not a description of what is missing.
- Write every mathematical expression in LaTeX between dollar signs, in "model_write_up", in "one_thing", in the "fix" fields and in the lines you quote: $n = k + 1$, $\\frac{k(k+1)}{2}$, $\\sum_{r=1}^{n} r$. A whole displayed line may use $$...$$. Keep one step per line and keep the line breaks — the page renders this, and plain ASCII like k(k+1)/2 renders badly.
- Do not put LaTeX in "transcription": that field must show the page as written, symbol for symbol.

Reply with strict JSON only, in this shape:
{
  "transcription": "<what you read, line by line, as plain text>",
  "legible": true|false,
  "mathematics": {
    "verdict": "correct"|"partially correct"|"incorrect",
    "errors": [{"line": "<the line where it goes wrong>", "problem": "<what is wrong>", "consequence": "<what it costs>"}]
  },
  "presentation": [{"id": "<rubric id>", "met": true|false, "code": "M1|A1|R1|AG", "comment": "<one sentence>", "fix": "<exact sentence to write>"}],
  "marks": {"available": <int or null>, "earned": <int>, "lost": [{"code": "M1|A1|R1|AG", "why": "<one sentence>"}]},
  "model_write_up": "<the candidate's own solution rewritten as a markscheme-quality write-up, in English, with all mathematics in LaTeX between dollar signs and one step per line>",
  "one_thing": "<the single most valuable change for next time, one sentence>"
}"""


def _image_part(data, kind='png'):
    if data[:2] == b'\xff\xd8':      # JPEG начинается с SOI
        kind = 'jpeg'
    return {'type': 'image_url', 'image_url': {
        'url': f'data:image/{kind};base64,' + base64.b64encode(data).decode()}}


def build_messages(*, work_images, question_text=None, question_images=(),
                   markscheme_images=(), instructions=None, reference=None,
                   marks=None, calculator=None, rubric_items=(), skill=None):
    """Собирает запрос: сначала задача и эталон разметки, потом работа."""
    content = []
    head = ['You are marking one question.']
    if reference:
        head.append(f'Source: {reference}.')
    if marks:
        head.append(f'The question is worth {marks} marks.')
    if calculator is not None:
        head.append('A calculator is allowed.' if calculator in ('yes', True)
                    else 'No calculator is allowed.')
    if skill:
        head.append(f'The technique being practised is: {skill}.')
    content.append({'type': 'text', 'text': ' '.join(head)})

    if question_text:
        content.append({'type': 'text',
                        'text': f'QUESTION:\n{question_text}'})
    if question_images:
        content.append({'type': 'text',
                        'text': 'QUESTION PAPER PAGE(S) — the question is on '
                                'these pages; ignore other questions on them.'})
        content += [_image_part(png) for png in question_images]
    if markscheme_images:
        content.append({'type': 'text',
                        'text': 'OFFICIAL MARKSCHEME PAGE(S) — mark against '
                                'this, and use its mark codes and wording.'})
        content += [_image_part(png) for png in markscheme_images]

    if instructions:
        content.append({'type': 'text', 'text':
                        'OFFICIAL INSTRUCTIONS TO EXAMINERS — printed at the '
                        'front of this very markscheme. These are the rules '
                        'you mark by, and they outrank the rubric below '
                        'wherever the two disagree:\n\n' + instructions})
    content.append({'type': 'text', 'text':
                    'PRESENTATION RUBRIC — judge presentation only against '
                    'these items, and drop any item the official '
                    'instructions above contradict:\n'
                    + json.dumps(list(rubric_items), ensure_ascii=False,
                                 indent=1)})
    content.append({'type': 'text',
                    'text': "CANDIDATE'S HANDWRITTEN WORK:"})
    content += [_image_part(png) for png in work_images[:MAX_PHOTOS]]
    return [{'role': 'system', 'content': SYSTEM},
            {'role': 'user', 'content': content}]


def grade(**kwargs):
    """Отправляет разбор и возвращает разобранный ответ модели."""
    model = kwargs.pop('model', None) or MODEL
    messages = build_messages(**kwargs)
    body = {'model': model, 'messages': messages,
            'response_format': {'type': 'json_object'}}
    request = urllib.request.Request(
        API_URL, method='POST', data=json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {api_key()}',
                 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = ''
        try:
            detail = json.load(error).get('error', {}).get('message', '')
        except Exception:  # noqa: BLE001
            pass
        raise GraderError(f'модель ответила {error.code}: {detail[:200]}')
    except OSError as error:
        raise GraderError(f'сеть недоступна: {error}')

    try:
        verdict = json.loads(payload['choices'][0]['message']['content'])
    except (KeyError, IndexError, json.JSONDecodeError) as error:
        raise GraderError(f'ответ модели не разобрался: {error}')

    verdict['model'] = payload.get('model', model)
    verdict['usage'] = payload.get('usage', {})
    return verdict


SPLIT_MODEL = os.environ.get('DRILL_SPLIT_MODEL', MODEL)
SPLIT_TIMEOUT = 120

SPLIT_SYSTEM = """You sort scanned pages of handwritten mathematics homework.

The student solved several questions on paper and scanned everything in one
go. Each page should carry the question number, written by hand in the
top-right corner. Your only job is to say which question each page belongs to.

Read the corner first. If a page has no number, continue the previous page:
work runs on. Never drop a page and never invent a question number outside
the given range.

Reply with JSON only: {"pages": [{"page": 1, "question": 2, "sure": true}]}
"page" is the 1-based position in the order given. "sure" is false when you
had to guess from the flow rather than read a number."""


def assign_pages(pages, count, model=None):
    """К какому заданию относится каждая страница присланной работы.

    Возвращает список номеров по одному на страницу. Дешёвый проход: от
    модели требуется прочесть цифру в углу, а не понять математику, и
    картинки идут уменьшенными. Раскладку всё равно подтверждают глазами,
    поэтому ошибка здесь стоит одного нажатия, а не балла.
    """
    if not pages:
        return []
    content = [{'type': 'text', 'text':
                f'There are {count} questions, numbered 1 to {count}, and '
                f'{len(pages)} pages below, in the order they were scanned.'}]
    for number, png in enumerate(pages, start=1):
        content.append({'type': 'text', 'text': f'PAGE {number}:'})
        content.append(_image_part(png))

    body = {'model': model or SPLIT_MODEL,
            'messages': [{'role': 'system', 'content': SPLIT_SYSTEM},
                         {'role': 'user', 'content': content}],
            'response_format': {'type': 'json_object'}}
    request = urllib.request.Request(
        API_URL, method='POST', data=json.dumps(body).encode(),
        headers={'Authorization': f'Bearer {api_key()}',
                 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=SPLIT_TIMEOUT) as response:
            payload = json.load(response)
        answer = json.loads(payload['choices'][0]['message']['content'])
    except (urllib.error.URLError, KeyError, IndexError, ValueError) as exc:
        raise GraderError(f'раскладка страниц не удалась: {exc}') from exc

    seen = {}
    for row in answer.get('pages') or ():
        try:
            page, question = int(row['page']), int(row['question'])
        except (KeyError, TypeError, ValueError):
            continue
        if 1 <= page <= len(pages) and 1 <= question <= count:
            seen[page] = question
    # Пропущенную страницу тянем за предыдущей: работа обычно продолжается.
    out, last = [], 1
    for page in range(1, len(pages) + 1):
        last = seen.get(page, last)
        out.append(last)
    return out
