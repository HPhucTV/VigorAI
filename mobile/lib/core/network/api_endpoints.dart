// [OWNER: M1] Hang so Endpoints khop 100% Muc 7 docs/system-design-spec.md
class ApiEndpoints {
  ApiEndpoints._();

  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  // Bat false khi ket noi FastAPI that (Staging / Docker local)
  static const bool useMockApi = bool.fromEnvironment(
    'USE_MOCK_API',
    defaultValue: true,
  );

  // Auth & CH Play Compliance (M3 & M1)
  static const String register = '/api/v1/auth/register';
  static const String login = '/api/v1/auth/login';
  static const String refresh = '/api/v1/auth/refresh';
  static const String exportMe = '/api/v1/users/me/export';
  static const String deleteMe = '/api/v1/users/me';
  static const String deleteAccountWeb = '/delete-account';

  // Offline-First Sync (M3 & M1)
  static const String syncPush = '/api/v1/sync/push';
  static const String syncPull = '/api/v1/sync/pull';

  // Health & Biometrics (M3 & M1)
  static const String biometrics = '/api/v1/health/biometrics';
  static String dailyHealth(String date) => '/api/v1/health/daily/$date';
  static const String meals = '/api/v1/health/meals';
  static const String supplements = '/api/v1/health/supplements';

  // 3D Exercises & Workouts (M3 & M2)
  static const String exercises = '/api/v1/exercises';
  static String exerciseAlternatives(String code) =>
      '/api/v1/exercises/$code/alternatives';
  static const String routines = '/api/v1/routines';
  static const String workoutSessions = '/api/v1/workouts/sessions';
  static const String analyticsSummary = '/api/v1/analytics/summary';

  // AI Models B & C (M4)
  static const String aiFoodAnalyze = '/api/v1/ai/food-analyze';
  static const String aiReadinessAndOverload =
      '/api/v1/ai/readiness-and-overload';
}
