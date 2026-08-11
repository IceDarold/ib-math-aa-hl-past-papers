#!/usr/bin/env node

import { readFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const slug = process.argv[2]
if (!slug) throw new Error('Usage: validate-session.mjs <session-slug>')
const sessions = JSON.parse(await readFile(resolve(here, 'sessions.json'), 'utf8'))
const session = sessions.find((item) => item.slug === slug)
if (!session) throw new Error(`Unknown session: ${slug}`)
const generatedRoot = resolve(repositoryRoot, 'classification/generated', slug, 'deepseek-v4-pro')
const schema = JSON.parse(await readFile(resolve(repositoryRoot, 'classification/schema/question-set.schema.json'), 'utf8'))
const allowedTopics = new Set(schema.$defs.block.properties.primary_topic.enum)
const allowedMethods = new Set(schema.$defs.block.properties.method_family.enum)
const allowedConfidence = new Set(schema.$defs.confidence.enum)
const allowedFlags = new Set(schema.$defs.block.properties.review_flags.items.enum)
let failed = false

function check(condition, message, errors) {
  if (!condition) errors.push(message)
}

for (const paper of [1, 2, 3]) {
  const document = JSON.parse(await readFile(resolve(generatedRoot, `paper-${paper}.json`), 'utf8'))
  const errors = []
  const seen = new Set()
  const expectedMarks = paper === 3 ? 55 : 110
  check(document.session === session.session, `session must be ${session.session}`, errors)
  check(document.zone === session.zone, `zone must be ${session.zone}`, errors)
  check(document.paper === paper, `paper must be ${paper}`, errors)
  check(document.calculator === (paper === 1 ? 'no' : 'yes'), 'calculator mismatch', errors)
  check(document.expected_total_marks === expectedMarks, `expected_total_marks must be ${expectedMarks}`, errors)
  for (const block of document.blocks) {
    const prefix = block.id ?? 'missing-id'
    check(typeof block.id === 'string' && block.id.startsWith(`${session.id_prefix}-P${paper}-Q`), `${prefix}: invalid ID prefix`, errors)
    check(!seen.has(block.id), `${prefix}: duplicate ID`, errors)
    seen.add(block.id)
    check(String(block.question).match(/^\d+$/), `${prefix}: invalid question`, errors)
    check(Number.isInteger(block.marks) && block.marks > 0, `${prefix}: invalid marks`, errors)
    check(allowedTopics.has(block.primary_topic), `${prefix}: unknown topic ${block.primary_topic}`, errors)
    check(allowedMethods.has(block.method_family), `${prefix}: unknown method ${block.method_family}`, errors)
    check(Array.isArray(block.method_tags) && block.method_tags.length > 0, `${prefix}: empty method_tags`, errors)
    check(Array.isArray(block.method_path) && block.method_path.length > 0, `${prefix}: empty method_path`, errors)
    check(Array.isArray(block.evidence) && block.evidence.length > 0, `${prefix}: empty evidence`, errors)
    check(['segmentation', 'topic', 'method'].every((key) => allowedConfidence.has(block.confidence?.[key])), `${prefix}: invalid confidence`, errors)
    check(Array.isArray(block.review_flags) && block.review_flags.every((flag) => allowedFlags.has(flag)), `${prefix}: invalid flags`, errors)
  }
  const marks = document.blocks.reduce((sum, block) => sum + block.marks, 0)
  check(marks === expectedMarks, `mark total ${marks}, expected ${expectedMarks}`, errors)
  if (errors.length > 0) {
    failed = true
    console.error(`${slug} paper-${paper}: FAILED`)
    for (const error of errors) console.error(`  - ${error}`)
  } else {
    const flagged = document.blocks.filter((block) => block.review_flags.length > 0).length
    console.log(`${slug} paper-${paper}: ${document.blocks.length} blocks, ${marks} marks, ${flagged} flagged`)
  }
}

if (failed) process.exitCode = 1
