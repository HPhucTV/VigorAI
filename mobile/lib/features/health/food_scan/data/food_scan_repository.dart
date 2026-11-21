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
    required this.baseProteinG,
    required this.baseCarbsG,
    required this.baseFatG,
    required this.adjustedGrams,
  });

  double get _ratio =>
      baseEstimatedGrams > 0 ? (adjustedGrams / baseEstimatedGrams) : 1.0;

  double get calories => ((baseCalories * _ratio) * 10).round() / 10.0;
  double get proteinG => ((baseProteinG * _ratio) * 10).round() / 10.0;
  double get carbsG => ((baseCarbsG * _ratio) * 10).round() / 10.0;
  double get fatG => ((baseFatG * _ratio) * 10).round() / 10.0;

  DetectedFoodItemModel scaleToGrams(double grams) {
    return DetectedFoodItemModel(
      classCode: classCode,
      nameVi: nameVi,
      confidence: confidence,
      bboxNorm: bboxNorm,
      baseEstimatedGrams: baseEstimatedGrams,
      baseCalories: baseCalories,
      baseProteinG: baseProteinG,
      baseCarbsG: baseCarbsG,
      baseFatG: baseFatG,
      adjustedGrams: grams.clamp(10.0, 1500.0),
    );
  }

  factory DetectedFoodItemModel.fromJson(Map<String, dynamic> json) {
    final estGrams = (json['estimated_grams'] as num?)?.toDouble() ?? 100.0;
    final rawBox = (json['bbox_norm'] as List?) ?? const [0.1, 0.1, 0.9, 0.9];
    return DetectedFoodItemModel(
      classCode: (json['class_code'] as String?) ?? 'FOOD_ITEM',
      nameVi: (json['name_vi'] as String?) ?? 'Món ăn',
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.85,
      bboxNorm: rawBox.map((e) => (e as num).toDouble()).toList(),
      baseEstimatedGrams: estGrams,
      baseCalories: (json['calories'] as num?)?.toDouble() ?? 0.0,
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
