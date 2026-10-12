import React, { useState } from 'react';
import { api } from '../api';

const CATEGORIES = [
  'Food',
  'Transport',
  'Shopping',
  'Housing',
  'Utilities',
  'Entertainment',
  'Healthcare',
  'Investment',
  'Other',
];

export default function BudgetsTab({ budgets, loading, onRefresh, currentMonth, currentYear, onChangePeriod }) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [category, setCategory] = useState('Food');
  const [limit, setLimit] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  const handleSaveBudget = async (e) => {
    e.preventDefault();
    setError(null);
    const numLimit = parseFloat(limit);
    if (isNaN(numLimit) || numLimit <= 0) {
      setError('Budget limit must be a positive number.');
      return;
    }

    try {
      setSaving(true);
      await api.saveBudget({
        category,
        monthly_limit: numLimit,
        month: currentMonth,
        year: currentYear,
      });
      setIsModalOpen(false);
      setLimit('');
      await onRefresh();
    } catch (err) {
      setError(err.message || 'Could not save budget.');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteBudget = async (id, cat) => {
    if (!window.confirm(`Delete monthly budget for ${cat}?`)) return;
    try {
      await api.deleteBudget(id);
      await onRefresh();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    }
  };

  return (
    <div className="tab-pane">
      {/* Header & Controls */}
      <div className="section-header-bar">
        <div>
          <h2 className="section-title" style={{ margin: 0 }}>Monthly Category Budgets</h2>
          <p style={{ margin: '4px 0 0', color: '#888', fontSize: '0.85rem' }}>
            Set category limits and track real-time utilization to prevent overspending.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select
            className="form-input"
            style={{ width: 'auto' }}
            value={currentMonth}
            onChange={(e) => onChangePeriod(parseInt(e.target.value, 10), currentYear)}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>
                {new Date(2000, m - 1).toLocaleString('default', { month: 'long' })}
              </option>
            ))}
          </select>

          <select
            className="form-input"
            style={{ width: 'auto' }}
            value={currentYear}
            onChange={(e) => onChangePeriod(currentMonth, parseInt(e.target.value, 10))}
          >
            {[2024, 2025, 2026, 2027].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>

          <button
            type="button"
            className="btn btn-primary"
            onClick={() => { setIsModalOpen(true); setError(null); }}
          >
            + Set Budget
          </button>
        </div>
      </div>

      {/* Budgets Grid */}
      {loading ? (
        <div className="loading-state">Evaluating budget thresholds...</div>
      ) : budgets.length === 0 ? (
        <div className="empty-state">
          <p style={{ margin: '0 0 8px', fontSize: '1.1rem' }}>No budgets configured for this month.</p>
          <span style={{ fontSize: '0.85rem', color: '#777' }}>
            Click &quot;+ Set Budget&quot; to establish spending caps for Food, Transport, or other categories.
          </span>
        </div>
      ) : (
        <div className="budgets-grid">
          {budgets.map((b) => {
            const isExceeded = b.status === 'exceeded';
            const isWarning = b.status === 'warning';
            const progressColor = isExceeded ? '#ef4444' : isWarning ? '#f59e0b' : '#6366f1';

            return (
              <div key={b.id} className="budget-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <h3 style={{ margin: 0, fontSize: '1.15rem' }}>{b.category}</h3>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    {isExceeded && <span className="badge danger-badge">⚠️ Over Budget</span>}
                    {isWarning && <span className="badge warning-badge">⚡ Near Limit</span>}
                    {!isExceeded && !isWarning && <span className="badge normal-badge">✓ On Track</span>}
                    <button
                      type="button"
                      className="close-btn"
                      style={{ fontSize: '0.9rem' }}
                      title="Delete Budget"
                      onClick={() => handleDeleteBudget(b.id, b.category)}
                    >
                      ✕
                    </button>
                  </div>
                </div>

                <div style={{ margin: '1rem 0 0.5rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                  <span style={{ color: '#aaa' }}>
                    Spent: <strong style={{ color: progressColor }}>₹{b.spent.toFixed(2)}</strong>
                  </span>
                  <span style={{ color: '#aaa' }}>
                    Limit: <strong>₹{b.monthly_limit.toFixed(2)}</strong>
                  </span>
                </div>

                {/* Progress Bar */}
                <div className="progress-track">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${Math.min(100, b.percentage)}%`,
                      backgroundColor: progressColor,
                    }}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#888', marginTop: '6px' }}>
                  <span>{b.percentage}% utilized</span>
                  <span>₹{b.remaining.toFixed(2)} remaining</span>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Set Budget Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
              <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Set Category Budget</h2>
              <button className="close-btn" onClick={() => setIsModalOpen(false)}>✕</button>
            </div>

            {error && <div className="error-banner">{error}</div>}

            <form onSubmit={handleSaveBudget} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label className="form-label">Category</label>
                <select
                  className="form-input"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label">Monthly Spending Limit (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="1"
                  required
                  className="form-input"
                  placeholder="e.g. 5000.00"
                  value={limit}
                  onChange={(e) => setLimit(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.85rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                  onClick={() => setIsModalOpen(false)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  {saving ? 'Saving...' : 'Save Budget'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
