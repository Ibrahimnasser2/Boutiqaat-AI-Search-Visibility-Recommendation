const BASE = import.meta.env.VITE_API_URL || ''

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err || res.statusText)
  }
  return res.json()
}

export const api = {
  health: () => fetchJson<{ status: string; mock_mode: boolean }>('/api/health'),
  loadSample: () => fetchJson<{ loaded: number }>('/api/queries/load-sample', { method: 'POST' }),
  runDemo: () => fetchJson<{ runs_completed: number; queries_loaded: number }>('/api/demo/run-full', { method: 'POST' }),
  getOverview: () => fetchJson<import('./types').OverviewMetrics>('/api/analysis/overview'),
  getIntents: () => fetchJson<import('./types').IntentBreakdown[]>('/api/analysis/intents'),
  getCompetitors: () => fetchJson<import('./types').CompetitorAggregate[]>('/api/analysis/competitors'),
  getOpportunities: (severity?: string) =>
    fetchJson<import('./types').Opportunity[]>(
      `/api/analysis/opportunities${severity ? `?severity=${severity}` : ''}`,
    ),
  getRunDetail: (runId: number) => fetchJson<import('./types').AnalysisDetail>(`/api/analysis/runs/${runId}`),
  getRuns: () => fetchJson<import('./types').AIRun[]>('/api/runs'),
  getQueries: () => fetchJson<import('./types').Query[]>('/api/queries'),
  generateReport: () => fetchJson<{ files: Record<string, string>; summary: Record<string, unknown> }>('/api/reports/sample'),
}
