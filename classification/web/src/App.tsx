import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { FilterPanel } from './components/FilterPanel'
import { Inspector } from './components/Inspector'
import { ResultsTable } from './components/ResultsTable'
import { StatusBar } from './components/StatusBar'
import { TopBar } from './components/TopBar'
import { PracticumHub } from './components/PracticumHub'
import { DrillView } from './components/DrillView'
import { fetchFacets, fetchQuestion, fetchQuestions, fetchSubjects, type AtlasFacets, type AtlasSubject } from './lib/api'
import { useI18n } from './i18n'
import type { Filters, FilterSetKey, Question } from './types'

const DEFAULT_SIDEBAR_WIDTH = 248
const MIN_SIDEBAR_WIDTH = 208
const MAX_SIDEBAR_WIDTH = 384

function sessionSortKey(session: string) {
  const match = /^(May|November) (\d{4})$/.exec(session)
  return match ? Number(match[2]) * 100 + (match[1] === 'May' ? 5 : 11) : Number.MAX_SAFE_INTEGER
}

const SUBJECT_KEY = 'question-atlas:subject'

const initialFilters: Filters = {
  query: '',
  paper: 'all',
  calculator: 'all',
  session: 'all',
  zone: 'all',
  status: 'all',
  topics: new Set(),
  methods: new Set(),
  forms: new Set(),
}

/** Отборы у предметов не совпадают: темы, приёмы и бумаги названы своими
 *  именами, и переносить их из математики в физику нечего. */
function freshFilters(): Filters {
  return { ...initialFilters, topics: new Set(), methods: new Set(), forms: new Set() }
}

function storedSubject(): string {
  try {
    return localStorage.getItem(SUBJECT_KEY) || 'math'
  } catch {
    return 'math'
  }
}

export default function App() {
  const { t } = useI18n()
  const [mode, setMode] = useState<'atlas' | 'practicums' | 'drill'>(() => {
    if (window.location.hash.startsWith('#practicums')) return 'practicums'
    if (window.location.hash.startsWith('#drill')) return 'drill'
    return 'atlas'
  })
  const [subject, setSubject] = useState<string>(storedSubject)
  const [subjects, setSubjects] = useState<AtlasSubject[]>([])
  const [filters, setFilters] = useState<Filters>(freshFilters)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedQuestion, setSelectedQuestion] = useState<Question | null>(null)
  const [pageQuestions, setPageQuestions] = useState<Question[]>([])
  const [facets, setFacets] = useState<AtlasFacets | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [resultMarks, setResultMarks] = useState(0)
  const [loading, setLoading] = useState(true)
  const [sidebarVisible, setSidebarVisible] = useState(() => localStorage.getItem('question-atlas:sidebar-visible') !== 'false')
  const [sidebarWidth, setSidebarWidth] = useState(() => {
    const storedValue = localStorage.getItem('question-atlas:sidebar-width')
    if (storedValue === null) return DEFAULT_SIDEBAR_WIDTH
    const stored = Number(storedValue)
    return Number.isFinite(stored)
      ? Math.min(MAX_SIDEBAR_WIDTH, Math.max(MIN_SIDEBAR_WIDTH, stored))
      : DEFAULT_SIDEBAR_WIDTH
  })
  const [compactLayout, setCompactLayout] = useState(() => window.matchMedia('(max-width: 960px)').matches)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [inspectorOpen, setInspectorOpen] = useState(false)
  const searchRef = useRef<HTMLInputElement>(null)

  const topicCounts = facets?.topics ?? []
  const methodCounts = facets?.methods ?? []
  const formCounts = facets?.forms ?? []
  // Бумаги приходят по частоте, а читаются по порядку: P1, P1A, P1B, P2.
  const paperCounts = useMemo(
    () => [...(facets?.papers ?? [])].sort((a, b) => a[0].localeCompare(b[0], undefined, { numeric: true })),
    [facets])
  const statusCounts = facets?.statuses ?? []
  const calculatorCounts = facets?.calculators ?? []
  // Разметку модели проверяет человек — но только там, где она была.
  const reviewed = statusCounts.some(([id]) => id === 'ai_draft' || id === 'manual_verified')
  const sessionCounts = useMemo(() => [...(facets?.sessions ?? [])].sort((a, b) => sessionSortKey(a[0]) - sessionSortKey(b[0])), [facets])
  const zoneCounts = useMemo(() => [...(facets?.zones ?? [])].sort((a, b) => a[0].localeCompare(b[0])), [facets])
  const archiveSessionCount = facets?.session_zones ?? 0
  const verifiedCount = facets?.verified ?? 0
  const draftCount = (facets?.total ?? 0) - verifiedCount
  const yearRange = useMemo(() => {
    const years = sessionCounts.map(([session]) => Number(session.slice(-4))).filter(Number.isFinite)
    if (years.length === 0) return '—'
    const first = Math.min(...years)
    const last = Math.max(...years)
    return first === last ? String(first) : `${first}–${last}`
  }, [sessionCounts])

  useEffect(() => {
    const controller = new AbortController()
    fetchFacets(subject, controller.signal).then(setFacets).catch(() => setFacets(null))
    return () => controller.abort()
  }, [subject])

  useEffect(() => {
    const controller = new AbortController()
    const delay = window.setTimeout(() => {
      setLoading(true)
      fetchQuestions(subject, filters, page, controller.signal)
        .then((result) => {
          setPageQuestions(result.items)
          setTotal(result.total)
          setResultMarks(result.totalMarks)
          if (selectedId && !result.items.some((question) => question.id === selectedId)) {
            setSelectedId(null)
            setSelectedQuestion(null)
            setInspectorOpen(false)
          }
        })
        .catch((error: unknown) => {
          if (error instanceof DOMException && error.name === 'AbortError') return
          setPageQuestions([])
          setTotal(0)
          setResultMarks(0)
        })
        .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    }, filters.query ? 180 : 0)
    return () => { controller.abort(); window.clearTimeout(delay) }
  }, [subject, filters, page, selectedId])

  useEffect(() => {
    if (!selectedId) return
    const controller = new AbortController()
    fetchQuestion(subject, selectedId, controller.signal).then(setSelectedQuestion).catch(() => {
      setSelectedQuestion(null)
      setInspectorOpen(false)
    })
    return () => controller.abort()
  }, [subject, selectedId])

  useEffect(() => {
    const media = window.matchMedia('(max-width: 960px)')
    const updateLayout = () => setCompactLayout(media.matches)
    media.addEventListener('change', updateLayout)
    return () => media.removeEventListener('change', updateLayout)
  }, [])

  useEffect(() => {
    localStorage.setItem('question-atlas:sidebar-visible', String(sidebarVisible))
  }, [sidebarVisible])

  useEffect(() => {
    localStorage.setItem('question-atlas:sidebar-width', String(sidebarWidth))
  }, [sidebarWidth])

  const selectQuestion = useCallback((id: string) => {
    setSelectedId(id)
    setSelectedQuestion(pageQuestions.find((question) => question.id === id) ?? null)
    setInspectorOpen(true)
  }, [pageQuestions])

  const moveSelection = useCallback((delta: number) => {
    if (pageQuestions.length === 0) return
    const currentIndex = pageQuestions.findIndex((question) => question.id === selectedId)
    const nextIndex = currentIndex === -1
      ? (delta > 0 ? 0 : pageQuestions.length - 1)
      : (currentIndex + delta + pageQuestions.length) % pageQuestions.length
    const next = pageQuestions[nextIndex]
    if (!next) return
    setSelectedId(next.id)
    document.querySelector<HTMLElement>(`[data-question-id="${CSS.escape(next.id)}"]`)?.scrollIntoView({ block: 'nearest' })
  }, [pageQuestions, selectedId])

  useEffect(() => {
    const handleKeyboard = (event: KeyboardEvent) => {
      if (mode !== 'atlas') return
      const typing = /input|textarea|select/i.test(document.activeElement?.tagName ?? '')
      if (event.key === '/' && !typing) {
        event.preventDefault()
        searchRef.current?.focus()
      } else if (event.key === 'Escape') {
        if (document.activeElement === searchRef.current) {
          setFilters((current) => ({ ...current, query: '' }))
          searchRef.current?.blur()
        }
        setFiltersOpen(false)
        setInspectorOpen(false)
      } else if (!typing && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
        event.preventDefault()
        moveSelection(event.key === 'ArrowDown' ? 1 : -1)
      }
    }
    document.addEventListener('keydown', handleKeyboard)
    return () => document.removeEventListener('keydown', handleKeyboard)
  }, [mode, moveSelection])

  useEffect(() => {
    if (mode === 'practicums') {
      if (!window.location.hash.startsWith('#practicums')) window.history.replaceState(null, '', '#practicums')
    } else if (mode === 'drill') {
      if (!window.location.hash.startsWith('#drill')) window.history.replaceState(null, '', '#drill')
    } else if (window.location.hash !== '#atlas') {
      window.history.replaceState(null, '', '#atlas')
    }
  }, [mode])

  const setSegment = (key: 'paper' | 'calculator' | 'session' | 'zone' | 'status', value: string) => {
    setFilters((current) => ({ ...current, [key]: value }))
    setPage(1)
  }

  const toggleSet = (key: FilterSetKey, value: string) => {
    setFilters((current) => {
      const next = new Set(current[key])
      next.has(value) ? next.delete(value) : next.add(value)
      return { ...current, [key]: next }
    })
    setPage(1)
  }

  const resetFilters = () => {
    setFilters(freshFilters())
    setPage(1)
  }

  /** Сменить предмет: отборы сбрасываются, потому что чужими они не бывают. */
  const switchSubject = useCallback((next: string) => {
    setSubject((current) => {
      if (next === current) return current
      try { localStorage.setItem(SUBJECT_KEY, next) } catch { /* не беда */ }
      setFilters(freshFilters())
      setFacets(null)
      setPage(1)
      setSelectedId(null)
      setSelectedQuestion(null)
      setInspectorOpen(false)
      return next
    })
  }, [])

  // Какие предметы подняты. Спрашивается один раз: список меняется с
  // выкаткой, а не по ходу работы.
  useEffect(() => {
    const controller = new AbortController()
    fetchSubjects(controller.signal)
      .then((list) => {
        const ready = list.filter((entry) => entry.ready)
        setSubjects(ready)
        // Предмет из прошлого захода мог исчезнуть или остаться без индекса.
        if (ready.length && !ready.some((entry) => entry.id === subject)) {
          const fallback = ready.find((entry) => entry.default) ?? ready[0]
          if (fallback) switchSubject(fallback.id)
        }
      })
      .catch(() => { /* один предмет — переключать нечего */ })
    return () => controller.abort()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const closeOverlays = () => {
    setFiltersOpen(false)
    setInspectorOpen(false)
  }

  const openPracticumQuestions = (topic: string) => {
    setFilters({ ...freshFilters(), query: topic })
    setPage(1)
    setMode('atlas')
  }

  return (
    <div className="flex h-full flex-col bg-canvas text-ink">
      <a className="fixed top-1.5 left-2 z-50 -translate-y-[150%] bg-ink px-3 py-2 text-canvas focus:translate-y-0" href={mode === 'atlas' ? '#results' : '#practicums'}>
        {mode === 'atlas' ? t('app.skipResults') : t('top.practicums')}
      </a>

      <TopBar
        mode={mode}
        query={filters.query}
        resultCount={total}
        resultMarks={resultMarks}
        sessionCount={archiveSessionCount}
        yearRange={yearRange}
        searchRef={searchRef}
        sidebarVisible={sidebarVisible}
        filtersOpen={filtersOpen}
        onQueryChange={(query) => { setFilters((current) => ({ ...current, query })); setPage(1) }}
        onOpenFilters={() => setFiltersOpen(true)}
        onToggleSidebar={() => setSidebarVisible((visible) => !visible)}
        onModeChange={setMode}
      />

      {mode === 'drill' ? <DrillView /> : mode === 'practicums' ? <PracticumHub onOpenAtlas={openPracticumQuestions} /> : <div className="relative flex min-h-0 flex-1 overflow-hidden">
        <AnimatePresence initial={false}>
          {compactLayout && (filtersOpen || inspectorOpen) && (
            <motion.button
              className="fixed inset-x-0 top-13 bottom-8 z-20 cursor-default border-0 bg-ink/25 backdrop-blur-[1px]"
              type="button"
              aria-label={t('app.closePanel')}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.18 }}
              onClick={closeOverlays}
            />
          )}
        </AnimatePresence>

        <AnimatePresence initial={false}>
          {(compactLayout ? filtersOpen : sidebarVisible) && (
            <FilterPanel
              filters={filters}
              subject={subject}
              subjects={subjects}
              onSubjectChange={switchSubject}
              topicCounts={topicCounts}
              methodCounts={methodCounts}
              sessionCounts={sessionCounts}
              zoneCounts={zoneCounts}
              paperCounts={paperCounts}
              statusCounts={statusCounts}
              calculatorCounts={calculatorCounts}
              formCounts={formCounts}
              compact={compactLayout}
              width={sidebarWidth}
              onResize={setSidebarWidth}
              onSetSegment={setSegment}
              onToggleSet={toggleSet}
              onReset={resetFilters}
              onClose={() => setFiltersOpen(false)}
            />
          )}
        </AnimatePresence>

        <ResultsTable
          questions={pageQuestions}
          selectedId={selectedId}
          marks={resultMarks}
          total={total}
          page={page}
          pageSize={50}
          loading={loading}
          onSelect={selectQuestion}
          onReset={resetFilters}
          onPageChange={setPage}
        />

        <AnimatePresence initial={false}>
          {inspectorOpen && selectedQuestion && (
            <Inspector
              question={selectedQuestion}
              compact={compactLayout}
              onClose={() => setInspectorOpen(false)}
            />
          )}
        </AnimatePresence>
      </div>}

      <StatusBar sessionCount={archiveSessionCount} verifiedCount={verifiedCount} draftCount={draftCount} reviewed={reviewed} />
    </div>
  )
}
