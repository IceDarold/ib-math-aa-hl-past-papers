#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const workRoot = resolve(repositoryRoot, 'classification/work/2024-may-tz1')
const promptRoot = resolve(workRoot, 'questions')

// PDF-page ranges were verified against the rendered papers. Preliminary
// markscheme pages are deliberately excluded.
const ranges = {
  1: {
    1: [[3, 3], [7, 7]], 2: [[4, 4], [8, 8]], 3: [[5, 5], [9, 9]],
    4: [[6, 6], [10, 11]], 5: [[7, 7], [12, 14]], 6: [[8, 8], [15, 16]],
    7: [[9, 9], [17, 17]], 8: [[10, 10], [18, 19]], 9: [[11, 12], [20, 21]],
    10: [[13, 13], [22, 26]], 11: [[14, 14], [27, 29]], 12: [[15, 17], [30, 33]],
  },
  2: {
    1: [[3, 3], [8, 9]], 2: [[4, 4], [10, 10]], 3: [[5, 5], [11, 11]],
    4: [[6, 6], [12, 12]], 5: [[7, 8], [13, 13]], 6: [[9, 9], [14, 14]],
    7: [[10, 10], [15, 15]], 8: [[11, 11], [16, 17]], 9: [[12, 12], [18, 19]],
    10: [[13, 14], [20, 22]], 11: [[15, 15], [23, 24]], 12: [[16, 17], [25, 29]],
  },
  3: {
    1: [[3, 4], [7, 11]], 2: [[5, 6], [12, 16]],
  },
}

function pagesBySection(raw) {
  const pages = { 'QUESTION PAPER': new Map(), MARKSCHEME: new Map() }
  let section = null
  let page = null
  let lines = []

  function flush() {
    if (section && page !== null) pages[section].set(page, lines.join('\n').trim())
  }

  for (const line of raw.split(/\r?\n/)) {
    const marker = line.match(/^===== (QUESTION PAPER|MARKSCHEME) · PDF PAGE (\d+) OF \d+ =====$/)
    if (marker) {
      flush()
      section = marker[1]
      page = Number(marker[2])
      lines = [line]
    } else if (section) {
      lines.push(line)
    }
  }
  flush()
  return pages
}

function selectPages(map, [start, end]) {
  const selected = []
  for (let page = start; page <= end; page += 1) {
    if (!map.has(page)) throw new Error(`Missing extracted PDF page ${page}`)
    selected.push(map.get(page))
  }
  return selected.join('\n\n')
}

function expectedMarks(questionText) {
  const match = questionText.match(/\[Maximum mark:\s*(\d+)\]/i)
  if (!match) throw new Error('Could not find [Maximum mark: N] in question pages')
  return Number(match[1])
}

await mkdir(promptRoot, { recursive: true })
const baseSystemPrompt = await readFile(resolve(workRoot, 'system-prompt.txt'), 'utf8')
const questionSystemPrompt = baseSystemPrompt
  .replace('The sum of block marks must equal expected_total_marks exactly.', 'The sum of block marks must equal expected_question_marks exactly.')
  .replace('Return only JSON matching the supplied schema.', 'Return only one question fragment matching the supplied schema.')
await writeFile(resolve(workRoot, 'question-system-prompt.txt'), questionSystemPrompt)

const strictSchema = JSON.parse(await readFile(resolve(repositoryRoot, 'classification/schema/question-set.schema.json'), 'utf8'))
const allowedTopics = strictSchema.$defs.block.properties.primary_topic.enum
const allowedMethods = strictSchema.$defs.block.properties.method_family.enum
const allowedFlags = strictSchema.$defs.block.properties.review_flags.items.enum
const compactSystemPrompt = `Classify one IB Mathematics AA HL question using its question-paper and markscheme extraction.

RULES
1. The markscheme is authoritative for parts, mark grouping, method steps, and alternatives.
2. Return one block per separately marked part. Never invent a split for shared marks; combine those parts and flag shared_marks.
3. Block marks must sum exactly to expected_question_marks.
4. method_path is a concise ordered list of marked operations. method_tags are reusable snake_case operations.
5. accepted_alternatives contains only complete alternative methods explicitly supported by the markscheme.
6. Cite MARKSCHEME PDF PAGE numbers in evidence. Do not fabricate quotes.
7. Use printed question-paper pages in source_pages and MARKSCHEME PDF PAGE numbers in markscheme_pages.
8. Flag uncertain formula, diagram, table, graph, or boundary extraction. Lower confidence instead of guessing.
9. IDs use 2024-MAY-TZ1-P{paper}-Q{two-digit question}-{uppercase part}, for example Q03-A or Q07-B-I. Use no suffix only for an unparted question.
10. task_summary, method_path, alternatives, and evidence must be concise English.

ALLOWED primary_topic VALUES
${allowedTopics.join(', ')}

ALLOWED method_family VALUES
${allowedMethods.join(', ')}

ALLOWED review_flags VALUES
${allowedFlags.join(', ')}

Confidence values: high, medium, low. Return only JSON matching the supplied schema.`
await writeFile(resolve(workRoot, 'question-system-compact.txt'), compactSystemPrompt)

for (const [paperText, questions] of Object.entries(ranges)) {
  const paper = Number(paperText)
  const raw = await readFile(resolve(workRoot, `paper-${paper}.txt`), 'utf8')
  const pages = pagesBySection(raw)
  for (const [questionText, [questionRange, markschemeRange]] of Object.entries(questions)) {
    const question = Number(questionText)
    const qp = selectPages(pages['QUESTION PAPER'], questionRange)
    const ms = selectPages(pages.MARKSCHEME, markschemeRange)
    const marks = expectedMarks(qp)
    const prompt = `Classify only May 2024 TZ1 Paper ${paper}, Question ${question}.\n\n` +
      `The required expected_question_marks value is ${marks}. The block marks must sum to ${marks}. ` +
      `Do not include any other question, even if page extraction contains a continuation marker.\n\n` +
      `${qp}\n\n${ms}\n`
    const filename = `paper-${paper}-q${String(question).padStart(2, '0')}.txt`
    await writeFile(resolve(promptRoot, filename), prompt)
    console.log(`${filename}: ${prompt.length.toLocaleString()} characters, ${marks} marks`)
  }
}
