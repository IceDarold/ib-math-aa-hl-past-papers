import { ArrowUpDownIcon } from './Icons'
import { useI18n } from '../i18n'
import { motion, useReducedMotion } from 'motion/react'

interface StatusBarProps {
  sessionCount: number
  verifiedCount: number
  draftCount: number
}

export function StatusBar({ sessionCount, verifiedCount, draftCount }: StatusBarProps) {
  const { count, t } = useI18n()
  const reduceMotion = useReducedMotion()
  return (
    <footer className="flex h-8 shrink-0 items-center justify-between border-t border-line bg-canvas px-3.5 text-[11px] text-muted max-[680px]:justify-center">
      <span className="flex items-center gap-1.5">
        <motion.span
          className="size-2 rounded-full bg-info"
          animate={reduceMotion ? undefined : { scale: [1, 1.35, 1], opacity: [0.75, 1, 0.75] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: 'easeInOut' }}
        />
        {count('sessions', sessionCount)} — {count('drafts', draftCount)} — {count('verifiedBlocks', verifiedCount)}
      </span>
      <span className="flex items-center gap-1.5 max-[680px]:hidden">
        <kbd className="inline-flex h-5 items-center gap-0.5 rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]"><ArrowUpDownIcon className="size-3" />↑↓</kbd> {t('status.select')}
        <i className="not-italic text-faint">—</i>
        <kbd className="inline-flex h-5 min-w-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]">/</kbd> {t('status.search')}
        <i className="not-italic text-faint">—</i>
        <kbd className="inline-flex h-5 items-center justify-center rounded-[3px] border border-line border-b-line-strong bg-surface px-1.5 font-mono text-[11px]">esc</kbd> {t('status.close')}
      </span>
    </footer>
  )
}
