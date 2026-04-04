import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import ClaimsPage from './pages/ClaimsPage'
import PolicyPage from './pages/PolicyPage'
import Layout from './components/Layout'

// Mock auth state — replace with Firebase Auth in production
const useAuth = () => {
  const [user] = useState(() => JSON.parse(localStorage.getItem('worker_user') || 'null'))
  return user
}

function ProtectedRoute({ children }) {
  const user = useAuth()
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
          <Route index element={<Dashboard />} />
          <Route path="claims" element={<ClaimsPage />} />
          <Route path="policy" element={<PolicyPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
