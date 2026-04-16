// dashboard/src/App.tsx
// نقطة الدخول الرئيسية للوحة المراقبين

import React, { useState } from 'react';
import { BrowserRouter, Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import {
  AppBar, Box, Button, Chip, CssBaseline,
  ThemeProvider, Toolbar, Tooltip, Typography, createTheme,
  Divider,
} from '@mui/material';
import {
  Dashboard, LockOpen, Logout, Security,
  ManageSearch, AccountTree, BarChart,
} from '@mui/icons-material';

import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import ResultsPage from './pages/ResultsPage';
import AuditLogPage from './pages/AuditLogPage';
import BlockchainExplorerPage from './pages/BlockchainExplorerPage';
import { apiLogout } from './services/api';

// ─── Algerian Theme ───────────────────────────────────────────
const theme = createTheme({
  direction: 'rtl',
  palette: {
    primary:   { main: '#006233' },
    secondary: { main: '#D21034' },
    background: { default: '#F5F7F5' },
  },
  typography: {
    fontFamily: 'Tajawal, Inter, sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: { fontFamily: 'Tajawal, sans-serif', fontWeight: 700, borderRadius: 8 },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: { boxShadow: '0 2px 12px rgba(0,98,51,0.08)' },
      },
    },
  },
});

// ─── Navigation Bar ────────────────────────────────────────────
const NavBar: React.FC<{
  adminName: string;
  role: string;
  onLogout: () => void;
}> = ({ adminName, role, onLogout }) => {
  const loc = useLocation();

  return (
    <AppBar position="sticky" elevation={0} sx={{
      bgcolor: '#fff',
      borderBottom: '1px solid #DDE8DF',
    }}>
      {/* شريط العلم */}
      <Box sx={{ height: 4, display: 'flex' }}>
        <Box sx={{ flex: 1, bgcolor: '#006233' }} />
        <Box sx={{ flex: 1, bgcolor: '#f0f0f0' }} />
        <Box sx={{ flex: 1, bgcolor: '#D21034' }} />
      </Box>

      <Toolbar sx={{ gap: 1, minHeight: '56px !important', px: 3 }}>
        {/* شعار */}
        <Security sx={{ color: '#006233', fontSize: 26 }} />
        <Typography sx={{
          fontFamily: 'Tajawal', fontWeight: 800, fontSize: 15,
          color: '#1A2E1F', flex: 1,
        }}>
          نظام التصويت الإلكتروني 2026
        </Typography>

        {/* روابط التنقل */}
        <Button
          component={Link} to="/"
          startIcon={<Dashboard />}
          variant={loc.pathname === '/' ? 'contained' : 'text'}
          size="small"
          sx={{
            fontFamily: 'Tajawal', fontSize: 13,
            bgcolor: loc.pathname === '/' ? '#006233' : 'transparent',
            color:   loc.pathname === '/' ? '#fff' : '#5A7062',
          }}
        >
          اللوحة
        </Button>

        <Button
          component={Link} to="/results"
          startIcon={<LockOpen />}
          variant={loc.pathname === '/results' ? 'contained' : 'text'}
          size="small"
          sx={{
            fontFamily: 'Tajawal', fontSize: 13,
            bgcolor: loc.pathname === '/results' ? '#D21034' : 'transparent',
            color:   loc.pathname === '/results' ? '#fff' : '#5A7062',
          }}
        >
          النتائج
        </Button>

        <Button
          component={Link} to="/explorer"
          startIcon={<AccountTree />}
          variant={loc.pathname === '/explorer' ? 'contained' : 'text'}
          size="small"
          sx={{
            fontFamily: 'Tajawal', fontSize: 13,
            bgcolor: loc.pathname === '/explorer' ? '#1565C0' : 'transparent',
            color:   loc.pathname === '/explorer' ? '#fff' : '#5A7062',
          }}
        >
          البلوكشين
        </Button>

        <Button
          component={Link} to="/audit"
          startIcon={<ManageSearch />}
          variant={loc.pathname === '/audit' ? 'contained' : 'text'}
          size="small"
          sx={{
            fontFamily: 'Tajawal', fontSize: 13,
            bgcolor: loc.pathname === '/audit' ? '#5A2D9A' : 'transparent',
            color:   loc.pathname === '/audit' ? '#fff' : '#5A7062',
          }}
        >
          السجل
        </Button>

        {/* معلومات المشرف */}
        <Chip
          label={`${adminName} — ${role}`}
          size="small"
          sx={{
            fontFamily: 'Tajawal', fontSize: 11,
            bgcolor: '#E8F5EE', color: '#006233',
            fontWeight: 600, mx: 1,
          }}
        />

        <Tooltip title="تسجيل الخروج / Déconnexion">
          <Button
            onClick={onLogout}
            startIcon={<Logout />}
            color="inherit"
            size="small"
            sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#D21034' }}
          >
            خروج
          </Button>
        </Tooltip>
      </Toolbar>
    </AppBar>
  );
};

// ─── App Root ─────────────────────────────────────────────────
const App: React.FC = () => {
  const [token,     setToken]     = useState<string | null>(null);
  const [adminInfo, setAdminInfo] = useState<{ full_name: string; role: string } | null>(null);

  const handleLogin = (t: string, info: { full_name: string; role: string }) => {
    setToken(t);
    setAdminInfo(info);
  };

  const handleLogout = async () => {
    if (token) {
      try { await apiLogout(token); } catch (_) { /* غير حرج */ }
    }
    setToken(null);
    setAdminInfo(null);
  };

  if (!token || !adminInfo) {
    return (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <LoginPage onLogin={handleLogin} />
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
          <NavBar
            adminName={adminInfo.full_name}
            role={adminInfo.role}
            onLogout={handleLogout}
          />
          <Box sx={{ flex: 1 }}>
            <Routes>
              <Route path="/"         element={<DashboardPage adminName={adminInfo.full_name} />} />
              <Route path="/results"  element={<ResultsPage token={token} />} />
              <Route path="/explorer" element={<BlockchainExplorerPage />} />
              <Route path="/audit"    element={<AuditLogPage token={token} />} />
              <Route path="*"         element={<Navigate to="/" replace />} />
            </Routes>
          </Box>
        </Box>
      </BrowserRouter>
    </ThemeProvider>
  );
};

export default App;
