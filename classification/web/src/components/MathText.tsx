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
        ? <InlineMath key={`${index}-${segment.value}`} tex={segment.value} />
        : <span key={`${index}-${segment.value}`}>{segment.value}</span>)}
    </span>
  )
}

function InlineMath({ tex }: { tex: string }) {
  const elementRef = useRef<HTMLSpanElement>(null)

  useLayoutEffect(() => {
    if (!elementRef.current) return
    katex.render(tex, elementRef.current, {
      displayMode: false,
      output: 'htmlAndMathml',
      throwOnError: false,
      strict: 'warn',
      trust: false,
    })
  }, [tex])

  return <span ref={elementRef} className="math-inline" data-tex={tex} />
}
