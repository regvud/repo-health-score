import type { HealthReport, Signal } from '../api'

const STATUS_COLOR: Record<Signal['status'], string> = {
  good: 'var(--green)',
  warning: 'var(--amber)',
  bad: 'var(--red)',
  neutral: 'var(--muted)',
}

function scoreColor(score: number): string {
  if (score >= 70) return 'var(--green)'
  if (score >= 40) return 'var(--amber)'
  return 'var(--red)'
}

interface Props {
  report: HealthReport
}

export default function HealthReport({ report }: Props) {
  return (
    <div className="report">
      <div className="report-header">
        <div className="report-info">
          <h2 className="repo-name">{report.repo}</h2>
          {report.meta.description && (
            <p className="repo-desc">{report.meta.description}</p>
          )}
          <div className="repo-meta">
            <span>★ {report.meta.stars.toLocaleString()}</span>
            <span>⑂ {report.meta.forks.toLocaleString()}</span>
            <span>{report.meta.open_issues.toLocaleString()} open issues</span>
            {report.meta.cached && <span className="badge">cached</span>}
          </div>
        </div>

        <div className="score-block">
          <span className="score-number" style={{ color: scoreColor(report.score) }}>
            {report.score}
          </span>
          <span className="score-denom">/ 100</span>
        </div>
      </div>

      <div className="signals">
        {report.signals.map(signal => (
          <div key={signal.name} className="signal">
            <div className="signal-row">
              <span className="signal-label">{signal.label}</span>
              <div className="signal-right">
                <span className="badge">{signal.weight}%</span>
                <span
                  className="signal-score"
                  style={{ color: signal.score != null ? STATUS_COLOR[signal.status] : 'var(--muted)' }}
                >
                  {signal.score ?? '—'}
                </span>
              </div>
            </div>
            <p className="signal-value">{signal.value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
