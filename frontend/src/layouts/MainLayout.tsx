import { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Box,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
  useMediaQuery,
  Paper,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  List as ListIcon,
  Add as AddIcon,
  Chat as ChatIcon,
  Close as CloseIcon,
  LightMode,
  DarkMode,
  Logout as LogoutIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useThemeMode } from '@/hooks/useThemeMode';
import { useAuth } from '@/hooks/useAuth';

interface MainLayoutProps {
  children: React.ReactNode;
}

const navigationItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Risk List', icon: <ListIcon />, path: '/risks' },
  { text: 'Add Risk', icon: <AddIcon />, path: '/risks/new' },
  { text: 'Risk Chat', icon: <ChatIcon />, path: '/chat' },
];

const DRAWER_WIDTH = 280;

export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const { mode, toggleTheme } = useThemeMode();
  const { logout } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down('lg'));
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleDrawerToggle = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    setDrawerOpen(false); // Always close drawer after navigation
  };

  const handleLogout = async () => {
    setDrawerOpen(false);
    await logout();
  };

  const drawer = (
    <Box sx={{ width: DRAWER_WIDTH, height: '100%' }}>
      {/* Drawer Header */}
      <Box sx={{
        height: 80,
        background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        px: 2,
        position: 'relative'
      }}>
        {isMobile && (
          <IconButton onClick={handleDrawerToggle} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        )}
      </Box>

      {/* Navigation List */}
      <List sx={{ p: 2 }}>
        {navigationItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 1 }}>
              <ListItemButton
                onClick={() => handleNavigate(item.path)}
                sx={{
                  borderRadius: 2,
                  py: 1.5,
                  px: 2,
                  minHeight: 56,
                  backgroundColor: isActive ? 'primary.main' : 'transparent',
                  color: isActive ? 'white' : 'text.primary',
                  '&:hover': {
                    backgroundColor: isActive ? 'primary.dark' : 'action.hover',
                  },
                  transition: 'all 0.2s ease-in-out',
                }}
              >
                <ListItemIcon
                  sx={{
                    minWidth: 40,
                    color: isActive ? 'white' : 'primary.main',
                  }}
                >
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 600 : 400,
                    fontSize: '0.95rem'
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}

        {/* Sign Out Button */}
        <ListItem disablePadding sx={{ mb: 1 }}>
          <ListItemButton
            onClick={handleLogout}
            sx={{
              borderRadius: 2,
              py: 1.5,
              px: 2,
              minHeight: 56,
              backgroundColor: 'transparent',
              color: 'text.primary',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
              transition: 'all 0.2s ease-in-out',
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: 40,
                color: 'error.main',
              }}
            >
              <LogoutIcon />
            </ListItemIcon>
            <ListItemText
              primary="Sign Out"
              primaryTypographyProps={{
                fontWeight: 400,
                fontSize: '0.95rem'
              }}
            />
          </ListItemButton>
        </ListItem>
      </List>

      {/* Footer */}
      <Box sx={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        p: 2,
        borderTop: '1px solid',
        borderColor: 'divider',
        backgroundColor: 'background.paper'
      }}>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
          © 2025 Technology Risk Register
        </Typography>
        <Typography variant="caption" color="text.secondary">
          v1.0.0
        </Typography>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', backgroundColor: 'background.default' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        elevation={1}
        sx={{
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: 'background.paper',
          color: 'text.primary',
          borderBottom: '1px solid',
          borderBottomColor: 'divider',
        }}
      >
        <Toolbar>
          <IconButton
            color="primary"
            aria-label="toggle drawer"
            onClick={handleDrawerToggle}
            edge="start"
            sx={{
              mr: 2,
              '&:hover': {
                backgroundColor: 'primary.light',
                color: 'white'
              }
            }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 600 }}>
            Technology Risk Register
          </Typography>
          <Tooltip title={mode === 'light' ? 'Switch to dark mode' : 'Switch to light mode'}>
            <IconButton
              onClick={toggleTheme}
              color="inherit"
              aria-label="toggle theme"
              sx={{ ml: 'auto' }}
            >
              {mode === 'light' ? <DarkMode /> : <LightMode />}
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Unified Drawer (works for both mobile and desktop) */}
      <Drawer
        variant={isMobile ? 'temporary' : 'temporary'} // Always temporary for cleaner behavior
        anchor="left"
        open={drawerOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better mobile performance
        }}
        PaperProps={{
          elevation: 8,
          sx: {
            width: DRAWER_WIDTH,
            background: theme.palette.mode === 'dark'
              ? `linear-gradient(180deg, ${theme.palette.background.paper} 0%, ${theme.palette.background.default} 100%)`
              : 'linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%)',
            border: 'none',
            position: 'relative',
          }
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Container
          maxWidth="xl"
          sx={{
            flexGrow: 1,
            py: 3,
            px: { xs: 2, sm: 3 } // Responsive padding
          }}
        >
          <Paper
            elevation={0}
            sx={{
              p: { xs: 2, sm: 3 },
              borderRadius: 2,
              backgroundColor: 'background.paper',
              minHeight: 'calc(100vh - 120px)',
              border: '1px solid',
              borderColor: 'divider'
            }}
          >
            {children}
          </Paper>
        </Container>
      </Box>
    </Box>
  );
};
