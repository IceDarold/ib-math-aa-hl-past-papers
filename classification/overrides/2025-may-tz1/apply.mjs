#!/usr/bin/env node

import { readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const here = dirname(fileURLToPath(import.meta.url))
const fragmentsRoot = resolve(here, '../../generated/2025-may-tz1/deepseek-v4-pro/fragments')
const documents = new Map()

async function load(name) {
  if (!documents.has(name)) {
    documents.set(name, JSON.parse(await readFile(resolve(fragmentsRoot, `${name}.json`), 'utf8')))
  }
  return documents.get(name)
}

function block(document, id) {
  const match = document.blocks.find((item) => item.id === id)
  if (!match) throw new Error(`Missing block ${id}`)
  return match
}

async function patchBlock(file, id, patch) {
  Object.assign(block(await load(file), id), patch)
}

async function setSourcePages(file, sourcePages) {
  const document = await load(file)
  for (const item of document.blocks) item.source_pages = sourcePages
}

// The question paper prints one [7] allocation for Q11(c)(i)-(ii), so the
// classification contract requires one block rather than an invented 3+4 split.
{
  const document = await load('paper-1-q11')
  const first = document.blocks.find((item) => item.id === '2025-MAY-TZ1-P1-Q11-C-I')
  const second = document.blocks.find((item) => item.id === '2025-MAY-TZ1-P1-Q11-C-II')
  if (first && second) {
    const combined = {
      id: '2025-MAY-TZ1-P1-Q11-C',
      question: '11',
      part: 'C',
      marks: first.marks + second.marks,
      source_pages: '13',
      markscheme_pages: '22',
      task_summary: 'Use a compound angle identity to show that sin 75° = (√2 + √6)/4, then use the sine rule to find QR = 5(√3 - 1) cm.',
      primary_topic: 'geometry.trigonometry',
      secondary_topics: ['geometry.trigonometric_identities'],
      method_family: 'trigonometric_reasoning',
      method_tags: [...new Set([...first.method_tags, ...second.method_tags])],
      method_path: [
        ...first.method_path.map((step) => `(i) ${step}`),
        ...second.method_path.map((step) => `(ii) ${step}`),
      ],
      accepted_alternatives: [...new Set([...first.accepted_alternatives, ...second.accepted_alternatives])],
      evidence: [...first.evidence, ...second.evidence],
      confidence: { segmentation: 'high', topic: 'high', method: 'high' },
      review_flags: ['shared_marks'],
    }
    const index = document.blocks.indexOf(first)
    document.blocks.splice(index, 2, combined)
  }
}

// Q6(a)(i)-(ii) likewise has one printed [3] allocation. Keep the graph flag
// because the combined task includes a sketch and its intercept.
{
  const document = await load('paper-2-q06')
  const first = document.blocks.find((item) => item.id === '2025-MAY-TZ1-P2-Q06-A-I')
  const second = document.blocks.find((item) => item.id === '2025-MAY-TZ1-P2-Q06-A-II')
  if (first && second) {
    const combined = {
      id: '2025-MAY-TZ1-P2-Q06-A',
      question: '6',
      part: 'A',
      marks: first.marks + second.marks,
      source_pages: '8',
      markscheme_pages: '13',
      task_summary: 'Write f(x) = 4 cot x + sin x in terms of sin x and cos x, then sketch y = f(x) for 0 < x < π and show its x-intercept.',
      primary_topic: 'functions.trigonometric_functions',
      secondary_topics: ['geometry.trigonometric_identities', 'functions.graphing'],
      method_family: 'function_analysis',
      method_tags: [...new Set([...first.method_tags, ...second.method_tags])],
      method_path: [
        ...first.method_path.map((step) => `(i) ${step}`),
        ...second.method_path.map((step) => `(ii) ${step}`),
      ],
      accepted_alternatives: [...new Set([...first.accepted_alternatives, ...second.accepted_alternatives])],
      evidence: [...first.evidence, ...second.evidence],
      confidence: { segmentation: 'high', topic: 'medium', method: 'medium' },
      review_flags: ['shared_marks', 'diagram_dependent'],
    }
    const index = document.blocks.indexOf(first)
    document.blocks.splice(index, 2, combined)
  }
}

await patchBlock('paper-1-q04', '2025-MAY-TZ1-P1-Q04-A', {
  method_family: 'probability_and_distributions',
})
await patchBlock('paper-1-q04', '2025-MAY-TZ1-P1-Q04-B', {
  method_family: 'probability_and_distributions',
})
await patchBlock('paper-1-q05', '2025-MAY-TZ1-P1-Q05-A', {
  task_summary: 'Show that the area of picture frame F_n is 20(9/4)^(n-1) cm², then find the mean area of the ten frames in the form p((9/4)^a - 1) cm².',
  method_path: [
    'Recognise that widths and heights form geometric sequences with common ratio 3/2',
    'Deduce that areas form a geometric sequence with first term 20 and common ratio 9/4',
    'Derive the nth term: area of F_n = 20(9/4)^(n-1)',
    'Use the geometric-series formula to obtain S_10 = 16((9/4)^10 - 1)',
    'Divide by 10 and simplify the mean to (8/5)((9/4)^10 - 1)',
    'Identify p = 8/5 and a = 10',
  ],
  evidence: [{
    markscheme_pages: '12',
    basis: 'M1 for finding or recognizing the common ratio; A1 and AG for the area sequence and nth-term formula; M1 and A1 for summing ten terms; A1 for the mean (8/5)((9/4)^10 - 1), so p=8/5 and a=10.',
  }],
  review_flags: ['shared_marks'],
})
await patchBlock('paper-1-q06', '2025-MAY-TZ1-P1-Q06', {
  primary_topic: 'geometry.vectors_3d',
})
await patchBlock('paper-1-q08', '2025-MAY-TZ1-P1-Q08-A', {
  primary_topic: 'functions.logarithmic_functions',
})
await patchBlock('paper-1-q10', '2025-MAY-TZ1-P1-Q10-C', {
  primary_topic: 'number_algebra.inequalities',
})
await patchBlock('paper-1-q10', '2025-MAY-TZ1-P1-Q10-D', {
  primary_topic: 'functions.logarithmic_functions',
})
await patchBlock('paper-1-q10', '2025-MAY-TZ1-P1-Q10-E', {
  primary_topic: 'functions.logarithmic_functions',
})
await patchBlock('paper-1-q11', '2025-MAY-TZ1-P1-Q11-C', {
  method_path: [
    '(i) Express sin 75° as sin(30° + 45°)',
    '(i) Apply sin(A + B) = sin A cos B + cos A sin B',
    '(i) Substitute the exact values and simplify to (√2 + √6)/4',
    '(ii) Let x = QR and apply the sine rule: 5/sin 75° = x/sin 45°',
    '(ii) Substitute the exact values to obtain x = 20/(√2(√2 + √6)) = 20/(2(1 + √3))',
    '(ii) Rationalize the denominator and simplify to x = 5(√3 - 1) cm',
  ],
  accepted_alternatives: [],
  evidence: [
    {
      markscheme_pages: '22',
      basis: '(i) M1 for using the identity for sin(30°+45°), A1A1 for the two exact terms, and AG for (√2+√6)/4.',
    },
    {
      markscheme_pages: '22',
      basis: '(ii) M1 for the sine rule 5/sin75° = x/sin45°; A1 for x = 20/(√2(√2+√6)) or equivalent; M1 for rationalizing; A1 for x = 5(√3-1) cm.',
    },
  ],
})
await patchBlock('paper-1-q12', '2025-MAY-TZ1-P1-Q12-B', {
  method_family: 'algebraic_transformation',
})
await patchBlock('paper-2-q04', '2025-MAY-TZ1-P2-Q04-C', {
  method_family: 'probability_and_distributions',
  review_flags: ['alternative_route'],
})
await patchBlock('paper-2-q06', '2025-MAY-TZ1-P2-Q06-B', {
  method_family: 'numerical_gdc',
})

// The generated draft used PDF indices for these questions. The interface and
// all other sessions use the printed question-paper page numbers.
await setSourcePages('paper-1-q10', '11')
{
  const document = await load('paper-1-q11')
  block(document, '2025-MAY-TZ1-P1-Q11-A').source_pages = '12'
  block(document, '2025-MAY-TZ1-P1-Q11-B').source_pages = '12'
  block(document, '2025-MAY-TZ1-P1-Q11-C').source_pages = '13'
}
await setSourcePages('paper-1-q12', '14')
await setSourcePages('paper-2-q04', '6')
await setSourcePages('paper-2-q06', '8')
await setSourcePages('paper-2-q07', '9')

for (const [name, document] of documents) {
  const marks = document.blocks.reduce((sum, item) => sum + item.marks, 0)
  if (marks !== document.expected_question_marks) {
    throw new Error(`${name}: ${marks} marks, expected ${document.expected_question_marks}`)
  }
  await writeFile(resolve(fragmentsRoot, `${name}.json`), `${JSON.stringify(document, null, 2)}\n`)
  console.log(`${name}: ${document.blocks.length} blocks, ${marks} marks`)
}
