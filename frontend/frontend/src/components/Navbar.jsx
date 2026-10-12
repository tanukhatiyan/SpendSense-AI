import React from 'react';

export default function Navbar({
  activeTab,
  setActiveTab,
  user,
  onOpenAuth,
  onLogout,
  onOpenAI,
  backendStatus,
}) {
  return (
    <header className="navbar-container">
      <div className="navbar-inner">
        {/* Brand */}
        <div className="navbar-brand" onClick={() => setActiveTab('dashboard')} style={{ cursor: 'pointer' }}>
          <span className="brand-icon">✨</span>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <h1 className="brand-title">SpendSense AI</h1>
              {backendStatus && (
                <span style={{ fontSize: '0.65rem', background: '#1e293b', color: '#38bdf8', padding: '2px 6px', borderRadius: '4px' }}>
                  v{backendStatus.version}
                </span>
              )}
            </div>
            <span className="brand-sub">Smart Expense & Finance Management</span>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="nav-tabs">
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'transactions' ? 'active' : ''}`}
            onClick={() => setActiveTab('transactions')}
          >
            💳 Transactions
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'budgets' ? 'active' : ''}`}
            onClick={() => setActiveTab('budgets')}
          >
            🎯 Budgets
          </button>
          <button
            type="button"
            className={`nav-tab-btn ${activeTab === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveTab('reports')}
          >
            📈 Reports
          </button>
        </nav>

        {/* Right Actions */}
        <div className="navbar-actions">
          {/* AI Trigger */}
          <button
            type="button"
            className="ai-trigger-btn"
            onClick={onOpenAI}
            title="Open AI Spending Assistant"
          >
            🤖 AI Assistant
          </button>

          {/* User Auth */}
          {user ? (
            <div className="user-profile-box">
              <span className="user-name" title={user.email}>
                👤 {user.full_name || user.email.split('@')[0]}
              </span>
              <button
                type="button"
                className="btn btn-secondary"
                style={{ padding: '6px 10px', fontSize: '0.8rem' }}
                onClick={onLogout}
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="btn btn-primary"
              style={{ padding: '8px 14px', fontSize: '0.85rem' }}
              onClick={onOpenAuth}
            >
              Sign In / Register
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
