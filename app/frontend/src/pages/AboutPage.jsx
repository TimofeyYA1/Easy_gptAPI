// src/pages/AboutPage.jsx
import React from 'react';
import './AboutPage.css';
import { useNavigate } from 'react-router-dom';

const AboutPage = () => {
  const navigate = useNavigate();
  const handleStartClick = () => {
    const token = localStorage.getItem('token');
    if (token) {
      navigate('/tokens');
    } else {
      navigate('/login');
    }
  };
  return (
    <div className="about-page">
      <div className="about-container">
        <h1>О проекте EasyGPT API</h1>
        <p className="about-intro">
          Мы предоставляем простой и надёжный доступ к ChatGPT API — без ограничений, с прозрачной системой токенов и поддержкой пользователей из России.
        </p>

        <div className="features-grid">
          <div className="feature-card">
            <h3>🚀 Быстрое подключение</h3>
            <p>Создайте токен и начните использовать API в течение минуты. У нас — минимум настроек.</p>
          </div>
          <div className="feature-card">
            <h3>🔒 Безопасность</h3>
            <p>Все данные защищены, а доступ к токенам возможен только после входа в аккаунт.</p>
          </div>
          <div className="feature-card">
            <h3>⚙️ Гибкость</h3>
            <p>Создавайте несколько токенов, управляйте их балансом, удаляйте и переименовывайте — всё в одном месте.</p>
          </div>
          <div className="feature-card">
            <h3>💬 Поддержка</h3>
            <p>Наша команда всегда на связи. Мы поможем вам интегрировать API или решить любые вопросы.</p>
          </div>
        </div>

        <div className="about-cta">
          <p>Готовы начать?</p>
          <button onClick={handleStartClick} className="primary-button">Создать токен</button>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
