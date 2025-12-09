/**
 * Theme context for managing light/dark mode across the application.
 * Follows the same pattern as AuthContext for consistency.
 */

import { createContext, useState, useEffect, useMemo } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider as MuiThemeProvider } from '@mui/material/styles';
import { createAppTheme } from '@/theme';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
  setThemeMode: (mode: ThemeMode) => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeContextProviderProps {
  children: ReactNode;
}

const THEME_STORAGE_KEY = 'theme_mode';

export function ThemeContextProvider({ children }: ThemeContextProviderProps) {
  // Initialize theme mode from localStorage, default to 'light'
  // Use lazy initialization to avoid flash of wrong theme
  const [mode, setMode] = useState<ThemeMode>(() => {
    try {
      const stored = localStorage.getItem(THEME_STORAGE_KEY);
      return stored === 'dark' ? 'dark' : 'light';
    } catch {
      // If localStorage is not available, default to light
      return 'light';
    }
  });

  // Persist theme preference to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(THEME_STORAGE_KEY, mode);
    } catch (error) {
      console.warn('Failed to save theme preference to localStorage:', error);
    }
  }, [mode]);

  // Toggle between light and dark mode
  const toggleTheme = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'));
  };

  // Explicitly set theme mode
  const setThemeMode = (newMode: ThemeMode) => {
    setMode(newMode);
  };

  // Create MUI theme based on current mode
  // Memoize to prevent unnecessary theme recreation
  const theme = useMemo(() => createAppTheme(mode), [mode]);

  const contextValue = useMemo(
    () => ({
      mode,
      toggleTheme,
      setThemeMode,
    }),
    [mode]
  );

  return (
    <ThemeContext.Provider value={contextValue}>
      <MuiThemeProvider theme={theme}>
        {children}
      </MuiThemeProvider>
    </ThemeContext.Provider>
  );
}
