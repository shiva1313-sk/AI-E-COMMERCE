import React from 'react';

const QUICK_AI_TAGS = [
  "Running shoes under ₹3000",
  "Phone under 20,000 with good camera",
  "Laptops for college under 30k",
  "Ergonomic mouse & keyboard",
  "ANC headphones for travel"
];

export default function HeroBanner({ onSearchTag, onOpenChatbot }) {
  return (
    <section className="hero-banner">
      <div className="hero-content">
        <div className="hero-badge">
          <span className="hero-badge-pulse" />
          <span>Flipkart-Grade AI Shopping & Assistant</span>
        </div>
        <h1 className="hero-title">
          Discover Best Deals with <span className="text-gradient">AI Precision</span>
        </h1>
        <p className="hero-subtitle">
          Over 60+ verified tech products, instant price matching, grounded customer policies, and seamless 1-click checkout.
        </p>

        <div className="hero-quick-tags">
          <span className="hero-tags-label">Popular AI Searches:</span>
          <div className="hero-tags-list">
            {QUICK_AI_TAGS.map((tag, idx) => (
              <button
                key={idx}
                className="hero-tag-pill"
                onClick={() => onSearchTag(tag)}
              >
                ✨ {tag}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="hero-action-card">
        <div className="hero-ai-card-inner">
          <div className="hero-ai-header">
            <div className="hero-ai-icon">🤖</div>
            <div>
              <h3 style={{ fontSize: '1rem', fontWeight: '700' }}>AI Assistant Active</h3>
              <p style={{ fontSize: '0.78rem', color: '#94a3b8' }}>RAG Grounded in Verified Catalog</p>
            </div>
          </div>
          <p style={{ fontSize: '0.84rem', color: '#cbd5e1', marginBottom: '14px', lineHeight: '1.5' }}>
            Need tailored product advice or have questions about 7-day returns, delivery, and warranty?
          </p>
          <button className="btn-hero-chat" onClick={onOpenChatbot}>
            <span>Chat with ShopEase AI</span>
            <span>➔</span>
          </button>
        </div>
      </div>
    </section>
  );
}
