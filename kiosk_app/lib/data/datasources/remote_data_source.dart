// lib/data/datasources/remote_data_source.dart
// طبقة الاتصال بـ Flask API — جميع طلبات HTTP هنا

import '../models/candidate_model.dart';
import '../models/voter_model.dart';
import '../models/vote_result_model.dart';
import '../../core/utils/api_client.dart';

class RemoteDataSource {
  // ─── التحقق من أهلية الناخب ─────────────────────────────────
  Future<VoterModel?> checkVoterStatus(String nfcUid) async {
    final result = await ApiClient.get(ApiEndpoints.voterStatus(nfcUid));
    if (result.isSuccess && result.data != null) {
      return VoterModel.fromJson(result.data!);
    }
    // 404 = بطاقة غير مسجلة
    if (result.statusCode == 404) {
      return VoterModel(
        eligible: false,
        message:  result.errorAr ?? 'بطاقة غير مسجلة',
        hasVoted: false,
      );
    }
    return null;
  }

  // ─── جلب المرشحين ───────────────────────────────────────────
  Future<List<CandidateModel>> getCandidates() async {
    final result = await ApiClient.getList(ApiEndpoints.candidates);
    if (result.isSuccess && result.data != null) {
      return result.data!
          .cast<Map<String, dynamic>>()
          .map(CandidateModel.fromJson)
          .toList();
    }
    throw Exception(result.errorAr ?? 'Failed to load candidates');
  }

  // ─── إرسال الصوت ────────────────────────────────────────────
  Future<VoteResultModel> castVote(String nfcUid, int candidateId) async {
    final result = await ApiClient.post(ApiEndpoints.vote, {
      'nfc_uid':      nfcUid,
      'candidate_id': candidateId,
    });
    if (result.isSuccess && result.data != null) {
      return VoteResultModel.fromJson(result.data!);
    }
    throw Exception(result.errorAr ?? 'Failed to cast vote');
  }

  // ─── فحص صحة النظام ─────────────────────────────────────────
  Future<bool> healthCheck() async {
    final result = await ApiClient.get(ApiEndpoints.health);
    return result.isSuccess &&
        result.data?['status'] == 'healthy';
  }
}
