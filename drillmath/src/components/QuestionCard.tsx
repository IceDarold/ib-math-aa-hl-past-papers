/** Карточка задания: один пункт настоящего билета.
 *
 * Картинка приходит с сервера: условие вопроса и один его пункт, тот,
 * что назван в подписи. Между кусками листа — тонкая черта: значит, в
 * билете между ними напечатано что-то ещё. Решать не нужно: нужно
 * узнать приём.
 */
import type { Card } from '../api'
import { api } from '../api'

export function QuestionCard({ card }: { card: Card }) {
  const pages = Math.max(card.pages || 1, 1)
  return (
    <section className="flex flex-col gap-3">
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
        <h2 className="text-[17px] font-medium text-ink">{card.reference}</h2>
        <span className="flex items-baseline gap-2 text-[12px] text-faint">
          <span>{card.marks} {card.marks === 1 ? 'балл' : card.marks < 5 ? 'балла' : 'баллов'}</span>
          <span>·</span>
          <span>{card.calculator === 'yes' ? 'с калькулятором' : 'без калькулятора'}</span>
        </span>
      </div>

      <div className="overflow-hidden rounded-2xl border border-line bg-surface shadow-card">
        {Array.from({ length: pages }, (_, index) => (
          <img
            key={index}
            src={api.page(card.block, index)}
            alt={`${card.reference}${pages > 1 ? `, страница ${index + 1}` : ''}`}
            loading="eager"
            className="page-scan w-full border-b border-line last:border-b-0"
          />
        ))}
      </div>

      <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <p className="max-w-[46ch] text-[13px] leading-relaxed text-faint">
          Решать не нужно. На карточке — условие и один пункт, тот, что
          назван сверху: каким приёмом он берётся.
        </p>
        {/* На телефоне картинка мельчает; ссылка открывает её отдельной
            вкладкой, и браузер даёт зум, которого в вёрстке нет. */}
        <a
          href={api.page(card.block, 0)}
          target="_blank"
          rel="noreferrer"
          className="shrink-0 text-[13px] text-accent hover:underline"
        >
          открыть крупнее
        </a>
      </div>
    </section>
  )
}
