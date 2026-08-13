import { useEffect, useMemo, useState } from 'react'
import { motion } from 'motion/react'
import { practicumSections, practicums, type Practicum, type PracticumSkill } from '../data/practicums'
import type { Question } from '../types'
import { MathText } from './MathText'

interface PracticumHubProps {
  questions: Question[]
  onOpenAtlas: (topic: string) => void
}

interface NotebookCell { cell_type: 'markdown' | 'code'; source: string[] }
interface Notebook { cells: NotebookCell[] }

const progressKey = 'question-atlas:practicum-progress'

function loadProgress(): Record<string, boolean> {
  try {
    const value = JSON.parse(localStorage.getItem(progressKey) ?? '{}') as unknown
    return value && typeof value === 'object' ? value as Record<string, boolean> : {}
  } catch {
    return {}
  }
}

function calculatorLabel(mode: PracticumSkill['calculator']) {
  return {
    required: 'нужен',
    replaces: 'заменяет ручной ход',
    speeds_up: 'ускоряет',
    checks: 'только проверка',
    forbidden: 'не поможет',
  }[mode]
}

function sourceStats(practicum: Practicum, questions: Question[]) {
  const matches = questions.filter((question) => practicum.topics.includes(question.primary_topic))
  return { blocks: matches.length, marks: matches.reduce((sum, question) => sum + question.marks, 0) }
}

export function PracticumHub({ questions, onOpenAtlas }: PracticumHubProps) {
  const ready = practicums.filter((practicum) => practicum.status === 'ready')
  const [selectedId, setSelectedId] = useState(ready[0]?.id ?? null)
  const [progress, setProgress] = useState<Record<string, boolean>>(loadProgress)
  const [studyOpen, setStudyOpen] = useState(false)
  const [notebook, setNotebook] = useState<Notebook | null>(null)
  const [notebookError, setNotebookError] = useState(false)
  const selected = practicums.find((practicum) => practicum.id === selectedId) ?? ready[0]

  const updateProgress = (id: string, checked: boolean) => {
    setProgress((current) => {
      const next = { ...current, [id]: checked }
      localStorage.setItem(progressKey, JSON.stringify(next))
      return next
    })
  }

  const completed = selected?.skills?.filter((skill) => progress[`${selected.id}:${skill.id}`]).length ?? 0
  const selectedStats = useMemo(() => selected ? sourceStats(selected, questions) : null, [questions, selected])

  useEffect(() => {
    setStudyOpen(false)
    setNotebook(null)
    setNotebookError(false)
  }, [selected?.id])

  useEffect(() => {
    if (!studyOpen || !selected?.notebook) return
    let cancelled = false
    fetch(`/${selected.notebook}`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error('notebook unavailable')))
      .then((value: Notebook) => { if (!cancelled) setNotebook(value) })
      .catch(() => { if (!cancelled) setNotebookError(true) })
    return () => { cancelled = true }
  }, [selected?.notebook, studyOpen])

  return (
    <main id="practicums" className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-300 px-4 py-7 max-[680px]:px-3 max-[680px]:py-5">
        <section className="grid gap-4 border-b border-line pb-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
          <div>
            <p className="mb-2 font-mono text-[11px] tracking-[0.12em] text-primary uppercase">Практикумы · AA HL</p>
            <h1 className="m-0 max-w-180 text-2xl leading-tight font-semibold tracking-[-0.025em]">Тренируй не тему, а конкретный ход решения.</h1>
            <p className="mt-3 mb-0 max-w-165 leading-relaxed text-muted">Каждый практикум ведёт по одной лестнице: распознать триггер → выполнить приём → решить связанное экзаменационное задание → вернуться к нему на скорость.</p>
          </div>
          <div className="grid grid-cols-2 border border-line-strong bg-surface text-center">
            <div className="px-4 py-3"><strong className="block text-xl tabular-nums">{practicums.length}</strong><span className="text-[11px] text-muted">в карте</span></div>
            <div className="border-l border-line px-4 py-3"><strong className="block text-xl tabular-nums">{ready.length}</strong><span className="text-[11px] text-muted">готовы</span></div>
          </div>
        </section>

        <section className="mt-6" aria-labelledby="practicum-map-title">
          <div className="mb-3 flex items-baseline justify-between gap-3">
            <h2 id="practicum-map-title" className="m-0 text-sm font-semibold">Карта подготовки</h2>
            <span className="text-xs text-muted">Готовые карточки открывают рабочую лестницу.</span>
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            {practicumSections.map((section) => {
              const sectionItems = practicums.filter((practicum) => practicum.section === section.id)
              return (
                <section key={section.id} className="border border-line bg-surface/45" aria-label={section.title}>
                  <header className="flex items-center justify-between border-b border-line bg-canvas px-3 py-2.5">
                    <h3 className="m-0 text-sm font-semibold">{section.id} · {section.title}</h3>
                    <span className="font-mono text-[11px] text-muted">{sectionItems.length}</span>
                  </header>
                  <div className="grid sm:grid-cols-2">
                    {sectionItems.map((practicum) => {
                      const active = practicum.id === selected?.id
                      const isReady = practicum.status === 'ready'
                      return (
                        <motion.button
                          key={practicum.id}
                          className={`min-h-22 cursor-pointer border-0 border-b border-line p-3 text-left last:border-b-0 hover:bg-primary-soft sm:[&:nth-last-child(2):nth-child(odd)]:border-b-0 ${active ? 'bg-primary-soft shadow-[inset_3px_0_0_var(--color-primary)]' : 'bg-transparent'} ${!isReady ? 'opacity-70' : ''}`}
                          type="button"
                          aria-pressed={active}
                          onClick={() => setSelectedId(practicum.id)}
                          whileTap={{ scale: 0.985 }}
                        >
                          <span className="mb-1 flex items-center justify-between gap-2 font-mono text-[11px] text-muted"><span>{practicum.id}</span><Status status={practicum.status} /></span>
                          <span className="block leading-snug font-medium">{practicum.title}</span>
                        </motion.button>
                      )
                    })}
                  </div>
                </section>
              )
            })}
          </div>
        </section>

        {selected && (
          <section className="mt-7 border border-line" aria-labelledby="selected-practicum-title">
            <header className="flex flex-wrap items-start justify-between gap-3 border-b border-line bg-surface px-4 py-4">
              <div>
                <p className="m-0 font-mono text-[11px] text-primary">{selected.id} · {selected.sectionTitle}</p>
                <h2 id="selected-practicum-title" className="mt-1 mb-0 text-xl leading-tight font-semibold">{selected.title}</h2>
              </div>
              <Status status={selected.status} large />
            </header>

            {selected.status === 'ready' && selected.skills && selected.corpus ? (
              <>
              <div className="grid xl:grid-cols-[minmax(0,1fr)_300px]">
                <div className="p-4">
                  <div className="mb-5 grid gap-3 sm:grid-cols-3">
                    <Metric value={selected.corpus.blocks} label="блоков в отобранном корпусе" />
                    <Metric value={selected.corpus.marks} label="баллов исходной практики" />
                    <Metric value={`${completed}/${selected.skills.length}`} label="приёмов отмечено" />
                  </div>
                  <div className="mb-3 flex items-baseline justify-between gap-3">
                    <h3 className="m-0 text-sm font-semibold">Лестница приёмов</h3>
                    <span className="text-xs text-muted">Сначала назвать приём, потом решать.</span>
                  </div>
                  <ol className="m-0 grid list-none gap-1.5 p-0">
                    {selected.skills.map((skill, index) => {
                      const key = `${selected.id}:${skill.id}`
                      const checked = Boolean(progress[key])
                      return (
                        <li key={skill.id} className={`grid grid-cols-[auto_auto_minmax(0,1fr)] gap-3 border border-line p-3 transition-colors ${checked ? 'bg-verified-soft' : 'bg-canvas'}`}>
                          <span className="grid size-6 place-items-center rounded-full border border-line-strong font-mono text-[11px] text-muted">{index + 1}</span>
                          <input className="mt-1 size-4 accent-[var(--color-verified)]" type="checkbox" checked={checked} aria-label={`Отметить приём «${skill.name}» пройденным`} onChange={(event) => updateProgress(key, event.target.checked)} />
                          <div className="min-w-0">
                            <strong className="block leading-snug">{skill.name}</strong>
                            <p className="mt-1 mb-2 leading-relaxed text-muted">Триггер: {skill.trigger}</p>
                            <span className="inline-flex rounded-[3px] border border-line bg-surface px-1.5 py-0.5 font-mono text-[10.5px] text-muted">GDC: {calculatorLabel(skill.calculator)}</span>
                          </div>
                        </li>
                      )
                    })}
                  </ol>
                </div>
                <aside className="border-t border-line bg-surface p-4 xl:border-t-0 xl:border-l">
                  <h3 className="m-0 text-sm font-semibold">Как проходить</h3>
                  <ol className="mt-3 mb-5 space-y-2 pl-4 leading-relaxed text-muted">
                    <li>Пройди ноутбук сверху вниз, не открывая решения заранее.</li>
                    <li>Отметь приём после самопроверки, а не после прочтения.</li>
                    <li>В конце вернись к заданию на таймере через неделю.</li>
                  </ol>
                  {selected.notebook && <a className="mb-2 flex min-h-9 items-center justify-center border border-primary bg-primary px-3 text-center font-medium text-white hover:bg-primary-dark" href={`/${selected.notebook}`} download>Скачать ноутбук .ipynb</a>}
                  <button className="mb-2 flex min-h-9 w-full cursor-pointer items-center justify-center border border-line-strong bg-canvas px-3 font-medium hover:bg-surface-strong" type="button" onClick={() => setStudyOpen((open) => !open)}>{studyOpen ? 'Закрыть режим обучения' : 'Учиться в браузере'}</button>
                  <button className="flex min-h-9 w-full cursor-pointer items-center justify-center border border-line-strong bg-canvas px-3 font-medium hover:bg-surface-strong" type="button" onClick={() => onOpenAtlas(selected.topics[0]!)}>Открыть задания этого практикума</button>
                  {selectedStats && <p className="mt-3 mb-0 text-xs leading-relaxed text-muted">В текущем атласе по основной теме: {selectedStats.blocks} блоков · {selectedStats.marks} баллов. Карта практикумов оставляет отбор и порядок упражнений за ноутбуком.</p>}
                </aside>
              </div>
              {studyOpen && <NotebookStudy notebook={notebook} error={notebookError} />}
              </>
            ) : (
              <div className="grid gap-4 p-4 md:grid-cols-[minmax(0,1fr)_auto] md:items-center">
                <div>
                  <h3 className="m-0 text-sm font-semibold">Практикум спланирован, но ещё не собран</h3>
                  <p className="mt-2 mb-0 max-w-150 leading-relaxed text-muted">Тема уже имеет границы в карте. Следующий шаг — карточки приёмов, отбор вопросов, затем ноутбук с самопроверкой и заданием на таймере.</p>
                </div>
                <button className="min-h-9 cursor-pointer border border-line-strong bg-canvas px-3 font-medium hover:bg-surface-strong" type="button" onClick={() => onOpenAtlas(selected.topics[0]!)}>Посмотреть корпус в атласе</button>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  )
}

function NotebookStudy({ notebook, error }: { notebook: Notebook | null; error: boolean }) {
  if (error) return <div className="border-t border-line p-4 text-muted">Не удалось загрузить учебный режим. Ноутбук по-прежнему доступен для скачивания.</div>
  if (!notebook) return <div className="border-t border-line p-4 text-muted">Загружаю практикум…</div>

  const solutionIndex = notebook.cells.findIndex((cell) => cell.cell_type === 'markdown' && cell.source.join('').includes('🔑 Решения'))
  const cells = notebook.cells.slice(0, solutionIndex === -1 ? notebook.cells.length : solutionIndex)
    .filter((cell) => cell.cell_type === 'markdown')

  return (
    <section className="border-t border-line bg-canvas p-4" aria-label="Учебный режим">
      <div className="mx-auto max-w-190">
        <div className="mb-5 border-l-3 border-primary bg-primary-soft px-3 py-2.5 text-sm leading-relaxed"><strong>Режим обучения.</strong> Решай задания на бумаге; решения намеренно скрыты. Для самопроверки ответа скачай полный ноутбук и запусти его в Jupyter или Kaggle.</div>
        <div className="grid gap-4">
          {cells.map((cell, index) => <NotebookMarkdown key={index} source={cell.source.join('')} />)}
        </div>
      </div>
    </section>
  )
}

function NotebookMarkdown({ source }: { source: string }) {
  const trimmed = source.replace(/^---\s*\n?/, '').trim()
  const heading = /^(#{1,2})\s+(.+?)(?:\n|$)/.exec(trimmed)
  const body = heading ? trimmed.slice(heading[0].length).trim() : trimmed
  const title = heading?.[2]?.replace(/\*\*/g, '')
  return (
    <article className="border border-line bg-surface/45 p-4 leading-relaxed">
      {title && (heading?.[1]?.length === 1 ? <h2 className="mt-0 mb-3 text-lg leading-snug font-semibold"><MathText>{title}</MathText></h2> : <h3 className="mt-0 mb-3 text-[15px] leading-snug font-semibold"><MathText>{title}</MathText></h3>)}
      {body && <div className="whitespace-pre-wrap text-[13px] text-ink"><MathText>{body.replace(/\*\*/g, '').replace(/\*(.*?)\*/g, '$1')}</MathText></div>}
    </article>
  )
}

function Status({ status, large = false }: { status: Practicum['status']; large?: boolean }) {
  const ready = status === 'ready'
  return <span className={`inline-flex items-center rounded-full border px-2 py-0.5 font-mono text-[10px] ${ready ? 'border-verified/25 bg-verified-soft text-verified' : 'border-line bg-surface text-muted'} ${large ? 'text-[11px]' : ''}`}>{ready ? 'готов' : 'в плане'}</span>
}

function Metric({ value, label }: { value: string | number; label: string }) {
  return <div className="border border-line bg-surface px-3 py-2.5"><strong className="block text-lg tabular-nums">{value}</strong><span className="text-[11px] leading-snug text-muted">{label}</span></div>
}
