/** Запросы к тренажёру. Служба одна на все входы — ib-drill на 8042,
 *  nginx проксирует сюда `/api/drill`. Своего состояния у сайта нет:
 *  и расписание, и журнал живут на сервере, поэтому занятие, начатое
 *  с телефона, видно с ноутбука. */
const API = '/api/drill'
const SUBJECT = 'math'

function url(path: string, params: Record<string, string | number | boolean | undefined> = {}) {
  const query = new URLSearchParams({ subject: SUBJECT })
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value))
  }
  return `${API}${path}?${query.toString()}`
}

async function get<T>(path: string, params?: Record<string, string | number | boolean | undefined>) {
  const response = await fetch(url(path, params), { headers: { Accept: 'application/json' } })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error((body as { error?: string }).error ?? `служба ответила ${response.status}`)
  return body as T
}

async function post<T>(path: string, payload: Record<string, unknown>) {
  const response = await fetch(`${API}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...payload, subject: SUBJECT }),
  })
  const body = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error((body as { error?: string }).error ?? `служба ответила ${response.status}`)
  return body as T
}

export interface Topic {
  id: string
  title: string
  section: string
  marks: number | null
  pick: number
  skills: number
}

export interface Setup {
  subject: string
  title: string
  sections: { id: string; title: string }[]
  practicums: Topic[]
}

export interface Card {
  item: string
  kind: 'pick'
  block: string
  reference: string
  marks: number
  paper: number | null
  calculator: string | null
  pages: number
  budget_ms: number
}

export interface Skill {
  id: string
  name: string
  practicum: string
  practicum_title: string
  section: string
  rung: number
  trigger: string
  calculator?: string
}

export interface Catalogue {
  /** Служба постарше отдаёт каталог без разделов: сайт это переживает. */
  sections?: { id: string; title: string }[]
  practicums: { id: string; title: string; section: string }[]
  skills: Skill[]
}

export interface Verdict {
  ok: boolean
  message: string
  skill: string
  skill_name: string
  trigger: string
  chain: string[]
  traps: string[]
  practicum: string
  picked?: { skill: string; name: string; practicum: string; near: boolean } | null
  method?: string[]
  alternatives?: string[]
  reference?: string
  marks?: number | null
  block?: string
  mark?: string
  strength?: { score: number | null; stability: number | null; due_in_days: number | null }
}

export const api = {
  setup: () => get<Setup>('/setup'),
  catalogue: () => get<Catalogue>('/catalogue'),
  next: (options: { topics?: string[]; named?: boolean; avoid?: string[] }) =>
    get<Card>('/next', {
      mode: 'pick',
      practicums: (options.topics ?? []).join(','),
      named: options.named ? 1 : 0,
      avoid: (options.avoid ?? []).join(','),
    }),
  answer: (payload: { item: string; answer: string; ms: number; first_ms: number }) =>
    post<Verdict>('/answer', { ...payload, mode: 'pick' }),
  flag: (block: string, skill: string) => post<{ ok: boolean }>('/flag', { block, skill }),
  page: (block: string, index: number) =>
    url('/page', { block, kind: 'question', n: index, crop: 1 }),
}
