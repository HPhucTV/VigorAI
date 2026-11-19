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

class ExerciseRepository {
  final AppDatabase _db;
  final Dio _dio;

  ExerciseRepository(this._db, this._dio);

  Future<List<ExerciseModel>> loadExercises({bool forceRefresh = false}) async {
    // 1. Khi chay Mock hoac offline-first chua co du lieu trong Drift -> nap tu mock_m2_exercises.json
    final existingRows = await _db.select(_db.exercisesTable).get();

    if (ApiEndpoints.useMockApi) {
      final mockList = await _loadFromMockAsset();
      if (existingRows.length != mockList.length) {
        await _upsertExercises(mockList);
      }
      return mockList;
    }

    if (!forceRefresh && existingRows.isNotEmpty) {
      return existingRows.map(_rowToModel).toList();
    }

    try {
      final response = await _dio.get<Map<String, dynamic>>(ApiEndpoints.exercises);
      final rawItems = (response.data?['items'] as List?) ?? const [];
      final remoteList = rawItems
          .map((e) => ExerciseModel.fromJson(e as Map<String, dynamic>))
          .toList();
      if (remoteList.isNotEmpty) {
        await _upsertExercises(remoteList);
        return remoteList;
      }
    } catch (_) {
      if (existingRows.isNotEmpty) {
        return existingRows.map(_rowToModel).toList();
      }
    }

    final fallback = await _loadFromMockAsset();
    await _upsertExercises(fallback);
    return fallback;
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
    final glbUrl = row.model3dGlbUrl;
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
