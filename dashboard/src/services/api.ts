// dashboard/src/services/api.ts

import axios from 'axios';

const BASE = 'http://209.38.44.237:5000';

const http = axios.create({
  baseURL: BASE,
  timeout: 12000,
  headers: { 'Content-Type': 'application/json' },
});

// ─── Types ──────────────────────────────────────────────────────
export interface VotingStats {
  total_voters:       number;
  voted_count:        number;
  remaining_count:    number;
  turnout_percentage: number;
  blockchain_length:  number;
  last_vote_time:     string | null;
}

export interface ChainStatus {
  valid:           boolean;
  message:         string;
  chain_length:    number;
  last_block_hash: string | null;
}

export interface BlockchainStatus {
  total_blocks: number;
  total_votes:  number;
  last_block: {
    index:         number;
    timestamp:     string;
    current_hash:  string;
    previous_hash: string;
    nonce:         number;
  } | null;
}

export interface AdminInfo {
  full_name: string;
  role:      string;
}

export interface LoginResponse {
  success:    boolean;
  token:      string;
  expires_in: number;
  admin:      AdminInfo;
}

export interface DecryptResult {
  candidate_id: number;
  name_ar:      string;
  name_fr:      string;
  votes:        number;
  percentage:   number;
}

export interface DecryptResponse {
  success:     boolean;
  total_votes: number;
  results:     DecryptResult[];
}

export interface WilayaStats {
  wilaya:       string;
  total_voters: number;
  voted_count:  number;
  turnout_pct:  number;
}

// ─── API calls ──────────────────────────────────────────────────
export const apiHealth         = ()              => http.get('/health');
export const apiStats          = ()              => http.get<VotingStats>('/stats');
export const apiVerifyChain    = ()              => http.get<ChainStatus>('/verify-chain');
export const apiBlockchainStatus = ()            => http.get<BlockchainStatus>('/blockchain/status');

export const apiLogin = (username: string, password: string) =>
  http.post<LoginResponse>('/admin/login', { username, password });

export const apiLogout = (token: string) =>
  http.post('/admin/logout', {}, { headers: { Authorization: `Bearer ${token}` } });

export const apiDecryptVotes = (token: string, password: string) =>
  http.post<DecryptResponse>(
    '/decrypt-votes',
    { private_key_password: password },
    { headers: { Authorization: `Bearer ${token}` } },
  );

export default http;

// ─── New endpoints ───────────────────────────────────────────

export interface AuditEntry {
  log_id:        number;
  action_type:   string;
  nfc_uid:       string | null;
  ip_address:    string | null;
  success:       boolean;
  error_message: string | null;
  timestamp:     string;
}

export interface AuditLogResponse {
  logs:   AuditEntry[];
  total:  number;
  limit:  number;
  offset: number;
}

export interface AllBlocksResponse {
  blocks: {
    block_index:    number;
    timestamp:      string;
    encrypted_vote: string;
    previous_hash:  string;
    current_hash:   string;
    nonce:          number;
  }[];
  total:  number;
  limit:  number;
  offset: number;
}

/** سجل المراجعة الأمنية */
export const apiAuditLog = (
  token:       string,
  actionType?: string,
  limit  = 200,
  offset = 0,
) => http.get<AuditLogResponse>('/audit-log', {
  headers: { Authorization: `Bearer ${token}` },
  params:  { action_type: actionType, limit, offset },
});

/** جميع كتل البلوكشين */
export const apiAllBlocks = (
  token:  string,
  limit  = 100,
  offset = 0,
) => http.get<AllBlocksResponse>('/blockchain/all', {
  headers: { Authorization: `Bearer ${token}` },
  params:  { limit, offset },
});

/** إحصائيات حسب الولاية */
export const apiWilayaStats = (token: string) =>
  http.get<WilayaStats[]>('/stats/wilaya', {
    headers: { Authorization: `Bearer ${token}` },
  });
