// lib/core/constants/app_theme.dart
// الثيم الكامل للتطبيق — Material 3 مع هوية جزائرية

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'app_colors.dart';

abstract class AppTheme {
  // ─── الثيم الفاتح ───────────────────────────────────────────
  static ThemeData get lightTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.light,

    colorScheme: const ColorScheme.light(
      primary:       AppColors.algerianGreen,
      onPrimary:     AppColors.textOnGreen,
      secondary:     AppColors.algerianRed,
      onSecondary:   AppColors.textOnDark,
      surface:       AppColors.backgroundCard,
      onSurface:     AppColors.textPrimary,
      error:         AppColors.error,
      outline:       AppColors.borderLight,
    ),

    scaffoldBackgroundColor: AppColors.backgroundMain,

    // ─── AppBar ─────────────────────────────────────
    appBarTheme: const AppBarTheme(
      backgroundColor:    AppColors.algerianGreen,
      foregroundColor:    AppColors.textOnDark,
      centerTitle:        true,
      elevation:          0,
      scrolledUnderElevation: 2,
      systemOverlayStyle: SystemUiOverlayStyle(
        statusBarColor:      Colors.transparent,
        statusBarBrightness: Brightness.dark,
        statusBarIconBrightness: Brightness.light,
      ),
      titleTextStyle: TextStyle(
        fontFamily:  'Tajawal',
        fontSize:    20,
        fontWeight:  FontWeight.w700,
        color:       AppColors.textOnDark,
        letterSpacing: 0.3,
      ),
    ),

    // ─── ElevatedButton ─────────────────────────────
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor:  AppColors.algerianGreen,
        foregroundColor:  AppColors.textOnDark,
        disabledBackgroundColor: AppColors.borderLight,
        minimumSize:      const Size(220, 58),
        padding:          const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        elevation:        3,
        shadowColor:      AppColors.shadowColor,
        textStyle: const TextStyle(
          fontFamily:  'Tajawal',
          fontSize:    18,
          fontWeight:  FontWeight.w700,
          letterSpacing: 0.5,
        ),
      ),
    ),

    // ─── OutlinedButton ─────────────────────────────
    outlinedButtonTheme: OutlinedButtonThemeData(
      style: OutlinedButton.styleFrom(
        foregroundColor: AppColors.algerianGreen,
        side: const BorderSide(color: AppColors.algerianGreen, width: 2),
        minimumSize: const Size(160, 52),
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        textStyle: const TextStyle(
          fontFamily:  'Tajawal',
          fontSize:    16,
          fontWeight:  FontWeight.w600,
        ),
      ),
    ),

    // ─── Card ───────────────────────────────────────
    cardTheme: CardTheme(
      color:     AppColors.backgroundCard,
      elevation: 4,
      shadowColor: AppColors.shadowColor,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      margin: const EdgeInsets.all(0),
    ),

    // ─── InputDecoration ────────────────────────────
    inputDecorationTheme: InputDecorationTheme(
      filled:      true,
      fillColor:   AppColors.backgroundMain,
      contentPadding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.borderLight),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.borderLight, width: 1.5),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.algerianGreen, width: 2.5),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: AppColors.algerianRed, width: 2),
      ),
      labelStyle: const TextStyle(
        fontFamily: 'Tajawal',
        color:      AppColors.textSecondary,
      ),
      hintStyle: const TextStyle(
        fontFamily: 'Tajawal',
        color:      AppColors.textHint,
      ),
    ),

    // ─── Typography ─────────────────────────────────
    textTheme: const TextTheme(
      displayLarge:  TextStyle(fontFamily: 'Tajawal', fontSize: 48, fontWeight: FontWeight.w800, color: AppColors.textPrimary),
      displayMedium: TextStyle(fontFamily: 'Tajawal', fontSize: 36, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
      displaySmall:  TextStyle(fontFamily: 'Tajawal', fontSize: 28, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
      headlineLarge: TextStyle(fontFamily: 'Tajawal', fontSize: 24, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
      headlineMedium:TextStyle(fontFamily: 'Tajawal', fontSize: 20, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
      headlineSmall: TextStyle(fontFamily: 'Tajawal', fontSize: 18, fontWeight: FontWeight.w600, color: AppColors.textPrimary),
      bodyLarge:     TextStyle(fontFamily: 'Tajawal', fontSize: 16, fontWeight: FontWeight.w400, color: AppColors.textPrimary),
      bodyMedium:    TextStyle(fontFamily: 'Tajawal', fontSize: 14, fontWeight: FontWeight.w400, color: AppColors.textSecondary),
      bodySmall:     TextStyle(fontFamily: 'Tajawal', fontSize: 12, fontWeight: FontWeight.w400, color: AppColors.textHint),
      labelLarge:    TextStyle(fontFamily: 'Tajawal', fontSize: 16, fontWeight: FontWeight.w700, color: AppColors.textPrimary),
    ),

    // ─── Divider ────────────────────────────────────
    dividerTheme: const DividerThemeData(
      color:     AppColors.borderLight,
      thickness: 1,
      space:     1,
    ),
  );

  // ─── دوال مساعدة ────────────────────────────────────────────
  static BoxDecoration cardDecoration({
    Color? color,
    double radius = 16,
    bool hasBorder = false,
    Color? borderColor,
  }) => BoxDecoration(
    color:  color ?? AppColors.backgroundCard,
    borderRadius: BorderRadius.circular(radius),
    border: hasBorder
        ? Border.all(color: borderColor ?? AppColors.borderLight, width: 1.5)
        : null,
    boxShadow: [
      BoxShadow(
        color:       AppColors.shadowColor,
        blurRadius:  12,
        offset:      const Offset(0, 4),
      ),
    ],
  );

  static BoxDecoration selectedCardDecoration({double radius = 16}) =>
    BoxDecoration(
      color: AppColors.greenSurface,
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(color: AppColors.algerianGreen, width: 3),
      boxShadow: [
        BoxShadow(
          color:      AppColors.algerianGreen.withOpacity(0.25),
          blurRadius: 16,
          spreadRadius: 2,
          offset:     const Offset(0, 4),
        ),
      ],
    );
}
