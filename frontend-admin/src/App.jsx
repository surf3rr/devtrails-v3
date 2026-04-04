import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import AdminLogin from './pages/AdminLogin'
import AnalyticsDashboard from './pages/AnalyticsDashboard'
import ClaimsManager from './pages/ClaimsManager'
import FraudMonitor from './pages/FraudMonitor'
import ZoneRisk from './pages/ZoneRisk'
import AdminLayout from './components/AdminLayout'

function ProtectedRoute({ children }) {
  const admin = JSON.parse(localStorage.getItem('admin_user') || 'null')
  return admin ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<AdminLogin />} />
        <Route path="/" element={<ProtectedRoute><AdminLayout /></ProtectedRoute>}>
          <Route index element={<AnalyticsDashboard />} />
          <Route path="claims" element={<ClaimsManager />} />
          <Route path="fraud" element={<FraudMonitor />} />
          <Route path="zones" element={<ZoneRisk />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
