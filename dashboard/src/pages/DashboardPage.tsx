// dashboard/src/pages/DashboardPage.tsx
// لوحة المراقبة الحية — إحصائيات + بلوكشين + نزاهة

import React, { useCallback, useEffect, useState } from 'react';
import {
  Box, Card, CardContent, CircularProgress,
  Grid, IconButton, LinearProgress,
  Tooltip, Typography,
} from '@mui/material';
import {
  HowToVote, Link as LinkIcon, People,
  Refresh, TrendingUp,
} from '@mui/icons-material';

import BlockchainChart, { ChartPoint } from '../components/BlockchainChart';
import IntegrityBadge from '../components/IntegrityBadge';
import StatsCard from '../components/StatsCard';

import {
  apiBlockchainStatus, apiStats, apiVerifyChain,
  BlockchainStatus, ChainStatus, VotingStats,
} from '../services/api';

interface Props { adminName: string; }

const EMPTY_STATS: VotingStats = {
  total_voters: 0, voted_count: 0, remaining_count: 0,
  turnout_percentage: 0, blockchain_length: 0, last_vote_time: null,
};

const DashboardPage: React.FC<Props> = ({ adminName }) => {
  const [stats,    setStats]    = useState<VotingStats>(EMPTY_STATS);
  const [chain,    setChain]    = useState<ChainStatus | null>(null);
  const [bcStatus, setBcStatus] = useState<BlockchainStatus | null>(null);
  const [chart,    setChart]    = useState<ChartPoint[]>([]);
  const [loading,  setLoading]  = useState(true);
  const [lastRefresh, setLastRefresh] = useState(new Date());



  // ─── جلب البيانات ───────────────────────────────────────────
  const fetchAll = useCallback(async () => {
    try {
      const [sRes, cRes, bRes] = await Promise.allSettled([
        apiStats(), apiVerifyChain(), apiBlockchainStatus(),
      ]);
      if (sRes.status === 'fulfilled') setStats(sRes.value.data);
      if (cRes.status === 'fulfilled') setChain(cRes.value.data);
      if (bRes.status === 'fulfilled') setBcStatus(bRes.value.data);
      setLastRefresh(new Date());
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, 30_000);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const pct = Math.min(100, stats.turnout_percentage ?? 0);

  return (
    <Box sx={{ p: 3, bgcolor: '#F5F7F5', minHeight: '100%' }}>

      {/* ─── رأس الصفحة ────────────────────────────────────── */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box>
          <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: '#1A2E1F' }}>
            📊 لوحة المراقبة الحية
          </Typography>
          <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062' }}>
            Tableau de bord en direct — مرحباً {adminName} •{' '}
            آخر تحديث: {lastRefresh.toLocaleTimeString('ar-DZ')}
          </Typography>
        </Box>
        <Tooltip title="تحديث البيانات">
          <IconButton
            onClick={fetchAll}
            disabled={loading}
            sx={{ bgcolor: '#fff', border: '1px solid #DDE8DF', '&:hover': { bgcolor: '#E8F5EE' } }}
          >
            {loading
              ? <CircularProgress size={20} sx={{ color: '#006233' }} />
              : <Refresh sx={{ color: '#006233' }} />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* ─── بطاقات الإحصائيات ─────────────────────────────── */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            titleAr="إجمالي الناخبين" titleFr="Total électeurs"
            value={stats.total_voters} icon={People}
            bgColor="#006233" loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            titleAr="صوّتوا حتى الآن" titleFr="Ont voté"
            value={stats.voted_count} icon={HowToVote}
            bgColor="#D21034" loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            titleAr="نسبة المشاركة" titleFr="Taux de participation"
            value={`${pct.toFixed(1)}%`} icon={TrendingUp}
            bgColor="#D4A017" textColor="#1A1A00"
            loading={loading}
            extra={
              <LinearProgress
                variant="determinate" value={pct}
                sx={{
                  height: 6, borderRadius: 3,
                  bgcolor: 'rgba(0,0,0,0.15)',
                  '& .MuiLinearProgress-bar': { bgcolor: '#006233', borderRadius: 3 },
                }}
              />
            }
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            titleAr="كتل البلوكشين" titleFr="Blocs blockchain"
            value={stats.blockchain_length} icon={LinkIcon}
            bgColor="#1565C0" loading={loading}
          />
        </Grid>
      </Grid>

      {/* ─── الرسم البياني + النزاهة ─────────────────────────── */}
      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} md={8}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2 }}>
                📈 تدفق الأصوات عبر الزمن / Flux des votes dans le temps
              </Typography>
              {chart.length === 0 ? (
                <Box sx={{
                  height: 240, display: 'flex', alignItems: 'center',
                  justifyContent: 'center', bgcolor: '#f8f9fa', borderRadius: 2,
                }}>
                  <Typography sx={{ fontFamily: 'Tajawal', color: '#999', fontSize: 14 }}>
                    في انتظار بدء التصويت / En attente du début du scrutin
                  </Typography>
                </Box>
              ) : (
                <BlockchainChart data={chart} />
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ borderRadius: 3, height: '100%' }}>
            <CardContent sx={{ p: 3 }}>
              <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2 }}>
                📦 آخر كتلة / Dernier bloc
              </Typography>
              {bcStatus?.last_block ? (
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {[
                    { label: 'رقم الكتلة', value: `#${bcStatus.last_block.index}` },
                    { label: 'الوقت', value: bcStatus.last_block.timestamp ? new Date(bcStatus.last_block.timestamp).toLocaleTimeString('ar-DZ') : '—' },
                    { label: 'Hash', value: `${(bcStatus.last_block.current_hash || '').substring(0, 12)}…`, mono: true },
                    { label: 'Nonce', value: String(bcStatus.last_block.nonce || 0) },
                  ].map(item => (
                    <Box key={item.label} sx={{
                      display: 'flex', justifyContent: 'space-between',
                      bgcolor: '#f8f9fa', borderRadius: 2, px: 1.5, py: 0.8,
                    }}>
                      <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#666' }}>
                        {item.label}
                      </Typography>
                      <Typography sx={{
                        fontFamily: item.mono ? 'monospace' : 'Tajawal',
                        fontSize: 12, fontWeight: 700, color: '#1A2E1F',
                      }}>
                        {item.value}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              ) : (
                <Typography sx={{ fontFamily: 'Tajawal', color: '#999', fontSize: 13 }}>
                  Genesis Block فقط
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* ─── شارات النزاهة ──────────────────────────────────── */}
      <Card sx={{ borderRadius: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 16, mb: 2 }}>
            🔍 حالة النزاهة / État d'intégrité
          </Typography>
          <IntegrityBadge
            chainValid={chain?.valid ?? true}
            chainLength={stats.blockchain_length}
            lastVoteTime={stats.last_vote_time}
            lastHash={chain?.last_block_hash ?? null}
          />
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardPage;
