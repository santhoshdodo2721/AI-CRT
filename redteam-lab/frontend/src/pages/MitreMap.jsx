import React, { useState, useEffect } from 'react';
import { Grid, Target } from 'lucide-react';
import { api } from '../services/api';

const MitreMap = () => {
  const [topMitre, setTopMitre] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMitre = async () => {
      try {
        const res = await api.get('/dashboard/stats');
        setTopMitre(res.data.top_mitre || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMitre();
  }, []);

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-[0_0_15px_rgba(52,211,153,0.5)]">
          <Grid size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">MITRE ATT&CK Matrix</h1>
          <p className="text-gray-400 text-sm">Heatmap of discovered techniques.</p>
        </div>
      </div>

      <div className="glass-panel min-h-[500px]">
        {loading ? (
          <div className="flex justify-center mt-20"><div className="loading-spinner"></div></div>
        ) : topMitre.length === 0 ? (
          <div className="empty-state mt-20">No MITRE techniques mapped yet.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {topMitre.map((m, i) => (
              <div key={i} className="bg-black/40 border border-green-500/30 p-4 rounded-lg relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-16 h-16 bg-green-500/10 rounded-bl-full -mr-8 -mt-8 transition-transform group-hover:scale-150" />
                <h3 className="text-xl font-mono font-bold text-green-400 mb-2 relative z-10">{m.id}</h3>
                <div className="flex items-center justify-between text-sm text-gray-400 relative z-10">
                  <span>Detections</span>
                  <span className="font-bold text-white bg-green-500/20 px-2 py-0.5 rounded-md">{m.count}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MitreMap;
