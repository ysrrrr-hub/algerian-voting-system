// lib/domain/entities/candidate.dart
// كيان المرشح — طبقة المنطق

class Candidate {
  final int    id;
  final String nameAr;
  final String nameFr;
  final String partyAr;
  final String partyFr;
  final String? photoUrl;
  final String? programAr;
  final String? programFr;
  final int    displayOrder;

  const Candidate({
    required this.id,
    required this.nameAr,
    required this.nameFr,
    required this.partyAr,
    required this.partyFr,
    this.photoUrl,
    this.programAr,
    this.programFr,
    required this.displayOrder,
  });

  String nameFor(bool isArabic)    => isArabic ? nameAr    : nameFr;
  String partyFor(bool isArabic)   => isArabic ? partyAr   : partyFr;
  String programFor(bool isArabic) => isArabic
      ? (programAr ?? '') : (programFr ?? '');

  @override
  bool operator ==(Object other) => other is Candidate && other.id == id;

  @override
  int get hashCode => id.hashCode;
}
