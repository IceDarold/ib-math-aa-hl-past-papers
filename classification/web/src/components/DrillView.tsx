import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { motion } from 'motion/react'
import { practicumSections } from '../data/practicums'
import { MathText } from './MathText'
import { WriteUpVerdict, type Verdict as WriteUp } from './WriteUpVerdict'
import { EveningView, type Evening, type EveningTheme } from './EveningView'

type Mode = 'mixed' | 'recognition' | 'compute' | 'written'
type Order = 'schedule' | 'ladder' | 'random'
type Screen = 'setup' | 'running' | 'done' | 'history' | 'map' | 'evening'

interface Option { code: string; name: string }

interface Item {
  item: string
  kind: 'recognition' | 'compute' | 'written'
  block?: string
  reference?: string
  marks?: number
  calculator?: string
  pages?: number
  skill: string
  skill_name: string
  trigger: string
  practicum: string
  practicum_title: string
  prompt: string
  note?: string
  options?: Option[]
  archive_marks?: [number, number] | null
  budget_ms: number
}

interface Verdict {
  ok: boolean
  message: string
  skill: string
  skill_name: string
  trigger: string
  chain: string[]
  traps: string[]
  practicum: string
  answer: string
}

interface WrittenBlock {
  practicum: string
  paper: number | null
  marks: number | null
}

interface SetupPracticum {
  id: string
  title: string
  section: string
  marks: number | null
  skills: number
  recognition: number
  compute: number
  written: number
  share: number
}

interface SkillStat {
  id: string
  practicum: string
  name: string
  rung: number
  seen: number
  wrong: number
  score: number | null
  stability: number | null
  retrievability: number | null
  difficulty: number | null
  days_since: number | null
  due_in_days: number | null
  has_compute: boolean
}

interface StrengthSkill extends SkillStat {
  marks: number
}

interface StrengthPracticum {
  id: string
  title: string
  skills: number
  started: number
  marks: number
  score: number | null
  due: number
}

interface Strength {
  skills: StrengthSkill[]
  practicums: StrengthPracticum[]
  horizon: number
}

interface WrittenRow {
  id: number
  ts: number
  reference: string
  practicum: string
  skill: string
  available: number | null
  earned: number | null
  math: string
  model: string
  pages: number
}

interface WrittenRecord extends WrittenRow {
  verdict: WriteUp & { error?: string }
  files: { index: number; name: string; url: string }[]
}

interface SkillCard {
  id: string
  practicum: string
  practicum_title: string
  name: string
  rung: number
  calculator: string
  trigger: string
  chain: string[]
  traps: string[]
  recognition: { prompt: string; answer: string; options: { code: string; name: string }[] }[]
  compute: { prompt: string; note?: string; answer: string } | null
  archive: { block: string; reference: string; marks: number | null; paper: number | null; calculator: string | null; question_url: string }[]
  state: {
    seen: number
    wrong: number
    score: number | null
    stability: number | null
    difficulty: number | null
    days_since: number | null
    due_in_days: number | null
  } | null
}

// Все тринадцать значений calculator.mode из карточек приёмов, от «нужен»
// до «бесполезен». Незнакомое печаталось бы английским словом посреди
// русской строки, поэтому словарь сверяется с карточками в check_skills.py.
const CALCULATOR: Record<string, string> = {
  required: 'нужен',
  needed: 'нужен',
  replaces: 'заменяет ручной ход',
  speeds_up: 'ускоряет',
  helps: 'помогает',
  partial: 'берёт на себя часть хода',
  checks: 'только проверка',
  yes: 'разрешён',
  allowed: 'разрешён, но не нужен',
  mixed: 'где как',
  forbidden: 'не поможет',
  no: 'не поможет',
  none: 'бесполезен совсем',
}

interface Stats {
  skills: SkillStat[]
  totals: { attempts: number; correct: number; avg_ms: number; avg_first_ms: number; today: number; today_correct: number }
}

type MarksBand = 'any' | 'easy' | 'mid' | 'hard'

interface Settings {
  mode: Mode
  practicums: string[]
  papers: number[]
  marks: MarksBand
  length: number
  order: Order
  onlyDue: boolean
  showTimer: boolean
}

interface Done {
  skill: string
  skillName: string
  practicum: string
  kind: Item['kind']
  ok: boolean
  hint: boolean
  ms: number
  firstMs: number
  earned?: number
  available?: number
}

const API = '/api/drill'
/** Подпись части разбора: одна и та же во всех строках, чтобы их не путали. */
const LABEL = 'font-mono text-[10px] uppercase tracking-wide text-faint max-[560px]:pt-1.5'
const SETTINGS_KEY = 'question-atlas:drill-setup'

const MODES: { id: Mode; label: string; hint: string }[] = [
  { id: 'mixed', label: 'вперемешку', hint: 'И назвать приём, и решить — вразнобой' },
  { id: 'recognition', label: 'узнавание', hint: 'Только назвать приём. Считать не нужно' },
  { id: 'compute', label: 'счёт', hint: 'Только решить и ввести ответ' },
  { id: 'written', label: 'разбор', hint: 'Настоящий вопрос архива: решаешь на бумаге и прикрепляешь фото' },
]

const MAX_EDGE = 1600
const MAX_PHOTOS = 6

function isPdf(file: File) {
  return file.type === 'application/pdf' || /\.pdf$/i.test(file.name)
}

/** PDF уходит как есть: постранично его разберёт сервер, где уже есть PyMuPDF. */
function readAsIs(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('файл не прочитался'))
    reader.onload = () => resolve(String(reader.result))
    reader.readAsDataURL(file)
  })
}

/** Снимок с телефона весит мегабайты, модели нужно куда меньше. */
function shrink(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('файл не прочитался'))
    reader.onload = () => {
      const picture = new Image()
      picture.onerror = () => reject(new Error('это не изображение'))
      picture.onload = () => {
        const scale = Math.min(1, MAX_EDGE / Math.max(picture.width, picture.height))
        const canvas = document.createElement('canvas')
        canvas.width = Math.round(picture.width * scale)
        canvas.height = Math.round(picture.height * scale)
        const context = canvas.getContext('2d')
        if (!context) { reject(new Error('canvas недоступен')); return }
        context.drawImage(picture, 0, 0, canvas.width, canvas.height)
        resolve(canvas.toDataURL('image/jpeg', 0.85))
      }
      picture.src = String(reader.result)
    }
    reader.readAsDataURL(file)
  })
}

const ORDERS: { id: Order; label: string; hint: string }[] = [
  { id: 'schedule', label: 'по расписанию', hint: 'Что весит больше на экзамене, что просрочено и где ошибки' },
  { id: 'ladder', label: 'сплошь', hint: 'Подряд от простого к сложному, реже виденное вперёд' },
  { id: 'random', label: 'наугад', hint: 'Поровну, без всякого расписания' },
]

const LENGTHS = [10, 20, 40, 0]
// Разбор письменной работы — минуты на задание, десяток тут был бы вечером.
const WRITTEN_LENGTHS = [1, 3, 5, 0]
// Тренировка одного приёма с карточки. Длина из настроек тут ни при чём:
// её выбирали для смеси, а очередь по одному приёму держат короткой.
const FOCUS_LENGTH = 10

const MARKS: { id: MarksBand; label: string; range: [number, number | null] | null; hint: string }[] = [
  { id: 'any', label: 'любые', range: null, hint: 'Как выпадет' },
  { id: 'easy', label: '1–3', range: [1, 3], hint: 'Короткие: один ход и ответ' },
  { id: 'mid', label: '4–6', range: [4, 6], hint: 'Обычный вопрос на несколько пунктов' },
  { id: 'hard', label: '7+', range: [7, null], hint: 'Длинные, с разбором на полстраницы' },
]

const PAPERS: { id: number; hint: string }[] = [
  { id: 1, hint: 'Без калькулятора' },
  { id: 2, hint: 'С калькулятором' },
  { id: 3, hint: 'Длинные исследования' },
]

const DEFAULTS: Settings = {
  mode: 'mixed',
  practicums: [],
  papers: [],
  marks: 'any',
  length: 20,
  order: 'schedule',
  onlyDue: false,
  showTimer: true,
}

function loadSettings(): Settings {
  try {
    const stored = JSON.parse(localStorage.getItem(SETTINGS_KEY) ?? 'null') as unknown
    if (stored && typeof stored === 'object') return { ...DEFAULTS, ...stored as Partial<Settings> }
  } catch {
    /* настройки — удобство, а не данные */
  }
  return DEFAULTS
}

function saveSettings(settings: Settings) {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings))
  } catch {
    /* приватное окно, чистая история — не беда */
  }
}

function when(ts: number) {
  return new Date(ts * 1000).toLocaleString('ru-RU', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit',
  })
}

/** «1 балл», «3 балла», «5 баллов». */
function marksWord(count: number) {
  const last = count % 10
  const two = count % 100
  if (last === 1 && two !== 11) return 'балл'
  if (last >= 2 && last <= 4 && (two < 12 || two > 14)) return 'балла'
  return 'баллов'
}

/** Цена вопросов архива за приёмом: «3 балла» или «2–5 баллов». */
function price([low, high]: [number, number]) {
  return low === high
    ? `${low} ${marksWord(low)}`
    : `${low}–${high} ${marksWord(high)}`
}

function seconds(ms: number) {
  return `${(ms / 1000).toFixed(1)} с`
}

function minutes(ms: number) {
  const total = Math.round(ms / 1000)
  return total < 60 ? `${total} с` : `${Math.floor(total / 60)} мин ${String(total % 60).padStart(2, '0')} с`
}

/** Сколько заданий этой темы доступно в выбранном режиме. */
function available(practicum: SetupPracticum, mode: Mode) {
  if (mode === 'recognition') return practicum.recognition
  if (mode === 'compute') return practicum.compute
  if (mode === 'written') return practicum.written
  return practicum.recognition + practicum.compute
}

/** Ступень лестницы силы: один тон, светлота падает с ростом счёта. */
const HEAT = [
  'bg-heat-0 text-ink', 'bg-heat-1 text-ink', 'bg-heat-2 text-ink',
  'bg-heat-3 text-ink', 'bg-heat-4 text-ink', 'bg-heat-5 text-ink',
  'bg-heat-6 text-canvas',
]

const HEAT_EDGES = [15, 30, 45, 60, 75, 90]

function heatTone(score: number | null) {
  // «Ни разу» — не ноль: не начинали и забыли это разные болезни, и
  // отличаются они не оттенком, а пунктиром и точкой вместо числа.
  if (score === null) return 'border-dashed border-line-strong bg-surface text-faint'
  let step = 0
  while (step < HEAT_EDGES.length && score >= (HEAT_EDGES[step] as number)) step += 1
  return `border-solid border-line ${HEAT[step]}`
}

/** Строка под картой: что за квадратом, на который навели. */
function heatRead(skill: StrengthSkill | null, horizon: number) {
  if (!skill) return `Наведите на квадрат. Счёт — свежесть, помноженная на глубину; сто означает приём, который держится ${Math.round(horizon)} дней.`
  if (skill.score === null) {
    return `${skill.practicum} · ${skill.name} — ни одной попытки${skill.marks ? `, за приёмом ${skill.marks} баллов архива` : ''}.`
  }
  const due = skill.due_in_days === null ? ''
    : skill.due_in_days <= 0 ? ', срок подошёл'
    : `, повторить через ${Math.round(skill.due_in_days)} дн.`
  return `${skill.practicum} · ${skill.name} — ${skill.score}, держится ${skill.stability} дн., последний раз ${skill.days_since === 0 ? 'сегодня' : `${skill.days_since} дн. назад`}${due}. Показов ${skill.seen}, мимо ${skill.wrong}.`
}

export function DrillView() {
  const [screen, setScreen] = useState<Screen>('setup')
  const [settings, setSettings] = useState<Settings>(loadSettings)
  const [setup, setSetup] = useState<SetupPracticum[] | null>(null)
  const [blocks, setBlocks] = useState<WrittenBlock[]>([])
  const [stats, setStats] = useState<Stats | null>(null)
  const [strength, setStrength] = useState<Strength | null>(null)
  const [hovered, setHovered] = useState<StrengthSkill | null>(null)
  const [asList, setAsList] = useState(false)
  const [evening, setEvening] = useState<Evening | null>(null)
  const [item, setItem] = useState<Item | null>(null)
  const [verdict, setVerdict] = useState<Verdict | null>(null)
  const [answer, setAnswer] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [elapsed, setElapsed] = useState(0)
  const [done, setDone] = useState<Done[]>([])
  const [photos, setPhotos] = useState<string[]>([])
  const [writeUp, setWriteUp] = useState<WriteUp | null>(null)
  const [gradingMs, setGradingMs] = useState(0)
  const [dragging, setDragging] = useState(false)
  // Подсказка к заданию — по нажатию. Открытая сразу, она называет метод
  // до того, как задание вообще прочитано, и решать становится нечего.
  const [hint, setHint] = useState(false)
  const [written, setWritten] = useState<WrittenRow[]>([])
  const [opened, setOpened] = useState<WrittenRecord | null>(null)
  const [card, setCard] = useState<SkillCard | null>(null)
  // Приём, который тренируют с карточки; null — обычная сессия.
  const [training, setTraining] = useState<{ id: string; name: string } | null>(null)

  const shownAt = useRef(0)
  const firstKeyAt = useRef(0)
  const startedAt = useRef(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const recent = useRef<string[]>([])
  const recentBlocks = useRef<string[]>([])
  // Тот же приём, что и в training, но там, откуда его прочитает запрос:
  // сессия начинается тем же нажатием, а state дойдёт только к следующему
  // кадру.
  const focus = useRef<{ id: string; name: string } | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  useEffect(() => { saveSettings(settings) }, [settings])

  const loadStats = useCallback(async () => {
    try {
      const response = await fetch(`${API}/stats`)
      if (response.ok) setStats(await response.json())
    } catch { /* статистика не критична */ }
    try {
      const response = await fetch(`${API}/strength`)
      if (response.ok) setStrength(await response.json())
    } catch { /* карта не критична */ }
    try {
      // Незаконченный вечер поднимается сам: задания брали в семь, работу
      // присылают в десять, и искать набор руками не нужно.
      const response = await fetch(`${API}/evening`)
      if (response.ok) {
        // Берём свежий вечер в любом состоянии, а не только незаконченный:
        // разобранный тоже нужно уметь открыть обратно — иначе результаты
        // исчезают из вида, стоит перезагрузить страницу.
        const sets: Evening[] = (await response.json()).sets ?? []
        setEvening(sets[0] ?? null)
      }
    } catch { /* вечер не критичен */ }
    try {
      const response = await fetch(`${API}/written`)
      if (response.ok) setWritten((await response.json()).history ?? [])
    } catch { /* список работ не критичен */ }
  }, [])

  /** Темы для вечера: вопросов на бумаге и сколько приёмов уже начинали. */
  const eveningThemes = useMemo<EveningTheme[]>(() => {
    if (!setup) return []
    const started = new Map<string, number>()
    for (const skill of strength?.skills ?? []) {
      if (skill.score !== null) {
        started.set(skill.practicum, (started.get(skill.practicum) ?? 0) + 1)
      }
    }
    return setup
      .filter((entry) => entry.written > 0)
      .map((entry) => ({
        id: entry.id,
        title: entry.title,
        written: entry.written,
        skills: entry.skills,
        started: started.get(entry.id) ?? 0,
      }))
  }, [setup, strength])

  const openEvening = useCallback(async (choice: {
    minutes: number; practicums: string[]; papers: number[]; only_due: boolean
  }) => {
    setError(null)
    setBusy(true)
    try {
      const response = await fetch(`${API}/evening/open`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(choice),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? 'набор не собрался')
      setEvening(payload)
    } catch (problem) {
      setError(problem instanceof Error ? problem.message : 'не собралось')
    } finally {
      setBusy(false)
    }
  }, [])

  const dropEvening = useCallback(async (id: string) => {
    setError(null)
    setBusy(true)
    try {
      await fetch(`${API}/evening/drop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      })
      setEvening(null)
    } catch { /* черновик всё равно перезапишется при следующей сборке */ }
    finally { setBusy(false) }
  }, [])

  const openSkill = useCallback(async (id: string, fresh = false) => {
    setError(null)
    try {
      const seed = fresh ? `&seed=${Math.floor(Math.random() * 2 ** 31)}` : ''
      const response = await fetch(`${API}/skill?id=${encodeURIComponent(id)}${seed}`)
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      setCard(await response.json())
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    }
  }, [])

  const openWritten = useCallback(async (id: number) => {
    setError(null)
    try {
      const response = await fetch(`${API}/written?id=${id}`)
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      setOpened(await response.json())
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    }
  }, [])

  useEffect(() => {
    void (async () => {
      try {
        const response = await fetch(`${API}/setup`)
        if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
        const payload = await response.json() as {
          practicums: SetupPracticum[]; written_blocks?: WrittenBlock[] }
        setSetup(payload.practicums)
        setBlocks(payload.written_blocks ?? [])
      } catch (failure) {
        setError(failure instanceof Error ? failure.message : 'не отвечает')
      }
    })()
    void loadStats()
  }, [loadStats])

  const chosen = useMemo(() => {
    if (!setup) return []
    const picked = settings.practicums.length ? settings.practicums : setup.map((entry) => entry.id)
    return setup.filter((entry) => picked.includes(entry.id) && available(entry, settings.mode) > 0)
  }, [settings.mode, settings.practicums, setup])

  /** Сколько настоящих вопросов проходит через выбранные темы, бумагу и цену. */
  const matchingWritten = useMemo(() => {
    const picked = new Set(chosen.map((entry) => entry.id))
    const band = MARKS.find((entry) => entry.id === settings.marks)?.range
    return blocks.filter((block) => {
      if (!picked.has(block.practicum)) return false
      if (settings.papers.length && !settings.papers.includes(block.paper ?? 0)) return false
      if (band) {
        const price = block.marks ?? 0
        if (price < band[0] || (band[1] !== null && price > band[1])) return false
      }
      return true
    }).length
  }, [blocks, chosen, settings.marks, settings.papers])

  const chosenSkills = useMemo(
    () => chosen.reduce((sum, entry) => sum + (settings.mode === 'compute'
      ? entry.compute
      : settings.mode === 'written' ? entry.written : entry.skills), 0),
    [chosen, settings.mode],
  )

  const nextItem = useCallback(async () => {
    setBusy(true)
    setVerdict(null)
    setWriteUp(null)
    setPhotos([])
    setAnswer('')
    setHint(false)
    setError(null)
    if (fileRef.current) fileRef.current.value = ''
    try {
      // Один приём тренируют счётом: задача собирается заново по зерну, и
      // десяток подряд не повторится. Узнаваний на приём в банке два-три,
      // и подряд они превратились бы в заучивание ответа.
      const only = focus.current
      const params = new URLSearchParams({
        mode: only ? 'compute' : settings.mode,
        order: only ? 'random' : settings.order,
        only_due: !only && settings.onlyDue ? '1' : '0',
        avoid: only ? '' : recent.current.slice(-3).join(','),
        avoid_blocks: recentBlocks.current.slice(-8).join(','),
        practicums: only ? '' : chosen.map((entry) => entry.id).join(','),
      })
      if (only) params.set('skills', only.id)
      if (!only && settings.mode === 'written') {
        if (settings.papers.length) params.set('papers', settings.papers.join(','))
        const band = MARKS.find((entry) => entry.id === settings.marks)?.range
        if (band) {
          params.set('marks_min', String(band[0]))
          if (band[1]) params.set('marks_max', String(band[1]))
        }
      }
      const response = await fetch(`${API}/next?${params.toString()}`)
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      setItem(await response.json())
      shownAt.current = performance.now()
      firstKeyAt.current = 0
      setElapsed(0)
      window.setTimeout(() => inputRef.current?.focus(), 30)
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
      setItem(null)
    } finally {
      setBusy(false)
    }
  }, [chosen, settings.mode, settings.onlyDue, settings.order, settings.papers, settings.marks])

  /** Начинает сессию. target — приём, если тренируют его одного. */
  const begin = useCallback((target: { id: string; name: string } | null) => {
    focus.current = target
    setTraining(target)
    setDone([])
    recent.current = []
    recentBlocks.current = []
    startedAt.current = performance.now()
    setScreen('running')
    void nextItem()
  }, [nextItem])

  const start = useCallback(() => begin(null), [begin])

  const finish = useCallback(() => {
    setScreen('done')
    setItem(null)
    setVerdict(null)
    void loadStats()
  }, [loadStats])

  useEffect(() => {
    if (screen !== 'running' || !item || verdict || writeUp) return
    const timer = window.setInterval(() => setElapsed(performance.now() - shownAt.current), 100)
    return () => window.clearInterval(timer)
  }, [item, screen, verdict, writeUp])

  const submit = useCallback(async (raw: string) => {
    if (!item || busy || verdict) return
    const value = raw.trim()
    if (!value) return
    setBusy(true)
    const ms = Math.round(performance.now() - shownAt.current)
    const firstMs = Math.round((firstKeyAt.current || performance.now()) - shownAt.current)
    try {
      const response = await fetch(`${API}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ item: item.item, answer: value, mode: settings.mode, ms, first_ms: firstMs, hint }),
      })
      if (!response.ok) throw new Error(`сервер ответил ${response.status}`)
      const result: Verdict = await response.json()
      setVerdict(result)
      recent.current = [...recent.current, item.skill].slice(-6)
      setDone((current) => [...current, {
        skill: item.skill,
        skillName: result.skill_name,
        practicum: item.practicum,
        kind: item.kind,
        ok: result.ok,
        hint,
        ms,
        firstMs,
      }])
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    } finally {
      setBusy(false)
    }
    // hint здесь не для красоты: без него замыкание submit помнит ту
    // подсказку, что была на момент показа задания, то есть всегда «нет».
  }, [busy, hint, item, settings.mode, verdict])

  const addPhotos = useCallback(async (files: FileList | File[] | null) => {
    const chosen = Array.from(files ?? []).filter(
      (file) => file.type.startsWith('image/') || isPdf(file))
    if (!chosen.length) return
    setError(null)
    try {
      const added = await Promise.all(chosen.slice(0, MAX_PHOTOS)
        .map((file) => (isPdf(file) ? readAsIs(file) : shrink(file))))
      setPhotos((current) => [...current, ...added].slice(0, MAX_PHOTOS))
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'снимок не прочитался')
    }
  }, [])

  const acceptsWork = screen === 'running' && item?.kind === 'written'
    && !writeUp && !busy

  useEffect(() => {
    // Снимок экрана и сфотографированный лист чаще всего уже в буфере:
    // проще вставить, чем искать файл в диалоге.
    if (!acceptsWork) return
    const onPaste = (event: ClipboardEvent) => {
      const files = event.clipboardData?.files
      if (files?.length) {
        event.preventDefault()
        void addPhotos(files)
      }
    }
    window.addEventListener('paste', onPaste)
    return () => window.removeEventListener('paste', onPaste)
  }, [acceptsWork, addPhotos])

  const submitWork = useCallback(async () => {
    if (!item || item.kind !== 'written' || busy || writeUp || !photos.length) return
    setBusy(true)
    const ms = Math.round(performance.now() - shownAt.current)
    const sentAt = performance.now()
    setGradingMs(0)
    try {
      const response = await fetch(`${API}/grade`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ block: item.block, photos }),
      })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error ?? `сервер ответил ${response.status}`)
      const result = payload as WriteUp
      result.elapsedMs = Math.round(performance.now() - sentAt)
      setWriteUp(result)
      recent.current = [...recent.current, item.skill].slice(-6)
      if (item.block) recentBlocks.current = [...recentBlocks.current, item.block].slice(-20)
      setDone((current) => [...current, {
        skill: item.skill,
        skillName: result.skill_name ?? item.skill_name,
        practicum: item.practicum,
        kind: 'written',
        ok: (result.marks?.available ?? 0) > 0
          && result.marks.earned === result.marks.available,
        // У разбора подсказки нет: там настоящий вопрос архива.
        hint: false,
        ms,
        firstMs: ms,
        earned: result.marks?.earned ?? 0,
        available: result.marks?.available ?? item.marks ?? 0,
      }])
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'не отвечает')
    } finally {
      setBusy(false)
    }
  }, [busy, item, photos, writeUp])

  useEffect(() => {
    // Разбор идёт десятки секунд: без счётчика непонятно, работает он
    // или страница повисла.
    if (!busy || item?.kind !== 'written' || writeUp) return
    const started = performance.now()
    const timer = window.setInterval(
      () => setGradingMs(performance.now() - started), 100)
    return () => window.clearInterval(timer)
  }, [busy, item, writeUp])

  const markFirstKey = useCallback(() => {
    if (!firstKeyAt.current) firstKeyAt.current = performance.now()
  }, [])

  const sessionLength = training ? FOCUS_LENGTH : settings.length

  const advance = useCallback(() => {
    if (sessionLength > 0 && done.length >= sessionLength) finish()
    else void nextItem()
  }, [done.length, finish, nextItem, sessionLength])

  useEffect(() => {
    if (screen !== 'running') return
    const onKey = (event: KeyboardEvent) => {
      if (verdict || writeUp) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); advance() }
        return
      }
      if (item?.kind === 'written') return
      if (!item || item.kind !== 'recognition' || !item.options) return
      const index = Number.parseInt(event.key, 10)
      const option = Number.isInteger(index) ? item.options[index - 1] : undefined
      if (option) { markFirstKey(); void submit(option.code) }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [advance, item, markFirstKey, screen, submit, verdict, writeUp])

  const toggle = (id: string) => {
    setSettings((current) => {
      const all = setup?.map((entry) => entry.id) ?? []
      const base = current.practicums.length ? current.practicums : all
      const next = base.includes(id) ? base.filter((entry) => entry !== id) : [...base, id]
      return { ...current, practicums: next.length === all.length ? [] : next }
    })
  }

  const isPicked = (id: string) => !settings.practicums.length || settings.practicums.includes(id)

  const bySection = useMemo(() => {
    if (!setup) return []
    return practicumSections
      .map((section) => ({ ...section, entries: setup.filter((entry) => entry.section === section.id) }))
      .filter((section) => section.entries.length > 0)
  }, [setup])

  // --- итог сессии ------------------------------------------------------
  const summary = useMemo(() => {
    const correct = done.filter((entry) => entry.ok).length
    const total = done.length
    const spent = done.reduce((sum, entry) => sum + entry.ms, 0)
    const recognition = done.filter((entry) => entry.kind === 'recognition')
    const misses = new Map<string, { name: string; practicum: string; wrong: number; total: number }>()
    for (const entry of done) {
      const row = misses.get(entry.skill) ?? { name: entry.skillName, practicum: entry.practicum, wrong: 0, total: 0 }
      row.total += 1
      if (!entry.ok) row.wrong += 1
      misses.set(entry.skill, row)
    }
    const marked = done.filter((entry) => entry.available !== undefined)
    return {
      correct,
      total,
      spent,
      hinted: done.filter((entry) => entry.hint).length,
      marksEarned: marked.reduce((sum, entry) => sum + (entry.earned ?? 0), 0),
      marksAvailable: marked.reduce((sum, entry) => sum + (entry.available ?? 0), 0),
      written: marked.length,
      avgFirst: recognition.length
        ? recognition.reduce((sum, entry) => sum + entry.firstMs, 0) / recognition.length
        : 0,
      weak: [...misses.values()].filter((row) => row.wrong > 0).sort((a, b) => b.wrong - a.wrong),
    }
  }, [done])

  if (error && !setup) {
    return <div className="min-h-0 flex-1 overflow-y-auto bg-canvas p-6">
      <p className="border border-line bg-surface p-3 text-sm text-ink">Тренажёр не отвечает: {error}</p>
    </div>
  }

  return (
    <div className="min-h-0 flex-1 overflow-y-auto bg-canvas">
      <div className="mx-auto flex max-w-3xl flex-col gap-6 px-4 py-6">

        {screen === 'setup' && setup && (
          <>
            <div className="flex flex-col gap-1">
              <h2 className="text-lg text-ink">Повторение</h2>
              <p className="text-sm text-muted">
                Практикум учит приёму, тренажёр держит его в форме. Соберите набор и начните.
              </p>
            </div>

            <button
              type="button"
              className="flex cursor-pointer items-center justify-between gap-3 border border-line-strong bg-surface p-3 text-left hover:bg-surface-strong"
              onClick={() => setScreen('evening')}
            >
              <span className="flex flex-col gap-0.5">
                <span className="text-sm text-ink">
                  {!evening ? 'Вечер: одна кнопка, лист на бумагу'
                    : evening.state === 'graded' ? 'Вечер разобран'
                      : evening.state === 'draft' ? 'Черновик вечера — не начат'
                        : 'Продолжить вечер'}
                </span>
                <span className="text-[11px] text-muted">
                  {!evening
                    ? 'Настоящие вопросы архива листом, решаешь на бумаге, присылаешь одним сканом'
                    : evening.state === 'graded'
                      ? `${evening.results.reduce((sum, row) => sum + (row.earned ?? 0), 0)} из ${evening.results.reduce((sum, row) => sum + (row.skipped || row.error ? 0 : (row.available ?? 0)), 0)} баллов, ${evening.questions.length} заданий`
                      : `${evening.questions.length} заданий, ${evening.marks} баллов${
                          evening.state === 'draft' ? ' · ждёт старта'
                            : evening.pages.length ? ' · работа прислана' : ' · лист собран'}`}
                </span>
              </span>
              <span className="font-mono text-[11px] text-faint">→</span>
            </button>

            <section className="flex flex-col gap-2">
              <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Режим</h3>
              <div className="grid grid-cols-3 gap-1.5 max-[560px]:grid-cols-1">
                {MODES.map((entry) => (
                  <button
                    key={entry.id}
                    type="button"
                    aria-pressed={settings.mode === entry.id}
                    className={`flex cursor-pointer flex-col gap-1 border p-2.5 text-left ${settings.mode === entry.id ? 'border-line-strong bg-surface' : 'border-line bg-canvas hover:bg-surface'}`}
                    onClick={() => setSettings((current) => ({ ...current, mode: entry.id }))}
                  >
                    <span className="font-mono text-[11px] text-ink">{entry.label}</span>
                    <span className="text-[11px] leading-snug text-muted">{entry.hint}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <div className="flex items-baseline justify-between gap-3">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Темы</h3>
                <div className="flex gap-2 font-mono text-[10px]">
                  <button type="button" className="cursor-pointer border-0 bg-transparent text-muted hover:text-ink" onClick={() => setSettings((current) => ({ ...current, practicums: [] }))}>все</button>
                </div>
              </div>
              {bySection.map((section) => (
                <div key={section.id} className="flex flex-col gap-1">
                  <span className="text-[11px] text-faint">{section.title}</span>
                  <div className="flex flex-wrap gap-1.5">
                    {section.entries.map((entry) => {
                      const count = available(entry, settings.mode)
                      const off = count === 0
                      const on = isPicked(entry.id) && !off
                      return (
                        <button
                          key={entry.id}
                          type="button"
                          disabled={off}
                          title={off ? `${entry.title} — в этом режиме заданий пока нет` : `${entry.title} — ${entry.marks ?? '?'} баллов архива, ${entry.skills} приёмов`}
                          aria-pressed={on}
                          className={`flex cursor-pointer items-baseline gap-1.5 border px-2 py-1 ${off ? 'border-line bg-canvas text-faint line-through' : on ? 'border-line-strong bg-ink text-canvas' : 'border-line bg-canvas text-muted hover:bg-surface'}`}
                          onClick={() => toggle(entry.id)}
                        >
                          <span className="font-mono text-[11px]">{entry.id}</span>
                          <span className="text-[11px]">{count || '—'}</span>
                        </button>
                      )
                    })}
                  </div>
                </div>
              ))}
              <p className="text-[11px] text-faint">
                Число на плитке — сколько заданий доступно в выбранном режиме.
                {settings.mode === 'written' && ' В разборе это настоящие вопросы архива: нужны бумага и камера, и одно задание занимает минуты, а не секунды.'}
              </p>
            </section>

            {settings.mode === 'written' && (
              <section className="grid grid-cols-2 gap-4 max-[560px]:grid-cols-1">
                <div className="flex flex-col gap-2">
                  <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Бумага</h3>
                  <div className="flex border border-line">
                    {PAPERS.map((paper) => {
                      const on = !settings.papers.length || settings.papers.includes(paper.id)
                      return (
                        <button
                          key={paper.id}
                          type="button"
                          title={paper.hint}
                          aria-pressed={on}
                          className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${on ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                          onClick={() => setSettings((current) => {
                            const all = PAPERS.map((entry) => entry.id)
                            const base = current.papers.length ? current.papers : all
                            const next = base.includes(paper.id)
                              ? base.filter((entry) => entry !== paper.id)
                              : [...base, paper.id]
                            return { ...current, papers: next.length === all.length ? [] : next }
                          })}
                        >
                          Paper {paper.id}
                        </button>
                      )
                    })}
                  </div>
                  <p className="text-[11px] leading-snug text-faint">
                    Paper 1 без калькулятора, Paper 2 с ним, Paper 3 — длинные исследования.
                  </p>
                </div>

                <div className="flex flex-col gap-2">
                  <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Цена вопроса</h3>
                  <div className="flex border border-line">
                    {MARKS.map((band) => (
                      <button
                        key={band.id}
                        type="button"
                        title={band.hint}
                        aria-pressed={settings.marks === band.id}
                        className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${settings.marks === band.id ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                        onClick={() => setSettings((current) => ({ ...current, marks: band.id }))}
                      >
                        {band.label}
                      </button>
                    ))}
                  </div>
                  <p className="text-[11px] leading-snug text-faint">
                    {MARKS.find((band) => band.id === settings.marks)?.hint}
                  </p>
                </div>
              </section>
            )}

            <section className="grid grid-cols-2 gap-4 max-[560px]:grid-cols-1">
              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Длина</h3>
                <div className="flex border border-line">
                  {(settings.mode === 'written' ? WRITTEN_LENGTHS : LENGTHS).map((length) => (
                    <button
                      key={length}
                      type="button"
                      aria-pressed={settings.length === length}
                      className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${settings.length === length ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                      onClick={() => setSettings((current) => ({ ...current, length }))}
                    >
                      {length === 0 ? 'без конца' : length}
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Порядок</h3>
                <div className="flex border border-line">
                  {ORDERS.map((entry) => (
                    <button
                      key={entry.id}
                      type="button"
                      title={entry.hint}
                      aria-pressed={settings.order === entry.id}
                      className={`h-7 flex-1 cursor-pointer border-0 border-l border-line px-2 font-mono text-[10px] first:border-l-0 ${settings.order === entry.id ? 'bg-ink text-canvas' : 'bg-canvas text-muted hover:bg-surface'}`}
                      onClick={() => setSettings((current) => ({ ...current, order: entry.id }))}
                    >
                      {entry.label}
                    </button>
                  ))}
                </div>
                <p className="text-[11px] leading-snug text-faint">{ORDERS.find((entry) => entry.id === settings.order)?.hint}</p>
              </div>
            </section>

            <section className="flex flex-col gap-2">
              <label className="flex cursor-pointer items-baseline gap-2 text-sm text-ink">
                <input type="checkbox" checked={settings.onlyDue} onChange={(event) => setSettings((current) => ({ ...current, onlyDue: event.target.checked }))} />
                <span>только то, чему подошёл срок
                  <span className="text-muted"> — если срок не подошёл ничему, набор берётся целиком</span>
                </span>
              </label>
              <label className="flex cursor-pointer items-baseline gap-2 text-sm text-ink">
                <input type="checkbox" checked={settings.showTimer} onChange={(event) => setSettings((current) => ({ ...current, showTimer: event.target.checked }))} />
                <span>показывать секундомер
                  <span className="text-muted"> — время записывается в любом случае</span>
                </span>
              </label>
            </section>

            <div className="flex flex-wrap items-center gap-4 border-t border-line pt-4">
              <button
                type="button"
                disabled={settings.mode === 'written' ? matchingWritten === 0 : chosenSkills === 0}
                className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90 disabled:cursor-default disabled:opacity-40"
                onClick={start}
              >
                начать
              </button>
              <span className="font-mono text-[11px] text-muted">
                {settings.mode === 'written'
                  ? (matchingWritten > 0
                      ? `${matchingWritten} вопросов подходит${settings.length ? `, в сессии ${settings.length}` : ''}`
                      : 'под этот отбор вопросов нет — снимите ограничение по бумаге или цене')
                  : chosenSkills > 0
                    ? `${chosen.length} тем, ${chosenSkills} приёмов${settings.length ? `, ${settings.length} заданий` : ''}`
                    : 'в этом режиме выбранные темы пусты'}
              </span>
              <button
                type="button"
                className="ml-auto cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
                onClick={() => { setCard(null); setScreen('map') }}
              >
                карта приёмов{stats ? ` (${stats.skills.length})` : ''}
              </button>
              {written.length > 0 && (
                <button
                  type="button"
                  className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
                  onClick={() => { setOpened(null); setScreen('history') }}
                >
                  мои работы ({written.length})
                </button>
              )}
            </div>
          </>
        )}

        {screen === 'evening' && (
          <EveningView
            evening={evening}
            themes={eveningThemes}
            busy={busy}
            setBusy={setBusy}
            onOpen={openEvening}
            onChange={setEvening}
            onDrop={dropEvening}
            onClose={() => { setScreen('setup'); void loadStats() }}
          />
        )}

        {screen === 'map' && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <h2 className="text-lg text-ink">Карта приёмов</h2>
              <button
                type="button"
                className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
                onClick={() => (card ? setCard(null) : setScreen('setup'))}
              >
                {card ? 'ко всем приёмам' : 'к настройкам'}
              </button>
            </div>

            {!card && strength && (
              <div className="flex flex-col gap-4" onMouseLeave={() => setHovered(null)}>
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="max-w-[46rem] text-sm text-muted">
                    Все {strength.skills.length} приёмов. Число — насколько приём отточен:
                    свежесть, помноженная на глубину. Каждое повторение поднимает его,
                    простой опускает. Нажмите на квадрат, чтобы открыть карточку приёма.
                  </p>
                  <button
                    type="button"
                    className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
                    onClick={() => setAsList((current) => !current)}
                  >
                    {asList ? 'картой' : 'списком'}
                  </button>
                </div>

                {!asList && <>
                  <div className="flex flex-col gap-1">
                    {strength.practicums.map((practicum) => (
                      <div key={practicum.id} className="flex items-center gap-2">
                        <span className="w-7 shrink-0 font-mono text-[10px] text-faint">{practicum.id}</span>
                        <span className="w-7 shrink-0 text-right font-mono text-[11px] tabular-nums text-ink">
                          {practicum.score ?? '·'}
                        </span>
                        <div className="flex gap-0.5">
                          {strength.skills.filter((skill) => skill.practicum === practicum.id).map((skill) => (
                            <button
                              key={skill.id}
                              type="button"
                              title={heatRead(skill, strength.horizon)}
                              onMouseEnter={() => setHovered(skill)}
                              onFocus={() => setHovered(skill)}
                              onClick={() => void openSkill(skill.id)}
                              className={`relative h-7 w-7 cursor-pointer border font-mono text-[10px] tabular-nums hover:outline hover:outline-2 hover:outline-offset-[-2px] hover:outline-ink ${heatTone(skill.score)}`}
                            >
                              {skill.score ?? '·'}
                              {skill.due_in_days !== null && skill.due_in_days <= 0 && (
                                <span className="pointer-events-none absolute inset-y-0 left-0 w-[3px] bg-primary" />
                              )}
                            </button>
                          ))}
                        </div>
                        <span className="ml-auto shrink-0 font-mono text-[10px] text-faint">
                          {practicum.started}/{practicum.skills} · {practicum.marks} б.
                        </span>
                      </div>
                    ))}
                  </div>

                  <p className="min-h-[2.5em] border-t border-line pt-2 text-[11px] text-muted">
                    {heatRead(hovered, strength.horizon)}
                  </p>

                  <div className="flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[10px] text-faint">
                    <span className="flex items-center gap-1">
                      слабее
                      {HEAT.map((tone, index) => (
                        <span key={index} className={`inline-block h-3 w-3 border border-line ${tone}`} />
                      ))}
                      сильнее
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="inline-block h-3 w-3 border border-dashed border-line-strong bg-surface" />
                      ни разу не показывали
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="relative inline-block h-3 w-3 border border-line bg-heat-2">
                        <span className="absolute inset-y-0 left-0 w-[2px] bg-primary" />
                      </span>
                      срок повторить подошёл
                    </span>
                  </div>
                </>}

                {asList && (
                  <table className="w-full border-collapse text-left">
                    <thead>
                      <tr className="border-b border-line font-mono text-[10px] tracking-wide text-faint uppercase">
                        <th className="py-1 pr-3 font-normal">приём</th>
                        <th className="py-1 pr-3 text-right font-normal">счёт</th>
                        <th className="py-1 pr-3 text-right font-normal">держится</th>
                        <th className="py-1 pr-3 text-right font-normal">повторить</th>
                        <th className="py-1 text-right font-normal">показов</th>
                      </tr>
                    </thead>
                    <tbody>
                      {strength.skills.map((skill) => (
                        <tr
                          key={skill.id}
                          tabIndex={0}
                          className="cursor-pointer border-b border-line hover:bg-surface"
                          onClick={() => void openSkill(skill.id)}
                        >
                          <td className="py-1.5 pr-3">
                            <span className="font-mono text-[10px] text-faint">{skill.practicum}</span>{' '}
                            <span className="text-sm text-ink">{skill.name}</span>
                          </td>
                          <td className="py-1.5 pr-3 text-right font-mono text-[11px] tabular-nums text-ink">{skill.score ?? '—'}</td>
                          <td className="py-1.5 pr-3 text-right font-mono text-[11px] tabular-nums text-muted">{skill.stability === null ? '—' : `${skill.stability} дн.`}</td>
                          <td className="py-1.5 pr-3 text-right font-mono text-[11px] tabular-nums text-muted">
                            {skill.due_in_days === null ? '—' : skill.due_in_days <= 0 ? 'пора' : `${Math.round(skill.due_in_days)} дн.`}
                          </td>
                          <td className="py-1.5 text-right font-mono text-[11px] tabular-nums text-muted">
                            {skill.seen}{skill.wrong ? ` / ${skill.wrong} мимо` : ''}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {card && (
              <motion.div initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col gap-4">
                <div className="flex flex-wrap items-start justify-between gap-3 border-b border-line pb-3">
                  <div className="flex flex-col gap-1">
                    <div className="flex flex-wrap items-baseline gap-x-3">
                      <h3 className="text-base text-ink">{card.name}</h3>
                      <span className="font-mono text-[10px] text-faint">
                        {card.practicum} · ступень {card.rung} · калькулятор {CALCULATOR[card.calculator] ?? card.calculator}
                      </span>
                    </div>
                    <span className="text-[11px] text-muted">{card.practicum_title}</span>
                  </div>
                  <div className="flex shrink-0 flex-col items-end gap-1">
                    <button
                      type="button"
                      className="h-9 cursor-pointer border border-line-strong bg-ink px-4 font-mono text-[11px] text-canvas hover:opacity-90"
                      onClick={() => begin({ id: card.id, name: card.name })}
                    >
                      тренировать приём
                    </button>
                    <span className="font-mono text-[10px] text-faint">
                      {FOCUS_LENGTH} заданий подряд, только на него
                    </span>
                  </div>
                </div>

                <dl className="grid grid-cols-[8rem_1fr] items-baseline gap-x-3 gap-y-3 max-[560px]:grid-cols-1 max-[560px]:gap-y-1">
                  <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">узнаётся по</dt>
                  <dd className="text-sm leading-relaxed text-ink"><MathText>{card.trigger}</MathText></dd>

                  <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">ход</dt>
                  <dd>
                    <ol className="flex flex-col gap-0.5 text-xs leading-relaxed text-muted">
                      {card.chain.map((step, index) => (
                        <li key={step} className="flex gap-2">
                          <span className="font-mono text-[10px] text-faint">{index + 1}</span>
                          <MathText>{step}</MathText>
                        </li>
                      ))}
                    </ol>
                  </dd>

                  <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">где срезаются</dt>
                  <dd>
                    <ul className="flex flex-col gap-1 text-xs leading-relaxed text-muted">
                      {card.traps.map((trap) => (
                        <li key={trap} className="flex gap-2">
                          <span className="text-faint">·</span>
                          <MathText>{trap}</MathText>
                        </li>
                      ))}
                    </ul>
                  </dd>

                  {card.recognition.length > 0 && <>
                    <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">узнать приём</dt>
                    <dd className="flex flex-col gap-2">
                      {card.recognition.map((example) => (
                        <div key={example.prompt} className="border-l-2 border-line pl-2 text-xs leading-relaxed">
                          <MathText className="block text-ink">{example.prompt}</MathText>
                          <span className="font-mono text-[10px] text-muted">ответ: {example.answer}</span>
                        </div>
                      ))}
                    </dd>
                  </>}

                  {card.compute && <>
                    <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">решить</dt>
                    <dd className="flex flex-col gap-1 border-l-2 border-line pl-2 text-xs leading-relaxed">
                      <MathText className="block text-ink">{card.compute.prompt}</MathText>
                      {card.compute.note && <MathText className="block text-faint">{card.compute.note}</MathText>}
                      <span className="font-mono text-[10px] text-muted">ответ: {card.compute.answer}</span>
                      <button
                        type="button"
                        className="w-fit cursor-pointer border-0 bg-transparent p-0 font-mono text-[10px] text-muted underline hover:text-ink"
                        onClick={() => void openSkill(card.id, true)}
                      >
                        другое задание
                      </button>
                    </dd>
                  </>}

                  {card.archive.length > 0 && <>
                    <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">в архиве</dt>
                    <dd className="flex flex-col gap-0.5 text-xs">
                      {card.archive.map((row) => (
                        <a
                          key={row.block}
                          href={row.question_url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex flex-wrap items-baseline gap-x-2 text-muted hover:text-ink"
                        >
                          <span className="text-ink">{row.reference}</span>
                          <span className="font-mono text-[10px] text-faint">
                            {row.marks} {marksWord(row.marks ?? 0)} · {row.calculator === 'yes' ? 'GDC' : 'без GDC'}
                          </span>
                        </a>
                      ))}
                    </dd>
                  </>}

                  <dt className="font-mono text-[10px] tracking-wide text-faint uppercase">у тебя</dt>
                  <dd className="font-mono text-[11px] text-muted">
                    {card.state
                      ? `сила ${card.state.score}, держится ${card.state.stability} дн., последний раз ${card.state.days_since === 0 ? 'сегодня' : `${card.state.days_since} дн. назад`}, срок ${(card.state.due_in_days ?? 0) <= 0 ? 'подошёл' : `через ${Math.round(card.state.due_in_days ?? 0)} дн.`}; показов ${card.state.seen}, мимо ${card.state.wrong}`
                      : 'ни одной попытки'}
                  </dd>
                </dl>
              </motion.div>
            )}
          </section>
        )}

        {screen === 'history' && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <h2 className="text-lg text-ink">Мои работы</h2>
              <button
                type="button"
                className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted underline hover:text-ink"
                onClick={() => (opened ? setOpened(null) : setScreen('setup'))}
              >
                {opened ? 'к списку' : 'к настройкам'}
              </button>
            </div>

            {!opened && (
              <ul className="flex flex-col">
                {written.map((row) => (
                  <li key={row.id}>
                    <button
                      type="button"
                      className="flex w-full flex-wrap items-baseline gap-x-3 gap-y-0.5 border-b border-line px-1 py-2 text-left hover:bg-surface"
                      onClick={() => void openWritten(row.id)}
                    >
                      <span className="w-24 shrink-0 font-mono text-[10px] text-faint">{when(row.ts)}</span>
                      <span className="font-mono text-[11px] text-ink">
                        {row.earned ?? '—'}/{row.available ?? '—'}
                      </span>
                      <span className="text-sm text-ink">{row.reference}</span>
                      <span className="text-[11px] text-muted">{row.math || 'не проверена'}</span>
                      <span className="ml-auto font-mono text-[10px] text-faint">
                        {row.pages} {row.pages === 1 ? 'страница' : 'страниц'}
                      </span>
                    </button>
                  </li>
                ))}
              </ul>
            )}

            {opened && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-wrap items-baseline gap-x-3 text-sm text-ink">
                  <span className="font-mono text-[10px] text-faint">{when(opened.ts)}</span>
                  <span>{opened.reference}</span>
                  <span className="font-mono text-[11px] text-muted">{opened.skill}</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {opened.files.map((file) => (
                    file.name.endsWith('.pdf')
                      ? <a key={file.url} href={file.url} target="_blank" rel="noreferrer"
                           className="grid h-28 w-20 place-items-center border border-line bg-surface font-mono text-[10px] text-muted hover:bg-canvas">
                          PDF
                        </a>
                      : <a key={file.url} href={file.url} target="_blank" rel="noreferrer">
                          <img src={file.url} alt={file.name} className="h-28 w-auto border border-line object-cover" />
                        </a>
                  ))}
                </div>

                {opened.verdict?.error
                  ? <p className="border border-line bg-surface p-3 text-sm text-ink">
                      Работа сохранена, но разбор не состоялся: {opened.verdict.error}
                    </p>
                  : <WriteUpVerdict verdict={opened.verdict} />}
              </div>
            )}
          </section>
        )}

        {screen === 'running' && (
          <>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-3 font-mono text-[11px] text-muted">
                <button type="button" className="cursor-pointer border border-line bg-canvas px-2 py-1 text-[10px] hover:bg-surface" onClick={finish}>закончить</button>
                <span>{done.length}{sessionLength ? ` / ${sessionLength}` : ''}</span>
                {training && <span className="text-ink">приём: {training.name}</span>}
              </div>
              {settings.showTimer && (
                <span className={`font-mono text-[11px] ${item && elapsed > item.budget_ms ? 'text-ink' : 'text-muted'}`}>
                  {seconds(elapsed)}{item ? ` / ${seconds(item.budget_ms)}` : ''}
                </span>
              )}
            </div>

            {error && <p className="border border-line bg-surface p-3 text-sm text-ink">Тренажёр не отвечает: {error}</p>}

            {item && (
              <motion.section
                key={item.item}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col gap-4 border border-line bg-canvas p-5"
              >
                <div className="flex items-center gap-2 font-mono text-[10px] text-faint">
                  <span className="border border-line px-1.5 py-0.5">{item.practicum}</span>
                  <span>{item.kind === 'recognition' ? 'назвать приём' : 'решить и ввести ответ'}</span>
                  {/* Своей цены у сгенерированной задачи нет — её не печатал
                      экзамен. Показывается цена вопросов архива, из которых
                      вырос приём: по ней видно, два это балла или семь. */}
                  {item.kind !== 'written' && item.archive_marks && (
                    <span>· в архиве {price(item.archive_marks)}</span>
                  )}
                </div>

                {item.kind === 'written' ? (
                  <div className="flex flex-col gap-3">
                    <div className="flex flex-wrap items-baseline justify-between gap-2">
                      <span className="text-sm text-ink">{item.reference}</span>
                      <span className="font-mono text-[11px] text-muted">
                        {item.marks} marks · {item.calculator === 'yes' ? 'GDC' : 'no GDC'}
                      </span>
                    </div>
                    <div className="flex flex-col gap-2">
                      {Array.from({ length: item.pages ?? 1 }, (_, page) => (
                        <img
                          key={page}
                          src={`${API}/page?block=${encodeURIComponent(item.block ?? '')}&kind=question&n=${page}`}
                          alt={`question page ${page + 1}`}
                          loading="lazy"
                          className="w-full border border-line bg-canvas"
                        />
                      ))}
                    </div>
                    <p className="text-[11px] text-faint">
                      Solve it on paper, in English, then photograph the page, paste it
                      from the clipboard or drop in a scanned PDF. Only your question is marked — ignore anything else
                      printed above or below it.
                    </p>
                  </div>
                ) : <>
                  <MathText className="text-[15px] leading-relaxed text-ink">{item.prompt}</MathText>
                  {item.note && (hint || verdict
                    // После ответа подсказка уже ничего не выдаёт, а объясняет,
                    // и прятать её за нажатием незачем.
                    ? <MathText className="text-xs text-muted">{item.note}</MathText>
                    : <button
                        type="button"
                        className="w-fit cursor-pointer border-0 bg-transparent p-0 font-mono text-[11px] text-muted underline hover:text-ink"
                        onClick={() => setHint(true)}
                      >
                        подсказка
                      </button>)}
                </>}

                {item.kind === 'written' ? (
                  !writeUp && <div
                    className={`flex flex-col gap-3 border-t pt-3 ${dragging ? 'border-line-strong bg-surface' : 'border-line'}`}
                    onDragOver={(event) => { event.preventDefault(); setDragging(true) }}
                    onDragLeave={() => setDragging(false)}
                    onDrop={(event) => {
                      event.preventDefault()
                      setDragging(false)
                      void addPhotos(event.dataTransfer.files)
                    }}
                  >
                    <input
                      ref={fileRef}
                      type="file"
                      accept="image/*,application/pdf"
                      capture="environment"
                      multiple
                      className="text-xs text-muted file:mr-2 file:cursor-pointer file:border file:border-line file:bg-canvas file:px-2 file:py-1 file:font-mono file:text-[11px] file:text-ink hover:file:bg-surface"
                      onChange={(event) => void addPhotos(event.target.files)}
                    />
                    <p className="text-[11px] text-faint">
                      {dragging
                        ? 'Отпустите — файлы добавятся к работе'
                        : 'Можно перетащить файлы сюда или вставить из буфера: Ctrl+V'}
                    </p>
                    {photos.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {photos.map((photo, index) => (
                          photo.startsWith('data:application/pdf')
                            ? <span key={photo.slice(-32)} className="grid h-24 w-20 place-items-center border border-line bg-surface font-mono text-[10px] text-muted">
                                PDF
                              </span>
                            : <img key={photo.slice(-32)} src={photo} alt={`page ${index + 1}`} className="h-24 w-auto border border-line object-cover" />
                        ))}
                      </div>
                    )}
                    <div className="flex flex-wrap items-center gap-3">
                      <button
                        type="button"
                        disabled={!photos.length || busy}
                        className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90 disabled:cursor-default disabled:opacity-40"
                        onClick={() => void submitWork()}
                      >
                        {busy ? 'marking…' : 'mark my work'}
                      </button>
                      {busy && (
                        <span className="font-mono text-[11px] text-muted">
                          reading your page and the markscheme · {(gradingMs / 1000).toFixed(1)} s
                        </span>
                      )}
                      {!busy && photos.length > 0 && (
                        <button type="button" className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted hover:text-ink" onClick={() => { setPhotos([]); if (fileRef.current) fileRef.current.value = '' }}>
                          clear
                        </button>
                      )}
                      {!busy && !photos.length && (
                        <button type="button" className="cursor-pointer border-0 bg-transparent font-mono text-[11px] text-muted hover:text-ink" onClick={advance}>
                          пропустить
                        </button>
                      )}
                    </div>
                  </div>
                ) : item.kind === 'recognition' && item.options
                  ? <div className="grid grid-cols-2 gap-1.5 max-[560px]:grid-cols-1">
                      {item.options.map((option, index) => (
                        <button
                          key={option.code}
                          type="button"
                          disabled={Boolean(verdict) || busy}
                          className="flex cursor-pointer items-baseline gap-2 border border-line bg-canvas px-2.5 py-2 text-left text-sm text-ink hover:bg-surface disabled:cursor-default disabled:opacity-60"
                          onClick={() => { markFirstKey(); void submit(option.code) }}
                        >
                          <span className="font-mono text-[10px] text-faint">{index + 1}</span>
                          <span className="font-mono text-[11px]">{option.code}</span>
                          <span className="text-xs text-muted">{option.name}</span>
                        </button>
                      ))}
                    </div>
                  : <form className="flex gap-2" onSubmit={(event) => { event.preventDefault(); void submit(answer) }}>
                      <input
                        ref={inputRef}
                        className="h-9 min-w-0 flex-1 border border-line bg-canvas px-2.5 font-mono text-sm text-ink outline-none focus:border-line-strong"
                        placeholder="например 2sqrt(6) или 1, 4"
                        value={answer}
                        disabled={Boolean(verdict)}
                        onChange={(event) => { markFirstKey(); setAnswer(event.target.value) }}
                      />
                      <button
                        type="submit"
                        disabled={Boolean(verdict) || busy || !answer.trim()}
                        className="h-9 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface disabled:cursor-default disabled:opacity-50"
                      >
                        ответить
                      </button>
                    </form>}

                {writeUp && (
                  <div className="flex flex-col gap-4 border-t border-line pt-3">
                    <WriteUpVerdict verdict={writeUp} />
                    <div className="flex items-center gap-3">
                      <button
                        type="button"
                        className="h-8 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface"
                        onClick={advance}
                      >
                        {sessionLength > 0 && done.length >= sessionLength ? 'итог' : 'дальше'}
                      </button>
                      <span className="font-mono text-[10px] text-faint">Enter или пробел</span>
                    </div>
                  </div>
                )}

                {verdict && (
                  <div className="flex flex-col gap-3 border-t border-line pt-3">
                    <MathText className="text-sm text-ink">{verdict.message}</MathText>
                    {hint && verdict.ok && (
                      <p className="font-mono text-[10px] text-faint">
                        подсказка взята — попытка идёт как трудная, и срок
                        повторения сдвинется меньше обычного
                      </p>
                    )}

                    <dl className="grid grid-cols-[8rem_1fr] items-baseline gap-x-3 gap-y-2.5 border-t border-line pt-3 max-[560px]:grid-cols-1 max-[560px]:gap-y-1">
                      {!verdict.ok && <>
                        <dt className={LABEL}>верный ответ</dt>
                        <dd className="font-mono text-sm text-ink">{verdict.answer}</dd>
                      </>}

                      <dt className={LABEL}>приём</dt>
                      <dd className="text-sm text-ink">
                        {verdict.skill_name}
                        <span className="ml-2 font-mono text-[10px] text-faint">{verdict.practicum}</span>
                      </dd>

                      <dt className={LABEL}>узнаётся по</dt>
                      <dd className="text-xs leading-relaxed text-muted">{verdict.trigger}</dd>

                      {verdict.chain.length > 0 && <>
                        <dt className={LABEL}>ход</dt>
                        <dd>
                          <ol className="flex flex-col gap-0.5 text-xs leading-relaxed text-muted">
                            {verdict.chain.map((step, index) => (
                              <li key={step} className="flex gap-2">
                                <span className="font-mono text-[10px] text-faint">{index + 1}</span>
                                <span>{step}</span>
                              </li>
                            ))}
                          </ol>
                        </dd>
                      </>}

                      {verdict.traps.length > 0 && <>
                        <dt className={LABEL}>где срезаются</dt>
                        <dd>
                          <ul className="flex flex-col gap-1 text-xs leading-relaxed text-muted">
                            {verdict.traps.map((trap) => (
                              <li key={trap} className="flex gap-2">
                                <span className="text-faint">·</span>
                                <span>{trap}</span>
                              </li>
                            ))}
                          </ul>
                        </dd>
                      </>}
                    </dl>

                    <div className="flex items-center gap-3 pt-1">
                      <button
                        type="button"
                        className="h-8 cursor-pointer border border-line-strong bg-canvas px-3 font-mono text-[11px] text-ink hover:bg-surface"
                        onClick={advance}
                      >
                        {sessionLength > 0 && done.length >= sessionLength ? 'итог' : 'дальше'}
                      </button>
                      <span className="font-mono text-[10px] text-faint">Enter или пробел</span>
                    </div>
                  </div>
                )}
              </motion.section>
            )}
          </>
        )}

        {screen === 'done' && (
          <section className="flex flex-col gap-5">
            <div className="flex flex-col gap-1">
              <h2 className="text-lg text-ink">
                {summary.written
                  ? `${summary.marksEarned} из ${summary.marksAvailable} баллов`
                  : summary.total ? `${summary.correct} из ${summary.total}` : 'Ни одного задания'}
              </h2>
              {summary.total > 0 && (
                <p className="font-mono text-[11px] text-muted">
                  {minutes(summary.spent)} всего, {seconds(summary.spent / summary.total)} на задание
                  {summary.avgFirst > 0 ? `, ${seconds(summary.avgFirst)} до первого нажатия в узнавании` : ''}
                  {summary.hinted > 0 ? `, с подсказкой ${summary.hinted}` : ''}
                </p>
              )}
            </div>

            {summary.weak.length > 0 && (
              <div className="flex flex-col gap-2">
                <h3 className="font-mono text-[10px] tracking-wide text-faint uppercase">Вернуться к этому</h3>
                <ul className="flex flex-col gap-1">
                  {summary.weak.map((row) => (
                    <li key={row.name} className="flex items-baseline gap-2 text-sm text-ink">
                      <span className="font-mono text-[10px] text-faint">{row.practicum}</span>
                      <span>{row.name}</span>
                      <span className="font-mono text-[10px] text-muted">{row.wrong} из {row.total} мимо</span>
                    </li>
                  ))}
                </ul>
                <p className="text-[11px] text-faint">
                  Эти приёмы вернутся завтра: ошибка сбрасывает срок повторения в начало.
                </p>
              </div>
            )}

            {summary.total > 0 && summary.weak.length === 0 && (
              <p className="text-sm text-muted">Без единой ошибки. Сроки повторения сдвинулись вперёд.</p>
            )}

            <div className="flex flex-wrap gap-3">
              <button type="button" className="h-9 cursor-pointer border border-line-strong bg-ink px-5 font-mono text-[11px] text-canvas hover:opacity-90" onClick={() => begin(training)}>ещё раз</button>
              <button type="button" className="h-9 cursor-pointer border border-line bg-canvas px-4 font-mono text-[11px] text-muted hover:bg-surface" onClick={() => setScreen('setup')}>настройки</button>
            </div>
          </section>
        )}

        {stats && screen !== 'running' && screen !== 'history' && screen !== 'map'
          && screen !== 'evening' && (
          <section className="flex flex-col gap-3 border-t border-line pt-4">
            <div className="flex flex-wrap items-baseline gap-x-5 gap-y-1 font-mono text-[11px] text-muted">
              <span>всего попыток {stats.totals.attempts}</span>
              <span>верно {stats.totals.correct}</span>
              <span>сегодня {stats.totals.today_correct}/{stats.totals.today}</span>
              {stats.totals.avg_first_ms > 0 && <span>до первого нажатия {seconds(stats.totals.avg_first_ms)}</span>}
            </div>
            <div className="flex flex-col gap-0.5">
              {(strength?.practicums ?? []).map((practicum) => (
                <div key={practicum.id} className="flex items-center gap-2">
                  <span className="w-7 shrink-0 font-mono text-[10px] text-faint">{practicum.id}</span>
                  <div className="flex gap-0.5">
                    {(strength?.skills ?? []).filter((skill) => skill.practicum === practicum.id).map((skill) => (
                      <span
                        key={skill.id}
                        title={heatRead(skill, strength?.horizon ?? 120)}
                        className={`relative inline-block h-4 w-4 border ${heatTone(skill.score)}`}
                      >
                        {skill.due_in_days !== null && skill.due_in_days <= 0 && (
                          <span className="pointer-events-none absolute inset-y-0 left-0 w-[2px] bg-primary" />
                        )}
                      </span>
                    ))}
                  </div>
                  <span className="ml-auto shrink-0 font-mono text-[10px] text-faint">{practicum.score ?? '·'}</span>
                </div>
              ))}
            </div>
            <p className="text-[11px] text-faint">
              Насыщенность — сила приёма, красная полоска снизу — подошёл срок повторить,
              пунктир — ни разу не показывали. Числа и разбор — на карте приёмов.
            </p>
          </section>
        )}
      </div>
    </div>
  )
}
