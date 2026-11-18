// [OWNER: M2] Routes cho Thu vien 3D Blender (F07-F13) & Tap Gym (F14-F18, F25)
import 'package:go_router/go_router.dart';

import '../../features/workout/presentation/live_workout_logger_screen.dart';

final List<RouteBase> gym3dWorkoutRoutes = [
  GoRoute(
    path: '/workout/live',
    name: 'live_workout_logger',
    builder: (context, state) => const LiveWorkoutLoggerScreen(),
  ),
];
