// [LOCKED STUB - Gop 3 nhom bang Drift tu M1, M2, M4]
// Khong sua truc tiep file nay ngoai viec chay `dart run build_runner build`
import 'package:drift/drift.dart';

import 'ai_cache_tables.drift.dart';
import 'health_tables.drift.dart';
import 'workout_tables.drift.dart';

// Sau khi chay `dart run build_runner build`, bo comment dong duoi:
// part 'app_database.g.dart';

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
    // M4 tables
    AiReadinessCacheTable,
    LocalProgressPhotosTable,
  ],
)
class AppDatabaseSchemaStub {
  const AppDatabaseSchemaStub();
}
