const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

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

export async function analyzeRepo(url: string): Promise<HealthReport> {
  const response = await fetch(`${API_BASE}/api/analyze/?url=${encodeURIComponent(url)}`)
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error ?? 'Something went wrong')
  }
  return data as HealthReport
}
