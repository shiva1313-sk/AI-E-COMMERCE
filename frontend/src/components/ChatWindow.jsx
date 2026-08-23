import React, { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import LoadingIndicator from './LoadingIndicator';

const SUGGESTIONS = [
  {
    tag: 'Running Shoes',
    text: 'Suggest running shoes under ₹3000'
  },
  {
    tag: 'Smartphones',
    text: 'I need a phone under 20,000 with a good camera'
  },
  {
    tag: 'Customer Support',
    text: 'Can I return a product after 7 days?'
  },
  {
    tag: 'College Tech',
    text: 'Show me affordable laptops for a college student'
  },
  {
    tag: 'Warranty Policy',
    text: 'How long is the product warranty and how do I claim it?'
  },
  {
    tag: 'Work From Home',
    text: 'Which ergonomic mouse and keyboard are good for daily office use?'
  }
];

export default function ChatWindow({
  messages,
  isLoading,
  onSendMessage,
  onSelectProduct
}) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="chat-feed">
      {messages.length === 0 ? (
        <div className="empty-chat-welcome">
          <div className="welcome-icon-box">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
              <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
              <line x1="12" y1="22.08" x2="12" y2="12"/>
            </svg>
          </div>
          <h2 className="welcome-title">How can I assist your shopping today?</h2>
          <p className="welcome-desc">
            Ask for product recommendations, compare specifications within your budget, or inquire about store policies like returns, cancellations, and warranties.
          </p>

          <div className="suggestion-grid">
            {SUGGESTIONS.map((item, idx) => (
              <div
                key={idx}
                className="suggestion-card"
                onClick={() => onSendMessage(item.text)}
              >
                <span className="suggestion-tag">{item.tag}</span>
                <span className="suggestion-text">"{item.text}"</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg}
              onSelectProduct={onSelectProduct}
            />
          ))}
          {isLoading && <LoadingIndicator />}
        </>
      )}
      <div ref={bottomRef} />
    </div>
  );
}
