import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Target, Play, Plus, X, Trash2 } from 'lucide-react';

const Campaigns = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  // Form State
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [description, setDescription] = useState('');

  useEffect(() => {
    fetchCampaigns();
  }, []);

  const fetchCampaigns = async () => {
    try {
      const res = await api.get('/campaigns');
      setCampaigns(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      const res = await api.post('/campaigns', {
        name,
        target,
        description,
        credentials: [],
        scope_config: {},
        ai_enabled: true
      });
      // Automatically start the campaign
      await api.post(`/ai/start-campaign/${res.data.id}`);
      setShowModal(false);
      navigate(`/campaigns/${res.data.id}`);
    } catch (err) {
      console.error(err);
    }
  };

  const startCampaign = async (id) => {
    try {
      await api.post(`/ai/start-campaign/${id}`);
      navigate(`/campaigns/${id}`);
    } catch (err) {
      console.error(err);
    }
  };

  const deleteCampaign = async (id) => {
    if (window.confirm("Are you sure you want to delete this operation?")) {
      try {
        await api.delete(`/campaigns/${id}`);
        fetchCampaigns();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6 relative">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Operations Center</h1>
          <p className="text-gray-400">Manage automated red team campaigns.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-purple-600 hover:bg-purple-500 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors shadow-lg shadow-purple-500/20"
        >
          <Plus size={18} />
          New Campaign
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {campaigns.map(camp => (
          <div key={camp.id} className="glass-panel flex flex-col cursor-pointer hover:border-purple-500/50" onClick={() => navigate(`/campaigns/${camp.id}`)}>
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold text-white">{camp.name}</h3>
              <span className={`px-2 py-1 text-xs uppercase font-bold tracking-wider rounded-md ${
                camp.status === 'running' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                camp.status === 'completed' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                'bg-gray-500/20 text-gray-400 border border-gray-500/30'
              }`}>
                {camp.status}
              </span>
            </div>
            <p className="text-sm text-gray-400 mb-6 flex-1">{camp.description || 'No description provided.'}</p>
            
            <div className="pt-4 border-t border-white/5 flex justify-between items-center mt-auto">
              <div className="text-sm text-gray-300 flex items-center gap-2">
                <Target size={14} className="text-purple-400" />
                {camp.target}
              </div>
              
              <div className="flex gap-2">
                {camp.status === 'created' && (
                  <button 
                    onClick={(e) => { e.stopPropagation(); startCampaign(camp.id); }}
                    className="bg-green-500/20 hover:bg-green-500/30 text-green-400 p-2 rounded-lg transition-colors border border-green-500/30"
                    title="Start Campaign"
                  >
                    <Play size={16} />
                  </button>
                )}
                <button 
                  onClick={(e) => { e.stopPropagation(); deleteCampaign(camp.id); }}
                  className="bg-red-500/20 hover:bg-red-500/30 text-red-400 p-2 rounded-lg transition-colors border border-red-500/30"
                  title="Delete Campaign"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="glass-panel w-full max-w-lg p-6 relative animate-in fade-in zoom-in-95 duration-200">
            <button 
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white"
            >
              <X size={20} />
            </button>
            <h2 className="text-2xl font-bold text-white mb-6">Create Campaign</h2>
            
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Campaign Name</label>
                <input 
                  type="text" 
                  value={name} onChange={(e)=>setName(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-purple-500"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Target Scope (IP/CIDR)</label>
                <input 
                  type="text" 
                  value={target} onChange={(e)=>setTarget(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-purple-500 font-mono"
                  placeholder="e.g. 192.168.1.0/24"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Description</label>
                <textarea 
                  value={description} onChange={(e)=>setDescription(e.target.value)}
                  className="w-full bg-black/50 border border-white/10 rounded-lg py-2.5 px-3 text-white focus:outline-none focus:border-purple-500 h-24 resize-none"
                />
              </div>
              <button 
                type="submit"
                className="w-full bg-purple-600 hover:bg-purple-500 text-white font-medium py-3 rounded-lg shadow-lg mt-4 transition-colors"
              >
                Initialize Operation
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Campaigns;
