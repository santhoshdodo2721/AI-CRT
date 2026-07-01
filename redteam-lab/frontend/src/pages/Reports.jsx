import React, { useState, useEffect } from 'react';
import { FileText, Download, Target } from 'lucide-react';
import { api } from '../services/api';

const Reports = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const res = await api.get('/campaigns');
        setCampaigns(res.data.filter(c => c.status === 'completed' || c.status === 'running'));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchCampaigns();
  }, []);

  const handleDownload = async (id, name) => {
    try {
      // Trigger the backend to generate the final report
      // Currently, it's just a JSON endpoint, but we can format it on the frontend or wait for a PDF endpoint
      const res = await api.get(`/reports/${id}`);
      
      const element = document.createElement("a");
      const file = new Blob([JSON.stringify(res.data, null, 2)], {type: 'application/json'});
      element.href = URL.createObjectURL(file);
      element.download = `report_${name}_${id}.json`;
      document.body.appendChild(element); // Required for this to work in FireFox
      element.click();
    } catch (err) {
      console.error("Download failed", err);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-6">
      <div className="mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shadow-[0_0_15px_rgba(192,132,252,0.5)]">
          <FileText size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Generated Reports</h1>
          <p className="text-gray-400 text-sm">Download executive and technical summaries.</p>
        </div>
      </div>

      <div className="space-y-4">
        {loading ? (
          <div className="p-8 text-center"><div className="loading-spinner mx-auto"></div></div>
        ) : campaigns.length === 0 ? (
          <div className="glass-panel empty-state">No completed reports available.</div>
        ) : (
          campaigns.map(camp => (
            <div key={camp.id} className="glass-panel flex justify-between items-center hover:border-purple-500/30 transition-colors">
              <div>
                <h3 className="text-lg font-bold text-white mb-1">{camp.name}</h3>
                <div className="text-sm text-gray-400 flex items-center gap-2">
                  <Target size={14} className="text-purple-400"/> {camp.target}
                  <span className="text-gray-600">|</span>
                  <span>ID: {camp.id}</span>
                </div>
              </div>
              <button 
                onClick={() => handleDownload(camp.id, camp.name)}
                className="bg-white/5 hover:bg-white/10 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors border border-white/10"
              >
                <Download size={18} />
                Download JSON
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Reports;
