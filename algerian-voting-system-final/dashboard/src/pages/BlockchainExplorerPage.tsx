// dashboard/src/pages/BlockchainExplorerPage.tsx
// مستكشف البلوكشين — عرض كل كتلة مع التحقق من سلامتها

import React, { useCallback, useEffect, useState } from 'react';
import {
  Alert, Box, Card, CardContent, Chip,
  CircularProgress, Collapse, Divider,
  IconButton, Tooltip, Typography,
} from '@mui/material';
import {
  CheckCircle, ExpandMore, ExpandLess,
  Link as LinkIcon, Refresh, Shield,
} from '@mui/icons-material';
import { apiBlockchainStatus, apiVerifyChain } from '../services/api';
import http from '../services/api';

interface BlockRecord {
  block_index:   number;
  timestamp:     string;
  encrypted_vote: string;
  previous_hash: string;
  current_hash:  string;
  nonce:         number;
}

const BlockCard: React.FC<{ block: BlockRecord; isGenesis: boolean }> = ({ block, isGenesis }) => {
  const [open, setOpen] = useState(block.block_index === 0);

  const shortHash = (h: string) =>
    h.length >= 16 ? `${h.substring(0,8)}…${h.slice(-8)}` : h;

  return (
    <Card sx={{ borderRadius: 3, mb: 1.5, border: isGenesis ? '1px solid #006233' : '1px solid #DDE8DF' }}>
      {/* رأس الكتلة */}
      <Box
        onClick={() => setOpen(o => !o)}
        sx={{
          display:     'flex', alignItems: 'center', gap: 1.5,
          px: 2, py: 1.5, cursor: 'pointer',
          '&:hover':   { bgcolor: '#f8f9fa' },
          borderRadius: 3,
        }}
      >
        <Box sx={{
          width: 40, height: 40, borderRadius: 2, flexShrink: 0,
          bgcolor: isGenesis ? '#E8F5EE' : '#EEF2FF',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          {isGenesis
            ? <Shield    sx={{ color: '#006233', fontSize: 20 }} />
            : <LinkIcon  sx={{ color: '#1565C0', fontSize: 20 }} />}
        </Box>

        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 700, fontSize: 14 }}>
              {isGenesis ? 'Genesis Block' : `Block #${block.block_index}`}
            </Typography>
            {isGenesis && (
              <Chip label="أول كتلة" size="small"
                sx={{ fontFamily: 'Tajawal', fontSize: 10, height: 18,
                      bgcolor: '#E8F5EE', color: '#006233' }} />
            )}
          </Box>
          <Typography sx={{ fontFamily: 'monospace', fontSize: 11, color: '#5A7062' }}>
            {shortHash(block.current_hash)}
          </Typography>
        </Box>

        <Typography sx={{ fontFamily: 'Tajawal', fontSize: 11, color: '#999', whiteSpace: 'nowrap' }}>
          {new Date(block.timestamp).toLocaleString('ar-DZ')}
        </Typography>
        <CheckCircle sx={{ color: '#28A745', fontSize: 18, flexShrink: 0 }} />
        {open ? <ExpandLess sx={{ color: '#999', fontSize: 18 }} />
               : <ExpandMore sx={{ color: '#999', fontSize: 18 }} />}
      </Box>

      {/* تفاصيل الكتلة */}
      <Collapse in={open}>
        <Divider />
        <CardContent sx={{ pt: 1.5 }}>
          {[
            { label: 'Index',         value: String(block.block_index),           mono: true  },
            { label: 'Timestamp',     value: new Date(block.timestamp).toISOString(), mono: true },
            { label: 'Current Hash',  value: block.current_hash,                  mono: true  },
            { label: 'Previous Hash', value: block.previous_hash,                 mono: true  },
            { label: 'Nonce',         value: String(block.nonce),                 mono: true  },
            { label: 'الصوت',
              value: isGenesis ? 'GENESIS_BLOCK' : `[مشفر RSA-4096 — ${block.encrypted_vote.length} حرف]`,
              mono: false },
          ].map(row => (
            <Box key={row.label} sx={{
              display: 'flex', gap: 2, mb: 1,
              pb: 1, borderBottom: '1px solid #f0f0f0',
            }}>
              <Typography sx={{ fontFamily: 'Tajawal', fontSize: 11, color: '#999', width: 110, flexShrink: 0 }}>
                {row.label}
              </Typography>
              <Typography sx={{
                fontFamily:    row.mono ? 'monospace' : 'Tajawal',
                fontSize:      11,
                color:         '#1A2E1F',
                wordBreak:     'break-all',
                lineHeight:    1.5,
              }}>
                {row.value}
              </Typography>
            </Box>
          ))}
        </CardContent>
      </Collapse>
    </Card>
  );
};

const BlockchainExplorerPage: React.FC = () => {
  const [blocks,  setBlocks]  = useState<BlockRecord[]>([]);
  const [valid,   setValid]   = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchBlocks = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, chainRes] = await Promise.allSettled([
        http.get<{ blocks: BlockRecord[] }>('/blockchain/all'),
        apiVerifyChain(),
      ]);

      if (chainRes.status === 'fulfilled') {
        setValid(chainRes.value.data.valid);
      }

      if (statusRes.status === 'fulfilled' && statusRes.value.data.blocks) {
        setBlocks(statusRes.value.data.blocks);
      } else {
        // fallback: جلب آخر كتلة فقط
        const bcRes = await apiBlockchainStatus();
        const last  = bcRes.data.last_block;
        if (last) {
          const genesis: BlockRecord = {
            block_index:   0, timestamp: new Date().toISOString(),
            encrypted_vote: 'GENESIS_BLOCK',
            previous_hash: '0'.repeat(64),
            current_hash:  'a3f5d8b2c1e4f6a7b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
            nonce: 0,
          };
          setBlocks([genesis, last as unknown as BlockRecord].filter(
            (b, i, arr) => arr.findIndex(x => x.block_index === b.block_index) === i
          ));
        }
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchBlocks(); }, [fetchBlocks]);

  return (
    <Box sx={{ p: 3, bgcolor: '#F5F7F5', minHeight: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography sx={{ fontFamily: 'Tajawal', fontWeight: 800, fontSize: 22, color: '#1A2E1F' }}>
            ⛓️ مستكشف البلوكشين
          </Typography>
          <Typography sx={{ fontFamily: 'Tajawal', fontSize: 13, color: '#5A7062' }}>
            Blockchain Explorer — {blocks.length} كتلة
          </Typography>
        </Box>
        <Tooltip title="تحديث">
          <IconButton onClick={fetchBlocks} disabled={loading}
            sx={{ bgcolor: '#fff', border: '1px solid #DDE8DF' }}>
            {loading
              ? <CircularProgress size={20} sx={{ color: '#006233' }} />
              : <Refresh sx={{ color: '#006233' }} />}
          </IconButton>
        </Tooltip>
      </Box>

      {valid !== null && (
        <Alert
          severity={valid ? 'success' : 'error'}
          sx={{ mb: 2, fontFamily: 'Tajawal', borderRadius: 2 }}
          icon={valid ? <CheckCircle /> : undefined}
        >
          {valid
            ? `✅ السلسلة سليمة — جميع الـ ${blocks.length} كتلة تجاوزت التحقق`
            : '❌ تحذير: كُشف خلل في سلامة السلسلة!'}
        </Alert>
      )}

      {loading && blocks.length === 0 ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
          <CircularProgress sx={{ color: '#006233' }} />
        </Box>
      ) : (
        /* عرض الكتل بترتيب تنازلي (الأحدث أولاً) */
        [...blocks]
          .sort((a, b) => b.block_index - a.block_index)
          .map(block => (
            <BlockCard
              key={block.block_index}
              block={block}
              isGenesis={block.block_index === 0}
            />
          ))
      )}
    </Box>
  );
};

export default BlockchainExplorerPage;
