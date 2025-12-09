import { createTheme, alpha } from '@mui/material/styles';
import { red } from '@mui/material/colors';

// TypeScript module augmentation to add custom chartColors to theme
declare module '@mui/material/styles' {
  interface Theme {
    chartColors: {
      critical: string;
      high: string;
      medium: string;
      low: string;
      mitigate: string;
      accept: string;
      transfer: string;
      avoid: string;
    };
  }
  interface ThemeOptions {
    chartColors?: {
      critical?: string;
      high?: string;
      medium?: string;
      low?: string;
      mitigate?: string;
      accept?: string;
      transfer?: string;
      avoid?: string;
    };
  }
}

/**
 * Create Material-UI theme with support for light and dark modes
 * @param mode - 'light' or 'dark'
 * @returns MUI theme object
 */
export const createAppTheme = (mode: 'light' | 'dark') => {
  const isDark = mode === 'dark';

  return createTheme({
    palette: {
      mode,
      primary: {
        main: isDark ? '#90caf9' : '#1976d2', // Lighter blue for dark mode contrast
      },
      secondary: {
        main: isDark ? '#f48fb1' : '#dc004e', // Lighter pink for dark mode
      },
      error: {
        main: red.A400,
      },
      background: {
        default: isDark ? '#121212' : '#f5f5f5',
        paper: isDark ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      h1: {
        fontSize: '2.5rem',
        fontWeight: 600,
        marginBottom: '1rem',
      },
      h2: {
        fontSize: '2rem',
        fontWeight: 600,
        marginBottom: '0.75rem',
      },
      h3: {
        fontSize: '1.5rem',
        fontWeight: 600,
        marginBottom: '0.5rem',
      },
    },
    // Custom chart colors that adapt to light/dark mode
    chartColors: {
      // Severity levels
      critical: isDark ? '#ef5350' : '#f44336', // Slightly lighter red for dark mode
      high: isDark ? '#ffa726' : '#ff9800',     // Slightly lighter orange for dark mode
      medium: isDark ? '#42a5f5' : '#2196f3',   // Slightly lighter blue for dark mode
      low: isDark ? '#66bb6a' : '#4caf50',      // Slightly lighter green for dark mode
      // Response strategies
      mitigate: isDark ? '#42a5f5' : '#2196f3', // Blue
      accept: isDark ? '#ffa726' : '#ff9800',   // Orange
      transfer: isDark ? '#ab47bc' : '#9c27b0', // Purple
      avoid: isDark ? '#66bb6a' : '#4caf50',    // Green
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: ({ theme }) => ({
            boxShadow: `0 2px 4px ${alpha(theme.palette.common.black, 0.1)}`,
          }),
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: ({ theme }) => ({
            borderRight: `1px solid ${alpha(theme.palette.divider, 0.12)}`,
          }),
        },
      },
      MuiListItemButton: {
        styleOverrides: {
          root: ({ theme }) => ({
            borderRadius: '8px',
            margin: '2px 8px',
            '&.Mui-selected': {
              backgroundColor: alpha(theme.palette.primary.main, 0.12),
              '&:hover': {
                backgroundColor: alpha(theme.palette.primary.main, 0.16),
              },
            },
            '&:hover': {
              backgroundColor: alpha(
                theme.palette.mode === 'dark'
                  ? theme.palette.common.white
                  : theme.palette.common.black,
                0.04
              ),
            },
          }),
        },
      },
      MuiCard: {
        styleOverrides: {
          root: ({ theme }) => ({
            boxShadow: `0 2px 8px ${alpha(theme.palette.common.black, isDark ? 0.3 : 0.1)}`,
            borderRadius: '8px',
          }),
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: '6px',
          },
        },
      },
    },
  });
};

// Export default light theme for backward compatibility (if needed)
export const theme = createAppTheme('light');
