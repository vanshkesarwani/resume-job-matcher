import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => {
    try {
      return localStorage.getItem('authToken') || null;
    } catch {
      return null;
    }
  });

  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('authUser');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState(true);

  // Validate existing token with /auth/me on mount
  useEffect(() => {
    const checkAuth = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/auth/me', {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          localStorage.setItem('authUser', JSON.stringify(userData));
        } else {
          // Token expired or invalid
          logout();
        }
      } catch (err) {
        console.warn('Auth verification network note:', err);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [token]);

  const login = async (email, password) => {
    const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to sign in. Please check your credentials.');
    }

    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('authUser', JSON.stringify(data.user));
    return data;
  };

  const signup = async (name, email, password) => {
    const response = await fetch('http://127.0.0.1:8000/api/v1/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || 'Failed to create account. Please try again.');
    }

    setToken(data.access_token);
    setUser(data.user);
    localStorage.setItem('authToken', data.access_token);
    localStorage.setItem('authUser', JSON.stringify(data.user));
    return data;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    try {
      localStorage.removeItem('authToken');
      localStorage.removeItem('authUser');
    } catch {
      // Ignored
    }
  };

  const getAuthHeaders = () => {
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const value = {
    user,
    token,
    isLoading,
    isAuthenticated: Boolean(token && user),
    login,
    signup,
    logout,
    getAuthHeaders,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

