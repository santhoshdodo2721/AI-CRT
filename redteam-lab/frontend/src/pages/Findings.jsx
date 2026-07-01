import React, { useState, useEffect } from 'react';
import { AlertTriangle, Filter } from 'lucide-react';
import { api } from '../services/api';

const Findings = () => {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        const res = await api.get('/campaigns/findings/all');
        setFindings(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchFindings();
  }, []);

  const getSeverityStyle = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'high': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'low': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight mb-2">Global Findings</h1>
          <p className="text-gray-400">Aggregated vulnerability database across all campaigns.</p>
        </div>
        <button className="bg-white/5 hover:bg-white/10 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-colors border border-white/10">
          <Filter size={18} />
          Filter
        </button>
      </div>

      <div className="glass-panel overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black/40 border-b border-white/5">
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Severity</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Title</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">MITRE ID</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Campaign</th>
                <th className="px-6 py-4 text-xs font-semibold text-gray-400 uppercase tracking-wider">Discovered</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading ? (
                <tr><td colSpan="5" className="p-8 text-center"><div className="loading-spinner mx-auto"></div></td></tr>
              ) : findings.length === 0 ? (
                <tr><td colSpan="5" className="p-8"><div className="empty-state">No findings recorded yet.</div></td></tr>
              ) : (
                findings.map((f) => (
                  <tr key={f.id} className="hover:bg-white/5 transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2.5 py-1 text-xs uppercase font-bold tracking-wider rounded-md border ${getSeverityStyle(f.severity)}`}>
                        {f.severity}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-white">{f.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {f.mitre_id && f.mitre_id !== 'None' ? (
                        <span className="font-mono text-xs text-purple-400 bg-purple-900/40 px-2 py-1 rounded">{f.mitre_id}</span>
                      ) : (
                        <span className="text-gray-500 text-xs italic">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300 font-mono">
                      {f.campaign_id.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                      {new Date(f.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Findings;
