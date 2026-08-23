import React, { useState } from 'react';
import { useCart } from '../context/CartContext';
import { formatCurrency, calculateDiscount, formatStockStatus } from '../utils/formatters';

export default function ProductDetails({ product, onClose }) {
  const { addToCart, initiateBuyNow } = useCart();
  const [imgError, setImgError] = useState(false);

  if (!product) return null;

  const discount = calculateDiscount(product.price, product.mrp);
  const specs = product.specifications || {};
  const isOutOfStock = product.stock_status === 'out_of_stock';
  const rating = product.rating || 4.5;
  const ratingCount = product.rating_count || 2400;
  const imageUrl = product.image_url;

  const handleBuyNow = () => {
    onClose();
    initiateBuyNow(product);
  };

  const handleAddToCart = () => {
    addToCart(product);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content product-details-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '6px' }}>
              <span className="product-brand">{product.brand}</span>
              <span className={`stock-pill ${product.stock_status}`}>
                {formatStockStatus(product.stock_status)}
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                ID: <code>{product.product_id}</code>
              </span>
            </div>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.3rem' }}>
              {product.name}
            </h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
              <span className="rating-pill">{rating.toFixed(1)} ★</span>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {ratingCount.toLocaleString('en-IN')} Customer Ratings
              </span>
              <span className="assured-badge">✦ Flipkart Assured Quality</span>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            ✕
          </button>
        </div>

        {/* Modal Body with Product Image & Details */}
        <div className="modal-product-layout">
          {imageUrl && !imgError && (
            <div className="modal-product-image-box">
              <img
                src={imageUrl}
                alt={product.name}
                className="modal-hero-image"
                onError={() => setImgError(true)}
              />
            </div>
          )}

          <div className="modal-product-content-col">
            {/* Pricing & Offer */}
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '16px' }}>
              <span style={{ fontSize: '1.6rem', fontWeight: '700', color: '#ffffff' }}>
                {formatCurrency(product.price)}
              </span>
              {product.mrp && product.mrp > product.price && (
                <>
                  <span className="price-mrp" style={{ fontSize: '1.05rem' }}>
                    {formatCurrency(product.mrp)}
                  </span>
                  {discount > 0 && <span className="discount-badge">{discount}% OFF</span>}
                </>
              )}
              <span style={{ fontSize: '0.82rem', color: '#38bdf8', marginLeft: 'auto' }}>
                🚚 {product.delivery_time || 'Free delivery by Tomorrow'}
              </span>
            </div>

            {/* CTA Buttons in Modal */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
              <button
                className="btn-card-cart"
                style={{ padding: '12px', fontSize: '0.9rem' }}
                onClick={handleAddToCart}
                disabled={isOutOfStock}
              >
                🛒 Add to Cart
              </button>
              <button
                className="btn-card-buynow"
                style={{ padding: '12px', fontSize: '0.9rem' }}
                onClick={handleBuyNow}
                disabled={isOutOfStock}
              >
                ⚡ Buy Now
              </button>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <h4 style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '6px' }}>
                Product Overview
              </h4>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: '1.6' }}>
                {product.description}
              </p>
            </div>

            {product.features && product.features.length > 0 && (
              <div style={{ marginBottom: '20px' }}>
                <h4 style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Key Features & Highlights
                </h4>
                <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  {product.features.map((feat, idx) => (
                    <li key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '0.86rem', color: '#cbd5e1' }}>
                      <span style={{ color: 'var(--accent-emerald)', marginTop: '2px' }}>✓</span>
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {Object.keys(specs).length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <h4 style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
              Complete Technical Specifications
            </h4>
            <div className="spec-grid">
              {Object.entries(specs).map(([key, val]) => (
                <div key={key} className="spec-item">
                  <div className="spec-key">{key}</div>
                  <div className="spec-val">{val}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div style={{ marginTop: '24px', display: 'flex', justifyContent: 'flex-end' }}>
          <button
            className="btn-secondary"
            onClick={onClose}
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
