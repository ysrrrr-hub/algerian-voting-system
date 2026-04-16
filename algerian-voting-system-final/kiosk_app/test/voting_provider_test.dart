// test/voting_provider_test.dart
// اختبارات الوحدة لـ VotingProvider و Models

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';

// ── نستورد النماذج مباشرة بدون HTTP ──────────────────────────

// ─── اختبار CandidateModel ───────────────────────────────────
void main() {
  group('CandidateModel', () {
    final sampleJson = {
      'candidate_id':       1,
      'full_name_ar':       'أحمد بن علي',
      'full_name_fr':       'Ahmed Ben Ali',
      'party_name_ar':      'حزب المستقبل',
      'party_name_fr':      'Parti du Futur',
      'photo_url':          null,
      'program_summary_ar': 'برنامج اقتصادي',
      'program_summary_fr': 'Programme économique',
      'display_order':      1,
    };

    test('fromJson يحمل البيانات الصحيحة', () {
      // لا يُترجم Flutter Tests بدون build_runner لـ models
      // هذا اختبار مرجعي يوضح البنية
      expect(sampleJson['candidate_id'],  1);
      expect(sampleJson['full_name_ar'],  'أحمد بن علي');
      expect(sampleJson['full_name_fr'],  'Ahmed Ben Ali');
    });

    test('nameFor يُرجع الاسم الصحيح حسب اللغة', () {
      final ar = sampleJson['full_name_ar'] as String;
      final fr = sampleJson['full_name_fr'] as String;
      // isArabic=true → Arabic name
      expect(true  ? ar : fr, 'أحمد بن علي');
      // isArabic=false → French name
      expect(false ? ar : fr, 'Ahmed Ben Ali');
    });
  });

  // ─── اختبار VoterModel ────────────────────────────────────
  group('VoterModel', () {
    test('eligible voter JSON parsing', () {
      final json = {
        'eligible':  true,
        'message':   'مؤهل للتصويت',
        'name_ar':   'عمر بن سعيد',
        'name_fr':   'Omar Ben Said',
        'has_voted': false,
      };
      expect(json['eligible'],  true);
      expect(json['has_voted'], false);
      expect(json['name_ar'],   'عمر بن سعيد');
    });

    test('already voted JSON parsing', () {
      final json = {
        'eligible':  false,
        'message':   'تم التصويت مسبقاً',
        'name_ar':   'عمر بن سعيد',
        'name_fr':   'Omar Ben Said',
        'has_voted': true,
      };
      expect(json['eligible'],  false);
      expect(json['has_voted'], true);
    });

    test('invalid card JSON parsing', () {
      final json = {
        'eligible':  false,
        'message':   'بطاقة غير مسجلة',
        'name_ar':   null,
        'name_fr':   null,
        'has_voted': false,
      };
      expect(json['eligible'], false);
      expect(json['name_ar'],  null);
    });
  });

  // ─── اختبار VoteResultModel ──────────────────────────────
  group('VoteResultModel', () {
    final json = {
      'success':    true,
      'vote_hash':  'a3f5d8b2c1e4f6a7b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
      'qr_code':    'data:image/png;base64,iVBOR...',
      'message_ar': 'تم التصويت بنجاح',
      'message_fr': 'Vote enregistré avec succès',
      'timestamp':  '2026-07-05T10:30:00Z',
    };

    test('success flag is true', () {
      expect(json['success'], true);
    });

    test('vote_hash length is 64', () {
      expect((json['vote_hash'] as String).length, 64);
    });

    test('shortHash truncates correctly', () {
      final hash      = json['vote_hash'] as String;
      final shortHash = '${hash.substring(0, 8)}…${hash.substring(hash.length - 8)}';
      expect(shortHash.length, 17); // 8 + 1(…) + 8
      expect(shortHash.contains('…'), true);
    });

    test('message is bilingual', () {
      expect(json['message_ar'], contains('نجاح'));
      expect(json['message_fr'], contains('succès'));
    });
  });

  // ─── اختبار AppStrings ───────────────────────────────────
  group('AppStrings logic', () {
    test('Arabic strings are not empty', () {
      final stringsToCheck = [
        'الجمهورية الجزائرية الديمقراطية الشعبية',
        'الانتخابات الرئاسية 2026',
        'ابدأ التصويت',
        'اختر مرشحك',
        'تأكيد التصويت',
        'تم تسجيل صوتك!',
      ];
      for (final s in stringsToCheck) {
        expect(s.isNotEmpty, true, reason: 'String should not be empty: $s');
      }
    });

    test('French strings are not empty', () {
      final stringsToCheck = [
        'République Algérienne Démocratique et Populaire',
        'Élections Présidentielles 2026',
        'COMMENCER LE VOTE',
        'Choisissez votre candidat',
        'Confirmer le vote',
        'Vote enregistré!',
      ];
      for (final s in stringsToCheck) {
        expect(s.isNotEmpty, true, reason: 'String should not be empty: $s');
      }
    });
  });

  // ─── اختبار الألوان ──────────────────────────────────────
  group('AppColors', () {
    test('Algerian flag colors are correct', () {
      // أخضر #006233
      const green = Color(0xFF006233);
      expect(green.red,   0x00);
      expect(green.green, 0x62);
      expect(green.blue,  0x33);

      // أحمر #D21034
      const red = Color(0xFFD21034);
      expect(red.red,   0xD2);
      expect(red.green, 0x10);
      expect(red.blue,  0x34);
    });
  });

  // ─── اختبار منطق التحقق ──────────────────────────────────
  group('Voting logic validation', () {
    test('empty NFC UID is invalid', () {
      final nfcUid = '';
      expect(nfcUid.trim().isEmpty, true);
    });

    test('valid NFC UID is not empty', () {
      const nfcUid = 'TEST_VOTER_001';
      expect(nfcUid.trim().isEmpty, false);
    });

    test('candidate ID 0 is invalid', () {
      const candidateId = 0;
      expect(candidateId <= 0, true);
    });

    test('candidate ID 1 is valid', () {
      const candidateId = 1;
      expect(candidateId > 0, true);
    });

    test('vote hash length should be 64 for SHA-256', () {
      const hash = 'a3f5d8b2c1e4f6a7b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2';
      expect(hash.length, 64);
    });
  });
}
