import type { Filters, FilterSetKey } from '../types'
import { formatKey } from '../lib/questions'
import { CheckIcon, CloseIcon, ResetIcon } from './Icons'

interface FilterPanelProps {
  filters: Filters
  topicCounts: Array<[string, number]>
  methodCounts: Array<[string, number]>
  open: boolean
  onSetSegment: (key: 'paper' | 'calculator', value: string) => void
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
  open,
  onSetSegment,
  onToggleSet,
  onReset,
  onClose,
}: FilterPanelProps) {
  return (
    <aside
      id="filters"
      aria-label="Фильтры"
      className={`relative flex min-h-0 min-w-0 flex-col gap-4.5 overflow-y-auto border-r border-line bg-canvas px-3.5 py-3.5 max-[960px]:fixed max-[960px]:inset-y-13 max-[960px]:bottom-8 max-[960px]:z-30 max-[960px]:w-[min(310px,88vw)] max-[960px]:shadow-overlay max-[960px]:transition-transform max-[960px]:duration-200 max-[960px]:ease-out-quart ${open ? 'max-[960px]:translate-x-0' : 'max-[960px]:-translate-x-full'}`}
    >
      <div className="flex items-center justify-between">
        <h2 className="m-0 text-sm font-semibold">Фильтры</h2>
        <button
          className="hidden size-8 cursor-pointer place-items-center border-0 bg-transparent max-[960px]:grid"
          type="button"
          aria-label="Закрыть фильтры"
          onClick={onClose}
        >
          <CloseIcon />
        </button>
      </div>

      <SegmentField
        legend="Бумага"
        value={filters.paper}
        options={[['all', 'Все'], ['1', 'P1'], ['2', 'P2'], ['3', 'P3']]}
        onChange={(value) => onSetSegment('paper', value)}
      />

      <SegmentField
        legend="Калькулятор"
        value={filters.calculator}
        options={[['all', 'Любой'], ['no', 'No'], ['yes', 'Yes']]}
        onChange={(value) => onSetSegment('calculator', value)}
      />

      <CheckboxFilter
        label="Тема"
        counts={topicCounts}
        selected={filters.topics}
        onToggle={(value) => onToggleSet('topics', value)}
      />

      <CheckboxFilter
        label="Семейство метода"
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
        Сбросить фильтры
      </button>
    </aside>
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
