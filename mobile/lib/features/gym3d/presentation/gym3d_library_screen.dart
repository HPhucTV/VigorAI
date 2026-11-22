// [OWNER: M2] Man hinh Thu vien Bai tap 3D Tuong tac (T-M2-03 / F07)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/config/feature_flags.dart';
import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../data/exercise_repository.dart';
import 'widgets/muscle_3d_viewer_widget.dart';

class Gym3DLibraryScreen extends ConsumerStatefulWidget {
  const Gym3DLibraryScreen({super.key});

  @override
  ConsumerState<Gym3DLibraryScreen> createState() => _Gym3DLibraryScreenState();
}

class _Gym3DLibraryScreenState extends ConsumerState<Gym3DLibraryScreen> {
  String _searchQuery = '';
  String _selectedEquipment = 'ALL';
  String _selectedMuscle = 'ALL';

  static const _muscleFilters = <String, String>{
    'ALL': 'Tất cả cơ',
    MuscleMaterialIds.chest: 'Ngực',
    MuscleMaterialIds.backLats: 'Xô & Lưng',
    MuscleMaterialIds.traps: 'Lưng trên / Cầu vai',
    MuscleMaterialIds.shoulders: 'Vai',
    MuscleMaterialIds.biceps: 'Tay trước',
    MuscleMaterialIds.triceps: 'Tay sau',
    MuscleMaterialIds.quads: 'Đùi trước',
    MuscleMaterialIds.hamstrings: 'Đùi sau',
    MuscleMaterialIds.glutes: 'Mông',
    MuscleMaterialIds.absCore: 'Bụng & Lõi',
  };

  static const _equipmentFilters = <String, String>{
    'ALL': 'Tất cả dụng cụ',
    'BARBELL': 'Đòn tạ',
    'DUMBBELL': 'Tạ đơn',
    'BODYWEIGHT': 'Trọng lượng cơ thể',
    'CABLE': 'Máy cáp',
    'MACHINE': 'Máy tập',
    'KETTLEBELL': 'Tạ ấm',
  };

  @override
  Widget build(BuildContext context) {
    final exercisesAsync = ref.watch(exercisesListProvider);
    final avatarPreset = ref.watch(bodyAvatarPresetProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Phòng tập 3D Tương tác'),
        actions: [
          PopupMenuButton<BodyAvatarPreset>(
            tooltip: 'Chọn mô hình cơ thể 3D',
            initialValue: avatarPreset,
            onSelected: (preset) {
              ref.read(bodyAvatarPresetProvider.notifier).state = preset;
            },
            itemBuilder: (_) => BodyAvatarPreset.values
                .map(
                  (preset) => PopupMenuItem<BodyAvatarPreset>(
                    value: preset,
                    child: Row(
                      children: [
                        Icon(
                          preset == avatarPreset
                              ? Icons.radio_button_checked
                              : Icons.radio_button_unchecked,
                          size: 18,
                          color: AppColors.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(preset.labelVi),
                      ],
                    ),
                  ),
                )
                .toList(),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
              child: Chip(
                avatar: const Icon(Icons.accessibility_new, size: 16),
                label: Text(
                  avatarPreset.shortLabelVi,
                  style: const TextStyle(fontSize: 12),
                ),
                visualDensity: VisualDensity.compact,
              ),
            ),
          ),
        ],
      ),
      body: exercisesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline, size: 42, color: AppColors.warningRed),
                const SizedBox(height: 12),
                Text('Không thể tải kho bài tập 3D: $err'),
                const SizedBox(height: 12),
                FilledButton(
                  onPressed: () => ref.invalidate(exercisesListProvider),
                  child: const Text('Thử lại'),
                ),
              ],
            ),
          ),
        ),
        data: (allExercises) {
          final visiblePool = FeatureFlags.isMvpClosedTesting
              ? allExercises.where((e) => e.isBundled).toList()
              : allExercises;

          final filtered = visiblePool.where((e) {
            if (_selectedMuscle != 'ALL') {
              final hitsMuscle = e.primaryMuscles.contains(_selectedMuscle) ||
                  e.secondaryMuscles.contains(_selectedMuscle);
              if (!hitsMuscle) return false;
            }
            if (_selectedEquipment != 'ALL' &&
                e.equipmentType != _selectedEquipment) {
              return false;
            }
            if (_searchQuery.trim().isNotEmpty) {
              final q = _searchQuery.trim().toLowerCase();
              return e.nameVi.toLowerCase().contains(q) ||
                  e.nameEn.toLowerCase().contains(q) ||
                  e.code.toLowerCase().contains(q);
            }
            return true;
          }).toList();

          return Column(
            children: [
              if (FeatureFlags.isMvpClosedTesting)
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                  child: Card(
                    color: const Color(0xFFE3F2FD),
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          const Icon(Icons.view_in_ar, color: AppColors.primary),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              'Đã có sẵn ${visiblePool.length} bài tập 3D — xoay 360°, Đúng/Sai & Bản đồ cơ.',
                              style: const TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 10, 16, 6),
                child: TextField(
                  decoration: const InputDecoration(
                    hintText: 'Tìm bài tập (Đẩy ngực, Incline, Ép cáp...)',
                    prefixIcon: Icon(Icons.search),
                    isDense: true,
                  ),
                  onChanged: (v) => setState(() => _searchQuery = v),
                ),
              ),
              SizedBox(
                height: 40,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: _muscleFilters.entries.map((entry) {
                    final selected = _selectedMuscle == entry.key;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: FilterChip(
                        label: Text(entry.value),
                        selected: selected,
                        visualDensity: VisualDensity.compact,
                        onSelected: (_) =>
                            setState(() => _selectedMuscle = entry.key),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 4),
              SizedBox(
                height: 40,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: _equipmentFilters.entries.map((entry) {
                    final selected = _selectedEquipment == entry.key;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(entry.value),
                        selected: selected,
                        visualDensity: VisualDensity.compact,
                        onSelected: (_) =>
                            setState(() => _selectedEquipment = entry.key),
                      ),
                    );
                  }).toList(),
                ),
              ),
              Expanded(
                child: filtered.isEmpty
                    ? const Center(child: Text('Không tìm thấy bài tập phù hợp.'))
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: filtered.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) =>
                            _Exercise3DCard(exercise: filtered[index]),
                      ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _Exercise3DCard extends StatelessWidget {
  final ExerciseModel exercise;

  const _Exercise3DCard({required this.exercise});

  IconData _iconForEquipment(String type) {
    switch (type) {
      case 'BARBELL':
        return Icons.fitness_center;
      case 'DUMBBELL':
      case 'KETTLEBELL':
        return Icons.sports_gymnastics;
      case 'BODYWEIGHT':
        return Icons.accessibility_new;
      default:
        return Icons.settings_input_component;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        borderRadius: BorderRadius.circular(16),
        onTap: () => context.push('/gym3d/exercise/${exercise.code}'),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              CircleAvatar(
                radius: 24,
                backgroundColor: AppColors.primary.withValues(alpha: 0.12),
                child: Icon(
                  _iconForEquipment(exercise.equipmentType),
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      exercise.nameVi,
                      style: const TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    if (exercise.nameEn.isNotEmpty)
                      Text(
                        '${exercise.nameEn} · ${exercise.equipmentType}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    const SizedBox(height: 6),
                    Wrap(
                      spacing: 6,
                      runSpacing: 4,
                      children: [
                        ...exercise.primaryMuscles.map(
                          (m) => Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.musclePrimaryRed
                                  .withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              MuscleMaterialIds.labelVi(m).split(' (').first,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: AppColors.musclePrimaryRed,
                              ),
                            ),
                          ),
                        ),
                        if (exercise.hasBadFormClip)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 3,
                            ),
                            decoration: BoxDecoration(
                              color: AppColors.primary.withValues(alpha: 0.10),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Text(
                              'Đúng / Sai 3D',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}
