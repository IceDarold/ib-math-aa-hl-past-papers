import { useCallback, useEffect, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { WriteUpVerdict, type Verdict } from './WriteUpVerdict'

const API = '/api/drill'
const MINUTES = [20, 40, 60]

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
  state: 'open' | 'graded'
  scanned_at: number | null
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

function when(ts: number) {
  return new Date(ts * 1000).toLocaleDateString('ru-RU',
    { day: 'numeric', month: 'long' })
}

export function EveningView({ evening, onOpen, onChange, onClose, busy, setBusy }: {
  evening: Evening | null
  onOpen: (minutes: number) => Promise<void>
  onChange: (evening: Evening) => void
  onClose: () => void
  busy: boolean
  setBusy: (busy: boolean) => void
}) {
  const [minutes, setMinutes] = useState(40)
  const [error, setError] = useState<string | null>(null)
  const [guessed, setGuessed] = useState(false)
  const [gradingMs, setGradingMs] = useState(0)
  const [opened, setOpened] = useState<number | null>(null)
  const picker = useRef<HTMLInputElement>(null)

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
        <div className="flex flex-wrap items-center gap-2">
          {MINUTES.map((value) => (
            <button
              key={value}
              type="button"
              className={`cursor-pointer border px-3 py-1.5 font-mono text-[11px] ${
                minutes === value ? 'border-ink bg-ink text-canvas'
                  : 'border-line bg-canvas text-muted hover:border-line-strong'}`}
              onClick={() => setMinutes(value)}
            >
              {value} минут
            </button>
          ))}
          <button
            type="button"
            disabled={busy}
            className="ml-2 cursor-pointer border border-ink bg-canvas px-4 py-1.5 text-sm text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
            onClick={() => void onOpen(minutes)}
          >
            {busy ? 'собираю…' : 'собрать вечер'}
          </button>
        </div>
        <p className="text-[11px] text-faint">
          На экзамене примерно минута на балл, так что сорок минут — это сорок
          баллов. Сколько это вопросов, решает набор.
        </p>
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
            {when(evening.ts)} · {evening.questions.length} заданий · {total} баллов
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
        </div>
      )}

      {/* --- подтверждение раскладки ------------------------------------ */}
      {evening.state !== 'graded' && evening.pages.length > 0 && (
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
              onClick={() => { setOpened(null); void onOpen(minutes) }}
            >
              {busy ? 'собираю…' : 'собрать новый вечер'}
            </button>
            {MINUTES.map((value) => (
              <button
                key={value}
                type="button"
                className={`cursor-pointer border px-3 py-1.5 font-mono text-[11px] ${
                  minutes === value ? 'border-ink bg-ink text-canvas'
                    : 'border-line bg-canvas text-muted hover:border-line-strong'}`}
                onClick={() => setMinutes(value)}
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
