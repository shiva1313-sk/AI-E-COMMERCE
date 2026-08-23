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

// Category mapping helper for instant client-side search
const CATEGORY_KEYWORDS = {
  'phone': 'Smartphones',
  'phones': 'Smartphones',
  'smartphone': 'Smartphones',
  'smartphones': 'Smartphones',
  'mobile': 'Smartphones',
  'mobiles': 'Smartphones',
  'laptop': 'Laptops',
  'laptops': 'Laptops',
  'computer': 'Laptops',
  'headphone': 'Headphones',
  'headphones': 'Headphones',
  'earphone': 'Headphones',
  'earbuds': 'Headphones',
  'shoe': 'Running Shoes',
  'shoes': 'Running Shoes',
  'sneaker': 'Running Shoes',
  'backpack': 'Backpacks',
  'backpacks': 'Backpacks',
  'bag': 'Backpacks',
  'watch': 'Smart Watches',
  'watches': 'Smart Watches',
  'smartwatch': 'Smart Watches',
  'keyboard': 'Keyboards',
  'keyboards': 'Keyboards',
  'mouse': 'Mouse',
  'desk': 'Office Accessories',
  'office': 'Office Accessories',
  'student': 'College Accessories',
  'college': 'College Accessories'
};

function filterLocalCatalog(catalog, query, category) {
  let list = [...catalog];

  // 1. Category filter
  if (category) {
    list = list.filter(p => p.category.toLowerCase() === category.toLowerCase());
  }

  // 2. Query search
  if (query && query.trim()) {
    const cleanQ = query.toLowerCase().trim();

    // Extract price if any
    let maxPrice = null;
    const priceMatch = cleanQ.match(/(?:under|below|less than|upto|budget of)\s*(?:rs\.?|inr|₹)?\s*(\d+)(k)?/i);
    if (priceMatch) {
      maxPrice = parseInt(priceMatch[1], 10) * (priceMatch[2] ? 1000 : 1);
    }

    // Extract category from query words
    let matchedCategory = null;
    for (const [kw, cat] of Object.entries(CATEGORY_KEYWORDS)) {
      if (new RegExp(`\\b${kw}\\b`, 'i').test(cleanQ)) {
        matchedCategory = cat;
        break;
      }
    }

    list = list.filter(p => {
      // Budget check
      if (maxPrice && p.price > maxPrice) return false;

      // If category matched from keyword, prioritize it
      if (matchedCategory && p.category.toLowerCase() === matchedCategory.toLowerCase()) {
        return true;
      }

      // Keyword text matching
      const pText = `${p.name} ${p.brand} ${p.category} ${p.description} ${(p.features || []).join(' ')}`.toLowerCase();
      const words = cleanQ.split(/\s+/).filter(w => w.length > 2 && !['under', 'below', 'show', 'suggest', 'with', 'for', 'the'].includes(w));
      
      if (words.length === 0) return true;
      return words.some(w => pText.includes(w));
    });
  }

  return list;
}

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
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState(null);
  const [sortBy, setSortBy] = useState('popular'); // 'popular' | 'price_low' | 'price_high' | 'rating'
  const [isChatbotOpen, setIsChatbotOpen] = useState(false);
  const [backendProducts, setBackendProducts] = useState(null);

  // Computed instant products (0ms latency, always populated)
  const products = useMemo(() => {
    if (backendProducts && backendProducts.length > 0) {
      return backendProducts;
    }
    return filterLocalCatalog(defaultProducts, searchQuery, activeCategory);
  }, [backendProducts, searchQuery, activeCategory]);

  // Background sync with backend
  useEffect(() => {
    let isMounted = true;

    async function syncBackend() {
      try {
        const filters = {};
        if (activeCategory) filters.category = activeCategory;
        if (searchQuery && searchQuery.trim()) filters.search = searchQuery.trim();

        const res = await api.getProducts(filters);
        if (isMounted && res && res.data) {
          setBackendProducts(res.data);
        }
      } catch (err) {
        // Fallback already rendered seamlessly via useMemo
        if (isMounted) setBackendProducts(null);
      }
    }

    // Reset backend cache on query change so instant local filter renders immediately
    setBackendProducts(null);
    syncBackend();

    return () => {
      isMounted = false;
    };
  }, [searchQuery, activeCategory]);

  // Handle header AI search submit
  const handleHeaderSearch = (query) => {
    setSearchQuery(query);
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

        {sortedProducts.length === 0 ? (
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
