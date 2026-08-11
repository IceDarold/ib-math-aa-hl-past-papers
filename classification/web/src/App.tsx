import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { FilterPanel } from './components/FilterPanel'
import { Inspector } from './components/Inspector'
import { ResultsTable } from './components/ResultsTable'
import { StatusBar } from './components/StatusBar'
import { TopBar } from './components/TopBar'
import { countBy, filterQuestions, questions } from './lib/questions'
import type { Filters, FilterSetKey } from './types'

const initialFilters: Filters = {
  query: '',
  paper: 'all',
  calculator: 'all',
  topics: new Set(),
  methods: new Set(),
}

export default function App() {
  const [filters, setFilters] = useState<Filters>(initialFilters)
  const [selectedId, setSelectedId] = useState<string | null>(questions[0]?.id ?? null)
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
    if (!filteredQuestions.some((question) => question.id === selectedId)) {
      setSelectedId(filteredQuestions[0]?.id ?? null)
    }
  }, [filteredQuestions, selectedId])

  const selectQuestion = useCallback((id: string, revealInspector: boolean) => {
    setSelectedId(id)
    if (revealInspector) setInspectorOpen(true)
  }, [])

  const moveSelection = useCallback((delta: number) => {
    if (filteredQuestions.length === 0) return
    const currentIndex = Math.max(0, filteredQuestions.findIndex((question) => question.id === selectedId))
    const nextIndex = (currentIndex + delta + filteredQuestions.length) % filteredQuestions.length
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
        onQueryChange={(query) => setFilters((current) => ({ ...current, query }))}
        onOpenFilters={() => setFiltersOpen(true)}
      />

      <div className="grid min-h-0 flex-1 grid-cols-[248px_minmax(480px,1fr)_390px] max-[1220px]:grid-cols-[224px_minmax(440px,1fr)_340px] max-[960px]:grid-cols-1">
        {(filtersOpen || inspectorOpen) && (
          <button className="fixed inset-x-0 top-13 bottom-8 z-20 hidden cursor-default border-0 bg-ink/25 max-[960px]:block" type="button" aria-label="Закрыть панель" onClick={closeOverlays} />
        )}

        <FilterPanel
          filters={filters}
          topicCounts={topicCounts}
          methodCounts={methodCounts}
          open={filtersOpen}
          onSetSegment={setSegment}
          onToggleSet={toggleSet}
          onReset={resetFilters}
          onClose={() => setFiltersOpen(false)}
        />

        <ResultsTable
          questions={filteredQuestions}
          selectedId={selectedId}
          marks={resultMarks}
          onSelect={selectQuestion}
          onReset={resetFilters}
          onOpenInspector={() => setInspectorOpen(true)}
        />

        <Inspector
          question={selectedQuestion}
          open={inspectorOpen}
          onClose={() => setInspectorOpen(false)}
        />
      </div>

      <StatusBar />
    </div>
  )
}
