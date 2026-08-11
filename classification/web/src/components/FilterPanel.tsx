import { useEffect, useRef } from 'react'
import type { CSSProperties, KeyboardEvent, PointerEvent as ReactPointerEvent } from 'react'
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
const activeSegmentClass = 'relative z-1 border-primary! bg-primary-soft text-primary-dark'

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
    <aside
      id="filters"
      aria-label={t('filters.label')}
      style={{ '--filter-panel-width': `${width}px` } as CSSProperties}
      className={`filter-panel z-10 flex min-h-0 min-w-0 shrink-0 flex-col gap-4.5 overflow-y-auto border-r border-line bg-canvas px-3.5 py-3.5 ${compact ? 'fixed top-13 bottom-8 left-0 z-30 shadow-overlay motion-safe:animate-[filter-panel-in_180ms_var(--ease-out-quart)]' : 'relative'}`}
    >
      <div className="flex items-center justify-between">
        <h2 className="m-0 text-sm font-semibold">{t('filters.label')}</h2>
        <button
          className={`size-8 cursor-pointer place-items-center border-0 bg-transparent ${compact ? 'grid' : 'hidden'}`}
          type="button"
          aria-label={t('filters.close')}
          onClick={onClose}
        >
          <CloseIcon />
        </button>
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

      <button
        className="mt-auto flex cursor-pointer items-center gap-1.5 border-0 bg-transparent py-2 text-left text-primary hover:text-primary-dark"
        type="button"
        onClick={onReset}
      >
        <ResetIcon className="size-4" />
        {t('filters.reset')}
      </button>

      {!compact && <SidebarResizeHandle width={width} onResize={onResize} />}
    </aside>
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
      <select
        className="h-8 w-full cursor-pointer border border-line-strong bg-canvas px-2 text-xs font-normal text-ink outline-none hover:bg-surface focus:border-primary focus:ring-1 focus:ring-primary"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="all">{t('filters.all')}</option>
        {options.map(([option, count]) => <option key={option} value={option}>{option} · {count}</option>)}
      </select>
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
  return (
    <fieldset className="m-0 border-0 p-0">
      <legend className="mb-1.5 p-0 text-xs font-semibold">{legend}</legend>
      <div className="grid auto-cols-fr grid-flow-col">
        {options.map(([optionValue, label]) => {
          const active = optionValue === value
          return (
            <button
              key={optionValue}
              className={`${baseSegmentClass} ${active ? activeSegmentClass : ''}`}
              type="button"
              aria-pressed={active}
              onClick={() => onChange(optionValue)}
            >
              {label}
            </button>
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
  return (
    <details className="border-t border-line pt-2.5" open>
      <summary className="flex cursor-pointer list-none items-center text-xs font-semibold marker:hidden">
        {label}
        {selected.size > 0 && <span className="ml-1.5 font-medium text-primary">· {selected.size}</span>}
        <span className="ml-auto text-muted group-open:rotate-180" aria-hidden="true">⌄</span>
      </summary>
      <div className="mt-2.5 grid gap-1.5">
        {counts.map(([key, count]) => {
          const checked = selected.has(key)
          return (
            <label key={key} className="grid cursor-pointer grid-cols-[16px_minmax(0,1fr)_auto] items-start gap-1.5 text-xs text-muted hover:text-ink">
              <input
                className="peer sr-only"
                type="checkbox"
                checked={checked}
                onChange={() => onToggle(key)}
              />
              <span className="grid size-3.5 place-items-center border border-line-strong bg-canvas peer-checked:border-primary peer-checked:bg-primary peer-focus-visible:ring-2 peer-focus-visible:ring-primary peer-focus-visible:ring-offset-1">
                {checked && <CheckIcon className="size-3 text-white" />}
              </span>
              <span>{formatKey(key)}</span>
              <span className="tabular-nums text-faint">{count}</span>
            </label>
          )
        })}
      </div>
    </details>
  )
}
