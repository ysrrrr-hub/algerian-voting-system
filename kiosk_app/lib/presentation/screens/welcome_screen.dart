// lib/presentation/screens/welcome_screen.dart
// شاشة الترحيب الرئيسية — مع وضع تجريبي مخفي (3 نقرات على الشعار)

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/app_colors.dart';
import '../providers/voting_provider.dart';
import '../widgets/algerian_flag_bar.dart';
import '../widgets/demo_mode_dialog.dart';
import 'language_screen.dart';
import 'nfc_scan_screen.dart';

class WelcomeScreen extends StatefulWidget {
  const WelcomeScreen({super.key});
  @override
  State<WelcomeScreen> createState() => _WelcomeScreenState();
}

class _WelcomeScreenState extends State<WelcomeScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;
  late Animation<double>    _fade;
  late Animation<Offset>    _slide;

  // ─── Demo Mode: عداد النقرات ─────────────────────────
  int    _tapCount = 0;
  Timer? _tapTimer;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync:    this,
      duration: const Duration(milliseconds: 900),
    );
    _fade  = CurvedAnimation(parent: _ctrl, curve: Curves.easeOut);
    _slide = Tween<Offset>(begin: const Offset(0, 0.06), end: Offset.zero)
        .animate(CurvedAnimation(parent: _ctrl, curve: Curves.easeOut));
    _ctrl.forward();
  }

  @override
  void dispose() {
    _tapTimer?.cancel();
    _ctrl.dispose();
    super.dispose();
  }

  /// Demo Mode: عند النقر 3 مرات على الشعار خلال ثانيتين
  void _handleLogoTap() {
    _tapCount++;
    _tapTimer?.cancel();
    _tapTimer = Timer(const Duration(seconds: 2), () => _tapCount = 0);

    if (_tapCount >= 3) {
      _tapCount = 0;
      _tapTimer?.cancel();
      _showDemoDialog();
    }
  }

  void _showDemoDialog() {
    showDialog(
      context: context,
      builder: (_) => DemoModeDialog(
        onUidSelected: (uid) {
          Navigator.pop(context); // أغلق الـ dialog
          _onDemoUidSelected(uid);
        },
      ),
    );
  }

  /// Demo Mode: بعد اختيار UID — ادخل مباشرة لشاشة NFC مع UID جاهز
  void _onDemoUidSelected(String uid) {
    final p = context.read<VotingProvider>();
    p.reset();
    p.setLanguage(true); // الافتراضي: عربي
    // انتقل مباشرة لشاشة NFC — UID سيكون جاهزاً في الحقل
    Navigator.push(context, MaterialPageRoute(
      builder: (_) => NfcScanScreen(initialUid: uid),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(children: [
        const AlgerianFlagBar(height: 8),

        // ─── خلفية متدرجة ──────────────────────────────
        Expanded(
          child: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end:   Alignment.bottomCenter,
                colors: [
                  Color(0xFFF0F7F2),
                  AppColors.algerianWhite,
                ],
              ),
            ),
            child: FadeTransition(
              opacity: _fade,
              child: SlideTransition(
                position: _slide,
                child: _buildContent(context),
              ),
            ),
          ),
        ),

        const AlgerianFlagBar(height: 4),
      ]),
    );
  }

  Widget _buildContent(BuildContext context) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 700),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // ─── شعار (3 نقرات = Demo Mode) ──────────
              GestureDetector(
                onTap: _handleLogoTap,
                child: Container(
                  width: 110, height: 110,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.algerianGreen,
                    boxShadow: [
                      BoxShadow(
                        color:      AppColors.algerianGreen.withValues(alpha: 0.3),
                        blurRadius: 24,
                        spreadRadius: 4,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.how_to_vote_rounded,
                    size:  60,
                    color: Colors.white,
                  ),
                ),
              ),

              const SizedBox(height: 28),

              // ─── العنوان ─────────────────────────────
              const Text(
                'الجمهورية الجزائرية الديمقراطية الشعبية',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily:  'Tajawal',
                  fontSize:    22,
                  fontWeight:  FontWeight.w800,
                  color:       AppColors.textPrimary,
                  height:      1.4,
                ),
              ),
              const SizedBox(height: 4),
              const Text(
                'République Algérienne Démocratique et Populaire',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontFamily: 'Tajawal',
                  fontSize:   13,
                  color:      AppColors.textSecondary,
                  letterSpacing: 0.3,
                ),
              ),

              const SizedBox(height: 16),

              // ─── شريط فاصل ───────────────────────────
              Container(
                height: 3,
                width:  120,
                decoration: BoxDecoration(
                  gradient: AppColors.flagGradient,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),

              const SizedBox(height: 16),

              // ─── عنوان الانتخابات ─────────────────────
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 20, vertical: 8),
                decoration: BoxDecoration(
                  color:  AppColors.algerianGreen,
                  borderRadius: BorderRadius.circular(30),
                ),
                child: const Text(
                  'الانتخابات الرئاسية 2026',
                  style: TextStyle(
                    fontFamily:  'Tajawal',
                    fontSize:    18,
                    fontWeight:  FontWeight.w700,
                    color:       Colors.white,
                  ),
                ),
              ),

              const SizedBox(height: 36),

              // ─── زر البدء ────────────────────────────
              SizedBox(
                width:  280,
                height: 60,
                child: ElevatedButton(
                  onPressed: () {
                    context.read<VotingProvider>().reset();
                    Navigator.push(context, MaterialPageRoute(
                      builder: (_) => const LanguageScreen(),
                    ));
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.algerianGreen,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(14),
                    ),
                    elevation: 4,
                  ),
                  child: const Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.touch_app_rounded, color: Colors.white),
                      SizedBox(width: 10),
                      Text(
                        'ابدأ التصويت — VOTER',
                        style: TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    18,
                          fontWeight:  FontWeight.w700,
                          color:       Colors.white,
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // ─── شريط الأمان ─────────────────────────
              const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.lock_rounded,
                      size: 14, color: AppColors.textSecondary),
                  SizedBox(width: 6),
                  Text(
                    'نظام تصويت آمن مدعوم بالبلوكشين  •  '
                    'Système sécurisé par blockchain',
                    style: TextStyle(
                      fontFamily: 'Tajawal',
                      fontSize:   11,
                      color:      AppColors.textSecondary,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 8),

              // ─── تلميح Demo Mode (خفي) ─────────────
              if (kIsWeb)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: ElevatedButton.icon(
                    onPressed: _showDemoDialog,
                    icon: const Icon(Icons.build_rounded, size: 16),
                    label: const Text('Demo Mode (Web)'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.orange,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(20),
                      ),
                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    ),
                  ),
                )
              else
                Text(
                  'v1.0.0  •  اضغط الشعار 3 مرات للوضع التجريبي',
                  style: TextStyle(
                    fontFamily: 'Tajawal',
                    fontSize:   9,
                    color:      AppColors.textHint.withValues(alpha: 0.5),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
