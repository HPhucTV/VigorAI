// [OWNER: M1] Repository quan ly Auth (Login/Register/Refresh/Delete) & CH Play Medical Disclaimer (T-M1-04..06)
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../../core/database/app_database.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/platform/photo_picker_service.dart';
import '../../../core/platform/workmanager_reminder_service.dart';

class AuthUserProfile {
  final String id;
  final String email;
  final String fullName;
  final String gender;
  final String? birthDateIso;
  final double heightCm;
  final String activityLevel;
  final String fitnessGoal;
  final bool medicalDisclaimerAccepted;

  const AuthUserProfile({
    required this.id,
    required this.email,
    required this.fullName,
    this.gender = 'MALE',
    this.birthDateIso,
    this.heightCm = 170.0,
    this.activityLevel = 'MODERATE',
    this.fitnessGoal = 'MAINTAIN',
    this.medicalDisclaimerAccepted = false,
  });

  /// Tinh tuoi theo ngay sinh YYYY-MM-DD; fallback ve 24 neu thieu hoac khong hop le.
  int calculateAgeYears({DateTime? referenceDate}) {
    final raw = birthDateIso?.trim();
    if (raw == null || raw.isEmpty) return 24;
    final dob = DateTime.tryParse(raw.split('T').first);
    if (dob == null) return 24;
    final ref = referenceDate ?? DateTime.now();
    var age = ref.year - dob.year;
    if (ref.month < dob.month ||
        (ref.month == dob.month && ref.day < dob.day)) {
      age--;
    }
    if (age < 10 || age > 100) return 24;
    return age;
  }

  factory AuthUserProfile.fromJson(Map<String, dynamic> json) {
    return AuthUserProfile(
      id: (json['id'] as String?) ?? 'local-user',
      email: json['email'] as String,
      fullName: (json['full_name'] as String?) ?? 'Người dùng VigorAI',
      gender: (json['gender'] as String?) ?? 'MALE',
      birthDateIso: json['birth_date'] as String?,
      heightCm: (json['height_cm'] as num?)?.toDouble() ?? 170.0,
      activityLevel: (json['activity_level'] as String?) ?? 'MODERATE',
      fitnessGoal: (json['fitness_goal'] as String?) ?? 'MAINTAIN',
      medicalDisclaimerAccepted:
          (json['medical_disclaimer_accepted'] as bool?) ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'email': email,
        'full_name': fullName,
        'gender': gender,
        'birth_date': birthDateIso,
        'height_cm': heightCm,
        'activity_level': activityLevel,
        'fitness_goal': fitnessGoal,
        'medical_disclaimer_accepted': medicalDisclaimerAccepted,
      };
}

class AuthRepository {
  final Dio _dio;
  final FlutterSecureStorage _storage;
  final AppDatabase _database;
  final PhotoPickerService _photoPickerService;

  AuthRepository(
    this._dio,
    this._storage,
    this._database,
    this._photoPickerService,
  );

  Future<bool> hasAcceptedDisclaimer() async {
    final value = await _storage.read(key: StorageKeys.disclaimerAccepted);
    return value == 'true';
  }

  Future<String> acceptMedicalDisclaimer() async {
    final acceptedAtUtc = DateTime.now().toUtc().toIso8601String();
    await _storage.write(key: StorageKeys.disclaimerAccepted, value: 'true');
    await _storage.write(
      key: StorageKeys.disclaimerAcceptedAt,
      value: acceptedAtUtc,
    );
    return acceptedAtUtc;
  }

  Future<bool> hasValidToken() async {
    final token = await _storage.read(key: StorageKeys.accessToken);
    return token != null && token.isNotEmpty;
  }

  Future<AuthUserProfile?> getCachedUserProfile() async {
    final raw = await _storage.read(key: StorageKeys.currentUserJson);
    if (raw == null || raw.isEmpty) return null;
    return AuthUserProfile.fromJson(jsonDecode(raw) as Map<String, dynamic>);
  }

  Future<AuthUserProfile> login({
    required String email,
    required String password,
  }) async {
    final response = await _dio.post<Map<String, dynamic>>(
      ApiEndpoints.login,
      data: <String, dynamic>{
        'email': email.trim(),
        'password': password,
      },
    );
    return _persistSessionFromResponse(response.data ?? const {});
  }

  Future<AuthUserProfile> register({
    required String email,
    required String password,
    required String fullName,
    required String gender,
    required double heightCm,
    required String fitnessGoal,
    required bool medicalDisclaimerAccepted,
  }) async {
    if (!medicalDisclaimerAccepted) {
      throw StateError(
        'Bạn bắt buộc phải đồng ý Miễn trừ Trách nhiệm Y tế trước khi đăng ký.',
      );
    }
    final response = await _dio.post<Map<String, dynamic>>(
      ApiEndpoints.register,
      data: <String, dynamic>{
        'email': email.trim(),
        'password': password,
        'full_name': fullName.trim(),
        'gender': gender,
        'height_cm': heightCm,
        'fitness_goal': fitnessGoal,
        'medical_disclaimer_accepted': medicalDisclaimerAccepted,
      },
    );
    return _persistSessionFromResponse(
      response.data ?? const {},
      fallbackEmail: email.trim(),
      fallbackName: fullName.trim(),
      fallbackGender: gender,
      fallbackHeight: heightCm,
      fallbackGoal: fitnessGoal,
    );
  }

  /// Lam moi Access Token bang Refresh Token (khop POST /api/v1/auth/refresh cua M3).
  Future<AuthUserProfile> refreshToken() async {
    final storedRefresh = await _storage.read(key: StorageKeys.refreshToken);
    if (storedRefresh == null || storedRefresh.isEmpty) {
      throw StateError('Không tìm thấy Refresh Token hợp lệ.');
    }
    final response = await _dio.post<Map<String, dynamic>>(
      ApiEndpoints.refresh,
      data: <String, dynamic>{'refresh_token': storedRefresh},
    );
    return _persistSessionFromResponse(response.data ?? const {});
  }

  /// Xoa vinh vien tai khoan tren Server (DELETE /api/v1/users/me) + don sach du lieu cuc bo (T-M1-06 / F26).
  Future<void> deleteAccountAndLocalData() async {
    await _dio.delete<Map<String, dynamic>>(ApiEndpoints.deleteMe);
    await _storage.deleteAll();
    await _photoPickerService.deleteAllPrivateProgressPhotos();
    await _photoPickerService.deleteAllPrivateMealPhotos();
    await SupplementIntakeStore().clearAll();
    await _database.clearAllLocalData();
  }

  Future<AuthUserProfile> _persistSessionFromResponse(
    Map<String, dynamic> data, {
    String? fallbackEmail,
    String? fallbackName,
    String? fallbackGender,
    double? fallbackHeight,
    String? fallbackGoal,
  }) async {
    final accessToken = data['access_token'] as String?;
    final refreshToken = data['refresh_token'] as String?;
    if (accessToken != null && accessToken.isNotEmpty) {
      await _storage.write(key: StorageKeys.accessToken, value: accessToken);
    }
    if (refreshToken != null && refreshToken.isNotEmpty) {
      await _storage.write(key: StorageKeys.refreshToken, value: refreshToken);
    }

    final userMap = data['user'] as Map<String, dynamic>? ??
        <String, dynamic>{
          'id': 'local-user',
          'email': fallbackEmail ?? 'demo@vigorai.app',
          'full_name': fallbackName ?? 'Thành viên VigorAI',
          'gender': fallbackGender ?? 'MALE',
          'height_cm': fallbackHeight ?? 172.0,
          'fitness_goal': fallbackGoal ?? 'BULK',
          'medical_disclaimer_accepted': true,
        };

    final profile = AuthUserProfile.fromJson(userMap);
    await _storage.write(
      key: StorageKeys.currentUserJson,
      value: jsonEncode(profile.toJson()),
    );
    return profile;
  }

  Future<void> logout() async {
    await _storage.delete(key: StorageKeys.accessToken);
    await _storage.delete(key: StorageKeys.refreshToken);
    await _storage.delete(key: StorageKeys.currentUserJson);
  }
}

final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dio = ref.watch(dioProvider);
  final storage = ref.watch(secureStorageProvider);
  final db = ref.watch(appDatabaseProvider);
  final photoPicker = ref.watch(photoPickerServiceProvider);
  return AuthRepository(dio, storage, db, photoPicker);
});
