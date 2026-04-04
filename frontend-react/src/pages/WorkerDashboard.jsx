import { useState, useEffect } from 'react';
import { CloudRain, ShieldCheck, Activity, AlertTriangle, ArrowRight, Zap } from 'lucide-react';

export default function WorkerDashboard() {
  const [loading, setLoading] = useState(false);
  const [claims, setClaims] = useState([
    { id: 'clm_01', date: 'Oct 12, 2026', amount: '₹2,000', status: 'PAID', event: 'Heavy Rain (>25mm)' },
    { id: 'clm_00', date: 'Sep 05, 2026', amount: '₹1,500', status: 'PAID', event: 'AQI > 350' }
  ]);
  const [simulating, setSimulating] = useState(false);

  const simulateRainEvent = async () => {
    setSimulating(true);
    // Mimic API logic
    setTimeout(() => {
      setClaims([
        { id: 'clm_02', date: 'Today', amount: '₹2,000', status: 'PENDING', event: 'Trigger Simulation' },
        ...claims
      ]);
      setSimulating(false);
      setTimeout(() => {
        setClaims(prev => [
          { ...prev[0], status: 'PAID' },
          ...prev.slice(1)
        ]);
        alert("Parametric trigger verified. Instant payout completed via Wallet/UPI.");
      }, 2000);
    }, 1500);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-500">Welcome back, John! Your earnings are protected.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Coverage Card */}
        <div className="glass-card p-6 flex flex-col justify-between">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-sm text-gray-500 font-medium">Active Coverage</p>
              <h3 className="text-2xl font-bold mt-1 text-primary-600">Dynamic Policy</h3>
            </div>
            <ShieldCheck className="w-8 h-8 text-primary-500" />
          </div>
          <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
            <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-1 rounded-full">Good Risk Tier</span>
            <p className="text-sm mt-3"><span className="font-semibold">Premium:</span> ₹20/week</p>
            <p className="text-sm"><span className="font-semibold">Max Payout:</span> ₹2,000/event</p>
          </div>
        </div>

        {/* Dynamic Trigger Stats */}
        <div className="glass-card p-6 flex flex-col justify-between col-span-1 md:col-span-2 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <CloudRain className="w-32 h-32" />
          </div>
          <div>
            <p className="text-sm text-gray-500 font-medium">Real-time Triggers</p>
            <h3 className="text-xl font-bold mt-1">Bangalore HSR Layout</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mt-6 z-10">
            <div>
              <p className="text-sm text-gray-500">Current Rainfall</p>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-blue-500">2.4 mm</span>
                <span className="text-xs text-gray-400 pb-1">/ threshold 20mm</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-500">Current AQI</p>
              <div className="flex items-end space-x-2">
                <span className="text-3xl font-bold text-yellow-500">145</span>
                <span className="text-xs text-gray-400 pb-1">/ threshold 300</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Demo Action Area */}
      <div className="glass-card p-6 border-l-4 border-primary-500">
        <div className="flex flex-col md:flex-row justify-between items-center bg-gray-50 dark:bg-gray-800/50 p-4 rounded-lg">
          <div>
            <h4 className="font-bold flex items-center"><Zap className="w-5 h-5 text-yellow-500 mr-2" /> Parametric Simulation</h4>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">Simulate a disruption event hitting the threshold to bypass normal waiting times. Watch automated claims execute instantly.</p>
          </div>
          <button 
            onClick={simulateRainEvent}
            disabled={simulating}
            className="mt-4 md:mt-0 w-full md:w-auto btn-primary bg-indigo-600 hover:bg-indigo-700 whitespace-nowrap"
          >
            {simulating ? "Scanning sensors..." : "Simulate Heavy Rain"}
          </button>
        </div>
      </div>

      {/* Claims History */}
      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-gray-100 dark:border-gray-700 font-bold text-lg flex justify-between items-center">
          Claims History
          <Activity className="w-5 h-5 text-gray-400" />
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800/50 text-gray-500">
              <tr>
                <th className="px-6 py-3 font-medium">Claim ID</th>
                <th className="px-6 py-3 font-medium">Date</th>
                <th className="px-6 py-3 font-medium">Trigger Event</th>
                <th className="px-6 py-3 font-medium">Payout</th>
                <th className="px-6 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {claims.map((claim, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50 dark:hover:bg-gray-800/30 transition-colors">
                  <td className="px-6 py-4 font-mono text-xs">{claim.id}</td>
                  <td className="px-6 py-4">{claim.date}</td>
                  <td className="px-6 py-4 text-gray-600 dark:text-gray-300">{claim.event}</td>
                  <td className="px-6 py-4 font-semibold">{claim.amount}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      claim.status === 'PAID' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                      'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
                    }`}>
                      {claim.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
