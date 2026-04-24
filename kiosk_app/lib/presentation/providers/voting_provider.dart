// lib/presentation/providers/voting_provider.dart
// State Management — يدير حالة التطبيق بالكامل

import 'package:flutter/foundation.dart';
import '../../core/constants/app_strings.dart';
import '../../data/datasources/local_data_source.dart';
import '../../data/datasources/remote_data_source.dart';
import '../../data/models/candidate_model.dart';
import '../../data/models/voter_model.dart';
import '../../data/models/vote_result_model.dart';

enum VotingState { idle, loading, success, error }

enum VoterError { none, notFound, alreadyVoted, networkError }

class VotingProvider extends ChangeNotifier {
  final RemoteDataSource _api   = RemoteDataSource();
  final LocalDataSource  _local = LocalDataSource();

  // ─── اللغة ──────────────────────────────────────────────────
  bool _isArabic = true;
  bool get isArabic => _isArabic;
  AppStrings get strings => AppStrings(isArabic: _isArabic);

  /// تحميل إعدادات اللغة من SharedPreferences عند بدء التطبيق
  Future<void> init() async {
    _isArabic = await _local.getIsArabic();
    notifyListeners();
  }

  void setLanguage(bool arabic) {
    _isArabic = arabic;
    _local.setIsArabic(arabic);   // حفظ في SharedPreferences
    notifyListeners();
  }

  // ─── NFC / الناخب ───────────────────────────────────────────
  String       _nfcUid    = '';
  VoterModel?  _voter;
  VotingState  _voterState = VotingState.idle;
  VoterError   _voterError = VoterError.none;

  String       get nfcUid     => _nfcUid;
  VoterModel?  get voter      => _voter;
  VotingState  get voterState => _voterState;
  VoterError   get voterError => _voterError;

  Future<void> checkVoter(String nfcUid) async {
    _nfcUid    = nfcUid.trim();
    _voterState = VotingState.loading;
    _voterError = VoterError.none;
    _voter      = null;
    notifyListeners();

    try {
      final result = await _api.checkVoterStatus(_nfcUid);
      if (result == null) {
        _voterState = VotingState.error;
        _voterError = VoterError.networkError;
      } else if (result.hasVoted) {
        _voter      = result;
        _voterState = VotingState.error;
        _voterError = VoterError.alreadyVoted;
      } else if (!result.eligible) {
        _voterState = VotingState.error;
        _voterError = VoterError.notFound;
      } else {
        _voter      = result;
        _voterState = VotingState.success;
      }
    } catch (_) {
      _voterState = VotingState.error;
      _voterError = VoterError.networkError;
    }
    notifyListeners();
  }

  // ─── المرشحون ────────────────────────────────────────────────
  List<CandidateModel> _candidates    = [];
  int?                 _selectedId;
  VotingState          _candidatesState = VotingState.idle;

  List<CandidateModel> get candidates      => _candidates;
  int?                 get selectedId      => _selectedId;
  VotingState          get candidatesState => _candidatesState;

  CandidateModel? get selectedCandidate {
    if (_selectedId == null) return null;
    try {
      return _candidates.firstWhere((c) => c.candidateId == _selectedId);
    } catch (_) {
      return null;
    }
  }

  Future<void> loadCandidates() async {
    // أولاً: تحقق من الـ cache المحلي
    final cached = await _local.getCachedCandidates();
    if (cached != null && cached.isNotEmpty) {
      _candidates      = cached;
      _candidatesState = VotingState.success;
      notifyListeners();
      return;
    }

    // ثانياً: جلب من الخادم
    _candidatesState = VotingState.loading;
    notifyListeners();
    try {
      _candidates      = await _api.getCandidates();
      _candidatesState = VotingState.success;
      // حفظ في cache للاستخدام لاحقاً
      await _local.cacheCandidates(_candidates);
    } catch (_) {
      _candidatesState = VotingState.error;
    }
    notifyListeners();
  }

  void selectCandidate(int id) {
    _selectedId = id;
    notifyListeners();
  }

  // ─── التصويت ────────────────────────────────────────────────
  VoteResultModel? _voteResult;
  VotingState      _voteState = VotingState.idle;
  int              _processingStep = 0;  // 0-4 لشاشة المعالجة

  VoteResultModel? get voteResult     => _voteResult;
  VotingState      get voteState      => _voteState;
  int              get processingStep => _processingStep;

  Future<void> submitVote() async {
    if (_selectedId == null || _nfcUid.isEmpty) return;

    _voteState      = VotingState.loading;
    _processingStep = 0;
    notifyListeners();

    // محاكاة خطوات المعالجة المرئية
    for (int i = 1; i <= 4; i++) {
      await Future.delayed(const Duration(milliseconds: 600));
      _processingStep = i;
      notifyListeners();
    }

    try {
      _voteResult = await _api.castVote(_nfcUid, _selectedId!);
      _voteState  = VotingState.success;
    } on ApiException catch (e) {
      if (e.statusCode == 403) {
        // Here we could directly route to the already voted screen if needed
        // but setting _voterError to alreadyVoted achieves it natively via wrapper
        _voterError = VoterError.alreadyVoted;
      }
      _voteState = VotingState.error;
    } catch (_) {
      _voteState = VotingState.error;
    }
    notifyListeners();
  }

  // ─── إعادة التعيين ──────────────────────────────────────────
  void reset() {
    _nfcUid          = '';
    _voter           = null;
    _voterState      = VotingState.idle;
    _voterError      = VoterError.none;
    _selectedId      = null;
    _voteResult      = null;
    _voteState       = VotingState.idle;
    _processingStep  = 0;
    // نحتفظ بـ _candidates و _isArabic
    notifyListeners();
  }

  void resetLanguage() {
    reset();
    _isArabic = true;
    _local.setIsArabic(true);
    notifyListeners();
  }

  /// مسح الـ cache (للمشرف عند تحديث قائمة المرشحين)
  Future<void> clearCandidatesCache() async {
    await _local.clearCache();
    _candidates      = [];
    _candidatesState = VotingState.idle;
    notifyListeners();
  }
}
