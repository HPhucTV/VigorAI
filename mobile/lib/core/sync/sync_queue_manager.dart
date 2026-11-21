// [OWNER: M1] Co che dong bo hai chieu Offline-First (T-M1-12: Push/Pull LWW & max(steps_count))
import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../database/app_database.dart';
import '../network/api_endpoints.dart';
import '../network/dio_client.dart';

enum SyncStatus {
  synced,
  pendingCreate,
  pendingUpdate,
  pendingDelete,
}

extension SyncStatusWire on SyncStatus {
  String get wireValue {
    switch (this) {
      case SyncStatus.synced:
        return 'SYNCED';
      case SyncStatus.pendingCreate:
        return 'PENDING_CREATE';
      case SyncStatus.pendingUpdate:
        return 'PENDING_UPDATE';
      case SyncStatus.pendingDelete:
        return 'PENDING_DELETE';
    }
  }
}

/// Ham thuan giai quyet xung dot dong bo (Last-Write-Wins UTC & max steps_count).
class SyncConflictResolver {
  const SyncConflictResolver._();

  static bool shouldServerWin({
    required DateTime localUpdatedAt,
    required DateTime serverUpdatedAt,
  }) {
    return !serverUpdatedAt.toUtc().isBefore(localUpdatedAt.toUtc());
  }

  static int mergeDailyHealthSteps({
    required int localSteps,
    required int serverSteps,
  }) {
    return math.max(localSteps, serverSteps);
  }
}

class SyncReport {
  final bool skippedOffline;
  final int pushedCount;
  final int pulledCount;
  final int remainingPendingCount;
  final DateTime syncedAtUtc;
  final String? errorMessage;

  const SyncReport({
    this.skippedOffline = false,
    this.pushedCount = 0,
    this.pulledCount = 0,
    this.remainingPendingCount = 0,
    required this.syncedAtUtc,
    this.errorMessage,
  });

  bool get isSuccess => errorMessage == null && !skippedOffline;
}

class SyncQueueState {
  final bool isSyncing;
  final int pendingCount;
  final DateTime? lastSyncedAtUtc;
  final String? lastError;

  const SyncQueueState({
    this.isSyncing = false,
    this.pendingCount = 0,
    this.lastSyncedAtUtc,
    this.lastError,
  });

  SyncQueueState copyWith({
    bool? isSyncing,
    int? pendingCount,
    DateTime? lastSyncedAtUtc,
    String? lastError,
    bool clearError = false,
  }) {
    return SyncQueueState(
      isSyncing: isSyncing ?? this.isSyncing,
      pendingCount: pendingCount ?? this.pendingCount,
      lastSyncedAtUtc: lastSyncedAtUtc ?? this.lastSyncedAtUtc,
      lastError: clearError ? null : (lastError ?? this.lastError),
    );
  }
}

class SyncQueueManager {
  final AppDatabase _db;
  final Dio _dio;
  final FlutterSecureStorage _storage;
  final Connectivity _connectivity;

  SyncQueueManager(
    this._db,
    this._dio,
    this._storage, {
    Connectivity? connectivity,
  }) : _connectivity = connectivity ?? Connectivity();

  Future<bool> isOnline() async {
    try {
      final results = await _connectivity.checkConnectivity();
      return results.any((r) => r != ConnectivityResult.none);
    } catch (_) {
      return true;
    }
  }

  Future<int> countPendingChanges() async {
    final bioCount = (await (_db.select(_db.biometricLogsTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final dailyCount = (await (_db.select(_db.dailyHealthLogsTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final mealCount = (await (_db.select(_db.mealLogsTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final suppCount = (await (_db.select(_db.supplementSchedulesTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final routineCount = (await (_db.select(_db.workoutRoutinesTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final sessionCount = (await (_db.select(_db.workoutSessionsTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;
    final setCount = (await (_db.select(_db.workoutSetsTable)
              ..where((t) => t.syncStatus.isNotValue('SYNCED')))
            .get())
        .length;

    return bioCount +
        dailyCount +
        mealCount +
        suppCount +
        routineCount +
        sessionCount +
        setCount;
  }

  Future<int> pushPendingChanges() async {
    final pendingBios = await (_db.select(_db.biometricLogsTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingDailies = await (_db.select(_db.dailyHealthLogsTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingMeals = await (_db.select(_db.mealLogsTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingSupps = await (_db.select(_db.supplementSchedulesTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingRoutines = await (_db.select(_db.workoutRoutinesTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingSessions = await (_db.select(_db.workoutSessionsTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();
    final pendingSets = await (_db.select(_db.workoutSetsTable)
          ..where((t) => t.syncStatus.isNotValue('SYNCED')))
        .get();

    final totalPending = pendingBios.length +
        pendingDailies.length +
        pendingMeals.length +
        pendingSupps.length +
        pendingRoutines.length +
        pendingSessions.length +
        pendingSets.length;
    if (totalPending == 0) return 0;

    final payload = <String, dynamic>{
      'biometric_logs': pendingBios
          .map(
            (b) => <String, dynamic>{
              'id': b.id,
              'weight_kg': b.weightKg,
              'body_fat_pct': b.bodyFatPct,
              'muscle_mass_kg': b.muscleMassKg,
              'bmi': b.bmi,
              'circumferences_cm': _decodeMapSafe(b.circumferencesJson),
              'logged_date': _formatDateIso(b.loggedDate),
              'updated_at': b.updatedAt.toUtc().toIso8601String(),
              'deleted_at': b.deletedAt?.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'daily_health_logs': pendingDailies
          .map(
            (d) => <String, dynamic>{
              'id': d.id,
              'log_date': d.logDateIso,
              'steps_count': d.stepsCount,
              'distance_km': d.distanceKm,
              'active_calories_kcal': d.activeCaloriesKcal,
              'water_ml': d.waterMl,
              'target_water_ml': d.targetWaterMl,
              'sleep_hours': d.sleepHours,
              'sleep_quality_score': d.sleepQualityScore,
              'updated_at': d.updatedAt.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'supplement_schedules': pendingSupps
          .map(
            (s) => <String, dynamic>{
              'id': s.id,
              'supplement_name': s.supplementName,
              'dosage_label': s.dosageLabel,
              'reminder_time': s.reminderTimeHhMm,
              'workout_days_only': s.workoutDaysOnly,
              'is_active': s.isActive,
              'updated_at': s.updatedAt.toUtc().toIso8601String(),
              'deleted_at': s.deletedAt?.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'meal_logs': pendingMeals
          .map(
            (m) => <String, dynamic>{
              'id': m.id,
              'meal_type': m.mealType,
              'ai_detected_items': _decodeListSafe(m.aiDetectedItemsJson),
              'total_calories': m.totalCalories,
              'protein_g': m.proteinG,
              'carbs_g': m.carbsG,
              'fat_g': m.fatG,
              'logged_at': m.loggedAt.toUtc().toIso8601String(),
              'updated_at': m.updatedAt.toUtc().toIso8601String(),
              'deleted_at': m.deletedAt?.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'workout_routines': pendingRoutines
          .map(
            (r) => <String, dynamic>{
              'id': r.id,
              'name': r.name,
              'split_type': r.splitType,
              'scheduled_weekdays': _decodeListSafe(r.scheduledWeekdaysJson),
              'exercises': _decodeListSafe(r.exercisesJson),
              'is_template': r.isTemplate,
              'updated_at': r.updatedAt.toUtc().toIso8601String(),
              'deleted_at': r.deletedAt?.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'workout_sessions': pendingSessions
          .map(
            (ws) => <String, dynamic>{
              'id': ws.id,
              'routine_id': ws.routineId,
              'session_title': ws.sessionTitle,
              'started_at': ws.startedAt.toUtc().toIso8601String(),
              'completed_at': ws.completedAt?.toUtc().toIso8601String(),
              'duration_seconds': ws.durationSeconds,
              'total_volume_kg': ws.totalVolumeKg,
              'status': ws.status,
              'updated_at': ws.updatedAt.toUtc().toIso8601String(),
              'deleted_at': ws.deletedAt?.toUtc().toIso8601String(),
            },
          )
          .toList(),
      'workout_sets': pendingSets
          .map(
            (wset) => <String, dynamic>{
              'id': wset.id,
              'session_id': wset.sessionId,
              'exercise_id': wset.exerciseId,
              'set_number': wset.setNumber,
              'set_type': wset.setType,
              'weight_kg': wset.weightKg,
              'reps': wset.reps,
              'rpe': wset.rpe,
              'estimated_1rm': wset.estimated1rm,
              'is_pr': wset.isPr,
              'completed_at': wset.completedAt.toUtc().toIso8601String(),
              'updated_at': wset.updatedAt.toUtc().toIso8601String(),
            },
          )
          .toList(),
    };

    final response = await _dio.post<Map<String, dynamic>>(
      ApiEndpoints.syncPush,
      data: payload,
    );
    final data = response.data ?? const <String, dynamic>{};
    final syncedIdsMap = (data['synced_ids'] as Map<String, dynamic>?) ?? const {};

    var markedCount = 0;
    await _db.transaction(() async {
      final bioIds = _stringList(syncedIdsMap['biometric_logs']);
      if (bioIds.isNotEmpty) {
        await (_db.update(_db.biometricLogsTable)..where((t) => t.id.isIn(bioIds)))
            .write(const BiometricLogsTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += bioIds.length;
      }
      final dailyIds = _stringList(syncedIdsMap['daily_health_logs']);
      if (dailyIds.isNotEmpty) {
        await (_db.update(_db.dailyHealthLogsTable)..where((t) => t.id.isIn(dailyIds)))
            .write(const DailyHealthLogsTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += dailyIds.length;
      }
      final suppIds = _stringList(syncedIdsMap['supplement_schedules']);
      if (suppIds.isNotEmpty) {
        await (_db.update(_db.supplementSchedulesTable)
              ..where((t) => t.id.isIn(suppIds)))
            .write(const SupplementSchedulesTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += suppIds.length;
      }
      final mealIds = _stringList(syncedIdsMap['meal_logs']);
      if (mealIds.isNotEmpty) {
        await (_db.update(_db.mealLogsTable)..where((t) => t.id.isIn(mealIds)))
            .write(const MealLogsTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += mealIds.length;
      }
      final routineIds = _stringList(syncedIdsMap['workout_routines']);
      if (routineIds.isNotEmpty) {
        await (_db.update(_db.workoutRoutinesTable)
              ..where((t) => t.id.isIn(routineIds)))
            .write(const WorkoutRoutinesTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += routineIds.length;
      }
      final sessionIds = _stringList(syncedIdsMap['workout_sessions']);
      if (sessionIds.isNotEmpty) {
        await (_db.update(_db.workoutSessionsTable)
              ..where((t) => t.id.isIn(sessionIds)))
            .write(const WorkoutSessionsTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += sessionIds.length;
      }
      final setIds = _stringList(syncedIdsMap['workout_sets']);
      if (setIds.isNotEmpty) {
        await (_db.update(_db.workoutSetsTable)..where((t) => t.id.isIn(setIds)))
            .write(const WorkoutSetsTableCompanion(syncStatus: Value('SYNCED')));
        markedCount += setIds.length;
      }
    });

    return markedCount > 0 ? markedCount : totalPending;
  }

  Future<int> pullServerUpdates({DateTime? sinceUtc}) async {
    final storedSince = sinceUtc?.toUtc().toIso8601String() ??
        await _storage.read(key: StorageKeys.lastSyncUtc);

    final response = await _dio.get<Map<String, dynamic>>(
      ApiEndpoints.syncPull,
      queryParameters: storedSince != null && storedSince.isNotEmpty
          ? <String, dynamic>{'since': storedSince}
          : null,
    );
    final data = response.data ?? const <String, dynamic>{};
    final records = (data['records'] as Map<String, dynamic>?) ?? const {};
    var appliedCount = 0;

    await _db.transaction(() async {
      // 1. Biometric Logs (LWW)
      for (final raw in (records['biometric_logs'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        if (id == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final legacyMockId =
            raw['logged_date'] != null ? 'bio-${raw['logged_date']}' : null;
        var existing = await (_db.select(_db.biometricLogsTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null && legacyMockId != null) {
          existing = await (_db.select(_db.biometricLogsTable)
                ..where((t) => t.id.equals(legacyMockId)))
              .getSingleOrNull();
        }
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          if (existing != null && existing.id != id) {
            await (_db.delete(_db.biometricLogsTable)
                  ..where((t) => t.id.equals(existing!.id)))
                .go();
          }
          await _db.into(_db.biometricLogsTable).insertOnConflictUpdate(
                BiometricLogsTableCompanion(
                  id: Value(id),
                  weightKg: Value((raw['weight_kg'] as num).toDouble()),
                  bodyFatPct: Value((raw['body_fat_pct'] as num?)?.toDouble()),
                  muscleMassKg: Value((raw['muscle_mass_kg'] as num?)?.toDouble()),
                  bmi: Value((raw['bmi'] as num).toDouble()),
                  circumferencesJson: Value(
                    jsonEncode(raw['circumferences_cm'] ?? const <String, dynamic>{}),
                  ),
                  loggedDate: Value(
                    DateTime.parse(raw['logged_date'] as String).toUtc(),
                  ),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                  deletedAt: Value(
                    raw['deleted_at'] != null
                        ? _parseUtc(raw['deleted_at'])
                        : null,
                  ),
                ),
              );
          appliedCount++;
        }
      }

      // 2. Daily Health Logs (LWW + max(steps_count))
      for (final raw in (records['daily_health_logs'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final logDateIso = raw['log_date']?.toString();
        if (logDateIso == null) continue;
        final id = raw['id']?.toString() ?? 'daily-$logDateIso';
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.dailyHealthLogsTable)
              ..where((t) => t.logDateIso.equals(logDateIso)))
            .getSingleOrNull();

        final serverSteps = (raw['steps_count'] as num?)?.toInt() ?? 0;
        final serverKcal = (raw['active_calories_kcal'] as num?)?.toInt() ?? 0;

        if (existing == null) {
          await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
                DailyHealthLogsTableCompanion(
                  id: Value(id),
                  logDateIso: Value(logDateIso),
                  stepsCount: Value(serverSteps),
                  distanceKm: Value((raw['distance_km'] as num?)?.toDouble() ?? 0.0),
                  activeCaloriesKcal: Value(serverKcal),
                  waterMl: Value((raw['water_ml'] as num?)?.toInt() ?? 0),
                  targetWaterMl:
                      Value((raw['target_water_ml'] as num?)?.toInt() ?? 2450),
                  sleepHours: Value((raw['sleep_hours'] as num?)?.toDouble() ?? 0.0),
                  sleepQualityScore:
                      Value((raw['sleep_quality_score'] as num?)?.toInt()),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                ),
              );
          appliedCount++;
        } else {
          final mergedSteps = SyncConflictResolver.mergeDailyHealthSteps(
            localSteps: existing.stepsCount,
            serverSteps: serverSteps,
          );
          final serverWins = SyncConflictResolver.shouldServerWin(
            localUpdatedAt: existing.updatedAt,
            serverUpdatedAt: serverUpdated,
          );
          await (_db.update(_db.dailyHealthLogsTable)
                ..where((t) => t.id.equals(existing.id)))
              .write(
            DailyHealthLogsTableCompanion(
              stepsCount: Value(mergedSteps),
              activeCaloriesKcal: Value(math.max(existing.activeCaloriesKcal, serverKcal)),
              distanceKm: Value(
                serverWins
                    ? math.max(
                        existing.distanceKm,
                        (raw['distance_km'] as num?)?.toDouble() ?? 0.0,
                      )
                    : existing.distanceKm,
              ),
              waterMl: Value(
                serverWins
                    ? (raw['water_ml'] as num?)?.toInt() ?? existing.waterMl
                    : existing.waterMl,
              ),
              targetWaterMl: Value(
                serverWins
                    ? (raw['target_water_ml'] as num?)?.toInt() ??
                        existing.targetWaterMl
                    : existing.targetWaterMl,
              ),
              sleepHours: Value(
                serverWins
                    ? (raw['sleep_hours'] as num?)?.toDouble() ?? existing.sleepHours
                    : existing.sleepHours,
              ),
              sleepQualityScore: Value(
                serverWins
                    ? (raw['sleep_quality_score'] as num?)?.toInt()
                    : existing.sleepQualityScore,
              ),
              syncStatus: Value(
                mergedSteps > serverSteps
                    ? 'PENDING_UPDATE'
                    : (serverWins ? 'SYNCED' : existing.syncStatus),
              ),
              updatedAt: Value(serverWins ? serverUpdated : existing.updatedAt),
            ),
          );
          appliedCount++;
        }
      }

      // 3. Meal Logs (LWW)
      for (final raw in (records['meal_logs'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        if (id == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.mealLogsTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          await _db.into(_db.mealLogsTable).insertOnConflictUpdate(
                MealLogsTableCompanion(
                  id: Value(id),
                  mealType: Value((raw['meal_type'] as String?) ?? 'LUNCH'),
                  localImagePath: Value(raw['local_image_path'] as String?),
                  aiDetectedItemsJson: Value(
                    jsonEncode(raw['ai_detected_items'] ?? const <dynamic>[]),
                  ),
                  totalCalories: Value((raw['total_calories'] as num?)?.toDouble() ?? 0.0),
                  proteinG: Value((raw['protein_g'] as num?)?.toDouble() ?? 0.0),
                  carbsG: Value((raw['carbs_g'] as num?)?.toDouble() ?? 0.0),
                  fatG: Value((raw['fat_g'] as num?)?.toDouble() ?? 0.0),
                  loggedAt: Value(_parseUtc(raw['logged_at'])),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                  deletedAt: Value(
                    raw['deleted_at'] != null
                        ? _parseUtc(raw['deleted_at'])
                        : null,
                  ),
                ),
              );
          appliedCount++;
        }
      }

      // 4. Supplement Schedules (LWW)
      for (final raw in (records['supplement_schedules'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        if (id == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.supplementSchedulesTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          await _db.into(_db.supplementSchedulesTable).insertOnConflictUpdate(
                SupplementSchedulesTableCompanion(
                  id: Value(id),
                  supplementName: Value((raw['supplement_name'] as String?) ?? 'Supplement'),
                  dosageLabel: Value((raw['dosage_label'] as String?) ?? '1 liều'),
                  reminderTimeHhMm: Value((raw['reminder_time'] as String?) ?? '08:00'),
                  workoutDaysOnly: Value((raw['workout_days_only'] as bool?) ?? false),
                  isActive: Value((raw['is_active'] as bool?) ?? true),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                  deletedAt: Value(
                    raw['deleted_at'] != null
                        ? _parseUtc(raw['deleted_at'])
                        : null,
                  ),
                ),
              );
          appliedCount++;
        }
      }

      // 5. Workout Routines (LWW)
      for (final raw in (records['workout_routines'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        if (id == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.workoutRoutinesTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          await _db.into(_db.workoutRoutinesTable).insertOnConflictUpdate(
                WorkoutRoutinesTableCompanion(
                  id: Value(id),
                  name: Value((raw['name'] as String?) ?? 'Giáo án cá nhân'),
                  splitType: Value((raw['split_type'] as String?) ?? 'CUSTOM'),
                  scheduledWeekdaysJson: Value(
                    jsonEncode(raw['scheduled_weekdays'] ?? const <dynamic>[]),
                  ),
                  exercisesJson: Value(
                    jsonEncode(raw['exercises'] ?? const <dynamic>[]),
                  ),
                  isTemplate: Value((raw['is_template'] as bool?) ?? false),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                  deletedAt: Value(
                    raw['deleted_at'] != null
                        ? _parseUtc(raw['deleted_at'])
                        : null,
                  ),
                ),
              );
          appliedCount++;
        }
      }

      // 6. Workout Sessions (LWW)
      for (final raw in (records['workout_sessions'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        if (id == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.workoutSessionsTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          await _db.into(_db.workoutSessionsTable).insertOnConflictUpdate(
                WorkoutSessionsTableCompanion(
                  id: Value(id),
                  routineId: Value(raw['routine_id']?.toString()),
                  sessionTitle:
                      Value((raw['session_title'] as String?) ?? 'Buổi tập Gym'),
                  startedAt: Value(_parseUtc(raw['started_at'])),
                  completedAt: Value(
                    raw['completed_at'] != null
                        ? _parseUtc(raw['completed_at'])
                        : null,
                  ),
                  durationSeconds:
                      Value((raw['duration_seconds'] as num?)?.toInt() ?? 0),
                  totalVolumeKg:
                      Value((raw['total_volume_kg'] as num?)?.toDouble() ?? 0.0),
                  status: Value((raw['status'] as String?) ?? 'COMPLETED'),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                  deletedAt: Value(
                    raw['deleted_at'] != null
                        ? _parseUtc(raw['deleted_at'])
                        : null,
                  ),
                ),
              );
          appliedCount++;
        }
      }

      // 7. Workout Sets (LWW)
      for (final raw in (records['workout_sets'] as List?) ?? const []) {
        if (raw is! Map<String, dynamic>) continue;
        final id = raw['id']?.toString();
        final sessionId = raw['session_id']?.toString();
        final exerciseId =
            raw['exercise_id']?.toString() ?? raw['exercise_code']?.toString();
        if (id == null || sessionId == null || exerciseId == null) continue;
        final serverUpdated = _parseUtc(raw['updated_at']);
        final existing = await (_db.select(_db.workoutSetsTable)
              ..where((t) => t.id.equals(id)))
            .getSingleOrNull();
        if (existing == null ||
            SyncConflictResolver.shouldServerWin(
              localUpdatedAt: existing.updatedAt,
              serverUpdatedAt: serverUpdated,
            )) {
          await _db.into(_db.workoutSetsTable).insertOnConflictUpdate(
                WorkoutSetsTableCompanion(
                  id: Value(id),
                  sessionId: Value(sessionId),
                  exerciseId: Value(exerciseId),
                  setNumber: Value((raw['set_number'] as num?)?.toInt() ?? 1),
                  setType: Value((raw['set_type'] as String?) ?? 'NORMAL'),
                  weightKg: Value((raw['weight_kg'] as num?)?.toDouble() ?? 0.0),
                  reps: Value((raw['reps'] as num?)?.toInt() ?? 0),
                  rpe: Value((raw['rpe'] as num?)?.toDouble()),
                  estimated1rm:
                      Value((raw['estimated_1rm'] as num?)?.toDouble() ?? 0.0),
                  isPr: Value((raw['is_pr'] as bool?) ?? false),
                  completedAt: Value(_parseUtc(raw['completed_at'])),
                  syncStatus: const Value('SYNCED'),
                  updatedAt: Value(serverUpdated),
                ),
              );
          appliedCount++;
        }
      }
    });

    final serverTime = data['server_time_utc']?.toString();
    if (serverTime != null && serverTime.isNotEmpty) {
      await _storage.write(key: StorageKeys.lastSyncUtc, value: serverTime);
    }

    return appliedCount;
  }

  Future<SyncReport> syncNow() async {
    final online = await isOnline();
    final nowUtc = DateTime.now().toUtc();
    if (!online) {
      final pending = await countPendingChanges();
      return SyncReport(
        skippedOffline: true,
        remainingPendingCount: pending,
        syncedAtUtc: nowUtc,
      );
    }
    try {
      final pushed = await pushPendingChanges();
      final pulled = await pullServerUpdates();
      final remaining = await countPendingChanges();
      return SyncReport(
        pushedCount: pushed,
        pulledCount: pulled,
        remainingPendingCount: remaining,
        syncedAtUtc: DateTime.now().toUtc(),
      );
    } catch (e) {
      final pending = await countPendingChanges();
      return SyncReport(
        remainingPendingCount: pending,
        syncedAtUtc: nowUtc,
        errorMessage: 'Đồng bộ thất bại: $e',
      );
    }
  }

  StreamSubscription<List<ConnectivityResult>> watchConnectivityAndAutoSync(
    void Function(SyncReport report)? onSynced,
  ) {
    return _connectivity.onConnectivityChanged.listen((results) async {
      final hasNet = results.any((r) => r != ConnectivityResult.none);
      if (!hasNet) return;
      final pending = await countPendingChanges();
      if (pending == 0) return;
      final report = await syncNow();
      onSynced?.call(report);
    });
  }

  static List<String> _stringList(dynamic raw) {
    if (raw is! List) return const [];
    return raw.map((e) => e.toString()).toList();
  }

  static Map<String, dynamic> _decodeMapSafe(String raw) {
    try {
      final decoded = jsonDecode(raw);
      if (decoded is Map<String, dynamic>) return decoded;
    } catch (_) {}
    return const <String, dynamic>{};
  }

  static List<dynamic> _decodeListSafe(String raw) {
    try {
      final decoded = jsonDecode(raw);
      if (decoded is List) return decoded;
    } catch (_) {}
    return const <dynamic>[];
  }

  static DateTime _parseUtc(dynamic raw) {
    if (raw == null) return DateTime.now().toUtc();
    return DateTime.parse(raw.toString()).toUtc();
  }

  static String _formatDateIso(DateTime dt) {
    final m = dt.month.toString().padLeft(2, '0');
    final d = dt.day.toString().padLeft(2, '0');
    return '${dt.year}-$m-$d';
  }
}

class SyncQueueController extends StateNotifier<SyncQueueState> {
  final SyncQueueManager _manager;
  StreamSubscription<List<ConnectivityResult>>? _connectivitySub;

  SyncQueueController(this._manager) : super(const SyncQueueState()) {
    refreshPendingCount();
    _connectivitySub = _manager.watchConnectivityAndAutoSync((report) {
      state = state.copyWith(
        isSyncing: false,
        pendingCount: report.remainingPendingCount,
        lastSyncedAtUtc: report.isSuccess ? report.syncedAtUtc : state.lastSyncedAtUtc,
        lastError: report.errorMessage,
        clearError: report.isSuccess,
      );
    });
  }

  Future<void> refreshPendingCount() async {
    final count = await _manager.countPendingChanges();
    state = state.copyWith(pendingCount: count);
  }

  Future<SyncReport> syncNow() async {
    if (state.isSyncing) {
      return SyncReport(
        skippedOffline: false,
        remainingPendingCount: state.pendingCount,
        syncedAtUtc: DateTime.now().toUtc(),
      );
    }
    state = state.copyWith(isSyncing: true, clearError: true);
    final report = await _manager.syncNow();
    state = state.copyWith(
      isSyncing: false,
      pendingCount: report.remainingPendingCount,
      lastSyncedAtUtc: report.isSuccess ? report.syncedAtUtc : state.lastSyncedAtUtc,
      lastError: report.errorMessage,
      clearError: report.isSuccess,
    );
    return report;
  }

  @override
  void dispose() {
    _connectivitySub?.cancel();
    super.dispose();
  }
}

final syncQueueManagerProvider = Provider<SyncQueueManager>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final dio = ref.watch(dioProvider);
  final storage = ref.watch(secureStorageProvider);
  return SyncQueueManager(db, dio, storage);
});

final syncQueueControllerProvider =
    StateNotifierProvider<SyncQueueController, SyncQueueState>((ref) {
  final mgr = ref.watch(syncQueueManagerProvider);
  return SyncQueueController(mgr);
});
