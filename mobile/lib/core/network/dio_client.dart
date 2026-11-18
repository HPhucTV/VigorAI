// [OWNER: M1] HTTP Client cau hinh san Timeout, JWT Bearer va Mock toggle
import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'api_endpoints.dart';

final dioProvider = Provider<Dio>((ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: ApiEndpoints.baseUrl,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: const {'Content-Type': 'application/json; charset=utf-8'},
    ),
  );
  // TODO(M1 - T-M1-05): Bo sung AuthInterceptor doc JWT tu flutter_secure_storage
  // va MockInterceptor khi ApiEndpoints.useMockApi == true.
  return dio;
});
