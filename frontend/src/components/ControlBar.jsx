import React from 'react';
import { SlidersHorizontal, ArrowUpDown, DollarSign, Layers } from 'lucide-react';

export default function ControlBar({
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  sortBy,
  setSortBy,
  sortOrder,
  setSortOrder,
  pageSize,
  setPageSize,
  totalCount
}) {
  return (
    <div className="glass-panel p-4 mb-6 flex flex-wrap items-center justify-between gap-4 border border-slate-800">
      
      {/* Price Range Filter */}
      <div className="flex items-center gap-2">
        <DollarSign className="w-4 h-4 text-indigo-400" />
        <span className="text-xs font-semibold text-slate-300">Price Range:</span>
        <input
          type="number"
          placeholder="Min $"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
          className="w-20 px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
        />
        <span className="text-slate-500 text-xs">-</span>
        <input
          type="number"
          placeholder="Max $"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          className="w-20 px-2.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
        />
      </div>

      {/* Sort By Selector */}
      <div className="flex items-center gap-2">
        <ArrowUpDown className="w-4 h-4 text-cyan-400" />
        <span className="text-xs font-semibold text-slate-300">Sort By:</span>
        <select
          value={`${sortBy}:${sortOrder}`}
          onChange={(e) => {
            const [field, order] = e.target.value.split(':');
            setSortBy(field);
            setSortOrder(order);
          }}
          className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
        >
          <option value="name:asc">Name (A → Z)</option>
          <option value="name:desc">Name (Z → A)</option>
          <option value="price:asc">Price (Low → High)</option>
          <option value="price:desc">Price (High → Low)</option>
          <option value="created_at:desc">Newest Arrivals</option>
          <option value="stock:desc">Stock Level</option>
        </select>
      </div>

      {/* Page Size Selector */}
      <div className="flex items-center gap-2">
        <Layers className="w-4 h-4 text-emerald-400" />
        <span className="text-xs font-semibold text-slate-300">Per Page:</span>
        <select
          value={pageSize}
          onChange={(e) => setPageSize(Number(e.target.value))}
          className="bg-slate-900 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500 font-semibold"
        >
          <option value={12}>12 items</option>
          <option value={24}>24 items</option>
          <option value={48}>48 items</option>
          <option value={96}>96 items</option>
        </select>
      </div>

      {/* Total Matching Items */}
      {totalCount !== null && (
        <div className="text-xs font-medium text-slate-400">
          Showing <span className="text-indigo-400 font-bold">{totalCount.toLocaleString()}</span> products
        </div>
      )}

    </div>
  );
}
