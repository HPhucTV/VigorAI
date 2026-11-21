// [OWNER: M2] Unit Tests & Performance Benchmark cho Sprint 2 (1RM, Plate Calculator, Volume/Radar 1.000 sets < 300ms, Recovery 3D) (T-M2-09..12)
import 'package:flutter_test/flutter_test.dart';
import 'package:vigorai_app/core/database/workout_tables.drift.dart';
import 'package:vigorai_app/core/theme/app_theme.dart';
import 'package:vigorai_app/features/ai_analytics/data/ai_analytics_repository.dart';
import 'package:vigorai_app/features/gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import 'package:vigorai_app/features/workout/domain/workout_calculators.dart';

void main() {
  group('WorkoutCalculators — 1RM Epley/Brzycki (F17)', () {
    test('returns exact weight for 1 rep and 0 for invalid inputs', () {
      expect(WorkoutCalculators.calculateEstimated1Rm(100.0, 1), 100.0);
      expect(WorkoutCalculators.calculateEstimated1Rm(0.0, 8), 0.0);
      expect(WorkoutCalculators.calculateEstimated1Rm(80.0, 0), 0.0);
    });

    test('uses average of Epley and Brzycki for 2..10 reps', () {
      // 100 kg x 5 reps: Epley = 100 * (1 + 5/30) = 116.6667, Brzycki = 100 * (36 / 32) = 112.5
      // Avg = 114.58
      expect(WorkoutCalculators.calculateEstimated1Rm(100.0, 5), 114.58);
      // 80 kg x 10 reps: Epley = 80 * 1.3333 = 106.67, Brzycki = 80 * 36/27 = 106.67
      expect(WorkoutCalculators.calculateEstimated1Rm(80.0, 10), 106.67);
    });

    test('uses Epley formula for > 10 reps', () {
      // 60 kg x 15 reps: 60 * (1 + 15/30) = 90.0
      expect(WorkoutCalculators.calculateEstimated1Rm(60.0, 15), 90.0);
    });
  });

  group('WorkoutCalculators — Visual Barbell Plate Calculator (F18)', () {
    test('decomposes 95 kg with 20 kg bar into 20 + 15 + 2.5 kg per side', () {
      final res = WorkoutCalculators.calculateBarbellPlates(
        targetWeightKg: 95.0,
        barWeightKg: 20.0,
      );
      expect(res.isExact, isTrue);
      expect(res.achievedWeightKg, 95.0);
      expect(res.perSidePlates, [20.0, 15.0, 2.5]);
      expect(res.warningMessage, isNull);
    });

    test('warns on odd weight indivisible by 1.25 kg per side and suggests nearest', () {
      final res = WorkoutCalculators.calculateBarbellPlates(
        targetWeightKg: 81.0,
        barWeightKg: 20.0,
      );
      expect(res.isExact, isFalse);
      expect(res.achievedWeightKg, 80.0);
      expect(res.nearestLowerKg, 80.0);
      expect(res.nearestHigherKg, 82.5);
      expect(res.warningMessage, isNotNull);
    });

    test('supports 15 kg female bar and 10 kg EZ bar', () {
      final female = WorkoutCalculators.calculateBarbellPlates(
        targetWeightKg: 45.0,
        barWeightKg: 15.0,
      );
      expect(female.isExact, isTrue);
      expect(female.perSidePlates, [15.0]);

      final belowBar = WorkoutCalculators.calculateBarbellPlates(
        targetWeightKg: 8.0,
        barWeightKg: 10.0,
      );
      expect(belowBar.isExact, isFalse);
      expect(belowBar.achievedWeightKg, 10.0);
    });
  });

  group('AiAnalyticsRepository — Recovery 3D & 1,000-set Benchmark (F20-F25)', () {
    test('maps muscle fatigue to canonical Green/Orange/Red recovery colors', () {
      expect(
        AiAnalyticsRepository.recoveryColorForFatigue(0.15),
        AppColors.muscleRecoveredGreen,
      );
      expect(
        AiAnalyticsRepository.recoveryColorForFatigue(0.45),
        AppColors.muscleSecondaryOrange,
      );
      expect(
        AiAnalyticsRepository.recoveryColorForFatigue(0.80),
        AppColors.musclePrimaryRed,
      );
      expect(
        AiAnalyticsRepository.newUserFallbackSnapshot().readinessScore,
        85.0,
      );
      expect(
        AiAnalyticsRepository.estimatedHoursToFullRecovery(
          MuscleMaterialIds.chest,
          0.5,
        ),
        greaterThan(24),
      );
    });

    test('aggregates Volume Load & 6-Axis Radar across 1,000 sets in < 300ms', () {
      final now = DateTime.utc(2026, 11, 20, 12, 0);
      final exercises = {
        'BARBELL_BENCH_PRESS': const ExerciseModel(
          id: 'ex-bench',
          code: 'BARBELL_BENCH_PRESS',
          nameVi: 'Đẩy ngực ngang',
          equipmentType: 'BARBELL',
          model3dGlbUrl: 'assets/3d_bundled/barbell_bench_press.glb',
          assetChecksum: 'abc',
          primaryMuscles: [MuscleMaterialIds.chest],
        ),
        'BARBELL_SQUAT': const ExerciseModel(
          id: 'ex-squat',
          code: 'BARBELL_SQUAT',
          nameVi: 'Squat',
          equipmentType: 'BARBELL',
          model3dGlbUrl: 'assets/3d_bundled/barbell_squat.glb',
          assetChecksum: 'def',
          primaryMuscles: [MuscleMaterialIds.quads, MuscleMaterialIds.glutes],
        ),
        'LAT_PULLDOWN': const ExerciseModel(
          id: 'ex-lat',
          code: 'LAT_PULLDOWN',
          nameVi: 'Kéo xô',
          equipmentType: 'CABLE',
          model3dGlbUrl: 'https://cdn.vigorai.app/exercises/lat_pulldown.glb',
          assetChecksum: 'ghi',
          primaryMuscles: [MuscleMaterialIds.backLats],
        ),
      };

      final sessions = <WorkoutSessionModel>[];
      final sets = <WorkoutSetModel>[];
      final codes = exercises.keys.toList();

      // 50 sessions x 20 sets = 1,000 sets
      for (var sIdx = 0; sIdx < 50; sIdx++) {
        final dt = now.subtract(Duration(days: sIdx % 25));
        final sessId = 'sess-$sIdx';
        sessions.add(
          WorkoutSessionModel(
            id: sessId,
            sessionTitle: 'Buổi tập #$sIdx',
            startedAt: dt,
            completedAt: dt.add(const Duration(minutes: 60)),
            durationSeconds: 3600,
            totalVolumeKg: 10000.0,
            status: 'COMPLETED',
            updatedAt: dt,
          ),
        );
        for (var j = 0; j < 20; j++) {
          final code = codes[(sIdx + j) % codes.length];
          sets.add(
            WorkoutSetModel(
              id: 'set-$sIdx-$j',
              sessionId: sessId,
              exerciseId: code,
              setNumber: j + 1,
              setType: j == 0 ? 'WARMUP' : 'NORMAL',
              weightKg: 80.0 + (j % 4) * 5.0,
              reps: 8,
              rpe: 8.0,
              estimated1rm: WorkoutCalculators.calculateEstimated1Rm(
                80.0 + (j % 4) * 5.0,
                8,
              ),
              completedAt: dt,
              updatedAt: dt,
            ),
          );
        }
      }

      final sw = Stopwatch()..start();
      final summary = AiAnalyticsRepository.aggregateAnalyticsFromData(
        sessions: sessions,
        sets: sets,
        exerciseByIdOrCode: exercises,
        periodDays: 90,
        now: now,
      );
      sw.stop();

      expect(sets.length, 1000);
      expect(sw.elapsedMilliseconds, lessThan(300));
      expect(summary.totalWorkingSets, 950); // 50 WARMUP excluded
      expect(summary.muscleRadarCounts['chest']!, greaterThan(0));
      expect(summary.muscleRadarCounts['legs']!, greaterThan(0));
      expect(summary.muscleRadarCounts['back']!, greaterThan(0));
      expect(summary.personalRecords, isNotEmpty);
      expect(summary.streakDays, greaterThan(0));
    });

    test('computes workout hydration bonus accurately when RPE is omitted or >= 7.0', () {
      final now = DateTime.utc(2026, 11, 21, 10, 0);
      final noRpeSets = [
        WorkoutSetModel(
          id: 's1',
          sessionId: 'sess-1',
          exerciseId: 'BARBELL_BENCH_PRESS',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 80.0,
          reps: 8,
          rpe: null,
          completedAt: now,
          updatedAt: now,
        ),
      ];
      final highRpeSets = [
        WorkoutSetModel(
          id: 's2',
          sessionId: 'sess-2',
          exerciseId: 'BARBELL_BENCH_PRESS',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 80.0,
          reps: 8,
          rpe: 7.5,
          completedAt: now,
          updatedAt: now,
        ),
      ];

      expect(
        WorkoutCalculators.calculateWorkoutHydrationBonusMl(
          durationSeconds: 30 * 60,
          sets: noRpeSets,
        ),
        500,
      );
      expect(
        WorkoutCalculators.calculateWorkoutHydrationBonusMl(
          durationSeconds: 30 * 60,
          sets: highRpeSets,
        ),
        750,
      );
      expect(
        WorkoutCalculators.calculateWorkoutHydrationBonusMl(
          durationSeconds: 60 * 60,
          sets: noRpeSets,
        ),
        750,
      );
    });

    test('excludes ABANDONED/deleted sessions, handles empty & pull-only ratio, and separates multi-year weeks', () {
      final now = DateTime.utc(2026, 11, 21, 12, 0);
      final exercises = {
        'LAT_PULLDOWN': const ExerciseModel(
          id: 'ex-lat',
          code: 'LAT_PULLDOWN',
          nameVi: 'Kéo xô',
          equipmentType: 'CABLE',
          model3dGlbUrl: 'assets/3d_bundled/lat_pulldown.glb',
          assetChecksum: 'abc',
          primaryMuscles: [MuscleMaterialIds.backLats],
        ),
      };

      // 1. Empty state -> pullPushRatio == 0.0
      final emptySummary = AiAnalyticsRepository.aggregateAnalyticsFromData(
        sessions: const [],
        sets: const [],
        exerciseByIdOrCode: exercises,
        now: now,
      );
      expect(emptySummary.pullPushRatio, 0.0);

      // 2. Two sessions from 2025-11-22 (364d ago, Monday 17/11/25) & 2026-11-16 (Monday 16/11/26), plus ABANDONED & soft-deleted sessions
      final d2025 = DateTime.utc(2025, 11, 22, 10, 0);
      final d2026 = DateTime.utc(2026, 11, 16, 10, 0);
      final sessions = [
        WorkoutSessionModel(
          id: 'sess-2025',
          sessionTitle: 'Old Back Day',
          startedAt: d2025,
          completedAt: d2025.add(const Duration(minutes: 45)),
          durationSeconds: 2700,
          totalVolumeKg: 1000.0,
          status: 'COMPLETED',
          updatedAt: d2025,
        ),
        WorkoutSessionModel(
          id: 'sess-2026',
          sessionTitle: 'Recent Back Day',
          startedAt: d2026,
          completedAt: d2026.add(const Duration(minutes: 45)),
          durationSeconds: 2700,
          totalVolumeKg: 1200.0,
          status: 'COMPLETED',
          updatedAt: d2026,
        ),
        WorkoutSessionModel(
          id: 'sess-abandoned',
          sessionTitle: 'Abandoned Day',
          startedAt: now,
          totalVolumeKg: 5000.0,
          status: 'ABANDONED',
          updatedAt: now,
        ),
        WorkoutSessionModel(
          id: 'sess-deleted',
          sessionTitle: 'Deleted Day',
          startedAt: now,
          totalVolumeKg: 5000.0,
          status: 'COMPLETED',
          updatedAt: now,
          deletedAt: now,
        ),
      ];

      final sets = [
        WorkoutSetModel(
          id: 'set-valid-1',
          sessionId: 'sess-2025',
          exerciseId: 'LAT_PULLDOWN',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 60.0,
          reps: 10,
          rpe: 8.0,
          estimated1rm: 80.0,
          completedAt: d2025,
          updatedAt: d2025,
        ),
        WorkoutSetModel(
          id: 'set-valid-2',
          sessionId: 'sess-2026',
          exerciseId: 'LAT_PULLDOWN',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 70.0,
          reps: 8,
          rpe: 8.0,
          estimated1rm: 88.0,
          completedAt: d2026,
          updatedAt: d2026,
        ),
        WorkoutSetModel(
          id: 'set-abandoned',
          sessionId: 'sess-abandoned',
          exerciseId: 'LAT_PULLDOWN',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 200.0,
          reps: 10,
          rpe: 9.0,
          estimated1rm: 266.0,
          completedAt: now,
          updatedAt: now,
        ),
        WorkoutSetModel(
          id: 'set-deleted',
          sessionId: 'sess-deleted',
          exerciseId: 'LAT_PULLDOWN',
          setNumber: 1,
          setType: 'NORMAL',
          weightKg: 220.0,
          reps: 10,
          rpe: 9.0,
          estimated1rm: 293.0,
          completedAt: now,
          updatedAt: now,
        ),
      ];

      final summary = AiAnalyticsRepository.aggregateAnalyticsFromData(
        sessions: sessions,
        sets: sets,
        exerciseByIdOrCode: exercises,
        periodDays: 365,
        now: now,
      );

      expect(summary.totalVolumeKg, 2200.0);
      expect(summary.totalWorkingSets, 2);
      expect(summary.weeklyVolume.length, 2);
      expect(
        summary.weeklyVolume.first.weekLabel,
        isNot(equals(summary.weeklyVolume.last.weekLabel)),
      );
      expect(summary.personalRecords.length, 1);
      expect(summary.personalRecords.first.best1rmKg, 88.0);
      expect(summary.pullPushRatio, greaterThan(0.0));
      // ABANDONED & deleted sessions at `now` must not count toward streak (most recent COMPLETED is 5 days ago)
      expect(summary.streakDays, 0);
    });

    test('prevents double scaling on base_mannequin_female.glb', () {
      final femaleBase = Muscle3DViewerWidget.effectiveScaleFor(
        BodyAvatarPreset.femaleFit,
        'assets/3d_bundled/base_mannequin_female.glb',
      );
      expect(femaleBase.x, 1.0);
      expect(femaleBase.y, 1.0);
      expect(femaleBase.z, 1.0);

      final femaleExercise = Muscle3DViewerWidget.effectiveScaleFor(
        BodyAvatarPreset.femaleFit,
        'assets/3d_bundled/barbell_bench_press.glb',
      );
      expect(femaleExercise.x, BodyAvatarPreset.femaleFit.scaleX);
      expect(femaleExercise.y, BodyAvatarPreset.femaleFit.scaleY);
      expect(femaleExercise.z, BodyAvatarPreset.femaleFit.scaleZ);
    });
  });
}
