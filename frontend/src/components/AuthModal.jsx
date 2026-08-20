import React, { useState } from 'react';
import { X, Lock, Mail, Sparkles, UserCheck } from 'lucide-react';
import { apiRequest, setAuth } from '../api';

export default function AuthModal({ isOpen, onClose, onLoginSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await apiRequest('/auth/register', 'POST', { email, password });
      }

      // 1. Get JWT bearer token from /auth/login
      const { data: tokenData } = await apiRequest('/auth/login', 'POST', { email, password });
      const token = tokenData.access_token;
      
      // Save token temporarily so /auth/me request includes Authorization header
      localStorage.setItem("token", token);

      // 2. Fetch full user profile from /auth/me
      const { data: userProfile } = await apiRequest('/auth/me', 'GET', null, true);

      // 3. Save auth token and user profile
      setAuth(token, userProfile);
      onLoginSuccess(userProfile);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickDemoLogin = async () => {
    setError('');
    setLoading(true);

    try {
      const { data: tokenData } = await apiRequest('/auth/login', 'POST', {
        email: 'alice@example.com',
        password: 'Password123!'
      });
      const token = tokenData.access_token;
      localStorage.setItem("token", token);

      const { data: userProfile } = await apiRequest('/auth/me', 'GET', null, true);
      setAuth(token, userProfile);
      onLoginSuccess(userProfile);
      onClose();
    } catch (err) {
      setError("Demo account unavailable. Try registering a new account.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade">
      <div onClick={onClose} className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"></div>

      <div className="glass-panel max-w-md w-full p-6 relative border border-slate-800 bg-slate-950/95 shadow-2xl z-10">
        
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-slate-500 hover:text-slate-200 p-1"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <UserCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-heading font-bold text-lg text-white">
              {isRegister ? 'Create Benchmark Account' : 'Authenticate Session'}
            </h3>
            <p className="text-xs text-slate-400">JWT Token Security</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="alice@example.com"
                className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary w-full py-2.5 text-xs font-bold"
          >
            {loading ? 'Authenticating...' : isRegister ? 'Register Account' : 'Sign In'}
          </button>
        </form>

        <div className="relative my-4">
          <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-slate-800"></div></div>
          <div className="relative flex justify-center text-[10px] uppercase"><span className="bg-slate-950 px-2 text-slate-500 font-semibold">Or Quick Demo</span></div>
        </div>

        <button
          onClick={handleQuickDemoLogin}
          disabled={loading}
          className="btn btn-secondary w-full py-2 text-xs flex items-center justify-center gap-2 border-indigo-500/20 text-indigo-300"
        >
          <Sparkles className="w-4 h-4 text-cyan-400" />
          <span>Quick Login as Demo User (Alice)</span>
        </button>

        <div className="mt-4 text-center">
          <button
            onClick={() => { setIsRegister(!isRegister); setError(''); }}
            className="text-xs text-slate-400 hover:text-indigo-400"
          >
            {isRegister ? 'Already have an account? Sign In' : "Don't have an account? Register"}
          </button>
        </div>

      </div>
    </div>
  );
}
