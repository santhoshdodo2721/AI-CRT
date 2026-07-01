import React, { useState, useEffect } from 'react';
import { Target, AlertTriangle, Shield, Grid, Activity } from 'lucide-react';
import { api } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get('/dashboard/stats');
        setStats(res.data);
      } catch (err) {
        console.error("Failed to load dashboard stats", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return <div className="p-8"><div className="loading-spinner"></div></div>;
  }

  const severityData = stats ? [
    { name: 'Critical', count: stats.findings.severity.critical || 0, color: '#f87171' },
    { name: 'High', count: stats.findings.severity.high || 0, color: '#fbbf24' },
    { name: 'Medium', count: stats.findings.severity.medium || 0, color: '#facc15' },
    { name: 'Low', count: stats.findings.severity.low || 0, color: '#38bdf8' },
  ] : [];

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Command Center</h1>
        <p className="text-gray-400">High-level overview of autonomous operations.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-panel flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium text-sm uppercase tracking-wider">Total Campaigns</h3>
            <Target className="text-purple-400" size={20} />
          </div>
          <div className="text-4xl font-bold text-white">{stats?.campaigns.total || 0}</div>
        </div>

        <div className="glass-panel flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium text-sm uppercase tracking-wider">Active Engagements</h3>
            <Activity className="text-blue-400" size={20} />
          </div>
          <div className="text-4xl font-bold text-white">{stats?.campaigns.active || 0}</div>
        </div>

        <div className="glass-panel flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium text-sm uppercase tracking-wider">Global Findings</h3>
            <AlertTriangle className="text-red-400" size={20} />
          </div>
          <div className="text-4xl font-bold text-white">{stats?.findings.total || 0}</div>
        </div>

        <div className="glass-panel flex flex-col justify-between">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-gray-400 font-medium text-sm uppercase tracking-wider">Top MITRE Tech</h3>
            <Grid className="text-green-400" size={20} />
          </div>
          <div className="text-xl font-bold text-white truncate">
            {stats?.top_mitre?.[0]?.id || 'None'}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="glass-panel h-96 flex flex-col">
          <h3 className="text-lg font-bold text-white mb-6">Findings by Severity</h3>
          <div className="flex-1">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={severityData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: '#12141c', borderColor: '#333', borderRadius: '8px' }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel h-96 flex flex-col">
          <h3 className="text-lg font-bold text-white mb-6">Top MITRE Techniques</h3>
          <div className="flex-1 overflow-y-auto custom-scrollbar">
             {stats?.top_mitre && stats.top_mitre.length > 0 ? (
               <div className="space-y-4">
                 {stats.top_mitre.map((m, i) => (
                    <div key={i} className="bg-black/30 p-4 rounded-lg border border-white/5 flex justify-between items-center">
                      <span className="font-mono text-purple-400 font-bold">{m.id}</span>
                      <span className="bg-purple-900/40 text-purple-300 px-3 py-1 rounded-full text-xs font-bold">{m.count} detections</span>
                    </div>
                 ))}
               </div>
             ) : (
               <div className="empty-state">No MITRE techniques mapped yet.</div>
             )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
