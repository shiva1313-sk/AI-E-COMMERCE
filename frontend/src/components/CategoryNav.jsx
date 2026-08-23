import React from 'react';

const CATEGORIES = [
  { id: 'all', name: 'All Categories', icon: '⚡' },
  { id: 'Smartphones', name: 'Mobiles & 5G', icon: '📱' },
  { id: 'Laptops', name: 'Laptops & PCs', icon: '💻' },
  { id: 'Headphones', name: 'Audio & TWS', icon: '🎧' },
  { id: 'Running Shoes', name: 'Footwear & Shoes', icon: '👟' },
  { id: 'Backpacks', name: 'Bags & Luggage', icon: '🎒' },
  { id: 'Smart Watches', name: 'Smart Wearables', icon: '⌚' },
  { id: 'Keyboards', name: 'Keyboards', icon: '⌨️' },
  { id: 'Mouse', name: 'Gaming & Mouse', icon: '🖱️' },
  { id: 'Office Accessories', name: 'Home & Office', icon: '🖥️' },
  { id: 'College Accessories', name: 'College Tech', icon: '📚' }
];

export default function CategoryNav({ activeCategory, onSelectCategory }) {
  return (
    <nav className="category-nav-bar">
      <div className="category-nav-container">
        {CATEGORIES.map((cat) => {
          const isActive = (activeCategory === null && cat.id === 'all') || (activeCategory === cat.id);
          return (
            <button
              key={cat.id}
              className={`category-item-btn ${isActive ? 'active' : ''}`}
              onClick={() => onSelectCategory(cat.id === 'all' ? null : cat.id)}
            >
              <span className="category-item-icon">{cat.icon}</span>
              <span className="category-item-name">{cat.name}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
