#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const slug = process.argv[2]
if (!slug) throw new Error('Usage: merge-bulk.mjs <session-slug>')
const workRoot = resolve(repositoryRoot, 'classification/work', slug)
const generatedRoot = resolve(repositoryRoot, 'classification/generated', slug, 'deepseek-v4-pro')
const metadata = JSON.parse(await readFile(resolve(workRoot, 'metadata.json'), 'utf8'))
const summary = []

for (const paper of metadata.papers) {
  const blocks = []
  for (const question of paper.questions) {
    const fragmentPath = resolve(generatedRoot, 'fragments', question.prompt.replace(/\.txt$/, '.json'))
    const fragment = JSON.parse(await readFile(fragmentPath, 'utf8'))
    const marks = fragment.blocks.reduce((sum, block) => sum + block.marks, 0)
    if (marks !== question.marks) throw new Error(`${slug} P${paper.paper} Q${question.question}: ${marks} marks, expected ${question.marks}`)
    blocks.push(...fragment.blocks)
  }
  const document = {
    session: metadata.session,
    zone: metadata.zone,
    paper: paper.paper,
    calculator: paper.calculator,
    expected_total_marks: paper.expected_total_marks,
    blocks,
  }
  const total = blocks.reduce((sum, block) => sum + block.marks, 0)
  if (total !== paper.expected_total_marks) throw new Error(`${slug} P${paper.paper}: ${total} marks, expected ${paper.expected_total_marks}`)
  await writeFile(resolve(generatedRoot, `paper-${paper.paper}.json`), `${JSON.stringify(document, null, 2)}\n`)
  const flagged = blocks.filter((block) => block.review_flags.length > 0).length
  summary.push({ paper: paper.paper, blocks: blocks.length, marks: total, flagged })
  console.log(`${slug} paper-${paper.paper}: ${blocks.length} blocks, ${total} marks, ${flagged} flagged`)
}

const manifest = {
  session: metadata.session,
  zone: metadata.zone,
  subject: 'IB Mathematics: Analysis and Approaches HL',
  provider: 'deepseek',
  model: 'deepseek-v4-pro[1m]',
  review_status: 'ai_draft',
  papers: summary,
  total_blocks: summary.reduce((sum, paper) => sum + paper.blocks, 0),
  total_marks: summary.reduce((sum, paper) => sum + paper.marks, 0),
  flagged_blocks: summary.reduce((sum, paper) => sum + paper.flagged, 0),
}
await writeFile(resolve(generatedRoot, 'manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`)
