// lib/domain/usecases/cast_vote_usecase.dart
// حالة الاستخدام: تسجيل الصوت

import '../entities/vote_receipt.dart';
import '../repositories/voting_repository.dart';

class CastVoteUseCase {
  final VotingRepository _repo;
  const CastVoteUseCase(this._repo);

  /// يُرسل الصوت ويُرجع الإيصال
  Future<VoteReceipt> execute(String nfcUid, int candidateId) async {
    if (nfcUid.trim().isEmpty) {
      throw ArgumentError('NFC UID مطلوب');
    }
    if (candidateId <= 0) {
      throw ArgumentError('candidate_id غير صالح');
    }
    return _repo.castVote(nfcUid.trim(), candidateId);
  }
}
