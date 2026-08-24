import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import defaultProducts from '../data/products.json';

// Local grounded solver for instant response during backend cold starts or connectivity transitions
function resolveLocalFallback(cleanMessage, orders = []) {
  const lower = cleanMessage.toLowerCase().trim();

  // 1. Order Status Queries
  if (
    lower.includes('order') ||
    lower.includes('status') ||
    lower.includes('track') ||
    lower.includes('delivery') ||
    /od\d+|ord\d+/i.test(lower)
  ) {
    if (!orders || orders.length === 0) {
      return {
        text: "You don't have any placed orders in your account yet. You can browse products, add items to your cart, and place an order to track real-time delivery status right here.",
        intent: 'ORDER_STATUS',
        products: [],
        sources: [
          {
            source_type: 'order',
            title: 'Account Order History',
            snippet: '0 active orders found in session.'
          }
        ]
      };
    }

    // Lookup specific order ID
    const idMatch = cleanMessage.match(/\b(?:#|order\s+)?(OD\d+|ORD\d+|\d{6,12})\b/i);
    if (idMatch) {
      const targetId = idMatch[1].toUpperCase();
      const matched = orders.find(o => String(o.orderId || '').toUpperCase().includes(targetId));
      if (matched) {
        const itemNames = (matched.items || []).map(i => i.product?.name).filter(Boolean);
        const itemStr = itemNames.length > 0 ? itemNames.join(', ') : 'your items';
        return {
          text: `Your order #${matched.orderId} for ${itemStr} is currently ${matched.status || 'In Transit'}, with expected delivery ${matched.expectedDelivery || 'in 2-3 business days'}.`,
          intent: 'ORDER_STATUS',
          products: (matched.items || []).map(i => ({
            ...i.product,
            reason: `Order #${matched.orderId} item (${matched.status})`
          })),
          sources: [
            {
              source_type: 'order',
              title: `Order #${matched.orderId}`,
              snippet: `Status: ${matched.status} | Delivery: ${matched.expectedDelivery}`
            }
          ]
        };
      }
    }

    // Default to latest order
    const latest = orders[0];
    const itemNames = (latest.items || []).map(i => i.product?.name).filter(Boolean);
    const itemStr = itemNames.length > 0 ? itemNames.join(', ') : 'your items';
    return {
      text: `Your order #${latest.orderId} for ${itemStr} is currently ${latest.status || 'In Transit'}, with expected delivery ${latest.expectedDelivery || 'in 2-3 business days'}.`,
      intent: 'ORDER_STATUS',
      products: (latest.items || []).map(i => ({
        ...i.product,
        reason: `Order #${latest.orderId} item (${latest.status})`
      })),
      sources: [
        {
          source_type: 'order',
          title: `Order #${latest.orderId}`,
          snippet: `Status: ${latest.status} | Delivery: ${latest.expectedDelivery}`
        }
      ]
    };
  }

  // 2. Policy Queries
  if (lower.includes('return') || lower.includes('replacement') || lower.includes('exchange')) {
    return {
      text: "ShopEase offers a 7-day hassle-free replacement and return policy on eligible electronics and footwear. Items must be in original condition with tags and packaging intact.",
      intent: 'CUSTOMER_SUPPORT',
      products: [],
      sources: [{ source_type: 'policy', title: 'Return & Replacement Policy', snippet: '7-day window for defective/damaged items.' }]
    };
  }

  if (lower.includes('cancel') || lower.includes('cancellation')) {
    return {
      text: "You can cancel your order free of charge anytime before it is dispatched directly from the Orders section in the header.",
      intent: 'CUSTOMER_SUPPORT',
      products: [],
      sources: [{ source_type: 'policy', title: 'Cancellation Policy', snippet: 'Instant cancellation before dispatch with full refund.' }]
    };
  }

  if (lower.includes('shipping') || lower.includes('delivery charge') || lower.includes('shipping cost')) {
    return {
      text: "We offer free express delivery across India on all orders above ₹500. Standard delivery typically takes 2-4 business days.",
      intent: 'CUSTOMER_SUPPORT',
      products: [],
      sources: [{ source_type: 'policy', title: 'Shipping & Delivery Policy', snippet: 'Free delivery above ₹500 | 2-4 business days.' }]
    };
  }

  if (lower.includes('payment') || lower.includes('cod') || lower.includes('upi') || lower.includes('credit card')) {
    return {
      text: "ShopEase supports all major payment methods including UPI (Google Pay, PhonePe, Paytm), Credit/Debit Cards, Net Banking, and Cash on Delivery (COD).",
      intent: 'CUSTOMER_SUPPORT',
      products: [],
      sources: [{ source_type: 'policy', title: 'Payment Policy', snippet: 'Supports UPI, Cards, Net Banking, and COD.' }]
    };
  }

  // 3. Greeting / General Queries
  if (/^(hi|hello|hey|help|good morning|good evening)\b/i.test(lower)) {
    return {
      text: "Hello! I am ShopEase AI Shopping Guide. I can help you search products, compare prices, track your orders, or answer store policy questions.",
      intent: 'GENERAL_QUERY',
      products: [],
      sources: []
    };
  }

  // 4. Product Recommendations from Catalog
  const priceMatch = lower.match(/(?:under|below|less than|upto|budget of)\s*(?:rs\.?|inr|₹)?\s*(\d+)(k)?/i);
  let maxPrice = null;
  if (priceMatch) {
    maxPrice = parseInt(priceMatch[1], 10) * (priceMatch[2] ? 1000 : 1);
  }

  let matchedProducts = defaultProducts.filter(p => {
    if (maxPrice && p.price > maxPrice) return false;
    const text = `${p.name} ${p.brand} ${p.category} ${p.description} ${(p.features || []).join(' ')}`.toLowerCase();
    const words = lower.split(/\s+/).filter(w => w.length > 2 && !['under', 'below', 'show', 'suggest', 'with', 'for', 'the'].includes(w));
    if (words.length === 0) return true;
    return words.some(w => text.includes(w));
  });

  if (matchedProducts.length > 0) {
    const topItems = matchedProducts.slice(0, 4);
    const names = topItems.map(p => p.name).join(', ');
    return {
      text: `Here are our top recommended products matching your request: ${names}.`,
      intent: 'PRODUCT_SEARCH',
      products: topItems.map(p => ({
        ...p,
        reason: `Matches your search criteria (₹${p.price.toLocaleString('en-IN')})`
      })),
      sources: topItems.map(p => ({
        source_type: 'product',
        title: p.name,
        snippet: `Price: ₹${p.price.toLocaleString('en-IN')} | ${p.category}`
      }))
    };
  }

  return {
    text: "I can help only with products, orders, and customer support information available in ShopEase.",
    intent: 'OUT_OF_SCOPE',
    products: [],
    sources: []
  };
}

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [health, setHealth] = useState(null);
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Check backend health on mount and periodically
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
      console.warn('Backend chat API unavailable, engaging grounded client resolver:', err);
      
      // Resolve seamlessly using grounded client logic
      const fallback = resolveLocalFallback(trimmed, orders);

      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: 'assistant',
          text: fallback.text,
          intent: fallback.intent,
          products: fallback.products || [],
          sources: fallback.sources || [],
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
