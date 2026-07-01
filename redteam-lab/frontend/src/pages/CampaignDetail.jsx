import React, { useState, useEffect } from 'react';
import { api, useCampaignWebsocket } from '../services/api';
import AIThoughtStream from '../components/AIThoughtStream';
import { useParams } from 'react-router-dom';

const CampaignDetail = () => {
  const { id: campaignId } = useParams();
  const [memory, setMemory] = useState(null);
  const [hosts, setHosts] = useState([]);
  const [pastThoughts, setPastThoughts] = useState([]);
  const [activeTab, setActiveTab] = useState('thoughts');
  const wsMessages = useCampaignWebsocket(campaignId);

  useEffect(() => {
    const fetchDetails = async () => {
      try {
        const memRes = await api.get(`/dashboard/campaign/${campaignId}/memory`);
        setMemory(memRes.data.memory);
        setHosts(memRes.data.hosts || []);
        
        const thoughtsRes = await api.get(`/ai/thoughts/${campaignId}`);
        setPastThoughts(thoughtsRes.data.decisions.reverse());
      } catch (e) {
        console.error("Failed to fetch campaign details", e);
      }
    };
    fetchDetails();
  }, [campaignId]);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="glass-panel flex justify-between items-center bg-gradient-to-r from-gray-900 to-black border-l-4" style={{borderLeftColor: 'var(--text-purple)'}}>
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight mb-1">Campaign Monitor</h1>
          <p className="text-sm text-gray-400 uppercase tracking-wider">Target: {memory?.target || 'Loading...'}</p>
        </div>
        <div className="text-right">
          <div className="text-xs text-gray-500 uppercase tracking-wider mb-1">Current Phase</div>
          <div className="text-2xl font-bold text-purple-400" style={{textShadow: '0 0 15px rgba(192, 132, 252, 0.4)'}}>
            {memory?.phase || 'INITIALIZING'}
          </div>
        </div>
      </div>
      
      {/* Tabs */}
      <div className="flex border-b border-white/10 gap-6">
        <button 
          onClick={() => setActiveTab('thoughts')}
          className={`pb-3 font-medium text-sm uppercase tracking-wider transition-colors ${activeTab === 'thoughts' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-500 hover:text-white'}`}
        >
          Live Thoughts
        </button>
        <button 
          onClick={() => setActiveTab('hosts')}
          className={`pb-3 font-medium text-sm uppercase tracking-wider transition-colors ${activeTab === 'hosts' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-500 hover:text-white'}`}
        >
          Discovered Hosts
        </button>
        <button 
          onClick={() => setActiveTab('findings')}
          className={`pb-3 font-medium text-sm uppercase tracking-wider transition-colors ${activeTab === 'findings' ? 'text-purple-400 border-b-2 border-purple-400' : 'text-gray-500 hover:text-white'}`}
        >
          Findings
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {activeTab === 'thoughts' && (
          <AIThoughtStream messages={[...pastThoughts, ...wsMessages]} />
        )}
        
        {activeTab === 'hosts' && (
          <div className="glass-panel">
            {hosts.length === 0 ? (
               <div className="empty-state">Waiting for reconnaissance data...</div>
            ) : (
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {hosts.map((host, i) => (
                    <div key={i} className="bg-black/40 border border-white/5 p-4 rounded-lg">
                      <div className="text-xl font-bold text-white mb-2">{host.ip}</div>
                      <div className="text-sm text-gray-400">
                        <span className="font-semibold text-gray-300">Open Ports:</span> {(host.open_ports || []).join(', ') || 'Scanning...'}
                      </div>
                    </div>
                 ))}
               </div>
            )}
          </div>
        )}

        {activeTab === 'findings' && (
           <div className="glass-panel empty-state">See Global Findings tab for aggregated data.</div>
        )}
      </div>
    </div>
  );
};

export default CampaignDetail;
