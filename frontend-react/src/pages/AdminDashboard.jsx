import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Users, AlertTriangle, ShieldAlert, CheckCircle } from 'lucide-react';

const data = [
  { name: 'Mon', claims: 12, fraud: 1 },
  { name: 'Tue', claims: 19, fraud: 2 },
  { name: 'Wed', claims: 3, fraud: 0 },
  { name: 'Thu', claims: 84, fraud: 5 }, // Extreme weather day
  { name: 'Fri', claims: 14, fraud: 1 },
  { name: 'Sat', claims: 5, fraud: 0 },
  { name: 'Sun', claims: 8, fraud: 0 },
];

export default function AdminDashboard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Admin Dashboard</h1>
          <p className="text-gray-500">System overview and fraud monitoring.</p>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="glass-card p-5">
          <div className="flex justify-between text-gray-500 mb-2">
            <span className="text-sm font-medium">Total Active Policies</span>
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold">12,450</p>
        </div>
        
        <div className="glass-card p-5">
          <div className="flex justify-between text-gray-500 mb-2">
            <span className="text-sm font-medium">Claims this Week</span>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </div>
          <p className="text-2xl font-bold">145</p>
        </div>

        <div className="glass-card p-5">
          <div className="flex justify-between text-gray-500 mb-2">
            <span className="text-sm font-medium">Total Payouts</span>
            <CheckCircle className="w-5 h-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold">₹2,90,000</p>
        </div>

        <div className="glass-card p-5 border-l-4 border-red-500">
          <div className="flex justify-between text-gray-500 mb-2">
            <span className="text-sm font-medium">Fraud Detected</span>
            <ShieldAlert className="w-5 h-5 text-red-500" />
          </div>
          <p className="text-2xl font-bold text-red-500">9</p>
          <p className="text-xs text-gray-400 mt-1">₹18,000 saved</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 lg:col-span-2">
          <h3 className="font-bold mb-4">Claims Volume vs Flagged Fraud</h3>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="name" stroke="#888" />
                <YAxis stroke="#888" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Line type="monotone" dataKey="claims" stroke="#22c55e" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 8 }} />
                <Line type="monotone" dataKey="fraud" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-bold mb-4">Risk Zones</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-lg">
              <div>
                <p className="font-semibold text-red-800 dark:text-red-400">Bellandur, BLR</p>
                <p className="text-xs text-red-600 dark:text-red-500">High flood risk</p>
              </div>
              <span className="font-bold text-red-600 dark:text-red-500">Premium: ₹45</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-yellow-50 dark:bg-yellow-900/10 border border-yellow-100 dark:border-yellow-900/30 rounded-lg">
              <div>
                <p className="font-semibold text-yellow-800 dark:text-yellow-400">Indiranagar, BLR</p>
                <p className="text-xs text-yellow-600 dark:text-yellow-500">Medium traffic/AQI</p>
              </div>
              <span className="font-bold text-yellow-600 dark:text-yellow-400">Premium: ₹30</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30 rounded-lg">
              <div>
                <p className="font-semibold text-green-800 dark:text-green-400">Jayanagar, BLR</p>
                <p className="text-xs text-green-600 dark:text-green-500">Low risk</p>
              </div>
              <span className="font-bold text-green-600 dark:text-green-400">Premium: ₹20</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
