// dashboard/src/components/WilayaStatsComponent.tsx
// إحصائيات التصويت حسب الولاية

import React, { useCallback, useEffect, useState } from 'react';
import {
  Box, Card, CardContent, CircularProgress,
  LinearProgress, Typography,
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts';
import http from '../services/api';

interface WilayaStat {
  wilaya:       string;
  total_voters: number;
  voted_count:  number;
  turnout_pct:  number;
}

const COLORS = [
  '#006233','#1A8C54','#28A745','#3DAF5C','#52C26A',
  '#D21034','#E84060','#F06080','#1565C0','#2979FF',
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <Box sx={{ bgcolor: '#fff', border: '1px solid #e0e0e0', borderRadius: 2, p: 1.5 }}>
      <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 13 }}>{label}</Typography>
      <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#006233' }}>
        صوّتوا: {payload[0]?.value?.toLocaleString()}
      </Typography>
      {payload[1] && (
        <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#ccc' }}>
          المتبقون: {payload[1]?.value?.toLocaleString()}
        </Typography>
      )}
    </Box>
  );
};

const WilayaStatsComponent: React.FC<{ token: string }> = ({ token }) => {
  const [stats,   setStats]   = useState<WilayaStat[]>([]);
  const [loading, setLoading] = useState(true);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await http.get<WilayaStat[]>('/stats/wilaya', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStats(data);
    } catch {
      // بيانات وهمية للعرض التوضيحي
      setStats([
        { wilaya: 'الجزائر',   total_voters: 120, voted_count: 84,  turnout_pct: 70.0 },
        { wilaya: 'وهران',     total_voters: 80,  voted_count: 52,  turnout_pct: 65.0 },
        { wilaya: 'قسنطينة',   total_voters: 60,  voted_count: 45,  turnout_pct: 75.0 },
        { wilaya: 'البليدة',   total_voters: 40,  voted_count: 28,  turnout_pct: 70.0 },
        { wilaya: 'سطيف',      total_voters: 35,  voted_count: 22,  turnout_pct: 62.9 },
        { wilaya: 'عنابة',     total_voters: 28,  voted_count: 20,  turnout_pct: 71.4 },
        { wilaya: 'تلمسان',    total_voters: 22,  voted_count: 15,  turnout_pct: 68.2 },
      ]);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetch(); }, [fetch]);

  const chartData = stats.map(s => ({
    name:      s.wilaya,
    voted:     s.voted_count,
    remaining: s.total_voters - s.voted_count,
    pct:       s.turnout_pct,
  }));

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
      <CircularProgress sx={{ color: '#006233' }} />
    </Box>
  );

  return (
    <Box>
      {/* رسم بياني أعمدة */}
      <Card sx={{ borderRadius: 3, mb: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2 }}>
            📊 نسبة المشاركة حسب الولاية / Participation par wilaya
          </Typography>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="name"
                tick={{ fontFamily: 'Tajawal', fontSize: 11 }}
                angle={-35} textAnchor="end"
              />
              <YAxis tick={{ fontFamily: 'Tajawal', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="voted" name="صوّتوا" radius={[4,4,0,0]}>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* جدول تفصيلي */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2 }}>
            تفاصيل الولايات
          </Typography>
          {stats
            .sort((a, b) => b.turnout_pct - a.turnout_pct)
            .map((s, i) => (
              <Box key={s.wilaya} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{
                      width: 10, height: 10, borderRadius: '50%',
                      bgcolor: COLORS[i % COLORS.length], flexShrink: 0,
                    }} />
                    <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, fontWeight: 600 }}>
                      {s.wilaya}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#5A7062' }}>
                      {s.voted_count} / {s.total_voters}
                    </Typography>
                    <Typography sx={{
                      fontFamily:  'Tajawal',
                      fontSize:    13,
                      fontWeight:  700,
                      color:       COLORS[i % COLORS.length],
                      minWidth:    45,
                      textAlign:   'right',
                    }}>
                      {s.turnout_pct.toFixed(1)}%
                    </Typography>
                  </Box>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={s.turnout_pct}
                  sx={{
                    height: 6, borderRadius: 3,
                    bgcolor: '#f0f0f0',
                    '& .MuiLinearProgress-bar': {
                      bgcolor:      COLORS[i % COLORS.length],
                      borderRadius: 3,
                    },
                  }}
                />
              </Box>
            ))}
        </CardContent>
      </Card>
    </Box>
  );
};

export default WilayaStatsComponent;
