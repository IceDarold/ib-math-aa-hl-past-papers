import type { Filters, Question, RawQuestion } from '../types'
import { normalizeQuestion } from './questions'

export interface AtlasFacets {
  total: number
  verified: number
  session_zones: number
  sessions: Array<[string, number]>
  zones: Array<[string, number]>
  topics: Array<[string, number]>
  methods: Array<[string, number]>
}

export interface QuestionPage {
  items: Question[]
  total: number
  totalMarks: number
  page: number
  pageSize: number
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(`API request failed (${response.status})`)
  return response.json() as Promise<T>
}

export function fetchFacets(signal?: AbortSignal) {
  return request<AtlasFacets>('/api/facets', signal)
}

export async function fetchQuestions(filters: Filters, page: number, signal?: AbortSignal): Promise<QuestionPage> {
  const params = new URLSearchParams({ page: String(page), page_size: '50' })
  if (filters.query.trim()) params.set('q', filters.query.trim())
  if (filters.paper !== 'all') params.set('paper', filters.paper)
  if (filters.calculator !== 'all') params.set('calculator', filters.calculator)
  if (filters.session !== 'all') params.set('session', filters.session)
  if (filters.zone !== 'all') params.set('zone', filters.zone)
  if (filters.status !== 'all') params.set('status', filters.status)
  filters.topics.forEach((topic) => params.append('topic', topic))
  filters.methods.forEach((method) => params.append('method', method))

  const data = await request<{ items: RawQuestion[]; total: number; total_marks: number; page: number; page_size: number }>(`/api/questions?${params}`, signal)
  return { items: data.items.map(normalizeQuestion), total: data.total, totalMarks: data.total_marks, page: data.page, pageSize: data.page_size }
}

export async function fetchQuestion(id: string, signal?: AbortSignal): Promise<Question> {
  return normalizeQuestion(await request<RawQuestion>(`/api/questions/${encodeURIComponent(id)}`, signal))
}
