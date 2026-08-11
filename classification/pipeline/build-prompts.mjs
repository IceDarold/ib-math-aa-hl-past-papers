#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const repositoryRoot = resolve(here, '../..')
const workRoot = resolve(repositoryRoot, 'classification/work/2024-may-tz1')
const pilotPath = resolve(repositoryRoot, 'classification/pilots/2024-november/questions.tsv')
const topicsPath = resolve(repositoryRoot, 'classification/taxonomy/topics.yaml')
const methodsPath = resolve(repositoryRoot, 'classification/taxonomy/method-families.yaml')

const sampleIds = new Set([
  '2024-NOV-COMMON-P1-Q02-B',
  '2024-NOV-COMMON-P1-Q03',
  '2024-NOV-COMMON-P1-Q06-A',
  '2024-NOV-COMMON-P1-Q07-B',
  '2024-NOV-COMMON-P1-Q08-B',
  '2024-NOV-COMMON-P1-Q10-B-D',
  '2024-NOV-COMMON-P1-Q11-C',
  '2024-NOV-COMMON-P2-Q01-A',
  '2024-NOV-COMMON-P2-Q06-A',
  '2024-NOV-COMMON-P2-Q10-C',
  '2024-NOV-COMMON-P2-Q11-B',
  '2024-NOV-COMMON-P3-Q01-F',
  '2024-NOV-COMMON-P3-Q02-E-I'
])

function parseTsv(raw) {
  const [headerLine, ...lines] = raw.trim().split(/\r?\n/)
  const headers = headerLine.split('\t')
  return lines.map((line) => Object.fromEntries(
    line.split('\t').map((value, index) => [headers[index], value]),
  ))
}

const [pilotRaw, topics, methods] = await Promise.all([
  readFile(pilotPath, 'utf8'),
  readFile(topicsPath, 'utf8'),
  readFile(methodsPath, 'utf8'),
])
const examples = parseTsv(pilotRaw).filter((row) => sampleIds.has(row.id))

const systemPrompt = `You classify IB Mathematics: Analysis and Approaches HL examination material for a research dataset.

NON-NEGOTIABLE RULES
1. Treat the markscheme as the authority for segmentation, marks, method steps, and accepted alternatives.
2. One block normally corresponds to one separately marked part. If marks are shared across adjacent parts, keep them as one combined block and add the shared_marks flag. Never invent a mark split.
3. The sum of block marks must equal expected_total_marks exactly.
4. method_path is an ordered sequence of concise operations evidenced by the markscheme, not a prose solution and not an unordered tag list.
5. accepted_alternatives contains only genuinely accepted complete alternative routes shown or explicitly allowed by the markscheme. Do not treat a minor algebraic rearrangement as an alternative route.
6. Use exactly one allowed primary_topic and exactly one allowed method_family. Secondary topics may use precise domain.subtopic identifiers following the gold examples.
7. Use snake_case atomic method_tags. Reuse gold vocabulary when applicable; create a new tag only when it names a genuinely reusable mathematical operation.
8. Evidence must cite MARKSCHEME PDF PAGE markers from the supplied extraction and state what that page proves. Do not fabricate quotations.
9. Use printed question-paper page numbers in source_pages when visible. Use MARKSCHEME PDF PAGE numbers in markscheme_pages.
10. Flag anything that cannot be trusted from extracted text, especially diagrams, matrices, radicals, tables, graphs, or shared mark boundaries.
11. IDs follow 2024-MAY-TZ1-P{paper}-Q{two-digit question}-{uppercase part}; omit the part suffix only for an unparted question. Examples: 2024-MAY-TZ1-P1-Q03, 2024-MAY-TZ1-P2-Q07-B-I, 2024-MAY-TZ1-P3-Q01-C-I-II.
12. Return only JSON matching the supplied schema.

PRIMARY-TOPIC TAXONOMY
${topics}

METHOD-FAMILY TAXONOMY
${methods}

GOLD EXAMPLES FROM THE MANUALLY REVIEWED NOVEMBER 2024 SESSION
${examples.map((row) => JSON.stringify(row)).join('\n')}
`

await mkdir(workRoot, { recursive: true })
await writeFile(resolve(workRoot, 'system-prompt.txt'), systemPrompt)

for (const paper of [1, 2, 3]) {
  const source = await readFile(resolve(workRoot, `paper-${paper}.txt`), 'utf8')
  const prompt = `Classify the complete May 2024 TZ1 Paper ${paper} below. Reconcile the question paper with the markscheme before producing blocks. Check the mark total twice.\n\n${source}`
  await writeFile(resolve(workRoot, `prompt-paper-${paper}.txt`), prompt)
  console.log(`prompt-paper-${paper}.txt: ${prompt.length.toLocaleString()} characters`)
}

console.log(`system-prompt.txt: ${systemPrompt.length.toLocaleString()} characters; ${examples.length} gold examples`)
