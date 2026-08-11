#!/usr/bin/env node

import { readFile } from 'node:fs/promises'
import { basename, dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const generatedRoot = resolve(repositoryRoot, 'classification/generated/2024-may-tz1/deepseek-v4-pro')
const schema = JSON.parse(await readFile(resolve(repositoryRoot, 'classification/schema/question-set.schema.json'), 'utf8'))
const review = JSON.parse(await readFile(resolve(repositoryRoot, 'classification/reviews/2024-may-tz1/calibration-v1.json'), 'utf8'))
const allowedTopics = new Set(schema.$defs.block.properties.primary_topic.enum)
const allowedMethods = new Set(schema.$defs.block.properties.method_family.enum)
const allowedConfidence = new Set(schema.$defs.confidence.enum)
const allowedFlags = new Set(schema.$defs.block.properties.review_flags.items.enum)
let failed = false
const generatedIds = new Set()

function assert(condition, message, errors) {
  if (!condition) errors.push(message)
}

for (const paper of [1, 2, 3]) {
  const path = resolve(generatedRoot, `paper-${paper}.json`)
  const document = JSON.parse(await readFile(path, 'utf8'))
  const errors = []
  const seen = new Set()
  const expectedMarks = paper === 3 ? 55 : 110

  assert(document.session === 'May 2024', 'session must be May 2024', errors)
  assert(document.zone === 'TZ1', 'zone must be TZ1', errors)
  assert(document.paper === paper, `paper must be ${paper}`, errors)
  assert(document.calculator === (paper === 1 ? 'no' : 'yes'), 'calculator value is inconsistent with paper', errors)
  assert(document.expected_total_marks === expectedMarks, `expected_total_marks must be ${expectedMarks}`, errors)
  assert(Array.isArray(document.blocks) && document.blocks.length > 0, 'blocks must be a non-empty array', errors)

  for (const [index, block] of (document.blocks ?? []).entries()) {
    const prefix = `block ${index + 1} (${block.id ?? 'missing id'})`
    assert(typeof block.id === 'string' && /^2024-MAY-TZ1-P[123]-Q\d{2}(?:-[A-Z0-9-]+)?$/.test(block.id), `${prefix}: invalid id`, errors)
    assert(!seen.has(block.id), `${prefix}: duplicate id`, errors)
    seen.add(block.id)
    generatedIds.add(block.id)
    assert(Number.isInteger(block.marks) && block.marks > 0, `${prefix}: marks must be a positive integer`, errors)
    assert(allowedTopics.has(block.primary_topic), `${prefix}: unknown primary_topic ${block.primary_topic}`, errors)
    assert(allowedMethods.has(block.method_family), `${prefix}: unknown method_family ${block.method_family}`, errors)
    assert(Array.isArray(block.method_tags) && block.method_tags.length > 0, `${prefix}: method_tags must not be empty`, errors)
    assert(Array.isArray(block.method_path) && block.method_path.length > 0, `${prefix}: method_path must not be empty`, errors)
    assert(Array.isArray(block.evidence) && block.evidence.length > 0, `${prefix}: evidence must not be empty`, errors)
    assert(['segmentation', 'topic', 'method'].every((key) => allowedConfidence.has(block.confidence?.[key])), `${prefix}: invalid confidence`, errors)
    assert(Array.isArray(block.review_flags) && block.review_flags.every((flag) => allowedFlags.has(flag)), `${prefix}: invalid review_flags`, errors)
  }

  const marks = (document.blocks ?? []).reduce((sum, block) => sum + block.marks, 0)
  assert(marks === expectedMarks, `mark total ${marks} does not equal ${expectedMarks}`, errors)

  if (errors.length > 0) {
    failed = true
    console.error(`${basename(path)}: FAILED`)
    for (const error of errors) console.error(`  - ${error}`)
  } else {
    const flagged = document.blocks.filter((block) => block.review_flags.length > 0).length
    const lowConfidence = document.blocks.filter((block) => Object.values(block.confidence).includes('low')).length
    console.log(`${basename(path)}: ${document.blocks.length} blocks, ${marks} marks, ${flagged} flagged, ${lowConfidence} low-confidence`)
  }
}

const reviewErrors = []
const reviewedIds = review.reviews.map((item) => item.id)
const uniqueReviewedIds = new Set(reviewedIds)
assert(uniqueReviewedIds.size === reviewedIds.length, 'review ledger contains duplicate ids', reviewErrors)
assert(reviewedIds.length === review.sample.flagged_count + review.sample.unflagged_count, 'review count does not match sample metadata', reviewErrors)
for (const item of review.reviews) {
  assert(generatedIds.has(item.id), `reviewed block does not exist: ${item.id}`, reviewErrors)
  assert(['accepted', 'corrected'].includes(item.verdict), `invalid review verdict for ${item.id}`, reviewErrors)
  assert(item.verdict === 'corrected' || !review.corrections[item.id], `accepted block has a correction: ${item.id}`, reviewErrors)
  assert(item.verdict !== 'corrected' || Boolean(review.corrections[item.id]), `corrected block has no correction: ${item.id}`, reviewErrors)
}
for (const id of Object.keys(review.corrections)) {
  assert(uniqueReviewedIds.has(id), `correction has no review entry: ${id}`, reviewErrors)
}
if (reviewErrors.length > 0) {
  failed = true
  console.error('calibration-v1.json: FAILED')
  for (const error of reviewErrors) console.error(`  - ${error}`)
} else {
  const corrected = review.reviews.filter((item) => item.verdict === 'corrected').length
  console.log(`calibration-v1.json: ${reviewedIds.length} reviewed, ${corrected} corrected`)
}

if (failed) process.exitCode = 1
