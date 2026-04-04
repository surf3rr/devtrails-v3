import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [authed, setAuthed] = useState(false);
  const [dark, setDark] = useState(true);

  return (
    <div className={dark ? 'dark' : ''}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={authed
            ? <Navigate to="/dashboard" replace />
            : <Login onLogin={() => setAuthed(true)} dark={dark} />}
          />
          <Route path="/dashboard" element={authed
            ? <Dashboard dark={dark} setDark={setDark} onLogout={() => setAuthed(false)} />
            : <Navigate to="/" replace />}
          />
        </Routes>
      </BrowserRouter>
    </div>
  );
}
