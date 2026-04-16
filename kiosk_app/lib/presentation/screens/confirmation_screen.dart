// lib/presentation/screens/confirmation_screen.dart
// حوار تأكيد الاختيار النهائي

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import 'processing_screen.dart';

class ConfirmationScreen extends StatelessWidget {
  const ConfirmationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<VotingProvider>(builder: (_, p, __) {
      final s = p.strings;
      final c = p.selectedCandidate!;

      return Scaffold(
        body: Column(children: [
          const AlgerianFlagBar(height: 8),

          Expanded(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 520),
                child: Container(
                  margin:  const EdgeInsets.all(24),
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    color:        AppColors.backgroundCard,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color:      AppColors.shadowColor,
                        blurRadius: 24,
                        offset:     const Offset(0, 8),
                      ),
                    ],
                  ),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // ─── عنوان ──────────────────────────
                      Text(
                        s.confirmTitle,
                        style: const TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    22,
                          fontWeight:  FontWeight.w800,
                          color:       AppColors.textPrimary,
                        ),
                      ),

                      const SizedBox(height: 24),

                      // ─── بطاقة المرشح المختار ────────────
                      Container(
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color:        AppColors.greenSurface,
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                              color: AppColors.algerianGreen, width: 2),
                        ),
                        child: Column(children: [
                          Container(
                            width: 80, height: 80,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: AppColors.backgroundCard,
                              border: Border.all(
                                  color: AppColors.algerianGreen,
                                  width: 2.5),
                            ),
                            child: const Icon(Icons.person_rounded,
                                size: 44, color: AppColors.algerianGreen),
                          ),
                          const SizedBox(height: 10),
                          Text(
                            c.fullNameAr,
                            style: const TextStyle(
                              fontFamily:  'Tajawal',
                              fontSize:    18,
                              fontWeight:  FontWeight.w700,
                              color:       AppColors.greenDark,
                            ),
                          ),
                          Text(
                            c.fullNameFr,
                            style: const TextStyle(
                              fontFamily:  'Tajawal',
                              fontSize:    13,
                              color:       AppColors.textSecondary,
                              fontStyle:   FontStyle.italic,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 4),
                            decoration: BoxDecoration(
                              color: AppColors.algerianGreen.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              c.partyFor(p.isArabic),
                              style: const TextStyle(
                                fontFamily: 'Tajawal',
                                fontSize:   12,
                                color:      AppColors.algerianGreen,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ]),
                      ),

                      const SizedBox(height: 20),

                      // ─── تحذير عدم الرجوع ───────────────
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color:        AppColors.redSurface,
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(
                              color: AppColors.algerianRed.withOpacity(0.3)),
                        ),
                        child: Row(children: [
                          const Icon(Icons.warning_amber_rounded,
                              color: AppColors.algerianRed, size: 18),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              s.confirmWarning,
                              style: const TextStyle(
                                fontFamily: 'Tajawal',
                                fontSize:   12,
                                color:      AppColors.redDark,
                                height:     1.4,
                              ),
                            ),
                          ),
                        ]),
                      ),

                      const SizedBox(height: 24),

                      // ─── أزرار ──────────────────────────
                      Row(children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: () => Navigator.pop(context),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppColors.textSecondary,
                              side: const BorderSide(
                                  color: AppColors.borderLight, width: 1.5),
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12)),
                            ),
                            child: Text(s.cancelBtn,
                                style: const TextStyle(
                                    fontFamily:  'Tajawal',
                                    fontSize:    16,
                                    fontWeight:  FontWeight.w600)),
                          ),
                        ),
                        const SizedBox(width: 14),
                        Expanded(
                          flex: 2,
                          child: ElevatedButton(
                            onPressed: () => Navigator.pushReplacement(
                              context,
                              MaterialPageRoute(
                                  builder: (_) => const ProcessingScreen()),
                            ),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.algerianGreen,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12)),
                            ),
                            child: Text(
                              s.confirmBtn,
                              style: const TextStyle(
                                fontFamily:  'Tajawal',
                                fontSize:    16,
                                fontWeight:  FontWeight.w700,
                                color:       Colors.white,
                              ),
                            ),
                          ),
                        ),
                      ]),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ]),
      );
    });
  }
}
