// lib/presentation/widgets/voting_progress_indicator.dart
// مؤشر تقدم خطوات التصويت (1 من 4)

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class VotingProgressIndicator extends StatelessWidget {
  final int  currentStep;   // 1-based
  final int  totalSteps;
  final bool isArabic;

  const VotingProgressIndicator({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color:   AppColors.backgroundCard,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Row(children: [
        // ─── نص الخطوة ─────────────────────────────────────
        Text(
          isArabic
              ? 'الخطوة $currentStep من $totalSteps'
              : 'Étape $currentStep sur $totalSteps',
          style: const TextStyle(
            fontFamily:  'Tajawal',
            fontSize:    13,
            fontWeight:  FontWeight.w600,
            color:       AppColors.algerianGreen,
          ),
        ),
        const SizedBox(width: 14),

        // ─── شريط التقدم ────────────────────────────────────
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value:     currentStep / totalSteps,
              minHeight: 6,
              backgroundColor:  AppColors.borderLight,
              valueColor: const AlwaysStoppedAnimation<Color>(
                  AppColors.algerianGreen),
            ),
          ),
        ),

        const SizedBox(width: 14),

        // ─── نقاط الخطوات ───────────────────────────────────
        Row(
          children: List.generate(totalSteps, (i) {
            final done   = i + 1 < currentStep;
            final active = i + 1 == currentStep;
            return Padding(
              padding: const EdgeInsets.only(left: 4),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 300),
                width:  active ? 20 : 8,
                height: 8,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  color: done || active
                      ? AppColors.algerianGreen
                      : AppColors.borderLight,
                ),
                child: done
                    ? const Icon(Icons.check, size: 6, color: Colors.white)
                    : null,
              ),
            );
          }),
        ),
      ]),
    );
  }
}

/// مؤشر دائري مع أيقونة للشاشات الانتقالية
class CircularStepIndicator extends StatelessWidget {
  final int  step;
  final int  total;
  final bool isArabic;

  const CircularStepIndicator({
    super.key,
    required this.step,
    required this.total,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: List.generate(total, (i) {
        final done   = i + 1 < step;
        final active = i + 1 == step;
        return Row(children: [
          if (i > 0)
            Container(
              width: 24, height: 1.5,
              color: i < step
                  ? AppColors.algerianGreen
                  : AppColors.borderLight,
            ),
          AnimatedContainer(
            duration: const Duration(milliseconds: 300),
            width: active ? 36 : 28,
            height: active ? 36 : 28,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: done
                  ? AppColors.algerianGreen
                  : active
                      ? AppColors.algerianGreen
                      : AppColors.backgroundMain,
              border: Border.all(
                color: done || active
                    ? AppColors.algerianGreen
                    : AppColors.borderLight,
                width: 2,
              ),
            ),
            child: Center(
              child: done
                  ? const Icon(Icons.check_rounded,
                        size: 16, color: Colors.white)
                  : Text(
                      '${i + 1}',
                      style: TextStyle(
                        fontFamily:  'Tajawal',
                        fontSize:    active ? 15 : 12,
                        fontWeight:  FontWeight.w700,
                        color: active || done
                            ? Colors.white
                            : AppColors.textHint,
                      ),
                    ),
            ),
          ),
        ]);
      }),
    );
  }
}
