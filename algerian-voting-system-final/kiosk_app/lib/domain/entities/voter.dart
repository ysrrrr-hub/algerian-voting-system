// lib/domain/entities/voter.dart
// كيان الناخب — طبقة المنطق (لا يعتمد على أي إطار عمل)

class Voter {
  final String nfcUid;
  final String nameAr;
  final String nameFr;
  final bool   eligible;
  final bool   hasVoted;

  const Voter({
    required this.nfcUid,
    required this.nameAr,
    required this.nameFr,
    required this.eligible,
    required this.hasVoted,
  });

  String nameFor(bool isArabic) => isArabic ? nameAr : nameFr;

  @override
  bool operator ==(Object other) =>
      other is Voter && other.nfcUid == nfcUid;

  @override
  int get hashCode => nfcUid.hashCode;
}
