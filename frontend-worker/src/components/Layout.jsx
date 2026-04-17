import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { LayoutDashboard, FileText, Shield, LogOut, Bell, Camera } from 'lucide-react'
import { signOut } from 'firebase/auth'
import { auth } from '../firebaseConfig'

const navItems = [
  { to: '/', icon: <LayoutDashboard size={22} />, label: 'Home', end: true },
  { to: '/claims', icon: <FileText size={22} />, label: 'Claims' },
  { to: '/policy', icon: <Shield size={22} />, label: 'Policy' },
  { to: '/verify', icon: <Camera size={22} />, label: 'Verify' },
]

export default function Layout({ user: firebaseUser, profile }) {
  const navigate = useNavigate()
  const location = useLocation()

  const logout = async () => {
    try { await signOut(auth) } catch (e) { console.warn(e) }
    navigate('/login')
  }

  // Display data from live Firestore profile
  const displayName = profile?.name || firebaseUser?.displayName || firebaseUser?.email?.split('@')[0] || 'Worker'
  const platform = profile?.platform || 'Delivery'

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      
      {/* Desktop Sidebar */}
      <aside className="desktop-sidebar" style={{
        width: '240px', flexShrink: 0, padding: '1.5rem 1rem',
        borderRight: '1px solid rgba(51,65,85,0.5)',
        display: 'flex', flexDirection: 'column', gap: '0.5rem',
        background: 'rgba(15,23,42,0.9)', position: 'sticky', top: 0, height: '100vh', overflowY: 'auto'
      }}>
        <div style={{ padding: '0.5rem 1rem', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{ width: 32, height: 32, borderRadius: '8px', background: 'linear-gradient(135deg,#16a34a,#22c55e)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem' }}>🛡️</div>
            <span style={{ fontWeight: 800, fontSize: '1rem', color: '#f1f5f9' }}>
              ParametricGuard
            </span>
          </div>
        </div>

        {/* Live Profile Pill */}
        <div className="glass-light" style={{ padding: '0.75rem 1rem', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg,#16a34a,#22c55e)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.875rem', color: 'white', flexShrink: 0 }}>
            {displayName[0]?.toUpperCase()}
          </div>
          <div style={{ overflow: 'hidden' }}>
            <div style={{ fontWeight: 600, fontSize: '0.8rem', color: '#f1f5f9', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{displayName}</div>
            <div style={{ fontSize: '0.7rem', color: '#22c55e' }}>{platform}</div>
          </div>
        </div>

        {navItems.map(n => (
          <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            {n.icon} {n.label}
          </NavLink>
        ))}

        <div style={{ marginTop: 'auto' }}>
          <button onClick={logout} className="nav-link" style={{ color: '#f87171', width: '100%', textAlign: 'left', background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        <header className="topbar" style={{
          padding: '1rem 1.5rem', borderBottom: '1px solid rgba(51,65,85,0.4)',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          background: 'rgba(15,23,42,0.6)', backdropFilter: 'blur(10px)',
          position: 'sticky', top: 0, zIndex: 50
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div className="pulse-dot" />
            <span style={{ fontSize: '0.72rem', color: '#4ade80', fontWeight: 500 }}>Live Cloud Sync</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button style={{ background: 'none', border: 'none', color: '#94a3b8' }}><Bell size={20} /></button>
          </div>
        </header>

        <main style={{ flex: 1, padding: '1.5rem', overflowY: 'auto' }}>
          <Outlet />
        </main>
      </div>

      {/* Mobile Bottom Nav */}
      <nav className="bottom-nav">
        {navItems.map(n => (
          <NavLink key={n.to} to={n.to} end={n.end} className={({ isActive }) => `bottom-nav-item ${isActive ? 'active' : ''}`}>
            {n.icon}
          </NavLink>
        ))}
        <button onClick={logout} className="bottom-nav-item" style={{ color: '#f87171', border: 'none', background: 'none' }}>
          <LogOut size={22} />
        </button>
      </nav>
    </div>
  )
}
