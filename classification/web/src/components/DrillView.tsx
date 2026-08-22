import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { MathText } from './MathText'

type Mode = 'mixed' | 'recognition' | 'compute'

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
  skill_name: string
  trigger: string
  answer: string
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
  practicums: { id: string; title: string; marks: number | null }[]
  totals: { attempts: number; correct: number; avg_ms: number; avg_first_ms: number; today: number; today_correct: number }
  uncovered: string[]
}

const API = '/api/drill'
const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: 'mixed', label: 'вперемешку', hint: 'Темы идут вразнобой — как на экзамене' },
  { id: 'recognition', label: 'узнавание', hint: 'Только назвать приём, считать не нужно' },
  { id: 'compute', label: 'счёт', hint: 'Только решить и ввести ответ' },
]

function seconds(ms: number) {
  return `${(ms / 1000).toFixed(1)} с`
}

/** Цвет плитки приёма: чем свежее и вернее, тем спокойнее. */
function tileTone(skill: SkillStat) {
  if (!skill.seen) return 'bg-surface text-faint'
  const errorRate = skill.wrong / skill.seen
  if (errorRate > 0.4) return 'bg-ink text-canvas'
  if (skill.due_in_days !== null && skill.due_in_days < 0) return 'bg-primary-soft text-ink'
  return 'bg-canvas text-muted'
}

export function DrillView() {
  const [mode, setMode] = useState<Mode>('mixed')
  const [item, setItem] = useState<Item | null>(null)
  const [verdict, setVerdict] = useState<Verdict | null>(null)
  const [answer, setAnswer] = useState('')
  const [stats, setStats] = useState<Stats | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [streak, setStreak] = useState(0)

  const shownAt = useRef<number>(0)
  const firstKeyAt = useRef<number>(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const recent = useRef<string[]>([])

  const loadStats = useCallback(async () => {
    try {
      const response = await fetch(`${API}/stats`)
      if (response.ok) setStats(await response.json())
    } catch {
      /* статистика не критична */
    }
  }, [])

  const nextItem = useCallback(async (which: Mode) => {
    setBusy(true)
    setVerdict(null)
    setAnswer('')
    setError(null)
    try {
      const avoid = recent.current.slice(-3).join(',')
      const response = await fetch(`${API}/next?mode=${which}&avoid=${encodeURIComponent(avoid)}`)
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      const next: Item = await response.json()
      setItem(next)
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
  }, [])

  useEffect(() => { void nextItem(mode); void loadStats() }, [mode, nextItem, loadStats])

  useEffect(() => {
    if (!item || verdict) return
    const timer = window.setInterval(() => setElapsed(performance.now() - shownAt.current), 100)
    return () => window.clearInterval(timer)
  }, [item, verdict])

  const submit = useCallback(async (raw: string) => {
    if (!item || busy || verdict) return
    const value = raw.trim()
    if (!value) return
    setBusy(true)
    try {
      const response = await fetch(`${API}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          item: item.item,
          answer: value,
          mode,
          ms: Math.round(performance.now() - shownAt.current),
          first_ms: Math.round((firstKeyAt.current || performance.now()) - shownAt.current),
        }),
      })
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      const result: Verdict = await response.json()
      setVerdict(result)
      setStreak((current) => (result.ok ? current + 1 : 0))
      recent.current = [...recent.current, item.skill].slice(-6)
      void loadStats()
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    } finally {
      setBusy(false)
    }
  }, [busy, item, loadStats, mode, verdict])

  const markFirstKey = useCallback(() => {
    if (!firstKeyAt.current) firstKeyAt.current = performance.now()
  }, [])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (verdict) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); void nextItem(mode) }
        return
      }
      if (!item || item.kind !== 'recognition' || !item.options) return
      const index = Number.parseInt(event.key, 10)
      const option = Number.isInteger(index) ? item.options[index - 1] : undefined
      if (option) {
        markFirstKey()
        void submit(option.code)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [item, markFirstKey, mode, nextItem, submit, verdict])

  const budgetTone = useMemo(() => {
    if (!item) return 'text-muted'
    return elapsed > item.budget_ms ? 'text-ink' : 'text-muted'
  }, [elapsed, item])

  const byPracticum = useMemo(() => {
    if (!stats) return []
    const groups = new Map<string, SkillStat[]>()
    for (const skill of stats.skills) {
      const list = groups.get(skill.practicum) ?? []
      list.push(skill)
      groups.set(skill.practicum, list)
    }
    return [...groups.entries()]
  }, [stats])

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">

        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex border border-line">
            {MODES.map((entry) => (
              <button
                key={entry.id}
                type="button"
                title={entry.hint}
                aria-pressed={mode === entry.id}
                className={`h-7 cursor-pointer border-0 border-l border-line px-3 font-mono text-[10px] first:border-l-0 ${mode === entry.id ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                onClick={() => setMode(entry.id)}
              >
                {entry.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4 font-mono text-[11px] text-muted">
            {streak > 1 && <span>подряд {streak}</span>}
            {stats && <span>сегодня {stats.totals.today_correct}/{stats.totals.today}</span>}
            <span className={budgetTone}>{seconds(elapsed)}{item ? ` / ${seconds(item.budget_ms)}` : ''}</span>
          </div>
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
              : <form
                  className="flex gap-2"
                  onSubmit={(event) => { event.preventDefault(); void submit(answer) }}
                >
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
              <div className="flex flex-col gap-2 border-t border-line pt-3">
                <MathText className={`text-sm ${verdict.ok ? 'text-ink' : 'text-ink'}`}>{verdict.message}</MathText>
                {!verdict.ok && <p className="font-mono text-xs text-muted">верно: {verdict.answer}</p>}
                <p className="text-xs text-muted">
                  <span className="text-ink">{verdict.skill_name}</span>
                  {verdict.trigger ? ` — ${verdict.trigger}` : ''}
                </p>
                <div className="flex items-center gap-3 pt-1">
                  <button
                    type="button"
                    className="h-8 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface"
                    onClick={() => void nextItem(mode)}
                  >
                    дальше
                  </button>
                  <span className="font-mono text-[10px] text-faint">Enter или пробел</span>
                </div>
              </div>
            )}
          </motion.section>
        )}

        {stats && (
          <section className="flex flex-col gap-3">
            <div className="flex flex-wrap items-baseline gap-x-5 gap-y-1 font-mono text-[11px] text-muted">
              <span>попыток {stats.totals.attempts}</span>
              <span>верно {stats.totals.correct}</span>
              {stats.totals.avg_first_ms > 0 && <span>до первого нажатия {seconds(stats.totals.avg_first_ms)}</span>}
              {stats.totals.avg_ms > 0 && <span>до ответа {seconds(stats.totals.avg_ms)}</span>}
            </div>
            <div className="flex flex-col gap-2">
              {byPracticum.map(([practicum, skills]) => (
                <div key={practicum} className="flex items-center gap-2">
                  <span className="w-7 shrink-0 font-mono text-[10px] text-faint">{practicum}</span>
                  <div className="flex flex-wrap gap-1">
                    {skills.map((skill) => (
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
              Тёмная плитка — приём, где ошибок больше двух из пяти. Светлая с заливкой — подошёл срок повторить.
              Точка — ни одной попытки.
            </p>
          </section>
        )}
      </div>
    </div>
  )
}
