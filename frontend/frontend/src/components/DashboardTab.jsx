import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#14b8a6', '#f97316'];

export default function DashboardTab({ totals, summary, recentExpenses, onSwitchToTransactions }) {
  const balance = totals.current_balance || 0;
  const isPositiveBalance = balance >= 0;

  const monthlyData = (summary?.monthly_trend || []).map((m) => ({
    name: `${m.month}/${m.year}`,
    Income: m.total_income,
    Expenses: m.total_expenses,
  }));

  const categoryPieData = (summary?.category_breakdown || []).map((c) => ({
    name: c.category,
    value: c.total,
  }));

  return (
    <div className="tab-pane">
      {/* Metric Cards */}
      <div className="metrics-grid">
        <div className="metric-card">
          <span className="metric-label">Current Balance</span>
          <p className="metric-value" style={{ color: isPositiveBalance ? '#22c55e' : '#ef4444' }}>
            ₹{balance.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <span style={{ fontSize: '0.8rem', color: isPositiveBalance ? '#4ade80' : '#f87171' }}>
            {isPositiveBalance ? '● Net positive cash flow' : '● Negative deficit'}
          </span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Total Income</span>
          <p className="metric-value" style={{ color: '#22c55e' }}>
            ₹{(totals.total_income || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <span style={{ fontSize: '0.8rem', color: '#888' }}>Total logged revenue</span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Total Expenses</span>
          <p className="metric-value" style={{ color: '#ef4444' }}>
            ₹{(totals.total_expenses || 0).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </p>
          <span style={{ fontSize: '0.8rem', color: '#888' }}>Total outflows recorded</span>
        </div>

        <div className="metric-card">
          <span className="metric-label">Total Transactions</span>
          <p className="metric-value" style={{ color: '#6366f1' }}>
            {totals.transaction_count || 0}
          </p>
          <span style={{ fontSize: '0.8rem', color: '#888' }}>Across all categories</span>
        </div>
      </div>

      {/* Analytics Charts */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3 className="section-title">Monthly Cash Flow Trend</h3>
          {monthlyData.length > 0 ? (
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#888" fontSize={12} />
                  <YAxis stroke="#888" fontSize={12} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e1e1e', borderColor: '#444', borderRadius: '6px' }}
                    formatter={(val) => [`₹${val.toFixed(2)}`, '']}
                  />
                  <Legend />
                  <Bar dataKey="Income" fill="#22c55e" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Expenses" fill="#ef4444" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-chart">No monthly transaction data available yet.</div>
          )}
        </div>

        <div className="chart-card">
          <h3 className="section-title">Expense Distribution</h3>
          {categoryPieData.length > 0 ? (
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={categoryPieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    labelLine={false}
                  >
                    {categoryPieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ backgroundColor: '#1e1e1e', borderColor: '#444', borderRadius: '6px' }}
                    formatter={(val) => [`₹${val.toFixed(2)}`, 'Spent']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="empty-chart">Log an expense to view category distribution.</div>
          )}
        </div>
      </div>

      {/* Recent Ledger Preview */}
      <div className="recent-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h3 className="section-title" style={{ margin: 0 }}>Recent Activity</h3>
          <button className="link-btn" onClick={onSwitchToTransactions}>
            View All Ledger Entries →
          </button>
        </div>

        {recentExpenses.length === 0 ? (
          <p style={{ color: '#888', fontStyle: 'italic', margin: '1rem 0' }}>
            No transactions found. Log your first expense or income!
          </p>
        ) : (
          <div className="table-responsive">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Type</th>
                  <th style={{ textAlign: 'right' }}>Amount</th>
                </tr>
              </thead>
              <tbody>
                {recentExpenses.slice(0, 5).map((item) => (
                  <tr key={item.id}>
                    <td style={{ color: '#999', fontSize: '0.85rem' }}>{item.date}</td>
                    <td><strong>{item.title}</strong></td>
                    <td><span className="badge category-badge">{item.category}</span></td>
                    <td>
                      <span className={`badge ${item.type === 'income' ? 'income-badge' : 'expense-badge'}`}>
                        {item.type}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right', fontWeight: 'bold', color: item.type === 'expense' ? '#ef4444' : '#22c55e' }}>
                      {item.type === 'expense' ? '-' : '+'}₹{Number(item.amount).toFixed(2)}
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
