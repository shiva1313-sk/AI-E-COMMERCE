import React, { useState, useEffect, useMemo, useCallback } from 'react';
import Header from './components/Header';
import CategoryNav from './components/CategoryNav';
import ProductCard from './components/ProductCard';
import ProductDetails from './components/ProductDetails';
import CartDrawer from './components/CartDrawer';
import CheckoutModal from './components/CheckoutModal';
import OrdersModal from './components/OrdersModal';
import ContactSupportModal from './components/ContactSupportModal';
import FloatingChatbot from './components/FloatingChatbot';
import { useChat } from './hooks/useChat';
import { useCart, CartProvider } from './context/CartContext';
import { api } from './services/api';
import defaultProducts from './data/products.json';

function MainAppContent() {
  const {
    messages,
    isLoading,
    health,
    sendMessage,
    clearChat
  } = useChat();

  const {
    orders,
    activeModal,
    modalProduct,
    toastMessage,
    setActiveModal,
    openProductDetails,
    closeModal
  } = useCart();

  // Local state for catalog browsing & filtering
  const [products, setProducts] = useState(defaultProducts || []);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);
  const [activeCategory, setActiveCategory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('popular'); // 'popular' | 'price_low' | 'price_high' | 'rating'
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);

  // Fetch products from backend hybrid search when search query or category changes
  const loadProducts = useCallback(async (query = searchQuery, category = activeCategory) => {
    setIsLoadingProducts(true);
    try {
      const filters = {};
      if (category) filters.category = category;
      if (query && query.trim()) filters.search = query.trim();

      const res = await api.getProducts(filters);
      if (res && res.data) {
        setProducts(res.data);
      }
    } catch (err) {
      console.warn('Backend search unavailable, applying client-side fallback:', err);
      let fallback = [...defaultProducts];
      if (category) {
        fallback = fallback.filter(p => p.category.toLowerCase() === category.toLowerCase());
      }
      if (query && query.trim()) {
        const q = query.toLowerCase().trim();
        fallback = fallback.filter(p =>
          p.name.toLowerCase().includes(q) ||
          p.category.toLowerCase().includes(q) ||
          p.brand.toLowerCase().includes(q) ||
          p.description.toLowerCase().includes(q) ||
          (p.features && p.features.some(f => f.toLowerCase().includes(q)))
        );
      }
      setProducts(fallback);
    } finally {
      setIsLoadingProducts(false);
    }
  }, [searchQuery, activeCategory]);

  // Initial load & category changes
  useEffect(() => {
    loadProducts(searchQuery, activeCategory);
  }, [searchQuery, activeCategory, loadProducts]);

  // Handle header AI search submit
  const handleHeaderSearch = (query) => {
    setSearchQuery(query);
    loadProducts(query, activeCategory);
    if (query && query.trim()) {
      // Also send to AI chatbot session with real user orders context
      sendMessage(query.trim(), orders);
    }
  };

  // Category navigation click
  const handleSelectCategory = (cat) => {
    setActiveCategory(cat);
  };

  // Sorting
  const sortedProducts = useMemo(() => {
    const list = [...products];
    if (sortBy === 'price_low') {
      list.sort((a, b) => a.price - b.price);
    } else if (sortBy === 'price_high') {
      list.sort((a, b) => b.price - a.price);
    } else if (sortBy === 'rating') {
      list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
    }
    return list;
  }, [products, sortBy]);

  return (
    <div className="app-container">
      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="app-toast">
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Flipkart Navigation Header */}
      <Header
        health={health}
        searchQuery={searchQuery}
        onSearch={handleHeaderSearch}
        onOpenCart={() => setActiveModal('cart')}
        onOpenOrders={() => setActiveModal('orders')}
        onOpenSupport={() => setActiveModal('support')}
        onOpenChatbot={() => setIsChatbotOpen(true)}
      />

      {/* Category Navigation Ribbon */}
      <CategoryNav
        activeCategory={activeCategory}
        onSelectCategory={handleSelectCategory}
      />

      {/* Main E-Commerce Product Catalog */}
      <main className="dashboard-main">
        <div className="catalog-header-bar">
          <div className="catalog-title-group">
            <h2>
              {activeCategory ? `${activeCategory}` : searchQuery ? `Search results for "${searchQuery}"` : 'Deals of the Day & Trending Tech'}
            </h2>
            <span className="catalog-count-label">
              Showing {sortedProducts.length} verified products
            </span>
          </div>

          <div className="catalog-sort-group">
            <span className="sort-label">Sort By:</span>
            <select
              className="sort-select"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="popular">Popularity & AI Rank</option>
              <option value="price_low">Price -- Low to High</option>
              <option value="price_high">Price -- High to Low</option>
              <option value="rating">Customer Rating</option>
            </select>
          </div>
        </div>

        {isLoadingProducts ? (
          <div style={{ textAlign: 'center', padding: '60px 0', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '2rem', marginBottom: '10px' }}>⏳</div>
            Searching products with AI hybrid ranking...
          </div>
        ) : sortedProducts.length === 0 ? (
          <div className="empty-cart-view">
            <div className="empty-cart-icon">🔍</div>
            <h3>No products found matching your requirements.</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '8px 0 20px' }}>
              Try adjusting your price filter or searching for another category or requirement.
            </p>
            <button className="btn-primary" onClick={() => { setSearchQuery(''); setActiveCategory(null); }}>
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="flipkart-product-grid">
            {sortedProducts.map(product => (
              <ProductCard
                key={product.product_id}
                item={product}
                onSelectProduct={openProductDetails}
              />
            ))}
          </div>
        )}
      </main>

      {/* Floating Flipkart AI Assistant */}
      <FloatingChatbot
        isOpen={isChatbotOpen}
        onToggle={() => setIsChatbotOpen(!isChatbotOpen)}
        messages={messages}
        isLoading={isLoading}
        onSendMessage={(msg) => sendMessage(msg, orders)}
        onClearChat={clearChat}
        onSelectProduct={openProductDetails}
      />

      {/* Modal Dialogs */}
      {activeModal === 'cart' && (
        <CartDrawer onClose={closeModal} />
      )}

      {activeModal === 'checkout' && (
        <CheckoutModal onClose={closeModal} />
      )}

      {activeModal === 'orders' && (
        <OrdersModal
          onClose={closeModal}
          onOpenSupport={() => setActiveModal('support')}
        />
      )}

      {activeModal === 'support' && (
        <ContactSupportModal
          onClose={closeModal}
          onOpenChatbot={() => {
            closeModal();
            setIsChatbotOpen(true);
          }}
        />
      )}

      {activeModal === 'productDetails' && modalProduct && (
        <ProductDetails
          product={modalProduct}
          onClose={closeModal}
        />
      )}
    </div>
  );
}

export default function App() {
  return (
    <CartProvider>
      <MainAppContent />
    </CartProvider>
  );
}
