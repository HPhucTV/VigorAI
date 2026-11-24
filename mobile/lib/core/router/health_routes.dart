// [OWNER: M1] Routes cho Onboarding Wizard, Auth, Ho so (/profile) & Health (F01-F06, F19 UI, F24 Anh)
import 'package:go_router/go_router.dart';

import '../../features/auth_privacy/presentation/app_launch_gate.dart';
import '../../features/auth_privacy/presentation/login_screen.dart';
import '../../features/auth_privacy/presentation/onboarding_disclaimer_screen.dart';
import '../../features/auth_privacy/presentation/profile_settings_screen.dart';
import '../../features/auth_privacy/presentation/register_screen.dart';
import '../../features/health/biometrics/presentation/biometrics_screen.dart';
import '../../features/health/food_scan/presentation/food_scan_screen.dart';
import '../../features/health/hydration/presentation/hydration_screen.dart';
import '../../features/health/nutrition/presentation/nutrition_screen.dart';
import '../../features/health/presentation/health_dashboard_screen.dart';
import '../../features/health/progress_photos/presentation/progress_photos_screen.dart';
import '../../features/health/sleep/presentation/sleep_screen.dart';
import '../../features/health/supplements/presentation/supplements_screen.dart';
import '../theme/app_theme.dart';

final List<RouteBase> healthRoutes = [
  GoRoute(
    path: '/onboarding',
    name: 'onboarding',
    builder: (context, state) {
      final mode = state.uri.queryParameters['mode'];
      if (mode == 'reconfigure' || mode == 'fresh') {
        return VigorAdaptiveTheme(
          child: OnboardingDisclaimerScreen(
            isReconfigureMode: mode == 'reconfigure',
          ),
        );
      }
      return const VigorAdaptiveTheme(child: AppLaunchGate());
    },
  ),
  GoRoute(
    path: '/login',
    name: 'login',
    builder: (context, state) => const VigorAdaptiveTheme(child: LoginScreen()),
  ),
  GoRoute(
    path: '/register',
    name: 'register',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: RegisterScreen()),
  ),
  GoRoute(
    path: '/profile',
    name: 'profile_settings',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: ProfileSettingsScreen()),
  ),
  GoRoute(
    path: '/health',
    name: 'health_dashboard',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: HealthDashboardScreen()),
  ),
  GoRoute(
    path: '/health/biometrics',
    name: 'health_biometrics',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: BiometricsScreen()),
  ),
  GoRoute(
    path: '/health/hydration',
    name: 'health_hydration',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: HydrationScreen()),
  ),
  GoRoute(
    path: '/health/nutrition',
    name: 'health_nutrition',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: NutritionScreen()),
  ),
  GoRoute(
    path: '/health/sleep',
    name: 'health_sleep',
    builder: (context, state) => const VigorAdaptiveTheme(child: SleepScreen()),
  ),
  GoRoute(
    path: '/health/supplements',
    name: 'health_supplements',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: SupplementsScreen()),
  ),
  GoRoute(
    path: '/health/food-scan',
    name: 'health_food_scan',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: FoodScanScreen()),
  ),
  GoRoute(
    path: '/health/progress-photos',
    name: 'health_progress_photos',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: ProgressPhotosScreen()),
  ),
];
