import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'

export type Locale = 'ru' | 'en'
export type Countable = 'blocks' | 'marks' | 'sessions' | 'drafts' | 'verifiedBlocks'

const messages = {
  ru: {
    'app.skipResults': 'К результатам',
    'app.closePanel': 'Закрыть панель',
    'brand.atlas': 'Атлас заданий',
    'language.label': 'Язык интерфейса',
    'language.russian': 'Русский',
    'language.english': 'English',
    'top.hideSidebar': 'Скрыть боковую панель',
    'top.showSidebar': 'Показать боковую панель',
    'top.openFilters': 'Открыть фильтры',
    'top.search': 'Поиск',
    'top.searchPlaceholder': 'ID, тема, метод…',
    'filters.label': 'Фильтры',
    'filters.close': 'Закрыть фильтры',
    'filters.paper': 'Бумага',
    'filters.session': 'Сессия',
    'filters.zone': 'Зона',
    'filters.status': 'Статус',
    'filters.calculator': 'Калькулятор',
    'filters.topic': 'Тема',
    'filters.methodFamily': 'Семейство метода',
    'filters.all': 'Все',
    'filters.any': 'Любой',
    'filters.no': 'Нет',
    'filters.yes': 'Да',
    'filters.manual': 'Проверено',
    'filters.aiDraft': 'Черновик ИИ',
    'filters.reset': 'Сбросить фильтры',
    'filters.resize': 'Изменить ширину боковой панели',
    'filters.resizeHint': 'Перетащите, чтобы изменить ширину',
    'results.task': 'Задание',
    'results.topic': 'Тема',
    'results.method': 'Метод',
    'results.marks': 'Баллы',
    'results.verified': 'проверено',
    'results.pages': 'с.',
    'results.emptyTitle': 'Ничего не найдено',
    'results.emptyBody': 'Измените запрос или сбросьте фильтры.',
    'results.reset': 'Сбросить',
    'inspector.label': 'Детали задания',
    'inspector.manualVerified': 'Проверено вручную',
    'inspector.aiDraft': 'Черновик ИИ',
    'inspector.close': 'Закрыть детали',
    'inspector.paper': 'Бумага',
    'inspector.calculator': 'с калькулятором',
    'inspector.nonCalculator': 'без калькулятора',
    'inspector.classification': 'Классификация',
    'inspector.primaryTopic': 'Основная тема',
    'inspector.secondary': 'Дополнительные',
    'inspector.methodFamily': 'Семейство метода',
    'inspector.methodTags': 'Теги метода',
    'inspector.sourcePages': 'Страницы источника',
    'inspector.markschemePages': 'Страницы схемы',
    'inspector.reviewFlags': 'Флаги проверки',
    'inspector.solutionPath': 'Путь решения',
    'inspector.alternatives': 'Допустимые альтернативы',
    'inspector.noAlternative': 'В схеме оценивания отдельный альтернативный маршрут не указан.',
    'inspector.evidence': 'Основание классификации',
    'inspector.confidence': 'Уверенность',
    'inspector.segmentation': 'сегментация',
    'inspector.topic': 'тема',
    'inspector.method': 'метод',
    'inspector.noEvidence': 'Основание не указано.',
    'inspector.msPage': 'МС с.',
    'inspector.source': 'Источник',
    'inspector.questionPaper': 'Условия заданий',
    'inspector.markscheme': 'Схема оценивания',
    'status.select': 'выбрать',
    'status.search': 'поиск',
    'status.close': 'закрыть',
  },
  en: {
    'app.skipResults': 'Skip to results',
    'app.closePanel': 'Close panel',
    'brand.atlas': 'Question Atlas',
    'language.label': 'Interface language',
    'language.russian': 'Russian',
    'language.english': 'English',
    'top.hideSidebar': 'Hide sidebar',
    'top.showSidebar': 'Show sidebar',
    'top.openFilters': 'Open filters',
    'top.search': 'Search',
    'top.searchPlaceholder': 'ID, topic, method…',
    'filters.label': 'Filters',
    'filters.close': 'Close filters',
    'filters.paper': 'Paper',
    'filters.session': 'Session',
    'filters.zone': 'Zone',
    'filters.status': 'Status',
    'filters.calculator': 'Calculator',
    'filters.topic': 'Topic',
    'filters.methodFamily': 'Method family',
    'filters.all': 'All',
    'filters.any': 'Any',
    'filters.no': 'No',
    'filters.yes': 'Yes',
    'filters.manual': 'Verified',
    'filters.aiDraft': 'AI draft',
    'filters.reset': 'Reset filters',
    'filters.resize': 'Resize filter sidebar',
    'filters.resizeHint': 'Drag to resize the sidebar',
    'results.task': 'Task',
    'results.topic': 'Topic',
    'results.method': 'Method',
    'results.marks': 'Marks',
    'results.verified': 'verified',
    'results.pages': 'pp.',
    'results.emptyTitle': 'No results found',
    'results.emptyBody': 'Change the query or reset the filters.',
    'results.reset': 'Reset',
    'inspector.label': 'Question details',
    'inspector.manualVerified': 'Manually verified',
    'inspector.aiDraft': 'AI draft',
    'inspector.close': 'Close details',
    'inspector.paper': 'Paper',
    'inspector.calculator': 'calculator',
    'inspector.nonCalculator': 'non-calculator',
    'inspector.classification': 'Classification',
    'inspector.primaryTopic': 'Primary topic',
    'inspector.secondary': 'Secondary',
    'inspector.methodFamily': 'Method family',
    'inspector.methodTags': 'Method tags',
    'inspector.sourcePages': 'Source pages',
    'inspector.markschemePages': 'Markscheme pages',
    'inspector.reviewFlags': 'Review flags',
    'inspector.solutionPath': 'Solution path',
    'inspector.alternatives': 'Accepted alternatives',
    'inspector.noAlternative': 'The markscheme does not specify a separate alternative route.',
    'inspector.evidence': 'Classification evidence',
    'inspector.confidence': 'Confidence',
    'inspector.segmentation': 'segmentation',
    'inspector.topic': 'topic',
    'inspector.method': 'method',
    'inspector.noEvidence': 'No evidence provided.',
    'inspector.msPage': 'MS p.',
    'inspector.source': 'Source',
    'inspector.questionPaper': 'Question paper',
    'inspector.markscheme': 'Markscheme',
    'status.select': 'select',
    'status.search': 'search',
    'status.close': 'close',
  },
} as const

type MessageKey = keyof typeof messages.ru

const countForms: Record<Locale, Record<Countable, [string, string, string]>> = {
  ru: {
    blocks: ['блок', 'блока', 'блоков'],
    marks: ['балл', 'балла', 'баллов'],
    sessions: ['сессия', 'сессии', 'сессий'],
    drafts: ['черновик ИИ', 'черновика ИИ', 'черновиков ИИ'],
    verifiedBlocks: ['проверенный блок', 'проверенных блока', 'проверенных блоков'],
  },
  en: {
    blocks: ['block', 'blocks', 'blocks'],
    marks: ['mark', 'marks', 'marks'],
    sessions: ['session', 'sessions', 'sessions'],
    drafts: ['AI draft', 'AI drafts', 'AI drafts'],
    verifiedBlocks: ['verified block', 'verified blocks', 'verified blocks'],
  },
}

interface I18nValue {
  locale: Locale
  setLocale: (locale: Locale) => void
  t: (key: MessageKey) => string
  count: (kind: Countable, value: number) => string
}

const I18nContext = createContext<I18nValue | null>(null)

function initialLocale(): Locale {
  const stored = localStorage.getItem('question-atlas:locale')
  if (stored === 'ru' || stored === 'en') return stored
  return navigator.language.toLowerCase().startsWith('ru') ? 'ru' : 'en'
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocale] = useState<Locale>(initialLocale)

  useEffect(() => {
    localStorage.setItem('question-atlas:locale', locale)
    document.documentElement.lang = locale
    document.title = `IB Math AA HL · ${messages[locale]['brand.atlas']}`
  }, [locale])

  const value = useMemo<I18nValue>(() => ({
    locale,
    setLocale,
    t: (key) => messages[locale][key],
    count: (kind, number) => {
      const [one, few, many] = countForms[locale][kind]
      if (locale === 'en') return `${number} ${number === 1 ? one : many}`
      const mod10 = number % 10
      const mod100 = number % 100
      const form = mod10 === 1 && mod100 !== 11
        ? one
        : mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)
          ? few
          : many
      return `${number} ${form}`
    },
  }), [locale])

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>
}

export function useI18n(): I18nValue {
  const value = useContext(I18nContext)
  if (!value) throw new Error('useI18n must be used within I18nProvider')
  return value
}
