// lib/domain/repositories/voting_repository.dart
// واجهة المستودع المجردة — تعريف العقد بلا تنفيذ

import '../entities/candidate.dart';
import '../entities/voter.dart';
import '../entities/vote_receipt.dart';

/// العقد الذي يجب أن تنفّذه طبقة Data.
/// طبقة Domain لا تعرف شيئاً عن HTTP أو قاعدة بيانات.
abstract class VotingRepository {
  /// التحقق من أهلية الناخب عبر NFC UID
  Future<Voter?> checkVoter(String nfcUid);

  /// جلب قائمة المرشحين النشطين
  Future<List<Candidate>> getCandidates();

  /// تسجيل صوت وإرجاع الإيصال
  Future<VoteReceipt> castVote(String nfcUid, int candidateId);

  /// فحص صحة الاتصال بالخادم
  Future<bool> healthCheck();
}
