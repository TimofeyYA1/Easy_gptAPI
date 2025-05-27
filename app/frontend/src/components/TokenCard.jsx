import React, { useState, useRef, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { FiCopy } from 'react-icons/fi';
import RenameTokenModal from './RenameTokenModal';
import './TokenCard.css';

const TokenCard = ({ token, selected, onSelect, onUpdate }) => {
  const [menuOpen, setMenuOpen] = useState(false);
  const iconRef = useRef(null);
  const [menuPosition, setMenuPosition] = useState({ top: 0, left: 0 });
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showTopUpModal, setShowTopUpModal] = useState(false); // для модалки пополнения

  const handleCopy = () => {
    navigator.clipboard.writeText(token.token);
  };

  const handleDelete = async () => {
    await fetch(`http://localhost:8001/api/tokens/${token.id}`, {
      method: 'DELETE',
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    onUpdate();
  };

  const handleGen = async () => {
    await fetch(`http://localhost:8001/api/${token.token}/regenerate`, {
      method: 'PATCH',
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
    console.log("handleRename вызван");
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
      document.addEventListener('click', handleClickOutside);
    }

    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  const renderMenu = () => (
    <div
      className="dropdown-menu"
      style={{ position: 'fixed', top: menuPosition.top, left: menuPosition.left, width: 160 }}
    >
      <div onClick={handleRename}>Переименовать</div>
      <div onClick={handleDelete}>Удалить</div>
      <div onClick={handleGen}>Перегенирировать</div>
    </div>
  );

  const renderTopUpModal = () => (
 <div className="modal-overlay">
    <div className="modal-content">
      <p>
        Пока эта функция недоступна. Если хотите узнать больше — пишите в&nbsp;
        <a
          href="https://t.me/timofeyakov1"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#6daaff', textDecoration: 'underline' }}
        >
          Telegram
        </a>
        .
      </p>
      <button onClick={() => setShowTopUpModal(false)}>Закрыть</button>
    </div>
  </div>  
  );

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
        <button className="top-up-btn" onClick={() => setShowTopUpModal(true)}>Пополнить</button>
        <div className="menu-icon" onClick={() => setMenuOpen(!menuOpen)} ref={iconRef}>
          ⋮
        </div>
      </div>

      {menuOpen && ReactDOM.createPortal(renderMenu(), document.body)}

      {showRenameModal && (
        <RenameTokenModal
          token={token}
          onClose={() => setShowRenameModal(false)}
          onRename={onUpdate}
        />
      )}

      {showTopUpModal && ReactDOM.createPortal(renderTopUpModal(), document.body)}
    </>
  );
};

export default TokenCard;
