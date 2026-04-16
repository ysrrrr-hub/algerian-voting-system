// lib/presentation/screens/voter_verified_screen.dart
// شاشة التحقق الناجح من هوية الناخب

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import '../widgets/voting_progress_indicator.dart';
import 'candidates_screen.dart';

class VoterVerifiedScreen extends StatefulWidget {
  const VoterVerifiedScreen({super.key});
  @override
  State<VoterVerifiedScreen> createState() => _VoterVerifiedScreenState();
}

class _VoterVerifiedScreenState extends State<VoterVerifiedScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double>   _scale;
  late Animation<double>   _fade;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync:    this,
      duration: const Duration(milliseconds: 700),
    );
    _scale = CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut);
    _fade  = CurvedAnimation(parent: _ctrl, curve: Curves.easeIn);
    _ctrl.forward();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p = context.watch<VotingProvider>();
    final s = p.strings;
    final voter = p.voter!;

    return Scaffold(
      body: Column(children: [
        const AlgerianFlagBar(height: 8),
        _StepBar(step: 2, total: 4, isArabic: p.isArabic),
        Expanded(
          child: Center(
            child: FadeTransition(
              opacity: _fade,
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 500),
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // ─── أيقونة نجاح ────────────────────
                      ScaleTransition(
                        scale: _scale,
                        child: Container(
                          width: 110, height: 110,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: AppColors.success,
                            boxShadow: [
                              BoxShadow(
                                color:      AppColors.success.withOpacity(0.3),
                                blurRadius: 24,
                                spreadRadius: 6,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.verified_user_rounded,
                            size:  60,
                            color: Colors.white,
                          ),
                        ),
                      ),

                      const SizedBox(height: 24),

                      Text(
                        s.verifiedTitle,
                        style: const TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    26,
                          fontWeight:  FontWeight.w800,
                          color:       AppColors.success,
                        ),
                      ),

                      const SizedBox(height: 16),

                      // ─── بطاقة الناخب ───────────────────
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color:        AppColors.greenSurface,
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                              color: AppColors.greenBorder, width: 1.5),
                        ),
                        child: Column(children: [
                          const Icon(Icons.person_rounded,
                              size: 40, color: AppColors.algerianGreen),
                          const SizedBox(height: 8),
                          Text(
                            voter.nameFor(p.isArabic),
                            style: const TextStyle(
                              fontFamily:  'Tajawal',
                              fontSize:    20,
                              fontWeight:  FontWeight.w700,
                              color:       AppColors.greenDark,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            s.voterEligible,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontFamily: 'Tajawal',
                              fontSize:   13,
                              color:      AppColors.textSecondary,
                            ),
                          ),
                        ]),
                      ),

                      const SizedBox(height: 28),

                      // ─── زر المتابعة ─────────────────────
                      SizedBox(
                        width: 260, height: 56,
                        child: ElevatedButton.icon(
                          onPressed: () => Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => const CandidatesScreen(),
                            ),
                          ),
                          icon:  const Icon(Icons.arrow_forward_rounded,
                              color: Colors.white),
                          label: Text(
                            s.proceedToVote,
                            style: const TextStyle(
                              fontFamily: 'Tajawal',
                              fontSize:   17,
                              fontWeight: FontWeight.w700,
                              color:      Colors.white,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ]),
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
