import React, { useState } from 'react';
import ChatWindow from './ChatWindow';
import ChatInput from './ChatInput';

export default function FloatingChatbot({
  isOpen,
  onToggle,
  messages,
  isLoading,
  onSendMessage,
  onClearChat,
  onSelectProduct
}) {
  const [isMaximized, setIsMaximized] = useState(false);

  return (
    <div className={`floating-chatbot-wrapper ${isOpen ? 'open' : ''} ${isMaximized ? 'maximized' : ''}`}>
      {/* Collapsed Floating Trigger Bubble */}
      {!isOpen && (
        <button className="floating-chatbot-trigger" onClick={onToggle} title="Open Flipkart AI Shopping Assistant">
          <div className="trigger-icon-pulse">
            <span className="trigger-pulse-dot" />
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <span className="trigger-text">Ask ShopEase AI</span>
        </button>
      )}

      {/* Expanded Chat Drawer / Window */}
      {isOpen && (
        <div className="floating-chat-window">
          {/* Chat Header */}
          <div className="floating-chat-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <div className="chat-avatar-badge">🤖</div>
              <div>
                <h3 style={{ fontSize: '0.95rem', fontWeight: '700', color: '#ffffff' }}>
                  ShopEase AI Shopping Guide
                </h3>
                <p style={{ fontSize: '0.72rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#34d399', display: 'inline-block' }} />
                  Grounded in 60+ Products & Policies
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              {messages.length > 0 && (
                <button
                  className="btn-chat-ctrl"
                  onClick={onClearChat}
                  title="Clear Chat History"
                >
                  🗑️
                </button>
              )}
              <button
                className="btn-chat-ctrl"
                onClick={() => setIsMaximized(!isMaximized)}
                title={isMaximized ? 'Restore Size' : 'Maximize'}
              >
                {isMaximized ? '❐' : '⛶'}
              </button>
              <button
                className="btn-chat-ctrl"
                onClick={onToggle}
                title="Close Assistant"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Chat Feed */}
          <div className="floating-chat-body">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              onSendMessage={onSendMessage}
              onSelectProduct={onSelectProduct}
            />
          </div>

          {/* Chat Input */}
          <div className="floating-chat-footer">
            <ChatInput
              onSendMessage={onSendMessage}
              isLoading={isLoading}
            />
          </div>
        </div>
      )}
    </div>
  );
}
