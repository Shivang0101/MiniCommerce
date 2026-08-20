import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

export default function Pagination({ page, pageSize, totalCount, onPageChange }) {
  if (!totalCount || totalCount <= 0) return null;

  const totalPages = Math.ceil(totalCount / pageSize);
  if (totalPages <= 1) return null;

  const startItem = (page - 1) * pageSize + 1;
  const endItem = Math.min(page * pageSize, totalCount);

  return (
    <div className="glass-panel p-4 mt-8 flex flex-wrap items-center justify-between gap-4 border border-slate-800">
      
      {/* Item Range Text */}
      <div className="text-xs text-slate-400">
        Showing <span className="font-semibold text-slate-200">{startItem.toLocaleString()}</span> to{' '}
        <span className="font-semibold text-slate-200">{endItem.toLocaleString()}</span> of{' '}
        <span className="font-semibold text-indigo-400">{totalCount.toLocaleString()}</span> items
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="btn btn-secondary py-1.5 px-3 text-xs disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous</span>
        </button>

        <div className="px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs font-semibold text-slate-300">
          Page <span className="text-cyan-400">{page}</span> of {totalPages.toLocaleString()}
        </div>

        <button
          onClick={() => onPageChange(page + 1)}
          disabled={page >= totalPages}
          className="btn btn-secondary py-1.5 px-3 text-xs disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <span>Next</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

    </div>
  );
}
