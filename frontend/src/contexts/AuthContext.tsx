/**
 * Authentication context for managing auth state across the application.
 */

import { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { useNavigate } from 'react-router-dom';
import * as authApi from '@/lib/auth';

interface AuthContextType {
  isAuthenticated: boolean;
  username: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Check if user is already authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = authApi.getToken();
      const storedUsername = authApi.getUsername();

      if (token && storedUsername) {
        try {
          // Verify token is still valid
          const result = await authApi.verifyToken();
          setIsAuthenticated(true);
          setUsername(result.username);
        } catch (error) {
          // Token is invalid or expired, clear it
          console.warn('Token verification failed, clearing auth', error);
          authApi.clearAuth();
          setIsAuthenticated(false);
          setUsername(null);
        }
      }

      setLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (username: string, password: string) => {
    try {
      await authApi.login({ username, password });
      setIsAuthenticated(true);
      setUsername(username);
      navigate('/');
    } catch (error) {
      console.error('Login failed', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.warn('Logout endpoint failed', error);
    } finally {
      setIsAuthenticated(false);
      setUsername(null);
      navigate('/login');
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
