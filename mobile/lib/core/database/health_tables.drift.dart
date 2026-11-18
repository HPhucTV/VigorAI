// [OWNER: M1] Bang SQLite Drift + Domain Entities Offline-First cho Suc khoe & Sinh trac
import 'dart:convert';
import 'dart:math' as math;

import 'package:drift/drift.dart';

// ============================================================================
// 1. DRIFT TABLE DEFINITIONS (Dung chung trong app_database.dart)
// ============================================================================

class BiometricLogsTable extends Table {
  TextColumn get id => text()();
  RealColumn get weightKg => real()();
  RealColumn get bodyFatPct => real().nullable()();
  RealColumn get muscleMassKg => real().nullable()();
  RealColumn get bmi => real()();
  TextColumn get circumferencesJson => text().withDefault(const Constant('{}'))();
  DateTimeColumn get loggedDate => dateTime()();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

class DailyHealthLogsTable extends Table {
  TextColumn get id => text()();
  TextColumn get logDateIso => text()(); // YYYY-MM-DD
  IntColumn get stepsCount => integer().withDefault(const Constant(0))();
  RealColumn get distanceKm => real().withDefault(const Constant(0.0))();
  IntColumn get activeCaloriesKcal => integer().withDefault(const Constant(0))();
  IntColumn get waterMl => integer().withDefault(const Constant(0))();
  IntColumn get targetWaterMl => integer().withDefault(const Constant(2000))();
  RealColumn get sleepHours => real().withDefault(const Constant(0.0))();
  IntColumn get sleepQualityScore => integer().nullable()();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

class MealLogsTable extends Table {
  TextColumn get id => text()();
  TextColumn get mealType => text()(); // BREAKFAST | LUNCH | DINNER | SNACK
  TextColumn get localImagePath => text().nullable()();
  TextColumn get aiDetectedItemsJson => text().withDefault(const Constant('[]'))();
  RealColumn get totalCalories => real().withDefault(const Constant(0.0))();
  RealColumn get proteinG => real().withDefault(const Constant(0.0))();
  RealColumn get carbsG => real().withDefault(const Constant(0.0))();
  RealColumn get fatG => real().withDefault(const Constant(0.0))();
  DateTimeColumn get loggedAt => dateTime()();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

class SupplementSchedulesTable extends Table {
  TextColumn get id => text()();
  TextColumn get supplementName => text()();
  TextColumn get dosageLabel => text()();
  TextColumn get reminderTimeHhMm => text()();
  BoolColumn get workoutDaysOnly => boolean().withDefault(const Constant(false))();
  BoolColumn get isActive => boolean().withDefault(const Constant(true))();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================================
// 2. DOMAIN ENTITIES & CONG THUC KHOA HOC OFFLINE-FIRST (T-M1-03)
// ============================================================================

class BiometricLogModel {
  final String id;
  final double weightKg;
  final double? bodyFatPct;
  final double? muscleMassKg;
  final double bmi;
  final Map<String, double> circumferencesCm;
  final String loggedDateIso;
  final String syncStatus;
  final DateTime updatedAt;
  final DateTime? deletedAt;

  const BiometricLogModel({
    required this.id,
    required this.weightKg,
    this.bodyFatPct,
    this.muscleMassKg,
    required this.bmi,
    this.circumferencesCm = const {},
    required this.loggedDateIso,
    this.syncStatus = 'SYNCED',
    required this.updatedAt,
    this.deletedAt,
  });

  /// Cong thuc BMI = weight_kg / (height_m)^2, lam tron 1 chu so thap phan
  static double calculateBmi(double weightKg, double heightCm) {
    if (heightCm <= 0) return 0.0;
    final heightM = heightCm / 100.0;
    final raw = weightKg / (heightM * heightM);
    return (raw * 10).round() / 10.0;
  }

  /// Phan loai BMI chuan Chau A (WHO Asia-Pacific)
  static String classifyAsianBmi(double bmi) {
    if (bmi < 18.5) return 'Thiếu cân';
    if (bmi < 23.0) return 'Bình thường';
    if (bmi < 25.0) return 'Thừa cân';
    return 'Béo phì';
  }

  factory BiometricLogModel.fromJson(Map<String, dynamic> json) {
    final rawCirc = json['circumferences_cm'] as Map<String, dynamic>? ?? {};
    return BiometricLogModel(
      id: (json['id'] as String?) ?? 'bio-${json['logged_date']}',
      weightKg: (json['weight_kg'] as num).toDouble(),
      bodyFatPct: (json['body_fat_pct'] as num?)?.toDouble(),
      muscleMassKg: (json['muscle_mass_kg'] as num?)?.toDouble(),
      bmi: (json['bmi'] as num).toDouble(),
      circumferencesCm: rawCirc.map((k, v) => MapEntry(k, (v as num).toDouble())),
      loggedDateIso: json['logged_date'] as String,
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now().toUtc(),
      deletedAt: json['deleted_at'] != null
          ? DateTime.parse(json['deleted_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'weight_kg': weightKg,
        'body_fat_pct': bodyFatPct,
        'muscle_mass_kg': muscleMassKg,
        'bmi': bmi,
        'circumferences_cm': circumferencesCm,
        'logged_date': loggedDateIso,
        'sync_status': syncStatus,
        'updated_at': updatedAt.toUtc().toIso8601String(),
        'deleted_at': deletedAt?.toUtc().toIso8601String(),
      };
}

class DailyHealthModel {
  final String id;
  final String logDateIso;
  final int stepsCount;
  final int targetSteps;
  final double distanceKm;
  final int activeCaloriesKcal;
  final int waterMl;
  final int targetWaterMl;
  final double sleepHours;
  final int? sleepQualityScore;
  final String syncStatus;
  final DateTime updatedAt;

  const DailyHealthModel({
    required this.id,
    required this.logDateIso,
    this.stepsCount = 0,
    this.targetSteps = 8000,
    this.distanceKm = 0.0,
    this.activeCaloriesKcal = 0,
    this.waterMl = 0,
    this.targetWaterMl = 2450,
    this.sleepHours = 0.0,
    this.sleepQualityScore,
    this.syncStatus = 'SYNCED',
    required this.updatedAt,
  });

  /// Cong thuc nuoc thong minh (F03): 35ml * weight_kg + bu nuoc buoi tap
  static int calculateTargetWaterMl(
    double weightKg, {
    int workoutMinutes = 0,
    double workoutRpe = 0.0,
  }) {
    final base = (35.0 * weightKg).round();
    int workoutBonus = 0;
    if (workoutMinutes >= 60 || workoutRpe >= 7.0) {
      workoutBonus = 750;
    } else if (workoutMinutes > 0) {
      workoutBonus = 500;
    }
    return base + workoutBonus;
  }

  /// Cong thuc BMR Mifflin-St Jeor (1990) & TDEE (F04)
  static double calculateBmrMifflinStJeor({
    required double weightKg,
    required double heightCm,
    required int ageYears,
    required String gender,
  }) {
    final base = 10.0 * weightKg + 6.25 * heightCm - 5.0 * ageYears;
    return gender.toUpperCase() == 'FEMALE' ? base - 161.0 : base + 5.0;
  }

  static double calculateTargetCalories({
    required double bmr,
    required String activityLevel,
    required String fitnessGoal,
  }) {
    const factors = {
      'SEDENTARY': 1.2,
      'LIGHT': 1.375,
      'MODERATE': 1.55,
      'ACTIVE': 1.725,
      'VERY_ACTIVE': 1.9,
    };
    final tdee = bmr * (factors[activityLevel.toUpperCase()] ?? 1.55);
    switch (fitnessGoal.toUpperCase()) {
      case 'BULK':
        return (tdee + 300).roundToDouble();
      case 'CUT':
        return math.max(bmr, tdee - 400).roundToDouble();
      default:
        return tdee.roundToDouble();
    }
  }

  DailyHealthModel copyWith({
    int? stepsCount,
    double? distanceKm,
    int? activeCaloriesKcal,
    int? waterMl,
    int? targetWaterMl,
    double? sleepHours,
    int? sleepQualityScore,
    String? syncStatus,
    DateTime? updatedAt,
  }) {
    return DailyHealthModel(
      id: id,
      logDateIso: logDateIso,
      stepsCount: stepsCount ?? this.stepsCount,
      targetSteps: targetSteps,
      distanceKm: distanceKm ?? this.distanceKm,
      activeCaloriesKcal: activeCaloriesKcal ?? this.activeCaloriesKcal,
      waterMl: waterMl ?? this.waterMl,
      targetWaterMl: targetWaterMl ?? this.targetWaterMl,
      sleepHours: sleepHours ?? this.sleepHours,
      sleepQualityScore: sleepQualityScore ?? this.sleepQualityScore,
      syncStatus: syncStatus ?? this.syncStatus,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  factory DailyHealthModel.fromJson(Map<String, dynamic> json) {
    return DailyHealthModel(
      id: (json['id'] as String?) ?? 'daily-${json['log_date']}',
      logDateIso: json['log_date'] as String,
      stepsCount: (json['steps_count'] as num?)?.toInt() ?? 0,
      targetSteps: (json['target_steps'] as num?)?.toInt() ?? 8000,
      distanceKm: (json['distance_km'] as num?)?.toDouble() ?? 0.0,
      activeCaloriesKcal: (json['active_calories_kcal'] as num?)?.toInt() ?? 0,
      waterMl: (json['water_ml'] as num?)?.toInt() ?? 0,
      targetWaterMl: (json['target_water_ml'] as num?)?.toInt() ?? 2450,
      sleepHours: (json['sleep_hours'] as num?)?.toDouble() ?? 0.0,
      sleepQualityScore: (json['sleep_quality_score'] as num?)?.toInt(),
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now().toUtc(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'log_date': logDateIso,
        'steps_count': stepsCount,
        'target_steps': targetSteps,
        'distance_km': distanceKm,
        'active_calories_kcal': activeCaloriesKcal,
        'water_ml': waterMl,
        'target_water_ml': targetWaterMl,
        'sleep_hours': sleepHours,
        'sleep_quality_score': sleepQualityScore,
        'sync_status': syncStatus,
        'updated_at': updatedAt.toUtc().toIso8601String(),
      };
}

class MealLogModel {
  final String id;
  final String mealType;
  final String title;
  final String? localImagePath;
  final String aiDetectedItemsJson;
  final double totalCalories;
  final double proteinG;
  final double carbsG;
  final double fatG;
  final DateTime loggedAt;
  final String syncStatus;
  final DateTime updatedAt;
  final DateTime? deletedAt;

  const MealLogModel({
    required this.id,
    required this.mealType,
    required this.title,
    this.localImagePath,
    this.aiDetectedItemsJson = '[]',
    required this.totalCalories,
    required this.proteinG,
    required this.carbsG,
    required this.fatG,
    required this.loggedAt,
    this.syncStatus = 'SYNCED',
    required this.updatedAt,
    this.deletedAt,
  });

  factory MealLogModel.fromJson(Map<String, dynamic> json) {
    return MealLogModel(
      id: json['id'] as String,
      mealType: json['meal_type'] as String,
      title: (json['title'] as String?) ?? 'Bữa ăn',
      localImagePath: json['local_image_path'] as String?,
      aiDetectedItemsJson: json['ai_detected_items'] != null
          ? jsonEncode(json['ai_detected_items'])
          : '[]',
      totalCalories: (json['total_calories'] as num).toDouble(),
      proteinG: (json['protein_g'] as num).toDouble(),
      carbsG: (json['carbs_g'] as num).toDouble(),
      fatG: (json['fat_g'] as num).toDouble(),
      loggedAt: DateTime.parse(json['logged_at'] as String),
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now().toUtc(),
      deletedAt: json['deleted_at'] != null
          ? DateTime.parse(json['deleted_at'] as String)
          : null,
    );
  }
}

class SupplementScheduleModel {
  final String id;
  final String supplementName;
  final String dosageLabel;
  final String reminderTimeHhMm;
  final bool workoutDaysOnly;
  final bool isActive;
  final bool takenToday;
  final String syncStatus;
  final DateTime updatedAt;

  const SupplementScheduleModel({
    required this.id,
    required this.supplementName,
    required this.dosageLabel,
    required this.reminderTimeHhMm,
    this.workoutDaysOnly = false,
    this.isActive = true,
    this.takenToday = false,
    this.syncStatus = 'SYNCED',
    required this.updatedAt,
  });

  factory SupplementScheduleModel.fromJson(Map<String, dynamic> json) {
    return SupplementScheduleModel(
      id: json['id'] as String,
      supplementName: json['supplement_name'] as String,
      dosageLabel: json['dosage_label'] as String,
      reminderTimeHhMm: json['reminder_time'] as String,
      workoutDaysOnly: (json['workout_days_only'] as bool?) ?? false,
      isActive: (json['is_active'] as bool?) ?? true,
      takenToday: (json['taken_today'] as bool?) ?? false,
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : DateTime.now().toUtc(),
    );
  }
}
