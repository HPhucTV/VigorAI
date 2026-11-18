// [OWNER: M4] Dinh nghia bang cache AI Readiness & Nhat ky anh Progress cuc bo
import 'package:drift/drift.dart';

class AiReadinessCacheTable extends Table {
  TextColumn get targetDateIso => text()(); // YYYY-MM-DD
  RealColumn get readinessScore => real()();
  TextColumn get readinessLevel => text()();
  TextColumn get muscleFatigueMapJson => text()();
  TextColumn get weightRecommendationsJson => text()();
  TextColumn get insightsJson => text().withDefault(const Constant('[]'))();
  DateTimeColumn get cachedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {targetDateIso};
}

class LocalProgressPhotosTable extends Table {
  TextColumn get id => text()();
  TextColumn get localFilePath => text()(); // Luu cuc bo getApplicationDocumentsDirectory()/progress_photos/
  TextColumn get poseTag => text().withDefault(const Constant('FRONT'))();
  DateTimeColumn get capturedAt => dateTime()();

  @override
  Set<Column> get primaryKey => {id};
}
