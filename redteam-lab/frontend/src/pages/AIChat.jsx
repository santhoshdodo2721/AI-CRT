import React, { useState, useEffect, useRef } from 'react';
import { Bot, User, Send, BrainCircuit } from 'lucide-react';
import { api } from '../services/api';

const AIChat = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Greetings, Operator. I am the AI Orchestrator. You can ask me about ongoing campaigns, specific hosts, or request analysis on discovered vulnerabilities. How can I assist you?' }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await api.post('/ai/ask', {
        question: userMsg,
        context: "You are an AI red team assistant conversing directly with the human operator."
      });
      setMessages(prev => [...prev, { role: 'assistant', text: res.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error connecting to the intelligence core.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto h-full flex flex-col">
      <div className="mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center shadow-[0_0_15px_rgba(192,132,252,0.5)]">
          <BrainCircuit size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">AI Intelligence Interface</h1>
          <p className="text-gray-400 text-sm">Direct link to the orchestration brain.</p>
        </div>
      </div>

      <div className="glass-panel flex-1 flex flex-col p-0 overflow-hidden border border-white/10" style={{ height: 'calc(100vh - 200px)' }}>
        <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                msg.role === 'user' ? 'bg-blue-600' : 'bg-purple-600'
              }`}>
                {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-white" />}
              </div>
              <div className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                msg.role === 'user' 
                  ? 'bg-blue-600/20 border border-blue-500/30 text-blue-100 rounded-tr-none'
                  : 'bg-white/5 border border-white/10 text-gray-200 rounded-tl-none leading-relaxed'
              }`}>
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center">
                <Bot size={16} className="text-white" />
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-none px-5 py-4 flex gap-1 items-center">
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        <div className="p-4 bg-black/40 border-t border-white/5">
          <form onSubmit={handleSend} className="relative flex items-center">
            <input 
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask the orchestrator..."
              className="w-full bg-black/60 border border-white/10 rounded-xl py-4 pl-4 pr-14 text-white focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all placeholder-gray-500"
            />
            <button 
              type="submit"
              disabled={loading || !input.trim()}
              className="absolute right-2 p-2 rounded-lg bg-purple-600 text-white hover:bg-purple-500 disabled:opacity-50 transition-colors"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default AIChat;
