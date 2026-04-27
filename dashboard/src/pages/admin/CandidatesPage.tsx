import React, { useEffect, useState } from 'react';
import {
  Box, Button, Card, CardContent, CircularProgress,
  IconButton, Table, TableBody, TableCell, TableContainer,
  TableHead, TableRow, Typography, Avatar, Tooltip, Alert
} from '@mui/material';
import { Add, Edit, Delete, Person } from '@mui/icons-material';
import { adminCandidatesApi, Candidate } from '../../services/api';
import CandidateFormModal from '../../components/admin/CandidateFormModal';
import DeleteConfirmDialog from '../../components/admin/DeleteConfirmDialog';

interface Props { token: string; }

const CandidatesPage: React.FC<Props> = ({ token }) => {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Modal states
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | undefined>(undefined);
  
  // Delete dialog states
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [candidateToDelete, setCandidateToDelete] = useState<Candidate | null>(null);

  const fetchCandidates = async () => {
    setLoading(true);
    try {
      const { data } = await adminCandidatesApi.list(token);
      setCandidates(data);
    } catch (err: any) {
      setError(err.response?.data?.error || 'فشل في تحميل قائمة المرشحين');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidates();
  }, [token]);

  const handleAdd = () => {
    setSelectedCandidate(undefined);
    setModalOpen(true);
  };

  const handleEdit = (c: Candidate) => {
    setSelectedCandidate(c);
    setModalOpen(true);
  };

  const handleDeleteClick = (c: Candidate) => {
    setCandidateToDelete(c);
    setDeleteDialogOpen(true);
  };

  const onSuccess = () => {
    setModalOpen(false);
    fetchCandidates();
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', p: 5 }}><CircularProgress /></Box>;

  return (
    <Box sx={{ p: 3, dir: 'rtl' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontFamily: 'Tajawal', fontWeight: 700 }}>
          🗳️ إدارة المرشحين / Gestion des Candidats
        </Typography>
        <Button 
          variant="contained" 
          startIcon={<Add />} 
          onClick={handleAdd}
          sx={{ bgcolor: '#006233', '&:hover': { bgcolor: '#004a26' }, fontFamily: 'Tajawal' }}
        >
          إضافة مرشح جديد
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <TableContainer component={Card} sx={{ borderRadius: 3 }}>
        <Table>
          <TableHead sx={{ bgcolor: '#f5f5f5' }}>
            <TableRow>
              <TableCell align="right" sx={{ fontWeight: 700, fontFamily: 'Tajawal' }}>الصورة</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700, fontFamily: 'Tajawal' }}>الاسم (Ar/Fr)</TableCell>
              <TableCell align="right" sx={{ fontWeight: 700, fontFamily: 'Tajawal' }}>الحزب</TableCell>
              <TableCell align="center" sx={{ fontWeight: 700, fontFamily: 'Tajawal' }}>اللون</TableCell>
              <TableCell align="center" sx={{ fontWeight: 700, fontFamily: 'Tajawal' }}>إجراءات</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {candidates.map((c) => (
              <TableRow key={c.id}>
                <TableCell align="right">
                  <Avatar 
                    src={c.photo_url} 
                    sx={{ width: 50, height: 50, border: `2px solid ${c.color}` }}
                  >
                    <Person />
                  </Avatar>
                </TableCell>
                <TableCell align="right">
                  <Typography sx={{ fontWeight: 600, fontSize: '0.95rem' }}>{c.name_ar}</Typography>
                  <Typography variant="caption" color="textSecondary">{c.name_fr}</Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">{c.party_ar || '-'}</Typography>
                  <Typography variant="caption" color="textSecondary">{c.party_fr || '-'}</Typography>
                </TableCell>
                <TableCell align="center">
                  <Box sx={{ 
                    width: 40, height: 20, bgcolor: c.color, 
                    borderRadius: 1, mx: 'auto', border: '1px solid #ddd' 
                  }} />
                  <Typography variant="caption">{c.color}</Typography>
                </TableCell>
                <TableCell align="center">
                  <Tooltip title="تعديل">
                    <IconButton onClick={() => handleEdit(c)} color="primary"><Edit /></IconButton>
                  </Tooltip>
                  <Tooltip title="حذف">
                    <IconButton onClick={() => handleDeleteClick(c)} sx={{ color: '#D21034' }}><Delete /></IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
            {candidates.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 5, color: '#999' }}>
                  لا يوجد مرشحون حالياً
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <CandidateFormModal 
        open={modalOpen} 
        onClose={() => setModalOpen(false)}
        candidate={selectedCandidate}
        token={token}
        onSuccess={onSuccess}
      />

      <DeleteConfirmDialog 
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        candidate={candidateToDelete}
        token={token}
        onSuccess={fetchCandidates}
      />
    </Box>
  );
};

export default CandidatesPage;
