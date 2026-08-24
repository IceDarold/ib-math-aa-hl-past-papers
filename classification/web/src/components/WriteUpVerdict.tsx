import { useState } from 'react'

export interface Verdict {
  transcription: string
  legible: boolean
  mathematics: {
    verdict: string
    errors: { line: string; problem: string; consequence: string }[]
  }
  presentation: { id: string; met: boolean; code: string; comment: string; fix: string }[]
  marks: { available: number | null; earned: number; lost: { code: string; why: string }[] }
  model_write_up: string
  one_thing: string
  reference: string | null
  skill_name: string | null
  model: string
}

const LABEL = 'font-mono text-[10px] uppercase tracking-wide text-faint max-[560px]:pt-1.5'

/** R1 is the mark candidates lose most often and notice least — make it loud. */
function codeTone(code: string) {
  return code === 'R1' ? 'bg-ink text-canvas' : 'bg-surface text-muted'
}

export function WriteUpVerdict({ verdict, markschemeUrl }: { verdict: Verdict; markschemeUrl?: string }) {
  const [showTranscription, setShowTranscription] = useState(false)
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line pb-3">
        <span className="text-sm text-ink">{verdict.reference}</span>
        <span className="font-mono text-[11px] text-muted">
          {verdict.marks.earned} / {verdict.marks.available ?? '?'} marks
        </span>
      </div>

      <dl className="grid grid-cols-[8rem_1fr] items-baseline gap-x-3 gap-y-3 max-[560px]:grid-cols-1 max-[560px]:gap-y-1">
        <dt className={LABEL}>mathematics</dt>
        <dd className="flex flex-col gap-1.5">
          <span className="text-sm text-ink">{verdict.mathematics?.verdict}</span>
          {verdict.mathematics?.errors?.map((item) => (
            <div key={item.line + item.problem} className="border-l-2 border-line pl-2 text-xs leading-relaxed text-muted">
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
              <span className={`h-fit px-1 py-0.5 font-mono text-[10px] ${item.met ? 'bg-surface text-faint' : codeTone(item.code)}`}>
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

        {verdict.marks?.lost?.length > 0 && <>
          <dt className={LABEL}>marks lost</dt>
          <dd className="flex flex-col gap-1 text-xs text-muted">
            {verdict.marks.lost.map((item) => (
              <div key={item.code + item.why} className="flex gap-2">
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
        <dd className="flex flex-col gap-2">
          <button
            type="button"
            className="w-fit cursor-pointer border-0 bg-transparent p-0 font-mono text-[11px] text-muted underline hover:text-ink"
            onClick={() => setShowTranscription((value) => !value)}
          >
            {showTranscription ? 'hide' : 'show'} the transcription
          </button>
          {showTranscription && (
            <pre className="whitespace-pre-wrap border border-line p-2 text-[11px] leading-relaxed text-muted">
              {verdict.transcription}
            </pre>
          )}
          {!verdict.legible && (
            <span className="text-[11px] text-ink">Some of the page was hard to read — check the transcription before trusting the marking.</span>
          )}
        </dd>
      </dl>

      <div className="flex flex-wrap items-center gap-3 text-[10px]">
        {markschemeUrl && (
          <a className="font-mono text-[11px] text-muted underline hover:text-ink" href={markschemeUrl} target="_blank" rel="noreferrer">
            open the official markscheme
          </a>
        )}
        <span className="font-mono text-faint">marked by {verdict.model}</span>
      </div>
    </div>
  )
}
