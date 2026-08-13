import type { Question } from '../types'
import { motion } from 'motion/react'
import { pdfUrl } from '../lib/questions'
import { useI18n } from '../i18n'
import { CheckIcon, CloseIcon, FileIcon } from './Icons'
import { MathText } from './MathText'
import { Taxon } from './ResultsTable'

interface InspectorProps {
  question: Question
  compact: boolean
  onClose: () => void
}

export function Inspector({ question, compact, onClose }: InspectorProps) {
  const { t } = useI18n()
  return (
    <motion.aside
      aria-label={t('inspector.label')}
      aria-live="polite"
      className={`inspector-panel min-h-0 min-w-0 shrink-0 overflow-y-auto border-l border-line bg-canvas ${compact ? 'fixed top-13 right-0 bottom-8 z-30 shadow-overlay' : 'relative'}`}
      initial={{ opacity: 0, x: compact ? 38 : 22, filter: 'blur(7px)' }}
      animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, x: compact ? 32 : 18, filter: 'blur(5px)' }}
      transition={{
        x: { type: 'spring', stiffness: 460, damping: 36, mass: 0.78 },
        opacity: { duration: 0.2 },
        filter: { duration: 0.22 },
      }}
    >
      <motion.div
        key={question.id}
        initial={{ opacity: 0, y: 10, filter: 'blur(4px)' }}
        animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
        transition={{ duration: 0.22 }}
      >
        <InspectorContent question={question} onClose={onClose} />
      </motion.div>
    </motion.aside>
  )
}

function InspectorContent({ question, onClose }: { question: Question; onClose: () => void }) {
  const { count, t } = useI18n()
  const questionLabel = `Q${question.question}${question.part === '-' ? '' : `(${question.part})`}`
  return (
    <>
      <header className="sticky top-0 z-10 border-b border-line bg-canvas/96 px-4.5 pt-3.5 pb-3 backdrop-blur-[2px]">
        <div className="flex items-center justify-between gap-2">
          <span className="min-w-0 flex-1 font-mono text-[11px] text-muted [overflow-wrap:anywhere]">{question.id}</span>
          <motion.span
            className={`flex shrink-0 items-center gap-1 border px-1.5 py-0.5 text-[10px] ${question.review_status === 'manual_verified' ? 'border-verified/40 bg-verified-soft text-verified' : 'border-info/40 bg-info/10 text-info'}`}
            initial={{ opacity: 0, scale: 0.84 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ type: 'spring', stiffness: 520, damping: 34 }}
          >
            {question.review_status === 'manual_verified' && <CheckIcon className="size-3" />}
            {question.review_status === 'manual_verified' ? t('inspector.manualVerified') : t('inspector.aiDraft')}
          </motion.span>
          <motion.button
            className="grid size-8 shrink-0 cursor-pointer place-items-center border border-transparent bg-transparent hover:border-line hover:bg-surface"
            type="button"
            aria-label={t('inspector.close')}
            whileHover={{ rotate: 6, scale: 1.08 }}
            whileTap={{ rotate: -6, scale: 0.86 }}
            onClick={onClose}
          >
            <CloseIcon />
          </motion.button>
        </div>
        <h2 className="my-3 mb-1.5 text-lg leading-tight font-semibold tracking-[-0.01em] text-pretty"><MathText>{question.task_summary}</MathText></h2>
        <div className="flex flex-wrap gap-1.5 text-[11px] text-muted">
          <span>{t('inspector.paper')} {question.paper}</span><span>—</span><span>{questionLabel}</span><span>—</span>
          <span>{count('marks', question.marks)}</span><span>—</span>
          <span className={question.calculator === 'yes' ? 'text-info' : ''}>{question.calculator === 'yes' ? t('inspector.calculator') : t('inspector.nonCalculator')}</span>
          <span>—</span><span>{question.session} — {question.zone}</span>
        </div>
      </header>

      <Section title={t('inspector.classification')}>
        <dl className="grid grid-cols-[105px_minmax(0,1fr)] items-start gap-x-2 gap-y-2">
          <dt className="text-[11px] text-muted">{t('inspector.primaryTopic')}</dt><dd className="m-0 min-w-0"><Taxon>{question.primary_topic}</Taxon></dd>
          <dt className="text-[11px] text-muted">{t('inspector.secondary')}</dt><dd className="m-0 min-w-0"><Tags values={question.secondaryTopics} /></dd>
          <dt className="text-[11px] text-muted">{t('inspector.methodFamily')}</dt><dd className="m-0 min-w-0"><Taxon>{question.methodFamily}</Taxon></dd>
          <dt className="text-[11px] text-muted">{t('inspector.methodTags')}</dt><dd className="m-0 min-w-0"><Tags values={question.tags} /></dd>
          <dt className="text-[11px] text-muted">{t('inspector.sourcePages')}</dt><dd className="m-0">{question.source_pages}</dd>
          <dt className="text-[11px] text-muted">{t('inspector.markschemePages')}</dt><dd className="m-0">{question.markscheme_pages}</dd>
          <dt className="text-[11px] text-muted">{t('inspector.reviewFlags')}</dt><dd className="m-0 min-w-0"><Tags values={question.reviewFlags} /></dd>
        </dl>
      </Section>

      <Section title={t('inspector.solutionPath')}>
        {question.pathSteps.length > 0 ? (
          <ol className="m-0 list-none p-0">
            {question.pathSteps.map((step, index) => (
              <motion.li
                key={`${index}-${step}`}
                className="relative min-h-10 pb-3 pl-8 leading-[1.45] last:pb-0"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: Math.min(index, 5) * 0.035, duration: 0.2 }}
              >
                <motion.span
                  className="absolute top-0 left-0 z-1 grid size-5 place-items-center rounded-full bg-primary font-mono text-[11px] text-white"
                  initial={{ scale: 0.4 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: Math.min(index, 5) * 0.035, type: 'spring', stiffness: 560, damping: 30 }}
                >
                  {index + 1}
                </motion.span>
                {index < question.pathSteps.length - 1 && <span className="absolute top-5 bottom-0 left-2.5 w-px bg-primary/30" aria-hidden="true" />}
                <MathText>{step}</MathText>
              </motion.li>
            ))}
          </ol>
        ) : <p className="m-0">—</p>}
      </Section>

      <Section title={t('inspector.alternatives')}>
        {question.alternatives.length > 0
          ? <AlternativeList values={question.alternatives} />
          : <p className="m-0 leading-relaxed text-muted">{t('inspector.noAlternative')}</p>}
      </Section>

      {question.review_status === 'ai_draft' && (
        <Section title={t('inspector.evidence')}>
          <div className="mb-2 text-[11px] text-muted">
            {t('inspector.confidence')}: {t('inspector.segmentation')} {question.confidenceLevels.segmentation} — {t('inspector.topic')} {question.confidenceLevels.topic} — {t('inspector.method')} {question.confidenceLevels.method}
          </div>
          {question.evidenceItems.length > 0 ? (
            <div className="grid gap-1.5">
              {question.evidenceItems.map((item, index) => (
                <div key={`${item.markscheme_pages}-${index}`} className="border border-line bg-surface px-2 py-1.5 leading-relaxed">
                  <span className="mr-1 font-mono text-[10px] text-muted">{t('inspector.msPage')} {item.markscheme_pages}</span>
                  <MathText>{item.basis}</MathText>
                </div>
              ))}
            </div>
          ) : <p className="m-0 text-muted">{t('inspector.noEvidence')}</p>}
        </Section>
      )}

      <Section title={t('inspector.source')}>
        <div className="grid grid-cols-2 gap-2">
          <SourceLink href={pdfUrl(question, 'question-paper.pdf')} label={t('inspector.questionPaper')} />
          <SourceLink href={pdfUrl(question, 'markscheme.pdf')} label={t('inspector.markscheme')} />
        </div>
      </Section>
    </>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <motion.section className="border-b border-line px-4.5 py-3.5" initial={{ opacity: 0.55 }} animate={{ opacity: 1 }}>
      <h3 className="mt-0 mb-2.5 text-xs font-semibold">{title}</h3>
      {children}
    </motion.section>
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
    <motion.a
      className="flex min-w-0 items-center gap-1.5 border border-line p-2 text-primary-dark no-underline transition-colors duration-150 hover:border-primary hover:bg-primary-soft"
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      whileHover={{ y: -2, scale: 1.015 }}
      whileTap={{ y: 0, scale: 0.97 }}
    >
      <FileIcon className="size-4 shrink-0" />
      <span className="overflow-hidden text-ellipsis whitespace-nowrap">{label}</span>
    </motion.a>
  )
}
