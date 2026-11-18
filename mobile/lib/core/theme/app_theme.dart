// [OWNER: M1] Theme sang/toi va Bang mau Giai phau 3D chuan hoa
import 'package:flutter/material.dart';

class AppColors {
  AppColors._();

  static const Color primary = Color(0xFF1565C0);
  static const Color accent = Color(0xFF00BFA5);

  // Mau Ban do Co bap 3D (F09) & Ban do Phuc hoi 3D (F23)
  static const Color musclePrimaryRed = Color(0xFFE53935);
  static const Color muscleSecondaryOrange = Color(0xFFFB8C00);
  static const Color muscleStabilizerYellow = Color(0xFFFDD835);
  static const Color muscleRecoveredGreen = Color(0xFF43A047);
  static const Color muscleNeutralGrey = Color(0xFF9E9E9E);
}

class AppTheme {
  AppTheme._();

  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        colorSchemeSeed: AppColors.primary,
        brightness: Brightness.light,
      );

  static ThemeData get darkTheme => ThemeData(
        useMaterial3: true,
        colorSchemeSeed: AppColors.primary,
        brightness: Brightness.dark,
      );
}
