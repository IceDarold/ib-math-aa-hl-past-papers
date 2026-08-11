import type { Question } from '../types'
import { AnimatePresence, LayoutGroup, motion } from 'motion/react'
import { shortId } from '../lib/questions'
import { useI18n } from '../i18n'
import { MathText } from './MathText'

interface ResultsTableProps {
  questions: Question[]
  selectedId: string | null
  marks: number
  onSelect: (id: string) => void
  onReset: () => void
}

export function ResultsTable({
  questions,
  selectedId,
  marks,
  onSelect,
  onReset,
}: ResultsTableProps) {
  const { count, t } = useI18n()
  return (
    <main id="results" tabIndex={-1} className="results-panel flex min-h-0 min-w-0 flex-1 flex-col bg-canvas">
      <div className="hidden min-h-10.5 items-center border-b border-line px-3 max-[960px]:flex">
        <div className="flex items-baseline gap-2">
          <AnimatePresence initial={false} mode="popLayout">
            <motion.strong key={questions.length} initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 6 }}>
              {count('blocks', questions.length)}
            </motion.strong>
          </AnimatePresence>
          <AnimatePresence initial={false} mode="popLayout">
            <motion.span key={marks} className="text-xs text-muted" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              {count('marks', marks)}
            </motion.span>
          </AnimatePresence>
        </div>
      </div>

      <div className="results-viewport min-h-0 overflow-x-hidden overflow-y-auto">
        <LayoutGroup id="results-selection">
          <table className="results-table border-collapse">
            <thead className="sticky top-0 z-10 bg-canvas">
              <tr>
                <Header className="results-col-id">ID</Header>
                <Header>{t('results.task')}</Header>
                <Header className="results-col-topic">{t('results.topic')}</Header>
                <Header className="results-col-method">{t('results.method')}</Header>
                <Header className="results-col-marks text-right">{t('results.marks')}</Header>
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
                    onClick={() => onSelect(question.id)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault()
                        onSelect(question.id)
                      }
                    }}
                  >
                    <td className="results-col-id relative h-12 overflow-hidden border-b border-line px-2.5 py-1.5 font-mono text-[11px] text-ellipsis whitespace-nowrap" title={question.id}>
                      {selected && (
                        <motion.span
                          layoutId="selected-row"
                          className="absolute inset-y-1.5 left-0 w-0.75 rounded-r-full bg-primary shadow-[0_0_12px_oklch(0.56_0.20_18/0.45)]"
                          transition={{ type: 'spring', stiffness: 520, damping: 42, mass: 0.72 }}
                          aria-hidden="true"
                        />
                      )}
                      {shortId(question)}
                    </td>
                    <td className="results-task h-12 overflow-hidden border-b border-line px-2.5 py-1.5 leading-[1.35]">
                      <MathText>{question.task_summary}</MathText>
                      <small className="mt-0.5 block text-muted max-[680px]:hidden">
                        {question.session} · {question.review_status === 'ai_draft' ? t('filters.aiDraft') : t('results.verified')} · Q{question.question}{question.part === '-' ? '' : `(${question.part})`} · {t('results.pages')} {question.source_pages}
                      </small>
                    </td>
                    <td className="results-col-topic h-12 overflow-hidden border-b border-line px-2.5 py-1.5">
                      <Taxon title={question.primary_topic}>{question.primary_topic}</Taxon>
                    </td>
                    <td className="results-col-method h-12 overflow-hidden border-b border-line px-2.5 py-1.5">
                      <Taxon title={question.methodFamily}>{question.methodFamily}</Taxon>
                    </td>
                    <td className="results-col-marks h-12 border-b border-line px-2.5 py-1.5 text-right tabular-nums">{question.marks}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </LayoutGroup>

        <AnimatePresence>
          {questions.length === 0 && (
            <motion.div
              className="grid min-h-65 place-content-center justify-items-center gap-2 text-muted"
              initial={{ opacity: 0, scale: 0.96, filter: 'blur(5px)' }}
              animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
              exit={{ opacity: 0, scale: 0.97, filter: 'blur(4px)' }}
            >
              <strong className="text-[15px] text-ink">{t('results.emptyTitle')}</strong>
              <span>{t('results.emptyBody')}</span>
              <motion.button
                className="min-h-7.5 cursor-pointer border border-line-strong bg-canvas px-2.5 hover:bg-surface"
                type="button"
                whileHover={{ y: -2, scale: 1.03 }}
                whileTap={{ y: 0, scale: 0.94 }}
                onClick={onReset}
              >
                {t('results.reset')}
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
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
