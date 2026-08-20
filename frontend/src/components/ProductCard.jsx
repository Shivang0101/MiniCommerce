import React from 'react';
import { ShoppingCart, Check, Package, Sparkles } from 'lucide-react';

export default function ProductCard({ product, onAddToCart, isAdding }) {
  const isOutOfStock = product.stock <= 0;
  const isLowStock = product.stock > 0 && product.stock <= 15;

  return (
    <div className="glass-panel glass-panel-interactive p-5 flex flex-col justify-between relative overflow-hidden group">
      
      {/* Background Accent Glow */}
      <div className="absolute -top-12 -right-12 w-24 h-24 bg-indigo-500/10 rounded-full blur-xl group-hover:bg-cyan-500/20 transition-all"></div>

      <div>
        {/* Top Header: Badge Tag */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            Hardware Lab
          </span>

          {isOutOfStock ? (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/20">
              Out of Stock
            </span>
          ) : isLowStock ? (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Only {product.stock} left
            </span>
          ) : (
            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {product.stock} in stock
            </span>
          )}
        </div>

        {/* Product Title */}
        <h3 className="font-heading font-bold text-base text-slate-100 mb-1.5 group-hover:text-cyan-300 transition-colors line-clamp-1">
          {product.name}
        </h3>

        {/* Description */}
        <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
          {product.description || "High-performance laboratory hardware component."}
        </p>
      </div>

      {/* Footer: Price & Add Button */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-3 mt-2">
        <div>
          <span className="text-xs text-slate-500 block">Price</span>
          <span className="font-heading font-extrabold text-lg text-white">
            ${parseFloat(product.price).toFixed(2)}
          </span>
        </div>

        <button
          onClick={() => onAddToCart(product.id)}
          disabled={isOutOfStock || isAdding}
          className={`btn text-xs py-2 px-3.5 ${
            isAdding
              ? 'btn-accent'
              : isOutOfStock
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : 'btn-primary'
          }`}
        >
          {isAdding ? (
            <>
              <Check className="w-3.5 h-3.5" />
              <span>Added</span>
            </>
          ) : isOutOfStock ? (
            <span>Sold Out</span>
          ) : (
            <>
              <ShoppingCart className="w-3.5 h-3.5" />
              <span>Add to Cart</span>
            </>
          )}
        </button>
      </div>

    </div>
  );
}
