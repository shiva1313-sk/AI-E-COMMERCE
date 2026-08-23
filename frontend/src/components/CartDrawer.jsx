import React from 'react';
import { useCart } from '../context/CartContext';
import { formatCurrency, calculateDiscount } from '../utils/formatters';

export default function CartDrawer({ onClose }) {
  const {
    cart,
    totalItems,
    totalPayable,
    totalMrp,
    totalDiscount,
    updateQuantity,
    removeFromCart,
    setActiveModal
  } = useCart();

  const handleProceedToCheckout = () => {
    setActiveModal('checkout');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="cart-drawer-content" onClick={(e) => e.stopPropagation()}>
        <div className="cart-drawer-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div className="cart-header-icon">🛒</div>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontFamily: 'var(--font-heading)' }}>My Cart</h2>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                {totalItems} {totalItems === 1 ? 'item' : 'items'} in your basket
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        {cart.length === 0 ? (
          <div className="empty-cart-view">
            <div className="empty-cart-icon">🛍️</div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '6px' }}>Your Cart is Empty</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '20px' }}>
              Explore our 60+ products and add your favorite tech items!
            </p>
            <button className="btn-primary" onClick={onClose}>
              Continue Shopping
            </button>
          </div>
        ) : (
          <div className="cart-drawer-body">
            {/* Cart Items List */}
            <div className="cart-items-list">
              {cart.map(({ product, quantity }) => {
                const discount = calculateDiscount(product.price, product.mrp);
                return (
                  <div key={product.product_id} className="cart-item-card">
                    <div className="cart-item-info">
                      <div className="cart-item-brand">{product.brand}</div>
                      <h4 className="cart-item-name">{product.name}</h4>
                      
                      <div className="cart-item-pricing">
                        <span className="cart-price-current">
                          {formatCurrency(product.price * quantity)}
                        </span>
                        {product.mrp && product.mrp > product.price && (
                          <>
                            <span className="cart-price-mrp">
                              {formatCurrency(product.mrp * quantity)}
                            </span>
                            {discount > 0 && (
                              <span className="discount-badge">{discount}% OFF</span>
                            )}
                          </>
                        )}
                      </div>

                      <div className="cart-delivery-tag">
                        🚚 {product.delivery_time || 'Free delivery by Tomorrow'}
                      </div>
                    </div>

                    <div className="cart-item-actions">
                      <div className="quantity-stepper">
                        <button
                          className="btn-qty"
                          onClick={() => updateQuantity(product.product_id, -1)}
                          title="Decrease quantity"
                        >
                          -
                        </button>
                        <span className="qty-value">{quantity}</span>
                        <button
                          className="btn-qty"
                          onClick={() => updateQuantity(product.product_id, 1)}
                          title="Increase quantity"
                        >
                          +
                        </button>
                      </div>

                      <button
                        className="btn-remove-cart"
                        onClick={() => removeFromCart(product.product_id)}
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Price Breakdown Card */}
            <div className="price-summary-card">
              <h3 className="summary-title">PRICE DETAILS ({totalItems} Items)</h3>
              
              <div className="summary-row">
                <span>Total MRP</span>
                <span>{formatCurrency(totalMrp)}</span>
              </div>
              
              <div className="summary-row green">
                <span>Discount on MRP</span>
                <span>- {formatCurrency(totalDiscount)}</span>
              </div>

              <div className="summary-row">
                <span>Delivery Charges</span>
                <span className="green-text">FREE</span>
              </div>

              <div className="summary-row">
                <span>Secured Packaging Fee</span>
                <span>FREE</span>
              </div>

              <div className="summary-divider" />

              <div className="summary-total-row">
                <span>Total Amount</span>
                <span>{formatCurrency(totalPayable)}</span>
              </div>

              {totalDiscount > 0 && (
                <div className="savings-banner">
                  🎉 You will save {formatCurrency(totalDiscount)} on this order!
                </div>
              )}

              <button className="btn-place-order" onClick={handleProceedToCheckout}>
                <span>Place Order</span>
                <span>➔</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
