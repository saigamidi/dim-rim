/**
 * Login page with form matching seed credentials.
 */

import { useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { Radar } from 'lucide-react';
import { useAuth } from '../lib/auth-context';

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  // Default to first seed user credentials
  const [email, setEmail] = useState('disruption.mgr@tmna.com');
  const [password, setPassword] = useState('Manager123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ email, password });
      navigate('/');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-canvas flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="bg-surface border border-line rounded-lg shadow-lg p-8">
          {/* Brand header */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <span className="w-12 h-12 rounded-lg bg-accent flex items-center justify-center">
              <Radar className="w-6 h-6 text-white" />
            </span>
            <div>
              <h1 className="font-head font-bold text-2xl text-ink">Disruption Manager RIM</h1>
              <p className="text-xs text-muted">MVP Demo Environment</p>
            </div>
          </div>

          {/* Login form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-ink-2 mb-2">
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-line rounded focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                placeholder="your.email@tmna.example"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-ink-2 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-line rounded focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
                placeholder="Enter password"
              />
            </div>

            {error && (
              <div className="p-3 bg-err-bg border border-[#D88C87] border-l-4 border-l-err rounded text-sm text-[#5E1411]">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 min-h-[40px] px-4 py-2 rounded bg-accent border border-accent text-white font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-[#1a5277] transition-colors"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* Demo credentials hint */}
          <div className="mt-6 p-4 bg-accent-soft border border-[#9DBFD8] rounded text-sm">
            <p className="font-semibold text-[#12405F] mb-2">Demo Credentials:</p>
            <ul className="text-xs text-ink-2 space-y-1 font-mono">
              <li>Disruption Manager: disruption.mgr@tmna.com / Manager123!</li>
              <li>Event Reviewer: event.reviewer@tmna.com / Reviewer123!</li>
              <li>VIP Comms: vip.comms@tmna.com / Comms123!</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
