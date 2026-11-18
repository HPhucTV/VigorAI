// [OWNER: M4] Routes cho AI Food Scan (F19), Readiness & Recovery 3D (F20-F23) & Analytics (F22, F24)
import 'package:go_router/go_router.dart';

import '../../features/ai_analytics/presentation/ai_coach_hub_screen.dart';

final List<RouteBase> aiAnalyticsRoutes = [
  GoRoute(
    path: '/ai-coach',
    name: 'ai_coach_hub',
    builder: (context, state) => const AiCoachHubScreen(),
  ),
];
