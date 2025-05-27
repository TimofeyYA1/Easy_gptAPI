import React, { useState } from 'react';
import './RenameTokenModal.css'; // Добавим стили для модалки

const RenameTokenModal = ({ token, onClose, onRename }) => {
  console.log('Модалка рендерится');
  const [newName, setNewName] = useState(token.name);
  const [error, setError] = useState("");

  const handleSubmit = async () => {
    if (!newName.trim()) {
      setError("Имя не может быть пустым");
      return;
    }

    try {
      await fetch(`http://localhost:8001/api/${token.token}/rename`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
        body: JSON.stringify({ new_name: newName}),
      });

      onRename(); // Вызываем onRename для обновления токенов
      onClose(); // Закрываем модалку
    } catch (error) {
      setError("Ошибка при переименовании токена");
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Переименовать токен</h3>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Новое имя токена"
        />
        {error && <div className="error-message">{error}</div>}
        <div className="modal-buttons">
          <button onClick={handleSubmit}>Сохранить</button>
          <button className="cancel" onClick={onClose}>Отмена</button>
        </div>
      </div>
    </div>
  );
};

export default RenameTokenModal;
