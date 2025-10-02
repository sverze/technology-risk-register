/**
 * Authentication utilities for API communication and token management.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const TOKEN_KEY = 'auth_token';
const USERNAME_KEY = 'auth_username';

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface TokenVerifyResponse {
  valid: boolean;
  username: string;
}

/**
 * Login with username and password.
 * Stores token in localStorage on success.
 */
export async function login(credentials: LoginCredentials): Promise<AuthToken> {
  // Create Basic Auth header
  const basicAuth = btoa(`${credentials.username}:${credentials.password}`);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${basicAuth}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Login failed: ${response.status}`);
  }

  const data: AuthToken = await response.json();

  // Store token and username in localStorage
  setToken(data.access_token);
  setUsername(credentials.username);

  return data;
}

/**
 * Verify the current token is still valid.
 */
export async function verifyToken(): Promise<TokenVerifyResponse> {
  const token = getToken();
  if (!token) {
    throw new Error('No token found');
  }

  const response = await fetch(`${API_BASE_URL}/auth/verify`, {
    method: 'GET',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Token verification failed: ${response.status}`);
  }

  return response.json();
}

/**
 * Logout - clears token from localStorage.
 * Optionally calls the logout endpoint.
 */
export async function logout(): Promise<void> {
  try {
    const token = getToken();
    if (token) {
      // Attempt to call logout endpoint (requires valid token)
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    }
  } catch (error) {
    // Ignore errors, we're logging out anyway
    console.warn('Logout endpoint failed, clearing local token anyway', error);
  } finally {
    // Always clear local storage
    clearAuth();
  }
}

/**
 * Get stored JWT token from localStorage.
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store JWT token in localStorage.
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get stored username from localStorage.
 */
export function getUsername(): string | null {
  return localStorage.getItem(USERNAME_KEY);
}

/**
 * Store username in localStorage.
 */
export function setUsername(username: string): void {
  localStorage.setItem(USERNAME_KEY, username);
}

/**
 * Clear all auth data from localStorage.
 */
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

/**
 * Check if user is authenticated (has token).
 * This does not verify the token is still valid.
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}
