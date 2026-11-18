// [OWNER: M1] Routes cho Auth, Onboarding, Medical Disclaimer (F26) & Health (F01-F06)
import 'package:go_router/go_router.dart';

import '../../features/auth_privacy/presentation/onboarding_disclaimer_screen.dart';
import '../../features/health/presentation/health_dashboard_screen.dart';

final List<RouteBase> healthRoutes = [
  GoRoute(
    path: '/onboarding',
    name: 'onboarding',
    builder: (context, state) => const OnboardingDisclaimerScreen(),
  ),
  GoRoute(
    path: '/health',
    name: 'health_dashboard',
    builder: (context, state) => const HealthDashboardScreen(),
  ),
];
