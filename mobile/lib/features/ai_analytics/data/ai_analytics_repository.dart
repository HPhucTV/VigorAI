// [OWNER: M2] AI Readiness 3D, Banister Local Decay & Analytics Aggregation Repository (T-M2-10, T-M2-11 / F20-F25)
import 'dart:convert';
import 'dart:math' as math;

import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/database/ai_cache_tables.drift.dart';
import '../../../core/database/app_database.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import '../../workout/domain/workout_calculators.dart';

class WeeklyVolumePoint {
  final String weekLabel;
  final double totalVolumeKg;
  final int sessionsCount;

  const WeeklyVolumePoint({
    required this.weekLabel,
    required this.totalVolumeKg,
    required this.sessionsCount,
  });
}

class PersonalRecordItem {
  final String exerciseCode;
  final String exerciseNameVi;
  final double best1rmKg;
  final double bestWeightKg;
  final int bestReps;
  final DateTime achievedAt;

  const PersonalRecordItem({
    required this.exerciseCode,
    required this.exerciseNameVi,
    required this.best1rmKg,
    required this.bestWeightKg,
    required this.bestReps,
    required this.achievedAt,
  });
}

class AnalyticsSummaryModel {
  final int periodDays;
  final List<WeeklyVolumePoint> weeklyVolume;
  final Map<String, double> volumeByMuscleAxis;
  final Map<String, int> muscleRadarCounts;
  final double pullPushRatio;
  final List<PersonalRecordItem> personalRecords;
  final int streakDays;
  final double totalVolumeKg;
  final int totalWorkingSets;

  const AnalyticsSummaryModel({
    required this.periodDays,
    required this.weeklyVolume,
    required this.volumeByMuscleAxis,
    required this.muscleRadarCounts,
    required this.pullPushRatio,
    required this.personalRecords,
    required this.streakDays,
    required this.totalVolumeKg,
    required this.totalWorkingSets,
  });
}

class AiAnalyticsRepository {
  static const Map<String, String> muscleToRadarAxis = {
    MuscleMaterialIds.chest: 'chest',
    MuscleMaterialIds.backLats: 'back',
    MuscleMaterialIds.traps: 'back',
    MuscleMaterialIds.shoulders: 'shoulders',
    MuscleMaterialIds.biceps: 'arms',
    MuscleMaterialIds.triceps: 'arms',
    MuscleMaterialIds.glutes: 'legs',
    MuscleMaterialIds.quads: 'legs',
    MuscleMaterialIds.hamstrings: 'legs',
    MuscleMaterialIds.calves: 'legs',
    MuscleMaterialIds.absCore: 'core',
  };

  static const Set<String> _largeMuscles = {
    MuscleMaterialIds.chest,
    MuscleMaterialIds.backLats,
    MuscleMaterialIds.glutes,
    MuscleMaterialIds.quads,
    MuscleMaterialIds.hamstrings,
  };

  final AppDatabase _db;
  final Dio _dio;
  final ExerciseRepository _exerciseRepo;

  AiAnalyticsRepository(this._db, this._dio, this._exerciseRepo);

  /// Quy doi muc moi co [0.0..1.0] sang bang mau phuc hoi 3D chuan F23.
  static Color recoveryColorForFatigue(double fatigue) {
    final f = fatigue.clamp(0.0, 1.0);
    if (f <= 0.25) return AppColors.muscleRecoveredGreen; // #43A047
    if (f <= 0.65) return AppColors.muscleSecondaryOrange; // #FB8C00
    return AppColors.musclePrimaryRed; // #E53935
  }

  static String recoveryStatusLabel(double fatigue) {
    final f = fatigue.clamp(0.0, 1.0);
    if (f <= 0.25) return 'Sẵn sàng tập nặng (75–100% hồi phục)';
    if (f <= 0.65) return 'Đang phục hồi — chỉ nên tập nhẹ/bổ trợ';
    return 'Đang mỏi cao — khuyến nghị nghỉ ngơi / Deload';
  }

  /// Uoc tinh so gio can de dat hoi phuc hoan toan (<5% moi) theo hang so Banister (tau=48h co lon, 36h co nho).
  static int estimatedHoursToFullRecovery(String matId, double fatigue) {
    final f = fatigue.clamp(0.0, 1.0);
    if (f <= 0.05) return 0;
    final tauHours = _largeMuscles.contains(matId) ? 48.0 : 36.0;
    final hours = (-tauHours * math.log(0.05 / f)).ceil();
    return hours.clamp(1, 96);
  }

  static Map<String, Color> buildRecovery3DColorsMap(
    Map<String, double> fatigueMap,
  ) {
    final colors = <String, Color>{};
    for (final matId in MuscleMaterialIds.all) {
      final f = fatigueMap[matId] ?? 0.0;
      colors[matId] = recoveryColorForFatigue(f);
    }
    return colors;
  }

  static AiReadinessSnapshotModel newUserFallbackSnapshot() {
    final todayIso = DateTime.now().toUtc().toIso8601String().split('T').first;
    return AiReadinessSnapshotModel(
      targetDateIso: todayIso,
      modelVersion: 'banister-fallback-new-user',
      readinessScore: 85.0,
      readinessLevel: 'READY',
      insights: const [
        'Tài khoản mới chưa đủ 3 ngày dữ liệu — AI đang dùng mức khởi tạo mặc định (85 điểm).',
        'Hãy ghi nhận buổi tập đầu tiên và giấc ngủ để cá nhân hóa gợi ý tải trọng.',
      ],
      muscleFatigueMap: {
        for (final m in MuscleMaterialIds.all) m: 0.0,
      },
      weightRecommendations: const [],
      disclaimer:
          'Gợi ý tải trọng do AI phân tích chỉ phục vụ mục đích tham khảo thể hình, hãy dừng tập ngay nếu thấy đau khớp bất thường.',
    );
  }

  Future<AiReadinessSnapshotModel> fetchReadinessAndOverload({
    bool forceRefresh = false,
  }) async {
    final todayIso = DateTime.now().toUtc().toIso8601String().split('T').first;

    if (!ApiEndpoints.useMockApi) {
      try {
        final res = await _dio
            .get<Map<String, dynamic>>(ApiEndpoints.aiReadinessAndOverload);
        if (res.data != null) {
          final model = AiReadinessSnapshotModel.fromJson(res.data!);
          await _cacheReadiness(model);
          return _overlayLocal72hFatigue(model);
        }
      } catch (_) {
        // Offline or unreachable -> fallback to cache / mock
      }
    }

    if (!forceRefresh) {
      final cachedRow = await (_db.select(_db.aiReadinessCacheTable)
            ..where((t) => t.targetDateIso.equals(todayIso)))
          .getSingleOrNull();
      if (cachedRow != null) {
        final cachedModel = _cacheRowToModel(cachedRow);
        return _overlayLocal72hFatigue(cachedModel);
      }
    }

    if (ApiEndpoints.useMockApi) {
      final mockModel = await _loadReadinessMock();
      await _cacheReadiness(mockModel);
      return _overlayLocal72hFatigue(mockModel);
    }

    final baseModel = await _loadReadinessMock();
    final hasAnyLocalSession = (await (_db.select(_db.workoutSessionsTable)
              ..where((t) => t.deletedAt.isNull())
              ..limit(1))
            .get())
        .isNotEmpty;
    if (!hasAnyLocalSession) {
      return newUserFallbackSnapshot();
    }
    return _overlayLocal72hFatigue(baseModel);
  }

  Future<AiReadinessSnapshotModel> _loadReadinessMock() async {
    final raw = await rootBundle.loadString('assets/mock_json/mock_m4_ai.json');
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    final readinessMap =
        (decoded['readiness_mock'] as Map<String, dynamic>?) ?? decoded;
    return AiReadinessSnapshotModel.fromJson(readinessMap);
  }

  Future<AiReadinessSnapshotModel> _overlayLocal72hFatigue(
    AiReadinessSnapshotModel base,
  ) async {
    final now = DateTime.now().toUtc();
    final cutoff = now.subtract(const Duration(hours: 72));
    final recentSessions = await (_db.select(_db.workoutSessionsTable)
          ..where((t) =>
              t.deletedAt.isNull() &
              t.status.equals('COMPLETED') &
              t.startedAt.isBiggerOrEqualValue(cutoff)))
        .get();

    if (recentSessions.isEmpty) return base;

    final exercises = await _exerciseRepo.loadExercises();
    final exMap = <String, ExerciseModel>{};
    for (final ex in exercises) {
      exMap[ex.code.toUpperCase()] = ex;
      exMap[ex.id] = ex;
    }

    final sessionStartById = {
      for (final s in recentSessions) s.id: s.completedAt ?? s.startedAt,
    };
    final sessionIds = sessionStartById.keys.toList();
    final setRows = await (_db.select(_db.workoutSetsTable)
          ..where((t) =>
              t.sessionId.isIn(sessionIds) &
              t.setType.isNotIn(const ['WARMUP'])))
        .get();

    final localFatigue = <String, double>{
      for (final m in MuscleMaterialIds.all) m: base.muscleFatigueMap[m] ?? 0.0,
    };

    for (final wset in setRows) {
      final ex = exMap[wset.exerciseId.toUpperCase()] ?? exMap[wset.exerciseId];
      if (ex == null) continue;
      final dt = sessionStartById[wset.sessionId] ?? wset.completedAt;
      final hoursAgo = math.max(0.0, now.difference(dt).inMinutes / 60.0);
      final rpeFactor = ((wset.rpe ?? 7.5) / 10.0).clamp(0.4, 1.0);
      final baseDose = 0.10 * rpeFactor;

      void addDose(String matId, double weight) {
        final tau = _largeMuscles.contains(matId) ? 48.0 : 36.0;
        final decayed = baseDose * weight * math.exp(-hoursAgo / tau);
        localFatigue[matId] =
            ((localFatigue[matId] ?? 0.0) + decayed).clamp(0.0, 1.0);
      }

      for (final m in ex.primaryMuscles) {
        addDose(m, 1.0);
      }
      for (final m in ex.secondaryMuscles) {
        addDose(m, 0.5);
      }
    }

    return AiReadinessSnapshotModel(
      targetDateIso: base.targetDateIso,
      modelVersion: base.modelVersion,
      readinessScore: base.readinessScore,
      readinessLevel: base.readinessLevel,
      insights: base.insights,
      muscleFatigueMap: localFatigue,
      weightRecommendations: base.weightRecommendations,
      disclaimer: base.disclaimer,
    );
  }

  Future<void> _cacheReadiness(AiReadinessSnapshotModel model) async {
    await _db.into(_db.aiReadinessCacheTable).insertOnConflictUpdate(
          AiReadinessCacheTableCompanion.insert(
            targetDateIso: model.targetDateIso,
            readinessScore: model.readinessScore,
            readinessLevel: model.readinessLevel,
            muscleFatigueMapJson: jsonEncode(model.muscleFatigueMap),
            weightRecommendationsJson: jsonEncode(
              model.weightRecommendations.map((e) => e.toJson()).toList(),
            ),
            insightsJson: Value(jsonEncode(model.insights)),
            cachedAt: DateTime.now().toUtc(),
          ),
        );
  }

  AiReadinessSnapshotModel _cacheRowToModel(AiReadinessCacheTableData row) {
    final fatigueRaw =
        jsonDecode(row.muscleFatigueMapJson) as Map<String, dynamic>;
    final recsRaw = jsonDecode(row.weightRecommendationsJson) as List<dynamic>;
    final insightsRaw = jsonDecode(row.insightsJson) as List<dynamic>;
    return AiReadinessSnapshotModel(
      targetDateIso: row.targetDateIso,
      modelVersion: 'cached-offline',
      readinessScore: row.readinessScore,
      readinessLevel: row.readinessLevel,
      insights: insightsRaw.cast<String>(),
      muscleFatigueMap: fatigueRaw
          .map((k, v) => MapEntry(k, (v as num).toDouble().clamp(0.0, 1.0))),
      weightRecommendations: recsRaw
          .map((e) => WeightRecommendationModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      disclaimer:
          'Gợi ý tải trọng do AI phân tích chỉ phục vụ mục đích tham khảo thể hình, hãy dừng tập ngay nếu thấy đau khớp bất thường.',
    );
  }

  Future<AnalyticsSummaryModel> loadAnalyticsSummary({
    int periodDays = 90,
  }) async {
    final exercises = await _exerciseRepo.loadExercises();
    final exMap = <String, ExerciseModel>{};
    for (final ex in exercises) {
      exMap[ex.code.toUpperCase()] = ex;
      exMap[ex.id] = ex;
    }

    final sessionRows = await (_db.select(_db.workoutSessionsTable)
          ..where((t) =>
              t.deletedAt.isNull() & t.status.equals('COMPLETED'))
          ..orderBy([(t) => OrderingTerm.asc(t.startedAt)]))
        .get();

    final setRows = await _db.select(_db.workoutSetsTable).get();

    final sessions = sessionRows
        .map(
          (r) => WorkoutSessionModel(
            id: r.id,
            routineId: r.routineId,
            sessionTitle: r.sessionTitle,
            startedAt: r.startedAt,
            completedAt: r.completedAt,
            durationSeconds: r.durationSeconds,
            totalVolumeKg: r.totalVolumeKg,
            status: r.status,
            syncStatus: r.syncStatus,
            updatedAt: r.updatedAt,
            deletedAt: r.deletedAt,
          ),
        )
        .toList();

    final sets = setRows
        .map(
          (r) => WorkoutSetModel(
            id: r.id,
            sessionId: r.sessionId,
            exerciseId: r.exerciseId,
            setNumber: r.setNumber,
            setType: r.setType,
            weightKg: r.weightKg,
            reps: r.reps,
            rpe: r.rpe,
            estimated1rm: r.estimated1rm,
            isPr: r.isPr,
            completedAt: r.completedAt,
            syncStatus: r.syncStatus,
            updatedAt: r.updatedAt,
          ),
        )
        .toList();

    return aggregateAnalyticsFromData(
      sessions: sessions,
      sets: sets,
      exerciseByIdOrCode: exMap,
      periodDays: periodDays,
    );
  }

  /// Tong hop thuan Dart duoc toi uu < 300ms cho >= 1.000 hiep tap (F22, F24, F25).
  static AnalyticsSummaryModel aggregateAnalyticsFromData({
    required List<WorkoutSessionModel> sessions,
    required List<WorkoutSetModel> sets,
    required Map<String, ExerciseModel> exerciseByIdOrCode,
    int periodDays = 90,
    DateTime? now,
  }) {
    final currentUtc = (now ?? DateTime.now().toUtc()).toUtc();
    final cutoff = currentUtc.subtract(Duration(days: periodDays));
    final radarCutoff = currentUtc.subtract(const Duration(days: 30));

    final filteredSessions = sessions
        .where((s) => s.deletedAt == null && !s.startedAt.isBefore(cutoff))
        .toList()
      ..sort((a, b) => a.startedAt.compareTo(b.startedAt));

    final sessionStartById = <String, DateTime>{
      for (final s in filteredSessions) s.id: s.startedAt,
    };

    final weeklyMap = <String, ({double vol, int count, DateTime sortDate})>{};
    var totalVolume = 0.0;

    for (final s in filteredSessions) {
      final d = s.startedAt.toUtc();
      final monday = DateTime.utc(d.year, d.month, d.day - (d.weekday - 1));
      final label = '${monday.day}/${monday.month}';
      final prev = weeklyMap[label];
      weeklyMap[label] = (
        vol: (prev?.vol ?? 0.0) + s.totalVolumeKg,
        count: (prev?.count ?? 0) + 1,
        sortDate: prev?.sortDate ?? monday,
      );
      totalVolume += s.totalVolumeKg;
    }

    final weeklyEntries = weeklyMap.entries.toList()
      ..sort((a, b) => a.value.sortDate.compareTo(b.value.sortDate));
    final weeklyVolume = weeklyEntries
        .map(
          (e) => WeeklyVolumePoint(
            weekLabel: e.key,
            totalVolumeKg: (e.value.vol * 10).round() / 10.0,
            sessionsCount: e.value.count,
          ),
        )
        .toList();

    final radarCounts = <String, int>{
      'chest': 0,
      'back': 0,
      'shoulders': 0,
      'arms': 0,
      'legs': 0,
      'core': 0,
    };
    final volumeByAxis = <String, double>{
      'chest': 0.0,
      'back': 0.0,
      'shoulders': 0.0,
      'arms': 0.0,
      'legs': 0.0,
      'core': 0.0,
    };

    final bestPrByExercise = <String, PersonalRecordItem>{};
    var workingSetsCount = 0;

    for (final wset in sets) {
      if (wset.setType.toUpperCase() == 'WARMUP') continue;
      final ex = exerciseByIdOrCode[wset.exerciseId.toUpperCase()] ??
          exerciseByIdOrCode[wset.exerciseId];

      // PR calculation over full history
      final est1rm = wset.estimated1rm > 0
          ? wset.estimated1rm
          : WorkoutCalculators.calculateEstimated1Rm(
              wset.weightKg,
              wset.reps,
            );
      if (ex != null && est1rm > 0) {
        final existing = bestPrByExercise[ex.code];
        if (existing == null || est1rm > existing.best1rmKg) {
          bestPrByExercise[ex.code] = PersonalRecordItem(
            exerciseCode: ex.code,
            exerciseNameVi: ex.nameVi,
            best1rmKg: est1rm,
            bestWeightKg: wset.weightKg,
            bestReps: wset.reps,
            achievedAt: wset.completedAt,
          );
        }
      }

      final sessDt = sessionStartById[wset.sessionId];
      if (sessDt == null) continue;
      workingSetsCount++;

      if (ex == null) continue;
      final setVol = wset.weightKg * wset.reps;
      final countedAxes = <String>{};
      for (final m in ex.primaryMuscles) {
        final axis = muscleToRadarAxis[m];
        if (axis != null && countedAxes.add(axis)) {
          volumeByAxis[axis] = (volumeByAxis[axis] ?? 0.0) + setVol;
          if (!sessDt.isBefore(radarCutoff) &&
              (wset.rpe == null || wset.rpe! >= 6.0)) {
            radarCounts[axis] = (radarCounts[axis] ?? 0) + 1;
          }
        }
      }
    }

    final prs = bestPrByExercise.values.toList()
      ..sort((a, b) => b.best1rmKg.compareTo(a.best1rmKg));

    final pushSets = radarCounts['chest']! + radarCounts['shoulders']!;
    final pullSets = radarCounts['back']!;
    final ratio =
        pushSets > 0 ? (pullSets / pushSets) : (pullSets > 0 ? 1.0 : 1.0);

    return AnalyticsSummaryModel(
      periodDays: periodDays,
      weeklyVolume: weeklyVolume,
      volumeByMuscleAxis: volumeByAxis,
      muscleRadarCounts: radarCounts,
      pullPushRatio: (ratio * 100).round() / 100.0,
      personalRecords: prs.take(15).toList(),
      streakDays: WorkoutCalculators.computeWorkoutStreakDays(
        sessions.where((s) => s.deletedAt == null).map((s) => s.startedAt),
        now: currentUtc,
      ),
      totalVolumeKg: (totalVolume * 10).round() / 10.0,
      totalWorkingSets: workingSetsCount,
    );
  }
}

final aiAnalyticsRepositoryProvider = Provider<AiAnalyticsRepository>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final dio = ref.watch(dioProvider);
  final exRepo = ref.watch(exerciseRepositoryProvider);
  return AiAnalyticsRepository(db, dio, exRepo);
});

final aiReadinessProvider =
    FutureProvider<AiReadinessSnapshotModel>((ref) async {
  return ref.watch(aiAnalyticsRepositoryProvider).fetchReadinessAndOverload();
});

final analyticsSummaryProvider =
    FutureProvider.family<AnalyticsSummaryModel, int>((ref, days) async {
  return ref
      .watch(aiAnalyticsRepositoryProvider)
      .loadAnalyticsSummary(periodDays: days);
});
