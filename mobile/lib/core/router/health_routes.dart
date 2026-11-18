// [OWNER: M1] Routes cho Onboarding/Medical Disclaimer, Auth (F26) & Health (F01-F06)
import 'package:go_router/go_router.dart';

import '../../features/auth_privacy/presentation/login_screen.dart';
import '../../features/auth_privacy/presentation/onboarding_disclaimer_screen.dart';
import '../../features/auth_privacy/presentation/register_screen.dart';
import '../../features/health/presentation/health_dashboard_screen.dart';

final List<RouteBase> healthRoutes = [
  GoRoute(
    path: '/onboarding',
    name: 'onboarding',
    builder: (context, state) => const OnboardingDisclaimerScreen(),
  ),
  GoRoute(
    path: '/login',
    name: 'login',
    builder: (context, state) => const LoginScreen(),
  ),
  GoRoute(
    path: '/register',
    name: 'register',
    builder: (context, state) => const RegisterScreen(),
  ),
  GoRoute(
    path: '/health',
    name: 'health_dashboard',
    builder: (context, state) => const HealthDashboardScreen(),
  ),
];
