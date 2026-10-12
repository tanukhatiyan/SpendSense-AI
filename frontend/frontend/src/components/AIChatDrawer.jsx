import React, { useState, useRef, useEffect } from 'react';
import { api } from '../api';

const QUICK_PROMPTS = [
  'How much did I spend this month?',
  'Which category costs me the most?',
  'Am I exceeding my budget?',
  'Where could I reduce spending?',
  'Summarize my spending habits.',
];

export default function AIChatDrawer({ isOpen, onClose }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "👋 Hi! I'm your **SpendSense AI Assistant**. I analyze your verified financial records to help you monitor spending, check budget thresholds, and find savings opportunities. What would you like to explore today?",
      provider: 'SpendSense AI Engine',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  if (!isOpen) return null;

  const handleSend = async (messageText) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || loading) return;

    const userMsg = { role: 'user', content: textToSend.trim() };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput('');
    setError(null);
    setLoading(true);

    try {
      // Build history for backend
      const history = updatedMessages
        .slice(-6)
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await api.askAI(userMsg.content, history);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          provider: res.provider || 'AI Engine',
        },
      ]);
    } catch (err) {
      setError(err.message || 'Unable to contact AI assistant.');
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content:
            '⚠️ Sorry, I could not complete that request. Please ensure the backend is running and any configured API keys are valid.',
          provider: 'Error',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-drawer-overlay" onClick={onClose}>
      <div className="ai-drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div className="ai-drawer-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.4rem' }}>🤖</span>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem' }}>SpendSense AI Assistant</h3>
              <span style={{ fontSize: '0.75rem', color: '#10b981' }}>● Grounded in Real Financial Ledger</span>
            </div>
          </div>
          <button className="close-btn" onClick={onClose} aria-label="Close assistant">✕</button>
        </div>

        {/* Quick Prompts Bar */}
        <div className="ai-quick-prompts">
          <span style={{ fontSize: '0.75rem', color: '#888', display: 'block', marginBottom: '4px' }}>
            Suggested Queries:
          </span>
          <div style={{ display: 'flex', gap: '6px', overflowX: 'auto', paddingBottom: '4px' }}>
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                className="ai-chip-btn"
                onClick={() => handleSend(prompt)}
                disabled={loading}
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Message Log */}
        <div className="ai-message-list">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`ai-message-bubble ${m.role === 'user' ? 'ai-user-bubble' : 'ai-bot-bubble'}`}
            >
              <div style={{ whiteSpace: 'pre-line', lineHeight: '1.5', fontSize: '0.92rem' }}>
                {m.content}
              </div>
              {m.role === 'assistant' && m.provider && (
                <div style={{ marginTop: '6px', fontSize: '0.7rem', color: '#777', textAlign: 'right' }}>
                  ⚡ Powered by {m.provider}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="ai-message-bubble ai-bot-bubble" style={{ color: '#888', fontStyle: 'italic' }}>
              <span>Analysing ledger & synthesizing financial advice...</span>
            </div>
          )}

          {error && <div className="error-banner" style={{ margin: '8px 0' }}>{error}</div>}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="ai-input-form"
        >
          <input
            type="text"
            className="form-input"
            placeholder="Ask a question about your spending..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !input.trim()}
            style={{ padding: '0 16px', fontWeight: 'bold' }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
