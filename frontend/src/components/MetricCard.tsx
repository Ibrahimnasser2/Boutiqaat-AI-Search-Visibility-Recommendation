interface Props {
  label: string
  value: string | number
  sub?: string
}

export default function MetricCard({ label, value, sub }: Props) {
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-1 text-3xl font-semibold text-brand-600">{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-400">{sub}</p>}
    </div>
  )
}
