// [OWNER: M1] Ho so The trang, Muc tieu Tap luyen & Phac do Ca nhan hoa Offline-First
import 'dart:convert';
import 'dart:math' as math;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import '../../../core/database/health_tables.drift.dart';
import '../../../core/network/dio_client.dart';
import '../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';

enum Somatotype {
  ectomorph(
    code: 'ECTOMORPH',
    labelVi: 'Ectomorph · Người gầy',
    shortLabelVi: 'Tạng Gầy',
    descriptionVi: 'Khung xương nhỏ, chuyển hóa nhanh, cần ưu tiên tăng cân và tạ vừa nặng.',
  ),
  mesomorph(
    code: 'MESOMORPH',
    labelVi: 'Mesomorph · Cân đối',
    shortLabelVi: 'Tạng Cân đối',
    descriptionVi: 'Khung vai cân đối, dễ đáp ứng tập luyện và phục hồi tốt.',
  ),
  endomorph(
    code: 'ENDOMORPH',
    labelVi: 'Endomorph · Đầy đặn',
    shortLabelVi: 'Tạng Đầy đặn',
    descriptionVi: 'Dễ tăng sức mạnh nhưng dễ tích mỡ, cần kiểm soát Calo và nhịp độ cao.',
  );

  final String code;
  final String labelVi;
  final String shortLabelVi;
  final String descriptionVi;

  const Somatotype({
    required this.code,
    required this.labelVi,
    required this.shortLabelVi,
    required this.descriptionVi,
  });

  static Somatotype fromCode(String? raw) {
    switch (raw?.toUpperCase()) {
      case 'ECTOMORPH':
        return Somatotype.ectomorph;
      case 'ENDOMORPH':
        return Somatotype.endomorph;
      default:
        return Somatotype.mesomorph;
    }
  }
}

enum BodyFatPreset {
  lean(
    code: 'LEAN',
    labelVi: 'Săn chắc / Rõ nét cơ',
    descriptionVi: 'Cơ bụng lộ nhẹ hoặc rõ, ít mỡ dưới da.',
    malePct: 10.0,
    femalePct: 17.0,
    maleRangeVi: 'Nam 8–12%',
    femaleRangeVi: 'Nữ 15–19%',
  ),
  athletic(
    code: 'ATHLETIC',
    labelVi: 'Cân đối / Thể thao',
    descriptionVi: 'Thân hình gọn gàng, khỏe khoắn và linh hoạt.',
    malePct: 15.0,
    femalePct: 22.0,
    maleRangeVi: 'Nam 13–17%',
    femaleRangeVi: 'Nữ 20–24%',
  ),
  average(
    code: 'AVERAGE',
    labelVi: 'Trung bình / Hơi đầy',
    descriptionVi: 'Mỡ tích nhẹ ở vùng bụng/hông, mục tiêu tăng cơ giảm mỡ.',
    malePct: 21.0,
    femalePct: 28.0,
    maleRangeVi: 'Nam 18–24%',
    femaleRangeVi: 'Nữ 25–30%',
  ),
  higherFat(
    code: 'HIGHER_FAT',
    labelVi: 'Ưu tiên giảm mỡ rõ rệt',
    descriptionVi: 'Cần cắt giảm mỡ an toàn đồng thời bảo toàn khối cơ.',
    malePct: 28.0,
    femalePct: 34.0,
    maleRangeVi: 'Nam 25%+',
    femaleRangeVi: 'Nữ 31%+',
  );

  final String code;
  final String labelVi;
  final String descriptionVi;
  final double malePct;
  final double femalePct;
  final String maleRangeVi;
  final String femaleRangeVi;

  const BodyFatPreset({
    required this.code,
    required this.labelVi,
    required this.descriptionVi,
    required this.malePct,
    required this.femalePct,
    required this.maleRangeVi,
    required this.femaleRangeVi,
  });

  double estimatedPctForGender(String gender) =>
      gender.toUpperCase() == 'FEMALE' ? femalePct : malePct;

  String rangeLabelForGender(String gender) =>
      gender.toUpperCase() == 'FEMALE' ? femaleRangeVi : maleRangeVi;

  static BodyFatPreset fromCode(String? raw) {
    switch (raw?.toUpperCase()) {
      case 'LEAN':
        return BodyFatPreset.lean;
      case 'AVERAGE':
        return BodyFatPreset.average;
      case 'HIGHER_FAT':
        return BodyFatPreset.higherFat;
      default:
        return BodyFatPreset.athletic;
    }
  }
}

enum ExperienceLevel {
  beginner(
    code: 'BEGINNER',
    labelVi: 'Người mới (< 6 tháng)',
    shortLabelVi: 'Mới tập',
    descriptionVi: 'Ưu tiên 3 hiệp/bài, tập chuẩn kỹ thuật 3D và làm quen nhịp thở.',
  ),
  intermediate(
    code: 'INTERMEDIATE',
    labelVi: 'Trung cấp (6–24 tháng)',
    shortLabelVi: 'Trung cấp',
    descriptionVi: 'Phân chia đa dạng PPL / Upper-Lower, tăng tải trọng đều đặn.',
  ),
  advanced(
    code: 'ADVANCED',
    labelVi: 'Nâng cao (> 2 năm)',
    shortLabelVi: 'Nâng cao',
    descriptionVi: 'Khối lượng tập cao hơn, hỗ trợ Superset và tạ nặng.',
  );

  final String code;
  final String labelVi;
  final String shortLabelVi;
  final String descriptionVi;

  const ExperienceLevel({
    required this.code,
    required this.labelVi,
    required this.shortLabelVi,
    required this.descriptionVi,
  });

  static ExperienceLevel fromCode(String? raw) {
    switch (raw?.toUpperCase()) {
      case 'BEGINNER':
        return ExperienceLevel.beginner;
      case 'ADVANCED':
        return ExperienceLevel.advanced;
      default:
        return ExperienceLevel.intermediate;
    }
  }
}

enum TrainingLocation {
  fullGym(
    code: 'FULL_GYM',
    labelVi: 'Phòng Gym đầy đủ máy',
    shortLabelVi: 'Phòng Gym',
    descriptionVi: 'Mở khóa toàn bộ đòn tạ, tạ đơn, máy cáp, máy khối & bodyweight.',
  ),
  homeDumbbell(
    code: 'HOME_DUMBBELL',
    labelVi: 'Tại nhà với Tạ đơn',
    shortLabelVi: 'Nhà · Tạ đơn',
    descriptionVi: 'Tự động đổi các bài máy/đòn tạ sang biến thể tạ đơn & trọng lượng cơ thể.',
  ),
  bodyweightOnly(
    code: 'BODYWEIGHT_ONLY',
    labelVi: 'Tại nhà Không dụng cụ',
    shortLabelVi: 'Nhà · Tay không',
    descriptionVi: 'Chỉ dùng trọng lượng cơ thể, tự tăng số rep để đủ kích thích cơ.',
  );

  final String code;
  final String labelVi;
  final String shortLabelVi;
  final String descriptionVi;

  const TrainingLocation({
    required this.code,
    required this.labelVi,
    required this.shortLabelVi,
    required this.descriptionVi,
  });

  static TrainingLocation fromCode(String? raw) {
    switch (raw?.toUpperCase()) {
      case 'HOME_DUMBBELL':
        return TrainingLocation.homeDumbbell;
      case 'BODYWEIGHT_ONLY':
        return TrainingLocation.bodyweightOnly;
      default:
        return TrainingLocation.fullGym;
    }
  }
}

enum ProgramChoiceType {
  aiCustom(
    code: 'AI_CUSTOM',
    labelVi: 'AI Thiết kế Riêng theo Vóc dáng',
    shortLabelVi: 'AI Cá nhân hóa',
    subtitleVi: 'Tự lắp ghép theo nơi tập, thời lượng, tạng người & nhóm cơ ưu tiên.',
  ),
  cbumPpl(
    code: 'CBUM_PPL',
    labelVi: 'CBum Classic Physique PPL',
    shortLabelVi: 'CBum PPL',
    subtitleVi: '6 buổi/tuần · Vai rộng, ngực trên dày và lưng xô chữ V.',
  ),
  jeffNippardUl(
    code: 'JEFF_NIPPARD_UL',
    labelVi: 'Jeff Nippard Khoa học Upper/Lower',
    shortLabelVi: 'Jeff Nippard U/L',
    subtitleVi: '4 buổi/tuần · Tối ưu phì đại cơ theo khoa học, cân bằng Đẩy/Kéo.',
  ),
  arnoldVolume(
    code: 'ARNOLD_VOLUME',
    labelVi: 'Arnold Golden Era Volume',
    shortLabelVi: 'Arnold Volume',
    subtitleVi: '5–6 buổi/tuần · Superset Ngực–Lưng đối kháng, tay & vai cổ điển.',
  ),
  gluteCoreSculpt(
    code: 'GLUTE_CORE_SCULPT',
    labelVi: 'Glute & Core Sculpt — Nữ Fitness',
    shortLabelVi: 'Glute & Core',
    subtitleVi: '4 buổi/tuần · Trọng tâm Mông tròn, Đùi sau, Lõi và Lưng thon.',
  ),
  homeShred(
    code: 'HOME_SHRED',
    labelVi: 'Home Dumbbell & Bodyweight Shred',
    shortLabelVi: 'Home Shred',
    subtitleVi: '3–4 buổi/tuần · Đốt mỡ giữ cơ 30–45 phút tại nhà.',
  );

  final String code;
  final String labelVi;
  final String shortLabelVi;
  final String subtitleVi;

  const ProgramChoiceType({
    required this.code,
    required this.labelVi,
    required this.shortLabelVi,
    required this.subtitleVi,
  });

  static ProgramChoiceType fromCode(String? raw) {
    for (final val in values) {
      if (val.code == raw?.toUpperCase()) return val;
    }
    return ProgramChoiceType.aiCustom;
  }
}

enum PriorityMuscleGroup {
  chest(
    code: 'CHEST',
    labelVi: 'Ngực',
    materialIds: [MuscleMaterialIds.chest],
  ),
  back(
    code: 'BACK',
    labelVi: 'Lưng Xô',
    materialIds: [MuscleMaterialIds.backLats, MuscleMaterialIds.traps],
  ),
  shoulders(
    code: 'SHOULDERS',
    labelVi: 'Vai',
    materialIds: [MuscleMaterialIds.shoulders],
  ),
  arms(
    code: 'ARMS',
    labelVi: 'Tay (Trước/Sau)',
    materialIds: [MuscleMaterialIds.biceps, MuscleMaterialIds.triceps],
  ),
  legsGlutes(
    code: 'LEGS_GLUTES',
    labelVi: 'Mông & Chân',
    materialIds: [
      MuscleMaterialIds.glutes,
      MuscleMaterialIds.quads,
      MuscleMaterialIds.hamstrings,
      MuscleMaterialIds.calves,
    ],
  ),
  absCore(
    code: 'ABS_CORE',
    labelVi: 'Bụng & Lõi',
    materialIds: [MuscleMaterialIds.absCore],
  );

  final String code;
  final String labelVi;
  final List<String> materialIds;

  const PriorityMuscleGroup({
    required this.code,
    required this.labelVi,
    required this.materialIds,
  });

  static PriorityMuscleGroup? fromCode(String? raw) {
    final upper = raw?.toUpperCase();
    for (final val in values) {
      if (val.code == upper) return val;
    }
    return null;
  }
}

class UserFitnessProfile {
  final String fullName;
  final String gender; // MALE | FEMALE
  final int ageYears;
  final double heightCm;
  final double currentWeightKg;
  final double targetWeightKg;
  final BodyFatPreset bodyFatPreset;
  final double estimatedBodyFatPct;
  final Somatotype somatotype;
  final ExperienceLevel experienceLevel;
  final TrainingLocation trainingLocation;
  final int sessionsPerWeek;
  final List<int> weeklyDays;
  final int sessionDurationMin;
  final List<PriorityMuscleGroup> priorityMuscles;
  final ProgramChoiceType selectedProgram;
  final String preferredAvatarCode; // MALE_FIT | FEMALE_FIT | MALE_BULK
  final bool hasCompletedWizard;

  const UserFitnessProfile({
    this.fullName = 'Vận động viên VigorAI',
    this.gender = 'MALE',
    this.ageYears = 24,
    this.heightCm = 172.0,
    this.currentWeightKg = 70.0,
    this.targetWeightKg = 73.0,
    this.bodyFatPreset = BodyFatPreset.athletic,
    this.estimatedBodyFatPct = 15.0,
    this.somatotype = Somatotype.mesomorph,
    this.experienceLevel = ExperienceLevel.intermediate,
    this.trainingLocation = TrainingLocation.fullGym,
    this.sessionsPerWeek = 4,
    this.weeklyDays = const [1, 2, 4, 5],
    this.sessionDurationMin = 55,
    this.priorityMuscles = const [
      PriorityMuscleGroup.chest,
      PriorityMuscleGroup.shoulders,
    ],
    this.selectedProgram = ProgramChoiceType.aiCustom,
    this.preferredAvatarCode = 'MALE_FIT',
    this.hasCompletedWizard = false,
  });

  String get derivedFitnessGoal {
    if (targetWeightKg > currentWeightKg + 1.0) return 'BULK';
    if (targetWeightKg < currentWeightKg - 1.0) return 'CUT';
    return 'MAINTAIN';
  }

  String get fitnessGoalLabelVi {
    switch (derivedFitnessGoal) {
      case 'BULK':
        return 'Tăng cơ';
      case 'CUT':
        return 'Giảm mỡ';
      default:
        return 'Giữ dáng';
    }
  }

  String get derivedActivityLevel {
    if (sessionsPerWeek >= 6) return 'VERY_ACTIVE';
    if (sessionsPerWeek >= 4) return 'ACTIVE';
    if (sessionsPerWeek >= 2) return 'MODERATE';
    return 'LIGHT';
  }

  double get bmi => BiometricLogModel.calculateBmi(currentWeightKg, heightCm);

  String get bmiLabel => BiometricLogModel.classifyAsianBmi(bmi);

  double get bmrKcal => DailyHealthModel.calculateBmrMifflinStJeor(
        weightKg: currentWeightKg,
        heightCm: heightCm,
        ageYears: ageYears,
        gender: gender,
      );

  double get targetCaloriesKcal {
    final base = DailyHealthModel.calculateTargetCalories(
      bmr: bmrKcal,
      activityLevel: derivedActivityLevel,
      fitnessGoal: derivedFitnessGoal,
    );
    if (somatotype == Somatotype.ectomorph && derivedFitnessGoal == 'BULK') {
      return (base + 100).roundToDouble(); // tong +400 kcal so voi TDEE
    }
    if (somatotype == Somatotype.endomorph && derivedFitnessGoal == 'CUT') {
      return math.max(bmrKcal, base - 50).roundToDouble();
    }
    return base;
  }

  MacroTargets get macroTargets {
    final baseMacros = DailyHealthModel.calculateMacroTargets(
      weightKg: currentWeightKg,
      targetCalories: targetCaloriesKcal,
    );
    if (somatotype == Somatotype.endomorph && derivedFitnessGoal == 'CUT') {
      final proteinG = (currentWeightKg * 2.1).roundToDouble();
      final fatG = ((targetCaloriesKcal * 0.25) / 9.0).roundToDouble();
      final rem =
          math.max(0.0, targetCaloriesKcal - (proteinG * 4.0) - (fatG * 9.0));
      return MacroTargets(
        targetCalories: targetCaloriesKcal,
        proteinG: proteinG,
        carbsG: (rem / 4.0).roundToDouble(),
        fatG: fatG,
      );
    }
    return baseMacros;
  }

  int get baseWaterTargetMl =>
      DailyHealthModel.calculateTargetWaterMl(currentWeightKg);

  int get workoutDayWaterTargetMl => DailyHealthModel.calculateTargetWaterMl(
        currentWeightKg,
        workoutMinutes: sessionDurationMin,
        workoutRpe: experienceLevel == ExperienceLevel.beginner ? 6.5 : 7.5,
      );

  Set<String> get priorityMuscleMaterialIds {
    final out = <String>{};
    for (final group in priorityMuscles) {
      out.addAll(group.materialIds);
    }
    return out;
  }

  BodyAvatarPreset get recommendedAvatarPreset {
    if (preferredAvatarCode == 'FEMALE_FIT') {
      return BodyAvatarPreset.femaleFit;
    }
    if (preferredAvatarCode == 'MALE_BULK') {
      return BodyAvatarPreset.maleBulk;
    }
    if (gender.toUpperCase() == 'FEMALE') {
      return BodyAvatarPreset.femaleFit;
    }
    if (derivedFitnessGoal == 'BULK' &&
        (bodyFatPreset == BodyFatPreset.lean ||
            bodyFatPreset == BodyFatPreset.athletic)) {
      return BodyAvatarPreset.maleBulk;
    }
    return BodyAvatarPreset.maleFit;
  }

  String get birthDateIso {
    final year = (DateTime.now().year - ageYears.clamp(16, 75));
    return '$year-01-01';
  }

  static List<int> defaultDaysForSessions(int sessions) {
    switch (sessions.clamp(1, 7)) {
      case 1:
        return const [1];
      case 2:
        return const [1, 4];
      case 3:
        return const [1, 3, 5];
      case 4:
        return const [1, 2, 4, 5];
      case 5:
        return const [1, 2, 3, 5, 6];
      case 6:
        return const [1, 2, 3, 4, 5, 6];
      default:
        return const [1, 2, 3, 4, 5, 6, 7];
    }
  }

  UserFitnessProfile copyWith({
    String? fullName,
    String? gender,
    int? ageYears,
    double? heightCm,
    double? currentWeightKg,
    double? targetWeightKg,
    BodyFatPreset? bodyFatPreset,
    double? estimatedBodyFatPct,
    Somatotype? somatotype,
    ExperienceLevel? experienceLevel,
    TrainingLocation? trainingLocation,
    int? sessionsPerWeek,
    List<int>? weeklyDays,
    int? sessionDurationMin,
    List<PriorityMuscleGroup>? priorityMuscles,
    ProgramChoiceType? selectedProgram,
    String? preferredAvatarCode,
    bool? hasCompletedWizard,
  }) {
    return UserFitnessProfile(
      fullName: fullName ?? this.fullName,
      gender: gender ?? this.gender,
      ageYears: ageYears ?? this.ageYears,
      heightCm: heightCm ?? this.heightCm,
      currentWeightKg: currentWeightKg ?? this.currentWeightKg,
      targetWeightKg: targetWeightKg ?? this.targetWeightKg,
      bodyFatPreset: bodyFatPreset ?? this.bodyFatPreset,
      estimatedBodyFatPct: estimatedBodyFatPct ?? this.estimatedBodyFatPct,
      somatotype: somatotype ?? this.somatotype,
      experienceLevel: experienceLevel ?? this.experienceLevel,
      trainingLocation: trainingLocation ?? this.trainingLocation,
      sessionsPerWeek: sessionsPerWeek ?? this.sessionsPerWeek,
      weeklyDays: weeklyDays ?? this.weeklyDays,
      sessionDurationMin: sessionDurationMin ?? this.sessionDurationMin,
      priorityMuscles: priorityMuscles ?? this.priorityMuscles,
      selectedProgram: selectedProgram ?? this.selectedProgram,
      preferredAvatarCode: preferredAvatarCode ?? this.preferredAvatarCode,
      hasCompletedWizard: hasCompletedWizard ?? this.hasCompletedWizard,
    );
  }

  factory UserFitnessProfile.fromJson(Map<String, dynamic> json) {
    final days = ((json['weekly_days'] as List?) ?? const [1, 2, 4, 5])
        .map((e) => (e as num).toInt())
        .where((d) => d >= 1 && d <= 7)
        .toList()
      ..sort();
    final muscles = ((json['priority_muscles'] as List?) ?? const [])
        .map((e) => PriorityMuscleGroup.fromCode(e?.toString()))
        .whereType<PriorityMuscleGroup>()
        .toList();

    return UserFitnessProfile(
      fullName: (json['full_name'] as String?) ?? 'Vận động viên VigorAI',
      gender: (json['gender'] as String?) ?? 'MALE',
      ageYears: ((json['age_years'] as num?)?.toInt() ?? 24).clamp(16, 75),
      heightCm: ((json['height_cm'] as num?)?.toDouble() ?? 172.0)
          .clamp(140.0, 210.0),
      currentWeightKg:
          ((json['current_weight_kg'] as num?)?.toDouble() ?? 70.0)
              .clamp(35.0, 180.0),
      targetWeightKg: ((json['target_weight_kg'] as num?)?.toDouble() ?? 73.0)
          .clamp(35.0, 180.0),
      bodyFatPreset: BodyFatPreset.fromCode(json['body_fat_preset'] as String?),
      estimatedBodyFatPct:
          (json['estimated_body_fat_pct'] as num?)?.toDouble() ?? 15.0,
      somatotype: Somatotype.fromCode(json['somatotype'] as String?),
      experienceLevel:
          ExperienceLevel.fromCode(json['experience_level'] as String?),
      trainingLocation:
          TrainingLocation.fromCode(json['training_location'] as String?),
      sessionsPerWeek:
          ((json['sessions_per_week'] as num?)?.toInt() ?? 4).clamp(1, 7),
      weeklyDays: days.isEmpty ? const [1, 2, 4, 5] : days,
      sessionDurationMin:
          ((json['session_duration_min'] as num?)?.toInt() ?? 55).clamp(25, 120),
      priorityMuscles: muscles,
      selectedProgram:
          ProgramChoiceType.fromCode(json['selected_program'] as String?),
      preferredAvatarCode:
          (json['preferred_avatar_code'] as String?) ?? 'MALE_FIT',
      hasCompletedWizard: (json['has_completed_wizard'] as bool?) ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'full_name': fullName,
        'gender': gender,
        'age_years': ageYears,
        'height_cm': heightCm,
        'current_weight_kg': currentWeightKg,
        'target_weight_kg': targetWeightKg,
        'body_fat_preset': bodyFatPreset.code,
        'estimated_body_fat_pct': estimatedBodyFatPct,
        'somatotype': somatotype.code,
        'experience_level': experienceLevel.code,
        'training_location': trainingLocation.code,
        'sessions_per_week': sessionsPerWeek,
        'weekly_days': weeklyDays,
        'session_duration_min': sessionDurationMin,
        'priority_muscles': priorityMuscles.map((m) => m.code).toList(),
        'selected_program': selectedProgram.code,
        'preferred_avatar_code': preferredAvatarCode,
        'has_completed_wizard': hasCompletedWizard,
      };
}

class UserFitnessProfileNotifier extends StateNotifier<UserFitnessProfile> {
  final FlutterSecureStorage _storage;

  UserFitnessProfileNotifier(this._storage)
      : super(const UserFitnessProfile()) {
    restore();
  }

  Future<void> restore() async {
    try {
      final raw = await _storage.read(key: StorageKeys.fitnessProfileJson);
      if (raw != null && raw.trim().isNotEmpty) {
        final decoded = jsonDecode(raw) as Map<String, dynamic>;
        state = UserFitnessProfile.fromJson(decoded);
      }
    } catch (_) {
      // Fallback ve mac dinh neu khong co plugin storage trong widget test
    }
  }

  Future<void> saveProfile(UserFitnessProfile next) async {
    state = next;
    try {
      await _storage.write(
        key: StorageKeys.fitnessProfileJson,
        value: jsonEncode(next.toJson()),
      );
    } catch (_) {
      // Ignore in test environments
    }
  }

  Future<void> clearProfile() async {
    state = const UserFitnessProfile();
    try {
      await _storage.delete(key: StorageKeys.fitnessProfileJson);
    } catch (_) {}
  }
}

final userFitnessProfileProvider =
    StateNotifierProvider<UserFitnessProfileNotifier, UserFitnessProfile>(
  (ref) {
    final storage = ref.watch(secureStorageProvider);
    return UserFitnessProfileNotifier(storage);
  },
);
