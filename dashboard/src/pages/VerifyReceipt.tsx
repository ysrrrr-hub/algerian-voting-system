import React, { useState, useEffect } from 'react';
import { Box, Card, Typography, TextField, Button, CircularProgress, Container, Alert } from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { CheckCircle, ErrorOutline, Search } from '@mui/icons-material';

const VerifyReceipt: React.FC = () => {
  const { code } = useParams<{ code?: string }>();
  const navigate = useNavigate();
  const [codeInput, setCodeInput] = useState(code || '');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (code) {
      verifyCode(code);
    }
  }, [code]);

  const verifyCode = async (c: string) => {
    if (!c.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`https://evotingdz.live/api/verify/${c}`);
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult({ verified: false, message_ar: 'حدث خطأ في الاتصال بالخادم', message_fr: 'Erreur de connexion' });
    }
    setLoading(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (codeInput) {
      navigate(`/verify/${codeInput.trim().toUpperCase()}`);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Official Header */}
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h6" sx={{ color: '#006233', fontWeight: 'bold', fontFamily: 'Tajawal' }}>
          الجمهورية الجزائرية الديمقراطية الشعبية
        </Typography>
        <Typography variant="body2" sx={{ color: '#006233', mb: 1, fontFamily: 'Roboto' }}>
          République Algérienne Démocratique et Populaire
        </Typography>
        <Typography variant="h5" sx={{ color: '#006233', fontWeight: 'bold', fontFamily: 'Tajawal' }}>
          الهيئة الوطنية المستقلة للانتخابات
        </Typography>
        <Typography variant="body1" sx={{ color: '#006233', fontFamily: 'Roboto' }}>
          Autorité Nationale Indépendante des Élections
        </Typography>
      </Box>

      {/* Main Card */}
      <Card sx={{ p: 4, borderRadius: 3, boxShadow: '0 4px 20px rgba(0,0,0,0.05)' }}>
        <Typography variant="h5" align="center" sx={{ mb: 3, fontWeight: 'bold', fontFamily: 'Tajawal' }}>
          بوابة تحقق وصل التصويت / Portail de vérification
        </Typography>

        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', marginBottom: '30px' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="ALG-2026-XXXXXXXX"
            value={codeInput}
            onChange={(e) => setCodeInput(e.target.value.toUpperCase())}
            inputProps={{ maxLength: 20, style: { textAlign: 'center', fontFamily: 'monospace', letterSpacing: 2, fontSize: 18 } }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={loading || !codeInput}
            sx={{ px: 4 }}
            startIcon={<Search />}
          >
            تحقق
          </Button>
        </form>

        {loading && <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}><CircularProgress /></Box>}

        {result && !loading && (
          <Box sx={{ mt: 2, animation: 'fadeIn 0.5s' }}>
            {result.verified ? (
              <>
                <Alert severity="success" icon={<CheckCircle fontSize="inherit" />} sx={{ mb: 3 }}>
                  <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{result.message_ar}</Typography>
                  <Typography variant="body2">{result.message_fr}</Typography>
                </Alert>
                <Box sx={{ bgcolor: '#F9F9F9', p: 3, borderRadius: 2, border: '1px solid #E0E0E0' }}>
                  <Typography variant="body1" sx={{ mb: 1 }}><strong>معرف الوصل:</strong> <span style={{ fontFamily: 'monospace' }}>{result.receipt_code}</span></Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}><strong>التاريخ والوقت:</strong> {new Date(result.timestamp).toLocaleString('en-GB')}</Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}><strong>الانتخابات:</strong> {result.election_name_ar}</Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}><strong>هاش الكتلة:</strong> <span style={{ fontFamily: 'monospace', fontSize: 12 }}>{result.block_hash}</span></Typography>
                  <Typography variant="body1" sx={{ mb: 1 }}><strong>عدد التحققات السابقة:</strong> {result.verified_count - 1}</Typography>
                  
                  <Box sx={{ mt: 3, p: 2, bgcolor: '#FFF8E1', borderLeft: '4px solid #FFC107', borderRadius: 1 }}>
                    <Typography variant="body2" sx={{ color: '#795548', fontWeight: 'bold' }}>{result.privacy_note_ar}</Typography>
                    <Typography variant="caption" sx={{ color: '#795548' }}>{result.privacy_note_fr}</Typography>
                  </Box>
                </Box>
              </>
            ) : (
              <Alert severity="error" icon={<ErrorOutline fontSize="inherit" />}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>{result.message_ar}</Typography>
                <Typography variant="body2">{result.message_fr}</Typography>
              </Alert>
            )}
          </Box>
        )}
      </Card>
    </Container>
  );
};

export default VerifyReceipt;
