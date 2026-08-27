#!/usr/bin/env python3
"""Собирает практикум в PDF со страницей размером с экран телефона.

Ноутбук в дороге всё равно не запустить, а читать и думать над ним хочется.
Обычный A4 на телефоне требует зумить и таскать страницу вбок; здесь страница
делается узкой (по умолчанию 90×160 мм), и текст занимает экран целиком.

    python practicum/make_pdf.py A4              # один практикум
    python practicum/make_pdf.py B4:archive      # архивный ноутбук темы
    python practicum/make_pdf.py --all           # все со status: ready
    python practicum/make_pdf.py A4 --tasks      # без раздела решений
    python practicum/make_pdf.py A4 --page 76x135 --font 12   # крупнее шрифт

Источник правды — practicum/map.yaml, как и у make_kaggle.py.

Формулы верстает KaTeX: он скачивается один раз в ~/.cache/ib-practicum
и дальше работает офлайн. Печатает headless Chromium через playwright.
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request

try:
    import yaml
except ImportError:
    sys.exit("нужен pyyaml: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KATEX_DIR = os.path.expanduser('~/.cache/ib-practicum/katex')
KATEX_URL = 'https://registry.npmjs.org/katex/latest'

# Ширина страницы в миллиметрах и кегль в пунктах. 90×160 — примерно пропорции
# телефона: страница влезает в экран по ширине, горизонтальной прокрутки нет.
DEFAULT_PAGE = '90x160'
DEFAULT_FONT = 10.5

# Поля страницы в миллиметрах. Из них считается ширина колонки, а она нужна
# не только вёрстке: браузер меряет формулы в экранном вьюпорте, и если тот
# не сузить до печатной ширины, переполнения не видно вовсе.
MARGIN = dict(top=8, right=6, bottom=10, left=6)


def load_map():
    with open(os.path.join(ROOT, 'practicum/map.yaml')) as fh:
        cmap = yaml.safe_load(fh)
    out = {}
    for sec in cmap['sections'].values():
        for p in sec['practicums']:
            out[p['id']] = p
    return out


def ensure_katex():
    """Кладёт дистрибутив KaTeX в кэш. Сеть нужна ровно один раз."""
    marker = os.path.join(KATEX_DIR, 'katex.min.css')
    if os.path.exists(marker):
        return KATEX_DIR
    print('  KaTeX не найден в кэше, качаю...')
    try:
        meta = json.load(urllib.request.urlopen(KATEX_URL, timeout=60))
        raw = urllib.request.urlopen(meta['dist']['tarball'], timeout=300).read()
    except OSError as e:
        sys.exit(f"не удалось скачать KaTeX ({e}). Нужна сеть — но только "
                 f"в первый раз, дальше он лежит в {KATEX_DIR}")
    os.makedirs(KATEX_DIR, exist_ok=True)
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        members = [m for m in tf.getmembers()
                   if m.name.startswith('package/dist/')
                   and m.name.endswith(('.css', '.js', '.woff2'))]
        for m in members:
            m.name = m.name[len('package/dist/'):]
        tf.extractall(KATEX_DIR, members=members, filter='data')
    print(f"  KaTeX {meta['version']} -> {KATEX_DIR}")
    return KATEX_DIR


# --- markdown ---------------------------------------------------------------

def make_markdown():
    """markdown-it с таблицами и долларовой математикой.

    Математика не отдаётся markdown на растерзание: внутри формул полно
    подчёркиваний и звёздочек, которые он превратил бы в курсив. Плагин
    dollarmath вырезает формулы в отдельные токены раньше всех прочих правил,
    а рендерятся они уже в браузере.
    """
    from markdown_it import MarkdownIt
    from mdit_py_plugins.dollarmath import dollarmath_plugin

    md = MarkdownIt('commonmark', {'html': False, 'typographer': True})
    md.enable(['table', 'strikethrough'])
    md.use(dollarmath_plugin, double_inline=True)

    def esc(text):
        return (text.replace('&', '&amp;').replace('<', '&lt;')
                    .replace('>', '&gt;'))

    def inline(self, tokens, idx, options, env):
        return f'<span class="tex" data-d="0">{esc(tokens[idx].content)}</span>'

    def block(self, tokens, idx, options, env):
        return f'<div class="tex" data-d="1">{esc(tokens[idx].content)}</div>\n'

    md.add_render_rule('math_inline', inline)
    md.add_render_rule('math_inline_double', block)
    md.add_render_rule('math_block', block)
    return md


# Заголовки в ноутбуках нередко идут после горизонтальной черты, то есть
# не в начале ячейки. Поэтому везде search с re.M, а не match: match якорится
# в позицию 0 и re.M ему не помогает — на этом легко потерять весь раздел.
# Заголовок раздела решений в разных практикумах записан по-разному:
# «# Решения» в A4 и «# 🔑 Решения» в остальных семи. Поэтому между решёткой
# и словом допускается что угодно — вторая решётка сюда не подойдёт,
# так что «## Решение 5» под правило не попадает.
RE_SOLUTIONS = re.compile(r'^\s{0,3}#\s.*Решения', re.M)
RE_TASK = re.compile(r'^\s{0,3}##\s+Задание', re.M)
RE_HEADING = re.compile(r'^\s{0,3}(#{1,3})\s+(.+?)\s*$', re.M)


def cells_html(nb, md, with_solutions=True):
    """Ячейки ноутбука в HTML. Код показывается, но выделен как несъедобный."""
    out, skipping = [], False
    for cell in nb['cells']:
        src = ''.join(cell['source'])
        if cell['cell_type'] == 'markdown':
            if RE_SOLUTIONS.search(src) and not with_solutions:
                skipping = True
                continue
            if skipping:
                continue
            out.append(md.render(src))
        elif not skipping:
            out.append(f'<pre class="code">{_esc(src.strip())}</pre>')
    return '\n'.join(out)


def headings(nb, with_solutions=True):
    """Заголовки в порядке следования — для починки закладок PDF.

    Chromium собирает оглавление по свёрстанному тексту и на переносе строки
    склеивает слова без пробела («множитель однойподстановкой»). Здесь берутся
    исходные заголовки, чтобы потом подставить их вместо испорченных.
    """
    found, skipping = [], False
    for cell in nb['cells']:
        if cell['cell_type'] != 'markdown':
            continue
        src = ''.join(cell['source'])
        if RE_SOLUTIONS.search(src) and not with_solutions:
            skipping = True
        if skipping:
            continue
        for _, title in RE_HEADING.findall(src):
            found.append(re.sub(r'[*_`]', '', title).strip())
    return found


def _esc(text):
    return (text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


# --- страница ---------------------------------------------------------------

CSS = """
@page {{
  size: {w}mm {h}mm;
  margin: {mt}mm {mr}mm {mb}mm {ml}mm;
}}
html {{ -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{
  font-family: 'DejaVu Serif', Georgia, serif;
  font-size: {fs}pt;
  line-height: 1.5;
  color: #14181d;
  margin: 0;
  hyphens: auto;
  -webkit-hyphens: auto;
  text-align: justify;
  text-justify: inter-word;
}}
p {{ margin: 0 0 .55em; orphans: 2; widows: 2; }}
/* Длинное неразрывное слово (ссылка, имя функции) шире колонки заставляет
   Chromium ужать при печати весь документ — заказанный кегль молча
   становится меньше. Разрешаем рвать такие слова где угодно. */
p, li, dd, dt, td, th, h1, h2, h3 {{ overflow-wrap: break-word; }}

h1, h2, h3 {{
  font-family: 'DejaVu Sans', Arial, sans-serif;
  line-height: 1.25;
  text-align: left;
  break-after: avoid-page;
  hyphens: none;
}}
h1 {{ font-size: 1.5em; margin: 0 0 .7em; break-before: page; }}
h1:first-child {{ break-before: auto; }}
h2 {{ font-size: 1.16em; margin: 1.5em 0 .5em; }}
h3 {{ font-size: 1.0em; margin: 1.2em 0 .4em; color: #33404d; }}

hr {{ border: 0; border-top: .6pt solid #c9d2da; margin: 1.4em 0; }}

ul, ol {{ margin: 0 0 .6em; padding-left: 1.25em; }}
li {{ margin-bottom: .28em; }}

strong {{ font-weight: 700; }}
em {{ font-style: italic; }}

code {{
  font-family: 'DejaVu Sans Mono', monospace;
  font-size: .8em;
  background: #eef2f6;
  padding: 0 .18em;
  border-radius: 2px;
  overflow-wrap: anywhere;
}}
pre {{
  font-family: 'DejaVu Sans Mono', monospace;
  font-size: .74em;
  line-height: 1.4;
  background: #f4f7fa;
  border-left: 2pt solid #b9c6d3;
  padding: .45em .5em;
  margin: .55em 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  text-align: left;
  hyphens: none;
  break-inside: avoid-page;
}}
pre code {{ background: none; padding: 0; font-size: 1em; }}
/* Ячейки самого ноутбука: их в дороге не запустить, поэтому приглушены. */
pre.code {{ background: #f7f7f5; border-left-color: #d8d8d2; color: #4a5058; }}

table {{
  border-collapse: collapse;
  width: 100%;
  font-size: .8em;
  margin: .6em 0;
  break-inside: avoid-page;
}}
th, td {{
  border: .5pt solid #c2ccd6;
  padding: .22em .35em;
  text-align: left;
  vertical-align: top;
  /* Колонки узкие, но рвать слово посреди («Множит-ель») незачем: сначала
     переносим по правилам, и только неразрывно длинное ломаем силой. */
  hyphens: auto;
  -webkit-hyphens: auto;
  overflow-wrap: break-word;
}}
th {{ background: #eef2f6; font-weight: 700; }}

blockquote {{
  margin: .6em 0;
  padding-left: .7em;
  border-left: 2pt solid #c9d2da;
  color: #414a55;
}}

.tex[data-d="1"] {{
  display: block;
  margin: .7em 0;
  text-align: center;
  break-inside: avoid-page;
}}
/* KaTeX кладёт рядом с картинкой формулы её же MathML — для экранных
   читалок. Он спрятан клипом, но ширину занимает, и Chromium при печати
   ужимает по нему весь документ: из-за одной формулы 10.5 pt превращались
   в 7. В PDF этот слой не нужен, убираем совсем. */
.katex-mathml {{ display: none !important; }}

/* Длинная формула не должна уезжать за поле: лучше уменьшить её. */
.katex-display {{ margin: 0; }}
/* Только на время замера: центрирование прячет половину выноса. */
.tex.measuring,
.tex.measuring .katex-display,
.tex.measuring .katex-display > .katex {{ text-align: left !important; }}
.katex {{ font-size: 1.02em; }}
.katex-display > .katex {{ font-size: 1.04em; }}

.cover {{ text-align: left; break-after: page; }}
.cover h1 {{ break-before: auto; font-size: 1.7em; margin-bottom: .3em; }}
.cover .sub {{ font-size: .95em; color: #46505b; margin-bottom: 1.4em; }}
.cover dl {{ margin: 0; font-size: .88em; }}
.cover dt {{ font-weight: 700; margin-top: .7em;
             font-family: 'DejaVu Sans', sans-serif; }}
.cover dd {{ margin: .1em 0 0; overflow-wrap: anywhere; }}
.cover .foot {{ margin-top: 2em; font-size: .78em; color: #6b7681; }}
"""

PAGE = """<!doctype html>
<html lang="ru"><head><meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="katex/katex.min.css">
<style>{css}</style>
</head><body>
{cover}
{content}
<script src="katex/katex.min.js"></script>
<script>
  window.__texErrors = [];

  // Длинная выкладка вида «A = B = C» в колонку шириной 78 мм не влезает
  // никогда. Ужимать её до половины кегля бессмысленно — читать всё равно
  // нельзя. Поэтому она разрезается по знакам отношения на верхнем уровне
  // вложенности и собирается обратно в aligned: ровно так её и написал бы
  // человек на узком листе.
  var RELATIONS = ['\\\\Longleftrightarrow', '\\\\Longrightarrow', '\\\\Rightarrow',
                   '\\\\implies', '\\\\iff', '\\\\equiv', '\\\\approx',
                   '\\\\leq', '\\\\geq', '\\\\le', '\\\\ge', '\\\\neq', '='];

  var TERMS = ['+', '-'];
  var SEPARATORS = [',', '\\\\qquad', '\\\\quad'];

  // Режет TeX по операторам, стоящим на нулевой глубине вложенности.
  // Считаются и фигурные скобки (дроби, индексы, \\text), и круглые с
  // квадратными: в TeX они обычные символы, и без их учёта (\\alpha+\\beta)
  // разрезается посередине.
  function splitTokens(tex, ops) {{
    var depth = 0, parts = [], cur = '', i = 0;
    while (i < tex.length) {{
      var c = tex[i];
      if (c === '{{' || c === '(' || c === '[') depth++;
      else if (c === '}}' || c === ')' || c === ']') depth--;
      if (depth === 0 && cur.trim()) {{      // ведущий унарный минус — не оператор
        var op = null;
        for (var k = 0; k < ops.length; k++) {{
          var r = ops[k];
          if (tex.startsWith(r, i)) {{
            // \\le — префикс \\left, поэтому следом не должно быть буквы
            var next = tex[i + r.length];
            if (r[0] !== '\\\\' || !next || !/[a-zA-Z]/.test(next)) {{ op = r; break; }}
          }}
        }}
        if (op) {{
          parts.push({{text: cur, op: op}});
          cur = '';
          i += op.length;
          continue;
        }}
      }}
      cur += c;
      i++;
    }}
    parts.push({{text: cur, op: null}});
    return parts;
  }}

  // Собирает лесенку. Порог в символах — грубая прикидка: точную ширину знает
  // только браузер, но резать заведомо короткие строки незачем.
  var WRAP = 42;

  // Ставит знак выравнивания перед первым отношением: в столбик формулы
  // читаются по знакам равенства, а не по левому краю.
  function alignAt(text) {{
    var p = splitTokens(text, RELATIONS);
    if (p.length < 2) return '&' + text.trim();
    var tail = '';
    for (var i = 1; i < p.length; i++) {{
      tail += (i > 1 ? p[i - 1].op : '') + p[i].text;
    }}
    return p[0].text.trim() + ' &' + p[0].op + ' ' + tail.trim();
  }}

  function layoutWide(tex) {{
    // Первым делом смотрим на разделители. Формула вида «A = B, C = D, E = F»
    // это перечисление независимых равенств, и резать её надо по запятым,
    // а не по знакам равенства: иначе левая часть одного равенства уезжает
    // в строку к правой части предыдущего.
    var items = splitTokens(tex, SEPARATORS);
    var lines;
    if (items.length >= 3) {{
      lines = [];
      for (var i = 0; i < items.length; i++) {{
        var body = items[i].text.trim();
        if (!body) continue;
        lines.push(alignAt(body) + (items[i].op === ',' ? ',' : ''));
      }}
    }} else {{
      var rel = splitTokens(tex, RELATIONS);
      if (rel.length >= 3) {{
        // A = B = C: каждое следующее равенство с новой строки
        lines = [rel[0].text.trim() + ' &' + rel[0].op + ' ' + rel[1].text.trim()];
        for (var j = 1; j < rel.length - 1; j++) {{
          lines.push('&' + rel[j].op + ' ' + rel[j + 1].text.trim());
        }}
      }} else if (rel.length === 2) {{
        // Одно отношение: знак остаётся в конце первой строки, правая часть
        // уходит вниз с отступом — как переносят формулу от руки.
        lines = ['&' + rel[0].text.trim(),
                 '&\\\\qquad ' + rel[0].op + ' ' + rel[1].text.trim()];
      }} else {{
        lines = ['&' + tex.trim()];
      }}
    }}

    // Второй уровень: строка, которая и так длинна, дополнительно режется
    // по плюсам и минусам верхнего уровня.
    var out = [];
    lines.forEach(function (ln) {{
      if (ln.length <= WRAP) {{ out.push(ln); return; }}
      var head = ln.replace(/^&(\\\\qquad )?/, '');
      var terms = splitTokens(head, TERMS);
      if (terms.length < 3) {{ out.push(ln); return; }}
      // Знак операции уходит в начало переносимой строки, а не остаётся
      // в конце предыдущей: так формулу переносят в книгах, и так сразу
      // видно, что строка — продолжение, а не новое выражение.
      out.push('&' + terms[0].text.trim());
      for (var j = 1; j < terms.length; j++) {{
        out.push('&\\\\qquad ' + terms[j - 1].op + ' ' + terms[j].text.trim());
      }}
    }});
    if (out.length < 2) return null;
    return '\\\\begin{{aligned}}' + out.join(' \\\\\\\\ ') + '\\\\end{{aligned}}';
  }}

  function draw(el, tex) {{
    katex.render(tex, el, {{
      displayMode: el.dataset.d === '1', throwOnError: true, strict: false,
    }});
  }}

  function contentWidth(el) {{
    var range = document.createRange();
    range.selectNodeContents(el);
    return range.getBoundingClientRect().width;
  }}

  document.querySelectorAll('.tex').forEach(function (el) {{
    var tex = el.textContent;
    el.dataset.src = tex;          // katex.render затрёт содержимое
    try {{
      draw(el, tex);
    }} catch (e) {{
      window.__texErrors.push(tex.slice(0, 70) + '  ||  ' + e.message);
      el.textContent = tex;
      el.style.color = '#b00';
    }}
  }});

  // Колонка узкая, и длинная выкладка в неё не влезает. Перенести формулу
  // KaTeX не умеет, обрезать её нельзя, поэтому такие формулы ужимаются
  // по ширине — до разумного предела, дальше уже нечитаемо.
  // Не влезающая формула дорого стоит: Chromium при печати ужимает по самому
  // широкому элементу ВЕСЬ документ, и из-за одной строки 10.5 pt становятся
  // семью. Поэтому такие формулы подгоняются по ширине колонки поштучно.
  //
  // Мерить можно только после document.fonts.ready. Шрифты KaTeX грузятся
  // асинхронно, и до их появления формулы свёрстаны запасным шрифтом —
  // заметно уже. Замеры получаются оптимистичными, подгонка недотягивает,
  // а потом шрифты приезжают и формулы разъезжаются обратно.
  window.__shrunk = [];
  document.fonts.ready.then(function () {{
  var COL = document.body.clientWidth;
  document.querySelectorAll('.tex').forEach(function (el) {{
    var display = el.dataset.d === '1';
    // На время замера блочная формула прижимается влево. У центрированной
    // вынос делится поровну на обе стороны: scrollWidth видит половину,
    // а Range упирается в колонку и показывает ровно её ширину — обе меры
    // занижают, и подгонка недотягивает. Прижатая выносит всё вправо,
    // и scrollWidth становится точным. Мерить по внутренним узлам KaTeX
    // нельзя: в 0.18 .base переименован в .katex-base, и проверка молча
    // перестаёт находить переполнение.
    if (display) el.classList.add('measuring');

    function overflow() {{
      var avail = display ? el.clientWidth : COL;
      if (avail <= 0) return 0;
      var need = display ? el.scrollWidth : contentWidth(el);
      return need > avail + 0.5 ? need / avail : 0;
    }}

    // Сначала пробуем разрезать выкладку по знакам отношения: строка
    // «A = B = C» на узкой колонке читается лесенкой куда лучше, чем та же
    // строка, ужатая вдвое. Сжатие остаётся на случай, когда резать нечего —
    // одна длинная дробь или произведение скобок.
    var scale = 1;
    if (display && overflow() > 1) {{
      var split = layoutWide(el.dataset.src || '');
      if (split) {{
        var before = el.innerHTML;
        try {{
          draw(el, split);
        }} catch (e) {{
          el.innerHTML = before;    // разрез породил неверный TeX — откат
        }}
      }}
    }}
    for (var pass = 0; pass < 4; pass++) {{
      var ratio = overflow();
      if (!ratio) break;
      scale = Math.max(0.5, scale * (1 / ratio) * 0.97);
      el.style.fontSize = scale * 100 + '%';
    }}
    el.classList.remove('measuring');
    if (scale < 0.62) {{
      window.__shrunk.push(Math.round(scale * 100) + '%: '
                           + (el.dataset.src || '').replace(/\\s+/g, ' ').slice(0, 55));
    }}
  }});

  // Если после всех подгонок что-то шире колонки, Chromium при печати
  // молча ужмёт ВЕСЬ документ, и заказанный кегль тихо превратится
  // в меньший. Молчать об этом нельзя: сообщаем, что именно не влезло.
  //
  // Запас равен полю страницы. Мелкий вынос в поле безвреден: там пусто,
  // и ничего не обрезается. Курсив свисает на пару пикселей всегда, а pre
  // с white-space: pre-wrap по стандарту вывешивает хвостовые пробелы
  // за край строки — без запаса предупреждение срабатывало бы вхолостую.
  window.__wide = [];
  var SLACK = {slack};
  // pre в список не входит намеренно. С white-space: pre-wrap и переносом
  // в любом месте он за колонку не выходит, зато по стандарту вывешивает
  // за край хвостовые пробелы строки — они не печатаются, но scrollWidth
  // их считает, и проверка срабатывала бы на каждом выровненном комментарии.
  document.querySelectorAll('p, li, dd, dt, td, th, table, .tex, h1, h2, h3')
          .forEach(function (el) {{
    var need = Math.max(el.scrollWidth, contentWidth(el));
    if (need > COL + SLACK) {{
      var what = (el.textContent || '').replace(/\\s+/g, ' ').trim().slice(0, 45);
      window.__wide.push(el.tagName.toLowerCase() + ' шире колонки на '
                         + Math.round(need - COL) + ' px: «' + what + '»');
    }}
  }});
  window.__ready = true;
  }});
</script>
</body></html>
"""

COVER = """<section class="cover">
<h1>{title}</h1>
<div class="sub">{subtitle}</div>
<dl>{items}</dl>
<div class="foot">{foot}</div>
</section>
"""


def cover_html(entry, nb, with_solutions):
    """Титульная страница: чем этот практикум занят и сколько в нём чего."""
    first = ''.join(nb['cells'][0]['source'])
    # Первый абзац после заголовка — короткая характеристика темы.
    body = first.split('\n', 1)[1] if '\n' in first else ''
    m = re.search(r'\*\*(.+?)\*\*(.*?)(?:\n\n|\Z)', body, re.S)
    subtitle = ''
    if m:
        subtitle = re.sub(r'\s+', ' ', (m.group(1) + m.group(2))).strip()
        subtitle = re.sub(r'[*_`$]', '', subtitle)

    tasks = sum(1 for c in nb['cells'] if c['cell_type'] == 'markdown'
                and RE_TASK.search(''.join(c['source'])))
    items = []
    # note в map.yaml записан свёрнутым скаляром: пустая строка в исходнике
    # превращается в одиночный \n, поэтому первый абзац отрезается по нему.
    note = (entry.get('note') or entry.get('exception') or '').strip()
    if note:
        items.append(('О практикуме', re.sub(r'\s+', ' ', note.split('\n')[0])))
    items.append(('Заданий', str(tasks)))
    items.append(('Раздел решений', 'включён' if with_solutions else 'не включён'))
    if entry.get('kaggle'):
        items.append(('Интерактивная версия',
                      f"kaggle.com/code/artemkonukhov/{entry['kaggle']}"))
    body_items = ''.join(f'<dt>{_esc(k)}</dt><dd>{_esc(v)}</dd>' for k, v in items)
    return COVER.format(
        title=_esc(f"Практикум {entry['id']}"),
        subtitle=_esc(subtitle),
        items=body_items,
        foot=_esc('Собрано из ноутбука репозитория ib-math-aa-hl-past-papers. '
                  'Проверки в PDF не работают — они для интерактивной версии.'),
    )


FOOTER = ("<div style=\"font-family:'DejaVu Sans',sans-serif;font-size:6.5pt;"
          "color:#8a939c;width:100%;text-align:center;padding:0 6mm;\">"
          "<span class=\"pageNumber\"></span></div>")


def render(entry, page, font, with_solutions, out_dir):
    katex = ensure_katex()
    md = make_markdown()
    nb = json.load(open(os.path.join(ROOT, entry['notebook'])))

    w, h = (float(v) for v in page.lower().split('x'))
    column_mm = w - MARGIN['left'] - MARGIN['right']
    if column_mm < 30:
        sys.exit(f'страница {w:g} мм слишком узкая для полей по '
                 f"{MARGIN['left']} мм")
    html = PAGE.format(
        title=f"Практикум {entry['id']}",
        css=CSS.format(w=w, h=h, fs=font, mt=MARGIN['top'], mr=MARGIN['right'],
                       mb=MARGIN['bottom'], ml=MARGIN['left']),
        cover=cover_html(entry, nb, with_solutions),
        content=cells_html(nb, md, with_solutions),
        slack=round(MARGIN['right'] / 25.4 * 96),
    )

    os.makedirs(out_dir, exist_ok=True)
    name = os.path.basename(entry['notebook']).replace('.ipynb', '.pdf')
    out = os.path.join(out_dir, name)

    with tempfile.TemporaryDirectory() as tmp:
        # KaTeX кладём рядом: шрифты в его CSS указаны относительными путями.
        shutil.copytree(katex, os.path.join(tmp, 'katex'))
        page_path = os.path.join(tmp, 'page.html')
        with open(page_path, 'w') as fh:
            fh.write(html)
        broken, cramped, wide = print_pdf(page_path, out, column_mm)

    fixed = fix_outline(out, headings(nb, with_solutions))

    size = os.path.getsize(out) / 1e6
    print(f"  {entry['id']}: {out}  ({size:.1f} МБ, страница {w:g}×{h:g} мм, "
          f"{font} pt)")
    if fixed:
        print(f"    закладок поправлено: {fixed}")
    for e in broken:
        print(f"    ❌ формула не разобрана: {e}")
    # Не ошибка вёрстки, а сигнал автору ноутбука: такую цепочку равенств
    # лучше разбить на две строки в исходнике, чем читать в половину кегля.
    for s in cramped:
        print(f"    ⚠ формула ужата до {s}")
    for s in wide:
        print(f"    ⚠ не влезает в страницу: {s}")
    return out


def fix_outline(path, titles):
    """Возвращает закладкам пробелы, потерянные Chromium на переносах строк."""
    try:
        import pymupdf
    except ImportError:
        return 0                       # необязательная косметика, не повод падать

    by_key = {re.sub(r'\s+', '', t): t for t in titles}
    doc = pymupdf.open(path)
    toc = doc.get_toc()
    changed = 0
    for row in toc:
        want = by_key.get(re.sub(r'\s+', '', row[1]))
        if want and want != row[1]:
            row[1] = want
            changed += 1
    if changed:
        doc.set_toc(toc)
        doc.saveIncr()
    doc.close()
    return changed


def print_pdf(page_path, out, column_mm):
    from playwright.sync_api import sync_playwright

    # Вьюпорт равен колонке печатной страницы: иначе всё меряется при ширине
    # 1280 px, ни одна формула не выглядит широкой, и подгонка не срабатывает.
    width_px = max(120, round(column_mm / 25.4 * 96))

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': width_px, 'height': 900})
        page.emulate_media(media='print')
        page.goto(f'file://{page_path}')
        page.wait_for_function('window.__ready === true', timeout=120_000)
        broken = page.evaluate('window.__texErrors')
        cramped = page.evaluate('window.__shrunk')
        wide = page.evaluate('window.__wide')[:3]
        page.pdf(
            path=out,
            prefer_css_page_size=True,
            print_background=True,
            display_header_footer=True,
            header_template='<div></div>',
            footer_template=FOOTER,
            outline=True,          # закладки по заголовкам — навигация с телефона
            tagged=True,
        )
        browser.close()
    return broken, cramped, wide


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('ids', nargs='*', help='идентификаторы практикумов, например A4')
    ap.add_argument('--all', action='store_true', help='все со status: ready')
    ap.add_argument('--tasks', action='store_true', help='без раздела решений')
    ap.add_argument('--page', default=DEFAULT_PAGE,
                    help=f'размер страницы в мм, ШxВ (по умолчанию {DEFAULT_PAGE})')
    ap.add_argument('--font', type=float, default=DEFAULT_FONT,
                    help=f'кегль в пунктах (по умолчанию {DEFAULT_FONT})')
    ap.add_argument('--out', default=os.path.join(ROOT, 'practicum/pdf'),
                    help='куда класть PDF')
    a = ap.parse_args()

    cmap = load_map()
    if a.all:
        chosen = [p for p in cmap.values() if p.get('status') == 'ready']
    else:
        if not a.ids:
            ap.error('укажите идентификаторы или --all')
        chosen = []
        for i in a.ids:
            name, _, kind = i.partition(':')
            entry = cmap.get(name.upper())
            if entry is None:
                sys.exit(f'нет такого практикума: {name}')
            if kind and kind != 'archive':
                sys.exit(f'непонятный вид ноутбука: {kind}')
            if kind:
                # архивный ноутбук темы: те же поля, другой файл
                if not entry.get('archive'):
                    sys.exit(f'{name}: архивный ноутбук ещё не собран')
                entry = dict(entry, id=f'{name.upper()}:archive',
                             notebook=entry['archive'],
                             title=entry['title'] + ' — архив задач')
            elif not entry.get('notebook'):
                sys.exit(f'{name}: ноутбук ещё не собран')
            chosen.append(entry)

    if not re.fullmatch(r'\d+(\.\d+)?x\d+(\.\d+)?', a.page.lower()):
        sys.exit(f'--page должен выглядеть как 90x160, а не {a.page}')

    print(f'практикумов к сборке: {len(chosen)}')
    for entry in sorted(chosen, key=lambda p: p['id']):
        render(entry, a.page, a.font, not a.tasks, a.out)
    print('готово')


if __name__ == '__main__':
    main()
