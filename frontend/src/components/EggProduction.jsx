/**
 * Egg Production Component - Display and record egg production
 */

import React, { useState, useEffect } from 'react';
import { useFetch, usePost, usePoll } from '../hooks';
import { eggProductionAPI, animalAPI } from '../services/apiService';
import './EggProduction.css';

export const EggProduction = () => {
  const { data: productions, loading, error, refetch } = useFetch('/egg-production/');
  const { data: animals } = useFetch('/animals/');
  const { post: postProduction, loading: posting } = usePost();
  
  // Poll for weekly summary
  const { data: weeklySummary } = usePoll(
    () => eggProductionAPI.getWeeklySummary(),
    5000,
    true
  );

  const [formData, setFormData] = useState({
    animal: '',
    quantity: '',
    date: new Date().toISOString().split('T')[0],
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await postProduction('/egg-production/', formData);
      setFormData({
        animal: '',
        quantity: '',
        date: new Date().toISOString().split('T')[0],
      });
      refetch();
      alert('Egg production recorded successfully!');
    } catch (error) {
      alert('Error recording egg production');
    }
  };

  if (loading) return <div className="egg-loading">Loading egg production data...</div>;

  return (
    <div className="egg-production">
      <div className="header">
        <h1>🥚 Egg Production</h1>
      </div>

      {/* Record Form */}
      <div className="record-form-container">
        <h2>Record Egg Production</h2>
        <form onSubmit={handleSubmit} className="record-form">
          <div className="form-group">
            <label>Animal</label>
            <select
              value={formData.animal}
              onChange={(e) => setFormData({ ...formData, animal: e.target.value })}
              required
              className="form-input"
            >
              <option value="">Select an animal</option>
              {animals?.map(animal => (
                <option key={animal.id} value={animal.id}>
                  {animal.name} ({animal.category_display})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label>Quantity</label>
            <input
              type="number"
              min="0"
              value={formData.quantity}
              onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
              required
              placeholder="0"
              className="form-input"
            />
          </div>

          <div className="form-group">
            <label>Date</label>
            <input
              type="date"
              value={formData.date}
              onChange={(e) => setFormData({ ...formData, date: e.target.value })}
              required
              className="form-input"
            />
          </div>

          <button
            type="submit"
            disabled={posting}
            className="btn btn-primary"
          >
            {posting ? 'Recording...' : 'Record Production'}
          </button>
        </form>
      </div>

      {/* Weekly Summary */}
      {weeklySummary && weeklySummary.length > 0 && (
        <div className="summary-container">
          <h2>Weekly Summary</h2>
          <div className="weekly-chart">
            {weeklySummary.map((day) => (
              <div key={day.date} className="day-bar">
                <div className="bar" style={{ height: `${Math.min(day.total * 5, 200)}px` }}>
                  {day.total}
                </div>
                <div className="date">{new Date(day.date).toLocaleDateString('en-US', { weekday: 'short' })}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Productions */}
      <div className="productions-container">
        <h2>Recent Production Records</h2>
        <div className="productions-list">
          {productions && productions.length > 0 ? (
            productions.slice(0, 20).map(production => (
              <ProductionItem key={production.id} production={production} />
            ))
          ) : (
            <p className="empty-message">No production records yet</p>
          )}
        </div>
      </div>

      <button onClick={refetch} className="btn-refresh">🔄 Refresh</button>
    </div>
  );
};

/**
 * Production Item Component
 */
const ProductionItem = ({ production }) => {
  return (
    <div className="production-item">
      <div className="item-left">
        <strong>{production.animal_name}</strong>
        <span className="date">{production.date}</span>
      </div>
      <div className="item-middle">
        <span className="quantity">{production.quantity} eggs</span>
        <span className="remaining">Remaining: {production.remaining_stock}</span>
      </div>
      <div className="item-right">
        <span className="collected-by">by {production.collected_by_username || 'System'}</span>
      </div>
    </div>
  );
};

export default EggProduction;
