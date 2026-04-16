// lib/domain/entities/vote_receipt.dart
// كيان إيصال التصويت

class VoteReceipt {
  final String voteHash;
  final String qrCode;
  final String timestamp;
  final String messageAr;
  final String messageFr;

  const VoteReceipt({
    required this.voteHash,
    required this.qrCode,
    required this.timestamp,
    required this.messageAr,
    required this.messageFr,
  });

  /// الـ hash المختصر للعرض على الشاشة
  String get shortHash {
    if (voteHash.length < 16) return voteHash;
    return '${voteHash.substring(0, 8)}…${voteHash.substring(voteHash.length - 8)}';
  }

  String messageFor(bool isArabic) => isArabic ? messageAr : messageFr;
}
