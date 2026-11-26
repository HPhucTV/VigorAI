// [OWNER: M1] Man hinh Nhat ky Calo & Macro chuan Mifflin-St Jeor (T-M1-09 / F04)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/theme/app_theme.dart';
import '../../data/health_repository.dart';
import '../data/offline_food_catalog.dart';

class NutritionScreen extends ConsumerWidget {
  const NutritionScreen({super.key});

  static const List<({String code, String label})> _mealSlots = [
    (code: 'BREAKFAST', label: 'Bữa Sáng'),
    (code: 'LUNCH', label: 'Bữa Trưa'),
    (code: 'DINNER', label: 'Bữa Tối'),
    (code: 'SNACK', label: 'Bữa Phụ'),
  ];

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(healthDashboardProvider);
    final controller = ref.read(healthDashboardProvider.notifier);
    final targets = state.macroTargets;
    final remainingKcal =
        (state.targetCaloriesKcal - state.totalCaloriesConsumed).round();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Nhật ký Calo & Macro'),
        actions: [
          IconButton(
            tooltip: 'Quét món ăn AI',
            icon: const Icon(Icons.camera_alt_outlined),
            onPressed: () => context.push('/health/food-scan'),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openAddMealSheet(context, controller),
        icon: const Icon(Icons.restaurant_menu),
        label: const Text('Thêm món'),
      ),
      body: ListView(
        padding: const EdgeInsets.fromLTRB(20, 14, 20, 88),
        children: [
          // The BMR / TDEE / Muc tieu Macro
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${state.totalCaloriesConsumed.round()} / ${state.targetCaloriesKcal.round()} kcal',
                    style: const TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: AppColors.calorieOrange,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    remainingKcal >= 0
                        ? 'Còn lại: $remainingKcal kcal · BMR ${state.bmrKcal.round()} kcal'
                        : 'Vượt ${remainingKcal.abs()} kcal · BMR ${state.bmrKcal.round()} kcal',
                  ),
                  const SizedBox(height: 10),
                  Wrap(
                    spacing: 8,
                    children: ['CUT', 'MAINTAIN', 'BULK'].map((goal) {
                      final label = goal == 'CUT'
                          ? 'Giảm mỡ'
                          : (goal == 'BULK' ? 'Tăng cơ' : 'Giữ dáng');
                      return ChoiceChip(
                        label: Text(label),
                        selected: state.fitnessGoal.toUpperCase() == goal,
                        onSelected: (_) => controller.changeNutritionGoal(
                          fitnessGoal: goal,
                          activityLevel: state.activityLevel,
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 14),
                  _MacroBar(
                    label: 'Protein (2.0 g/kg)',
                    consumed: state.totalProteinConsumed,
                    target: targets.proteinG,
                    color: AppColors.primary,
                  ),
                  const SizedBox(height: 8),
                  _MacroBar(
                    label: 'Carbs',
                    consumed: state.totalCarbsConsumed,
                    target: targets.carbsG,
                    color: AppColors.stepTeal,
                  ),
                  const SizedBox(height: 8),
                  _MacroBar(
                    label: 'Fat (25% kcal)',
                    consumed: state.totalFatConsumed,
                    target: targets.fatG,
                    color: AppColors.calorieOrange,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Nguồn công thức: Mifflin-St Jeor (1990) & hệ số hoạt động thể chất. Thông tin dinh dưỡng chỉ mang tính tham khảo.',
                    style: TextStyle(
                      fontSize: 11,
                      color: AppColors.secondaryText(context),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 10),

          // Nut mo nhanh Quet mon an AI (F19)
          Card(
            color: AppColors.tintedSurface(context, AppColors.calorieOrange),
            child: ListTile(
              leading: const CircleAvatar(
                backgroundColor: AppColors.calorieOrange,
                child: Icon(Icons.auto_awesome, color: Colors.white),
              ),
              title: const Text(
                'Quét Món ăn bằng AI Camera',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: const Text(
                'Chụp hoặc chọn ảnh món ăn để AI nhận diện & tính Macro tự động',
              ),
              trailing: const Icon(Icons.arrow_forward_ios, size: 16),
              onTap: () => context.push('/health/food-scan'),
            ),
          ),
          const SizedBox(height: 12),

          // Nhat ky chia 4 bua
          ..._mealSlots.map((slot) {
            final slotMeals = state.meals
                .where((m) => m.mealType.toUpperCase() == slot.code)
                .toList();
            final slotKcal = slotMeals.fold<double>(
              0.0,
              (sum, m) => sum + m.totalCalories,
            );
            return Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          slot.label,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                        Text(
                          '${slotKcal.round()} kcal',
                          style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            color: AppColors.calorieOrange,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    if (slotMeals.isEmpty)
                      Text(
                        'Chưa có món nào trong bữa này.',
                        style: TextStyle(
                          fontSize: 13,
                          color: AppColors.secondaryText(context),
                        ),
                      )
                    else
                      ...slotMeals.map(
                        (meal) => ListTile(
                          dense: true,
                          contentPadding: EdgeInsets.zero,
                          title: Text(meal.title),
                          subtitle: Text(
                            '${meal.totalCalories.round()} kcal · '
                            'P ${meal.proteinG.toStringAsFixed(1)}g · '
                            'C ${meal.carbsG.toStringAsFixed(1)}g · '
                            'F ${meal.fatG.toStringAsFixed(1)}g',
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline, size: 20),
                            onPressed: () => controller.deleteMeal(meal.id),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  Future<void> _openAddMealSheet(
    BuildContext context,
    HealthDashboardController controller,
  ) async {
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (sheetCtx) => _AddMealSheet(controller: controller),
    );
  }
}

class _AddMealSheet extends StatefulWidget {
  final HealthDashboardController controller;
  const _AddMealSheet({required this.controller});

  @override
  State<_AddMealSheet> createState() => _AddMealSheetState();
}

class _AddMealSheetState extends State<_AddMealSheet> {
  String _mealType = 'LUNCH';
  String _query = '';
  bool _manualMode = false;
  OfflineFoodCatalogItem _selectedFood = kOfflineFoodCatalog.first;
  double _grams = kOfflineFoodCatalog.first.defaultServingG;

  final _titleCtrl = TextEditingController();
  final _kcalCtrl = TextEditingController();
  final _proteinCtrl = TextEditingController();
  final _carbsCtrl = TextEditingController();
  final _fatCtrl = TextEditingController();

  @override
  void dispose() {
    _titleCtrl.dispose();
    _kcalCtrl.dispose();
    _proteinCtrl.dispose();
    _carbsCtrl.dispose();
    _fatCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filtered = kOfflineFoodCatalog.where((item) {
      if (_query.trim().isEmpty) return true;
      final q = _query.trim().toLowerCase();
      return item.nameVi.toLowerCase().contains(q) ||
          item.classCode.toLowerCase().contains(q);
    }).toList();

    return Padding(
      padding: EdgeInsets.fromLTRB(
        16,
        16,
        16,
        MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Thêm món ăn vào Nhật ký Calo',
              style: TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
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
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Chọn từ danh sách'),
                    selected: !_manualMode,
                    onSelected: (_) => setState(() => _manualMode = false),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: ChoiceChip(
                    label: const Text('Nhập tay tự do'),
                    selected: _manualMode,
                    onSelected: (_) => setState(() => _manualMode = true),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            if (!_manualMode) ...[
              TextField(
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.search),
                  labelText: 'Tìm món ăn (VD: ức gà, cơm, phở...)',
                ),
                onChanged: (v) => setState(() => _query = v),
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 140,
                child: ListView.builder(
                  itemCount: filtered.length,
                  itemBuilder: (_, idx) {
                    final item = filtered[idx];
                    final selected = item.classCode == _selectedFood.classCode;
                    return ListTile(
                      dense: true,
                      selected: selected,
                      title: Text(item.nameVi),
                      subtitle: Text(
                        '${item.kcalPer100g.round()} kcal / 100g · P ${item.proteinPer100g}g',
                      ),
                      trailing: selected
                          ? const Icon(Icons.check_circle, color: AppColors.primary)
                          : null,
                      onTap: () => setState(() {
                        _selectedFood = item;
                        _grams = item.defaultServingG;
                      }),
                    );
                  },
                ),
              ),
              const Divider(),
              Text(
                'Khẩu phần: ${_grams.round()} g (${_selectedFood.caloriesForGrams(_grams).round()} kcal)',
                style: const TextStyle(fontWeight: FontWeight.w600),
              ),
              Slider(
                value: _grams.clamp(20, 600),
                min: 20,
                max: 600,
                divisions: 58,
                label: '${_grams.round()} g',
                onChanged: (v) => setState(() => _grams = v),
              ),
              Text(
                'P: ${_selectedFood.proteinForGrams(_grams)}g · '
                'C: ${_selectedFood.carbsForGrams(_grams)}g · '
                'F: ${_selectedFood.fatForGrams(_grams)}g',
              ),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: () async {
                  await widget.controller.addMeal(
                    mealType: _mealType,
                    title: '${_selectedFood.nameVi} (${_grams.round()}g)',
                    calories: _selectedFood.caloriesForGrams(_grams),
                    proteinG: _selectedFood.proteinForGrams(_grams),
                    carbsG: _selectedFood.carbsForGrams(_grams),
                    fatG: _selectedFood.fatForGrams(_grams),
                    aiDetectedItems: [
                      {
                        'class_code': _selectedFood.classCode,
                        'name_vi': _selectedFood.nameVi,
                        'estimated_grams': _grams,
                        'calories': _selectedFood.caloriesForGrams(_grams),
                      }
                    ],
                  );
                  if (context.mounted) Navigator.of(context).pop();
                },
                child: const Text('Lưu món ăn'),
              ),
            ] else ...[
              TextField(
                controller: _titleCtrl,
                decoration: const InputDecoration(labelText: 'Tên món ăn *'),
              ),
              const SizedBox(height: 8),
              TextField(
                controller: _kcalCtrl,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Calories (kcal) *'),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _proteinCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Đạm (g)'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _carbsCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Tinh bột (g)'),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _fatCtrl,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(labelText: 'Chất béo (g)'),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              FilledButton(
                onPressed: () async {
                  final title = _titleCtrl.text.trim();
                  final kcal = double.tryParse(_kcalCtrl.text.trim()) ?? 0.0;
                  if (title.isEmpty || kcal <= 0) return;
                  await widget.controller.addMeal(
                    mealType: _mealType,
                    title: title,
                    calories: kcal,
                    proteinG: double.tryParse(_proteinCtrl.text.trim()) ?? 0.0,
                    carbsG: double.tryParse(_carbsCtrl.text.trim()) ?? 0.0,
                    fatG: double.tryParse(_fatCtrl.text.trim()) ?? 0.0,
                  );
                  if (context.mounted) Navigator.of(context).pop();
                },
                child: const Text('Lưu món nhập tay'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MacroBar extends StatelessWidget {
  final String label;
  final double consumed;
  final double target;
  final Color color;

  const _MacroBar({
    required this.label,
    required this.consumed,
    required this.target,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final ratio = target > 0 ? (consumed / target).clamp(0.0, 1.0) : 0.0;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontSize: 13),
              ),
            ),
            const SizedBox(width: 8),
            Flexible(
              child: FittedBox(
                fit: BoxFit.scaleDown,
                alignment: Alignment.centerRight,
                child: Text(
                  '${consumed.toStringAsFixed(1)} / ${target.round()} g (${(ratio * 100).round()}%)',
                  maxLines: 1,
                  style: const TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: ratio,
          color: color,
          backgroundColor: color.withValues(alpha: 0.15),
          minHeight: 7,
          borderRadius: BorderRadius.circular(4),
        ),
      ],
    );
  }
}
