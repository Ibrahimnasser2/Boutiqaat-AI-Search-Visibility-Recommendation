import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import SeverityBadge from '../components/SeverityBadge'
import { api } from '../services/api'
import type { AnalysisDetail } from '../types'

export default function QueryDetail() {
  const { runId } = useParams()
  const [detail, setDetail] = useState<AnalysisDetail | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!runId) return
    api.getRunDetail(Number(runId))
      .then(setDetail)
      .catch((e) => setError(e.message))
  }, [runId])

  if (error) return <div className="p-8 text-red-600">{error}</div>
  if (!detail) return <div className="p-8 text-slate-400">Loading…</div>

  const v = detail.visibility

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b bg-white px-4 py-4">
        <Link to="/" className="text-sm text-brand-600 hover:underline">← Back to Dashboard</Link>
        <h1 className="mt-2 text-lg font-bold">{detail.query_text}</h1>
        <p className="text-sm text-slate-500">{detail.provider} · {detail.model}</p>
      </header>

      <main className="mx-auto max-w-5xl space-y-6 p-6">
        <section className="grid gap-4 md:grid-cols-4">
          <Stat label="Mentioned" value={v.boutiqaat_mentioned ? 'Yes' : 'No'} highlight={v.boutiqaat_mentioned} />
          <Stat label="Recommended" value={v.boutiqaat_recommended ? 'Yes' : 'No'} highlight={v.boutiqaat_recommended} />
          <Stat label="Position" value={v.boutiqaat_position ?? 'N/A'} />
          <Stat label="Visibility Score" value={v.visibility_score} />
        </section>

        <section className="rounded-xl bg-white p-6 shadow-sm border">
          <h2 className="font-semibold">AI Answer</h2>
          <pre className="mt-3 whitespace-pre-wrap rounded-lg bg-slate-50 p-4 text-sm text-slate-700">{detail.raw_answer}</pre>
          <p className="mt-2 text-xs text-slate-400">{v.explanation}</p>
        </section>

        <div className="grid gap-6 md:grid-cols-2">
          <section className="rounded-xl bg-white p-6 shadow-sm border">
            <h2 className="font-semibold">Competitors</h2>
            <ul className="mt-3 space-y-2">
              {detail.competitors.map((c, i) => (
                <li key={i} className="flex justify-between border-b border-slate-50 py-2 text-sm">
                  <span>{c.position}. {c.name}</span>
                  <span className="text-slate-400">{c.evidence.slice(0, 60)}…</span>
                </li>
              ))}
              {detail.competitors.length === 0 && <p className="text-slate-400 text-sm">None extracted</p>}
            </ul>
          </section>

          <section className="rounded-xl bg-white p-6 shadow-sm border">
            <h2 className="font-semibold">Sources</h2>
            <ul className="mt-3 space-y-2">
              {detail.sources.map((s, i) => (
                <li key={i} className="text-sm">
                  <a href={s.url} target="_blank" rel="noreferrer" className="text-brand-600 hover:underline">
                    {s.title || s.domain}
                  </a>
                  <span className="ml-2 text-xs text-slate-400">{s.source_type}</span>
                  {s.supports_boutiqaat && (
                    <span className="ml-2 rounded bg-brand-50 px-1.5 text-xs text-brand-600">Boutiqaat</span>
                  )}
                </li>
              ))}
              {detail.sources.length === 0 && <p className="text-slate-400 text-sm">No sources cited</p>}
            </ul>
          </section>
        </div>

        <section className="rounded-xl bg-white p-6 shadow-sm border">
          <h2 className="font-semibold">Potential Opportunities</h2>
          <div className="mt-4 space-y-4">
            {detail.opportunities.map((o) => (
              <div key={o.id} className="rounded-lg border border-slate-100 p-4">
                <div className="flex items-center gap-2">
                  <h3 className="font-medium">{o.title}</h3>
                  <SeverityBadge severity={o.severity} />
                </div>
                <p className="mt-2 text-sm text-slate-600">{o.explanation}</p>
                <p className="mt-1 text-sm text-brand-600"><strong>Action:</strong> {o.recommendation}</p>
                <p className="mt-1 text-xs text-slate-400">Evidence: {o.evidence}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  )
}

function Stat({ label, value, highlight }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`rounded-xl p-4 ${highlight ? 'bg-brand-50 border border-brand-100' : 'bg-white border border-slate-100'}`}>
      <p className="text-xs text-slate-500">{label}</p>
      <p className="text-xl font-semibold">{value}</p>
    </div>
  )
}
