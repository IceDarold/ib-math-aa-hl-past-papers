import type { RefObject } from 'react'
import { AnimatePresence, LayoutGroup, motion } from 'motion/react'
import { useI18n } from '../i18n'
import { MenuIcon, PanelLeftIcon, SearchIcon } from './Icons'

interface TopBarProps {
  query: string
  resultCount: number
  resultMarks: number
  sessionCount: number
  yearRange: string
  searchRef: RefObject<HTMLInputElement | null>
  sidebarVisible: boolean
  filtersOpen: boolean
  onQueryChange: (query: string) => void
  onOpenFilters: () => void
  onToggleSidebar: () => void
}

export function TopBar({
  query,
  resultCount,
  resultMarks,
  sessionCount,
  yearRange,
  searchRef,
  sidebarVisible,
  filtersOpen,
  onQueryChange,
  onOpenFilters,
  onToggleSidebar,
}: TopBarProps) {
  const { count, locale, setLocale, t } = useI18n()
  return (
    <header className="grid h-13 shrink-0 grid-cols-[auto_auto_auto_minmax(260px,1fr)_auto_auto] items-center gap-4 border-b border-line bg-canvas px-3 max-[1220px]:gap-3 max-[960px]:grid-cols-[auto_auto_minmax(0,1fr)_auto] max-[960px]:gap-2.5 max-[960px]:pl-2">
      <motion.button
        className="grid size-8 cursor-pointer place-items-center border border-transparent bg-transparent hover:border-line hover:bg-surface max-[960px]:hidden"
        type="button"
        aria-label={sidebarVisible ? t('top.hideSidebar') : t('top.showSidebar')}
        aria-controls="filters"
        aria-expanded={sidebarVisible}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.86 }}
        onClick={onToggleSidebar}
      >
        <motion.span className="grid place-items-center" animate={{ rotateY: sidebarVisible ? 0 : 180 }}>
          <PanelLeftIcon />
        </motion.span>
      </motion.button>

      <motion.button
        className="hidden size-8 cursor-pointer place-items-center border-0 bg-transparent max-[960px]:grid"
        type="button"
        aria-label={t('top.openFilters')}
        aria-controls="filters"
        aria-expanded={filtersOpen}
        whileHover={{ scale: 1.08 }}
        whileTap={{ scale: 0.86, rotate: -4 }}
        onClick={onOpenFilters}
      >
        <MenuIcon />
      </motion.button>

      <div className="flex items-baseline gap-2 whitespace-nowrap text-[15px] max-[680px]:text-sm" aria-label={`IB Math AA HL · ${t('brand.atlas')}`}>
        <strong className="text-base max-[680px]:text-sm">IB Math AA HL</strong>
        <span className="text-faint max-[960px]:hidden">/</span>
        <span className="max-[960px]:hidden">{t('brand.atlas')}</span>
      </div>

      <div className="whitespace-nowrap max-[960px]:hidden">
        {yearRange} <span className="text-faint">· {count('sessions', sessionCount)}</span>
      </div>

      <motion.label
        className="group/search mx-auto grid h-8.5 w-full min-w-0 max-w-155 grid-cols-[24px_1fr_auto] items-center gap-1.5 border border-line-strong bg-canvas px-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary max-[960px]:justify-self-stretch max-[680px]:grid-cols-[20px_1fr]"
        whileHover={{ scale: 1.006 }}
      >
        <SearchIcon className="text-muted" />
        <span className="sr-only">{t('top.search')}</span>
        <input
          ref={searchRef}
          className="h-full min-w-0 border-0 bg-transparent text-ink outline-0 placeholder:text-muted"
          type="search"
          autoComplete="off"
          placeholder={t('top.searchPlaceholder')}
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
        />
        <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px] text-muted max-[680px]:hidden">/</kbd>
      </motion.label>

      <div className="whitespace-nowrap text-xs text-muted max-[1220px]:hidden">
        <AnimatedMetric value={`${locale}-${resultCount}`} label={count('blocks', resultCount)} /> <span className="text-faint">·</span>{' '}
        <AnimatedMetric value={`${locale}-${resultMarks}`} label={count('marks', resultMarks)} />
      </div>

      <LayoutGroup id="language-toggle">
        <div className="grid grid-cols-2 border border-line-strong" role="group" aria-label={t('language.label')}>
          {(['ru', 'en'] as const).map((option) => {
            const active = locale === option
            return (
              <motion.button
                key={option}
                className={`relative isolate h-7 min-w-7 cursor-pointer border-0 bg-canvas px-1.5 font-mono text-[10px] transition-colors duration-150 ${active ? 'text-canvas' : 'text-muted hover:bg-surface hover:text-ink'}`}
                type="button"
                aria-label={option === 'ru' ? t('language.russian') : t('language.english')}
                aria-pressed={active}
                whileTap={{ scale: 0.88 }}
                onClick={() => setLocale(option)}
              >
                {active && (
                  <motion.span
                    layoutId="language-active"
                    className="absolute inset-0 z-0 bg-ink"
                    transition={{ type: 'spring', stiffness: 560, damping: 38, mass: 0.62 }}
                    aria-hidden="true"
                  />
                )}
                <span className="relative z-1">{option.toUpperCase()}</span>
              </motion.button>
            )
          })}
        </div>
      </LayoutGroup>
    </header>
  )
}

function AnimatedMetric({ value, label }: { value: string; label: string }) {
  return (
    <span className="relative inline-grid overflow-hidden align-bottom">
      <AnimatePresence initial={false} mode="popLayout">
        <motion.strong
          key={value}
          className="col-start-1 row-start-1 font-semibold text-ink"
          initial={{ opacity: 0, y: -8, filter: 'blur(3px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          exit={{ opacity: 0, y: 8, filter: 'blur(3px)' }}
          transition={{ duration: 0.16 }}
        >
          {label}
        </motion.strong>
      </AnimatePresence>
    </span>
  )
}
