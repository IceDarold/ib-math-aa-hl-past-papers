import type { Filters, Question, RawQuestion } from '../types'
import { normalizeQuestion } from './questions'

type Count = Array<[string, number]>

export interface AtlasFacets {
  subject: string
  total: number
  verified: number
  session_zones: number
  sessions: Count
  zones: Count
  topics: Count
  methods: Count
  // Бумаги, статусы и калькулятор раньше были вшиты в страницу тремя
  // парами кнопок. Теперь их называет служба: у физики бумаги зовутся
  // 1A, 1B и 2, а статус один — «выведено из схемы оценивания».
  papers: Count
  statuses: Count
  calculators: Count
  columns: string[]
  // Форма ответа есть только там, где предмет её знает.
  forms?: Count
}

export interface AtlasSubject {
  id: string
  ready: boolean
  default: boolean
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

export async function fetchSubjects(signal?: AbortSignal): Promise<AtlasSubject[]> {
  const data = await request<{ subjects: AtlasSubject[] }>('/api/subjects', signal)
  return data.subjects ?? []
}

export function fetchFacets(subject: string, signal?: AbortSignal) {
  return request<AtlasFacets>(`/api/facets?subject=${encodeURIComponent(subject)}`, signal)
}

export async function fetchQuestions(subject: string, filters: Filters, page: number, signal?: AbortSignal): Promise<QuestionPage> {
  const params = new URLSearchParams({ subject, page: String(page), page_size: '50' })
  if (filters.query.trim()) params.set('q', filters.query.trim())
  if (filters.paper !== 'all') params.set('paper', filters.paper)
  if (filters.calculator !== 'all') params.set('calculator', filters.calculator)
  if (filters.session !== 'all') params.set('session', filters.session)
  if (filters.zone !== 'all') params.set('zone', filters.zone)
  if (filters.status !== 'all') params.set('status', filters.status)
  filters.topics.forEach((topic) => params.append('topic', topic))
  filters.methods.forEach((method) => params.append('method', method))
  filters.forms.forEach((form) => params.append('form', form))

  const data = await request<{ items: RawQuestion[]; total: number; total_marks: number; page: number; page_size: number }>(`/api/questions?${params}`, signal)
  return { items: data.items.map(normalizeQuestion), total: data.total, totalMarks: data.total_marks, page: data.page, pageSize: data.page_size }
}

export async function fetchQuestion(subject: string, id: string, signal?: AbortSignal): Promise<Question> {
  return normalizeQuestion(await request<RawQuestion>(
    `/api/questions/${encodeURIComponent(id)}?subject=${encodeURIComponent(subject)}`, signal))
}
