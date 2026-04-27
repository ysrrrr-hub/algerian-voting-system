import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Typography, Box
} from '@mui/material';
import { adminCandidatesApi, Candidate } from '../../services/api';

interface Props {
  open: boolean;
  onClose: () => void;
  candidate: Candidate | null;
  token: string;
  onSuccess: () => void;
}

const DeleteConfirmDialog: React.FC<Props> = ({ open, onClose, candidate, token, onSuccess }) => {
  const [confirmName, setConfirmName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleDelete = async () => {
    if (!candidate) return;
    
    setLoading(true);
    setError('');
    try {
      await adminCandidatesApi.delete(token, candidate.id);
      setConfirmName('');
      onSuccess();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.error || 'فشل الحذف. قد يكون للمرشح أصوات مسجلة.');
    } finally {
      setLoading(false);
    }
  };

  if (!candidate) return null;

  return (
    <Dialog open={open} onClose={onClose} dir="rtl">
      <DialogTitle sx={{ fontFamily: 'Tajawal', fontWeight: 700, color: '#D21034' }}>
        ⚠️ تأكيد حذف المرشح
      </DialogTitle>
      <DialogContent>
        <Typography gutterBottom>
          أنت على وشك حذف المرشح <strong>{candidate.name_ar}</strong> نهائياً. 
          لا يمكن التراجع عن هذه العملية.
        </Typography>
        
        <Box sx={{ mt: 3, p: 2, bgcolor: '#fff5f5', borderRadius: 1, border: '1px solid #ffdada' }}>
          <Typography variant="body2" color="error" sx={{ mb: 1 }}>
            لتأكيد الحذف، يرجى كتابة اسم المرشح (<strong>{candidate.name_ar}</strong>) في الحقل أدناه:
          </Typography>
          <TextField 
            fullWidth size="small" value={confirmName}
            onChange={e => setConfirmName(e.target.value)}
            placeholder="اكتب الاسم هنا"
          />
        </Box>
        
        {error && <Typography color="error" sx={{ mt: 2, fontSize: '0.875rem' }}>{error}</Typography>}
      </DialogContent>
      <DialogActions sx={{ p: 2 }}>
        <Button onClick={onClose} disabled={loading}>إلغاء</Button>
        <Button 
          onClick={handleDelete} 
          variant="contained" 
          disabled={loading || confirmName !== candidate.name_ar}
          sx={{ bgcolor: '#D21034', '&:hover': { bgcolor: '#a00d27' } }}
        >
          {loading ? 'جاري الحذف...' : 'تأكيد الحذف النهائي'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default DeleteConfirmDialog;
