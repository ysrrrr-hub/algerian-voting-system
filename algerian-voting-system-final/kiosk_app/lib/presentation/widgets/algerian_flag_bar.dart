// lib/presentation/widgets/algerian_flag_bar.dart
import 'package:flutter/material.dart';
import '../../core/constants/app_colors.dart';

/// شريط أعلى الشاشة بألوان العلم الجزائري
class AlgerianFlagBar extends StatelessWidget {
  final double height;
  const AlgerianFlagBar({super.key, this.height = 6});

  @override
  Widget build(BuildContext context) => SizedBox(
    height: height,
    child: Row(children: [
      Expanded(child: Container(color: AppColors.algerianGreen)),
      Expanded(child: Container(color: AppColors.algerianWhite)),
      Expanded(child: Container(color: AppColors.algerianRed)),
    ]),
  );
}
