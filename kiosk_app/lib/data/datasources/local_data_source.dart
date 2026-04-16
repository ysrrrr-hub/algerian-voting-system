// lib/data/datasources/local_data_source.dart
// التخزين المحلي — تخزين مؤقت للمرشحين + إعدادات اللغة

import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/candidate_model.dart';

class LocalDataSource {
  static const _keyLanguage    = 'selected_language_ar';
  static const _keyCandidates  = 'cached_candidates';
  static const _keyCacheTime   = 'candidates_cache_time';
  static const _cacheTtlHours  = 6;  // مدة صلاحية الـ cache: 6 ساعات

  // ─── اللغة ──────────────────────────────────────────────────
  Future<bool> getIsArabic() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_keyLanguage) ?? true;
  }

  Future<void> setIsArabic(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_keyLanguage, value);
  }

  // ─── المرشحون (cache) ─────────────────────────────────────
  Future<List<CandidateModel>?> getCachedCandidates() async {
    final prefs = await SharedPreferences.getInstance();

    // تحقق من انتهاء الصلاحية
    final cacheTime = prefs.getInt(_keyCacheTime) ?? 0;
    final now       = DateTime.now().millisecondsSinceEpoch;
    final ttlMs     = _cacheTtlHours * 3600 * 1000;

    if (now - cacheTime > ttlMs) return null;   // منتهي الصلاحية

    final raw = prefs.getString(_keyCandidates);
    if (raw == null) return null;

    try {
      final List<dynamic> list = jsonDecode(raw);
      return list
          .cast<Map<String, dynamic>>()
          .map(CandidateModel.fromJson)
          .toList();
    } catch (_) {
      return null;
    }
  }

  Future<void> cacheCandidates(List<CandidateModel> candidates) async {
    final prefs = await SharedPreferences.getInstance();
    final raw   = jsonEncode(candidates.map((c) => {
      'candidate_id':      c.candidateId,
      'full_name_ar':      c.fullNameAr,
      'full_name_fr':      c.fullNameFr,
      'party_name_ar':     c.partyNameAr,
      'party_name_fr':     c.partyNameFr,
      'photo_url':         c.photoUrl,
      'program_summary_ar': c.programAr,
      'program_summary_fr': c.programFr,
      'display_order':     c.displayOrder,
    }).toList());
    await prefs.setString(_keyCandidates, raw);
    await prefs.setInt(_keyCacheTime, DateTime.now().millisecondsSinceEpoch);
  }

  Future<void> clearCache() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_keyCandidates);
    await prefs.remove(_keyCacheTime);
  }

  // ─── إعدادات الكيوسك ─────────────────────────────────────
  Future<Map<String, dynamic>> getKioskSettings() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'is_arabic':       prefs.getBool(_keyLanguage) ?? true,
      'auto_reset_secs': prefs.getInt('auto_reset_secs') ?? 30,
      'show_dev_input':  prefs.getBool('show_dev_input') ?? true,
    };
  }

  Future<void> setAutoResetSeconds(int seconds) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('auto_reset_secs', seconds);
  }
}
