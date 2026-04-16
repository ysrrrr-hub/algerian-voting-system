// dashboard/src/components/BlockchainChart.tsx

import React from 'react';
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, ReferenceLine,
} from 'recharts';
import { Box, Typography } from '@mui/material';

export interface ChartPoint { time: string; votes: number; blocks: number; }

interface Props { data: ChartPoint[]; }

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <Box sx={{
      bgcolor: '#fff', border: '1px solid #e0e0e0',
      borderRadius: 2, p: 1.5, boxShadow: 2,
    }}>
      <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#666', mb: 0.5 }}>
        {label}
      </Typography>
      <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, fontWeight: 700, color: '#006233' }}>
        {payload[0]?.value} صوت
      </Typography>
    </Box>
  );
};

const BlockchainChart: React.FC<Props> = ({ data }) => (
  <ResponsiveContainer width="100%" height={240}>
    <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
      <defs>
        <linearGradient id="voteGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="5%"  stopColor="#006233" stopOpacity={0.25} />
          <stop offset="95%" stopColor="#006233" stopOpacity={0}    />
        </linearGradient>
      </defs>
      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
      <XAxis
        dataKey="time"
        tick={{ fontFamily: 'Tajawal', fontSize: 11, fill: '#999' }}
        axisLine={false} tickLine={false}
      />
      <YAxis
        tick={{ fontFamily: 'Tajawal', fontSize: 11, fill: '#999' }}
        axisLine={false} tickLine={false}
      />
      <Tooltip content={<CustomTooltip />} />
      <Area
        type="monotone" dataKey="votes"
        stroke="#006233" strokeWidth={2.5}
        fill="url(#voteGrad)"
        dot={{ r: 3, fill: '#006233', strokeWidth: 0 }}
        activeDot={{ r: 6, fill: '#006233' }}
        name="الأصوات"
      />
    </AreaChart>
  </ResponsiveContainer>
);

export default BlockchainChart;
