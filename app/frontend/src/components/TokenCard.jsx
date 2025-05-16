import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { FiCopy } from 'react-icons/fi';
import RenameTokenModal from './RenameTokenModal'; // импортируем модалку
import './TokenCard.css';

const TokenCard = ({ token, selected, onSelect, onUpdate }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const iconRef = useRef(null);
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });
  const [showRenameModal, setShowRenameModal] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(token.token);
  };

  const handleDelete = async () => {
    await fetch(`http://localhost:8000/api/tokens/${token.id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    onUpdate();
  };

  const handleSelect = (e) => {
    onSelect(token.id, e.target.checked);
  };

  const handleRename = () => {
      console.log("handleRename вызван"); // Это поможет понять, вызывается ли обработчик
      setShowRenameModal(true);
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!iconRef.current?.contains(event.target)) {
        setMenuOpen(false);
      }
    };

    if (menuOpen) {
      const rect = iconRef.current.getBoundingClientRect();
      setMenuPosition({ top: rect.bottom + 5, left: rect.left });
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  const renderMenu = () => (
    <div
      className="dropdown-menu"
      style={{ position: 'fixed', top: menuPosition.top, left: menuPosition.left }}
    >
      <div onClick={handleRename}>Переименовать</div>
      <div onClick={handleDelete}>Удалить</div>
    </div>
  );
  console.log(showRenameModal);
  return (
    <>
      <div className="token-card">
        <input
          type="checkbox"
          className="token-checkbox"
          checked={selected}
          onChange={handleSelect}
        />
        <div className="token-name">{token.name}</div>
        <div className="token-string">
          <span className="token-value">{token.token}</span>
          <FiCopy className="copy-icon" onClick={handleCopy} title="Копировать" />
        </div>
        <div className="token-balance">{token.balance}</div>
        <button className="top-up-btn">Пополнить</button>
        <div className="menu-icon" onClick={() => setMenuOpen(!menuOpen)} ref={iconRef}>
          ⋮
        </div>
      </div>

      {menuOpen && ReactDOM.createPortal(renderMenu(), document.body)}

      {showRenameModal && (
        <RenameTokenModal
          token={token}
          onClose={() => setShowRenameModal(false)}
          onRename={onUpdate} // обновляем список токенов
        />
      )}
    </>
  );
};

export default TokenCard;
