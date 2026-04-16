// lib/presentation/widgets/security_badge.dart
// شارة الأمان — تُعرض في أسفل كل الشاشات

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class SecurityBadge extends StatelessWidget {
  final bool isArabic;
  const SecurityBadge({super.key, this.isArabic = true});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.lock_rounded,
              size: 13, color: AppColors.textHint),
          const SizedBox(width: 6),
          Text(
            isArabic
                ? 'نظام تصويت آمن • RSA-4096 + Blockchain'
                : 'Système sécurisé • RSA-4096 + Blockchain',
            style: const TextStyle(
              fontFamily: 'Tajawal',
              fontSize:   11,
              color:      AppColors.textHint,
            ),
          ),
          const SizedBox(width: 10),
          Container(
            width:  6, height: 6,
            decoration: const BoxDecoration(
              shape: BoxShape.circle,
              color: AppColors.success,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            isArabic ? 'متصل' : 'Connecté',
            style: const TextStyle(
              fontFamily: 'Tajawal',
              fontSize:   11,
              color:      AppColors.success,
            ),
          ),
        ],
      ),
    );
  }
}

/// شارة صغيرة للتشفير تُوضع داخل البطاقات
class EncryptionChip extends StatelessWidget {
  const EncryptionChip({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color:        AppColors.greenSurface,
        borderRadius: BorderRadius.circular(20),
        border:       Border.all(color: AppColors.greenBorder),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.shield_rounded, size: 12, color: AppColors.algerianGreen),
          SizedBox(width: 4),
          Text(
            'RSA-4096',
            style: TextStyle(
              fontFamily:  'Tajawal',
              fontSize:    10,
              fontWeight:  FontWeight.w600,
              color:       AppColors.algerianGreen,
            ),
          ),
        ],
      ),
    );
  }
}
