import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Login({ onLogin, dark }) {
  const [email, setEmail] = useState('arjun@example.com');
  const [password, setPassword] = useState('password');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    setError('');
    if (!email || !password) { setError('Please fill in all fields.'); return; }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onLogin();
      navigate('/dashboard');
    }, 900);
  };

  const bg = dark
    ? 'bg-[#0a0f1e] text-white'
    : 'bg-gradient-to-br from-slate-100 to-blue-50 text-slate-900';
  const card = dark
    ? 'bg-[#111827] border border-[#1e2d45] shadow-2xl'
    : 'bg-white border border-slate-200 shadow-2xl';
  const input = dark
    ? 'bg-[#0a0f1e] border-[#1e2d45] text-white placeholder-slate-500 focus:border-[#00e5a0]'
    : 'bg-slate-50 border-slate-300 text-slate-900 placeholder-slate-400 focus:border-blue-500';
  const label = dark ? 'text-slate-400' : 'text-slate-600';

  return (
    <div className={`min-h-screen flex items-center justify-center ${bg} transition-colors duration-300`}>
      {/* Background grid decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className={`absolute top-0 left-0 w-full h-full opacity-5 ${dark ? 'block' : 'hidden'}`}
          style={{backgroundImage:'linear-gradient(#00e5a0 1px,transparent 1px),linear-gradient(90deg,#00e5a0 1px,transparent 1px)',backgroundSize:'48px 48px'}}/>
        <div className={`absolute -top-32 -right-32 w-96 h-96 rounded-full blur-3xl ${dark?'bg-[#0057ff22]':'bg-blue-200'} opacity-40`}/>
        <div className={`absolute -bottom-20 -left-20 w-72 h-72 rounded-full blur-3xl ${dark?'bg-[#00e5a022]':'bg-emerald-100'} opacity-50`}/>
      </div>

      <div className={`relative w-full max-w-md mx-4 rounded-2xl p-8 fade-up ${card}`}>
        {/* Logo */}
        <div className="mb-8 text-center">
          <div className="inline-flex items-center gap-2 mb-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#00e5a0] to-[#0057ff] flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                <path d="M8 1L14 4.5V11.5L8 15L2 11.5V4.5L8 1Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
                <path d="M8 5V11M5 6.5L8 8.5L11 6.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="font-mono-custom font-bold text-lg tracking-tight">
              Parametric<span className="text-[#00e5a0]">Guard</span>
            </span>
          </div>
          <p className={`text-sm ${label}`}>Parametric insurance, automated &amp; instant</p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className={`block text-xs font-semibold mb-1.5 uppercase tracking-wider ${label}`}>Email</label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className={`w-full rounded-xl border px-4 py-3 text-sm outline-none transition-all duration-200 ${input}`}
              placeholder="you@example.com"
            />
          </div>
          <div>
            <label className={`block text-xs font-semibold mb-1.5 uppercase tracking-wider ${label}`}>Password</label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              className={`w-full rounded-xl border px-4 py-3 text-sm outline-none transition-all duration-200 ${input}`}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <div className="text-xs text-red-400 bg-red-900/20 border border-red-800/40 rounded-lg px-3 py-2">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl font-semibold text-sm tracking-wide
              bg-gradient-to-r from-[#00e5a0] to-[#0057ff] text-white
              hover:opacity-90 active:scale-[.98] transition-all duration-150
              disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="white" strokeWidth="3" strokeDasharray="30" strokeDashoffset="10"/>
                </svg>
                Signing in…
              </>
            ) : 'Login'}
          </button>
        </form>

        <p className={`mt-6 text-center text-xs ${label}`}>
          Demo credentials pre-filled ↑ — just click Login
        </p>
      </div>
    </div>
  );
}
