// lib/presentation/screens/language_screen.dart

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import 'nfc_scan_screen.dart';

class LanguageScreen extends StatelessWidget {
  const LanguageScreen({super.key});

  void _select(BuildContext ctx, bool arabic) {
    ctx.read<VotingProvider>().setLanguage(arabic);
    Navigator.push(ctx, MaterialPageRoute(
      builder: (_) => const NfcScanScreen(),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        const AlgerianFlagBar(height: 8),
        Expanded(
          child: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'اختر اللغة  /  Choisissez la langue',
                  style: TextStyle(
                    fontFamily:  'Tajawal',
                    fontSize:    24,
                    fontWeight:  FontWeight.w700,
                    color:       AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 48),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _LangCard(
                      emoji:    '🇩🇿',
                      title:    'العربية',
                      subtitle: 'Arabe',
                      onTap:    () => _select(context, true),
                    ),
                    const SizedBox(width: 32),
                    _LangCard(
                      emoji:    '🇫🇷',
                      title:    'Français',
                      subtitle: 'الفرنسية',
                      onTap:    () => _select(context, false),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ]),
    );
  }
}

class _LangCard extends StatefulWidget {
  final String emoji, title, subtitle;
  final VoidCallback onTap;
  const _LangCard({
    required this.emoji, required this.title,
    required this.subtitle, required this.onTap,
  });
  @override State<_LangCard> createState() => _LangCardState();
}

class _LangCardState extends State<_LangCard> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: widget.onTap,
      onTapDown: (_) => setState(() => _hovered = true),
      onTapUp:   (_) => setState(() => _hovered = false),
      onTapCancel: () => setState(() => _hovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 180, height: 200,
        decoration: BoxDecoration(
          color:        _hovered
              ? AppColors.greenSurface
              : AppColors.backgroundCard,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: _hovered
                ? AppColors.algerianGreen
                : AppColors.borderLight,
            width: _hovered ? 2.5 : 1.5,
          ),
          boxShadow: [
            BoxShadow(
              color:      _hovered
                  ? AppColors.algerianGreen.withOpacity(0.15)
                  : AppColors.shadowColor,
              blurRadius:   _hovered ? 20 : 8,
              offset:       const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(widget.emoji, style: const TextStyle(fontSize: 52)),
            const SizedBox(height: 12),
            Text(widget.title, style: const TextStyle(
              fontFamily:  'Tajawal',
              fontSize:    22,
              fontWeight:  FontWeight.w700,
              color:       AppColors.textPrimary,
            )),
            const SizedBox(height: 4),
            Text(widget.subtitle, style: const TextStyle(
              fontFamily: 'Tajawal',
              fontSize:   13,
              color:      AppColors.textSecondary,
            )),
          ],
        ),
      ),
    );
  }
}
