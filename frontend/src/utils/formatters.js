export function formatScore(score) {
  if (typeof score !== 'number') return 'N/A'
  return `${(score * 100).toFixed(0)}%`
}

export function getScoreBand(score) {
  if (score >= 0.8) return 'high'
  if (score >= 0.6) return 'medium'
  return 'low'
}

export function getScoreColor(score) {
  if (score >= 0.8) return 'emerald'
  if (score >= 0.6) return 'amber'
  return 'rose'
}

export function formatDate(isoString) {
  if (!isoString) return ''
  return new Date(isoString).toLocaleString()
}
