import { useEffect, useId, useRef, useState } from 'react'
import type { CSSProperties, KeyboardEvent, PointerEvent as ReactPointerEvent } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import type { Filters, FilterSetKey } from '../types'
import { formatKey } from '../lib/questions'
import { useI18n } from '../i18n'
import { CheckIcon, CloseIcon, ResetIcon } from './Icons'

interface FilterPanelProps {
  filters: Filters
  topicCounts: Array<[string, number]>
  methodCounts: Array<[string, number]>
  sessionCounts: Array<[string, number]>
  zoneCounts: Array<[string, number]>
  compact: boolean
  width: number
  onResize: (width: number) => void
  onSetSegment: (key: 'paper' | 'calculator' | 'session' | 'zone' | 'status', value: string) => void
  onToggleSet: (key: FilterSetKey, value: string) => void
  onReset: () => void
  onClose: () => void
}

const baseSegmentClass = 'h-8 cursor-pointer border border-r-0 border-line bg-canvas px-2 text-xs transition-colors duration-150 ease-out-quart last:border-r hover:bg-surface'
const activeSegmentClass = 'relative z-1 text-primary-dark'

export function FilterPanel({
  filters,
  topicCounts,
  methodCounts,
  sessionCounts,
  zoneCounts,
  compact,
  width,
  onResize,
  onSetSegment,
  onToggleSet,
  onReset,
  onClose,
}: FilterPanelProps) {
  const { t } = useI18n()
  return (
    <motion.aside
      id="filters"
      aria-label={t('filters.label')}
      style={{ '--filter-panel-width': `${width}px` } as CSSProperties}
      className={`filter-panel z-10 flex min-h-0 min-w-0 shrink-0 flex-col gap-4.5 overflow-y-auto border-r border-line bg-canvas px-3.5 py-3.5 ${compact ? 'fixed top-13 bottom-8 left-0 z-30 shadow-overlay' : 'relative'}`}
      initial={{ opacity: 0, x: compact ? -32 : -16, filter: 'blur(5px)' }}
      animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, x: compact ? -28 : -12, filter: 'blur(4px)' }}
      transition={{
        x: { type: 'spring', stiffness: 480, damping: 38, mass: 0.75 },
        opacity: { duration: 0.18 },
        filter: { duration: 0.2 },
      }}
    >
      <div className="flex items-center justify-between">
        <h2 className="m-0 text-sm font-semibold">{t('filters.label')}</h2>
        <motion.button
          className={`size-8 cursor-pointer place-items-center border-0 bg-transparent ${compact ? 'grid' : 'hidden'}`}
          type="button"
          aria-label={t('filters.close')}
          whileHover={{ rotate: 5, scale: 1.08 }}
          whileTap={{ rotate: -5, scale: 0.86 }}
          onClick={onClose}
        >
          <CloseIcon />
        </motion.button>
      </div>

      <SegmentField
        legend={t('filters.paper')}
        value={filters.paper}
        options={[['all', t('filters.all')], ['1', 'P1'], ['2', 'P2'], ['3', 'P3']]}
        onChange={(value) => onSetSegment('paper', value)}
      />

      <SelectField
        legend={t('filters.session')}
        value={filters.session}
        options={sessionCounts}
        onChange={(value) => onSetSegment('session', value)}
      />

      <SelectField
        legend={t('filters.zone')}
        value={filters.zone}
        options={zoneCounts}
        onChange={(value) => onSetSegment('zone', value)}
      />

      <SegmentField
        legend={t('filters.status')}
        value={filters.status}
        options={[["all", t('filters.all')], ["manual_verified", t('filters.manual')], ["ai_draft", t('filters.aiDraft')]]}
        onChange={(value) => onSetSegment('status', value)}
      />

      <SegmentField
        legend={t('filters.calculator')}
        value={filters.calculator}
        options={[['all', t('filters.any')], ['no', t('filters.no')], ['yes', t('filters.yes')]]}
        onChange={(value) => onSetSegment('calculator', value)}
      />

      <CheckboxFilter
        label={t('filters.topic')}
        counts={topicCounts}
        selected={filters.topics}
        onToggle={(value) => onToggleSet('topics', value)}
      />

      <CheckboxFilter
        label={t('filters.methodFamily')}
        counts={methodCounts}
        selected={filters.methods}
        onToggle={(value) => onToggleSet('methods', value)}
      />

      <motion.button
        className="mt-auto flex cursor-pointer items-center gap-1.5 border-0 bg-transparent py-2 text-left text-primary hover:text-primary-dark"
        type="button"
        whileHover={{ x: 4 }}
        whileTap={{ scale: 0.96 }}
        onClick={onReset}
      >
        <ResetIcon className="size-4" />
        {t('filters.reset')}
      </motion.button>

      {!compact && <SidebarResizeHandle width={width} onResize={onResize} />}
    </motion.aside>
  )
}

function SelectField({
  legend,
  value,
  options,
  onChange,
}: {
  legend: string
  value: string
  options: Array<[string, number]>
  onChange: (value: string) => void
}) {
  const { t } = useI18n()
  return (
    <label className="grid gap-1.5 text-xs font-semibold">
      {legend}
      <motion.select
        className="h-8 w-full cursor-pointer border border-line-strong bg-canvas px-2 text-xs font-normal text-ink outline-none hover:bg-surface focus:border-primary focus:ring-1 focus:ring-primary"
        value={value}
        whileFocus={{ scale: 1.012 }}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="all">{t('filters.all')}</option>
        {options.map(([option, count]) => <option key={option} value={option}>{option} — {count}</option>)}
      </motion.select>
    </label>
  )
}

const MIN_WIDTH = 208
const MAX_WIDTH = 384

function SidebarResizeHandle({ width, onResize }: { width: number; onResize: (width: number) => void }) {
  const { t } = useI18n()
  const drag = useRef<{ x: number; width: number } | null>(null)
  const clamp = (value: number) => Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, value))

  useEffect(() => {
    const handlePointerMove = (event: globalThis.PointerEvent) => {
      if (!drag.current) return
      onResize(clamp(drag.current.width + event.clientX - drag.current.x))
    }

    const stopDragging = () => {
      drag.current = null
    }

    window.addEventListener('pointermove', handlePointerMove)
    window.addEventListener('pointerup', stopDragging)
    window.addEventListener('pointercancel', stopDragging)
    return () => {
      window.removeEventListener('pointermove', handlePointerMove)
      window.removeEventListener('pointerup', stopDragging)
      window.removeEventListener('pointercancel', stopDragging)
    }
  }, [onResize])

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    event.preventDefault()
    drag.current = { x: event.clientX, width }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault()
      onResize(clamp(width + (event.key === 'ArrowRight' ? 16 : -16)))
    } else if (event.key === 'Home') {
      event.preventDefault()
      onResize(MIN_WIDTH)
    } else if (event.key === 'End') {
      event.preventDefault()
      onResize(MAX_WIDTH)
    }
  }

  return (
    <div
      className="group absolute inset-y-0 -right-1.5 z-20 w-3 cursor-col-resize touch-none outline-none"
      role="separator"
      aria-label={t('filters.resize')}
      aria-orientation="vertical"
      aria-valuemin={MIN_WIDTH}
      aria-valuemax={MAX_WIDTH}
      aria-valuenow={Math.round(width)}
      tabIndex={0}
      title={t('filters.resizeHint')}
      onDoubleClick={() => onResize(248)}
      onKeyDown={handleKeyDown}
      onPointerDown={handlePointerDown}
    >
      <span className="mx-auto block h-full w-px bg-transparent transition-colors duration-150 group-hover:bg-primary group-focus-visible:bg-primary" />
    </div>
  )
}

interface SegmentFieldProps {
  legend: string
  value: string
  options: Array<[string, string]>
  onChange: (value: string) => void
}

function SegmentField({ legend, value, options, onChange }: SegmentFieldProps) {
  const segmentId = useId()
  return (
    <fieldset className="m-0 border-0 p-0">
      <legend className="mb-1.5 p-0 text-xs font-semibold">{legend}</legend>
      <div className="grid auto-cols-fr grid-flow-col">
        {options.map(([optionValue, label]) => {
          const active = optionValue === value
          return (
            <motion.button
              key={optionValue}
              className={`${baseSegmentClass} isolate ${active ? activeSegmentClass : ''}`}
              type="button"
              aria-pressed={active}
              whileHover={{ y: -1 }}
              whileTap={{ scale: 0.94, y: 0 }}
              onClick={() => onChange(optionValue)}
            >
              {active && (
                <motion.span
                  layoutId={`segment-${segmentId}`}
                  className="absolute inset-[-1px] z-0 border border-primary bg-primary-soft"
                  transition={{ type: 'spring', stiffness: 520, damping: 38, mass: 0.65 }}
                  aria-hidden="true"
                />
              )}
              <span className="relative z-1">{label}</span>
            </motion.button>
          )
        })}
      </div>
    </fieldset>
  )
}

interface CheckboxFilterProps {
  label: string
  counts: Array<[string, number]>
  selected: Set<string>
  onToggle: (value: string) => void
}

function CheckboxFilter({ label, counts, selected, onToggle }: CheckboxFilterProps) {
  const [open, setOpen] = useState(true)
  return (
    <section className="border-t border-line pt-2.5">
      <motion.button
        className="flex w-full cursor-pointer items-center border-0 bg-transparent p-0 text-left text-xs font-semibold"
        type="button"
        aria-expanded={open}
        whileTap={{ scale: 0.98 }}
        onClick={() => setOpen((current) => !current)}
      >
        {label}
        <AnimatePresence initial={false} mode="popLayout">
          {selected.size > 0 && (
            <motion.span
              key={selected.size}
              className="ml-1.5 font-medium text-primary"
              initial={{ opacity: 0, scale: 0.7, y: 3 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.7, y: -3 }}
            >
              — {selected.size}
            </motion.span>
          )}
        </AnimatePresence>
        <motion.span className="ml-auto text-muted" animate={{ rotate: open ? 180 : 0 }} aria-hidden="true">⌄</motion.span>
      </motion.button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            className="overflow-hidden"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ height: { duration: 0.24 }, opacity: { duration: 0.15 } }}
          >
            <div className="grid gap-1.5 pt-2.5">
              {counts.map(([key, count]) => {
                const checked = selected.has(key)
                return (
                  <motion.label
                    key={key}
                    className="grid cursor-pointer grid-cols-[16px_minmax(0,1fr)_auto] items-start gap-1.5 text-xs text-muted hover:text-ink"
                    whileHover={{ x: 2 }}
                    whileTap={{ scale: 0.985 }}
                  >
                    <input
                      className="peer sr-only"
                      type="checkbox"
                      checked={checked}
                      onChange={() => onToggle(key)}
                    />
                    <motion.span
                      className="grid size-3.5 place-items-center border border-line-strong bg-canvas peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-1"
                      animate={checked
                        ? { scale: [1, 1.16, 1], borderColor: 'var(--color-primary)', backgroundColor: 'var(--color-primary)' }
                        : { scale: 1, borderColor: 'var(--color-line-strong)', backgroundColor: 'var(--color-canvas)' }}
                      transition={{ duration: 0.18 }}
                    >
                      <AnimatePresence initial={false}>
                        {checked && (
                          <motion.span initial={{ scale: 0.2, rotate: -25 }} animate={{ scale: 1, rotate: 0 }} exit={{ scale: 0.2, rotate: 20 }}>
                            <CheckIcon className="size-3 text-white" />
                          </motion.span>
                        )}
                      </AnimatePresence>
                    </motion.span>
                    <span>{formatKey(key)}</span>
                    <span className="tabular-nums text-faint">{count}</span>
                  </motion.label>
                )
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  )
}
