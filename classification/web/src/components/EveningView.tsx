import { useCallback, useEffect, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { WriteUpVerdict, type Verdict } from './WriteUpVerdict'

const API = '/api/drill'
const MINUTES = [20, 40, 60]
const PAPERS: { id: number; hint: string }[] = [
  { id: 1, hint: 'без калькулятора' },
  { id: 2, hint: 'с калькулятором' },
  { id: 3, hint: 'длинные исследования' },
]
const STORE = 'drill.evening.settings'

export interface EveningTheme {
  id: string
  title: string
  written: number
  skills: number
  started: number
}

interface Choice {
  minutes: number
  practicums: string[]
  papers: number[]
  onlyDue: boolean
}

/** Что выбрано в прошлый раз. Собирать отбор каждый вечер заново незачем. */
function loadChoice(themes: EveningTheme[]): Choice {
  const started = themes.filter((theme) => theme.started > 0).map((t) => t.id)
  // По умолчанию — темы, которые уже начинали. Вопрос на бумаге по приёму,
  // которого ещё не разбирали, это не проверка, а потерянные полчаса.
  const fallback: Choice = {
    minutes: 40,
    practicums: started.length ? started : themes.map((theme) => theme.id),
    papers: [],
    onlyDue: false,
  }
  try {
    const saved = window.localStorage.getItem(STORE)
    if (!saved) return fallback
    const parsed = JSON.parse(saved) as Partial<Choice>
    const known = new Set(themes.map((theme) => theme.id))
    const picked = (parsed.practicums ?? []).filter((id) => known.has(id))
    return {
      minutes: Number(parsed.minutes) || fallback.minutes,
      practicums: picked.length ? picked : fallback.practicums,
      papers: (parsed.papers ?? []).filter((id) => [1, 2, 3].includes(id)),
      onlyDue: Boolean(parsed.onlyDue),
    }
  } catch {
    return fallback
  }
}

function saveChoice(choice: Choice) {
  try {
    window.localStorage.setItem(STORE, JSON.stringify(choice))
  } catch { /* приватное окно — переживём */ }
}

export interface EveningQuestion {
  n: number
  block: string
  skill: string
  skill_name: string
  practicum: string
  marks: number
  paper: number | null
  calculator: string | null
  reference: string
}

interface EveningPage {
  index: number
  file: string
  question: number
}

export interface EveningResult {
  n: number
  block: string
  skill: string
  skill_name: string
  practicum: string
  reference: string
  available: number | null
  earned: number | null
  pages: number
  skipped?: boolean
  error?: string
  message?: string
  mark?: string
  verdict?: Verdict
  strength?: { score: number | null; stability: number | null; due_in_days: number | null }
}

export interface Evening {
  id: string
  ts: number
  minutes: number
  marks: number
  state: 'draft' | 'open' | 'graded'
  scanned_at: number | null
  started_at: number | null
  questions: EveningQuestion[]
  pages: EveningPage[]
  results: EveningResult[]
}

const CALCULATOR: Record<string, string> = { yes: 'можно', no: 'нельзя' }

/** Файл → data-URL: сервер разбирает и снимки, и один PDF на весь вечер. */
function readFile(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error(`не прочитался файл ${file.name}`))
    reader.readAsDataURL(file)
  })
}

function clock(ts: number) {
  return new Date(ts * 1000).toLocaleTimeString('ru-RU',
    { hour: '2-digit', minute: '2-digit' })
}

function when(ts: number) {
  return new Date(ts * 1000).toLocaleDateString('ru-RU',
    { day: 'numeric', month: 'long' })
}

export function EveningView({ evening, themes, onOpen, onChange, onDrop, onClose, busy, setBusy }: {
  evening: Evening | null
  themes: EveningTheme[]
  onOpen: (choice: { minutes: number; practicums: string[]; papers: number[]; only_due: boolean }) => Promise<void>
  onChange: (evening: Evening) => void
  onDrop: (id: string) => Promise<void>
  onClose: () => void
  busy: boolean
  setBusy: (busy: boolean) => void
}) {
  const [choice, setChoice] = useState<Choice>(() => loadChoice(themes))
  const [error, setError] = useState<string | null>(null)
  const [guessed, setGuessed] = useState(false)
  const [gradingMs, setGradingMs] = useState(0)
  const [opened, setOpened] = useState<number | null>(null)
  const picker = useRef<HTMLInputElement>(null)

  useEffect(() => { saveChoice(choice) }, [choice])

  const collect = useCallback(() => onOpen({
    minutes: choice.minutes,
    // Выбраны все темы — не передаём ничего: пусть отбора и не будет.
    practicums: choice.practicums.length === themes.length ? [] : choice.practicums,
    papers: choice.papers,
    only_due: choice.onlyDue,
  }), [choice, onOpen, themes.length])

  const toggle = useCallback(<T,>(list: T[], value: T) => (
    list.includes(value) ? list.filter((item) => item !== value) : [...list, value]
  ), [])

  // Разбор восьми заданий идёт минуту-полторы. Без часов это выглядит
  // зависшим, и работу присылают второй раз.
  useEffect(() => {
    if (!busy || !evening?.pages?.length || evening.state === 'graded') return
    const started = Date.now()
    const timer = window.setInterval(() => setGradingMs(Date.now() - started), 200)
    return () => window.clearInterval(timer)
  }, [busy, evening?.pages?.length, evening?.state])

  const send = useCallback(async (files: FileList | null) => {
    if (!files?.length || !evening) return
    setError(null)
    setBusy(true)
    try {
      const photos = await Promise.all(Array.from(files).map(readFile))
      const response = await fetch(`${API}/evening/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: evening.id, photos }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? 'страницы не приняты')
      setGuessed(Boolean(payload.guessed))
      onChange({ ...evening, pages: payload.pages })
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : 'не отправилось')
    } finally {
      setBusy(false)
    }
  }, [evening, onChange, setBusy])

  const retag = useCallback((index: number, question: number) => {
    if (!evening) return
    onChange({
      ...evening,
      pages: evening.pages.map((page) => (page.index === index
        ? { ...page, question } : page)),
    })
  }, [evening, onChange])

  const start = useCallback(async () => {
    if (!evening) return
    setError(null)
    setBusy(true)
    try {
      const response = await fetch(`${API}/evening/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: evening.id }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? 'вечер не начался')
      onChange(payload)
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : 'не начался')
    } finally {
      setBusy(false)
    }
  }, [evening, onChange, setBusy])

  const grade = useCallback(async () => {
    if (!evening) return
    setError(null)
    setBusy(true)
    try {
      const response = await fetch(`${API}/evening/grade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          id: evening.id,
          assignment: evening.pages.map((page) => page.question),
        }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? 'разбор не сработал')
      onChange(payload)
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : 'не разобралось')
    } finally {
      setBusy(false)
    }
  }, [evening, onChange, setBusy])

  // --- вечер ещё не собран -------------------------------------------
  if (!evening) {
    return (
      <section className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <h2 className="text-lg text-ink">Вечер</h2>
          <p className="max-w-[42rem] text-sm text-muted">
            Одна кнопка собирает лист настоящих вопросов архива — по приёмам,
            которые просели сильнее прочих. Решаешь на бумаге, присылаешь одним
            сканом, разбор приходит на всё сразу.
          </p>
        </div>
        <section className="flex flex-col gap-2">
          <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Сколько</h3>
          <div className="flex flex-wrap items-center gap-2">
            {MINUTES.map((value) => (
              <button
                key={value}
                type="button"
                aria-pressed={choice.minutes === value}
                className={`cursor-pointer border px-3 py-1.5 font-mono text-[11px] ${
                  choice.minutes === value ? 'border-ink bg-ink text-canvas'
                    : 'border-line bg-canvas text-muted hover:border-line-strong'}`}
                onClick={() => setChoice((c) => ({ ...c, minutes: value }))}
              >
                {value} минут
              </button>
            ))}
            <span className="font-mono text-[10px] text-faint">
              примерно минута на балл
            </span>
          </div>
        </section>

        <section className="flex flex-col gap-2">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Темы</h3>
            <div className="flex gap-3 font-mono text-[10px] text-muted">
              <button type="button" className="cursor-pointer border-0 bg-transparent underline hover:text-ink"
                onClick={() => setChoice((c) => ({ ...c, practicums: themes.map((t) => t.id) }))}>
                все
              </button>
              <button type="button" className="cursor-pointer border-0 bg-transparent underline hover:text-ink"
                onClick={() => setChoice((c) => {
                  const started = themes.filter((t) => t.started > 0).map((t) => t.id)
                  return { ...c, practicums: started.length ? started : themes.map((t) => t.id) }
                })}>
                начатые
              </button>
            </div>
          </div>
          <div className="grid grid-cols-4 gap-1.5 max-[720px]:grid-cols-2">
            {themes.map((theme) => {
              const on = choice.practicums.includes(theme.id)
              return (
                <button
                  key={theme.id}
                  type="button"
                  aria-pressed={on}
                  disabled={!theme.written}
                  title={theme.title}
                  className={`flex cursor-pointer flex-col gap-0.5 border p-2 text-left disabled:cursor-default disabled:opacity-30 ${
                    on ? 'border-line-strong bg-surface'
                      : 'border-dashed border-line bg-canvas opacity-45 hover:opacity-70'}`}
                  onClick={() => setChoice((c) => ({
                    ...c, practicums: toggle(c.practicums, theme.id),
                  }))}
                >
                  <span className="flex items-baseline gap-1.5">
                    <span className="font-mono text-[11px] text-ink">{theme.id}</span>
                    <span className="truncate text-[11px] text-muted">{theme.title}</span>
                  </span>
                  <span className="font-mono text-[10px] text-faint">
                    {theme.written} вопросов · {theme.started
                      ? `начато ${theme.started} из ${theme.skills}`
                      : 'не начинали'}
                  </span>
                </button>
              )
            })}
          </div>
          <p className="text-[11px] text-faint">
            По умолчанию — темы, которые уже начинали. Вопрос на бумаге по приёму,
            которого ещё не разбирали, это не проверка, а потерянные полчаса.
          </p>
        </section>

        <section className="flex flex-col gap-2">
          <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Бумага</h3>
          <div className="flex flex-wrap items-center gap-2">
            {PAPERS.map((paper) => {
              const on = choice.papers.includes(paper.id)
              return (
                <button
                  key={paper.id}
                  type="button"
                  aria-pressed={on}
                  className={`cursor-pointer border px-3 py-1.5 font-mono text-[11px] ${
                    on ? 'border-ink bg-ink text-canvas'
                      : 'border-line bg-canvas text-muted hover:border-line-strong'}`}
                  onClick={() => setChoice((c) => ({ ...c, papers: toggle(c.papers, paper.id) }))}
                >
                  P{paper.id} · {paper.hint}
                </button>
              )
            })}
            {choice.papers.length > 0 && (
              <button type="button"
                className="cursor-pointer border-0 bg-transparent font-mono text-[10px] text-muted underline hover:text-ink"
                onClick={() => setChoice((c) => ({ ...c, papers: [] }))}>
                любая
              </button>
            )}
          </div>
        </section>

        <label className="flex w-fit cursor-pointer items-center gap-2 text-sm text-muted">
          <input
            type="checkbox"
            checked={choice.onlyDue}
            onChange={(event) => setChoice((c) => ({ ...c, onlyDue: event.target.checked }))}
          />
          только то, чему подошёл срок
        </label>

        <div className="flex flex-wrap items-center gap-3 border-t border-line pt-4">
          <button
            type="button"
            disabled={busy || !choice.practicums.length}
            className="cursor-pointer border border-ink bg-canvas px-4 py-1.5 text-sm text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
            onClick={() => void collect()}
          >
            {busy ? 'собираю…' : 'собрать вечер'}
          </button>
          <span className="font-mono text-[10px] text-faint">
            {choice.practicums.length
              ? `${choice.practicums.length} тем · ${themes
                  .filter((theme) => choice.practicums.includes(theme.id))
                  .reduce((sum, theme) => sum + theme.written, 0)} вопросов под отбором`
              : 'выберите хотя бы одну тему'}
          </span>
        </div>
      </section>
    )
  }

  const total = evening.questions.reduce((sum, q) => sum + (q.marks || 0), 0)
  const earned = evening.results.reduce((sum, row) => sum + (row.earned ?? 0), 0)
  const marked = evening.results.filter((row) => !row.skipped && !row.error)
  const scored = marked.reduce((sum, row) => sum + (row.available ?? 0), 0)

  return (
    <section className="flex flex-col gap-5">
      <div className="flex flex-wrap items-baseline justify-between gap-3 border-b border-line pb-3">
        <div className="flex flex-wrap items-baseline gap-x-3">
          <h2 className="text-lg text-ink">Вечер</h2>
          <span className="font-mono text-[11px] text-faint">
            {evening.state === 'draft' ? 'черновик' : when(evening.ts)}
            {' · '}{evening.questions.length} заданий · {total} баллов
            {evening.state === 'open' && evening.started_at
              && ` · начат в ${clock(evening.started_at)}`}
            {evening.state === 'graded' && scored > 0 && ` · набрано ${earned} из ${scored}`}
          </span>
        </div>
        <button
          type="button"
          className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
          onClick={onClose}
        >
          к настройкам
        </button>
      </div>

      {error && <p className="border-l-2 border-primary pl-2 text-sm text-primary">{error}</p>}

      {/* --- задания --------------------------------------------------- */}
      {evening.state !== 'graded' && (
        <div className="flex flex-col gap-3">
          <div className="flex flex-col">
            {evening.questions.map((question) => (
              <div key={question.n} className="flex flex-wrap items-baseline gap-x-3 border-b border-line py-1.5">
                <span className="w-5 shrink-0 font-mono text-[11px] text-faint">{question.n}</span>
                <span className="text-sm text-ink">{question.reference}</span>
                <span className="font-mono text-[10px] text-faint">
                  {question.marks} б. · калькулятор {CALCULATOR[question.calculator ?? ''] ?? '—'}
                </span>
                <span className="ml-auto font-mono text-[10px] text-faint">{question.skill_name}</span>
              </div>
            ))}
          </div>

          {evening.state === 'draft' ? (
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                disabled={busy}
                className="cursor-pointer border border-ink bg-ink px-5 py-1.5 text-sm text-canvas hover:bg-ink/90 disabled:cursor-default disabled:opacity-50"
                onClick={() => void start()}
              >
                {busy ? 'начинаю…' : 'старт'}
              </button>
              <button
                type="button"
                disabled={busy}
                className="cursor-pointer border border-line bg-canvas px-4 py-1.5 text-sm text-muted hover:border-line-strong disabled:cursor-default disabled:opacity-50"
                onClick={() => void onDrop(evening.id)}
              >
                назад к отбору
              </button>
              <span className="max-w-[26rem] font-mono text-[10px] text-faint">
                Пока это черновик: его можно пересобрать, и в счёт он не идёт.
                Со «старта» вечер начинается — и лист, и приём работы.
              </span>
            </div>
          ) : (
            <div className="flex flex-wrap items-center gap-2">
              <a
                href={`${API}/evening/sheet?id=${evening.id}`}
                target="_blank"
                rel="noreferrer"
                className="border border-ink bg-canvas px-4 py-1.5 text-sm text-ink no-underline hover:bg-surface"
              >
                открыть лист заданий
              </a>
              <input
                ref={picker}
                type="file"
                accept="image/*,application/pdf"
                multiple
                className="hidden"
                onChange={(event) => void send(event.target.files)}
              />
              <button
                type="button"
                disabled={busy}
                className="cursor-pointer border border-line bg-canvas px-4 py-1.5 text-sm text-muted hover:border-line-strong disabled:cursor-default disabled:opacity-50"
                onClick={() => picker.current?.click()}
              >
                {busy && !evening.pages.length ? 'принимаю…' : 'прислать работу'}
              </button>
              <span className="font-mono text-[10px] text-faint">
                один скан или пачка фото · набор {evening.id}
              </span>
            </div>
          )}
        </div>
      )}

      {/* --- подтверждение раскладки ------------------------------------ */}
      {evening.state === 'open' && evening.pages.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }}
          className="flex flex-col gap-3 border-t border-line pt-4">
          <div className="flex flex-col gap-1">
            <h3 className="text-sm text-ink">Чьи это страницы</h3>
            <p className="text-[11px] text-faint">
              {guessed
                ? 'Номера прочитать не удалось — страницы разложены по порядку. Проверь и поправь.'
                : 'Номер прочитан в углу каждой страницы. Проверь одним взглядом и поправь, если что-то уехало.'}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            {evening.pages.map((page) => (
              <div key={page.index} className="flex w-28 flex-col gap-1">
                <img
                  src={`${API}/evening/page?id=${evening.id}&n=${page.index}`}
                  alt={`страница ${page.index + 1}`}
                  className="h-32 w-28 border border-line object-cover object-top"
                />
                <select
                  value={page.question}
                  onChange={(event) => retag(page.index, Number(event.target.value))}
                  className="border border-line bg-canvas px-1 py-0.5 font-mono text-[10px] text-ink"
                >
                  {evening.questions.map((question) => (
                    <option key={question.n} value={question.n}>
                      № {question.n} · {question.marks} б.
                    </option>
                  ))}
                </select>
              </div>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              disabled={busy}
              className="cursor-pointer border border-ink bg-ink px-4 py-1.5 text-sm text-canvas hover:bg-ink/90 disabled:cursor-default disabled:opacity-50"
              onClick={() => void grade()}
            >
              {busy ? `разбираю… ${(gradingMs / 1000).toFixed(0)} с` : 'разобрать вечер'}
            </button>
            <button
              type="button"
              disabled={busy}
              className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink disabled:opacity-50"
              onClick={() => picker.current?.click()}
            >
              прислать другие страницы
            </button>
          </div>
        </motion.div>
      )}

      {/* --- результаты -------------------------------------------------- */}
      {evening.state === 'graded' && (
        <div className="flex flex-col gap-5">
          <div className="flex flex-col">
            {evening.results.map((row) => (
              <button
                key={row.n}
                type="button"
                disabled={!row.verdict}
                aria-expanded={opened === row.n}
                className={`flex items-baseline gap-x-3 border-b border-line py-1.5 text-left ${
                  row.verdict ? 'cursor-pointer hover:bg-surface' : 'cursor-default'} ${
                  opened === row.n ? 'bg-surface' : ''}`}
                onClick={() => setOpened(opened === row.n ? null : row.n)}
              >
                <span className="w-5 shrink-0 font-mono text-[11px] text-faint">{row.n}</span>
                <span className="shrink-0 text-sm text-ink">{row.reference}</span>
                <span className="truncate font-mono text-[10px] text-faint">{row.skill_name}</span>
                <span className="ml-auto w-16 shrink-0 text-right font-mono text-[11px] tabular-nums text-ink">
                  {row.skipped ? '—' : row.error ? 'сбой'
                    : `${row.earned ?? 0} / ${row.available ?? 0}`}
                </span>
                <span className="w-16 shrink-0 text-right font-mono text-[10px] text-faint">
                  {row.strength?.score === undefined || row.strength?.score === null
                    ? '' : `сила ${row.strength.score}`}
                </span>
              </button>
            ))}
          </div>

          {opened === null && evening.results.some((row) => row.verdict) && (
            <p className="text-[11px] text-faint">
              Нажмите на строку, чтобы открыть разбор: что прочитано, где потерян
              балл и как это записывают в схеме оценивания.
            </p>
          )}

          {evening.results.map((row) => (row.verdict && opened === row.n ? (
            <motion.div key={row.n} initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-2 border-t border-line pt-4">
              <span className="font-mono text-[10px] uppercase tracking-wide text-faint">
                задание {row.n}
              </span>
              <WriteUpVerdict verdict={row.verdict} />
            </motion.div>
          ) : null))}

          {evening.results.some((row) => row.skipped || row.error) && (
            <p className="text-[11px] text-faint">
              {evening.results.filter((row) => row.skipped).length > 0 && (
                `Без страниц осталось заданий: ${evening.results.filter((row) => row.skipped).length}. `
              )}
              Нерешённое силу приёма не роняет — это решение не решать, а не промах.
            </p>
          )}

          <div className="flex flex-wrap items-center gap-2 border-t border-line pt-4">
            <button
              type="button"
              disabled={busy}
              className="cursor-pointer border border-ink bg-canvas px-4 py-1.5 text-sm text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
              onClick={() => { setOpened(null); void collect() }}
            >
              {busy ? 'собираю…' : 'собрать новый вечер'}
            </button>
            {MINUTES.map((value) => (
              <button
                key={value}
                type="button"
                className={`cursor-pointer border px-3 py-1.5 font-mono text-[11px] ${
                  choice.minutes === value ? 'border-ink bg-ink text-canvas'
                    : 'border-line bg-canvas text-muted hover:border-line-strong'}`}
                onClick={() => setChoice((c) => ({ ...c, minutes: value }))}
              >
                {value} минут
              </button>
            ))}
            <button
              type="button"
              className="ml-auto cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
              onClick={onClose}
            >
              к настройкам
            </button>
          </div>
        </div>
      )}
    </section>
  )
}
