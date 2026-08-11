import { ArrowUpDownIcon } from './Icons'

interface StatusBarProps {
  sessionCount: number
  verifiedCount: number
  draftCount: number
}

export function StatusBar({ sessionCount, verifiedCount, draftCount }: StatusBarProps) {
  return (
    <footer className="flex h-8 shrink-0 items-center justify-between border-t border-line bg-canvas px-3.5 text-[11px] text-muted max-[680px]:justify-center">
      <span className="flex items-center gap-1.5">
        <span className="size-2 rounded-full bg-info" />
        {sessionCount} сессий · {draftCount} AI draft · {verifiedCount} проверено
      </span>
      <span className="flex items-center gap-1.5 max-[680px]:hidden">
        <kbd className="inline-flex h-5 items-center gap-0.5 rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]"><ArrowUpDownIcon className="size-3" />↑↓</kbd> выбрать
        <i className="not-italic text-faint">·</i>
        <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]">/</kbd> поиск
        <i className="not-italic text-faint">·</i>
        <kbd className="inline-flex h-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]">esc</kbd> закрыть
      </span>
    </footer>
  )
}
