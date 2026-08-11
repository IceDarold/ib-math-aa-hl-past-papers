#!/usr/bin/env node

import { spawn } from 'node:child_process'
import { access, mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const slug = process.argv[2]
if (!slug) throw new Error('Usage: run-deepseek-bulk.mjs <session-slug> [concurrency]')
const concurrency = Math.max(1, Math.min(6, Number(process.argv[3] ?? 3)))
const workRoot = resolve(repositoryRoot, 'classification/work', slug)
const generatedRoot = resolve(repositoryRoot, 'classification/generated', slug, 'deepseek-v4-pro')
const fragmentRoot = resolve(generatedRoot, 'fragments')
const rawRoot = resolve(generatedRoot, 'raw')
const [metadata, systemPrompt, outputSchema] = await Promise.all([
  readFile(resolve(workRoot, 'metadata.json'), 'utf8').then(JSON.parse),
  readFile(resolve(workRoot, 'system-prompt.txt'), 'utf8'),
  readFile(resolve(repositoryRoot, 'classification/schema/question-fragment.transport.schema.json'), 'utf8').then(JSON.parse),
])

await Promise.all([mkdir(fragmentRoot, { recursive: true }), mkdir(rawRoot, { recursive: true })])
const allJobs = metadata.papers.flatMap((paper) => paper.questions.map((question) => ({
  paper: paper.paper,
  ...question,
  promptPath: resolve(workRoot, 'questions', question.prompt),
  outputPath: resolve(fragmentRoot, question.prompt.replace(/\.txt$/, '.json')),
  rawPath: resolve(rawRoot, question.prompt.replace(/\.txt$/, '.json')),
})))
const jobs = []
for (const job of allJobs) {
  try {
    await access(job.outputPath)
    console.log(`SKIP ${slug} P${job.paper} Q${job.question}: fragment exists`)
  } catch {
    jobs.push(job)
  }
}

let cursor = 0
let failures = 0
let totalCost = 0

function partSuffix(part) {
  return String(part ?? '')
    .replace(/[()]/g, '-')
    .replace(/[^a-z0-9]+/gi, '-')
    .replace(/^-|-$/g, '')
    .toUpperCase()
}

function normalizeFragment(fragment, job) {
  const blocks = fragment.blocks.map((block) => {
    const suffix = partSuffix(block.part)
    return {
      ...block,
      id: `${metadata.id_prefix}-P${job.paper}-Q${String(job.question).padStart(2, '0')}${suffix ? `-${suffix}` : ''}`,
      question: String(job.question),
    }
  })
  return { question: String(job.question), expected_question_marks: job.marks, blocks }
}

async function run(job) {
  const prompt = await readFile(job.promptPath, 'utf8')
  const args = [
    '--bare', '-p', '--tools', '', '--no-session-persistence',
    '--model', 'deepseek-v4-pro[1m]', '--effort', 'medium',
    '--output-format', 'json', '--json-schema', JSON.stringify(outputSchema),
    '--system-prompt', systemPrompt,
  ]
  const result = await new Promise((resolvePromise, reject) => {
    const child = spawn('claude', args, { cwd: repositoryRoot, stdio: ['pipe', 'pipe', 'pipe'] })
    let stdout = ''
    let stderr = ''
    child.stdout.on('data', (chunk) => { stdout += chunk })
    child.stderr.on('data', (chunk) => { stderr += chunk })
    child.on('error', reject)
    child.on('close', (code) => code === 0 ? resolvePromise({ stdout, stderr }) : reject(new Error(`claude exited ${code}: ${stderr}`)))
    child.stdin.end(prompt)
  })
  const outer = JSON.parse(result.stdout.trim().split(/\r?\n/).at(-1))
  if (outer.is_error || !outer.structured_output) throw new Error(outer.result || 'DeepSeek returned no structured_output')
  await writeFile(job.rawPath, `${JSON.stringify(outer.structured_output, null, 2)}\n`)
  const fragment = normalizeFragment(outer.structured_output, job)
  const markTotal = fragment.blocks.reduce((sum, block) => sum + block.marks, 0)
  if (markTotal !== job.marks) {
    throw new Error(`mark total ${markTotal}, expected ${job.marks}`)
  }
  await writeFile(job.outputPath, `${JSON.stringify(fragment, null, 2)}\n`)
  totalCost += outer.total_cost_usd ?? 0
  console.log(`OK ${slug} P${job.paper} Q${job.question}: ${fragment.blocks.length} blocks, ${markTotal} marks, $${(outer.total_cost_usd ?? 0).toFixed(3)}`)
}

async function worker() {
  while (cursor < jobs.length) {
    const job = jobs[cursor]
    cursor += 1
    try {
      await run(job)
    } catch (error) {
      failures += 1
      console.error(`FAIL ${slug} P${job.paper} Q${job.question}: ${error.message}`)
    }
  }
}

await Promise.all(Array.from({ length: concurrency }, () => worker()))
console.log(`${slug}: ${jobs.length - failures}/${jobs.length} pending questions completed; estimated cost $${totalCost.toFixed(2)}`)
if (failures > 0) process.exitCode = 1
