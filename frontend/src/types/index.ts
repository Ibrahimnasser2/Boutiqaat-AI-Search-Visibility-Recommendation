export interface Query {
  id: number
  text: string
  intent: string
  category: string
  geography: string
  created_at: string
}

export interface OverviewMetrics {
  total_queries: number
  total_runs: number
  mention_rate: number
  recommendation_rate: number
  average_position: number | null
  top3_rate: number
  visibility_score: number
  source_coverage: number
}

export interface IntentBreakdown {
  intent: string
  query_count: number
  mention_rate: number
  recommendation_rate: number
  visibility_score: number
}

export interface CompetitorAggregate {
  name: string
  mention_count: number
  recommendation_count: number
  mention_rate: number
  recommendation_rate: number
  average_position: number | null
  top3_rate: number
}

export interface Opportunity {
  id: number
  run_id: number
  category: string
  severity: string
  title: string
  explanation: string
  recommendation: string
  evidence: string
}

export interface AnalysisDetail {
  run_id: number
  query_id: number
  query_text: string
  provider: string
  model: string
  raw_answer: string
  structured_answer: Record<string, unknown>
  visibility: {
    boutiqaat_mentioned: boolean
    boutiqaat_recommended: boolean
    boutiqaat_position: number | null
    visibility_score: number
    confidence: number
    explanation: string
  }
  competitors: Array<{ name: string; position: number | null; recommended: boolean; evidence: string }>
  sources: Array<{ url: string; domain: string; title: string; source_type: string; supports_boutiqaat: boolean }>
  opportunities: Opportunity[]
}

export interface AIRun {
  id: number
  query_id: number
  provider: string
  model: string
  timestamp: string
  status: string
}
