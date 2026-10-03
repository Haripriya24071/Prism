import React, { useState } from 'react';

export function AgentGrid({ agents = [] }) {
  const [filter, setFilter] = useState('ALL');

  const categories = ['ALL', 'ANALYST', 'STRATEGIST', 'ADVERSARIAL'];

  const filteredAgents = filter === 'ALL'
    ? agents
    : agents.filter(a => a.persona?.toUpperCase().includes(filter));

  return (
    <div className="space-y-4">
      <div className="flex gap-2 border-b border-slate-800 pb-2">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`text-xs px-3 py-1 rounded-lg transition-colors ${
              filter === cat
                ? 'bg-indigo-600 text-white font-medium'
                : 'text-slate-400 hover:bg-slate-800'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredAgents.length > 0 ? (
          filteredAgents.map(agent => (
            <div key={agent.id} className="p-4 bg-slate-900/60 border border-slate-800 rounded-xl">
              <h4 className="font-semibold text-sm text-slate-200">{agent.title}</h4>
              <p className="text-xs text-slate-400 mt-1">{agent.status || 'Active'}</p>
            </div>
          ))
        ) : (
          <div className="col-span-full py-8 text-center text-xs text-slate-500">
            No agents found for filter: {filter}
          </div>
        )}
      </div>
    </div>
  );
}
