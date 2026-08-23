import React, { useState } from 'react';
import { useCart } from '../context/CartContext';
import { formatCurrency, calculateDiscount, formatStockStatus } from '../utils/formatters';

export default function ProductCard({ item, onSelectProduct }) {
  const { addToCart, initiateBuyNow } = useCart();
  const [imgError, setImgError] = useState(false);

  const details = item.product_details || item;
  const discount = calculateDiscount(item.price, details.mrp);
  const stock = item.stock_status || details.stock_status || 'in_stock';
  const rating = details.rating || 4.4;
  const ratingCount = details.rating_count || 1250;
  const isOutOfStock = stock === 'out_of_stock';
  const imageUrl = details.image_url || item.image_url;

  return (
    <div className="flipkart-product-card">
      {/* Product Image Media Container */}
      <div className="card-image-container" onClick={() => onSelectProduct(details)}>
        {imageUrl && !imgError ? (
          <img
            src={imageUrl}
            alt={item.name}
            className="card-product-image"
            loading="lazy"
            onError={() => setImgError(true)}
          />
        ) : (
          <div className="card-image-fallback">
            <span className="fallback-category-icon">📦</span>
            <span className="fallback-category-name">{details.category || 'Tech'}</span>
          </div>
        )}

        {/* Top Floating Badge on Image */}
        {details.badge && (
          <span className="card-custom-badge floating">{details.badge}</span>
        )}
      </div>

      {/* Brand & Stock Header */}
      <div className="card-top-badges">
        <span className="card-brand-tag">{item.brand || details.brand}</span>
        <span className={`stock-pill ${stock}`}>
          {formatStockStatus(stock)}
        </span>
      </div>

      {/* Product Title */}
      <h3
        className="card-product-title"
        onClick={() => onSelectProduct(details)}
        title={item.name}
      >
        {item.name}
      </h3>

      {/* Ratings & Assured */}
      <div className="card-rating-row">
        <span className="rating-pill">
          {rating.toFixed(1)} ★
        </span>
        <span className="rating-count-text">
          ({ratingCount.toLocaleString('en-IN')})
        </span>
        <span className="assured-badge">✦ Assured</span>
      </div>

      {/* Pricing Section */}
      <div className="card-price-section">
        <div className="price-main-line">
          <span className="price-current">{formatCurrency(item.price)}</span>
          {details.mrp && details.mrp > item.price && (
            <>
              <span className="price-mrp">{formatCurrency(details.mrp)}</span>
              {discount > 0 && <span className="discount-tag">{discount}% off</span>}
            </>
          )}
        </div>
        <div className="delivery-promise-text">
          🚚 {details.delivery_time || 'Free delivery by Tomorrow'}
        </div>
      </div>

      {/* AI Recommendation Reason if provided */}
      {item.reason && (
        <div className="card-ai-reason">
          <span className="reason-label">✨ Why AI Recommended</span>
          <p className="reason-text">{item.reason}</p>
        </div>
      )}

      {/* Key Highlights */}
      {details.features && details.features.length > 0 && (
        <ul className="card-features-preview">
          {details.features.slice(0, 2).map((feat, idx) => (
            <li key={idx}>• {feat}</li>
          ))}
        </ul>
      )}

      {/* Action Buttons */}
      <div className="card-actions-group">
        <button
          className="btn-card-cart"
          onClick={() => addToCart(details)}
          disabled={isOutOfStock}
          title="Add to Basket"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="9" cy="21" r="1"/>
            <circle cx="20" cy="21" r="1"/>
            <path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"/>
          </svg>
          Add to Cart
        </button>

        <button
          className="btn-card-buynow"
          onClick={() => initiateBuyNow(details)}
          disabled={isOutOfStock}
          title="Buy Immediately"
        >
          ⚡ Buy Now
        </button>
      </div>

      <button
        className="btn-card-specs-link"
        onClick={() => onSelectProduct(details)}
      >
        View Full Specifications ➔
      </button>
    </div>
  );
}
