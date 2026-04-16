// dashboard/src/components/StatsCard.tsx

import React from 'react';
import { Box, Card, CardContent, Typography, Skeleton } from '@mui/material';
import { SvgIconComponent } from '@mui/icons-material';

interface Props {
  titleAr:   string;
  titleFr:   string;
  value:     string | number;
  icon:      SvgIconComponent;
  bgColor:   string;
  textColor?: string;
  trend?:    { value: number; label: string };
  loading?:  boolean;
  extra?:    React.ReactNode;
}

const StatsCard: React.FC<Props> = ({
  titleAr, titleFr, value, icon: Icon,
  bgColor, textColor = '#fff',
  trend, loading, extra,
}) => (
  <Card sx={{ bgcolor: bgColor, color: textColor, height: '100%', borderRadius: 3, overflow: 'hidden', position: 'relative' }}>
    {/* خلفية زخرفية */}
    <Box sx={{
      position: 'absolute', top: -20, right: -20,
      width: 100, height: 100, borderRadius: '50%',
      bgcolor: 'rgba(255,255,255,0.08)',
    }} />

    <CardContent sx={{ p: 3, pb: '20px !important' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <Box sx={{ flex: 1 }}>
          <Typography sx={{ fontFamily: 'Tajawal, sans-serif', fontWeight: 700, fontSize: 15, opacity: 0.9, mb: 0.5 }}>
            {titleAr}
          </Typography>

          {loading ? (
            <Skeleton variant="text" width={100} height={52} sx={{ bgcolor: 'rgba(255,255,255,0.2)' }} />
          ) : (
            <Typography sx={{ fontFamily: 'Tajawal, sans-serif', fontWeight: 800, fontSize: 36, lineHeight: 1.1, my: 0.5 }}>
              {typeof value === 'number' ? value.toLocaleString('ar-DZ') : value}
            </Typography>
          )}

          <Typography sx={{ fontFamily: 'Tajawal, sans-serif', fontSize: 12, opacity: 0.7 }}>
            {titleFr}
          </Typography>

          {trend && (
            <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography sx={{
                fontSize: 11, fontFamily: 'Tajawal, sans-serif',
                bgcolor: 'rgba(255,255,255,0.15)',
                px: 1, py: 0.2, borderRadius: 10,
              }}>
                {trend.value > 0 ? '↑' : '↓'} {Math.abs(trend.value)}% {trend.label}
              </Typography>
            </Box>
          )}
        </Box>

        <Box sx={{
          bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 2,
          p: 1.2, display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon sx={{ fontSize: 32, color: textColor }} />
        </Box>
      </Box>

      {extra && <Box sx={{ mt: 1.5 }}>{extra}</Box>}
    </CardContent>
  </Card>
);

export default StatsCard;
