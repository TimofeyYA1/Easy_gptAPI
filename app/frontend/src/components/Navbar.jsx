// src/components/Navbar.jsx
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="logo">
        🤖 EasyGPT<span style={{ color: 'var(--accent-blue)' }}>API</span>
      </div>
      <div className="nav-links">
        {token && <Link to="/tokens">Мои токены</Link>}
        <Link to="/chat">Чат с ИИ</Link>
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>

        {token ? (
          <button onClick={handleLogout} className="nav-btn logout">Выйти</button> // Кнопка Выйти
        ) : (
          <Link to="/login" className="nav-links a login-btn">Login</Link> // Кнопка Login
        )}
      </div>
    </nav>
  );
};

export default Navbar;
