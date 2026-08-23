import React from 'react';
import ProductCard from './ProductCard';

export default function ProductGrid({ products, onSelectProduct }) {
  if (!products || products.length === 0) return null;

  return (
    <div className="product-grid-container">
      {products.map((item, index) => (
        <ProductCard
          key={item.product_id || index}
          item={item}
          onSelectProduct={onSelectProduct}
        />
      ))}
    </div>
  );
}
