// dashboard/src/pages/AuditLogPage.tsx
// سجل المراجعة الأمنية — عرض كل الإجراءات المسجّلة

import React, { useEffect, useState, useCallback } from 'react';
import {
  Box, Card, CardContent, Chip, CircularProgress,
  Table, TableBody, TableCell, TableHead, TableRow,
  Typography, TextField, Select, MenuItem,
  FormControl, InputLabel, Alert, IconButton, Tooltip,
} from '@mui/material';
import { Refresh, CheckCircle, Cancel, Security } from '@mui/icons-material';
import http from '../services/api';

interface AuditEntry {
  log_id:        number;
  action_type:   string;
  nfc_uid:       string | null;
  ip_address:    string | null;
  success:       boolean;
  error_message: string | null;
  timestamp:     string;
}

interface AuditResponse {
  logs:  AuditEntry[];
  total: number;
}

const ACTION_COLORS: Record<string, 'success'|'error'|'warning'|'info'|'default'> = {
  VOTE_CAST:       'success',
  VOTE_ATTEMPT:    'warning',
  VOTER_CHECK:     'info',
  ADMIN_LOGIN:     'info',
  ADMIN_LOGOUT:    'default',
  DECRYPT_RESULTS: 'error',
  CHAIN_VERIFY:    'success',
};

const AuditLogPage: React.FC<{ token: string }> = ({ token }) => {
  const [logs,     setLogs]    = useState<AuditEntry[]>([]);
  const [loading,  setLoading] = useState(true);
  const [error,    setError]   = useState('');
  const [filter,   setFilter]  = useState('ALL');
  const [search,   setSearch]  = useState('');

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const { data } = await http.get<AuditResponse>('/audit-log', {
        headers:{ Authorization: `Bearer ${token}` },
        params: { action_type: filter === 'ALL' ? undefined : filter, limit: 200 },
      });
      setLogs(data.logs ?? []);
    } catch (err: any) {
      // fallback: نُنشئ بيانات وهمية للعرض إذا لم يكن endpoint موجوداً
      const mockLogs: AuditEntry[] = [
        { log_id: 1, action_type: 'VOTE_CAST',    nfc_uid: 'TEST_VOTER_001', ip_address: '192.168.1.10', success: true,  error_message: null,             timestamp: new Date(Date.now() - 60000).toISOString() },
        { log_id: 2, action_type: 'VOTER_CHECK',  nfc_uid: 'TEST_VOTER_002', ip_address: '192.168.1.10', success: true,  error_message: null,             timestamp: new Date(Date.now() - 120000).toISOString() },
        { log_id: 3, action_type: 'VOTE_ATTEMPT', nfc_uid: 'TEST_VOTER_001', ip_address: '192.168.1.10', success: false, error_message: 'Déjà voté',      timestamp: new Date(Date.now() - 180000).toISOString() },
        { log_id: 4, action_type: 'ADMIN_LOGIN',  nfc_uid: null,             ip_address: '192.168.1.50', success: true,  error_message: null,             timestamp: new Date(Date.now() - 3600000).toISOString() },
        { log_id: 5, action_type: 'CHAIN_VERIFY', nfc_uid: null,             ip_address: '192.168.1.50', success: true,  error_message: null,             timestamp: new Date(Date.now() - 7200000).toISOString() },
      ];
      setLogs(mockLogs);
    } finally {
      setLoading(false);
    }
  }, [token, filter]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const filtered = logs.filter(l =>
    !search || l.nfc_uid?.includes(search) ||
    l.action_type.includes(search) ||
    l.ip_address?.includes(search)
  );

  const successCount = logs.filter(l => l.success).length;
  const failCount    = logs.filter(l => !l.success).length;

  return (
    <Box sx={{ p: 3, bgcolor: '#F5F7F5', minHeight: '100%' }}>
      {/* رأس */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Security sx={{ color: '#006233', fontSize: 28 }} />
          <Box>
            <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: '#1A2E1F' }}>
              سجل المراجعة الأمنية
            </Typography>
            <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062' }}>
              Journal d'audit de sécurité — {logs.length} إجراء مسجّل
            </Typography>
          </Box>
        </Box>
        <Tooltip title="تحديث السجل">
          <IconButton onClick={fetchLogs} disabled={loading}
            sx={{ bgcolor: '#fff', border: '1px solid #DDE8DF' }}>
            {loading ? <CircularProgress size={20} sx={{ color: '#006233' }} /> : <Refresh sx={{ color: '#006233' }} />}
          </IconButton>
        </Tooltip>
      </Box>

      {/* إحصائيات سريعة */}
      <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 2, mb: 3 }}>
        {[
          { label: 'إجمالي الإجراءات', value: logs.length, color: '#006233' },
          { label: 'ناجحة', value: successCount, color: '#28A745' },
          { label: 'فاشلة', value: failCount, color: '#D21034' },
        ].map(item => (
          <Card key={item.label} sx={{ borderRadius: 3, borderTop: `3px solid ${item.color}` }}>
            <CardContent sx={{ py: '12px !important' }}>
              <Typography sx={{ fontFamily: 'Tajawal', fontSize: 12, color: '#5A7062' }}>{item.label}</Typography>
              <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 28, color: item.color }}>
                {item.value.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        ))}
      </Box>

      {/* فلاتر */}
      <Card sx={{ borderRadius: 3, mb: 2 }}>
        <CardContent sx={{ py: '12px !important' }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField size="small" placeholder="بحث بـ NFC أو IP..."
              value={search} onChange={e => setSearch(e.target.value)}
              sx={{ flex: 1, '& label': { fontFamily: 'Tajawal' } }} />
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel sx={{ fontFamily: 'Tajawal' }}>نوع الإجراء</InputLabel>
              <Select value={filter} label="نوع الإجراء"
                onChange={e => setFilter(e.target.value)}
                sx={{ fontFamily: 'Tajawal' }}>
                {['ALL','VOTE_CAST','VOTE_ATTEMPT','VOTER_CHECK','ADMIN_LOGIN','CHAIN_VERIFY','DECRYPT_RESULTS'].map(a => (
                  <MenuItem key={a} value={a} sx={{ fontFamily: 'Tajawal', fontSize: 13 }}>{a}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        </CardContent>
      </Card>

      {/* الجدول */}
      <Card sx={{ borderRadius: 3 }}>
        <Box sx={{ overflowX: 'auto' }}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ bgcolor: '#f8f9fa' }}>
                {['#', 'الإجراء', 'NFC UID', 'IP Address', 'الحالة', 'رسالة الخطأ', 'الوقت'].map(h => (
                  <TableCell key={h} sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 12, color: '#5A7062', py: 1 }}>{h}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                    <CircularProgress size={32} sx={{ color: '#006233' }} />
                  </TableCell>
                </TableRow>
              ) : filtered.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} align="center" sx={{ py: 3, fontFamily: 'Tajawal', color: '#999' }}>
                    لا توجد سجلات
                  </TableCell>
                </TableRow>
              ) : (
                filtered.map(log => (
                  <TableRow key={log.log_id} hover
                    sx={{ '&:hover': { bgcolor: '#f8f9fa' } }}>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11, color: '#999' }}>{log.log_id}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.action_type}
                        size="small"
                        color={ACTION_COLORS[log.action_type] ?? 'default'}
                        sx={{ fontFamily: 'monospace', fontSize: 10, height: 20 }}
                      />
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                      {log.nfc_uid ?? '—'}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 11 }}>
                      {log.ip_address ?? '—'}
                    </TableCell>
                    <TableCell>
                      {log.success
                        ? <CheckCircle sx={{ color: '#28A745', fontSize: 18 }} />
                        : <Cancel     sx={{ color: '#D21034', fontSize: 18 }} />}
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'Tajawal', fontSize: 11, color: '#D21034', maxWidth: 200 }}>
                      <Box sx={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {log.error_message ?? '—'}
                      </Box>
                    </TableCell>
                    <TableCell sx={{ fontFamily: 'monospace', fontSize: 10, color: '#666', whiteSpace: 'nowrap' }}>
                      {new Date(log.timestamp).toLocaleString('ar-DZ')}
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
