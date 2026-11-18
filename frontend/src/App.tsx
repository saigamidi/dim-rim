/**
 * Main App component with router setup.
 */

import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { RequireAuth } from './components/auth/RequireAuth';
import { LoginPage } from './pages/LoginPage';
import { IntakeCasesPage } from './pages/IntakeCasesPage';
import { ClassificationReviewPage } from './pages/ClassificationReviewPage';
import { VinReviewPage } from './pages/VinReviewPage';
import { AuditTrailPage } from './pages/AuditTrailPage';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <RequireAuth>
                <IntakeCasesPage />
              </RequireAuth>
            }
          />
          <Route
            path="/intake"
            element={
              <RequireAuth>
                <IntakeCasesPage />
              </RequireAuth>
            }
          />
          {/* Classification routes - index redirects to intake */}
          <Route
            path="/classification"
            element={
              <RequireAuth>
                <Navigate to="/intake" replace />
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/classification"
            element={
              <RequireAuth>
                <ClassificationReviewPage />
              </RequireAuth>
            }
          />
          {/* VIN Review routes - index redirects to intake */}
          <Route
            path="/vin-review"
            element={
              <RequireAuth>
                <Navigate to="/intake" replace />
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/vins"
            element={
              <RequireAuth>
                <VinReviewPage />
              </RequireAuth>
            }
          />
          {/* Audit routes - index redirects to intake */}
          <Route
            path="/audit"
            element={
              <RequireAuth>
                <Navigate to="/intake" replace />
              </RequireAuth>
            }
          />
          <Route
            path="/cases/:caseId/audit"
            element={
              <RequireAuth>
                <AuditTrailPage />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
