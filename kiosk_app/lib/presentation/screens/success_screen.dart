// lib/presentation/screens/success_screen.dart
// شاشة النجاح + QR Code الإيصال

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:qr_flutter/qr_flutter.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import 'welcome_screen.dart';

class SuccessScreen extends StatefulWidget {
  const SuccessScreen({super.key});
  @override
  State<SuccessScreen> createState() => _SuccessScreenState();
}

class _SuccessScreenState extends State<SuccessScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double>   _scale;
  late Animation<double>   _fade;

  // عداد تلقائي للعودة للبداية (30 ثانية)
  int _countdown = 30;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync:    this,
      duration: const Duration(milliseconds: 800),
    );
    _scale = CurvedAnimation(parent: _ctrl, curve: Curves.elasticOut);
    _fade  = CurvedAnimation(parent: _ctrl, curve: Curves.easeIn);
    _ctrl.forward();
    _startCountdown();
  }

  void _startCountdown() {
    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;
      if (_countdown > 1) {
        setState(() => _countdown--);
        _startCountdown();
      } else {
        _finish();
      }
    });
  }

  void _finish() {
    if (!mounted) return;
    context.read<VotingProvider>().resetLanguage();
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const WelcomeScreen()),
      (_) => false,
    );
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final p      = context.watch<VotingProvider>();
    final s      = p.strings;
    final result = p.voteResult;

    return Scaffold(
      body: Column(children: [
        const AlgerianFlagBar(height: 8),

        Expanded(
          child: FadeTransition(
            opacity: _fade,
            child: Container(
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end:   Alignment.bottomCenter,
                  colors: [AppColors.greenSurface, AppColors.algerianWhite],
                ),
              ),
              child: Center(
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 700),
                  child: Padding(
                    padding: const EdgeInsets.all(28),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        // ─── العمود الأيسر: نص ──────────────
                        Expanded(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              ScaleTransition(
                                scale: _scale,
                                child: Container(
                                  width: 90, height: 90,
                                  decoration: const BoxDecoration(
                                    shape: BoxShape.circle,
                                    color: AppColors.algerianGreen,
                                  ),
                                  child: const Icon(
                                    Icons.check_rounded,
                                    size:  52,
                                    color: Colors.white,
                                  ),
                                ),
                              ),
                              const SizedBox(height: 20),
                              Text(
                                s.successTitle,
                                style: const TextStyle(
                                  fontFamily:  'Tajawal',
                                  fontSize:    28,
                                  fontWeight:  FontWeight.w800,
                                  color:       AppColors.algerianGreen,
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                s.successSubtitle,
                                style: const TextStyle(
                                  fontFamily: 'Tajawal',
                                  fontSize:   15,
                                  color:      AppColors.textSecondary,
                                  height:     1.5,
                                ),
                              ),
                              if (result != null) ...[
                                const SizedBox(height: 16),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color:        AppColors.backgroundCard,
                                    borderRadius: BorderRadius.circular(10),
                                    border: Border.all(
                                        color: AppColors.borderLight),
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        s.voteHashLabel,
                                        style: const TextStyle(
                                          fontFamily:  'Tajawal',
                                          fontSize:    11,
                                          color:       AppColors.textSecondary,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        result.shortHash,
                                        style: const TextStyle(
                                          fontFamily:   'Tajawal',
                                          fontSize:     14,
                                          fontWeight:   FontWeight.w700,
                                          color:        AppColors.algerianGreen,
                                          letterSpacing: 1.5,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                              const SizedBox(height: 24),
                              SizedBox(
                                width:  200,
                                height: 50,
                                child: ElevatedButton.icon(
                                  onPressed: _finish,
                                  icon: const Icon(Icons.home_rounded,
                                      color: Colors.white, size: 20),
                                  label: Text(
                                    '${s.finishBtn} (${ _countdown})',
                                    style: const TextStyle(
                                      fontFamily:  'Tajawal',
                                      fontSize:    16,
                                      fontWeight:  FontWeight.w700,
                                      color:       Colors.white,
                                    ),
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),

                        const SizedBox(width: 32),

                        // ─── العمود الأيمن: QR Code ──────────
                        if (result != null)
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Container(
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color:        AppColors.backgroundCard,
                                  borderRadius: BorderRadius.circular(16),
                                  boxShadow: [
                                    BoxShadow(
                                      color:      AppColors.shadowColor,
                                      blurRadius: 16,
                                      offset:     const Offset(0, 4),
                                    ),
                                  ],
                                ),
                                child: Column(children: [
                                  QrImageView(
                                    data:            result.voteHash,
                                    version:         QrVersions.auto,
                                    size:            160,
                                    foregroundColor: AppColors.algerianGreen,
                                  ),
                                  const SizedBox(height: 10),
                                  Text(
                                    s.receiptTitle,
                                    style: const TextStyle(
                                      fontFamily:  'Tajawal',
                                      fontSize:    13,
                                      fontWeight:  FontWeight.w600,
                                      color:       AppColors.textPrimary,
                                    ),
                                  ),
                                  const SizedBox(height: 4),
                                  SizedBox(
                                    width: 160,
                                    child: Text(
                                      s.receiptHint,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        fontFamily: 'Tajawal',
                                        fontSize:   10,
                                        color:      AppColors.textSecondary,
                                        height:     1.4,
                                      ),
                                    ),
                                  ),
                                ]),
                              ),
                            ],
                          ),
                      ],
                    ),
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
