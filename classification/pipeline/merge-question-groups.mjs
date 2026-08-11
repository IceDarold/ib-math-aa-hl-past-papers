#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const config = JSON.parse(await readFile(resolve(here, 'question-groups.json'), 'utf8'))
const generatedRoot = resolve(repositoryRoot, 'classification/generated/2024-may-tz1/deepseek-v4-pro')
const partialRoot = resolve(generatedRoot, 'partials')
const fragmentRoot = resolve(generatedRoot, 'fragments')
const allowedFlags = new Set([
  'shared_marks', 'alternative_route', 'diagram_dependent', 'formula_extraction_uncertain',
  'part_boundary_uncertain', 'topic_uncertain', 'method_uncertain', 'markscheme_ambiguity',
])
const topicAliases = new Map([
  ['algebra.algebraic_transformation', 'number_algebra.polynomials'],
])

function confidence(value) {
  return ['high', 'medium', 'low'].includes(value) ? value : 'medium'
}

await mkdir(fragmentRoot, { recursive: true })
for (const [id, question] of Object.entries(config)) {
  const partials = []
  let missing = false
  for (const group of question.groups) {
    try {
      const partial = JSON.parse(await readFile(resolve(partialRoot, `${id}-${group.id}.json`), 'utf8'))
      const marks = partial.blocks.reduce((sum, block) => sum + block.marks, 0)
      if (marks !== group.marks) throw new Error(`${id}-${group.id}: ${marks} marks, expected ${group.marks}`)
      partials.push(partial)
    } catch (error) {
      if (error.code === 'ENOENT') {
        missing = true
        break
      }
      throw error
    }
  }
  if (missing) continue

  const [paperNumber, questionNumber] = id.match(/^paper-(\d)-q(\d{2})$/).slice(1)
  const idPrefix = `2024-MAY-TZ1-P${paperNumber}-Q${questionNumber}`
  const blocks = partials.flatMap((partial) => partial.blocks).map((block) => {
    const partSuffix = String(block.part ?? '')
      .replace(/[()]/g, '-')
      .replace(/[^a-z0-9]+/gi, '-')
      .replace(/^-|-$/g, '')
      .toUpperCase()
    const evidence = Array.isArray(block.evidence) && block.evidence.length > 0
      ? block.evidence
      : [{
          markscheme_pages: question.markscheme_pages,
          basis: 'The cited markscheme pages establish the scored method path and mark allocation.',
        }]
    return ({
    ...block,
    id: `${idPrefix}${partSuffix && partSuffix !== '-' ? `-${partSuffix}` : ''}`,
    question: question.question,
    source_pages: question.source_pages,
    markscheme_pages: question.markscheme_pages,
    primary_topic: topicAliases.get(block.primary_topic) ?? block.primary_topic,
    secondary_topics: block.secondary_topics ?? [],
    evidence,
    confidence: typeof block.confidence === 'string' ? {
      segmentation: confidence(block.confidence),
      topic: confidence(block.confidence),
      method: confidence(block.confidence),
    } : block.confidence,
    review_flags: (block.review_flags ?? []).filter((flag) => allowedFlags.has(flag)),
  })})
  const marks = blocks.reduce((sum, block) => sum + block.marks, 0)
  if (marks !== question.marks) throw new Error(`${id}: ${marks} marks, expected ${question.marks}`)
  const fragment = { question: question.question, expected_question_marks: question.marks, blocks }
  await writeFile(resolve(fragmentRoot, `${id}.json`), `${JSON.stringify(fragment, null, 2)}\n`)
  console.log(`${id}: ${blocks.length} blocks, ${marks} marks`)
}
