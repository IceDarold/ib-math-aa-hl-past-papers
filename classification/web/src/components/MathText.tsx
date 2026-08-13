import katex from 'katex'
import { useLayoutEffect, useMemo, useRef } from 'react'
import { tokenizeMathText } from '../lib/math'

interface MathTextProps {
  children: string
  className?: string
}

export function MathText({ children, className }: MathTextProps) {
  const segments = useMemo(() => tokenizeMathText(children), [children])
  return (
    <span className={className}>
      {segments.map((segment, index) => segment.type === 'math'
        ? <InlineMath key={`${index}-${segment.value}`} tex={segment.value} fallback={segment.source ?? segment.value} display={segment.display} />
        : <span key={`${index}-${segment.value}`}>{segment.value}</span>)}
    </span>
  )
}

function InlineMath({ tex, fallback, display = false }: { tex: string; fallback: string; display?: boolean }) {
  const elementRef = useRef<HTMLSpanElement>(null)

  useLayoutEffect(() => {
    if (!elementRef.current) return
    try {
      katex.render(tex, elementRef.current, {
        displayMode: display,
        output: 'htmlAndMathml',
        throwOnError: true,
        strict: 'ignore',
        trust: false,
      })
      delete elementRef.current.dataset.mathError
    } catch {
      elementRef.current.textContent = fallback
      elementRef.current.dataset.mathError = 'true'
    }
  }, [fallback, tex])

  return <span ref={elementRef} className="math-inline" data-tex={tex} />
}
