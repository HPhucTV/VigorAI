// [OWNER: M1] Hang so Endpoints khop 100% Muc 7 docs/system-design-spec.md
class ApiEndpoints {
  ApiEndpoints._();

  /// Domain Production chuẩn duy nhất trên Railway (phục vụ cả Core DB, 3D GLB & AI).
  static const String productionBaseUrl =
      'https://vigorai-production.up.railway.app';

  // Bật false khi kết nối FastAPI thật (Production / Staging / Docker local)
  static const bool useMockApi = bool.fromEnvironment(
    'USE_MOCK_API',
    defaultValue: true,
  );

  static const String _envBaseUrl = String.fromEnvironment('API_BASE_URL');

  /// Khi `USE_MOCK_API=false` mà không truyền `API_BASE_URL`, tự động trỏ về
  /// `productionBaseUrl` để đồng nhất 1 domain duy nhất giữa `.aab` và `.apk`.
  static const String baseUrl = _envBaseUrl != ''
      ? _envBaseUrl
      : (useMockApi ? 'http://10.0.2.2:8000' : productionBaseUrl);

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
  static const String foodCatalog = '/api/v1/health/catalog';
  static const String meals = '/api/v1/health/meals';
  static const String supplements = '/api/v1/health/supplements';
  static String deleteSupplement(String id) => '/api/v1/health/supplements/$id';

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
