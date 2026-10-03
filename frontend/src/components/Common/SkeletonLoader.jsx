export function SkeletonCard({ height = 'var(--space-16)' }) {
  return (
    <div className="skeleton" style={{ width: '100%', height }} aria-hidden="true" />
  )
}
