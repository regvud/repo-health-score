export type { Signal, HealthReport } from './interfaces/responses'

const API_BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export async function analyzeRepo(url: string): Promise<HealthReport> {
  const response = await fetch(`${API_BASE}/api/analyze/?url=${encodeURIComponent(url)}`)
  const data = await response.json()
  if (!response.ok) {
    throw new Error(data.error ?? 'Something went wrong')
  }
  return data as HealthReport
}
