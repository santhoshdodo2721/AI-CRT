import React, { useEffect, useRef } from 'react';

const AIThoughtStream = ({ messages }) => {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="glass-panel thought-stream-container">
      <h3 className="thought-header">
        <span className="status-dot"></span>
        AI Orchestrator Live Thoughts
      </h3>
      
      <div className="thought-entries">
        {messages.filter(m => m.type === 'ai.thought').length === 0 && (
          <div className="empty-state">Waiting for AI orchestrator to begin reasoning loop...</div>
        )}
        
        {messages.filter(m => m.type === 'ai.thought').map((msg, i) => (
          <div key={i} className="thought-entry">
            <div className="thought-step">Step {msg.step}</div>
            <div className="thought-observation">Observation: {msg.observation}</div>
            <div className="thought-reasoning">Reasoning: {msg.reasoning}</div>
            <div className="thought-action">
              Action: {msg.action} 
              {msg.tool && <span className="thought-tool">[{msg.tool}]</span>}
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
};

export default AIThoughtStream;
