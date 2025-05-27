import './HelpPage.css';
import React, { useEffect } from 'react';

const HelpPage = () => {
    useEffect(() => {
    // Включаем прокрутку при заходе на HelpPage
    document.body.style.overflow = 'auto';

    // Когда уходим — возвращаем как было (например, отключаем)
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
            <p><strong>POST /ask_gpt-3.5-turbo</strong> — отправить одиночный запрос к GPT без истории.</p>
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
            <p><strong>POST /dialogs/create</strong> — создать диалог с заголовком и системной ролью.</p>
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
            <p><strong>POST /dialogs/chat</strong> — отправить новое сообщение в диалоге.</p>
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
            <p><strong>GET /dialogs/{`{token}`}</strong></p>
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
            <p><strong>DELETE /dialogs/{`{dialog_id}`}?token=tok_abc123</strong></p>
            <pre>
{`{
  "detail": "Диалог uuid-1234 удалён"
}`}
            </pre>
          </section>

          <section>
            <h2>✏️ 6. Переименование диалога</h2>
            <p><strong>PATCH /dialogs/rename</strong></p>
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
        </div>
      </main>
    </div>
  );
};

export default HelpPage;
