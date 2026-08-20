import React from 'react';
import ProductCard from './ProductCard';
import { SearchX, Sparkles } from 'lucide-react';

export default function ProductGrid({ products, loading, onAddToCart, addingId }) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="glass-panel p-5 h-56 flex flex-col justify-between">
            <div>
              <div className="skeleton h-4 w-20 mb-3"></div>
              <div className="skeleton h-5 w-3/4 mb-2"></div>
              <div className="skeleton h-3 w-full mb-1"></div>
              <div className="skeleton h-3 w-2/3"></div>
            </div>
            <div className="flex justify-between items-center pt-3 border-t border-slate-800">
              <div className="skeleton h-6 w-16"></div>
              <div className="skeleton h-8 w-24 rounded-xl"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!products || products.length === 0) {
    return (
      <div className="glass-panel p-12 text-center my-8 max-w-xl mx-auto border border-slate-800">
        <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-800">
          <SearchX className="w-8 h-8 text-slate-500" />
        </div>
        <h3 className="font-heading font-bold text-lg text-slate-200 mb-2">No Matching Products Found</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto mb-4">
          We couldn't find any products matching your search or filter criteria in the 50,000 dataset.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 animate-fade">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onAddToCart={onAddToCart}
          isAdding={addingId === product.id}
        />
      ))}
    </div>
  );
}
