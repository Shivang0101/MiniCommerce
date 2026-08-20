import React, { useState, useEffect } from 'react';
import { X, User, ShieldCheck, Clock, PackageCheck, ShoppingBag, DollarSign, Calendar, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';
import { apiRequest } from '../api';

export default function ProfileModal({ isOpen, onClose, user, productsMap }) {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedOrderId, setExpandedOrderId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    if (isOpen && user) {
      fetchOrders();
    }
  }, [isOpen, user]);

  const fetchOrders = async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await apiRequest('/orders', 'GET', null, true);
      setOrders(data || []);
    } catch (err) {
      setError(err.message || 'Failed to load order history');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyId = (id) => {
    navigator.clipboard.writeText(id);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleExpand = (id) => {
    setExpandedOrderId(expandedOrderId === id ? null : id);
  };

  if (!isOpen || !user) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade overflow-y-auto">
      {/* Backdrop */}
      <div onClick={onClose} className="fixed inset-0 bg-slate-950/80 backdrop-blur-md"></div>

      {/* Modal Container */}
      <div className="glass-panel max-w-2xl w-full max-h-[90vh] flex flex-col relative border border-slate-800 bg-slate-950/95 shadow-2xl z-10 overflow-hidden my-auto">
        
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-500 p-0.5 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <User className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <div>
              <h2 className="font-heading font-bold text-lg text-white">Account Profile & Orders</h2>
              <p className="text-xs text-slate-400">Manage user session & purchase history</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-200 p-2 rounded-lg hover:bg-slate-900 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* User Profile Card */}
          <div className="glass-panel p-5 border border-slate-800/90 bg-slate-900/60 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 font-heading font-bold text-lg">
                {user.email ? user.email.substring(0, 2).toUpperCase() : 'US'}
              </div>
              <div>
                <h3 className="font-heading font-bold text-base text-white">{user.email}</h3>
                <div className="flex items-center gap-2 text-xs text-slate-400 mt-0.5">
                  <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Authenticated Session</span>
                </div>
              </div>
            </div>

            <div className="text-right">
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-wider block">Total Orders</span>
              <span className="font-heading font-extrabold text-xl text-cyan-400">{orders.length}</span>
            </div>
          </div>

          {/* Section Heading */}
          <div className="flex items-center justify-between">
            <h3 className="font-heading font-bold text-base text-slate-200 flex items-center gap-2">
              <PackageCheck className="w-4 h-4 text-indigo-400" />
              <span>Previous Orders</span>
            </h3>
            <button
              onClick={fetchOrders}
              className="text-xs text-indigo-400 hover:text-indigo-300 font-semibold"
            >
              Refresh History
            </button>
          </div>

          {/* Order List */}
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="glass-panel p-4 h-24 skeleton"></div>
              ))}
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl">
              {error}
            </div>
          ) : orders.length === 0 ? (
            <div className="text-center py-12 glass-panel border border-slate-800">
              <ShoppingBag className="w-10 h-10 text-slate-600 mx-auto mb-3" />
              <p className="text-sm font-semibold text-slate-400">No Previous Orders Found</p>
              <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
                Add products to your cart and execute an atomic checkout to view order confirmations here.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => {
                const isExpanded = expandedOrderId === order.id;
                const formattedDate = new Date(order.created_at).toLocaleString();

                return (
                  <div
                    key={order.id}
                    className="glass-panel border border-slate-800/90 overflow-hidden transition-all"
                  >
                    {/* Order Summary Row */}
                    <div
                      onClick={() => toggleExpand(order.id)}
                      className="p-4 flex flex-wrap items-center justify-between gap-3 cursor-pointer hover:bg-slate-900/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="px-2.5 py-1 text-[10px] font-bold rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {order.status}
                        </span>

                        <div>
                          <div className="flex items-center gap-2">
                            <span className="font-mono text-xs font-semibold text-slate-200">
                              Order #{String(order.id).substring(0, 8)}...
                            </span>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleCopyId(order.id); }}
                              className="text-slate-500 hover:text-cyan-400 p-0.5"
                              title="Copy Order ID"
                            >
                              {copiedId === order.id ? (
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                              ) : (
                                <Copy className="w-3.5 h-3.5" />
                              )}
                            </button>
                          </div>
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-400 mt-0.5">
                            <Calendar className="w-3 h-3 text-slate-500" />
                            <span>{formattedDate}</span>
                          </div>
                        </div>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <span className="text-[10px] text-slate-500 block">Total</span>
                          <span className="font-heading font-extrabold text-sm text-white">
                            ${parseFloat(order.total_amount).toFixed(2)}
                          </span>
                        </div>

                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-slate-400" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-slate-400" />
                        )}
                      </div>
                    </div>

                    {/* Order Details Drawer */}
                    {isExpanded && (
                      <div className="p-4 bg-slate-950/80 border-t border-slate-800/80 space-y-3">
                        <h4 className="text-xs font-semibold text-slate-300">Purchased Items ({order.order_items.length})</h4>
                        
                        <div className="space-y-2">
                          {order.order_items.map((item) => {
                            const cachedProduct = productsMap[item.product_id] || item.product;
                            const name = cachedProduct?.name || `Product #${String(item.product_id).substring(0, 8)}`;
                            const unitPrice = parseFloat(item.price);
                            const lineTotal = unitPrice * item.quantity;

                            return (
                              <div
                                key={item.id}
                                className="flex items-center justify-between text-xs p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/60"
                              >
                                <div className="min-w-0 flex-1 pr-2">
                                  <span className="font-medium text-slate-200 block truncate">{name}</span>
                                  <span className="text-[11px] text-slate-400">
                                    Qty: <strong className="text-slate-200">{item.quantity}</strong> × ${unitPrice.toFixed(2)}
                                  </span>
                                </div>

                                <div className="font-heading font-bold text-slate-200">
                                  ${lineTotal.toFixed(2)}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}

                  </div>
                );
              })}
            </div>
          )}

        </div>

      </div>
    </div>
  );
}
