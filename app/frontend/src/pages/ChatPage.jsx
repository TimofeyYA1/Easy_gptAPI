// ChatPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import './ChatPage.css';

const API_BASE = "http://localhost:8000";

const ChatPage = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef(null);

  // 1. Проверка токена и загрузка истории
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return navigate('/login');

    (async () => {
      try {
        const res = await fetch(`${API_BASE}/api/chat`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setMessages(Array.isArray(data.history) ? data.history : []);
      } catch (e) {
        console.error('Не удалось загрузить историю:', e);
        setMessages([]);
      }
    })();
  }, [navigate]);

  // 2. Автоскролл
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // 3. Отправка сообщения
  const handleSend = async () => {
    if (!input.trim()) return;
    const token = localStorage.getItem('token');

    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: input }),
      });
      const { reply } = await res.json();
      setMessages(prev => [...prev, { sender: 'bot', text: reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { sender: 'bot', text: 'Ошибка сервера.' }]);
    } finally {
      setInput('');
      setLoading(false);
    }
  };

  // 4. Очистка чата
  const handleClear = async () => {
    const token = localStorage.getItem('token');
    try {
      await fetch(`${API_BASE}/api/chat/clear`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages([]);
    } catch (e) {
      console.error('Не удалось очистить чат:', e);
    }
  };

  const onKeyDown = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        <header className="chat-header">
          <span>Чат с ИИ</span>
          <button className="clear-button" onClick={handleClear}>Очистить</button>
        </header>
        <div className="chat-messages">
          {(messages || []).map((m, i) => (
            m.sender === 'bot'
              ? (
                <pre key={i} className="message bot html-message">
                  {m.text}
                </pre>
              )
              : (
                <div key={i} className="message user">
                  {m.text}
                </div>
              )
          ))}
          <div ref={bottomRef} />
        </div>
        <div className="chat-input-area">
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="Введите сообщение..."
            rows={1}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()}>
            {loading ? '…' : 'Отправить'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
