import './Home.css';
import { useNavigate } from 'react-router-dom';

const Home = () => {
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
    <div className="home-container">
      <main className="main-content">
        <div className="text-content">
          <h1>
            Простой доступ к <span>ChatGPT</span> из <span>России</span>
          </h1>
          <p>
            Наш сервис обеспечивает удобный, быстрый и безопасный доступ к ChatGPT API без ограничений.
          </p>
          <div className="button-group">
            <button onClick={handleStartClick} className="primary-button">
              Начать
            </button>
            <a href="/about" className="secondary-button">Узнать больше</a>
          </div>
        </div>
        <div className="image-container">
          <img
            src="https://images.unsplash.com/photo-1620712943543-bcc4688e7485"
            alt="AI Illustration"
            className="tilted-image"
          />
        </div>
      </main>
    </div>
  );
};

export default Home;