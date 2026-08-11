import type { RefObject } from 'react'
import { MenuIcon, SearchIcon } from './Icons'

interface TopBarProps {
  query: string
  resultCount: number
  resultMarks: number
  searchRef: RefObject<HTMLInputElement | null>
  onQueryChange: (query: string) => void
  onOpenFilters: () => void
}

export function TopBar({
  query,
  resultCount,
  resultMarks,
  searchRef,
  onQueryChange,
  onOpenFilters,
}: TopBarProps) {
  return (
    <header className="grid h-13 shrink-0 grid-cols-[auto_auto_minmax(260px,1fr)_auto] items-center gap-6 border-b border-line bg-canvas px-4 max-[1220px]:gap-3.5 max-[960px]:grid-cols-[auto_auto_1fr] max-[960px]:gap-2.5 max-[960px]:pl-2">
      <button
        className="hidden size-8 cursor-pointer place-items-center border-0 bg-transparent max-[960px]:grid"
        type="button"
        aria-label="Открыть фильтры"
        aria-controls="filters"
        onClick={onOpenFilters}
      >
        <MenuIcon />
      </button>

      <div className="flex items-baseline gap-2 whitespace-nowrap text-[15px] max-[680px]:text-sm" aria-label="IB Math AA HL Question Atlas">
        <strong className="text-base max-[680px]:text-sm">IB Math AA HL</strong>
        <span className="text-faint max-[960px]:hidden">/</span>
        <span className="max-[960px]:hidden">Question Atlas</span>
      </div>

      <div className="whitespace-nowrap max-[960px]:hidden">
        November 2024 <span className="text-faint">· Common</span>
      </div>

      <label className="group/search mx-auto grid h-8.5 w-full max-w-155 grid-cols-[24px_1fr_auto] items-center gap-1.5 border border-line-strong bg-canvas px-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary max-[960px]:justify-self-stretch max-[680px]:grid-cols-[20px_1fr]">
        <SearchIcon className="text-muted" />
        <span className="sr-only">Поиск</span>
        <input
          ref={searchRef}
          className="h-full min-w-0 border-0 bg-transparent text-ink outline-0 placeholder:text-muted"
          type="search"
          autoComplete="off"
          placeholder="ID, topic, method…"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
        <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px] text-muted max-[680px]:hidden">/</kbd>
      </label>

      <div className="whitespace-nowrap text-xs text-muted max-[1220px]:hidden">
        <strong className="font-semibold text-ink">{resultCount}</strong> blocks <span className="text-faint">·</span>{' '}
        <strong className="font-semibold text-ink">{resultMarks}</strong> marks
      </div>
    </header>
  )
}
