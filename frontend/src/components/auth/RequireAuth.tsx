/**
 * Route guard component requiring authentication.
 * Redirects to login if user is not authenticated.
 */

import { Navigate } from 'react-router-dom';
import { useAuth } from '../../lib/auth-context';

interface RequireAuthProps {
  children: React.ReactNode;
}

export function RequireAuth({ children }: RequireAuthProps) {
  const { user, loading } = useAuth();

  if (loading) {
    // Show loading spinner while checking auth
    return (
      <div className="flex items-center justify-center min-h-screen bg-canvas">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
          <p className="mt-4 text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    // Not authenticated, redirect to login
    return <Navigate to="/login" replace />;
  }

  // Authenticated, render children
  return <>{children}</>;
}
