// lib/presentation/screens/error_already_voted_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import 'welcome_screen.dart';

class ErrorAlreadyVotedScreen extends StatefulWidget {
  const ErrorAlreadyVotedScreen({super.key});

  @override
  State<ErrorAlreadyVotedScreen> createState() => _ErrorAlreadyVotedScreenState();
}

class _ErrorAlreadyVotedScreenState extends State<ErrorAlreadyVotedScreen> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 10), () {
      if (mounted) {
        context.read<VotingProvider>().resetLanguage();
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (_) => const WelcomeScreen()),
          (_) => false,
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final p = context.watch<VotingProvider>();
    final s = p.strings;

    return _ErrorBase(
      icon:       Icons.how_to_vote_rounded,
      iconColor:  AppColors.algerianRed,
      bgColor:    AppColors.redSurface,
      title:      s.alreadyVotedTitle,
      message:    s.alreadyVotedMsg,
      primaryLabel:   s.backToStart,
      onPrimary: () {
        p.resetLanguage();
        Navigator.pushAndRemoveUntil(
          context,
          MaterialPageRoute(builder: (_) => const WelcomeScreen()),
          (_) => false,
        );
      },
    );
  }
}


// lib/presentation/screens/error_invalid_card_screen.dart

class ErrorInvalidCardScreen extends StatelessWidget {
  const ErrorInvalidCardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<VotingProvider>();
    final s = p.strings;

    return _ErrorBase(
      icon:       Icons.credit_card_off_rounded,
      iconColor:  AppColors.warning,
      bgColor:    const Color(0xFFFFF8E1),
      title:      s.invalidCardTitle,
      message:    s.invalidCardMsg,
      primaryLabel:   s.retryBtn,
      secondaryLabel: s.callAgent,
      onPrimary:  () => Navigator.pop(context),
      onSecondary: () {
        // في بيئة الإنتاج: إرسال إشارة لموظف المكتب
        Navigator.pop(context);
      },
    );
  }
}


// ─── قالب مشترك لشاشات الخطأ ────────────────────────────────────
class _ErrorBase extends StatelessWidget {
  final IconData  icon;
  final Color     iconColor, bgColor;
  final String    title, message, primaryLabel;
  final String?   secondaryLabel;
  final VoidCallback onPrimary;
  final VoidCallback? onSecondary;

  const _ErrorBase({
    required this.icon,
    required this.iconColor,
    required this.bgColor,
    required this.title,
    required this.message,
    required this.primaryLabel,
    this.secondaryLabel,
    required this.onPrimary,
    this.onSecondary,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
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
                    // ─── أيقونة ────────────────────────────
                    Container(
                      width: 110, height: 110,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: bgColor,
                        border: Border.all(
                            color: iconColor.withOpacity(0.4), width: 2),
                      ),
                      child: Icon(icon, size: 60, color: iconColor),
                    ),

                    const SizedBox(height: 24),

                    Text(
                      title,
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        fontFamily:  'Tajawal',
                        fontSize:    24,
                        fontWeight:  FontWeight.w800,
                        color:       iconColor,
                      ),
                    ),

                    const SizedBox(height: 12),

                    Text(
                      message,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontFamily: 'Tajawal',
                        fontSize:   15,
                        color:      AppColors.textSecondary,
                        height:     1.6,
                      ),
                    ),

                    const SizedBox(height: 32),

                    // ─── الأزرار ───────────────────────────
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        if (secondaryLabel != null) ...[
                          OutlinedButton.icon(
                            onPressed: onSecondary,
                            icon:  const Icon(Icons.support_agent_rounded),
                            label: Text(secondaryLabel!,
                                style: const TextStyle(
                                    fontFamily: 'Tajawal', fontSize: 15)),
                          ),
                          const SizedBox(width: 14),
                        ],
                        ElevatedButton(
                          onPressed: onPrimary,
                          child: Text(
                            primaryLabel,
                            style: const TextStyle(
                              fontFamily:  'Tajawal',
                              fontSize:    16,
                              fontWeight:  FontWeight.w700,
                              color:       Colors.white,
                            ),
                          ),
                        ),
                      ],
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
