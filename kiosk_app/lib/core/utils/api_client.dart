// lib/core/utils/api_client.dart
// HTTP Client المركزي مع معالجة الأخطاء والـ timeout

import 'dart:convert';
import 'package:http/http.dart' as http;

// ─── Endpoints ──────────────────────────────────────────────────
abstract class ApiEndpoints {
  // غيّر هذا العنوان حسب بيئة التشغيل
  static const String _base = 'http://localhost:5000/api';

  static const String health      = '$_base/health';
  static const String candidates  = '$_base/candidates';
  static const String vote        = '$_base/vote';
  static const String verifyChain = '$_base/verify-chain';
  static const String stats       = '$_base/stats';

  static String voterStatus(String nfcUid) =>
      '$_base/voter-status/$nfcUid';
}

// ─── نتيجة الطلب ────────────────────────────────────────────────
class ApiResult<T> {
  final T?     data;
  final String? errorAr;
  final String? errorFr;
  final int     statusCode;

  const ApiResult._({
    this.data,
    this.errorAr,
    this.errorFr,
    required this.statusCode,
  });

  factory ApiResult.success(T data, {int statusCode = 200}) =>
      ApiResult._(data: data, statusCode: statusCode);

  factory ApiResult.failure(String ar, String fr, {int statusCode = 500}) =>
      ApiResult._(errorAr: ar, errorFr: fr, statusCode: statusCode);

  bool get isSuccess => data != null && errorAr == null;

  String error(bool isArabic) => isArabic ? (errorAr ?? '') : (errorFr ?? '');
}

// ─── HTTP Client ─────────────────────────────────────────────────
class ApiClient {
  static const Duration _timeout = Duration(seconds: 15);

  static final http.Client _client = http.Client();

  static Map<String, String> get _headers => {
    'Content-Type': 'application/json; charset=UTF-8',
    'Accept':       'application/json',
    'X-App-Source': 'kiosk',
  };

  /// GET request
  static Future<ApiResult<Map<String, dynamic>>> get(String url) async {
    try {
      final res = await _client
          .get(Uri.parse(url), headers: _headers)
          .timeout(_timeout);
      return _parse(res);
    } on Exception catch (e) {
      if (e.toString().contains('ClientException') || e.toString().contains('Failed host lookup')) {
        return ApiResult.failure(
          'تعذّر الاتصال بالخادم',
          'Impossible de contacter le serveur',
        );
      }
      return ApiResult.failure(
        'خطأ غير متوقع: $e',
        'Erreur inattendue: $e',
      );
    }
  }

  /// POST request
  static Future<ApiResult<Map<String, dynamic>>> post(
    String url,
    Map<String, dynamic> body,
  ) async {
    try {
      final res = await _client
          .post(Uri.parse(url),
              headers: _headers, body: jsonEncode(body))
          .timeout(_timeout);
      return _parse(res);
    } on Exception catch (e) {
      if (e.toString().contains('ClientException') || e.toString().contains('Failed host lookup')) {
        return ApiResult.failure(
          'تعذّر الاتصال بالخادم',
          'Impossible de contacter le serveur',
        );
      }
      return ApiResult.failure(
        'خطأ غير متوقع: $e',
        'Erreur inattendue: $e',
      );
    }
  }

  /// GET — يُرجع قائمة
  static Future<ApiResult<List<dynamic>>> getList(String url) async {
    try {
      final res = await _client
          .get(Uri.parse(url), headers: _headers)
          .timeout(_timeout);
      if (res.statusCode == 200) {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is List) return ApiResult.success(data);
        return ApiResult.failure(
          'تنسيق البيانات غير صحيح',
          'Format de données incorrect',
        );
      }
      return _parseError(res);
    } on Exception catch (e) {
      if (e.toString().contains('ClientException') || e.toString().contains('Failed host lookup')) {
        return ApiResult.failure(
          'تعذّر الاتصال بالخادم',
          'Impossible de contacter le serveur',
        );
      }
      return ApiResult.failure(
        'خطأ غير متوقع: $e',
        'Erreur inattendue: $e',
      );
    }
  }

  // ─── مساعد: تحليل الاستجابة ─────────────────────────────────
  static ApiResult<Map<String, dynamic>> _parse(http.Response res) {
    try {
      final Map<String, dynamic> body =
          jsonDecode(utf8.decode(res.bodyBytes));
      if (res.statusCode >= 200 && res.statusCode < 300) {
        return ApiResult.success(body, statusCode: res.statusCode);
      }
      return ApiResult.failure(
        body['error_ar'] ?? body['error'] ?? 'حدث خطأ',
        body['error_fr'] ?? body['error'] ?? 'Une erreur est survenue',
        statusCode: res.statusCode,
      );
    } catch (_) {
      return ApiResult.failure(
        'تعذّر تحليل رد الخادم',
        'Impossible de parser la réponse',
        statusCode: res.statusCode,
      );
    }
  }

  static ApiResult<T> _parseError<T>(http.Response res) {
    try {
      final body = jsonDecode(utf8.decode(res.bodyBytes));
      return ApiResult.failure(
        body['error_ar'] ?? 'حدث خطأ',
        body['error_fr'] ?? 'Une erreur est survenue',
        statusCode: res.statusCode,
      );
    } catch (_) {
      return ApiResult.failure(
        'خطأ ${res.statusCode}',
        'Erreur ${res.statusCode}',
        statusCode: res.statusCode,
      );
    }
  }
}
