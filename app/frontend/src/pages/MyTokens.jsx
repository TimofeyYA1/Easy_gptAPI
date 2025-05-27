import React, { useEffect, useState } from "react";
import CreateTokenModal from "../components/CreateTokenModal";
import TokenCard from "../components/TokenCard";
import "./MyTokens.css";

const TokensPage = () => {
  const [tokens, setTokens] = useState([]);
  const [selectedTokenIds, setSelectedTokenIds] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/tokens", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setTokens(data);
      } else {
        console.error("Ошибка при загрузке токенов");
      }
    } catch (error) {
      console.error("Ошибка при запросе токенов:", error);
    }
  };

  const handleSelect = (id, isChecked) => {
    setSelectedTokenIds((prev) =>
      isChecked ? [...prev, id] : prev.filter((tokenId) => tokenId !== id)
    );
  };

  const handleDeleteSelected = async () => {
    for (const id of selectedTokenIds) {
      await fetch(`http://localhost:8000/api/tokens/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      });
    }
    setSelectedTokenIds([]);
    fetchTokens();
  };

  const filteredTokens = tokens.filter((t) =>
    (t.name || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="tokens-page-container">
      <div className="tokens-header">
        <h2>Мои токены</h2>
        <div className="tokens-controls">
          <input
            type="text"
            placeholder="Поиск токенов..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          {selectedTokenIds.length > 0 && (
            <button onClick={handleDeleteSelected} className="danger-btn">
              Удалить выбранные
            </button>
          )}
          <button onClick={() => setShowModal(true)}>Создать</button>
        </div>
      </div>

      <div className="tokens-list-wrapper">
        <div className="tokens-list-scrollable">
          {filteredTokens.length === 0 ? (
            <div className="no-tokens-message">У вас пока нет токенов</div>
          ) : (
            filteredTokens.map((token) => (
              <TokenCard
                key={token.id}
                token={token}
                selected={selectedTokenIds.includes(token.id)}
                onSelect={(id) =>handleSelect(id, !selectedTokenIds.includes(id))}
                onUpdate={fetchTokens}
                onDeleted={() =>
                  setTokens((prev) => prev.filter((t) => t.id !== token.id))
                }
              />
            ))
          )}
        </div>
      </div>

      {showModal && (
        <CreateTokenModal
          onClose={() => setShowModal(false)}
          onCreated={(newToken) => {
            setTokens((prevTokens) => [newToken, ...prevTokens]);
            setShowModal(false);
          }}
        />
      )}
    </div>
  );
};

export default TokensPage;
