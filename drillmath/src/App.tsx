/** Тренажёр «Приём»: узнать приём по настоящему вопросу архива.
 *
 * Отдельный сайт, а не вкладка атласа: занятие здесь одно, и экран под
 * него устроен целиком — слева страница билета, справа каталог приёмов.
 * Служба та же, что у атласа (ib-drill), поэтому журнал, расписание и
 * сила приёмов общие: занятие, начатое здесь, видно и там.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api, type Card, type Catalogue as CatalogueData, type Setup, type Verdict as Result } from './api'
import { Catalogue } from './components/Catalogue'
import { QuestionCard } from './components/QuestionCard'
import { Verdict } from './components/Verdict'

type Screen = 'start' | 'running' | 'done'

interface Done {
  reference: string
  ok: boolean
  near: boolean
  skill: string
  skillName: string
  picked: string | null
  pickedName: string | null
  ms: number
}

const LENGTHS = [10, 20, 40, 0]
const KEY = 'drillmath.settings.v1'

interface Settings {
  length: number
  topics: string[]
  named: boolean
}

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(KEY)
    if (raw) {
      const saved = JSON.parse(raw) as Partial<Settings>
      return {
        length: typeof saved.length === 'number' ? saved.length : 20,
        topics: Array.isArray(saved.topics) ? saved.topics : [],
        named: Boolean(saved.named),
      }
    }
  } catch { /* не беда */ }
  return { length: 20, topics: [], named: false }
}

function seconds(ms: number) {
  const total = Math.round(ms / 1000)
  return total < 60 ? `${total} с` : `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`
}

export function App() {
  const [screen, setScreen] = useState<Screen>('start')
  const [settings, setSettings] = useState<Settings>(loadSettings)
  const [setup, setSetup] = useState<Setup | null>(null)
  const [catalogue, setCatalogue] = useState<CatalogueData | null>(null)
  const [card, setCard] = useState<Card | null>(null)
  const [chosen, setChosen] = useState<string | null>(null)
  const [result, setResult] = useState<Result | null>(null)
  const [done, setDone] = useState<Done[]>([])
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [pickTopics, setPickTopics] = useState(false)

  const shownAt = useRef(0)
  const firstMoveAt = useRef(0)
  const seenSkills = useRef<string[]>([])
  const seenBlocks = useRef<string[]>([])

  useEffect(() => { try { localStorage.setItem(KEY, JSON.stringify(settings)) } catch { /* не беда */ } },
    [settings])

  useEffect(() => {
    Promise.all([api.setup(), api.catalogue()])
      .then(([one, two]) => { setSetup(one); setCatalogue(two) })
      .catch((failure: unknown) => setError(failure instanceof Error ? failure.message : 'служба молчит'))
  }, [])

  useEffect(() => {
    if (screen !== 'running' || !card || result) return
    const timer = window.setInterval(() => setElapsed(performance.now() - shownAt.current), 200)
    return () => window.clearInterval(timer)
  }, [card, result, screen])

  const pull = useCallback(async () => {
    setBusy(true)
    setError(null)
    try {
      const next = await api.next({
        topics: settings.topics,
        named: settings.named,
        avoid: seenSkills.current.slice(-6),
      })
      setCard(next)
      setChosen(null)
      setResult(null)
      shownAt.current = performance.now()
      firstMoveAt.current = 0
      setElapsed(0)
      seenBlocks.current = [...seenBlocks.current, next.block].slice(-40)
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не вышло взять вопрос')
    } finally {
      setBusy(false)
    }
  }, [settings.named, settings.topics])

  const start = useCallback(() => {
    setDone([])
    seenSkills.current = []
    seenBlocks.current = []
    setScreen('running')
    void pull()
  }, [pull])

  const submit = useCallback(async (skill: string) => {
    if (!card || busy || result) return
    setBusy(true)
    const ms = Math.round(performance.now() - shownAt.current)
    const first = Math.round((firstMoveAt.current || performance.now()) - shownAt.current)
    try {
      const verdict = await api.answer({ item: card.item, answer: skill, ms, first_ms: first })
      setResult(verdict)
      seenSkills.current = [...seenSkills.current, verdict.skill].slice(-6)
      setDone((current) => [...current, {
        reference: card.reference,
        ok: verdict.ok,
        near: Boolean(verdict.picked?.near),
        skill: verdict.skill,
        skillName: verdict.skill_name,
        picked: verdict.picked?.skill ?? null,
        pickedName: verdict.picked?.name ?? null,
        ms,
      }])
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'ответ не ушёл')
    } finally {
      setBusy(false)
    }
  }, [busy, card, result])

  const advance = useCallback(() => {
    if (settings.length > 0 && done.length >= settings.length) {
      setScreen('done')
      return
    }
    void pull()
  }, [done.length, pull, settings.length])

  useEffect(() => {
    if (screen !== 'running') return
    const onKey = (event: KeyboardEvent) => {
      const typing = event.target instanceof HTMLElement
        && ['INPUT', 'TEXTAREA'].includes(event.target.tagName)
      if (result && (event.key === 'Enter' || event.key === ' ')) {
        event.preventDefault()
        advance()
        return
      }
      if (!result && !typing && event.key === 'Enter' && chosen) {
        event.preventDefault()
        void submit(chosen)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [advance, chosen, result, screen, submit])

  const markMove = useCallback(() => {
    if (!firstMoveAt.current) firstMoveAt.current = performance.now()
  }, [])

  const cards = useMemo(
    () => (setup?.practicums ?? []).reduce((sum, topic) => sum + (topic.pick ?? 0), 0),
    [setup])

  const chosenName = useMemo(
    () => catalogue?.skills.find((skill) => skill.id === chosen)?.name ?? null,
    [catalogue, chosen])

  const correct = done.filter((row) => row.ok).length

  // ------------------------------------------------------------------ шапка
  const bar = (
    <header className="sticky top-0 z-30 border-b border-line bg-canvas/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-[1400px] items-center gap-4 px-4">
        <span className="text-[15px] font-medium tracking-tight text-ink">Приём</span>
        {screen === 'running' && (
          <>
            <span className="font-mono text-[13px] text-muted">
              {done.length}{settings.length > 0 ? ` / ${settings.length}` : ''}
            </span>
            <div className="hidden h-1 flex-1 overflow-hidden rounded-full bg-sunken sm:block">
              <div
                className="h-full rounded-full bg-accent transition-[width] duration-300"
                style={{ width: settings.length > 0
                  ? `${Math.min(100, (done.length / settings.length) * 100)}%`
                  : '0%' }}
              />
            </div>
            <span className={`ml-auto font-mono text-[13px] ${
              card && elapsed > card.budget_ms ? 'text-near' : 'text-faint'}`}>
              {seconds(elapsed)}
            </span>
            <button
              type="button"
              className="cursor-pointer text-[13px] text-muted hover:text-ink"
              onClick={() => setScreen(done.length ? 'done' : 'start')}
            >
              закончить
            </button>
          </>
        )}
        {screen !== 'running' && (
          <span className="ml-auto text-[13px] text-faint">IB Mathematics AA HL</span>
        )}
      </div>
    </header>
  )

  // ------------------------------------------------------------------ начало
  if (screen === 'start') {
    const sections = setup?.sections ?? []
    return (
      <div className="min-h-dvh">
        {bar}
        <main className="mx-auto flex max-w-2xl flex-col gap-8 px-4 py-10 sm:py-16">
          <div className="flex flex-col gap-3">
            <h1 className="text-[28px] leading-tight font-semibold tracking-tight text-ink sm:text-[34px]">
              Узнать приём по вопросу
            </h1>
            <p className="text-[17px] leading-relaxed text-muted">
              На карточке — настоящая страница билета IB. Решать не нужно: нужно
              назвать приём, которым этот пункт берётся, и найти его в каталоге.
              На экзамене это и есть самая дорогая часть работы: вопрос приходит
              без подписи, из какой он темы.
            </p>
            {setup && (
              <p className="text-[13px] text-faint">
                {cards} карточек · {catalogue?.skills.length ?? 0} приёмов · {setup.practicums.length} тем
              </p>
            )}
          </div>

          {error && (
            <p className="rounded-xl border border-miss bg-miss-soft px-4 py-3 text-[14px] text-ink">
              Тренажёр не отвечает: {error}
            </p>
          )}

          <div className="flex flex-col gap-3">
            <p className="text-[12px] font-medium tracking-wide text-faint uppercase">сколько вопросов</p>
            <div className="flex flex-wrap gap-2">
              {LENGTHS.map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setSettings((current) => ({ ...current, length: value }))}
                  className={`h-10 cursor-pointer rounded-xl border px-4 text-[15px] transition-colors ${
                    settings.length === value
                      ? 'border-accent bg-accent-soft text-ink'
                      : 'border-line bg-surface text-muted hover:text-ink'
                  }`}
                >
                  {value === 0 ? 'без конца' : value}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-3">
            <div className="flex items-baseline justify-between gap-3">
              <p className="text-[12px] font-medium tracking-wide text-faint uppercase">темы</p>
              <button
                type="button"
                className="cursor-pointer text-[13px] text-accent hover:underline"
                onClick={() => setPickTopics((current) => !current)}
              >
                {pickTopics ? 'свернуть' : settings.topics.length ? 'изменить' : 'выбрать'}
              </button>
            </div>
            <p className="text-[15px] text-muted">
              {settings.topics.length === 0
                ? 'Все темы вперемешку — так же, как на экзамене.'
                : `Выбрано ${settings.topics.length}: ${settings.topics.join(', ')}`}
            </p>
            {pickTopics && setup && (
              <div className="flex flex-col gap-4 rounded-xl border border-line bg-surface p-4 shadow-card">
                {sections.map((section) => (
                  <div key={section.id} className="flex flex-col gap-2">
                    <p className="text-[12px] font-medium tracking-wide text-faint uppercase">{section.title}</p>
                    <div className="flex flex-wrap gap-1.5">
                      {setup.practicums.filter((topic) => topic.section === section.id).map((topic) => {
                        const on = settings.topics.includes(topic.id)
                        const empty = !topic.pick
                        return (
                          <button
                            key={topic.id}
                            type="button"
                            disabled={empty}
                            title={`${topic.title} · ${topic.pick} карточек`}
                            onClick={() => setSettings((current) => ({
                              ...current,
                              topics: on
                                ? current.topics.filter((id) => id !== topic.id)
                                : [...current.topics, topic.id],
                            }))}
                            className={`h-8 cursor-pointer rounded-lg border px-2.5 font-mono text-[12px] transition-colors disabled:cursor-default disabled:opacity-40 ${
                              on ? 'border-accent bg-accent-soft text-ink' : 'border-line bg-surface text-muted hover:text-ink'
                            }`}
                          >
                            {topic.id}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                ))}
                {settings.topics.length > 0 && (
                  <button
                    type="button"
                    className="w-fit cursor-pointer text-[13px] text-accent hover:underline"
                    onClick={() => setSettings((current) => ({ ...current, topics: [] }))}
                  >
                    снять все
                  </button>
                )}
              </div>
            )}
          </div>

          <label className="flex cursor-pointer items-start gap-3">
            <input
              type="checkbox"
              checked={settings.named}
              onChange={(event) => setSettings((current) => ({ ...current, named: event.target.checked }))}
              className="mt-1 size-4 accent-[var(--c-accent)]"
            />
            <span className="flex flex-col gap-0.5">
              <span className="text-[15px] text-ink">давать и те, где метод назван в условии</span>
              <span className="text-[13px] text-faint">
                «Use Euler’s method with a step of 0.1» — узнавать там нечего,
                поэтому обычно такие вопросы не идут. Их 247 из 1267.
              </span>
            </span>
          </label>

          <button
            type="button"
            disabled={!setup || !catalogue}
            onClick={start}
            className="h-12 w-full cursor-pointer rounded-xl bg-accent text-[16px] font-medium text-surface transition-opacity hover:opacity-90 disabled:cursor-default disabled:opacity-50 sm:w-fit sm:px-8"
          >
            начать
          </button>
        </main>
      </div>
    )
  }

  // ------------------------------------------------------------------- итог
  if (screen === 'done') {
    const wrong = done.filter((row) => !row.ok)
    const total = done.reduce((sum, row) => sum + row.ms, 0)
    return (
      <div className="min-h-dvh">
        {bar}
        <main className="mx-auto flex max-w-2xl flex-col gap-8 px-4 py-10 sm:py-16">
          <div className="flex flex-col gap-2">
            <h1 className="text-[28px] leading-tight font-semibold tracking-tight text-ink">
              {correct} из {done.length}
            </h1>
            <p className="text-[15px] text-muted">
              {done.length ? `${seconds(total / Math.max(done.length, 1))} на вопрос · ${seconds(total)} всего` : 'ни одного вопроса'}
            </p>
          </div>

          {wrong.length > 0 && (
            <div className="flex flex-col gap-3">
              <p className="text-[12px] font-medium tracking-wide text-faint uppercase">что с чем слиплось</p>
              <ul className="flex flex-col divide-y divide-line overflow-hidden rounded-xl border border-line bg-surface shadow-card">
                {wrong.map((row, index) => (
                  <li key={`${row.reference}-${index}`} className="flex flex-col gap-1 px-4 py-3">
                    <span className="text-[15px] text-ink">
                      {row.pickedName
                        ? <>назвали «{row.pickedName}» вместо «{row.skillName}»</>
                        : <>не назвали «{row.skillName}»</>}
                    </span>
                    <span className="flex items-baseline gap-2 text-[12px] text-faint">
                      <span>{row.reference}</span>
                      {row.near && <span className="text-near">схема этот ход упоминает</span>}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={start}
              className="h-12 cursor-pointer rounded-xl bg-accent px-6 text-[16px] font-medium text-surface hover:opacity-90"
            >
              ещё раз
            </button>
            <button
              type="button"
              onClick={() => setScreen('start')}
              className="h-12 cursor-pointer rounded-xl border border-line bg-surface px-6 text-[16px] text-muted hover:text-ink"
            >
              к настройкам
            </button>
          </div>
        </main>
      </div>
    )
  }

  // ---------------------------------------------------------------- занятие
  return (
    <div className="min-h-dvh">
      {bar}
      <main className="mx-auto grid max-w-[1400px] gap-6 px-4 py-6 lg:grid-cols-[minmax(0,1.1fr)_minmax(0,1fr)] lg:py-8">
        {error && (
          <p className="rounded-xl border border-miss bg-miss-soft px-4 py-3 text-[14px] text-ink lg:col-span-2">
            {error}
          </p>
        )}

        {card ? <QuestionCard card={card} /> : (
          <div className="h-64 animate-pulse rounded-2xl border border-line bg-surface" />
        )}

        <div
          className="flex min-h-0 flex-col gap-3 lg:sticky lg:top-20 lg:h-[calc(100dvh-7rem)]"
          onPointerDown={markMove}
        >
          {result ? (
            <Verdict
              result={result}
              last={settings.length > 0 && done.length >= settings.length}
              onNext={advance}
            />
          ) : catalogue ? (
            <>
              <Catalogue
                data={catalogue}
                chosen={chosen}
                disabled={busy}
                onChoose={setChosen}
                onSubmit={(skill) => void submit(skill)}
              />
              {/* Кнопка держится у нижнего края экрана: на телефоне до неё
                  иначе нужно доскроллить мимо каталога. Список выше
                  ограничен по высоте, поэтому она ничего не закрывает. */}
              <div className="sticky bottom-0 z-20 flex shrink-0 items-center gap-3 rounded-xl border border-line bg-surface p-2.5 pb-[max(0.625rem,env(safe-area-inset-bottom))] shadow-card lg:pb-2.5">
                <span className="min-w-0 flex-1 truncate text-[14px] text-muted">
                  {chosenName ?? 'выберите приём в каталоге'}
                </span>
                <button
                  type="button"
                  disabled={!chosen || busy}
                  onClick={() => chosen && void submit(chosen)}
                  className="h-11 shrink-0 cursor-pointer rounded-xl bg-accent px-5 text-[15px] font-medium text-surface transition-opacity hover:opacity-90 disabled:cursor-default disabled:opacity-40"
                >
                  ответить
                </button>
              </div>
            </>
          ) : (
            <div className="h-64 animate-pulse rounded-2xl border border-line bg-surface" />
          )}
        </div>
      </main>
    </div>
  )
}
