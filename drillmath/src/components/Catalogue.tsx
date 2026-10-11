/** Каталог приёмов: сначала тема, потом её приёмы.
 *
 * Плоским списком на двести восемьдесят шесть строк не пользуются — его
 * скроллят. Поэтому каталог вложенный: разделы силлабуса, внутри темы,
 * внутри темы её лестница приёмов. Поиск идёт поверх вложенности и по
 * всем темам сразу — и по названию приёма, и по признаку узнавания,
 * потому что вспоминают обычно признак, а не имя. Стёрли запрос —
 * вернулись туда, где стояли.
 */
import { useMemo, useRef, useState } from 'react'
import type { Catalogue as Data, Skill } from '../api'

function plain(value: string) {
  return value.toLowerCase().replace(/ё/g, 'е')
}

function count(n: number) {
  const tail = n % 10
  const teen = n % 100
  if (teen >= 11 && teen <= 14) return `${n} приёмов`
  if (tail === 1) return `${n} приём`
  if (tail >= 2 && tail <= 4) return `${n} приёма`
  return `${n} приёмов`
}

interface Props {
  data: Data
  chosen: string | null
  disabled?: boolean
  onChoose: (skill: string) => void
  /** Двойное нажатие по приёму отвечает сразу: так быстрее, когда уверен. */
  onSubmit?: (skill: string) => void
}

export function Catalogue({ data, chosen, disabled, onChoose, onSubmit }: Props) {
  const [query, setQuery] = useState('')
  const [topic, setTopic] = useState<string | null>(null)
  const box = useRef<HTMLDivElement>(null)

  const needle = plain(query.trim())
  const toTop = () => { if (box.current) box.current.scrollTop = 0 }

  const found = useMemo(() => {
    if (!needle) return []
    const words = needle.split(/\s+/)
    return data.skills.filter((skill) => {
      const hay = plain(`${skill.id} ${skill.name} ${skill.practicum_title} ${skill.trigger}`)
      return words.every((word) => hay.includes(word))
    })
  }, [data, needle])

  const sizes = useMemo(() => {
    const out = new Map<string, number>()
    for (const skill of data.skills) out.set(skill.practicum, (out.get(skill.practicum) ?? 0) + 1)
    return out
  }, [data])

  const sections = useMemo(() => {
    const titles = new Map((data.sections ?? []).map((section) => [section.id, section.title]))
    const out: { id: string; title: string; topics: Data['practicums'] }[] = []
    for (const entry of data.practicums) {
      const last = out[out.length - 1]
      if (last && last.id === entry.section) last.topics.push(entry)
      else out.push({ id: entry.section, title: titles.get(entry.section) ?? entry.section, topics: [entry] })
    }
    return out
  }, [data])

  const inside = useMemo(
    () => data.skills.filter((skill) => skill.practicum === topic),
    [data, topic])

  const groups = useMemo(() => {
    const out: { id: string; title: string; skills: Skill[] }[] = []
    for (const skill of found) {
      const last = out[out.length - 1]
      if (last && last.id === skill.practicum) last.skills.push(skill)
      else out.push({ id: skill.practicum, title: skill.practicum_title, skills: [skill] })
    }
    return out
  }, [found])

  const here = data.practicums.find((entry) => entry.id === topic)

  const row = (skill: Skill, withTopic: boolean) => (
    <button
      key={skill.id}
      type="button"
      disabled={disabled}
      aria-pressed={chosen === skill.id}
      onClick={() => onChoose(skill.id)}
      onDoubleClick={() => onSubmit?.(skill.id)}
      className={`flex w-full cursor-pointer flex-col items-start gap-1 border-l-2 px-4 py-3 text-left transition-colors disabled:cursor-default ${
        chosen === skill.id
          ? 'border-l-accent bg-accent-soft'
          : 'border-l-transparent hover:bg-sunken'
      }`}
    >
      <span className="flex w-full items-baseline gap-2.5">
        <span className="w-4 shrink-0 font-mono text-[11px] text-faint">{skill.rung}</span>
        <span className="text-[15px] font-medium text-ink">{skill.name}</span>
        {withTopic && (
          <span className="ml-auto shrink-0 rounded-md bg-sunken px-1.5 py-0.5 font-mono text-[10px] text-muted">
            {skill.practicum}
          </span>
        )}
      </span>
      <span className="pl-[1.625rem] text-[13px] leading-snug text-muted">{skill.trigger}</span>
    </button>
  )

  const header = (text: string) => (
    <div className="sticky top-0 z-10 border-b border-line bg-surface/95 px-4 py-1.5 text-[11px] font-medium tracking-wide text-faint uppercase backdrop-blur">
      {text}
    </div>
  )

  return (
    <div className="flex min-h-0 flex-1 flex-col gap-3">
      <div className="flex items-center gap-2">
        <input
          className="h-11 min-w-0 flex-1 rounded-xl border border-line bg-surface px-3.5 text-[15px] text-ink shadow-xs outline-none placeholder:text-faint focus:border-accent"
          placeholder="искать приём во всех темах"
          value={query}
          disabled={disabled}
          onChange={(event) => { setQuery(event.target.value); toTop() }}
        />
        {query && (
          <button
            type="button"
            className="h-11 cursor-pointer rounded-xl border border-line bg-surface px-3 text-[13px] text-muted hover:text-ink"
            onClick={() => { setQuery(''); toTop() }}
          >
            сбросить
          </button>
        )}
      </div>

      <div className="flex items-baseline gap-2 px-0.5 text-[12px] text-faint">
        {needle ? (
          <span>нашлось {found.length} в {groups.length} темах</span>
        ) : here ? (
          <>
            <button
              type="button"
              className="cursor-pointer text-accent hover:underline"
              onClick={() => { setTopic(null); toTop() }}
            >
              ← все темы
            </button>
            <span className="text-faint">·</span>
            <span className="text-muted">{here.title}</span>
            <span className="ml-auto">{count(inside.length)}</span>
          </>
        ) : (
          <span>{data.practicums.length} тем · {data.skills.length} приёмов</span>
        )}
      </div>

      {/* На телефоне колонка не ограничена высотой экрана, и без потолка
          список разворачивается на все двести восемьдесят шесть строк —
          страница перестаёт кончаться. Потолок в 55dvh оставляет на
          экране и карточку, и кнопку. */}
      <div
        ref={box}
        className="max-h-[55dvh] min-h-0 flex-1 overflow-y-auto overscroll-contain rounded-xl border border-line bg-surface shadow-card lg:max-h-none"
      >
        {needle && groups.length === 0 && (
          <p className="px-4 py-6 text-[15px] text-muted">
            Ничего не нашлось. Попробуйте слово из признака узнавания — например,
            «меняется знак» или «шаг».
          </p>
        )}

        {needle && groups.map((group) => (
          <div key={group.id}>
            {header(`${group.id} · ${group.title}`)}
            {group.skills.map((skill) => row(skill, false))}
          </div>
        ))}

        {!needle && !here && sections.map((section) => (
          <div key={section.id}>
            {header(section.title)}
            {section.topics.map((entry) => (
              <button
                key={entry.id}
                type="button"
                disabled={disabled}
                onClick={() => { setTopic(entry.id); toTop() }}
                className="flex w-full cursor-pointer items-center gap-3 border-l-2 border-l-transparent px-4 py-3 text-left transition-colors hover:bg-sunken disabled:cursor-default"
              >
                <span className="w-8 shrink-0 rounded-md bg-sunken px-1.5 py-0.5 text-center font-mono text-[11px] text-muted">
                  {entry.id}
                </span>
                <span className="text-[15px] text-ink">{entry.title}</span>
                <span className="ml-auto shrink-0 text-[12px] text-faint">{count(sizes.get(entry.id) ?? 0)}</span>
                <span className="shrink-0 text-faint">›</span>
              </button>
            ))}
          </div>
        ))}

        {!needle && here && <>
          {header(`${here.id} · ${here.title}`)}
          {inside.map((skill) => row(skill, false))}
        </>}
      </div>
    </div>
  )
}
