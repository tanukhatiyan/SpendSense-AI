import React, { useState } from 'react';
import { api } from '../api';

export default function ReportsTab({ summary, loading, startDate, setStartDate, endDate, setEndDate }) {
  const [exporting, setExporting] = useState(false);
  const [exportError, setExportError] = useState(null);

  const handleExport = async () => {
    try {
      setExporting(true);
      setExportError(null);
      await api.downloadCsv(startDate, endDate);
    } catch (err) {
      setExportError(err.message || 'Export failed.');
    } finally {
      setExporting(false);
    }
  };

  const breakdowns = summary?.category_breakdown || [];

  return (
    <div className="tab-pane">
      {/* Header and Filter */}
      <div className="section-header-bar">
        <div>
          <h2 className="section-title" style={{ margin: 0 }}>Financial Reports & Analytics</h2>
          <p style={{ margin: '4px 0 0', color: '#888', fontSize: '0.85rem' }}>
            Comprehensive overview of category allocations and data export.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input
            type="date"
            className="form-input"
            style={{ width: 'auto' }}
            title="Start Date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <span style={{ color: '#666' }}>to</span>
          <input
            type="date"
            className="form-input"
            style={{ width: 'auto' }}
            title="End Date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <button
            type="button"
            className="btn btn-primary"
            disabled={exporting}
            onClick={handleExport}
          >
            {exporting ? 'Generating...' : '📥 Export CSV'}
          </button>
        </div>
      </div>

      {exportError && <div className="error-banner">{exportError}</div>}

      {/* Summary Highlight */}
      <div className="metrics-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="metric-card">
          <span className="metric-label">Period Income</span>
          <p className="metric-value" style={{ color: '#22c55e' }}>
            ₹{(summary?.total_income || 0).toFixed(2)}
          </p>
        </div>
        <div className="metric-card">
          <span className="metric-label">Period Expenses</span>
          <p className="metric-value" style={{ color: '#ef4444' }}>
            ₹{(summary?.total_expenses || 0).toFixed(2)}
          </p>
        </div>
        <div className="metric-card">
          <span className="metric-label">Net Savings / Deficit</span>
          <p
            className="metric-value"
            style={{ color: (summary?.net_balance || 0) >= 0 ? '#22c55e' : '#ef4444' }}
          >
            ₹{(summary?.net_balance || 0).toFixed(2)}
          </p>
        </div>
        <div className="metric-card">
          <span className="metric-label">Total Transactions</span>
          <p className="metric-value" style={{ color: '#6366f1' }}>
            {summary?.transaction_count || 0}
          </p>
        </div>
      </div>

      {/* Category Breakdown Table */}
      <div className="ledger-card">
        <h3 className="section-title">Category Spending Breakdown</h3>
        {loading ? (
          <div className="loading-state">Aggregating records...</div>
        ) : breakdowns.length === 0 ? (
          <div className="empty-state">No expense records found for the selected period.</div>
        ) : (
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th style={{ textAlign: 'center' }}>Transactions</th>
                  <th style={{ textAlign: 'right' }}>Total Outflow</th>
                  <th style={{ textAlign: 'right' }}>Share of Expenses</th>
                </tr>
              </thead>
              <tbody>
                {breakdowns.map((cat) => (
                  <tr key={cat.category}>
                    <td>
                      <span className="badge category-badge">{cat.category}</span>
                    </td>
                    <td style={{ textAlign: 'center' }}>{cat.count}</td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold', color: '#ef4444' }}>
                      ₹{cat.total.toFixed(2)}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '8px' }}>
                        <span>{cat.percentage}%</span>
                        <div style={{ width: '60px', height: '6px', background: '#333', borderRadius: '3px', overflow: 'hidden' }}>
                          <div style={{ width: `${cat.percentage}%`, height: '100%', background: '#6366f1' }} />
                        </div>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
