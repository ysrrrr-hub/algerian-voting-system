// dashboard/src/pages/ResultsPage.tsx
// صفحة فك تشفير وعرض النتائج — للمشرفين بعد انتهاء الانتخابات

import React, { useState } from 'react';
import {
  Alert, Box, Button, Card, CardContent, CircularProgress,
  InputAdornment, IconButton, LinearProgress,
  TextField, Typography,
} from '@mui/material';
import { LockOpen, Visibility, VisibilityOff, EmojiEvents } from '@mui/icons-material';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiDecryptVotes, DecryptResult } from '../services/api';

interface Props { token: string; }

const COLORS = ['#006233', '#D21034', '#D4A017', '#1565C0', '#7B1FA2'];

const ResultsPage: React.FC<Props> = ({ token }) => {
  const [password, setPassword] = useState('');
  const [showPw,   setShowPw]   = useState(false);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState('');
  const [results,  setResults]  = useState<DecryptResult[] | null>(null);
  const [total,    setTotal]    = useState(0);

  const handleDecrypt = async () => {
    setLoading(true); setError('');
    try {
      const { data } = await apiDecryptVotes(token, password);
      if (data.success) { setResults(data.results); setTotal(data.total_votes); }
    } catch (err: any) {
      setError(err.response?.data?.error_ar || 'فشل فك التشفير');
    } finally { setLoading(false); }
  };

  const pieData = results?.map(r => ({ name: r.name_ar, value: r.votes })) ?? [];

  return (
    <Box sx={{ p: 3, bgcolor: '#F5F7F5', minHeight: '100%' }}>
      <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, mb: 3, color: '#1A2E1F' }}>
        🗳️ فك تشفير النتائج / Déchiffrement des résultats
      </Typography>

      {!results ? (
        /* ─── نموذج فك التشفير ──────────────────────────────── */
        <Box sx={{ maxWidth: 520, mx: 'auto' }}>
          <Card sx={{ borderRadius: 3 }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Box sx={{
                  width: 80, height: 80, borderRadius: '50%',
                  bgcolor: '#E8F5EE', mx: 'auto', mb: 2,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <LockOpen sx={{ fontSize: 40, color: '#006233' }} />
                </Box>
                <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 18 }}>
                  أدخل كلمة مرور المفتاح الخاص
                </Typography>
                <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062', mt: 0.5 }}>
                  Entrez le mot de passe de la clé privée RSA-4096
                </Typography>
              </Box>

              {error && <Alert severity="error" sx={{ mb: 2, fontFamily: 'Tajawal' }}>{error}</Alert>}

              <TextField
                fullWidth type={showPw ? 'text' : 'password'}
                label="كلمة مرور المفتاح الخاص"
                value={password}
                onChange={e => setPassword(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && password && handleDecrypt()}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton onClick={() => setShowPw(v => !v)}>
                        {showPw ? <VisibilityOff /> : <Visibility />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
                sx={{ mb: 3, '& label': { fontFamily: 'Tajawal' } }}
              />

              <Alert severity="warning" sx={{ mb: 3, fontFamily: 'Tajawal', fontSize: 12 }}>
                ⚠️ هذه العملية لا رجوع عنها. تأكد من انتهاء فترة التصويت قبل المتابعة.
              </Alert>

              <Button
                fullWidth variant="contained" size="large"
                disabled={loading || !password}
                onClick={handleDecrypt}
                sx={{
                  bgcolor: '#D21034', py: 1.5, borderRadius: 2,
                  fontFamily: 'Tajawal', fontSize: 16, fontWeight: 700,
                  '&:hover': { bgcolor: '#A00D27' },
                }}
              >
                {loading
                  ? <CircularProgress size={24} color="inherit" />
                  : '🔓 فك تشفير النتائج / Déchiffrer'}
              </Button>
            </CardContent>
          </Card>
        </Box>
      ) : (
        /* ─── عرض النتائج ───────────────────────────────────── */
        <Box>
          <Alert severity="success" sx={{ mb: 3, fontFamily: 'Tajawal', fontSize: 14, borderRadius: 2 }}>
            ✅ تم فك تشفير <strong>{total.toLocaleString()}</strong> صوت بنجاح |
            {total.toLocaleString()} votes déchiffrés avec succès
          </Alert>

          <Box sx={{ display: 'grid', gridTemplateColumns: { md: '1fr 1fr' }, gap: 3 }}>
            {/* قائمة النتائج */}
            <Box>
              {results.map((r, i) => (
                <Card key={r.candidate_id} sx={{ mb: 2, borderRadius: 3, overflow: 'hidden' }}>
                  <Box sx={{ height: 4, bgcolor: COLORS[i % COLORS.length] }} />
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1.5 }}>
                      {/* رتبة */}
                      <Box sx={{
                        width: 40, height: 40, borderRadius: '50%',
                        bgcolor: COLORS[i % COLORS.length],
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        flexShrink: 0,
                      }}>
                        {i === 0 ? <EmojiEvents sx={{ color: '#fff', fontSize: 20 }} />
                          : <Typography sx={{ color: '#fff', fontWeight: 800, fontSize: 16 }}>{i + 1}</Typography>}
                      </Box>

                      <Box sx={{ flex: 1, minWidth: 0 }}>
                        <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 15, color: '#1A2E1F' }}>
                          {r.name_ar}
                        </Typography>
                        <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#5A7062', fontStyle: 'italic' }}>
                          {r.name_fr}
                        </Typography>
                      </Box>

                      <Box sx={{ textAlign: 'right', flexShrink: 0 }}>
                        <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: COLORS[i % COLORS.length] }}>
                          {r.votes.toLocaleString()}
                        </Typography>
                        <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#5A7062' }}>
                          {r.percentage.toFixed(1)}%
                        </Typography>
                      </Box>
                    </Box>

                    <LinearProgress
                      variant="determinate" value={r.percentage}
                      sx={{
                        height: 8, borderRadius: 4,
                        bgcolor: '#f0f0f0',
                        '& .MuiLinearProgress-bar': {
                          bgcolor: COLORS[i % COLORS.length], borderRadius: 4,
                        },
                      }}
                    />
                  </CardContent>
                </Card>
              ))}
            </Box>

            {/* Pie Chart */}
            <Card sx={{ borderRadius: 3, alignSelf: 'start' }}>
              <CardContent sx={{ p: 3 }}>
                <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2, textAlign: 'center' }}>
                  توزيع الأصوات / Répartition des votes
                </Typography>
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie
                      data={pieData} cx="50%" cy="50%"
                      outerRadius={100} innerRadius={40}
                      dataKey="value" label={({ name, percent }) =>
                        `${name}: ${(percent! * 100).toFixed(1)}%`}
                      labelLine={false}
                    >
                      {pieData.map((_, i) => (
                        <Cell key={i} fill={COLORS[i % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(v: number) => [`${v} صوت`, '']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default ResultsPage;
