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

/** Какие предметы подняты службой. */
export async function subjects(): Promise<SubjectInfo[]> {
  const response = await fetch(`${API}/subjects`)
  if (!response.ok) throw new Error('список предметов не пришёл')
  return (await response.json()).subjects ?? []
}
