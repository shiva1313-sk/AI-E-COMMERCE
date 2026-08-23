import React, { createContext, useContext, useState, useEffect } from 'react';

const CartContext = createContext();

export function CartProvider({ children }) {
  // Cart state persisted in localStorage
  const [cart, setCart] = useState(() => {
    try {
      const saved = localStorage.getItem('shopease_cart');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Orders state persisted in localStorage
  const [orders, setOrders] = useState(() => {
    try {
      const saved = localStorage.getItem('shopease_orders');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  // Active modals: 'cart', 'checkout', 'orders', 'support', 'productDetails'
  const [activeModal, setActiveModal] = useState(null);
  const [modalProduct, setModalProduct] = useState(null);
  const [buyNowItem, setBuyNowItem] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  // Sync cart to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('shopease_cart', JSON.stringify(cart));
    } catch (e) {
      console.error('Failed to save cart to localStorage:', e);
    }
  }, [cart]);

  // Sync orders to localStorage
  useEffect(() => {
    try {
      localStorage.setItem('shopease_orders', JSON.stringify(orders));
    } catch (e) {
      console.error('Failed to save orders to localStorage:', e);
    }
  }, [orders]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 3000);
  };

  const addToCart = (product, quantity = 1) => {
    if (!product || !product.product_id) return;
    
    setCart(prevCart => {
      const existingIndex = prevCart.findIndex(item => item.product.product_id === product.product_id);
      if (existingIndex > -1) {
        const updated = [...prevCart];
        updated[existingIndex].quantity += quantity;
        return updated;
      } else {
        return [...prevCart, { product, quantity }];
      }
    });

    showToast(`Added "${product.name.slice(0, 24)}..." to Cart! 🛒`);
  };

  const removeFromCart = (productId) => {
    setCart(prevCart => prevCart.filter(item => item.product.product_id !== productId));
    showToast('Item removed from cart.');
  };

  const updateQuantity = (productId, delta) => {
    setCart(prevCart => {
      return prevCart
        .map(item => {
          if (item.product.product_id === productId) {
            const newQty = item.quantity + delta;
            return newQty > 0 ? { ...item, quantity: newQty } : null;
          }
          return item;
        })
        .filter(Boolean);
    });
  };

  const clearCart = () => {
    setCart([]);
  };

  const initiateBuyNow = (product) => {
    setBuyNowItem({ product, quantity: 1 });
    setActiveModal('checkout');
  };

  const placeOrder = ({ address, paymentMethod, items, totalAmount, totalMrp }) => {
    const orderId = 'OD' + Math.floor(1000000000 + Math.random() * 9000000000);
    const newOrder = {
      orderId,
      date: new Date().toISOString(),
      items: items || (buyNowItem ? [buyNowItem] : cart),
      totalAmount,
      totalMrp,
      address,
      paymentMethod,
      status: 'Confirmed - Preparing for Dispatch',
      expectedDelivery: 'Arriving in 2-3 Days',
      trackingNumber: 'TRK' + Math.floor(10000000 + Math.random() * 90000000)
    };

    setOrders(prev => [newOrder, ...prev]);

    // If order was placed for entire cart, clear cart
    if (!buyNowItem) {
      clearCart();
    }
    setBuyNowItem(null);

    return newOrder;
  };

  const openProductDetails = (product) => {
    setModalProduct(product);
    setActiveModal('productDetails');
  };

  const closeModal = () => {
    setActiveModal(null);
    setModalProduct(null);
    setBuyNowItem(null);
  };

  // Calculations
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
  const totalPayable = cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0);
  const totalMrp = cart.reduce((sum, item) => sum + ((item.product.mrp || item.product.price) * item.quantity), 0);
  const totalDiscount = Math.max(0, totalMrp - totalPayable);

  return (
    <CartContext.Provider
      value={{
        cart,
        orders,
        activeModal,
        modalProduct,
        buyNowItem,
        toastMessage,
        totalItems,
        totalPayable,
        totalMrp,
        totalDiscount,
        addToCart,
        removeFromCart,
        updateQuantity,
        clearCart,
        initiateBuyNow,
        placeOrder,
        openProductDetails,
        setActiveModal,
        closeModal,
        showToast
      }}
    >
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
}
