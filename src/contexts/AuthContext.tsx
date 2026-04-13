/**
 * Auth Context
 * Global authentication state management
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authAPI } from '@/services/api/apiService';
import type { User, LoginForm, SignupForm } from '@/types/models';
import { logger } from '@/utils/logger';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginForm) => Promise<{ success: boolean; error?: string }>;
  signup: (formData: SignupForm) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state from session
  useEffect(() => {
    const currentUser = authAPI.getCurrentUser();
    setUser(currentUser);
    setIsLoading(false);

    const handleUnauthorized = () => {
      logger.warn('Unauthorized access detected, logging out');
      authAPI.logout().then(() => {
        setUser(null);
        window.location.href = '/login';
      });
    };

    window.addEventListener('auth:unauthorized', handleUnauthorized);
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized);
  }, []);

  const login = async (credentials: LoginForm) => {
    logger.info('Attempting login', { email: credentials.email });

    try {
      const response = await authAPI.login(credentials);

      if (response.success && response.data) {
        setUser(response.data.user);
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Login failed' };
      }
    } catch (error) {
      logger.error('Login error', error as Error);
      return { success: false, error: 'An error occurred during login' };
    }
  };

  const signup = async (formData: SignupForm) => {
    logger.info('Attempting signup', { email: formData.email });

    try {
      const response = await authAPI.signup(formData);

      if (response.success && response.data) {
        setUser(response.data.user);
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Signup failed' };
      }
    } catch (error) {
      logger.error('Signup error', error as Error);
      return { success: false, error: 'An error occurred during signup' };
    }
  };

  const logout = async () => {
    logger.info('Logging out');
    await authAPI.logout();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
