// [OWNER: M1] Cau noi Android Health Connect API (F02, F05)
class DailyHealthSnapshot {
  final int stepsCount;
  final double distanceKm;
  final int activeCaloriesKcal;
  final double sleepHours;

  const DailyHealthSnapshot({
    required this.stepsCount,
    required this.distanceKm,
    required this.activeCaloriesKcal,
    required this.sleepHours,
  });
}

class HealthConnectBridge {
  Future<bool> requestHealthPermissionsWithRationale() async {
    // Hoan thien tich hop package `health` trong Task T-M1-07
    return false;
  }

  Future<DailyHealthSnapshot> fetchTodaySnapshot() async {
    return const DailyHealthSnapshot(
      stepsCount: 0,
      distanceKm: 0.0,
      activeCaloriesKcal: 0,
      sleepHours: 0.0,
    );
  }
}
