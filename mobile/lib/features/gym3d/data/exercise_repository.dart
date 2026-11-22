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
    'BARBELL_SQUAT': 'assets/3d_bundled/barbell_squat.glb',
    'PUSH_UP': 'assets/3d_bundled/push_up.glb',
  };

  static bool _hasStaleUrl(String code, String url) {
    if (url.startsWith('http://localhost:9000') ||
        url.startsWith('https://cdn.vigorai.app')) {
      return true;
    }
    if (url.startsWith('assets/3d_bundled/') &&
        !_localBundledGlbs.containsKey(code.toUpperCase()) &&
        url != 'assets/3d_bundled/base_mannequin.glb') {
      return true;
    }
    return false;
  }

  static int _rowQualityScore(String id, String code, String url) {
    var score = 0;
    if (!_hasStaleUrl(code, url)) score += 4;
    if (!id.startsWith('ex-')) score += 2;
    if (url.startsWith('https://') || url.startsWith('assets/')) score += 1;
    return score;
  }

  /// Chon ban ghi uu tien nhat khi co nhieu dong cung ma `code` (tranh loi Bad state: Too many elements).
  static T pickPreferredByCode<T>(
    List<T> candidates, {
    required String Function(T item) idOf,
    required String Function(T item) codeOf,
    required String Function(T item) urlOf,
  }) {
    var best = candidates.first;
    var bestScore = _rowQualityScore(idOf(best), codeOf(best), urlOf(best));
    for (var i = 1; i < candidates.length; i++) {
      final cand = candidates[i];
      final score = _rowQualityScore(idOf(cand), codeOf(cand), urlOf(cand));
      if (score > bestScore) {
        best = cand;
        bestScore = score;
      }
    }
    return best;
  }

  /// Khu trung lap danh sach bai tap theo ma `code` (khong phan biet hoa/thuong).
  static List<T> deduplicateByCode<T>(
    Iterable<T> items, {
    required String Function(T item) idOf,
    required String Function(T item) codeOf,
    required String Function(T item) urlOf,
  }) {
    final grouped = <String, List<T>>{};
    for (final item in items) {
      grouped.putIfAbsent(codeOf(item).trim().toUpperCase(), () => []).add(item);
    }
    return grouped.values
        .map(
          (group) => pickPreferredByCode<T>(
            group,
            idOf: idOf,
            codeOf: codeOf,
            urlOf: urlOf,
          ),
        )
        .toList();
  }

  final AppDatabase _db;
  final Dio _dio;
  final bool _useMockApi;

  ExerciseRepository(this._db, this._dio, {bool? useMockApi})
      : _useMockApi = useMockApi ?? ApiEndpoints.useMockApi;

  Future<List<ExercisesTableData>> _cleanupDuplicateRows(
    List<ExercisesTableData> rawRows,
  ) async {
    if (rawRows.length <= 1) return rawRows;
    final grouped = <String, List<ExercisesTableData>>{};
    for (final row in rawRows) {
      grouped.putIfAbsent(row.code.trim().toUpperCase(), () => []).add(row);
    }

    final kept = <ExercisesTableData>[];
    final redundantIds = <String>[];
    for (final group in grouped.values) {
      if (group.length == 1) {
        kept.add(group.first);
        continue;
      }
      final preferred = pickPreferredByCode<ExercisesTableData>(
        group,
        idOf: (r) => r.id,
        codeOf: (r) => r.code,
        urlOf: (r) => r.model3dGlbUrl,
      );
      kept.add(preferred);
      for (final row in group) {
        if (row.id != preferred.id) {
          redundantIds.add(row.id);
        }
      }
    }

    if (redundantIds.isNotEmpty) {
      await (_db.delete(_db.exercisesTable)
            ..where((t) => t.id.isIn(redundantIds)))
          .go();
    }
    return kept;
  }

  ExerciseModel _applyBundledOverrides(
    ExerciseModel model,
    Map<String, ExerciseModel> mockByCode,
  ) {
    final upper = model.code.toUpperCase();
    final localPath = _localBundledGlbs[upper];
    final mockMeta = mockByCode[upper];
    if (localPath != null) {
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

    final staleUrl = _hasStaleUrl(upper, model.model3dGlbUrl);
    final resolvedUrl =
        (staleUrl && mockMeta != null) ? mockMeta.model3dGlbUrl : model.model3dGlbUrl;
    final resolvedChecksum =
        (staleUrl && mockMeta != null) ? mockMeta.assetChecksum : model.assetChecksum;
    final resolvedClips =
        model.clips.length >= 2 ? model.clips : (mockMeta?.clips ?? model.clips);

    return ExerciseModel(
      id: model.id,
      code: model.code,
      nameVi: model.nameVi,
      nameEn: model.nameEn,
      equipmentType: model.equipmentType,
      model3dGlbUrl: resolvedUrl,
      assetChecksum: resolvedChecksum,
      primaryMuscles: model.primaryMuscles,
      secondaryMuscles: model.secondaryMuscles,
      stabilizerMuscles: model.stabilizerMuscles,
      phaseKeyframes: model.phaseKeyframes,
      badFormWarnings: model.badFormWarnings,
      setupGuide: model.setupGuide,
      isBundled: false,
      clips: resolvedClips,
    );
  }

  Future<List<ExerciseModel>> loadExercises({bool forceRefresh = false}) async {
    final rawRows = await _db.select(_db.exercisesTable).get();
    final existingRows = await _cleanupDuplicateRows(rawRows);
    final mockList = await _loadFromMockAsset();
    final mockByCode = <String, ExerciseModel>{
      for (final m in mockList) m.code.toUpperCase(): m,
    };

    if (_useMockApi) {
      final existingByCode = {
        for (final r in existingRows) r.code.toUpperCase(): r,
      };
      final stale = existingRows.length != mockList.length ||
          mockList.any((m) {
            final row = existingByCode[m.code.toUpperCase()];
            return row == null ||
                row.assetChecksum != m.assetChecksum ||
                row.model3dGlbUrl != m.model3dGlbUrl ||
                row.nameVi != m.nameVi;
          });
      if (stale) {
        await _upsertExercises(mockList);
      }
      return mockList;
    }

    final hasStaleCache =
        existingRows.any((r) => _hasStaleUrl(r.code, r.model3dGlbUrl));
    final hasMockSeededRows = existingRows.any((r) => r.id.startsWith('ex-'));
    if (!forceRefresh &&
        !hasStaleCache &&
        !hasMockSeededRows &&
        existingRows.length >= mockList.length) {
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
    final normalized = code.trim().toUpperCase();
    final matchedRows = await (_db.select(_db.exercisesTable)
          ..where((t) => t.code.equals(normalized)))
        .get();
    if (matchedRows.isNotEmpty) {
      final preferred = matchedRows.length == 1
          ? matchedRows.first
          : pickPreferredByCode<ExercisesTableData>(
              matchedRows,
              idOf: (r) => r.id,
              codeOf: (r) => r.code,
              urlOf: (r) => r.model3dGlbUrl,
            );
      if (matchedRows.length > 1) {
        final redundantIds = matchedRows
            .where((r) => r.id != preferred.id)
            .map((r) => r.id)
            .toList();
        if (redundantIds.isNotEmpty) {
          await (_db.delete(_db.exercisesTable)
                ..where((t) => t.id.isIn(redundantIds)))
              .go();
        }
      }
      final mockList = await _loadFromMockAsset();
      final mockByCode = <String, ExerciseModel>{
        for (final m in mockList) m.code.toUpperCase(): m,
      };
      return _applyBundledOverrides(_rowToModel(preferred), mockByCode);
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
    final uniqueItems = deduplicateByCode<ExerciseModel>(
      items,
      idOf: (e) => e.id,
      codeOf: (e) => e.code,
      urlOf: (e) => e.model3dGlbUrl,
    );
    final incomingIdByCode = <String, String>{
      for (final item in uniqueItems) item.code.trim().toUpperCase(): item.id,
    };

    await _db.transaction(() async {
      final currentRows = await _db.select(_db.exercisesTable).get();
      final staleIds = <String>[];
      for (final row in currentRows) {
        final upper = row.code.trim().toUpperCase();
        final replacementId = incomingIdByCode[upper];
        if (replacementId != null && row.id != replacementId) {
          staleIds.add(row.id);
        }
      }
      if (staleIds.isNotEmpty) {
        await (_db.delete(_db.exercisesTable)
              ..where((t) => t.id.isIn(staleIds)))
            .go();
      }
      await _db.batch((batch) {
        for (final item in uniqueItems) {
          batch.insert(
            _db.exercisesTable,
            ExercisesTableCompanion.insert(
              id: item.id,
              code: item.code.trim().toUpperCase(),
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
    });
  }

  ExerciseModel _rowToModel(ExercisesTableData row) {
    final upper = row.code.toUpperCase();
    final bundled = _localBundledGlbs.containsKey(upper);
    final glbUrl = _localBundledGlbs[upper] ?? row.model3dGlbUrl;
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
