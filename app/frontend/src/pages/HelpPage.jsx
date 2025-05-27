import './HelpPage.css';
import React, { useEffect } from 'react';

const HelpPage = () => {
  useEffect(() => {
    document.body.style.overflow = 'auto';
    return () => {
      document.body.style.overflow = 'hidden';
    };
  }, []);

  return (
    <div className="help-container">
      <main className="help-content">
        <div className="help-text">
          <h1>📖 Как пользоваться API</h1>
          <p>Вот список всех доступных запросов к серверу:</p>

          <section>
            <h2>📩 1. Отправка запроса к GPT</h2>
            <p><strong>POST</strong> — отправить одиночный запрос к GPT без истории.</p>
            <p><code>http://83.242.100.163:8001/ask_gpt-3.5-turbo</code></p>
            <pre>
{`{
  "prompt": "Расскажи анекдот",
  "token": "tok_abc123",
  "max_tokens": 100,
  "temperature": 0.3
}`}
            </pre>
            <p><strong>Ответ:</strong></p>
            <pre>
{`{
  "response": "Вот анекдот...",
  "total_cost": 100
}`}
            </pre>
          </section>

          <section>
            <h2>💬 2. Создание нового диалога</h2>
            <p><strong>POST</strong> — создать диалог с заголовком и системной ролью.</p>
            <p><code>http://83.242.100.163:8001/dialogs/create</code></p>
            <pre>
{`{
  "token": "tok_abc123",
  "title": "Помощник по программированию",
  "model": "gpt-3.5-turbo",
  "temperature": 0.3,
  "system": "Ты программист, помогаешь писать код"
}`}
            </pre>
            <p><strong>Ответ:</strong></p>
            <pre>
{`{
  "dialog_id": "uuid-1234",
  "title": "Помощник по программированию"
}`}
            </pre>
          </section>

          <section>
            <h2>🔁 3. Продолжение диалога</h2>
            <p><strong>POST</strong> — отправить новое сообщение в диалоге.</p>
            <p><code>http://83.242.100.163:8001/dialogs/chat</code></p>
            <pre>
{`{
  "dialog_id": "uuid-1234",
  "token": "tok_abc123",
  "message": "Как написать функцию на Python?",
  "max_tokens": 100
}`}
            </pre>
            <p><strong>Ответ:</strong></p>
            <pre>
{`{
  "response": "Вот пример функции...",
  "total_tokens_used": 150,
  "new_balance": 9850,
  "total_tokens": 300
}`}
            </pre>
          </section>

          <section>
            <h2>📄 4. Получить список диалогов</h2>
            <p><strong>GET</strong> — получить все диалоги по токену.</p>
            <p><code>http://83.242.100.163:8001/dialogs/{`{token}`}</code></p>
            <pre>
{`{
  "dialogs": [
    { "id": "uuid-1", "title": "Помощник", "model": "gpt-3.5-turbo" },
    { "id": "uuid-2", "title": "Шутки", "model": "gpt-3.5-turbo" }
  ]
}`}
            </pre>
          </section>

          <section>
            <h2>🗑 5. Удаление диалога</h2>
            <p><strong>DELETE</strong> — удалить диалог по ID и токену.</p>
            <p><code>http://83.242.100.163:8001/dialogs/{`{dialog_id}`}?token=tok_abc123</code></p>
            <pre>
{`{
  "detail": "Диалог uuid-1234 удалён"
}`}
            </pre>
          </section>

          <section>
            <h2>✏️ 6. Переименование диалога</h2>
            <p><strong>PATCH</strong> — переименовать существующий диалог.</p>
            <p><code>http://83.242.100.163:8001/dialogs/rename</code></p>
            <pre>
{`{
  "dialog_id": "uuid-1234",
  "token": "tok_abc123",
  "new_title": "Новый заголовок"
}`}
            </pre>
            <p><strong>Ответ:</strong></p>
            <pre>
{`{
  "detail": "Диалог uuid-1234 переименован в 'Новый заголовок'"
}`}
            </pre>
          </section>

          <hr style={{ marginTop: '40px' }} />

          <section>
            <h2>📚 Документация API</h2>
            <p>
              Полная интерактивная документация Swagger доступна по адресу:&nbsp;
              <a
                href="http://83.242.100.163:8001/docs#/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#6daaff', textDecoration: 'underline' }}
              >
                http://83.242.100.163:8001/docs#/
              </a>
            </p>
          </section>
        </div>
      </main>
    </div>
  );
};

export default HelpPage;
