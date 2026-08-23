import React from 'react';
import { useCart } from '../context/CartContext';
import { formatCurrency } from '../utils/formatters';

export default function OrdersModal({ onClose, onOpenSupport }) {
  const { orders } = useCart();

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="orders-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.3rem' }}>📦</span>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem' }}>My Orders</h2>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        {orders.length === 0 ? (
          <div className="empty-cart-view" style={{ padding: '40px 20px' }}>
            <div className="empty-cart-icon">📦</div>
            <h3 style={{ fontSize: '1.15rem', marginBottom: '6px' }}>No Orders Placed Yet</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginBottom: '20px' }}>
              When you buy products, their live tracking status and invoices will appear here.
            </p>
            <button className="btn-primary" onClick={onClose}>
              Start Shopping
            </button>
          </div>
        ) : (
          <div className="orders-list">
            {orders.map((order) => (
              <div key={order.orderId} className="order-card">
                <div className="order-card-header">
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="order-id-badge">{order.orderId}</span>
                      <span className="order-status-pill">{order.status}</span>
                    </div>
                    <span className="order-date-text">
                      Placed on {new Date(order.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                    </span>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <span className="order-total-amount">{formatCurrency(order.totalAmount)}</span>
                    <span className="order-payment-mode">{order.paymentMethod}</span>
                  </div>
                </div>

                <div className="order-items-container">
                  {order.items.map(({ product, quantity }) => (
                    <div key={product.product_id} className="order-item-row">
                      <div className="order-item-details">
                        <span className="order-item-brand">{product.brand}</span>
                        <h4 className="order-item-title">{product.name}</h4>
                        <span className="order-item-meta">
                          Qty: {quantity} • {formatCurrency(product.price)} each
                        </span>
                      </div>
                      <span className="order-item-delivery">
                        🚚 {order.expectedDelivery}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="order-card-footer">
                  <div className="order-tracking-info">
                    <span>Tracking No: <code>{order.trackingNumber}</code></span>
                  </div>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <button
                      className="btn-order-action"
                      onClick={() => {
                        onClose();
                        onOpenSupport();
                      }}
                    >
                      Need Help / Return
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
