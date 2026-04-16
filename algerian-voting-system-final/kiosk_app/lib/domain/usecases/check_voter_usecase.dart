// lib/domain/usecases/check_voter_usecase.dart
// حالة الاستخدام: التحقق من الناخب

import '../entities/voter.dart';
import '../repositories/voting_repository.dart';

class CheckVoterUseCase {
  final VotingRepository _repo;
  const CheckVoterUseCase(this._repo);

  /// ينفّذ التحقق ويعيد الناخب أو null إذا لم يُعثر عليه
  Future<Voter?> execute(String nfcUid) async {
    if (nfcUid.trim().isEmpty) {
      throw ArgumentError('NFC UID لا يمكن أن يكون فارغاً');
    }
    return _repo.checkVoter(nfcUid.trim());
  }
}
