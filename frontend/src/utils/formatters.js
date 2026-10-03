export function formatScore(score) {
  if (typeof score !== 'number') return 'N/A';
  return (score * 100).toFixed(0) + '%';
}

export function getScoreColor(score) {
  if (score >= 0.8) return 'text-emerald-400 border-emerald-500/50 bg-emerald-500/10';
  if (score >= 0.6) return 'text-amber-400 border-amber-500/50 bg-amber-500/10';
  return 'text-rose-400 border-rose-500/50 bg-rose-500/10';
}

export function formatDate(isoString) {
  if (!isoString) return '';
  return new Date(isoString).toLocaleString();
}
