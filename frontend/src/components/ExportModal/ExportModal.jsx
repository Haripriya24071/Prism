import React from 'react';

export function ExportModal({ isOpen, onClose, onExport }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
        <h3 className="text-lg font-bold text-slate-100 mb-2">Export BRD Document</h3>
        <p className="text-xs text-slate-400 mb-6">Choose your preferred format to export the generated artifact.</p>

        <div className="space-y-3 mb-6">
          <button
            onClick={() => onExport('markdown')}
            className="w-full text-left p-3 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 text-slate-200 font-medium text-sm flex justify-between items-center transition-colors"
          >
            <span>Markdown (.md)</span>
            <span className="text-xs text-slate-500">Recommended</span>
          </button>
          <button
            onClick={() => onExport('json')}
            className="w-full text-left p-3 rounded-xl border border-slate-800 bg-slate-800/40 hover:bg-slate-800 text-slate-200 font-medium text-sm flex justify-between items-center transition-colors"
          >
            <span>JSON Schema (.json)</span>
            <span className="text-xs text-slate-500">Raw Data</span>
          </button>
        </div>

        <div className="flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-slate-400 hover:text-slate-200 text-sm transition-colors"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
