#!/usr/bin/env node

import { execFileSync } from 'node:child_process'
import { mkdir, writeFile } from 'node:fs/promises'
import { basename, dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const sourceRoot = resolve(repositoryRoot, 'AA_HL/2024/May/TZ1')
const outputRoot = resolve(repositoryRoot, 'classification/work/2024-may-tz1')

function runMutool(args) {
  return execFileSync('mutool', args, {
    encoding: 'utf8',
    maxBuffer: 32 * 1024 * 1024,
  })
}

function pageCount(pdfPath) {
  const match = runMutool(['info', pdfPath]).match(/^Pages:\s+(\d+)/m)
  if (!match) throw new Error(`Could not read page count: ${pdfPath}`)
  return Number(match[1])
}

function normalizeText(value) {
  return value
    .replace(/\r/g, '')
    .replace(/[\t ]+\n/g, '\n')
    .replace(/\n{4,}/g, '\n\n\n')
    .trim()
}

function extractPages(pdfPath, label) {
  const pages = []
  const count = pageCount(pdfPath)
  for (let page = 1; page <= count; page += 1) {
    const text = normalizeText(runMutool(['draw', '-F', 'txt', '-o', '-', pdfPath, String(page)]))
    pages.push(`===== ${label} · PDF PAGE ${page} OF ${count} =====\n${text || '[NO EXTRACTABLE TEXT]'}`)
  }
  return { count, text: pages.join('\n\n') }
}

await mkdir(outputRoot, { recursive: true })

for (const paper of [1, 2, 3]) {
  const directory = join(sourceRoot, `Paper ${paper}`)
  const questionPaper = join(directory, 'question-paper.pdf')
  const markscheme = join(directory, 'markscheme.pdf')
  const question = extractPages(questionPaper, 'QUESTION PAPER')
  const marks = extractPages(markscheme, 'MARKSCHEME')
  const output = [
    '# Source metadata',
    `session: May 2024`,
    `zone: TZ1`,
    `paper: ${paper}`,
    `calculator: ${paper === 1 ? 'no' : 'yes'}`,
    `expected_total_marks: ${paper === 3 ? 55 : 110}`,
    `question_file: ${questionPaper.slice(repositoryRoot.length + 1)}`,
    `markscheme_file: ${markscheme.slice(repositoryRoot.length + 1)}`,
    `question_pdf_pages: ${question.count}`,
    `markscheme_pdf_pages: ${marks.count}`,
    '',
    question.text,
    '',
    marks.text,
    '',
  ].join('\n')
  const outputPath = join(outputRoot, `paper-${paper}.txt`)
  await writeFile(outputPath, output)
  console.log(`${basename(outputPath)}: ${output.length.toLocaleString()} characters`)
}
