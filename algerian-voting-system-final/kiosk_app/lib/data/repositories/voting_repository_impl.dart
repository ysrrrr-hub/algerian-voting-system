// lib/data/repositories/voting_repository_impl.dart
// تنفيذ المستودع — يربط Domain بـ Data layer

import '../../domain/entities/candidate.dart';
import '../../domain/entities/voter.dart';
import '../../domain/entities/vote_receipt.dart';
import '../../domain/repositories/voting_repository.dart';
import '../datasources/remote_data_source.dart';
import '../models/candidate_model.dart';
import '../models/voter_model.dart';
import '../models/vote_result_model.dart';

class VotingRepositoryImpl implements VotingRepository {
  final RemoteDataSource _remote;
  const VotingRepositoryImpl(this._remote);

  // ─── تحويل Model → Entity ─────────────────────────────────
  static Voter _voterFromModel(VoterModel m, String nfcUid) => Voter(
    nfcUid:   nfcUid,
    nameAr:   m.nameAr ?? '',
    nameFr:   m.nameFr ?? '',
    eligible: m.eligible,
    hasVoted: m.hasVoted,
  );

  static Candidate _candidateFromModel(CandidateModel m) => Candidate(
    id:           m.candidateId,
    nameAr:       m.fullNameAr,
    nameFr:       m.fullNameFr,
    partyAr:      m.partyNameAr,
    partyFr:      m.partyNameFr,
    photoUrl:     m.photoUrl,
    programAr:    m.programAr,
    programFr:    m.programFr,
    displayOrder: m.displayOrder,
  );

  static VoteReceipt _receiptFromModel(VoteResultModel m) => VoteReceipt(
    voteHash:  m.voteHash,
    qrCode:    m.qrCode,
    timestamp: m.timestamp,
    messageAr: m.messageAr,
    messageFr: m.messageFr,
  );

  // ─── تنفيذ الواجهة ────────────────────────────────────────
  @override
  Future<Voter?> checkVoter(String nfcUid) async {
    final model = await _remote.checkVoterStatus(nfcUid);
    if (model == null) return null;
    return _voterFromModel(model, nfcUid);
  }

  @override
  Future<List<Candidate>> getCandidates() async {
    final models = await _remote.getCandidates();
    return models.map(_candidateFromModel).toList();
  }

  @override
  Future<VoteReceipt> castVote(String nfcUid, int candidateId) async {
    final model = await _remote.castVote(nfcUid, candidateId);
    return _receiptFromModel(model);
  }

  @override
  Future<bool> healthCheck() => _remote.healthCheck();
}
