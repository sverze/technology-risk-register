/**
 * Custom hook to access theme context.
 * Named useThemeMode to avoid conflict with MUI's useTheme hook.
 * Follows the same pattern as useAuth for consistency.
 */

import { useContext } from 'react';
import { ThemeContext } from '@/contexts/ThemeContext';

export function useThemeMode() {
  const context = useContext(ThemeContext);

  if (context === undefined) {
    throw new Error('useThemeMode must be used within a ThemeContextProvider');
  }

  return context;
}
