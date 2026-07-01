import React, { useState, useEffect } from 'react';
import { Grid, HelpCircle, Activity } from 'lucide-react';
import { api } from '../services/api';

const MITRE_MATRIX = [
  {
    tactic: "Recon",
    id: "TA0043",
    techniques: [
      { id: "T1595", name: "Active Scanning" },
      { id: "T1592", name: "Gather Host Info" }
    ]
  },
  {
    tactic: "Initial Access",
    id: "TA0001",
    techniques: [
      { id: "T1078", name: "Valid Accounts" },
      { id: "T1190", name: "Exploit Web App" },
      { id: "T1566", name: "Phishing" }
    ]
  },
  {
    tactic: "Execution",
    id: "TA0002",
    techniques: [
      { id: "T1059", name: "Command/Scripting" },
      { id: "T1204", name: "User Execution" }
    ]
  },
  {
    tactic: "Persistence",
    id: "TA0003",
    techniques: [
      { id: "T1053", name: "Scheduled Task" },
      { id: "T1136", name: "Create Account" },
      { id: "T1098", name: "Account Admin" }
    ]
  },
  {
    tactic: "PrivEsc",
    id: "TA0004",
    techniques: [
      { id: "T1548", name: "Abuse Elevation" },
      { id: "T1068", name: "Exploit for PrivEsc" }
    ]
  },
  {
    tactic: "Evasion",
    id: "TA0005",
    techniques: [
      { id: "T1562", name: "Impair Defenses" },
      { id: "T1027", name: "Obfuscated Files" }
    ]
  },
  {
    tactic: "Cred Access",
    id: "TA0006",
    techniques: [
      { id: "T1552", name: "Unsecured Creds" },
      { id: "T1110", name: "Brute Force" }
    ]
  },
  {
    tactic: "Discovery",
    id: "TA0007",
    techniques: [
      { id: "T1046", name: "Service Discovery" },
      { id: "T1018", name: "System Discovery" },
      { id: "T1082", name: "System Info" }
    ]
  },
  {
    tactic: "Lateral Move",
    id: "TA0008",
    techniques: [
      { id: "T1021", name: "Remote Services" }
    ]
  },
  {
    tactic: "Exfiltration",
    id: "TA0010",
    techniques: [
      { id: "T1048", name: "Exfil Over Alt Port" }
    ]
  },
  {
    tactic: "Impact",
    id: "TA0040",
    techniques: [
      { id: "T1486", name: "Data Encrypted" },
      { id: "T1496", name: "Resource Hijack" }
    ]
  }
];

const MitreMap = () => {
  const [detections, setDetections] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMitre = async () => {
      try {
        const res = await api.get('/dashboard/stats');
        const lookup = {};
        (res.data.top_mitre || []).forEach(m => {
          const baseId = m.id.split('.')[0];
          lookup[baseId] = (lookup[baseId] || 0) + m.count;
        });
        setDetections(lookup);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchMitre();
  }, []);

  return (
    <div className="p-8 max-w-[1600px] mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center shadow-[0_0_15px_rgba(52,211,153,0.4)]">
          <Grid size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">MITRE ATT&CK® Enterprise Matrix</h1>
          <p className="text-gray-400 text-sm">Real-time heatmap of modular cyber range threat simulations.</p>
        </div>
      </div>

      <div className="glass-panel overflow-x-auto p-6 border border-white/10 bg-[#0c0d14]/90 backdrop-blur-xl rounded-2xl shadow-2xl">
        {loading ? (
          <div className="flex justify-center my-20">
            <div className="loading-spinner" />
          </div>
        ) : (
          <div className="flex gap-3 min-w-[1250px] select-none">
            {MITRE_MATRIX.map((col, idx) => (
              <div key={idx} className="flex-1 flex flex-col gap-3 min-w-[115px]">
                {/* Tactic Header */}
                <div className="bg-[#161824] border border-white/10 rounded-xl p-3 text-center shadow-md relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-green-500 to-emerald-400" />
                  <div className="text-[10px] text-gray-500 font-mono font-semibold mb-0.5">{col.id}</div>
                  <div className="text-xs font-bold text-gray-200 tracking-wide truncate" title={col.tactic}>
                    {col.tactic}
                  </div>
                </div>

                {/* Techniques List */}
                <div className="flex flex-col gap-2">
                  {col.techniques.map((tech, tIdx) => {
                    const count = detections[tech.id] || 0;
                    const isActive = count > 0;
                    return (
                      <div 
                        key={tIdx} 
                        className={`border rounded-xl p-3.5 text-left transition-all duration-300 relative flex flex-col justify-between min-h-[90px] ${
                          isActive 
                            ? 'bg-gradient-to-br from-green-500/15 to-green-600/5 border-green-500/40 shadow-[0_4px_20px_rgba(34,197,94,0.12)] hover:border-green-400/60 scale-[1.02]' 
                            : 'bg-[#10111a]/40 border-white/5 opacity-40 hover:opacity-60'
                        }`}
                      >
                        <div>
                          <div className="flex justify-between items-start mb-1.5">
                            <span className={`text-[9px] font-mono font-bold tracking-wider ${isActive ? 'text-green-400' : 'text-gray-500'}`}>
                              {tech.id}
                            </span>
                            {isActive && (
                              <span className="flex h-2 w-2 relative">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                              </span>
                            )}
                          </div>
                          <div className={`text-xs font-bold leading-snug tracking-tight ${isActive ? 'text-green-100' : 'text-gray-400'}`}>
                            {tech.name}
                          </div>
                        </div>

                        {isActive && (
                          <div className="mt-3 pt-2 border-t border-green-500/10 flex items-center justify-between">
                            <span className="text-[9px] text-green-500/70 font-mono font-bold uppercase tracking-wider">Detected</span>
                            <span className="bg-green-500/20 text-green-300 text-[10px] font-bold px-2 py-0.5 rounded-md border border-green-500/20">
                              {count}
                            </span>
                          </div>
                        )}
                      </div>
                    );
                  })}
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
