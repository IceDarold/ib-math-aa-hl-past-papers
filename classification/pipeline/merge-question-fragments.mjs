#!/usr/bin/env node

import { mkdir, readFile, readdir, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const generatedRoot = resolve(repositoryRoot, 'classification/generated/2024-may-tz1/deepseek-v4-pro')
const fragmentsRoot = resolve(generatedRoot, 'fragments')
const reviewPath = resolve(repositoryRoot, 'classification/reviews/2024-may-tz1/calibration-v1.json')

const review = JSON.parse(await readFile(reviewPath, 'utf8'))
const corrections = new Map(Object.entries(review.corrections ?? {}))

const sourcePages = {
  1: { 1: '2', 2: '3', 3: '4', 4: '5', 5: '6', 6: '7', 7: '8', 8: '9', 9: '10-11', 10: '12', 11: '13', 12: '14-16' },
  2: { 1: '2', 2: '3', 3: '4', 4: '5', 5: '6-7', 6: '8', 7: '9', 8: '10', 9: '11', 10: '12-13', 11: '14', 12: '15-16' },
  3: { 1: '2-3', 2: '4-5' },
}

function normalizeBlock(block, paper, question) {
  const partSuffix = String(block.part ?? '')
    .replace(/[()]/g, '-')
    .replace(/[^a-z0-9]+/gi, '-')
    .replace(/^-|-$/g, '')
    .toUpperCase()
  const markschemePages = String(block.markscheme_pages ?? block.evidence?.[0]?.markscheme_pages ?? '')
  const evidence = Array.isArray(block.evidence) && block.evidence.length > 0
    ? block.evidence
    : [{
        markscheme_pages: markschemePages,
        basis: 'The cited markscheme pages establish the scored method path and mark allocation.',
      }]
  const normalized = {
    ...block,
    id: `2024-MAY-TZ1-P${paper}-Q${String(question).padStart(2, '0')}${partSuffix && partSuffix !== '-' ? `-${partSuffix}` : ''}`,
    question: String(question),
    source_pages: sourcePages[paper][question],
    markscheme_pages: markschemePages,
    evidence,
  }
  return { ...normalized, ...(corrections.get(normalized.id) ?? {}) }
}

const files = (await readdir(fragmentsRoot)).filter((file) => /^paper-[123]-q\d{2}\.json$/.test(file)).sort()
for (const paper of [1, 2, 3]) {
  const paperFiles = files.filter((file) => file.startsWith(`paper-${paper}-`))
  if (paperFiles.length === 0) continue
  const fragments = await Promise.all(paperFiles.map(async (file) => ({
    question: Number(file.match(/-q(\d{2})\.json$/)[1]),
    value: JSON.parse(await readFile(resolve(fragmentsRoot, file), 'utf8')),
  })))
  const document = {
    session: 'May 2024',
    zone: 'TZ1',
    paper,
    calculator: paper === 1 ? 'no' : 'yes',
    expected_total_marks: paper === 3 ? 55 : 110,
    blocks: fragments.flatMap((fragment) => fragment.value.blocks.map((block) => normalizeBlock(block, paper, fragment.question))),
  }
  await mkdir(generatedRoot, { recursive: true })
  await writeFile(resolve(generatedRoot, `paper-${paper}.json`), `${JSON.stringify(document, null, 2)}\n`)
  console.log(`paper-${paper}.json: ${paperFiles.length} questions, ${document.blocks.length} blocks, ${document.blocks.reduce((sum, block) => sum + block.marks, 0)} marks`)
}
