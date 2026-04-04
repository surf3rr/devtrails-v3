import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';

const fmt = (n) => '₹' + Number(n).toLocaleString('en-IN', { minimumFractionDigits: 2 });

// ── Tiny UI atoms ─────────────────────────────────────────────────────────────
function Card({ children, className = '' }) {
  return (
    <div className={`rounded-2xl p-5 border transition-colors duration-300 ${className}`}>
      {children}
    </div>
  );
}

function Badge({ children, color = 'emerald' }) {
  const map = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    red:     'bg-red-500/10    text-red-400    border-red-500/30',
    blue:    'bg-blue-500/10   text-blue-400   border-blue-500/30',
    amber:   'bg-amber-500/10  text-amber-400  border-amber-500/30',
  };
  return (
    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full border ${map[color]}`}>
      {children}
    </span>
  );
}

// ── Navbar ────────────────────────────────────────────────────────────────────
function Navbar({ dark, setDark, onLogout }) {
  const bar = dark
    ? 'bg-[#111827]/80 border-[#1e2d45] text-white'
    : 'bg-white/80 border-slate-200 text-slate-900';

  return (
    <nav className={`sticky top-0 z-30 backdrop-blur-xl border-b px-4 md:px-8 h-14 flex items-center justify-between ${bar}`}>
      <div className="flex items-center gap-2">
        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[#00e5a0] to-[#0057ff] flex items-center justify-center">
          <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
            <path d="M8 1L14 4.5V11.5L8 15L2 11.5V4.5L8 1Z" stroke="white" strokeWidth="1.5" strokeLinejoin="round"/>
            <path d="M8 5V11M5 6.5L8 8.5L11 6.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <span className="font-mono-custom font-bold text-sm tracking-tight">
          Parametric<span className="text-[#00e5a0]">Guard</span>
        </span>
      </div>

      <div className="flex items-center gap-3">
        {/* Dark/Light toggle */}
        <button
          onClick={() => setDark(d => !d)}
          className={`relative w-12 h-6 rounded-full transition-colors duration-300 ${dark ? 'bg-[#00e5a0]/30' : 'bg-slate-200'}`}
        >
          <div className={`absolute top-0.5 w-5 h-5 rounded-full flex items-center justify-center text-xs transition-all duration-300 ${dark ? 'left-6 bg-[#00e5a0]' : 'left-0.5 bg-white shadow'}`}>
            {dark ? '🌙' : '☀️'}
          </div>
        </button>

        <button
          onClick={onLogout}
          className={`text-xs font-semibold px-3 py-1.5 rounded-lg border transition-all duration-150 hover:opacity-80 ${dark ? 'border-[#1e2d45] text-slate-400' : 'border-slate-300 text-slate-600'}`}
        >
          Logout
        </button>
      </div>
    </nav>
  );
}

// ── Sections ──────────────────────────────────────────────────────────────────
function UserCard({ user, dark }) {
  const card = dark ? 'bg-[#111827] border-[#1e2d45]' : 'bg-white border-slate-200';
  const sub  = dark ? 'text-slate-400' : 'text-slate-500';
  const val  = dark ? 'text-white' : 'text-slate-900';

  return (
    <Card className={`${card} fade-up relative overflow-hidden`}>
      {/* Decorative blob */}
      <div className="absolute -top-6 -right-6 w-32 h-32 rounded-full bg-gradient-to-br from-[#00e5a0]/10 to-[#0057ff]/10 blur-2xl pointer-events-none"/>
      <p className={`text-xs font-semibold uppercase tracking-widest mb-3 ${sub}`}>Account</p>
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className={`text-xl font-bold mb-0.5 ${val}`}>{user?.name || '—'}</h2>
          <p className={`text-sm flex items-center gap-1 ${sub}`}>
            <svg width="12" height="12" viewBox="0 0 16 16" fill="none" className="flex-shrink-0">
              <path d="M8 1.5C5.51 1.5 3.5 3.51 3.5 6c0 3.75 4.5 8.5 4.5 8.5s4.5-4.75 4.5-8.5c0-2.49-2.01-4.5-4.5-4.5z" stroke="currentColor" strokeWidth="1.3"/>
              <circle cx="8" cy="6" r="1.5" stroke="currentColor" strokeWidth="1.3"/>
            </svg>
            {user?.location}
          </p>
        </div>
        <Badge color={user?.policy_active ? 'emerald' : 'red'}>
          {user?.policy_active ? '● Active' : '○ Inactive'}
        </Badge>
      </div>

      <div className="mt-4 pt-4 border-t border-dashed grid grid-cols-2 gap-4"
        style={{borderColor: dark ? '#1e2d45' : '#e2e8f0'}}>
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Wallet Balance</p>
          <p className={`text-lg font-bold font-mono-custom text-[#00e5a0]`}>{user ? fmt(user.wallet_balance) : '—'}</p>
        </div>
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Policy Status</p>
          <p className={`text-base font-semibold ${val}`}>{user?.policy_active ? 'Protected' : 'Unprotected'}</p>
        </div>
      </div>
    </Card>
  );
}

function PolicyCard({ policy, dark, onBuy }) {
  const card = dark ? 'bg-[#111827] border-[#1e2d45]' : 'bg-white border-slate-200';
  const sub  = dark ? 'text-slate-400' : 'text-slate-500';
  const val  = dark ? 'text-white' : 'text-slate-900';
  const [busy, setBusy] = useState(false);
  const [msg,  setMsg]  = useState('');

  const handle = async () => {
    setBusy(true); setMsg('');
    try {
      const r = await fetch(`${API}/buy-policy`, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({coverage:50000}) });
      const d = await r.json();
      setMsg(d.message);
      onBuy();
    } catch { setMsg('Backend unreachable — using mock.'); onBuy(); }
    finally { setBusy(false); }
  };

  return (
    <Card className={`${card} fade-up-2`}>
      <p className={`text-xs font-semibold uppercase tracking-widest mb-3 ${sub}`}>Policy Details</p>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Weekly Premium</p>
          <p className={`text-lg font-bold font-mono-custom ${val}`}>{policy ? fmt(policy.weekly_premium) : '—'}</p>
        </div>
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Coverage</p>
          <p className={`text-lg font-bold font-mono-custom text-[#0057ff]`}>{policy ? fmt(policy.coverage_amount) : '—'}</p>
        </div>
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Active Since</p>
          <p className={`text-sm font-medium ${val}`}>{policy?.start_date || '—'}</p>
        </div>
        <div>
          <p className={`text-xs ${sub} mb-0.5`}>Days Active</p>
          <p className={`text-sm font-medium ${val}`}>{policy ? `${policy.days_active} days` : '—'}</p>
        </div>
      </div>
      {msg && <p className="text-xs text-emerald-400 mb-3">{msg}</p>}
      <button
        onClick={handle}
        disabled={busy}
        className="w-full py-2.5 rounded-xl text-sm font-semibold text-white
          bg-gradient-to-r from-[#0057ff] to-[#00e5a0]
          hover:opacity-90 active:scale-[.98] transition-all disabled:opacity-50"
      >
        {busy ? 'Processing…' : '+ Buy / Renew Policy'}
      </button>
    </Card>
  );
}

function EventCard({ event, dark }) {
  const triggered = event?.triggered;
  const card = dark ? 'bg-[#111827] border-[#1e2d45]' : 'bg-white border-slate-200';
  const sub  = dark ? 'text-slate-400' : 'text-slate-500';
  const val  = dark ? 'text-white' : 'text-slate-900';

  // Rainfall bar %
  const pct = event ? Math.min(100, (event.rainfall_mm / 120) * 100) : 0;
  const barColor = triggered ? '#ef4444' : '#00e5a0';

  return (
    <Card className={`${card} fade-up-3 relative overflow-hidden`}>
      {triggered && (
        <div className="absolute inset-0 pointer-events-none rounded-2xl"
          style={{boxShadow:'inset 0 0 0 1.5px rgba(239,68,68,0.4)', background:'rgba(239,68,68,0.03)'}}/>
      )}
      <div className="flex items-center justify-between mb-3">
        <p className={`text-xs font-semibold uppercase tracking-widest ${sub}`}>Event Status</p>
        <div className="flex items-center gap-1.5">
          <span className={`w-2 h-2 rounded-full pulse-dot ${triggered ? 'bg-red-500' : 'bg-emerald-400'}`}/>
          <span className={`text-xs ${sub}`}>{event?.last_checked || 'Live'}</span>
        </div>
      </div>

      <p className={`text-base font-semibold mb-4 ${triggered ? 'text-red-400' : 'text-emerald-400'}`}>
        {event?.status || 'Loading…'}
      </p>

      {/* Rainfall bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs mb-1">
          <span className={sub}>Rainfall</span>
          <span className={`font-mono-custom font-bold`} style={{color:barColor}}>
            {event ? `${event.rainfall_mm} mm` : '—'}
          </span>
        </div>
        <div className={`h-2 rounded-full overflow-hidden ${dark?'bg-slate-800':'bg-slate-100'}`}>
          <div className="h-full rounded-full transition-all duration-700" style={{width:`${pct}%`, background: barColor}}/>
        </div>
        <div className="flex justify-between text-xs mt-1">
          <span className={sub}>0 mm</span>
          <span className={sub}>Threshold: {event?.threshold_mm}mm</span>
          <span className={sub}>120 mm</span>
        </div>
      </div>

      {triggered && (
        <div className="rounded-xl p-3 bg-red-500/10 border border-red-500/30 flex items-center justify-between">
          <div>
            <p className="text-xs font-semibold text-red-400 mb-0.5">🚨 Payout Triggered</p>
            <p className={`text-xs ${sub}`}>Auto-credit on next cycle</p>
          </div>
          <p className="text-lg font-bold font-mono-custom text-red-400">{fmt(event.payout_amount)}</p>
        </div>
      )}
    </Card>
  );
}

function ClaimsCard({ claims, dark }) {
  const card = dark ? 'bg-[#111827] border-[#1e2d45]' : 'bg-white border-slate-200';
  const sub  = dark ? 'text-slate-400' : 'text-slate-500';
  const val  = dark ? 'text-white' : 'text-slate-900';
  const row  = dark ? 'hover:bg-white/[.03]' : 'hover:bg-slate-50';
  const divider = dark ? 'border-[#1e2d45]' : 'border-slate-100';

  const icons = { 'Heavy Rain':'🌧️', 'Traffic Disruption':'🚦' };

  return (
    <Card className={`${card} fade-up-4`}>
      <p className={`text-xs font-semibold uppercase tracking-widest mb-4 ${sub}`}>Recent Payouts</p>
      <div className="space-y-0">
        {claims?.length ? claims.map((c, i) => (
          <div key={c.id} className={`flex items-center gap-3 py-3 ${row} rounded-xl px-2 transition-colors cursor-default ${i < claims.length-1 ? `border-b ${divider}` : ''}`}>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-base flex-shrink-0"
              style={{background: dark ? '#1e2d45' : '#f1f5f9'}}>
              {icons[c.event] || '📋'}
            </div>
            <div className="flex-1 min-w-0">
              <p className={`text-sm font-medium truncate ${val}`}>{c.event}</p>
              <p className={`text-xs ${sub}`}>{c.date}</p>
            </div>
            <div className="text-right flex-shrink-0">
              <p className="text-sm font-bold font-mono-custom text-[#00e5a0]">+{fmt(c.amount)}</p>
              <Badge color="emerald">{c.status}</Badge>
            </div>
          </div>
        )) : (
          <p className={`text-sm text-center py-6 ${sub}`}>No payouts yet</p>
        )}
      </div>
    </Card>
  );
}

// ── Dashboard page ────────────────────────────────────────────────────────────
export default function Dashboard({ dark, setDark, onLogout }) {
  const navigate = useNavigate();
  const [user,   setUser]   = useState(null);
  const [policy, setPolicy] = useState(null);
  const [event,  setEvent]  = useState(null);
  const [claims, setClaims] = useState([]);

  const fetchAll = useCallback(async () => {
    const safe = async (url, fallback) => {
      try { const r = await fetch(url); return r.ok ? r.json() : fallback; }
      catch { return fallback; }
    };

    const [u, p, ev, cl] = await Promise.all([
      safe(`${API}/user`,   { name:'Arjun Mehta', location:'Chennai, TN', wallet_balance:12450, policy_active:true }),
      safe(`${API}/policy`, { weekly_premium:149, coverage_amount:50000, start_date:'2025-02-14', days_active:47 }),
      safe(`${API}/events`, { rainfall_mm:55, threshold_mm:80, triggered:false, status:'No disruption detected', last_checked:'--:--', payout_amount:0 }),
      safe(`${API}/claims`, { claims:[] }),
    ]);
    setUser(u); setPolicy(p); setEvent(ev); setClaims(cl.claims || []);
  }, []);

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 8000);
    return () => clearInterval(id);
  }, [fetchAll]);

  const bg = dark
    ? 'bg-[#0a0f1e] text-white'
    : 'bg-gradient-to-br from-slate-50 to-blue-50/50 text-slate-900';

  const handleLogout = () => { onLogout(); navigate('/'); };

  return (
    <div className={`min-h-screen ${bg} transition-colors duration-300`}>
      {/* Background grid */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className={`absolute top-0 left-0 w-full h-full opacity-[.03] ${dark ? 'block' : 'hidden'}`}
          style={{backgroundImage:'linear-gradient(#00e5a0 1px,transparent 1px),linear-gradient(90deg,#00e5a0 1px,transparent 1px)',backgroundSize:'48px 48px'}}/>
        <div className={`absolute top-0 right-0 w-[500px] h-[500px] rounded-full blur-[120px] opacity-10 ${dark?'bg-[#0057ff]':'bg-blue-300'}`}/>
        <div className={`absolute bottom-0 left-0 w-96 h-96 rounded-full blur-[100px] opacity-10 ${dark?'bg-[#00e5a0]':'bg-emerald-200'}`}/>
      </div>

      <Navbar dark={dark} setDark={setDark} onLogout={handleLogout}/>

      <main className="relative max-w-5xl mx-auto px-4 md:px-6 py-6 grid gap-4
        grid-cols-1 md:grid-cols-2 lg:grid-cols-2">

        {/* Row 1: User + Policy */}
        <UserCard   user={user}     dark={dark}/>
        <PolicyCard policy={policy} dark={dark} onBuy={fetchAll}/>

        {/* Row 2: Event + Claims (spans both on mobile) */}
        <EventCard  event={event}   dark={dark}/>
        <ClaimsCard claims={claims} dark={dark}/>
      </main>

      {/* Footer */}
      <footer className={`text-center pb-6 text-xs ${dark?'text-slate-600':'text-slate-400'}`}>
        ParametricGuard · Demo Build · Data refreshes every 8s
      </footer>
    </div>
  );
}
