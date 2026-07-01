import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Monitor, Server, Cpu, Clock } from 'lucide-react';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAgents = async () => {
      try {
        const res = await api.get('/agents');
        setAgents(res.data);
      } catch (err) {
        console.error("Failed to load agents", err);
      } finally {
        setLoading(false);
      }
    };
    fetchAgents();
    
    const interval = setInterval(fetchAgents, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Agents Fleet</h1>
        <p className="text-gray-400">Manage and monitor connected execution agents.</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {loading && agents.length === 0 ? (
          <div className="p-8"><div className="loading-spinner"></div></div>
        ) : agents.length === 0 ? (
          <div className="glass-panel empty-state">No agents connected. Start an agent binary to register.</div>
        ) : (
          agents.map(agent => (
            <div key={agent.id} className="glass-panel flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center shadow-lg ${
                  agent.status === 'online' || agent.status === 'running' 
                    ? 'bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 text-green-400'
                    : 'bg-gradient-to-br from-gray-500/20 to-gray-600/20 border border-gray-500/30 text-gray-400'
                }`}>
                  <Server size={24} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    {agent.name}
                    <span className={`px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded-full ${
                      agent.status === 'running' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                      agent.status === 'online' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                      'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                    }`}>
                      {agent.status}
                    </span>
                  </h3>
                  <div className="text-sm text-gray-400 flex items-center gap-3 mt-1">
                    <span className="flex items-center gap-1"><Monitor size={14}/> {agent.hostname}</span>
                    <span className="flex items-center gap-1"><Cpu size={14}/> {agent.ip_address}</span>
                  </div>
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Last Heartbeat</div>
                <div className="text-sm text-gray-300 flex items-center gap-1 justify-end">
                  <Clock size={14} className="text-purple-400"/>
                  {new Date(agent.last_seen).toLocaleString()}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Agents;
