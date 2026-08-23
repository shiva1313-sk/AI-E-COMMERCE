import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Check backend health on mount
  useEffect(() => {
    async function fetchHealth() {
      try {
        const data = await api.checkHealth();
        setHealth(data);
      } catch (err) {
        setHealth({ status: 'offline', error: err.message });
      }
    }
    fetchHealth();
    const interval = setInterval(fetchHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const sendMessage = useCallback(async (text, orders = []) => {
    if (!text || !text.trim() || isLoading) return;

    const trimmed = text.trim();
    const userMsgId = Date.now().toString();
    
    // Add user message
    setMessages(prev => [
      ...prev,
      {
        id: userMsgId,
        sender: 'user',
        text: trimmed,
        timestamp: new Date()
      }
    ]);

    setIsLoading(true);
    setError(null);

    try {
      const response = await api.sendChatMessage(trimmed, conversationId, orders);
      
      if (response.conversation_id && !conversationId) {
        setConversationId(response.conversation_id);
      }

      // Add assistant response
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: response.message,
          intent: response.intent,
          products: response.products || [],
          sources: response.sources || [],
          timestamp: new Date()
        }
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      setError(err.message || 'Failed to receive response from server.');
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          isError: true,
          text: 'Sorry, I encountered an issue communicating with the server. Please check that the backend is running and try again.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [conversationId, isLoading]);

  const clearChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    health,
    selectedProduct,
    setSelectedProduct,
    sendMessage,
    clearChat
  };
}
