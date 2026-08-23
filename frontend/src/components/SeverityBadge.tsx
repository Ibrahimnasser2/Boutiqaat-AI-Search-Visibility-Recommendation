const colors: Record<string, string> = {
  high: 'bg-red-100 text-red-700',
  medium: 'bg-amber-100 text-amber-700',
  low: 'bg-green-100 text-green-700',
}

interface Props {
  severity: string
}

export default function SeverityBadge({ severity }: Props) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${colors[severity] || 'bg-slate-100 text-slate-600'}`}>
      {severity}
    </span>
  )
}
