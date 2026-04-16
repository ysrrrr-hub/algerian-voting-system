// lib/presentation/widgets/candidate_card.dart

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_theme.dart';
import '../../data/models/candidate_model.dart';

class CandidateCard extends StatelessWidget {
  final CandidateModel candidate;
  final bool           isSelected;
  final bool           isArabic;
  final VoidCallback   onTap;

  const CandidateCard({
    super.key,
    required this.candidate,
    required this.isSelected,
    required this.isArabic,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve:    Curves.easeInOut,
        decoration: isSelected
            ? AppTheme.selectedCardDecoration()
            : AppTheme.cardDecoration(hasBorder: true),
        padding: const EdgeInsets.all(14),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // ─── صورة / أيقونة المرشح ─────────────────────
            Stack(
              alignment: Alignment.bottomRight,
              children: [
                Container(
                  width: 90, height: 90,
                  decoration: BoxDecoration(
                    shape:  BoxShape.circle,
                    color:  isSelected
                        ? AppColors.greenSurface
                        : AppColors.backgroundMain,
                    border: Border.all(
                      color: isSelected
                          ? AppColors.algerianGreen
                          : AppColors.borderLight,
                      width: 2.5,
                    ),
                  ),
                  child: ClipOval(
                    child: candidate.photoUrl != null
                        ? Image.network(
                            candidate.photoUrl!,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => _defaultAvatar(),
                          )
                        : _defaultAvatar(),
                  ),
                ),
                if (isSelected)
                  Container(
                    padding: const EdgeInsets.all(3),
                    decoration: const BoxDecoration(
                      color: AppColors.algerianGreen,
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(
                      Icons.check,
                      color: Colors.white,
                      size:  14,
                    ),
                  ),
              ],
            ),

            const SizedBox(height: 10),

            // ─── الاسم العربي ────────────────────────────
            Text(
              candidate.fullNameAr,
              textAlign: TextAlign.center,
              maxLines:  2,
              overflow:  TextOverflow.ellipsis,
              style: TextStyle(
                fontFamily:  'Tajawal',
                fontSize:    13,
                fontWeight:  FontWeight.w700,
                color: isSelected
                    ? AppColors.algerianGreen
                    : AppColors.textPrimary,
              ),
            ),

            const SizedBox(height: 3),

            // ─── الاسم الفرنسي ───────────────────────────
            Text(
              candidate.fullNameFr,
              textAlign: TextAlign.center,
              maxLines:  1,
              overflow:  TextOverflow.ellipsis,
              style: TextStyle(
                fontFamily: 'Tajawal',
                fontSize:   10,
                color:      AppColors.textSecondary,
                fontStyle:  FontStyle.italic,
              ),
            ),

            const SizedBox(height: 6),

            // ─── الحزب ──────────────────────────────────
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppColors.algerianGreen.withOpacity(0.1)
                    : AppColors.backgroundMain,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isSelected
                      ? AppColors.greenBorder
                      : AppColors.borderLight,
                ),
              ),
              child: Text(
                candidate.partyFor(isArabic),
                textAlign: TextAlign.center,
                maxLines:  2,
                overflow:  TextOverflow.ellipsis,
                style: TextStyle(
                  fontFamily: 'Tajawal',
                  fontSize:   9,
                  color: isSelected
                      ? AppColors.greenDark
                      : AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _defaultAvatar() => Icon(
    Icons.person_rounded,
    size:  48,
    color: AppColors.textHint,
  );
}
