import questionData from '../data/questions.json'
import type { Question, RawQuestion } from '../types'

const methodRules: ReadonlyArray<readonly [string, RegExp]> = [
  ['mathematical_induction', /induction/],
  ['numerical_gdc', /gdc|numerical|regression/],
  ['optimization', /optimi|maximi|minimi|stationary.*objective|objective_function/],
  ['integration', /integral|integration|antiderivative|volume_of_revolution/],
  ['differentiation', /differentiat|derivative|quotient_rule|implicit/],
  ['limits_and_series', /limit|maclaurin|series_expansion/],
  ['complex_number_reasoning', /complex|de_moivre|argand|conjugate|modulus|argument/],
  ['vector_reasoning', /vector|dot_product|cross_product|line_plane|parametri[sz]ation/],
  ['probability_and_distributions', /probability|expectation|distribution|cdf|median/],
  ['combinatorial_counting', /combin|permutation|arrangement|counting/],
  ['sequences_and_recurrences', /sequence|recurrence|arithmetic_|geometric_|equilibrium/],
  ['trigonometric_reasoning', /trigon|sine|cosine|tangent|secant|angle_identity/],
  ['geometric_reasoning', /geometry|area|volume|surface|length|midpoint|circle|sector/],
  ['direct_proof', /proof|divisibility|identity|contradiction/],
  ['mathematical_modelling', /model|constraint|interpret|population/],
  ['function_analysis', /graph|range|domain|asymptote|turning_point|inverse|monotonic/],
  ['equation_and_inequality_solving', /solve|equation|inequality|discriminant|roots|sign_analysis/],
  ['polynomial_structure', /polynomial|coefficient|factor_theorem|reciprocal_root/],
  ['algebraic_transformation', /algebra|factor|expand|rearrange|substitution|simplif|rationali[sz]e/],
]

function splitPipe(value: string): string[] {
  if (!value || value === '-') return []
  return value.split('|').map((part) => part.trim()).filter(Boolean)
}

function splitPath(value: string): string[] {
  if (!value || value === '-') return []
  return value.split(';').map((part) => part.trim()).filter(Boolean)
}

function inferMethodFamily(tags: string[], path: string): string {
  const text = `${tags.join(' ')} ${path}`.toLowerCase()
  return methodRules.find(([, pattern]) => pattern.test(text))?.[0] ?? 'formula_application'
}

function normalizeQuestion(row: RawQuestion): Question {
  const tags = splitPipe(row.method_tags)
  const evidenceItems = JSON.parse(row.evidence || '[]') as Question['evidenceItems']
  const confidenceLevels = JSON.parse(row.confidence || '{}') as Question['confidenceLevels']
  return {
    ...row,
    paper: Number(row.paper),
    marks: Number(row.marks),
    tags,
    secondaryTopics: splitPipe(row.secondary_topics),
    alternatives: splitPipe(row.accepted_alternatives),
    pathSteps: splitPath(row.method_path),
    topicFamily: row.primary_topic.split('.')[0] ?? row.primary_topic,
    methodFamily: row.method_family || inferMethodFamily(tags, row.method_path),
    evidenceItems,
    confidenceLevels,
    reviewFlags: splitPipe(row.review_flags),
  }
}

export const questions = (questionData as RawQuestion[]).map(normalizeQuestion)

export function countBy(
  items: Question[],
  getValue: (item: Question) => string,
): Array<[string, number]> {
  const counts = new Map<string, number>()
  items.forEach((item) => {
    const value = getValue(item)
    counts.set(value, (counts.get(value) ?? 0) + 1)
  })
  return [...counts].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
}

export function filterQuestions(items: Question[], filters: import('../types').Filters): Question[] {
  const query = filters.query.trim().toLowerCase()
  return items.filter((row) => {
    if (filters.paper !== 'all' && row.paper !== Number(filters.paper)) return false
    if (filters.calculator !== 'all' && row.calculator !== filters.calculator) return false
    if (filters.session !== 'all' && row.session !== filters.session) return false
    if (filters.status !== 'all' && row.review_status !== filters.status) return false
    if (filters.topics.size && !filters.topics.has(row.topicFamily)) return false
    if (filters.methods.size && !filters.methods.has(row.methodFamily)) return false
    if (!query) return true

    return [
      row.id,
      row.task_summary,
      row.primary_topic,
      row.secondary_topics,
      row.method_tags,
      row.method_path,
      row.accepted_alternatives,
      row.methodFamily,
      row.session,
      row.zone,
      row.review_status,
      row.review_flags,
      `paper ${row.paper}`,
      `p${row.paper}`,
    ].join(' ').toLowerCase().includes(query)
  })
}

export function shortId(row: Question): string {
  const part = row.part === '-' ? '' : `-${row.part.toUpperCase()}`
  const session = row.session === 'May 2024' ? '24M' : '24N'
  const zone = row.zone === 'Common' ? 'C' : row.zone
  return `${session}-${zone}-P${row.paper}-Q${row.question.padStart(2, '0')}${part}`
}

export function pdfUrl(row: Question, filename: 'question-paper.pdf' | 'markscheme.pdf'): string {
  const pageSource = filename === 'markscheme.pdf' ? row.markscheme_pages : row.source_pages
  const page = pageSource.split('-')[0] ?? pageSource
  const session = row.session === 'May 2024' ? 'May/TZ1' : 'November/Common'
  return `/AA_HL/2024/${session}/Paper%20${row.paper}/${filename}#page=${encodeURIComponent(page)}`
}

export function formatKey(key: string): string {
  return key.split('_').map((part) => `${part[0]?.toUpperCase() ?? ''}${part.slice(1)}`).join(' ')
}

export function pluralize(number: number, one: string, few: string, many: string): string {
  const mod10 = number % 10
  const mod100 = number % 100
  const form = mod10 === 1 && mod100 !== 11
    ? one
    : mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)
      ? few
      : many
  return `${number} ${form}`
}
