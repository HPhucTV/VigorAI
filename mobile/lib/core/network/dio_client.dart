// [OWNER: M1] HTTP Client tich hop SecureStorage JWT AuthInterceptor (Auto-Refresh 401) & MockApiInterceptor
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'api_endpoints.dart';

class StorageKeys {
  StorageKeys._();

  static const String accessToken = 'vigorai_jwt_access_token';
  static const String refreshToken = 'vigorai_jwt_refresh_token';
  static const String disclaimerAccepted = 'vigorai_medical_disclaimer_accepted';
  static const String disclaimerAcceptedAt = 'vigorai_medical_disclaimer_at';
  static const String currentUserJson = 'vigorai_current_user_json';
  static const String lastSyncUtc = 'vigorai_last_sync_utc';
  static const String fitnessProfileJson = 'vigorai_user_fitness_profile_json';
  static const String themeModePreference = 'vigorai_theme_mode_preference';
}

final secureStorageProvider = Provider<FlutterSecureStorage>((ref) {
  return const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
  );
});

/// Tu dong gan Bearer JWT vao header va tu dong gia han token khi gap loi 401.
class AuthInterceptor extends Interceptor {
  final FlutterSecureStorage _storage;
  final Dio _refreshDio;
  final Dio _retryDio;

  AuthInterceptor(this._storage, this._refreshDio, this._retryDio);

  static const _publicPaths = {
    ApiEndpoints.login,
    ApiEndpoints.register,
    ApiEndpoints.refresh,
    ApiEndpoints.deleteAccountWeb,
  };

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!_publicPaths.contains(options.path)) {
      final token = await _storage.read(key: StorageKeys.accessToken);
      if (token != null && token.isNotEmpty) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }
    handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final statusCode = err.response?.statusCode;
    final path = err.requestOptions.path;
    final alreadyRetried = err.requestOptions.extra['_retried'] == true;

    if (statusCode == 401 && !_publicPaths.contains(path) && !alreadyRetried) {
      final storedRefresh = await _storage.read(key: StorageKeys.refreshToken);
      if (storedRefresh != null && storedRefresh.isNotEmpty) {
        try {
          final refreshRes = await _refreshDio.post<Map<String, dynamic>>(
            ApiEndpoints.refresh,
            data: <String, dynamic>{'refresh_token': storedRefresh},
          );
          final data = refreshRes.data ?? const <String, dynamic>{};
          final newAccess = data['access_token'] as String?;
          final newRefresh = data['refresh_token'] as String?;

          if (newAccess != null && newAccess.isNotEmpty) {
            await _storage.write(key: StorageKeys.accessToken, value: newAccess);
            if (newRefresh != null && newRefresh.isNotEmpty) {
              await _storage.write(
                key: StorageKeys.refreshToken,
                value: newRefresh,
              );
            }

            final retryOptions = err.requestOptions;
            retryOptions.headers['Authorization'] = 'Bearer $newAccess';
            retryOptions.extra['_retried'] = true;

            final retryResponse = await _retryDio.fetch<dynamic>(retryOptions);
            handler.resolve(retryResponse);
            return;
          }
        } catch (_) {
          // Refresh token het han hoac tai khoan da bi xoa -> don session cuc bo
          await _storage.delete(key: StorageKeys.accessToken);
          await _storage.delete(key: StorageKeys.refreshToken);
          await _storage.delete(key: StorageKeys.currentUserJson);
        }
      }
    }

    handler.next(err);
  }
}

/// Gia lap API Auth & Health tu assets/mock_json/mock_m1_health.json khi useMockApi = true.
class MockApiInterceptor extends Interceptor {
  Map<String, dynamic>? _cachedMockM1;
  Map<String, dynamic>? _cachedMockM4;

  Future<Map<String, dynamic>> _loadMockM1() async {
    if (_cachedMockM1 != null) return _cachedMockM1!;
    final raw = await rootBundle.loadString('assets/mock_json/mock_m1_health.json');
    _cachedMockM1 = jsonDecode(raw) as Map<String, dynamic>;
    return _cachedMockM1!;
  }

  Future<Map<String, dynamic>> _loadMockM4() async {
    if (_cachedMockM4 != null) return _cachedMockM4!;
    final raw = await rootBundle.loadString('assets/mock_json/mock_m4_ai.json');
    _cachedMockM4 = jsonDecode(raw) as Map<String, dynamic>;
    return _cachedMockM4!;
  }

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    if (!ApiEndpoints.useMockApi) {
      handler.next(options);
      return;
    }

    final path = options.path;
    final method = options.method.toUpperCase();

    if (path == ApiEndpoints.aiFoodAnalyze && method == 'POST') {
      final mockAi = await _loadMockM4();
      handler.resolve(
        Response<Map<String, dynamic>>(
          requestOptions: options,
          statusCode: 200,
          data: Map<String, dynamic>.from(
            mockAi['food_analyze_mock'] as Map<String, dynamic>,
          ),
        ),
      );
      return;
    }

    if (path.startsWith('/api/v1/sync')) {
      final nowUtcIso = DateTime.now().toUtc().toIso8601String();
      if (path == ApiEndpoints.syncPush && method == 'POST') {
        final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
        final syncedIds = <String, List<String>>{};
        var totalApplied = 0;
        for (final key in const [
          'biometric_logs',
          'daily_health_logs',
          'supplement_schedules',
          'meal_logs',
          'workout_routines',
          'workout_sessions',
          'workout_sets',
        ]) {
          final items = (body[key] as List?) ?? const [];
          final ids = <String>[];
          for (final item in items) {
            if (item is Map && item['id'] != null) {
              ids.add(item['id'].toString());
            }
          }
          syncedIds[key] = ids;
          totalApplied += items.length;
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              'status': 'ok',
              'synced_ids': syncedIds,
              'total_applied': totalApplied,
              'server_time_utc': nowUtcIso,
            },
          ),
        );
        return;
      }

      if (path == ApiEndpoints.syncPull && method == 'GET') {
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              'since': options.queryParameters['since'],
              'server_time_utc': nowUtcIso,
              'records': <String, dynamic>{},
            },
          ),
        );
        return;
      }
    }

    if (path.startsWith('/api/v1/auth') ||
        path.startsWith('/api/v1/health') ||
        path.startsWith('/api/v1/users')) {
      final mock = await _loadMockM1();

      if (path == ApiEndpoints.register) {
        final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
        if (body['medical_disclaimer_accepted'] != true) {
          handler.reject(
            DioException.badResponse(
              statusCode: 400,
              requestOptions: options,
              response: Response<Map<String, dynamic>>(
                requestOptions: options,
                statusCode: 400,
                data: <String, dynamic>{
                  'detail': 'Ban phai chap nhan Mien tru Trach nhiem Y te de dang ky.',
                },
              ),
            ),
          );
          return;
        }
        final userMap = Map<String, dynamic>.from(mock['user'] as Map<String, dynamic>);
        userMap['email'] = body['email'] ?? userMap['email'];
        userMap['full_name'] = body['full_name'] ?? userMap['full_name'];
        userMap['gender'] = body['gender'] ?? userMap['gender'];
        userMap['height_cm'] = body['height_cm'] ?? userMap['height_cm'];
        userMap['fitness_goal'] = body['fitness_goal'] ?? userMap['fitness_goal'];
        if (body['birth_date'] != null) {
          userMap['birth_date'] = body['birth_date'];
        }
        if (body['activity_level'] != null) {
          userMap['activity_level'] = body['activity_level'];
        }
        userMap['medical_disclaimer_accepted'] = true;

        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              ...mock['auth_tokens'] as Map<String, dynamic>,
              'expires_in_seconds': 900,
              'user': userMap,
            },
          ),
        );
        return;
      }

      if (path == ApiEndpoints.login || path == ApiEndpoints.refresh) {
        if (path == ApiEndpoints.refresh) {
          final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
          final rt = body['refresh_token'] as String?;
          if (rt == null || rt.isEmpty) {
            handler.reject(
              DioException.badResponse(
                statusCode: 401,
                requestOptions: options,
                response: Response<Map<String, dynamic>>(
                  requestOptions: options,
                  statusCode: 401,
                  data: <String, dynamic>{'detail': 'Refresh token khong hop le.'},
                ),
              ),
            );
            return;
          }
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              ...mock['auth_tokens'] as Map<String, dynamic>,
              'expires_in_seconds': 900,
              'user': mock['user'],
            },
          ),
        );
        return;
      }

      if (path == ApiEndpoints.biometrics) {
        if (method == 'POST') {
          final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
          handler.resolve(
            Response<Map<String, dynamic>>(
              requestOptions: options,
              statusCode: 201,
              data: body,
            ),
          );
          return;
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{'items': mock['biometrics']},
          ),
        );
        return;
      }

      if (path.startsWith('/api/v1/health/daily/')) {
        if (method == 'PUT') {
          final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
          handler.resolve(
            Response<Map<String, dynamic>>(
              requestOptions: options,
              statusCode: 200,
              data: body,
            ),
          );
          return;
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: mock['daily_health'] as Map<String, dynamic>,
          ),
        );
        return;
      }

      if (path == ApiEndpoints.foodCatalog) {
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              'items': const [
                {
                  'class_code': 'GRILLED_CHICKEN_BREAST',
                  'name_vi': 'Ức gà áp chảo',
                  'name_en': 'Grilled Chicken Breast',
                  'kcal_per_100g': 165.0,
                  'protein_per_100g': 31.0,
                  'carbs_per_100g': 0.0,
                  'fat_per_100g': 3.6,
                  'default_serving_g': 180.0,
                },
                {
                  'class_code': 'WHITE_RICE',
                  'name_vi': 'Cơm trắng',
                  'name_en': 'Steamed White Rice',
                  'kcal_per_100g': 130.0,
                  'protein_per_100g': 2.7,
                  'carbs_per_100g': 28.2,
                  'fat_per_100g': 0.3,
                  'default_serving_g': 150.0,
                },
              ],
            },
          ),
        );
        return;
      }

      if (path == ApiEndpoints.meals) {
        if (method == 'POST') {
          final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
          handler.resolve(
            Response<Map<String, dynamic>>(
              requestOptions: options,
              statusCode: 201,
              data: body,
            ),
          );
          return;
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{'items': mock['meals']},
          ),
        );
        return;
      }

      if (path == ApiEndpoints.supplements) {
        if (method == 'POST') {
          final body = options.data as Map<String, dynamic>? ?? <String, dynamic>{};
          handler.resolve(
            Response<Map<String, dynamic>>(
              requestOptions: options,
              statusCode: 201,
              data: body,
            ),
          );
          return;
        }
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{'items': mock['supplements']},
          ),
        );
        return;
      }

      if (path.startsWith('${ApiEndpoints.supplements}/') && method == 'DELETE') {
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{'status': 'deleted'},
          ),
        );
        return;
      }

      if (path == ApiEndpoints.exportMe) {
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: mock,
          ),
        );
        return;
      }

      if (path == ApiEndpoints.deleteMe) {
        handler.resolve(
          Response<Map<String, dynamic>>(
            requestOptions: options,
            statusCode: 200,
            data: <String, dynamic>{
              'status': 'deleted',
              'message': 'Tai khoan va toan bo du lieu da duoc xoa vinh vien.',
            },
          ),
        );
        return;
      }
    }

    handler.next(options);
  }
}

final dioProvider = Provider<Dio>((ref) {
  final storage = ref.watch(secureStorageProvider);
  final baseOptions = BaseOptions(
    baseUrl: ApiEndpoints.baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 15),
    headers: const {'Content-Type': 'application/json; charset=utf-8'},
  );

  final mockInterceptor = MockApiInterceptor();
  final refreshDio = Dio(baseOptions)..interceptors.add(mockInterceptor);
  final dio = Dio(baseOptions);

  dio.interceptors.addAll([
    AuthInterceptor(storage, refreshDio, dio),
    mockInterceptor,
  ]);
  return dio;
});
