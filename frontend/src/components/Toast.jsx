import React, { useEffect } from 'react';
import { CheckCircle2, AlertTriangle, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => {
        onClose();
      }, 6000);
      return () => clearTimeout(timer);
    }
  }, [toast, onClose]);

  if (!toast) return null;

  const isSuccess = toast.type === 'success';

  return (
    <div className="fixed bottom-6 right-6 z-50 max-w-md animate-fade">
      <div className={`glass-panel p-4 flex items-start gap-3 border shadow-2xl ${
        isSuccess ? 'border-emerald-500/40 bg-slate-950/95' : 'border-rose-500/40 bg-slate-950/95'
      }`}>
        {isSuccess ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        ) : (
          <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
        )}

        <div className="flex-1">
          <h4 className={`font-heading font-bold text-sm ${isSuccess ? 'text-emerald-400' : 'text-rose-400'}`}>
            {toast.title}
          </h4>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            {toast.message}
          </p>

          {toast.orderId && (
            <div className="mt-2 pt-2 border-t border-slate-800 text-[11px] font-mono text-slate-400">
              Order ID: <span className="text-cyan-400">{toast.orderId}</span>
            </div>
          )}
        </div>

        <button
          onClick={onClose}
          className="text-slate-500 hover:text-slate-300 p-1"
        >
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
