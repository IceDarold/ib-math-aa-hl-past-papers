import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { FilterPanel } from './components/FilterPanel'
import { Inspector } from './components/Inspector'
import { ResultsTable } from './components/ResultsTable'
import { StatusBar } from './components/StatusBar'
import { TopBar } from './components/TopBar'
import { countBy, filterQuestions, questions } from './lib/questions'
import type { Filters, FilterSetKey } from './types'

const DEFAULT_SIDEBAR_WIDTH = 248
const MIN_SIDEBAR_WIDTH = 208
const MAX_SIDEBAR_WIDTH = 384

const initialFilters: Filters = {
  query: '',
  paper: 'all',
  calculator: 'all',
  topics: new Set(),
  methods: new Set(),
}

export default function App() {
  const [filters, setFilters] = useState<Filters>(initialFilters)
  const [selectedId, setSelectedId] = useState<string | null>(null)
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

  const filteredQuestions = useMemo(() => filterQuestions(questions, filters), [filters])
  const resultMarks = useMemo(
    () => filteredQuestions.reduce((sum, question) => sum + question.marks, 0),
    [filteredQuestions],
  )
  const selectedQuestion = useMemo(
    () => questions.find((question) => question.id === selectedId) ?? null,
    [selectedId],
  )
  const topicCounts = useMemo(() => countBy(questions, (question) => question.topicFamily), [])
  const methodCounts = useMemo(() => countBy(questions, (question) => question.methodFamily), [])

  useEffect(() => {
    if (selectedId && !filteredQuestions.some((question) => question.id === selectedId)) {
      setSelectedId(null)
      setInspectorOpen(false)
    }
  }, [filteredQuestions, selectedId])

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
    setInspectorOpen(true)
  }, [])

  const moveSelection = useCallback((delta: number) => {
    if (filteredQuestions.length === 0) return
    const currentIndex = filteredQuestions.findIndex((question) => question.id === selectedId)
    const nextIndex = currentIndex === -1
      ? (delta > 0 ? 0 : filteredQuestions.length - 1)
      : (currentIndex + delta + filteredQuestions.length) % filteredQuestions.length
    const next = filteredQuestions[nextIndex]
    if (!next) return
    setSelectedId(next.id)
    document.querySelector<HTMLElement>(`[data-question-id="${CSS.escape(next.id)}"]`)?.scrollIntoView({ block: 'nearest' })
  }, [filteredQuestions, selectedId])

  useEffect(() => {
    const handleKeyboard = (event: KeyboardEvent) => {
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
  }, [moveSelection])

  const setSegment = (key: 'paper' | 'calculator', value: string) => {
    setFilters((current) => ({ ...current, [key]: value }))
  }

  const toggleSet = (key: FilterSetKey, value: string) => {
    setFilters((current) => {
      const next = new Set(current[key])
      next.has(value) ? next.delete(value) : next.add(value)
      return { ...current, [key]: next }
    })
  }

  const resetFilters = () => {
    setFilters({ ...initialFilters, topics: new Set(), methods: new Set() })
  }

  const closeOverlays = () => {
    setFiltersOpen(false)
    setInspectorOpen(false)
  }

  return (
    <div className="flex h-full flex-col bg-canvas text-ink">
      <a className="fixed top-1.5 left-2 z-50 -translate-y-[150%] bg-ink px-3 py-2 text-canvas focus:translate-y-0" href="#results">
        К результатам
      </a>

      <TopBar
        query={filters.query}
        resultCount={filteredQuestions.length}
        resultMarks={resultMarks}
        searchRef={searchRef}
        sidebarVisible={sidebarVisible}
        filtersOpen={filtersOpen}
        onQueryChange={(query) => setFilters((current) => ({ ...current, query }))}
        onOpenFilters={() => setFiltersOpen(true)}
        onToggleSidebar={() => setSidebarVisible((visible) => !visible)}
      />

      <div className="relative flex min-h-0 flex-1 overflow-hidden">
        {compactLayout && (filtersOpen || inspectorOpen) && (
          <button className="fixed inset-x-0 top-13 bottom-8 z-20 cursor-default border-0 bg-ink/25" type="button" aria-label="Закрыть панель" onClick={closeOverlays} />
        )}

        {(compactLayout ? filtersOpen : sidebarVisible) && (
          <FilterPanel
            filters={filters}
            topicCounts={topicCounts}
            methodCounts={methodCounts}
            compact={compactLayout}
            width={sidebarWidth}
            onResize={setSidebarWidth}
            onSetSegment={setSegment}
            onToggleSet={toggleSet}
            onReset={resetFilters}
            onClose={() => setFiltersOpen(false)}
          />
        )}

        <ResultsTable
          questions={filteredQuestions}
          selectedId={selectedId}
          marks={resultMarks}
          onSelect={selectQuestion}
          onReset={resetFilters}
        />

        {inspectorOpen && selectedQuestion && (
          <Inspector
            question={selectedQuestion}
            compact={compactLayout}
            onClose={() => setInspectorOpen(false)}
          />
        )}
      </div>

      <StatusBar />
    </div>
  )
}
