import React from 'react';
import { LayoutGrid, Laptop, Smartphone, Monitor, Keyboard, HardDrive, Headphones, Wifi, Cpu } from 'lucide-react';

const CATEGORIES = [
  { id: 'All', label: 'All Products', icon: LayoutGrid },
  { id: 'Laptops', label: 'Laptops', icon: Laptop },
  { id: 'Smartphones', label: 'Smartphones', icon: Smartphone },
  { id: 'Monitors', label: 'Monitors', icon: Monitor },
  { id: 'Keyboards', label: 'Keyboards', icon: Keyboard },
  { id: 'Storage', label: 'Storage', icon: HardDrive },
  { id: 'Audio', label: 'Audio', icon: Headphones },
  { id: 'Networking', label: 'Networking', icon: Wifi },
  { id: 'Components', label: 'Components', icon: Cpu },
];

export default function CategoryBar({ selectedCategory, onSelectCategory }) {
  return (
    <div className="w-full overflow-x-auto py-4 scrollbar-none border-b border-slate-800/60 bg-slate-950/40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-2 min-w-max">
        {CATEGORIES.map((cat) => {
          const Icon = cat.icon;
          const isSelected = selectedCategory.toLowerCase() === cat.id.toLowerCase();
          return (
            <button
              key={cat.id}
              onClick={() => onSelectCategory(cat.id)}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
                isSelected
                  ? 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-lg shadow-indigo-500/25 scale-105'
                  : 'bg-slate-900/80 text-slate-400 hover:text-slate-200 hover:bg-slate-800/80 border border-slate-800'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isSelected ? 'text-white' : 'text-slate-400'}`} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
