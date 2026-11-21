// [OWNER: M2] Thuat toan Thuan Dart: 1RM (Epley/Brzycki), Progressive Overload, Barbell Plate Calculator & Volume (T-M2-09 / F15, F17, F18, F22)
import '../../../core/database/workout_tables.drift.dart';

class OverloadSuggestion {
  final String action; // INCREASE | MAINTAIN
  final double suggestedWeightKg;
  final String reason;

  const OverloadSuggestion({
    required this.action,
    required this.suggestedWeightKg,
    required this.reason,
  });
}

class PlateCalculationResult {
  final double targetWeightKg;
  final double barWeightKg;
  final List<double> perSidePlates;
  final double achievedWeightKg;
  final double remainderPerSideKg;
  final bool isExact;
  final double? nearestLowerKg;
  final double? nearestHigherKg;
  final String? warningMessage;

  const PlateCalculationResult({
    required this.targetWeightKg,
    required this.barWeightKg,
    required this.perSidePlates,
    required this.achievedWeightKg,
    required this.remainderPerSideKg,
    required this.isExact,
    this.nearestLowerKg,
    this.nearestHigherKg,
    this.warningMessage,
  });

  double get perSideTotalKg => (achievedWeightKg - barWeightKg) / 2.0;

  Map<double, int> get plateCounts {
    final counts = <double, int>{};
    for (final plate in perSidePlates) {
      counts[plate] = (counts[plate] ?? 0) + 1;
    }
    return counts;
  }
}

class WorkoutCalculators {
  WorkoutCalculators._();

  static const List<double> standardPlatesKg = [
    20.0,
    15.0,
    10.0,
    5.0,
    2.5,
    1.25,
  ];

  static double _round1(double v) => (v * 10.0).round() / 10.0;
  static double _round2(double v) => (v * 100.0).round() / 100.0;

  /// Uoc tinh 1RM chuan khoa hoc Epley (1985) & Brzycki (1993) (F17).
  /// - Reps == 1: 1RM = W
  /// - 2 <= Reps <= 10: Trung binh cong Epley va Brzycki
  /// - Reps > 10: Epley
  static double calculateEstimated1Rm(double weightKg, int reps) {
    if (weightKg <= 0 || reps <= 0) return 0.0;
    if (reps == 1) return _round2(weightKg);
    final epley = weightKg * (1.0 + reps / 30.0);
    if (reps <= 10) {
      final brzycki = weightKg * (36.0 / (37.0 - reps));
      return _round2((epley + brzycki) / 2.0);
    }
    return _round2(epley);
  }

  /// De xuat tang tien tai trong co ban (F17).
  static OverloadSuggestion suggestBasicOverload({
    required double lastWeightKg,
    required int completedReps,
    required int targetRepMax,
    required double avgRpe,
    bool isLowerBody = false,
  }) {
    if (lastWeightKg <= 0) {
      return const OverloadSuggestion(
        action: 'MAINTAIN',
        suggestedWeightKg: 20.0,
        reason: 'Chưa có lịch sử trước đó — bắt đầu với thanh đòn chuẩn 20 kg.',
      );
    }
    if (completedReps >= targetRepMax && avgRpe <= 8.0) {
      final increment = isLowerBody ? 5.0 : 2.5;
      return OverloadSuggestion(
        action: 'INCREASE',
        suggestedWeightKg: _round1(lastWeightKg + increment),
        reason:
            'Đã đạt đỉnh $targetRepMax reps với RPE ${avgRpe.toStringAsFixed(1)} ≤ 8.0 — gợi ý tăng +$increment kg.',
      );
    }
    return OverloadSuggestion(
      action: 'MAINTAIN',
      suggestedWeightKg: _round1(lastWeightKg),
      reason: 'Giữ nguyên mức tạ để hoàn thiện kỹ thuật và đủ biên độ rep.',
    );
  }

  /// Thuat toan Tham lam tinh banh ta moi ben thanh don (F18).
  static PlateCalculationResult calculateBarbellPlates({
    required double targetWeightKg,
    double barWeightKg = 20.0,
    List<double> availablePlates = standardPlatesKg,
  }) {
    final sortedPlates = List<double>.from(availablePlates)
      ..sort((a, b) => b.compareTo(a));

    if (targetWeightKg < barWeightKg) {
      return PlateCalculationResult(
        targetWeightKg: targetWeightKg,
        barWeightKg: barWeightKg,
        perSidePlates: const [],
        achievedWeightKg: barWeightKg,
        remainderPerSideKg: 0.0,
        isExact: false,
        nearestLowerKg: barWeightKg,
        nearestHigherKg: barWeightKg,
        warningMessage:
            'Mức tạ mục tiêu nhỏ hơn trọng lượng thanh đòn (${_round2(barWeightKg)} kg).',
      );
    }

    final targetCents = (targetWeightKg * 100.0).round();
    final barCents = (barWeightKg * 100.0).round();
    var remainingSideCents = ((targetCents - barCents) / 2.0).round();
    final chosen = <double>[];

    for (final plate in sortedPlates) {
      final plateCents = (plate * 100.0).round();
      if (plateCents <= 0) continue;
      while (remainingSideCents >= plateCents) {
        chosen.add(plate);
        remainingSideCents -= plateCents;
      }
    }

    final chosenSideCents =
        chosen.fold<int>(0, (sum, p) => sum + (p * 100.0).round());
    final achievedKg = _round2((barCents + chosenSideCents * 2) / 100.0);
    final remainderPerSideKg = _round2(remainingSideCents / 100.0);
    final exact = remainingSideCents == 0 &&
        ((achievedKg * 100.0).round() == targetCents);

    final minPlate = sortedPlates.isNotEmpty ? sortedPlates.last : 1.25;
    final stepTotalKg = minPlate * 2.0;
    final lowerKg = achievedKg;
    final higherKg = exact ? achievedKg : _round2(achievedKg + stepTotalKg);

    String? warning;
    if (!exact) {
      warning =
          'Không thể chia chẵn chính xác với bánh nhỏ nhất ${_round2(minPlate)} kg. '
          'Gợi ý gần nhất: $lowerKg kg hoặc $higherKg kg.';
    }

    return PlateCalculationResult(
      targetWeightKg: _round2(targetWeightKg),
      barWeightKg: _round2(barWeightKg),
      perSidePlates: chosen,
      achievedWeightKg: achievedKg,
      remainderPerSideKg: remainderPerSideKg,
      isExact: exact,
      nearestLowerKg: lowerKg,
      nearestHigherKg: higherKg,
      warningMessage: warning,
    );
  }

  /// Tong Volume Load cua cac hiep lam viec (loai tru WARMUP) (F15, F22).
  static double calculateSessionVolumeKg(Iterable<WorkoutSetModel> sets) {
    var total = 0.0;
    for (final s in sets) {
      if (s.setType.toUpperCase() == 'WARMUP') continue;
      total += s.weightKg * s.reps;
    }
    return _round1(total);
  }

  /// Tinh muc bu nuoc sau buoi tap (F03): >=60p hoac RPE TB >=7.0 -> +750ml, con lai -> +500ml.
  /// Khi khong co hiep nao ghi RPE, avgRpe mac dinh 0.0 thay vi 7.0 de tranh cong nham +750ml.
  static int calculateWorkoutHydrationBonusMl({
    required int durationSeconds,
    required List<WorkoutSetModel> sets,
  }) {
    final workingSets =
        sets.where((s) => s.setType.toUpperCase() != 'WARMUP').toList();
    final rpes =
        workingSets.where((s) => s.rpe != null).map((s) => s.rpe!).toList();
    final avgRpe =
        rpes.isEmpty ? 0.0 : rpes.reduce((a, b) => a + b) / rpes.length;
    final durationMinutes = durationSeconds / 60.0;
    return (durationMinutes >= 60.0 || avgRpe >= 7.0) ? 750 : 500;
  }

  /// Quy doi kg <-> lbs tien loi khi nhap lieu o phong Gym (F15).
  static double lbsToKg(double lbs) => _round1(lbs * 0.45359237);
  static double kgToLbs(double kg) => _round1(kg / 0.45359237);

  /// Dem chuoi ngay tap luyen lien tuc (cho phep cach nhau <= 2 ngay nghi phuc hoi) (F25).
  static int computeWorkoutStreakDays(
    Iterable<DateTime> sessionDates, {
    DateTime? now,
  }) {
    final today = (now ?? DateTime.now().toUtc()).toUtc();
    final uniqueDays = sessionDates
        .map((d) => DateTime.utc(d.toUtc().year, d.toUtc().month, d.toUtc().day))
        .toSet()
        .toList()
      ..sort((a, b) => b.compareTo(a));

    if (uniqueDays.isEmpty) return 0;
    final todayDate = DateTime.utc(today.year, today.month, today.day);
    if (todayDate.difference(uniqueDays.first).inDays > 2) return 0;

    var streak = 0;
    var cursor = uniqueDays.first;
    for (final d in uniqueDays) {
      if (cursor.difference(d).inDays <= 2) {
        streak++;
        cursor = d;
      } else {
        break;
      }
    }
    return streak;
  }
}
