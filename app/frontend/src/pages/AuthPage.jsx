import React, { useState } from 'react'; 
import { useNavigate } from 'react-router-dom'; // добавлено
import './AuthPage.css';

const LoginPage = () => {
  const navigate = useNavigate();

  const [mode, setMode] = useState('login');
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    const endpoint = mode === 'login' ? '/api/login' : '/api/register';

    try {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': mode === 'login'
            ? 'application/x-www-form-urlencoded'
            : 'application/json',
        },
        body:
          mode === 'login'
            ? new URLSearchParams({
                username: email,
                password,
              })
            : JSON.stringify({
                email,
                username,
                password,
                repeat_password: repeatPassword,
              }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.detail || 'Ошибка авторизации');
        return;
      }

      if (data.access_token) {
        localStorage.setItem('token', data.access_token);
        navigate('/'); // Переход после успешного входа
      }
    } catch (error) {
      console.error('Ошибка запроса:', error);
      alert('Произошла ошибка при подключении к серверу');
    }
  };

  return (
    <div className="login-page">
      <div className={`auth-box ${mode === 'register' ? 'register-mode' : ''}`}>
        <div className="auth-toggle">
          <button
            className={mode === 'login' ? 'active' : ''}
            onClick={() => setMode('login')}
          >
            Вход
          </button>
          <button
            className={mode === 'register' ? 'active' : ''}
            onClick={() => setMode('register')}
          >
            Регистрация
          </button>
        </div>

        <h2 className="auth-title">
          {mode === 'login' ? 'Добро пожаловать' : 'Создать аккаунт'}
        </h2>

        <form className="auth-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          {mode === 'register' && (
            <input
              type="text"
              placeholder="Имя пользователя"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
          )}
          <input
            type="password"
            placeholder="Пароль"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {mode === 'register' && (
            <input
              type="password"
              placeholder="Повторите пароль"
              value={repeatPassword}
              onChange={(e) => setRepeatPassword(e.target.value)}
            />
          )}
          <button type="submit" className="submit-btn">
            {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </button>
        </form>

        <div className="auth-footer"> 
          {mode === 'login' ? (
            <>
              Нет аккаунта?{' '}
              <span onClick={() => setMode('register')}>Зарегистрируйтесь</span>
            </>
          ) : (
            <>
              Уже есть аккаунт?{' '}
              <span onClick={() => setMode('login')}>Войдите</span>
            </>
          )}
        </div>
      </div>

      <div className="info-box">
        <h3>Доступ к ChatGPT из России</h3>
        <p>
          Наш сервис предоставляет простой и безопасный способ использовать ChatGPT API без
          ограничений.
        </p>
        <ul>
          <li>✔️ Множественные API-токены</li>
          <li>✔️ Быстрое и надёжное подключение</li>
          <li>✔️ Гибкая оплата только за использование</li>
          <li>✔️ Простая интеграция с вашим приложением</li>
        </ul>
      </div>
    </div>
  );
};

export default LoginPage;
