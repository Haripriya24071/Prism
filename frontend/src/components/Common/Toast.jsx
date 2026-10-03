import React from 'react';

export function Toast({ message, type = 'info', onClose }) {
  if (!message) return null;

  const bg = type === 'error' ? 'bg-rose-900/90 border-rose-700 text-rose-100' : 'bg-indigo-900/90 border-indigo-700 text-indigo-100';

  return (
    <div className={`fixed bottom-5 right-5 px-4 py-3 border rounded-xl shadow-xl z-50 text-sm flex items-center gap-3 backdrop-blur ${bg}`}>
      <span>{message}</span>
      {onClose && (
        <button onClick={onClose} className="opacity-70 hover:opacity-100 text-xs">✕</button>
      )}
    </div>
  );
}
