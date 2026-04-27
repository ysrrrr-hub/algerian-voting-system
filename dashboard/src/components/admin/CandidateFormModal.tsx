import React, { useState, useEffect } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, TextField, Box, Grid, Typography, IconButton
} from '@mui/material';
import { CloudUpload, Close } from '@mui/icons-material';
import { adminCandidatesApi, Candidate } from '../../services/api';

interface Props {
  open: boolean;
  onClose: () => void;
  candidate?: Candidate;
  token: string;
  onSuccess: () => void;
}

const CandidateFormModal: React.FC<Props> = ({ open, onClose, candidate, token, onSuccess }) => {
  const [formData, setFormData] = useState({
    name_ar: '',
    name_fr: '',
    party_ar: '',
    party_fr: '',
    color: '#006233',
    bio_ar: '',
    bio_fr: ''
  });
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (candidate) {
      setFormData({
        name_ar: candidate.name_ar,
        name_fr: candidate.name_fr,
        party_ar: candidate.party_ar || '',
        party_fr: candidate.party_fr || '',
        color: candidate.color,
        bio_ar: candidate.bio_ar || '',
        bio_fr: candidate.bio_fr || ''
      });
      setPreview(candidate.photo_url || null);
    } else {
      setFormData({
        name_ar: '', name_fr: '', party_ar: '', party_fr: '',
        color: '#006233', bio_ar: '', bio_fr: ''
      });
      setPreview(null);
      setFile(null);
    }
    setError('');
  }, [candidate, open]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setFile(f);
      setPreview(URL.createObjectURL(f));
    }
  };

  const handleSubmit = async () => {
    if (!formData.name_ar || !formData.name_fr) {
      setError('الأسماء مطلوبة');
      return;
    }

    const data = new FormData();
    Object.entries(formData).forEach(([k, v]) => data.append(k, v));
    if (file) data.append('photo', file);

    setLoading(true);
    try {
      if (candidate) {
        await adminCandidatesApi.update(token, candidate.id, data);
      } else {
        await adminCandidatesApi.create(token, data);
      }
      onSuccess();
    } catch (err: any) {
      setError(err.response?.data?.error || 'حدث خطأ أثناء الحفظ');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="md" dir="rtl">
      <DialogTitle sx={{ fontFamily: 'Tajawal', fontWeight: 700, display: 'flex', justifyContent: 'space-between' }}>
        {candidate ? '✏️ تعديل بيانات المرشح' : '➕ إضافة مرشح جديد'}
        <IconButton onClick={onClose}><Close /></IconButton>
      </DialogTitle>
      <DialogContent dividers>
        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField 
              fullWidth label="الاسم العربي*" value={formData.name_ar} 
              onChange={e => setFormData({...formData, name_ar: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField 
              fullWidth label="الاسم الفرنسي*" value={formData.name_fr} 
              onChange={e => setFormData({...formData, name_fr: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField 
              fullWidth label="الحزب (عربي)" value={formData.party_ar} 
              onChange={e => setFormData({...formData, party_ar: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField 
              fullWidth label="الحزب (فرنسي)" value={formData.party_fr} 
              onChange={e => setFormData({...formData, party_fr: e.target.value})}
              sx={{ mb: 2 }}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" display="block" gutterBottom>لون المرشح المميز</Typography>
              <input 
                type="color" value={formData.color} 
                onChange={e => setFormData({...formData, color: e.target.value})}
                style={{ width: '100%', height: 40, border: '1px solid #ddd', borderRadius: 4, cursor: 'pointer' }}
              />
            </Box>
            
            <Box sx={{ border: '2px dashed #ccc', p: 2, textAlign: 'center', borderRadius: 2 }}>
              {preview ? (
                <Box sx={{ position: 'relative' }}>
                  <img src={preview} alt="preview" style={{ maxWidth: '100%', maxHeight: 150, borderRadius: 8 }} />
                  <Button size="small" onClick={() => setPreview(null)} sx={{ display: 'block', mx: 'auto', mt: 1 }}>تغيير الصورة</Button>
                </Box>
              ) : (
                <Button variant="outlined" component="label" startIcon={<CloudUpload />}>
                  رفع صورة المرشح
                  <input type="file" hidden accept="image/*" onChange={handleFileChange} />
                </Button>
              )}
            </Box>
          </Grid>

          <Grid item xs={12}>
            <TextField 
              fullWidth multiline rows={3} label="السيرة الذاتية (عربي)" value={formData.bio_ar} 
              onChange={e => setFormData({...formData, bio_ar: e.target.value})}
              sx={{ mb: 2 }}
            />
            <TextField 
              fullWidth multiline rows={3} label="السيرة الذاتية (فرنسي)" value={formData.bio_fr} 
              onChange={e => setFormData({...formData, bio_fr: e.target.value})}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions sx={{ p: 2.5 }}>
        <Button onClick={onClose} color="inherit">إلغاء</Button>
        <Button 
          onClick={handleSubmit} variant="contained" disabled={loading}
          sx={{ bgcolor: '#006233', '&:hover': { bgcolor: '#004a26' } }}
        >
          {loading ? 'جاري الحفظ...' : 'حفظ البيانات'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CandidateFormModal;
