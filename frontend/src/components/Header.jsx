import React, { useState } from 'react';
import { useCart } from '../context/CartContext';

export default function Header({
  health,
  onSearch,
  searchQuery,
  onOpenCart,
  onOpenOrders,
  onOpenSupport,
  onOpenChatbot
}) {
  const { totalItems } = useCart();
  const [localQuery, setLocalQuery] = useState(searchQuery || '');

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (!localQuery.trim()) return;
    onSearch(localQuery.trim());
  };

  const isOnline = health && (health.status === 'healthy' || health.status === 'degraded');
  const isOllamaOnline = health?.ollama === 'available';

  return (
    <header className="flipkart-header">
      <div className="header-inner">
        {/* Brand Logo */}
        <div className="header-brand-group">
          <div className="brand-logo-container" onClick={() => onSearch('')} style={{ cursor: 'pointer' }}>
            <span className="brand-name">ShopEase</span>
            <span className="brand-plus-tag">
              Explore <em>Plus</em> ✦
            </span>
          </div>
        </div>

        {/* Top AI Search Bar */}
        <form onSubmit={handleSearchSubmit} className="header-ai-search-form">
          <div className="ai-search-input-box">
            <svg className="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8"/>
              <line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input
              type="text"
              className="ai-search-input"
              value={localQuery}
              onChange={(e) => setLocalQuery(e.target.value)}
              placeholder="Search products, brands or try AI queries (e.g. 'Running shoes under 3000')..."
            />
            {localQuery && (
              <button
                type="button"
                className="btn-clear-search"
                onClick={() => {
                  setLocalQuery('');
                  onSearch('');
                }}
              >
                ✕
              </button>
            )}
            <button type="submit" className="btn-ai-search-submit" title="AI Search">
              <span>Search</span>
            </button>
          </div>
        </form>

        {/* Right Actions: AI Assistant, Support, Orders, Cart */}
        <div className="header-nav-actions">
          {/* Ask AI Button */}
          <button className="nav-action-btn ai-highlight" onClick={onOpenChatbot}>
            <span className="nav-btn-icon">🤖</span>
            <span className="nav-btn-text">AI Assistant</span>
          </button>

          {/* 24/7 Support */}
          <button className="nav-action-btn" onClick={onOpenSupport}>
            <span className="nav-btn-icon">🎧</span>
            <span className="nav-btn-text">Support</span>
          </button>

          {/* My Orders */}
          <button className="nav-action-btn" onClick={onOpenOrders}>
            <span className="nav-btn-icon">📦</span>
            <span className="nav-btn-text">Orders</span>
          </button>

          {/* Cart with Live Count Badge */}
          <button className="nav-action-btn cart-btn" onClick={onOpenCart}>
            <div className="cart-icon-wrapper">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="9" cy="21" r="1"/>
                <circle cx="20" cy="21" r="1"/>
                <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
              </svg>
              {totalItems > 0 && (
                <span className="cart-count-badge">{totalItems}</span>
              )}
            </div>
            <span className="nav-btn-text">Cart</span>
          </button>

          {/* Health Pill */}
          <div className="header-health-pill" title={`Ollama: ${health?.ollama || 'Checking'}`}>
            <span className={`status-dot ${isOnline ? 'online' : 'offline'}`} />
            <span className="health-text">{isOllamaOnline ? 'AI Model Online' : 'AI Hybrid Active'}</span>
          </div>
        </div>
      </div>
    </header>
  );
}
