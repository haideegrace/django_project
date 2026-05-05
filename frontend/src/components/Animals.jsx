/**
 * Animals Component - Display and manage animals
 */

import React, { useState } from 'react';
import { useFetch, useDebounce } from '../hooks';
import { animalAPI } from '../services/apiService';
import './Animals.css';

export const Animals = () => {
  const { data: animals, loading, error, refetch } = useFetch('/animals/');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const debouncedSearch = useDebounce(searchTerm, 300);

  // Filter animals
  const filteredAnimals = (animals || []).filter(animal => {
    const matchesSearch = animal.name.toLowerCase().includes(debouncedSearch.toLowerCase());
    const matchesCategory = !selectedCategory || animal.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  // Group by category
  const grouped = filteredAnimals.reduce((acc, animal) => {
    const category = animal.category_display || animal.category;
    if (!acc[category]) acc[category] = [];
    acc[category].push(animal);
    return acc;
  }, {});

  if (loading) return <div className="animals-loading">Loading animals...</div>;
  if (error) return <div className="animals-error">Error: {error.message}</div>;

  return (
    <div className="animals">
      <div className="animals-header">
        <h1>🐔 Animals & Inventory</h1>
        <button onClick={refetch} className="btn-refresh">🔄 Refresh</button>
      </div>

      {/* Search and Filter */}
      <div className="animals-controls">
        <input
          type="text"
          placeholder="Search animals..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="category-select"
        >
          <option value="">All Categories</option>
          <option value="chicken">Chicken</option>
          <option value="duck">Duck</option>
          <option value="goose">Goose</option>
          <option value="turkey">Turkey</option>
          <option value="quail">Quail</option>
          <option value="pigs">Pigs</option>
          <option value="goat">Goat</option>
          <option value="fish">Fish</option>
        </select>
      </div>

      {/* Animals by Category */}
      {Object.entries(grouped).map(([category, categoryAnimals]) => (
        <div key={category} className="animals-category">
          <h2>{category} ({categoryAnimals.length})</h2>
          <div className="animals-grid">
            {categoryAnimals.map(animal => (
              <AnimalCard key={animal.id} animal={animal} onRefresh={refetch} />
            ))}
          </div>
        </div>
      ))}

      {filteredAnimals.length === 0 && (
        <div className="empty-state">
          <p>No animals found</p>
        </div>
      )}
    </div>
  );
};

/**
 * Animal Card Component
 */
const AnimalCard = ({ animal, onRefresh }) => {
  const [showStats, setShowStats] = useState(false);
  const [stats, setStats] = useState(null);

  const handleViewStats = async () => {
    if (!showStats) {
      try {
        const data = await animalAPI.getStatistics(animal.id);
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
      }
    }
    setShowStats(!showStats);
  };

  return (
    <div className="animal-card">
      <div className="card-header">
        <h3>{animal.name}</h3>
        <span className="category-badge">{animal.category_display}</span>
      </div>
      
      <div className="card-body">
        <div className="stat">
          <span className="label">Total Count:</span>
          <span className="value">{animal.total_count}</span>
        </div>
      </div>

      <div className="card-actions">
        <button className="btn btn-small" onClick={handleViewStats}>
          {showStats ? '📊 Hide Stats' : '📊 View Stats'}
        </button>
      </div>

      {showStats && stats && (
        <div className="stats-expanded">
          <div className="stat">
            <span className="label">Today's Eggs:</span>
            <span className="value">{stats.today_eggs}</span>
          </div>
          <div className="stat">
            <span className="label">Weekly Eggs:</span>
            <span className="value">{stats.week_eggs}</span>
          </div>
          <div className="stat">
            <span className="label">Monthly Eggs:</span>
            <span className="value">{stats.month_eggs}</span>
          </div>
          <div className="stat">
            <span className="label">Week Mortality:</span>
            <span className="value">{stats.week_mortality}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Animals;
