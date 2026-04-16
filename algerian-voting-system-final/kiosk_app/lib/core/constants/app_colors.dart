// lib/core/constants/app_colors.dart
// نظام الألوان الكامل — مستوحى من العلم الجزائري

import 'package:flutter/material.dart';

abstract class AppColors {
  // ─── ألوان العلم الجزائري ───────────────────────────────────
  static const Color algerianGreen  = Color(0xFF006233);
  static const Color algerianRed    = Color(0xFFD21034);
  static const Color algerianWhite  = Color(0xFFFFFFFF);
  static const Color goldAccent     = Color(0xFFD4A017);

  // ─── تدرجات الأخضر ─────────────────────────────────────────
  static const Color greenDark      = Color(0xFF004D27);
  static const Color greenMedium    = Color(0xFF006233);
  static const Color greenLight     = Color(0xFF1A8C54);
  static const Color greenSurface   = Color(0xFFE8F5EE);
  static const Color greenBorder    = Color(0xFF80BC9C);

  // ─── تدرجات الأحمر ─────────────────────────────────────────
  static const Color redDark        = Color(0xFFA00D27);
  static const Color redMedium      = Color(0xFFD21034);
  static const Color redLight       = Color(0xFFE8405A);
  static const Color redSurface     = Color(0xFFFDE8EC);

  // ─── خلفيات ─────────────────────────────────────────────────
  static const Color backgroundMain = Color(0xFFF5F7F5);
  static const Color backgroundCard = Color(0xFFFFFFFF);
  static const Color backgroundDark = Color(0xFF0A1F14);  // للشاشات الاحتفالية

  // ─── نصوص ───────────────────────────────────────────────────
  static const Color textPrimary    = Color(0xFF1A2E1F);
  static const Color textSecondary  = Color(0xFF5A7062);
  static const Color textHint       = Color(0xFF9EB5A4);
  static const Color textOnDark     = Color(0xFFFFFFFF);
  static const Color textOnGreen    = Color(0xFFFFFFFF);

  // ─── حالات وظيفية ───────────────────────────────────────────
  static const Color success        = Color(0xFF28A745);
  static const Color warning        = Color(0xFFFFC107);
  static const Color error          = Color(0xFFD21034);
  static const Color info           = Color(0xFF1565C0);

  // ─── حدود وظلال ─────────────────────────────────────────────
  static const Color borderLight    = Color(0xFFDDE8DF);
  static const Color borderFocus    = Color(0xFF006233);
  static const Color shadowColor    = Color(0x1A006233);

  // ─── تدرجات جاهزة ───────────────────────────────────────────
  static const LinearGradient heroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end:   Alignment.bottomRight,
    colors: [greenDark, greenMedium, Color(0xFF1A7A44)],
  );

  static const LinearGradient flagGradient = LinearGradient(
    colors: [algerianGreen, algerianWhite, algerianRed],
    stops:  [0.0, 0.5, 1.0],
  );

  static const RadialGradient glowGreen = RadialGradient(
    colors: [Color(0x40006233), Color(0x00006233)],
  );
}
