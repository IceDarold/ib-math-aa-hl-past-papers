import { useEffect, useState } from 'react'
import { motion } from 'motion/react'
import { c3Exercises, type BrowserExercise } from '../data/browser-practicums'
import { practicumSections, practicums, type Practicum, type PracticumSkill } from '../data/practicums'
import { MathText } from './MathText'

interface PracticumHubProps {
  onOpenAtlas: (topic: string) => void
}

type PlayerTab = 'route' | 'practice' | 'exam'
interface Progress { completed: string[]; active: number; timerSeconds?: number }

const progressKey = 'question-atlas:browser-practicum-progress-v1'

function loadProgress(): Progress {
  try {
    const value = JSON.parse(localStorage.getItem(progressKey) ?? '{}') as Partial<Progress>
    return { completed: Array.isArray(value.completed) ? value.completed : [], active: Number.isInteger(value.active) ? Math.max(0, value.active!) : 0 }
  } catch {
    return { completed: [], active: 0 }
  }
}

function saveProgress(progress: Progress) {
  localStorage.setItem(progressKey, JSON.stringify(progress))
}

function calculatorLabel(mode: PracticumSkill['calculator']) {
  return { required: 'нужен', replaces: 'заменяет ручной ход', speeds_up: 'ускоряет', checks: 'только проверка', forbidden: 'не поможет' }[mode]
}

function selectedFromHash() {
  const value = /^#practicums\/([A-Z]\d+)$/.exec(window.location.hash)?.[1]
  return practicums.some((practicum) => practicum.id === value) ? value! : null
}

function setPracticumHash(id: string | null) {
  window.history.replaceState(null, '', id ? `#practicums/${id}` : '#practicums')
}

export function PracticumHub({ onOpenAtlas }: PracticumHubProps) {
  const browserPracticum = practicums.find((practicum) => practicum.id === 'C3')!
  const ready = practicums.filter((practicum) => practicum.status === 'ready')
  const [selectedId, setSelectedId] = useState<string | null>(selectedFromHash)
  const [progress, setProgress] = useState<Progress>(loadProgress)
  const selected = practicums.find((practicum) => practicum.id === selectedId) ?? null
  const completed = progress.completed.length

  const updateProgress = (next: Progress) => {
    setProgress(next)
    saveProgress(next)
  }

  const open = (id: string) => {
    setSelectedId(id)
    setPracticumHash(id)
  }

  useEffect(() => {
    const receiveHash = () => setSelectedId(selectedFromHash())
    window.addEventListener('hashchange', receiveHash)
    return () => window.removeEventListener('hashchange', receiveHash)
  }, [])

  if (selected) {
    return selected.id === 'C3'
      ? <BrowserPracticum practicum={browserPracticum} progress={progress} onProgress={updateProgress} onBack={() => { setSelectedId(null); setPracticumHash(null) }} onOpenAtlas={onOpenAtlas} />
      : <PlannedPracticum practicum={selected} onBack={() => { setSelectedId(null); setPracticumHash(null) }} onOpenAtlas={onOpenAtlas} />
  }

  return (
    <main id="practicums" className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-300 px-4 py-7 max-[680px]:px-3 max-[680px]:py-5">
        <header className="max-w-180">
          <p className="mb-2 font-mono text-[11px] tracking-[0.12em] text-primary uppercase">Практикумы — AA HL</p>
          <h1 className="m-0 text-3xl leading-[1.08] font-semibold tracking-[-0.035em]">Учебный маршрут, а не каталог тем.</h1>
          <p className="mt-3 mb-0 leading-relaxed text-muted">Выбирай один узкий ход, решай настоящие экзаменационные задачи, возвращайся к нему на скорость. Карта нужна для навигации; учёба начинается с конкретного следующего шага.</p>
        </header>

        <section className="mt-7 grid gap-4 lg:grid-cols-[minmax(0,1.35fr)_minmax(280px,.65fr)]" aria-label="Следующий шаг">
          <article className="border border-ink bg-ink p-5 text-canvas sm:p-6">
            <p className="m-0 font-mono text-[11px] tracking-[0.1em] text-primary-light uppercase">Начать сейчас — 45–70 минут</p>
            <h2 className="mt-2 mb-2 text-2xl leading-tight font-semibold">C3 — Тригонометрические уравнения</h2>
            <p className="m-0 max-w-145 leading-relaxed text-canvas/75">10 реальных вопросов идут от опорного угла до отбора посторонних корней. Проверка принимает эквивалентные записи и ловит потерянные решения.</p>
            <div className="mt-5 flex flex-wrap items-center gap-3">
              <button className="min-h-10 cursor-pointer border border-primary bg-primary px-4 font-medium text-white hover:bg-primary-dark" type="button" onClick={() => open('C3')}>{completed ? 'Продолжить' : 'Начать практикум'}</button>
              <span className="font-mono text-xs text-canvas/60">{completed}/{c3Exercises.length} заданий решено</span>
            </div>
          </article>
          <aside className="border border-line bg-surface p-5">
            <p className="m-0 font-mono text-[11px] tracking-[0.1em] text-muted uppercase">Принцип</p>
            <ol className="mt-3 mb-0 space-y-3 pl-4 text-sm leading-relaxed text-muted">
              <li>Назови триггер до вычислений.</li>
              <li>Реши на бумаге, затем введи ответ.</li>
              <li>Вернись к финальному заданию на таймере.</li>
            </ol>
          </aside>
        </section>

        <section className="mt-8" aria-labelledby="available-title">
          <div className="mb-3 flex items-baseline justify-between gap-3"><h2 id="available-title" className="m-0 text-lg font-semibold">Доступно сейчас</h2><span className="text-xs text-muted">Не все узлы карты становятся интерфейсом до появления упражнений.</span></div>
          <div className="grid gap-3 md:grid-cols-2">
            {ready.map((practicum) => (
              <button key={practicum.id} className="group grid cursor-pointer grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-3 border border-line bg-surface p-4 text-left hover:border-line-strong hover:bg-primary-soft" type="button" onClick={() => open(practicum.id)}>
                <span className="grid size-9 place-items-center rounded-full border border-primary/30 bg-primary-soft font-mono text-xs text-primary">{practicum.id}</span>
                <span><strong className="block leading-snug">{practicum.title}</strong><small className="mt-1 block text-muted">{practicum.id === 'C3' ? 'Браузерный режим — проверка ответов — таймер' : 'Ноутбук и карта приёмов'}</small></span>
                <span className="text-muted group-hover:text-ink">→</span>
              </button>
            ))}
          </div>
        </section>

        <section className="mt-8 border-t border-line pt-5" aria-labelledby="map-title">
          <div className="flex flex-wrap items-baseline justify-between gap-3"><h2 id="map-title" className="m-0 text-sm font-semibold">Вся карта подготовки</h2><span className="text-xs text-muted">{practicums.length} практикумов — {ready.length} собраны</span></div>
          <div className="mt-3 grid gap-3 xl:grid-cols-2">
            {practicumSections.map((section) => {
              const items = practicums.filter((practicum) => practicum.section === section.id)
              return <section key={section.id} className="border border-line"><header className="flex items-center justify-between border-b border-line bg-surface px-3 py-2"><h3 className="m-0 text-sm font-medium">{section.id} — {section.title}</h3><span className="font-mono text-[11px] text-muted">{items.length}</span></header><div className="grid sm:grid-cols-2">{items.map((practicum) => <button key={practicum.id} className="flex min-h-14 cursor-pointer items-center gap-2 border-b border-line px-3 py-2 text-left text-sm last:border-b-0 even:sm:border-l hover:bg-primary-soft" type="button" onClick={() => open(practicum.id)}><span className={`size-2 rounded-full ${practicum.status === 'ready' ? 'bg-verified' : 'bg-line-strong'}`} /><span className="min-w-0"><span className="mr-1 font-mono text-[11px] text-muted">{practicum.id}</span>{practicum.title}</span></button>)}</div></section>
            })}
          </div>
        </section>
      </div>
    </main>
  )
}

function BrowserPracticum({ practicum, progress, onProgress, onBack, onOpenAtlas }: { practicum: Practicum; progress: Progress; onProgress: (progress: Progress) => void; onBack: () => void; onOpenAtlas: (topic: string) => void }) {
  const [tab, setTab] = useState<PlayerTab>(progress.completed.length ? 'practice' : 'route')
  const active = Math.min(progress.active, c3Exercises.length - 1)
  const exercise = c3Exercises[active]!
  const skills = practicum.skills ?? []
  const completeExercise = () => {
    const completed = progress.completed.includes(exercise.id) ? progress.completed : [...progress.completed, exercise.id]
    onProgress({ ...progress, completed, active: Math.min(active + 1, c3Exercises.length - 1) })
  }
  const selectExercise = (index: number) => { onProgress({ ...progress, active: index }); setTab(index === c3Exercises.length - 1 ? 'exam' : 'practice') }

  return (
    <main id="practicums" className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto w-full max-w-300 px-4 py-6 max-[680px]:px-3">
        <button className="mb-5 cursor-pointer border-0 bg-transparent p-0 text-sm text-muted hover:text-ink" type="button" onClick={onBack}>← Все практикумы</button>
        <header className="border border-line bg-surface p-5 sm:p-6">
          <div className="flex flex-wrap items-start justify-between gap-4"><div><p className="m-0 font-mono text-[11px] tracking-[0.1em] text-primary uppercase">C — Геометрия и тригонометрия</p><h1 className="mt-2 mb-2 text-3xl leading-tight font-semibold tracking-[-0.03em]">{practicum.title}</h1><p className="m-0 max-w-165 leading-relaxed text-muted">Научись видеть форму уравнения до первого преобразования — и не теряй корни на области.</p></div><div className="border border-line bg-canvas px-3 py-2 text-right"><strong className="block text-xl tabular-nums">{progress.completed.length}/{c3Exercises.length}</strong><span className="text-[11px] text-muted">решено в браузере</span></div></div>
          <div className="mt-5 h-1.5 overflow-hidden bg-line"><motion.div className="h-full bg-verified" animate={{ width: `${progress.completed.length / c3Exercises.length * 100}%` }} /></div>
        </header>

        <PracticumIntroduction />

        <nav className="mt-5 flex overflow-x-auto border-b border-line" aria-label="Разделы практикума">
          <TabButton active={tab === 'route'} onClick={() => setTab('route')}>Маршрут</TabButton>
          <TabButton active={tab === 'practice'} onClick={() => setTab('practice')}>Практика — {progress.completed.length}/{c3Exercises.length - 1}</TabButton>
          <TabButton active={tab === 'exam'} onClick={() => { setTab('exam'); selectExercise(c3Exercises.length - 1) }}>Таймер</TabButton>
        </nav>

        {tab === 'route' && <RouteView skills={skills} completed={progress.completed} onStart={() => setTab('practice')} />}
        {tab !== 'route' && <section className="mt-5 grid gap-5 xl:grid-cols-[230px_minmax(0,1fr)]">
          <ExerciseRail exercises={c3Exercises} active={active} completed={progress.completed} onSelect={selectExercise} />
          <ExerciseCard exercise={exercise} index={active} exam={tab === 'exam'} onComplete={completeExercise} onNext={() => selectExercise(Math.min(active + 1, c3Exercises.length - 1))} />
        </section>}

        <footer className="mt-8 flex flex-wrap gap-3 border-t border-line pt-5 text-sm"><a className="min-h-9 border border-line-strong px-3 py-2 hover:bg-surface" href={`/${practicum.notebook}`} download>Скачать полный ноутбук</a><button className="min-h-9 cursor-pointer border border-line-strong bg-canvas px-3 hover:bg-surface" type="button" onClick={() => onOpenAtlas(practicum.topics[0]!)}>Посмотреть весь корпус в Atlas</button></footer>
      </div>
    </main>
  )
}

function PracticumIntroduction() {
  return <section className="mt-5 border border-line bg-surface/45" aria-labelledby="practicum-introduction-title">
    <div className="border-b border-line bg-canvas px-4 py-3 sm:px-5"><p className="m-0 font-mono text-[11px] tracking-[0.1em] text-primary uppercase">Перед началом</p><h2 id="practicum-introduction-title" className="mt-1 mb-0 text-lg font-semibold">Как устроен этот практикум</h2></div>
    <div className="grid gap-5 p-4 sm:p-5 lg:grid-cols-[minmax(0,1.15fr)_minmax(0,.85fr)]">
      <div className="space-y-3 leading-relaxed text-muted">
        <p className="mt-0 mb-0">Тригонометрические уравнения почти не требуют калькулятора: 23 из 31 отобранного блока — Paper 1. Баллы здесь теряются обычно не на тождестве, а на одном и том же: найден один корень, а остальные не попали в ответ.</p>
        <p className="m-0">Лестница идёт от опорного угла и составного аргумента к двойному углу, разложению на множители и отбору посторонних решений. Главный вопрос до вычислений: <strong className="text-ink">сколько функций и сколько разных аргументов стоит в уравнении?</strong> Цель — свести оба числа к одному.</p>
        <p className="m-0">Все задания — реальные вопросы AA HL из May 2021 — November 2025. Проверка принимает эквивалентные записи вроде <MathText>{'$\\pi/6$'}</MathText> и десятичного приближения, но отдельно проверяет, что не потеряны другие корни на области.</p>
      </div>
      <aside className="border border-line bg-canvas p-4"><h3 className="mt-0 mb-3 text-sm font-semibold">Как проходить</h3><ol className="m-0 space-y-2 pl-4 text-sm leading-relaxed text-muted"><li>Открой «Маршрут» и прочитай триггеры приёмов.</li><li>Решай каждую задачу на бумаге до ввода ответа.</li><li>Используй подсказку только после собственной попытки.</li><li>Финальное задание открывай по таймеру и повтори через неделю.</li></ol><p className="mt-4 mb-0 border-t border-line pt-3 text-xs leading-relaxed text-muted">Уровни: 🟢 чистый приём — 🟡 неочевидная обёртка — 🔴 комбинация приёмов или экзаменационный формат.</p></aside>
    </div>
  </section>
}

function RouteView({ skills, completed, onStart }: { skills: PracticumSkill[]; completed: string[]; onStart: () => void }) {
  return <section className="mt-5 grid gap-5 xl:grid-cols-[minmax(0,1fr)_300px]"><div className="border border-line p-4 sm:p-5"><p className="m-0 text-sm leading-relaxed text-muted">Сначала опознай форму. Следующий приём всегда расширяет предыдущий — не нужно выбирать из всей тригонометрии сразу.</p><ol className="mt-5 grid list-none gap-2 p-0">{skills.map((skill, index) => <li key={skill.id} className="grid grid-cols-[auto_minmax(0,1fr)] gap-3 border border-line bg-surface p-3"><span className="grid size-7 place-items-center rounded-full border border-line-strong font-mono text-[11px] text-muted">{index + 1}</span><div><strong className="block">{skill.name}</strong><p className="mt-1 mb-2 text-sm leading-relaxed text-muted">Триггер: {skill.trigger}</p><span className="font-mono text-[10.5px] text-muted">GDC: {calculatorLabel(skill.calculator)}</span></div></li>)}</ol></div><aside className="h-fit border border-primary/30 bg-primary-soft p-4"><p className="m-0 font-mono text-[11px] text-primary uppercase">Как проходить</p><ol className="mt-3 mb-5 space-y-2 pl-4 text-sm leading-relaxed"><li>Решай на бумаге.</li><li>Вводи только финальный набор корней.</li><li>Открывай подсказку лишь после своей попытки.</li><li>Вернись к финалу через неделю.</li></ol><button className="min-h-10 w-full cursor-pointer border border-primary bg-primary px-3 font-medium text-white hover:bg-primary-dark" type="button" onClick={onStart}>{completed.length ? 'Продолжить практику' : 'Начать с первого задания'}</button></aside></section>
}

function ExerciseRail({ exercises, active, completed, onSelect }: { exercises: BrowserExercise[]; active: number; completed: string[]; onSelect: (index: number) => void }) {
  return <aside className="h-fit border border-line bg-surface"><div className="border-b border-line px-3 py-2.5"><h2 className="m-0 text-sm font-semibold">Лестница заданий</h2></div><ol className="m-0 list-none p-0">{exercises.map((item, index) => <li key={item.id}><button className={`flex w-full cursor-pointer items-center gap-2 border-0 border-b border-line px-3 py-2.5 text-left text-xs last:border-b-0 hover:bg-primary-soft ${index === active ? 'bg-primary-soft' : ''}`} type="button" onClick={() => onSelect(index)}><span className={`grid size-5 shrink-0 place-items-center rounded-full border font-mono text-[10px] ${completed.includes(item.id) ? 'border-verified bg-verified text-white' : 'border-line-strong text-muted'}`}>{completed.includes(item.id) ? '✓' : index + 1}</span><span className="min-w-0"><span className="mr-1">{item.level}</span>{item.title}</span></button></li>)}</ol></aside>
}

function ExerciseCard({ exercise, index, exam, onComplete, onNext }: { exercise: BrowserExercise; index: number; exam: boolean; onComplete: () => void; onNext: () => void }) {
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<'correct' | 'incorrect' | null>(null)
  const [hint, setHint] = useState(false)
  const [solution, setSolution] = useState(false)
  const [seconds, setSeconds] = useState(0)
  const [running, setRunning] = useState(false)
  const [started, setStarted] = useState(false)

  useEffect(() => { setAnswer(''); setResult(null); setHint(false); setSolution(false); setSeconds(0); setRunning(false); setStarted(false) }, [exercise.id])
  useEffect(() => {
    if (!running) return
    const timer = window.setInterval(() => setSeconds((value) => value + 1), 1000)
    return () => window.clearInterval(timer)
  }, [running])

  const check = () => {
    const values = parseAnswer(answer)
    const expected = [...exercise.expected].sort((a, b) => a - b)
    const valid = values.length === expected.length && values.every((value, position) => Math.abs(value - expected[position]!) < 1e-6)
    setResult(valid ? 'correct' : 'incorrect')
    if (valid) onComplete()
  }
  const time = `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`
  const beginTimer = () => { setStarted(true); setRunning(true) }

  return (
    <article className="border border-line bg-surface">
      <header className="flex flex-wrap items-start justify-between gap-3 border-b border-line bg-canvas p-4 sm:p-5">
        <div><p className="m-0 font-mono text-[11px] text-primary">{exercise.level} — Шаг {index + 1} — {exercise.skillId}</p><h2 className="mt-1 mb-0 text-xl leading-tight font-semibold">{exercise.title}</h2></div>
        <span className="border border-line px-2 py-1 font-mono text-[10.5px] text-muted">{exercise.unit === 'degrees' ? 'ответ в градусах' : 'ответ в радианах'}</span>
      </header>
      <div className="p-4 sm:p-5">
        <div className="relative">
          <div className={exam && !started ? 'pointer-events-none select-none blur-[7px] opacity-45' : ''} aria-hidden={exam && !started}>
            <div className="max-w-165 text-[16px] leading-relaxed"><MathText>{exercise.prompt}</MathText></div>
            <p className="mt-4 mb-0 text-xs text-muted">Источник: {exercise.source}</p>
          </div>
          {exam && !started && <div className="absolute inset-0 grid place-items-center bg-surface/45 backdrop-blur-[2px]"><div className="max-w-85 p-4 text-center"><p className="m-0 text-sm leading-relaxed">Условие откроется только вместе с таймером. Решай без подсказок и не останавливайся на первом корне.</p><button className="mt-4 min-h-10 cursor-pointer border border-primary bg-primary px-4 font-medium text-white hover:bg-primary-dark" type="button" onClick={beginTimer}>Начать таймер</button></div></div>}
        </div>

        {exam && started && <div className="mt-5 flex items-center justify-between border border-primary/30 bg-primary-soft p-3"><span className="text-sm">Финальное задание: решай с закрытыми подсказками.</span><button className="cursor-pointer border border-primary bg-canvas px-2.5 py-1 text-sm" type="button" onClick={() => setRunning((value) => !value)}>{running ? 'Пауза' : 'Продолжить'} — {time}</button></div>}

        {(!exam || started) && <>
          <div className="mt-6 border-t border-line pt-5"><label className="block text-sm font-medium" htmlFor={`answer-${exercise.id}`}>{exercise.answerMode === 'roots' ? 'Все корни' : 'Значение'}</label><p className="mt-1 mb-2 text-xs text-muted">Вводи через запятую. Поддерживаются `pi`, `π`, десятичные дроби и операции: например `pi/6, 5*pi/6`.</p><div className="flex flex-col gap-2 sm:flex-row"><input id={`answer-${exercise.id}`} className="min-h-10 min-w-0 flex-1 border border-line-strong bg-canvas px-3 font-mono text-sm outline-none focus:border-primary" value={answer} onChange={(event) => setAnswer(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter') check() }} placeholder={exercise.answerMode === 'roots' ? 'pi/6, 5*pi/6' : '17*pi/6'} /><button className="min-h-10 cursor-pointer border border-primary bg-primary px-4 font-medium text-white hover:bg-primary-dark" type="button" onClick={check}>Проверить</button></div>{result && <div className={`mt-3 border p-3 text-sm ${result === 'correct' ? 'border-verified/40 bg-verified-soft text-verified' : 'border-primary/30 bg-primary-soft text-ink'}`}>{result === 'correct' ? '✓ Верно. Все требуемые значения найдены.' : 'Пока не сходится. Проверь область, число корней и формат ответа.'}</div>}</div>
          <div className="mt-5 flex flex-wrap gap-2"><button className="min-h-8 cursor-pointer border border-line-strong bg-canvas px-3 text-sm hover:bg-surface-strong" type="button" onClick={() => setHint((value) => !value)}>{hint ? 'Скрыть подсказку' : 'Нужна подсказка'}</button><button className="min-h-8 cursor-pointer border border-line-strong bg-canvas px-3 text-sm hover:bg-surface-strong" type="button" onClick={() => setSolution(true)}>Показать решение</button>{result === 'correct' && index < c3Exercises.length - 1 && <button className="min-h-8 cursor-pointer border border-verified bg-verified px-3 text-sm text-white" type="button" onClick={onNext}>Следующее задание →</button>}</div>
          {hint && <div className="mt-3 border-l-3 border-primary bg-primary-soft p-3 text-sm leading-relaxed"><strong>Подсказка.</strong> <MathText>{exercise.hint}</MathText></div>}
          {solution && <div className="mt-3 border-l-3 border-line-strong bg-canvas p-3 text-sm leading-relaxed"><strong>Ход решения.</strong> <MathText>{exercise.solution}</MathText></div>}
        </>}
      </div>
    </article>
  )
}

function PlannedPracticum({ practicum, onBack, onOpenAtlas }: { practicum: Practicum; onBack: () => void; onOpenAtlas: (topic: string) => void }) {
  return <main id="practicums" className="min-h-0 flex-1 overflow-y-auto bg-canvas"><div className="mx-auto max-w-190 px-4 py-7"><button className="mb-5 cursor-pointer border-0 bg-transparent p-0 text-sm text-muted hover:text-ink" type="button" onClick={onBack}>← Все практикумы</button><section className="border border-line p-5"><p className="m-0 font-mono text-[11px] text-primary">{practicum.id} — {practicum.sectionTitle}</p><h1 className="mt-2 mb-2 text-2xl font-semibold">{practicum.title}</h1><p className="m-0 leading-relaxed text-muted">Карта и границы темы готовы. Браузерная лестница появится после отбора заданий, карточек приёмов и проверок — не раньше.</p><button className="mt-5 min-h-9 cursor-pointer border border-line-strong bg-canvas px-3 hover:bg-surface" type="button" onClick={() => onOpenAtlas(practicum.topics[0]!)}>Посмотреть исходный корпус в Atlas</button></section></div></main>
}

function TabButton({ active, children, onClick }: { active: boolean; children: React.ReactNode; onClick: () => void }) {
  return <button className={`min-h-10 cursor-pointer border-0 border-b-2 px-3 text-sm ${active ? 'border-primary text-ink' : 'border-transparent text-muted hover:text-ink'}`} type="button" onClick={onClick}>{children}</button>
}

function parseAnswer(value: string): number[] {
  return value.split(/[;,]/).map((item) => item.trim()).filter(Boolean).map((item) => {
    const expression = item.replaceAll('π', 'pi').replace(/\bpi\b/gi, 'Math.PI')
    if (!/^[0-9+*/().\sMathPI-]+$/.test(expression)) return Number.NaN
    try { return Function(`"use strict"; return (${expression})`)() as number } catch { return Number.NaN }
  }).filter(Number.isFinite).sort((a, b) => a - b)
}
