/** Разбор попытки: что было на самом деле.
 *
 * Главное здесь не «верно/неверно», а ход самой схемы оценивания: это
 * разметка конкретного вопроса, а не пересказ приёма. Поэтому она стоит
 * первой, сразу под вердиктом, и читается как ответ на «а как надо было».
 */
import { useState } from 'react'
import type { Verdict as Result } from '../api'
import { api } from '../api'

const TONE = {
  ok: { bar: 'bg-ok', chip: 'bg-ok-soft text-ok', word: 'верно' },
  near: { bar: 'bg-near', chip: 'bg-near-soft text-near', word: 'рядом' },
  miss: { bar: 'bg-miss', chip: 'bg-miss-soft text-miss', word: 'мимо' },
} as const

export function Verdict({ result, onNext, last }: {
  result: Result
  onNext: () => void
  last: boolean
}) {
  const [flagged, setFlagged] = useState(false)
  const tone = result.ok ? TONE.ok : result.picked?.near ? TONE.near : TONE.miss

  return (
    <section className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto rounded-2xl border border-line bg-surface p-5 shadow-card">
      <div className="flex items-center gap-3">
        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[13px] font-medium ${tone.chip}`}>
          {tone.word}
        </span>
        {result.picked && (
          <span className="text-[14px] text-muted">
            вы назвали «{result.picked.name}»
            <span className="ml-1.5 font-mono text-[11px] text-faint">{result.picked.practicum}</span>
          </span>
        )}
      </div>

      <div className="flex flex-col gap-1">
        <p className="text-[12px] font-medium tracking-wide text-faint uppercase">приём</p>
        <p className="text-[19px] leading-tight font-medium text-ink">{result.skill_name}</p>
        <p className="font-mono text-[11px] text-faint">{result.skill}</p>
      </div>

      {result.method && result.method.length > 0 && (
        <div className="flex flex-col gap-1.5">
          <p className="text-[12px] font-medium tracking-wide text-faint uppercase">
            схема оценивания шла так
          </p>
          <ol className="flex flex-col gap-1.5">
            {result.method.map((step, index) => (
              <li key={step} className="flex gap-2.5 text-[14px] leading-snug text-ink">
                <span className="mt-0.5 w-4 shrink-0 font-mono text-[11px] text-faint">{index + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {result.alternatives && result.alternatives.length > 0 && (
        <div className="flex flex-col gap-1.5">
          <p className="text-[12px] font-medium tracking-wide text-faint uppercase">и так тоже принимают</p>
          <ul className="flex flex-col gap-1.5">
            {result.alternatives.map((line) => (
              <li key={line} className="flex gap-2.5 text-[14px] leading-snug text-muted">
                <span className="text-faint">·</span>
                <span>{line}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex flex-col gap-1.5">
        <p className="text-[12px] font-medium tracking-wide text-faint uppercase">узнаётся по</p>
        <p className="text-[14px] leading-snug text-muted">{result.trigger}</p>
      </div>

      {result.chain.length > 0 && (
        <details className="group">
          <summary className="cursor-pointer list-none text-[13px] text-accent hover:underline">
            ход приёма целиком ({result.chain.length})
          </summary>
          <ol className="mt-2 flex flex-col gap-1.5">
            {result.chain.map((step, index) => (
              <li key={step} className="flex gap-2.5 text-[14px] leading-snug text-muted">
                <span className="mt-0.5 w-4 shrink-0 font-mono text-[11px] text-faint">{index + 1}</span>
                <span>{step}</span>
              </li>
            ))}
          </ol>
        </details>
      )}

      {!result.ok && result.traps.length > 0 && (
        <div className="flex flex-col gap-1.5 rounded-xl bg-sunken p-3.5">
          <p className="text-[12px] font-medium tracking-wide text-faint uppercase">где срезаются</p>
          <ul className="flex flex-col gap-1.5">
            {result.traps.map((trap) => (
              <li key={trap} className="flex gap-2.5 text-[14px] leading-snug text-muted">
                <span className="text-faint">·</span>
                <span>{trap}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-auto flex flex-wrap items-center gap-3 border-t border-line pt-4">
        <button
          type="button"
          onClick={onNext}
          className="h-11 cursor-pointer rounded-xl bg-accent px-5 text-[15px] font-medium text-surface transition-opacity hover:opacity-90"
        >
          {last ? 'итог' : 'дальше'}
        </button>
        <span className="text-[12px] text-faint">Enter или пробел</span>
        <button
          type="button"
          disabled={flagged}
          onClick={() => {
            if (!result.block) return
            void api.flag(result.block, result.skill).then(() => setFlagged(true)).catch(() => undefined)
          }}
          className="ml-auto cursor-pointer text-[12px] text-faint underline hover:text-muted disabled:cursor-default disabled:no-underline"
        >
          {flagged ? 'отмечено' : 'разметка неверна'}
        </button>
      </div>
    </section>
  )
}
