import type { Question } from '../types'
import { pdfUrl } from '../lib/questions'
import { CheckIcon, CloseIcon, FileIcon } from './Icons'
import { MathText } from './MathText'
import { Taxon } from './ResultsTable'

interface InspectorProps {
  question: Question
  compact: boolean
  onClose: () => void
}

export function Inspector({ question, compact, onClose }: InspectorProps) {
  return (
    <aside
      aria-label="Детали задания"
      aria-live="polite"
      className={`inspector-panel min-h-0 min-w-0 shrink-0 overflow-y-auto border-l border-line bg-canvas motion-safe:animate-[panel-in_180ms_var(--ease-out-quart)] ${compact ? 'fixed top-13 right-0 bottom-8 z-30 shadow-overlay' : 'relative'}`}
    >
      <InspectorContent question={question} onClose={onClose} />
    </aside>
  )
}

function InspectorContent({ question, onClose }: { question: Question; onClose: () => void }) {
  const questionLabel = `Q${question.question}${question.part === '-' ? '' : `(${question.part})`}`
  return (
    <>
      <header className="sticky top-0 z-10 border-b border-line bg-canvas/96 px-4.5 pt-3.5 pb-3 backdrop-blur-[2px]">
        <div className="flex items-center justify-between gap-2">
          <span className="min-w-0 flex-1 font-mono text-[11px] text-muted [overflow-wrap:anywhere]">{question.id}</span>
          <span className="flex shrink-0 items-center gap-1 border border-verified/40 bg-verified-soft px-1.5 py-0.5 text-[10px] text-verified">
            <CheckIcon className="size-3" /> Проверено вручную
          </span>
          <button className="grid size-8 shrink-0 cursor-pointer place-items-center border border-transparent bg-transparent hover:border-line hover:bg-surface" type="button" aria-label="Закрыть детали" onClick={onClose}>
            <CloseIcon />
          </button>
        </div>
        <h2 className="my-3 mb-1.5 text-lg leading-tight font-semibold tracking-[-0.01em] text-pretty"><MathText>{question.task_summary}</MathText></h2>
        <div className="flex flex-wrap gap-1.5 text-[11px] text-muted">
          <span>Paper {question.paper}</span><span>·</span><span>{questionLabel}</span><span>·</span>
          <span>{question.marks} {question.marks === 1 ? 'mark' : 'marks'}</span><span>·</span>
          <span className={question.calculator === 'yes' ? 'text-info' : ''}>{question.calculator === 'yes' ? 'calculator' : 'non-calculator'}</span>
        </div>
      </header>

      <Section title="Классификация">
        <dl className="grid grid-cols-[105px_minmax(0,1fr)] items-start gap-x-2 gap-y-2">
          <dt className="text-[11px] text-muted">Primary topic</dt><dd className="m-0 min-w-0"><Taxon>{question.primary_topic}</Taxon></dd>
          <dt className="text-[11px] text-muted">Secondary</dt><dd className="m-0 min-w-0"><Tags values={question.secondaryTopics} /></dd>
          <dt className="text-[11px] text-muted">Method family</dt><dd className="m-0 min-w-0"><Taxon>{question.methodFamily}</Taxon></dd>
          <dt className="text-[11px] text-muted">Method tags</dt><dd className="m-0 min-w-0"><Tags values={question.tags} /></dd>
          <dt className="text-[11px] text-muted">Source pages</dt><dd className="m-0">{question.source_pages}</dd>
        </dl>
      </Section>

      <Section title="Путь решения">
        {question.pathSteps.length > 0 ? (
          <ol className="m-0 list-none p-0">
            {question.pathSteps.map((step, index) => (
              <li key={`${index}-${step}`} className="relative min-h-10 pb-3 pl-8 leading-[1.45] last:pb-0">
                <span className="absolute top-0 left-0 z-1 grid size-5 place-items-center rounded-full bg-primary font-mono text-[11px] text-white">{index + 1}</span>
                {index < question.pathSteps.length - 1 && <span className="absolute top-5 bottom-0 left-2.5 w-px bg-primary/30" aria-hidden="true" />}
                <MathText>{step}</MathText>
              </li>
            ))}
          </ol>
        ) : <p className="m-0">—</p>}
      </Section>

      <Section title="Допустимые альтернативы">
        {question.alternatives.length > 0
          ? <AlternativeList values={question.alternatives} />
          : <p className="m-0 leading-relaxed text-muted">В markscheme отдельный альтернативный маршрут не указан.</p>}
      </Section>

      <Section title="Источник">
        <div className="grid grid-cols-2 gap-2">
          <SourceLink href={pdfUrl(question, 'question-paper.pdf')} label="Question paper" />
          <SourceLink href={pdfUrl(question, 'markscheme.pdf')} label="Markscheme" />
        </div>
      </Section>
    </>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="border-b border-line px-4.5 py-3.5">
      <h3 className="mt-0 mb-2.5 text-xs font-semibold">{title}</h3>
      {children}
    </section>
  )
}

function Tags({ values }: { values: string[] }) {
  if (values.length === 0) return <>—</>
  return (
    <div className="flex flex-wrap gap-1">
      {values.map((value) => <Taxon key={value}>{value}</Taxon>)}
    </div>
  )
}

function AlternativeList({ values }: { values: string[] }) {
  return (
    <div className="grid gap-1.5">
      {values.map((value) => (
        <div key={value} className="border border-line bg-surface px-2 py-1.5 leading-relaxed">
          <MathText>{value}</MathText>
        </div>
      ))}
    </div>
  )
}

function SourceLink({ href, label }: { href: string; label: string }) {
  return (
    <a className="flex min-w-0 items-center gap-1.5 border border-line p-2 text-primary-dark no-underline transition-colors duration-150 hover:border-primary hover:bg-primary-soft" href={href} target="_blank" rel="noopener noreferrer">
      <FileIcon className="size-4 shrink-0" />
      <span className="overflow-hidden text-ellipsis whitespace-nowrap">{label}</span>
    </a>
  )
}
