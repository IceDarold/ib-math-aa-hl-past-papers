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
        : <span key={`${index}-${segment.value}`}>{emphasise(segment.value)}</span>)}
    </span>
  )
}

/** «Найдите **точное** значение» — жирным.
 *
 * Выделение в условиях расставлено там, где мимо него проходят: «целых»,
 * «тупой», «а затем». Рисовать его было некому, и на экране стояли сами
 * звёздочки.
 *
 * Звёздочка бывает и не разметкой: ответы печатаются так, как их пишет
 * sympy, и `2*x**2 + 3*x - 6` содержит целых две. Поэтому парой считается
 * только та, что стоит по краям слова: перед открывающей и после
 * закрывающей не должно быть буквы или цифры.
 */
const EMPHASIS = /(?<![\p{L}\p{N}])\*\*(?=\S)(.+?)(?<=\S)\*\*(?![\p{L}\p{N}])/gu

function emphasise(value: string) {
  return value.split(EMPHASIS).map((piece, index) => (
    index % 2 ? <strong key={index}>{piece}</strong> : piece
  ))
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
