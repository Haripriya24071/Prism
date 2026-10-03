import React from 'react';

export function VoiceButton({ isListening, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-label={isListening ? 'Stop voice recording' : 'Start voice recording'}
      aria-pressed={isListening}
      className={`p-2.5 rounded-xl transition-all focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
        isListening
          ? 'bg-rose-600/30 text-rose-400 border border-rose-500/50 animate-pulse'
          : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/60'
      }`}
    >
      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 016 0v6a3 3 0 01-3 3z" />
      </svg>
    </button>
  );
}
