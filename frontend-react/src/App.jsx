import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom'
import { Moon, Sun, Shield, Menu } from 'lucide-react'

import AuthPage from './pages/AuthPage'
import WorkerDashboard from './pages/WorkerDashboard'
import AdminDashboard from './pages/AdminDashboard'

function Layout({ children }) {
  const [darkMode, setDarkMode] = useState(false)

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <nav className="bg-white/80 dark:bg-darkCard/80 backdrop-blur-md sticky top-0 z-50 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <Link to="/" className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-primary-500" />
              <span className="font-bold text-xl tracking-tight">Parametric<span className="text-primary-500">Guard</span></span>
            </Link>
            
            <div className="flex items-center space-x-4">
              <Link to="/auth" className="text-gray-500 hover:text-gray-900 dark:text-gray-300 dark:hover:text-white font-medium">Login</Link>
              <button 
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition shadow-sm border border-gray-200 dark:border-gray-700"
              >
                {darkMode ? <Sun className="h-5 w-5 text-yellow-400"/> : <Moon className="h-5 w-5 text-gray-500" />}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        {children}
      </main>
    </div>
  )
}

function Home() {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <h1 className="text-5xl font-extrabold pb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary-500 to-teal-400">
        AI Parametric Insurance for Gig Workers
      </h1>
      <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mb-8">
        Protect your earnings automatically against unpredictable disruptions like extreme weather, completely driven by smart triggers.
      </p>
      <div className="flex space-x-4">
        <Link to="/worker" className="btn-primary">Worker Dashboard</Link>
        <Link to="/admin" className="px-4 py-2 border-2 border-primary-500 text-primary-600 dark:text-primary-400 font-semibold rounded-lg hover:bg-primary-50 dark:hover:bg-primary-900/30 transition shadow-sm">
          Admin Panel
        </Link>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/worker" element={<WorkerDashboard />} />
          <Route path="/admin" element={<AdminDashboard />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
