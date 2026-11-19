// [OWNER: M2] Dinh nghia bang cache AI Readiness & Nhat ky anh Progress cuc bo (T-M2-04)
// Luu y: LocalProgressPhotosTable duoc giu nguyen cho M1 su dung o tinh nang F24 (Progress Photos).
import 'package:drift/drift.dart';

// ============================================================================
// 1. DRIFT TABLE DEFINITIONS
// ============================================================================

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

// ============================================================================
// 2. DOMAIN ENTITIES (Khớp 100% Backend AI Schema backend/app/schemas/ai_schema.py)
// ============================================================================

class WeightRecommendationModel {
  final String exerciseCode;
  final String action; // INCREASE | MAINTAIN | DELOAD
  final double recommendedWeightKg;
  final String recommendedReps;
  final String reason;

  const WeightRecommendationModel({
    required this.exerciseCode,
    required this.action,
    required this.recommendedWeightKg,
    required this.recommendedReps,
    required this.reason,
  });

  factory WeightRecommendationModel.fromJson(Map<String, dynamic> json) {
    return WeightRecommendationModel(
      exerciseCode: json['exercise_code'] as String,
      action: json['action'] as String,
      recommendedWeightKg: (json['recommended_weight_kg'] as num).toDouble(),
      recommendedReps: json['recommended_reps'] as String,
      reason: json['reason'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'exercise_code': exerciseCode,
        'action': action,
        'recommended_weight_kg': recommendedWeightKg,
        'recommended_reps': recommendedReps,
        'reason': reason,
      };
}

class AiReadinessSnapshotModel {
  final String targetDateIso;
  final String modelVersion;
  final double readinessScore;
  final String readinessLevel; // READY | MODERATE | REST_RECOMMENDED
  final List<String> insights;
  final Map<String, double> muscleFatigueMap;
  final List<WeightRecommendationModel> weightRecommendations;
  final String disclaimer;

  const AiReadinessSnapshotModel({
    required this.targetDateIso,
    required this.modelVersion,
    required this.readinessScore,
    required this.readinessLevel,
    this.insights = const [],
    this.muscleFatigueMap = const {},
    this.weightRecommendations = const [],
    required this.disclaimer,
  });

  factory AiReadinessSnapshotModel.fromJson(Map<String, dynamic> json) {
    final rawFatigue =
        (json['muscle_fatigue_map'] as Map<String, dynamic>?) ?? const {};
    return AiReadinessSnapshotModel(
      targetDateIso: json['target_date'] as String,
      modelVersion: (json['model_version'] as String?) ?? 'unknown',
      readinessScore: (json['readiness_score'] as num).toDouble(),
      readinessLevel: (json['readiness_level'] as String?) ?? 'READY',
      insights: ((json['insights'] as List?) ?? const []).cast<String>(),
      muscleFatigueMap: rawFatigue.map(
        (k, v) => MapEntry(k, (v as num).toDouble().clamp(0.0, 1.0)),
      ),
      weightRecommendations: ((json['weight_recommendations'] as List?) ?? const [])
          .map((e) => WeightRecommendationModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      disclaimer: (json['disclaimer'] as String?) ??
          'Gợi ý tải trọng do AI phân tích chỉ phục vụ mục đích tham khảo thể hình.',
    );
  }

  Map<String, dynamic> toJson() => {
        'target_date': targetDateIso,
        'model_version': modelVersion,
        'readiness_score': readinessScore,
        'readiness_level': readinessLevel,
        'insights': insights,
        'muscle_fatigue_map': muscleFatigueMap,
        'weight_recommendations':
            weightRecommendations.map((e) => e.toJson()).toList(),
        'disclaimer': disclaimer,
      };
}
