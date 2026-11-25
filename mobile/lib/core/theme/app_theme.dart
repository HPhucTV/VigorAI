// [OWNER: M1] Theme Mau 01 Obsidian Performance Lab (Dark) & Alabaster Performance Lab (Light), Helper Tu thich ung & Provider
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../network/dio_client.dart';

class AppColors {
  AppColors._();

  // Brand & Telemetry Colors (readable across Light & Dark where referenced statically)
  static const Color primary = Color(0xFF0284C7);
  static const Color accent = Color(0xFF0D9488);
  static const Color volt = Color(0xFFCCFF00);
  static const Color voltOnLight = Color(0xFF4D7C0F);

  // Light Mode tokens (Alabaster Performance Lab)
  static const Color lightScaffold = Color(0xFFF4F6F9);
  static const Color lightCard = Color(0xFFFFFFFF);
  static const Color lightElevated = Color(0xFFEDF1F7);
  static const Color lightCardBorder = Color(0xFFE4E9F1);
  static const Color lightPrimary = Color(0xFF0F172A);
  static const Color lightAccent = Color(0xFF0284C7);

  // Dark Mode tokens (Obsidian Performance Lab - Mau 01)
  static const Color darkPrimary = Color(0xFFCCFF00);
  static const Color darkAccent = Color(0xFF38BDF8);
  static const Color darkScaffold = Color(0xFF090B0F);
  static const Color darkCard = Color(0xFF12161E);
  static const Color darkElevated = Color(0xFF19202C);
  static const Color darkCardBorder = Color(0x14FFFFFF);
  static const Color darkNavBar = Color(0xFF141923);

  // Mau chuc nang Suc khoe
  static const Color hydrationBlue = Color(0xFF0EA5E9);
  static const Color calorieOrange = Color(0xFFF97316);
  static const Color sleepPurple = Color(0xFF8B5CF6);
  static const Color stepTeal = Color(0xFF14B8A6);
  static const Color warningRed = Color(0xFFEF4444);

  // Mau Ban do Co bap 3D & Ban do Phuc hoi 3D (Khoa chuan theo workout_sprint2_test & Blender MCP)
  static const Color musclePrimaryRed = Color(0xFFE53935);
  static const Color muscleSecondaryOrange = Color(0xFFFB8C00);
  static const Color muscleStabilizerYellow = Color(0xFFFDD835);
  static const Color muscleRecoveredGreen = Color(0xFF43A047);
  static const Color muscleNeutralGrey = Color(0xFF9E9E9E);

  static bool isDark(BuildContext context) =>
      Theme.of(context).brightness == Brightness.dark;

  static Color tintedSurface(
    BuildContext context,
    Color baseColor, {
    double lightAlpha = 0.08,
    double darkAlpha = 0.16,
  }) {
    return baseColor.withValues(alpha: isDark(context) ? darkAlpha : lightAlpha);
  }

  static Color subtleSurface(BuildContext context) =>
      isDark(context) ? darkElevated : lightElevated;

  static Color elevatedSurface(BuildContext context) =>
      isDark(context) ? darkElevated : lightElevated;

  static Color accentStrong(BuildContext context) =>
      isDark(context) ? darkPrimary : lightPrimary;

  static Color telemetryCyan(BuildContext context) =>
      isDark(context) ? darkAccent : lightAccent;

  static Color secondaryText(BuildContext context) =>
      Theme.of(context).colorScheme.onSurfaceVariant;

  static Color subtleBorder(BuildContext context) =>
      isDark(context) ? darkCardBorder : lightCardBorder;

  static List<BoxShadow> cardShadow(BuildContext context) => isDark(context)
      ? const []
      : const [
          BoxShadow(
            color: Color(0x0A0F172A),
            blurRadius: 24,
            offset: Offset(0, 8),
          ),
        ];
}

class AppTheme {
  AppTheme._();

  static TextTheme _buildTextTheme(TextTheme base, Color onSurface, Color muted) {
    return base.copyWith(
      headlineMedium: base.headlineMedium?.copyWith(
        color: onSurface,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.8,
        fontFeatures: const [FontFeature.tabularFigures()],
      ),
      headlineSmall: base.headlineSmall?.copyWith(
        color: onSurface,
        fontWeight: FontWeight.w800,
        letterSpacing: -0.6,
        fontFeatures: const [FontFeature.tabularFigures()],
      ),
      titleLarge: base.titleLarge?.copyWith(
        color: onSurface,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.4,
      ),
      titleMedium: base.titleMedium?.copyWith(
        color: onSurface,
        fontWeight: FontWeight.w700,
        letterSpacing: -0.2,
      ),
      bodyMedium: base.bodyMedium?.copyWith(
        color: onSurface,
        height: 1.4,
      ),
      bodySmall: base.bodySmall?.copyWith(
        color: muted,
        height: 1.35,
      ),
    );
  }

  static ThemeData get lightTheme {
    final baseScheme = ColorScheme.fromSeed(
      seedColor: AppColors.lightPrimary,
      secondary: AppColors.lightAccent,
      brightness: Brightness.light,
    );
    final colorScheme = baseScheme.copyWith(
      primary: AppColors.lightPrimary,
      onPrimary: Colors.white,
      secondary: AppColors.lightAccent,
      onSecondary: Colors.white,
      surface: AppColors.lightCard,
      onSurface: AppColors.lightPrimary,
      onSurfaceVariant: const Color(0xFF64748B),
      surfaceContainerLowest: AppColors.lightScaffold,
      surfaceContainerLow: AppColors.lightCard,
      surfaceContainer: AppColors.lightCard,
      surfaceContainerHigh: AppColors.lightElevated,
      surfaceContainerHighest: const Color(0xFFE2E8F0),
      outlineVariant: AppColors.lightCardBorder,
    );
    final baseTheme = ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: Brightness.light,
    );
    return baseTheme.copyWith(
      scaffoldBackgroundColor: AppColors.lightScaffold,
      textTheme: _buildTextTheme(
        baseTheme.textTheme,
        colorScheme.onSurface,
        colorScheme.onSurfaceVariant,
      ),
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: AppColors.lightScaffold,
        foregroundColor: colorScheme.onSurface,
        titleTextStyle: TextStyle(
          color: colorScheme.onSurface,
          fontSize: 18,
          fontWeight: FontWeight.w800,
          letterSpacing: -0.4,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: AppColors.lightCard,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.lightCardBorder),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.lightCard,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.lightCardBorder),
        ),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: AppColors.lightCard,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: const StadiumBorder(),
        side: const BorderSide(color: AppColors.lightCardBorder),
        backgroundColor: AppColors.lightCard,
        selectedColor: AppColors.lightPrimary.withValues(alpha: 0.12),
        labelStyle: TextStyle(
          fontSize: 12.5,
          fontWeight: FontWeight.w600,
          color: colorScheme.onSurface,
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: AppColors.lightCard,
        indicatorColor: AppColors.lightPrimary.withValues(alpha: 0.10),
        elevation: 0,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 11,
            fontWeight: selected ? FontWeight.bold : FontWeight.w500,
            color: selected
                ? AppColors.lightPrimary
                : colorScheme.onSurfaceVariant,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected
                ? AppColors.lightPrimary
                : colorScheme.onSurfaceVariant,
          );
        }),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.lightCardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.lightCardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.lightPrimary, width: 1.5),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          side: const BorderSide(color: AppColors.lightCardBorder),
        ),
      ),
    );
  }

  static ThemeData get darkTheme {
    final baseScheme = ColorScheme.fromSeed(
      seedColor: AppColors.darkAccent,
      secondary: AppColors.darkAccent,
      brightness: Brightness.dark,
    );
    final colorScheme = baseScheme.copyWith(
      primary: AppColors.darkPrimary,
      onPrimary: AppColors.darkScaffold,
      secondary: AppColors.darkAccent,
      onSecondary: AppColors.darkScaffold,
      surface: AppColors.darkCard,
      onSurface: const Color(0xFFF8FAFC),
      onSurfaceVariant: const Color(0xFF8B95A5),
      surfaceContainerLowest: AppColors.darkScaffold,
      surfaceContainerLow: const Color(0xFF0E1219),
      surfaceContainer: AppColors.darkCard,
      surfaceContainerHigh: AppColors.darkElevated,
      surfaceContainerHighest: const Color(0xFF232C3D),
      outlineVariant: AppColors.darkCardBorder,
    );
    final baseTheme = ThemeData(
      useMaterial3: true,
      colorScheme: colorScheme,
      brightness: Brightness.dark,
    );
    return baseTheme.copyWith(
      scaffoldBackgroundColor: AppColors.darkScaffold,
      textTheme: _buildTextTheme(
        baseTheme.textTheme,
        colorScheme.onSurface,
        colorScheme.onSurfaceVariant,
      ),
      appBarTheme: AppBarTheme(
        centerTitle: false,
        elevation: 0,
        scrolledUnderElevation: 0,
        backgroundColor: AppColors.darkScaffold,
        foregroundColor: colorScheme.onSurface,
        titleTextStyle: TextStyle(
          color: colorScheme.onSurface,
          fontSize: 18,
          fontWeight: FontWeight.w800,
          letterSpacing: -0.4,
        ),
      ),
      cardTheme: CardThemeData(
        elevation: 0,
        color: AppColors.darkCard,
        margin: EdgeInsets.zero,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.darkCardBorder),
        ),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: AppColors.darkCard,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(color: AppColors.darkCardBorder),
        ),
      ),
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: AppColors.darkCard,
        surfaceTintColor: Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
        ),
      ),
      chipTheme: ChipThemeData(
        shape: const StadiumBorder(),
        side: const BorderSide(color: AppColors.darkCardBorder),
        backgroundColor: AppColors.darkElevated,
        selectedColor: AppColors.darkPrimary.withValues(alpha: 0.18),
        labelStyle: TextStyle(
          fontSize: 12.5,
          fontWeight: FontWeight.w600,
          color: colorScheme.onSurface,
        ),
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: AppColors.darkNavBar,
        indicatorColor: AppColors.darkPrimary.withValues(alpha: 0.18),
        elevation: 0,
        labelTextStyle: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return TextStyle(
            fontSize: 11,
            fontWeight: selected ? FontWeight.bold : FontWeight.w500,
            color: selected
                ? AppColors.darkPrimary
                : colorScheme.onSurfaceVariant,
          );
        }),
        iconTheme: WidgetStateProperty.resolveWith((states) {
          final selected = states.contains(WidgetState.selected);
          return IconThemeData(
            color: selected
                ? AppColors.darkPrimary
                : colorScheme.onSurfaceVariant,
          );
        }),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.darkElevated,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.darkCardBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.darkCardBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: AppColors.darkPrimary, width: 1.4),
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          side: const BorderSide(color: AppColors.darkCardBorder),
        ),
      ),
    );
  }
}

enum AppThemePreference {
  system(code: 'SYSTEM', labelVi: 'Theo máy'),
  light(code: 'LIGHT', labelVi: 'Sáng'),
  dark(code: 'DARK', labelVi: 'Tối');

  final String code;
  final String labelVi;

  const AppThemePreference({required this.code, required this.labelVi});

  static AppThemePreference fromCode(String? raw) {
    switch (raw?.toUpperCase()) {
      case 'LIGHT':
        return AppThemePreference.light;
      case 'DARK':
        return AppThemePreference.dark;
      default:
        return AppThemePreference.system;
    }
  }
}

class ThemePreferenceNotifier extends StateNotifier<AppThemePreference> {
  final FlutterSecureStorage _storage;

  ThemePreferenceNotifier(this._storage) : super(AppThemePreference.system) {
    _restore();
  }

  Future<void> _restore() async {
    try {
      final raw = await _storage.read(key: StorageKeys.themeModePreference);
      if (raw != null && raw.isNotEmpty) {
        state = AppThemePreference.fromCode(raw);
      }
    } catch (_) {
      // An toan trong widget test / moi truong khong co plugin platform
    }
  }

  Future<void> setPreference(AppThemePreference pref) async {
    state = pref;
    try {
      await _storage.write(
        key: StorageKeys.themeModePreference,
        value: pref.code,
      );
    } catch (_) {
      // Ignore in test environments
    }
  }

  Future<void> toggleQuickLightDark(Brightness currentBrightness) async {
    final next = currentBrightness == Brightness.dark
        ? AppThemePreference.light
        : AppThemePreference.dark;
    await setPreference(next);
  }
}

final themePreferenceProvider =
    StateNotifierProvider<ThemePreferenceNotifier, AppThemePreference>((ref) {
  final storage = ref.watch(secureStorageProvider);
  return ThemePreferenceNotifier(storage);
});

/// Wrapper giup doi Light / Dark Mode tuc thi trong toan app ma khong sua main.dart.
class VigorAdaptiveTheme extends ConsumerWidget {
  final Widget child;

  const VigorAdaptiveTheme({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final pref = ref.watch(themePreferenceProvider);
    if (pref == AppThemePreference.system) {
      return child;
    }
    final targetTheme = pref == AppThemePreference.dark
        ? AppTheme.darkTheme
        : AppTheme.lightTheme;
    return AnimatedTheme(
      data: targetTheme,
      duration: const Duration(milliseconds: 220),
      curve: Curves.easeOutCubic,
      child: child,
    );
  }
}
