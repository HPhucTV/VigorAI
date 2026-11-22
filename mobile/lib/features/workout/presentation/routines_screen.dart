// [OWNER: M2] Man hinh Lich tap luyen & Thiet ke Giao an Tuan Offline-First (PPL, Upper-Lower, Full Body, Superset) (T-M2-09 / F14)
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/database/workout_tables.drift.dart';
import '../../../core/theme/app_theme.dart';
import '../../gym3d/data/exercise_repository.dart';
import '../data/workout_repository.dart';

class RoutinesScreen extends ConsumerStatefulWidget {
  const RoutinesScreen({super.key});

  @override
  ConsumerState<RoutinesScreen> createState() => _RoutinesScreenState();
}

class _RoutinesScreenState extends ConsumerState<RoutinesScreen> {
  static const _weekdayLabels = <int, String>{
    1: 'T2',
    2: 'T3',
    3: 'T4',
    4: 'T5',
    5: 'T6',
    6: 'T7',
    7: 'CN',
  };

  int _selectedWeekday = DateTime.now().weekday;

  Future<void> _openBuilder({WorkoutRoutineModel? initial}) async {
    final allExercises = await ref.read(exercisesListProvider.future);
    if (!mounted) return;
    final saved = await showModalBottomSheet<WorkoutRoutineModel>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      builder: (ctx) => _RoutineBuilderSheet(
        initial: initial,
        allExercises: allExercises,
      ),
    );
    if (saved != null) {
      await ref.read(workoutRepositoryProvider).saveRoutine(saved);
      ref.invalidate(workoutRoutinesProvider);
    }
  }

  @override
  Widget build(BuildContext context) {
    final routinesAsync = ref.watch(workoutRoutinesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lịch & Giáo án Tập luyện'),
        actions: [
          IconButton(
            tooltip: 'Tạo giáo án mới',
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () => _openBuilder(),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _openBuilder(),
        icon: const Icon(Icons.add),
        label: const Text('Tạo giáo án'),
      ),
      body: routinesAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Lỗi tải giáo án: $err')),
        data: (routines) {
          final todaysRoutines = routines
              .where((r) => r.scheduledWeekdays.contains(_selectedWeekday))
              .toList();

          return ListView(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 90),
            children: [
              const Text(
                'Lịch tập trong tuần',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 8),
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: _weekdayLabels.entries.map((e) {
                    final selected = _selectedWeekday == e.key;
                    final hasRoutine = routines
                        .any((r) => r.scheduledWeekdays.contains(e.key));
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(hasRoutine ? '${e.value} •' : e.value),
                        selected: selected,
                        onSelected: (_) =>
                            setState(() => _selectedWeekday = e.key),
                      ),
                    );
                  }).toList(),
                ),
              ),
              const SizedBox(height: 12),
              if (todaysRoutines.isNotEmpty) ...[
                Text(
                  'Gợi ý lịch ${_weekdayLabels[_selectedWeekday]}:',
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 6),
                ...todaysRoutines.map(
                  (r) => _RoutineCard(
                    routine: r,
                    highlight: true,
                    onStart: () => context.push('/workout/live?routineId=${r.id}'),
                    onDuplicate: () async {
                      await ref
                          .read(workoutRepositoryProvider)
                          .duplicateTemplate(r);
                      ref.invalidate(workoutRoutinesProvider);
                    },
                    onEdit: r.isTemplate ? null : () => _openBuilder(initial: r),
                    onDelete: r.isTemplate
                        ? null
                        : () async {
                            await ref
                                .read(workoutRepositoryProvider)
                                .softDeleteRoutine(r.id);
                            ref.invalidate(workoutRoutinesProvider);
                          },
                  ),
                ),
                const Divider(height: 24),
              ],
              const Text(
                'Tất cả Giáo án & Mẫu chuẩn',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 8),
              ...routines.map(
                (r) => _RoutineCard(
                  routine: r,
                  highlight: false,
                  onStart: () => context.push('/workout/live?routineId=${r.id}'),
                  onDuplicate: () async {
                    await ref
                        .read(workoutRepositoryProvider)
                        .duplicateTemplate(r);
                    ref.invalidate(workoutRoutinesProvider);
                  },
                  onEdit: r.isTemplate ? null : () => _openBuilder(initial: r),
                  onDelete: r.isTemplate
                      ? null
                      : () async {
                          await ref
                              .read(workoutRepositoryProvider)
                              .softDeleteRoutine(r.id);
                          ref.invalidate(workoutRoutinesProvider);
                        },
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _RoutineCard extends StatelessWidget {
  final WorkoutRoutineModel routine;
  final bool highlight;
  final VoidCallback onStart;
  final VoidCallback onDuplicate;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const _RoutineCard({
    required this.routine,
    required this.highlight,
    required this.onStart,
    required this.onDuplicate,
    this.onEdit,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final hasSuperset = routine.exercises.any((e) => e.supersetGroupId != null);
    return Card(
      color: highlight ? const Color(0xFFE3F2FD) : null,
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    routine.name,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                    ),
                  ),
                ),
                if (routine.isTemplate)
                  const Chip(
                    label: Text('Mẫu', style: TextStyle(fontSize: 11)),
                    visualDensity: VisualDensity.compact,
                  ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              '${routine.splitType} · ${routine.exercises.length} bài tập'
              '${hasSuperset ? " · Có Superset" : ""}',
              style: Theme.of(context).textTheme.bodySmall,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 4,
              children: routine.exercises.take(5).map((ex) {
                return Chip(
                  label: Text(
                    '${ex.exerciseCode} (${ex.targetSets}x${ex.targetRepMin}-${ex.targetRepMax})'
                    '${ex.supersetGroupId != null ? " [SS#${ex.supersetGroupId}]" : ""}',
                    style: const TextStyle(fontSize: 11),
                  ),
                  visualDensity: VisualDensity.compact,
                );
              }).toList(),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: FilledButton.icon(
                    onPressed: onStart,
                    style: FilledButton.styleFrom(
                      minimumSize: const Size(0, 40),
                    ),
                    icon: const Icon(Icons.play_arrow, size: 18),
                    label: const Text('Bắt đầu tập'),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton(
                  tooltip: 'Nhân bản',
                  onPressed: onDuplicate,
                  icon: const Icon(Icons.copy_outlined),
                ),
                if (onEdit != null)
                  IconButton(
                    tooltip: 'Chỉnh sửa',
                    onPressed: onEdit,
                    icon: const Icon(Icons.edit_outlined),
                  ),
                if (onDelete != null)
                  IconButton(
                    tooltip: 'Xóa',
                    onPressed: onDelete,
                    icon: const Icon(
                      Icons.delete_outline,
                      color: AppColors.warningRed,
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _EditableRoutineItem {
  final int uid;
  RoutineExerciseItem item;

  _EditableRoutineItem(this.uid, this.item);
}

class _RoutineBuilderSheet extends StatefulWidget {
  final WorkoutRoutineModel? initial;
  final List<ExerciseModel> allExercises;

  const _RoutineBuilderSheet({
    this.initial,
    required this.allExercises,
  });

  @override
  State<_RoutineBuilderSheet> createState() => _RoutineBuilderSheetState();
}

class _RoutineBuilderSheetState extends State<_RoutineBuilderSheet> {
  late TextEditingController _nameCtrl;
  late String _splitType;
  late Set<int> _weekdays;
  late List<_EditableRoutineItem> _entries;
  int _nextUid = 0;

  static const _splits = ['PUSH_PULL_LEGS', 'UPPER_LOWER', 'FULL_BODY', 'BRO_SPLIT', 'CUSTOM'];

  @override
  void initState() {
    super.initState();
    _nameCtrl = TextEditingController(
      text: widget.initial?.name ?? 'Giáo án Cá nhân mới',
    );
    _splitType = widget.initial?.splitType ?? 'PUSH_PULL_LEGS';
    _weekdays = Set<int>.from(widget.initial?.scheduledWeekdays ?? const [1, 4]);
    final sourceItems = widget.initial?.exercises ??
        const [
          RoutineExerciseItem(
            exerciseCode: 'BARBELL_BENCH_PRESS',
            orderIndex: 0,
            targetSets: 4,
            targetRepMin: 6,
            targetRepMax: 8,
            defaultRestSeconds: 150,
          ),
        ];
    _entries = sourceItems
        .map((e) => _EditableRoutineItem(_nextUid++, e))
        .toList();
    _normalizeEntries();
  }

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  void _normalizeEntries() {
    final counts = <int, int>{};
    for (final entry in _entries) {
      final gid = entry.item.supersetGroupId;
      if (gid != null) {
        counts[gid] = (counts[gid] ?? 0) + 1;
      }
    }
    for (var i = 0; i < _entries.length; i++) {
      final cur = _entries[i].item;
      final gid = cur.supersetGroupId;
      final validGid = (gid != null && (counts[gid] ?? 0) >= 2) ? gid : null;
      _entries[i].item = RoutineExerciseItem(
        exerciseCode: cur.exerciseCode,
        orderIndex: i,
        supersetGroupId: validGid,
        targetSets: cur.targetSets,
        targetRepMin: cur.targetRepMin,
        targetRepMax: cur.targetRepMax,
        defaultRestSeconds: cur.defaultRestSeconds,
      );
    }
  }

  int _nextAvailableSupersetGroupId() {
    final used = <int>{};
    for (final entry in _entries) {
      if (entry.item.supersetGroupId != null) {
        used.add(entry.item.supersetGroupId!);
      }
    }
    var candidate = 1;
    while (used.contains(candidate)) {
      candidate++;
    }
    return candidate;
  }

  String _nameForCode(String code) {
    for (final ex in widget.allExercises) {
      if (ex.code == code) return ex.nameVi;
    }
    return code;
  }

  Future<void> _pickExerciseToAdd() async {
    if (_entries.length >= 15) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Tối đa 15 bài tập trong 1 giáo án.')),
      );
      return;
    }
    final picked = await showDialog<ExerciseModel>(
      context: context,
      builder: (ctx) => SimpleDialog(
        title: const Text('Thêm bài tập (tối đa 15)'),
        children: widget.allExercises
            .map(
              (ex) => SimpleDialogOption(
                onPressed: () => Navigator.of(ctx).pop(ex),
                child: Text('${ex.nameVi} (${ex.equipmentType})'),
              ),
            )
            .toList(),
      ),
    );
    if (picked == null) return;
    setState(() {
      _entries.add(
        _EditableRoutineItem(
          _nextUid++,
          RoutineExerciseItem(
            exerciseCode: picked.code,
            orderIndex: _entries.length,
            targetSets: 3,
            targetRepMin: 8,
            targetRepMax: 12,
            defaultRestSeconds:
                picked.equipmentType == 'BARBELL' ? 150 : 90,
          ),
        ),
      );
      _normalizeEntries();
    });
  }

  void _toggleSupersetWithNext(int index) {
    if (index + 1 >= _entries.length) return;
    setState(() {
      final current = _entries[index].item;
      final next = _entries[index + 1].item;
      final clearGroup = current.supersetGroupId != null &&
          current.supersetGroupId == next.supersetGroupId;
      final int? groupId = clearGroup
          ? null
          : (current.supersetGroupId ??
              next.supersetGroupId ??
              _nextAvailableSupersetGroupId());
      _entries[index].item = RoutineExerciseItem(
        exerciseCode: current.exerciseCode,
        orderIndex: index,
        supersetGroupId: groupId,
        targetSets: current.targetSets,
        targetRepMin: current.targetRepMin,
        targetRepMax: current.targetRepMax,
        defaultRestSeconds: current.defaultRestSeconds,
      );
      _entries[index + 1].item = RoutineExerciseItem(
        exerciseCode: next.exerciseCode,
        orderIndex: index + 1,
        supersetGroupId: groupId,
        targetSets: next.targetSets,
        targetRepMin: next.targetRepMin,
        targetRepMax: next.targetRepMax,
        defaultRestSeconds: next.defaultRestSeconds,
      );
      _normalizeEntries();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: SizedBox(
        height: MediaQuery.of(context).size.height * 0.85,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Thiết kế Giáo án (Kéo thả & Superset)',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            TextField(
              controller: _nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Tên giáo án',
                isDense: true,
              ),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue:
                  _splits.contains(_splitType) ? _splitType : 'CUSTOM',
              decoration: const InputDecoration(
                labelText: 'Phân chia Split',
                isDense: true,
              ),
              items: _splits
                  .map((s) => DropdownMenuItem(value: s, child: Text(s)))
                  .toList(),
              onChanged: (v) {
                if (v != null) setState(() => _splitType = v);
              },
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              children: [1, 2, 3, 4, 5, 6, 7].map((d) {
                final label = d == 7 ? 'CN' : 'T${d + 1}';
                return FilterChip(
                  label: Text(label),
                  selected: _weekdays.contains(d),
                  visualDensity: VisualDensity.compact,
                  onSelected: (on) {
                    setState(() {
                      if (on) {
                        _weekdays.add(d);
                      } else {
                        _weekdays.remove(d);
                      }
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Danh sách bài tập (${_entries.length}/15)',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                TextButton.icon(
                  onPressed: _pickExerciseToAdd,
                  icon: const Icon(Icons.add),
                  label: const Text('Thêm bài'),
                ),
              ],
            ),
            Expanded(
              child: ReorderableListView.builder(
                itemCount: _entries.length,
                onReorderItem: (oldIndex, newIndex) {
                  setState(() {
                    final moved = _entries.removeAt(oldIndex);
                    _entries.insert(newIndex, moved);
                    _normalizeEntries();
                  });
                },
                itemBuilder: (context, index) {
                  final entry = _entries[index];
                  final item = entry.item;
                  return Card(
                    key: ValueKey('routine-item-${entry.uid}'),
                    child: ListTile(
                      dense: true,
                      leading: const Icon(Icons.drag_handle),
                      title: Text(_nameForCode(item.exerciseCode)),
                      subtitle: Text(
                        '${item.targetSets} hiệp · ${item.targetRepMin}-${item.targetRepMax} reps · Nghỉ ${item.defaultRestSeconds}s'
                        '${item.supersetGroupId != null ? " · Superset #${item.supersetGroupId}" : ""}',
                      ),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (index + 1 < _entries.length)
                            IconButton(
                              tooltip: 'Ghép/Hủy Superset với bài kế tiếp',
                              icon: Icon(
                                Icons.link,
                                color: item.supersetGroupId != null
                                    ? AppColors.primary
                                    : Colors.grey,
                              ),
                              onPressed: () => _toggleSupersetWithNext(index),
                            ),
                          IconButton(
                            icon: const Icon(Icons.close, size: 18),
                            onPressed: () {
                              setState(() {
                                _entries.removeAt(index);
                                _normalizeEntries();
                              });
                            },
                          ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 8),
            FilledButton.icon(
              onPressed: () {
                if (_entries.isEmpty) return;
                _normalizeEntries();
                final model = WorkoutRoutineModel(
                  id: widget.initial?.id ?? '',
                  name: _nameCtrl.text.trim().isEmpty
                      ? 'Giáo án Cá nhân'
                      : _nameCtrl.text.trim(),
                  splitType: _splitType,
                  scheduledWeekdays: _weekdays.toList()..sort(),
                  exercises: _entries.map((e) => e.item).toList(),
                  isTemplate: false,
                  updatedAt: DateTime.now().toUtc(),
                );
                Navigator.of(context).pop(model);
              },
              icon: const Icon(Icons.save),
              label: const Text('Lưu Giáo án'),
            ),
          ],
        ),
      ),
    );
  }
}
