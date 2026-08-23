import React from 'react';
import ProductGrid from './ProductGrid';

export default function ChatMessage({ message, onSelectProduct }) {
  const isUser = message.sender === 'user';

  // Basic markdown-like line renderer for paragraphs and bullet points
  const renderFormattedText = (text) => {
    if (!text) return null;
    const lines = text.split('\n');
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) {
        return <div key={idx} style={{ height: '8px' }} />;
      }
      if (trimmed.startsWith('• ') || trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
        return (
          <li key={idx} style={{ marginLeft: '18px', marginBottom: '4px' }}>
            {parseInlineStyles(trimmed.substring(2))}
          </li>
        );
      }
      return (
        <p key={idx} style={{ marginBottom: '6px' }}>
          {parseInlineStyles(trimmed)}
        </p>
      );
    });
  };

  const parseInlineStyles = (str) => {
    // Basic bold **text** parsing
    const parts = str.split(/(\*\*.*?\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={i}>{part.slice(2, -2)}</strong>;
      }
      if (part.startsWith('*') && part.endsWith('*') && part.length > 2) {
        return <em key={i}>{part.slice(1, -1)}</em>;
      }
      return part;
    });
  };

  return (
    <div className={`chat-row ${isUser ? 'user' : 'assistant'}`}>
      <div className={`avatar ${isUser ? 'user-avatar' : 'ai-avatar'}`}>
        {isUser ? (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        ) : (
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        )}
      </div>

      <div className="message-bubble-container">
        <div className="message-bubble">
          {renderFormattedText(message.text)}
        </div>

        {/* Product Recommendations Grid */}
        {message.products && message.products.length > 0 && (
          <ProductGrid
            products={message.products}
            onSelectProduct={onSelectProduct}
          />
        )}

        {/* Grounded Source References */}
        {message.sources && message.sources.length > 0 && (
          <div className="sources-container">
            <span className="sources-label">Sources:</span>
            {message.sources.map((src, idx) => (
              <span key={idx} className="source-pill" title={src.snippet}>
                {src.title}
                {src.score ? ` (${Math.round(src.score * 100)}%)` : ''}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
