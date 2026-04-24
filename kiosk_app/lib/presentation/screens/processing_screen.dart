// lib/presentation/screens/processing_screen.dart
// شاشة المعالجة — تُظهر خطوات التشفير والبلوكشين بشكل مرئي

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import 'success_screen.dart';
import 'welcome_screen.dart';

class ProcessingScreen extends StatefulWidget {
  const ProcessingScreen({super.key});
  @override
  State<ProcessingScreen> createState() => _ProcessingScreenState();
}

class _ProcessingScreenState extends State<ProcessingScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _submit());
  }

  Future<void> _submit() async {
    final p = context.read<VotingProvider>();
    await p.submitVote();
    if (!mounted) return;
    
    if (p.voteState == VotingState.success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const SuccessScreen()),
      );
    } else {
      if (p.voterError == VoterError.alreadyVoted) {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const ErrorAlreadyVotedScreen()),
        );
      } else {
        // خطأ: إعادة للبداية بعد 3 ثوانٍ
        await Future.delayed(const Duration(seconds: 3));
        if (mounted) {
          Navigator.pushAndRemoveUntil(
            context,
            MaterialPageRoute(builder: (_) => const WelcomeScreen()),
            (_) => false,
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<VotingProvider>(builder: (_, p, __) {
      final s    = p.strings;
      final step = p.processingStep;

      final steps = [
        (Icons.lock_rounded,          s.processingStep1),
        (Icons.link_rounded,          s.processingStep2),
        (Icons.verified_rounded,      s.processingStep3),
        (Icons.qr_code_2_rounded,     s.processingStep4),
      ];

      return Scaffold(
        backgroundColor: AppColors.backgroundDark,
        body: Column(children: [
          const AlgerianFlagBar(height: 8),
          Expanded(
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 480),
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // ─── أيقونة دوّارة ──────────────────
                      Container(
                        width: 100, height: 100,
                        decoration: BoxDecoration(
                          shape:  BoxShape.circle,
                          color:  AppColors.algerianGreen.withOpacity(0.15),
                          border: Border.all(
                              color: AppColors.algerianGreen, width: 2),
                        ),
                        child: const Center(
                          child: CircularProgressIndicator(
                            color:       AppColors.algerianGreen,
                            strokeWidth: 3,
                          ),
                        ),
                      ),

                      const SizedBox(height: 28),

                      Text(
                        s.processingTitle,
                        style: const TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    22,
                          fontWeight:  FontWeight.w700,
                          color:       Colors.white,
                        ),
                      ),

                      const SizedBox(height: 32),

                      // ─── خطوات المعالجة ─────────────────
                      ...steps.asMap().entries.map((e) {
                        final idx    = e.key;
                        final icon   = e.value.$1;
                        final label  = e.value.$2;
                        final done   = step > idx + 1;
                        final active = step == idx + 1;

                        return AnimatedContainer(
                          duration: const Duration(milliseconds: 300),
                          margin: const EdgeInsets.only(bottom: 12),
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: done
                                ? AppColors.algerianGreen.withOpacity(0.2)
                                : active
                                    ? AppColors.algerianGreen.withOpacity(0.1)
                                    : Colors.white.withOpacity(0.04),
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(
                              color: done
                                  ? AppColors.algerianGreen
                                  : active
                                      ? AppColors.algerianGreen.withOpacity(0.5)
                                      : Colors.white.withOpacity(0.1),
                              width: done || active ? 1.5 : 1,
                            ),
                          ),
                          child: Row(children: [
                            Icon(
                              done ? Icons.check_circle_rounded : icon,
                              color: done
                                  ? AppColors.algerianGreen
                                  : active
                                      ? Colors.white
                                      : Colors.white.withOpacity(0.3),
                              size: 22,
                            ),
                            const SizedBox(width: 12),
                            Text(
                              label,
                              style: TextStyle(
                                fontFamily:  'Tajawal',
                                fontSize:    14,
                                fontWeight:  active
                                    ? FontWeight.w700
                                    : FontWeight.w400,
                                color: done
                                    ? AppColors.algerianGreen
                                    : active
                                        ? Colors.white
                                        : Colors.white.withOpacity(0.35),
                              ),
                            ),
                            const Spacer(),
                            if (active)
                              const SizedBox(
                                width: 16, height: 16,
                                child: CircularProgressIndicator(
                                  color:       Colors.white,
                                  strokeWidth: 2,
                                ),
                              ),
                            if (done)
                              const Icon(Icons.done_all_rounded,
                                  color: AppColors.algerianGreen, size: 16),
                          ]),
                        );
                      }),
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
