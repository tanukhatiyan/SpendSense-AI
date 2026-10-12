import React, { useState, useEffect, useCallback } from 'react';
import { api } from './api';
import Navbar from './components/Navbar';
import DashboardTab from './components/DashboardTab';
import TransactionsTab from './components/TransactionsTab';
import BudgetsTab from './components/BudgetsTab';
import ReportsTab from './components/ReportsTab';
import AuthModal from './components/AuthModal';
import AIChatDrawer from './components/AIChatDrawer';
import './App.css';

export default function App() {
  // Navigation & Modals
  const [activeTab, setActiveTab] = useState('dashboard');
  const [authModalOpen, setAuthModalOpen] = useState(false);
  const [aiDrawerOpen, setAiDrawerOpen] = useState(false);

  // User Authentication
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('spendsense_user');
    return saved ? JSON.parse(saved) : null;
  });

  // Application Data
  const [backendStatus, setBackendStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [totals, setTotals] = useState({
    total_income: 0,
    total_expenses: 0,
    current_balance: 0,
    transaction_count: 0,
  });

  const [summary, setSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [budgets, setBudgets] = useState([]);

  // Periods & Filters
  const [currentMonth, setCurrentMonth] = useState(() => new Date().getMonth() + 1);
  const [currentYear, setCurrentYear] = useState(() => new Date().getFullYear());

  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 15;

  // Master Data Refresh
  const refreshData = useCallback(async () => {
    try {
      setLoading(true);

      const [statusRes, totalsRes, summaryRes, expensesRes, budgetsRes] = await Promise.all([
        api.getStatus().catch(() => null),
        api.getTotals().catch(() => ({ total_income: 0, total_expenses: 0, current_balance: 0, transaction_count: 0 })),
        api.getSummary(startDate || undefined, endDate || undefined).catch(() => null),
        api.getExpenses({
          category: categoryFilter || undefined,
          type: typeFilter || undefined,
          search: search || undefined,
          start_date: startDate || undefined,
          end_date: endDate || undefined,
          skip: page * pageSize,
          limit: pageSize,
        }).catch(() => []),
        api.getBudgets(currentMonth, currentYear).catch(() => []),
      ]);

      if (statusRes) setBackendStatus(statusRes);
      if (totalsRes) setTotals(totalsRes);
      if (summaryRes) setSummary(summaryRes);
      if (expensesRes) setExpenses(expensesRes);
      if (budgetsRes) setBudgets(budgetsRes);

      setError(null);
    } catch (err) {
      setError(err.message || 'Unable to connect to backend.');
    } finally {
      setLoading(false);
    }
  }, [categoryFilter, typeFilter, search, startDate, endDate, page, currentMonth, currentYear]);

  // Initial mount & sync
  useEffect(() => {
    refreshData();
  }, [refreshData]);

  // Sync token expiration and auth state changes
  useEffect(() => {
    const handleAuthChange = () => {
      const savedUser = localStorage.getItem('spendsense_user');
      setUser(savedUser ? JSON.parse(savedUser) : null);
      refreshData();
    };
    window.addEventListener('auth-changed', handleAuthChange);
    return () => window.removeEventListener('auth-changed', handleAuthChange);
  }, [refreshData]);

  const handleLogout = () => {
    localStorage.removeItem('spendsense_token');
    localStorage.removeItem('spendsense_user');
    setUser(null);
    refreshData();
  };

  const handleChangePeriod = (month, year) => {
    setCurrentMonth(month);
    setCurrentYear(year);
  };

  return (
    <div className="app-container">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        user={user}
        onOpenAuth={() => setAuthModalOpen(true)}
        onLogout={handleLogout}
        onOpenAI={() => setAiDrawerOpen(true)}
        backendStatus={backendStatus}
      />

      <main className="main-content">
        {/* Backend Connectivity Status Bar */}
        <div className="system-status-banner">
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: backendStatus ? '#22c55e' : '#ef4444' }}>●</span>
            <span>
              {backendStatus
                ? `${backendStatus.app_name || backendStatus['app name']} v${backendStatus.version} connected`
                : 'Connecting to SpendSense API...'}
            </span>
          </div>
          {user ? (
            <span style={{ color: '#8b5cf6', fontSize: '0.8rem' }}>
              🔒 Authenticated session: {user.email}
            </span>
          ) : (
            <span style={{ color: '#aaa', fontSize: '0.8rem' }}>
              💡 Guest / Local mode active. Sign in to synchronize your private ledger.
            </span>
          )}
        </div>

        {error && <div className="error-banner">{error}</div>}

        {/* Tab Views */}
        {activeTab === 'dashboard' && (
          <DashboardTab
            totals={totals}
            summary={summary}
            recentExpenses={expenses}
            onSwitchToTransactions={() => setActiveTab('transactions')}
          />
        )}

        {activeTab === 'transactions' && (
          <TransactionsTab
            expenses={expenses}
            loading={loading}
            onRefresh={refreshData}
            search={search}
            setSearch={setSearch}
            categoryFilter={categoryFilter}
            setCategoryFilter={setCategoryFilter}
            typeFilter={typeFilter}
            setTypeFilter={setTypeFilter}
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
            page={page}
            setPage={setPage}
            pageSize={pageSize}
          />
        )}

        {activeTab === 'budgets' && (
          <BudgetsTab
            budgets={budgets}
            loading={loading}
            onRefresh={refreshData}
            currentMonth={currentMonth}
            currentYear={currentYear}
            onChangePeriod={handleChangePeriod}
          />
        )}

        {activeTab === 'reports' && (
          <ReportsTab
            summary={summary}
            loading={loading}
            startDate={startDate}
            setStartDate={setStartDate}
            endDate={endDate}
            setEndDate={setEndDate}
            onRefresh={refreshData}
          />
        )}
      </main>

      {/* Authentication Modal */}
      <AuthModal
        isOpen={authModalOpen}
        onClose={() => setAuthModalOpen(false)}
        onAuthSuccess={(authenticatedUser) => {
          setUser(authenticatedUser);
          refreshData();
        }}
      />

      {/* AI Spending Assistant Drawer */}
      <AIChatDrawer
        isOpen={aiDrawerOpen}
        onClose={() => setAiDrawerOpen(false)}
      />
    </div>
  );
}