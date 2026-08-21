import React, { useState, useEffect } from 'react';
import { ShoppingBag, Search, Zap, User, LogOut, ShieldCheck, History, Bell, Activity, Gauge, MapPin, ChevronDown } from 'lucide-react';

export default function Navbar({ search, setSearch, cartCount, user, onOpenCart, onOpenAuth, onLogout, onOpenProfile, isAdminView, onToggleAdmin, onOpenStoreManager }) {
  const [notifications, setNotifications] = useState([
    { id: "init_1", type: "SYSTEM", title: "ARQ Worker Online", message: "Background task queue worker connected to Redis.", timestamp: Date.now() / 1000 }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [rateLimitQuota, setRateLimitQuota] = useState({ limit: 60, remaining: 60 });

  useEffect(() => {
    const handleRateLimitUpdate = (e) => {
      if (e.detail) {
        setRateLimitQuota({
          limit: parseInt(e.detail.limit || 60, 10),
          remaining: parseInt(e.detail.remaining || 60, 10)
        });
      }
    };
    window.addEventListener("ratelimit-update", handleRateLimitUpdate);
    return () => window.removeEventListener("ratelimit-update", handleRateLimitUpdate);
  }, []);

  const isStoreManager = user && (user.is_admin || user.role === 'STORE_MANAGER' || user.role === 'SRE_ADMIN');

  return (
    <header className="sticky top-0 z-40 w-full glass-panel border-b border-slate-800/90 bg-slate-950/95 backdrop-blur-xl shadow-2xl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between gap-4">
        
        {/* Logo & Delivery Location Indicator */}
        <div className="flex items-center gap-4">
          <div 
            className="flex items-center gap-3 cursor-pointer group" 
            onClick={() => { if (isAdminView) onToggleAdmin(); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <Zap className="w-5 h-5 text-cyan-400 fill-cyan-400/20" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-heading font-extrabold text-xl tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                  MiniCommerce <span className="gradient-text">Pro</span>
                </span>
                <span className="px-2 py-0.5 text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full">
                  STORE
                </span>
              </div>
              <p className="text-[11px] text-slate-400 hidden sm:block">Enterprise Hardware & Electronics</p>
            </div>
          </div>

          {/* Delivery Location Pill (Amazon Style) */}
          <div className="hidden lg:flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800/80 text-xs text-slate-300">
            <MapPin className="w-3.5 h-3.5 text-cyan-400" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] uppercase font-bold text-slate-500">Deliver to</span>
              <span className="font-semibold text-slate-200 text-[11px]">New York 10001</span>
            </div>
          </div>
        </div>

        {/* Global Search Bar */}
        {!isAdminView && (
          <div className="flex-1 max-w-md relative hidden md:block">
            <div className="relative">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search products (e.g., Keyboard, Monitor, Audio)..."
                className="w-full pl-10 pr-12 py-2.5 bg-slate-900/90 border border-slate-800 rounded-xl text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
              {search && (
                <button
                  onClick={() => setSearch('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-slate-300 font-semibold"
                >
                  Clear
                </button>
              )}
            </div>
          </div>
        )}

        {/* Right Action Controls */}
        <div className="flex items-center gap-3">
          
          {/* Rate Limit Quota Meter */}
          <div className="hidden xl:flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl" title="Redis Sliding-Window Rate Limit Quota">
            <Gauge className="w-3.5 h-3.5 text-cyan-400" />
            <div className="flex flex-col text-left">
              <span className="text-[9px] uppercase font-bold tracking-wider text-slate-500">Rate Quota</span>
              <span className="text-xs font-semibold text-cyan-300">
                {rateLimitQuota.remaining} / {rateLimitQuota.limit} reqs
              </span>
            </div>
          </div>

          {/* Store Manager Portal Button */}
          {isStoreManager && onOpenStoreManager && (
            <button
              onClick={onOpenStoreManager}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30 hover:bg-amber-500/20 transition-all"
              title="Store Manager Inventory & Catalog Portal"
            >
              <span>🏬 Store Portal</span>
            </button>
          )}

          {/* Admin Observability Toggle Button */}
          <button
            onClick={onToggleAdmin}
            className={`flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-bold transition-all border ${
              isAdminView
                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-lg shadow-cyan-500/10'
                : 'bg-slate-900 hover:bg-slate-800 text-slate-300 border-slate-800'
            }`}
            title="Toggle Admin Observability Control Panel"
          >
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>{isAdminView ? 'Storefront' : 'Admin Panel'}</span>
          </button>


          {/* Notification Inbox Bell */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2.5 bg-slate-900/90 hover:bg-slate-800 border border-slate-800 rounded-xl text-slate-300 hover:text-white transition-all"
              title="Async Task Notifications"
            >
              <Bell className="w-4 h-4 text-blue-400" />
              {notifications.length > 0 && (
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-cyan-400 rounded-full animate-ping" />
              )}
            </button>

            {/* Notifications Dropdown */}
            {showNotifications && (
              <div className="absolute right-0 mt-3 w-80 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-4 z-50 animate-in fade-in">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2 mb-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                    <Bell className="w-3.5 h-3.5 text-blue-400" /> Async Worker Stream
                  </h4>
                  <span className="text-[10px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-full font-semibold">
                    {notifications.length} Active
                  </span>
                </div>
                <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                  {notifications.map((n) => (
                    <div key={n.id} className="p-2.5 bg-slate-950/80 border border-slate-800/80 rounded-xl text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-cyan-300">{n.title}</span>
                        <span className="text-[10px] text-slate-500">Just now</span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-relaxed">{n.message}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* User Profile / Auth Control */}
          {user ? (
            <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-xl">
              <User className="w-4 h-4 text-blue-400" />
              <div className="hidden sm:flex flex-col text-left">
                <span className="text-xs font-bold text-slate-200 truncate max-w-[110px]">{user.email}</span>
                {user.is_admin && <span className="text-[9px] text-cyan-400 font-extrabold uppercase tracking-wider">ADMIN</span>}
              </div>
              <button
                onClick={onLogout}
                className="p-1 text-slate-400 hover:text-rose-400 transition-colors ml-1"
                title="Log Out"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="btn btn-secondary text-xs py-2 px-3.5 font-bold"
            >
              <User className="w-4 h-4 text-blue-400" />
              <span>Sign In</span>
            </button>
          )}

          {/* Cart Drawer Button */}
          <button
            onClick={onOpenCart}
            className="btn btn-primary text-xs py-2 px-4 flex items-center gap-2 font-bold shadow-lg shadow-blue-600/30"
          >
            <ShoppingBag className="w-4 h-4" />
            <span>Cart</span>
            {cartCount > 0 && (
              <span className="ml-1 px-1.5 py-0.5 rounded-full bg-white text-blue-700 font-extrabold text-[11px]">
                {cartCount}
              </span>
            )}
          </button>

        </div>

      </div>
    </header>
  );
}
