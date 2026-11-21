// [OWNER: M1] Unit Test cong thuc Suc khoe, WorkManager, Food Scan Scale & Sync Conflict LWW (Sprint 2)
import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:vigorai_app/core/database/health_tables.drift.dart';
import 'package:vigorai_app/core/database/workout_tables.drift.dart';
import 'package:vigorai_app/core/platform/workmanager_reminder_service.dart';
import 'package:vigorai_app/core/sync/sync_queue_manager.dart';
import 'package:vigorai_app/features/auth_privacy/data/auth_repository.dart';
import 'package:vigorai_app/features/health/food_scan/data/food_scan_repository.dart';

void main() {
  group('F01 - Biometrics, WHO Asian BMI & 7-Day Moving Average', () {
    test('calculates BMI rounded to 1 decimal and classifies Asian thresholds', () {
      expect(BiometricLogModel.calculateBmi(70.0, 175.0), 22.9);
      expect(BiometricLogModel.classifyAsianBmi(18.0), 'Thiếu cân');
      expect(BiometricLogModel.classifyAsianBmi(22.9), 'Bình thường');
      expect(BiometricLogModel.classifyAsianBmi(23.7), 'Thừa cân');
      expect(BiometricLogModel.classifyAsianBmi(25.5), 'Béo phì');
    });

    test('calculates 7-day moving average accurately on chronological logs', () {
      final now = DateTime.utc(2026, 11, 20);
      final weights = [70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 76.0, 77.0];
      final logs = [
        for (var i = 0; i < weights.length; i++)
          BiometricLogModel(
            id: 'b-$i',
            weightKg: weights[i],
            bmi: 23.0,
            loggedDateIso: '2026-11-${(10 + i).toString().padLeft(2, '0')}',
            updatedAt: now,
          ),
      ];

      final ma = BiometricLogModel.calculateMovingAverage7Day(logs);
      expect(ma.length, 8);
      expect(ma[0], 70.0);
      expect(ma[6], 73.0); // avg(70..76) = 73.0
      expect(ma[7], 74.0); // avg(71..77) = 74.0
    });
  });

  group('F03 - Smart Hydration & WorkManager Time Window', () {
    test('adds +500ml for moderate workout and +750ml for 60m RPE 8 workout', () {
      // Base: 35 * 70 = 2450 ml
      expect(DailyHealthModel.calculateTargetWaterMl(70.0), 2450);
      expect(
        DailyHealthModel.calculateTargetWaterMl(
          70.0,
          workoutMinutes: 40,
          workoutRpe: 6.0,
        ),
        2950,
      );
      expect(
        DailyHealthModel.calculateTargetWaterMl(
          70.0,
          workoutMinutes: 60,
          workoutRpe: 8.0,
        ),
        3200,
      );
    });

    test('restricts hydration reminders strictly to 07:00 - 21:30', () {
      expect(
        WorkmanagerReminderService.isWithinHydrationWindow(
          DateTime(2026, 11, 20, 6, 59),
        ),
        isFalse,
      );
      expect(
        WorkmanagerReminderService.isWithinHydrationWindow(
          DateTime(2026, 11, 20, 7, 0),
        ),
        isTrue,
      );
      expect(
        WorkmanagerReminderService.isWithinHydrationWindow(
          DateTime(2026, 11, 20, 21, 30),
        ),
        isTrue,
      );
      expect(
        WorkmanagerReminderService.isWithinHydrationWindow(
          DateTime(2026, 11, 20, 21, 31),
        ),
        isFalse,
      );
    });
  });

  group('F04 & F05 - Mifflin-St Jeor BMR/TDEE/Macros & Sleep Classification', () {
    test('calculates BMR, Bulk/Cut/Maintain calories and Macro targets', () {
      // Male: 10*70 + 6.25*172 - 5*24 + 5 = 700 + 1075 - 120 + 5 = 1660
      final bmrMale = DailyHealthModel.calculateBmrMifflinStJeor(
        weightKg: 70.0,
        heightCm: 172.0,
        ageYears: 24,
        gender: 'MALE',
      );
      expect(bmrMale, 1660.0);

      final bulkKcal = DailyHealthModel.calculateTargetCalories(
        bmr: bmrMale,
        activityLevel: 'MODERATE',
        fitnessGoal: 'BULK',
      );
      // 1660 * 1.55 = 2573 -> +300 = 2873
      expect(bulkKcal, 2873.0);

      final cutKcal = DailyHealthModel.calculateTargetCalories(
        bmr: bmrMale,
        activityLevel: 'SEDENTARY',
        fitnessGoal: 'CUT',
      );
      // max(1660, 1660*1.2 - 400 = 1592) => clamped at BMR 1660
      expect(cutKcal, 1660.0);

      final macros = DailyHealthModel.calculateMacroTargets(
        weightKg: 70.0,
        targetCalories: 2800.0,
      );
      expect(macros.proteinG, 140.0); // 2.0 g/kg * 70
      expect(macros.fatG, 78.0); // round((2800 * 0.25)/9) = 78
      expect(macros.carbsG, 385.0); // (2800 - 560 - 702)/4 = 384.5 -> 385
    });

    test('classifies sleep duration correctly', () {
      expect(DailyHealthModel.classifySleepStatus(5.5), 'Thiếu ngủ');
      expect(DailyHealthModel.classifySleepStatus(7.5), 'Đạt chuẩn 7–9h');
      expect(DailyHealthModel.classifySleepStatus(9.5), 'Ngủ bù');
    });
  });

  group('F06 - SupplementIntakeStore ("Da uong" & Weekly Adherence)', () {
    late Directory tempDir;

    setUp(() async {
      tempDir = await Directory.systemTemp.createTemp('vigorai_supp_test_');
    });

    tearDown(() async {
      if (await tempDir.exists()) {
        await tempDir.delete(recursive: true);
      }
    });

    test('marks supplement taken without UI and computes 7-day adherence', () async {
      final store = SupplementIntakeStore(directoryResolver: () async => tempDir);
      await store.markTaken('supp-001', dateIso: '2026-11-20');
      await store.markTaken('supp-002', dateIso: '2026-11-20');
      await store.markTaken('supp-001', dateIso: '2026-11-19');

      final taken20 = await store.getTakenIdsForDate('2026-11-20');
      expect(taken20, {'supp-001', 'supp-002'});

      // 3 taken out of (2 active * 7 days = 14) => 21.4%
      final adherence = await store.calculateWeeklyAdherence(
        activeSupplementCount: 2,
        referenceDate: DateTime(2026, 11, 20),
      );
      expect(adherence, 21.4);

      await store.unmarkTaken('supp-002', dateIso: '2026-11-20');
      expect(await store.getTakenIdsForDate('2026-11-20'), {'supp-001'});
    });
  });

  group('F19 & T-M1-12 - Food Gram Scaling & Sync LWW Conflict Resolution', () {
    test('scales calories and macros accurately when adjusting gram slider', () {
      final item = DetectedFoodItemModel.fromJson({
        'class_code': 'GRILLED_CHICKEN_BREAST',
        'name_vi': 'Ức gà áp chảo',
        'confidence': 0.93,
        'bbox_norm': [0.18, 0.25, 0.52, 0.61],
        'estimated_grams': 180.0,
        'calories': 297.0,
        'protein_g': 55.8,
        'carbs_g': 0.0,
        'fat_g': 6.5,
      });

      final scaled = item.scaleToGrams(90.0);
      expect(scaled.calories, 148.5);
      expect(scaled.proteinG, 27.9);
      expect(scaled.fatG, 3.3);

      final title = MealLogModel.extractTitleFromDetectedItems(
        jsonEncode([scaled.toJson()]),
      );
      expect(title, 'Ức gà áp chảo');
    });

    test('resolves LWW timestamps and preserves max(steps_count)', () {
      final t1 = DateTime.utc(2026, 11, 20, 8, 0);
      final t2 = DateTime.utc(2026, 11, 20, 10, 0);
      expect(
        SyncConflictResolver.shouldServerWin(
          localUpdatedAt: t1,
          serverUpdatedAt: t2,
        ),
        isTrue,
      );
      expect(
        SyncConflictResolver.shouldServerWin(
          localUpdatedAt: t2,
          serverUpdatedAt: t1,
        ),
        isFalse,
      );
      expect(
        SyncConflictResolver.mergeDailyHealthSteps(
          localSteps: 9200,
          serverSteps: 4500,
        ),
        9200,
      );
    });

    test('calculates user age from birth_date with safe fallbacks', () {
      final refDate = DateTime(2026, 11, 21);

      const birthdayPassed = AuthUserProfile(
        id: 'u-1',
        email: 'demo@vigorai.app',
        fullName: 'Nguyen Van An',
        birthDateIso: '2002-05-14',
      );
      expect(birthdayPassed.calculateAgeYears(referenceDate: refDate), 24);

      const birthdayNotPassed = AuthUserProfile(
        id: 'u-2',
        email: 'u2@vigorai.app',
        fullName: 'User 2',
        birthDateIso: '2002-12-01',
      );
      expect(birthdayNotPassed.calculateAgeYears(referenceDate: refDate), 23);

      const missingDob = AuthUserProfile(
        id: 'u-3',
        email: 'u3@vigorai.app',
        fullName: 'User 3',
      );
      expect(missingDob.calculateAgeYears(referenceDate: refDate), 24);

      const invalidDob = AuthUserProfile(
        id: 'u-4',
        email: 'u4@vigorai.app',
        fullName: 'User 4',
        birthDateIso: 'not-a-date',
      );
      expect(invalidDob.calculateAgeYears(referenceDate: refDate), 24);

      const outOfRangeDob = AuthUserProfile(
        id: 'u-5',
        email: 'u5@vigorai.app',
        fullName: 'User 5',
        birthDateIso: '2022-01-01',
      );
      expect(outOfRangeDob.calculateAgeYears(referenceDate: refDate), 24);
    });

    test('parses backend JSON compatibility for AuthUserProfile and Sync models', () {
      final profile = AuthUserProfile.fromJson({
        'id': '11111111-1111-4111-8111-111111111111',
        'email': 'demo@vigorai.app',
        'full_name': 'Nguyễn Văn An',
        'gender': 'MALE',
        'birth_date': '2002-05-14',
        'height_cm': 172.0,
        'activity_level': 'MODERATE',
        'fitness_goal': 'BULK',
        'medical_disclaimer_accepted': true,
      });
      expect(profile.birthDateIso, '2002-05-14');
      expect(profile.toJson()['birth_date'], '2002-05-14');

      final routine = WorkoutRoutineModel.fromJson({
        'id': 'r-1',
        'name': 'Push Pull Legs',
        'split_type': 'PPL',
        'scheduled_weekdays': [1, 3, 5],
        'exercises': [
          {
            'exercise_code': 'BARBELL_BENCH_PRESS',
            'order_index': 0,
            'target_sets': 4,
            'target_rep_min': 6,
            'target_rep_max': 8,
            'default_rest_seconds': 120,
          },
        ],
        'is_template': false,
        'updated_at': '2026-11-20T10:00:00Z',
      });
      expect(routine.exercises.single.exerciseCode, 'BARBELL_BENCH_PRESS');

      final session = WorkoutSessionModel.fromJson({
        'id': 's-1',
        'routine_id': 'r-1',
        'session_title': 'Push Day',
        'started_at': '2026-11-20T09:00:00Z',
        'completed_at': '2026-11-20T10:00:00Z',
        'duration_seconds': 3600,
        'total_volume_kg': 4200.0,
        'status': 'COMPLETED',
        'updated_at': '2026-11-20T10:00:00Z',
      });
      expect(session.durationSeconds, 3600);

      final wset = WorkoutSetModel.fromJson({
        'id': 'set-1',
        'session_id': 's-1',
        'exercise_id': 'ex-1',
        'set_number': 1,
        'set_type': 'NORMAL',
        'weight_kg': 80.0,
        'reps': 8,
        'rpe': 8.0,
        'estimated_1rm': 101.33,
        'is_pr': true,
        'completed_at': '2026-11-20T09:15:00Z',
        'updated_at': '2026-11-20T09:15:00Z',
      });
      expect(wset.isPr, isTrue);
      expect(wset.estimated1rm, 101.33);
    });
  });
}
