// lib/data/models/vote_result_model.dart

class ReceiptModel {
  final String receiptCode;
  final String qrData;
  final String timestamp;
  final String privacyNoteAr;
  final String privacyNoteFr;

  const ReceiptModel({
    required this.receiptCode,
    required this.qrData,
    required this.timestamp,
    required this.privacyNoteAr,
    required this.privacyNoteFr,
  });

  factory ReceiptModel.fromJson(Map<String, dynamic> j) => ReceiptModel(
    receiptCode:   j['receipt_code']   as String? ?? '',
    qrData:        j['qr_data']        as String? ?? '',
    timestamp:     j['timestamp']      as String? ?? '',
    privacyNoteAr: j['privacy_note_ar'] as String? ?? '',
    privacyNoteFr: j['privacy_note_fr'] as String? ?? '',
  );
}

class VoteResultModel {
  final bool          success;
  final String        blockHash;
  final String        messageAr;
  final String        messageFr;
  final String        timestamp;
  final ReceiptModel? receipt;

  const VoteResultModel({
    required this.success,
    required this.blockHash,
    required this.messageAr,
    required this.messageFr,
    required this.timestamp,
    this.receipt,
  });

  factory VoteResultModel.fromJson(Map<String, dynamic> j) => VoteResultModel(
    success:   j['success']    as bool? ?? false,
    blockHash: j['block_hash'] as String? ?? '',
    messageAr: j['message_ar'] as String? ?? '',
    messageFr: j['message_fr'] as String? ?? '',
    timestamp: j['timestamp']  as String? ?? '',
    receipt:   j['receipt'] != null ? ReceiptModel.fromJson(j['receipt'] as Map<String, dynamic>) : null,
  );

  String messageFor(bool isArabic) => isArabic ? messageAr : messageFr;
  String get shortHash => blockHash.length >= 16
      ? '${blockHash.substring(0, 8)}…${blockHash.substring(blockHash.length - 8)}'
      : blockHash;
}
