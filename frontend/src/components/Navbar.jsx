import React from 'react';
import { ShoppingBag, Search, Zap, User, LogOut, ShieldCheck, History } from 'lucide-react';

export default function Navbar({ search, setSearch, cartCount, user, onOpenCart, onOpenAuth, onLogout, onOpenProfile }) {
  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        
        {/* Logo & Version Badge */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
              <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-heading font-extrabold text-xl tracking-tight text-white">
                MiniCommerce <span className="gradient-text">V2</span>
              </span>
              <span className="px-2 py-0.5 text-[10px] font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">
                LAB
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Database & Concurrency Engineering</p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-md relative">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search 50,000+ products (e.g., Gaming, Pro, Monitor)..."
              className="w-full pl-10 pr-4 py-2.5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-300"
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Right Action Controls */}
        <div className="flex items-center gap-3">
          {/* User Profile Pill / Login */}
          {user ? (
            <div className="flex items-center gap-2">
              <button
                onClick={onOpenProfile}
                className="flex items-center gap-2 bg-slate-900/90 hover:bg-slate-800 border border-slate-800 px-3 py-1.5 rounded-xl transition-all"
                title="View Profile & Order History"
              >
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-semibold text-slate-200 truncate max-w-[120px]">
                  {user.email}
                </span>
                <History className="w-3.5 h-3.5 text-indigo-400 ml-1" />
              </button>

              <button
                onClick={onLogout}
                title="Logout"
                className="text-slate-400 hover:text-rose-400 p-2 rounded-lg hover:bg-slate-900 transition-colors"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn btn-secondary py-2 text-xs"
            >
              <User className="w-4 h-4 text-indigo-400" />
              <span>Login Demo</span>
            </button>
          )}

          {/* Cart Trigger Button */}
          <button
            onClick={onOpenCart}
            className="btn btn-primary py-2 relative"
          >
            <ShoppingBag className="w-4 h-4" />
            <span className="hidden sm:inline">Cart</span>
            {cartCount > 0 && (
              <span className="absolute -top-1.5 -right-1.5 bg-emerald-500 text-slate-950 font-bold text-[11px] w-5 h-5 rounded-full flex items-center justify-center shadow-lg shadow-emerald-500/30 animate-pulse">
                {cartCount}
              </span>
            )}
          </button>
        </div>

      </div>
    </header>
  );
}
