import React, { useState } from 'react';
import { api } from '../api';

const CATEGORIES = [
  'Food',
  'Transport',
  'Shopping',
  'Salary',
  'Housing',
  'Utilities',
  'Entertainment',
  'Healthcare',
  'Investment',
  'Other',
];

export default function TransactionsTab({
  expenses,
  loading,
  onRefresh,
  search,
  setSearch,
  categoryFilter,
  setCategoryFilter,
  typeFilter,
  setTypeFilter,
  startDate,
  setStartDate,
  endDate,
  setEndDate,
  page,
  setPage,
  pageSize,
}) {
  // Form State
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('Food');
  const [type, setType] = useState('expense');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState(null);
  const [formSuccess, setFormSuccess] = useState(null);

  // Edit Modal State
  const [editingItem, setEditingItem] = useState(null);
  const [editSaving, setEditSaving] = useState(false);
  const [editError, setEditError] = useState(null);

  // Deletion State
  const [deletingId, setDeletingId] = useState(null);

  // Handle Create Transaction
  const handleCreate = async (e) => {
    e.preventDefault();
    setFormError(null);
    setFormSuccess(null);

    const numericAmount = parseFloat(amount);
    if (!title.trim()) {
      setFormError('Please enter a transaction title.');
      return;
    }
    if (isNaN(numericAmount) || numericAmount <= 0) {
      setFormError('Amount must be a positive number greater than 0.');
      return;
    }

    try {
      setSaving(true);
      await api.createExpense({
        title: title.trim(),
        amount: numericAmount,
        category,
        type,
        date: date || undefined,
        notes: notes.trim() || undefined,
      });

      // Clear Form
      setTitle('');
      setAmount('');
      setNotes('');
      setFormSuccess('Transaction saved successfully!');
      setTimeout(() => setFormSuccess(null), 3000);

      await onRefresh();
    } catch (err) {
      setFormError(err.message || 'Failed to save transaction.');
    } finally {
      setSaving(false);
    }
  };

  // Handle Edit Transaction
  const handleOpenEdit = (item) => {
    setEditingItem({
      ...item,
      amount: item.amount.toString(),
    });
    setEditError(null);
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    if (!editingItem) return;
    setEditError(null);

    const numericAmount = parseFloat(editingItem.amount);
    if (!editingItem.title.trim()) {
      setEditError('Title cannot be empty.');
      return;
    }
    if (isNaN(numericAmount) || numericAmount <= 0) {
      setEditError('Amount must be greater than 0.');
      return;
    }

    try {
      setEditSaving(true);
      await api.updateExpense(editingItem.id, {
        title: editingItem.title.trim(),
        amount: numericAmount,
        category: editingItem.category,
        type: editingItem.type,
        date: editingItem.date,
        notes: editingItem.notes?.trim() || null,
      });

      setEditingItem(null);
      await onRefresh();
    } catch (err) {
      setEditError(err.message || 'Could not update transaction.');
    } finally {
      setEditSaving(false);
    }
  };

  // Handle Delete
  const handleDelete = async (id, itemTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${itemTitle}"?`)) {
      return;
    }
    try {
      setDeletingId(id);
      await api.deleteExpense(id);
      await onRefresh();
    } catch (err) {
      alert(`Could not delete: ${err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  // Reset Filters
  const handleClearFilters = () => {
    setSearch('');
    setCategoryFilter('');
    setTypeFilter('');
    setStartDate('');
    setEndDate('');
    setPage(0);
  };

  return (
    <div className="tab-pane">
      <div className="transactions-layout">
        {/* Transaction Entry Form */}
        <div className="form-card">
          <h2 className="section-title">Log Transaction</h2>

          {formError && <div className="error-banner">{formError}</div>}
          {formSuccess && <div className="success-banner">{formSuccess}</div>}

          <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <div>
              <label className="form-label">Title / Description</label>
              <input
                type="text"
                required
                className="form-input"
                placeholder="e.g. Grocery store, Uber, Client payment"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>

            <div style={{ display: 'flex', gap: '0.85rem' }}>
              <div style={{ flex: 1 }}>
                <label className="form-label">Amount (₹)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  required
                  className="form-input"
                  placeholder="0.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>

              <div style={{ flex: 1 }}>
                <label className="form-label">Type</label>
                <select className="form-input" value={type} onChange={(e) => setType(e.target.value)}>
                  <option value="expense">Expense (-)</option>
                  <option value="income">Income (+)</option>
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '0.85rem' }}>
              <div style={{ flex: 1 }}>
                <label className="form-label">Category</label>
                <select className="form-input" value={category} onChange={(e) => setCategory(e.target.value)}>
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div style={{ flex: 1 }}>
                <label className="form-label">Date</label>
                <input
                  type="date"
                  required
                  className="form-input"
                  value={date}
                  onChange={(e) => setDate(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="form-label">Notes (Optional)</label>
              <input
                type="text"
                className="form-input"
                placeholder="Additional details..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </div>

            <button
              type="submit"
              disabled={saving}
              className="btn btn-primary"
              style={{ marginTop: '0.5rem', padding: '12px', fontWeight: 'bold' }}
            >
              {saving ? 'Recording Transaction...' : 'Save Transaction'}
            </button>
          </form>
        </div>

        {/* Filters & Ledger List */}
        <div className="ledger-card">
          <div className="filters-bar">
            <input
              type="text"
              className="form-input search-input"
              placeholder="🔍 Search transactions..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            />

            <select
              className="form-input filter-select"
              value={categoryFilter}
              onChange={(e) => { setCategoryFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Categories</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>

            <select
              className="form-input filter-select"
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(0); }}
            >
              <option value="">All Types</option>
              <option value="expense">Expenses Only</option>
              <option value="income">Income Only</option>
            </select>

            <input
              type="date"
              className="form-input date-input"
              title="Start Date"
              value={startDate}
              onChange={(e) => { setStartDate(e.target.value); setPage(0); }}
            />

            <input
              type="date"
              className="form-input date-input"
              title="End Date"
              value={endDate}
              onChange={(e) => { setEndDate(e.target.value); setPage(0); }}
            />

            {(search || categoryFilter || typeFilter || startDate || endDate) && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleClearFilters}
                style={{ padding: '6px 12px', fontSize: '0.85rem' }}
              >
                Clear
              </button>
            )}
          </div>

          {/* Ledger Table */}
          {loading ? (
            <div className="loading-state">Syncing ledger records...</div>
          ) : expenses.length === 0 ? (
            <div className="empty-state">
              <p style={{ margin: '0 0 8px', fontSize: '1.1rem' }}>No transactions match your current filters.</p>
              <span style={{ fontSize: '0.85rem', color: '#777' }}>
                Try adjusting your search criteria or add a new transaction above.
              </span>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Title & Notes</th>
                    <th>Category</th>
                    <th>Type</th>
                    <th style={{ textAlign: 'right' }}>Amount</th>
                    <th style={{ textAlign: 'center', width: '90px' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {expenses.map((item) => (
                    <tr key={item.id}>
                      <td style={{ color: '#999', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
                        {item.date}
                      </td>
                      <td>
                        <strong style={{ display: 'block', fontSize: '0.95rem' }}>{item.title}</strong>
                        {item.notes && <span style={{ fontSize: '0.8rem', color: '#777' }}>{item.notes}</span>}
                      </td>
                      <td><span className="badge category-badge">{item.category}</span></td>
                      <td>
                        <span className={`badge ${item.type === 'income' ? 'income-badge' : 'expense-badge'}`}>
                          {item.type}
                        </span>
                      </td>
                      <td style={{ textAlign: 'right', fontWeight: 'bold', fontSize: '1rem', color: item.type === 'expense' ? '#ef4444' : '#22c55e' }}>
                        {item.type === 'expense' ? '-' : '+'}₹{Number(item.amount).toFixed(2)}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        <div style={{ display: 'flex', gap: '6px', justifyContent: 'center' }}>
                          <button
                            type="button"
                            className="action-btn edit-action"
                            title="Edit Transaction"
                            onClick={() => handleOpenEdit(item)}
                          >
                            ✎
                          </button>
                          <button
                            type="button"
                            className="action-btn delete-action"
                            title="Delete Transaction"
                            disabled={deletingId === item.id}
                            onClick={() => handleDelete(item.id, item.title)}
                          >
                            {deletingId === item.id ? '…' : '✕'}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination Controls */}
          <div className="pagination-bar">
            <button
              className="btn btn-secondary"
              disabled={page === 0}
              onClick={() => setPage((prev) => Math.max(0, prev - 1))}
            >
              ← Previous
            </button>
            <span style={{ fontSize: '0.85rem', color: '#888' }}>
              Page {page + 1}
            </span>
            <button
              className="btn btn-secondary"
              disabled={expenses.length < pageSize}
              onClick={() => setPage((prev) => prev + 1)}
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* Edit Transaction Modal */}
      {editingItem && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h2 style={{ margin: 0, fontSize: '1.3rem' }}>Edit Transaction</h2>
              <button className="close-btn" onClick={() => setEditingItem(null)}>✕</button>
            </div>

            {editError && <div className="error-banner">{editError}</div>}

            <form onSubmit={handleUpdate} style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              <div>
                <label className="form-label">Title</label>
                <input
                  type="text"
                  required
                  className="form-input"
                  value={editingItem.title}
                  onChange={(e) => setEditingItem({ ...editingItem, title: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.85rem' }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label">Amount (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0.01"
                    required
                    className="form-input"
                    value={editingItem.amount}
                    onChange={(e) => setEditingItem({ ...editingItem, amount: e.target.value })}
                  />
                </div>

                <div style={{ flex: 1 }}>
                  <label className="form-label">Type</label>
                  <select
                    className="form-input"
                    value={editingItem.type}
                    onChange={(e) => setEditingItem({ ...editingItem, type: e.target.value })}
                  >
                    <option value="expense">Expense (-)</option>
                    <option value="income">Income (+)</option>
                  </select>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '0.85rem' }}>
                <div style={{ flex: 1 }}>
                  <label className="form-label">Category</label>
                  <select
                    className="form-input"
                    value={editingItem.category}
                    onChange={(e) => setEditingItem({ ...editingItem, category: e.target.value })}
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>

                <div style={{ flex: 1 }}>
                  <label className="form-label">Date</label>
                  <input
                    type="date"
                    required
                    className="form-input"
                    value={editingItem.date}
                    onChange={(e) => setEditingItem({ ...editingItem, date: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="form-label">Notes</label>
                <input
                  type="text"
                  className="form-input"
                  value={editingItem.notes || ''}
                  onChange={(e) => setEditingItem({ ...editingItem, notes: e.target.value })}
                />
              </div>

              <div style={{ display: 'flex', gap: '0.85rem', marginTop: '0.5rem' }}>
                <button
                  type="button"
                  className="btn btn-secondary"
                  style={{ flex: 1 }}
                  onClick={() => setEditingItem(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={editSaving}
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                >
                  {editSaving ? 'Updating...' : 'Save Changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
