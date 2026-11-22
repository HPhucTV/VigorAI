// [OWNER: M1] Man hinh Quet Mon an AI Model B + Ve BBox + Thanh keo Gram + Disclaimer (T-M1-10 / F19)
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/platform/photo_picker_service.dart';
import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';
import '../data/food_scan_repository.dart';

class FoodScanScreen extends ConsumerStatefulWidget {
  const FoodScanScreen({super.key});

  @override
  ConsumerState<FoodScanScreen> createState() => _FoodScanScreenState();
}

class _FoodScanScreenState extends ConsumerState<FoodScanScreen> {
  File? _selectedImage;
  double _imageAspectRatio = 4.0 / 3.0;
  bool _isAnalyzing = false;
  bool _isSaving = false;
  String _mealType = 'LUNCH';
  String? _errorMessage;
  FoodAnalyzeResultModel? _result;

  Future<void> _pickAndAnalyze({required bool fromCamera}) async {
    setState(() {
      _errorMessage = null;
    });
    final picker = ref.read(photoPickerServiceProvider);
    final File? file = fromCamera
        ? await picker.captureFromCameraCompressed()
        : await picker.pickFromGalleryCompressed();
    if (file == null) return;

    var ratio = 4.0 / 3.0;
    try {
      final bytes = await file.readAsBytes();
      final decoded = await decodeImageFromList(bytes);
      if (decoded.width > 0 && decoded.height > 0) {
        ratio = decoded.width / decoded.height;
      }
      decoded.dispose();
    } catch (_) {}
    if (!mounted) return;

    setState(() {
      _selectedImage = file;
      _imageAspectRatio = ratio;
      _isAnalyzing = true;
      _result = null;
    });

    try {
      final repo = ref.read(foodScanRepositoryProvider);
      final analyzed = await repo.analyzeFoodImage(file, mealType: _mealType);
      if (!mounted) return;
      setState(() {
        _result = analyzed;
        _isAnalyzing = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isAnalyzing = false;
        _errorMessage = 'Không thể phân tích món ăn: $e';
      });
    }
  }

  Future<void> _saveToMealLog() async {
    final res = _result;
    if (res == null || res.detectedItems.isEmpty) return;
    setState(() => _isSaving = true);
    try {
      String? persistedImagePath;
      if (_selectedImage != null) {
        final savedFile = await ref
            .read(photoPickerServiceProvider)
            .savePrivateMealPhoto(_selectedImage!);
        persistedImagePath = savedFile.path;
      }
      final title = res.detectedItems
          .map((e) => '${e.nameVi} (${e.adjustedGrams.round()}g)')
          .join(' + ');
      await ref.read(healthDashboardProvider.notifier).addMeal(
            mealType: _mealType,
            title: title,
            calories: res.totalCalories,
            proteinG: res.totalProteinG,
            carbsG: res.totalCarbsG,
            fatG: res.totalFatG,
            localImagePath: persistedImagePath,
            aiDetectedItems: res.detectedItems.map((e) => e.toJson()).toList(),
          );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Đã lưu ${res.totalCalories.round()} kcal vào Nhật ký Calo!',
          ),
        ),
      );
      context.pop();
    } finally {
      if (mounted) setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final res = _result;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Quét Món ăn AI'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Chon anh bang Android Photo Picker API (khong xin READ_MEDIA_IMAGES)
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: _isAnalyzing
                      ? null
                      : () => _pickAndAnalyze(fromCamera: true),
                  icon: const Icon(Icons.camera_alt_outlined),
                  label: const Text('Chụp món ăn'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: FilledButton.tonalIcon(
                  onPressed: _isAnalyzing
                      ? null
                      : () => _pickAndAnalyze(fromCamera: false),
                  icon: const Icon(Icons.photo_library_outlined),
                  label: const Text('Chọn từ thư viện'),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Chon bua an
          Wrap(
            spacing: 6,
            children: const [
              ('BREAKFAST', 'Sáng'),
              ('LUNCH', 'Trưa'),
              ('DINNER', 'Tối'),
              ('SNACK', 'Phụ'),
            ]
                .map(
                  (slot) => ChoiceChip(
                    label: Text(slot.$2),
                    selected: _mealType == slot.$1,
                    onSelected: (_) => setState(() => _mealType = slot.$1),
                  ),
                )
                .toList(),
          ),
          const SizedBox(height: 12),

          // Hinh anh + Bounding Box Overlay
          if (_selectedImage != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: AspectRatio(
                aspectRatio: _imageAspectRatio,
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    Image.file(_selectedImage!, fit: BoxFit.fill),
                    if (res != null && res.detectedItems.isNotEmpty)
                      CustomPaint(
                        painter: _FoodBboxPainter(res.detectedItems),
                      ),
                    if (_isAnalyzing)
                      Container(
                        color: Colors.black54,
                        child: const Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              CircularProgressIndicator(color: Colors.white),
                              SizedBox(height: 10),
                              Text(
                                'AI đang nhận diện món ăn...',
                                style: TextStyle(color: Colors.white),
                              ),
                            ],
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            )
          else
            Container(
              height: 180,
              decoration: BoxDecoration(
                color: const Color(0xFFF3F6FA),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: Colors.black12),
              ),
              child: const Center(
                child: Padding(
                  padding: EdgeInsets.all(20),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.fastfood_outlined, size: 42, color: Colors.black45),
                      SizedBox(height: 8),
                      Text(
                        'Chụp hoặc chọn ảnh bữa ăn để AI nhận diện và ước tính dinh dưỡng.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.black54),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          if (_errorMessage != null) ...[
            const SizedBox(height: 10),
            Card(
              color: Colors.red.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Text(_errorMessage!),
              ),
            ),
          ],

          if (res != null) ...[
            const SizedBox(height: 14),
            Card(
              color: const Color(0xFFFFF8E1),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tổng: ${res.totalCalories.round()} kcal',
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: AppColors.calorieOrange,
                      ),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      'Đạm: ${res.totalProteinG.toStringAsFixed(1)}g · '
                      'Carb: ${res.totalCarbsG.toStringAsFixed(1)}g · '
                      'Fat: ${res.totalFatG.toStringAsFixed(1)}g',
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),

            ...List.generate(res.detectedItems.length, (idx) {
              final item = res.detectedItems[idx];
              return Card(
                margin: const EdgeInsets.only(bottom: 8),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            '${item.nameVi} (${(item.confidence * 100).round()}%)',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                          Text(
                            '${item.calories.round()} kcal',
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              color: AppColors.calorieOrange,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Khẩu phần: ${item.adjustedGrams.round()} g · '
                        'P ${item.proteinG}g · C ${item.carbsG}g · F ${item.fatG}g',
                        style: const TextStyle(fontSize: 13),
                      ),
                      Slider(
                        value: item.adjustedGrams.clamp(20.0, 600.0),
                        min: 20,
                        max: 600,
                        divisions: 58,
                        label: '${item.adjustedGrams.round()} g',
                        onChanged: (grams) {
                          setState(() {
                            _result = res.copyWithItemGrams(idx, grams);
                          });
                        },
                      ),
                    ],
                  ),
                ),
              );
            }),

            // Bat buoc hien thi Disclaimer duoi ket qua AI Model B (AGENTS.md & F26)
            Card(
              color: const Color(0xFFF3F6FA),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline, size: 18, color: Colors.black54),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        res.disclaimer,
                        style: const TextStyle(fontSize: 12, color: Colors.black54),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),

            FilledButton.icon(
              onPressed: _isSaving ? null : _saveToMealLog,
              icon: const Icon(Icons.save_alt),
              label: Text(
                _isSaving
                    ? 'Đang lưu...'
                    : 'Lưu vào Nhật ký Calo (${res.totalCalories.round()} kcal)',
              ),
            ),
          ],
        ],
      ),
    );
  }
}

class _FoodBboxPainter extends CustomPainter {
  final List<DetectedFoodItemModel> items;

  _FoodBboxPainter(this.items);

  @override
  void paint(Canvas canvas, Size size) {
    const palette = [
      Color(0xFFE53935),
      Color(0xFF00BFA5),
      Color(0xFFFB8C00),
      Color(0xFF1565C0),
    ];

    for (var i = 0; i < items.length; i++) {
      final item = items[i];
      if (item.bboxNorm.length < 4) continue;
      final color = palette[i % palette.length];
      final rect = Rect.fromLTRB(
        item.bboxNorm[0].clamp(0.0, 1.0) * size.width,
        item.bboxNorm[1].clamp(0.0, 1.0) * size.height,
        item.bboxNorm[2].clamp(0.0, 1.0) * size.width,
        item.bboxNorm[3].clamp(0.0, 1.0) * size.height,
      );

      final borderPaint = Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.5;
      canvas.drawRect(rect, borderPaint);

      final textPainter = TextPainter(
        text: TextSpan(
          text: ' ${item.nameVi} ${(item.confidence * 100).round()}% ',
          style: const TextStyle(
            color: Colors.white,
            fontSize: 11,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      )..layout();

      final labelBg = Rect.fromLTWH(
        rect.left,
        (rect.top - 18).clamp(0.0, size.height - 18),
        textPainter.width,
        18,
      );
      canvas.drawRect(labelBg, Paint()..color = color);
      textPainter.paint(canvas, Offset(labelBg.left, labelBg.top + 2));
    }
  }

  @override
  bool shouldRepaint(covariant _FoodBboxPainter oldDelegate) =>
      oldDelegate.items != items;
}
