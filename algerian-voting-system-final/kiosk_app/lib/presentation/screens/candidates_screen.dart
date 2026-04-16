// lib/presentation/screens/candidates_screen.dart
// شاشة اختيار المرشح — شبكة 5 بطاقات

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import '../widgets/candidate_card.dart';
import '../widgets/voting_progress_indicator.dart';
import 'confirmation_screen.dart';

class CandidatesScreen extends StatefulWidget {
  const CandidatesScreen({super.key});
  @override
  State<CandidatesScreen> createState() => _CandidatesScreenState();
}

class _CandidatesScreenState extends State<CandidatesScreen> {
  @override
  void initState() {
    super.initState();
    // نجلب المرشحين عند أول ظهور للشاشة
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<VotingProvider>().loadCandidates();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<VotingProvider>(builder: (_, p, __) {
      final s = p.strings;

      return Scaffold(
        body: Column(children: [
          const AlgerianFlagBar(height: 8),
          _StepBar(step: 3, total: 4, isArabic: p.isArabic),

          // ─── رأس الصفحة ──────────────────────────────
          Container(
            color:   AppColors.backgroundCard,
            padding: const EdgeInsets.symmetric(
                horizontal: 24, vertical: 12),
            child: Row(children: [
              const Icon(Icons.how_to_vote_rounded,
                  color: AppColors.algerianGreen, size: 22),
              const SizedBox(width: 10),
              Expanded(
                child: Text(
                  s.candidatesTitle,
                  style: const TextStyle(
                    fontFamily:  'Tajawal',
                    fontSize:    18,
                    fontWeight:  FontWeight.w700,
                    color:       AppColors.textPrimary,
                  ),
                ),
              ),
              // مؤشر الاختيار
              if (p.selectedId != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color:        AppColors.greenSurface,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: AppColors.greenBorder),
                  ),
                  child: Row(children: [
                    const Icon(Icons.check_circle,
                        size: 14, color: AppColors.algerianGreen),
                    const SizedBox(width: 4),
                    Text(
                      s.selectedBadge,
                      style: const TextStyle(
                        fontFamily:  'Tajawal',
                        fontSize:    12,
                        fontWeight:  FontWeight.w600,
                        color:       AppColors.algerianGreen,
                      ),
                    ),
                  ]),
                ),
            ]),
          ),

          const Divider(height: 1),

          // ─── شبكة المرشحين ───────────────────────────
          Expanded(
            child: _buildBody(p),
          ),

          // ─── شريط التأكيد السفلي ─────────────────────
          _BottomBar(
            isArabic: p.isArabic,
            enabled:  p.selectedId != null,
            label:    s.confirm,
            onTap: () => Navigator.push(context, MaterialPageRoute(
              builder: (_) => const ConfirmationScreen(),
            )),
          ),
        ]),
      );
    });
  }

  Widget _buildBody(VotingProvider p) {
    if (p.candidatesState == VotingState.loading) {
      return const Center(
        child: CircularProgressIndicator(color: AppColors.algerianGreen),
      );
    }
    if (p.candidatesState == VotingState.error || p.candidates.isEmpty) {
      return Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.wifi_off_rounded,
              size: 48, color: AppColors.textHint),
          const SizedBox(height: 12),
          Text(
            p.strings.connectionError,
            style: const TextStyle(
              fontFamily: 'Tajawal',
              color:      AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: () => p.loadCandidates(),
            child: Text(p.strings.retryBtn),
          ),
        ]),
      );
    }

    return Padding(
      padding: const EdgeInsets.all(16),
      child: GridView.builder(
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount:   5,
          childAspectRatio: 0.62,
          crossAxisSpacing: 14,
          mainAxisSpacing:  14,
        ),
        itemCount: p.candidates.length,
        itemBuilder: (_, i) {
          final c = p.candidates[i];
          return CandidateCard(
            candidate:  c,
            isSelected: p.selectedId == c.candidateId,
            isArabic:   p.isArabic,
            onTap:      () => p.selectCandidate(c.candidateId),
          );
        },
      ),
    );
  }
}

// ─── شريط الزر السفلي ───────────────────────────────────────────
class _BottomBar extends StatelessWidget {
  final bool         isArabic, enabled;
  final String       label;
  final VoidCallback onTap;
  const _BottomBar({
    required this.isArabic, required this.enabled,
    required this.label,    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color:   AppColors.backgroundCard,
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      child: SafeArea(
        top: false,
        child: SizedBox(
          width:  double.infinity,
          height: 54,
          child: ElevatedButton(
            onPressed: enabled ? onTap : null,
            style: ElevatedButton.styleFrom(
              backgroundColor: enabled
                  ? AppColors.algerianGreen
                  : AppColors.borderLight,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
            child: Text(
              label,
              style: TextStyle(
                fontFamily:  'Tajawal',
                fontSize:    18,
                fontWeight:  FontWeight.w700,
                color: enabled ? Colors.white : AppColors.textHint,
              ),
            ),
          ),
        ),
      ),
    );
  }
}

// ─── _StepBar helper ─────────────────────────────────────────
class _StepBar extends StatelessWidget {
  final int step, total;
  final bool isArabic;
  const _StepBar({required this.step, required this.total, required this.isArabic});
  @override
  Widget build(BuildContext context) => VotingProgressIndicator(
    currentStep: step, totalSteps: total, isArabic: isArabic,
  );
}
