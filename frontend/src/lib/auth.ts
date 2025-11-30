/**
 * Authentication utilities for API communication and token management.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';
const TOKEN_KEY = 'auth_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const USERNAME_KEY = 'auth_username';

// Refresh mutex to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

// Token refresh buffer - refresh 5 minutes before expiry
const TOKEN_REFRESH_BUFFER_MS = 5 * 60 * 1000;

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthToken {
  access_token: string;
  refresh_token: string;
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

  // Store both tokens and username in localStorage
  setToken(data.access_token);
  setRefreshToken(data.refresh_token);
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
 * Refresh the access token using the refresh token.
 * Uses a mutex to prevent multiple simultaneous refresh attempts.
 */
export async function refreshAccessToken(): Promise<string> {
  // If already refreshing, wait for that promise
  if (isRefreshing && refreshPromise) {
    return refreshPromise;
  }

  // Start refresh process
  isRefreshing = true;
  refreshPromise = (async () => {
    try {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token found');
      }

      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) {
        // Refresh token expired or invalid - need to re-login
        clearAuth();
        throw new Error('Refresh token expired');
      }

      const data: { access_token: string; token_type: string } = await response.json();
      setToken(data.access_token);
      return data.access_token;
    } finally {
      // Always reset refresh state
      isRefreshing = false;
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Proactively refresh the token if it's expiring soon.
 * Safe to call repeatedly - uses mutex to prevent multiple refreshes.
 * Returns the current token if no refresh needed.
 */
export async function ensureValidToken(): Promise<string | null> {
  const token = getToken();

  if (!token) {
    return null; // Not authenticated
  }

  if (shouldRefreshToken()) {
    try {
      return await refreshAccessToken();
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Token refresh failed, user needs to re-login
      return null;
    }
  }

  return token; // Token is still valid
}

/**
 * Get stored JWT access token from localStorage.
 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store JWT access token in localStorage.
 */
export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Get stored refresh token from localStorage.
 */
export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

/**
 * Store refresh token in localStorage.
 */
export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
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
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

/**
 * Check if user is authenticated (has token).
 * This does not verify the token is still valid.
 */
export function isAuthenticated(): boolean {
  return getToken() !== null;
}

/**
 * Decode JWT token to extract payload (without verification).
 * Returns null if token is invalid or malformed.
 */
function decodeJWT(token: string): { exp?: number; [key: string]: unknown } | null {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Failed to decode JWT:', error);
    return null;
  }
}

/**
 * Check if a JWT token is expired or about to expire.
 * Returns true if token will expire within the buffer time.
 */
export function isTokenExpiringSoon(token: string): boolean {
  const payload = decodeJWT(token);
  if (!payload || !payload.exp) {
    return true; // Treat invalid tokens as expired
  }

  const expiryTime = payload.exp * 1000; // Convert to milliseconds
  const now = Date.now();
  const timeUntilExpiry = expiryTime - now;

  return timeUntilExpiry <= TOKEN_REFRESH_BUFFER_MS;
}

/**
 * Check if the current access token needs refreshing.
 * Returns true if token is missing, invalid, or expiring soon.
 */
export function shouldRefreshToken(): boolean {
  const token = getToken();
  if (!token) return false; // No token, can't refresh

  return isTokenExpiringSoon(token);
}
