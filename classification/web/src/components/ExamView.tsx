import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'motion/react'

interface Question {
  block: string
  reference: string
  skill: string
  skill_name: string
  practicum: string
  marks: number | null
  calculator: string | null
  paper: number | null
  session: string | null
  question_url: string
  markscheme_url: string
}

interface RubricResult {
  id: string
  met: boolean
  code: string
  comment: string
  fix: string
}

interface Verdict {
  transcription: string
  legible: boolean
  mathematics: {
    verdict: string
    errors: { line: string; problem: string; consequence: string }[]
  }
  presentation: RubricResult[]
  marks: { available: number | null; earned: number; lost: { code: string; why: string }[] }
  model_write_up: string
  one_thing: string
  reference: string | null
  skill_name: string | null
  model: string
}

interface HistoryRow {
  id: number
  ts: number
  reference: string
  skill: string
  practicum: string
  available: number | null
  earned: number | null
  math: string
}

const API = '/api/drill'
const LABEL = 'font-mono text-[10px] uppercase tracking-wide text-faint'
const MAX_EDGE = 1600
const MAX_PHOTOS = 6

/** Photos come off a phone at several megabytes; the model needs far less. */
function shrink(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('could not read the file'))
    reader.onload = () => {
      const image = new Image()
      image.onerror = () => reject(new Error('could not decode the image'))
      image.onload = () => {
        const scale = Math.min(1, MAX_EDGE / Math.max(image.width, image.height))
        const canvas = document.createElement('canvas')
        canvas.width = Math.round(image.width * scale)
        canvas.height = Math.round(image.height * scale)
        const context = canvas.getContext('2d')
        if (!context) { reject(new Error('canvas unavailable')); return }
        context.drawImage(image, 0, 0, canvas.width, canvas.height)
        resolve(canvas.toDataURL('image/jpeg', 0.85))
      }
      image.src = String(reader.result)
    }
    reader.readAsDataURL(file)
  })
}

function markTone(code: string) {
  return code === 'R1' ? 'bg-ink text-canvas' : 'bg-surface text-muted'
}

export function ExamView() {
  const [questions, setQuestions] = useState<Question[] | null>(null)
  const [practicum, setPracticum] = useState<string>('A7')
  const [chosen, setChosen] = useState<Question | null>(null)
  const [photos, setPhotos] = useState<string[]>([])
  const [verdict, setVerdict] = useState<Verdict | null>(null)
  const [history, setHistory] = useState<HistoryRow[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showWork, setShowWork] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadHistory = useCallback(async () => {
    try {
      const response = await fetch(`${API}/written`)
      if (response.ok) setHistory((await response.json()).history ?? [])
    } catch { /* history is not critical */ }
  }, [])

  useEffect(() => {
    void (async () => {
      try {
        const response = await fetch(`${API}/questions`)
        if (!response.ok) throw new Error(`server said ${response.status}`)
        setQuestions((await response.json()).questions ?? [])
      } catch (failure) {
        setError(failure instanceof Error ? failure.message : 'not responding')
      }
    })()
    void loadHistory()
  }, [loadHistory])

  const practicums = useMemo(
    () => [...new Set((questions ?? []).map((entry) => entry.practicum))].sort(),
    [questions],
  )
  const shown = useMemo(
    () => (questions ?? []).filter((entry) => entry.practicum === practicum),
    [practicum, questions],
  )

  const addPhotos = async (files: FileList | null) => {
    if (!files?.length) return
    setError(null)
    try {
      const added = await Promise.all([...files].slice(0, MAX_PHOTOS).map(shrink))
      setPhotos((current) => [...current, ...added].slice(0, MAX_PHOTOS))
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'could not read the photo')
    }
  }

  const submit = async () => {
    if (!chosen || !photos.length || busy) return
    setBusy(true)
    setError(null)
    setVerdict(null)
    try {
      const response = await fetch(`${API}/grade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ block: chosen.block, photos }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? `server said ${response.status}`)
      setVerdict(payload as Verdict)
      void loadHistory()
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'not responding')
    } finally {
      setBusy(false)
    }
  }

  const reset = () => {
    setVerdict(null)
    setPhotos([])
    setShowWork(false)
    if (fileRef.current) fileRef.current.value = ''
  }

  const earnedRate = useMemo(() => {
    const rows = history.filter((row) => row.available)
    if (!rows.length) return null
    const available = rows.reduce((sum, row) => sum + (row.available ?? 0), 0)
    const earned = rows.reduce((sum, row) => sum + (row.earned ?? 0), 0)
    return { available, earned, share: available ? earned / available : 0 }
  }, [history])

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">

        <div className="flex flex-col gap-1">
          <h2 className="text-lg text-ink">Exam write-up</h2>
          <p className="text-sm text-muted">
            Solve a real past-paper question on paper, in English, then photograph it.
            You are marked twice: once on the mathematics, once on the way it is written.
          </p>
        </div>

        {error && <p className="border border-line bg-surface p-3 text-sm text-ink">{error}</p>}

        {!verdict && <>
          <section className="flex flex-col gap-2">
            <h3 className={LABEL}>Topic</h3>
            <div className="flex flex-wrap gap-1.5">
              {practicums.map((entry) => (
                <button
                  key={entry}
                  type="button"
                  aria-pressed={practicum === entry}
                  className={`cursor-pointer border px-2 py-1 font-mono text-[11px] ${practicum === entry ? 'border-line-strong bg-ink text-canvas' : 'border-line bg-canvas text-muted hover:bg-surface'}`}
                  onClick={() => { setPracticum(entry); setChosen(null) }}
                >
                  {entry}
                </button>
              ))}
            </div>
          </section>

          <section className="flex flex-col gap-2">
            <h3 className={LABEL}>Question — {shown.length} in this topic</h3>
            <div className="flex max-h-72 flex-col gap-1 overflow-y-auto border border-line p-1">
              {shown.map((entry) => (
                <button
                  key={entry.block}
                  type="button"
                  aria-pressed={chosen?.block === entry.block}
                  className={`flex flex-wrap items-baseline gap-x-2 gap-y-0.5 border px-2 py-1.5 text-left ${chosen?.block === entry.block ? 'border-line-strong bg-surface' : 'border-transparent hover:bg-surface'}`}
                  onClick={() => { setChosen(entry); reset() }}
                >
                  <span className="text-sm text-ink">{entry.reference}</span>
                  <span className="font-mono text-[10px] text-faint">
                    {entry.marks ?? '?'} marks · {entry.calculator === 'yes' ? 'GDC' : 'no GDC'}
                  </span>
                  <span className="w-full text-[11px] text-muted">{entry.skill_name}</span>
                </button>
              ))}
            </div>
          </section>

          {chosen && (
            <motion.section
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col gap-3 border border-line p-4"
            >
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <span className="text-sm text-ink">{chosen.reference}</span>
                <a
                  className="font-mono text-[11px] text-muted underline hover:text-ink"
                  href={chosen.question_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  open the question paper
                </a>
              </div>
              <p className="text-[11px] text-faint">
                The markscheme stays closed until you have been marked.
              </p>

              <div className="flex flex-wrap items-center gap-3">
                <input
                  ref={fileRef}
                  type="file"
                  accept="image/*"
                  capture="environment"
                  multiple
                  className="text-xs text-muted file:mr-2 file:cursor-pointer file:border file:border-line file:bg-canvas file:px-2 file:py-1 file:font-mono file:text-[11px] file:text-ink hover:file:bg-surface"
                  onChange={(event) => void addPhotos(event.target.files)}
                />
                {photos.length > 0 && (
                  <span className="font-mono text-[11px] text-muted">
                    {photos.length} page{photos.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>

              {photos.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {photos.map((photo, index) => (
                    <img
                      key={photo.slice(-32)}
                      src={photo}
                      alt={`page ${index + 1}`}
                      className="h-24 w-auto border border-line object-cover"
                    />
                  ))}
                </div>
              )}

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  disabled={!photos.length || busy}
                  className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90 disabled:cursor-default disabled:opacity-40"
                  onClick={() => void submit()}
                >
                  {busy ? 'marking…' : 'mark my work'}
                </button>
                {busy && <span className="font-mono text-[11px] text-muted">reading the page and the markscheme, ~20 s</span>}
                {photos.length > 0 && !busy && (
                  <button type="button" className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted hover:text-ink" onClick={reset}>
                    clear
                  </button>
                )}
              </div>
            </motion.section>
          )}
        </>}

        {verdict && (
          <motion.section initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-5">
            <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line pb-3">
              <span className="text-sm text-ink">{verdict.reference}</span>
              <span className="font-mono text-[11px] text-muted">
                {verdict.marks.earned} / {verdict.marks.available ?? '?'} marks
              </span>
            </div>

            <dl className="grid grid-cols-[8rem_1fr] items-baseline gap-x-3 gap-y-3 max-[560px]:grid-cols-1">
              <dt className={LABEL}>mathematics</dt>
              <dd className="flex flex-col gap-1.5">
                <span className="text-sm text-ink">{verdict.mathematics.verdict}</span>
                {verdict.mathematics.errors?.map((item) => (
                  <div key={item.line} className="border-l-2 border-line pl-2 text-xs leading-relaxed text-muted">
                    <span className="font-mono text-[11px] text-ink">{item.line}</span>
                    <span className="block">{item.problem}</span>
                    <span className="block text-faint">{item.consequence}</span>
                  </div>
                ))}
              </dd>

              <dt className={LABEL}>presentation</dt>
              <dd className="flex flex-col gap-1.5">
                {verdict.presentation?.map((item) => (
                  <div key={item.id} className="flex gap-2 text-xs leading-relaxed">
                    <span className={`h-fit px-1 py-0.5 font-mono text-[10px] ${item.met ? 'bg-surface text-faint' : markTone(item.code)}`}>
                      {item.code}
                    </span>
                    <span className={item.met ? 'text-faint' : 'text-muted'}>
                      {item.met ? <s>{item.comment}</s> : <>
                        {item.comment}
                        <span className="mt-0.5 block text-ink">→ {item.fix}</span>
                      </>}
                    </span>
                  </div>
                ))}
              </dd>

              {verdict.marks.lost?.length > 0 && <>
                <dt className={LABEL}>marks lost</dt>
                <dd className="flex flex-col gap-1 text-xs text-muted">
                  {verdict.marks.lost.map((item) => (
                    <div key={item.why} className="flex gap-2">
                      <span className="font-mono text-[10px] text-ink">{item.code}</span>
                      <span>{item.why}</span>
                    </div>
                  ))}
                </dd>
              </>}

              <dt className={LABEL}>one thing</dt>
              <dd className="text-sm text-ink">{verdict.one_thing}</dd>

              <dt className={LABEL}>model write-up</dt>
              <dd className="whitespace-pre-wrap border border-line bg-surface p-3 text-xs leading-relaxed text-ink">
                {verdict.model_write_up}
              </dd>

              <dt className={LABEL}>what it read</dt>
              <dd>
                <button type="button" className="cursor-pointer border-0 bg-transparent p-0 font-mono text-[11px] text-muted underline hover:text-ink" onClick={() => setShowWork((value) => !value)}>
                  {showWork ? 'hide' : 'show'} the transcription
                </button>
                {showWork && (
                  <pre className="mt-2 whitespace-pre-wrap border border-line p-2 text-[11px] leading-relaxed text-muted">{verdict.transcription}</pre>
                )}
              </dd>
            </dl>

            <div className="flex flex-wrap items-center gap-3 border-t border-line pt-3">
              <button type="button" className="h-9 cursor-pointer border border-line-strong bg-canvas px-4 font-mono text-[11px] text-ink hover:bg-surface" onClick={reset}>
                another attempt
              </button>
              {chosen && (
                <a className="font-mono text-[11px] text-muted underline hover:text-ink" href={chosen.markscheme_url} target="_blank" rel="noreferrer">
                  open the official markscheme
                </a>
              )}
              <span className="font-mono text-[10px] text-faint">marked by {verdict.model}</span>
            </div>
          </motion.section>
        )}

        {history.length > 0 && (
          <section className="flex flex-col gap-2 border-t border-line pt-4">
            <div className="flex items-baseline justify-between gap-3">
              <h3 className={LABEL}>previous write-ups</h3>
              {earnedRate && (
                <span className="font-mono text-[11px] text-muted">
                  {earnedRate.earned}/{earnedRate.available} marks · {Math.round(earnedRate.share * 100)}%
                </span>
              )}
            </div>
            <ul className="flex flex-col gap-1">
              {history.slice(0, 12).map((row) => (
                <li key={row.id} className="flex flex-wrap items-baseline gap-x-2 text-xs text-muted">
                  <span className="font-mono text-[10px] text-ink">{row.earned ?? '?'}/{row.available ?? '?'}</span>
                  <span>{row.reference}</span>
                  <span className="text-faint">{row.math}</span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  )
}
