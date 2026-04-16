// lib/data/models/voter_model.dart

class VoterModel {
  final bool    eligible;
  final String  message;
  final String? nameAr;
  final String? nameFr;
  final bool    hasVoted;

  const VoterModel({
    required this.eligible,
    required this.message,
    this.nameAr,
    this.nameFr,
    required this.hasVoted,
  });

  factory VoterModel.fromJson(Map<String, dynamic> j) => VoterModel(
    eligible: j['eligible'] as bool? ?? false,
    message:  j['message']  as String? ?? '',
    nameAr:   j['name_ar']  as String?,
    nameFr:   j['name_fr']  as String?,
    hasVoted: j['has_voted'] as bool? ?? false,
  );

  String nameFor(bool isArabic) =>
      isArabic ? (nameAr ?? '') : (nameFr ?? nameAr ?? '');
}
