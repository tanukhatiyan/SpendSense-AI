import React, { useState } from 'react';
import { api } from '../api';

export default function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await api.register({
          email: email.trim(),
          password: password.trim(),
          full_name: fullName.trim() || undefined,
        });
        // Auto login after register
        const tokenRes = await api.login(email.trim(), password.trim());
        localStorage.setItem('spendsense_token', tokenRes.access_token);
        localStorage.setItem('spendsense_user', JSON.stringify(tokenRes.user));
        onAuthSuccess(tokenRes.user);
        onClose();
      } else {
        const tokenRes = await api.login(email.trim(), password.trim());
        localStorage.setItem('spendsense_token', tokenRes.access_token);
        localStorage.setItem('spendsense_user', JSON.stringify(tokenRes.user));
        onAuthSuccess(tokenRes.user);
        onClose();
      }
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.2rem' }}>
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>
            {isRegister ? 'Create Account' : 'Welcome Back'}
          </h2>
          <button className="close-btn" onClick={onClose} aria-label="Close modal">✕</button>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {isRegister && (
            <div>
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="e.g. John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="form-label">Email Address</label>
            <input
              type="email"
              required
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="form-label">Password</label>
            <input
              type="password"
              required
              minLength={6}
              className="form-input"
              placeholder="At least 6 characters"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
            style={{ marginTop: '0.5rem', padding: '12px' }}
          >
            {loading ? 'Processing...' : isRegister ? 'Register & Continue' : 'Sign In'}
          </button>
        </form>

        <div style={{ marginTop: '1.2rem', textAlign: 'center', fontSize: '0.9rem', color: '#888' }}>
          {isRegister ? (
            <span>
              Already have an account?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => { setIsRegister(false); setError(null); }}
              >
                Sign In
              </button>
            </span>
          ) : (
            <span>
              New to SpendSense AI?{' '}
              <button
                type="button"
                className="link-btn"
                onClick={() => { setIsRegister(true); setError(null); }}
              >
                Create an account
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
