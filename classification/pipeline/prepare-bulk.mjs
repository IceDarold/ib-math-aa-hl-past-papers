#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const sessions = JSON.parse(await readFile(resolve(here, 'sessions.json'), 'utf8'))
const requested = process.argv.slice(2).filter((value) => !value.startsWith('-'))
const selected = requested.length > 0
  ? requested.map((slug) => sessions.find((item) => item.slug === slug) ?? fail(`Unknown session: ${slug}`))
  : sessions.filter((item) => !item.processed)

const schema = JSON.parse(await readFile(resolve(repositoryRoot, 'classification/schema/question-set.schema.json'), 'utf8'))
const topics = schema.$defs.block.properties.primary_topic.enum
const methods = schema.$defs.block.properties.method_family.enum
const flags = schema.$defs.block.properties.review_flags.items.enum

function fail(message) {
  throw new Error(message)
}

function runMutool(args) {
  return execFileSync('mutool', args, {
    encoding: 'utf8',
    maxBuffer: 64 * 1024 * 1024,
    stdio: ['ignore', 'pipe', 'ignore'],
  })
}

function pageCount(pdfPath) {
  const match = runMutool(['info', pdfPath]).match(/^Pages:\s+(\d+)/m)
  if (!match) fail(`Could not read page count: ${pdfPath}`)
  return Number(match[1])
}

function normalizeText(value) {
  return value.replace(/\r/g, '').replace(/[\t ]+\n/g, '\n').replace(/\n{4,}/g, '\n\n\n').trim()
}

function extractPages(pdfPath, label) {
  const count = pageCount(pdfPath)
  const pages = []
  for (let page = 1; page <= count; page += 1) {
    const text = normalizeText(runMutool(['draw', '-q', '-F', 'txt', '-o', '-', pdfPath, String(page)]))
    pages.push({
      page,
      text,
      marked: `===== ${label} · PDF PAGE ${page} OF ${count} =====\n${text || '[NO EXTRACTABLE TEXT]'}`,
    })
  }
  return pages
}

function questionStarts(pages) {
  const starts = []
  const pattern = /(?:^|\n)\s*(\d{1,2})\.\s*(?:\n\s*)?\[Maximum marks?:\s*(\d+)\]/gi
  for (const entry of pages) {
    for (const match of entry.text.matchAll(pattern)) {
      const question = Number(match[1])
      if (!starts.some((item) => item.question === question)) {
        starts.push({ question, marks: Number(match[2]), page: entry.page })
      }
    }
  }
  starts.sort((a, b) => a.question - b.question)
  if (starts.length === 0) fail('No [Maximum mark: N] question headers found')
  for (let index = 0; index < starts.length; index += 1) {
    if (starts[index].question !== index + 1) fail(`Question sequence is not contiguous: ${JSON.stringify(starts)}`)
  }
  return starts
}

function exactQuestionMarker(text, question) {
  const dotted = new RegExp(`(?:^|\\n)\\s*${question}\\.\\s*(?:\\n|$)`).test(text)
  const contextualHeader = new RegExp(`(?:^|\\n)\\s*${question}\\.?\\s*(?:\\n\\s*)?(?:METHOD\\b|\\([a-z]\\))`, 'i').test(text)
  return dotted || contextualHeader
}

function strongQuestionHeader(text, question) {
  return new RegExp(`(?:^|\\n)\\s*${question}\\.?\\s*(?:\\n\\s*)?(?:METHOD\\b|\\([a-z]\\))`, 'i').test(text)
}

function markschemeStarts(pages, questions) {
  const sectionStart = pages.find((entry) => /(?:^|\n)\s*Section A\s*(?:\n|$)/i.test(entry.text) && exactQuestionMarker(entry.text, 1))
    ?? pages.find((entry) => strongQuestionHeader(entry.text, 1))
  if (!sectionStart) fail('Could not locate markscheme Section A / Question 1 start')
  const starts = []
  let minimumPage = sectionStart.page
  for (const { question } of questions) {
    const entry = pages.find((candidate) => candidate.page >= minimumPage && exactQuestionMarker(candidate.text, question))
    if (!entry) fail(`Could not locate markscheme start for Question ${question}`)
    starts.push({ question, page: entry.page })
    minimumPage = entry.page
  }
  return starts
}

function inclusiveRange(pages, start, nextStart) {
  const end = nextStart ?? pages.at(-1).page
  return pages.filter((entry) => entry.page >= start && entry.page <= end).map((entry) => entry.marked).join('\n\n')
}

function sourceFor(session, paper) {
  return resolve(repositoryRoot, session.sources?.[String(paper)] ?? session.source)
}

function systemPrompt(session) {
  return `You classify one IB Mathematics: Analysis and Approaches HL question for a research dataset.

RULES
1. Treat the markscheme as authoritative for segmentation, marks, scored method steps, and accepted alternatives.
2. Return one block per separately marked part. If adjacent parts share one printed mark allocation, combine them and add shared_marks. Never invent a mark split.
3. The block marks must sum exactly to expected_question_marks.
4. method_path is a concise ordered list of marked mathematical operations. method_tags are reusable snake_case operations.
5. accepted_alternatives contains only complete alternative routes explicitly accepted by the markscheme.
6. Cite MARKSCHEME PDF PAGE markers in evidence. Do not fabricate quotations.
7. source_pages uses printed question-paper page numbers when visible; markscheme_pages uses the supplied MARKSCHEME PDF PAGE numbers.
8. Flag uncertain formulas, radicals, matrices, diagrams, tables, graphs, or part boundaries and lower confidence instead of guessing.
9. IDs start with ${session.id_prefix}-P{paper}-Q{two-digit question}. Use uppercase part suffixes, for example ${session.id_prefix}-P1-Q03-A or ${session.id_prefix}-P2-Q07-B-I. Omit the suffix only for an unparted question.
10. Use exactly one allowed primary_topic and one allowed method_family. Prefer the dominant scored solution method, not the surface wording.
11. task_summary, method_path, alternatives, and evidence must be concise English. Preserve mathematical signs, radicals, powers, and conditions exactly.
12. The supplied page range can include the start of an adjacent question. Classify only the explicitly requested question.

ALLOWED primary_topic VALUES
${topics.join(', ')}

ALLOWED method_family VALUES
${methods.join(', ')}

ALLOWED review_flags VALUES
${flags.join(', ')}

Confidence values: high, medium, low. Return only schema-valid JSON.`
}

for (const session of selected) {
  const workRoot = resolve(repositoryRoot, 'classification/work', session.slug)
  const promptRoot = resolve(workRoot, 'questions')
  await mkdir(promptRoot, { recursive: true })
  await writeFile(resolve(workRoot, 'system-prompt.txt'), `${systemPrompt(session)}\n`)
  const metadata = { ...session, provider: 'deepseek', model: 'deepseek-v4-pro[1m]', papers: [] }

  for (const paper of [1, 2, 3]) {
    const sourceRoot = sourceFor(session, paper)
    const questionPath = join(sourceRoot, `Paper ${paper}`, 'question-paper.pdf')
    const markschemePath = join(sourceRoot, `Paper ${paper}`, 'markscheme.pdf')
    const qp = extractPages(questionPath, 'QUESTION PAPER')
    const ms = extractPages(markschemePath, 'MARKSCHEME')
    const questions = questionStarts(qp)
    const markStarts = markschemeStarts(ms, questions)
    const expectedTotal = paper === 3 ? 55 : 110
    const total = questions.reduce((sum, item) => sum + item.marks, 0)
    if (total !== expectedTotal) fail(`${session.slug} Paper ${paper}: maximum marks total ${total}, expected ${expectedTotal}`)

    const paperMetadata = {
      paper,
      calculator: paper === 1 ? 'no' : 'yes',
      expected_total_marks: expectedTotal,
      question_file: questionPath.slice(repositoryRoot.length + 1),
      markscheme_file: markschemePath.slice(repositoryRoot.length + 1),
      questions: [],
    }

    for (let index = 0; index < questions.length; index += 1) {
      const item = questions[index]
      const next = questions[index + 1]
      const markStart = markStarts[index]
      const nextMark = markStarts[index + 1]
      const qpText = inclusiveRange(qp, item.page, next?.page)
      const msText = inclusiveRange(ms, markStart.page, nextMark?.page)
      const prompt = `Classify only ${session.session} ${session.zone} Paper ${paper}, Question ${item.question}.

expected_question_marks=${item.marks}. Block marks must sum exactly to ${item.marks}.
Do not include any adjacent question that happens to appear in the page extraction.

${qpText}

${msText}
`
      const filename = `paper-${paper}-q${String(item.question).padStart(2, '0')}.txt`
      await writeFile(resolve(promptRoot, filename), prompt.replaceAll('\f', ''))
      paperMetadata.questions.push({
        question: String(item.question), marks: item.marks, prompt: filename,
        question_pdf_pages: [item.page, next?.page ?? qp.at(-1).page],
        markscheme_pdf_pages: [markStart.page, nextMark?.page ?? ms.at(-1).page],
        prompt_characters: prompt.length,
      })
    }
    metadata.papers.push(paperMetadata)
    console.log(`${session.slug} paper-${paper}: ${questions.length} questions, ${total} marks`)
  }
  await writeFile(resolve(workRoot, 'metadata.json'), `${JSON.stringify(metadata, null, 2)}\n`)
}
