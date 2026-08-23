import React, { useState } from 'react';
import { useCart } from '../context/CartContext';
import { formatCurrency } from '../utils/formatters';

export default function CheckoutModal({ onClose }) {
  const {
    cart,
    buyNowItem,
    totalPayable,
    totalMrp,
    totalDiscount,
    placeOrder,
    setActiveModal
  } = useCart();

  // Determine items and pricing
  const items = buyNowItem ? [buyNowItem] : cart;
  const orderTotal = buyNowItem ? buyNowItem.product.price * buyNowItem.quantity : totalPayable;
  const orderMrp = buyNowItem ? (buyNowItem.product.mrp || buyNowItem.product.price) * buyNowItem.quantity : totalMrp;
  const orderDiscount = Math.max(0, orderMrp - orderTotal);

  const [step, setStep] = useState('form'); // 'form' | 'success'
  const [placedOrderDetails, setPlacedOrderDetails] = useState(null);

  // Address Form State
  const [formData, setFormData] = useState({
    name: 'Shiva Kumar',
    phone: '9876543210',
    pincode: '560001',
    locality: 'Indiranagar',
    address: '#42, 100ft Road, Near Metro Station',
    city: 'Bengaluru',
    state: 'Karnataka'
  });

  // Payment Method State
  const [paymentMethod, setPaymentMethod] = useState('UPI'); // 'UPI' | 'Card' | 'Netbanking' | 'COD'

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleConfirmOrder = (e) => {
    e.preventDefault();
    if (!formData.name || !formData.phone || !formData.address || !formData.pincode) {
      alert('Please fill out all required delivery address fields.');
      return;
    }

    const order = placeOrder({
      address: formData,
      paymentMethod,
      items,
      totalAmount: orderTotal,
      totalMrp: orderMrp
    });

    setPlacedOrderDetails(order);
    setStep('success');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="checkout-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '1.4rem' }}>{step === 'success' ? '🎉' : '🛍️'}</span>
            <h2 style={{ fontFamily: 'var(--font-heading)', fontSize: '1.25rem' }}>
              {step === 'success' ? 'Order Placed Successfully!' : 'Flipkart Quick Checkout'}
            </h2>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </div>

        {step === 'form' ? (
          <form onSubmit={handleConfirmOrder} className="checkout-form-layout">
            <div className="checkout-main-col">
              {/* Step 1: Delivery Address */}
              <div className="checkout-section">
                <div className="checkout-section-header">
                  <span className="step-num">1</span>
                  <h3>Delivery Address</h3>
                </div>

                <div className="form-grid-2">
                  <div className="form-group">
                    <label>Full Name *</label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>Mobile Number (10 Digits) *</label>
                    <input
                      type="tel"
                      name="phone"
                      value={formData.phone}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-group" style={{ marginTop: '10px' }}>
                  <label>Flat / House No. / Street Address *</label>
                  <input
                    type="text"
                    name="address"
                    value={formData.address}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-grid-3" style={{ marginTop: '10px' }}>
                  <div className="form-group">
                    <label>Pincode *</label>
                    <input
                      type="text"
                      name="pincode"
                      value={formData.pincode}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>City *</label>
                    <input
                      type="text"
                      name="city"
                      value={formData.city}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label>State *</label>
                    <input
                      type="text"
                      name="state"
                      value={formData.state}
                      onChange={handleInputChange}
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Step 2: Payment Method */}
              <div className="checkout-section" style={{ marginTop: '16px' }}>
                <div className="checkout-section-header">
                  <span className="step-num">2</span>
                  <h3>Select Payment Option</h3>
                </div>

                <div className="payment-options-list">
                  <label className={`payment-option-card ${paymentMethod === 'UPI' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === 'UPI'}
                      onChange={() => setPaymentMethod('UPI')}
                    />
                    <div className="payment-opt-info">
                      <span className="payment-opt-title">UPI (Google Pay, PhonePe, Paytm)</span>
                      <span className="payment-opt-desc">Instant payment with 0% extra surcharge</span>
                    </div>
                    <span className="payment-badge">Fastest</span>
                  </label>

                  <label className={`payment-option-card ${paymentMethod === 'Card' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === 'Card'}
                      onChange={() => setPaymentMethod('Card')}
                    />
                    <div className="payment-opt-info">
                      <span className="payment-opt-title">Credit / Debit Card</span>
                      <span className="payment-opt-desc">Visa, MasterCard, RuPay, Amex accepted</span>
                    </div>
                  </label>

                  <label className={`payment-option-card ${paymentMethod === 'Netbanking' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === 'Netbanking'}
                      onChange={() => setPaymentMethod('Netbanking')}
                    />
                    <div className="payment-opt-info">
                      <span className="payment-opt-title">Net Banking</span>
                      <span className="payment-opt-desc">Supported for all 50+ major Indian banks</span>
                    </div>
                  </label>

                  <label className={`payment-option-card ${paymentMethod === 'COD' ? 'selected' : ''}`}>
                    <input
                      type="radio"
                      name="payment"
                      checked={paymentMethod === 'COD'}
                      onChange={() => setPaymentMethod('COD')}
                    />
                    <div className="payment-opt-info">
                      <span className="payment-opt-title">Cash on Delivery (COD)</span>
                      <span className="payment-opt-desc">Pay with cash or QR scan upon delivery</span>
                    </div>
                  </label>
                </div>
              </div>
            </div>

            {/* Right Column: Order Summary */}
            <div className="checkout-summary-col">
              <div className="price-summary-card">
                <h3 className="summary-title">ORDER SUMMARY ({items.length} {items.length === 1 ? 'Product' : 'Products'})</h3>

                <div className="checkout-items-preview">
                  {items.map(({ product, quantity }) => (
                    <div key={product.product_id} className="preview-item-row">
                      <div className="preview-item-text">
                        <span className="preview-name">{product.name}</span>
                        <span className="preview-qty">Qty: {quantity}</span>
                      </div>
                      <span className="preview-price">{formatCurrency(product.price * quantity)}</span>
                    </div>
                  ))}
                </div>

                <div className="summary-divider" />

                <div className="summary-row">
                  <span>Price (MRP)</span>
                  <span>{formatCurrency(orderMrp)}</span>
                </div>

                <div className="summary-row green">
                  <span>Special Discount</span>
                  <span>- {formatCurrency(orderDiscount)}</span>
                </div>

                <div className="summary-row">
                  <span>Delivery</span>
                  <span className="green-text">FREE</span>
                </div>

                <div className="summary-divider" />

                <div className="summary-total-row">
                  <span>Total Payable</span>
                  <span>{formatCurrency(orderTotal)}</span>
                </div>

                <button type="submit" className="btn-confirm-order">
                  <span>Confirm Order ({formatCurrency(orderTotal)})</span>
                  <span>➔</span>
                </button>

                <p className="checkout-safe-badge">
                  🔒 256-bit SSL Encrypted & 100% Safe Checkout
                </p>
              </div>
            </div>
          </form>
        ) : (
          /* Step 2: Success Screen */
          <div className="order-success-view">
            <div className="success-icon-box">✓</div>
            <h3 style={{ fontSize: '1.4rem', fontFamily: 'var(--font-heading)', color: '#34d399', marginBottom: '6px' }}>
              Thank you! Your order is placed.
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '20px' }}>
              Order ID: <code style={{ color: '#818cf8', fontWeight: '700' }}>{placedOrderDetails?.orderId}</code>
            </p>

            <div className="order-info-card">
              <div className="order-info-row">
                <span>Expected Delivery:</span>
                <strong style={{ color: '#38bdf8' }}>{placedOrderDetails?.expectedDelivery}</strong>
              </div>
              <div className="order-info-row">
                <span>Shipping Address:</span>
                <span>{formData.name}, {formData.address}, {formData.city} - {formData.pincode}</span>
              </div>
              <div className="order-info-row">
                <span>Payment Mode:</span>
                <span>{placedOrderDetails?.paymentMethod}</span>
              </div>
              <div className="order-info-row">
                <span>Total Paid:</span>
                <strong style={{ color: '#ffffff' }}>{formatCurrency(placedOrderDetails?.totalAmount)}</strong>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '24px' }}>
              <button
                className="btn-primary"
                onClick={() => {
                  onClose();
                  setActiveModal('orders');
                }}
              >
                View in My Orders
              </button>
              <button
                className="btn-secondary"
                onClick={onClose}
              >
                Continue Shopping
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
