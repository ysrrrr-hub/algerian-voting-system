// lib/presentation/screens/nfc_scan_screen.dart
// شاشة مسح بطاقة NFC — مع وضع تطوير لإدخال UID يدوياً

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import '../widgets/voting_progress_indicator.dart';
import 'voter_verified_screen.dart';
import 'error_already_voted_screen.dart';
import 'error_invalid_card_screen.dart';

class NfcScanScreen extends StatefulWidget {
  final String? initialUid;
  const NfcScanScreen({super.key, this.initialUid});
  @override
  State<NfcScanScreen> createState() => _NfcScanScreenState();
}

class _NfcScanScreenState extends State<NfcScanScreen>
    with SingleTickerProviderStateMixin {
  late final TextEditingController _ctrl;
  late AnimationController _pulseCtrl;
  late Animation<double>   _pulse;

  @override
  void initState() {
    super.initState();
    _ctrl = TextEditingController(text: widget.initialUid ?? 'TEST_VOTER_001');
    _pulseCtrl = AnimationController(
      vsync:    this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _pulse = Tween<double>(begin: 0.85, end: 1.0)
        .animate(CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut));
  }

  @override
  void dispose() {
    _ctrl.dispose();
    _pulseCtrl.dispose();
    super.dispose();
  }

  Future<void> _scan() async {
    final p = context.read<VotingProvider>();
    await p.checkVoter(_ctrl.text.trim());
    if (!mounted) return;

    switch (p.voterError) {
      case VoterError.none:
        Navigator.push(context, _route(const VoterVerifiedScreen()));
        break;
      case VoterError.alreadyVoted:
        Navigator.push(context, _route(const ErrorAlreadyVotedScreen()));
        break;
      case VoterError.notFound:
        Navigator.push(context, _route(const ErrorInvalidCardScreen()));
        break;
      case VoterError.networkError:
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              context.read<VotingProvider>().strings.connectionError,
              style: const TextStyle(fontFamily: 'Tajawal', fontSize: 16),
              textAlign: TextAlign.center,
            ),
            backgroundColor: Colors.red.shade800,
            duration: const Duration(seconds: 4),
          ),
        );
        break;
    }
  }

  PageRoute _route(Widget screen) =>
      MaterialPageRoute(builder: (_) => screen);

  @override
  Widget build(BuildContext context) {
    final p = context.watch<VotingProvider>();
    final s = p.strings;

    return Scaffold(
      body: Column(children: [
        const AlgerianFlagBar(height: 8),

        // ─── شريط التقدم ────────────────────────────────
        _StepBar(step: 1, total: 4, isArabic: p.isArabic),

        Expanded(
          child: Center(
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 600),
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    // ─── أيقونة NFC متحركة ───────────────
                    ScaleTransition(
                      scale: _pulse,
                      child: Container(
                        width: 140, height: 140,
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: AppColors.greenSurface,
                          border: Border.all(
                            color: AppColors.algerianGreen,
                            width: 3,
                          ),
                          boxShadow: [
                            BoxShadow(
                              color:      AppColors.algerianGreen.withOpacity(0.2),
                              blurRadius: 30,
                              spreadRadius: 8,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.contactless_rounded,
                          size:  72,
                          color: AppColors.algerianGreen,
                        ),
                      ),
                    ),

                    const SizedBox(height: 28),

                    Text(
                      s.scanTitle,
                      style: const TextStyle(
                        fontFamily:  'Tajawal',
                        fontSize:    24,
                        fontWeight:  FontWeight.w700,
                        color:       AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      s.scanInstruction,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontFamily: 'Tajawal',
                        fontSize:   15,
                        color:      AppColors.textSecondary,
                        height:     1.5,
                      ),
                    ),

                    const SizedBox(height: 32),

                    // ─── حقل إدخال يدوي (وضع التطوير) ───
                    Container(
                      decoration: BoxDecoration(
                        color:        AppColors.backgroundCard,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.borderLight),
                        boxShadow: [
                          BoxShadow(
                            color:      AppColors.shadowColor,
                            blurRadius: 8,
                            offset:     const Offset(0, 2),
                          ),
                        ],
                      ),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 4),
                      child: Row(children: [
                        const Icon(Icons.credit_card_rounded,
                            color: AppColors.algerianGreen),
                        const SizedBox(width: 10),
                        Expanded(
                          child: TextField(
                            controller:    _ctrl,
                            textAlign:     TextAlign.center,
                            textDirection: TextDirection.ltr,
                            style: const TextStyle(
                              fontFamily:  'Tajawal',
                              fontSize:    16,
                              fontWeight:  FontWeight.w600,
                              color:       AppColors.textPrimary,
                              letterSpacing: 2,
                            ),
                            decoration: InputDecoration(
                              border:      InputBorder.none,
                              hintText:    'NFC UID',
                              hintStyle:   TextStyle(
                                color:    AppColors.textHint,
                                fontSize: 14,
                              ),
                            ),
                          ),
                        ),
                      ]),
                    ),

                    const SizedBox(height: 24),

                    // ─── زر المسح ───────────────────────
                    if (p.voterState == VotingState.loading)
                      const CircularProgressIndicator(
                          color: AppColors.algerianGreen)
                    else
                      SizedBox(
                        width: 220, height: 56,
                        child: ElevatedButton.icon(
                          onPressed: _scan,
                          icon:  const Icon(Icons.nfc_rounded,
                              color: Colors.white),
                          label: Text(
                            '${s.confirm}  /  Scanner',
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
      ]),
    );
  }
}

// ─── شريط خطوات التقدم (re-export من voting_progress_indicator) ──────────────
// يُستخدم من nfc_scan_screen, voter_verified_screen, candidates_screen
class _StepBar extends StatelessWidget {
  final int  step, total;
  final bool isArabic;
  const _StepBar({
    required this.step,
    required this.total,
    required this.isArabic,
  });

  @override
  Widget build(BuildContext context) {
    return VotingProgressIndicator(
      currentStep: step,
      totalSteps:  total,
      isArabic:    isArabic,
    );
  }
}
