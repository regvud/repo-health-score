import type { Signal } from '../interfaces/responses'

export const STATUS_COLOR: Record<Signal['status'], string> = {
  good: 'var(--green)',
  warning: 'var(--amber)',
  bad: 'var(--red)',
  neutral: 'var(--muted)',
}

export function scoreColor(score: number): string {
  if (score >= 70) return 'var(--green)'
  if (score >= 40) return 'var(--amber)'
  return 'var(--red)'
}
