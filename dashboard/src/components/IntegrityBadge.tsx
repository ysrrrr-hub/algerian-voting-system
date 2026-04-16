// dashboard/src/components/IntegrityBadge.tsx

import React from 'react';
import { Box, Chip, Typography } from '@mui/material';
import {
  CheckCircle, Cancel, Lock, AccessTime,
  DataObject, VerifiedUser,
} from '@mui/icons-material';

interface Props {
  chainValid:    boolean;
  chainLength:   number;
  lastVoteTime:  string | null;
  lastHash:      string | null;
}

const IntegrityBadge: React.FC<Props> = ({
  chainValid, chainLength, lastVoteTime, lastHash,
}) => (
  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
    {/* ─── الشارات الرئيسية */}
    <Box sx={{ display: 'flex', gap: 1.5, flexWrap: 'wrap' }}>
      <Chip
        icon={chainValid ? <CheckCircle /> : <Cancel />}
        label={chainValid ? 'السلسلة سليمة / Chaîne valide' : 'خلل في السلسلة / Chaîne corrompue'}
        color={chainValid ? 'success' : 'error'}
        variant="filled"
        sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 13 }}
      />
      <Chip
        icon={<Lock />}
        label="RSA-4096 + SHA-256 نشط"
        color="primary"
        variant="outlined"
        sx={{ fontFamily: 'Tajawal', fontWeight: 600, fontSize: 12 }}
      />
      <Chip
        icon={<VerifiedUser />}
        label="التصويت المزدوج: ممنوع"
        color="default"
        variant="outlined"
        sx={{ fontFamily: 'Tajawal', fontSize: 12 }}
      />
    </Box>

    {/* ─── معلومات إضافية */}
    <Box sx={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: 1.5,
    }}>
      <_InfoBox
        icon={<DataObject sx={{ fontSize: 16, color: '#006233' }} />}
        label="عدد الكتل / Blocs"
        value={chainLength.toLocaleString()}
      />
      <_InfoBox
        icon={<AccessTime sx={{ fontSize: 16, color: '#1565C0' }} />}
        label="آخر تصويت / Dernier vote"
        value={lastVoteTime
          ? new Date(lastVoteTime).toLocaleTimeString('ar-DZ')
          : 'لا يوجد'}
      />
      {lastHash && (
        <_InfoBox
          icon={<Lock sx={{ fontSize: 16, color: '#666' }} />}
          label="آخر hash"
          value={`${lastHash.substring(0, 8)}…${lastHash.slice(-8)}`}
          mono
        />
      )}
    </Box>
  </Box>
);

const _InfoBox: React.FC<{
  icon: React.ReactNode; label: string; value: string; mono?: boolean;
}> = ({ icon, label, value, mono }) => (
  <Box sx={{
    display: 'flex', alignItems: 'center', gap: 1,
    bgcolor: '#f8f9fa', borderRadius: 2, px: 1.5, py: 1,
    border: '1px solid #eeeeee',
  }}>
    {icon}
    <Box>
      <Typography sx={{ fontFamily: 'Tajawal', fontSize: 10, color: '#999' }}>
        {label}
      </Typography>
      <Typography sx={{
        fontFamily: mono ? 'monospace' : 'Tajawal',
        fontSize: 13, fontWeight: 700, color: '#333',
      }}>
        {value}
      </Typography>
    </Box>
  </Box>
);

export default IntegrityBadge;
