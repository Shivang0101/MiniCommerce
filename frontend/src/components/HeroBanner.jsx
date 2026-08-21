import React from 'react';
import { Sparkles, Truck, ShieldCheck, Zap, ArrowRight, Percent } from 'lucide-react';

export default function HeroBanner({ onSelectCategory }) {
  return (
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-slate-900 via-slate-950 to-slate-900 border border-slate-800 shadow-2xl my-6">
      
      {/* Decorative Glow Orbs */}
      <div className="absolute -top-24 -left-24 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -right-24 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8 sm:py-10 flex flex-col md:flex-row items-center justify-between gap-8">
        
        {/* Left Deal Content */}
        <div className="space-y-4 max-w-2xl text-center md:text-left">
          
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-bold uppercase tracking-wider">
            <Percent className="w-3.5 h-3.5" />
            <span>Tech Deals Week — Up to 40% Off</span>
          </div>

          <h1 className="font-heading font-extrabold text-3xl sm:text-4xl lg:text-5xl tracking-tight text-white leading-tight">
            Enterprise Hardware & <br className="hidden sm:block" />
            <span className="gradient-text">Developer Workstations</span>
          </h1>

          <p className="text-slate-400 text-sm sm:text-base font-normal leading-relaxed max-w-xl">
            Upgrade your developer environment with high-performance mechanical keyboards, curved ultrawides, and studio audio rigs.
          </p>

          {/* Quick Category Action Pills */}
          <div className="pt-2 flex flex-wrap items-center justify-center md:justify-start gap-3">
            <button
              onClick={() => onSelectCategory('Keyboards')}
              className="btn btn-primary text-xs py-2.5 px-4 shadow-lg shadow-blue-600/25 flex items-center gap-2"
            >
              <span>Explore Keyboards</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onSelectCategory('Monitors')}
              className="btn btn-secondary text-xs py-2.5 px-4 border-slate-700 text-slate-200 hover:text-white"
            >
              <span>Curved Monitors</span>
            </button>
            <button
              onClick={() => onSelectCategory('Audio')}
              className="btn btn-secondary text-xs py-2.5 px-4 border-slate-700 text-slate-200 hover:text-white"
            >
              <span>Studio Audio</span>
            </button>
          </div>

        </div>

        {/* Right Feature Highlights Card */}
        <div className="w-full md:w-80 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-5 rounded-2xl space-y-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <Truck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">FREE Express Shipping</h4>
              <p className="text-[11px] text-slate-400">Orders over $49 ship next-day</p>
            </div>
          </div>

          <div className="border-t border-slate-800/80 pt-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">2-Year Hardware Protection</h4>
              <p className="text-[11px] text-slate-400">Includes 24/7 tech support</p>
            </div>
          </div>

          <div className="border-t border-slate-800/80 pt-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Zap className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-white">Async Task Checkout</h4>
              <p className="text-[11px] text-slate-400">PostgreSQL locks & ARQ offloading</p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
