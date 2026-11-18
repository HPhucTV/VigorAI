// [OWNER: M2] Dinh nghia cac bang SQLite Drift cho Kho 3D & Thuc thi Buoi tap Gym
import 'package:drift/drift.dart';

class ExercisesTable extends Table {
  TextColumn get id => text()();
  TextColumn get code => text()();
  TextColumn get nameVi => text()();
  TextColumn get equipmentType => text()();
  TextColumn get model3dGlbUrl => text()();
  TextColumn get assetChecksum => text()();
  TextColumn get primaryMusclesJson => text()();
  TextColumn get secondaryMusclesJson => text().withDefault(const Constant('[]'))();
  TextColumn get stabilizerMusclesJson => text().withDefault(const Constant('[]'))();
  TextColumn get phaseKeyframesJson => text().withDefault(const Constant('{}'))();
  TextColumn get badFormWarningsJson => text().withDefault(const Constant('[]'))();

  @override
  Set<Column> get primaryKey => {id};
}

class WorkoutRoutinesTable extends Table {
  TextColumn get id => text()();
  TextColumn get name => text()();
  TextColumn get splitType => text()();
  TextColumn get scheduledWeekdaysJson => text().withDefault(const Constant('[]'))();
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
