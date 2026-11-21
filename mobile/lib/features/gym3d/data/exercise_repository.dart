// [OWNER: M2] Offline-First Exercise Repository doc Drift / Mock JSON / FastAPI (T-M2-03 / F07)
import 'dart:convert';

import 'package:dio/dio.dart';
import 'package:drift/drift.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/database/app_database.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/network/api_endpoints.dart';
import '../../../core/network/dio_client.dart';
import '../presentation/widgets/muscle_3d_viewer_widget.dart';

class ExerciseRepository {
  static const Map<String, String> _localBundledGlbs = {
    'BARBELL_BENCH_PRESS': 'assets/3d_bundled/barbell_bench_press.glb',
    'INCLINE_DUMBBELL_PRESS': 'assets/3d_bundled/incline_dumbbell_press.glb',
    'CABLE_CHEST_FLY': 'assets/3d_bundled/cable_chest_fly.glb',
    'WIDE_GRIP_PULLUP': 'assets/3d_bundled/wide_grip_pullup.glb',
    'LAT_PULLDOWN': 'assets/3d_bundled/lat_pulldown.glb',
    'STRAIGHT_ARM_CABLE_PULLDOWN': 'assets/3d_bundled/straight_arm_cable_pulldown.glb',
    'BARBELL_BENT_OVER_ROW': 'assets/3d_bundled/barbell_bent_over_row.glb',
    'SEATED_CABLE_ROW': 'assets/3d_bundled/seated_cable_row.glb',
    'BARBELL_DEADLIFT': 'assets/3d_bundled/barbell_deadlift.glb',
    'DUMBBELL_SHOULDER_PRESS': 'assets/3d_bundled/dumbbell_shoulder_press.glb',
    'DUMBBELL_LATERAL_RAISE': 'assets/3d_bundled/dumbbell_lateral_raise.glb',
    'CABLE_FACE_PULL': 'assets/3d_bundled/cable_face_pull.glb',
    'BARBELL_BICEP_CURL': 'assets/3d_bundled/barbell_bicep_curl.glb',
    'DUMBBELL_HAMMER_CURL': 'assets/3d_bundled/dumbbell_hammer_curl.glb',
    'INCLINE_DUMBBELL_CURL': 'assets/3d_bundled/incline_dumbbell_curl.glb',
    'CABLE_TRICEP_PUSHDOWN': 'assets/3d_bundled/cable_tricep_pushdown.glb',
    'SKULL_CRUSHER': 'assets/3d_bundled/skull_crusher.glb',
    'OVERHEAD_DUMBBELL_TRICEP_EXT': 'assets/3d_bundled/overhead_dumbbell_tricep_ext.glb',
    'BARBELL_SQUAT': 'assets/3d_bundled/barbell_squat.glb',
    'LEG_PRESS': 'assets/3d_bundled/leg_press.glb',
    'LEG_EXTENSION': 'assets/3d_bundled/leg_extension.glb',
    'ROMANIAN_DEADLIFT': 'assets/3d_bundled/romanian_deadlift.glb',
    'LEG_CURL_MACHINE': 'assets/3d_bundled/leg_curl_machine.glb',
    'SEATED_LEG_CURL': 'assets/3d_bundled/seated_leg_curl.glb',
    'BARBELL_HIP_THRUST': 'assets/3d_bundled/barbell_hip_thrust.glb',
    'WALKING_LUNGE': 'assets/3d_bundled/walking_lunge.glb',
    'CABLE_GLUTE_KICKBACK': 'assets/3d_bundled/cable_glute_kickback.glb',
    'HANGING_LEG_RAISE': 'assets/3d_bundled/hanging_leg_raise.glb',
    'CABLE_CRUNCH': 'assets/3d_bundled/cable_crunch.glb',
    'PLANK': 'assets/3d_bundled/plank.glb',
    'PUSH_UP': 'assets/3d_bundled/push_up.glb',
  };

  final AppDatabase _db;
  final Dio _dio;

  ExerciseRepository(this._db, this._dio);

  ExerciseModel _applyBundledOverrides(
    ExerciseModel model,
    Map<String, ExerciseModel> mockByCode,
  ) {
    final upper = model.code.toUpperCase();
    final localPath = _localBundledGlbs[upper];
    if (localPath == null) return model;
    final mockMeta = mockByCode[upper];
    return ExerciseModel(
      id: model.id,
      code: model.code,
      nameVi: mockMeta?.nameVi ?? model.nameVi,
      nameEn: mockMeta?.nameEn ?? model.nameEn,
      equipmentType: model.equipmentType,
      model3dGlbUrl: localPath,
      assetChecksum: mockMeta?.assetChecksum ?? model.assetChecksum,
      primaryMuscles: model.primaryMuscles,
      secondaryMuscles: model.secondaryMuscles,
      stabilizerMuscles: model.stabilizerMuscles,
      phaseKeyframes: model.phaseKeyframes,
      badFormWarnings: model.badFormWarnings,
      setupGuide: model.setupGuide,
      isBundled: true,
      clips: const ['Anim_GoodForm', 'Anim_BadForm'],
    );
  }

  Future<List<ExerciseModel>> loadExercises({bool forceRefresh = false}) async {
    final existingRows = await _db.select(_db.exercisesTable).get();
    final mockList = await _loadFromMockAsset();
    final mockByCode = <String, ExerciseModel>{
      for (final m in mockList) m.code.toUpperCase(): m,
    };

    if (ApiEndpoints.useMockApi) {
      if (existingRows.length != mockList.length) {
        await _upsertExercises(mockList);
      }
      return mockList;
    }

    if (!forceRefresh && existingRows.length >= mockList.length) {
      return existingRows
          .map(_rowToModel)
          .map((e) => _applyBundledOverrides(e, mockByCode))
          .toList();
    }

    try {
      final response = await _dio.get<Map<String, dynamic>>(ApiEndpoints.exercises);
      final rawItems = (response.data?['items'] as List?) ?? const [];
      final remoteList = rawItems
          .map((e) => _applyBundledOverrides(
                ExerciseModel.fromJson(e as Map<String, dynamic>),
                mockByCode,
              ))
          .toList();
      if (remoteList.isNotEmpty) {
        final mergedByCode = <String, ExerciseModel>{
          for (final m in mockList) m.code.toUpperCase(): m,
          for (final r in remoteList) r.code.toUpperCase(): r,
        };
        final merged = mergedByCode.values.toList();
        await _upsertExercises(merged);
        return merged;
      }
    } catch (_) {
      if (existingRows.isNotEmpty) {
        return existingRows
            .map(_rowToModel)
            .map((e) => _applyBundledOverrides(e, mockByCode))
            .toList();
      }
    }

    await _upsertExercises(mockList);
    return mockList;
  }

  Future<ExerciseModel?> getExerciseByCode(String code) async {
    final normalized = code.toUpperCase();
    final row = await (_db.select(_db.exercisesTable)
          ..where((t) => t.code.equals(normalized)))
        .getSingleOrNull();
    if (row != null) {
      return _rowToModel(row);
    }
    final all = await loadExercises();
    for (final ex in all) {
      if (ex.code.toUpperCase() == normalized) return ex;
    }
    return null;
  }

  Future<List<ExerciseModel>> _loadFromMockAsset() async {
    final raw =
        await rootBundle.loadString('assets/mock_json/mock_m2_exercises.json');
    final decoded = jsonDecode(raw) as Map<String, dynamic>;
    final list = (decoded['exercises'] as List?) ?? const [];
    return list
        .map((e) => ExerciseModel.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  Future<void> _upsertExercises(List<ExerciseModel> items) async {
    await _db.batch((batch) {
      for (final item in items) {
        batch.insert(
          _db.exercisesTable,
          ExercisesTableCompanion.insert(
            id: item.id,
            code: item.code,
            nameVi: item.nameVi,
            nameEn: Value(item.nameEn),
            equipmentType: item.equipmentType,
            model3dGlbUrl: item.model3dGlbUrl,
            assetChecksum: item.assetChecksum,
            primaryMusclesJson: jsonEncode(item.primaryMuscles),
            secondaryMusclesJson: Value(jsonEncode(item.secondaryMuscles)),
            stabilizerMusclesJson: Value(jsonEncode(item.stabilizerMuscles)),
            phaseKeyframesJson: Value(jsonEncode(item.phaseKeyframes.toJson())),
            badFormWarningsJson: Value(jsonEncode(item.badFormWarnings)),
            setupGuideJson: Value(jsonEncode(item.setupGuide)),
          ),
          mode: InsertMode.insertOrReplace,
        );
      }
    });
  }

  ExerciseModel _rowToModel(ExercisesTableData row) {
    final glbUrl = _localBundledGlbs[row.code.toUpperCase()] ?? row.model3dGlbUrl;
    final bundled = glbUrl.startsWith('assets/');
    return ExerciseModel(
      id: row.id,
      code: row.code,
      nameVi: row.nameVi,
      nameEn: row.nameEn,
      equipmentType: row.equipmentType,
      model3dGlbUrl: glbUrl,
      assetChecksum: row.assetChecksum,
      primaryMuscles:
          (jsonDecode(row.primaryMusclesJson) as List).cast<String>(),
      secondaryMuscles:
          (jsonDecode(row.secondaryMusclesJson) as List).cast<String>(),
      stabilizerMuscles:
          (jsonDecode(row.stabilizerMusclesJson) as List).cast<String>(),
      phaseKeyframes: ExercisePhaseKeyframes.fromJson(
        jsonDecode(row.phaseKeyframesJson) as Map<String, dynamic>,
      ),
      badFormWarnings:
          (jsonDecode(row.badFormWarningsJson) as List).cast<String>(),
      setupGuide: jsonDecode(row.setupGuideJson) as Map<String, dynamic>,
      isBundled: bundled,
      clips: bundled
          ? const ['Anim_GoodForm', 'Anim_BadForm']
          : const ['Anim_GoodForm'],
    );
  }
}

final bodyAvatarPresetProvider = StateProvider<BodyAvatarPreset>(
  (ref) => BodyAvatarPreset.maleFit,
);

final exerciseRepositoryProvider = Provider<ExerciseRepository>((ref) {
  final db = ref.watch(appDatabaseProvider);
  final dio = ref.watch(dioProvider);
  return ExerciseRepository(db, dio);
});

final exercisesListProvider = FutureProvider<List<ExerciseModel>>((ref) async {
  return ref.watch(exerciseRepositoryProvider).loadExercises();
});

final exerciseByCodeProvider =
    FutureProvider.family<ExerciseModel?, String>((ref, code) async {
  return ref.watch(exerciseRepositoryProvider).getExerciseByCode(code);
});
