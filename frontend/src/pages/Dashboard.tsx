import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import MetricCard from '../components/MetricCard'
import SeverityBadge from '../components/SeverityBadge'
import { api } from '../services/api'
import type { CompetitorAggregate, IntentBreakdown, Opportunity, OverviewMetrics } from '../types'

export default function Dashboard() {
  const [overview, setOverview] = useState<OverviewMetrics | null>(null)
  const [intents, setIntents] = useState<IntentBreakdown[]>([])
  const [competitors, setCompetitors] = useState<CompetitorAggregate[]>([])
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [runs, setRuns] = useState<{ id: number; query_id: number }[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [mockMode, setMockMode] = useState(true)

  const loadData = async () => {
    setError('')
    try {
      const [ov, int, comp, opp, runList, health] = await Promise.all([
        api.getOverview(),
        api.getIntents(),
        api.getCompetitors(),
        api.getOpportunities(),
        api.getRuns(),
        api.health(),
      ])
      setOverview(ov)
      setIntents(int)
      setCompetitors(comp)
      setOpportunities(opp)
      setRuns(runList)
      setMockMode(health.mock_mode)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load data')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const runDemo = async () => {
    setLoading(true)
    setError('')
    try {
      await api.runDemo()
      await loadData()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Demo failed')
    } finally {
      setLoading(false)
    }
  }

  const exportReport = async () => {
    try {
      const result = await api.generateReport()
      window.open('/api/reports/sample/html', '_blank')
      alert(`Report generated!\nJSON: ${result.files.json}`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Report failed')
    }
  }

  const empty = !overview || overview.total_runs === 0

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-xl font-bold text-brand-700">AI Search Visibility Analyzer</h1>
            <p className="text-sm text-slate-500">Boutiqaat · Observable AI-search visibility</p>
          </div>
          <div className="flex items-center gap-3">
            {mockMode && (
              <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-600">
                Offline Mode
              </span>
            )}
            <button
              onClick={runDemo}
              disabled={loading}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {loading ? 'Running…' : 'Run Full Analysis'}
            </button>
            <button
              onClick={exportReport}
              disabled={empty}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium hover:bg-slate-50 disabled:opacity-50"
            >
              Export Report
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8">
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">{error}</div>
        )}

        {empty ? (
          <div className="rounded-xl border border-dashed border-slate-300 bg-white p-16 text-center">
            <h2 className="text-lg font-semibold">No analysis data yet</h2>
            <p className="mt-2 text-slate-500">Click &quot;Run Full Analysis&quot; to load customer queries and analyze Boutiqaat visibility.</p>
          </div>
        ) : (
          overview && (
            <>
              <section className="grid grid-cols-2 gap-4 md:grid-cols-4 lg:grid-cols-4">
                <MetricCard label="Total Queries" value={overview.total_queries} />
                <MetricCard label="Mention Rate" value={`${overview.mention_rate}%`} sub="Boutiqaat mentioned" />
                <MetricCard label="Recommendation Rate" value={`${overview.recommendation_rate}%`} sub="Actively recommended" />
                <MetricCard label="Visibility Score" value={overview.visibility_score} sub="Composite diagnostic metric" />
                <MetricCard label="Avg Position" value={overview.average_position ?? 'N/A'} sub="When recommended" />
                <MetricCard label="Top-3 Rate" value={`${overview.top3_rate}%`} />
                <MetricCard label="Source Coverage" value={`${overview.source_coverage}%`} sub="Rec. with Boutiqaat sources" />
                <MetricCard label="AI Runs" value={overview.total_runs} />
              </section>

              <div className="mt-8 grid gap-6 lg:grid-cols-2">
                <section className="rounded-xl bg-white p-6 shadow-sm border border-slate-100">
                  <h2 className="mb-4 text-lg font-semibold">Visibility by Intent</h2>
                  {intents.length > 0 ? (
                    <ResponsiveContainer width="100%" height={280}>
                      <BarChart data={intents}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="intent" tick={{ fontSize: 11 }} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="mention_rate" fill="#a78bfa" name="Mention %" />
                        <Bar dataKey="recommendation_rate" fill="#6c3fc5" name="Rec %" />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="text-slate-400">No intent data</p>
                  )}
                </section>

                <section className="rounded-xl bg-white p-6 shadow-sm border border-slate-100">
                  <h2 className="mb-4 text-lg font-semibold">Competitor Comparison</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b text-left text-slate-500">
                          <th className="pb-2">Company</th>
                          <th className="pb-2">Mention %</th>
                          <th className="pb-2">Rec %</th>
                          <th className="pb-2">Avg Pos</th>
                          <th className="pb-2">Top-3 %</th>
                        </tr>
                      </thead>
                      <tbody>
                        {competitors.slice(0, 8).map((c) => (
                          <tr key={c.name} className="border-b border-slate-50">
                            <td className="py-2 font-medium">{c.name}</td>
                            <td>{c.mention_rate}%</td>
                            <td>{c.recommendation_rate}%</td>
                            <td>{c.average_position ?? '—'}</td>
                            <td>{c.top3_rate}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </section>
              </div>

              <section className="mt-8 rounded-xl bg-white p-6 shadow-sm border border-slate-100">
                <h2 className="mb-4 text-lg font-semibold">Opportunities</h2>
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {opportunities.slice(0, 9).map((o) => (
                    <div key={o.id} className="rounded-lg border border-slate-100 p-4">
                      <div className="flex items-start justify-between gap-2">
                        <h3 className="font-medium text-sm">{o.title}</h3>
                        <SeverityBadge severity={o.severity} />
                      </div>
                      <p className="mt-2 text-xs text-slate-500 line-clamp-2">{o.explanation}</p>
                      <p className="mt-2 text-xs text-brand-600">{o.recommendation}</p>
                      <Link to={`/runs/${o.run_id}`} className="mt-2 inline-block text-xs text-brand-500 hover:underline">
                        View query →
                      </Link>
                    </div>
                  ))}
                </div>
              </section>

              <section className="mt-8 rounded-xl bg-white p-6 shadow-sm border border-slate-100">
                <h2 className="mb-4 text-lg font-semibold">Recent Query Runs</h2>
                <div className="space-y-2">
                  {runs.slice(0, 10).map((r) => (
                    <Link
                      key={r.id}
                      to={`/runs/${r.id}`}
                      className="flex items-center justify-between rounded-lg border border-slate-100 px-4 py-3 hover:bg-brand-50"
                    >
                      <span className="text-sm">Run #{r.id}</span>
                      <span className="text-xs text-brand-600">View details →</span>
                    </Link>
                  ))}
                </div>
              </section>
            </>
          )
        )}
      </main>
    </div>
  )
}
