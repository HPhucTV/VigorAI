// [OWNER: M2] Routes cho Thu vien 3D Blender (F07-F13) & Tap Gym (F14-F18, F25)
import 'package:go_router/go_router.dart';

import '../../features/gym3d/presentation/exercise_3d_detail_screen.dart';
import '../../features/gym3d/presentation/gym3d_library_screen.dart';
import '../../features/workout/presentation/live_workout_logger_screen.dart';
import '../../features/workout/presentation/routines_screen.dart';
import '../theme/app_theme.dart';

final List<RouteBase> gym3dWorkoutRoutes = [
  GoRoute(
    path: '/gym3d',
    name: 'gym3d_library',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: Gym3DLibraryScreen()),
  ),
  GoRoute(
    path: '/gym3d/exercise/:code',
    name: 'gym3d_exercise_detail',
    builder: (context, state) => VigorAdaptiveTheme(
      child: Exercise3DDetailScreen(
        exerciseCode: state.pathParameters['code'] ?? 'BARBELL_SQUAT',
      ),
    ),
  ),
  GoRoute(
    path: '/workout/routines',
    name: 'workout_routines',
    builder: (context, state) =>
        const VigorAdaptiveTheme(child: RoutinesScreen()),
  ),
  GoRoute(
    path: '/workout/live',
    name: 'live_workout_logger',
    builder: (context, state) => VigorAdaptiveTheme(
      child: LiveWorkoutLoggerScreen(
        initialRoutineId: state.uri.queryParameters['routineId'],
        initialExerciseCode: state.uri.queryParameters['exerciseCode'],
      ),
    ),
  ),
];
