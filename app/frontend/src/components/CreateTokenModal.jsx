import React, { useState } from "react";
import "./CreateTokenModal.css";

const CreateTokenModal = ({ onClose, onCreated, onError }) => {
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleCreate = async () => {
    if (!name.trim()) {
      setError("Название не может быть пустым");
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/tokens", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ name }),
      });

      if (response.ok) {
        const newToken = await response.json();
        onCreated(newToken);
      } else {
        const data = await response.json();
        const message = data.detail || "Ошибка при создании токена";
        setError(message);
        if (onError) onError(message);
      }
    } catch (e) {
      const message = "Сетевая ошибка или сервер недоступен";
      setError(message);
      if (onError) onError(message);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>Создание токена</h3>
        <input
          type="text"
          placeholder="Название токена"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        {error && <div className="error-message">{error}</div>}
        <div className="modal-buttons">
          <button onClick={handleCreate}>Создать</button>
          <button onClick={onClose} className="cancel">Отмена</button>
        </div>
      </div>
    </div>
  );
};

export default CreateTokenModal;
