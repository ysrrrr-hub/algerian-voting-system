// dashboard/src/pages/LoginPage.tsx

import React, { useState } from 'react';
import {
  Box, Card, CardContent, TextField, Button,
  Typography, Alert, CircularProgress, InputAdornment,
  IconButton,
} from '@mui/material';
import { Lock, Person, Visibility, VisibilityOff } from '@mui/icons-material';
import { apiLogin } from '../services/api';

interface Props { onLogin: (token: string, admin: { full_name: string; role: string }) => void; }

const LoginPage: React.FC<Props> = ({ onLogin }) => {
  const [username, setUsername]   = useState('admin');
  const [password, setPassword]   = useState('');
  const [showPw,   setShowPw]     = useState(false);
  const [loading,  setLoading]    = useState(false);
  const [error,    setError]      = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const { data } = await apiLogin(username, password);
      if (data.success) {
        localStorage.setItem('auth_token', data.token);
        localStorage.setItem('auth_user', data.username);
        localStorage.setItem('auth_expires', String(Date.now() + data.expires_in * 1000));
        onLogin(data.token, { full_name: data.username, role: 'مشرف / Superviseur' });
      }
    } catch (err: any) {
      setError(
        err.response?.data?.error
        || 'خطأ في الاتصال — Erreur de connexion',
      );
    } finally { setLoading(false); }
  };

  return (
    <Box sx={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #004D27 0%, #006233 50%, #1A8C54 100%)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: 'Tajawal, sans-serif',
    }}>
      {/* خلفية زخرفية */}
      <Box sx={{
        position: 'fixed', inset: 0, overflow: 'hidden', pointerEvents: 'none',
      }}>
        {[...Array(3)].map((_, i) => (
          <Box key={i} sx={{
            position: 'absolute',
            width:  [300, 200, 150][i],
            height: [300, 200, 150][i],
            borderRadius: '50%',
            bgcolor: 'rgba(255,255,255,0.04)',
            top:  [`10%`, `60%`, `30%`][i],
            left: [`5%`, `75%`, `50%`][i],
          }} />
        ))}
      </Box>

      <Card sx={{
        width: 420, borderRadius: 4,
        boxShadow: '0 24px 64px rgba(0,0,0,0.3)',
        overflow: 'visible', position: 'relative',
      }}>
        {/* شريط العلم */}
        <Box sx={{ height: 6, display: 'flex', borderRadius: '16px 16px 0 0', overflow: 'hidden' }}>
          <Box sx={{ flex: 1, bgcolor: '#006233' }} />
          <Box sx={{ flex: 1, bgcolor: '#fff' }} />
          <Box sx={{ flex: 1, bgcolor: '#D21034' }} />
        </Box>

        <CardContent sx={{ p: 4 }}>
          {/* رأس */}
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Box sx={{
              width: 72, height: 72, borderRadius: '50%',
              bgcolor: '#006233', mx: 'auto', mb: 2,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              boxShadow: '0 8px 24px rgba(0,98,51,0.3)',
            }}>
              <Lock sx={{ fontSize: 36, color: '#fff' }} />
            </Box>
            <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: '#1A2E1F' }}>
              لوحة المراقبين
            </Typography>
            <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062', mt: 0.5 }}>
              Tableau de bord des superviseurs
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2, fontFamily: 'Tajawal', borderRadius: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              fullWidth required
              label="اسم المستخدم / Nom d'utilisateur"
              value={username}
              onChange={e => setUsername(e.target.value)}
              InputProps={{ startAdornment: (
                <InputAdornment position="start">
                  <Person sx={{ color: '#006233' }} />
                </InputAdornment>
              )}}
              sx={{ mb: 2.5, '& label': { fontFamily: 'Tajawal' } }}
            />
            <TextField
              fullWidth required
              label="كلمة المرور / Mot de passe"
              type={showPw ? 'text' : 'password'}
              value={password}
              onChange={e => setPassword(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Lock sx={{ color: '#006233' }} />
                  </InputAdornment>
                ),
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton onClick={() => setShowPw(v => !v)} edge="end">
                      {showPw ? <VisibilityOff /> : <Visibility />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
              sx={{ mb: 3, '& label': { fontFamily: 'Tajawal' } }}
            />
            <Button
              fullWidth type="submit" variant="contained" size="large"
              disabled={loading || !username || !password}
              sx={{
                bgcolor: '#006233', py: 1.5, borderRadius: 2, fontFamily: 'Tajawal',
                fontSize: 17, fontWeight: 700,
                '&:hover': { bgcolor: '#004D27' },
              }}
            >
              {loading ? <CircularProgress size={24} color="inherit" /> : 'دخول — Connexion'}
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default LoginPage;
