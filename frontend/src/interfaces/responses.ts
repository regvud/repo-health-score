export interface Signal {
  name: string
  label: string
  weight: number
  score: number | null
  value: string
  status: 'good' | 'warning' | 'bad' | 'neutral'
}

export interface HealthReport {
  repo: string
  score: number
  signals: Signal[]
  meta: {
    stars: number
    forks: number
    open_issues: number
    description: string | null
    cached: boolean
  }
}
