// [LOCKED STUB - Ket hop 3 danh sach route doc lap tu M1, M2, M4]
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'ai_analytics_routes.dart';
import 'gym3d_workout_routes.dart';
import 'health_routes.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/onboarding',
    routes: [
      ...healthRoutes,
      ...gym3dWorkoutRoutes,
      ...aiAnalyticsRoutes,
    ],
  );
});
