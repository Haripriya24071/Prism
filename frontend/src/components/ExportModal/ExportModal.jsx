import { useEffect, useRef } from 'react'
import './ExportModal.css'

const FORMATS = [
  { id: 'markdown', label: 'Markdown (.md)', note: 'Recommended' },
  { id: 'json', label: 'JSON (.json)', note: 'Raw data' },
]

export function ExportModal({ isOpen, onClose, onExport }) {
  const dialogRef = useRef(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) {
      return undefined
    }
    if (isOpen && !dialog.open) {
      dialog.showModal()
    }
    if (!isOpen && dialog.open) {
      dialog.close()
    }
    return undefined
  }, [isOpen])

  return (
    <dialog ref={dialogRef} className="export-modal" onClose={onClose} aria-labelledby="export-modal-title">
      <h3 id="export-modal-title" className="export-modal__title">Export BRD</h3>
      <p className="export-modal__text">Choose a format for the generated document.</p>

      <div className="export-modal__options">
        {FORMATS.map((format) => (
          <button
            key={format.id}
            type="button"
            className="export-modal__option"
            onClick={() => onExport(format.id)}
          >
            <span>{format.label}</span>
            <span className="export-modal__note">{format.note}</span>
          </button>
        ))}
      </div>

      <button type="button" className="export-modal__cancel" onClick={onClose}>
        Cancel
      </button>
    </dialog>
  )
}
