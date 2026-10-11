/** Каталог приёмов как пространство ответа в режиме «выбор приёма».
 *
 * Режим устроен так: на карточке настоящая страница билета, а приём надо
 * найти самому — не выбрать из восьми кнопок одной темы, как в узнавании,
 * а назвать из всех двухсот восьмидесяти шести. Искать по каталогу
 * разрешено и даже предполагается: на экзамене под рукой лежит формульный
 * буклет, и умение быстро найти в нём нужное место — часть работы.
 *
 * Поиск идёт и по названию приёма, и по признаку узнавания: «меняется
 * знак» найдётся по слову из триггера, даже если в названии его нет.
 * Каталог тянется один раз на вкладку — он не меняется между заданиями.
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

interface Props {
  subject: string
  disabled?: boolean
  /** Что выбрано после ответа: подсвечивается и не меняется. */
  locked?: string | null
  onPick: (skill: string) => void
}

export function PickCatalogue({ subject, disabled, locked, onPick }: Props) {
  const [catalogue, setCatalogue] = useState<Catalogue | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [chosen, setChosen] = useState<string | null>(null)
  const search = useRef<HTMLInputElement>(null)

  useEffect(() => {
    let alive = true
    load(subject)
      .then((data) => { if (alive) setCatalogue(data) })
      .catch((failure: unknown) => {
        if (alive) setError(failure instanceof Error ? failure.message : 'нет каталога')
      })
    return () => { alive = false }
  }, [subject])

  // Новая карточка — чистый поиск: прошлый запрос к ней отношения не имеет.
  useEffect(() => { if (!locked) { setChosen(null); setQuery('') } }, [locked])

  const found = useMemo(() => {
    const skills = catalogue?.skills ?? []
    const needle = plain(query.trim())
    if (!needle) return skills
    const words = needle.split(/\s+/)
    return skills.filter((skill) => {
      const hay = plain(`${skill.id} ${skill.name} ${skill.practicum_title} ${skill.trigger}`)
      return words.every((word) => hay.includes(word))
    })
  }, [catalogue, query])

  const groups = useMemo(() => {
    const out: { id: string; title: string; skills: CatalogueSkill[] }[] = []
    for (const skill of found) {
      const last = out[out.length - 1]
      if (last && last.id === skill.practicum) last.skills.push(skill)
      else out.push({ id: skill.practicum, title: skill.practicum_title, skills: [skill] })
    }
    return out
  }, [found])

  const picked = locked ?? chosen

  if (error) return <p className="text-sm text-ink">Каталог приёмов не открылся: {error}</p>
  if (!catalogue) return <p className="font-mono text-[11px] text-faint">каталог грузится…</p>

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <input
          ref={search}
          className="h-9 min-w-0 flex-1 border border-line bg-canvas px-2.5 text-sm text-ink outline-none focus:border-line-strong"
          placeholder="искать приём: по названию или по признаку"
          value={query}
          disabled={disabled}
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && picked && !disabled) {
              event.preventDefault()
              onPick(picked)
            }
          }}
        />
        <button
          type="button"
          disabled={disabled || !picked}
          className="h-9 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
          onClick={() => picked && onPick(picked)}
        >
          ответить
        </button>
      </div>

      <p className="font-mono text-[10px] text-faint">
        {found.length === catalogue.skills.length
          ? `${catalogue.skills.length} приёмов во всех темах`
          : `нашлось ${found.length}`}
        {picked && !locked && ' · Enter отправляет выбранный'}
      </p>

      <div className="max-h-[22rem] overflow-y-auto border border-line bg-canvas">
        {groups.length === 0 && (
          <p className="p-3 text-sm text-muted">Ничего не нашлось. Попробуйте слово из признака узнавания.</p>
        )}
        {groups.map((group) => (
          <div key={group.id}>
            <div className="sticky top-0 z-10 flex items-baseline gap-2 border-b border-line bg-surface px-2.5 py-1 font-mono text-[10px] text-muted">
              <span className="border border-line px-1 py-0.5 text-ink">{group.id}</span>
              <span className="truncate">{group.title}</span>
            </div>
            {group.skills.map((skill) => (
              <button
                key={skill.id}
                type="button"
                disabled={disabled}
                aria-pressed={picked === skill.id}
                className={`flex w-full cursor-pointer flex-col items-start gap-0.5 border-b border-line px-2.5 py-2 text-left hover:bg-surface disabled:cursor-default ${
                  picked === skill.id ? 'bg-surface' : 'bg-canvas'
                }`}
                onClick={() => setChosen(skill.id)}
              >
                <span className="flex w-full items-baseline gap-2">
                  <span className="font-mono text-[10px] text-faint">{skill.rung}</span>
                  <span className="text-sm text-ink">{skill.name}</span>
                </span>
                <span className="pl-5 text-[11px] leading-snug text-muted">{skill.trigger}</span>
              </button>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
