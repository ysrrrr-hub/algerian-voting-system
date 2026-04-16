// lib/presentation/widgets/bilingual_button.dart
// زر ثنائي اللغة — يعرض النص بالعربية والفرنسية معاً

import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

class BilingualButton extends StatelessWidget {
  final String   labelAr;
  final String   labelFr;
  final VoidCallback onPressed;
  final Color?   backgroundColor;
  final Color?   foregroundColor;
  final double   height;
  final double?  width;
  final IconData? icon;
  final bool     isLoading;
  final bool     enabled;

  const BilingualButton({
    super.key,
    required this.labelAr,
    required this.labelFr,
    required this.onPressed,
    this.backgroundColor,
    this.foregroundColor,
    this.height = 56,
    this.width,
    this.icon,
    this.isLoading = false,
    this.enabled = true,
  });

  @override
  Widget build(BuildContext context) {
    final bg = backgroundColor ?? AppColors.algerianGreen;
    final fg = foregroundColor ?? Colors.white;

    return SizedBox(
      height: height,
      width:  width,
      child: ElevatedButton(
        onPressed: (enabled && !isLoading) ? onPressed : null,
        style: ElevatedButton.styleFrom(
          backgroundColor:         bg,
          disabledBackgroundColor: AppColors.borderLight,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: enabled ? 3 : 0,
          shadowColor: bg.withOpacity(0.3),
        ),
        child: isLoading
            ? SizedBox(
                width: 22, height: 22,
                child: CircularProgressIndicator(
                  color:       fg,
                  strokeWidth: 2.5,
                ),
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (icon != null) ...[
                    Icon(icon, color: fg, size: 20),
                    const SizedBox(width: 8),
                  ],
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        labelAr,
                        style: TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    16,
                          fontWeight:  FontWeight.w700,
                          color:       fg,
                          height:      1.1,
                        ),
                      ),
                      Text(
                        labelFr,
                        style: TextStyle(
                          fontFamily:  'Tajawal',
                          fontSize:    11,
                          fontWeight:  FontWeight.w400,
                          color:       fg.withOpacity(0.8),
                          height:      1.1,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
      ),
    );
  }
}

/// نسخة مصغرة للأزرار الثانوية
class BilingualOutlinedButton extends StatelessWidget {
  final String       labelAr;
  final String       labelFr;
  final VoidCallback onPressed;

  const BilingualOutlinedButton({
    super.key,
    required this.labelAr,
    required this.labelFr,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        side:  const BorderSide(color: AppColors.algerianGreen, width: 1.5),
        shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10)),
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(labelAr, style: const TextStyle(
            fontFamily:  'Tajawal',
            fontSize:    14,
            fontWeight:  FontWeight.w600,
            color:       AppColors.algerianGreen,
            height:      1.1,
          )),
          Text(labelFr, style: const TextStyle(
            fontFamily: 'Tajawal',
            fontSize:   10,
            color:      AppColors.textSecondary,
            height:     1.1,
          )),
        ],
      ),
    );
  }
}
