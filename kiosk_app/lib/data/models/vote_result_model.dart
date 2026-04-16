// lib/data/models/vote_result_model.dart

class VoteResultModel {
  final bool   success;
  final String voteHash;
  final String qrCode;
  final String messageAr;
  final String messageFr;
  final String timestamp;

  const VoteResultModel({
    required this.success,
    required this.voteHash,
    required this.qrCode,
    required this.messageAr,
    required this.messageFr,
    required this.timestamp,
  });

  factory VoteResultModel.fromJson(Map<String, dynamic> j) => VoteResultModel(
    success:   j['success']    as bool? ?? false,
    voteHash:  j['vote_hash']  as String? ?? '',
    qrCode:    j['qr_code']    as String? ?? '',
    messageAr: j['message_ar'] as String? ?? '',
    messageFr: j['message_fr'] as String? ?? '',
    timestamp: j['timestamp']  as String? ?? '',
  );

  String messageFor(bool isArabic) => isArabic ? messageAr : messageFr;
  String get shortHash => voteHash.length >= 16
      ? '${voteHash.substring(0, 8)}…${voteHash.substring(voteHash.length - 8)}'
      : voteHash;
}
