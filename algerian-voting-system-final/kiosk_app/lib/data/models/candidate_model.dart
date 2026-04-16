// lib/data/models/candidate_model.dart

class CandidateModel {
  final int    candidateId;
  final String fullNameAr;
  final String fullNameFr;
  final String partyNameAr;
  final String partyNameFr;
  final String? photoUrl;
  final String? programAr;
  final String? programFr;
  final int    displayOrder;

  const CandidateModel({
    required this.candidateId,
    required this.fullNameAr,
    required this.fullNameFr,
    required this.partyNameAr,
    required this.partyNameFr,
    this.photoUrl,
    this.programAr,
    this.programFr,
    required this.displayOrder,
  });

  factory CandidateModel.fromJson(Map<String, dynamic> j) => CandidateModel(
    candidateId:  j['candidate_id']        as int,
    fullNameAr:   j['full_name_ar']         as String? ?? '',
    fullNameFr:   j['full_name_fr']         as String? ?? '',
    partyNameAr:  j['party_name_ar']        as String? ?? '',
    partyNameFr:  j['party_name_fr']        as String? ?? '',
    photoUrl:     j['photo_url']            as String?,
    programAr:    j['program_summary_ar']   as String?,
    programFr:    j['program_summary_fr']   as String?,
    displayOrder: j['display_order']        as int? ?? 0,
  );

  String nameFor(bool isArabic)  => isArabic ? fullNameAr  : fullNameFr;
  String partyFor(bool isArabic) => isArabic ? partyNameAr : partyNameFr;
}
