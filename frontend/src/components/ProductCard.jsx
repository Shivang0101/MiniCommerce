import React from 'react';
import { ShoppingCart, Check, Star, Truck, ShieldCheck, Cpu, Monitor, Keyboard, Headphones, HardDrive, Smartphone } from 'lucide-react';

export default function ProductCard({ product, onAddToCart, isAdding }) {
  const isOutOfStock = product.stock <= 0;
  const isLowStock = product.stock > 0 && product.stock <= 15;

  // Calculate realistic discount & MSRP strikethrough price for e-commerce feel
  const currentPrice = parseFloat(product.price);
  const msrpPrice = (currentPrice * 1.22).toFixed(2);
  const discountPercent = 18;

  // Generate consistent pseudo-random star rating based on product name hash
  const nameHash = product.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const rating = (4.4 + (nameHash % 6) * 0.1).toFixed(1);
  const reviewCount = 85 + (nameHash % 320);

  // Pick category icon visual helper
  const getCategoryIcon = (name) => {
    const n = name.toLowerCase();
    if (n.includes('keyboard')) return <Keyboard className="w-8 h-8 text-blue-400" />;
    if (n.includes('monitor') || n.includes('screen')) return <Monitor className="w-8 h-8 text-cyan-400" />;
    if (n.includes('headphone') || n.includes('mic') || n.includes('audio')) return <Headphones className="w-8 h-8 text-indigo-400" />;
    if (n.includes('storage') || n.includes('hub') || n.includes('usb')) return <HardDrive className="w-8 h-8 text-emerald-400" />;
    if (n.includes('phone') || n.includes('mobile')) return <Smartphone className="w-8 h-8 text-amber-400" />;
    return <Cpu className="w-8 h-8 text-purple-400" />;
  };

  return (
    <div className="glass-panel glass-panel-interactive p-5 flex flex-col justify-between relative overflow-hidden group bg-slate-900/90 border-slate-800/90 rounded-2xl hover:border-blue-500/40">
      
      {/* Top Banner Tag: Discount & Stock */}
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className="text-[10px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
          {discountPercent}% OFF
        </span>

        {isOutOfStock ? (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
            Sold Out
          </span>
        ) : isLowStock ? (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40">
            Only {product.stock} left!
          </span>
        ) : (
          <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            In Stock
          </span>
        )}
      </div>

      {/* Product Image Visual Box */}
      <div className="w-full h-36 rounded-xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-center relative my-2 group-hover:border-slate-700 transition-colors">
        {getCategoryIcon(product.name)}
        <span className="absolute bottom-2 right-2 prime-badge">
          <Truck className="w-3 h-3" /> Express
        </span>
      </div>

      {/* Content Section */}
      <div className="space-y-1.5 mt-2">
        
        {/* Star Ratings */}
        <div className="flex items-center gap-1 text-xs">
          <div className="star-rating">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
          </div>
          <span className="font-bold text-amber-400 text-xs">{rating}</span>
          <span className="text-slate-500 text-[11px]">({reviewCount})</span>
        </div>

        {/* Title */}
        <h3 className="font-heading font-bold text-sm text-slate-100 group-hover:text-blue-400 transition-colors line-clamp-1">
          {product.name}
        </h3>

        {/* Description */}
        <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed h-8">
          {product.description || "Enterprise grade hardware component."}
        </p>

      </div>

      {/* Price & Add to Cart Footer */}
      <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between gap-3 mt-4">
        
        {/* Price Display */}
        <div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-heading font-extrabold text-lg text-white">
              ${currentPrice.toFixed(2)}
            </span>
            <span className="text-xs text-slate-500 line-through">
              ${msrpPrice}
            </span>
          </div>
          <span className="text-[10px] text-emerald-400 block font-semibold">FREE One-Day Delivery</span>
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={() => onAddToCart(product.id)}
          disabled={isOutOfStock || isAdding}
          className={`btn text-xs py-2 px-3.5 font-bold transition-all ${
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
              <span>Add</span>
            </>
          )}
        </button>

      </div>

    </div>
  );
}
