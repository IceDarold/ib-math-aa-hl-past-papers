import type { Question } from '../types'
import { pluralize, shortId } from '../lib/questions'
import { MathText } from './MathText'

interface ResultsTableProps {
  questions: Question[]
  selectedId: string | null
  marks: number
  onSelect: (id: string, revealInspector: boolean) => void
  onReset: () => void
  onOpenInspector: () => void
}

export function ResultsTable({
  questions,
  selectedId,
  marks,
  onSelect,
  onReset,
  onOpenInspector,
}: ResultsTableProps) {
  return (
    <main id="results" tabIndex={-1} className="flex min-h-0 min-w-0 flex-col bg-canvas">
      <div className="hidden min-h-10.5 items-center justify-between border-b border-line px-3 max-[960px]:flex">
        <div className="flex items-baseline gap-2">
          <strong>{pluralize(questions.length, 'блок', 'блока', 'блоков')}</strong>
          <span className="text-xs text-muted">{pluralize(marks, 'балл', 'балла', 'баллов')}</span>
        </div>
        <button
          className="min-h-7.5 cursor-pointer border border-line-strong bg-canvas px-2.5 disabled:cursor-default disabled:opacity-45"
          type="button"
          disabled={!selectedId}
          onClick={onOpenInspector}
        >
          Детали
        </button>
      </div>

      <div className="min-h-0 overflow-auto">
        <table className="w-full table-fixed border-collapse">
          <thead className="sticky top-0 z-10 bg-canvas">
            <tr>
              <Header className="w-44 max-[1220px]:w-36.5 max-[960px]:w-42 max-[680px]:w-32">ID</Header>
              <Header>Задание</Header>
              <Header className="w-38.5 max-[1220px]:w-34 max-[680px]:w-32.5 max-[480px]:hidden">Тема</Header>
              <Header className="w-43 max-[1220px]:w-37 max-[680px]:hidden">Метод</Header>
              <Header className="w-13.5 text-right">Баллы</Header>
            </tr>
          </thead>
          <tbody>
            {questions.map((question) => {
              const selected = question.id === selectedId
              return (
                <tr
                  key={question.id}
                  data-question-id={question.id}
                  tabIndex={0}
                  aria-selected={selected}
                  className={`relative cursor-pointer transition-colors duration-150 ease-out-quart hover:bg-surface focus-visible:relative focus-visible:z-1 ${selected ? 'bg-primary-soft shadow-[inset_0_0_0_1px_oklch(0.82_0.08_18)]' : ''}`}
                  onClick={() => onSelect(question.id, true)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                      event.preventDefault()
                      onSelect(question.id, true)
                    }
                  }}
                >
                  <td className="h-12 overflow-hidden border-b border-line px-2.5 py-1.5 font-mono text-[11px] text-ellipsis whitespace-nowrap" title={question.id}>
                    {shortId(question)}
                  </td>
                  <td className="h-12 border-b border-line px-2.5 py-1.5 leading-[1.35]">
                    <MathText>{question.task_summary}</MathText>
                    <small className="mt-0.5 block text-muted max-[680px]:hidden">
                      Q{question.question}{question.part === '-' ? '' : `(${question.part})`} · pp. {question.source_pages}
                    </small>
                  </td>
                  <td className="h-12 border-b border-line px-2.5 py-1.5 max-[480px]:hidden">
                    <Taxon title={question.primary_topic}>{question.primary_topic}</Taxon>
                  </td>
                  <td className="h-12 border-b border-line px-2.5 py-1.5 max-[680px]:hidden">
                    <Taxon title={question.methodFamily}>{question.methodFamily}</Taxon>
                  </td>
                  <td className="h-12 border-b border-line px-2.5 py-1.5 text-right tabular-nums">{question.marks}</td>
                </tr>
              )
            })}
          </tbody>
        </table>

        {questions.length === 0 && (
          <div className="grid min-h-65 place-content-center justify-items-center gap-2 text-muted">
            <strong className="text-[15px] text-ink">Ничего не найдено</strong>
            <span>Измените запрос или сбросьте фильтры.</span>
            <button className="min-h-7.5 cursor-pointer border border-line-strong bg-canvas px-2.5 hover:bg-surface" type="button" onClick={onReset}>
              Сбросить
            </button>
          </div>
        )}
      </div>
    </main>
  )
}

function Header({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <th className={`h-10 border-b border-line px-2.5 text-left text-[11px] font-semibold tracking-[0.025em] text-muted uppercase ${className}`} scope="col">
      {children}
    </th>
  )
}

export function Taxon({ children, title }: { children: React.ReactNode; title?: string }) {
  return (
    <span className="inline-block max-w-full overflow-hidden rounded-[3px] border border-line bg-surface px-1.5 py-0.5 font-mono text-[10.5px] text-ellipsis whitespace-nowrap" title={title}>
      {children}
    </span>
  )
}
