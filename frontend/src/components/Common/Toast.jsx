import './Toast.css'

export function Toast({ message, type = 'info', onClose }) {
  if (!message) {
    return null
  }

  return (
    <div className="toast" data-type={type} role={type === 'error' ? 'alert' : 'status'}>
      <span>{message}</span>
      {onClose && (
        <button type="button" className="toast__close" aria-label="Dismiss" onClick={onClose}>
          ✕
        </button>
      )}
    </div>
  )
}
