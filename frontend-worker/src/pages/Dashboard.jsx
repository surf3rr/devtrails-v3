import { useState, useEffect } from 'react'
import { CloudRain, TrendingUp, ShieldCheck, IndianRupee, Wind } from 'lucide-react'
import { collection, query, where, onSnapshot } from 'firebase/firestore'
import { db } from '../firebaseConfig'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const API = API_BASE.endsWith('/api') ? API_BASE : `${API_BASE}/api`

export default function Dashboard({ user: firebaseUser, profile }) {
  const [premiumInfo, setPremiumInfo] = useState(null)
  const [claims, setClaims] = useState([])
  const [rainfall, setRainfall] = useState(2.4)
  const [aqi] = useState(145)

  // ── Step 1: Handle Premium Fetch when Profile changes ─────────────────────
  useEffect(() => {
    if (!profile) return
    
    const fetchPremium = async () => {
      try {
        const res = await fetch(`${API}/premium/calculate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            plan: profile.plan || 'standard', 
            zone: 'hsr_layout', 
            platform: (profile.platform || 'swiggy').toLowerCase() 
          })
        })
        const pData = await res.json()
        setPremiumInfo(pData)
      } catch (e) {
        console.error("Premium fetch failed", e)
      }
    }
    fetchPremium()
  }, [profile])

  // ── Step 2: Real-time Claims Listener ──────────────────────────────────────
  useEffect(() => {
    if (!firebaseUser?.uid) return
    const claimsQuery = query(
      collection(db, 'claims'),
      where('userId', '==', firebaseUser.uid)
    )
    const unsubscribe = onSnapshot(claimsQuery, (snapshot) => {
      const liveClaims = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
      setClaims(liveClaims)
    })
    return () => unsubscribe()
  }, [firebaseUser?.uid])

  if (!profile || !premiumInfo) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', color: '#64748b' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: 40, height: 40, border: '3px solid #1e293b', borderTop: '3px solid #22c55e', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          <p style={{ fontSize: '0.875rem' }}>Syncing with Firebase...</p>
        </div>
      </div>
    )
  }

  const weeklyCap = premiumInfo.weekly_cap || 0
  const totalPaidThisWeek = claims
    .filter(c => {
      const weekAgo = Date.now() - 7 * 86400 * 1000
      const claimDate = c.created_at || Date.now()
      return (c.status === 'approved_paid' || c.status === 'PAID') && claimDate > weekAgo
    })
    .reduce((sum, c) => sum + (c.amount || 0), 0)
  
  const remainingCap = Math.max(0, weeklyCap - totalPaidThisWeek)
  const trustScore = profile.trustScore || 0.85
  const riskColor = trustScore > 0.8 ? '#4ade80' : trustScore > 0.5 ? '#facc15' : '#f87171'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      {/* Header */}
      <div>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#f1f5f9' }}>
          Good morning, {profile.name?.split(' ')[0] || 'Worker'} 👋
        </h2>
        <p style={{ color: '#64748b', fontSize: '0.875rem', marginTop: '0.2rem' }}>
          {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'short' })}
          &nbsp;·&nbsp;<span style={{ color: '#22c55e' }}>{profile.platform}</span>
        </p>
      </div>

      {/* KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '0.75rem' }}>
        {[
          { label: 'Weekly Premium', value: `₹${premiumInfo.weekly_premium}`, sub: `${premiumInfo.plan} Plan`, color: '#4ade80', icon: <IndianRupee size={18} />, bg: 'rgba(34,197,94,0.1)', border: '#22c55e' },
          { label: 'Remaining Cap', value: `₹${remainingCap}`, sub: `of ₹${weeklyCap} total`, color: '#60a5fa', icon: <TrendingUp size={18} />, bg: 'rgba(96,165,250,0.1)', border: '#60a5fa' },
          { label: 'Trust Score', value: `${(trustScore * 100).toFixed(0)}`, sub: 'Low fraud risk', color: riskColor, icon: <ShieldCheck size={18} />, bg: 'rgba(74,222,128,0.08)', border: riskColor },
          { label: 'Total Paid', value: `₹${claims.filter(c => c.status === 'approved_paid' || c.status === 'PAID').reduce((sum, c) => sum + (c.amount || 0), 0)}`, sub: 'All time', color: '#f59e0b', icon: <IndianRupee size={18} />, bg: 'rgba(245,158,11,0.1)', border: '#f59e0b' },
        ].map((s, i) => (
          <div key={i} className="glass stat-card" style={{ borderTop: `3px solid ${s.border}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div className="stat-label">{s.label}</div>
                <div className="stat-value" style={{ color: s.color }}>{s.value}</div>
                <div className="stat-sub">{s.sub}</div>
              </div>
              <div style={{ padding: '0.4rem', background: s.bg, borderRadius: '0.5rem' }}>
                <span style={{ color: s.color }}>{s.icon}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Live Conditions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '1rem' }}>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontWeight: 700, color: '#f1f5f9', fontSize: '0.9rem' }}>Live Conditions</h3>
            <span className="badge badge-green">HSR Layout</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.78rem' }}><CloudRain size={13} /> Rainfall</div>
                <span style={{ fontSize: '0.78rem', color: rainfall > 20 ? '#f87171' : '#4ade80', fontWeight: 700 }}>{rainfall}mm</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${Math.min(100, (rainfall / 20) * 100)}%` }} />
              </div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#94a3b8', fontSize: '0.78rem' }}><Wind size={13} /> AQI</div>
                <span style={{ fontSize: '0.78rem', color: '#facc15', fontWeight: 700 }}>{aqi} / 300</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${Math.min(100, (aqi / 300) * 100)}%`, background: '#f59e0b' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Payouts */}
      <div className="glass">
        <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid rgba(51,65,85,0.4)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontWeight: 700, color: '#f1f5f9', fontSize: '0.9rem' }}>Recent Payouts</h3>
          <span className="badge badge-green">{claims.length} activities</span>
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Event</th>
                <th>Payout</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {claims.map((row, i) => (
                <tr key={i}>
                  <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{row.created_at ? new Date(row.created_at).toLocaleDateString() : 'Today'}</td>
                  <td>{row.event || 'Parametric Trigger'}</td>
                  <td style={{ fontWeight: 700, color: '#f1f5f9' }}>₹{row.amount || 0}</td>
                  <td>
                    <span className={`badge ${row.status === 'approved_paid' || row.status === 'PAID' ? 'badge-green' : 'badge-red'}`}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
              {claims.length === 0 && (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>No recent claims found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
