// [OWNER: M2] Offline-First Workout Repository (Routines, Crash-Safe Logger, PR, Swapper, Smart Hydration Hook) (T-M2-09)
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';

import '../../../core/database/app_database.dart';
import '../../../core/database/health_tables.drift.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../domain/workout_calculators.dart';

class ActiveWorkoutSnapshot {
  final WorkoutSessionModel session;
  final List<WorkoutSetModel> sets;

  const ActiveWorkoutSnapshot({
    required this.session,
    required this.sets,
  });
}

class CompletedWorkoutSummary {
  final WorkoutSessionModel session;
  final int totalSets;
  final int workingSets;
  final int newPrCount;
  final int hydrationBonusMl;
  final bool syncedToServer;

  const CompletedWorkoutSummary({
    required this.session,
    required this.totalSets,
    required this.workingSets,
    required this.newPrCount,
    required this.hydrationBonusMl,
    required this.syncedToServer,
  });
}

class AlternativeExerciseCandidate {
  final ExerciseModel exercise;
  final double overlapRatio;
  final bool differentEquipment;

  const AlternativeExerciseCandidate({
    required this.exercise,
    required this.overlapRatio,
    required this.differentEquipment,
  });
}

class WorkoutRepository {
  final AppDatabase _db;
  final Dio _dio;
  final ExerciseRepository _exerciseRepo;
  final Uuid _uuid = const Uuid();

  WorkoutRepository(this._db, this._dio, this._exerciseRepo);

  static String localDateIso([DateTime? now]) {
    final dt = (now ?? DateTime.now()).toLocal();
    final m = dt.month.toString().padLeft(2, '0');
    final d = dt.day.toString().padLeft(2, '0');
    return '${dt.year}-$m-$d';
  }

  static List<WorkoutRoutineModel> _defaultTemplateRoutines() {
    final now = DateTime.now().toUtc();
    return [
      WorkoutRoutineModel(
        id: 'tpl-ppl-push-chest',
        name: 'PPL — Ngày Đẩy (Ngực 3D, Vai, Tay sau)',
        splitType: 'PUSH_PULL_LEGS',
        scheduledWeekdays: const [1, 4],
        isTemplate: true,
        syncStatus: 'SYNCED',
        updatedAt: now,
        exercises: const [
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENCH_PRESS',
            orderIndex: 0,
            targetSets: 4,
            targetRepMin: 6,
            targetRepMax: 8,
            defaultRestSeconds: 150,
          ),
          RoutineExerciseItem(
            exerciseCode: 'INCLINE_DUMBBELL_PRESS',
            orderIndex: 1,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds: 120,
          ),
          RoutineExerciseItem(
            exerciseCode: 'CABLE_CHEST_FLY',
            orderIndex: 2,
            targetSets: 3,
            targetRepMin: 12,
            targetRepMax: 15,
            defaultRestSeconds: 90,
          ),
          RoutineExerciseItem(
            exerciseCode: 'DUMBBELL_SHOULDER_PRESS',
            orderIndex: 3,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds: 120,
          ),
          RoutineExerciseItem(
            exerciseCode: 'CABLE_TRICEP_PUSHDOWN',
            orderIndex: 4,
            targetSets: 3,
            targetRepMin: 10,
            targetRepMax: 14,
            defaultRestSeconds: 75,
          ),
        ],
      ),
      WorkoutRoutineModel(
        id: 'tpl-upper-lower-upper',
        name: 'Upper-Lower — Thân trên Sức mạnh',
        splitType: 'UPPER_LOWER',
        scheduledWeekdays: const [1, 4],
        isTemplate: true,
        syncStatus: 'SYNCED',
        updatedAt: now,
        exercises: const [
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENCH_PRESS',
            orderIndex: 0,
            targetSets: 4,
            targetRepMin: 5,
            targetRepMax: 8,
            defaultRestSeconds: 150,
          ),
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENT_OVER_ROW',
            orderIndex: 1,
            targetSets: 4,
            targetRepMin: 6,
            targetRepMax: 10,
            defaultRestSeconds: 150,
          ),
          RoutineExerciseItem(
            exerciseCode: 'INCLINE_DUMBBELL_PRESS',
            orderIndex: 2,
            supersetGroupId: 1,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds: 90,
          ),
          RoutineExerciseItem(
            exerciseCode: 'LAT_PULLDOWN',
            orderIndex: 3,
            supersetGroupId: 1,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds: 90,
          ),
        ],
      ),
      WorkoutRoutineModel(
        id: 'tpl-full-body-foundation',
        name: 'Full Body — Nền tảng 3 Buổi/Tuần',
        splitType: 'FULL_BODY',
        scheduledWeekdays: const [1, 3, 5],
        isTemplate: true,
        syncStatus: 'SYNCED',
        updatedAt: now,
        exercises: const [
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_SQUAT',
            orderIndex: 0,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 10,
            defaultRestSeconds: 150,
          ),
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENCH_PRESS',
            orderIndex: 1,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 10,
            defaultRestSeconds: 120,
          ),
          RoutineExerciseItem(
            exerciseCode: 'LAT_PULLDOWN',
            orderIndex: 2,
            targetSets: 3,
            targetRepMin: 10,
            targetRepMax: 12,
            defaultRestSeconds: 90,
          ),
          RoutineExerciseItem(
            exerciseCode: 'PLANK',
            orderIndex: 3,
            targetSets: 3,
            targetRepMin: 45,
            targetRepMax: 60,
            defaultRestSeconds: 60,
          ),
        ],
      ),
      WorkoutRoutineModel(
        id: 'tpl-bro-split-chest',
        name: 'Bro Split — Ngày Ngực Chuyên sâu (3D)',
        splitType: 'BRO_SPLIT',
        scheduledWeekdays: const [1],
        isTemplate: true,
        syncStatus: 'SYNCED',
        updatedAt: now,
        exercises: const [
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENCH_PRESS',
            orderIndex: 0,
            targetSets: 4,
            targetRepMin: 6,
            targetRepMax: 8,
            defaultRestSeconds: 150,
          ),
          RoutineExerciseItem(
            exerciseCode: 'INCLINE_DUMBBELL_PRESS',
            orderIndex: 1,
            targetSets: 4,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds: 120,
          ),
          RoutineExerciseItem(
            exerciseCode: 'CABLE_CHEST_FLY',
            orderIndex: 2,
            targetSets: 3,
            targetRepMin: 12,
            targetRepMax: 15,
            defaultRestSeconds: 75,
          ),
        ],
      ),
    ];
  }

  Future<List<WorkoutRoutineModel>> loadRoutines() async {
    var rows = await (_db.select(_db.workoutRoutinesTable)
          ..where((t) => t.deletedAt.isNull())
          ..orderBy([
            (t) => OrderingTerm.desc(t.isTemplate),
            (t) => OrderingTerm.desc(t.updatedAt),
          ]))
        .get();

    if (rows.isEmpty) {
      await _seedDefaultTemplates();
      rows = await (_db.select(_db.workoutRoutinesTable)
            ..where((t) => t.deletedAt.isNull())
            ..orderBy([
              (t) => OrderingTerm.desc(t.isTemplate),
              (t) => OrderingTerm.desc(t.updatedAt),
            ]))
          .get();
    }

    if (!ApiEndpoints.useMockApi) {
      try {
        final res = await _dio.get<Map<String, dynamic>>(ApiEndpoints.routines);
        final items = (res.data?['items'] as List?) ?? const [];
        for (final raw in items) {
          final model =
              WorkoutRoutineModel.fromJson(raw as Map<String, dynamic>);
          await _upsertRoutineRow(model);
        }
        rows = await (_db.select(_db.workoutRoutinesTable)
              ..where((t) => t.deletedAt.isNull())
              ..orderBy([
                (t) => OrderingTerm.desc(t.isTemplate),
                (t) => OrderingTerm.desc(t.updatedAt),
              ]))
            .get();
      } catch (_) {
        // Offline-first fallback: keep SQLite routines
      }
    }

    return rows.map(_routineRowToModel).toList();
  }

  Future<void> _seedDefaultTemplates() async {
    for (final tpl in _defaultTemplateRoutines()) {
      await _upsertRoutineRow(tpl);
    }
  }

  Future<void> _upsertRoutineRow(WorkoutRoutineModel r) async {
    await _db.into(_db.workoutRoutinesTable).insertOnConflictUpdate(
          WorkoutRoutinesTableCompanion.insert(
            id: r.id,
            name: r.name,
            splitType: r.splitType,
            scheduledWeekdaysJson: Value(jsonEncode(r.scheduledWeekdays)),
            exercisesJson:
                Value(jsonEncode(r.exercises.map((e) => e.toJson()).toList())),
            isTemplate: Value(r.isTemplate),
            syncStatus: Value(r.syncStatus),
            updatedAt: r.updatedAt,
            deletedAt: Value(r.deletedAt),
          ),
        );
  }

  WorkoutRoutineModel _routineRowToModel(WorkoutRoutinesTableData row) {
    final weekdays = (jsonDecode(row.scheduledWeekdaysJson) as List)
        .map((e) => (e as num).toInt())
        .toList();
    final exItems = (jsonDecode(row.exercisesJson) as List)
        .map((e) => RoutineExerciseItem.fromJson(e as Map<String, dynamic>))
        .toList()
      ..sort((a, b) => a.orderIndex.compareTo(b.orderIndex));

    return WorkoutRoutineModel(
      id: row.id,
      name: row.name,
      splitType: row.splitType,
      scheduledWeekdays: weekdays,
      exercises: exItems,
      isTemplate: row.isTemplate,
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    );
  }

  Future<WorkoutRoutineModel> saveRoutine(WorkoutRoutineModel routine) async {
    final now = DateTime.now().toUtc();
    final isNew = routine.id.isEmpty;
    final saved = WorkoutRoutineModel(
      id: isNew ? _uuid.v4() : routine.id,
      name: routine.name.trim(),
      splitType: routine.splitType,
      scheduledWeekdays: routine.scheduledWeekdays,
      exercises: routine.exercises,
      isTemplate: false,
      syncStatus: isNew ? 'PENDING_CREATE' : 'PENDING_UPDATE',
      updatedAt: now,
    );
    await _upsertRoutineRow(saved);
    return saved;
  }

  Future<WorkoutRoutineModel> duplicateTemplate(
    WorkoutRoutineModel source,
  ) async {
    return saveRoutine(
      WorkoutRoutineModel(
        id: '',
        name: '${source.name} (Bản sao)',
        splitType: source.splitType,
        scheduledWeekdays: source.scheduledWeekdays,
        exercises: source.exercises,
        isTemplate: false,
        updatedAt: DateTime.now().toUtc(),
      ),
    );
  }

  /// Thay the cac giao an AI tu dong tao truoc do bang phac do moi (giu nguyen giao an tu tao & mau chuan).
  Future<List<WorkoutRoutineModel>> applyGeneratedPlan(
    List<WorkoutRoutineModel> generated,
  ) async {
    final now = DateTime.now().toUtc();
    final existingRows = await (_db.select(_db.workoutRoutinesTable)
          ..where((t) => t.isTemplate.equals(false)))
        .get();
    final staleAiIds = existingRows
        .where((r) => r.id.startsWith('ai-plan-'))
        .map((r) => r.id)
        .toList();
    if (staleAiIds.isNotEmpty) {
      await (_db.update(_db.workoutRoutinesTable)
            ..where((t) => t.id.isIn(staleAiIds)))
          .write(
        WorkoutRoutinesTableCompanion(
          deletedAt: Value(now),
          updatedAt: Value(now),
          syncStatus: const Value('PENDING_DELETE'),
        ),
      );
    }

    for (final routine in generated) {
      await _upsertRoutineRow(routine);
    }
    return generated;
  }

  static WorkoutRoutineModel? pickTodayRoutine(
    List<WorkoutRoutineModel> routines, {
    int? weekday,
  }) {
    if (routines.isEmpty) return null;
    final targetDay = weekday ?? DateTime.now().weekday;
    for (final r in routines) {
      if (!r.isTemplate && r.scheduledWeekdays.contains(targetDay)) return r;
    }
    for (final r in routines) {
      if (r.scheduledWeekdays.contains(targetDay)) return r;
    }
    for (final r in routines) {
      if (!r.isTemplate) return r;
    }
    return routines.first;
  }

  Future<void> softDeleteRoutine(String routineId) async {
    final existing = await (_db.select(_db.workoutRoutinesTable)
          ..where((t) => t.id.equals(routineId)))
        .getSingleOrNull();
    if (existing == null || existing.isTemplate) return;
    final now = DateTime.now().toUtc();
    await (_db.update(_db.workoutRoutinesTable)
          ..where((t) => t.id.equals(routineId)))
        .write(
      WorkoutRoutinesTableCompanion(
        deletedAt: Value(now),
        updatedAt: Value(now),
        syncStatus: const Value('PENDING_DELETE'),
      ),
    );
  }

  Future<WorkoutRoutineModel?> getRoutineById(String routineId) async {
    final row = await (_db.select(_db.workoutRoutinesTable)
          ..where((t) => t.id.equals(routineId) & t.deletedAt.isNull()))
        .getSingleOrNull();
    return row == null ? null : _routineRowToModel(row);
  }

  /// Tim phien dang tap do (`IN_PROGRESS`) de khoi phuc neu app bi tat dot ngot (F15).
  Future<ActiveWorkoutSnapshot?> getActiveInProgressSession() async {
    final row = await (_db.select(_db.workoutSessionsTable)
          ..where((t) => t.status.equals('IN_PROGRESS') & t.deletedAt.isNull())
          ..orderBy([(t) => OrderingTerm.desc(t.startedAt)])
          ..limit(1))
        .getSingleOrNull();
    if (row == null) return null;

    final setRows = await (_db.select(_db.workoutSetsTable)
          ..where((t) => t.sessionId.equals(row.id))
          ..orderBy([(t) => OrderingTerm.asc(t.setNumber)]))
        .get();

    return ActiveWorkoutSnapshot(
      session: _sessionRowToModel(row),
      sets: setRows.map(_setRowToModel).toList(),
    );
  }

  Future<WorkoutSessionModel> startNewSession({
    required String title,
    String? routineId,
  }) async {
    final now = DateTime.now().toUtc();
    final session = WorkoutSessionModel(
      id: _uuid.v4(),
      routineId: routineId,
      sessionTitle: title,
      startedAt: now,
      status: 'IN_PROGRESS',
      syncStatus: 'PENDING_CREATE',
      updatedAt: now,
    );
    await _upsertSessionRow(session);
    return session;
  }

  Future<WorkoutSetModel> saveSetImmediately({
    required String sessionId,
    required String exerciseIdOrCode,
    required int setNumber,
    required String setType,
    required double weightKg,
    required int reps,
    double? rpe,
    String? existingSetId,
  }) async {
    final now = DateTime.now().toUtc();
    final setId = existingSetId ?? _uuid.v4();
    final est1rm = WorkoutCalculators.calculateEstimated1Rm(weightKg, reps);

    final prevBest = await getHistoricalBest1Rm(
      exerciseIdOrCode,
      excludeSetId: setId,
    );
    final isPr = setType.toUpperCase() != 'WARMUP' &&
        est1rm > 0 &&
        est1rm > prevBest;

    final model = WorkoutSetModel(
      id: setId,
      sessionId: sessionId,
      exerciseId: exerciseIdOrCode,
      setNumber: setNumber,
      setType: setType.toUpperCase(),
      weightKg: weightKg,
      reps: reps,
      rpe: rpe,
      estimated1rm: est1rm,
      isPr: isPr,
      completedAt: now,
      syncStatus: existingSetId == null ? 'PENDING_CREATE' : 'PENDING_UPDATE',
      updatedAt: now,
    );

    await _db.into(_db.workoutSetsTable).insertOnConflictUpdate(
          WorkoutSetsTableCompanion.insert(
            id: model.id,
            sessionId: model.sessionId,
            exerciseId: model.exerciseId,
            setNumber: model.setNumber,
            setType: Value(model.setType),
            weightKg: model.weightKg,
            reps: model.reps,
            rpe: Value(model.rpe),
            estimated1rm: Value(model.estimated1rm),
            isPr: Value(model.isPr),
            completedAt: model.completedAt,
            syncStatus: Value(model.syncStatus),
            updatedAt: model.updatedAt,
          ),
        );

    await _recomputeSessionVolume(sessionId);
    return model;
  }

  Future<void> deleteSet(String setId, String sessionId) async {
    await (_db.delete(_db.workoutSetsTable)..where((t) => t.id.equals(setId)))
        .go();
    await _recomputeSessionVolume(sessionId);
  }

  Future<void> replaceExerciseInActiveSets({
    required String sessionId,
    required String oldExerciseCode,
    required String newExerciseCode,
  }) async {
    // Theo tieu chi F25: Giu nguyen cac hiep da ghi truoc do; chi doi cac hiep chua ghi/moi.
    // Ham nay khong xoa hiep cu ma tra ve control sach cho UI doi card ke tiep.
    final _ = (sessionId, oldExerciseCode, newExerciseCode);
  }

  Future<void> abandonActiveSession(String sessionId) async {
    final now = DateTime.now().toUtc();
    await (_db.update(_db.workoutSessionsTable)
          ..where((t) => t.id.equals(sessionId)))
        .write(
      WorkoutSessionsTableCompanion(
        status: const Value('ABANDONED'),
        completedAt: Value(now),
        updatedAt: Value(now),
        syncStatus: const Value('PENDING_UPDATE'),
      ),
    );
  }

  Future<CompletedWorkoutSummary> completeSession({
    required WorkoutSessionModel session,
    required List<WorkoutSetModel> sets,
    required int durationSeconds,
  }) async {
    final now = DateTime.now().toUtc();
    final volume = WorkoutCalculators.calculateSessionVolumeKg(sets);
    final workingSets =
        sets.where((s) => s.setType.toUpperCase() != 'WARMUP').toList();
    final bonusMl = WorkoutCalculators.calculateWorkoutHydrationBonusMl(
      durationSeconds: durationSeconds,
      sets: sets,
    );

    var completed = WorkoutSessionModel(
      id: session.id,
      routineId: session.routineId,
      sessionTitle: session.sessionTitle,
      startedAt: session.startedAt,
      completedAt: now,
      durationSeconds: durationSeconds,
      totalVolumeKg: volume,
      status: 'COMPLETED',
      syncStatus: 'PENDING_CREATE',
      updatedAt: now,
    );

    await _upsertSessionRow(completed);
    await _applyHydrationWorkoutBonus(bonusMl);

    var synced = false;
    if (!ApiEndpoints.useMockApi) {
      try {
        final payload = {
          'id': completed.id,
          if (completed.routineId != null &&
              !completed.routineId!.startsWith('tpl-'))
            'routine_id': completed.routineId,
          'session_title': completed.sessionTitle,
          'started_at': completed.startedAt.toUtc().toIso8601String(),
          'completed_at': now.toIso8601String(),
          'duration_seconds': durationSeconds,
          'status': 'COMPLETED',
          'updated_at': now.toIso8601String(),
          'sets': sets
              .map(
                (s) => {
                  'id': s.id,
                  'exercise_code': s.exerciseId.toUpperCase(),
                  'set_number': s.setNumber,
                  'set_type': s.setType,
                  'weight_kg': s.weightKg,
                  'reps': s.reps,
                  if (s.rpe != null) 'rpe': s.rpe,
                  'completed_at': s.completedAt.toUtc().toIso8601String(),
                  'updated_at': s.updatedAt.toUtc().toIso8601String(),
                },
              )
              .toList(),
        };
        await _dio.post<Map<String, dynamic>>(
          ApiEndpoints.workoutSessions,
          data: payload,
        );
        synced = true;
        completed = WorkoutSessionModel(
          id: completed.id,
          routineId: completed.routineId,
          sessionTitle: completed.sessionTitle,
          startedAt: completed.startedAt,
          completedAt: completed.completedAt,
          durationSeconds: completed.durationSeconds,
          totalVolumeKg: completed.totalVolumeKg,
          status: completed.status,
          syncStatus: 'SYNCED',
          updatedAt: completed.updatedAt,
        );
        await _upsertSessionRow(completed);

        final syncedSetIds =
            sets.map((s) => s.id).where((id) => id.isNotEmpty).toList();
        if (syncedSetIds.isNotEmpty) {
          await (_db.update(_db.workoutSetsTable)
                ..where((t) =>
                    t.sessionId.equals(completed.id) &
                    t.id.isIn(syncedSetIds)))
              .write(
            WorkoutSetsTableCompanion(
              syncStatus: const Value('SYNCED'),
              updatedAt: Value(now),
            ),
          );
        }
      } catch (_) {
        synced = false;
      }
    }

    return CompletedWorkoutSummary(
      session: completed,
      totalSets: sets.length,
      workingSets: workingSets.length,
      newPrCount: workingSets.where((s) => s.isPr).length,
      hydrationBonusMl: bonusMl,
      syncedToServer: synced,
    );
  }

  Future<void> _applyHydrationWorkoutBonus(int bonusMl) async {
    final nowUtc = DateTime.now().toUtc();
    final todayIso = localDateIso();
    final dailyRows = await (_db.select(_db.dailyHealthLogsTable)
          ..where((t) => t.logDateIso.equals(todayIso))
          ..orderBy([(t) => OrderingTerm.desc(t.updatedAt)]))
        .get();
    final row = dailyRows.isNotEmpty ? dailyRows.first : null;
    if (dailyRows.length > 1) {
      final redundantIds = dailyRows.skip(1).map((r) => r.id).toList();
      await (_db.delete(_db.dailyHealthLogsTable)
            ..where((t) => t.id.isIn(redundantIds)))
          .go();
    }
    final latestBio = await (_db.select(_db.biometricLogsTable)
          ..where((t) => t.deletedAt.isNull())
          ..orderBy([
            (t) => OrderingTerm.desc(t.loggedDate),
            (t) => OrderingTerm.desc(t.updatedAt),
          ])
          ..limit(1))
        .getSingleOrNull();
    final baseTarget =
        DailyHealthModel.calculateTargetWaterMl(latestBio?.weightKg ?? 70.0);
    final desiredTarget = baseTarget + bonusMl;

    if (row == null) {
      await _db.into(_db.dailyHealthLogsTable).insertOnConflictUpdate(
            DailyHealthLogsTableCompanion.insert(
              id: 'daily-$todayIso',
              logDateIso: todayIso,
              targetWaterMl: Value(desiredTarget),
              syncStatus: const Value('PENDING_CREATE'),
              updatedAt: nowUtc,
            ),
          );
    } else if (row.targetWaterMl < desiredTarget) {
      await (_db.update(_db.dailyHealthLogsTable)
            ..where((t) => t.id.equals(row.id)))
          .write(
        DailyHealthLogsTableCompanion(
          targetWaterMl: Value(desiredTarget),
          syncStatus: const Value('PENDING_UPDATE'),
          updatedAt: Value(nowUtc),
        ),
      );
    }
  }

  Future<List<String>> _loadValidSessionIds() async {
    final rows = await (_db.select(_db.workoutSessionsTable)
          ..where((t) =>
              t.deletedAt.isNull() &
              t.status.isNotIn(const ['ABANDONED', 'CANCELLED'])))
        .get();
    return rows.map((r) => r.id).toList();
  }

  Future<double> getHistoricalBest1Rm(
    String exerciseIdOrCode, {
    String? excludeSetId,
  }) async {
    final validSessionIds = await _loadValidSessionIds();
    if (validSessionIds.isEmpty) return 0.0;

    final normalized = exerciseIdOrCode.toUpperCase();
    final rows = await (_db.select(_db.workoutSetsTable)
          ..where((t) =>
              t.sessionId.isIn(validSessionIds) &
              t.exerciseId.equals(normalized) &
              t.setType.isNotIn(const ['WARMUP'])))
        .get();
    var best = 0.0;
    for (final row in rows) {
      if (excludeSetId != null && row.id == excludeSetId) continue;
      if (row.estimated1rm > best) best = row.estimated1rm;
    }
    return best;
  }

  /// Pre-fill muc ta & so rep cua buoi tap gan nhat (F15).
  Future<({double weightKg, int reps, double? rpe})?>
      getLastPerformanceForExercise(String exerciseCode) async {
    final validSessionIds = await _loadValidSessionIds();
    if (validSessionIds.isEmpty) return null;

    final normalized = exerciseCode.toUpperCase();
    final rows = await (_db.select(_db.workoutSetsTable)
          ..where((t) =>
              t.sessionId.isIn(validSessionIds) &
              t.exerciseId.equals(normalized) &
              t.setType.isNotIn(const ['WARMUP']))
          ..orderBy([(t) => OrderingTerm.desc(t.completedAt)])
          ..limit(1))
        .get();
    if (rows.isEmpty) return null;
    final latest = rows.first;
    return (weightKg: latest.weightKg, reps: latest.reps, rpe: latest.rpe);
  }

  /// Goi y top 5 bai tap thay the cung nhom co chinh (>=80% trung khop, uu tien khac dung cu) (F25).
  Future<List<AlternativeExerciseCandidate>> findAlternativeExercises(
    ExerciseModel current,
  ) async {
    final all = await _exerciseRepo.loadExercises();
    final targetPrimary = current.primaryMuscles.toSet();
    final targetSecondary = current.secondaryMuscles.toSet();
    final candidates = <AlternativeExerciseCandidate>[];

    for (final cand in all) {
      if (cand.code.toUpperCase() == current.code.toUpperCase()) continue;
      final candPrimary = cand.primaryMuscles.toSet();
      final shared = targetPrimary.intersection(candPrimary);
      if (shared.isEmpty) continue;
      final denom = targetPrimary.length < candPrimary.length
          ? targetPrimary.length
          : candPrimary.length;
      final ratio = shared.length / (denom > 0 ? denom : 1);
      if (ratio < 0.8) continue;

      candidates.add(
        AlternativeExerciseCandidate(
          exercise: cand,
          overlapRatio: ratio,
          differentEquipment:
              cand.equipmentType.toUpperCase() !=
              current.equipmentType.toUpperCase(),
        ),
      );
    }

    candidates.sort((a, b) {
      final cmpRatio = b.overlapRatio.compareTo(a.overlapRatio);
      if (cmpRatio != 0) return cmpRatio;
      if (a.differentEquipment != b.differentEquipment) {
        return a.differentEquipment ? -1 : 1;
      }
      final aSec = targetSecondary
          .intersection(a.exercise.secondaryMuscles.toSet())
          .length;
      final bSec = targetSecondary
          .intersection(b.exercise.secondaryMuscles.toSet())
          .length;
      return bSec.compareTo(aSec);
    });

    return candidates.take(5).toList();
  }

  Future<List<WorkoutSessionModel>> loadCompletedSessions() async {
    final rows = await (_db.select(_db.workoutSessionsTable)
          ..where(
              (t) => t.status.equals('COMPLETED') & t.deletedAt.isNull())
          ..orderBy([(t) => OrderingTerm.desc(t.startedAt)]))
        .get();
    return rows.map(_sessionRowToModel).toList();
  }

  Future<List<WorkoutSetModel>> loadAllSets() async {
    final rows = await _db.select(_db.workoutSetsTable).get();
    return rows.map(_setRowToModel).toList();
  }

  Future<void> _recomputeSessionVolume(String sessionId) async {
    final setRows = await (_db.select(_db.workoutSetsTable)
          ..where((t) => t.sessionId.equals(sessionId)))
        .get();
    final volume =
        WorkoutCalculators.calculateSessionVolumeKg(setRows.map(_setRowToModel));
    await (_db.update(_db.workoutSessionsTable)
          ..where((t) => t.id.equals(sessionId)))
        .write(
      WorkoutSessionsTableCompanion(
        totalVolumeKg: Value(volume),
        updatedAt: Value(DateTime.now().toUtc()),
      ),
    );
  }

  Future<void> _upsertSessionRow(WorkoutSessionModel s) async {
    await _db.into(_db.workoutSessionsTable).insertOnConflictUpdate(
          WorkoutSessionsTableCompanion.insert(
            id: s.id,
            routineId: Value(s.routineId),
            sessionTitle: s.sessionTitle,
            startedAt: s.startedAt,
            completedAt: Value(s.completedAt),
            durationSeconds: Value(s.durationSeconds),
            totalVolumeKg: Value(s.totalVolumeKg),
            status: Value(s.status),
            syncStatus: Value(s.syncStatus),
            updatedAt: s.updatedAt,
            deletedAt: Value(s.deletedAt),
          ),
        );
  }

  WorkoutSessionModel _sessionRowToModel(WorkoutSessionsTableData row) {
    return WorkoutSessionModel(
      id: row.id,
      routineId: row.routineId,
      sessionTitle: row.sessionTitle,
      startedAt: row.startedAt,
      completedAt: row.completedAt,
      durationSeconds: row.durationSeconds,
      totalVolumeKg: row.totalVolumeKg,
      status: row.status,
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
      deletedAt: row.deletedAt,
    );
  }

  WorkoutSetModel _setRowToModel(WorkoutSetsTableData row) {
    return WorkoutSetModel(
      id: row.id,
      sessionId: row.sessionId,
      exerciseId: row.exerciseId,
      setNumber: row.setNumber,
      setType: row.setType,
      weightKg: row.weightKg,
      reps: row.reps,
      rpe: row.rpe,
      estimated1rm: row.estimated1rm,
      isPr: row.isPr,
      completedAt: row.completedAt,
      syncStatus: row.syncStatus,
      updatedAt: row.updatedAt,
    );
  }
}

final workoutRepositoryProvider = Provider<WorkoutRepository>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final dio = ref.watch(dioProvider);
  final exRepo = ref.watch(exerciseRepositoryProvider);
  return WorkoutRepository(db, dio, exRepo);
});

final workoutRoutinesProvider =
    FutureProvider<List<WorkoutRoutineModel>>((ref) async {
  return ref.watch(workoutRepositoryProvider).loadRoutines();
});
