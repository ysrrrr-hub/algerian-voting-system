// lib/main.dart
// نقطة دخول التطبيق

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';

import 'core/constants/app_theme.dart';
import 'presentation/providers/voting_provider.dart';
import 'presentation/screens/welcome_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // وضع Kiosk: قفل الاتجاه + ملء الشاشة
  await SystemChrome.setPreferredOrientations([
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]);
  await SystemChrome.setEnabledSystemUIMode(SystemUiMode.immersiveSticky);

  // تحميل إعدادات اللغة المحفوظة
  final provider = VotingProvider();
  await provider.init();

  runApp(VotingApp(provider: provider));
}

class VotingApp extends StatelessWidget {
  final VotingProvider provider;
  const VotingApp({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: provider,
      child: MaterialApp(
        title:              'نظام التصويت الإلكتروني 2026',
        debugShowCheckedModeBanner: false,
        theme:              AppTheme.lightTheme,
        home:               const WelcomeScreen(),
        builder: (context, child) => Directionality(
          textDirection: TextDirection.rtl,
          child: child!,
        ),
      ),
    );
  }
}
