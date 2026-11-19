// [SHARED DATABASE - Gop 3 nhom bang Drift tu M1 & M2]
// Da mo khoa de sinh `app_database.g.dart` cho Offline-First SQLite (T-M1-03).
import 'dart:io';

import 'package:drift/drift.dart';
import 'package:drift/native.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

import 'ai_cache_tables.drift.dart';
import 'health_tables.drift.dart';
import 'workout_tables.drift.dart';

part 'app_database.g.dart';

@DriftDatabase(
  tables: [
    // M1 tables
    BiometricLogsTable,
    DailyHealthLogsTable,
    MealLogsTable,
    SupplementSchedulesTable,
    // M2 tables
    ExercisesTable,
    WorkoutRoutinesTable,
    WorkoutSessionsTable,
    WorkoutSetsTable,
    AiReadinessCacheTable,
    LocalProgressPhotosTable,
  ],
)
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  AppDatabase.forTesting(super.e);

  @override
  int get schemaVersion => 1;

  /// Xoa sach toan bo du lieu SQLite cuc bo khi nguoi dung Xoa tai khoan vinh vien (F26).
  Future<void> clearAllLocalData() async {
    await transaction(() async {
      for (final table in allTables) {
        await delete(table).go();
      }
    });
  }
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'vigorai.sqlite'));
    return NativeDatabase.createInBackground(file);
  });
}

final appDatabaseProvider = Provider<AppDatabase>((ref) {
  final db = AppDatabase();
  ref.onDispose(db.close);
  return db;
});
