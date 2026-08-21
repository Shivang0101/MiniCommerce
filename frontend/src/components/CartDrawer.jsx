import React from 'react';
import { X, Trash2, Plus, Minus, Zap, ShoppingBag, ShieldCheck } from 'lucide-react';

export default function CartDrawer({
  isOpen,
  onClose,
  cart,
  productsMap,
  onUpdateQuantity,
  onRemoveItem,
  onCheckout,
  isCheckingOut,
  user
}) {
  if (!isOpen) return null;

  const items = cart?.cart_items || [];
  
  // Calculate cart total defensively
  let totalAmount = 0;
  items.forEach((item) => {
    if (!item) return;
    const product = (productsMap && productsMap[item.product_id]) || item.product;
    const price = product && product.price ? parseFloat(product.price) : 0;
    totalAmount += price * (item.quantity || 1);
  });

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fade">
      {/* Overlay backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md transition-opacity"
      ></div>

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md glass-panel border-l border-slate-800 bg-slate-950/95 flex flex-col justify-between shadow-2xl">
          
          {/* Header */}
          <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
                <ShoppingBag className="w-5 h-5" />
              </div>
              <div>
                <h2 className="font-heading font-bold text-lg text-white">Your Cart</h2>
                <p className="text-xs text-slate-400">{items.length} unique item(s)</p>
              </div>
            </div>

            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-slate-900 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Item List */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {items.length === 0 ? (
              <div className="text-center py-16">
                <ShoppingBag className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <p className="text-sm font-semibold text-slate-400">Your shopping cart is empty</p>
                <p className="text-xs text-slate-500 mt-1">Browse products and add items to begin testing checkout.</p>
              </div>
            ) : (
              items.map((item) => {
                if (!item) return null;
                const product = (productsMap && productsMap[item.product_id]) || item.product;
                const name = product?.name || (item.product_id ? `Product #${String(item.product_id).substring(0, 8)}` : "Item");
                const price = product?.price ? parseFloat(product.price) : 0;
                const quantity = item.quantity || 1;

                return (
                  <div
                    key={item.id || Math.random()}
                    className="glass-panel p-4 flex items-center justify-between gap-3 border border-slate-800/90"
                  >
                    <div className="flex-1 min-w-0">
                      <h4 className="font-heading font-semibold text-sm text-slate-200 truncate">
                        {name}
                      </h4>
                      <div className="text-xs text-indigo-400 font-bold mt-0.5">
                        ${price.toFixed(2)} <span className="text-slate-500 font-normal">each</span>
                      </div>
                    </div>

                    {/* Quantity Controls */}
                    <div className="flex items-center gap-2 bg-slate-900/90 border border-slate-800 px-2 py-1 rounded-lg">
                      <button
                        onClick={() => onUpdateQuantity(item.id, quantity - 1)}
                        className="text-slate-400 hover:text-white p-0.5"
                      >
                        <Minus className="w-3 h-3" />
                      </button>

                      <span className="text-xs font-bold text-slate-200 w-5 text-center">
                        {quantity}
                      </span>

                      <button
                        onClick={() => onUpdateQuantity(item.id, quantity + 1)}
                        className="text-slate-400 hover:text-white p-0.5"
                      >
                        <Plus className="w-3 h-3" />
                      </button>
                    </div>

                    {/* Delete Item */}
                    <button
                      onClick={() => onRemoveItem(item.id)}
                      className="text-slate-500 hover:text-rose-400 p-1 transition-colors"
                      title="Remove item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                );
              })
            )}
          </div>

          {/* Footer Checkout Summary */}
          {items.length > 0 && (
            <div className="p-6 border-t border-slate-800 bg-slate-950/90 space-y-4">
              
              {/* Idempotency Protection Indicator */}
              <div className="flex items-center gap-2 text-[11px] text-slate-400 bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-800">
                <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
                <span>Protected by <strong className="text-slate-200">Idempotency-Key</strong> & row locks</span>
              </div>

              {/* Total Amount */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-400 font-medium">Grand Total</span>
                <span className="font-heading font-extrabold text-2xl text-white">
                  ${totalAmount.toFixed(2)}
                </span>
              </div>

              {/* Checkout Button & Order Status Pill */}
              <button
                onClick={onCheckout}
                disabled={isCheckingOut}
                className="btn btn-accent w-full py-3 text-sm font-bold flex items-center justify-center gap-2 shadow-lg shadow-emerald-500/20"
              >
                {isCheckingOut ? (
                  <div className="flex items-center gap-2">
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    <span className="animate-pulse">Processing ➔ Confirmed ➔ Receipt Emailed</span>
                  </div>
                ) : (
                  <>
                    <Zap className="w-4 h-4 fill-white" />
                    <span>⚡ Atomic Checkout (ARQ Offloaded)</span>
                  </>
                )}
              </button>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}
