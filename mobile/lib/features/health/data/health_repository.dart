// [OWNER: M1] Offline-First Health Repository (Drift SQLite + WorkManager + SyncQueue) (T-M1-05, T-M1-08..12)
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../core/database/app_database.dart';
import '../../../core/database/health_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/platform/workmanager_reminder_service.dart';
import '../../../core/sync/sync_queue_manager.dart';
import '../../auth_privacy/data/auth_repository.dart';
import '../../auth_privacy/data/user_fitness_profile.dart';
import '../../auth_privacy/presentation/auth_controller.dart';

class HealthDashboardState {
  final bool isLoading;
  final bool isSyncing;
  final DailyHealthModel? dailyHealth;
  final List<DailyHealthModel> sleepHistory7Days;
  final List<BiometricLogModel> biometrics;
  final List<MealLogModel> meals;
  final List<SupplementScheduleModel> supplements;
  final double targetCaloriesKcal;
  final MacroTargets macroTargets;
  final double bmrKcal;
  final String fitnessGoal;
  final String activityLevel;
  final int workoutBonusWaterMl;
  final String? workoutBonusReason;
  final double weeklySupplementAdherencePct;
  final bool hydrationReminderEnabled;
  final bool supplementReminderEnabled;
  final int pendingSyncCount;
  final String? lastSyncMessage;
  final String? errorMessage;

  const HealthDashboardState({
    this.isLoading = false,
    this.isSyncing = false,
    this.dailyHealth,
    this.sleepHistory7Days = const [],
    this.biometrics = const [],
    this.meals = const [],
    this.supplements = const [],
    this.targetCaloriesKcal = 2400.0,
    this.macroTargets = const MacroTargets(
      targetCalories: 2400,
      proteinG: 140,
      carbsG: 310,
      fatG: 67,
    ),
    this.bmrKcal = 1650.0,
    this.fitnessGoal = 'BULK',
    this.activityLevel = 'MODERATE',
    this.workoutBonusWaterMl = 0,
    this.workoutBonusReason,
    this.weeklySupplementAdherencePct = 0.0,
    this.hydrationReminderEnabled = true,
    this.supplementReminderEnabled = true,
    this.pendingSyncCount = 0,
    this.lastSyncMessage,
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
    bool? isSyncing,
    DailyHealthModel? dailyHealth,
    List<DailyHealthModel>? sleepHistory7Days,
    List<BiometricLogModel>? biometrics,
    List<MealLogModel>? meals,
    List<SupplementScheduleModel>? supplements,
    double? targetCaloriesKcal,
    MacroTargets? macroTargets,
    double? bmrKcal,
    String? fitnessGoal,
    String? activityLevel,
    int? workoutBonusWaterMl,
    String? workoutBonusReason,
    bool clearBonusReason = false,
    double? weeklySupplementAdherencePct,
    bool? hydrationReminderEnabled,
    bool? supplementReminderEnabled,
    int? pendingSyncCount,
    String? lastSyncMessage,
    bool clearSyncMessage = false,
    String? errorMessage,
    bool clearError = false,
  }) {
    return HealthDashboardState(
      isLoading: isLoading ?? this.isLoading,
      isSyncing: isSyncing ?? this.isSyncing,
      dailyHealth: dailyHealth ?? this.dailyHealth,
      sleepHistory7Days: sleepHistory7Days ?? this.sleepHistory7Days,
      biometrics: biometrics ?? this.biometrics,
      meals: meals ?? this.meals,
      supplements: supplements ?? this.supplements,
      targetCaloriesKcal: targetCaloriesKcal ?? this.targetCaloriesKcal,
      macroTargets: macroTargets ?? this.macroTargets,
      bmrKcal: bmrKcal ?? this.bmrKcal,
      fitnessGoal: fitnessGoal ?? this.fitnessGoal,
      activityLevel: activityLevel ?? this.activityLevel,
      workoutBonusWaterMl: workoutBonusWaterMl ?? this.workoutBonusWaterMl,
      workoutBonusReason: clearBonusReason
          ? null
          : (workoutBonusReason ?? this.workoutBonusReason),
      weeklySupplementAdherencePct:
          weeklySupplementAdherencePct ?? this.weeklySupplementAdherencePct,
      hydrationReminderEnabled:
          hydrationReminderEnabled ?? this.hydrationReminderEnabled,
      supplementReminderEnabled:
          supplementReminderEnabled ?? this.supplementReminderEnabled,
      pendingSyncCount: pendingSyncCount ?? this.pendingSyncCount,
      lastSyncMessage: clearSyncMessage
          ? null
          : (lastSyncMessage ?? this.lastSyncMessage),
      errorMessage: clearError ? null : (errorMessage ?? this.errorMessage),
    );
  }
}

class HealthRepository {
  final AppDatabase _db;
  final Dio _dio;
  final SupplementIntakeStore _intakeStore;
  final SyncQueueManager _syncManager;
  final Uuid _uuid = const Uuid();

  HealthRepository(
    this._db,
    this._dio,
    this._intakeStore,
    this._syncManager,
  );

  static String todayIso([DateTime? now]) {
    final dt = now ?? DateTime.now();
    final m = dt.month.toString().padLeft(2, '0');
    final d = dt.day.toString().padLeft(2, '0');
    return '${dt.year}-$m-$d';
  }

  Future<DailyHealthLogsTableData?> _findDailyRowByDate(String dateIso) async {
    final rows = await (_db.select(_db.dailyHealthLogsTable)
          ..where((t) => t.logDateIso.equals(dateIso))
          ..orderBy([(t) => OrderingTerm.desc(t.updatedAt)]))
        .get();
    if (rows.isEmpty) return null;
    final latest = rows.first;
    if (rows.length > 1) {
      final redundantIds = rows.skip(1).map((r) => r.id).toList();
      await (_db.delete(_db.dailyHealthLogsTable)
            ..where((t) => t.id.isIn(redundantIds)))
          .go();
    }
    return latest;
  }

  Future<HealthDashboardState> loadDashboardData({
    double heightCm = 172.0,
    String gender = 'MALE',
    int ageYears = 24,
    String activityLevel = 'MODERATE',
    String fitnessGoal = 'BULK',
  }) async {
    final todayStr = todayIso();

    // 1. Seed Drift tu Mock/Live API neu SQLite cuc bo chua co du lieu
    final existingBios = await (_db.select(_db.biometricLogsTable)
          ..where((t) => t.deletedAt.isNull()))
        .get();
    final existingDaily = await _findDailyRowByDate(todayStr);

    if (existingBios.isEmpty && existingDaily == null) {
      await _bootstrapInitialData(todayStr);
    }

    // 2. Doc toan bo du lieu Offline-First tu Drift SQLite
    final bioRows = await (_db.select(_db.biometricLogsTable)
          ..where((t) => t.deletedAt.isNull())
          ..orderBy([
            (t) => OrderingTerm.desc(t.loggedDate),
            (t) => OrderingTerm.desc(t.updatedAt),
          ]))
        .get();
    final biometrics = bioRows.map(_mapBiometricRow).toList();

    final dailyRows = await (_db.select(_db.dailyHealthLogsTable)
          ..orderBy([(t) => OrderingTerm.desc(t.logDateIso)]))
        .get();
    final allDailies = dailyRows.map(_mapDailyRow).toList();
    var todayDaily = allDailies.cast<DailyHealthModel?>().firstWhere(
          (d) => d?.logDateIso == todayStr,
          orElse: () => null,
        );

    final nowUtc = DateTime.now().toUtc();
    if (todayDaily == null) {
      final latestWeight =
          biometrics.isNotEmpty ? biometrics.first.weightKg : 70.0;
      final baseWater = DailyHealthModel.calculateTargetWaterMl(latestWeight);
      final newDailyId = 'daily-$todayStr';
      await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
            DailyHealthLogsTableCompanion(
              id: Value(newDailyId),
              logDateIso: Value(todayStr),
              stepsCount: const Value(0),
              distanceKm: const Value(0.0),
              activeCaloriesKcal: const Value(0),
              waterMl: const Value(0),
              targetWaterMl: Value(baseWater),
              sleepHours: const Value(0.0),
              syncStatus: const Value('SYNCED'),
              updatedAt: Value(nowUtc),
            ),
          );
      todayDaily = DailyHealthModel(
        id: newDailyId,
        logDateIso: todayStr,
        targetWaterMl: baseWater,
        updatedAt: nowUtc,
      );
    }

    // 3. Tu dong cong bu nuoc neu ngay hom nay co buoi tap Gym trong Drift (F03), hoac giu muc bu thu cong da chon
    final currentWeight =
        biometrics.isNotEmpty ? biometrics.first.weightKg : 70.0;
    final workoutHydration =
        await _detectTodayWorkoutHydrationBonus(todayStr);
    final baseWaterOnly = DailyHealthModel.calculateTargetWaterMl(currentWeight);
    var bonusMl = 0;
    String? bonusReason = workoutHydration.$3;
    if (workoutHydration.$1 > 0) {
      final computedTargetWater = DailyHealthModel.calculateTargetWaterMl(
        currentWeight,
        workoutMinutes: workoutHydration.$1,
        workoutRpe: workoutHydration.$2,
      );
      bonusMl = (computedTargetWater - baseWaterOnly).clamp(0, 1500);
      if (todayDaily.targetWaterMl != computedTargetWater && bonusMl > 0) {
        todayDaily = todayDaily.copyWith(
          targetWaterMl: computedTargetWater,
          syncStatus: 'PENDING_UPDATE',
          updatedAt: nowUtc,
        );
        await (_db.update(_db.dailyHealthLogsTable)
              ..where((t) => t.id.equals(todayDaily!.id)))
            .write(
          DailyHealthLogsTableCompanion(
            targetWaterMl: Value(computedTargetWater),
            syncStatus: const Value('PENDING_UPDATE'),
            updatedAt: Value(nowUtc),
          ),
        );
      }
    } else if (todayDaily.targetWaterMl > baseWaterOnly) {
      bonusMl = (todayDaily.targetWaterMl - baseWaterOnly).clamp(0, 1500);
      bonusReason = 'Đã cộng bù +$bonusMl ml theo mức vận động hôm nay';
    }

    // 4. Loc bua an cua ngay hom nay
    final allMealRows = await (_db.select(_db.mealLogsTable)
          ..where((t) => t.deletedAt.isNull())
          ..orderBy([(t) => OrderingTerm.desc(t.loggedAt)]))
        .get();
    final todayMeals = allMealRows
        .where((m) => todayIso(m.loggedAt.toLocal()) == todayStr)
        .map(_mapMealRow)
        .toList();

    // 5. Doc danh sach Supplement & trang thai "Da uong"
    final suppRows = await (_db.select(_db.supplementSchedulesTable)
          ..where((t) => t.deletedAt.isNull() & t.isActive.equals(true))
          ..orderBy([(t) => OrderingTerm.asc(t.reminderTimeHhMm)]))
        .get();
    final takenTodayIds = await _intakeStore.getTakenIdsForDate(todayStr);
    final supplements = suppRows
        .map(
          (row) => SupplementScheduleModel(
            id: row.id,
            supplementName: row.supplementName,
            dosageLabel: row.dosageLabel,
            reminderTimeHhMm: row.reminderTimeHhMm,
            workoutDaysOnly: row.workoutDaysOnly,
            isActive: row.isActive,
            takenToday: takenTodayIds.contains(row.id),
            syncStatus: row.syncStatus,
            updatedAt: row.updatedAt,
          ),
        )
        .toList();
    final adherencePct = await _intakeStore.calculateWeeklyAdherence(
      activeSupplementCount: supplements.length,
    );

    // 6. Tinh BMR (Mifflin-St Jeor), TDEE & Macro Targets (F04)
    final bmr = DailyHealthModel.calculateBmrMifflinStJeor(
      weightKg: currentWeight,
      heightCm: heightCm,
      ageYears: ageYears,
      gender: gender,
    );
    final targetKcal = DailyHealthModel.calculateTargetCalories(
      bmr: bmr,
      activityLevel: activityLevel,
      fitnessGoal: fitnessGoal,
    );
    final macroTargets = DailyHealthModel.calculateMacroTargets(
      weightKg: currentWeight,
      targetCalories: targetKcal,
    );

    // 7. Lich su giac ngu 7 ngay
    final sleepHistory = allDailies.take(7).toList().reversed.toList();
    final pendingCount = await _syncManager.countPendingChanges();

    return HealthDashboardState(
      isLoading: false,
      dailyHealth: todayDaily,
      sleepHistory7Days: sleepHistory,
      biometrics: biometrics,
      meals: todayMeals,
      supplements: supplements,
      targetCaloriesKcal: targetKcal,
      macroTargets: macroTargets,
      bmrKcal: bmr,
      fitnessGoal: fitnessGoal,
      activityLevel: activityLevel,
      workoutBonusWaterMl: bonusMl,
      workoutBonusReason: bonusReason,
      weeklySupplementAdherencePct: adherencePct,
      pendingSyncCount: pendingCount,
    );
  }

  Future<(int, double, String?)> _detectTodayWorkoutHydrationBonus(
    String todayStr,
  ) async {
    final sessions = await (_db.select(_db.workoutSessionsTable)
          ..where((t) => t.deletedAt.isNull()))
        .get();
    final todaySessions = sessions
        .where((s) => todayIso(s.startedAt.toLocal()) == todayStr)
        .toList();
    if (todaySessions.isEmpty) return (0, 0.0, null);

    var maxMin = 0;
    for (final s in todaySessions) {
      final mins = (s.durationSeconds / 60).round();
      if (mins > maxMin) maxMin = mins;
    }
    if (maxMin == 0) maxMin = 45;

    final sessionIds = todaySessions.map((s) => s.id).toList();
    final sets = await (_db.select(_db.workoutSetsTable)
          ..where((t) => t.sessionId.isIn(sessionIds)))
        .get();
    final rpes = sets.where((s) => s.rpe != null).map((s) => s.rpe!).toList();
    final avgRpe = rpes.isEmpty
        ? 0.0
        : rpes.fold<double>(0.0, (a, b) => a + b) / rpes.length;

    if (maxMin >= 60 || avgRpe >= 7.0) {
      return (
        maxMin,
        avgRpe,
        'Bù +750 ml cho buổi tập Gym (${maxMin}p · RPE ${avgRpe.toStringAsFixed(1)})',
      );
    }
    return (
      maxMin,
      avgRpe,
      'Bù +500 ml cho buổi tập Gym (${maxMin}p)',
    );
  }

  Future<void> _bootstrapInitialData(String todayStr) async {
    Map<String, dynamic>? payload;
    if (ApiEndpoints.useMockApi) {
      final raw =
          await rootBundle.loadString('assets/mock_json/mock_m1_health.json');
      payload = jsonDecode(raw) as Map<String, dynamic>;
    } else {
      try {
        final dailyRes = await _dio.get<Map<String, dynamic>>(
          ApiEndpoints.dailyHealth(todayStr),
        );
        final bioRes =
            await _dio.get<Map<String, dynamic>>(ApiEndpoints.biometrics);
        final mealRes =
            await _dio.get<Map<String, dynamic>>(ApiEndpoints.meals);
        final suppRes =
            await _dio.get<Map<String, dynamic>>(ApiEndpoints.supplements);
        payload = <String, dynamic>{
          'daily_health': dailyRes.data ?? const <String, dynamic>{},
          'biometrics': (bioRes.data?['items'] as List?) ?? const [],
          'meals': (mealRes.data?['items'] as List?) ?? const [],
          'supplements': (suppRes.data?['items'] as List?) ?? const [],
        };
      } catch (_) {
        // Neu offline lan dau khi Live API -> khoi tao du lieu rong sach
        payload = null;
      }
    }

    if (payload == null) return;
    final data = payload;

    await _db.transaction(() async {
      final bioList = (data['biometrics'] as List?) ?? const [];
      for (final item in bioList) {
        if (item is! Map<String, dynamic>) continue;
        final model = BiometricLogModel.fromJson(item);
        await _db.into(_db.biometricLogsTable).insertOnConflictUpdate(
              BiometricLogsTableCompanion(
                id: Value(model.id),
                weightKg: Value(model.weightKg),
                bodyFatPct: Value(model.bodyFatPct),
                muscleMassKg: Value(model.muscleMassKg),
                bmi: Value(model.bmi),
                circumferencesJson: Value(jsonEncode(model.circumferencesCm)),
                loggedDate: Value(DateTime.parse(model.loggedDateIso).toUtc()),
                syncStatus: const Value('SYNCED'),
                updatedAt: Value(model.updatedAt.toUtc()),
                deletedAt: Value(model.deletedAt?.toUtc()),
              ),
            );
      }

      final dailyRaw = data['daily_health'];
      if (dailyRaw is Map<String, dynamic> && dailyRaw.isNotEmpty) {
        final d = DailyHealthModel.fromJson(dailyRaw);
        final dateIso = ApiEndpoints.useMockApi ? todayStr : d.logDateIso;
        await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
              DailyHealthLogsTableCompanion(
                id: Value(ApiEndpoints.useMockApi ? 'daily-$todayStr' : d.id),
                logDateIso: Value(dateIso),
                stepsCount: Value(d.stepsCount),
                distanceKm: Value(d.distanceKm),
                activeCaloriesKcal: Value(d.activeCaloriesKcal),
                waterMl: Value(d.waterMl),
                targetWaterMl: Value(d.targetWaterMl),
                sleepHours: Value(d.sleepHours),
                sleepQualityScore: Value(d.sleepQualityScore),
                syncStatus: const Value('SYNCED'),
                updatedAt: Value(d.updatedAt.toUtc()),
              ),
            );
      }

      final mealList = (data['meals'] as List?) ?? const [];
      for (final item in mealList) {
        if (item is! Map<String, dynamic>) continue;
        final m = MealLogModel.fromJson(item);
        final loggedAt = ApiEndpoints.useMockApi
            ? DateTime.now().toUtc()
            : m.loggedAt.toUtc();
        final detectedJson = m.aiDetectedItemsJson == '[]'
            ? jsonEncode([
                {'name_vi': m.title}
              ])
            : m.aiDetectedItemsJson;
        await _db.into(_db.mealLogsTable).insertOnConflictUpdate(
              MealLogsTableCompanion(
                id: Value(m.id),
                mealType: Value(m.mealType),
                localImagePath: Value(m.localImagePath),
                aiDetectedItemsJson: Value(detectedJson),
                totalCalories: Value(m.totalCalories),
                proteinG: Value(m.proteinG),
                carbsG: Value(m.carbsG),
                fatG: Value(m.fatG),
                loggedAt: Value(loggedAt),
                syncStatus: const Value('SYNCED'),
                updatedAt: Value(m.updatedAt.toUtc()),
                deletedAt: Value(m.deletedAt?.toUtc()),
              ),
            );
      }

      final suppList = (data['supplements'] as List?) ?? const [];
      for (final item in suppList) {
        if (item is! Map<String, dynamic>) continue;
        final s = SupplementScheduleModel.fromJson(item);
        await _db.into(_db.supplementSchedulesTable).insertOnConflictUpdate(
              SupplementSchedulesTableCompanion(
                id: Value(s.id),
                supplementName: Value(s.supplementName),
                dosageLabel: Value(s.dosageLabel),
                reminderTimeHhMm: Value(s.reminderTimeHhMm),
                workoutDaysOnly: Value(s.workoutDaysOnly),
                isActive: Value(s.isActive),
                syncStatus: const Value('SYNCED'),
                updatedAt: Value(s.updatedAt.toUtc()),
              ),
            );
        if (s.takenToday) {
          await _intakeStore.markTaken(s.id, dateIso: todayStr);
        }
      }
    });
  }

  Future<void> saveBiometric({
    required double weightKg,
    required double heightCm,
    double? bodyFatPct,
    double? muscleMassKg,
    Map<String, double> circumferencesCm = const {},
    DateTime? loggedDate,
  }) async {
    final nowUtc = DateTime.now().toUtc();
    final targetDate = (loggedDate ?? DateTime.now()).toUtc();
    final bmi = BiometricLogModel.calculateBmi(weightKg, heightCm);
    final id = _uuid.v4();

    await _db.into(_db.biometricLogsTable).insert(
          BiometricLogsTableCompanion.insert(
            id: id,
            weightKg: weightKg,
            bodyFatPct: Value(bodyFatPct),
            muscleMassKg: Value(muscleMassKg),
            bmi: bmi,
            circumferencesJson: Value(jsonEncode(circumferencesCm)),
            loggedDate: targetDate,
            syncStatus: const Value('PENDING_CREATE'),
            updatedAt: nowUtc,
          ),
        );
  }

  Future<void> addWaterMl({
    required int deltaMl,
    required double weightKg,
    int? targetWaterMlOverride,
  }) async {
    final todayStr = todayIso();
    final nowUtc = DateTime.now().toUtc();
    final existing = await _findDailyRowByDate(todayStr);

    final targetMl = targetWaterMlOverride ??
        existing?.targetWaterMl ??
        DailyHealthModel.calculateTargetWaterMl(weightKg);
    final nextWater = ((existing?.waterMl ?? 0) + deltaMl).clamp(0, 12000);

    await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
          DailyHealthLogsTableCompanion(
            id: Value(existing?.id ?? 'daily-$todayStr'),
            logDateIso: Value(todayStr),
            stepsCount: Value(existing?.stepsCount ?? 0),
            distanceKm: Value(existing?.distanceKm ?? 0.0),
            activeCaloriesKcal: Value(existing?.activeCaloriesKcal ?? 0),
            waterMl: Value(nextWater),
            targetWaterMl: Value(targetMl),
            sleepHours: Value(existing?.sleepHours ?? 0.0),
            sleepQualityScore: Value(existing?.sleepQualityScore),
            syncStatus: const Value('PENDING_UPDATE'),
            updatedAt: Value(nowUtc),
          ),
        );
  }

  Future<void> updateTargetWaterMl(int targetWaterMl) async {
    final todayStr = todayIso();
    final nowUtc = DateTime.now().toUtc();
    final existing = await _findDailyRowByDate(todayStr);
    if (existing == null) return;
    await (_db.update(_db.dailyHealthLogsTable)
          ..where((t) => t.id.equals(existing.id)))
        .write(
      DailyHealthLogsTableCompanion(
        targetWaterMl: Value(targetWaterMl),
        syncStatus: const Value('PENDING_UPDATE'),
        updatedAt: Value(nowUtc),
      ),
    );
  }

  Future<void> saveSleepLog({
    required double sleepHours,
    int? qualityScore,
    DateTime? logDate,
  }) async {
    final targetIso = todayIso(logDate);
    final nowUtc = DateTime.now().toUtc();
    final existing = await _findDailyRowByDate(targetIso);

    await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
          DailyHealthLogsTableCompanion(
            id: Value(existing?.id ?? 'daily-$targetIso'),
            logDateIso: Value(targetIso),
            stepsCount: Value(existing?.stepsCount ?? 0),
            distanceKm: Value(existing?.distanceKm ?? 0.0),
            activeCaloriesKcal: Value(existing?.activeCaloriesKcal ?? 0),
            waterMl: Value(existing?.waterMl ?? 0),
            targetWaterMl: Value(existing?.targetWaterMl ?? 2450),
            sleepHours: Value((sleepHours * 10).round() / 10.0),
            sleepQualityScore: Value(qualityScore),
            syncStatus: const Value('PENDING_UPDATE'),
            updatedAt: Value(nowUtc),
          ),
        );
  }

  Future<void> saveMealLog({
    required String mealType,
    required String title,
    required double calories,
    required double proteinG,
    required double carbsG,
    required double fatG,
    String? localImagePath,
    List<Map<String, dynamic>> aiDetectedItems = const [],
    DateTime? loggedAt,
  }) async {
    final nowUtc = DateTime.now().toUtc();
    final items = aiDetectedItems.isNotEmpty
        ? aiDetectedItems
        : [
            <String, dynamic>{
              'name_vi': title,
              'calories': calories,
              'protein_g': proteinG,
              'carbs_g': carbsG,
              'fat_g': fatG,
            },
          ];

    await _db.into(_db.mealLogsTable).insert(
          MealLogsTableCompanion.insert(
            id: _uuid.v4(),
            mealType: mealType.toUpperCase(),
            localImagePath: Value(localImagePath),
            aiDetectedItemsJson: Value(jsonEncode(items)),
            totalCalories: Value(calories),
            proteinG: Value(proteinG),
            carbsG: Value(carbsG),
            fatG: Value(fatG),
            loggedAt: (loggedAt ?? DateTime.now()).toUtc(),
            syncStatus: const Value('PENDING_CREATE'),
            updatedAt: nowUtc,
          ),
        );
  }

  Future<void> softDeleteMeal(String mealId) async {
    final nowUtc = DateTime.now().toUtc();
    await (_db.update(_db.mealLogsTable)..where((t) => t.id.equals(mealId)))
        .write(
      MealLogsTableCompanion(
        deletedAt: Value(nowUtc),
        syncStatus: const Value('PENDING_DELETE'),
        updatedAt: Value(nowUtc),
      ),
    );
  }

  Future<String> saveSupplementSchedule({
    required String name,
    required String dosageLabel,
    required String reminderTimeHhMm,
    bool workoutDaysOnly = false,
  }) async {
    final id = _uuid.v4();
    final nowUtc = DateTime.now().toUtc();
    await _db.into(_db.supplementSchedulesTable).insert(
          SupplementSchedulesTableCompanion.insert(
            id: id,
            supplementName: name.trim(),
            dosageLabel: dosageLabel.trim(),
            reminderTimeHhMm: reminderTimeHhMm,
            workoutDaysOnly: Value(workoutDaysOnly),
            isActive: const Value(true),
            syncStatus: const Value('PENDING_CREATE'),
            updatedAt: nowUtc,
          ),
        );
    return id;
  }

  Future<void> setSupplementTakenToday(String supplementId, bool taken) async {
    final todayStr = todayIso();
    if (taken) {
      await _intakeStore.markTaken(supplementId, dateIso: todayStr);
    } else {
      await _intakeStore.unmarkTaken(supplementId, dateIso: todayStr);
    }
    await (_db.update(_db.supplementSchedulesTable)
          ..where((t) => t.id.equals(supplementId)))
        .write(
      SupplementSchedulesTableCompanion(
        updatedAt: Value(DateTime.now().toUtc()),
      ),
    );
  }

  Future<void> softDeleteSupplement(String supplementId) async {
    final nowUtc = DateTime.now().toUtc();
    await (_db.update(_db.supplementSchedulesTable)
          ..where((t) => t.id.equals(supplementId)))
        .write(
      SupplementSchedulesTableCompanion(
        isActive: const Value(false),
        deletedAt: Value(nowUtc),
        syncStatus: const Value('PENDING_DELETE'),
        updatedAt: Value(nowUtc),
      ),
    );
  }

  BiometricLogModel _mapBiometricRow(BiometricLogsTableData row) {
    final rawMap = _decodeMapSafe(row.circumferencesJson);
    return BiometricLogModel(
      id: row.id,
      weightKg: row.weightKg,
      bodyFatPct: row.bodyFatPct,
      muscleMassKg: row.muscleMassKg,
      bmi: row.bmi,
      circumferencesCm:
          rawMap.map((k, v) => MapEntry(k, (v as num).toDouble())),
      loggedDateIso: todayIso(row.loggedDate.toLocal()),
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    );
  }

  DailyHealthModel _mapDailyRow(DailyHealthLogsTableData row) {
    return DailyHealthModel(
      id: row.id,
      logDateIso: row.logDateIso,
      stepsCount: row.stepsCount,
      distanceKm: row.distanceKm,
      activeCaloriesKcal: row.activeCaloriesKcal,
      waterMl: row.waterMl,
      targetWaterMl: row.targetWaterMl,
      sleepHours: row.sleepHours,
      sleepQualityScore: row.sleepQualityScore,
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
    );
  }

  MealLogModel _mapMealRow(MealLogsTableData row) {
    return MealLogModel(
      id: row.id,
      mealType: row.mealType,
      title: MealLogModel.extractTitleFromDetectedItems(row.aiDetectedItemsJson),
      localImagePath: row.localImagePath,
      aiDetectedItemsJson: row.aiDetectedItemsJson,
      totalCalories: row.totalCalories,
      proteinG: row.proteinG,
      carbsG: row.carbsG,
      fatG: row.fatG,
      loggedAt: row.loggedAt,
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    );
  }

  Map<String, dynamic> _decodeMapSafe(String raw) {
    try {
      final d = jsonDecode(raw);
      if (d is Map<String, dynamic>) return d;
    } catch (_) {}
    return const <String, dynamic>{};
  }
}

class HealthDashboardController extends StateNotifier<HealthDashboardState> {
  final HealthRepository _repository;
  final SyncQueueManager _syncManager;
  final WorkmanagerReminderService _reminderService;
  final AuthUserProfile? _userProfile;
  final UserFitnessProfile? _fitnessProfile;
  String? _activityLevelOverride;
  String? _fitnessGoalOverride;

  HealthDashboardController(
    this._repository,
    this._syncManager,
    this._reminderService,
    this._userProfile, {
    UserFitnessProfile? fitnessProfile,
  })  : _fitnessProfile = fitnessProfile,
        super(const HealthDashboardState(isLoading: true)) {
    load();
  }

  bool get _hasWizard => _fitnessProfile?.hasCompletedWizard ?? false;

  double get _heightCm => _hasWizard
      ? _fitnessProfile!.heightCm
      : (_userProfile?.heightCm ?? 172.0);
  String get _gender => _hasWizard
      ? _fitnessProfile!.gender
      : (_userProfile?.gender ?? 'MALE');
  int get _ageYears => _hasWizard
      ? _fitnessProfile!.ageYears
      : (_userProfile?.calculateAgeYears() ?? 24);

  Future<void> load({
    String? activityLevelOverride,
    String? fitnessGoalOverride,
  }) async {
    if (activityLevelOverride != null) {
      _activityLevelOverride = activityLevelOverride;
    }
    if (fitnessGoalOverride != null) {
      _fitnessGoalOverride = fitnessGoalOverride;
    }
    state = state.copyWith(isLoading: true, clearError: true);
    try {
      final act = _activityLevelOverride ??
          (_hasWizard
              ? _fitnessProfile!.derivedActivityLevel
              : _userProfile?.activityLevel) ??
          state.activityLevel;
      final goal = _fitnessGoalOverride ??
          (_hasWizard
              ? _fitnessProfile!.derivedFitnessGoal
              : _userProfile?.fitnessGoal) ??
          state.fitnessGoal;
      final loaded = await _repository.loadDashboardData(
        heightCm: _heightCm,
        gender: _gender,
        ageYears: _ageYears,
        activityLevel: act,
        fitnessGoal: goal,
      );
      var resolved = loaded;
      if (_hasWizard &&
          _activityLevelOverride == null &&
          _fitnessGoalOverride == null) {
        final fp = _fitnessProfile!;
        final currentWeight =
            loaded.latestBiometric?.weightKg ?? fp.currentWeightKg;
        final personalizedProfile =
            fp.copyWith(currentWeightKg: currentWeight);
        resolved = loaded.copyWith(
          targetCaloriesKcal: personalizedProfile.targetCaloriesKcal,
          macroTargets: personalizedProfile.macroTargets,
          bmrKcal: personalizedProfile.bmrKcal,
        );
      }
      state = resolved.copyWith(
        hydrationReminderEnabled: state.hydrationReminderEnabled,
        supplementReminderEnabled: state.supplementReminderEnabled,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: 'Không thể tải dữ liệu sức khỏe: $e',
      );
    }
  }

  Future<void> changeNutritionGoal({
    required String fitnessGoal,
    required String activityLevel,
  }) async {
    await load(
      fitnessGoalOverride: fitnessGoal,
      activityLevelOverride: activityLevel,
    );
  }

  Future<void> addBiometric({
    required double weightKg,
    double? bodyFatPct,
    double? muscleMassKg,
    Map<String, double> circumferencesCm = const {},
    DateTime? loggedDate,
  }) async {
    await _repository.saveBiometric(
      weightKg: weightKg,
      heightCm: _heightCm,
      bodyFatPct: bodyFatPct,
      muscleMassKg: muscleMassKg,
      circumferencesCm: circumferencesCm,
      loggedDate: loggedDate,
    );
    await load();
  }

  Future<void> addWaterMl(int deltaMl) async {
    final currentWeight = state.latestBiometric?.weightKg ?? 70.0;
    await _repository.addWaterMl(
      deltaMl: deltaMl,
      weightKg: currentWeight,
      targetWaterMlOverride: state.dailyHealth?.targetWaterMl,
    );
    await load();
  }

  /// Tinh lai muc tieu nuoc bu mo hoi sau buoi tap Gym (F03): +500ml tap vua, +750ml >=60p hoac RPE>=7
  Future<void> applyWorkoutHydrationBonus({
    required int workoutMinutes,
    required double workoutRpe,
  }) async {
    final currentWeight = state.latestBiometric?.weightKg ?? 70.0;
    final newTarget = DailyHealthModel.calculateTargetWaterMl(
      currentWeight,
      workoutMinutes: workoutMinutes,
      workoutRpe: workoutRpe,
    );
    final baseTarget = DailyHealthModel.calculateTargetWaterMl(currentWeight);
    final bonus = (newTarget - baseTarget).clamp(0, 1500);
    await _repository.updateTargetWaterMl(newTarget);
    await load();
    state = state.copyWith(
      workoutBonusWaterMl: bonus,
      workoutBonusReason: bonus >= 750
          ? 'Bù +750 ml sau buổi tập ${workoutMinutes}p RPE ${workoutRpe.toStringAsFixed(1)}'
          : 'Bù +500 ml sau buổi tập ${workoutMinutes}p',
    );
  }

  Future<void> toggleHydrationReminder(bool enabled) async {
    state = state.copyWith(hydrationReminderEnabled: enabled);
    await _reminderService.scheduleHydrationReminders(
      enabled: enabled,
      currentMl: state.dailyHealth?.waterMl ?? 0,
      targetMl: state.dailyHealth?.targetWaterMl ?? 2450,
    );
  }

  Future<void> sendSampleHydrationReminder() async {
    await _reminderService.showHydrationNotification(
      currentMl: state.dailyHealth?.waterMl ?? 0,
      targetMl: state.dailyHealth?.targetWaterMl ?? 2450,
    );
  }

  Future<void> logSleep({
    required double sleepHours,
    int? qualityScore,
    DateTime? logDate,
  }) async {
    await _repository.saveSleepLog(
      sleepHours: sleepHours,
      qualityScore: qualityScore,
      logDate: logDate,
    );
    await load();
  }

  Future<void> addMeal({
    required String mealType,
    required String title,
    required double calories,
    required double proteinG,
    required double carbsG,
    required double fatG,
    String? localImagePath,
    List<Map<String, dynamic>> aiDetectedItems = const [],
  }) async {
    await _repository.saveMealLog(
      mealType: mealType,
      title: title,
      calories: calories,
      proteinG: proteinG,
      carbsG: carbsG,
      fatG: fatG,
      localImagePath: localImagePath,
      aiDetectedItems: aiDetectedItems,
    );
    await load();
  }

  Future<void> deleteMeal(String mealId) async {
    await _repository.softDeleteMeal(mealId);
    await load();
  }

  Future<void> addSupplement({
    required String name,
    required String dosageLabel,
    required String reminderTimeHhMm,
    bool workoutDaysOnly = false,
  }) async {
    final id = await _repository.saveSupplementSchedule(
      name: name,
      dosageLabel: dosageLabel,
      reminderTimeHhMm: reminderTimeHhMm,
      workoutDaysOnly: workoutDaysOnly,
    );
    await _reminderService.scheduleSupplementReminders(
      enabled: state.supplementReminderEnabled,
      nextSupplementId: id,
      nextSupplementName: name,
      nextDosageLabel: dosageLabel,
    );
    await load();
  }

  Future<void> toggleSupplementTakenToday(String supplementId) async {
    final item = state.supplements.firstWhere(
      (s) => s.id == supplementId,
      orElse: () => SupplementScheduleModel(
        id: supplementId,
        supplementName: '',
        dosageLabel: '',
        reminderTimeHhMm: '08:00',
        updatedAt: DateTime.now().toUtc(),
      ),
    );
    await _repository.setSupplementTakenToday(supplementId, !item.takenToday);
    await load();
  }

  Future<void> deleteSupplement(String supplementId) async {
    await _repository.softDeleteSupplement(supplementId);
    await load();
  }

  Future<void> toggleSupplementReminders(bool enabled) async {
    state = state.copyWith(supplementReminderEnabled: enabled);
    final first = state.supplements.isNotEmpty ? state.supplements.first : null;
    await _reminderService.scheduleSupplementReminders(
      enabled: enabled,
      nextSupplementId: first?.id,
      nextSupplementName: first?.supplementName,
      nextDosageLabel: first?.dosageLabel,
    );
  }

  Future<bool> sendSampleSupplementReminder(SupplementScheduleModel item) {
    return _reminderService.showSupplementNotification(
      supplementId: item.id,
      supplementName: item.supplementName,
      dosageLabel: item.dosageLabel,
    );
  }

  Future<SyncReport> syncWithServer() async {
    state = state.copyWith(isSyncing: true, clearSyncMessage: true);
    final report = await _syncManager.syncNow();
    await load();
    final msg = report.skippedOffline
        ? 'Chưa có mạng — ${report.remainingPendingCount} thay đổi đã được lưu trên thiết bị.'
        : (report.errorMessage ??
            'Đã đồng bộ ${report.pushedCount} thay đổi lên máy chủ.');
    state = state.copyWith(isSyncing: false, lastSyncMessage: msg);
    return report;
  }

  /// Tuong thich nguoc cho HealthDashboardScreen cu (neu can)
  void markSynced() {
    syncWithServer();
  }

  void logOfflineWeight(double weightKg, {double heightCm = 172.0}) {
    _repository
        .saveBiometric(weightKg: weightKg, heightCm: heightCm)
        .then((_) => load());
  }
}

final healthRepositoryProvider = Provider<HealthRepository>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final dio = ref.watch(dioProvider);
  final intakeStore = ref.watch(supplementIntakeStoreProvider);
  final syncManager = ref.watch(syncQueueManagerProvider);
  return HealthRepository(db, dio, intakeStore, syncManager);
});

final healthDashboardProvider =
    StateNotifierProvider<HealthDashboardController, HealthDashboardState>(
  (ref) {
    final repo = ref.watch(healthRepositoryProvider);
    final syncMgr = ref.watch(syncQueueManagerProvider);
    final reminderSvc = ref.watch(workmanagerReminderServiceProvider);
    final user = ref.watch(authControllerProvider.select((s) => s.user));
    final fitnessProfile = ref.watch(userFitnessProfileProvider);
    return HealthDashboardController(
      repo,
      syncMgr,
      reminderSvc,
      user,
      fitnessProfile: fitnessProfile,
    );
  },
);
