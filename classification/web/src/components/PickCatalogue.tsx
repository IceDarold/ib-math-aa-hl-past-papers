/** Каталог приёмов как пространство ответа в режиме «выбор приёма».
 *
 * Режим устроен так: на карточке настоящая страница билета, а приём надо
 * найти самому — не выбрать из восьми кнопок одной темы, как в узнавании,
 * а назвать из всех двухсот восьмидесяти шести. Искать по каталогу
 * разрешено и даже предполагается: на экзамене под рукой лежит формульный
 * буклет, и умение быстро найти в нём нужное место — часть работы.
 *
 * Каталог вложенный: сначала тема, потом её приёмы. Плоским списком на
 * двести восемьдесят шесть строк пользоваться нельзя — в нём не читают,
 * а скроллят. Зато поиск плоский и идёт поверх вложенности: он ищет и по
 * названию приёма, и по признаку узнавания, по всем темам сразу, и
 * показывает, из какой тема находка. Стёрли запрос — вернулись туда, где
 * стояли.
 *
 * Каталог тянется один раз на вкладку: между заданиями он не меняется.
 */
import { useEffect, useMemo, useRef, useState } from 'react'
import * as drillApi from '../drillApi'

export interface CatalogueSkill {
  id: string
  name: string
  practicum: string
  practicum_title: string
  section: string
  rung: number
  trigger: string
  calculator?: string
}

interface Catalogue {
  sections?: { id: string; title: string }[]
  practicums: { id: string; title: string; section: string }[]
  skills: CatalogueSkill[]
}

/** Каталог один на вкладку: между заданиями он не меняется. */
const cache = new Map<string, Promise<Catalogue>>()

function load(subject: string): Promise<Catalogue> {
  const have = cache.get(subject)
  if (have) return have
  const asked = fetch(drillApi.url('/catalogue', subject), {
    headers: { Accept: 'application/json' },
  }).then((response) => {
    if (!response.ok) throw new Error(`каталог не пришёл: ${response.status}`)
    return response.json() as Promise<Catalogue>
  })
  cache.set(subject, asked)
  return asked
}

/** Нормализация для поиска: регистр и ё. */
function plain(value: string): string {
  return value.toLowerCase().replace(/ё/g, 'е')
}

function count(n: number): string {
  const tail = n % 10
  const teen = n % 100
  if (teen >= 11 && teen <= 14) return `${n} приёмов`
  if (tail === 1) return `${n} приём`
  if (tail >= 2 && tail <= 4) return `${n} приёма`
  return `${n} приёмов`
}

interface Props {
  subject: string
  disabled?: boolean
  onPick: (skill: string) => void
}

export function PickCatalogue({ subject, disabled, onPick }: Props) {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [topic, setTopic] = useState<string | null>(null)
  const [chosen, setChosen] = useState<string | null>(null)
  const list = useRef<HTMLDivElement>(null)

  useEffect(() => {
    let alive = true
    load(subject)
      .then((data) => { if (alive) setCatalogue(data) })
      .catch((failure: unknown) => {
        if (alive) setError(failure instanceof Error ? failure.message : 'нет каталога')
      })
    return () => { alive = false }
  }, [subject])

  const needle = plain(query.trim())

  const found = useMemo(() => {
    const skills = catalogue?.skills ?? []
    if (!needle) return []
    const words = needle.split(/\s+/)
    return skills.filter((skill) => {
      const hay = plain(`${skill.id} ${skill.name} ${skill.practicum_title} ${skill.trigger}`)
      return words.every((word) => hay.includes(word))
    })
  }, [catalogue, needle])

  /** Темы по разделам силлабуса: первый уровень каталога. */
  const sections = useMemo(() => {
    if (!catalogue) return []
    const titles = new Map((catalogue.sections ?? []).map((s) => [s.id, s.title]))
    const out: { id: string; title: string; topics: typeof catalogue.practicums }[] = []
    for (const entry of catalogue.practicums) {
      const last = out[out.length - 1]
      if (last && last.id === entry.section) last.topics.push(entry)
      else out.push({
        id: entry.section,
        title: titles.get(entry.section) ?? entry.section,
        topics: [entry],
      })
    }
    return out
  }, [catalogue])

  const sizes = useMemo(() => {
    const out = new Map<string, number>()
    for (const skill of catalogue?.skills ?? []) {
      out.set(skill.practicum, (out.get(skill.practicum) ?? 0) + 1)
    }
    return out
  }, [catalogue])

  const inside = useMemo(
    () => (catalogue?.skills ?? []).filter((skill) => skill.practicum === topic),
    [catalogue, topic])

  /** Поиск идёт поверх вложенности: находки сгруппированы по темам. */
  const groups = useMemo(() => {
    const out: { id: string; title: string; skills: CatalogueSkill[] }[] = []
    for (const skill of found) {
      const last = out[out.length - 1]
      if (last && last.id === skill.practicum) last.skills.push(skill)
      else out.push({ id: skill.practicum, title: skill.practicum_title, skills: [skill] })
    }
    return out
  }, [found])

  if (error) return <p className="text-sm text-ink">Каталог приёмов не открылся: {error}</p>
  if (!catalogue) return <p className="font-mono text-[11px] text-faint">каталог грузится…</p>

  const here = catalogue.practicums.find((entry) => entry.id === topic)

  /** Строка приёма — одинаковая и в теме, и в находках поиска. */
  const line = (skill: CatalogueSkill, withTopic: boolean) => (
    <button
      key={skill.id}
      type="button"
      disabled={disabled}
      aria-pressed={chosen === skill.id}
      className={`flex w-full cursor-pointer flex-col items-start gap-0.5 border-b border-line px-2.5 py-2 text-left hover:bg-surface disabled:cursor-default ${
        chosen === skill.id ? 'bg-surface' : 'bg-canvas'
      }`}
      onClick={() => setChosen(skill.id)}
    >
      <span className="flex w-full items-baseline gap-2">
        <span className="font-mono text-[10px] text-faint">{skill.rung}</span>
        <span className="text-sm text-ink">{skill.name}</span>
        {withTopic && (
          <span className="ml-auto shrink-0 font-mono text-[10px] text-faint">{skill.practicum}</span>
        )}
      </span>
      <span className="pl-5 text-[11px] leading-snug text-muted">{skill.trigger}</span>
    </button>
  )

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <input
          className="h-9 min-w-0 flex-1 border border-line bg-canvas px-2.5 text-sm text-ink outline-none focus:border-line-strong"
          placeholder="искать приём по всем темам: по названию или по признаку"
          value={query}
          disabled={disabled}
          onChange={(event) => {
            setQuery(event.target.value)
            if (list.current) list.current.scrollTop = 0
          }}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && chosen && !disabled) {
              event.preventDefault()
              onPick(chosen)
            }
          }}
        />
        <button
          type="button"
          disabled={disabled || !chosen}
          className="h-9 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
          onClick={() => chosen && onPick(chosen)}
        >
          ответить
        </button>
      </div>

      <div className="flex flex-wrap items-baseline gap-x-3 font-mono text-[10px] text-faint">
        {needle
          ? <span>нашлось {found.length} в {groups.length} темах</span>
          : here
            ? <span>{here.id} · {count(inside.length)}</span>
            : <span>{catalogue.practicums.length} тем, {catalogue.skills.length} приёмов</span>}
        {chosen && <span className="text-muted">Enter отправляет выбранный</span>}
      </div>

      <div ref={list} className="max-h-[22rem] overflow-y-auto border border-line bg-canvas">
        {/* Поиск: плоский список поверх вложенности, с пометкой темы. */}
        {needle && groups.length === 0 && (
          <p className="p-3 text-sm text-muted">Ничего не нашлось. Попробуйте слово из признака узнавания.</p>
        )}
        {needle && groups.map((group) => (
          <div key={group.id}>
            <div className="sticky top-0 z-10 flex items-baseline gap-2 border-b border-line bg-surface px-2.5 py-1 font-mono text-[10px] text-muted">
              <span className="border border-line px-1 py-0.5 text-ink">{group.id}</span>
              <span className="truncate">{group.title}</span>
            </div>
            {group.skills.map((skill) => line(skill, false))}
          </div>
        ))}

        {/* Первый уровень: разделы силлабуса и темы внутри них. */}
        {!needle && !here && sections.map((section) => (
          <div key={section.id}>
            <div className="sticky top-0 z-10 border-b border-line bg-surface px-2.5 py-1 font-mono text-[10px] text-muted">
              {section.title}
            </div>
            {section.topics.map((entry) => (
              <button
                key={entry.id}
                type="button"
                disabled={disabled}
                className="flex w-full cursor-pointer items-baseline gap-2 border-b border-line bg-canvas px-2.5 py-2 text-left hover:bg-surface disabled:cursor-default"
                onClick={() => { setTopic(entry.id); if (list.current) list.current.scrollTop = 0 }}
              >
                <span className="shrink-0 border border-line px-1 py-0.5 font-mono text-[10px] text-ink">{entry.id}</span>
                <span className="text-sm text-ink">{entry.title}</span>
                <span className="ml-auto shrink-0 font-mono text-[10px] text-faint">
                  {count(sizes.get(entry.id) ?? 0)} →
                </span>
              </button>
            ))}
          </div>
        ))}

        {/* Второй уровень: приёмы выбранной темы, по ступеням лестницы. */}
        {!needle && here && <>
          <div className="sticky top-0 z-10 flex items-baseline gap-2 border-b border-line bg-surface px-2.5 py-1">
            <button
              type="button"
              className="cursor-pointer border-0 bg-transparent p-0 font-mono text-[10px] text-muted underline hover:text-ink"
              onClick={() => { setTopic(null); if (list.current) list.current.scrollTop = 0 }}
            >
              ← все темы
            </button>
            <span className="border border-line px-1 py-0.5 font-mono text-[10px] text-ink">{here.id}</span>
            <span className="truncate font-mono text-[10px] text-muted">{here.title}</span>
          </div>
          {inside.map((skill) => line(skill, false))}
        </>}
      </div>
    </div>
  )
}
