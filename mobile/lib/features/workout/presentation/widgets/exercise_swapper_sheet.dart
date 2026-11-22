// [OWNER: M2] Hop thoai Doi Bai tap Tuc thi cung nhom co chinh >=80% (Exercise Swapper) (T-M2-09 / F25)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../../core/database/workout_tables.drift.dart';
import '../../../../core/theme/app_theme.dart';
import '../../../gym3d/presentation/widgets/muscle_3d_viewer_widget.dart';
import '../../data/workout_repository.dart';

Future<ExerciseModel?> showExerciseSwapperSheet(
  BuildContext context,
  WidgetRef ref, {
  required ExerciseModel currentExercise,
}) {
  return showModalBottomSheet<ExerciseModel>(
    context: context,
    isScrollControlled: true,
    useSafeArea: true,
    builder: (ctx) => _ExerciseSwapperContent(currentExercise: currentExercise),
  );
}

class _ExerciseSwapperContent extends ConsumerWidget {
  final ExerciseModel currentExercise;

  const _ExerciseSwapperContent({required this.currentExercise});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final future = ref
        .read(workoutRepositoryProvider)
        .findAlternativeExercises(currentExercise);

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.swap_horiz, color: AppColors.primary),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Đổi bài tập tức thì',
                      style:
                          TextStyle(fontSize: 17, fontWeight: FontWeight.bold),
                    ),
                    Text(
                      'Thay cho: ${currentExercise.nameVi} (giữ nguyên các hiệp đã ghi)',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.close),
                onPressed: () => Navigator.of(context).pop(),
              ),
            ],
          ),
          const SizedBox(height: 12),
          FutureBuilder<List<AlternativeExerciseCandidate>>(
            future: future,
            builder: (context, snap) {
              if (snap.connectionState == ConnectionState.waiting) {
                return const Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: CircularProgressIndicator()),
                );
              }
              final items = snap.data ?? const [];
              if (items.isEmpty) {
                return const Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('Không tìm thấy bài tập thay thế phù hợp.'),
                );
              }
              return ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 380),
                child: ListView.separated(
                  shrinkWrap: true,
                  itemCount: items.length,
                  separatorBuilder: (_, __) => const SizedBox(height: 8),
                  itemBuilder: (context, index) {
                    final cand = items[index];
                    final ex = cand.exercise;
                    final primaryLabel = ex.primaryMuscles
                        .map((m) => MuscleMaterialIds.labelVi(m).split(' (').first)
                        .join(', ');
                    return Card(
                      child: ListTile(
                        title: Text(
                          ex.nameVi,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          '${ex.equipmentType} · Trùng ${(cand.overlapRatio * 100).round()}% ($primaryLabel)'
                          '${cand.differentEquipment ? " · Khác dụng cụ" : ""}',
                        ),
                        trailing: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            IconButton(
                              tooltip: 'Xem 3D',
                              icon: const Icon(
                                Icons.view_in_ar,
                                color: AppColors.primary,
                              ),
                              onPressed: () =>
                                  context.push('/gym3d/exercise/${ex.code}'),
                            ),
                            FilledButton(
                              onPressed: () => Navigator.of(context).pop(ex),
                              style: FilledButton.styleFrom(
                                minimumSize: const Size(64, 36),
                                padding:
                                    const EdgeInsets.symmetric(horizontal: 12),
                              ),
                              child: const Text('Đổi'),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
