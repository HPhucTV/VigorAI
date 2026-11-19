// [OWNER: M2] Bang SQLite Drift + Domain Entities Offline-First cho Kho 3D & Tap Gym (T-M2-04)
import 'dart:convert';

import 'package:drift/drift.dart';

// ============================================================================
// 1. DRIFT TABLE DEFINITIONS (Dung chung trong app_database.dart)
// ============================================================================

class ExercisesTable extends Table {
  TextColumn get id => text()();
  TextColumn get code => text()();
  TextColumn get nameVi => text()();
  TextColumn get nameEn => text().withDefault(const Constant(''))();
  TextColumn get equipmentType => text()();
  TextColumn get model3dGlbUrl => text()();
  TextColumn get assetChecksum => text()();
  TextColumn get primaryMusclesJson => text()();
  TextColumn get secondaryMusclesJson => text().withDefault(const Constant('[]'))();
  TextColumn get stabilizerMusclesJson => text().withDefault(const Constant('[]'))();
  TextColumn get phaseKeyframesJson => text().withDefault(const Constant('{}'))();
  TextColumn get badFormWarningsJson => text().withDefault(const Constant('[]'))();
  TextColumn get setupGuideJson => text().withDefault(const Constant('{}'))();

  @override
  Set<Column> get primaryKey => {id};
}

class WorkoutRoutinesTable extends Table {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get splitType => text()();
  TextColumn get scheduledWeekdaysJson => text().withDefault(const Constant('[]'))();
  TextColumn get exercisesJson => text().withDefault(const Constant('[]'))();
  BoolColumn get isTemplate => boolean().withDefault(const Constant(false))();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

class WorkoutSessionsTable extends Table {
  TextColumn get id => text()();
  TextColumn get routineId => text().nullable()();
  TextColumn get sessionTitle => text()();
  DateTimeColumn get startedAt => dateTime()();
  DateTimeColumn get completedAt => dateTime().nullable()();
  IntColumn get durationSeconds => integer().withDefault(const Constant(0))();
  RealColumn get totalVolumeKg => real().withDefault(const Constant(0.0))();
  TextColumn get status => text().withDefault(const Constant('IN_PROGRESS'))();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();
  DateTimeColumn get deletedAt => dateTime().nullable()();

  @override
  Set<Column> get primaryKey => {id};
}

class WorkoutSetsTable extends Table {
  TextColumn get id => text()();
  TextColumn get sessionId => text()();
  TextColumn get exerciseId => text()();
  IntColumn get setNumber => integer()();
  TextColumn get setType => text().withDefault(const Constant('NORMAL'))();
  RealColumn get weightKg => real()();
  IntColumn get reps => integer()();
  RealColumn get rpe => real().nullable()();
  RealColumn get estimated1rm => real().withDefault(const Constant(0.0))();
  BoolColumn get isPr => boolean().withDefault(const Constant(false))();
  DateTimeColumn get completedAt => dateTime()();
  TextColumn get syncStatus => text().withDefault(const Constant('PENDING_CREATE'))();
  DateTimeColumn get updatedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================================
// 2. DOMAIN ENTITIES (Khớp 100% Backend FastAPI M3 & Blender MCP Spec)
// ============================================================================

class PhaseWindowModel {
  final double start;
  final double end;
  final String breath;

  const PhaseWindowModel({
    required this.start,
    required this.end,
    required this.breath,
  });

  factory PhaseWindowModel.fromDynamic(
    dynamic raw, {
    required double fallbackStart,
    required double fallbackEnd,
    required String defaultBreath,
    double totalFrames = 100.0,
  }) {
    if (raw is Map<String, dynamic>) {
      return PhaseWindowModel(
        start: (raw['start'] as num?)?.toDouble() ?? fallbackStart,
        end: (raw['end'] as num?)?.toDouble() ?? fallbackEnd,
        breath: (raw['breath'] as String?) ?? defaultBreath,
      );
    }
    if (raw is List && raw.length >= 2) {
      final f0 = (raw[0] as num).toDouble();
      final f1 = (raw[1] as num).toDouble();
      final denom = totalFrames > 0 ? totalFrames : 100.0;
      return PhaseWindowModel(
        start: (f0 / denom).clamp(0.0, 1.0),
        end: (f1 / denom).clamp(0.0, 1.0),
        breath: defaultBreath,
      );
    }
    return PhaseWindowModel(
      start: fallbackStart,
      end: fallbackEnd,
      breath: defaultBreath,
    );
  }

  Map<String, dynamic> toJson() => {
        'start': start,
        'end': end,
        'breath': breath,
      };
}

class ExercisePhaseKeyframes {
  final PhaseWindowModel eccentric;
  final PhaseWindowModel isometric;
  final PhaseWindowModel concentric;

  const ExercisePhaseKeyframes({
    this.eccentric = const PhaseWindowModel(start: 0.0, end: 0.45, breath: 'Hít vào'),
    this.isometric = const PhaseWindowModel(start: 0.45, end: 0.55, breath: 'Giữ lõi'),
    this.concentric = const PhaseWindowModel(start: 0.55, end: 1.0, breath: 'Thở ra'),
  });

  factory ExercisePhaseKeyframes.fromJson(Map<String, dynamic>? json) {
    if (json == null || json.isEmpty) {
      return const ExercisePhaseKeyframes();
    }
    double totalFrames = 100.0;
    final rawConc = json['concentric'];
    if (rawConc is List && rawConc.length >= 2) {
      final last = (rawConc[1] as num).toDouble();
      if (last > 1.0) totalFrames = last;
    }
    return ExercisePhaseKeyframes(
      eccentric: PhaseWindowModel.fromDynamic(
        json['eccentric'],
        fallbackStart: 0.0,
        fallbackEnd: 0.45,
        defaultBreath: 'Hít vào',
        totalFrames: totalFrames,
      ),
      isometric: PhaseWindowModel.fromDynamic(
        json['isometric'],
        fallbackStart: 0.45,
        fallbackEnd: 0.55,
        defaultBreath: 'Giữ lõi',
        totalFrames: totalFrames,
      ),
      concentric: PhaseWindowModel.fromDynamic(
        json['concentric'],
        fallbackStart: 0.55,
        fallbackEnd: 1.0,
        defaultBreath: 'Thở ra',
        totalFrames: totalFrames,
      ),
    );
  }

  Map<String, dynamic> toJson() => {
        'eccentric': eccentric.toJson(),
        'isometric': isometric.toJson(),
        'concentric': concentric.toJson(),
      };
}

class ExerciseModel {
  final String id;
  final String code;
  final String nameVi;
  final String nameEn;
  final String equipmentType;
  final String model3dGlbUrl;
  final String assetChecksum;
  final List<String> primaryMuscles;
  final List<String> secondaryMuscles;
  final List<String> stabilizerMuscles;
  final ExercisePhaseKeyframes phaseKeyframes;
  final List<String> badFormWarnings;
  final Map<String, dynamic> setupGuide;
  final bool isBundled;
  final List<String> clips;

  const ExerciseModel({
    required this.id,
    required this.code,
    required this.nameVi,
    this.nameEn = '',
    required this.equipmentType,
    required this.model3dGlbUrl,
    required this.assetChecksum,
    required this.primaryMuscles,
    this.secondaryMuscles = const [],
    this.stabilizerMuscles = const [],
    this.phaseKeyframes = const ExercisePhaseKeyframes(),
    this.badFormWarnings = const [],
    this.setupGuide = const {},
    this.isBundled = false,
    this.clips = const ['Anim_GoodForm'],
  });

  bool get hasBadFormClip => clips.contains('Anim_BadForm') || isBundled;

  factory ExerciseModel.fromJson(Map<String, dynamic> json) {
    final code = json['code'] as String;
    final glbUrl = (json['model_3d_glb_url'] as String?) ??
        'assets/3d_bundled/${code.toLowerCase()}.glb';
    final bundled = (json['bundled'] as bool?) ?? glbUrl.startsWith('assets/');
    final rawClips = (json['clips'] as List?)?.cast<String>();
    return ExerciseModel(
      id: (json['id'] as String?) ?? 'ex-${code.toLowerCase()}',
      code: code,
      nameVi: (json['name_vi'] as String?) ?? code,
      nameEn: (json['name_en'] as String?) ?? '',
      equipmentType: (json['equipment_type'] as String?) ?? 'BODYWEIGHT',
      model3dGlbUrl: glbUrl,
      assetChecksum: (json['asset_checksum'] as String?) ?? '',
      primaryMuscles:
          ((json['primary_muscles'] as List?) ?? const []).cast<String>(),
      secondaryMuscles:
          ((json['secondary_muscles'] as List?) ?? const []).cast<String>(),
      stabilizerMuscles:
          ((json['stabilizer_muscles'] as List?) ?? const []).cast<String>(),
      phaseKeyframes: ExercisePhaseKeyframes.fromJson(
        json['phase_keyframes'] as Map<String, dynamic>?,
      ),
      badFormWarnings:
          ((json['bad_form_warnings'] as List?) ?? const []).cast<String>(),
      setupGuide: (json['setup_guide'] as Map<String, dynamic>?) ?? const {},
      isBundled: bundled,
      clips: rawClips ??
          (bundled ? const ['Anim_GoodForm', 'Anim_BadForm'] : const ['Anim_GoodForm']),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'code': code,
        'name_vi': nameVi,
        'name_en': nameEn,
        'equipment_type': equipmentType,
        'model_3d_glb_url': model3dGlbUrl,
        'asset_checksum': assetChecksum,
        'primary_muscles': primaryMuscles,
        'secondary_muscles': secondaryMuscles,
        'stabilizer_muscles': stabilizerMuscles,
        'phase_keyframes': phaseKeyframes.toJson(),
        'bad_form_warnings': badFormWarnings,
        'setup_guide': setupGuide,
        'bundled': isBundled,
        'clips': clips,
      };
}

class RoutineExerciseItem {
  final String exerciseCode;
  final int orderIndex;
  final int? supersetGroupId;
  final int targetSets;
  final int targetRepMin;
  final int targetRepMax;
  final int defaultRestSeconds;

  const RoutineExerciseItem({
    required this.exerciseCode,
    required this.orderIndex,
    this.supersetGroupId,
    this.targetSets = 3,
    this.targetRepMin = 8,
    this.targetRepMax = 12,
    this.defaultRestSeconds = 90,
  });

  factory RoutineExerciseItem.fromJson(Map<String, dynamic> json) {
    return RoutineExerciseItem(
      exerciseCode: json['exercise_code'] as String,
      orderIndex: (json['order_index'] as num?)?.toInt() ?? 0,
      supersetGroupId: (json['superset_group_id'] as num?)?.toInt(),
      targetSets: (json['target_sets'] as num?)?.toInt() ?? 3,
      targetRepMin: (json['target_rep_min'] as num?)?.toInt() ?? 8,
      targetRepMax: (json['target_rep_max'] as num?)?.toInt() ?? 12,
      defaultRestSeconds: (json['default_rest_seconds'] as num?)?.toInt() ?? 90,
    );
  }

  Map<String, dynamic> toJson() => {
        'exercise_code': exerciseCode,
        'order_index': orderIndex,
        'superset_group_id': supersetGroupId,
        'target_sets': targetSets,
        'target_rep_min': targetRepMin,
        'target_rep_max': targetRepMax,
        'default_rest_seconds': defaultRestSeconds,
      };
}

class WorkoutRoutineModel {
  final String id;
  final String name;
  final String splitType;
  final List<int> scheduledWeekdays;
  final List<RoutineExerciseItem> exercises;
  final bool isTemplate;
  final String syncStatus;
  final DateTime updatedAt;
  final DateTime? deletedAt;

  const WorkoutRoutineModel({
    required this.id,
    required this.name,
    required this.splitType,
    this.scheduledWeekdays = const [],
    this.exercises = const [],
    this.isTemplate = false,
    this.syncStatus = 'PENDING_CREATE',
    required this.updatedAt,
    this.deletedAt,
  });

  factory WorkoutRoutineModel.fromJson(Map<String, dynamic> json) {
    return WorkoutRoutineModel(
      id: json['id'] as String,
      name: json['name'] as String,
      splitType: (json['split_type'] as String?) ?? 'CUSTOM',
      scheduledWeekdays:
          ((json['scheduled_weekdays'] as List?) ?? const []).map((e) => (e as num).toInt()).toList(),
      exercises: ((json['exercises'] as List?) ?? const [])
          .map((e) => RoutineExerciseItem.fromJson(e as Map<String, dynamic>))
          .toList(),
      isTemplate: (json['is_template'] as bool?) ?? false,
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String).toUtc()
          : DateTime.now().toUtc(),
      deletedAt: json['deleted_at'] != null
          ? DateTime.parse(json['deleted_at'] as String).toUtc()
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'split_type': splitType,
        'scheduled_weekdays': scheduledWeekdays,
        'exercises': exercises.map((e) => e.toJson()).toList(),
        'is_template': isTemplate,
        'sync_status': syncStatus,
        'updated_at': updatedAt.toUtc().toIso8601String(),
        'deleted_at': deletedAt?.toUtc().toIso8601String(),
      };
}

class WorkoutSessionModel {
  final String id;
  final String? routineId;
  final String sessionTitle;
  final DateTime startedAt;
  final DateTime? completedAt;
  final int durationSeconds;
  final double totalVolumeKg;
  final String status;
  final String syncStatus;
  final DateTime updatedAt;
  final DateTime? deletedAt;

  const WorkoutSessionModel({
    required this.id,
    this.routineId,
    required this.sessionTitle,
    required this.startedAt,
    this.completedAt,
    this.durationSeconds = 0,
    this.totalVolumeKg = 0.0,
    this.status = 'IN_PROGRESS',
    this.syncStatus = 'PENDING_CREATE',
    required this.updatedAt,
    this.deletedAt,
  });

  factory WorkoutSessionModel.fromJson(Map<String, dynamic> json) {
    return WorkoutSessionModel(
      id: json['id'] as String,
      routineId: json['routine_id'] as String?,
      sessionTitle: json['session_title'] as String,
      startedAt: DateTime.parse(json['started_at'] as String).toUtc(),
      completedAt: json['completed_at'] != null
          ? DateTime.parse(json['completed_at'] as String).toUtc()
          : null,
      durationSeconds: (json['duration_seconds'] as num?)?.toInt() ?? 0,
      totalVolumeKg: (json['total_volume_kg'] as num?)?.toDouble() ?? 0.0,
      status: (json['status'] as String?) ?? 'IN_PROGRESS',
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String).toUtc()
          : DateTime.now().toUtc(),
      deletedAt: json['deleted_at'] != null
          ? DateTime.parse(json['deleted_at'] as String).toUtc()
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'routine_id': routineId,
        'session_title': sessionTitle,
        'started_at': startedAt.toUtc().toIso8601String(),
        'completed_at': completedAt?.toUtc().toIso8601String(),
        'duration_seconds': durationSeconds,
        'total_volume_kg': totalVolumeKg,
        'status': status,
        'sync_status': syncStatus,
        'updated_at': updatedAt.toUtc().toIso8601String(),
        'deleted_at': deletedAt?.toUtc().toIso8601String(),
      };
}

class WorkoutSetModel {
  final String id;
  final String sessionId;
  final String exerciseId;
  final int setNumber;
  final String setType;
  final double weightKg;
  final int reps;
  final double? rpe;
  final double estimated1rm;
  final bool isPr;
  final DateTime completedAt;
  final String syncStatus;
  final DateTime updatedAt;

  const WorkoutSetModel({
    required this.id,
    required this.sessionId,
    required this.exerciseId,
    required this.setNumber,
    this.setType = 'NORMAL',
    required this.weightKg,
    required this.reps,
    this.rpe,
    this.estimated1rm = 0.0,
    this.isPr = false,
    required this.completedAt,
    this.syncStatus = 'PENDING_CREATE',
    required this.updatedAt,
  });

  factory WorkoutSetModel.fromJson(Map<String, dynamic> json) {
    return WorkoutSetModel(
      id: json['id'] as String,
      sessionId: json['session_id'] as String,
      exerciseId: json['exercise_id'] as String,
      setNumber: (json['set_number'] as num).toInt(),
      setType: (json['set_type'] as String?) ?? 'NORMAL',
      weightKg: (json['weight_kg'] as num).toDouble(),
      reps: (json['reps'] as num).toInt(),
      rpe: (json['rpe'] as num?)?.toDouble(),
      estimated1rm: (json['estimated_1rm'] as num?)?.toDouble() ?? 0.0,
      isPr: (json['is_pr'] as bool?) ?? false,
      completedAt: DateTime.parse(json['completed_at'] as String).toUtc(),
      syncStatus: (json['sync_status'] as String?) ?? 'SYNCED',
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String).toUtc()
          : DateTime.now().toUtc(),
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'session_id': sessionId,
        'exercise_id': exerciseId,
        'set_number': setNumber,
        'set_type': setType,
        'weight_kg': weightKg,
        'reps': reps,
        'rpe': rpe,
        'estimated_1rm': estimated1rm,
        'is_pr': isPr,
        'completed_at': completedAt.toUtc().toIso8601String(),
        'sync_status': syncStatus,
        'updated_at': updatedAt.toUtc().toIso8601String(),
      };
}

String encodeJsonSafe(Object value) => jsonEncode(value);
