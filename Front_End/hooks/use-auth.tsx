'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { AuthContextType, User } from '@/types/auth';
import { authService } from '@/services';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    let storedToken = localStorage.getItem('auth_token');
    let storedUser = localStorage.getItem('user');

    // Also check sessionStorage if not in localStorage
    if (!storedToken) {
      storedToken = sessionStorage.getItem('auth_token');
      storedUser = sessionStorage.getItem('user');
    }

    if (storedToken && storedUser) {
      setToken(storedToken);
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        // Invalid JSON, clear storage
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
        sessionStorage.removeItem('auth_token');
        sessionStorage.removeItem('user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (username: string, password: string, rememberMe: boolean) => {
    setIsLoading(true);
    try {
      const response = await authService.login({ username, password });

      const token = response.token;
      let user: User;

      if (response.role === 'admin') {
        user = { role: 'admin' };
      } else {
        user = {
          role: 'company',
          company: response.company,
        };
      }

      setToken(token);
      setUser(user);

      if (rememberMe) {
        localStorage.setItem('auth_token', token);
        localStorage.setItem('user', JSON.stringify(user));
      } else {
        sessionStorage.setItem('auth_token', token);
        sessionStorage.setItem('user', JSON.stringify(user));
      }

      if (user.role === 'admin') {
        router.replace('/admin/dashboard');
      } else {
        router.replace('/dashboard');
      }
    } catch (error) {
      throw error;
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  const logout = useCallback(() => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('auth_token');
    sessionStorage.removeItem('user');
    router.replace('/login');
  }, [router]);

  const value: AuthContextType = {
    user,
    token,
    isAuthenticated: !!user && !!token,
    isLoading,
    login,
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
