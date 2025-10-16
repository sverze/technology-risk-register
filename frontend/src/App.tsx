import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from '@/layouts/MainLayout';
import { Dashboard } from '@/pages/Dashboard';
import { RiskList } from '@/pages/RiskList';
import { AddRisk } from '@/pages/AddRisk';
import { ViewRisk } from '@/pages/ViewRisk';
import { EditRisk } from '@/pages/EditRisk';
import { RiskChat } from '@/pages/RiskChat';
import { Login } from '@/pages/Login';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { Box, CircularProgress } from '@mui/material';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <MainLayout>
              <Dashboard />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/risks"
        element={
          <ProtectedRoute>
            <MainLayout>
              <RiskList />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/risks/new"
        element={
          <ProtectedRoute>
            <MainLayout>
              <AddRisk />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/risks/:riskId"
        element={
          <ProtectedRoute>
            <MainLayout>
              <ViewRisk />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/risks/:riskId/edit"
        element={
          <ProtectedRoute>
            <MainLayout>
              <EditRisk />
            </MainLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <MainLayout>
              <RiskChat />
            </MainLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  );
}

export default App
