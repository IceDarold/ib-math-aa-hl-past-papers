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
}

export interface Question extends Omit<RawQuestion, 'paper' | 'marks'> {
  paper: number
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
  paper: 'all' | '1' | '2' | '3'
  calculator: 'all' | 'yes' | 'no'
  session: 'all' | 'May 2024' | 'November 2024'
  status: 'all' | 'manual_verified' | 'ai_draft'
  topics: Set<string>
  methods: Set<string>
}

export type FilterSetKey = 'topics' | 'methods'
