// [OWNER: M1] Repository Quet Mon an AI Model B (T-M1-10 / F19 -> F04)
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path/path.dart' as p;

import '../../../../core/network/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/platform/photo_picker_service.dart';

class DetectedFoodItemModel {
  final String classCode;
  final String nameVi;
  final double confidence;
  final List<double> bboxNorm; // [xMin, yMin, xMax, yMax] trong [0.0..1.0]
  final double baseEstimatedGrams;
  final double baseCalories;
  final int baseCaloriesMin;
  final int baseCaloriesMax;
  final double baseProteinG;
  final double baseCarbsG;
  final double baseFatG;
  final double adjustedGrams;

  const DetectedFoodItemModel({
    required this.classCode,
    required this.nameVi,
    required this.confidence,
    required this.bboxNorm,
    required this.baseEstimatedGrams,
    required this.baseCalories,
    required this.baseCaloriesMin,
    required this.baseCaloriesMax,
    required this.baseProteinG,
    required this.baseCarbsG,
    required this.baseFatG,
    required this.adjustedGrams,
  });

  double get _ratio =>
      baseEstimatedGrams > 0 ? (adjustedGrams / baseEstimatedGrams) : 1.0;

  bool get isBeverage =>
      classCode.startsWith('DRINK_') ||
      const {
        'BOTTLED_DRINK',
        'COFFEE_MILK_TEA',
        'FRUIT_JUICE_SMOOTHIE',
      }.contains(classCode);

  String get unitLabel => isBeverage ? 'ml' : 'g';

  double get calories => ((baseCalories * _ratio) * 10).round() / 10.0;
  double get proteinG => ((baseProteinG * _ratio) * 10).round() / 10.0;
  double get carbsG => ((baseCarbsG * _ratio) * 10).round() / 10.0;
  double get fatG => ((baseFatG * _ratio) * 10).round() / 10.0;

  int _roundStep(double raw, {required bool up, required int step}) {
    if (raw <= 0) return 0;
    return up
        ? ((raw / step).ceil() * step)
        : ((raw / step).floor() * step);
  }

  bool get _isUnmodified => (adjustedGrams - baseEstimatedGrams).abs() < 0.05;

  int get caloriesMin {
    if (calories <= 0) return 0;
    if (_isUnmodified && baseCaloriesMin > 0) return baseCaloriesMin;
    final step = (calories < 120 || baseCaloriesMin % 10 != 0) ? 5 : 10;
    final scaled = baseCaloriesMin > 0
        ? (baseCaloriesMin * _ratio)
        : (calories * 0.8);
    final rounded = _roundStep(scaled, up: false, step: step);
    return (rounded == 0 && calories >= 10) ? step : rounded;
  }

  int get caloriesMax {
    if (calories <= 0) return 0;
    if (_isUnmodified && baseCaloriesMax > caloriesMin) return baseCaloriesMax;
    final step = (calories < 120 || baseCaloriesMax % 10 != 0) ? 5 : 10;
    final scaled = baseCaloriesMax > 0
        ? (baseCaloriesMax * _ratio)
        : (calories * 1.2);
    final rounded = _roundStep(scaled, up: true, step: step);
    return rounded <= caloriesMin ? (caloriesMin + step) : rounded;
  }

  String get caloriesRangeText =>
      calories <= 0 ? '0 kcal' : '~$caloriesMin – $caloriesMax kcal';

  DetectedFoodItemModel scaleToGrams(double grams) {
    return DetectedFoodItemModel(
      classCode: classCode,
      nameVi: nameVi,
      confidence: confidence,
      bboxNorm: bboxNorm,
      baseEstimatedGrams: baseEstimatedGrams,
      baseCalories: baseCalories,
      baseCaloriesMin: baseCaloriesMin,
      baseCaloriesMax: baseCaloriesMax,
      baseProteinG: baseProteinG,
      baseCarbsG: baseCarbsG,
      baseFatG: baseFatG,
      adjustedGrams: grams.clamp(10.0, 1500.0),
    );
  }

  factory DetectedFoodItemModel.fromJson(Map<String, dynamic> json) {
    final estGrams = (json['estimated_grams'] as num?)?.toDouble() ?? 100.0;
    final baseCal = (json['calories'] as num?)?.toDouble() ?? 0.0;
    final calMin =
        (json['calories_min'] as num?)?.toInt() ?? (baseCal * 0.8).floor();
    final calMax =
        (json['calories_max'] as num?)?.toInt() ?? (baseCal * 1.2).ceil();
    final rawBox = (json['bbox_norm'] as List?) ?? const [0.1, 0.1, 0.9, 0.9];
    return DetectedFoodItemModel(
      classCode: (json['class_code'] as String?) ?? 'FOOD_ITEM',
      nameVi: (json['name_vi'] as String?) ?? 'Món ăn',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.85,
      bboxNorm: rawBox.map((e) => (e as num).toDouble()).toList(),
      baseEstimatedGrams: estGrams,
      baseCalories: baseCal,
      baseCaloriesMin: calMin,
      baseCaloriesMax: calMax,
      baseProteinG: (json['protein_g'] as num?)?.toDouble() ?? 0.0,
      baseCarbsG: (json['carbs_g'] as num?)?.toDouble() ?? 0.0,
      baseFatG: (json['fat_g'] as num?)?.toDouble() ?? 0.0,
      adjustedGrams: estGrams,
    );
  }

  Map<String, dynamic> toJson() => {
        'class_code': classCode,
        'name_vi': nameVi,
        'confidence': confidence,
        'bbox_norm': bboxNorm,
        'estimated_grams': adjustedGrams,
        'calories': calories,
        'calories_min': caloriesMin,
        'calories_max': caloriesMax,
        'calories_range_label': caloriesRangeText,
        'protein_g': proteinG,
        'carbs_g': carbsG,
        'fat_g': fatG,
      };
}

class FoodAnalyzeResultModel {
  final int inferenceTimeMs;
  final String modelVersion;
  final List<DetectedFoodItemModel> detectedItems;
  final String disclaimer;

  const FoodAnalyzeResultModel({
    required this.inferenceTimeMs,
    required this.modelVersion,
    required this.detectedItems,
    required this.disclaimer,
  });

  double get totalCalories =>
      detectedItems.fold<double>(0.0, (s, e) => s + e.calories);

  (int, int) get _effectiveTotalBounds {
    if (totalCalories <= 0) return (0, 0);
    var rawMin = detectedItems.fold<int>(0, (s, e) => s + e.caloriesMin);
    var rawMax = detectedItems.fold<int>(0, (s, e) => s + e.caloriesMax);
    if (detectedItems.length >= 2 && totalCalories >= 60) {
      for (var i = 0; i < 40 && (rawMax - rawMin) > 100; i++) {
        if ((rawMin + 5) <= totalCalories &&
            (totalCalories - (rawMin + 5)) >= (rawMax - totalCalories)) {
          rawMin += 5;
        } else if ((rawMax - 5) >= totalCalories) {
          rawMax -= 5;
        } else {
          break;
        }
      }
      if ((rawMax - rawMin) < 50) {
        rawMax = rawMin + 50;
      }
    }
    return (rawMin, rawMax);
  }

  int get totalCaloriesMin => _effectiveTotalBounds.$1;
  int get totalCaloriesMax => _effectiveTotalBounds.$2;
  String get totalCaloriesRangeText => totalCalories <= 0
      ? '0 kcal'
      : '~$totalCaloriesMin – $totalCaloriesMax kcal';
  double get totalProteinG =>
      detectedItems.fold<double>(0.0, (s, e) => s + e.proteinG);
  double get totalCarbsG =>
      detectedItems.fold<double>(0.0, (s, e) => s + e.carbsG);
  double get totalFatG =>
      detectedItems.fold<double>(0.0, (s, e) => s + e.fatG);

  FoodAnalyzeResultModel copyWithItemGrams(int index, double grams) {
    final updated = List<DetectedFoodItemModel>.from(detectedItems);
    updated[index] = updated[index].scaleToGrams(grams);
    return FoodAnalyzeResultModel(
      inferenceTimeMs: inferenceTimeMs,
      modelVersion: modelVersion,
      detectedItems: updated,
      disclaimer: disclaimer,
    );
  }

  factory FoodAnalyzeResultModel.fromJson(Map<String, dynamic> json) {
    final items = ((json['detected_items'] as List?) ?? const [])
        .map((e) => DetectedFoodItemModel.fromJson(e as Map<String, dynamic>))
        .toList();
    return FoodAnalyzeResultModel(
      inferenceTimeMs: (json['inference_time_ms'] as num?)?.toInt() ?? 0,
      modelVersion: (json['model_version'] as String?) ?? 'yolov8s-food',
      detectedItems: items,
      disclaimer: (json['disclaimer'] as String?) ??
          'Giá trị dinh dưỡng được AI ước tính dựa trên hình ảnh, vui lòng kiểm tra lại khẩu phần gram trước khi lưu.',
    );
  }
}

class FoodScanRepository {
  final Dio _dio;
  final PhotoPickerService _photoPickerService;

  FoodScanRepository(this._dio, this._photoPickerService);

  Future<FoodAnalyzeResultModel> analyzeFoodImage(
    File imageFile, {
    String mealType = 'LUNCH',
  }) async {
    final validSize = await _photoPickerService.validateUnder300Kb(imageFile);
    if (!validSize && await imageFile.exists()) {
      final bytes = await imageFile.length();
      if (bytes > PhotoPickerService.maxAllowedBytes) {
        // Van gui neu he thong khong nen nho hon duoc, nhung ghi chu chuan kich thuoc
      }
    }

    final formData = FormData.fromMap(<String, dynamic>{
      'image': await MultipartFile.fromFile(
        imageFile.path,
        filename: p.basename(imageFile.path),
      ),
      'meal_type': mealType,
    });

    final response = await _dio.post<Map<String, dynamic>>(
      ApiEndpoints.aiFoodAnalyze,
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );

    return FoodAnalyzeResultModel.fromJson(
      response.data ?? const <String, dynamic>{},
    );
  }
}

final foodScanRepositoryProvider = Provider<FoodScanRepository>((ref) {
  final dio = ref.watch(dioProvider);
  final photoPicker = ref.watch(photoPickerServiceProvider);
  return FoodScanRepository(dio, photoPicker);
});
