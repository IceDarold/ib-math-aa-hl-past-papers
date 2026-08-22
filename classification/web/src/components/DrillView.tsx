import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { practicumSections } from '../data/practicums'
import { MathText } from './MathText'

type Mode = 'mixed' | 'recognition' | 'compute'
type Order = 'schedule' | 'ladder' | 'random'
type Screen = 'setup' | 'running' | 'done'

interface Option { code: string; name: string }

interface Item {
  item: string
  kind: 'recognition' | 'compute'
  skill: string
  skill_name: string
  trigger: string
  practicum: string
  practicum_title: string
  prompt: string
  note?: string
  options?: Option[]
  budget_ms: number
}

interface Verdict {
  ok: boolean
  message: string
  skill: string
  skill_name: string
  trigger: string
  chain: string[]
  traps: string[]
  practicum: string
  answer: string
}

interface SetupPracticum {
  id: string
  title: string
  section: string
  marks: number | null
  skills: number
  recognition: number
  compute: number
  share: number
}

interface SkillStat {
  id: string
  practicum: string
  name: string
  rung: number
  seen: number
  wrong: number
  box: number | null
  due_in_days: number | null
  has_compute: boolean
}

interface Stats {
  skills: SkillStat[]
  totals: { attempts: number; correct: number; avg_ms: number; avg_first_ms: number; today: number; today_correct: number }
}

interface Settings {
  mode: Mode
  practicums: string[]
  length: number
  order: Order
  onlyDue: boolean
  showTimer: boolean
}

interface Done {
  skill: string
  skillName: string
  practicum: string
  kind: Item['kind']
  ok: boolean
  ms: number
  firstMs: number
}

const API = '/api/drill'
/** Подпись части разбора: одна и та же во всех строках, чтобы их не путали. */
const LABEL = 'font-mono text-[10px] uppercase tracking-wide text-faint max-[560px]:pt-1.5'
const SETTINGS_KEY = 'question-atlas:drill-setup'

const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: 'mixed', label: 'вперемешку', hint: 'И назвать приём, и решить — вразнобой' },
  { id: 'recognition', label: 'узнавание', hint: 'Только назвать приём. Считать не нужно' },
  { id: 'compute', label: 'счёт', hint: 'Только решить и ввести ответ' },
]

const ORDERS: { id: Order; label: string; hint: string }[] = [
  { id: 'schedule', label: 'по расписанию', hint: 'Что весит больше на экзамене, что просрочено и где ошибки' },
  { id: 'ladder', label: 'сплошь', hint: 'Подряд от простого к сложному, реже виденное вперёд' },
  { id: 'random', label: 'наугад', hint: 'Поровну, без всякого расписания' },
]

const LENGTHS = [10, 20, 40, 0]

const DEFAULTS: Settings = {
  mode: 'mixed',
  practicums: [],
  length: 20,
  order: 'schedule',
  onlyDue: false,
  showTimer: true,
}

function loadSettings(): Settings {
  try {
    const stored = JSON.parse(localStorage.getItem(SETTINGS_KEY) ?? 'null') as unknown
    if (stored && typeof stored === 'object') return { ...DEFAULTS, ...stored as Partial<Settings> }
  } catch {
    /* настройки — удобство, а не данные */
  }
  return DEFAULTS
}

function saveSettings(settings: Settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
  } catch {
    /* приватное окно, чистая история — не беда */
  }
}

function seconds(ms: number) {
  return `${(ms / 1000).toFixed(1)} с`
}

function minutes(ms: number) {
  const total = Math.round(ms / 1000)
  return total < 60 ? `${total} с` : `${Math.floor(total / 60)} мин ${String(total % 60).padStart(2, '0')} с`
}

/** Сколько заданий этой темы доступно в выбранном режиме. */
function available(practicum: SetupPracticum, mode: Mode) {
  if (mode === 'recognition') return practicum.recognition
  if (mode === 'compute') return practicum.compute
  return practicum.recognition + practicum.compute
}

function tileTone(skill: SkillStat) {
  if (!skill.seen) return 'bg-surface text-faint'
  if (skill.wrong / skill.seen > 0.4) return 'bg-ink text-canvas'
  if (skill.due_in_days !== null && skill.due_in_days < 0) return 'bg-primary-soft text-ink'
  return 'bg-canvas text-muted'
}

export function DrillView() {
  const [screen, setScreen] = useState<Screen>('setup')
  const [settings, setSettings] = useState<Settings>(loadSettings)
  const [setup, setSetup] = useState<SetupPracticum[] | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [item, setItem] = useState<Item | null>(null)
  const [verdict, setVerdict] = useState<Verdict | null>(null)
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [done, setDone] = useState<Done[]>([])

  const shownAt = useRef(0)
  const firstKeyAt = useRef(0)
  const startedAt = useRef(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const recent = useRef<string[]>([])

  useEffect(() => { saveSettings(settings) }, [settings])

  const loadStats = useCallback(async () => {
    try {
      const response = await fetch(`${API}/stats`)
      if (response.ok) setStats(await response.json())
    } catch { /* статистика не критична */ }
  }, [])

  useEffect(() => {
    void (async () => {
      try {
        const response = await fetch(`${API}/setup`)
        if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
        const payload = await response.json() as { practicums: SetupPracticum[] }
        setSetup(payload.practicums)
      } catch (failure) {
        setError(failure instanceof Error ? failure.message : 'не отвечает')
      }
    })()
    void loadStats()
  }, [loadStats])

  const chosen = useMemo(() => {
    if (!setup) return []
    const picked = settings.practicums.length ? settings.practicums : setup.map((entry) => entry.id)
    return setup.filter((entry) => picked.includes(entry.id) && available(entry, settings.mode) > 0)
  }, [settings.mode, settings.practicums, setup])

  const chosenSkills = useMemo(
    () => chosen.reduce((sum, entry) => sum + (settings.mode === 'compute' ? entry.compute : entry.skills), 0),
    [chosen, settings.mode],
  )

  const nextItem = useCallback(async () => {
    setBusy(true)
    setVerdict(null)
    setAnswer('')
    setError(null)
    try {
      const params = new URLSearchParams({
        mode: settings.mode,
        order: settings.order,
        only_due: settings.onlyDue ? '1' : '0',
        avoid: recent.current.slice(-3).join(','),
        practicums: chosen.map((entry) => entry.id).join(','),
      })
      const response = await fetch(`${API}/next?${params.toString()}`)
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      setItem(await response.json())
      shownAt.current = performance.now()
      firstKeyAt.current = 0
      setElapsed(0)
      window.setTimeout(() => inputRef.current?.focus(), 30)
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
      setItem(null)
    } finally {
      setBusy(false)
    }
  }, [chosen, settings.mode, settings.onlyDue, settings.order])

  const start = useCallback(() => {
    setDone([])
    recent.current = []
    startedAt.current = performance.now()
    setScreen('running')
    void nextItem()
  }, [nextItem])

  const finish = useCallback(() => {
    setScreen('done')
    setItem(null)
    setVerdict(null)
    void loadStats()
  }, [loadStats])

  useEffect(() => {
    if (screen !== 'running' || !item || verdict) return
    const timer = window.setInterval(() => setElapsed(performance.now() - shownAt.current), 100)
    return () => window.clearInterval(timer)
  }, [item, screen, verdict])

  const submit = useCallback(async (raw: string) => {
    if (!item || busy || verdict) return
    const value = raw.trim()
    if (!value) return
    setBusy(true)
    const ms = Math.round(performance.now() - shownAt.current)
    const firstMs = Math.round((firstKeyAt.current || performance.now()) - shownAt.current)
    try {
      const response = await fetch(`${API}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: item.item, answer: value, mode: settings.mode, ms, first_ms: firstMs }),
      })
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      const result: Verdict = await response.json()
      setVerdict(result)
      recent.current = [...recent.current, item.skill].slice(-6)
      setDone((current) => [...current, {
        skill: item.skill,
        skillName: result.skill_name,
        practicum: item.practicum,
        kind: item.kind,
        ok: result.ok,
        ms,
        firstMs,
      }])
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    } finally {
      setBusy(false)
    }
  }, [busy, item, settings.mode, verdict])

  const markFirstKey = useCallback(() => {
    if (!firstKeyAt.current) firstKeyAt.current = performance.now()
  }, [])

  const advance = useCallback(() => {
    if (settings.length > 0 && done.length >= settings.length) finish()
    else void nextItem()
  }, [done.length, finish, nextItem, settings.length])

  useEffect(() => {
    if (screen !== 'running') return
    const onKey = (event: KeyboardEvent) => {
      if (verdict) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); advance() }
        return
      }
      if (!item || item.kind !== 'recognition' || !item.options) return
      const index = Number.parseInt(event.key, 10)
      const option = Number.isInteger(index) ? item.options[index - 1] : undefined
      if (option) { markFirstKey(); void submit(option.code) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [advance, item, markFirstKey, screen, submit, verdict])

  const toggle = (id: string) => {
    setSettings((current) => {
      const all = setup?.map((entry) => entry.id) ?? []
      const base = current.practicums.length ? current.practicums : all
      const next = base.includes(id) ? base.filter((entry) => entry !== id) : [...base, id]
      return { ...current, practicums: next.length === all.length ? [] : next }
    })
  }

  const isPicked = (id: string) => !settings.practicums.length || settings.practicums.includes(id)

  const bySection = useMemo(() => {
    if (!setup) return []
    return practicumSections
      .map((section) => ({ ...section, entries: setup.filter((entry) => entry.section === section.id) }))
      .filter((section) => section.entries.length > 0)
  }, [setup])

  // --- итог сессии ------------------------------------------------------
  const summary = useMemo(() => {
    const correct = done.filter((entry) => entry.ok).length
    const total = done.length
    const spent = done.reduce((sum, entry) => sum + entry.ms, 0)
    const recognition = done.filter((entry) => entry.kind === 'recognition')
    const misses = new Map<string, { name: string; practicum: string; wrong: number; total: number }>()
    for (const entry of done) {
      const row = misses.get(entry.skill) ?? { name: entry.skillName, practicum: entry.practicum, wrong: 0, total: 0 }
      row.total += 1
      if (!entry.ok) row.wrong += 1
      misses.set(entry.skill, row)
    }
    return {
      correct,
      total,
      spent,
      avgFirst: recognition.length
        ? recognition.reduce((sum, entry) => sum + entry.firstMs, 0) / recognition.length
        : 0,
      weak: [...misses.values()].filter((row) => row.wrong > 0).sort((a, b) => b.wrong - a.wrong),
    }
  }, [done])

  if (error && !setup) {
    return <div className="min-h-0 flex-1 overflow-y-auto bg-canvas p-6">
      <p className="border border-line bg-surface p-3 text-sm text-ink">Тренажёр не отвечает: {error}</p>
    </div>
  }

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">

        {screen === 'setup' && setup && (
          <>
            <div className="flex flex-col gap-1">
              <h2 className="text-lg text-ink">Повторение</h2>
              <p className="text-sm text-muted">
                Практикум учит приёму, тренажёр держит его в форме. Соберите набор и начните.
              </p>
            </div>

            <section className="flex flex-col gap-2">
              <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Режим</h3>
              <div className="grid grid-cols-3 gap-1.5 max-[560px]:grid-cols-1">
                {MODES.map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    aria-pressed={settings.mode === entry.id}
                    className={`flex cursor-pointer flex-col gap-1 border p-2.5 text-left ${settings.mode === entry.id ? 'border-line-strong bg-surface' : 'border-line bg-canvas hover:bg-surface'}`}
                    onClick={() => setSettings((current) => ({ ...current, mode: entry.id }))}
                  >
                    <span className="font-mono text-[11px] text-ink">{entry.label}</span>
                    <span className="text-[11px] leading-snug text-muted">{entry.hint}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <div className="flex items-baseline justify-between gap-3">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Темы</h3>
                <div className="flex gap-2 font-mono text-[10px]">
                  <button type="button" className="cursor-pointer border-0 bg-transparent text-muted hover:text-ink" onClick={() => setSettings((current) => ({ ...current, practicums: [] }))}>все</button>
                </div>
              </div>
              {bySection.map((section) => (
                <div key={section.id} className="flex flex-col gap-1">
                  <span className="text-[11px] text-faint">{section.title}</span>
                  <div className="flex flex-wrap gap-1.5">
                    {section.entries.map((entry) => {
                      const count = available(entry, settings.mode)
                      const off = count === 0
                      const on = isPicked(entry.id) && !off
                      return (
                        <button
                          key={entry.id}
                          type="button"
                          disabled={off}
                          title={off ? `${entry.title} — в этом режиме заданий пока нет` : `${entry.title} — ${entry.marks ?? '?'} баллов архива, ${entry.skills} приёмов`}
                          aria-pressed={on}
                          className={`flex cursor-pointer items-baseline gap-1.5 border px-2 py-1 ${off ? 'border-line bg-canvas text-faint line-through' : on ? 'border-line-strong bg-ink text-canvas' : 'border-line bg-canvas text-muted hover:bg-surface'}`}
                          onClick={() => toggle(entry.id)}
                        >
                          <span className="font-mono text-[11px]">{entry.id}</span>
                          <span className="text-[11px]">{count || '—'}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
              <p className="text-[11px] text-faint">
                Число на плитке — сколько заданий доступно в выбранном режиме.
              </p>
            </section>

            <section className="grid grid-cols-2 gap-4 max-[560px]:grid-cols-1">
              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Длина</h3>
                <div className="flex border border-line">
                  {LENGTHS.map((length) => (
                    <button
                      key={length}
                      type="button"
                      aria-pressed={settings.length === length}
                      className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${settings.length === length ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                      onClick={() => setSettings((current) => ({ ...current, length }))}
                    >
                      {length === 0 ? 'без конца' : length}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Порядок</h3>
                <div className="flex border border-line">
                  {ORDERS.map((entry) => (
                    <button
                      key={entry.id}
                      type="button"
                      title={entry.hint}
                      aria-pressed={settings.order === entry.id}
                      className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${settings.order === entry.id ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                      onClick={() => setSettings((current) => ({ ...current, order: entry.id }))}
                    >
                      {entry.label}
                    </button>
                  ))}
                </div>
                <p className="text-[11px] leading-snug text-faint">{ORDERS.find((entry) => entry.id === settings.order)?.hint}</p>
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <label className="flex cursor-pointer items-baseline gap-2 text-sm text-ink">
                <input type="checkbox" checked={settings.onlyDue} onChange={(event) => setSettings((current) => ({ ...current, onlyDue: event.target.checked }))} />
                <span>только то, чему подошёл срок
                  <span className="text-muted"> — если срок не подошёл ничему, набор берётся целиком</span>
                </span>
              </label>
              <label className="flex cursor-pointer items-baseline gap-2 text-sm text-ink">
                <input type="checkbox" checked={settings.showTimer} onChange={(event) => setSettings((current) => ({ ...current, showTimer: event.target.checked }))} />
                <span>показывать секундомер
                  <span className="text-muted"> — время записывается в любом случае</span>
                </span>
              </label>
            </section>

            <div className="flex flex-wrap items-center gap-4 border-t border-line pt-4">
              <button
                type="button"
                disabled={chosenSkills === 0}
                className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90 disabled:cursor-default disabled:opacity-40"
                onClick={start}
              >
                начать
              </button>
              <span className="font-mono text-[11px] text-muted">
                {chosenSkills > 0
                  ? `${chosen.length} тем, ${chosenSkills} приёмов${settings.length ? `, ${settings.length} заданий` : ''}`
                  : 'в этом режиме выбранные темы пусты'}
              </span>
            </div>
          </>
        )}

        {screen === 'running' && (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3 font-mono text-[11px] text-muted">
                <button type="button" className="cursor-pointer border border-line bg-canvas px-2 py-1 text-[10px] hover:bg-surface" onClick={finish}>закончить</button>
                <span>{done.length}{settings.length ? ` / ${settings.length}` : ''}</span>
              </div>
              {settings.showTimer && (
                <span className={`font-mono text-[11px] ${item && elapsed > item.budget_ms ? 'text-ink' : 'text-muted'}`}>
                  {seconds(elapsed)}{item ? ` / ${seconds(item.budget_ms)}` : ''}
                </span>
              )}
            </div>

            {error && <p className="border border-line bg-surface p-3 text-sm text-ink">Тренажёр не отвечает: {error}</p>}

            {item && (
              <motion.section
                key={item.item}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col gap-4 border border-line bg-canvas p-5"
              >
                <div className="flex items-center gap-2 font-mono text-[10px] text-faint">
                  <span className="border border-line px-1.5 py-0.5">{item.practicum}</span>
                  <span>{item.kind === 'recognition' ? 'назвать приём' : 'решить и ввести ответ'}</span>
                </div>

                <MathText className="text-[15px] leading-relaxed text-ink">{item.prompt}</MathText>
                {item.note && <MathText className="text-xs text-muted">{item.note}</MathText>}

                {item.kind === 'recognition' && item.options
                  ? <div className="grid grid-cols-2 gap-1.5 max-[560px]:grid-cols-1">
                      {item.options.map((option, index) => (
                        <button
                          key={option.code}
                          type="button"
                          disabled={Boolean(verdict) || busy}
                          className="flex cursor-pointer items-baseline gap-2 border border-line bg-canvas px-2.5 py-2 text-left text-sm text-ink hover:bg-surface disabled:cursor-default disabled:opacity-60"
                          onClick={() => { markFirstKey(); void submit(option.code) }}
                        >
                          <span className="font-mono text-[10px] text-faint">{index + 1}</span>
                          <span className="font-mono text-[11px]">{option.code}</span>
                          <span className="text-xs text-muted">{option.name}</span>
                        </button>
                      ))}
                    </div>
                  : <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); void submit(answer) }}>
                      <input
                        ref={inputRef}
                        className="h-9 min-w-0 flex-1 border border-line bg-canvas px-2.5 font-mono text-sm text-ink outline-none focus:border-line-strong"
                        placeholder="например 2sqrt(6) или 1, 4"
                        value={answer}
                        disabled={Boolean(verdict)}
                        onChange={(event) => { markFirstKey(); setAnswer(event.target.value) }}
                      />
                      <button
                        type="submit"
                        disabled={Boolean(verdict) || busy || !answer.trim()}
                        className="h-9 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
                      >
                        ответить
                      </button>
                    </form>}

                {verdict && (
                  <div className="flex flex-col gap-3 border-t border-line pt-3">
                    <MathText className="text-sm text-ink">{verdict.message}</MathText>

                    <dl className="grid grid-cols-[8rem_1fr] items-baseline gap-x-3 gap-y-2.5 border-t border-line pt-3 max-[560px]:grid-cols-1 max-[560px]:gap-y-1">
                      {!verdict.ok && <>
                        <dt className={LABEL}>верный ответ</dt>
                        <dd className="font-mono text-sm text-ink">{verdict.answer}</dd>
                      </>}

                      <dt className={LABEL}>приём</dt>
                      <dd className="text-sm text-ink">
                        {verdict.skill_name}
                        <span className="ml-2 font-mono text-[10px] text-faint">{verdict.practicum}</span>
                      </dd>

                      <dt className={LABEL}>узнаётся по</dt>
                      <dd className="text-xs leading-relaxed text-muted">{verdict.trigger}</dd>

                      {verdict.chain.length > 0 && <>
                        <dt className={LABEL}>ход</dt>
                        <dd>
                          <ol className="flex flex-col gap-0.5 text-xs leading-relaxed text-muted">
                            {verdict.chain.map((step, index) => (
                              <li key={step} className="flex gap-2">
                                <span className="font-mono text-[10px] text-faint">{index + 1}</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ol>
                        </dd>
                      </>}

                      {verdict.traps.length > 0 && <>
                        <dt className={LABEL}>где срезаются</dt>
                        <dd>
                          <ul className="flex flex-col gap-1 text-xs leading-relaxed text-muted">
                            {verdict.traps.map((trap) => (
                              <li key={trap} className="flex gap-2">
                                <span className="text-faint">·</span>
                                <span>{trap}</span>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </>}
                    </dl>

                    <div className="flex items-center gap-3 pt-1">
                      <button
                        type="button"
                        className="h-8 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface"
                        onClick={advance}
                      >
                        {settings.length > 0 && done.length >= settings.length ? 'итог' : 'дальше'}
                      </button>
                      <span className="font-mono text-[10px] text-faint">Enter или пробел</span>
                    </div>
                  </div>
                )}
              </motion.section>
            )}
          </>
        )}

        {screen === 'done' && (
          <section className="flex flex-col gap-5">
            <div className="flex flex-col gap-1">
              <h2 className="text-lg text-ink">
                {summary.total ? `${summary.correct} из ${summary.total}` : 'Ни одного задания'}
              </h2>
              {summary.total > 0 && (
                <p className="font-mono text-[11px] text-muted">
                  {minutes(summary.spent)} всего, {seconds(summary.spent / summary.total)} на задание
                  {summary.avgFirst > 0 ? `, ${seconds(summary.avgFirst)} до первого нажатия в узнавании` : ''}
                </p>
              )}
            </div>

            {summary.weak.length > 0 && (
              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Вернуться к этому</h3>
                <ul className="flex flex-col gap-1">
                  {summary.weak.map((row) => (
                    <li key={row.name} className="flex items-baseline gap-2 text-sm text-ink">
                      <span className="font-mono text-[10px] text-faint">{row.practicum}</span>
                      <span>{row.name}</span>
                      <span className="font-mono text-[10px] text-muted">{row.wrong} из {row.total} мимо</span>
                    </li>
                  ))}
                </ul>
                <p className="text-[11px] text-faint">
                  Эти приёмы вернутся завтра: ошибка сбрасывает срок повторения в начало.
                </p>
              </div>
            )}

            {summary.total > 0 && summary.weak.length === 0 && (
              <p className="text-sm text-muted">Без единой ошибки. Сроки повторения сдвинулись вперёд.</p>
            )}

            <div className="flex flex-wrap gap-3">
              <button type="button" className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90" onClick={start}>ещё раз</button>
              <button type="button" className="h-9 cursor-pointer border border-line bg-canvas px-4 font-mono text-[11px] text-muted hover:bg-surface" onClick={() => setScreen('setup')}>настройки</button>
            </div>
          </section>
        )}

        {stats && screen !== 'running' && (
          <section className="flex flex-col gap-3 border-t border-line pt-4">
            <div className="flex flex-wrap items-baseline gap-x-5 gap-y-1 font-mono text-[11px] text-muted">
              <span>всего попыток {stats.totals.attempts}</span>
              <span>верно {stats.totals.correct}</span>
              <span>сегодня {stats.totals.today_correct}/{stats.totals.today}</span>
              {stats.totals.avg_first_ms > 0 && <span>до первого нажатия {seconds(stats.totals.avg_first_ms)}</span>}
            </div>
            <div className="flex flex-col gap-2">
              {[...new Set(stats.skills.map((skill) => skill.practicum))].map((practicum) => (
                <div key={practicum} className="flex items-center gap-2">
                  <span className="w-7 shrink-0 font-mono text-[10px] text-faint">{practicum}</span>
                  <div className="flex flex-wrap gap-1">
                    {stats.skills.filter((skill) => skill.practicum === practicum).map((skill) => (
                      <span
                        key={skill.id}
                        title={`${skill.name} — показов ${skill.seen}, ошибок ${skill.wrong}${skill.has_compute ? '' : ', только узнавание'}`}
                        className={`border border-line px-1.5 py-0.5 font-mono text-[10px] ${tileTone(skill)}`}
                      >
                        {skill.seen || '·'}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <p className="text-[11px] text-faint">
              Тёмная плитка — приём, где ошибок больше двух из пяти. Светлая с заливкой — подошёл срок повторить. Точка — ни одной попытки.
            </p>
          </section>
        )}
      </div>
    </div>
  )
}
