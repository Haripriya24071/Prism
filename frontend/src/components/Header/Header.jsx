import React from 'react';

export function Header({ currentStage = 'intake', sessionId }) {
  const stages = [
    { id: 'intake', label: '1. Prompt Intake' },
    { id: 'generation', label: '2. Multi-Agent Synthesis' },
    { id: 'results', label: '3. BRD & Metrics' },
  ];

  return (
    <header className="w-full h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur px-6 flex items-center justify-between sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <span className="font-extrabold text-lg text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400">
          PRISM
        </span>
        <span className="text-xs text-slate-500 font-mono px-2 py-0.5 rounded bg-slate-900 border border-slate-800">
          v1.0.0
        </span>
      </div>

      <nav className="flex items-center gap-2">
        {stages.map((st, idx) => {
          const isActive = currentStage === st.id;
          return (
            <React.Fragment key={st.id}>
              {idx > 0 && <span className="text-slate-700">/</span>}
              <span
                className={`text-xs font-medium px-3 py-1 rounded-full transition-all ${
                  isActive
                    ? 'bg-indigo-600/30 border border-indigo-500/50 text-indigo-300'
                    : 'text-slate-500 hover:text-slate-400'
                }`}
              >
                {st.label}
              </span>
            </React.Fragment>
          );
        })}
      </nav>

      <div className="text-xs font-mono text-slate-400 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        {sessionId ? `Session: ${sessionId.slice(0, 8)}...` : 'Ready'}
      </div>
    </header>
  );
}
