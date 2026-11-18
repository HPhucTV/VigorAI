// [OWNER: M1] Offline-First Health Repository & Riverpod State (T-M1-05)
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../core/database/health_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';

class HealthDashboardState {
  final bool isLoading;
  final DailyHealthModel? dailyHealth;
  final List<BiometricLogModel> biometrics;
  final List<MealLogModel> meals;
  final List<SupplementScheduleModel> supplements;
  final double targetCaloriesKcal;
  final int pendingSyncCount;
  final String? errorMessage;

  const HealthDashboardState({
    this.isLoading = false,
    this.dailyHealth,
    this.biometrics = const [],
    this.meals = const [],
    this.supplements = const [],
    this.targetCaloriesKcal = 2400.0,
    this.pendingSyncCount = 0,
    this.errorMessage,
  });

  BiometricLogModel? get latestBiometric =>
      biometrics.isNotEmpty ? biometrics.first : null;

  double get totalCaloriesConsumed =>
      meals.fold<double>(0.0, (sum, item) => sum + item.totalCalories);

  double get totalProteinConsumed =>
      meals.fold<double>(0.0, (sum, item) => sum + item.proteinG);

  double get totalCarbsConsumed =>
      meals.fold<double>(0.0, (sum, item) => sum + item.carbsG);

  double get totalFatConsumed =>
      meals.fold<double>(0.0, (sum, item) => sum + item.fatG);

  HealthDashboardState copyWith({
    bool? isLoading,
    DailyHealthModel? dailyHealth,
    List<BiometricLogModel>? biometrics,
    List<MealLogModel>? meals,
    List<SupplementScheduleModel>? supplements,
    double? targetCaloriesKcal,
    int? pendingSyncCount,
    String? errorMessage,
    bool clearError = false,
  }) {
    return HealthDashboardState(
      isLoading: isLoading ?? this.isLoading,
      dailyHealth: dailyHealth ?? this.dailyHealth,
      biometrics: biometrics ?? this.biometrics,
      meals: meals ?? this.meals,
      supplements: supplements ?? this.supplements,
      targetCaloriesKcal: targetCaloriesKcal ?? this.targetCaloriesKcal,
      pendingSyncCount: pendingSyncCount ?? this.pendingSyncCount,
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class HealthRepository {
  final Dio _dio;
  final Uuid _uuid = const Uuid();

  HealthRepository(this._dio);

  Future<HealthDashboardState> loadDashboardData({
    String dateIso = '2026-11-18',
    double heightCm = 172.0,
    String gender = 'MALE',
    String activityLevel = 'MODERATE',
    String fitnessGoal = 'BULK',
  }) async {
    if (ApiEndpoints.useMockApi) {
      final raw =
          await rootBundle.loadString('assets/mock_json/mock_m1_health.json');
      final mock = jsonDecode(raw) as Map<String, dynamic>;
      return _parsePayload(
        dailyJson: mock['daily_health'] as Map<String, dynamic>,
        biometricsList: mock['biometrics'] as List<dynamic>,
        mealsList: mock['meals'] as List<dynamic>,
        supplementsList: mock['supplements'] as List<dynamic>,
        heightCm: heightCm,
        gender: gender,
        activityLevel: activityLevel,
        fitnessGoal: fitnessGoal,
      );
    }

    final dailyRes =
        await _dio.get<Map<String, dynamic>>(ApiEndpoints.dailyHealth(dateIso));
    final bioRes =
        await _dio.get<Map<String, dynamic>>(ApiEndpoints.biometrics);
    final mealRes = await _dio.get<Map<String, dynamic>>(ApiEndpoints.meals);
    final suppRes =
        await _dio.get<Map<String, dynamic>>(ApiEndpoints.supplements);

    return _parsePayload(
      dailyJson: dailyRes.data ?? const <String, dynamic>{},
      biometricsList: (bioRes.data?['items'] as List<dynamic>?) ?? const [],
      mealsList: (mealRes.data?['items'] as List<dynamic>?) ?? const [],
      supplementsList: (suppRes.data?['items'] as List<dynamic>?) ?? const [],
      heightCm: heightCm,
      gender: gender,
      activityLevel: activityLevel,
      fitnessGoal: fitnessGoal,
    );
  }

  HealthDashboardState _parsePayload({
    required Map<String, dynamic> dailyJson,
    required List<dynamic> biometricsList,
    required List<dynamic> mealsList,
    required List<dynamic> supplementsList,
    required double heightCm,
    required String gender,
    required String activityLevel,
    required String fitnessGoal,
  }) {
    final daily = DailyHealthModel.fromJson(dailyJson);
    final biometrics = biometricsList
        .map((e) => BiometricLogModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final meals = mealsList
        .map((e) => MealLogModel.fromJson(e as Map<String, dynamic>))
        .toList();
    final supplements = supplementsList
        .map((e) => SupplementScheduleModel.fromJson(e as Map<String, dynamic>))
        .toList();

    final currentWeight = biometrics.isNotEmpty ? biometrics.first.weightKg : 70.0;
    final bmr = DailyHealthModel.calculateBmrMifflinStJeor(
      weightKg: currentWeight,
      heightCm: heightCm,
      ageYears: 24,
      gender: gender,
    );
    final targetKcal = DailyHealthModel.calculateTargetCalories(
      bmr: bmr,
      activityLevel: activityLevel,
      fitnessGoal: fitnessGoal,
    );

    return HealthDashboardState(
      isLoading: false,
      dailyHealth: daily,
      biometrics: biometrics,
      meals: meals,
      supplements: supplements,
      targetCaloriesKcal: targetKcal,
      pendingSyncCount: 0,
    );
  }

  BiometricLogModel createOfflineBiometric({
    required double weightKg,
    required double heightCm,
    double? bodyFatPct,
    double? muscleMassKg,
  }) {
    final now = DateTime.now().toUtc();
    final todayIso = now.toIso8601String().split('T').first;
    final bmi = BiometricLogModel.calculateBmi(weightKg, heightCm);
    return BiometricLogModel(
      id: _uuid.v4(),
      weightKg: weightKg,
      bodyFatPct: bodyFatPct,
      muscleMassKg: muscleMassKg,
      bmi: bmi,
      loggedDateIso: todayIso,
      syncStatus: 'PENDING_CREATE',
      updatedAt: now,
    );
  }
}

class HealthDashboardController extends StateNotifier<HealthDashboardState> {
  final HealthRepository _repository;

  HealthDashboardController(this._repository)
      : super(const HealthDashboardState(isLoading: true)) {
    load();
  }

  Future<void> load() async {
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final loaded = await _repository.loadDashboardData();
      state = loaded;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Không thể tải dữ liệu sức khỏe: $e',
      );
    }
  }

  void addWaterMl(int deltaMl) {
    final current = state.dailyHealth;
    if (current == null) return;
    final updated = current.copyWith(
      waterMl: (current.waterMl + deltaMl).clamp(0, 10000),
      syncStatus: 'PENDING_UPDATE',
      updatedAt: DateTime.now().toUtc(),
    );
    state = state.copyWith(
      dailyHealth: updated,
      pendingSyncCount: state.pendingSyncCount + 1,
    );
  }

  void logOfflineWeight(double weightKg, {double heightCm = 172.0}) {
    final newLog = _repository.createOfflineBiometric(
      weightKg: weightKg,
      heightCm: heightCm,
    );
    state = state.copyWith(
      biometrics: [newLog, ...state.biometrics],
      pendingSyncCount: state.pendingSyncCount + 1,
    );
  }

  void markSynced() {
    if (state.dailyHealth == null) return;
    state = state.copyWith(
      dailyHealth: state.dailyHealth!.copyWith(syncStatus: 'SYNCED'),
      pendingSyncCount: 0,
    );
  }
}

final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  final dio = ref.watch(dioProvider);
  return HealthRepository(dio);
});

final healthDashboardProvider =
    StateNotifierProvider<HealthDashboardController, HealthDashboardState>((ref) {
  final repo = ref.watch(healthRepositoryProvider);
  return HealthDashboardController(repo);
});
