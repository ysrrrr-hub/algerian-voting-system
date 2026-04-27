import React, { useEffect, useState, useCallback } from 'react';
import {
  Box, Card, CardContent, Chip, CircularProgress,
  Table, TableBody, TableCell, TableHead, TableRow,
  Typography, TextField, Select, MenuItem,
  FormControl, InputLabel, Button, IconButton, Tooltip, Grid, Stack
} from '@mui/material';
import { Refresh, CheckCircle, Cancel, Security, FileDownload, Warning } from '@mui/icons-material';
import { apiAuditLog, apiAuditStats, AuditEntry } from '../services/api';

const ACTION_LABELS_AR: Record<string, string> = {
  VOTE_CAST: 'تصويت',
  VOTE_DUPLICATE_BLOCKED: 'تصويت مزدوج محظور',
  VOTER_NOT_FOUND: 'ناخب غير موجود',
  VOTER_AUTHENTICATED: 'توثيق ناخب',
  ADMIN_LOGIN_SUCCESS: 'دخول مشرف ناجح',
  ADMIN_LOGIN_FAILED: 'فشل دخول مشرف',
  ADMIN_LOGOUT: 'تسجيل خروج مشرف',
  RECEIPT_VERIFIED: 'تحقق من وصل',
  RECEIPT_VERIFICATION_FAILED: 'فشل تحقق من وصل',
  RECEIPT_GENERATED: 'توليد وصل',
  BLOCKCHAIN_VERIFIED: 'تحقق بلوكشين',
  AUDIT_VIEWED: 'عرض السجل',
  AUDIT_EXPORTED: 'تصدير السجل',
  SYSTEM_ERROR: 'خطأ نظام'
};

const AuditLogPage: React.FC<{ token: string }> = ({ token }) => {
  const [logs, setLogs] = useState<AuditEntry[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  const [filterAction, setFilterAction] = useState('ALL');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [search, setSearch] = useState('');
  
  const [page] = useState(1);
  const [perPage] = useState(50);

  const fetchStats = useCallback(async () => {
    try {
      const res = await apiAuditStats(token);
      setStats(res.data);
    } catch(err) { }
  }, [token]);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    try {
      const actionParam = filterAction === 'ALL' ? undefined : filterAction;
      const statusParam = filterStatus === 'ALL' ? undefined : filterStatus;
      
      const { data } = await apiAuditLog(token, actionParam, statusParam, perPage, page);
      setLogs(data.logs ?? []);
      fetchStats();
    } catch (err: any) {
      console.error(err);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  }, [token, filterAction, filterStatus, page, perPage, fetchStats]);

  useEffect(() => { 
    fetchLogs(); 
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, [fetchLogs]);

  const handleExportCsv = () => {
    let url = `/api/audit/export?`;
    let params = new URLSearchParams();
    if (filterAction !== 'ALL') params.append('action_type', filterAction);
    if (filterStatus !== 'ALL') params.append('status', filterStatus);
    window.location.href = url + params.toString();
  };

  const filtered = logs.filter(l =>
    !search || 
    (l.nfc_uid && l.nfc_uid.includes(search)) ||
    (l.ip_address && l.ip_address.includes(search)) ||
    (l.identifier_hash && l.identifier_hash.includes(search))
  );

  return (
    <Box sx={{ p: 3, bgcolor: '#F5F7F5', minHeight: '100%' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Security sx={{ color: '#006233', fontSize: 28 }} />
          <Box>
            <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: '#1A2E1F' }}>
              سجل المراجعة الأمنية
            </Typography>
            <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062' }}>
              Journal d'audit de sécurité
            </Typography>
          </Box>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<FileDownload />} 
            onClick={handleExportCsv}
            sx={{ px: 3, fontFamily: 'Tajawal', bgcolor: '#006233' }}
          >
            تصدير CSV / Export
          </Button>
          <Tooltip title="تحديث السجل">
            <IconButton onClick={fetchLogs} disabled={loading} sx={{ bgcolor: '#fff', border: '1px solid #DDE8DF' }}>
              {loading ? <CircularProgress size={20} sx={{ color: '#006233' }} /> : <Refresh sx={{ color: '#006233' }} />}
            </IconButton>
          </Tooltip>
        </Stack>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {[
          { label: 'إجمالي الأحداث / Total', value: stats?.total ?? '-', icon: '📊', color: '#006233' },
          { label: 'آخر 24 ساعة / Last 24h', value: stats?.last_24h ?? '-', icon: '⏰', color: '#1565C0' },
          { label: 'أصوات اليوم / Votes Today', value: stats?.votes_today ?? '-', icon: '🗳️', color: '#28A745' },
          { label: 'عمليات فاشلة / Failed Today', value: stats?.failed_today ?? '-', icon: '⚠️', color: '#D21034' },
        ].map(item => (
          <Grid item xs={12} sm={6} md={3} key={item.label}>
            <Card sx={{ borderRadius: 3, borderTop: `4px solid ${item.color}` }}>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Box>
                    <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#5A7062', whiteSpace: 'pre-line' }}>{item.label}</Typography>
                    <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 26, color: item.color, mt: 1 }}>{item.value}</Typography>
                  </Box>
                  <Typography fontSize={32}>{item.icon}</Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Filters */}
      <Card sx={{ borderRadius: 3, mb: 2 }}>
        <CardContent sx={{ py: '16px !important' }}>
          <Stack direction={{ xs: 'column', md: 'row' }} spacing={2} alignItems="center">
            <TextField 
              size="small" placeholder="بحث بـ NFC أو IP أو Hash..."
              value={search} onChange={e => setSearch(e.target.value)}
              sx={{ flex: 1, '& input': { fontFamily: 'Tajawal' } }} 
            />
            
            <FormControl size="small" sx={{ minWidth: 200 }}>
              <InputLabel sx={{ fontFamily: 'Tajawal' }}>نوع الإجراء (Action Type)</InputLabel>
              <Select value={filterAction} label="نوع الإجراء (Action Type)" onChange={e => setFilterAction(e.target.value)} sx={{ fontFamily: 'Tajawal' }}>
                <MenuItem value="ALL">الكل / All</MenuItem>
                {Object.keys(ACTION_LABELS_AR).map(a => (
                  <MenuItem key={a} value={a} sx={{ fontFamily: 'Tajawal' }}>{ACTION_LABELS_AR[a]}</MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel sx={{ fontFamily: 'Tajawal' }}>الحالة (Status)</InputLabel>
              <Select value={filterStatus} label="الحالة (Status)" onChange={e => setFilterStatus(e.target.value)} sx={{ fontFamily: 'Tajawal' }}>
                <MenuItem value="ALL">الكل / All</MenuItem>
                <MenuItem value="SUCCESS">ناجح / Success</MenuItem>
                <MenuItem value="FAILED">فشل / Failed</MenuItem>
                <MenuItem value="WARNING">تنبيه / Warning</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </CardContent>
      </Card>

      {/* Table */}
      <Card sx={{ borderRadius: 3 }}>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                {['الوقت', 'الحدث', 'الفاعل', 'IP / User-Agent', 'الحالة', 'التفاصيل'].map(h => (
                  <TableCell key={h} sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 13, color: '#5A7062', py: 1.5 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading && filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} sx={{ color: '#006233' }} />
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3, fontFamily: 'Tajawal', color: '#999' }}>لا توجد سجلات</TableCell>
                </TableRow>
              ) : (
                filtered.map(log => (
                  <TableRow key={log.log_id} hover sx={{ '&:hover': { bgcolor: '#f8f9fa' } }}>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11, color: '#666', whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString('ar-DZ')}
                    </TableCell>
                    <TableCell>
                      <Chip label={ACTION_LABELS_AR[log.action_type] || log.action_type} size="small" color={log.status === 'SUCCESS' ? 'default' : log.status === 'WARNING' ? 'warning' : 'error'} sx={{ fontFamily: 'Tajawal', fontSize: 11 }} />
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                      {log.identifier_hash ? `Hash: ${log.identifier_hash.substring(0,8)}...` : log.nfc_uid ? `UID: ${log.nfc_uid}` : '—'}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                      <Box>{log.ip_address ?? '—'}</Box>
                      <Box sx={{ fontSize: 9, color: '#999' }}>{log.user_agent ? log.user_agent.substring(0, 30) + '...' : ''}</Box>
                    </TableCell>
                    <TableCell>
                      {log.status === 'SUCCESS' ? <CheckCircle sx={{ color: '#28A745', fontSize: 18 }} /> : log.status === 'WARNING' ? <Warning sx={{ color: '#FFC107', fontSize: 18 }} /> : <Cancel sx={{ color: '#D21034', fontSize: 18 }} />}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'Tajawal', fontSize: 11, maxWidth: 200 }}>
                      <Box sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{log.error_message ?? '—'}</Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </Box>
      </Card>
    </Box>
  );
};

export default AuditLogPage;
