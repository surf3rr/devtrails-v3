import { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { onAuthStateChanged } from 'firebase/auth'
import { auth } from './firebaseConfig'
import { onSnapshot, doc } from 'firebase/firestore'
import { db } from './firebaseConfig'

import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ClaimsPage from './pages/ClaimsPage'
import PolicyPage from './pages/PolicyPage'
import VerificationPage from './pages/VerificationPage'
import Layout from './components/Layout'

function ProtectedRoute({ children, user, loading }) {
  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', background: '#0f172a', color: '#64748b', fontSize: '0.9rem'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: 30, height: 30, border: '3px solid #1e293b', borderTop: '3px solid #22c55e', borderRadius: '50%', animation: 'spin 1s linear infinite' }} />
          Authenticating...
        </div>
      </div>
    )
  }
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  const [firebaseUser, setFirebaseUser] = useState(null)
  const [profile, setProfile] = useState(null)
  const [authLoading, setAuthLoading] = useState(true)

  useEffect(() => {
    // 1. Listen to Firebase Auth state
    const unsubscribeAuth = onAuthStateChanged(auth, (user) => {
      setFirebaseUser(user)
      if (!user) {
        setProfile(null)
        setAuthLoading(false)
      }
    })
    return () => unsubscribeAuth()
  }, [])

  useEffect(() => {
    // 2. Listen to Firestore Profile state if authenticated
    if (!firebaseUser) return

    const unsubscribeProfile = onSnapshot(doc(db, 'users', firebaseUser.uid), 
      (snap) => {
        if (snap.exists()) {
          setProfile(snap.data())
        }
        setAuthLoading(false)
      },
      () => setAuthLoading(false)
    )

    return () => unsubscribeProfile()
  }, [firebaseUser])

  const isLoading = authLoading && !profile

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute user={firebaseUser} loading={isLoading}>
              <Layout user={firebaseUser} profile={profile} />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard user={firebaseUser} profile={profile} />} />
          <Route path="claims" element={<ClaimsPage user={firebaseUser} profile={profile} />} />
          <Route path="policy" element={<PolicyPage user={firebaseUser} profile={profile} />} />
          <Route path="verify" element={<VerificationPage user={firebaseUser} profile={profile} />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
