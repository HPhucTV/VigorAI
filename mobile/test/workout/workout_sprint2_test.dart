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
  });
}
