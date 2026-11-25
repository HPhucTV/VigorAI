// [OWNER: M2] Bo may Sinh Giao an Thong minh (Smart Routine Generator Engine) & 5 Chuong trinh VDV kinh dien
import 'dart:math' as math;

import '../../../core/database/workout_tables.drift.dart';
import '../../auth_privacy/data/user_fitness_profile.dart';

class ProProgramCatalogItem {
  final ProgramChoiceType type;
  final String title;
  final String athleteTag;
  final String frequencyLabel;
  final String focusSummary;
  final String targetAudience;

  const ProProgramCatalogItem({
    required this.type,
    required this.title,
    required this.athleteTag,
    required this.frequencyLabel,
    required this.focusSummary,
    required this.targetAudience,
  });
}

class _SessionBlueprint {
  final String name;
  final String splitType;
  final List<String> exerciseCodes;
  final bool enablePushPullSuperset;

  const _SessionBlueprint({
    required this.name,
    required this.splitType,
    required this.exerciseCodes,
    this.enablePushPullSuperset = false,
  });
}

class SmartRoutineGenerator {
  SmartRoutineGenerator._();

  static const String aiPlanIdPrefix = 'ai-plan-';

  static const List<ProProgramCatalogItem> proProgramsCatalog = [
    ProProgramCatalogItem(
      type: ProgramChoiceType.cbumPpl,
      title: 'CBum Classic Physique PPL',
      athleteTag: 'Cổ điển · Thẩm mỹ V-Taper',
      frequencyLabel: '6 buổi/tuần',
      focusSummary: 'Vai rộng, ngực trên dày và lưng xô hình chữ V sắc nét.',
      targetAudience: 'Phù hợp người thích tập PPL chuẩn thể hình cổ điển.',
    ),
    ProProgramCatalogItem(
      type: ProgramChoiceType.jeffNippardUl,
      title: 'Jeff Nippard Khoa học Upper/Lower',
      athleteTag: 'Khoa học Thể thao · Cân bằng',
      frequencyLabel: '4 buổi/tuần',
      focusSummary: 'Tối ưu phì đại cơ với tỷ lệ Đẩy/Kéo cân đối và RPE chuẩn.',
      targetAudience: 'Phù hợp mọi cấp độ muốn tăng cơ bền vững 4 buổi/tuần.',
    ),
    ProProgramCatalogItem(
      type: ProgramChoiceType.arnoldVolume,
      title: 'Arnold Golden Era Volume',
      athleteTag: 'Thể hình Huyền thoại · Superset',
      frequencyLabel: '5–6 buổi/tuần',
      focusSummary: 'Phối hợp Ngực–Lưng đối kháng Superset, chú trọng tay & vai.',
      targetAudience: 'Phù hợp người có quỹ thời gian khá và thích pump cơ mạnh.',
    ),
    ProProgramCatalogItem(
      type: ProgramChoiceType.gluteCoreSculpt,
      title: 'Glute & Core Sculpt — Nữ Fitness',
      athleteTag: 'Vóc dáng Đồng hồ cát',
      frequencyLabel: '4 buổi/tuần',
      focusSummary: 'Trọng tâm Mông tròn, Đùi sau săn, Bụng lõi & Lưng thon.',
      targetAudience: 'Thiết kế tối ưu cho nữ hoặc mục tiêu phát triển thân dưới.',
    ),
    ProProgramCatalogItem(
      type: ProgramChoiceType.homeShred,
      title: 'Home Dumbbell & Bodyweight Shred',
      athleteTag: 'Tại nhà · Đốt mỡ giữ cơ',
      frequencyLabel: '3–4 buổi/tuần',
      focusSummary: 'Linh hoạt 30–45 phút chỉ với tạ đơn hoặc trọng lượng cơ thể.',
      targetAudience: 'Phù hợp tập tại nhà ít dụng cụ nhưng vẫn đủ kích thích cơ.',
    ),
  ];

  static const Map<PriorityMuscleGroup, List<String>> _priorityCandidates = {
    PriorityMuscleGroup.chest: [
      'CABLE_CHEST_FLY',
      'INCLINE_DUMBBELL_PRESS',
      'PUSH_UP',
    ],
    PriorityMuscleGroup.back: [
      'STRAIGHT_ARM_CABLE_PULLDOWN',
      'ONE_ARM_DUMBBELL_ROW',
      'WIDE_GRIP_PULLUP',
    ],
    PriorityMuscleGroup.shoulders: [
      'DUMBBELL_LATERAL_RAISE',
      'CABLE_FACE_PULL',
      'DUMBBELL_SHOULDER_PRESS',
    ],
    PriorityMuscleGroup.arms: [
      'INCLINE_DUMBBELL_CURL',
      'OVERHEAD_DUMBBELL_TRICEP_EXT',
      'DUMBBELL_HAMMER_CURL',
      'CABLE_TRICEP_PUSHDOWN',
    ],
    PriorityMuscleGroup.legsGlutes: [
      'BARBELL_HIP_THRUST',
      'LEG_EXTENSION',
      'WALKING_LUNGE',
      'GOBLET_SQUAT',
    ],
    PriorityMuscleGroup.absCore: [
      'HANGING_LEG_RAISE',
      'CABLE_CRUNCH',
      'PLANK',
    ],
  };

  static bool isEquipmentAllowed(
    ExerciseModel ex,
    TrainingLocation location,
  ) {
    final eq = ex.equipmentType.toUpperCase();
    final code = ex.code.toUpperCase();
    switch (location) {
      case TrainingLocation.fullGym:
        return true;
      case TrainingLocation.homeDumbbell:
        return eq == 'DUMBBELL' || eq == 'BODYWEIGHT';
      case TrainingLocation.bodyweightOnly:
        return eq == 'BODYWEIGHT' || code == 'WALKING_LUNGE';
    }
  }

  static List<WorkoutRoutineModel> generatePlan({
    required UserFitnessProfile profile,
    required List<ExerciseModel> allExercises,
  }) {
    final now = DateTime.now().toUtc();
    final byCode = <String, ExerciseModel>{
      for (final ex in allExercises) ex.code.toUpperCase(): ex,
    };

    final blueprints = _blueprintsForProfile(profile);
    final rawDays = List<int>.from(profile.weeklyDays)..sort();
    final validDays = rawDays.where((d) => d >= 1 && d <= 7).toList();
    final fallbackDays = validDays.isEmpty
        ? UserFitnessProfile.defaultDaysForSessions(blueprints.length)
        : validDays;

    // Phan bo ngay tap trong tuan vao tung buoi cua chuong trinh
    final assignedWeekdays = List.generate(
      blueprints.length,
      (_) => <int>[],
    );
    for (var i = 0; i < fallbackDays.length; i++) {
      assignedWeekdays[i % blueprints.length].add(fallbackDays[i]);
    }
    for (var i = 0; i < blueprints.length; i++) {
      if (assignedWeekdays[i].isEmpty) {
        assignedWeekdays[i].add(((i * 2) % 7) + 1);
      }
      assignedWeekdays[i] = assignedWeekdays[i].toSet().toList()..sort();
    }

    final desiredExerciseCount = _exerciseCountForDuration(
      profile.sessionDurationMin,
    );
    final repRange = _repRangeForProfile(profile);
    final restTimes = _restTimesForProfile(profile);

    final result = <WorkoutRoutineModel>[];
    for (var dayIdx = 0; dayIdx < blueprints.length; dayIdx++) {
      final bp = blueprints[dayIdx];
      final pickedCodes = <String>[];

      // 1. Loc theo dia diem / dung cu & tu dong thay bai trung nhom co neu thieu dung cu
      for (final rawCode in bp.exerciseCodes) {
        final code = rawCode.toUpperCase();
        final candidate = _resolveExerciseForLocation(
          targetCode: code,
          location: profile.trainingLocation,
          byCode: byCode,
          allExercises: allExercises,
          alreadyPicked: pickedCodes,
        );
        if (candidate != null && !pickedCodes.contains(candidate)) {
          pickedCodes.add(candidate);
        }
      }

      // 2. Uu tien them bai cho nhom co muc tieu (Priority Muscles)
      for (final priority in profile.priorityMuscles) {
        if (pickedCodes.length >= desiredExerciseCount + 1) break;
        if (!_blueprintMatchesPriority(bp, priority, byCode)) continue;
        final bonusCode = _pickBonusExerciseForPriority(
          priority: priority,
          location: profile.trainingLocation,
          byCode: byCode,
          alreadyPicked: pickedCodes,
        );
        if (bonusCode != null) {
          pickedCodes.add(bonusCode);
        }
      }

      // 3. Bo sung neu chua du so bai theo thoi luong (hoac cat gon neu <= 35 phut)
      if (pickedCodes.length < desiredExerciseCount &&
          profile.trainingLocation == TrainingLocation.bodyweightOnly) {
        for (final bwCode in const [
          'PUSH_UP',
          'WALKING_LUNGE',
          'WIDE_GRIP_PULLUP',
          'HANGING_LEG_RAISE',
          'PLANK',
        ]) {
          if (pickedCodes.length >= desiredExerciseCount) break;
          if (byCode.containsKey(bwCode) && !pickedCodes.contains(bwCode)) {
            pickedCodes.add(bwCode);
          }
        }
      }

      final trimmedCodes = pickedCodes.take(desiredExerciseCount).toList();
      if (trimmedCodes.isEmpty && allExercises.isNotEmpty) {
        trimmedCodes.add(allExercises.first.code.toUpperCase());
      }

      final priorityMaterials = profile.priorityMuscleMaterialIds;
      final items = <RoutineExerciseItem>[];
      for (var i = 0; i < trimmedCodes.length; i++) {
        final code = trimmedCodes[i];
        final ex = byCode[code];
        final isCompound = ex != null &&
            (ex.equipmentType == 'BARBELL' || ex.primaryMuscles.length >= 2);
        var sets = _setsForExercise(
          profile: profile,
          isCompound: isCompound,
          index: i,
        );
        if (ex != null &&
            ex.primaryMuscles.any((m) => priorityMaterials.contains(m)) &&
            profile.experienceLevel != ExperienceLevel.beginner &&
            sets < 4) {
          sets += 1;
        }

        final isPlank = code == 'PLANK';
        final repMin = isPlank ? 45 : repRange.$1;
        final repMax = isPlank ? 60 : repRange.$2;
        final restSec = isPlank
            ? 60
            : (isCompound ? restTimes.compoundSec : restTimes.isolationSec);

        final supersetGroup = (bp.enablePushPullSuperset &&
                profile.experienceLevel != ExperienceLevel.beginner &&
                i >= 2 &&
                i <= 3 &&
                trimmedCodes.length >= 4)
            ? 1
            : null;

        items.add(
          RoutineExerciseItem(
            exerciseCode: code,
            orderIndex: i,
            supersetGroupId: supersetGroup,
            targetSets: sets,
            targetRepMin: repMin,
            targetRepMax: repMax,
            defaultRestSeconds: restSec,
          ),
        );
      }

      result.add(
        WorkoutRoutineModel(
          id: '$aiPlanIdPrefix${profile.selectedProgram.code.toLowerCase()}-day${dayIdx + 1}',
          name: bp.name,
          splitType: bp.splitType,
          scheduledWeekdays: assignedWeekdays[dayIdx],
          exercises: items,
          isTemplate: false,
          syncStatus: 'PENDING_CREATE',
          updatedAt: now,
        ),
      );
    }

    return result;
  }

  static List<_SessionBlueprint> _blueprintsForProfile(
    UserFitnessProfile profile,
  ) {
    switch (profile.selectedProgram) {
      case ProgramChoiceType.cbumPpl:
        return const [
          _SessionBlueprint(
            name: 'CBum Push — Ngực trên & Vai',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'INCLINE_DUMBBELL_PRESS',
              'BARBELL_BENCH_PRESS',
              'DUMBBELL_SHOULDER_PRESS',
              'DUMBBELL_LATERAL_RAISE',
              'CABLE_CHEST_FLY',
              'CABLE_TRICEP_PUSHDOWN',
            ],
          ),
          _SessionBlueprint(
            name: 'CBum Pull — Lưng Xô chữ V & Tay trước',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'WIDE_GRIP_PULLUP',
              'BARBELL_BENT_OVER_ROW',
              'LAT_PULLDOWN',
              'SEATED_CABLE_ROW',
              'CABLE_FACE_PULL',
              'INCLINE_DUMBBELL_CURL',
            ],
          ),
          _SessionBlueprint(
            name: 'CBum Legs — Đùi trước, Đùi sau & Lõi',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'BARBELL_SQUAT',
              'ROMANIAN_DEADLIFT',
              'LEG_PRESS',
              'LEG_EXTENSION',
              'SEATED_LEG_CURL',
              'HANGING_LEG_RAISE',
            ],
          ),
        ];
      case ProgramChoiceType.jeffNippardUl:
        return const [
          _SessionBlueprint(
            name: 'Jeff Nippard Upper A — Sức mạnh Đẩy/Kéo',
            splitType: 'UPPER_LOWER',
            exerciseCodes: [
              'BARBELL_BENCH_PRESS',
              'BARBELL_BENT_OVER_ROW',
              'DUMBBELL_SHOULDER_PRESS',
              'LAT_PULLDOWN',
              'CABLE_FACE_PULL',
              'DUMBBELL_HAMMER_CURL',
            ],
          ),
          _SessionBlueprint(
            name: 'Jeff Nippard Lower A — Squat & Đùi sau',
            splitType: 'UPPER_LOWER',
            exerciseCodes: [
              'BARBELL_SQUAT',
              'ROMANIAN_DEADLIFT',
              'LEG_PRESS',
              'SEATED_LEG_CURL',
              'STANDING_CALF_RAISE',
              'CABLE_CRUNCH',
            ],
          ),
          _SessionBlueprint(
            name: 'Jeff Nippard Upper B — Phì đại Thân trên',
            splitType: 'UPPER_LOWER',
            exerciseCodes: [
              'INCLINE_DUMBBELL_PRESS',
              'SEATED_CABLE_ROW',
              'DUMBBELL_LATERAL_RAISE',
              'STRAIGHT_ARM_CABLE_PULLDOWN',
              'SKULL_CRUSHER',
              'BARBELL_BICEP_CURL',
            ],
          ),
          _SessionBlueprint(
            name: 'Jeff Nippard Lower B — Mông & Lưng dưới',
            splitType: 'UPPER_LOWER',
            exerciseCodes: [
              'BARBELL_DEADLIFT',
              'BARBELL_HIP_THRUST',
              'WALKING_LUNGE',
              'LEG_EXTENSION',
              'LEG_CURL_MACHINE',
              'HANGING_LEG_RAISE',
            ],
          ),
        ];
      case ProgramChoiceType.arnoldVolume:
        return const [
          _SessionBlueprint(
            name: 'Arnold Day 1 — Ngực & Lưng Đối kháng',
            splitType: 'ARNOLD_SPLIT',
            enablePushPullSuperset: true,
            exerciseCodes: [
              'BARBELL_BENCH_PRESS',
              'WIDE_GRIP_PULLUP',
              'INCLINE_DUMBBELL_PRESS',
              'BARBELL_BENT_OVER_ROW',
              'CABLE_CHEST_FLY',
              'SEATED_CABLE_ROW',
            ],
          ),
          _SessionBlueprint(
            name: 'Arnold Day 2 — Vai & Tay Superset',
            splitType: 'ARNOLD_SPLIT',
            enablePushPullSuperset: true,
            exerciseCodes: [
              'DUMBBELL_SHOULDER_PRESS',
              'DUMBBELL_LATERAL_RAISE',
              'BARBELL_BICEP_CURL',
              'SKULL_CRUSHER',
              'INCLINE_DUMBBELL_CURL',
              'OVERHEAD_DUMBBELL_TRICEP_EXT',
            ],
          ),
          _SessionBlueprint(
            name: 'Arnold Day 3 — Chân & Bụng Thép',
            splitType: 'ARNOLD_SPLIT',
            exerciseCodes: [
              'BARBELL_SQUAT',
              'ROMANIAN_DEADLIFT',
              'WALKING_LUNGE',
              'LEG_EXTENSION',
              'LEG_CURL_MACHINE',
              'HANGING_LEG_RAISE',
            ],
          ),
        ];
      case ProgramChoiceType.gluteCoreSculpt:
        return const [
          _SessionBlueprint(
            name: 'Glute Sculpt A — Mông Đỉnh & Đùi trước',
            splitType: 'GLUTE_CORE',
            exerciseCodes: [
              'BARBELL_HIP_THRUST',
              'GOBLET_SQUAT',
              'WALKING_LUNGE',
              'CABLE_GLUTE_KICKBACK',
              'PLANK',
            ],
          ),
          _SessionBlueprint(
            name: 'Upper Tone & Core — Lưng thon & Vai gọn',
            splitType: 'GLUTE_CORE',
            exerciseCodes: [
              'LAT_PULLDOWN',
              'DUMBBELL_SHOULDER_PRESS',
              'SEATED_CABLE_ROW',
              'DUMBBELL_LATERAL_RAISE',
              'CABLE_FACE_PULL',
              'CABLE_CRUNCH',
            ],
          ),
          _SessionBlueprint(
            name: 'Glute & Hamstrings B — Đùi sau & Mông dưới',
            splitType: 'GLUTE_CORE',
            exerciseCodes: [
              'ROMANIAN_DEADLIFT',
              'BARBELL_HIP_THRUST',
              'SEATED_LEG_CURL',
              'CABLE_GLUTE_KICKBACK',
              'HANGING_LEG_RAISE',
            ],
          ),
        ];
      case ProgramChoiceType.homeShred:
        return const [
          _SessionBlueprint(
            name: 'Home Shred A — Thân trên & Lõi Đốt mỡ',
            splitType: 'HOME_SHRED',
            exerciseCodes: [
              'PUSH_UP',
              'INCLINE_DUMBBELL_PRESS',
              'ONE_ARM_DUMBBELL_ROW',
              'DUMBBELL_LATERAL_RAISE',
              'DUMBBELL_HAMMER_CURL',
              'PLANK',
            ],
          ),
          _SessionBlueprint(
            name: 'Home Shred B — Thân dưới & Bụng',
            splitType: 'HOME_SHRED',
            exerciseCodes: [
              'GOBLET_SQUAT',
              'WALKING_LUNGE',
              'OVERHEAD_DUMBBELL_TRICEP_EXT',
              'HANGING_LEG_RAISE',
              'PLANK',
            ],
          ),
          _SessionBlueprint(
            name: 'Home Shred C — Toàn thân Sức bền',
            splitType: 'HOME_SHRED',
            exerciseCodes: [
              'PUSH_UP',
              'ONE_ARM_DUMBBELL_ROW',
              'GOBLET_SQUAT',
              'DUMBBELL_SHOULDER_PRESS',
              'WALKING_LUNGE',
              'PLANK',
            ],
          ),
        ];
      case ProgramChoiceType.aiCustom:
        if (profile.sessionsPerWeek <= 3) {
          return const [
            _SessionBlueprint(
              name: 'AI Full Body A — Sức mạnh Nền tảng',
              splitType: 'FULL_BODY',
              exerciseCodes: [
                'BARBELL_SQUAT',
                'BARBELL_BENCH_PRESS',
                'LAT_PULLDOWN',
                'DUMBBELL_SHOULDER_PRESS',
                'PLANK',
              ],
            ),
            _SessionBlueprint(
              name: 'AI Full Body B — Kéo & Đùi sau',
              splitType: 'FULL_BODY',
              exerciseCodes: [
                'BARBELL_DEADLIFT',
                'INCLINE_DUMBBELL_PRESS',
                'ONE_ARM_DUMBBELL_ROW',
                'WALKING_LUNGE',
                'HANGING_LEG_RAISE',
              ],
            ),
            _SessionBlueprint(
              name: 'AI Full Body C — Thẩm mỹ & Lõi',
              splitType: 'FULL_BODY',
              exerciseCodes: [
                'GOBLET_SQUAT',
                'PUSH_UP',
                'SEATED_CABLE_ROW',
                'DUMBBELL_LATERAL_RAISE',
                'CABLE_CRUNCH',
              ],
            ),
          ];
        }
        if (profile.sessionsPerWeek == 4) {
          return const [
            _SessionBlueprint(
              name: 'AI Upper A — Ngực, Lưng & Vai',
              splitType: 'UPPER_LOWER',
              exerciseCodes: [
                'BARBELL_BENCH_PRESS',
                'BARBELL_BENT_OVER_ROW',
                'DUMBBELL_SHOULDER_PRESS',
                'LAT_PULLDOWN',
                'DUMBBELL_LATERAL_RAISE',
                'CABLE_TRICEP_PUSHDOWN',
              ],
            ),
            _SessionBlueprint(
              name: 'AI Lower A — Đùi trước & Lõi',
              splitType: 'UPPER_LOWER',
              exerciseCodes: [
                'BARBELL_SQUAT',
                'ROMANIAN_DEADLIFT',
                'LEG_PRESS',
                'LEG_EXTENSION',
                'SEATED_LEG_CURL',
                'PLANK',
              ],
            ),
            _SessionBlueprint(
              name: 'AI Upper B — Thân trên Phì đại',
              splitType: 'UPPER_LOWER',
              exerciseCodes: [
                'INCLINE_DUMBBELL_PRESS',
                'SEATED_CABLE_ROW',
                'CABLE_CHEST_FLY',
                'CABLE_FACE_PULL',
                'INCLINE_DUMBBELL_CURL',
                'OVERHEAD_DUMBBELL_TRICEP_EXT',
              ],
            ),
            _SessionBlueprint(
              name: 'AI Lower B — Mông, Đùi sau & Bụng',
              splitType: 'UPPER_LOWER',
              exerciseCodes: [
                'BARBELL_DEADLIFT',
                'BARBELL_HIP_THRUST',
                'WALKING_LUNGE',
                'LEG_CURL_MACHINE',
                'HANGING_LEG_RAISE',
              ],
            ),
          ];
        }
        return const [
          _SessionBlueprint(
            name: 'AI Push — Ngực, Vai & Tay sau',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'BARBELL_BENCH_PRESS',
              'INCLINE_DUMBBELL_PRESS',
              'DUMBBELL_SHOULDER_PRESS',
              'DUMBBELL_LATERAL_RAISE',
              'CABLE_CHEST_FLY',
              'CABLE_TRICEP_PUSHDOWN',
            ],
          ),
          _SessionBlueprint(
            name: 'AI Pull — Lưng Xô & Tay trước',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'BARBELL_DEADLIFT',
              'WIDE_GRIP_PULLUP',
              'BARBELL_BENT_OVER_ROW',
              'SEATED_CABLE_ROW',
              'CABLE_FACE_PULL',
              'BARBELL_BICEP_CURL',
            ],
          ),
          _SessionBlueprint(
            name: 'AI Legs — Chân, Mông & Lõi',
            splitType: 'PUSH_PULL_LEGS',
            exerciseCodes: [
              'BARBELL_SQUAT',
              'ROMANIAN_DEADLIFT',
              'BARBELL_HIP_THRUST',
              'WALKING_LUNGE',
              'SEATED_LEG_CURL',
              'HANGING_LEG_RAISE',
            ],
          ),
        ];
    }
  }

  static String? _resolveExerciseForLocation({
    required String targetCode,
    required TrainingLocation location,
    required Map<String, ExerciseModel> byCode,
    required List<ExerciseModel> allExercises,
    required List<String> alreadyPicked,
  }) {
    final direct = byCode[targetCode];
    if (direct != null &&
        isEquipmentAllowed(direct, location) &&
        !alreadyPicked.contains(targetCode)) {
      return targetCode;
    }
    if (direct == null) return null;

    // Thuat toan overlapRatio tim bai cung nhom co chinh phu hop dung cu hien co
    final targetPrimary = direct.primaryMuscles.toSet();
    final targetSecondary = direct.secondaryMuscles.toSet();
    ExerciseModel? best;
    var bestScore = -1.0;

    for (final cand in allExercises) {
      final candCode = cand.code.toUpperCase();
      if (alreadyPicked.contains(candCode)) continue;
      if (!isEquipmentAllowed(cand, location)) continue;

      final candPrimary = cand.primaryMuscles.toSet();
      final shared = targetPrimary.intersection(candPrimary);
      if (shared.isEmpty) continue;
      final denom = math.min(targetPrimary.length, candPrimary.length);
      final ratio = shared.length / (denom > 0 ? denom : 1);
      final secShared = targetSecondary.intersection(cand.secondaryMuscles.toSet()).length;
      final bundledBonus = cand.isBundled ? 0.05 : 0.0;
      final score = ratio + secShared * 0.08 + bundledBonus;
      if (score > bestScore) {
        bestScore = score;
        best = cand;
      }
    }

    return best?.code.toUpperCase();
  }

  static bool _blueprintMatchesPriority(
    _SessionBlueprint bp,
    PriorityMuscleGroup priority,
    Map<String, ExerciseModel> byCode,
  ) {
    final targetMats = priority.materialIds.toSet();
    for (final code in bp.exerciseCodes) {
      final ex = byCode[code.toUpperCase()];
      if (ex == null) continue;
      if (ex.primaryMuscles.any(targetMats.contains) ||
          ex.secondaryMuscles.any(targetMats.contains)) {
        return true;
      }
    }
    return false;
  }

  static String? _pickBonusExerciseForPriority({
    required PriorityMuscleGroup priority,
    required TrainingLocation location,
    required Map<String, ExerciseModel> byCode,
    required List<String> alreadyPicked,
  }) {
    final preferred = _priorityCandidates[priority] ?? const [];
    for (final code in preferred) {
      if (alreadyPicked.contains(code)) continue;
      final ex = byCode[code];
      if (ex != null && isEquipmentAllowed(ex, location)) {
        return code;
      }
    }
    final targetMats = priority.materialIds.toSet();
    for (final entry in byCode.entries) {
      if (alreadyPicked.contains(entry.key)) continue;
      if (!isEquipmentAllowed(entry.value, location)) continue;
      if (entry.value.primaryMuscles.any(targetMats.contains)) {
        return entry.key;
      }
    }
    return null;
  }

  static int _exerciseCountForDuration(int durationMin) {
    if (durationMin <= 35) return 4;
    if (durationMin <= 65) return 5;
    return 6;
  }

  static int _setsForExercise({
    required UserFitnessProfile profile,
    required bool isCompound,
    required int index,
  }) {
    var sets = 3;
    if (profile.sessionDurationMin > 65 && isCompound) {
      sets = 4;
    } else if (profile.sessionDurationMin > 35 && isCompound && index < 2) {
      sets = 4;
    }
    if (profile.experienceLevel == ExperienceLevel.beginner) {
      sets = math.min(sets, 3);
    } else if (profile.experienceLevel == ExperienceLevel.advanced && isCompound) {
      sets = math.min(sets + 1, 5);
    }
    return sets;
  }

  static (int, int) _repRangeForProfile(UserFitnessProfile profile) {
    if (profile.trainingLocation == TrainingLocation.bodyweightOnly) {
      return const (12, 20);
    }
    switch (profile.somatotype) {
      case Somatotype.ectomorph:
        return const (6, 10);
      case Somatotype.mesomorph:
        return const (8, 12);
      case Somatotype.endomorph:
        return const (10, 15);
    }
  }

  static ({int compoundSec, int isolationSec}) _restTimesForProfile(
    UserFitnessProfile profile,
  ) {
    int cSec;
    int iSec;
    switch (profile.somatotype) {
      case Somatotype.ectomorph:
        cSec = 150;
        iSec = 120;
      case Somatotype.mesomorph:
        cSec = 120;
        iSec = 90;
      case Somatotype.endomorph:
        cSec = 90;
        iSec = 60;
    }
    if (profile.sessionDurationMin <= 35) {
      cSec = math.min(cSec, 75);
      iSec = math.min(iSec, 60);
    }
    return (compoundSec: cSec, isolationSec: iSec);
  }
}
