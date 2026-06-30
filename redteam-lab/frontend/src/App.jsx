import React, { useState, useEffect } from 'react';

const API = 'http://localhost:8000/api/lab';

export default function Dashboard() {
  const [tasks, setTasks] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [form, setForm] = useState({ module: 'recon.nmap_scan', target: '10.20.27.201', ports: '8000' });

  const fetchTasks = () => fetch(`${API}/tasks`).then(r => r.json()).then(setTasks).catch(() => {});
  useEffect(() => { fetchTasks(); const i = setInterval(fetchTasks, 2000); return () => clearInterval(i); }, []);

  const createTask = async (e) => {
    e.preventDefault();
    await fetch(`${API}/create`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) });
  };

  const analyze = async (id) => {
    const res = await fetch(`${API}/analyze/${id}`);
    const data = await res.json();
    setAnalysis(data);
  };

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@300;500;700;900&display=swap');
        :root { --neon-cyan: #00f3ff; --neon-purple: #bc13fe; --neon-green: #0aff00; --bg-dark: #050505; --glass: rgba(10, 10, 10, 0.7); }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { background-color: var(--bg-dark); color: #fff; font-family: 'Inter', sans-serif; overflow: hidden; }
        .app-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; background: linear-gradient(var(--bg-dark) 1px, transparent 1px), linear-gradient(90deg, var(--bg-dark) 1px, transparent 1px); background-size: 50px 50px; background-position: center center; background-color: #020202; }
        .app-bg::after { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: radial-gradient(circle at 50% 50%, transparent 0%, var(--bg-dark) 80%); }
        .layout { display: grid; grid-template-columns: 350px 1fr 400px; grid-template-rows: 80px 1fr; height: 100vh; gap: 1px; background-color: #111; }
        .top-bar { grid-column: 1 / -1; background: #0a0a0a; display: flex; align-items: center; justify-content: space-between; padding: 0 30px; border-bottom: 1px solid #222; }
        .logo { font-family: 'JetBrains Mono', monospace; font-weight: 700; font-size: 20px; letter-spacing: 2px; color: var(--neon-cyan); text-shadow: 0 0 10px rgba(0, 243, 255, 0.5); }
        .status-chip { display: flex; align-items: center; gap: 10px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #888; }
        .live-dot { width: 8px; height: 8px; background: var(--neon-green); border-radius: 50%; box-shadow: 0 0 10px var(--neon-green); animation: pulse 2s infinite; }
        .panel { background: var(--glass); backdrop-filter: blur(20px); overflow-y: auto; padding: 25px; }
        .panel::-webkit-scrollbar { width: 4px; } .panel::-webkit-scrollbar-thumb { background: #333; }
        .launcher h2 { font-size: 12px; letter-spacing: 3px; color: #666; margin-bottom: 30px; text-transform: uppercase; }
        .form-group { margin-bottom: 25px; position: relative; }
        .form-group label { position: absolute; top: -8px; left: 10px; background: #111; padding: 0 5px; font-size: 10px; color: var(--neon-cyan); letter-spacing: 1px; text-transform: uppercase; }
        .form-control { width: 100%; background: #0a0a0a; border: 1px solid #333; color: #fff; padding: 15px; font-family: 'JetBrains Mono', monospace; font-size: 14px; outline: none; transition: 0.3s; }
        .form-control:focus { border-color: var(--neon-cyan); box-shadow: 0 0 15px rgba(0, 243, 255, 0.2); }
        .btn-launch { width: 100%; padding: 18px; background: transparent; border: 1px solid var(--neon-purple); color: var(--neon-purple); font-family: 'Inter', sans-serif; font-weight: 700; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; cursor: pointer; position: relative; overflow: hidden; transition: 0.4s; margin-top: 40px; }
        .btn-launch:hover { color: #fff; background: var(--neon-purple); box-shadow: 0 0 30px rgba(188, 19, 254, 0.4); }
        .feed-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 30px; border-bottom: 1px solid #222; padding-bottom: 15px; }
        .feed-title { font-size: 32px; font-weight: 900; line-height: 1; }
        .feed-stats { display: flex; gap: 20px; }
        .stat-box { text-align: right; }
        .stat-num { font-size: 24px; font-weight: 700; color: var(--neon-cyan); }
        .stat-label { font-size: 10px; color: #555; text-transform: uppercase; letter-spacing: 1px; }
        .task-card { background: rgba(20, 20, 20, 0.6); border: 1px solid #222; padding: 20px; margin-bottom: 15px; border-left: 4px solid #333; transition: 0.3s; position: relative; overflow: hidden; }
        .task-card::before { content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03), transparent); transform: translateX(-100%); transition: 0.5s; }
        .task-card:hover::before { transform: translateX(100%); }
        .task-card.status-running { border-left-color: var(--neon-cyan); box-shadow: inset 4px 0 10px -5px var(--neon-cyan); animation: borderPulse 2s infinite; }
        .task-card.status-completed { border-left-color: var(--neon-green); }
        .task-card.status-pending { border-left-color: #666; }
        .tc-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .tc-id { font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #555; }
        .tc-module { font-weight: 700; font-size: 16px; margin-bottom: 5px; text-transform: capitalize; }
        .tc-target { font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #888; }
        .btn-analyze { margin-top: 15px; background: rgba(188, 19, 254, 0.1); border: 1px solid var(--neon-purple); color: var(--neon-purple); padding: 8px 16px; font-size: 11px; font-weight: 700; letter-spacing: 1px; cursor: pointer; text-transform: uppercase; transition: 0.3s; }
        .btn-analyze:hover { background: var(--neon-purple); color: #fff; }
        .terminal-container { height: 100%; display: flex; flex-direction: column; background: #000 !important; border: 1px solid #333; }
        .terminal-top { display: flex; align-items: center; gap: 6px; padding: 12px 15px; background: #111; border-bottom: 1px solid #333; }
        .t-dot { width: 10px; height: 10px; border-radius: 50%; }
        .terminal-body { flex: 1; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 13px; line-height: 1.6; overflow-y: auto; }
        .t-line { margin-bottom: 12px; opacity: 0; animation: fadeIn 0.3s forwards; }
        .t-key { color: #555; margin-right: 10px; }
        .t-cmd { color: #888; }
        .t-success { color: var(--neon-green); }
        .t-warn { color: #ffb800; }
        .t-danger { color: #ff003c; }
        .t-info { color: var(--neon-cyan); }
        .t-cursor::after { content: '\u2588'; color: var(--neon-cyan); animation: blink 1s step-end infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
        @keyframes borderPulse { 0% { box-shadow: inset 4px 0 10px -5px var(--neon-cyan); } 50% { box-shadow: inset 4px 0 20px -5px var(--neon-cyan); } 100% { box-shadow: inset 4px 0 10px -5px var(--neon-cyan); } }
        @keyframes fadeIn { to { opacity: 1; } }
        @keyframes blink { 50% { opacity: 0; } }
      `}</style>

      <div className="app-bg"></div>
      <div className="layout">
        <header className="top-bar">
          <div className="logo">REDTEAM::LAB</div>
          <div className="status-chip">
            <div className="live-dot"></div>
            <span>SYSTEMS NOMINAL</span>
            <span style={{marginLeft: '20px', color: '#444'}}>|</span>
            <span style={{marginLeft: '20px'}}>{new Date().toLocaleTimeString()}</span>
          </div>
        </header>

        <aside className="panel launcher">
          <h2>Attack Vector</h2>
          <form onSubmit={createTask}>
            <div className="form-group">
              <label>Module</label>
              <select className="form-control" value={form.module} onChange={e => setForm({...form, module: e.target.value})}>
                <option value="recon.nmap_scan">recon.nmap_scan</option>
                <option value="vuln_scan.nuclei_scan">vuln.nuclei_scan</option>
                <option value="initial_access.default_creds_check">initial_access.default_creds</option>
                <option value="execution.command_test">execution.command_test</option>
                <option value="persistence.cron_test">persistence.cron_test</option>
                <option value="privilege_escalation.sudo_check">privesc.sudo_check</option>
                <option value="defense_evasion.encoded_command_test">evasion.encoded_cmd</option>
                <option value="credentials.env_secret_scan">cred.secret_scan</option>
                <option value="lateral_movement.network_reachability">lateral.net_reachability</option>
              </select>
            </div>
            <div className="form-group">
              <label>Target Host</label>
              <input className="form-control" type="text" value={form.target} onChange={e => setForm({...form, target: e.target.value})} required />
            </div>
            <div className="form-group">
              <label>Parameters</label>
              <input className="form-control" type="text" value={form.ports} onChange={e => setForm({...form, ports: e.target.value})} placeholder="-p 8000" />
            </div>
            <button type="submit" className="btn-launch">Initiate Sequence</button>
          </form>
        </aside>

        <main className="panel">
          <div className="feed-header">
            <div>
              <div className="feed-title">ACTIVE OPERATIONS</div>
              <div style={{fontSize: '12px', color: '#444', marginTop: '5px'}}>REAL-TIME TASK MONITORING</div>
            </div>
            <div className="feed-stats">
              <div className="stat-box">
                <div className="stat-num">{tasks.filter(t => t.status === 'running').length}</div>
                <div className="stat-label">Active</div>
              </div>
              <div className="stat-box">
                <div className="stat-num">{tasks.filter(t => t.status === 'completed').length}</div>
                <div className="stat-label">Closed</div>
              </div>
            </div>
          </div>

          <div>
            {tasks.length === 0 && <div style={{color: '#333', textAlign: 'center', marginTop: '50px', fontFamily: 'JetBrains Mono'}}>AWAITING INSTRUCTIONS...</div>}
            {[...tasks].reverse().map((task, i) => (
              <div key={task.id} className={`task-card status-${task.status}`} style={{animationDelay: `${i * 0.1}s`}}>
                <div className="tc-header">
                  <div className="tc-id">SEQ-{String(task.id).padStart(4, '0')}</div>
                  <div style={{fontSize: 11, letterSpacing: 1, color: task.status === 'running' ? 'var(--neon-cyan)' : task.status === 'completed' ? 'var(--neon-green)' : '#666', textTransform: 'uppercase'}}>{task.status}</div>
                </div>
                <div className="tc-module">{task.module.replace('.', ' / ')}</div>
                <div className="tc-target">TARGET: {task.target} {task.ports ? `| PARAMS: ${task.ports}` : ''}</div>
                {task.status === 'completed' && (
                  <button className="btn-analyze" onClick={() => analyze(task.id)}>Request AI Analysis</button>
                )}
              </div>
            ))}
          </div>
        </main>

        <aside className="panel terminal-container">
          <div className="terminal-top">
            <div className="t-dot" style={{background: '#ff5f56'}}></div>
            <div className="t-dot" style={{background: '#ffbd2e'}}></div>
            <div className="t-dot" style={{background: '#27c93f'}}></div>
            <span style={{marginLeft: '15px', fontFamily: 'JetBrains Mono', fontSize: 12, color: '#555'}}>root@ai-engine:~/analysis</span>
          </div>
          <div className="terminal-body">
            {!analysis ? (
              <div className="t-line t-cmd t-cursor">Waiting for analysis request...</div>
            ) : (
              <>
                <div className="t-line" style={{animationDelay: '0.1s'}}><span className="t-key">[SYS]</span> <span className="t-cmd">Initializing analyzer for {analysis.target}...</span></div>
                {analysis.ai_engine && <div className="t-line" style={{animationDelay: '0.2s'}}><span className="t-key">[ENG]</span> <span className="t-info">Engine: {analysis.ai_engine}</span></div>}
                {analysis.error && <div className="t-line" style={{animationDelay: '0.25s'}}><span className="t-key">[ERR]</span> <span className="t-danger">{analysis.error}</span></div>}
                <div className="t-line" style={{animationDelay: '0.3s'}}><span className="t-key">[OUT]</span> <span className="t-success">{analysis.summary}</span></div>
                <div className="t-line" style={{animationDelay: '0.5s'}}><span className="t-key">[RISK]</span> <span className={analysis.risk_level === 'Low' || analysis.risk_level === 'Info' ? 't-success' : 't-danger'}>Threat Level: {analysis.risk_level.toUpperCase()}</span></div>
                {analysis.findings?.length > 0 && (
                  <div className="t-line" style={{animationDelay: '0.7s'}}>
                    <span className="t-key">[FND]</span>
                    <div style={{marginLeft: '60px', color: '#ddd'}}>{analysis.findings.map((f, i) => <div key={i}>- {f}</div>)}</div>
                  </div>
                )}
                {analysis.mitre_techniques?.length > 0 && (
                  <div className="t-line" style={{animationDelay: '0.9s'}}>
                    <span className="t-key">[MITRE]</span>
                    <div style={{marginLeft: '60px', color: 'var(--neon-cyan)'}}>{analysis.mitre_techniques.map((m, i) => <div key={i}>&#10140; {m.id} ({m.name})</div>)}</div>
                  </div>
                )}
                {analysis.next_steps?.length > 0 && (
                  <div className="t-line" style={{animationDelay: '1.1s'}}>
                    <span className="t-key">[NXT]</span>
                    <div style={{marginLeft: '60px', color: 'var(--neon-purple)'}}>{analysis.next_steps.map((s, i) => <div key={i}>&#10148; {s}</div>)}</div>
                  </div>
                )}
                <div className="t-line t-cmd t-cursor" style={{animationDelay: '1.3s'}}>Analysis complete.</div>
              </>
            )}
          </div>
        </aside>
      </div>
    </>
  );
}
