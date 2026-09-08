/** Запросы к тренажёру: предмет едет с каждым.
 *
 * Служба держит несколько предметов сразу — математику и физику, — и
 * отвечает по тому, который назвали. Не назвали — ответит предметом по
 * умолчанию, и это самое неприятное, что может случиться: занятие по
 * физике незаметно уедет в математику. Поэтому предмет подставляется
 * здесь, в одном месте, а не в каждом вызове.
 */
export const API = '/api/drill'

export type SubjectInfo = {
  id: string
  title: string
  /** Есть ли у предмета письменный режим: подлинник страницами. */
  written: boolean
  default: boolean
}

/** Адрес ручки для одного предмета: `/next?mode=mixed` → `…&subject=math`. */
export function url(path: string, subject: string): string {
  const [route, query] = path.split('?')
  const params = new URLSearchParams(query ?? '')
  params.set('subject', subject)
  return `${API}${route}?${params.toString()}`
}

/** Тело POST-запроса вместе с предметом. */
export function payload(subject: string, body: Record<string, unknown>): string {
  return JSON.stringify({ ...body, subject })
}

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(path, { signal, headers: { Accept: 'application/json' } })
  if (!response.ok) throw new Error(`тренажёр ответил ${response.status}`)
  return response.json() as Promise<T>
}

export type PracticumSkill = {
  id: string
  name: string
  rung: number
  trigger: string
  calculator?: string | null
}

export type PracticumLink = { label: string; href: string; kind: string }

export type Practicum = {
  id: string
  title: string
  section: string
  marks: number | null
  blocks: number | null
  skills: PracticumSkill[]
  status: 'ready' | 'planned'
  links: PracticumLink[]
  note: string
  /** Чем открыть эти же вопросы в атласе: у предметов размечено по-разному. */
  atlas: { query?: string; methods?: string[] }
}

export type PracticumMap = {
  subject: string
  title: string
  sections: Array<{ id: string; title: string }>
  practicums: Practicum[]
}

/** Карта практикумов предмета: чему учат и чем это открыть.
 *
 *  Раньше страница держала этот список у себя и отстала: в репозитории
 *  двадцать два собранных практикума, а страница знала о двух. Теперь он
 *  приходит из той же карты, по которой практикумы собираются. */
export function fetchPracticums(subject: string, signal?: AbortSignal) {
  return request<PracticumMap>(url('/practicums', subject), signal)
}

/** Какие предметы подняты службой. */
export async function subjects(signal?: AbortSignal): Promise<SubjectInfo[]> {
  const data = await request<{ subjects: SubjectInfo[] }>(`${API}/subjects`, signal)
  return data.subjects ?? []
}
