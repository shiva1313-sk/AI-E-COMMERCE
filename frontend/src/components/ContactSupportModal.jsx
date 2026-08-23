import React from 'react';

export default function ContactSupportModal({ onClose, onOpenChatbot }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="support-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.4rem' }}>🎧</span>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem' }}>
              ShopEase 24/7 Customer Help Center
            </h2>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        <div className="support-channels-grid">
          <div className="support-channel-card">
            <div className="channel-icon">📞</div>
            <h4>Toll-Free Helpline</h4>
            <p className="channel-highlight">1800-202-9898</p>
            <p className="channel-subtext">Mon to Sat, 9:00 AM – 8:00 PM IST</p>
          </div>

          <div className="support-channel-card">
            <div className="channel-icon">✉️</div>
            <h4>Email Support</h4>
            <p className="channel-highlight">support@shopease.com</p>
            <p className="channel-subtext">Guaranteed response within 24 hours</p>
          </div>

          <div className="support-channel-card">
            <div className="channel-icon">🤖</div>
            <h4>AI Instant Support</h4>
            <p className="channel-highlight">Live 24/7 Assistant</p>
            <button
              className="btn-channel-action"
              onClick={() => {
                onClose();
                onOpenChatbot();
              }}
            >
              Start AI Chat
            </button>
          </div>
        </div>

        <h3 style={{ fontSize: '0.95rem', color: '#94a3b8', textTransform: 'uppercase', marginTop: '24px', marginBottom: '12px', letterSpacing: '0.04em' }}>
          Quick Store Policies & Guidelines
        </h3>

        <div className="support-faq-grid">
          <div className="support-faq-card">
            <h5>🔄 7-Day Easy Returns</h5>
            <p>Return any eligible product within 7 days of delivery. Refunds are credited to UPI in 24-48 hours and cards in 3-5 days.</p>
          </div>

          <div className="support-faq-card">
            <h5>🚚 Fast & Free Shipping</h5>
            <p>Free standard delivery on all orders above ₹999. Express delivery delivered in 24-48 hours across metro locations.</p>
          </div>

          <div className="support-faq-card">
            <h5>🛡️ 1-Year Brand Warranty</h5>
            <p>All electronics carry standard 1-year brand warranty from authorized manufacturer service centers.</p>
          </div>

          <div className="support-faq-card">
            <h5>🚫 Instant Cancellation</h5>
            <p>Cancel any order before dispatch with 100% full instant refund to your original payment method.</p>
          </div>
        </div>

        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
          <button className="btn-secondary" onClick={onClose}>
            Close Help Center
          </button>
        </div>
      </div>
    </div>
  );
}
