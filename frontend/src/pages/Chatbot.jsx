import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Bot,
  User,
  Send,
  RefreshCw,
  Trash2,
  Copy,
  Check,
  Sprout,
  Code2,
  Atom,
  Briefcase,
  ArrowRight,
  BrainCircuit,
  MessageSquare
} from 'lucide-react';
import api from '../api';

const TOPIC_CARDS = [
  {
    icon: Code2,
    title: 'Programming & Tech',
    color: 'from-blue-500 to-indigo-700',
    prompt: 'What is Python and how does it compare to Java? Write a simple example.',
  },
  {
    icon: Atom,
    title: 'Science & Explanations',
    color: 'from-cyan-500 to-teal-700',
    prompt: 'Explain photosynthesis simply: chemical equation, light reactions, and Calvin cycle.',
  },
  {
    icon: Sprout,
    title: 'Crop & Soil Intelligence',
    color: 'from-emerald-500 to-emerald-700',
    prompt: 'What is the best soil for Rice and how should soil pH be managed?',
  },
  {
    icon: Briefcase,
    title: 'Career & Writing Support',
    color: 'from-purple-500 to-purple-700',
    prompt: 'Help me prepare for a technical interview using the STAR method with examples.',
  },
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [copiedIdx, setCopiedIdx] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    fetchChatHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const fetchChatHistory = async () => {
    try {
      setInitialLoading(true);
      const res = await api.get('/chat/history');
      if (res.data && res.data.length > 0) {
        setMessages(res.data);
      } else {
        // Initial welcome message
        setMessages([
          {
            role: 'assistant',
            message: '🌾 **Welcome to AgriSense AI Assistant!**\n\nI am your versatile, intelligent conversational AI. You can ask me anything across:\n- **Programming & Technology**: Python, Java factorial, RAM vs ROM, APIs, SQL, algorithms\n- **Science & Education**: Photosynthesis, physics, mathematics, chemistry, biology\n- **Career & Writing**: Interview preparation, resumes, Instagram captions, summaries\n- **Agricultural Intelligence**: 12 crop guides, soil pH management, N-P-K schedules, and YieldSense ML model specs\n- **Personalized Data**: Your registered farms, crop plantings, and prediction history\n\nSelect a topic above or type your question below!',
            suggestions: [
              'What is Python?',
              'Explain photosynthesis',
              'What is the best soil for rice?',
              'Write a Java program for factorial',
              'Explain the ML prediction model'
            ],
            created_at: new Date().toISOString(),
          },
        ]);
      }
    } catch (err) {
      console.warn('Could not load chat history:', err);
      setMessages([
        {
          role: 'assistant',
          message: '🌾 **Welcome to AgriSense AI!** How can I assist you today?',
          suggestions: ['What is Python?', 'What is the best soil for rice?', 'Explain photosynthesis'],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setInitialLoading(false);
    }
  };

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMessage = {
      role: 'user',
      message: textToSend,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const historyPayload = messages.slice(-6).map((m) => ({
        role: m.role,
        message: m.message,
      }));

      const res = await api.post('/chat', {
        message: textToSend,
        history: historyPayload,
      });

      const botMessage = {
        role: 'assistant',
        message: res.data.reply,
        category: res.data.category,
        suggestions: res.data.suggestions || [],
        created_at: res.data.timestamp || new Date().toISOString(),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          message: '⚠️ Sorry, I encountered an issue connecting to the AI service. Please ensure the backend server is running.',
          suggestions: ['What is Python?', 'What is the best soil for rice?', 'Explain the ML prediction model'],
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to clear your conversation history?')) {
      try {
        await api.delete('/chat/history');
      } catch (err) {
        console.warn('Could not clear server chat history:', err);
      }
      setMessages([
        {
          role: 'assistant',
          message: 'Conversation history cleared. Ask me any question on programming, science, mathematics, career, or agriculture to get started!',
          suggestions: [
            'What is Python?',
            'Explain photosynthesis',
            'What is the best soil for rice?',
            'Write a Java program for factorial'
          ],
          created_at: new Date().toISOString(),
        },
      ]);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="bg-white p-6 md:p-8 rounded-3xl border border-[#e3ecd9] flex flex-col md:flex-row justify-between items-start md:items-center gap-4 shadow-sm relative overflow-hidden">
        <div className="absolute right-0 top-0 w-36 h-36 bg-emerald-50 rounded-full blur-3xl pointer-events-none" />
        <div className="relative">
          <div className="flex items-center gap-2 text-brand-600 font-semibold text-xs uppercase tracking-wider mb-1">
            <Sparkles size={16} />
            <span>YieldSense AI Intelligence Engine</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-slate-800">AgriSense AI Assistant 🤖</h2>
          <p className="text-slate-500 text-sm mt-1">
            General AI assistant for programming, science, mathematics, career, and domain-grounded agricultural forecasting.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleClearHistory}
            className="flex items-center gap-1.5 px-4 py-2 bg-rose-50 hover:bg-rose-100 text-rose-700 rounded-2xl text-xs font-semibold transition-all border border-rose-200 shadow-2xs"
          >
            <Trash2 size={14} />
            <span>Clear History</span>
          </button>
        </div>
      </div>

      {/* Interactive Topic Suggestion Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {TOPIC_CARDS.map((card, i) => {
          const Icon = card.icon;
          return (
            <button
              key={i}
              onClick={() => handleSend(card.prompt)}
              className="bg-white p-5 rounded-3xl border border-[#e3ecd9] hover:border-brand-300 transition-all text-left shadow-2xs group flex flex-col justify-between hover:shadow-md hover:-translate-y-0.5"
            >
              <div>
                <div className={`w-10 h-10 rounded-2xl bg-gradient-to-tr ${card.color} text-white flex items-center justify-center mb-3 shadow-sm`}>
                  <Icon size={20} />
                </div>
                <h4 className="font-bold text-sm text-slate-800 group-hover:text-brand-700 transition-colors">
                  {card.title}
                </h4>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2 leading-relaxed">
                  {card.prompt}
                </p>
              </div>
              <div className="flex items-center gap-1 text-xs font-semibold text-brand-600 mt-3">
                <span>Ask this</span>
                <ArrowRight size={12} className="transform group-hover:translate-x-1 transition-transform" />
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Conversation Container */}
      <div className="bg-white rounded-3xl border border-[#e3ecd9] shadow-sm flex flex-col h-[600px] overflow-hidden">
        {/* Chat Messages Log */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-50/40">
          {initialLoading ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
              <RefreshCw size={24} className="animate-spin text-brand-600" />
              <span className="text-xs">Loading conversation history...</span>
            </div>
          ) : (
            messages.map((msg, idx) => {
              const isUser = msg.role === 'user';
              return (
                <div key={idx} className={`flex gap-3.5 ${isUser ? 'justify-end' : 'justify-start'}`}>
                  {!isUser && (
                    <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-brand-600 to-emerald-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
                      <Bot size={18} />
                    </div>
                  )}

                  <div className="max-w-[85%] sm:max-w-[78%] space-y-2.5">
                    <div
                      className={`p-5 rounded-3xl text-sm leading-relaxed ${
                        isUser
                          ? 'bg-brand-600 text-white rounded-tr-none shadow-sm'
                          : 'bg-white text-slate-800 rounded-tl-none border border-[#e3ecd9] shadow-sm'
                      }`}
                    >
                      <div className="whitespace-pre-wrap font-sans">
                        {msg.message}
                      </div>

                      {!isUser && (
                        <div className="flex items-center justify-between mt-3 pt-2.5 border-t border-slate-100 text-xs text-slate-400">
                          <span className="text-[11px]">
                            {msg.category ? `Category: ${msg.category.replace('_', ' ')}` : 'AgriSense Verified'}
                          </span>
                          <button
                            onClick={() => handleCopy(msg.message, idx)}
                            className="flex items-center gap-1 hover:text-slate-700 transition-colors font-medium text-[11px]"
                          >
                            {copiedIdx === idx ? <Check size={13} className="text-emerald-500" /> : <Copy size={13} />}
                            <span>{copiedIdx === idx ? 'Copied' : 'Copy answer'}</span>
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Interactive suggestions */}
                    {!isUser && msg.suggestions && msg.suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-2 pt-1">
                        {msg.suggestions.map((sug, sIdx) => (
                          <button
                            key={sIdx}
                            onClick={() => handleSend(sug)}
                            className="px-3 py-1.5 bg-white hover:bg-brand-50 border border-[#e3ecd9] hover:border-brand-300 text-brand-800 text-xs font-medium rounded-full transition-all text-left shadow-2xs hover:shadow-sm"
                          >
                            💡 {sug}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>

                  {isUser && (
                    <div className="w-9 h-9 rounded-2xl bg-slate-200 text-slate-700 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <User size={18} />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {loading && (
            <div className="flex items-center gap-3 p-4 bg-white rounded-2xl border border-slate-200 w-fit text-xs text-slate-500 shadow-sm animate-pulse">
              <RefreshCw size={16} className="animate-spin text-brand-600" />
              <span>AgriSense AI is generating response...</span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="p-4 bg-white border-t border-[#e3ecd9] flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask anything: Python, Java, Photosynthesis, Crops, Soil pH, ML prediction model..."
            className="flex-1 px-5 py-3.5 bg-slate-50 border border-slate-200 rounded-2xl text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="flex items-center gap-2 px-6 py-3.5 bg-brand-600 hover:bg-brand-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-2xl font-semibold shadow-sm transition-all"
          >
            <span>Send</span>
            <Send size={16} />
          </button>
        </form>
      </div>
    </div>
  );
}
