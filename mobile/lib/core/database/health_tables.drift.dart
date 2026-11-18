// [OWNER: M1] Dinh nghia cac bang SQLite Drift cho phan he Suc khoe & Sinh trac
import 'package:drift/drift.dart';

class BiometricLogsTable extends Table {
  TextColumn get id => text()();
  FloatColumn get weightKg => real()();
  FloatColumn get bodyFatPct => real().nullable()();
  FloatColumn get muscleMassKg => real().nullable()();
  FloatColumn get bmi => real()();
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
