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
}

export interface Filters {
  query: string
  paper: 'all' | '1' | '2' | '3'
  calculator: 'all' | 'yes' | 'no'
  topics: Set<string>
  methods: Set<string>
}

export type FilterSetKey = 'topics' | 'methods'
