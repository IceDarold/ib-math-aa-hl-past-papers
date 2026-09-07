export interface RawQuestion {
  id: string
  paper: string
  question: string
  part: string
  marks: string
  calculator: 'yes' | 'no'
  source_pages: string
  task_summary: string
  primary_topic: string
  secondary_topics: string
  method_tags: string
  method_path: string
  accepted_alternatives: string
  session: string
  zone: string
  review_status: 'manual_verified' | 'ai_draft'
  method_family: string
  markscheme_pages: string
  evidence: string
  confidence: string
  review_flags: string
  source_root: string
  // Своё у физики: у неё подлинник разобран, а не лежит ссылкой на PDF.
  // Столбцы приходят от службы, какие у предмета есть.
  level?: string
  form?: string
  command_term?: string
  marking_points?: string
  scheme_flags?: string
  question_text?: string
  markscheme?: string
}

export interface Question extends Omit<RawQuestion, 'marks'> {
  // Бумага остаётся строкой: у физики это 1A, 1B и 2, и Number() делал
  // из них NaN.
  marks: number
  tags: string[]
  secondaryTopics: string[]
  alternatives: string[]
  pathSteps: string[]
  topicFamily: string
  methodFamily: string
  evidenceItems: Array<{ markscheme_pages: string; basis: string }>
  confidenceLevels: { segmentation: string; topic: string; method: string }
  reviewFlags: string[]
}

export interface Filters {
  query: string
  // Бумаги и статусы у предметов разные, поэтому это просто строки, а
  // список берётся от службы.
  paper: string
  calculator: string
  session: string
  zone: string
  status: string
  topics: Set<string>
  methods: Set<string>
  // Форма ответа — ось, которой у математики нет вовсе.
  forms: Set<string>
}

export type FilterSetKey = 'topics' | 'methods' | 'forms'
