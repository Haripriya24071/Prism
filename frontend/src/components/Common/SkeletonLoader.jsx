import React from 'react';

export function SkeletonCard({ height = 'h-32' }) {
  return (
    <div className={`w-full ${height} bg-slate-900/60 border border-slate-800/80 rounded-xl animate-pulse p-4 flex flex-col justify-between`}>
      <div className="h-4 bg-slate-800 rounded w-1/3" />
      <div className="space-y-2">
        <div className="h-3 bg-slate-800/80 rounded w-5/6" />
        <div className="h-3 bg-slate-800/80 rounded w-4/6" />
      </div>
    </div>
  );
}
