// lib/domain/usecases/get_candidates_usecase.dart
// حالة الاستخدام: جلب قائمة المرشحين

import '../entities/candidate.dart';
import '../repositories/voting_repository.dart';

class GetCandidatesUseCase {
  final VotingRepository _repo;
  const GetCandidatesUseCase(this._repo);

  Future<List<Candidate>> execute() => _repo.getCandidates();
}
